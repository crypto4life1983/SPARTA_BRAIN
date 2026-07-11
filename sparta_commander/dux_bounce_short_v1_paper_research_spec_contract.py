"""Dux BOUNCE SHORT V1 -- PAPER RESEARCH SPECIFICATION (PURE, SPEC-ONLY, DATA- AND
EXECUTION-BLOCKED).

Human-approved build token: HUMAN_APPROVED_BUILD_DUX_BOUNCE_SHORT_V1_SPEC_ONLY.
Classification: SPEC_ONLY_DATA_AND_EXECUTION_BLOCKED.

This contract FREEZES the Bounce Short V1 research hypothesis + its data/execution contract
and COMPUTES NOTHING. It is not a candidate, opens no lane, and authorizes no data, event
study, replay, backtest, scanner, paper/live trade, broker connection, or locate purchase.

Bounce Short V1 ONLY -- deliberately NOT combined with gap-up short, first red day, options,
any crypto candidate, or any existing operational trading lane. The core hypothesis is an
UNPROVEN EXTERNAL (trader-reported) claim: a small-cap equity that revisits a mechanically
established historical high-volume resistance zone MAY subsequently underperform when
historical trapped supply materially exceeds current buying demand. Nothing here asserts this
is true; nothing here is computable today (SPARTA has no qualifying small-cap infrastructure).

Every operational capability is pinned False with a full scope_locks set; the validator
rejects any tamper that would enable a capability, mark trader claims proven/accepted, choose
a numeric value for an unresolved threshold, or promote to candidate/executable/data-fetching.
"""
from __future__ import annotations

from typing import Any

DBS_SCHEMA_VERSION = 1
DBS_MODE = "RESEARCH_ONLY"
DBS_LANE = "us_small_cap_short_research_spec_only"          # NOT an operational lane
DBS_CLASSIFICATION = "SPEC_ONLY_DATA_AND_EXECUTION_BLOCKED"

RECORD_ID = "DUX_BOUNCE_SHORT_V1_PAPER_RESEARCH_SPEC"
PLAYBOOK = "bounce_short"
APPROVAL_TOKEN = "HUMAN_APPROVED_BUILD_DUX_BOUNCE_SHORT_V1_SPEC_ONLY"

# separated from -- must NOT be combined
SEPARATED_FROM = ("gap_up_short", "first_red_day", "options",
                  "crypto_candidates", "existing_operational_trading_lanes")

CORE_HYPOTHESIS = (
    "A small-cap equity that revisits a mechanically established historical high-volume "
    "resistance zone may subsequently underperform when historical trapped supply materially "
    "exceeds current buying demand.")
HYPOTHESIS_IS_UNPROVEN_EXTERNAL = True

# --- formulas (symbolic spec; explicitly NOT computable today) ------------------------------
FORMULAS = {
    "historical_trapped_dollar_block":
        "estimated_historical_shares_near_resistance "
        "* frozen_historical_resistance_reference_price",
    "trapped_supply_ratio":
        "estimated_historical_shares_near_resistance "
        "/ projected_current_day_volume_as_of_fixed_time",
}
FORMULAS_CURRENTLY_COMPUTABLE = False

# --- volume-at-price method distinction (exact vs approximate) ------------------------------
VAP_METHODS = {
    "preferred_exact": {
        "method": "consolidated_trade_print_or_tick_level_volume_at_price",
        "is_exact": True, "is_approximation": False},
    "fallback_approximate": {
        "method": "one_minute_ohlcv_deterministic_allocation_pre_declared",
        "is_exact": False, "is_approximation": True,
        "must_never_be_called_exact_shares_at_resistance": True},
}
DAILY_OHLCV_SUFFICIENT_FOR_VAP = False   # daily bars are INSUFFICIENT for VAP reconstruction

NO_HINDSIGHT_RULES = (
    "historical spike, resistance reference, price band, aggregation window and volume "
    "calculation use ONLY information available BEFORE the future bounce signal bar",
    "no zone may be manually or retrospectively selected because price later reacted there",
)

