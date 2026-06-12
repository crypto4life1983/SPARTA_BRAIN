"""SPARTA OVERNIGHT AUTOPILOT RESEARCH QUEUE CONTRACT (READ-ONLY,
RESEARCH ONLY, QUEUE RULES + RUN-RECORD SCHEMA).

Turns the overnight research planner from planner-only into a SCHEDULED
research queue controller -- without breaking a single lane law:

SCHEDULING MODEL (frozen): the schedule lives in WINDOWS TASK SCHEDULER and
is installed MANUALLY by the human (matching the repo's existing
install_*.ps1 precedent). The Python runner is ONE-SHOT: it processes the
queue once and exits -- no daemon, no while-loop, no sleep, no in-process
scheduler library, ever.

TASK MODEL (frozen): the queue may execute ONLY safe offline/local tasks
that create NO new research evidence -- integrity audits, contract
certification sweeps, safety-test reports, and ADVISORY-ONLY seed research
brief drafts synthesized from already-frozen evidence. Detection runs,
replays, staging, fetching, edits, commits, pushes, promotions: all of
these remain behind their explicit HUMAN_APPROVED gates and may only be
QUEUED AS PROPOSALS for the human, never executed by the autopilot.

Every morning the autopilot must answer honestly: what ran, what artifacts
were produced, and what next HUMAN gate is required. Claims made: none,
ever. The two-candidate ledger is preserved verbatim and the autopilot can
never revive either corpse.
"""

from __future__ import annotations

from typing import Any

from sparta_commander.crypto_intraday_breakout_pullback_structure_v2_result_and_rejection_record_contract import (
    REJECTION_REASON as C2_REASON,
    REJECTION_STATUS as C2_STATUS,
)
from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
    REJECTION_REASON as C1_REASON,
    REJECTION_STATUS as C1_STATUS,
)

OA_SCHEMA_VERSION = "overnight_autopilot_research_queue_contract.v1"
OA_LABEL = ("SPARTA Overnight Autopilot Research Queue Contract "
            "(READ-ONLY, RESEARCH ONLY, ONE-SHOT RUNS, HUMAN-INSTALLED "
            "SCHEDULE)")
OA_MODE = "RESEARCH_ONLY"
VERDICT_OA_READY = "OVERNIGHT_AUTOPILOT_QUEUE_CONTRACT_READY"
VERDICT_OA_BLOCKED = "OVERNIGHT_AUTOPILOT_QUEUE_CONTRACT_BLOCKED"
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_OVERNIGHT_AUTOPILOT_FIRST_RUN_ONCE"

QUEUE_PATH = "data/overnight_autopilot/queue.json"
REPORTS_DIR = "data/overnight_autopilot/reports"

SCHEDULING_MODEL = (
    "the schedule is a WINDOWS TASK SCHEDULER task installed MANUALLY by "
    "the human via a reviewed install script; the python runner is "
    "one-shot per invocation -- it processes the queue once, writes its "
    "morning report, and exits; no daemon, no while-loop, no sleep, no "
    "in-process scheduler library")

# CLOSED set: the ONLY task types the autopilot may execute.
ALLOWED_TASK_TYPES = (
    "integrity_audit",              # re-hash all protected evidence
    "contract_certification_sweep",  # rebuild live review verdicts
    "safety_test_suite_report",     # run the pytest safety suite, report
    "seed_research_brief_draft",    # ADVISORY-ONLY synthesis from frozen
                                    # evidence; drafts a NEW-family brief
)

TASK_TYPE_DEFINITIONS = {
    "integrity_audit": ("re-verify byte-identity of every protected "
                        "evidence file (baselines, manifests, labels, "
                        "replay artifacts); report INTACT or name the "
                        "violation"),
    "contract_certification_sweep": ("rebuild the live verdicts of the "
                                     "pushed review contracts and confirm "
                                     "every one still certifies unchanged"),
    "safety_test_suite_report": ("run the repository safety test suite "
                                 "and report pass/fail counts"),
    "seed_research_brief_draft": ("draft an advisory-only research brief "
                                  "for a NEW candidate family from the "
                                  "frozen seeds; the brief proposes, the "
                                  "human decides; never a rescue of a "
                                  "rejected candidate"),
}

# CLOSED set of things the queue must REFUSE to execute. These may appear
# in the queue only as status=proposal_for_human entries.
FORBIDDEN_TASK_TYPES = (
    "detection_run", "redetection_run", "replay_run", "staging_run",
    "data_fetch_run", "candle_download", "mutable_edit_application",
    "strategy_spec_build", "commit_or_push", "mission_flow_registration",
    "scorer_run", "optimizer_run", "paper_trading", "live_trading",
    "promotion", "gate_unlock", "evidence_deletion",
)

ALLOWED_TASK_STATUSES = ("queued", "done", "skipped_forbidden",
                         "proposal_for_human")

RUN_RECORD_REQUIRED_FIELDS = (
    "run_id", "started_utc", "finished_utc", "tasks_executed",
    "tasks_skipped", "proposals_surfaced_for_human", "artifacts_produced",
    "integrity_status", "claims_made", "no_commit_no_push",
    "next_human_gate",
)

