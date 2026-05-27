"""Read-only adapter for the SPARTA Trade Intelligence Journal.

Reads the external obsidian-trade-logger project STRICTLY READ-ONLY:

  * No writes anywhere outside SPARTA_BRAIN.
  * sqlite3 is opened with `uri=True` + `mode=ro` so writes are physically
    impossible at the connection level.
  * No broker / API / order / execution imports.
  * No scheduler / trigger / no live trading code path.
  * No fabricated values: every section that cannot be computed is returned
    with status="MISSING" and a reason string.

Preferred data sources (best-effort, in order):
  1. existing JSON snapshots in the external project's reports/ and data/
     folders (already-computed metrics, just rendered through).
  2. trades.db read-only sqlite SELECT against the existing schema.

The module never raises out to its caller. All errors are captured in
`payload["errors"]`. The caller (app.py /journal route) still wraps this in
its own try/except so a catastrophic failure still renders the page with
ERROR posture.

Override the external root for tests with `SPARTA_TRADE_LOGGER_ROOT`.
"""
from __future__ import annotations

import json
import math
import os
import random
import sqlite3
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_DEFAULT_EXTERNAL_ROOT = r"C:\Users\mahmo\obsidian-trade-logger"
_EXTERNAL_ROOT_ENV = "SPARTA_TRADE_LOGGER_ROOT"

# Source paths inside the external project (read-only). All optional.
_REL_TRADES_DB = ("data", "trades.db")
_REL_SI_REPORT = ("data", "strategy_intelligence_report.json")
_REL_SP_REPORT = ("reports", "strategy_performance.json")
_REL_PORTFOLIO = ("reports", "portfolio_simulator.json")
_REL_GATES = (
    ("data", "evidence_gate.json", "evidence_gate"),
    ("data", "strategy_decision_state.json", "strategy_decision_state"),
    ("data", "health_response_state.json", "health_response"),
    ("data", "final_stack_paper_state.json", "final_stack_paper"),
    ("data", "volatility_regime_monitor.json", "volatility_regime_monitor"),
)

_MAX_ROWS_FOR_COMPUTE = 50_000  # hard cap; the journal is a viewer not a job

_POSTURE = {
    "trading": "PAUSED",
    "live_status": "BLOCKED_AT_6_GATES",
    "read_only": True,
    "external_project": "READ_ONLY",
    "broker_api": "DISCONNECTED",
}


def external_root() -> Path:
    return Path(os.environ.get(_EXTERNAL_ROOT_ENV, _DEFAULT_EXTERNAL_ROOT))


# ── safe IO helpers ─────────────────────────────────────────────────────────

def _safe_load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def _read_trades_ro(db_path: Path) -> tuple[list[dict[str, Any]], str | None]:
    """Open trades.db in URI mode=ro and pull the LEFT-JOIN we need.

    Returns (rows, error_message_or_None). Never raises.
    """
    if not db_path.exists():
        return [], None
    try:
        # URI form `mode=ro` is enforced by SQLite itself. Even if downstream
        # code attempted a write, the engine would refuse.
        uri = f"file:{db_path.as_posix()}?mode=ro"
        conn = sqlite3.connect(uri, uri=True)
        conn.row_factory = sqlite3.Row
    except sqlite3.Error as exc:
        return [], f"sqlite_connect:{type(exc).__name__}:{exc}"
    try:
        try:
            cur = conn.execute(
                """
                SELECT
                    t.id, t.exchange, t.symbol, t.strategy, t.direction,
                    t.entry, t.sl, t.size_usd,
                    t.open_date, t.close_date,
                    t.outcome, t.pnl_usd, t.pnl_r,
                    e.max_favorable_R, e.max_adverse_R
                FROM trades t
                LEFT JOIN trade_excursions e ON e.trade_id = t.id
                LIMIT ?
                """,
                (_MAX_ROWS_FOR_COMPUTE,),
            )
        except sqlite3.OperationalError:
            try:
                cur = conn.execute(
                    "SELECT * FROM trades LIMIT ?", (_MAX_ROWS_FOR_COMPUTE,)
                )
            except sqlite3.OperationalError as exc:
                return [], f"sqlite_query:{type(exc).__name__}:{exc}"
        try:
            rows = [dict(row) for row in cur.fetchall()]
        except sqlite3.Error as exc:
            return [], f"sqlite_fetch:{type(exc).__name__}:{exc}"
    finally:
        try:
            conn.close()
        except sqlite3.Error:
            pass
    return rows, None


