"""Crypto-D1 V2 SIMULATED Paper-Trading Runner (NO LIVE MONEY, HUMAN-AUTHORIZED).

The human-authorized companion to the V2 paper-trading PREP-ONLY contract. It RUNS the
single selected variant ``V2_trend_plus_cash_regime`` in SIMULATED paper mode over the
already QA-passed local staged spot CSVs (BTC/ETH/SOL) and writes ONLY simulated paper
logs / reports under ``reports/crypto_d1_paper_prep/``.

It is a SIMULATION end-to-end:
  - starting equity is 10000 USDT of SIMULATED capital;
  - every fill is a model fill at that day's QA-passed close, charged the prep
    contract's assumed fee + slippage; NO real order is ever placed;
  - it is long-only with the pinned V2 rules (200-day trend filter; cash regime
    requiring >= 2 of 3 sleeves in trend); no leverage / shorting / margin -- ever;
  - the prep contract's kill switch is enforced live: a daily mark-to-market loss
    beyond -10%, a drawdown beyond -50%, or stale data beyond 48h FLATTENS the book to
    cash and HALTS; nothing auto-resumes (a human must restart).

It refuses to run (verdict BLOCKED_NOT_READY, writes nothing) unless
``check_paper_prep_readiness`` is READY -- i.e. the variant-backtest review APPROVED
paper prep for exactly V2. It reads ONLY the three staged files
``data/crypto_d1_spot/raw/{BTC,ETH,SOL}_1d.csv``.

It connects to NO broker and NO exchange, uses NO network and NO credentials, executes
NO real order, and UNLOCKS no gate: paper_trading_gate, micro_live_gate and the live
gate all stay LOCKED. Promoting V2 to a REAL (micro-live) account requires a SEPARATE
explicit human command.

Public API:
  - PAPER_RUN_SCHEMA_VERSION / PAPER_RUN_LABEL / PAPER_RUN_MODE
  - PAPER_LOG_DIR / SELECTED_VARIANT_ID
  - VERDICT_PAPER_RUN_COMPLETE / VERDICT_BLOCKED_NOT_READY
  - get_paper_run_label()
  - run_simulated_paper(repo_root=".", *, write=True)
  - validate_paper_run_report(report)
  - render_paper_run_markdown(report)
"""

from __future__ import annotations

import json
import math
import os
import statistics
from typing import Any

from sparta_commander.strategy_factory_crypto_d1_real_data_qa_runner import (
    QA_APPROVED_INPUT_DIR,
    QA_REQUIRED_SYMBOLS,
)
from sparta_commander.strategy_factory_crypto_d1_baseline_backtest_runner import (
    INITIAL_CAPITAL,
    _TRADING_DAYS_PER_YEAR,
    _iso_to_date,
    _max_drawdown,
    _read_close_series,
)
from sparta_commander.strategy_factory_crypto_d1_variant_backtest_runner import (
    _sma,
    _target_weights,
)
from sparta_commander.strategy_factory_crypto_d1_paper_trading_prep_contract import (
    PAPER_LOG_DIR,
    SELECTED_VARIANT_ID,
    VERDICT_READY,
    build_paper_prep_config,
    check_paper_prep_readiness,
)

PAPER_RUN_SCHEMA_VERSION = "strategy_factory_crypto_d1_paper_trading_run_simulated.v1"
PAPER_RUN_LABEL = "Crypto-D1 V2 SIMULATED Paper-Trading Runner (NO LIVE MONEY)"
PAPER_RUN_MODE = "RESEARCH_ONLY"

VERDICT_PAPER_RUN_COMPLETE = "PAPER_RUN_COMPLETE"
VERDICT_BLOCKED_NOT_READY = "BLOCKED_NOT_READY"

_AUTHORIZATION = "APPROVE_PAPER_TRADING_RUN_SIMULATED_NO_LIVE_MONEY"

# After a simulated paper run, the ONLY thing a human could authorize next is a REAL
# micro-live trial -- which stays LOCKED and is NOT part of this module.
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_MICRO_LIVE_TRIAL_REAL_MONEY_SEPARATE_GATE"

_KILL_HARD_DRAWDOWN = "hard_drawdown_kill"
_KILL_DAILY_LOSS = "daily_loss_halt"
_KILL_DATA_STALENESS = "data_staleness_halt"


