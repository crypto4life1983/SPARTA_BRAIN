"""SPARTA Arbitrage Factory V1 - JARVIS/DASHBOARD SCAN REPORT WIRING (READ-ONLY).

Display-only wiring: turns a persisted scan report into a dashboard panel and
a JARVIS answer to "what did you find while I was sleeping?" -- TEXT ONLY.
No button, no action, no send, no run, no fetch. Reading the newest report
json under reports/arbitrage_factory_v1/ is the only I/O, and it is read-only.

Forbidden display language (refuses the whole display): buy, sell, long,
short, guaranteed, winning, and 'profitable' without an [evidence: ...] label.
Every display carries the mandatory disclaimer, a 'no trade was placed'
statement, and human_action_needed=True.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sparta_commander.arbitrage_alert_report_schema_contract import (
    MANDATORY_DISCLAIMER,
    REPORTS_ROOT,
)

WIRING_SCHEMA_VERSION = "arbitrage_jarvis_dashboard_scan_report_wiring.v1"
WIRING_LABEL = (
    "SPARTA Arbitrage Factory V1 JARVIS/Dashboard Scan Report Wiring "
    "(READ-ONLY, DISPLAY ONLY)"
)
WIRING_MODE = "RESEARCH_ONLY"

VERDICT_DISPLAY_READY = "ARBITRAGE_SCAN_DISPLAY_READY"
VERDICT_DISPLAY_REFUSED = "ARBITRAGE_SCAN_DISPLAY_REFUSED"
NEXT_REQUIRED_ACTION = "HUMAN_REVIEW_OF_SCAN_DISPLAY"

FORBIDDEN_DISPLAY_WORDS = ("buy", "sell", "long", "short", "guaranteed", "winning")
EVIDENCE_MARKER = "[evidence:"


def _screen(*texts: Any) -> str | None:
    joined = " ".join(str(t) for t in texts if t is not None).lower()
    words = joined.replace(",", " ").replace(".", " ").split()
    for bad in FORBIDDEN_DISPLAY_WORDS:
        if bad in words:
            return bad
    if "profitable" in joined and EVIDENCE_MARKER not in joined:
        return "profitable_without_evidence_label"
    return None


def load_latest_scan_report(repo_root: Any = ".") -> dict[str, Any] | None:
    """Read-only: load the newest persisted scan report json, else None."""
    out_dir = Path(repo_root) / REPORTS_ROOT
    files = sorted(out_dir.glob("arbitrage_scan_*.json")) if out_dir.is_dir() else []
    if not files:
        return None
    return json.loads(files[-1].read_text(encoding="utf-8"))


def build_scan_report_display(scan_report: Any) -> dict[str, Any]:
    """Turn ONE persisted scan report into a display-only model. PURE beyond
    its input; never raises, never sends, never runs anything."""
    model: dict[str, Any] = {
        "schema_version": WIRING_SCHEMA_VERSION, "label": WIRING_LABEL,
        "mode": WIRING_MODE, "lane": "arbitrage_factory_v1",
        "verdict": None, "blockers": [],
        "dashboard_display": None, "jarvis_answer": None,
        "display_only_no_controls": True, "no_button_can_execute": True,
        "nothing_sent": True, "no_trade_was_placed": True,
        "human_action_needed": True, "disclaimer": MANDATORY_DISCLAIMER,
        "executes": False, "runs_scanner": False, "fetches_data": False,
        "uses_network": False, "uses_credentials": False,
        "contains_order_logic": False, "sends_notifications": False,
        "starts_scheduler": False, "promotes_gate": False,
        "unlocks_downstream_gate": False,
        "paper_trading_gate_locked": True, "micro_live_gate_locked": True,
        "live_gate_locked": True,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    if not isinstance(scan_report, dict):
        model["verdict"] = VERDICT_DISPLAY_REFUSED
        model["blockers"].append("no_persisted_scan_report_found")
        return model
    alerts = scan_report.get("alerts") or []
    if scan_report.get("verdict") != "ARBITRAGE_SCAN_COMPLETED_REPORT_READY":
        model["verdict"] = VERDICT_DISPLAY_REFUSED
        model["blockers"].append("report_not_a_completed_scan")
        return model

    counts = {"PASS": 0, "WATCH": 0, "FAIL": 0}
    lines = []
    for a in alerts:
        verdict = a.get("verdict")
        if verdict not in counts:
            model["verdict"] = VERDICT_DISPLAY_REFUSED
            model["blockers"].append("alert_verdict_outside_closed_set")
            return model
        counts[verdict] += 1
        lines.append(f"[{verdict}] {a.get('family_id')}: gross "
                     f"{a.get('gross_edge_bps')} bps -> net "
                     f"{a.get('net_edge_bps')} bps after all costs")
        token = _screen(a.get("summary"))
        if token:
            model["verdict"] = VERDICT_DISPLAY_REFUSED
            model["blockers"].append("forbidden_display_language:" + token)
            return model

    ts = scan_report.get("run_timestamp_utc")
    if counts["PASS"] or counts["WATCH"]:
        finding = (f"{counts['PASS']} PASS and {counts['WATCH']} WATCH research "
                   "candidates survived the full cost stack and await your review")
    else:
        finding = ("no candidate survived the full cost stack -- every gross "
                   "edge died under fees, spread, slippage, funding and "
                   "withdrawal costs")
    jarvis_answer = (
        f"While you were sleeping, I ran one approved arbitrage research scan "
        f"at {ts}. Honest answer: {finding}. "
        f"PASS {counts['PASS']} / WATCH {counts['WATCH']} / FAIL {counts['FAIL']}. "
        "No trade was placed, nothing is scheduled, and all trading gates "
        "remain locked. This is research only, not a trade signal; the next "
        "step, if any, is yours."
    )
    token = _screen(jarvis_answer, *lines)
    if token:
        model["verdict"] = VERDICT_DISPLAY_REFUSED
        model["blockers"].append("forbidden_display_language:" + token)
        return model

    model["verdict"] = VERDICT_DISPLAY_READY
    model["jarvis_answer"] = jarvis_answer
    model["dashboard_display"] = {
        "panel_title": "Arbitrage Factory V1 - Latest Research Scan",
        "latest_report_timestamp_utc": ts,
        "report_was_persisted": bool(scan_report.get("report_written")),
        "scanner_run_was_human_approved": True,
        "pass_watch_fail_counts": counts,
        "alert_lines": lines,
        "no_trade_was_placed": True,
        "human_action_needed": True,
        "disclaimer": MANDATORY_DISCLAIMER,
        "display_only": True, "action_buttons": [],
    }
    return model


def validate_scan_report_display(model: Any) -> dict[str, Any]:
    """Validate display safety invariants. Never raises."""
    errors: list[str] = []
    if not isinstance(model, dict):
        return {"valid": False, "errors": ["model_not_a_dict"]}
    m = model
    if m.get("verdict") not in (VERDICT_DISPLAY_READY, VERDICT_DISPLAY_REFUSED):
        errors.append("bad_verdict")
    if m.get("verdict") == VERDICT_DISPLAY_REFUSED:
        if not m.get("blockers"):
            errors.append("refused_without_blockers")
        if m.get("dashboard_display") is not None or m.get("jarvis_answer"):
            errors.append("refused_carries_display")
    if m.get("verdict") == VERDICT_DISPLAY_READY:
        dash = m.get("dashboard_display") or {}
        if dash.get("action_buttons"):
            errors.append("display_carries_action_buttons")
        if dash.get("disclaimer") != MANDATORY_DISCLAIMER:
            errors.append("disclaimer_missing")
        if "not a trade signal" not in str(m.get("jarvis_answer")):
            errors.append("jarvis_answer_missing_no_signal_line")
        if "No trade was placed" not in str(m.get("jarvis_answer")):
            errors.append("jarvis_answer_missing_no_trade_line")
        if _screen(m.get("jarvis_answer")) is not None:
            errors.append("forbidden_language_in_answer")
    for key in ("display_only_no_controls", "no_button_can_execute",
                "nothing_sent", "no_trade_was_placed", "human_action_needed",
                "paper_trading_gate_locked", "micro_live_gate_locked",
                "live_gate_locked"):
        if m.get(key) is not True:
            errors.append("flag_dropped:" + key)
    for key in ("executes", "runs_scanner", "fetches_data", "uses_network",
                "uses_credentials", "contains_order_logic",
                "sends_notifications", "starts_scheduler", "promotes_gate",
                "unlocks_downstream_gate"):
        if m.get(key) is not False:
            errors.append("capability_not_false:" + key)
    return {"valid": not errors, "errors": errors}
