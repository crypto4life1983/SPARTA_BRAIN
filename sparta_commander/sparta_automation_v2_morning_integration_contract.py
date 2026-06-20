"""SPARTA Automation V2 -- Morning Surface Integration Bundle
-- PURE, READ-ONLY, RESEARCH ONLY.

A cohesive, read-only integration layer that surfaces the SPARTA Research Factory
Automation V2 / Morning Decision Packet inside the existing morning-report and
autopilot-panel surfaces, WITHOUT modifying those surface files (regression safety). It
proves exactly how each surface consumes the V2 packet:

  * `repo_state_from_surface()` -- maps a morning surface's git summary (+ optional sync
    info) to the V2 `repo_state`, flagging which fields are known vs defaulted;
  * `build_v2_morning_section()` -- the display-ready Automation V2 section (repo sync,
    git-safety, candidate status, C22 DATA_NOT_READY blocker, evidence chain, recommended
    next safe task, the EXACT next human approval token, and the explicit danger-lock
    display);
  * `render_v2_section_markdown()` / `render_v2_section_html()` -- additive renderers;
  * `augment_morning_report()` / `augment_panel()` -- NON-MUTATING composers that return a
    NEW dict with the V2 section attached (the original report/panel is never mutated);
  * `augment_morning_report_markdown()` -- appends the V2 markdown to an existing report
    markdown string.

It executes NOTHING, performs NO git/network I/O, and changes NO automation behaviour: it
only RE-SURFACES the read-only V2 recommendations. While C22 is at DATA_NOT_READY the
surfaced recommendation is DATASET STAGING (never "advance to labels", never fabricate
data). Every dangerous channel is shown LOCKED and every capability flag is pinned False.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.sparta_research_factory_automation_v2_contract as _v2

MI_SCHEMA_VERSION = 1
MI_MODE = "RESEARCH_ONLY"
MI_LANE = "crypto_d1_auto_research"
BUNDLE_NAME = "SPARTA_AUTOMATION_V2_MORNING_SURFACE_INTEGRATION"

# the explicit human-readable danger-lock lines the surface must display.
DANGER_LOCK_DISPLAY = (
    "no live trading",
    "no paper trading",
    "no broker/order code",
    "no Signum / MCP / Hyperliquid / API-wallet / credentials",
    "no Claude routines",
    "no bot edits",
    "no scheduler install/trigger",
    "no auto commit / push / fetch / promote / advance",
)

_CAPABILITY_FLAGS_FALSE = (
    "executes", "performs_git_io", "performs_network_io", "mutates_source_surfaces",
    "auto_commits", "auto_pushes", "auto_fetches_data", "auto_promotes_candidate",
    "auto_advances_gate", "skips_any_human_gate", "broad_git_add", "fetches_data",
    "stages_dataset", "starts_c22_labels", "builds_replay", "modifies_strategy_rules",
    "reopens_closed_candidate", "starts_c23", "modifies_scheduler",
    "installs_scheduler", "triggers_scheduler", "sends_notifications", "sends_email",
    "calls_api", "uses_network", "uses_credentials", "uses_api_keys", "connects_signum",
    "uses_mcp", "accesses_hyperliquid", "connects_broker", "connects_exchange",
    "sends_trades", "edits_bots", "creates_claude_routines", "uses_real_money",
    "places_orders", "contains_order_logic", "paper_trading", "live_trading",
    "deploys_capital", "recommends_advancing_to_labels_while_blocked",
    "unlocks_downstream_gate", "crosses_into_forbidden_gate",
)


def repo_state_from_surface(git_summary: dict | None,
                            sync_info: dict | None = None) -> dict[str, Any]:
    """PURE. Map a morning-surface git summary (clean/staged/modified/untracked) plus an
    optional sync_info (head/origin/ahead/behind) to the V2 repo_state. Flags which
    fields are KNOWN vs defaulted so the surface never over-claims sync facts it lacks."""
    gs = git_summary or {}
    si = sync_info or {}
    staged = int(gs.get("staged", 0) or 0)
    modified = int(gs.get("modified", 0) or 0)
    untracked = int(gs.get("untracked", 0) or 0)
    clean = gs.get("clean")
    if clean is None:
        clean = (staged == 0 and modified == 0)
    sync_known = bool(si)
    return {
        "head": si.get("head"),
        "origin": si.get("origin"),
        "ahead": int(si.get("ahead", 0) or 0),
        "behind": int(si.get("behind", 0) or 0),
        "clean": bool(clean),
        "staged_count": staged,
        "untracked_clutter_present": untracked > 0,
        "untracked_clutter_ignored_by_path": True,
        # provenance of what is known vs defaulted
        "_sync_info_known": sync_known,
        "_clean_known": gs.get("clean") is not None,
    }


def build_v2_morning_section(repo_state: dict) -> dict[str, Any]:
    """PURE. Build the display-ready Automation V2 morning section from the V2 packet.
    Read-only; surfaces the C22 DATA_NOT_READY block as a DATASET-STAGING recommendation
    (never labels)."""
    pkt = _v2.build_morning_decision_packet(repo_state)
    git = pkt["git_safety"]
    cand = pkt["candidate_status"]["c22"]
    gate = pkt["recommended_gate"]
    c22_blocked = cand.get("blocked_reason") == "DATA_NOT_READY"

    section: dict[str, Any] = {
        "section": "automation_v2_morning_packet",
        "bundle": _v2.BUNDLE_NAME,
        "integration_bundle": BUNDLE_NAME,
        "mode": MI_MODE, "read_only": True, "recommends_only": True,
        "executes_nothing": True,
        # repo sync + safety
        "repo_sync": dict(pkt["repo_sync"]),
        "git_safe_to_automate": git["safe_to_automate"],
        "git_blockers": list(git["blockers"]),
        "git_warnings": list(git["warnings"]),
        "sync_info_known": bool(repo_state.get("_sync_info_known")),
        # candidate status + the C22 blocker
        "candidate_status_line": (
            "C22 at %s -- %s%s" % (cand.get("current_stage"), cand.get("last_verdict"),
                                   " (BLOCKED)" if c22_blocked else "")),
        "lane_active_candidate": pkt["candidate_status"]["lane_active_candidate"],
        "rejected_ledger_count": pkt["candidate_status"]["rejected_ledger_count"],
        "last_rejected_candidate":
            pkt["candidate_status"]["last_rejected_candidate"],
        "c22_stage_verdicts": dict(cand.get("stage_verdicts") or {}),
        "c22_data_not_ready": c22_blocked,
        "last_verdict": pkt["last_verdict"],
        "blockers": list(pkt["blockers"]),
        # evidence
        "evidence_chain_valid": pkt["evidence"]["c22_chain_artifacts_valid"],
        "evidence_test_files": list(pkt["evidence"]["c22_evidence_test_files"]),
        # the recommendation + exact next token
        "recommended_gate_kind": gate["recommendation_kind"],
        "recommended_gate_reason": gate["reason"],
        "recommended_next_safe_task": pkt["next_safe_task"]["next_safe_task"],
        "next_human_approval_token": pkt["next_recommended_human_action"],
        "do_not_proceed_to_labels": c22_blocked,
        "do_not_fabricate_data": c22_blocked,
        # explicit safety-lock display
        "danger_locks_display": list(DANGER_LOCK_DISPLAY),
        "danger_locks": dict(pkt["danger_locks"]),
        "requires_human_approval": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        section[flag] = False
    # honest cross-check: True ONLY if the recommendation is actually ADVANCE while
    # blocked (a dirty-repo RESOLVE_REPO or a pending PUSH legitimately takes priority and
    # is NOT "advancing to labels").
    section["recommends_advancing_to_labels_while_blocked"] = (
        c22_blocked and gate["recommendation_kind"] == _v2.REC_ADVANCE)
    return section


def render_v2_section_markdown(section: dict) -> str:
    """PURE. Additive markdown block for the morning report (does not touch the rest)."""
    s = section or {}
    lines = ["## Automation V2 -- Morning Decision Packet (read-only, research-only)"]
    rs = s.get("repo_sync") or {}
    lines.append("- Repo sync: in_sync=%s ahead=%s behind=%s clean=%s | safe_to_"
                 "automate=%s" % (rs.get("in_sync"), rs.get("ahead"), rs.get("behind"),
                                  rs.get("clean"), s.get("git_safe_to_automate")))
    lines.append("- Candidate: %s" % s.get("candidate_status_line"))
    lines.append("- Rejected ledger: C1-C21 (%s) | last rejected: %s | lane active: %s"
                 % (s.get("rejected_ledger_count"), s.get("last_rejected_candidate"),
                    s.get("lane_active_candidate")))
    lines.append("- Last verdict: **%s** | blockers: %s"
                 % (s.get("last_verdict"), ", ".join(s.get("blockers") or []) or "none"))
    lines.append("- Evidence chain valid: %s" % s.get("evidence_chain_valid"))
    lines.append("- Recommended next gate: **%s** -- %s"
                 % (s.get("recommended_gate_kind"), s.get("recommended_gate_reason")))
    lines.append("- Next safe task: %s" % s.get("recommended_next_safe_task"))
    lines.append("- NEXT HUMAN APPROVAL TOKEN (copy-paste): `%s`"
                 % s.get("next_human_approval_token"))
    if s.get("c22_data_not_ready"):
        lines.append("- ⚠ C22 is DATA_NOT_READY -- DO NOT proceed to labels; DO NOT "
                     "fabricate data; stage a frozen dataset first.")
    lines.append("- Safety locks: %s" % "; ".join(s.get("danger_locks_display") or []))
    return "\n".join(lines)


def render_v2_section_html(section: dict) -> str:
    """PURE. Additive HTML block for the autopilot/JARVIS panel."""
    s = section or {}

    def esc(x: Any) -> str:
        return (str(x).replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;"))
    parts = ['<div class="jv-am-h">Automation V2 — Morning Decision Packet</div>']
    parts.append('<div class="jv-detail">Candidate: <b>%s</b></div>'
                 % esc(s.get("candidate_status_line")))
    parts.append('<div class="jv-detail">Last verdict: <code>%s</code> · safe to '
                 'automate: %s</div>' % (esc(s.get("last_verdict")),
                                         esc(s.get("git_safe_to_automate"))))
    parts.append('<div class="jv-detail">Recommended: <b>%s</b></div>'
                 % esc(s.get("recommended_gate_kind")))
    parts.append('<div class="jv-detail">Next approval token: <code>%s</code></div>'
                 % esc(s.get("next_human_approval_token")))
    if s.get("c22_data_not_ready"):
        parts.append('<div class="jv-detail jv-am-bad">⚠ C22 DATA_NOT_READY — do NOT '
                     'proceed to labels; do NOT fabricate data; stage a frozen dataset '
                     'first.</div>')
    parts.append('<div class="jv-detail">Safety locks: %s</div>'
                 % esc("; ".join(s.get("danger_locks_display") or [])))
    return "".join(parts)


def augment_morning_report(report: dict, git_summary: dict | None = None,
                           sync_info: dict | None = None) -> dict[str, Any]:
    """PURE, NON-MUTATING. Return a NEW report dict with the Automation V2 section
    attached. The original `report` is never mutated. If git_summary is omitted, the
    report's own `git_status_summary` is used."""
    rep = dict(report or {})
    gs = git_summary if git_summary is not None else rep.get("git_status_summary")
    repo_state = repo_state_from_surface(gs, sync_info)
    section = build_v2_morning_section(repo_state)
    rep["automation_v2_packet"] = section
    rep["automation_v2_packet_markdown"] = render_v2_section_markdown(section)
    rep["automation_v2_integrated"] = True
    rep["automation_v2_source_unmutated"] = True
    return rep


