"""Tests for the SPARTA Breakout-Pullback-Structure Detector Dry Run.

Fixture/in-memory 15m candles only: a clean breakout->retest->continuation
fixture is ACCEPTED above the 81 bps floor; every failure mode maps to its
closed status; the dry run cannot fetch, write, replay, or score; candidate
#1 stays rejected; all gates stay LOCKED.
"""

from __future__ import annotations

import ast
import os.path

import sparta_commander.crypto_intraday_breakout_pullback_structure_detector_dry_run as bpr


def _bar(i, o, h, l, c, **extra):
    bar = {"timestamp_utc": "2026-06-10T%02d:%02d:00Z" % (i // 4,
                                                          (i % 4) * 15),
           "open": o, "high": h, "low": l, "close": c}
    bar.update(extra)
    return bar


def _range_bars(count, start=0):
    return [_bar(start + i, 99.9, 100.5, 99.5, 100.1)
            for i in range(count)]


def _accepted_fixture():
    candles = _range_bars(36)
    candles.append(_bar(36, 100.2, 101.1, 100.1, 101.0))   # breakout
    candles.append(_bar(37, 101.0, 102.0, 100.9, 101.8))   # run-up
    candles.append(_bar(38, 101.6, 101.7, 100.55, 100.9))  # pullback/retest
    candles.append(_bar(39, 101.0, 102.0, 100.9, 101.9))   # continuation
    return candles


def _run(candles):
    return bpr.run_bp_detector_dry_run("BTCUSD", "2026-06-10", candles)


def test_valid_fixture_setup_accepts():
    label = _run(_accepted_fixture())
    assert label["detector_status"] == (
        "BP_SETUP_LABEL_ACCEPTED_FOR_REPLAY_REVIEW")
    assert label["direction"] == "long"
    assert label["range_high"] == 100.5 and label["range_low"] == 99.5
    assert label["breakout_close"] == 101.0
    assert label["breakout_body_ratio"] >= 0.5
    assert label["pullback_level"] == 100.55
    assert 0 < label["pullback_depth_ratio"] <= 0.618
    assert label["continuation_close"] == 101.9
    assert label["entry_price"] == 101.9
    assert label["stop_model"] in ("structural_swing", "atr_1_5x")
    # the WIDER stop was selected
    assert label["selected_stop_price"] <= min(
        label["structural_stop_price"], label["atr_stop_price"]) + 1e-9
    assert label["risk_distance_bps"] >= 81
    assert label["cost_floor_pass"] is True
    assert label["target_4r_price"] > label["target_3r_price"] > (
        label["target_2r_price"]) > label["entry_price"]
    assert label["label_authorizes_nothing"] is True


def test_no_breakout_rejects():
    label = _run(_range_bars(45))
    assert label["detector_status"] == "BP_SETUP_REJECTED_NO_BREAKOUT"


def test_weak_breakout_rejects():
    candles = _range_bars(36)
    candles.append(_bar(36, 100.55, 101.3, 100.3, 100.75))  # body 0.2
    candles.extend(_range_bars(3, start=37))
    label = _run(candles)
    assert label["detector_status"] == "BP_SETUP_REJECTED_WEAK_BREAKOUT"
    assert label["breakout_body_ratio"] < 0.5


def test_no_pullback_rejects():
    candles = _range_bars(36)
    candles.append(_bar(36, 100.2, 101.1, 100.1, 101.0))   # breakout
    candles.append(_bar(37, 101.0, 101.8, 101.2, 101.5))
    candles.append(_bar(38, 101.5, 101.9, 101.3, 101.6))
    candles.append(_bar(39, 101.6, 102.0, 101.4, 101.8))
    label = _run(candles)
    assert label["detector_status"] == "BP_SETUP_REJECTED_NO_PULLBACK"


def test_failed_retest_on_breakout_failure_rejects():
    candles = _range_bars(36)
    candles.append(_bar(36, 100.2, 101.1, 100.1, 101.0))   # breakout
    candles.append(_bar(37, 100.9, 101.0, 99.9, 100.0))    # close < 100.25
    candles.extend(_range_bars(2, start=38))
    label = _run(candles)
    assert label["detector_status"] == "BP_SETUP_REJECTED_FAILED_RETEST"
    assert label["retest_pass"] is False


def test_too_deep_pullback_rejects_as_failed_retest():
    candles = _range_bars(36)
    candles.append(_bar(36, 100.2, 101.1, 100.1, 101.0))   # breakout
    candles.append(_bar(37, 101.0, 103.5, 100.9, 103.3))   # big leg
    candles.append(_bar(38, 103.0, 103.1, 100.55, 100.9))  # deep retest
    candles.append(_bar(39, 101.0, 102.0, 100.9, 101.9))
    label = _run(candles)
    assert label["detector_status"] == "BP_SETUP_REJECTED_FAILED_RETEST"
    assert label["pullback_depth_ratio"] > 0.618


