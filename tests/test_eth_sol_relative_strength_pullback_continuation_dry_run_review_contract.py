"""Tests for the Candidate #5 dry-run review / evidence-freeze contract.

Proves: the review FREEZES by recomputing the pushed dry run live and
matching every frozen fact; the full upstream chain gates it; all
fixture counts, accepted geometry, partial-floor arithmetic, and the
RS/pullback/trigger/stop/geometry/no-lookahead/non-overlap proofs hold;
purity and safety locks; tampering invalidates; no real candles, no real
detection, no execution of any kind. Commander safety suite runs
alongside."""

from __future__ import annotations

import ast

import sparta_commander.eth_sol_relative_strength_pullback_continuation_detector_spec_contract as c5d
import sparta_commander.eth_sol_relative_strength_pullback_continuation_dry_run_review_contract as c5r


def test_review_frozen_with_zero_mismatches():
    record = c5r.build_c5_dry_run_review()
    assert record["verdict"] == c5r.VERDICT_C5R_FROZEN
    assert record["blockers"] == []
    assert record["mismatches"] == []
    assert c5r.validate_c5_dry_run_review(record)["valid"] is True
    assert record["candidate_id"] == (
        "ETH_SOL_RELATIVE_STRENGTH_PULLBACK_CONTINUATION_V1")
    assert c5r.build_c5_dry_run_review() == record  # determinism


def test_upstream_chain_certifies_live():
    import sparta_commander.eth_sol_relative_strength_pullback_continuation_spec_review_contract as c5s
    import sparta_commander.eth_sol_relative_strength_pullback_continuation_family_proposal_contract as c5p
    import sparta_commander.strategy_factory_autopilot_research_loop_v1_contract as ap
    assert c5d.build_c5_detector_spec_contract()["verdict"] == (
        "CANDIDATE_5_DETECTOR_SPEC_READY")
    assert c5d.run_c5_detector_dry_run()["verdict"] == (
        "CANDIDATE_5_DETECTOR_DRY_RUN_PASSED")
    assert c5s.build_candidate_5_spec_review()["verdict"] == (
        "CANDIDATE_5_SPEC_REVIEW_READY")
    assert c5p.build_candidate_5_family_proposal()["verdict"] == (
        "CANDIDATE_5_FAMILY_PROPOSAL_READY")
    assert ap.build_autopilot_loop_contract()["verdict"] == (
        "STRATEGY_FACTORY_AUTOPILOT_RESEARCH_LOOP_V1_READY")
    from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
        REJECTION_STATUS as C1)
    from sparta_commander.crypto_intraday_breakout_pullback_structure_v2_result_and_rejection_record_contract import (
        REJECTION_STATUS as C2)
    from sparta_commander.btc_sol_long_trend_continuation_v1_result_and_rejection_record_contract import (
        REJECTION_STATUS as C3)
    from sparta_commander.sol_btc_long_1h_swing_structure_rejection_record_contract import (
        REJECTION_STATUS as C4)
    assert C1 == C2 == C3 == C4 == "REJECTED_KEPT_ON_RECORD"


def test_frozen_fixture_counts():
    assert c5r.EXPECTED_FIXTURE_COUNTS == {
        "eth_accepted": {"attempts": 1, "accepted": 1},
        "sol_accepted": {"attempts": 1, "accepted": 1},
        "rs_not_stronger": {"attempts": 1, "accepted": 0},
        "pullback_too_short": {"attempts": 1, "accepted": 0},
        "pullback_too_long": {"attempts": 1, "accepted": 0},
        "pullback_too_deep": {"attempts": 1, "accepted": 0},
        "pullback_below_leg_low": {"attempts": 1, "accepted": 0},
        "no_trigger_intrabar_only": {"attempts": 0, "accepted": 0},
        "tight_floor_partial": {"attempts": 1, "accepted": 1}}


def test_frozen_accepted_record_facts():
    eth = c5r.EXPECTED_ETH_ACCEPTED
    assert eth["symbol"] == "ETHUSD"
    assert eth["direction"] == "long"
    assert eth["timeframe"] == "1h"
    assert eth["accepted_count"] == 1
    assert eth["entry_price"] == 110.7
    assert eth["stop_distance"] == 1.8
    assert eth["stop_price"] == 108.9
    assert eth["stop_source"] == (
        "structure_distance_greater_than_1_5x_atr")
    assert eth["stop_distance"] > 1.5 * eth["atr14"]
    assert eth["geometry_floor_pass_by_variant"] == {
        "2r": True, "3r": True, "4r": True}
    assert eth["replay_start_time"] > eth["trigger_time"]
    sol = c5r.EXPECTED_SOL_ACCEPTED
    assert sol["symbol"] == "SOLUSD"
    assert sol["accepted_count"] == 1
    assert sol["entry_price"] == 110.7
    assert sol["stop_distance"] == 1.8
    assert sol["same_frozen_scanner_geometry_as_eth"] is True


