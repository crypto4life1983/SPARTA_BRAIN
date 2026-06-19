"""Purity / safety tests for the C20 real-candle labels runner
tools/c20_real_candle_labels_once.py.

Verifies (by reading the source, NOT executing it): no side effects at import (file
writes only inside main()); no network / broker / credential / order / subprocess
reach; SHA-pins the 9 frozen PUBLIC BTC/ETH/SOL spot+perp+funding sources and aborts on
drift; reuses the FROZEN committed C20 detector primitives + params; produces
mechanically-neutral basis/funding-carry LABELS (per-asset setups, entry reasons
funding_carry/basis_convergence, exits, mechanical-neutrality counts, forward-OOS 2026
counts, turnover); applies NO replay / PnL / fee (37 bps + perp frictions reserved); no
XAUUSD; and writes only into the gitignored C20 labels dir."""
from __future__ import annotations

import ast
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = _REPO_ROOT / "tools" / "c20_real_candle_labels_once.py"


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
                "fapi.binance.com", "subprocess", "place_order", "create_order"):
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
    for tok in ('"BTCUSDT_spot"', '"BTCUSDT_perp"', '"BTCUSDT_funding"',
                '"SOLUSDT_perp"', "compute_sha256", "SOURCE SHA MISMATCH",
                "mismatch", "return 2"):
        assert tok in src, tok


def test_reuses_frozen_detector_primitives_and_params():
    src = _src()
    assert ("mechanically_neutral_spot_perp_basis_funding_carry_v1_"
            "detector_spec_dry_run_contract" in src)
    for tok in ("_d20._neutral_leg_weights", "_d20.BASIS_Z_WINDOW",
                "_d20.FUNDING_LOOKBACK", "_d20.ENTRY_BASIS_Z",
                "_d20.ENTRY_CARRY_BPS", "_d20.EXIT_BASIS_Z", "_d20.STOP_BASIS_Z",
                "_d20.MAX_GROSS", "_d20.MIN_SPACING",
                "_d20.FUNDING_ANNUALIZATION_DAYS"):
        assert tok in src, tok


def test_basis_and_funding_definitions_present():
    src = _src()
    # same-asset relative basis = (perp - spot) / spot
    assert "(perp[d] - spot[d]) / spot[d]" in src
    # funding aggregated to daily then annualized carry over the lookback
    assert "FUNDING_ANNUALIZATION_DAYS" in src
    assert "funding_rate" in src and "datetime" in src


def test_label_definitions_present():
    src = _src()
    for tok in ("setup_count", "entry_count", "entry_reason_counts",
                "exit_counts", "funding_carry", "basis_convergence",
                "convergence", "carry_decay", "negative_carry", "divergence_stop",
                "neutrality_break", "mechanical_neutral_pass",
                "forward_oos_entry_count", "max_concurrent_positions",
                "gross_cap_respected", "spacing_ok"):
        assert tok in src, tok


def test_no_replay_pnl_fee_optimization_xauusd():
    src = _src()
    for tok in ("no_replay_or_pnl", '"fee_applied": False',
                "all_in_round_trip_bps_reserved"):
        assert tok in src, tok
    # no replay / PnL / fee / baseline / optimization computation in the labels runner
    for banned in ("compute_pnl", "buy_and_hold", "sharpe", "calmar", "net_return",
                   "* 0.0037", "fee_bps *", "optimize", "param_sweep"):
        assert banned not in src, banned
    # no gold / XAUUSD: any such line must be a NO-XAUUSD disclaimer (negated)
    for line in src.splitlines():
        low = line.lower()
        if "xau" in low or "gold" in low:
            assert ("no_xau" in low or "no xau" in low or "no gold" in low
                    or "no_gold" in low), "non-negated gold/XAU line: %s" % line.strip()


def test_writes_only_into_c20_labels_dir():
    src = _src()
    assert "mechanically_neutral_spot_perp_basis_funding_carry_c20" in src
    assert "labels" in src
    assert "LABELS_PATH" in src and "SUMMARY_PATH" in src
    # the source data is read only from the frozen public spot/perp/funding raw dir
    assert "crypto_basis_funding_research" in src and "raw" in src
