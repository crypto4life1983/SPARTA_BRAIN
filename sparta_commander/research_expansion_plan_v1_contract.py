"""SPARTA Research Expansion Plan v1 -- PURE PLANNER / SPEC.

RESEARCH ONLY. This contract is a PURE, in-memory PLAN + DECISION layer for
running MORE candidate families FASTER while preserving every safety lock. It
DECLARES the max-automation research-expansion plan (the frozen gate sequence,
priority scoring, overnight batching protocol, anti-loop protection, and the
portfolio-level objective) and provides PURE scoring / ranking / batch-planning
functions over DECLARED candidate-idea metadata.

It does NOTHING else: it does NOT build candidate files, NOT write files, NOT run
any detector / labels / replay / robustness / portfolio compute, NOT fetch data,
NOT read real data, NOT stage / commit / push, and NOT touch any paper / live /
broker / credential / order surface. Every capability flag is pinned False and a
full scope_locks set is attached, so "more speed, same safety" is STRUCTURAL --
there is no execution capability here at all. Building the selected idea, and any
commit / push, STILL require explicit human approval at each existing gate.

THE GATE SEQUENCE IS PRESERVED UNCHANGED (each stage human-gated):
  proposal -> spec -> detector_dry_run -> real_candle_labels ->
  fee_honest_replay -> rejection_or_promote_decision

THE C14 LESSON IS OPERATIONALIZED IN THE PRIORITY SCORE: conviction-bar timing
had a real signal vs random-entry but FAILED buy-and-hold and forward-OOS. So the
score weights a DURABILITY proxy (expected to beat buy-and-hold AND continue in
forward-OOS) far above a TIMING proxy (beats random-entry) -- beating random is
necessary but NOT sufficient.
"""
from __future__ import annotations

from typing import Any

REP_SCHEMA_VERSION = 1
REP_MODE = "RESEARCH_ONLY"

# --- the preserved, frozen gate sequence (each stage human-gated) -----------
GATE_SEQUENCE = (
    "family_proposal",
    "candidate_spec",
    "detector_spec_dry_run",
    "real_candle_labels_review",
    "fee_honest_replay_review",
    "rejection_or_promote_decision",
)
HUMAN_GATED_STAGES = tuple(GATE_SEQUENCE)
REAL_DATA_STAGES = ("real_candle_labels_review", "fee_honest_replay_review")

# --- full C1-C14 rejected/closed ledger (learning data; never re-proposed) --
REJECTED_FAMILIES_C1_TO_C14 = (
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
    "conviction_bar_follow_through",               # C14
)

# --- the CURRENT canonical rejected ledger (C1-C15; used for FORWARD anti-loop).
# The C1-C14 tuple above is kept FROZEN because the (already pushed) C15 chain +
# tournament proposal legitimately reference it as it was when C15 was still an
# open candidate. New proposals must use this 20-family ledger so C15 is never
# re-proposed.
REJECTED_FAMILIES_C1_TO_C15 = REJECTED_FAMILIES_C1_TO_C14 + (
    "slow_vol_targeted_time_series_momentum",      # C15
)

# --- the CURRENT canonical rejected ledger (C1-C16; used for FORWARD anti-loop).
# The C1-C15 tuple above is kept FROZEN because the (already pushed) C16 chain
# legitimately references it as it was when C16 was still an open candidate. New
# proposals must use this 21-family ledger so C16 is never re-proposed.
REJECTED_FAMILIES_C1_TO_C16 = REJECTED_FAMILIES_C1_TO_C15 + (
    "cointegration_pairs_market_neutral",          # C16
)

# --- the CURRENT canonical rejected ledger (C1-C17; 22 families). The C1-C16 tuple
# above is kept FROZEN because the (already pushed) C16 AND C17 chains legitimately
# reference it as it was while C17 was still an open candidate (count 21). New
# proposals must use this 22-family ledger so C17 is never re-proposed. C17
# (risk-adjusted portfolio construction) was REJECTED at the fee-honest replay
# stage: it failed to beat SOL buy-and-hold and the equal-weight basket on Sharpe /
# Calmar and its 2026 forward-OOS edge did not hold -- lower drawdown alone is not
# enough.
REJECTED_FAMILIES_C1_TO_C17 = REJECTED_FAMILIES_C1_TO_C16 + (
    "risk_adjusted_portfolio_construction_vol_targeted_allocation",   # C17
)

