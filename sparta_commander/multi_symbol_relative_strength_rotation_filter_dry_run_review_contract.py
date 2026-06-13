"""SPARTA CANDIDATE #6 DRY-RUN REVIEW / EVIDENCE FREEZE (READ-ONLY,
RESEARCH ONLY): MULTI_SYMBOL_RELATIVE_STRENGTH_ROTATION_FILTER_V1.

Freezes the synthetic dry-run outcomes of the pushed Candidate #6
detector spec. The dry run is pure, deterministic and reads NO files, so
this review certifies by RE-COMPUTING every frozen fact live from the
pushed detector module -- fixture counts, the accepted setup's exact
geometry (entry 106.5, stop distance 1.5, STRUCTURE-wider not
ATR-wider, all 81 bps floors passing), the tie rejection, the three
negative-RS-at-rank-#1 rejections, the zero-attempt no-fresh-high case,
and the last-bar no-evaluation rejection. If any future change makes
the pushed scanner behave differently, this review flips to REJECTED on
its own.

Synthetic fixtures only. No real candle has been touched for candidate
#6, no staged data read, no aggregation executed, no labels, no replay,
no artifacts, and this module performs none. This gate authorizes NO
real detection: the real-candle gate becomes reachable only after this
review is committed and pushed, and opens only on its own explicit
human command. Nothing here is a profitability claim.
"""

from __future__ import annotations

from typing import Any

import sparta_commander.multi_symbol_relative_strength_rotation_filter_detector_spec_contract as _det
import sparta_commander.strategy_factory_autopilot_research_loop_v1_contract as _loop
import sparta_commander.strategy_factory_candidate_recommendation_v1_contract as _rec
from sparta_commander.multi_symbol_relative_strength_rotation_filter_family_proposal_contract import (
    CANDIDATE_ID,
    VERDICT_C6P_READY,
    build_candidate_6_family_proposal,
)
from sparta_commander.multi_symbol_relative_strength_rotation_filter_spec_review_contract import (
    VERDICT_C6S_READY,
    build_candidate_6_spec_review,
)

C6R_SCHEMA_VERSION = (
    "multi_symbol_relative_strength_rotation_filter_dry_run_review.v1")
C6R_LABEL = ("SPARTA Candidate #6 Dry-Run Review / Evidence Freeze "
             "(READ-ONLY, RESEARCH ONLY, SYNTHETIC OUTCOMES ONLY, "
             "NOT A PROFITABILITY CLAIM)")
C6R_MODE = "RESEARCH_ONLY"
VERDICT_C6R_FROZEN = "CANDIDATE_6_DRY_RUN_REVIEW_FROZEN"
VERDICT_C6R_REJECTED = "CANDIDATE_6_DRY_RUN_REVIEW_REJECTED"
VERDICT_C6R_BLOCKED = "CANDIDATE_6_DRY_RUN_REVIEW_BLOCKED"
NEXT_REQUIRED_ACTION = (
    "HUMAN_APPROVED_CANDIDATE_6_REAL_CANDLE_DETECTION")

EXPECTED_DETECTOR_VERDICT = "CANDIDATE_6_DETECTOR_SPEC_READY"
EXPECTED_DRY_RUN_VERDICT = "CANDIDATE_6_DETECTOR_DRY_RUN_PASSED"

EXPECTED_FIXTURE_COUNTS = {
    "sol_rank1_breakout": {"attempts": 1, "accepted": 1},
    "rank_tie_fails": {"attempts": 1, "accepted": 0},
    "rank1_but_negative_rs": {"attempts": 3, "accepted": 0},
    "no_fresh_closing_high": {"attempts": 0, "accepted": 0},
    "event_on_last_bar": {"attempts": 1, "accepted": 0},
}

EXPECTED_ACCEPTED_SETUP = {
    "symbol": "SOLUSD",
    "entry_price": 106.5,
    "stop_distance": 1.5,
    "structure_stop_distance": 1.5,
    "atr14": 0.571429,
    "stop_source": "structure_wider_than_1_5x_atr",
    "geometry_floor_pass_by_variant": {"2r": True, "3r": True,
                                       "4r": True},
    "target_distance_bps_2r": 281.690141,
    "event_time": "2026-04-02T06:00:00Z",
    "replay_start_time": "2026-04-02T07:00:00Z",
}

EXPECTED_REJECTION_FACTS = {
    "tie_status": "rejected_not_strict_rank_1",
    "negative_rs_status": "rejected_rs_not_positive",
    "negative_rs_all_strict_rank_1": True,
    "negative_rs_all_rs_not_positive": True,
    "last_bar_status": "rejected_no_evaluation_bar",
    "last_bar_reason": "no_next_bar_for_evaluation",
}

