"""Daily READ-ONLY learning report over the operator's real trade journal.

Posture (non-negotiable):
  * Research / observation only. No broker, no orders, no execution path.
  * trades.db is opened with the sqlite URI ``file:...?mode=ro`` so writes are
    impossible at the connection level. The external project is never touched.
  * The only files written live under ``C:\\SPARTA_BRAIN\\reports\\trade_learning\\``.
  * Every suggestion is emitted with status ``SUGGESTION_ONLY`` and the caveat
    "observation only; not applied". Nothing here changes any rule anywhere.

Usage:
    .venv\\Scripts\\python tools\\trade_journal_learning_report.py

Pure core: ``build_learning_report(trades, excursions, as_of)`` — deterministic
for fixed input (no clocks, no randomness, sorted keys everywhere).

Standard library only.
"""
from __future__ import annotations

import json
import sqlite3
import statistics
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tools.trade_journal_adapter import (  # noqa: E402  (reuse, never modify)
    _REL_TRADES_DB,
    _coerce_float,
    _parse_dt,
    external_root,
)

BANNER = (
    "READ ONLY · OBSERVATION ONLY · NO LIVE READINESS CLAIM · "
    "NO STRATEGY APPROVAL · NO BROKER / NO ORDER"
)
CAVEAT = "observation only; not applied"

MIN_PER_STRATEGY = 20
MIN_SIGNALS = 30
STOP_BREACH_R = -1.2          # planned max loss is -1R; below this = breach
PLANNED_MAX_LOSS_R = -1.0

STRATEGY_LABELS = {
    "D": "Donchian Breakout", "D2": "Donchian Breakout (loose)",
    "E": "EMA Cross", "E2": "EMA Cross (loose)",
    "F": "Fibonacci", "F2": "Fibonacci (loose)",
    "G": "Range Reversion",
}
_TREND_UP = "TREND_UP"
_TREND_DOWN = "TREND_DOWN"
_NO_TREND = ("RANGE", "CHOP", "COMPRESSION")
_WEEKDAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")

# Words that must never appear in any rendered output of this tool.
FORBIDDEN_WORDS = ("validated", "ready", "approved", "profitable strategy")

REPORT_DIR = _REPO_ROOT / "reports" / "trade_learning"


# ── small helpers ───────────────────────────────────────────────────────────

def _r(x: float | None, nd: int = 3) -> float | None:
    return None if x is None else round(float(x), nd)


def _pnl(row: dict[str, Any]) -> float | None:
    return _coerce_float(row.get("pnl_r"))


def _signal_key(row: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(row.get("open_date") or ""),
        str(row.get("symbol") or ""),
        str(row.get("direction") or "").lower(),
    )


def _alignment(row: dict[str, Any]) -> str:
    regime = row.get("regime_at_open")
    direction = str(row.get("direction") or "").lower()
    if regime is None or str(regime).strip() == "":
        return "UNLABELED"
    regime = str(regime).upper()
    if regime in _NO_TREND:
        return "NO_TREND_REGIME"
    if (regime == _TREND_DOWN and direction == "short") or (
        regime == _TREND_UP and direction == "long"
    ):
        return "ALIGNED"
    if regime in (_TREND_UP, _TREND_DOWN):
        return "COUNTER"
    return "UNLABELED"


def _stats(rows: list[dict[str, Any]]) -> dict[str, Any]:
    vals = [v for v in (_pnl(r) for r in rows) if v is not None]
    n = len(vals)
    if n == 0:
        return {"n": 0, "n_signals": 0, "sum_R": 0.0, "avg_R": None, "win_rate": None}
    return {
        "n": n,
        "n_signals": len({_signal_key(r) for r in rows if _pnl(r) is not None}),
        "sum_R": _r(sum(vals)),
        "avg_R": _r(sum(vals) / n),
        "win_rate": _r(sum(1 for v in vals if v > 0) / n),
    }


def _group(rows: list[dict[str, Any]], key_fn) -> dict[str, dict[str, Any]]:
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        k = key_fn(r)
        if k is None:
            continue
        buckets[str(k)].append(r)
    return {k: _stats(buckets[k]) for k in sorted(buckets)}


def _profit_factor(vals: list[float]) -> float | None:
    gains = sum(v for v in vals if v > 0)
    losses = -sum(v for v in vals if v < 0)
    if losses == 0:
        return None
    return _r(gains / losses)


