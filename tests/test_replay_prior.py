"""tools/replay_prior.py: in-sample priors per hypothesis kind, and the ledger column."""
import json
import sys

sys.path.insert(0, r"C:\SPARTA_BRAIN")
from tools import replay_prior as rp  # noqa: E402
from tools import trade_hypothesis_ledger as thl  # noqa: E402
from tools import replay_bot_rules as rb  # noqa: E402


def _sig(sym, strat, date, direction, R, *, allowed=True, reason="", regime="TREND_UP", days=3,
         outcome="LOSS", to40=None, features=None):
    exit_i = 10
    return dict(sym=sym, strat=strat, base=strat, i=1, date=date, direction=direction, entry=100.0, sl=95.0,
                tp1=115.0, regime=regime, allowed=allowed, reason=reason, confirm=True,
                features=features or {},
                res_base=dict(R=R, outcome=outcome, days=days, mfe=0.5, exit_i=exit_i, exit_date="2026-01-20"),
                res_to40=dict(R=(to40 if to40 is not None else R), outcome=outcome, days=days, mfe=0.5,
                              exit_i=exit_i, exit_date="2026-01-25"),
                res_f1r=None)


def _hyp(kind, params, hid="h"):
    return {"id": hid, "kind": kind, "params": params, "status": "SHADOW"}


def test_block_where_prior_is_minus_R_of_matching_trades():
    taken = [_sig("BTC", "D", "2025-01-05", "short", -1.0), _sig("ETH", "D", "2025-02-05", "short", -0.5),
             _sig("SOL", "D", "2025-03-05", "long", 2.0)]
    pr = rp.prior_for(_hyp("block_where", {"where": {"strategy": "D", "direction": "short"}}), taken, [], [])
    assert pr["n"] == 2 and abs(pr["prior_delta_R_mean"] - 0.75) < 1e-9 and pr["sum"] == 1.5


def test_feature_cell_and_hold_bucket_fields():
    s = _sig("BTC", "F", "2025-01-05", "long", 1.0, days=14, features={"body_bucket": "full"})
    assert rp.signal_field(s, "hold_bucket") == "long"
    assert rp.signal_field(s, "body_bucket") == "full"
    assert rp.signal_field(s, "regime_at_open") == "TREND_UP"
    pr = rp.prior_for(_hyp("block_where", {"where": {"body_bucket": "full"}}), [s], [], [])
    assert pr["n"] == 1 and pr["prior_delta_R_mean"] == -1.0


def test_unblock_priors_use_refused_signals_or_the_slot_leftovers():
    blocked = [_sig("BTC", "D", "2025-01-05", "long", 1.5, allowed=False, reason="regime=TREND_DOWN blocks new longs"),
               _sig("ETH", "D", "2025-01-06", "short", -1.0, allowed=False, reason="regime=TREND_UP blocks new shorts")]
    pr = rp.prior_for(_hyp("unblock", {"counted_reason": "TREND_DOWN_BLOCKS_LONG"}), [], blocked, [])
    assert pr["n"] == 1 and pr["prior_delta_R_mean"] == 1.5
    pr2 = rp.prior_for(_hyp("unblock", {"counted_reason": "SLOT_OCCUPIED"}), [], blocked,
                       [_sig("X", "D", "2025-01-07", "long", -0.2)])
    assert pr2["n"] == 1 and pr2["prior_delta_R_mean"] == -0.2
    assert rp.prior_for(_hyp("unblock", {"counted_reason": "NOPE"}), [], blocked, [])["n"] == 0


def test_extend_timeout_prior_is_paired_on_timeouts_only():
    taken = [_sig("BTC", "D", "2025-01-05", "long", 0.1, outcome="TIMEOUT", to40=0.6),
             _sig("ETH", "D", "2025-01-06", "long", -1.0, outcome="LOSS", to40=-1.0)]
    pr = rp.prior_for(_hyp("extend_timeout", {"horizon_days": 40}), taken, [], [])
    assert pr["n"] == 1 and abs(pr["prior_delta_R_mean"] - 0.5) < 1e-9
    assert rp.prior_for(_hyp("extend_timeout", {"horizon_days": 30}), taken, [], [])["n"] == 0
    assert rp.prior_for(_hyp("stop_cap", {}), taken, [], [])["n"] == 0
    assert rp.prior_for(_hyp("partial", {}), taken, [], [])["n"] == 0


def test_stability_needs_two_half_years_with_ten_trades_each():
    dates_a = ["2025-01-%02d" % (i + 1) for i in range(12)]
    dates_b = ["2025-06-%02d" % (i + 1) for i in range(12)]
    st = rp._stats([0.5] * 12 + [0.3] * 12, dates_a + dates_b)
    assert st["stable"] is True
    st = rp._stats([0.5] * 12 + [-0.3] * 12, dates_a + dates_b)
    assert st["stable"] is False
    st = rp._stats([0.5] * 12 + [-0.3] * 3, dates_a + dates_b[:3])
    assert st["stable"] is None


def test_one_slot_respects_per_symbol_lock_across_strategies_and_slot_count():
    rb.SYMBOLS[:] = rb.SYMBOLS  # unchanged; order lookup uses the real list
    syms = rb.SYMBOLS[:3]
    sigs = [_sig(syms[0], "D", "2025-01-05", "long", 1.0), _sig(syms[0], "F", "2025-01-05", "long", 1.0),
            _sig(syms[1], "F", "2025-01-05", "long", 1.0), _sig(syms[2], "D", "2025-01-05", "long", 1.0)]
    taken = rb.one_slot(sigs, "res_base", slots=1)
    assert [(s["sym"], s["strat"]) for s, r in taken] == [(syms[0], "D"), (syms[1], "F")]   # F cannot take sym0
    taken3 = rb.one_slot(sigs, "res_base", slots=3)
    assert [(s["sym"], s["strat"]) for s, r in taken3] == [(syms[0], "D"), (syms[2], "D"), (syms[1], "F")]


def test_ledger_renders_the_prior_column_from_the_json_file(tmp_path, monkeypatch):
    ledger = thl.new_ledger("2026-10-01")
    ledger["hypotheses"]["blockwhere__strategy=D__direction=short"] = {
        "id": "blockwhere__strategy=D__direction=short", "kind": "block_where", "rule": "r",
        "params": {"where": {"strategy": "D", "direction": "short"}}, "registered_as_of": "2026-10-01",
        "registered_evidence": {"n": 3}, "registered_label": "T", "status": "SHADOW",
        "thresholds": dict(thl.DEFAULT_THRESHOLDS),
        "forward": {"n_signals": 0, "n_rows": 0, "delta_R_mean": None, "delta_R_sum": 0.0,
                    "bootstrap_p_positive": None, "wins": 0, "losses": 0, "samples": [],
                    "signal_keys_evaluated": [], "trade_ids_evaluated": [], "last_eval_as_of": None},
        "history": [{"as_of": "2026-10-01", "status": "SHADOW", "note": "t"}],
    }
    monkeypatch.setattr(thl, "REPORT_DIR", tmp_path)
    md = thl.render_markdown(ledger)
    assert "| replay prior |" in md and "| - | need 20" in md
    (tmp_path / thl.REPLAY_PRIORS_NAME).write_text(json.dumps({"priors": {
        "blockwhere__strategy=D__direction=short": {"n": 256, "prior_delta_R_mean": -0.084, "p_pos": 0.001, "stable": False}}}),
        encoding="utf-8")
    md = thl.render_markdown(ledger)
    assert "Δ-0.084 n=256 p=0.001 unstable" in md
    assert thl.forbidden_words_found(md) == []
