"""SPARTA Crypto-D1 Readiness Gate — validator (research-only, stdlib).

Validates `reports/crypto_d1_readiness_gate_v1/readiness_gate.json` against the
required schema and the hard safety contract:
  * research_only is True, read_only is True
  * eleven execution / fetch / connection / dataset-processing / scheduler /
    network / credential flags are False
  * readiness_status is one of the 5 allowed lifecycle statuses and defaults to
    NOT_READY_FOR_REAL_DATA
  * all 10 audited Bundle 11-20 artifact paths exist on disk
  * all 20 readiness questions are present
  * the missing-items list is present and non-empty
  * the future-authorization gates are documented and the trading gate is
    explicitly forbidden
  * the lane recommendation forbids ACTIVE / STRONG promotion
  * required distinction phrases are present and no forbidden capability phrase
    appears in either document

Standard library only. No network. No broker/exchange imports. No subprocess.
No credential / env reads.

CLI:
  python tools/crypto_d1_readiness_gate_check.py validate
  python tools/crypto_d1_readiness_gate_check.py show
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
GATE_DIR_REL = "reports/crypto_d1_readiness_gate_v1"
GATE_JSON = "readiness_gate.json"
GATE_MD = "readiness_gate.md"

REQUIRED_TOP_LEVEL_KEYS = (
    "readiness_gate_id",
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
    "readiness_status",
    "readiness_decision",
    "audited_artifacts",
    "readiness_questions",
    "required_artifact_checks",
    "validator_checks",
    "safety_checks",
    "missing_items",
    "blockers",
    "allowed_next_steps",
    "forbidden_next_steps",
    "readiness_status_options",
    "readiness_status_rules",
    "future_authorization_requirements",
    "data_intake_gate",
    "qa_run_gate",
    "backtest_gate",
    "trading_gate",
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

ALLOWED_READINESS_STATUSES = (
    "NOT_READY_FOR_REAL_DATA",
    "READY_FOR_OPERATOR_DATA_INTAKE",
    "READY_FOR_QA_RUN",
    "READY_FOR_BASELINE_BACKTEST_REVIEW",
    "BLOCKED",
)

DEFAULT_READINESS_STATUS = "NOT_READY_FOR_REAL_DATA"

REQUIRED_AUDITED_ARTIFACT_IDS = (
    "crypto_d1_protocol_v1",
    "crypto_d1_data_contract_v1",
    "crypto_d1_dataset_manifest_v1",
    "crypto_d1_qa_freeze_spec_v1",
    "crypto_d1_baseline_backtest_plan_v1",
    "crypto_d1_backtest_runner_v1",
    "crypto_d1_data_acquisition_authorization_v1",
    "crypto_d1_data_source_evaluation_v1",
    "crypto_d1_data_qa_runtime_tool_v1",
    "crypto_d1_manual_dataset_intake_runbook_v1",
)

REQUIRED_ARTIFACT_FIELDS = (
    "artifact_id",
    "bundle",
    "path",
    "exists",
    "validator_command",
    "validation_status",
    "role_in_pipeline",
    "remaining_limitations",
)

REQUIRED_TARGET_ASSETS = ("BTC", "ETH", "SOL")

REQUIRED_QUESTION_COUNT = 20

NON_EMPTY_LIST_SECTIONS = (
    "audited_artifacts",
    "readiness_questions",
    "required_artifact_checks",
    "missing_items",
    "allowed_next_steps",
    "forbidden_next_steps",
    "safety_boundaries",
    "no_profit_claim_policy",
)

# Phrases that must appear verbatim in BOTH documents for word discipline.
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

# Forbidden capability claims (case-insensitive scan of both docs).
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
    if data.get("read_only") is not True:
        errors.append("read_only must be True")

    # readiness_status must be allowed and default to NOT_READY_FOR_REAL_DATA.
    rs = data.get("readiness_status")
    if rs not in ALLOWED_READINESS_STATUSES:
        errors.append(f"readiness_status must be one of {list(ALLOWED_READINESS_STATUSES)} (got {rs!r})")
    if rs != DEFAULT_READINESS_STATUS:
        errors.append(f"readiness_status must default to {DEFAULT_READINESS_STATUS!r} (got {rs!r})")

    # readiness_status_options must list exactly the 5 allowed statuses.
    opts = data.get("readiness_status_options")
    if not isinstance(opts, list) or list(opts) != list(ALLOWED_READINESS_STATUSES):
        errors.append(f"readiness_status_options must equal {list(ALLOWED_READINESS_STATUSES)}")

    # readiness_status_rules must define each of the 5 statuses.
    rules = data.get("readiness_status_rules")
    if isinstance(rules, dict):
        for s in ALLOWED_READINESS_STATUSES:
            if s not in rules:
                errors.append(f"readiness_status_rules missing status: {s}")
    else:
        errors.append("readiness_status_rules must be a dict")

    # Scope.
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

    # Audited artifacts: all 10 ids present, all fields present, all paths exist.
    artifacts = data.get("audited_artifacts")
    if not isinstance(artifacts, list) or len(artifacts) < 10:
        errors.append("audited_artifacts must be a list with at least 10 entries")
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
        if art.get("exists") is not True:
            errors.append(f"audited_artifact {art.get('artifact_id', '?')!r}: exists must be True")
        p = art.get("path")
        if isinstance(p, str) and p:
            if not (repo_root / p).exists():
                errors.append(f"audited_artifact {art.get('artifact_id', '?')!r}: path does not exist on disk: {p}")
        else:
            errors.append(f"audited_artifact {art.get('artifact_id', '?')!r}: path must be a non-empty string")

    # Readiness questions: exactly 20, numbered 1..20, each with answer.
    questions = data.get("readiness_questions")
    if not isinstance(questions, list) or len(questions) != REQUIRED_QUESTION_COUNT:
        errors.append(f"readiness_questions must be a list of exactly {REQUIRED_QUESTION_COUNT} entries")
        questions = []
    seen_numbers = set()
    for q in questions:
        if not isinstance(q, dict):
            errors.append("non-dict readiness_question entry")
            continue
        for f in ("number", "question", "answer"):
            if f not in q:
                errors.append(f"readiness_question missing field {f}: {q!r}")
        n = q.get("number")
        if isinstance(n, int):
            seen_numbers.add(n)
    if questions and seen_numbers != set(range(1, REQUIRED_QUESTION_COUNT + 1)):
        errors.append(f"readiness_questions must be numbered 1..{REQUIRED_QUESTION_COUNT} (got {sorted(seen_numbers)})")
    # Q20 must report the default status.
    for q in questions:
        if isinstance(q, dict) and q.get("number") == 20:
            if q.get("answer") != DEFAULT_READINESS_STATUS:
                errors.append(f"readiness_question 20 answer must be {DEFAULT_READINESS_STATUS!r}")

    # validator_checks.
    vc = data.get("validator_checks")
    if not isinstance(vc, dict):
        errors.append("validator_checks must be a dict")
    else:
        if vc.get("all_validators_pass") is not True:
            errors.append("validator_checks.all_validators_pass must be True")
        if not isinstance(vc.get("tools_required"), list) or not vc.get("tools_required"):
            errors.append("validator_checks.tools_required must be a non-empty list")

    # safety_checks: all must be True.
    sc = data.get("safety_checks")
    if not isinstance(sc, dict):
        errors.append("safety_checks must be a dict")
    else:
        for k in ("all_safety_flags_false_in_this_gate",
                  "no_forbidden_capability_phrases_in_any_doc",
                  "no_real_data_files_created_by_this_bundle",
                  "no_data_crypto_d1_research_directory_created",
                  "no_qa_run_against_real_data_in_this_bundle",
                  "no_backtest_run_in_this_bundle",
                  "no_credentials_required_by_this_gate",
                  "no_paper_or_live_execution_files_modified_by_this_bundle",
                  "no_jarvis_dashboard_files_modified_by_this_bundle",
                  "registry_stays_WATCH_never_ACTIVE_never_STRONG"):
            if sc.get(k) is not True:
                errors.append(f"safety_checks.{k} must be True")

    # missing_items must be a non-empty list (the substance of NOT_READY).
    mi = data.get("missing_items")
    if not isinstance(mi, list) or not mi:
        errors.append("missing_items must be a non-empty list while status is NOT_READY_FOR_REAL_DATA")

    # blockers must be a list (may be empty).
    if not isinstance(data.get("blockers"), list):
        errors.append("blockers must be a list (may be empty)")

    # Future-authorization gates.
    far = data.get("future_authorization_requirements")
    if not isinstance(far, dict):
        errors.append("future_authorization_requirements must be a dict")
    else:
        for gate_name in ("data_intake_gate", "qa_run_gate", "backtest_gate"):
            g = far.get(gate_name)
            if isinstance(g, dict):
                req = g.get("all_required")
                if not isinstance(req, list) or not req:
                    errors.append(f"future_authorization_requirements.{gate_name}.all_required must be a non-empty list")
            else:
                errors.append(f"future_authorization_requirements.{gate_name} must be a dict")
        tg = far.get("trading_gate")
        if isinstance(tg, dict):
            if tg.get("explicitly_forbidden_by_this_readiness_gate") is not True:
                errors.append("trading_gate.explicitly_forbidden_by_this_readiness_gate must be True")
        else:
            errors.append("future_authorization_requirements.trading_gate must be a dict")

    # lane_recommendation: must forbid ACTIVE / STRONG promotion + stay WATCH/MIXED.
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

    # Non-empty list sections.
    for k in NON_EMPTY_LIST_SECTIONS:
        v = data.get(k)
        if not isinstance(v, list) or not v:
            errors.append(f"section {k} must be a non-empty list")

    # safety_boundaries phrases.
    sb = data.get("safety_boundaries") or []
    sb_join = " ".join(str(x) for x in sb).lower()
    for needle in ("research-only", "no broker", "no live", "no data fetch"):
        if needle not in sb_join:
            errors.append(f"safety_boundaries missing safety phrase: {needle!r}")

    # Distinction phrases must appear in BOTH the markdown and the JSON blob.
    blob = json.dumps(data, ensure_ascii=False)
    mpath = repo_root / GATE_DIR_REL / GATE_MD
    md = mpath.read_text(encoding="utf-8") if mpath.exists() else None
    if md is None:
        errors.append(f"missing: {mpath.as_posix()}")
    for phrase in DISTINCTION_PHRASES:
        if md is not None and phrase not in md:
            errors.append(f"readiness_gate.md missing distinction phrase: {phrase!r}")
        if phrase not in blob:
            errors.append(f"readiness_gate.json missing distinction phrase: {phrase!r}")

    # Forbidden phrases must not appear in either doc.
    blob_l = blob.lower()
    md_l = md.lower() if md is not None else ""
    for phrase in FORBIDDEN_PHRASES:
        pl = phrase.lower()
        if pl in blob_l:
            errors.append(f"readiness_gate.json contains forbidden phrase: {phrase!r}")
        if md is not None and pl in md_l:
            errors.append(f"readiness_gate.md contains forbidden phrase: {phrase!r}")

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
            print(f"  - B{a.get('bundle'):>2} {str(a.get('artifact_id', '?')):<46} exists={a.get('exists')} status={a.get('validation_status')}")
    mi = data.get("missing_items") or []
    print(f"missing_items ({len(mi)}):")
    for m in mi:
        print(f"  - {m}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="SPARTA Crypto-D1 Readiness Gate validator (research-only)",
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