def _days_between(a: Any, b: Any) -> float | None:
    da, db_ = _parse_dt(a), _parse_dt(b)
    if da is None or db_ is None:
        return None
    return (db_ - da).total_seconds() / 86400.0


def _weekday(row: dict[str, Any]) -> str | None:
    dt = _parse_dt(row.get("open_date"))
    return None if dt is None else _WEEKDAYS[dt.weekday()]


def _month(row: dict[str, Any]) -> str | None:
    dt = _parse_dt(row.get("close_date"))
    return None if dt is None else dt.strftime("%Y-%m")


# ── report sections ─────────────────────────────────────────────────────────

def _counts(trades: list[dict[str, Any]], closed: list[dict[str, Any]]) -> dict[str, Any]:
    raw_vals = [v for v in (_pnl(r) for r in closed) if v is not None]
    by_sig: dict[tuple, list[float]] = defaultdict(list)
    for r in closed:
        v = _pnl(r)
        if v is not None:
            by_sig[_signal_key(r)].append(v)
    best = [max(vs) for vs in by_sig.values()]
    mean = [sum(vs) / len(vs) for vs in by_sig.values()]
    n = len(raw_vals)
    return {
        "rows": len(trades),
        "closed": len(closed),
        "open": len(trades) - len(closed),
        "distinct_signals_all_rows": len({_signal_key(r) for r in trades}),
        "distinct_signals_closed": len(by_sig),
        "sum_R_raw": _r(sum(raw_vals)),
        "sum_R_dedup_best": _r(sum(best)),
        "sum_R_dedup_mean": _r(sum(mean)),
        "win_rate": _r(sum(1 for v in raw_vals if v > 0) / n) if n else None,
        "expectancy_R": _r(sum(raw_vals) / n) if n else None,
        "expectancy_R_dedup_mean": _r(sum(mean) / len(mean)) if mean else None,
        "profit_factor": _profit_factor(raw_vals),
        "dedup_key": "open_date+symbol+direction",
        "note": (
            "raw rows overstate the sample: the bot mirrors signals on binance "
            "and kraken and the loose '2' variants often fire on the same bar"
        ),
    }


def _stop_discipline(closed: list[dict[str, Any]]) -> dict[str, Any]:
    breaches = []
    excess = 0.0
    for r in closed:
        v = _pnl(r)
        if v is None or v >= STOP_BREACH_R:
            continue
        excess += PLANNED_MAX_LOSS_R - v
        breaches.append({
            "id": r.get("id"),
            "symbol": r.get("symbol"),
            "strategy": r.get("strategy"),
            "direction": r.get("direction"),
            "open_date": r.get("open_date"),
            "pnl_r": _r(v),
            "sl": _coerce_float(r.get("sl")),
            "close_price": _coerce_float(r.get("close_price")),
        })
    breaches.sort(key=lambda b: (b["pnl_r"] if b["pnl_r"] is not None else 0.0, str(b["id"])))
    return {
        "threshold_R": STOP_BREACH_R,
        "planned_max_loss_R": PLANNED_MAX_LOSS_R,
        "n_breaches": len(breaches),
        "total_excess_loss_R": _r(excess),
        "breaches": breaches,
    }


def _mfe_capture(
    closed: list[dict[str, Any]], excursions: dict[int, dict[str, Any]]
) -> dict[str, Any]:
    mfe_list: list[float] = []
    real_list: list[float] = []
    giveback: list[float] = []
    reached_2r_closed_below_1r = 0
    for r in closed:
        ex = excursions.get(r.get("id"))
        if not ex:
            continue
        mfe = _coerce_float(ex.get("max_favorable_R"))
        real = _pnl(r)
        if mfe is None or real is None or mfe < 1.0:
            continue
        mfe_list.append(mfe)
        real_list.append(real)
        gb = _coerce_float(ex.get("r_given_back_from_peak"))
        if gb is not None:
            giveback.append(gb)
        if (bool(ex.get("did_reach_2R")) or mfe >= 2.0) and real < 1.0:
            reached_2r_closed_below_1r += 1
    n = len(mfe_list)
    if n == 0:
        return {
            "n": 0, "status": "MISSING",
            "reason": "no closed trade with excursion row and max_favorable_R >= 1",
        }
    mean_mfe = statistics.fmean(mfe_list)
    mean_real = statistics.fmean(real_list)
    return {
        "n": n,
        "status": "OK",
        "mean_MFE_R": _r(mean_mfe),
        "mean_realized_R": _r(mean_real),
        "mean_r_given_back_from_peak": _r(statistics.fmean(giveback)) if giveback else None,
        "capture_ratio": _r(mean_real / mean_mfe) if mean_mfe else None,
        "reached_2R_but_closed_below_1R": reached_2r_closed_below_1r,
    }