PRESERVED_LEDGER = {
    "candidate_1": {
        "candidate_id": "NY_SESSION_FVG_CHOCH_STRATEGY_CANDIDATE_V1",
        "status": "REJECTED_KEPT_ON_RECORD",
        "reason": "COST_NON_VIABLE_RISK_GEOMETRY"},
    "candidate_2": {
        "candidate_id": "CRYPTO_INTRADAY_BREAKOUT_PULLBACK_STRUCTURE_V1",
        "status": "REJECTED_KEPT_ON_RECORD",
        "reason": "EDGE_FAILURE_SURVIVED_ONE_AUTHORIZED_FILTER_EXPERIMENT"},
    "seeds_for_new_families_only": (
        "btc_was_net_positive_in_all_variants_small_sample",
        "sol_was_net_positive_at_3r_and_4r",
        "long_side_was_materially_stronger_than_shorts"),
    "seeds_are_never_rescue_paths": True,
}

FORBIDDEN = (
    "wallet_account_order_trading_live_capability",
    "api_keys_or_broker_credentials",
    "automatic_paper_or_live_promotion",
    "automatic_commit_or_push",
    "deleting_or_hiding_failed_evidence",
    "executing_human_gated_research_tasks",
    "in_process_daemons_loops_or_sleep_scheduling",
    "reviving_rejected_candidates",
    "profitability_claims",
    "gate_unlocks",
)

_FORBIDDEN_KEY_TOKENS = ("api_key", "credential", "wallet", "account",
                         "order", "login", "secret", "password", "broker",
                         "live_authorized", "paper_authorized")


def get_overnight_autopilot_contract_label() -> str:
    return OA_LABEL


def validate_queue_task(task: Any) -> dict[str, Any]:
    """Pure gate over ONE queue entry. Forbidden task types may exist in
    the queue ONLY as proposal_for_human; the runner must never execute
    them. Never raises."""
    result: dict[str, Any] = {"executable": False, "errors": [],
                              "is_human_proposal": False}
    if not isinstance(task, dict):
        result["errors"].append("task_not_a_dict")
        return result
    errors = result["errors"]
    for key in task:
        lowered = str(key).lower()
        for token in _FORBIDDEN_KEY_TOKENS:
            if token in lowered:
                errors.append("forbidden_task_field:" + str(key))
    params = task.get("params")
    if isinstance(params, dict):
        for key in params:
            lowered = str(key).lower()
            for token in _FORBIDDEN_KEY_TOKENS:
                if token in lowered:
                    errors.append("forbidden_param_field:" + str(key))
    if not task.get("task_id"):
        errors.append("task_id_required")
    status = task.get("status")
    if status not in ALLOWED_TASK_STATUSES:
        errors.append("status_outside_closed_set:" + str(status))
    task_type = task.get("task_type")
    if task_type in FORBIDDEN_TASK_TYPES:
        if status == "proposal_for_human":
            result["is_human_proposal"] = not errors
            return result  # valid as a proposal; NEVER executable
        errors.append("forbidden_task_type_can_only_be_a_proposal:"
                      + str(task_type))
        return result
    if task_type not in ALLOWED_TASK_TYPES:
        errors.append("task_type_outside_closed_set:" + str(task_type))
        return result
    result["executable"] = not errors and status == "queued"
    return result


