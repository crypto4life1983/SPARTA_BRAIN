"""SPARTA Candidate #11 candidate specification: cross_asset_dispersion_reversion_v1.

SPEC ONLY. RESEARCH ONLY. This contract advances Candidate #11 from the family
proposal to a strict, pre-registered candidate specification. It is pure and
in-memory: NO detector, NO labels, NO replay, NO robustness, NO generalization
run, NO data fetch, NO trading, NO portfolio compute, NO downstream gate unlock.
It only fixes the hypothesis geometry + the research protocol for human review.

Chain gate: build_candidate_11_spec() requires build_candidate_11_family_proposal()
to return CANDIDATE_11_FAMILY_PROPOSAL_READY.

THE C10 LESSON (enforced here as a structural requirement):
  C10 was undifferentiated long-drift dressed as a calendar edge and only failed
  the generalization gate at the very end. C11 therefore (a) uses a RELATIVE /
  cross-sectional edge (regime-symmetric by construction, never a calendar /
  weekday trigger, never a single-asset bet) and (b) MAKES the early
  generalization battery -- cross-weekday neutrality, cross-asset (multiple
  laggards), forward-OOS continuation, and cross-regime (bull/bear/chop)
  stability -- a MANDATORY gate at the labels/replay stage, BEFORE any
  robustness or promotion. Failing any early-generalization check is a
  STRUCTURAL REJECTION, not a warning.
"""
from __future__ import annotations

from typing import Any

from sparta_commander.cross_asset_dispersion_reversion_v1_family_proposal_contract import (  # noqa: E501
    CANDIDATE_FAMILY,
    CANDIDATE_ID,
    REJECTED_FAMILIES_C1_TO_C10,
    VERDICT_C11P_READY,
    build_candidate_11_family_proposal,
)

C11S_SCHEMA_VERSION = 1
C11S_MODE = "RESEARCH_ONLY"
CANDIDATE_NUMBER = 11

VERDICT_C11S_READY = "CANDIDATE_11_SPEC_READY"
VERDICT_C11S_BLOCKED = "CANDIDATE_11_SPEC_BLOCKED"
NEXT_REQUIRED_ACTION = "HUMAN_DECISION_C11_ADVANCE_TO_DETECTOR_SPEC_OR_REJECT"

HEAD_AT_C11_PROPOSAL = "476425b171adeab8cd9adc72e6c67bf160ecc8a8"

# --- 1. symbol universe (cross-asset by construction; never single-asset) ---
SYMBOL_UNIVERSE = ("BTCUSD", "ETHUSD", "SOLUSD")
MIN_ASSETS_REQUIRED = 3
MARKET_TYPE = "spot"
DIRECTION = "long_only"
DIRECTION_NOTE = ("long-only research labels on the relative laggard; never a "
                  "short/borrow leg, never a trading capability")

# --- 2. timeframe -----------------------------------------------------------
TIMEFRAME = "1d"
SESSION = "24/7 crypto; weekday-agnostic by construction (no weekday/calendar "
SESSION += "trigger permitted)"

# --- 3. entry concept (RELATIVE / cross-sectional; pre-registered) ----------
DISPERSION_LOOKBACK_BARS = 5            # k-day return for the cross-sectional z
DISPERSION_Z_ENTRY_THRESHOLD = -1.0     # enter the laggard when z <= -1.0
BASKET_REGIME_FILTER = (
    "Enter ONLY when the basket is not in a confirmed downtrend: basket-median "
    "close must be at or above its own SMA(50). The signal is the asset's "
    "k-day return cross-sectional z-score vs the basket; the relative LAGGARD "
    "(most negative z at/below the threshold) is entered long at the daily "
    "close. Weekday is irrelevant.")
ENTRY_CONCEPT = {
    "trigger": "cross_sectional_dispersion_reversion_of_the_relative_laggard",
    "lookback_return_bars": DISPERSION_LOOKBACK_BARS,
    "z_score_entry_threshold": DISPERSION_Z_ENTRY_THRESHOLD,
    "z_score_basis": "k_day_return_z_score_vs_basket_of_majors",
    "regime_filter": BASKET_REGIME_FILTER,
    "entry_price": "close_of_the_signal_bar (no intrabar entry)",
    "one_position_per_asset": True,
    "weekday_or_calendar_trigger": False,
    "single_asset_or_single_weekday": False,
}

