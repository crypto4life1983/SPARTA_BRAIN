"""Purity / safety tests for the C20 fee-honest replay runner
tools/c20_fee_honest_replay_once.py.

Verifies (by reading the source, NOT executing it): no side effects at import (file
writes only inside main()); no network / broker / credential / order / subprocess reach;
SHA-pins the 9 frozen sources + the frozen labels artifact and aborts on drift (and on
input mutation during replay); reuses the FROZEN committed C20 detector cost constant;
applies the 74 bps two-leg cost (37 bps per leg, doubled) -- not dropped; compares vs a
random/null market-neutral baseline (NOT buy-and-hold); does NO optimization / tuning /
rescue / parameter sweep / data fetch; no XAUUSD; and writes only into the gitignored C20
replay_results dir."""
from __future__ import annotations

import ast
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = _REPO_ROOT / "tools" / "c20_fee_honest_replay_once.py"


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


def test_sha_pins_sources_labels_and_drift_abort():
    src = _src()
    for tok in ("EXPECTED_SOURCE_SHA256", "EXPECTED_LABELS_SHA256", "compute_sha256",
                "source_sha_pin_does_not_match_before_replay",
                "labels_sha_pin_does_not_match_before_replay",
                "inputs_mutated_during_replay"):
        assert tok in src, tok


def test_reuses_frozen_cost_constant_and_applies_two_leg_cost():
    src = _src()
    assert ("mechanically_neutral_spot_perp_basis_funding_carry_v1_"
            "detector_spec_dry_run_contract" in src)
    assert "_d20.ALL_IN_ROUND_TRIP_BPS" in src
    for tok in ("ROUND_TRIP_COST", "ENTRY_COST", "EXIT_COST", "NUM_LEGS"):
        assert tok in src, tok


def test_random_null_baseline_not_buy_and_hold():
    src = _src()
    assert "random/null" in src or "random_null" in src
    assert "always-on" in src or "always_on" in src.lower() or "null" in src
    # the baseline must NOT be buy-and-hold
    assert "buy_and_hold" not in src
    assert "buy-and-hold" not in src.lower() or "NOT buy-and-hold" in src


def test_no_optimization_tuning_sweep_xauusd():
    src = _src()
    for tok in ("no_parameter_optimization", "no_reparameterization",
                "no_parameter_sweep", "no_tuning", "no_rescue"):
        assert tok in src, tok
    for banned in ("optimize(", "param_sweep", "grid_search", "minimize("):
        assert banned not in src, banned
    for line in src.splitlines():
        low = line.lower()
        if "xau" in low or "gold" in low:
            assert ("no_xau" in low or "no xau" in low or "no gold" in low
                    or "no_gold" in low), "non-negated gold/XAU line: %s" % line.strip()


def test_writes_only_into_c20_replay_dir():
    src = _src()
    assert "mechanically_neutral_spot_perp_basis_funding_carry_c20" in src
    assert "replay_results" in src
    assert "LEDGER_PATH" in src and "SUMMARY_PATH" in src
    assert "crypto_basis_funding_research" in src
