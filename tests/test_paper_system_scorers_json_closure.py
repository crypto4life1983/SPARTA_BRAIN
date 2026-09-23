"""JSON closure records (2026-09-23).

The operator closed funding_carry_paper and s21_weekly_rs_paper on 2026-09-19 with JSON
records that carry a `verdict` (commit 54dff246). The scorer previously recognised only
`CLOSURE_DECISION_*.md`, so both lines kept re-deriving a live status. These tests pin the
new behaviour on tmp_path only: nothing here reads the real repos.
"""
from __future__ import annotations

import json
from pathlib import Path

from tools import paper_system_scorers as pss

AS_OF = "2026-09-23"


def _write_json(p: Path, doc: dict) -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(doc), encoding="utf-8")
    return p


# ── recognising a closure JSON ───────────────────────────────────────────────

def test_closure_files_keeps_only_json_with_closed_verdict(tmp_path):
    _write_json(tmp_path / "funding_carry_closure_decision_20260919.json",
                {"verdict": "REJECTED_CLOSED", "decision_date": "2026-09-19"})
    _write_json(tmp_path / "S21_REPLAYED_OOS_DIAGNOSTIC_20260919.json",
                {"verdict": "CLOSED_FAILED_OWN_DRAWDOWN_GATE", "run_date": "2026-09-19"})
    _write_json(tmp_path / "g2_same_period_estimate.json", {"cagr_pct": 2.296})       # no verdict
    _write_json(tmp_path / "open_window_read.json", {"verdict": "CONFIRMED_POSITIVE"})  # not closed
    (tmp_path / "notes.json").write_text("not json at all", encoding="utf-8")
    (tmp_path / "CLOSURE_DECISION_2026-09-11.md").write_text("**Decision**: closed", encoding="utf-8")

    found = [Path(p).name for p in pss._closure_files(tmp_path)]
    assert found == ["CLOSURE_DECISION_2026-09-11.md",
                     "S21_REPLAYED_OOS_DIAGNOSTIC_20260919.json",
                     "funding_carry_closure_decision_20260919.json"]


def test_closure_files_on_missing_folder_is_empty(tmp_path):
    assert pss._closure_files(tmp_path / "nope") == []


def test_recorded_closure_json_summary_uses_verdict_and_date(tmp_path):
    p = _write_json(tmp_path / "funding_carry_closure_decision_20260919.json",
                    {"verdict": "REJECTED_CLOSED", "decision_date": "2026-09-19"})
    c = pss._recorded_closure({"closure_files": [str(p)]})
    assert c["summary"] == "REJECTED_CLOSED (2026-09-19)"
    assert c["path"] == str(p)


def test_recorded_closure_skips_json_without_closed_verdict(tmp_path):
    p = _write_json(tmp_path / "estimate.json", {"verdict": "CONFIRMED_POSITIVE"})
    assert pss._recorded_closure({"closure_files": [str(p)]}) is None


def test_markdown_closure_still_read_the_old_way(tmp_path):
    p = tmp_path / "CLOSURE_DECISION_2026-09-11.md"
    p.write_text("# closure\n\n**Decision**: REJECTED on own gate\n", encoding="utf-8")
    c = pss._recorded_closure({"closure_files": [str(p)]})
    assert "summary" not in c
    assert c["text"].startswith("# closure")


# ── the two lines now honour the record ──────────────────────────────────────

def _fc_open_inputs():
    # a tracker that would otherwise read CONFIRMED (window satisfied, positive, no alerts)
    return {"latest": {
        "strategy_label": "always_on_monthly",
        "report_date_utc": "2026-09-23T00:00:00+00:00",
        "tracker_state": {"launch_date_utc": "2026-05-13T00:00:00+00:00", "days_since_launch": 133,
                          "paper_equity": 10049.78, "initial_capital": 10000.0},
        "since_inception": {"final_equity_usd": 10049.78, "funding_pnl_total_usd": 97.96,
                            "basis_pnl_total_usd": 0.18, "total_simulated_costs_usd": 48.36,
                            "cost_consumption_pct": 0.3577, "max_drawdown_pct": -0.0017,
                            "n_position_changes": 5},
        "alerts_active": [],
        "data_freshness": {"last_data_ts_utc": "2026-09-23T00:00:00+00:00", "stale_hours": 0.0},
    }, "alerts_rows": [], "phase8_report_present": True, "source_files": ["latest.json"]}


