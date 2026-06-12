"""SPARTA CANDIDATE #3 REAL-CANDLE DETECTOR LABELS REVIEW / EVIDENCE
FREEZE (READ-ONLY, RESEARCH ONLY): BTC_SOL_LONG_TREND_CONTINUATION_V1.

Freezes the one-pass real-candle detection result: 711 attempts across
BTCUSD and SOLUSD on the existing staged 15m data, ZERO accepted labels
at the 81 bps floor. Per the pushed pre-committed rules, zero accepted
labels is a VALID HONEST OUTCOME, not a failure to be engineered around.

Frozen consequences:
  - NO replay is authorized -- there are no accepted labels to replay;
  - NO profitability claim is permitted (there is nothing to claim);
  - NO mutable edit is authorized BY THIS CONTRACT -- any edit path would
    require its own explicitly human-approved contract;
  - the artifacts are sha-pinned and may never be rewritten or deleted.

This module observes the untracked artifacts READ-ONLY and certifies them
against the frozen facts. It runs no detector, no replay, fetches
nothing, and authorizes nothing.
"""

from __future__ import annotations

import hashlib as _hashlib
import json as _json
import pathlib as _pathlib
from typing import Any

from sparta_commander.btc_sol_long_trend_continuation_detector_spec_contract import (
    TC_DETECTOR_STATUSES,
)
from sparta_commander.btc_sol_long_trend_continuation_strategy_spec_contract import (
    CANDIDATE_ID,
)
from sparta_commander.crypto_intraday_breakout_pullback_structure_v2_result_and_rejection_record_contract import (
    REJECTION_STATUS as C2_STATUS,
)
from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
    REJECTION_STATUS as C1_STATUS,
)

TCL_SCHEMA_VERSION = (
    "btc_sol_long_trend_continuation_real_candle_labels_review.v1")
TCL_LABEL = ("SPARTA Candidate #3 Real-Candle Labels Review / Evidence "
             "Freeze (READ-ONLY, RESEARCH ONLY, ZERO ACCEPTS FROZEN, "
             "NOT A PROFITABILITY CLAIM)")
TCL_MODE = "RESEARCH_ONLY"
VERDICT_TCL_FROZEN = "CANDIDATE_3_REAL_CANDLE_LABELS_FROZEN_ZERO_ACCEPTS"
VERDICT_TCL_REJECTED = "CANDIDATE_3_LABELS_REVIEW_REJECTED"
VERDICT_TCL_BLOCKED = "CANDIDATE_3_LABELS_REVIEW_BLOCKED"
NEXT_REQUIRED_ACTION = "HUMAN_DECISION_ON_CANDIDATE_3_OUTCOME"

LABELS_PATH = ("data/trend_continuation/detector_labels/"
               "tc3_detector_labels_2026-05-02_2026-06-10.jsonl")
SUMMARY_PATH = ("data/trend_continuation/detector_labels/"
                "tc3_detector_summary_2026-05-02_2026-06-10.json")

EXPECTED_LABELS_SHA256 = (
    "ad7fb2813804d01c8e0e31014651eb4c459b32ac8cdc26e62c61a7ee4074c2cc")
EXPECTED_SUMMARY_SHA256 = (
    "dda0766e7880d9fef1c7a451a09b183095df0e46d4c41cf4f45e9eee57853af9")

EXPECTED_COUNTS = {
    "BTCUSD": {"attempts": 334, "accepted": 0, "rejected": 334},
    "SOLUSD": {"attempts": 377, "accepted": 0, "rejected": 377},
    "total": {"attempts": 711, "accepted": 0, "rejected": 711},
}

EXPECTED_STATUS_BREAKDOWN = {
    "rejected_pullback_too_short": 627,
    "rejected_no_resumption_close": 40,
    "rejected_retrace_too_deep": 15,
    "rejected_trend_not_qualified": 15,
    "rejected_pullback_broke_swing_low": 7,
    "rejected_cost_floor_risk_too_small": 6,
    "rejected_pullback_too_long": 1,
}

