"""Tests for the Factory-D3 IS baseline runner harness.

Covers the loader (sorting, duplicate-date + invalid-OHLC rejection), the
two-layer IS/OOS seal (path-level and bar-date level), metric normalization
(including the zero-loss profit-factor case, an explicit max-drawdown check, and
empty trade lists), the standard-schema report builder + write_report
integration, callable-not-dynamic-import safety, and an offline-source token
scan.

Synthetic data only. No real NQ/ES CSVs are read; no strategy is backtested.
"""

import json
import os

import pytest

from engine import validation_is_runner as R
from engine import validation_reports as VR


def _write_csv(path, rows):
    """rows: list of (date_str, open, high, low, close, volume)."""
    lines = ["ts_event,open,high,low,close,volume"]
    for d, o, h, l, c, v in rows:
        lines.append(f"{d},{o},{h},{l},{c},{v}")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    return path


def _good_rows(dates):
    return [(d, 100.0, 105.0, 95.0, 102.0, 1000.0) for d in dates]


def _trade(r):
    return {"r_multiple": r}


# 1 -- loader sorts bars ascending by timestamp.
def test_load_yearly_csvs_sorts_bars(tmp_path):
    p = _write_csv(
        str(tmp_path / "nq_2020.csv"),
        _good_rows(["2020-03-01", "2020-01-01", "2020-02-01"]),
    )
    bars, qa = R.load_yearly_csvs([p])
    dates = [str(b["timestamp"].date()) for b in bars]
    assert dates == ["2020-01-01", "2020-02-01", "2020-03-01"]
    assert qa["total_bars"] == 3
    assert qa["date_range"] == ["2020-01-01", "2020-03-01"]


# 2 -- duplicate calendar dates are rejected.
def test_duplicate_dates_rejected(tmp_path):
    p = _write_csv(
        str(tmp_path / "nq_2020.csv"),
        _good_rows(["2020-01-01", "2020-01-01"]),
    )
    with pytest.raises(ValueError):
        R.load_yearly_csvs([p])


# 3 -- invalid OHLC rows are rejected (here: high < low).
def test_invalid_ohlc_rejected(tmp_path):
    p = _write_csv(
        str(tmp_path / "nq_2020.csv"),
        [("2020-01-01", 100.0, 90.0, 95.0, 92.0, 1000.0)],  # high 90 < low 95
    )
    with pytest.raises(ValueError):
        R.load_yearly_csvs([p])


# 4 -- IS path seal rejects 2023/2024/2025 files.
def test_is_guard_rejects_oos_paths():
    with pytest.raises(ValueError):
        R.assert_is_only_paths(["data/nq_2022.csv", "data/nq_2024.csv"], "IS")
    # clean IS set raises nothing
    R.assert_is_only_paths(["data/nq_2021.csv", "data/nq_2022.csv"], "IS")


# 5 -- IS bar-date seal rejects bars outside the expected IS years.
def test_is_guard_rejects_out_of_range_bars(tmp_path):
    p = _write_csv(
        str(tmp_path / "mix.csv"),
        _good_rows(["2020-06-01", "2023-06-01"]),
    )
    bars, _ = R.load_yearly_csvs([p])
    with pytest.raises(ValueError):
        R.assert_bars_in_is_range(bars, [2020, 2021, 2022])
    # within range -> no raise
    R.assert_bars_in_is_range(bars, [2020, 2023])


# 6 -- run_is_baseline accepts a trade list and computes standard metrics.
def test_run_is_baseline_trade_list_metrics():
    trades = [_trade(2.0), _trade(-1.0), _trade(-1.0), _trade(2.0)]
    out = R.run_is_baseline(lambda bars: trades, bars=[])
    m = out["metrics"]
    assert m["trade_count"] == 4
    assert m["total_r"] == 2.0
    assert m["win_rate"] == 0.5
    assert m["best_r"] == 2.0
    assert m["worst_r"] == -1.0
    assert m["profit_factor"] == pytest.approx(2.0)  # 4.0 wins / 2.0 losses


# 7 -- profit factor is safe (None) when there are no losing trades.
def test_profit_factor_zero_loss_safe():
    m = R.compute_is_metrics([_trade(1.0), _trade(2.0), _trade(0.5)])
    assert m["profit_factor"] is None
    assert m["total_r"] == pytest.approx(3.5)


# 8 -- max drawdown computed correctly on a known sequence.
def test_max_drawdown_correct():
    # equity path 0->1->-1->0 ; peak 1, trough -1 -> max DD = 2.0R
    m = R.compute_is_metrics([_trade(1.0), _trade(-2.0), _trade(1.0)])
    assert m["max_drawdown_r"] == pytest.approx(2.0)


