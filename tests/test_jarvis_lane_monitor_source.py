"""Tests for the read-only Crypto-D1 Lane Monitor source aggregator.

`app._jarvis_crypto_d1_lane_monitor()` produces a compact, DYNAMIC lane summary
for the dashboard: the clamped lane / evidence / readiness truth (reused from the
Mission Flow source) plus the LATEST official checkpoint resolved by scanning
committed plan -> executed result -> decision-memo artifacts under reports/.

These tests pin the safety contract:
- a plan-only checkpoint reports PLAN_ONLY + the "implement runner + tests" action;
- an executed result advances the checkpoint to EXECUTED with the verdict/run_id;
- a decision memo advances it to DECISION_RECORDED (highest precedence);
- a tampered result verdict (ACTIVE/STRONG) is clamped to WATCH, never surfaced;
- the four authorization booleans are ALWAYS false, even if a source claims true;
- latest_master reflects the injected git HEAD (the reader runs no subprocess);
- the aggregator never creates a directory and never runs a subprocess.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

pytest.importorskip("fastapi")

_CANDIDATES_REL = \
    "reports/strategy_factory_routines/candidate_registry/candidates.json"
_READINESS_REL = "reports/crypto_d1_readiness_gate_v1/readiness_gate.json"
_PLAN_REL = "reports/crypto_d1_momentum_confirmation_v1_plan/report.json"
_RESULT_REL = ("reports/crypto_d1_momentum_confirmation_v1/"
               "CRYPTO_D1_SPOT_BTC_ETH_SOL_V001_V002/"
               "crypto_d1_momentum_confirmation_report.json")
_MEMO_REL = ("reports/crypto_d1_momentum_confirmation_v1/"
             "CRYPTO_D1_SPOT_BTC_ETH_SOL_V001_V002/decision_memo.md")


def _write(base: Path, rel: str, text: str) -> None:
    p = base / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def _write_json(base: Path, rel: str, obj) -> None:
    _write(base, rel, json.dumps(obj))


def _seed_lane_sources(base: Path) -> None:
    """Seed the clamped lane / evidence / readiness truth (WATCH/MIXED/NOT_READY)."""
    _write_json(base, _CANDIDATES_REL, {
        "candidates": [
            {"candidate_id": "crypto_d1_protocol", "lane": "crypto_d1",
             "status": "WATCH", "evidence_level": "MIXED"},
        ],
    })
    _write_json(base, _READINESS_REL, {
        "readiness_status": "NOT_READY_FOR_REAL_DATA"})


def _seed_plan(base: Path, status: str = "PLAN_ONLY_NOT_EXECUTED") -> None:
    _write_json(base, _PLAN_REL, {
        "plan_id": "crypto_d1_momentum_confirmation_v1_plan",
        "plan_date": "2026-06-03",
        "status": status,
        # Even if a plan ever claimed authorization, the monitor must clamp false.
        "authorizes_execution": True,
        "authorizes_paper_or_live": True,
        "promotes_active_or_strong": True,
        "starts_bundle_23": True,
    })


def _seed_result(base: Path, verdict: str = "WATCH",
                 run_id: str = "2a3be425522a04ec") -> None:
    _write_json(base, _RESULT_REL, {
        "pass_watch_fail_status": verdict, "run_id": run_id})


# --- Test 1: plan-only checkpoint ------------------------------------------

def test_plan_only_checkpoint(monkeypatch, tmp_path):
    import app as app_module
    _seed_lane_sources(tmp_path)
    _seed_plan(tmp_path)
    monkeypatch.setattr(app_module, "BASE", tmp_path)
    lm = app_module._jarvis_crypto_d1_lane_monitor(git_head="c66c827")

    assert lm["read_only"] is True
    assert lm["display_only"] is True
    assert lm["no_execution"] is True
    assert lm["safety_level"] == "research_only"

    assert lm["lane_status"] == "WATCH"
    assert lm["evidence_level"] == "MIXED"
    assert lm["lane_label"] == "WATCH / MIXED"
    assert lm["readiness_status"] == "NOT_READY_FOR_REAL_DATA"

    cp = lm["latest_checkpoint"]
    assert cp["title"] == "Momentum Confirmation v1"
    assert cp["stage"] == "PLAN_ONLY"
    assert cp["plan_status"] == "PLAN_ONLY_NOT_EXECUTED"
    assert "PLAN_ONLY_NOT_EXECUTED" in cp["status_label"]
    assert cp["verdict"] is None
    assert cp["run_id"] is None

    assert lm["latest_master"] == "c66c827"
    assert "Implement runner" in lm["next_required_action"]

    # authorization booleans are ALWAYS false (even though the plan claimed true)
    assert lm["trading_authorization"] is False
    assert lm["paper_or_live_authorized"] is False
    assert lm["bundle_23_started"] is False
    assert lm["active_strong_promoted"] is False


# --- Test 2: executed result advances the checkpoint -----------------------

def test_executed_result_checkpoint(monkeypatch, tmp_path):
    import app as app_module
    _seed_lane_sources(tmp_path)
    _seed_plan(tmp_path)
    _seed_result(tmp_path, verdict="WATCH", run_id="2a3be425522a04ec")
    monkeypatch.setattr(app_module, "BASE", tmp_path)
    lm = app_module._jarvis_crypto_d1_lane_monitor(git_head="c66c827")

    cp = lm["latest_checkpoint"]
    assert cp["stage"] == "EXECUTED"
    assert cp["verdict"] == "WATCH"
    assert cp["run_id"] == "2a3be425522a04ec"
    assert cp["status_label"] == "Momentum Confirmation v1 — EXECUTED (WATCH)"
    assert cp["report_rel"].endswith("crypto_d1_momentum_confirmation_report.json")
    assert cp["decision_memo_rel"] is None
    assert "Operator review" in lm["next_required_action"]
    # the lane never promotes on an executed WATCH result
    assert lm["lane_status"] == "WATCH"
    assert lm["active_strong_promoted"] is False


# --- Test 3: a decision memo takes precedence over the executed result ------

def test_decision_memo_checkpoint(monkeypatch, tmp_path):
    import app as app_module
    _seed_lane_sources(tmp_path)
    _seed_plan(tmp_path)
    _seed_result(tmp_path, verdict="WATCH")
    _write(tmp_path, _MEMO_REL, "# Decision: remain WATCH / MIXED\n")
    monkeypatch.setattr(app_module, "BASE", tmp_path)
    lm = app_module._jarvis_crypto_d1_lane_monitor(git_head="c66c827")

    cp = lm["latest_checkpoint"]
    assert cp["stage"] == "DECISION_RECORDED"
    assert cp["decision_memo_rel"].endswith("decision_memo.md")
    assert "decision recorded" in cp["status_label"]
    assert "next checkpoint" in lm["next_required_action"]


# --- Test 4: a tampered result verdict is clamped --------------------------

def test_forbidden_verdict_is_clamped(monkeypatch, tmp_path):
    import app as app_module
    _seed_lane_sources(tmp_path)
    _seed_plan(tmp_path)
    _seed_result(tmp_path, verdict="ACTIVE", run_id="deadbeefdeadbeef")
    monkeypatch.setattr(app_module, "BASE", tmp_path)
    lm = app_module._jarvis_crypto_d1_lane_monitor(git_head="c66c827")

    cp = lm["latest_checkpoint"]
    # ACTIVE must NEVER surface; it is clamped to WATCH with a recorded warning
    assert cp["verdict"] == "WATCH"
    assert cp["verdict"] != "ACTIVE"
    assert any("ACTIVE" in w and "clamped" in w for w in lm["warnings"])
    assert lm["active_strong_promoted"] is False


# --- Test 5: no plan present fails closed -----------------------------------

def test_no_plan_fails_closed(monkeypatch, tmp_path):
    import app as app_module
    _seed_lane_sources(tmp_path)  # lane sources only; NO plan artifact
    monkeypatch.setattr(app_module, "BASE", tmp_path)
    lm = app_module._jarvis_crypto_d1_lane_monitor()

    cp = lm["latest_checkpoint"]
    assert cp["stage"] == "UNKNOWN"
    assert cp["plan_id"] is None
    assert any("no crypto_d1 plan" in w for w in lm["warnings"])
    # conservative defaults still hold and authorization stays false
    assert lm["lane_status"] == "WATCH"
    assert lm["readiness_status"] == "NOT_READY_FOR_REAL_DATA"
    assert lm["latest_master"] is None
    assert lm["trading_authorization"] is False


# --- Test 6: no side effects (no dir creation, no subprocess) ---------------

def test_no_side_effects(monkeypatch, tmp_path):
    import app as app_module
    _seed_lane_sources(tmp_path)
    _seed_plan(tmp_path)
    monkeypatch.setattr(app_module, "BASE", tmp_path)

    def _boom(*a, **k):  # pragma: no cover - must never be called
        raise AssertionError("lane monitor source must not run subprocesses")

    monkeypatch.setattr(subprocess, "run", _boom)
    monkeypatch.setattr(subprocess, "Popen", _boom)

    lm = app_module._jarvis_crypto_d1_lane_monitor(git_head="c66c827")
    assert lm["latest_checkpoint"]["stage"] == "PLAN_ONLY"
    # a read-only probe must not materialize the research data directory
    assert not (tmp_path / "data" / "crypto_d1_research").exists()


# --- Test 7: humanizer keeps version tokens lowercase ----------------------

def test_humanize_plan_title():
    import app as app_module
    fn = app_module._jarvis_lm_humanize_plan
    assert fn("crypto_d1_momentum_confirmation_v1_plan") == \
        "Momentum Confirmation v1"
    assert fn("crypto_d1_baseline_backtest_plan_v1_plan") == \
        "Baseline Backtest Plan v1"


# --- Test 8: ROUTE-LEVEL — /api/jarvis/status surfaces lane_monitor ---------

def test_route_status_includes_lane_monitor():
    """The live read-only endpoint must expose the lane_monitor payload."""
    import app as app_module
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    r = client.get("/api/jarvis/status")
    assert r.status_code == 200
    d = r.json()
    assert "lane_monitor" in d, "status payload missing lane_monitor key"
    lm = d["lane_monitor"]
    assert isinstance(lm, dict)
    assert lm["read_only"] is True
    assert lm["display_only"] is True
    assert lm["no_execution"] is True


# --- Test 9: ROUTE-LEVEL — clamped truth + all authorization flags false ----

def test_route_lane_monitor_truth_and_flags():
    """Route view reflects the committed clamped truth and never authorizes."""
    import app as app_module
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    lm = client.get("/api/jarvis/status").json()["lane_monitor"]

    assert lm["lane_status"] == "WATCH"
    assert lm["evidence_level"] == "MIXED"
    assert lm["lane_label"] == "WATCH / MIXED"
    assert lm["readiness_status"] == "NOT_READY_FOR_REAL_DATA"

    # the four authorization booleans are ALWAYS false over the wire
    assert lm["trading_authorization"] is False
    assert lm["paper_or_live_authorized"] is False
    assert lm["bundle_23_started"] is False
    assert lm["active_strong_promoted"] is False

    # a committed result may never surface a promoting verdict on the wire
    assert lm["latest_checkpoint"]["verdict"] not in ("ACTIVE", "STRONG", "PASS")


# --- Test 10: ROUTE-LEVEL clamp — ACTIVE/STRONG/PASS cannot surface ---------

@pytest.mark.parametrize("forbidden", ["ACTIVE", "STRONG", "PASS"])
def test_route_forbidden_verdict_cannot_surface(monkeypatch, tmp_path,
                                                forbidden):
    """Even if a result file is tampered to a promoting verdict, the route view
    clamps it to WATCH and records a warning; promotion stays false."""
    import app as app_module
    from fastapi.testclient import TestClient
    _seed_lane_sources(tmp_path)
    _seed_plan(tmp_path)
    _seed_result(tmp_path, verdict=forbidden, run_id="deadbeefdeadbeef")
    monkeypatch.setattr(app_module, "BASE", tmp_path)

    client = TestClient(app_module.app)
    lm = client.get("/api/jarvis/status").json()["lane_monitor"]
    cp = lm["latest_checkpoint"]

    assert cp["verdict"] == "WATCH"
    assert cp["verdict"] != forbidden
    assert any(forbidden in w and "clamped" in w for w in lm["warnings"])
    assert lm["active_strong_promoted"] is False
    assert lm["trading_authorization"] is False


# --- Test 11: missing plan_date tie-break is deterministic -----------------

def test_missing_plan_date_tiebreak_is_deterministic(monkeypatch, tmp_path):
    """Two plans with NO plan_date must resolve to a single stable checkpoint
    (lexically-last plan dir), never raise, and never depend on FS order."""
    import app as app_module
    _seed_lane_sources(tmp_path)
    # Two competing plans, both WITHOUT a plan_date field.
    _write_json(tmp_path, "reports/crypto_d1_aaa_first_v1_plan/report.json",
                {"plan_id": "crypto_d1_aaa_first_v1_plan",
                 "status": "PLAN_ONLY_NOT_EXECUTED"})
    _write_json(tmp_path, "reports/crypto_d1_zzz_latest_v1_plan/report.json",
                {"plan_id": "crypto_d1_zzz_latest_v1_plan",
                 "status": "PLAN_ONLY_NOT_EXECUTED"})
    monkeypatch.setattr(app_module, "BASE", tmp_path)

    first = app_module._jarvis_crypto_d1_lane_monitor(git_head="c66c827")
    second = app_module._jarvis_crypto_d1_lane_monitor(git_head="c66c827")

    cp = first["latest_checkpoint"]
    # lexically-last dir wins the tie deterministically
    assert cp["plan_id"] == "crypto_d1_zzz_latest_v1_plan"
    assert cp["title"] == "Zzz Latest v1"
    # stable across repeated calls (no FS-iteration-order dependence)
    assert second["latest_checkpoint"]["plan_id"] == cp["plan_id"]


# --- Test 12: confirmation nuance labels sample sufficiency, never promotes --

def test_result_nuance_n20_all_n30_btc_only():
    """The compact nuance reports N=20 floor-backed on all 3 assets and N=30
    floor-backed on BTC only (ETH/SOL sample-thin) from family OOS counts."""
    import app as app_module
    robj = {
        "pass_watch_fail_status": "WATCH",
        "family_oos_trade_counts": {
            "momentum_20": {"per_asset": {"BTC": 32, "ETH": 31, "SOL": 23}},
            "momentum_30": {"per_asset": {"BTC": 27, "ETH": 19, "SOL": 18}},
        },
    }
    rn = app_module._jarvis_lm_result_nuance(robj)
    assert rn["available"] is True
    assert "N=20 floor-backed on all 3 assets" in rn["summary"]
    assert "N=30 floor-backed on BTC only" in rn["summary"]
    assert "ETH,SOL sample-thin" in rn["summary"]
    by_lb = {e["lookback"]: e for e in rn["per_lookback"]}
    assert by_lb["N=20"]["clears_floor"] == ["BTC", "ETH", "SOL"]
    assert by_lb["N=30"]["clears_floor"] == ["BTC"]
    assert by_lb["N=30"]["sample_thin"] == ["ETH", "SOL"]


def test_result_nuance_falls_back_safely_on_missing_counts():
    """No family counts -> the safe 'details in latest report.' fallback."""
    import app as app_module
    rn = app_module._jarvis_lm_result_nuance({"pass_watch_fail_status": "WATCH"})
    assert rn["available"] is False
    assert rn["summary"] == "details in latest report."


# --- Test 8: confirmation nuance is summarized from the report -------------

_FAMILY_OOS_COUNTS = {
    "momentum_20": {"meets_family_floor": True, "oos_trades_total": 86,
                    "per_asset": {"BTC": 32, "ETH": 31, "SOL": 23}},
    "momentum_30": {"meets_family_floor": True, "oos_trades_total": 64,
                    "per_asset": {"BTC": 27, "ETH": 19, "SOL": 18}},
}


def _seed_result_with_nuance(base: Path) -> None:
    _write_json(base, _RESULT_REL, {
        "pass_watch_fail_status": "WATCH", "run_id": "2a3be425522a04ec",
        "family_oos_trade_counts": _FAMILY_OOS_COUNTS})


def test_result_nuance_floor_summary(monkeypatch, tmp_path):
    import app as app_module
    _seed_lane_sources(tmp_path)
    _seed_plan(tmp_path)
    _seed_result_with_nuance(tmp_path)
    monkeypatch.setattr(app_module, "BASE", tmp_path)
    lm = app_module._jarvis_crypto_d1_lane_monitor(git_head="c66c827")

    rn = lm["result_nuance"]
    assert rn["available"] is True
    # N=20 clears the 20-trade floor on all three; N=30 on BTC only.
    assert "N=20 floor-backed on all 3 assets" in rn["summary"]
    assert "N=30 floor-backed on BTC only" in rn["summary"]
    assert "ETH,SOL sample-thin" in rn["summary"]
    by_lb = {x["lookback"]: x for x in rn["per_lookback"]}
    assert by_lb["N=20"]["clears_floor"] == ["BTC", "ETH", "SOL"]
    assert by_lb["N=30"]["clears_floor"] == ["BTC"]
    assert by_lb["N=30"]["sample_thin"] == ["ETH", "SOL"]


def test_result_nuance_falls_back_when_counts_absent(monkeypatch, tmp_path):
    import app as app_module
    _seed_lane_sources(tmp_path)
    _seed_plan(tmp_path)
    _seed_result(tmp_path)  # no family_oos_trade_counts in this report
    monkeypatch.setattr(app_module, "BASE", tmp_path)
    lm = app_module._jarvis_crypto_d1_lane_monitor(git_head="c66c827")

    rn = lm["result_nuance"]
    assert rn["available"] is False
    assert rn["summary"] == "details in latest report."


# --- Test 9: newest-plan selection with a missing plan_date ----------------

_ALT_PLAN_REL = "reports/crypto_d1_baseline_backtest_v1_plan/report.json"


def test_newest_plan_prefers_dated_over_dateless(monkeypatch, tmp_path):
    import app as app_module
    _seed_lane_sources(tmp_path)
    # A dateless plan must never outrank a dated one (empty string sorts first).
    _write_json(tmp_path, _ALT_PLAN_REL, {
        "plan_id": "crypto_d1_baseline_backtest_v1_plan",
        "status": "PLAN_ONLY_NOT_EXECUTED"})  # NO plan_date
    _seed_plan(tmp_path)  # the momentum confirmation plan, plan_date 2026-06-03
    monkeypatch.setattr(app_module, "BASE", tmp_path)
    lm = app_module._jarvis_crypto_d1_lane_monitor(git_head="c66c827")

    cp = lm["latest_checkpoint"]
    assert cp["plan_id"] == "crypto_d1_momentum_confirmation_v1_plan"
    assert cp["title"] == "Momentum Confirmation v1"
    assert cp["plan_date"] == "2026-06-03"


def test_newest_plan_dateless_tiebreak_is_deterministic(monkeypatch, tmp_path):
    import app as app_module
    _seed_lane_sources(tmp_path)
    # Two dateless plans: tie-break is by directory name; the lexically last
    # ('...momentum...' > '...baseline...') wins, deterministically.
    _write_json(tmp_path, _ALT_PLAN_REL, {
        "plan_id": "crypto_d1_baseline_backtest_v1_plan",
        "status": "PLAN_ONLY_NOT_EXECUTED"})
    _seed_plan(tmp_path, status="PLAN_ONLY_NOT_EXECUTED")
    # Strip the plan_date so both are dateless.
    obj = json.loads((tmp_path / _PLAN_REL).read_text(encoding="utf-8"))
    obj.pop("plan_date", None)
    _write_json(tmp_path, _PLAN_REL, obj)
    monkeypatch.setattr(app_module, "BASE", tmp_path)
    lm = app_module._jarvis_crypto_d1_lane_monitor(git_head="c66c827")

    cp = lm["latest_checkpoint"]
    assert cp["plan_id"] == "crypto_d1_momentum_confirmation_v1_plan"
    assert cp["plan_date"] is None


# --- Test 10: route-level wiring exposes the read-only monitor --------------

def test_route_status_includes_lane_monitor(monkeypatch, tmp_path):
    import app as app_module
    from fastapi.testclient import TestClient
    _seed_lane_sources(tmp_path)
    _seed_plan(tmp_path)
    monkeypatch.setattr(app_module, "BASE", tmp_path)

    client = TestClient(app_module.app)
    d = client.get("/api/jarvis/status").json()

    assert "lane_monitor" in d
    lm = d["lane_monitor"]
    assert lm["read_only"] is True
    assert lm["display_only"] is True
    assert lm["no_execution"] is True
    assert lm["safety_level"] == "research_only"
    assert lm["lane_status"] == "WATCH"
    assert lm["evidence_level"] == "MIXED"
    assert lm["lane_label"] == "WATCH / MIXED"
    assert lm["readiness_status"] == "NOT_READY_FOR_REAL_DATA"
    # all four authorization flags hard-false at the route boundary
    assert lm["trading_authorization"] is False
    assert lm["paper_or_live_authorized"] is False
    assert lm["bundle_23_started"] is False
    assert lm["active_strong_promoted"] is False


def test_route_status_clamps_forbidden_verdicts(monkeypatch, tmp_path):
    import app as app_module
    from fastapi.testclient import TestClient
    for forbidden in ("ACTIVE", "STRONG", "PASS"):
        _seed_lane_sources(tmp_path)
        _seed_plan(tmp_path)
        _seed_result(tmp_path, verdict=forbidden, run_id="deadbeefdeadbeef")
        monkeypatch.setattr(app_module, "BASE", tmp_path)

        client = TestClient(app_module.app)
        lm = client.get("/api/jarvis/status").json()["lane_monitor"]

        cp = lm["latest_checkpoint"]
        assert cp["verdict"] == "WATCH", forbidden
        assert cp["verdict"] != forbidden
        assert lm["lane_status"] not in ("ACTIVE", "STRONG", "PASS")
        assert lm["active_strong_promoted"] is False
        assert any(forbidden in w and "clamped" in w for w in lm["warnings"])
