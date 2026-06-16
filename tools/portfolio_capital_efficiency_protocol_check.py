"""SPARTA Portfolio Capital-Efficiency Protocol Memo — validator (research-only, stdlib).

Validates `reports/portfolio_capital_efficiency_protocol_v1/protocol.json`
against the required schema and the hard safety contract:
  * research_only is True; advisory_only is True
  * eight execution / fetch / connection / allocation / sizing / backtest
    flags are False:
      data_fetch_enabled
      exchange_connection_enabled
      live_trading_enabled
      broker_control_enabled
      paper_order_execution_enabled
      live_capital_allocation_enabled
      position_sizing_execution_enabled
      backtest_enabled
  * lane == 'portfolio_capital_efficiency'
  * lane_status_self_declared == 'WATCH'
  * c10_boundary.must_not_touch_c10 is True
  * scope.in_scope / scope.out_of_scope are non-empty lists; out_of_scope
    explicitly names live capital + execution exclusions
  * input_sources are all read_only; inadmissible_inputs is non-empty and
    names live balances + uncommitted working tree
  * capital_efficiency_metrics include the 5 declared metrics, each
    definition_only
  * allocation_baselines include the 4 declared models with discretionary_human
    marked WATCH_only
  * validation_phases include P0..P8
  * pass_watch_fail_rules + kill_conditions + required_future_artifacts +
    safety_boundaries + no_profit_claim_policy are non-empty
  * no profitability / live-readiness / allocate-now claim

Standard library only. No network. No broker/exchange imports. No subprocess.
No credential / env reads.

CLI:
  python tools/portfolio_capital_efficiency_protocol_check.py validate
  python tools/portfolio_capital_efficiency_protocol_check.py show
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PROTO_DIR_REL = "reports/portfolio_capital_efficiency_protocol_v1"
PROTO_JSON = "protocol.json"
PROTO_MD = "protocol.md"

REQUIRED_TOP_LEVEL_KEYS = (
    "protocol_id",
    "title",
    "version",
    "research_only",
    "advisory_only",
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
    "c10_boundary",
    "scope",
    "input_sources",
    "inadmissible_inputs",
    "capital_efficiency_metrics",
    "allocation_baselines",
    "validation_phases",
    "pass_watch_fail_rules",
    "kill_conditions",
    "required_future_artifacts",
    "safety_boundaries",
    "no_profit_claim_policy",
)

MUST_BE_FALSE_FLAGS = (
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

REQUIRED_BASELINE_IDS = (
    "equal_weight",
    "inverse_volatility",
    "capped_weight",
    "discretionary_human",
)

REQUIRED_VALIDATION_PHASES = (
    "P0_protocol",
    "P1_input_contract",
    "P2_efficiency_metric_spec",
    "P3_allocation_baseline_spec",
    "P4_overlap_correlation_spec",
    "P5_advisory_report_shape",
    "P6_robustness_sensitivity",
    "P7_paper_allocation_simulation",
    "P8_live_capital_allocation",
)

NON_EMPTY_LIST_SECTIONS = (
    "inadmissible_inputs",
    "kill_conditions",
    "required_future_artifacts",
    "safety_boundaries",
    "no_profit_claim_policy",
)

# Distinction phrases that must appear in the markdown.
DISTINCTION_PHRASES = (
    "A capital-efficiency score does not imply future returns",
    "An advisory allocation is not an execution instruction",
    "No allocation is authorized by this protocol alone",
    "Advisory-only",
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
    "allocate capital now",
    "increase position size",
    "execute this allocation",
)


def _load(repo_root: Path):
    p = repo_root / PROTO_DIR_REL / PROTO_JSON
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
        return False, ["protocol.json is not a JSON object"]

    for k in REQUIRED_TOP_LEVEL_KEYS:
        if k not in data:
            errors.append(f"missing key: {k}")

    for flag in MUST_BE_FALSE_FLAGS:
        if data.get(flag) is not False:
            errors.append(f"safety flag {flag} must be False (got {data.get(flag)!r})")
    if data.get("research_only") is not True:
        errors.append("research_only must be True")
    if data.get("advisory_only") is not True:
        errors.append("advisory_only must be True")

    # Lane.
    if data.get("lane") != "portfolio_capital_efficiency":
        errors.append(f"lane must be 'portfolio_capital_efficiency' (got {data.get('lane')!r})")
    if data.get("lane_status_self_declared") != "WATCH":
        errors.append(
            f"lane_status_self_declared must be 'WATCH' (got {data.get('lane_status_self_declared')!r})"
        )

    # C10 boundary.
    c10 = data.get("c10_boundary")
    if not isinstance(c10, dict):
        errors.append("c10_boundary must be a dict")
    elif c10.get("must_not_touch_c10") is not True:
        errors.append("c10_boundary.must_not_touch_c10 must be True")

    # Scope.
    scope = data.get("scope")
    if not isinstance(scope, dict):
        errors.append("scope must be a dict")
    else:
        for side in ("in_scope", "out_of_scope"):
            v = scope.get(side)
            if not isinstance(v, list) or not v:
                errors.append(f"scope.{side} must be a non-empty list")
        oos_join = " ".join(str(x) for x in (scope.get("out_of_scope") or [])).lower()
        for needle in ("live capital", "order placement"):
            if needle not in oos_join:
                errors.append(f"scope.out_of_scope missing exclusion phrase: {needle!r}")

    # Input sources all read_only.
    src = data.get("input_sources")
    if not isinstance(src, list) or not src:
        errors.append("input_sources must be a non-empty list")
    else:
        for s in src:
            if isinstance(s, dict) and s.get("access") != "read_only":
                errors.append(
                    f"input_source {s.get('id')!r} access must be 'read_only' (got {s.get('access')!r})"
                )

    # Inadmissible inputs must name live balances + uncommitted working tree.
    inadm = data.get("inadmissible_inputs")
    if not isinstance(inadm, list) or not inadm:
        errors.append("inadmissible_inputs must be a non-empty list")
    else:
        inadm_join = " ".join(str(x) for x in inadm).lower()
        for needle in ("live", "uncommitted"):
            if needle not in inadm_join:
                errors.append(f"inadmissible_inputs missing needle: {needle!r}")

    # Capital-efficiency metrics: 5 metrics, each definition_only.
    cem = data.get("capital_efficiency_metrics")
    if not isinstance(cem, list):
        errors.append("capital_efficiency_metrics must be a list")
        cem = []
    cem_ids = {m.get("id") for m in cem if isinstance(m, dict)}
    for mid in REQUIRED_METRIC_IDS:
        if mid not in cem_ids:
            errors.append(f"capital_efficiency_metrics missing id: {mid}")
    for m in cem:
        if isinstance(m, dict) and m.get("definition_only") is not True:
            errors.append(f"metric {m.get('id')!r} must be definition_only (got {m.get('definition_only')!r})")

    # Allocation baselines: 4 models, discretionary_human WATCH_only.
    ab = data.get("allocation_baselines")
    if not isinstance(ab, list):
        errors.append("allocation_baselines must be a list")
        ab = []
    ab_ids = {b.get("id") for b in ab if isinstance(b, dict)}
    for bid in REQUIRED_BASELINE_IDS:
        if bid not in ab_ids:
            errors.append(f"allocation_baselines missing id: {bid}")
    dh = next((b for b in ab if isinstance(b, dict) and b.get("id") == "discretionary_human"), None)
    if dh is not None and dh.get("status") != "WATCH_only":
        errors.append(f"discretionary_human status must be 'WATCH_only' (got {dh.get('status')!r})")

    # Validation phases: all P0..P8 markers present.
    vp = data.get("validation_phases")
    if not isinstance(vp, list) or not vp:
        errors.append("validation_phases must be a non-empty list")
    else:
        phase_ids = {p.get("phase") for p in vp if isinstance(p, dict)}
        for required in REQUIRED_VALIDATION_PHASES:
            if required not in phase_ids:
                errors.append(f"validation_phases missing phase: {required}")

    # pass_watch_fail_rules: PASS/WATCH/FAIL keys.
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

    # safety_boundaries must mention research-only / advisory / no broker /
    # no live / no order / no c10.
    sb = data.get("safety_boundaries") or []
    sb_join = " ".join(str(x) for x in sb).lower()
    for needle in ("research-only", "advisory-only", "no broker", "no live", "no order", "candidate #10"):
        if needle not in sb_join:
            errors.append(f"safety_boundaries missing safety phrase: {needle!r}")

    # Distinction phrases in markdown.
    mpath = repo_root / PROTO_DIR_REL / PROTO_MD
    if mpath.exists():
        md = mpath.read_text(encoding="utf-8")
        for phrase in DISTINCTION_PHRASES:
            if phrase not in md:
                errors.append(f"protocol.md missing distinction phrase: {phrase!r}")
        for phrase in FORBIDDEN_PHRASES:
            if phrase.lower() in md.lower():
                errors.append(f"protocol.md contains forbidden phrase: {phrase!r}")
    else:
        errors.append(f"missing: {mpath.as_posix()}")

    # JSON scan.
    blob = json.dumps(data, ensure_ascii=False).lower()
    for phrase in FORBIDDEN_PHRASES:
        if phrase.lower() in blob:
            errors.append(f"protocol.json contains forbidden phrase: {phrase!r}")

    return (not errors), errors


def show(repo_root: Path = REPO_ROOT) -> int:
    data, err = _load(repo_root)
    if err:
        print(err)
        return 1
    print(f"protocol_id:          {data.get('protocol_id')}")
    print(f"title:                {data.get('title')}")
    print(f"version:              {data.get('version')}")
    print(f"research_only:        {data.get('research_only')}")
    print(f"advisory_only:        {data.get('advisory_only')}")
    print(f"lane:                 {data.get('lane')}")
    print(f"lane_status:          {data.get('lane_status_self_declared')}")
    c10 = data.get("c10_boundary") or {}
    print(f"must_not_touch_c10:   {c10.get('must_not_touch_c10')}")
    print("safety flags (must all be False):")
    for f in MUST_BE_FALSE_FLAGS:
        print(f"  {f}: {data.get(f)}")
    cem = data.get("capital_efficiency_metrics") or []
    print(f"capital_efficiency_metrics ({len(cem)}):")
    for m in cem:
        if isinstance(m, dict):
            print(f"  - {str(m.get('id', '?')):>28}  definition_only={m.get('definition_only')}")
    ab = data.get("allocation_baselines") or []
    print(f"allocation_baselines ({len(ab)}):")
    for b in ab:
        if isinstance(b, dict):
            print(f"  - {str(b.get('id', '?')):>22}  status={b.get('status')}")
    vp = data.get("validation_phases") or []
    print(f"validation_phases ({len(vp)}):")
    for p in vp:
        if isinstance(p, dict):
            print(f"  - {p.get('phase')}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="SPARTA Portfolio Capital-Efficiency Protocol Memo validator (research-only)",
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
