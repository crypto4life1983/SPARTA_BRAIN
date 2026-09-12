"""Phase 4: APPLIED tracking — once the operator applies a rule in the paper bot, the ledger
stops counterfactual scoring for it and tracks realized journal expectancy after the apply
date against the baseline frozen at apply time."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import trade_hypothesis_ledger as thl  # noqa: E402


def _t(i, close_date, pnl_r, symbol=None, exchange="binance", direction="long", regime="TREND_UP"):
    return {"id": i, "exchange": exchange, "symbol": symbol or f"S{i}", "strategy": "D", "direction": direction,
            "regime_at_open": regime, "open_date": "2026-09-01", "close_date": close_date,
            "pnl_r": pnl_r, "pnl_usd": pnl_r * 20}


def _ledger_with_one():
    ledger = thl.new_ledger("2026-09-11")
    thl.register_from_report({"suggestions": [{"id": "block_long_in_TREND_DOWN", "rule": "x",
                                                "evidence": {"n": 4}, "label": "OK", "sample_ok": True}]},
                             "2026-09-11", ledger)
    return ledger


def test_mark_applied_freezes_baseline_and_switches_status():
    ledger = _ledger_with_one()
    before = [_t(1, "2026-09-05", 1.0), _t(2, "2026-09-10", -1.0), _t(3, "2026-09-11", 0.5)]
    hyp = thl.mark_applied(ledger, "block_long_in_TREND_DOWN", "2026-09-11", before, note="bot c9a8f7b")
    assert hyp["status"] == "APPLIED"
    assert hyp["applied"]["baseline_n"] == 3
    assert abs(hyp["applied"]["baseline_mean_R"] - (0.5 / 3)) < 1e-3  # stored rounded to 4 dp
    assert hyp["history"][-1]["status"] == "APPLIED" and "c9a8f7b" in hyp["history"][-1]["note"]


def test_update_forward_tracks_post_apply_expectancy_and_flags_regression():
    ledger = _ledger_with_one()
    base = [_t(i, "2026-09-05", 1.0) for i in range(1, 11)]  # baseline mean +1.0
    thl.mark_applied(ledger, "block_long_in_TREND_DOWN", "2026-09-11", base)
    # after apply: 25 signals averaging +0.2R -> regression flag (below 1.0 - 0.2)
    after = [_t(100 + i, "2026-09-20", 0.2) for i in range(25)]
    # mirrored exchange rows must count once
    after.append(_t(999, "2026-09-21", 0.2, symbol="S100", exchange="kraken"))
    summ = thl.update_forward(ledger, base + after, {}, "2026-09-30")
    ap = ledger["hypotheses"]["block_long_in_TREND_DOWN"]["applied"]
    assert ap["n_after"] == 25
    assert abs(ap["mean_R_after"] - 0.2) < 1e-9
    assert ap["regression_flag"] is True
    assert ap["p_after_ge_baseline"] is not None and ap["p_after_ge_baseline"] < 0.05
    assert summ["evaluated"]["block_long_in_TREND_DOWN"]["applied"] is True
    # the counterfactual forward block is untouched for an APPLIED rule
    assert ledger["hypotheses"]["block_long_in_TREND_DOWN"]["forward"]["n_signals"] == 0


def test_applied_without_regression_is_not_flagged():
    ledger = _ledger_with_one()
    base = [_t(i, "2026-09-05", 0.5) for i in range(1, 6)]
    thl.mark_applied(ledger, "block_long_in_TREND_DOWN", "2026-09-11", base)
    after = [_t(100 + i, "2026-09-20", 0.6) for i in range(25)]
    thl.update_forward(ledger, base + after, {}, "2026-09-30")
    ap = ledger["hypotheses"]["block_long_in_TREND_DOWN"]["applied"]
    assert ap["regression_flag"] is False and ap["n_after"] == 25


def test_markdown_renders_applied_status():
    ledger = _ledger_with_one()
    thl.mark_applied(ledger, "block_long_in_TREND_DOWN", "2026-09-11", [_t(1, "2026-09-05", 1.0)])
    md = thl.render_markdown(ledger)
    assert "APPLIED" in md
    assert thl.forbidden_words_found(md) == []
