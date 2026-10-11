"""Generic 'partial_tp_or_trail_<X>R' hypotheses (2026-10-11).

The bot's 2R partial is APPLIED. Three 2026-10 timeouts reached +1.08/+1.32/
+1.58R and gave it all back, so a 1R trigger is scored in shadow with the same
evaluator and the bot's own excursion rows. These tests pin id parsing, the
1R arithmetic, frozen post-fix evidence, forward scoring that waits for the
excursion row, mirrored-row collapse, thresholds, and a clean render. tmp_path
only, never the real trades.db.
"""
from __future__ import annotations

import pytest

from tools import trade_hypothesis_ledger as thl

AS_OF = "2026-10-11"
SID = "partial_tp_or_trail_1R"


def _trade(tid, symbol, open_date, close_date, pnl_r, *, outcome=None, exchange="binance", strategy="D"):
    return {"id": tid, "exchange": exchange, "symbol": symbol, "strategy": strategy, "direction": "long",
            "entry": 100.0, "sl": 90.0, "tp1": 130.0, "tp1_hit": 0, "atr14": 5.0, "size_usd": 20.0,
            "open_date": open_date, "close_date": close_date,
            "outcome": outcome or ("WIN" if pnl_r > 0 else "LOSS"), "pnl_r": pnl_r,
            "pnl_usd": pnl_r * 20.0, "regime_at_open": "TREND_UP"}


def _ex(tid, mfe):
    return {"trade_id": tid, "max_favorable_R": mfe, "max_adverse_R": -0.4, "did_reach_1R": int(mfe >= 1)}


# ── id -> kind ────────────────────────────────────────────────────────────────

def test_kind_for_generic_partial_ids():
    assert thl.kind_for_id("partial_tp_or_trail_1R") == ("partial", {"trigger_R": 1.0, "fraction": 0.5})
    assert thl.kind_for_id("partial_tp_or_trail_1.5R") == ("partial", {"trigger_R": 1.5, "fraction": 0.5})
    assert thl.kind_for_id("partial_tp_or_trail_2R") == ("partial_2R", {"trigger_R": 2.0, "fraction": 0.5})
    assert thl.kind_for_id("partial_tp_or_trail_0R") == ("unknown", {})
    assert thl.kind_for_id("partial_tp_or_trail_-1R") == ("unknown", {})
    assert thl.kind_for_id("partial_tp_or_trail_xR") == ("unknown", {})
    assert thl.kind_for_id("partial_tp_or_trail_1") == ("unknown", {})
    assert thl.partial_id(1.0) == SID and thl.partial_id(1.5) == "partial_tp_or_trail_1.5R"


# ── the 1R arithmetic on the trades that prompted it ──────────────────────────

def test_one_r_evaluator_on_the_october_timeouts():
    ledger = thl.new_ledger(AS_OF)
    thl.register_partial(ledger, 1.0, AS_OF, [], {})
    h = ledger["hypotheses"][SID]
    sol = _trade(58, "SOLUSDT", "2026-09-19", "2026-10-09", -0.332, outcome="TIMEOUT")
    avax = _trade(61, "AVAXUSDT", "2026-09-20", "2026-10-10", 0.182, outcome="TIMEOUT")
    # SOL reached +1.08R, closed -0.332: rule = 0.5 + 0 → delta +0.832
    assert thl.evaluate_hypothesis(h, sol, _ex(58, 1.08)) == pytest.approx(0.832)
    # AVAX reached +1.58R, closed +0.182: rule = 0.5 + 0.091 → delta +0.409
    assert thl.evaluate_hypothesis(h, avax, _ex(61, 1.58)) == pytest.approx(0.409)
    # a runner that went on to +3R gives back 1.0R under the rule
    assert thl.evaluate_hypothesis(h, _trade(1, "X", "2026-10-01", "2026-10-05", 3.0), _ex(1, 3.2)) == pytest.approx(-1.0)
    # never reached 1R, or no excursion row yet → not applicable
    assert thl.evaluate_hypothesis(h, sol, _ex(58, 0.9)) is None
    assert thl.evaluate_hypothesis(h, sol, None) is None


