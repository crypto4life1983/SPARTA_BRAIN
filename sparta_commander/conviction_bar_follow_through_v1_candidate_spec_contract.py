"""SPARTA Candidate #14 candidate specification: conviction_bar_follow_through_v1.

SPEC ONLY. RESEARCH ONLY. This contract advances Candidate #14 from the family
proposal to a strict, pre-registered candidate specification. It is pure and
in-memory: NO detector, NO labels, NO replay, NO robustness, NO generalization
run, NO data fetch, NO trading, NO portfolio compute, NO downstream gate unlock.
It only fixes the hypothesis geometry + the research protocol for human review.

Chain gate: build_candidate_14_spec() requires build_candidate_14_family_proposal()
to return CANDIDATE_14_FAMILY_PROPOSAL_READY.

THE C10 + C11 + C12 + C13 LESSONS (enforced here as structural requirements):
  * C10: no date/weekday trigger; regime symmetry + forward-OOS mandatory early.
  * C11: strong labels are NECESSARY BUT NOT SUFFICIENT; forward-OOS + bull/bear/
    chop net symmetry are HARD replay gates.
  * C12: the must-beat-RANDOM-ENTRY baseline is the decisive anti-edge filter;
    target capture must dominate; must beat buy-and-hold.
  * C13: a too-RARE trigger is a STRUCTURAL REJECTION at the labels stage BEFORE
    replay -- the labels sample-size gate (>=100 total / >=20 per asset / >=20
    per regime + a populated forward-OOS window) is enforced FIRST, and the
    conviction threshold is pre-registered FREQUENT ENOUGH to clear it (never
    fit to manufacture samples).
"""
from __future__ import annotations

from typing import Any

from sparta_commander.conviction_bar_follow_through_v1_family_proposal_contract import (  # noqa: E501
    CANDIDATE_FAMILY,
    CANDIDATE_ID,
    REJECTED_FAMILIES_C1_TO_C13,
    VERDICT_C14P_READY,
    build_candidate_14_family_proposal,
)

C14S_SCHEMA_VERSION = 1
C14S_MODE = "RESEARCH_ONLY"
CANDIDATE_NUMBER = 14

VERDICT_C14S_READY = "CANDIDATE_14_SPEC_READY"
VERDICT_C14S_BLOCKED = "CANDIDATE_14_SPEC_BLOCKED"
NEXT_REQUIRED_ACTION = "HUMAN_DECISION_C14_ADVANCE_TO_DETECTOR_SPEC_OR_REJECT"

HEAD_AT_C14_PROPOSAL = "127d959a0aea695ba42993a1fb046a4c2c96823a"

# --- 1. symbol universe (cross-asset required; never single-asset) ----------
SYMBOL_UNIVERSE = ("BTCUSD", "ETHUSD", "SOLUSD")
MIN_ASSETS_REQUIRED = 3
MARKET_TYPE = "spot"
DIRECTION = "long_only"
DIRECTION_NOTE = ("long-only research labels on the conviction-bar "
                  "follow-through; never a short/borrow leg, never a trading "
                  "capability")
NO_DATA_FETCH = True
SOURCES_FROZEN_ON_DISK = ("data/crypto_d1_spot/raw/BTC_1d.csv",
                          "data/crypto_d1_spot/raw/ETH_1d.csv",
                          "data/crypto_d1_spot/raw/SOL_1d.csv")

# --- 2. timeframe -----------------------------------------------------------
TIMEFRAME = "1d"
SESSION = ("24/7 crypto; weekday-agnostic by construction (no weekday/calendar "
           "trigger permitted)")

# --- 3. conviction-bar definition + entry (pre-registered; deterministic) ---
ATR_LENGTH = 14
RANGE_ATR_MULTIPLE = 1.5            # true_range >= 1.5 * ATR(14) (outlier, frequent)
CLOSE_LOCATION_MIN = 0.75          # close in the TOP quartile of the bar range
CONVICTION_BAR_DEFINITION = (
    "On bar t let true_range = max(high-low, |high-prev_close|, |low-prev_close|) "
    "and ATR = ATR(14) at t. A CONVICTION BAR requires BOTH: (a) true_range >= "
    "RANGE_ATR_MULTIPLE * ATR (a volatility-expansion OUTLIER, NOT conditioned on "
    "any prior compression) AND (b) close-location: close >= low + "
    "CLOSE_LOCATION_MIN * (high - low)  (the close in the TOP quartile of the "
    "bar's own range). No date/weekday condition; no level breakout; no prior "
    "compression precondition.")
