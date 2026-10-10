"""Timeout hindsight resolver (2026-10-10): what a longer hold would have done.

Origin: on 2026-10-09/10 three paper trades opened 09-19/20 closed as TIMEOUT at
20 days held with the market flat (SOL -0.33R, BTC +0.08R, AVAX +0.18R). The
journal cannot say whether holding longer would have helped, so this resolver
walks the daily bars after the close. Pure functions tested here, network
replaced by a fake fetch, files on tmp_path only.
"""
from __future__ import annotations

from datetime import date

import pytest

from tools import trade_timeout_hindsight as tth

#: trade #58 as stored after the 2026-10-09 run: SOL D long on kraken, timed out.
SOL = {"id": 58, "exchange": "kraken", "symbol": "SOLUSDT", "strategy": "D", "direction": "long",
       "entry": 112.69, "sl": 101.33359466447087, "tp1": 146.7592160065874, "tp1_hit": 0,
       "atr14": 5.678202667764567, "size_usd": 33.56, "open_date": "2026-09-19",
       "close_date": "2026-10-09", "close_price": 109.5, "outcome": "TIMEOUT", "pnl_r": -0.332}
#: trade #61: AVAX F long on binance, timed out a day later.
AVAX = {"id": 61, "exchange": "binance", "symbol": "AVAXUSDT", "strategy": "F", "direction": "long",
        "entry": 10.094, "sl": 8.87918657748177, "tp1": 12.059568117634495, "tp1_hit": 0,
        "atr14": 0.6074067112591145, "size_usd": 40.0, "open_date": "2026-09-20",
        "close_date": "2026-10-10", "close_price": 10.335, "outcome": "TIMEOUT", "pnl_r": 0.182}


def _bars(start: str, closes: list[float], spread: float = 0.5) -> list[dict]:
    d = date.fromisoformat(start)
    out = []
    for i, c in enumerate(closes):
        day = date.fromordinal(d.toordinal() + i).isoformat()
        out.append({"day": day, "open": c, "high": c + spread, "low": c - spread, "close": c})
    return out


# ── arithmetic mirrors the bot ────────────────────────────────────────────────

def test_pnl_r_reproduces_the_bots_realized_r_at_the_actual_exit():
    assert tth.pnl_r(SOL, 109.5) == pytest.approx(-0.332, abs=0.002)      # kraken fees
    assert tth.pnl_r(AVAX, 10.335) == pytest.approx(0.182, abs=0.002)     # binance fees


def test_risk_unit_falls_back_to_2atr_when_the_stop_sits_at_breakeven():
    assert tth.risk_unit(SOL) == pytest.approx(11.3564, abs=1e-3)
    be = dict(SOL, sl=SOL["entry"])
    assert tth.risk_unit(be) == pytest.approx(2 * SOL["atr14"])
    assert tth.risk_unit(dict(be, atr14=None)) is None
    assert tth.pnl_r(dict(be, atr14=None), 120.0) is None


def test_extension_window_is_the_bars_the_bot_never_saw():
    assert tth.extension_window(SOL, 40) == (date(2026, 10, 9), 20)
    assert tth.extension_window(SOL, 25) == (date(2026, 10, 9), 5)
    assert tth.extension_window(SOL, 20) is None
    assert tth.extension_window(dict(SOL, close_date=None), 40) is None


def test_only_timeout_closes_with_a_risk_unit_are_candidates():
    assert tth.is_candidate(SOL)
    assert not tth.is_candidate(dict(SOL, outcome="LOSS"))
    assert not tth.is_candidate(dict(SOL, pnl_r=None))
    assert not tth.is_candidate(dict(SOL, sl=SOL["entry"], atr14=None))
    assert not tth.is_candidate(dict(SOL, tp1=None))


# ── the walk ─────────────────────────────────────────────────────────────────

