"""C22 replay-specification (Phase A, REV1) tests. Verify the nine revision points plus the
Phase-A invariants: frozen dates/counts, July 16/17/20 exclusion, determinism + stable hash,
no optimization/fetch/execution/token/lifecycle capability, no artificial strategy max-hold,
unresolved short instrument, disaggregated costs, forward-snapshot alignment, delisting
separation, deterministic exposure ordering, survivorship-free benchmarks, non-decisive
held-out, and the gated-before-replay guarantees. Pure module — no dataset needed."""
import hashlib
import json

import sparta_commander.external_signum_trend_radar_gc_long_short_v1_replay_spec_contract as spec
import sparta_commander.external_signum_trend_radar_gc_long_short_v1_real_candle_labels_review_contract as rev


def test_frozen_dates_counts_and_exclusions():
    s = spec.build_replay_spec()
    ev = s["frozen_evidence"]
    assert ev["date_range"] == ["2026-06-20", "2026-07-15"]
    assert ev["decision_windows"] == 26 and ev["total_label_rows"] == 1300
    assert ev["actionable_labels"] == 88 and sum(ev["actionable_breakdown"].values()) == 88
    assert len(ev["expected_dates"]) == 26 and ev["expected_dates"][-1] == "2026-07-15"
    assert ev["no_new_entry_after"] == "2026-07-15"
    for d in ("2026-07-16", "2026-07-17", "2026-07-20"):
        assert d not in ev["expected_dates"] and d in ev["excluded_future_dates"]
    assert all(d <= "2026-07-15" for d in ev["expected_dates"])


def test_point1_no_artificial_30day_strategy_exit():
    s = spec.build_replay_spec()
    em = s["exit_methodology"]
    assert em["max_holding_period_in_frozen_spec"] is None
    assert em["no_artificial_strategy_max_hold"] is True
    fl = em["forced_or_administrative_liquidation"]
    assert fl["is_a_strategy_exit"] is False
    assert em["unresolved_positions_after_reviewed_coverage"] == \
        "BLOCKED_BY_INSUFFICIENT_FORWARD_EXIT_PATH_DATA"
    fx = s["forward_exit_path_extension_rule"]
    assert fx["initial_review_calendar_days"] == 30
    assert fx["extension_increment_calendar_days"] == 15
    assert fx["increment_is_predeclared_not_outcome_driven"] is True
    assert fx["extension_defined_without_examining_economic_results"] is True
    assert fx["administrative_liquidation_excluded_from_decisive_metrics"] is True
    assert fx["no_new_entries_after"] == "2026-07-15"
    assert "non-export" in fx["weekend_and_non_export_handling"].lower()


def test_point2_short_instrument_unresolved_and_fail_closed():
    s = spec.build_replay_spec()
    sg = s["short_instrument_gate"]
    assert sg["status"] == "UNRESOLVED_PENDING_SEPARATE_HUMAN_SELECTION"
    assert sg["thirty_seven_bps_short_model_approved"] is False
    assert set(sg["options"]) == {"linear_perpetual_futures", "spot_margin_short"}
    for req in ("explicit venue", "instrument type", "historical price source"):
        assert any(req in x for x in sg["required_before_dry_run"])
    fc = " ".join(sg["fail_closed_when"])
    for cond in ("did not exist on the signal date", "borrow availability cannot be established",
                 "cannot be mapped deterministically", "differs materially"):
        assert cond in fc
    assert sg["same_ohlc_for_both_not_assumed"] is True


def test_point3_disaggregated_costs_37bps_only_sensitivity():
    s = spec.build_replay_spec()
    cm = s["execution_and_cost_model"]
    for comp in ("exchange_fee_entry", "exchange_fee_exit", "bid_ask_spread", "entry_slippage",
                 "exit_slippage", "funding_or_borrow_cost",
                 "exceptional_or_liquidation_exit_cost"):
        assert comp in cm["disaggregated_cost_components"]
    assert cm["base_case_values_frozen_here"] is False
    assert "SENSITIVITY" in cm["thirty_seven_bps_role"].upper()
    assert cm["sensitivity_all_in_round_trip_bps"] == 37.0
    assert cm["results_required_at_three_levels"] == ["gross", "transaction_cost_only",
                                                      "fully_net"]
    assert "reviewed execution-data contract" in cm["base_case_values_source"]


