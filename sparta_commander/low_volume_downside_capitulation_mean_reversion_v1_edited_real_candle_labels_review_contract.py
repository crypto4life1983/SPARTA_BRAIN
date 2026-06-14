"""SPARTA CANDIDATE #9 EDITED REAL-CANDLE DETECTOR LABELS REVIEW /
EVIDENCE FREEZE (READ-ONLY, RESEARCH ONLY, POST-EDIT SAMPLE-SIZE
ADEQUACY STILL STRUCTURALLY FAILED, POST-EDIT AUTO-REJECTION
TRIGGER FIRED, NOT A PROFITABILITY CLAIM, NOT A RESCUE):
LOW_VOLUME_DOWNSIDE_CAPITULATION_MEAN_REVERSION_V1.

Freezes the EDITED one-pass real-candle detection result on the
staged BTCUSD 15m data for the sample window 2026-05-02_2026-06-10
produced by the untracked edited runner
tools/c9_edited_real_candle_detection_relaxed_z_once.py with the
SINGLE applied edit DOWNSIDE_Z_SCORE_THRESHOLD = -1.5 (was -2.0,
per the pushed C9 single-edit decision at commit 6e88a827):

  - 3,840 staged BTCUSD 15m bars scanned (closed window
    2026-05-02T00:00:00Z .. 2026-06-10T23:45:00Z; same coverage as
    the original detection);
  - 27 joint-trigger attempts (vs 8 original; 3.4x increase from
    the relaxed z threshold, matching the normal-distribution
    lower-tail expansion from ~2.3% to ~6.7% of bars);
  - 5 accepted setups before the proposal-level anti-cluster filter;
  - 5 accepted setups after the proposal-level anti-cluster filter;
  - 0 dropped by anti-cluster (the 5 accepted events are spread
    over the sample window with gaps >= 8 bars; nothing to drop);
  - 22 rejected by the scanner; breakdown:
      * 12 rejected_geometry_floor (small-magnitude excursions
        screened by the 81 bps fee-aware floor; same failure mode
        as the original)
      *  0 invalid stop geometry, 0 no_evaluation_bar
      * 10 rejected_entry_bar_close_at_or_below_trigger_bar_low
        (NEW failure mode at the relaxed threshold; entry bars
        continued through the trigger low, structurally falsifying
        the asymmetry thesis on those bars; the entry-bar
        invalidation gate correctly filtered these out as the
        edge argument designed it to);
  - identity check 1: 5 + 22 = 27 (accepted-pre + rejected =
    attempts);
  - identity check 2: 5 + 0 = 5 (accepted-post + drops =
    accepted-pre);
  - SAMPLE-SIZE ADEQUACY STRUCTURALLY STILL FAILED:
    5 accepted-post < 20 threshold;
    sample_size_still_below_threshold_after_edited_detection = True;
    post_edit_auto_rejection_trigger_fired = True;
    `sample_size_still_below_threshold_after_edited_detection` is
    one of the 12 post-edit auto-rejection triggers frozen in the
    pushed C9 single-edit decision -- it has FIRED, so Candidate
    #9 satisfies the auto-rejection condition for the next HUMAN
    DECISION gate;
  - anti-cluster gap (8) remains proposal-level locked and was NOT
    spent as the edit token;
  - sample-size adequacy threshold (20) remains proposal-level
    locked and was NOT spent as the edit token;
  - explicit-edge-argument field remains proposal-level locked and
    was NOT spent as the edit token;
  - edit token state: 1 used (on DOWNSIDE_Z_SCORE_THRESHOLD only,
    -2.0 -> -1.5), 0 remaining, no second edit allowed;
  - replay_executed_now: False; pnl_computed: False;
  - the original (pre-edit) C9 labels review at the prior committed
    SHA-pins remains unchanged.

EVIDENCE LANGUAGE ONLY. NO edge has been demonstrated. NO
profitability is claimed. The honest finding is that on the
2026-05-02_2026-06-10 BTCUSD 15m window, the relaxed z-score
threshold expanded triggers from 8 to 27 (3.4x, matching the
predicted lower-tail expansion), but accepted-post-anti-cluster
setups only grew from 1 to 5 -- still WELL BELOW the proposal/
spec-locked sample-size adequacy threshold of 20. The joint trigger
remains structurally rare even at the relaxed threshold: the volume
condition (the structural microstructure edge) is the binding
constraint, not the z-score. Additionally, 10 of the new triggers
were structurally falsified at the entry-bar invalidation gate
(panic continued, asymmetry thesis fails on those bars). The C9
hypothesis's edge argument was empirically CORRECT about thin-book
panic excursions being rare; the data on this 40-day sample does
not support C9 producing enough qualifying events to be evaluable.
The single C9 edit token is now spent permanently; no further edits
are allowed. The next HUMAN DECISION is to formalize the C9
rejection as the 9th ledger entry and extend V4 -> V5 blacklist
with `low_volume_downside_capitulation_mean_reversion` (mirroring
the C7 path).

This module observes the UNTRACKED edited artifacts READ-ONLY,
recounts acceptance and drop totals from the edited labels JSON
itself, re-verifies the two staged-source SHA-256 pins, verifies
the edited summary's self-claimed flags, and certifies every frozen
fact. It runs nothing, fetches nothing, modifies nothing, and
authorizes nothing.

Chain-gated live on: the pushed eight-record rejection ledger
(C1-C8), the pushed C9 family proposal, the pushed C9 spec review,
the pushed C9 detector spec + dry-run path, the pushed C9 dry-run
review, the pushed C9 ORIGINAL real-candle labels review (the
motivation for the edit), the pushed C9 single-edit decision (the
edit being verified here), the pushed V4 rejected-family blacklist,
the pushed V3 blacklist, the pushed Overnight Research Autopilot
V2, the pushed Recommendation V1, and the pushed Autopilot Loop V1.
"""

from __future__ import annotations

import hashlib as _hashlib
import json as _json
import pathlib as _pathlib
from typing import Any