def test_horizon_exit_at_the_last_bars_close():
    bars = _bars("2026-10-09", [110.0] * 20)
    s = tth.simulate_extension(SOL, bars, 40)
    assert s["resolved"] and s["exit_reason"] == tth.EXIT_HORIZON
    assert s["exit_price"] == 110.0 and s["exit_day"] == "2026-10-28"
    assert s["bars_needed"] == 20 and s["bars_used"] == 20


def test_target_touch_exits_at_tp1_on_that_day():
    bars = _bars("2026-10-09", [110.0] * 5 + [150.0] + [120.0] * 14)
    s = tth.simulate_extension(SOL, bars, 40)
    assert s["exit_reason"] == tth.EXIT_TARGET and s["exit_day"] == "2026-10-14"
    assert s["exit_price"] == pytest.approx(SOL["tp1"])


def test_stop_is_checked_before_target_within_a_bar():
    wide = _bars("2026-10-09", [110.0] * 20)
    wide[3].update(high=200.0, low=90.0)   # both touched on the same day → pessimistic
    s = tth.simulate_extension(SOL, wide, 40)
    assert s["exit_reason"] == tth.EXIT_STOP and s["exit_day"] == "2026-10-12"
    assert s["exit_price"] == pytest.approx(SOL["sl"])


def test_bars_before_the_window_and_beyond_the_horizon_are_ignored():
    bars = _bars("2026-10-01", [200.0] * 8) + _bars("2026-10-09", [110.0] * 20) + _bars("2026-10-29", [300.0] * 3)
    s = tth.simulate_extension(SOL, bars, 40)
    assert s["exit_reason"] == tth.EXIT_HORIZON and s["exit_price"] == 110.0


def test_short_window_without_a_touch_stays_unresolved():
    s = tth.simulate_extension(SOL, _bars("2026-10-09", [110.0] * 7), 40)
    assert not s["resolved"] and s["exit_reason"] is None and s["bars_used"] == 7


def test_short_side_mirrors_the_levels():
    short = dict(SOL, direction="short", sl=120.0, tp1=100.0)
    bars = _bars("2026-10-09", [110.0] * 2 + [99.0] + [110.0] * 17)
    assert tth.simulate_extension(short, bars, 40)["exit_reason"] == tth.EXIT_TARGET
    bars[1].update(high=121.0)
    assert tth.simulate_extension(short, bars, 40)["exit_reason"] == tth.EXIT_STOP


def test_hindsight_row_carries_the_delta_against_the_realized_r():
    r = tth.hindsight_row(SOL, _bars("2026-10-09", [110.0] * 20), 40, "2026-10-29")
    assert r["resolved"] and r["trade_id"] == 58 and r["horizon_days"] == 40
    assert r["sim_pnl_r"] == pytest.approx(tth.pnl_r(SOL, 110.0))
    assert r["delta_R"] == pytest.approx(r["sim_pnl_r"] - (-0.332), abs=1e-4)
    assert r["resolved_as_of"] == "2026-10-29" and r["error"] is None
    pending = tth.hindsight_row(SOL, [], 40, "2026-10-12", error="URLError: boom")
    assert not pending["resolved"] and pending["delta_R"] is None and pending["error"].startswith("URLError")


# ── cache + refresh (fake network) ───────────────────────────────────────────

class _Fetch:
    def __init__(self, bars_by_symbol, fail=()):
        self.bars, self.fail, self.calls = bars_by_symbol, set(fail), []

    def __call__(self, symbol, start_day, limit):
        self.calls.append((symbol, start_day, limit))
        if symbol in self.fail:
            raise OSError("network down")
        return self.bars.get(symbol, [])


def test_refresh_resolves_once_and_never_refetches_a_resolved_row(tmp_path):
    p = tmp_path / "h.jsonl"
    fetch = _Fetch({"SOLUSDT": _bars("2026-10-09", [110.0] * 20)})
    loss = dict(AVAX, id=59, outcome="LOSS", pnl_r=-1.022)
    rows = tth.refresh([SOL, loss], [40], "2026-10-30", path=p, fetch=fetch, today=date(2026, 10, 30))
    assert [tth.hindsight_key(r) for r in rows] == [(58, 40)]
    assert rows[0]["resolved"] and fetch.calls == [("SOLUSDT", date(2026, 10, 9), 22)]
    rows2 = tth.refresh([SOL, loss], [40], "2026-10-31", path=p, fetch=fetch, today=date(2026, 10, 31))
    assert len(fetch.calls) == 1 and rows2[0]["resolved_as_of"] == "2026-10-30"
    assert tth.load_hindsight(p) == rows2


