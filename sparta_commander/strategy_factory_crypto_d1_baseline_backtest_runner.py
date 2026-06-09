"""Crypto-D1 Baseline Backtest Runner (READ-ONLY, HUMAN-AUTHORIZED SINGLE RUN).

The human-authorized companion to the PREP-ONLY contract. It RUNS the one approved
baseline -- ``long_only_buy_and_hold_equal_weight_spot_d1`` -- over the already
QA-passed local staged spot CSVs, and writes ONLY baseline report artifacts under
``reports/crypto_d1_baseline_backtest/``.

What it does:
  - refuses to run unless ``check_baseline_prep_readiness`` returns READY (every
    staged file present, canonical schema, non-empty, byte-identical to what the
    Real Data QA run recorded, qa_report verdict PASS);
  - reads ONLY the three staged files
    data/crypto_d1_spot/raw/{BTC,ETH,SOL}_1d.csv (read-only);
  - runs a single forward pass: buy equal-weight at the first common date's close,
    hold to the last common date -- NO rebalancing, NO parameters, NO lookahead;
  - reports total return, CAGR, max drawdown, volatility, Sharpe, trade count and
    a per-symbol breakdown.

What it does NOT do: no optimization, no parameter search, no walk-forward, no
lookahead, no shorting, no leverage/margin, no order execution, no broker/exchange,
no paper/live/micro-live, no network, no credentials. It UNLOCKS no gate: running
this approved baseline leaves paper_trading_gate and micro_live_gate LOCKED.

Public API:
  - RUNNER_SCHEMA_VERSION / RUNNER_LABEL / RUNNER_MODE
  - BASELINE_REPORT_DIR / INITIAL_CAPITAL
  - VERDICT_BASELINE_COMPLETE / VERDICT_BLOCKED_NOT_READY
  - get_baseline_backtest_runner_label()
  - run_baseline_backtest(repo_root=".", *, write=True)
  - validate_baseline_backtest_report(report)
  - render_baseline_backtest_markdown(report)
"""

from __future__ import annotations

import csv
import datetime
import json
import math
import os
import statistics
from typing import Any

from sparta_commander.strategy_factory_crypto_d1_real_data_qa_runner import (
    QA_APPROVED_INPUT_DIR,
    QA_REQUIRED_FIELDS,
    QA_REQUIRED_SYMBOLS,
)
from sparta_commander.strategy_factory_crypto_d1_baseline_backtest_prep_contract import (
    BASELINE_STRATEGY_ID,
    VERDICT_READY,
    baseline_run_constraints,
    check_baseline_prep_readiness,
)

RUNNER_SCHEMA_VERSION = "strategy_factory_crypto_d1_baseline_backtest_runner.v1"
RUNNER_LABEL = "Crypto-D1 Baseline Backtest Runner (long-only buy & hold, equal weight)"
RUNNER_MODE = "RESEARCH_ONLY"

BASELINE_REPORT_DIR = "reports/crypto_d1_baseline_backtest"
INITIAL_CAPITAL = 10000.0

VERDICT_BASELINE_COMPLETE = "BASELINE_COMPLETE"
VERDICT_BLOCKED_NOT_READY = "BLOCKED_NOT_READY"

_TRADING_DAYS_PER_YEAR = 365  # crypto trades every calendar day
_DATE_IDX = QA_REQUIRED_FIELDS.index("date")
_CLOSE_IDX = QA_REQUIRED_FIELDS.index("close")


def get_baseline_backtest_runner_label() -> str:
    """Human label for the recognized Crypto-D1 baseline backtest runner."""
    return RUNNER_LABEL


def _read_close_series(path: str) -> dict[str, float]:
    """Read a staged CSV read-only and return an ordered {date: close} map. Skips a
    canonical header row and any blank rows; never raises on a single bad row."""
    series: dict[str, float] = {}
    if not os.path.isfile(path):
        return series
    with open(path, "r", encoding="utf-8", newline="") as fh:
        rows = [r for r in csv.reader(fh) if r and any(c.strip() for c in r)]
    if not rows:
        return series
    header = [c.strip().lower() for c in rows[0]]
    data = rows[1:] if header == [c.lower() for c in QA_REQUIRED_FIELDS] else rows
    for row in data:
        if len(row) <= _CLOSE_IDX:
            continue
        date = row[_DATE_IDX].strip()
        try:
            close = float(row[_CLOSE_IDX].strip())
        except (TypeError, ValueError):
            continue
        if date and close > 0:
            series[date] = close
    return series


