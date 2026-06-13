"""SPARTA CANDIDATE #5 REAL-CANDLE DETECTOR LABELS REVIEW / EVIDENCE
FREEZE (READ-ONLY, RESEARCH ONLY):
ETH_SOL_RELATIVE_STRENGTH_PULLBACK_CONTINUATION_V1.

Freezes the one-pass real-candle detection result: 411 attempts across
ETHUSD and SOLUSD on the existing staged 15m data (aggregated to 1h by
the pushed aggregator, both symbols loaded simultaneously for the RS
gate, timestamp alignment asserted), SIX setups accepted with every
variant clearing the 81 bps floor at label time.

WHAT THIS IS NOT: no replay has run; no edge has been demonstrated; no
profitability exists or is claimed. SIX labels is a SMALL SAMPLE -- below
the ten that candidate #4's family froze as its near-zero line -- and the
spec's promotion conditions require sample_size_not_near_zero, so even a
positive replay could not promote without explicit human judgment. The
dominant rejection (372/411 pullback_too_long) repeats the candidate #3
scarcity pattern. Whether to replay the six, spend the single structure
edit, or reject is the HUMAN decision at the next gate.

This module observes the untracked artifacts READ-ONLY, recounts all 411
labels from the JSONL itself, re-verifies the staged-data shas, and
certifies every frozen fact. It runs nothing, fetches nothing, and
authorizes nothing.
"""

from __future__ import annotations

import hashlib as _hashlib
import json as _json
import pathlib as _pathlib
from typing import Any

import sparta_commander.strategy_factory_autopilot_research_loop_v1_contract as _loop
from sparta_commander.btc_sol_long_trend_continuation_v1_result_and_rejection_record_contract import (
    REJECTION_STATUS as C3_STATUS,
)
from sparta_commander.crypto_intraday_breakout_pullback_structure_v2_result_and_rejection_record_contract import (
    REJECTION_STATUS as C2_STATUS,
)
from sparta_commander.eth_sol_relative_strength_pullback_continuation_dry_run_review_contract import (
    VERDICT_C5R_FROZEN,
    build_c5_dry_run_review,
)
from sparta_commander.eth_sol_relative_strength_pullback_continuation_family_proposal_contract import (
    CANDIDATE_ID,
)
from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
    REJECTION_STATUS as C1_STATUS,
)
from sparta_commander.sol_btc_long_1h_swing_structure_rejection_record_contract import (
    REJECTION_STATUS as C4_STATUS,
)

C5L_SCHEMA_VERSION = (
    "eth_sol_relative_strength_real_candle_labels_review.v1")
C5L_LABEL = ("SPARTA Candidate #5 Real-Candle Labels Review / Evidence "
             "Freeze (READ-ONLY, RESEARCH ONLY, 6 LABELS FROZEN SMALL "
             "SAMPLE, NOT A PROFITABILITY CLAIM)")
C5L_MODE = "RESEARCH_ONLY"
VERDICT_C5L_FROZEN = (
    "CANDIDATE_5_REAL_CANDLE_LABELS_FROZEN_READY_FOR_HUMAN_REVIEW")
VERDICT_C5L_REJECTED = "CANDIDATE_5_LABELS_REVIEW_REJECTED"
VERDICT_C5L_BLOCKED = "CANDIDATE_5_LABELS_REVIEW_BLOCKED"
NEXT_REQUIRED_ACTION = (
    "HUMAN_DECISION_C5_REPLAY_SMALL_SAMPLE_OR_EDIT_OR_REJECT")

HEAD_AT_DETECTION = "c511db021476ac0db611919f752a0fed7f1b038d"
RUNNER_PATH = "tools/c5_real_candle_detection_once.py"
LABELS_PATH = ("data/relative_strength_c5/detector_labels/"
               "c5_detector_labels_2026-05-02_2026-06-10.jsonl")
SUMMARY_PATH = ("data/relative_strength_c5/detector_labels/"
                "c5_detector_summary_2026-05-02_2026-06-10.json")
EXPECTED_LABELS_SHA256 = (
    "72dd8aec73b492b25968c8578bc471716d277d9027cd89a54fab8981b4328d87")
EXPECTED_SUMMARY_SHA256 = (
    "6bf7d34d0ca14d1a2601627fc7d7d0db628aa3b77cffff95402b05953ac9f6d1")

