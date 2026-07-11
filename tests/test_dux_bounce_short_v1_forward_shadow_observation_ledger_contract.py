"""Integrity + anti-tamper tests for the Dux forward-shadow manual case-series ledger."""
import copy

import sparta_commander.dux_bounce_short_v1_forward_shadow_observation_ledger_contract as t


# --- helpers ---------------------------------------------------------------------------------
def reg(**over):
    """A registered (entry-snapshot-stamped), pre-outcome observation with sane manual values."""
    o = t.new_observation_record()
    o.update({
        "observation_id": "OBS-1", "ticker": "ABCD", "exchange": "NASDAQ", "sector": "Tech",
        "issuer_country": "US", "observation_date": "2026-07-10",
        "observation_timestamp": "2026-07-10T09:20:00-04:00", "current_price": 3.5,
        "premarket_gap_pct": 40.0, "original_spike_date": "2026-05-01",
        "sessions_since_original_spike": 48, "resistance_band_lower": 5.0,
        "resistance_band_upper": 6.0, "approx_historical_volume_in_band": 1_200_000,
        "approximation_method": "visual_band_from_daily_bars", "approximation_method_version": "v1",
        "vap_source_bars_or_chart_ref": "chart:ABCD_2026-05-01",
        "original_spike_total_volume": 9_000_000, "premarket_volume": 800_000,
        "premarket_volume_as_of_time": "2026-07-10T09:15:00-04:00",
        "point_in_time_shares_outstanding": 50_000_000, "shares_float_source": "manual:SEC 10-Q",
        "shares_float_source_timestamp": "2026-07-01T00:00:00+00:00", "split_flag": False,
        "reverse_split_flag": False, "dilution_flag": True, "halt_status": "NONE",
        "hypothetical_entry_price": 5.2, "hypothetical_invalidation_stop": 6.1,
        "intended_target": 3.8, "uncertainty_flags": ["premarket_volume_approx"],
        "pre_outcome_chart_ref": "chart:ABCD_pre",
        "recorded_at_utc": "2026-07-10T13:20:00+00:00",
        "signal_recorded_at_utc": "2026-07-10T13:20:00+00:00",
        "hypothetical_entry_timestamp_utc": "2026-07-10T13:35:00+00:00",
        "signal_information_cutoff_utc": "2026-07-10T13:34:00+00:00",
    })
    o.update(over)
    return t.stamp_entry_snapshot(o)


def complete(o, label="NEGATIVE_SHORT_RETURN", status="COMPLETED"):
    o = copy.deepcopy(o)
    o["status"] = status
    o["outcome_label"] = label
    o.update({
        "max_adverse_excursion_pct": 2.0, "max_favourable_excursion_pct": 10.0,
        "open_to_close_short_return_pct": -1.5, "next_session_short_return_pct": 3.0,
        "three_session_short_return_pct": 5.0,
        "outcome_window_start_utc": "2026-07-10T13:35:00+00:00",
        "outcome_window_end_utc": "2026-07-15T20:00:00+00:00",
        "outcome_data_source": "manual:broker chart", "outcome_calculation_version": "v1",
        "outcome_recorded_at_utc": "2026-07-16T00:00:00+00:00",
        "post_outcome_chart_ref": "chart:ABCD_post",
    })
    return o


def good_daily_review(**over):
    d = t.new_daily_review_record()
    d.update({
        "review_id": "DR-1", "market_date": "2026-07-10",
        "review_started_at_utc": "2026-07-10T12:00:00+00:00",
        "review_completed_at_utc": "2026-07-10T13:00:00+00:00",
        "discovery_process_version": "v1", "reviewed_universe_description": "US small caps < $10",
        "reviewed_sources": ["manual scan"], "review_completed": True,
        "all_identified_candidates_recorded_attestation": True,
    })
    d.update(over)
    return d


