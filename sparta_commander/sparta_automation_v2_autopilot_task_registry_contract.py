"""SPARTA Automation V2 -- Autopilot Task Registry / Allowlist Registration Contract
-- PURE, READ-ONLY, RESEARCH ONLY, DEFINITION-ONLY.

REGISTERS the Automation V2 daily decision report runner
(tools/sparta_automation_v2_daily_report_once.py) as an ALLOWED REPORT-ONLY task in the
overnight / autopilot report-only task registry, so a future overnight run may include it
and Jarvis can wake up with the Automation V2 decision packet already generated -- WITHOUT
crossing any human gate.

What this is (and is NOT):
  * It is an ADDITIVE registry/allowlist record. It declares ONE registered task --
    `automation_v2_daily_report` -- classified REPORT_ONLY / READ_ONLY / NO_NETWORK /
    NO_GIT_WRITE, whose output goes ONLY to the GITIGNORED path
    reports/automation_v2_daily/.
  * It does NOT mutate the frozen crypto_d1 overnight queue allowlist
    (overnight_autopilot_research_queue_contract.ALLOWED_TASK_TYPES is tamper-locked and
    ledger-bound and is left byte-for-byte untouched).
  * It does NOT install or trigger any scheduler, does NOT modify any Windows Task
    Scheduler / cron config, does NOT modify any existing scheduled task, does NOT start
    any background process / daemon, does NOT run the overnight autopilot, and does NOT
    invoke the runner. Enabling the registered task inside the actual overnight runner
    remains a SEPARATE future human gate.

Safety proof: the registration is gated on the daily-report contract proving -- in-memory,
no I/O -- that the registered runner CANNOT fetch data, trade, place orders, commit, push,
advance gates, promote candidates, or use APIs, and that while C22 is at DATA_NOT_READY the
surfaced recommendation is DATASET STAGING only (never labels, never fabricated data).
Every dangerous capability is pinned False with a full scope_locks set.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.sparta_automation_v2_daily_report_contract as _drc
import sparta_commander.sparta_automation_v2_nightly_wrapper_contract as _nw

TR_SCHEMA_VERSION = 1
TR_MODE = "RESEARCH_ONLY"
TR_LANE = "crypto_d1_auto_research"
BUNDLE_NAME = "SPARTA_AUTOMATION_V2_AUTOPILOT_TASK_REGISTRY"

# --- the single registered REPORT-ONLY task --------------------------------
REGISTERED_TASK_ID = "automation_v2_daily_report"
RUNNER_PATH = "tools/sparta_automation_v2_daily_report_once.py"
RUNNER_INVOCATION = "python tools/sparta_automation_v2_daily_report_once.py"
TASK_CLASS = "REPORT_ONLY"
TASK_CLASSIFICATION = ("REPORT_ONLY", "READ_ONLY", "NO_NETWORK", "NO_GIT_WRITE")
ARTIFACT_DIR = _drc.ARTIFACT_DIR                       # reports/automation_v2_daily
ARTIFACT_IS_GITIGNORED = _drc.ARTIFACT_IS_GITIGNORED   # True

# the CLOSED allowlist of task_ids this registry permits in the report-only queue.
REGISTERED_REPORT_ONLY_TASKS = (REGISTERED_TASK_ID,)

REC_DATASET_STAGING = "RECOMMEND_DATASET_STAGING"

VERDICT_REGISTERED = "AUTOMATION_V2_DAILY_REPORT_REGISTERED_AS_REPORT_ONLY_TASK"
VERDICT_BLOCKED = "AUTOMATION_V2_DAILY_REPORT_REGISTRATION_BLOCKED"
# enabling the registered task INSIDE the overnight runner is a separate human gate.
NEXT_REQUIRED_ACTION = (
    "HUMAN_APPROVED_ENABLE_AUTOMATION_V2_REPORT_ONLY_TASK_IN_OVERNIGHT_QUEUE")

_PROOF_TS = "2026-06-20T00:00:00Z"

# field-name tokens that must NEVER appear on a task descriptor offered to the allowlist.
_FORBIDDEN_DESCRIPTOR_TOKENS = (
    "api_key", "credential", "wallet", "account", "order", "login", "secret",
    "password", "broker", "live_authorized", "paper_authorized", "private_key",
)

_CAPABILITY_FLAGS_FALSE = (
    "executes", "invokes_runner", "runs_runner", "runs_autopilot",
    "installs_scheduler", "triggers_scheduler", "modifies_windows_task_scheduler",
    "modifies_cron", "modifies_existing_scheduled_task", "starts_background_process",
    "starts_persistent_daemon", "auto_executes", "schedules_anything",
    "modifies_frozen_overnight_queue_allowlist", "performs_git_io", "performs_network_io",
    "auto_commits", "auto_pushes", "auto_fetches_data", "auto_promotes_candidate",
    "auto_advances_gate", "skips_any_human_gate", "broad_git_add", "fetches_data",
    "stages_dataset", "starts_c22_labels", "builds_replay", "modifies_strategy_rules",
    "reopens_closed_candidate", "starts_c23", "sends_notifications", "sends_email",
    "calls_api", "uses_network", "uses_credentials", "uses_api_keys", "connects_signum",
    "uses_mcp", "accesses_hyperliquid", "connects_broker", "connects_exchange",
    "sends_trades", "edits_bots", "creates_claude_routines", "uses_real_money",
    "places_orders", "contains_order_logic", "paper_trading", "live_trading",
    "deploys_capital", "unlocks_downstream_gate", "crosses_into_forbidden_gate",
)


def registration_safety_proof() -> dict[str, Any]:
    """PURE. Prove -- in-memory, no I/O -- that the registered runner is incapable of any
    dangerous action and that while C22 is DATA_NOT_READY it recommends dataset staging
    only. Builds a clean daily report through the pure daily-report contract (never runs
    the runner)."""
    clean = _drc.build_daily_report(dict(_drc.SAMPLE_REPO_STATE), _PROOF_TS)
    rsf = clean.get("runner_safety") or {}
    guarantee = _nw.verify_morning_output_guarantee(clean)

    proven_incapable_of = {
        "fetch_data": clean.get("fetches_data") is False and rsf.get("no_data_fetch"),
        "trade": clean.get("live_trading") is False and clean.get("paper_trading")
        is False,
        "place_orders": clean.get("places_orders") is False
        and clean.get("contains_order_logic") is False,
        "commit": clean.get("auto_commits") is False and rsf.get("no_git_commit"),
        "push": clean.get("auto_pushes") is False and rsf.get("no_git_push"),
        "advance_gate": clean.get("auto_advances_gate") is False,
        "promote_candidate": clean.get("auto_promotes_candidate") is False,
        "use_api": clean.get("calls_api") is False and clean.get("uses_api_keys")
        is False,
    }
    recommends_dataset_staging_only = (
        clean.get("c22_data_not_ready") is True
        and clean.get("recommended_gate_kind") == REC_DATASET_STAGING
        and clean.get("do_not_proceed_to_labels") is True
        and clean.get("do_not_fabricate_data") is True
        and clean.get("recommends_advancing_to_labels_while_blocked") is False
        and "STAGE_FROZEN_TREND_RADAR_GC_DETECTOR_DATASET"
        in (clean.get("next_human_approval_token") or ""))

    return {
        "daily_report_valid": _drc.validate_daily_report(clean)["valid"],
        "morning_output_guarantee_ok": guarantee["ok"],
        "c22_data_not_ready": clean.get("c22_data_not_ready"),
        "recommended_gate_kind": clean.get("recommended_gate_kind"),
        "next_human_approval_token": clean.get("next_human_approval_token"),
        "recommends_dataset_staging_only": recommends_dataset_staging_only,
        "proven_incapable_of": proven_incapable_of,
        "all_dangerous_capabilities_disproven": all(proven_incapable_of.values()),
        "runner_safety": dict(rsf),
    }


def build_task_registration() -> dict[str, Any]:
    """Assemble the report-only task registration. Pure; no I/O. Gated on the daily-report
    safety proof + the nightly-wrapper readiness spec validating; otherwise BLOCKED."""
    proof = registration_safety_proof()
    wrapper = _nw.build_nightly_wrapper_spec()
    wrapper_valid = _nw.validate_nightly_wrapper_spec(wrapper)["valid"]

    record: dict[str, Any] = {
        "schema_version": TR_SCHEMA_VERSION, "mode": TR_MODE, "lane": TR_LANE,
        "bundle_name": BUNDLE_NAME,
        "section": "automation_v2_autopilot_task_registry",
        "is_definition_only": True, "executes_nothing": True,
        "does_not_invoke_runner": True, "does_not_run_autopilot": True,
        "does_not_modify_frozen_overnight_queue_allowlist": True,
        "label": (
            "SPARTA Automation V2 autopilot task registry (READ-ONLY, RESEARCH ONLY, "
            "DEFINITION ONLY). Registers the daily decision report runner as an ALLOWED "
            "REPORT-ONLY task into the gitignored reports path; does NOT mutate the frozen "
            "crypto_d1 overnight queue allowlist; installs / triggers NO scheduler; "
            "executes nothing. Enabling the task inside the overnight runner is a separate "
            "human gate."),
        # the registered task entry (the allowlist row)
        "registered_report_only_tasks": list(REGISTERED_REPORT_ONLY_TASKS),
        "registered_task": {
            "task_id": REGISTERED_TASK_ID,
            "runner_path": RUNNER_PATH,
            "runner_invocation": RUNNER_INVOCATION,
            "task_class": TASK_CLASS,
            "classification": list(TASK_CLASSIFICATION),
            "output_artifact_dir": ARTIFACT_DIR,
            "output_is_gitignored": ARTIFACT_IS_GITIGNORED,
            "read_only": True, "no_network": True, "no_git_write": True,
            "requires_no_human_gate_crossing": True,
            "does_not_auto_advance_or_promote": True,
            "may_be_queued_as_reporting_only_task": True,
            "enabling_in_overnight_runner_is_a_separate_human_gate": True},
        # eligibility verdict for a future overnight report-only queue
        "autopilot_queue_eligibility": {
            "eligible_for_report_only_queue": True,
            "task_class": "REPORT_ONLY",
            "read_only": True, "no_network": True, "no_git_write": True,
            "requires_no_human_gate_crossing": True,
            "does_not_auto_advance_or_promote": True},
        # scheduler safety (definition only; nothing installed or triggered)
        "scheduler_safety": {
            "installs_scheduler": False, "triggers_scheduler": False,
            "modifies_windows_task_scheduler": False, "modifies_cron": False,
            "modifies_existing_scheduled_task": False,
            "starts_background_process": False, "starts_persistent_daemon": False,
            "auto_executes": False, "is_definition_only": True,
            "invocation_is_manual_or_operator_initiated": True},
        # the in-memory safety proof + the nightly-wrapper readiness validation
        "registration_safety_proof": proof,
        "nightly_wrapper_valid": wrapper_valid,
        "c22_data_not_ready": proof["c22_data_not_ready"],
        "recommends_dataset_staging_only": proof["recommends_dataset_staging_only"],
        "next_human_approval_token": proof["next_human_approval_token"],
        "danger_locks": {
            "live_trading_locked": True, "paper_trading_locked": True,
            "broker_locked": True, "signum_locked": True, "mcp_locked": True,
            "hyperliquid_locked": True, "scheduler_locked": True,
            "bot_edits_locked": True, "trades_locked": True,
            "no_automatic_commit": True, "no_automatic_push": True,
            "no_automatic_data_fetch": True, "never_skips_human_gates": True},
        "next_required_action": NEXT_REQUIRED_ACTION,
        "requires_human_approval": True,
        "verdict": None, "blockers": [],
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_execute": True, "no_invoke_runner": True, "no_run_autopilot": True,
        "no_modify_frozen_overnight_queue_allowlist": True,
        "no_scheduler_install": True, "no_scheduler_trigger": True,
        "no_modify_task_scheduler": True, "no_modify_cron": True,
        "no_modify_existing_scheduled_task": True, "no_background_process": True,
        "no_persistent_daemon": True, "no_auto_execute": True, "no_git_io": True,
        "no_network_io": True, "no_auto_commit": True, "no_auto_push": True,
        "no_auto_fetch": True, "no_auto_promote": True, "no_auto_advance": True,
        "no_broad_git_add": True, "no_data_fetch": True, "no_stage_dataset": True,
        "no_start_labels": True, "no_replay": True, "no_modify_strategy_rules": True,
        "no_start_c23": True, "no_reopen_closed_candidate": True, "no_signum": True,
        "no_mcp": True, "no_hyperliquid": True, "no_api_keys": True,
        "no_credentials": True, "no_bot_edits": True, "no_claude_routines": True,
        "no_send_trades": True, "no_broker": True, "no_order_logic": True,
        "no_paper_trading": True, "no_live_trading": True,
        "no_crossing_into_forbidden_gate": True,
    }

    blockers = record["blockers"]
    if not proof["all_dangerous_capabilities_disproven"]:
        blockers.append("dangerous_capability_not_disproven")
    if not proof["recommends_dataset_staging_only"]:
        blockers.append("c22_not_recommending_dataset_staging_only")
    if proof["daily_report_valid"] is not True:
        blockers.append("daily_report_invalid")
    if proof["morning_output_guarantee_ok"] is not True:
        blockers.append("morning_output_guarantee_failed")
    if wrapper_valid is not True:
        blockers.append("nightly_wrapper_spec_invalid")
    record["verdict"] = VERDICT_BLOCKED if blockers else VERDICT_REGISTERED
    return record


def is_task_allowed_in_report_only_queue(task: Any) -> dict[str, Any]:
    """PURE allowlist gate over ONE candidate task descriptor. A task is allowed ONLY when
    it is the registered Automation V2 daily report runner, classified REPORT_ONLY, with no
    forbidden credential/order/wallet field tokens. Never raises; refuses everything else.
    """
    result: dict[str, Any] = {"allowed": False, "reasons": []}
    reasons = result["reasons"]
    if not isinstance(task, dict):
        reasons.append("task_not_a_dict")
        return result
    for key in task:
        lowered = str(key).lower()
        for token in _FORBIDDEN_DESCRIPTOR_TOKENS:
            if token in lowered:
                reasons.append("forbidden_descriptor_field:" + str(key))
    if task.get("task_id") not in REGISTERED_REPORT_ONLY_TASKS:
        reasons.append("task_id_not_registered:" + str(task.get("task_id")))
    if task.get("task_class") != TASK_CLASS:
        reasons.append("task_class_not_report_only:" + str(task.get("task_class")))
    runner = task.get("runner_path") or task.get("runner")
    if runner not in (None, RUNNER_PATH):
        reasons.append("runner_path_not_registered:" + str(runner))
    result["allowed"] = not reasons
    return result


def validate_task_registration(record: Any) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the registration is research-only,
    definition-only (invokes nothing, runs no autopilot, installs/triggers no scheduler,
    does not mutate the frozen overnight queue allowlist), registers the daily report
    runner REPORT_ONLY / READ_ONLY / NO_NETWORK / NO_GIT_WRITE into the GITIGNORED reports
    path, proves the runner is incapable of every dangerous action and recommends dataset
    staging only while C22 is DATA_NOT_READY, and pins every capability flag False."""
    failures: list = []
    if not isinstance(record, dict):
        return {"valid": False, "failures": ["record_not_a_dict"]}
    r = record

    if r.get("mode") != TR_MODE:
        failures.append("mode_not_research_only")
    if r.get("verdict") not in (VERDICT_REGISTERED, VERDICT_BLOCKED):
        failures.append("bad_verdict")
    if r.get("is_definition_only") is not True:
        failures.append("not_definition_only")
    if r.get("executes_nothing") is not True:
        failures.append("executes_something")
    if r.get("does_not_invoke_runner") is not True:
        failures.append("must_not_invoke_runner")
    if r.get("does_not_run_autopilot") is not True:
        failures.append("must_not_run_autopilot")
    if r.get("does_not_modify_frozen_overnight_queue_allowlist") is not True:
        failures.append("must_not_modify_frozen_overnight_queue_allowlist")

    # the registered task row
    if tuple(r.get("registered_report_only_tasks") or ()) != REGISTERED_REPORT_ONLY_TASKS:
        failures.append("registered_tasks_tampered")
    rt = r.get("registered_task") or {}
    if rt.get("task_id") != REGISTERED_TASK_ID:
        failures.append("registered_task_id_wrong")
    if rt.get("runner_path") != RUNNER_PATH:
        failures.append("registered_runner_path_wrong")
    if rt.get("task_class") != TASK_CLASS:
        failures.append("registered_task_class_not_report_only")
    cls = rt.get("classification") or []
    for c in ("REPORT_ONLY", "READ_ONLY", "NO_NETWORK", "NO_GIT_WRITE"):
        if c not in cls:
            failures.append("classification_missing_%s" % c)
    if rt.get("output_artifact_dir") != ARTIFACT_DIR:
        failures.append("artifact_dir_wrong")
    if not str(rt.get("output_artifact_dir", "")).startswith("reports/"):
        failures.append("artifact_not_under_reports")
    if rt.get("output_is_gitignored") is not True:
        failures.append("output_not_gitignored")
    for k in ("read_only", "no_network", "no_git_write",
              "requires_no_human_gate_crossing", "does_not_auto_advance_or_promote",
              "may_be_queued_as_reporting_only_task",
              "enabling_in_overnight_runner_is_a_separate_human_gate"):
        if rt.get(k) is not True:
            failures.append("registered_task_flag_off_%s" % k)

    # eligibility verdict
    aq = r.get("autopilot_queue_eligibility") or {}
    if aq.get("eligible_for_report_only_queue") is not True:
        failures.append("not_eligible_for_report_only_queue")
    if aq.get("task_class") != "REPORT_ONLY":
        failures.append("eligibility_task_class_not_report_only")
    for k in ("read_only", "no_network", "no_git_write",
              "requires_no_human_gate_crossing", "does_not_auto_advance_or_promote"):
        if aq.get(k) is not True:
            failures.append("eligibility_off_%s" % k)

    # scheduler safety
    sch = r.get("scheduler_safety") or {}
    for k in ("installs_scheduler", "triggers_scheduler",
              "modifies_windows_task_scheduler", "modifies_cron",
              "modifies_existing_scheduled_task", "starts_background_process",
              "starts_persistent_daemon", "auto_executes"):
        if sch.get(k) is not False:
            failures.append("scheduler_safety_violation_%s" % k)
    if sch.get("is_definition_only") is not True:
        failures.append("scheduler_not_definition_only")

    # safety proof: dangerous capabilities disproven + dataset-staging-only
    proof = r.get("registration_safety_proof") or {}
    if proof.get("all_dangerous_capabilities_disproven") is not True:
        failures.append("dangerous_capability_not_disproven")
    pic = proof.get("proven_incapable_of") or {}
    for k in ("fetch_data", "trade", "place_orders", "commit", "push",
              "advance_gate", "promote_candidate", "use_api"):
        if pic.get(k) is not True:
            failures.append("not_proven_incapable_of_%s" % k)
    if proof.get("daily_report_valid") is not True:
        failures.append("daily_report_invalid")
    if proof.get("morning_output_guarantee_ok") is not True:
        failures.append("morning_output_guarantee_failed")
    if r.get("nightly_wrapper_valid") is not True:
        failures.append("nightly_wrapper_invalid")

    # C22 DATA_NOT_READY -> dataset staging only
    if r.get("c22_data_not_ready") is not True:
        failures.append("c22_should_be_data_not_ready")
    if r.get("recommends_dataset_staging_only") is not True:
        failures.append("must_recommend_dataset_staging_only")
    tok = r.get("next_human_approval_token") or ""
    if "STAGE_FROZEN_TREND_RADAR_GC_DETECTOR_DATASET" not in tok:
        failures.append("token_not_dataset_staging")

    # danger locks
    dl = r.get("danger_locks") or {}
    for k in ("live_trading_locked", "paper_trading_locked", "broker_locked",
              "signum_locked", "mcp_locked", "hyperliquid_locked", "scheduler_locked",
              "bot_edits_locked", "trades_locked", "no_automatic_commit",
              "no_automatic_push", "no_automatic_data_fetch", "never_skips_human_gates"):
        if dl.get(k) is not True:
            failures.append("danger_lock_off_%s" % k)

    # verdict consistency with blockers
    blockers = r.get("blockers") or []
    if r.get("verdict") == VERDICT_REGISTERED and blockers:
        failures.append("registered_with_blockers")
    if r.get("verdict") == VERDICT_BLOCKED and not blockers:
        failures.append("blocked_without_blockers")

    locks = r.get("scope_locks") or {}
    for key in ("no_execute", "no_invoke_runner", "no_run_autopilot",
                "no_modify_frozen_overnight_queue_allowlist", "no_scheduler_install",
                "no_scheduler_trigger", "no_modify_task_scheduler", "no_modify_cron",
                "no_modify_existing_scheduled_task", "no_background_process",
                "no_persistent_daemon", "no_auto_execute", "no_git_io", "no_network_io",
                "no_auto_commit", "no_auto_push", "no_auto_fetch", "no_auto_promote",
                "no_auto_advance", "no_broad_git_add", "no_data_fetch", "no_stage_dataset",
                "no_start_labels", "no_replay", "no_modify_strategy_rules", "no_start_c23",
                "no_signum", "no_mcp", "no_hyperliquid", "no_crossing_into_forbidden_gate"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if r.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