def test_no_continuation_rejects():
    candles = _range_bars(36)
    candles.append(_bar(36, 100.2, 101.1, 100.1, 101.0))   # breakout
    candles.append(_bar(37, 101.0, 102.0, 100.9, 101.8))   # run-up
    candles.append(_bar(38, 101.6, 101.7, 100.55, 100.9))  # pullback
    candles.append(_bar(39, 100.9, 101.5, 100.7, 101.2))   # never > 101.7
    label = _run(candles)
    assert label["detector_status"] == "BP_SETUP_REJECTED_NO_CONTINUATION"


def test_risk_below_81_bps_rejects():
    tight = [_bar(i, 99.99, 100.02, 99.98, 100.01) for i in range(36)]
    tight.append(_bar(36, 100.0, 100.16, 100.0, 100.13))    # breakout
    tight.append(_bar(37, 100.13, 100.3, 100.18, 100.28))   # run-up
    tight.append(_bar(38, 100.25, 100.26, 100.12, 100.2))   # retest
    tight.append(_bar(39, 100.2, 100.32, 100.18, 100.3))    # continuation
    label = _run(tight)
    assert label["detector_status"] == "BP_SETUP_REJECTED_RISK_BELOW_81_BPS"
    assert label["risk_distance_bps"] < 81
    assert label["cost_floor_pass"] is False


def test_insufficient_candles_rejects():
    label = _run(_range_bars(10))
    assert label["detector_status"] == (
        "BP_SETUP_REJECTED_INSUFFICIENT_CANDLES")
    assert _run(None)["detector_status"] == (
        "BP_SETUP_REJECTED_INSUFFICIENT_CANDLES")
    broken = _range_bars(45)
    del broken[5]["close"]
    assert _run(broken)["detector_status"] == (
        "BP_SETUP_REJECTED_INSUFFICIENT_CANDLES")


def test_forbidden_candle_fields_reject():
    for bad in ("order_id", "api_key", "wallet_address", "broker_ref"):
        candles = _accepted_fixture()
        candles[3] = _bar(3, 99.9, 100.5, 99.5, 100.1, **{bad: "x"})
        label = _run(candles)
        assert label["detector_status"] == (
            "BP_SETUP_REJECTED_FORBIDDEN_CAPABILITY"), bad


def test_dry_run_is_deterministic_and_fixture_only():
    assert _run(_accepted_fixture()) == _run(_accepted_fixture())
    # nothing on disk was touched, no detector_labels for candidate #2 exist
    assert not os.path.isdir(
        "C:/SPARTA_BRAIN/data/crypto_intraday_breakout_pullback_structure")


def test_candidate_1_remains_rejected_and_preserved():
    from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
        REJECTION_REASON, REJECTION_STATUS)
    assert REJECTION_STATUS == "REJECTED_KEPT_ON_RECORD"
    assert REJECTION_REASON == "COST_NON_VIABLE_RISK_GEOMETRY"
    label = _run(_accepted_fixture())
    assert label["candidate_id"] == (
        "CRYPTO_INTRADAY_BREAKOUT_PULLBACK_STRUCTURE_V1")


def test_gates_locked_in_spec_record():
    import sparta_commander.crypto_intraday_breakout_pullback_structure_detector_spec as bpd
    spec = bpd.record_bp_detector_spec(
        "BREAKOUT_PULLBACK_STRATEGY_SPEC_READY")
    assert spec["paper_trading_gate_locked"] is True
    assert spec["micro_live_gate_locked"] is True
    assert spec["live_gate_locked"] is True
    assert spec["runs_detector_now"] is False
    assert spec["runs_replay_now"] is False
    assert spec["scores_now"] is False


def test_label_action_no_io_no_network_imports():
    assert bpr.get_bp_detector_dry_run_label() == bpr.BPR_LABEL
    assert bpr.BPR_MODE == "RESEARCH_ONLY"
    assert bpr.MIN_CANDLES == 40
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in bpr.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(bpr.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    assert "while true" not in src.lower() and "sleep(" not in src.lower()
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch("):
        assert verb not in src, verb
    tree = ast.parse(src)
    sparta_imports = {node.module for node in ast.walk(tree)
                      if isinstance(node, ast.ImportFrom) and node.module
                      and node.module.startswith("sparta_commander")}
    for module in sparta_imports:
        for fragment in ("replay_runner", "replay_spec", "optimizer",
                         "fetch"):
            assert fragment not in module, module
    banned_mods = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
                   "subprocess", "websockets", "aiohttp", "schedule",
                   "apscheduler", "threading", "asyncio", "time", "telegram",
                   "email", "csv", "pandas", "pathlib", "os", "io", "json",
                   "shutil", "databento", "ssl", "ftplib", "datetime",
                   "hashlib"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods)
    assert not any(call.func.attr == "open" if isinstance(call.func, ast.Attribute)
                   else getattr(call.func, "id", "") == "open"
                   for call in ast.walk(tree) if isinstance(call, ast.Call))