EXPECTED_FLOOR_NEAR_MISSES_BPS = (
    35.76, 37.44, 51.38, 70.58, 72.6, 77.92)

FROZEN_DECISION_FACTS = (
    "real-candle detection completed exactly once on the existing "
    "staged btcusd/solusd 15m data; no fetching, no api occurred",
    "zero accepted labels at the 81 bps floor is a valid honest "
    "outcome, not a failure to be engineered around",
    "no replay is authorized because there are no accepted labels",
    "no profitability claim is permitted",
    "no mutable edit is authorized by this contract",
)


def get_tc3_labels_review_label() -> str:
    return TCL_LABEL


def observe_tc3_labels(repo_root: Any,
                       tracked_paths: Any = ()) -> dict[str, Any]:
    """Read the artifacts READ-ONLY and extract the facts. Never raises
    on missing files; reports absence instead."""
    observation: dict[str, Any] = {
        "labels_exists": False, "summary_exists": False,
        "labels_sha256": None, "summary_sha256": None,
        "labels_line_count": None, "status_breakdown": None,
        "accepted_count": None, "per_symbol_counts": None,
        "floor_near_misses_bps": None, "candidate_id_in_labels": None,
        "statuses_in_closed_set": None,
        "artifacts_tracked_in_git": [],
    }
    root = _pathlib.Path(str(repo_root))
    tracked = {str(p).replace("\\", "/") for p in (tracked_paths or ())}
    for rel in (LABELS_PATH, SUMMARY_PATH):
        if rel in tracked:
            observation["artifacts_tracked_in_git"].append(rel)
    labels_file = root / LABELS_PATH
    summary_file = root / SUMMARY_PATH
    if summary_file.is_file():
        observation["summary_exists"] = True
        raw = summary_file.read_bytes()
        observation["summary_sha256"] = _hashlib.sha256(raw).hexdigest()
    if labels_file.is_file():
        observation["labels_exists"] = True
        raw = labels_file.read_bytes()
        observation["labels_sha256"] = _hashlib.sha256(raw).hexdigest()
        lines = raw.decode("utf-8").splitlines()
        observation["labels_line_count"] = len(lines)
        labels = [_json.loads(line) for line in lines]
        breakdown: dict[str, int] = {}
        per_symbol: dict[str, dict[str, int]] = {}
        for label in labels:
            breakdown[label["status"]] = breakdown.get(
                label["status"], 0) + 1
            sym = per_symbol.setdefault(
                label["symbol"], {"attempts": 0, "accepted": 0,
                                  "rejected": 0})
            sym["attempts"] += 1
            if label["status"] == "accepted_for_replay_review":
                sym["accepted"] += 1
            else:
                sym["rejected"] += 1
        observation["status_breakdown"] = breakdown
        observation["per_symbol_counts"] = per_symbol
        observation["accepted_count"] = sum(
            1 for label in labels
            if label["status"] == "accepted_for_replay_review")
        observation["floor_near_misses_bps"] = sorted(
            round(label["risk_distance_bps"], 2) for label in labels
            if label["status"] == "rejected_cost_floor_risk_too_small")
        observation["candidate_id_in_labels"] = (
            all(label["candidate_id"] == CANDIDATE_ID
                for label in labels) if labels else None)
        observation["statuses_in_closed_set"] = all(
            label["status"] in TC_DETECTOR_STATUSES for label in labels)
    return observation


