"""Tests for tools/trade_journal_learning_report.py (pure builder only).

Never touches the real trades.db: every test feeds synthetic rows into
``build_learning_report``.
"""
from __future__ import annotations

import json

import pytest

from tools import trade_journal_learning_report as tjl


def _row(i, exchange, symbol, direction, strategy, regime, open_date, close_date,
         pnl_r, outcome="LOSS", sl=100.0, close_price=95.0):
    return {
        "id": i, "exchange": exchange, "symbol": symbol, "strategy": strategy,
        "direction": direction, "entry": 100.0, "sl": sl, "tp1": 110.0,
        "open_date": open_date, "close_date": close_date, "close_price": close_price,
        "outcome": outcome, "pnl_usd": None if pnl_r is None else pnl_r * 10.0, "pnl_r": pnl_r,
        "regime_at_open": regime, "strategy_status": "active",
    }


def _synthetic():
    t = []
    # S1 + S2: counter-trend losers (long in TREND_DOWN), mirrored on 2 exchanges
    t += [_row(1, "binance", "BTCUSDT", "long", "D", "TREND_DOWN", "2026-05-04", "2026-05-06", -1.0),
          _row(2, "kraken", "BTCUSDT", "long", "D", "TREND_DOWN", "2026-05-04", "2026-05-06", -1.0)]
    t += [_row(3, "binance", "ETHUSDT", "long", "D2", "TREND_DOWN", "2026-05-05", "2026-05-07", -1.0),
          _row(4, "kraken", "ETHUSDT", "long", "D2", "TREND_DOWN", "2026-05-05", "2026-05-07", -1.0)]
    # S3: aligned short, one leg breached the stop badly
    t += [_row(5, "binance", "SOLUSDT", "short", "E", "TREND_DOWN", "2026-05-06", "2026-05-10", -4.6,
               sl=105.0, close_price=146.0),
          _row(6, "kraken", "SOLUSDT", "short", "E", "TREND_DOWN", "2026-05-06", "2026-05-10", -1.0)]
    # S4..S6: aligned longs in TREND_UP, winners, some TIMEOUT closes
    t += [_row(7, "binance", "XRPUSDT", "long", "F", "TREND_UP", "2026-05-11", "2026-05-21", 1.0, "WIN"),
          _row(8, "kraken", "XRPUSDT", "long", "F", "TREND_UP", "2026-05-11", "2026-05-21", 1.0, "WIN")]
    t += [_row(9, "binance", "ADAUSDT", "long", "F", "TREND_UP", "2026-05-12", "2026-05-22", 1.0, "TIMEOUT"),
          _row(10, "kraken", "ADAUSDT", "long", "F", "TREND_UP", "2026-05-12", "2026-05-22", 1.0, "TIMEOUT")]
    t += [_row(11, "binance", "LTCUSDT", "long", "G", "RANGE", "2026-05-13", "2026-05-23", 0.5, "TIMEOUT"),
          _row(12, "kraken", "LTCUSDT", "long", "G", "RANGE", "2026-05-13", "2026-05-23", 1.0, "WIN")]
    # one still-open row (must be excluded from closed stats)
    t.append(_row(13, "binance", "DOGEUSDT", "short", "D", None, "2026-05-14", None, None, None))
    return t


def _excursions():
    ex = {}
    for tid in (7, 8, 9, 10, 11):
        ex[tid] = {"trade_id": tid, "max_favorable_R": 3.0, "max_adverse_R": -0.3,
                   "did_reach_2R": 1, "did_reach_3R": 1, "r_given_back_from_peak": 2.0}
    # excursion below the 1R MFE floor must be ignored
    ex[1] = {"trade_id": 1, "max_favorable_R": 0.4, "did_reach_2R": 0,
             "r_given_back_from_peak": 1.4}
    return ex


@pytest.fixture
def rep():
    return tjl.build_learning_report(_synthetic(), _excursions(), "2026-09-09")