def _iso_to_date(value: str) -> datetime.date:
    return datetime.date(int(value[0:4]), int(value[5:7]), int(value[8:10]))


def _max_drawdown(values: list[float]) -> float:
    """Most negative peak-to-trough fractional drawdown over an equity curve. <= 0."""
    peak = values[0]
    worst = 0.0
    for v in values:
        if v > peak:
            peak = v
        dd = v / peak - 1.0 if peak > 0 else 0.0
        if dd < worst:
            worst = dd
    return worst


def run_baseline_backtest(repo_root: str = ".", *, write: bool = True) -> dict[str, Any]:
    """Run the single approved baseline (long-only, equal-weight, buy & hold) over the
    QA-passed staged CSVs and return a report dict. Refuses to run (verdict
    BLOCKED_NOT_READY, writes nothing) unless baseline prep is READY. Reads only the
    three staged files; when write=True writes ONLY the baseline report (json + md)
    under reports/crypto_d1_baseline_backtest/. Never fetches, never executes an
    order, never touches a gate."""
    constraints = baseline_run_constraints()
    prep = check_baseline_prep_readiness(repo_root)

    # Hard gate: only run on a READY prep, and only under the contract constraints.
    forbidden_on = [
        k
        for k in ("optimization", "parameter_search", "walk_forward",
                  "allow_shorting", "allow_leverage", "allow_margin")
        if constraints.get(k) is not False
    ]
    if prep["verdict"] != VERDICT_READY or forbidden_on:
        blockers = list(prep.get("blockers", []))
        if prep["verdict"] != VERDICT_READY:
            blockers.append("baseline_prep_not_ready")
        blockers.extend("constraint_violation:" + k for k in forbidden_on)
        return _blocked_report(blockers, constraints)

    input_dir = os.path.join(repo_root, QA_APPROVED_INPUT_DIR)
    series_by_symbol: dict[str, dict[str, float]] = {}
    files_read: list[str] = []
    for sym in QA_REQUIRED_SYMBOLS:
        path = os.path.join(input_dir, sym + "_1d.csv")
        series_by_symbol[sym] = _read_close_series(path)
        files_read.append(path)

    # Common trading dates across all symbols (no lookahead: we only ever use the
    # entry-date close to size positions, then mark to subsequent closes).
    common = set.intersection(*(set(s.keys()) for s in series_by_symbol.values()))
    common_dates = sorted(common)
    if len(common_dates) < 2:
        return _blocked_report(["insufficient_common_history"], constraints)

    entry_date, exit_date = common_dates[0], common_dates[-1]
    n = len(QA_REQUIRED_SYMBOLS)
    alloc = INITIAL_CAPITAL / n

    units: dict[str, float] = {}
    per_symbol: list[dict[str, Any]] = []
    for sym in QA_REQUIRED_SYMBOLS:
        entry_close = series_by_symbol[sym][entry_date]
        exit_close = series_by_symbol[sym][exit_date]
        units[sym] = alloc / entry_close
        final_value = units[sym] * exit_close
        per_symbol.append(
            {
                "symbol": sym,
                "entry_date": entry_date,
                "exit_date": exit_date,
                "entry_close": entry_close,
                "exit_close": exit_close,
                "allocation_weight": 1.0 / n,
                "allocated_capital": alloc,
                "final_value": final_value,
                "symbol_return": exit_close / entry_close - 1.0,
                "contribution_to_portfolio": final_value / INITIAL_CAPITAL,
            }
        )

    equity_curve: list[dict[str, Any]] = []
    values: list[float] = []
    for date in common_dates:
        value = sum(units[sym] * series_by_symbol[sym][date] for sym in QA_REQUIRED_SYMBOLS)
        equity_curve.append({"date": date, "value": value})
        values.append(value)

    daily_returns = [values[i] / values[i - 1] - 1.0 for i in range(1, len(values))]
    total_return = values[-1] / INITIAL_CAPITAL - 1.0
    days = max(1, (_iso_to_date(exit_date) - _iso_to_date(entry_date)).days)
    years = days / 365.25
    cagr = (values[-1] / INITIAL_CAPITAL) ** (1.0 / years) - 1.0 if years > 0 else 0.0
    max_dd = _max_drawdown(values)
    vol = (
        statistics.stdev(daily_returns) * math.sqrt(_TRADING_DAYS_PER_YEAR)
        if len(daily_returns) >= 2
        else 0.0
    )
    mean_daily = statistics.fmean(daily_returns) if daily_returns else 0.0
    sd_daily = statistics.stdev(daily_returns) if len(daily_returns) >= 2 else 0.0
    sharpe = (
        (mean_daily / sd_daily) * math.sqrt(_TRADING_DAYS_PER_YEAR) if sd_daily > 0 else 0.0
    )

    performance = {
        "initial_capital": INITIAL_CAPITAL,
        "final_value": values[-1],
        "total_return": total_return,
        "cagr": cagr,
        "max_drawdown": max_dd,
        "annualized_volatility": vol,
        "sharpe_ratio": sharpe,
        "trading_days": len(common_dates),
        "calendar_days": days,
        "entry_date": entry_date,
        "exit_date": exit_date,
    }

    # Buy & hold equal weight = one buy per symbol at entry; no rebalances, no exits
    # executed during the run (positions marked to market, never traded).
    trade_summary = {
        "trade_count": n,
        "buys": n,
        "sells": 0,
        "rebalances": 0,
        "exits_executed_during_run": 0,
        "single_pass": True,
    }

    report = _base_report(constraints)
    report.update(
        {
            "verdict": VERDICT_BASELINE_COMPLETE,
            "blockers": [],
            "baseline_prep_verdict": prep["verdict"],
            "symbols": list(QA_REQUIRED_SYMBOLS),
            "performance": performance,
            "trade_summary": trade_summary,
            "per_symbol": per_symbol,
            "equity_curve": equity_curve,
            "files_read": files_read,
        }
    )

    files_written: list[str] = []
    if write:
        rep_dir = os.path.join(repo_root, BASELINE_REPORT_DIR)
        os.makedirs(rep_dir, exist_ok=True)
        rep_json = os.path.join(rep_dir, "baseline_backtest_report.json")
        with open(rep_json, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2)
        files_written.append(rep_json)
        rep_md = os.path.join(rep_dir, "baseline_backtest_report.md")
        with open(rep_md, "w", encoding="utf-8") as fh:
            fh.write(render_baseline_backtest_markdown(report))
        files_written.append(rep_md)

    report["files_written"] = files_written
    return report


