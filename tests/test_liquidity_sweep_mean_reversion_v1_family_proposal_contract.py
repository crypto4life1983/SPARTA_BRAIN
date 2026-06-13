"""Tests for the Candidate #8 family proposal
(LIQUIDITY_SWEEP_MEAN_REVERSION_V1).

Verifies: proposal certifies READY; chain gates live (seven-record
ledger + V3 blacklist + V2 + Recommendation V1 + Autopilot V1);
blocks if any C1-C7 status drifts; family is NOT in the V3 blacklist;
universe BTCUSD only, 15m, long_only; 27 bps fee + 81 bps floor;
built-in anti-cluster (C6 lesson) and built-in sample-size adequacy
(C7 lesson); proposal-only no-downstream-capability; rejects reuse of
each of the seven rejected families; AST/purity green. Commander
safety suite runs alongside (12 tests)."""

from __future__ import annotations

import ast

import sparta_commander.liquidity_sweep_mean_reversion_v1_family_proposal_contract as c8p
import sparta_commander.strategy_factory_autopilot_research_loop_v1_contract as ap
import sparta_commander.strategy_factory_candidate_recommendation_v1_contract as rec
import sparta_commander.strategy_factory_overnight_research_autopilot_v2_contract as oap2
import sparta_commander.strategy_factory_rejected_family_blacklist_v3_contract as bl3


def _record():
    return c8p.build_candidate_8_family_proposal()


# (1) C8 proposal certifies READY end-to-end ---------------------------------

def test_1_candidate_8_proposal_certifies_ready():
    record = _record()
    assert record["verdict"] == c8p.VERDICT_C8P_READY
    assert record["blockers"] == []
    assert c8p.validate_candidate_8_family_proposal(
        record)["valid"] is True
    assert _record() == record  # determinism
    assert record["candidate_id"] == "LIQUIDITY_SWEEP_MEAN_REVERSION_V1"
    assert record["candidate_family"] == "liquidity_sweep_mean_reversion"
    assert record["symbols"] == ["BTCUSD"]
    assert record["timeframe"] == "15m"
    assert record["direction"] == "long_only"
    assert record["is_proposal_only"] is True
    assert record["is_a_rescue_attempt"] is False


# (2) chain gates live: 7-record ledger + V3 + V2 + Rec V1 + Autopilot V1 ---

def test_2_chain_gates_live():
    record = _record()
    assert record["ledger_status_seven_records"] == [
        "REJECTED_KEPT_ON_RECORD"] * 7
    assert record["ledger_all_rejected_kept_on_record"] is True
    assert record["v3_blacklist_verdict"] == bl3.VERDICT_BL3_READY
    assert record["v2_verdict"] == oap2.VERDICT_OAP2_READY
    assert record["recommendation_verdict"] == rec.VERDICT_CR_READY
    assert record["autopilot_loop_verdict"] == ap.VERDICT_AP_READY
    assert record["loop_proposal_check"]["acceptable"] is True
    assert record["hypothesis_language_check"]["acceptable"] is True
    assert record["recommendation_hard_rules_check"][
        "acceptable"] is True


# (3) blocks if any C1-C7 status drifts -------------------------------------

def test_3_blocks_if_any_c1_to_c7_status_drifts():
    import sparta_commander.liquidity_sweep_mean_reversion_v1_family_proposal_contract as mod
    originals = {key: getattr(mod, key) for key in
                 ("C1_STATUS", "C2_STATUS", "C3_STATUS", "C4_STATUS",
                  "C5_STATUS", "C6_STATUS", "C7_STATUS")}
    try:
        for key in originals:
            setattr(mod, key, "APPROVED_FOR_TRADING")
            record = mod.build_candidate_8_family_proposal()
            assert record["verdict"] == c8p.VERDICT_C8P_BLOCKED, key
            assert "seven_record_ledger_broken" in record[
                "blockers"], key
            setattr(mod, key, originals[key])
    finally:
        for key, value in originals.items():
            setattr(mod, key, value)
    assert mod.build_candidate_8_family_proposal()["verdict"] == (
        c8p.VERDICT_C8P_READY)


# (4) candidate #8 is NOT in the V3 blacklist -------------------------------

def test_4_candidate_8_family_not_in_v3_blacklist():
    assert c8p.CANDIDATE_FAMILY not in bl3.REJECTED_FAMILY_LOGIC_BLACKLIST_V3
    assert c8p.CANDIDATE_FAMILY not in (
        oap2.REJECTED_FAMILY_LOGIC_BLACKLIST)
    assert c8p.CANDIDATE_FAMILY not in rec.ALL_REJECTED_FAMILIES
    assert c8p.CANDIDATE_FAMILY not in ap.REJECTED_FAMILIES
    # the proposal record exposes a union of all known rejected
    # families; C8 must not equal any of them
    record = _record()
    for fam in record["all_known_rejected_families"]:
        assert fam != c8p.CANDIDATE_FAMILY


# (5)-(11) rejects reuse of each rejected family (C1-C7) -------------------

