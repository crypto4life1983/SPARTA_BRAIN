"""Derived reason SLOT_OCCUPIED (2026-10-05): the ledger scores the one-slot-per-strategy cap.

Origin: after the 42-symbol expansion the bot's one-open-position-per-(exchange,
strategy) rule hid 87 gate-allowed signals in 11 days (data/blocked_entries.jsonl,
reason "slot occupied by <SYM>"). The bot's missed-opportunity resolver already
scores those signals but leaves counted_reason empty, so no unblock hypothesis
could see them. These tests pin the read-only join, on tmp_path only.
"""
from __future__ import annotations

import json

from tools import trade_hypothesis_ledger as thl


def _blocked(run_date, symbol, strategy, direction="long", reason="slot occupied by BTCUSDT",
             exchange="binance"):
    return {"atr14": 0.5, "direction": direction, "entry": 5.0, "exchange": exchange,
            "reason": reason, "run_date": run_date, "sl": 3.5, "strategy": strategy,
            "symbol": symbol, "tp1": 6.5}


def _outcome(ts, symbol, strategy="D", direction="long", *, passed=True, reason=None,
             dar=0.06, classification="BAD_BLOCK"):
    """risk_frac = 3*2/100 = 0.06, so dar=+0.06 -> +1R."""
    return {"candidate_id": f"{ts}|{symbol}|{strategy}", "ts_utc": f"{ts}T00:00:00+00:00",
            "symbol": symbol, "strategy_id": strategy, "direction": direction,
            "counted_reason": reason, "passed_all_gates": passed, "entry_candidate": 100.0,
            "atr": 2.0, "dir_adjusted_return_20": dar, "classification": classification,
            "classification_horizon": 20}


def _write_jsonl(path, rows):
    path.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")


# ── keys: run_date - 1 day, slot rows only, exchange collapsed ───────────────

def test_slot_keys_shift_run_date_to_bar_day_and_ignore_other_reasons(tmp_path):
    p = tmp_path / "blocked_entries.jsonl"
    p.write_text(
        json.dumps(_blocked("2026-09-28", "POLUSDT", "D")) + "\n"
        + json.dumps(_blocked("2026-09-28", "POLUSDT", "D", exchange="kraken")) + "\n"
        + json.dumps(_blocked("2026-09-28", "NEARUSDT", "F2", reason="D2 quarantined")) + "\n"
        + json.dumps(_blocked("", "XLMUSDT", "D")) + "\n"
        + "not json\n\n[1]\n",
        encoding="utf-8",
    )
    keys = thl.load_slot_occupied_keys(p)
    assert keys == {("POLUSDT", "D", "long", "2026-09-27")}


def test_slot_keys_missing_file_is_empty(tmp_path):
    assert thl.load_slot_occupied_keys(tmp_path / "absent.jsonl") == set()


# ── tagging: only passed + uncounted + matching rows, inputs untouched ────────

def test_tag_slot_occupied_only_touches_matching_uncounted_rows():
    keys = {("POLUSDT", "D", "long", "2026-09-27")}
    match = _outcome("2026-09-27", "POLUSDT")
    other_day = _outcome("2026-09-28", "POLUSDT")
    already = _outcome("2026-09-27", "POLUSDT", reason="TREND_DOWN_BLOCKS_LONG", passed=False)
    gated = _outcome("2026-09-27", "POLUSDT", passed=False)
    rows = [match, other_day, already, gated]
    out = thl.tag_slot_occupied(rows, keys)
    assert [o["counted_reason"] for o in out] == [
        thl.SLOT_OCCUPIED_REASON, None, "TREND_DOWN_BLOCKS_LONG", None]
    assert out[0]["derived_reason_source"] == "data/blocked_entries.jsonl"
    assert match["counted_reason"] is None  # pure: input not mutated
    assert out[1] is other_day and out[2] is already and out[3] is gated


def test_tag_slot_occupied_with_no_keys_is_identity():
    rows = [_outcome("2026-09-27", "POLUSDT")]
    out = thl.tag_slot_occupied(rows, set())
    assert out == rows and out is not rows


# ── end to end: loader + evidence + registration + forward scoring ───────────

def test_tagged_loader_feeds_unblock_evidence_and_forward_scoring(tmp_path):
    outcomes_p, blocked_p = tmp_path / "outcomes.jsonl", tmp_path / "blocked.jsonl"
    _write_jsonl(blocked_p, [_blocked("2026-09-26", "NEARUSDT", "D"),
                             _blocked("2026-10-02", "LINKUSDT", "D")])
    _write_jsonl(outcomes_p, [
        _outcome("2026-09-25", "NEARUSDT", dar=-0.06, classification="GOOD_BLOCK"),  # frozen
        _outcome("2026-10-01", "LINKUSDT", dar=0.12, classification="BAD_BLOCK"),    # forward +2R
        _outcome("2026-10-01", "ADAUSDT", dar=0.12, classification="BAD_BLOCK"),     # no slot row
    ])
    tagged = thl.load_missed_outcomes_tagged(outcomes_p, blocked_p)
    assert [o.get("counted_reason") for o in tagged] == ["SLOT_OCCUPIED", "SLOT_OCCUPIED", None]

    ledger = thl.new_ledger("2026-09-30")
    sid = thl.register_unblock(ledger, "slot_occupied", "2026-09-30", tagged)
    assert sid == "unblock__SLOT_OCCUPIED"
    ev = ledger["hypotheses"][sid]["registered_evidence"]
    assert ev["n_resolved_blocks"] == 1 and ev["good_blocks"] == 1
    assert ev["net_hyp_R"] == -1.0

    thl.update_forward(ledger, [], {}, "2026-10-05", outcomes=tagged)
    fwd = ledger["hypotheses"][sid]["forward"]
    assert fwd["n_signals"] == 1
    assert fwd["delta_R_sum"] == 2.0


def test_kind_for_slot_occupied_id():
    assert thl.kind_for_id("unblock__SLOT_OCCUPIED") == ("unblock", {"counted_reason": "SLOT_OCCUPIED"})
