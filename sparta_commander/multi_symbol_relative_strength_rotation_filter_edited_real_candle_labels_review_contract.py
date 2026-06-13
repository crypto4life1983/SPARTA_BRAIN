"""SPARTA CANDIDATE #6 EDITED REAL-CANDLE LABELS REVIEW / EVIDENCE
FREEZE (READ-ONLY, RESEARCH ONLY, NOT A PROFITABILITY CLAIM):
MULTI_SYMBOL_RELATIVE_STRENGTH_ROTATION_FILTER_V1.

Freezes the result of the pushed single-edit clustering filter applied
at label-emission time on the existing staged 2026-05-02_2026-06-10
sample window. The pushed Candidate #6 scanner saw 389 attempts and
flagged 135 as accepted (unchanged); the pushed 24-bar same-symbol
minimum bar-gap clustering filter then removed 99 accepted events
(BTCUSD 23, ETHUSD 21, SOLUSD 55) leaving 36 independent kept accepted
events (BTCUSD 9, ETHUSD 11, SOLUSD 16). Every kept accepted event
still passes the 81 bps gross-target-distance floor at 2R/3R/4R --
floor compliance was not weakened by the edit; the edit only reduced
density.

WHAT THIS IS NOT: no replay has run on the edited label set; no edge
has been demonstrated; no profitability exists or is claimed. The edit
token is already spent on origin/master and cannot be refunded; the
family's second edit attempt is permanently rejected. Whether to
authorize a fee-honest replay on the 36 kept labels or close the
family without one is the HUMAN decision at the next gate.

This module observes the untracked edited artifacts READ-ONLY,
recounts all 389 lines from the JSONL, re-verifies the six staged-data
shas (unchanged from the original detection run), verifies the
summary's edit_constants match the pushed single-edit contract's
frozen constants, and certifies every frozen fact. It runs nothing,
fetches nothing, modifies nothing, and authorizes nothing.

Chain-gated on the pushed five-record rejection ledger, the pushed C6
family proposal, the pushed C6 spec review, the pushed C6 detector
spec, the pushed C6 dry-run review, the pushed C6 real-candle labels
review, the pushed C6 informational replay results review, the pushed
C6 single-edit clustering-filter contract, the pushed Recommendation
V1, and the pushed Autopilot Loop V1.
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
from sparta_commander.multi_symbol_relative_strength_rotation_filter_dry_run_review_contract import (
    VERDICT_C6R_FROZEN,
    build_c6_dry_run_review,
)
from sparta_commander.multi_symbol_relative_strength_rotation_filter_family_proposal_contract import (
    CANDIDATE_ID,
    VERDICT_C6P_READY,
    build_candidate_6_family_proposal,
)
from sparta_commander.multi_symbol_relative_strength_rotation_filter_real_candle_labels_review_contract import (
    EXPECTED_ACCEPTED_SETUP_IDS as ORIGINAL_ACCEPTED_SETUP_IDS,
    EXPECTED_AGGREGATION_COUNTS,
    EXPECTED_ALIGNMENT_STATUS,
    EXPECTED_STAGED_SHAS,
    VERDICT_C6L_FROZEN,
    build_c6_labels_review,
)
from sparta_commander.multi_symbol_relative_strength_rotation_filter_replay_results_review_contract import (
    VERDICT_C6RR_FROZEN,
    build_c6_replay_results_review,
)
from sparta_commander.multi_symbol_relative_strength_rotation_filter_single_edit_clustering_filter_contract import (
    MIN_BARS_BETWEEN_SAME_SYMBOL_ACCEPTED_EVENTS_1H,
    VERDICT_C6E_READY,
    build_c6_single_edit_clustering_filter,
)
from sparta_commander.multi_symbol_relative_strength_rotation_filter_spec_review_contract import (
    VERDICT_C6S_READY,
    build_candidate_6_spec_review,
)
from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
    REJECTION_STATUS as C1_STATUS,
)
from sparta_commander.sol_btc_long_1h_swing_structure_rejection_record_contract import (
    REJECTION_STATUS as C4_STATUS,
)

C6EL_SCHEMA_VERSION = (
    "multi_symbol_relative_strength_rotation_filter_edited_real_candle"
    "_labels_review.v1")
C6EL_LABEL = ("SPARTA Candidate #6 Edited Real-Candle Labels Review / "
              "Evidence Freeze (READ-ONLY, RESEARCH ONLY, 36 KEPT "
              "LABELS FROZEN, NOT A PROFITABILITY CLAIM)")
C6EL_MODE = "RESEARCH_ONLY"
VERDICT_C6EL_FROZEN = (
    "CANDIDATE_6_EDITED_REAL_CANDLE_LABELS_FROZEN_READY_FOR_HUMAN_REVIEW")
VERDICT_C6EL_REJECTED = (
    "CANDIDATE_6_EDITED_REAL_CANDLE_LABELS_REVIEW_REJECTED")
VERDICT_C6EL_BLOCKED = (
    "CANDIDATE_6_EDITED_REAL_CANDLE_LABELS_REVIEW_BLOCKED")
NEXT_REQUIRED_ACTION = (
    "HUMAN_DECISION_C6_AUTHORIZE_EDITED_REPLAY_OR_CLOSE_FAMILY")

HEAD_AT_EDITED_RELABEL = "13eb9ecce745d8874b99947aed5ef0fba53aa0f7"
RUNNER_PATH = "tools/c6_edited_relabel_clustering_filter_once.py"
LABELS_PATH = ("data/rs_rotation_c6/edited_detector_labels/"
               "c6_edited_detector_labels_2026-05-02_2026-06-10.jsonl")
SUMMARY_PATH = ("data/rs_rotation_c6/edited_detector_labels/"
                "c6_edited_detector_summary_2026-05-02_2026-06-10.json")
EXPECTED_LABELS_SHA256 = (
    "a2c720be296914edc863835c02b71949cbf727ae67b0853018983f4a8ae9d987")
EXPECTED_SUMMARY_SHA256 = (
    "92bdf76ec9474292a92ce687a5d830b5f1d66ad65cc4f49c86489219d0446f7a")

# the edited run does NOT touch staged data; staged shas frozen at the
# same six values as the original C6 labels review
EXPECTED_STAGED_SHAS_FROZEN = dict(EXPECTED_STAGED_SHAS)

EXPECTED_EDIT_CONSTANTS = {
    "min_bars_between_same_symbol_accepted_events_1h":
        MIN_BARS_BETWEEN_SAME_SYMBOL_ACCEPTED_EVENTS_1H,
    "tie_breaker": "keep_the_earlier_event_drop_the_later_one",
    "scope": "per_symbol",
    "applies_at": "label_emission_time_before_replay",
}

EXPECTED_AGGREGATION_COUNTS_FROZEN = dict(EXPECTED_AGGREGATION_COUNTS)
EXPECTED_ALIGNMENT_STATUS_FROZEN = EXPECTED_ALIGNMENT_STATUS

EXPECTED_TOTAL_ATTEMPTS = 389
EXPECTED_ACCEPTED_BEFORE_EDIT = 135
EXPECTED_ACCEPTED_AFTER_EDIT = 36
EXPECTED_REMOVED_BY_CLUSTERING_TOTAL = 99
EXPECTED_SCANNER_REJECTED_TOTAL = 254  # unchanged from original review

EXPECTED_PER_SYMBOL_EDITED = {
    "BTCUSD": {"attempts": 127, "accepted_before_edit": 32,
               "accepted_after_edit": 9,
               "scanner_rejected": 95, "removed_by_clustering": 23,
               "floor_pass_2r": 9, "floor_pass_3r": 9,
               "floor_pass_4r": 9, "floor_fail": 0},
    "ETHUSD": {"attempts": 130, "accepted_before_edit": 32,
               "accepted_after_edit": 11,
               "scanner_rejected": 98, "removed_by_clustering": 21,
               "floor_pass_2r": 11, "floor_pass_3r": 11,
               "floor_pass_4r": 11, "floor_fail": 0},
    "SOLUSD": {"attempts": 132, "accepted_before_edit": 71,
               "accepted_after_edit": 16,
               "scanner_rejected": 61, "removed_by_clustering": 55,
               "floor_pass_2r": 16, "floor_pass_3r": 16,
               "floor_pass_4r": 16, "floor_fail": 0},
    "total": {"attempts": 389, "accepted_before_edit": 135,
              "accepted_after_edit": 36,
              "scanner_rejected": 254,
              "removed_by_clustering": 99,
              "floor_pass_2r": 36, "floor_pass_3r": 36,
              "floor_pass_4r": 36, "floor_fail": 0},
}

EXPECTED_FLOOR_PASS_AFTER_EDIT = {
    "2r": 36, "3r": 36, "4r": 36}
EXPECTED_FLOOR_FAIL_AFTER_EDIT = {"2r": 0, "3r": 0, "4r": 0}

EXPECTED_KEPT_ACCEPTED_SETUP_IDS = (
    "BTCUSD_2026-05-04T17:00:00Z", "BTCUSD_2026-05-08T11:00:00Z",
    "BTCUSD_2026-05-13T02:00:00Z", "BTCUSD_2026-05-14T14:00:00Z",
    "BTCUSD_2026-05-20T08:00:00Z", "BTCUSD_2026-05-23T18:00:00Z",
    "BTCUSD_2026-05-24T23:00:00Z", "BTCUSD_2026-05-30T14:00:00Z",
    "BTCUSD_2026-06-10T13:00:00Z",
    "ETHUSD_2026-05-02T20:00:00Z", "ETHUSD_2026-05-03T22:00:00Z",
    "ETHUSD_2026-05-13T04:00:00Z", "ETHUSD_2026-05-17T12:00:00Z",
    "ETHUSD_2026-05-20T05:00:00Z", "ETHUSD_2026-05-23T20:00:00Z",
    "ETHUSD_2026-05-25T16:00:00Z", "ETHUSD_2026-05-29T15:00:00Z",
    "ETHUSD_2026-05-31T01:00:00Z", "ETHUSD_2026-06-06T23:00:00Z",
    "ETHUSD_2026-06-07T23:00:00Z",
    "SOLUSD_2026-05-05T18:00:00Z", "SOLUSD_2026-05-07T07:00:00Z",
    "SOLUSD_2026-05-08T10:00:00Z", "SOLUSD_2026-05-10T08:00:00Z",
    "SOLUSD_2026-05-11T15:00:00Z", "SOLUSD_2026-05-14T15:00:00Z",
    "SOLUSD_2026-05-17T05:00:00Z", "SOLUSD_2026-05-20T14:00:00Z",
    "SOLUSD_2026-05-21T17:00:00Z", "SOLUSD_2026-05-23T19:00:00Z",
    "SOLUSD_2026-05-27T15:00:00Z", "SOLUSD_2026-05-28T18:00:00Z",
    "SOLUSD_2026-05-30T02:00:00Z", "SOLUSD_2026-05-31T03:00:00Z",
    "SOLUSD_2026-06-07T01:00:00Z", "SOLUSD_2026-06-08T17:00:00Z",
)

FROZEN_EDITED_REVIEW_FACTS = (
    "edit applied: label-time same-symbol minimum bar-gap clustering "
    "filter, 24 completed 1h bars between accepted events per symbol",
    "tie-breaker: keep the earlier accepted event, drop the later",
    "edit applied at label-emission time BEFORE replay-time non-overlap",
    "replay-time same-symbol non-overlap remains unchanged",
    "no other detector or spec parameter was changed",
    "staged 15m candles unchanged; six staged shas match the original "
    "detection run exactly",
    "1h aggregation and timestamp alignment identical to the original "
    "run: 960 bars per symbol; aligned across the full universe",
    "scanner rejections unchanged at 254/389; the edit cannot promote "
    "any rejected setup",
    "135 accepted setups before edit; 36 accepted setups after edit; "
    "99 removed by the 24-bar clustering filter",
    "per-symbol removal: BTCUSD 23 of 32 (kept 9), ETHUSD 21 of 32 "
    "(kept 11), SOLUSD 55 of 71 (kept 16) -- SOLUSD was the dominant "
    "clustered symbol",
    "every kept accepted setup still clears the 81 bps gross-target-"
    "distance floor at 2R, 3R, and 4R; floor compliance not weakened "
    "by the edit",
    "no replay has run on the edited label set; no edge demonstrated; "
    "no profitability claim",
    "the family's single edit token is already spent on origin/master "
    "and cannot be refunded; a second edit is permanently rejected",
)

CLAIM_LOCKS = (
    "no_profitability_claim",
    "no_paper_approval",
    "no_live_approval",
    "no_execution_approval",
    "no_winner_wording",
    "no_replay_authorized_by_this_gate",
    "no_second_edit_possible",
    "no_rejection_decision_made_by_this_gate",
    "edit_token_already_spent_no_refund",
)


def get_c6_edited_labels_review_label() -> str:
    return C6EL_LABEL


def observe_c6_edited_labels(repo_root: Any,
                             tracked_paths: Any = ()
                             ) -> dict[str, Any]:
    """Read the edited artifacts READ-ONLY and recount the facts. Never
    raises on missing files; reports absence instead."""
    observation: dict[str, Any] = {
        "labels_exists": False, "summary_exists": False,
        "labels_sha256": None, "summary_sha256": None,
        "labels_line_count": None,
        "accepted_count_before_edit": None,
        "accepted_count_after_edit": None,
        "removed_by_clustering_total": None,
        "scanner_rejected_total": None,
        "per_symbol_counts": None,
        "kept_accepted_setup_ids": None,
        "floor_pass_after_edit": None,
        "floor_fail_after_edit": None,
        "all_kept_pass_floor_at_all_variants": None,
        "edit_constants_in_summary": None,
        "summary_aggregation_counts": None,
        "summary_alignment_status": None,
        "summary_replay_executed_now": None,
        "summary_no_second_edit": None,
        "summary_no_detector_rewrite": None,
        "summary_no_profitability_claim": None,
        "summary_no_paper_or_live_authorization": None,
        "summary_no_parameter_changes": None,
        "candidate_id_in_summary": None,
        "staged_shas_now": None, "staged_shas_match": None,
        "artifacts_tracked_in_git": [],
    }
    root = _pathlib.Path(str(repo_root))
    tracked = {str(p).replace("\\", "/") for p in (tracked_paths or ())}
    for rel in (LABELS_PATH, SUMMARY_PATH, RUNNER_PATH):
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
    summary_file = root / SUMMARY_PATH
    labels_file = root / LABELS_PATH
    if summary_file.is_file():
        observation["summary_exists"] = True
        raw_summary = summary_file.read_bytes()
        observation["summary_sha256"] = _hashlib.sha256(
            raw_summary).hexdigest()
        summary = _json.loads(raw_summary.decode("utf-8"))
        observation["candidate_id_in_summary"] = summary.get(
            "candidate_id")
        observation["edit_constants_in_summary"] = summary.get(
            "edit_constants")
        observation["summary_aggregation_counts"] = summary.get(
            "aggregation_counts")
        observation["summary_alignment_status"] = summary.get(
            "timestamp_alignment_status")
        observation["summary_replay_executed_now"] = summary.get(
            "replay_executed_now")
        observation["summary_no_second_edit"] = summary.get(
            "no_second_edit")
        observation["summary_no_detector_rewrite"] = summary.get(
            "no_detector_rewrite")
        observation["summary_no_parameter_changes"] = summary.get(
            "no_parameter_changes_other_than_pushed_clustering_filter")
        observation["summary_no_profitability_claim"] = summary.get(
            "no_profitability_claim")
        observation["summary_no_paper_or_live_authorization"] = (
            summary.get("no_paper_or_live_authorization"))
    if not labels_file.is_file():
        return observation
    observation["labels_exists"] = True
    raw = labels_file.read_bytes()
    observation["labels_sha256"] = _hashlib.sha256(raw).hexdigest()
    lines = raw.decode("utf-8").splitlines()
    observation["labels_line_count"] = len(lines)
    labels = [_json.loads(line) for line in lines]
    per_symbol: dict[str, dict[str, int]] = {}
    kept_ids: list[str] = []
    accepted_before = 0
    accepted_after = 0
    removed_by_clustering = 0
    scanner_rejected = 0
    floor_pass = {"2r": 0, "3r": 0, "4r": 0}
    floor_fail = {"2r": 0, "3r": 0, "4r": 0}
    all_pass = True
    for label in labels:
        sym = per_symbol.setdefault(label["symbol"], {
            "attempts": 0, "accepted_before_edit": 0,
            "accepted_after_edit": 0,
            "scanner_rejected": 0,
            "removed_by_clustering": 0,
            "floor_pass_2r": 0, "floor_pass_3r": 0,
            "floor_pass_4r": 0, "floor_fail": 0})
        sym["attempts"] += 1
        status = label["status"]
        kept_flag = label.get("kept_after_clustering_filter")
        if status == "accepted_for_replay_review":
            accepted_before += 1
            sym["accepted_before_edit"] += 1
            if kept_flag is True:
                kept_ids.append(label["setup_id"])
                accepted_after += 1
                sym["accepted_after_edit"] += 1
                for name in ("2r", "3r", "4r"):
                    if label["accepted_for_labeling_by_variant"][name]:
                        sym["floor_pass_" + name] += 1
                        floor_pass[name] += 1
                    else:
                        sym["floor_fail"] += 1
                        floor_fail[name] += 1
                if not all(label["accepted_for_labeling_by_variant"][
                        name] for name in ("2r", "3r", "4r")):
                    all_pass = False
            elif kept_flag is False:
                removed_by_clustering += 1
                sym["removed_by_clustering"] += 1
            else:
                all_pass = False
        else:
            scanner_rejected += 1
            sym["scanner_rejected"] += 1
            if kept_flag is not None:
                all_pass = False
    observation["accepted_count_before_edit"] = accepted_before
    observation["accepted_count_after_edit"] = accepted_after
    observation["removed_by_clustering_total"] = removed_by_clustering
    observation["scanner_rejected_total"] = scanner_rejected
    observation["per_symbol_counts"] = per_symbol
    observation["kept_accepted_setup_ids"] = tuple(sorted(kept_ids))
    observation["floor_pass_after_edit"] = floor_pass
    observation["floor_fail_after_edit"] = floor_fail
    observation[
        "all_kept_pass_floor_at_all_variants"] = bool(all_pass)
    return observation


def certify_c6_edited_labels_review(observation: Any
                                    ) -> dict[str, Any]:
    """Pure certification of an observation against the frozen facts."""
    failures: list[str] = []
    if not isinstance(observation, dict):
        return {"certified": False,
                "failures": ["observation_not_a_dict"]}
    o = observation
    if not o.get("labels_exists"):
        failures.append("edited_labels_artifact_missing")
    if not o.get("summary_exists"):
        failures.append("edited_summary_artifact_missing")
    if failures:
        return {"certified": False, "failures": failures}
    if o.get("labels_sha256") != EXPECTED_LABELS_SHA256:
        failures.append("edited_labels_sha_mismatch")
    if o.get("summary_sha256") != EXPECTED_SUMMARY_SHA256:
        failures.append("edited_summary_sha_mismatch")
    if o.get("labels_line_count") != EXPECTED_TOTAL_ATTEMPTS:
        failures.append("label_count_must_equal_389")
    if o.get("accepted_count_before_edit") != (
            EXPECTED_ACCEPTED_BEFORE_EDIT):
        failures.append("accepted_before_edit_must_equal_135")
    if o.get("accepted_count_after_edit") != (
            EXPECTED_ACCEPTED_AFTER_EDIT):
        failures.append("accepted_after_edit_must_equal_36")
    if o.get("removed_by_clustering_total") != (
            EXPECTED_REMOVED_BY_CLUSTERING_TOTAL):
        failures.append("removed_by_clustering_total_must_equal_99")
    if o.get("scanner_rejected_total") != (
            EXPECTED_SCANNER_REJECTED_TOTAL):
        failures.append("scanner_rejected_total_must_equal_254")
    per_symbol = o.get("per_symbol_counts") or {}
    for symbol in ("BTCUSD", "ETHUSD", "SOLUSD"):
        if per_symbol.get(symbol) != EXPECTED_PER_SYMBOL_EDITED[symbol]:
            failures.append("per_symbol_counts_mismatch:" + symbol)
    if set(per_symbol) - {"BTCUSD", "ETHUSD", "SOLUSD"}:
        failures.append("unexpected_symbols_in_labels")
    if o.get("kept_accepted_setup_ids") != (
            EXPECTED_KEPT_ACCEPTED_SETUP_IDS):
        failures.append("kept_accepted_setup_ids_mismatch")
    if o.get("floor_pass_after_edit") != EXPECTED_FLOOR_PASS_AFTER_EDIT:
        failures.append("floor_pass_after_edit_mismatch")
    if o.get("floor_fail_after_edit") != EXPECTED_FLOOR_FAIL_AFTER_EDIT:
        failures.append("floor_fail_after_edit_must_be_zero_everywhere")
    if o.get("all_kept_pass_floor_at_all_variants") is not True:
        failures.append("kept_set_must_pass_all_variant_floors")
    if o.get("edit_constants_in_summary") != EXPECTED_EDIT_CONSTANTS:
        failures.append("edit_constants_in_summary_mismatch")
    if o.get("summary_aggregation_counts") != (
            EXPECTED_AGGREGATION_COUNTS_FROZEN):
        failures.append("aggregation_counts_in_summary_mismatch")
    if o.get("summary_alignment_status") != (
            EXPECTED_ALIGNMENT_STATUS_FROZEN):
        failures.append("alignment_status_in_summary_mismatch")
    if o.get("summary_replay_executed_now") is not False:
        failures.append("summary_must_record_no_replay_executed")
    if o.get("summary_no_second_edit") is not True:
        failures.append("summary_must_record_no_second_edit")
    if o.get("summary_no_detector_rewrite") is not True:
        failures.append("summary_must_record_no_detector_rewrite")
    if o.get("summary_no_parameter_changes") is not True:
        failures.append("summary_must_record_no_parameter_changes")
    if o.get("summary_no_profitability_claim") is not True:
        failures.append("summary_must_record_no_profitability_claim")
    if o.get("summary_no_paper_or_live_authorization") is not True:
        failures.append("summary_must_record_no_paper_or_live")
    if o.get("staged_shas_match") is not True:
        failures.append("staged_data_shas_changed_by_or_after_edit")
    if o.get("candidate_id_in_summary") != CANDIDATE_ID:
        failures.append("summary_candidate_id_mismatch")
    if o.get("artifacts_tracked_in_git"):
        failures.append(
            "edited_runner_and_artifacts_must_stay_untracked")
    return {"certified": not failures, "failures": failures}


def build_c6_edited_labels_review(repo_root: Any,
                                  tracked_paths: Any = ()
                                  ) -> dict[str, Any]:
    """Observe read-only and certify; chain-gated on the full pushed C6
    lane plus the single-edit contract plus Recommendation V1 plus
    Autopilot V1 plus the five-record rejection ledger."""
    record: dict[str, Any] = {
        "schema_version": C6EL_SCHEMA_VERSION, "label": C6EL_LABEL,
        "mode": C6EL_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [], "failures": [],
        "candidate_id": CANDIDATE_ID,
        "head_at_edited_relabel": HEAD_AT_EDITED_RELABEL,
        "runner_path_untracked_only": RUNNER_PATH,
        "labels_path": LABELS_PATH, "summary_path": SUMMARY_PATH,
        "expected_labels_sha256": EXPECTED_LABELS_SHA256,
        "expected_summary_sha256": EXPECTED_SUMMARY_SHA256,
        "expected_staged_shas":
            dict(EXPECTED_STAGED_SHAS_FROZEN),
        "expected_edit_constants": dict(EXPECTED_EDIT_CONSTANTS),
        "expected_aggregation_counts":
            dict(EXPECTED_AGGREGATION_COUNTS_FROZEN),
        "expected_alignment_status":
            EXPECTED_ALIGNMENT_STATUS_FROZEN,
        "expected_total_attempts": EXPECTED_TOTAL_ATTEMPTS,
        "expected_accepted_before_edit":
            EXPECTED_ACCEPTED_BEFORE_EDIT,
        "expected_accepted_after_edit":
            EXPECTED_ACCEPTED_AFTER_EDIT,
        "expected_removed_by_clustering_total":
            EXPECTED_REMOVED_BY_CLUSTERING_TOTAL,
        "expected_scanner_rejected_total":
            EXPECTED_SCANNER_REJECTED_TOTAL,
        "expected_per_symbol_edited": {
            sym: dict(value) for sym, value
            in EXPECTED_PER_SYMBOL_EDITED.items()},
        "expected_floor_pass_after_edit":
            dict(EXPECTED_FLOOR_PASS_AFTER_EDIT),
        "expected_floor_fail_after_edit":
            dict(EXPECTED_FLOOR_FAIL_AFTER_EDIT),
        "expected_kept_accepted_setup_ids":
            list(EXPECTED_KEPT_ACCEPTED_SETUP_IDS),
        "frozen_review_facts": list(FROZEN_EDITED_REVIEW_FACTS),
        "claim_locks": list(CLAIM_LOCKS),
        "human_review_required": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True, "live_gate_locked": True,
        "edit_authorized_by_this_gate": False,
        "second_edit_possible": False,
        "rejection_decision_by_this_gate": False,
        "replay_authorized_by_this_gate": False,
        "labels_changed_by_this_gate": False,
        "detector_changed_by_this_gate": False,
        "executes": False, "writes_files": False, "labels_now": False,
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
        "authorizes_paper_execution": False,
        "authorizes_micro_live": False, "authorizes_live_trading": False,
        "promotes_gate": False, "unlocks_downstream_gate": False,
        "claims_profitability": False,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    if not (C1_STATUS == C2_STATUS == C3_STATUS == C4_STATUS
            == C5_STATUS == "REJECTED_KEPT_ON_RECORD"):
        record["verdict"] = VERDICT_C6EL_BLOCKED
        record["blockers"].append("ledger_broken")
        return record
    if build_candidate_6_family_proposal()["verdict"] != (
            VERDICT_C6P_READY):
        record["verdict"] = VERDICT_C6EL_BLOCKED
        record["blockers"].append("family_proposal_not_certifying")
        return record
    if build_candidate_6_spec_review()["verdict"] != VERDICT_C6S_READY:
        record["verdict"] = VERDICT_C6EL_BLOCKED
        record["blockers"].append("spec_review_not_certifying")
        return record
    if build_c6_dry_run_review()["verdict"] != VERDICT_C6R_FROZEN:
        record["verdict"] = VERDICT_C6EL_BLOCKED
        record["blockers"].append("dry_run_review_not_certifying")
        return record
    labels_review = build_c6_labels_review(repo_root, tracked_paths)
    if labels_review["verdict"] != VERDICT_C6L_FROZEN:
        record["verdict"] = VERDICT_C6EL_BLOCKED
        record["blockers"].append(
            "original_labels_review_not_certifying")
        record["blockers"].extend(labels_review["failures"])
        return record
    replay_review = build_c6_replay_results_review(repo_root,
                                                   tracked_paths)
    if replay_review["verdict"] != VERDICT_C6RR_FROZEN:
        record["verdict"] = VERDICT_C6EL_BLOCKED
        record["blockers"].append(
            "replay_results_review_not_certifying")
        record["blockers"].extend(replay_review["failures"])
        return record
    single_edit = build_c6_single_edit_clustering_filter(repo_root,
                                                         tracked_paths)
    if single_edit["verdict"] != VERDICT_C6E_READY:
        record["verdict"] = VERDICT_C6EL_BLOCKED
        record["blockers"].append(
            "single_edit_contract_not_certifying")
        return record
    if _rec.build_candidate_recommendation()["verdict"] != (
            _rec.VERDICT_CR_READY):
        record["verdict"] = VERDICT_C6EL_BLOCKED
        record["blockers"].append("recommendation_not_certifying")
        return record
    if _loop.build_autopilot_loop_contract()["verdict"] != (
            _loop.VERDICT_AP_READY):
        record["verdict"] = VERDICT_C6EL_BLOCKED
        record["blockers"].append("autopilot_loop_not_certifying")
        return record
    observation = observe_c6_edited_labels(repo_root, tracked_paths)
    result = certify_c6_edited_labels_review(observation)
    record["failures"] = result["failures"]
    record["verdict"] = (VERDICT_C6EL_FROZEN if result["certified"]
                         else VERDICT_C6EL_REJECTED)
    return record


def validate_c6_edited_labels_review(record: Any) -> dict[str, Any]:
    """Validate shape, frozen facts, and safety invariants. Never
    raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_C6EL_FROZEN,
                                VERDICT_C6EL_REJECTED,
                                VERDICT_C6EL_BLOCKED):
        errors.append("bad_verdict")
    if r.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if r.get("head_at_edited_relabel") != HEAD_AT_EDITED_RELABEL:
        errors.append("head_tampered")
    if r.get("expected_labels_sha256") != EXPECTED_LABELS_SHA256:
        errors.append("labels_sha_tampered")
    if r.get("expected_summary_sha256") != EXPECTED_SUMMARY_SHA256:
        errors.append("summary_sha_tampered")
    if r.get("expected_staged_shas") != EXPECTED_STAGED_SHAS_FROZEN:
        errors.append("staged_shas_tampered")
    if r.get("expected_edit_constants") != EXPECTED_EDIT_CONSTANTS:
        errors.append("edit_constants_tampered")
    if r.get("expected_aggregation_counts") != (
            EXPECTED_AGGREGATION_COUNTS_FROZEN):
        errors.append("aggregation_counts_tampered")
    if r.get("expected_alignment_status") != (
            EXPECTED_ALIGNMENT_STATUS_FROZEN):
        errors.append("alignment_status_tampered")
    if r.get("expected_total_attempts") != EXPECTED_TOTAL_ATTEMPTS:
        errors.append("total_attempts_tampered")
    if r.get("expected_accepted_before_edit") != (
            EXPECTED_ACCEPTED_BEFORE_EDIT):
        errors.append("accepted_before_edit_tampered")
    if r.get("expected_accepted_after_edit") != (
            EXPECTED_ACCEPTED_AFTER_EDIT):
        errors.append("accepted_after_edit_tampered")
    if r.get("expected_removed_by_clustering_total") != (
            EXPECTED_REMOVED_BY_CLUSTERING_TOTAL):
        errors.append("removed_by_clustering_total_tampered")
    if r.get("expected_scanner_rejected_total") != (
            EXPECTED_SCANNER_REJECTED_TOTAL):
        errors.append("scanner_rejected_total_tampered")
    expected_split = {sym: dict(value) for sym, value
                      in EXPECTED_PER_SYMBOL_EDITED.items()}
    if r.get("expected_per_symbol_edited") != expected_split:
        errors.append("per_symbol_edited_tampered")
    if r.get("expected_floor_pass_after_edit") != (
            EXPECTED_FLOOR_PASS_AFTER_EDIT):
        errors.append("floor_pass_after_edit_tampered")
    if r.get("expected_floor_fail_after_edit") != (
            EXPECTED_FLOOR_FAIL_AFTER_EDIT):
        errors.append("floor_fail_after_edit_tampered")
    if tuple(r.get("expected_kept_accepted_setup_ids") or ()) != (
            EXPECTED_KEPT_ACCEPTED_SETUP_IDS):
        errors.append("kept_accepted_setup_ids_tampered")
    if tuple(r.get("frozen_review_facts") or ()) != (
            FROZEN_EDITED_REVIEW_FACTS):
        errors.append("frozen_review_facts_tampered")
    if tuple(r.get("claim_locks") or ()) != CLAIM_LOCKS:
        errors.append("claim_locks_tampered")
    for key in ("edit_authorized_by_this_gate",
                "second_edit_possible",
                "rejection_decision_by_this_gate",
                "replay_authorized_by_this_gate",
                "labels_changed_by_this_gate",
                "detector_changed_by_this_gate"):
        if r.get(key) is not False:
            errors.append("downstream_lock_wrong:" + key)
    if r.get("verdict") == VERDICT_C6EL_FROZEN and r.get("failures"):
        errors.append("frozen_with_failures")
    for key, want in (("human_review_required", True),
                      ("paper_trading_gate_locked", True),
                      ("micro_live_gate_locked", True),
                      ("live_gate_locked", True)):
        if r.get(key) is not want:
            errors.append("constitution_flag_wrong:" + key)
    for key in ("executes", "writes_files", "labels_now",
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
                "authorizes_paper_execution", "authorizes_micro_live",
                "authorizes_live_trading", "promotes_gate",
                "unlocks_downstream_gate", "claims_profitability"):
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)
    if r.get("next_required_action") != NEXT_REQUIRED_ACTION:
        errors.append("next_required_action_tampered")
    # the kept set is a strict subset of the original accepted set
    kept = set(r.get("expected_kept_accepted_setup_ids") or ())
    if not kept.issubset(set(ORIGINAL_ACCEPTED_SETUP_IDS)):
        errors.append("kept_set_must_be_subset_of_original_accepted")
    if len(kept) != EXPECTED_ACCEPTED_AFTER_EDIT:
        errors.append("kept_set_size_must_equal_36")
    return {"valid": not errors, "errors": errors}
