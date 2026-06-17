"""SPARTA Candidate #13 family proposal: lead_lag_propagation_continuation_v1.

PROPOSAL ONLY. RESEARCH ONLY. This contract proposes a NEW strategy family for
the Strategy Factory after Candidates #10, #11 AND #12 were all closed
REJECTED_KEPT_ON_RECORD. It is pure and in-memory: NO detector, NO labels, NO
replay, NO robustness, NO generalization run, NO data fetch, NO trading, NO
portfolio compute, NO downstream gate unlock. It only proposes a hypothesis +
differentiation + research plan for human review.

Chain gate: build_candidate_13_family_proposal() requires
build_c12_rejection_record() to return REJECTED_KEPT_ON_RECORD -- C13 may only
open once C12 is formally closed on the ledger.

THE C10 + C11 + C12 LESSONS (applied as HARD rules here):
  * C10: an undifferentiated bullish LONG-DRIFT edge dressed as a Friday calendar
    anomaly, caught only at the final generalization gate. -> no date/weekday
    trigger; regime symmetry + forward-OOS mandatory early.
  * C11: STRONG labels (cross-asset, cross-regime, weekday-neutral) yet FAILED
    the replay on forward-OOS + regime symmetry. -> labels are NECESSARY BUT NOT
    SUFFICIENT; forward-OOS continuation AND bull/bear/chop net symmetry are HARD
    replay gates.
  * C12: 206 strong labels (bear-largest) yet net-negative every variant and
    WORSE than random-entry timing. -> the must-beat-RANDOM-ENTRY baseline is the
    decisive anti-edge filter; the entry SIGNAL must add value over random
    timing, target capture must dominate horizon exits, and the edge must beat a
    matched buy-and-hold (no bull-carry reliance).

C13 is a materially-new EDGE AXIS -- cross-asset LEAD-LAG PROPAGATION
(information diffusion): when the price LEADER (BTC) posts a confirmed large daily
move, the laggier majors (ETH/SOL) tend to PROPAGATE it over a short horizon, and
the follower's catch-up is the edge. This is a directional-causality / timing
edge -- NOT reversion (C11), NOT relative-strength ranking/rotation (C9-area),
NOT same-asset trend continuation (C5/C6), NOT a calendar/structure/volatility/
capitulation/reclaim trigger. All five+ C10/C11/C12 hard gates are built in from
the start, plus a C13-specific gate: the cross-asset propagation must beat a
"buy-the-leader-instead" / follower-own-momentum baseline, so the edge is the
DIFFUSION, not generic strength.
"""
from __future__ import annotations

from typing import Any

from sparta_commander.failed_breakdown_reclaim_reversal_v1_rejection_record_contract import (  # noqa: E501
    REJECTION_STATUS as C12_REJECTION_STATUS,
    build_c12_rejection_record,
)

C13P_SCHEMA_VERSION = 1
C13P_MODE = "RESEARCH_ONLY"
CANDIDATE_NUMBER = 13
CANDIDATE_FAMILY = "lead_lag_propagation_continuation"
CANDIDATE_ID = "LEAD_LAG_PROPAGATION_CONTINUATION_V1"

VERDICT_C13P_READY = "CANDIDATE_13_FAMILY_PROPOSAL_READY"
VERDICT_C13P_BLOCKED = "CANDIDATE_13_FAMILY_PROPOSAL_BLOCKED"
NEXT_REQUIRED_ACTION = "HUMAN_DECISION_C13_ADVANCE_TO_SPEC_OR_REJECT_PROPOSAL"

HEAD_AT_C12_REJECTION = "7a04fa723afa3f33dc41445af6a36be64f325c07"

# Full C1-C12 rejected-family ledger (every version string; C12 appended).
REJECTED_FAMILIES_C1_TO_C12 = (
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
)

CLEAN_HYPOTHESIS = (
    "BTC is the crypto price LEADER. When BTC posts a CONFIRMED large daily move "
    "(a pre-registered positive return z-score) that a laggier major (ETH or "
    "SOL) has NOT yet matched, the leader's move tends to PROPAGATE to the "
    "follower over a short 1-2 day horizon. Enter the FOLLOWER long at the close "
    "that confirms the leader's move and capture the catch-up with a fast "
    "target. The signal is a LEADER->FOLLOWER timing/causality edge, not "
    "reversion, not a ranking, and not a same-asset trend bet.")