ENTRY_CONCEPT = {
    "trigger": "single_bar_conviction_event_range_outlier_plus_strong_close",
    "range_atr_multiple": RANGE_ATR_MULTIPLE,
    "atr_length": ATR_LENGTH,
    "close_location_min": CLOSE_LOCATION_MIN,
    "condition_a_range_outlier": "true_range >= 1.5 * ATR(14)",
    "condition_b_strong_close": "close >= low + 0.75 * (high - low)",
    "entry_price": "close of the conviction (signal) bar (no intrabar entry)",
    "one_position_per_asset": True,
    "no_compression_precondition": True,
    "weekday_or_calendar_trigger": False,
    "single_asset_or_single_weekday": False,
    "relies_on_long_drift_or_bull_carry": False,
}

# --- 4. stop / risk geometry (ATR(14)-validated; never tightened post-hoc) --
STOP_ATR_MULTIPLIER = 1.0
RISK_GEOMETRY = {
    "atr_length": ATR_LENGTH,
    "structure_stop": ("stop_price = entry_close - STOP_ATR_MULTIPLIER * "
                       "ATR(14) at the signal bar; stop_distance = entry_close - "
                       "stop_price; INVALID if stop_distance <= 0 or stop not "
                       "below entry; never tightened post-hoc"),
    "stop_atr_multiplier": STOP_ATR_MULTIPLIER,
    "risk_unit_R": "stop_distance (entry_close - stop_price)",
    "sizing": "equal-weight / fixed-fraction research sizing only; NO leverage; "
              "NO shorting; NO portfolio compute",
}

# --- 5. target variants (pre-registered; no new variants after label freeze) -
TARGET_VARIANTS = ("1r", "1.5r", "2r")
TARGET_R_MULTIPLES = {"1r": 1.0, "1.5r": 1.5, "2r": 2.0}
TARGET_POLICY = {
    "variants": list(TARGET_VARIANTS),
    "target_r_multiples": dict(TARGET_R_MULTIPLES),
    "target_price_formula": "entry_close + R_multiple * stop_distance",
    "no_new_variants_after_label_freeze": True,
}
TARGET_DISTANCE_FLOOR_BPS = 81.0

# --- 6. cost model (fee + slippage honest; inherits C10-C13 discipline) -----
FEE_ROUND_TRIP_BPS = 27.0
SLIPPAGE_ROUND_TRIP_BPS = 10.0
ALL_IN_ROUND_TRIP_BPS = 37.0
COST_MODEL = {
    "fee_round_trip_bps": FEE_ROUND_TRIP_BPS,
    "slippage_round_trip_bps": SLIPPAGE_ROUND_TRIP_BPS,
    "all_in_round_trip_bps": ALL_IN_ROUND_TRIP_BPS,
    "applied_as": "R-units of the setup stop distance "
                  "(net_r = gross_r - all_in_bps / stop_distance_bps)",
    "taker_default": True,
    "no_zero_fee_no_maker_rebate_default": True,
    "risk_floor": ("a setup is rejected unless at least one target variant's "
                   "GROSS target distance >= TARGET_DISTANCE_FLOOR_BPS (81 bps)"),
}

# --- 7. holding horizon + exit handling (human-fixed; disclosed; not optimized)
MAX_HOLD_BARS = 2                  # human-fixed in 1-2 range; disclosed
HORIZON_SOURCE = "human_fixed_short_hold_1_to_2_bars_spec_predeclared_max_2"
EXIT_POLICY = {
    "max_hold_bars": MAX_HOLD_BARS,
    "scan_window": "bars [entry_index+1 .. entry_index+MAX_HOLD_BARS] "
                   "(next-bar onward; entry bar not re-scanned)",
    "stop_hit": "low <= stop_price -> gross_r = -1",
    "target_hit": "high >= target_price -> gross_r = +R_multiple",
    "same_bar_straddle": "STOP FIRST (conservative) -> gross_r = -1",
    "horizon_exit": ("if neither stop nor target by entry_index+MAX_HOLD_BARS, "
                     "exit at that bar's close -> gross_r = "
                     "(exit_close - entry_close) / stop_distance"),
    "decisive": "every setup resolves; horizon bars beyond source excluded",
    "horizon_not_optimized_after_results": True,
}