# --- 4. stop / risk geometry (pre-registered; never tightened post-hoc) -----
ATR_LENGTH = 14
STRUCTURE_STOP_ATR_MULTIPLIER = 1.5
RISK_GEOMETRY = {
    "atr_length": ATR_LENGTH,
    "structure_stop": "stop_price = entry_price - 1.5 * ATR(14) at the entry "
                      "bar; stop_distance = entry - stop; INVALID if "
                      "stop_distance <= 0 or stop not below entry; never "
                      "tightened post-hoc",
    "risk_unit_R": "stop_distance",
    "sizing": "equal-weight / fixed-fraction research sizing only; NO leverage; "
              "NO shorting; NO portfolio compute",
}

# --- 5. target variants (pre-registered; no new variants after label freeze) -
TARGET_VARIANTS = ("2r", "3r", "4r")
TARGET_POLICY = {
    "variants": list(TARGET_VARIANTS),
    "target_price_formula": "entry_price + R_multiple * stop_distance",
    "no_new_variants_after_label_freeze": True,
}
TARGET_DISTANCE_FLOOR_BPS = 81.0        # gross target-distance floor

# --- 6. cost model (fee + slippage honest; inherits C10 discipline) ---------
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
}

# --- 7. sample-size requirements (cross-asset + cross-regime coverage) -------
SAMPLE_SIZE_REQUIREMENTS = {
    "min_accepted_total": 100,
    "min_accepted_per_asset": 20,
    "min_accepted_per_regime": 20,          # bull / bear / chop
    "enforced_at": "labels_review_gate",
    "below_minimum_is_structural_rejection": True,
    "does_not_consume_edit_token": True,
}

# --- 8. invalidation / rejection rules --------------------------------------
INVALIDATION_REJECTION_RULES = (
    "Invalid stop geometry (stop_distance <= 0 or stop not below entry) -> "
    "setup rejected.",
    "No variant clears the 81 bps gross target-distance floor -> setup "
    "rejected.",
    "Basket in a confirmed downtrend (basket-median below SMA(50)) -> no entry.",
    "Asset z-score not at/below the pre-registered threshold -> no entry.",
    "Insufficient sample (total/per-asset/per-regime below minimums) at the "
    "labels-review gate -> structural rejection.",
    "Any dependence on a specific weekday or calendar date detected -> "
    "structural rejection (the edge must be weekday-neutral).",
    "Edge explained by generic bullish long-drift (fails regime-symmetry) -> "
    "structural rejection.",
    "Edge does not continue in forward-OOS -> structural rejection.",
    "Any parameter fit, weekday re-selection, or best-cell selection -> "
    "structural rejection.",
)

# --- 9. anti-overfit / generalization rules (the C10 lesson, ENFORCED) ------
EARLY_GENERALIZATION_BATTERY = (
    "cross_weekday_neutrality_required_early",
    "cross_asset_multiple_laggards_required_early",
    "forward_oos_continuation_required_early",
    "cross_regime_bull_bear_chop_stability_required_early",
)
ANTI_OVERFIT_GENERALIZATION_RULES = {
    "early_generalization_battery": list(EARLY_GENERALIZATION_BATTERY),
    "battery_runs_before_robustness_and_before_promotion": True,
    "failing_any_battery_check_is_structural_rejection": True,
    "pre_registered_grid_only_no_in_sample_fitting": True,
    "no_weekday_or_calendar_trigger": True,
    "no_best_cell_selected_as_promotion": True,
    "regime_symmetry_required_not_long_drift": True,
    "is_oos_sealed_before_any_run": True,
    "original_rejected_geometry_never_reused_unchanged": True,
}