EDGE_SOURCE_HYPOTHESIS = (
    "Information diffusion / lead-lag price discovery: BTC's liquidity and price "
    "leadership propagate to alts with a short lag, so the follower's lagged "
    "catch-up after a confirmed leader move is the edge source. A large leader "
    "up-move diffuses in up, down, and chop regimes -- so the edge must be "
    "regime-symmetric, must beat random-entry timing, must beat buy-and-hold, "
    "and must beat a buy-the-leader-instead baseline (else it is generic "
    "strength / carry, not diffusion).")

# Why C13 is materially different from EACH rejected family (C1-C12).
MATERIAL_DIFFERENCE_FROM_EACH_REJECTED = {
    "ny_session_fvg_choch": "No intraday FVG/CHoCH structure and no session window; the trigger is a confirmed daily leader move that propagates cross-asset to a follower.",
    "ny_session_fvg_choch_v3": "Same: no intraday structural-imbalance pattern, no session; daily cross-asset lead-lag propagation.",
    "crypto_intraday_breakout_pullback_structure": "No breakout/pullback geometry; entry is on a FOLLOWER conditioned on a LEADER's confirmed move, on the daily timeframe.",
    "crypto_intraday_breakout_pullback_structure_v2": "Same: cross-asset propagation trigger, not a single-asset breakout-pullback continuation.",
    "long_biased_trend_continuation": "NOT same-asset trend continuation: the trigger asset (leader BTC) is DIFFERENT from the traded asset (follower ETH/SOL), and a must-beat-buy-and-hold + beat-the-leader baseline forbids generic long carry.",
    "btc_sol_long_trend_continuation_v1": "Same: not absolute trend continuation of the traded asset; a leader->follower diffusion event with a short horizon.",
    "long_1h_swing_structure": "No swing-structure pattern and not 1h; a daily cross-asset lead-lag propagation signal.",
    "sol_btc_long_1h_swing_structure": "Same: no swing structure, daily timeframe, leader->follower trigger.",
    "eth_sol_relative_strength_pullback_continuation": "Not relative-strength and not a pullback: no ranking of strongest/weakest; entry is the follower's CATCH-UP to a confirmed leader move, gated against being generic strength by the beat-the-leader baseline.",
    "eth_sol_relative_strength_pullback_continuation_v1": "Same: leader->follower diffusion timing, not an RS pullback continuation.",
    "multi_symbol_relative_strength_rotation_filter": "No cross-sectional ranking/rotation into top performers; a directed LEADER->FOLLOWER propagation event from a single designated leader.",
    "volatility_compression_expansion": "Trigger is a confirmed leader RETURN move that diffuses cross-asset, not a single-asset volatility-band compression/expansion state; volatility only sizes the stop.",
    "liquidity_sweep_mean_reversion": "Not a mean-reversion of a liquidity wick; a CONTINUATION/propagation of a confirmed leader move into a follower (opposite directional thesis), inherently two-asset.",
    "low_volume_downside_capitulation_mean_reversion": "Not volume/capitulation-based and not mean-reversion; a leader-move-driven cross-asset catch-up, conditioned on the leader not the follower's panic.",
    "intraweek_calendar_seasonality_drift": "A market-EVENT trigger (a confirmed leader move), never a date/weekday; directly avoids C10's calendar + long-drift trap, with must-beat-buy-and-hold forbidding drift in disguise.",
    "cross_asset_dispersion_reversion": "OPPOSITE cross-asset thesis: C11 buys the relative LAGGARD betting on REVERSION toward the basket; C13 buys the FOLLOWER betting the LEADER's move PROPAGATES (continuation). Single-leader directed trigger vs cross-sectional z ranking; continuation vs reversion.",
    "failed_breakdown_reclaim_reversal": "Not a single-asset structural reclaim event and not mean-reversion; a cross-asset directional-causality (leader->follower) continuation, and it carries the C12 must-beat-RANDOM-ENTRY + target-capture-dominance gates from the start.",
}

