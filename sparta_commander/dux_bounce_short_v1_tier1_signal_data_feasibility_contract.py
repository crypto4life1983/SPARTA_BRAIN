"""Dux Bounce Short V1 -- TIER-1 SIGNAL-DATA FEASIBILITY (PURE, SPEC-ONLY, DATA-BLOCKED).

Human-approved build token: HUMAN_APPROVED_BUILD_DUX_TIER1_SIGNAL_DATA_FEASIBILITY_CONTRACT_ONLY.
Classification: TIER1_SIGNAL_DATA_FEASIBILITY_ONLY.

Specifies (does NOT execute) the data feasibility for the committed research branch
DIRECT_PREMARKET_GAP_INTO_PRIOR_HIGH_VOLUME_RESISTANCE. The only future conclusion this path
may reach is SIGNAL_DIAGNOSTIC_ONLY_NOT_TRADABLE. It approves NO purchase/subscription/fetch/
download/sample of data, creates NO candidate, and opens NO lane. Providers are recorded as
feasibility candidates only. Every operational capability is pinned False; the validator
rejects any tamper toward purchase/fetch/candidate/executable/tradable status.
"""
from __future__ import annotations

from typing import Any

T1_SCHEMA_VERSION = 1
T1_MODE = "RESEARCH_ONLY"
T1_CLASSIFICATION = "TIER1_SIGNAL_DATA_FEASIBILITY_ONLY"
RECORD_ID = "DUX_BOUNCE_SHORT_V1_TIER1_SIGNAL_DATA_FEASIBILITY"
APPROVAL_TOKEN = "HUMAN_APPROVED_BUILD_DUX_TIER1_SIGNAL_DATA_FEASIBILITY_CONTRACT_ONLY"

SELECTED_BRANCH = "DIRECT_PREMARKET_GAP_INTO_PRIOR_HIGH_VOLUME_RESISTANCE"
PERMITTED_FUTURE_CONCLUSION = "SIGNAL_DIAGNOSTIC_ONLY_NOT_TRADABLE"
PROHIBITED_CONCLUSIONS = (
    "executable", "shortable", "profitable_trading_strategy", "candidate_quality_evidence",
    "locate_aware", "full_dux_strategy_replicated")
UNRESOLVED = "UNRESOLVED_HUMAN_GATED"

# --- providers: FEASIBILITY CANDIDATES ONLY (no purchase approved) --------------------------
PROVIDER_CANDIDATES = {
    "massive_polygon": "FEASIBILITY_CANDIDATE_NOT_APPROVED_PURCHASE",
    "sharadar_nasdaq_data_link": "FEASIBILITY_CANDIDATE_NOT_APPROVED_PURCHASE",
    "ortex": "FEASIBILITY_CANDIDATE_NOT_APPROVED_PURCHASE",
    "databento": "FEASIBILITY_CANDIDATE_NOT_APPROVED_PURCHASE",
    "ibkr": "BROKER_SPECIFIC_INDICATIVE_RECENT_BORROW_REFERENCE",
}

# --- historical free float (corrected): potentially sourceable via ORTEX, unresolved --------
HISTORICAL_FREE_FLOAT_STATUS = "POTENTIALLY_SOURCEABLE_VIA_ORTEX"
HISTORICAL_FREE_FLOAT_SEMANTICS = "COVERAGE_AND_KNOWLEDGE_DATE_SEMANTICS_UNRESOLVED"
FREE_FLOAT_VERIFICATION_REQUIRED = (
    "earliest_available_date", "historical_depth", "active_and_delisted_small_cap_coverage",
    "update_frequency", "effective_date", "publication_knowledge_date", "restatement_policy",
    "data_methodology", "corporate_action_handling", "dilution_and_offering_handling",
    "ticker_history_handling", "missing_value_frequency")
FREE_FLOAT_DECLARED_UNOBTAINABLE = False   # do NOT declare it unobtainable
FREE_FLOAT_ACCEPTED = False                # not accepted until verified

# distinct measures that must NEVER be substituted for one another
FLOAT_MEASURES = ("shares_outstanding", "weighted_shares_outstanding",
                  "share_class_shares_outstanding", "free_float", "lendable_inventory")
