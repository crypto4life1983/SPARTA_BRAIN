"""SPARTA CANDIDATE #3 V1 RESULT FREEZE + FORMAL REJECTION RECORD
(READ-ONLY, RESEARCH ONLY): BTC_SOL_LONG_TREND_CONTINUATION_V1.

THE LEDGER ENTRY: Candidate #3 is REJECTED_KEPT_ON_RECORD, reason
NEAR_ZERO_SETUPS_AFTER_ONE_AUTHORIZED_STRUCTURE_EDIT.

The one authorized Mutable Edit V1 (pullback = lower low OR lower close)
ran exactly once on the same staged BTCUSD/SOLUSD sample as the frozen
zero-accept run and produced 9 accepted labels out of 711 attempts --
below the pre-committed near-zero threshold of 10. The rule was frozen
BEFORE the number was known, and it is honored exactly: no recount, no
threshold change, no replay of 9 labels, no second edit.

Frozen consequences (validator-permanent):
  - candidate #3 may not continue as-is;
  - candidate #3 may not receive another mutable edit;
  - no replay is authorized;
  - no profitability claim is permitted;
  - the V1 artifacts are sha-pinned and may never be rewritten/deleted.

Seed observations are preserved STRICTLY for NEW candidate families and
are never rescue paths for candidate #3 (or #1, or #2).

This module observes the untracked V1 artifacts READ-ONLY and certifies
them against the frozen facts. It runs nothing, fetches nothing, and
authorizes nothing.
"""

from __future__ import annotations

import hashlib as _hashlib
import json as _json
import pathlib as _pathlib
from typing import Any

