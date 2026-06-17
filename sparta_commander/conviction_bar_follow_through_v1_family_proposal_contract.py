"""SPARTA Candidate #14 family proposal: conviction_bar_follow_through_v1.

PROPOSAL ONLY. RESEARCH ONLY. This contract proposes a NEW strategy family for
the Strategy Factory after Candidates #10, #11, #12 AND #13 were all closed
REJECTED_KEPT_ON_RECORD. It is pure and in-memory: NO detector, NO labels, NO
replay, NO robustness, NO generalization run, NO data fetch, NO trading, NO
portfolio compute, NO downstream gate unlock. It only proposes a hypothesis +
differentiation + research plan for human review.

Chain gate: build_candidate_14_family_proposal() requires
build_c13_rejection_record() to return REJECTED_KEPT_ON_RECORD -- C14 may only
open once C13 is formally closed on the ledger.

THE C10 + C11 + C12 + C13 LESSONS (applied as HARD rules here):
  * C10: undifferentiated bullish LONG-DRIFT dressed as a calendar edge -> no
    date/weekday trigger; regime symmetry + forward-OOS mandatory early.
  * C11: strong labels yet FAILED replay on forward-OOS + regime symmetry ->
    labels are NECESSARY BUT NOT SUFFICIENT; both are HARD replay gates.
  * C12: the must-beat-RANDOM-ENTRY baseline is the decisive anti-edge filter;
    target capture must dominate horizon exits; must beat buy-and-hold.
  * C13: a too-RARE trigger (41 labels, ETH 18, all regimes < 20, zero
    forward-OOS) is a STRUCTURAL REJECTION at the labels stage, BEFORE replay ->
    the labels sample-size gate (>=100 total / >=20 per asset / >=20 per regime
    + a populated forward-OOS window) must pass BEFORE replay, and a candidate's
    trigger must be FREQUENT ENOUGH to clear it.

C14 is a materially-new SINGLE-BAR CONVICTION EVENT: a daily bar whose true range
is an OUTLIER (>= K * ATR(14)) AND that closes in the TOP quartile of its own
range (a strong, conviction close), followed long for a SHORT bounded horizon on
the hypothesis that the conviction shock partially persists. It is NOT a
volatility compression->expansion squeeze (no compression precondition), NOT a
breakout-of-a-level, NOT a trend-STATE bet, NOT mean-reversion, NOT calendar,
cross-sectional, reclaim, or lead-lag. All the C10-C13 hard gates are built in
from the start, including the structural labels sample-size gate BEFORE replay.
"""
from __future__ import annotations

from typing import Any

from sparta_commander.lead_lag_propagation_continuation_v1_rejection_record_contract import (  # noqa: E501
    REJECTION_STATUS as C13_REJECTION_STATUS,
    build_c13_rejection_record,
)

C14P_SCHEMA_VERSION = 1
C14P_MODE = "RESEARCH_ONLY"
CANDIDATE_NUMBER = 14
CANDIDATE_FAMILY = "conviction_bar_follow_through"
CANDIDATE_ID = "CONVICTION_BAR_FOLLOW_THROUGH_V1"

VERDICT_C14P_READY = "CANDIDATE_14_FAMILY_PROPOSAL_READY"
VERDICT_C14P_BLOCKED = "CANDIDATE_14_FAMILY_PROPOSAL_BLOCKED"
NEXT_REQUIRED_ACTION = "HUMAN_DECISION_C14_ADVANCE_TO_SPEC_OR_REJECT_PROPOSAL"

HEAD_AT_C13_REJECTION = "2d287bb2d6feb31a35286e2080e821bac5419612"

# Full C1-C13 rejected-family ledger (every version string; C13 appended).
REJECTED_FAMILIES_C1_TO_C13 = (
    "ny_session_fvg_choch",
    "ny_session_fvg_choch_v3",
    "crypto_intraday_breakout_pullback_structure",
    "crypto_intraday_breakout_pullback_structure_v2",
    "long_biased_trend_continuation",
    "btc_sol_long_trend_continuation_v1",
    "long_1h_swing_structure",
    "sol_btc_long_1h_swing_structure",
    "eth_sol_relative_strength_pullback_continuation",
    "eth_sol_relative_strength_pullback_continuation_v1",
    "multi_symbol_relative_strength_rotation_filter",
    "volatility_compression_expansion",
    "liquidity_sweep_mean_reversion",
    "low_volume_downside_capitulation_mean_reversion",
    "intraweek_calendar_seasonality_drift",        # C10
    "cross_asset_dispersion_reversion",            # C11
    "failed_breakdown_reclaim_reversal",           # C12
    "lead_lag_propagation_continuation",           # C13
)