# --- 8. non-overlap rule ----------------------------------------------------
NON_OVERLAP_POLICY = {
    "rule": "per_asset_resolved_exit_reduce_or_keep_only_never_add",
    "detail": ("one position per asset: drop a later setup on the SAME asset "
               "whose entry_index <= that asset's active resolved exit index; "
               "different assets may overlap; never add"),
}

# --- 9. baseline comparisons (the anti-carry / anti-drift gates) ------------
BASELINE_COMPARISONS = {
    "matched_buy_and_hold": (
        "long the SAME asset over the same entry windows, passive hold to the "
        "+MAX_HOLD close, same cost; the strategy MUST EXCEED it"),
    "matched_random_entry": (
        "the same number of entries per asset on the same date span drawn with a "
        "FIXED DETERMINISTIC SEED, identical stop/target/horizon geometry + cost; "
        "the strategy MUST EXCEED it (the conviction-bar filter must add timing "
        "value over random)"),
    "both_required": True,
    "failing_either_is_structural_rejection": True,
}

# --- 10. early structural rejection gates (battery; before robustness) ------
MAX_HORIZON_EXIT_SHARE = 0.50
EARLY_STRUCTURAL_REJECTION_GATES = (
    "structural_labels_sample_size_gate_required_first",
    "forward_oos_continuation_required_early",
    "cross_regime_bull_bear_chop_symmetry_required_early",
    "cross_asset_multiple_assets_required_early",
    "beats_matched_buy_and_hold_baseline_required_early",
    "beats_matched_random_entry_baseline_required_early",
    "target_capture_dominates_horizon_exit_share_capped_required_early",
    "no_weekday_or_calendar_dependence_required_early",
)
SAMPLE_SIZE_REQUIREMENTS = {
    "min_accepted_total": 100,
    "min_accepted_per_asset": 20,
    "min_accepted_per_regime": 20,          # bull / bear / chop
    "forward_oos_window_must_be_populated": True,
    "enforced_at": "labels_review_gate_BEFORE_replay",
    "below_minimum_is_structural_rejection": True,
    "is_the_c13_lesson": True,
}

# --- invalidation / rejection rules -----------------------------------------
INVALIDATION_REJECTION_RULES = (
    "Bar is not a conviction bar (true_range < 1.5*ATR OR close < top quartile) "
    "-> no entry.",
    "Invalid stop geometry (stop_distance <= 0 or stop not below entry) -> "
    "setup rejected.",
    "No target variant clears the 81 bps gross target-distance floor -> setup "
    "rejected.",
    "Sample below total/per-asset/per-regime minimums OR an empty forward-OOS "
    "window at the labels gate -> STRUCTURAL rejection BEFORE replay (the C13 "
    "lesson).",
    "Result horizon/drift dominated (horizon-exit share > 50%) -> STRUCTURAL "
    "rejection.",
    "Does not beat matched buy-and-hold OR matched random-entry baseline -> "
    "STRUCTURAL rejection.",
    "Not regime-symmetric across bull/bear/chop -> STRUCTURAL rejection.",
    "Does not continue in forward-OOS -> STRUCTURAL rejection.",
    "Single-asset dependence or any weekday/calendar dependence -> STRUCTURAL "
    "rejection.",
    "Any parameter fit beyond the single documented one-edit allowance, or any "
    "post-OOS rescue edit, or fitting the threshold to manufacture samples -> "
    "STRUCTURAL rejection.",
)

# --- one-edit allowance rules -----------------------------------------------
ONE_EDIT_ALLOWANCE = {
    "exactly_one_documented_parameter_edit_permitted": True,
    "editable_scope": ("a single pre-registered parameter -- exactly ONE of "
                       "{RANGE_ATR_MULTIPLE, CLOSE_LOCATION_MIN, "
                       "STOP_ATR_MULTIPLIER, MAX_HOLD_BARS} -- may be changed "
                       "once"),
    "must_be_documented_before_rerun": True,
    "must_revalidate_full_early_battery": True,
    "never_to_rescue_after_seeing_forward_oos": True,
    "never_to_manufacture_samples": True,
    "never_reused_more_than_once": True,
    "does_not_unlock_any_downstream_gate": True,
    "second_edit_is_structural_rejection": True,
}

