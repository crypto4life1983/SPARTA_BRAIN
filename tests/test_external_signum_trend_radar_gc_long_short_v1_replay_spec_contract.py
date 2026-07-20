"""C22 replay-specification (Phase A, spec-only) tests: frozen dates/counts, July 16/17/20
exclusion, determinism + stable spec hash, no optimization/fetch/execution/token/lifecycle
capability, missing-data fail-closed behavior, no-lookahead entry/exit rules, non-omittable
costs + benchmarks, and the gated-before-replay guarantees. Pure module — no dataset needed."""
import hashlib
import json

import sparta_commander.external_signum_trend_radar_gc_long_short_v1_replay_spec_contract as spec
import sparta_commander.external_signum_trend_radar_gc_long_short_v1_real_candle_labels_review_contract as rev


def test_frozen_dates_and_counts_exact():
    s = spec.build_replay_spec()
    ev = s["frozen_evidence"]
    assert ev["date_range"] == ["2026-06-20", "2026-07-15"]
    assert ev["decision_windows"] == 26
    assert ev["rows_per_window"] == 50
    assert ev["total_label_rows"] == 1300
    assert ev["actionable_labels"] == 88
    assert sum(ev["actionable_breakdown"].values()) == 88
    assert len(ev["expected_dates"]) == 26
    assert ev["expected_dates"][0] == "2026-06-20" and ev["expected_dates"][-1] == "2026-07-15"


def test_july_16_17_20_and_future_excluded():
    s = spec.build_replay_spec()
    ev = s["frozen_evidence"]
    for d in ("2026-07-16", "2026-07-17", "2026-07-20"):
        assert d not in ev["expected_dates"]
        assert d in ev["excluded_future_dates"]
    assert all(d <= "2026-07-15" for d in ev["expected_dates"])
    # forward snapshots that exist on disk are explicitly out-of-scope until gated
    inv = s["price_path_missing_data_inventory"]
    assert inv["already_on_disk_but_out_of_scope_until_gated"] == \
        ["2026-07-16", "2026-07-17", "2026-07-20"]


def test_provenance_tiers_retained_8_12_6():
    s = spec.build_replay_spec()
    assert s["frozen_evidence"]["provenance_tier_counts_retained_in_attribution"] == {
        "LEGACY_REDUCED_ONLY": 8, "LEGACY_REDUCED_WITH_SIDECAR_NO_RAW": 12,
        "FULL_RAW_REDUCTION_PROVENANCE": 6}
    assert "performance_by_provenance_tier" in s["required_results"]["attribution"]


def test_deterministic_serialization_and_stable_hash():
    s1 = spec.build_replay_spec()
    s2 = spec.build_replay_spec()
    assert spec.canonical_spec_bytes(s1) == spec.canonical_spec_bytes(s2)
    assert s1["spec_sha256"] == s2["spec_sha256"]
    # hash reproduces over canonical bytes (excludes the self field)
    assert s1["spec_sha256"] == hashlib.sha256(spec.canonical_spec_bytes(s1)).hexdigest()
    # canonical bytes are sorted + newline-terminated
    assert spec.canonical_spec_bytes(s1).endswith(b"\n")
    assert "spec_sha256" not in json.loads(spec.canonical_spec_bytes(s1))


def test_all_capability_flags_false():
    s = spec.build_replay_spec()
    for flag in spec._CAPABILITY_FLAGS_FALSE:
        assert s[flag] is False, flag
    # explicit high-risk flags
    for flag in ("runs_replay", "simulates_replay", "fetches_data", "optimizes_parameters",
                 "issues_token", "consumes_token", "unlocks_replay_gate", "advances_lifecycle",
                 "changes_collection_state", "mutates_v1_v2_artifacts", "changes_labels",
                 "changes_dates", "changes_assets", "changes_signal_rules"):
        assert s[flag] is False


def test_missing_data_inventory_is_fail_closed_and_gated():
    s = spec.build_replay_spec()
    inv = s["price_path_missing_data_inventory"]
    assert inv["status"] == "NOT_FROZEN_NOT_AUTHORIZED"
    assert inv["gate_required_before_use"] == "C22_FORWARD_PRICE_DATA_READY_FOR_HUMAN_REVIEW"
    # post-2026-07-15 snapshots are exit-only, never new entries
    assert "EXIT EVALUATION ONLY" in inv["hard_rule"]
    dc = s["price_path_data_contract"]
    assert dc["missing_bar_policy"].startswith("FAIL-CLOSED")
    assert dc["end_of_test_fail_closed_rule"]["horizon_is_proposed_not_tuned"] is True


