"""Crypto-D1 V2 Resume-Policy SIMULATION Runner (READ-ONLY, NO LIVE MONEY).

The human-authorized companion to the V2 resume-policy research PLAN. It RUNS the six
PRE-REGISTERED, FIXED resume policies (RP1..RP6) for the single selected variant
``V2_trend_plus_cash_regime`` in SIMULATED paper mode over the already QA-passed local
staged spot CSVs (BTC/ETH/SOL), across the four FIXED regime sub-windows from the plan.

It exists to produce the multi-regime simulated evidence the paper-run review asked for,
WITHOUT optimization, parameter search, or any change of parameters based on results: the
policies and regimes are read verbatim from the resume-policy research plan and are never
fitted or tuned here.

Each (policy, regime) run is the V2 strategy with the prep contract's kill switch enforced
live, BUT instead of staying halted forever, the resume policy decides when (and at what
exposure) to come back. A re-halt can occur again afterwards; the cycle is honest.

It RUNS NOTHING real: every fill is a model fill at the QA-passed daily close charged the
prep contract's fee + slippage; NO real order is placed; long-only; no leverage / shorting
/ margin. It connects to NO broker / exchange, uses NO network / credentials, and UNLOCKS
no gate: paper_trading_gate, micro_live_gate and the live gate all stay LOCKED. Promoting
V2 to real money requires a SEPARATE explicit human command.

It refuses to run (verdict BLOCKED_NOT_READY, writes nothing) unless the paper-prep gate
is READY for exactly V2. It reads ONLY ``data/crypto_d1_spot/raw/{BTC,ETH,SOL}_1d.csv`` and
writes ONLY simulated reports under ``reports/crypto_d1_resume_policy_sim/``.

Public API:
  - RESUME_SIM_SCHEMA_VERSION / RESUME_SIM_LABEL / RESUME_SIM_MODE
  - RESUME_SIM_LOG_DIR / SELECTED_VARIANT_ID
  - VERDICT_RERUNS_COMPLETE / VERDICT_BLOCKED_NOT_READY
  - get_resume_sim_label()
  - run_resume_policy_simulations(repo_root=".", *, write=True)
  - validate_resume_policy_simulation_report(report)
  - render_resume_policy_simulation_markdown(report)
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
    SELECTED_VARIANT_ID,
    VERDICT_READY,
    build_paper_prep_config,
    check_paper_prep_readiness,
)
from sparta_commander.strategy_factory_crypto_d1_paper_trading_run_simulated import (
    _flatten_to_cash,
    _v2_rule_params,
    _KILL_DAILY_LOSS,
    _KILL_DATA_STALENESS,
    _KILL_HARD_DRAWDOWN,
)
from sparta_commander.strategy_factory_crypto_d1_resume_policy_research_plan import (
    resume_policy_candidates,
    regimes_to_cover,
)

RESUME_SIM_SCHEMA_VERSION = "strategy_factory_crypto_d1_resume_policy_simulation_runner.v1"
RESUME_SIM_LABEL = "Crypto-D1 V2 Resume-Policy SIMULATION Runner (READ-ONLY, NO LIVE MONEY)"
RESUME_SIM_MODE = "RESEARCH_ONLY"

RESUME_SIM_LOG_DIR = "reports/crypto_d1_resume_policy_sim"

VERDICT_RERUNS_COMPLETE = "RESUME_POLICY_RERUNS_COMPLETE"
VERDICT_BLOCKED_NOT_READY = "BLOCKED_NOT_READY"

_AUTHORIZATION = "APPROVE_RESUME_POLICY_SIMULATION_RERUN_READ_ONLY"

# After these reruns the only thing a human could authorize is a REVIEW of the resume-policy
# evidence -- still no live money, still a separate locked gate.
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_RESUME_POLICY_RESULTS_REVIEW"


def get_resume_sim_label() -> str:
    """Human label for the recognized Crypto-D1 V2 resume-policy simulation runner."""
    return RESUME_SIM_LABEL


def _basket_vol(closes_aligned: dict[str, list[float]], symbols: list[str], i: int,
                lookback: int) -> float | None:
    """Trailing realized volatility of an equal-weight basket of the sleeves, ending at
    index ``i`` over ``lookback`` days. A market-vol proxy independent of position. Pure;
    no lookahead (uses only data up to and including ``i``). Returns None if too short."""
    rets: list[float] = []
    start = max(1, i - lookback + 1)
    for j in range(start, i + 1):
        day = []
        for s in symbols:
            prev = closes_aligned[s][j - 1]
            cur = closes_aligned[s][j]
            if prev > 0:
                day.append(cur / prev - 1.0)
        if day:
            rets.append(sum(day) / len(day))
    if len(rets) < 2:
        return None
    return statistics.stdev(rets)


def _resume_condition(ptype: str, days_halted: int, min_days: int, breadth: int,
                      breadth_req: int, vol_today: float | None,
                      vol_ref: float | None) -> bool:
    """Evaluate a FIXED resume rule. Pure; reads only the day's already-computed market
    state (trend breadth, market vol) -- never fitted, never tuned."""
    if days_halted < min_days:
        return False
    if breadth < breadth_req:
        return False
    if ptype == "volatility_cooldown" and vol_ref is not None:
        return vol_today is not None and vol_today <= vol_ref
    return True


def _precompute_market(closes_aligned: dict[str, list[float]], symbols: list[str],
                       sma_window: int, vol_lookback: int) -> dict[str, Any]:
    """Precompute, ONCE, the policy/regime-independent market state per day: per-sleeve
    trend membership (close > SMA200), trend breadth, and basket realized vol. Pure."""
    n = len(closes_aligned[symbols[0]])
    in_trend: list[dict[str, bool]] = []
    breadth: list[int] = []
    vol: list[float | None] = []
    for i in range(n):
        flags: dict[str, bool] = {}
        for s in symbols:
            sma = _sma(closes_aligned[s][: i + 1], sma_window)
            flags[s] = sma is not None and closes_aligned[s][i] > sma
        in_trend.append(flags)
        breadth.append(sum(1 for s in symbols if flags[s]))
        vol.append(_basket_vol(closes_aligned, symbols, i, vol_lookback))
    return {"in_trend": in_trend, "breadth": breadth, "vol": vol}


def _summarize(values: list[float], active_dates: list[str], trade_count: int,
               total_costs: float, kill_events: list[dict[str, Any]],
               resume_events: list[dict[str, Any]], halted_at_end: bool) -> dict[str, Any]:
    """Compute simulated metrics for one (policy, regime) run. Pure."""
    final_value = values[-1]
    daily_returns = [values[i] / values[i - 1] - 1.0 for i in range(1, len(values)) if values[i - 1] > 0]
    total_return = final_value / INITIAL_CAPITAL - 1.0
    max_dd = _max_drawdown(values)
    sd = statistics.stdev(daily_returns) if len(daily_returns) >= 2 else 0.0
    mean = statistics.fmean(daily_returns) if daily_returns else 0.0
    sharpe = (mean / sd) * math.sqrt(_TRADING_DAYS_PER_YEAR) if sd > 0 else 0.0
    vol = sd * math.sqrt(_TRADING_DAYS_PER_YEAR)
    in_market_days = sum(1 for v in daily_returns if abs(v) > 0)
    return {
        "starting_equity": INITIAL_CAPITAL,
        "final_equity": final_value,
        "total_return": total_return,
        "max_drawdown": max_dd,
        "sharpe_ratio": sharpe,
        "annualized_volatility": vol,
        "trading_days": len(active_dates),
        "entry_date": active_dates[0],
        "exit_date": active_dates[-1],
        "simulated_trades": trade_count,
        "total_simulated_costs": total_costs,
        "real_orders_placed": 0,
        "num_kill_events": len(kill_events),
        "num_resume_events": len(resume_events),
        "halted_at_end": halted_at_end,
        "kill_events": kill_events,
        "resume_events": resume_events,
        "post_resume_max_drawdown": _post_resume_drawdown(values, active_dates, resume_events),
    }


def _post_resume_drawdown(values: list[float], active_dates: list[str],
                          resume_events: list[dict[str, Any]]) -> float:
    """Worst drawdown over the equity path AFTER the first resume (0.0 if never resumed)."""
    if not resume_events:
        return 0.0
    first = resume_events[0]["date"]
    try:
        idx = active_dates.index(first)
    except ValueError:
        return 0.0
    tail = values[idx:]
    return _max_drawdown(tail) if len(tail) >= 2 else 0.0


def _simulate_regime(common_dates: list[str], series_by_symbol: dict[str, dict[str, float]],
                     closes_aligned: dict[str, list[float]], symbols: list[str],
                     market: dict[str, Any], config: dict[str, Any],
                     policy: dict[str, Any], window: str) -> dict[str, Any] | None:
    """Run V2 with one FIXED resume policy over one regime sub-window. SMA/vol are warmed
    up on real history BEFORE the window; equity starts fresh at the window entry. Pure
    (reads precomputed series + prices only); writes nothing; places no real order."""
    start_s, end_s = window.split("..")
    start_d, end_d = _iso_to_date(start_s), _iso_to_date(end_s)

    acct = config["paper_account"]
    limits = config["risk_limits"]
    kill = config["kill_switch"]
    cost_rate = float(acct.get("assumed_fee_rate", 0.0)) + float(acct.get("assumed_slippage_rate", 0.0))
    _sma_window, min_sleeves = _v2_rule_params(config)
    hard_dd_kill = float(kill.get("drawdown_kill_threshold", -0.50))
    daily_loss_halt = float(kill.get("daily_loss_halt_threshold", -0.10))
    staleness_hours = float(kill.get("data_staleness_halt_hours", 48))
    gross_cap_base = float(limits.get("max_gross_exposure", 1.0))

    trig = policy.get("resume_trigger") or {}
    ptype = str(trig.get("type", "breadth_only"))
    min_days = int(trig.get("min_days_halted", 0))
    breadth_req = int(trig.get("breadth_required", min_sleeves))
    confirmation_days = int(trig.get("confirmation_days", 0))
    stages = list(policy.get("exposure_stages") or [1.0])

    cash = INITIAL_CAPITAL
    units = {s: 0.0 for s in symbols}
    peak = INITIAL_CAPITAL
    prev_value = INITIAL_CAPITAL
    prev_active_date = start_d
    started = False
    halted = False
    days_halted = 0
    exposure_scale = 1.0
    confirm_count = 0
    vol_ref: float | None = None
    vol_observed: list[float] = []

    values: list[float] = []
    active_dates: list[str] = []
    kill_events: list[dict[str, Any]] = []
    resume_events: list[dict[str, Any]] = []
    trade_count = 0
    total_costs = 0.0

    for i, date in enumerate(common_dates):
        d = _iso_to_date(date)
        if d < start_d:
            continue
        if d > end_d:
            break

        closes_today = {s: series_by_symbol[s][date] for s in symbols}
        in_trend = market["in_trend"][i]
        n_in_trend = market["breadth"][i]
        vol_today = market["vol"][i]

        if not started:
            started = True
            cash = INITIAL_CAPITAL
            units = {s: 0.0 for s in symbols}
            peak = INITIAL_CAPITAL
            prev_value = INITIAL_CAPITAL
            prev_active_date = d

        active_dates.append(date)
        value = cash + sum(units[s] * closes_today[s] for s in symbols)
        if value > peak:
            peak = value
        drawdown = value / peak - 1.0 if peak > 0 else 0.0
        daily_return = value / prev_value - 1.0 if prev_value > 0 else 0.0
        gap_hours = (d - prev_active_date).days * 24.0 if len(active_dates) > 1 else 0.0

        # Kill switch (only while running).
        kill_today: str | None = None
        if not halted:
            if drawdown <= hard_dd_kill:
                kill_today = _KILL_HARD_DRAWDOWN
            elif daily_return <= daily_loss_halt:
                kill_today = _KILL_DAILY_LOSS
            elif len(active_dates) > 1 and gap_hours > staleness_hours:
                kill_today = _KILL_DATA_STALENESS
        if kill_today is not None:
            units, cash, cost = _flatten_to_cash(units, cash, closes_today, cost_rate)
            total_costs += cost
            if cost > 0:
                trade_count += 1
            halted = True
            days_halted = 0
            confirm_count = 0
            exposure_scale = 1.0
            value = cash
            kill_events.append({"date": date, "reason": kill_today, "drawdown": drawdown,
                                "daily_return": daily_return, "equity_at_halt": value})
            if ptype == "volatility_cooldown":
                pool = [v for v in vol_observed if v is not None]
                vol_ref = statistics.median(pool) if pool else None

        # Resume policy (only while halted).
        if halted:
            days_halted += 1
            if _resume_condition(ptype, days_halted, min_days, n_in_trend, breadth_req,
                                 vol_today, vol_ref):
                halted = False
                resume_events.append({"date": date, "days_halted": days_halted,
                                      "breadth": n_in_trend})
                exposure_scale = stages[0] if ptype == "staged_exposure" else 1.0
                confirm_count = 0

        # Staged exposure ramp (HALF -> FULL after confirming days).
        if (not halted) and ptype == "staged_exposure" and exposure_scale < stages[-1]:
            if n_in_trend >= breadth_req:
                confirm_count += 1
                if confirm_count >= confirmation_days:
                    exposure_scale = stages[-1]
            else:
                confirm_count = 0

        # Trade to target (only while running).
        target_weights: dict[str, float] = {}
        if not halted:
            active_syms = [s for s in symbols if in_trend[s]] if n_in_trend >= min_sleeves else []
            target_weights = _target_weights(
                active_syms, has_vol=False, vol_lookback=0, returns_to_today={},
                has_cap=False, cap_weight=1.0, gross_cap=gross_cap_base * exposure_scale,
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
        prev_active_date = d
        vol_observed.append(vol_today if vol_today is not None else 0.0)

    if len(values) < 2:
        return None
    return _summarize(values, active_dates, trade_count, total_costs, kill_events,
                      resume_events, halted)


def _aggregate_policy(regime_results: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate one policy's per-regime metrics. Reporting only -- never feeds back into
    parameters. Pure."""
    rets = [r["metrics"]["total_return"] for r in regime_results if r.get("metrics")]
    dds = [r["metrics"]["max_drawdown"] for r in regime_results if r.get("metrics")]
    shp = [r["metrics"]["sharpe_ratio"] for r in regime_results if r.get("metrics")]
    return {
        "regimes_evaluated": len(rets),
        "mean_total_return": statistics.fmean(rets) if rets else 0.0,
        "min_total_return": min(rets) if rets else 0.0,
        "worst_max_drawdown": min(dds) if dds else 0.0,
        "mean_sharpe_ratio": statistics.fmean(shp) if shp else 0.0,
    }


