"""SPARTA CANDIDATE #9 FAMILY PROPOSAL (READ-ONLY, RESEARCH ONLY,
PROPOSAL GATE ONLY):
LOW_VOLUME_DOWNSIDE_CAPITULATION_MEAN_REVERSION_V1.

Drafted via the pushed Rejected Family Blacklist V4 schema (which
extended V3 with the C8 entry `liquidity_sweep_mean_reversion`) and
validated through BOTH pushed gate layers: Autopilot Loop V1's
validate_candidate_family_proposal / screen_output_language gates
AND Recommendation V1's hard rejection rules. BLOCKED if the EIGHT-
record ledger (C1-C8), V4, V3, V2, Recommendation V1, or the
Autopilot Loop V1 stops certifying, or if the family equals any
rejected family name from any pushed rejection-family tuple.

CLEAN HYPOTHESIS (evidence language only): candidate #9 tests
whether a JOINT price-and-volume trigger on BTCUSD 15m bars -- a
completed 15m bar whose close-to-close log return is strictly below
a fee-aware downside z-score over a rolling 96-bar window AND whose
volume is strictly below the median volume over the same 96-bar
window -- followed by an entry on the close of the NEXT completed
bar (no intrabar entry), produces fee-viable mean-reversion long
labels at 27 bps round-trip with the 81 bps gross target-distance
floor, on a per-symbol minimum-bar-gap clustering policy and a
sample-size adequacy assessment built in at proposal time. The
EDGE HYPOTHESIS is a microstructure asymmetry -- not a chart
pattern -- between the panic price set by depleted top-of-book bid
liquidity and the deeper-book patient-buyer reference price that
re-marks shortly after.

C8 LESSON ANSWERED AT PROPOSAL TIME (V4-required field): an
explicit_edge_argument_beyond_pattern_geometry field is built in.
The argument is structural, not visual: the joint price-AND-volume
condition is a proxy for the order-book asymmetry that produces the
mean reversion, not a candle shape that resembles one.

MATERIAL DIFFERENCES from C1-C8 (each listed explicitly):
  - NOT C1 (ny session fvg/choch): no session window, no fair-value
    gap, no change-of-character; trigger is volume-conditioned
    statistical excursion, not session-anchored structure;
  - NOT C2 (breakout-pullback): the trigger is the EXTREME
    downside excursion itself, not a range breakout or a pullback
    after a breakout; the trade direction is MEAN-REVERTING against
    the move, not continuing it;
  - NOT C3 (btc/sol long trend continuation): single-symbol BTCUSD
    only; no cross-symbol trend filter; trade direction is counter-
    trend by construction;
  - NOT C4 (sol/btc 1h swing structure): single-symbol BTCUSD only;
    no pair coupling; no swing-pivot trigger;
  - NOT C5 (eth/sol relative strength pullback continuation): no
    pairwise rs comparison; no pullback-after-rs-lead structure;
  - NOT C6 (multi-symbol relative-strength rotation/rank): single-
    symbol BTCUSD only; no cross-sectional rank, no top-ranked
    filter;
  - NOT C7 (volatility compression-expansion): no ATR contraction,
    no ATR-rolling-average comparison, no expansion multiplier; the
    trigger is a JOINT price-AND-volume condition on a single bar;
  - NOT C8 (liquidity sweep mean reversion): no sweep-below-prior-
    lookback-low geometry, no reclaim-window-with-upper-third
    confirmation; the trigger is statistical (z-score) and
    microstructural (below-median volume) on a SINGLE bar; entry is
    on the NEXT bar's close (no reclaim-confirmation pattern).

C6 ANTI-CLUSTER LESSON BAKED IN AT PROPOSAL TIME (not as a future
edit): a built-in minimum-bar-gap clustering constraint between
accepted setups on the same symbol is part of the family
hypothesis. NOT the single allowed C9 edit token.

C7 SAMPLE-SIZE ADEQUACY LESSON BAKED IN AT PROPOSAL TIME (not as a
future edit): a built-in minimum-accepted-setup-count threshold
checked at the labels-review gate. NOT the single allowed C9 edit
token.

C8 EXPLICIT-EDGE-ARGUMENT LESSON BAKED IN AT PROPOSAL TIME (the
V4-required field): an explicit_edge_argument_beyond_pattern
_geometry field carries the structural microstructure claim and is
required at the proposal level by V4 -- this is NOT the single C9
edit token either.

This is a PROPOSAL. It runs no detector, fetches nothing, builds
no labels, replays nothing, creates no artifacts/runners/
schedulers/data/PnL, and the next stage is candidate_spec review
by the human -- not detector execution. Seeds are inspiration and
risk-control lessons only, never rescue paths; no C1-C8 setup_ids,
replay rows, labels, edited labels, or rejected geometry may be
reused as candidate #9 evidence.
"""

from __future__ import annotations

from typing import Any