# --- tests -----------------------------------------------------------------------------------
def test_1_classification_branch_conclusion_pinned():
    s = t.build_observation_ledger_spec()
    assert s["classification"] == "MANUAL_FORWARD_SHADOW_CASE_SERIES_ONLY"
    assert s["selected_branch"] == "DIRECT_PREMARKET_GAP_INTO_PRIOR_HIGH_VOLUME_RESISTANCE"
    assert s["permitted_conclusion"] == "SIGNAL_DIAGNOSTIC_ONLY_NOT_TRADABLE"
    assert t.validate_observation_ledger_spec(s)["valid"] is True
    for k, v in (("classification", "X"), ("selected_branch", "Y"),
                 ("permitted_conclusion", "Z")):
        b = t.build_observation_ledger_spec(); b[k] = v
        assert t.validate_observation_ledger_spec(b)["valid"] is False


def test_2_schemas_contain_required_fields():
    o = t.new_observation_record()
    for k in ("observation_id", "ticker", "exchange", "sector", "issuer_country", "current_price",
              "premarket_gap_pct", "original_spike_date", "sessions_since_original_spike",
              "resistance_band_lower", "resistance_band_upper", "approx_historical_volume_in_band",
              "approximation_method", "original_spike_total_volume", "premarket_volume",
              "premarket_volume_as_of_time", "point_in_time_shares_outstanding", "free_float",
              "shares_float_source", "shares_float_source_timestamp", "split_flag",
              "reverse_split_flag", "dilution_flag", "halt_status", "ssr_status",
              "borrow_locate_status", "hypothetical_entry_price", "hypothetical_invalidation_stop",
              "intended_target", "pre_outcome_chart_ref", "post_outcome_chart_ref",
              "uncertainty_flags", "provenance", "entry_snapshot_hash", "sequence_number",
              "previous_record_hash", "record_hash", "signal_recorded_at_utc",
              "hypothetical_entry_timestamp_utc", "signal_information_cutoff_utc"):
        assert k in o, k
    d = t.new_daily_review_record()
    for k in ("review_id", "market_date", "market_timezone", "review_started_at_utc",
              "review_completed_at_utc", "discovery_process_version", "reviewed_universe_description",
              "reviewed_sources", "review_completed", "candidate_count",
              "candidate_observation_ids", "no_candidate_found", "incomplete_review_reason",
              "all_identified_candidates_recorded_attestation"):
        assert k in d, k


def test_3_new_observation_has_no_outcome_info():
    o = t.new_observation_record()
    assert o["status"] == "OPEN"
    assert o["vap_exactness"] == "APPROXIMATE"
    assert o["float_status_label"] == "DUX_FLOAT_FILTER_NOT_YET_VALIDATED"
    for k in t.OUTCOME_ALL_FIELDS:
        assert o[k] is None, k


def test_4_registration_after_hypothetical_entry_rejected():
    assert t.validate_observation(reg())["valid"] is True
    bad = reg(signal_recorded_at_utc="2026-07-10T13:40:00+00:00")  # after 13:35 entry
    r = t.validate_observation(bad)
    assert r["valid"] is False and "registration_after_hypothetical_entry" in r["failures"]


def test_5_information_cutoff_enforced():
    bad = reg(signal_information_cutoff_utc="2026-07-10T13:50:00+00:00")  # after entry
    r = t.validate_observation(bad)
    assert r["valid"] is False and "information_cutoff_after_hypothetical_entry" in r["failures"]


def test_6_entry_snapshot_cannot_change_after_outcome():
    o = complete(reg())
    assert t.validate_observation(o)["valid"] is True
    o["current_price"] = 999.0  # mutate a frozen entry field after outcomes recorded
    r = t.validate_observation(o)
    assert r["valid"] is False
    assert "entry_snapshot_hash_mismatch_entry_field_changed" in r["failures"]


