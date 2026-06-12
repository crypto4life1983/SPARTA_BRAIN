"""SPARTA CANDIDATE #4 DRY-RUN REVIEW / EVIDENCE FREEZE (READ-ONLY,
RESEARCH ONLY): SOL_BTC_LONG_1H_SWING_STRUCTURE_V1.

Freezes the synthetic dry-run outcomes of the pushed Candidate #4
detector spec. The dry run is pure, deterministic and reads NO files, so
this review certifies by RE-COMPUTING it live and comparing every frozen
fact byte-for-byte -- if any future change makes the pushed scanner
behave differently, this review flips to REJECTED on its own.

Synthetic fixtures only. No real-candle detection has happened for
Candidate #4, no replay, no fetch, and this module performs none. The
frozen facts certify detector BEHAVIOR, not edge: nothing here is a
profitability claim and nothing here authorizes anything.
"""

from __future__ import annotations

from typing import Any

from sparta_commander.ny_session_fvg_choch_mutable_candidate_edit_v2_cost_viability import (
    MINIMUM_RISK_DISTANCE_BPS,
)
from sparta_commander.sol_btc_long_1h_swing_structure_detector_spec_contract import (
    VERDICT_C4D_DRY_RUN_PASSED,
    VERDICT_C4D_READY,
    _fixture_1h_accepted,
    _fixture_1h_tight,
    _fixture_4h,
    build_c4_detector_spec_contract,
    evaluate_trend_qualification_4h,
    find_confirmed_swing_lows,
    run_c4_detector_dry_run,
    scan_c4_setups,
)
from sparta_commander.sol_btc_long_1h_swing_structure_strategy_spec_contract import (
    CANDIDATE_ID,
)

C4R_SCHEMA_VERSION = "sol_btc_long_1h_swing_structure_dry_run_review.v1"
C4R_LABEL = ("SPARTA Candidate #4 Dry-Run Review / Evidence Freeze "
             "(READ-ONLY, RESEARCH ONLY, SYNTHETIC OUTCOMES ONLY, "
             "NOT A PROFITABILITY CLAIM)")
C4R_MODE = "RESEARCH_ONLY"
VERDICT_C4R_APPROVED = (
    "CANDIDATE_4_DRY_RUN_REVIEW_APPROVED_DETECTOR_BEHAVIOR_FROZEN")
VERDICT_C4R_REJECTED = "CANDIDATE_4_DRY_RUN_REVIEW_REJECTED"
VERDICT_C4R_BLOCKED = "CANDIDATE_4_DRY_RUN_REVIEW_BLOCKED"
NEXT_REQUIRED_ACTION = (
    "HUMAN_APPROVED_CANDIDATE_4_REAL_CANDLE_DETECTION")

# --- frozen dry-run facts (exact values from the reviewed run) -------------

EXPECTED_DETECTOR_VERDICT = "CANDIDATE_4_DETECTOR_DRY_RUN_PASSED"

EXPECTED_ACCEPTED_FIXTURE = {
    "symbol": "SOLUSD",
    "total_labels": 1,
    "accepted_labels": 1,
    "accepted_setup_id": "SOLUSD_2026-02-02T16:00:00Z",
    "sl1_low_price": 99.0,
    "sl2_low_price": 99.8,
    "sl2_higher_than_sl1": True,
    "inter_swing_high_price": 101.5,
    "entry_price": 101.8,
    "structural_stop_price": 99.8,
    "stop_price": 99.8,
    "stop_source": "structural_sl2_low",
    "stop_selected_because": "structural_wider_than_1_5x_atr_stop",
    "risk_distance_bps": 196.463654,
    "risk_meets_81bps_floor": True,
    "target_2r_price": 105.8,
    "target_3r_price": 107.8,
    "target_4r_price": 109.8,
}

EXPECTED_TIGHT_FIXTURE = {
    "symbol": "BTCUSD",
    "total_labels": 1,
    "accepted_labels": 0,
    "cost_floor_rejections": 1,
    "rejected_setup_id": "BTCUSD_2026-02-02T15:00:00Z",
    "risk_distance_bps": 63.756744,
    "risk_below_81bps_floor": True,
}

EXPECTED_DOWNTREND_FIXTURE = {
    "symbol": "SOLUSD",
    "total_labels": 1,
    "accepted_labels": 0,
    "trend_rejections": 1,
}

EXPECTED_ANTI_LOOKAHEAD = {
    "gate_0359_completed_4h_bars": 12,
    "gate_0359_sufficient": False,
    "gate_0400_completed_4h_bars": 13,
    "gate_0400_sufficient": True,
    "swing_confirmation_lag_bars": 2,
    "swing_lows_full_series": (10, 16),
    "swing_lows_truncated_before_confirmation": (10,),
}

FROZEN_SCOPE_FACTS = (
    "synthetic in-memory fixtures only",
    "no real-candle detection has occurred for candidate #4",
    "no replay has occurred for candidate #4",
    "frozen facts certify detector behavior, not edge",
    "nothing here is a profitability claim",
)


def get_c4_dry_run_review_label() -> str:
    return C4R_LABEL


