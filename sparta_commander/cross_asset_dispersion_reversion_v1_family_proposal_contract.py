"""SPARTA Candidate #11 family proposal: cross_asset_dispersion_reversion_v1.

PROPOSAL ONLY. RESEARCH ONLY. This contract proposes a NEW strategy family for
the Strategy Factory after Candidate #10 was closed REJECTED_KEPT_ON_RECORD. It
is pure and in-memory: NO detector, NO labels, NO replay, NO robustness, NO
generalization run, NO data fetch, NO trading, NO portfolio compute, NO
downstream gate unlock. It only proposes a hypothesis + differentiation +
research plan for human review.

Chain gate: build_candidate_11_family_proposal() requires
build_c10_rejection_record() to return REJECTED_KEPT_ON_RECORD -- C11 may only
open once C10 is formally closed on the ledger.

THE C10 LESSON (applied as a HARD rule here):
  C10 passed labels, cost-honest replay, and robustness, then FAILED the final
  cross-asset/cross-weekday/forward-OOS generalization gate -- its apparent
  Friday edge was undifferentiated bullish LONG-DRIFT, not a real anomaly, and
  the failure was only caught at the LAST gate. C11 therefore (a) uses a
  RELATIVE / cross-sectional edge (not generic long-drift), and (b) MANDATES
  early generalization validation (cross-weekday-neutrality, cross-asset,
  forward-OOS, cross-regime) at the LABELS/REPLAY stage, BEFORE any robustness
  or promotion -- so a drift artifact is caught early, not at the end.
"""
from __future__ import annotations

from typing import Any

from sparta_commander.intraweek_calendar_seasonality_drift_v1_rejection_record_contract import (  # noqa: E501
    REJECTION_STATUS as C10_REJECTION_STATUS,
    build_c10_rejection_record,
)

C11P_SCHEMA_VERSION = 1
C11P_MODE = "RESEARCH_ONLY"
CANDIDATE_NUMBER = 11
CANDIDATE_FAMILY = "cross_asset_dispersion_reversion"
CANDIDATE_ID = "CROSS_ASSET_DISPERSION_REVERSION_V1"

VERDICT_C11P_READY = "CANDIDATE_11_FAMILY_PROPOSAL_READY"
VERDICT_C11P_BLOCKED = "CANDIDATE_11_FAMILY_PROPOSAL_BLOCKED"
NEXT_REQUIRED_ACTION = "HUMAN_DECISION_C11_ADVANCE_TO_SPEC_OR_REJECT_PROPOSAL"

HEAD_AT_C10_REJECTION = "1ddfb49b433b4849c85ceb7550960ca5330b5b95"

# Full C1-C10 rejected-family ledger (every version string).
REJECTED_FAMILIES_C1_TO_C10 = (
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
    "intraweek_calendar_seasonality_drift",   # C10
)

CLEAN_HYPOTHESIS = (
    "When the daily returns of the major crypto majors disperse abnormally -- "
    "one major lags the cross-sectional median by an extreme negative z-score "
    "while the basket is not in a confirmed downtrend regime -- the relative "
    "LAGGARD tends to revert toward the basket over a short horizon. The signal "
    "is RELATIVE (cross-sectional), not a directional bet on the market going "
    "up.")
EDGE_SOURCE_HYPOTHESIS = (
    "Cross-sectional dispersion reversion / lead-lag catch-up among highly "
    "correlated majors: idiosyncratic single-name lag inside a co-moving "
    "basket partially mean-reverts. The edge source is the relative spread, "
    "which exists in up, down, and chop regimes -- it is NOT undifferentiated "
    "long-drift.")