def test_frozen_tight_floor_partial_arithmetic():
    tight = c5r.EXPECTED_TIGHT_FLOOR
    assert tight["target_distance_bps_2r"] == 56.017347
    assert tight["target_distance_bps_3r"] == 84.026021
    assert tight["target_distance_bps_4r"] == 112.034695
    assert tight["floor_bps"] == 81.0
    assert tight["target_distance_bps_2r"] < 81.0      # 2R fails
    assert tight["target_distance_bps_3r"] >= 81.0     # 3R passes
    assert tight["target_distance_bps_4r"] >= 81.0     # 4R passes
    assert tight["floor_pass"] == {"2r": False, "3r": True, "4r": True}


def test_frozen_dry_run_proofs_complete():
    proofs = c5r.FROZEN_DRY_RUN_PROOFS
    assert len(proofs) == 9
    assert any("return_20 must be positive AND greater" in p
               for p in proofs)
    assert any("2-6 bars only" in p and "38.2 percent" in p
               for p in proofs)
    assert any("intrabar high alone is not enough" in p for p in proofs)
    assert any("max(atr stop, structure stop)" in p
               and "min(...)" in p for p in proofs)
    assert any("27 bps" in p and "81 bps" in p and "2r/3r/4r" in p
               for p in proofs)
    assert any("future-bar mutation cannot change" in p
               and "next bar strictly after" in p for p in proofs)
    assert any("reduce-only, never add" in p for p in proofs)
    assert any("no file i/o" in p and "no network" in p for p in proofs)
    assert any("no real-detection authorization" in p for p in proofs)


def test_tampering_invalidates():
    for field, value in (
            ("expected_detector_verdict", "SOMETHING"),
            ("expected_dry_run_verdict", "SOMETHING"),
            ("expected_fixture_counts", {}),
            ("expected_eth_accepted", {"entry_price": 1.0}),
            ("expected_sol_accepted", {}),
            ("expected_tight_floor", {"floor_bps": 54.0}),
            ("frozen_dry_run_proofs", []),
            ("real_detection_authorized_by_this_gate", True),
            ("claims_profitability", True),
            ("auto_pushes", True),
            ("runs_real_detection_now", True),
            ("creates_data_artifacts_now", True),
            ("live_gate_locked", False),
            ("candidate_id", "CANDIDATE_4_REVIVED"),
            ("verdict", "CANDIDATE_5_APPROVED_FOR_TRADING")):
        tampered = c5r.build_c5_dry_run_review()
        tampered[field] = value
        assert c5r.validate_c5_dry_run_review(
            tampered)["valid"] is False, field
    frozen_with_mismatch = c5r.build_c5_dry_run_review()
    frozen_with_mismatch["mismatches"] = ["fake"]
    assert c5r.validate_c5_dry_run_review(
        frozen_with_mismatch)["valid"] is False


def test_no_real_candles_and_capabilities_locked():
    dry = c5d.run_c5_detector_dry_run()
    assert dry["reads_real_candles"] is False
    assert dry["reads_any_files"] is False
    assert dry["uses_synthetic_fixtures_only"] is True
    record = c5r.build_c5_dry_run_review()
    assert record["real_detection_authorized_by_this_gate"] is False
    for key in ("executes", "writes_files", "labels_now",
                "runs_real_detection_now", "runs_replay_now",
                "scores_now", "stages_data_now", "fetches_data",
                "calls_api", "uses_network", "uses_credentials",
                "uses_wallet", "uses_account", "connects_broker",
                "connects_exchange", "uses_real_money",
                "contains_order_logic", "starts_scheduler",
                "sends_notifications", "auto_commits", "auto_pushes",
                "creates_runners_now", "creates_data_artifacts_now",
                "modifies_staged_market_data",
                "authorizes_paper_execution", "authorizes_micro_live",
                "authorizes_live_trading", "promotes_gate",
                "unlocks_downstream_gate", "claims_profitability"):
        assert record[key] is False, key
    assert record["paper_trading_gate_locked"] is True
    assert record["micro_live_gate_locked"] is True
    assert record["live_gate_locked"] is True


def test_next_gate_is_real_candle_authorization_only():
    record = c5r.build_c5_dry_run_review()
    assert record["next_required_action"] == (
        "HUMAN_APPROVED_CANDIDATE_5_REAL_CANDLE_DETECTION")
    assert c5r.NEXT_REQUIRED_ACTION == (
        "HUMAN_APPROVED_CANDIDATE_5_REAL_CANDLE_DETECTION")
    # this gate itself authorizes nothing
    assert record["real_detection_authorized_by_this_gate"] is False
    assert record["unlocks_downstream_gate"] is False
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in c5r.NEXT_REQUIRED_ACTION.upper(), banned


def test_label_and_module_purity():
    assert c5r.get_c5_dry_run_review_label() == c5r.C5R_LABEL
    assert "READ-ONLY" in c5r.C5R_LABEL
    assert "NOT A PROFITABILITY CLAIM" in c5r.C5R_LABEL
    assert c5r.C5R_MODE == "RESEARCH_ONLY"
    assert c5r.VERDICT_C5R_FROZEN == "CANDIDATE_5_DRY_RUN_REVIEW_FROZEN"
    src = open(c5r.__file__, encoding="utf-8").read()
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
