"""Tests for the Candidate #8 dry-run review / evidence-freeze
contract (LIQUIDITY_SWEEP_MEAN_REVERSION_V1).

Verifies: chain-gate on the seven-record ledger + C8 family proposal
+ C8 spec review + C8 detector spec+dry-run + V3 blacklist + V2 +
Recommendation V1 + Autopilot V1; the live recomputation matches
every frozen fact (10 fixture summaries, the single accepted setup's
exact geometry, strict-below sweep, strict-above reclaim, upper-third
2/3 confirmation, 4-bar reclaim window, BTCUSD/15m/long_only
enforcement, structure-stop formula 0.20 x ATR(14), 27/81 bps
fee/floor with boundary at 80 bps, 8-bar anti-cluster with boundary
at exactly +8, sample-size threshold 20 gate-only NOT edit token);
review-only / downstream gates locked; AST/purity green."""

from __future__ import annotations

import ast

import sparta_commander.liquidity_sweep_mean_reversion_v1_detector_dry_run_review_contract as c8r
import sparta_commander.liquidity_sweep_mean_reversion_v1_detector_spec_dry_run_contract as c8d
import sparta_commander.liquidity_sweep_mean_reversion_v1_family_proposal_contract as c8p
import sparta_commander.liquidity_sweep_mean_reversion_v1_spec_review_contract as c8s
import sparta_commander.strategy_factory_autopilot_research_loop_v1_contract as ap
import sparta_commander.strategy_factory_candidate_recommendation_v1_contract as rec
import sparta_commander.strategy_factory_overnight_research_autopilot_v2_contract as oap2
import sparta_commander.strategy_factory_rejected_family_blacklist_v3_contract as bl3


def _record():
    return c8r.build_candidate_8_dry_run_review()


# ---- chain gate + frozen verdict -------------------------------------------

def test_review_frozen_and_chain_gates_all_certify():
    assert c8p.build_candidate_8_family_proposal()["verdict"] == (
        c8p.VERDICT_C8P_READY)
    assert c8s.build_candidate_8_spec_review()["verdict"] == (
        c8s.VERDICT_C8S_READY)
    assert c8d.build_candidate_8_detector_spec_contract()[
        "verdict"] == c8d.VERDICT_C8D_READY
    assert c8d.run_c8_detector_dry_run()["verdict"] == (
        c8d.VERDICT_C8D_DRY_RUN_PASSED)
    assert bl3.build_rejected_family_blacklist_v3()["verdict"] == (
        bl3.VERDICT_BL3_READY)
    assert oap2.build_overnight_research_autopilot_v2_contract()[
        "verdict"] == oap2.VERDICT_OAP2_READY
    assert rec.build_candidate_recommendation()["verdict"] == (
        rec.VERDICT_CR_READY)
    assert ap.build_autopilot_loop_contract()["verdict"] == (
        ap.VERDICT_AP_READY)
    record = _record()
    assert record["verdict"] == c8r.VERDICT_C8R_FROZEN
    assert record["blockers"] == []
    assert record["failures"] == []
    assert c8r.validate_candidate_8_dry_run_review(
        record)["valid"] is True
    assert _record() == record  # determinism


def test_seven_record_ledger_intact():
    from sparta_commander.btc_sol_long_trend_continuation_v1_result_and_rejection_record_contract import (  # noqa: E501
        REJECTION_STATUS as C3)
    from sparta_commander.crypto_intraday_breakout_pullback_structure_v2_result_and_rejection_record_contract import (  # noqa: E501
        REJECTION_STATUS as C2)
    from sparta_commander.eth_sol_relative_strength_rejection_record_contract import (  # noqa: E501
        REJECTION_STATUS as C5)
    from sparta_commander.multi_symbol_relative_strength_rotation_filter_rejection_record_contract import (  # noqa: E501
        REJECTION_STATUS as C6)
    from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (  # noqa: E501
        REJECTION_STATUS as C1)
    from sparta_commander.sol_btc_long_1h_swing_structure_rejection_record_contract import (  # noqa: E501
        REJECTION_STATUS as C4)
    from sparta_commander.volatility_compression_expansion_v1_rejection_record import (  # noqa: E501
        REJECTION_STATUS as C7)
    assert C1 == C2 == C3 == C4 == C5 == C6 == C7 == (
        "REJECTED_KEPT_ON_RECORD")


