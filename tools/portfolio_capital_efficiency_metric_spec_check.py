"""SPARTA Portfolio Capital-Efficiency Metric Spec — validator (research-only, stdlib).

Validates `reports/portfolio_capital_efficiency_metric_spec_v1/metric_spec.json`
against the required schema and the hard safety contract:
  * research_only + advisory_only + framework_only are True; compute_enabled
    + eight execution / fetch / connection / allocation / sizing / backtest
    flags are False
  * lane == 'portfolio_capital_efficiency'; phase == 'P2_efficiency_metric_spec'
  * lane_status_self_declared == 'WATCH'; verdict_ceiling max == 'WATCH'
  * companion_documents reference the P0 protocol + P1 input contract
  * the 5 metrics are present, each with formula + inputs + units +
    computed_in_this_bundle == False + non-empty validation_rules
  * marginal_capital_efficiency carries ranking_only == True
  * metric_validation_rules + advisory_report_schema present;
    advisory_report_schema.produced_in_this_bundle == False
  * Candidate #10 deferred: c10_boundary.must_not_touch_c10 True and
    connection_status == 'deferred_not_connected'
  * pass_watch_fail_rules + required_future_artifacts + safety_boundaries +
    no_profit_claim_policy non-empty
  * no profitability / live-readiness / allocate-now / connect-c10 claim

Standard library only. No network. No broker/exchange imports. No subprocess.
No credential / env reads.

CLI:
  python tools/portfolio_capital_efficiency_metric_spec_check.py validate
  python tools/portfolio_capital_efficiency_metric_spec_check.py show
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SPEC_DIR_REL = "reports/portfolio_capital_efficiency_metric_spec_v1"
SPEC_JSON = "metric_spec.json"
SPEC_MD = "metric_spec.md"

REQUIRED_TOP_LEVEL_KEYS = (
    "metric_spec_id",
    "title",
    "version",
    "phase",
    "research_only",
    "advisory_only",
    "framework_only",
    "compute_enabled",
    "data_fetch_enabled",
    "exchange_connection_enabled",
    "live_trading_enabled",
    "broker_control_enabled",
    "paper_order_execution_enabled",
    "live_capital_allocation_enabled",
    "position_sizing_execution_enabled",
    "backtest_enabled",
    "lane",
    "lane_status_self_declared",
    "companion_documents",
    "verdict_ceiling_rules",
    "c10_boundary",
    "metrics",
    "input_field_dependencies",
    "metric_validation_rules",
    "advisory_report_schema",
    "pass_watch_fail_rules",
    "required_future_artifacts",
    "safety_boundaries",
    "no_profit_claim_policy",
)

MUST_BE_FALSE_FLAGS = (
    "compute_enabled",
    "data_fetch_enabled",
    "exchange_connection_enabled",
    "live_trading_enabled",
    "broker_control_enabled",
    "paper_order_execution_enabled",
    "live_capital_allocation_enabled",
    "position_sizing_execution_enabled",
    "backtest_enabled",
)

REQUIRED_METRIC_IDS = (
    "capital_at_risk_budget",
    "candidate_overlap",
    "diversification_ratio",
    "concentration_limit",
    "marginal_capital_efficiency",
)

NON_EMPTY_LIST_SECTIONS = (
    "required_future_artifacts",
    "safety_boundaries",
    "no_profit_claim_policy",
)

DISTINCTION_PHRASES = (
    "Advisory-only",
    "No metric is computed in this bundle.",
    "A capital-efficiency score does not imply future returns.",
    "An advisory allocation is not an execution instruction.",
    "Candidate #10 remains deferred and is not connected by this spec.",
)

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
    "allocate capital now",
    "increase position size",
    "execute this allocation",
    "connect c10 now",
)


def _load(repo_root: Path):
    p = repo_root / SPEC_DIR_REL / SPEC_JSON
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
        return False, ["metric_spec.json is not a JSON object"]

    for k in REQUIRED_TOP_LEVEL_KEYS:
        if k not in data:
            errors.append(f"missing key: {k}")

    for flag in MUST_BE_FALSE_FLAGS:
        if data.get(flag) is not False:
            errors.append(f"safety flag {flag} must be False (got {data.get(flag)!r})")
    for true_flag in ("research_only", "advisory_only", "framework_only"):
        if data.get(true_flag) is not True:
            errors.append(f"{true_flag} must be True")

    if data.get("lane") != "portfolio_capital_efficiency":
        errors.append(f"lane must be 'portfolio_capital_efficiency' (got {data.get('lane')!r})")
    if data.get("phase") != "P2_efficiency_metric_spec":
        errors.append(f"phase must be 'P2_efficiency_metric_spec' (got {data.get('phase')!r})")
    if data.get("lane_status_self_declared") != "WATCH":
        errors.append(
            f"lane_status_self_declared must be 'WATCH' (got {data.get('lane_status_self_declared')!r})"
        )

    # Companion documents reference P0 + P1.
    cd = data.get("companion_documents")
    if not isinstance(cd, dict):
        errors.append("companion_documents must be a dict")
    else:
        joined = " ".join(str(v) for v in cd.values())
        for needle in ("portfolio_capital_efficiency_protocol_v1", "portfolio_capital_efficiency_input_contract_v1"):
            if needle not in joined:
                errors.append(f"companion_documents must reference {needle}")

    # Verdict ceiling.
    vcr = data.get("verdict_ceiling_rules")
    if not isinstance(vcr, dict):
        errors.append("verdict_ceiling_rules must be a dict")
    else:
        if vcr.get("max_surfaced_verdict") != "WATCH":
            errors.append(f"verdict_ceiling_rules.max_surfaced_verdict must be 'WATCH' (got {vcr.get('max_surfaced_verdict')!r})")
        if vcr.get("pass_active_strong_forbidden") is not True:
            errors.append("verdict_ceiling_rules.pass_active_strong_forbidden must be True")

    # C10 boundary.
    c10b = data.get("c10_boundary")
    if not isinstance(c10b, dict):
        errors.append("c10_boundary must be a dict")
    else:
        if c10b.get("must_not_touch_c10") is not True:
            errors.append("c10_boundary.must_not_touch_c10 must be True")
        if c10b.get("connection_status") != "deferred_not_connected":
            errors.append(
                f"c10_boundary.connection_status must be 'deferred_not_connected' (got {c10b.get('connection_status')!r})"
            )

    # Metrics.
    metrics = data.get("metrics")
    if not isinstance(metrics, list) or not metrics:
        errors.append("metrics must be a non-empty list")
        metrics = []
    m_by_id = {m.get("id"): m for m in metrics if isinstance(m, dict)}
    for mid in REQUIRED_METRIC_IDS:
        if mid not in m_by_id:
            errors.append(f"metrics missing id: {mid}")
    for m in metrics:
        if not isinstance(m, dict):
            continue
        mid = m.get("id")
        if m.get("computed_in_this_bundle") is not False:
            errors.append(f"metric {mid!r} computed_in_this_bundle must be False (spec-only)")
        if not m.get("formula"):
            errors.append(f"metric {mid!r} missing formula")
        if not isinstance(m.get("inputs"), list) or not m.get("inputs"):
            errors.append(f"metric {mid!r} inputs must be a non-empty list")
        if not m.get("units"):
            errors.append(f"metric {mid!r} missing units")
        if not isinstance(m.get("validation_rules"), list) or not m.get("validation_rules"):
            errors.append(f"metric {mid!r} validation_rules must be a non-empty list")
    # marginal_capital_efficiency must be ranking_only.
    mce = m_by_id.get("marginal_capital_efficiency")
    if isinstance(mce, dict) and mce.get("ranking_only") is not True:
        errors.append("marginal_capital_efficiency must carry ranking_only == True")

    # metric_validation_rules present + non-empty.
    mvr = data.get("metric_validation_rules")
    if not isinstance(mvr, dict) or not mvr:
        errors.append("metric_validation_rules must be a non-empty dict")

    # advisory_report_schema not produced here.
    ars = data.get("advisory_report_schema")
    if not isinstance(ars, dict):
        errors.append("advisory_report_schema must be a dict")
    else:
        if ars.get("produced_in_this_bundle") is not False:
            errors.append("advisory_report_schema.produced_in_this_bundle must be False")
        for side in ("portfolio_level_fields", "per_candidate_fields"):
            if not isinstance(ars.get(side), list) or not ars.get(side):
                errors.append(f"advisory_report_schema.{side} must be a non-empty list")

    # pass_watch_fail_rules.
    pwf = data.get("pass_watch_fail_rules")
    if isinstance(pwf, dict):
        for k in ("PASS", "WATCH", "FAIL"):
            if k not in pwf:
                errors.append(f"pass_watch_fail_rules missing key: {k}")
    else:
        errors.append("pass_watch_fail_rules must be a dict")

    # Non-empty list sections.
    for k in NON_EMPTY_LIST_SECTIONS:
        v = data.get(k)
        if not isinstance(v, list) or not v:
            errors.append(f"section {k} must be a non-empty list")

    # safety_boundaries phrases.
    sb = data.get("safety_boundaries") or []
    sb_join = " ".join(str(x) for x in sb).lower()
    for needle in ("research-only", "advisory-only", "no broker", "no live", "candidate #10", "no metric computed"):
        if needle not in sb_join:
            errors.append(f"safety_boundaries missing safety phrase: {needle!r}")

    # Distinction phrases in markdown.
    mpath = repo_root / SPEC_DIR_REL / SPEC_MD
    if mpath.exists():
        md = mpath.read_text(encoding="utf-8")
        for phrase in DISTINCTION_PHRASES:
            if phrase not in md:
                errors.append(f"metric_spec.md missing distinction phrase: {phrase!r}")
        for phrase in FORBIDDEN_PHRASES:
            if phrase.lower() in md.lower():
                errors.append(f"metric_spec.md contains forbidden phrase: {phrase!r}")
    else:
        errors.append(f"missing: {mpath.as_posix()}")

    # JSON scan.
    blob = json.dumps(data, ensure_ascii=False).lower()
    for phrase in FORBIDDEN_PHRASES:
        if phrase.lower() in blob:
            errors.append(f"metric_spec.json contains forbidden phrase: {phrase!r}")

    return (not errors), errors


def show(repo_root: Path = REPO_ROOT) -> int:
    data, err = _load(repo_root)
    if err:
        print(err)
        return 1
    print(f"metric_spec_id:       {data.get('metric_spec_id')}")
    print(f"title:                {data.get('title')}")
    print(f"version:              {data.get('version')}")
    print(f"phase:                {data.get('phase')}")
    print(f"lane:                 {data.get('lane')}")
    print(f"lane_status:          {data.get('lane_status_self_declared')}")
    print(f"compute_enabled:      {data.get('compute_enabled')}")
    c10b = data.get("c10_boundary") or {}
    print(f"c10 must_not_touch:   {c10b.get('must_not_touch_c10')}")
    print(f"c10 connection:       {c10b.get('connection_status')}")
    print("safety flags (must all be False):")
    for f in MUST_BE_FALSE_FLAGS:
        print(f"  {f}: {data.get(f)}")
    metrics = data.get("metrics") or []
    print(f"metrics ({len(metrics)}):")
    for m in metrics:
        if isinstance(m, dict):
            print(f"  - {str(m.get('id', '?')):>30}  computed={m.get('computed_in_this_bundle')} ranking_only={m.get('ranking_only')}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="SPARTA Portfolio Capital-Efficiency Metric Spec validator (research-only)",
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
