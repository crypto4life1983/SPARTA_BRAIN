"""Tests for the Factory-D7 regime-breakdown integration layer.

Covers tertile determinism, threshold application, volatility classification,
trade tagging, per-regime concentration summary, the conservative verdict map
(acceptable / inconclusive / concentrated / fail), the standard-schema report
builder + write_report integration, an offline-source token scan, empty-input
safety, and a no-real-data scan.

Synthetic data only. No real NQ/ES CSVs are read; no strategy is backtested.
"""

import json
import os

import pytest

from engine import validation_regime as RG
from engine import validation_reports as VR


def _trade(idx, r):
    return {"entry_index": idx, "r_multiple": float(r)}


# 1 -- tertiles are deterministic for a fixed distribution.
def test_tertiles_deterministic():
    vals = [0.01 * i for i in range(10)]
    a = RG.compute_is_tertiles(vals)
    b = RG.compute_is_tertiles(list(reversed(vals)))
    assert a == b
    assert a["lower"] <= a["upper"]


# 2 -- apply_regime_thresholds buckets low/mid/high correctly.
def test_apply_regime_thresholds():
    th = {"lower": 1.0, "upper": 2.0}
    assert RG.apply_regime_thresholds([0.5, 1.0, 1.5, 2.0, 2.5], th) == [
        "low", "low", "mid", "mid", "high"
    ]


# 3 -- classify_volatility_regimes labels per-bar and flags missing ATR.
def test_classify_volatility_regimes():
    bars = [{"close": 100.0, "atr20": v} for v in (1.0, 2.0, 3.0, 4.0, 5.0)]
    bars.append({"close": 100.0})  # missing atr -> unknown
    labels = RG.classify_volatility_regimes(bars)
    assert len(labels) == len(bars)
    assert labels[-1] == "unknown"
    assert set(labels[:-1]) <= {"low", "mid", "high"}
    assert "low" in labels and "high" in labels


# 4 -- regime tagging attaches the entry-bar regime, unknown when out of range.
def test_tag_trades_by_entry_regime():
    regimes = ["low", "mid", "high"]
    trades = [_trade(0, 1.0), _trade(2, -1.0), _trade(9, 0.5)]
    tagged = RG.tag_trades_by_entry_regime(trades, regimes)
    assert tagged[0]["regime"] == "low"
    assert tagged[1]["regime"] == "high"
    assert tagged[2]["regime"] == "unknown"
    # original trades are not mutated
    assert "regime" not in trades[0]


# 5 -- summary counts and per-regime totals are correct.
def test_summary_counts_and_totals():
    trades = [
        {"regime": "low", "r_multiple": 2.0},
        {"regime": "low", "r_multiple": -1.0},
        {"regime": "high", "r_multiple": 3.0},
    ]
    s = RG.summarize_by_regime(trades)
    assert s["trade_count"] == 3
    assert s["total_r"] == pytest.approx(4.0)
    assert s["by_regime"]["low"]["trade_count"] == 2
    assert s["by_regime"]["low"]["total_r"] == pytest.approx(1.0)
    assert s["regime_count"] == 2


# 6 -- verdict ACCEPTABLE for a spread, robust distribution.
def test_verdict_acceptable():
    summary = {
        "trade_count": 30, "regime_count": 3, "total_r": 15.0,
        "dominant_count_share": 0.40, "net_without_dominant": 9.0,
    }
    assert RG.derive_regime_verdict(summary) == RG.REGIME_RISK_ACCEPTABLE


# 7 -- verdict CONCENTRATED when one regime dominates the trade count.
def test_verdict_concentrated():
    summary = {
        "trade_count": 20, "regime_count": 3, "total_r": 10.0,
        "dominant_count_share": 0.75, "net_without_dominant": 4.0,
    }
    assert RG.derive_regime_verdict(summary) == RG.REGIME_RISK_CONCENTRATED


# 8 -- verdict FAIL when the edge lives entirely in one dominant regime.
def test_verdict_fail():
    summary = {
        "trade_count": 20, "regime_count": 3, "total_r": 5.0,
        "dominant_count_share": 0.85, "net_without_dominant": -3.0,
    }
    assert RG.derive_regime_verdict(summary) == RG.REGIME_RISK_FAIL


# 9 -- verdict INCONCLUSIVE for a single regime / no spread.
def test_verdict_inconclusive():
    summary = {
        "trade_count": 12, "regime_count": 1, "total_r": 8.0,
        "dominant_count_share": 1.0, "net_without_dominant": 0.0,
    }
    assert RG.derive_regime_verdict(summary) == RG.REGIME_RISK_INCONCLUSIVE


# 10 -- build_regime_report returns a valid D2-schema report.
def test_build_report_valid_schema():
    trades = [
        {"regime": "low", "r_multiple": 2.0},
        {"regime": "mid", "r_multiple": 1.0},
        {"regime": "high", "r_multiple": -1.0},
    ]
    summary = RG.summarize_by_regime(trades)
    rep = RG.build_regime_report(
        branch_id="S99",
        title="Synthetic Regime Breakdown",
        summary=summary,
        source_commits={"engine": "deadbeef"},
        input_files=["data/synthetic_trades.json"],
        data_window={"years": [2020]},
        created_utc="2026-05-30T00:00:00+00:00",
    )
    assert VR.validate_report(rep) == []
    assert rep["module_id"] == "regime_breakdown"
    assert rep["next_allowed_step"] == "multimarket"
    assert "no_regime_cherry_picking" in rep["forbidden_actions"]


# 11 -- write_report integration produces report.json + report.md.
def test_write_report_integration(tmp_path):
    trades = [{"regime": "low", "r_multiple": 1.0}, {"regime": "high", "r_multiple": -1.0}]
    summary = RG.summarize_by_regime(trades)
    rep = RG.build_regime_report(
        branch_id="S99",
        title="Synthetic Regime Breakdown",
        summary=summary,
        verdict=RG.REGIME_RISK_INCONCLUSIVE,
        created_utc="2026-05-30T00:00:00+00:00",
    )
    dest = str(tmp_path / "rep")
    paths = VR.write_report(rep, dest)
    assert os.path.isfile(paths["report_json"])
    assert os.path.isfile(paths["report_md"])
    with open(paths["report_json"], "r", encoding="utf-8") as fh:
        loaded = json.load(fh)
    assert loaded["metrics"]["trade_count"] == 2


# 12 -- module source is offline/inert (no network/broker/dynamic-exec/VC tokens).
def test_module_source_is_offline_inert():
    mod_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "engine", "validation_regime.py",
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
    assert RG.classify_volatility_regimes([]) == []
    s = RG.summarize_by_regime([])
    assert s["trade_count"] == 0
    assert RG.derive_regime_verdict(s) == RG.REGIME_RISK_INCONCLUSIVE


# 14 -- module reads no real market data (no CSV/data-loading references).
def test_module_reads_no_real_data():
    mod_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "engine", "validation_regime.py",
    )
    with open(mod_path, "r", encoding="utf-8") as fh:
        text = fh.read().lower()
    for token in [".csv", "data_offline", "load_daily_bars", "load_yearly_csvs", "open("]:
        assert token not in text, f"module references real-data token: {token}"
