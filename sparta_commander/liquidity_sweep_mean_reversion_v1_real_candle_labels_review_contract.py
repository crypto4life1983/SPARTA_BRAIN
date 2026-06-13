"""SPARTA CANDIDATE #8 REAL-CANDLE DETECTOR LABELS REVIEW / EVIDENCE
FREEZE (READ-ONLY, RESEARCH ONLY, NOT A PROFITABILITY CLAIM):
LIQUIDITY_SWEEP_MEAN_REVERSION_V1.

Freezes the one-pass real-candle detection result on the staged
BTCUSD 15m data for the sample window 2026-05-02_2026-06-10 produced
by the untracked runner tools/c8_real_candle_detection_once.py:

  - 3,840 staged BTCUSD 15m bars scanned (closed window
    2026-05-02T00:00:00Z .. 2026-06-10T23:45:00Z);
  - 133 attempts (one per sweep event triggered);
  - 73 accepted setups before the proposal-level anti-cluster filter;
  - 51 accepted setups after the proposal-level anti-cluster filter;
  - 22 dropped by anti-cluster as clustered within 8 bars of a prior
    accepted event on the same symbol;
  - 60 rejected by the scanner; breakdown:
      * 57 rejected_no_qualifying_reclaim_within_4_bars
      *  3 rejected_geometry_floor
  - identity check 1: 73 + 60 = 133 (accepted-pre + rejected =
    attempts);
  - identity check 2: 51 + 22 = 73 (accepted-post + drops =
    accepted-pre);
  - sample-size adequacy: 51 accepted-post >= 20 threshold, so the
    proposal-locked sample-size adequacy check is SATISFIED; this
    does NOT consume the single C8 edit token;
  - anti-cluster: 8-bar min gap, keep-earlier-drop-later tie-breaker,
    and the policy does NOT consume the single C8 edit token;
  - replay_executed_now: False; pnl_computed: False;
  - single C8 edit token NOT applied.

EVIDENCE LANGUAGE ONLY. NO edge has been demonstrated. NO
profitability is claimed. The honest finding is that on the
2026-05-02_2026-06-10 BTCUSD 15m window the C8 scanner emitted 51
accepted-post-anti-cluster candidate setups; whether the per-setup
quality and the broader real-replay behaviour will support an edge
is the next-gate HUMAN decision. This module does NOT approve replay;
it only freezes the detection evidence and confirms the
sample-size-adequacy threshold was met without consuming the edit
token.

This module observes the UNTRACKED artifacts READ-ONLY, recounts
acceptance and drop totals from the labels JSON itself, re-verifies
the two staged-source SHA-256 pins, verifies the summary's
self-claimed flags, and certifies every frozen fact. It runs nothing,
fetches nothing, modifies nothing, and authorizes nothing.

Chain-gated live on: the pushed seven-record rejection ledger
(C1-C7), the pushed C8 family proposal, the pushed C8 spec review,
the pushed C8 detector spec + dry-run path, the pushed C8 dry-run
review, the pushed V3 rejected-family blacklist, the pushed Overnight
Research Autopilot V2, the pushed Recommendation V1, and the pushed
Autopilot Loop V1.
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
from sparta_commander.liquidity_sweep_mean_reversion_v1_detector_dry_run_review_contract import (
    VERDICT_C8R_FROZEN,
    build_candidate_8_dry_run_review,
)
from sparta_commander.liquidity_sweep_mean_reversion_v1_detector_spec_dry_run_contract import (
    VERDICT_C8D_READY,
    build_candidate_8_detector_spec_contract,
)
from sparta_commander.liquidity_sweep_mean_reversion_v1_family_proposal_contract import (
    CANDIDATE_FAMILY,
    CANDIDATE_ID,
    VERDICT_C8P_READY,
    build_candidate_8_family_proposal,
)
from sparta_commander.liquidity_sweep_mean_reversion_v1_spec_review_contract import (
    VERDICT_C8S_READY,
    build_candidate_8_spec_review,
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
from sparta_commander.volatility_compression_expansion_v1_rejection_record import (
    REJECTION_STATUS as C7_STATUS,
)

C8L_SCHEMA_VERSION = (
    "liquidity_sweep_mean_reversion_v1_real_candle_labels_review.v1")
C8L_LABEL = ("SPARTA Candidate #8 Real-Candle Labels Review / "
             "Evidence Freeze (READ-ONLY, RESEARCH ONLY, 51 ACCEPTED "
             "POST ANTI-CLUSTER, SAMPLE-SIZE ADEQUACY SATISFIED, "
             "NOT A PROFITABILITY CLAIM, NOT A RESCUE)")
C8L_MODE = "RESEARCH_ONLY"
VERDICT_C8L_FROZEN = (
    "CANDIDATE_8_REAL_CANDLE_LABELS_REVIEW_FROZEN")
VERDICT_C8L_REJECTED = (
    "CANDIDATE_8_REAL_CANDLE_LABELS_REVIEW_REJECTED")
VERDICT_C8L_BLOCKED = (
    "CANDIDATE_8_REAL_CANDLE_LABELS_REVIEW_BLOCKED")
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_CANDIDATE_8_REPLAY"
CURRENT_LOOP_STAGE = "detector_and_label_review"

HEAD_AT_DETECTION = "6d62f936e135cedc5317edf92cb875de31333215"
RUNNER_PATH = "tools/c8_real_candle_detection_once.py"
LABELS_PATH = ("data/liquidity_sweep_c8/detector_labels/"
               "c8_detector_labels_2026-05-02_2026-06-10.json")
SUMMARY_PATH = ("data/liquidity_sweep_c8/detector_labels/"
                "c8_detector_summary_2026-05-02_2026-06-10.json")
EXPECTED_LABELS_SHA256 = (
    "f323ff7188b672a9af2521e30d3b7a4052217d86c7bbb0f8c0e86405cb81fee3")
EXPECTED_SUMMARY_SHA256 = (
    "d1655123990b0080ef741bda49ea5baa20d6640c4b2d4476986f29deb2e4ae90")

EXPECTED_STAGED_SHAS = {
    "data/ny_fvg_choch/staged/BTCUSD_15m_2026-05-02_2026-06-09.csv":
        "4ee373b28caeafa47d463e0fc2582f1958b877a8f05df0714a0afd1298ee"
        "9f14",
    "data/ny_fvg_choch/staged/BTCUSD_15m_2026-06-01_2026-06-10.csv":
        "4bb50873df5194de65315bf44f1823d17922e445745401eb01aa1670aed4"
        "956d",
}

EXPECTED_SAMPLE_TAG = "2026-05-02_2026-06-10"
EXPECTED_START_INCLUSIVE_UTC = "2026-05-02T00:00:00Z"
EXPECTED_END_INCLUSIVE_UTC = "2026-06-10T23:45:00Z"
EXPECTED_BARS_SCANNED = 3840
EXPECTED_FIRST_BAR_TIME = "2026-05-02T00:00:00Z"
EXPECTED_LAST_BAR_TIME = "2026-06-10T23:45:00Z"

EXPECTED_TOTAL_ATTEMPTS = 133
EXPECTED_ACCEPTED_PRE_ANTI_CLUSTER = 73
EXPECTED_ACCEPTED_POST_ANTI_CLUSTER = 51
EXPECTED_REJECTED_BY_SCANNER = 60
EXPECTED_DROPPED_BY_ANTI_CLUSTER = 22

EXPECTED_STATUS_BREAKDOWN = {
    "accepted_for_replay_review": 73,
    "rejected_no_qualifying_reclaim_within_4_bars": 57,
    "rejected_geometry_floor": 3,
    "rejected_clustered_within_8_bars_of_prior_accepted": 22,
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
    "accepted_count": 51,
    "minimum_required_at_labels_review_gate": 20,
    "below_minimum_at_dry_run": False,
    "enforced_at_labels_review_gate_only": True,
    "does_not_consume_edit_token": True,
}
EXPECTED_SAMPLE_SIZE_SATISFIED = True

EXPECTED_ANTI_CLUSTER_FACTS = {
    "anti_cluster_min_bar_gap": 8,
    "tie_breaker": "keep_the_earlier_event_drop_the_later_one",
    "anti_cluster_does_not_consume_edit_token": True,
    "accepted_before_anti_cluster": 73,
    "accepted_after_anti_cluster": 51,
    "dropped_by_anti_cluster": 22,
}

EXPECTED_SUMMARY_SELF_CLAIMS = {
    "candidate_id": "LIQUIDITY_SWEEP_MEAN_REVERSION_V1",
    "candidate_family": "liquidity_sweep_mean_reversion",
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
    "no_replay": True, "no_relabel": True, "no_pnl": True,
    "no_fetch": True, "no_network": True, "no_api": True,
    "no_credentials": True, "no_broker": True,
    "no_exchange": True, "no_wallet": True,
    "no_scheduler": True, "no_paper_trading": True,
    "no_micro_live": True, "no_live_trading": True,
    "no_edit_token_consumed": True,
    "no_downstream_gates_unlocked": True,
}

FROZEN_DETECTION_FACTS = (
    "single-symbol btcusd 15m, long-only labels-only research",
    "existing staged btcusd 15m data only; no fetch",
    "3840 staged btcusd 15m bars covering the closed window "
    "2026-05-02T00:00:00Z..2026-06-10T23:45:00Z; no gaps",
    "scanner skips bars below RANGE_SWING_LOW_LOOKBACK_BARS (96)",
    "133 attempts triggered by sweep events whose low strictly "
    "exceeded the proposal-locked 0.25 x ATR(14) penetration below "
    "the 96-bar reference low",
    "73 accepted before anti-cluster; 51 accepted after anti-cluster",
    "60 rejected by scanner: 57 on no_qualifying_reclaim_within_4"
    "_bars, 3 on geometry_floor",
    "22 dropped by 8-bar anti-cluster as clustered within 8 bars of "
    "a prior accepted event on the same symbol",
    "73 + 60 = 133 (accepted-pre + rejected = attempts)",
    "51 + 22 = 73 (accepted-post + drops = accepted-pre)",
    "sample-size adequacy SATISFIED: 51 >= 20 minimum at labels-"
    "review gate",
    "anti-cluster gap remains proposal-level locked and does NOT "
    "consume the single c8 edit token",
    "sample-size adequacy threshold remains proposal-level locked "
    "and does NOT consume the single c8 edit token",
    "no replay; no pnl; no relabel; no edit token applied",
    "no profitability claim, no winner wording, no paper/live "
    "approval",
)

CLAIM_LOCKS = (
    "no_profitability_claim",
    "no_paper_approval",
    "no_live_approval",
    "no_execution_approval",
    "no_winner_wording",
    "no_replay_authorized_by_this_gate",
    "no_relabel_authorized_by_this_gate",
    "no_edit_token_applied_by_this_gate",
    "no_rejection_decision_made_by_this_gate",
    "anti_cluster_gap_remains_proposal_level_locked",
    "sample_size_threshold_remains_proposal_level_locked",
)


def get_candidate_8_labels_review_label() -> str:
    return C8L_LABEL


def observe_c8_labels(repo_root: Any,
                      tracked_paths: Any = ()
                      ) -> dict[str, Any]:
    """Read the untracked artifacts READ-ONLY and recount the facts.
    Never raises on missing files; reports absence instead."""
    observation: dict[str, Any] = {
        "labels_exists": False, "summary_exists": False,
        "labels_sha256": None, "summary_sha256": None,
        "labels_accepted_post_count": None,
        "labels_dropped_count": None,
        "labels_all_accepted_symbol_btcusd": None,
        "labels_all_accepted_timeframe_15m": None,
        "labels_all_accepted_direction_long_only": None,
        "labels_all_accepted_status_accepted_for_replay_review": None,
        "labels_all_dropped_status_clustered": None,
        "labels_anti_cluster_min_bar_gap": None,
        "labels_anti_cluster_does_not_consume_edit_token": None,
        "labels_sample_size_adequacy": None,
        "labels_scope_locks": None,
        "labels_source_unchanged_during_detection": None,
        "summary_candidate_id": None,
        "summary_candidate_family": None,
        "summary_symbol": None,
        "summary_timeframe": None,
        "summary_direction": None,
        "summary_sample_tag": None,
        "summary_start_inclusive_utc": None,
        "summary_end_inclusive_utc": None,
        "summary_bars_scanned": None,
        "summary_first_bar_time_utc": None,
        "summary_last_bar_time_utc": None,
        "summary_attempts": None,
        "summary_accepted_pre_anti_cluster": None,
        "summary_accepted_post_anti_cluster": None,
        "summary_rejected": None,
        "summary_anti_cluster_drops": None,
        "summary_status_breakdown": None,
        "summary_anti_cluster_min_bar_gap": None,
        "summary_anti_cluster_does_not_consume_edit_token": None,
        "summary_sample_size_adequacy": None,
        "summary_scope_locks": None,
        "summary_source_unchanged_during_detection": None,
        "summary_labels_sha256_self_reported": None,
        "staged_shas_now": None,
        "staged_shas_match": None,
        "artifacts_tracked_in_git": [],
    }
    root = _pathlib.Path(str(repo_root))
    tracked = {str(p).replace("\\", "/")
               for p in (tracked_paths or ())}
    for rel in (LABELS_PATH, SUMMARY_PATH, RUNNER_PATH):
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
    summary_file = root / SUMMARY_PATH
    labels_file = root / LABELS_PATH
    if summary_file.is_file():
        observation["summary_exists"] = True
        raw_summary = summary_file.read_bytes()
        observation["summary_sha256"] = _hashlib.sha256(
            raw_summary).hexdigest()
        summary = _json.loads(raw_summary.decode("utf-8"))
        for src_key, dst_key in (
                ("candidate_id", "summary_candidate_id"),
                ("candidate_family", "summary_candidate_family"),
                ("symbol", "summary_symbol"),
                ("timeframe", "summary_timeframe"),
                ("direction", "summary_direction"),
                ("sample_tag", "summary_sample_tag"),
                ("start_inclusive_utc",
                 "summary_start_inclusive_utc"),
                ("end_inclusive_utc",
                 "summary_end_inclusive_utc"),
                ("bars_scanned", "summary_bars_scanned"),
                ("first_bar_time_utc",
                 "summary_first_bar_time_utc"),
                ("last_bar_time_utc",
                 "summary_last_bar_time_utc"),
                ("attempts", "summary_attempts"),
                ("accepted_pre_anti_cluster",
                 "summary_accepted_pre_anti_cluster"),
                ("accepted_post_anti_cluster",
                 "summary_accepted_post_anti_cluster"),
                ("rejected", "summary_rejected"),
                ("anti_cluster_drops", "summary_anti_cluster_drops"),
                ("status_breakdown", "summary_status_breakdown"),
                ("anti_cluster_min_bar_gap",
                 "summary_anti_cluster_min_bar_gap"),
                ("anti_cluster_does_not_consume_edit_token",
                 "summary_anti_cluster_does_not_consume_edit_token"),
                ("sample_size_adequacy",
                 "summary_sample_size_adequacy"),
                ("scope_locks", "summary_scope_locks"),
                ("source_unchanged_during_detection",
                 "summary_source_unchanged_during_detection"),
                ("labels_sha256",
                 "summary_labels_sha256_self_reported")):
            observation[dst_key] = summary.get(src_key)
    if not labels_file.is_file():
        return observation
    observation["labels_exists"] = True
    raw_labels = labels_file.read_bytes()
    observation["labels_sha256"] = _hashlib.sha256(
        raw_labels).hexdigest()
    labels = _json.loads(raw_labels.decode("utf-8"))
    accepted_post = labels.get(
        "accepted_setups_post_anti_cluster") or []
    dropped = labels.get("anti_cluster_dropped") or []
    observation["labels_accepted_post_count"] = len(accepted_post)
    observation["labels_dropped_count"] = len(dropped)
    observation["labels_all_accepted_symbol_btcusd"] = all(
        s.get("symbol") == "BTCUSD" for s in accepted_post)
    observation["labels_all_accepted_timeframe_15m"] = all(
        s.get("timeframe") == "15m" for s in accepted_post)
    observation["labels_all_accepted_direction_long_only"] = all(
        s.get("direction") == "long_only" for s in accepted_post)
    observation[
        "labels_all_accepted_status_accepted_for_replay_review"
    ] = all(
        s.get("status") == "accepted_for_replay_review"
        for s in accepted_post)
    observation["labels_all_dropped_status_clustered"] = all(
        s.get("status") == (
            "rejected_clustered_within_8_bars_of_prior_accepted")
        for s in dropped)
    observation["labels_anti_cluster_min_bar_gap"] = labels.get(
        "anti_cluster_min_bar_gap")
    observation[
        "labels_anti_cluster_does_not_consume_edit_token"] = (
        labels.get("anti_cluster_does_not_consume_edit_token"))
    observation["labels_sample_size_adequacy"] = labels.get(
        "sample_size_adequacy")
    observation["labels_scope_locks"] = labels.get("scope_locks")
    observation[
        "labels_source_unchanged_during_detection"] = labels.get(
        "source_unchanged_during_detection")
    return observation


def certify_c8_labels_review(observation: Any) -> dict[str, Any]:
    """Pure certification of an observation against the frozen facts.
    Never raises."""
    failures: list[str] = []
    if not isinstance(observation, dict):
        return {"certified": False,
                "failures": ["observation_not_a_dict"]}
    o = observation
    if not o.get("labels_exists"):
        failures.append("labels_artifact_missing")
    if not o.get("summary_exists"):
        failures.append("summary_artifact_missing")
    if failures:
        return {"certified": False, "failures": failures}
    if o.get("labels_sha256") != EXPECTED_LABELS_SHA256:
        failures.append("labels_sha_mismatch")
    if o.get("summary_sha256") != EXPECTED_SUMMARY_SHA256:
        failures.append("summary_sha_mismatch")
    if o.get("labels_accepted_post_count") != (
            EXPECTED_ACCEPTED_POST_ANTI_CLUSTER):
        failures.append("labels_accepted_post_count_must_equal_51")
    if o.get("labels_dropped_count") != (
            EXPECTED_DROPPED_BY_ANTI_CLUSTER):
        failures.append("labels_dropped_count_must_equal_22")
    if o.get("labels_all_accepted_symbol_btcusd") is not True:
        failures.append("accepted_setups_not_all_btcusd")
    if o.get("labels_all_accepted_timeframe_15m") is not True:
        failures.append("accepted_setups_not_all_15m")
    if o.get("labels_all_accepted_direction_long_only") is not True:
        failures.append("accepted_setups_not_all_long_only")
    if o.get(
            "labels_all_accepted_status_accepted_for_replay_review"
    ) is not True:
        failures.append(
            "accepted_setups_not_all_accepted_for_replay_review")
    if o.get("labels_all_dropped_status_clustered") is not True:
        failures.append("dropped_setups_not_all_clustered_status")
    if o.get("labels_anti_cluster_min_bar_gap") != 8:
        failures.append("labels_anti_cluster_min_bar_gap_must_be_8")
    if o.get(
            "labels_anti_cluster_does_not_consume_edit_token"
    ) is not True:
        failures.append(
            "labels_anti_cluster_must_not_consume_edit_token")
    if o.get("labels_sample_size_adequacy") != (
            EXPECTED_SAMPLE_SIZE_ADEQUACY):
        failures.append("labels_sample_size_adequacy_mismatch")
    if o.get("labels_scope_locks") != EXPECTED_SCOPE_LOCKS:
        failures.append("labels_scope_locks_mismatch")
    if o.get(
            "labels_source_unchanged_during_detection") is not True:
        failures.append(
            "labels_source_unchanged_during_detection_must_be_true")
    # summary self-claims
    for key, want in EXPECTED_SUMMARY_SELF_CLAIMS.items():
        got = o.get("summary_" + key)
        if got != want:
            failures.append("summary_claim_mismatch:" + key)
    if o.get("summary_status_breakdown") != (
            EXPECTED_STATUS_BREAKDOWN):
        failures.append("summary_status_breakdown_mismatch")
    if o.get("summary_sample_size_adequacy") != (
            EXPECTED_SAMPLE_SIZE_ADEQUACY):
        failures.append("summary_sample_size_adequacy_mismatch")
    if o.get("summary_scope_locks") != EXPECTED_SCOPE_LOCKS:
        failures.append("summary_scope_locks_mismatch")
    if o.get("summary_labels_sha256_self_reported") != (
            EXPECTED_LABELS_SHA256):
        failures.append("summary_labels_sha_self_report_mismatch")
    if o.get("staged_shas_match") is not True:
        failures.append("staged_data_shas_changed")
    if o.get("artifacts_tracked_in_git"):
        failures.append("runner_and_artifacts_must_stay_untracked")
    return {"certified": not failures, "failures": failures}


def build_c8_labels_review(repo_root: Any,
                           tracked_paths: Any = ()
                           ) -> dict[str, Any]:
    """Observe read-only and certify; chain-gated on the full pushed
    C8 lane (proposal -> spec -> detector spec/dry-run -> dry-run
    review) plus V3 blacklist + V2 + Recommendation V1 + Autopilot V1
    + seven-record rejection ledger."""
    record: dict[str, Any] = {
        "schema_version": C8L_SCHEMA_VERSION, "label": C8L_LABEL,
        "mode": C8L_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [], "failures": [],
        "candidate_id": CANDIDATE_ID,
        "candidate_family": CANDIDATE_FAMILY,
        "head_at_detection": HEAD_AT_DETECTION,
        "runner_path_untracked_only": RUNNER_PATH,
        "labels_path": LABELS_PATH, "summary_path": SUMMARY_PATH,
        "expected_labels_sha256": EXPECTED_LABELS_SHA256,
        "expected_summary_sha256": EXPECTED_SUMMARY_SHA256,
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
        "expected_rejected_by_scanner": EXPECTED_REJECTED_BY_SCANNER,
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
        "expected_anti_cluster_facts":
            dict(EXPECTED_ANTI_CLUSTER_FACTS),
        "expected_summary_self_claims":
            dict(EXPECTED_SUMMARY_SELF_CLAIMS),
        "expected_scope_locks": dict(EXPECTED_SCOPE_LOCKS),
        "frozen_detection_facts": list(FROZEN_DETECTION_FACTS),
        "claim_locks": list(CLAIM_LOCKS),
        "ledger_status_seven_records": None,
        "ledger_all_rejected_kept_on_record": None,
        "human_review_required": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True, "live_gate_locked": True,
        "is_labels_review_only": True,
        "is_a_rescue_attempt": False,
        "edit_token_applied_by_this_gate": False,
        "rejection_decision_made_by_this_gate": False,
        "replay_authorized_by_this_gate": False,
        "relabel_authorized_by_this_gate": False,
        "executes": False, "writes_files": False, "labels_now": False,
        "runs_real_candle_detection": False,
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
        "creates_runners_now": False, "creates_data_artifacts_now": False,
        "creates_detector_implementation_now": False,
        "computes_pnl_now": False,
        "modifies_staged_market_data": False,
        "authorizes_paper_execution": False,
        "authorizes_micro_live": False, "authorizes_live_trading": False,
        "promotes_gate": False, "unlocks_downstream_gate": False,
        "unlocks_real_candle_detection": False,
        "unlocks_replay_now": False, "unlocks_relabel_now": False,
        "unlocks_edit_token_now": False,
        "claims_profitability": False,
        "next_required_action": NEXT_REQUIRED_ACTION,
        "current_loop_stage": CURRENT_LOOP_STAGE,
    }
    statuses = (C1_STATUS, C2_STATUS, C3_STATUS, C4_STATUS, C5_STATUS,
                C6_STATUS, C7_STATUS)
    record["ledger_status_seven_records"] = list(statuses)
    record["ledger_all_rejected_kept_on_record"] = all(
        s == "REJECTED_KEPT_ON_RECORD" for s in statuses)
    if not record["ledger_all_rejected_kept_on_record"]:
        record["verdict"] = VERDICT_C8L_BLOCKED
        record["blockers"].append("seven_record_ledger_broken")
        return record
    if build_candidate_8_family_proposal()["verdict"] != (
            VERDICT_C8P_READY):
        record["verdict"] = VERDICT_C8L_BLOCKED
        record["blockers"].append(
            "candidate_8_proposal_not_certifying")
        return record
    if build_candidate_8_spec_review()["verdict"] != VERDICT_C8S_READY:
        record["verdict"] = VERDICT_C8L_BLOCKED
        record["blockers"].append(
            "candidate_8_spec_review_not_certifying")
        return record
    if build_candidate_8_detector_spec_contract()["verdict"] != (
            VERDICT_C8D_READY):
        record["verdict"] = VERDICT_C8L_BLOCKED
        record["blockers"].append(
            "candidate_8_detector_spec_not_certifying")
        return record
    if build_candidate_8_dry_run_review()["verdict"] != (
            VERDICT_C8R_FROZEN):
        record["verdict"] = VERDICT_C8L_BLOCKED
        record["blockers"].append(
            "candidate_8_dry_run_review_not_certifying")
        return record
    if build_rejected_family_blacklist_v3()["verdict"] != (
            VERDICT_BL3_READY):
        record["verdict"] = VERDICT_C8L_BLOCKED
        record["blockers"].append("v3_blacklist_not_certifying")
        return record
    if build_overnight_research_autopilot_v2_contract()["verdict"] != (
            VERDICT_OAP2_READY):
        record["verdict"] = VERDICT_C8L_BLOCKED
        record["blockers"].append(
            "overnight_research_autopilot_v2_not_certifying")
        return record
    if _rec.build_candidate_recommendation()["verdict"] != (
            _rec.VERDICT_CR_READY):
        record["verdict"] = VERDICT_C8L_BLOCKED
        record["blockers"].append("recommendation_not_certifying")
        return record
    if _loop.build_autopilot_loop_contract()["verdict"] != (
            _loop.VERDICT_AP_READY):
        record["verdict"] = VERDICT_C8L_BLOCKED
        record["blockers"].append("autopilot_loop_not_certifying")
        return record
    observation = observe_c8_labels(repo_root, tracked_paths)
    result = certify_c8_labels_review(observation)
    record["failures"] = result["failures"]
    record["verdict"] = (VERDICT_C8L_FROZEN if result["certified"]
                         else VERDICT_C8L_REJECTED)
    return record


def validate_c8_labels_review(record: Any) -> dict[str, Any]:
    """Validate shape, frozen facts, and safety invariants. Never
    raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_C8L_FROZEN,
                                VERDICT_C8L_REJECTED,
                                VERDICT_C8L_BLOCKED):
        errors.append("bad_verdict")
    if r.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if r.get("candidate_family") != CANDIDATE_FAMILY:
        errors.append("candidate_family_tampered")
    if r.get("head_at_detection") != HEAD_AT_DETECTION:
        errors.append("head_tampered")
    if r.get("expected_labels_sha256") != EXPECTED_LABELS_SHA256:
        errors.append("labels_sha_tampered")
    if r.get("expected_summary_sha256") != EXPECTED_SUMMARY_SHA256:
        errors.append("summary_sha_tampered")
    if r.get("expected_staged_shas") != EXPECTED_STAGED_SHAS:
        errors.append("staged_shas_tampered")
    if r.get("expected_sample_tag") != EXPECTED_SAMPLE_TAG:
        errors.append("sample_tag_tampered")
    if r.get("expected_start_inclusive_utc") != (
            EXPECTED_START_INCLUSIVE_UTC):
        errors.append("start_utc_tampered")
    if r.get("expected_end_inclusive_utc") != (
            EXPECTED_END_INCLUSIVE_UTC):
        errors.append("end_utc_tampered")
    if r.get("expected_bars_scanned") != EXPECTED_BARS_SCANNED:
        errors.append("bars_scanned_tampered")
    if r.get("expected_first_bar_time") != EXPECTED_FIRST_BAR_TIME:
        errors.append("first_bar_tampered")
    if r.get("expected_last_bar_time") != EXPECTED_LAST_BAR_TIME:
        errors.append("last_bar_tampered")
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
    if r.get("expected_identity_checks") != (
            EXPECTED_IDENTITY_CHECKS):
        errors.append("identity_checks_tampered")
    if r.get("expected_sample_size_adequacy") != (
            EXPECTED_SAMPLE_SIZE_ADEQUACY):
        errors.append("sample_size_adequacy_tampered")
    if r.get("expected_sample_size_satisfied") is not (
            EXPECTED_SAMPLE_SIZE_SATISFIED):
        errors.append("sample_size_satisfied_tampered")
    if r.get("expected_anti_cluster_facts") != (
            EXPECTED_ANTI_CLUSTER_FACTS):
        errors.append("anti_cluster_facts_tampered")
    if r.get("expected_summary_self_claims") != (
            EXPECTED_SUMMARY_SELF_CLAIMS):
        errors.append("summary_self_claims_tampered")
    if r.get("expected_scope_locks") != EXPECTED_SCOPE_LOCKS:
        errors.append("scope_locks_tampered")
    if tuple(r.get("frozen_detection_facts") or ()) != (
            FROZEN_DETECTION_FACTS):
        errors.append("frozen_detection_facts_tampered")
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
                      ("is_labels_review_only", True),
                      ("is_a_rescue_attempt", False)):
        if r.get(key) is not want:
            errors.append("constitution_flag_wrong:" + key)
    for key in ("edit_token_applied_by_this_gate",
                "rejection_decision_made_by_this_gate",
                "replay_authorized_by_this_gate",
                "relabel_authorized_by_this_gate"):
        if r.get(key) is not False:
            errors.append("downstream_lock_wrong:" + key)
    for key in ("executes", "writes_files", "labels_now",
                "runs_real_candle_detection",
                "runs_relabel", "runs_replay",
                "runs_real_detection_now", "runs_replay_now",
                "scores_now", "stages_data_now", "fetches_data",
                "calls_api", "uses_network", "uses_credentials",
                "uses_wallet", "uses_account", "connects_broker",
                "connects_exchange", "uses_real_money",
                "contains_order_logic",
                "contains_portfolio_allocation_logic",
                "starts_scheduler", "sends_notifications",
                "auto_commits", "auto_pushes", "creates_runners_now",
                "creates_data_artifacts_now",
                "creates_detector_implementation_now",
                "computes_pnl_now",
                "modifies_staged_market_data",
                "authorizes_paper_execution", "authorizes_micro_live",
                "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate",
                "unlocks_real_candle_detection",
                "unlocks_replay_now", "unlocks_relabel_now",
                "unlocks_edit_token_now", "claims_profitability"):
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)
    if r.get("verdict") == VERDICT_C8L_FROZEN and r.get("failures"):
        errors.append("frozen_with_failures")
    return {"valid": not errors, "errors": errors}