# --- external claimed priors -- TRADER-REPORTED HYPOTHESES, NON-EVIDENCE --------------------
EXTERNAL_CLAIMED_PRIORS = (
    {"claim": "share_price_preferably_above", "reported_value": "$3"},
    {"claim": "market_cap_below_approx", "reported_value": "$100M-$200M"},
    {"claim": "float_below_approx", "reported_value": "50M shares"},
    {"claim": "historical_dollar_block_near_or_above_approx", "reported_value": "$150M"},
    {"claim": "trapped_supply_ratio_approx", "reported_value": "2:1 or stronger"},
    {"claim": "reported_win_rate", "reported_value": "80%-85%"},
    {"claim": "reported_fade_potential", "reported_value": "50%-75%"},
)

# --- unresolved definitions -- ALL human-gated; NO numeric value chosen ---------------------
_UNRESOLVED = "UNRESOLVED_HUMAN_GATED"
UNRESOLVED_DEFINITIONS = {k: _UNRESOLVED for k in (
    "qualifying_historical_spike", "historical_resistance_reference", "resistance_band_width",
    "historical_aggregation_window", "exact_vs_approximate_vap_method",
    "minimum_trapped_dollar_block", "projected_full_day_volume_estimator",
    "estimator_as_of_time", "minimum_trapped_supply_ratio", "float_rotation",
    "point_in_time_initial_market_cap", "consolidation", "momentum_shift", "first_weakness",
    "entry", "stop", "partial_covers", "final_cover", "time_exit", "halt_handling",
    "ssr_rule201_handling", "borrow_and_locate_eligibility", "commissions", "slippage",
    "market_impact",
    # added by the pre-commit deep-read amendment
    "near_term_vs_long_lag_cohort_boundary", "entry_distance_to_resistance_band_formula",
    "entry_distance_threshold")}

# --- A. non-executable signal diagnostic (future, gated) ------------------------------------
SIGNAL_DIAGNOSTIC_REQUIREMENTS = (
    "survivorship_free_small_cap_universe", "delisted_securities",
    "premarket_and_regular_session_minute_or_trade_data",
    "point_in_time_float_and_shares_outstanding", "corporate_actions_and_dilution",
    "fixed_no_lookahead_definitions", "minimum_sample_gate",
    "unconditional_and_matched_event_benchmarks")
SIGNAL_NO_BORROW_LABEL = "SIGNAL_DIAGNOSTIC_ONLY_NOT_TRADABLE"

# --- B. executable paper simulation -- blocked until ALL exist ------------------------------
EXECUTABLE_SIM_BLOCKED_UNTIL = (
    "point_in_time_short_availability", "locate_availability_and_cost", "ongoing_borrow_fees",
    "forced_buy_in_and_recall_treatment", "trading_halt_timeline", "ssr_rule201_timeline",
    "realistic_next_bar_or_event_driven_fills", "commissions", "slippage",
    "gap_through_stop_handling", "market_impact_and_participation_limits")

# --- data tiers -----------------------------------------------------------------------------
DATA_TIERS = {
    "tier0_currently_available": "NO_QUALIFYING_SMALL_CAP_INFRASTRUCTURE",
    "tier1_signal_diagnostic":
        "BLOCKED_NEEDS_SURVIVORSHIP_FREE_SYMBOLS_DELISTINGS_PIT_FUNDAMENTALS_MINUTE_TRADE_DATA",
    "tier2_executable_simulation":
        "BLOCKED_NEEDS_TIER1_PLUS_BORROW_LOCATE_HALT_SSR_REALISTIC_EXECUTION",
    "tier3_shadow_scanner": "BLOCKED_UNTIL_TIER2_SURVIVES_HUMAN_REVIEW",
    "tier4_candidate_consideration": "BLOCKED_BEHIND_SEPARATE_EXPLICIT_HUMAN_APPROVAL",
}

# --- (1) family lifecycle context -- EXPLANATORY ONLY (does not activate other playbooks) ---
FAMILY_LIFECYCLE = {
    "gap_up_short": "current-day demand exhaustion",
    "bounce_short": "historical trapped supply vs weaker current demand",
    "first_red_day": "multi-day dollar-volume exhaustion",
    "relationship_note": (
        "A first green day may be too crowded/dangerous for a same-day Gap-Up Short, while "
        "that same high-volume event may LATER create the historical trapped-supply/resistance "
        "condition used by Bounce Short."),
}

