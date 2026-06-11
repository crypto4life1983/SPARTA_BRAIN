"""Tests for the Arbitrage Factory V1 JARVIS/dashboard scan report wiring.

Display-only: no run, no fetch, no send, no buttons, gates locked."""

from __future__ import annotations

import ast

import sparta_commander.arbitrage_jarvis_dashboard_scan_report_wiring_contract as wj
from sparta_commander.arbitrage_alert_report_schema_contract import MANDATORY_DISCLAIMER


def _report(verdicts=("FAIL", "FAIL")):
    return {
        "verdict": "ARBITRAGE_SCAN_COMPLETED_REPORT_READY",
        "run_timestamp_utc": "2026-06-11T17:09:21Z",
        "report_written": True,
        "alerts": [
            {"verdict": v, "family_id": "ARB_F1_spot_perp_funding_basis",
             "gross_edge_bps": 0.27, "net_edge_bps": -83.7,
             "summary": "funding carry candidate; net edge after full costs"}
            for v in verdicts
        ],
    }


def test_fail_fail_report_yields_honest_jarvis_answer():
    m = wj.build_scan_report_display(_report())
    assert m["verdict"] == wj.VERDICT_DISPLAY_READY
    ans = m["jarvis_answer"]
    assert "While you were sleeping" in ans
    assert "no candidate survived the full cost stack" in ans
    assert "PASS 0 / WATCH 0 / FAIL 2" in ans
    assert "No trade was placed" in ans
    assert "not a trade signal" in ans
    assert m["dashboard_display"]["pass_watch_fail_counts"] == {
        "PASS": 0, "WATCH": 0, "FAIL": 2}


def test_pass_report_summarized_without_hype():
    m = wj.build_scan_report_display(_report(("PASS", "WATCH", "FAIL")))
    assert m["verdict"] == wj.VERDICT_DISPLAY_READY
    assert "1 PASS and 1 WATCH" in m["jarvis_answer"]
    assert "await your review" in m["jarvis_answer"]
    assert wj._screen(m["jarvis_answer"]) is None


def test_display_has_metadata_and_no_buttons():
    m = wj.build_scan_report_display(_report())
    d = m["dashboard_display"]
    assert d["latest_report_timestamp_utc"] == "2026-06-11T17:09:21Z"
    assert d["report_was_persisted"] is True
    assert d["scanner_run_was_human_approved"] is True
    assert d["no_trade_was_placed"] is True
    assert d["human_action_needed"] is True
    assert d["disclaimer"] == MANDATORY_DISCLAIMER
    assert d["action_buttons"] == []


def test_unsafe_language_refused():
    bad = _report()
    bad["alerts"][0]["summary"] = "buy this winning setup"
    m = wj.build_scan_report_display(bad)
    assert m["verdict"] == wj.VERDICT_DISPLAY_REFUSED
    assert any("forbidden_display_language" in b for b in m["blockers"])
    assert m["dashboard_display"] is None and m["jarvis_answer"] is None
    bad2 = _report()
    bad2["alerts"][0]["summary"] = "clearly profitable opportunity"
    m2 = wj.build_scan_report_display(bad2)
    assert m2["verdict"] == wj.VERDICT_DISPLAY_REFUSED
    ok = _report()
    ok["alerts"][0]["summary"] = "profitable in gross terms [evidence: scan json]"
    assert wj.build_scan_report_display(ok)["verdict"] == wj.VERDICT_DISPLAY_READY


def test_missing_or_bad_report_refused():
    assert wj.build_scan_report_display(None)["verdict"] == wj.VERDICT_DISPLAY_REFUSED
    bad = _report()
    bad["verdict"] = "SOMETHING_ELSE"
    assert wj.build_scan_report_display(bad)["verdict"] == wj.VERDICT_DISPLAY_REFUSED
    bad2 = _report(("BUY",))
    m = wj.build_scan_report_display(bad2)
    assert m["verdict"] == wj.VERDICT_DISPLAY_REFUSED
    assert "alert_verdict_outside_closed_set" in m["blockers"]


def test_inert_on_all_paths_and_validates():
    for m in (wj.build_scan_report_display(_report()),
              wj.build_scan_report_display(None)):
        assert wj.validate_scan_report_display(m)["valid"] is True
        for key in ("executes", "runs_scanner", "fetches_data", "uses_network",
                    "uses_credentials", "contains_order_logic",
                    "sends_notifications", "starts_scheduler", "promotes_gate",
                    "unlocks_downstream_gate"):
            assert m[key] is False, key
        assert m["paper_trading_gate_locked"] is True
        assert m["micro_live_gate_locked"] is True
        assert m["live_gate_locked"] is True
        assert m["no_trade_was_placed"] is True


def test_validator_rejects_tampering():
    m = wj.build_scan_report_display(_report())
    m["dashboard_display"]["action_buttons"] = [{"label": "Run"}]
    assert wj.validate_scan_report_display(m)["valid"] is False
    m2 = wj.build_scan_report_display(_report())
    m2["jarvis_answer"] = "guaranteed winning trade tonight"
    v2 = wj.validate_scan_report_display(m2)
    assert v2["valid"] is False
    m3 = wj.build_scan_report_display(_report())
    m3["no_trade_was_placed"] = False
    assert wj.validate_scan_report_display(m3)["valid"] is False


def test_load_latest_scan_report_reads_real_evidence():
    r = wj.load_latest_scan_report(".")
    assert r is not None
    assert r["verdict"] == "ARBITRAGE_SCAN_COMPLETED_REPORT_READY"
    assert wj.load_latest_scan_report("/nonexistent_root_xyz") is None


def test_action_and_imports_clean():
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE", "EXECUTION",
                   "BACKTEST", "BASELINE", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in wj.NEXT_REQUIRED_ACTION.upper(), banned
    tree = ast.parse(open(wj.__file__, encoding="utf-8").read())
    banned_mods = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
                   "subprocess", "websockets", "aiohttp", "schedule",
                   "apscheduler", "threading", "asyncio", "time", "telegram",
                   "email", "fastapi", "flask"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods)
