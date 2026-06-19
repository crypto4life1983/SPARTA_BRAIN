"""Purity / safety tests for the C18 H4 real-candle labels runner
tools/c18_h4_real_candle_labels_once.py.

Verifies: no side effects at import (writes only inside main()); no network / broker /
credential / order reach; SHA-pins the BTCUSDT 4h source and aborts on drift; reuses
the FROZEN committed C18 detector (run_detector + its params); produces long
market-structure setup labels; runs the structural gate (labels / long-only /
max-units / non-overlap / structural stops / spacing / forward-OOS); applies NO
replay / PnL / fee; no XAUUSD; writes only into the gitignored C18 H4 labels dir."""
from __future__ import annotations

import ast
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = _REPO_ROOT / "tools" / "c18_h4_real_candle_labels_once.py"


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
                "os.environ", "getenv", "urlopen", "api.binance.com",
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


def test_sha_pins_source_and_drift_abort():
    src = _src()
    assert "EXPECTED_SOURCE_SHA256" in src
    for tok in ('"BTCUSD"', "source_sha_pin_does_not_match_before_labeling",
                "source_mutated_during_labeling"):
        assert tok in src, tok


def test_reuses_frozen_detector_primitives():
    src = _src()
    assert ("h4_trend_following_market_structure_v1_detector_spec_dry_run_contract"
            in src)
    for tok in ("det.run_detector", "det.MAX_UNITS", "det.MIN_SPACING",
                "det.STOP_BUFFER_FRAC", "det.K"):
        assert tok in src, tok


def test_structural_gate_and_label_definition():
    src = _src()
    for tok in ("long_market_structure_trend_setup_with_pyramids", "MIN_LABELS_TOTAL",
                "all_long_only", "max_units_ok", "one_position_per_symbol",
                "structural_stops_below_anchor", "spacing_min_6_bars",
                "forward_oos_populated", "structural_review"):
        assert tok in src, tok


def test_no_replay_pnl_fee_optimization_xauusd():
    src = _src()
    for tok in ("no_replay", "no_pnl", "no_fee_application", "no_optimization",
                "no_xauusd"):
        assert tok in src, tok
    # no replay/PnL/fee computation
    for banned in ("compute_pnl", "buy_and_hold", "sharpe", "calmar", "net_return",
                   "fee_bps *", "* 0.0037"):
        assert banned not in src, banned
    # the only crypto symbol the labels runner reads is BTCUSD/BTCUSDT; any xau/gold
    # line must be a NO-XAUUSD disclaimer (negated)
    assert 'SYMBOL = "BTCUSD"' in src
    for line in src.splitlines():
        low = line.lower()
        if "xau" in low or "gold" in low:
            negated = ("no_xau" in low or "no xau" in low or "no gold" in low
                       or "no_gold" in low)
            assert negated, "non-negated gold/XAU line: %s" % line.strip()


def test_writes_only_into_c18_h4_labels_dir():
    src = _src()
    assert "h4_trend_following_market_structure_c18" in src
    assert "labels" in src
    assert "LABELS_PATH" in src and "SUMMARY_PATH" in src