import sparta_commander.strategy_factory_autopilot_research_loop_v1_contract as _loop
import sparta_commander.strategy_factory_candidate_recommendation_v1_contract as _rec
from sparta_commander.btc_sol_long_trend_continuation_v1_result_and_rejection_record_contract import (
    REJECTION_STATUS as C3_STATUS,
)
from sparta_commander.crypto_intraday_breakout_pullback_structure_v2_result_and_rejection_record_contract import (
    REJECTION_STATUS as C2_STATUS,
)
from sparta_commander.eth_sol_relative_strength_rejection_record_contract import (
    REJECTION_STATUS as C5_STATUS,
)
from sparta_commander.liquidity_sweep_mean_reversion_v1_rejection_record import (
    REJECTION_STATUS as C8_STATUS,
)
from sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_detector_spec_dry_run_contract import (
    VERDICT_C9D_READY,
    build_candidate_9_detector_spec_contract,
)
from sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_dry_run_review_contract import (
    VERDICT_C9R_FROZEN,
    build_candidate_9_dry_run_review,
)
from sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_family_proposal_contract import (
    CANDIDATE_FAMILY,
    CANDIDATE_ID,
    VERDICT_C9P_READY,
    build_candidate_9_family_proposal,
)
from sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_real_candle_labels_review_contract import (
    EXPECTED_LABELS_SHA256 as ORIGINAL_LABELS_SHA256,
    EXPECTED_SUMMARY_SHA256 as ORIGINAL_SUMMARY_SHA256,
    VERDICT_C9L_FROZEN,
    build_c9_labels_review,
)
from sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_single_edit_relaxed_z_score_decision_contract import (
    EDIT_PARAMETER_NAME,
    EDIT_PARAMETER_NEW_VALUE,
    EDIT_PARAMETER_OLD_VALUE,
    VERDICT_C9E_APPROVED,
    build_c9_single_edit_relaxed_z_score,
)
from sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_spec_review_contract import (
    VERDICT_C9S_READY,
    build_candidate_9_spec_review,
)
from sparta_commander.multi_symbol_relative_strength_rotation_filter_rejection_record_contract import (
    REJECTION_STATUS as C6_STATUS,
)
from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
    REJECTION_STATUS as C1_STATUS,
)
from sparta_commander.sol_btc_long_1h_swing_structure_rejection_record_contract import (
    REJECTION_STATUS as C4_STATUS,
)
from sparta_commander.strategy_factory_overnight_research_autopilot_v2_contract import (
    VERDICT_OAP2_READY,
    build_overnight_research_autopilot_v2_contract,
)
from sparta_commander.strategy_factory_rejected_family_blacklist_v3_contract import (
    VERDICT_BL3_READY,
    build_rejected_family_blacklist_v3,
)
from sparta_commander.strategy_factory_rejected_family_blacklist_v4_contract import (
    VERDICT_BL4_READY,
    build_rejected_family_blacklist_v4,
)
from sparta_commander.volatility_compression_expansion_v1_rejection_record import (
    REJECTION_STATUS as C7_STATUS,
)

C9EL_SCHEMA_VERSION = (
    "low_volume_downside_capitulation_mean_reversion_v1_edited"
    "_real_candle_labels_review.v1")
C9EL_LABEL = ("SPARTA Candidate #9 EDITED Real-Candle Labels "
              "Review / Evidence Freeze (READ-ONLY, RESEARCH ONLY, "
              "5 ACCEPTED POST ANTI-CLUSTER, POST-EDIT "
              "SAMPLE-SIZE STILL FAILED, POST-EDIT AUTO-REJECTION "
              "TRIGGER FIRED, NOT A PROFITABILITY CLAIM, NOT A "
              "RESCUE)")
C9EL_MODE = "RESEARCH_ONLY"
VERDICT_C9EL_FROZEN = (
    "CANDIDATE_9_EDITED_REAL_CANDLE_LABELS_REVIEW_FROZEN")
VERDICT_C9EL_REJECTED = (
    "CANDIDATE_9_EDITED_REAL_CANDLE_LABELS_REVIEW_REJECTED")
VERDICT_C9EL_BLOCKED = (
    "CANDIDATE_9_EDITED_REAL_CANDLE_LABELS_REVIEW_BLOCKED")
NEXT_REQUIRED_ACTION = (
    "HUMAN_DECISION_C9_REJECT_AFTER_EDIT_DID_NOT_RESOLVE_SAMPLE"
    "_SIZE_INADEQUACY")
CURRENT_LOOP_STAGE = "detector_and_label_review"

HEAD_AT_EDITED_DETECTION = (
    "6e88a827be09ab24b062c47aa4d1e313c39e3dfb")
EDITED_RUNNER_PATH = (
    "tools/c9_edited_real_candle_detection_relaxed_z_once.py")
EDITED_LABELS_PATH = (
    "data/low_volume_capitulation_c9/edited_detector_labels/"
    "c9_edited_detector_labels_relaxed_z_2026-05-02_2026-06-10.json")
EDITED_SUMMARY_PATH = (
    "data/low_volume_capitulation_c9/edited_detector_labels/"
    "c9_edited_detector_summary_relaxed_z_2026-05-02_2026-06-10.json")
EXPECTED_EDITED_LABELS_SHA256 = (
    "6e4f89821547cb89bb94b58a3c6dfcaac486af278aba6cf47171f72e359d3474")
EXPECTED_EDITED_SUMMARY_SHA256 = (
    "f689920b512587386538d83045ef3208ae8db7577abd6b0e79197f5cfafc53dc")

EXPECTED_STAGED_SHAS = {
    "data/ny_fvg_choch/staged/BTCUSD_15m_2026-05-02_2026-06-09.csv":
        "4ee373b28caeafa47d463e0fc2582f1958b877a8f05df0714a0afd"
        "1298ee9f14",
    "data/ny_fvg_choch/staged/BTCUSD_15m_2026-06-01_2026-06-10.csv":
        "4bb50873df5194de65315bf44f1823d17922e445745401eb01aa16"
        "70aed4956d",
}

EXPECTED_SAMPLE_TAG = "2026-05-02_2026-06-10"
EXPECTED_START_INCLUSIVE_UTC = "2026-05-02T00:00:00Z"
EXPECTED_END_INCLUSIVE_UTC = "2026-06-10T23:45:00Z"
EXPECTED_BARS_SCANNED = 3840
EXPECTED_FIRST_BAR_TIME = "2026-05-02T00:00:00Z"
EXPECTED_LAST_BAR_TIME = "2026-06-10T23:45:00Z"

# Edited (post-edit) counts
EXPECTED_TOTAL_ATTEMPTS = 27
EXPECTED_ACCEPTED_PRE_ANTI_CLUSTER = 5
EXPECTED_ACCEPTED_POST_ANTI_CLUSTER = 5
EXPECTED_REJECTED_BY_SCANNER = 22
EXPECTED_DROPPED_BY_ANTI_CLUSTER = 0

EXPECTED_STATUS_BREAKDOWN = {
    "accepted_for_replay_review": 5,
    "rejected_geometry_floor": 12,
    "rejected_entry_bar_close_at_or_below_trigger_bar_low": 10,
}