# --- 10. next gate after spec -----------------------------------------------
NEXT_GATE_AFTER_SPEC = {
    "action": NEXT_REQUIRED_ACTION,
    "description": "Human decides whether to advance C11 to the detector spec / "
                   "dry-run gate (still no labels, no replay, no data fetch) or "
                   "reject. The early generalization battery is mandatory at the "
                   "labels/replay stage that follows.",
}

C11S_LABEL = (
    "SPARTA Candidate #11 Candidate Spec (READ-ONLY, RESEARCH ONLY). "
    "cross_asset_dispersion_reversion: long the relative LAGGARD on extreme "
    "cross-sectional dispersion (RELATIVE, regime-symmetric; NOT calendar, NOT "
    "long-drift, NOT single-asset/single-weekday). MATERIALLY DIFFERENT FROM "
    "C1-C10. SPEC ONLY -- NO DETECTOR, NO LABELS, NO REPLAY, NO DATA FETCH, NO "
    "TRADING. EARLY GENERALIZATION BATTERY IS MANDATORY BEFORE ANY PROMOTION."
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
    "fits_parameters", "uses_weekday_or_calendar_trigger", "is_single_asset",
    "is_a_rescue_attempt", "authorizes_paper_execution", "authorizes_micro_live",
    "authorizes_live_trading", "promotes_gate", "unlocks_downstream_gate",
    "claims_profitability", "claims_edge", "claims_paper_or_live_readiness",
    "executes", "writes_files",
)


def get_candidate_11_spec_label() -> str:
    return C11S_LABEL


def get_candidate_11_spec_next_action() -> str:
    return NEXT_REQUIRED_ACTION


def build_candidate_11_spec(repo_root: Any = ".",
                            tracked_paths: list | None = None
                            ) -> dict[str, Any]:
    """Assemble the strict Candidate #11 candidate spec. Chain-gated on the
    READY family proposal. Pure; no I/O; spec only."""
    record: dict[str, Any] = {
        "schema_version": C11S_SCHEMA_VERSION,
        "label": C11S_LABEL, "mode": C11S_MODE,
        "lane": "crypto_d1_auto_research",
        "candidate_number": CANDIDATE_NUMBER,
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "verdict": None, "blockers": [],
        "head_at_c11_proposal": HEAD_AT_C11_PROPOSAL,
        # 1-10 spec sections
        "symbol_universe": list(SYMBOL_UNIVERSE),
        "min_assets_required": MIN_ASSETS_REQUIRED,
        "market_type": MARKET_TYPE,
        "direction": DIRECTION, "direction_note": DIRECTION_NOTE,
        "timeframe": TIMEFRAME, "session": SESSION,
        "entry_concept": dict(ENTRY_CONCEPT),
        "risk_geometry": dict(RISK_GEOMETRY),
        "target_policy": dict(TARGET_POLICY),
        "target_distance_floor_bps": TARGET_DISTANCE_FLOOR_BPS,
        "cost_model": dict(COST_MODEL),
        "sample_size_requirements": dict(SAMPLE_SIZE_REQUIREMENTS),
        "invalidation_rejection_rules": list(INVALIDATION_REJECTION_RULES),
        "anti_overfit_generalization_rules":
            dict(ANTI_OVERFIT_GENERALIZATION_RULES),
        "early_generalization_battery": list(EARLY_GENERALIZATION_BATTERY),
        "next_gate_after_spec": dict(NEXT_GATE_AFTER_SPEC),
        "rejected_families_c1_to_c10": list(REJECTED_FAMILIES_C1_TO_C10),
        # posture
        "is_spec_only": True,
        "is_materially_new_family": True,
        "is_a_rescue_attempt": False,
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
        "no_portfolio_compute": True, "no_parameter_fitting": True,
        "no_weekday_trigger": True, "no_calendar_trigger": True,
        "no_best_cell_selected_as_promotion": True,
        "no_rescue_of_rejected_geometry": True, "no_profitability_claim": True,
        "no_paper_live_readiness_claim": True, "no_downstream_gate_unlock": True,
    }

    # Materially new + must not be a rejected family.
    if CANDIDATE_FAMILY in REJECTED_FAMILIES_C1_TO_C10:
        record["verdict"] = VERDICT_C11S_BLOCKED
        record["blockers"].append("spec_family_is_a_rejected_family")
        return record

    proposal = build_candidate_11_family_proposal(repo_root, tracked_paths or [])
    record["proposal_verdict"] = proposal.get("verdict")
    if proposal.get("verdict") != VERDICT_C11P_READY:
        record["verdict"] = VERDICT_C11S_BLOCKED
        record["blockers"].append("proposal_not_ready")
        return record

    record["verdict"] = VERDICT_C11S_READY
    return record