# --- the CURRENT canonical rejected ledger (C1-C18; 23 families). The C1-C17 tuple
# above is kept FROZEN because the (already pushed) C17 AND C18 chains legitimately
# reference it as it was while C18 was still an open candidate (count 22). New
# proposals must use this 23-family ledger so C18 is never re-proposed. C18 (H4
# market-structure trend-following) was REJECTED at the fee-honest replay stage: it
# made +95.4% but failed BTC buy-and-hold risk-adjusted (Sharpe 0.52 vs 0.93, Calmar
# 0.25 vs 0.60) and its 2026 forward-OOS edge did not hold -- lower drawdown alone is
# not enough. (This rejects the objective C18 approximation, not the observed
# trader's exact private system.)
REJECTED_FAMILIES_C1_TO_C18 = REJECTED_FAMILIES_C1_TO_C17 + (
    "h4_trend_following_market_structure",   # C18
)

# --- the CURRENT canonical rejected ledger (C1-C19; 24 families). The C1-C18 tuple
# above is kept FROZEN because the (already pushed) C19 chain references it as it was
# while C19 was still an open candidate (count 23). New proposals must use this
# 24-family ledger so C19 is never re-proposed. C19 (OOS-validated beta-neutral
# cross-sectional relative value) was REJECTED at the real-candle labels / neutrality
# gate: only 41 tradeable entries (< 100 structural sample gate) and OOS beta-
# neutrality held on only 862/1977 bars (~44%) -- echoing the C16 failure that
# neutrality does not persist out of sample; no fee-honest replay was run.
REJECTED_FAMILIES_C1_TO_C19 = REJECTED_FAMILIES_C1_TO_C18 + (
    "oos_validated_beta_neutral_cross_sectional_relative_value",   # C19
)

# --- the CURRENT canonical rejected ledger (C1-C20; 25 families). The C1-C19 tuple
# above is kept FROZEN because the (already pushed) C20 chain references it as it was
# while C20 was still an open candidate (count 24). New proposals must use this
# 25-family ledger so C20 is never re-proposed. C20 (mechanically-neutral spot/perp
# basis + funding carry) was REJECTED at the fee-honest replay stage: applying the
# reserved 37 bps all-in cost PER LEG (74 bps round-trip per trade, two legs) to the
# 704 frozen trades produced a portfolio net -74.5% (Sharpe -12.84, Calmar -0.285,
# max DD -74.5%) and the 2026 forward-OOS failed (net -8.3%, Sharpe -12.2, 0% win
# rate). All four decisive gates failed; it lost badly vs the random/null always-on
# neutral-carry baseline (+21.2%, Sharpe 1.09). The mechanically-neutral CARRY itself
# is real -- the always-on null is positive (BTC/ETH funding) -- so this rejects the
# C20 entry/exit TIMING, whose 704 round-trips x 74 bps = 521% cost drag destroyed the
# carry, NOT the same-asset carry thesis. A low-turnover always-on carry would be a
# SEPARATE future candidate only under explicit human approval.
REJECTED_FAMILIES_C1_TO_C20 = REJECTED_FAMILIES_C1_TO_C19 + (
    "mechanically_neutral_spot_perp_basis_funding_carry",   # C20
)

