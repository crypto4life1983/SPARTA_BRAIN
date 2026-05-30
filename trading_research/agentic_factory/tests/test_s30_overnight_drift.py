"""Tests for the S30 Overnight Session-Return Decomposition / Overnight Drift engine.

Covers the frozen S30-D2 rules: the overnight/day/total leg decomposition and its
hard measurement-reconstruction gate, observations starting at the second bar,
entry at the prior close and exit at the current open, the long-overnight-only
invariant, the absence of any day-session exposure or stop/target logic, the
percent return, the ATR20[t-1] (prior, not current) normalization, skipping of
invalid/missing/zero/negative prices, the top-day dependence gate, the
distribution summary, safe handling of empty/short data, a deterministic
known-sequence total, the measurement-validity failure path, and an
offline-safety scan of the engine source.

Synthetic-data only. No real NQ/ES data is read here; load_daily_bars and
run_backtest are never called.
"""

import os
from datetime import datetime, timedelta

import pytest

from engine import s30_overnight_drift as S

BASE = datetime(2020, 1, 1)


def _bar(k, o, h, l, c, v=1000.0):
    return {
        "timestamp": BASE + timedelta(days=k),
        "open": o, "high": h, "low": l, "close": c, "volume": v,
    }


def _make(seq):
    """Build bars from a list of (open, high, low, close) tuples."""
    return [_bar(i, o, h, l, c) for i, (o, h, l, c) in enumerate(seq)]


def _known_sequence():
    """A small hand-checked sequence; overnight points are +1, +1, -1 -> net +1."""
    return _make([
        (100.0, 100.5, 99.5, 100.0),   # day0: close 100
        (101.0, 102.5, 100.5, 102.0),  # day1: o101 (+1 vs prev close 100), c102
        (103.0, 103.5, 100.5, 101.0),  # day2: o103 (+1 vs prev close 102), c101
        (100.0, 105.5, 99.5, 105.0),   # day3: o100 (-1 vs prev close 101), c105
    ])


def _ramp(n=30):
    """n bars with varied ranges so ATR changes bar-to-bar; overnight = +0.5 each."""
    out = []
    for i in range(n):
        c = 100.0 + i
        o = c - 0.5
        h = c + 1.0 + (i % 3)
        l = (c - 0.5) - 1.0 - (i % 2)   # below both o and c
        out.append(_bar(i, o, h, l, c))
    return out


# 1 — measurement reconstruction: overnight + day_session == total day (within tol).
def test_measurement_reconstruction_holds():
    obs = S.build_overnight_observations(_known_sequence())
    assert len(obs) == 3
    for o in obs:
        assert o["overnight_points"] + o["day_session_points"] == pytest.approx(
            o["total_day_points"]
        )
        assert abs(o["reconstruction_error"]) <= S.RECONSTRUCTION_TOLERANCE
    chk = S.validate_overnight_measurement(obs)
    assert chk["valid"] is True
    assert chk["observation_count"] == 3


# 2 — observations start at the SECOND bar, never the first (no t-1 for bar 0).
def test_observations_start_at_second_bar():
    bars = _known_sequence()
    obs = S.build_overnight_observations(bars)
    assert len(obs) == len(bars) - 1
    assert obs[0]["current_index"] == 1
    assert obs[0]["prior_index"] == 0
    assert min(o["current_index"] for o in obs) == 1   # bar 0 is never a trade date


# 3 — entry uses the PRIOR close.
def test_entry_uses_prior_close():
    bars = _known_sequence()
    obs = S.build_overnight_observations(bars)
    for o in obs:
        assert o["entry_price"] == bars[o["prior_index"]]["close"]
        assert o["prior_close"] == bars[o["prior_index"]]["close"]


# 4 — exit uses the CURRENT open.
def test_exit_uses_current_open():
    bars = _known_sequence()
    obs = S.build_overnight_observations(bars)
    for o in obs:
        assert o["exit_price"] == bars[o["current_index"]]["open"]
        assert o["current_open"] == bars[o["current_index"]]["open"]


# 5 — long-overnight-only invariant: every observation is the frozen direction.
def test_long_overnight_only_direction():
    obs = S.simulate_s30(_known_sequence())
    assert obs
    for o in obs:
        assert o["direction"] == S.DIRECTION == "long_overnight"
        assert "short" not in o["direction"]


# 6 — no day-session exposure: the day leg is MEASURED but never traded.
def test_no_day_session_exposure():
    obs = S.build_overnight_observations(_known_sequence())
    for o in obs:
        assert "day_session_points" in o            # measured for comparison
        assert "day_session_exposure" not in o      # but never a held position
        assert o["exit_price"] == o["current_open"]  # exit at open, not close
        assert o["exit_price"] != o["total_day_points"]


# 7 — no stop/target logic: distribution-only, no path-dependent exit fields.
def test_no_stop_or_target_fields():
    obs = S.build_overnight_observations(_known_sequence())
    forbidden = ("stop_price", "target_price", "exit_reason", "r_multiple",
                 "time_stop", "risk")
    for o in obs:
        for key in forbidden:
            assert key not in o


# 8 — percent overnight return = open[t] / close[t-1] - 1.
def test_percent_return_correct():
    bars = _known_sequence()
    obs = S.build_overnight_observations(bars)
    for o in obs:
        expected = bars[o["current_index"]]["open"] / bars[o["prior_index"]]["close"] - 1.0
        assert o["overnight_return_pct"] == pytest.approx(expected)