def get_paper_run_label() -> str:
    """Human label for the recognized Crypto-D1 V2 simulated paper-trading runner."""
    return PAPER_RUN_LABEL


def _v2_rule_params(config: dict[str, Any]) -> tuple[int, int]:
    """Pull V2's pinned trend-filter SMA window and cash-regime breadth from the prep
    config's risk limits. Pure."""
    limits = config.get("risk_limits") or {}
    sma_window = int(limits.get("trend_filter_sma_days", 200))
    min_sleeves = int(limits.get("min_sleeves_in_trend_to_invest", 2))
    return sma_window, min_sleeves


def _flatten_to_cash(
    units: dict[str, float],
    cash: float,
    closes_today: dict[str, float],
    cost_rate: float,
) -> tuple[dict[str, float], float, float]:
    """Liquidate every sleeve to cash at today's close, charging simulated costs on the
    traded notional. Returns (zeroed units, new cash, cost charged). Pure."""
    notional = sum(units[s] * closes_today[s] for s in units)
    cost = notional * cost_rate
    cash_after = cash + notional - cost
    return {s: 0.0 for s in units}, cash_after, cost


def run_simulated_paper(repo_root: str = ".", *, write: bool = True) -> dict[str, Any]:
    """Run V2 in SIMULATED paper mode over the QA-passed staged CSVs and return a report.

    Refuses (verdict BLOCKED_NOT_READY, writes nothing) unless paper prep is READY. Reads
    only the three staged CSVs; when ``write=True`` writes ONLY simulated paper artifacts
    (jsonl log + json + md) under ``reports/crypto_d1_paper_prep/``. Places NO real order,
    connects to NO broker/exchange, uses NO network/credentials, and UNLOCKS no gate."""
    readiness = check_paper_prep_readiness(repo_root)
    config = build_paper_prep_config()

    blockers: list[str] = []
    if readiness.get("verdict") != VERDICT_READY:
        blockers.append("paper_prep_not_ready")
        blockers.extend("prep:" + b for b in readiness.get("blockers", []))
    if blockers:
        return _blocked_report(blockers, config)

    acct = config["paper_account"]
    limits = config["risk_limits"]
    kill = config["kill_switch"]
    cost_rate = float(acct.get("assumed_fee_rate", 0.0)) + float(acct.get("assumed_slippage_rate", 0.0))
    sma_window, min_sleeves = _v2_rule_params(config)
    hard_dd_kill = float(kill.get("drawdown_kill_threshold", -0.50))
    daily_loss_halt = float(kill.get("daily_loss_halt_threshold", -0.10))
    staleness_hours = float(kill.get("data_staleness_halt_hours", 48))

    input_dir = os.path.join(repo_root, QA_APPROVED_INPUT_DIR)
    series_by_symbol: dict[str, dict[str, float]] = {}
    files_read: list[str] = []
    for sym in QA_REQUIRED_SYMBOLS:
        path = os.path.join(input_dir, sym + "_1d.csv")
        series_by_symbol[sym] = _read_close_series(path)
        files_read.append(path)

    symbols = list(QA_REQUIRED_SYMBOLS)
    common = set.intersection(*(set(s.keys()) for s in series_by_symbol.values()))
    common_dates = sorted(common)
    if len(common_dates) < 2:
        return _blocked_report(["insufficient_common_history"], config)

    closes_aligned: dict[str, list[float]] = {
        s: [series_by_symbol[s][d] for d in common_dates] for s in symbols
    }

    cash = INITIAL_CAPITAL
    units = {s: 0.0 for s in symbols}
    peak = INITIAL_CAPITAL
    halted = False
    prev_value = INITIAL_CAPITAL
    trade_count = 0
    total_costs = 0.0
    kill_events: list[dict[str, Any]] = []
    values: list[float] = []
    log_records: list[dict[str, Any]] = []

    for i, date in enumerate(common_dates):
        closes_today = {s: series_by_symbol[s][date] for s in symbols}

        # Mark to market BEFORE any action today.
        value = cash + sum(units[s] * closes_today[s] for s in symbols)
        if value > peak:
            peak = value
        drawdown = value / peak - 1.0 if peak > 0 else 0.0
        daily_return = value / prev_value - 1.0 if prev_value > 0 else 0.0
        gap_hours = (
            (_iso_to_date(date) - _iso_to_date(common_dates[i - 1])).days * 24.0
            if i > 0 else 0.0
        )

        kill_today: str | None = None
        if not halted:
            if drawdown <= hard_dd_kill:
                kill_today = _KILL_HARD_DRAWDOWN
            elif daily_return <= daily_loss_halt:
                kill_today = _KILL_DAILY_LOSS
            elif i > 0 and gap_hours > staleness_hours:
                kill_today = _KILL_DATA_STALENESS

        if kill_today is not None:
            units, cash, cost = _flatten_to_cash(units, cash, closes_today, cost_rate)
            total_costs += cost
            if cost > 0:
                trade_count += 1
            halted = True
            value = cash
            kill_events.append({
                "date": date,
                "reason": kill_today,
                "drawdown": drawdown,
                "daily_return": daily_return,
                "equity_at_halt": value,
            })

        # Per-sleeve trend status (close > SMA200). Insufficient history => not in trend.
        in_trend: dict[str, bool] = {}
        for s in symbols:
            sma = _sma(closes_aligned[s][: i + 1], sma_window)
            in_trend[s] = sma is not None and closes_today[s] > sma
        n_in_trend = sum(1 for s in symbols if in_trend[s])

        target_weights: dict[str, float] = {}
        if not halted:
            active_syms = [s for s in symbols if in_trend[s]] if n_in_trend >= min_sleeves else []
            target_weights = _target_weights(
                active_syms,
                has_vol=False,
                vol_lookback=0,
                returns_to_today={},
                has_cap=False,
                cap_weight=1.0,
                gross_cap=float(limits.get("max_gross_exposure", 1.0)),
            )
            value = cash + sum(units[s] * closes_today[s] for s in symbols)
            new_units = {
                s: (value * target_weights.get(s, 0.0) / closes_today[s]) if closes_today[s] > 0 else 0.0
                for s in symbols
            }
            traded_notional = sum(abs(new_units[s] - units[s]) * closes_today[s] for s in symbols)
            cost = traded_notional * cost_rate
            if traded_notional > 1e-12:
                trade_count += 1
            total_costs += cost
            units = new_units
            cash = value - sum(units[s] * closes_today[s] for s in symbols) - cost

        value = cash + sum(units[s] * closes_today[s] for s in symbols)
        values.append(value)
        prev_value = value

        log_records.append({
            "date": date,
            "in_trend_by_symbol": dict(in_trend),
            "sleeves_in_trend": n_in_trend,
            "target_weights": {s: round(w, 6) for s, w in target_weights.items()},
            "simulated_positions": {s: round(units[s] * closes_today[s], 4) for s in symbols},
            "equity": round(value, 4),
            "cash": round(cash, 4),
            "drawdown": round(drawdown, 6),
            "daily_return": round(daily_return, 6),
            "kill_switch_state": "HALTED" if halted else "ACTIVE",
            "kill_reason": kill_today,
            "real_order_placed": False,
        })

    summary = _summarize_run(common_dates, values, trade_count, total_costs, kill_events, halted)
    report = _base_report(config)
    report.update({
        "verdict": VERDICT_PAPER_RUN_COMPLETE,
        "blockers": [],
        "selected_variant_id": SELECTED_VARIANT_ID,
        "paper_prep_verdict": readiness.get("verdict"),
        "symbols": symbols,
        "window": {
            "entry_date": common_dates[0],
            "exit_date": common_dates[-1],
            "trading_days": len(common_dates),
        },
        "performance": summary["performance"],
        "kill_switch_triggered": summary["kill_switch_triggered"],
        "kill_switch_events": kill_events,
        "halted_at_end": halted,
        "trade_summary": summary["trade_summary"],
        "files_read": files_read,
    })

    files_written: list[str] = []
    if write:
        out_dir = os.path.join(repo_root, PAPER_LOG_DIR)
        os.makedirs(out_dir, exist_ok=True)
        log_path = os.path.join(out_dir, "paper_run_log.jsonl")
        with open(log_path, "w", encoding="utf-8") as fh:
            for rec in log_records:
                fh.write(json.dumps(rec) + "\n")
        files_written.append(log_path)
        rep_json = os.path.join(out_dir, "paper_run_report.json")
        with open(rep_json, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2)
        files_written.append(rep_json)
        rep_md = os.path.join(out_dir, "paper_run_report.md")
        with open(rep_md, "w", encoding="utf-8") as fh:
            fh.write(render_paper_run_markdown(report))
        files_written.append(rep_md)

    report["files_written"] = files_written
    return report


