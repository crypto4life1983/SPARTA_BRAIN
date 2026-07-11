"""Minimal integrity + anti-tamper tests for the Dux Bounce Short V1 Tier-1 signal-data
feasibility contract (spec-only, data-blocked)."""
import sparta_commander.dux_bounce_short_v1_tier1_signal_data_feasibility_contract as t


def test_1_classification_and_not_tradable_label_pinned():
    r = t.build_tier1_feasibility()
    assert r["classification"] == "TIER1_SIGNAL_DATA_FEASIBILITY_ONLY"
    assert r["permitted_future_conclusion"] == "SIGNAL_DIAGNOSTIC_ONLY_NOT_TRADABLE"
    for pc in ("executable", "shortable", "profitable_trading_strategy",
               "candidate_quality_evidence", "locate_aware", "full_dux_strategy_replicated"):
        assert pc in r["prohibited_conclusions"]
    assert t.validate_tier1_feasibility(r)["valid"] is True


def test_2_selected_v1_branch_unchanged():
    r = t.build_tier1_feasibility()
    assert r["selected_branch"] == "DIRECT_PREMARKET_GAP_INTO_PRIOR_HIGH_VOLUME_RESISTANCE"
    bad = t.build_tier1_feasibility(); bad["selected_branch"] = "SOMETHING_ELSE"
    assert t.validate_tier1_feasibility(bad)["valid"] is False


def test_3_providers_are_candidates_not_purchases():
    r = t.build_tier1_feasibility()
    assert r["any_provider_selected_for_purchase"] is False
    assert set(r["provider_candidates"]) >= {"massive_polygon", "sharadar_nasdaq_data_link",
                                             "ortex", "databento", "ibkr"}
    assert r["provider_purchase_approved"] is False and r["subscription_approved"] is False
    bad = t.build_tier1_feasibility(); bad["any_provider_selected_for_purchase"] = True
    assert t.validate_tier1_feasibility(bad)["valid"] is False


def test_4_ortex_free_float_potential_and_unresolved_not_accepted_or_unavailable():
    r = t.build_tier1_feasibility()
    assert r["historical_free_float_status"] == "POTENTIALLY_SOURCEABLE_VIA_ORTEX"
    assert r["historical_free_float_semantics"] == "COVERAGE_AND_KNOWLEDGE_DATE_SEMANTICS_UNRESOLVED"
    assert r["free_float_declared_unobtainable"] is False
    assert r["free_float_accepted"] is False
    for k in ("earliest_available_date", "historical_depth", "publication_knowledge_date",
              "restatement_policy", "dilution_and_offering_handling"):
        assert k in r["free_float_verification_required"]
    for bad_field, val in (("free_float_declared_unobtainable", True), ("free_float_accepted", True)):
        b = t.build_tier1_feasibility(); b[bad_field] = val
        assert t.validate_tier1_feasibility(b)["valid"] is False


def test_5_share_measures_remain_distinct():
    r = t.build_tier1_feasibility()
    assert "shares_outstanding" in r["float_measures"] and "free_float" in r["float_measures"]
    assert "lendable_inventory" in r["float_measures"]
    assert r["measure_distinctness_preserved"] is True
    bad = t.build_tier1_feasibility(); bad["measures_substituted"] = True
    assert t.validate_tier1_feasibility(bad)["valid"] is False


def test_6_float_absent_label():
    r = t.build_tier1_feasibility()
    assert r["float_absent_label"] == "DUX_FLOAT_FILTER_NOT_YET_VALIDATED"
    assert "not a complete replication" in r["float_absent_permitted_question"].lower()


def test_7_two_pass_design_preserved():
    r = t.build_tier1_feasibility()
    a = r["pass_a_broad_daily_discovery"]; b = r["pass_b_bounded_intraday"]
    assert a["high_recall_no_future_returns"] is True
    assert a["daily_data_may_finalize_vap_eligibility"] is False
    assert b["minute_data_purchased_or_downloaded_under_this_approval"] is False
    assert b["must_include_all_prescreened_candidates_not_only_fades"] is True