def test_chain_blocks_when_ledger_breaks():
    import sparta_commander.liquidity_sweep_mean_reversion_v1_detector_dry_run_review_contract as mod
    originals = {k: getattr(mod, k) for k in
                 ("C1_STATUS", "C2_STATUS", "C3_STATUS",
                  "C4_STATUS", "C5_STATUS", "C6_STATUS",
                  "C7_STATUS")}
    try:
        for key in originals:
            setattr(mod, key, "APPROVED_FOR_TRADING")
            record = mod.build_candidate_8_dry_run_review()
            assert record["verdict"] == c8r.VERDICT_C8R_BLOCKED, key
            assert "seven_record_ledger_broken" in (
                record["blockers"]), key
            setattr(mod, key, originals[key])
    finally:
        for k, v in originals.items():
            setattr(mod, k, v)
    assert mod.build_candidate_8_dry_run_review()["verdict"] == (
        c8r.VERDICT_C8R_FROZEN)


# ---- expected upstream verdicts (frozen) -----------------------------------

def test_expected_upstream_verdicts_frozen():
    record = _record()
    assert record["expected_detector_verdict"] == (
        "CANDIDATE_8_DETECTOR_SPEC_READY")
    assert record["expected_dry_run_verdict"] == (
        "CANDIDATE_8_DETECTOR_DRY_RUN_PASSED")
    assert record["expected_combined_verdict"] == (
        "CANDIDATE_8_DETECTOR_SPEC_DRY_RUN_READY")
    for field, bad in (
            ("expected_detector_verdict", "CANDIDATE_8_FOO"),
            ("expected_dry_run_verdict", "CANDIDATE_8_BAR"),
            ("expected_combined_verdict", "CANDIDATE_8_BAZ")):
        tampered = _record()
        tampered[field] = bad
        assert c8r.validate_candidate_8_dry_run_review(
            tampered)["valid"] is False, field


# ---- frozen per-fixture counts ---------------------------------------------

def test_expected_fixture_counts_match_pushed_dry_run():
    record = _record()
    counts = record["expected_fixture_counts"]
    for name in ("valid_sweep_and_reclaim", "insufficient_history",
                 "equality_at_sweep_threshold", "reclaim_too_late",
                 "reclaim_close_equals_reference",
                 "close_not_in_upper_third",
                 "geometry_floor_all_variants_fail", "anti_cluster",
                 "sample_size_adequacy", "context_enforcement"):
        assert name in counts, name
    assert counts["valid_sweep_and_reclaim"]["attempts"] == 1
    assert counts["valid_sweep_and_reclaim"]["accepted"] == 1
    assert counts["valid_sweep_and_reclaim"][
        "first_accepted_floor_pass"] == {
            "2r": True, "3r": True, "4r": True}
    assert counts["insufficient_history"]["attempts"] == 0
    assert counts["equality_at_sweep_threshold"]["attempts"] == 0
    assert counts["reclaim_too_late"]["attempts"] == 1
    assert counts["reclaim_too_late"][
        "rejected_no_qualifying_reclaim"] == 1
    assert counts["reclaim_close_equals_reference"][
        "rejection_reasons"] == [
            "no_bar_within_window_closed_strictly_above_swept"
            "_reference"]
    assert counts["close_not_in_upper_third"][
        "rejection_reasons"] == [
            "no_bar_within_window_closed_in_upper_third_of_its_range"]
    assert counts["geometry_floor_all_variants_fail"][
        "floor_pass_by_variant"] == {
            "2r": False, "3r": False, "4r": False}
    assert counts["anti_cluster"]["anti_cluster_min_bar_gap"] == 8
    assert counts["anti_cluster"][
        "anti_cluster_does_not_consume_edit_token"] is True
    assert counts["sample_size_adequacy"][
        "below_minimum_at_dry_run"] is True
    assert counts["sample_size_adequacy"][
        "at_threshold_below_flag"] is False
    assert counts["sample_size_adequacy"][
        "enforced_at_labels_review_gate_only"] is True
    assert counts["sample_size_adequacy"][
        "does_not_consume_edit_token"] is True
    assert counts["context_enforcement"] == {
        "symbol_eth": True, "timeframe_1h": True,
        "direction_short": True}


