"""Crypto-D1 Risk-Controlled Variant Backtest Runner (READ-ONLY, HUMAN-AUTHORIZED).

The human-authorized companion to the variant PREP-ONLY contract. It RUNS the five
pre-registered, risk-controlled, long-only variants over the already QA-passed local
staged spot CSVs and writes ONLY variant report artifacts under
``reports/crypto_d1_variant_backtest/``:

  V1 trend_filter
  V2 trend_plus_cash_regime
  V3 voltarget_concentration_cap
  V4 monthly_rebalance_capped
  V5 full_risk_managed

Each variant uses EXACTLY the single pre-registered parameterization pinned by the
prep contract (CONTROL_PARAMETERS) -- there is NO optimization, NO parameter search,
NO walk-forward, NO lookahead (every signal uses only data up to and including the
current day, and trades at that day's close). The portfolio is long-only; sleeves
that fail a control move to cash; leverage / shorting / margin are never used.

It refuses to run unless ``check_variant_prep_readiness`` returns READY (the staged
QA-passed inputs are intact and every variant manifest is fully specified). It reads
ONLY the three staged files data/crypto_d1_spot/raw/{BTC,ETH,SOL}_1d.csv.

It UNLOCKS no gate: running these approved variants leaves paper_trading_gate and
micro_live_gate LOCKED. Per-variant paper-prep ELIGIBILITY is REPORTED (reusing the
baseline review's fixed promotion criteria) but is only a recommendation; a SEPARATE
explicit human command is required before anything is promoted.

Public API:
  - RUNNER_SCHEMA_VERSION / RUNNER_LABEL / RUNNER_MODE
  - VARIANT_REPORT_DIR / INITIAL_CAPITAL
  - VERDICT_VARIANTS_COMPLETE / VERDICT_BLOCKED_NOT_READY
  - get_variant_backtest_runner_label()
  - run_variant_backtests(repo_root=".", *, write=True)
  - validate_variant_backtest_report(report)
  - render_variant_backtest_markdown(report)
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
    VERDICT_BASELINE_COMPLETE,
    _TRADING_DAYS_PER_YEAR,
    _iso_to_date,
    _max_drawdown,
    _read_close_series,
)
from sparta_commander.strategy_factory_crypto_d1_variant_backtest_prep_contract import (
    VERDICT_READY,
    build_variant_manifests,
    check_variant_prep_readiness,
)
from sparta_commander.strategy_factory_crypto_d1_baseline_backtest_review_contract import (
    DO_NOT_PROMOTE_TO_PAPER_YET,
    PROMOTE_TO_PAPER_PREP,
    promotion_criteria,
    review_baseline_report,
)

RUNNER_SCHEMA_VERSION = "strategy_factory_crypto_d1_variant_backtest_runner.v1"
RUNNER_LABEL = "Crypto-D1 Risk-Controlled Variant Backtest Runner (5 pre-registered long-only variants)"
RUNNER_MODE = "RESEARCH_ONLY"

VARIANT_REPORT_DIR = "reports/crypto_d1_variant_backtest"

VERDICT_VARIANTS_COMPLETE = "VARIANTS_COMPLETE"
VERDICT_BLOCKED_NOT_READY = "BLOCKED_NOT_READY"

_AUTHORIZATION = "APPROVE_RISK_CONTROLLED_VARIANT_BACKTEST_RUN_READ_ONLY"
_DEFAULT_REENTRY_BREADTH = 2  # used by stop_risk_off re-entry when no cash_regime breadth


def get_variant_backtest_runner_label() -> str:
    """Human label for the recognized Crypto-D1 variant backtest runner."""
    return RUNNER_LABEL


# --------------------------------------------------------------------------- #
# sizing / masking helpers (pure)
# --------------------------------------------------------------------------- #
def _sma(closes: list[float], window: int) -> float | None:
    """Simple moving average of the last ``window`` closes, or None if there is not
    yet enough history (no lookahead: caller passes closes up to and including today)."""
    if window <= 0 or len(closes) < window:
        return None
    return sum(closes[-window:]) / float(window)


def _trailing_vol(returns: list[float], lookback: int) -> float | None:
    """Sample stdev of the last ``lookback`` daily returns, or None if < 2 available."""
    window = returns[-lookback:] if lookback > 0 else returns
    if len(window) < 2:
        return None
    return statistics.stdev(window)


def _apply_concentration_cap(weights: dict[str, float], cap: float) -> dict[str, float]:
    """Water-fill cap: clip each weight at ``cap`` and redistribute the excess across
    uncapped sleeves proportionally. If every sleeve is capped, the residual simply
    stays in cash (the returned weights then sum to < 1). Pure."""
    w = dict(weights)
    for _ in range(16):
        over = {s: v for s, v in w.items() if v > cap + 1e-15}
        if not over:
            break
        excess = sum(v - cap for v in over.values())
        for s in over:
            w[s] = cap
        under = {s: v for s, v in w.items() if v < cap - 1e-15}
        total_under = sum(under.values())
        if total_under <= 0:
            break
        for s in under:
            w[s] += excess * (under[s] / total_under)
    return {s: min(v, cap) for s, v in w.items()}


def _target_weights(
    active: list[str],
    *,
    has_vol: bool,
    vol_lookback: int,
    returns_to_today: dict[str, list[float]],
    has_cap: bool,
    cap_weight: float,
    gross_cap: float,
) -> dict[str, float]:
    """Resolve the day's target weights over the ACTIVE sleeves from the pinned sizing
    controls: inverse-vol (volatility_cap) or equal weight, then concentration cap,
    then scale gross exposure to the fixed ceiling. Pure; no lookahead."""
    if not active:
        return {}
    raw: dict[str, float] = {}
    use_equal = not has_vol
    if has_vol:
        for s in active:
            v = _trailing_vol(returns_to_today.get(s, []), vol_lookback)
            if v is None or v <= 0:
                use_equal = True  # not enough history to size by vol -> equal weight
                break
            raw[s] = 1.0 / v
    if use_equal:
        raw = {s: 1.0 for s in active}
    total = sum(raw.values())
    weights = {s: raw[s] / total for s in active} if total > 0 else {}
    if has_cap:
        weights = _apply_concentration_cap(weights, cap_weight)
    gross = sum(weights.values())
    if gross > gross_cap and gross > 0:
        weights = {s: v * (gross_cap / gross) for s, v in weights.items()}
    return weights


def _simulate_variant(
    manifest: dict[str, Any],
    series_by_symbol: dict[str, dict[str, float]],
    common_dates: list[str],
) -> dict[str, Any]:
    """Run a single pre-registered variant as a long-only, cash-when-out, daily
    target-weight portfolio. Risk-off controls (trend / cash-regime / stop) move
    affected sleeves to cash the day their signal triggers; sizing controls
    (equal / inverse-vol) and the concentration cap set target weights; the
    periodic_rebalance control restricts STRUCTURAL re-weighting to a monthly cadence
    while risk-off exits always act immediately. No lookahead; no leverage."""
    symbols = list(QA_REQUIRED_SYMBOLS)
    controls = set(manifest.get("controls") or [])
    params = manifest.get("fixed_parameters") or {}

    has_trend = "trend_filter" in controls
    has_cash = "cash_regime" in controls
    has_vol = "volatility_cap" in controls
    has_stop = "stop_risk_off" in controls
    has_reb = "periodic_rebalance" in controls
    has_cap = "sol_concentration_cap" in controls

    sma_window = int(params.get("trend_filter", {}).get("sma_window_days", 0)) if has_trend else 0
    min_sleeves = int(params.get("cash_regime", {}).get("min_sleeves_in_trend", 0)) if has_cash else 0
    vol_lookback = int(params.get("volatility_cap", {}).get("vol_lookback_days", 0)) if has_vol else 0
    gross_cap = float(params.get("volatility_cap", {}).get("gross_exposure_cap", 1.0)) if has_vol else 1.0
    dd_stop = float(params.get("stop_risk_off", {}).get("drawdown_stop", 0.0)) if has_stop else 0.0
    cap_weight = float(params.get("sol_concentration_cap", {}).get("max_weight_per_asset", 1.0)) if has_cap else 1.0

    # Aligned per-symbol close + daily-return series over the common trading calendar.
    closes_aligned: dict[str, list[float]] = {s: [series_by_symbol[s][d] for d in common_dates] for s in symbols}
    returns_aligned: dict[str, list[float]] = {}
    for s in symbols:
        cs = closes_aligned[s]
        returns_aligned[s] = [cs[i] / cs[i - 1] - 1.0 for i in range(1, len(cs))]

    cash = INITIAL_CAPITAL
    units = {s: 0.0 for s in symbols}
    stopped = False
    peak = INITIAL_CAPITAL
    prev_active: set[str] | None = None
    prev_month: str | None = None
    rebalance_count = 0
    trade_count = 0

    values: list[float] = []
    equity_curve: list[dict[str, Any]] = []

    for i, date in enumerate(common_dates):
        closes_today = {s: series_by_symbol[s][date] for s in symbols}
        value = cash + sum(units[s] * closes_today[s] for s in symbols)
        if value > peak:
            peak = value
        drawdown = value / peak - 1.0 if peak > 0 else 0.0

        # Per-sleeve trend status (close > SMA). Without a trend filter every sleeve
        # counts as "in trend". Insufficient history => not in trend (stays in cash).
        in_trend: dict[str, bool] = {}
        for s in symbols:
            if has_trend:
                sma = _sma(closes_aligned[s][: i + 1], sma_window)
                in_trend[s] = sma is not None and closes_today[s] > sma
            else:
                in_trend[s] = True
        n_in_trend = sum(1 for s in symbols if in_trend[s])

        # Drawdown stop / risk-off: trip to cash when drawdown breaches the floor; only
        # re-enter once breadth (trend re-confirmation) recovers.
        if has_stop:
            if not stopped and drawdown <= dd_stop:
                stopped = True
            elif stopped:
                reentry_breadth = min_sleeves if has_cash else _DEFAULT_REENTRY_BREADTH
                if n_in_trend >= reentry_breadth:
                    stopped = False

        active = {s: in_trend[s] for s in symbols}
        if has_cash and n_in_trend < min_sleeves:
            active = {s: False for s in symbols}
        if has_stop and stopped:
            active = {s: False for s in symbols}
        active_syms = [s for s in symbols if active[s]]

        # Structural re-weighting cadence: daily unless a periodic_rebalance cadence is
        # pinned (then monthly). Risk-off mask changes always force an immediate trade.
        cadence_day = (prev_month != date[:7]) if has_reb else True
        mask_changed = prev_active is None or set(active_syms) != prev_active
        do_rebalance = cadence_day or mask_changed

        if do_rebalance:
            returns_to_today = {s: returns_aligned[s][:i] for s in symbols}
            weights = _target_weights(
                active_syms,
                has_vol=has_vol,
                vol_lookback=vol_lookback,
                returns_to_today=returns_to_today,
                has_cap=has_cap,
                cap_weight=cap_weight,
                gross_cap=gross_cap,
            )
            value = cash + sum(units[s] * closes_today[s] for s in symbols)
            new_units = {
                s: (value * weights.get(s, 0.0) / closes_today[s]) if closes_today[s] > 0 else 0.0
                for s in symbols
            }
            trade_count += sum(1 for s in symbols if abs(new_units[s] - units[s]) > 1e-12)
            units = new_units
            cash = value - sum(units[s] * closes_today[s] for s in symbols)
            rebalance_count += 1

        prev_active = set(active_syms)
        prev_month = date[:7]

        value = cash + sum(units[s] * closes_today[s] for s in symbols)
        values.append(value)
        equity_curve.append({"date": date, "value": value})

    return _summarize_variant(manifest, symbols, common_dates, closes_aligned, units,
                              cash, values, equity_curve, rebalance_count, trade_count)


def _summarize_variant(
    manifest: dict[str, Any],
    symbols: list[str],
    common_dates: list[str],
    closes_aligned: dict[str, list[float]],
    units: dict[str, float],
    cash: float,
    values: list[float],
    equity_curve: list[dict[str, Any]],
    rebalance_count: int,
    trade_count: int,
) -> dict[str, Any]:
    """Compute performance metrics, per-symbol breakdown, and a paper-prep eligibility
    verdict (reusing the baseline review's fixed promotion criteria) for one variant."""
    entry_date, exit_date = common_dates[0], common_dates[-1]
    final_value = values[-1]
    daily_returns = [values[i] / values[i - 1] - 1.0 for i in range(1, len(values))]
    total_return = final_value / INITIAL_CAPITAL - 1.0
    calendar_days = max(1, (_iso_to_date(exit_date) - _iso_to_date(entry_date)).days)
    years = calendar_days / 365.25
    cagr = (final_value / INITIAL_CAPITAL) ** (1.0 / years) - 1.0 if years > 0 and final_value > 0 else 0.0
    max_dd = _max_drawdown(values)
    sd_daily = statistics.stdev(daily_returns) if len(daily_returns) >= 2 else 0.0
    vol = sd_daily * math.sqrt(_TRADING_DAYS_PER_YEAR)
    mean_daily = statistics.fmean(daily_returns) if daily_returns else 0.0
    sharpe = (mean_daily / sd_daily) * math.sqrt(_TRADING_DAYS_PER_YEAR) if sd_daily > 0 else 0.0

    per_symbol: list[dict[str, Any]] = []
    for s in symbols:
        exit_close = closes_aligned[s][-1]
        held_value = units[s] * exit_close
        per_symbol.append(
            {
                "symbol": s,
                "entry_close": closes_aligned[s][0],
                "exit_close": exit_close,
                "final_units": units[s],
                "final_value": held_value,
                "contribution_to_portfolio": held_value / INITIAL_CAPITAL,
                "market_return": exit_close / closes_aligned[s][0] - 1.0,
            }
        )

    performance = {
        "initial_capital": INITIAL_CAPITAL,
        "final_value": final_value,
        "final_cash": cash,
        "total_return": total_return,
        "cagr": cagr,
        "max_drawdown": max_dd,
        "annualized_volatility": vol,
        "sharpe_ratio": sharpe,
        "trading_days": len(common_dates),
        "calendar_days": calendar_days,
        "entry_date": entry_date,
        "exit_date": exit_date,
    }
    trade_summary = {
        "trade_count": trade_count,
        "rebalances": rebalance_count,
        # informational: managed variants DO trade in/out of cash (not buy & hold)
        "sells": max(0, trade_count - len(symbols)),
    }

    # Reuse the baseline review's promotion logic as the single source of truth for
    # eligibility (drawdown floor, Sharpe, return, coverage, completeness).
    pseudo_report = {
        "verdict": VERDICT_BASELINE_COMPLETE,
        "performance": performance,
        "trade_summary": trade_summary,
        "per_symbol": per_symbol,
    }
    review = review_baseline_report(pseudo_report)
    crit = promotion_criteria()
    beats_drawdown_floor = max_dd >= crit["max_acceptable_drawdown"]

    return {
        "variant_id": manifest.get("variant_id"),
        "description": manifest.get("description"),
        "controls": list(manifest.get("controls") or []),
        "fixed_parameters": manifest.get("fixed_parameters"),
        "hypothesis": manifest.get("hypothesis"),
        "performance": performance,
        "trade_summary": trade_summary,
        "per_symbol": per_symbol,
        "equity_curve": equity_curve,
        "beats_drawdown_floor": beats_drawdown_floor,
        "promotion_decision": review["promotion_decision"],
        "eligible_for_paper_prep": review["eligible_for_paper_prep"],
        "eligibility_blockers": review["blockers"],
    }


def run_variant_backtests(repo_root: str = ".", *, write: bool = True) -> dict[str, Any]:
    """Run the five pre-registered risk-controlled variants over the QA-passed staged
    CSVs and return a combined report. Refuses (verdict BLOCKED_NOT_READY, writes
    nothing) unless variant prep is READY and its constraints forbid optimization /
    search / walk-forward / lookahead / leverage / shorting. Reads only the three
    staged files; when write=True writes ONLY the variant report (json + md) under
    reports/crypto_d1_variant_backtest/. Never fetches, never executes a live order,
    never touches a gate."""
    prep = check_variant_prep_readiness(repo_root)
    constraints = prep.get("variant_constraints") or {}
    forbidden_on = [
        k
        for k in ("optimization", "parameter_search", "walk_forward",
                  "lookahead_allowed", "allow_shorting", "allow_leverage", "allow_margin")
        if constraints.get(k) is not False
    ]
    blockers: list[str] = []
    if prep["verdict"] != VERDICT_READY:
        blockers.append("variant_prep_not_ready")
        blockers.extend("prep:" + b for b in prep.get("blockers", []))
    blockers.extend("constraint_violation:" + k for k in forbidden_on)
    if blockers:
        return _blocked_report(blockers, constraints)

    input_dir = os.path.join(repo_root, QA_APPROVED_INPUT_DIR)
    series_by_symbol: dict[str, dict[str, float]] = {}
    files_read: list[str] = []
    for sym in QA_REQUIRED_SYMBOLS:
        path = os.path.join(input_dir, sym + "_1d.csv")
        series_by_symbol[sym] = _read_close_series(path)
        files_read.append(path)

    common = set.intersection(*(set(s.keys()) for s in series_by_symbol.values()))
    common_dates = sorted(common)
    if len(common_dates) < 2:
        return _blocked_report(["insufficient_common_history"], constraints)

    manifests = build_variant_manifests()
    variant_results = [_simulate_variant(m, series_by_symbol, common_dates) for m in manifests]

    eligible_variants = [v["variant_id"] for v in variant_results if v["eligible_for_paper_prep"]]
    variants_beating_floor = [v["variant_id"] for v in variant_results if v["beats_drawdown_floor"]]

    report = _base_report(constraints)
    report.update(
        {
            "verdict": VERDICT_VARIANTS_COMPLETE,
            "blockers": [],
            "variant_prep_verdict": prep["verdict"],
            "symbols": list(QA_REQUIRED_SYMBOLS),
            "window": {"entry_date": common_dates[0], "exit_date": common_dates[-1],
                       "trading_days": len(common_dates)},
            "variant_count": len(variant_results),
            "variant_results": variant_results,
            "variants_beating_drawdown_floor": variants_beating_floor,
            "eligible_for_paper_prep": eligible_variants,
            "any_variant_eligible_for_paper_prep": bool(eligible_variants),
            "promotion_criteria": promotion_criteria(),
            "files_read": files_read,
        }
    )

    files_written: list[str] = []
    if write:
        rep_dir = os.path.join(repo_root, VARIANT_REPORT_DIR)
        os.makedirs(rep_dir, exist_ok=True)
        rep_json = os.path.join(rep_dir, "variant_backtest_report.json")
        with open(rep_json, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2)
        files_written.append(rep_json)
        rep_md = os.path.join(rep_dir, "variant_backtest_report.md")
        with open(rep_md, "w", encoding="utf-8") as fh:
            fh.write(render_variant_backtest_markdown(report))
        files_written.append(rep_md)

    report["files_written"] = files_written
    return report


def _base_report(constraints: dict[str, Any]) -> dict[str, Any]:
    """Common report skeleton carrying the read-only safety posture. Running these
    approved variants changes NO gate: paper / micro-live stay LOCKED."""
    return {
        "schema_version": RUNNER_SCHEMA_VERSION,
        "label": RUNNER_LABEL,
        "mode": RUNNER_MODE,
        "authorization": _AUTHORIZATION,
        "run_constraints": dict(constraints),
        # Capability posture: read-only backtest passes; nothing live.
        "executes_orders": False,
        "ran_optimization": False,
        "ran_parameter_search": False,
        "ran_walk_forward": False,
        "used_lookahead": False,
        "used_leverage": False,
        "used_shorting": False,
        "touches_broker_or_exchange": False,
        "uses_only_qa_passed_inputs": True,
        # Gate posture (UNCHANGED by this run):
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
        "unlocks_downstream_gate": False,
        "authorizes_paper_trading": False,
        "no_network_used": True,
        "no_credentials_used": True,
        "manual_csv_only": True,
    }


def _blocked_report(blockers: list[str], constraints: dict[str, Any]) -> dict[str, Any]:
    """A refusal report: prep was not READY (or a constraint was violated), so no
    variant ran and nothing was written."""
    report = _base_report(constraints)
    report.update(
        {
            "verdict": VERDICT_BLOCKED_NOT_READY,
            "blockers": list(blockers),
            "symbols": list(QA_REQUIRED_SYMBOLS),
            "variant_count": 0,
            "variant_results": [],
            "variants_beating_drawdown_floor": [],
            "eligible_for_paper_prep": [],
            "any_variant_eligible_for_paper_prep": False,
            "files_read": [],
            "files_written": [],
        }
    )
    return report


def validate_variant_backtest_report(report: Any) -> dict[str, Any]:
    """Validate (read-only) a variant report's shape and safety invariants. Returns
    {"valid": bool, "errors": [...]}; never raises."""
    errors: list[str] = []
    if not isinstance(report, dict):
        return {"valid": False, "errors": ["report_not_a_dict"]}
    r = report

    if r.get("verdict") not in (VERDICT_VARIANTS_COMPLETE, VERDICT_BLOCKED_NOT_READY):
        errors.append("bad_verdict")
    if r.get("schema_version") != RUNNER_SCHEMA_VERSION:
        errors.append("bad_schema_version")

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
        "used_leverage",
        "used_shorting",
        "touches_broker_or_exchange",
        "unlocks_downstream_gate",
        "authorizes_paper_trading",
    )
    for key in must_be_false:
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)

    if r.get("verdict") == VERDICT_VARIANTS_COMPLETE:
        results = r.get("variant_results")
        if not isinstance(results, list) or len(results) != 5:
            errors.append("expected_five_variant_results")
        else:
            for v in results:
                if not isinstance(v, dict) or not isinstance(v.get("performance"), dict):
                    errors.append("variant_performance_missing")
                    break
        # An eligible variant must carry no eligibility blockers.
        for v in results or []:
            if isinstance(v, dict) and v.get("eligible_for_paper_prep") is True and (v.get("eligibility_blockers") or []):
                errors.append("eligible_variant_with_blockers:" + str(v.get("variant_id")))

    return {"valid": not errors, "errors": errors}