BORROW_MEASURES = ("free_float", "securities_lending_utilization", "cost_to_borrow",
                   "shares_available", "broker_specific_short_availability",
                   "lendable_quantity", "locate_approval", "locate_price", "recalls",
                   "forced_buy_ins")

FLOAT_ABSENT_LABEL = "DUX_FLOAT_FILTER_NOT_YET_VALIDATED"
FLOAT_ABSENT_PERMITTED_QUESTION = (
    "Does a return to a prior high-volume resistance zone under weaker present demand predict "
    "negative forward returns? (NOT a complete replication of the Dux Bounce Short setup)")

# --- two-pass data-acquisition design -------------------------------------------------------
PASS_A_BROAD_DAILY_DISCOVERY = {
    "purpose": "discover plausible historical candidate events without future returns and "
               "without restricting to today's surviving companies",
    "candidate_sources": ("sharadar_sep_sf1_tickers_actions",
                          "massive_historical_ticker_reference_crosscheck"),
    "required_broad_fields": (
        "stable_historical_identifier", "ticker_history", "active_delisted_status",
        "listing_and_delisting_dates", "exchange", "otc_pink_status", "daily_ohlcv",
        "splits_and_reverse_splits", "ticker_changes", "mergers_and_delistings",
        "point_in_time_shares_with_knowledge_date_fields", "sector_and_issuer_country"),
    "high_recall_no_future_returns": True,
    "may_identify": ("original_high_volume_spike_dates", "later_revisit_dates",
                     "rough_historical_resistance_references", "direct_premarket_gap_candidate_dates"),
    "daily_data_may_finalize_vap_eligibility": False,
}
PASS_B_BOUNDED_INTRADAY = {
    "precondition": "only after Pass A produces an UNBIASED candidate ledger + separate approval",
    "windows_requested": ("original_spike_session_intraday_window",
                          "historical_resistance_formation_window", "signal_date_premarket_window",
                          "signal_date_regular_session_window", "fixed_forward_return_windows"),
    "must_include_all_prescreened_candidates_not_only_fades": True,
    "minute_data_purchased_or_downloaded_under_this_approval": False,
}

ANTI_SELECTION_BIAS_REJECTED = (
    "hand_selecting_famous_tickers", "selecting_only_events_known_to_have_fallen",
    "selecting_candidates_from_todays_surviving_symbols",
    "excluding_delisted_or_bankrupt_firms",
    "dropping_events_because_borrow_unavailable_in_signal_only_analysis",
    "changing_event_definition_after_observing_returns",
    "using_transcript_case_studies_as_primary_sample")
TRANSCRIPT_CASES_ROLE = "external_examples_or_implementation_checks_only"

# --- VAP coverage tiers ---------------------------------------------------------------------
VAP_TIERS = ("FULL_OR_DISCLOSED_COVERAGE_TRADE_PRINT_VAP", "PARTIAL_VENUE_TRADE_PRINT_VAP",
             "MINUTE_BAR_VAP_APPROXIMATION")
MASSIVE_FULL_VAP_LABEL_REQUIRES = (
    "exchanges_included", "finra_trf_off_exchange_treatment", "otc_treatment",
    "odd_lot_treatment", "cancelled_corrected_trade_handling", "duplicate_handling",
    "historical_coverage")
DATABENTO_VENUE_NOT_CONSOLIDATED_UNLESS_ASSEMBLED = True

# --- point-in-time knowledge fields (mandatory on every reference/fundamental value) --------
PIT_KNOWLEDGE_FIELDS = (
    "effective_date", "fiscal_or_period_end", "filing_publication_date",
    "provider_last_updated", "value_known_as_of_signal_time", "staleness_days",
    "as_reported_or_restated", "source_provider", "source_dataset", "source_field")
PIT_UNRESOLVED_MARKER = "POINT_IN_TIME_KNOWLEDGE_DATE_SEMANTICS_UNRESOLVED"

# --- two-stage pilot: PLANNING DEFAULTS ONLY ------------------------------------------------
PILOT_PLANNING = {
    "date_range_default": "2019-2024",
    "approx_events_default": 100,
    "status": "PLANNING_DEFAULT_NOT_YET_APPROVED_FOR_EXECUTION",
}
PILOT_UNRESOLVED = {k: UNRESOLVED for k in (
    "exact_historical_range", "candidate_count", "discovery_split", "validation_split",
    "pass_fail_threshold")}