def _summarize_run(
    common_dates: list[str],
    values: list[float],
    trade_count: int,
    total_costs: float,
    kill_events: list[dict[str, Any]],
    halted: bool,
) -> dict[str, Any]:
    """Compute simulated performance metrics and a trade/kill summary. Pure."""
    final_value = values[-1]
    daily_returns = [values[i] / values[i - 1] - 1.0 for i in range(1, len(values)) if values[i - 1] > 0]
    total_return = final_value / INITIAL_CAPITAL - 1.0
    max_dd = _max_drawdown(values)
    sd_daily = statistics.stdev(daily_returns) if len(daily_returns) >= 2 else 0.0
    mean_daily = statistics.fmean(daily_returns) if daily_returns else 0.0
    sharpe = (mean_daily / sd_daily) * math.sqrt(_TRADING_DAYS_PER_YEAR) if sd_daily > 0 else 0.0
    vol = sd_daily * math.sqrt(_TRADING_DAYS_PER_YEAR)
    performance = {
        "starting_equity": INITIAL_CAPITAL,
        "final_equity": final_value,
        "total_return": total_return,
        "max_drawdown": max_dd,
        "sharpe_ratio": sharpe,
        "annualized_volatility": vol,
        "trading_days": len(common_dates),
        "entry_date": common_dates[0],
        "exit_date": common_dates[-1],
    }
    trade_summary = {
        "simulated_trades": trade_count,
        "total_simulated_costs": total_costs,
        "real_orders_placed": 0,
    }
    return {
        "performance": performance,
        "trade_summary": trade_summary,
        "kill_switch_triggered": bool(kill_events),
    }