C10_C11_C12_LESSONS_APPLIED = (
    "C10 lesson: never a calendar/weekday trigger; regime symmetry + forward-OOS "
    "continuation are mandatory and validated EARLY.",
    "C11 lesson: strong labels are NECESSARY BUT NOT SUFFICIENT -- forward-OOS "
    "continuation and bull/bear/chop net symmetry are HARD replay-stage gates.",
    "C12 lesson: the must-beat-RANDOM-ENTRY baseline is the decisive anti-edge "
    "filter; the entry signal must add value over random timing, target capture "
    "must dominate horizon exits, and the edge must beat a matched buy-and-hold "
    "(no bull-carry reliance).",
    "C13-specific consequence: add a beat-the-LEADER (buy-the-leader-instead / "
    "follower-own-momentum) baseline so the demonstrated edge is the cross-asset "
    "DIFFUSION, not generic strength -- enforced early as a structural rejection.",
)

# THE HARD RULE that operationalizes the C10 + C11 + C12 lessons for C13.
HARD_RULE_EARLY_GENERALIZATION_AND_ANTI_DRIFT = (
    "Candidate #13 MUST pass an EARLY battery at the labels/replay stage, BEFORE "
    "robustness and BEFORE any promotion: (1) FORWARD-OOS continuation (net "
    "positive after honest costs in a sealed forward window); (2) CROSS-REGIME "
    "SYMMETRY (net-positive, or at minimum non-negative, in bull AND bear AND "
    "chop); (3) CROSS-ASSET (must hold on more than one FOLLOWER, e.g. ETH AND "
    "SOL); (4) MUST BEAT a matched BUY-AND-HOLD AND a matched RANDOM-ENTRY "
    "baseline over the same dates; (5) TARGET-CAPTURE DOMINANCE (horizon-exit "
    "share below a pre-registered cap); and (6) MUST BEAT a BUY-THE-LEADER / "
    "follower-own-momentum baseline (the cross-asset diffusion must add value "
    "over generic strength). Failing ANY is a STRUCTURAL REJECTION, not a "
    "warning.")

ANTI_TRAP_FILTERS = (
    "REJECT if the edge is explained by generic bullish long-drift / market "
    "carry (must beat matched buy-and-hold AND be regime-symmetric).",
    "REJECT if it is worse than (or not better than) a matched RANDOM-ENTRY "
    "baseline -- the direct C12 failure mode; the leader-move SIGNAL must add "
    "timing value.",
    "REJECT if it is just generic strength: it must beat a BUY-THE-LEADER / "
    "follower-own-momentum baseline, else the cross-asset diffusion is not the "
    "edge.",
    "REJECT if the result is horizon/drift dominated (horizon-exit share above "
    "the pre-registered cap; target capture must dominate).",
    "REJECT if the edge does not continue in forward-OOS (required early).",
    "REJECT if it depends on a single follower (cross-asset required) or on any "
    "weekday/calendar date (no date/weekday trigger permitted).",
    "PENALIZE thin per-trade net edge and fee/slippage fragility before any "
    "robustness run.",
)

DATA_NEEDS = {
    "leader_asset": "BTC",
    "follower_assets": ["ETH", "SOL"],
    "assets_required_minimum": ["BTC", "ETH", "SOL"],
    "assets_preferred_future": ["BTC", "ETH", "SOL", "plus additional majors as "
                                "followers (separately authorized fetch)"],
    "timeframe": "1d",
    "market_type": "spot",
    "fields_required": ["open", "high", "low", "close"],
    "already_on_disk_frozen": ["data/crypto_d1_spot/raw/BTC_1d.csv",
                               "data/crypto_d1_spot/raw/ETH_1d.csv",
                               "data/crypto_d1_spot/raw/SOL_1d.csv"],
    "new_fetch_needed_for_initial_research": False,
    "wider_follower_set_needs_separate_authorized_fetch": True,
}
LEADER = "BTCUSD"
FOLLOWERS = ("ETHUSD", "SOLUSD")
SYMBOLS = ("BTCUSD", "ETHUSD", "SOLUSD")
TIMEFRAME = "1d"
DIRECTION = "long_only"
DIRECTION_NOTE = ("long-only research labels on the follower's catch-up; never a "
                  "short/borrow leg and never a trading capability")

