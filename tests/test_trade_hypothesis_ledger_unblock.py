"""'unblock' hypotheses (2026-09-23): the ledger learns from entries the bot did NOT take.

Origin: on 2026-09-15 BTC/ETH/SOL/LINK broke their 20-day lows, the bot's D/D2/F/F2
short signals fired, and the regime gate blocked all of them (TREND_UP blocks new
shorts). With hindsight every one would have been stopped out on 09-18. The ledger
could not score that because it only sees trades that were taken; the bot's own
blocked-entry ledger can. These tests pin the bridge, on tmp_path only.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools import trade_hypothesis_ledger as thl

AS_OF = "2026-09-23"
REASON = "TREND_UP_BLOCKS_SHORT"


def _outcome(ts, symbol, dar, *, entry=100.0, atr=2.0, classification="GOOD_BLOCK",
             reason=REASON, horizon=20, strategy="D", cid=None):
    """One resolved blocked-entry row. risk_frac = 3*atr/entry = 0.06, so
    dar=-0.06 -> -1R, dar=+0.12 -> +2R."""
    return {"candidate_id": cid or f"{ts}|{symbol}|{strategy}", "ts_utc": f"{ts}T00:00:00+00:00",
            "symbol": symbol, "strategy_id": strategy, "direction": "short",
            "counted_reason": reason, "entry_candidate": entry, "atr": atr,
            f"dir_adjusted_return_{horizon}": dar, "classification": classification,
            "classification_horizon": horizon}


# ── id -> kind, R formula, loader ────────────────────────────────────────────

def test_kind_for_unblock_id():
    assert thl.kind_for_id("unblock__TREND_UP_BLOCKS_SHORT") == ("unblock", {"counted_reason": REASON})
    assert thl.kind_for_id("unblock__trend_up_blocks_short") == ("unblock", {"counted_reason": REASON})
    assert thl.kind_for_id("unblock__") == ("unknown", {})


def test_outcome_r_mirrors_bot_formula():
    assert thl.outcome_r(_outcome("2026-09-15", "BTCUSDT", -0.06)) == pytest.approx(-1.0)
    assert thl.outcome_r(_outcome("2026-09-15", "BTCUSDT", 0.12)) == pytest.approx(2.0)
    assert thl.outcome_r({"classification_horizon": None}) is None
    assert thl.outcome_r(_outcome("2026-09-15", "X", None)) is None
    assert thl.outcome_r(_outcome("2026-09-15", "X", 0.1, entry=0.0)) is None


def test_load_missed_outcomes_tolerates_missing_and_junk(tmp_path):
    assert thl.load_missed_outcomes(tmp_path / "nope.jsonl") == []
    p = tmp_path / "o.jsonl"
    p.write_text('{"a": 1}\nnot json\n\n[1,2]\n{"b": 2}\n', encoding="utf-8")
    assert thl.load_missed_outcomes(p) == [{"a": 1}, {"b": 2}]


# ── registration freezes the hindsight record ────────────────────────────────

def _history():
    return [_outcome("2026-09-15", "BTCUSDT", -0.06),
            _outcome("2026-09-15", "LINKUSDT", -0.09),
            _outcome("2026-09-16", "AAVEUSDT", -0.03),
            _outcome("2026-09-16", "ETHUSDT", 0.06, classification="BAD_BLOCK", reason="RANGE_MID"),
            _outcome("2026-09-17", "SOLUSDT", 0.06, classification="UNRESOLVED")]


def test_register_unblock_freezes_evidence_and_is_idempotent():
    ledger = thl.new_ledger(AS_OF)
    sid = thl.register_unblock(ledger, "trend_up_blocks_short", AS_OF, _history(), note="09-15 dump")
    assert sid == "unblock__TREND_UP_BLOCKS_SHORT"
    h = ledger["hypotheses"][sid]
    assert h["status"] == "SHADOW" and h["kind"] == "unblock"
    ev = h["registered_evidence"]
    assert ev["n_resolved_blocks"] == 3 and ev["good_blocks"] == 3 and ev["bad_blocks"] == 0
    assert ev["net_hyp_R"] == pytest.approx(-3.0) and ev["mean_hyp_R"] == pytest.approx(-1.0)
    assert "09-15 dump" in h["history"][0]["note"]
    assert thl.register_unblock(ledger, REASON, "2026-09-24", _history()) is None   # untouched
    assert ledger["hypotheses"][sid]["registered_as_of"] == AS_OF
    assert thl.register_unblock(ledger, "  ", AS_OF, _history()) is None


# ── forward scoring: only resolved rows strictly after registration, once ────

def test_forward_scores_only_post_registration_resolved_rows():
    ledger = thl.new_ledger(AS_OF)
    sid = thl.register_unblock(ledger, REASON, AS_OF, _history())
    later = _history() + [
        _outcome("2026-09-23", "BTCUSDT", 0.06),                          # same day: excluded
        _outcome("2026-09-25", "BTCUSDT", 0.12, classification="BAD_BLOCK"),
        _outcome("2026-09-26", "SOLUSDT", -0.06),
        _outcome("2026-09-27", "ETHUSDT", 0.03, classification="UNRESOLVED"),  # not yet resolved
        _outcome("2026-09-28", "XRPUSDT", 0.30, reason="RANGE_MID"),          # other gate
    ]
    s = thl.update_forward(ledger, [], {}, "2026-09-29", outcomes=later)
    f = ledger["hypotheses"][sid]["forward"]
    assert s["evaluated"][sid]["new_signals"] == 2
    assert f["n_signals"] == 2 and f["n_rows"] == 2
    assert [x["delta_R"] for x in f["samples"]] == [pytest.approx(2.0), pytest.approx(-1.0)]
    assert f["samples"][0]["classification"] == "BAD_BLOCK" and f["samples"][0]["trade_id"] is None
    assert f["delta_R_sum"] == pytest.approx(1.0)
    assert ledger["hypotheses"][sid]["status"] == "SHADOW"          # n < 20

    # a re-run adds nothing; the previously unresolved row is picked up once resolved
    thl.update_forward(ledger, [], {}, "2026-09-30", outcomes=later)
    assert f["n_signals"] == 2
    later[-2]["classification"] = "GOOD_BLOCK"
    thl.update_forward(ledger, [], {}, "2026-10-01", outcomes=later)
    assert f["n_signals"] == 3 and f["samples"][-1]["symbol"] == "ETHUSDT"


def test_thresholds_reject_when_gate_keeps_being_right():
    ledger = thl.new_ledger(AS_OF)
    sid = thl.register_unblock(ledger, REASON, AS_OF, [])
    rows = [_outcome(f"2026-10-{d:02d}", f"S{d}USDT", -0.06) for d in range(1, 23)]
    thl.update_forward(ledger, [], {}, "2026-11-01", outcomes=rows)
    h = ledger["hypotheses"][sid]
    assert h["forward"]["n_signals"] == 22
    assert h["status"] == "REJECTED"                       # p_positive 0 <= 0.5
    assert h["history"][-1]["note"].startswith("SHADOW -> REJECTED")


def test_thresholds_confirm_when_blocks_keep_missing_winners():
    ledger = thl.new_ledger(AS_OF)
    sid = thl.register_unblock(ledger, REASON, AS_OF, [])
    rows = [_outcome(f"2026-10-{d:02d}", f"S{d}USDT", 0.12, classification="BAD_BLOCK") for d in range(1, 23)]
    thl.update_forward(ledger, [], {}, "2026-11-01", outcomes=rows)
    assert ledger["hypotheses"][sid]["status"] == "CONFIRMED"


# ── other kinds untouched; render and cycle carry the new kind ───────────────

def test_trade_kinds_ignore_outcomes_and_unblock_ignores_trades():
    ledger = thl.new_ledger(AS_OF)
    thl.register_from_report({"suggestions": [{"id": "block_long_in_TREND_DOWN", "rule": "r"}]}, AS_OF, ledger)
    sid = thl.register_unblock(ledger, REASON, AS_OF, [])
    trade = {"id": 1, "symbol": "BTCUSDT", "exchange": "binance", "strategy": "D", "direction": "long",
             "regime_at_open": "TREND_DOWN", "open_date": "2026-09-24", "close_date": "2026-09-26",
             "pnl_r": -1.0, "pnl_usd": -10.0, "outcome": "LOSS"}
    thl.update_forward(ledger, [trade], {}, "2026-09-29",
                       outcomes=[_outcome("2026-09-25", "BTCUSDT", -0.06)])
    assert ledger["hypotheses"]["block_long_in_TREND_DOWN"]["forward"]["n_signals"] == 1
    assert ledger["hypotheses"][sid]["forward"]["n_signals"] == 1
    assert ledger["hypotheses"][sid]["forward"]["trade_ids_evaluated"] == []


def test_render_and_cycle_include_unblock(tmp_path, monkeypatch):
    ledger_path, report_dir = tmp_path / "ledger.json", tmp_path / "rep"
    ledger = thl.new_ledger(AS_OF)
    thl.register_unblock(ledger, REASON, AS_OF, _history())
    thl.save_ledger(ledger, ledger_path)
    out = thl.run_cycle({"suggestions": []}, [], {}, "2026-09-29", ledger_path=ledger_path,
                        report_dir=report_dir, outcomes=[_outcome("2026-09-25", "BTCUSDT", -0.06)])
    assert out["hypotheses"]["unblock__TREND_UP_BLOCKS_SHORT"]["forward"]["n_signals"] == 1
    md = (report_dir / thl.MD_NAME).read_text(encoding="utf-8")
    assert "unblock__TREND_UP_BLOCKS_SHORT" in md and "| unblock |" in md
    assert thl.forbidden_words_found(md) == []
    # outcomes=None must fall back to the loader, never crash when the file is absent
    monkeypatch.setattr(thl, "missed_outcomes_path", lambda ext_root=None: tmp_path / "absent.jsonl")
    out2 = thl.run_cycle({"suggestions": []}, [], {}, "2026-09-30", ledger_path=ledger_path, report_dir=report_dir)
    assert out2["hypotheses"]["unblock__TREND_UP_BLOCKS_SHORT"]["forward"]["n_signals"] == 1
