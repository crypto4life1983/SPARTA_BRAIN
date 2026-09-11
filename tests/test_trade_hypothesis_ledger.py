"""Tests for tools/trade_hypothesis_ledger.py — synthetic data only, never the
real trades.db. File I/O goes through tmp_path."""
from __future__ import annotations

import json

import pytest

from tools import trade_hypothesis_ledger as thl

AS_OF = "2026-09-11"


def _row(i, symbol="BTCUSDT", direction="long", strategy="D", regime="TREND_DOWN",
         open_date="2026-09-12", close_date="2026-09-14", pnl_r=-1.0, exchange="binance"):
    return {
        "id": i, "exchange": exchange, "symbol": symbol, "strategy": strategy,
        "direction": direction, "entry": 100.0, "sl": 95.0, "tp1": 110.0,
        "open_date": open_date, "close_date": close_date, "close_price": 95.0,
        "outcome": "WIN" if (pnl_r or 0) > 0 else "LOSS", "pnl_usd": None,
        "pnl_r": pnl_r, "regime_at_open": regime,
    }


def _sugg(sid, rule="r", evidence=None):
    return {"id": sid, "rule": rule, "evidence": evidence or {"n": 4, "avg_R": -0.3},
            "status": "SUGGESTION_ONLY", "sample_ok": True, "label": "OK", "caveat": "c"}


def _report(*ids):
    return {"suggestions": [_sugg(i) for i in ids]}


def _hyp(sid, registered=AS_OF, ledger=None):
    ledger = ledger if ledger is not None else thl.new_ledger(registered)
    thl.register_from_report(_report(sid), registered, ledger)
    return ledger, ledger["hypotheses"][sid]


# ── registration ────────────────────────────────────────────────────────────

def test_registration_creates_shadow_and_freezes_evidence():
    ledger = thl.new_ledger(AS_OF)
    added = thl.register_from_report(_report("block_long_in_TREND_DOWN"), AS_OF, ledger)
    assert added == ["block_long_in_TREND_DOWN"]
    h = ledger["hypotheses"]["block_long_in_TREND_DOWN"]
    assert h["status"] == "SHADOW"
    assert h["kind"] == "block"
    assert h["params"] == {"direction": "long", "regime": "TREND_DOWN", "alignment": "COUNTER"}
    assert h["registered_as_of"] == AS_OF
    assert h["registered_evidence"] == {"n": 4, "avg_R": -0.3}
    assert h["thresholds"] == thl.DEFAULT_THRESHOLDS
    assert h["history"][0]["status"] == "SHADOW"


def test_registration_idempotent_and_evidence_frozen():
    ledger = thl.new_ledger(AS_OF)
    thl.register_from_report(_report("enforce_hard_stop"), AS_OF, ledger)
    # second run: different evidence + later date must NOT overwrite
    rep2 = {"suggestions": [_sugg("enforce_hard_stop", evidence={"n_breaches": 99})]}
    added = thl.register_from_report(rep2, "2026-10-01", ledger)
    assert added == []
    h = ledger["hypotheses"]["enforce_hard_stop"]
    assert h["registered_as_of"] == AS_OF
    assert h["registered_evidence"] == {"n": 4, "avg_R": -0.3}
    assert len(h["history"]) == 1
    # suggestion disappearing from the report never deletes
    thl.register_from_report({"suggestions": []}, "2026-10-02", ledger)
    assert "enforce_hard_stop" in ledger["hypotheses"]


def test_unknown_id_stays_proposed_and_is_never_evaluated():
    ledger = thl.new_ledger(AS_OF)
    thl.register_from_report(_report("something_new_xyz"), AS_OF, ledger)
    h = ledger["hypotheses"]["something_new_xyz"]
    assert h["kind"] == "unknown" and h["status"] == "PROPOSED"
    trades = [_row(i, pnl_r=-1.0) for i in range(1, 30)]
    thl.update_forward(ledger, trades, {}, "2026-12-01")
    assert h["status"] == "PROPOSED"
    assert h["forward"]["n_signals"] == 0
    assert thl.evaluate_hypothesis(h, trades[0], None) is None


@pytest.mark.parametrize("sid,kind,params", [
    ("block_long_in_TREND_DOWN", "block", {"direction": "long", "regime": "TREND_DOWN", "alignment": "COUNTER"}),
    ("block_short_in_TREND_UP", "block", {"direction": "short", "regime": "TREND_UP", "alignment": "COUNTER"}),
    ("review_pause_D2", "block", {"strategy": "D2"}),
    ("enforce_hard_stop", "stop_cap", {"cap_R": -1.5}),
    ("partial_tp_or_trail_2R", "partial_2R", {"trigger_R": 2.0, "fraction": 0.5}),
    ("flag_weekday_Mon", "flag", {"weekday": "Mon"}),
    ("flag_Fri", "flag", {"weekday": "Fri"}),
    ("nonsense", "unknown", {}),
])
def test_kind_mapping(sid, kind, params):
    assert thl.kind_for_id(sid) == (kind, params)


