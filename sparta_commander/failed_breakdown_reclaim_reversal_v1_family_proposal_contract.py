"""SPARTA Candidate #12 family proposal: failed_breakdown_reclaim_reversal_v1.

PROPOSAL ONLY. RESEARCH ONLY. This contract proposes a NEW strategy family for
the Strategy Factory after Candidates #10 AND #11 were both closed
REJECTED_KEPT_ON_RECORD. It is pure and in-memory: NO detector, NO labels, NO
replay, NO robustness, NO generalization run, NO data fetch, NO trading, NO
portfolio compute, NO downstream gate unlock. It only proposes a hypothesis +
differentiation + research plan for human review.

Chain gate: build_candidate_12_family_proposal() requires
build_c11_rejection_record() to return REJECTED_KEPT_ON_RECORD -- C12 may only
open once C11 is formally closed on the ledger.

THE C10 + C11 LESSONS (applied as HARD rules here):
  * C10 was undifferentiated bullish LONG-DRIFT dressed as a Friday calendar
    edge, only caught at the final generalization gate. Lesson: never a
    date/weekday trigger; regime symmetry and forward-OOS are mandatory early.
  * C11 had STRONG real-candle labels (cross-asset, cross-regime, weekday-
    neutral) yet still FAILED the fee-honest replay: forward-OOS 2026 negative
    for every variant, bear-regime negative, and the result was horizon/drift
    dominated (65-75% horizon exits, ~2-11% hit rate) -- i.e. it leaned on
    bull/chop holding drift, not on the signal. Lesson: strong labels are
    NECESSARY BUT NOT SUFFICIENT; forward-OOS continuation AND regime symmetry
    are HARD replay-stage gates, and an edge must make its money from the EVENT
    (target capture), not from being long during an uptrend.

C12 is built to resist exactly those failure modes: an EVENT-confirmed reversal
(a failed breakdown that is RECLAIMED on the close) with a short, bounded hold;
and it adds two NEW anti-drift / anti-carry gates that neither C10 nor C11 had --
(1) the strategy must BEAT a matched buy-and-hold AND a matched random-entry
baseline over the same dates, and (2) a hard cap on horizon-exit share (target
capture must dominate) -- both enforced EARLY as structural rejections.
"""
from __future__ import annotations

from typing import Any

from sparta_commander.cross_asset_dispersion_reversion_v1_rejection_record_contract import (  # noqa: E501
    REJECTION_STATUS as C11_REJECTION_STATUS,
    build_c11_rejection_record,
)

C12P_SCHEMA_VERSION = 1
C12P_MODE = "RESEARCH_ONLY"
CANDIDATE_NUMBER = 12
CANDIDATE_FAMILY = "failed_breakdown_reclaim_reversal"
CANDIDATE_ID = "FAILED_BREAKDOWN_RECLAIM_REVERSAL_V1"

VERDICT_C12P_READY = "CANDIDATE_12_FAMILY_PROPOSAL_READY"
VERDICT_C12P_BLOCKED = "CANDIDATE_12_FAMILY_PROPOSAL_BLOCKED"
NEXT_REQUIRED_ACTION = "HUMAN_DECISION_C12_ADVANCE_TO_SPEC_OR_REJECT_PROPOSAL"

HEAD_AT_C11_REJECTION = "0fa49663de9307d90bd2f6b60456811fc78097d9"

# Full C1-C11 rejected-family ledger (every version string; C11 appended).
REJECTED_FAMILIES_C1_TO_C11 = (
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
    "intraweek_calendar_seasonality_drift",       # C10
    "cross_asset_dispersion_reversion",           # C11
)

CLEAN_HYPOTHESIS = (
    "When price breaks to a new K-day low intrabar but then RECLAIMS that prior "
    "K-day low by the daily close (a FAILED BREAKDOWN -- a stop-run / liquidity "
    "grab that is immediately rejected), the next few bars tend to resolve "
    "upward. The signal is a CONFIRMED reversal EVENT (the close-back-above), "
    "not a dip-buy, not a trend bet, and not a calendar effect. Profit must come "
    "from capturing the post-reclaim snap, NOT from holding through drift.")
EDGE_SOURCE_HYPOTHESIS = (
    "Liquidity/stop-run microstructure: a sweep of resting liquidity below an "
    "obvious K-day low that fails to follow through and is reclaimed on the "
    "close traps breakdown sellers and forces short-covering / dip absorption. "
    "The edge source is the FAILED-BREAKDOWN RECLAIM event itself, which occurs "
    "in bull, bear, and chop regimes -- so it must be regime-symmetric, and it "
    "must beat a matched buy-and-hold baseline (else it is just market carry).")