EXPECTED_STAGED_SHAS = {
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

EXPECTED_COUNTS = {
    "ETHUSD": {"attempts": 213, "accepted": 3, "rejected": 210},
    "SOLUSD": {"attempts": 198, "accepted": 3, "rejected": 195},
    "total": {"attempts": 411, "accepted": 6, "rejected": 405},
}

EXPECTED_STATUS_BREAKDOWN = {
    "accepted_for_replay_review": 6,
    "rejected_pullback_too_long": 372,
    "rejected_pullback_too_short": 21,
    "rejected_pullback_too_deep": 8,
    "rejected_rs_not_stronger": 4,
}

EXPECTED_VARIANT_ACCEPTS = {"2r": 6, "3r": 6, "4r": 6}

# geometry frozen with display rounding: entry/stop 2dp, 2r bps 1dp,
# rs percentages 2dp
EXPECTED_ACCEPTED_SETUPS = {
    "ETHUSD_2026-05-13T08:00:00Z": {
        "entry": 2316.64, "stop": 2295.63, "bps_2r": 181.4,
        "rs_symbol_pct": 1.21, "rs_other_pct": 0.37},
    "ETHUSD_2026-05-24T01:00:00Z": {
        "entry": 2122.56, "stop": 2094.83, "bps_2r": 261.3,
        "rs_symbol_pct": 2.79, "rs_other_pct": 1.84},
    "ETHUSD_2026-05-25T14:00:00Z": {
        "entry": 2128.34, "stop": 2112.25, "bps_2r": 151.2,
        "rs_symbol_pct": 1.35, "rs_other_pct": 1.1},
    "SOLUSD_2026-05-06T01:00:00Z": {
        "entry": 86.86, "stop": 85.98, "bps_2r": 202.8,
        "rs_symbol_pct": 2.28, "rs_other_pct": -0.29},
    "SOLUSD_2026-05-06T06:00:00Z": {
        "entry": 87.49, "stop": 86.61, "bps_2r": 200.8,
        "rs_symbol_pct": 3.05, "rs_other_pct": -0.33},
    "SOLUSD_2026-05-09T01:00:00Z": {
        "entry": 93.51, "stop": 91.73, "bps_2r": 380.7,
        "rs_symbol_pct": 6.2, "rs_other_pct": 1.68},
}

EXPECTED_TRIGGER_RANGE = {
    "earliest": "2026-05-02T21:00:00Z",
    "latest": "2026-06-10T23:00:00Z",
}

FROZEN_DETECTION_FACTS = (
    "existing staged ethusd and solusd 15m data only; no fetch",
    "both symbols loaded simultaneously for the rs gate",
    "15m aggregated to 1h by the pushed aggregator; 960 1h bars each",
    "timestamp alignment asserted across symbols",
    "pushed scan_c5_setups ran exactly once per symbol",
    "no replay; labels only; no staged-data modification",
    "zero variant-floor fails among accepted setups",
    "zero partial-eligibility accepted setups",
    "every accepted setup clears 81 bps even at 2r; accepted 2r "
    "target-distance range 151-381 bps",
    "no non-overlap removals at label time; the policy remains "
    "replay/variant dependent",
)

FROZEN_SMALL_SAMPLE_FLAGS = (
    "six accepted labels is a small sample, below the ten that "
    "candidate #4's family froze as its near-zero line",
    "the spec's promotion conditions require sample_size_not_near_zero",
    "the dominant rejection (372/411 pullback_too_long) repeats the "
    "candidate #3 scarcity pattern",
    "replay the six, spend the single structure edit, or reject is "
    "the human decision at the next gate",
    "no profitability claim is permitted",
)


def get_c5_labels_review_label() -> str:
    return C5L_LABEL


def observe_c5_labels(repo_root: Any,
                      tracked_paths: Any = ()) -> dict[str, Any]:
    """Read the artifacts READ-ONLY and recount the facts. Never raises
    on missing files; reports absence instead."""
    observation: dict[str, Any] = {
        "labels_exists": False, "summary_exists": False,
        "labels_sha256": None, "summary_sha256": None,
        "labels_line_count": None, "status_breakdown": None,
        "accepted_count": None, "per_symbol_counts": None,
        "variant_accepts": None, "variant_floor_fail_counts": None,
        "partial_eligibility_ids": None,
        "accepted_geometry": None, "trigger_range": None,
        "staged_shas_now": None, "staged_shas_match": None,
        "candidate_id_in_labels": None,
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
        observation["summary_sha256"] = _hashlib.sha256(
            summary_file.read_bytes()).hexdigest()
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
        sym = per_symbol.setdefault(
            label["symbol"], {"attempts": 0, "accepted": 0,
                              "rejected": 0})
        sym["attempts"] += 1
        if label["status"] == "accepted_for_replay_review":
            sym["accepted"] += 1
            accepted.append(label)
        else:
            sym["rejected"] += 1
    observation["status_breakdown"] = breakdown
    observation["per_symbol_counts"] = per_symbol
    observation["accepted_count"] = len(accepted)
    observation["variant_accepts"] = {name: sum(
        1 for label in accepted
        if label["accepted_for_labeling_by_variant"][name])
        for name in ("2r", "3r", "4r")}
    observation["variant_floor_fail_counts"] = {name: sum(
        1 for label in accepted
        if not label["accepted_for_labeling_by_variant"][name])
        for name in ("2r", "3r", "4r")}
    observation["partial_eligibility_ids"] = sorted(
        label["setup_id"] for label in accepted
        if not all(label["accepted_for_labeling_by_variant"].values()))
    observation["accepted_geometry"] = {
        label["setup_id"]: {
            "entry": round(label["entry_price"], 2),
            "stop": round(label["stop_price"], 2),
            "bps_2r": round(label["target_distance_bps_2r"], 1),
            "rs_symbol_pct": round(label["return_20_symbol"] * 100, 2),
            "rs_other_pct": round(label["return_20_other"] * 100, 2)}
        for label in accepted}
    triggers = sorted(label["trigger_time"] for label in labels)
    observation["trigger_range"] = {
        "earliest": triggers[0] if triggers else None,
        "latest": triggers[-1] if triggers else None}
    observation["candidate_id_in_labels"] = None  # not in label schema
    return observation


def certify_c5_labels_review(observation: Any) -> dict[str, Any]:
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
    for symbol in ("ETHUSD", "SOLUSD"):
        if per_symbol.get(symbol) != EXPECTED_COUNTS[symbol]:
            failures.append("per_symbol_counts_mismatch:" + symbol)
    if set(per_symbol) - {"ETHUSD", "SOLUSD"}:
        failures.append("unexpected_symbols_in_labels")
    if o.get("variant_accepts") != EXPECTED_VARIANT_ACCEPTS:
        failures.append("variant_accepts_mismatch")
    if o.get("variant_floor_fail_counts") != {"2r": 0, "3r": 0,
                                              "4r": 0}:
        failures.append("variant_floor_fail_counts_mismatch")
    if o.get("partial_eligibility_ids") != []:
        failures.append("partial_eligibility_must_be_empty")
    geometry = o.get("accepted_geometry") or {}
    if set(geometry) != set(EXPECTED_ACCEPTED_SETUPS):
        failures.append("accepted_setup_ids_mismatch")
    else:
        for setup_id, expected in EXPECTED_ACCEPTED_SETUPS.items():
            if geometry.get(setup_id) != expected:
                failures.append("accepted_geometry_mismatch:" + setup_id)
    for setup in EXPECTED_ACCEPTED_SETUPS.values():
        if not 81 <= setup["bps_2r"]:
            failures.append("frozen_geometry_below_floor_impossible")
        if not 151 <= setup["bps_2r"] <= 381:
            failures.append("frozen_geometry_outside_frozen_range")
    if o.get("trigger_range") != EXPECTED_TRIGGER_RANGE:
        failures.append("trigger_range_mismatch")
    if o.get("staged_shas_match") is not True:
        failures.append("staged_data_shas_changed")
    if o.get("artifacts_tracked_in_git"):
        failures.append("runner_and_artifacts_must_stay_untracked")
    return {"certified": not failures, "failures": failures}


def build_c5_labels_review(repo_root: Any,
                           tracked_paths: Any = ()) -> dict[str, Any]:
    """Observe read-only and certify; gated on the full upstream chain
    and the four-record ledger."""
    record: dict[str, Any] = {
        "schema_version": C5L_SCHEMA_VERSION, "label": C5L_LABEL,
        "mode": C5L_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [], "failures": [],
        "candidate_id": CANDIDATE_ID,
        "head_at_detection": HEAD_AT_DETECTION,
        "runner_path_untracked_only": RUNNER_PATH,
        "labels_path": LABELS_PATH, "summary_path": SUMMARY_PATH,
        "expected_labels_sha256": EXPECTED_LABELS_SHA256,
        "expected_summary_sha256": EXPECTED_SUMMARY_SHA256,
        "expected_staged_shas": dict(EXPECTED_STAGED_SHAS),
        "expected_counts": {key: dict(value) for key, value
                            in EXPECTED_COUNTS.items()},
        "expected_status_breakdown": dict(EXPECTED_STATUS_BREAKDOWN),
        "expected_variant_accepts": dict(EXPECTED_VARIANT_ACCEPTS),
        "expected_accepted_setups": {
            key: dict(value) for key, value
            in EXPECTED_ACCEPTED_SETUPS.items()},
        "expected_trigger_range": dict(EXPECTED_TRIGGER_RANGE),
        "frozen_detection_facts": list(FROZEN_DETECTION_FACTS),
        "frozen_small_sample_flags": list(FROZEN_SMALL_SAMPLE_FLAGS),
        "replay_has_run": False,
        "replay_edit_or_reject_is_human_decision": True,
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
        "contains_order_logic": False, "starts_scheduler": False,
        "sends_notifications": False,
        "auto_commits": False, "auto_pushes": False,
        "creates_runners_now": False, "creates_data_artifacts_now": False,
        "modifies_staged_market_data": False,
        "authorizes_paper_execution": False,
        "authorizes_micro_live": False, "authorizes_live_trading": False,
        "promotes_gate": False, "unlocks_downstream_gate": False,
        "claims_profitability": False,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    if C1_STATUS != "REJECTED_KEPT_ON_RECORD" \
            or C2_STATUS != "REJECTED_KEPT_ON_RECORD" \
            or C3_STATUS != "REJECTED_KEPT_ON_RECORD" \
            or C4_STATUS != "REJECTED_KEPT_ON_RECORD":
        record["verdict"] = VERDICT_C5L_BLOCKED
        record["blockers"].append("ledger_broken")
        return record
    if build_c5_dry_run_review()["verdict"] != VERDICT_C5R_FROZEN:
        record["verdict"] = VERDICT_C5L_BLOCKED
        record["blockers"].append("dry_run_review_not_certifying")
        return record
    if _loop.build_autopilot_loop_contract()["verdict"] != (
            _loop.VERDICT_AP_READY):
        record["verdict"] = VERDICT_C5L_BLOCKED
        record["blockers"].append("autopilot_loop_not_certifying")
        return record
    observation = observe_c5_labels(repo_root, tracked_paths)
    result = certify_c5_labels_review(observation)
    record["failures"] = result["failures"]
    record["verdict"] = (VERDICT_C5L_FROZEN if result["certified"]
                         else VERDICT_C5L_REJECTED)
    return record


def validate_c5_labels_review(record: Any) -> dict[str, Any]:
    """Validate shape, frozen facts, and safety invariants. Never
    raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_C5L_FROZEN, VERDICT_C5L_REJECTED,
                                VERDICT_C5L_BLOCKED):
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
    expected_counts = {key: dict(value) for key, value
                       in EXPECTED_COUNTS.items()}
    if r.get("expected_counts") != expected_counts:
        errors.append("counts_tampered")
    if r.get("expected_status_breakdown") != EXPECTED_STATUS_BREAKDOWN:
        errors.append("breakdown_tampered")
    if r.get("expected_variant_accepts") != EXPECTED_VARIANT_ACCEPTS:
        errors.append("variant_accepts_tampered")
    expected_setups = {key: dict(value) for key, value
                       in EXPECTED_ACCEPTED_SETUPS.items()}
    if r.get("expected_accepted_setups") != expected_setups:
        errors.append("accepted_setups_tampered")
    if r.get("expected_trigger_range") != EXPECTED_TRIGGER_RANGE:
        errors.append("trigger_range_tampered")
    if tuple(r.get("frozen_detection_facts") or ()) != (
            FROZEN_DETECTION_FACTS):
        errors.append("detection_facts_tampered")
    if tuple(r.get("frozen_small_sample_flags") or ()) != (
            FROZEN_SMALL_SAMPLE_FLAGS):
        errors.append("small_sample_flags_tampered")
    if r.get("replay_has_run") is not False:
        errors.append("replay_must_not_have_run")
    if r.get("replay_edit_or_reject_is_human_decision") is not True:
        errors.append("human_decision_flag_wrong")
    if r.get("verdict") == VERDICT_C5L_FROZEN and r.get("failures"):
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
                "contains_order_logic", "starts_scheduler",
                "sends_notifications", "auto_commits", "auto_pushes",
                "creates_runners_now", "creates_data_artifacts_now",
                "modifies_staged_market_data",
                "authorizes_paper_execution", "authorizes_micro_live",
                "authorizes_live_trading", "promotes_gate",
                "unlocks_downstream_gate", "claims_profitability"):
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)
    return {"valid": not errors, "errors": errors}