# ── evaluators ──────────────────────────────────────────────────────────────

def test_block_evaluator():
    _, h = _hyp("block_long_in_TREND_DOWN")
    assert thl.evaluate_hypothesis(h, _row(1, pnl_r=-1.2)) == pytest.approx(1.2)
    assert thl.evaluate_hypothesis(h, _row(2, pnl_r=2.0)) == pytest.approx(-2.0)
    assert thl.evaluate_hypothesis(h, _row(3, direction="short")) is None
    assert thl.evaluate_hypothesis(h, _row(4, regime="TREND_UP")) is None
    assert thl.evaluate_hypothesis(h, _row(5, regime=None)) is None
    assert thl.evaluate_hypothesis(h, _row(6, pnl_r=None)) is None


def test_review_pause_is_strategy_block():
    _, h = _hyp("review_pause_D2")
    assert thl.evaluate_hypothesis(h, _row(1, strategy="D2", pnl_r=-0.8)) == pytest.approx(0.8)
    assert thl.evaluate_hypothesis(h, _row(2, strategy="D2", pnl_r=1.5)) == pytest.approx(-1.5)
    assert thl.evaluate_hypothesis(h, _row(3, strategy="D", pnl_r=-0.8)) is None


def test_stop_cap_evaluator():
    _, h = _hyp("enforce_hard_stop")
    assert thl.evaluate_hypothesis(h, _row(1, pnl_r=-4.6)) == pytest.approx(3.1)
    assert thl.evaluate_hypothesis(h, _row(2, pnl_r=-1.5)) is None
    assert thl.evaluate_hypothesis(h, _row(3, pnl_r=-1.0)) is None
    assert thl.evaluate_hypothesis(h, _row(4, pnl_r=2.0)) is None


def test_partial_2R_evaluator():
    _, h = _hyp("partial_tp_or_trail_2R")
    ex_hi = {"trade_id": 1, "max_favorable_R": 2.5}
    ex_lo = {"trade_id": 1, "max_favorable_R": 1.9}
    # reached 2R then closed at -1: rule locks 1.0R → delta +2.0
    assert thl.evaluate_hypothesis(h, _row(1, pnl_r=-1.0), ex_hi) == pytest.approx(2.0)
    # reached 2R, closed at +3: rule gives 1.0 + 0.5*3 = 2.5 → delta -0.5
    assert thl.evaluate_hypothesis(h, _row(2, pnl_r=3.0), ex_hi) == pytest.approx(-0.5)
    # reached 2R, closed at exactly +2: rule 2.0 → delta 0
    assert thl.evaluate_hypothesis(h, _row(3, pnl_r=2.0), ex_hi) == pytest.approx(0.0)
    # never reached 2R → not applicable
    assert thl.evaluate_hypothesis(h, _row(4, pnl_r=1.0), ex_lo) is None
    # no excursion row → unknown
    assert thl.evaluate_hypothesis(h, _row(5, pnl_r=1.0), None) is None


def test_flag_evaluator():
    _, h = _hyp("flag_weekday_Mon")
    mon = _row(1, open_date="2026-09-14", pnl_r=-2.0)   # 2026-09-14 is a Monday
    tue = _row(2, open_date="2026-09-15", pnl_r=-2.0)
    assert thl.evaluate_hypothesis(h, mon) == pytest.approx(2.0)
    assert thl.evaluate_hypothesis(h, tue) is None


# ── forward evaluation ──────────────────────────────────────────────────────

def test_forward_ignores_trades_closed_on_or_before_registration():
    ledger, h = _hyp("block_long_in_TREND_DOWN")
    trades = [
        _row(1, close_date="2026-09-10", pnl_r=-1.0),               # before
        _row(2, close_date="2026-09-11", pnl_r=-1.0),               # same day → excluded
        _row(3, close_date="2026-09-11T23:59:00", pnl_r=-1.0),      # same day (datetime) → excluded
        _row(4, open_date="2026-09-12", close_date="2026-09-12", pnl_r=-1.0),  # after → counted
        _row(5, open_date="2026-09-13", close_date=None, pnl_r=None),          # open → skipped
    ]
    thl.update_forward(ledger, trades, {}, "2026-09-20")
    f = h["forward"]
    assert f["n_signals"] == 1
    assert f["trade_ids_evaluated"] == [4]
    assert f["delta_R_sum"] == pytest.approx(1.0)
    assert f["last_eval_as_of"] == "2026-09-20"
    assert f["bootstrap_p_positive"] is None  # n < 5


