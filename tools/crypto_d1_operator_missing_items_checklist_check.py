"""SPARTA Crypto-D1 Operator Missing Items Checklist -- validator (research-only, stdlib).

Validates `reports/crypto_d1_operator_missing_items_checklist_v1/checklist.json`
against the required schema and the hard safety contract:
  * research_only is True, read_only is True
  * eleven execution / fetch / connection / dataset-processing / scheduler /
    network / credential flags are False
  * overall_readiness_status defaults to NOT_READY_FOR_REAL_DATA
  * exactly 16 checklist items numbered 1..16, each with the 9 required fields
  * every item's status is one of MISSING / COMPLETE / BLOCKED / NOT_APPLICABLE
  * every item's approval_status is one of PENDING / APPROVED / REJECTED / WITHDRAWN
  * anti-fake-completion: status=COMPLETE requires non-empty evidence_path AND
    approval_status=APPROVED
  * status=BLOCKED requires non-empty blocking_reason
  * consistency: if any item is COMPLETE while overall_readiness_status remains
    NOT_READY_FOR_REAL_DATA, overall_readiness_status_override_reason must be
    non-empty
  * required distinction phrases are present in BOTH md and json, no forbidden
    capability phrase in either doc
  * lane_recommendation forbids ACTIVE / STRONG promotion and stays WATCH/MIXED

Standard library only. No network. No broker/exchange imports. No subprocess.
No credential / env reads.

CLI:
  python tools/crypto_d1_operator_missing_items_checklist_check.py validate
  python tools/crypto_d1_operator_missing_items_checklist_check.py show
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CHECKLIST_DIR_REL = "reports/crypto_d1_operator_missing_items_checklist_v1"
CHECKLIST_JSON = "checklist.json"
CHECKLIST_MD = "checklist.md"

REQUIRED_TOP_LEVEL_KEYS = (
    "checklist_id",
    "title",
    "version",
    "kind",
    "read_only",
    "research_only",
    "data_fetch_enabled",
    "exchange_connection_enabled",
    "live_trading_enabled",
    "broker_control_enabled",
    "paper_order_execution_enabled",
    "order_placement_enabled",
    "backtest_execution_enabled",
    "dataset_processing_enabled",
    "scheduler_enabled",
    "network_calls_enabled",
    "credentials_required",
    "lane",
    "target_assets",
    "allowed_market_type",
    "timeframe",
    "session_calendar",
    "companion_documents",
    "research_objective",
    "overall_readiness_status",
    "overall_readiness_status_override_reason",
    "item_status_options",
    "approval_status_options",
    "items",
    "required_artifact_checks",
    "validator_checks",
    "safety_checks",
    "allowed_next_steps",
    "forbidden_next_steps",
    "future_authorization_requirements",
    "lane_recommendation",
    "safety_boundaries",
    "no_profit_claim_policy",
)

MUST_BE_FALSE_FLAGS = (
    "data_fetch_enabled",
    "exchange_connection_enabled",
    "live_trading_enabled",
    "broker_control_enabled",
    "paper_order_execution_enabled",
    "order_placement_enabled",
    "backtest_execution_enabled",
    "dataset_processing_enabled",
    "scheduler_enabled",
    "network_calls_enabled",
    "credentials_required",
)

DEFAULT_OVERALL_READINESS_STATUS = "NOT_READY_FOR_REAL_DATA"

ITEM_STATUS_OPTIONS = ("MISSING", "COMPLETE", "BLOCKED", "NOT_APPLICABLE")
APPROVAL_STATUS_OPTIONS = ("PENDING", "APPROVED", "REJECTED", "WITHDRAWN")

REQUIRED_ITEM_FIELDS = (
    "number",
    "name",
    "status",
    "operator_answer",
    "evidence_path",
    "reviewer_notes",
    "approval_status",
    "blocking_reason",
    "next_action",
)

REQUIRED_ITEM_COUNT = 16

REQUIRED_TARGET_ASSETS = ("BTC", "ETH", "SOL")

NON_EMPTY_LIST_SECTIONS = (
    "items",
    "required_artifact_checks",
    "allowed_next_steps",
    "forbidden_next_steps",
    "safety_boundaries",
    "no_profit_claim_policy",
)

DISTINCTION_PHRASES = (
    "NOT_READY_FOR_REAL_DATA is the honest default",
    "Specification completeness is not data readiness",
    "QA_PASS does not authorize live trading",
    "QA_PASS does not authorize paper trading",
    "QA_PASS does not authorize automatic backtesting",
    "A good historical chart does not imply future returns",
    "No real data has entered SPARTA",
    "Crypto-D1 remains WATCH / MIXED",
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
)


def _load(repo_root: Path):
    p = repo_root / CHECKLIST_DIR_REL / CHECKLIST_JSON
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
        return False, ["checklist.json is not a JSON object"]

    for k in REQUIRED_TOP_LEVEL_KEYS:
        if k not in data:
            errors.append(f"missing key: {k}")

    for flag in MUST_BE_FALSE_FLAGS:
        if data.get(flag) is not False:
            errors.append(f"safety flag {flag} must be False (got {data.get(flag)!r})")
    if data.get("research_only") is not True:
        errors.append("research_only must be True")
    if data.get("read_only") is not True:
        errors.append("read_only must be True")

    if list(data.get("target_assets") or []) != list(REQUIRED_TARGET_ASSETS):
        errors.append(f"target_assets must be {list(REQUIRED_TARGET_ASSETS)}")
    if data.get("allowed_market_type") != "spot":
        errors.append("allowed_market_type must be 'spot'")
    if data.get("timeframe") != "1d":
        errors.append("timeframe must be '1d'")
    if data.get("session_calendar") != "24/7":
        errors.append("session_calendar must be '24/7'")
    if data.get("lane") != "crypto_d1_protocol":
        errors.append("lane must be 'crypto_d1_protocol'")

    if list(data.get("item_status_options") or []) != list(ITEM_STATUS_OPTIONS):
        errors.append(f"item_status_options must equal {list(ITEM_STATUS_OPTIONS)}")
    if list(data.get("approval_status_options") or []) != list(APPROVAL_STATUS_OPTIONS):
        errors.append(f"approval_status_options must equal {list(APPROVAL_STATUS_OPTIONS)}")

    items = data.get("items")
    if not isinstance(items, list) or len(items) != REQUIRED_ITEM_COUNT:
        errors.append(f"items must be a list of exactly {REQUIRED_ITEM_COUNT} entries")
        items = []

    seen_numbers = set()
    any_complete = False
    for it in items:
        if not isinstance(it, dict):
            errors.append("non-dict item entry")
            continue
        for f in REQUIRED_ITEM_FIELDS:
            if f not in it:
                errors.append(f"item missing field {f}: {it!r}")
        n = it.get("number")
        if isinstance(n, int):
            seen_numbers.add(n)
        st = it.get("status")
        if st not in ITEM_STATUS_OPTIONS:
            errors.append(f"item {n!r}: invalid status {st!r}; must be one of {list(ITEM_STATUS_OPTIONS)}")
        appr = it.get("approval_status")
        if appr not in APPROVAL_STATUS_OPTIONS:
            errors.append(f"item {n!r}: invalid approval_status {appr!r}; must be one of {list(APPROVAL_STATUS_OPTIONS)}")
        # Anti-fake-completion rules:
        if st == "COMPLETE":
            any_complete = True
            ev = str(it.get("evidence_path", "") or "").strip()
            if not ev:
                errors.append(f"item {n!r}: status=COMPLETE requires non-empty evidence_path")
            if appr != "APPROVED":
                errors.append(f"item {n!r}: status=COMPLETE requires approval_status=APPROVED (got {appr!r})")
        # BLOCKED requires blocking_reason
        if st == "BLOCKED":
            br = str(it.get("blocking_reason", "") or "").strip()
            if not br:
                errors.append(f"item {n!r}: status=BLOCKED requires non-empty blocking_reason")

    if items and seen_numbers != set(range(1, REQUIRED_ITEM_COUNT + 1)):
        errors.append(f"items must be numbered 1..{REQUIRED_ITEM_COUNT} (got {sorted(seen_numbers)})")

    # overall_readiness_status: default must be NOT_READY_FOR_REAL_DATA
    overall = data.get("overall_readiness_status")
    if overall != DEFAULT_OVERALL_READINESS_STATUS:
        # Allow non-default only if every required item is COMPLETE OR a
        # non-empty override_reason explains why.
        override_reason = str(data.get("overall_readiness_status_override_reason", "") or "").strip()
        all_complete = items and all(
            (i.get("status") == "COMPLETE") for i in items if isinstance(i, dict)
        )
        if not all_complete and not override_reason:
            errors.append(
                f"overall_readiness_status is {overall!r} but not all items are COMPLETE "
                f"and overall_readiness_status_override_reason is empty"
            )

    # Consistency rule: any COMPLETE item while overall remains the default
    # status requires an override_reason explaining why.
    if any_complete and overall == DEFAULT_OVERALL_READINESS_STATUS:
        override_reason = str(data.get("overall_readiness_status_override_reason", "") or "").strip()
        if not override_reason:
            errors.append(
                "at least one item is COMPLETE but overall_readiness_status remains "
                "NOT_READY_FOR_REAL_DATA without overall_readiness_status_override_reason"
            )

    # validator_checks
    vc = data.get("validator_checks")
    if not isinstance(vc, dict):
        errors.append("validator_checks must be a dict")
    else:
        if vc.get("all_validators_pass") is not True:
            errors.append("validator_checks.all_validators_pass must be True")
        if not isinstance(vc.get("tools_required"), list) or not vc.get("tools_required"):
            errors.append("validator_checks.tools_required must be a non-empty list")

    # safety_checks
    sc = data.get("safety_checks")
    if not isinstance(sc, dict):
        errors.append("safety_checks must be a dict")
    else:
        for k in ("all_safety_flags_false_in_this_checklist",
                  "no_forbidden_capability_phrases_in_any_doc",
                  "no_real_data_files_created_by_this_bundle",
                  "no_data_crypto_d1_research_directory_created",
                  "no_qa_run_against_real_data_in_this_bundle",
                  "no_backtest_run_in_this_bundle",
                  "no_credentials_required_by_this_checklist",
                  "no_paper_or_live_execution_files_modified_by_this_bundle",
                  "no_jarvis_dashboard_files_modified_by_this_bundle",
                  "no_source_approved_by_default",
                  "registry_stays_WATCH_never_ACTIVE_never_STRONG"):
            if sc.get(k) is not True:
                errors.append(f"safety_checks.{k} must be True")

    # Future-authorization gates.
    far = data.get("future_authorization_requirements")
    if not isinstance(far, dict):
        errors.append("future_authorization_requirements must be a dict")
    else:
        ccg = far.get("checklist_completion_gate")
        if isinstance(ccg, dict):
            req = ccg.get("all_required")
            if not isinstance(req, list) or not req:
                errors.append("future_authorization_requirements.checklist_completion_gate.all_required must be a non-empty list")
        else:
            errors.append("future_authorization_requirements.checklist_completion_gate must be a dict")
        tg = far.get("trading_gate")
        if isinstance(tg, dict):
            if tg.get("explicitly_forbidden_by_this_checklist") is not True:
                errors.append("trading_gate.explicitly_forbidden_by_this_checklist must be True")
        else:
            errors.append("future_authorization_requirements.trading_gate must be a dict")

    # lane_recommendation: WATCH/MIXED, no ACTIVE/STRONG promotion
    lr = data.get("lane_recommendation")
    if isinstance(lr, dict):
        if lr.get("current_verdict") != "WATCH":
            errors.append("lane_recommendation.current_verdict must be 'WATCH'")
        if lr.get("evidence_level") != "MIXED":
            errors.append("lane_recommendation.evidence_level must be 'MIXED'")
        if lr.get("do_not_promote_to_ACTIVE") is not True:
            errors.append("lane_recommendation.do_not_promote_to_ACTIVE must be True")
        if lr.get("do_not_promote_to_STRONG_evidence") is not True:
            errors.append("lane_recommendation.do_not_promote_to_STRONG_evidence must be True")
    else:
        errors.append("lane_recommendation must be a dict")

    for k in NON_EMPTY_LIST_SECTIONS:
        v = data.get(k)
        if not isinstance(v, list) or not v:
            errors.append(f"section {k} must be a non-empty list")

    sb = data.get("safety_boundaries") or []
    sb_join = " ".join(str(x) for x in sb).lower()
    for needle in ("research-only", "no broker", "no live", "no data fetch"):
        if needle not in sb_join:
            errors.append(f"safety_boundaries missing safety phrase: {needle!r}")

    # Distinction phrases in BOTH md and json blob.
    blob = json.dumps(data, ensure_ascii=False)
    mpath = repo_root / CHECKLIST_DIR_REL / CHECKLIST_MD
    md = mpath.read_text(encoding="utf-8") if mpath.exists() else None
    if md is None:
        errors.append(f"missing: {mpath.as_posix()}")
    for phrase in DISTINCTION_PHRASES:
        if md is not None and phrase not in md:
            errors.append(f"checklist.md missing distinction phrase: {phrase!r}")
        if phrase not in blob:
            errors.append(f"checklist.json missing distinction phrase: {phrase!r}")

    blob_l = blob.lower()
    md_l = md.lower() if md is not None else ""
    for phrase in FORBIDDEN_PHRASES:
        pl = phrase.lower()
        if pl in blob_l:
            errors.append(f"checklist.json contains forbidden phrase: {phrase!r}")
        if md is not None and pl in md_l:
            errors.append(f"checklist.md contains forbidden phrase: {phrase!r}")

    return (not errors), errors


def show(repo_root: Path = REPO_ROOT) -> int:
    data, err = _load(repo_root)
    if err:
        print(err)
        return 1
    print(f"checklist_id:               {data.get('checklist_id')}")
    print(f"title:                      {data.get('title')}")
    print(f"version:                    {data.get('version')}")
    print(f"research_only:              {data.get('research_only')}")
    print(f"overall_readiness_status:   {data.get('overall_readiness_status')}")
    print("safety flags (must all be False):")
    for f in MUST_BE_FALSE_FLAGS:
        print(f"  {f}: {data.get(f)}")
    items = data.get("items") or []
    print(f"items ({len(items)}):")
    counts = {s: 0 for s in ITEM_STATUS_OPTIONS}
    for it in items:
        if isinstance(it, dict):
            st = it.get("status", "?")
            counts[st] = counts.get(st, 0) + 1
            print(f"  #{it.get('number'):>2} [{st:<14}] {it.get('name')}")
    print("status counts:")
    for s, c in counts.items():
        print(f"  {s:<14}: {c}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="SPARTA Crypto-D1 Operator Missing Items Checklist validator (research-only)",
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