def test_tampering_with_fixture_counts_rejects():
    tampered = _record()
    tampered["expected_fixture_counts"] = {}
    assert c8r.validate_candidate_8_dry_run_review(
        tampered)["valid"] is False
    tampered = _record()
    tampered["expected_fixture_counts"][
        "valid_sweep_and_reclaim"]["accepted"] = 0
    assert c8r.validate_candidate_8_dry_run_review(
        tampered)["valid"] is False


# ---- frozen single accepted setup ------------------------------------------

def test_accepted_setup_frozen_with_exact_numerics():
    accepted = _record()["expected_accepted_setup"]
    assert accepted["symbol"] == "BTCUSD"
    assert accepted["timeframe"] == "15m"
    assert accepted["direction"] == "long_only"
    assert accepted["sweep_index"] == 100
    assert accepted["reclaim_index"] == 101
    assert accepted["event_index"] == 101
    assert accepted["entry_price"] == 50030.0
    assert accepted["sweep_low"] == 49600.0
    assert accepted["reference_low"] == 49975.0
    assert accepted["reclaim_close"] == 50030.0
    assert accepted["reclaim_close_strictly_above_reference"] is True
    assert accepted["close_in_upper_third_passes"] is True
    assert accepted["stop_below_entry"] is True
    assert accepted["stop_below_sweep_low"] is True
    assert accepted["status"] == "accepted_for_replay_review"
    assert accepted["geometry_floor_pass_by_variant"] == {
        "2r": True, "3r": True, "4r": True}
    assert accepted["accepted_for_labeling_by_variant"] == {
        "2r": True, "3r": True, "4r": True}


def test_tampering_with_accepted_setup_rejects():
    tampered = _record()
    tampered["expected_accepted_setup"] = {}
    assert c8r.validate_candidate_8_dry_run_review(
        tampered)["valid"] is False
    tampered = _record()
    tampered["expected_accepted_setup"]["entry_price"] = 99999.0
    assert c8r.validate_candidate_8_dry_run_review(
        tampered)["valid"] is False


# ---- frozen anti-cluster + sample-size facts ------------------------------

def test_expected_anti_cluster_facts():
    anti = _record()["expected_anti_cluster"]
    assert anti["anti_cluster_min_bar_gap"] == 8
    assert anti["tie_breaker"] == (
        "keep_the_earlier_event_drop_the_later_one")
    assert anti["anti_cluster_does_not_consume_edit_token"] is True
    assert anti["boundary_at_8_is_kept"] is True
    assert anti["gap_of_7_is_dropped"] is True
    assert "synthetic_c_outside" in anti["kept_ids_in_dry_run"]
    assert "synthetic_b_inside" in anti["dropped_ids_in_dry_run"]
    tampered = _record()
    tampered["expected_anti_cluster"]["anti_cluster_min_bar_gap"] = 6
    assert c8r.validate_candidate_8_dry_run_review(
        tampered)["valid"] is False
    tampered = _record()
    tampered["expected_anti_cluster"][
        "anti_cluster_does_not_consume_edit_token"] = False
    assert c8r.validate_candidate_8_dry_run_review(
        tampered)["valid"] is False


def test_expected_sample_size_facts():
    facts = _record()["expected_sample_size_facts"]
    assert facts["threshold_min_accepted_at_labels_review_gate"] == 20
    assert facts["count_3_is_below_threshold"] is True
    assert facts["count_20_is_not_below_threshold"] is True
    assert facts["enforced_at_labels_review_gate_only"] is True
    assert facts["does_not_consume_edit_token"] is True
    for value in (0, 5, 15, 19, 21, 50):
        tampered = _record()
        tampered["expected_sample_size_facts"][
            "threshold_min_accepted_at_labels_review_gate"] = value
        assert c8r.validate_candidate_8_dry_run_review(
            tampered)["valid"] is False, value
    tampered = _record()
    tampered["expected_sample_size_facts"][
        "does_not_consume_edit_token"] = False
    assert c8r.validate_candidate_8_dry_run_review(
        tampered)["valid"] is False


# ---- frozen behavioural facts ---------------------------------------------

