"""SPARTA CANDIDATE #4 REAL-CANDLE DETECTOR LABELS REVIEW / EVIDENCE
FREEZE (READ-ONLY, RESEARCH ONLY): SOL_BTC_LONG_1H_SWING_STRUCTURE_V1.

Freezes the one-pass real-candle detection result: 275 attempts across
SOLUSD and BTCUSD on the existing staged 15m data (aggregated 15m -> 1h
-> 4h by the pushed aggregators), 22 accepted labels at the 81 bps floor.
The pre-committed near-zero rule did NOT trigger (22 >= 10), so the
candidate advances to the replay-review path.

WHAT THIS IS NOT: no replay has run; no edge has been demonstrated; no
profitability exists or is claimed. 22 labels are only a testable sample.
The fee-honest 27 bps replay -- behind its own explicit human gate -- is
where this candidate lives or dies, exactly as candidate #2 did at this
same stage.

This module observes the untracked artifacts READ-ONLY, recounts all 275
labels from the JSONL itself, and certifies every frozen fact. It runs
no detector, no replay, fetches nothing, and authorizes nothing.
"""

from __future__ import annotations

import hashlib as _hashlib
import json as _json
import pathlib as _pathlib
import statistics as _statistics
from typing import Any

from sparta_commander.btc_sol_long_trend_continuation_v1_result_and_rejection_record_contract import (
    REJECTION_STATUS as C3_STATUS,
)
from sparta_commander.crypto_intraday_breakout_pullback_structure_v2_result_and_rejection_record_contract import (
    REJECTION_STATUS as C2_STATUS,
)
from sparta_commander.ny_session_fvg_choch_mutable_candidate_edit_v2_cost_viability import (
    MINIMUM_RISK_DISTANCE_BPS,
)
from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
    REJECTION_STATUS as C1_STATUS,
)
from sparta_commander.sol_btc_long_1h_swing_structure_detector_spec_contract import (
    C4_DETECTOR_STATUSES,
)
from sparta_commander.sol_btc_long_1h_swing_structure_strategy_spec_contract import (
    CANDIDATE_ID,
)

C4L_SCHEMA_VERSION = (
    "sol_btc_long_1h_swing_structure_real_candle_labels_review.v1")
C4L_LABEL = ("SPARTA Candidate #4 Real-Candle Labels Review / Evidence "
             "Freeze (READ-ONLY, RESEARCH ONLY, 22 LABELS FROZEN, "
             "NOT A PROFITABILITY CLAIM)")
C4L_MODE = "RESEARCH_ONLY"
VERDICT_C4L_FROZEN = (
    "CANDIDATE_4_REAL_CANDLE_LABELS_FROZEN_ACCEPTED_FOR_REPLAY_REVIEW")
VERDICT_C4L_REJECTED = "CANDIDATE_4_LABELS_REVIEW_REJECTED"
VERDICT_C4L_BLOCKED = "CANDIDATE_4_LABELS_REVIEW_BLOCKED"
NEXT_REQUIRED_ACTION = (
    "HUMAN_APPROVED_C4_FEE_HONEST_REPLAY_OF_22_ACCEPTED_LABELS")

LABELS_PATH = ("data/swing_structure_c4/detector_labels/"
               "c4_detector_labels_2026-05-02_2026-06-10.jsonl")
SUMMARY_PATH = ("data/swing_structure_c4/detector_labels/"
                "c4_detector_summary_2026-05-02_2026-06-10.json")

EXPECTED_LABELS_SHA256 = (
    "8b89b87dd615921405cf4e7a9f50ef908b6dfbcdc593f6781ff062a6a2dcc746")
EXPECTED_SUMMARY_SHA256 = (
    "d70b6979f33186d4538897e4cf92e3fd2787d18793dddf7a0c0b1db556336205")

EXPECTED_COUNTS = {
    "SOLUSD": {"attempts": 137, "accepted": 12, "rejected": 125},
    "BTCUSD": {"attempts": 138, "accepted": 10, "rejected": 128},
    "total": {"attempts": 275, "accepted": 22, "rejected": 253},
}