EXPECTED_IDENTITY_CHECKS = {
    "accepted_pre_plus_rejected_equals_attempts":
        EXPECTED_ACCEPTED_PRE_ANTI_CLUSTER
        + EXPECTED_REJECTED_BY_SCANNER == EXPECTED_TOTAL_ATTEMPTS,
    "accepted_post_plus_dropped_equals_accepted_pre":
        EXPECTED_ACCEPTED_POST_ANTI_CLUSTER
        + EXPECTED_DROPPED_BY_ANTI_CLUSTER
        == EXPECTED_ACCEPTED_PRE_ANTI_CLUSTER,
}

EXPECTED_SAMPLE_SIZE_ADEQUACY = {
    "accepted_count": 5,
    "minimum_required_at_labels_review_gate": 20,
    "below_minimum_at_dry_run": True,
    "enforced_at_labels_review_gate_only": True,
    "does_not_consume_edit_token": True,
}
EXPECTED_SAMPLE_SIZE_SATISFIED = False
EXPECTED_SAMPLE_SIZE_STILL_BELOW_THRESHOLD_AFTER_EDITED_DETECTION = (
    True)
EXPECTED_POST_EDIT_AUTO_REJECTION_TRIGGER_FIRED = True
EXPECTED_POST_EDIT_AUTO_REJECTION_TRIGGER_NAME = (
    "sample_size_still_below_threshold_after_edited_detection")

EXPECTED_ANTI_CLUSTER_FACTS = {
    "anti_cluster_min_bar_gap": 8,
    "tie_breaker": "keep_the_earlier_event_drop_the_later_one",
    "anti_cluster_does_not_consume_edit_token": True,
    "accepted_before_anti_cluster": 5,
    "accepted_after_anti_cluster": 5,
    "dropped_by_anti_cluster": 0,
}

EXPECTED_EDIT_STATE_CARRIED_FORWARD = {
    "edit_parameter": EDIT_PARAMETER_NAME,
    "original_value_signed": -2.0,
    "edited_value_signed": -1.5,
    "original_abs": 2.0,
    "edited_abs": 1.5,
    "edit_token_used": 1,
    "edits_remaining_after_this": 0,
    "no_second_edit_applied": True,
    "is_single_controlled_relaxation": True,
    "is_a_rescue_bundle": False,
    "all_other_c9_parameters_unchanged": True,
    "single_edit_decision_head": HEAD_AT_EDITED_DETECTION,
    "anti_cluster_did_not_consume_edit_token": True,
    "sample_size_did_not_consume_edit_token": True,
    "explicit_edge_argument_field_did_not_consume_edit_token": True,
    "original_c9_labels_review_sha_pins_unchanged": True,
}

EXPECTED_ORIGINAL_LABELS_SHA_PINS_CARRIED_FORWARD = {
    "original_labels_sha256": ORIGINAL_LABELS_SHA256,
    "original_summary_sha256": ORIGINAL_SUMMARY_SHA256,
}

EXPECTED_SUMMARY_SELF_CLAIMS = {
    "candidate_id": "LOW_VOLUME_DOWNSIDE_CAPITULATION_MEAN"
                    "_REVERSION_V1",
    "candidate_family": "low_volume_downside_capitulation_mean"
                        "_reversion",
    "symbol": "BTCUSD",
    "timeframe": "15m",
    "direction": "long_only",
    "sample_tag": EXPECTED_SAMPLE_TAG,
    "start_inclusive_utc": EXPECTED_START_INCLUSIVE_UTC,
    "end_inclusive_utc": EXPECTED_END_INCLUSIVE_UTC,
    "bars_scanned": EXPECTED_BARS_SCANNED,
    "first_bar_time_utc": EXPECTED_FIRST_BAR_TIME,
    "last_bar_time_utc": EXPECTED_LAST_BAR_TIME,
    "attempts": EXPECTED_TOTAL_ATTEMPTS,
    "accepted_pre_anti_cluster": EXPECTED_ACCEPTED_PRE_ANTI_CLUSTER,
    "accepted_post_anti_cluster":
        EXPECTED_ACCEPTED_POST_ANTI_CLUSTER,
    "rejected": EXPECTED_REJECTED_BY_SCANNER,
    "anti_cluster_drops": EXPECTED_DROPPED_BY_ANTI_CLUSTER,
    "anti_cluster_min_bar_gap": 8,
    "anti_cluster_does_not_consume_edit_token": True,
    "source_unchanged_during_detection": True,
}

EXPECTED_SCOPE_LOCKS = {
    "no_second_edit": True, "no_replay": True,
    "no_relabel": True, "no_pnl": True,
    "no_fetch": True, "no_network": True, "no_api": True,
    "no_credentials": True, "no_broker": True,
    "no_exchange": True, "no_wallet": True,
    "no_scheduler": True, "no_paper_trading": True,
    "no_micro_live": True, "no_live_trading": True,
    "no_downstream_gates_unlocked": True,
    "anti_cluster_did_not_consume_edit_token": True,
    "sample_size_did_not_consume_edit_token": True,
    "explicit_edge_argument_field_unchanged": True,
}

FROZEN_EDITED_DETECTION_FACTS = (
    "single-symbol btcusd 15m, long-only labels-only research",
    "existing staged btcusd 15m data only; no fetch",
    "3840 staged btcusd 15m bars covering the closed window "
    "2026-05-02T00:00:00Z..2026-06-10T23:45:00Z; same coverage as "
    "the original c9 detection",
    "scanner skips bars below ROLLING_WINDOW_BARS + 1 = 97",
    "the SINGLE c9 edit token applied: DOWNSIDE_Z_SCORE_THRESHOLD "
    "changed from -2.0 to -1.5; all other c9 numerics and rules "
    "remain unchanged",
    "27 joint-trigger attempts (vs 8 original); a 3.4x increase, "
    "matching the predicted normal-distribution lower-tail "
    "expansion from ~2.3% (at -2.0sigma) to ~6.7% (at -1.5sigma)",
    "5 accepted before anti-cluster; 5 accepted after anti-cluster",
    "22 rejected by scanner: 12 on geometry_floor (small "
    "excursions screened by the 81 bps fee-aware floor; same "
    "failure mode as original) and 10 on a NEW failure mode that "
    "did not appear in the original: rejected_entry_bar_close_at"
    "_or_below_trigger_bar_low (entry bars continued through the "
    "trigger low, structurally falsifying the asymmetry thesis on "
    "those bars; the entry-bar invalidation gate correctly "
    "filtered these out as the edge argument designed it to)",
    "0 dropped by 8-bar anti-cluster (the 5 accepted events are "
    "spread over the sample window with gaps >= 8 bars; nothing "
    "to drop)",
    "5 + 22 = 27 (accepted-pre + rejected = attempts)",
    "5 + 0 = 5 (accepted-post + drops = accepted-pre)",
    "SAMPLE-SIZE ADEQUACY STRUCTURALLY STILL FAILED: 5 accepted-"
    "post < 20 threshold; the relaxed z threshold expanded "
    "triggers 3.4x but accepted setups only grew from 1 to 5; the "
    "joint condition's volume gate (the structural microstructure "
    "edge) remains the binding constraint, not the z-score",
    "POST-EDIT AUTO-REJECTION TRIGGER FIRED: "
    "`sample_size_still_below_threshold_after_edited_detection` "
    "is one of the 12 post-edit auto-rejection triggers frozen in "
    "the pushed C9 single-edit decision at commit 6e88a827; it has "
    "FIRED, so Candidate #9 satisfies the auto-rejection "
    "condition for the next human decision gate",
    "anti-cluster gap remains proposal-level locked at 8 bars and "
    "does NOT consume the single c9 edit token (which was spent "
    "on the z-score threshold)",
    "sample-size adequacy threshold remains proposal-level locked "
    "at 20 accepted setups and does NOT consume the single c9 "
    "edit token",
    "explicit-edge-argument field remains proposal/spec-level "
    "locked and does NOT consume the single c9 edit token",
    "edit token state: 1 used (on DOWNSIDE_Z_SCORE_THRESHOLD "
    "only), 0 remaining, no second edit allowed; the original "
    "(pre-edit) c9 labels review SHA pins remain unchanged on "
    "origin/master",
    "no replay; no pnl; no relabel; no further edit allowed",
    "no profitability claim, no winner wording, no paper/live "
    "approval; the empirical finding confirms the c9 edge "
    "argument's prediction that thin-book panic excursions are "
    "rare, but the family does not produce enough qualifying "
    "events on this sample to be evaluable",
)

