"""SPARTA CONTROL PANEL renderer -- PURE, READ-ONLY, REPORTING ONLY.

Renders the Bundle A current-state control packet
(sparta_current_state_control_packet_contract) into a single read-only SPARTA Control Panel
(HTML + markdown). The current-state packet is the SINGLE SOURCE OF TRUTH: this renderer
recomputes NOTHING (no separate C22 progress, no separate task classification) -- it only
formats what the packet already provides.

It computes a clear status BADGE -- HEALTHY / NEEDS_ATTENTION / BLOCKED /
NOT_READY_COLLECTING -- and shows repo state (sync, clean, staged, dangerous-artifact
guard), lane state (C21 closed/ledger-26, C22 active HOLD replay-locked, progress, C23
on-deck), C22 collection (progress, missing-export warning, 20/20 readiness alert),
scheduled-task health, and the current next action with the SUGGESTED tokens (collect /
review-at-20 / open-C23-after-C22). Tokens are SUGGESTIONS ONLY and are never executed.

It performs NO I/O, modifies NOTHING, changes NO scheduled task, runs NO labels/replay,
fetches NO data, connects to NOTHING. Pure formatting only.
"""
from __future__ import annotations

from typing import Any

CPR_SCHEMA_VERSION = 1

BADGE_HEALTHY = "HEALTHY"
BADGE_NEEDS_ATTENTION = "NEEDS_ATTENTION"
BADGE_BLOCKED = "BLOCKED"
BADGE_NOT_READY_COLLECTING = "NOT_READY_COLLECTING"
ALL_BADGES = (BADGE_HEALTHY, BADGE_NEEDS_ATTENTION, BADGE_BLOCKED,
              BADGE_NOT_READY_COLLECTING)

_BADGE_CLASS = {
    BADGE_HEALTHY: "jv-am-ok", BADGE_NOT_READY_COLLECTING: "jv-am-warn",
    BADGE_NEEDS_ATTENTION: "jv-am-warn", BADGE_BLOCKED: "jv-am-bad",
}