# ── computation helpers (stdlib only) ────────────────────────────────────────

def _coerce_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_dt(value: Any) -> datetime | None:
    if not value:
        return None
    s = str(value).strip()
    if not s:
        return None
    try:
        if len(s) == 10:
            return datetime.strptime(s, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


def _percentile(sorted_arr: list[float], pct: float) -> float | None:
    if not sorted_arr:
        return None
    if pct <= 0:
        return sorted_arr[0]
    if pct >= 100:
        return sorted_arr[-1]
    idx = int(round((pct / 100.0) * (len(sorted_arr) - 1)))
    return sorted_arr[idx]


def _pearson(a: list[float], b: list[float]) -> float | None:
    n = len(a)
    if n < 2 or n != len(b):
        return None
    ma = sum(a) / n
    mb = sum(b) / n
    num = sum((ai - ma) * (bi - mb) for ai, bi in zip(a, b))
    da = math.sqrt(sum((ai - ma) ** 2 for ai in a))
    db = math.sqrt(sum((bi - mb) ** 2 for bi in b))
    if da == 0.0 or db == 0.0:
        return None
    return num / (da * db)


def _pnl_r_series(rows: list[dict[str, Any]]) -> list[float]:
    out: list[float] = []
    for r in rows:
        if r.get("close_date") is None:
            continue
        v = _coerce_float(r.get("pnl_r"))
        if v is not None:
            out.append(v)
    return out


# ── computed sections ───────────────────────────────────────────────────────

def _compute_daily_pnl_correlation(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_day: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    strategies: set[str] = set()
    for r in rows:
        cd = r.get("close_date")
        if not cd:
            continue
        pnl = _coerce_float(r.get("pnl_usd"))
        if pnl is None:
            continue
        strat = str(r.get("strategy") or "unknown")
        day = str(cd)[:10]
        by_day[day][strat] += pnl
        strategies.add(strat)

    strats_sorted = sorted(strategies)
    days_sorted = sorted(by_day.keys())
    if len(strats_sorted) < 2 or len(days_sorted) < 5:
        return {
            "status": "MISSING",
            "reason": "need_at_least_2_strategies_and_5_days",
            "strategy_count": len(strats_sorted),
            "day_count": len(days_sorted),
        }

    series = {s: [by_day[d].get(s, 0.0) for d in days_sorted] for s in strats_sorted}
    matrix = []
    for s1 in strats_sorted:
        row_vals = []
        for s2 in strats_sorted:
            c = _pearson(series[s1], series[s2])
            row_vals.append(None if c is None else round(c, 3))
        matrix.append({"strategy": s1, "values": row_vals})
    return {
        "status": "OK",
        "strategies": strats_sorted,
        "matrix": matrix,
        "day_count": len(days_sorted),
    }


_WEEKDAY_NAMES = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
_MONTH_NAMES = (
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
)


def _bucket_perf(
    rows: list[dict[str, Any]], bucket_fn, labels: tuple[str, ...]
) -> dict[str, Any]:
    buckets: dict[int, list[float]] = defaultdict(list)
    for r in rows:
        cd = r.get("close_date")
        dt = _parse_dt(cd)
        pnl_r = _coerce_float(r.get("pnl_r"))
        if dt is None or pnl_r is None:
            continue
        try:
            idx = bucket_fn(dt)
        except Exception:
            continue
        if not isinstance(idx, int):
            continue
        if 0 <= idx < len(labels):
            buckets[idx].append(pnl_r)

    if not buckets:
        return {"status": "MISSING", "reason": "no_closed_trades_with_dates"}

    out_rows = []
    for i, label in enumerate(labels):
        vals = buckets.get(i, [])
        if vals:
            avg = sum(vals) / len(vals)
            wins = sum(1 for v in vals if v > 0)
            out_rows.append({
                "label": label,
                "trades": len(vals),
                "avg_R": round(avg, 3),
                "win_rate": round(wins / len(vals), 3),
                "sum_R": round(sum(vals), 3),
            })
        else:
            out_rows.append({
                "label": label, "trades": 0,
                "avg_R": None, "win_rate": None, "sum_R": None,
            })
    return {"status": "OK", "rows": out_rows}


def _compute_weekday_performance(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return _bucket_perf(rows, lambda dt: dt.weekday(), _WEEKDAY_NAMES)


def _compute_month_performance(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return _bucket_perf(rows, lambda dt: dt.month - 1, _MONTH_NAMES)


def _compute_monte_carlo(
    pnl_r_list: list[float], runs: int = 500, seed: int = 42
) -> dict[str, Any]:
    n = len(pnl_r_list)
    if n < 10:
        return {
            "status": "MISSING",
            "reason": "need_at_least_10_closed_trades_with_pnl_R",
            "trade_count": n,
        }
    rng = random.Random(seed)
    finals: list[float] = []
    max_dds: list[float] = []
    for _ in range(runs):
        cum = 0.0
        peak = 0.0
        worst_dd = 0.0
        for _ in range(n):
            cum += pnl_r_list[rng.randrange(n)]
            if cum > peak:
                peak = cum
            dd = cum - peak
            if dd < worst_dd:
                worst_dd = dd
        finals.append(cum)
        max_dds.append(worst_dd)
    finals.sort()
    max_dds.sort()
    return {
        "status": "OK",
        "runs": runs,
        "trade_count": n,
        "method": "bootstrap_resample_pnl_R_with_replacement",
        "final_R_p5": round(_percentile(finals, 5), 3),
        "final_R_p50": round(_percentile(finals, 50), 3),
        "final_R_p95": round(_percentile(finals, 95), 3),
        "max_dd_R_p5": round(_percentile(max_dds, 5), 3),
        "max_dd_R_p50": round(_percentile(max_dds, 50), 3),
        "max_dd_R_p95": round(_percentile(max_dds, 95), 3),
    }


def _compute_risk_of_ruin(
    pnl_r_list: list[float],
    *,
    risk_pct_per_trade: float = 1.0,
    ruin_drawdown_pct: float = 50.0,
    runs: int = 1000,
    path_len: int = 200,
    seed: int = 43,
) -> dict[str, Any]:
    n = len(pnl_r_list)
    if n < 10:
        return {
            "status": "MISSING",
            "reason": "need_at_least_10_closed_trades_with_pnl_R",
            "trade_count": n,
        }
    rng = random.Random(seed)
    ruined = 0
    risk_frac = risk_pct_per_trade / 100.0
    ruin_floor = 1.0 - (ruin_drawdown_pct / 100.0)
    for _ in range(runs):
        equity = 1.0
        peak = 1.0
        for _ in range(path_len):
            r = pnl_r_list[rng.randrange(n)]
            equity *= (1.0 + r * risk_frac)
            if equity > peak:
                peak = equity
            if equity <= peak * ruin_floor or equity <= 0.0:
                ruined += 1
                break
    return {
        "status": "OK",
        "method": "simulation_ruin_if_equity_under_peak_x_ruin_floor",
        "runs": runs,
        "path_length": path_len,
        "risk_pct_per_trade": risk_pct_per_trade,
        "ruin_drawdown_pct": ruin_drawdown_pct,
        "risk_of_ruin_pct": round(100.0 * ruined / runs, 2),
        "trade_count": n,
    }


# ── shaping helpers for the UI payload ──────────────────────────────────────

def _strategy_rows_from_si_report(si: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    per_strategy = si.get("per_strategy") or {}
    if not isinstance(per_strategy, dict):
        return out
    for name, metrics in sorted(per_strategy.items()):
        if not isinstance(metrics, dict):
            continue
        out.append({
            "strategy": name,
            "total_trades": metrics.get("total_trades"),
            "closed_trades": metrics.get("closed_trades"),
            "open_trades": metrics.get("open_trades"),
            "win_rate": metrics.get("win_rate"),
            "expectancy_R": metrics.get("expectancy_R"),
            "profit_factor": metrics.get("profit_factor"),
            "long_performance": metrics.get("long_performance"),
            "short_performance": metrics.get("short_performance"),
            "best_symbol": metrics.get("best_symbol"),
            "worst_symbol": metrics.get("worst_symbol"),
            "confidence": metrics.get("confidence"),
            "confidence_label": metrics.get("confidence_label"),
            "data_quality": metrics.get("data_quality"),
        })
    return out


def _symbol_rows_from_si_report(si: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    per_symbol = si.get("per_symbol") or {}
    if not isinstance(per_symbol, dict):
        return out
    for sym, metrics in sorted(per_symbol.items()):
        if not isinstance(metrics, dict):
            continue
        out.append({
            "symbol": sym,
            "best_strategy": metrics.get("best_strategy"),
            "worst_strategy": metrics.get("worst_strategy"),
            "total_exposure_attempts": metrics.get("total_exposure_attempts"),
            "blocked_attempts": metrics.get("blocked_attempts"),
            "open_lock": metrics.get("open_lock"),
        })
    return out


def _strategy_rows_from_trade_rows(
    rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Lightweight in-process equivalent of strategy_intelligence.compute_strategy_metrics.

    Computed only when the external SI report is missing but trades.db is
    readable. Mirrors the public fields the UI needs.
    """
    by_strat: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        by_strat[str(r.get("strategy") or "unknown")].append(r)

    out: list[dict[str, Any]] = []
    for name in sorted(by_strat):
        srows = by_strat[name]
        closed = [r for r in srows if r.get("close_date") is not None]
        opened = [r for r in srows if r.get("close_date") is None]
        n_closed = len(closed)

        def _outcome_eq(r: dict[str, Any], target: str) -> bool:
            return (r.get("outcome") or "").lower() == target

        win_rate: Any = "INSUFFICIENT_DATA"
        expectancy_R: Any = "INSUFFICIENT_DATA"
        profit_factor: Any = "INSUFFICIENT_DATA"
        long_perf: Any = "INSUFFICIENT_DATA"
        short_perf: Any = "INSUFFICIENT_DATA"

        if n_closed >= 5:
            wins = [r for r in closed if _outcome_eq(r, "win")]
            losses = [r for r in closed if (r.get("outcome") or "").lower() in ("loss", "sl")]
            win_rate = round(len(wins) / n_closed, 4)
            r_vals = [_coerce_float(r.get("pnl_r")) for r in closed]
            r_vals = [v for v in r_vals if v is not None]
            if r_vals:
                expectancy_R = round(sum(r_vals) / len(r_vals), 4)
            win_pnl = sum(_coerce_float(r.get("pnl_usd")) or 0.0 for r in wins)
            loss_pnl = sum(_coerce_float(r.get("pnl_usd")) or 0.0 for r in losses)
            if not losses:
                profit_factor = "INF"
            elif not wins:
                profit_factor = 0
            elif loss_pnl == 0:
                profit_factor = None
            else:
                profit_factor = round(win_pnl / abs(loss_pnl), 4)

            long_r = [
                _coerce_float(r.get("pnl_r"))
                for r in closed
                if (r.get("direction") or "").lower() == "long"
            ]
            long_r = [v for v in long_r if v is not None]
            short_r = [
                _coerce_float(r.get("pnl_r"))
                for r in closed
                if (r.get("direction") or "").lower() == "short"
            ]
            short_r = [v for v in short_r if v is not None]
            if len(long_r) >= 3:
                long_perf = round(sum(long_r) / len(long_r), 4)
            if len(short_r) >= 3:
                short_perf = round(sum(short_r) / len(short_r), 4)

        if n_closed < 5:
            data_quality = "LOW"
        elif n_closed < 10:
            data_quality = "MEDIUM"
        else:
            data_quality = "HIGH"

        out.append({
            "strategy": name,
            "total_trades": len(srows),
            "closed_trades": n_closed,
            "open_trades": len(opened),
            "win_rate": win_rate,
            "expectancy_R": expectancy_R,
            "profit_factor": profit_factor,
            "long_performance": long_perf,
            "short_performance": short_perf,
            "best_symbol": None,
            "worst_symbol": None,
            "confidence": None,
            "confidence_label": None,
            "data_quality": data_quality,
        })
    return out


def _symbol_rows_from_trade_rows(
    rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_sym: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        by_sym[str(r.get("symbol") or "unknown")].append(r)
    out = []
    for sym in sorted(by_sym):
        srows = by_sym[sym]
        out.append({
            "symbol": sym,
            "best_strategy": None,
            "worst_strategy": None,
            "total_exposure_attempts": len(srows),
            "blocked_attempts": None,
            "open_lock": any(r.get("close_date") is None for r in srows),
        })
    return out


def _scorecard_rows_from_strategy_rows(
    strategy_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Compact scorecard summary per strategy for the top table."""
    out = []
    for row in strategy_rows:
        out.append({
            "strategy": row.get("strategy"),
            "closed_trades": row.get("closed_trades"),
            "win_rate": row.get("win_rate"),
            "expectancy_R": row.get("expectancy_R"),
            "profit_factor": row.get("profit_factor"),
            "data_quality": row.get("data_quality"),
            "confidence_label": row.get("confidence_label"),
        })
    return out


def _collect_gates(root: Path) -> list[dict[str, Any]]:
    out = []
    for parts in _REL_GATES:
        rel_dir, rel_file, label = parts
        path = root / rel_dir / rel_file
        if not path.exists():
            out.append({
                "name": label,
                "status": "MISSING",
                "detail": f"{rel_dir}/{rel_file} not found",
            })
            continue
        data = _safe_load_json(path)
        if data is None:
            out.append({
                "name": label,
                "status": "MISSING",
                "detail": "file not readable as JSON",
            })
            continue
        # Surface a short status line. We never invent — only echo what's there.
        detail_keys = ("status", "mode", "decision", "verdict", "state", "phase")
        detail = ""
        for k in detail_keys:
            v = data.get(k) if isinstance(data, dict) else None
            if isinstance(v, str) and v.strip():
                detail = f"{k}={v.strip()}"
                break
        if not detail:
            detail = "present"
        out.append({"name": label, "status": "OK", "detail": detail})
    return out


# ── evidence quality (UI explainer) ─────────────────────────────────────────

# Thresholds are intentionally hard-coded constants so the explainer is a
# pure UI layer with no config surface. Changing them is a code review,
# not a runtime toggle.
_EQ_THR_PER_STRATEGY_MIN_CLOSED = 5
_EQ_THR_MONTE_CARLO_MIN_CLOSED = 10
_EQ_THR_RISK_OF_RUIN_MIN_CLOSED = 10
_EQ_THR_DAILY_CORRELATION_MIN_DAYS = 5
_EQ_THR_OBSERVATION_TOTAL_CLOSED = 30


def _eq_thresholds_block() -> dict[str, int]:
    return {
        "per_strategy_min_closed": _EQ_THR_PER_STRATEGY_MIN_CLOSED,
        "monte_carlo_min_trades": _EQ_THR_MONTE_CARLO_MIN_CLOSED,
        "risk_of_ruin_min_trades": _EQ_THR_RISK_OF_RUIN_MIN_CLOSED,
        "daily_correlation_min_days": _EQ_THR_DAILY_CORRELATION_MIN_DAYS,
        "observation_total_closed": _EQ_THR_OBSERVATION_TOTAL_CLOSED,
    }


def _compute_evidence_quality(
    *,
    closed_n: int,
    strategy_rows: list[dict[str, Any]],
    correlation_day_count: int,
) -> dict[str, Any]:
    """Build the read-only Evidence Quality explainer block.

    Purely factual: counts vs. thresholds. Never claims live-readiness,
    never recommends a strategy, never proposes an action.
    """
    checks: list[dict[str, Any]] = []

    # 1. Per-strategy minimum sample size.
    insufficient: list[tuple[str, int]] = []
    for row in strategy_rows:
        name = row.get("strategy")
        c = row.get("closed_trades")
        if isinstance(c, int) and c < _EQ_THR_PER_STRATEGY_MIN_CLOSED:
            insufficient.append((str(name), c))
    if insufficient:
        joined = ", ".join(f"{s} ({c})" for s, c in insufficient)
        checks.append({
            "name": "Per-strategy minimum sample size",
            "label": "INSUFFICIENT_FOR_STRATEGY_CONFIDENCE",
            "status": "BLOCKED",
            "detail": (
                f"{len(insufficient)} strategy/strategies have "
                f"closed_trades < {_EQ_THR_PER_STRATEGY_MIN_CLOSED}: {joined}"
            ),
            "required": _EQ_THR_PER_STRATEGY_MIN_CLOSED,
        })
    else:
        checks.append({
            "name": "Per-strategy minimum sample size",
            "label": "PER_STRATEGY_SAMPLE_OK",
            "status": "OK",
            "detail": (
                f"all listed strategies have "
                f"closed_trades >= {_EQ_THR_PER_STRATEGY_MIN_CLOSED}"
            ),
            "required": _EQ_THR_PER_STRATEGY_MIN_CLOSED,
        })

    # 2. Monte Carlo minimum sample size.
    if closed_n < _EQ_THR_MONTE_CARLO_MIN_CLOSED:
        checks.append({
            "name": "Monte Carlo minimum sample size",
            "label": "MONTE_CARLO_BLOCKED_N_LT_10",
            "status": "BLOCKED",
            "detail": (
                f"closed_trades={closed_n}, required>={_EQ_THR_MONTE_CARLO_MIN_CLOSED}"
            ),
            "required": _EQ_THR_MONTE_CARLO_MIN_CLOSED,
        })
    else:
        checks.append({
            "name": "Monte Carlo minimum sample size",
            "label": "MONTE_CARLO_SAMPLE_OK",
            "status": "OK",
            "detail": (
                f"closed_trades={closed_n}, required>={_EQ_THR_MONTE_CARLO_MIN_CLOSED}"
            ),
            "required": _EQ_THR_MONTE_CARLO_MIN_CLOSED,
        })

    # 3. Risk of ruin minimum sample size.
    if closed_n < _EQ_THR_RISK_OF_RUIN_MIN_CLOSED:
        checks.append({
            "name": "Risk of ruin minimum sample size",
            "label": "RISK_OF_RUIN_BLOCKED_N_LT_10",
            "status": "BLOCKED",
            "detail": (
                f"closed_trades={closed_n}, required>={_EQ_THR_RISK_OF_RUIN_MIN_CLOSED}"
            ),
            "required": _EQ_THR_RISK_OF_RUIN_MIN_CLOSED,
        })
    else:
        checks.append({
            "name": "Risk of ruin minimum sample size",
            "label": "RISK_OF_RUIN_SAMPLE_OK",
            "status": "OK",
            "detail": (
                f"closed_trades={closed_n}, required>={_EQ_THR_RISK_OF_RUIN_MIN_CLOSED}"
            ),
            "required": _EQ_THR_RISK_OF_RUIN_MIN_CLOSED,
        })

    # 4. Daily correlation minimum unique close-days.
    if correlation_day_count < _EQ_THR_DAILY_CORRELATION_MIN_DAYS:
        checks.append({
            "name": "Daily correlation minimum unique days",
            "label": "DAILY_CORRELATION_BLOCKED_N_DAYS_LT_5",
            "status": "BLOCKED",
            "detail": (
                f"unique_close_days={correlation_day_count}, "
                f"required>={_EQ_THR_DAILY_CORRELATION_MIN_DAYS}"
            ),
            "required": _EQ_THR_DAILY_CORRELATION_MIN_DAYS,
        })
    else:
        checks.append({
            "name": "Daily correlation minimum unique days",
            "label": "DAILY_CORRELATION_SAMPLE_OK",
            "status": "OK",
            "detail": (
                f"unique_close_days={correlation_day_count}, "
                f"required>={_EQ_THR_DAILY_CORRELATION_MIN_DAYS}"
            ),
            "required": _EQ_THR_DAILY_CORRELATION_MIN_DAYS,
        })

    # Final state — purely descriptive, never a readiness claim.
    any_blocked = any(c["status"] == "BLOCKED" for c in checks)
    reasons: list[str] = []
    if closed_n < _EQ_THR_OBSERVATION_TOTAL_CLOSED:
        reasons.append(
            f"total_closed_trades ({closed_n}) < "
            f"{_EQ_THR_OBSERVATION_TOTAL_CLOSED}"
        )
    if any_blocked:
        blocked_labels = [c["label"] for c in checks if c["status"] == "BLOCKED"]
        reasons.append("blocking_checks=" + ",".join(blocked_labels))

    if not reasons:
        final_state = "OBSERVATION_THRESHOLDS_MET"
        if not reasons:
            reasons = [
                f"total_closed_trades ({closed_n}) >= "
                f"{_EQ_THR_OBSERVATION_TOTAL_CLOSED} and no blocking checks"
            ]
    else:
        final_state = "OBSERVATION_ONLY"

    return {
        "total_closed_trades": closed_n,
        "thresholds": _eq_thresholds_block(),
        "checks": checks,
        "final_state": final_state,
        "final_state_reason": reasons,
    }


# ── staleness detection ─────────────────────────────────────────────────────

def _si_stale_warning(
    si_report: dict[str, Any] | None,
    db_path: Path,
    trade_rows: list[dict[str, Any]],
) -> str:
    """Return a warning string if `strategy_intelligence_report.json` is older
    than the live trades.db mtime or the latest close_date in trade_rows.

    Empty string when SI report is absent, unparseable, or fresh enough.
    Never raises.
    """
    if not isinstance(si_report, dict):
        return ""
    si_dt = _parse_dt(si_report.get("generated_at"))
    if si_dt is None:
        return ""

    db_mtime_dt: datetime | None = None
    if db_path.exists():
        try:
            db_mtime_dt = datetime.fromtimestamp(
                db_path.stat().st_mtime, tz=timezone.utc
            )
        except OSError:
            db_mtime_dt = None

    latest_close_dt: datetime | None = None
    for r in trade_rows or []:
        cd = r.get("close_date")
        if not cd:
            continue
        dt = _parse_dt(cd)
        if dt is not None and (latest_close_dt is None or dt > latest_close_dt):
            latest_close_dt = dt

    is_stale = False
    if db_mtime_dt is not None and si_dt < db_mtime_dt:
        is_stale = True
    if latest_close_dt is not None and si_dt < latest_close_dt:
        is_stale = True
    if not is_stale:
        return ""

    return (
        "strategy_intelligence_report_stale:"
        f"generated_at={si_dt.isoformat()};"
        f"trades_db_mtime={db_mtime_dt.isoformat() if db_mtime_dt else 'unknown'};"
        f"latest_close_date={latest_close_dt.isoformat() if latest_close_dt else 'unknown'}"
    )


# ── main entrypoint ─────────────────────────────────────────────────────────

def _empty_payload(
    *,
    status: str = "MISSING",
    missing: list[str] | None = None,
    errors: list[str] | None = None,
    root: Path | None = None,
) -> dict[str, Any]:
    return {
        "status": status,
        "posture": dict(_POSTURE),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "external_root": str(root) if root else "",
        "external_root_exists": bool(root and root.exists()),
        "summary": {
            "strategy_count": 0,
            "symbol_count": 0,
            "trade_count": 0,
            "closed_trade_count": 0,
            "open_trade_count": 0,
            "source": "none",
        },
        "scorecards": [],
        "strategy_metrics": [],
        "symbol_metrics": [],
        "gates": [],
        "daily_pnl_correlation": {"status": "MISSING", "reason": "no_data_loaded"},
        "weekday_performance": {"status": "MISSING", "reason": "no_data_loaded"},
        "month_performance": {"status": "MISSING", "reason": "no_data_loaded"},
        "risk_of_ruin": {"status": "MISSING", "reason": "no_data_loaded"},
        "monte_carlo_summary": {"status": "MISSING", "reason": "no_data_loaded"},
        "evidence_quality": {
            "total_closed_trades": 0,
            "thresholds": _eq_thresholds_block(),
            "checks": [],
            "final_state": "MISSING",
            "final_state_reason": ["no_data_loaded"],
        },
        "missing": list(missing or []),
        "errors": list(errors or []),
    }


def load_payload() -> dict[str, Any]:
    """Build the read-only journal payload. Never raises."""
    root = external_root()
    payload = _empty_payload(root=root)

    if not root.exists():
        payload["status"] = "MISSING"
        payload["missing"].append(f"external_root_not_found:{root}")
        return payload

    # 1. Try existing snapshot reports (lowest blast radius).
    si_path = root.joinpath(*_REL_SI_REPORT)
    sp_path = root.joinpath(*_REL_SP_REPORT)
    si_report = _safe_load_json(si_path)
    sp_report = _safe_load_json(sp_path)
    if si_report is None:
        payload["missing"].append(f"strategy_intelligence_report:{si_path}")
    if sp_report is None:
        payload["missing"].append(f"strategy_performance_report:{sp_path}")

    # 2. Try trades.db read-only for the lightweight extras the snapshot
    #    can't cover (correlation, weekday, MC, RoR) AND, since the SI
    #    snapshot can fall behind the live DB, treat the live DB as the
    #    authoritative source for per-strategy and per-symbol rows when
    #    any trade rows can be read.
    db_path = root.joinpath(*_REL_TRADES_DB)
    trade_rows: list[dict[str, Any]] = []
    if db_path.exists():
        trade_rows, db_err = _read_trades_ro(db_path)
        if db_err:
            payload["errors"].append(db_err)
            payload["missing"].append(f"trades_db_read_failed:{db_path}")
    else:
        payload["missing"].append(f"trades_db:{db_path}")

    strategy_rows: list[dict[str, Any]] = []
    symbol_rows: list[dict[str, Any]] = []
    # Precedence (smallest safe fix for the stale-SI bug):
    #   1. Live trades.db rows when present — authoritative.
    #   2. Else fall back to the SI snapshot if any.
    #   3. Else leave empty so the UI renders MISSING.
    if trade_rows:
        strategy_rows = _strategy_rows_from_trade_rows(trade_rows)
        symbol_rows = _symbol_rows_from_trade_rows(trade_rows)
    elif si_report is not None:
        strategy_rows = _strategy_rows_from_si_report(si_report)
        symbol_rows = _symbol_rows_from_si_report(si_report)

    # Additive warning: flag the SI snapshot as stale when its generated_at is
    # older than the trades.db mtime or the latest close_date we just read.
    stale_warning = _si_stale_warning(si_report, db_path, trade_rows)
    if stale_warning:
        payload["missing"].append(stale_warning)

    # Closed/open counts (best-effort from trade rows or SI report).
    closed_n = 0
    open_n = 0
    if trade_rows:
        for r in trade_rows:
            if r.get("close_date") is None:
                open_n += 1
            else:
                closed_n += 1
    elif strategy_rows:
        for row in strategy_rows:
            c = row.get("closed_trades")
            o = row.get("open_trades")
            if isinstance(c, int):
                closed_n += c
            if isinstance(o, int):
                open_n += o

    # Source label reflects what actually populated the scorecards / metrics.
    # The live DB is authoritative whenever it returned rows; the SI snapshot
    # is annotated as "stale_superseded" when it exists but was overridden.
    source_label = "none"
    if trade_rows and si_report is not None:
        source_label = "trades_db (si_report_present_but_superseded)"
    elif trade_rows:
        source_label = "trades_db"
    elif si_report is not None:
        source_label = "si_report"

    payload["summary"] = {
        "strategy_count": len(strategy_rows),
        "symbol_count": len(symbol_rows),
        "trade_count": len(trade_rows) if trade_rows else (closed_n + open_n),
        "closed_trade_count": closed_n,
        "open_trade_count": open_n,
        "source": source_label,
    }
    payload["scorecards"] = _scorecard_rows_from_strategy_rows(strategy_rows)
    payload["strategy_metrics"] = strategy_rows
    payload["symbol_metrics"] = symbol_rows
    payload["gates"] = _collect_gates(root)

    if trade_rows:
        payload["daily_pnl_correlation"] = _compute_daily_pnl_correlation(trade_rows)
        payload["weekday_performance"] = _compute_weekday_performance(trade_rows)
        payload["month_performance"] = _compute_month_performance(trade_rows)
        pnl_r_series = _pnl_r_series(trade_rows)
        payload["monte_carlo_summary"] = _compute_monte_carlo(pnl_r_series)
        payload["risk_of_ruin"] = _compute_risk_of_ruin(pnl_r_series)
    else:
        for key in (
            "daily_pnl_correlation",
            "weekday_performance",
            "month_performance",
            "monte_carlo_summary",
            "risk_of_ruin",
        ):
            payload[key] = {
                "status": "MISSING",
                "reason": "no_trade_rows_available",
            }

    # Evidence Quality (UI explainer). Computed last so it reads from the
    # already-populated correlation block. Always present so the template
    # never has to handle a missing key.
    _corr_block = payload.get("daily_pnl_correlation") or {}
    _corr_day_count = _corr_block.get("day_count")
    if not isinstance(_corr_day_count, int):
        _corr_day_count = 0
    payload["evidence_quality"] = _compute_evidence_quality(
        closed_n=closed_n,
        strategy_rows=strategy_rows,
        correlation_day_count=_corr_day_count,
    )

    # Overall status: OK if anything loaded; MISSING otherwise.
    if (
        not strategy_rows
        and not symbol_rows
        and not trade_rows
        and not payload["gates"]
    ):
        payload["status"] = "MISSING"
    else:
        # Promote to OK even if some sub-sections are MISSING; the UI shows
        # MISSING per-section so the overall status just reflects "the page
        # has something to render".
        payload["status"] = "OK"

    return payload


__all__ = ["load_payload", "external_root"]