def test_funding_carry_closed_on_record_beats_a_confirmed_tracker(tmp_path):
    p = _write_json(tmp_path / "reports" / "approvals" / "funding_carry_closure_decision_20260919.json",
                    {"verdict": "REJECTED_CLOSED", "decision_date": "2026-09-19"})
    inputs = _fc_open_inputs()
    before = pss.score_funding_carry(inputs, AS_OF)  # without the record: a live read
    assert before["window"]["kind"] != "closed_by_operator"
    assert before["status"] in (pss.STATUS_CONFIRMED, pss.STATUS_SHADOW)

    inputs["closure_files"] = [str(p)]
    rec = pss.score_funding_carry(inputs, AS_OF)
    assert rec["status"] == pss.STATUS_REJECTED
    assert rec["window"]["kind"] == "closed_by_operator"
    assert "REJECTED_CLOSED (2026-09-19)" in rec["reason"]
    assert str(p) in rec["source_files"]
    assert pss.forbidden_words_found(rec["reason"] + rec["recommendation"]) == []


def test_s21_closed_on_record_instead_of_no_data(tmp_path):
    p = _write_json(tmp_path / "reports" / "s21_weekly_rs_paper" / "S21_REPLAYED_OOS_DIAGNOSTIC_20260919.json",
                    {"verdict": "CLOSED_FAILED_OWN_DRAWDOWN_GATE", "run_date": "2026-09-19",
                     "label": "REPLAYED_DIAGNOSTIC_NOT_PAPER_EVIDENCE"})
    base = {"state": None, "gate_eval": None, "thresholds": {}, "rebalance_days": 5,
            "start_cash": 100_000.0, "manifest_status": {}, "state_path": "x", "source_files": []}
    assert pss.score_s21(dict(base), AS_OF)["status"] == pss.STATUS_NO_DATA

    rec = pss.score_s21({**base, "closure_files": [str(p)]}, AS_OF)
    assert rec["status"] == pss.STATUS_REJECTED
    assert rec["window"]["kind"] == "closed_by_operator"
    assert "CLOSED_FAILED_OWN_DRAWDOWN_GATE (2026-09-19)" in rec["reason"]


# ── loaders find the SPARTA-side records; score_all wires the root through ───

def test_loaders_pick_up_sparta_side_records(tmp_path):
    ext, sp = tmp_path / "ext", tmp_path / "sparta"
    fc = _write_json(sp / "reports" / "approvals" / "funding_carry_closure_decision_20260919.json",
                     {"verdict": "REJECTED_CLOSED"})
    s21 = _write_json(sp / "reports" / "s21_weekly_rs_paper" / "diag.json",
                      {"verdict": "CLOSED_FAILED_OWN_DRAWDOWN_GATE"})
    _write_json(sp / "reports" / "s21_weekly_rs_paper" / "not_a_closure.json", {"result": 1})

    assert pss.load_funding_carry_inputs(ext, sp)["closure_files"] == [str(fc)]
    assert pss.load_s21_inputs(sp)["closure_files"] == [str(s21)]

    recs = {r["line"]: r for r in pss.score_all(AS_OF, ext_root=ext, sparta_root=sp)}
    assert recs[pss.LINE_FUNDING_CARRY]["window"]["kind"] == "closed_by_operator"
    assert recs[pss.LINE_S21]["window"]["kind"] == "closed_by_operator"


def test_loader_without_records_is_unchanged(tmp_path):
    ext, sp = tmp_path / "ext", tmp_path / "sparta"
    assert pss.load_funding_carry_inputs(ext, sp)["closure_files"] == []
    assert pss.load_s21_inputs(sp)["closure_files"] == []


# ── no redundant closure recommendation for a line already closed on record ──

def test_no_closure_recommendation_for_closed_by_operator(tmp_path):
    p = _write_json(tmp_path / "funding_carry_closure_decision_20260919.json",
                    {"verdict": "REJECTED_CLOSED", "decision_date": "2026-09-19"})
    inputs = {**_fc_open_inputs(), "closure_files": [str(p)]}
    closed = pss.score_funding_carry(inputs, AS_OF)
    rd, hist = tmp_path / "rep", tmp_path / "rep" / "history.jsonl"
    assert pss.write_closure_recommendations([closed], rd, hist) == []
    assert not list(rd.glob("closure_recommendation_*.md")) if rd.exists() else True

    # an ordinary REJECTED read (not closed on record) still gets its one recommendation
    plain = pss.score_funding_carry({**_fc_open_inputs(), "latest": {
        **_fc_open_inputs()["latest"],
        "since_inception": {**_fc_open_inputs()["latest"]["since_inception"],
                            "final_equity_usd": 9950.0, "max_drawdown_pct": -0.12}}}, AS_OF)
    assert plain["status"] == pss.STATUS_REJECTED
    assert len(pss.write_closure_recommendations([plain], rd, hist)) == 1
