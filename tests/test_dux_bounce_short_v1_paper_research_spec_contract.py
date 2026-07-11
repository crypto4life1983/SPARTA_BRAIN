"""Minimal integrity tests for the Dux Bounce Short V1 paper-research spec (SPEC-ONLY,
DATA- AND EXECUTION-BLOCKED). Covers only record integrity + anti-tamper."""
import sparta_commander.dux_bounce_short_v1_paper_research_spec_contract as d


def test_1_record_builds_and_validates():
    r = d.build_bounce_short_v1_spec()
    assert r["classification"] == "SPEC_ONLY_DATA_AND_EXECUTION_BLOCKED"
    assert not r["blockers"]
    assert d.validate_bounce_short_v1_spec(r)["valid"] is True


def test_2_bounce_short_separate_from_gapup_and_first_red_day():
    r = d.build_bounce_short_v1_spec()
    assert r["bounce_short_only"] is True
    assert r["combined_with_other_playbooks"] is False
    for s in ("gap_up_short", "first_red_day", "options", "crypto_candidates",
              "existing_operational_trading_lanes"):
        assert s in r["separated_from"]


def test_3_trader_claims_remain_non_evidence():
    r = d.build_bounce_short_v1_spec()
    assert r["claims_are_non_evidence"] is True
    assert r["treats_claims_as_evidence"] is False
    for p in r["external_claimed_priors"]:
        assert p["proven"] is False and p["accepted_as_evidence"] is False
        assert p["status"] == "TRADER_REPORTED_HYPOTHESIS"


def test_4_exact_vs_approximate_vap_distinguished():
    r = d.build_bounce_short_v1_spec()
    assert r["vap_methods"]["preferred_exact"]["is_exact"] is True
    fb = r["vap_methods"]["fallback_approximate"]
    assert fb["is_approximation"] is True and fb["is_exact"] is False
    assert fb["must_never_be_called_exact_shares_at_resistance"] is True


def test_5_daily_rejected_as_sufficient_for_vap():
    r = d.build_bounce_short_v1_spec()
    assert r["daily_ohlcv_sufficient_for_vap"] is False
    assert r["reads_daily_as_vap"] is False


def test_6_signal_only_not_tradable_without_borrow():
    r = d.build_bounce_short_v1_spec()
    assert r["signal_only_is_tradable"] is False
    assert r["signal_no_borrow_label"] == "SIGNAL_DIAGNOSTIC_ONLY_NOT_TRADABLE"
    assert r["executable_paper_simulation_blocked"] is True
    for req in ("point_in_time_short_availability", "locate_availability_and_cost",
                "ongoing_borrow_fees"):
        assert req in r["executable_sim_blocked_until"]


def test_7_all_operational_capability_flags_false():
    r = d.build_bounce_short_v1_spec()
    for flag in d._CAPABILITY_FLAGS_FALSE:
        assert r[flag] is False, flag
    for flag in ("is_candidate", "creates_candidate", "assigns_candidate_number",
                 "activates_lane", "runs_event_study", "runs_backtest", "runs_replay",
                 "fetches_data", "creates_scanner", "paper_trades", "places_orders",
                 "connects_broker", "purchases_locates", "opens_options_lane",
                 "auto_commits", "auto_pushes"):
        assert r[flag] is False


def test_8_tamper_to_candidate_executable_datafetch_or_proven_rejected():
    # candidate tamper
    r = d.build_bounce_short_v1_spec(); r["is_candidate"] = True
    assert d.validate_bounce_short_v1_spec(r)["valid"] is False
    # executable tamper
    r = d.build_bounce_short_v1_spec(); r["paper_trades"] = True
    assert d.validate_bounce_short_v1_spec(r)["valid"] is False
    # data-fetch tamper
    r = d.build_bounce_short_v1_spec(); r["fetches_data"] = True
    assert d.validate_bounce_short_v1_spec(r)["valid"] is False
    # proven-prior tamper
    r = d.build_bounce_short_v1_spec(); r["external_claimed_priors"][0]["proven"] = True
    assert d.validate_bounce_short_v1_spec(r)["valid"] is False
    # daily-as-VAP tamper
    r = d.build_bounce_short_v1_spec(); r["daily_ohlcv_sufficient_for_vap"] = True
    assert d.validate_bounce_short_v1_spec(r)["valid"] is False
    # silently resolving an unresolved threshold
    r = d.build_bounce_short_v1_spec(); r["unresolved_definitions"]["minimum_trapped_supply_ratio"] = 2.0
    assert d.validate_bounce_short_v1_spec(r)["valid"] is False


# ---- pre-commit deep-read amendment coverage --------------------------------

def test_amend_1_v1_selects_only_direct_premarket_gap_branch():
    r = d.build_bounce_short_v1_spec()
    assert r["v1_branch"] == "DIRECT_PREMARKET_GAP_INTO_PRIOR_HIGH_VOLUME_RESISTANCE"
    assert "gaps in premarket toward a mechanically established historical resistance band" \
        in r["v1_branch_description"]