# Why C11 is materially different from EACH rejected family (C1-C10).
MATERIAL_DIFFERENCE_FROM_EACH_REJECTED = {
    "ny_session_fvg_choch": "No price-structure (FVG/CHoCH) pattern; the trigger is a cross-sectional return z-score, not an intraday structural event.",
    "ny_session_fvg_choch_v3": "Same: no structural-pattern trigger; cross-asset statistic instead, daily not intraday-session.",
    "crypto_intraday_breakout_pullback_structure": "No breakout or pullback; the entry is a relative-laggard reversion, not a continuation of a breakout.",
    "crypto_intraday_breakout_pullback_structure_v2": "Same: no breakout-pullback geometry; cross-sectional reversion signal.",
    "long_biased_trend_continuation": "NOT a directional long-bias / trend-continuation edge; the signal is relative (laggard vs basket) and is the core C10 trap this family explicitly avoids.",
    "btc_sol_long_trend_continuation_v1": "Same: not absolute trend continuation; relative cross-sectional reversion.",
    "long_1h_swing_structure": "No swing-structure pattern and not 1h; daily cross-sectional dispersion statistic.",
    "sol_btc_long_1h_swing_structure": "Same: no swing structure; daily cross-asset reversion.",
    "eth_sol_relative_strength_pullback_continuation": "OPPOSITE relative-signal direction: RS families buy the STRONGEST (continuation); C11 buys the relative LAGGARD (reversion).",
    "eth_sol_relative_strength_pullback_continuation_v1": "Same: reversion of the laggard, not continuation of the leader.",
    "multi_symbol_relative_strength_rotation_filter": "Rotation buys leaders/momentum; C11 is reversion of the dispersion spread (laggard catch-up), the opposite mechanism.",
    "volatility_compression_expansion": "Trigger is cross-sectional return DISPERSION across assets, not a single-asset volatility-band compression/expansion.",
    "liquidity_sweep_mean_reversion": "Reverts a CROSS-SECTIONAL relative-lag z-score, not an absolute single-asset liquidity-sweep wick; inherently multi-asset.",
    "low_volume_downside_capitulation_mean_reversion": "Uses relative-to-basket oversold (z vs peers), NOT absolute single-asset capitulation/volume; conditioned on basket regime, not single-name panic.",
    "intraweek_calendar_seasonality_drift": "Trigger is a market-STATE condition (cross-sectional dispersion), never a calendar date/weekday; inherently cross-asset, directly avoiding C10's calendar + single-asset/single-weekday + long-drift traps.",
}

C10_LESSON_APPLIED = (
    "C10 was undifferentiated long-drift dressed as a calendar edge and only "
    "failed at the final generalization gate; C11's edge is RELATIVE / "
    "cross-sectional (regime-symmetric by construction), and generalization is "
    "validated EARLY, not deferred.",
    "Do not trust simple calendar/long-drift edges; require cross-weekday, "
    "cross-asset, and forward-OOS generalization before belief.",
)

# THE HARD RULE that operationalizes the C10 lesson for C11.
HARD_RULE_EARLY_GENERALIZATION = (
    "Candidate #11 MUST pass an EARLY generalization battery -- cross-weekday "
    "NEUTRALITY (the edge must NOT depend on any specific weekday), cross-asset "
    "(must hold on multiple laggards, not one asset), forward-OOS continuation, "
    "and cross-regime stability (bull / bear / chop) -- at the LABELS/REPLAY "
    "stage, BEFORE robustness and BEFORE any promotion consideration. Failing "
    "any early-generalization check is a STRUCTURAL REJECTION, not a warning.")

ANTI_TRAP_FILTERS = (
    "REJECT if the edge is explained by generic bullish long-drift (test: "
    "regime-symmetry across bull/bear/chop must hold).",
    "REJECT if the edge depends on a single asset or a single weekday "
    "(test: cross-asset + cross-weekday-neutrality required early).",
    "REJECT if the edge is a calendar/seasonality artifact (no date/weekday "
    "trigger permitted).",
    "REJECT if the edge does not continue in forward-OOS (forward continuation "
    "required early, not at the end).",
    "PENALIZE thin per-trade net edge and fee/slippage fragility before any "
    "robustness run.",
)

