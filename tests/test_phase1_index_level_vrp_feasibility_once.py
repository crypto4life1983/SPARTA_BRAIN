"""Determinism + purity tests for the Phase-1 index-level VRP feasibility evaluator.

Proves the evaluator reads ONLY the frozen local DVOL + spot dirs; imports NO network/fetch
libs and uses NO private/signed/account/order/trade endpoints; runs NO option-trading
simulation (no straddle/strangle/delta-hedge P&L); uses fixed forward windows 7/14/30 only;
is deterministic; covers BTC/ETH only; and discloses the March-2020 DVOL gap. Data-dependent
checks skip if the gitignored frozen data is absent."""
from __future__ import annotations

import ast
import math
from pathlib import Path

import pytest

import tools.phase1_index_level_vrp_feasibility_once as ev


def test_reads_only_frozen_dirs():
    assert ev.DVOL_RAW.as_posix().endswith("data/deribit_iv_universe/raw")
    assert ev.OHLCV_RAW.as_posix().endswith("data/broad_crypto_universe_c23_c24/raw")


def test_fixed_windows_and_btc_eth_only():
    assert ev.FWD_WINDOWS == (7, 14, 30)
    assert ev.MAIN_WINDOW == 30
    assert ev.CURRENCIES == ("BTC", "ETH")
    assert ev.MARCH_2020_COVERED is False


def test_module_purity_no_network_no_trading_sim():
    src = Path(ev.__file__).read_text(encoding="utf-8")
    doc = ast.get_docstring(ast.parse(src)) or ""
    low = src.replace(doc, "").lower()
    # actionable network / endpoint / trading-sim markers must be ABSENT (descriptive docstring
    # prose like "NO straddle ... simulation" is stripped above)
    for bad in ("urllib", "requests", "socket", "http", "fetch", "urlopen", "/private/",
                "/public/", "deribit.com", "place_order", "straddle_pnl", "delta_hedge(",
                "strangle_pnl", "api_key"):
        assert bad not in low, bad
    tree = ast.parse(src)
    banned = {"urllib", "requests", "socket", "http", "ccxt", "subprocess", "numpy",
              "pandas", "telegram"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned), imported & banned


def test_realized_vol_helper_correct():
    # constant +1%/day -> zero realized vol; forward window strictly after each date
    closes = {f"2021-03-{i:02d}": 100.0 * (1.01 ** (i - 24)) for i in range(24, 31)}
    rv = ev._fwd_realized_vol(closes, 3)
    assert all(abs(v) < 1e-6 for v in rv.values())  # constant growth -> ~0 vol
    # summary helper
    s = ev._summ([1.0, -2.0, 3.0])
    assert s["hit_rate"] == 2 / 3 and s["worst_spread"] == -2.0 and s["best_spread"] == 3.0


@pytest.mark.skipif(not (ev.DVOL_RAW.exists() and any(ev.DVOL_RAW.glob("*_dvol_1d.csv"))
                         and ev.OHLCV_RAW.exists()),
                    reason="frozen DVOL/spot data not present (gitignored/local-only)")
def test_evaluation_is_deterministic():
    a = ev.evaluate()
    b = ev.evaluate()
    for c in ev.CURRENCIES:
        assert a[c]["windows"] == b[c]["windows"]
        assert a[c]["ex_2021"] == b[c]["ex_2021"]
        assert a[c]["yearly"] == b[c]["yearly"]
    assert set(a) == {"BTC", "ETH"}