FROZEN_SCOPE_FACTS = (
    "synthetic in-memory fixtures only",
    "no real candle has been touched for candidate #6",
    "no staged data read; no 15m to 1h aggregation executed",
    "no labels, no replay, no artifacts",
    "frozen facts certify detector behavior, not edge",
    "nothing here is a profitability claim",
)

CLAIM_LOCKS = (
    "no_profitability_claim",
    "no_paper_approval",
    "no_live_approval",
    "no_execution_approval",
    "no_winner_wording",
)


def get_c6_dry_run_review_label() -> str:
    return C6R_LABEL


def _recompute_observation() -> dict[str, Any]:
    """Re-run the pushed dry run + targeted scans live (pure)."""
    dry = _det.run_c6_detector_dry_run()
    accepted_run = _det.scan_c6_setups(_det.build_bars({
        "BTCUSD": _det.fixture_flat(50.0),
        "ETHUSD": _det.fixture_flat(80.0),
        "SOLUSD": _det.fixture_sol_breakout()}), "SOLUSD")
    tie_run = _det.scan_c6_setups(_det.build_bars({
        "BTCUSD": _det.fixture_flat(50.0),
        "ETHUSD": _det.fixture_sol_breakout(),
        "SOLUSD": _det.fixture_sol_breakout()}), "SOLUSD")
    negative_run = _det.scan_c6_setups(_det.build_bars({
        "BTCUSD": _det.fixture_falling(300.0),
        "ETHUSD": _det.fixture_falling(250.0),
        "SOLUSD": _det.fixture_recovering_but_negative()}), "SOLUSD")
    truncated = _det.scan_c6_setups(_det.build_bars({
        "BTCUSD": _det.fixture_flat(50.0, 31),
        "ETHUSD": _det.fixture_flat(80.0, 31),
        "SOLUSD": _det.fixture_sol_breakout()[:31]}), "SOLUSD")
    return {"dry": dry, "accepted_run": accepted_run,
            "tie_run": tie_run, "negative_run": negative_run,
            "truncated_run": truncated}