def test_7_chain_integrity_violations_rejected():
    led = t.build_ledger([reg(observation_id="A"), reg(observation_id="B"),
                          reg(observation_id="C")])
    assert t.validate_ledger(led)["valid"] is True
    # duplicate id
    dup = copy.deepcopy(led); dup["observations"][1]["observation_id"] = "A"
    assert t.validate_ledger(dup)["valid"] is False
    # sequence gap
    gap = copy.deepcopy(led); gap["observations"][2]["sequence_number"] = 5
    assert t.validate_ledger(gap)["valid"] is False
    # reorder
    ro = copy.deepcopy(led); ro["observations"] = list(reversed(ro["observations"]))
    assert t.validate_ledger(ro)["valid"] is False
    # broken hash link
    bh = copy.deepcopy(led); bh["observations"][1]["record_hash"] = "0" * 64
    assert t.validate_ledger(bh)["valid"] is False
    # record-count mismatch
    cm = copy.deepcopy(led); cm["declared_record_count"] = 99
    assert t.validate_ledger(cm)["valid"] is False


def test_8_deletion_limitation_stated_honestly():
    s = t.build_observation_ledger_spec()
    assert s["deletion_limitation"] == \
        "DELETION_OUTSIDE_THE_SUPPLIED_CHAIN_CANNOT_BE_PROVEN_WITHOUT_AN_EXTERNAL_CHECKPOINT"
    assert "integrity guard" in s["honest_limitations"]["entry_snapshot"].lower()
    led = t.build_ledger([reg()])
    assert t.validate_ledger(led)["limitations"] == [s["deletion_limitation"]]
    b = t.build_observation_ledger_spec(); del b["deletion_limitation"]
    assert t.validate_observation_ledger_spec(b)["valid"] is False


def test_9_daily_no_candidate_review_validates():
    d = good_daily_review(no_candidate_found=True, candidate_count=0, candidate_observation_ids=[])
    assert t.validate_daily_review(d)["valid"] is True
    d2 = good_daily_review(candidate_count=2, candidate_observation_ids=["A", "B"])
    assert t.validate_daily_review(d2)["valid"] is True
    bad = good_daily_review(candidate_count=1, candidate_observation_ids=["A", "B"])
    assert t.validate_daily_review(bad)["valid"] is False  # count != referenced ids


def test_10_incomplete_review_cannot_claim_complete_capture():
    d = good_daily_review(review_completed=False,
                          all_identified_candidates_recorded_attestation=True,
                          incomplete_review_reason="ran out of time")
    r = t.validate_daily_review(d)
    assert r["valid"] is False
    assert "incomplete_review_cannot_attest_all_candidates_recorded" in r["failures"]


def test_11_missing_daily_coverage_blocks_comprehensive_claim():
    led = t.build_ledger([reg()], daily_reviews=[])
    assert t.can_claim_comprehensive(led)["comprehensive_claim_supported"] is False
    led2 = t.build_ledger([reg()], daily_reviews=[
        good_daily_review(no_candidate_found=True)])
    assert t.can_claim_comprehensive(led2)["comprehensive_claim_supported"] is True
    # spec never asserts complete coverage
    assert t.build_observation_ledger_spec()["claims_complete_market_coverage"] is False


def test_12_status_transitions_and_outcome_labels_separate():
    assert set(t.LIFECYCLE_STATUSES).isdisjoint(set(t.OUTCOME_LABELS))
    assert t.validate_status_transition("OPEN", "COMPLETED") is True
    assert t.validate_status_transition("COMPLETED", "OPEN") is False
    assert t.validate_status_transition("DISQUALIFIED_BEFORE_ENTRY", "COMPLETED") is False
    # an OPEN record may not carry an outcome label
    bad = reg(); bad["outcome_label"] = "NEGATIVE_SHORT_RETURN"
    assert t.validate_observation(bad)["valid"] is False


