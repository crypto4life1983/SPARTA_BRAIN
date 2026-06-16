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
    required 2019 in-sample coverage is missing;
  - on the COVERED success path freezes a deterministic, SHA-pinned
    per-setup labels artifact + summary artifact under
    detector_labels/ (separate from the coverage_blocker artifact) that
    is recount-sufficient for a later labels review."""

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


# ---- success-path frozen detector_labels artifact ------------------------

def test_runner_success_path_writes_detector_labels_artifacts():
    """Source-level proof the covered path freezes labels + summary
    artifacts under detector_labels/ via the deterministic writer."""
    src = _src()
    assert "DETECTOR_LABELS_DIR" in src
    assert "detector_labels" in src
    assert "_dump_json(LABELS_PATH" in src
    assert "_dump_json(SUMMARY_PATH" in src
    assert "build_detection_artifacts" in src
    # deterministic write: sorted keys, no wall-clock timestamp.
    assert "sort_keys=True" in src
    assert "deterministic_no_wallclock_timestamp" in src


def test_runner_blocker_path_separate_from_labels_path():
    mod = _runner_module()
    assert "coverage_blocker" in str(mod.BLOCKER_PATH)
    assert "detector_labels" in str(mod.LABELS_PATH)
    assert "detector_labels" in str(mod.SUMMARY_PATH)
    assert "coverage_blocker" not in str(mod.LABELS_PATH)
    assert "coverage_blocker" not in str(mod.SUMMARY_PATH)
    assert mod.LABELS_PATH != mod.BLOCKER_PATH
    assert mod.SUMMARY_PATH != mod.BLOCKER_PATH
    assert mod.LABELS_PATH != mod.SUMMARY_PATH
    assert mod.MIN_LABELS_REVIEW_THRESHOLD == 100


def _fake_detection_inputs():
    source_meta = {
        "source_path": "data/crypto_d1_spot/raw/BTC_1d.csv",
        "row_count": 2716,
        "first_date": "2019-01-01",
        "last_date": "2026-06-08",
        "sha256": "043fb722b35e738a0c2050f9388defc7ca99322ed2f1539897"
                  "46ee28bbb89b88",
    }
    selection = {
        "favorable_weekday_bucket": 5,
        "favorable_weekday_bucket_cardinality": 1,
        "per_weekday_mean_bps": {1: 42.44, 2: 34.28, 3: 28.65,
                                 4: 61.30, 5: 83.90, 6: 34.67,
                                 7: 69.50},
        "per_weekday_sample_count": {1: 208, 2: 208, 3: 208, 4: 208,
                                     5: 208, 6: 208, 7: 208},
        "selection_metric": "highest_in_sample_mean",
        "floor_bps": 81.0,
        "cleared_81_bps_floor": True,
        "bucket_value_is_data_determined_not_hardcoded": True,
        "selected_on_in_sample_window_only": True,
        "in_sample_window": ["2019-01-01", "2022-12-31"],
    }
    a1 = {"setup_id": "BTCUSD_2023-01-06",
          "status": "accepted_for_replay_review", "entry_index": 10,
          "entry_date": "2023-01-06", "entry_price": 17000.0,
          "trigger_iso_weekday": 5, "favorable_weekday_bucket": 5,
          "rejection_reasons": []}
    a2 = {"setup_id": "BTCUSD_2023-01-13",
          "status": "accepted_for_replay_review", "entry_index": 17,
          "entry_date": "2023-01-13", "entry_price": 19000.0,
          "trigger_iso_weekday": 5, "favorable_weekday_bucket": 5,
          "rejection_reasons": []}
    rej = {"setup_id": "BTCUSD_2023-01-20",
           "status": "rejected_geometry_floor", "entry_index": 24,
           "entry_date": "2023-01-20",
           "rejection_reasons": ["all_variant_target_distances_below_81"]}
    setups = [a1, a2, rej]
    cluster = {"kept": [a1, a2], "dropped": [],
               "anti_cluster_min_bar_gap": 5,
               "tie_breaker": "keep_the_earlier_event_drop_the_later_one",
               "anti_cluster_does_not_consume_edit_token": True}
    adequacy = {"accepted_count": 2,
                "minimum_required_at_labels_review_gate": 100,
                "below_minimum_at_dry_run": True,
                "enforced_at_labels_review_gate_only": True,
                "does_not_consume_edit_token": True}
    return source_meta, selection, setups, cluster, adequacy


def test_build_artifacts_pins_source_sha_range_rowcount():
    mod = _runner_module()
    sm, sel, setups, cluster, adeq = _fake_detection_inputs()
    labels, summary = mod.build_detection_artifacts(
        source_meta=sm, selection=sel, setups=setups, cluster=cluster,
        adequacy=adeq, sha_before="abc123", sha_after="abc123")
    for art in (labels, summary):
        assert art["source_path"] == sm["source_path"]
        assert art["source_sha256_before"] == "abc123"
        assert art["source_sha256_after"] == "abc123"
        assert art["source_unchanged_during_detection"] is True
        assert art["source_first_date"] == "2019-01-01"
        assert art["source_last_date"] == "2026-06-08"
        assert art["source_row_count"] == 2716
        assert art["in_sample_selection_window"] == [
            "2019-01-01", "2022-12-31"]
        assert art["out_of_sample_window"] == [
            "2023-01-01", "2025-12-31"]
        assert art["favorable_weekday_bucket"] == 5
        assert art["per_weekday_in_sample_mean_bps"][5] == 83.90
        assert art["minimum_labels_review_threshold"] == 100


def test_build_artifacts_let_labels_review_recount_without_stdout():
    """The artifact alone must let a labels review recount accepted /
    dropped totals; here 2 accepted / 0 dropped, recounted purely from
    the frozen per-setup records (a scaled-down stand-in for the real
    156 / 0 run)."""
    mod = _runner_module()
    sm, sel, setups, cluster, adeq = _fake_detection_inputs()
    labels, summary = mod.build_detection_artifacts(
        source_meta=sm, selection=sel, setups=setups, cluster=cluster,
        adequacy=adeq, sha_before="x", sha_after="x")
    recount_accepted = len(labels["accepted_setups_post_anti_cluster"])
    recount_dropped = len(labels["anti_cluster_dropped"])
    assert recount_accepted == 2
    assert recount_dropped == 0
    assert labels["accepted_post_anti_cluster"] == recount_accepted
    assert labels["anti_cluster_dropped_count"] == recount_dropped
    assert summary["accepted_post_anti_cluster"] == recount_accepted
    assert summary["anti_cluster_dropped_count"] == recount_dropped
    assert labels["attempts"] == 3
    assert labels["accepted_pre_anti_cluster"] == 2
    assert labels["status_breakdown"] == {
        "accepted_for_replay_review": 2, "rejected_geometry_floor": 1}
    assert all(r["status"] == "accepted_for_replay_review"
               for r in labels["accepted_setups_post_anti_cluster"])
    # accepted records carry recountable per-setup identity fields.
    for r in labels["accepted_setups_post_anti_cluster"]:
        assert r["setup_id"]
        assert r["favorable_weekday_bucket"] == 5
        assert r["trigger_iso_weekday"] == 5


def test_build_artifacts_make_no_pnl_replay_or_trading_claims():
    mod = _runner_module()
    sm, sel, setups, cluster, adeq = _fake_detection_inputs()
    labels, summary = mod.build_detection_artifacts(
        source_meta=sm, selection=sel, setups=setups, cluster=cluster,
        adequacy=adeq, sha_before="x", sha_after="x")
    for art in (labels, summary):
        assert art["no_replay"] is True
        assert art["no_pnl"] is True
        assert art["no_trading"] is True
        assert art["scope_locks"]["no_replay"] is True
        assert art["scope_locks"]["no_pnl"] is True
        assert art["scope_locks"]["no_live_trading"] is True
        assert art["deterministic_no_wallclock_timestamp"] is True


def test_summary_references_labels_path_like_c4_c9_pattern():
    mod = _runner_module()
    sm, sel, setups, cluster, adeq = _fake_detection_inputs()
    _labels, summary = mod.build_detection_artifacts(
        source_meta=sm, selection=sel, setups=setups, cluster=cluster,
        adequacy=adeq, sha_before="x", sha_after="x")
    assert summary["labels_path"].endswith(".json")
    assert "detector_labels" in summary["labels_path"]
    assert summary["artifact_schema_version"] == "c10_detector_summary_v1"
    assert _labels["artifact_schema_version"] == "c10_detector_labels_v1"