DATA_NEEDS = {
    "assets_required_minimum": ["BTC", "ETH", "SOL"],
    "assets_preferred_future": ["BTC", "ETH", "SOL", "plus additional majors "
                                "for a wider cross-section (separately "
                                "authorized fetch)"],
    "timeframe": "1d",
    "market_type": "spot",
    "already_on_disk_frozen": ["data/crypto_d1_spot/raw/BTC_1d.csv",
                               "data/crypto_d1_spot/raw/ETH_1d.csv",
                               "data/crypto_d1_spot/raw/SOL_1d.csv"],
    "new_fetch_needed_for_initial_research": False,
    "wider_cross_section_needs_separate_authorized_fetch": True,
}
SYMBOLS = ("BTCUSD", "ETHUSD", "SOLUSD")
TIMEFRAME = "1d"
DIRECTION = "long_only"
DIRECTION_NOTE = ("long-only research labels on the relative laggard; never a "
                  "trading capability and never a short/borrow leg")

ENTRY_CONCEPT = (
    "On each daily close, compute each major's recent return (e.g. k-day) and "
    "its cross-sectional z-score vs the basket. ENTER LONG the relative laggard "
    "when its z-score <= a pre-registered negative threshold AND the basket is "
    "NOT in a confirmed downtrend regime. The weekday is irrelevant by design.")
EXIT_CONCEPT = (
    "Pre-registered short fixed horizon (e.g. 3-5 daily bars) OR reversion to "
    "the basket median, whichever first; never re-optimized after seeing "
    "results.")
RISK_GEOMETRY = {
    "stop": "ATR(14)-based structure stop, pre-registered multiplier; never "
            "tightened post-hoc.",
    "targets": "pre-registered R-multiples (e.g. 1.5R/2R/3R); no new variants "
               "after label freeze.",
    "costs": "taker fees + conservative slippage modeled honestly before any "
             "PASS (inherits the C10 cost-honesty discipline).",
    "sizing": "equal-weight / fixed-fraction research sizing only; NO portfolio "
              "compute, NO leverage, NO shorting.",
}

EARLY_GENERALIZATION_CHECKS = (
    "cross_weekday_neutrality_required_early",
    "cross_asset_multiple_laggards_required_early",
    "forward_oos_continuation_required_early",
    "cross_regime_bull_bear_chop_stability_required_early",
)
PROMOTION_TO_HUMAN_REVIEW_CONDITIONS = (
    "passes the EARLY generalization battery before robustness",
    "net-positive after honest fees + slippage with adequate sample",
    "regime-symmetric (not explained by long-drift)",
    "no single-asset / single-weekday dependence",
    "every gate human-reviewed; the human decides",
)

C11P_LABEL = (
    "SPARTA Candidate #11 Family Proposal (READ-ONLY, RESEARCH ONLY). "
    "cross_asset_dispersion_reversion: buy the relative LAGGARD on extreme "
    "cross-sectional dispersion (a RELATIVE, regime-symmetric reversion signal, "
    "NOT long-drift). MATERIALLY DIFFERENT FROM C1-C10. PROPOSAL ONLY -- NO "
    "DETECTOR, NO LABELS, NO REPLAY, NO TRADING. EARLY GENERALIZATION VALIDATION "
    "IS MANDATORY BEFORE ANY PROMOTION."
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
    "is_a_rescue_attempt", "authorizes_paper_execution",
    "authorizes_micro_live", "authorizes_live_trading", "promotes_gate",
    "unlocks_downstream_gate", "claims_profitability", "claims_edge",
    "executes", "writes_files",
)


def get_candidate_11_family_proposal_label() -> str:
    return C11P_LABEL


def get_candidate_11_family_proposal_next_action() -> str:
    return NEXT_REQUIRED_ACTION


