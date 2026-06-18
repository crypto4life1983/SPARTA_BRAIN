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

import sparta_commander.crypto_d1_candidate_research_lane_status_v1_contract as _lane
import sparta_commander.automation_readiness_bundle_integration_v1_contract as _ari
import sparta_commander.automation_readiness_next_strategy_research_memo_v1_contract as _memo

REPO_ROOT = Path(__file__).resolve().parent
LATEST_JSON_REL = "reports/autopilot_morning/latest.json"
LATEST_MD_REL = "reports/autopilot_morning/latest.md"

PANEL_TITLE = "AUTOPILOT MORNING REPORT"
NO_REPORT_MESSAGE = "No morning report generated yet."
NEXT_CANDIDATE_DRIFT_TOKEN = "BUILD_NEXT_CANDIDATE_FAMILY_PROPOSAL"


def automation_readiness_block() -> dict[str, Any]:
    """Pure, READ-ONLY. The authoritative candidate-research-lane / automation-
    readiness truth, computed from the committed lane-status + bundle integration
    contracts -- INDEPENDENT of the (possibly stale) latest.json candidate_status
    and independent of git state, so a dirty tree or a missing report can never
    hide C16 / ledger-21 / automation-readiness status. Never raises."""
    try:
        lane = _lane.get_lane_status()
        integ = _ari.build_automation_readiness_integration()
        sf = lane.get("safety_flags") or {}
        return {
            "available": True,
            "c16_lifecycle_complete": lane.get("c16_lifecycle_complete"),
            "rejected_ledger_count": lane.get("rejected_ledger_count"),
            "next_required_action": lane.get("next_required_action"),
            "run_record_next_human_gate": integ.get("next_required_action"),
            "surfaces_agree": integ.get("surfaces_agree"),
            "section13_recommendation_when_clean":
                (integ.get("surfaces") or {}).get(
                    "coordinator_recommendation_kind"),
            "section14_present": True,
            "next_is_new_candidate": integ.get("next_is_new_candidate"),
            "candidate_lane": lane.get("candidate_lane") or [],
            "safety_locks": {
                "real_data_qa": lane.get("real_data_qa_state"),
                "replay": lane.get("replay_state"),
                "paper_trading": lane.get("paper_trading_state"),
                "micro_live": ("LOCKED" if sf.get("micro_live_locked")
                               else "UNLOCKED"),
                "live_trading": lane.get("live_trading_state"),
            },
        }
    except Exception:  # noqa: BLE001 — view must never crash the console
        return {"available": False, "c16_lifecycle_complete": None,
                "rejected_ledger_count": None, "next_required_action": None,
                "section14_present": False, "candidate_lane": [],
                "safety_locks": {}}


def next_strategy_memo_block() -> dict[str, Any]:
    """Pure, READ-ONLY. Compact display block from the committed next-strategy
    research memo contract. Creates no candidate; executes nothing. Never raises."""
    try:
        m = _memo.build_next_strategy_research_memo()
        return {
            "available": True,
            "recommended_direction": (m.get("recommended_direction") or {}).get(
                "name"),
            "recommended_direction_key": m.get("recommended_direction_key"),
            "ranked_directions": [d.get("name")
                                  for d in m.get("next_research_directions") or []],
            "why_recommended_is_different": m.get("why_recommended_is_different"),
            "creates_candidate_id": m.get("creates_candidate_id"),
            "human_approval_before_candidate":
                m.get("human_approval_before_candidate"),
            "next_required_action": m.get("next_required_action"),
        }
    except Exception:  # noqa: BLE001 — view must never crash the console
        return {"available": False}


def _drift_warning(report) -> bool:
    """True if the next-candidate drift token leaks into the report's plan or
    what-to-do-next (it must not, post-C16)."""
    if not isinstance(report, dict):
        return False
    ap = report.get("autopilot_plan") or {}
    hay = " ".join(str(x) for x in (
        ap.get("next_safe_action"), ap.get("recommended_token"),
        ap.get("decision"), report.get("what_to_do_next")))
    return NEXT_CANDIDATE_DRIFT_TOKEN in hay