def _recompute_observation() -> dict[str, Any]:
    """Re-run the pushed dry run + scanners live (pure, in-memory)."""
    uptrend_4h = _fixture_4h(True)
    bars_accepted = _fixture_1h_accepted()
    accepted_run = scan_c4_setups(bars_accepted, uptrend_4h, "SOLUSD")
    accepted = [lab for lab in accepted_run
                if lab["status"] == "accepted_for_replay_review"]
    tight_run = scan_c4_setups(_fixture_1h_tight(), uptrend_4h, "BTCUSD")
    floor_rejects = [lab for lab in tight_run if lab["status"]
                     == "rejected_cost_floor_risk_too_small"]
    down_run = scan_c4_setups(bars_accepted, _fixture_4h(False), "SOLUSD")
    early = evaluate_trend_qualification_4h(
        uptrend_4h, "2026-01-31T03:59:00Z")
    later = evaluate_trend_qualification_4h(
        uptrend_4h, "2026-01-31T04:00:00Z")
    return {
        "dry_run_verdict": run_c4_detector_dry_run()["verdict"],
        "accepted_run": accepted_run, "accepted": accepted,
        "tight_run": tight_run, "floor_rejects": floor_rejects,
        "down_run": down_run, "early": early, "later": later,
        "swings_full": tuple(find_confirmed_swing_lows(bars_accepted)),
        "swings_truncated": tuple(
            find_confirmed_swing_lows(bars_accepted[:17])),
    }


def build_c4_dry_run_review() -> dict[str, Any]:
    """Recompute the dry run live and certify it against the frozen
    facts. Gated on the detector spec contract being READY."""
    record: dict[str, Any] = {
        "schema_version": C4R_SCHEMA_VERSION, "label": C4R_LABEL,
        "mode": C4R_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [], "mismatches": [],
        "candidate_id": CANDIDATE_ID,
        "expected_detector_verdict": EXPECTED_DETECTOR_VERDICT,
        "expected_accepted_fixture": dict(EXPECTED_ACCEPTED_FIXTURE),
        "expected_tight_fixture": dict(EXPECTED_TIGHT_FIXTURE),
        "expected_downtrend_fixture": dict(EXPECTED_DOWNTREND_FIXTURE),
        "expected_anti_lookahead": {
            key: (list(value) if isinstance(value, tuple) else value)
            for key, value in EXPECTED_ANTI_LOOKAHEAD.items()},
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
        "claims_profitability": False, "revives_candidate_3": False,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    spec = build_c4_detector_spec_contract()
    if spec["verdict"] != VERDICT_C4D_READY:
        record["verdict"] = VERDICT_C4R_BLOCKED
        record["blockers"].append("detector_spec_not_ready")
        record["blockers"].extend(spec["blockers"])
        return record
    observed = _recompute_observation()
    mismatches = record["mismatches"]

    if observed["dry_run_verdict"] != EXPECTED_DETECTOR_VERDICT:
        mismatches.append("dry_run_verdict_changed:"
                          + str(observed["dry_run_verdict"]))
    if observed["dry_run_verdict"] != VERDICT_C4D_DRY_RUN_PASSED:
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
                ("sl1_low_price", "sl1_low_price"),
                ("sl2_low_price", "sl2_low_price"),
                ("inter_swing_high_price", "inter_swing_high_price"),
                ("entry_price", "entry_price"),
                ("structural_stop_price", "structural_stop_price"),
                ("stop_price", "stop_price"),
                ("stop_source", "stop_source"),
                ("risk_distance_bps", "risk_distance_bps"),
                ("target_2r_price", "target_2r_price"),
                ("target_3r_price", "target_3r_price"),
                ("target_4r_price", "target_4r_price")):
            if winner.get(label_field) != exp_a[expected_key]:
                mismatches.append("accepted_fixture_fact_changed:"
                                  + label_field)
        if not (winner.get("sl2_low_price")
                > winner.get("sl1_low_price")):
            mismatches.append("accepted_fixture_not_higher_low")
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
        if reject.get("risk_distance_bps") != exp_t["risk_distance_bps"]:
            mismatches.append("tight_fixture_fact_changed:risk_bps")
        if not (reject.get("risk_distance_bps")
                < MINIMUM_RISK_DISTANCE_BPS):
            mismatches.append("tight_fixture_not_below_floor")

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
            exp_al["gate_0359_completed_4h_bars"]):
        mismatches.append("anti_lookahead_0359_bars_changed")
    if observed["early"]["insufficient_history"] is not (
            not exp_al["gate_0359_sufficient"]):
        mismatches.append("anti_lookahead_0359_sufficiency_changed")
    if observed["later"]["completed_bars"] != (
            exp_al["gate_0400_completed_4h_bars"]):
        mismatches.append("anti_lookahead_0400_bars_changed")
    if observed["later"]["insufficient_history"] is not (
            not exp_al["gate_0400_sufficient"]):
        mismatches.append("anti_lookahead_0400_sufficiency_changed")
    if observed["swings_full"] != exp_al["swing_lows_full_series"]:
        mismatches.append("swing_detection_changed")
    if observed["swings_truncated"] != (
            exp_al["swing_lows_truncated_before_confirmation"]):
        mismatches.append("swing_confirmation_lag_broken")

    record["verdict"] = (VERDICT_C4R_APPROVED if not mismatches
                         else VERDICT_C4R_REJECTED)
    return record


def validate_c4_dry_run_review(record: Any) -> dict[str, Any]:
    """Validate shape, frozen facts, and safety invariants. Never
    raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_C4R_APPROVED,
                                VERDICT_C4R_REJECTED,
                                VERDICT_C4R_BLOCKED):
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
    expected_al = {
        key: (list(value) if isinstance(value, tuple) else value)
        for key, value in EXPECTED_ANTI_LOOKAHEAD.items()}
    if r.get("expected_anti_lookahead") != expected_al:
        errors.append("anti_lookahead_facts_tampered")
    if tuple(r.get("frozen_scope_facts") or ()) != FROZEN_SCOPE_FACTS:
        errors.append("scope_facts_tampered")
    if r.get("cost_floor_bps") != MINIMUM_RISK_DISTANCE_BPS:
        errors.append("floor_tampered")
    if r.get("verdict") == VERDICT_C4R_APPROVED and r.get("mismatches"):
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
                "claims_profitability", "revives_candidate_3"):
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)
    return {"valid": not errors, "errors": errors}