# --- anti-overfit / generalization rules (C10-C13 lessons, ENFORCED) --------
ANTI_OVERFIT_GENERALIZATION_RULES = {
    "early_battery": list(EARLY_STRUCTURAL_REJECTION_GATES),
    "battery_runs_before_robustness_and_before_promotion": True,
    "failing_any_battery_check_is_structural_rejection": True,
    "structural_labels_sample_size_gate_enforced_before_replay": True,
    "pre_registered_deterministic_threshold_no_grid_fitting": True,
    "threshold_not_fit_to_manufacture_samples": True,
    "no_weekday_or_calendar_trigger": True,
    "no_best_cell_selected_as_promotion": True,
    "regime_symmetry_required_not_long_drift": True,
    "must_beat_buy_and_hold_and_random_entry": True,
    "target_capture_must_dominate_horizon_capped": True,
    "max_horizon_exit_share": MAX_HORIZON_EXIT_SHARE,
    "is_oos_sealed_before_any_run": True,
    "original_rejected_geometry_never_reused_unchanged": True,
}

# --- next gate after spec ---------------------------------------------------
NEXT_GATE_AFTER_SPEC = {
    "action": NEXT_REQUIRED_ACTION,
    "description": ("Human decides whether to advance C14 to the detector spec / "
                    "dry-run gate (still no labels, no replay, no data fetch) or "
                    "reject. The structural labels sample-size gate + the early "
                    "generalization + anti-drift battery are mandatory at the "
                    "labels/replay stage that follows."),
}

C14S_LABEL = (
    "SPARTA Candidate #14 Candidate Spec (READ-ONLY, RESEARCH ONLY). "
    "conviction_bar_follow_through: long after a single-bar conviction event "
    "(true_range >= 1.5*ATR(14) AND close >= low+0.75*range); ATR(14) stop; "
    "1R/1.5R/2R; <=2-bar hold; 37 bps. MATERIALLY DIFFERENT FROM C1-C13. SPEC "
    "ONLY -- NO DETECTOR, NO LABELS, NO REPLAY, NO DATA FETCH, NO TRADING. "
    "STRUCTURAL LABELS SAMPLE-SIZE GATE + FORWARD-OOS + REGIME SYMMETRY + "
    "MUST-BEAT-BUY&HOLD + MUST-BEAT-RANDOM + TARGET-CAPTURE-DOMINANCE ARE "
    "MANDATORY EARLY GATES."
)

_CAPABILITY_FLAGS_FALSE = (
    "runs_detector", "builds_detector_now", "runs_labels", "labels_now",
    "runs_replay", "runs_replay_now", "runs_robustness", "runs_generalization",
    "fetches_data", "stages_data_now", "calls_api", "uses_network",
    "uses_credentials", "uses_wallet", "uses_account", "connects_broker",
    "connects_exchange", "uses_real_money", "contains_order_logic",
    "contains_portfolio_allocation_logic", "runs_portfolio_compute",
    "deploys_capital", "starts_scheduler", "sends_notifications",
    "auto_commits", "auto_pushes", "reuses_rejected_geometry_unchanged",
    "fits_parameters_beyond_one_edit", "uses_weekday_or_calendar_trigger",
    "is_single_asset_edge", "relies_on_long_drift_or_bull_carry",
    "fits_threshold_to_manufacture_samples", "is_a_rescue_attempt",
    "authorizes_paper_execution", "authorizes_micro_live",
    "authorizes_live_trading", "promotes_gate", "unlocks_downstream_gate",
    "claims_profitability", "claims_edge", "claims_paper_or_live_readiness",
    "executes", "writes_files",
)


def get_candidate_14_spec_label() -> str:
    return C14S_LABEL


def get_candidate_14_spec_next_action() -> str:
    return NEXT_REQUIRED_ACTION