def test_8_daily_data_cannot_finalize_vap():
    r = t.build_tier1_feasibility()
    assert r["daily_data_finalizes_vap_eligibility"] is False
    bad = t.build_tier1_feasibility(); bad["daily_data_finalizes_vap_eligibility"] = True
    assert t.validate_tier1_feasibility(bad)["valid"] is False


def test_9_discovery_no_future_returns_no_famous_ticker_selection():
    r = t.build_tier1_feasibility()
    assert r["uses_future_returns_in_discovery"] is False
    for rule in ("hand_selecting_famous_tickers", "selecting_only_events_known_to_have_fallen",
                 "selecting_candidates_from_todays_surviving_symbols",
                 "using_transcript_case_studies_as_primary_sample"):
        assert rule in r["anti_selection_bias_rejected"]
    assert r["transcript_cases_role"] == "external_examples_or_implementation_checks_only"
    bad = t.build_tier1_feasibility(); bad["uses_future_returns_in_discovery"] = True
    assert t.validate_tier1_feasibility(bad)["valid"] is False


def test_10_vap_coverage_labels_distinct():
    r = t.build_tier1_feasibility()
    assert tuple(r["vap_tiers"]) == ("FULL_OR_DISCLOSED_COVERAGE_TRADE_PRINT_VAP",
                                     "PARTIAL_VENUE_TRADE_PRINT_VAP", "MINUTE_BAR_VAP_APPROXIMATION")
    assert r["databento_venue_not_consolidated_unless_assembled"] is True
    for k in ("finra_trf_off_exchange_treatment", "cancelled_corrected_trade_handling",
              "odd_lot_treatment", "historical_coverage"):
        assert k in r["massive_full_vap_label_requires"]


def test_11_point_in_time_knowledge_fields_mandatory():
    r = t.build_tier1_feasibility()
    for fld in ("effective_date", "fiscal_or_period_end", "filing_publication_date",
                "provider_last_updated", "value_known_as_of_signal_time", "staleness_days",
                "as_reported_or_restated", "source_provider", "source_dataset", "source_field"):
        assert fld in r["pit_knowledge_fields"]
    assert r["polygon_knowledge_date_semantics"] == "POINT_IN_TIME_KNOWLEDGE_DATE_SEMANTICS_UNRESOLVED"


def test_12_borrow_and_locate_concepts_separate():
    r = t.build_tier1_feasibility()
    assert r["borrow_measures_separate"] is True
    assert r["ortex_ctb_or_float_proves_locate"] is False
    for m in ("cost_to_borrow", "shares_available", "broker_specific_short_availability",
              "locate_approval", "locate_price", "recalls", "forced_buy_ins"):
        assert m in r["borrow_measures"]
    assert r["ibkr_status"] == "BROKER_SPECIFIC_INDICATIVE_RECENT_BORROW_REFERENCE"


def test_13_pilot_dates_and_counts_are_planning_defaults_human_gated():
    r = t.build_tier1_feasibility()
    assert r["pilot_planning"]["status"] == "PLANNING_DEFAULT_NOT_YET_APPROVED_FOR_EXECUTION"
    assert r["pilot_planning"]["date_range_default"] == "2019-2024"
    for k in ("exact_historical_range", "candidate_count", "discovery_split", "validation_split",
              "pass_fail_threshold"):
        assert r["pilot_unresolved"][k] == "UNRESOLVED_HUMAN_GATED"
    assert r["pilot_statistical_pass_threshold_assigned"] is False
    bad = t.build_tier1_feasibility(); bad["pilot_unresolved"]["pass_fail_threshold"] = 0.05
    assert t.validate_tier1_feasibility(bad)["valid"] is False


def test_14_all_operational_flags_false():
    r = t.build_tier1_feasibility()
    for flag in t._CAPABILITY_FLAGS_FALSE:
        assert r[flag] is False, flag


def test_15_tamper_to_purchase_fetch_candidate_executable_tradable_rejected():
    for k, v in (("provider_purchase_approved", True), ("data_fetch_approved", True),
                 ("is_candidate", True), ("reports_executable_returns", True),
                 ("reports_candidate_quality", True), ("runs_daily_discovery", True),
                 ("purchases_locates", True), ("cost_approved_or_exact", True)):
        r = t.build_tier1_feasibility(); r[k] = v
        assert t.validate_tier1_feasibility(r)["valid"] is False, k
