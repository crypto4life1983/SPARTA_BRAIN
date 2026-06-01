"""SPARTA Crypto-D1 Baseline Backtest Plan -- validator (research-only, stdlib).

Validates `reports/crypto_d1_baseline_backtest_plan_v1/backtest_plan.json`
against the required schema and the hard safety contract:
  * research_only is True
  * seven execution / fetch / connection / backtest-execution /
    dataset-processing flags are False:
      data_fetch_enabled
      exchange_connection_enabled
      live_trading_enabled
      broker_control_enabled
      paper_order_execution_enabled
      backtest_execution_enabled
      dataset_processing_enabled
  * lane == 'crypto_d1_protocol'
  * target_assets include BTC, ETH, SOL
  * allowed_market_type == 'spot'; perp_futures + dated_futures + options +
    leveraged in forbidden_market_types
  * timeframe.primary == '1d'; intraday is explicitly out of scope
  * baseline_strategy_families include the 6 declared families with
    mean_reversion marked WATCH_only
  * parameter_policy forbids unlimited optimization
  * required_dataset_gate enforces frozen + QA_PASS (or approved QA_WARN) +
    no-lookahead-check
  * report_schema.required_fields contains all 27 future report fields
  * metrics_required contains the 17 declared metrics
  * pass_watch_fail_rules + kill_conditions + forbidden_actions +
    safety_boundaries are non-empty
  * cost_model_requirements / slippage_model_requirements present and
    forbid zero-cost baselines
  * no profitability / live-readiness / backtest-authorize claim in either
    file

Standard library only. No network. No broker/exchange imports. No subprocess.
No credential / env reads.

CLI:
  python tools/crypto_d1_backtest_plan_check.py validate
  python tools/crypto_d1_backtest_plan_check.py show
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLAN_DIR_REL = "reports/crypto_d1_baseline_backtest_plan_v1"
PLAN_JSON = "backtest_plan.json"
PLAN_MD = "backtest_plan.md"

REQUIRED_TOP_LEVEL_KEYS = (
    "backtest_plan_id",
    "title",
    "version",
    "research_only",
    "data_fetch_enabled",
    "exchange_connection_enabled",
    "live_trading_enabled",
    "broker_control_enabled",
    "paper_order_execution_enabled",
    "backtest_execution_enabled",
    "dataset_processing_enabled",
    "lane",
    "target_assets",
    "timeframe",
    "allowed_market_type",
    "forbidden_market_types",
    "required_prior_artifacts",
    "required_dataset_gate",
    "baseline_strategy_families",
    "parameter_policy",
    "train_test_policy",
    "IS_OOS_policy",
    "walk_forward_policy",
    "cost_model_requirements",
    "slippage_model_requirements",
    "position_sizing_policy",
    "risk_model_requirements",
    "metrics_required",
    "report_schema",
    "candidate_registry_update_rules",
    "pass_watch_fail_rules",
    "kill_conditions",
    "forbidden_actions",
    "required_future_artifacts",
    "safety_boundaries",
)

MUST_BE_FALSE_FLAGS = (
    "data_fetch_enabled",
    "exchange_connection_enabled",
    "live_trading_enabled",
    "broker_control_enabled",
    "paper_order_execution_enabled",
    "backtest_execution_enabled",
    "dataset_processing_enabled",
)

REQUIRED_TARGET_ASSETS = ("BTC", "ETH", "SOL")

REQUIRED_STRATEGY_FAMILY_IDS = (
    "buy_and_hold_benchmark",
    "donchian_channel_breakout",
    "moving_average_trend_filter",
    "momentum_continuation",
    "volatility_regime_gate",
    "mean_reversion",
)

REQUIRED_REPORT_SCHEMA_FIELDS = (
    "run_id",
    "strategy_id",
    "dataset_id",
    "dataset_version",
    "protocol_version",
    "data_contract_version",
    "manifest_version",
    "QA_report_id",
    "generated_at",
    "assets",
    "timeframe",
    "market_type",
    "strategy_family",
    "parameters",
    "cost_model",
    "slippage_model",
    "IS_period",
    "OOS_period",
    "metrics",
    "per_asset_metrics",
    "benchmark_metrics",
    "pass_watch_fail_status",
    "failure_reasons",
    "warnings",
    "next_action",
    "forbidden_next_steps",
    "safety_flags",
)

REQUIRED_METRICS = (
    "CAGR_or_total_return",
    "annualized_volatility",
    "max_drawdown",
    "sharpe_like_risk_metric_with_caveats",
    "win_rate",
    "trade_count",
    "average_trade_return",
    "median_trade_return",
    "exposure_percentage",
    "turnover",
    "fee_slippage_paid",
    "OOS_return",
    "OOS_drawdown",
    "per_asset_results",
    "basket_results",
    "benchmark_comparison",
    "sensitivity_summary",
)

REQUIRED_DATASET_GATE_KEYS = (
    "dataset_exists_on_disk",
    "dataset_manifest_exists",
    "qa_freeze_report_exists",
    "dataset_is_FROZEN",
    "qa_status_pass_or_approved_warn",
    "dataset_id_and_version_cited_in_report",
    "data_contract_version_cited_in_report",
    "protocol_version_cited_in_report",
    "manifest_version_cited_in_report",
    "qa_report_id_cited_in_report",
    "no_lookahead_qa_check_passed",
    "duplicate_missing_timestamp_checks_passed",
)

REQUIRED_PARAMETER_POLICY_KEYS = (
    "small_pre_registered_grid_only",
    "no_unlimited_optimization",
    "no_genetic_search",
    "no_ai_selected_best_parameter_after_seeing_oos",
    "no_repeated_tuning_on_oos",
    "parameter_count_budget_per_family",
    "all_combinations_logged",
    "chosen_parameter_must_be_explainable",
    "baseline_first_complexity_later",
)

REQUIRED_COST_MODEL_KEYS = (
    "spot_taker_fee_assumption_required",
    "default_assumption",
    "fees_as_distinct_pnl_line_required",
    "no_pass_if_costs_ignored",
    "cost_sensitivity_test_required_before_pass",
)

REQUIRED_SLIPPAGE_KEYS = (
    "slippage_assumption_required",
    "spread_proxy_required_when_quote_data_unavailable",
    "no_zero_slippage_baseline",
)

REQUIRED_POSITION_SIZING_KEYS = (
    "no_leverage",
    "long_only_spot_first",
    "no_shorting_in_this_protocol",
    "cash_or_risk_off_state_required",
)

NON_EMPTY_LIST_SECTIONS = (
    "forbidden_market_types",
    "required_prior_artifacts",
    "metrics_required",
    "kill_conditions",
    "forbidden_actions",
    "required_future_artifacts",
    "safety_boundaries",
)

# Distinction phrases that must appear in the markdown for word discipline.
DISTINCTION_PHRASES = (
    "This plan does not imply edge",
    "No backtest is run by this bundle",
    "No historical result is produced by this bundle",
    "A future PASS is not trading authorization",
    "No paper/live trading is authorized",
    "No data fetch is authorized",
    "Crypto trend ideas are not profitable until tested",
    "24/7",
)

# Forbidden capability claims.
FORBIDDEN_PHRASES = (
    "guaranteed profit",
    "risk-free profit",
    "guaranteed alpha",
    "live-ready",
    "production-ready",
    "live trading enabled",
    "this is profitable",
    "we have an edge",
    "place the order",
    "place an order",
    "connect to exchange",
    "fetch live data",
)


def _load(repo_root: Path):
    p = repo_root / PLAN_DIR_REL / PLAN_JSON
    if not p.exists():
        return None, f"missing: {p.as_posix()}"
    try:
        return json.loads(p.read_text(encoding="utf-8")), None
    except Exception as exc:  # noqa: BLE001
        return None, f"invalid JSON ({type(exc).__name__}): {p.as_posix()}"


def validate(repo_root: Path = REPO_ROOT):
    errors: list = []
    data, err = _load(repo_root)
    if err:
        return False, [err]
    if not isinstance(data, dict):
        return False, ["backtest_plan.json is not a JSON object"]

    for k in REQUIRED_TOP_LEVEL_KEYS:
        if k not in data:
            errors.append(f"missing key: {k}")

    for flag in MUST_BE_FALSE_FLAGS:
        if data.get(flag) is not False:
            errors.append(f"safety flag {flag} must be False (got {data.get(flag)!r})")
    if data.get("research_only") is not True:
        errors.append("research_only must be True")

    if data.get("lane") != "crypto_d1_protocol":
        errors.append(f"lane must be 'crypto_d1_protocol' (got {data.get('lane')!r})")

    tas = data.get("target_assets")
    if not isinstance(tas, list) or not tas:
        errors.append("target_assets must be a non-empty list")
    else:
        canonical_set = {a.get("symbol_canonical") for a in tas if isinstance(a, dict)}
        for asset in REQUIRED_TARGET_ASSETS:
            if asset not in canonical_set:
                errors.append(f"target_assets missing required canonical symbol: {asset}")

    if data.get("allowed_market_type") != "spot":
        errors.append(f"allowed_market_type must be 'spot' (got {data.get('allowed_market_type')!r})")

    fmt = data.get("forbidden_market_types")
    if not isinstance(fmt, list) or not fmt:
        errors.append("forbidden_market_types must be a non-empty list")
    else:
        joined = " ".join(str(x) for x in fmt).lower()
        for needle in ("perp", "dated_futures", "options", "leveraged"):
            if needle not in joined:
                errors.append(f"forbidden_market_types missing needle: {needle!r}")

    tf = data.get("timeframe")
    if not isinstance(tf, dict):
        errors.append("timeframe must be a dict")
    else:
        if tf.get("primary") != "1d":
            errors.append(f"timeframe.primary must be '1d' (got {tf.get('primary')!r})")
        if tf.get("intraday_explicitly_out_of_scope") is not True:
            errors.append("timeframe.intraday_explicitly_out_of_scope must be True")

    sf = data.get("baseline_strategy_families")
    if not isinstance(sf, list) or not sf:
        errors.append("baseline_strategy_families must be a non-empty list")
    else:
        sf_ids = {f.get("id") for f in sf if isinstance(f, dict)}
        for fid in REQUIRED_STRATEGY_FAMILY_IDS:
            if fid not in sf_ids:
                errors.append(f"baseline_strategy_families missing id: {fid}")
        mr = next((f for f in sf if isinstance(f, dict) and f.get("id") == "mean_reversion"), None)
        if mr is not None and mr.get("status") != "WATCH_only":
            errors.append(f"mean_reversion status must be 'WATCH_only' (got {mr.get('status')!r})")
        bench = next((f for f in sf if isinstance(f, dict) and f.get("id") == "buy_and_hold_benchmark"), None)
        if bench is not None and bench.get("status") != "benchmark":
            errors.append(f"buy_and_hold_benchmark status must be 'benchmark' (got {bench.get('status')!r})")

    pp = data.get("parameter_policy")
    if not isinstance(pp, dict):
        errors.append("parameter_policy must be a dict")
    else:
        for k in REQUIRED_PARAMETER_POLICY_KEYS:
            if k not in pp:
                errors.append(f"parameter_policy missing key: {k}")
        for k in ("no_unlimited_optimization", "no_genetic_search",
                  "no_ai_selected_best_parameter_after_seeing_oos",
                  "no_repeated_tuning_on_oos", "all_combinations_logged"):
            if pp.get(k) is not True:
                errors.append(f"parameter_policy.{k} must be True")

    dg = data.get("required_dataset_gate")
    if not isinstance(dg, dict):
        errors.append("required_dataset_gate must be a dict")
    else:
        for k in REQUIRED_DATASET_GATE_KEYS:
            if k not in dg:
                errors.append(f"required_dataset_gate missing key: {k}")

    cm = data.get("cost_model_requirements")
    if not isinstance(cm, dict):
        errors.append("cost_model_requirements must be a dict")
    else:
        for k in REQUIRED_COST_MODEL_KEYS:
            if k not in cm:
                errors.append(f"cost_model_requirements missing key: {k}")
        if cm.get("no_pass_if_costs_ignored") is not True:
            errors.append("cost_model_requirements.no_pass_if_costs_ignored must be True")
        if cm.get("fees_as_distinct_pnl_line_required") is not True:
            errors.append("cost_model_requirements.fees_as_distinct_pnl_line_required must be True")

    sm = data.get("slippage_model_requirements")
    if not isinstance(sm, dict):
        errors.append("slippage_model_requirements must be a dict")
    else:
        for k in REQUIRED_SLIPPAGE_KEYS:
            if k not in sm:
                errors.append(f"slippage_model_requirements missing key: {k}")
        if sm.get("no_zero_slippage_baseline") is not True:
            errors.append("slippage_model_requirements.no_zero_slippage_baseline must be True")

    ps = data.get("position_sizing_policy")
    if not isinstance(ps, dict):
        errors.append("position_sizing_policy must be a dict")
    else:
        for k in REQUIRED_POSITION_SIZING_KEYS:
            if k not in ps:
                errors.append(f"position_sizing_policy missing key: {k}")
        for k in ("no_leverage", "long_only_spot_first", "no_shorting_in_this_protocol"):
            if ps.get(k) is not True:
                errors.append(f"position_sizing_policy.{k} must be True")

    mr = data.get("metrics_required")
    if not isinstance(mr, list) or not mr:
        errors.append("metrics_required must be a non-empty list")
    else:
        mr_set = set(mr)
        for m in REQUIRED_METRICS:
            if m not in mr_set:
                errors.append(f"metrics_required missing metric: {m}")

    rs = data.get("report_schema")
    if not isinstance(rs, dict):
        errors.append("report_schema must be a dict")
    else:
        rf = rs.get("required_fields")
        if not isinstance(rf, list) or not rf:
            errors.append("report_schema.required_fields must be a non-empty list")
        else:
            rf_set = set(rf)
            for fld in REQUIRED_REPORT_SCHEMA_FIELDS:
                if fld not in rf_set:
                    errors.append(f"report_schema.required_fields missing field: {fld}")
        if isinstance(rf, list) and rs.get("field_count") is not None:
            try:
                if int(rs.get("field_count")) != len(rf):
                    errors.append(
                        f"report_schema.field_count ({rs.get('field_count')}) "
                        f"does not match len(required_fields) ({len(rf)})"
                    )
            except (TypeError, ValueError):
                errors.append("report_schema.field_count must be an integer")

    pwf = data.get("pass_watch_fail_rules")
    if isinstance(pwf, dict):
        for k in ("PASS", "WATCH", "FAIL"):
            if k not in pwf:
                errors.append(f"pass_watch_fail_rules missing key: {k}")
    elif isinstance(pwf, list):
        joined = " ".join(str(x) for x in pwf)
        for k in ("PASS", "WATCH", "FAIL"):
            if k not in joined:
                errors.append(f"pass_watch_fail_rules missing marker: {k}")
    else:
        errors.append("pass_watch_fail_rules must be a dict or list")

    for k in NON_EMPTY_LIST_SECTIONS:
        v = data.get(k)
        if not isinstance(v, list) or not v:
            errors.append(f"section {k} must be a non-empty list")

    sb = data.get("safety_boundaries") or []
    sb_join = " ".join(str(x) for x in sb).lower()
    for needle in ("research-only", "no broker", "no live", "no order"):
        if needle not in sb_join:
            errors.append(f"safety_boundaries missing safety phrase: {needle!r}")

    mpath = repo_root / PLAN_DIR_REL / PLAN_MD
    if mpath.exists():
        md = mpath.read_text(encoding="utf-8")
        for phrase in DISTINCTION_PHRASES:
            if phrase not in md:
                errors.append(f"backtest_plan.md missing distinction phrase: {phrase!r}")
        for phrase in FORBIDDEN_PHRASES:
            if phrase.lower() in md.lower():
                errors.append(f"backtest_plan.md contains forbidden phrase: {phrase!r}")
    else:
        errors.append(f"missing: {mpath.as_posix()}")

    blob = json.dumps(data, ensure_ascii=False).lower()
    for phrase in FORBIDDEN_PHRASES:
        if phrase.lower() in blob:
            errors.append(f"backtest_plan.json contains forbidden phrase: {phrase!r}")

    return (not errors), errors


def show(repo_root: Path = REPO_ROOT) -> int:
    data, err = _load(repo_root)
    if err:
        print(err)
        return 1
    print(f"backtest_plan_id:    {data.get('backtest_plan_id')}")
    print(f"title:               {data.get('title')}")
    print(f"version:             {data.get('version')}")
    print(f"research_only:       {data.get('research_only')}")
    print(f"lane:                {data.get('lane')}")
    print(f"allowed_market_type: {data.get('allowed_market_type')}")
    print("safety flags (must all be False):")
    for f in MUST_BE_FALSE_FLAGS:
        print(f"  {f}: {data.get(f)}")
    tas = data.get("target_assets") or []
    print(f"target_assets ({len(tas)}):")
    for a in tas:
        if isinstance(a, dict):
            print(f"  - {a.get('symbol_canonical')}  {a.get('label')}  required={a.get('required')}")
    sf = data.get("baseline_strategy_families") or []
    print(f"baseline_strategy_families ({len(sf)}):")
    for f in sf:
        if isinstance(f, dict):
            print(f"  - {str(f.get('id', '?')):>32}  status={f.get('status')}")
    mr = data.get("metrics_required") or []
    print(f"metrics_required ({len(mr)})")
    rs = data.get("report_schema") or {}
    rf = rs.get("required_fields") or []
    print(f"report_schema.required_fields ({len(rf)})")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="SPARTA Crypto-D1 Baseline Backtest Plan validator (research-only)",
    )
    parser.add_argument("command", choices=("validate", "show"))
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    args = parser.parse_args(argv)
    root = Path(args.repo_root).resolve()
    if args.command == "validate":
        ok, errs = validate(root)
        if ok:
            print("validate: OK")
            return 0
        print("validate: FAIL")
        for e in errs:
            print(f"  - {e}")
        return 2
    if args.command == "show":
        return show(root)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
