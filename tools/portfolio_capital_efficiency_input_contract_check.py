"""SPARTA Portfolio Capital-Efficiency Input Contract — validator (research-only, stdlib).

Validates `reports/portfolio_capital_efficiency_input_contract_v1/input_contract.json`
against the required schema and the hard safety contract:
  * research_only + advisory_only + framework_only are True
  * eight execution / fetch / connection / allocation / sizing / backtest
    flags are False
  * lane == 'portfolio_capital_efficiency'; phase == 'P1_input_contract'
  * lane_status_self_declared == 'WATCH'; verdict_ceiling max == 'WATCH'
  * companion_documents reference the P0 protocol
  * admissible_input_classes are all read_only + frozen_required
  * required_fields_per_input is non-empty
  * admissibility_rules require committed + frozen-with-checksum inputs
  * Candidate #10 is a DEFERRED, NOT-CONNECTED input:
      - deferred_inputs contains c10_frozen_replay_output with
        connection_status == 'deferred_not_connected'
      - c10_boundary.must_not_touch_c10 is True
      - c10_boundary.connection_status == 'deferred_not_connected'
  * inadmissible_inputs name live balances + uncommitted working tree
  * pass_watch_fail_rules + required_future_artifacts + safety_boundaries +
    no_profit_claim_policy are non-empty
  * no profitability / live-readiness / allocate-now / connect-c10 claim

Standard library only. No network. No broker/exchange imports. No subprocess.
No credential / env reads.

CLI:
  python tools/portfolio_capital_efficiency_input_contract_check.py validate
  python tools/portfolio_capital_efficiency_input_contract_check.py show
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTRACT_DIR_REL = "reports/portfolio_capital_efficiency_input_contract_v1"
CONTRACT_JSON = "input_contract.json"
CONTRACT_MD = "input_contract.md"

REQUIRED_TOP_LEVEL_KEYS = (
    "input_contract_id",
    "title",
    "version",
    "phase",
    "research_only",
    "advisory_only",
    "framework_only",
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
    "admissible_input_classes",
    "required_fields_per_input",
    "admissibility_rules",
    "deferred_inputs",
    "c10_boundary",
    "inadmissible_inputs",
    "verdict_ceiling_rules",
    "freeze_requirements",
    "pass_watch_fail_rules",
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

REQUIRED_INPUT_CLASS_IDS = (
    "strategy_report_registry_output",
    "strategy_candidate_registry_output",
    "frozen_per_strategy_backtest_report",
)

NON_EMPTY_LIST_SECTIONS = (
    "required_fields_per_input",
    "inadmissible_inputs",
    "required_future_artifacts",
    "safety_boundaries",
    "no_profit_claim_policy",
)

DISTINCTION_PHRASES = (
    "Advisory-only",
    "No allocation is authorized by this contract alone.",
    "Candidate #10 frozen replay outputs are a deferred future input and are not connected by this contract.",
    "A capital-efficiency score does not imply future returns.",
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
    p = repo_root / CONTRACT_DIR_REL / CONTRACT_JSON
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
        return False, ["input_contract.json is not a JSON object"]

    for k in REQUIRED_TOP_LEVEL_KEYS:
        if k not in data:
            errors.append(f"missing key: {k}")

    for flag in MUST_BE_FALSE_FLAGS:
        if data.get(flag) is not False:
            errors.append(f"safety flag {flag} must be False (got {data.get(flag)!r})")
    for true_flag in ("research_only", "advisory_only", "framework_only"):
        if data.get(true_flag) is not True:
            errors.append(f"{true_flag} must be True")

    # Lane + phase.
    if data.get("lane") != "portfolio_capital_efficiency":
        errors.append(f"lane must be 'portfolio_capital_efficiency' (got {data.get('lane')!r})")
    if data.get("phase") != "P1_input_contract":
        errors.append(f"phase must be 'P1_input_contract' (got {data.get('phase')!r})")
    if data.get("lane_status_self_declared") != "WATCH":
        errors.append(
            f"lane_status_self_declared must be 'WATCH' (got {data.get('lane_status_self_declared')!r})"
        )

    # Companion documents reference the P0 protocol.
    cd = data.get("companion_documents")
    if not isinstance(cd, dict):
        errors.append("companion_documents must be a dict")
    else:
        joined = " ".join(str(v) for v in cd.values())
        if "portfolio_capital_efficiency_protocol_v1" not in joined:
            errors.append("companion_documents must reference portfolio_capital_efficiency_protocol_v1")

    # Admissible input classes: all read_only + frozen_required; required ids present.
    aic = data.get("admissible_input_classes")
    if not isinstance(aic, list) or not aic:
        errors.append("admissible_input_classes must be a non-empty list")
        aic = []
    aic_ids = {c.get("id") for c in aic if isinstance(c, dict)}
    for cid in REQUIRED_INPUT_CLASS_IDS:
        if cid not in aic_ids:
            errors.append(f"admissible_input_classes missing id: {cid}")
    for c in aic:
        if isinstance(c, dict):
            if c.get("access") != "read_only":
                errors.append(f"input class {c.get('id')!r} access must be 'read_only' (got {c.get('access')!r})")
            if c.get("frozen_required") is not True:
                errors.append(f"input class {c.get('id')!r} frozen_required must be True")

    # Admissibility rules require committed + frozen-with-checksum.
    ar = data.get("admissibility_rules")
    if not isinstance(ar, dict):
        errors.append("admissibility_rules must be a dict")
    else:
        for needed in ("must_be_committed", "must_be_frozen_with_checksum"):
            if needed not in ar:
                errors.append(f"admissibility_rules missing key: {needed}")

    # Candidate #10 deferral.
    di = data.get("deferred_inputs")
    if not isinstance(di, list) or not di:
        errors.append("deferred_inputs must be a non-empty list")
        di = []
    c10_entry = next((d for d in di if isinstance(d, dict) and d.get("id") == "c10_frozen_replay_output"), None)
    if c10_entry is None:
        errors.append("deferred_inputs missing c10_frozen_replay_output entry")
    elif c10_entry.get("connection_status") != "deferred_not_connected":
        errors.append(
            f"c10 deferred entry connection_status must be 'deferred_not_connected' (got {c10_entry.get('connection_status')!r})"
        )

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

    # Inadmissible inputs name live + uncommitted.
    inadm = data.get("inadmissible_inputs")
    if not isinstance(inadm, list) or not inadm:
        errors.append("inadmissible_inputs must be a non-empty list")
    else:
        inadm_join = " ".join(str(x) for x in inadm).lower()
        for needle in ("live", "uncommitted"):
            if needle not in inadm_join:
                errors.append(f"inadmissible_inputs missing needle: {needle!r}")

    # Verdict ceiling.
    vcr = data.get("verdict_ceiling_rules")
    if not isinstance(vcr, dict):
        errors.append("verdict_ceiling_rules must be a dict")
    else:
        if vcr.get("max_surfaced_verdict") != "WATCH":
            errors.append(f"verdict_ceiling_rules.max_surfaced_verdict must be 'WATCH' (got {vcr.get('max_surfaced_verdict')!r})")
        if vcr.get("pass_active_strong_forbidden") is not True:
            errors.append("verdict_ceiling_rules.pass_active_strong_forbidden must be True")

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

    # safety_boundaries must mention the key phrases.
    sb = data.get("safety_boundaries") or []
    sb_join = " ".join(str(x) for x in sb).lower()
    for needle in ("research-only", "advisory-only", "no broker", "no live", "candidate #10", "not connected"):
        if needle not in sb_join:
            errors.append(f"safety_boundaries missing safety phrase: {needle!r}")

    # Distinction phrases in markdown.
    mpath = repo_root / CONTRACT_DIR_REL / CONTRACT_MD
    if mpath.exists():
        md = mpath.read_text(encoding="utf-8")
        for phrase in DISTINCTION_PHRASES:
            if phrase not in md:
                errors.append(f"input_contract.md missing distinction phrase: {phrase!r}")
        for phrase in FORBIDDEN_PHRASES:
            if phrase.lower() in md.lower():
                errors.append(f"input_contract.md contains forbidden phrase: {phrase!r}")
    else:
        errors.append(f"missing: {mpath.as_posix()}")

    # JSON scan.
    blob = json.dumps(data, ensure_ascii=False).lower()
    for phrase in FORBIDDEN_PHRASES:
        if phrase.lower() in blob:
            errors.append(f"input_contract.json contains forbidden phrase: {phrase!r}")

    return (not errors), errors


def show(repo_root: Path = REPO_ROOT) -> int:
    data, err = _load(repo_root)
    if err:
        print(err)
        return 1
    print(f"input_contract_id:    {data.get('input_contract_id')}")
    print(f"title:                {data.get('title')}")
    print(f"version:              {data.get('version')}")
    print(f"phase:                {data.get('phase')}")
    print(f"lane:                 {data.get('lane')}")
    print(f"lane_status:          {data.get('lane_status_self_declared')}")
    print(f"framework_only:       {data.get('framework_only')}")
    c10b = data.get("c10_boundary") or {}
    print(f"c10 must_not_touch:   {c10b.get('must_not_touch_c10')}")
    print(f"c10 connection:       {c10b.get('connection_status')}")
    print("safety flags (must all be False):")
    for f in MUST_BE_FALSE_FLAGS:
        print(f"  {f}: {data.get(f)}")
    aic = data.get("admissible_input_classes") or []
    print(f"admissible_input_classes ({len(aic)}):")
    for c in aic:
        if isinstance(c, dict):
            print(f"  - {str(c.get('id', '?')):>36}  read_only={c.get('access') == 'read_only'} frozen={c.get('frozen_required')}")
    di = data.get("deferred_inputs") or []
    print(f"deferred_inputs ({len(di)}):")
    for d in di:
        if isinstance(d, dict):
            print(f"  - {str(d.get('id', '?')):>24}  status={d.get('connection_status')}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="SPARTA Portfolio Capital-Efficiency Input Contract validator (research-only)",
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