# --- the CURRENT canonical rejected ledger (C1-C21; 26 families). The C1-C20 tuple
# above is kept FROZEN because the (already pushed) C21 chain references it as it was
# while C21 was still an open candidate (count 25). New proposals must use this
# 26-family ledger so C21 is never re-proposed. C21 (low-turnover same-asset spot/perp
# funding carry) was REJECTED at the fee-honest replay stage: unlike C20 the LOW-TURNOVER
# design WORKED (20 trades, cost drag 14.8%, net +20.2% / Sharpe 1.05 vs C20's -74.5%),
# but it does NOT beat the trivial always-on neutral-carry null (+21.2%, Sharpe 1.09) and
# the 2026 forward-OOS fails (strategy -1.0%, null -0.5%); 2 of 4 decisive gates pass and
# the two decisive market-neutral gates (beats-null, forward-OOS) fail. The SPARTA
# Pipeline Audit v1 cross-checks all pass, so this is an EDGE-driven rejection, not a
# fee/funding/lookahead/duplicate/alignment artifact. The carry SOURCE is real but free
# (it is the null) and OOS-fragile; the detector timing adds no edge. The always-on carry
# itself would be a SEPARATE future candidate only under explicit human approval.
REJECTED_FAMILIES_C1_TO_C21 = REJECTED_FAMILIES_C1_TO_C20 + (
    "low_turnover_same_asset_spot_perp_funding_carry",   # C21
)

# --- learning data distilled from C1-C16 (why each broad mechanism failed) ---
REJECTED_FAMILY_LESSONS = {
    "calendar_seasonality": "C10: undifferentiated long-drift dressed as a "
                            "Friday calendar edge; never a date/weekday trigger.",
    "cross_sectional_reversion": "C11: strong labels but forward-OOS negative + "
                                 "bear-weak; labels necessary not sufficient.",
    "single_asset_reclaim_reversion": "C12: net-negative after costs and WORSE "
                                      "than random entry; horizon/drift dominated.",
    "cross_asset_lead_lag": "C13: too RARE (41 labels) -> structural rejection at "
                            "the labels sample-size gate, before replay.",
    "single_bar_conviction_continuation":
        "C14: BEAT random-entry (real timing signal) but LOST to buy-and-hold "
        "and FAILED forward-OOS -- a timing signal is not a durable edge.",
    "slow_time_series_momentum_carry":
        "C15: net-positive and BEAT random-entry, but LOST to buy-and-hold with a "
        "net-negative bear regime and short side -- long-bull crypto carry that "
        "underperforms buy-and-hold is not a durable edge.",
    "cointegration_pairs_market_neutral":
        "C16: market-neutrality avoided the C14/C15 carry trap, but crypto-D1 "
        "cointegration is too INTERMITTENT (43 labels < 100) and a level-OLS hedge "
        "is not return-beta-neutral out of sample (net beta 2.82 > 0.10) -- "
        "rejected at the labels stage before replay.",
    "risk_adjusted_portfolio_construction_vol_targeted_allocation":
        "C17: vol-targeted / risk-parity allocation cleared the labels structural "
        "gate (well-formed, long-only, gross-capped, low-turnover) but was rejected "
        "at fee-honest replay -- it cut max drawdown to -37.8% yet did NOT beat SOL "
        "buy-and-hold (Sharpe 0.80 vs 1.08, Calmar 0.47 vs 0.83) or the equal-weight "
        "basket (Sharpe 0.80 vs 1.04) on a RISK-ADJUSTED basis and the 2026 "
        "forward-OOS edge did not hold; in a crypto bull, de-risking away from the "
        "biggest winner lowers risk-adjusted return -- lower drawdown alone is not "
        "an edge over simply holding the basket.",
    "h4_trend_following_market_structure":
        "C18: H4 market-structure trend-following (no-indicator, patience, "
        "add-to-winners) cleared the labels structural gate (389 setups) but was "
        "rejected at fee-honest replay -- it made +95.4% and cut max drawdown to "
        "-38.2% yet did NOT beat BTC buy-and-hold (Sharpe 0.52 vs 0.93, Calmar 0.25 "
        "vs 0.60), had a low 15.2% win rate with negative total R (-101.4, structural "
        "stops bled faster than the pyramided winners recovered), and the 2026 "
        "forward-OOS edge did not hold; lower drawdown alone is not an edge over "
        "holding BTC. (Rejects the objective approximation, not the observed trader's "
        "exact private system.)",
    "oos_validated_beta_neutral_cross_sectional_relative_value":
        "C19: OOS-validated beta-neutral cross-sectional relative value cleared the "
        "position mechanics (gross capped 1.0, one live position, >= 5-bar spacing) "
        "but was REJECTED at the real-candle labels / neutrality gate -- only 41 "
        "tradeable entries (< 100 structural sample gate) and OOS beta-neutrality "
        "held on only 862/1977 bars (~44%), with 15 positions closed by "
        "neutrality-break; this echoes the C16 failure that return-beta neutrality "
        "does not persist out of sample, so no fee-honest replay was run.",
    "mechanically_neutral_spot_perp_basis_funding_carry":
        "C20: mechanically-neutral same-asset long-spot/short-perp basis + funding "
        "carry cleared every prior structural gate (704 entries, mechanical "
        "neutrality 100% by construction) but was REJECTED at fee-honest replay -- "
        "the entry/exit TIMING over-trades: 704 round-trips x 74 bps two-leg cost = "
        "521% cost drag, turning a +21.2% raw carry into net -74.5% (Sharpe -12.84), "
        "with 2026 forward-OOS net -8.3% / 0% win rate and losing badly to the "
        "random/null always-on neutral-carry baseline (+21.2%, Sharpe 1.09). The "
        "CARRY THESIS is real (always-on null positive, BTC/ETH funding Sharpe ~8); "
        "this rejects the TIMING/churn, not the carry. A LOW-TURNOVER always-on carry "
        "may deserve a separate future candidate under explicit human approval -- "
        "churn cost, not signal, is the killer here.",
    "low_turnover_same_asset_spot_perp_funding_carry":
        "C21: low-turnover same-asset spot/perp funding carry was the low-turnover "
        "answer to C20 -- and the low-turnover design WORKED: 20 trades (cost drag "
        "14.8% vs C20's 521%) kept it net +20.2% (Sharpe 1.05; gross +25.7%, Sharpe "
        "1.31), validating that CHURN, not signal, killed C20. BUT it was REJECTED at "
        "fee-honest replay because it does NOT beat the trivial always-on neutral-carry "
        "null (+21.2%, Sharpe 1.09) and the 2026 forward-OOS fails (strategy -1.0%, null "
        "-0.5%): 2 of 4 decisive gates pass, the two decisive gates (beats-null, "
        "forward-OOS) fail. SPARTA Pipeline Audit v1 confirms this is not a fee/funding/"
        "lookahead/duplicate/alignment artifact. The carry SOURCE is real but FREE (it "
        "is the null) and OOS-fragile; the detector timing adds no edge. Two lessons: "
        "(1) low turnover fixes the churn; (2) same-asset carry timing adds no edge over "
        "the always-on null -- the always-on carry itself is a SEPARATE future candidate "
        "only with explicit human approval.",
}