def build_candidate_14_spec(repo_root: Any = ".",
                            tracked_paths: list | None = None
                            ) -> dict[str, Any]:
    """Assemble the strict Candidate #14 candidate spec. Chain-gated on the
    READY family proposal. Pure; no I/O; spec only."""
    record: dict[str, Any] = {
        "schema_version": C14S_SCHEMA_VERSION,
        "label": C14S_LABEL, "mode": C14S_MODE,
        "lane": "crypto_d1_auto_research",
        "candidate_number": CANDIDATE_NUMBER,
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "verdict": None, "blockers": [],
        "head_at_c14_proposal": HEAD_AT_C14_PROPOSAL,
        # 1-10 spec sections
        "symbol_universe": list(SYMBOL_UNIVERSE),
        "min_assets_required": MIN_ASSETS_REQUIRED,
        "market_type": MARKET_TYPE,
        "direction": DIRECTION, "direction_note": DIRECTION_NOTE,
        "no_data_fetch": NO_DATA_FETCH,
        "sources_frozen_on_disk": list(SOURCES_FROZEN_ON_DISK),
        "timeframe": TIMEFRAME, "session": SESSION,
        "conviction_bar_definition": CONVICTION_BAR_DEFINITION,
        "range_atr_multiple": RANGE_ATR_MULTIPLE,
        "close_location_min": CLOSE_LOCATION_MIN,
        "entry_concept": dict(ENTRY_CONCEPT),
        "risk_geometry": dict(RISK_GEOMETRY),
        "target_policy": dict(TARGET_POLICY),
        "target_distance_floor_bps": TARGET_DISTANCE_FLOOR_BPS,
        "cost_model": dict(COST_MODEL),
        "exit_policy": dict(EXIT_POLICY),
        "max_hold_bars": MAX_HOLD_BARS,
        "horizon_source": HORIZON_SOURCE,
        "non_overlap_policy": dict(NON_OVERLAP_POLICY),
        "baseline_comparisons": dict(BASELINE_COMPARISONS),
        "early_structural_rejection_gates":
            list(EARLY_STRUCTURAL_REJECTION_GATES),
        "max_horizon_exit_share": MAX_HORIZON_EXIT_SHARE,
        "sample_size_requirements": dict(SAMPLE_SIZE_REQUIREMENTS),
        "invalidation_rejection_rules": list(INVALIDATION_REJECTION_RULES),
        "one_edit_allowance": dict(ONE_EDIT_ALLOWANCE),
        "anti_overfit_generalization_rules":
            dict(ANTI_OVERFIT_GENERALIZATION_RULES),
        "next_gate_after_spec": dict(NEXT_GATE_AFTER_SPEC),
        "rejected_families_c1_to_c13": list(REJECTED_FAMILIES_C1_TO_C13),
        # posture
        "is_spec_only": True,
        "is_materially_new_family": True,
        "is_a_rescue_attempt": False,
        "relies_on_long_drift_or_bull_carry": False,
        "current_loop_stage": "candidate_spec",
        "human_review_required": True,
        "detector_gate_locked": True,
        "labels_gate_locked": True,
        "replay_gate_locked": True,
        "data_fetch_gate_locked": True,
        "paper_trading_gate_locked": True,
        "live_gate_locked": True,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_detector": True, "no_labels": True, "no_replay": True,
        "no_robustness_run": True, "no_generalization_run": True,
        "no_data_fetch": True, "no_paper_trading": True, "no_live_trading": True,
        "no_broker": True, "no_credentials": True, "no_order_logic": True,
        "no_portfolio_compute": True, "no_parameter_fitting_beyond_one_edit": True,
        "no_threshold_fit_to_manufacture_samples": True,
        "no_weekday_trigger": True, "no_calendar_trigger": True,
        "no_best_cell_selected_as_promotion": True,
        "no_rescue_of_rejected_geometry": True,
        "no_long_drift_or_bull_carry_reliance": True,
        "no_profitability_claim": True,
        "no_paper_live_readiness_claim": True, "no_downstream_gate_unlock": True,
    }

    # Materially new + must not be a rejected family.
    if CANDIDATE_FAMILY in REJECTED_FAMILIES_C1_TO_C13:
        record["verdict"] = VERDICT_C14S_BLOCKED
        record["blockers"].append("spec_family_is_a_rejected_family")
        return record

    proposal = build_candidate_14_family_proposal(repo_root, tracked_paths or [])
    record["proposal_verdict"] = proposal.get("verdict")
    if proposal.get("verdict") != VERDICT_C14P_READY:
        record["verdict"] = VERDICT_C14S_BLOCKED
        record["blockers"].append("proposal_not_ready")
        return record

    record["verdict"] = VERDICT_C14S_READY
    return record


