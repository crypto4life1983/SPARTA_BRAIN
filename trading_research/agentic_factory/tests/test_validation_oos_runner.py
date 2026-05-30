"""Tests for the Factory-D4 OOS protocol + run enforcement layer.

Covers the protocol-binding gate (placeholder rejection), the two-layer OOS seal
(path-level IS/2026 refusal, bar-date refusal), protocol/result report builders,
the protocol-bound run guard, callable-not-dynamic-import safety, metric
normalization on synthetic trades, and an offline-source token scan (including a
no-version-control-call check).

Synthetic data only. No real NQ/ES CSVs are read; no strategy is backtested.
"""

import json
import os
from datetime import datetime

import pytest

from engine import validation_oos_runner as O
from engine import validation_reports as VR


def _bars(years):
    return [{"timestamp": datetime(y, 6, 1), "close": 100.0} for y in years]


def _trade(r):
    return {"r_multiple": r}


# 1 -- protocol binding rejects empty / missing / DRAFT / UNCOMMITTED.
def test_protocol_binding_rejects_placeholders():
    for bad in ["", "   ", "DRAFT", "uncommitted", "UNCOMMITTED", "none", None, 123]:
        with pytest.raises(ValueError):
            O.assert_oos_protocol_bound(bad)


# 2 -- protocol binding accepts a real-looking hash string.
def test_protocol_binding_accepts_real_hash():
    O.assert_oos_protocol_bound("023fc7db35d838994a54d1c1b4bb28ae32dcf47b")
    O.assert_oos_protocol_bound("5c538c1")


# 3 -- OOS path guard rejects in-sample 2013-2022 paths.
def test_oos_path_guard_rejects_is_paths():
    with pytest.raises(ValueError):
        O.assert_oos_only_paths(["data/nq_2024.csv", "data/nq_2019.csv"], "OOS")


# 4 -- OOS path guard accepts 2023-2025 paths.
def test_oos_path_guard_accepts_oos_paths():
    O.assert_oos_only_paths(
        ["data/nq_2023.csv", "data/nq_2024.csv", "data/nq_2025.csv"], "OOS"
    )


# 5 -- OOS path guard rejects 2026 by default.
def test_oos_path_guard_rejects_2026_default():
    with pytest.raises(ValueError):
        O.assert_oos_only_paths(["data/nq_2026.csv"], "OOS")


# 6 -- OOS bar-date guard rejects IS-year bars.
def test_oos_bar_guard_rejects_is_bars():
    with pytest.raises(ValueError):
        O.assert_bars_in_oos_range(_bars([2024, 2020]))


# 7 -- OOS bar-date guard accepts 2023-2025 bars.
def test_oos_bar_guard_accepts_oos_bars():
    O.assert_bars_in_oos_range(_bars([2023, 2024, 2025]))


# 8 -- build_oos_protocol_report returns a valid D2-schema report.
def test_build_protocol_report_valid_schema():
    rep = O.build_oos_protocol_report(
        branch_id="S99",
        title="Synthetic OOS Protocol",
        criteria={"pass": "OOS net>0 both markets", "fail": "either market net<0"},
        protocol_rules=["one_shot", "no_reuse", "compare_strictly_to_floors"],
        source_commits={"engine": "deadbeef"},
        created_utc="2026-05-30T00:00:00+00:00",
    )
    assert VR.validate_report(rep) == []
    assert rep["module_id"] == "oos_protocol"
    assert rep["next_allowed_step"] == "oos_run"
    assert rep["frozen_parameters"]["pass_watch_fail_criteria"]["pass"]


# 9 -- run_oos_baseline refuses to run without a protocol_commit.
def test_run_oos_refuses_without_protocol():
    with pytest.raises(ValueError):
        O.run_oos_baseline(lambda bars: [], _bars([2024]), metadata={})
    with pytest.raises(ValueError):
        O.run_oos_baseline(
            lambda bars: [], _bars([2024]), metadata={"protocol_commit": "DRAFT"}
        )


# 10 -- run_oos_baseline uses the passed callable directly (no dynamic import).
def test_run_oos_uses_passed_callable():
    calls = {"n": 0, "got_bars": None}
    sentinel = _bars([2024])

    def runner(bars):
        calls["n"] += 1
        calls["got_bars"] = bars
        return [_trade(1.0)]

    out = O.run_oos_baseline(
        runner, sentinel, metadata={"protocol_commit": "abc123def"}
    )
    assert calls["n"] == 1
    assert calls["got_bars"] is sentinel
    assert out["raw"] == [_trade(1.0)]


# 11 -- run_oos_baseline computes standard metrics on synthetic trades.
def test_run_oos_computes_metrics():
    trades = [_trade(2.0), _trade(-1.0), _trade(-1.0), _trade(2.0)]
    out = O.run_oos_baseline(
        lambda bars: trades,
        _bars([2023, 2024, 2025]),
        metadata={"protocol_commit": "abc123def", "oos_years": {2023, 2024, 2025}},
    )
    m = out["metrics"]
    assert m["trade_count"] == 4
    assert m["total_r"] == 2.0
    assert m["profit_factor"] == pytest.approx(2.0)


# 11b -- run_oos_baseline still enforces the bar-date seal under a valid protocol.
def test_run_oos_enforces_bar_range_even_when_bound():
    with pytest.raises(ValueError):
        O.run_oos_baseline(
            lambda bars: [], _bars([2024, 2021]),
            metadata={"protocol_commit": "abc123def"},
        )


# 12 -- build_oos_result_report includes the protocol commit.
def test_build_result_report_includes_protocol_commit():
    rep = O.build_oos_result_report(
        branch_id="S99",
        title="Synthetic OOS Result",
        verdict="OOS_FAIL",
        metrics={"trade_count": 1, "total_r": -1.0, "profit_factor": None},
        protocol_commit="abc123def456",
        created_utc="2026-05-30T00:00:00+00:00",
    )
    assert VR.validate_report(rep) == []
    assert rep["source_commits"]["protocol_commit"] == "abc123def456"
    assert rep["module_id"] == "oos_run"


# 13 -- module source is offline/inert (no network/broker/dynamic-exec/VC tokens).
def test_module_source_is_offline_inert():
    mod_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "engine", "validation_oos_runner.py",
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


# 14 -- criteria / frozen params survive a write_report JSON round-trip.
def test_protocol_criteria_survive_roundtrip(tmp_path):
    criteria = {"pass": "net>0", "watch": "0..-0.5R", "fail": "<-0.5R", "nested": {"a": [1, 2]}}
    rep = O.build_oos_protocol_report(
        branch_id="S99",
        title="Roundtrip Protocol",
        criteria=criteria,
        protocol_rules=["one_shot"],
        created_utc="2026-05-30T00:00:00+00:00",
    )
    out = str(tmp_path / "rep")
    VR.write_report(rep, out)
    with open(os.path.join(out, "report.json"), "r", encoding="utf-8") as fh:
        loaded = json.load(fh)
    assert loaded["frozen_parameters"]["pass_watch_fail_criteria"] == criteria
    assert loaded["frozen_parameters"]["protocol_rules"] == ["one_shot"]


# 15 -- the 2026 override only works when explicitly allowed.
def test_2026_override_explicit_only():
    with pytest.raises(ValueError):
        O.assert_oos_only_paths(["data/nq_2026.csv"], "OOS", allow_2026=False)
    # explicit allow -> no raise
    O.assert_oos_only_paths(["data/nq_2026.csv"], "OOS", allow_2026=True)
