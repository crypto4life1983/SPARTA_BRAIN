"""'extend_timeout' hypotheses (2026-10-10): would a longer hold have helped?

The bot closes at 20 days held. These tests pin the ledger side: id parsing,
frozen post-fix evidence, forward scoring from the resolver's rows only once
resolved, mirrored-row collapse, and a cycle that never touches the network
unless such a hypothesis is active. tmp_path only.
"""
from __future__ import annotations

import pytest

from tools import trade_hypothesis_ledger as thl
from tools import trade_timeout_hindsight as tth

AS_OF = "2026-10-10"
SID = "extend_timeout__40"


def _trade(tid, symbol, open_date, close_date, pnl_r, *, outcome="TIMEOUT", exchange="binance",
           entry=100.0, sl=90.0, tp1=130.0):
    return {"id": tid, "exchange": exchange, "symbol": symbol, "strategy": "D", "direction": "long",
            "entry": entry, "sl": sl, "tp1": tp1, "tp1_hit": 0, "atr14": 5.0, "size_usd": 20.0,
            "open_date": open_date, "close_date": close_date, "outcome": outcome, "pnl_r": pnl_r,
            "pnl_usd": pnl_r * 20.0, "regime_at_open": "TREND_UP"}


def _row(tid, sim_r, *, horizon=40, resolved=True, reason=tth.EXIT_HORIZON):
    return {"trade_id": tid, "horizon_days": horizon, "resolved": resolved,
            "exit_reason": reason if resolved else None, "sim_pnl_r": sim_r if resolved else None,
            "delta_R": None, "symbol": "X", "strategy": "D"}


# ── id -> kind ────────────────────────────────────────────────────────────────

def test_kind_for_extend_timeout_id():
    assert thl.kind_for_id("extend_timeout__40") == ("extend_timeout", {"horizon_days": 40})
    assert thl.kind_for_id("extend_timeout__20") == ("unknown", {})      # not longer than the bot
    assert thl.kind_for_id("extend_timeout__x") == ("unknown", {})
    assert thl.kind_for_id("extend_timeout__") == ("unknown", {})


# ── registration freezes post-fix timeouts only ──────────────────────────────

def _history_trades():
    return [_trade(40, "ETHUSDT", "2026-09-01", "2026-09-21", 0.5),          # pre-fix: retired
            _trade(58, "SOLUSDT", "2026-09-19", "2026-10-09", -0.332),
            _trade(59, "ARBUSDT", "2026-09-19", "2026-10-09", -1.022, outcome="LOSS"),
            _trade(61, "AVAXUSDT", "2026-09-20", "2026-10-10", 0.182)]


def test_register_freezes_post_fix_evidence_and_is_idempotent():
    ledger = thl.new_ledger(AS_OF)
    rows = [_row(40, 2.0), _row(58, -0.5), _row(61, 1.4, reason=tth.EXIT_TARGET)]
    sid = thl.register_extend_timeout(ledger, 40, AS_OF, _history_trades(), rows, note="three flat timeouts")
    assert sid == SID
    h = ledger["hypotheses"][sid]
    assert h["status"] == "SHADOW" and h["kind"] == "extend_timeout" and h["params"] == {"horizon_days": 40}
    ev = h["registered_evidence"]
    assert ev["n_timeouts"] == 2 and ev["n_resolved"] == 2          # #40 retired, #59 not a timeout
    assert ev["would_hit_target"] == 1 and ev["still_open_at_horizon"] == 1
    assert ev["evidence_from"] == thl.EVIDENCE_VALID_FROM
    assert "three flat timeouts" in h["history"][0]["note"]
    assert thl.register_extend_timeout(ledger, 40, "2026-10-11", [], []) is None     # untouched
    assert ledger["hypotheses"][sid]["registered_as_of"] == AS_OF
    assert thl.register_extend_timeout(ledger, 20, AS_OF, [], []) is None
    assert thl.register_extend_timeout(ledger, "abc", AS_OF, [], []) is None