def test_5_rejects_reuse_of_c1_fvg_choch_family():
    assert "ny_session_fvg_choch_v3" in (
        bl3.REJECTED_FAMILY_LOGIC_BLACKLIST_V3)
    bad = _record()
    bad["candidate_family"] = "ny_session_fvg_choch_v3"
    assert c8p.validate_candidate_8_family_proposal(
        bad)["valid"] is False


def test_6_rejects_reuse_of_c2_breakout_pullback_family():
    assert "crypto_intraday_breakout_pullback_structure_v2" in (
        bl3.REJECTED_FAMILY_LOGIC_BLACKLIST_V3)
    bad = _record()
    bad["candidate_family"] = (
        "crypto_intraday_breakout_pullback_structure_v2")
    assert c8p.validate_candidate_8_family_proposal(
        bad)["valid"] is False


def test_7_rejects_reuse_of_c3_trend_continuation_family():
    assert "btc_sol_long_trend_continuation_v1" in (
        bl3.REJECTED_FAMILY_LOGIC_BLACKLIST_V3)
    bad = _record()
    bad["candidate_family"] = "btc_sol_long_trend_continuation_v1"
    assert c8p.validate_candidate_8_family_proposal(
        bad)["valid"] is False


def test_8_rejects_reuse_of_c4_swing_structure_family():
    assert "sol_btc_long_1h_swing_structure" in (
        bl3.REJECTED_FAMILY_LOGIC_BLACKLIST_V3)
    bad = _record()
    bad["candidate_family"] = "sol_btc_long_1h_swing_structure"
    assert c8p.validate_candidate_8_family_proposal(
        bad)["valid"] is False


def test_9_rejects_reuse_of_c5_rs_pullback_family():
    assert ("eth_sol_relative_strength_pullback_continuation_v1"
            in bl3.REJECTED_FAMILY_LOGIC_BLACKLIST_V3)
    bad = _record()
    bad["candidate_family"] = (
        "eth_sol_relative_strength_pullback_continuation_v1")
    assert c8p.validate_candidate_8_family_proposal(
        bad)["valid"] is False


def test_10_rejects_reuse_of_c6_rs_rotation_family():
    assert "multi_symbol_relative_strength_rotation_filter" in (
        bl3.REJECTED_FAMILY_LOGIC_BLACKLIST_V3)
    bad = _record()
    bad["candidate_family"] = (
        "multi_symbol_relative_strength_rotation_filter")
    assert c8p.validate_candidate_8_family_proposal(
        bad)["valid"] is False


def test_11_rejects_reuse_of_c7_volatility_compression_family():
    assert "volatility_compression_expansion" in (
        bl3.REJECTED_FAMILY_LOGIC_BLACKLIST_V3)
    bad = _record()
    bad["candidate_family"] = "volatility_compression_expansion"
    assert c8p.validate_candidate_8_family_proposal(
        bad)["valid"] is False


# (12) 27 bps fee + 81 bps floor enforced -----------------------------------

def test_12_fee_27_and_floor_81_enforced():
    record = _record()
    fee = record["fee_aware_geometry_policy"]
    assert fee["fee_model_round_trip_bps"] == 27
    assert fee["minimum_gross_target_distance_floor_bps"] == 81
    assert fee["no_maker_rebate_assumption"] is True
    assert fee["no_zero_fee_assumption"] is True
    for value in (0, 5, 13, 26, 28, 100):
        bad = _record()
        bad["fee_aware_geometry_policy"] = dict(
            bad["fee_aware_geometry_policy"],
            fee_model_round_trip_bps=value)
        assert c8p.validate_candidate_8_family_proposal(
            bad)["valid"] is False, value
    for value in (0, 27, 80, 82, 162):
        bad = _record()
        bad["fee_aware_geometry_policy"] = dict(
            bad["fee_aware_geometry_policy"],
            minimum_gross_target_distance_floor_bps=value)
        assert c8p.validate_candidate_8_family_proposal(
            bad)["valid"] is False, value


# (13) C6 lesson built in: anti-cluster at proposal time -------------------

def test_13_anti_cluster_built_in_at_proposal_time():
    record = _record()
    anti = record["anti_cluster_policy"]
    assert anti["built_in_at_label_emission_time"] is True
    assert anti["scope"] == (
        "per_symbol_minimum_bar_gap_between_accepted_events")
    assert anti["applies_before_replay_time_non_overlap"] is True
    assert anti["replay_time_non_overlap_unchanged"] is True
    assert anti["is_not_the_single_allowed_c8_edit"] is True
    assert "c6" in anti["reason_for_built_in"].lower()
    bad = _record()
    bad["anti_cluster_policy"] = dict(
        bad["anti_cluster_policy"],
        is_not_the_single_allowed_c8_edit=False)
    assert c8p.validate_candidate_8_family_proposal(
        bad)["valid"] is False


# (14) C7 lesson built in: sample-size adequacy at proposal time -----------