def test_13_units_and_formulas_pinned():
    s = t.build_observation_ledger_spec()
    assert s["short_return_formula"] == t.SHORT_RETURN_FORMULA
    assert "short" in s["mae_definition"].lower() and "short" in s["mfe_definition"].lower()
    for m in t.OUTCOME_METRIC_FIELDS:
        assert m.endswith("_pct")
        assert s["outcome_units"][m] == "percent"


def test_14_missing_float_requires_not_validated_label():
    ok = reg(free_float=None)  # default label is the not-validated marker
    assert t.validate_observation(ok)["valid"] is True
    bad = reg(free_float=None, float_status_label="FLOAT_OK")
    r = t.validate_observation(bad)
    assert r["valid"] is False and "missing_float_requires_not_validated_label" in r["failures"]


def test_15_missing_borrow_does_not_permit_dropping():
    o = complete(reg(borrow_locate_status=None), label="NEGATIVE_SHORT_RETURN")
    assert t.validate_observation(o)["valid"] is True  # retained despite no borrow + loss
    s = t.build_observation_ledger_spec()
    assert s["borrow_controls_retention"] is False
    assert s["records_removable_when_losing_or_incomplete"] is False
    b = t.build_observation_ledger_spec(); b["borrow_controls_retention"] = True
    assert t.validate_observation_ledger_spec(b)["valid"] is False


def test_16_approximate_vap_cannot_be_exact():
    bad = reg(); bad["vap_exactness"] = "EXACT"
    r = t.validate_observation(bad)
    assert r["valid"] is False and "vap_exactness_must_be_approximate" in r["failures"]
    assert t.build_observation_ledger_spec()["vap_exactness_locked"] == "APPROXIMATE"


def test_17_spike_day_total_cannot_substitute_for_band_volume():
    bad = reg(band_volume_is_full_spike_day_total=True)
    r = t.validate_observation(bad)
    assert r["valid"] is False
    assert "spike_day_total_may_not_substitute_for_band_volume" in r["failures"]


def test_18_pre_and_post_outcome_charts_separate():
    assert "pre_outcome_chart_ref" in t.ENTRY_SNAPSHOT_FIELDS
    assert "post_outcome_chart_ref" not in t.ENTRY_SNAPSHOT_FIELDS
    o = complete(reg())  # sets post chart; pre chart frozen in snapshot
    assert t.validate_observation(o)["valid"] is True
    assert o["pre_outcome_chart_ref"] == "chart:ABCD_pre"
    assert o["post_outcome_chart_ref"] == "chart:ABCD_post"


def test_19_twenty_completed_is_rule_learning_checkpoint_only():
    s = t.build_observation_ledger_spec()
    assert s["checkpoint_at_completed_observations"] == 20
    assert s["checkpoint_label"] == "RULE_LEARNING_CHECKPOINT_NOT_STATISTICAL_PROOF"
    assert s["checkpoint_is_statistical_proof"] is False
    for k in ("promotes_candidate", "approves_data_purchase", "authorizes_scanner",
              "authorizes_paper_or_live_trading", "reports_profitability"):
        assert s["checkpoint_permissions"][k] is False
    b = t.build_observation_ledger_spec(); b["checkpoint_is_statistical_proof"] = True
    assert t.validate_observation_ledger_spec(b)["valid"] is False


def test_20_all_operational_flags_false():
    s = t.build_observation_ledger_spec()
    for flag in t._CAPABILITY_FLAGS_FALSE:
        assert s[flag] is False, flag


def test_21_tamper_toward_unbiased_profitable_tradable_candidate_live_rejected():
    for flag in ("claims_unbiased_sample", "is_unbiased_universe_sample", "reports_profitability",
                 "reports_tradability", "is_candidate", "creates_candidate", "recommends_live_trade",
                 "authorizes_next_stage", "paper_trades", "live_trades", "runs_scanner",
                 "auto_market_data_fetch", "computes_account_pnl"):
        b = t.build_observation_ledger_spec(); b[flag] = True
        assert t.validate_observation_ledger_spec(b)["valid"] is False, flag