def _base_report(constraints: dict[str, Any]) -> dict[str, Any]:
    """Common report skeleton carrying the read-only safety posture. Running this
    approved baseline changes NO gate: paper / micro-live stay LOCKED."""
    return {
        "schema_version": RUNNER_SCHEMA_VERSION,
        "label": RUNNER_LABEL,
        "mode": RUNNER_MODE,
        "strategy_id": BASELINE_STRATEGY_ID,
        "authorization": "APPROVE_BASELINE_BACKTEST_RUN_READ_ONLY",
        "run_constraints": dict(constraints),
        # Capability posture: a single read-only backtest pass; nothing live.
        "executes_orders": False,
        "ran_optimization": False,
        "ran_parameter_search": False,
        "ran_walk_forward": False,
        "used_lookahead": False,
        "touches_broker_or_exchange": False,
        "uses_only_qa_passed_inputs": True,
        # Gate posture (UNCHANGED by this run):
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
        "unlocks_downstream_gate": False,
        "no_network_used": True,
        "no_credentials_used": True,
        "manual_csv_only": True,
    }


def _blocked_report(blockers: list[str], constraints: dict[str, Any]) -> dict[str, Any]:
    """A refusal report: prep was not READY (or a constraint was violated), so the
    baseline did NOT run and nothing was written."""
    report = _base_report(constraints)
    report.update(
        {
            "verdict": VERDICT_BLOCKED_NOT_READY,
            "blockers": list(blockers),
            "symbols": list(QA_REQUIRED_SYMBOLS),
            "performance": None,
            "trade_summary": None,
            "per_symbol": [],
            "equity_curve": [],
            "files_read": [],
            "files_written": [],
        }
    )
    return report