def test_refresh_waits_until_a_bar_can_exist_and_retries_pending_rows(tmp_path):
    p = tmp_path / "h.jsonl"
    fetch = _Fetch({"SOLUSDT": _bars("2026-10-09", [110.0] * 3)})
    # the morning of the close: no completed bar in the window yet → no fetch
    assert tth.refresh([SOL], [40], "2026-10-09", path=p, fetch=fetch, today=date(2026, 10, 9)) == []
    assert fetch.calls == []
    rows = tth.refresh([SOL], [40], "2026-10-12", path=p, fetch=fetch, today=date(2026, 10, 12))
    assert len(fetch.calls) == 1 and not rows[0]["resolved"] and rows[0]["bars_used"] == 3
    fetch.bars["SOLUSDT"] = _bars("2026-10-09", [110.0] * 20)
    rows = tth.refresh([SOL], [40], "2026-10-29", path=p, fetch=fetch, today=date(2026, 10, 29))
    assert len(fetch.calls) == 2 and rows[0]["resolved"] and rows[0]["exit_reason"] == tth.EXIT_HORIZON


def test_refresh_survives_a_failing_symbol_and_honours_the_fetch_cap(tmp_path):
    p = tmp_path / "h.jsonl"
    fetch = _Fetch({"AVAXUSDT": _bars("2026-10-10", [10.3] * 20)}, fail={"SOLUSDT"})
    rows = tth.refresh([SOL, AVAX], [40], "2026-10-30", path=p, fetch=fetch, today=date(2026, 10, 30))
    by = {tth.hindsight_key(r): r for r in rows}
    assert not by[(58, 40)]["resolved"] and "network down" in by[(58, 40)]["error"]
    assert by[(61, 40)]["resolved"]
    fetch2 = _Fetch({"SOLUSDT": _bars("2026-10-09", [110.0] * 20), "AVAXUSDT": _bars("2026-10-10", [10.3] * 20)})
    rows = tth.refresh([SOL, AVAX], [40], "2026-10-30", path=tmp_path / "cap.jsonl", fetch=fetch2,
                       today=date(2026, 10, 30), max_fetches=1)
    assert len(fetch2.calls) == 1 and len(rows) == 1


def test_loader_tolerates_junk_and_last_row_wins(tmp_path):
    p = tmp_path / "h.jsonl"
    p.write_text('not json\n{"a": 1}\n{"trade_id": 58, "horizon_days": 40, "resolved": false}\n'
                 '{"trade_id": 58, "horizon_days": 40, "resolved": true}\n', encoding="utf-8")
    rows = tth.load_hindsight(p)
    assert len(rows) == 2 and tth.index_hindsight(rows)[(58, 40)]["resolved"] is True
    assert tth.load_hindsight(tmp_path / "absent.jsonl") == []


def test_summary_counts_exit_reasons():
    rows = [tth.hindsight_row(SOL, _bars("2026-10-09", [110.0] * 20), 40, "x"),
            tth.hindsight_row(AVAX, _bars("2026-10-10", [10.3] * 2 + [13.0] + [10.3] * 17), 40, "x"),
            tth.hindsight_row(dict(SOL, id=70), _bars("2026-10-09", [110.0] * 2), 40, "x")]
    s = tth.summarize(rows, 40)
    assert s["n_timeouts"] == 3 and s["n_resolved"] == 2
    assert s["would_hit_target"] == 1 and s["still_open_at_horizon"] == 1 and s["would_hit_stop"] == 0
    assert s["mean_delta_R"] == pytest.approx((rows[0]["delta_R"] + rows[1]["delta_R"]) / 2, abs=1e-4)