def test_evidence_counts_only_resolved_rows_closed_up_to_the_date():
    trades = _history_trades() + [_trade(70, "LINKUSDT", "2026-10-01", "2026-10-21", 0.1),   # after up_to
                                  _trade(66, "DOGEUSDT", "2026-09-21", "2026-10-10", 0.0)]   # no row yet
    rows = [_row(58, -0.5), _row(61, 0.0, resolved=False), _row(70, 3.0)]
    ev = thl.extend_timeout_evidence(40, trades, rows, up_to=AS_OF)
    assert ev["n_timeouts"] == 3 and ev["n_resolved"] == 1
    assert ev["sum_delta_R"] == pytest.approx(-0.5 - (-0.332))


# ── forward scoring ──────────────────────────────────────────────────────────

def test_forward_scores_timeouts_after_registration_once_resolved():
    ledger = thl.new_ledger(AS_OF)
    thl.register_extend_timeout(ledger, 40, AS_OF, [], [])
    trades = [
        _trade(58, "SOLUSDT", "2026-09-19", "2026-10-09", -0.332),                 # before reg
        _trade(63, "COMPUSDT", "2026-09-23", "2026-10-13", -0.2),                  # after, resolved
        _trade(64, "ATOMUSDT", "2026-10-10", "2026-10-30", 0.1),                   # after, pending
        _trade(65, "XRPUSDT", "2026-10-11", "2026-10-15", -1.0, outcome="LOSS"),   # not a timeout
    ]
    rows = [_row(58, 1.0), _row(63, 0.8), _row(64, 0.0, resolved=False)]
    s = thl.update_forward(ledger, trades, {}, "2026-11-01", hindsight=rows)
    f = ledger["hypotheses"][SID]["forward"]
    assert s["evaluated"][SID]["new_signals"] == 1
    assert f["n_signals"] == 1 and f["samples"][0]["trade_id"] == 63
    assert f["samples"][0]["delta_R"] == pytest.approx(0.8 - (-0.2))
    assert f["trade_ids_evaluated"] == [63]
    # pending row resolves later → picked up exactly once
    thl.update_forward(ledger, trades, {}, "2026-11-02", hindsight=rows)
    assert f["n_signals"] == 1
    rows[2] = _row(64, -0.9, reason=tth.EXIT_STOP)
    thl.update_forward(ledger, trades, {}, "2026-11-20", hindsight=rows)
    assert f["n_signals"] == 2 and f["samples"][-1]["delta_R"] == pytest.approx(-1.0)
    thl.update_forward(ledger, trades, {}, "2026-11-21", hindsight=rows)
    assert f["n_signals"] == 2 and ledger["hypotheses"][SID]["status"] == "SHADOW"


def test_mirrored_exchange_rows_collapse_to_one_signal_on_the_best_row():
    ledger = thl.new_ledger(AS_OF)
    thl.register_extend_timeout(ledger, 40, AS_OF, [], [])
    trades = [_trade(70, "BTCUSDT", "2026-10-11", "2026-10-31", 0.05, exchange="binance"),
              _trade(71, "BTCUSDT", "2026-10-11", "2026-10-31", 0.02, exchange="kraken")]
    rows = [_row(70, 1.0), _row(71, 0.9)]
    thl.update_forward(ledger, trades, {}, "2026-11-25", hindsight=rows)
    f = ledger["hypotheses"][SID]["forward"]
    assert f["n_signals"] == 1 and f["n_rows"] == 2 and f["samples"][0]["trade_id"] == 70
    assert f["samples"][0]["delta_R"] == pytest.approx(0.95)


def test_wrong_horizon_rows_and_other_kinds_are_ignored():
    ledger = thl.new_ledger(AS_OF)
    thl.register_extend_timeout(ledger, 40, AS_OF, [], [])
    thl.register_from_report({"suggestions": [{"id": "block_long_in_TREND_UP", "rule": "r"}]}, AS_OF, ledger)
    t = _trade(63, "COMPUSDT", "2026-09-23", "2026-10-13", -0.2)
    thl.update_forward(ledger, [t], {}, "2026-11-01", hindsight=[_row(63, 0.8, horizon=30)])
    assert ledger["hypotheses"][SID]["forward"]["n_signals"] == 0
    assert ledger["hypotheses"]["block_long_in_TREND_UP"]["forward"]["n_signals"] == 1
    assert thl.evaluate_extend_timeout(ledger["hypotheses"][SID], t, None) is None
    assert thl.evaluate_extend_timeout(ledger["hypotheses"][SID], dict(t, outcome="WIN"), _row(63, 0.8)) is None


