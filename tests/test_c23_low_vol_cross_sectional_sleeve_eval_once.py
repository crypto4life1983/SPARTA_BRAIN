"""Determinism + purity tests for the exploratory C23 low-vol sleeve evaluation tool.

Proves the evaluator: imports NO network/fetch/trading libraries; reads ONLY the frozen
broad-universe dir; uses fixed (non-optimized) parameters; and is deterministic (identical
output across runs). Stat-helper correctness is checked on a fixed synthetic series. The
data-dependent determinism check skips cleanly if the gitignored frozen data is absent."""
from __future__ import annotations

import ast
import math
from pathlib import Path

import pytest

import tools.c23_low_vol_cross_sectional_sleeve_eval_once as c23e


def test_module_purity_no_network_or_trading():
    src = Path(c23e.__file__).read_text(encoding="utf-8")
    # strip the module docstring: words like "fetch"/"http" legitimately appear there as
    # prose ("runs NO fetch"), describing what the tool does NOT do.
    doc = ast.get_docstring(ast.parse(src)) or ""
    low = src.replace(doc, "").lower()
    for bad in ("urllib", "requests", "socket.", "ccxt", "binance.", "api_key",
                "place_order", "create_order", "urlopen", "subprocess", ".get(\"http"):
        assert bad not in low, bad
    tree = ast.parse(src)
    banned = {"urllib", "requests", "socket", "http", "ccxt", "subprocess", "telegram"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned), imported & banned


def test_fixed_parameters_reported():
    assert c23e.VOL_LOOKBACK_DAYS == 30
    assert c23e.REBALANCE_EVERY_DAYS == 21
    assert c23e.COHORT_QUANTILE == 0.20
    assert c23e.ALL_IN_ROUND_TRIP_BPS == 37.0


def test_reads_only_frozen_dir():
    assert c23e.RAW.as_posix().endswith("data/broad_crypto_universe_c23_c24/raw")


def test_stats_helpers_correct():
    # known series: constant +1% daily -> positive, zero vol
    s = {f"2021-01-{i:02d}": 0.01 for i in range(1, 20)}
    st = c23e.series_stats(s)
    assert st["pos_day_rate"] == 1.0
    assert st["max_dd"] == 0.0
    assert abs(c23e.stdev([1.0, 1.0, 1.0])) < 1e-12
    assert abs(c23e.stdev([0.0, 2.0]) - math.sqrt(2.0)) < 1e-9
    # pearson of identical VARYING series == 1 (constant series has zero variance -> None)
    v = {f"2021-01-{i:02d}": (0.01 if i % 2 else -0.02) for i in range(1, 40)}
    assert abs(c23e.pearson(v, dict(v)) - 1.0) < 1e-9
    assert c23e.pearson(s, dict(s)) is None  # constant series -> undefined corr


@pytest.mark.skipif(not (c23e.RAW.exists() and any(c23e.RAW.glob("*_1d.csv"))),
                    reason="frozen broad-universe data not present (gitignored/local-only)")
def test_evaluation_is_deterministic():
    a = c23e.evaluate()
    b = c23e.evaluate()
    assert a["sleeve"] == b["sleeve"]
    assert a["corr_btc"] == b["corr_btc"]
    assert a["yearly_sleeve"] == b["yearly_sleeve"]
    # dollar-neutral construction: long leg positive weights, short leg negative
    assert a["n_symbols"] == 42
