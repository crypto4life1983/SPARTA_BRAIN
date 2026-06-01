"""SPARTA Arbitrage Research Readiness Gate — validator (research-only, stdlib).

Validates `reports/arbitrage_research_readiness_gate_v1/readiness_gate.json`
against the required schema and the hard safety contract:
  * research_only is True
  * seven execution / fetch / connection / backtest / dataset-processing flags
    are False:
      data_fetch_enabled
      exchange_connection_enabled
      live_trading_enabled
      broker_control_enabled
      paper_order_execution_enabled
      backtest_enabled
      dataset_processing_enabled
  * readiness_status is one of PASS / WATCH / BLOCKED / PARKED
  * the six audited artifact paths exist on disk and validate
  * the data-collection / backtest / trading future-authorization gates are
    documented and the trading gate is explicitly forbidden
  * no profitability / live-readiness / backtest-authorize claim

Standard library only. No network. No broker/exchange imports. No subprocess.
No credential / env reads.

CLI:
  python tools/arbitrage_readiness_gate_check.py validate
  python tools/arbitrage_readiness_gate_check.py show
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
GATE_DIR_REL = "reports/arbitrage_research_readiness_gate_v1"
GATE_JSON = "readiness_gate.json"
GATE_MD = "readiness_gate.md"

REQUIRED_TOP_LEVEL_KEYS = (
    "readiness_gate_id",
    "title",
    "version",
    "research_only",
    "data_fetch_enabled",
    "exchange_connection_enabled",
    "live_trading_enabled",
    "broker_control_enabled",
    "paper_order_execution_enabled",
    "backtest_enabled",
    "dataset_processing_enabled",
    "readiness_decision",
    "readiness_status",
    "audited_artifacts",
    "required_artifact_checks",
    "validator_checks",
    "safety_checks",
    "missing_items",
    "blockers",
    "allowed_next_steps",
    "forbidden_next_steps",
    "future_authorization_requirements",
    "data_collection_gate",
    "backtest_gate",
    "trading_gate",
    "pass_watch_fail_rules",
    "lane_recommendation",
    "safety_boundaries",
)

MUST_BE_FALSE_FLAGS = (
    "data_fetch_enabled",
    "exchange_connection_enabled",
    "live_trading_enabled",
    "broker_control_enabled",
    "paper_order_execution_enabled",
    "backtest_enabled",
    "dataset_processing_enabled",
)

ALLOWED_READINESS_STATUSES = {"PASS", "WATCH", "BLOCKED", "PARKED"}

REQUIRED_AUDITED_ARTIFACT_IDS = (
    "arbitrage_research_protocol_v1",
    "arbitrage_data_contract_v1",
    "arbitrage_dataset_manifest_v1",
    "arbitrage_qa_harness_spec_v1",
    "arbitrage_data_source_evaluation_v1",
    "arbitrage_sample_dataset_plan_v1",
)

REQUIRED_ARTIFACT_FIELDS = (
    "artifact_id",
    "path",
    "exists",
    "validation_status",
    "safety_flags_status",
    "role_in_pipeline",
    "remaining_limitations",
)

NON_EMPTY_LIST_SECTIONS = (
    "audited_artifacts",
    "required_artifact_checks",
    "allowed_next_steps",
    "forbidden_next_steps",
    "safety_boundaries",
)

# Distinction phrases that must appear in markdown.
DISTINCTION_PHRASES = (
    "NOT pure arbitrage",
    "RELATIVE_VALUE",
    "WATCH does not imply edge",
    "A price gap is not profit",
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
    p = repo_root / GATE_DIR_REL / GATE_JSON
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
        return False, ["readiness_gate.json is not a JSON object"]

    for k in REQUIRED_TOP_LEVEL_KEYS:
        if k not in data:
            errors.append(f"missing key: {k}")

    for flag in MUST_BE_FALSE_FLAGS:
        if data.get(flag) is not False:
            errors.append(f"safety flag {flag} must be False (got {data.get(flag)!r})")
    if data.get("research_only") is not True:
        errors.append("research_only must be True")

    # readiness_status must be one of the allowed values.
    rs = data.get("readiness_status")
    if rs not in ALLOWED_READINESS_STATUSES:
        errors.append(f"readiness_status must be one of {sorted(ALLOWED_READINESS_STATUSES)} (got {rs!r})")

    # Audited artifacts: all 6 ids present, all fields present, all paths exist on disk.
    artifacts = data.get("audited_artifacts")
    if not isinstance(artifacts, list) or len(artifacts) < 6:
        errors.append("audited_artifacts must be a list with at least 6 entries")
        artifacts = []
    ids_present = {a.get("artifact_id") for a in artifacts if isinstance(a, dict)}
    for aid in REQUIRED_AUDITED_ARTIFACT_IDS:
        if aid not in ids_present:
            errors.append(f"audited_artifacts missing required id: {aid}")
    for art in artifacts:
        if not isinstance(art, dict):
            errors.append("non-dict audited_artifact entry")
            continue
        for f in REQUIRED_ARTIFACT_FIELDS:
            if f not in art:
                errors.append(f"audited_artifact {art.get('artifact_id', '?')!r}: missing field {f}")
        # exists flag must be True AND the path must actually exist on disk.
        if art.get("exists") is not True:
            errors.append(f"audited_artifact {art.get('artifact_id', '?')!r}: exists must be True")
        p = art.get("path")
        if isinstance(p, str) and p:
            full = repo_root / p
            if not full.exists():
                errors.append(f"audited_artifact {art.get('artifact_id', '?')!r}: path does not exist on disk: {p}")
        else:
            errors.append(f"audited_artifact {art.get('artifact_id', '?')!r}: path must be a non-empty string")

    # validator_checks: must claim all_validators_pass True.
    vc = data.get("validator_checks")
    if not isinstance(vc, dict):
        errors.append("validator_checks must be a dict")
    else:
        if vc.get("all_validators_pass") is not True:
            errors.append("validator_checks.all_validators_pass must be True")
        if not isinstance(vc.get("tools_required"), list) or not vc.get("tools_required"):
            errors.append("validator_checks.tools_required must be a non-empty list")

    # safety_checks: must claim no execution / data / sealed touches.
    sc = data.get("safety_checks")
    if not isinstance(sc, dict):
        errors.append("safety_checks must be a dict")
    else:
        for k in ("all_execution_flags_false_across_all_six_arbitrage_docs",
                 "no_forbidden_capability_phrases_in_any_doc",
                 "no_data_files_present_in_any_arbitrage_report_dir",
                 "no_credentials_required_by_any_arbitrage_tool_or_doc",
                 "no_paper_or_live_execution_files_modified_by_any_arbitrage_bundle",
                 "no_jarvis_dashboard_files_modified_by_any_arbitrage_bundle",
                 "no_sealed_artifacts_touched"):
            if sc.get(k) is not True:
                errors.append(f"safety_checks.{k} must be True")

    # missing_items / blockers must be lists (may be empty).
    for k in ("missing_items", "blockers"):
        v = data.get(k)
        if not isinstance(v, list):
            errors.append(f"section {k} must be a list (may be empty)")

    # Future-authorization gates.
    far = data.get("future_authorization_requirements")
    if not isinstance(far, dict):
        errors.append("future_authorization_requirements must be a dict")
    else:
        dcg = far.get("data_collection_gate")
        if isinstance(dcg, dict):
            req = dcg.get("all_required")
            if not isinstance(req, list) or not req:
                errors.append("future_authorization_requirements.data_collection_gate.all_required must be a non-empty list")
            else:
                joined = " ".join(str(x) for x in req).lower()
                for marker in ("explicit_operator_authorization",
                              "exact_source_class_from_bundle_8",
                              "exact_storage_path_named",
                              "no_credentials_unless_separately_authorized",
                              "no_trading_permissions",
                              "separate_data_collection_bundle_approved"):
                    if marker not in joined:
                        errors.append(f"data_collection_gate.all_required missing marker: {marker}")
        else:
            errors.append("future_authorization_requirements.data_collection_gate must be a dict")
        btg = far.get("backtest_gate")
        if isinstance(btg, dict):
            req = btg.get("all_required")
            if not isinstance(req, list) or not req:
                errors.append("future_authorization_requirements.backtest_gate.all_required must be a non-empty list")
            else:
                joined = " ".join(str(x) for x in req).lower()
                for marker in ("data_collection_complete",
                              "per_dataset_manifest_frozen",
                              "qa_report_created",
                              "qa_status",
                              "no_lookahead_check",
                              "no_execution_claims",
                              "separate_backtest_bundle_approved"):
                    if marker not in joined:
                        errors.append(f"backtest_gate.all_required missing marker: {marker}")
        else:
            errors.append("future_authorization_requirements.backtest_gate must be a dict")
        tg = far.get("trading_gate")
        if isinstance(tg, dict):
            if tg.get("explicitly_forbidden_by_this_readiness_gate") is not True:
                errors.append("trading_gate.explicitly_forbidden_by_this_readiness_gate must be True")
        else:
            errors.append("future_authorization_requirements.trading_gate must be a dict")

    # pass_watch_fail_rules: must include PASS / WATCH / BLOCKED / PARKED.
    pwf = data.get("pass_watch_fail_rules")
    if isinstance(pwf, dict):
        for k in ("PASS", "WATCH", "BLOCKED", "PARKED"):
            if k not in pwf:
                errors.append(f"pass_watch_fail_rules missing key: {k}")
    else:
        errors.append("pass_watch_fail_rules must be a dict")

    # lane_recommendation: must forbid ACTIVE / STRONG promotion.
    lr = data.get("lane_recommendation")
    if isinstance(lr, dict):
        if lr.get("do_not_promote_to_ACTIVE") is not True:
            errors.append("lane_recommendation.do_not_promote_to_ACTIVE must be True")
        if lr.get("do_not_promote_to_STRONG_evidence") is not True:
            errors.append("lane_recommendation.do_not_promote_to_STRONG_evidence must be True")
    else:
        errors.append("lane_recommendation must be a dict")

    # Non-empty list sections.
    for k in NON_EMPTY_LIST_SECTIONS:
        v = data.get(k)
        if not isinstance(v, list) or not v:
            errors.append(f"section {k} must be a non-empty list")

    # safety_boundaries: research-only / no broker / no live / no order.
    sb = data.get("safety_boundaries") or []
    sb_join = " ".join(str(x) for x in sb).lower()
    for needle in ("research-only", "no broker", "no live", "no order"):
        if needle not in sb_join:
            errors.append(f"safety_boundaries missing safety phrase: {needle!r}")

    # Distinction phrases in markdown.
    mpath = repo_root / GATE_DIR_REL / GATE_MD
    if mpath.exists():
        md = mpath.read_text(encoding="utf-8")
        for phrase in DISTINCTION_PHRASES:
            if phrase not in md:
                errors.append(f"readiness_gate.md missing distinction phrase: {phrase!r}")
        for phrase in FORBIDDEN_PHRASES:
            if phrase.lower() in md.lower():
                errors.append(f"readiness_gate.md contains forbidden phrase: {phrase!r}")
    else:
        errors.append(f"missing: {mpath.as_posix()}")

    # JSON scan.
    blob = json.dumps(data, ensure_ascii=False).lower()
    for phrase in FORBIDDEN_PHRASES:
        if phrase.lower() in blob:
            errors.append(f"readiness_gate.json contains forbidden phrase: {phrase!r}")

    return (not errors), errors


def show(repo_root: Path = REPO_ROOT) -> int:
    data, err = _load(repo_root)
    if err:
        print(err)
        return 1
    print(f"readiness_gate_id: {data.get('readiness_gate_id')}")
    print(f"title:             {data.get('title')}")
    print(f"version:           {data.get('version')}")
    print(f"research_only:     {data.get('research_only')}")
    print(f"readiness_status:  {data.get('readiness_status')}")
    print("safety flags (must all be False):")
    for f in MUST_BE_FALSE_FLAGS:
        print(f"  {f}: {data.get(f)}")
    arts = data.get("audited_artifacts") or []
    print(f"audited_artifacts ({len(arts)}):")
    for a in arts:
        if isinstance(a, dict):
            print(f"  - {str(a.get('artifact_id', '?')):>40}  exists={a.get('exists')}  status={a.get('validation_status')}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="SPARTA Arbitrage Research Readiness Gate validator (research-only)",
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