def validate_candidate_14_spec(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. READY only when the spec is materially new, pins
    all sections (conviction-bar rule 1.5*ATR + 0.75 close-location, ATR stop,
    81 bps floor over 37 bps cost, 1R/1.5R/2R, <=2-bar hold, per-asset non-
    overlap, BOTH baseline gates, the full early battery WITH the structural
    labels sample-size gate FIRST + the horizon cap, the one-edit allowance),
    enforces no calendar/weekday + no long-drift reliance + no threshold fitting,
    and locks all execution gates."""
    failures: list = []
    if record.get("verdict") != VERDICT_C14S_READY:
        failures.append("verdict_not_ready")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("mode") != C14S_MODE:
        failures.append("mode_not_research_only")
    if record.get("candidate_number") != 14:
        failures.append("candidate_number_tampered")
    if record.get("proposal_verdict") != VERDICT_C14P_READY:
        failures.append("proposal_verdict_tampered")

    # Materially new.
    if record.get("is_materially_new_family") is not True:
        failures.append("not_marked_materially_new")
    if record.get("candidate_family") in (
            record.get("rejected_families_c1_to_c13") or []):
        failures.append("spec_family_is_rejected_family")

    # 1-2 universe + timeframe + no fetch.
    su = record.get("symbol_universe") or []
    if len(su) < MIN_ASSETS_REQUIRED:
        failures.append("symbol_universe_too_small_single_asset_trap")
    if record.get("timeframe") != "1d":
        failures.append("timeframe_tampered")
    if record.get("market_type") != "spot":
        failures.append("market_type_tampered")
    if record.get("no_data_fetch") is not True:
        failures.append("no_data_fetch_flag_tampered")

    # 3 conviction-bar rule.
    if not record.get("conviction_bar_definition"):
        failures.append("conviction_bar_definition_missing")
    if record.get("range_atr_multiple") != RANGE_ATR_MULTIPLE:
        failures.append("range_multiple_tampered")
    if record.get("close_location_min") != CLOSE_LOCATION_MIN:
        failures.append("close_location_tampered")
    ec = record.get("entry_concept") or {}
    if ec.get("no_compression_precondition") is not True:
        failures.append("compression_precondition_introduced")
    if ec.get("weekday_or_calendar_trigger") is not False:
        failures.append("entry_uses_weekday_or_calendar_trigger")
    if ec.get("single_asset_or_single_weekday") is not False:
        failures.append("entry_is_single_asset_or_single_weekday")
    if ec.get("relies_on_long_drift_or_bull_carry") is not False:
        failures.append("entry_relies_on_long_drift")

    # 4-7 geometry / cost / exit.
    for section in ("risk_geometry", "target_policy", "cost_model",
                    "exit_policy", "non_overlap_policy", "baseline_comparisons",
                    "sample_size_requirements", "one_edit_allowance",
                    "next_gate_after_spec"):
        if not record.get(section):
            failures.append("section_missing_%s" % section)
    rg = record.get("risk_geometry") or {}
    if rg.get("atr_length") != ATR_LENGTH:
        failures.append("atr_length_tampered")
    if rg.get("stop_atr_multiplier") != STOP_ATR_MULTIPLIER:
        failures.append("stop_multiplier_tampered")
    tp = record.get("target_policy") or {}
    if list(tp.get("variants") or []) != list(TARGET_VARIANTS):
        failures.append("target_variants_tampered")
    cm = record.get("cost_model") or {}
    if cm.get("all_in_round_trip_bps") != ALL_IN_ROUND_TRIP_BPS:
        failures.append("cost_model_tampered")
    if (cm.get("fee_round_trip_bps", 0) + cm.get("slippage_round_trip_bps", 0)
            != ALL_IN_ROUND_TRIP_BPS):
        failures.append("cost_components_do_not_sum")
    if record.get("target_distance_floor_bps") != TARGET_DISTANCE_FLOOR_BPS:
        failures.append("risk_floor_tampered")
    if record.get("max_hold_bars") != MAX_HOLD_BARS or MAX_HOLD_BARS > 2:
        failures.append("max_hold_tampered")
    ep = record.get("exit_policy") or {}
    if "STOP FIRST" not in ep.get("same_bar_straddle", ""):
        failures.append("straddle_not_conservative")

    # 8 non-overlap.
    nop = record.get("non_overlap_policy") or {}
    if nop.get("rule") != "per_asset_resolved_exit_reduce_or_keep_only_never_add":
        failures.append("non_overlap_tampered")

    # 9 BOTH baseline gates required.
    bc = record.get("baseline_comparisons") or {}
    if not (bc.get("matched_buy_and_hold") and bc.get("matched_random_entry")):
        failures.append("baseline_comparisons_incomplete")
    if bc.get("both_required") is not True:
        failures.append("baselines_not_both_required")
    if bc.get("failing_either_is_structural_rejection") is not True:
        failures.append("baseline_failure_not_structural")

    # 10 early battery (incl. the structural sample-size gate FIRST + horizon cap)
    gates = record.get("early_structural_rejection_gates") or []
    for chk in EARLY_STRUCTURAL_REJECTION_GATES:
        if chk not in gates:
            failures.append("early_gate_missing_%s" % chk)
    if "structural_labels_sample_size_gate_required_first" not in gates:
        failures.append("sample_size_gate_not_first")
    if record.get("max_horizon_exit_share") != MAX_HORIZON_EXIT_SHARE:
        failures.append("horizon_cap_tampered")
    ss = record.get("sample_size_requirements") or {}
    if not (ss.get("min_accepted_per_asset") and ss.get("min_accepted_per_regime")):
        failures.append("sample_size_cross_asset_cross_regime_missing")
    if ss.get("forward_oos_window_must_be_populated") is not True:
        failures.append("forward_oos_population_requirement_missing")
    if ss.get("below_minimum_is_structural_rejection") is not True:
        failures.append("sample_size_below_min_not_structural")
    aog = record.get("anti_overfit_generalization_rules") or {}
    if aog.get("structural_labels_sample_size_gate_enforced_before_replay") is not True:
        failures.append("sample_size_gate_not_before_replay")
    if aog.get("battery_runs_before_robustness_and_before_promotion") is not True:
        failures.append("battery_not_before_promotion")
    if aog.get("failing_any_battery_check_is_structural_rejection") is not True:
        failures.append("battery_failure_not_structural_rejection")
    if aog.get("must_beat_buy_and_hold_and_random_entry") is not True:
        failures.append("must_beat_baselines_not_required")
    if aog.get("target_capture_must_dominate_horizon_capped") is not True:
        failures.append("target_capture_dominance_not_required")
    if aog.get("regime_symmetry_required_not_long_drift") is not True:
        failures.append("regime_symmetry_not_required")
    if aog.get("no_weekday_or_calendar_trigger") is not True:
        failures.append("calendar_trigger_not_forbidden")
    if aog.get("threshold_not_fit_to_manufacture_samples") is not True:
        failures.append("threshold_fitting_not_forbidden")

    # one-edit allowance.
    oe = record.get("one_edit_allowance") or {}
    if oe.get("exactly_one_documented_parameter_edit_permitted") is not True:
        failures.append("one_edit_allowance_tampered")
    if oe.get("second_edit_is_structural_rejection") is not True:
        failures.append("second_edit_not_rejected")
    if oe.get("never_to_rescue_after_seeing_forward_oos") is not True:
        failures.append("post_oos_rescue_not_forbidden")
    if oe.get("never_to_manufacture_samples") is not True:
        failures.append("manufacture_samples_not_forbidden")

    # next gate.
    if record.get("next_required_action") != NEXT_REQUIRED_ACTION:
        failures.append("next_gate_tampered")

    # Spec-only posture + locks.
    if record.get("is_spec_only") is not True:
        failures.append("not_spec_only")
    if record.get("relies_on_long_drift_or_bull_carry") is not False:
        failures.append("long_drift_reliance_flag_tampered")
    locks = record.get("scope_locks") or {}
    for key in ("no_detector", "no_labels", "no_replay", "no_data_fetch",
                "no_paper_trading", "no_live_trading", "no_portfolio_compute",
                "no_calendar_trigger", "no_weekday_trigger",
                "no_long_drift_or_bull_carry_reliance",
                "no_threshold_fit_to_manufacture_samples",
                "no_paper_live_readiness_claim"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for key in ("detector_gate_locked", "labels_gate_locked",
                "replay_gate_locked", "data_fetch_gate_locked",
                "paper_trading_gate_locked", "live_gate_locked",
                "human_review_required"):
        if record.get(key) is not True:
            failures.append("gate_flag_tampered_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