# ── registration freezes post-fix evidence ───────────────────────────────────

def _history():
    trades = [_trade(40, "ETHUSDT", "2026-09-01", "2026-09-21", 0.5),                      # pre-fix: retired
              _trade(58, "SOLUSDT", "2026-09-19", "2026-10-09", -0.332, outcome="TIMEOUT"),
              _trade(59, "ARBUSDT", "2026-09-19", "2026-10-09", -1.022),                   # never reached 1R
              _trade(61, "AVAXUSDT", "2026-09-20", "2026-10-10", 0.182, outcome="TIMEOUT"),
              _trade(66, "DOGEUSDT", "2026-09-21", "2026-10-10", 0.0)]                     # no excursion row
    ex = {40: _ex(40, 2.5), 58: _ex(58, 1.08), 59: _ex(59, 0.3), 61: _ex(61, 1.58)}
    return trades, ex


def test_register_freezes_post_fix_evidence_and_is_idempotent():
    ledger = thl.new_ledger(AS_OF)
    trades, ex = _history()
    assert thl.register_partial(ledger, 1.0, AS_OF, trades, ex, note="three flat timeouts") == SID
    h = ledger["hypotheses"][SID]
    assert h["status"] == "SHADOW" and h["kind"] == "partial" and h["params"] == {"trigger_R": 1.0, "fraction": 0.5}
    ev = h["registered_evidence"]
    assert ev["n_closed"] == 4 and ev["n_with_excursion"] == 3 and ev["n_reached_trigger"] == 2
    assert ev["sum_delta_R"] == pytest.approx(0.832 + 0.409, abs=1e-3)
    assert ev["evidence_from"] == thl.EVIDENCE_VALID_FROM
    assert "three flat timeouts" in h["history"][0]["note"]
    assert thl.register_partial(ledger, 1.0, "2026-10-12", [], {}) is None          # untouched
    assert ledger["hypotheses"][SID]["registered_as_of"] == AS_OF
    assert thl.register_partial(ledger, 0.0, AS_OF, [], {}) is None
    assert thl.register_partial(ledger, "abc", AS_OF, [], {}) is None


def test_register_never_touches_the_applied_2R_entry():
    ledger = thl.new_ledger("2026-09-11")
    thl.register_from_report({"suggestions": [{"id": "partial_tp_or_trail_2R", "rule": "r"}]}, "2026-09-11", ledger)
    before = dict(ledger["hypotheses"]["partial_tp_or_trail_2R"])
    assert thl.register_partial(ledger, 2.0, AS_OF, [], {}) is None
    assert ledger["hypotheses"]["partial_tp_or_trail_2R"] == before


def test_evidence_respects_the_up_to_date():
    trades, ex = _history()
    trades.append(_trade(70, "LINKUSDT", "2026-10-01", "2026-10-21", 0.1))
    ex[70] = _ex(70, 1.4)
    assert thl.partial_evidence(1.0, trades, ex, up_to=AS_OF)["n_reached_trigger"] == 2
    assert thl.partial_evidence(1.0, trades, ex, up_to="2026-10-31")["n_reached_trigger"] == 3


# ── forward scoring ──────────────────────────────────────────────────────────

