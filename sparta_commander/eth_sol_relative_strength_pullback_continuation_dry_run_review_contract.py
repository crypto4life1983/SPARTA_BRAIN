"""SPARTA CANDIDATE #5 DRY-RUN REVIEW / EVIDENCE FREEZE (READ-ONLY,
RESEARCH ONLY): ETH_SOL_RELATIVE_STRENGTH_PULLBACK_CONTINUATION_V1.

Freezes the synthetic dry-run outcomes of the pushed Candidate #5
detector spec. The dry run is pure, deterministic and reads NO files, so
this review certifies by RE-COMPUTING every frozen fact live -- fixture
counts, accepted-record geometry, the partial-floor arithmetic, the
RS/pullback/trigger/stop proofs, the no-lookahead proofs, and the
non-overlap proofs. If any future change makes the pushed scanner behave
differently, this review flips to REJECTED on its own.

Synthetic fixtures only. No real candle has been read for candidate #5,
no real detector run, no replay, no fetch, and this module performs
none. This gate authorizes NO real detection: the real-candle gate
becomes reachable only after this review is committed and pushed, and it
opens only on its own explicit human command. Nothing here is a
profitability claim.
"""

from __future__ import annotations

from typing import Any

import sparta_commander.eth_sol_relative_strength_pullback_continuation_detector_spec_contract as _det
import sparta_commander.strategy_factory_autopilot_research_loop_v1_contract as _loop
from sparta_commander.eth_sol_relative_strength_pullback_continuation_family_proposal_contract import (
    CANDIDATE_ID,
    VERDICT_C5P_READY,
    build_candidate_5_family_proposal,
)
from sparta_commander.eth_sol_relative_strength_pullback_continuation_spec_review_contract import (
    VERDICT_C5S_READY,
    build_candidate_5_spec_review,
)

C5R_SCHEMA_VERSION = (
    "eth_sol_relative_strength_pullback_continuation_dry_run_review.v1")
C5R_LABEL = ("SPARTA Candidate #5 Dry-Run Review / Evidence Freeze "
             "(READ-ONLY, RESEARCH ONLY, SYNTHETIC OUTCOMES ONLY, "
             "NOT A PROFITABILITY CLAIM)")
C5R_MODE = "RESEARCH_ONLY"
VERDICT_C5R_FROZEN = "CANDIDATE_5_DRY_RUN_REVIEW_FROZEN"
VERDICT_C5R_REJECTED = "CANDIDATE_5_DRY_RUN_REVIEW_REJECTED"
VERDICT_C5R_BLOCKED = "CANDIDATE_5_DRY_RUN_REVIEW_BLOCKED"
NEXT_REQUIRED_ACTION = (
    "HUMAN_APPROVED_CANDIDATE_5_REAL_CANDLE_DETECTION")

EXPECTED_DETECTOR_VERDICT = "CANDIDATE_5_DETECTOR_SPEC_READY"
EXPECTED_DRY_RUN_VERDICT = "CANDIDATE_5_DETECTOR_DRY_RUN_PASSED"

EXPECTED_FIXTURE_COUNTS = {
    "eth_accepted": {"attempts": 1, "accepted": 1},
    "sol_accepted": {"attempts": 1, "accepted": 1},
    "rs_not_stronger": {"attempts": 1, "accepted": 0},
    "pullback_too_short": {"attempts": 1, "accepted": 0},
    "pullback_too_long": {"attempts": 1, "accepted": 0},
    "pullback_too_deep": {"attempts": 1, "accepted": 0},
    "pullback_below_leg_low": {"attempts": 1, "accepted": 0},
    "no_trigger_intrabar_only": {"attempts": 0, "accepted": 0},
    "tight_floor_partial": {"attempts": 1, "accepted": 1},
}

