"""JARVIS Autopilot Morning Report panel (READ-ONLY view layer).

Renders the overnight-autopilot morning report (produced by
tools/sparta_autopilot_morning_report.py at reports/autopilot_morning/
latest.json) for display inside the JARVIS console, so the operator never has
to open latest.md by hand.

This is a pure, read-only view module: it READS the already-generated
latest.json and returns a panel dict (+ a server-rendered HTML fragment). It
has NO trading, paper, live, broker, exchange, order, credential, network,
detector, replay, or portfolio-compute capability, and NEVER claims paper/live
readiness. It runs nothing and writes nothing.

Behavior:
  * latest.json missing  -> panel state NO_REPORT ("No morning report generated
    yet.").
  * latest.json present  -> surfaces run status, last run time, tasks, errors,
    candidate status (incl. C10 closed/rejected and any open C11 gate), the
    exact paste-text for the next human decision, the git summary, and the path
    to the full latest.md.
"""
from __future__ import annotations

import html as _html
import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent
LATEST_JSON_REL = "reports/autopilot_morning/latest.json"
LATEST_MD_REL = "reports/autopilot_morning/latest.md"

PANEL_TITLE = "AUTOPILOT MORNING REPORT"
NO_REPORT_MESSAGE = "No morning report generated yet."

_STATUS_CLASS = {
    "SUCCESS": "ok", "PARTIAL": "warn", "FAILED": "bad",
    "DID_NOT_RUN": "muted", "NO_REPORT": "muted",
}


def load_latest_report(repo_root: Any = REPO_ROOT):
    """Read reports/autopilot_morning/latest.json. Returns the report dict, or
    None if the file is absent / unreadable. Never raises."""
    p = Path(repo_root) / LATEST_JSON_REL
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001 — view must never crash the console
        return None


def build_autopilot_morning_panel(report) -> dict[str, Any]:
    """Pure. Normalize the morning report (or None) into a JARVIS panel dict.
    Always returns a dict; never claims paper/live readiness."""
    if not isinstance(report, dict):
        panel = {
            "available": False,
            "panel_title": PANEL_TITLE,
            "run_status": "NO_REPORT",
            "headline": NO_REPORT_MESSAGE,
            "last_run_time": None,
            "tasks_attempted": [], "tasks_completed": [], "tasks_failed": [],
            "error_summary": [],
            "candidate_status": {},
            "c10_status_line": None,
            "next_human_gate": {"action": "NONE",
                                "approval_text_to_paste": None,
                                "reject_text_to_paste": None,
                                "candidate": None},
            "git_status_summary": None,
            "ahead_behind": None,
            "autopilot_plan": {},
            "full_report_path": LATEST_MD_REL,
            "no_paper_live_readiness_claim": True,
        }
        panel["html"] = render_autopilot_morning_html(panel)
        return panel

    cstat = report.get("candidate_status") or {}
    c10 = cstat.get("C10") or {}
    c10_line = None
    if c10:
        c10_line = "%s: %s (active=%s)" % (
            c10.get("family", "C10"), c10.get("status", "?"),
            c10.get("active"))
    gate = report.get("next_required_human_gate") or {}
    panel = {
        "available": True,
        "panel_title": PANEL_TITLE,
        "run_status": report.get("run_status") or "DID_NOT_RUN",
        "headline": report.get("what_to_do_next") or "",
        "last_run_time": report.get("last_run_time"),
        "run_id": report.get("run_id"),
        "tasks_attempted": list(report.get("tasks_attempted") or []),
        "tasks_completed": list(report.get("tasks_completed") or []),
        "tasks_failed": list(report.get("tasks_failed") or []),
        "error_summary": list(report.get("error_summary") or []),
        "candidate_status": cstat,
        "c10_status_line": c10_line,
        "next_human_gate": {
            "candidate": gate.get("candidate"),
            "action": gate.get("action") or "NONE",
            "approval_text_to_paste": gate.get("approval_text_to_paste"),
            "reject_text_to_paste": gate.get("reject_text_to_paste"),
        },
        "git_status_summary": report.get("git_status_summary"),
        "ahead_behind": report.get("ahead_behind"),
        "autopilot_plan": report.get("autopilot_plan") or {},
        "full_report_path": LATEST_MD_REL,
        "no_paper_live_readiness_claim": True,
    }
    panel["html"] = render_autopilot_morning_html(panel)
    return panel


def _esc(x) -> str:
    return _html.escape("" if x is None else str(x))


def _li(items) -> str:
    if not items:
        return '<div class="jv-detail">(none)</div>'
    return ('<ul class="jv-am-list">'
            + "".join("<li>%s</li>" % _esc(i) for i in items) + "</ul>")


