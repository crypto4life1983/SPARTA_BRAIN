"""Tests for the Factory-D7 walk-forward / rolling-window integration layer.

Covers year-range filtering, year-by-year summary, rolling 3yr / 5yr window
construction and aggregation, the conservative stability verdict map (stable /
inconclusive / fragile / fail), the standard-schema report builder + write_report
integration, an offline-source token scan, empty-input safety, and a no-real-data
scan.

Synthetic data only. No real NQ/ES CSVs are read; no strategy is backtested.
"""

import json
import os

import pytest

from engine import validation_walk_forward as WF
from engine import validation_reports as VR


def _trade(year, r):
    return {"year": year, "r_multiple": float(r)}


# 1 -- year-range filtering keeps only in-range trades.
def test_filter_trades_by_year_range():
    trades = [_trade(2013, 1.0), _trade(2018, 1.0), _trade(2024, 1.0)]
    kept = WF.filter_trades_by_year_range(trades, 2014, 2022)
    assert [t["year"] for t in kept] == [2018]


# 2 -- year-by-year summary counts trades and totals R per year.
def test_summarize_year_by_year():
    trades = [_trade(2015, 2.0), _trade(2015, -1.0), _trade(2016, 3.0)]
    s = WF.summarize_year_by_year(trades)
    assert s["by_year"]["2015"]["trade_count"] == 2
    assert s["by_year"]["2015"]["total_r"] == pytest.approx(1.0)
    assert s["by_year"]["2016"]["total_r"] == pytest.approx(3.0)
    assert s["positive_years"] == 2
    assert s["total_r"] == pytest.approx(4.0)


# 3 -- rolling 3-year windows over 2013-2022.
def test_rolling_windows_3yr():
    wins = WF.rolling_windows(2013, 2022, 3)
    assert wins[0] == (2013, 2015)
    assert wins[-1] == (2020, 2022)
    assert len(wins) == 8


# 4 -- rolling 5-year windows over 2013-2022.
def test_rolling_windows_5yr():
    wins = WF.rolling_windows(2013, 2022, 5)
    assert wins[0] == (2013, 2017)
    assert wins[-1] == (2018, 2022)
    assert len(wins) == 6


# 5 -- rolling-window summary aggregates per-year totals into each window.
def test_summarize_rolling_windows():
    trades = [_trade(y, 1.0) for y in range(2013, 2023)]  # +1R every year
    s = WF.summarize_rolling_windows(trades, 2013, 2022, 3)
    assert s["window_count"] == 8
    assert s["windows_with_trades"] == 8
    assert s["positive_window_share"] == pytest.approx(1.0)
    assert s["windows"][0]["total_r"] == pytest.approx(3.0)


# 6 -- verdict STABLE when nearly all windows are positive.
def test_verdict_stable():
    summary = {"windows_with_trades": 8, "positive_window_share": 1.0}
    assert WF.derive_walk_forward_verdict(summary) == WF.WALK_FORWARD_STABLE


# 7 -- verdict FRAGILE for a meaningful minority of losing windows.
def test_verdict_fragile():
    summary = {"windows_with_trades": 8, "positive_window_share": 0.60}
    assert WF.derive_walk_forward_verdict(summary) == WF.WALK_FORWARD_FRAGILE


# 8 -- verdict FAIL when half or more windows are non-positive.
def test_verdict_fail():
    summary = {"windows_with_trades": 8, "positive_window_share": 0.40}
    assert WF.derive_walk_forward_verdict(summary) == WF.WALK_FORWARD_FAIL


# 9 -- verdict INCONCLUSIVE with too few populated windows.
def test_verdict_inconclusive():
    summary = {"windows_with_trades": 1, "positive_window_share": 1.0}
    assert WF.derive_walk_forward_verdict(summary) == WF.WALK_FORWARD_INCONCLUSIVE
    summary2 = {"windows_with_trades": 0, "positive_window_share": None}
    assert WF.derive_walk_forward_verdict(summary2) == WF.WALK_FORWARD_INCONCLUSIVE


# 10 -- build_walk_forward_report returns a valid D2-schema report.
def test_build_report_valid_schema():
    trades = [_trade(y, 1.0) for y in range(2013, 2023)]
    summary = WF.summarize_rolling_windows(trades, 2013, 2022, 3)
    rep = WF.build_walk_forward_report(
        branch_id="S99",
        title="Synthetic Walk Forward",
        summary=summary,
        source_commits={"engine": "deadbeef"},
        input_files=["data/synthetic_trades.json"],
        data_window={"years": list(range(2013, 2023))},
        created_utc="2026-05-30T00:00:00+00:00",
    )
    assert VR.validate_report(rep) == []
    assert rep["module_id"] == "walk_forward"
    assert rep["next_allowed_step"] == "friction_stress"
    assert rep["frozen_parameters"]["window_size"] == 3
    assert "no_window_cherry_picking" in rep["forbidden_actions"]


# 11 -- write_report integration produces report.json + report.md.
def test_write_report_integration(tmp_path):
    trades = [_trade(y, 1.0) for y in range(2013, 2023)]
    summary = WF.summarize_rolling_windows(trades, 2013, 2022, 5)
    rep = WF.build_walk_forward_report(
        branch_id="S99",
        title="Synthetic Walk Forward",
        summary=summary,
        verdict=WF.WALK_FORWARD_STABLE,
        created_utc="2026-05-30T00:00:00+00:00",
    )
    dest = str(tmp_path / "rep")
    paths = VR.write_report(rep, dest)
    assert os.path.isfile(paths["report_json"])
    assert os.path.isfile(paths["report_md"])
    with open(paths["report_json"], "r", encoding="utf-8") as fh:
        loaded = json.load(fh)
    assert loaded["metrics"]["window_size"] == 5
    assert loaded["verdict"] == WF.WALK_FORWARD_STABLE


# 12 -- module source is offline/inert (no network/broker/dynamic-exec/VC tokens).
def test_module_source_is_offline_inert():
    mod_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "engine", "validation_walk_forward.py",
    )
    with open(mod_path, "r", encoding="utf-8") as fh:
        text = fh.read().lower()
    forbidden = [
        "subprocess", "socket", "urllib", "requests", "httpx", "aiohttp",
        "websockets", "ccxt", "binance", "bybit", "alpaca", "ib_insync",
        "broker", "api_key", "os.system", "exec(", "eval(",
        "importlib", "__import__", "git",
    ]
    hits = [tok for tok in forbidden if tok in text]
    assert hits == [], f"forbidden tokens in module source: {hits}"


# 13 -- empty inputs are handled safely (no crash, INCONCLUSIVE).
def test_empty_inputs_handled_safely():
    ys = WF.summarize_year_by_year([])
    assert ys["year_count"] == 0
    s = WF.summarize_rolling_windows([], 2013, 2022, 3)
    assert s["windows_with_trades"] == 0
    assert s["positive_window_share"] is None
    assert WF.derive_walk_forward_verdict(s) == WF.WALK_FORWARD_INCONCLUSIVE


# 14 -- module reads no real market data (no CSV/data-loading references).
def test_module_reads_no_real_data():
    mod_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "engine", "validation_walk_forward.py",
    )
    with open(mod_path, "r", encoding="utf-8") as fh:
        text = fh.read().lower()
    for token in [".csv", "data_offline", "load_daily_bars", "load_yearly_csvs", "open("]:
        assert token not in text, f"module references real-data token: {token}"