def run_resume_policy_simulations(repo_root: str = ".", *, write: bool = True) -> dict[str, Any]:
    """Run all six FIXED resume policies over all four FIXED regimes in SIMULATED mode.

    Refuses (verdict BLOCKED_NOT_READY, writes nothing) unless paper prep is READY. Reads
    only the three staged CSVs; when ``write=True`` writes ONLY simulated reports under
    ``reports/crypto_d1_resume_policy_sim/``. Runs NO optimization / parameter search,
    places NO real order, connects to NO broker/exchange, uses NO network/credentials, and
    UNLOCKS no gate."""
    readiness = check_paper_prep_readiness(repo_root)
    config = build_paper_prep_config()

    blockers: list[str] = []
    if readiness.get("verdict") != VERDICT_READY:
        blockers.append("paper_prep_not_ready")
        blockers.extend("prep:" + b for b in readiness.get("blockers", []))
    if blockers:
        return _blocked_report(blockers, config)

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

    closes_aligned = {s: [series_by_symbol[s][d] for d in common_dates] for s in symbols}
    sma_window, _min_sleeves = _v2_rule_params(config)
    vol_lookback = 30
    market = _precompute_market(closes_aligned, symbols, sma_window, vol_lookback)

    policies = resume_policy_candidates()
    regimes = regimes_to_cover()

    policy_results: list[dict[str, Any]] = []
    log_records: list[dict[str, Any]] = []
    for policy in policies:
        regime_results: list[dict[str, Any]] = []
        for regime in regimes:
            metrics = _simulate_regime(common_dates, series_by_symbol, closes_aligned,
                                       symbols, market, config, policy, regime["window"])
            entry = {"regime_id": regime["regime_id"], "window": regime["window"],
                     "metrics": metrics, "evaluated": metrics is not None}
            regime_results.append(entry)
            log_records.append({
                "policy_id": policy["policy_id"],
                "regime_id": regime["regime_id"],
                "window": regime["window"],
                "evaluated": metrics is not None,
                "total_return": (metrics or {}).get("total_return"),
                "max_drawdown": (metrics or {}).get("max_drawdown"),
                "sharpe_ratio": (metrics or {}).get("sharpe_ratio"),
                "num_kill_events": (metrics or {}).get("num_kill_events"),
                "num_resume_events": (metrics or {}).get("num_resume_events"),
                "halted_at_end": (metrics or {}).get("halted_at_end"),
                "real_orders_placed": 0,
            })
        policy_results.append({
            "policy_id": policy["policy_id"],
            "description": policy.get("description"),
            "reentry_exposure": policy.get("reentry_exposure"),
            "regime_results": regime_results,
            "aggregate": _aggregate_policy(regime_results),
        })

    rankings = _rank_policies(policy_results)

    report = _base_report(config)
    report.update({
        "verdict": VERDICT_RERUNS_COMPLETE,
        "blockers": [],
        "selected_variant_id": SELECTED_VARIANT_ID,
        "paper_prep_verdict": readiness.get("verdict"),
        "symbols": symbols,
        "data_window": {"entry_date": common_dates[0], "exit_date": common_dates[-1],
                        "trading_days": len(common_dates)},
        "regimes": [{"regime_id": r["regime_id"], "window": r["window"]} for r in regimes],
        "policy_results": policy_results,
        "rankings": rankings,
        "files_read": files_read,
    })

    files_written: list[str] = []
    if write:
        out_dir = os.path.join(repo_root, RESUME_SIM_LOG_DIR)
        os.makedirs(out_dir, exist_ok=True)
        log_path = os.path.join(out_dir, "resume_policy_sim_log.jsonl")
        with open(log_path, "w", encoding="utf-8") as fh:
            for rec in log_records:
                fh.write(json.dumps(rec) + "\n")
        files_written.append(log_path)
        rep_json = os.path.join(out_dir, "resume_policy_sim_report.json")
        with open(rep_json, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2)
        files_written.append(rep_json)
        rep_md = os.path.join(out_dir, "resume_policy_sim_report.md")
        with open(rep_md, "w", encoding="utf-8") as fh:
            fh.write(render_resume_policy_simulation_markdown(report))
        files_written.append(rep_md)

    report["files_written"] = files_written
    return report


