"""SPARTA Candidate #13 candidate specification: lead_lag_propagation_continuation_v1.

SPEC ONLY. RESEARCH ONLY. This contract advances Candidate #13 from the family
proposal to a strict, pre-registered candidate specification. It is pure and
in-memory: NO detector, NO labels, NO replay, NO robustness, NO generalization
run, NO data fetch, NO trading, NO portfolio compute, NO downstream gate unlock.
It only fixes the hypothesis geometry + the research protocol for human review.

Chain gate: build_candidate_13_spec() requires build_candidate_13_family_proposal()
to return CANDIDATE_13_FAMILY_PROPOSAL_READY.

THE C10 + C11 + C12 LESSONS (enforced here as structural requirements):
  * C10: no date/weekday trigger; regime symmetry + forward-OOS mandatory early.
  * C11: strong labels are NECESSARY BUT NOT SUFFICIENT; forward-OOS continuation
    AND bull/bear/chop net symmetry are HARD replay gates.
  * C12: the must-beat-RANDOM-ENTRY baseline is the decisive anti-edge filter;
    target capture must dominate horizon exits; the edge must beat buy-and-hold.
  * C13-specific: the cross-asset propagation must ALSO beat a BUY-THE-LEADER
    baseline (same signal bars, leader entry, identical geometry) so the
    demonstrated edge is the DIFFUSION, not generic strength.
"""
from __future__ import annotations

from typing import Any

from sparta_commander.lead_lag_propagation_continuation_v1_family_proposal_contract import (  # noqa: E501
    CANDIDATE_FAMILY,
    CANDIDATE_ID,
    REJECTED_FAMILIES_C1_TO_C12,
    VERDICT_C13P_READY,
    build_candidate_13_family_proposal,
)

C13S_SCHEMA_VERSION = 1
C13S_MODE = "RESEARCH_ONLY"
CANDIDATE_NUMBER = 13

VERDICT_C13S_READY = "CANDIDATE_13_SPEC_READY"
VERDICT_C13S_BLOCKED = "CANDIDATE_13_SPEC_BLOCKED"
NEXT_REQUIRED_ACTION = "HUMAN_DECISION_C13_ADVANCE_TO_DETECTOR_SPEC_OR_REJECT"

HEAD_AT_C13_PROPOSAL = "ae97e896ba2fc924df82e97beafb2ecdbaa4c739"

# --- 1. leader / follower universe (cross-asset; leader != follower) --------
LEADER = "BTCUSD"
FOLLOWERS = ("ETHUSD", "SOLUSD")
SYMBOL_UNIVERSE = ("BTCUSD", "ETHUSD", "SOLUSD")
MIN_FOLLOWERS_REQUIRED = 2
MARKET_TYPE = "spot"
DIRECTION = "long_only"
DIRECTION_NOTE = ("long-only research labels on the follower's catch-up; never a "
                  "short/borrow leg, never a trading capability")
NO_DATA_FETCH = True
SOURCES_FROZEN_ON_DISK = ("data/crypto_d1_spot/raw/BTC_1d.csv",
                          "data/crypto_d1_spot/raw/ETH_1d.csv",
                          "data/crypto_d1_spot/raw/SOL_1d.csv")

# --- 2. timeframe -----------------------------------------------------------
TIMEFRAME = "1d"
SESSION = ("24/7 crypto; weekday-agnostic by construction (no weekday/calendar "
           "trigger permitted)")

# --- 3. leader move + lag condition + entry (pre-registered; deterministic) --
LEADER_RETURN_LOOKBACK_BARS = 1         # the leader's 1-day return
LEADER_Z_LOOKBACK = 90                  # rolling window for the leader z-score
LEADER_Z_ENTRY_THRESHOLD = 1.5          # confirmed large move: z >= +1.5
LAG_MARGIN_FRACTION = 0.5               # follower captured < 50% of leader move
LEADER_MOVE_DEFINITION = (
    "On bar t let r_L = the LEADER (BTC) LEADER_RETURN_LOOKBACK_BARS-day return "
    "and z_L = (r_L - mean) / std of the leader's daily return over the prior "
    "LEADER_Z_LOOKBACK bars. A CONFIRMED leader move requires r_L > 0 AND "
    "z_L >= LEADER_Z_ENTRY_THRESHOLD (a large positive daily move).")