import sparta_commander.strategy_factory_autopilot_research_loop_v1_contract as _loop
import sparta_commander.strategy_factory_candidate_recommendation_v1_contract as _rec
from sparta_commander.btc_sol_long_trend_continuation_v1_result_and_rejection_record_contract import (
    REJECTION_STATUS as C3_STATUS,
)
from sparta_commander.crypto_intraday_breakout_pullback_structure_v2_result_and_rejection_record_contract import (
    REJECTION_STATUS as C2_STATUS,
)
from sparta_commander.eth_sol_relative_strength_rejection_record_contract import (
    REJECTION_STATUS as C5_STATUS,
)
from sparta_commander.liquidity_sweep_mean_reversion_v1_rejection_record import (
    REJECTION_STATUS as C8_STATUS,
)
from sparta_commander.multi_symbol_relative_strength_rotation_filter_rejection_record_contract import (
    REJECTION_STATUS as C6_STATUS,
)
from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
    REJECTION_STATUS as C1_STATUS,
)
from sparta_commander.sol_btc_long_1h_swing_structure_rejection_record_contract import (
    REJECTION_STATUS as C4_STATUS,
)
from sparta_commander.strategy_factory_overnight_research_autopilot_v2_contract import (
    REJECTED_FAMILY_LOGIC_BLACKLIST as V2_BLACKLIST,
    VERDICT_OAP2_READY,
    build_overnight_research_autopilot_v2_contract,
)
from sparta_commander.strategy_factory_rejected_family_blacklist_v3_contract import (
    REJECTED_FAMILY_LOGIC_BLACKLIST_V3 as V3_BLACKLIST,
    VERDICT_BL3_READY,
    build_rejected_family_blacklist_v3,
)
from sparta_commander.strategy_factory_rejected_family_blacklist_v4_contract import (
    REJECTED_FAMILY_LOGIC_BLACKLIST_V4 as V4_BLACKLIST,
    VERDICT_BL4_READY,
    build_rejected_family_blacklist_v4,
)
from sparta_commander.volatility_compression_expansion_v1_rejection_record import (
    REJECTION_STATUS as C7_STATUS,
)

C9P_SCHEMA_VERSION = (
    "low_volume_downside_capitulation_mean_reversion_v1_family"
    "_proposal.v1")
C9P_LABEL = ("SPARTA Candidate #9 Family Proposal "
             "(READ-ONLY, RESEARCH ONLY, PROPOSAL GATE ONLY, "
             "VALIDATED BY AUTOPILOT LOOP V1 AND RECOMMENDATION V1, "
             "DRAFTED VIA REJECTED FAMILY BLACKLIST V4 SCHEMA, "
             "EXPLICIT EDGE ARGUMENT BEYOND PATTERN GEOMETRY "
             "REQUIRED, NOT A RESCUE, NOT A CLAIM)")
C9P_MODE = "RESEARCH_ONLY"
VERDICT_C9P_READY = "CANDIDATE_9_FAMILY_PROPOSAL_READY"
VERDICT_C9P_BLOCKED = "CANDIDATE_9_FAMILY_PROPOSAL_BLOCKED"
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_CANDIDATE_9_SPEC_REVIEW"
NEXT_LOOP_STAGE = "candidate_spec"

CANDIDATE_ID = (
    "LOW_VOLUME_DOWNSIDE_CAPITULATION_MEAN_REVERSION_V1")
CANDIDATE_FAMILY = (
    "low_volume_downside_capitulation_mean_reversion")

CLEAN_HYPOTHESIS = (
    "candidate #9 tests whether a JOINT price-and-volume trigger on "
    "btcusd 15m bars -- a completed 15m bar whose close-to-close "
    "log return is strictly below a fee-aware downside z-score over "
    "a rolling 96-bar window AND whose volume is strictly below the "
    "median volume over the same 96-bar window -- followed by an "
    "entry on the close of the NEXT completed 15m bar (no intrabar "
    "entry; the next bar confirms the panic does not continue), "
    "produces fee-viable mean-reversion long labels at 27 bps round-"
    "trip with the 81 bps gross target-distance floor, on a per-"
    "symbol minimum-bar-gap clustering policy and a sample-size "
    "adequacy assessment built in at proposal time; single-symbol, "
    "15m, long-only, labels-only research; the edge hypothesis is a "
    "microstructure asymmetry between the panic price set by "
    "depleted top-of-book bid liquidity and the deeper-book patient-"
    "buyer reference price that re-marks shortly after -- this is "
    "NOT a chart pattern, NOT a cross-symbol filter, NOT a trend "
    "continuation, NOT a volatility-regime trigger, NOT a sweep-"
    "reclaim event")

EDGE_SOURCE_HYPOTHESIS = (
    "the structural source of the proposed edge is order-book "
    "ASYMMETRY at the trigger bar moment: a large downside "
    "excursion that occurs while volume is below the rolling "
    "median is, by construction, NOT driven by committed "
    "institutional selling (which would push volume above median); "
    "instead it reflects depleted top-of-book bid liquidity that "
    "let a small number of stops/liquidations clear the visible "
    "book and reprice the asset to the next deeper bid level; the "
    "deeper book (institutional vwap-anchored desks, market-maker "
    "mean-reverting inventory, opportunistic prop traders) has not "
    "yet stepped in; as those deeper bids step in and re-mark the "
    "book toward the rolling reference price, the panic-driven "
    "price moves back up; the edge is the GAP between the panic "
    "price and the deeper-book reference price; the 27 bps fee + "
    "81 bps floor naturally screen out small excursions where the "
    "gap is too narrow to clear costs; only structurally large "
    "excursions pass the floor")

