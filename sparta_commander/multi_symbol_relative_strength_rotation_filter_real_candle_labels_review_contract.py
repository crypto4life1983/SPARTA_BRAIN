"""SPARTA CANDIDATE #6 REAL-CANDLE DETECTOR LABELS REVIEW / EVIDENCE
FREEZE (READ-ONLY, RESEARCH ONLY):
MULTI_SYMBOL_RELATIVE_STRENGTH_ROTATION_FILTER_V1.

Freezes the one-pass real-candle detection result: 389 attempts across
BTCUSD/ETHUSD/SOLUSD on the existing staged 15m data (aggregated to 1h
by the pushed aggregator, all three symbols loaded simultaneously with
timestamp alignment asserted across the universe), 135 setups accepted
with EVERY accepted setup clearing the 81 bps floor at every variant.

WHAT THIS IS NOT: no replay has run; no edge has been demonstrated; no
profitability exists or is claimed. The strict-rank-#1 filter is the
dominant constraint (231/254 = 91% of rejections), exactly as the
family was designed; SOLUSD's higher accept rate (71 vs ~32 for the
other two) is consistent with the seed observation that SOL was
structurally strongest in this sample window. These are LABELS. Replay,
edit, and rejection are all separate downstream human gates -- nothing
here authorizes any of them.

This module observes the untracked artifacts READ-ONLY, recounts all
389 labels from the JSONL itself, re-verifies the six staged-data
shas, and certifies every frozen fact. It runs nothing, fetches
nothing, and authorizes nothing.
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
from sparta_commander.multi_symbol_relative_strength_rotation_filter_detector_spec_contract import (
    C6_DETECTOR_STATUSES,
    VERDICT_C6D_READY,
    build_c6_detector_spec_contract,
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

C6L_SCHEMA_VERSION = (
    "multi_symbol_relative_strength_rotation_filter_real_candle_labels"
    "_review.v1")
C6L_LABEL = ("SPARTA Candidate #6 Real-Candle Labels Review / Evidence "
             "Freeze (READ-ONLY, RESEARCH ONLY, 135 LABELS FROZEN, "
             "NOT A PROFITABILITY CLAIM)")
C6L_MODE = "RESEARCH_ONLY"
VERDICT_C6L_FROZEN = (
    "CANDIDATE_6_REAL_CANDLE_LABELS_FROZEN_READY_FOR_HUMAN_REVIEW")
VERDICT_C6L_REJECTED = "CANDIDATE_6_LABELS_REVIEW_REJECTED"
VERDICT_C6L_BLOCKED = "CANDIDATE_6_LABELS_REVIEW_BLOCKED"
NEXT_REQUIRED_ACTION = (
    "HUMAN_DECISION_C6_REPLAY_OR_EDIT_OR_REJECT")

HEAD_AT_DETECTION = "2e0622501be4ec2dbb4c8cc3adb28af50003be89"
RUNNER_PATH = "tools/c6_real_candle_detection_once.py"
LABELS_PATH = ("data/rs_rotation_c6/detector_labels/"
               "c6_detector_labels_2026-05-02_2026-06-10.jsonl")
SUMMARY_PATH = ("data/rs_rotation_c6/detector_labels/"
                "c6_detector_summary_2026-05-02_2026-06-10.json")
EXPECTED_LABELS_SHA256 = (
    "bc8471fc78bbfe409b5cb0efa951608cddd73f3485d66dbd8d711bb1f4307d7a")
EXPECTED_SUMMARY_SHA256 = (
    "110b84b2ad96de5136d1a89da4ef26f2fbd1b4a0f45527f5e0f1a0c612fc18c7")

EXPECTED_STAGED_SHAS = {
    "data/ny_fvg_choch/staged/BTCUSD_15m_2026-05-02_2026-06-09.csv":
        "4ee373b28caeafa47d463e0fc2582f1958b877a8f05df0714a0afd1298ee"
        "9f14",
    "data/ny_fvg_choch/staged/BTCUSD_15m_2026-06-01_2026-06-10.csv":
        "4bb50873df5194de65315bf44f1823d17922e445745401eb01aa1670aed4"
        "956d",
    "data/ny_fvg_choch/staged/ETHUSD_15m_2026-05-02_2026-06-09.csv":
        "2d96b6a1ed82293fc63fecf2f1948fd1990e0a1b42827670d6fcdce9abd6"
        "f980",
    "data/ny_fvg_choch/staged/ETHUSD_15m_2026-06-01_2026-06-10.csv":
        "bc7e86f1e2294b2a826675eb80ee51f95a4f2b5ef55212eadad924716687"
        "55f1",
    "data/ny_fvg_choch/staged/SOLUSD_15m_2026-05-02_2026-06-09.csv":
        "f782856870d5d5652f3a42c619419fc56f90e89fdf5b036a56eeb347aee2"
        "f884",
    "data/ny_fvg_choch/staged/SOLUSD_15m_2026-06-01_2026-06-10.csv":
        "3437bf5d580f71108a1f5034104955eaf5d4bb4cd2255ea0dcd625c7b15b"
        "2f65",
}

EXPECTED_AGGREGATION_COUNTS = {
    "BTCUSD": {"bars_15m": 3840, "bars_1h": 960},
    "ETHUSD": {"bars_15m": 3840, "bars_1h": 960},
    "SOLUSD": {"bars_15m": 3840, "bars_1h": 960},
}
EXPECTED_ALIGNMENT_STATUS = "aligned_across_btcusd_ethusd_solusd"

EXPECTED_COUNTS = {
    "BTCUSD": {"attempts": 127, "accepted": 32, "rejected": 95,
               "rejected_not_strict_rank_1": 85,
               "rejected_rs_not_positive": 10,
               "floor_pass_2r": 32, "floor_pass_3r": 32,
               "floor_pass_4r": 32, "floor_fail": 0},
    "ETHUSD": {"attempts": 130, "accepted": 32, "rejected": 98,
               "rejected_not_strict_rank_1": 88,
               "rejected_rs_not_positive": 10,
               "floor_pass_2r": 32, "floor_pass_3r": 32,
               "floor_pass_4r": 32, "floor_fail": 0},
    "SOLUSD": {"attempts": 132, "accepted": 71, "rejected": 61,
               "rejected_not_strict_rank_1": 58,
               "rejected_rs_not_positive": 3,
               "floor_pass_2r": 71, "floor_pass_3r": 71,
               "floor_pass_4r": 71, "floor_fail": 0},
    "total": {"attempts": 389, "accepted": 135, "rejected": 254,
              "rejected_not_strict_rank_1": 231,
              "rejected_rs_not_positive": 23,
              "floor_pass_2r": 135, "floor_pass_3r": 135,
              "floor_pass_4r": 135, "floor_fail": 0},
}

EXPECTED_STATUS_BREAKDOWN = {
    "accepted_for_replay_review": 135,
    "rejected_not_strict_rank_1": 231,
    "rejected_rs_not_positive": 23,
}

EXPECTED_ACCEPTED_SETUP_IDS = (
    "BTCUSD_2026-05-04T17:00:00Z", "BTCUSD_2026-05-05T02:00:00Z",
    "BTCUSD_2026-05-05T03:00:00Z", "BTCUSD_2026-05-05T04:00:00Z",
    "BTCUSD_2026-05-05T05:00:00Z", "BTCUSD_2026-05-05T06:00:00Z",
    "BTCUSD_2026-05-05T12:00:00Z", "BTCUSD_2026-05-05T13:00:00Z",
    "BTCUSD_2026-05-05T14:00:00Z", "BTCUSD_2026-05-05T15:00:00Z",
    "BTCUSD_2026-05-08T11:00:00Z", "BTCUSD_2026-05-13T02:00:00Z",
    "BTCUSD_2026-05-13T03:00:00Z", "BTCUSD_2026-05-14T14:00:00Z",
    "BTCUSD_2026-05-14T16:00:00Z", "BTCUSD_2026-05-20T08:00:00Z",
    "BTCUSD_2026-05-20T09:00:00Z", "BTCUSD_2026-05-20T10:00:00Z",
    "BTCUSD_2026-05-20T12:00:00Z", "BTCUSD_2026-05-23T18:00:00Z",
    "BTCUSD_2026-05-24T23:00:00Z", "BTCUSD_2026-05-25T00:00:00Z",
    "BTCUSD_2026-05-25T04:00:00Z", "BTCUSD_2026-05-25T05:00:00Z",
    "BTCUSD_2026-05-25T06:00:00Z", "BTCUSD_2026-05-25T08:00:00Z",
    "BTCUSD_2026-05-25T09:00:00Z", "BTCUSD_2026-05-25T14:00:00Z",
    "BTCUSD_2026-05-30T14:00:00Z", "BTCUSD_2026-06-10T13:00:00Z",
    "BTCUSD_2026-06-10T14:00:00Z", "BTCUSD_2026-06-10T15:00:00Z",
    "ETHUSD_2026-05-02T20:00:00Z", "ETHUSD_2026-05-02T21:00:00Z",
    "ETHUSD_2026-05-02T22:00:00Z", "ETHUSD_2026-05-03T11:00:00Z",
    "ETHUSD_2026-05-03T12:00:00Z", "ETHUSD_2026-05-03T14:00:00Z",
    "ETHUSD_2026-05-03T15:00:00Z", "ETHUSD_2026-05-03T17:00:00Z",
    "ETHUSD_2026-05-03T19:00:00Z", "ETHUSD_2026-05-03T22:00:00Z",
    "ETHUSD_2026-05-04T01:00:00Z", "ETHUSD_2026-05-04T02:00:00Z",
    "ETHUSD_2026-05-04T03:00:00Z", "ETHUSD_2026-05-04T04:00:00Z",
    "ETHUSD_2026-05-13T04:00:00Z", "ETHUSD_2026-05-13T08:00:00Z",
    "ETHUSD_2026-05-13T09:00:00Z", "ETHUSD_2026-05-17T12:00:00Z",
    "ETHUSD_2026-05-20T05:00:00Z", "ETHUSD_2026-05-20T06:00:00Z",
    "ETHUSD_2026-05-23T20:00:00Z", "ETHUSD_2026-05-25T16:00:00Z",
    "ETHUSD_2026-05-29T15:00:00Z", "ETHUSD_2026-05-29T16:00:00Z",
    "ETHUSD_2026-05-31T01:00:00Z", "ETHUSD_2026-05-31T02:00:00Z",
    "ETHUSD_2026-06-06T23:00:00Z", "ETHUSD_2026-06-07T21:00:00Z",
    "ETHUSD_2026-06-07T22:00:00Z", "ETHUSD_2026-06-07T23:00:00Z",
    "ETHUSD_2026-06-08T00:00:00Z", "ETHUSD_2026-06-08T12:00:00Z",
    "SOLUSD_2026-05-05T18:00:00Z", "SOLUSD_2026-05-05T19:00:00Z",
    "SOLUSD_2026-05-05T20:00:00Z", "SOLUSD_2026-05-05T21:00:00Z",
    "SOLUSD_2026-05-06T01:00:00Z", "SOLUSD_2026-05-06T02:00:00Z",
    "SOLUSD_2026-05-06T03:00:00Z", "SOLUSD_2026-05-06T05:00:00Z",
    "SOLUSD_2026-05-06T06:00:00Z", "SOLUSD_2026-05-06T07:00:00Z",
    "SOLUSD_2026-05-06T08:00:00Z", "SOLUSD_2026-05-06T09:00:00Z",
    "SOLUSD_2026-05-06T11:00:00Z", "SOLUSD_2026-05-07T07:00:00Z",
    "SOLUSD_2026-05-08T10:00:00Z", "SOLUSD_2026-05-08T14:00:00Z",
    "SOLUSD_2026-05-08T15:00:00Z", "SOLUSD_2026-05-08T17:00:00Z",
    "SOLUSD_2026-05-08T18:00:00Z", "SOLUSD_2026-05-08T19:00:00Z",
    "SOLUSD_2026-05-09T01:00:00Z", "SOLUSD_2026-05-09T03:00:00Z",
    "SOLUSD_2026-05-09T05:00:00Z", "SOLUSD_2026-05-09T07:00:00Z",
    "SOLUSD_2026-05-10T08:00:00Z", "SOLUSD_2026-05-10T09:00:00Z",
    "SOLUSD_2026-05-10T15:00:00Z", "SOLUSD_2026-05-10T16:00:00Z",
    "SOLUSD_2026-05-10T17:00:00Z", "SOLUSD_2026-05-11T15:00:00Z",
    "SOLUSD_2026-05-11T16:00:00Z", "SOLUSD_2026-05-11T17:00:00Z",
    "SOLUSD_2026-05-11T19:00:00Z", "SOLUSD_2026-05-14T15:00:00Z",
    "SOLUSD_2026-05-17T05:00:00Z", "SOLUSD_2026-05-17T07:00:00Z",
    "SOLUSD_2026-05-17T10:00:00Z", "SOLUSD_2026-05-17T21:00:00Z",
    "SOLUSD_2026-05-20T14:00:00Z", "SOLUSD_2026-05-20T15:00:00Z",
    "SOLUSD_2026-05-20T16:00:00Z", "SOLUSD_2026-05-20T17:00:00Z",
    "SOLUSD_2026-05-21T00:00:00Z", "SOLUSD_2026-05-21T03:00:00Z",
    "SOLUSD_2026-05-21T04:00:00Z", "SOLUSD_2026-05-21T17:00:00Z",
    "SOLUSD_2026-05-21T19:00:00Z", "SOLUSD_2026-05-22T11:00:00Z",
    "SOLUSD_2026-05-22T12:00:00Z", "SOLUSD_2026-05-23T19:00:00Z",
    "SOLUSD_2026-05-24T08:00:00Z", "SOLUSD_2026-05-24T09:00:00Z",
    "SOLUSD_2026-05-27T15:00:00Z", "SOLUSD_2026-05-28T18:00:00Z",
    "SOLUSD_2026-05-29T09:00:00Z", "SOLUSD_2026-05-30T02:00:00Z",
    "SOLUSD_2026-05-30T15:00:00Z", "SOLUSD_2026-05-30T16:00:00Z",
    "SOLUSD_2026-05-30T17:00:00Z", "SOLUSD_2026-05-31T03:00:00Z",
    "SOLUSD_2026-06-07T01:00:00Z", "SOLUSD_2026-06-07T03:00:00Z",
    "SOLUSD_2026-06-07T04:00:00Z", "SOLUSD_2026-06-07T05:00:00Z",
    "SOLUSD_2026-06-07T06:00:00Z", "SOLUSD_2026-06-07T07:00:00Z",
    "SOLUSD_2026-06-07T08:00:00Z", "SOLUSD_2026-06-08T17:00:00Z",
    "SOLUSD_2026-06-08T18:00:00Z", "SOLUSD_2026-06-08T19:00:00Z",
    "SOLUSD_2026-06-08T20:00:00Z",
)

FROZEN_DETECTION_FACTS = (
    "existing staged btcusd/ethusd/solusd 15m data only; no fetch",
    "all three symbols loaded simultaneously for the rs gate",
    "15m aggregated to 1h by the pushed aggregator; 960 1h bars each",
    "timestamp alignment asserted across the full universe at every "
    "index",
    "pushed scan_c6_setups ran exactly once per symbol; rules cannot "
    "drift",
    "no replay; labels only; no staged-data modification",
    "every accepted setup clears the 81 bps floor at every variant; "
    "zero floor-fail across the accepted set",
    "strict-rank-#1 is the dominant constraint at 231/254 of all "
    "rejections",
    "solusd accepted 71 of 132 attempts; ethusd 32 of 130; btcusd 32 "
    "of 127 -- consistent with the seed observation that sol was "
    "structurally strongest in this window",
    "non-overlap is exit-dependent and applies at replay policy time "
    "per the frozen spec; no removals occur at label time",
)

CLAIM_LOCKS = (
    "no_profitability_claim",
    "no_paper_approval",
    "no_live_approval",
    "no_execution_approval",
    "no_winner_wording",
    "no_replay_authorized_by_this_gate",
    "no_edit_or_rejection_decision_made_yet",
)


def get_c6_labels_review_label() -> str:
    return C6L_LABEL


def observe_c6_labels(repo_root: Any,
                      tracked_paths: Any = ()) -> dict[str, Any]:
    """Read the artifacts READ-ONLY and recount the facts. Never raises
    on missing files; reports absence instead."""
    observation: dict[str, Any] = {
        "labels_exists": False, "summary_exists": False,
        "labels_sha256": None, "summary_sha256": None,
        "labels_line_count": None, "status_breakdown": None,
        "accepted_count": None, "per_symbol_counts": None,
        "accepted_setup_ids": None,
        "floor_pass_all_variants_for_all_accepted": None,
        "staged_shas_now": None, "staged_shas_match": None,
        "aggregation_counts": None, "alignment_status": None,
        "candidate_id_in_summary": None,
        "artifacts_tracked_in_git": [],
    }
    root = _pathlib.Path(str(repo_root))
    tracked = {str(p).replace("\\", "/") for p in (tracked_paths or ())}
    for rel in (LABELS_PATH, SUMMARY_PATH, RUNNER_PATH):
        if rel in tracked:
            observation["artifacts_tracked_in_git"].append(rel)
    staged_now = {}
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
        observation["candidate_id_in_summary"] = summary.get(
            "candidate_id")
        observation["aggregation_counts"] = summary.get(
            "aggregation_counts")
        observation["alignment_status"] = summary.get(
            "timestamp_alignment_status")
    if not labels_file.is_file():
        return observation
    observation["labels_exists"] = True
    raw = labels_file.read_bytes()
    observation["labels_sha256"] = _hashlib.sha256(raw).hexdigest()
    lines = raw.decode("utf-8").splitlines()
    observation["labels_line_count"] = len(lines)
    labels = [_json.loads(line) for line in lines]
    breakdown: dict[str, int] = {}
    per_symbol: dict[str, dict[str, int]] = {}
    accepted = []
    for label in labels:
        breakdown[label["status"]] = breakdown.get(label["status"], 0) + 1
        sym = per_symbol.setdefault(label["symbol"], {
            "attempts": 0, "accepted": 0, "rejected": 0,
            "rejected_not_strict_rank_1": 0,
            "rejected_rs_not_positive": 0,
            "floor_pass_2r": 0, "floor_pass_3r": 0,
            "floor_pass_4r": 0, "floor_fail": 0})
        sym["attempts"] += 1
        if label["status"] == "accepted_for_replay_review":
            sym["accepted"] += 1
            accepted.append(label)
            for name in ("2r", "3r", "4r"):
                if label["accepted_for_labeling_by_variant"][name]:
                    sym["floor_pass_" + name] += 1
                else:
                    sym["floor_fail"] += 1
        else:
            sym["rejected"] += 1
            if label["status"] == "rejected_not_strict_rank_1":
                sym["rejected_not_strict_rank_1"] += 1
            elif label["status"] == "rejected_rs_not_positive":
                sym["rejected_rs_not_positive"] += 1
    observation["status_breakdown"] = breakdown
    observation["per_symbol_counts"] = per_symbol
    observation["accepted_count"] = len(accepted)
    observation["accepted_setup_ids"] = tuple(sorted(
        label["setup_id"] for label in accepted))
    observation["floor_pass_all_variants_for_all_accepted"] = all(
        all(label["accepted_for_labeling_by_variant"][name]
            for name in ("2r", "3r", "4r"))
        for label in accepted) if accepted else None
    return observation


def certify_c6_labels_review(observation: Any) -> dict[str, Any]:
    """Pure certification of an observation against the frozen facts."""
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
    if o.get("labels_line_count") != EXPECTED_COUNTS["total"]["attempts"]:
        failures.append("label_count_mismatch")
    if o.get("accepted_count") != EXPECTED_COUNTS["total"]["accepted"]:
        failures.append("accepted_count_mismatch")
    if o.get("status_breakdown") != EXPECTED_STATUS_BREAKDOWN:
        failures.append("status_breakdown_mismatch")
    per_symbol = o.get("per_symbol_counts") or {}
    for symbol in ("BTCUSD", "ETHUSD", "SOLUSD"):
        if per_symbol.get(symbol) != EXPECTED_COUNTS[symbol]:
            failures.append("per_symbol_counts_mismatch:" + symbol)
    if set(per_symbol) - {"BTCUSD", "ETHUSD", "SOLUSD"}:
        failures.append("unexpected_symbols_in_labels")
    if o.get("accepted_setup_ids") != EXPECTED_ACCEPTED_SETUP_IDS:
        failures.append("accepted_setup_ids_mismatch")
    if o.get("floor_pass_all_variants_for_all_accepted") is not True:
        failures.append("accepted_set_must_pass_all_variant_floors")
    if o.get("staged_shas_match") is not True:
        failures.append("staged_data_shas_changed")
    if o.get("aggregation_counts") != EXPECTED_AGGREGATION_COUNTS:
        failures.append("aggregation_counts_mismatch")
    if o.get("alignment_status") != EXPECTED_ALIGNMENT_STATUS:
        failures.append("alignment_status_mismatch")
    if o.get("artifacts_tracked_in_git"):
        failures.append("runner_and_artifacts_must_stay_untracked")
    return {"certified": not failures, "failures": failures}


def build_c6_labels_review(repo_root: Any,
                           tracked_paths: Any = ()) -> dict[str, Any]:
    """Observe read-only and certify; gated on the full upstream chain
    and the five-record ledger."""
    record: dict[str, Any] = {
        "schema_version": C6L_SCHEMA_VERSION, "label": C6L_LABEL,
        "mode": C6L_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [], "failures": [],
        "candidate_id": CANDIDATE_ID,
        "head_at_detection": HEAD_AT_DETECTION,
        "runner_path_untracked_only": RUNNER_PATH,
        "labels_path": LABELS_PATH, "summary_path": SUMMARY_PATH,
        "expected_labels_sha256": EXPECTED_LABELS_SHA256,
        "expected_summary_sha256": EXPECTED_SUMMARY_SHA256,
        "expected_staged_shas": dict(EXPECTED_STAGED_SHAS),
        "expected_aggregation_counts": {
            sym: dict(value) for sym, value
            in EXPECTED_AGGREGATION_COUNTS.items()},
        "expected_alignment_status": EXPECTED_ALIGNMENT_STATUS,
        "expected_counts": {key: dict(value) for key, value
                            in EXPECTED_COUNTS.items()},
        "expected_status_breakdown": dict(EXPECTED_STATUS_BREAKDOWN),
        "expected_accepted_setup_ids": list(EXPECTED_ACCEPTED_SETUP_IDS),
        "frozen_detection_facts": list(FROZEN_DETECTION_FACTS),
        "claim_locks": list(CLAIM_LOCKS),
        "replay_has_run": False,
        "replay_authorized_by_this_gate": False,
        "edit_decision_made": False,
        "rejection_decision_made": False,
        "human_review_required": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True, "live_gate_locked": True,
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
        record["verdict"] = VERDICT_C6L_BLOCKED
        record["blockers"].append("ledger_broken")
        return record
    if build_c6_dry_run_review()["verdict"] != VERDICT_C6R_FROZEN:
        record["verdict"] = VERDICT_C6L_BLOCKED
        record["blockers"].append("dry_run_review_not_certifying")
        return record
    if build_c6_detector_spec_contract()["verdict"] != VERDICT_C6D_READY:
        record["verdict"] = VERDICT_C6L_BLOCKED
        record["blockers"].append("detector_spec_not_certifying")
        return record
    if build_candidate_6_spec_review()["verdict"] != VERDICT_C6S_READY:
        record["verdict"] = VERDICT_C6L_BLOCKED
        record["blockers"].append("spec_review_not_certifying")
        return record
    if build_candidate_6_family_proposal()["verdict"] != (
            VERDICT_C6P_READY):
        record["verdict"] = VERDICT_C6L_BLOCKED
        record["blockers"].append("family_proposal_not_certifying")
        return record
    if _rec.build_candidate_recommendation()["verdict"] != (
            _rec.VERDICT_CR_READY):
        record["verdict"] = VERDICT_C6L_BLOCKED
        record["blockers"].append("recommendation_not_certifying")
        return record
    if _loop.build_autopilot_loop_contract()["verdict"] != (
            _loop.VERDICT_AP_READY):
        record["verdict"] = VERDICT_C6L_BLOCKED
        record["blockers"].append("autopilot_loop_not_certifying")
        return record
    observation = observe_c6_labels(repo_root, tracked_paths)
    result = certify_c6_labels_review(observation)
    record["failures"] = result["failures"]
    record["verdict"] = (VERDICT_C6L_FROZEN if result["certified"]
                         else VERDICT_C6L_REJECTED)
    return record


def validate_c6_labels_review(record: Any) -> dict[str, Any]:
    """Validate shape, frozen facts, and safety invariants. Never
    raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_C6L_FROZEN, VERDICT_C6L_REJECTED,
                                VERDICT_C6L_BLOCKED):
        errors.append("bad_verdict")
    if r.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if r.get("head_at_detection") != HEAD_AT_DETECTION:
        errors.append("head_tampered")
    if r.get("expected_labels_sha256") != EXPECTED_LABELS_SHA256:
        errors.append("labels_sha_tampered")
    if r.get("expected_summary_sha256") != EXPECTED_SUMMARY_SHA256:
        errors.append("summary_sha_tampered")
    if r.get("expected_staged_shas") != EXPECTED_STAGED_SHAS:
        errors.append("staged_shas_tampered")
    expected_agg = {sym: dict(value) for sym, value
                    in EXPECTED_AGGREGATION_COUNTS.items()}
    if r.get("expected_aggregation_counts") != expected_agg:
        errors.append("aggregation_counts_tampered")
    if r.get("expected_alignment_status") != EXPECTED_ALIGNMENT_STATUS:
        errors.append("alignment_status_tampered")
    expected_counts = {key: dict(value) for key, value
                       in EXPECTED_COUNTS.items()}
    if r.get("expected_counts") != expected_counts:
        errors.append("counts_tampered")
    if r.get("expected_status_breakdown") != EXPECTED_STATUS_BREAKDOWN:
        errors.append("breakdown_tampered")
    if tuple(r.get("expected_accepted_setup_ids") or ()) != (
            EXPECTED_ACCEPTED_SETUP_IDS):
        errors.append("accepted_setup_ids_tampered")
    if tuple(r.get("frozen_detection_facts") or ()) != (
            FROZEN_DETECTION_FACTS):
        errors.append("detection_facts_tampered")
    if tuple(r.get("claim_locks") or ()) != CLAIM_LOCKS:
        errors.append("claim_locks_tampered")
    for key in ("replay_has_run", "replay_authorized_by_this_gate",
                "edit_decision_made", "rejection_decision_made"):
        if r.get(key) is not False:
            errors.append("downstream_decision_flag_wrong:" + key)
    if r.get("verdict") == VERDICT_C6L_FROZEN and r.get("failures"):
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
    return {"valid": not errors, "errors": errors}