def _pct(x: Any) -> str:
    try:
        return f"{float(x) * 100:.2f}%"
    except (TypeError, ValueError):
        return str(x)


def render_variant_backtest_markdown(report: Any) -> str:
    """Render a variant report as deterministic markdown. Pure string work."""
    r = report if isinstance(report, dict) else {}
    lines: list[str] = []
    lines.append("# Crypto-D1 Risk-Controlled Variant Backtest (5 pre-registered long-only variants)")
    lines.append("")
    lines.append("- Verdict: " + str(r.get("verdict", "")))
    lines.append("- Authorization: " + str(r.get("authorization", "")))
    blockers = r.get("blockers") or []
    lines.append("- Blockers: " + ("none" if not blockers else ", ".join(blockers)))
    win = r.get("window") or {}
    if win:
        lines.append("- Window: " + str(win.get("entry_date")) + " -> " + str(win.get("exit_date"))
                     + " (" + str(win.get("trading_days")) + " trading days)")
    lines.append("- Variants beating -50% drawdown floor: "
                 + (", ".join(r.get("variants_beating_drawdown_floor") or []) or "none"))
    lines.append("- Variants eligible for paper-prep review: "
                 + (", ".join(r.get("eligible_for_paper_prep") or []) or "none"))
    lines.append("")
    lines.append("## Per-variant results")
    for v in r.get("variant_results", []):
        perf = v.get("performance") or {}
        lines.append("### " + str(v.get("variant_id")) + " -- " + str(v.get("description")))
        lines.append("- Controls: " + ", ".join(v.get("controls") or []))
        lines.append("- Total return: " + _pct(perf.get("total_return"))
                     + " | CAGR: " + _pct(perf.get("cagr")))
        lines.append("- Max drawdown: " + _pct(perf.get("max_drawdown"))
                     + " | Sharpe: " + f"{float(perf.get('sharpe_ratio', 0)):.2f}"
                     + " | Vol: " + _pct(perf.get("annualized_volatility")))
        lines.append("- Beats -50% drawdown floor: " + str(v.get("beats_drawdown_floor")))
        lines.append("- Promotion decision: " + str(v.get("promotion_decision"))
                     + " | Eligible for paper-prep: " + str(v.get("eligible_for_paper_prep")))
        blk = v.get("eligibility_blockers") or []
        lines.append("- Eligibility blockers: " + ("none" if not blk else ", ".join(blk)))
        lines.append("")
    lines.append("## Gates (read-only metadata, UNCHANGED)")
    lines.append("- paper_trading_gate: LOCKED")
    lines.append("- micro_live_gate: LOCKED")
    lines.append("- executes_orders: False")
    lines.append("- touches_broker_or_exchange: False")
    return "\n".join(lines)


if __name__ == "__main__":  # pragma: no cover
    out = run_variant_backtests(repo_root=".", write=False)
    print(render_variant_backtest_markdown(out))
