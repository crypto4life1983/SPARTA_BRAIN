"""Purity / safety tests for the C11 fee-honest replay runner
tools/c11_fee_honest_replay_once.py.

Verifies: no side effects at import (writes only inside main()); no network /
broker / credential / order reach; SHA-pins the labels artifact + all three
sources and aborts on drift; reuses the FROZEN labels artifact (no relabel, no
detector re-run); the human-fixed 5-bar horizon is declared as NOT
spec-pre-declared; conservative stop-first straddle; per-asset reduce-or-keep
non-overlap; computes net fee-only AND all-in R with the 37 bps cost split;
records forward-OOS + worst-losing-streak; writes only into the gitignored c11
replay-results dir. csv/hashlib/json/open are legitimate runner tools; network/
broker reach is NOT.
"""
from __future__ import annotations

import ast
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = _REPO_ROOT / "tools" / "c11_fee_honest_replay_once.py"


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
                "inputs_mutated_during_replay_evaluation",
                "inputs_mutated_after_replay_artifact_write"):
        assert tok in src, tok


def test_reuses_frozen_labels_no_relabel_no_detector_rerun():
    src = _src()
    assert "c11_detector_labels.json" in src
    assert "accepted_labels" in src
    # The runner must NOT import/run the detector scanner (no relabel).
    assert "scan_c11_setups" not in src
    assert "detector_spec_dry_run_contract" not in src


def test_human_fixed_horizon_declared_not_spec_predeclared():
    src = _src()
    assert "HOLDING_HORIZON_BARS = 5" in src
    assert "spec_predeclared_horizon" in src
    assert "human_fixed_at_replay_gate_spec_did_not_predeclare" in src
    assert "no_horizon_optimization" in src


def test_conservative_straddle_and_per_asset_non_overlap():
    src = _src()
    assert "stop_first_conservative_miss" in src
    assert "per_asset_reduce_or_keep_only_never_add" in src


def test_cost_split_and_net_r_columns():
    src = _src()
    assert "FEE_ROUND_TRIP_BPS = 27.0" in src
    assert "SLIPPAGE_ROUND_TRIP_BPS = 10.0" in src
    assert "net_r_fee_only" in src and "net_r_all_in" in src


def test_records_forward_oos_and_worst_streak():
    src = _src()
    assert "forward_oos" in src.lower()
    assert "worst_losing_streak" in src
    assert "per_regime_net_all_in" in src and "per_asset_net_all_in" in src


def test_writes_only_into_c11_replay_dir():
    src = _src()
    assert "cross_asset_dispersion_reversion_c11" in src
    assert "replay_results" in src
    assert "REPLAY_LEDGER_PATH" in src and "REPLAY_SUMMARY_PATH" in src
