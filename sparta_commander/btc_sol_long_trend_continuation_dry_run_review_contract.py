"""SPARTA CANDIDATE #3 DRY-RUN REVIEW / EVIDENCE FREEZE (READ-ONLY,
RESEARCH ONLY): BTC_SOL_LONG_TREND_CONTINUATION_V1.

Freezes the synthetic dry-run outcomes of the pushed Candidate #3
detector spec. Because the dry run is pure, deterministic and reads NO
files, this review certifies by RE-COMPUTING the dry run live and
comparing every frozen fact byte-for-byte against the expectations below
-- stronger than hashing an artifact, and it proves the pushed scanner
still produces exactly the reviewed behavior.

Synthetic fixtures only. No real-candle detection has happened for
Candidate #3, no replay, no fetch, and this module performs none. The
frozen facts certify detector BEHAVIOR, not edge: nothing here is a
profitability claim and nothing here authorizes anything.
"""

from __future__ import annotations

from typing import Any

from sparta_commander.btc_sol_long_trend_continuation_detector_spec_contract import (
    VERDICT_TCD_DRY_RUN_PASSED,
    VERDICT_TCD_READY,
    _fixture_1h,
    _fixture_15m_accepted,
    _fixture_15m_tight,
    build_tc_detector_spec_contract,
    evaluate_trend_qualification,
    run_tc_detector_dry_run,
    scan_tc_setups,
)
from sparta_commander.btc_sol_long_trend_continuation_strategy_spec_contract import (
    CANDIDATE_ID,
)
from sparta_commander.ny_session_fvg_choch_mutable_candidate_edit_v2_cost_viability import (
    MINIMUM_RISK_DISTANCE_BPS,
)

DRR_SCHEMA_VERSION = "btc_sol_long_trend_continuation_dry_run_review.v1"
DRR_LABEL = ("SPARTA Candidate #3 Dry-Run Review / Evidence Freeze "
             "(READ-ONLY, RESEARCH ONLY, SYNTHETIC OUTCOMES ONLY, "
             "NOT A PROFITABILITY CLAIM)")
DRR_MODE = "RESEARCH_ONLY"
VERDICT_DRR_APPROVED = (
    "CANDIDATE_3_DRY_RUN_REVIEW_APPROVED_DETECTOR_BEHAVIOR_FROZEN")
VERDICT_DRR_REJECTED = "CANDIDATE_3_DRY_RUN_REVIEW_REJECTED"
VERDICT_DRR_BLOCKED = "CANDIDATE_3_DRY_RUN_REVIEW_BLOCKED"
NEXT_REQUIRED_ACTION = (
    "HUMAN_APPROVED_CANDIDATE_3_REAL_CANDLE_DETECTION")

# --- frozen dry-run facts (exact values from the reviewed run) -------------

EXPECTED_DETECTOR_VERDICT = "CANDIDATE_3_DETECTOR_DRY_RUN_PASSED"

EXPECTED_ACCEPTED_FIXTURE = {
    "symbol": "BTCUSD",
    "total_labels": 5,
    "accepted_labels": 1,
    "accepted_setup_id": "BTCUSD_2026-01-02T18:00:00Z",
    "entry_price": 102.4,
    "stop_price": 101.5,
    "structural_stop_price": 101.5,
    "stop_source": "structural_pullback_low",
    "stop_selected_because": "structural_wider_than_1_5x_atr_stop",
    "risk_distance_bps": 87.890625,
    "risk_meets_81bps_floor": True,
    "target_2r_price": 104.2,
    "target_3r_price": 105.1,
    "target_4r_price": 106.0,
}

EXPECTED_TIGHT_FIXTURE = {
    "symbol": "SOLUSD",
    "total_labels": 7,
    "accepted_labels": 0,
    "cost_floor_rejections": 1,
    "rejected_setup_id": "SOLUSD_2026-01-02T18:00:00Z",
    "stop_source": "volatility_1_5x_atr14",
    "stop_selected_because": "volatility_wider_than_structural_stop",
    "risk_distance_bps": 39.910845,
    "risk_below_81bps_floor": True,
}

EXPECTED_DOWNTREND_FIXTURE = {
    "symbol": "BTCUSD",
    "total_labels": 5,
    "accepted_labels": 0,
    "trend_rejections": 1,
}

EXPECTED_ANTI_LOOKAHEAD = {
    "signal_0659_completed_1h_bars": 24,
    "signal_0659_sufficient": False,
    "signal_0700_completed_1h_bars": 25,
    "signal_0700_sufficient": True,
}

