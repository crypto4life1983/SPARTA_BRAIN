"""SPARTA CANDIDATE #10 FAMILY PROPOSAL (READ-ONLY, RESEARCH ONLY,
PROPOSAL GATE ONLY): INTRAWEEK_CALENDAR_SEASONALITY_DRIFT_V1.

Drafted via the pushed Rejected Family Blacklist V5 schema (which
extended V4 with the C9 entry
`low_volume_downside_capitulation_mean_reversion`) and the pushed
Overnight Autopilot Next-Candidate Proposal Drafter, then validated
through every pushed gate layer: Autopilot Loop V1's
validate_candidate_family_proposal / screen_output_language, the
Recommendation V1 hard rejection rules, AND the drafter's pure
validate_c10_proposal_draft static validator. BLOCKED if the NINE-
record ledger (C1-C9), V5, V4, V3, V2, Recommendation V1, the
Autopilot Loop V1, or the drafter stops certifying, or if the family
equals any rejected-family name from any pushed rejection-family
tuple.

CLEAN HYPOTHESIS (evidence language only): candidate #10 tests
whether a SINGLE deterministic CALENDAR trigger on BTCUSD daily (1d)
bars -- a completed daily bar whose ISO weekday index equals a pre-
specified favorable weekday bucket -- followed by a long entry on
that bar's CLOSE (no intrabar entry) and a fixed-horizon exit a
frozen number of completed daily bars later, captures a recurring
intra-week seasonality risk premium. There is NO price-pattern
condition, NO volume condition, and NO statistical-excursion
condition: the trigger is the clock alone. The EDGE HYPOTHESIS is a
calendar risk premium driven by recurring weekly liquidity and flow
cycles -- exogenous-time conditioning, NOT a chart shape.

SINGLE-TRIGGER DESIGN ANSWERS THE C9 LESSON AT PROPOSAL TIME: C9
failed because a JOINT price-AND-volume intersection was structurally
too sparse to reach an adequate accepted-setup count. C10 is
deliberately a SINGLE deterministic calendar condition, so there is
no intersection of trigger conditions to thin out the sample; a
weekday bucket recurs every calendar week, which makes the sample
abundant by construction over any multi-year window. The joint/
intersection-trigger sample-size pre-justification field explicitly
records that this design uses no intersecting conditions and that any
future addition of a second intersecting condition would require
separate pre-justification before it could be adopted.

C8 LESSON ANSWERED AT PROPOSAL TIME (V5-required field): an
explicit_edge_argument_beyond_pattern_geometry field is built in. The
argument is an exogenous calendar risk premium, not a candle shape:
the entry fires on the clock regardless of the price configuration at
the trigger bar.

MATERIAL DIFFERENCES from C1-C9 (each listed explicitly):
  - NOT C1 (ny_session_fvg_choch_v3): no session window used as a
    structure-hunting window, no fair-value gap, no change-of-
    character; the clock is the WHOLE signal, not a window in which
    to find price geometry;
  - NOT C2 (crypto_intraday_breakout_pullback_structure_v2): no
    breakout, no range, no pullback retest;
  - NOT C3 (btc_sol_long_trend_continuation_v1): no trend filter, no
    moving-average condition, no cross-symbol coupling;
  - NOT C4 (sol_btc_long_1h_swing_structure): no swing-pivot trigger,
    no pair coupling, daily not 1h;
  - NOT C5 (eth_sol_relative_strength_pullback_continuation_v1): no
    pairwise relative-strength comparison, no pullback-after-rs-lead
    structure;
  - NOT C6 (multi_symbol_relative_strength_rotation_filter): single-
    symbol BTCUSD only, no cross-sectional rank, no rotation filter;
  - NOT C7 (volatility_compression_expansion): no ATR contraction, no
    ATR-rolling-average comparison, no expansion multiplier;
  - NOT C8 (liquidity_sweep_mean_reversion): no sweep-below-prior-low
    geometry, no reclaim-window confirmation;
  - NOT C9 (low_volume_downside_capitulation_mean_reversion): no
    volume condition, no downside z-score, no mean-reversion-after-
    excursion; the trigger is a SINGLE deterministic calendar bucket
    and the trade is a directional calendar-drift long, not a
    counter-excursion reversion.

C6 ANTI-CLUSTER LESSON BAKED IN AT PROPOSAL TIME: a weekday bucket
fires at most once per ISO week by construction, and a per-symbol
minimum-bar-gap of one week is committed at proposal time. The
calendar itself is the primary anti-cluster constraint.

C7 SAMPLE-SIZE ADEQUACY LESSON BAKED IN AT PROPOSAL TIME: a built-in
minimum-occurrence-count threshold per weekday bucket is checked at
the labels-review gate; a multi-year daily window yields on the order
of hundreds of occurrences per weekday, the opposite of the C7/C9
sparsity failure.

This is a PROPOSAL. It runs no detector, fetches nothing, builds no
labels, replays nothing, creates no artifacts/runners/schedulers/
data/PnL, and the next stage is candidate_spec review by the human --
not detector execution. Seeds are inspiration and risk-control
lessons only, never rescue paths; no C1-C9 setup_ids, replay rows,
labels, edited labels, or rejected geometry may be reused as
candidate #10 evidence.
"""

from __future__ import annotations

from typing import Any