def _seed_brief_path(report):
    if not isinstance(report, dict):
        return None
    for f in report.get("files_created_or_changed") or []:
        if "seed_brief_draft" in str(f):
            return str(f)
    return None

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
            "automation_readiness": automation_readiness_block(),
            "next_strategy_memo": next_strategy_memo_block(),
            "drift_warning": False,
            "git_dirty_warning": False,
            "run_id": None,
            "latest_run_record_id": None,
            "seed_brief_path": None,
            "full_report_path": LATEST_MD_REL,
            "no_paper_live_readiness_claim": True,
        }
        panel["safety_locks"] = panel["automation_readiness"].get(
            "safety_locks", {})
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
        "automation_readiness": automation_readiness_block(),
        "next_strategy_memo": next_strategy_memo_block(),
        "drift_warning": _drift_warning(report),
        "git_dirty_warning": (report.get("git_status_summary") or {}).get(
            "clean") is False,
        "run_id": report.get("run_id"),
        "latest_run_record_id": report.get("run_id"),
        "seed_brief_path": _seed_brief_path(report),
        "full_report_path": LATEST_MD_REL,
        "no_paper_live_readiness_claim": True,
    }
    panel["safety_locks"] = panel["automation_readiness"].get("safety_locks", {})
    panel["html"] = render_autopilot_morning_html(panel)
    return panel


def _esc(x) -> str:
    return _html.escape("" if x is None else str(x))


def _li(items) -> str:
    if not items:
        return '<div class="jv-detail">(none)</div>'
    return ('<ul class="jv-am-list">'
            + "".join("<li>%s</li>" % _esc(i) for i in items) + "</ul>")


def _render_automation_readiness_html(panel: dict) -> str:
    """Pure. The authoritative C16 / ledger-21 / automation-readiness / safety-lock
    block. Rendered in BOTH the report-present and no-report paths, and unaffected
    by a dirty tree, so this status is never hidden."""
    ar = panel.get("automation_readiness") or {}
    locks = panel.get("safety_locks") or ar.get("safety_locks") or {}
    parts = []
    if panel.get("git_dirty_warning"):
        parts.append('<div class="jv-am-h jv-am-bad">⚠ Git tracked tree DIRTY</div>'
                     '<div class="jv-detail">Commit/clean before any auto-advance. '
                     'Automation-readiness status below is unaffected.</div>')
    if panel.get("drift_warning"):
        parts.append('<div class="jv-am-h jv-am-bad">⚠ NEXT-CANDIDATE DRIFT</div>'
                     '<div class="jv-detail">A surface shows <code>%s</code> — '
                     'expected automation readiness.</div>'
                     % _esc(NEXT_CANDIDATE_DRIFT_TOKEN))
    parts.append('<div class="jv-am-h">Candidate research lane — '
                 'AUTOMATION READINESS</div>')
    parts.append('<div class="jv-detail">C16 lifecycle complete: <b>%s</b> · '
                 'rejected ledger: <b>%s</b> families</div>'
                 % (_esc(ar.get("c16_lifecycle_complete")),
                    _esc(ar.get("rejected_ledger_count"))))
    parts.append('<div class="jv-detail">Next required action: <code>%s</code></div>'
                 % _esc(ar.get("next_required_action")))
    parts.append('<div class="jv-detail">§13 (clean tree) recommends: <b>%s</b> · '
                 '§14 present: %s · surfaces agree: %s · recommends new candidate: '
                 '%s</div>'
                 % (_esc(ar.get("section13_recommendation_when_clean")),
                    _esc(ar.get("section14_present")),
                    _esc(ar.get("surfaces_agree")),
                    _esc(ar.get("next_is_new_candidate"))))
    lane = ar.get("candidate_lane") or []
    if lane:
        rows = "".join(
            "<li><b>%s</b> (%s): %s — rejected at %s</li>"
            % (_esc(c.get("candidate")), _esc(c.get("family")),
               _esc(c.get("state")), _esc(c.get("rejected_at"))) for c in lane)
        parts.append('<div class="jv-am-h">Candidate lane</div>'
                     '<ul class="jv-am-list">%s</ul>' % rows)
    parts.append('<div class="jv-am-h">Safety locks</div>')
    parts.append('<div class="jv-detail">real-data-QA <b>%s</b> · replay <b>%s</b> '
                 '· paper <b>%s</b> · micro-live <b>%s</b> · live <b>%s</b></div>'
                 % (_esc(locks.get("real_data_qa")), _esc(locks.get("replay")),
                    _esc(locks.get("paper_trading")), _esc(locks.get("micro_live")),
                    _esc(locks.get("live_trading"))))
    # next-strategy research memo (research-only; creates NO candidate)
    nm = panel.get("next_strategy_memo") or {}
    if nm.get("available"):
        parts.append('<div class="jv-am-h">Next-strategy research memo '
                     '(research-only · no candidate)</div>')
        parts.append('<div class="jv-detail">Recommended next direction: '
                     '<b>%s</b> (<code>%s</code>)</div>'
                     % (_esc(nm.get("recommended_direction")),
                        _esc(nm.get("recommended_direction_key"))))
        ranked = nm.get("ranked_directions") or []
        if ranked:
            rows = "".join("<li>%s</li>" % _esc(d) for d in ranked)
            parts.append('<div class="jv-detail">Ranked directions:</div>'
                         '<ul class="jv-am-list">%s</ul>' % rows)
        if nm.get("why_recommended_is_different"):
            parts.append('<div class="jv-detail">Why it avoids C1–C16 failure '
                         'modes: %s</div>'
                         % _esc(nm.get("why_recommended_is_different")))
        parts.append('<div class="jv-detail">Creates a candidate yet: <b>%s</b> '
                     '(no C17)</div>' % _esc(nm.get("creates_candidate_id")))
        parts.append('<div class="jv-am-paste">Before any candidate → human gate: '
                     '<code>%s</code></div>'
                     % _esc(nm.get("human_approval_before_candidate")))
    return "".join(parts)


