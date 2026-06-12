"""Tests for the Candidate #3 dry-run review / evidence-freeze contract.

Proves: the review APPROVES by recomputing the pushed dry run live and
matching every frozen fact; any tampering with the frozen expectations
invalidates; synthetic-only scope facts are frozen; capabilities are zero;
and the next action is the real-candle detection HUMAN gate.
"""

from __future__ import annotations

import ast

import sparta_commander.btc_sol_long_trend_continuation_dry_run_review_contract as drr


def test_review_approved_with_zero_mismatches():
    record = drr.build_dry_run_review()
    assert record["verdict"] == drr.VERDICT_DRR_APPROVED
    assert record["blockers"] == []
    assert record["mismatches"] == []
    assert drr.validate_dry_run_review(record)["valid"] is True
    assert record["candidate_id"] == "BTC_SOL_LONG_TREND_CONTINUATION_V1"
    # determinism
    assert drr.build_dry_run_review() == record


def test_frozen_accepted_fixture_facts():
    exp = drr.EXPECTED_ACCEPTED_FIXTURE
    assert exp["symbol"] == "BTCUSD"
    assert exp["total_labels"] == 5
    assert exp["accepted_labels"] == 1
    assert exp["entry_price"] == 102.4
    assert exp["stop_price"] == 101.5
    assert exp["structural_stop_price"] == 101.5
    assert exp["stop_source"] == "structural_pullback_low"
    assert exp["stop_selected_because"] == (
        "structural_wider_than_1_5x_atr_stop")
    assert exp["risk_distance_bps"] == 87.890625
    assert exp["risk_distance_bps"] >= 81
    assert exp["risk_meets_81bps_floor"] is True
    assert (exp["target_2r_price"], exp["target_3r_price"],
            exp["target_4r_price"]) == (104.2, 105.1, 106.0)


def test_frozen_tight_and_downtrend_facts():
    tight = drr.EXPECTED_TIGHT_FIXTURE
    assert tight["symbol"] == "SOLUSD"
    assert tight["accepted_labels"] == 0
    assert tight["cost_floor_rejections"] == 1
    assert tight["stop_source"] == "volatility_1_5x_atr14"
    assert tight["stop_selected_because"] == (
        "volatility_wider_than_structural_stop")
    assert tight["risk_distance_bps"] == 39.910845
    assert tight["risk_distance_bps"] < 81
    assert tight["risk_below_81bps_floor"] is True
    down = drr.EXPECTED_DOWNTREND_FIXTURE
    assert down["accepted_labels"] == 0
    assert down["trend_rejections"] == 1


def test_frozen_anti_lookahead_facts():
    al = drr.EXPECTED_ANTI_LOOKAHEAD
    assert al["signal_0659_completed_1h_bars"] == 24
    assert al["signal_0659_sufficient"] is False
    assert al["signal_0700_completed_1h_bars"] == 25
    assert al["signal_0700_sufficient"] is True


def test_scope_facts_frozen_no_real_detection_no_replay():
    record = drr.build_dry_run_review()
    facts = record["frozen_scope_facts"]
    assert "synthetic in-memory fixtures only" in facts
    assert ("no real-candle detection has occurred for candidate #3"
            in facts)
    assert "no replay has occurred for candidate #3" in facts
    assert "nothing here is a profitability claim" in facts
    assert record["runs_real_detection_now"] is False
    assert record["runs_replay_now"] is False
    assert record["fetches_data"] is False
    tampered = drr.build_dry_run_review()
    tampered["frozen_scope_facts"] = tampered["frozen_scope_facts"][:2]
    assert drr.validate_dry_run_review(tampered)["valid"] is False


def test_tampering_frozen_facts_invalidates():
    for field, value in (
            ("expected_detector_verdict", "SOMETHING_ELSE"),
            ("expected_accepted_fixture", {"entry_price": 1.0}),
            ("expected_tight_fixture", {"risk_distance_bps": 80.9}),
            ("expected_downtrend_fixture", {"accepted_labels": 1}),
            ("expected_anti_lookahead", {}),
            ("cost_floor_bps", 54),
            ("candidate_id", "CANDIDATE_2_REVIVED")):
        tampered = drr.build_dry_run_review()
        tampered[field] = value
        assert drr.validate_dry_run_review(
            tampered)["valid"] is False, field
    approved_with_mismatch = drr.build_dry_run_review()
    approved_with_mismatch["mismatches"] = ["fake"]
    assert drr.validate_dry_run_review(
        approved_with_mismatch)["valid"] is False


def test_capabilities_locked():
    record = drr.build_dry_run_review()
    for key in ("executes", "writes_files", "runs_real_detection_now",
                "runs_replay_now", "scores_now", "stages_data_now",
                "fetches_data", "calls_api", "uses_network",
                "uses_credentials", "uses_wallet", "connects_broker",
                "connects_exchange", "uses_real_money",
                "contains_order_logic", "starts_scheduler",
                "sends_notifications", "authorizes_paper_execution",
                "authorizes_micro_live", "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate",
                "claims_profitability", "revives_candidate_2"):
        assert record[key] is False, key
    assert record["paper_trading_gate_locked"] is True
    assert record["micro_live_gate_locked"] is True
    assert record["live_gate_locked"] is True
    tampered = drr.build_dry_run_review()
    tampered["claims_profitability"] = True
    assert drr.validate_dry_run_review(tampered)["valid"] is False


def test_ledger_untouched_upstream():
    from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
        REJECTION_STATUS as C1, REJECTION_REASON as R1)
    from sparta_commander.crypto_intraday_breakout_pullback_structure_v2_result_and_rejection_record_contract import (
        REJECTION_STATUS as C2, REJECTION_REASON as R2)
    assert (C1, R1) == ("REJECTED_KEPT_ON_RECORD",
                        "COST_NON_VIABLE_RISK_GEOMETRY")
    assert (C2, R2) == (
        "REJECTED_KEPT_ON_RECORD",
        "EDGE_FAILURE_SURVIVED_ONE_AUTHORIZED_FILTER_EXPERIMENT")


def test_label_action_and_module_purity():
    assert drr.get_dry_run_review_label() == drr.DRR_LABEL
    assert "READ-ONLY" in drr.DRR_LABEL
    assert "NOT A PROFITABILITY CLAIM" in drr.DRR_LABEL
    assert drr.DRR_MODE == "RESEARCH_ONLY"
    assert drr.NEXT_REQUIRED_ACTION == (
        "HUMAN_APPROVED_CANDIDATE_3_REAL_CANDLE_DETECTION")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in drr.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(drr.__file__, encoding="utf-8").read()
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
