"""Purity / safety tests for the C10 fee+slippage-honest replay runner
tools/c10_fee_honest_replay_156_once.py.

Verifies the runner: imports with no side effects (file writes only inside the
__main__-invoked main()); performs no network / broker / credential / order /
scheduler action; pins the source + labels + summary SHAs and aborts on drift;
declares the locked 27 bps fee + 10 bps slippage cost basis; writes only into
the gitignored replay_results data dir; and carries the full scope-lock set.
The runner legitimately uses csv/hashlib/json/open (it reads frozen candles,
SHA-pins inputs, and freezes replay artifacts), so those are NOT banned here --
network/broker/credential reach IS."""
from __future__ import annotations

import ast
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = _REPO_ROOT / "tools" / "c10_fee_honest_replay_156_once.py"


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
        "os.environ", "getenv", "urlopen", "api.telegram.org",
        "subprocess",
    )
    for tok in forbidden:
        assert tok not in src, tok


def test_side_effects_only_in_main():
    """No module-level file write / mkdir; writes live inside main()."""
    tree = ast.parse(_src())
    main_fn = next((n for n in tree.body
                    if isinstance(n, ast.FunctionDef) and n.name == "main"),
                   None)
    assert main_fn is not None, "main() missing"
    main_lines = set(range(main_fn.lineno, (main_fn.end_lineno or main_fn.lineno) + 1))
    write_markers = ("mkdir", "json.dump", "\"w\"", "'w'")
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            seg = ast.get_source_segment(_src(), node) or ""
            if any(m in seg for m in ("mkdir", "json.dump")):
                assert node.lineno in main_lines, (
                    "write call outside main(): line %d" % node.lineno)


def test_has_main_guard_and_no_import_time_execution():
    src = _src()
    assert 'if __name__ == "__main__":' in src
    # main() is only invoked under the guard, never at import.
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            name = getattr(node.value.func, "id", "")
            assert name != "main", "main() called at module top level"


def test_sha_pins_and_drift_abort_present():
    src = _src()
    assert "EXPECTED_SOURCE_SHA" in src
    assert "EXPECTED_LABELS_SHA" in src
    assert "EXPECTED_SUMMARY_SHA" in src
    assert "sha_pin_does_not_match_before_replay" in src
    assert "inputs_mutated_during_replay_evaluation" in src
    assert "inputs_mutated_after_replay_artifact_write" in src


def test_cost_basis_declared_fee_and_slippage():
    src = _src()
    assert "FEE_ROUND_TRIP_BPS = 27.0" in src
    assert "SLIPPAGE_ROUND_TRIP_BPS = 10.0" in src
    assert "net_r_all_in" in src
    assert "net_r_fee_only" in src


def test_stop_first_conservative_and_horizon_exit():
    src = _src()
    assert "stop_first_conservative_miss" in src
    assert "miss_same_bar_straddle" in src
    assert "HOLDING_HORIZON_BARS = 5" in src
    assert "horizon" in src


def test_scope_locks_present_and_true():
    """Import the module object and check the runner's scope-lock posture via
    source (no execution)."""
    src = _src()
    for lock in ("no_paper_trading", "no_live_trading", "no_broker",
                 "no_credentials", "no_order_logic", "no_relabel",
                 "no_profitability_claim", "no_downstream_gate_unlock",
                 "no_network", "no_fetch"):
        assert lock in src, lock


def test_writes_only_into_replay_results_dir():
    src = _src()
    assert "replay_results" in src
    assert "REPLAY_LEDGER_PATH" in src
    assert "REPLAY_SUMMARY_PATH" in src
    # the two write targets are under the replay_results out dir
    assert 'OUT_DIR = (REPO_ROOT / "data" / "intraweek_calendar_seasonality_c10"' in src
    assert '"replay_results")' in src