def render_autopilot_morning_html(panel: dict) -> str:
    """Pure. Server-rendered HTML fragment for the JARVIS panel body. No JS, no
    inline event handlers, no execution affordances. Never claims paper/live
    readiness."""
    status = panel.get("run_status") or "NO_REPORT"
    klass = _STATUS_CLASS.get(status, "muted")

    if not panel.get("available"):
        head = ('<div class="jv-am" data-run-status="NO_REPORT">'
                '<div class="jv-am-status jv-am-muted">%s</div>'
                '<div class="jv-detail">%s</div>'
                % (_esc(status), _esc(NO_REPORT_MESSAGE)))
        # automation-readiness status is shown even with no report
        body = _render_automation_readiness_html(panel)
        foot = ('<div class="jv-am-foot">Research-only status surface. '
                'No paper/live-readiness claim.</div>'
                '<div class="jv-detail">Full report: %s</div></div>'
                % _esc(panel.get("full_report_path")))
        return head + body + foot

    parts = ['<div class="jv-am" data-run-status="%s">' % _esc(status)]
    # 1. run status  +  2. last run time  +  run id / seed brief (run metadata)
    parts.append('<div class="jv-am-status jv-am-%s">Run: %s</div>'
                 % (klass, _esc(status)))
    parts.append('<div class="jv-detail">Last run: %s · run id: %s</div>'
                 % (_esc(panel.get("last_run_time") or "—"),
                    _esc(panel.get("latest_run_record_id") or "—")))
    if panel.get("seed_brief_path"):
        parts.append('<div class="jv-detail">Latest seed brief: %s</div>'
                     % _esc(panel.get("seed_brief_path")))
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
    # 12. Candidate research lane — AUTOMATION READINESS (authoritative; from the
    #     committed lane-status + integration contracts, not the stale source)
    parts.append(_render_automation_readiness_html(panel))
    # 13. path to full report
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