FROZEN_SCOPE_FACTS = (
    "synthetic in-memory fixtures only",
    "no real-candle detection has occurred for candidate #3",
    "no replay has occurred for candidate #3",
    "frozen facts certify detector behavior, not edge",
    "nothing here is a profitability claim",
)


def get_dry_run_review_label() -> str:
    return DRR_LABEL


def _recompute_observation() -> dict[str, Any]:
    """Re-run the pushed dry run + scanners live (pure, in-memory)."""
    uptrend_1h = _fixture_1h(True)
    accepted_run = scan_tc_setups(
        _fixture_15m_accepted(), uptrend_1h, "BTCUSD")
    accepted = [lab for lab in accepted_run
                if lab["status"] == "accepted_for_replay_review"]
    tight_run = scan_tc_setups(
        _fixture_15m_tight(), uptrend_1h, "SOLUSD")
    floor_rejects = [lab for lab in tight_run if lab["status"]
                     == "rejected_cost_floor_risk_too_small"]
    down_run = scan_tc_setups(
        _fixture_15m_accepted(), _fixture_1h(False), "BTCUSD")
    early = evaluate_trend_qualification(uptrend_1h, "2026-01-02T06:59:00Z")
    later = evaluate_trend_qualification(uptrend_1h, "2026-01-02T07:00:00Z")
    return {
        "dry_run_verdict": run_tc_detector_dry_run()["verdict"],
        "accepted_run": accepted_run, "accepted": accepted,
        "tight_run": tight_run, "floor_rejects": floor_rejects,
        "down_run": down_run, "early": early, "later": later,
    }