def test_forward_scores_closes_after_registration_once_the_excursion_row_exists():
    ledger = thl.new_ledger(AS_OF)
    thl.register_partial(ledger, 1.0, AS_OF, [], {})
    trades = [
        _trade(61, "AVAXUSDT", "2026-09-20", "2026-10-10", 0.182, outcome="TIMEOUT"),   # before reg
        _trade(63, "COMPUSDT", "2026-09-23", "2026-10-13", -0.2, outcome="TIMEOUT"),    # after, reached 1.52R
        _trade(64, "ATOMUSDT", "2026-10-10", "2026-10-20", -1.0),                       # after, never reached
        _trade(65, "TRXUSDT", "2026-10-11", "2026-10-15", 0.4),                         # after, row arrives later
    ]
    ex = {61: _ex(61, 1.58), 63: _ex(63, 1.52), 64: _ex(64, 0.2)}
    s = thl.update_forward(ledger, trades, ex, "2026-10-21")
    f = ledger["hypotheses"][SID]["forward"]
    assert s["evaluated"][SID]["new_signals"] == 1
    assert f["n_signals"] == 1 and f["samples"][0]["trade_id"] == 63
    assert f["samples"][0]["delta_R"] == pytest.approx(0.7)       # 0.5 + 0 - (-0.2)
    assert f["trade_ids_evaluated"] == [63]
    thl.update_forward(ledger, trades, ex, "2026-10-22")
    assert f["n_signals"] == 1
    ex[65] = _ex(65, 1.1)
    thl.update_forward(ledger, trades, ex, "2026-10-23")
    assert f["n_signals"] == 2 and f["samples"][-1]["delta_R"] == pytest.approx(0.5 + 0.2 - 0.4)
    assert ledger["hypotheses"][SID]["status"] == "SHADOW"


def test_mirrored_exchange_rows_collapse_to_one_signal():
    ledger = thl.new_ledger(AS_OF)
    thl.register_partial(ledger, 1.0, AS_OF, [], {})
    trades = [_trade(70, "BTCUSDT", "2026-10-12", "2026-10-20", 0.05, exchange="binance"),
              _trade(71, "BTCUSDT", "2026-10-12", "2026-10-20", 0.02, exchange="kraken")]
    thl.update_forward(ledger, trades, {70: _ex(70, 1.3), 71: _ex(71, 1.3)}, "2026-10-21")
    f = ledger["hypotheses"][SID]["forward"]
    assert f["n_signals"] == 1 and f["n_rows"] == 2 and f["samples"][0]["trade_id"] == 70
    assert f["samples"][0]["delta_R"] == pytest.approx(0.5 + 0.025 - 0.05)


def test_thresholds_decide_from_forward_rows():
    trades = [_trade(100 + i, f"S{i}USDT", "2026-10-12", "2026-10-20", 3.0) for i in range(22)]
    ex = {100 + i: _ex(100 + i, 3.5) for i in range(22)}
    ledger = thl.new_ledger(AS_OF)
    thl.register_partial(ledger, 1.0, AS_OF, [], {})
    thl.update_forward(ledger, trades, ex, "2026-11-01")          # every runner gave back 1R → rejected
    assert ledger["hypotheses"][SID]["status"] == "REJECTED"
    ledger = thl.new_ledger(AS_OF)
    thl.register_partial(ledger, 1.0, AS_OF, [], {})
    stopped = [dict(t, pnl_r=-1.0, outcome="LOSS") for t in trades]
    thl.update_forward(ledger, stopped, ex, "2026-11-01")         # every runner round-tripped to the stop
    assert ledger["hypotheses"][SID]["status"] == "CONFIRMED"


# ── cycle + render ───────────────────────────────────────────────────────────

def test_cycle_renders_the_kind_without_forbidden_words(tmp_path):
    ledger_path, report_dir = tmp_path / "l.json", tmp_path / "rep"
    ledger = thl.new_ledger(AS_OF)
    thl.register_partial(ledger, 1.0, AS_OF, [], {})
    thl.save_ledger(ledger, ledger_path)
    t = _trade(63, "COMPUSDT", "2026-09-23", "2026-10-13", -0.2, outcome="TIMEOUT")
    out = thl.run_cycle({"suggestions": []}, [t], {63: _ex(63, 1.52)}, "2026-10-21",
                        ledger_path=ledger_path, report_dir=report_dir, outcomes=[])
    assert out["hypotheses"][SID]["forward"]["n_signals"] == 1
    md = (report_dir / thl.MD_NAME).read_text(encoding="utf-8")
    assert SID in md and "| partial |" in md
    assert thl.forbidden_words_found(md) == []