LAG_CONDITION = (
    "The FOLLOWER must have UNDER-participated on the same bar t: the follower's "
    "same-window return r_F < LAG_MARGIN_FRACTION * r_L (it captured less than "
    "half the leader's move), leaving room to catch up. r_F is read on bar t "
    "only; no future bar is used.")
ENTRY_CONCEPT = {
    "leader": LEADER, "followers": list(FOLLOWERS),
    "leader_return_lookback_bars": LEADER_RETURN_LOOKBACK_BARS,
    "leader_z_lookback": LEADER_Z_LOOKBACK,
    "leader_z_entry_threshold": LEADER_Z_ENTRY_THRESHOLD,
    "lag_margin_fraction": LAG_MARGIN_FRACTION,
    "confirmed_leader_move": "r_L > 0 and z_L >= 1.5",
    "lag_condition": "r_F < 0.5 * r_L",
    "entry_price": "close of the FOLLOWER on the signal bar t (no intrabar entry)",
    "trigger_asset_differs_from_traded_asset": True,
    "one_position_per_follower": True,
    "weekday_or_calendar_trigger": False,
    "single_asset_or_single_weekday": False,
    "relies_on_long_drift_or_bull_carry": False,
}

# --- 4. stop / risk geometry (ATR(14)-validated; never tightened post-hoc) --
ATR_LENGTH = 14
STOP_ATR_MULTIPLIER = 1.0
RISK_GEOMETRY = {
    "atr_length": ATR_LENGTH,
    "structure_stop": ("stop_price = follower_close[t] - "
                       "STOP_ATR_MULTIPLIER * ATR(14) on the FOLLOWER at bar t; "
                       "stop_distance = entry_close - stop_price; INVALID if "
                       "stop_distance <= 0 or stop not below entry; never "
                       "tightened post-hoc"),
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
TARGET_DISTANCE_FLOOR_BPS = 81.0        # gross target-distance floor vs 37 bps cost

# --- 6. cost model (fee + slippage honest; inherits C10/C11/C12 discipline) -
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
MAX_HOLD_BARS = 2                       # human-fixed in 1-2 range; disclosed
HORIZON_SOURCE = "human_fixed_short_hold_1_to_2_bars_spec_predeclared_max_2"
EXIT_POLICY = {
    "max_hold_bars": MAX_HOLD_BARS,
    "scan_window": "bars [entry_index+1 .. entry_index+MAX_HOLD_BARS] on the "
                   "FOLLOWER (next-bar onward; entry bar not re-scanned)",
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
    "rule": "per_follower_resolved_exit_reduce_or_keep_only_never_add",
    "detail": ("one position per follower: drop a later setup on the SAME "
               "follower whose entry_index <= that follower's active resolved "
               "exit index; different followers may overlap; never add"),
}

# --- 9. baseline comparisons (the anti-carry / anti-drift / anti-strength) ---
BASELINE_COMPARISONS = {
    "matched_buy_and_hold": (
        "long the SAME follower over the same entry windows, passive hold to the "
        "+MAX_HOLD close, same cost; the strategy MUST EXCEED it"),
    "matched_random_entry": (
        "the same number of entries per follower on the same date span drawn "
        "with a FIXED DETERMINISTIC SEED, identical stop/target/horizon geometry "
        "+ cost; the strategy MUST EXCEED it (the leader-move SIGNAL must add "
        "timing value over random)"),
    "buy_the_leader": (
        "on each C13 signal bar, instead enter the LEADER (BTC) long with the "
        "IDENTICAL geometry (leader entry close, leader ATR stop, same R + "
        "horizon + cost); the FOLLOWER strategy MUST EXCEED this -- else the "
        "cross-asset diffusion is just generic strength / buying the leader"),
    "all_three_required": True,
    "failing_any_is_structural_rejection": True,
}

# --- 10. early structural rejection gates (battery; before robustness) ------
MAX_HORIZON_EXIT_SHARE = 0.50           # target capture MUST dominate
EARLY_STRUCTURAL_REJECTION_GATES = (
    "forward_oos_continuation_required_early",
    "cross_regime_bull_bear_chop_symmetry_required_early",
    "cross_asset_multiple_followers_required_early",
    "beats_matched_buy_and_hold_baseline_required_early",
    "beats_matched_random_entry_baseline_required_early",
    "beats_buy_the_leader_baseline_required_early",
    "target_capture_dominates_horizon_exit_share_capped_required_early",
    "no_weekday_or_calendar_dependence_required_early",
    "sample_size_minimums_required_early",
)
SAMPLE_SIZE_REQUIREMENTS = {
    "min_accepted_total": 100,
    "min_accepted_per_follower": 20,
    "min_accepted_per_regime": 20,          # bull / bear / chop
    "enforced_at": "labels_review_and_replay_gate",
    "below_minimum_is_structural_rejection": True,
}

# --- invalidation / rejection rules -----------------------------------------
INVALIDATION_REJECTION_RULES = (
    "Leader move not confirmed (r_L <= 0 or z_L < 1.5) -> no entry.",
    "Follower did not under-participate (r_F >= 0.5 * r_L) -> no entry "
    "(no lag to catch up).",
    "Invalid stop geometry (stop_distance <= 0 or stop not below entry) -> "
    "setup rejected.",
    "No target variant clears the 81 bps gross target-distance floor -> setup "
    "rejected.",
    "Result horizon/drift dominated (horizon-exit share > 50%) -> STRUCTURAL "
    "rejection.",
    "Does not beat matched buy-and-hold OR matched random-entry OR the "
    "buy-the-leader baseline -> STRUCTURAL rejection.",
    "Not regime-symmetric across bull/bear/chop -> STRUCTURAL rejection.",
    "Does not continue in forward-OOS -> STRUCTURAL rejection.",
    "Single-follower dependence or any weekday/calendar dependence -> STRUCTURAL "
    "rejection.",
    "Sample below total/per-follower/per-regime minimums at the labels/replay "
    "gate -> STRUCTURAL rejection.",
    "Any parameter fit beyond the single documented one-edit allowance, or any "
    "post-OOS rescue edit -> STRUCTURAL rejection.",
)

# --- one-edit allowance rules -----------------------------------------------
ONE_EDIT_ALLOWANCE = {
    "exactly_one_documented_parameter_edit_permitted": True,
    "editable_scope": ("a single pre-registered parameter -- exactly ONE of "
                       "{LEADER_Z_ENTRY_THRESHOLD, LAG_MARGIN_FRACTION, "
                       "STOP_ATR_MULTIPLIER, MAX_HOLD_BARS} -- may be changed "
                       "once"),
    "must_be_documented_before_rerun": True,
    "must_revalidate_full_early_battery": True,
    "never_to_rescue_after_seeing_forward_oos": True,
    "never_reused_more_than_once": True,
    "does_not_unlock_any_downstream_gate": True,
    "second_edit_is_structural_rejection": True,
}

# --- anti-overfit / generalization rules (C10+C11+C12 lessons, ENFORCED) ----
ANTI_OVERFIT_GENERALIZATION_RULES = {
    "early_battery": list(EARLY_STRUCTURAL_REJECTION_GATES),
    "battery_runs_before_robustness_and_before_promotion": True,
    "failing_any_battery_check_is_structural_rejection": True,
    "pre_registered_deterministic_parameters_no_grid_fitting": True,
    "no_weekday_or_calendar_trigger": True,
    "no_best_cell_selected_as_promotion": True,
    "regime_symmetry_required_not_long_drift": True,
    "must_beat_buy_and_hold_and_random_entry": True,
    "must_beat_buy_the_leader": True,
    "target_capture_must_dominate_horizon_capped": True,
    "max_horizon_exit_share": MAX_HORIZON_EXIT_SHARE,
    "is_oos_sealed_before_any_run": True,
    "original_rejected_geometry_never_reused_unchanged": True,
}

# --- next gate after spec ---------------------------------------------------
NEXT_GATE_AFTER_SPEC = {
    "action": NEXT_REQUIRED_ACTION,
    "description": ("Human decides whether to advance C13 to the detector spec / "
                    "dry-run gate (still no labels, no replay, no data fetch) or "
                    "reject. The early generalization + anti-drift battery "
                    "(incl. the buy-the-leader gate) is mandatory at the "
                    "labels/replay stage that follows."),
}

C13S_LABEL = (
    "SPARTA Candidate #13 Candidate Spec (READ-ONLY, RESEARCH ONLY). "
    "lead_lag_propagation_continuation: long a FOLLOWER (ETH/SOL) when the LEADER "
    "(BTC) posts a confirmed daily move (z>=1.5) the follower under-participated "
    "in (r_F < 0.5*r_L); ATR(14) stop; 1R/1.5R/2R; <=2-bar hold; 37 bps. "
    "MATERIALLY DIFFERENT FROM C1-C12. SPEC ONLY -- NO DETECTOR, NO LABELS, NO "
    "REPLAY, NO DATA FETCH, NO TRADING. FORWARD-OOS + REGIME SYMMETRY + "
    "MUST-BEAT-BUY&HOLD + MUST-BEAT-RANDOM + MUST-BEAT-LEADER + "
    "TARGET-CAPTURE-DOMINANCE ARE MANDATORY EARLY GATES."
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
    "is_a_rescue_attempt", "authorizes_paper_execution", "authorizes_micro_live",
    "authorizes_live_trading", "promotes_gate", "unlocks_downstream_gate",
    "claims_profitability", "claims_edge", "claims_paper_or_live_readiness",
    "executes", "writes_files",
)


def get_candidate_13_spec_label() -> str:
    return C13S_LABEL


def get_candidate_13_spec_next_action() -> str:
    return NEXT_REQUIRED_ACTION


def build_candidate_13_spec(repo_root: Any = ".",
                            tracked_paths: list | None = None
                            ) -> dict[str, Any]:
    """Assemble the strict Candidate #13 candidate spec. Chain-gated on the
    READY family proposal. Pure; no I/O; spec only."""
    record: dict[str, Any] = {
        "schema_version": C13S_SCHEMA_VERSION,
        "label": C13S_LABEL, "mode": C13S_MODE,
        "lane": "crypto_d1_auto_research",
        "candidate_number": CANDIDATE_NUMBER,
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "verdict": None, "blockers": [],
        "head_at_c13_proposal": HEAD_AT_C13_PROPOSAL,
        # 1-10 spec sections
        "leader": LEADER, "followers": list(FOLLOWERS),
        "symbol_universe": list(SYMBOL_UNIVERSE),
        "min_followers_required": MIN_FOLLOWERS_REQUIRED,
        "market_type": MARKET_TYPE,
        "direction": DIRECTION, "direction_note": DIRECTION_NOTE,
        "no_data_fetch": NO_DATA_FETCH,
        "sources_frozen_on_disk": list(SOURCES_FROZEN_ON_DISK),
        "timeframe": TIMEFRAME, "session": SESSION,
        "leader_move_definition": LEADER_MOVE_DEFINITION,
        "lag_condition_definition": LAG_CONDITION,
        "leader_return_lookback_bars": LEADER_RETURN_LOOKBACK_BARS,
        "leader_z_lookback": LEADER_Z_LOOKBACK,
        "leader_z_entry_threshold": LEADER_Z_ENTRY_THRESHOLD,
        "lag_margin_fraction": LAG_MARGIN_FRACTION,
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
        "rejected_families_c1_to_c12": list(REJECTED_FAMILIES_C1_TO_C12),
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
        "no_weekday_trigger": True, "no_calendar_trigger": True,
        "no_best_cell_selected_as_promotion": True,
        "no_rescue_of_rejected_geometry": True,
        "no_long_drift_or_bull_carry_reliance": True,
        "no_profitability_claim": True,
        "no_paper_live_readiness_claim": True, "no_downstream_gate_unlock": True,
    }

    # Materially new + must not be a rejected family.
    if CANDIDATE_FAMILY in REJECTED_FAMILIES_C1_TO_C12:
        record["verdict"] = VERDICT_C13S_BLOCKED
        record["blockers"].append("spec_family_is_a_rejected_family")
        return record

    proposal = build_candidate_13_family_proposal(repo_root, tracked_paths or [])
    record["proposal_verdict"] = proposal.get("verdict")
    if proposal.get("verdict") != VERDICT_C13P_READY:
        record["verdict"] = VERDICT_C13S_BLOCKED
        record["blockers"].append("proposal_not_ready")
        return record

    record["verdict"] = VERDICT_C13S_READY
    return record


def validate_candidate_13_spec(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. READY only when the spec is materially new, pins
    all sections (leader!=follower, z-threshold, lag condition, ATR stop, 81 bps
    floor over 37 bps cost, 1R/1.5R/2R, <=2-bar hold, per-follower non-overlap,
    ALL THREE baseline gates incl. buy-the-leader, the full early battery + the
    horizon cap, the one-edit allowance), enforces no calendar/weekday + no
    long-drift reliance, and locks all execution gates."""
    failures: list = []
    if record.get("verdict") != VERDICT_C13S_READY:
        failures.append("verdict_not_ready")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("mode") != C13S_MODE:
        failures.append("mode_not_research_only")
    if record.get("candidate_number") != 13:
        failures.append("candidate_number_tampered")
    if record.get("proposal_verdict") != VERDICT_C13P_READY:
        failures.append("proposal_verdict_tampered")

    # Materially new.
    if record.get("is_materially_new_family") is not True:
        failures.append("not_marked_materially_new")
    if record.get("candidate_family") in (
            record.get("rejected_families_c1_to_c12") or []):
        failures.append("spec_family_is_rejected_family")

    # 1-2 universe + leader!=follower + timeframe + no fetch.
    fol = record.get("followers") or []
    if len(fol) < MIN_FOLLOWERS_REQUIRED:
        failures.append("too_few_followers_single_asset_trap")
    if record.get("leader") in fol:
        failures.append("leader_is_a_follower_not_cross_asset")
    if record.get("timeframe") != "1d":
        failures.append("timeframe_tampered")
    if record.get("market_type") != "spot":
        failures.append("market_type_tampered")
    if record.get("no_data_fetch") is not True:
        failures.append("no_data_fetch_flag_tampered")

    # 3 leader move + lag + entry.
    if not record.get("leader_move_definition"):
        failures.append("leader_move_definition_missing")
    if not record.get("lag_condition_definition"):
        failures.append("lag_condition_missing")
    if record.get("leader_z_entry_threshold") != LEADER_Z_ENTRY_THRESHOLD:
        failures.append("z_threshold_tampered")
    if record.get("lag_margin_fraction") != LAG_MARGIN_FRACTION:
        failures.append("lag_margin_tampered")
    ec = record.get("entry_concept") or {}
    if ec.get("trigger_asset_differs_from_traded_asset") is not True:
        failures.append("trigger_not_cross_asset")
    if ec.get("weekday_or_calendar_trigger") is not False:
        failures.append("entry_uses_weekday_or_calendar_trigger")
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
    if nop.get("rule") != "per_follower_resolved_exit_reduce_or_keep_only_never_add":
        failures.append("non_overlap_tampered")

    # 9 ALL THREE baseline gates required (incl. buy-the-leader).
    bc = record.get("baseline_comparisons") or {}
    if not (bc.get("matched_buy_and_hold") and bc.get("matched_random_entry")
            and bc.get("buy_the_leader")):
        failures.append("baseline_comparisons_incomplete")
    if bc.get("all_three_required") is not True:
        failures.append("baselines_not_all_three_required")
    if bc.get("failing_any_is_structural_rejection") is not True:
        failures.append("baseline_failure_not_structural")

    # 10 early battery (incl. buy-the-leader + horizon cap) enforced.
    gates = record.get("early_structural_rejection_gates") or []
    for chk in EARLY_STRUCTURAL_REJECTION_GATES:
        if chk not in gates:
            failures.append("early_gate_missing_%s" % chk)
    if record.get("max_horizon_exit_share") != MAX_HORIZON_EXIT_SHARE:
        failures.append("horizon_cap_tampered")
    ss = record.get("sample_size_requirements") or {}
    if not (ss.get("min_accepted_per_follower")
            and ss.get("min_accepted_per_regime")):
        failures.append("sample_size_cross_asset_cross_regime_missing")
    aog = record.get("anti_overfit_generalization_rules") or {}
    if aog.get("battery_runs_before_robustness_and_before_promotion") is not True:
        failures.append("battery_not_before_promotion")
    if aog.get("failing_any_battery_check_is_structural_rejection") is not True:
        failures.append("battery_failure_not_structural_rejection")
    if aog.get("must_beat_buy_and_hold_and_random_entry") is not True:
        failures.append("must_beat_baselines_not_required")
    if aog.get("must_beat_buy_the_leader") is not True:
        failures.append("must_beat_leader_not_required")
    if aog.get("target_capture_must_dominate_horizon_capped") is not True:
        failures.append("target_capture_dominance_not_required")
    if aog.get("regime_symmetry_required_not_long_drift") is not True:
        failures.append("regime_symmetry_not_required")
    if aog.get("no_weekday_or_calendar_trigger") is not True:
        failures.append("calendar_trigger_not_forbidden")

    # one-edit allowance.
    oe = record.get("one_edit_allowance") or {}
    if oe.get("exactly_one_documented_parameter_edit_permitted") is not True:
        failures.append("one_edit_allowance_tampered")
    if oe.get("second_edit_is_structural_rejection") is not True:
        failures.append("second_edit_not_rejected")
    if oe.get("never_to_rescue_after_seeing_forward_oos") is not True:
        failures.append("post_oos_rescue_not_forbidden")

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