ENTRY_CONCEPT = (
    "On each daily close, compute the LEADER's (BTC) k-day return and its "
    "pre-registered z-score. A CONFIRMED leader move requires that z-score >= a "
    "pre-registered POSITIVE threshold AND the FOLLOWER (ETH or SOL) has NOT yet "
    "matched it (the follower's same-window return lags the leader by a "
    "pre-registered margin). Enter the follower LONG at that close. Weekday is "
    "irrelevant by design; the trigger asset differs from the traded asset.")
EXIT_CONCEPT = (
    "Pre-registered SHORT fixed horizon (e.g. 1-2 daily bars) OR a pre-registered "
    "R-multiple target, whichever first; the horizon is a human-fixed, disclosed "
    "assumption (NOT optimized after results). Target capture must dominate -- a "
    "high horizon-exit share is a structural rejection.")
RISK_GEOMETRY = {
    "stop": "ATR(14)-based structure stop on the FOLLOWER, pre-registered "
            "multiplier; INVALID if stop not below entry; never tightened "
            "post-hoc.",
    "targets": "pre-registered R-multiples (e.g. 1R/1.5R/2R); no new variants "
               "after label freeze; a gross target-distance floor in bps.",
    "costs": "taker fees + conservative slippage modeled honestly (inherits the "
             "C10/C11/C12 37 bps all-in discipline) before any PASS.",
    "sizing": "equal-weight / fixed-fraction research sizing only; NO leverage; "
              "NO shorting; NO portfolio compute.",
}

EARLY_GENERALIZATION_CHECKS = (
    "forward_oos_continuation_required_early",
    "cross_regime_bull_bear_chop_symmetry_required_early",
    "cross_asset_multiple_followers_required_early",
    "beats_buy_and_hold_and_random_entry_baseline_required_early",
    "target_capture_dominates_horizon_exit_share_capped_required_early",
    "beats_buy_the_leader_or_follower_momentum_baseline_required_early",
)
PROMOTION_TO_HUMAN_REVIEW_CONDITIONS = (
    "passes the EARLY generalization + anti-drift battery before robustness",
    "net-positive after honest fees + slippage with adequate sample",
    "regime-symmetric (not explained by long-drift / bull carry)",
    "beats a matched buy-and-hold AND random-entry baseline on the same dates",
    "beats a buy-the-leader / follower-own-momentum baseline (diffusion, not "
    "generic strength)",
    "target-capture dominated (horizon-exit share below the pre-registered cap)",
    "continues in forward-OOS",
    "no single-follower / weekday / calendar dependence",
    "every gate human-reviewed; the human decides",
)