def augment_morning_report_markdown(existing_markdown: str, section: dict) -> str:
    """PURE. Append the V2 markdown section to an existing morning-report markdown."""
    base = existing_markdown or ""
    return (base.rstrip("\n") + "\n\n" + render_v2_section_markdown(section)).lstrip("\n")


def augment_panel(panel: dict, git_summary: dict | None = None,
                  sync_info: dict | None = None) -> dict[str, Any]:
    """PURE, NON-MUTATING. Return a NEW panel dict with the Automation V2 section + its
    HTML block attached. The original `panel` is never mutated."""
    pan = dict(panel or {})
    gs = git_summary
    if gs is None:
        gs = (pan.get("git_status_summary")
              or (pan.get("automation_readiness") or {}).get("git_status_summary"))
    repo_state = repo_state_from_surface(gs, sync_info)
    section = build_v2_morning_section(repo_state)
    pan["automation_v2"] = section
    pan["automation_v2_html"] = render_v2_section_html(section)
    pan["automation_v2_integrated"] = True
    pan["automation_v2_source_unmutated"] = True
    return pan


def validate_v2_morning_section(section: dict) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the section is research-only, read-only,
    surfaces the candidate status + (while blocked) the C22 DATA_NOT_READY DATASET-STAGING
    recommendation (never labels, never fabricate data), carries the explicit danger-lock
    display + the locked danger channels, the C1-C21 (26) ledger, the exact next human
    approval token, and pins every capability flag False."""
    failures: list = []
    if section.get("mode") != MI_MODE:
        failures.append("mode_not_research_only")
    if section.get("read_only") is not True:
        failures.append("not_read_only")
    if section.get("recommends_only") is not True:
        failures.append("not_recommends_only")
    if section.get("executes_nothing") is not True:
        failures.append("executes_something")

    # candidate ledger + status surfaced
    if section.get("rejected_ledger_count") != 26:
        failures.append("ledger_not_26")
    if not section.get("candidate_status_line"):
        failures.append("candidate_status_line_missing")
    if not section.get("last_verdict"):
        failures.append("last_verdict_missing")

    # while C22 is DATA_NOT_READY: staging recommendation when the repo is safe, never
    # labels / fabricate. A dirty repo (RESOLVE_REPO) or pending push legitimately takes
    # higher priority -- but the section must NEVER recommend advancing to labels.
    if section.get("c22_data_not_ready") is True:
        rs = section.get("repo_sync") or {}
        git_safe = (section.get("git_safe_to_automate") is True
                    and int(rs.get("ahead", 0) or 0) == 0)
        if git_safe and section.get("recommended_gate_kind") != _v2.REC_STAGE_DATA:
            failures.append("blocked_must_recommend_staging_when_repo_safe")
        if section.get("recommended_gate_kind") == _v2.REC_ADVANCE and git_safe:
            failures.append("must_not_advance_to_labels_while_blocked")
        if section.get("do_not_proceed_to_labels") is not True:
            failures.append("must_say_do_not_proceed_to_labels")
        if section.get("do_not_fabricate_data") is not True:
            failures.append("must_say_do_not_fabricate_data")
        if section.get("recommends_advancing_to_labels_while_blocked") is not False:
            failures.append("must_not_advance_to_labels_while_blocked")
        tok = section.get("next_human_approval_token") or ""
        if "STAGE_FROZEN_TREND_RADAR_GC_DETECTOR_DATASET" not in tok:
            failures.append("next_token_not_dataset_staging")

    # the explicit danger-lock display + locked channels
    disp = section.get("danger_locks_display") or []
    joined = " || ".join(disp).lower()
    for must in ("no live trading", "no paper trading", "no broker/order",
                 "signum", "mcp", "hyperliquid", "no claude routines", "no bot edits",
                 "no scheduler", "no auto commit"):
        if must not in joined:
            failures.append("danger_display_missing_%s" % must.split()[0])
    dl = section.get("danger_locks") or {}
    for k in ("no_automatic_commit", "no_automatic_push", "no_automatic_data_fetch",
              "no_automatic_candidate_promotion", "never_skips_human_gates",
              "live_trading_locked", "paper_trading_locked", "signum_locked",
              "mcp_locked", "hyperliquid_locked", "scheduler_locked",
              "bot_edits_locked", "trades_locked"):
        if dl.get(k) is not True:
            failures.append("danger_lock_off_%s" % k)

    # the next approval token present + carries no forbidden verb
    if not section.get("next_human_approval_token"):
        failures.append("next_token_missing")
    low = str(section.get("next_human_approval_token") or "").lower()
    for bad in _v2.FORBIDDEN_TOKEN_SUBSTRINGS:
        if bad in low:
            failures.append("next_token_forbidden_%s" % bad)

    for flag in _CAPABILITY_FLAGS_FALSE:
        if section.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
