"""SPARTA CURRENT-STATE CONTROL PACKET -- canonical read-only aggregate surface
-- PURE, READ-ONLY, REPORTING ONLY.

One CANONICAL current-state packet that aggregates (read-only) the whole research-workflow
status into a single source of truth, ending the multi-way redundant status computation:

  * repo state (HEAD / origin / ahead-behind / clean / staged / dangerous-staged guard);
  * lane state (C21 closed/rejected ledger 26; C22 active collection lane HOLD_FOR_MORE_
    FROZEN_DATA_WINDOWS, replay locked, progress X/20; C23 queued/on-deck, proposal frozen);
  * C22 collection (live count, missing-export warning, 20/20 readiness alert);
  * scheduled-task health (OK / STALE / FAILED / MISSING, from the health classifier);
  * the current TRUE next action + the suggested tokens (collect / review-at-20-20 / open
    C23-after-C22), which are SUGGESTIONS ONLY and are NEVER auto-executed.

It reuses the committed C22 current morning packet (which reads the realigned lane-status v2
surface + tracker) for the lane/progress facts, so progress is single-sourced through that
chain. It is PURE: the runner gathers the git facts + task records + dates read-only and
passes them in; this contract performs NO I/O, modifies NOTHING, changes NO scheduled task,
runs NO labels/replay, fetches NO data, connects to NOTHING, and advances NOTHING. Every
capability flag is pinned False.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.sparta_c22_current_morning_packet_contract as _c22cur
import sparta_commander.c22_signum_gc_data_collection_tracker_contract as _trk
import sparta_commander.sparta_scheduled_task_health_classifier_contract as _th

CP_SCHEMA_VERSION = 1
CP_MODE = "RESEARCH_ONLY"
CP_LANE = "crypto_d1_auto_research"

REQUIRED_WINDOWS = _trk.REQUIRED_WINDOWS
COLLECT_TOKEN = _c22cur.COLLECT_TOKEN
REVIEW_TOKEN = _c22cur.REVIEW_TOKEN
C23_OPEN_TOKEN = _c22cur.C23_OPEN_GATE
# the number of days a window may lag before a missing-export is warned (one full skipped day)
MISSING_EXPORT_DAY_THRESHOLD = 1

VERDICT_CONTROL = "SPARTA_CURRENT_STATE_CONTROL_PACKET"
STATUS_HEALTHY = "HEALTHY"
STATUS_NEEDS_ATTENTION = "NEEDS_ATTENTION"

# staged paths that must NEVER be committed (gitignored artifact guard).
_DANGEROUS_STAGED_PREFIXES = (
    "data/external_signum_trend_radar_gc/",
    "data/external_signum_trend_radar_gc_inbox/",
    "reports/automation_v2_daily/",
    "reports/autopilot_morning/",
)

_CAPABILITY_FLAGS_FALSE = (
    "executes", "performs_io", "performs_network_io", "modifies_files",
    "modifies_c21_logic", "modifies_c22_pipeline", "modifies_c23_proposal",
    "changes_scheduled_task", "installs_scheduler", "adds_scheduler_code",
    "opens_c23_as_active", "auto_executes_token", "runs_labels", "runs_replay",
    "optimizes_parameters", "fetches_data", "stages_data", "connects_signum", "uses_mcp",
    "accesses_hyperliquid", "calls_api", "uses_credentials", "places_orders",
    "sends_trades", "paper_trading", "live_trading", "connects_broker", "reopens_c21",
    "auto_commits", "auto_pushes", "crosses_into_forbidden_gate",
)


def is_dangerous_staged(staged_paths: Any) -> bool:
    """PURE. True if any staged path is a gitignored artifact that must never be committed."""
    for p in (staged_paths or []):
        s = str(p)
        for pref in _DANGEROUS_STAGED_PREFIXES:
            if s.startswith(pref):
                return True
    return False


def build_current_state_packet(repo_state: dict, collected_windows: int,
                               latest_window_date: Any,
                               days_since_latest_window: Any,
                               task_health: dict) -> dict[str, Any]:
    """PURE. Assemble the canonical current-state control packet from read-only inputs. No
    I/O. Tokens are suggestions only; nothing is executed/advanced."""
    rs = dict(repo_state or {})
    staged_paths = list(rs.get("staged_paths") or [])
    has_staged = len(staged_paths) > 0
    dangerous_staged = is_dangerous_staged(staged_paths)

    # lane + C22 collection (single-sourced via the committed current morning packet)
    cur = _c22cur.build_c22_current_morning_packet(collected_windows)
    collected = cur["collected_windows"]
    ready_for_review = cur["ready_for_review"]

    # C22 missing-export warning (an expected daily window appears to be missing)
    dsl = days_since_latest_window
    missing_export_warning = (isinstance(dsl, int) and dsl > MISSING_EXPORT_DAY_THRESHOLD)

    th = dict(task_health or {})
    th_valid = _th.validate_task_health(th)["valid"] if th else False
    tasks_attention = bool(th.get("any_failed")) or bool(th.get("any_missing"))

    # overall health: read-only summary -- HEALTHY unless something needs attention.
    attention_reasons: list = []
    if rs.get("clean") is False:
        attention_reasons.append("tracked_tree_dirty")
    if dangerous_staged:
        attention_reasons.append("dangerous_artifact_staged")
    if tasks_attention:
        attention_reasons.append("scheduled_task_failed_or_missing")
    if th.get("any_stale"):
        attention_reasons.append("scheduled_task_stale")
    if missing_export_warning:
        attention_reasons.append("c22_export_appears_missing")
    overall = STATUS_NEEDS_ATTENTION if attention_reasons else STATUS_HEALTHY

    record: dict[str, Any] = {
        "schema_version": CP_SCHEMA_VERSION, "mode": CP_MODE, "lane": CP_LANE,
        "is_current_state_control_packet": True, "is_read_only_surface": True,
        "verdict": VERDICT_CONTROL,
        "overall_status": overall,
        "attention_reasons": attention_reasons,
        # repo state
        "repo_state": {
            "head": rs.get("head"), "origin": rs.get("origin"),
            "ahead": rs.get("ahead"), "behind": rs.get("behind"),
            "in_sync": (rs.get("ahead") == 0 and rs.get("behind") == 0),
            "tracked_tree_clean": rs.get("clean"),
            "has_staged": has_staged,
            "staged_count": len(staged_paths),
            "dangerous_staged_artifact": dangerous_staged,
        },
        # lane state (single-sourced)
        "lane": {
            "c21_closed_rejected": cur["c21_closed_rejected"],
            "rejected_ledger_count": cur["rejected_ledger_count"],
            "active_candidate": "C22",
            "c22_family": cur["c22_family"],
            "c22_state": cur["c22_state"],
            "c22_replay_locked": cur["c22_replay_locked"],
            "c23_on_deck": cur["c23_on_deck"],
            "c23_is_active": cur["c23_is_active"],
            "c23_proposal_frozen": cur["c23_proposal_frozen"],
        },
        # C22 collection
        "c22_collection": {
            "collected_windows": collected,
            "required_windows": REQUIRED_WINDOWS,
            "progress": cur["collection_progress"],
            "windows_remaining": cur["windows_remaining"],
            "latest_window_date": latest_window_date,
            "days_since_latest_window": dsl,
            "missing_export_warning": missing_export_warning,
            "missing_export_detail": (
                "no new frozen GC window for >%d day(s); run the external read-only routine "
                "and save the daily export" % MISSING_EXPORT_DAY_THRESHOLD
                if missing_export_warning else None),
            "ready_for_review": ready_for_review,
            "readiness_alert": (
                "C22 has reached %d/%d -- you may now (suggestion) paste: %s"
                % (collected, REQUIRED_WINDOWS, REVIEW_TOKEN)
                if ready_for_review else None),
        },
        # scheduled-task health
        "task_health": th,
        "task_health_record_valid": th_valid,
        # next action (suggestion only, never executed)
        "next_action": {
            "authoritative_next_action": cur["authoritative_next_action"],
            "authoritative_next_action_source": cur["authoritative_next_action_source"],
            "collect_more_windows_token": COLLECT_TOKEN,
            "review_token_when_ready": REVIEW_TOKEN,
            "c23_open_token_after_c22": C23_OPEN_TOKEN,
            "tokens_are_suggestion_only": True,
            "auto_executes_any_token": False,
        },
        "supersedes_stale_data_not_ready_view": True,
        "advances_nothing": True,
        "human_review_required": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_execute": True, "no_io": True, "no_network_io": True, "no_modify_files": True,
        "no_modify_c21_logic": True, "no_modify_c22_pipeline": True,
        "no_modify_c23_proposal": True, "no_change_scheduled_task": True,
        "no_install_scheduler": True, "no_add_scheduler_code": True,
        "no_open_c23_as_active": True, "no_auto_execute_token": True, "no_run_labels": True,
        "no_replay": True, "no_optimization": True, "no_data_fetch": True,
        "no_signum_connection": True, "no_mcp": True, "no_hyperliquid": True,
        "no_api_keys": True, "no_credentials": True, "no_order_logic": True,
        "no_paper_trading": True, "no_live_trading": True, "no_broker": True,
        "no_reopen_c21": True, "no_auto_commit": True, "no_auto_push": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_current_state_packet(record: Any) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when research-only, read-only surface; the lane
    shows C21 closed (ledger 26) / C22 active HOLD replay-locked / C23 on-deck-not-active;
    the C22 collection progress is consistent; the dangerous-staged guard is present; the
    overall status is consistent with the attention reasons; the next-action tokens are
    suggestion-only and never auto-executed; and every capability flag is False."""
    failures: list = []
    if not isinstance(record, dict):
        return {"valid": False, "failures": ["record_not_a_dict"]}
    r = record

    if r.get("mode") != CP_MODE:
        failures.append("mode_not_research_only")
    if r.get("is_current_state_control_packet") is not True:
        failures.append("not_control_packet")
    if r.get("is_read_only_surface") is not True:
        failures.append("not_read_only_surface")
    if r.get("verdict") != VERDICT_CONTROL:
        failures.append("bad_verdict")
    if r.get("overall_status") not in (STATUS_HEALTHY, STATUS_NEEDS_ATTENTION):
        failures.append("bad_overall_status")

    # overall status consistent with attention reasons
    reasons = r.get("attention_reasons") or []
    if r.get("overall_status") == STATUS_HEALTHY and reasons:
        failures.append("healthy_with_attention_reasons")
    if r.get("overall_status") == STATUS_NEEDS_ATTENTION and not reasons:
        failures.append("attention_without_reasons")

    # lane
    lane = r.get("lane") or {}
    if lane.get("c21_closed_rejected") is not True:
        failures.append("c21_not_closed")
    if lane.get("rejected_ledger_count") != 26:
        failures.append("ledger_not_26")
    if lane.get("active_candidate") != "C22":
        failures.append("active_not_c22")
    if lane.get("c22_state") != "HOLD_FOR_MORE_FROZEN_DATA_WINDOWS":
        failures.append("c22_state_not_hold")
    if lane.get("c22_replay_locked") is not True:
        failures.append("replay_not_locked")
    if lane.get("c23_on_deck") is not True or lane.get("c23_is_active") is not False:
        failures.append("c23_not_on_deck_only")

    # C22 collection progress consistent
    coll = r.get("c22_collection") or {}
    cw = coll.get("collected_windows")
    if not isinstance(cw, int) or cw < 0:
        failures.append("bad_collected_windows")
    else:
        if coll.get("required_windows") != REQUIRED_WINDOWS:
            failures.append("required_windows_wrong")
        if coll.get("windows_remaining") != max(0, REQUIRED_WINDOWS - cw):
            failures.append("windows_remaining_inconsistent")
        if coll.get("progress") != "%d/%d" % (cw, REQUIRED_WINDOWS):
            failures.append("progress_inconsistent")
        if coll.get("ready_for_review") is not (cw >= REQUIRED_WINDOWS):
            failures.append("ready_inconsistent")

    # repo state: dangerous-staged guard present
    rs = r.get("repo_state") or {}
    if "dangerous_staged_artifact" not in rs:
        failures.append("dangerous_staged_guard_missing")

    # next action: tokens suggestion-only, never auto-executed; never the stale staging token
    na = r.get("next_action") or {}
    if na.get("tokens_are_suggestion_only") is not True:
        failures.append("tokens_not_suggestion_only")
    if na.get("auto_executes_any_token") is not False:
        failures.append("tokens_must_not_auto_execute")
    if na.get("collect_more_windows_token") != COLLECT_TOKEN:
        failures.append("collect_token_wrong")
    if na.get("review_token_when_ready") != REVIEW_TOKEN:
        failures.append("review_token_wrong")
    if na.get("c23_open_token_after_c22") != C23_OPEN_TOKEN:
        failures.append("c23_open_token_wrong")
    expected_auth = REVIEW_TOKEN if coll.get("ready_for_review") else COLLECT_TOKEN
    if na.get("authoritative_next_action") != expected_auth:
        failures.append("authoritative_action_inconsistent")

    if r.get("advances_nothing") is not True:
        failures.append("must_advance_nothing")

    locks = r.get("scope_locks") or {}
    for key in ("no_execute", "no_io", "no_network_io", "no_modify_files",
                "no_modify_c21_logic", "no_modify_c22_pipeline", "no_modify_c23_proposal",
                "no_change_scheduled_task", "no_install_scheduler", "no_add_scheduler_code",
                "no_open_c23_as_active", "no_auto_execute_token", "no_run_labels",
                "no_replay", "no_optimization", "no_data_fetch", "no_signum_connection",
                "no_mcp", "no_order_logic", "no_paper_trading", "no_live_trading",
                "no_reopen_c21"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if r.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