CLAIM_LOCKS = (
    "no_profitability_claim",
    "no_paper_approval",
    "no_live_approval",
    "no_execution_approval",
    "no_winner_wording",
    "no_replay_authorized_by_this_gate",
    "no_relabel_authorized_by_this_gate",
    "no_second_edit_applied_by_this_gate",
    "no_rejection_decision_made_by_this_gate",
    "anti_cluster_gap_remains_proposal_level_locked",
    "sample_size_threshold_remains_proposal_level_locked",
    "explicit_edge_argument_field_remains_proposal_level_locked",
    "edit_token_already_spent_no_further_edits_allowed",
    "post_edit_auto_rejection_trigger_fired_recorded_only_human"
    "_must_authorize_rejection_record",
)


def get_candidate_9_edited_labels_review_label() -> str:
    return C9EL_LABEL


def observe_c9_edited_labels(repo_root: Any,
                             tracked_paths: Any = ()
                             ) -> dict[str, Any]:
    """Read the untracked edited artifacts READ-ONLY and recount the
    facts. Never raises on missing files; reports absence instead."""
    observation: dict[str, Any] = {
        "edited_labels_exists": False,
        "edited_summary_exists": False,
        "edited_labels_sha256": None,
        "edited_summary_sha256": None,
        "edited_labels_accepted_post_count": None,
        "edited_labels_dropped_count": None,
        "edited_labels_all_accepted_symbol_btcusd": None,
        "edited_labels_all_accepted_timeframe_15m": None,
        "edited_labels_all_accepted_direction_long_only": None,
        "edited_labels_all_accepted_status_accepted_for_replay"
        "_review": None,
        "edited_labels_anti_cluster_min_bar_gap": None,
        "edited_labels_anti_cluster_does_not_consume_edit_token":
            None,
        "edited_labels_sample_size_adequacy": None,
        "edited_labels_scope_locks": None,
        "edited_labels_source_unchanged_during_detection": None,
        "edited_labels_edit_state": None,
        "edited_summary_candidate_id": None,
        "edited_summary_candidate_family": None,
        "edited_summary_symbol": None,
        "edited_summary_timeframe": None,
        "edited_summary_direction": None,
        "edited_summary_sample_tag": None,
        "edited_summary_start_inclusive_utc": None,
        "edited_summary_end_inclusive_utc": None,
        "edited_summary_bars_scanned": None,
        "edited_summary_first_bar_time_utc": None,
        "edited_summary_last_bar_time_utc": None,
        "edited_summary_attempts": None,
        "edited_summary_accepted_pre_anti_cluster": None,
        "edited_summary_accepted_post_anti_cluster": None,
        "edited_summary_rejected": None,
        "edited_summary_anti_cluster_drops": None,
        "edited_summary_status_breakdown": None,
        "edited_summary_anti_cluster_min_bar_gap": None,
        "edited_summary_anti_cluster_does_not_consume_edit_token":
            None,
        "edited_summary_sample_size_adequacy": None,
        "edited_summary_scope_locks": None,
        "edited_summary_source_unchanged_during_detection": None,
        "edited_summary_labels_sha256_self_reported": None,
        "edited_summary_edit_state": None,
        "staged_shas_now": None,
        "staged_shas_match": None,
        "artifacts_tracked_in_git": [],
    }
    root = _pathlib.Path(str(repo_root))
    tracked = {str(p).replace("\\", "/")
               for p in (tracked_paths or ())}
    for rel in (EDITED_LABELS_PATH, EDITED_SUMMARY_PATH,
                EDITED_RUNNER_PATH):
        if rel in tracked:
            observation["artifacts_tracked_in_git"].append(rel)
    staged_now: dict[str, Any] = {}
    for rel in EXPECTED_STAGED_SHAS:
        target = root / rel
        staged_now[rel] = (_hashlib.sha256(
            target.read_bytes()).hexdigest()
            if target.is_file() else None)
    observation["staged_shas_now"] = staged_now
    observation["staged_shas_match"] = (
        staged_now == EXPECTED_STAGED_SHAS)
    summary_file = root / EDITED_SUMMARY_PATH
    labels_file = root / EDITED_LABELS_PATH
    if summary_file.is_file():
        observation["edited_summary_exists"] = True
        raw_summary = summary_file.read_bytes()
        observation["edited_summary_sha256"] = _hashlib.sha256(
            raw_summary).hexdigest()
        summary = _json.loads(raw_summary.decode("utf-8"))
        for src_key, dst_key in (
                ("candidate_id", "edited_summary_candidate_id"),
                ("candidate_family",
                 "edited_summary_candidate_family"),
                ("symbol", "edited_summary_symbol"),
                ("timeframe", "edited_summary_timeframe"),
                ("direction", "edited_summary_direction"),
                ("sample_tag", "edited_summary_sample_tag"),
                ("start_inclusive_utc",
                 "edited_summary_start_inclusive_utc"),
                ("end_inclusive_utc",
                 "edited_summary_end_inclusive_utc"),
                ("bars_scanned", "edited_summary_bars_scanned"),
                ("first_bar_time_utc",
                 "edited_summary_first_bar_time_utc"),
                ("last_bar_time_utc",
                 "edited_summary_last_bar_time_utc"),
                ("attempts", "edited_summary_attempts"),
                ("accepted_pre_anti_cluster",
                 "edited_summary_accepted_pre_anti_cluster"),
                ("accepted_post_anti_cluster",
                 "edited_summary_accepted_post_anti_cluster"),
                ("rejected", "edited_summary_rejected"),
                ("anti_cluster_drops",
                 "edited_summary_anti_cluster_drops"),
                ("status_breakdown",
                 "edited_summary_status_breakdown"),
                ("anti_cluster_min_bar_gap",
                 "edited_summary_anti_cluster_min_bar_gap"),
                ("anti_cluster_does_not_consume_edit_token",
                 "edited_summary_anti_cluster_does_not_consume"
                 "_edit_token"),
                ("sample_size_adequacy",
                 "edited_summary_sample_size_adequacy"),
                ("scope_locks", "edited_summary_scope_locks"),
                ("source_unchanged_during_detection",
                 "edited_summary_source_unchanged_during"
                 "_detection"),
                ("labels_sha256",
                 "edited_summary_labels_sha256_self_reported"),
                ("edit_state", "edited_summary_edit_state")):
            observation[dst_key] = summary.get(src_key)
    if not labels_file.is_file():
        return observation
    observation["edited_labels_exists"] = True
    raw_labels = labels_file.read_bytes()
    observation["edited_labels_sha256"] = _hashlib.sha256(
        raw_labels).hexdigest()
    labels = _json.loads(raw_labels.decode("utf-8"))
    accepted_post = labels.get(
        "accepted_setups_post_anti_cluster") or []
    dropped = labels.get("anti_cluster_dropped") or []
    observation["edited_labels_accepted_post_count"] = len(
        accepted_post)
    observation["edited_labels_dropped_count"] = len(dropped)
    observation["edited_labels_all_accepted_symbol_btcusd"] = all(
        s.get("symbol") == "BTCUSD" for s in accepted_post)
    observation["edited_labels_all_accepted_timeframe_15m"] = all(
        s.get("timeframe") == "15m" for s in accepted_post)
    observation[
        "edited_labels_all_accepted_direction_long_only"] = all(
        s.get("direction") == "long_only" for s in accepted_post)
    observation[
        "edited_labels_all_accepted_status_accepted_for_replay"
        "_review"
    ] = all(
        s.get("status") == "accepted_for_replay_review"
        for s in accepted_post)
    observation["edited_labels_anti_cluster_min_bar_gap"] = (
        labels.get("anti_cluster_min_bar_gap"))
    observation[
        "edited_labels_anti_cluster_does_not_consume_edit_token"
    ] = labels.get("anti_cluster_does_not_consume_edit_token")
    observation["edited_labels_sample_size_adequacy"] = labels.get(
        "sample_size_adequacy")
    observation["edited_labels_scope_locks"] = labels.get(
        "scope_locks")
    observation[
        "edited_labels_source_unchanged_during_detection"] = (
        labels.get("source_unchanged_during_detection"))
    observation["edited_labels_edit_state"] = labels.get(
        "edit_state")
    return observation