EXPLICIT_EDGE_ARGUMENT_BEYOND_PATTERN_GEOMETRY = (
    "1) THE CLAIM IS MICROSTRUCTURAL, NOT VISUAL: the joint price-"
    "AND-volume condition is a proxy for an order-book asymmetry "
    "that produces the mean reversion. The chart shape (a single "
    "down-bar) is a CONSEQUENCE of the structural setup, not the "
    "source of edge. A pure chart pattern (e.g., a down-bar on "
    "above-median volume) would have a different and probably "
    "negative expectancy.\n"
    "2) WHY VOLUME IS THE EDGE: when committed institutional "
    "selling drives a downside move, volume rises in lockstep with "
    "price. When the move is driven by depleted top-of-book bid "
    "liquidity (a stop run, a thin-book cascade), the dollar value "
    "transacted is much smaller relative to the price impact -- "
    "low volume IS the signature of structural rather than "
    "fundamental selling.\n"
    "3) WHY MEAN REVERSION SHOULD FOLLOW: the deeper book (vwap-"
    "anchored institutional bids, market-maker mean-reverting "
    "inventory, opportunistic prop traders) has a reference price "
    "that did NOT move with the top-of-book cascade. Those agents "
    "post bids back at the deeper reference; their bids are "
    "structurally above the panic clearing price; price re-marks "
    "upward to clear those bids. The mean reversion is a "
    "MECHANICAL consequence of the asymmetry, not a behavioral "
    "guess.\n"
    "4) WHY 27 BPS + 81 BPS NATURALLY SCREENS: the EXPECTED gap "
    "between the panic price and the deeper-book reference must "
    "exceed the 81 bps gross target-distance floor for any "
    "structural reversal to be tradeable; for excursions where the "
    "gap is below 81 bps, the deeper book absorbs the excursion "
    "without a tradeable reversal -- those are correctly filtered "
    "out at label time.\n"
    "5) WHY THIS IS NOT C8: c8 used a SWEEP geometry (penetrate "
    "below a 96-bar low by a fixed atr multiple) and a RECLAIM "
    "confirmation (a later bar closes back above with an upper-"
    "third confirmation). C9 uses NO geometric reference low and "
    "NO reclaim confirmation. C9 enters on the close of the bar "
    "AFTER the trigger bar regardless of whether that next bar "
    "recovers price -- because the EDGE is in the order-book re-"
    "marking that happens in the minutes AFTER the panic clearing, "
    "not in a visual reclaim pattern. The two families test "
    "STRUCTURALLY DIFFERENT EDGES and may both fail; the C8 "
    "rejection does NOT carry over to C9.\n"
    "6) HOW THIS RESPECTS THE C8 LESSON: the C8 lesson was that "
    "structural cleanliness alone does not produce edge; pattern "
    "geometry must be accompanied by an explicit edge claim. C9's "
    "explicit edge claim is the order-book asymmetry above; the "
    "claim is FALSIFIABLE by the per-variant net R sums at the "
    "replay gate; if all variants come out structurally net-"
    "negative in-sample, C9 is rejected for the same reason C8 "
    "was -- the proposed edge did not survive the 27 bps + 81 bps "
    "geometry. Spending the one allowed structural edit on a "
    "different z-score or volume percentile threshold is the only "
    "permitted contingency.")

EXPLICIT_NON_REUSE_OF_REJECTED_FAMILY_LOGIC = (
    "no C1-C8 setup_ids may be referenced as evidence",
    "no C1-C8 replay rows, labels, or relabel artifacts may be "
    "reused",
    "no C1-C8 rejected geometry may be reused unchanged",
    "no C1 ny-session window, no C1 fair-value-gap geometry, no "
    "C1 change-of-character structure",
    "no C2 range-breakout geometry, no C2 pullback retest structure",
    "no C3 trend-continuation filter, no C3 cross-symbol coupling",
    "no C4 swing-pivot trigger, no C4 sol/btc pair coupling",
    "no C5 pairwise relative-strength comparison",
    "no C6 multi-symbol rank, no C6 rotation filter",
    "no C7 atr contraction, no C7 atr-rolling-average comparison, "
    "no C7 expansion multiplier",
    "no C8 sweep-below-prior-low geometry, no C8 reclaim-window-"
    "with-upper-third confirmation, no C8 sweep-reference-low "
    "lookback",
)

RATIONALE_PARAGRAPH = (
    "Single-bar joint price-AND-volume triggers have not been "
    "tested in C1-C8. C1-C5 used pattern geometry (FVG/CHoCH, "
    "breakout-pullback, trend continuation, swing structure, "
    "relative strength). C6 used cross-symbol rank. C7 used "
    "volatility regime (price-only). C8 used liquidity sweep "
    "geometry (price-only). C9 introduces VOLUME as a first-class "
    "trigger gate paired with a fee-aware downside z-score. The "
    "structural argument is order-book asymmetry between thin-book "
    "panic clearing and patient deeper-book buyers; the empirical "
    "test is the per-variant fee-honest replay against the SAME "
    "staged BTCUSD 15m sample window 2026-05-02_2026-06-10. The "
    "BTCUSD 15m staged data already contains a volume column that "
    "the C1-C8 detectors did not use; this proposal is the first "
    "family in the lane to consume that column structurally. Anti-"
    "cluster and sample-size adequacy are built in at proposal "
    "time per the C6 and C7 lessons; the explicit edge argument "
    "above satisfies the V4 requirement introduced by the C8 "
    "rejection.")

DIFFERENCE_FROM_REJECTED_FAMILIES = (
    "1) not ny-session fvg/choch (no session window, no fvg, no "
    "choch); "
    "2) not generic breakout-pullback (no range breakout, no "
    "pullback retest; the entry is counter to the move, not with "
    "it); "
    "3) not btc/sol long trend continuation (single-symbol "
    "btcusd; no cross-symbol trend filter; direction is mean-"
    "reverting against the trigger bar); "
    "4) not sol/btc 1h swing structure (single-symbol; no pair "
    "coupling; no swing-pivot); "
    "5) not eth/sol relative-strength pullback continuation (no "
    "pairwise rs); "
    "6) not multi-symbol relative-strength rotation (no rank, no "
    "rotation, no cross-sectional filter); "
    "7) not volatility compression-expansion (no atr contraction, "
    "no atr-rolling-average comparison, no expansion multiplier); "
    "8) not liquidity sweep mean reversion (no sweep-below-prior-"
    "low geometry, no reclaim-window confirmation, no upper-third "
    "rule, no reference low lookback); "
    "9) the trigger is a JOINT price-and-volume condition on a "
    "single bar (z-score below threshold AND volume below median); "
    "10) the edge hypothesis is a microstructure asymmetry between "
    "thin-book panic and deeper-book reference, NOT a chart "
    "pattern; "
    "11) the c6 anti-cluster lesson is built into the proposal as "
    "a pre-committed per-symbol minimum-bar-gap policy, not a "
    "future edit; "
    "12) the c7 sample-size adequacy lesson is built into the "
    "proposal as a pre-committed minimum-accepted-setup-count "
    "threshold at the labels-review gate, not a future edit; "
    "13) the c8 explicit-edge-argument lesson is satisfied by the "
    "explicit_edge_argument_beyond_pattern_geometry field, not a "
    "future edit")