def build_c6_dry_run_review() -> dict[str, Any]:
    """Recompute the dry run live and certify it against the frozen
    facts. Gated on the full pushed candidate #6 chain + recommendation
    + loop (+ the five-record ledger via the proposal)."""
    record: dict[str, Any] = {
        "schema_version": C6R_SCHEMA_VERSION, "label": C6R_LABEL,
        "mode": C6R_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [], "mismatches": [],
        "candidate_id": CANDIDATE_ID,
        "expected_detector_verdict": EXPECTED_DETECTOR_VERDICT,
        "expected_dry_run_verdict": EXPECTED_DRY_RUN_VERDICT,
        "expected_fixture_counts": {
            key: dict(value) for key, value
            in EXPECTED_FIXTURE_COUNTS.items()},
        "expected_accepted_setup": {
            key: (dict(value) if isinstance(value, dict) else value)
            for key, value in EXPECTED_ACCEPTED_SETUP.items()},
        "expected_rejection_facts": dict(EXPECTED_REJECTION_FACTS),
        "frozen_scope_facts": list(FROZEN_SCOPE_FACTS),
        "claim_locks": list(CLAIM_LOCKS),
        "real_detection_authorized_by_this_gate": False,
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
    detector = _det.build_c6_detector_spec_contract()
    if detector["verdict"] != _det.VERDICT_C6D_READY:
        record["verdict"] = VERDICT_C6R_BLOCKED
        record["blockers"].append("detector_spec_not_certifying")
        record["blockers"].extend(detector["blockers"])
        return record
    if build_candidate_6_spec_review()["verdict"] != VERDICT_C6S_READY:
        record["verdict"] = VERDICT_C6R_BLOCKED
        record["blockers"].append("spec_review_not_certifying")
        return record
    if build_candidate_6_family_proposal()["verdict"] != (
            VERDICT_C6P_READY):
        record["verdict"] = VERDICT_C6R_BLOCKED
        record["blockers"].append("family_proposal_not_certifying")
        return record
    if _rec.build_candidate_recommendation()["verdict"] != (
            _rec.VERDICT_CR_READY):
        record["verdict"] = VERDICT_C6R_BLOCKED
        record["blockers"].append("recommendation_not_certifying")
        return record
    if _loop.build_autopilot_loop_contract()["verdict"] != (
            _loop.VERDICT_AP_READY):
        record["verdict"] = VERDICT_C6R_BLOCKED
        record["blockers"].append("autopilot_loop_not_certifying")
        return record
    observed = _recompute_observation()
    mismatches = record["mismatches"]

    if observed["dry"]["verdict"] != EXPECTED_DRY_RUN_VERDICT:
        mismatches.append("dry_run_verdict_changed:"
                          + str(observed["dry"]["verdict"]))
    fixtures = observed["dry"]["fixtures"]
    for name, expected in EXPECTED_FIXTURE_COUNTS.items():
        got = fixtures.get(name) or {}
        if got.get("attempts") != expected["attempts"] \
                or got.get("accepted") != expected["accepted"]:
            mismatches.append("fixture_count_changed:" + name)

    accepted = [setup for setup in observed["accepted_run"]
                if setup["status"] == "accepted_for_replay_review"]
    if len(observed["accepted_run"]) != 1 or len(accepted) != 1:
        mismatches.append("accepted_fixture_changed")
    else:
        winner = accepted[0]
        exp = EXPECTED_ACCEPTED_SETUP
        for field in ("symbol", "entry_price", "stop_distance",
                      "structure_stop_distance", "atr14",
                      "geometry_floor_pass_by_variant",
                      "target_distance_bps_2r", "event_time",
                      "replay_start_time"):
            if winner.get(field) != exp[field]:
                mismatches.append("accepted_fact_changed:" + field)
        # STRUCTURE-wider, not ATR-wider, re-derived live
        if not (winner["structure_stop_distance"]
                > _det.ATR_MULTIPLIER * winner["atr14"]):
            mismatches.append("accepted_stop_not_structure_wider")
        if winner["stop_distance"] != winner["structure_stop_distance"]:
            mismatches.append("accepted_stop_source_changed")
        if not all(winner["geometry_floor_pass_by_variant"].values()):
            mismatches.append("accepted_floor_not_all_passing")
        if not winner["replay_start_time"] > winner["event_time"]:
            mismatches.append("accepted_replay_start_not_after_event")

    if [setup["status"] for setup in observed["tie_run"]] != [
            EXPECTED_REJECTION_FACTS["tie_status"]]:
        mismatches.append("tie_rejection_changed")
    negative = observed["negative_run"]
    if len(negative) != 3:
        mismatches.append("negative_rs_attempt_count_changed")
    else:
        for setup in negative:
            if setup["status"] != EXPECTED_REJECTION_FACTS[
                    "negative_rs_status"]:
                mismatches.append("negative_rs_status_changed")
                break
            if setup["strict_rank_1"] is not True:
                mismatches.append("negative_rs_rank_1_proof_broken")
                break
            if setup["rs_positive"] is not False:
                mismatches.append("negative_rs_positivity_proof_broken")
                break
    truncated = observed["truncated_run"]
    if [setup["status"] for setup in truncated] != [
            EXPECTED_REJECTION_FACTS["last_bar_status"]]:
        mismatches.append("last_bar_rejection_changed")
    elif EXPECTED_REJECTION_FACTS["last_bar_reason"] not in (
            truncated[0]["rejection_reasons"]):
        mismatches.append("last_bar_reason_changed")

    record["verdict"] = (VERDICT_C6R_FROZEN if not mismatches
                         else VERDICT_C6R_REJECTED)
    return record


def validate_c6_dry_run_review(record: Any) -> dict[str, Any]:
    """Validate shape, frozen facts, and safety invariants. Never
    raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_C6R_FROZEN, VERDICT_C6R_REJECTED,
                                VERDICT_C6R_BLOCKED):
        errors.append("bad_verdict")
    if r.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if r.get("expected_detector_verdict") != EXPECTED_DETECTOR_VERDICT:
        errors.append("detector_verdict_tampered")
    if r.get("expected_dry_run_verdict") != EXPECTED_DRY_RUN_VERDICT:
        errors.append("dry_run_verdict_tampered")
    expected_counts = {key: dict(value) for key, value
                       in EXPECTED_FIXTURE_COUNTS.items()}
    if r.get("expected_fixture_counts") != expected_counts:
        errors.append("fixture_counts_tampered")
    expected_setup = {key: (dict(value) if isinstance(value, dict)
                            else value)
                      for key, value in EXPECTED_ACCEPTED_SETUP.items()}
    if r.get("expected_accepted_setup") != expected_setup:
        errors.append("accepted_setup_tampered")
    if r.get("expected_rejection_facts") != EXPECTED_REJECTION_FACTS:
        errors.append("rejection_facts_tampered")
    if tuple(r.get("frozen_scope_facts") or ()) != FROZEN_SCOPE_FACTS:
        errors.append("scope_facts_tampered")
    if tuple(r.get("claim_locks") or ()) != CLAIM_LOCKS:
        errors.append("claim_locks_tampered")
    if r.get("real_detection_authorized_by_this_gate") is not False:
        errors.append("real_detection_must_not_be_authorized")
    if r.get("verdict") == VERDICT_C6R_FROZEN and r.get("mismatches"):
        errors.append("frozen_with_mismatches")
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