def test_point4_forward_snapshot_alignment_and_exit_only():
    s = spec.build_replay_spec()
    fa = s["forward_snapshot_alignment"]
    assert fa["exit_only_manifest_marker"] == "EXIT_ONLY"
    assert "FAIL-CLOSED" in fa["malformed_or_unavailable_export"]
    assert "top-50" in fa["out_of_radar_definition"].lower()
    assert "Monday" in fa["friday_positions_before_monday"]
    assert "carry" in fa["weekend_non_export_dates"].lower()
    assert "next" in fa["timestamp_alignment"].lower()
    assert "REJECTED" in fa["post_2026_07_15_snapshots"]


def test_point5_delisting_separated_from_out_of_radar():
    s = spec.build_replay_spec()
    du = s["delisting_and_unavailability"]
    assert du["categories"] == list(spec.UNAVAILABILITY_CATEGORIES)
    assert du["delisting_not_treated_as_ordinary_out_of_radar"] is True
    assert du["never_invent_favourable_price"] is True
    assert "DELISTED_EXIT" in du["PERMANENT_DELISTING"]
    assert "FAIL-CLOSED" in du["NO_EXECUTABLE_NEXT_BAR"]


def test_point6_exposure_ordering_deterministic():
    s = spec.build_replay_spec()
    sh = s["signal_handling"]
    assert sh["deterministic_competition_ordering"] == [
        "decision_date_ascending", "market_rank_ascending",
        "stable_asset_identifier_ascending"]
    assert sh["one_position_per_asset"] is True
    assert sh["no_simultaneous_long_and_short_same_asset"] is True
    assert sh["max_gross_exposure_pct_nav"] == 100.0
    assert "REJECTION" in sh["insufficient_nav_rule"].upper()
    assert "resized" in sh["insufficient_nav_rule"]
    assert "EXITS are processed BEFORE entries" in sh["exit_ordering_vs_entry"]
    assert "SKIPPED" in sh["signal_while_exit_pending"]


def test_point7_benchmarks_survivorship_free_and_matched_random():
    s = spec.build_replay_spec()
    bm = s["benchmarks"]
    for b in ("BTC_buy_and_hold", "equal_weight_passive_universe_point_in_time",
              "zero_return_always_flat_null", "fixed_seed_matched_random_entry_null",
              "c22_signal_off_control", "gross_vs_net_strategy"):
        assert b in bm["required"]
    assert "point-in-time" in bm["survivorship_bias_control"]
    assert "MATCHED" in bm["random_null_matching"]
    assert bm["random_null_no_easier_execution"] is True


def test_point8_held_out_is_non_decisive():
    s = spec.build_replay_spec()
    rg = s["precommitted_rejection_gates"]
    ho = rg["held_out_segment"]
    assert ho["is_decisive_gate"] is False
    assert "NON-DECISIVE" in ho["role"].upper()
    # must NOT appear in the economic rejection list any more
    assert not any("held-out" in x.lower() or "forward/held-out" in x.lower()
                   for x in rg["economic_performance_rejection"])


def test_point9_four_separated_gate_classes_and_non_conclusive_annualized():
    s = spec.build_replay_spec()
    rg = s["precommitted_rejection_gates"]
    assert rg["integrity_rejection"] and rg["data_or_execution_rejection"]
    assert rg["economic_performance_rejection"] and rg["insufficient_statistical_power_warning"]
    assert rg["insufficient_statistical_power_warning"]["actionable_labels"] == 88
    for k in ("no_post_run_optimization", "no_selective_asset_removal",
              "no_selective_date_removal", "no_selective_rerun", "no_post_run_rescue"):
        assert rg[k] is True
    assert s["required_results"]["annualized_return_marked_non_conclusive"] is True
    assert s["required_results"]["return"] == ["gross_return", "transaction_cost_only_return",
                                               "net_return"]