CLEAN_HYPOTHESIS = (
    "When a daily bar's TRUE RANGE is an OUTLIER (>= K * ATR(14)) AND it CLOSES "
    "in the TOP quartile of its own range -- a single-bar high-CONVICTION "
    "volatility-expansion event -- the move tends to FOLLOW THROUGH over a short "
    "1-2 day horizon. Enter long at the conviction bar's close and capture the "
    "follow-through with a fast target. The signal is a single-bar conviction "
    "EVENT, not a squeeze-release, breakout level, trend-state, or mean "
    "reversion.")
EDGE_SOURCE_HYPOTHESIS = (
    "A single-bar OUTLIER range with a strong upper-range close reflects an "
    "information / positioning shock (forced flow, repricing) that partially "
    "PERSISTS over a short horizon. The edge source is the short-horizon "
    "persistence of the conviction shock -- which can occur in up, down, and "
    "chop regimes -- so it must be regime-symmetric, must beat random-entry "
    "timing AND buy-and-hold, and target capture must dominate (else it is just "
    "drift / carry, not a conviction edge).")

# Why C14 is materially different from EACH rejected family (C1-C13).
MATERIAL_DIFFERENCE_FROM_EACH_REJECTED = {
    "ny_session_fvg_choch": "No intraday FVG/CHoCH structure and no session window; the trigger is a daily single-bar range-outlier + close-location statistic.",
    "ny_session_fvg_choch_v3": "Same: no intraday structural-imbalance pattern; daily conviction-bar event.",
    "crypto_intraday_breakout_pullback_structure": "No breakout of any level and no pullback; entry is on the conviction bar's own close, not a continuation of a level break.",
    "crypto_intraday_breakout_pullback_structure_v2": "Same: range-outlier + close-strength single-bar trigger, not a breakout-pullback geometry.",
    "long_biased_trend_continuation": "NOT a trend-STATE bet: a single-bar conviction EVENT with a must-beat-buy-and-hold gate that explicitly forbids relying on generic long carry.",
    "btc_sol_long_trend_continuation_v1": "Same: not absolute trend continuation; a single conviction-bar follow-through over a short horizon.",
    "long_1h_swing_structure": "No swing-structure pattern and not 1h; a daily single-bar range/close-location event.",
    "sol_btc_long_1h_swing_structure": "Same: no swing structure, daily timeframe, conviction-bar trigger.",
    "eth_sol_relative_strength_pullback_continuation": "Not relative-strength and not a pullback: a single-asset ABSOLUTE single-bar conviction event, no cross-sectional ranking.",
    "eth_sol_relative_strength_pullback_continuation_v1": "Same: absolute single-asset conviction-bar trigger, not an RS pullback.",
    "multi_symbol_relative_strength_rotation_filter": "No cross-sectional ranking/rotation; a per-asset single-bar conviction event.",
    "volatility_compression_expansion": "NO compression precondition: C-vol trades the COMPRESSION->EXPANSION transition (squeeze release / NR7); C14 triggers on an ABSOLUTE single-bar range OUTLIER (>= K*ATR) WITH a specific top-quartile CLOSE LOCATION, regardless of any prior compression -- a different signal entirely.",
    "liquidity_sweep_mean_reversion": "CONTINUATION not mean-reversion, and no liquidity wick: a conviction-bar follow-through, the opposite directional thesis.",
    "low_volume_downside_capitulation_mean_reversion": "Not volume/capitulation-based and not mean-reversion: trigger is range-outlier + close-strength, can fire on any volume and on UP conviction bars.",
    "intraweek_calendar_seasonality_drift": "A market-STATE/EVENT trigger (a conviction bar), never a date/weekday; with a must-beat-buy-and-hold gate so it cannot be long-drift in disguise.",
    "cross_asset_dispersion_reversion": "Single-asset ABSOLUTE single-bar event, not a cross-sectional relative z-score; continuation not reversion.",
    "failed_breakdown_reclaim_reversal": "Not a failed-breakdown reclaim of a structural low and not mean-reversion; an expansion/conviction bar follow-through.",
    "lead_lag_propagation_continuation": "Single-asset SELF-triggered conviction event, not a cross-asset leader->follower propagation; no second trigger asset.",
}