# --- THE C14 LESSON (preserved + operationalized) ---------------------------
C14_LESSON = (
    "Conviction-bar timing had genuine signal vs random-entry, but it FAILED the "
    "buy-and-hold comparison and the forward-OOS 2026 continuation. Beating "
    "random-entry is NECESSARY BUT NOT SUFFICIENT; a durable tradeable edge must "
    "ALSO beat buy-and-hold and continue in forward-OOS. The priority score "
    "therefore weights the DURABILITY proxy above the TIMING proxy.")

# --- priority scoring spec (pre-registered weights; never fit) ---------------
PRIORITY_WEIGHTS = {
    "durability_proxy": 0.45,          # expected to beat buy-and-hold AND forward-OOS
    "timing_signal_proxy": 0.15,       # beats random-entry (necessary, not sufficient)
    "novelty_distinct_axis": 0.20,     # a materially-new mechanism axis
    "portfolio_fit": 0.20,             # low-correlation + capital-efficient
}
PORTFOLIO_FIT_WEIGHTS = {
    "expected_low_correlation": 0.4,
    "capital_efficiency_proxy": 0.35,
    "regime_breadth_proxy": 0.25,      # spans bull/bear/chop, not one regime
}

# --- anti-loop protection ---------------------------------------------------
ANTI_LOOP_RULES = {
    "no_rejected_family_reproposed": True,
    "material_difference_from_all_rejected_required": True,
    "parameter_only_modifications_penalized": True,
    "param_only_is_not_buildable": True,
    "distinct_edge_axis_required_for_priority": True,
}