def test_amend_2_other_variants_out_of_v1_scope():
    r = d.build_bounce_short_v1_spec()
    for v in ("intraday_ramp_into_resistance", "near_term_vs_long_lag_pooling",
              "failed_squeeze_50pct_drop_and_bounce", "next_day_crowded_runner_fade",
              "afternoon_gap_up_exhaustion_setup"):
        assert v in r["out_of_v1_scope_variants"]
    assert r["v1_branch_thresholds_assigned"] is False


def test_amend_3_total_spike_volume_not_substituted_for_band_volume():
    r = d.build_bounce_short_v1_spec()
    assert r["estimated_historical_shares_near_resistance_is_band_restricted"] is True
    assert r["trapped_shares_equals_total_spike_day_volume"] is False
    tampered = d.build_bounce_short_v1_spec()
    tampered["trapped_shares_equals_total_spike_day_volume"] = True
    assert d.validate_bounce_short_v1_spec(tampered)["valid"] is False


def test_amend_4_projected_volume_no_circular_collapse_adjustment():
    r = d.build_bounce_short_v1_spec()
    assert r["projected_volume_may_be_reduced_for_expected_collapse"] is False
    assert r["volume_multipliers_frozen"] is False
    for req in ("fixed_as_of_time", "only_volume_observed_up_to_the_as_of_time",
                "no_future_bars", "no_reduction_merely_because_a_collapse_is_expected"):
        assert req in r["projected_volume_estimator_requirements"]
    tampered = d.build_bounce_short_v1_spec()
    tampered["projected_volume_may_be_reduced_for_expected_collapse"] = True
    assert d.validate_bounce_short_v1_spec(tampered)["valid"] is False


def test_amend_5_near_term_and_long_lag_not_silently_pooled():
    r = d.build_bounce_short_v1_spec()
    assert r["time_lag_cohorts_pooled"] is False
    assert r["near_term_and_long_lag_reported_separately"] is True
    assert r["future_event_must_include_sessions_since_historical_spike"] is True
    assert r["unresolved_definitions"]["near_term_vs_long_lag_cohort_boundary"] == "UNRESOLVED_HUMAN_GATED"
    tampered = d.build_bounce_short_v1_spec(); tampered["time_lag_cohorts_pooled"] = True
    assert d.validate_bounce_short_v1_spec(tampered)["valid"] is False


def test_amend_6_no_variant_proven_superior():
    r = d.build_bounce_short_v1_spec()
    assert r["relative_variant_win_rate_known"] is False
    assert r["preferred_variant_asserted"] is False
    assert r["v1_branch_selected_for_simplicity_not_superiority"] is True
    assert r["variant_fade_assignments_proven"] is False
    tampered = d.build_bounce_short_v1_spec(); tampered["preferred_variant_asserted"] = True
    assert d.validate_bounce_short_v1_spec(tampered)["valid"] is False


def test_amend_7_ratio_interpretations_and_participation_limits_non_evidence():
    r = d.build_bounce_short_v1_spec()
    assert r["trapped_supply_ratio_studied_as"] == "continuous_feature_initially"
    assert r["ratio_interpretations_are_binary_thresholds"] is False
    assert set(r["ratio_interpretations_non_evidence"]) >= {"approx_1_to_1", "approx_2_to_1", "approx_10_to_1"}
    assert "max_position_below_approx_10pct_of_point_in_time_float" in r["participation_priors_non_evidence"]
    assert r["float_rotation_universally_bullish_or_bearish"] is False


def test_amend_8_lifecycle_context_does_not_activate_other_playbooks():
    r = d.build_bounce_short_v1_spec()
    assert r["lifecycle_context_is_explanatory_only"] is True
    assert r["lifecycle_activates_gap_up_or_first_red_day"] is False
    assert r["inherits_other_playbook_rules_or_stats"] is False
    assert "gap_up_short" in r["family_lifecycle"] and "first_red_day" in r["family_lifecycle"]
    assert r["combined_with_other_playbooks"] is False


def test_amend_9_required_future_event_fields_present_no_current_availability():
    r = d.build_bounce_short_v1_spec()
    for fld in ("original_spike_date", "sessions_since_historical_spike",
                "estimated_volume_inside_resistance_band", "resistance_band_lower",
                "resistance_band_upper", "trapped_supply_ratio", "point_in_time_float",
                "entry_distance_to_resistance_band", "approach_path", "borrow_eligibility",
                "halt_status", "ssr_status"):
        assert fld in r["required_future_event_fields"]
    assert r["future_event_fields_imply_current_availability"] is False
    # all prior integrity + anti-tamper still holds
    assert d.validate_bounce_short_v1_spec(r)["valid"] is True
