"""Purity / safety tests for the C15 real-candle labels runner
tools/c15_real_candle_detection_once.py.

Verifies: no side effects at import (writes only inside main()); no network /
broker / credential / order reach; SHA-pins the 3 sources and aborts on drift;
reuses the FROZEN committed C15 detector (no re-implementation); extracts entry-
event labels; runs the structural sample-size gate; computes NO replay / PnL / cost
/ baseline; writes only into the gitignored c15 detector-labels dir."""
from __future__ import annotations

import ast
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = _REPO_ROOT / "tools" / "c15_real_candle_detection_once.py"


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
                    if isinstance(n, ast.FunctionDef) and n.name == "main"), None)
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


def test_sha_pins_sources_and_drift_abort():
    src = _src()
    assert "EXPECTED_SHAS" in src
    for tok in ('"BTCUSD"', '"ETHUSD"', '"SOLUSD"',
                "source_sha_pins_do_not_match_before_detection",
                "sources_mutated_during_detection",
                "sources_mutated_after_artifact_write"):
        assert tok in src, tok


def test_reuses_frozen_detector_no_reimplementation():
    src = _src()
    assert "slow_vol_targeted_time_series_momentum_v1_detector_spec_dry_run_contract" in src  # noqa: E501
    assert "det.scan_c15_states" in src
    assert "accepted_labels" in src


def test_entry_label_definition_and_structural_gate():
    src = _src()
    assert "extract_entry_labels" in src
    assert "state_transition_into_active_position_entry_event" in src
    for tok in ("MIN_LABELS_TOTAL", "MIN_PER_ASSET", "MIN_PER_REGIME",
                "forward_oos_populated", "structural_rejection_pressure",
                "sample_size"):
        assert tok in src, tok


def test_no_replay_pnl_cost_baseline():
    src = _src()
    assert "no_replay" in src and "no_pnl" in src
    assert "no_cost_application" in src
    assert "no_baseline_comparison_in_this_gate" in src
    assert "no_parameter_fitting" in src
    # no profit / PnL computation tokens
    for tok in ("net_r", "compute_pnl", "buy_and_hold", "random_entry"):
        assert tok not in src, tok


def test_writes_only_into_c15_labels_dir():
    src = _src()
    assert "slow_vol_targeted_time_series_momentum_c15" in src
    assert "detector_labels" in src
    assert "LABELS_PATH" in src and "SUMMARY_PATH" in src
