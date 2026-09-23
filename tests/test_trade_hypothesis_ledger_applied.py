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


def _t(i, close_date, pnl_r, symbol=None, exchange="binance", direction="long", regime="TREND_UP",
       open_date="2026-09-01"):
    """open_date defaults to a PRE-partial-bar-fix date (see thl.EVIDENCE_VALID_FROM);
    pass an on/after date to build a baseline that is admissible as evidence."""
    return {"id": i, "exchange": exchange, "symbol": symbol or f"S{i}", "strategy": "D", "direction": direction,
            "regime_at_open": regime, "open_date": open_date, "close_date": close_date,
            "pnl_r": pnl_r, "pnl_usd": pnl_r * 20}


POST_FIX = "2026-09-16"   # on/after thl.EVIDENCE_VALID_FROM


def _ledger_with_one():
    ledger = thl.new_ledger("2026-09-11")
    thl.register_from_report({"suggestions": [{"id": "block_long_in_TREND_DOWN", "rule": "x",
                                                "evidence": {"n": 4}, "label": "OK", "sample_ok": True}]},
                             "2026-09-11", ledger)
    return ledger


def test_mark_applied_freezes_baseline_and_switches_status():
    """A baseline needs APPLIED_MIN_N admissible (post-fix) closes to be usable."""
    ledger = _ledger_with_one()
    before = [_t(i, "2026-09-20", 1.0 if i % 2 else -1.0, open_date=POST_FIX)
              for i in range(1, thl.APPLIED_MIN_N + 1)]
    hyp = thl.mark_applied(ledger, "block_long_in_TREND_DOWN", "2026-09-30", before, note="bot c9a8f7b")
    assert hyp["status"] == "APPLIED"
    assert hyp["applied"]["baseline_n"] == thl.APPLIED_MIN_N
    assert hyp["applied"]["baseline_mean_R"] is not None
    assert hyp["applied"]["baseline_status"] == thl.BASELINE_EMPIRICAL
    assert hyp["history"][-1]["status"] == "APPLIED" and "c9a8f7b" in hyp["history"][-1]["note"]


def test_mark_applied_refuses_a_baseline_built_from_retired_trades():
    """THE POINT OF THE CHANGE. Pre-partial-bar-fix trades are retired evidence;
    they must never become the number an applied rule is judged against."""
    ledger = _ledger_with_one()
    before = [_t(1, "2026-09-05", 1.0), _t(2, "2026-09-10", -1.0), _t(3, "2026-09-11", 0.5)]
    hyp = thl.mark_applied(ledger, "block_long_in_TREND_DOWN", "2026-09-11", before)
    ap = hyp["applied"]
    assert ap["baseline_n"] == 0, "pre-fix closes must not enter the baseline at all"
    assert ap["baseline_mean_R"] is None
    assert ap["baseline_status"] == thl.BASELINE_INSUFFICIENT
    assert str(thl.ROLLBACK_ABS_MEAN_R) in ap["rollback_rule"]


def test_mark_applied_with_too_few_post_fix_closes_has_no_baseline():
    ledger = _ledger_with_one()
    before = [_t(i, "2026-09-20", 1.0, open_date=POST_FIX) for i in range(1, 4)]
    ap = thl.mark_applied(ledger, "block_long_in_TREND_DOWN", "2026-09-30", before)["applied"]
    assert ap["baseline_n"] == 3           # counted, but not enough to use
    assert ap["baseline_mean_R"] is None
    assert ap["baseline_status"] == thl.BASELINE_INSUFFICIENT


def test_update_forward_tracks_post_apply_expectancy_and_flags_regression():
    ledger = _ledger_with_one()
    # baseline mean +1.0 from APPLIED_MIN_N admissible (post-fix) closes
    base = [_t(i, "2026-09-16", 1.0, open_date=POST_FIX) for i in range(1, thl.APPLIED_MIN_N + 1)]
    thl.mark_applied(ledger, "block_long_in_TREND_DOWN", "2026-09-17", base)
    # after apply: 25 signals averaging +0.2R -> regression flag (below 1.0 - 0.2)
    after = [_t(100 + i, "2026-09-20", 0.2, open_date=POST_FIX) for i in range(25)]
    # mirrored exchange rows must count once
    after.append(_t(999, "2026-09-21", 0.2, symbol="S100", exchange="kraken", open_date=POST_FIX))
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


# ── absolute rollback rule when no admissible baseline exists ───────────────

def _applied_without_baseline(ledger):
    """Apply with only retired trades available -> baseline_mean_R is None."""
    retired = [_t(i, "2026-09-05", 1.0) for i in range(1, 6)]
    thl.mark_applied(ledger, "block_long_in_TREND_DOWN", "2026-09-11", retired)
    return retired