# Why C12 is materially different from EACH rejected family (C1-C11).
MATERIAL_DIFFERENCE_FROM_EACH_REJECTED = {
    "ny_session_fvg_choch": "No intraday FVG/CHoCH structure and no session window; the trigger is a daily failed-breakdown reclaim of a K-day low, confirmed on the close.",
    "ny_session_fvg_choch_v3": "Same: no intraday structural-imbalance pattern, no NY session; daily close-confirmed reclaim event.",
    "crypto_intraday_breakout_pullback_structure": "OPPOSITE direction of the same axis: that family buys breakOUT continuation; C12 fades a failed breakDOWN that is reclaimed (a reversal, not a continuation), and on the daily timeframe.",
    "crypto_intraday_breakout_pullback_structure_v2": "Same: continuation-of-breakout vs reversal-of-failed-breakdown; daily not intraday.",
    "long_biased_trend_continuation": "NOT a trend/long-bias edge; it is an event-confirmed counter-move reversal with a short bounded hold and an explicit must-beat-buy-and-hold gate that directly forbids relying on bull carry.",
    "btc_sol_long_trend_continuation_v1": "Same: not absolute trend continuation; a single-bar reclaim reversal event.",
    "long_1h_swing_structure": "No swing-structure pattern and not 1h; a daily K-day-low reclaim event.",
    "sol_btc_long_1h_swing_structure": "Same: no swing structure, daily timeframe, reclaim-event trigger.",
    "eth_sol_relative_strength_pullback_continuation": "Not relative-strength and not continuation: a single-asset absolute price-level reclaim, traded as reversal not pullback-continuation.",
    "eth_sol_relative_strength_pullback_continuation_v1": "Same: absolute single-asset reclaim event, not a relative-strength pullback continuation.",
    "multi_symbol_relative_strength_rotation_filter": "No cross-sectional ranking/rotation; a single-asset absolute structural-level reclaim, evaluated per asset.",
    "volatility_compression_expansion": "Trigger is a failed-breakdown RECLAIM of a price level, not a volatility-band compression/expansion state; volatility only sizes the stop.",
    "liquidity_sweep_mean_reversion": "Distinct trigger AND confirmation: C8 fades the sweep WICK itself (intrabar mean reversion of a liquidity wick); C12 requires a CLOSE back above a structural K-day low (a confirmed failed-breakdown reclaim) before any entry -- confirmation-based, not wick-fade, and tied to a defined K-day structural level rather than an arbitrary wick.",
    "low_volume_downside_capitulation_mean_reversion": "NOT volume- or capitulation-based: the trigger is purely the price-structure reclaim of a K-day low and can fire on any volume; no capitulation/low-volume condition.",
    "intraweek_calendar_seasonality_drift": "A market-STATE/EVENT trigger (failed-breakdown reclaim), never a date/weekday; directly avoids C10's calendar + long-drift trap, and adds a must-beat-buy-and-hold gate so it cannot be long-drift in disguise.",
    "cross_asset_dispersion_reversion": "SINGLE-ASSET ABSOLUTE structural event, not a cross-sectional relative z-score; and unlike C11 it is target-capture-driven with a HARD horizon-exit-share cap so it cannot be horizon/drift dominated, plus a must-beat-buy-and-hold gate that C11 lacked.",
}

C10_C11_LESSONS_APPLIED = (
    "C10 lesson: never a calendar/weekday trigger; regime symmetry and "
    "forward-OOS continuation are mandatory and validated EARLY, not at the end.",
    "C11 lesson: strong labels are NECESSARY BUT NOT SUFFICIENT -- forward-OOS "
    "continuation and regime symmetry are HARD replay-stage gates; an edge that "
    "is horizon/drift dominated or that does not beat buy-and-hold is rejected.",
    "Operational consequence for C12: add an explicit must-beat-buy-and-hold AND "
    "must-beat-random-entry baseline gate, and a hard cap on horizon-exit share "
    "(target capture must dominate), BOTH enforced early as structural "
    "rejections -- gates that neither C10 nor C11 carried.",
)

# THE HARD RULE that operationalizes the C10 + C11 lessons for C12.
HARD_RULE_EARLY_GENERALIZATION_AND_ANTI_DRIFT = (
    "Candidate #12 MUST pass an EARLY battery at the labels/replay stage, BEFORE "
    "robustness and BEFORE any promotion: (1) FORWARD-OOS continuation (the edge "
    "must still be net-positive after honest costs in a sealed forward window); "
    "(2) CROSS-REGIME SYMMETRY (net-positive, or at minimum non-negative, in "
    "bull AND bear AND chop -- not carried by one regime); (3) CROSS-ASSET (must "
    "hold on more than one asset); (4) MUST BEAT a matched BUY-AND-HOLD AND a "
    "matched RANDOM-ENTRY baseline over the same dates (the edge must be "
    "attributable to the reclaim EVENT, not to being long in an uptrend); and "
    "(5) TARGET-CAPTURE DOMINANCE (horizon-exit share must stay below a "
    "pre-registered cap -- the edge cannot be horizon/drift dominated). Failing "
    "ANY of these is a STRUCTURAL REJECTION, not a warning.")

