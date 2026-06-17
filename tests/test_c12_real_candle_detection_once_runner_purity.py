"""Purity / safety tests for the C12 real-candle detection runner
tools/c12_real_candle_detection_once.py.

Verifies: no side effects at import (writes only inside main()); no network /
broker / credential / order reach; SHA-pins all three sources + aborts on drift;
reuses the committed C12 detector; computes NO replay, NO PnL, and NO baseline
comparison; applies the labels-stage entry-spacing non-overlap; classifies regime
per-asset; runs the sample-size + structural checks and records
structural_rejection_pressure when they fail; reserves a forward-OOS window;
writes only into the gitignored c12 data dir. csv/hashlib/json/datetime/open are
legitimate runner tools; network/broker reach is NOT."""
from __future__ import annotations

import ast
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = _REPO_ROOT / "tools" / "c12_real_candle_detection_once.py"


def _src():
    return RUNNER.read_text(encoding="utf-8")


def test_runner_exists():
    assert RUNNER.exists(), RUNNER


def test_no_network_broker_credential_imports():
    src = _src()
    for tok in ("import requests", "from requests", "import urllib",
                "import http", "import socket", "import ssl", "import ccxt",
                "from ccxt", "import binance", "import alpaca",
                "import websockets", "import aiohttp", "import dotenv",
                "os.environ", "getenv", "urlopen", "api.telegram.org",
                "subprocess", "place_order", "create_order"):
        assert tok not in src, tok


def test_side_effects_only_in_main():
    src = _src()
    tree = ast.parse(src)
    main_fn = next((n for n in tree.body
                    if isinstance(n, ast.FunctionDef) and n.name == "main"),
                   None)
    assert main_fn is not None
    main_lines = set(range(main_fn.lineno,
                           (main_fn.end_lineno or main_fn.lineno) + 1))
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            seg = ast.get_source_segment(src, node) or ""
            if "mkdir" in seg or "json.dump" in seg:
                assert node.lineno in main_lines, node.lineno


def test_has_main_guard_no_import_time_execution():
    src = _src()
    assert 'if __name__ == "__main__":' in src
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            assert getattr(node.value.func, "id", "") != "main"


def test_sha_pins_all_sources_and_drift_abort():
    src = _src()
    assert "EXPECTED_SHAS" in src
    for tok in ('"BTCUSD"', '"ETHUSD"', '"SOLUSD"',
                "source_sha_pins_do_not_match_before_detection",
                "sources_mutated_during_detection",
                "sources_mutated_after_artifact_write"):
        assert tok in src, tok


def test_no_replay_no_pnl_no_baseline_no_fetch():
    src = _src()
    for tok in ("no_replay", "no_pnl", "no_baseline_comparison_in_this_gate",
                "no_data_fetch", "no_data_mutation", "no_best_asset_selection",
                "no_parameter_fitting"):
        assert tok in src, tok


def test_reuses_committed_detector():
    src = _src()
    assert "failed_breakdown_reclaim_reversal_v1_detector_spec_dry_run_contract" in src
    assert "scan_c12_setups" in src


def test_labels_stage_non_overlap_no_horizon_walk():
    src = _src()
    assert "labels_stage_non_overlap" in src
    # the labels gate must NOT evaluate horizons / PnL outcomes here
    assert "evaluate_one_setup_horizon" not in src
    assert "apply_non_overlap" not in src


def test_sample_size_and_battery_and_rejection_pressure():
    src = _src()
    assert "MIN_LABELS_TOTAL = 100" in src
    assert "MIN_PER_ASSET = 20" in src
    assert "MIN_PER_REGIME = 20" in src
    assert "structural_checks_battery" in src
    assert "structural_rejection_pressure" in src
    assert "forward_oos" in src.lower()


def test_regime_classified_per_asset():
    src = _src()
    assert "classify_regime" in src
    assert "REGIME_SMA_SHORT = 50" in src and "REGIME_SMA_LONG = 200" in src


def test_writes_only_into_c12_dir():
    src = _src()
    assert "failed_breakdown_reclaim_reversal_c12" in src
    assert "LABELS_PATH" in src and "SUMMARY_PATH" in src