EXPECTED_ETH_ACCEPTED = {
    "symbol": "ETHUSD", "direction": "long", "timeframe": "1h",
    "accepted_count": 1,
    "entry_price": 110.7,
    "stop_distance": 1.8,
    "stop_price": 108.9,
    "atr14": 0.875,
    "stop_source": "structure_distance_greater_than_1_5x_atr",
    "geometry_floor_pass_by_variant": {"2r": True, "3r": True,
                                       "4r": True},
    "trigger_time": "2026-03-02T01:00:00Z",
    "replay_start_time": "2026-03-02T02:00:00Z",
}

EXPECTED_SOL_ACCEPTED = {
    "symbol": "SOLUSD", "direction": "long", "timeframe": "1h",
    "accepted_count": 1,
    "entry_price": 110.7,
    "stop_distance": 1.8,
    "same_frozen_scanner_geometry_as_eth": True,
}

EXPECTED_TIGHT_FLOOR = {
    "entry_price": 110.68,
    "stop_distance": 0.31,
    "target_distance_bps_2r": 56.017347,
    "target_distance_bps_3r": 84.026021,
    "target_distance_bps_4r": 112.034695,
    "floor_pass": {"2r": False, "3r": True, "4r": True},
    "floor_bps": 81.0,
}

FROZEN_DRY_RUN_PROOFS = (
    "rs gate: return_20 must be positive AND greater than the other "
    "symbol's return_20",
    "pullback: 2-6 bars only, depth at most 38.2 percent of the up-leg, "
    "pullback low above the up-leg low",
    "trigger: close above the pullback high required; an intrabar high "
    "alone is not enough; the rs gate must still pass at the trigger",
    "stop: distance must be positive; WIDER rule uses max(atr stop, "
    "structure stop); a min(...) mutation produces a different stop",
    "geometry: 27 bps fee assumption, 81 bps gross target-distance "
    "floor, 2r/3r/4r only",
    "no-lookahead: a future-bar mutation cannot change a past setup; "
    "replay_start_time is the next bar strictly after the trigger; a "
    "trigger on the last bar is rejected because no evaluation bar "
    "exists",
    "non-overlap: overlapping same-symbol setups removed "
    "deterministically; different symbols never block each other; "
    "kept plus removed equals total; reduce-only, never add",
    "purity: no file i/o, no network, no module-level runner, fully "
    "deterministic, no wall-clock behavior, no artifact creation",
    "safety: no paper/live/trading/wallet/account/api capability; no "
    "profitability or winner claim; no real-detection authorization "
    "from this gate",
)


def get_c5_dry_run_review_label() -> str:
    return C5R_LABEL


def _recompute_observation() -> dict[str, Any]:
    """Re-run the pushed dry run + targeted proofs live (pure)."""
    dry = _det.run_c5_detector_dry_run()
    flat = _det.fixture_flat_other()
    eth = _det.scan_c5_setups(_det.fixture_accepted(), flat, "ETHUSD")
    sol = _det.scan_c5_setups(_det.fixture_accepted(), flat, "SOLUSD")
    tight = _det.scan_c5_setups(_det.fixture_tight_floor(), flat,
                                "ETHUSD")
    # no-lookahead proofs
    bars = _det.fixture_accepted()
    mutated = [dict(b) for b in bars]
    mutated[28] = _det._bar(28, 50.0, 200.0, 10.0, 150.0)
    base = eth[0] if eth else None
    after = [s for s in _det.scan_c5_setups(mutated, flat, "ETHUSD")
             if base and s["setup_id"] == base["setup_id"]]
    last_bar_run = _det.scan_c5_setups(bars[:26], flat, "ETHUSD")
    # non-overlap proofs
    rows = [
        {"symbol": "ETHUSD", "trigger_time": "T01",
         "exit_time_by_variant": {"2r": "T05"}},
        {"symbol": "ETHUSD", "trigger_time": "T03",
         "exit_time_by_variant": {"2r": "T08"}},
        {"symbol": "ETHUSD", "trigger_time": "T06",
         "exit_time_by_variant": {"2r": "T09"}},
        {"symbol": "SOLUSD", "trigger_time": "T02",
         "exit_time_by_variant": {"2r": "T04"}},
    ]
    overlap = _det.apply_same_symbol_non_overlap(rows, "2r")
    return {"dry": dry, "eth": eth, "sol": sol, "tight": tight,
            "future_mutation_setups": after, "base": base,
            "last_bar_run": last_bar_run, "overlap": overlap,
            "rows_total": len(rows)}