def _rank_policies(policy_results: list[dict[str, Any]]) -> dict[str, Any]:
    """Identify the best policy by mean return, by worst-case drawdown (least bad), and by
    mean Sharpe. Pure reporting -- NO parameter is changed based on this."""
    if not policy_results:
        return {}
    by_return = max(policy_results, key=lambda p: p["aggregate"]["mean_total_return"])
    by_drawdown = max(policy_results, key=lambda p: p["aggregate"]["worst_max_drawdown"])
    by_sharpe = max(policy_results, key=lambda p: p["aggregate"]["mean_sharpe_ratio"])
    return {
        "best_by_mean_return": by_return["policy_id"],
        "best_by_worst_drawdown": by_drawdown["policy_id"],
        "best_by_mean_sharpe": by_sharpe["policy_id"],
    }


def _base_report(config: dict[str, Any]) -> dict[str, Any]:
    """Common report skeleton carrying the read-only / no-live-money safety posture. This
    run changes NO gate and tunes NO parameter."""
    return {
        "schema_version": RESUME_SIM_SCHEMA_VERSION,
        "label": RESUME_SIM_LABEL,
        "mode": RESUME_SIM_MODE,
        "authorization": _AUTHORIZATION,
        "config": config,
        # Capability posture (simulation only, fixed policies):
        "uses_real_money": False,
        "connects_broker": False,
        "connects_exchange": False,
        "executes_real_orders": False,
        "simulated_orders_only": True,
        "uses_network": False,
        "uses_credentials": False,
        "ran_optimization": False,
        "ran_parameter_search": False,
        "parameters_changed_based_on_results": False,
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
    """A refusal report: paper prep was not READY, so no simulated reruns occurred and
    nothing was written."""
    report = _base_report(config)
    report.update({
        "verdict": VERDICT_BLOCKED_NOT_READY,
        "blockers": list(blockers),
        "selected_variant_id": SELECTED_VARIANT_ID,
        "symbols": list(QA_REQUIRED_SYMBOLS),
        "regimes": [],
        "policy_results": [],
        "rankings": {},
        "files_read": [],
        "files_written": [],
    })
    return report


def validate_resume_policy_simulation_report(report: Any) -> dict[str, Any]:
    """Validate (read-only) a resume-policy simulation report's shape and safety
    invariants. Returns {"valid": bool, "errors": [...]}; never raises."""
    errors: list[str] = []
    if not isinstance(report, dict):
        return {"valid": False, "errors": ["report_not_a_dict"]}
    r = report

    if r.get("verdict") not in (VERDICT_RERUNS_COMPLETE, VERDICT_BLOCKED_NOT_READY):
        errors.append("bad_verdict")
    if r.get("schema_version") != RESUME_SIM_SCHEMA_VERSION:
        errors.append("bad_schema_version")
    if r.get("selected_variant_id") != SELECTED_VARIANT_ID:
        errors.append("bad_selected_variant")

    must_be_locked = ("paper_trading_gate_locked", "micro_live_gate_locked", "live_gate_locked")
    for key in must_be_locked:
        if r.get(key) is not True:
            errors.append("gate_not_locked:" + key)

    must_be_false = (
        "uses_real_money", "connects_broker", "connects_exchange", "executes_real_orders",
        "uses_network", "uses_credentials", "ran_optimization", "ran_parameter_search",
        "parameters_changed_based_on_results", "used_lookahead", "used_leverage",
        "used_shorting", "used_margin", "unlocks_downstream_gate", "authorizes_live_trading",
    )
    for key in must_be_false:
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)

    if r.get("simulated_orders_only") is not True:
        errors.append("simulated_orders_only_not_true")

    if r.get("verdict") == VERDICT_RERUNS_COMPLETE:
        results = r.get("policy_results")
        if not isinstance(results, list) or not results:
            errors.append("no_policy_results")
            results = []
        for p in results:
            for rr in p.get("regime_results", []):
                m = rr.get("metrics")
                if m and m.get("real_orders_placed") != 0:
                    errors.append("real_orders_placed_nonzero:" + str(p.get("policy_id")))

    return {"valid": not errors, "errors": errors}