def test_thresholds_decide_from_forward_rows():
    ledger = thl.new_ledger(AS_OF)
    thl.register_extend_timeout(ledger, 40, AS_OF, [], [])
    trades = [_trade(100 + i, f"S{i}USDT", "2026-10-11", "2026-10-31", 0.0) for i in range(22)]
    thl.update_forward(ledger, trades, {}, "2026-12-01", hindsight=[_row(100 + i, -0.8, reason=tth.EXIT_STOP) for i in range(22)])
    assert ledger["hypotheses"][SID]["status"] == "REJECTED"
    ledger = thl.new_ledger(AS_OF)
    thl.register_extend_timeout(ledger, 40, AS_OF, [], [])
    thl.update_forward(ledger, trades, {}, "2026-12-01", hindsight=[_row(100 + i, 1.5, reason=tth.EXIT_TARGET) for i in range(22)])
    assert ledger["hypotheses"][SID]["status"] == "CONFIRMED"


# ── cycle: no network unless an extend_timeout hypothesis is active ──────────

def test_cycle_without_the_kind_never_calls_the_resolver(tmp_path, monkeypatch):
    monkeypatch.setattr(tth, "refresh", lambda *a, **k: (_ for _ in ()).throw(AssertionError("network")))
    monkeypatch.setattr(tth, "HINDSIGHT_PATH", tmp_path / "absent.jsonl")
    out = thl.run_cycle({"suggestions": []}, [], {}, AS_OF, ledger_path=tmp_path / "l.json",
                        report_dir=tmp_path / "rep", outcomes=[])
    assert thl.extend_timeout_horizons(out) == []


def test_cycle_with_the_kind_falls_back_to_the_cache_when_the_refresh_fails(tmp_path, monkeypatch, capsys):
    ledger_path, report_dir = tmp_path / "l.json", tmp_path / "rep"
    ledger = thl.new_ledger(AS_OF)
    thl.register_extend_timeout(ledger, 40, AS_OF, [], [])
    thl.save_ledger(ledger, ledger_path)
    cache = tmp_path / "h.jsonl"
    tth.save_hindsight([_row(63, 0.8)], cache)
    monkeypatch.setattr(tth, "HINDSIGHT_PATH", cache)
    monkeypatch.setattr(tth, "refresh", lambda *a, **k: (_ for _ in ()).throw(OSError("offline")))
    t = _trade(63, "COMPUSDT", "2026-09-23", "2026-10-13", -0.2)
    out = thl.run_cycle({"suggestions": []}, [t], {}, "2026-11-01", ledger_path=ledger_path,
                        report_dir=report_dir, outcomes=[])
    assert "refresh skipped" in capsys.readouterr().out
    assert out["hypotheses"][SID]["forward"]["n_signals"] == 1
    md = (report_dir / thl.MD_NAME).read_text(encoding="utf-8")
    assert SID in md and "| extend_timeout |" in md
    assert thl.forbidden_words_found(md) == []


def test_cycle_passes_the_refreshed_rows_through(tmp_path, monkeypatch):
    ledger_path = tmp_path / "l.json"
    ledger = thl.new_ledger(AS_OF)
    thl.register_extend_timeout(ledger, 40, AS_OF, [], [])
    thl.save_ledger(ledger, ledger_path)
    seen = {}

    def fake_refresh(trades, horizons, as_of, **kw):
        seen.update(horizons=horizons, as_of=as_of)
        return [_row(63, 0.8)]

    monkeypatch.setattr(tth, "refresh", fake_refresh)
    t = _trade(63, "COMPUSDT", "2026-09-23", "2026-10-13", -0.2)
    out = thl.run_cycle({"suggestions": []}, [t], {}, "2026-11-01", ledger_path=ledger_path,
                        report_dir=tmp_path / "rep", outcomes=[])
    assert seen == {"horizons": [40], "as_of": "2026-11-01"}
    assert out["hypotheses"][SID]["forward"]["n_signals"] == 1
