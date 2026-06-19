"""Purity / safety tests for the C19 real-candle labels runner
tools/c19_real_candle_labels_once.py.

Verifies (by reading the source, NOT executing it): no side effects at import (file
writes only inside main()); no network / broker / credential / order / subprocess
reach; SHA-pins the cached BTC/ETH/SOL D1 sources and aborts on drift; reuses the
FROZEN committed C19 detector primitives + params; produces market-neutral
relative-value LABELS (neutrality pass/fail, setups, entries/exits/stops, turnover,
structural counts); applies NO replay / PnL / fee (37 bps reserved); no XAUUSD; and
writes only into the gitignored C19 labels dir."""
from __future__ import annotations

import ast
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = _REPO_ROOT / "tools" / "c19_real_candle_labels_once.py"


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


def test_sha_pins_sources_and_drift_abort():
    src = _src()
    assert "EXPECTED_SOURCE_SHA256" in src
    for tok in ('"BTCUSD"', '"ETHUSD"', '"SOLUSD"', "compute_sha256",
                "SOURCE SHA MISMATCH", "actual_sha != EXPECTED_SOURCE_SHA256"):
        assert tok in src, tok


def test_reuses_frozen_detector_primitives():
    src = _src()
    assert ("oos_validated_beta_neutral_cross_sectional_relative_value_v1_"
            "detector_spec_dry_run_contract" in src)
    for tok in ("_d19._ols_beta_2", "_d19._residual_series",
                "_d19._net_beta_to_basket", "_d19._normalized_leg_weights",
                "_d19.BETA_WINDOW", "_d19.OOS_WINDOW", "_d19.BETA_TOL",
                "_d19.ENTRY_Z", "_d19.STOP_Z", "_d19.MIN_SPACING"):
        assert tok in src, tok


def test_label_definitions_present():
    src = _src()
    for tok in ("neutrality_pass", "neutrality_fail", "setup_count", "entry_count",
                "exit_counts", "neutrality_break", "divergence_stop",
                "mean_reversion", "max_concurrent_positions", "gross_cap_respected",
                "spacing_ok"):
        assert tok in src, tok


def test_no_replay_pnl_fee_optimization_xauusd():
    src = _src()
    for tok in ("no_replay_or_pnl", '"fee_applied": False',
                "all_in_round_trip_bps_reserved"):
        assert tok in src, tok
    # no replay / PnL / fee / baseline computation in the labels runner
    for banned in ("compute_pnl", "buy_and_hold", "sharpe", "calmar", "net_return",
                   "* 0.0037", "fee_bps *"):
        assert banned not in src, banned
    # no gold / XAUUSD: any such line must be a NO-XAUUSD disclaimer (negated)
    for line in src.splitlines():
        low = line.lower()
        if "xau" in low or "gold" in low:
            assert ("no_xau" in low or "no xau" in low or "no gold" in low
                    or "no_gold" in low), "non-negated gold/XAU line: %s" % line.strip()


def test_writes_only_into_c19_labels_dir():
    src = _src()
    assert "oos_validated_beta_neutral_cross_sectional_relative_value_c19" in src
    assert "labels" in src
    assert "LABELS_PATH" in src and "SUMMARY_PATH" in src
    # the source data is read only from the cached crypto_d1_spot raw dir
    assert "crypto_d1_spot" in src and "raw" in src
