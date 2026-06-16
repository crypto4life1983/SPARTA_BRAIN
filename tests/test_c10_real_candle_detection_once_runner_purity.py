"""Purity / boundedness tests for the C10 real-candle detection
one-off runner (`tools/c10_real_candle_detection_once.py`). Untracked
runner; this test is also untracked unless a later review gate
explicitly approves committing it.

Verifies the runner:
  - imports no network / process / scheduler / broker module;
  - calls no exec / eval / order / login / fetch verb;
  - is locked to BTCUSD / 1d / long_only / C10 family;
  - uses ONLY the canonical staged crypto_d1_spot source (NOT
    frozen_regime_inputs);
  - uses the pushed C10 selector + scanner + anti-cluster filter +
    sample-size adequacy check from sparta_commander;
  - performs no replay / relabel / PnL / trading / scheduler action;
  - has side effects only inside the __main__ block;
  - BLOCKS final detection (no scan, no setup claims) when the
    required 2019 in-sample coverage is missing -- the actual state of
    the staged data today."""

from __future__ import annotations

import ast
from pathlib import Path

RUNNER_PATH = (Path(__file__).resolve().parent.parent
               / "tools" / "c10_real_candle_detection_once.py")


def _src() -> str:
    return RUNNER_PATH.read_text(encoding="utf-8")


def _tree() -> ast.AST:
    return ast.parse(_src())


def test_runner_file_exists_and_parses():
    assert RUNNER_PATH.exists()
    assert ast.parse(_src())


def test_runner_imports_no_network_process_or_scheduler_modules():
    tree = _tree()
    banned_top_level = {
        "urllib", "requests", "socket", "http", "ccxt", "smtplib",
        "subprocess", "websockets", "aiohttp", "schedule",
        "apscheduler", "telegram", "databento", "ssl", "ftplib",
        "selenium", "paramiko", "scapy", "fabric",
        "multiprocessing",
    }
    imported = {
        n.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for n in node.names
    } | {
        node.module.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    }
    assert not (imported & banned_top_level), (
        imported & banned_top_level)


def test_runner_does_not_use_exec_eval_or_trading_verbs():
    tree = _tree()
    banned_call_names = {
        "exec", "eval", "compile",
        "place_order", "submit_order", "send_order",
        "create_order", "cancel_order", "buy", "sell",
        "place_buy", "place_sell",
        "fetch_ticker", "fetch_balance", "fetch_ohlcv",
        "fetch_trades", "fetch_order", "fetch_orders",
        "urlopen", "Request", "Popen", "spawn", "spawnl",
        "spawnv", "system", "connect_broker",
        "connect_exchange", "send_message", "send_notification",
        "send_email", "login", "authenticate",
        "Scheduler", "start_scheduler", "schedule_job", "cron",
    }
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name = (func.attr if isinstance(func, ast.Attribute)
                else getattr(func, "id", ""))
        assert name not in banned_call_names, "call:" + name


def test_runner_locked_to_btcusd_1d_long_only_and_c10_family():
    src = _src()
    assert "INTRAWEEK_CALENDAR_SEASONALITY_DRIFT_V1" in src
    assert "intraweek_calendar_seasonality_drift" in src
    assert 'SYMBOL = "BTCUSD"' in src
    assert 'TIMEFRAME = "1d"' in src
    assert 'DIRECTION = "long_only"' in src
    for banned_symbol in ("ETHUSD", "SOLUSD", "AVAXUSD", "ARBUSD",
                          "MATICUSD"):
        assert banned_symbol not in src, banned_symbol
    # 1d is the C10 timeframe; every OTHER timeframe is forbidden.
    for banned_tf in ('"1h"', '"4h"', '"15m"', '"1m"', '"30m"',
                      '"5m"'):
        assert banned_tf not in src, banned_tf


def test_runner_uses_only_canonical_crypto_d1_spot_source():
    src = _src()
    assert "crypto_d1_spot" in src
    assert "BTC_1d.csv" in src
    # The frozen_regime_inputs source is NOT authorized for this runner.
    # It may appear ONLY as negative documentation / a scope-lock key;
    # it must NEVER be used as a quoted path segment (a real source
    # join such as / "frozen_regime_inputs").
    assert '"frozen_regime_inputs"' not in src
    assert "'frozen_regime_inputs'" not in src


def test_runner_pins_source_data_with_sha256():
    src = _src()
    assert "compute_sha256" in src
    assert "staged_source_data_mutated_during_scan" in src


def test_runner_emits_only_under_c10_data_path():
    src = _src()
    assert "intraweek_calendar_seasonality_c10" in src
    assert "OUT_DIR.mkdir" in src
    for banned_out in ("data/low_volume_capitulation_c9",
                       "data/liquidity_sweep_c8",
                       "data/volatility_compression_c7",
                       "data/rs_rotation_c6",
                       "data/eth_sol_relative_strength_c5",
                       "data/sol_btc_long_c4",
                       "data/btc_sol_long_c3",
                       "data/breakout_pullback",
                       "data/ny_fvg_choch/detector_labels",
                       "data/ny_fvg_choch/replay_results"):
        assert banned_out + '", "w"' not in src, banned_out
        assert banned_out + '", "wb"' not in src, banned_out