# --- (2) the single V1 branch selected for future research; other variants out of scope ------
V1_BRANCH = "DIRECT_PREMARKET_GAP_INTO_PRIOR_HIGH_VOLUME_RESISTANCE"
V1_BRANCH_DESCRIPTION = (
    "A small-cap stock gaps in premarket toward a mechanically established historical "
    "resistance band created during a prior high-volume spike, while projected present-day "
    "demand is materially weaker than estimated historical trapped supply.")
OUT_OF_V1_SCOPE_VARIANTS = (
    "intraday_ramp_into_resistance", "near_term_vs_long_lag_pooling",
    "failed_squeeze_50pct_drop_and_bounce", "next_day_crowded_runner_fade",
    "afternoon_gap_up_exhaustion_setup")

# --- (5) projected current-day volume estimator requirements + non-circularity --------------
PROJECTED_VOLUME_ESTIMATOR_REQUIREMENTS = (
    "fixed_as_of_time", "instrument_or_universe_appropriate_historical_intraday_volume_curve",
    "only_volume_observed_up_to_the_as_of_time", "no_future_bars",
    "no_reduction_merely_because_a_collapse_is_expected")
PROJECTED_VOLUME_NON_CIRCULARITY_RULE = (
    "projected volume may be revised ONLY from observed volume pace or other pre-declared "
    "observable inputs; it may NOT be reduced because the model predicts buyers will disappear")
# transcript-reported multipliers -- NON-EVIDENCE, explicitly NOT frozen
REPORTED_VOLUME_MULTIPLIERS_NON_EVIDENCE = ("premarket_volume_x5", "premarket_volume_x10")

# --- (6) ratio interpretations -- external priors, NOT binary SPARTA thresholds -------------
RATIO_INTERPRETATIONS_NON_EVIDENCE = ("approx_1_to_1", "approx_2_to_1", "approx_10_to_1")

# --- (10) participation / market-impact priors -- external NON-EVIDENCE ---------------------
PARTICIPATION_PRIORS_NON_EVIDENCE = (
    "max_position_below_approx_10pct_of_point_in_time_float",
    "max_position_below_approx_1pct_of_current_traded_volume",
    "progressive_covering_may_be_necessary_at_large_size",
    "own_buy_to_cover_orders_can_change_the_price_path")

# --- (11) float rotation lifecycle ----------------------------------------------------------
FLOAT_ROTATION_FORMULA = "cumulative_shares_traded / point_in_time_float"
FLOAT_ROTATION_WARNING_PRIOR_NON_EVIDENCE = "approx_15x_rotation"
FLOAT_ROTATION_LIFECYCLE_NOTE = (
    "high rotation may increase same-day squeeze/crowding risk AND the same high-volume event "
    "may strengthen a later trapped-supply hypothesis; not universally bullish or bearish")

# --- (13) required FUTURE event fields (data contract only; not currently available) --------
REQUIRED_FUTURE_EVENT_FIELDS = (
    "original_spike_date", "sessions_since_historical_spike", "original_spike_total_volume",
    "estimated_volume_inside_resistance_band", "resistance_band_lower", "resistance_band_upper",
    "resistance_reference_price", "exact_or_approximate_vap_method", "premarket_gap_percentage",
    "premarket_volume_as_of_fixed_time", "projected_current_day_volume",
    "projection_method_version", "trapped_supply_ratio", "historical_trapped_dollar_block",
    "point_in_time_float", "float_rotation_on_original_event",
    "entry_distance_to_resistance_band", "approach_path", "borrow_eligibility",
    "halt_status", "ssr_status")

_CAPABILITY_FLAGS_FALSE = (
    "is_candidate", "creates_candidate", "assigns_candidate_number", "activates_lane",
    "runs_event_study", "runs_backtest", "runs_replay", "creates_labels", "fetches_data",
    "copies_data", "creates_scanner", "paper_trades", "places_orders", "connects_broker",
    "purchases_locates", "opens_options_lane", "changes_queue", "changes_gate",
    "changes_lifecycle", "changes_research_standards", "auto_commits", "auto_pushes",
    "combines_with_other_playbooks", "treats_claims_as_evidence",
    "computes_trapped_supply_now", "reads_daily_as_vap", "crosses_into_forbidden_gate",
)