def test_counts_and_dedup(rep):
    c = rep["counts"]
    assert (c["rows"], c["closed"], c["open"]) == (13, 12, 1)
    assert c["distinct_signals_closed"] == 6
    assert c["distinct_signals_all_rows"] == 7
    assert c["sum_R_raw"] == pytest.approx(-4.1)
    assert c["sum_R_dedup_best"] == pytest.approx(0.0)
    assert c["sum_R_dedup_mean"] == pytest.approx(-2.05)
    assert c["win_rate"] == pytest.approx(6 / 12)
    assert c["expectancy_R"] == pytest.approx(-4.1 / 12, abs=1e-3)
    assert c["profit_factor"] == pytest.approx(5.5 / 9.6, abs=1e-3)


def test_alignment_buckets(rep):
    al = rep["by_alignment"]
    assert al["COUNTER"]["n"] == 4 and al["COUNTER"]["n_signals"] == 2
    assert al["ALIGNED"]["n"] == 6
    assert al["NO_TREND_REGIME"]["n"] == 2
    assert "UNLABELED" not in al  # the only unlabeled row is still open
    rxd = rep["by_regime_x_direction"]
    assert rxd["TREND_DOWN|long"]["alignment"] == "COUNTER"
    assert rxd["TREND_DOWN|short"]["alignment"] == "ALIGNED"
    assert rxd["RANGE|long"]["alignment"] == "NO_TREND_REGIME"


def test_stop_discipline(rep):
    sd = rep["stop_discipline"]
    assert sd["n_breaches"] == 1
    b = sd["breaches"][0]
    assert b["id"] == 5 and b["pnl_r"] == -4.6 and b["sl"] == 105.0 and b["close_price"] == 146.0
    assert sd["total_excess_loss_R"] == pytest.approx(3.6)


def test_mfe_capture(rep):
    m = rep["mfe_capture"]
    assert m["n"] == 5
    assert m["mean_MFE_R"] == 3.0
    assert m["mean_realized_R"] == pytest.approx(0.9)
    assert m["capture_ratio"] == pytest.approx(0.3)
    assert m["mean_r_given_back_from_peak"] == 2.0
    assert m["reached_2R_but_closed_below_1R"] == 1


def test_holding_and_sample_quality(rep):
    h = rep["holding"]
    assert h["n_timeout"] == 3 and h["timeout_share"] == pytest.approx(0.25)
    assert h["by_outcome"]["LOSS"]["mean_days"] == pytest.approx(2.67, abs=0.01)
    sq = rep["sample_quality"]
    assert sq["overall_label"] == "PRELIMINARY" and sq["overall_sample_ok"] is False
    assert all(v["label"] == "PRELIMINARY" for v in sq["per_strategy"].values())


def test_suggestions_generated(rep):
    ids = {s["id"] for s in rep["suggestions"]}
    assert {"block_long_in_TREND_DOWN", "enforce_hard_stop", "partial_tp_or_trail_2R"} <= ids
    for s in rep["suggestions"]:
        assert s["status"] == "SUGGESTION_ONLY"
        assert s["caveat"] == "observation only; not applied"
        assert s["sample_ok"] is False
        assert isinstance(s["evidence"], dict) and s["evidence"]
    block = next(s for s in rep["suggestions"] if s["id"] == "block_long_in_TREND_DOWN")
    assert block["evidence"]["n"] == 4 and block["evidence"]["avg_R"] == -1.0


def test_markdown_has_banner_and_no_forbidden_words(rep):
    md = tjl.render_markdown(rep)
    assert tjl.BANNER in md
    assert "PRELIMINARY" in md
    assert tjl.forbidden_words_found(md) == []
    assert tjl.forbidden_words_found(json.dumps(rep)) == []
    for w in tjl.FORBIDDEN_WORDS:
        assert w not in md.lower()


def test_deterministic():
    a = tjl.build_learning_report(_synthetic(), _excursions(), "2026-09-09")
    b = tjl.build_learning_report(list(reversed(_synthetic())), _excursions(), "2026-09-09")
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
    assert tjl.render_markdown(a) == tjl.render_markdown(b)


def test_empty_input_is_safe():
    rep = tjl.build_learning_report([], {}, "2026-09-09")
    assert rep["counts"]["closed"] == 0 and rep["suggestions"] == []
    assert rep["mfe_capture"]["status"] == "MISSING"
    assert tjl.forbidden_words_found(tjl.render_markdown(rep)) == []