C13P_LABEL = (
    "SPARTA Candidate #13 Family Proposal (READ-ONLY, RESEARCH ONLY). "
    "lead_lag_propagation_continuation: go long a FOLLOWER (ETH/SOL) when the "
    "LEADER (BTC) posts a confirmed large move the follower has not yet matched, "
    "betting the move PROPAGATES (a cross-asset diffusion timing edge, NOT "
    "reversion, ranking, calendar, or same-asset trend). MATERIALLY DIFFERENT "
    "FROM C1-C12. PROPOSAL ONLY -- NO DETECTOR, NO LABELS, NO REPLAY, NO TRADING. "
    "FORWARD-OOS + REGIME SYMMETRY + MUST-BEAT-BUY&HOLD + MUST-BEAT-RANDOM + "
    "MUST-BEAT-LEADER + TARGET-CAPTURE-DOMINANCE ARE HARD GATES FROM THE START."
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


def get_candidate_13_family_proposal_label() -> str:
    return C13P_LABEL


def get_candidate_13_family_proposal_next_action() -> str:
    return NEXT_REQUIRED_ACTION


def build_candidate_13_family_proposal(repo_root: Any = ".",
                                       tracked_paths: list | None = None
                                       ) -> dict[str, Any]:
    """Assemble the Candidate #13 family proposal. Chain-gated on the closed
    C12 rejection record. Pure; no I/O; proposal only."""
    record: dict[str, Any] = {
        "schema_version": C13P_SCHEMA_VERSION,
        "label": C13P_LABEL, "mode": C13P_MODE,
        "lane": "crypto_d1_auto_research",
        "candidate_number": CANDIDATE_NUMBER,
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "verdict": None, "blockers": [],
        "head_at_c12_rejection": HEAD_AT_C12_REJECTION,
        "clean_hypothesis": CLEAN_HYPOTHESIS,
        "edge_source_hypothesis": EDGE_SOURCE_HYPOTHESIS,
        "rejected_families_c1_to_c12": list(REJECTED_FAMILIES_C1_TO_C12),
        "material_difference_from_each_rejected":
            dict(MATERIAL_DIFFERENCE_FROM_EACH_REJECTED),
        "c10_c11_c12_lessons_applied": list(C10_C11_C12_LESSONS_APPLIED),
        "hard_rule_early_generalization_and_anti_drift":
            HARD_RULE_EARLY_GENERALIZATION_AND_ANTI_DRIFT,
        "anti_trap_filters": list(ANTI_TRAP_FILTERS),
        "data_needs": dict(DATA_NEEDS),
        "leader": LEADER, "followers": list(FOLLOWERS),
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
    # must differentiate from EVERY rejected family C1-C12.
    if CANDIDATE_FAMILY in REJECTED_FAMILIES_C1_TO_C12:
        record["verdict"] = VERDICT_C13P_BLOCKED
        record["blockers"].append("proposed_family_is_a_rejected_family")
        return record
    missing = [f for f in REJECTED_FAMILIES_C1_TO_C12
               if f not in MATERIAL_DIFFERENCE_FROM_EACH_REJECTED]
    if missing:
        record["verdict"] = VERDICT_C13P_BLOCKED
        record["blockers"].append("differentiation_missing_for_some_rejected")
        return record

    rej = build_c12_rejection_record(repo_root, tracked_paths or [])
    record["c12_rejection_status"] = rej.get("rejection_status")
    if rej.get("rejection_status") != C12_REJECTION_STATUS:
        record["verdict"] = VERDICT_C13P_BLOCKED
        record["blockers"].append("c12_not_closed_on_record")
        return record

    record["verdict"] = VERDICT_C13P_READY
    return record


def validate_candidate_13_family_proposal(record: dict[str, Any]
                                          ) -> dict[str, Any]:
    """Anti-tamper validator. READY is valid only when the proposal is
    materially new, differentiates from every rejected family C1-C12, carries
    the hard early-generalization + anti-drift rule (incl. the must-beat-random-
    entry, must-beat-buy-and-hold, must-beat-leader, and target-capture gates),
    and locks all execution / downstream gates."""
    failures: list = []
    if record.get("verdict") != VERDICT_C13P_READY:
        failures.append("verdict_not_ready")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("mode") != C13P_MODE:
        failures.append("mode_not_research_only")
    if record.get("candidate_family") != CANDIDATE_FAMILY:
        failures.append("candidate_family_tampered")
    if record.get("candidate_number") != 13:
        failures.append("candidate_number_tampered")

    # Materially new + full differentiation across C1-C12.
    if record.get("is_materially_new_family") is not True:
        failures.append("not_marked_materially_new")
    if record.get("candidate_family") in (
            record.get("rejected_families_c1_to_c12") or []):
        failures.append("proposed_family_is_rejected_family")
    diff = record.get("material_difference_from_each_rejected") or {}
    for f in (record.get("rejected_families_c1_to_c12") or []):
        if not diff.get(f):
            failures.append("differentiation_missing_%s" % f)
    if record.get("c12_rejection_status") != "REJECTED_KEPT_ON_RECORD":
        failures.append("c12_rejection_status_tampered")

    # The hard early-generalization + anti-drift rule + checks must be present.
    if not record.get("hard_rule_early_generalization_and_anti_drift"):
        failures.append("hard_early_generalization_rule_missing")
    for chk in ("forward_oos_continuation_required_early",
                "cross_regime_bull_bear_chop_symmetry_required_early",
                "cross_asset_multiple_followers_required_early",
                "beats_buy_and_hold_and_random_entry_baseline_required_early",
                "target_capture_dominates_horizon_exit_share_capped_required_early",
                "beats_buy_the_leader_or_follower_momentum_baseline_required_early"):
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
