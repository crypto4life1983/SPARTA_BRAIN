"""Determinism + purity tests for the exploratory C24 illiquidity sleeve evaluation tool.

Proves the evaluator imports NO network/fetch/trading libraries, reads ONLY the frozen
broad-universe dir, uses fixed (non-optimized) parameters with a STRESS grid (not a search),
and is deterministic. Data-dependent checks skip if the gitignored frozen data is absent."""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

import tools.c24_illiquidity_cross_sectional_sleeve_eval_once as c24e


def test_module_purity_no_network_or_trading():
    src = Path(c24e.__file__).read_text(encoding="utf-8")
    doc = ast.get_docstring(ast.parse(src)) or ""
    low = src.replace(doc, "").lower()
    for bad in ("urllib", "requests", "socket.", "ccxt", "binance.", "api_key",
                "place_order", "create_order", "urlopen", "subprocess"):
        assert bad not in low, bad
    tree = ast.parse(src)
    banned = {"urllib", "requests", "socket", "http", "ccxt", "subprocess", "telegram"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned), imported & banned


def test_fixed_parameters_and_stress_grid():
    assert c24e.AMIHUD_LOOKBACK_DAYS == 30
    assert c24e.REBALANCE_EVERY_DAYS == 21
    assert c24e.COHORT_QUANTILE == 0.20
    assert c24e.FEE_BPS == 27.0 and c24e.SLIPPAGE_BPS == 10.0
    assert c24e.ILLIQ_STRESS_M == 3.0
    assert c24e.M_GRID == (1.0, 2.0, 3.0, 5.0, 10.0)  # fixed stress grid, not a search


def test_reads_only_frozen_dir():
    assert c24e.RAW.as_posix().endswith("data/broad_crypto_universe_c23_c24/raw")


@pytest.mark.skipif(not (c24e.RAW.exists() and any(c24e.RAW.glob("*_1d.csv"))),
                    reason="frozen broad-universe data not present (gitignored/local-only)")
def test_evaluation_is_deterministic_and_cost_monotone():
    a = c24e.evaluate()
    b = c24e.evaluate()
    assert a["base_net"] == b["base_net"]
    assert a["sensitivity"] == b["sensitivity"]
    assert a["n_symbols"] == 42
    # higher long-leg slippage multiplier => non-increasing CAGR (cost monotonicity)
    cagrs = [a["sensitivity"][m]["cagr"] for m in c24e.M_GRID]
    assert all(cagrs[i] >= cagrs[i + 1] - 1e-12 for i in range(len(cagrs) - 1))