def _holding(closed: list[dict[str, Any]]) -> dict[str, Any]:
    by_outcome: dict[str, list[float]] = defaultdict(list)
    for r in closed:
        d = _days_between(r.get("open_date"), r.get("close_date"))
        if d is None:
            continue
        by_outcome[str(r.get("outcome") or "UNKNOWN").upper()].append(d)
    out = {
        k: {"n": len(v), "mean_days": _r(statistics.fmean(v), 2), "max_days": _r(max(v), 2)}
        for k, v in sorted(by_outcome.items())
    }
    n_closed = len(closed)
    n_timeout = sum(1 for r in closed if str(r.get("outcome") or "").upper() == "TIMEOUT")
    return {
        "by_outcome": out,
        "timeout_share": _r(n_timeout / n_closed) if n_closed else None,
        "n_timeout": n_timeout,
    }


def _sample_quality(
    by_strategy: dict[str, dict[str, Any]], distinct_signals_closed: int
) -> dict[str, Any]:
    per = {}
    for s, st in by_strategy.items():
        per[s] = {
            "closed": st["n"],
            "closed_signals": st["n_signals"],
            "min_required": MIN_PER_STRATEGY,
            "label": "OK" if st["n"] >= MIN_PER_STRATEGY else "PRELIMINARY",
        }
    overall_ok = distinct_signals_closed >= MIN_SIGNALS
    return {
        "per_strategy": per,
        "dedup_signals": distinct_signals_closed,
        "min_signals": MIN_SIGNALS,
        "overall_label": "OK" if overall_ok else "PRELIMINARY",
        "overall_sample_ok": overall_ok,
        "note": "every conclusion below threshold is PRELIMINARY",
    }