def test_expected_insufficient_history_fact():
    fact = _record()["expected_insufficient_history_fact"]
    assert fact["min_evaluable_sweep_bar_index"] == 96
    assert fact["scanner_skips_below_lookback"] is True
    assert fact["warmup_50_attempts"] == 0
    assert fact["warmup_30_attempts"] == 0


def test_expected_strict_below_sweep_fact():
    fact = _record()["expected_strict_below_sweep_fact"]
    assert fact["rule"] == (
        "strict_low_below_reference_minus_0_25_x_atr")
    assert fact["equality_at_threshold_rejects"] is True


def test_expected_strict_above_reclaim_fact():
    fact = _record()["expected_strict_above_reclaim_fact"]
    assert fact["rule"] == (
        "reclaim_close_strictly_above_swept_reference")
    assert fact["close_equal_to_reference_rejects"] is True


def test_expected_upper_third_fact():
    fact = _record()["expected_upper_third_fact"]
    assert fact["rule"] == (
        "close_must_be_in_upper_third_of_own_range")
    assert abs(fact["upper_third_fraction"]
               - (2.0 / 3.0)) < 1e-12
    assert fact[
        "close_at_midpoint_or_below_two_thirds_rejects"] is True


def test_expected_reclaim_window_fact():
    fact = _record()["expected_reclaim_window_fact"]
    assert fact["window_bars"] == 4
    assert fact["reclaim_at_offset_5_rejects"] is True
    assert "first_qualifying_bar_within_4" in fact["rule"]


def test_expected_universe_enforcement():
    fact = _record()["expected_universe_enforcement"]
    assert fact["universe"] == ["BTCUSD"]
    assert fact["timeframe"] == "15m"
    assert fact["direction"] == "long_only"
    assert fact["non_btcusd_raises_valueerror"] is True
    assert fact["non_15m_raises_valueerror"] is True
    assert fact["non_long_only_raises_valueerror"] is True
    assert fact["non_list_bars_raises_valueerror"] is True


def test_expected_stop_facts_locked():
    facts = _record()["expected_stop_facts"]
    assert facts["structure_stop_buffer_atr_multiplier"] == 0.20
    assert facts["stop_distance_formula"] == (
        "entry_price - (sweep_low - "
        "STRUCTURE_STOP_BUFFER_ATR_MULTIPLIER * ATR14)")
    assert facts["stop_never_tightened_after_entry"] is True
    happy = facts[
        "happy_path_entry_50030_sweep_low_49600_atr_76_785714"]
    assert happy["stop_below_entry"] is True
    assert happy["stop_below_sweep_low"] is True
    assert happy["valid"] is True
    assert abs(happy["stop_buffer_price"] - 15.3571428) < 1e-5
    assert abs(happy["stop_price"] - 49584.6428572) < 1e-5


def test_expected_floor_facts_27_and_81_with_boundary():
    facts = _record()["expected_floor_facts"]
    assert facts["fee_round_trip_bps"] == 27.0
    assert facts["target_distance_floor_bps"] == 81.0
    assert facts[
        "tiny_stop_distance_50_at_entry_50000_all_variants_fail"
    ] == {"2r": False, "3r": False, "4r": False}
    assert facts[
        "stop_distance_250_at_entry_50000_all_variants_pass"
    ] == {"2r": True, "3r": True, "4r": True}
    assert facts[
        "stop_distance_200_at_entry_50000_boundary_2r_fails_others"
        "_pass"] == {"2r": False, "3r": True, "4r": True}


# ---- frozen findings + claim locks ----------------------------------------

def test_frozen_review_findings_complete():
    findings = _record()["frozen_review_findings"]
    joined = " || ".join(findings)
    assert "exactly one accepted setup" in joined
    assert "stop_distance 445.357143" in joined
    assert "96-bar lookback" in joined
    assert "strict below sweep threshold rejects equality" in joined
    assert "reclaim close strictly above swept reference rejects" \
        in joined
    assert "upper-third confirmation at 2/3" in joined
    assert "reclaim window of 4 completed 15m bars" in joined
    assert "btcusd-only universe" in joined
    assert "81 bps floor" in joined
    assert "anti-cluster gap of 8" in joined
    assert "proposal-level locked and does NOT consume the single c8" \
        in joined
    assert "sample-size adequacy threshold of 20" in joined
    assert "zero dry-run failures" in joined