LOOP_PROPOSAL = {
    "family": CANDIDATE_FAMILY,
    "hypothesis": CLEAN_HYPOTHESIS,
    "difference_from_rejected_families":
        DIFFERENCE_FROM_REJECTED_FAMILIES,
    "uses_seeds_as_rescue": False,
}

# universe, timeframe, direction --------------------------------------------
SYMBOLS = ("BTCUSD",)
TIMEFRAME = "15m"
DIRECTION = "long_only"
DIRECTION_NOTE = "long-only research labels; never trading capability"
SAMPLE_WINDOW_PROPOSAL = "2026-05-02_2026-06-10"

# joint price-AND-volume trigger family (declarative; exact numerics
# frozen at spec review) ----------------------------------------------------
TRIGGER_FAMILY = {
    "name": "low_volume_downside_capitulation_event",
    "definition": (
        "1) rolling stats window: the prior n completed 15m bars; "
        "2) downside z-score condition: the trigger bar's close-to-"
        "close log return is strictly below (mean - z * std) of the "
        "rolling-window log returns; "
        "3) below-median volume condition: the trigger bar's volume "
        "is strictly below the median volume over the same rolling-"
        "window completed bars; "
        "4) JOINT trigger: BOTH the z-score and the volume "
        "conditions must hold on the SAME completed 15m bar; "
        "5) entry: on the CLOSE of the bar IMMEDIATELY AFTER the "
        "trigger bar (the post-panic confirmation bar); no intrabar "
        "entry; if the post-panic bar's low penetrates a structural "
        "stop before close, the setup is invalidated at the entry "
        "gate"),
    "uses_completed_15m_bars_only": True,
    "no_future_bars": True,
    "no_same_bar_lookahead": True,
    "no_intrabar_entry": True,
    "evaluation_starts_next_15m_bar_after_entry_close": True,
    "exact_numeric_form_frozen_at_spec_review": True,
    "is_a_joint_price_and_volume_microstructure_trigger": True,
    "is_not_a_cross_symbol_rs_filter": True,
    "is_not_a_session_anchored_trigger": True,
    "is_not_a_breakout_pullback_trigger": True,
    "is_not_a_trend_ma_filter": True,
    "is_not_a_swing_pivot_trigger": True,
    "is_not_an_atr_contraction_expansion_trigger": True,
    "is_not_a_relative_strength_rotation_trigger": True,
    "is_not_a_sweep_reclaim_trigger": True,
}

# structure-stop family (below the trigger bar's low) ----------------------
STOP_FAMILY = {
    "rule": ("structure-based stop: entry_price - (trigger_bar_low "
             "- stop_buffer); buffer expressed as a small atr-"
             "fraction of the rolling-window atr; final stop is at "
             "or below the trigger bar's low so a re-test of the "
             "panic low invalidates the setup"),
    "exact_form_frozen_at_spec_review": True,
    "never_tightened_after_entry": True,
    "stop_must_be_below_entry": True,
    "invalid_if_stop_distance_not_positive": True,
}

# target variants ----------------------------------------------------------
TARGET_VARIANTS = ("2r", "3r", "4r")
TARGET_POLICY = {
    "variants": TARGET_VARIANTS,
    "target_price_formula":
        "entry_price + r_multiple * stop_distance",
    "no_new_variants_after_label_freeze": True,
}

# fee-aware geometry policy (kept at the pushed lane standard) -------------
FEE_AWARE_GEOMETRY_POLICY = {
    "fee_model_round_trip_bps": 27,
    "minimum_gross_target_distance_floor_bps": 81,
    "floor_is_3x_round_trip_fees": True,
    "floor_checked_before_replay_eligibility": True,
    "no_maker_rebate_assumption": True,
    "no_zero_fee_assumption": True,
}

# C6 lesson: anti-cluster baked into the proposal at label time -----------
ANTI_CLUSTER_POLICY = {
    "built_in_at_label_emission_time": True,
    "scope": "per_symbol_minimum_bar_gap_between_accepted_events",
    "exact_min_bars_frozen_at_spec_review": True,
    "applies_before_replay_time_non_overlap": True,
    "replay_time_non_overlap_unchanged": True,
    "is_not_the_single_allowed_c9_edit": True,
    "reason_for_built_in":
        "c6_clustering_filter_edit_proved_density_was_structural",
}

# C7 lesson: sample-size adequacy assessed at proposal level ---------------
SAMPLE_SIZE_ADEQUACY_POLICY = {
    "built_in_at_proposal_time": True,
    "minimum_accepted_setup_count_threshold_frozen_at_spec_review":
        True,
    "applies_at_labels_review_gate": True,
    "below_threshold_triggers_structural_rejection_without_edit"
    "_token": True,
    "reason_for_built_in":
        "c7_zero_accepted_setups_proved_proposal_must_commit_a"
        "_minimum_evaluable_count_before_labels_are_emitted",
    "is_not_the_single_allowed_c9_edit": True,
}