# --- portfolio-level objective (tracked; advisory; NOT computed here) --------
PORTFOLIO_OBJECTIVE = {
    "prefer_low_correlation_to_existing_research": True,
    "prefer_capital_efficient": True,
    "tracked_dimensions": ("trade_time_overlap", "regime_profile",
                           "symbol_exposure", "holding_time_bars",
                           "return_stream_correlation"),
    "computed_in_this_contract": False,   # objective is declared, not run
    "feeds": "portfolio_capital_efficiency lane (separately authorized COMPUTE)",
}

# --- overnight batching protocol (planner-only; builds nothing) -------------
OVERNIGHT_BATCHING = {
    "steps": ("generate_multiple_candidate_ideas",
              "score_and_rank_by_priority",
              "select_only_the_best_one_or_best_few",
              "RECOMMEND_build_of_selected_to_the_human",
              "produce_morning_report"),
    "default_build_top_k": 1,
    "max_build_top_k": 3,
    "builds_anything_automatically": False,
    "auto_pushes": False,
    "auto_commits": False,
    "requires_human_approval_to_build_each_gate": True,
    "stops_before_real_data_gates": True,
}

REP_LABEL = (
    "SPARTA Research Expansion Plan v1 (READ-ONLY, RESEARCH ONLY, PURE PLANNER). "
    "Run MORE candidate families FASTER via overnight idea generation + priority "
    "ranking + build-only-the-best-few, while PRESERVING the proposal->spec->"
    "detector->labels->replay->decision gate sequence and EVERY safety lock. "
    "Priority weights DURABILITY (beat buy-and-hold + forward-OOS) above TIMING "
    "(beat random) per the C14 lesson. Anti-loop: never re-propose a rejected "
    "family, require material difference, penalize parameter-only tweaks. "
    "Portfolio objective: prefer low-correlation, capital-efficient candidates. "
    "BUILDS NOTHING, COMMITS NOTHING, PUSHES NOTHING, FETCHES NOTHING -- every "
    "build/commit/push still needs explicit human approval."
)

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "builds_candidate_files", "runs_detector",
    "runs_labels", "runs_replay", "runs_robustness", "runs_portfolio_compute",
    "fetches_data", "reads_real_data", "mutates_data", "stages_data",
    "auto_commits", "auto_pushes", "modifies_scheduler", "starts_scheduler",
    "sends_notifications", "calls_api", "uses_network", "uses_credentials",
    "connects_broker", "connects_exchange", "uses_real_money", "places_orders",
    "contains_order_logic", "paper_trading", "live_trading", "deploys_capital",
    "promotes_gate", "unlocks_downstream_gate", "skips_any_gate",
    "reproposes_rejected_family", "advances_without_human_approval",
    "claims_profitability", "claims_edge", "crosses_into_forbidden_gate",
)


def _clamp(x) -> float:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return 0.0
    return 0.0 if v < 0.0 else (1.0 if v > 1.0 else v)


def portfolio_fit_score(pf: dict) -> float:
    """Pure weighted portfolio-fit score in [0,1] from DECLARED proxies. Computes
    NO real correlation -- it only blends the proposer's declared estimates."""
    pf = pf or {}
    w = PORTFOLIO_FIT_WEIGHTS
    lc = _clamp(1.0 if pf.get("expected_low_correlation") is True
                else pf.get("expected_low_correlation", 0.0))
    ce = _clamp(pf.get("capital_efficiency_proxy", 0.0))
    rb = _clamp(pf.get("regime_breadth_proxy", 0.0))
    return (w["expected_low_correlation"] * lc
            + w["capital_efficiency_proxy"] * ce
            + w["regime_breadth_proxy"] * rb)


