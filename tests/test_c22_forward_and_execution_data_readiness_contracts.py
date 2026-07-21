"""C22 Phase B1 forward-exit-data + execution-data readiness contract tests. Pure modules --
no dataset needed. Verify frozen cutoff, EXIT_ONLY, no-entry-after-cutoff, entire-export vs
asset-absence distinction, deterministic 30/15 horizon, coverage-blocks-readiness, short
instrument unresolved, funding/borrow non-omittable, basis review required, 37bps sensitivity-
only, componentized costs, no fetch/admit/replay/token/lifecycle capability, deterministic
serialization, stable hashes."""
import hashlib
import json

import pytest

import sparta_commander.c22_forward_exit_data_readiness_contract as fed
import sparta_commander.c22_execution_data_short_instrument_feasibility_contract as exe
import tools.c22_forward_and_execution_data_readiness_report_once as rpt


# ---------------- Forward exit-data contract ----------------
def test_frozen_cutoff_and_exit_only():
    c = fed.build_forward_exit_data_contract()
    assert c["entry_cutoff"] == "2026-07-15"
    assert c["first_exit_only_date"] == "2026-07-16"
    assert c["no_new_entries_after_cutoff"] is True
    assert c["post_cutoff_files_marked"] == "EXIT_ONLY"
    assert c["post_cutoff_not_used_in_v2_labels_or_entries"] is True
    assert c["bound_replay_spec_sha256"] == \
        "9bf10af353521738f440c2e953af44cdd5ed093590f03a843a01972485dd9867"


def test_july_16_17_20_cannot_generate_entries():
    for d in ("2026-07-16", "2026-07-17", "2026-07-20"):
        assert fed.is_admissible_entry_date(d) is False
    assert fed.is_admissible_entry_date("2026-07-15") is True
    assert fed.is_admissible_entry_date("2026-06-20") is True


def test_entire_export_failure_differs_from_asset_absence():
    d = fed.REV1_FIVE_CASE_DISTINCTION
    assert d["absent_from_valid_top50"] == "OUT_OF_RADAR"
    assert d["entire_export_missing_or_malformed"] == "FAIL_CLOSED_HALT"
    assert d["no_executable_price"] == "FAIL_CLOSED_HALT"
    assert d["temporary_suspension"] == "HOLD_AND_FLAG"
    assert d["permanent_delisting_with_real_price"] == "DELISTED_EXIT_DIAGNOSTIC"
    # the two are genuinely different outcomes
    assert d["absent_from_valid_top50"] != d["entire_export_missing_or_malformed"]


def test_initial_30day_and_15day_extensions_deterministic():
    c = fed.build_forward_exit_data_contract()
    ir = c["initial_exit_data_range"]
    assert ir["start"] == "2026-07-16" and ir["calendar_days"] == 30
    assert ir["end"] == "2026-08-14"  # 2026-07-16 + 29 days
    e1 = c["first_extension_range"]; e2 = c["second_extension_range"]
    assert e1["start"] == "2026-08-15" and e1["end"] == "2026-08-29" and e1["calendar_days"] == 15
    assert e2["start"] == "2026-08-30" and e2["end"] == "2026-09-13"
    # deterministic: pure function of index, recomputes identically
    assert fed.extension_range(1) == e1 and fed.extension_range(2) == e2
    assert c["extension_is_deterministic_not_outcome_driven"] is True


def test_expected_sessions_are_weekdays_only():
    sess = fed.expected_export_sessions("2026-07-16", "2026-07-22")
    # 07-18 Sat, 07-19 Sun excluded
    assert "2026-07-18" not in sess and "2026-07-19" not in sess
    assert sess == ["2026-07-16", "2026-07-17", "2026-07-20", "2026-07-21", "2026-07-22"]


def test_incomplete_coverage_blocks_readiness():
    sess = fed.expected_export_sessions("2026-07-16", "2026-07-22")
    present = {"2026-07-16", "2026-07-17", "2026-07-20"}  # 07-21, 07-22 missing
    r = fed.readiness_from_coverage(sess, present)
    assert r["covered"] is False
    assert r["readiness"] == "BLOCKED_BY_INSUFFICIENT_FORWARD_EXIT_PATH_DATA"
    assert r["missing_sessions"] == ["2026-07-21", "2026-07-22"]
    # full coverage -> complete
    r2 = fed.readiness_from_coverage(sess, present | {"2026-07-21", "2026-07-22"})
    assert r2["covered"] is True and r2["readiness"] == "COVERAGE_COMPLETE_FOR_RANGE"