def test_forward_skips_already_evaluated_ids_and_accumulates():
    ledger, h = _hyp("block_long_in_TREND_DOWN")
    t1 = [_row(1, open_date="2026-09-12", close_date="2026-09-13", pnl_r=-1.0)]
    thl.update_forward(ledger, t1, {}, "2026-09-14")
    assert h["forward"]["n_signals"] == 1
    # same trade again + one new one
    t2 = t1 + [_row(2, open_date="2026-09-15", close_date="2026-09-16", pnl_r=0.5)]
    thl.update_forward(ledger, t2, {}, "2026-09-17")
    f = h["forward"]
    assert f["n_signals"] == 2
    assert f["trade_ids_evaluated"] == [1, 2]
    assert f["delta_R_sum"] == pytest.approx(0.5)
    assert f["wins"] == 1 and f["losses"] == 1
    # third run with nothing new is a no-op on the stats
    thl.update_forward(ledger, t2, {}, "2026-09-18")
    assert f["n_signals"] == 2 and f["delta_R_sum"] == pytest.approx(0.5)


def test_forward_dedups_mirrored_rows_to_best_R_row():
    ledger, h = _hyp("block_long_in_TREND_DOWN")
    trades = [
        _row(1, exchange="binance", open_date="2026-09-12", close_date="2026-09-13", pnl_r=-1.0),
        _row(2, exchange="kraken", open_date="2026-09-12", close_date="2026-09-13", pnl_r=-0.4),
    ]
    thl.update_forward(ledger, trades, {}, "2026-09-14")
    f = h["forward"]
    assert f["n_signals"] == 1
    assert f["n_rows"] == 2
    assert f["trade_ids_evaluated"] == [1, 2]
    assert f["samples"][0]["trade_id"] == 2          # best-R row (-0.4 > -1.0)
    assert f["delta_R_sum"] == pytest.approx(0.4)
    # a late-closing mirror of the same signal must not be double counted
    trades.append(_row(3, exchange="kraken", open_date="2026-09-12", close_date="2026-09-20", pnl_r=-1.0))
    thl.update_forward(ledger, trades, {}, "2026-09-21")
    assert f["n_signals"] == 1


def test_forward_non_applicable_trade_not_marked_evaluated():
    ledger, h = _hyp("partial_tp_or_trail_2R")
    t = [_row(1, open_date="2026-09-12", close_date="2026-09-13", pnl_r=-1.0)]
    thl.update_forward(ledger, t, {}, "2026-09-14")      # no excursion yet → unknown
    assert h["forward"]["n_signals"] == 0 and h["forward"]["trade_ids_evaluated"] == []
    thl.update_forward(ledger, t, {1: {"max_favorable_R": 2.2}}, "2026-09-15")
    assert h["forward"]["n_signals"] == 1
    assert h["forward"]["delta_R_sum"] == pytest.approx(2.0)


def test_bootstrap_deterministic_and_min_n():
    d = [1.0, -0.2, 0.5, 0.3, -0.1, 0.8, 0.2]
    a = thl.bootstrap_p_positive(d)
    b = thl.bootstrap_p_positive(list(d))
    assert a == b and 0.9 <= a <= 1.0
    assert thl.bootstrap_p_positive([1.0, 1.0, 1.0, 1.0]) is None
    assert thl.bootstrap_p_positive([-1.0] * 10) == 0.0
    assert thl.bootstrap_p_positive([1.0] * 10) == 1.0


def _n_trades(n, pnl_fn, start_id=1):
    out = []
    for k in range(n):
        d = 12 + k  # distinct open dates → distinct signals; keep in September/October
        month, day = (9, d) if d <= 30 else (10, d - 30)
        od = f"2026-{month:02d}-{day:02d}"
        out.append(_row(start_id + k, open_date=od, close_date=od, pnl_r=pnl_fn(k)))
    return out


def test_promotion_to_confirmed_at_threshold():
    ledger, h = _hyp("block_long_in_TREND_DOWN")
    thl.update_forward(ledger, _n_trades(19, lambda k: -1.0), {}, "2026-10-01")
    assert h["status"] == "SHADOW"                       # 19 < 20
    thl.update_forward(ledger, _n_trades(20, lambda k: -1.0), {}, "2026-10-02")
    assert h["status"] == "CONFIRMED"
    assert h["forward"]["n_signals"] == 20
    assert h["forward"]["bootstrap_p_positive"] == 1.0
    assert h["history"][-1]["status"] == "CONFIRMED"
    assert h["history"][-1]["as_of"] == "2026-10-02"
    assert len(h["history"]) == 2


