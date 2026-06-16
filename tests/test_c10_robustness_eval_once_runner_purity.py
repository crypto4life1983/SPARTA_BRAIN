"""Purity / safety tests for the C10 robustness evaluation runner
tools/c10_robustness_eval_once.py.

Verifies the runner: imports with no side effects (writes only inside the
__main__-invoked main()); no network / broker / credential / order / scheduler
reach; SHA-pins the replay ledger/summary, labels, and source and aborts on
drift; declares no-relabel / no-weekday-change / no-parameter-fitting; stresses
costs at 37/50/75/100 bps and horizons 3/5/7/10; writes only into the gitignored
robustness_eval data dir. csv/hashlib/json/open are legitimate runner tools and
are NOT banned; network/broker reach IS."""
from __future__ import annotations

import ast
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = _REPO_ROOT / "tools" / "c10_robustness_eval_once.py"


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


def test_sha_pins_and_drift_abort_present():
    src = _src()
    for tok in ("EXPECTED_LEDGER_SHA", "EXPECTED_SUMMARY_SHA",
                "EXPECTED_LABELS_SHA", "EXPECTED_SOURCE_SHA",
                "input_sha_pins_do_not_match_before_robustness",
                "inputs_mutated_during_robustness_evaluation",
                "source_mutated_after_robustness_write"):
        assert tok in src, tok


def test_no_relabel_no_fit_no_weekday_change_no_optimization():
    src = _src()
    for tok in ("no_relabel", "no_parameter_fitting", "no_weekday_change",
                "no_detector_change", "no_downstream_gate_unlock"):
        assert tok in src, tok


def test_cost_and_horizon_stress_grid_declared():
    src = _src()
    assert "COST_STRESS_BPS = (37.0, 50.0, 75.0, 100.0)" in src
    assert "HORIZON_SENSITIVITY_BARS = (3, 5, 7, 10)" in src
    assert "CANONICAL_HORIZON_BARS = 5" in src
    assert "CANONICAL_ALL_IN_BPS = 37.0" in src


def test_writes_only_into_robustness_eval_dir():
    src = _src()
    assert "robustness_eval" in src
    assert "ROBUSTNESS_PATH" in src
    assert 'OUT_DIR = DATA_DIR / "robustness_eval"' in src


def test_scope_locks_present():
    src = _src()
    for lock in ("no_paper_trading", "no_live_trading", "no_broker",
                 "no_credentials", "no_order_logic", "no_portfolio_allocation",
                 "no_profitability_claim", "no_network", "no_fetch"):
        assert lock in src, lock