def render_autopilot_morning_html(panel: dict) -> str:
    """Pure. Server-rendered HTML fragment for the JARVIS panel body. No JS, no
    inline event handlers, no execution affordances. Never claims paper/live
    readiness."""
    status = panel.get("run_status") or "NO_REPORT"
    klass = _STATUS_CLASS.get(status, "muted")

    if not panel.get("available"):
        return (
            '<div class="jv-am" data-run-status="NO_REPORT">'
            '<div class="jv-am-status jv-am-muted">%s</div>'
            '<div class="jv-detail">%s</div>'
            '<div class="jv-am-foot">Research-only status surface. '
            'No paper/live-readiness claim.</div>'
            '<div class="jv-detail">Full report: %s</div>'
            "</div>" % (_esc(status), _esc(NO_REPORT_MESSAGE),
                        _esc(panel.get("full_report_path"))))

    parts = ['<div class="jv-am" data-run-status="%s">' % _esc(status)]
    # 1. run status  +  2. last run time
    parts.append('<div class="jv-am-status jv-am-%s">Run: %s</div>'
                 % (klass, _esc(status)))
    parts.append('<div class="jv-detail">Last run: %s</div>'
                 % _esc(panel.get("last_run_time") or "—"))
    # 3. tasks attempted / completed
    parts.append('<div class="jv-am-h">Tasks attempted</div>'
                 + _li(panel.get("tasks_attempted")))
    parts.append('<div class="jv-am-h">Tasks completed</div>'
                 + _li(panel.get("tasks_completed")))
    if panel.get("tasks_failed"):
        parts.append('<div class="jv-am-h jv-am-bad">Tasks FAILED</div>'
                     + _li(panel.get("tasks_failed")))
    # 4. error summary
    parts.append('<div class="jv-am-h">Error summary</div>'
                 + _li(panel.get("error_summary")))
    # 5. candidate status  (incl. 6. C10 closed/rejected)
    parts.append('<div class="jv-am-h">Candidate status</div>')
    cstat = panel.get("candidate_status") or {}
    if cstat:
        rows = []
        for key in sorted(cstat.keys()):
            c = cstat[key]
            rows.append("<li><b>%s</b> (%s): %s — next: %s</li>"
                        % (_esc(key), _esc(c.get("family")),
                           _esc(c.get("status")), _esc(c.get("next_action"))))
        parts.append('<ul class="jv-am-list">' + "".join(rows) + "</ul>")
    else:
        parts.append('<div class="jv-detail">(none)</div>')
    # 7. open human gate (incl C11)  +  8. exact paste-text
    gate = panel.get("next_human_gate") or {}
    if gate.get("action") and not str(gate["action"]).startswith("NONE"):
        parts.append('<div class="jv-am-h jv-am-gate">Next human decision</div>')
        parts.append('<div class="jv-detail">%s on %s</div>'
                     % (_esc(gate.get("action")), _esc(gate.get("candidate"))))
        if gate.get("approval_text_to_paste"):
            parts.append('<div class="jv-am-paste">Advance → paste: '
                         '<code>%s</code></div>'
                         % _esc(gate.get("approval_text_to_paste")))
        if gate.get("reject_text_to_paste"):
            parts.append('<div class="jv-am-paste">Reject → paste: '
                         '<code>%s</code></div>'
                         % _esc(gate.get("reject_text_to_paste")))
    else:
        parts.append('<div class="jv-am-h">Next human decision</div>'
                     '<div class="jv-detail">None open.</div>')
    # 9. git status summary
    gs = panel.get("git_status_summary") or {}
    ab = panel.get("ahead_behind") or {}
    parts.append('<div class="jv-am-h">Git</div>')
    parts.append('<div class="jv-detail">branch %s · staged %s · '
                 'modified %s · untracked %s · ahead %s · behind %s</div>'
                 % (_esc(gs.get("branch")), _esc(gs.get("staged")),
                    _esc(gs.get("modified")), _esc(gs.get("untracked")),
                    _esc(ab.get("ahead")), _esc(ab.get("behind"))))
    # 11. Safe Research Autopilot recommendation (planner-only, read-only)
    ap = panel.get("autopilot_plan") or {}
    if ap:
        parts.append('<div class="jv-am-h">Safe Research Autopilot '
                     '(planner-only)</div>')
        parts.append('<div class="jv-detail">Recommends: <b>%s</b></div>'
                     % _esc(ap.get("next_safe_action")))
        parts.append('<div class="jv-detail">%s</div>' % _esc(ap.get("reason")))
        if ap.get("stopped_before"):
            parts.append('<div class="jv-detail jv-am-gate">Hard-stops before: '
                         '%s</div>' % _esc(ap.get("stopped_before")))
        if ap.get("recommended_token"):
            parts.append('<div class="jv-am-paste">Next → paste: '
                         '<code>%s</code></div>'
                         % _esc(ap.get("recommended_token")))
        parts.append('<div class="jv-detail">planner read-only · executes '
                     'nothing</div>')
    # 12. path to full report
    parts.append('<div class="jv-detail">Full report: %s</div>'
                 % _esc(panel.get("full_report_path")))
    parts.append('<div class="jv-am-foot">Research-only status surface. '
                 'No paper/live-readiness claim.</div>')
    parts.append("</div>")
    return "".join(parts)


def get_autopilot_morning_panel(repo_root: Any = REPO_ROOT) -> dict[str, Any]:
    """Convenience: load + build in one read-only call (used by the JARVIS
    status feed and the standalone route)."""
    return build_autopilot_morning_panel(load_latest_report(repo_root))