def _base_report(config: dict[str, Any]) -> dict[str, Any]:
    """Common report skeleton carrying the no-live-money safety posture. A simulated
    paper run changes NO gate: paper / micro-live / live all stay LOCKED."""
    return {
        "schema_version": PAPER_RUN_SCHEMA_VERSION,
        "label": PAPER_RUN_LABEL,
        "mode": PAPER_RUN_MODE,
        "authorization": _AUTHORIZATION,
        "config": config,
        # Capability posture (simulation only):
        "uses_real_money": False,
        "connects_broker": False,
        "connects_exchange": False,
        "executes_real_orders": False,
        "simulated_orders_only": True,
        "uses_network": False,
        "uses_credentials": False,
        "ran_optimization": False,
        "ran_parameter_search": False,
        "used_lookahead": False,
        "used_leverage": False,
        "used_shorting": False,
        "used_margin": False,
        "uses_only_qa_passed_inputs": True,
        "manual_csv_only": True,
        # Gate posture (UNCHANGED by this run):
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
        "live_gate_locked": True,
        "unlocks_downstream_gate": False,
        "authorizes_live_trading": False,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }


def _blocked_report(blockers: list[str], config: dict[str, Any]) -> dict[str, Any]:
    """A refusal report: paper prep was not READY, so no simulated run occurred and
    nothing was written."""
    report = _base_report(config)
    report.update({
        "verdict": VERDICT_BLOCKED_NOT_READY,
        "blockers": list(blockers),
        "selected_variant_id": SELECTED_VARIANT_ID,
        "symbols": list(QA_REQUIRED_SYMBOLS),
        "performance": {},
        "kill_switch_triggered": False,
        "kill_switch_events": [],
        "halted_at_end": False,
        "trade_summary": {"simulated_trades": 0, "total_simulated_costs": 0.0, "real_orders_placed": 0},
        "files_read": [],
        "files_written": [],
    })
    return report