# C8 lesson: explicit edge argument required at proposal time -------------
EXPLICIT_EDGE_ARGUMENT_POLICY = {
    "built_in_at_proposal_time": True,
    "v4_required_field": True,
    "argument_is_microstructural_not_visual": True,
    "argument_is_falsifiable_by_per_variant_net_r_sums": True,
    "is_not_the_single_allowed_c9_edit": True,
    "reason_for_built_in":
        "c8_all_three_variants_net_negative_in_sample_proved"
        "_pattern_geometry_alone_is_not_an_edge_source_and_the_v4"
        "_blacklist_requires_an_explicit_argument_at_proposal_time",
}

# replay-time same-symbol non-overlap (inherited risk control) ------------
NON_OVERLAP_POLICY = {
    "built_in_at_label_replay_policy_time": True,
    "evaluated_per_variant": True,
    "reduce_or_keep_only_never_add_trades": True,
    "is_not_an_edit_or_rescue_path": True,
}

# edit allowance (same one-token allowance as the pushed pattern) ---------
EDIT_ALLOWANCE_POLICY = (
    "at most ONE pre-committed edit for candidate #9, only if "
    "evidence-supported, only via a separately human-approved "
    "contract; if spent and results remain negative or below the "
    "sample-size adequacy threshold, candidate #9 is REJECTED_KEPT"
    "_ON_RECORD; the anti-cluster policy, the sample-size adequacy "
    "policy, AND the explicit-edge-argument field are NOT this "
    "edit token; the edit must target a different structural "
    "parameter (e.g., the z-score threshold, the volume percentile, "
    "the rolling-window size, or the structure-stop buffer "
    "multiplier) if spent")

# expected failure modes (frozen, evidence-language only) ----------------
EXPECTED_FAILURE_MODES = (
    "cost_prohibitive_small_excursions_failing_the_81_bps_floor_at"
    "_label_time",
    "low_volume_downside_excursions_during_strong_downtrends_where"
    "_the_mean_reversion_never_materializes_and_stops_are_hit",
    "single_symbol_sample_size_too_small_in_the_pushed_window_to"
    "_support_a_meaningful_kept_trade_count_per_variant_which_is"
    "_exactly_what_the_built_in_sample_size_adequacy_check_catches",
    "below_median_volume_thresholds_that_are_too_lenient_producing"
    "_many_trivial_setups_or_too_strict_producing_no_qualifying"
    "_setups",
    "z_score_thresholds_that_are_too_lenient_producing_small_non"
    "_tradeable_excursions_or_too_strict_producing_no_qualifying"
    "_setups",
    "rolling_window_choice_that_either_misses_regime_shifts_or_is"
    "_too_short_to_stabilize_the_volume_median",
    "any_post_edit_replay_remaining_net_negative_or_with_hit_rate"
    "_below_breakeven_at_any_variant",
    "structural_microstructure_argument_failing_empirically_in"
    "_the_pushed_sample_meaning_the_proposed_edge_did_not_survive"
    "_the_27_bps_plus_81_bps_geometry_which_would_be_a_clean"
    "_rejection_not_a_rescue_path",
)

# seeds (inspiration only, never rescue paths) ---------------------------
SEED_USAGE = (
    "c6_clustering_lesson_is_inspiration_for_built_in_anti_cluster"
    "_policy_not_rescue",
    "c7_sample_size_adequacy_lesson_is_inspiration_for_built_in"
    "_minimum_count_threshold_not_rescue",
    "c8_explicit_edge_argument_lesson_is_inspiration_for_built_in"
    "_microstructure_claim_field_not_rescue",
    "c5_thin_risk_fee_sensitivity_is_a_risk_control_lesson_only",
    "single_symbol_btcusd_15m_joint_price_volume_microstructure"
    "_trigger_is_a_clean_new_hypothesis_not_a_recombination_of"
    "_rejected_geometry",
    "the_btcusd_15m_volume_column_in_the_staged_data_is_a_new"
    "_input_that_c1_through_c8_did_not_consume_structurally",
    "no_c1_c8_setup_ids_replay_rows_labels_edited_labels_or_replay"
    "_results_may_be_reused_as_candidate_9_evidence",
)
SEEDS_ARE_NEVER_RESCUE_PATHS = True

PROMOTION_TO_HUMAN_REVIEW_CONDITIONS = (
    "fee-honest replay net-positive on the overlap-adjusted "
    "independent sample with sample size at or above the proposal-"
    "committed minimum",
    "all artifact hashes and gates certify",
    "promotion produces a human-review record only: no claim, no "
    "paper, no live, no capability change",
)

SAFETY_AND_NO_CLAIM = (
    "no trading, no paper trading, no live trading",
    "no wallet, account, api, or order capability",
    "no auto-push, no auto-commit",
    "no scheduler activation",
    "no profitability claim and no winner wording at any stage",
    "all output must be evidence language only",
    "every stage requires evidence freeze and explicit human gates",
)

# the V4 blacklist must include this family's eight rejected predecessors
ALL_KNOWN_REJECTED_FAMILIES = tuple(sorted(set(
    list(_loop.REJECTED_FAMILIES) + list(_rec.ALL_REJECTED_FAMILIES)
    + list(V2_BLACKLIST) + list(V3_BLACKLIST) + list(V4_BLACKLIST))))


def get_candidate_9_proposal_label() -> str:
    return C9P_LABEL