EXPECTED_STATUS_BREAKDOWN = {
    "accepted_for_replay_review": 22,
    "rejected_not_higher_low": 137,
    "rejected_sl2_low_broken_before_entry": 78,
    "rejected_trend_not_qualified": 26,
    "rejected_cost_floor_risk_too_small": 6,
    "rejected_insufficient_4h_history": 4,
    "rejected_no_trigger_close_within_window": 2,
}

EXPECTED_ACCEPTED_FACTS = {
    "all_cleared_81bps_floor": True,
    "risk_bps_min": 83.86,
    "risk_bps_median": 139.39,
    "risk_bps_max": 402.67,
    "structural_stop_count": 21,
    "atr_stop_count": 1,
    "sol_accepted": 12,
    "btc_accepted": 10,
}

NEAR_ZERO_THRESHOLD_ACCEPTED_LABELS = 10

FROZEN_DECISION_FACTS = (
    "real-candle detection completed exactly once on the existing "
    "staged solusd/btcusd 15m data, aggregated 15m to 1h to 4h by the "
    "pushed aggregators; no fetching, no api occurred",
    "the pre-committed near-zero rule did not trigger: 22 accepted is "
    "at or above the threshold of 10",
    "replay has not yet run; nothing about edge or profitability is "
    "known or claimed",
    "no profitability claim is permitted",
    "the artifacts are sha-pinned and may never be rewritten or deleted",
)


def get_c4_labels_review_label() -> str:
    return C4L_LABEL


def observe_c4_labels(repo_root: Any,
                      tracked_paths: Any = ()) -> dict[str, Any]:
    """Read the artifacts READ-ONLY and extract the facts. Never raises
    on missing files; reports absence instead."""
    observation: dict[str, Any] = {
        "labels_exists": False, "summary_exists": False,
        "labels_sha256": None, "summary_sha256": None,
        "labels_line_count": None, "status_breakdown": None,
        "accepted_count": None, "per_symbol_counts": None,
        "accepted_all_at_or_above_floor": None,
        "accepted_risk_bps_min": None,
        "accepted_risk_bps_median": None,
        "accepted_risk_bps_max": None,
        "structural_stop_count": None, "atr_stop_count": None,
        "sol_accepted_count": None, "btc_accepted_count": None,
        "near_zero_rule_triggered": None,
        "candidate_id_in_labels": None,
        "statuses_in_closed_set": None,
        "artifacts_tracked_in_git": [],
    }
    root = _pathlib.Path(str(repo_root))
    tracked = {str(p).replace("\\", "/") for p in (tracked_paths or ())}
    for rel in (LABELS_PATH, SUMMARY_PATH):
        if rel in tracked:
            observation["artifacts_tracked_in_git"].append(rel)
    summary_file = root / SUMMARY_PATH
    labels_file = root / LABELS_PATH
    if summary_file.is_file():
        observation["summary_exists"] = True
        observation["summary_sha256"] = _hashlib.sha256(
            summary_file.read_bytes()).hexdigest()
    if labels_file.is_file():
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
            breakdown[label["status"]] = breakdown.get(
                label["status"], 0) + 1
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
        if accepted:
            risks = [label["risk_distance_bps"] for label in accepted]
            observation["accepted_all_at_or_above_floor"] = all(
                risk >= MINIMUM_RISK_DISTANCE_BPS for risk in risks)
            observation["accepted_risk_bps_min"] = round(min(risks), 2)
            observation["accepted_risk_bps_median"] = round(
                _statistics.median(risks), 2)
            observation["accepted_risk_bps_max"] = round(max(risks), 2)
            observation["structural_stop_count"] = sum(
                1 for label in accepted
                if label["stop_source"] == "structural_sl2_low")
            observation["atr_stop_count"] = sum(
                1 for label in accepted
                if label["stop_source"] == "volatility_1_5x_atr14")
            observation["sol_accepted_count"] = sum(
                1 for label in accepted if label["symbol"] == "SOLUSD")
            observation["btc_accepted_count"] = sum(
                1 for label in accepted if label["symbol"] == "BTCUSD")
        observation["near_zero_rule_triggered"] = (
            len(accepted) < NEAR_ZERO_THRESHOLD_ACCEPTED_LABELS)
        observation["candidate_id_in_labels"] = (
            all(label["candidate_id"] == CANDIDATE_ID
                for label in labels) if labels else None)
        observation["statuses_in_closed_set"] = all(
            label["status"] in C4_DETECTOR_STATUSES for label in labels)
    return observation