def test_no_lookahead_entry_and_exit_rules():
    s = spec.build_replay_spec()
    sh = s["signal_handling"]
    assert "NEXT daily session" in sh["earliest_permissible_entry"]
    assert any("no same-bar fill" in x for x in sh["lookahead_prevention"])
    ex = s["execution_and_cost_model"]
    assert ex["execution_style"].startswith("next-bar")
    assert "lookahead_audit" in s["required_results"]["integrity_audit"]


def test_no_max_holding_period_invented():
    s = spec.build_replay_spec()
    em = s["exit_methodology"]
    # frozen detector spec defines NO max holding period -> must be None, not invented
    assert em["max_holding_period_in_frozen_spec"] is None
    # the only bound is the fail-closed END_OF_TEST horizon, explicitly NOT a detector rule
    assert "NOT a detector rule" in em["max_holding_period_note"]


def test_costs_and_benchmarks_cannot_be_omitted():
    s = spec.build_replay_spec()
    # 37bps is proposed, NOT silently inherited, and short carry is separately required
    cm = s["execution_and_cost_model"]
    assert cm["note_not_silently_inheriting_37bps"] is True
    assert cm["proposed_transaction_cost_all_in_round_trip_bps"] == 37.0
    assert "instrument_unresolved" in cm["short_specific_costs_must_be_separately_modeled"]
    req = s["benchmarks"]["required"]
    for b in ("BTC_buy_and_hold", "equal_weight_passive_universe",
              "zero_return_always_flat_null", "fixed_seed_random_entry_null",
              "c22_signal_off_null", "gross_vs_net_strategy"):
        assert b in req
    # validator rejects a spec with a benchmark removed
    bad = spec.build_replay_spec()
    bad["benchmarks"] = {"required": ["BTC_buy_and_hold"]}
    assert spec.validate_replay_spec(bad)["valid"] is False


def test_precommitted_rejection_gates_separated():
    s = spec.build_replay_spec()
    g = s["precommitted_rejection_gates"]
    assert g["integrity_rejection"] and g["execution_or_data_rejection"]
    assert g["economic_performance_rejection"] and g["insufficient_statistical_power_warning"]
    assert g["no_post_run_rescue"] is True and g["no_selective_rerun"] is True
    assert g["insufficient_statistical_power_warning"]["actionable_labels"] == 88


def test_proposed_lifecycle_gate_sequence_and_tokens():
    s = spec.build_replay_spec()
    gates = [g["gate"] for g in s["proposed_lifecycle_gates"]]
    assert gates == [
        "C22_REPLAY_SPEC_READY_FOR_HUMAN_REVIEW",
        "C22_FORWARD_PRICE_DATA_READY_FOR_HUMAN_REVIEW",
        "C22_DRY_RUN_READY_FOR_HUMAN_REVIEW",
        "C22_FEE_HONEST_REPLAY_READY_FOR_HUMAN_AUTHORIZATION",
        "C22_REPLAY_RESULTS_READY_FOR_HUMAN_REVIEW"]
    # the fee-honest replay gate binds the canonical committed token
    fee_gate = s["proposed_lifecycle_gates"][3]
    assert fee_gate["human_token"] == rev.NEXT_ACTION_ADVANCE
    assert s["replay_advance_token"] == "HUMAN_DECISION_C22_ADVANCE_TO_REPLAY_OR_REJECT"


def test_validator_accepts_ready_spec_rejects_tamper():
    s = spec.build_replay_spec()
    assert s["verdict"] == spec.VERDICT_READY
    assert s["blockers"] == []
    v = spec.validate_replay_spec(s)
    assert v["valid"] is True, v["failures"]
    # tamper: flip a capability flag
    t = spec.build_replay_spec()
    t["runs_replay"] = True
    assert spec.validate_replay_spec(t)["valid"] is False
    # tamper: sneak in a future date
    t2 = spec.build_replay_spec()
    t2["frozen_evidence"]["expected_dates"] = t2["frozen_evidence"]["expected_dates"] + \
        ["2026-07-16"]
    assert spec.validate_replay_spec(t2)["valid"] is False


def test_signal_set_single_sourced_unchanged():
    s = spec.build_replay_spec()
    assert set(s["signal_handling"]["signal_set_single_sourced"]) == {
        "LONG_ENTRY", "HEDGE_SHORT", "BEAR_SHORT", "NONE", "SKIP"}
    sz = s["signal_handling"]["position_sizing_pct_nav"]
    assert sz["hedge_short"] == 3.0 and sz["bear_short"] == 5.0
    assert sz["long_otherwise"] == 2.0
    assert s["signal_handling"]["leverage"] == 1