def _pct(x: Any) -> str:
    try:
        return f"{float(x) * 100:.2f}%"
    except (TypeError, ValueError):
        return str(x)


def render_resume_policy_simulation_markdown(report: Any) -> str:
    """Render a resume-policy simulation report as deterministic markdown. Pure."""
    r = report if isinstance(report, dict) else {}
    lines: list[str] = []
    lines.append("# Crypto-D1 V2 Resume-Policy SIMULATION (READ-ONLY, NO LIVE MONEY)")
    lines.append("")
    lines.append("- Verdict: " + str(r.get("verdict", "")))
    lines.append("- Authorization: " + str(r.get("authorization", "")))
    lines.append("- Selected variant: " + str(r.get("selected_variant_id", "")))
    blockers = r.get("blockers") or []
    lines.append("- Blockers: " + ("none" if not blockers else ", ".join(blockers)))
    rk = r.get("rankings") or {}
    if rk:
        lines.append("- Best by mean return: " + str(rk.get("best_by_mean_return")))
        lines.append("- Best by worst drawdown: " + str(rk.get("best_by_worst_drawdown")))
        lines.append("- Best by mean Sharpe: " + str(rk.get("best_by_mean_sharpe")))
    lines.append("")
    for p in r.get("policy_results") or []:
        agg = p.get("aggregate") or {}
        lines.append("## " + str(p.get("policy_id")) + " (" + str(p.get("reentry_exposure")) + ")")
        lines.append("- " + str(p.get("description")))
        lines.append("- Mean return: " + _pct(agg.get("mean_total_return"))
                     + " | Worst drawdown: " + _pct(agg.get("worst_max_drawdown"))
                     + " | Mean Sharpe: " + f"{float(agg.get('mean_sharpe_ratio', 0) or 0):.2f}")
        for rr in p.get("regime_results") or []:
            m = rr.get("metrics") or {}
            lines.append("  - " + str(rr.get("regime_id")) + ": return " + _pct(m.get("total_return"))
                         + ", maxDD " + _pct(m.get("max_drawdown"))
                         + ", Sharpe " + f"{float(m.get('sharpe_ratio', 0) or 0):.2f}"
                         + ", kills " + str(m.get("num_kill_events"))
                         + ", resumes " + str(m.get("num_resume_events")))
    lines.append("")
    lines.append("## Gates (read-only metadata, UNCHANGED)")
    lines.append("- paper_trading_gate: LOCKED")
    lines.append("- micro_live_gate: LOCKED")
    lines.append("- live_gate: LOCKED")
    lines.append("- uses_real_money: False | executes_real_orders: False | ran_optimization: False")
    lines.append("- Next required action: " + str(r.get("next_required_action", "")))
    return "\n".join(lines)


if __name__ == "__main__":  # pragma: no cover
    out = run_resume_policy_simulations(repo_root=".", write=False)
    print(render_resume_policy_simulation_markdown(out))