def certify_c9_edited_labels_review(
        observation: Any) -> dict[str, Any]:
    """Pure certification of an observation against the frozen
    facts. Never raises."""
    failures: list[str] = []
    if not isinstance(observation, dict):
        return {"certified": False,
                "failures": ["observation_not_a_dict"]}
    o = observation
    if not o.get("edited_labels_exists"):
        failures.append("edited_labels_artifact_missing")
    if not o.get("edited_summary_exists"):
        failures.append("edited_summary_artifact_missing")
    if failures:
        return {"certified": False, "failures": failures}
    if o.get("edited_labels_sha256") != (
            EXPECTED_EDITED_LABELS_SHA256):
        failures.append("edited_labels_sha_mismatch")
    if o.get("edited_summary_sha256") != (
            EXPECTED_EDITED_SUMMARY_SHA256):
        failures.append("edited_summary_sha_mismatch")
    if o.get("edited_labels_accepted_post_count") != (
            EXPECTED_ACCEPTED_POST_ANTI_CLUSTER):
        failures.append(
            "edited_labels_accepted_post_count_must_equal_5")
    if o.get("edited_labels_dropped_count") != (
            EXPECTED_DROPPED_BY_ANTI_CLUSTER):
        failures.append("edited_labels_dropped_count_must_equal_0")
    if o.get("edited_labels_all_accepted_symbol_btcusd") is not True:
        failures.append("edited_accepted_setups_not_all_btcusd")
    if o.get("edited_labels_all_accepted_timeframe_15m") is not True:
        failures.append("edited_accepted_setups_not_all_15m")
    if o.get("edited_labels_all_accepted_direction_long_only"
             ) is not True:
        failures.append(
            "edited_accepted_setups_not_all_long_only")
    if o.get(
            "edited_labels_all_accepted_status_accepted_for_replay"
            "_review"
    ) is not True:
        failures.append(
            "edited_accepted_setups_not_all_accepted_for_replay"
            "_review")
    if o.get("edited_labels_anti_cluster_min_bar_gap") != 8:
        failures.append(
            "edited_labels_anti_cluster_min_bar_gap_must_be_8")
    if o.get(
            "edited_labels_anti_cluster_does_not_consume_edit"
            "_token") is not True:
        failures.append(
            "edited_labels_anti_cluster_must_not_consume_edit_token")
    if o.get("edited_labels_sample_size_adequacy") != (
            EXPECTED_SAMPLE_SIZE_ADEQUACY):
        failures.append(
            "edited_labels_sample_size_adequacy_mismatch")
    if o.get("edited_labels_scope_locks") != EXPECTED_SCOPE_LOCKS:
        failures.append("edited_labels_scope_locks_mismatch")
    if o.get(
            "edited_labels_source_unchanged_during_detection"
    ) is not True:
        failures.append(
            "edited_labels_source_unchanged_during_detection_must"
            "_be_true")
    # Edit state in labels
    edit_state_in_labels = o.get("edited_labels_edit_state") or {}
    if edit_state_in_labels.get("edit_parameter") != (
            "DOWNSIDE_Z_SCORE_THRESHOLD"):
        failures.append(
            "edited_labels_edit_parameter_must_be_z_threshold")
    if edit_state_in_labels.get("original_value_signed") != -2.0:
        failures.append(
            "edited_labels_edit_old_value_must_be_minus_2_0")
    if edit_state_in_labels.get("edited_value_signed") != -1.5:
        failures.append(
            "edited_labels_edit_new_value_must_be_minus_1_5")
    if edit_state_in_labels.get("edits_remaining_after_this") != 0:
        failures.append(
            "edited_labels_edit_remaining_must_be_0")
    if edit_state_in_labels.get("no_second_edit_applied") is not (
            True):
        failures.append(
            "edited_labels_no_second_edit_must_be_true")
    if edit_state_in_labels.get(
            "is_single_controlled_relaxation") is not True:
        failures.append(
            "edited_labels_must_be_single_controlled_relaxation")
    if edit_state_in_labels.get("is_a_rescue_bundle") is not False:
        failures.append(
            "edited_labels_must_not_be_a_rescue_bundle")
    if edit_state_in_labels.get(
            "all_other_c9_parameters_unchanged") is not True:
        failures.append(
            "edited_labels_other_c9_parameters_must_be_unchanged")
    # summary self-claims
    for key, want in EXPECTED_SUMMARY_SELF_CLAIMS.items():
        got = o.get("edited_summary_" + key)
        if got != want:
            failures.append(
                "edited_summary_claim_mismatch:" + key)
    if o.get("edited_summary_status_breakdown") != (
            EXPECTED_STATUS_BREAKDOWN):
        failures.append(
            "edited_summary_status_breakdown_mismatch")
    if o.get("edited_summary_sample_size_adequacy") != (
            EXPECTED_SAMPLE_SIZE_ADEQUACY):
        failures.append(
            "edited_summary_sample_size_adequacy_mismatch")
    if o.get("edited_summary_scope_locks") != EXPECTED_SCOPE_LOCKS:
        failures.append("edited_summary_scope_locks_mismatch")
    if o.get("edited_summary_labels_sha256_self_reported") != (
            EXPECTED_EDITED_LABELS_SHA256):
        failures.append(
            "edited_summary_labels_sha_self_report_mismatch")
    # Edit state in summary
    edit_state_in_summary = o.get(
        "edited_summary_edit_state") or {}
    if edit_state_in_summary.get("edit_parameter") != (
            "DOWNSIDE_Z_SCORE_THRESHOLD"):
        failures.append(
            "edited_summary_edit_parameter_must_be_z_threshold")
    if edit_state_in_summary.get("edited_value_signed") != -1.5:
        failures.append(
            "edited_summary_edit_new_value_must_be_minus_1_5")
    if o.get("staged_shas_match") is not True:
        failures.append("staged_data_shas_changed")
    if o.get("artifacts_tracked_in_git"):
        failures.append(
            "edited_runner_and_artifacts_must_stay_untracked")
    return {"certified": not failures, "failures": failures}