C10_C11_C12_C13_LESSONS_APPLIED = (
    "C10 lesson: never a calendar/weekday trigger; regime symmetry + forward-OOS "
    "continuation are mandatory and validated EARLY.",
    "C11 lesson: strong labels are NECESSARY BUT NOT SUFFICIENT -- forward-OOS "
    "continuation and bull/bear/chop net symmetry are HARD replay gates.",
    "C12 lesson: the must-beat-RANDOM-ENTRY baseline is the decisive anti-edge "
    "filter; target capture must dominate horizon exits; must beat buy-and-hold "
    "(no bull-carry reliance).",
    "C13 lesson: a too-RARE trigger is a STRUCTURAL REJECTION at the labels stage "
    "BEFORE replay -- the labels sample-size gate (>=100 total / >=20 per asset / "
    ">=20 per regime + a populated forward-OOS window) must pass first, and the "
    "conviction-bar threshold must be calibrated FREQUENT ENOUGH to clear it "
    "(pre-registered, never fit to manufacture samples).",
)

# THE HARD RULE that operationalizes the C10-C13 lessons for C14.
HARD_RULE_EARLY_GENERALIZATION_AND_ANTI_DRIFT = (
    "Candidate #14 MUST pass an EARLY battery BEFORE robustness and BEFORE any "
    "promotion: (0) a STRUCTURAL LABELS SAMPLE-SIZE gate FIRST (>=100 accepted "
    "total, >=20 per asset, >=20 per regime, and a NON-EMPTY forward-OOS window) "
    "-- failing it is a labels-stage structural rejection, the C13 lesson; "
    "(1) FORWARD-OOS continuation; (2) CROSS-REGIME SYMMETRY (bull/bear/chop "
    "net-positive or at minimum non-negative); (3) CROSS-ASSET (holds on more "
    "than one asset); (4) MUST BEAT a matched BUY-AND-HOLD AND a matched "
    "RANDOM-ENTRY baseline; and (5) TARGET-CAPTURE DOMINANCE (horizon-exit share "
    "below a pre-registered cap). Failing ANY is a STRUCTURAL REJECTION, not a "
    "warning.")

ANTI_TRAP_FILTERS = (
    "REJECT if the edge is explained by generic bullish long-drift / market "
    "carry (must beat matched buy-and-hold AND be regime-symmetric).",
    "REJECT if it is not better than a matched RANDOM-ENTRY baseline -- the "
    "conviction-bar filter must add timing value (the C12 failure mode).",
    "REJECT if the result is horizon/drift dominated (horizon-exit share above "
    "the pre-registered cap; target capture must dominate).",
    "REJECT if the edge does not continue in forward-OOS (required early).",
    "REJECT if the trigger is too RARE to clear the labels sample-size gate "
    "(>=100 / >=20 per asset / >=20 per regime + populated forward-OOS) -- the "
    "C13 failure mode; the threshold is pre-registered, never fit for samples.",
    "REJECT if it depends on a single asset (cross-asset required) or any "
    "weekday/calendar date (no date/weekday trigger permitted).",
    "PENALIZE thin per-trade net edge and fee/slippage fragility before any "
    "robustness run.",
)

DATA_NEEDS = {
    "assets_required_minimum": ["BTC", "ETH", "SOL"],
    "assets_preferred_future": ["BTC", "ETH", "SOL", "plus additional majors "
                                "(separately authorized fetch)"],
    "timeframe": "1d",
    "market_type": "spot",
    "fields_required": ["open", "high", "low", "close"],
    "already_on_disk_frozen": ["data/crypto_d1_spot/raw/BTC_1d.csv",
                               "data/crypto_d1_spot/raw/ETH_1d.csv",
                               "data/crypto_d1_spot/raw/SOL_1d.csv"],
    "new_fetch_needed_for_initial_research": False,
    "wider_asset_set_needs_separate_authorized_fetch": True,
}
SYMBOLS = ("BTCUSD", "ETHUSD", "SOLUSD")
TIMEFRAME = "1d"
DIRECTION = "long_only"
DIRECTION_NOTE = ("long-only research labels on the conviction-bar "
                  "follow-through; never a short/borrow leg and never a trading "
                  "capability")