def certify_tc3_labels_review(observation: Any) -> dict[str, Any]:
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
    if o.get("accepted_count") != 0:
        failures.append("expected_zero_accepts")
    if o.get("status_breakdown") != EXPECTED_STATUS_BREAKDOWN:
        failures.append("status_breakdown_mismatch")
    per_symbol = o.get("per_symbol_counts") or {}
    for symbol in ("BTCUSD", "SOLUSD"):
        if per_symbol.get(symbol) != EXPECTED_COUNTS[symbol]:
            failures.append("per_symbol_counts_mismatch:" + symbol)
    if set(per_symbol) - {"BTCUSD", "SOLUSD"}:
        failures.append("unexpected_symbols_in_labels")
    if tuple(o.get("floor_near_misses_bps") or ()) != (
            EXPECTED_FLOOR_NEAR_MISSES_BPS):
        failures.append("floor_near_misses_mismatch")
    if max(EXPECTED_FLOOR_NEAR_MISSES_BPS) >= 81:
        failures.append("near_miss_at_or_above_floor_impossible")
    if o.get("candidate_id_in_labels") is not True:
        failures.append("candidate_id_mismatch_in_labels")
    if o.get("statuses_in_closed_set") is not True:
        failures.append("status_outside_closed_set")
    if o.get("artifacts_tracked_in_git"):
        failures.append("artifacts_must_stay_untracked")
    return {"certified": not failures, "failures": failures}


def build_tc3_labels_review(repo_root: Any,
                            tracked_paths: Any = ()) -> dict[str, Any]:
    """Observe read-only and certify; gated on the ledger being intact."""
    record: dict[str, Any] = {
        "schema_version": TCL_SCHEMA_VERSION, "label": TCL_LABEL,
        "mode": TCL_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [], "failures": [],
        "candidate_id": CANDIDATE_ID,
        "labels_path": LABELS_PATH, "summary_path": SUMMARY_PATH,
        "expected_labels_sha256": EXPECTED_LABELS_SHA256,
        "expected_summary_sha256": EXPECTED_SUMMARY_SHA256,
        "expected_counts": {key: dict(value) for key, value
                            in EXPECTED_COUNTS.items()},
        "expected_status_breakdown": dict(EXPECTED_STATUS_BREAKDOWN),
        "expected_floor_near_misses_bps": list(
            EXPECTED_FLOOR_NEAR_MISSES_BPS),
        "frozen_decision_facts": list(FROZEN_DECISION_FACTS),
        "replay_authorized": False,
        "mutable_edit_authorized": False,
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
        "claims_profitability": False, "revives_candidate_2": False,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    if C1_STATUS != "REJECTED_KEPT_ON_RECORD" \
            or C2_STATUS != "REJECTED_KEPT_ON_RECORD":
        record["verdict"] = VERDICT_TCL_BLOCKED
        record["blockers"].append("ledger_broken")
        return record
    observation = observe_tc3_labels(repo_root, tracked_paths)
    result = certify_tc3_labels_review(observation)
    record["failures"] = result["failures"]
    record["verdict"] = (VERDICT_TCL_FROZEN if result["certified"]
                         else VERDICT_TCL_REJECTED)
    return record


def validate_tc3_labels_review(record: Any) -> dict[str, Any]:
    """Validate shape, frozen facts, and safety invariants. Never
    raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_TCL_FROZEN, VERDICT_TCL_REJECTED,
                                VERDICT_TCL_BLOCKED):
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
    if tuple(r.get("expected_floor_near_misses_bps") or ()) != (
            EXPECTED_FLOOR_NEAR_MISSES_BPS):
        errors.append("near_misses_tampered")
    if tuple(r.get("frozen_decision_facts") or ()) != (
            FROZEN_DECISION_FACTS):
        errors.append("decision_facts_tampered")
    if r.get("replay_authorized") is not False:
        errors.append("replay_must_not_be_authorized")
    if r.get("mutable_edit_authorized") is not False:
        errors.append("mutable_edit_must_not_be_authorized")
    if r.get("verdict") == VERDICT_TCL_FROZEN and r.get("failures"):
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
                "claims_profitability", "revives_candidate_2"):
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)
    return {"valid": not errors, "errors": errors}