def build_c9_edited_labels_review(
        repo_root: Any, tracked_paths: Any = ()
) -> dict[str, Any]:
    """Observe read-only and certify; chain-gated on the full pushed
    C9 lane through the single-edit decision plus V4 + V3 + V2 +
    Recommendation V1 + Autopilot V1 + eight-record rejection
    ledger. The pushed ORIGINAL C9 labels review must still certify
    (its SHA pins remain unchanged on origin/master)."""
    record: dict[str, Any] = {
        "schema_version": C9EL_SCHEMA_VERSION, "label": C9EL_LABEL,
        "mode": C9EL_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [], "failures": [],
        "candidate_id": CANDIDATE_ID,
        "candidate_family": CANDIDATE_FAMILY,
        "head_at_edited_detection": HEAD_AT_EDITED_DETECTION,
        "edited_runner_path_untracked_only": EDITED_RUNNER_PATH,
        "edited_labels_path": EDITED_LABELS_PATH,
        "edited_summary_path": EDITED_SUMMARY_PATH,
        "expected_edited_labels_sha256":
            EXPECTED_EDITED_LABELS_SHA256,
        "expected_edited_summary_sha256":
            EXPECTED_EDITED_SUMMARY_SHA256,
        "expected_staged_shas": dict(EXPECTED_STAGED_SHAS),
        "expected_sample_tag": EXPECTED_SAMPLE_TAG,
        "expected_start_inclusive_utc": EXPECTED_START_INCLUSIVE_UTC,
        "expected_end_inclusive_utc": EXPECTED_END_INCLUSIVE_UTC,
        "expected_bars_scanned": EXPECTED_BARS_SCANNED,
        "expected_first_bar_time": EXPECTED_FIRST_BAR_TIME,
        "expected_last_bar_time": EXPECTED_LAST_BAR_TIME,
        "expected_total_attempts": EXPECTED_TOTAL_ATTEMPTS,
        "expected_accepted_pre_anti_cluster":
            EXPECTED_ACCEPTED_PRE_ANTI_CLUSTER,
        "expected_accepted_post_anti_cluster":
            EXPECTED_ACCEPTED_POST_ANTI_CLUSTER,
        "expected_rejected_by_scanner":
            EXPECTED_REJECTED_BY_SCANNER,
        "expected_dropped_by_anti_cluster":
            EXPECTED_DROPPED_BY_ANTI_CLUSTER,
        "expected_status_breakdown":
            dict(EXPECTED_STATUS_BREAKDOWN),
        "expected_identity_checks":
            dict(EXPECTED_IDENTITY_CHECKS),
        "expected_sample_size_adequacy":
            dict(EXPECTED_SAMPLE_SIZE_ADEQUACY),
        "expected_sample_size_satisfied":
            EXPECTED_SAMPLE_SIZE_SATISFIED,
        "expected_sample_size_still_below_threshold_after_edited"
        "_detection":
            EXPECTED_SAMPLE_SIZE_STILL_BELOW_THRESHOLD_AFTER_EDITED_DETECTION,
        "expected_post_edit_auto_rejection_trigger_fired":
            EXPECTED_POST_EDIT_AUTO_REJECTION_TRIGGER_FIRED,
        "expected_post_edit_auto_rejection_trigger_name":
            EXPECTED_POST_EDIT_AUTO_REJECTION_TRIGGER_NAME,
        "expected_anti_cluster_facts":
            dict(EXPECTED_ANTI_CLUSTER_FACTS),
        "expected_edit_state_carried_forward":
            dict(EXPECTED_EDIT_STATE_CARRIED_FORWARD),
        "expected_original_labels_sha_pins_carried_forward":
            dict(EXPECTED_ORIGINAL_LABELS_SHA_PINS_CARRIED_FORWARD),
        "expected_summary_self_claims":
            dict(EXPECTED_SUMMARY_SELF_CLAIMS),
        "expected_scope_locks": dict(EXPECTED_SCOPE_LOCKS),
        "frozen_edited_detection_facts":
            list(FROZEN_EDITED_DETECTION_FACTS),
        "claim_locks": list(CLAIM_LOCKS),
        "ledger_status_eight_records": None,
        "ledger_all_rejected_kept_on_record": None,
        "human_review_required": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True, "live_gate_locked": True,
        "is_edited_labels_review_only": True,
        "is_a_rescue_attempt": False,
        "is_a_rescue_bundle": False,
        "second_edit_applied_by_this_gate": False,
        "rejection_decision_made_by_this_gate": False,
        "replay_authorized_by_this_gate": False,
        "relabel_authorized_by_this_gate": False,
        "edit_token_remaining": 0,
        "no_further_c9_edits_allowed": True,
        "executes": False, "writes_files": False, "labels_now":
            False,
        "runs_real_candle_detection": False,
        "runs_edited_real_candle_detection": False,
        "runs_relabel": False, "runs_replay": False,
        "runs_real_detection_now": False, "runs_replay_now": False,
        "scores_now": False, "stages_data_now": False,
        "fetches_data": False, "calls_api": False, "uses_network": False,
        "uses_credentials": False, "uses_wallet": False,
        "uses_account": False, "connects_broker": False,
        "connects_exchange": False, "uses_real_money": False,
        "contains_order_logic": False,
        "contains_portfolio_allocation_logic": False,
        "starts_scheduler": False, "sends_notifications": False,
        "auto_commits": False, "auto_pushes": False,
        "creates_runners_now": False, "creates_data_artifacts_now":
            False,
        "creates_detector_implementation_now": False,
        "computes_pnl_now": False,
        "modifies_staged_market_data": False,
        "modifies_detector_artifacts": False,
        "modifies_labels_artifacts": False,
        "modifies_edited_labels_artifacts": False,
        "authorizes_paper_execution": False,
        "authorizes_micro_live": False, "authorizes_live_trading":
            False,
        "promotes_gate": False, "unlocks_downstream_gate": False,
        "unlocks_real_candle_detection": False,
        "unlocks_replay_now": False, "unlocks_relabel_now": False,
        "unlocks_edit_token_now": False,
        "claims_profitability": False,
        "next_required_action": NEXT_REQUIRED_ACTION,
        "current_loop_stage": CURRENT_LOOP_STAGE,
    }
    statuses = (C1_STATUS, C2_STATUS, C3_STATUS, C4_STATUS, C5_STATUS,
                C6_STATUS, C7_STATUS, C8_STATUS)
    record["ledger_status_eight_records"] = list(statuses)
    record["ledger_all_rejected_kept_on_record"] = all(
        s == "REJECTED_KEPT_ON_RECORD" for s in statuses)
    if not record["ledger_all_rejected_kept_on_record"]:
        record["verdict"] = VERDICT_C9EL_BLOCKED
        record["blockers"].append("eight_record_ledger_broken")
        return record
    if build_candidate_9_family_proposal()["verdict"] != (
            VERDICT_C9P_READY):
        record["verdict"] = VERDICT_C9EL_BLOCKED
        record["blockers"].append(
            "candidate_9_proposal_not_certifying")
        return record
    if build_candidate_9_spec_review()["verdict"] != VERDICT_C9S_READY:
        record["verdict"] = VERDICT_C9EL_BLOCKED
        record["blockers"].append(
            "candidate_9_spec_review_not_certifying")
        return record
    if build_candidate_9_detector_spec_contract()["verdict"] != (
            VERDICT_C9D_READY):
        record["verdict"] = VERDICT_C9EL_BLOCKED
        record["blockers"].append(
            "candidate_9_detector_spec_not_certifying")
        return record
    if build_candidate_9_dry_run_review()["verdict"] != (
            VERDICT_C9R_FROZEN):
        record["verdict"] = VERDICT_C9EL_BLOCKED
        record["blockers"].append(
            "candidate_9_dry_run_review_not_certifying")
        return record
    if build_c9_labels_review(repo_root, tracked_paths)[
            "verdict"] != VERDICT_C9L_FROZEN:
        record["verdict"] = VERDICT_C9EL_BLOCKED
        record["blockers"].append(
            "candidate_9_original_labels_review_not_certifying")
        return record
    if build_c9_single_edit_relaxed_z_score(
            repo_root, tracked_paths)["verdict"] != (
            VERDICT_C9E_APPROVED):
        record["verdict"] = VERDICT_C9EL_BLOCKED
        record["blockers"].append(
            "candidate_9_single_edit_decision_not_certifying")
        return record
    # The single-edit decision must show the z-score parameter
    if EDIT_PARAMETER_NAME != "DOWNSIDE_Z_SCORE_THRESHOLD" \
            or EDIT_PARAMETER_OLD_VALUE != -2.0 \
            or EDIT_PARAMETER_NEW_VALUE != -1.5:
        record["verdict"] = VERDICT_C9EL_BLOCKED
        record["blockers"].append(
            "single_edit_decision_parameter_or_values_drifted")
        return record
    if build_rejected_family_blacklist_v4()["verdict"] != (
            VERDICT_BL4_READY):
        record["verdict"] = VERDICT_C9EL_BLOCKED
        record["blockers"].append("v4_blacklist_not_certifying")
        return record
    if build_rejected_family_blacklist_v3()["verdict"] != (
            VERDICT_BL3_READY):
        record["verdict"] = VERDICT_C9EL_BLOCKED
        record["blockers"].append("v3_blacklist_not_certifying")
        return record
    if build_overnight_research_autopilot_v2_contract()["verdict"] != (
            VERDICT_OAP2_READY):
        record["verdict"] = VERDICT_C9EL_BLOCKED
        record["blockers"].append(
            "overnight_research_autopilot_v2_not_certifying")
        return record
    if _rec.build_candidate_recommendation()["verdict"] != (
            _rec.VERDICT_CR_READY):
        record["verdict"] = VERDICT_C9EL_BLOCKED
        record["blockers"].append("recommendation_not_certifying")
        return record
    if _loop.build_autopilot_loop_contract()["verdict"] != (
            _loop.VERDICT_AP_READY):
        record["verdict"] = VERDICT_C9EL_BLOCKED
        record["blockers"].append("autopilot_loop_not_certifying")
        return record
    observation = observe_c9_edited_labels(repo_root, tracked_paths)
    result = certify_c9_edited_labels_review(observation)
    record["failures"] = result["failures"]
    record["verdict"] = (VERDICT_C9EL_FROZEN if result["certified"]
                         else VERDICT_C9EL_REJECTED)
    return record


