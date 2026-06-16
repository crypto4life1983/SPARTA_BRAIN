"""Purity / safety tests for the C10 generalization runner
tools/c10_cross_asset_cross_weekday_forward_oos_eval_once.py.

Verifies: no side effects at import (writes only inside the __main__-invoked
main()); no network / broker / credential / order / scheduler reach; SHA-pins
all three (BTC/ETH/SOL) frozen sources and aborts on drift; reuses the committed
detector geometry primitives; does NOT call select_favorable_weekday_bucket (no
in-sample weekday re-optimization); scans all 7 weekdays for cross-weekday;
self-validates the 156 BTC-Friday OOS count; writes only into the gitignored
generalization dir. csv/hashlib/json/datetime/open are legitimate runner tools
and are NOT banned; network/broker reach IS."""
from __future__ import annotations

import ast
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = (_REPO_ROOT / "tools"
               / "c10_cross_asset_cross_weekday_forward_oos_eval_once.py")


def _src():
    return RUNNER_PATH.read_text(encoding="utf-8")


def test_runner_exists():
    assert RUNNER_PATH.exists(), RUNNER_PATH


def test_no_network_broker_credential_imports():
    src = _src()
    forbidden = (
        "import requests", "from requests", "import urllib", "from urllib",
        "import http", "from http", "import socket", "import ssl",
        "import ccxt", "from ccxt", "import alpaca", "from alpaca",
        "import binance", "from binance", "import websockets", "import aiohttp",
        "import schedule", "import apscheduler", "import telegram",
        "import smtplib", "import dotenv", "from dotenv",
        "os.environ", "getenv", "urlopen", "api.telegram.org", "subprocess",
    )
    for tok in forbidden:
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
                assert node.lineno in main_lines, (
                    "write call outside main(): line %d" % node.lineno)


def test_has_main_guard_no_import_time_execution():
    src = _src()
    assert 'if __name__ == "__main__":' in src
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            assert getattr(node.value.func, "id", "") != "main"


def test_sha_pins_all_three_sources_and_drift_abort():
    src = _src()
    assert "EXPECTED_SHAS" in src
    for sym in ('"BTC"', '"ETH"', '"SOL"'):
        assert sym in src
    assert "source_sha_pin_mismatch" in src
    assert "sources_mutated_during_generalization" in src
    assert "sources_mutated_after_write" in src


def test_no_weekday_reselection_no_optimizer_call():
    """The in-sample optimizer must NOT be invoked (no weekday re-fit).
    Check for an actual CALL (`name(`), not the docstring mention."""
    src = _src()
    assert "select_favorable_weekday_bucket(" not in src
    # also assert no AST Call to that optimizer
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            n = (node.func.attr if isinstance(node.func, ast.Attribute)
                 else getattr(node.func, "id", ""))
            assert n != "select_favorable_weekday_bucket", "optimizer called"
    assert "INHERITED_FRIDAY_BUCKET = 5" in src
    for tok in ("no_weekday_reselection", "no_parameter_fitting",
                "no_optimization", "no_best_cell_selected_as_promotion",
                "no_relabel"):
        assert tok in src, tok


def test_reuses_committed_detector_primitives():
    src = _src()
    assert "intraweek_calendar_seasonality_drift_v1_detector_spec_dry_run_contract" in src
    for prim in ("_precompute_atr", "compute_stop", "geometry_floor_by_variant",
                 "apply_anti_cluster_filter"):
        assert prim in src, prim


def test_all_seven_weekdays_and_self_validation():
    src = _src()
    assert "ALL_WEEKDAYS = (1, 2, 3, 4, 5, 6, 7)" in src
    assert "EXPECTED_BTC_FRIDAY_OOS_ACCEPTED = 156" in src
    assert "self_validation_failed_btc_friday_oos" in src


def test_windows_and_cost_inherited():
    src = _src()
    assert 'OOS_WINDOW = ("2023-01-01", "2025-12-31")' in src
    assert 'FORWARD_WINDOW = ("2026-01-01", "2026-06-08")' in src
    assert "ALL_IN_BPS = 37.0" in src


def test_writes_only_into_generalization_dir():
    src = _src()
    assert "cross_asset_weekday_forward_oos" in src
    assert "OUT_PATH" in src


def test_scope_locks_present():
    src = _src()
    for lock in ("no_paper_trading", "no_live_trading", "no_broker",
                 "no_credentials", "no_order_logic", "no_portfolio_allocation",
                 "no_profitability_claim", "no_network", "no_fetch"):
        assert lock in src, lock