# ── evidence split (pre / post the 2026-09-15 partial-bar fix) ──────────────

def _split_rows():
    """3 retired (pre-fix) + 2 valid (post-fix) closed trades."""
    return [
        _row(1, "binance", "BTCUSDT", "long", "D", "TREND_UP",
             "2026-09-01", "2026-09-05", 2.0, outcome="TIMEOUT"),
        _row(2, "binance", "ETHUSDT", "long", "E", "TREND_UP",
             "2026-09-02", "2026-09-06", 3.0, outcome="WIN"),
        _row(3, "kraken", "SOLUSDT", "short", "F", "TREND_DOWN",
             "2026-09-14", "2026-09-18", -1.0, outcome="LOSS"),
        _row(4, "binance", "ADAUSDT", "short", "F2", "TREND_DOWN",
             "2026-09-16", "2026-09-19", -1.0, outcome="LOSS"),
        _row(5, "binance", "BCHUSDT", "short", "F", "TREND_DOWN",
             "2026-09-17", "2026-09-19", -1.0, outcome="LOSS"),
    ]


def test_evidence_split_partitions_on_the_cutoff():
    rep = tjl.build_learning_report(_split_rows(), {}, as_of="2026-09-21")
    ev = rep["evidence_split"]

    assert ev["cutoff"] == tjl.EVIDENCE_VALID_FROM == "2026-09-15"
    assert ev["cutoff_field"] == "open_date"
    # 2026-09-14 is BEFORE the cutoff, 2026-09-16/17 are on/after it
    assert ev["retired"]["closed"] == 3
    assert ev["valid_forward"]["closed"] == 2
    # the two buckets must account for every closed row, none dropped
    assert ev["retired"]["closed"] + ev["valid_forward"]["closed"] == rep["counts"]["closed"]


def test_evidence_split_keeps_headline_counts_untouched():
    """The split must be additive: it never filters the headline numbers."""
    rows = _split_rows()
    rep = tjl.build_learning_report(rows, {}, as_of="2026-09-21")
    assert rep["counts"]["closed"] == 5
    assert rep["counts"]["sum_R_raw"] == pytest.approx(2.0)


def test_evidence_split_reports_each_side_independently():
    rep = tjl.build_learning_report(_split_rows(), {}, as_of="2026-09-21")
    ev = rep["evidence_split"]

    assert ev["retired"]["sum_R_raw"] == pytest.approx(4.0)
    # the module rounds every R figure to 3dp via _r()
    assert ev["retired"]["expectancy_R"] == pytest.approx(4.0 / 3, abs=5e-4)
    assert ev["retired"]["outcome_WIN"] == 1
    assert ev["retired"]["outcome_TIMEOUT_positive"] == 1

    assert ev["valid_forward"]["sum_R_raw"] == pytest.approx(-2.0)
    assert ev["valid_forward"]["expectancy_R"] == pytest.approx(-1.0)
    assert ev["valid_forward"]["win_rate"] == pytest.approx(0.0)
    assert ev["valid_forward"]["outcome_WIN"] == 0


def test_evidence_split_handles_an_all_valid_book():
    rows = [r for r in _split_rows() if r["open_date"] >= "2026-09-15"]
    ev = tjl.build_learning_report(rows, {}, as_of="2026-09-21")["evidence_split"]
    assert ev["retired"]["closed"] == 0
    assert ev["retired"]["expectancy_R"] is None
    assert ev["valid_forward"]["closed"] == 2
    assert ev["retired_share_of_closed"] == pytest.approx(0.0)


def test_evidence_split_renders_both_buckets_in_markdown():
    rep = tjl.build_learning_report(_split_rows(), {}, as_of="2026-09-21")
    md = tjl.render_markdown(rep)
    assert "## Evidence split (cutoff 2026-09-15 on open_date)" in md
    assert "| valid forward evidence |" in md
    assert "| retired (pre-fix) |" in md
    assert tjl.forbidden_words_found(md) == []
