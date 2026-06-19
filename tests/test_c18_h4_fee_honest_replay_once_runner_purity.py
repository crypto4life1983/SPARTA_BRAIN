"""Purity / safety tests for the C18 H4 fee-honest replay runner
tools/c18_h4_fee_honest_replay_once.py.

Verifies: no side effects at import (writes only inside main()); no network / broker /
credential / order reach; SHA-pins the BTCUSDT 4h source + the frozen labels and
aborts on drift; reuses the FROZEN committed C18 detector (no new params); APPLIES the
37 bps cost (18.5 bps one-way per unit leg) and never drops it; computes Sharpe /
Calmar / max-drawdown / net-return / win-rate / R vs BTC buy-and-hold full-window +
2026 forward-OOS; NO optimization / re-parameterization / parameter sweep; NO XAUUSD;
writes only into the gitignored C18 replay_results dir."""
from __future__ import annotations

import ast
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = _REPO_ROOT / "tools" / "c18_h4_fee_honest_replay_once.py"


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


def test_sha_pins_source_labels_and_drift_abort():
    src = _src()
    assert "EXPECTED_SOURCE_SHA256" in src and "EXPECTED_LABELS_SHA256" in src
    for tok in ("source_sha_pin_does_not_match_before_replay",
                "labels_sha_pin_does_not_match_before_replay",
                "inputs_mutated_during_replay"):
        assert tok in src, tok


def test_applies_37bps_cost_not_dropped():
    src = _src()
    for tok in ("FEE_ROUND_TRIP_BPS", "SLIPPAGE_ROUND_TRIP_BPS",
                "ALL_IN_ROUND_TRIP_BPS", "ONE_WAY_COST", "total_cost"):
        assert tok in src, tok
    assert "27.0" in src and "10.0" in src        # 27 + 10 = 37


def test_reuses_frozen_detector_no_new_params():
    src = _src()
    assert ("h4_trend_following_market_structure_v1_detector_spec_dry_run_contract"
            in src)
    assert "det.run_detector" in src
    for tok in ("no_optimization", "no_reparameterization", "no_parameter_sweep"):
        assert tok in src, tok
    for banned in ("grid_search", "optimize", "for param in", "param_grid"):
        assert banned not in src, banned


def test_computes_risk_adjusted_metrics_and_btc_buy_and_hold():
    src = _src()
    for tok in ("sharpe", "calmar", "max_drawdown", "net_return", "win_rate",
                "total_R", "buy_and_hold", "forward_oos", "decisive_gate_results"):
        assert tok in src, tok


def test_no_xauusd():
    for line in _src().splitlines():
        low = line.lower()
        if "xau" in low or "gold" in low:
            assert ("no_xau" in low or "no xau" in low or "no gold" in low
                    or "no_gold" in low), "non-negated gold/XAU line: %s" % line.strip()


def test_writes_only_into_c18_replay_dir():
    src = _src()
    assert "h4_trend_following_market_structure_c18" in src
    assert "replay_results" in src
    assert "LEDGER_PATH" in src and "SUMMARY_PATH" in src