def build_dry_run_review() -> dict[str, Any]:
    """Recompute the dry run live and certify it against the frozen
    facts. Gated on the detector spec contract being READY."""
    record: dict[str, Any] = {
        "schema_version": DRR_SCHEMA_VERSION, "label": DRR_LABEL,
        "mode": DRR_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [], "mismatches": [],
        "candidate_id": CANDIDATE_ID,
        "expected_detector_verdict": EXPECTED_DETECTOR_VERDICT,
        "expected_accepted_fixture": dict(EXPECTED_ACCEPTED_FIXTURE),
        "expected_tight_fixture": dict(EXPECTED_TIGHT_FIXTURE),
        "expected_downtrend_fixture": dict(EXPECTED_DOWNTREND_FIXTURE),
        "expected_anti_lookahead": dict(EXPECTED_ANTI_LOOKAHEAD),
        "frozen_scope_facts": list(FROZEN_SCOPE_FACTS),
        "cost_floor_bps": MINIMUM_RISK_DISTANCE_BPS,
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
    spec = build_tc_detector_spec_contract()
    if spec["verdict"] != VERDICT_TCD_READY:
        record["verdict"] = VERDICT_DRR_BLOCKED
        record["blockers"].append("detector_spec_not_ready")
        record["blockers"].extend(spec["blockers"])
        return record
    observed = _recompute_observation()
    mismatches = record["mismatches"]

    if observed["dry_run_verdict"] != EXPECTED_DETECTOR_VERDICT:
        mismatches.append("dry_run_verdict_changed:"
                          + str(observed["dry_run_verdict"]))
    if observed["dry_run_verdict"] != VERDICT_TCD_DRY_RUN_PASSED:
        mismatches.append("dry_run_no_longer_passing")

    exp_a = EXPECTED_ACCEPTED_FIXTURE
    if len(observed["accepted_run"]) != exp_a["total_labels"]:
        mismatches.append("accepted_fixture_label_count_changed")
    if len(observed["accepted"]) != exp_a["accepted_labels"]:
        mismatches.append("accepted_fixture_accept_count_changed")
    elif observed["accepted"]:
        winner = observed["accepted"][0]
        for label_field, expected_key in (
                ("setup_id", "accepted_setup_id"),
                ("entry_price", "entry_price"),
                ("stop_price", "stop_price"),
                ("structural_stop_price", "structural_stop_price"),
                ("stop_source", "stop_source"),
                ("risk_distance_bps", "risk_distance_bps"),
                ("target_2r_price", "target_2r_price"),
                ("target_3r_price", "target_3r_price"),
                ("target_4r_price", "target_4r_price")):
            if winner.get(label_field) != exp_a[expected_key]:
                mismatches.append("accepted_fixture_fact_changed:"
                                  + label_field)
        if not (winner.get("risk_distance_bps")
                >= MINIMUM_RISK_DISTANCE_BPS):
            mismatches.append("accepted_fixture_below_floor")
        if not (winner.get("volatility_stop_price")
                > winner.get("structural_stop_price")):
            mismatches.append("accepted_fixture_structural_not_wider")

    exp_t = EXPECTED_TIGHT_FIXTURE
    if len(observed["tight_run"]) != exp_t["total_labels"]:
        mismatches.append("tight_fixture_label_count_changed")
    if any(lab["status"] == "accepted_for_replay_review"
           for lab in observed["tight_run"]):
        mismatches.append("tight_fixture_accepted_something")
    if len(observed["floor_rejects"]) != exp_t["cost_floor_rejections"]:
        mismatches.append("tight_fixture_floor_reject_count_changed")
    elif observed["floor_rejects"]:
        reject = observed["floor_rejects"][0]
        if reject.get("setup_id") != exp_t["rejected_setup_id"]:
            mismatches.append("tight_fixture_fact_changed:setup_id")
        if reject.get("stop_source") != exp_t["stop_source"]:
            mismatches.append("tight_fixture_fact_changed:stop_source")
        if reject.get("risk_distance_bps") != exp_t["risk_distance_bps"]:
            mismatches.append("tight_fixture_fact_changed:risk_bps")
        if not (reject.get("risk_distance_bps")
                < MINIMUM_RISK_DISTANCE_BPS):
            mismatches.append("tight_fixture_not_below_floor")
        if not (reject.get("stop_price")
                < reject.get("structural_stop_price")):
            mismatches.append("tight_fixture_volatility_not_wider")

    exp_d = EXPECTED_DOWNTREND_FIXTURE
    if len(observed["down_run"]) != exp_d["total_labels"]:
        mismatches.append("downtrend_fixture_label_count_changed")
    if any(lab["status"] == "accepted_for_replay_review"
           for lab in observed["down_run"]):
        mismatches.append("downtrend_fixture_accepted_something")
    trend_rejects = [lab for lab in observed["down_run"] if lab["status"]
                     == "rejected_trend_not_qualified"]
    if len(trend_rejects) != exp_d["trend_rejections"]:
        mismatches.append("downtrend_fixture_trend_reject_count_changed")

    exp_al = EXPECTED_ANTI_LOOKAHEAD
    if observed["early"]["completed_bars"] != (
            exp_al["signal_0659_completed_1h_bars"]):
        mismatches.append("anti_lookahead_0659_bars_changed")
    if observed["early"]["insufficient_history"] is not (
            not exp_al["signal_0659_sufficient"]):
        mismatches.append("anti_lookahead_0659_sufficiency_changed")
    if observed["later"]["completed_bars"] != (
            exp_al["signal_0700_completed_1h_bars"]):
        mismatches.append("anti_lookahead_0700_bars_changed")
    if observed["later"]["insufficient_history"] is not (
            not exp_al["signal_0700_sufficient"]):
        mismatches.append("anti_lookahead_0700_sufficiency_changed")

    record["verdict"] = (VERDICT_DRR_APPROVED if not mismatches
                         else VERDICT_DRR_REJECTED)
    return record


def validate_dry_run_review(record: Any) -> dict[str, Any]:
    """Validate shape, frozen facts, and safety invariants. Never
    raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_DRR_APPROVED,
                                VERDICT_DRR_REJECTED,
                                VERDICT_DRR_BLOCKED):
        errors.append("bad_verdict")
    if r.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if r.get("expected_detector_verdict") != EXPECTED_DETECTOR_VERDICT:
        errors.append("expected_verdict_tampered")
    if r.get("expected_accepted_fixture") != EXPECTED_ACCEPTED_FIXTURE:
        errors.append("accepted_facts_tampered")
    if r.get("expected_tight_fixture") != EXPECTED_TIGHT_FIXTURE:
        errors.append("tight_facts_tampered")
    if r.get("expected_downtrend_fixture") != EXPECTED_DOWNTREND_FIXTURE:
        errors.append("downtrend_facts_tampered")
    if r.get("expected_anti_lookahead") != EXPECTED_ANTI_LOOKAHEAD:
        errors.append("anti_lookahead_facts_tampered")
    if tuple(r.get("frozen_scope_facts") or ()) != FROZEN_SCOPE_FACTS:
        errors.append("scope_facts_tampered")
    if r.get("cost_floor_bps") != MINIMUM_RISK_DISTANCE_BPS:
        errors.append("floor_tampered")
    if r.get("verdict") == VERDICT_DRR_APPROVED and r.get("mismatches"):
        errors.append("approved_with_mismatches")
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
