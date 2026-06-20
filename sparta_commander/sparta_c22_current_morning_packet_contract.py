"""SPARTA C22 CURRENT morning packet -- AUTHORITATIVE next-action surface
-- PURE, READ-ONLY, RESEARCH ONLY, STATUS-SURFACE ONLY.

An ADDITIVE current/live morning packet that supersedes the stale Automation V2
"DATA_NOT_READY / stage dataset" packet for the AUTHORITATIVE next-action display. It reads
the realigned lane-status v2 surface (crypto_d1_candidate_research_lane_status_v2_realigned)
+ the committed tracker / readiness-watcher tokens and reports the CURRENT truth:

  * C21 closed / rejected (ledger C1-C21 = 26);
  * C22 is the ACTIVE collection lane at HOLD_FOR_MORE_FROZEN_DATA_WINDOWS, replay LOCKED,
    progress X/20 (committed baseline 1/20; live collected_windows injectable);
  * TRUE next action while X < 20: collect more frozen daily Trend Radar GC windows
    (HUMAN_STAGE_MORE_FROZEN_DAILY_TREND_RADAR_GC_WINDOWS_THEN_REREVIEW_C22_LABELS);
  * at X >= 20: SUGGEST ONLY HUMAN_APPROVED_C22_SIGNUM_GC_FROZEN_DATA_WINDOW_REVIEW
    (never auto-run);
  * C23 is QUEUED / ON-DECK only (proposal frozen, not active), opening solely via
    HUMAN_DECISION_OPEN_CANDIDATE_23_AFTER_C22_CONCLUDES_OR_HOLD.

It is a STATUS SURFACE: it modifies no C21/C22/C23 logic, opens no candidate, runs no
labels/replay, fetches nothing, and advances nothing. The earlier DATA_NOT_READY /
dataset-staging view is explicitly marked SUPERSEDED (the dataset is staged + validated and
labels were produced; the lane is now collecting more windows). Every capability flag is
pinned False.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.crypto_d1_candidate_research_lane_status_v2_realigned_contract as _v2real  # noqa: E501
import sparta_commander.c22_signum_gc_data_collection_tracker_contract as _trk
import sparta_commander.c22_signum_gc_collection_readiness_watcher_contract as _rw

CMP_SCHEMA_VERSION = 1
CMP_MODE = "RESEARCH_ONLY"
CMP_LANE = "crypto_d1_auto_research"

REQUIRED_WINDOWS = _trk.REQUIRED_WINDOWS                          # 20
C22_STATE = _trk.C22_STATE                                       # HOLD_FOR_MORE_FROZEN...
COLLECT_TOKEN = _trk.NEXT_HUMAN_ACTION_WHEN_READY                # stage-more-windows token
REVIEW_TOKEN = _rw.SUGGESTED_REVIEW_TOKEN                        # frozen-window-review token
C23_OPEN_GATE = _v2real.C23_OPEN_GATE_AFTER_C22                  # open-C23-after-C22 token

AUTHORITATIVE_SOURCE = "C22_CURRENT_COLLECTION"
# the stale token this packet supersedes (the old Automation V2 data-readiness view).
SUPERSEDED_STAGING_TOKEN = (
    "HUMAN_STAGE_FROZEN_TREND_RADAR_GC_DETECTOR_DATASET_THEN_REAUTHORISE_C22_LABELS")

VERDICT_CURRENT = "C22_CURRENT_MORNING_PACKET_AUTHORITATIVE"

_CAPABILITY_FLAGS_FALSE = (
    "executes", "modifies_c21_rejection_logic", "modifies_c22_pipeline",
    "modifies_c22_importer", "modifies_c22_scheduler", "modifies_c22_tracker_storage",
    "modifies_c23_proposal", "opens_c23_as_active", "auto_executes_review_token",
    "runs_labels", "runs_replay", "builds_replay", "optimizes_parameters",
    "fetches_data", "stages_data", "performs_network_io", "connects_signum", "uses_mcp",
    "accesses_hyperliquid", "calls_api", "uses_credentials", "edits_bots", "sends_trades",
    "places_orders", "contains_order_logic", "paper_trading", "live_trading",
    "connects_broker", "installs_scheduler", "triggers_scheduler", "reopens_c21",
    "starts_c24", "auto_commits", "auto_pushes", "auto_advances",
    "crosses_into_forbidden_gate",
)


def build_c22_current_morning_packet(collected_windows: int | None = None) -> dict[str, Any]:
    """PURE. Build the current authoritative morning packet from the realigned lane-status
    v2 surface. `collected_windows` (live tracker count) is injectable; defaults to the
    committed baseline. No I/O."""
    lane = _v2real.build_realigned_lane_status(collected_windows)
    ad = lane["active_candidate_detail"]
    od = lane["on_deck_candidate_detail"]
    collected = ad["collected_windows"]
    remaining = ad["windows_remaining"]
    progress = ad["collection_progress"]
    ready_for_review = collected >= REQUIRED_WINDOWS

    # TRUE next action: collect while < 20; at >= 20 SUGGEST the review token (never auto-run)
    authoritative_next_action = REVIEW_TOKEN if ready_for_review else COLLECT_TOKEN

    record: dict[str, Any] = {
        "schema_version": CMP_SCHEMA_VERSION, "mode": CMP_MODE, "lane": CMP_LANE,
        "section": "c22_current_authoritative_next_action",
        "is_current_authoritative_packet": True, "is_status_surface_only": True,
        "label": (
            "C22 current morning packet -- AUTHORITATIVE next action (READ-ONLY, STATUS "
            "SURFACE). C21 closed; C22 active collection lane HOLD_FOR_MORE_FROZEN_DATA_"
            "WINDOWS, replay locked, progress %s; collect more windows toward 20/20, then "
            "suggest the frozen-window review; C23 queued/on-deck (proposal frozen). "
            "Supersedes the stale DATA_NOT_READY / dataset-staging view." % progress),
        # C21
        "c21_closed_rejected": lane["c21_closed_rejected"],
        "rejected_ledger_count": lane["rejected_ledger_count"],
        # C22 active collection
        "active_candidate": "C22",
        "c22_family": ad["family"],
        "c22_state": C22_STATE,
        "c22_replay_locked": True,
        "collected_windows": collected,
        "required_windows": REQUIRED_WINDOWS,
        "windows_remaining": remaining,
        "collection_progress": progress,
        "ready_for_review": ready_for_review,
        # authoritative next action (current truth)
        "authoritative_next_action_source": AUTHORITATIVE_SOURCE,
        "authoritative_next_action": authoritative_next_action,
        "collect_more_windows_token": COLLECT_TOKEN,
        "review_token_when_ready": REVIEW_TOKEN,
        "review_token_is_suggestion_only": True,
        "auto_executes_review_token": False,
        # supersession of the stale data-readiness view
        "supersedes_automation_v2_data_not_ready_packet": True,
        "superseded_staging_token": SUPERSEDED_STAGING_TOKEN,
        "does_not_present_dataset_staging_as_current_action":
            authoritative_next_action != SUPERSEDED_STAGING_TOKEN,
        # C23 on-deck
        "c23_on_deck": True,
        "c23_family": od["family"],
        "c23_proposal_frozen": od["proposal_frozen_for_human_review"],
        "c23_is_active": False,
        "c23_open_gate": C23_OPEN_GATE,
        # state
        "advances_nothing": True, "human_review_required": True,
        "verdict": VERDICT_CURRENT,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_execute": True, "no_modify_c21_rejection": True,
        "no_modify_c22_pipeline": True, "no_modify_c22_tracker_storage": True,
        "no_modify_c23_proposal": True, "no_open_c23_as_active": True,
        "no_auto_execute_review_token": True, "no_run_labels": True, "no_replay": True,
        "no_optimization": True, "no_data_fetch": True, "no_network_io": True,
        "no_signum_connection": True, "no_mcp": True, "no_hyperliquid": True,
        "no_api_keys": True, "no_credentials": True, "no_bot_edits": True,
        "no_send_trades": True, "no_order_logic": True, "no_paper_trading": True,
        "no_live_trading": True, "no_broker": True, "no_install_scheduler": True,
        "no_trigger_scheduler": True, "no_reopen_c21": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return record


def render_current_packet_markdown(packet: dict) -> str:
    """PURE. The current authoritative next-action section as markdown."""
    s = packet or {}
    lines = [
        "- C21: closed / rejected (ledger C1-C21 = %s)" % s.get("rejected_ledger_count"),
        "- C22 active collection lane: **%s** (replay locked)" % s.get("c22_state"),
        "- Collection progress: **%s** (%s more needed)" % (
            s.get("collection_progress"), s.get("windows_remaining")),
    ]
    if s.get("ready_for_review"):
        lines.append("- TRUE NEXT ACTION (suggestion): `%s`"
                     % s.get("review_token_when_ready"))
    else:
        lines.append("- TRUE NEXT ACTION: collect more frozen daily Trend Radar GC "
                     "windows toward 20/20 -> `%s`" % s.get("collect_more_windows_token"))
        lines.append("- At 20/20 only suggest: `%s`" % s.get("review_token_when_ready"))
    lines.append("- C23: queued / ON-DECK only (proposal FROZEN, not active) -- opens only "
                 "via `%s`" % s.get("c23_open_gate"))
    lines.append("> NOTE: this SUPERSEDES the earlier Automation V2 "
                 "\"DATA_NOT_READY / stage dataset\" view -- the dataset is staged + "
                 "validated and labels were produced; the lane is now collecting more "
                 "windows.")
    return "\n".join(lines)


def render_current_packet_html(packet: dict) -> str:
    """PURE. The current authoritative next-action section as a small HTML block."""
    s = packet or {}

    def esc(x: Any) -> str:
        return (str(x).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
    if s.get("ready_for_review"):
        nxt = ("TRUE NEXT ACTION (suggestion): <code>%s</code>"
               % esc(s.get("review_token_when_ready")))
    else:
        nxt = ("TRUE NEXT ACTION: collect more windows toward 20/20 -> <code>%s</code>"
               % esc(s.get("collect_more_windows_token")))
    return "".join([
        "<ul>",
        "<li>C21: closed / rejected (ledger %s)</li>" % esc(s.get("rejected_ledger_count")),
        "<li>C22 active collection lane: <b>%s</b> (replay locked)</li>"
        % esc(s.get("c22_state")),
        "<li>Collection progress: <b>%s</b> (%s more needed)</li>" % (
            esc(s.get("collection_progress")), esc(s.get("windows_remaining"))),
        "<li>%s</li>" % nxt,
        "<li>C23: queued / on-deck (proposal frozen, not active) -- opens via "
        "<code>%s</code></li>" % esc(s.get("c23_open_gate")),
        "<li>Supersedes the earlier Automation V2 DATA_NOT_READY / dataset-staging "
        "view.</li>",
        "</ul>",
    ])


def validate_c22_current_morning_packet(record: Any) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when research-only, status-surface-only; C21 is
    closed (ledger 26); C22 is active HOLD with replay locked and progress consistent; the
    authoritative next action is the COLLECT token (< 20) or the SUGGESTED REVIEW token
    (>= 20) and is NEVER the superseded dataset-staging token; the review token is a
    suggestion only (never auto-run); C23 is on-deck/frozen/not-active; and every capability
    flag is False."""
    failures: list = []
    if not isinstance(record, dict):
        return {"valid": False, "failures": ["record_not_a_dict"]}
    r = record

    if r.get("mode") != CMP_MODE:
        failures.append("mode_not_research_only")
    if r.get("is_current_authoritative_packet") is not True:
        failures.append("not_current_authoritative_packet")
    if r.get("is_status_surface_only") is not True:
        failures.append("not_status_surface_only")
    if r.get("verdict") != VERDICT_CURRENT:
        failures.append("bad_verdict")

    # C21 closed, ledger 26
    if r.get("c21_closed_rejected") is not True:
        failures.append("c21_not_closed")
    if r.get("rejected_ledger_count") != 26:
        failures.append("ledger_not_26")

    # C22 active HOLD, replay locked, progress consistent
    if r.get("active_candidate") != "C22":
        failures.append("active_not_c22")
    if r.get("c22_state") != C22_STATE:
        failures.append("c22_state_not_hold")
    if r.get("c22_replay_locked") is not True:
        failures.append("replay_not_locked")
    cw = r.get("collected_windows")
    if not isinstance(cw, int) or cw < 0:
        failures.append("bad_collected_windows")
    else:
        if r.get("required_windows") != REQUIRED_WINDOWS:
            failures.append("required_windows_wrong")
        if r.get("windows_remaining") != max(0, REQUIRED_WINDOWS - cw):
            failures.append("windows_remaining_inconsistent")
        if r.get("collection_progress") != "%d/%d" % (cw, REQUIRED_WINDOWS):
            failures.append("progress_string_inconsistent")
        if r.get("ready_for_review") is not (cw >= REQUIRED_WINDOWS):
            failures.append("ready_flag_inconsistent")

    # authoritative next action: collect (<20) or suggested review (>=20); never staging
    ready = r.get("ready_for_review") is True
    expected = REVIEW_TOKEN if ready else COLLECT_TOKEN
    if r.get("authoritative_next_action") != expected:
        failures.append("authoritative_next_action_wrong")
    if r.get("authoritative_next_action_source") != AUTHORITATIVE_SOURCE:
        failures.append("authoritative_source_wrong")
    if r.get("authoritative_next_action") == SUPERSEDED_STAGING_TOKEN:
        failures.append("must_not_present_dataset_staging")
    if r.get("does_not_present_dataset_staging_as_current_action") is not True:
        failures.append("staging_not_marked_superseded")
    if r.get("supersedes_automation_v2_data_not_ready_packet") is not True:
        failures.append("must_supersede_data_not_ready_packet")
    if r.get("review_token_is_suggestion_only") is not True:
        failures.append("review_token_not_suggestion_only")
    if r.get("auto_executes_review_token") is not False:
        failures.append("review_token_must_not_auto_execute")

    # C23 on-deck/frozen/not-active
    if r.get("c23_on_deck") is not True:
        failures.append("c23_not_on_deck")
    if r.get("c23_is_active") is not False:
        failures.append("c23_must_not_be_active")
    if r.get("c23_proposal_frozen") is not True:
        failures.append("c23_proposal_not_frozen")
    if r.get("c23_open_gate") != C23_OPEN_GATE:
        failures.append("c23_open_gate_wrong")

    if r.get("advances_nothing") is not True:
        failures.append("must_advance_nothing")

    locks = r.get("scope_locks") or {}
    for key in ("no_execute", "no_modify_c21_rejection", "no_modify_c22_pipeline",
                "no_modify_c22_tracker_storage", "no_modify_c23_proposal",
                "no_open_c23_as_active", "no_auto_execute_review_token", "no_run_labels",
                "no_replay", "no_optimization", "no_data_fetch", "no_network_io",
                "no_signum_connection", "no_mcp", "no_order_logic", "no_paper_trading",
                "no_live_trading", "no_install_scheduler", "no_reopen_c21"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if r.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