def _suggestions(rep: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    overall_ok = rep["sample_quality"]["overall_sample_ok"]

    def add(sid: str, rule: str, evidence: dict[str, Any], sample_ok: bool) -> None:
        out.append({
            "id": sid,
            "rule": rule,
            "evidence": evidence,
            "status": "SUGGESTION_ONLY",
            "sample_ok": bool(sample_ok),
            "label": "OK" if sample_ok else "PRELIMINARY",
            "caveat": CAVEAT,
        })

    # 1. counter-trend groups losing money
    for key, st in rep["by_regime_x_direction"].items():
        if st.get("alignment") != "COUNTER":
            continue
        if st["n"] >= 4 and st["avg_R"] is not None and st["avg_R"] < 0:
            regime, direction = key.split("|", 1)
            add(
                f"block_{direction}_in_{regime}",
                f"block {direction} when regime={regime} (counter-trend)",
                {k: st[k] for k in ("n", "n_signals", "sum_R", "avg_R", "win_rate")},
                overall_ok,
            )

    # 2. strategies with negative expectancy
    for s, st in rep["by_strategy"].items():
        if st["n"] >= 8 and st["avg_R"] is not None and st["avg_R"] < -0.3:
            add(
                f"review_pause_{s}",
                f"review/pause strategy {s} ({STRATEGY_LABELS.get(s, s)})",
                {k: st[k] for k in ("n", "n_signals", "sum_R", "avg_R", "win_rate")},
                overall_ok and st["n"] >= MIN_PER_STRATEGY,
            )

    # 3. stop discipline
    sd = rep["stop_discipline"]
    if (sd["total_excess_loss_R"] or 0.0) > 2.0:
        add(
            "enforce_hard_stop",
            "enforce hard stop / investigate fills (losses beyond planned -1R)",
            {
                "n_breaches": sd["n_breaches"],
                "total_excess_loss_R": sd["total_excess_loss_R"],
                "worst_ids": [b["id"] for b in sd["breaches"][:5]],
            },
            overall_ok,
        )

    # 4. MFE capture
    mfe = rep["mfe_capture"]
    if mfe.get("n", 0) >= 5 and mfe.get("capture_ratio") is not None and mfe["capture_ratio"] < 0.7:
        add(
            "partial_tp_or_trail_2R",
            "add partial take-profit or trailing stop at 2R",
            {k: mfe[k] for k in (
                "n", "mean_MFE_R", "mean_realized_R", "capture_ratio",
                "reached_2R_but_closed_below_1R",
            )},
            overall_ok,
        )

    # 5. weekday noise flags
    for wd, st in rep["by_weekday"].items():
        if st["n"] >= 6 and st["avg_R"] is not None and st["avg_R"] < -1:
            add(
                f"flag_weekday_{wd}",
                f"flag {wd} entries for review (likely noise)",
                {k: st[k] for k in ("n", "n_signals", "sum_R", "avg_R", "win_rate")},
                overall_ok,
            )

    out.sort(key=lambda s: s["id"])
    return out


# ── public pure builder ─────────────────────────────────────────────────────

def build_learning_report(
    trades: list[dict[str, Any]],
    excursions: dict[int, dict[str, Any]],
    as_of: str,
) -> dict[str, Any]:
    """Pure, deterministic. ``trades`` = rows of the trades table as dicts;
    ``excursions`` = {trade_id: excursion row}. Closed = close_date not None."""
    trades = [dict(t) for t in trades]
    closed = [t for t in trades if t.get("close_date") not in (None, "")]

    by_strategy = _group(closed, lambda r: str(r.get("strategy") or "UNKNOWN"))

    rxd: dict[str, dict[str, Any]] = {}
    grouped = _group(
        closed,
        lambda r: f"{str(r.get('regime_at_open') or 'NONE').upper()}|{str(r.get('direction') or '').lower()}",
    )
    for key, st in grouped.items():
        regime, direction = key.split("|", 1)
        probe = {"regime_at_open": None if regime == "NONE" else regime, "direction": direction}
        rxd[key] = {**st, "alignment": _alignment(probe)}

    rep: dict[str, Any] = {
        "banner": BANNER,
        "posture": {
            "mode": "READ_ONLY_OBSERVATION",
            "broker": "NONE",
            "orders": "NONE",
            "external_project_modified": False,
            "rules_applied": False,
        },
        "as_of": as_of,
        "thresholds": {
            "MIN_PER_STRATEGY": MIN_PER_STRATEGY,
            "MIN_SIGNALS": MIN_SIGNALS,
            "STOP_BREACH_R": STOP_BREACH_R,
        },
        "strategy_labels": dict(STRATEGY_LABELS),
        "counts": _counts(trades, closed),
        "by_strategy": by_strategy,
        "by_regime_x_direction": rxd,
        "by_alignment": _group(closed, _alignment),
        "by_outcome": _group(closed, lambda r: str(r.get("outcome") or "UNKNOWN").upper()),
        "by_exchange": _group(closed, lambda r: str(r.get("exchange") or "UNKNOWN")),
        "by_weekday": _group(closed, _weekday),
        "by_month": _group(closed, _month),
        "stop_discipline": _stop_discipline(closed),
        "mfe_capture": _mfe_capture(closed, excursions or {}),
        "holding": _holding(closed),
    }
    rep["sample_quality"] = _sample_quality(by_strategy, rep["counts"]["distinct_signals_closed"])
    rep["suggestions"] = _suggestions(rep)
    return rep


# ── markdown render ─────────────────────────────────────────────────────────

def _fmt(v: Any) -> str:
    if v is None:
        return "-"
    if isinstance(v, float):
        return f"{v:.3f}"
    return str(v)


def _table(title: str, groups: dict[str, dict[str, Any]], extra: tuple[str, ...] = ()) -> list[str]:
    cols = ("n", "n_signals", "sum_R", "avg_R", "win_rate") + extra
    lines = [f"### {title}", "", "| bucket | " + " | ".join(cols) + " |",
             "|" + "---|" * (len(cols) + 1)]
    for k, st in groups.items():
        lines.append(f"| {k} | " + " | ".join(_fmt(st.get(c)) for c in cols) + " |")
    lines.append("")
    return lines


def render_markdown(rep: dict[str, Any]) -> str:
    c = rep["counts"]
    sq = rep["sample_quality"]
    L = [
        f"# Trade Journal Learning Report — {rep['as_of']}",
        "",
        f"**{rep['banner']}**",
        "",
        f"Sample label: **{sq['overall_label']}** "
        f"(dedup closed signals {sq['dedup_signals']} vs MIN_SIGNALS={sq['min_signals']}). "
        "Every conclusion below threshold is PRELIMINARY.",
        "",
        "## Counts (closed trades)",
        "",
        f"- rows {c['rows']} · closed {c['closed']} · open {c['open']} · "
        f"distinct signals (closed) {c['distinct_signals_closed']}",
        f"- sum_R raw {_fmt(c['sum_R_raw'])} · dedup best-row {_fmt(c['sum_R_dedup_best'])} · "
        f"dedup mean-row {_fmt(c['sum_R_dedup_mean'])}",
        f"- win rate {_fmt(c['win_rate'])} · expectancy {_fmt(c['expectancy_R'])} R "
        f"(dedup mean {_fmt(c['expectancy_R_dedup_mean'])}) · profit factor {_fmt(c['profit_factor'])}",
        f"- note: {c['note']}",
        "",
        "## Breakdowns",
        "",
    ]
    L += _table("By strategy", rep["by_strategy"])
    L += _table("By regime x direction", rep["by_regime_x_direction"], ("alignment",))
    L += _table("By alignment", rep["by_alignment"])
    L += _table("By outcome", rep["by_outcome"])
    L += _table("By exchange", rep["by_exchange"])
    L += _table("By weekday (open_date)", rep["by_weekday"])
    L += _table("By month (close_date)", rep["by_month"])

    sd = rep["stop_discipline"]
    L += ["## Stop discipline", "",
          f"- breaches (pnl_r < {sd['threshold_R']}): {sd['n_breaches']} · "
          f"total excess loss beyond -1R: {_fmt(sd['total_excess_loss_R'])} R", ""]
    if sd["breaches"]:
        L += ["| id | symbol | strategy | dir | open_date | pnl_r | sl | close_price |",
              "|---|---|---|---|---|---|---|---|"]
        for b in sd["breaches"]:
            L.append(
                f"| {b['id']} | {b['symbol']} | {b['strategy']} | {b['direction']} | "
                f"{b['open_date']} | {_fmt(b['pnl_r'])} | {_fmt(b['sl'])} | {_fmt(b['close_price'])} |"
            )
        L.append("")

    m = rep["mfe_capture"]
    L += ["## MFE capture (closed, excursion row, MFE >= 1R)", ""]
    if m.get("status") == "OK":
        L += [f"- n {m['n']} · mean MFE {_fmt(m['mean_MFE_R'])} R · mean realized "
              f"{_fmt(m['mean_realized_R'])} R · mean given back {_fmt(m['mean_r_given_back_from_peak'])} R",
              f"- capture ratio {_fmt(m['capture_ratio'])} · reached 2R but closed below 1R: "
              f"{m['reached_2R_but_closed_below_1R']}", ""]
    else:
        L += [f"- MISSING: {m.get('reason')}", ""]

    h = rep["holding"]
    L += ["## Holding", "",
          f"- TIMEOUT share {_fmt(h['timeout_share'])} ({h['n_timeout']} closes)"]
    for k, v in h["by_outcome"].items():
        L.append(f"- {k}: n {v['n']} · mean {_fmt(v['mean_days'])} d · max {_fmt(v['max_days'])} d")
    L.append("")

    L += ["## Sample quality", ""]
    for s, v in sq["per_strategy"].items():
        L.append(f"- {s}: closed {v['closed']} (signals {v['closed_signals']}) vs "
                 f"{v['min_required']} → {v['label']}")
    L.append("")

    L += ["## Rule suggestions (SUGGESTION_ONLY)", ""]
    if not rep["suggestions"]:
        L.append("- none triggered by the current thresholds")
    for s in rep["suggestions"]:
        L.append(f"- **{s['id']}** [{s['label']}] — {s['rule']} · evidence "
                 f"{json.dumps(s['evidence'], sort_keys=True)} · {s['caveat']}")
    L += ["", f"_{rep['banner']}_", ""]
    return "\n".join(L)


def forbidden_words_found(text: str) -> list[str]:
    low = text.lower()
    return [w for w in FORBIDDEN_WORDS if w in low]


# ── read-only loading ───────────────────────────────────────────────────────

def load_journal_ro(db_path: Path) -> tuple[list[dict[str, Any]], dict[int, dict[str, Any]]]:
    """Open trades.db strictly read-only (URI mode=ro) and pull both tables."""
    uri = f"file:{db_path.as_posix()}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    try:
        trades = [dict(r) for r in conn.execute("SELECT * FROM trades ORDER BY id")]
        excursions: dict[int, dict[str, Any]] = {}
        try:
            for r in conn.execute("SELECT * FROM trade_excursions"):
                d = dict(r)
                excursions[int(d["trade_id"])] = d
        except sqlite3.OperationalError:
            pass
    finally:
        conn.close()
    return trades, excursions


def _register_manual_entry() -> None:
    """One-shot /guide registration. Never allowed to break the report."""
    try:
        import database as db  # local sparta.db; unrelated to trades.db
        db.upsert_manual_entry(
            "trade_journal_learning",
            module_name="Trade Journal Learning Report",
            category="Trading",
            status="live",
            short_description=(
                "Daily read-only learning pass over the real trade journal; "
                "emits rule SUGGESTIONS only (never applied)."
            ),
            how_it_works=(
                "Opens obsidian-trade-logger trades.db with sqlite mode=ro, "
                "dedups mirrored binance/kraken + loose-variant rows, computes "
                "by-strategy/regime/alignment/weekday stats, stop-discipline "
                "breaches, MFE capture and holding; suggestions are generated "
                "mechanically and labelled PRELIMINARY below sample thresholds."
            ),
            when_to_use=(
                "Daily review of what the journal says. Observation only: no "
                "broker, no orders, no rule changes."
            ),
            user_action=(
                "Run `.venv\\Scripts\\python tools\\trade_journal_learning_report.py`; "
                "read reports/trade_learning/latest.md (history in history.jsonl)."
            ),
            sort_order=96,
        )
    except Exception as exc:  # noqa: BLE001 - registration is best-effort
        print(f"[manual-entry] skipped: {type(exc).__name__}: {exc}")


def main() -> int:
    db_path = external_root().joinpath(*_REL_TRADES_DB)
    if not db_path.exists():
        print(f"trades.db not found: {db_path}")
        return 1
    as_of = datetime.now().strftime("%Y-%m-%d")  # local operator date
    trades, excursions = load_journal_ro(db_path)
    rep = build_learning_report(trades, excursions, as_of)
    rep["source"] = {"db_path": str(db_path), "open_mode": "uri mode=ro"}
    md = render_markdown(rep)
    bad = forbidden_words_found(md)
    if bad:
        print(f"WARNING forbidden words in render: {bad}")

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    (REPORT_DIR / "latest.json").write_text(
        json.dumps(rep, indent=2, sort_keys=True), encoding="utf-8"
    )
    (REPORT_DIR / "latest.md").write_text(md, encoding="utf-8")
    c = rep["counts"]
    line = {
        "as_of": as_of,
        "rows": c["rows"],
        "closed": c["closed"],
        "dedup_signals": c["distinct_signals_closed"],
        "sum_R_raw": c["sum_R_raw"],
        "sum_R_dedup_best": c["sum_R_dedup_best"],
        "sum_R_dedup_mean": c["sum_R_dedup_mean"],
        "expectancy_R": c["expectancy_R"],
        "n_suggestions": len(rep["suggestions"]),
        "sample_label": rep["sample_quality"]["overall_label"],
    }
    with (REPORT_DIR / "history.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(line, sort_keys=True) + "\n")

    _register_manual_entry()
    print(BANNER)
    print(f"wrote {REPORT_DIR / 'latest.json'}, latest.md, history.jsonl (+1 line)")
    print(f"closed {c['closed']} rows / {c['distinct_signals_closed']} signals · "
          f"suggestions {len(rep['suggestions'])} · sample {rep['sample_quality']['overall_label']}")
    try:  # additive: feed the forward hypothesis ledger; never allowed to break the report
        from tools import trade_hypothesis_ledger as thl
        led = thl.run_cycle(rep, trades, excursions, as_of)
        print(f"[hypothesis-ledger] {led['_last_run']['by_status']} → {thl.LEDGER_PATH}")
    except Exception as exc:  # noqa: BLE001
        print(f"[hypothesis-ledger] skipped: {type(exc).__name__}: {exc}")
    return 0


__all__ = [
    "build_learning_report", "render_markdown", "load_journal_ro",
    "forbidden_words_found", "BANNER", "CAVEAT", "MIN_PER_STRATEGY", "MIN_SIGNALS",
]

if __name__ == "__main__":
    sys.exit(main())