def validate_c9_edited_labels_review(record: Any) -> dict[str, Any]:
    """Validate shape, frozen facts, and safety invariants. Never
    raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_C9EL_FROZEN,
                                VERDICT_C9EL_REJECTED,
                                VERDICT_C9EL_BLOCKED):
        errors.append("bad_verdict")
    if r.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if r.get("candidate_family") != CANDIDATE_FAMILY:
        errors.append("candidate_family_tampered")
    if r.get("head_at_edited_detection") != HEAD_AT_EDITED_DETECTION:
        errors.append("head_tampered")
    if r.get("expected_edited_labels_sha256") != (
            EXPECTED_EDITED_LABELS_SHA256):
        errors.append("edited_labels_sha_tampered")
    if r.get("expected_edited_summary_sha256") != (
            EXPECTED_EDITED_SUMMARY_SHA256):
        errors.append("edited_summary_sha_tampered")
    if r.get("expected_staged_shas") != EXPECTED_STAGED_SHAS:
        errors.append("staged_shas_tampered")
    if r.get("expected_sample_tag") != EXPECTED_SAMPLE_TAG:
        errors.append("sample_tag_tampered")
    if r.get("expected_bars_scanned") != EXPECTED_BARS_SCANNED:
        errors.append("bars_scanned_tampered")
    if r.get("expected_total_attempts") != EXPECTED_TOTAL_ATTEMPTS:
        errors.append("total_attempts_tampered")
    if r.get("expected_accepted_pre_anti_cluster") != (
            EXPECTED_ACCEPTED_PRE_ANTI_CLUSTER):
        errors.append("accepted_pre_tampered")
    if r.get("expected_accepted_post_anti_cluster") != (
            EXPECTED_ACCEPTED_POST_ANTI_CLUSTER):
        errors.append("accepted_post_tampered")
    if r.get("expected_rejected_by_scanner") != (
            EXPECTED_REJECTED_BY_SCANNER):
        errors.append("rejected_count_tampered")
    if r.get("expected_dropped_by_anti_cluster") != (
            EXPECTED_DROPPED_BY_ANTI_CLUSTER):
        errors.append("anti_cluster_dropped_tampered")
    if r.get("expected_status_breakdown") != (
            EXPECTED_STATUS_BREAKDOWN):
        errors.append("status_breakdown_tampered")
    if r.get("expected_identity_checks") != EXPECTED_IDENTITY_CHECKS:
        errors.append("identity_checks_tampered")
    if r.get("expected_sample_size_adequacy") != (
            EXPECTED_SAMPLE_SIZE_ADEQUACY):
        errors.append("sample_size_adequacy_tampered")
    if r.get("expected_sample_size_satisfied") is not (
            EXPECTED_SAMPLE_SIZE_SATISFIED):
        errors.append("sample_size_satisfied_tampered")
    if r.get(
            "expected_sample_size_still_below_threshold_after_edited"
            "_detection") is not (
            EXPECTED_SAMPLE_SIZE_STILL_BELOW_THRESHOLD_AFTER_EDITED_DETECTION):
        errors.append(
            "sample_size_still_below_threshold_after_edited_tampered")
    if r.get("expected_post_edit_auto_rejection_trigger_fired"
             ) is not (
            EXPECTED_POST_EDIT_AUTO_REJECTION_TRIGGER_FIRED):
        errors.append(
            "post_edit_auto_rejection_trigger_fired_tampered")
    if r.get("expected_post_edit_auto_rejection_trigger_name") != (
            EXPECTED_POST_EDIT_AUTO_REJECTION_TRIGGER_NAME):
        errors.append(
            "post_edit_auto_rejection_trigger_name_tampered")
    if r.get("expected_anti_cluster_facts") != (
            EXPECTED_ANTI_CLUSTER_FACTS):
        errors.append("anti_cluster_facts_tampered")
    if r.get("expected_edit_state_carried_forward") != (
            EXPECTED_EDIT_STATE_CARRIED_FORWARD):
        errors.append("edit_state_carried_forward_tampered")
    if r.get(
            "expected_original_labels_sha_pins_carried_forward"
    ) != EXPECTED_ORIGINAL_LABELS_SHA_PINS_CARRIED_FORWARD:
        errors.append("original_labels_sha_pins_carried_forward"
                      "_tampered")
    if r.get("expected_summary_self_claims") != (
            EXPECTED_SUMMARY_SELF_CLAIMS):
        errors.append("summary_self_claims_tampered")
    if r.get("expected_scope_locks") != EXPECTED_SCOPE_LOCKS:
        errors.append("scope_locks_tampered")
    if tuple(r.get("frozen_edited_detection_facts") or ()) != (
            FROZEN_EDITED_DETECTION_FACTS):
        errors.append("frozen_edited_detection_facts_tampered")
    if tuple(r.get("claim_locks") or ()) != CLAIM_LOCKS:
        errors.append("claim_locks_tampered")
    if r.get("next_required_action") != NEXT_REQUIRED_ACTION:
        errors.append("next_required_action_tampered")
    if r.get("current_loop_stage") != CURRENT_LOOP_STAGE:
        errors.append("current_loop_stage_tampered")
    for key, want in (("human_review_required", True),
                      ("paper_trading_gate_locked", True),
                      ("micro_live_gate_locked", True),
                      ("live_gate_locked", True),
                      ("is_edited_labels_review_only", True),
                      ("is_a_rescue_attempt", False),
                      ("is_a_rescue_bundle", False),
                      ("edit_token_remaining", 0),
                      ("no_further_c9_edits_allowed", True)):
        if r.get(key) is not want:
            errors.append("constitution_flag_wrong:" + key)
    for key in ("second_edit_applied_by_this_gate",
                "rejection_decision_made_by_this_gate",
                "replay_authorized_by_this_gate",
                "relabel_authorized_by_this_gate"):
        if r.get(key) is not False:
            errors.append("downstream_lock_wrong:" + key)
    for key in ("executes", "writes_files", "labels_now",
                "runs_real_candle_detection",
                "runs_edited_real_candle_detection",
                "runs_relabel", "runs_replay",
                "runs_real_detection_now", "runs_replay_now",
                "scores_now", "stages_data_now", "fetches_data",
                "calls_api", "uses_network", "uses_credentials",
                "uses_wallet", "uses_account", "connects_broker",
                "connects_exchange", "uses_real_money",
                "contains_order_logic",
                "contains_portfolio_allocation_logic",
                "starts_scheduler", "sends_notifications",
                "auto_commits", "auto_pushes",
                "creates_runners_now",
                "creates_data_artifacts_now",
                "creates_detector_implementation_now",
                "computes_pnl_now",
                "modifies_staged_market_data",
                "modifies_detector_artifacts",
                "modifies_labels_artifacts",
                "modifies_edited_labels_artifacts",
                "authorizes_paper_execution",
                "authorizes_micro_live",
                "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate",
                "unlocks_real_candle_detection",
                "unlocks_replay_now", "unlocks_relabel_now",
                "unlocks_edit_token_now", "claims_profitability"):
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)
    if r.get("verdict") == VERDICT_C9EL_FROZEN and r.get(
            "failures"):
        errors.append("frozen_with_failures")
    return {"valid": not errors, "errors": errors}