def build_bounce_short_v1_spec() -> dict[str, Any]:
    """PURE. Assemble the frozen Bounce Short V1 paper-research spec. No I/O; computes/advances
    nothing; authorizes nothing."""
    blockers: list = []
    record: dict[str, Any] = {
        "schema_version": DBS_SCHEMA_VERSION, "mode": DBS_MODE, "lane": DBS_LANE,
        "classification": DBS_CLASSIFICATION,
        "record_id": RECORD_ID, "playbook": PLAYBOOK, "approved_via": APPROVAL_TOKEN,
        "is_spec_only": True, "is_candidate": False, "is_proposal": False,
        "blockers": blockers,
        # scope separation
        "bounce_short_only": True, "separated_from": list(SEPARATED_FROM),
        "combined_with_other_playbooks": False,
        # hypothesis (unproven, external)
        "core_hypothesis": CORE_HYPOTHESIS,
        "hypothesis_is_unproven_external": HYPOTHESIS_IS_UNPROVEN_EXTERNAL,
        # formulas
        "formulas": dict(FORMULAS),
        "formulas_currently_computable": FORMULAS_CURRENTLY_COMPUTABLE,
        # VAP
        "vap_methods": {k: dict(v) for k, v in VAP_METHODS.items()},
        "daily_ohlcv_sufficient_for_vap": DAILY_OHLCV_SUFFICIENT_FOR_VAP,
        "no_hindsight_rules": list(NO_HINDSIGHT_RULES),
        # external priors -> non-evidence
        "external_claimed_priors": [
            {**dict(p), "status": "TRADER_REPORTED_HYPOTHESIS",
             "proven": False, "accepted_as_evidence": False}
            for p in EXTERNAL_CLAIMED_PRIORS],
        "claims_are_non_evidence": True,
        # unresolved definitions
        "unresolved_definitions": dict(UNRESOLVED_DEFINITIONS),
        # signal vs execution
        "signal_diagnostic_requirements": list(SIGNAL_DIAGNOSTIC_REQUIREMENTS),
        "signal_no_borrow_label": SIGNAL_NO_BORROW_LABEL,
        "signal_only_is_tradable": False,
        "executable_sim_blocked_until": list(EXECUTABLE_SIM_BLOCKED_UNTIL),
        "executable_paper_simulation_blocked": True,
        # data tiers
        "data_tiers": dict(DATA_TIERS),
        # (1) family lifecycle context -- explanatory only; does NOT activate other playbooks
        "family_lifecycle": dict(FAMILY_LIFECYCLE),
        "lifecycle_context_is_explanatory_only": True,
        "lifecycle_activates_gap_up_or_first_red_day": False,
        "inherits_other_playbook_rules_or_stats": False,
        # (2) narrow V1 branch; other variants out of scope + unresolved
        "v1_branch": V1_BRANCH,
        "v1_branch_description": V1_BRANCH_DESCRIPTION,
        "out_of_v1_scope_variants": list(OUT_OF_V1_SCOPE_VARIANTS),
        "v1_branch_thresholds_assigned": False,
        # (3) historical volume precision -- band-restricted, NOT full spike-day volume
        "estimated_historical_shares_near_resistance_is_band_restricted": True,
        "trapped_shares_equals_total_spike_day_volume": False,
        "trapped_shares_precision_note": (
            "estimated_historical_shares_near_resistance includes ONLY volume allocated to the "
            "frozen historical resistance band; it must NOT equal total spike-day volume, total "
            "volume for every spike-session bar, or volume traded materially below the band"),
        # (4) VAP approximation disclosure + no future-reaction in allocation/band
        "vap_approximation_multi_bin_allocation_disclosure_required": True,
        "vap_uses_future_reaction_for_allocation_or_band": False,
        # (5) projected current-day volume estimator (unresolved) + non-circularity
        "projected_volume_estimator_requirements": list(PROJECTED_VOLUME_ESTIMATOR_REQUIREMENTS),
        "projected_volume_non_circularity_rule": PROJECTED_VOLUME_NON_CIRCULARITY_RULE,
        "projected_volume_may_be_reduced_for_expected_collapse": False,
        "reported_volume_multipliers_non_evidence": list(REPORTED_VOLUME_MULTIPLIERS_NON_EVIDENCE),
        "volume_multipliers_frozen": False,
        # (6) two demand measures; ratio as continuous feature; interpretations non-evidence
        "trapped_supply_ratio_studied_as": "continuous_feature_initially",
        "ratio_interpretations_non_evidence": list(RATIO_INTERPRETATIONS_NON_EVIDENCE),
        "ratio_interpretations_are_binary_thresholds": False,
        # (7) time-lag separation
        "future_event_must_include_sessions_since_historical_spike": True,
        "time_lag_cohorts_pooled": False,
        "near_term_and_long_lag_reported_separately": True,
        # (8) approach-path separation -- no proven superiority
        "relative_variant_win_rate_known": False,
        "preferred_variant_asserted": False,
        "v1_branch_selected_for_simplicity_not_superiority": True,
        # (9) proximity-to-resistance feature (no sizing rule yet)
        "future_feature_entry_distance_to_resistance_band": True,
        "sizing_rule_created": False,
        # (10) participation / market-impact priors -- non-evidence
        "participation_priors_non_evidence": list(PARTICIPATION_PRIORS_NON_EVIDENCE),
        # (11) float rotation lifecycle
        "float_rotation_formula": FLOAT_ROTATION_FORMULA,
        "float_rotation_warning_prior_non_evidence": FLOAT_ROTATION_WARNING_PRIOR_NON_EVIDENCE,
        "float_rotation_lifecycle_note": FLOAT_ROTATION_LIFECYCLE_NOTE,
        "float_rotation_universally_bullish_or_bearish": False,
        # (12) claimed fade / variant contradictions -- non-evidence
        "variant_fade_assignments_proven": False,
        # (13) required future event fields (data contract only)
        "required_future_event_fields": list(REQUIRED_FUTURE_EVENT_FIELDS),
        "future_event_fields_imply_current_availability": False,
        # posture
        "advances_nothing": True, "human_review_required": True,
        "next_gate": "SEPARATE_HUMAN_APPROVAL_REQUIRED_FOR_TIER1_DATA_CONTRACT_FEASIBILITY",
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_candidate": True, "no_candidate_number": True, "no_activate_lane": True,
        "no_event_study": True, "no_backtest": True, "no_replay": True, "no_labels": True,
        "no_data_fetch": True, "no_copy_data": True, "no_scanner": True, "no_paper_trades": True,
        "no_orders": True, "no_broker": True, "no_locate_purchase": True, "no_options_lane": True,
        "no_change_queue": True, "no_change_gate": True, "no_change_lifecycle": True,
        "no_change_research_standards": True, "no_auto_commit": True, "no_auto_push": True,
        "no_combine_playbooks": True, "no_treat_claims_as_evidence": True,
        "no_compute_trapped_supply_now": True, "no_daily_as_vap": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_bounce_short_v1_spec(record: Any) -> dict[str, Any]:
    """Anti-tamper validator. Valid ONLY when research-only, spec-only, classification
    SPEC_ONLY_DATA_AND_EXECUTION_BLOCKED; bounce-short kept separate; hypothesis flagged
    unproven; formulas not marked computable; exact vs approximate VAP distinguished and daily
    rejected for VAP; trader claims non-evidence (never proven/accepted); every unresolved
    definition still UNRESOLVED (no numeric value); signal-only not tradable; executable sim
    blocked; and every capability flag False."""
    f: list = []
    if not isinstance(record, dict):
        return {"valid": False, "failures": ["record_not_a_dict"]}
    r = record
    if r.get("mode") != DBS_MODE:
        f.append("mode_not_research_only")
    if r.get("classification") != DBS_CLASSIFICATION:
        f.append("classification_wrong")
    if r.get("is_spec_only") is not True:
        f.append("not_spec_only")
    if r.get("is_candidate") is not False or r.get("is_proposal") is not False:
        f.append("must_not_be_candidate_or_proposal")
    if r.get("blockers"):
        f.append("has_blockers")
    # scope separation
    if r.get("bounce_short_only") is not True or r.get("combines_with_other_playbooks") is not False \
            or r.get("combined_with_other_playbooks") is not False:
        f.append("scope_not_isolated")
    for s in ("gap_up_short", "first_red_day", "options", "crypto_candidates",
              "existing_operational_trading_lanes"):
        if s not in (r.get("separated_from") or []):
            f.append("missing_separation:%s" % s)
    # hypothesis + formulas
    if r.get("hypothesis_is_unproven_external") is not True:
        f.append("hypothesis_must_be_unproven_external")
    if r.get("formulas_currently_computable") is not False:
        f.append("formulas_must_not_be_computable_now")
    if r.get("computes_trapped_supply_now") is not False:
        f.append("must_not_compute_trapped_supply_now")
    # VAP: exact vs approximate distinguished; daily rejected
    vm = r.get("vap_methods") or {}
    if (vm.get("preferred_exact") or {}).get("is_exact") is not True:
        f.append("preferred_vap_must_be_exact")
    fb = vm.get("fallback_approximate") or {}
    if fb.get("is_approximation") is not True or fb.get("is_exact") is not False:
        f.append("fallback_vap_must_be_labelled_approximation")
    if fb.get("must_never_be_called_exact_shares_at_resistance") is not True:
        f.append("fallback_vap_must_not_be_called_exact")
    if r.get("daily_ohlcv_sufficient_for_vap") is not False or r.get("reads_daily_as_vap") is not False:
        f.append("daily_must_be_insufficient_for_vap")
    # external priors non-evidence
    if r.get("claims_are_non_evidence") is not True or r.get("treats_claims_as_evidence") is not False:
        f.append("claims_must_be_non_evidence")
    for p in (r.get("external_claimed_priors") or []):
        if p.get("proven") is not False or p.get("accepted_as_evidence") is not False \
                or p.get("status") != "TRADER_REPORTED_HYPOTHESIS":
            f.append("prior_marked_proven_or_evidence:%s" % p.get("claim"))
    # unresolved definitions -- every one still the sentinel (no numeric/other value)
    ud = r.get("unresolved_definitions") or {}
    for k in UNRESOLVED_DEFINITIONS:
        if ud.get(k) != _UNRESOLVED:
            f.append("definition_resolved_or_tampered:%s" % k)
    # signal vs execution
    if r.get("signal_only_is_tradable") is not False:
        f.append("signal_only_must_not_be_tradable")
    if r.get("signal_no_borrow_label") != SIGNAL_NO_BORROW_LABEL:
        f.append("signal_no_borrow_label_wrong")
    if r.get("executable_paper_simulation_blocked") is not True:
        f.append("executable_sim_must_be_blocked")
    for req in EXECUTABLE_SIM_BLOCKED_UNTIL:
        if req not in (r.get("executable_sim_blocked_until") or []):
            f.append("missing_executable_precondition:%s" % req)
    # data tiers
    dt = r.get("data_tiers") or {}
    if dt.get("tier0_currently_available") != "NO_QUALIFYING_SMALL_CAP_INFRASTRUCTURE":
        f.append("tier0_wrong")
    for t in ("tier1_signal_diagnostic", "tier2_executable_simulation",
              "tier3_shadow_scanner", "tier4_candidate_consideration"):
        if "BLOCKED" not in str(dt.get(t, "")):
            f.append("tier_not_blocked:%s" % t)
    # --- pre-commit deep-read amendment invariants ---
    # (1) lifecycle explanatory only; must not activate other playbooks or inherit their rules
    if r.get("lifecycle_context_is_explanatory_only") is not True:
        f.append("lifecycle_must_be_explanatory_only")
    if r.get("lifecycle_activates_gap_up_or_first_red_day") is not False:
        f.append("lifecycle_must_not_activate_other_playbooks")
    if r.get("inherits_other_playbook_rules_or_stats") is not False:
        f.append("must_not_inherit_other_playbook_rules")
    # (2) narrow V1 branch; other variants out of scope; no branch thresholds
    if r.get("v1_branch") != V1_BRANCH:
        f.append("v1_branch_wrong")
    for v in OUT_OF_V1_SCOPE_VARIANTS:
        if v not in (r.get("out_of_v1_scope_variants") or []):
            f.append("missing_out_of_scope_variant:%s" % v)
    if r.get("v1_branch_thresholds_assigned") is not False:
        f.append("v1_branch_thresholds_must_not_be_assigned")
    # (3) band-restricted trapped shares != total spike-day volume
    if r.get("estimated_historical_shares_near_resistance_is_band_restricted") is not True:
        f.append("trapped_shares_must_be_band_restricted")
    if r.get("trapped_shares_equals_total_spike_day_volume") is not False:
        f.append("trapped_shares_must_not_equal_total_spike_day_volume")
    # (4) VAP approximation disclosure + no future reaction
    if r.get("vap_approximation_multi_bin_allocation_disclosure_required") is not True:
        f.append("vap_multi_bin_disclosure_required")
    if r.get("vap_uses_future_reaction_for_allocation_or_band") is not False:
        f.append("vap_must_not_use_future_reaction")
    # (5) projected-volume estimator non-circularity; multipliers not frozen
    for req in PROJECTED_VOLUME_ESTIMATOR_REQUIREMENTS:
        if req not in (r.get("projected_volume_estimator_requirements") or []):
            f.append("missing_projected_volume_requirement:%s" % req)
    if r.get("projected_volume_may_be_reduced_for_expected_collapse") is not False:
        f.append("projected_volume_circular_collapse_adjustment_forbidden")
    if r.get("volume_multipliers_frozen") is not False:
        f.append("volume_multipliers_must_not_be_frozen")
    # (6) ratio continuous; interpretations non-evidence, not binary thresholds
    if r.get("trapped_supply_ratio_studied_as") != "continuous_feature_initially":
        f.append("ratio_must_be_continuous_feature")
    if r.get("ratio_interpretations_are_binary_thresholds") is not False:
        f.append("ratio_interpretations_must_not_be_binary_thresholds")
    # (7) time-lag never silently pooled
    if r.get("time_lag_cohorts_pooled") is not False:
        f.append("time_lag_cohorts_must_not_be_pooled")
    if r.get("near_term_and_long_lag_reported_separately") is not True:
        f.append("near_and_long_lag_must_be_reported_separately")
    if r.get("future_event_must_include_sessions_since_historical_spike") is not True:
        f.append("must_include_sessions_since_historical_spike")
    # (8) no proven variant superiority
    if r.get("relative_variant_win_rate_known") is not False:
        f.append("relative_variant_win_rate_must_be_unknown")
    if r.get("preferred_variant_asserted") is not False:
        f.append("no_preferred_variant_may_be_asserted")
    # (9) proximity feature present; no sizing rule
    if r.get("future_feature_entry_distance_to_resistance_band") is not True:
        f.append("entry_distance_feature_required")
    if r.get("sizing_rule_created") is not False:
        f.append("no_sizing_rule_may_be_created")
    # (11) float rotation not universally directional
    if r.get("float_rotation_universally_bullish_or_bearish") is not False:
        f.append("float_rotation_must_not_be_universally_directional")
    # (12) no proven fade/variant assignment
    if r.get("variant_fade_assignments_proven") is not False:
        f.append("variant_fade_assignments_must_not_be_proven")
    # (13) required future event fields present + not implying current availability
    for fld in REQUIRED_FUTURE_EVENT_FIELDS:
        if fld not in (r.get("required_future_event_fields") or []):
            f.append("missing_future_event_field:%s" % fld)
    if r.get("future_event_fields_imply_current_availability") is not False:
        f.append("future_fields_must_not_imply_current_availability")

    if r.get("advances_nothing") is not True:
        f.append("must_advance_nothing")
    for flag in _CAPABILITY_FLAGS_FALSE:
        if r.get(flag) is not False:
            f.append("capability_flag_true:%s" % flag)
    return {"valid": not f, "failures": f}
