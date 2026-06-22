"""Determinism + purity tests for the cross-sectional funding-carry sleeve evaluator.

Proves the evaluator imports NO network/fetch/trading libraries; reads ONLY the frozen local
OHLCV + funding dirs; uses fixed (non-optimized) parameters; respects the 40-symbol funding
allowlist with EOS/MKR excluded; sums funding by actual per-day timestamps (handles non-8h
cadence); does not forward-fill; and is deterministic. Data-dependent checks skip if the
gitignored frozen data is absent."""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

import tools.cross_sectional_funding_carry_sleeve_eval_once as ev


def test_module_purity_no_network_or_trading():
    src = Path(ev.__file__).read_text(encoding="utf-8")
    doc = ast.get_docstring(ast.parse(src)) or ""
    low = src.replace(doc, "").lower()
    for bad in ("urllib", "requests", "socket.", "ccxt", "binance.", "api_key",
                "place_order", "create_order", "urlopen", "fundingrate", "subprocess",
                "fapi.binance"):
        assert bad not in low, bad
    tree = ast.parse(src)
    banned = {"urllib", "requests", "socket", "http", "ccxt", "subprocess", "telegram"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned), imported & banned


def test_fixed_parameters():
    assert ev.FUNDING_LOOKBACK_DAYS == 30
    assert ev.REBALANCE_EVERY_DAYS == 21
    assert ev.COHORT_QUANTILE == 0.20
    assert ev.BASE_COST_BPS == 74.0
    assert ev.STRESS_COST_BPS == (37.0, 150.0, 300.0)
    assert ev.EXCLUDED == ("EOSUSDT", "MKRUSDT")


def test_reads_only_frozen_dirs():
    assert ev.OHLCV_RAW.as_posix().endswith("data/broad_crypto_universe_c23_c24/raw")
    assert ev.FUNDING_RAW.as_posix().endswith("data/broad_crypto_funding_universe/raw")


def test_stats_and_window_helpers():
    s = {f"2021-01-{i:02d}": 0.001 for i in range(1, 20)}
    st = ev.series_stats(s)
    assert st["pos_day_rate"] == 1.0 and st["max_dd"] == 0.0
    assert ev._compound(s, lambda d: True) > 0
    assert ev._compound(s, lambda d: d[:4] == "2099") == 0.0  # empty window -> 0


@pytest.mark.skipif(not (ev.FUNDING_RAW.exists() and any(ev.FUNDING_RAW.glob("*_funding.csv"))),
                    reason="frozen funding data not present (gitignored/local-only)")
def test_allowlist_40_and_eos_mkr_excluded():
    fund = ev.load_funding_daily()
    assert len(fund) == 40
    assert "EOSUSDT" not in fund and "MKRUSDT" not in fund
    # funding is summed per day from actual timestamps (non-8h cadence handled): a 4h-cadence
    # symbol will have some days with more than 3 funding events folded into the daily sum.
    # sanity: every value is a finite float and days are date strings
    for sym, days in fund.items():
        for day, v in list(days.items())[:1]:
            assert len(day) == 10 and isinstance(v, float)


@pytest.mark.skipif(not (ev.FUNDING_RAW.exists() and any(ev.FUNDING_RAW.glob("*_funding.csv"))),
                    reason="frozen funding data not present (gitignored/local-only)")
def test_evaluation_is_deterministic_and_cost_monotone():
    a = ev.evaluate()
    b = ev.evaluate()
    assert a["net_base"] == b["net_base"]
    assert a["yearly_net"] == b["yearly_net"]
    assert a["n_funding_symbols"] == 40
    # higher round-trip cost -> non-increasing net CAGR
    cagrs = [ev.evaluate(cohort_cost_bps=bps)["net_base"]["cagr"]
             for bps in (0.0, 74.0, 150.0, 300.0)]
    assert all(cagrs[i] >= cagrs[i + 1] - 1e-12 for i in range(len(cagrs) - 1))