ENTRY_CONCEPT = (
    "On each daily bar compute true_range and ATR(14). A CONVICTION BAR requires "
    "(a) true_range >= K * ATR(14) (a pre-registered volatility-expansion "
    "OUTLIER, NOT conditioned on any prior compression) AND (b) the close in the "
    "TOP quartile of the bar's range: close >= low + 0.75 * (high - low) (a "
    "strong conviction close). Enter LONG at that bar's close. Weekday is "
    "irrelevant by design; the trigger is purely the range-outlier + close "
    "location.")
EXIT_CONCEPT = (
    "Pre-registered SHORT fixed horizon (e.g. 1-2 daily bars) OR a pre-registered "
    "R-multiple target, whichever first; the horizon is a human-fixed, disclosed "
    "assumption (NOT optimized after results). Target capture must dominate -- a "
    "high horizon-exit share is a structural rejection.")
RISK_GEOMETRY = {
    "stop": "ATR(14)-based structure stop, pre-registered multiplier; INVALID if "
            "stop not below entry; never tightened post-hoc.",
    "targets": "pre-registered R-multiples (e.g. 1R/1.5R/2R); no new variants "
               "after label freeze; a gross target-distance floor in bps.",
    "costs": "taker fees + conservative slippage modeled honestly (inherits the "
             "C10-C13 37 bps all-in discipline) before any PASS.",
    "sizing": "equal-weight / fixed-fraction research sizing only; NO leverage; "
              "NO shorting; NO portfolio compute.",
}

EARLY_GENERALIZATION_CHECKS = (
    "structural_labels_sample_size_gate_before_replay_required_early",
    "forward_oos_continuation_required_early",
    "cross_regime_bull_bear_chop_symmetry_required_early",
    "cross_asset_multiple_assets_required_early",
    "beats_buy_and_hold_and_random_entry_baseline_required_early",
    "target_capture_dominates_horizon_exit_share_capped_required_early",
)
PROMOTION_TO_HUMAN_REVIEW_CONDITIONS = (
    "passes the STRUCTURAL labels sample-size gate first (the C13 lesson)",
    "passes the EARLY generalization + anti-drift battery before robustness",
    "net-positive after honest fees + slippage with adequate sample",
    "regime-symmetric (not explained by long-drift / bull carry)",
    "beats a matched buy-and-hold AND random-entry baseline on the same dates",
    "target-capture dominated (horizon-exit share below the pre-registered cap)",
    "continues in forward-OOS",
    "no single-asset / weekday / calendar dependence",
    "every gate human-reviewed; the human decides",
)

C14P_LABEL = (
    "SPARTA Candidate #14 Family Proposal (READ-ONLY, RESEARCH ONLY). "
    "conviction_bar_follow_through: go long after a single-bar CONVICTION event "
    "(true_range >= K*ATR(14) AND top-quartile close), betting the conviction "
    "shock follows through over a short horizon (NOT a squeeze-release, breakout "
    "level, trend-state, mean-reversion, calendar, cross-sectional, reclaim, or "
    "lead-lag). MATERIALLY DIFFERENT FROM C1-C13. PROPOSAL ONLY -- NO DETECTOR, "
    "NO LABELS, NO REPLAY, NO TRADING. STRUCTURAL LABELS SAMPLE-SIZE GATE + "
    "FORWARD-OOS + REGIME SYMMETRY + MUST-BEAT-BUY&HOLD + MUST-BEAT-RANDOM + "
    "TARGET-CAPTURE-DOMINANCE ARE HARD GATES FROM THE START."
)

