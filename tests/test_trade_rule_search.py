from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import trade_hypothesis_ledger as thl  # noqa: E402
from tools import trade_rule_search as rs  # noqa: E402


def _t(i, strategy="D", direction="long", regime="TREND_UP", exchange="binance", open_date="2026-06-01",
       close_date="2026-06-10", pnl_r=1.0, symbol=None):
    return {
        "id": i, "exchange": exchange, "symbol": symbol or f"S{i}USDT", "strategy": strategy,
        "direction": direction, "regime_at_open": regime, "open_date": open_date,
        "close_date": close_date, "pnl_r": pnl_r, "pnl_usd": pnl_r * 20, "outcome": "X",
    }


def _dataset():
    """40 signals: 30 benign (mean ~ +0.5) and one poisoned cell (G long) with 10 signals at −1.5."""
    rows = []
    for i in range(30):
        rows.append(_t(i, strategy="D" if i % 2 else "E", direction="long" if i % 3 else "short",
                       regime="TREND_UP", pnl_r=0.5 + (i % 5) * 0.1, open_date=f"2026-06-{(i % 28) + 1:02d}"))
    for i in range(30, 40):
        rows.append(_t(i, strategy="G", direction="long", regime="TREND_DOWN", pnl_r=-1.5,
                       open_date=f"2026-07-{(i % 28) + 1:02d}"))
    return rows


def test_dedup_keeps_best_row_per_signal():
    a = _t(1, pnl_r=-1.0, symbol="XRPUSDT", exchange="binance")
    b = _t(2, pnl_r=0.4, symbol="XRPUSDT", exchange="kraken")
    sig = rs.dedup_signals([a, b])
    assert len(sig) == 1 and sig[0]["id"] == 2


def test_scan_finds_poisoned_cell_and_deflates():
    rows = rs.scan_cells(rs.dedup_signals(_dataset()))
    by_id = {r["id"]: r for r in rows}
    g = by_id["blockwhere__strategy=G__direction=long"]
    assert g["n_signals"] == 10 and g["mean_R"] == -1.5
    assert g["candidate"] is True
    assert g["p_adj"] >= g["p_raw"]  # Bonferroni never makes it smaller
    assert g["cells_tested"] >= 5
    # a benign cell must not be a candidate
    assert all(not r["candidate"] for r in rows if r["mean_R"] > 0)


def test_no_candidate_when_nothing_is_negative():
    benign = [_t(i, pnl_r=0.3 + (i % 3) * 0.1, open_date=f"2026-06-{(i % 28) + 1:02d}") for i in range(30)]
    rows = rs.scan_cells(rs.dedup_signals(benign))
    assert rows and not any(r["candidate"] for r in rows)


def test_weekly_budget_and_no_duplicates(tmp_path: Path):
    ledger_path = tmp_path / "ledger.json"
    rep_dir = tmp_path / "rep"
    rep1 = rs.run_cycle(_dataset(), "2026-09-11", ledger_path=ledger_path, report_dir=rep_dir)
    assert 1 <= len(rep1["registered"]) <= rs.MAX_NEW_PER_WEEK
    ledger = thl.load_ledger(ledger_path)
    first = set(rep1["registered"])
    assert first <= set(ledger["hypotheses"].keys())
    for hid in first:
        assert ledger["hypotheses"][hid]["kind"] == "block_where"
        assert ledger["hypotheses"][hid]["status"] == "SHADOW"
    # same week again: already-registered ids are skipped; budget shared across the week
    rep2 = rs.run_cycle(_dataset(), "2026-09-12", ledger_path=ledger_path, report_dir=rep_dir)
    assert not (set(rep2["registered"]) & first)
    total_week = rs.registrations_this_week(thl.load_ledger(ledger_path), "2026-09-12")
    assert total_week <= rs.MAX_NEW_PER_WEEK
    assert (rep_dir / rs.JSON_NAME).exists() and (rep_dir / rs.MD_NAME).exists()
    assert len((rep_dir / rs.HISTORY_NAME).read_text().splitlines()) == 2


def test_ledger_scores_block_where_forward_only():
    hyp = {"id": "blockwhere__strategy=G__direction=long", "kind": "block_where",
           "params": {"where": {"strategy": "G", "direction": "long"}}}
    assert thl.evaluate_hypothesis(hyp, _t(1, strategy="G", direction="long", pnl_r=-0.8)) == 0.8
    assert thl.evaluate_hypothesis(hyp, _t(2, strategy="G", direction="short", pnl_r=-0.8)) is None
    assert thl.evaluate_hypothesis(hyp, _t(3, strategy="D", direction="long", pnl_r=-0.8)) is None
    wd = {"id": "x", "kind": "block_where", "params": {"where": {"weekday": "Fri", "hold_bucket": "short"}}}
    fri = _t(4, open_date="2026-09-11", close_date="2026-09-14", pnl_r=-1.0)  # 2026-09-11 is a Friday
    assert thl.evaluate_hypothesis(wd, fri) == 1.0


def test_kind_for_id_parses_blockwhere():
    kind, params = thl.kind_for_id("blockwhere__regime_at_open=RANGE__direction=long")
    assert kind == "block_where" and params["where"] == {"regime_at_open": "RANGE", "direction": "long"}
    assert thl.kind_for_id("blockwhere__")[0] == "unknown"


def test_markdown_clean_and_deterministic(tmp_path: Path):
    ledger = thl.new_ledger("2026-09-11")
    sig = rs.dedup_signals(_dataset())
    a = rs.build_report(sig, ledger, "2026-09-11")
    b = rs.build_report(sig, ledger, "2026-09-11")
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
    md = rs.render_markdown(a)
    assert "OBSERVATION ONLY" in md
    assert rs.forbidden_words_found(md) == []
