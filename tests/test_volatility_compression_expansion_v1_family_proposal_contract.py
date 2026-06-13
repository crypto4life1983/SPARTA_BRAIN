"""Tests for the Candidate #7 family proposal
(VOLATILITY_COMPRESSION_EXPANSION_V1).

Covers all 14 commanded requirements: proposal passes; chain gates
live (six-record ledger + V2 + Recommendation V1 + Autopilot V1);
blocks if any C1-C6 status drifts; refuses each rejected-family
reuse (C1-C6); enforces 27 bps fee assumption and 81 bps floor;
proves the proposal-only boundary (zero spec/detector/labels/replay
/fetch/data/runner/scheduler/paper/live/trading capability); proves
no profit/paper/live/winner wording; AST/purity green. Commander
safety suite runs alongside (12 tests)."""

from __future__ import annotations

import ast

import sparta_commander.strategy_factory_autopilot_research_loop_v1_contract as ap
import sparta_commander.strategy_factory_candidate_recommendation_v1_contract as rec
import sparta_commander.strategy_factory_overnight_research_autopilot_v2_contract as oap2
import sparta_commander.volatility_compression_expansion_v1_family_proposal_contract as c7p


def _record():
    return c7p.build_candidate_7_family_proposal()


# (1) Candidate #7 proposal passes -------------------------------------------

def test_1_candidate_7_proposal_certifies_ready():
    record = _record()
    assert record["verdict"] == c7p.VERDICT_C7P_READY
    assert record["blockers"] == []
    assert c7p.validate_candidate_7_family_proposal(
        record)["valid"] is True
    # determinism
    assert _record() == record
    # selected candidate identity
    assert record["candidate_id"] == "VOLATILITY_COMPRESSION_EXPANSION_V1"
    assert record["candidate_family"] == (
        "volatility_compression_expansion")
    assert record["symbols"] == ["BTCUSD"]
    assert record["timeframe"] == "4h"
    assert record["direction"] == "long_only"
    assert record["is_proposal_only"] is True
    assert record["is_a_rescue_attempt"] is False


# (2) Chain gates live: six-record ledger + V2 + Recommendation V1 +
#     Autopilot V1 ----------------------------------------------------------

def test_2_chain_gates_live():
    record = _record()
    assert record["ledger_status_six_records"] == [
        "REJECTED_KEPT_ON_RECORD"] * 6
    assert record["ledger_all_rejected_kept_on_record"] is True
    assert record["v2_verdict"] == oap2.VERDICT_OAP2_READY
    assert record["recommendation_verdict"] == rec.VERDICT_CR_READY
    assert record["autopilot_loop_verdict"] == ap.VERDICT_AP_READY
    assert record["loop_proposal_check"]["acceptable"] is True
    assert record["hypothesis_language_check"]["acceptable"] is True
    assert record["recommendation_hard_rules_check"]["acceptable"] is (
        True)


# (3) Blocks if any C1-C6 rejection record is missing or not
#     REJECTED_KEPT_ON_RECORD --------------------------------------------

def test_3_blocks_if_any_c1_to_c6_status_drifts():
    import sparta_commander.volatility_compression_expansion_v1_family_proposal_contract as mod
    originals = {key: getattr(mod, key) for key in
                 ("C1_STATUS", "C2_STATUS", "C3_STATUS", "C4_STATUS",
                  "C5_STATUS", "C6_STATUS")}
    try:
        for key in originals:
            for replacement in ("APPROVED_FOR_TRADING", "PENDING", ""):
                setattr(mod, key, replacement)
                record = mod.build_candidate_7_family_proposal()
                assert record["verdict"] == c7p.VERDICT_C7P_BLOCKED, (
                    key, replacement)
                assert "six_record_ledger_broken" in record[
                    "blockers"], (key, replacement)
                assert record[
                    "ledger_all_rejected_kept_on_record"] is False
            setattr(mod, key, originals[key])
    finally:
        for key, value in originals.items():
            setattr(mod, key, value)
    # baseline restored
    assert mod.build_candidate_7_family_proposal()["verdict"] == (
        c7p.VERDICT_C7P_READY)


# (4) Rejects reuse of Candidate #6 RS rotation logic ----------------------

def test_4_rejects_reuse_of_c6_rs_rotation_family():
    # C6 family name is in V2's blacklist; if the C7 family ever
    # equaled it, the validator would flag it
    assert "multi_symbol_relative_strength_rotation_filter" in (
        oap2.REJECTED_FAMILY_LOGIC_BLACKLIST)
    # the C7 family name is materially different
    assert c7p.CANDIDATE_FAMILY != (
        "multi_symbol_relative_strength_rotation_filter")
    # synthesize the bad scenario: tamper the record to claim the C6
    # family and prove the validator rejects
    bad = _record()
    bad["candidate_family"] = (
        "multi_symbol_relative_strength_rotation_filter")
    assert c7p.validate_candidate_7_family_proposal(
        bad)["valid"] is False
    # also assert the family is in the all_known_rejected_families
    # tuple (a deterministic union of the three pushed blacklists)
    assert "multi_symbol_relative_strength_rotation_filter" in (
        _record()["all_known_rejected_families"])


