"""Purity / safety tests for the C21 real-candle labels runner
tools/c21_real_candle_labels_once.py.

Verifies (by reading the source, NOT executing it): no side effects at import (file
writes only inside main()); no network / broker / credential / order / subprocess reach;
SHA-pins the 9 frozen PUBLIC sources and aborts on drift; REUSES the FROZEN committed C21
detector (run_detector + params -- no re-parameterization); produces low-turnover labels
(detected/accepted/rejected setups, round-trips, hold lengths, mechanical-neutrality,
forward-OOS); applies NO replay / PnL / fee (37/74 bps reserved); NO optimization /
tuning; NO basis-z / drawdown stop introduced; NOT a C20 rescue/retune; no XAUUSD; and
writes only into the gitignored C21 labels dir."""
from __future__ import annotations

import ast
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = _REPO_ROOT / "tools" / "c21_real_candle_labels_once.py"


def _src():
    return RUNNER.read_text(encoding="utf-8")


def test_runner_exists():
    assert RUNNER.exists(), RUNNER


def test_no_network_broker_credential_imports():
    src = _src()
    for tok in ("import requests", "from requests", "import urllib", "import http",
                "import socket", "import ssl", "import ccxt", "from ccxt",
                "import binance", "import alpaca", "import websockets",
                "import aiohttp", "import dotenv", "os.environ", "getenv", "urlopen",
                "api.binance.com", "fapi.binance.com", "subprocess", "place_order",
                "create_order"):
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


def test_sha_pins_nine_sources_and_drift_abort():
    src = _src()
    assert "EXPECTED_SOURCE_SHA256" in src
    for tok in ('"BTCUSDT_spot"', '"BTCUSDT_perp"', '"SOLUSDT_funding"',
                "compute_sha256", "SOURCE SHA MISMATCH",
                "actual_sha != EXPECTED_SOURCE_SHA256", "return 2"):
        assert tok in src, tok


def test_reuses_frozen_detector_no_reparameterization():
    src = _src()
    assert ("low_turnover_same_asset_spot_perp_funding_carry_v1_"
            "detector_spec_dry_run_contract" in src)
    # the labels runner REUSES the committed detector's pure run_detector + params
    assert "_d21.run_detector" in src
    for tok in ("_d21.CARRY_REGIME_WINDOW", "_d21.ENTER_CARRY_BPS",
                "_d21.MIN_HOLD_BARS", "_d21.REBALANCE_CADENCE",
                "_d21.MAX_ROUND_TRIPS_PER_YEAR"):
        assert tok in src, tok


def test_low_turnover_label_definitions_present():
    src = _src()
    for tok in ("detected_setup_count", "accepted_label_count",
                "rejected_label_count", "rejected_by_cadence",
                "rejected_by_turnover_ceiling", "round_trips", "round_trips_per_year",
                "avg_hold_bars", "mechanical_neutral_pass",
                "forward_oos_accepted_count", "durable_carry_regime_breakdown"):
        assert tok in src, tok


def test_no_replay_pnl_fee_optimization_basis_z_drawdown_xauusd():
    src = _src()
    for tok in ("no_replay_or_pnl", '"fee_applied": False',
                "all_in_round_trip_bps_reserved", "replay_remains_locked",
                '"uses_basis_z_stop": False', '"uses_drawdown_stop": False'):
        assert tok in src, tok
    for banned in ("compute_pnl", "buy_and_hold", "sharpe", "calmar", "net_return",
                   "optimize(", "param_sweep", "grid_search", "basis_z_stop = True",
                   "drawdown_stop = True"):
        assert banned not in src, banned
    # NOT a C20 rescue/retune
    assert '"is_rescue_or_retune_of_c20": False' in src
    assert '"c20_remains_rejected": True' in src
    # no gold / XAUUSD: any such line must be a NO-XAUUSD disclaimer (negated)
    for line in src.splitlines():
        low = line.lower()
        if "xau" in low or "gold" in low:
            assert ("no_xau" in low or "no xau" in low or "no gold" in low
                    or "no_gold" in low), "non-negated gold/XAU line: %s" % line.strip()


def test_writes_only_into_c21_labels_dir():
    src = _src()
    assert "low_turnover_same_asset_spot_perp_funding_carry_c21" in src
    assert "labels" in src
    assert "LABELS_PATH" in src and "SUMMARY_PATH" in src
    assert "crypto_basis_funding_research" in src and "raw" in src
