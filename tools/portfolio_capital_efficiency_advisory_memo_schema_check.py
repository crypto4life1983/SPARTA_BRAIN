"""SPARTA Portfolio Capital-Efficiency Advisory Memo Schema — validator (research-only, stdlib).

Validates `reports/portfolio_capital_efficiency_advisory_memo_schema_v1/advisory_memo_schema.json`
against the required schema and the hard safety contract:
  * research_only + advisory_only + framework_only True; compute_enabled +
    capital_deployment_enabled + eight execution flags False
  * lane == 'portfolio_capital_efficiency'; phase == 'P5_advisory_memo_schema'
  * lane_status_self_declared == 'WATCH'; verdict_ceiling max == 'WATCH'
  * companion_documents reference P0 + P1 + P2 + P3 + P4
  * memo_produced_in_this_bundle == False
  * the 10 required memo sections are present, each produced_in_this_bundle ==
    False with a purpose + non-empty required_fields
  * allowed_classifications are EXACTLY the five allowed WATCH/undefined labels
    (each id is watch_only_* or undefined_insufficient_data)
  * forbidden_verdict_language enumerates the required forbidden tokens
    (PASS / ACTIVE / STRONG / approved for paper trading / approved for live
    trading / profit guarantee / capital deployment instruction /
    broker/order/credential logic)
  * verdict_language_rules + memo_global_rules present
  * Candidate #10 deferred: c10_boundary.must_not_touch_c10 True and
    connection_status == 'deferred_not_connected'
  * pass_watch_fail_rules + required_future_artifacts + safety_boundaries +
    no_profit_claim_policy non-empty
  * no capability-claim phrase (separate from the enumerated forbidden-verdict
    list) appears in md/json

Standard library only. No network. No broker/exchange imports. No subprocess.
No credential / env reads.

CLI:
  python tools/portfolio_capital_efficiency_advisory_memo_schema_check.py validate
  python tools/portfolio_capital_efficiency_advisory_memo_schema_check.py show
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR_REL = "reports/portfolio_capital_efficiency_advisory_memo_schema_v1"
SCHEMA_JSON = "advisory_memo_schema.json"
SCHEMA_MD = "advisory_memo_schema.md"

REQUIRED_TOP_LEVEL_KEYS = (
    "advisory_memo_schema_id",
    "title",
    "version",
    "phase",
    "research_only",
    "advisory_only",
    "framework_only",
    "compute_enabled",
    "capital_deployment_enabled",
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
    "memo_produced_in_this_bundle",
    "verdict_ceiling_rules",
    "c10_boundary",
    "memo_sections",
    "allowed_classifications",
    "forbidden_verdict_language",
    "verdict_language_rules",
    "memo_global_rules",
    "pass_watch_fail_rules",
    "required_future_artifacts",
    "safety_boundaries",
    "no_profit_claim_policy",
)

MUST_BE_FALSE_FLAGS = (
    "compute_enabled",
    "capital_deployment_enabled",
    "data_fetch_enabled",
    "exchange_connection_enabled",
    "live_trading_enabled",
    "broker_control_enabled",
    "paper_order_execution_enabled",
    "live_capital_allocation_enabled",
    "position_sizing_execution_enabled",
    "backtest_enabled",
)

REQUIRED_MEMO_SECTION_IDS = (
    "admissible_frozen_inputs_summary",
    "inadmissible_deferred_inputs_summary",
    "per_strategy_standalone_summary",
    "overlap_correlation_summary",
    "allocation_baseline_comparison",
    "capital_efficiency_ranking",
    "basket_usefulness_classification",
    "risk_warnings_and_limitations",
    "operator_decision_checklist",
    "no_action_recommendation",
)

ALLOWED_CLASSIFICATION_IDS = frozenset((
    "watch_only_useful_candidate",
    "watch_only_basket_candidate",
    "watch_only_redundant_candidate",
    "watch_only_inadmissible",
    "undefined_insufficient_data",
))

REQUIRED_FORBIDDEN_VERDICT_TOKENS = (
    "PASS",
    "ACTIVE",
    "STRONG",
    "approved for paper trading",
    "approved for live trading",
    "profit guarantee",
    "capital deployment instruction",
    "broker/order/credential logic",
)

NON_EMPTY_LIST_SECTIONS = (
    "required_future_artifacts",
    "safety_boundaries",
    "no_profit_claim_policy",
)

DISTINCTION_PHRASES = (
    "Advisory-only",
    "No real results are computed in this bundle.",
    "A capital-efficiency score does not imply future returns.",
    "An advisory allocation is not an execution instruction.",
    "Candidate #10 remains deferred and is not connected by this schema.",
)

# Capability-claim phrases that must never be ASSERTED anywhere. Deliberately
# distinct from the enumerated forbidden_verdict_language tokens (which the
# schema legitimately lists as disallowed verdict labels).
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
    "deploy capital now",
    "connect c10 now",
)


def _load(repo_root: Path):
    p = repo_root / SCHEMA_DIR_REL / SCHEMA_JSON
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
        return False, ["advisory_memo_schema.json is not a JSON object"]

    for k in REQUIRED_TOP_LEVEL_KEYS:
        if k not in data:
            errors.append(f"missing key: {k}")

    for flag in MUST_BE_FALSE_FLAGS:
        if data.get(flag) is not False:
            errors.append(f"safety flag {flag} must be False (got {data.get(flag)!r})")
    for true_flag in ("research_only", "advisory_only", "framework_only"):
        if data.get(true_flag) is not True:
            errors.append(f"{true_flag} must be True")
    if data.get("memo_produced_in_this_bundle") is not False:
        errors.append("memo_produced_in_this_bundle must be False (spec-only)")

    if data.get("lane") != "portfolio_capital_efficiency":
        errors.append(f"lane must be 'portfolio_capital_efficiency' (got {data.get('lane')!r})")
    if data.get("phase") != "P5_advisory_memo_schema":
        errors.append(f"phase must be 'P5_advisory_memo_schema' (got {data.get('phase')!r})")
    if data.get("lane_status_self_declared") != "WATCH":
        errors.append(
            f"lane_status_self_declared must be 'WATCH' (got {data.get('lane_status_self_declared')!r})"
        )

    # Companion documents reference P0 + P1 + P2 + P3 + P4.
    cd = data.get("companion_documents")
    if not isinstance(cd, dict):
        errors.append("companion_documents must be a dict")
    else:
        joined = " ".join(str(v) for v in cd.values())
        for needle in (
            "portfolio_capital_efficiency_protocol_v1",
            "portfolio_capital_efficiency_input_contract_v1",
            "portfolio_capital_efficiency_metric_spec_v1",
            "portfolio_capital_efficiency_allocation_baseline_spec_v1",
            "portfolio_capital_efficiency_overlap_correlation_method_v1",
        ):
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

    # Memo sections.
    sections = data.get("memo_sections")
    if not isinstance(sections, list) or not sections:
        errors.append("memo_sections must be a non-empty list")
        sections = []
    s_by_id = {s.get("id"): s for s in sections if isinstance(s, dict)}
    for sid in REQUIRED_MEMO_SECTION_IDS:
        if sid not in s_by_id:
            errors.append(f"memo_sections missing id: {sid}")
    for s in sections:
        if not isinstance(s, dict):
            continue
        sid = s.get("id")
        if s.get("produced_in_this_bundle") is not False:
            errors.append(f"memo section {sid!r} produced_in_this_bundle must be False (spec-only)")
        if not s.get("purpose"):
            errors.append(f"memo section {sid!r} missing purpose")
        if not isinstance(s.get("required_fields"), list) or not s.get("required_fields"):
            errors.append(f"memo section {sid!r} required_fields must be a non-empty list")

    # Allowed classifications: EXACTLY the five allowed labels.
    ac = data.get("allowed_classifications")
    if not isinstance(ac, list) or not ac:
        errors.append("allowed_classifications must be a non-empty list")
        ac = []
    ac_ids = {c.get("id") for c in ac if isinstance(c, dict)}
    extra = ac_ids - ALLOWED_CLASSIFICATION_IDS
    missing = ALLOWED_CLASSIFICATION_IDS - ac_ids
    if extra:
        errors.append(f"allowed_classifications contains non-allowed labels: {sorted(extra)}")
    if missing:
        errors.append(f"allowed_classifications missing required labels: {sorted(missing)}")
    for cid in ac_ids:
        if not (str(cid).startswith("watch_only_") or cid == "undefined_insufficient_data"):
            errors.append(f"classification {cid!r} must be watch_only_* or undefined_insufficient_data")

    # Forbidden verdict language enumerates the required tokens.
    fvl = data.get("forbidden_verdict_language")
    if not isinstance(fvl, list) or not fvl:
        errors.append("forbidden_verdict_language must be a non-empty list")
    else:
        fvl_set = {str(x) for x in fvl}
        for tok in REQUIRED_FORBIDDEN_VERDICT_TOKENS:
            if tok not in fvl_set:
                errors.append(f"forbidden_verdict_language missing token: {tok!r}")

    # verdict_language_rules + memo_global_rules present + non-empty.
    vlr = data.get("verdict_language_rules")
    if not isinstance(vlr, dict) or not vlr:
        errors.append("verdict_language_rules must be a non-empty dict")
    mgr = data.get("memo_global_rules")
    if not isinstance(mgr, dict) or not mgr:
        errors.append("memo_global_rules must be a non-empty dict")
    elif "no_real_results_in_this_bundle" not in mgr:
        errors.append("memo_global_rules missing key: no_real_results_in_this_bundle")

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
    for needle in ("research-only", "advisory-only", "no broker", "no live", "candidate #10", "no capital deployment"):
        if needle not in sb_join:
            errors.append(f"safety_boundaries missing safety phrase: {needle!r}")

    # Distinction phrases in markdown + capability-claim scan.
    mpath = repo_root / SCHEMA_DIR_REL / SCHEMA_MD
    if mpath.exists():
        md = mpath.read_text(encoding="utf-8")
        for phrase in DISTINCTION_PHRASES:
            if phrase not in md:
                errors.append(f"advisory_memo_schema.md missing distinction phrase: {phrase!r}")
        for phrase in FORBIDDEN_PHRASES:
            if phrase.lower() in md.lower():
                errors.append(f"advisory_memo_schema.md contains forbidden phrase: {phrase!r}")
    else:
        errors.append(f"missing: {mpath.as_posix()}")

    # JSON capability-claim scan (the enumerated forbidden_verdict_language is
    # exempt by construction -- those tokens are not in FORBIDDEN_PHRASES).
    blob = json.dumps(data, ensure_ascii=False).lower()
    for phrase in FORBIDDEN_PHRASES:
        if phrase.lower() in blob:
            errors.append(f"advisory_memo_schema.json contains forbidden phrase: {phrase!r}")

    return (not errors), errors


def show(repo_root: Path = REPO_ROOT) -> int:
    data, err = _load(repo_root)
    if err:
        print(err)
        return 1
    print(f"advisory_memo_schema_id: {data.get('advisory_memo_schema_id')}")
    print(f"title:                {data.get('title')}")
    print(f"version:              {data.get('version')}")
    print(f"phase:                {data.get('phase')}")
    print(f"lane:                 {data.get('lane')}")
    print(f"lane_status:          {data.get('lane_status_self_declared')}")
    print(f"memo_produced:        {data.get('memo_produced_in_this_bundle')}")
    c10b = data.get("c10_boundary") or {}
    print(f"c10 must_not_touch:   {c10b.get('must_not_touch_c10')}")
    print(f"c10 connection:       {c10b.get('connection_status')}")
    print("safety flags (must all be False):")
    for f in MUST_BE_FALSE_FLAGS:
        print(f"  {f}: {data.get(f)}")
    sections = data.get("memo_sections") or []
    print(f"memo_sections ({len(sections)}):")
    for s in sections:
        if isinstance(s, dict):
            print(f"  - {s.get('id')}")
    ac = [c.get("id") for c in data.get("allowed_classifications", []) if isinstance(c, dict)]
    print(f"allowed_classifications ({len(ac)}): {ac}")
    print(f"forbidden_verdict_language: {data.get('forbidden_verdict_language')}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="SPARTA Portfolio Capital-Efficiency Advisory Memo Schema validator (research-only)",
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
