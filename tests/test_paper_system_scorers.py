"""Tests for tools/paper_system_scorers.py (pure scorers + file plumbing on tmp_path).

Never touches the real obsidian-trade-logger or the real reports/trade_learning dir:
every test feeds synthetic inputs, and score_all is pointed at tmp_path roots.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools import paper_system_scorers as pss

AS_OF = "2026-09-11"


# ── synthetic inputs ─────────────────────────────────────────────────────────

def fc_latest(*, days=121, equity=10049.78, max_dd=-0.0017, stale=0.0, alerts=None):
    return {
        "strategy_label": "always_on_monthly",
        "report_date_utc": "2026-09-11T00:00:00+00:00",
        "tracker_state": {"launch_date_utc": "2026-05-13T00:00:00+00:00", "days_since_launch": days,
                          "paper_equity": equity, "initial_capital": 10000.0},
        "since_inception": {"final_equity_usd": equity, "funding_pnl_total_usd": 97.96,
                            "basis_pnl_total_usd": 0.18, "total_simulated_costs_usd": 48.36,
                            "cost_consumption_pct": 0.3577, "max_drawdown_pct": max_dd,
                            "n_position_changes": 5},
        "alerts_active": alerts or [],
        "data_freshness": {"last_data_ts_utc": "2026-09-11T00:00:00+00:00", "stale_hours": stale},
    }


def fut_latest(*, days=80, trades=52, n_long=19, n_short=33, pnl=-2172.5, max_dd=-0.069,
               worst_day=-0.0095, n_crit=0, stale=28.1, status="ON-TRACK", alerts=None,
               launch="2026-05-13T00:00:00+00:00"):
    return {
        "status": status, "strategy_label": "MNQ_risk_$500",
        "report_date_utc": "2026-09-10T00:00:00+00:00",
        "tracker_state": {"launch_date_utc": launch, "trading_days_since_launch": days,
                          "paper_equity_usd": 50000 + pnl, "initial_capital_usd": 50000.0,
                          "instrument": "MNQ", "current_spec_hash": "a", "launch_spec_hash": "a"},
        "since_inception": {"n_trades_fired": trades, "n_long": n_long, "n_short": n_short,
                            "net_pnl_usd": pnl, "max_drawdown_pct": max_dd, "total_costs_usd": 167.5},
        "alerts_active": alerts or [],
        "graduation_progress": {"trading_days_complete": days, "trading_days_required": 60,
                                "trades_complete": trades, "trades_required": 40,
                                "n_long": n_long, "n_short": n_short, "long_short_min_each_required": 10,
                                "realized_pnl_usd": pnl, "realized_pnl_positive": str(pnl > 0),
                                "max_drawdown_pct": max_dd, "max_drawdown_within_15pct": max_dd > -0.15,
                                "worst_day_pct": worst_day, "worst_day_within_5pct": worst_day > -0.05,
                                "active_critical_alerts": n_crit},
        "data_freshness": {"last_data_ts_utc": "2026-09-08T19:55:00+00:00", "stale_hours": stale},
    }


def fs_rows(forward_n=0, forward_r=1.0, backfill_n=3):
    rows = [{"symbol": "BTCUSDT", "entry_time": "2020-02-26", "exit_time": "2020-02-27",
             "net_r": "-1.025", "engine": "v2_bb_snapback"} for _ in range(backfill_n)]
    rows += [{"symbol": "ETHUSDT", "entry_time": f"2026-09-{12 + i:02d}", "exit_time": "2026-09-30",
              "net_r": str(forward_r), "engine": "baseline_breakout"} for i in range(forward_n)]
    rows.append({"symbol": "XRPUSDT", "entry_time": "2026-09-13", "exit_time": "2026-09-14",
                 "net_r": "0.0", "engine": "skipped_by_d4"})
    return rows


def fs_state(status="OK", load_errors=None):
    return {"status": status, "generated_at": "2026-09-11T11:30:16+00:00", "appended_rows": 0,
            "candidate_rows": 257, "load_errors": load_errors or {},
            "frozen_parameters": {"FROZEN_STACK_LABEL": "Donchian-ATR-3.0x + V2 + D4"}}


S21_T = {"drawdown_kill": 0.30, "annualized_cost_drag_max": 0.05,
         "gate_12wk_min_closed_trades": 15, "gate_24wk_min_closed_trades": 35}


def s21_state(*, closed=20, first_idx=0, last_idx=60, equity=101000.0, halted=False,
              cost_drag=0.01, max_dd=0.05):
    return {"state_version": 2, "closed_trades_total": closed, "first_asof_index": first_idx,
            "last_asof_index": last_idx, "last_equity_after": equity, "halted": halted,
            "cycles_completed": 13, "first_asof_date": "2026-06-05",
            "equity_path": [{"annualized_cost_drag": cost_drag}], "drawdown": {"max_dd": max_dd}}


def s21_inputs(state, gate_eval=None):
    return {"state": state, "gate_eval": gate_eval, "thresholds": S21_T, "rebalance_days": 5,
            "start_cash": 100000.0, "manifest_status": {"paper_state": "HARNESS_BUILT_NOT_YET_RUN"},
            "state_path": "x/runs/cycles_v2/harness_state.json", "source_files": []}


ALL_SCORERS = {
    "fc": lambda: pss.score_funding_carry({"latest": fc_latest(), "alerts_rows": [], "phase8_report_present": True, "source_files": ["a"]}, AS_OF),
    "nq": lambda: pss.score_nq_orb({"latest": fut_latest(), "source_files": ["b"]}, AS_OF),
    "gc": lambda: pss.score_gc_ict({"latest": fut_latest(days=63, trades=1, n_long=1, n_short=0, pnl=-450.77, max_dd=0.0, stale=24.0, launch="2026-06-14"), "source_files": ["c"]}, AS_OF),
    "fs": lambda: pss.score_frozen_stack({"state": fs_state(), "trades_rows": fs_rows(), "validation": {"headline": {"d4_agreement_pct": 100.0, "global_verdict": "DRIFT_WARNING"}}, "forward_split": "2026-09-11", "source_files": ["d"]}, AS_OF),
    "s21": lambda: pss.score_s21(s21_inputs(None), AS_OF),
}


# ── schema / determinism / forbidden words ───────────────────────────────────

@pytest.mark.parametrize("key", sorted(ALL_SCORERS))
def test_schema_complete(key):
    rec = ALL_SCORERS[key]()
    assert tuple(rec.keys()) == pss.RECORD_KEYS
    assert rec["status"] in pss.STATUSES
    assert rec["sign"] in ("POSITIVE", "NEGATIVE", "FLAT", "NONE")
    assert set(rec["window"]) == {"kind", "end_or_min_n", "satisfied"}
    assert isinstance(rec["window"]["satisfied"], bool)
    assert rec["criteria_file"]
    assert rec["as_of"] == AS_OF
    for g in rec["own_gates"]:
        assert {"name", "threshold", "value", "status", "hard"} <= set(g)
        assert g["status"] in ("PASS", "FAIL", "PENDING", "NOT_EVALUABLE", "MANUAL")
    json.dumps(rec, sort_keys=True)  # serialisable


@pytest.mark.parametrize("key", sorted(ALL_SCORERS))
def test_deterministic(key):
    a = json.dumps(ALL_SCORERS[key](), sort_keys=True)
    b = json.dumps(ALL_SCORERS[key](), sort_keys=True)
    assert a == b


def test_forbidden_words_absent_everywhere():
    recs = [f() for f in ALL_SCORERS.values()]
    # add resolved records so closure text is exercised too
    recs.append(pss.score_nq_orb({"latest": fut_latest(pnl=1500.0), "source_files": []}, AS_OF))
    md = pss.render_markdown(recs, AS_OF)
    assert pss.BANNER in md
    assert pss.forbidden_words_found(md) == []
    for r in recs:
        assert pss.forbidden_words_found(json.dumps(r)) == []
        assert pss.forbidden_words_found(pss.render_closure_recommendation(r)) == []


def test_forbidden_word_detector_boundaries():
    assert pss.forbidden_words_found("this is validated and approved, deployable, deploy") == ["approved", "deploy", "deployable", "validated"]
    assert pss.forbidden_words_found("already readiness approval") == []
    assert pss.forbidden_words_found("a profitable strategy") == ["profitable strategy"]


# ── decide() branches ────────────────────────────────────────────────────────

def _g(name, status, hard=True):
    return pss.gate(name, ">0", 1.0, status, hard)


def test_decide_branches():
    assert pss.decide(True, "POSITIVE", [_g("a", "PASS")])[0] == "CONFIRMED"
    assert pss.decide(True, "POSITIVE", [_g("a", "PASS"), _g("m", "MANUAL")])[0] == "CONFIRMED"
    assert pss.decide(True, "NEGATIVE", [_g("a", "PASS")])[0] == "REJECTED"
    assert pss.decide(True, "POSITIVE", [_g("a", "FAIL")])[0] == "REJECTED"
    assert pss.decide(True, "POSITIVE", [_g("a", "FAIL", hard=False)])[0] == "SHADOW"
    assert pss.decide(True, "POSITIVE", [_g("a", "NOT_EVALUABLE")])[0] == "SHADOW"
    assert pss.decide(True, "FLAT", [_g("a", "PASS")])[0] == "SHADOW"
    assert pss.decide(False, "POSITIVE", [_g("a", "PASS")])[0] == "SHADOW"
    assert pss.decide(True, "POSITIVE", [_g("a", "PASS")], blocked_reason="PAUSE")[0] == "BLOCKED"
    assert pss.decide(True, "POSITIVE", [_g("a", "PASS")], blocked_reason="x", no_data_reason="y")[0] == "NO_DATA"


# ── funding carry ────────────────────────────────────────────────────────────

def test_fc_is_shadow_while_no_same_period_estimate_has_been_sealed():
    """Without a sealed same-period Phase-6B estimate the hard gate cannot be evaluated, so the
    line stays in SHADOW rather than being scored on a quantity the plan does not ask for."""
    rec = ALL_SCORERS["fc"]()
    assert rec["window"]["satisfied"] and rec["sign"] == "POSITIVE"
    assert rec["status"] == "SHADOW"
    st = {g["name"]: g["status"] for g in rec["own_gates"]}
    assert st["g1_90d_without_non_outage_critical"] == "PASS"
    assert st["g2_realized_cagr_within_30pct_of_phase6b_same_period"] == "NOT_EVALUABLE"
    assert st["g3_max_dd_vs_phase6b_worst_oos"] == "PASS"
    assert st["g4_phase8_basis_aware_completed_and_reviewed"] == "MANUAL"
    assert "g2_" in rec["reason"]
    assert rec["days_elapsed"] == 121


@pytest.mark.parametrize("band,expected_gate,expected_status", [
    ({"low": 0.0100, "high": 0.0300}, "PASS", "CONFIRMED"),   # realized inside the band
    ({"low": 0.0161, "high": 0.0299}, "FAIL", "REJECTED"),    # realized just below it
])
def test_fc_scores_g2_once_a_same_period_estimate_is_supplied(band, expected_gate, expected_status):
    """With the estimate present the gate evaluates, and the scorer's pre-registered rule
    (window satisfied + hard gate FAIL -> REJECTED) fires without any further intervention."""
    est = {"simulator_same_period_cagr": 0.02296, "accept_band": band, "_path": "g2_x.json",
           "_sha256": "a" * 64, "window": {"start": "2026-05-13", "end": "2026-09-12", "days": 122}}
    rec = pss.score_funding_carry({"latest": fc_latest(), "alerts_rows": [], "phase8_report_present": True,
                                   "g2_same_period_estimate": est, "source_files": ["a"]}, AS_OF)
    st = {g["name"]: g["status"] for g in rec["own_gates"]}
    assert st["g2_realized_cagr_within_30pct_of_phase6b_same_period"] == expected_gate
    assert rec["status"] == expected_status


def test_fc_g2_estimate_reader_ignores_a_tampered_artifact(tmp_path):
    """A sealed estimate whose sha256 sidecar does not match is ignored, never scored."""
    d = tmp_path / "reports" / "paper_funding_carry"
    d.mkdir(parents=True)
    p = d / "g2_same_period_estimate_20260912T000000Z.json"
    p.write_bytes(b'{"simulator_same_period_cagr": 0.02, "accept_band": {"low": 0.01, "high": 0.03}}')
    p.with_suffix(".json.sha256").write_text("0" * 64 + "\n", encoding="utf-8")
    assert pss._latest_g2_estimate(tmp_path) is None


def test_fc_g2_estimate_reader_is_scoped_to_the_given_root(tmp_path):
    """The reader must never reach outside the root it is given (synthetic-tree isolation)."""
    assert pss._latest_g2_estimate(tmp_path) is None


def test_fc_g2_estimate_reader_ignores_a_tampered_artifact(tmp_path, monkeypatch):
    """A sealed estimate whose sha256 sidecar does not match is ignored, never scored."""
    d = tmp_path / "reports" / "paper_funding_carry"
    d.mkdir(parents=True)
    p = d / "g2_same_period_estimate_20260912T000000Z.json"
    p.write_bytes(b'{"simulator_same_period_cagr": 0.02, "accept_band": {"low": 0.01, "high": 0.03}}')
    p.with_suffix(".json.sha256").write_text("0" * 64 + "\n", encoding="utf-8")
    monkeypatch.setattr(pss, "external_root", lambda: tmp_path)
    assert pss._latest_g2_estimate() is None


def test_fc_window_open_is_shadow():
    rec = pss.score_funding_carry({"latest": fc_latest(days=40), "alerts_rows": [], "source_files": []}, AS_OF)
    assert rec["status"] == "SHADOW" and not rec["window"]["satisfied"]


def test_fc_rejected_on_negative_sign_or_dd_fail():
    neg = pss.score_funding_carry({"latest": fc_latest(equity=9950.0), "alerts_rows": [], "source_files": []}, AS_OF)
    assert neg["status"] == "REJECTED" and neg["sign"] == "NEGATIVE"
    dd = pss.score_funding_carry({"latest": fc_latest(max_dd=-0.12), "alerts_rows": [], "source_files": []}, AS_OF)
    assert dd["status"] == "REJECTED"
    assert any(g["name"].startswith("g3_") and g["status"] == "FAIL" for g in dd["own_gates"])


def test_fc_non_outage_critical_from_alert_rows_fails_gate1():
    rows = [{"report_date_utc": "2026-06-01T00:00:00+00:00", "severity": "CRITICAL", "code": "DATA_STALE_CRITICAL", "message": ""},
            {"report_date_utc": "2026-05-01T00:00:00+00:00", "severity": "CRITICAL", "code": "DRAWDOWN_CRITICAL", "message": "pre-launch"},
            {"report_date_utc": "2026-07-01T00:00:00+00:00", "severity": "CRITICAL", "code": "FUNDING_8H_CRITICAL", "message": ""}]
    rec = pss.score_funding_carry({"latest": fc_latest(), "alerts_rows": rows, "source_files": []}, AS_OF)
    g1 = next(g for g in rec["own_gates"] if g["name"].startswith("g1_"))
    assert g1["value"] == 1.0 and g1["status"] == "FAIL"
    assert rec["status"] == "REJECTED"


def test_fc_blocked_on_pause_or_stale():
    pause = pss.score_funding_carry({"latest": fc_latest(alerts=[{"severity": "CRITICAL", "code": "DRAWDOWN_CRITICAL"}]), "source_files": []}, AS_OF)
    assert pause["status"] == "BLOCKED" and "PAUSE" in pause["reason"]
    stale = pss.score_funding_carry({"latest": fc_latest(stale=60.0), "source_files": []}, AS_OF)
    assert stale["status"] == "BLOCKED" and "stale" in stale["reason"]


def test_fc_no_data():
    rec = pss.score_funding_carry({"latest": None, "source_files": []}, AS_OF)
    assert rec["status"] == "NO_DATA" and rec["own_gates"] == []


# ── NQ ORB / GC ICT ──────────────────────────────────────────────────────────

def test_nq_real_shape_is_rejected():
    rec = ALL_SCORERS["nq"]()
    assert rec["window"]["satisfied"] and rec["sign"] == "NEGATIVE"
    assert rec["status"] == "REJECTED"
    assert "c3_realized_pnl_positive" in rec["reason"]
    assert rec["sample"] == {"n_trades": 52, "n_days": 80}
    assert rec["headline_metrics"]["tracker_status"] == "ON-TRACK"


def test_nq_confirmed_when_positive_and_gates_pass():
    rec = pss.score_nq_orb({"latest": fut_latest(pnl=1500.0), "source_files": []}, AS_OF)
    assert rec["status"] == "CONFIRMED"
    assert all(g["status"] in ("PASS", "MANUAL") for g in rec["own_gates"])


def test_nq_rejected_on_hard_gate_even_if_positive():
    rec = pss.score_nq_orb({"latest": fut_latest(pnl=1500.0, n_long=5, n_short=47), "source_files": []}, AS_OF)
    assert rec["status"] == "REJECTED" and "c6_long_and_short_min_each" in rec["reason"]
    rec = pss.score_nq_orb({"latest": fut_latest(pnl=1500.0, worst_day=-0.06), "source_files": []}, AS_OF)
    assert rec["status"] == "REJECTED" and "c5_" in rec["reason"]


def test_nq_blocked_on_pause_and_stale():
    rec = pss.score_nq_orb({"latest": fut_latest(status="PAUSE", alerts=[{"severity": "CRITICAL", "code": "DATA_MISSING_CURRENT_SESSION"}]), "source_files": []}, AS_OF)
    assert rec["status"] == "BLOCKED" and "DATA_MISSING_CURRENT_SESSION" in rec["reason"]
    rec = pss.score_nq_orb({"latest": fut_latest(stale=49.0), "source_files": []}, AS_OF)
    assert rec["status"] == "BLOCKED"


def test_gc_real_shape_is_shadow_window_open():
    rec = ALL_SCORERS["gc"]()
    assert rec["status"] == "SHADOW" and not rec["window"]["satisfied"]
    assert rec["sign"] == "NEGATIVE"  # negative sign alone never rejects an open window
    assert "1/40 trades" in rec["reason"] and "thin line" in rec["reason"]
    assert rec["launched"] == "2026-06-14"
    st = {g["name"]: g["status"] for g in rec["own_gates"]}
    assert st["c2_fired_trades"] == "PENDING" and st["c3_realized_pnl_positive"] == "PENDING"


def test_futures_string_bools_are_not_trusted():
    latest = fut_latest(pnl=-1.0)
    latest["graduation_progress"]["realized_pnl_positive"] = "False"
    latest["graduation_progress"]["max_drawdown_within_15pct"] = "True"
    rec = pss.score_gc_ict({"latest": latest, "source_files": []}, AS_OF)
    st = {g["name"]: g["status"] for g in rec["own_gates"]}
    assert st["c3_realized_pnl_positive"] == "FAIL" and st["c4_max_drawdown_within_15pct"] == "PASS"


def test_futures_no_data():
    assert pss.score_gc_ict({"latest": None, "source_files": []}, AS_OF)["status"] == "NO_DATA"


# ── frozen stack ─────────────────────────────────────────────────────────────

def test_fs_zero_forward_rows_is_shadow_and_backfill_excluded():
    rec = ALL_SCORERS["fs"]()
    assert rec["status"] == "SHADOW" and rec["sign"] == "NONE"
    assert "0 forward rows" in rec["reason"]
    assert rec["sample"]["n_trades"] == 0 and rec["sample"]["n_backfill_rows_excluded"] == 3
    assert rec["headline_metrics"]["forward_n_skipped_by_d4"] == 1
    assert rec["headline_metrics"]["backfill_not_scored"]["n_rows"] == 3
    st = {g["name"]: g["status"] for g in rec["own_gates"]}
    assert st["f2_paper_equity_dd_within_envelope"] == "NOT_EVALUABLE"
    assert st["f3_d4_reproducibility"] == "PASS"


def test_fs_forward_rows_scored_separately_from_backfill():
    rows = fs_rows(forward_n=6, forward_r=0.5, backfill_n=10)
    rec = pss.score_frozen_stack({"state": fs_state(), "trades_rows": rows, "validation": None, "forward_split": "2026-09-11", "source_files": []}, "2026-10-01")
    assert rec["sign"] == "POSITIVE" and rec["sample"]["n_trades"] == 6
    assert rec["headline_metrics"]["forward_sum_net_r"] == 3.0
    assert rec["status"] == "SHADOW"  # 20 days < 90-day conservative window


def test_fs_window_satisfied_branches():
    base = {"state": fs_state(), "validation": {"headline": {"d4_agreement_pct": 95.0}}, "forward_split": "2026-09-11", "source_files": []}
    neg = pss.score_frozen_stack({**base, "trades_rows": fs_rows(forward_n=6, forward_r=-1.0)}, "2027-01-01")
    assert neg["window"]["satisfied"] and neg["status"] == "REJECTED"
    pos = pss.score_frozen_stack({**base, "trades_rows": fs_rows(forward_n=6, forward_r=1.0)}, "2027-01-01")
    assert pos["status"] == "SHADOW" and "f2_paper_equity_dd_within_envelope=NOT_EVALUABLE" in pos["reason"]


def test_fs_blocked_and_no_data():
    blk = pss.score_frozen_stack({"state": fs_state(status="ERROR"), "trades_rows": fs_rows(), "forward_split": "2026-09-11", "source_files": []}, AS_OF)
    assert blk["status"] == "BLOCKED"
    blk2 = pss.score_frozen_stack({"state": fs_state(load_errors={"BTCUSDT": "missing"}), "trades_rows": fs_rows(), "forward_split": "2026-09-11", "source_files": []}, AS_OF)
    assert blk2["status"] == "BLOCKED"
    assert pss.score_frozen_stack({"state": None, "trades_rows": None, "source_files": []}, AS_OF)["status"] == "NO_DATA"


# ── s21 ──────────────────────────────────────────────────────────────────────

def test_s21_no_state_is_no_data_with_legacy_note():
    rec = ALL_SCORERS["s21"]()
    assert rec["status"] == "NO_DATA"
    assert "LESSON_S21_PAPER_001/002" in rec["reason"] and "cycles_v2" in rec["reason"]
    assert rec["window"]["end_or_min_n"]["12wk"]["min_closed_trades"] == 15
    assert rec["window"]["end_or_min_n"]["24wk"]["min_closed_trades"] == 35


def test_s21_confirmed_rejected_shadow_blocked():
    ok = pss.score_s21(s21_inputs(s21_state()), AS_OF)
    assert ok["window"]["satisfied"] and ok["status"] == "SHADOW"  # 24wk milestone still PENDING
    assert "m_24wk_milestone=PENDING" in ok["reason"]
    full = pss.score_s21(s21_inputs(s21_state(closed=40, last_idx=120)), AS_OF)
    assert full["status"] == "CONFIRMED"
    neg = pss.score_s21(s21_inputs(s21_state(closed=40, last_idx=120, equity=95000.0)), AS_OF)
    assert neg["status"] == "REJECTED"
    drag = pss.score_s21(s21_inputs(s21_state(cost_drag=0.09)), AS_OF)
    assert drag["status"] == "REJECTED" and "COST_DRAG_GT_MAX" in json.dumps(drag["own_gates"])
    early = pss.score_s21(s21_inputs(s21_state(closed=3, last_idx=10)), AS_OF)
    assert early["status"] == "SHADOW" and not early["window"]["satisfied"]
    halt = pss.score_s21(s21_inputs(s21_state(halted=True)), AS_OF)
    assert halt["status"] == "BLOCKED"


def test_s21_prefers_cycle_runner_gate_eval_when_given():
    ge = {"checks": {"halted": False, "annualized_cost_drag": 0.01, "max_drawdown": 0.02, "mechanic_drift": False},
          "gates": {"12wk": {"status": "FAIL", "reason": "MECHANIC_DRIFT"}, "24wk": {"status": "NOT_YET_EVALUABLE", "reason": "x"}},
          "disclosure": "DIAGNOSTIC_ONLY"}
    rec = pss.score_s21(s21_inputs(s21_state(), gate_eval=ge), AS_OF)
    assert rec["status"] == "REJECTED" and "m_12wk_milestone" in rec["reason"]
    assert rec["headline_metrics"]["gate_eval_source"] == "cycle_runner.evaluate_gates"


# ── file plumbing on tmp_path ────────────────────────────────────────────────

def test_score_all_on_empty_roots_is_all_no_data(tmp_path):
    recs = pss.score_all(AS_OF, ext_root=tmp_path / "ext", sparta_root=tmp_path / "sp")
    assert [r["line"] for r in recs] == list(pss.LINES)
    assert all(r["status"] == "NO_DATA" for r in recs)
    assert all(r["source_files"] == [] for r in recs)


def test_score_all_reads_synthetic_tree(tmp_path):
    ext = tmp_path / "ext"
    (ext / "reports" / "paper_funding_carry").mkdir(parents=True)
    (ext / "reports" / "nq_paper_orb").mkdir(parents=True)
    (ext / "reports" / "gc_paper_ict").mkdir(parents=True)
    (ext / "data").mkdir()
    (ext / "reports" / "paper_funding_carry" / "latest.json").write_text(json.dumps(fc_latest()), encoding="utf-8")
    (ext / "reports" / "nq_paper_orb" / "latest.json").write_text(json.dumps(fut_latest()), encoding="utf-8")
    (ext / "reports" / "gc_paper_ict" / "latest.json").write_text(json.dumps(fut_latest(trades=1)), encoding="utf-8")
    (ext / "data" / "final_stack_paper_state.json").write_text(json.dumps(fs_state()), encoding="utf-8")
    (ext / "data" / "final_stack_paper_trades.csv").write_text(
        "symbol,entry_time,exit_time,net_r,engine\nBTCUSDT,2020-02-26,2020-02-27,-1.025,v2_bb_snapback\n", encoding="utf-8")
    recs = pss.score_all(AS_OF, ext_root=ext, sparta_root=tmp_path / "sp")
    by = {r["line"]: r for r in recs}
    assert by["funding_carry_paper"]["status"] == "SHADOW"
    assert by["nq_orb_paper"]["status"] == "REJECTED"
    assert by["gc_ict_paper"]["status"] == "SHADOW"
    assert by["frozen_stack_paper_forward"]["status"] == "SHADOW"
    assert by["s21_weekly_rs_paper"]["status"] == "NO_DATA"
    assert all(Path(p).is_relative_to(ext) for r in recs for p in r["source_files"])


def test_closure_written_once_and_idempotent(tmp_path):
    rd = tmp_path / "reports"
    hist = rd / pss.HISTORY_JSONL
    rej = pss.score_nq_orb({"latest": fut_latest(), "source_files": []}, AS_OF)
    shadow = ALL_SCORERS["gc"]()
    written = pss.write_closure_recommendations([rej, shadow], rd, hist)
    assert [p.name for p in written] == [f"closure_recommendation_nq_orb_paper_{AS_OF}.md"]
    text = written[0].read_text(encoding="utf-8")
    assert pss.BANNER in text and "REJECTED" in text and pss.forbidden_words_found(text) == []
    written[0].write_text(text + "\nOPERATOR NOTE", encoding="utf-8")
    # same day again: file exists -> untouched
    assert pss.write_closure_recommendations([rej], rd, hist) == []
    assert written[0].read_text(encoding="utf-8").endswith("OPERATOR NOTE")
    # later day, history records the resolution -> no second closure file
    with hist.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(pss.history_line([rej], AS_OF)) + "\n")
    rej2 = pss.score_nq_orb({"latest": fut_latest()}, "2026-09-12")
    assert pss.write_closure_recommendations([rej2], rd, hist) == []
    # a different resolution (CONFIRMED after a restart) is a new first-time event
    conf = pss.score_nq_orb({"latest": fut_latest(pnl=900.0)}, "2026-12-01")
    assert len(pss.write_closure_recommendations([conf], rd, hist)) == 1
    assert sorted(p.name for p in rd.glob("closure_recommendation_*.md")) == [
        f"closure_recommendation_nq_orb_paper_{AS_OF}.md", "closure_recommendation_nq_orb_paper_2026-12-01.md"]


def test_history_line_shape():
    recs = [ALL_SCORERS["nq"](), ALL_SCORERS["s21"]()]
    line = pss.history_line(recs, AS_OF)
    assert line["as_of"] == AS_OF and set(line["lines"]) == {"nq_orb_paper", "s21_weekly_rs_paper"}
    assert set(line["lines"]["nq_orb_paper"]) == {"status", "sign", "reason", "window_satisfied"}
    assert "generated_at" not in line


def test_main_writes_only_under_report_dir(tmp_path, monkeypatch):
    rd = tmp_path / "out"
    monkeypatch.setattr(pss, "score_all", lambda as_of: [ALL_SCORERS["nq"](), ALL_SCORERS["gc"]()])
    monkeypatch.setattr(pss, "_register_manual_entry", lambda: None)
    assert pss.main(["--as-of", AS_OF, "--report-dir", str(rd)]) == 0
    names = sorted(p.name for p in rd.iterdir())
    assert names == [f"closure_recommendation_nq_orb_paper_{AS_OF}.md", pss.HISTORY_JSONL,
                     pss.SCORECARD_JSON, pss.SCORECARD_MD]
    payload = json.loads((rd / pss.SCORECARD_JSON).read_text(encoding="utf-8"))
    assert payload["banner"] == pss.BANNER and len(payload["records"]) == 2
    assert pss.forbidden_words_found((rd / pss.SCORECARD_MD).read_text(encoding="utf-8")) == []
    assert pss.main(["--as-of", AS_OF, "--report-dir", str(rd)]) == 0
    assert len((rd / pss.HISTORY_JSONL).read_text(encoding="utf-8").splitlines()) == 2
    assert len(list(rd.glob("closure_recommendation_*.md"))) == 1


# ── 2026-09-12: recorded closures and the corrected frozen-stack split ───────

def test_recorded_closure_short_circuits_a_line(tmp_path):
    """A line the operator has closed must report the closure, not a live status,
    so it stops reappearing in the daily human queue."""
    c = tmp_path / "CLOSURE_DECISION_2026-09-11.md"
    c.write_text("# NQ ORB closure\n\n**Decision: CLOSED - REJECTED_BY_OWN_GRADUATION_CRITERIA.**\n",
                 encoding="utf-8")
    rec = pss._score_futures_tracker(
        pss.LINE_NQ_ORB, pss.NQ_CRITERIA,
        {"latest": {"status": "PAUSE", "tracker_state": {}}, "source_files": [],
         "closure_files": [str(c)]},
        "2026-09-12", "2026-05-13")
    assert rec["status"] == pss.STATUS_REJECTED
    assert "closed by recorded operator decision" in rec["reason"]
    assert rec["window"]["satisfied"] is True
    assert str(c) in rec["source_files"]


def test_no_closure_file_still_scores_normally(tmp_path):
    rec = pss._score_futures_tracker(
        pss.LINE_GC_ICT, pss.GC_CRITERIA,
        {"latest": None, "source_files": [], "closure_files": []},
        "2026-09-12", "2026-06-14")
    assert rec["status"] == pss.STATUS_NO_DATA


def test_empty_closure_file_is_ignored(tmp_path):
    c = tmp_path / "CLOSURE_DECISION_blank.md"
    c.write_text("   \n", encoding="utf-8")
    assert pss._recorded_closure({"closure_files": [str(c)]}) is None


def test_frozen_stack_split_is_the_data_ceiling_not_today():
    """The 1m cache had stopped at 2026-03-31; entries after it were unavailable to
    the bot under locked parameters, so they are out-of-sample evidence."""
    assert pss.FROZEN_STACK_FORWARD_SPLIT == "2026-03-31"
    assert "ceiling" in pss.FROZEN_STACK_SPLIT_BASIS
