"""Tests for the Factory-D5 entry-significance integration layer.

Covers signal-index normalization (sort/dedupe + rejection rules), the
fixed-horizon significance run (one result per horizon, determinism, empty-signal
safety, optional raw-signal baseline), the conservative verdict mapping, and the
standard-schema report builder + write_report integration, plus an offline-source
token scan and a no-real-data scan.

Synthetic data only. No real NQ/ES CSVs are read; no strategy is backtested.
"""

import json
import os

import pytest

from engine import validation_entry_significance as E
from engine import signal_significance as S
from engine import validation_reports as VR


def _bars(prices):
    return [{"close": float(p)} for p in prices]


def _synthetic_series(n=200):
    # gentle deterministic drift so forward returns are finite/non-degenerate
    return [100.0 + 0.1 * i for i in range(n)]


def _result_block(verdicts):
    """Build a minimal run-output-shaped dict from a {horizon: verdict} map."""
    return {"results": {str(h): {"verdict": v} for h, v in verdicts.items()}}


# 1 -- normalize sorts and deduplicates.
def test_normalize_sorts_and_dedups():
    assert E.normalize_signal_indices([5, 1, 5, 3, 1]) == [1, 3, 5]


# 2 -- normalize rejects negative indices.
def test_normalize_rejects_negative():
    with pytest.raises(ValueError):
        E.normalize_signal_indices([1, -2, 3])


# 3 -- normalize rejects non-int (incl. bool and float).
def test_normalize_rejects_non_int():
    with pytest.raises(ValueError):
        E.normalize_signal_indices([1, 2.0, 3])
    with pytest.raises(ValueError):
        E.normalize_signal_indices([1, True, 3])


# 4 -- normalize respects max_index.
def test_normalize_respects_max_index():
    assert E.normalize_signal_indices([0, 5, 9], max_index=9) == [0, 5, 9]
    with pytest.raises(ValueError):
        E.normalize_signal_indices([0, 5, 10], max_index=9)


# 5 -- run returns exactly one result per horizon.
def test_run_one_result_per_horizon():
    bars = _bars(_synthetic_series(200))
    out = E.run_entry_significance(
        bars, [10, 20, 30, 40], horizons=(5, 10, 20), n_iter=200, seed=0
    )
    assert set(out["results"].keys()) == {"5", "10", "20"}
    for h in ("5", "10", "20"):
        assert out["results"][h]["horizon"] == int(h)


# 6 -- run is deterministic under a fixed seed.
def test_run_deterministic_with_seed():
    bars = _bars(_synthetic_series(200))
    a = E.run_entry_significance(bars, [10, 20, 30], n_iter=300, seed=7)
    b = E.run_entry_significance(bars, [10, 20, 30], n_iter=300, seed=7)
    assert a == b


# 7 -- run handles empty signals safely (NO_RESULT, no crash).
def test_run_empty_signals_safe():
    bars = _bars(_synthetic_series(120))
    out = E.run_entry_significance(bars, [], horizons=(5, 10), n_iter=100, seed=0)
    for h in ("5", "10"):
        assert out["results"][h]["verdict"] == S.NO_RESULT
    assert E.derive_entry_verdict(out) == E.ENTRY_EDGE_INCONCLUSIVE


# 8 -- verdict SUPPORTED when horizons show EDGE_LIKELY and no NO_EDGE.
def test_verdict_supported():
    res = _result_block({5: S.EDGE_LIKELY, 10: S.EDGE_LIKELY, 20: S.INCONCLUSIVE})
    assert E.derive_entry_verdict(res, min_supported_horizons=1) == E.ENTRY_EDGE_SUPPORTED


# 9 -- verdict NOT_SUPPORTED when every valid horizon is NO_EDGE.
def test_verdict_not_supported():
    res = _result_block({5: S.NO_EDGE, 10: S.NO_EDGE, 20: S.NO_RESULT})
    assert E.derive_entry_verdict(res) == E.ENTRY_EDGE_NOT_SUPPORTED


# 10 -- verdict INCONCLUSIVE for mixed EDGE_LIKELY + NO_EDGE.
def test_verdict_inconclusive_mixed():
    res = _result_block({5: S.EDGE_LIKELY, 10: S.NO_EDGE, 20: S.INCONCLUSIVE})
    assert E.derive_entry_verdict(res) == E.ENTRY_EDGE_INCONCLUSIVE


# 11 -- build_entry_significance_report returns a valid D2-schema report.
def test_build_report_valid_schema():
    bars = _bars(_synthetic_series(200))
    out = E.run_entry_significance(bars, [10, 20, 30], n_iter=200, seed=0)
    rep = E.build_entry_significance_report(
        branch_id="S99",
        title="Synthetic Entry Significance",
        results=out,
        source_commits={"engine": "deadbeef"},
        input_files=["data/synthetic_2020.csv"],
        data_window={"years": [2020]},
        created_utc="2026-05-30T00:00:00+00:00",
    )
    assert VR.validate_report(rep) == []
    assert rep["module_id"] == "entry_significance"
    assert rep["next_allowed_step"] == "sequence_risk"
    assert rep["verdict"] in (
        E.ENTRY_EDGE_SUPPORTED, E.ENTRY_EDGE_INCONCLUSIVE, E.ENTRY_EDGE_NOT_SUPPORTED
    )
    assert "no_horizon_shopping" in rep["forbidden_actions"]


# 12 -- write_report integration produces report.json + report.md.
def test_write_report_integration(tmp_path):
    bars = _bars(_synthetic_series(150))
    out = E.run_entry_significance(bars, [10, 20], horizons=(5, 10), n_iter=100, seed=0)
    rep = E.build_entry_significance_report(
        branch_id="S99",
        title="Synthetic Entry Significance",
        results=out,
        verdict=E.ENTRY_EDGE_INCONCLUSIVE,
        created_utc="2026-05-30T00:00:00+00:00",
    )
    dest = str(tmp_path / "rep")
    paths = VR.write_report(rep, dest)
    assert os.path.isfile(paths["report_json"])
    assert os.path.isfile(paths["report_md"])
    with open(paths["report_json"], "r", encoding="utf-8") as fh:
        loaded = json.load(fh)
    assert loaded["metrics"]["by_horizon"]["5"]["horizon"] == 5


# 13 -- module source is offline/inert (no network/broker/dynamic-exec/VC tokens).
def test_module_source_is_offline_inert():
    mod_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "engine", "validation_entry_significance.py",
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


# 14 -- the optional baseline_signal_indices path runs without breaking.
def test_baseline_signal_indices_path():
    bars = _bars(_synthetic_series(200))
    out = E.run_entry_significance(
        bars, [10, 20, 30],
        horizons=(5, 10), n_iter=100, seed=0,
        baseline_signal_indices=[15, 25, 35, 45],
    )
    bc = out["baseline_comparison"]
    assert bc is not None
    assert set(bc.keys()) == {"5", "10"}
    assert "real_mean" in bc["5"] and "alt_mean" in bc["5"]
    assert bc["5"]["alt_count"] >= 1


# 15 -- module reads no real market data (no CSV/data-loading references).
def test_module_reads_no_real_data():
    mod_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "engine", "validation_entry_significance.py",
    )
    with open(mod_path, "r", encoding="utf-8") as fh:
        text = fh.read().lower()
    for token in [".csv", "data_offline", "load_daily_bars", "load_yearly_csvs", "open("]:
        assert token not in text, f"module references real-data token: {token}"