_CAPABILITY_FLAGS_FALSE = (
    "runs_detector", "runs_detector_now", "labels_now", "runs_labels",
    "runs_replay", "runs_replay_now", "runs_robustness", "runs_generalization",
    "fetches_data", "stages_data_now", "calls_api", "uses_network",
    "uses_credentials", "uses_wallet", "uses_account", "connects_broker",
    "connects_exchange", "uses_real_money", "contains_order_logic",
    "contains_portfolio_allocation_logic", "runs_portfolio_compute",
    "deploys_capital", "starts_scheduler", "sends_notifications",
    "auto_commits", "auto_pushes", "reuses_rejected_geometry_unchanged",
    "is_a_rescue_attempt", "uses_weekday_or_calendar_trigger",
    "is_single_asset_edge", "relies_on_long_drift_or_bull_carry",
    "authorizes_paper_execution", "authorizes_micro_live",
    "authorizes_live_trading", "promotes_gate", "unlocks_downstream_gate",
    "claims_profitability", "claims_edge", "executes", "writes_files",
)


def get_candidate_14_family_proposal_label() -> str:
    return C14P_LABEL


def get_candidate_14_family_proposal_next_action() -> str:
    return NEXT_REQUIRED_ACTION


def build_candidate_14_family_proposal(repo_root: Any = ".",
                                       tracked_paths: list | None = None
                                       ) -> dict[str, Any]:
    """Assemble the Candidate #14 family proposal. Chain-gated on the closed
    C13 rejection record. Pure; no I/O; proposal only."""
    record: dict[str, Any] = {
        "schema_version": C14P_SCHEMA_VERSION,
        "label": C14P_LABEL, "mode": C14P_MODE,
        "lane": "crypto_d1_auto_research",
        "candidate_number": CANDIDATE_NUMBER,
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "verdict": None, "blockers": [],
        "head_at_c13_rejection": HEAD_AT_C13_REJECTION,
        "clean_hypothesis": CLEAN_HYPOTHESIS,
        "edge_source_hypothesis": EDGE_SOURCE_HYPOTHESIS,
        "rejected_families_c1_to_c13": list(REJECTED_FAMILIES_C1_TO_C13),
        "material_difference_from_each_rejected":
            dict(MATERIAL_DIFFERENCE_FROM_EACH_REJECTED),
        "c10_c11_c12_c13_lessons_applied":
            list(C10_C11_C12_C13_LESSONS_APPLIED),
        "hard_rule_early_generalization_and_anti_drift":
            HARD_RULE_EARLY_GENERALIZATION_AND_ANTI_DRIFT,
        "anti_trap_filters": list(ANTI_TRAP_FILTERS),
        "data_needs": dict(DATA_NEEDS),
        "symbols": list(SYMBOLS), "timeframe": TIMEFRAME,
        "direction": DIRECTION, "direction_note": DIRECTION_NOTE,
        "entry_concept": ENTRY_CONCEPT, "exit_concept": EXIT_CONCEPT,
        "risk_geometry": dict(RISK_GEOMETRY),
        "early_generalization_checks": list(EARLY_GENERALIZATION_CHECKS),
        "promotion_to_human_review_conditions":
            list(PROMOTION_TO_HUMAN_REVIEW_CONDITIONS),
        "is_proposal_only": True,
        "is_materially_new_family": True,
        "is_a_rescue_attempt": False,
        "reuses_rejected_geometry_unchanged": False,
        "relies_on_long_drift_or_bull_carry": False,
        "current_loop_stage": "candidate_family_proposal",
        "human_review_required": True,
        "detector_gate_locked": True,
        "labels_gate_locked": True,
        "replay_gate_locked": True,
        "paper_trading_gate_locked": True,
        "live_gate_locked": True,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_detector": True, "no_labels": True, "no_replay": True,
        "no_robustness_run": True, "no_generalization_run": True,
        "no_data_fetch": True, "no_paper_trading": True,
        "no_live_trading": True, "no_broker": True, "no_credentials": True,
        "no_order_logic": True, "no_portfolio_compute": True,
        "no_optimization": True, "no_weekday_trigger": True,
        "no_calendar_trigger": True, "no_rescue_of_rejected_geometry": True,
        "no_long_drift_or_bull_carry_reliance": True,
        "no_profitability_claim": True, "no_downstream_gate_unlock": True,
    }

    # The proposed family must be MATERIALLY NEW (not a rejected family) and
    # must differentiate from EVERY rejected family C1-C13.
    if CANDIDATE_FAMILY in REJECTED_FAMILIES_C1_TO_C13:
        record["verdict"] = VERDICT_C14P_BLOCKED
        record["blockers"].append("proposed_family_is_a_rejected_family")
        return record
    missing = [f for f in REJECTED_FAMILIES_C1_TO_C13
               if f not in MATERIAL_DIFFERENCE_FROM_EACH_REJECTED]
    if missing:
        record["verdict"] = VERDICT_C14P_BLOCKED
        record["blockers"].append("differentiation_missing_for_some_rejected")
        return record

    rej = build_c13_rejection_record(repo_root, tracked_paths or [])
    record["c13_rejection_status"] = rej.get("rejection_status")
    if rej.get("rejection_status") != C13_REJECTION_STATUS:
        record["verdict"] = VERDICT_C14P_BLOCKED
        record["blockers"].append("c13_not_closed_on_record")
        return record

    record["verdict"] = VERDICT_C14P_READY
    return record