def build_candidate_9_family_proposal() -> dict[str, Any]:
    """Assemble the C9 proposal. Chain-gated on the EIGHT-record
    rejection ledger (C1-C8), the pushed V4 blacklist, V3, V2,
    Recommendation V1, and Autopilot Loop V1. Validated by the
    loop's validate_candidate_family_proposal + screen_output
    _language gates AND by Recommendation V1's apply_hard_rejection
    _rules."""
    record: dict[str, Any] = {
        "schema_version": C9P_SCHEMA_VERSION, "label": C9P_LABEL,
        "mode": C9P_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [],
        "candidate_id": CANDIDATE_ID,
        "candidate_family": CANDIDATE_FAMILY,
        "selected_candidate_id": CANDIDATE_ID,
        "clean_hypothesis": CLEAN_HYPOTHESIS,
        "edge_source_hypothesis": EDGE_SOURCE_HYPOTHESIS,
        "explicit_edge_argument_beyond_pattern_geometry":
            EXPLICIT_EDGE_ARGUMENT_BEYOND_PATTERN_GEOMETRY,
        "explicit_non_reuse_of_rejected_family_logic":
            list(EXPLICIT_NON_REUSE_OF_REJECTED_FAMILY_LOGIC),
        "rationale_paragraph": RATIONALE_PARAGRAPH,
        "difference_from_rejected_families":
            DIFFERENCE_FROM_REJECTED_FAMILIES,
        "loop_proposal": dict(LOOP_PROPOSAL),
        "loop_proposal_check": None,
        "hypothesis_language_check": None,
        "recommendation_hard_rules_check": None,
        "symbols": list(SYMBOLS), "timeframe": TIMEFRAME,
        "direction": DIRECTION, "direction_note": DIRECTION_NOTE,
        "sample_window_proposal": SAMPLE_WINDOW_PROPOSAL,
        "trigger_family": dict(TRIGGER_FAMILY),
        "stop_family": dict(STOP_FAMILY),
        "target_policy": {"variants": list(TARGET_VARIANTS),
                          "target_price_formula":
                              TARGET_POLICY["target_price_formula"],
                          "no_new_variants_after_label_freeze": True},
        "fee_aware_geometry_policy":
            dict(FEE_AWARE_GEOMETRY_POLICY),
        "anti_cluster_policy": dict(ANTI_CLUSTER_POLICY),
        "sample_size_adequacy_policy":
            dict(SAMPLE_SIZE_ADEQUACY_POLICY),
        "explicit_edge_argument_policy":
            dict(EXPLICIT_EDGE_ARGUMENT_POLICY),
        "non_overlap_policy": dict(NON_OVERLAP_POLICY),
        "edit_allowance_policy": EDIT_ALLOWANCE_POLICY,
        "expected_failure_modes": list(EXPECTED_FAILURE_MODES),
        "seed_usage": list(SEED_USAGE),
        "seeds_are_never_rescue_paths": SEEDS_ARE_NEVER_RESCUE_PATHS,
        "required_evidence_stages": list(_loop.LOOP_STAGES),
        "rejection_conditions": list(_loop.AUTO_REJECTION_RULES),
        "promotion_to_human_review_conditions": list(
            PROMOTION_TO_HUMAN_REVIEW_CONDITIONS),
        "safety_and_no_claim": list(SAFETY_AND_NO_CLAIM),
        "all_known_rejected_families": list(
            ALL_KNOWN_REJECTED_FAMILIES),
        "ledger_status_eight_records": None,
        "ledger_all_rejected_kept_on_record": None,
        "v4_blacklist_verdict": None,
        "v4_blacklist_clearance": None,
        "v3_blacklist_verdict": None,
        "v2_verdict": None,
        "recommendation_verdict": None,
        "autopilot_loop_verdict": None,
        "next_loop_stage": NEXT_LOOP_STAGE,
        "human_review_required": True,
        "human_review_required_at_every_gate": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True, "live_gate_locked": True,
        "is_a_rescue_attempt": False,
        "is_proposal_only": True,
        "plan_is_not_a_promotion": True,
        "executes": False, "writes_files": False, "labels_now": False,
        "runs_spec_review_now": False,
        "runs_detector": False, "runs_real_candle_detection": False,
        "runs_relabel": False, "runs_replay": False,
        "runs_real_detection_now": False, "runs_replay_now": False,
        "scores_now": False, "stages_data_now": False,
        "fetches_data": False, "calls_api": False, "uses_network": False,
        "uses_credentials": False, "uses_wallet": False,
        "uses_account": False, "connects_broker": False,
        "connects_exchange": False, "uses_real_money": False,
        "contains_order_logic": False,
        "contains_portfolio_allocation_logic": False,
        "starts_scheduler": False, "sends_notifications": False,
        "auto_commits": False, "auto_pushes": False,
        "creates_runners_now": False, "creates_data_artifacts_now":
            False,
        "creates_detector_label_replay_files_now": False,
        "creates_detector_implementation_now": False,
        "computes_pnl_now": False,
        "modifies_staged_market_data": False,
        "authorizes_paper_execution": False,
        "authorizes_micro_live": False, "authorizes_live_trading": False,
        "promotes_gate": False, "unlocks_downstream_gate": False,
        "claims_profitability": False,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    statuses = (C1_STATUS, C2_STATUS, C3_STATUS, C4_STATUS, C5_STATUS,
                C6_STATUS, C7_STATUS, C8_STATUS)
    record["ledger_status_eight_records"] = list(statuses)
    record["ledger_all_rejected_kept_on_record"] = all(
        s == "REJECTED_KEPT_ON_RECORD" for s in statuses)
    if not record["ledger_all_rejected_kept_on_record"]:
        record["verdict"] = VERDICT_C9P_BLOCKED
        record["blockers"].append("eight_record_ledger_broken")
        return record
    v4 = build_rejected_family_blacklist_v4()
    record["v4_blacklist_verdict"] = v4["verdict"]
    if v4["verdict"] != VERDICT_BL4_READY:
        record["verdict"] = VERDICT_C9P_BLOCKED
        record["blockers"].append("v4_blacklist_not_certifying")
        return record
    v3 = build_rejected_family_blacklist_v3()
    record["v3_blacklist_verdict"] = v3["verdict"]
    if v3["verdict"] != VERDICT_BL3_READY:
        record["verdict"] = VERDICT_C9P_BLOCKED
        record["blockers"].append("v3_blacklist_not_certifying")
        return record
    v2 = build_overnight_research_autopilot_v2_contract()
    record["v2_verdict"] = v2["verdict"]
    if v2["verdict"] != VERDICT_OAP2_READY:
        record["verdict"] = VERDICT_C9P_BLOCKED
        record["blockers"].append(
            "overnight_research_autopilot_v2_not_certifying")
        return record
    recommendation = _rec.build_candidate_recommendation()
    record["recommendation_verdict"] = recommendation["verdict"]
    if recommendation["verdict"] != _rec.VERDICT_CR_READY:
        record["verdict"] = VERDICT_C9P_BLOCKED
        record["blockers"].append("recommendation_not_certifying")
        return record
    loop_contract = _loop.build_autopilot_loop_contract()
    record["autopilot_loop_verdict"] = loop_contract["verdict"]
    if loop_contract["verdict"] != _loop.VERDICT_AP_READY:
        record["verdict"] = VERDICT_C9P_BLOCKED
        record["blockers"].append("autopilot_loop_not_certifying")
        return record
    # the family must NOT be in any of the rejection-family tuples
    if CANDIDATE_FAMILY in _loop.REJECTED_FAMILIES \
            or CANDIDATE_FAMILY in _rec.ALL_REJECTED_FAMILIES \
            or CANDIDATE_FAMILY in V2_BLACKLIST \
            or CANDIDATE_FAMILY in V3_BLACKLIST \
            or CANDIDATE_FAMILY in V4_BLACKLIST:
        record["verdict"] = VERDICT_C9P_BLOCKED
        record["blockers"].append("family_is_a_rejected_family")
        record["v4_blacklist_clearance"] = False
        return record
    record["v4_blacklist_clearance"] = True
    proposal_check = _loop.validate_candidate_family_proposal(
        dict(LOOP_PROPOSAL))
    record["loop_proposal_check"] = proposal_check
    language_check = _loop.screen_output_language(CLEAN_HYPOTHESIS)
    record["hypothesis_language_check"] = language_check
    hard_check = _rec.apply_hard_rejection_rules({
        "family": CANDIDATE_FAMILY,
        "hypothesis": CLEAN_HYPOTHESIS,
        "materially_different_because":
            DIFFERENCE_FROM_REJECTED_FAMILIES,
        "why_not_rescue":
            ("a joint price-and-volume single-bar microstructure "
             "trigger has not been tested in c1-c8; the staged "
             "btcusd 15m volume column is consumed structurally "
             "for the first time in this lane; no c1-c8 setup_ids, "
             "labels, or rejected geometry are reused; the c6 anti-"
             "cluster lesson, c7 sample-size adequacy lesson, and "
             "c8 explicit-edge-argument lesson are all built into "
             "the proposal as pre-committed policies, not future "
             "edits"),
        "required_spec_gates": ("81_bps_floor_at_label_time",
                                "27_bps_fee_model", "wider_stop_rule",
                                "same_symbol_non_overlap",
                                "completed_bars_only_no_lookahead"),
        "direction": DIRECTION,
    })
    record["recommendation_hard_rules_check"] = hard_check
    if not proposal_check["acceptable"]:
        record["verdict"] = VERDICT_C9P_BLOCKED
        record["blockers"].append("loop_proposal_gate_rejected")
        record["blockers"].extend(proposal_check["errors"])
        return record
    if not language_check["acceptable"]:
        record["verdict"] = VERDICT_C9P_BLOCKED
        record["blockers"].append("forbidden_language_in_hypothesis")
        return record
    if not hard_check["acceptable"]:
        record["verdict"] = VERDICT_C9P_BLOCKED
        record["blockers"].append(
            "recommendation_hard_rules_rejected")
        record["blockers"].extend(hard_check["rejections"])
        return record
    record["verdict"] = VERDICT_C9P_READY
    return record


def validate_candidate_9_family_proposal(record: Any
                                         ) -> dict[str, Any]:
    """Validate shape and safety invariants. Never raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_C9P_READY,
                                VERDICT_C9P_BLOCKED):
        errors.append("bad_verdict")
    if r.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if r.get("selected_candidate_id") != CANDIDATE_ID:
        errors.append("selected_candidate_id_tampered")
    if r.get("candidate_family") != CANDIDATE_FAMILY:
        errors.append("candidate_family_tampered")
    if r.get("candidate_family") in _loop.REJECTED_FAMILIES \
            or r.get("candidate_family") in _rec.ALL_REJECTED_FAMILIES \
            or r.get("candidate_family") in V2_BLACKLIST \
            or r.get("candidate_family") in V3_BLACKLIST \
            or r.get("candidate_family") in V4_BLACKLIST:
        errors.append("candidate_family_is_a_rejected_family")
    if r.get("clean_hypothesis") != CLEAN_HYPOTHESIS:
        errors.append("hypothesis_tampered")
    if r.get("edge_source_hypothesis") != EDGE_SOURCE_HYPOTHESIS:
        errors.append("edge_source_hypothesis_tampered")
    if r.get(
            "explicit_edge_argument_beyond_pattern_geometry"
    ) != EXPLICIT_EDGE_ARGUMENT_BEYOND_PATTERN_GEOMETRY:
        errors.append(
            "explicit_edge_argument_beyond_pattern_geometry_tampered")
    if tuple(r.get(
            "explicit_non_reuse_of_rejected_family_logic") or ()) != (
            EXPLICIT_NON_REUSE_OF_REJECTED_FAMILY_LOGIC):
        errors.append("explicit_non_reuse_tampered")
    if r.get("rationale_paragraph") != RATIONALE_PARAGRAPH:
        errors.append("rationale_paragraph_tampered")
    if r.get("difference_from_rejected_families") != (
            DIFFERENCE_FROM_REJECTED_FAMILIES):
        errors.append("difference_tampered")
    if r.get("loop_proposal") != LOOP_PROPOSAL:
        errors.append("loop_proposal_tampered")
    if r.get("symbols") != list(SYMBOLS) or r.get("timeframe") != (
            TIMEFRAME) or r.get("direction") != DIRECTION:
        errors.append("universe_timeframe_or_direction_tampered")
    if r.get("sample_window_proposal") != SAMPLE_WINDOW_PROPOSAL:
        errors.append("sample_window_proposal_tampered")
    if r.get("trigger_family") != TRIGGER_FAMILY:
        errors.append("trigger_family_tampered")
    if r.get("stop_family") != STOP_FAMILY:
        errors.append("stop_family_tampered")
    target = r.get("target_policy") or {}
    if target.get("variants") != list(TARGET_VARIANTS):
        errors.append("target_variants_tampered")
    if target.get("target_price_formula") != (
            TARGET_POLICY["target_price_formula"]):
        errors.append("target_price_formula_tampered")
    fee = r.get("fee_aware_geometry_policy") or {}
    if fee != FEE_AWARE_GEOMETRY_POLICY:
        errors.append("fee_aware_geometry_policy_tampered")
    if fee.get("fee_model_round_trip_bps") != 27:
        errors.append("fee_27bps_changed")
    if fee.get("minimum_gross_target_distance_floor_bps") != 81:
        errors.append("floor_81bps_changed")
    if fee.get("no_maker_rebate_assumption") is not True \
            or fee.get("no_zero_fee_assumption") is not True:
        errors.append("fee_assumption_weakened")
    if r.get("anti_cluster_policy") != ANTI_CLUSTER_POLICY:
        errors.append("anti_cluster_policy_tampered")
    if r.get("sample_size_adequacy_policy") != (
            SAMPLE_SIZE_ADEQUACY_POLICY):
        errors.append("sample_size_adequacy_policy_tampered")
    if r.get("explicit_edge_argument_policy") != (
            EXPLICIT_EDGE_ARGUMENT_POLICY):
        errors.append("explicit_edge_argument_policy_tampered")
    if r.get("non_overlap_policy") != NON_OVERLAP_POLICY:
        errors.append("non_overlap_policy_tampered")
    if r.get("edit_allowance_policy") != EDIT_ALLOWANCE_POLICY:
        errors.append("edit_allowance_policy_tampered")
    if tuple(r.get("expected_failure_modes") or ()) != (
            EXPECTED_FAILURE_MODES):
        errors.append("expected_failure_modes_tampered")
    if tuple(r.get("seed_usage") or ()) != SEED_USAGE:
        errors.append("seed_usage_tampered")
    if r.get("seeds_are_never_rescue_paths") is not True:
        errors.append("seeds_must_never_be_rescue_paths")
    if tuple(r.get("required_evidence_stages") or ()) != (
            _loop.LOOP_STAGES):
        errors.append("required_evidence_stages_tampered")
    if tuple(r.get("rejection_conditions") or ()) != (
            _loop.AUTO_REJECTION_RULES):
        errors.append("rejection_conditions_tampered")
    if tuple(r.get("safety_and_no_claim") or ()) != SAFETY_AND_NO_CLAIM:
        errors.append("safety_and_no_claim_tampered")
    if r.get("next_loop_stage") != NEXT_LOOP_STAGE:
        errors.append("next_loop_stage_tampered")
    if r.get("next_required_action") != NEXT_REQUIRED_ACTION:
        errors.append("next_required_action_tampered")
    for key, want in (("human_review_required", True),
                      ("human_review_required_at_every_gate", True),
                      ("paper_trading_gate_locked", True),
                      ("micro_live_gate_locked", True),
                      ("live_gate_locked", True),
                      ("is_a_rescue_attempt", False),
                      ("is_proposal_only", True),
                      ("plan_is_not_a_promotion", True)):
        if r.get(key) is not want:
            errors.append("constitution_flag_wrong:" + key)
    for key in ("executes", "writes_files", "labels_now",
                "runs_spec_review_now", "runs_detector",
                "runs_real_candle_detection", "runs_relabel",
                "runs_replay",
                "runs_real_detection_now", "runs_replay_now",
                "scores_now", "stages_data_now", "fetches_data",
                "calls_api", "uses_network", "uses_credentials",
                "uses_wallet", "uses_account", "connects_broker",
                "connects_exchange", "uses_real_money",
                "contains_order_logic",
                "contains_portfolio_allocation_logic",
                "starts_scheduler", "sends_notifications",
                "auto_commits", "auto_pushes", "creates_runners_now",
                "creates_data_artifacts_now",
                "creates_detector_label_replay_files_now",
                "creates_detector_implementation_now",
                "computes_pnl_now",
                "modifies_staged_market_data",
                "authorizes_paper_execution", "authorizes_micro_live",
                "authorizes_live_trading", "promotes_gate",
                "unlocks_downstream_gate", "claims_profitability"):
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)
    if r.get("verdict") == VERDICT_C9P_READY and r.get("blockers"):
        errors.append("ready_with_blockers")
    return {"valid": not errors, "errors": errors}