ANTI_TRAP_FILTERS = (
    "REJECT if the edge is explained by generic bullish long-drift / market "
    "carry (test: must beat a matched buy-and-hold baseline on the same dates "
    "AND be regime-symmetric across bull/bear/chop).",
    "REJECT if the result is horizon/drift dominated (test: horizon-exit share "
    "must stay below a pre-registered cap; target capture must dominate) -- the "
    "direct C11 failure mode.",
    "REJECT if the edge does not continue in forward-OOS (forward continuation "
    "required early, not at the end) -- the direct C10 AND C11 failure mode.",
    "REJECT if the edge depends on a single asset (cross-asset required) or on "
    "any weekday/calendar date (no date/weekday trigger permitted).",
    "REJECT if the 'reclaim' is not CONFIRMED on the close (no anticipatory "
    "intrabar entries; the failed-breakdown must close back above the level).",
    "PENALIZE thin per-trade net edge and fee/slippage fragility before any "
    "robustness run.",
)

DATA_NEEDS = {
    "assets_required_minimum": ["BTC", "ETH", "SOL"],
    "assets_preferred_future": ["BTC", "ETH", "SOL", "plus additional majors "
                                "for wider cross-asset confirmation (separately "
                                "authorized fetch)"],
    "timeframe": "1d",
    "market_type": "spot",
    "fields_required": ["open", "high", "low", "close"],
    "already_on_disk_frozen": ["data/crypto_d1_spot/raw/BTC_1d.csv",
                               "data/crypto_d1_spot/raw/ETH_1d.csv",
                               "data/crypto_d1_spot/raw/SOL_1d.csv"],
    "new_fetch_needed_for_initial_research": False,
    "wider_cross_section_needs_separate_authorized_fetch": True,
}
SYMBOLS = ("BTCUSD", "ETHUSD", "SOLUSD")
TIMEFRAME = "1d"
DIRECTION = "long_only"
DIRECTION_NOTE = ("long-only research labels on the reclaim reversal; never a "
                  "trading capability and never a short/borrow leg")

ENTRY_CONCEPT = (
    "On each daily bar, let L_K = the lowest LOW over the prior K bars "
    "(pre-registered K, e.g. 20). A FAILED-BREAKDOWN RECLAIM occurs when the "
    "bar's low pierces below L_K (a new K-day low intrabar) BUT the bar CLOSES "
    "back above L_K. Enter LONG at that bar's close. No date/weekday condition; "
    "the trigger is purely the structural-level reclaim event.")
EXIT_CONCEPT = (
    "Pre-registered SHORT bounded horizon (e.g. 2-3 daily bars) OR a "
    "pre-registered R-multiple target, whichever comes first; the horizon is a "
    "human-fixed, disclosed assumption (NOT optimized after results, the C11 "
    "discipline). Target capture must dominate -- a high horizon-exit share is a "
    "structural rejection.")
RISK_GEOMETRY = {
    "stop": "structure stop just below the reclaim bar's low; ATR(14)-validated "
            "pre-registered multiplier; INVALID if stop not below entry; never "
            "tightened post-hoc.",
    "targets": "pre-registered R-multiples (e.g. 1.5R/2R/3R); no new variants "
               "after label freeze; a gross target-distance floor in bps.",
    "costs": "taker fees + conservative slippage modeled honestly (inherits the "
             "C10/C11 37 bps all-in discipline) before any PASS.",
    "sizing": "equal-weight / fixed-fraction research sizing only; NO leverage, "
              "NO shorting, NO portfolio compute.",
}

EARLY_GENERALIZATION_CHECKS = (
    "forward_oos_continuation_required_early",
    "cross_regime_bull_bear_chop_symmetry_required_early",
    "cross_asset_multiple_assets_required_early",
    "beats_buy_and_hold_and_random_entry_baseline_required_early",
    "target_capture_dominates_horizon_exit_share_capped_required_early",
)
PROMOTION_TO_HUMAN_REVIEW_CONDITIONS = (
    "passes the EARLY generalization + anti-drift battery before robustness",
    "net-positive after honest fees + slippage with adequate sample",
    "regime-symmetric (not explained by long-drift / bull carry)",
    "beats a matched buy-and-hold AND random-entry baseline on the same dates",
    "target-capture dominated (horizon-exit share below the pre-registered cap)",
    "continues in forward-OOS",
    "no single-asset / weekday / calendar dependence",
    "every gate human-reviewed; the human decides",
)

