"""Strategy Family Tournament v1 -- FAMILY PROPOSAL / SPEC (PURE, RESEARCH ONLY).

A pure, in-memory PROPOSAL that lays out a systematic tournament of the major
well-known strategy families, to find which one has the best chance for the SPARTA
crypto-D1 portfolio. It SPECIFIES each family (core idea / symbols+timeframes /
expected regime / entry / exit / risk / why it differs from the rejected C1-C14
variants / expected failure mode), a durability-weighted SCORING + RANKING to pick
which family to test FIRST, the durability + recent-relevance + forward-OOS +
regime-tagging windows, and the portfolio objective.

It does NOTHING else: it does NOT fetch data, NOT backtest, NOT build detector /
labels / replay, NOT write files, NOT run anything, NOT stage / commit / push, and
NOT touch any paper / live / broker / credential / order surface. Every capability
flag is pinned False with a full scope_locks set, so this is a SPEC only -- each
family still has to pass the SAME human-gated gate sequence (proposal -> spec ->
detector dry-run -> real-candle labels -> fee-honest replay -> rejection/promote)
before anything is believed.

Market making is explicitly EXCLUDED (not suitable now): it needs low-latency
infrastructure, order-book execution, and live spread capture -- outside the
research-only, daily-bar, no-execution scope.

The scoring operationalizes the C14 lesson: DURABILITY (a real 3-year edge that
ALSO survives forward-OOS and isn't just buy-and-hold beta) is weighted above
everything else; a recent-relevance signal alone is necessary but not sufficient.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.research_expansion_plan_v1_contract as _rep

SFT_SCHEMA_VERSION = 1
SFT_MODE = "RESEARCH_ONLY"
SFT_LANE = "crypto_d1_auto_research"

# The same canonical rejected ledger (C1-C14, 19) + C14 lesson the rest of the
# research-expansion system uses. Every tournament family must be a GENERIC family
# distinct from the SPECIFIC rejected variants.
REJECTED_FAMILIES_C1_TO_C14 = tuple(_rep.REJECTED_FAMILIES_C1_TO_C14)
C14_LESSON = _rep.C14_LESSON

# --- the preserved, frozen gate sequence (each stage human-gated) -----------
GATE_SEQUENCE = (
    "family_proposal", "candidate_spec", "detector_spec_dry_run",
    "real_candle_labels_review", "fee_honest_replay_review",
    "rejection_or_promote_decision",
)

# --- evaluation windows (requirement 7) -------------------------------------
EVALUATION_WINDOWS = {
    "durability_window_days": 1095,            # 3-year long-history durability
    "recent_relevance_window_days_min": 90,    # recent 3-month relevance
    "recent_relevance_window_days_max": 180,   # recent 6-month relevance
    "forward_oos_required": True,
    "forward_oos_window": "2026_unseen_continuation",
    "regime_specific_tagging_required": True,
    "regimes": ("bull", "bear", "chop"),
    "min_labels_total": 100, "min_labels_per_asset": 20,
    "min_labels_per_regime": 20,               # structural sample-size gate (C13)
}

# --- durability-weighted scoring (requirement 6; C14 lesson) ----------------
SCORING_WEIGHTS = {
    "durability_3yr": 0.35,        # a real 3-year edge (weighted highest)
    "recent_relevance": 0.20,      # recent 3-6 month relevance
    "forward_oos_prior": 0.15,     # prior expectation it survives forward-OOS
    "novelty_vs_c1_c14": 0.15,     # materially different from rejected variants
    "portfolio_fit": 0.15,         # low-corr / capital-efficient / low-overlap
}

# --- portfolio objective (requirement 8) ------------------------------------
PORTFOLIO_OBJECTIVE = {
    "prefer_low_correlation": True,
    "prefer_capital_efficient": True,
    "prefer_low_overlap": True,
    "prefer_different_holding_periods": True,
    "tracked_dimensions": ("return_stream_correlation", "capital_efficiency",
                           "trade_time_overlap", "holding_period_bucket",
                           "regime_profile", "symbol_exposure"),
    "computed_in_this_contract": False,        # objective is declared, not run
}

# --------------------------------------------------------------------------- #
# The 7 included families (full spec) + the excluded one.
# --------------------------------------------------------------------------- #
FAMILIES: tuple = (
    {
        "key": "trend_following",
        "name": "Trend following (time-series momentum, position-level)",
        "included": True,
        "core_idea": ("Ride large persistent directional moves: go with the sign "
                      "of slow price momentum, vol-target the position, and go "
                      "flat/short in downtrends rather than holding through."),
        "symbols": ("BTCUSD", "ETHUSD", "SOLUSD"),
        "timeframes": ("D1",),
        "holding_period": "weeks_to_months",
        "expected_regime": "trending_bull_and_bear (hurts in chop)",
        "entry_logic": ("long when fast/slow EMA stack + multi-week return are "
                        "positive and above a volatility-scaled threshold; "
                        "symmetric short/flat when negative"),
        "exit_logic": ("trend-flip (EMA cross / sign change) or vol-stop; no fixed "
                       "horizon -- let winners run, cut on regime flip"),
        "risk_logic": ("volatility targeting (ATR-scaled position size), per-trade "
                       "vol-stop, portfolio heat cap across the 3 symbols"),
        "difference_from_c1_c14": ("C4/C5 (long_biased / btc_sol trend "
            "CONTINUATION) and the 1h continuation variants were FAST, fixed-"
            "horizon directional continuation setups; this is SLOW, vol-targeted, "
            "flat/short-in-bear time-series momentum at the position level"),
        "expected_failure_mode": ("collapses into buy-and-hold beta during a "
            "persistent bull (the C14 trap -- beats random but loses to B&H) "
            "unless the bear-side flat/short and vol-targeting add real value; "
            "whipsaw losses in chop"),
        "score_inputs": {"durability_3yr": 0.85, "recent_relevance": 0.60,
                         "forward_oos_prior": 0.70, "novelty_vs_c1_c14": 0.60,
                         "portfolio_fit": 0.70},
    },
    {
        "key": "statistical_arbitrage_pairs",
        "name": "Statistical arbitrage / cointegration pairs (market-neutral)",
        "included": True,
        "core_idea": ("Trade the mean-reverting spread of a cointegrated pair "
                      "(e.g. ETH-BTC, SOL-ETH): long the cheap leg / short the "
                      "rich leg when the spread z-score is extreme."),
        "symbols": ("ETH/BTC", "SOL/ETH", "SOL/BTC"),
        "timeframes": ("D1",),
        "holding_period": "days_to_weeks",
        "expected_regime": "range/chop friendly; risk in structural regime breaks",
        "entry_logic": ("enter when the cointegration-residual z-score exceeds a "
                        "band (e.g. |z|>=2) AND the cointegration test is still "
                        "valid over the rolling durability window"),
        "exit_logic": ("z-score reverts toward 0 (take), z-band stop on widening, "
                       "or cointegration-break invalidation exit"),
        "risk_logic": ("dollar-neutral / beta-neutral legs, spread vol-stop, "
                       "hard exit if the rolling cointegration p-value degrades"),
        "difference_from_c1_c14": ("C11 (cross_asset_dispersion_reversion) traded "
            "cross-sectional DISPERSION, not a cointegrated two-leg spread; classic "
            "stat-arb pairs with rolling cointegration validation has NOT been "
            "tried -- it is genuinely market-neutral"),
        "expected_failure_mode": ("cointegration breaks in a structural regime "
            "shift (one leg de-pegs / decouples) and the spread trends instead of "
            "reverting; fees on two legs erode a thin edge"),
        "score_inputs": {"durability_3yr": 0.70, "recent_relevance": 0.50,
                         "forward_oos_prior": 0.55, "novelty_vs_c1_c14": 0.80,
                         "portfolio_fit": 0.85},
    },
    {
        "key": "momentum_relative_strength",
        "name": "Momentum / cross-sectional relative strength",
        "included": True,
        "core_idea": ("Rank a universe by recent risk-adjusted return; hold the "
                      "strongest, avoid/short the weakest, rebalance periodically."),
        "symbols": ("BTCUSD", "ETHUSD", "SOLUSD", "(extensible universe)"),
        "timeframes": ("D1",),
        "holding_period": "weeks",
        "expected_regime": "dispersed trending (needs cross-sectional spread)",
        "entry_logic": ("at each rebalance, long the top-ranked symbol(s) by "
                        "lookback momentum if the cross-sectional spread is wide "
                        "enough to matter"),
        "exit_logic": ("periodic rebalance rotation out of weakening names; "
                       "spread-collapse flat"),
        "risk_logic": ("equal-risk weighting across held names, per-name vol-stop, "
                       "gross exposure cap"),
        "difference_from_c1_c14": ("C8-class (eth_sol_relative_strength, "
            "multi_symbol_rotation_filter) were 2-3 symbol pairwise RS filters; "
            "this is a ranked cross-sectional momentum portfolio over an "
            "extensible universe with periodic rebalance"),
        "expected_failure_mode": ("too few liquid D1 crypto names -> the cross-"
            "section is too thin to rank; reduces to single-name trend and "
            "double-counts the trend family"),
        "score_inputs": {"durability_3yr": 0.75, "recent_relevance": 0.55,
                         "forward_oos_prior": 0.60, "novelty_vs_c1_c14": 0.40,
                         "portfolio_fit": 0.65},
    },
    {
        "key": "position_trading",
        "name": "Position trading (multi-month regime-conditioned)",
        "included": True,
        "core_idea": ("Hold a core directional position for months, switched on/"
                      "off by a slow macro/regime filter rather than by short-term "
                      "signals."),
        "symbols": ("BTCUSD", "ETHUSD"),
        "timeframes": ("D1", "W1_context"),
        "holding_period": "months",
        "expected_regime": "long secular bull legs; flat in confirmed bear",
        "entry_logic": ("enter core long when the slow regime filter (e.g. price "
                        "above long MA + positive multi-month trend) turns on"),
        "exit_logic": ("regime filter turns off (step aside to cash); no intra-"
                       "regime churn"),
        "risk_logic": ("conservative fixed fractional sizing, regime-off = flat, "
                       "drawdown circuit-breaker"),
        "difference_from_c1_c14": ("no C1-C14 candidate held for MONTHS or used a "
            "slow on/off regime switch; all prior were intraday/1h/daily-horizon "
            "setups"),
        "expected_failure_mode": ("indistinguishable from buy-and-hold beta with a "
            "lag (the C14 trap in its starkest form) -- the regime-off periods "
            "must add enough downside avoidance to beat B&H net of costs"),
        "score_inputs": {"durability_3yr": 0.70, "recent_relevance": 0.50,
                         "forward_oos_prior": 0.55, "novelty_vs_c1_c14": 0.60,
                         "portfolio_fit": 0.55},
    },
    {
        "key": "breakout_trading",
        "name": "Breakout trading (D1 range/volatility expansion)",
        "included": True,
        "core_idea": ("Enter on a confirmed break of a well-defined consolidation "
                      "range with a volatility/volume expansion, targeting the "
                      "ensuing impulse."),
        "symbols": ("BTCUSD", "ETHUSD", "SOLUSD"),
        "timeframes": ("D1",),
        "holding_period": "days",
        "expected_regime": "post-compression expansion; fails in chop (false breaks)",
        "entry_logic": ("break of an N-day range high/low with a range-width and "
                        "expansion filter; enter on close-confirmation, not wick"),
        "exit_logic": ("measured-move / R-multiple target, time-stop, or failed-"
                       "break reversal exit"),
        "risk_logic": ("stop just inside the broken level, ATR-floored risk "
                       "distance, one position per symbol"),
        "difference_from_c1_c14": ("C3 (crypto_intraday_breakout_pullback) was an "
            "intraday pullback-after-breakout entry; this is a D1 range/volatility-"
            "expansion breakout at close-confirmation, position horizon"),
        "expected_failure_mode": ("false breakouts in chop dominate; the expansion "
            "filter is too loose -> death by a thousand whipsaws after fees"),
        "score_inputs": {"durability_3yr": 0.60, "recent_relevance": 0.55,
                         "forward_oos_prior": 0.50, "novelty_vs_c1_c14": 0.35,
                         "portfolio_fit": 0.50},
    },
    {
        "key": "mean_reversion",
        "name": "Mean reversion (oscillator/z-score band, regime-filtered)",
        "included": True,
        "core_idea": ("In a confirmed ranging regime, fade extremes back toward a "
                      "moving mean using an oscillator / price z-score band."),
        "symbols": ("BTCUSD", "ETHUSD", "SOLUSD"),
        "timeframes": ("D1",),
        "holding_period": "days",
        "expected_regime": "ranging/chop ONLY (explicit anti-trend regime filter)",
        "entry_logic": ("price z-score / RSI extreme against a flat regime filter "
                        "(no entries when a trend filter is on)"),
        "exit_logic": ("revert to mean (take), opposite-band stop, time-stop"),
        "risk_logic": ("tight stop beyond the band, half-size in elevated vol, no "
                       "entries while the trend filter is active"),
        "difference_from_c1_c14": ("C9/C8-class MR (liquidity_sweep, low_volume_"
            "capitulation, dispersion_reversion) were single-shot EVENT-triggered "
            "reversions; this is a continuous oscillator/z-score band MR gated by "
            "an explicit ranging-regime filter"),
        "expected_failure_mode": ("a trend breaks out of the range and the fade "
            "keeps adding to a loser; the regime filter lags the breakout (classic "
            "MR ruin)"),
        "score_inputs": {"durability_3yr": 0.50, "recent_relevance": 0.50,
                         "forward_oos_prior": 0.45, "novelty_vs_c1_c14": 0.30,
                         "portfolio_fit": 0.60},
    },
    {
        "key": "swing_trading",
        "name": "Swing trading (multi-day D1 structure swings)",
        "included": True,
        "core_idea": ("Capture multi-day swings between structural support/"
                      "resistance with a trend/regime bias, holding days to a "
                      "couple of weeks."),
        "symbols": ("BTCUSD", "ETHUSD", "SOLUSD"),
        "timeframes": ("D1",),
        "holding_period": "days_to_two_weeks",
        "expected_regime": "moderate trend with pullbacks (not violent chop)",
        "entry_logic": ("pullback into D1 structure (prior swing low / demand) in "
                        "the direction of the higher-timeframe bias"),
        "exit_logic": ("next swing high / structure target, structure-break stop, "
                       "time-stop"),
        "risk_logic": ("stop beyond the structural level, fixed fractional risk, "
                       "one swing per symbol at a time"),
        "difference_from_c1_c14": ("C6/C7 (long_1h_swing_structure, sol_btc_1h_"
            "swing) were 1h-structure swings; this is a D1-structure swing on the "
            "daily timeframe with a higher-timeframe bias filter"),
        "expected_failure_mode": ("D1 structure is too coarse / too few clean "
            "setups -> tiny sample (the C13 structural-rejection risk) or the "
            "swings just re-express trend with worse timing"),
        "score_inputs": {"durability_3yr": 0.45, "recent_relevance": 0.50,
                         "forward_oos_prior": 0.40, "novelty_vs_c1_c14": 0.35,
                         "portfolio_fit": 0.50},
    },
)

EXCLUDED_FAMILIES: tuple = (
    {
        "key": "market_making",
        "name": "Market making / spread capture",
        "included": False,
        "exclusion_reason": ("requires low-latency infrastructure, order-book "
            "execution, and live spread capture -- outside the research-only, "
            "daily-bar, no-execution SPARTA scope"),
        "requires": ("colocation/low-latency", "order_book_access",
                     "live_quoting_and_cancels", "inventory_risk_engine"),
        "revisit_when": "only if a live execution venue + infra are ever authorized",
    },
)

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "builds_candidate_files", "runs_detector",
    "runs_labels", "runs_replay", "runs_backtest", "runs_robustness",
    "runs_portfolio_compute", "fetches_data", "reads_real_data", "mutates_data",
    "stages_data", "auto_commits", "auto_pushes", "modifies_scheduler",
    "sends_notifications", "calls_api", "uses_network", "uses_credentials",
    "connects_broker", "connects_exchange", "uses_real_money", "places_orders",
    "contains_order_logic", "market_making", "paper_trading", "live_trading",
    "deploys_capital", "promotes_gate", "unlocks_downstream_gate", "skips_any_gate",
    "reproposes_rejected_family", "advances_without_human_approval",
    "claims_profitability", "claims_edge", "crosses_into_forbidden_gate",
)


def _clamp(x) -> float:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return 0.0
    return 0.0 if v < 0.0 else (1.0 if v > 1.0 else v)


def score_family(family: dict) -> dict[str, Any]:
    """Pure durability-weighted priority score for ONE family. Excluded families
    are not scorable. Computes nothing about real data -- it blends the declared
    proxies only."""
    out: dict[str, Any] = {"key": family.get("key"), "scorable": False,
                           "priority_score": 0.0, "components": {}, "reason": None}
    if not family.get("included"):
        out["reason"] = "family_excluded_not_suitable_now"
        return out
    si = family.get("score_inputs") or {}
    comp = {k: _clamp(si.get(k, 0.0)) for k in SCORING_WEIGHTS}
    score = sum(SCORING_WEIGHTS[k] * comp[k] for k in SCORING_WEIGHTS)
    out["scorable"] = True
    out["priority_score"] = round(score, 6)
    out["components"] = comp
    out["reason"] = "scored"
    return out


def rank_families(families: Any = None) -> list[dict[str, Any]]:
    """Pure ranking: score the included families, sort by priority desc, ties by
    key for determinism."""
    fams = families if families is not None else FAMILIES
    scored = [score_family(f) for f in fams]
    ranked = [s for s in scored if s["scorable"]]
    ranked.sort(key=lambda s: (-s["priority_score"], str(s["key"])))
    return ranked


def recommended_first_family(families: Any = None) -> dict[str, Any]:
    """Pure: the top-ranked family to test first (the tournament's seed #1)."""
    ranked = rank_families(families)
    if not ranked:
        return {"key": None, "priority_score": None}
    top = ranked[0]
    return {"key": top["key"], "priority_score": top["priority_score"],
            "components": top["components"]}


def get_strategy_family_tournament_label() -> str:
    return (
        "Strategy Family Tournament v1 (READ-ONLY, RESEARCH ONLY, PURE PROPOSAL). "
        "Systematically test the major well-known strategy families (trend "
        "following, breakout, mean reversion, momentum/relative strength, stat-arb/"
        "pairs, swing, position) on crypto-D1 to find the best chance for the "
        "portfolio. Durability (3yr edge surviving forward-OOS, not buy-and-hold "
        "beta -- the C14 lesson) is weighted highest. Market making EXCLUDED "
        "(needs live order-book infra). PROPOSAL ONLY: every family still runs the "
        "full human-gated gate sequence. NO data fetch, NO backtest, NO paper/live, "
        "BUILDS/COMMITS/PUSHES NOTHING.")


def get_strategy_family_tournament_next_action() -> str:
    return "HUMAN_DECISION_APPROVE_TOURNAMENT_AND_BUILD_FIRST_FAMILY_SPEC_OR_AMEND"


def build_strategy_family_tournament_proposal(
        repo_root: Any = ".", tracked_paths: list | None = None) -> dict[str, Any]:
    """Assemble the frozen Strategy Family Tournament v1 proposal record. Pure; no
    I/O; proposal/spec only. Executes nothing."""
    ranked = rank_families()
    first = recommended_first_family()
    record: dict[str, Any] = {
        "schema_version": SFT_SCHEMA_VERSION, "mode": SFT_MODE, "lane": SFT_LANE,
        "label": get_strategy_family_tournament_label(),
        "is_pure_proposal_only": True,
        "goal": ("find which well-known strategy family has the best chance for "
                 "the SPARTA crypto-D1 portfolio, tested systematically under the "
                 "same gates, with durability weighted above recent relevance"),
        "gate_sequence": list(GATE_SEQUENCE),
        "gate_sequence_preserved_unchanged": True,
        "families": [dict(f) for f in FAMILIES],
        "included_family_keys": [f["key"] for f in FAMILIES if f["included"]],
        "excluded_families": [dict(f) for f in EXCLUDED_FAMILIES],
        "excluded_family_keys": [f["key"] for f in EXCLUDED_FAMILIES],
        "evaluation_windows": dict(EVALUATION_WINDOWS),
        "scoring_weights": dict(SCORING_WEIGHTS),
        "durability_weighted_above_relevance":
            SCORING_WEIGHTS["durability_3yr"] > SCORING_WEIGHTS["recent_relevance"],
        "portfolio_objective": dict(PORTFOLIO_OBJECTIVE),
        "c14_lesson": C14_LESSON,
        "rejected_families_c1_to_c14": list(REJECTED_FAMILIES_C1_TO_C14),
        "rejected_families_count": len(REJECTED_FAMILIES_C1_TO_C14),
        "ranking": ranked,
        "recommended_first_family": first,
        "anti_loop_each_family_differs_from_c1_c14": all(
            bool(f.get("difference_from_c1_c14")) for f in FAMILIES),
        "human_review_required": True,
        "current_loop_stage": "strategy_family_tournament_proposal",
        "next_required_action": get_strategy_family_tournament_next_action(),
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_build": True, "no_write": True, "no_execute": True,
        "no_data_fetch": True, "no_backtest": True, "no_detector_run": True,
        "no_labels": True, "no_replay": True, "no_robustness": True,
        "no_portfolio_compute": True, "no_real_data_access": True,
        "no_stage": True, "no_commit": True, "no_push": True,
        "no_auto_commit": True, "no_auto_push": True, "no_scheduler_change": True,
        "no_broker": True, "no_credentials": True, "no_order_logic": True,
        "no_market_making": True, "no_paper_trading": True, "no_live_trading": True,
        "no_gate_skip": True, "no_rejected_family_repropose": True,
        "no_downstream_gate_unlock": True, "no_profitability_claim": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_strategy_family_tournament_proposal(
        record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the proposal is research-only, pure-
    proposal-only, preserves the gate sequence, includes the 7 families with all
    required per-family fields, excludes market making, weights durability above
    recent relevance, carries the full windows + portfolio objective + C14 lesson +
    the 19-family ledger, and pins every capability flag False."""
    failures: list = []
    if record.get("mode") != SFT_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_pure_proposal_only") is not True:
        failures.append("not_pure_proposal_only")
    if list(record.get("gate_sequence") or []) != list(GATE_SEQUENCE):
        failures.append("gate_sequence_tampered")
    if record.get("gate_sequence_preserved_unchanged") is not True:
        failures.append("gate_sequence_not_marked_preserved")

    fams = record.get("families") or []
    included = [f for f in fams if f.get("included")]
    if len(included) != 7:
        failures.append("expected_7_included_families")
    required_keys = {"trend_following", "breakout_trading", "mean_reversion",
                     "momentum_relative_strength", "statistical_arbitrage_pairs",
                     "swing_trading", "position_trading"}
    if {f.get("key") for f in included} != required_keys:
        failures.append("included_family_set_mismatch")
    per_family_fields = ("core_idea", "symbols", "timeframes", "expected_regime",
                         "entry_logic", "exit_logic", "risk_logic",
                         "difference_from_c1_c14", "expected_failure_mode",
                         "score_inputs")
    for f in included:
        for field in per_family_fields:
            if not f.get(field):
                failures.append("family_%s_missing_%s" % (f.get("key"), field))

    # market making excluded
    excl = {f.get("key") for f in (record.get("excluded_families") or [])}
    if "market_making" not in excl:
        failures.append("market_making_not_excluded")
    if "market_making" in {f.get("key") for f in included}:
        failures.append("market_making_must_not_be_included")

    # durability weighted above recent relevance (C14 lesson)
    sw = record.get("scoring_weights") or {}
    if not (sw.get("durability_3yr", 0) > sw.get("recent_relevance", 1)):
        failures.append("durability_not_weighted_above_relevance")
    if record.get("durability_weighted_above_relevance") is not True:
        failures.append("durability_above_relevance_flag_tampered")

    # windows present (requirement 7)
    w = record.get("evaluation_windows") or {}
    if w.get("durability_window_days") != 1095:
        failures.append("durability_window_not_3yr")
    if w.get("forward_oos_required") is not True:
        failures.append("forward_oos_not_required")
    if w.get("regime_specific_tagging_required") is not True:
        failures.append("regime_tagging_not_required")
    for k in ("recent_relevance_window_days_min", "recent_relevance_window_days_max"):
        if not w.get(k):
            failures.append("recent_relevance_window_missing_%s" % k)

    # portfolio objective (requirement 8) declared, not computed
    po = record.get("portfolio_objective") or {}
    for k in ("prefer_low_correlation", "prefer_capital_efficient",
              "prefer_low_overlap", "prefer_different_holding_periods"):
        if po.get(k) is not True:
            failures.append("portfolio_objective_missing_%s" % k)
    if po.get("computed_in_this_contract") is not False:
        failures.append("portfolio_objective_must_not_be_computed_here")

    # learning data + C14 lesson
    if record.get("rejected_families_count") != 19:
        failures.append("rejected_ledger_not_19")
    if not record.get("c14_lesson"):
        failures.append("c14_lesson_missing")
    if record.get("anti_loop_each_family_differs_from_c1_c14") is not True:
        failures.append("a_family_not_differentiated_from_c1_c14")

    # ranking + first recommendation present
    if not record.get("ranking"):
        failures.append("ranking_missing")
    if not (record.get("recommended_first_family") or {}).get("key"):
        failures.append("recommended_first_family_missing")

    locks = record.get("scope_locks") or {}
    for key in ("no_build", "no_write", "no_execute", "no_data_fetch",
                "no_backtest", "no_labels", "no_replay", "no_portfolio_compute",
                "no_commit", "no_push", "no_auto_commit", "no_auto_push",
                "no_broker", "no_order_logic", "no_market_making",
                "no_paper_trading", "no_live_trading", "no_gate_skip",
                "no_rejected_family_repropose"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
