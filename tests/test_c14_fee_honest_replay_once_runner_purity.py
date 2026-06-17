"""Purity / safety tests for the C14 fee-honest replay runner
tools/c14_fee_honest_replay_once.py.

Verifies: no side effects at import (writes only inside main()); no network /
broker / credential / order reach; SHA-pins the labels artifact + all three
sources and aborts on drift; reuses the FROZEN labels artifact (no relabel, no
detector re-scan); 37 bps cost split; matched buy-and-hold + deterministic
random-entry baselines; horizon-exit cap; forward-OOS; writes only into the
gitignored c14 replay-results dir."""
from __future__ import annotations

import ast
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = _REPO_ROOT / "tools" / "c14_fee_honest_replay_once.py"


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


def test_sha_pins_labels_and_all_sources_and_drift_abort():
    src = _src()
    assert "EXPECTED_LABELS_SHA" in src and "EXPECTED_SOURCE_SHA" in src
    for tok in ('"BTCUSD"', '"ETHUSD"', '"SOLUSD"',
                "source_sha_pins_do_not_match_before_replay",
                "labels_sha_pin_does_not_match_before_replay",
                "inputs_mutated_during_replay",
                "inputs_mutated_after_replay_artifact_write"):
        assert tok in src, tok


def test_reuses_frozen_labels_no_relabel_no_detector_rescan():
    src = _src()
    assert "c14_detector_labels.json" in src
    assert "accepted_labels" in src
    assert "scan_c14_setups" not in src


def test_cost_split_and_baselines():
    src = _src()
    assert "FEE_ROUND_TRIP_BPS = 27.0" in src
    assert "SLIPPAGE_ROUND_TRIP_BPS = 10.0" in src
    assert "buy_and_hold" in src.lower()
    assert "random_entry" in src.lower()
    assert "RANDOM_MASTER_SEED" in src


def test_decisive_gate_terms_present():
    src = _src()
    for tok in ("horizon_exit_share", "target_capture_dominates",
                "regime_symmetry", "forward_oos", "beats_random_entry",
                "beats_buy_and_hold", "structural_rejection_pressure"):
        assert tok in src, tok


def test_no_optimization_no_one_edit():
    src = _src()
    assert "no_parameter_optimization" in src
    assert "no_one_edit_allowance_used" in src


def test_writes_only_into_c14_replay_dir():
    src = _src()
    assert "conviction_bar_follow_through_c14" in src
    assert "replay_results" in src
    assert "REPLAY_LEDGER_PATH" in src and "REPLAY_SUMMARY_PATH" in src
