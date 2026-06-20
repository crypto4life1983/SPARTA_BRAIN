"""SPARTA Automation V2 -- Report-Only Queue Adapter Contract
-- PURE, READ-ONLY, RESEARCH ONLY, DEFINITION-ONLY.

WIRES the already-registered Automation V2 daily report task
(automation_v2_daily_report -> tools/sparta_automation_v2_daily_report_once.py) into an
ACTUAL, consultable overnight/autopilot REPORT-ONLY queue, additively.

Why an adapter (not a queue mutation): the legacy crypto_d1 overnight queue
(overnight_autopilot_research_queue_contract.ALLOWED_TASK_TYPES) is FROZEN and
tamper-locked and ledger-bound; modifying it would break its anti-tamper validator. So this
adapter is a SEPARATE, additive report-only queue: it assembles the concrete queue a future
overnight run would iterate, gates every entry through the live registry allowlist
(sparta_automation_v2_autopilot_task_registry_contract.is_task_allowed_in_report_only_queue),
and proves the legacy frozen allowlist is left byte-for-byte untouched.

It executes NOTHING. It does NOT run the runner, does NOT run the overnight autopilot, does
NOT install or trigger any scheduler, does NOT modify any Windows Task Scheduler / cron /
background process, performs NO git or network I/O, fetches NO data, stages NO dataset,
starts NO C22 labels / replay, promotes / advances NO candidate. `resolve_dispatch` only
DEFINES how a future human-or-scheduled trigger would invoke the runner; it runs nothing.
While C22 is at DATA_NOT_READY the surfaced recommendation is DATASET STAGING only. Every
dangerous capability is pinned False with a full scope_locks set.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.overnight_autopilot_research_queue_contract as _legacy
import sparta_commander.sparta_automation_v2_autopilot_task_registry_contract as _tr

QA_SCHEMA_VERSION = 1
QA_MODE = "RESEARCH_ONLY"
QA_LANE = "crypto_d1_auto_research"
BUNDLE_NAME = "SPARTA_AUTOMATION_V2_REPORT_ONLY_QUEUE_ADAPTER"

ARTIFACT_DIR = _tr.ARTIFACT_DIR                       # reports/automation_v2_daily
ARTIFACT_IS_GITIGNORED = _tr.ARTIFACT_IS_GITIGNORED   # True
ARTIFACT_MARKDOWN_BASENAME = "automation_v2_daily_report"

VERDICT_QUEUE_READY = "V2_REPORT_ONLY_QUEUE_READY"
VERDICT_QUEUE_BLOCKED = "V2_REPORT_ONLY_QUEUE_BLOCKED"
# the trigger that would actually run an overnight report-only pass is a separate human or
# manually-installed-scheduled action -- this adapter triggers nothing.
NEXT_REQUIRED_ACTION = (
    "HUMAN_OR_MANUALLY_INSTALLED_SCHEDULED_TRIGGER_OF_REPORT_ONLY_PASS")

# the legacy frozen allowlist snapshot this adapter must leave untouched.
_LEGACY_FROZEN_ALLOWLIST = (
    "integrity_audit", "contract_certification_sweep",
    "safety_test_suite_report", "seed_research_brief_draft")

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


def _legacy_allowlist_preserved() -> dict[str, Any]:
    """PURE. Prove the legacy frozen overnight queue allowlist is unchanged and that the V2
    task is NOT smuggled into it."""
    current = tuple(_legacy.ALLOWED_TASK_TYPES)
    contract = _legacy.build_overnight_autopilot_contract()
    return {
        "frozen_allowlist": list(current),
        "unchanged": current == _LEGACY_FROZEN_ALLOWLIST,
        "v2_task_not_in_legacy_allowlist":
            _tr.REGISTERED_TASK_ID not in current,
        "legacy_contract_self_certifies":
            _legacy.validate_overnight_autopilot_contract(contract)["valid"] is True,
    }


def _queue_entry() -> dict[str, Any]:
    """PURE. The single report-only queue entry for the registered V2 daily report task,
    each field sourced from the live registry contract + gated through its allowlist."""
    entry = {
        "task_id": _tr.REGISTERED_TASK_ID,
        "runner_path": _tr.RUNNER_PATH,
        "runner_invocation": _tr.RUNNER_INVOCATION,
        "task_class": _tr.TASK_CLASS,
        "classification": list(_tr.TASK_CLASSIFICATION),
        "output_artifact_dir": ARTIFACT_DIR,
        "output_is_gitignored": ARTIFACT_IS_GITIGNORED,
        "status": "eligible",
        "read_only": True, "no_network": True, "no_git_write": True,
        "requires_no_human_gate_crossing": True,
        "does_not_auto_advance_or_promote": True,
        "enabling_in_overnight_runner_is_a_separate_human_gate": True,
    }
    entry["allowlist_check"] = _tr.is_task_allowed_in_report_only_queue(entry)
    return entry


def v2_report_artifact_path(stamp: str | None = None) -> str:
    """PURE. The expected report-only artifact path (under the gitignored ARTIFACT_DIR) for
    Jarvis / morning-report surfacing. With no stamp, returns the directory + basename
    pattern; with a stamp, the concrete markdown path. No I/O."""
    if stamp:
        return "%s/%s_%s.md" % (ARTIFACT_DIR, ARTIFACT_MARKDOWN_BASENAME, stamp)
    return "%s/%s_*.md" % (ARTIFACT_DIR, ARTIFACT_MARKDOWN_BASENAME)


def resolve_dispatch(task_entry: dict) -> dict[str, Any]:
    """PURE. DEFINE (do not execute) how a future report-only pass would invoke an ALLOWED
    queue entry. Returns the invocation descriptor with will_execute pinned False. Refuses
    to describe a dispatch for a task the allowlist does not admit. Never raises, runs
    nothing."""
    check = _tr.is_task_allowed_in_report_only_queue(task_entry or {})
    if not check["allowed"]:
        return {"dispatchable": False, "reasons": check["reasons"],
                "will_execute": False}
    return {
        "dispatchable": True,
        "runner_invocation": _tr.RUNNER_INVOCATION,
        "output_artifact_dir": ARTIFACT_DIR,
        "output_is_gitignored": True,
        "will_execute": False,
        "executes_here": False,
        "requires_human_or_scheduled_trigger": True,
        "trigger_is_not_installed_here": True,
    }


def build_v2_report_only_queue() -> dict[str, Any]:
    """Assemble the additive V2 report-only queue. Pure; no I/O. Gated on the live registry
    being REGISTERED + its safety proof + the legacy frozen allowlist being preserved;
    otherwise BLOCKED. Executes nothing."""
    registration = _tr.build_task_registration()
    reg_valid = _tr.validate_task_registration(registration)["valid"]
    proof = registration["registration_safety_proof"]
    legacy = _legacy_allowlist_preserved()
    entry = _queue_entry()

    record: dict[str, Any] = {
        "schema_version": QA_SCHEMA_VERSION, "mode": QA_MODE, "lane": QA_LANE,
        "bundle_name": BUNDLE_NAME,
        "section": "automation_v2_report_only_queue_adapter",
        "is_definition_only": True, "executes_nothing": True,
        "is_additive_adapter": True,
        "does_not_invoke_runner": True, "does_not_run_autopilot": True,
        "does_not_modify_frozen_overnight_queue_allowlist": True,
        "label": (
            "SPARTA Automation V2 report-only queue adapter (READ-ONLY, RESEARCH ONLY, "
            "DEFINITION ONLY). Additively wires the registered daily report task into a "
            "consultable overnight report-only queue; preserves the frozen legacy "
            "allowlist; installs / triggers NO scheduler; executes nothing."),
        # the concrete report-only queue (what a future overnight pass would iterate)
        "queue": [entry],
        "queue_task_ids": [entry["task_id"]],
        "registry_verdict": registration["verdict"],
        "registry_valid": reg_valid,
        # legacy preservation proof
        "legacy_allowlist_preserved": legacy,
        # eligibility + dispatch definition
        "eligible_for_future_overnight_report_only_execution": True,
        "dispatch_definition": resolve_dispatch(entry),
        # artifact surfacing for Jarvis / morning report
        "artifact_dir": ARTIFACT_DIR,
        "artifact_is_gitignored": ARTIFACT_IS_GITIGNORED,
        "artifact_path_pattern": v2_report_artifact_path(),
        # scheduler safety
        "scheduler_safety": {
            "installs_scheduler": False, "triggers_scheduler": False,
            "modifies_windows_task_scheduler": False, "modifies_cron": False,
            "modifies_existing_scheduled_task": False,
            "starts_background_process": False, "starts_persistent_daemon": False,
            "auto_executes": False, "is_definition_only": True,
            "invocation_is_manual_or_operator_initiated": True},
        # C22 state surfaced (sourced from the registry safety proof)
        "c22_data_not_ready": registration["c22_data_not_ready"],
        "recommends_dataset_staging_only": registration["recommends_dataset_staging_only"],
        "next_human_approval_token": registration["next_human_approval_token"],
        "registration_safety_proof": proof,
        "danger_locks": dict(registration["danger_locks"]),
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
    if registration["verdict"] != _tr.VERDICT_REGISTERED:
        blockers.append("registry_not_registered")
    if reg_valid is not True:
        blockers.append("registry_invalid")
    if not entry["allowlist_check"]["allowed"]:
        blockers.append("queue_entry_not_allowed")
    if not legacy["unchanged"]:
        blockers.append("legacy_allowlist_changed")
    if not legacy["v2_task_not_in_legacy_allowlist"]:
        blockers.append("v2_task_smuggled_into_legacy_allowlist")
    if not proof["all_dangerous_capabilities_disproven"]:
        blockers.append("dangerous_capability_not_disproven")
    if not proof["recommends_dataset_staging_only"]:
        blockers.append("c22_not_recommending_dataset_staging_only")
    record["verdict"] = VERDICT_QUEUE_BLOCKED if blockers else VERDICT_QUEUE_READY
    return record


def validate_v2_report_only_queue(record: Any) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the adapter is research-only, definition-only
    (invokes nothing, runs no autopilot, installs/triggers no scheduler), additive (the
    legacy frozen allowlist is preserved and the V2 task is not smuggled into it), the
    queue's single entry is the registered REPORT_ONLY / READ_ONLY / NO_NETWORK /
    NO_GIT_WRITE daily report task into the GITIGNORED reports path, dispatch executes
    nothing, the runner is proven incapable of every dangerous action, C22 DATA_NOT_READY
    still recommends dataset staging only, and every capability flag is False."""
    failures: list = []
    if not isinstance(record, dict):
        return {"valid": False, "failures": ["record_not_a_dict"]}
    r = record

    if r.get("mode") != QA_MODE:
        failures.append("mode_not_research_only")
    if r.get("verdict") not in (VERDICT_QUEUE_READY, VERDICT_QUEUE_BLOCKED):
        failures.append("bad_verdict")
    if r.get("is_definition_only") is not True:
        failures.append("not_definition_only")
    if r.get("executes_nothing") is not True:
        failures.append("executes_something")
    if r.get("is_additive_adapter") is not True:
        failures.append("not_additive_adapter")
    if r.get("does_not_invoke_runner") is not True:
        failures.append("must_not_invoke_runner")
    if r.get("does_not_run_autopilot") is not True:
        failures.append("must_not_run_autopilot")
    if r.get("does_not_modify_frozen_overnight_queue_allowlist") is not True:
        failures.append("must_not_modify_frozen_overnight_queue_allowlist")

    # legacy preservation
    legacy = r.get("legacy_allowlist_preserved") or {}
    if legacy.get("unchanged") is not True:
        failures.append("legacy_allowlist_changed")
    if legacy.get("v2_task_not_in_legacy_allowlist") is not True:
        failures.append("v2_task_in_legacy_allowlist")
    if legacy.get("legacy_contract_self_certifies") is not True:
        failures.append("legacy_contract_does_not_self_certify")
    if tuple(legacy.get("frozen_allowlist") or ()) != _LEGACY_FROZEN_ALLOWLIST:
        failures.append("frozen_allowlist_snapshot_wrong")

    # the queue + its single registered entry
    queue = r.get("queue") or []
    if len(queue) != 1:
        failures.append("queue_must_have_exactly_the_registered_task")
    if r.get("registry_verdict") != _tr.VERDICT_REGISTERED:
        failures.append("registry_not_registered")
    if r.get("registry_valid") is not True:
        failures.append("registry_invalid")
    for entry in queue:
        if entry.get("task_id") != _tr.REGISTERED_TASK_ID:
            failures.append("queue_entry_task_id_wrong")
        if entry.get("runner_path") != _tr.RUNNER_PATH:
            failures.append("queue_entry_runner_path_wrong")
        if entry.get("task_class") != "REPORT_ONLY":
            failures.append("queue_entry_not_report_only")
        cls = entry.get("classification") or []
        for c in ("REPORT_ONLY", "READ_ONLY", "NO_NETWORK", "NO_GIT_WRITE"):
            if c not in cls:
                failures.append("queue_entry_classification_missing_%s" % c)
        if entry.get("output_artifact_dir") != ARTIFACT_DIR:
            failures.append("queue_entry_artifact_dir_wrong")
        if not str(entry.get("output_artifact_dir", "")).startswith("reports/"):
            failures.append("queue_entry_artifact_not_under_reports")
        if entry.get("output_is_gitignored") is not True:
            failures.append("queue_entry_output_not_gitignored")
        ac = entry.get("allowlist_check") or {}
        if ac.get("allowed") is not True:
            failures.append("queue_entry_not_admitted_by_allowlist")

    # eligibility + dispatch executes nothing
    if r.get("eligible_for_future_overnight_report_only_execution") is not True:
        failures.append("not_eligible_for_future_overnight_execution")
    disp = r.get("dispatch_definition") or {}
    if disp.get("dispatchable") is not True:
        failures.append("dispatch_not_dispatchable")
    if disp.get("will_execute") is not False:
        failures.append("dispatch_would_execute")
    if disp.get("requires_human_or_scheduled_trigger") is not True:
        failures.append("dispatch_missing_trigger_gate")

    # artifact path is gitignored + under reports
    if r.get("artifact_dir") != ARTIFACT_DIR:
        failures.append("artifact_dir_wrong")
    if not str(r.get("artifact_dir", "")).startswith("reports/"):
        failures.append("artifact_not_under_reports")
    if r.get("artifact_is_gitignored") is not True:
        failures.append("artifact_not_gitignored")
    if ARTIFACT_DIR not in str(r.get("artifact_path_pattern", "")):
        failures.append("artifact_path_pattern_wrong")

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

    # safety proof: dangerous capabilities disproven
    proof = r.get("registration_safety_proof") or {}
    if proof.get("all_dangerous_capabilities_disproven") is not True:
        failures.append("dangerous_capability_not_disproven")
    pic = proof.get("proven_incapable_of") or {}
    for k in ("fetch_data", "trade", "place_orders", "commit", "push",
              "advance_gate", "promote_candidate", "use_api"):
        if pic.get(k) is not True:
            failures.append("not_proven_incapable_of_%s" % k)

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

    # verdict consistency
    blockers = r.get("blockers") or []
    if r.get("verdict") == VERDICT_QUEUE_READY and blockers:
        failures.append("ready_with_blockers")
    if r.get("verdict") == VERDICT_QUEUE_BLOCKED and not blockers:
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