def validate_candidate_14_family_proposal(record: dict[str, Any]
                                          ) -> dict[str, Any]:
    """Anti-tamper validator. READY is valid only when the proposal is
    materially new, differentiates from every rejected family C1-C13, carries
    the hard early-generalization + anti-drift rule (incl. the structural labels
    sample-size gate, the must-beat-random-entry / buy-and-hold gates, and the
    target-capture cap), and locks all execution / downstream gates."""
    failures: list = []
    if record.get("verdict") != VERDICT_C14P_READY:
        failures.append("verdict_not_ready")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("mode") != C14P_MODE:
        failures.append("mode_not_research_only")
    if record.get("candidate_family") != CANDIDATE_FAMILY:
        failures.append("candidate_family_tampered")
    if record.get("candidate_number") != 14:
        failures.append("candidate_number_tampered")

    # Materially new + full differentiation across C1-C13.
    if record.get("is_materially_new_family") is not True:
        failures.append("not_marked_materially_new")
    if record.get("candidate_family") in (
            record.get("rejected_families_c1_to_c13") or []):
        failures.append("proposed_family_is_rejected_family")
    diff = record.get("material_difference_from_each_rejected") or {}
    for f in (record.get("rejected_families_c1_to_c13") or []):
        if not diff.get(f):
            failures.append("differentiation_missing_%s" % f)
    if record.get("c13_rejection_status") != "REJECTED_KEPT_ON_RECORD":
        failures.append("c13_rejection_status_tampered")

    # The hard early-generalization + anti-drift rule + checks must be present.
    if not record.get("hard_rule_early_generalization_and_anti_drift"):
        failures.append("hard_early_generalization_rule_missing")
    for chk in ("structural_labels_sample_size_gate_before_replay_required_early",
                "forward_oos_continuation_required_early",
                "cross_regime_bull_bear_chop_symmetry_required_early",
                "cross_asset_multiple_assets_required_early",
                "beats_buy_and_hold_and_random_entry_baseline_required_early",
                "target_capture_dominates_horizon_exit_share_capped_required_early"):
        if chk not in (record.get("early_generalization_checks") or []):
            failures.append("early_generalization_check_missing_%s" % chk)

    # Proposal-only posture + the anti-carry stance.
    if record.get("is_proposal_only") is not True:
        failures.append("not_proposal_only")
    if record.get("is_a_rescue_attempt") is not False:
        failures.append("rescue_attempt_flag_tampered")
    if record.get("relies_on_long_drift_or_bull_carry") is not False:
        failures.append("long_drift_reliance_flag_tampered")

    locks = record.get("scope_locks") or {}
    for key in ("no_detector", "no_labels", "no_replay", "no_data_fetch",
                "no_paper_trading", "no_live_trading", "no_portfolio_compute",
                "no_calendar_trigger", "no_weekday_trigger",
                "no_rescue_of_rejected_geometry",
                "no_long_drift_or_bull_carry_reliance"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for key in ("detector_gate_locked", "labels_gate_locked",
                "replay_gate_locked", "paper_trading_gate_locked",
                "live_gate_locked", "human_review_required"):
        if record.get(key) is not True:
            failures.append("gate_flag_tampered_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