def test_classification_never_admits():
    c = fed.build_forward_exit_data_contract()
    assert c["classification_never_admits"] is True
    assert set(fed.INVENTORY_CLASSES) == {
        "PRESENT_BUT_NOT_ADMITTED", "VALID_EXIT_ONLY_CANDIDATE", "INVALID", "DUPLICATE",
        "OUTSIDE_REQUIRED_RANGE", "MISSING_EXPECTED_EXPORT"}
    # a valid present in-range post-cutoff snapshot is at most a candidate, never admitted
    assert fed.classify_inventory_date("2026-07-16", True, True, False, True) == \
        "VALID_EXIT_ONLY_CANDIDATE"
    assert fed.classify_inventory_date("2026-07-16", False, False, False, True) == \
        "MISSING_EXPECTED_EXPORT"
    assert fed.classify_inventory_date("2026-06-20", True, True, False, False) == \
        "OUTSIDE_REQUIRED_RANGE"
    assert fed.classify_inventory_date("2026-07-16", True, True, True, True) == "DUPLICATE"
    assert fed.classify_inventory_date("2026-07-16", True, False, False, True) == "INVALID"


def test_admin_liquidation_non_decisive():
    c = fed.build_forward_exit_data_contract()
    al = c["administrative_liquidation"]
    assert al["non_decisive"] is True
    assert al["excluded_from_return_sharpe_calmar_benchmarks"] is True
    assert al["permitted_only_as_truncation_diagnostic"] is True


def test_forward_required_fields_present():
    c = fed.build_forward_exit_data_contract()
    for fld in ("runDate", "gc.upper", "gc.filter", "gc.trend", "source_sha256",
                "exit_only_admission_marker", "provenance_tier_or_source_class"):
        assert fld in c["required_snapshot_fields"]


def test_forward_capability_flags_false_and_validator():
    c = fed.build_forward_exit_data_contract()
    for flag in fed._CAPABILITY_FLAGS_FALSE:
        assert c[flag] is False, flag
    assert c["verdict"] == fed.VERDICT_READY and c["blockers"] == []
    v = fed.validate_forward_exit_data_contract(c)
    assert v["valid"] is True, v["failures"]
    # tamper: admit entries after cutoff
    t = fed.build_forward_exit_data_contract(); t["no_new_entries_after_cutoff"] = False
    assert fed.validate_forward_exit_data_contract(t)["valid"] is False


# ---------------- Execution-data / short feasibility contract ----------------
def test_short_instrument_unresolved():
    c = exe.build_execution_data_contract()
    assert c["short_instrument_status"] == "UNRESOLVED_PENDING_SEPARATE_HUMAN_SELECTION"
    assert c["instrument_selected"] is False


def test_both_options_specified_and_fail_closed():
    c = exe.build_execution_data_contract()
    o1 = c["option_1_linear_perpetual_futures"]
    o2 = c["option_2_spot_margin_short"]
    for r in ("historical_funding_rate_source", "funding_timestamps_and_payment_intervals",
              "tick_size", "lot_size", "delisting_and_contract_migration_history"):
        assert r in o1["requirements"]
    for r in ("historical_borrow_availability", "historical_borrow_rate_source",
              "borrow_charging_interval", "suspension_and_delisting_history"):
        assert r in o2["requirements"]
    assert o1["fail_closed_when_any_absent"] is True
    assert o2["fail_closed_when_any_absent"] is True


def test_funding_or_borrow_cannot_be_omitted():
    c = exe.build_execution_data_contract()
    assert "funding_or_borrow_cost" in c["cost_components"]
    # prohibitions forbid assuming zero funding / borrow availability
    for p in ("assuming_zero_funding", "assuming_borrow_availability",
              "silently_using_spot_ohlc_for_perpetual_fills",
              "silently_using_perpetual_ohlc_for_spot_margin_fills",
              "substituting_a_currently_available_instrument_for_one_that_did_not_exist_historically"):
        assert p in c["prohibitions"]


def test_signal_execution_basis_review_required():
    c = exe.build_execution_data_contract()
    assert c["basis_alignment_review_required"] is True
    assert c["basis_adjustment_selected"] is False
    for fld in ("signal_price", "execution_reference_price", "percentage_basis",
                "symbol_map_confidence"):
        assert fld in c["basis_alignment_diagnostic_fields"]


def test_37bps_sensitivity_only_and_componentized():
    c = exe.build_execution_data_contract()
    assert c["thirty_seven_bps_status"] == "SENSITIVITY_CASE_NOT_BASE_CASE"
    assert c["thirty_seven_bps_is_base_case"] is False
    assert c["cost_base_case_approved"] is False
    for comp in ("entry_exchange_fee", "exit_exchange_fee", "entry_half_spread",
                 "exit_half_spread", "entry_slippage", "exit_slippage",
                 "funding_or_borrow_cost", "exceptional_exit_cost"):
        assert comp in c["cost_components"]
    assert c["cost_result_levels"] == ["gross", "transaction_cost_only_net",
                                       "fully_net_after_funding_or_borrow"]