def test_all_capability_flags_false():
    s = spec.build_replay_spec()
    for flag in spec._CAPABILITY_FLAGS_FALSE:
        assert s[flag] is False, flag
    for flag in ("runs_replay", "simulates_replay", "fetches_data", "admits_forward_data",
                 "optimizes_parameters", "issues_token", "consumes_token",
                 "approves_short_instrument", "approves_cost_base_case", "unlocks_replay_gate",
                 "advances_lifecycle", "changes_collection_state", "mutates_v1_v2_artifacts",
                 "modifies_lifecycle_orchestrator", "invents_prices"):
        assert s[flag] is False


def test_missing_data_inventory_fail_closed_and_gated():
    s = spec.build_replay_spec()
    inv = s["price_path_missing_data_inventory"]
    assert inv["status"] == "NOT_FROZEN_NOT_AUTHORIZED"
    assert inv["insufficient_data_outcome"] == "BLOCKED_BY_INSUFFICIENT_FORWARD_EXIT_PATH_DATA"
    assert inv["gate_required_before_use"] == "C22_FORWARD_PRICE_DATA_READY_FOR_HUMAN_REVIEW"
    assert inv["already_on_disk_but_out_of_scope_until_gated"] == \
        ["2026-07-16", "2026-07-17", "2026-07-20"]


def test_no_lookahead_and_next_bar_execution():
    s = spec.build_replay_spec()
    sh = s["signal_handling"]
    assert "NEXT executable market session" in sh["earliest_permissible_entry"]
    assert any("no same-bar fill" in x for x in sh["lookahead_prevention"])
    assert s["execution_and_cost_model"]["execution_style"].startswith("next-bar")
    assert "lookahead_audit" in s["required_results"]["integrity_audit"]


def test_determinism_stable_hash_and_canonical():
    s1 = spec.build_replay_spec()
    s2 = spec.build_replay_spec()
    assert spec.canonical_spec_bytes(s1) == spec.canonical_spec_bytes(s2)
    assert s1["spec_sha256"] == s2["spec_sha256"]
    assert s1["spec_sha256"] == hashlib.sha256(spec.canonical_spec_bytes(s1)).hexdigest()
    assert spec.canonical_spec_bytes(s1).endswith(b"\n")
    assert "spec_sha256" not in json.loads(spec.canonical_spec_bytes(s1))


def test_lifecycle_gate_sequence_and_token():
    s = spec.build_replay_spec()
    gates = [g["gate"] for g in s["proposed_lifecycle_gates"]]
    assert gates == [
        "C22_REPLAY_SPEC_READY_FOR_HUMAN_REVIEW",
        "C22_FORWARD_PRICE_DATA_READY_FOR_HUMAN_REVIEW",
        "C22_DRY_RUN_READY_FOR_HUMAN_REVIEW",
        "C22_FEE_HONEST_REPLAY_READY_FOR_HUMAN_AUTHORIZATION",
        "C22_REPLAY_RESULTS_READY_FOR_HUMAN_REVIEW"]
    assert s["proposed_lifecycle_gates"][3]["human_token"] == rev.NEXT_ACTION_ADVANCE
    assert s["replay_advance_token"] == "HUMAN_DECISION_C22_ADVANCE_TO_REPLAY_OR_REJECT"


def test_validator_accepts_ready_rejects_tamper():
    s = spec.build_replay_spec()
    assert s["verdict"] == spec.VERDICT_READY and s["blockers"] == []
    assert spec.validate_replay_spec(s)["valid"] is True, spec.validate_replay_spec(s)["failures"]
    # tamper: approve the short 37bps model
    t = spec.build_replay_spec(); t["short_instrument_gate"]["thirty_seven_bps_short_model_approved"] = True
    assert spec.validate_replay_spec(t)["valid"] is False
    # tamper: make forced liquidation a strategy exit
    t2 = spec.build_replay_spec()
    t2["exit_methodology"]["forced_or_administrative_liquidation"]["is_a_strategy_exit"] = True
    assert spec.validate_replay_spec(t2)["valid"] is False
    # tamper: reinstate held-out as decisive
    t3 = spec.build_replay_spec()
    t3["precommitted_rejection_gates"]["held_out_segment"]["is_decisive_gate"] = True
    assert spec.validate_replay_spec(t3)["valid"] is False
    # tamper: future date
    t4 = spec.build_replay_spec()
    t4["frozen_evidence"]["expected_dates"].append("2026-07-16")
    assert spec.validate_replay_spec(t4)["valid"] is False
