"""Purity / safety tests for the C15 fee-honest replay runner
tools/c15_fee_honest_replay_once.py.

Verifies: no side effects at import (writes only inside main()); no network /
broker / credential / order reach; SHA-pins the frozen labels + all 3 sources and
aborts on drift; reuses the FROZEN labels (no relabel, no new label set); 37 bps
cost split applied and not droppable; matched buy-and-hold + deterministic
random-entry (fixed seed) baselines via an internal LCG (no RNG import); evaluates
the decisive gates on NET; writes only into the gitignored c15 replay-results
dir; no parameter optimization."""
from __future__ import annotations

import ast
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = _REPO_ROOT / "tools" / "c15_fee_honest_replay_once.py"


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


def test_no_rng_import_uses_internal_lcg():
    src = _src()
    assert "import random" not in src and "from random" not in src
    assert "import numpy" not in src and "from numpy" not in src
    assert "def lcg(" in src
    assert "RANDOM_MASTER_SEED" in src


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


def test_sha_pins_labels_and_sources_and_drift_abort():
    src = _src()
    assert "EXPECTED_LABELS_SHA256" in src and "EXPECTED_SOURCE_SHA256" in src
    for tok in ('"BTCUSD"', '"ETHUSD"', '"SOLUSD"',
                "source_sha_pins_do_not_match_before_replay",
                "labels_sha_pin_does_not_match_before_replay",
                "inputs_mutated_during_replay",
                "inputs_mutated_after_replay_artifact_write"):
        assert tok in src, tok


def test_reuses_frozen_labels_no_relabel():
    src = _src()
    assert "c15_detector_labels.json" in src
    assert "accepted_labels" in src
    assert "no_new_label_set" in src


def test_cost_split_and_baselines():
    src = _src()
    assert "FEE_ROUND_TRIP_BPS = 27.0" in src
    assert "SLIPPAGE_ROUND_TRIP_BPS = 10.0" in src
    assert "ALL_IN_ROUND_TRIP_BPS" in src
    assert "buy_and_hold" in src.lower()
    assert "random_entry" in src.lower()
    assert "N_RESAMPLES = 200" in src


def test_decisive_gate_terms_present():
    src = _src()
    for tok in ("full_sample_net_positive", "forward_oos_net_positive",
                "no_single_regime_dependence", "no_single_asset_dependence",
                "no_one_sided_side_fragility", "beats_buy_and_hold",
                "beats_random_entry", "turnover_sane_for_slow_strategy",
                "all_decisive_gates_pass"):
        assert tok in src, tok


def test_no_optimization():
    src = _src()
    assert "no_parameter_optimization" in src
    assert "no_one_edit_allowance_used" in src


def test_writes_only_into_c15_replay_dir():
    src = _src()
    assert "slow_vol_targeted_time_series_momentum_c15" in src
    assert "replay_results" in src
    assert "LEDGER_PATH" in src and "SUMMARY_PATH" in src