def score_candidate_idea(idea: dict, rejected_families: Any = None) -> dict[str, Any]:
    """Pure priority score for ONE declared candidate idea. Anti-loop gates run
    first (rejected family / not-materially-different / parameter-only). Then a
    weighted score that puts DURABILITY above TIMING (the C14 lesson). Builds
    nothing; recommends nothing executable."""
    rejected = set(rejected_families if rejected_families is not None
                   else REJECTED_FAMILIES_C1_TO_C21)
    family = idea.get("family")
    out: dict[str, Any] = {
        "family": family, "buildable": False, "priority_score": 0.0,
        "components": {}, "reason": None,
        "is_pure_recommendation": True, "executes_nothing": True,
    }

    # Anti-loop gate 1: never re-propose a rejected/closed family.
    if family in rejected:
        out["reason"] = "family_in_rejected_ledger_C1_to_C16"
        return out
    # Anti-loop gate 2: must be materially different from ALL rejected families.
    if idea.get("materially_different_from_all_rejected") is not True:
        out["reason"] = "not_materially_different_from_all_rejected"
        return out
    # Anti-loop gate 3: parameter-only modifications are NOT buildable.
    if idea.get("is_param_only_modification") is True:
        out["reason"] = "parameter_only_modification_not_buildable"
        return out
    # A distinct mechanism axis is required to earn priority.
    if idea.get("distinct_edge_axis") is not True:
        out["reason"] = "no_distinct_edge_axis"
        return out

    w = PRIORITY_WEIGHTS
    dur = _clamp(idea.get("durability_proxy", 0.0))
    tim = _clamp(idea.get("timing_signal_proxy", 0.0))
    nov = 1.0 if idea.get("distinct_edge_axis") is True else 0.0
    pf = portfolio_fit_score(idea.get("portfolio_fit") or {})
    components = {
        "durability_proxy": dur, "timing_signal_proxy": tim,
        "novelty_distinct_axis": nov, "portfolio_fit": pf,
    }
    score = (w["durability_proxy"] * dur + w["timing_signal_proxy"] * tim
             + w["novelty_distinct_axis"] * nov + w["portfolio_fit"] * pf)
    out["buildable"] = True
    out["priority_score"] = round(score, 6)
    out["components"] = components
    out["reason"] = "scored"
    return out


def rank_candidate_ideas(ideas: list, rejected_families: Any = None
                         ) -> list[dict[str, Any]]:
    """Pure ranking: score every idea, return the BUILDABLE ones sorted by
    priority score (desc), ties broken by family name for determinism."""
    scored = [score_candidate_idea(i, rejected_families) for i in (ideas or [])]
    buildable = [s for s in scored if s["buildable"]]
    buildable.sort(key=lambda s: (-s["priority_score"], str(s["family"])))
    return buildable


def overnight_batch_plan(ideas: list, build_top_k: int = 1,
                         rejected_families: Any = None) -> dict[str, Any]:
    """Pure overnight-batch PLAN: generate(declared) -> rank -> select the best
    few -> RECOMMEND build to the human -> morning-report summary. Builds /
    commits / pushes NOTHING; every selected idea still needs human approval at
    each gate."""
    k = max(0, min(int(build_top_k), OVERNIGHT_BATCHING["max_build_top_k"]))
    scored = [score_candidate_idea(i, rejected_families) for i in (ideas or [])]
    ranked = rank_candidate_ideas(ideas, rejected_families)
    selected = ranked[:k]
    skipped = [s for s in scored if not s["buildable"]]
    return {
        "generated_count": len(ideas or []),
        "scored_count": len(scored),
        "buildable_count": len(ranked),
        "ranked": ranked,
        "selected_to_build": selected,
        "skipped_or_rejected": skipped,
        "build_top_k": k,
        "recommended_build_tokens": [
            "BUILD_NEXT_CANDIDATE_FAMILY_PROPOSAL_ONLY" for _ in selected],
        "builds_anything_automatically": False,
        "auto_commits": False, "auto_pushes": False, "fetches_data": False,
        "requires_human_approval_to_build_each_gate": True,
        "stops_before_real_data_gates": True,
        "morning_report_summary": {
            "generated": len(ideas or []),
            "buildable": len(ranked),
            "selected_to_build": [s["family"] for s in selected],
            "top_priority_score": (selected[0]["priority_score"]
                                   if selected else None),
            "skipped_families": [s["family"] for s in skipped],
            "executes_nothing": True,
        },
    }


def get_research_expansion_plan_label() -> str:
    return REP_LABEL