def validate_run_record(record: Any) -> dict[str, Any]:
    """Pure gate over one morning run report. Never raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"acceptable": False, "errors": ["record_not_a_dict"]}
    for field in RUN_RECORD_REQUIRED_FIELDS:
        if field not in record:
            errors.append("missing_run_field:" + field)
    if errors:
        return {"acceptable": False, "errors": errors}
    if record.get("claims_made") != "none":
        errors.append("claims_must_be_none")
    if record.get("no_commit_no_push") is not True:
        errors.append("run_must_not_commit_or_push")
    if not str(record.get("next_human_gate") or "").strip():
        errors.append("next_human_gate_required")
    for task in record.get("tasks_executed") or []:
        if isinstance(task, dict) and task.get("task_type") in (
                FORBIDDEN_TASK_TYPES):
            errors.append("executed_a_forbidden_task:"
                          + str(task.get("task_type")))
    return {"acceptable": not errors, "errors": errors}


def build_overnight_autopilot_contract() -> dict[str, Any]:
    """Assemble the contract, gated on BOTH rejection records being intact
    (the autopilot can never exist in a world where the ledger broke)."""
    record: dict[str, Any] = {
        "schema_version": OA_SCHEMA_VERSION, "label": OA_LABEL,
        "mode": OA_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [],
        "scheduling_model": SCHEDULING_MODEL,
        "queue_path": QUEUE_PATH, "reports_dir": REPORTS_DIR,
        "allowed_task_types": list(ALLOWED_TASK_TYPES),
        "task_type_definitions": dict(TASK_TYPE_DEFINITIONS),
        "forbidden_task_types": list(FORBIDDEN_TASK_TYPES),
        "allowed_task_statuses": list(ALLOWED_TASK_STATUSES),
        "run_record_required_fields": list(RUN_RECORD_REQUIRED_FIELDS),
        "preserved_ledger": {
            "candidate_1": dict(PRESERVED_LEDGER["candidate_1"]),
            "candidate_2": dict(PRESERVED_LEDGER["candidate_2"]),
            "seeds_for_new_families_only": list(
                PRESERVED_LEDGER["seeds_for_new_families_only"]),
            "seeds_are_never_rescue_paths": True},
        "forbidden": list(FORBIDDEN),
        "task_install_is_manual_human_action": True,
        "runner_is_one_shot_no_daemon": True,
        "human_gated_tasks_can_only_be_proposals": True,
        "every_candidate_still_requires_evidence_freeze_and_human_gates":
            True,
        "modifies_mission_flow": False, "modifies_pm_lane": False,
        "human_review_required": True,
        "executes": False, "writes_files": False, "writes_reports": False,
        "modifies_labels": False, "deletes_labels": False,
        "modifies_staged_files": False,
        "runs_detector_now": False, "runs_replay_now": False,
        "scores_now": False, "fetches_data": False, "calls_api": False,
        "uses_network": False, "uses_credentials": False, "uses_wallet": False,
        "connects_broker": False, "connects_exchange": False,
        "uses_real_money": False, "contains_order_logic": False,
        "starts_scheduler": False, "sends_notifications": False,
        "authorizes_paper_execution": False, "authorizes_micro_live": False,
        "authorizes_live_trading": False, "promotes_gate": False,
        "unlocks_downstream_gate": False,
        "paper_trading_gate_locked": True, "micro_live_gate_locked": True,
        "live_gate_locked": True,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    if C1_STATUS != "REJECTED_KEPT_ON_RECORD" \
            or C1_REASON != "COST_NON_VIABLE_RISK_GEOMETRY":
        record["verdict"] = VERDICT_OA_BLOCKED
        record["blockers"].append("candidate_1_ledger_broken")
        return record
    if C2_STATUS != "REJECTED_KEPT_ON_RECORD" or C2_REASON != (
            "EDGE_FAILURE_SURVIVED_ONE_AUTHORIZED_FILTER_EXPERIMENT"):
        record["verdict"] = VERDICT_OA_BLOCKED
        record["blockers"].append("candidate_2_ledger_broken")
        return record
    record["verdict"] = VERDICT_OA_READY
    return record


def validate_overnight_autopilot_contract(record: Any) -> dict[str, Any]:
    """Validate the contract's shape and safety invariants. Never raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_OA_READY, VERDICT_OA_BLOCKED):
        errors.append("bad_verdict")
    if r.get("scheduling_model") != SCHEDULING_MODEL:
        errors.append("scheduling_model_tampered")
    if tuple(r.get("allowed_task_types") or ()) != ALLOWED_TASK_TYPES:
        errors.append("allowed_tasks_tampered")
    if tuple(r.get("forbidden_task_types") or ()) != FORBIDDEN_TASK_TYPES:
        errors.append("forbidden_tasks_weakened")
    if tuple(r.get("run_record_required_fields") or ()) != (
            RUN_RECORD_REQUIRED_FIELDS):
        errors.append("run_record_schema_tampered")
    ledger = r.get("preserved_ledger") or {}
    if (ledger.get("candidate_1") != PRESERVED_LEDGER["candidate_1"]
            or ledger.get("candidate_2") != PRESERVED_LEDGER["candidate_2"]
            or tuple(ledger.get("seeds_for_new_families_only") or ())
            != PRESERVED_LEDGER["seeds_for_new_families_only"]
            or ledger.get("seeds_are_never_rescue_paths") is not True):
        errors.append("preserved_ledger_tampered")
    if tuple(r.get("forbidden") or ()) != FORBIDDEN:
        errors.append("forbidden_list_weakened")
    for key, want in (
        ("task_install_is_manual_human_action", True),
        ("runner_is_one_shot_no_daemon", True),
        ("human_gated_tasks_can_only_be_proposals", True),
        ("every_candidate_still_requires_evidence_freeze_and_human_gates",
         True),
        ("modifies_mission_flow", False), ("modifies_pm_lane", False),
        ("human_review_required", True),
        ("paper_trading_gate_locked", True),
        ("micro_live_gate_locked", True), ("live_gate_locked", True),
    ):
        if r.get(key) is not want:
            errors.append("constitution_flag_wrong:" + key)
    for key in ("executes", "writes_files", "writes_reports",
                "modifies_labels", "deletes_labels", "modifies_staged_files",
                "runs_detector_now", "runs_replay_now", "scores_now",
                "fetches_data", "calls_api", "uses_network",
                "uses_credentials", "uses_wallet", "connects_broker",
                "connects_exchange", "uses_real_money",
                "contains_order_logic", "starts_scheduler",
                "sends_notifications", "authorizes_paper_execution",
                "authorizes_micro_live", "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate"):
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)
    return {"valid": not errors, "errors": errors}