PILOT_PLANNED_OUTPUTS = (
    "open_to_close_forward_return", "next_session_return", "three_session_return", "mae", "mfe",
    "gap_adjusted_return", "matched_control_return", "unconditional_small_cap_return",
    "near_term_vs_long_lag_cohort", "exact_vs_approx_vap_tag",
    "float_available_vs_float_unavailable_cohort", "corporate_action_and_data_quality_flags")
PILOT_PRIORITIZES_FALSIFICATION = True
PILOT_STATISTICAL_PASS_THRESHOLD_ASSIGNED = False

COST_STATUS_LABELS = ("PUBLIC_LIST_PRICE", "PROVIDER_ESTIMATOR_OUTPUT", "QUOTE_REQUIRED",
                      "UNVERIFIED_BUDGET_ESTIMATE")
COST_APPROVED_OR_EXACT = False

_CAPABILITY_FLAGS_FALSE = (
    "is_candidate", "creates_candidate", "assigns_candidate_number", "activates_lane",
    "provider_purchase_approved", "subscription_approved", "data_fetch_approved",
    "data_download_approved", "data_copy_approved", "runs_daily_discovery", "runs_event_study",
    "runs_backtest", "runs_replay", "creates_labels", "creates_scanner", "paper_trades",
    "live_trades", "connects_broker", "requests_locates", "purchases_locates",
    "reports_executable_returns", "reports_candidate_quality", "changes_queue", "changes_gate",
    "changes_lifecycle", "auto_commits", "auto_pushes",
    "free_float_declared_unobtainable", "free_float_accepted",
    "daily_data_finalizes_vap_eligibility", "uses_future_returns_in_discovery",
    "modifies_bounce_short_v1", "crosses_into_forbidden_gate")