C12P_LABEL = (
    "SPARTA Candidate #12 Family Proposal (READ-ONLY, RESEARCH ONLY). "
    "failed_breakdown_reclaim_reversal: go long when a new K-day-low breakdown "
    "is RECLAIMED on the daily close (a confirmed stop-run reversal EVENT, NOT a "
    "dip-buy, trend bet, or calendar effect). MATERIALLY DIFFERENT FROM C1-C11. "
    "PROPOSAL ONLY -- NO DETECTOR, NO LABELS, NO REPLAY, NO TRADING. FORWARD-OOS "
    "+ REGIME SYMMETRY + MUST-BEAT-BUY-AND-HOLD + TARGET-CAPTURE-DOMINANCE ARE "
    "HARD GATES FROM THE START."
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


def get_candidate_12_family_proposal_label() -> str:
    return C12P_LABEL


def get_candidate_12_family_proposal_next_action() -> str:
    return NEXT_REQUIRED_ACTION


def build_candidate_12_family_proposal(repo_root: Any = ".",
                                       tracked_paths: list | None = None
                                       ) -> dict[str, Any]:
    """Assemble the Candidate #12 family proposal. Chain-gated on the closed
    C11 rejection record. Pure; no I/O; proposal only."""
    record: dict[str, Any] = {
        "schema_version": C12P_SCHEMA_VERSION,
        "label": C12P_LABEL, "mode": C12P_MODE,
        "lane": "crypto_d1_auto_research",
        "candidate_number": CANDIDATE_NUMBER,
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "verdict": None, "blockers": [],
        "head_at_c11_rejection": HEAD_AT_C11_REJECTION,
        "clean_hypothesis": CLEAN_HYPOTHESIS,
        "edge_source_hypothesis": EDGE_SOURCE_HYPOTHESIS,
        "rejected_families_c1_to_c11": list(REJECTED_FAMILIES_C1_TO_C11),
        "material_difference_from_each_rejected":
            dict(MATERIAL_DIFFERENCE_FROM_EACH_REJECTED),
        "c10_c11_lessons_applied": list(C10_C11_LESSONS_APPLIED),
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
    # must differentiate from EVERY rejected family C1-C11.
    if CANDIDATE_FAMILY in REJECTED_FAMILIES_C1_TO_C11:
        record["verdict"] = VERDICT_C12P_BLOCKED
        record["blockers"].append("proposed_family_is_a_rejected_family")
        return record
    missing = [f for f in REJECTED_FAMILIES_C1_TO_C11
               if f not in MATERIAL_DIFFERENCE_FROM_EACH_REJECTED]
    if missing:
        record["verdict"] = VERDICT_C12P_BLOCKED
        record["blockers"].append("differentiation_missing_for_some_rejected")
        return record

    rej = build_c11_rejection_record(repo_root, tracked_paths or [])
    record["c11_rejection_status"] = rej.get("rejection_status")
    if rej.get("rejection_status") != C11_REJECTION_STATUS:
        record["verdict"] = VERDICT_C12P_BLOCKED
        record["blockers"].append("c11_not_closed_on_record")
        return record

    record["verdict"] = VERDICT_C12P_READY
    return record


def validate_candidate_12_family_proposal(record: dict[str, Any]
                                          ) -> dict[str, Any]:
    """Anti-tamper validator. READY is valid only when the proposal is
    materially new, differentiates from every rejected family C1-C11, carries
    the hard early-generalization + anti-drift rule (incl. the must-beat-buy-and-
    hold and target-capture-dominance gates), and locks all execution /
    downstream gates."""
    failures: list = []
    if record.get("verdict") != VERDICT_C12P_READY:
        failures.append("verdict_not_ready")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("mode") != C12P_MODE:
        failures.append("mode_not_research_only")
    if record.get("candidate_family") != CANDIDATE_FAMILY:
        failures.append("candidate_family_tampered")
    if record.get("candidate_number") != 12:
        failures.append("candidate_number_tampered")

    # Materially new + full differentiation across C1-C11.
    if record.get("is_materially_new_family") is not True:
        failures.append("not_marked_materially_new")
    if record.get("candidate_family") in (
            record.get("rejected_families_c1_to_c11") or []):
        failures.append("proposed_family_is_rejected_family")
    diff = record.get("material_difference_from_each_rejected") or {}
    for f in (record.get("rejected_families_c1_to_c11") or []):
        if not diff.get(f):
            failures.append("differentiation_missing_%s" % f)
    if record.get("c11_rejection_status") != "REJECTED_KEPT_ON_RECORD":
        failures.append("c11_rejection_status_tampered")

    # The hard early-generalization + anti-drift rule + checks must be present.
    if not record.get("hard_rule_early_generalization_and_anti_drift"):
        failures.append("hard_early_generalization_rule_missing")
    for chk in ("forward_oos_continuation_required_early",
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