def certify_c4_labels_review(observation: Any) -> dict[str, Any]:
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
    for symbol in ("SOLUSD", "BTCUSD"):
        if per_symbol.get(symbol) != EXPECTED_COUNTS[symbol]:
            failures.append("per_symbol_counts_mismatch:" + symbol)
    if set(per_symbol) - {"SOLUSD", "BTCUSD"}:
        failures.append("unexpected_symbols_in_labels")
    exp = EXPECTED_ACCEPTED_FACTS
    if o.get("accepted_all_at_or_above_floor") is not True:
        failures.append("accepted_label_below_floor")
    if o.get("accepted_risk_bps_min") != exp["risk_bps_min"]:
        failures.append("risk_min_mismatch")
    if o.get("accepted_risk_bps_median") != exp["risk_bps_median"]:
        failures.append("risk_median_mismatch")
    if o.get("accepted_risk_bps_max") != exp["risk_bps_max"]:
        failures.append("risk_max_mismatch")
    if o.get("structural_stop_count") != exp["structural_stop_count"]:
        failures.append("structural_stop_count_mismatch")
    if o.get("atr_stop_count") != exp["atr_stop_count"]:
        failures.append("atr_stop_count_mismatch")
    if o.get("sol_accepted_count") != exp["sol_accepted"]:
        failures.append("sol_accepted_mismatch")
    if o.get("btc_accepted_count") != exp["btc_accepted"]:
        failures.append("btc_accepted_mismatch")
    if o.get("near_zero_rule_triggered") is not False:
        failures.append("near_zero_rule_must_not_have_triggered")
    if EXPECTED_COUNTS["total"]["accepted"] < (
            NEAR_ZERO_THRESHOLD_ACCEPTED_LABELS):
        failures.append("frozen_counts_contradict_near_zero_outcome")
    if o.get("candidate_id_in_labels") is not True:
        failures.append("candidate_id_mismatch_in_labels")
    if o.get("statuses_in_closed_set") is not True:
        failures.append("status_outside_closed_set")
    if o.get("artifacts_tracked_in_git"):
        failures.append("artifacts_must_stay_untracked")
    return {"certified": not failures, "failures": failures}


