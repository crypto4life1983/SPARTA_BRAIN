"""Candidate #25 INTAKE + DISTINCTNESS REVIEW -- video momentum breakout / scalping family
-- PURE, RESEARCH ONLY, NO-GO / NEAR-DUPLICATE REVIEW (NOT a C25 proposal).

Research-only intake for the human-approved C25 distinctness-review direction
(HUMAN_APPROVED_C25_VIDEO_MOMENTUM_BREAKOUT_SCALPING_INTAKE_AND_DISTINCTNESS_REVIEW_ONLY).
The reviewed family is the uploaded "break and bounce" video strategy and its indicator
variants: a DIRECTIONAL intraday momentum-breakout / scalping family on a fast (5-minute)
timeframe -- prior-range breakout + retest/bounce, hammer/engulfing reversal-candle entry,
or the indicator parameterizations (fast MA above slow MA, close above the close 20 bars ago,
green-body / non-wicky candle, Z-score filter, VWMA/Bollinger buy-the-dip), long/short
mirrored, with fixed percentage stop/take-profit brackets (1.5%/3%, 1%/2%, 1.7%/3%).

VERDICT: NO-GO / NEAR-DUPLICATE. This family is NOT materially new -- it is a RECOMBINATION
and RE-PARAMETERIZATION of mechanisms already REJECTED in the C1-C21 ledger (intraday
breakout-pullback, single-bar conviction/reversal candle, time-series momentum, trend
following, and buy-the-dip mean-reversion), on a faster timeframe with fixed brackets. It
shares the DIRECTIONAL single-asset-timing shape that has failed at every prior gate, and it
is the OPPOSITE of the deliberately NEUTRAL high-breadth shape chosen for C23/C24 precisely
because the directional shape keeps failing. The 5-minute timeframe makes the C20 churn/cost
lesson ACUTE (high turnover x realistic per-round-trip cost destroys edge), and the video's
70% win-rate / 1.6 profit-factor claims are UNVERIFIED with material overfitting and drawdown
risk. Recommendation: KEEP IN IDEA-BANK as NO-GO; do NOT promote to C25 proposal-readiness.

It DECLARES the family, an overlap matrix vs C1-C24, the distinctness assessment, and the
required skepticism (unverified claims, overfitting, 5-minute scalping cost/slippage, high
drawdown without a strict fee-honest drawdown gate, must beat realistic costs + a CORRECT
benchmark not just buy-and-hold). It builds NO spec/detector/labels/replay; runs NO
optimization/data-fetch; connects NOTHING; does NOT open C25/C24/C23 as active; does NOT
advance C22; does NOT touch any C21/C22/C23/C24 file or lane-status surface; and advances
NOTHING. Every capability flag is pinned False with a full scope_locks set.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.research_expansion_plan_v1_contract as _rep

C25R_SCHEMA_VERSION = 1
C25R_MODE = "RESEARCH_ONLY"
C25R_LANE = "crypto_d1_auto_research"

REVIEW_ID = "C25_INTAKE_DISTINCTNESS_REVIEW"
REVIEWED_FAMILY = "intraday_momentum_breakout_retest_reversal_scalping_directional"
SOURCE = ("uploaded video transcript 'break and bounce' (manual_inputs/"
          "youtube_break_and_bounce_transcript.txt) + operator-listed indicator variants")

REVIEW_TOKEN = ("HUMAN_APPROVED_C25_VIDEO_MOMENTUM_BREAKOUT_SCALPING_"
                "INTAKE_AND_DISTINCTNESS_REVIEW_ONLY")

REJECTED_FAMILIES_C1_TO_C21 = tuple(_rep.REJECTED_FAMILIES_C1_TO_C21)   # 26
# the prior proposed-but-not-rejected candidates whose queue must be preserved.
C22_FAMILY = "external_signum_trend_radar_gc_long_short"
C22_STATE = "HOLD_FOR_MORE_FROZEN_DATA_WINDOWS"
C22_PROGRESS = "2/20"
C23_FAMILY = "crypto_cross_sectional_low_volatility_anomaly_beta_neutral"
C24_FAMILY = "crypto_cross_sectional_illiquidity_premium_beta_neutral"

VERDICT_NO_GO = "C25_NO_GO_NEAR_DUPLICATE_OF_REJECTED_DIRECTIONAL_FAMILIES"
RECOMMENDATION = "REMAIN_IDEA_BANK_NO_GO"

# --- the reviewed family + variants -----------------------------------------
FAMILY_DESCRIPTION = (
    "DIRECTIONAL intraday momentum-breakout / scalping on a fast (5-minute) timeframe: a "
    "prior-range breakout with retest/bounce and a hammer/engulfing reversal-candle entry "
    "(the 'break and bounce' video), or the indicator parameterizations -- fast MA above slow "
    "MA, current close above the close 20 bars ago, green-body / non-wicky candle, optional "
    "Z-score filter, VWMA/Bollinger buy-the-dip -- long and short mirrored, with FIXED "
    "percentage stop / take-profit brackets. The edge claim is short-horizon directional "
    "price continuation/reversal timing, i.e. single-asset TIMING, not a new structural axis.")

REVIEWED_VARIANTS = (
    {"key": "break_and_bounce_reversal_candle",
     "desc": "prior-day range box -> 15m breakout close -> 5m hammer/engulfing reversal entry, "
             "fixed R-multiple target (~2-3x stop), first 2.5h of session (video core)"},
    {"key": "fast_ma_over_slow_ma_momentum_breakout",
     "desc": "fast MA above slow MA + close above close 20 bars ago + green candle, entry at "
             "next open, 1.5% stop / 3% take-profit, short mirrored"},
    {"key": "sma50_over_sma100",
     "desc": "SMA50 above SMA100 trend filter, 1% stop / 2% take-profit"},
    {"key": "ema10_over_sma50_zscore",
     "desc": "EMA10 above SMA50 + close above 20 bars ago + Z-score <= 2, 1.7% stop / 3% "
             "take-profit"},
    {"key": "sma_body_fraction_non_wicky",
     "desc": "SMA body-fraction / non-wicky candle + close above SMA100 + close above 20 bars "
             "ago (single-bar conviction continuation)"},
    {"key": "vwma_bollinger_buy_the_dip",
     "desc": "VWMA or Bollinger-style buy-the-dip mean-reversion variant, 1% stop / 2% "
             "take-profit"},
)

# --- overlap matrix vs C1-C24 (each component -> the prior family it duplicates) ----
# Every matched_family below is asserted to be present in the C1-C21 rejected ledger
# (anti-tamper: the no-go must cite REAL rejected families), except the C22/C23/C24
# shape rows which reference the in-flight/queued candidates.
OVERLAP_MATRIX = (
    {"component": "fast MA above slow MA (trend filter), SMA50>SMA100, EMA10>SMA50",
     "matched_family": "h4_trend_following_market_structure",
     "also": "long_biased_trend_continuation",
     "overlap": "HIGH",
     "note": "moving-average trend-following is C18 (rejected at fee-honest replay: did not "
             "beat BTC buy-and-hold risk-adjusted, forward-OOS failed); only the timeframe "
             "differs"},
    {"component": "close above the close 20 bars ago (momentum)",
     "matched_family": "slow_vol_targeted_time_series_momentum",
     "also": "",
     "overlap": "HIGH",
     "note": "lookback-return time-series momentum is C15 (beat random-entry but LOST to "
             "buy-and-hold, net-negative bear regime); the 20-bar lookback is a parameter"},
    {"component": "green-body / non-wicky / hammer / engulfing reversal candle",
     "matched_family": "conviction_bar_follow_through",
     "also": "",
     "overlap": "HIGH",
     "note": "single-bar conviction/reversal-candle timing is C14 (genuine timing signal but "
             "LOST to buy-and-hold and FAILED forward-OOS)"},
    {"component": "prior-range breakout + retest/pullback bounce entry",
     "matched_family": "crypto_intraday_breakout_pullback_structure",
     "also": "",
     "overlap": "HIGH",
     "note": "intraday breakout-pullback structure is C3/C4 (rejected); 'break and bounce' is "
             "breakout + pullback by another name"},
    {"component": "VWMA / Bollinger buy-the-dip + 'bounce' off a level (mean-reversion)",
     "matched_family": "liquidity_sweep_mean_reversion",
     "also": "low_volume_downside_capitulation_mean_reversion",
     "overlap": "HIGH",
     "note": "buy-the-dip / bounce mean-reversion overlaps C8/C9 (net-negative after costs, "
             "worse than random entry)"},
    {"component": "Z-score / volatility filter on entries",
     "matched_family": "volatility_compression_expansion",
     "also": "",
     "overlap": "MEDIUM",
     "note": "a volatility filter is a gating parameter (overlaps the C-series vol-state work), "
             "not a new edge axis"},
    {"component": "fixed % stop/take-profit brackets (1.5/3, 1/2, 1.7/3) + 5m timeframe",
     "matched_family": "",
     "also": "",
     "overlap": "PARAMETER_ONLY",
     "note": "bracket sizes + timeframe are PARAMETER choices, not a mechanism -- a multiple "
             "-comparisons / overfitting surface, never a distinctness source"},
    {"component": "directional single-asset long/short intraday timing (overall shape)",
     "matched_family": "",
     "also": C22_FAMILY,
     "overlap": "SHAPE_DIRECTIONAL",
     "note": "same DIRECTIONAL timing shape as C22 (external trend-radar) and every rejected "
             "directional family; the OPPOSITE of the NEUTRAL high-breadth shape chosen for "
             "C23 (low-vol) and C24 (illiquidity) precisely because directional timing keeps "
             "failing top-winner-removal + buy-and-hold + forward-OOS"},
)

# --- distinctness assessment ------------------------------------------------
DISTINCTNESS_ASSESSMENT = {
    "is_materially_distinct_enough_for_c25": False,
    "introduces_new_edge_axis": False,
    "edge_axis": "short_horizon_directional_price_timing_already_covered",
    "is_recombination_of_rejected_families": True,
    "is_reparameterization_of_rejected_families": True,
    "distinct_from_c23_c24_but_returns_to_rejected_directional_shape": True,
    "neutral_high_breadth_shape": False,
    "matched_rejected_family_count": 6,
    "reason": (
        "every mechanism in the family maps to an already-REJECTED directional/mean-reversion "
        "family (C3/C4 breakout-pullback, C14 conviction/reversal candle, C15 time-series "
        "momentum, C18 MA trend-following, C8/C9 buy-the-dip); the only novel elements are the "
        "5-minute timeframe and fixed % brackets, which are PARAMETERS, not a new edge axis. "
        "It re-enters the directional single-asset-timing shape that has failed at every gate "
        "and that C23/C24 were deliberately designed to avoid."),
}

# --- required skepticism (encoded as hard review flags) ---------------------
SKEPTICISM_FLAGS = {
    "video_and_backtest_claims_unverified": True,
    "win_rate_and_profit_factor_treated_as_unverified": True,
    "overfitting_risk_multiple_variants_and_brackets": True,
    "five_minute_scalping_cost_slippage_risk": True,
    "high_turnover_churn_destroys_edge_c20_lesson": True,
    "high_drawdown_unacceptable_without_strict_fee_honest_drawdown_gate": True,
    "must_beat_realistic_costs_not_just_buy_and_hold": True,
    "must_beat_correct_benchmark_not_buy_and_hold_only": True,
    "stocks_demo_does_not_transfer_to_crypto_perp_cost_regime": True,
}

COST_DRAWDOWN_CONCERNS = (
    "5-minute scalping implies HIGH turnover; at SPARTA's reserved ~37 bps all-in per "
    "round-trip, the C20 arithmetic (704 round-trips x 74 bps = 521% cost drag turned +21% "
    "gross into -74.5% net) shows high-frequency directional churn is the single most likely "
    "killer -- any future version must be judged NET of a fee-honest, slippage-aware cost "
    "overlay, not on gross/video numbers",
    "fixed % brackets (1.5/3, 1/2, 1.7/3) across multiple indicator variants are a "
    "multiple-comparisons / curve-fitting surface; the 70% win-rate / 1.6 profit-factor video "
    "claims are UNVERIFIED and must be treated as marketing until independently replayed",
    "high-drawdown variants are UNACCEPTABLE without a strict fee-honest maximum-drawdown gate; "
    "lower drawdown alone is not an edge (the C17/C18 lesson) and a correct benchmark (not just "
    "buy-and-hold) must be beaten net of cost",
    "the video demo is on STOCKS in the cash-session open; the crypto perp cost/slippage/24-7 "
    "regime is materially harsher, so the demonstrated behaviour does not transfer",
)

# --- queue preservation (reported, never mutated) ---------------------------
QUEUE_SNAPSHOT = {
    "c22_active_collection": True,
    "c22_progress": C22_PROGRESS,
    "c22_state": C22_STATE,
    "c22_replay_locked": True,
    "c23_on_deck": True,
    "c24_queued_behind_c23": True,
    "c25_created_as_proposal": False,
    "c25_opened_as_active": False,
    "queue_order": ("C22_active", "C23_on_deck", "C24_behind_c23", "C25_not_created_no_go"),
}

# no token opens C25; the only forward path is a CONDITIONAL human revisit IF (and only if) a
# materially-distinct, cost-survivable reformulation is later proposed.
CONDITIONAL_REVISIT_TOKEN = (
    "HUMAN_DECISION_REVISIT_C25_ONLY_IF_MATERIALLY_DISTINCT_COST_SURVIVABLE_REFORMULATION")
NEXT_GATE = "NONE_NO_GO_REMAINS_IDEA_BANK"

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "builds_candidate_files", "builds_spec", "builds_c25_proposal",
    "promotes_to_c25_proposal", "runs_detector", "runs_labels", "runs_replay", "runs_backtest",
    "computes_pnl", "optimizes_parameters", "reparameterizes", "tunes_parameters",
    "runs_rescue", "reproposes_rejected_family", "runs_robustness", "fetches_data",
    "reads_real_data", "mutates_data", "stages_data", "opens_c25_as_active",
    "opens_c24_as_active", "opens_c23_as_active", "displaces_active_c22", "advances_c22",
    "touches_c22_pipeline", "modifies_c21_files", "modifies_c22_files", "modifies_c23_files",
    "modifies_c24_files", "modifies_lane_status_surface", "auto_commits", "auto_pushes",
    "modifies_scheduler", "installs_scheduler", "sends_notifications", "calls_api",
    "uses_network", "uses_credentials", "uses_api_keys", "connects_signum", "uses_mcp",
    "uses_trader_dev_mcp", "accesses_hyperliquid", "connects_broker", "connects_exchange",
    "sends_trades", "edits_bots", "creates_claude_routines", "uses_real_money", "places_orders",
    "contains_order_logic", "adds_new_instrument_class", "paper_trading", "live_trading",
    "deploys_capital", "promotes_gate", "unlocks_downstream_gate", "skips_any_gate",
    "advances_without_human_approval", "claims_profitability", "claims_edge",
    "crosses_into_forbidden_gate",
)


def get_c25_intake_review_label() -> str:
    return (
        "Candidate #25 INTAKE + DISTINCTNESS REVIEW (READ-ONLY, RESEARCH ONLY, NO-GO). The "
        "uploaded 'break and bounce' / 5-minute momentum-breakout scalping family is a "
        "RECOMBINATION + RE-PARAMETERIZATION of already-rejected directional families "
        "(C3/C4 breakout-pullback, C14 conviction/reversal candle, C15 time-series momentum, "
        "C18 MA trend-following, C8/C9 buy-the-dip) on a faster timeframe with fixed brackets -- "
        "NOT a materially new edge axis, and the OPPOSITE of the NEUTRAL shape of C23/C24. "
        "5-minute scalping makes the C20 churn/cost problem acute and the video win-rate / "
        "profit-factor claims are UNVERIFIED with overfitting + drawdown risk. Recommendation: "
        "REMAIN IDEA-BANK NO-GO; do NOT promote to C25. Queue preserved: C22 active (2/20, "
        "replay locked), C23 on-deck, C24 behind C23, C25 NOT created. NOT a profitability "
        "claim; advances nothing.")


def get_c25_intake_review_next_gate() -> str:
    return NEXT_GATE


def _rows(seq) -> list:
    return [dict(r) for r in seq]


def build_c25_intake_review() -> dict[str, Any]:
    """Assemble the frozen C25 intake / distinctness-review record. Pure; no I/O; review only;
    NO-GO. Anti-tamper-gated: the no-go must cite REAL rejected families and must NOT mark the
    family materially distinct."""
    blockers: list = []
    if len(REJECTED_FAMILIES_C1_TO_C21) != 26:
        blockers.append("rejected_ledger_not_26")
    # every cited matched_family must be a REAL rejected family (no fabricated citations)
    for row in OVERLAP_MATRIX:
        fam = row.get("matched_family")
        if fam and fam not in REJECTED_FAMILIES_C1_TO_C21:
            blockers.append("cited_family_not_in_ledger:%s" % fam)

    record: dict[str, Any] = {
        "schema_version": C25R_SCHEMA_VERSION, "mode": C25R_MODE, "lane": C25R_LANE,
        "label": get_c25_intake_review_label(),
        "review_id": REVIEW_ID, "reviewed_family": REVIEWED_FAMILY, "source": SOURCE,
        "intake_kind": "DISTINCTNESS_REVIEW",
        "is_pure_review_only": True,
        "is_proposal": False,
        "approved_via": REVIEW_TOKEN,
        "blockers": blockers,
        "verdict": (VERDICT_NO_GO if not blockers else "C25_REVIEW_BLOCKED"),
        "recommendation": RECOMMENDATION,
        "is_materially_distinct_enough_for_c25": False,
        # the required sections
        "family_description": FAMILY_DESCRIPTION,
        "reviewed_variants": _rows(REVIEWED_VARIANTS),
        "overlap_matrix": _rows(OVERLAP_MATRIX),
        "distinctness_assessment": dict(DISTINCTNESS_ASSESSMENT),
        "skepticism_flags": dict(SKEPTICISM_FLAGS),
        "cost_drawdown_concerns": list(COST_DRAWDOWN_CONCERNS),
        # queue preservation (reported, never mutated)
        "queue_snapshot": {k: (list(v) if isinstance(v, tuple) else v)
                           for k, v in QUEUE_SNAPSHOT.items()},
        "active_candidate_in_flight": "C22",
        "c22_state_unchanged": C22_STATE,
        "c22_progress_unchanged": C22_PROGRESS,
        "c23_on_deck_unchanged": True,
        "c24_queued_behind_c23_unchanged": True,
        "does_not_open_c25_as_active": True,
        "does_not_open_c24_as_active": True,
        "does_not_open_c23_as_active": True,
        "does_not_advance_c22": True,
        "does_not_touch_c22_collection_pipeline": True,
        "does_not_modify_c21_c22_c23_c24_files": True,
        "does_not_modify_lane_status_surface": True,
        "is_additive_new_surface_only": True,
        # next gate
        "next_gate": NEXT_GATE,
        "conditional_revisit_token": CONDITIONAL_REVISIT_TOKEN,
        "creates_c25_proposal": False,
        "promotes_to_c25": False,
        "advances_nothing": True,
        "human_review_required": True,
        "buy_and_hold_is_not_the_only_benchmark": True,
        "must_beat_realistic_costs_and_correct_benchmark": True,
        "rejected_families_count": len(REJECTED_FAMILIES_C1_TO_C21),
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_build": True, "no_write": True, "no_execute": True, "no_spec": True,
        "no_detector": True, "no_dry_run": True, "no_labels": True, "no_replay": True,
        "no_backtest": True, "no_pnl": True, "no_optimization": True,
        "no_reparameterization": True, "no_tuning": True, "no_rescue": True,
        "no_robustness": True, "no_data_fetch": True, "no_real_data_access": True,
        "no_new_instrument_class": True, "no_stage": True, "no_commit": True, "no_push": True,
        "no_auto_commit": True, "no_auto_push": True, "no_create_c25_proposal": True,
        "no_promote_to_c25": True, "no_open_c25_as_active": True, "no_open_c24_as_active": True,
        "no_open_c23_as_active": True, "no_advance_c22": True, "no_touch_c22_pipeline": True,
        "no_modify_c21_c22_c23_c24_files": True, "no_modify_lane_status": True,
        "no_scheduler_change": True, "no_scheduler_install": True, "no_signum_connection": True,
        "no_mcp": True, "no_trader_dev_mcp": True, "no_hyperliquid": True, "no_api_keys": True,
        "no_credentials": True, "no_bot_edits": True, "no_claude_routines": True,
        "no_send_trades": True, "no_broker": True, "no_order_logic": True,
        "no_paper_trading": True, "no_live_trading": True, "no_gate_skip": True,
        "no_rejected_family_repropose": True, "no_downstream_gate_unlock": True,
        "no_profitability_claim": True, "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_c25_intake_review(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the record is research-only, review-only (NOT a
    proposal), a NO-GO that does NOT mark the family materially distinct, cites only REAL
    rejected families with at least four HIGH overlaps, encodes the required skepticism
    (unverified claims, overfitting, 5-minute scalping cost/slippage, drawdown gate, beat
    realistic costs + correct benchmark), preserves the C22/C23/C24 queue without creating a
    C25 proposal or mutating anything, and pins every capability flag False."""
    failures: list = []
    if record.get("mode") != C25R_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_pure_review_only") is not True:
        failures.append("not_pure_review_only")
    if record.get("is_proposal") is not False:
        failures.append("must_not_be_a_proposal")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("verdict") != VERDICT_NO_GO:
        failures.append("verdict_not_no_go")
    if record.get("recommendation") != RECOMMENDATION:
        failures.append("recommendation_not_idea_bank_no_go")

    # NO-GO core: must NOT be marked materially distinct; must be a recombination
    if record.get("is_materially_distinct_enough_for_c25") is not False:
        failures.append("must_not_be_materially_distinct")
    da = record.get("distinctness_assessment") or {}
    if da.get("is_materially_distinct_enough_for_c25") is not False:
        failures.append("assessment_distinct_flag_must_be_false")
    if da.get("introduces_new_edge_axis") is not False:
        failures.append("assessment_new_axis_must_be_false")
    if da.get("is_recombination_of_rejected_families") is not True:
        failures.append("assessment_must_be_recombination")
    if da.get("neutral_high_breadth_shape") is not False:
        failures.append("must_not_claim_neutral_shape")

    # overlap matrix: cite only REAL rejected families; >= 4 HIGH overlaps; covers the
    # directional-shape row vs C22/C23/C24
    matrix = record.get("overlap_matrix") or []
    if len(matrix) < 6:
        failures.append("overlap_matrix_too_small")
    highs = [r for r in matrix if r.get("overlap") == "HIGH"]
    if len(highs) < 4:
        failures.append("insufficient_high_overlaps")
    for r in matrix:
        fam = r.get("matched_family")
        if fam and fam not in REJECTED_FAMILIES_C1_TO_C21:
            failures.append("cited_family_not_in_ledger:%s" % fam)
        if not r.get("component") or not r.get("note"):
            failures.append("overlap_row_incomplete")
            break
    matched = {r.get("matched_family") for r in matrix if r.get("matched_family")}
    for must in ("h4_trend_following_market_structure",
                 "slow_vol_targeted_time_series_momentum",
                 "conviction_bar_follow_through",
                 "crypto_intraday_breakout_pullback_structure"):
        if must not in matched:
            failures.append("overlap_missing_%s" % must)
    shape_rows = " ".join(str(r.get("also", "")) + " " + str(r.get("note", ""))
                          for r in matrix)
    if C22_FAMILY not in shape_rows:
        failures.append("missing_directional_shape_vs_c22")
    if "C23" not in shape_rows or "C24" not in shape_rows:
        failures.append("missing_shape_contrast_vs_c23_c24")

    # required skepticism flags all present + True
    sf = record.get("skepticism_flags") or {}
    for k in ("video_and_backtest_claims_unverified",
              "overfitting_risk_multiple_variants_and_brackets",
              "five_minute_scalping_cost_slippage_risk",
              "high_turnover_churn_destroys_edge_c20_lesson",
              "high_drawdown_unacceptable_without_strict_fee_honest_drawdown_gate",
              "must_beat_realistic_costs_not_just_buy_and_hold",
              "must_beat_correct_benchmark_not_buy_and_hold_only"):
        if sf.get(k) is not True:
            failures.append("skepticism_flag_off_%s" % k)
    if len(record.get("cost_drawdown_concerns") or []) < 3:
        failures.append("insufficient_cost_drawdown_concerns")

    # queue preservation + no mutation + no proposal creation
    qs = record.get("queue_snapshot") or {}
    if qs.get("c22_state") != C22_STATE:
        failures.append("queue_c22_state_wrong")
    if qs.get("c22_progress") != C22_PROGRESS:
        failures.append("queue_c22_progress_wrong")
    if qs.get("c22_replay_locked") is not True:
        failures.append("queue_c22_replay_not_locked")
    if qs.get("c23_on_deck") is not True:
        failures.append("queue_c23_not_on_deck")
    if qs.get("c24_queued_behind_c23") is not True:
        failures.append("queue_c24_not_behind_c23")
    if qs.get("c25_created_as_proposal") is not False:
        failures.append("queue_c25_must_not_be_created")
    for k in ("does_not_open_c25_as_active", "does_not_open_c24_as_active",
              "does_not_open_c23_as_active", "does_not_advance_c22",
              "does_not_touch_c22_collection_pipeline",
              "does_not_modify_c21_c22_c23_c24_files",
              "does_not_modify_lane_status_surface"):
        if record.get(k) is not True:
            failures.append("preservation_off_%s" % k)
    if record.get("creates_c25_proposal") is not False:
        failures.append("must_not_create_c25_proposal")
    if record.get("promotes_to_c25") is not False:
        failures.append("must_not_promote_to_c25")
    if record.get("advances_nothing") is not True:
        failures.append("must_advance_nothing")
    if record.get("next_gate") != NEXT_GATE:
        failures.append("next_gate_wrong")
    if record.get("must_beat_realistic_costs_and_correct_benchmark") is not True:
        failures.append("must_require_realistic_costs_and_correct_benchmark")
    if record.get("rejected_families_count") != 26:
        failures.append("ledger_not_26")

    locks = record.get("scope_locks") or {}
    for key in ("no_build", "no_spec", "no_detector", "no_dry_run", "no_labels", "no_replay",
                "no_optimization", "no_data_fetch", "no_commit", "no_push",
                "no_create_c25_proposal", "no_promote_to_c25", "no_open_c25_as_active",
                "no_open_c24_as_active", "no_open_c23_as_active", "no_advance_c22",
                "no_touch_c22_pipeline", "no_modify_c21_c22_c23_c24_files",
                "no_modify_lane_status", "no_signum_connection", "no_mcp", "no_trader_dev_mcp",
                "no_hyperliquid", "no_api_keys", "no_credentials", "no_broker",
                "no_order_logic", "no_paper_trading", "no_live_trading", "no_gate_skip",
                "no_rejected_family_repropose"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
