"""Purity / safety tests for the C17 real-candle allocation-labels runner
tools/c17_real_candle_allocation_once.py.

Verifies: no side effects at import (writes only inside main()); no network /
broker / credential / order reach; SHA-pins the 3 sources and aborts on drift;
reuses the FROZEN committed C17 allocator (allocate_c17 + its params); produces
weekly long/flat allocation labels; runs the structural gate (rebalances /
long-only / gross-capped / vol-target / forward-OOS) and reports turnover; computes
NO replay / backtest / PnL / cost / baseline / optimization; writes only into the
gitignored c17 allocation-labels dir."""
from __future__ import annotations

import ast
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = _REPO_ROOT / "tools" / "c17_real_candle_allocation_once.py"


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


def test_reuses_frozen_allocator_primitives():
    src = _src()
    assert ("risk_adjusted_portfolio_construction_vol_targeted_allocation_v1_"
            "detector_spec_dry_run_contract") in src
    for tok in ("det.allocate_c17", "det.VOL_LOOKBACK", "det.TARGET_VOL",
                "det.MAX_GROSS", "det.NO_TRADE_BAND",
                "det.MAX_AVG_WEEKLY_TURNOVER"):
        assert tok in src, tok


def test_allocator_labels_and_structural_gate():
    src = _src()
    for tok in ("weekly_rebalance_long_flat_allocation_observation",
                "MIN_REBALANCES", "all_weights_long_only", "gross_never_exceeds_cap",
                "vol_target_active", "forward_oos_populated", "avg_weekly_turnover",
                "turnover_within_cap", "structural_review"):
        assert tok in src, tok


def test_no_replay_pnl_cost_baseline_optimization():
    src = _src()
    for tok in ("no_replay", "no_backtest", "no_pnl", "no_cost_application",
                "no_baseline", "no_optimization", "no_auto_trading"):
        assert tok in src, tok
    # no actual return/PnL/baseline computation in this gate
    for tok in ("compute_pnl", "buy_and_hold", "equal_weight_basket",
                "net_return", "sharpe", "calmar"):
        assert tok not in src, tok


def test_writes_only_into_c17_labels_dir():
    src = _src()
    assert ("risk_adjusted_portfolio_construction_vol_targeted_allocation_c17"
            in src)
    assert "allocation_labels" in src
    assert "LABELS_PATH" in src and "SUMMARY_PATH" in src
