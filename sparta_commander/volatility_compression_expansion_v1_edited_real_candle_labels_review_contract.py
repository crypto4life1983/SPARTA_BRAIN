"""SPARTA CANDIDATE #7 EDITED REAL-CANDLE DETECTOR LABELS REVIEW /
EVIDENCE FREEZE (READ-ONLY, RESEARCH ONLY, NOT A PROFITABILITY CLAIM):
VOLATILITY_COMPRESSION_EXPANSION_V1.

Freezes the result of the pushed single-edit token application
(CONTRACTION_FRACTION 0.6 -> 0.7) on the same staged BTCUSD 4h sample
window. The edited scan produced the SAME counts as the original
detection: 122 attempts, 0 accepted setups, 122 rejections all on
`rejected_contraction_window`. ATR(14) on this window NEVER dropped
below 0.7 x its 100-bar rolling-average ATR for 5 consecutive
completed bars -- the relaxation from 0.6 to 0.7 made zero
structural difference.

THE POST-EDIT AUTO-REJECTION TRIGGER HAS FIRED:
  - near_zero_accepted_count_after_edited_detection = True

Per the pushed C7 single-edit decision contract on origin/master, the
single edit token is permanently spent and no further C7 edits are
allowed. Candidate #7 is now structurally headed for formal
rejection as the seventh ledger entry. This gate is INFORMATION-only;
the rejection record itself is authored at the next gate.

WHAT THIS IS NOT: no replay has run on the edited label set; no
profitability claim; no winner wording; no paper / micro-live / live
authorization; no second edit attempted; no original pushed-review
artifact was modified.

This module observes the UNTRACKED edited artifacts READ-ONLY,
recounts all 122 labels from the JSONL itself, re-verifies the two
staged-data shas, re-verifies the original pushed-review artifact
shas unchanged, verifies the summary's self-claimed flags including
the edit-token-spent flags, and certifies every frozen fact. It runs
nothing, fetches nothing, modifies nothing, and authorizes nothing.

Chain-gated live on: the pushed six-record rejection ledger (C1-C6),
the pushed C7 family proposal, the pushed C7 spec review, the pushed
C7 detector spec + dry-run, the pushed C7 dry-run review, the pushed
C7 real-candle labels review, the pushed C7 single-edit decision, the
pushed Overnight Research Autopilot V2, the pushed Recommendation V1,
and the pushed Autopilot Loop V1.
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
from sparta_commander.volatility_compression_expansion_v1_detector_dry_run_review_contract import (
    VERDICT_C7R_FROZEN,
    build_candidate_7_dry_run_review,
)
from sparta_commander.volatility_compression_expansion_v1_detector_spec_dry_run_contract import (
    VERDICT_C7D_READY,
    build_c7_detector_spec_contract,
)
from sparta_commander.volatility_compression_expansion_v1_family_proposal_contract import (
    CANDIDATE_FAMILY,
    CANDIDATE_ID,
    VERDICT_C7P_READY,
    build_candidate_7_family_proposal,
)
from sparta_commander.volatility_compression_expansion_v1_real_candle_labels_review_contract import (
    EXPECTED_LABELS_SHA256 as ORIGINAL_LABELS_SHA256,
    EXPECTED_STAGED_SHAS,
    EXPECTED_SUMMARY_SHA256 as ORIGINAL_SUMMARY_SHA256,
    LABELS_PATH as ORIGINAL_LABELS_PATH,
    SUMMARY_PATH as ORIGINAL_SUMMARY_PATH,
    VERDICT_C7L_FROZEN,
    build_c7_labels_review,
)
from sparta_commander.volatility_compression_expansion_v1_single_edit_relaxed_contraction_decision_contract import (
    EDIT_PARAMETER_NEW_VALUE,
    EDIT_PARAMETER_OLD_VALUE,
    VERDICT_C7E_APPROVED,
    build_c7_single_edit_relaxed_contraction,
)
from sparta_commander.volatility_compression_expansion_v1_spec_review_contract import (
    VERDICT_C7S_READY,
    build_candidate_7_spec_review,
)

C7EL_SCHEMA_VERSION = (
    "volatility_compression_expansion_v1_edited_real_candle_labels"
    "_review.v1")
C7EL_LABEL = (
    "SPARTA Candidate #7 Edited Real-Candle Labels Review / Evidence "
    "Freeze (READ-ONLY, RESEARCH ONLY, 122 LABELS FROZEN, ZERO "
    "ACCEPTED SETUPS AFTER EDIT, POST-EDIT AUTO-REJECTION TRIGGER "
    "FIRED, NOT A PROFITABILITY CLAIM)")
C7EL_MODE = "RESEARCH_ONLY"
VERDICT_C7EL_FROZEN = (
    "CANDIDATE_7_EDITED_REAL_CANDLE_LABELS_REVIEW_FROZEN")
VERDICT_C7EL_REJECTED = (
    "CANDIDATE_7_EDITED_REAL_CANDLE_LABELS_REVIEW_REJECTED")
VERDICT_C7EL_BLOCKED = (
    "CANDIDATE_7_EDITED_REAL_CANDLE_LABELS_REVIEW_BLOCKED")
NEXT_REQUIRED_ACTION = (
    "BUILD_C7_REJECTION_RECORD_AS_SEVENTH_LEDGER_ENTRY")

HEAD_AT_EDITED_DETECTION = (
    "ebf8672af44a1d482241a924032d7fa7fe7eeead")
EDITED_RUNNER_PATH = (
    "tools/c7_edited_real_candle_detection_once.py")
EDITED_LABELS_PATH = (
    "data/volatility_compression_c7/edited_detector_labels/"
    "c7_edited_detector_labels_2026-05-02_2026-06-10.jsonl")
EDITED_SUMMARY_PATH = (
    "data/volatility_compression_c7/edited_detector_labels/"
    "c7_edited_detector_summary_2026-05-02_2026-06-10.json")
EXPECTED_EDITED_LABELS_SHA256 = (
    "cc258348c9962c11a3bc60180f589ebc6353ceb16a44734ae9a541aa91b5695e")
EXPECTED_EDITED_SUMMARY_SHA256 = (
    "60a5a04feb448c9e3cfd03b136be3f837bf4b623cc3667691ef4d95b0578234c")

# original pushed-review C7 detection artifacts MUST remain unchanged
EXPECTED_ORIGINAL_LABELS_SHA256 = ORIGINAL_LABELS_SHA256
EXPECTED_ORIGINAL_SUMMARY_SHA256 = ORIGINAL_SUMMARY_SHA256
EXPECTED_ORIGINAL_LABELS_PATH = ORIGINAL_LABELS_PATH
EXPECTED_ORIGINAL_SUMMARY_PATH = ORIGINAL_SUMMARY_PATH

# staged BTCUSD 15m source data pins (same as the pushed labels review)
EXPECTED_STAGED_SHAS_FROZEN = dict(EXPECTED_STAGED_SHAS)

EXPECTED_AGGREGATION_RULE = {
    "method": "aggregate_4h_from_15m",
    "buckets_aligned_to_hours": (0, 4, 8, 12, 16, 20),
    "complete_bucket_rule": "exactly_16_15m_bars_per_bucket",
    "incomplete_buckets_dropped": True,
    "bars_15m_input": 3840,
    "bars_4h_output": 240,
}

# Edited detection counts -- identical structure to the original ----------
EXPECTED_TOTAL_ATTEMPTS = 122
EXPECTED_ACCEPTED_PRE_ANTI_CLUSTER = 0
EXPECTED_ACCEPTED_POST_ANTI_CLUSTER = 0
EXPECTED_REJECTED_BY_SCANNER = 122
EXPECTED_DROPPED_BY_ANTI_CLUSTER = 0
EXPECTED_MIN_EVENT_INDEX = 118
EXPECTED_MAX_EVENT_INDEX = 239

EXPECTED_STATUS_BREAKDOWN = {
    "rejected_contraction_window": 122,
}

EXPECTED_FLOOR_PASS_COUNTS = {
    "2r": 0, "3r": 0, "4r": 0,
}

# the rejection reason text in each label must reference the relaxed
# 0.7 fraction (proof the edited rule was actually applied)
EXPECTED_REJECTION_REASON_FRAGMENT = (
    "strict_below_0.7_x_rolling_avg")

# Spot-check setup IDs (same as the original detection -- the
# evaluable index range did not change because the warm-up math is
# identical) ------------------------------------------------------------
EXPECTED_FIRST_THREE_SORTED_SETUP_IDS = (
    "BTCUSD_2026-05-21T16:00:00Z",
    "BTCUSD_2026-05-21T20:00:00Z",
    "BTCUSD_2026-05-22T00:00:00Z",
)
EXPECTED_LAST_THREE_SORTED_SETUP_IDS = (
    "BTCUSD_2026-06-10T12:00:00Z",
    "BTCUSD_2026-06-10T16:00:00Z",
    "BTCUSD_2026-06-10T20:00:00Z",
)

EXPECTED_SAMPLE_TAG = "2026-05-02_2026-06-10"

# Summary self-claims that the edited runner records -----------------------
EXPECTED_SUMMARY_SELF_CLAIMS = {
    "candidate_id": "VOLATILITY_COMPRESSION_EXPANSION_V1",
    "edit_applied": "relaxed_contraction_fraction_only",
    "edit_parameter_name": "CONTRACTION_FRACTION",
    "edit_parameter_old_value": EDIT_PARAMETER_OLD_VALUE,
    "edit_parameter_new_value": EDIT_PARAMETER_NEW_VALUE,
    "symbol": "BTCUSD",
    "timeframe": "4h",
    "direction": "long_only",
    "sample_tag": EXPECTED_SAMPLE_TAG,
    "edit_token_used": 1,
    "edits_remaining_after_this": 0,
    "this_is_the_only_allowed_c7_edit": True,
    "no_other_numeric_changed_besides_contraction_fraction": True,
    "anti_cluster_does_not_consume_edit_token": True,
    "replay_executed_now": False,
    "pnl_computed": False,
    "labels_authorize_nothing": True,
    "statuses_closed_set_ok": True,
    "original_labels_sha256_verified": EXPECTED_ORIGINAL_LABELS_SHA256,
    "original_summary_sha256_verified": EXPECTED_ORIGINAL_SUMMARY_SHA256,
    "git_head": HEAD_AT_EDITED_DETECTION,
}

# Post-edit auto-rejection trigger that fired ------------------------------
EXPECTED_POST_EDIT_AUTO_REJECTION_TRIGGER_FIRED = (
    "near_zero_accepted_count_after_edited_detection")
EXPECTED_AUTO_REJECTION_TRIGGER_STATUS = {
    "near_zero_accepted_count_after_edited_detection": True,
    "any_attempt_to_change_more_than_contraction_fraction": False,
    "any_attempt_to_spend_a_second_edit_on_this_family": False,
    "any_attempt_to_change_an_inviolable_upstream_rule": False,
    "any_artifact_hash_or_gate_mismatch_in_edited_pipeline": False,
}

FROZEN_EDITED_DETECTION_FACTS = (
    "single-symbol btcusd 4h, long-only labels-only research",
    "edited rule: CONTRACTION_FRACTION = 0.7 (relaxed from 0.6 via "
    "the pushed single-edit decision); no other numeric changed",
    "existing staged btcusd 15m data only; no fetch; staged source "
    "shas unchanged pre/post",
    "original pushed-review artifacts unchanged: labels sha "
    "dc242578... and summary sha b9d9d781... byte-identical pre/post",
    "15m aggregated to 4h via complete-16-quarter-hour buckets; 240 "
    "complete 4h bars produced from 3840 input 15m bars (identical "
    "to original)",
    "scanner skips bars below min_event_index = 118",
    "122 attempts span event indices 118..239 inclusive (identical "
    "to original)",
    "every attempt rejected on contraction window; the relaxation "
    "from 0.6 to 0.7 made zero structural difference -- atr(14) "
    "never dropped below 0.7 x its 100-bar rolling average for 5 "
    "consecutive completed bars",
    "label rejection_reasons explicitly reference 'strict_below_0.7"
    "_x_rolling_avg', proving the edited rule was actually applied",
    "zero accepted setups; zero floor-pass at 2r, 3r, or 4r; zero "
    "anti-cluster drops",
    "the pushed POST_EDIT_AUTO_REJECTION_TRIGGERS.near_zero_accepted"
    "_count_after_edited_detection clause has fired",
    "no replay; no pnl; no relabel; the single C7 edit token is "
    "permanently spent and no further edits are allowed",
    "anti-cluster gap remains proposal-level locked and does NOT "
    "consume the edit token",
    "candidate #7 is structurally headed for formal rejection at "
    "the next gate as the seventh ledger entry",
    "no profitability claim, no winner wording, no paper/live "
    "approval, no execution authorization",
)

CLAIM_LOCKS = (
    "no_profitability_claim",
    "no_paper_approval",
    "no_live_approval",
    "no_execution_approval",
    "no_winner_wording",
    "no_replay_authorized_by_this_gate",
    "no_relabel_authorized_by_this_gate",
    "no_second_edit_possible",
    "no_rejection_record_created_by_this_gate",
    "anti_cluster_gap_remains_proposal_level_locked",
    "edit_token_already_spent_no_refund",
)


def get_candidate_7_edited_labels_review_label() -> str:
    return C7EL_LABEL


def observe_c7_edited_labels(repo_root: Any,
                             tracked_paths: Any = ()
                             ) -> dict[str, Any]:
    """Read the untracked edited artifacts READ-ONLY and recount the
    facts. Also re-verifies the original pushed-review artifacts are
    byte-identical. Never raises on missing files; reports absence
    instead."""
    observation: dict[str, Any] = {
        "edited_labels_exists": False,
        "edited_summary_exists": False,
        "edited_labels_sha256": None,
        "edited_summary_sha256": None,
        "edited_labels_line_count": None,
        "status_breakdown": None,
        "all_symbols_btcusd": None,
        "all_timeframes_4h": None,
        "all_direction_long": None,
        "all_rejection_reasons_reference_0_7": None,
        "min_event_index_seen": None,
        "max_event_index_seen": None,
        "first_three_sorted_setup_ids": None,
        "last_three_sorted_setup_ids": None,
        "summary_candidate_id": None,
        "summary_edit_applied": None,
        "summary_edit_parameter_name": None,
        "summary_edit_parameter_old_value": None,
        "summary_edit_parameter_new_value": None,
        "summary_symbol": None,
        "summary_timeframe": None,
        "summary_direction": None,
        "summary_sample_tag": None,
        "summary_edit_token_used": None,
        "summary_edits_remaining_after_this": None,
        "summary_this_is_the_only_allowed_c7_edit": None,
        "summary_no_other_numeric_changed_besides_contraction_fraction":
            None,
        "summary_anti_cluster_does_not_consume_edit_token": None,
        "summary_replay_executed_now": None,
        "summary_pnl_computed": None,
        "summary_labels_authorize_nothing": None,
        "summary_statuses_closed_set_ok": None,
        "summary_original_labels_sha256_verified": None,
        "summary_original_summary_sha256_verified": None,
        "summary_git_head": None,
        "summary_total_attempts": None,
        "summary_accepted_before_anti_cluster": None,
        "summary_accepted_after_anti_cluster": None,
        "summary_rejected_by_scanner": None,
        "summary_dropped_by_anti_cluster": None,
        "summary_status_breakdown": None,
        "summary_floor_pass_pre": None,
        "summary_floor_pass_post": None,
        "summary_bars_15m": None,
        "summary_bars_4h": None,
        "original_labels_sha256_now": None,
        "original_summary_sha256_now": None,
        "original_artifacts_unchanged": None,
        "staged_shas_now": None,
        "staged_shas_match": None,
        "artifacts_tracked_in_git": [],
    }
    root = _pathlib.Path(str(repo_root))
    tracked = {str(p).replace("\\", "/") for p in (tracked_paths or ())}
    for rel in (EDITED_LABELS_PATH, EDITED_SUMMARY_PATH,
                EDITED_RUNNER_PATH):
        if rel in tracked:
            observation["artifacts_tracked_in_git"].append(rel)
    staged_now: dict[str, Any] = {}
    for rel in EXPECTED_STAGED_SHAS_FROZEN:
        target = root / rel
        staged_now[rel] = (_hashlib.sha256(
            target.read_bytes()).hexdigest()
            if target.is_file() else None)
    observation["staged_shas_now"] = staged_now
    observation["staged_shas_match"] = (
        staged_now == EXPECTED_STAGED_SHAS_FROZEN)
    # original pushed-review artifacts must remain byte-identical
    original_labels = root / EXPECTED_ORIGINAL_LABELS_PATH
    original_summary = root / EXPECTED_ORIGINAL_SUMMARY_PATH
    if original_labels.is_file():
        observation["original_labels_sha256_now"] = (
            _hashlib.sha256(original_labels.read_bytes()).hexdigest())
    if original_summary.is_file():
        observation["original_summary_sha256_now"] = (
            _hashlib.sha256(original_summary.read_bytes()).hexdigest())
    observation["original_artifacts_unchanged"] = (
        observation["original_labels_sha256_now"] == (
            EXPECTED_ORIGINAL_LABELS_SHA256)
        and observation["original_summary_sha256_now"] == (
            EXPECTED_ORIGINAL_SUMMARY_SHA256))
    # edited summary
    edited_summary_file = root / EDITED_SUMMARY_PATH
    if edited_summary_file.is_file():
        observation["edited_summary_exists"] = True
        raw_summary = edited_summary_file.read_bytes()
        observation["edited_summary_sha256"] = _hashlib.sha256(
            raw_summary).hexdigest()
        summary = _json.loads(raw_summary.decode("utf-8"))
        observation["summary_candidate_id"] = summary.get(
            "candidate_id")
        observation["summary_edit_applied"] = summary.get(
            "edit_applied")
        observation["summary_edit_parameter_name"] = summary.get(
            "edit_parameter_name")
        observation["summary_edit_parameter_old_value"] = summary.get(
            "edit_parameter_old_value")
        observation["summary_edit_parameter_new_value"] = summary.get(
            "edit_parameter_new_value")
        observation["summary_symbol"] = summary.get("symbol")
        observation["summary_timeframe"] = summary.get("timeframe")
        observation["summary_direction"] = summary.get("direction")
        observation["summary_sample_tag"] = summary.get("sample_tag")
        observation["summary_edit_token_used"] = summary.get(
            "edit_token_used")
        observation["summary_edits_remaining_after_this"] = summary.get(
            "edits_remaining_after_this")
        observation[
            "summary_this_is_the_only_allowed_c7_edit"] = summary.get(
            "this_is_the_only_allowed_c7_edit")
        observation[
            "summary_no_other_numeric_changed_besides_contraction"
            "_fraction"] = summary.get(
                "no_other_numeric_changed_besides_contraction_fraction")
        observation[
            "summary_anti_cluster_does_not_consume_edit_token"] = (
            summary.get("anti_cluster_does_not_consume_edit_token"))
        observation["summary_replay_executed_now"] = summary.get(
            "replay_executed_now")
        observation["summary_pnl_computed"] = summary.get("pnl_computed")
        observation["summary_labels_authorize_nothing"] = summary.get(
            "labels_authorize_nothing")
        observation["summary_statuses_closed_set_ok"] = summary.get(
            "statuses_closed_set_ok")
        observation[
            "summary_original_labels_sha256_verified"] = summary.get(
            "original_labels_sha256_verified")
        observation[
            "summary_original_summary_sha256_verified"] = summary.get(
            "original_summary_sha256_verified")
        observation["summary_git_head"] = summary.get("git_head")
        observation["summary_total_attempts"] = summary.get(
            "total_attempts")
        observation["summary_accepted_before_anti_cluster"] = (
            summary.get("accepted_before_anti_cluster"))
        observation["summary_accepted_after_anti_cluster"] = (
            summary.get("accepted_after_anti_cluster"))
        observation["summary_rejected_by_scanner"] = summary.get(
            "rejected_by_scanner")
        observation["summary_dropped_by_anti_cluster"] = summary.get(
            "dropped_by_anti_cluster")
        observation["summary_status_breakdown"] = summary.get(
            "status_breakdown")
        observation["summary_floor_pass_pre"] = summary.get(
            "floor_pass_counts_pre_anti_cluster")
        observation["summary_floor_pass_post"] = summary.get(
            "floor_pass_counts_post_anti_cluster")
        observation["summary_bars_15m"] = summary.get("bars_15m")
        observation["summary_bars_4h"] = summary.get(
            "bars_4h_after_aggregation")
    edited_labels_file = root / EDITED_LABELS_PATH
    if not edited_labels_file.is_file():
        return observation
    observation["edited_labels_exists"] = True
    raw = edited_labels_file.read_bytes()
    observation["edited_labels_sha256"] = _hashlib.sha256(
        raw).hexdigest()
    lines = raw.decode("utf-8").splitlines()
    observation["edited_labels_line_count"] = len(lines)
    labels = [_json.loads(line) for line in lines]
    breakdown: dict[str, int] = {}
    all_btc = True
    all_4h = True
    all_long = True
    all_reasons_have_0_7 = True
    min_idx, max_idx = None, None
    for label in labels:
        breakdown[label["status"]] = breakdown.get(
            label["status"], 0) + 1
        if label.get("symbol") != "BTCUSD":
            all_btc = False
        if label.get("timeframe") != "4h":
            all_4h = False
        if label.get("direction") != "long":
            all_long = False
        reasons = " ".join(label.get("rejection_reasons") or [])
        if EXPECTED_REJECTION_REASON_FRAGMENT not in reasons:
            all_reasons_have_0_7 = False
        ev = label.get("event_index")
        if ev is not None:
            if min_idx is None or ev < min_idx:
                min_idx = ev
            if max_idx is None or ev > max_idx:
                max_idx = ev
    observation["status_breakdown"] = breakdown
    observation["all_symbols_btcusd"] = all_btc
    observation["all_timeframes_4h"] = all_4h
    observation["all_direction_long"] = all_long
    observation["all_rejection_reasons_reference_0_7"] = (
        all_reasons_have_0_7)
    observation["min_event_index_seen"] = min_idx
    observation["max_event_index_seen"] = max_idx
    sorted_ids = sorted(label["setup_id"] for label in labels)
    observation["first_three_sorted_setup_ids"] = tuple(sorted_ids[:3])
    observation["last_three_sorted_setup_ids"] = tuple(sorted_ids[-3:])
    return observation


def certify_c7_edited_labels_review(observation: Any
                                    ) -> dict[str, Any]:
    """Pure certification of an observation against the frozen facts."""
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
    if o.get("edited_labels_sha256") != EXPECTED_EDITED_LABELS_SHA256:
        failures.append("edited_labels_sha_mismatch")
    if o.get("edited_summary_sha256") != EXPECTED_EDITED_SUMMARY_SHA256:
        failures.append("edited_summary_sha_mismatch")
    if o.get("edited_labels_line_count") != EXPECTED_TOTAL_ATTEMPTS:
        failures.append("edited_label_count_must_equal_122")
    if o.get("status_breakdown") != EXPECTED_STATUS_BREAKDOWN:
        failures.append("status_breakdown_mismatch")
    if o.get("all_symbols_btcusd") is not True:
        failures.append("not_all_btcusd")
    if o.get("all_timeframes_4h") is not True:
        failures.append("not_all_4h")
    if o.get("all_direction_long") is not True:
        failures.append("not_all_long_direction")
    if o.get("all_rejection_reasons_reference_0_7") is not True:
        failures.append(
            "rejection_reasons_must_reference_strict_below_0_7")
    if o.get("min_event_index_seen") != EXPECTED_MIN_EVENT_INDEX:
        failures.append("min_event_index_must_equal_118")
    if o.get("max_event_index_seen") != EXPECTED_MAX_EVENT_INDEX:
        failures.append("max_event_index_must_equal_239")
    if o.get("first_three_sorted_setup_ids") != (
            EXPECTED_FIRST_THREE_SORTED_SETUP_IDS):
        failures.append("first_three_setup_ids_mismatch")
    if o.get("last_three_sorted_setup_ids") != (
            EXPECTED_LAST_THREE_SORTED_SETUP_IDS):
        failures.append("last_three_setup_ids_mismatch")
    # summary self-claims (key-by-key against EXPECTED_SUMMARY_SELF_CLAIMS)
    name_map = {
        "candidate_id": "summary_candidate_id",
        "edit_applied": "summary_edit_applied",
        "edit_parameter_name": "summary_edit_parameter_name",
        "edit_parameter_old_value": "summary_edit_parameter_old_value",
        "edit_parameter_new_value": "summary_edit_parameter_new_value",
        "symbol": "summary_symbol",
        "timeframe": "summary_timeframe",
        "direction": "summary_direction",
        "sample_tag": "summary_sample_tag",
        "edit_token_used": "summary_edit_token_used",
        "edits_remaining_after_this":
            "summary_edits_remaining_after_this",
        "this_is_the_only_allowed_c7_edit":
            "summary_this_is_the_only_allowed_c7_edit",
        "no_other_numeric_changed_besides_contraction_fraction":
            "summary_no_other_numeric_changed_besides_contraction"
            "_fraction",
        "anti_cluster_does_not_consume_edit_token":
            "summary_anti_cluster_does_not_consume_edit_token",
        "replay_executed_now": "summary_replay_executed_now",
        "pnl_computed": "summary_pnl_computed",
        "labels_authorize_nothing":
            "summary_labels_authorize_nothing",
        "statuses_closed_set_ok": "summary_statuses_closed_set_ok",
        "original_labels_sha256_verified":
            "summary_original_labels_sha256_verified",
        "original_summary_sha256_verified":
            "summary_original_summary_sha256_verified",
        "git_head": "summary_git_head",
    }
    for key, want in EXPECTED_SUMMARY_SELF_CLAIMS.items():
        observation_key = name_map[key]
        if o.get(observation_key) != want:
            failures.append("summary_claim_mismatch:" + key)
    if o.get("summary_total_attempts") != EXPECTED_TOTAL_ATTEMPTS:
        failures.append("summary_total_attempts_must_equal_122")
    if o.get("summary_accepted_before_anti_cluster") != 0:
        failures.append("summary_accepted_before_must_equal_0")
    if o.get("summary_accepted_after_anti_cluster") != 0:
        failures.append("summary_accepted_after_must_equal_0")
    if o.get("summary_rejected_by_scanner") != (
            EXPECTED_REJECTED_BY_SCANNER):
        failures.append("summary_rejected_must_equal_122")
    if o.get("summary_dropped_by_anti_cluster") != 0:
        failures.append("summary_dropped_must_equal_0")
    if o.get("summary_status_breakdown") != EXPECTED_STATUS_BREAKDOWN:
        failures.append("summary_status_breakdown_mismatch")
    if o.get("summary_floor_pass_pre") != EXPECTED_FLOOR_PASS_COUNTS:
        failures.append("summary_floor_pass_pre_must_be_all_zero")
    if o.get("summary_floor_pass_post") != EXPECTED_FLOOR_PASS_COUNTS:
        failures.append("summary_floor_pass_post_must_be_all_zero")
    if o.get("summary_bars_15m") != EXPECTED_AGGREGATION_RULE[
            "bars_15m_input"]:
        failures.append("summary_bars_15m_must_equal_3840")
    if o.get("summary_bars_4h") != EXPECTED_AGGREGATION_RULE[
            "bars_4h_output"]:
        failures.append("summary_bars_4h_must_equal_240")
    if o.get("staged_shas_match") is not True:
        failures.append("staged_data_shas_changed")
    if o.get("original_artifacts_unchanged") is not True:
        failures.append("original_pushed_review_artifacts_changed")
    if o.get("artifacts_tracked_in_git"):
        failures.append(
            "edited_runner_and_artifacts_must_stay_untracked")
    return {"certified": not failures, "failures": failures}


def build_c7_edited_labels_review(repo_root: Any,
                                  tracked_paths: Any = ()
                                  ) -> dict[str, Any]:
    """Observe read-only and certify; chain-gated on the full pushed
    C7 lane (proposal -> spec -> detector spec/dry-run -> dry-run
    review -> labels review -> single-edit decision) plus V2 +
    Recommendation V1 + Autopilot V1 + six-record rejection ledger."""
    record: dict[str, Any] = {
        "schema_version": C7EL_SCHEMA_VERSION, "label": C7EL_LABEL,
        "mode": C7EL_MODE, "lane": "crypto_d1_auto_research",
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
        "expected_original_labels_sha256":
            EXPECTED_ORIGINAL_LABELS_SHA256,
        "expected_original_summary_sha256":
            EXPECTED_ORIGINAL_SUMMARY_SHA256,
        "expected_staged_shas":
            dict(EXPECTED_STAGED_SHAS_FROZEN),
        "expected_aggregation_rule": {
            key: (list(value) if isinstance(value, tuple) else value)
            for key, value in EXPECTED_AGGREGATION_RULE.items()},
        "expected_total_attempts": EXPECTED_TOTAL_ATTEMPTS,
        "expected_accepted_pre_anti_cluster":
            EXPECTED_ACCEPTED_PRE_ANTI_CLUSTER,
        "expected_accepted_post_anti_cluster":
            EXPECTED_ACCEPTED_POST_ANTI_CLUSTER,
        "expected_rejected_by_scanner": EXPECTED_REJECTED_BY_SCANNER,
        "expected_dropped_by_anti_cluster":
            EXPECTED_DROPPED_BY_ANTI_CLUSTER,
        "expected_min_event_index": EXPECTED_MIN_EVENT_INDEX,
        "expected_max_event_index": EXPECTED_MAX_EVENT_INDEX,
        "expected_status_breakdown":
            dict(EXPECTED_STATUS_BREAKDOWN),
        "expected_floor_pass_counts":
            dict(EXPECTED_FLOOR_PASS_COUNTS),
        "expected_rejection_reason_fragment":
            EXPECTED_REJECTION_REASON_FRAGMENT,
        "expected_first_three_sorted_setup_ids":
            list(EXPECTED_FIRST_THREE_SORTED_SETUP_IDS),
        "expected_last_three_sorted_setup_ids":
            list(EXPECTED_LAST_THREE_SORTED_SETUP_IDS),
        "expected_sample_tag": EXPECTED_SAMPLE_TAG,
        "expected_summary_self_claims":
            dict(EXPECTED_SUMMARY_SELF_CLAIMS),
        "expected_post_edit_auto_rejection_trigger_fired":
            EXPECTED_POST_EDIT_AUTO_REJECTION_TRIGGER_FIRED,
        "expected_auto_rejection_trigger_status":
            dict(EXPECTED_AUTO_REJECTION_TRIGGER_STATUS),
        "frozen_edited_detection_facts":
            list(FROZEN_EDITED_DETECTION_FACTS),
        "claim_locks": list(CLAIM_LOCKS),
        "ledger_status_six_records": None,
        "ledger_all_rejected_kept_on_record": None,
        "human_review_required": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True, "live_gate_locked": True,
        "is_edited_labels_review_only": True,
        "is_a_rescue_attempt": False,
        "second_edit_possible": False,
        "edit_token_applied_by_this_gate": False,
        "rejection_decision_made_by_this_gate": False,
        "replay_authorized_by_this_gate": False,
        "relabel_authorized_by_this_gate": False,
        "executes": False, "writes_files": False, "labels_now": False,
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
        "creates_runners_now": False, "creates_data_artifacts_now": False,
        "modifies_staged_market_data": False,
        "modifies_detector_artifacts": False,
        "computes_pnl_now": False,
        "authorizes_paper_execution": False,
        "authorizes_micro_live": False, "authorizes_live_trading": False,
        "promotes_gate": False, "unlocks_downstream_gate": False,
        "unlocks_replay_now": False, "unlocks_relabel_now": False,
        "unlocks_second_edit_now": False,
        "claims_profitability": False,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    statuses = (C1_STATUS, C2_STATUS, C3_STATUS, C4_STATUS, C5_STATUS,
                C6_STATUS)
    record["ledger_status_six_records"] = list(statuses)
    record["ledger_all_rejected_kept_on_record"] = all(
        s == "REJECTED_KEPT_ON_RECORD" for s in statuses)
    if not record["ledger_all_rejected_kept_on_record"]:
        record["verdict"] = VERDICT_C7EL_BLOCKED
        record["blockers"].append("six_record_ledger_broken")
        return record
    if build_candidate_7_family_proposal()["verdict"] != (
            VERDICT_C7P_READY):
        record["verdict"] = VERDICT_C7EL_BLOCKED
        record["blockers"].append("candidate_7_proposal_not_certifying")
        return record
    if build_candidate_7_spec_review()["verdict"] != VERDICT_C7S_READY:
        record["verdict"] = VERDICT_C7EL_BLOCKED
        record["blockers"].append(
            "candidate_7_spec_review_not_certifying")
        return record
    if build_c7_detector_spec_contract()["verdict"] != (
            VERDICT_C7D_READY):
        record["verdict"] = VERDICT_C7EL_BLOCKED
        record["blockers"].append(
            "candidate_7_detector_spec_not_certifying")
        return record
    if build_candidate_7_dry_run_review()["verdict"] != (
            VERDICT_C7R_FROZEN):
        record["verdict"] = VERDICT_C7EL_BLOCKED
        record["blockers"].append(
            "candidate_7_dry_run_review_not_certifying")
        return record
    if build_c7_labels_review(repo_root, tracked_paths)["verdict"] \
            != VERDICT_C7L_FROZEN:
        record["verdict"] = VERDICT_C7EL_BLOCKED
        record["blockers"].append(
            "candidate_7_labels_review_not_certifying")
        return record
    single_edit = build_c7_single_edit_relaxed_contraction(
        repo_root, tracked_paths)
    if single_edit["verdict"] != VERDICT_C7E_APPROVED:
        record["verdict"] = VERDICT_C7EL_BLOCKED
        record["blockers"].append(
            "candidate_7_single_edit_decision_not_certifying")
        return record
    if build_overnight_research_autopilot_v2_contract()["verdict"] != (
            VERDICT_OAP2_READY):
        record["verdict"] = VERDICT_C7EL_BLOCKED
        record["blockers"].append(
            "overnight_research_autopilot_v2_not_certifying")
        return record
    if _rec.build_candidate_recommendation()["verdict"] != (
            _rec.VERDICT_CR_READY):
        record["verdict"] = VERDICT_C7EL_BLOCKED
        record["blockers"].append("recommendation_not_certifying")
        return record
    if _loop.build_autopilot_loop_contract()["verdict"] != (
            _loop.VERDICT_AP_READY):
        record["verdict"] = VERDICT_C7EL_BLOCKED
        record["blockers"].append("autopilot_loop_not_certifying")
        return record
    observation = observe_c7_edited_labels(repo_root, tracked_paths)
    result = certify_c7_edited_labels_review(observation)
    record["failures"] = result["failures"]
    record["verdict"] = (VERDICT_C7EL_FROZEN if result["certified"]
                         else VERDICT_C7EL_REJECTED)
    return record


def validate_c7_edited_labels_review(record: Any
                                     ) -> dict[str, Any]:
    """Validate shape, frozen facts, and safety invariants. Never
    raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_C7EL_FROZEN,
                                VERDICT_C7EL_REJECTED,
                                VERDICT_C7EL_BLOCKED):
        errors.append("bad_verdict")
    if r.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if r.get("candidate_family") != CANDIDATE_FAMILY:
        errors.append("candidate_family_tampered")
    if r.get("head_at_edited_detection") != (
            HEAD_AT_EDITED_DETECTION):
        errors.append("head_tampered")
    if r.get("expected_edited_labels_sha256") != (
            EXPECTED_EDITED_LABELS_SHA256):
        errors.append("edited_labels_sha_tampered")
    if r.get("expected_edited_summary_sha256") != (
            EXPECTED_EDITED_SUMMARY_SHA256):
        errors.append("edited_summary_sha_tampered")
    if r.get("expected_original_labels_sha256") != (
            EXPECTED_ORIGINAL_LABELS_SHA256):
        errors.append("original_labels_sha_tampered")
    if r.get("expected_original_summary_sha256") != (
            EXPECTED_ORIGINAL_SUMMARY_SHA256):
        errors.append("original_summary_sha_tampered")
    if r.get("expected_staged_shas") != EXPECTED_STAGED_SHAS_FROZEN:
        errors.append("staged_shas_tampered")
    expected_agg = {key: (list(value) if isinstance(value, tuple)
                          else value)
                    for key, value
                    in EXPECTED_AGGREGATION_RULE.items()}
    if r.get("expected_aggregation_rule") != expected_agg:
        errors.append("aggregation_rule_tampered")
    if r.get("expected_total_attempts") != EXPECTED_TOTAL_ATTEMPTS:
        errors.append("total_attempts_tampered")
    if r.get("expected_accepted_pre_anti_cluster") != 0:
        errors.append("accepted_pre_tampered")
    if r.get("expected_accepted_post_anti_cluster") != 0:
        errors.append("accepted_post_tampered")
    if r.get("expected_rejected_by_scanner") != (
            EXPECTED_REJECTED_BY_SCANNER):
        errors.append("rejected_count_tampered")
    if r.get("expected_dropped_by_anti_cluster") != 0:
        errors.append("anti_cluster_dropped_tampered")
    if r.get("expected_min_event_index") != EXPECTED_MIN_EVENT_INDEX:
        errors.append("min_event_index_tampered")
    if r.get("expected_max_event_index") != EXPECTED_MAX_EVENT_INDEX:
        errors.append("max_event_index_tampered")
    if r.get("expected_status_breakdown") != (
            EXPECTED_STATUS_BREAKDOWN):
        errors.append("status_breakdown_tampered")
    if r.get("expected_floor_pass_counts") != (
            EXPECTED_FLOOR_PASS_COUNTS):
        errors.append("floor_pass_tampered")
    if r.get("expected_rejection_reason_fragment") != (
            EXPECTED_REJECTION_REASON_FRAGMENT):
        errors.append("rejection_reason_fragment_tampered")
    if tuple(r.get("expected_first_three_sorted_setup_ids") or ()) != (
            EXPECTED_FIRST_THREE_SORTED_SETUP_IDS):
        errors.append("first_three_ids_tampered")
    if tuple(r.get("expected_last_three_sorted_setup_ids") or ()) != (
            EXPECTED_LAST_THREE_SORTED_SETUP_IDS):
        errors.append("last_three_ids_tampered")
    if r.get("expected_sample_tag") != EXPECTED_SAMPLE_TAG:
        errors.append("sample_tag_tampered")
    if r.get("expected_summary_self_claims") != (
            EXPECTED_SUMMARY_SELF_CLAIMS):
        errors.append("summary_self_claims_tampered")
    if r.get("expected_post_edit_auto_rejection_trigger_fired") != (
            EXPECTED_POST_EDIT_AUTO_REJECTION_TRIGGER_FIRED):
        errors.append("post_edit_trigger_fired_label_tampered")
    if r.get("expected_auto_rejection_trigger_status") != (
            EXPECTED_AUTO_REJECTION_TRIGGER_STATUS):
        errors.append("auto_rejection_trigger_status_tampered")
    if tuple(r.get("frozen_edited_detection_facts") or ()) != (
            FROZEN_EDITED_DETECTION_FACTS):
        errors.append("frozen_edited_detection_facts_tampered")
    if tuple(r.get("claim_locks") or ()) != CLAIM_LOCKS:
        errors.append("claim_locks_tampered")
    if r.get("next_required_action") != NEXT_REQUIRED_ACTION:
        errors.append("next_required_action_tampered")
    for key, want in (("human_review_required", True),
                      ("paper_trading_gate_locked", True),
                      ("micro_live_gate_locked", True),
                      ("live_gate_locked", True),
                      ("is_edited_labels_review_only", True),
                      ("is_a_rescue_attempt", False),
                      ("second_edit_possible", False)):
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
                "auto_commits", "auto_pushes", "creates_runners_now",
                "creates_data_artifacts_now",
                "modifies_staged_market_data",
                "modifies_detector_artifacts",
                "computes_pnl_now",
                "authorizes_paper_execution", "authorizes_micro_live",
                "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate",
                "unlocks_replay_now", "unlocks_relabel_now",
                "unlocks_second_edit_now", "claims_profitability"):
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)
    if r.get("verdict") == VERDICT_C7EL_FROZEN and r.get("failures"):
        errors.append("frozen_with_failures")
    return {"valid": not errors, "errors": errors}