def build_candidate_11_family_proposal(repo_root: Any = ".",
                                       tracked_paths: list | None = None
                                       ) -> dict[str, Any]:
    """Assemble the Candidate #11 family proposal. Chain-gated on the closed
    C10 rejection record. Pure; no I/O; proposal only."""
    record: dict[str, Any] = {
        "schema_version": C11P_SCHEMA_VERSION,
        "label": C11P_LABEL, "mode": C11P_MODE,
        "lane": "crypto_d1_auto_research",
        "candidate_number": CANDIDATE_NUMBER,
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "verdict": None, "blockers": [],
        "head_at_c10_rejection": HEAD_AT_C10_REJECTION,
        "clean_hypothesis": CLEAN_HYPOTHESIS,
        "edge_source_hypothesis": EDGE_SOURCE_HYPOTHESIS,
        "rejected_families_c1_to_c10": list(REJECTED_FAMILIES_C1_TO_C10),
        "material_difference_from_each_rejected":
            dict(MATERIAL_DIFFERENCE_FROM_EACH_REJECTED),
        "c10_lesson_applied": list(C10_LESSON_APPLIED),
        "hard_rule_early_generalization": HARD_RULE_EARLY_GENERALIZATION,
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
        "no_profitability_claim": True, "no_downstream_gate_unlock": True,
    }

    # The proposed family must be MATERIALLY NEW (not a rejected family) and
    # must differentiate from EVERY rejected family.
    if CANDIDATE_FAMILY in REJECTED_FAMILIES_C1_TO_C10:
        record["verdict"] = VERDICT_C11P_BLOCKED
        record["blockers"].append("proposed_family_is_a_rejected_family")
        return record
    missing = [f for f in REJECTED_FAMILIES_C1_TO_C10
               if f not in MATERIAL_DIFFERENCE_FROM_EACH_REJECTED]
    if missing:
        record["verdict"] = VERDICT_C11P_BLOCKED
        record["blockers"].append("differentiation_missing_for_some_rejected")
        return record

    rej = build_c10_rejection_record(repo_root, tracked_paths or [])
    record["c10_rejection_status"] = rej.get("rejection_status")
    if rej.get("rejection_status") != C10_REJECTION_STATUS:
        record["verdict"] = VERDICT_C11P_BLOCKED
        record["blockers"].append("c10_not_closed_on_record")
        return record

    record["verdict"] = VERDICT_C11P_READY
    return record


def validate_candidate_11_family_proposal(record: dict[str, Any]
                                          ) -> dict[str, Any]:
    """Anti-tamper validator. READY is valid only when the proposal is
    materially new, differentiates from every rejected family, carries the hard
    early-generalization rule, and locks all execution / downstream gates."""
    failures: list = []
    if record.get("verdict") != VERDICT_C11P_READY:
        failures.append("verdict_not_ready")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("mode") != C11P_MODE:
        failures.append("mode_not_research_only")
    if record.get("candidate_family") != CANDIDATE_FAMILY:
        failures.append("candidate_family_tampered")
    if record.get("candidate_number") != 11:
        failures.append("candidate_number_tampered")

    # Materially new + full differentiation.
    if record.get("is_materially_new_family") is not True:
        failures.append("not_marked_materially_new")
    if record.get("candidate_family") in (
            record.get("rejected_families_c1_to_c10") or []):
        failures.append("proposed_family_is_rejected_family")
    diff = record.get("material_difference_from_each_rejected") or {}
    for f in (record.get("rejected_families_c1_to_c10") or []):
        if not diff.get(f):
            failures.append("differentiation_missing_%s" % f)
    if record.get("c10_rejection_status") != "REJECTED_KEPT_ON_RECORD":
        failures.append("c10_rejection_status_tampered")

    # The hard early-generalization rule + checks must be present.
    if not record.get("hard_rule_early_generalization"):
        failures.append("hard_early_generalization_rule_missing")
    for chk in ("cross_weekday_neutrality_required_early",
                "cross_asset_multiple_laggards_required_early",
                "forward_oos_continuation_required_early",
                "cross_regime_bull_bear_chop_stability_required_early"):
        if chk not in (record.get("early_generalization_checks") or []):
            failures.append("early_generalization_check_missing_%s" % chk)

    # Proposal-only posture.
    if record.get("is_proposal_only") is not True:
        failures.append("not_proposal_only")
    if record.get("is_a_rescue_attempt") is not False:
        failures.append("rescue_attempt_flag_tampered")

    locks = record.get("scope_locks") or {}
    for key in ("no_detector", "no_labels", "no_replay", "no_data_fetch",
                "no_paper_trading", "no_live_trading", "no_portfolio_compute",
                "no_calendar_trigger", "no_weekday_trigger",
                "no_rescue_of_rejected_geometry"):
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