def test_execution_feasibility_and_liquidity_evidence():
    c = exe.build_execution_data_contract()
    efr = c["execution_feasibility_rules"]
    assert efr["exits_before_entries"] is True
    assert efr["no_proportional_resizing"] is True
    assert efr["missing_next_bar_fail_closed"] is True
    assert efr["deterministic_ordering"] == ["decision_date_ascending", "market_rank_ascending",
                                             "stable_asset_identifier_ascending"]
    assert "UNRESOLVED" in efr["partial_fill_policy"]
    for ev in ("daily_notional_volume", "order_size_as_pct_of_volume", "lot_size",
               "price_increment", "instrument_availability"):
        assert ev in c["liquidity_feasibility_evidence"]


def test_proposed_lifecycle_gates_inactive():
    c = exe.build_execution_data_contract()
    gates = [g["gate"] for g in c["proposed_lifecycle_gates"]]
    assert gates == [
        "C22_FORWARD_EXIT_DATA_CONTRACT_READY_FOR_HUMAN_REVIEW",
        "C22_EXECUTION_DATA_CONTRACT_READY_FOR_HUMAN_REVIEW",
        "C22_EXIT_ONLY_DATASET_READY_FOR_ADMISSION_REVIEW",
        "C22_SHORT_INSTRUMENT_READY_FOR_HUMAN_SELECTION",
        "C22_EXECUTION_COST_BASE_CASE_READY_FOR_HUMAN_REVIEW",
        "C22_DRY_RUN_SPEC_READY_FOR_HUMAN_REVIEW"]
    assert c["lifecycle_gates_activated"] is False
    for g in c["proposed_lifecycle_gates"]:
        assert g["human_token"].startswith("HUMAN_DECISION_C22_")


def test_execution_capability_flags_false_and_validator():
    c = exe.build_execution_data_contract()
    for flag in exe._CAPABILITY_FLAGS_FALSE:
        assert c[flag] is False, flag
    assert c["verdict"] == exe.VERDICT_READY and c["blockers"] == []
    v = exe.validate_execution_data_contract(c)
    assert v["valid"] is True, v["failures"]
    # tamper: select instrument
    t = exe.build_execution_data_contract(); t["instrument_selected"] = True
    assert exe.validate_execution_data_contract(t)["valid"] is False
    # tamper: make 37bps the base case
    t2 = exe.build_execution_data_contract(); t2["thirty_seven_bps_is_base_case"] = True
    assert exe.validate_execution_data_contract(t2)["valid"] is False


# ---------------- determinism ----------------
def test_deterministic_serialization_and_stable_hashes():
    a1 = fed.build_forward_exit_data_contract(); a2 = fed.build_forward_exit_data_contract()
    assert fed.canonical_contract_bytes(a1) == fed.canonical_contract_bytes(a2)
    assert a1["contract_sha256"] == a2["contract_sha256"]
    assert a1["contract_sha256"] == hashlib.sha256(fed.canonical_contract_bytes(a1)).hexdigest()
    b1 = exe.build_execution_data_contract(); b2 = exe.build_execution_data_contract()
    assert exe.canonical_contract_bytes(b1) == exe.canonical_contract_bytes(b2)
    assert b1["contract_sha256"] == b2["contract_sha256"]
    assert "contract_sha256" not in json.loads(fed.canonical_contract_bytes(a1))
    assert "contract_sha256" not in json.loads(exe.canonical_contract_bytes(b1))


def test_report_deterministic_and_no_admission():
    r1 = rpt.build_report()
    r2 = rpt.build_report()
    assert rpt.canonical_report_bytes(r1) == rpt.canonical_report_bytes(r2)
    md1 = rpt.render_markdown(r1); md2 = rpt.render_markdown(r2)
    assert md1 == md2
    # nothing admitted / selected / approved
    assert r1["no_data_admitted"] and r1["no_instrument_selected"]
    assert r1["no_cost_base_case_approved"] and r1["no_replay_or_simulation"]
    inv = r1["local_forward_inventory"]
    assert all(s["admitted"] is False for s in inv["present_post_cutoff_snapshots"])
    # post-cutoff snapshots present but only candidates, never admitted
    assert inv["present_valid_exit_only_candidate_dates"] == \
        ["2026-07-16", "2026-07-17", "2026-07-20"]
    # forward coverage over the 30-day horizon is incomplete -> blocked
    assert inv["coverage_verdict"] == "BLOCKED_BY_INSUFFICIENT_FORWARD_EXIT_PATH_DATA"