def test_claim_locks_present():
    locks = _record()["claim_locks"]
    for required in (
            "no_real_candle_detection_authorized_by_this_gate",
            "no_labels_authorized_by_this_gate",
            "no_replay_authorized_by_this_gate",
            "no_relabel_authorized_by_this_gate",
            "no_paper_approval", "no_live_approval",
            "no_execution_approval", "no_winner_wording",
            "no_profitability_claim",
            "anti_cluster_gap_remains_proposal_level_locked",
            "sample_size_threshold_remains_proposal_level_locked"):
        assert required in locks, required
    tampered = _record()
    tampered["claim_locks"] = []
    assert c8r.validate_candidate_8_dry_run_review(
        tampered)["valid"] is False


# ---- review-only safety / capability flags --------------------------------

def test_review_only_with_all_downstream_gates_locked():
    record = _record()
    assert record["is_review_only"] is True
    assert record["current_loop_stage"] == (
        "detector_and_label_review")
    assert record["human_review_required"] is True
    assert record["paper_trading_gate_locked"] is True
    assert record["micro_live_gate_locked"] is True
    assert record["live_gate_locked"] is True
    for key in ("runs_real_candle_detection",
                "runs_real_detection_now", "labels_now",
                "runs_replay", "runs_replay_now", "runs_relabel",
                "scores_now", "stages_data_now",
                "fetches_data", "calls_api", "uses_network",
                "uses_credentials", "uses_wallet", "uses_account",
                "connects_broker", "connects_exchange",
                "uses_real_money", "contains_order_logic",
                "contains_portfolio_allocation_logic",
                "starts_scheduler", "sends_notifications",
                "auto_commits", "auto_pushes",
                "creates_runners_now", "creates_data_artifacts_now",
                "creates_detector_implementation_now",
                "computes_pnl_now",
                "modifies_staged_market_data",
                "authorizes_paper_execution",
                "authorizes_micro_live", "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate",
                "unlocks_real_candle_detection",
                "unlocks_detector_now",
                "unlocks_labels_now", "unlocks_replay_now",
                "unlocks_relabel_now", "claims_profitability",
                "executes", "writes_files"):
        assert record[key] is False, key
        tampered = _record()
        tampered[key] = True
        assert c8r.validate_candidate_8_dry_run_review(
            tampered)["valid"] is False, key


def test_label_next_required_action_and_label_text():
    record = _record()
    assert record["next_required_action"] == (
        "HUMAN_APPROVED_CANDIDATE_8_REAL_CANDLE_DETECTION")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH",
                   "EXECUTE", "EXECUTION", "BACKTEST", "BASELINE",
                   "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in c8r.NEXT_REQUIRED_ACTION.upper(), banned
    assert c8r.get_candidate_8_dry_run_review_label() == c8r.C8R_LABEL
    assert c8r.C8R_MODE == "RESEARCH_ONLY"
    for phrase in ("READ-ONLY", "RESEARCH ONLY",
                   "SYNTHETIC OUTCOMES ONLY",
                   "NOT A PROFITABILITY CLAIM",
                   "NOT A RESCUE"):
        assert phrase in c8r.C8R_LABEL, phrase
    for banned_phrase in ("WINNER", "PROFITABLE", "EDGE CONFIRMED",
                          "APPROVED FOR PAPER",
                          "APPROVED FOR LIVE"):
        assert banned_phrase not in c8r.C8R_LABEL.upper(), (
            banned_phrase)


# ---- module purity --------------------------------------------------------

def test_module_purity_no_banned_imports_no_io_no_main():
    src = open(c8r.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir",
                 "rmdir", "rename", "touch("):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned_mods = {"urllib", "requests", "socket", "http", "ccxt",
                   "smtplib", "subprocess", "websockets", "aiohttp",
                   "schedule", "apscheduler", "threading", "asyncio",
                   "time", "sched", "telegram", "email", "csv",
                   "pandas", "pathlib", "os", "io", "json", "shutil",
                   "databento", "ssl", "ftplib", "hashlib",
                   "statistics", "random"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods), imported & banned_mods
    for call in ast.walk(tree):
        if not isinstance(call, ast.Call):
            continue
        name = (call.func.attr if isinstance(call.func, ast.Attribute)
                else getattr(call.func, "id", ""))
        assert name not in ("open", "exec", "eval", "compile"), name