def build_c5_dry_run_review() -> dict[str, Any]:
    """Recompute the dry run live and certify it against the frozen
    facts. Gated on the full pushed candidate #5 chain + loop +
    ledger."""
    record: dict[str, Any] = {
        "schema_version": C5R_SCHEMA_VERSION, "label": C5R_LABEL,
        "mode": C5R_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [], "mismatches": [],
        "candidate_id": CANDIDATE_ID,
        "expected_detector_verdict": EXPECTED_DETECTOR_VERDICT,
        "expected_dry_run_verdict": EXPECTED_DRY_RUN_VERDICT,
        "expected_fixture_counts": {
            key: dict(value) for key, value
            in EXPECTED_FIXTURE_COUNTS.items()},
        "expected_eth_accepted": {
            key: (dict(value) if isinstance(value, dict) else value)
            for key, value in EXPECTED_ETH_ACCEPTED.items()},
        "expected_sol_accepted": dict(EXPECTED_SOL_ACCEPTED),
        "expected_tight_floor": {
            key: (dict(value) if isinstance(value, dict) else value)
            for key, value in EXPECTED_TIGHT_FLOOR.items()},
        "frozen_dry_run_proofs": list(FROZEN_DRY_RUN_PROOFS),
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
    detector = _det.build_c5_detector_spec_contract()
    if detector["verdict"] != _det.VERDICT_C5D_READY:
        record["verdict"] = VERDICT_C5R_BLOCKED
        record["blockers"].append("detector_spec_not_certifying")
        record["blockers"].extend(detector["blockers"])
        return record
    if build_candidate_5_spec_review()["verdict"] != VERDICT_C5S_READY:
        record["verdict"] = VERDICT_C5R_BLOCKED
        record["blockers"].append("spec_review_not_certifying")
        return record
    if build_candidate_5_family_proposal()["verdict"] != (
            VERDICT_C5P_READY):
        record["verdict"] = VERDICT_C5R_BLOCKED
        record["blockers"].append("family_proposal_not_certifying")
        return record
    if _loop.build_autopilot_loop_contract()["verdict"] != (
            _loop.VERDICT_AP_READY):
        record["verdict"] = VERDICT_C5R_BLOCKED
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

    eth = observed["eth"]
    if len(eth) != 1 or eth[0]["status"] != "accepted_for_replay_review":
        mismatches.append("eth_accepted_changed")
    else:
        winner = eth[0]
        exp = EXPECTED_ETH_ACCEPTED
        for field in ("symbol", "direction", "timeframe", "entry_price",
                      "stop_distance", "stop_price", "atr14",
                      "geometry_floor_pass_by_variant", "trigger_time",
                      "replay_start_time"):
            if winner.get(field) != exp[field]:
                mismatches.append("eth_fact_changed:" + field)
        # stop source: structure strictly greater than 1.5 x atr
        if not (winner["entry_price"] - winner["pullback_low"]
                > _det.ATR_MULTIPLIER * winner["atr14"]):
            mismatches.append("eth_stop_source_not_structure")
        if not winner["replay_start_time"] > winner["trigger_time"]:
            mismatches.append("eth_replay_start_not_after_trigger")

    sol = observed["sol"]
    if len(sol) != 1 or sol[0]["status"] != "accepted_for_replay_review":
        mismatches.append("sol_accepted_changed")
    else:
        if sol[0]["symbol"] != "SOLUSD" \
                or sol[0]["entry_price"] != 110.7 \
                or sol[0]["stop_distance"] != 1.8 \
                or sol[0]["direction"] != "long" \
                or sol[0]["timeframe"] != "1h":
            mismatches.append("sol_fact_changed")

    tight = observed["tight"]
    if len(tight) != 1:
        mismatches.append("tight_floor_changed")
    else:
        got = tight[0]
        exp_t = EXPECTED_TIGHT_FLOOR
        if got["entry_price"] != exp_t["entry_price"] \
                or got["stop_distance"] != exp_t["stop_distance"] \
                or got["target_distance_bps_2r"] != (
                    exp_t["target_distance_bps_2r"]) \
                or got["target_distance_bps_3r"] != (
                    exp_t["target_distance_bps_3r"]) \
                or got["target_distance_bps_4r"] != (
                    exp_t["target_distance_bps_4r"]) \
                or got["geometry_floor_pass_by_variant"] != (
                    exp_t["floor_pass"]):
            mismatches.append("tight_floor_fact_changed")
        if not (exp_t["target_distance_bps_2r"]
                < exp_t["floor_bps"]
                <= exp_t["target_distance_bps_3r"]):
            mismatches.append("tight_floor_arithmetic_impossible")

    if len(observed["future_mutation_setups"]) != 1 \
            or observed["future_mutation_setups"][0] != observed["base"]:
        mismatches.append("no_lookahead_future_mutation_proof_broken")
    if any(s["status"] == "accepted_for_replay_review"
           for s in observed["last_bar_run"]):
        mismatches.append("last_bar_trigger_must_not_be_accepted")
    if not any("no_next_bar_for_evaluation" in s["rejection_reasons"]
               for s in observed["last_bar_run"]):
        mismatches.append("last_bar_rejection_reason_missing")

    overlap = observed["overlap"]
    kept_ids = {(r["symbol"], r["trigger_time"])
                for r in overlap["kept"]}
    removed_ids = {(r["symbol"], r["trigger_time"])
                   for r in overlap["removed"]}
    if removed_ids != {("ETHUSD", "T03")}:
        mismatches.append("non_overlap_removal_changed")
    if ("SOLUSD", "T02") not in kept_ids:
        mismatches.append("non_overlap_cross_symbol_blocked")
    if len(overlap["kept"]) + len(overlap["removed"]) != (
            observed["rows_total"]):
        mismatches.append("non_overlap_accounting_broken")
    if len(overlap["kept"]) > observed["rows_total"]:
        mismatches.append("non_overlap_added_trades_impossible")

    record["verdict"] = (VERDICT_C5R_FROZEN if not mismatches
                         else VERDICT_C5R_REJECTED)
    return record


def validate_c5_dry_run_review(record: Any) -> dict[str, Any]:
    """Validate shape, frozen facts, and safety invariants. Never
    raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_C5R_FROZEN, VERDICT_C5R_REJECTED,
                                VERDICT_C5R_BLOCKED):
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
    expected_eth = {key: (dict(value) if isinstance(value, dict)
                          else value)
                    for key, value in EXPECTED_ETH_ACCEPTED.items()}
    if r.get("expected_eth_accepted") != expected_eth:
        errors.append("eth_facts_tampered")
    if r.get("expected_sol_accepted") != EXPECTED_SOL_ACCEPTED:
        errors.append("sol_facts_tampered")
    expected_tight = {key: (dict(value) if isinstance(value, dict)
                            else value)
                      for key, value in EXPECTED_TIGHT_FLOOR.items()}
    if r.get("expected_tight_floor") != expected_tight:
        errors.append("tight_floor_tampered")
    if tuple(r.get("frozen_dry_run_proofs") or ()) != (
            FROZEN_DRY_RUN_PROOFS):
        errors.append("dry_run_proofs_tampered")
    if r.get("real_detection_authorized_by_this_gate") is not False:
        errors.append("real_detection_must_not_be_authorized")
    if r.get("verdict") == VERDICT_C5R_FROZEN and r.get("mismatches"):
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