def build_tier1_feasibility() -> dict[str, Any]:
    """PURE. Assemble the Tier-1 signal-data feasibility spec. No I/O; approves nothing."""
    record: dict[str, Any] = {
        "schema_version": T1_SCHEMA_VERSION, "mode": T1_MODE,
        "classification": T1_CLASSIFICATION, "record_id": RECORD_ID,
        "approved_via": APPROVAL_TOKEN,
        "is_spec_only": True, "is_candidate": False, "is_proposal": False,
        "selected_branch": SELECTED_BRANCH,
        "permitted_future_conclusion": PERMITTED_FUTURE_CONCLUSION,
        "prohibited_conclusions": list(PROHIBITED_CONCLUSIONS),
        # providers
        "provider_candidates": dict(PROVIDER_CANDIDATES),
        "any_provider_selected_for_purchase": False,
        # free float (corrected)
        "historical_free_float_status": HISTORICAL_FREE_FLOAT_STATUS,
        "historical_free_float_semantics": HISTORICAL_FREE_FLOAT_SEMANTICS,
        "free_float_verification_required": list(FREE_FLOAT_VERIFICATION_REQUIRED),
        "free_float_declared_unobtainable": FREE_FLOAT_DECLARED_UNOBTAINABLE,
        "free_float_accepted": FREE_FLOAT_ACCEPTED,
        # measure distinctness
        "float_measures": list(FLOAT_MEASURES), "borrow_measures": list(BORROW_MEASURES),
        "measure_distinctness_preserved": True, "measures_substituted": False,
        # float-absent label
        "float_absent_label": FLOAT_ABSENT_LABEL,
        "float_absent_permitted_question": FLOAT_ABSENT_PERMITTED_QUESTION,
        # two-pass design
        "pass_a_broad_daily_discovery": {k: (list(v) if isinstance(v, tuple) else v)
                                         for k, v in PASS_A_BROAD_DAILY_DISCOVERY.items()},
        "pass_b_bounded_intraday": {k: (list(v) if isinstance(v, tuple) else v)
                                    for k, v in PASS_B_BOUNDED_INTRADAY.items()},
        # anti-selection-bias
        "anti_selection_bias_rejected": list(ANTI_SELECTION_BIAS_REJECTED),
        "transcript_cases_role": TRANSCRIPT_CASES_ROLE,
        "uses_future_returns_in_discovery": False,
        # VAP
        "vap_tiers": list(VAP_TIERS),
        "massive_full_vap_label_requires": list(MASSIVE_FULL_VAP_LABEL_REQUIRES),
        "databento_venue_not_consolidated_unless_assembled":
            DATABENTO_VENUE_NOT_CONSOLIDATED_UNLESS_ASSEMBLED,
        "daily_data_finalizes_vap_eligibility": False,
        # point-in-time knowledge
        "pit_knowledge_fields": list(PIT_KNOWLEDGE_FIELDS),
        "pit_unresolved_marker": PIT_UNRESOLVED_MARKER,
        "polygon_knowledge_date_semantics": PIT_UNRESOLVED_MARKER,
        # borrow separation
        "borrow_measures_separate": True,
        "ortex_ctb_or_float_proves_locate": False,
        "ibkr_status": "BROKER_SPECIFIC_INDICATIVE_RECENT_BORROW_REFERENCE",
        # pilot (planning defaults only)
        "pilot_planning": dict(PILOT_PLANNING),
        "pilot_unresolved": dict(PILOT_UNRESOLVED),
        "pilot_planned_outputs": list(PILOT_PLANNED_OUTPUTS),
        "pilot_prioritizes_falsification": PILOT_PRIORITIZES_FALSIFICATION,
        "pilot_statistical_pass_threshold_assigned": PILOT_STATISTICAL_PASS_THRESHOLD_ASSIGNED,
        # cost
        "cost_status_labels": list(COST_STATUS_LABELS),
        "cost_approved_or_exact": COST_APPROVED_OR_EXACT,
        # posture
        "advances_nothing": True, "human_review_required": True,
        "next_gate": "SEPARATE_HUMAN_APPROVAL_REQUIRED_FOR_PASS_A_ACQUISITION",
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_purchase": True, "no_subscription": True, "no_data_fetch": True,
        "no_data_download": True, "no_data_copy": True, "no_daily_discovery_run": True,
        "no_event_study": True, "no_backtest": True, "no_replay": True, "no_labels": True,
        "no_scanner": True, "no_paper_trades": True, "no_live_trades": True, "no_broker": True,
        "no_locate_request": True, "no_locate_purchase": True, "no_executable_returns": True,
        "no_candidate": True, "no_candidate_number": True, "no_activate_lane": True,
        "no_change_queue": True, "no_change_gate": True, "no_change_lifecycle": True,
        "no_modify_bounce_short_v1": True, "no_future_returns_in_discovery": True,
        "no_daily_vap_finalization": True, "no_declare_free_float_unobtainable": True,
        "no_accept_unverified_free_float": True, "no_auto_commit": True, "no_auto_push": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_tier1_feasibility(record: Any) -> dict[str, Any]:
    """Anti-tamper validator. Rejects any enablement of purchase/fetch/candidate/executable/
    tradable status; enforces the not-tradable label, the fixed V1 branch, provider-candidate
    (not purchased) status, the corrected free-float classification (potential+unresolved, not
    accepted and not declared unobtainable), measure distinctness, two-pass design, daily != VAP
    finalization, no-future-returns discovery, distinct VAP labels, mandatory PIT fields, borrow
    separation, planning-default (human-gated) pilot values, and all-False capability flags."""
    f: list = []
    if not isinstance(record, dict):
        return {"valid": False, "failures": ["record_not_a_dict"]}
    r = record
    if r.get("mode") != T1_MODE:
        f.append("mode_not_research_only")
    if r.get("classification") != T1_CLASSIFICATION:
        f.append("classification_wrong")
    if r.get("is_spec_only") is not True or r.get("is_candidate") is not False:
        f.append("must_be_spec_only_not_candidate")
    if r.get("selected_branch") != SELECTED_BRANCH:
        f.append("selected_branch_changed")
    if r.get("permitted_future_conclusion") != PERMITTED_FUTURE_CONCLUSION:
        f.append("permitted_conclusion_wrong")
    for pc in PROHIBITED_CONCLUSIONS:
        if pc not in (r.get("prohibited_conclusions") or []):
            f.append("missing_prohibited_conclusion:%s" % pc)
    # providers = candidates only
    if r.get("any_provider_selected_for_purchase") is not False:
        f.append("no_provider_may_be_selected_for_purchase")
    pv = r.get("provider_candidates") or {}
    for k in ("massive_polygon", "sharadar_nasdaq_data_link", "ortex", "databento", "ibkr"):
        if k not in pv:
            f.append("missing_provider_candidate:%s" % k)
    if pv.get("ibkr") != "BROKER_SPECIFIC_INDICATIVE_RECENT_BORROW_REFERENCE":
        f.append("ibkr_status_wrong")
    # free float: potential + unresolved; not accepted; not declared unobtainable
    if r.get("historical_free_float_status") != HISTORICAL_FREE_FLOAT_STATUS:
        f.append("free_float_status_wrong")
    if r.get("historical_free_float_semantics") != HISTORICAL_FREE_FLOAT_SEMANTICS:
        f.append("free_float_semantics_wrong")
    if r.get("free_float_declared_unobtainable") is not False:
        f.append("must_not_declare_free_float_unobtainable")
    if r.get("free_float_accepted") is not False:
        f.append("must_not_accept_unverified_free_float")
    # measure distinctness
    if r.get("measure_distinctness_preserved") is not True or r.get("measures_substituted") is not False:
        f.append("measures_must_stay_distinct")
    if r.get("float_absent_label") != FLOAT_ABSENT_LABEL:
        f.append("float_absent_label_wrong")
    # two-pass + daily != VAP finalization + no future returns in discovery
    if (r.get("pass_a_broad_daily_discovery") or {}).get("daily_data_may_finalize_vap_eligibility") is not False:
        f.append("daily_must_not_finalize_vap")
    if r.get("daily_data_finalizes_vap_eligibility") is not False:
        f.append("daily_vap_finalization_forbidden")
    if (r.get("pass_b_bounded_intraday") or {}).get("minute_data_purchased_or_downloaded_under_this_approval") is not False:
        f.append("no_minute_data_under_this_approval")
    if r.get("uses_future_returns_in_discovery") is not False:
        f.append("discovery_must_not_use_future_returns")
    for rule in ("selecting_candidates_from_todays_surviving_symbols",
                 "selecting_only_events_known_to_have_fallen", "hand_selecting_famous_tickers"):
        if rule not in (r.get("anti_selection_bias_rejected") or []):
            f.append("missing_anti_selection_rule:%s" % rule)
    # VAP labels distinct
    if tuple(r.get("vap_tiers") or ()) != VAP_TIERS:
        f.append("vap_tiers_tampered")
    if r.get("databento_venue_not_consolidated_unless_assembled") is not True:
        f.append("databento_venue_label_wrong")
    # PIT knowledge fields mandatory
    for fld in PIT_KNOWLEDGE_FIELDS:
        if fld not in (r.get("pit_knowledge_fields") or []):
            f.append("missing_pit_field:%s" % fld)
    # borrow separation
    if r.get("borrow_measures_separate") is not True or r.get("ortex_ctb_or_float_proves_locate") is not False:
        f.append("borrow_separation_violated")
    # pilot planning-default + human-gated
    if (r.get("pilot_planning") or {}).get("status") != "PLANNING_DEFAULT_NOT_YET_APPROVED_FOR_EXECUTION":
        f.append("pilot_must_be_planning_default")
    if any(v != UNRESOLVED for v in (r.get("pilot_unresolved") or {}).values()) \
            or set(r.get("pilot_unresolved") or {}) != set(PILOT_UNRESOLVED):
        f.append("pilot_gated_values_must_be_unresolved")
    if r.get("pilot_statistical_pass_threshold_assigned") is not False:
        f.append("no_pass_threshold_may_be_assigned")
    # cost not approved/exact
    if r.get("cost_approved_or_exact") is not False:
        f.append("no_cost_may_be_approved_or_exact")
    if r.get("advances_nothing") is not True:
        f.append("must_advance_nothing")
    for flag in _CAPABILITY_FLAGS_FALSE:
        if r.get(flag) is not False:
            f.append("capability_flag_true:%s" % flag)
    return {"valid": not f, "failures": f}