def validate_candidate_11_spec(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. READY only when the spec is materially new, pins
    all ten sections, enforces the early generalization battery + no
    calendar/weekday/single-asset trap, and locks all execution gates."""
    failures: list = []
    if record.get("verdict") != VERDICT_C11S_READY:
        failures.append("verdict_not_ready")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("mode") != C11S_MODE:
        failures.append("mode_not_research_only")
    if record.get("candidate_number") != 11:
        failures.append("candidate_number_tampered")
    if record.get("proposal_verdict") != VERDICT_C11P_READY:
        failures.append("proposal_verdict_tampered")

    # Materially new.
    if record.get("is_materially_new_family") is not True:
        failures.append("not_marked_materially_new")
    if record.get("candidate_family") in (
            record.get("rejected_families_c1_to_c10") or []):
        failures.append("spec_family_is_rejected_family")

    # 1-10 sections present + non-empty.
    su = record.get("symbol_universe") or []
    if len(su) < MIN_ASSETS_REQUIRED:
        failures.append("symbol_universe_too_small_single_asset_trap")
    if record.get("timeframe") != "1d":
        failures.append("timeframe_tampered")
    ec = record.get("entry_concept") or {}
    if ec.get("weekday_or_calendar_trigger") is not False:
        failures.append("entry_uses_weekday_or_calendar_trigger")
    if ec.get("single_asset_or_single_weekday") is not False:
        failures.append("entry_is_single_asset_or_single_weekday")
    for section in ("risk_geometry", "target_policy", "cost_model",
                    "sample_size_requirements", "next_gate_after_spec"):
        if not record.get(section):
            failures.append("section_missing_%s" % section)
    if not record.get("invalidation_rejection_rules"):
        failures.append("invalidation_rules_missing")
    cm = record.get("cost_model") or {}
    if cm.get("all_in_round_trip_bps") != ALL_IN_ROUND_TRIP_BPS:
        failures.append("cost_model_tampered")
    ss = record.get("sample_size_requirements") or {}
    if not (ss.get("min_accepted_per_asset") and ss.get("min_accepted_per_regime")):
        failures.append("sample_size_cross_asset_cross_regime_missing")

    # 9. early-generalization battery enforced.
    aog = record.get("anti_overfit_generalization_rules") or {}
    if aog.get("battery_runs_before_robustness_and_before_promotion") is not True:
        failures.append("early_generalization_not_before_promotion")
    if aog.get("failing_any_battery_check_is_structural_rejection") is not True:
        failures.append("battery_failure_not_structural_rejection")
    for chk in EARLY_GENERALIZATION_BATTERY:
        if chk not in (record.get("early_generalization_battery") or []):
            failures.append("battery_check_missing_%s" % chk)
    if aog.get("no_weekday_or_calendar_trigger") is not True:
        failures.append("calendar_trigger_not_forbidden")
    if aog.get("regime_symmetry_required_not_long_drift") is not True:
        failures.append("regime_symmetry_not_required")

    # 10. next gate.
    if record.get("next_required_action") != NEXT_REQUIRED_ACTION:
        failures.append("next_gate_tampered")

    # Spec-only posture + locks.
    if record.get("is_spec_only") is not True:
        failures.append("not_spec_only")
    locks = record.get("scope_locks") or {}
    for key in ("no_detector", "no_labels", "no_replay", "no_data_fetch",
                "no_paper_trading", "no_live_trading", "no_portfolio_compute",
                "no_calendar_trigger", "no_weekday_trigger",
                "no_parameter_fitting", "no_paper_live_readiness_claim"):
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
