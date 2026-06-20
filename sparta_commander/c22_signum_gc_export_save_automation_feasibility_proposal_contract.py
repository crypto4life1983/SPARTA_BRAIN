"""Candidate #22 -- Signum GC EXPORT/SAVE AUTOMATION FEASIBILITY PROPOSAL
-- PURE, PROPOSAL-ONLY, RESEARCH ONLY.

DEFINES (does NOT implement) a feasibility comparison of ways to automate the currently
MANUAL step -- export/save the daily Signum Trend Radar GC JSON into the approved local
inbox (data/external_signum_trend_radar_gc_inbox/). It is a PROPOSAL: it performs NO live
Signum/GC login, NO fetch, NO browser automation, NO API call, NO MCP call, and NO network
call; it stores NO credentials / cookies / tokens / passwords / session files; and it
implements NOTHING. C22 stays HOLD_FOR_MORE_FROZEN_DATA_WINDOWS with replay locked.

It compares three options on safety / credential exposure / brittleness / ToS-account risk:

  (1) Official export / API method (IF one exists)  -- preferred IF a READ-ONLY official
      export is available; needs an API key kept OUTSIDE the repo; verifying availability is
      a separate future read-only human-gated step.
  (2) Browser / UI automation (if no official export) -- NOT recommended: requires stored
      login/session, is brittle to UI changes, and carries ToS/account risk.
  (3) Semi-automatic reminder + manual download fallback -- the SAFEST and largely already
      in place (external read-only Claude Routine export + local importer + import
      automation + readiness watcher); needs no credentials and no SPARTA-side network.

Recommendation: ADOPT option 3 now; INVESTIGATE option 1 next as a read-only human-gated
feasibility check; do NOT pursue option 2. Every dangerous capability is pinned False.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.c22_signum_gc_data_collection_tracker_contract as _trk

FP_SCHEMA_VERSION = 1
FP_MODE = "RESEARCH_ONLY"
FP_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = _trk.CANDIDATE_ID
INBOX_DIR = "data/external_signum_trend_radar_gc_inbox"
C22_STATE = _trk.C22_STATE                            # HOLD_FOR_MORE_FROZEN_DATA_WINDOWS

VERDICT_PROPOSAL_READY = "C22_EXPORT_SAVE_AUTOMATION_FEASIBILITY_PROPOSAL_READY_FOR_REVIEW"
NEXT_REQUIRED_ACTION = "HUMAN_DECISION_C22_EXPORT_SAVE_AUTOMATION_METHOD_OR_HOLD"

OPTION_OFFICIAL = "official_export_or_api"
OPTION_BROWSER = "browser_ui_automation"
OPTION_SEMI_AUTO = "semi_auto_reminder_manual_download"

ROLE_ADOPT_NOW = "adopt_now"
ROLE_INVESTIGATE_NEXT = "investigate_next_read_only_human_gated"
ROLE_NOT_RECOMMENDED = "not_recommended"

# the three options, compared. SAFETY_RANK: 1 = safest.
OPTIONS = (
    {
        "id": OPTION_SEMI_AUTO,
        "name": "Semi-automatic reminder + manual download fallback",
        "description": (
            "The human stays the actor: the external read-only Claude Routine produces the "
            "JSON, the human saves it to the inbox, and SPARTA's importer + import "
            "automation + readiness watcher handle everything after the file exists. Add "
            "only a daily REMINDER nudge (already surfaced by the Jarvis tracker / watcher) "
            "-- no SPARTA-side login, fetch, or browser."),
        "requires_credentials": False,
        "credential_storage_required": False,
        "needs_network_when_implemented": False,
        "needs_browser_automation": False,
        "tos_or_account_risk": "none",
        "brittleness": "low",
        "safety_rank": 1,
        "largely_already_built": True,
        "pros": ["no credentials stored anywhere", "no SPARTA-side network/browser",
                 "no ToS/account risk", "robust to Signum UI/API changes",
                 "most of the pipeline already exists"],
        "cons": ["the daily export+save click remains manual",
                 "depends on human consistency (mitigated by the reminder + tracker)"],
        "recommendation_role": ROLE_ADOPT_NOW,
    },
    {
        "id": OPTION_OFFICIAL,
        "name": "Official export / API method (if available)",
        "description": (
            "IF Signum exposes a READ-ONLY official export/API for trend-radar-daily, a "
            "local one-shot could fetch + save the JSON. Requires an API key kept OUTSIDE "
            "the repo (gitignored local_secrets/, never committed). Whether such a "
            "read-only export exists is UNKNOWN here and must be verified by a separate "
            "read-only, human-gated feasibility step -- not in this proposal."),
        "requires_credentials": True,
        "credential_storage_required": True,
        "credential_storage_location_if_adopted": "gitignored local_secrets/ (never repo)",
        "needs_network_when_implemented": True,
        "needs_browser_automation": False,
        "tos_or_account_risk": "low_if_official_read_only",
        "brittleness": "low_to_medium",
        "safety_rank": 2,
        "availability_unknown_must_verify_read_only": True,
        "pros": ["fully hands-off once configured", "stable if officially supported",
                 "read-only scope possible (export only, no trading)"],
        "cons": ["requires an API key + secure out-of-repo storage",
                 "availability unknown -- needs a read-only feasibility check first",
                 "introduces a SPARTA-side network dependency"],
        "recommendation_role": ROLE_INVESTIGATE_NEXT,
    },
    {
        "id": OPTION_BROWSER,
        "name": "Browser / UI automation (if no official export)",
        "description": (
            "Drive a headless/automated browser to log into Signum and download the JSON. "
            "Requires storing login credentials or a session/cookie, is brittle to any UI "
            "change, and may violate ToS / trigger account protections."),
        "requires_credentials": True,
        "credential_storage_required": True,
        "needs_network_when_implemented": True,
        "needs_browser_automation": True,
        "tos_or_account_risk": "high",
        "brittleness": "high",
        "safety_rank": 3,
        "pros": ["works even with no official export"],
        "cons": ["must store login/session (high credential-exposure risk)",
                 "brittle: breaks on any Signum UI change",
                 "possible ToS violation / account lockout risk",
                 "hard to keep strictly read-only"],
        "recommendation_role": ROLE_NOT_RECOMMENDED,
    },
)

_CAPABILITY_FLAGS_FALSE = (
    "executes", "implements_export_automation", "performs_signum_login", "fetches_data",
    "performs_network_io", "performs_browser_automation", "calls_api", "uses_mcp",
    "opens_browser", "stores_credentials", "stores_cookies", "stores_tokens",
    "stores_passwords", "stores_session_files", "uses_api_keys", "connects_signum",
    "accesses_hyperliquid", "runs_labels", "runs_replay", "builds_replay",
    "optimizes_parameters", "edits_bots", "sends_trades", "places_orders",
    "contains_order_logic", "paper_trading", "live_trading", "connects_broker",
    "installs_scheduler", "triggers_scheduler", "modifies_c22_rules", "starts_c23",
    "reopens_c21", "auto_commits", "auto_pushes", "auto_advances",
    "crosses_into_forbidden_gate",
)


def build_feasibility_proposal() -> dict[str, Any]:
    """Assemble the PROPOSAL-ONLY feasibility comparison + recommendation. Pure; no I/O;
    implements nothing; performs no login/fetch/browser/API/MCP/network."""
    options = [dict(o) for o in OPTIONS]
    recommended_primary = OPTION_SEMI_AUTO
    investigate_next = OPTION_OFFICIAL
    not_recommended = OPTION_BROWSER

    record: dict[str, Any] = {
        "schema_version": FP_SCHEMA_VERSION, "mode": FP_MODE, "lane": FP_LANE,
        "candidate_id": CANDIDATE_ID,
        "is_proposal_only": True, "implements_nothing": True,
        "label": (
            "Candidate #22 Signum GC export/save automation feasibility PROPOSAL "
            "(PROPOSAL ONLY, RESEARCH ONLY). Compares official-API vs browser-automation vs "
            "semi-auto-reminder for automating the manual daily export/save into the inbox. "
            "Implements nothing; performs no login/fetch/browser/API/MCP/network; stores no "
            "credentials. Recommends adopting the semi-auto reminder now and investigating "
            "an official read-only export next (separate human gate); browser automation is "
            "not recommended."),
        "inbox_dir": INBOX_DIR,
        "options": options,
        "comparison_axes": ["requires_credentials", "credential_storage_required",
                            "needs_network_when_implemented", "needs_browser_automation",
                            "tos_or_account_risk", "brittleness", "safety_rank"],
        # recommendation
        "recommended_primary": recommended_primary,
        "recommended_primary_role": ROLE_ADOPT_NOW,
        "investigate_next": investigate_next,
        "investigate_next_is_read_only_human_gated": True,
        "not_recommended": not_recommended,
        "recommendation_summary": (
            "ADOPT the semi-automatic reminder + manual download now (safest, no "
            "credentials, largely already built via the external Routine + importer + "
            "import automation + readiness watcher). INVESTIGATE an official READ-ONLY "
            "Signum export next as a separate read-only, human-gated feasibility step. Do "
            "NOT pursue browser/UI automation (credential exposure + brittleness + ToS "
            "risk)."),
        "verdict": VERDICT_PROPOSAL_READY,
        "next_required_action": NEXT_REQUIRED_ACTION,
        # preserved state
        "c22_state": C22_STATE,
        "replay_locked": True,
        "advances_nothing": True,
        "human_review_required": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_execute": True, "no_implement_export_automation": True,
        "no_signum_login": True, "no_fetch": True, "no_network_io": True,
        "no_browser_automation": True, "no_open_browser": True, "no_api_call": True,
        "no_mcp": True, "no_store_credentials": True, "no_store_cookies": True,
        "no_store_tokens": True, "no_store_passwords": True, "no_store_session_files": True,
        "no_api_keys": True, "no_signum_connection": True, "no_hyperliquid": True,
        "no_run_labels": True, "no_replay": True, "no_optimization": True,
        "no_bot_edits": True, "no_trades": True, "no_order_logic": True,
        "no_paper_trading": True, "no_live_trading": True, "no_broker": True,
        "no_install_scheduler": True, "no_trigger_scheduler": True,
        "no_modify_c22_rules": True, "no_start_c23": True, "no_reopen_c21": True,
        "no_auto_commit": True, "no_auto_push": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_feasibility_proposal(record: Any) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when research-only, proposal-only (implements
    nothing, no login/fetch/browser/API/MCP/network, stores no credentials); all three
    options are compared; the recommendation prefers the semi-auto option, marks the
    official option as a read-only human-gated follow-up, and rejects browser automation;
    C22 stays HOLD with replay locked; and every capability flag is False."""
    failures: list = []
    if not isinstance(record, dict):
        return {"valid": False, "failures": ["record_not_a_dict"]}
    r = record

    if r.get("mode") != FP_MODE:
        failures.append("mode_not_research_only")
    if r.get("is_proposal_only") is not True:
        failures.append("not_proposal_only")
    if r.get("implements_nothing") is not True:
        failures.append("implements_something")
    if r.get("verdict") != VERDICT_PROPOSAL_READY:
        failures.append("bad_verdict")

    # all three options present + compared
    opts = {o.get("id"): o for o in (r.get("options") or [])}
    for oid in (OPTION_OFFICIAL, OPTION_BROWSER, OPTION_SEMI_AUTO):
        if oid not in opts:
            failures.append("option_missing_%s" % oid)
    for oid, o in opts.items():
        for axis in ("requires_credentials", "needs_browser_automation", "safety_rank",
                     "recommendation_role"):
            if axis not in o:
                failures.append("option_%s_missing_axis_%s" % (oid, axis))

    # recommendation: semi-auto adopt-now, official investigate-next, browser not-recommended
    if r.get("recommended_primary") != OPTION_SEMI_AUTO:
        failures.append("primary_not_semi_auto")
    if opts.get(OPTION_SEMI_AUTO, {}).get("recommendation_role") != ROLE_ADOPT_NOW:
        failures.append("semi_auto_not_adopt_now")
    if r.get("investigate_next") != OPTION_OFFICIAL:
        failures.append("investigate_next_not_official")
    if r.get("investigate_next_is_read_only_human_gated") is not True:
        failures.append("official_followup_not_read_only_human_gated")
    if opts.get(OPTION_OFFICIAL, {}).get("recommendation_role") != ROLE_INVESTIGATE_NEXT:
        failures.append("official_not_investigate_next")
    if r.get("not_recommended") != OPTION_BROWSER:
        failures.append("not_recommended_not_browser")
    if opts.get(OPTION_BROWSER, {}).get("recommendation_role") != ROLE_NOT_RECOMMENDED:
        failures.append("browser_not_marked_not_recommended")
    # the semi-auto option must be the credential-free, no-browser, safest one
    sa = opts.get(OPTION_SEMI_AUTO, {})
    if sa.get("requires_credentials") is not False:
        failures.append("semi_auto_should_need_no_credentials")
    if sa.get("needs_browser_automation") is not False:
        failures.append("semi_auto_should_need_no_browser")
    if sa.get("safety_rank") != 1:
        failures.append("semi_auto_should_be_safest")

    # state preserved
    if r.get("c22_state") != C22_STATE:
        failures.append("c22_state_changed")
    if r.get("replay_locked") is not True:
        failures.append("replay_not_locked")
    if r.get("advances_nothing") is not True:
        failures.append("must_advance_nothing")

    locks = r.get("scope_locks") or {}
    for key in ("no_execute", "no_implement_export_automation", "no_signum_login",
                "no_fetch", "no_network_io", "no_browser_automation", "no_api_call",
                "no_mcp", "no_store_credentials", "no_store_cookies", "no_store_tokens",
                "no_store_passwords", "no_store_session_files", "no_api_keys",
                "no_signum_connection", "no_run_labels", "no_replay", "no_optimization",
                "no_order_logic", "no_paper_trading", "no_live_trading",
                "no_modify_c22_rules", "no_start_c23", "no_reopen_c21"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if r.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