def test_runner_uses_pushed_c10_contract_for_selection_and_scan():
    src = _src()
    assert ("sparta_commander.intraweek_calendar_seasonality_drift"
            "_v1_detector_spec_dry_run_contract") in src
    assert "select_favorable_weekday_bucket" in src
    assert "scan_c10_setups" in src
    assert "apply_anti_cluster_filter" in src
    assert "check_sample_size_adequacy" in src


def test_runner_does_not_perform_replay_relabel_pnl_or_trading():
    """AST-only check: replay/relabel/PnL/trading/scheduler names must
    not appear as definitions, calls, imports, or attribute
    references. (Mentions inside docstrings or scope-lock string
    literals are not callable behaviour and are allowed.)"""
    tree = _tree()
    banned_names = {
        "compute_pnl", "evaluate_pnl", "run_replay",
        "evaluate_replay", "relabel", "do_relabel",
        "paper_trade", "live_trade", "place_trade",
        "broker_api", "exchange_api", "wallet_api",
        "private_api", "rest_api",
        "send_email", "send_message", "notify",
        "Scheduler", "start_scheduler", "schedule_job", "cron",
    }
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                             ast.ClassDef)):
            assert node.name not in banned_names, (
                "definition:" + node.name)
        if isinstance(node, ast.Call):
            func = node.func
            name = (func.attr if isinstance(func, ast.Attribute)
                    else getattr(func, "id", ""))
            assert name not in banned_names, "call:" + name
        if isinstance(node, ast.Attribute):
            assert node.attr not in banned_names, (
                "attribute:" + node.attr)
        if isinstance(node, ast.Import):
            for n in node.names:
                assert n.name.split(".")[0] not in banned_names, (
                    "import:" + n.name)
        if isinstance(node, ast.ImportFrom) and node.module:
            assert node.module.split(".")[0] not in banned_names, (
                "importfrom:" + node.module)


def test_runner_main_module_side_effect_only_inside_main_block():
    """Importing the runner must NOT trigger detection or file writes:
    no top-level Call expression statements are allowed."""
    tree = _tree()
    for node in tree.body:
        if isinstance(node, ast.Expr) and isinstance(
                node.value, ast.Call):
            assert False, (
                "runner has a top-level Call expression: "
                + ast.dump(node))


def test_runner_scope_locks_present():
    src = _src()
    for lock in ("no_replay", "no_relabel", "no_pnl", "no_fetch",
                 "no_network", "no_api", "no_credentials",
                 "no_broker", "no_exchange", "no_wallet",
                 "no_scheduler", "no_paper_trading",
                 "no_micro_live", "no_live_trading",
                 "no_edit_token_consumed",
                 "no_downstream_gates_unlocked",
                 "frozen_regime_inputs_source_not_used",
                 "c10_contract_not_weakened_for_missing_2019"):
        assert lock in src, lock


# ---- functional proof of the coverage block -------------------------------

def _runner_module():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "c10_real_candle_detection_once_under_test", RUNNER_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_runner_blocks_when_2019_in_sample_coverage_missing():
    """The pure coverage evaluator must BLOCK when the source begins
    after the required in-sample start, and must NOT block when 2019 is
    present -- proving the gate is real, not hard-coded to always pass
    or always fail."""
    mod = _runner_module()
    # Required in-sample window is taken from the pushed C10 detector
    # and starts in 2019.
    assert mod.REQUIRED_IN_SAMPLE_START == "2019-01-01"
    # Actual staged data begins 2020-01-01 -> missing coverage -> BLOCK.
    blocked = mod.evaluate_in_sample_coverage("2020-01-01")
    assert blocked["in_sample_coverage_present"] is False
    assert blocked["missing_2019_in_sample_coverage"] is True
    assert blocked["status"] == (
        "BLOCKED_MISSING_REQUIRED_IN_SAMPLE_COVERAGE")
    # A hypothetical fully-covered source would NOT block.
    covered = mod.evaluate_in_sample_coverage("2019-01-01")
    assert covered["in_sample_coverage_present"] is True
    assert covered["missing_2019_in_sample_coverage"] is False
    assert covered["status"] == "REQUIRED_IN_SAMPLE_COVERAGE_PRESENT"
    # A missing/empty source also blocks (never silently proceeds).
    empty = mod.evaluate_in_sample_coverage(None)
    assert empty["in_sample_coverage_present"] is False
    assert empty["status"] == (
        "BLOCKED_MISSING_REQUIRED_IN_SAMPLE_COVERAGE")