def build_c4_labels_review(repo_root: Any,
                           tracked_paths: Any = ()) -> dict[str, Any]:
    """Observe read-only and certify; gated on the three-record ledger
    being intact."""
    record: dict[str, Any] = {
        "schema_version": C4L_SCHEMA_VERSION, "label": C4L_LABEL,
        "mode": C4L_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [], "failures": [],
        "candidate_id": CANDIDATE_ID,
        "labels_path": LABELS_PATH, "summary_path": SUMMARY_PATH,
        "expected_labels_sha256": EXPECTED_LABELS_SHA256,
        "expected_summary_sha256": EXPECTED_SUMMARY_SHA256,
        "expected_counts": {key: dict(value) for key, value
                            in EXPECTED_COUNTS.items()},
        "expected_status_breakdown": dict(EXPECTED_STATUS_BREAKDOWN),
        "expected_accepted_facts": dict(EXPECTED_ACCEPTED_FACTS),
        "near_zero_threshold_accepted_labels":
            NEAR_ZERO_THRESHOLD_ACCEPTED_LABELS,
        "frozen_decision_facts": list(FROZEN_DECISION_FACTS),
        "replay_has_run": False,
        "human_review_required": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True, "live_gate_locked": True,
        "executes": False, "writes_files": False,
        "runs_real_detection_now": False, "runs_replay_now": False,
        "scores_now": False, "stages_data_now": False,
        "fetches_data": False, "calls_api": False, "uses_network": False,
        "uses_credentials": False, "uses_wallet": False,
        "connects_broker": False, "connects_exchange": False,
        "uses_real_money": False, "contains_order_logic": False,
        "starts_scheduler": False, "sends_notifications": False,
        "authorizes_paper_execution": False,
        "authorizes_micro_live": False, "authorizes_live_trading": False,
        "promotes_gate": False, "unlocks_downstream_gate": False,
        "claims_profitability": False, "revives_candidate_3": False,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    if C1_STATUS != "REJECTED_KEPT_ON_RECORD" \
            or C2_STATUS != "REJECTED_KEPT_ON_RECORD" \
            or C3_STATUS != "REJECTED_KEPT_ON_RECORD":
        record["verdict"] = VERDICT_C4L_BLOCKED
        record["blockers"].append("ledger_broken")
        return record
    observation = observe_c4_labels(repo_root, tracked_paths)
    result = certify_c4_labels_review(observation)
    record["failures"] = result["failures"]
    record["verdict"] = (VERDICT_C4L_FROZEN if result["certified"]
                         else VERDICT_C4L_REJECTED)
    return record


def validate_c4_labels_review(record: Any) -> dict[str, Any]:
    """Validate shape, frozen facts, and safety invariants. Never
    raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_C4L_FROZEN, VERDICT_C4L_REJECTED,
                                VERDICT_C4L_BLOCKED):
        errors.append("bad_verdict")
    if r.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if r.get("expected_labels_sha256") != EXPECTED_LABELS_SHA256:
        errors.append("labels_sha_tampered")
    if r.get("expected_summary_sha256") != EXPECTED_SUMMARY_SHA256:
        errors.append("summary_sha_tampered")
    expected_counts = {key: dict(value) for key, value
                       in EXPECTED_COUNTS.items()}
    if r.get("expected_counts") != expected_counts:
        errors.append("counts_tampered")
    if r.get("expected_status_breakdown") != EXPECTED_STATUS_BREAKDOWN:
        errors.append("breakdown_tampered")
    if r.get("expected_accepted_facts") != EXPECTED_ACCEPTED_FACTS:
        errors.append("accepted_facts_tampered")
    if r.get("near_zero_threshold_accepted_labels") != (
            NEAR_ZERO_THRESHOLD_ACCEPTED_LABELS):
        errors.append("threshold_tampered")
    if tuple(r.get("frozen_decision_facts") or ()) != (
            FROZEN_DECISION_FACTS):
        errors.append("decision_facts_tampered")
    if r.get("replay_has_run") is not False:
        errors.append("replay_must_not_have_run")
    if r.get("verdict") == VERDICT_C4L_FROZEN and r.get("failures"):
        errors.append("frozen_with_failures")
    for key, want in (("human_review_required", True),
                      ("paper_trading_gate_locked", True),
                      ("micro_live_gate_locked", True),
                      ("live_gate_locked", True)):
        if r.get(key) is not want:
            errors.append("constitution_flag_wrong:" + key)
    for key in ("executes", "writes_files", "runs_real_detection_now",
                "runs_replay_now", "scores_now", "stages_data_now",
                "fetches_data", "calls_api", "uses_network",
                "uses_credentials", "uses_wallet", "connects_broker",
                "connects_exchange", "uses_real_money",
                "contains_order_logic", "starts_scheduler",
                "sends_notifications", "authorizes_paper_execution",
                "authorizes_micro_live", "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate",
                "claims_profitability", "revives_candidate_3"):
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)
    return {"valid": not errors, "errors": errors}