# (5) Rejects reuse of Candidate #5 RS pullback continuation logic ------

def test_5_rejects_reuse_of_c5_rs_pullback_continuation_family():
    # REC V1 uses base name; V2 uses module-style _v1 variant
    assert "eth_sol_relative_strength_pullback_continuation" in (
        rec.ALL_REJECTED_FAMILIES)
    assert "eth_sol_relative_strength_pullback_continuation_v1" in (
        oap2.REJECTED_FAMILY_LOGIC_BLACKLIST)
    assert c7p.CANDIDATE_FAMILY != (
        "eth_sol_relative_strength_pullback_continuation")
    assert c7p.CANDIDATE_FAMILY != (
        "eth_sol_relative_strength_pullback_continuation_v1")
    for bad_name in (
            "eth_sol_relative_strength_pullback_continuation",
            "eth_sol_relative_strength_pullback_continuation_v1"):
        bad = _record()
        bad["candidate_family"] = bad_name
        assert c7p.validate_candidate_7_family_proposal(
            bad)["valid"] is False, bad_name


# (6) Rejects reuse of Candidate #1 FVG/CHoCH logic ---------------------

def test_6_rejects_reuse_of_c1_fvg_choch_family():
    assert "ny_session_fvg_choch" in ap.REJECTED_FAMILIES
    assert "ny_session_fvg_choch" in rec.ALL_REJECTED_FAMILIES
    assert "ny_session_fvg_choch_v3" in (
        oap2.REJECTED_FAMILY_LOGIC_BLACKLIST)
    assert c7p.CANDIDATE_FAMILY != "ny_session_fvg_choch"
    bad = _record()
    bad["candidate_family"] = "ny_session_fvg_choch"
    assert c7p.validate_candidate_7_family_proposal(
        bad)["valid"] is False


# (7) Rejects reuse of Candidate #2 breakout-pullback structure logic ---

def test_7_rejects_reuse_of_c2_breakout_pullback_structure_family():
    assert "crypto_intraday_breakout_pullback_structure" in (
        ap.REJECTED_FAMILIES)
    assert "crypto_intraday_breakout_pullback_structure" in (
        rec.ALL_REJECTED_FAMILIES)
    assert "crypto_intraday_breakout_pullback_structure_v2" in (
        oap2.REJECTED_FAMILY_LOGIC_BLACKLIST)
    assert c7p.CANDIDATE_FAMILY != (
        "crypto_intraday_breakout_pullback_structure")
    bad = _record()
    bad["candidate_family"] = (
        "crypto_intraday_breakout_pullback_structure")
    assert c7p.validate_candidate_7_family_proposal(
        bad)["valid"] is False


# (8) Rejects reuse of Candidate #3 BTC/SOL trend continuation logic ----

def test_8_rejects_reuse_of_c3_btc_sol_trend_continuation_family():
    assert "long_biased_trend_continuation" in ap.REJECTED_FAMILIES
    assert "long_biased_trend_continuation" in (
        rec.ALL_REJECTED_FAMILIES)
    assert "btc_sol_long_trend_continuation_v1" in (
        oap2.REJECTED_FAMILY_LOGIC_BLACKLIST)
    assert c7p.CANDIDATE_FAMILY != "long_biased_trend_continuation"
    bad = _record()
    bad["candidate_family"] = "long_biased_trend_continuation"
    assert c7p.validate_candidate_7_family_proposal(
        bad)["valid"] is False


# (9) Rejects reuse of Candidate #4 SOL/BTC 1h swing structure logic ----

def test_9_rejects_reuse_of_c4_swing_structure_family():
    assert "long_1h_swing_structure" in ap.REJECTED_FAMILIES
    assert "long_1h_swing_structure" in rec.ALL_REJECTED_FAMILIES
    assert "sol_btc_long_1h_swing_structure" in (
        oap2.REJECTED_FAMILY_LOGIC_BLACKLIST)
    assert c7p.CANDIDATE_FAMILY != "long_1h_swing_structure"
    bad = _record()
    bad["candidate_family"] = "long_1h_swing_structure"
    assert c7p.validate_candidate_7_family_proposal(
        bad)["valid"] is False


# (10) 27 bps fee assumption enforced -----------------------------------

def test_10_fee_27_bps_assumption_enforced():
    record = _record()
    fee = record["fee_aware_geometry_policy"]
    assert fee["fee_model_round_trip_bps"] == 27
    assert fee["no_maker_rebate_assumption"] is True
    assert fee["no_zero_fee_assumption"] is True
    for value in (0, 5, 13, 20, 26, 28, 50, 100):
        bad = _record()
        bad["fee_aware_geometry_policy"] = dict(
            bad["fee_aware_geometry_policy"],
            fee_model_round_trip_bps=value)
        assert c7p.validate_candidate_7_family_proposal(
            bad)["valid"] is False, value
    for assumption in ("no_maker_rebate_assumption",
                       "no_zero_fee_assumption"):
        bad = _record()
        bad["fee_aware_geometry_policy"] = dict(
            bad["fee_aware_geometry_policy"], **{assumption: False})
        assert c7p.validate_candidate_7_family_proposal(
            bad)["valid"] is False, assumption