def test_14_sample_size_adequacy_built_in_at_proposal_time():
    record = _record()
    sa = record["sample_size_adequacy_policy"]
    assert sa["built_in_at_proposal_time"] is True
    assert sa[
        "minimum_accepted_setup_count_threshold_frozen_at_spec_review"
    ] is True
    assert sa["applies_at_labels_review_gate"] is True
    assert sa[
        "below_threshold_triggers_structural_rejection_without_edit_token"
    ] is True
    assert "c7" in sa["reason_for_built_in"].lower()
    assert sa["is_not_the_single_allowed_c8_edit"] is True
    bad = _record()
    bad["sample_size_adequacy_policy"] = dict(
        bad["sample_size_adequacy_policy"],
        below_threshold_triggers_structural_rejection_without_edit_token=
        False)
    assert c8p.validate_candidate_8_family_proposal(
        bad)["valid"] is False


# (15) proposal-only boundary: zero downstream capability ------------------

def test_15_proposal_only_no_downstream_capability():
    record = _record()
    for key in ("runs_spec_review_now",
                "runs_detector", "runs_real_candle_detection",
                "runs_relabel", "runs_replay", "labels_now",
                "runs_real_detection_now", "runs_replay_now",
                "scores_now", "stages_data_now",
                "fetches_data", "calls_api", "uses_network",
                "uses_credentials", "uses_wallet", "uses_account",
                "connects_broker", "connects_exchange",
                "uses_real_money", "contains_order_logic",
                "contains_portfolio_allocation_logic",
                "starts_scheduler", "sends_notifications",
                "auto_commits", "auto_pushes",
                "creates_runners_now", "creates_data_artifacts_now",
                "creates_detector_label_replay_files_now",
                "creates_detector_implementation_now",
                "computes_pnl_now",
                "modifies_staged_market_data",
                "authorizes_paper_execution",
                "authorizes_micro_live",
                "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate",
                "claims_profitability",
                "executes", "writes_files"):
        assert record[key] is False, key
        tampered = _record()
        tampered[key] = True
        assert c8p.validate_candidate_8_family_proposal(
            tampered)["valid"] is False, key
    assert record["paper_trading_gate_locked"] is True
    assert record["micro_live_gate_locked"] is True
    assert record["live_gate_locked"] is True
    assert record["is_proposal_only"] is True
    assert record["next_loop_stage"] == "candidate_spec"


# (16) no profitability/paper/live/winner wording ------------------------

def test_16_no_profitability_paper_live_or_winner_wording():
    record = _record()
    assert record["claims_profitability"] is False
    assert record["authorizes_paper_execution"] is False
    assert record["authorizes_live_trading"] is False
    assert record["hypothesis_language_check"]["acceptable"] is True
    assert record["hypothesis_language_check"]["violations"] == []
    text = (c8p.CLEAN_HYPOTHESIS + " "
            + c8p.DIFFERENCE_FROM_REJECTED_FAMILIES).lower()
    for token in ("winner", "winning strategy", "profitable",
                  "profitability proven", "edge confirmed",
                  "guaranteed", "can't lose", "holy grail",
                  "ready for live", "ready for paper"):
        assert token not in text, token
    label = c8p.C8P_LABEL
    assert "READ-ONLY" in label
    assert "NOT A RESCUE" in label
    assert "NOT A CLAIM" in label
    for banned_phrase in ("WINNER", "PROFITABLE", "EDGE CONFIRMED",
                          "APPROVED FOR PAPER", "APPROVED FOR LIVE"):
        assert banned_phrase not in label.upper(), banned_phrase
    safety = record["safety_and_no_claim"]
    for fact in ("no trading, no paper trading, no live trading",
                 "no wallet, account, api, or order capability",
                 "no auto-push, no auto-commit",
                 "no scheduler activation",
                 "no profitability claim and no winner wording at "
                 "any stage"):
        assert fact in safety, fact


# (17) AST/purity --------------------------------------------------------

def test_17_ast_purity_and_no_writers_or_runners():
    assert c8p.get_candidate_8_proposal_label() == c8p.C8P_LABEL
    assert c8p.C8P_MODE == "RESEARCH_ONLY"
    assert c8p.VERDICT_C8P_READY == "CANDIDATE_8_FAMILY_PROPOSAL_READY"
    assert c8p.NEXT_REQUIRED_ACTION == (
        "HUMAN_APPROVED_CANDIDATE_8_SPEC_REVIEW")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in c8p.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(c8p.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    assert "random" not in src
    assert "now(" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch(", "subprocess", "Popen", "system("):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned_mods = {"urllib", "requests", "socket", "http", "ccxt",
                   "smtplib", "subprocess", "websockets", "aiohttp",
                   "schedule", "apscheduler", "threading", "asyncio",
                   "time", "sched", "telegram", "email", "csv", "pandas",
                   "pathlib", "os", "io", "json", "shutil", "databento",
                   "ssl", "ftplib", "datetime", "hashlib", "statistics",
                   "random"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods)
    assert not any(
        call.func.attr == "open" if isinstance(call.func, ast.Attribute)
        else getattr(call.func, "id", "") == "open"
        for call in ast.walk(tree) if isinstance(call, ast.Call))