def test_absolute_rule_flags_rollback_when_post_fix_mean_is_negative():
    ledger = _ledger_with_one()
    retired = _applied_without_baseline(ledger)
    after = [_t(100 + i, "2026-09-20", -0.5, open_date=POST_FIX)
             for i in range(thl.APPLIED_MIN_N)]
    thl.update_forward(ledger, retired + after, {}, "2026-09-30")
    ap = ledger["hypotheses"]["block_long_in_TREND_DOWN"]["applied"]
    assert ap["baseline_mean_R"] is None
    assert ap["n_after"] == thl.APPLIED_MIN_N
    assert ap["regression_flag"] is True
    # no baseline means no "p vs baseline" - inventing one is the failure avoided
    assert ap["p_after_ge_baseline"] is None


def test_absolute_rule_does_not_flag_a_positive_mean():
    ledger = _ledger_with_one()
    retired = _applied_without_baseline(ledger)
    after = [_t(100 + i, "2026-09-20", 0.5, open_date=POST_FIX)
             for i in range(thl.APPLIED_MIN_N)]
    thl.update_forward(ledger, retired + after, {}, "2026-09-30")
    ap = ledger["hypotheses"]["block_long_in_TREND_DOWN"]["applied"]
    assert ap["regression_flag"] is False
    # ... and a positive mean must NOT be read as the rule being confirmed
    assert ledger["hypotheses"]["block_long_in_TREND_DOWN"]["status"] == "APPLIED"


def test_absolute_rule_never_flags_below_the_minimum_sample():
    ledger = _ledger_with_one()
    retired = _applied_without_baseline(ledger)
    after = [_t(100 + i, "2026-09-20", -5.0, open_date=POST_FIX)
             for i in range(thl.APPLIED_MIN_N - 1)]
    thl.update_forward(ledger, retired + after, {}, "2026-09-30")
    ap = ledger["hypotheses"]["block_long_in_TREND_DOWN"]["applied"]
    assert ap["n_after"] == thl.APPLIED_MIN_N - 1
    assert ap["regression_flag"] is False, "must not judge below the pre-registered n"


# ── legacy records: annotate, never silently rewrite ───────────────────────

def test_legacy_pre_fix_baseline_is_annotated_as_retired():
    """The four rules applied 2026-09-11 carry a numeric baseline frozen from
    retired trades. Until the separately-approved re-dating happens, the ledger
    must SAY so rather than print it as if it were admissible."""
    ap = {"applied_as_of": "2026-09-11", "baseline_mean_R": 0.2508, "baseline_n": 31}
    assert thl._baseline_status(ap) == thl.BASELINE_RETIRED


def test_post_fix_apply_with_a_number_is_empirical():
    ap = {"applied_as_of": "2026-09-20", "baseline_mean_R": 0.4, "baseline_n": 25}
    assert thl._baseline_status(ap) == thl.BASELINE_EMPIRICAL


def test_update_forward_stamps_the_retired_flag_on_legacy_records():
    ledger = _ledger_with_one()
    hyp = ledger["hypotheses"]["block_long_in_TREND_DOWN"]
    hyp["status"] = "APPLIED"
    hyp["applied"] = {           # exactly the shape on disk today
        "applied_as_of": "2026-09-11", "note": "", "baseline_n": 31,
        "baseline_mean_R": 0.2508, "n_after": 0, "mean_R_after": None,
        "p_after_ge_baseline": None, "regression_flag": False, "last_eval_as_of": None,
    }
    after = [_t(100 + i, "2026-09-19", -1.0, open_date=POST_FIX) for i in range(2)]
    thl.update_forward(ledger, after, {}, "2026-09-21")
    ap = hyp["applied"]
    assert ap["baseline_status"] == thl.BASELINE_RETIRED
    assert ap["baseline_is_retired_evidence"] is True
    # the pre-registered values themselves are untouched - re-dating is step 4
    assert ap["applied_as_of"] == "2026-09-11"
    assert ap["baseline_mean_R"] == 0.2508


def test_rendered_ledger_warns_about_a_retired_baseline():
    ledger = _ledger_with_one()
    hyp = ledger["hypotheses"]["block_long_in_TREND_DOWN"]
    hyp["status"] = "APPLIED"
    hyp["applied"] = {"applied_as_of": "2026-09-11", "baseline_mean_R": 0.2508,
                      "baseline_n": 31, "n_after": 2, "mean_R_after": -1.017,
                      "p_after_ge_baseline": None, "regression_flag": False}
    md = thl.render_markdown(ledger)
    assert "RETIRED" in md
    assert thl.forbidden_words_found(md) == []