def _esc(x: Any) -> str:
    return (str(x).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def compute_badge(packet: dict) -> str:
    """PURE. Derive the single status badge from the current-state packet. Precedence:
    BLOCKED (dangerous staged artifact OR a priority scheduled task FAILED/MISSING) >
    NEEDS_ATTENTION (any other attention reason) > NOT_READY_COLLECTING (C22 still < 20/20,
    otherwise clean) > HEALTHY."""
    p = packet or {}
    rs = p.get("repo_state") or {}
    th = p.get("task_health") or {}
    coll = p.get("c22_collection") or {}
    priority_broken = bool(th.get("priority_failed_or_missing"))
    if rs.get("dangerous_staged_artifact") is True or priority_broken:
        return BADGE_BLOCKED
    if p.get("overall_status") == "NEEDS_ATTENTION":
        return BADGE_NEEDS_ATTENTION
    if coll.get("ready_for_review") is not True:
        return BADGE_NOT_READY_COLLECTING
    return BADGE_HEALTHY


def render_control_panel_markdown(packet: dict) -> str:
    """PURE. The control panel as markdown (single source = the packet)."""
    p = packet or {}
    rs = p.get("repo_state") or {}
    lane = p.get("lane") or {}
    coll = p.get("c22_collection") or {}
    th = p.get("task_health") or {}
    na = p.get("next_action") or {}
    badge = compute_badge(p)
    lines = [
        "# SPARTA Control Panel (read-only)",
        "",
        "**Status: %s**" % badge,
    ]
    if p.get("attention_reasons"):
        lines.append("- Attention: %s" % ", ".join(p["attention_reasons"]))
    lines += [
        "",
        "## Repo",
        "- HEAD `%s` / origin `%s` | in sync: %s (ahead %s / behind %s)" % (
            rs.get("head"), rs.get("origin"), rs.get("in_sync"),
            rs.get("ahead"), rs.get("behind")),
        "- Tracked tree clean: %s | staged: %s | dangerous staged artifact: %s" % (
            rs.get("tracked_tree_clean"), rs.get("staged_count"),
            rs.get("dangerous_staged_artifact")),
        "",
        "## Lane",
        "- C21: closed/rejected (ledger %s)" % lane.get("rejected_ledger_count"),
        "- C22 active collection lane: **%s** (replay locked: %s)" % (
            lane.get("c22_state"), lane.get("c22_replay_locked")),
        "- C23: on-deck %s / active %s / proposal frozen %s" % (
            lane.get("c23_on_deck"), lane.get("c23_is_active"),
            lane.get("c23_proposal_frozen")),
        "",
        "## C22 collection",
        "- Progress: **%s** (%s more needed)" % (
            coll.get("progress"), coll.get("windows_remaining")),
        "- Latest window: %s" % (coll.get("latest_window_date") or "-"),
    ]
    if coll.get("missing_export_warning"):
        lines.append("- ⚠ MISSING EXPORT: %s" % coll.get("missing_export_detail"))
    if coll.get("readiness_alert"):
        lines.append("- ✅ READINESS: %s" % coll.get("readiness_alert"))
    lines += ["", "## Scheduled tasks (%s)" % th.get("overall_task_health", "?")]
    for t in (th.get("tasks") or []):
        lines.append("- %s: **%s**%s" % (
            t.get("name"), t.get("status"),
            " (priority)" if t.get("is_priority") else ""))
    lines += [
        "",
        "## Next action (suggestion only — never auto-executed)",
        "- ➤ %s" % na.get("authoritative_next_action"),
        "- At 20/20 suggest: `%s`" % na.get("review_token_when_ready"),
        "- C23 opens (after C22 concludes) via: `%s`" % na.get("c23_open_token_after_c22"),
    ]
    return "\n".join(lines)


def render_watchdog_section_html(watchdog: dict) -> str:
    """PURE. The Bundle C scheduled-run watchdog summary (read-only display of an existing
    watchdog finding -- recomputes nothing). Returns '' if no watchdog finding."""
    w = watchdog or {}
    if not w:
        return ""
    sev = w.get("severity")
    cls = {"ALERT": "jv-am-bad", "ATTENTION": "jv-am-warn", "NONE": "jv-am-ok"}.get(
        sev, "jv-am-muted")
    parts = ['<div class="jv-am-h %s">Scheduled-run watchdog: %s</div><ul>'
             % (cls, _esc(sev))]
    parts.append('<li>Primary recommendation: <b>%s</b></li>'
                 % _esc(w.get("primary_recommendation")))
    ps = w.get("priority_states") or {}
    parts.append('<li>Priority tasks: %s</li>' % _esc(
        ", ".join("%s=%s" % (k.split("_")[-1] if "_" in k else k, v)
                  for k, v in ps.items())))
    risks = [k for k, v in (w.get("c22_risks") or {}).items() if v is True]
    parts.append('<li>C22 risks: %s</li>' % _esc(", ".join(risks) or "none"))
    for chk in (w.get("operator_checks") or []):
        parts.append('<li class="jv-detail">check: %s</li>' % _esc(chk))
    parts.append('<li class="jv-detail">reran_any_task=%s | changed_any_scheduled_task=%s '
                 '| auto_executes_any_token=%s</li></ul>' % (
                     _esc(w.get("reran_any_task")),
                     _esc(w.get("changed_any_scheduled_task")),
                     _esc(w.get("auto_executes_any_token"))))
    return "".join(parts)


def render_lifecycle_section_html(lifecycle: dict) -> str:
    """PURE. The Bundle D candidate-lifecycle summary (read-only display of an existing
    lifecycle finding -- recomputes nothing). Returns '' if no lifecycle finding."""
    lo = lifecycle or {}
    if not lo:
        return ""
    st = lo.get("lifecycle_state") or {}
    parts = ['<div class="jv-am-h jv-am-gate">Candidate lifecycle</div><ul>']
    parts.append('<li>Current gate: <b>%s</b></li>' % _esc(lo.get("current_gate")))
    parts.append('<li>Suggested human token: <code>%s</code></li>'
                 % _esc(lo.get("suggested_human_token")))
    parts.append('<li>C22 progress / state: %s / %s</li>' % (
        _esc(st.get("c22_progress")), _esc(st.get("c22_state"))))
    parts.append('<li>C23 gate: %s</li>' % _esc(lo.get("c23_gate")))
    parts.append('<li class="jv-detail">advances_any_candidate=%s | opens_c23_as_active=%s '
                 '| auto_executes_any_token=%s | modifies_repo=%s</li></ul>' % (
                     _esc(lo.get("advances_any_candidate")),
                     _esc(lo.get("opens_c23_as_active")),
                     _esc(lo.get("auto_executes_any_token")),
                     _esc(lo.get("modifies_repo"))))
    return "".join(parts)


def render_control_panel_html(packet: dict, watchdog: dict = None,
                              lifecycle: dict = None) -> str:
    """PURE. The control panel as an HTML fragment (no JS, no execution affordances).
    Optionally appends the read-only Bundle C watchdog + Bundle D lifecycle summaries
    (display-only; recomputes nothing)."""
    p = packet or {}
    rs = p.get("repo_state") or {}
    lane = p.get("lane") or {}
    coll = p.get("c22_collection") or {}
    th = p.get("task_health") or {}
    na = p.get("next_action") or {}
    badge = compute_badge(p)
    parts = [
        '<div class="jv-am" data-badge="%s">' % _esc(badge),
        '<div class="jv-am-status %s">SPARTA STATUS: %s</div>' % (
            _BADGE_CLASS.get(badge, "jv-am-muted"), _esc(badge)),
    ]
    if p.get("attention_reasons"):
        parts.append('<div class="jv-detail jv-am-warn">Attention: %s</div>'
                     % _esc(", ".join(p["attention_reasons"])))
    # repo
    parts.append('<div class="jv-am-h">Repo</div><ul>')
    parts.append('<li>HEAD <code>%s</code> / origin <code>%s</code> | in sync: %s '
                 '(ahead %s / behind %s)</li>' % (
                     _esc(rs.get("head")), _esc(rs.get("origin")), _esc(rs.get("in_sync")),
                     _esc(rs.get("ahead")), _esc(rs.get("behind"))))
    parts.append('<li>tracked tree clean: %s | staged: %s | dangerous staged artifact: '
                 '<b>%s</b></li></ul>' % (
                     _esc(rs.get("tracked_tree_clean")), _esc(rs.get("staged_count")),
                     _esc(rs.get("dangerous_staged_artifact"))))
    # lane
    parts.append('<div class="jv-am-h">Lane</div><ul>')
    parts.append('<li>C21: closed/rejected (ledger %s)</li>'
                 % _esc(lane.get("rejected_ledger_count")))
    parts.append('<li>C22 active collection lane: <b>%s</b> (replay locked: %s)</li>' % (
        _esc(lane.get("c22_state")), _esc(lane.get("c22_replay_locked"))))
    parts.append('<li>C23: on-deck %s / active %s / proposal frozen %s</li></ul>' % (
        _esc(lane.get("c23_on_deck")), _esc(lane.get("c23_is_active")),
        _esc(lane.get("c23_proposal_frozen"))))
    # c22 collection
    parts.append('<div class="jv-am-h">C22 collection</div><ul>')
    parts.append('<li>Progress: <b>%s</b> (%s more needed) | latest window: %s</li>' % (
        _esc(coll.get("progress")), _esc(coll.get("windows_remaining")),
        _esc(coll.get("latest_window_date") or "-")))
    if coll.get("missing_export_warning"):
        parts.append('<li class="jv-am-bad">⚠ MISSING EXPORT: %s</li>'
                     % _esc(coll.get("missing_export_detail")))
    if coll.get("readiness_alert"):
        parts.append('<li class="jv-am-ok">✅ READINESS: %s</li>'
                     % _esc(coll.get("readiness_alert")))
    parts.append('</ul>')
    # tasks
    parts.append('<div class="jv-am-h">Scheduled tasks (%s)</div><ul>'
                 % _esc(th.get("overall_task_health", "?")))
    for t in (th.get("tasks") or []):
        cls = {"OK": "jv-am-ok", "STALE": "jv-am-warn", "FAILED": "jv-am-bad",
               "MISSING": "jv-am-bad"}.get(t.get("status"), "jv-am-muted")
        parts.append('<li class="%s">%s: <b>%s</b>%s</li>' % (
            cls, _esc(t.get("name")), _esc(t.get("status")),
            " (priority)" if t.get("is_priority") else ""))
    parts.append('</ul>')
    # next action
    parts.append('<div class="jv-am-h jv-am-gate">Next action (suggestion only — never '
                 'auto-executed)</div>')
    parts.append('<div class="jv-am-paste">➤ <code>%s</code></div>'
                 % _esc(na.get("authoritative_next_action")))
    parts.append('<div class="jv-detail">At 20/20 suggest: <code>%s</code></div>'
                 % _esc(na.get("review_token_when_ready")))
    parts.append('<div class="jv-detail">C23 opens (after C22 concludes) via: '
                 '<code>%s</code></div>' % _esc(na.get("c23_open_token_after_c22")))
    parts.append('</div>')
    # optional read-only Bundle C watchdog + Bundle D lifecycle summaries
    parts.append(render_watchdog_section_html(watchdog))
    parts.append(render_lifecycle_section_html(lifecycle))
    return "".join(parts)