# 9 — ATR-normalized overnight uses the PRIOR ATR20, not the current bar's ATR20.
def test_normalized_uses_prior_atr():
    bars = _ramp(30)
    atr = S.wilder_atr(bars, S.ATR_PERIOD)
    obs = S.build_overnight_observations(bars)
    warm = [o for o in obs if o["atr20_prior"] is not None]
    assert warm, "expected some warm ATR observations"
    for o in warm:
        t = o["current_index"]
        assert o["atr20_prior"] == atr[t - 1]                       # prior, not current
        assert o["normalized_overnight_r"] == pytest.approx(
            o["overnight_points"] / atr[t - 1]
        )
    # prove prior != current somewhere (so the t-1 choice is actually exercised).
    some = warm[0]
    ti = some["current_index"]
    assert atr[ti - 1] != atr[ti]


# 10 — a pair with a missing open/close is SKIPPED.
def test_missing_price_pair_skipped():
    bars = _known_sequence()
    bars[2]["open"] = None                       # break day2's overnight leg
    obs = S.build_overnight_observations(bars)
    assert all(o["current_index"] != 2 for o in obs)   # day2 skipped
    assert len(obs) == 2                                # 3 - 1 skipped


# 11 — invalid zero/negative prices are rejected.
def test_invalid_prices_rejected():
    bars = _known_sequence()
    bars[1]["close"] = 0.0     # used as prior_close for day2 -> day2 skipped
    bars[3]["open"] = -5.0     # day3 overnight invalid -> day3 skipped
    obs = S.build_overnight_observations(bars)
    idxs = {o["current_index"] for o in obs}
    assert 2 not in idxs and 3 not in idxs
    assert all(o["entry_price"] > 0 and o["exit_price"] > 0 for o in obs)


# 12 — top-day dependence gate detects fat-tail concentration.
def test_top_day_dependence_gate():
    fragile = [{"overnight_points": p} for p in [10.0, 9.0, 8.0, -1, -1, -1, -1]]
    g = S.top_day_dependence(fragile)
    assert g["net_points"] == pytest.approx(23.0)
    assert g["net_ex_top3"] == pytest.approx(-4.0)
    assert g["passes_ex_top3"] is False
    robust = [{"overnight_points": p} for p in [3.0, 2.0, 1.5, 1.0, 1.0, 1.0, -1.0]]
    g2 = S.top_day_dependence(robust)
    assert g2["net_ex_top3"] == pytest.approx(2.0)
    assert g2["passes_ex_top3"] is True


# 13 — summary computes count, totals, average, median, win rate, positive years.
def test_summary_fields():
    obs = S.build_overnight_observations(_known_sequence())
    s = S.summarize_overnight(obs)
    assert s["observation_count"] == 3
    assert s["total_points"] == pytest.approx(1.0)        # +1 +1 -1
    assert s["average_points"] == pytest.approx(1.0 / 3.0)
    assert s["median_points"] == pytest.approx(1.0)        # sorted [-1, 1, 1]
    assert s["win_rate"] == pytest.approx(2.0 / 3.0)
    assert s["year_count"] == 1
    assert "2020" in s["positive_years"]                   # net +1 in 2020
    assert s["positive_year_count"] == 1


# 14 — empty / short data returns safely.
def test_empty_and_short_data_safe():
    assert S.build_overnight_observations([]) == []
    assert S.simulate_s30([]) == []
    assert S.build_overnight_observations([_bar(0, 100, 101, 99, 100)]) == []  # one bar, no t-1
    assert S.summarize_overnight([])["observation_count"] == 0
    assert S.validate_overnight_measurement([])["valid"] is True


# 15 — deterministic known sequence produces the expected total overnight points.
def test_known_sequence_total_points():
    obs = S.simulate_s30(_known_sequence())
    pts = [o["overnight_points"] for o in obs]
    assert pts == pytest.approx([1.0, 1.0, -1.0])
    assert sum(pts) == pytest.approx(1.0)


# 16 — measurement-validity failure raises (strict) and flags (non-strict).
def test_measurement_validity_failure_raises_or_flags():
    bad = [
        {"reconstruction_error": 0.0},
        {"reconstruction_error": 5.0},   # legs do not reconcile to the total
    ]
    flagged = S.validate_overnight_measurement(bad)        # non-strict -> flag
    assert flagged["valid"] is False
    assert flagged["max_abs_reconstruction_error"] == pytest.approx(5.0)
    with pytest.raises(S.MeasurementValidityError):
        S.validate_overnight_measurement(bad, strict=True)


# 17 — offline safety: engine source has no network/broker/secret tokens.
def test_engine_source_is_offline_inert():
    engine_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "engine", "s30_overnight_drift.py",
    )
    with open(engine_path, "r", encoding="utf-8") as fh:
        text = fh.read().lower()
    forbidden = [
        "requests", "urllib", "httpx", "aiohttp", "websockets", "socket",
        "ccxt", "binance", "bybit", "ib_insync", "alpaca", "api_key",
    ]
    hits = [tok for tok in forbidden if tok in text]
    assert hits == [], f"forbidden tokens in engine source: {hits}"


# 18 — no real CSV/data used: this suite never calls the file loader or backtest.
def test_no_real_data_used_in_suite():
    test_path = os.path.abspath(__file__)
    with open(test_path, "r", encoding="utf-8") as fh:
        text = fh.read()
    # Needles built by concatenation so they do not appear literally in this file.
    assert ("load_daily" + "_bars(") not in text
    assert ("run_" + "backtest(") not in text
    assert (".cs" + "v") not in text