# (11) 81 bps floor enforced -------------------------------------------

def test_11_floor_81_bps_enforced():
    record = _record()
    fee = record["fee_aware_geometry_policy"]
    assert fee["minimum_gross_target_distance_floor_bps"] == 81
    assert fee["floor_is_3x_round_trip_fees"] is True
    for value in (0, 27, 54, 80, 82, 100, 162):
        bad = _record()
        bad["fee_aware_geometry_policy"] = dict(
            bad["fee_aware_geometry_policy"],
            minimum_gross_target_distance_floor_bps=value)
        assert c7p.validate_candidate_7_family_proposal(
            bad)["valid"] is False, value


# (12) Proposal-only boundary: no spec/detector/labels/replay/fetch/data
#      /runner/scheduler/paper/live/trading capability ------------------

def test_12_proposal_only_no_downstream_capability():
    record = _record()
    for key in ("runs_spec_review_now",
                "runs_detector",
                "runs_real_candle_detection",
                "runs_relabel", "runs_replay", "labels_now",
                "runs_real_detection_now", "runs_replay_now",
                "scores_now", "stages_data_now",
                "fetches_data", "calls_api", "uses_network",
                "uses_credentials", "uses_wallet", "uses_account",
                "connects_broker", "connects_exchange",
                "uses_real_money",
                "contains_order_logic",
                "contains_portfolio_allocation_logic",
                "starts_scheduler", "sends_notifications",
                "auto_commits", "auto_pushes",
                "creates_runners_now", "creates_data_artifacts_now",
                "creates_detector_label_replay_files_now",
                "creates_detector_implementation_now",
                "modifies_staged_market_data",
                "authorizes_paper_execution",
                "authorizes_micro_live",
                "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate",
                "claims_profitability",
                "executes", "writes_files"):
        assert record[key] is False, key
        # flipping any of these to True invalidates
        tampered = _record()
        tampered[key] = True
        assert c7p.validate_candidate_7_family_proposal(
            tampered)["valid"] is False, key
    assert record["paper_trading_gate_locked"] is True
    assert record["micro_live_gate_locked"] is True
    assert record["live_gate_locked"] is True
    assert record["is_proposal_only"] is True
    assert record["next_loop_stage"] == "candidate_spec"


# (13) No profitability/paper/live/winner wording -----------------------

def test_13_no_profitability_paper_live_or_winner_wording():
    record = _record()
    assert record["authorizes_paper_execution"] is False
    assert record["authorizes_live_trading"] is False
    assert record["claims_profitability"] is False
    # the hypothesis text passes the pushed evidence-language screener
    assert record["hypothesis_language_check"]["acceptable"] is True
    assert record["hypothesis_language_check"]["violations"] == []
    # all forbidden tokens absent from hypothesis (lower-cased check)
    text = (c7p.CLEAN_HYPOTHESIS + " "
            + c7p.DIFFERENCE_FROM_REJECTED_FAMILIES).lower()
    for token in ("winner", "winning strategy", "profitable",
                  "profitability proven", "edge confirmed",
                  "guaranteed", "can't lose", "holy grail",
                  "ready for live", "ready for paper"):
        assert token not in text, token
    safety = record["safety_and_no_claim"]
    for fact in ("no trading, no paper trading, no live trading",
                 "no wallet, account, api, or order capability",
                 "no auto-push, no auto-commit",
                 "no scheduler activation",
                 "no profitability claim and no winner wording at any "
                 "stage"):
        assert fact in safety, fact
    # the label must include READ-ONLY / NOT A RESCUE / NOT A CLAIM
    label = c7p.C7P_LABEL
    assert "READ-ONLY" in label
    assert "NOT A RESCUE" in label
    assert "NOT A CLAIM" in label
    for banned_phrase in ("WINNER", "PROFITABLE", "EDGE CONFIRMED",
                          "APPROVED FOR PAPER", "APPROVED FOR LIVE"):
        assert banned_phrase not in label.upper(), banned_phrase


# (14) AST/purity --------------------------------------------------------

def test_14_ast_purity_and_no_writers_or_runners():
    assert c7p.get_candidate_7_proposal_label() == c7p.C7P_LABEL
    assert c7p.C7P_MODE == "RESEARCH_ONLY"
    assert c7p.VERDICT_C7P_READY == "CANDIDATE_7_FAMILY_PROPOSAL_READY"
    assert c7p.NEXT_REQUIRED_ACTION == (
        "HUMAN_APPROVED_CANDIDATE_7_SPEC_REVIEW")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in c7p.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(c7p.__file__, encoding="utf-8").read()
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