def build_research_expansion_plan(repo_root: Any = ".",
                                  tracked_paths: list | None = None
                                  ) -> dict[str, Any]:
    """Assemble the frozen Research Expansion Plan v1 record. Pure; no I/O; plan
    + spec only. Executes nothing."""
    record: dict[str, Any] = {
        "schema_version": REP_SCHEMA_VERSION, "label": REP_LABEL, "mode": REP_MODE,
        "lane": "crypto_d1_auto_research",
        "is_pure_planner_only": True,
        "goal": ("increase candidate-discovery speed while keeping ALL safety "
                 "locks: no paper trading, no live trading, no broker, no orders, "
                 "no auto-push without human approval"),
        "gate_sequence": list(GATE_SEQUENCE),
        "gate_sequence_preserved_unchanged": True,
        "human_gated_stages": list(HUMAN_GATED_STAGES),
        "real_data_stages": list(REAL_DATA_STAGES),
        "rejected_families_c1_to_c14": list(REJECTED_FAMILIES_C1_TO_C14),
        "rejected_families_current": list(REJECTED_FAMILIES_C1_TO_C21),
        "rejected_families_count": len(REJECTED_FAMILIES_C1_TO_C21),
        "rejected_family_lessons": dict(REJECTED_FAMILY_LESSONS),
        "c14_lesson": C14_LESSON,
        "priority_weights": dict(PRIORITY_WEIGHTS),
        "portfolio_fit_weights": dict(PORTFOLIO_FIT_WEIGHTS),
        "durability_weighted_above_timing":
            PRIORITY_WEIGHTS["durability_proxy"] > PRIORITY_WEIGHTS["timing_signal_proxy"],
        "anti_loop_rules": dict(ANTI_LOOP_RULES),
        "portfolio_objective": dict(PORTFOLIO_OBJECTIVE),
        "overnight_batching": dict(OVERNIGHT_BATCHING),
        "speed_levers": (
            "(1) overnight idea GENERATION produces several declared candidate "
            "ideas at once; (2) PRIORITY RANKING spends effort only on the "
            "best-scoring few; (3) the low-risk research build gates (proposal / "
            "spec / detector dry-run) can be recommended for auto-advance by the "
            "Safe Research Autopilot v1 planner, while the real-data gates "
            "(labels / replay) and ALL commits/pushes stay human-gated; (4) the "
            "rejected-family ledger + lessons prune the search up front so no "
            "effort is wasted re-deriving known dead ends."),
        "human_review_required": True,
        "current_loop_stage": "research_expansion_plan_spec",
        "next_required_action":
            "HUMAN_DECISION_ADOPT_RESEARCH_EXPANSION_PLAN_OR_AMEND",
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_build": True, "no_write": True, "no_execute": True,
        "no_detector_run": True, "no_labels": True, "no_replay": True,
        "no_robustness": True, "no_portfolio_compute": True, "no_data_fetch": True,
        "no_real_data_access": True, "no_stage": True, "no_commit": True,
        "no_push": True, "no_auto_push_without_human_approval": True,
        "no_scheduler_change": True, "no_broker": True, "no_credentials": True,
        "no_order_logic": True, "no_paper_trading": True, "no_live_trading": True,
        "no_gate_skip": True, "no_rejected_family_repropose": True,
        "no_param_only_buildable": True, "no_downstream_gate_unlock": True,
        "no_profitability_claim": True,
    }
    return record