# 9 -- build_is_report returns a report that validates against the D2 schema.
def test_build_is_report_valid_schema():
    metrics = R.compute_is_metrics([_trade(1.0), _trade(-1.0)])
    rep = R.build_is_report(
        branch_id="S99",
        module_id="is_baseline",
        title="Synthetic IS Baseline",
        verdict="CONTINUE",
        metrics=metrics,
        input_files=["data/synthetic_2020.csv"],
        data_window={"years": [2020], "bars": 2},
        frozen_parameters={"PARAM_A": 1, "PARAM_B": 2},
        source_commits={"engine": "deadbeef"},
        created_utc="2026-05-30T00:00:00+00:00",
    )
    assert VR.validate_report(rep) == []
    assert rep["next_allowed_step"] == "oos_protocol"
    assert "no_oos_peek" in rep["forbidden_actions"]


# 10 -- write_report integration produces report.json + report.md from an IS report.
def test_write_report_integration(tmp_path):
    metrics = R.compute_is_metrics([_trade(1.0), _trade(-1.0)])
    rep = R.build_is_report(
        branch_id="S99",
        module_id="is_baseline",
        title="Synthetic IS Baseline",
        verdict="PARK",
        metrics=metrics,
        input_files=["data/synthetic_2020.csv"],
        data_window={"years": [2020]},
        frozen_parameters={"PARAM_A": 1},
        created_utc="2026-05-30T00:00:00+00:00",
    )
    out = str(tmp_path / "rep")
    paths = VR.write_report(rep, out)
    assert os.path.isfile(paths["report_json"])
    assert os.path.isfile(paths["report_md"])
    with open(paths["report_json"], "r", encoding="utf-8") as fh:
        assert json.load(fh)["verdict"] == "PARK"


# 11 -- module source is offline/inert (no network/broker/dynamic-exec tokens).
def test_module_source_is_offline_inert():
    mod_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "engine", "validation_is_runner.py",
    )
    with open(mod_path, "r", encoding="utf-8") as fh:
        text = fh.read().lower()
    forbidden = [
        "subprocess", "socket", "urllib", "requests", "httpx", "aiohttp",
        "websockets", "ccxt", "binance", "bybit", "alpaca", "ib_insync",
        "broker", "api_key", "os.system", "exec(", "eval(",
        "importlib", "__import__",
    ]
    hits = [tok for tok in forbidden if tok in text]
    assert hits == [], f"forbidden tokens in module source: {hits}"


# 12 -- the strategy_runner callable is invoked directly (no dynamic import).
def test_strategy_runner_called_directly():
    calls = {"n": 0, "got_bars": None}
    sentinel_bars = [{"timestamp": None, "marker": True}]

    def runner(bars):
        calls["n"] += 1
        calls["got_bars"] = bars
        return [_trade(1.0)]

    out = R.run_is_baseline(runner, bars=sentinel_bars)
    assert calls["n"] == 1
    assert calls["got_bars"] is sentinel_bars  # exact object passed through
    assert out["metrics"]["trade_count"] == 1
    assert out["raw"] == [_trade(1.0)]


# 13 -- empty trade list is handled safely.
def test_empty_trade_list_safe():
    m = R.compute_is_metrics([])
    assert m["trade_count"] == 0
    assert m["total_r"] == 0.0
    assert m["profit_factor"] is None
    assert m["best_r"] is None
    out = R.run_is_baseline(lambda bars: [], bars=[])
    assert out["metrics"]["trade_count"] == 0


# 14 -- metadata / frozen parameters are preserved through the report.
def test_frozen_parameters_preserved():
    frozen = {"EMA": 50, "nested": {"a": [1, 2], "b": True}}
    rep = R.build_is_report(
        branch_id="S99",
        module_id="is_baseline",
        title="Preserve Test",
        verdict="CONTINUE",
        metrics=R.compute_is_metrics([_trade(1.0)]),
        input_files=["data/synthetic_2020.csv"],
        data_window={"years": [2020]},
        frozen_parameters=frozen,
        created_utc="2026-05-30T00:00:00+00:00",
    )
    assert rep["frozen_parameters"] == frozen
    assert rep["frozen_parameters"]["nested"]["b"] is True


# 14b -- a summary-dict runner result is normalized into the standard metric set.
def test_summary_dict_runner_normalized():
    summary = {"trade_count": 12, "total_r": -0.72, "profit_factor": 0.91}
    out = R.run_is_baseline(lambda bars: summary, bars=[])
    m = out["metrics"]
    assert m["trade_count"] == 12
    assert m["total_r"] == -0.72
    # standard keys present even when the runner omitted them
    assert "median_r" in m and m["median_r"] is None