import sparta_commander.strategy_factory_autopilot_research_loop_v1_contract as _loop
import sparta_commander.strategy_factory_candidate_recommendation_v1_contract as _rec
import sparta_commander.strategy_factory_overnight_autopilot_next_candidate_proposal_drafter_contract as _drafter
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
from sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_rejection_record import (
    REJECTION_STATUS as C9_STATUS,
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
from sparta_commander.strategy_factory_rejected_family_blacklist_v5_contract import (
    LEDGER_FAMILY_LABELS as V5_LEDGER_FAMILY_LABELS,
    REJECTED_FAMILY_LOGIC_BLACKLIST_V5 as V5_BLACKLIST,
    VERDICT_BL5_READY,
    build_rejected_family_blacklist_v5,
)
from sparta_commander.volatility_compression_expansion_v1_rejection_record import (
    REJECTION_STATUS as C7_STATUS,
)

C10P_SCHEMA_VERSION = (
    "intraweek_calendar_seasonality_drift_v1_family_proposal.v1")
C10P_LABEL = ("SPARTA Candidate #10 Family Proposal "
              "(READ-ONLY, RESEARCH ONLY, PROPOSAL GATE ONLY, "
              "VALIDATED BY AUTOPILOT LOOP V1, RECOMMENDATION V1, AND "
              "THE V5 NEXT-CANDIDATE PROPOSAL DRAFTER, DRAFTED VIA "
              "REJECTED FAMILY BLACKLIST V5 SCHEMA, EXPLICIT EDGE "
              "ARGUMENT BEYOND PATTERN GEOMETRY REQUIRED, SINGLE-"
              "TRIGGER DESIGN, NOT A RESCUE, NOT A CLAIM)")
C10P_MODE = "RESEARCH_ONLY"
VERDICT_C10P_READY = "CANDIDATE_10_FAMILY_PROPOSAL_READY"
VERDICT_C10P_BLOCKED = "CANDIDATE_10_FAMILY_PROPOSAL_BLOCKED"
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_CANDIDATE_10_SPEC_REVIEW"
NEXT_LOOP_STAGE = "candidate_spec"

CANDIDATE_ID = "INTRAWEEK_CALENDAR_SEASONALITY_DRIFT_V1"
CANDIDATE_FAMILY = "intraweek_calendar_seasonality_drift"

# locked numerics (inherited from the pushed chain; never weakened) --------
LOCKED_FEE_ROUND_TRIP_BPS = 27
LOCKED_GROSS_TARGET_DISTANCE_FLOOR_BPS = 81

CLEAN_HYPOTHESIS = (
    "candidate #10 tests whether a SINGLE deterministic calendar "
    "trigger on btcusd daily (1d) bars -- a completed daily bar whose "
    "iso weekday index equals a pre-specified favorable weekday "
    "bucket -- followed by a long entry on that bar's close (no "
    "intrabar entry) and a fixed-horizon exit a frozen number of "
    "completed daily bars later, captures a recurring intra-week "
    "seasonality risk premium at 27 bps round-trip with the 81 bps "
    "gross target-distance floor; single-symbol, daily, long-only, "
    "labels-only research; there is no price-pattern condition, no "
    "volume condition, and no statistical-excursion condition -- the "
    "trigger is the clock alone; the edge hypothesis is an exogenous "
    "calendar risk premium driven by recurring weekly liquidity and "
    "flow cycles, NOT a chart pattern, NOT a cross-symbol filter, NOT "
    "a trend continuation, NOT a volatility-regime trigger, NOT a "
    "sweep-reclaim event, and NOT a volume-conditioned excursion")

EDGE_SOURCE_HYPOTHESIS = (
    "the structural source of the proposed edge is a recurring "
    "weekly flow cycle that is anchored to the calendar rather than "
    "to price: crypto liquidity thins across the weekend (fewer "
    "institutional desks, lower depth) and re-thickens as the global "
    "trading week resumes, and recurring weekly inflow patterns "
    "(scheduled allocations, payroll-cycle retail inflows, weekly "
    "options and futures roll timing) bias realized drift toward "
    "particular weekday buckets; because the conditioning variable is "
    "exogenous time and not any function of the price series, the "
    "signal is orthogonal to every price-geometry and volume "
    "condition tried in c1-c9; the 27 bps fee plus the 81 bps gross "
    "target-distance floor naturally screen out weekday buckets whose "
    "expected drift is too small to clear costs, so only buckets with "
    "a structurally large enough expected move survive label-time "
    "eligibility")

EXPLICIT_EDGE_ARGUMENT_BEYOND_PATTERN_GEOMETRY = (
    "1) THE CLAIM IS A CALENDAR RISK PREMIUM, NOT A VISUAL PATTERN: "
    "the trigger is the weekday index of a completed daily bar. No "
    "candlestick shape, no support/resistance level, no breakout, no "
    "excursion, and no volume figure participates in the entry "
    "decision. The price configuration at the trigger bar is "
    "irrelevant by construction.\n"
    "2) WHY A WEEKLY CALENDAR DRIFT CAN EXIST: market liquidity and "
    "flow are not uniform across the week. Weekend depth is "
    "structurally thinner; the resumption of the global trading week "
    "reintroduces institutional depth and recurring scheduled "
    "inflows. Those flows are anchored to the clock, not to the "
    "chart, and a recurring flow imbalance is a candidate source of a "
    "small directional drift on specific weekdays.\n"
    "3) WHY THIS IS ORTHOGONAL TO C1-C9: every prior family "
    "conditioned on a function of the price (and, for c9, volume) "
    "series -- session structure, breakout geometry, trend filters, "
    "swing pivots, relative strength, cross-sectional rank, "
    "volatility regime, sweep/reclaim geometry, or a volume-and-z-"
    "score excursion. The calendar weekday index shares no input with "
    "any of them; it can be present when all nine prior triggers are "
    "absent and vice versa.\n"
    "4) WHY 27 BPS + 81 BPS NATURALLY SCREENS: the expected per-"
    "bucket drift over the chosen holding horizon must exceed the 81 "
    "bps gross target-distance floor for the bucket to be label-"
    "eligible; weekday buckets whose expected drift is below the "
    "floor are correctly filtered out, leaving only buckets with a "
    "large enough recurring move to be evaluable under fee-honest "
    "geometry.\n"
    "5) WHY THIS IS A SINGLE-TRIGGER DESIGN (THE C9 LESSON): c9 "
    "failed because a joint price-AND-volume intersection was too "
    "sparse to reach an adequate accepted-setup count. c10 uses ONE "
    "deterministic calendar condition with no intersection, so the "
    "sample cannot be thinned by an intersection of conditions; a "
    "weekday bucket recurs every calendar week, giving hundreds of "
    "occurrences over a multi-year window. The single-trigger choice "
    "is the direct structural answer to the c9 sparsity failure.\n"
    "6) FALSIFIABILITY: the calendar-risk-premium claim is "
    "falsifiable by the per-bucket per-horizon fee-honest replay net "
    "r sums at the replay gate; if every weekday bucket comes out "
    "structurally net-negative in-sample under the 27 bps + 81 bps "
    "geometry, candidate #10 is rejected for the same evidence reason "
    "its predecessors were -- the proposed edge did not survive the "
    "cost geometry. Spending the one allowed structural edit on a "
    "different weekday bucket, a different holding horizon, or a "
    "different favorable-bucket selection window is the only "
    "permitted contingency.")

JOINT_OR_INTERSECTION_TRIGGER_SAMPLE_SIZE_PRE_JUSTIFICATION = (
    "NOT APPLICABLE BY DESIGN: candidate #10 uses a SINGLE "
    "deterministic calendar trigger (the completed daily bar's iso "
    "weekday index equals a pre-specified bucket). There is no "
    "intersection of trigger conditions, so the c9 intersection-"
    "sparsity failure mode cannot occur. Pre-justification of sample "
    "size is therefore structural and abundant: a weekday bucket "
    "recurs once per iso week, so over the proposed multi-year daily "
    "window each bucket accrues on the order of hundreds of "
    "independent occurrences, far above the proposal-committed "
    "minimum-occurrence threshold. If a future spec edit were to "
    "introduce a SECOND intersecting condition (for example a "
    "volatility-regime gate on top of the weekday bucket), that "
    "addition would itself require an explicit joint-trigger sample-"
    "size pre-justification before it could be adopted, and it would "
    "consume the single allowed structural edit token; it is not "
    "part of this proposal.")

EXPLICIT_NON_REUSE_OF_REJECTED_FAMILY_LOGIC = (
    "no C1-C9 setup_ids may be referenced as evidence; "
    "no C1-C9 replay rows, labels, or relabel artifacts may be "
    "reused; "
    "no C1-C9 rejected geometry may be reused unchanged; "
    "no C1 ny-session window, fair-value-gap, or change-of-character "
    "structure; "
    "no C2 range-breakout or pullback-retest structure; "
    "no C3 trend-continuation filter or cross-symbol coupling; "
    "no C4 swing-pivot trigger or sol/btc pair coupling; "
    "no C5 pairwise relative-strength comparison; "
    "no C6 multi-symbol rank or rotation filter; "
    "no C7 atr contraction, atr-rolling-average comparison, or "
    "expansion multiplier; "
    "no C8 sweep-below-prior-low geometry or reclaim-window "
    "confirmation; "
    "no C9 volume condition, downside z-score, or mean-reversion-"
    "after-excursion logic")

RATIONALE_PARAGRAPH = (
    "A purely calendar-conditioned directional drift has not been "
    "tested in c1-c9. c1-c5 and c8 used price-pattern geometry; c6 "
    "used cross-sectional relative-strength rank; c7 used a "
    "volatility regime; c9 used a joint price-and-volume excursion. "
    "c10 introduces the calendar weekday index as a first-class and "
    "exogenous trigger that shares no input with any prior family. "
    "The structural argument is a recurring weekly flow imbalance "
    "anchored to the clock; the empirical test is the per-bucket per-"
    "horizon fee-honest replay against a multi-year staged btcusd "
    "daily window. The single-trigger design is the deliberate "
    "structural answer to the c9 intersection-sparsity failure; anti-"
    "cluster protection is intrinsic because a weekday bucket fires "
    "at most once per iso week, and sample-size adequacy is intrinsic "
    "because each bucket recurs every week. The explicit edge "
    "argument satisfies the v5 requirement introduced by the c8 "
    "rejection, and the joint-trigger pre-justification field records "
    "that no intersecting conditions are used.")

# differentiation keyed by the EXACT V5 blacklist labels so the
# drafter's validate_c10_proposal_draft can confirm all nine are
# addressed by name ---------------------------------------------------------
DIFFERENTIATION_FROM_EACH_REJECTED_FAMILY = {
    "ny_session_fvg_choch_v3": (
        "no session window used to hunt price structure, no fair-"
        "value gap, no change-of-character; the weekday index is the "
        "entire signal, not a window for geometry"),
    "crypto_intraday_breakout_pullback_structure_v2": (
        "no breakout, no range, no pullback retest; entry is "
        "calendar-timed, not structure-timed"),
    "btc_sol_long_trend_continuation_v1": (
        "no trend filter, no moving-average condition, no cross-"
        "symbol coupling; single-symbol btcusd"),
    "sol_btc_long_1h_swing_structure": (
        "no swing-pivot trigger, no pair coupling; daily not 1h; "
        "trigger is the clock, not a pivot"),
    "eth_sol_relative_strength_pullback_continuation_v1": (
        "no pairwise relative-strength comparison, no pullback-after-"
        "rs-lead structure"),
    "multi_symbol_relative_strength_rotation_filter": (
        "single-symbol btcusd only, no cross-sectional rank, no "
        "rotation filter"),
    "volatility_compression_expansion": (
        "no atr contraction, no atr-rolling-average comparison, no "
        "expansion multiplier; trigger is exogenous time"),
    "liquidity_sweep_mean_reversion": (
        "no sweep-below-prior-low geometry, no reclaim-window "
        "confirmation, no reference-low lookback"),
    "low_volume_downside_capitulation_mean_reversion": (
        "no volume condition, no downside z-score, no mean-reversion-"
        "after-excursion; a single deterministic calendar trigger "
        "and a directional calendar drift, not a counter-excursion "
        "reversion"),
}

# a flat string form of the differentiation for the loop / recommendation
# gates (which expect non-empty text) --------------------------------------
DIFFERENCE_FROM_REJECTED_FAMILIES = (
    "1) not ny_session_fvg_choch_v3 (no session structure-window, no "
    "fvg, no choch); "
    "2) not crypto_intraday_breakout_pullback_structure_v2 (no "
    "breakout, no pullback retest); "
    "3) not btc_sol_long_trend_continuation_v1 (single-symbol, no "
    "trend filter, no cross-symbol coupling); "
    "4) not sol_btc_long_1h_swing_structure (no swing pivot, no pair "
    "coupling, daily not 1h); "
    "5) not eth_sol_relative_strength_pullback_continuation_v1 (no "
    "pairwise relative strength); "
    "6) not multi_symbol_relative_strength_rotation_filter (no rank, "
    "no rotation, no cross-sectional filter); "
    "7) not volatility_compression_expansion (no atr contraction, no "
    "atr-rolling-average comparison, no expansion multiplier); "
    "8) not liquidity_sweep_mean_reversion (no sweep geometry, no "
    "reclaim confirmation); "
    "9) not low_volume_downside_capitulation_mean_reversion (no "
    "volume condition, no downside z-score, no excursion reversion); "
    "10) the trigger is a single deterministic calendar weekday "
    "bucket on a completed daily bar; "
    "11) the edge hypothesis is an exogenous calendar risk premium, "
    "not a chart pattern; "
    "12) anti-cluster protection is intrinsic (one fire per iso "
    "week) and committed at proposal time, not a future edit; "
    "13) sample-size adequacy is intrinsic (a bucket recurs every "
    "week) and the minimum-occurrence threshold is committed at "
    "proposal time, not a future edit; "
    "14) the explicit edge argument and the joint-trigger pre-"
    "justification fields are built into the proposal per the c8 and "
    "c9 lessons")

LOOP_PROPOSAL = {
    "family": CANDIDATE_FAMILY,
    "hypothesis": CLEAN_HYPOTHESIS,
    "difference_from_rejected_families":
        DIFFERENCE_FROM_REJECTED_FAMILIES,
    "uses_seeds_as_rescue": False,
}

# universe, timeframe, direction -------------------------------------------
SYMBOLS = ("BTCUSD",)
TIMEFRAME = "1d"
DIRECTION = "long_only"
DIRECTION_NOTE = "long-only research labels; never trading capability"
SAMPLE_WINDOW_PROPOSAL = "2019-01-01_2025-12-31"

# single deterministic calendar trigger (declarative; exact numerics
# frozen at spec review) ---------------------------------------------------
TRIGGER_FAMILY = {
    "name": "intraweek_calendar_weekday_bucket_event",
    "definition": (
        "1) favorable-bucket selection: a pre-specified iso weekday "
        "bucket (e.g. a single weekday or a contiguous pair of "
        "weekdays) chosen on an in-sample selection window that is "
        "frozen at spec review; "
        "2) trigger: the completed daily bar's iso weekday index "
        "equals the pre-specified bucket; "
        "3) NO price-pattern, volume, excursion, or statistical "
        "condition participates in the trigger; "
        "4) entry: a long entry on the CLOSE of the triggering "
        "completed daily bar (no intrabar entry); "
        "5) exit: a fixed-horizon exit a frozen number of completed "
        "daily bars after entry, set at spec review"),
    "uses_completed_daily_bars_only": True,
    "no_future_bars": True,
    "no_same_bar_lookahead": True,
    "no_intrabar_entry": True,
    "is_a_single_deterministic_calendar_trigger": True,
    "uses_no_price_pattern_condition": True,
    "uses_no_volume_condition": True,
    "uses_no_statistical_excursion_condition": True,
    "exact_numeric_form_frozen_at_spec_review": True,
    "is_not_a_cross_symbol_rs_filter": True,
    "is_not_a_session_anchored_structure_trigger": True,
    "is_not_a_breakout_pullback_trigger": True,
    "is_not_a_trend_ma_filter": True,
    "is_not_a_swing_pivot_trigger": True,
    "is_not_an_atr_contraction_expansion_trigger": True,
    "is_not_a_relative_strength_rotation_trigger": True,
    "is_not_a_sweep_reclaim_trigger": True,
    "is_not_a_volume_conditioned_excursion_trigger": True,
}

# fixed-horizon exit / structure stop --------------------------------------
EXIT_FAMILY = {
    "rule": ("fixed-horizon exit: close the long at the close of the "
             "daily bar a frozen number of completed daily bars after "
             "entry; a structural protective stop a frozen distance "
             "below entry invalidates the setup if hit first"),
    "exact_horizon_frozen_at_spec_review": True,
    "structural_stop_distance_frozen_at_spec_review": True,
    "stop_must_be_below_entry": True,
    "never_tightened_after_entry": True,
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

# C6 lesson: anti-cluster intrinsic to the calendar -----------------------
ANTI_CLUSTER_POLICY = {
    "built_in_at_label_emission_time": True,
    "scope": "per_symbol_one_fire_per_iso_week_plus_minimum_bar_gap",
    "calendar_is_the_primary_anti_cluster_constraint": True,
    "minimum_bar_gap_frozen_at_spec_review": True,
    "applies_before_replay_time_non_overlap": True,
    "replay_time_non_overlap_unchanged": True,
    "is_not_the_single_allowed_c10_edit": True,
    "reason_for_built_in":
        "c6_clustering_filter_edit_proved_density_must_be_controlled"
        "_at_proposal_time",
}

# C7 lesson: sample-size adequacy intrinsic to a weekly recurrence --------
SAMPLE_SIZE_ADEQUACY_POLICY = {
    "built_in_at_proposal_time": True,
    "minimum_occurrence_count_per_bucket_threshold_frozen_at_spec"
    "_review": True,
    "applies_at_labels_review_gate": True,
    "below_threshold_triggers_structural_rejection_without_edit"
    "_token": True,
    "sample_is_abundant_by_construction_a_bucket_recurs_every_iso"
    "_week": True,
    "reason_for_built_in":
        "c7_zero_accepted_setups_and_c9_intersection_sparsity_proved"
        "_the_proposal_must_commit_a_minimum_evaluable_count_and"
        "_avoid_an_overly_narrow_intersection_of_triggers",
    "is_not_the_single_allowed_c10_edit": True,
}

# C8 lesson: explicit edge argument required at proposal time -------------
EXPLICIT_EDGE_ARGUMENT_POLICY = {
    "built_in_at_proposal_time": True,
    "v5_required_field": True,
    "argument_is_a_calendar_risk_premium_not_visual": True,
    "argument_is_orthogonal_to_all_price_and_volume_conditions": True,
    "argument_is_falsifiable_by_per_bucket_net_r_sums": True,
    "is_not_the_single_allowed_c10_edit": True,
    "reason_for_built_in":
        "c8_all_variants_net_negative_in_sample_proved_pattern"
        "_geometry_alone_is_not_an_edge_source_and_v5_requires_an"
        "_explicit_argument_at_proposal_time",
}

# C9 lesson: single-trigger design + joint-trigger pre-justification ------
JOINT_TRIGGER_PRE_JUSTIFICATION_POLICY = {
    "design_is_single_deterministic_trigger": True,
    "no_intersection_of_trigger_conditions": True,
    "intersection_sparsity_failure_cannot_occur": True,
    "future_second_intersecting_condition_requires_separate_pre"
    "_justification": True,
    "future_second_intersecting_condition_would_consume_the_single"
    "_edit_token": True,
    "is_not_the_single_allowed_c10_edit": True,
    "reason_for_built_in":
        "c9_joint_price_and_volume_intersection_was_too_sparse_to"
        "_reach_an_adequate_accepted_setup_count",
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
    "at most ONE pre-committed edit for candidate #10, only if "
    "evidence-supported, only via a separately human-approved "
    "contract; if spent and results remain net-negative or below the "
    "sample-size adequacy threshold, candidate #10 is REJECTED_KEPT"
    "_ON_RECORD; the anti-cluster policy, the sample-size adequacy "
    "policy, the explicit-edge-argument field, and the joint-trigger "
    "pre-justification field are NOT this edit token; the edit must "
    "target a different structural parameter (the favorable weekday "
    "bucket, the holding horizon, the favorable-bucket selection "
    "window, or the structural stop distance) if spent")

# expected failure modes (frozen, evidence-language only) ----------------
EXPECTED_FAILURE_MODES = (
    "cost_prohibitive_buckets_whose_expected_drift_fails_the_81_bps"
    "_floor_at_label_time",
    "weekday_seasonality_that_is_not_stable_out_of_sample_so_the_in"
    "_sample_favorable_bucket_does_not_persist",
    "holding_horizon_choice_that_either_dilutes_the_drift_or_adds"
    "_uncompensated_overnight_risk",
    "structural_calendar_drift_failing_empirically_in_the_staged"
    "_window_meaning_the_proposed_edge_did_not_survive_the_27_bps"
    "_plus_81_bps_geometry_which_would_be_a_clean_rejection_not_a"
    "_rescue_path",
    "any_post_edit_replay_remaining_net_negative_or_with_hit_rate"
    "_below_breakeven_at_any_variant",
    "regime_dependence_where_the_seasonality_only_appears_in_one"
    "_market_regime_and_reverses_in_another",
)

# seeds (inspiration only, never rescue paths) ---------------------------
SEED_USAGE = (
    "c6_clustering_lesson_is_inspiration_for_intrinsic_one_fire_per"
    "_week_anti_cluster_not_rescue",
    "c7_sample_size_adequacy_lesson_is_inspiration_for_a_minimum"
    "_occurrence_threshold_not_rescue",
    "c8_explicit_edge_argument_lesson_is_inspiration_for_the_calendar"
    "_risk_premium_argument_field_not_rescue",
    "c9_intersection_sparsity_lesson_is_inspiration_for_the_single"
    "_trigger_design_not_rescue",
    "single_symbol_btcusd_daily_calendar_weekday_trigger_is_a_clean"
    "_new_hypothesis_not_a_recombination_of_rejected_geometry",
    "the_calendar_weekday_index_is_a_new_exogenous_input_that_c1"
    "_through_c9_did_not_consume",
    "no_c1_c9_setup_ids_replay_rows_labels_edited_labels_or_replay"
    "_results_may_be_reused_as_candidate_10_evidence",
)
SEEDS_ARE_NEVER_RESCUE_PATHS = True

PROMOTION_TO_HUMAN_REVIEW_CONDITIONS = (
    "fee-honest replay net-positive on the overlap-adjusted "
    "independent sample with per-bucket occurrence counts at or above "
    "the proposal-committed minimum",
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

# the union of every pushed rejected-family tuple this family must clear
ALL_KNOWN_REJECTED_FAMILIES = tuple(sorted(set(
    list(_loop.REJECTED_FAMILIES) + list(_rec.ALL_REJECTED_FAMILIES)
    + list(V2_BLACKLIST) + list(V3_BLACKLIST) + list(V4_BLACKLIST)
    + list(V5_BLACKLIST))))

# the next-required human gate string (banned-token-free) -----------------
NEXT_HUMAN_GATE = NEXT_REQUIRED_ACTION

# the flat human-filled C10 draft that the pushed drafter's static
# validate_c10_proposal_draft must certify ---------------------------------
C10_DRAFT = {
    "proposed_family_label": CANDIDATE_FAMILY,
    "hypothesis_statement": CLEAN_HYPOTHESIS,
    "edge_source_hypothesis": EDGE_SOURCE_HYPOTHESIS,
    "explicit_edge_argument_beyond_pattern_geometry":
        EXPLICIT_EDGE_ARGUMENT_BEYOND_PATTERN_GEOMETRY,
    "joint_or_intersection_trigger_sample_size_pre_justification":
        JOINT_OR_INTERSECTION_TRIGGER_SAMPLE_SIZE_PRE_JUSTIFICATION,
    "universe_proposal": "BTCUSD",
    "timeframe_proposal": TIMEFRAME,
    "direction_proposal": DIRECTION,
    "fee_assumption_round_trip_bps": LOCKED_FEE_ROUND_TRIP_BPS,
    "minimum_gross_target_distance_floor_bps":
        LOCKED_GROSS_TARGET_DISTANCE_FLOOR_BPS,
    "sample_window_proposal": SAMPLE_WINDOW_PROPOSAL,
    "differentiation_from_each_rejected_family":
        dict(DIFFERENTIATION_FROM_EACH_REJECTED_FAMILY),
    "explicit_non_reuse_of_rejected_family_logic":
        EXPLICIT_NON_REUSE_OF_REJECTED_FAMILY_LOGIC,
    "anti_cluster_protection_at_proposal_time": (
        "intrinsic: a weekday bucket fires at most once per iso week "
        "by construction, plus a committed per-symbol minimum-bar-gap "
        "of one week; the calendar is the primary anti-cluster "
        "constraint (c6 lesson), built in at proposal time"),
    "sample_size_adequacy_assessment_at_proposal_time": (
        "intrinsic and abundant: a weekday bucket recurs once per iso "
        "week, so the proposed multi-year daily window yields on the "
        "order of hundreds of occurrences per bucket, far above the "
        "proposal-committed minimum-occurrence threshold; this "
        "directly answers the c7 and c9 sparsity failures"),
    "rationale_paragraph": RATIONALE_PARAGRAPH,
    "human_review_required_at_every_gate": True,
    "no_promotion_no_paper_no_live": True,
    "next_human_gate": NEXT_HUMAN_GATE,
}


def get_candidate_10_proposal_label() -> str:
    return C10P_LABEL


def get_c10_draft() -> dict[str, Any]:
    """Return a copy of the flat human-filled C10 draft."""
    draft = dict(C10_DRAFT)
    draft["differentiation_from_each_rejected_family"] = dict(
        DIFFERENTIATION_FROM_EACH_REJECTED_FAMILY)
    return draft


def build_candidate_10_family_proposal() -> dict[str, Any]:
    """Assemble the C10 proposal. Chain-gated on the NINE-record
    rejection ledger (C1-C9), the pushed V5 blacklist, V4, V3, V2,
    Recommendation V1, the Autopilot Loop V1, and the pushed Overnight
    Autopilot Next-Candidate Proposal Drafter. Validated by the loop's
    validate_candidate_family_proposal + screen_output_language gates,
    Recommendation V1's apply_hard_rejection_rules, AND the drafter's
    validate_c10_proposal_draft static validator."""
    record: dict[str, Any] = {
        "schema_version": C10P_SCHEMA_VERSION, "label": C10P_LABEL,
        "mode": C10P_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [],
        "candidate_id": CANDIDATE_ID,
        "candidate_family": CANDIDATE_FAMILY,
        "selected_candidate_id": CANDIDATE_ID,
        "clean_hypothesis": CLEAN_HYPOTHESIS,
        "edge_source_hypothesis": EDGE_SOURCE_HYPOTHESIS,
        "explicit_edge_argument_beyond_pattern_geometry":
            EXPLICIT_EDGE_ARGUMENT_BEYOND_PATTERN_GEOMETRY,
        "joint_or_intersection_trigger_sample_size_pre_justification":
            JOINT_OR_INTERSECTION_TRIGGER_SAMPLE_SIZE_PRE_JUSTIFICATION,
        "explicit_non_reuse_of_rejected_family_logic":
            EXPLICIT_NON_REUSE_OF_REJECTED_FAMILY_LOGIC,
        "rationale_paragraph": RATIONALE_PARAGRAPH,
        "difference_from_rejected_families":
            DIFFERENCE_FROM_REJECTED_FAMILIES,
        "differentiation_from_each_rejected_family":
            dict(DIFFERENTIATION_FROM_EACH_REJECTED_FAMILY),
        "loop_proposal": dict(LOOP_PROPOSAL),
        "loop_proposal_check": None,
        "hypothesis_language_check": None,
        "recommendation_hard_rules_check": None,
        "drafter_draft_validation": None,
        "symbols": list(SYMBOLS), "timeframe": TIMEFRAME,
        "direction": DIRECTION, "direction_note": DIRECTION_NOTE,
        "sample_window_proposal": SAMPLE_WINDOW_PROPOSAL,
        "trigger_family": dict(TRIGGER_FAMILY),
        "exit_family": dict(EXIT_FAMILY),
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
        "joint_trigger_pre_justification_policy":
            dict(JOINT_TRIGGER_PRE_JUSTIFICATION_POLICY),
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
        "ledger_status_nine_records": None,
        "ledger_all_rejected_kept_on_record": None,
        "v5_blacklist_verdict": None,
        "v5_blacklist_clearance": None,
        "v4_blacklist_verdict": None,
        "v3_blacklist_verdict": None,
        "v2_verdict": None,
        "recommendation_verdict": None,
        "autopilot_loop_verdict": None,
        "drafter_verdict": None,
        "c10_draft": None,
        "next_loop_stage": NEXT_LOOP_STAGE,
        "human_review_required": True,
        "human_review_required_at_every_gate": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True, "live_gate_locked": True,
        "is_a_rescue_attempt": False,
        "is_proposal_only": True,
        "plan_is_not_a_promotion": True,
        "no_promotion_no_paper_no_live": True,
        "executes": False, "writes_files": False, "labels_now": False,
        "runs_spec_review_now": False,
        "runs_detector": False, "runs_real_candle_detection": False,
        "runs_dry_run": False,
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
        "uses_external_data_source": False,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    statuses = (C1_STATUS, C2_STATUS, C3_STATUS, C4_STATUS, C5_STATUS,
                C6_STATUS, C7_STATUS, C8_STATUS, C9_STATUS)
    record["ledger_status_nine_records"] = list(statuses)
    record["ledger_all_rejected_kept_on_record"] = all(
        s == "REJECTED_KEPT_ON_RECORD" for s in statuses)
    if not record["ledger_all_rejected_kept_on_record"]:
        record["verdict"] = VERDICT_C10P_BLOCKED
        record["blockers"].append("nine_record_ledger_broken")
        return record
    v5 = build_rejected_family_blacklist_v5()
    record["v5_blacklist_verdict"] = v5["verdict"]
    if v5["verdict"] != VERDICT_BL5_READY:
        record["verdict"] = VERDICT_C10P_BLOCKED
        record["blockers"].append("v5_blacklist_not_certifying")
        return record
    v4 = build_rejected_family_blacklist_v4()
    record["v4_blacklist_verdict"] = v4["verdict"]
    if v4["verdict"] != VERDICT_BL4_READY:
        record["verdict"] = VERDICT_C10P_BLOCKED
        record["blockers"].append("v4_blacklist_not_certifying")
        return record
    v3 = build_rejected_family_blacklist_v3()
    record["v3_blacklist_verdict"] = v3["verdict"]
    if v3["verdict"] != VERDICT_BL3_READY:
        record["verdict"] = VERDICT_C10P_BLOCKED
        record["blockers"].append("v3_blacklist_not_certifying")
        return record
    v2 = build_overnight_research_autopilot_v2_contract()
    record["v2_verdict"] = v2["verdict"]
    if v2["verdict"] != VERDICT_OAP2_READY:
        record["verdict"] = VERDICT_C10P_BLOCKED
        record["blockers"].append(
            "overnight_research_autopilot_v2_not_certifying")
        return record
    recommendation = _rec.build_candidate_recommendation()
    record["recommendation_verdict"] = recommendation["verdict"]
    if recommendation["verdict"] != _rec.VERDICT_CR_READY:
        record["verdict"] = VERDICT_C10P_BLOCKED
        record["blockers"].append("recommendation_not_certifying")
        return record
    loop_contract = _loop.build_autopilot_loop_contract()
    record["autopilot_loop_verdict"] = loop_contract["verdict"]
    if loop_contract["verdict"] != _loop.VERDICT_AP_READY:
        record["verdict"] = VERDICT_C10P_BLOCKED
        record["blockers"].append("autopilot_loop_not_certifying")
        return record
    drafter = (
        _drafter
        .build_overnight_autopilot_next_candidate_proposal_drafter())
    record["drafter_verdict"] = drafter["verdict"]
    if drafter["verdict"] != _drafter.VERDICT_DRAFTER_READY:
        record["verdict"] = VERDICT_C10P_BLOCKED
        record["blockers"].append("drafter_not_certifying")
        return record
    # the family must NOT be in any of the rejection-family tuples
    if CANDIDATE_FAMILY in _loop.REJECTED_FAMILIES \
            or CANDIDATE_FAMILY in _rec.ALL_REJECTED_FAMILIES \
            or CANDIDATE_FAMILY in V2_BLACKLIST \
            or CANDIDATE_FAMILY in V3_BLACKLIST \
            or CANDIDATE_FAMILY in V4_BLACKLIST \
            or CANDIDATE_FAMILY in V5_BLACKLIST:
        record["verdict"] = VERDICT_C10P_BLOCKED
        record["blockers"].append("family_is_a_rejected_family")
        record["v5_blacklist_clearance"] = False
        return record
    record["v5_blacklist_clearance"] = True
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
            ("a single deterministic calendar weekday trigger has not "
             "been tested in c1-c9; the calendar weekday index is a "
             "new exogenous input consumed for the first time in this "
             "lane; no c1-c9 setup_ids, labels, or rejected geometry "
             "are reused; the c6 anti-cluster lesson, c7 sample-size "
             "adequacy lesson, c8 explicit-edge-argument lesson, and "
             "c9 single-trigger lesson are all built into the "
             "proposal as pre-committed policies, not future edits"),
        "required_spec_gates": ("81_bps_floor_at_label_time",
                                "27_bps_fee_model",
                                "structural_stop_rule",
                                "same_symbol_non_overlap",
                                "completed_bars_only_no_lookahead"),
        "direction": DIRECTION,
    })
    record["recommendation_hard_rules_check"] = hard_check
    draft = get_c10_draft()
    draft_validation = _drafter.validate_c10_proposal_draft(draft)
    record["drafter_draft_validation"] = draft_validation
    record["c10_draft"] = draft
    if not proposal_check["acceptable"]:
        record["verdict"] = VERDICT_C10P_BLOCKED
        record["blockers"].append("loop_proposal_gate_rejected")
        record["blockers"].extend(proposal_check["errors"])
        return record
    if not language_check["acceptable"]:
        record["verdict"] = VERDICT_C10P_BLOCKED
        record["blockers"].append("forbidden_language_in_hypothesis")
        return record
    if not hard_check["acceptable"]:
        record["verdict"] = VERDICT_C10P_BLOCKED
        record["blockers"].append(
            "recommendation_hard_rules_rejected")
        record["blockers"].extend(hard_check["rejections"])
        return record
    if not draft_validation["valid"]:
        record["verdict"] = VERDICT_C10P_BLOCKED
        record["blockers"].append("drafter_draft_validation_failed")
        record["blockers"].extend(draft_validation["errors"])
        return record
    record["verdict"] = VERDICT_C10P_READY
    return record


def validate_candidate_10_family_proposal(record: Any
                                          ) -> dict[str, Any]:
    """Validate shape and safety invariants. Never raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_C10P_READY,
                                VERDICT_C10P_BLOCKED):
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
            or r.get("candidate_family") in V4_BLACKLIST \
            or r.get("candidate_family") in V5_BLACKLIST:
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
    if r.get(
            "joint_or_intersection_trigger_sample_size_pre"
            "_justification"
    ) != JOINT_OR_INTERSECTION_TRIGGER_SAMPLE_SIZE_PRE_JUSTIFICATION:
        errors.append("joint_trigger_pre_justification_tampered")
    if r.get("explicit_non_reuse_of_rejected_family_logic") != (
            EXPLICIT_NON_REUSE_OF_REJECTED_FAMILY_LOGIC):
        errors.append("explicit_non_reuse_tampered")
    if r.get("rationale_paragraph") != RATIONALE_PARAGRAPH:
        errors.append("rationale_paragraph_tampered")
    if r.get("difference_from_rejected_families") != (
            DIFFERENCE_FROM_REJECTED_FAMILIES):
        errors.append("difference_tampered")
    if r.get("differentiation_from_each_rejected_family") != (
            DIFFERENTIATION_FROM_EACH_REJECTED_FAMILY):
        errors.append("differentiation_dict_tampered")
    if r.get("loop_proposal") != LOOP_PROPOSAL:
        errors.append("loop_proposal_tampered")
    if r.get("symbols") != list(SYMBOLS) or r.get("timeframe") != (
            TIMEFRAME) or r.get("direction") != DIRECTION:
        errors.append("universe_timeframe_or_direction_tampered")
    if r.get("sample_window_proposal") != SAMPLE_WINDOW_PROPOSAL:
        errors.append("sample_window_proposal_tampered")
    if r.get("trigger_family") != TRIGGER_FAMILY:
        errors.append("trigger_family_tampered")
    if r.get("exit_family") != EXIT_FAMILY:
        errors.append("exit_family_tampered")
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
    if r.get("joint_trigger_pre_justification_policy") != (
            JOINT_TRIGGER_PRE_JUSTIFICATION_POLICY):
        errors.append("joint_trigger_pre_justification_policy_tampered")
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
    # the embedded flat draft must still certify against the live drafter
    draft = r.get("c10_draft")
    if r.get("verdict") == VERDICT_C10P_READY:
        if not isinstance(draft, dict):
            errors.append("c10_draft_missing")
        else:
            dv = _drafter.validate_c10_proposal_draft(draft)
            if not dv["valid"]:
                errors.append("c10_draft_no_longer_valid")
    for key, want in (("human_review_required", True),
                      ("human_review_required_at_every_gate", True),
                      ("paper_trading_gate_locked", True),
                      ("micro_live_gate_locked", True),
                      ("live_gate_locked", True),
                      ("is_a_rescue_attempt", False),
                      ("is_proposal_only", True),
                      ("plan_is_not_a_promotion", True),
                      ("no_promotion_no_paper_no_live", True)):
        if r.get(key) is not want:
            errors.append("constitution_flag_wrong:" + key)
    for key in ("executes", "writes_files", "labels_now",
                "runs_spec_review_now", "runs_detector",
                "runs_real_candle_detection", "runs_dry_run",
                "runs_relabel", "runs_replay",
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
                "unlocks_downstream_gate", "claims_profitability",
                "uses_external_data_source"):
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)
    if r.get("verdict") == VERDICT_C10P_READY and r.get("blockers"):
        errors.append("ready_with_blockers")
    return {"valid": not errors, "errors": errors}