def validate_baseline_backtest_report(report: Any) -> dict[str, Any]:
    """Validate (read-only) a baseline report's shape and safety invariants. Returns
    {"valid": bool, "errors": [...]}; never raises."""
    errors: list[str] = []
    if not isinstance(report, dict):
        return {"valid": False, "errors": ["report_not_a_dict"]}
    r = report

    if r.get("verdict") not in (VERDICT_BASELINE_COMPLETE, VERDICT_BLOCKED_NOT_READY):
        errors.append("bad_verdict")
    if r.get("schema_version") != RUNNER_SCHEMA_VERSION:
        errors.append("bad_schema_version")
    if r.get("strategy_id") != BASELINE_STRATEGY_ID:
        errors.append("bad_strategy_id")

    must_be_locked = ("paper_trading_gate_locked", "micro_live_gate_locked")
    for key in must_be_locked:
        if r.get(key) is not True:
            errors.append("gate_not_locked:" + key)

    must_be_false = (
        "executes_orders",
        "ran_optimization",
        "ran_parameter_search",
        "ran_walk_forward",
        "used_lookahead",
        "touches_broker_or_exchange",
        "unlocks_downstream_gate",
    )
    for key in must_be_false:
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)

    if r.get("verdict") == VERDICT_BASELINE_COMPLETE:
        perf = r.get("performance")
        if not isinstance(perf, dict):
            errors.append("performance_missing")
        ts = r.get("trade_summary")
        if not isinstance(ts, dict) or ts.get("sells", None) != 0:
            errors.append("trade_summary_not_long_only_buy_and_hold")

    return {"valid": not errors, "errors": errors}


def _pct(x: Any) -> str:
    try:
        return f"{float(x) * 100:.2f}%"
    except (TypeError, ValueError):
        return str(x)


def render_baseline_backtest_markdown(report: Any) -> str:
    """Render a baseline report as deterministic markdown. Pure string work."""
    r = report if isinstance(report, dict) else {}
    lines: list[str] = []
    lines.append("# Crypto-D1 Baseline Backtest (long-only buy & hold, equal weight)")
    lines.append("")
    lines.append("- Verdict: " + str(r.get("verdict", "")))
    lines.append("- Strategy: " + str(r.get("strategy_id", "")))
    lines.append("- Authorization: " + str(r.get("authorization", "")))
    blockers = r.get("blockers") or []
    lines.append("- Blockers: " + ("none" if not blockers else ", ".join(blockers)))
    lines.append("")
    perf = r.get("performance")
    if isinstance(perf, dict):
        lines.append("## Performance")
        lines.append("- Window: " + str(perf.get("entry_date")) + " -> " + str(perf.get("exit_date"))
                     + " (" + str(perf.get("trading_days")) + " trading days)")
        lines.append("- Initial capital: " + str(perf.get("initial_capital")))
        lines.append("- Final value: " + f"{float(perf.get('final_value', 0)):.2f}")
        lines.append("- Total return: " + _pct(perf.get("total_return")))
        lines.append("- CAGR: " + _pct(perf.get("cagr")))
        lines.append("- Max drawdown: " + _pct(perf.get("max_drawdown")))
        lines.append("- Annualized volatility: " + _pct(perf.get("annualized_volatility")))
        lines.append("- Sharpe ratio: " + f"{float(perf.get('sharpe_ratio', 0)):.2f}")
        lines.append("")
    ts = r.get("trade_summary")
    if isinstance(ts, dict):
        lines.append("## Trades")
        lines.append("- Trade count: " + str(ts.get("trade_count"))
                     + " (buys=" + str(ts.get("buys"))
                     + ", sells=" + str(ts.get("sells"))
                     + ", rebalances=" + str(ts.get("rebalances")) + ")")
        lines.append("")
    lines.append("## Per-symbol breakdown")
    for s in r.get("per_symbol", []):
        lines.append(
            "- " + str(s.get("symbol"))
            + ": return=" + _pct(s.get("symbol_return"))
            + ", entry=" + str(s.get("entry_close"))
            + " -> exit=" + str(s.get("exit_close"))
            + ", contribution=" + _pct(s.get("contribution_to_portfolio"))
        )
    lines.append("")
    lines.append("## Gates (read-only metadata, UNCHANGED)")
    lines.append("- paper_trading_gate: LOCKED")
    lines.append("- micro_live_gate: LOCKED")
    lines.append("- executes_orders: False")
    lines.append("- touches_broker_or_exchange: False")
    return "\n".join(lines)


if __name__ == "__main__":  # pragma: no cover
    out = run_baseline_backtest(repo_root=".", write=False)
    print(render_baseline_backtest_markdown(out))
