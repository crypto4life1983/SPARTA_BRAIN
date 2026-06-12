"""Tests for the Candidate #4 dry-run review / evidence-freeze contract.

Proves: the review APPROVES by recomputing the pushed dry run live and
matching every frozen fact; tampering with any frozen block invalidates;
synthetic-only scope facts are frozen; capabilities are zero; the next
action is the real-candle detection HUMAN gate."""

from __future__ import annotations

import ast

import sparta_commander.sol_btc_long_1h_swing_structure_dry_run_review_contract as c4r


def test_review_approved_with_zero_mismatches():
    record = c4r.build_c4_dry_run_review()
    assert record["verdict"] == c4r.VERDICT_C4R_APPROVED
    assert record["blockers"] == []
    assert record["mismatches"] == []
    assert c4r.validate_c4_dry_run_review(record)["valid"] is True
    assert record["candidate_id"] == "SOL_BTC_LONG_1H_SWING_STRUCTURE_V1"
    assert c4r.build_c4_dry_run_review() == record  # determinism


def test_frozen_accepted_fixture_facts():
    exp = c4r.EXPECTED_ACCEPTED_FIXTURE
    assert exp["symbol"] == "SOLUSD"
    assert exp["total_labels"] == 1
    assert exp["accepted_labels"] == 1
    assert exp["sl1_low_price"] == 99.0
    assert exp["sl2_low_price"] == 99.8
    assert exp["sl2_low_price"] > exp["sl1_low_price"]
    assert exp["sl2_higher_than_sl1"] is True
    assert exp["inter_swing_high_price"] == 101.5
    assert exp["entry_price"] == 101.8
    assert exp["structural_stop_price"] == 99.8
    assert exp["stop_price"] == 99.8
    assert exp["stop_source"] == "structural_sl2_low"
    assert exp["stop_selected_because"] == (
        "structural_wider_than_1_5x_atr_stop")
    assert exp["risk_distance_bps"] == 196.463654
    assert exp["risk_distance_bps"] >= 81
    assert exp["risk_meets_81bps_floor"] is True
    assert (exp["target_2r_price"], exp["target_3r_price"],
            exp["target_4r_price"]) == (105.8, 107.8, 109.8)


def test_frozen_tight_and_downtrend_facts():
    tight = c4r.EXPECTED_TIGHT_FIXTURE
    assert tight["symbol"] == "BTCUSD"
    assert tight["accepted_labels"] == 0
    assert tight["cost_floor_rejections"] == 1
    assert tight["risk_distance_bps"] == 63.756744
    assert tight["risk_distance_bps"] < 81
    assert tight["risk_below_81bps_floor"] is True
    down = c4r.EXPECTED_DOWNTREND_FIXTURE
    assert down["accepted_labels"] == 0
    assert down["trend_rejections"] == 1


def test_frozen_anti_lookahead_facts():
    al = c4r.EXPECTED_ANTI_LOOKAHEAD
    assert al["gate_0359_completed_4h_bars"] == 12
    assert al["gate_0359_sufficient"] is False
    assert al["gate_0400_completed_4h_bars"] == 13
    assert al["gate_0400_sufficient"] is True
    assert al["swing_confirmation_lag_bars"] == 2
    assert al["swing_lows_full_series"] == (10, 16)
    assert al["swing_lows_truncated_before_confirmation"] == (10,)


def test_scope_facts_frozen_no_real_detection_no_replay():
    record = c4r.build_c4_dry_run_review()
    facts = record["frozen_scope_facts"]
    assert "synthetic in-memory fixtures only" in facts
    assert ("no real-candle detection has occurred for candidate #4"
            in facts)
    assert "no replay has occurred for candidate #4" in facts
    assert "nothing here is a profitability claim" in facts
    assert record["runs_real_detection_now"] is False
    assert record["runs_replay_now"] is False
    assert record["fetches_data"] is False
    tampered = c4r.build_c4_dry_run_review()
    tampered["frozen_scope_facts"] = tampered["frozen_scope_facts"][:2]
    assert c4r.validate_c4_dry_run_review(tampered)["valid"] is False


def test_tampering_frozen_facts_invalidates():
    for field, value in (
            ("expected_detector_verdict", "SOMETHING_ELSE"),
            ("expected_accepted_fixture", {"entry_price": 1.0}),
            ("expected_tight_fixture", {"risk_distance_bps": 80.9}),
            ("expected_downtrend_fixture", {"accepted_labels": 1}),
            ("expected_anti_lookahead", {}),
            ("cost_floor_bps", 54),
            ("candidate_id", "CANDIDATE_3_REVIVED")):
        tampered = c4r.build_c4_dry_run_review()
        tampered[field] = value
        assert c4r.validate_c4_dry_run_review(
            tampered)["valid"] is False, field
    approved_with_mismatch = c4r.build_c4_dry_run_review()
    approved_with_mismatch["mismatches"] = ["fake"]
    assert c4r.validate_c4_dry_run_review(
        approved_with_mismatch)["valid"] is False


def test_capabilities_locked():
    record = c4r.build_c4_dry_run_review()
    for key in ("executes", "writes_files", "runs_real_detection_now",
                "runs_replay_now", "scores_now", "stages_data_now",
                "fetches_data", "calls_api", "uses_network",
                "uses_credentials", "uses_wallet", "connects_broker",
                "connects_exchange", "uses_real_money",
                "contains_order_logic", "starts_scheduler",
                "sends_notifications", "authorizes_paper_execution",
                "authorizes_micro_live", "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate",
                "claims_profitability", "revives_candidate_3"):
        assert record[key] is False, key
    assert record["paper_trading_gate_locked"] is True
    assert record["micro_live_gate_locked"] is True
    assert record["live_gate_locked"] is True
    tampered = c4r.build_c4_dry_run_review()
    tampered["claims_profitability"] = True
    assert c4r.validate_c4_dry_run_review(tampered)["valid"] is False


def test_ledger_untouched_upstream():
    from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
        REJECTION_STATUS as C1)
    from sparta_commander.crypto_intraday_breakout_pullback_structure_v2_result_and_rejection_record_contract import (
        REJECTION_STATUS as C2)
    from sparta_commander.btc_sol_long_trend_continuation_v1_result_and_rejection_record_contract import (
        REJECTION_STATUS as C3)
    assert C1 == C2 == C3 == "REJECTED_KEPT_ON_RECORD"


def test_label_action_and_module_purity():
    assert c4r.get_c4_dry_run_review_label() == c4r.C4R_LABEL
    assert "READ-ONLY" in c4r.C4R_LABEL
    assert "NOT A PROFITABILITY CLAIM" in c4r.C4R_LABEL
    assert c4r.C4R_MODE == "RESEARCH_ONLY"
    assert c4r.NEXT_REQUIRED_ACTION == (
        "HUMAN_APPROVED_CANDIDATE_4_REAL_CANDLE_DETECTION")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in c4r.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(c4r.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch("):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned_mods = {"urllib", "requests", "socket", "http", "ccxt",
                   "smtplib", "subprocess", "websockets", "aiohttp",
                   "schedule", "apscheduler", "threading", "asyncio",
                   "time", "sched", "telegram", "email", "csv", "pandas",
                   "pathlib", "os", "io", "json", "shutil", "databento",
                   "ssl", "ftplib", "hashlib", "datetime"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods)
    assert not any(
        call.func.attr == "open" if isinstance(call.func, ast.Attribute)
        else getattr(call.func, "id", "") == "open"
        for call in ast.walk(tree) if isinstance(call, ast.Call))