def validate_paper_run_report(report: Any) -> dict[str, Any]:
    """Validate (read-only) a simulated paper-run report's shape and safety invariants.
    Returns {"valid": bool, "errors": [...]}; never raises."""
    errors: list[str] = []
    if not isinstance(report, dict):
        return {"valid": False, "errors": ["report_not_a_dict"]}
    r = report

    if r.get("verdict") not in (VERDICT_PAPER_RUN_COMPLETE, VERDICT_BLOCKED_NOT_READY):
        errors.append("bad_verdict")
    if r.get("schema_version") != PAPER_RUN_SCHEMA_VERSION:
        errors.append("bad_schema_version")
    if r.get("selected_variant_id") != SELECTED_VARIANT_ID:
        errors.append("bad_selected_variant")

    must_be_locked = ("paper_trading_gate_locked", "micro_live_gate_locked", "live_gate_locked")
    for key in must_be_locked:
        if r.get(key) is not True:
            errors.append("gate_not_locked:" + key)

    must_be_false = (
        "uses_real_money",
        "connects_broker",
        "connects_exchange",
        "executes_real_orders",
        "uses_network",
        "uses_credentials",
        "ran_optimization",
        "ran_parameter_search",
        "used_lookahead",
        "used_leverage",
        "used_shorting",
        "used_margin",
        "unlocks_downstream_gate",
        "authorizes_live_trading",
    )
    for key in must_be_false:
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)

    if r.get("simulated_orders_only") is not True:
        errors.append("simulated_orders_only_not_true")

    if r.get("verdict") == VERDICT_PAPER_RUN_COMPLETE:
        if r.get("trade_summary", {}).get("real_orders_placed") != 0:
            errors.append("real_orders_placed_nonzero")
        if not isinstance(r.get("performance"), dict) or not r.get("performance"):
            errors.append("performance_missing")

    return {"valid": not errors, "errors": errors}


def _pct(x: Any) -> str:
    try:
        return f"{float(x) * 100:.2f}%"
    except (TypeError, ValueError):
        return str(x)


def render_paper_run_markdown(report: Any) -> str:
    """Render a simulated paper-run report as deterministic markdown. Pure string work."""
    r = report if isinstance(report, dict) else {}
    perf = r.get("performance") or {}
    trades = r.get("trade_summary") or {}
    win = r.get("window") or {}
    lines: list[str] = []
    lines.append("# Crypto-D1 V2 SIMULATED Paper-Trading Run (NO LIVE MONEY)")
    lines.append("")
    lines.append("- Verdict: " + str(r.get("verdict", "")))
    lines.append("- Authorization: " + str(r.get("authorization", "")))
    lines.append("- Selected variant: " + str(r.get("selected_variant_id", "")))
    blockers = r.get("blockers") or []
    lines.append("- Blockers: " + ("none" if not blockers else ", ".join(blockers)))
    if win:
        lines.append("- Window: " + str(win.get("entry_date")) + " -> " + str(win.get("exit_date"))
                     + " (" + str(win.get("trading_days")) + " trading days)")
    lines.append("")
    lines.append("## Simulated performance (10000 USDT simulated, NO real money)")
    lines.append("- Starting equity: " + str(perf.get("starting_equity")))
    lines.append("- Final equity: " + str(perf.get("final_equity")))
    lines.append("- Total return: " + _pct(perf.get("total_return"))
                 + " | Max drawdown: " + _pct(perf.get("max_drawdown")))
    lines.append("- Sharpe: " + f"{float(perf.get('sharpe_ratio', 0) or 0):.2f}"
                 + " | Vol: " + _pct(perf.get("annualized_volatility")))
    lines.append("- Simulated trades: " + str(trades.get("simulated_trades"))
                 + " | Real orders placed: " + str(trades.get("real_orders_placed")))
    lines.append("")
    lines.append("## Kill switch")
    lines.append("- Triggered: " + str(r.get("kill_switch_triggered")))
    lines.append("- Halted at end: " + str(r.get("halted_at_end")))
    for ev in r.get("kill_switch_events") or []:
        lines.append("  - " + str(ev.get("date")) + ": " + str(ev.get("reason"))
                     + " (drawdown " + _pct(ev.get("drawdown"))
                     + ", daily " + _pct(ev.get("daily_return")) + ")")
    lines.append("")
    lines.append("## Gates (read-only metadata, UNCHANGED)")
    lines.append("- paper_trading_gate: LOCKED")
    lines.append("- micro_live_gate: LOCKED")
    lines.append("- live_gate: LOCKED")
    lines.append("- uses_real_money: False | executes_real_orders: False")
    lines.append("- Next required action: " + str(r.get("next_required_action", "")))
    return "\n".join(lines)


if __name__ == "__main__":  # pragma: no cover
    out = run_simulated_paper(repo_root=".", write=False)
    print(render_paper_run_markdown(out))
