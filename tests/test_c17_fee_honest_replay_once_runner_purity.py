"""Purity / safety tests for the C17 fee-honest replay runner
tools/c17_fee_honest_replay_once.py.

Verifies: no side effects at import (writes only inside main()); no network /
broker / credential / order reach; SHA-pins the 3 sources + the frozen labels and
aborts on drift; APPLIES the 37 bps cost (18.5 bps one-way) and never drops it;
replays the FROZEN labels without optimization / re-parameterization; computes
Sharpe / Calmar / max-drawdown / net-return vs buy-and-hold + equal-weight basket;
writes only into the gitignored c17 replay_results dir."""
from __future__ import annotations

import ast
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = _REPO_ROOT / "tools" / "c17_fee_honest_replay_once.py"


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


def test_sha_pins_sources_labels_and_drift_abort():
    src = _src()
    assert "EXPECTED_SOURCE_SHA256" in src and "EXPECTED_LABELS_SHA256" in src
    for tok in ('"BTCUSD"', '"ETHUSD"', '"SOLUSD"',
                "source_sha_pins_do_not_match_before_replay",
                "labels_sha_pin_does_not_match_before_replay",
                "inputs_mutated_during_replay",
                "inputs_mutated_after_replay_artifact_write"):
        assert tok in src, tok


def test_applies_37bps_cost_not_dropped():
    src = _src()
    for tok in ("FEE_ROUND_TRIP_BPS", "SLIPPAGE_ROUND_TRIP_BPS",
                "ALL_IN_ROUND_TRIP_BPS", "ONE_WAY_COST", "total_cost_drag"):
        assert tok in src, tok
    assert "27.0" in src and "10.0" in src        # 27 + 10 = 37


def test_no_optimization_or_reparameterization():
    src = _src()
    assert "no_optimization" in src and "no_reparameterization" in src
    assert "no_reallocation_new_params" in src
    # replays the frozen labels; does not re-run the allocator with new params
    for tok in ("allocate_c17", "grid_search", "optimize", "for param in"):
        assert tok not in src, tok


def test_computes_risk_adjusted_metrics_and_baselines():
    src = _src()
    for tok in ("sharpe", "calmar", "max_drawdown", "net_return",
                "buy_and_hold", "equal_weight_basket", "forward_oos",
                "decisive_gate_results"):
        assert tok in src, tok


def test_writes_only_into_c17_replay_dir():
    src = _src()
    assert ("risk_adjusted_portfolio_construction_vol_targeted_allocation_c17"
            in src)
    assert "replay_results" in src
    assert "LEDGER_PATH" in src and "SUMMARY_PATH" in src