from sparta_commander.btc_sol_long_trend_continuation_mutable_edit_v1_pullback_definition import (
    NEAR_ZERO_THRESHOLD_ACCEPTED_LABELS,
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

RJ3_SCHEMA_VERSION = (
    "btc_sol_long_trend_continuation_v1_result_and_rejection_record.v1")
RJ3_LABEL = ("SPARTA Candidate #3 V1 Result Freeze + Rejection Record "
             "(READ-ONLY, RESEARCH ONLY, REJECTED KEPT ON RECORD, "
             "NOT A PROFITABILITY CLAIM)")
RJ3_MODE = "RESEARCH_ONLY"
VERDICT_RJ3_RECORDED = (
    "CANDIDATE_3_V1_RESULT_FROZEN_AND_CANDIDATE_REJECTED_KEPT_ON_RECORD")
VERDICT_RJ3_REVIEW_REJECTED = "CANDIDATE_3_REJECTION_RECORD_REVIEW_REJECTED"
VERDICT_RJ3_BLOCKED = "CANDIDATE_3_REJECTION_RECORD_BLOCKED"
NEXT_REQUIRED_ACTION = "HUMAN_DECISION_ON_NEXT_CANDIDATE_FAMILY"

REJECTION_STATUS = "REJECTED_KEPT_ON_RECORD"
REJECTION_REASON = (
    "NEAR_ZERO_SETUPS_AFTER_ONE_AUTHORIZED_STRUCTURE_EDIT")

V1_LABELS_PATH = ("data/trend_continuation/edit_v1/"
                  "tc3_v1_labels_2026-05-02_2026-06-10.jsonl")
V1_SUMMARY_PATH = ("data/trend_continuation/edit_v1/"
                   "tc3_v1_summary_2026-05-02_2026-06-10.json")

EXPECTED_V1_LABELS_SHA256 = (
    "e02d58c184656b49731519d04a2101a05cc90874a9234b7647638d0a3656a69b")
EXPECTED_V1_SUMMARY_SHA256 = (
    "99e1eee0ccb9c76a588bf065b44eff0df84d406fc1c50e33818df4fc3233f63f")

EXPECTED_V1_COUNTS = {
    "BTCUSD": {"attempts": 334, "accepted": 2, "rejected": 332},
    "SOLUSD": {"attempts": 377, "accepted": 7, "rejected": 370},
    "total": {"attempts": 711, "accepted": 9, "rejected": 702},
}

EXPECTED_V1_STATUS_BREAKDOWN = {
    "accepted_for_replay_review": 9,
    "rejected_pullback_too_short": 399,
    "rejected_no_resumption_close": 147,
    "rejected_retrace_too_deep": 46,
    "rejected_trend_not_qualified": 46,
    "rejected_cost_floor_risk_too_small": 29,
    "rejected_pullback_broke_swing_low": 19,
    "rejected_pullback_too_long": 15,
    "rejected_insufficient_1h_history": 1,
}

FROZEN_RESULT_FACTS = (
    "mutable edit v1 was the one authorized edit for candidate #3",
    "v1 redetection ran exactly once on the same staged btcusd/solusd "
    "sample as the frozen zero-accept run; no fetch, no api occurred",
    "9 accepted labels is below the pre-committed near-zero threshold "
    "of 10, so the failure rule triggered as frozen",
    "no replay is authorized",
    "no second mutable edit is authorized",
    "no profitability claim is permitted",
)

SEED_OBSERVATIONS_FOR_NEW_FAMILIES_ONLY = (
    "sol_produced_7_of_9_accepted_labels",
    "all_9_accepted_labels_used_structural_stops",
    "accepted_risk_distances_were_healthy_92_to_151_bps",
)
SEEDS_ARE_NEVER_RESCUE_PATHS = True


def get_tc3_rejection_record_label() -> str:
    return RJ3_LABEL


def observe_v1_result(repo_root: Any,
                      tracked_paths: Any = ()) -> dict[str, Any]:
    """Read the V1 artifacts READ-ONLY and extract the facts. Never
    raises on missing files; reports absence instead."""
    observation: dict[str, Any] = {
        "labels_exists": False, "summary_exists": False,
        "labels_sha256": None, "summary_sha256": None,
        "labels_line_count": None, "status_breakdown": None,
        "accepted_count": None, "per_symbol_counts": None,
        "sol_accepted_count": None,
        "accepted_all_structural_stops": None,
        "accepted_risk_bps_min": None, "accepted_risk_bps_max": None,
        "near_zero_rule_triggered": None,
        "artifacts_tracked_in_git": [],
    }
    root = _pathlib.Path(str(repo_root))
    tracked = {str(p).replace("\\", "/") for p in (tracked_paths or ())}
    for rel in (V1_LABELS_PATH, V1_SUMMARY_PATH):
        if rel in tracked:
            observation["artifacts_tracked_in_git"].append(rel)
    summary_file = root / V1_SUMMARY_PATH
    labels_file = root / V1_LABELS_PATH
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
        observation["sol_accepted_count"] = sum(
            1 for label in accepted if label["symbol"] == "SOLUSD")
        observation["accepted_all_structural_stops"] = (
            all(label["stop_source"] == "structural_pullback_low"
                for label in accepted) if accepted else None)
        if accepted:
            risks = [label["risk_distance_bps"] for label in accepted]
            observation["accepted_risk_bps_min"] = round(min(risks), 2)
            observation["accepted_risk_bps_max"] = round(max(risks), 2)
        observation["near_zero_rule_triggered"] = (
            len(accepted) < NEAR_ZERO_THRESHOLD_ACCEPTED_LABELS)
    return observation


def certify_v1_result(observation: Any) -> dict[str, Any]:
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
    if o.get("labels_sha256") != EXPECTED_V1_LABELS_SHA256:
        failures.append("labels_sha_mismatch")
    if o.get("summary_sha256") != EXPECTED_V1_SUMMARY_SHA256:
        failures.append("summary_sha_mismatch")
    if o.get("labels_line_count") != (
            EXPECTED_V1_COUNTS["total"]["attempts"]):
        failures.append("label_count_mismatch")
    if o.get("accepted_count") != EXPECTED_V1_COUNTS["total"]["accepted"]:
        failures.append("accepted_count_mismatch")
    if o.get("status_breakdown") != EXPECTED_V1_STATUS_BREAKDOWN:
        failures.append("status_breakdown_mismatch")
    per_symbol = o.get("per_symbol_counts") or {}
    for symbol in ("BTCUSD", "SOLUSD"):
        if per_symbol.get(symbol) != EXPECTED_V1_COUNTS[symbol]:
            failures.append("per_symbol_counts_mismatch:" + symbol)
    if set(per_symbol) - {"BTCUSD", "SOLUSD"}:
        failures.append("unexpected_symbols_in_labels")
    if o.get("sol_accepted_count") != 7:
        failures.append("sol_seed_observation_mismatch")
    if o.get("accepted_all_structural_stops") is not True:
        failures.append("structural_stop_seed_observation_mismatch")
    if o.get("accepted_risk_bps_min") != 92.18:
        failures.append("risk_min_mismatch")
    if o.get("accepted_risk_bps_max") != 151.47:
        failures.append("risk_max_mismatch")
    if o.get("near_zero_rule_triggered") is not True:
        failures.append("near_zero_rule_must_have_triggered")
    if EXPECTED_V1_COUNTS["total"]["accepted"] >= (
            NEAR_ZERO_THRESHOLD_ACCEPTED_LABELS):
        failures.append("frozen_counts_contradict_near_zero_rule")
    if o.get("artifacts_tracked_in_git"):
        failures.append("artifacts_must_stay_untracked")
    return {"certified": not failures, "failures": failures}


def build_tc3_rejection_record(repo_root: Any,
                               tracked_paths: Any = ()) -> dict[str, Any]:
    """Observe read-only and certify; record the formal rejection."""
    record: dict[str, Any] = {
        "schema_version": RJ3_SCHEMA_VERSION, "label": RJ3_LABEL,
        "mode": RJ3_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [], "failures": [],
        "candidate_id": CANDIDATE_ID,
        "rejection_status": REJECTION_STATUS,
        "rejection_reason": REJECTION_REASON,
        "v1_labels_path": V1_LABELS_PATH,
        "v1_summary_path": V1_SUMMARY_PATH,
        "expected_v1_labels_sha256": EXPECTED_V1_LABELS_SHA256,
        "expected_v1_summary_sha256": EXPECTED_V1_SUMMARY_SHA256,
        "expected_v1_counts": {key: dict(value) for key, value
                               in EXPECTED_V1_COUNTS.items()},
        "expected_v1_status_breakdown": dict(
            EXPECTED_V1_STATUS_BREAKDOWN),
        "near_zero_threshold_accepted_labels":
            NEAR_ZERO_THRESHOLD_ACCEPTED_LABELS,
        "frozen_result_facts": list(FROZEN_RESULT_FACTS),
        "seed_observations_for_new_families_only": list(
            SEED_OBSERVATIONS_FOR_NEW_FAMILIES_ONLY),
        "seeds_are_never_rescue_paths": SEEDS_ARE_NEVER_RESCUE_PATHS,
        "candidate_3_may_continue_as_is": False,
        "candidate_3_may_receive_another_mutable_edit": False,
        "replay_authorized": False,
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
        record["verdict"] = VERDICT_RJ3_BLOCKED
        record["blockers"].append("ledger_broken")
        return record
    observation = observe_v1_result(repo_root, tracked_paths)
    result = certify_v1_result(observation)
    record["failures"] = result["failures"]
    record["verdict"] = (VERDICT_RJ3_RECORDED if result["certified"]
                         else VERDICT_RJ3_REVIEW_REJECTED)
    return record


def validate_tc3_rejection_record(record: Any) -> dict[str, Any]:
    """Validate shape, frozen facts, permanence flags. Never raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_RJ3_RECORDED,
                                VERDICT_RJ3_REVIEW_REJECTED,
                                VERDICT_RJ3_BLOCKED):
        errors.append("bad_verdict")
    if r.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if r.get("rejection_status") != REJECTION_STATUS:
        errors.append("rejection_status_tampered")
    if r.get("rejection_reason") != REJECTION_REASON:
        errors.append("rejection_reason_tampered")
    if r.get("expected_v1_labels_sha256") != EXPECTED_V1_LABELS_SHA256:
        errors.append("labels_sha_tampered")
    if r.get("expected_v1_summary_sha256") != EXPECTED_V1_SUMMARY_SHA256:
        errors.append("summary_sha_tampered")
    expected_counts = {key: dict(value) for key, value
                       in EXPECTED_V1_COUNTS.items()}
    if r.get("expected_v1_counts") != expected_counts:
        errors.append("counts_tampered")
    if r.get("expected_v1_status_breakdown") != (
            EXPECTED_V1_STATUS_BREAKDOWN):
        errors.append("breakdown_tampered")
    if r.get("near_zero_threshold_accepted_labels") != (
            NEAR_ZERO_THRESHOLD_ACCEPTED_LABELS):
        errors.append("threshold_tampered")
    if tuple(r.get("frozen_result_facts") or ()) != FROZEN_RESULT_FACTS:
        errors.append("result_facts_tampered")
    if tuple(r.get("seed_observations_for_new_families_only") or ()) != (
            SEED_OBSERVATIONS_FOR_NEW_FAMILIES_ONLY):
        errors.append("seed_observations_tampered")
    if r.get("seeds_are_never_rescue_paths") is not True:
        errors.append("seeds_must_never_be_rescue_paths")
    for key in ("candidate_3_may_continue_as_is",
                "candidate_3_may_receive_another_mutable_edit",
                "replay_authorized"):
        if r.get(key) is not False:
            errors.append("permanence_flag_wrong:" + key)
    if r.get("verdict") == VERDICT_RJ3_RECORDED and r.get("failures"):
        errors.append("recorded_with_failures")
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