def validate_research_expansion_plan(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. The plan is valid only when it is pure-planner-only,
    preserves the exact 6-stage gate sequence, keeps the real-data gates human-
    gated, weights durability above timing (the C14 lesson), carries the anti-loop
    rules + the full rejected ledger, declares (does not run) the portfolio
    objective, and pins every capability flag False."""
    failures: list = []
    if record.get("mode") != REP_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_pure_planner_only") is not True:
        failures.append("not_pure_planner_only")

    # Gate sequence preserved exactly.
    if list(record.get("gate_sequence") or []) != list(GATE_SEQUENCE):
        failures.append("gate_sequence_tampered")
    if record.get("gate_sequence_preserved_unchanged") is not True:
        failures.append("gate_sequence_not_marked_preserved")
    for stage in REAL_DATA_STAGES:
        if stage not in (record.get("real_data_stages") or []):
            failures.append("real_data_stage_missing_%s" % stage)

    # C14 lesson operationalized: durability weighted above timing.
    pw = record.get("priority_weights") or {}
    if not (pw.get("durability_proxy", 0) > pw.get("timing_signal_proxy", 1)):
        failures.append("durability_not_weighted_above_timing")
    if record.get("durability_weighted_above_timing") is not True:
        failures.append("durability_above_timing_flag_tampered")
    if not record.get("c14_lesson"):
        failures.append("c14_lesson_missing")

    # Anti-loop rules.
    al = record.get("anti_loop_rules") or {}
    for key in ("no_rejected_family_reproposed",
                "material_difference_from_all_rejected_required",
                "parameter_only_modifications_penalized",
                "param_only_is_not_buildable"):
        if al.get(key) is not True:
            failures.append("anti_loop_rule_off_%s" % key)

    # Historical C1-C14 ledger (frozen; referenced by the pushed C15 chain).
    led = record.get("rejected_families_c1_to_c14") or []
    for fam in ("intraweek_calendar_seasonality_drift",
                "cross_asset_dispersion_reversion",
                "failed_breakdown_reclaim_reversal",
                "lead_lag_propagation_continuation",
                "conviction_bar_follow_through"):
        if fam not in led:
            failures.append("rejected_ledger_missing_%s" % fam)
    if len(led) != 19:
        failures.append("rejected_ledger_count_unexpected")

    # CURRENT canonical ledger (C1-C18) used for forward anti-loop: must add C18
    # (and still contain C17 + C16 + C15).
    cur = record.get("rejected_families_current") or []
    if "low_turnover_same_asset_spot_perp_funding_carry" not in cur:
        failures.append("current_ledger_missing_c21")
    if "mechanically_neutral_spot_perp_basis_funding_carry" not in cur:
        failures.append("current_ledger_missing_c20")
    if "oos_validated_beta_neutral_cross_sectional_relative_value" not in cur:
        failures.append("current_ledger_missing_c19")
    if "h4_trend_following_market_structure" not in cur:
        failures.append("current_ledger_missing_c18")
    if "risk_adjusted_portfolio_construction_vol_targeted_allocation" not in cur:
        failures.append("current_ledger_missing_c17")
    if "cointegration_pairs_market_neutral" not in cur:
        failures.append("current_ledger_missing_c16")
    if "slow_vol_targeted_time_series_momentum" not in cur:
        failures.append("current_ledger_missing_c15")
    if len(cur) != 26:
        failures.append("current_ledger_count_unexpected")
    if record.get("rejected_families_count") != 26:
        failures.append("rejected_families_count_not_26")

    # Portfolio objective declared, NOT computed.
    po = record.get("portfolio_objective") or {}
    if po.get("computed_in_this_contract") is not False:
        failures.append("portfolio_objective_must_not_be_computed_here")
    for dim in ("trade_time_overlap", "regime_profile", "symbol_exposure",
                "holding_time_bars"):
        if dim not in (po.get("tracked_dimensions") or ()):
            failures.append("portfolio_dimension_missing_%s" % dim)

    # Overnight batching is planner-only.
    ob = record.get("overnight_batching") or {}
    if ob.get("builds_anything_automatically") is not False:
        failures.append("overnight_auto_build_set")
    if ob.get("auto_pushes") is not False:
        failures.append("overnight_auto_push_set")
    if ob.get("requires_human_approval_to_build_each_gate") is not True:
        failures.append("overnight_no_human_approval_required")

    locks = record.get("scope_locks") or {}
    for key in ("no_build", "no_write", "no_execute", "no_labels", "no_replay",
                "no_portfolio_compute", "no_data_fetch", "no_real_data_access",
                "no_commit", "no_push", "no_auto_push_without_human_approval",
                "no_paper_trading", "no_live_trading", "no_broker",
                "no_gate_skip", "no_rejected_family_repropose",
                "no_param_only_buildable"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