def test_rejection_at_threshold():
    ledger, h = _hyp("block_long_in_TREND_DOWN")
    thl.update_forward(ledger, _n_trades(20, lambda k: 1.0), {}, "2026-10-02")  # all winners: blocking hurts
    assert h["status"] == "REJECTED"
    assert h["forward"]["bootstrap_p_positive"] == 0.0
    assert h["history"][-1]["status"] == "REJECTED"
    # terminal: further trades are not evaluated
    thl.update_forward(ledger, _n_trades(25, lambda k: -1.0), {}, "2026-10-03")
    assert h["status"] == "REJECTED" and h["forward"]["n_signals"] == 20


def test_mixed_evidence_stays_shadow():
    ledger, h = _hyp("block_long_in_TREND_DOWN")
    # 13 blocked losers (delta +1) vs 11 blocked winners (delta -1): slightly positive, ambiguous
    thl.update_forward(ledger, _n_trades(24, lambda k: -1.0 if k < 13 else 1.0), {}, "2026-10-05")
    assert h["status"] == "SHADOW"
    p = h["forward"]["bootstrap_p_positive"]
    assert 0.5 < p < 0.9


def test_update_forward_is_deterministic():
    trades = _n_trades(12, lambda k: -0.5 if k % 3 else 1.2)
    l1, _ = _hyp("block_long_in_TREND_DOWN")
    l2, _ = _hyp("block_long_in_TREND_DOWN")
    thl.update_forward(l1, trades, {}, "2026-10-05")
    thl.update_forward(l2, list(reversed(trades)), {}, "2026-10-05")
    assert json.dumps(l1, sort_keys=True) == json.dumps(l2, sort_keys=True)


# ── markdown ────────────────────────────────────────────────────────────────

def test_markdown_banner_and_no_forbidden_words():
    ledger = thl.new_ledger(AS_OF)
    thl.register_from_report(
        _report("block_long_in_TREND_DOWN", "enforce_hard_stop", "partial_tp_or_trail_2R",
                "review_pause_D2", "flag_weekday_Mon", "weird_id"),
        AS_OF, ledger)
    thl.update_forward(ledger, _n_trades(20, lambda k: -1.0), {}, "2026-10-02")
    md = thl.render_markdown(ledger)
    assert thl.BANNER in md
    assert thl.forbidden_words_found(md) == []
    assert "What a CONFIRMED rule means" in md
    assert "Nothing is applied automatically" in md
    assert "| block_long_in_TREND_DOWN | **CONFIRMED** |" in md
    assert "| weird_id | **PROPOSED** |" in md
    assert "need 20 forward signals" in md
    assert thl.forbidden_words_found("this is already done") == ["ready"]


def test_markdown_empty_ledger():
    md = thl.render_markdown(thl.new_ledger(AS_OF))
    assert thl.BANNER in md and thl.forbidden_words_found(md) == []


# ── file cycle ──────────────────────────────────────────────────────────────

def test_run_cycle_writes_files_and_is_idempotent(tmp_path):
    lp = tmp_path / "data" / "ledger.json"
    rd = tmp_path / "reports"
    rep = _report("block_long_in_TREND_DOWN", "enforce_hard_stop")
    trades = [_row(1, close_date="2026-09-10", pnl_r=-1.0)]  # closed before registration
    out = thl.run_cycle(rep, trades, {}, AS_OF, ledger_path=lp, report_dir=rd)
    assert lp.exists() and (rd / thl.MD_NAME).exists() and (rd / thl.HISTORY_NAME).exists()
    assert out["_last_run"]["registered"] == ["block_long_in_TREND_DOWN", "enforce_hard_stop"]
    assert out["_last_run"]["forward_n"] == {"block_long_in_TREND_DOWN": 0, "enforce_hard_stop": 0}
    saved = json.loads(lp.read_text(encoding="utf-8"))
    assert "_last_run" not in saved
    assert set(saved["hypotheses"]) == {"block_long_in_TREND_DOWN", "enforce_hard_stop"}
    assert saved["posture"]["rules_applied"] is False
    # second run: nothing re-registered, history gets a second line
    out2 = thl.run_cycle(rep, trades, {}, "2026-09-12", ledger_path=lp, report_dir=rd)
    assert out2["_last_run"]["registered"] == []
    assert len((rd / thl.HISTORY_NAME).read_text(encoding="utf-8").strip().splitlines()) == 2
    assert json.loads(lp.read_text(encoding="utf-8"))["hypotheses"]["enforce_hard_stop"]["registered_as_of"] == AS_OF
