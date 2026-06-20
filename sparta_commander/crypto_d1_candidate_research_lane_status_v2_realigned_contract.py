"""Crypto-D1 candidate research lane status -- V2 REALIGNED CURRENT VIEW
-- PURE, READ-ONLY, RESEARCH ONLY, STATUS-SURFACE ONLY.

An ADDITIVE realigned lane-status surface that accurately reflects the CURRENT lane state:

  * C21 closed / rejected at fee-honest replay (kept on record; ledger C1-C21 = 26);
  * C22 (external_signum_trend_radar_gc_long_short) is the CURRENT active/passive collection
    lane at HOLD_FOR_MORE_FROZEN_DATA_WINDOWS, replay LOCKED, collection progress sourced
    from the committed tracker logic (bootstrap baseline 1/20; live count via the tracker
    runner);
  * C23 (crypto_cross_sectional_low_volatility_anomaly_beta_neutral) is QUEUED / ON-DECK
    only -- its family proposal is FROZEN for human review and it MUST NOT become active
    until C22 concludes and a human approves
    HUMAN_DECISION_OPEN_CANDIDATE_23_AFTER_C22_CONCLUDES_OR_HOLD.

WHY ADDITIVE (not a v1 mutation): the v1 lane-status contract
(crypto_d1_candidate_research_lane_status_v1_contract) is CHAIN-REFERENCED by the already
pushed C22 family-proposal contract (which blocks unless active_candidate is None) and by
several other pushed contracts/tools; v1 is therefore kept FROZEN as the historical
"C22 family-proposal readiness" snapshot, and THIS contract supersedes it for the CURRENT
view. This is a STATUS SURFACE only: it reads frozen committed facts, builds nothing,
modifies no C21/C22/C23 logic, opens no candidate, runs no labels/replay, fetches nothing,
and advances nothing. Every capability flag is pinned False.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.crypto_d1_candidate_research_lane_status_v1_contract as _v1
import sparta_commander.c22_signum_gc_data_collection_tracker_contract as _trk
import sparta_commander.crypto_cross_sectional_low_volatility_anomaly_beta_neutral_v1_proposal_contract as _c23  # noqa: E501

LS2_SCHEMA_VERSION = 1
LS2_MODE = "RESEARCH_ONLY"
LS2_LANE = "crypto_d1_auto_research"

# C22 -- the in-flight active collection candidate.
C22_CANDIDATE_ID = "C22"
C22_FAMILY = "external_signum_trend_radar_gc_long_short"
C22_STAGE = "real_candle_labels_review"
C22_STATE = _trk.C22_STATE                              # HOLD_FOR_MORE_FROZEN_DATA_WINDOWS
C22_COLLECTION_HOLD_TOKEN = _trk.NEXT_HUMAN_ACTION_WHEN_READY
REQUIRED_WINDOWS = _trk.REQUIRED_WINDOWS               # 20

# C23 -- the queued / on-deck candidate (proposal frozen).
C23_CANDIDATE_ID = _c23.CANDIDATE_ID                   # "C23"
C23_FAMILY = _c23.CANDIDATE_FAMILY
C23_OPEN_GATE_AFTER_C22 = _c23.NEXT_HUMAN_GATE_AFTER_PROPOSAL

VERDICT_REALIGNED = "CRYPTO_D1_LANE_STATUS_REALIGNED_C22_ACTIVE_C23_ON_DECK"

_CAPABILITY_FLAGS_FALSE = (
    "executes", "modifies_c21_rejection_logic", "modifies_c22_pipeline",
    "modifies_c22_importer", "modifies_c22_scheduler", "modifies_c23_proposal",
    "opens_c23_as_active", "mutates_lane_status_v1", "runs_labels", "runs_replay",
    "builds_replay", "optimizes_parameters", "fetches_data", "stages_data",
    "performs_network_io", "connects_signum", "uses_mcp", "accesses_hyperliquid",
    "calls_api", "uses_credentials", "uses_api_keys", "edits_bots", "sends_trades",
    "places_orders", "contains_order_logic", "paper_trading", "live_trading",
    "connects_broker", "installs_scheduler", "triggers_scheduler", "starts_c24",
    "reopens_c21", "auto_commits", "auto_pushes", "auto_advances",
    "crosses_into_forbidden_gate",
)


def build_realigned_lane_status(collected_windows: int | None = None) -> dict[str, Any]:
    """PURE. Build the realigned current lane-status snapshot. Sources the rejected ledger
    + C21 rejection detail from the FROZEN v1 surface (read-only), the C22 collection
    progress from the committed tracker logic (bootstrap baseline unless a live count is
    passed), and the C23 family/verdict/open-gate from the committed C23 proposal. No I/O."""
    v1 = _v1.get_lane_status()
    c21_detail = dict(v1.get("last_rejected_candidate_detail") or {})
    ledger_count = v1.get("rejected_ledger_count")

    # C22 collection progress from the committed tracker logic (bootstrap baseline = 1/20).
    baseline = _trk.build_collection_status([_trk.EXPORT_PREFIX + ".json"])
    collected = (baseline["collected_windows"] if collected_windows is None
                 else int(collected_windows))
    windows_remaining = max(0, REQUIRED_WINDOWS - collected)
    progress = "%d/%d" % (collected, REQUIRED_WINDOWS)

    # C23 proposal status (frozen for human review).
    c23_proposal = _c23.build_c23_proposal()
    c23_verdict = c23_proposal.get("verdict")

    record: dict[str, Any] = {
        "schema_version": LS2_SCHEMA_VERSION, "mode": LS2_MODE, "lane": LS2_LANE,
        "is_realigned_current_lane_status": True,
        "is_status_surface_only": True,
        "supersedes_lane_status_v1_for_current_view": True,
        "v1_kept_frozen_for_pushed_c22_proposal_chain": True,
        "label": (
            "Crypto-D1 candidate research lane status -- REALIGNED current view (READ-ONLY, "
            "STATUS SURFACE ONLY). C21 rejected/closed (ledger C1-C21=26); C22 is the active "
            "collection lane at HOLD_FOR_MORE_FROZEN_DATA_WINDOWS, replay locked, "
            "progress %s; C23 is queued/on-deck with its proposal frozen and must not open "
            "until C22 concludes + explicit human approval. Modifies no C21/C22/C23 logic; "
            "opens no candidate; advances nothing." % progress),
        # --- rejected ledger / C21 closed -----------------------------------
        "rejected_ledger_count": ledger_count,
        "rejected_ledger_is_c1_to_c21": ledger_count == 26,
        "last_rejected_candidate": v1.get("last_rejected_candidate"),
        "c21_closed_rejected": True,
        "c21_rejection_status": "REJECTED_AT_FEE_HONEST_REPLAY_KEPT_ON_RECORD",
        "c21_rejection_verdict": c21_detail.get("verdict"),
        "c21_rejected_at_stage": c21_detail.get("rejected_at"),
        "c21_rejection_logic_unchanged": True,
        # --- C22 active / passive collection lane ---------------------------
        "active_candidate": C22_CANDIDATE_ID,
        "active_candidate_detail": {
            "candidate_id": C22_CANDIDATE_ID,
            "family": C22_FAMILY,
            "stage": C22_STAGE,
            "state": C22_STATE,
            "is_active_collection_lane": True,
            "is_passive_collection_lane": True,
            "replay_locked": True,
            "collected_windows": collected,
            "required_windows": REQUIRED_WINDOWS,
            "windows_remaining": windows_remaining,
            "collection_progress": progress,
            "collection_progress_source": (
                "committed tracker logic (bootstrap baseline; live count via the "
                "tracker runner / Jarvis tracker)"),
            "collection_hold_token": C22_COLLECTION_HOLD_TOKEN,
            "collection_pipeline_untouched": True,
        },
        "c22_state": C22_STATE,
        "c22_replay_locked": True,
        "c22_is_active": True,
        # --- C23 queued / on-deck only --------------------------------------
        "on_deck_candidate": C23_CANDIDATE_ID,
        "on_deck_candidate_detail": {
            "candidate_id": C23_CANDIDATE_ID,
            "family": C23_FAMILY,
            "proposal_verdict": c23_verdict,
            "proposal_frozen_for_human_review":
                c23_verdict == "C23_PROPOSAL_FROZEN_FOR_HUMAN_REVIEW",
            "is_active": False,
            "is_queued_on_deck": True,
            "must_not_become_active_until_c22_concludes": True,
            "open_requires_human_token": C23_OPEN_GATE_AFTER_C22,
        },
        "c23_is_active": False,
        "c23_is_queued_on_deck": True,
        "c23_open_gate_after_c22_concludes": C23_OPEN_GATE_AFTER_C22,
        # --- current lane action: C22 collection (HOLD); C23 queued behind --
        "current_stage": "c22_active_collection_hold__c23_on_deck",
        "next_required_action": C22_COLLECTION_HOLD_TOKEN,
        "advances_nothing": True,
        "human_review_required": True,
        "verdict": VERDICT_REALIGNED,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_execute": True, "no_modify_c21_rejection": True, "no_modify_c22_pipeline": True,
        "no_modify_c22_importer": True, "no_modify_c22_scheduler": True,
        "no_modify_c23_proposal": True, "no_open_c23_as_active": True,
        "no_mutate_lane_status_v1": True, "no_run_labels": True, "no_replay": True,
        "no_optimization": True, "no_data_fetch": True, "no_network_io": True,
        "no_signum_connection": True, "no_mcp": True, "no_hyperliquid": True,
        "no_api_keys": True, "no_credentials": True, "no_bot_edits": True,
        "no_send_trades": True, "no_order_logic": True, "no_paper_trading": True,
        "no_live_trading": True, "no_broker": True, "no_install_scheduler": True,
        "no_trigger_scheduler": True, "no_reopen_c21": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_realigned_lane_status(record: Any) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when research-only, status-surface-only; C21 is
    shown closed/rejected (ledger 26) with its rejection logic unchanged; C22 is the active
    collection lane at HOLD_FOR_MORE_FROZEN_DATA_WINDOWS with replay locked and a progress
    consistent with the required-window count; C23 is queued/on-deck (proposal frozen, NOT
    active) and may open only via the after-C22 human token; v1 is left frozen; and every
    capability flag is False."""
    failures: list = []
    if not isinstance(record, dict):
        return {"valid": False, "failures": ["record_not_a_dict"]}
    r = record

    if r.get("mode") != LS2_MODE:
        failures.append("mode_not_research_only")
    if r.get("is_realigned_current_lane_status") is not True:
        failures.append("not_realigned_status")
    if r.get("is_status_surface_only") is not True:
        failures.append("not_status_surface_only")
    if r.get("verdict") != VERDICT_REALIGNED:
        failures.append("bad_verdict")
    if r.get("supersedes_lane_status_v1_for_current_view") is not True:
        failures.append("must_supersede_v1_for_current_view")
    if r.get("v1_kept_frozen_for_pushed_c22_proposal_chain") is not True:
        failures.append("must_keep_v1_frozen")

    # C21 closed/rejected, ledger 26, rejection logic unchanged
    if r.get("rejected_ledger_count") != 26:
        failures.append("ledger_not_26")
    if r.get("last_rejected_candidate") != "C21":
        failures.append("last_rejected_not_c21")
    if r.get("c21_closed_rejected") is not True:
        failures.append("c21_not_closed")
    if r.get("c21_rejection_logic_unchanged") is not True:
        failures.append("c21_rejection_logic_must_be_unchanged")

    # C22 active collection lane, HOLD, replay locked, progress consistent
    if r.get("active_candidate") != "C22":
        failures.append("active_candidate_not_c22")
    if r.get("c22_state") != C22_STATE:
        failures.append("c22_state_not_hold")
    if r.get("c22_replay_locked") is not True:
        failures.append("c22_replay_not_locked")
    ad = r.get("active_candidate_detail") or {}
    if ad.get("family") != C22_FAMILY:
        failures.append("c22_family_wrong")
    if ad.get("state") != C22_STATE:
        failures.append("c22_detail_state_wrong")
    if ad.get("replay_locked") is not True:
        failures.append("c22_detail_replay_not_locked")
    if ad.get("required_windows") != REQUIRED_WINDOWS:
        failures.append("required_windows_wrong")
    cw = ad.get("collected_windows")
    if not isinstance(cw, int) or cw < 0:
        failures.append("bad_collected_windows")
    elif ad.get("windows_remaining") != max(0, REQUIRED_WINDOWS - cw):
        failures.append("windows_remaining_inconsistent")
    elif ad.get("collection_progress") != "%d/%d" % (cw, REQUIRED_WINDOWS):
        failures.append("progress_string_inconsistent")
    if ad.get("collection_pipeline_untouched") is not True:
        failures.append("c22_pipeline_must_be_untouched")

    # C23 queued/on-deck only, proposal frozen, not active
    if r.get("on_deck_candidate") != "C23":
        failures.append("on_deck_not_c23")
    if r.get("c23_is_active") is not False:
        failures.append("c23_must_not_be_active")
    if r.get("c23_is_queued_on_deck") is not True:
        failures.append("c23_must_be_on_deck")
    if r.get("c23_open_gate_after_c22_concludes") != C23_OPEN_GATE_AFTER_C22:
        failures.append("c23_open_gate_wrong")
    od = r.get("on_deck_candidate_detail") or {}
    if od.get("family") != C23_FAMILY:
        failures.append("c23_family_wrong")
    if od.get("proposal_frozen_for_human_review") is not True:
        failures.append("c23_proposal_not_frozen")
    if od.get("is_active") is not False:
        failures.append("c23_detail_active_true")
    if od.get("must_not_become_active_until_c22_concludes") is not True:
        failures.append("c23_must_wait_for_c22")
    if od.get("open_requires_human_token") != C23_OPEN_GATE_AFTER_C22:
        failures.append("c23_open_token_wrong")

    # current action + advances nothing
    if r.get("next_required_action") != C22_COLLECTION_HOLD_TOKEN:
        failures.append("next_action_not_c22_collection_hold")
    if r.get("advances_nothing") is not True:
        failures.append("must_advance_nothing")

    locks = r.get("scope_locks") or {}
    for key in ("no_execute", "no_modify_c21_rejection", "no_modify_c22_pipeline",
                "no_modify_c23_proposal", "no_open_c23_as_active",
                "no_mutate_lane_status_v1", "no_run_labels", "no_replay",
                "no_optimization", "no_data_fetch", "no_network_io",
                "no_signum_connection", "no_mcp", "no_order_logic", "no_paper_trading",
                "no_live_trading", "no_install_scheduler", "no_reopen_c21"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if r.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
