"""SPARTA Automation V2 -- Daily Decision Report Contract
-- PURE, READ-ONLY, RESEARCH ONLY.

The PURE content builder for the overnight/autopilot "daily decision report" artifact. It
assembles a deterministic daily report from the Automation V2 morning-section integration
(the read-only morning decision packet) plus the injected git/run facts -- run timestamp,
git HEAD, sync state, candidate state, blockers, recommended next action, the EXACT human
approval token, and the danger-lock display. The matching runner
(tools/sparta_automation_v2_daily_report_once.py) gathers the git facts read-only and
writes this report to a GITIGNORED local artifact path; this contract performs NO I/O.

Determinism: `build_daily_report(repo_state, run_timestamp)` is a pure function of its
inputs and the FROZEN committed candidate chain, so the rendered markdown is byte-stable
for fixed inputs. `build_sample_report()` pins a fixed sample (SAMPLE_REPO_STATE +
SAMPLE_TIMESTAMP) whose rendered markdown SHA256 is pinned in SAMPLE_MARKDOWN_SHA256.

It executes NOTHING, performs NO git/network I/O, commits/pushes/fetches NOTHING, stages
no dataset, starts no labels/replay, modifies no strategy rules, and touches NO Signum /
MCP / Hyperliquid / API / credentials / paper / live / broker / order / scheduler surface.
Every dangerous capability is pinned False with a full scope_locks set. While C22 is at
DATA_NOT_READY the surfaced recommendation is DATASET STAGING (never labels, never fake
data).
"""
from __future__ import annotations

from typing import Any

import sparta_commander.sparta_automation_v2_morning_integration_contract as _mi

DR_SCHEMA_VERSION = 1
DR_MODE = "RESEARCH_ONLY"
DR_LANE = "crypto_d1_auto_research"
BUNDLE_NAME = "SPARTA_AUTOMATION_V2_DAILY_DECISION_REPORT"

# the SAFE, gitignored artifact location (relative to repo root).
ARTIFACT_DIR = "reports/automation_v2_daily"
ARTIFACT_MARKDOWN_BASENAME = "automation_v2_daily_report"
ARTIFACT_JSON_BASENAME = "automation_v2_daily_report"
ARTIFACT_IS_GITIGNORED = True

# the human-readable runner-safety lines the report must display.
RUNNER_SAFETY_DISPLAY = (
    "read-only runner: no git commit / push / fetch",
    "no broad git add; writes only to the gitignored reports artifact path",
    "no data fetch; no network; no API keys / credentials",
    "no Signum / MCP / Hyperliquid",
    "no live / paper trading; no broker / order code",
    "no scheduler install or trigger",
    "no auto-advance / auto-promote / auto-commit / auto-push",
)

_CAPABILITY_FLAGS_FALSE = (
    "executes", "performs_git_io", "performs_network_io", "writes_files",
    "auto_commits", "auto_pushes", "auto_fetches_data", "auto_promotes_candidate",
    "auto_advances_gate", "skips_any_human_gate", "broad_git_add", "fetches_data",
    "stages_dataset", "starts_c22_labels", "builds_replay", "modifies_strategy_rules",
    "reopens_closed_candidate", "starts_c23", "modifies_scheduler", "installs_scheduler",
    "triggers_scheduler", "sends_notifications", "sends_email", "calls_api",
    "uses_network", "uses_credentials", "uses_api_keys", "connects_signum", "uses_mcp",
    "accesses_hyperliquid", "connects_broker", "connects_exchange", "sends_trades",
    "edits_bots", "creates_claude_routines", "uses_real_money", "places_orders",
    "contains_order_logic", "paper_trading", "live_trading", "deploys_capital",
    "commits_artifact_to_git", "recommends_advancing_to_labels_while_blocked",
    "unlocks_downstream_gate", "crosses_into_forbidden_gate",
)


def _runner_safety() -> dict[str, bool]:
    return {
        "read_only": True, "no_git_commit": True, "no_git_push": True,
        "no_git_fetch": True, "no_broad_git_add": True, "no_data_fetch": True,
        "no_network": True, "no_signum": True, "no_mcp": True, "no_hyperliquid": True,
        "no_api_keys": True, "no_credentials": True, "no_live_trading": True,
        "no_paper_trading": True, "no_broker": True, "no_order_logic": True,
        "no_scheduler_install": True, "no_scheduler_trigger": True,
        "no_auto_advance": True, "no_auto_promote": True,
        "writes_only_to_gitignored_reports_path": True,
        "artifact_not_committed_to_git": True,
    }


def build_daily_report(repo_state: dict, run_timestamp: str) -> dict[str, Any]:
    """PURE. Assemble the deterministic daily decision report from the V2 morning section
    + the injected git/run facts. No I/O. Byte-stable for fixed inputs."""
    section = _mi.build_v2_morning_section(repo_state)
    rs_sync = section["repo_sync"]

    record: dict[str, Any] = {
        "schema_version": DR_SCHEMA_VERSION, "mode": DR_MODE, "lane": DR_LANE,
        "bundle_name": BUNDLE_NAME,
        "section": "automation_v2_daily_decision_report",
        "is_read_only_report": True, "recommends_only": True, "executes_nothing": True,
        # artifact metadata (the runner writes to this gitignored path)
        "artifact": {
            "dir": ARTIFACT_DIR,
            "markdown_basename": ARTIFACT_MARKDOWN_BASENAME,
            "json_basename": ARTIFACT_JSON_BASENAME,
            "gitignored": ARTIFACT_IS_GITIGNORED,
            "committed_to_git": False},
        # run + git facts
        "run_timestamp_utc": run_timestamp,
        "git_head": rs_sync.get("head"),
        "git_origin": rs_sync.get("origin"),
        "in_sync": rs_sync.get("in_sync"),
        "ahead": rs_sync.get("ahead"), "behind": rs_sync.get("behind"),
        "tree_clean": rs_sync.get("clean"),
        "git_safe_to_automate": section["git_safe_to_automate"],
        "git_blockers": list(section["git_blockers"]),
        "git_warnings": list(section["git_warnings"]),
        "sync_info_known": section["sync_info_known"],
        # candidate state
        "candidate_status_line": section["candidate_status_line"],
        "lane_active_candidate": section["lane_active_candidate"],
        "rejected_ledger_count": section["rejected_ledger_count"],
        "last_rejected_candidate": section["last_rejected_candidate"],
        "c22_stage_verdicts": dict(section["c22_stage_verdicts"]),
        "c22_data_not_ready": section["c22_data_not_ready"],
        "last_verdict": section["last_verdict"],
        "blockers": list(section["blockers"]),
        "evidence_chain_valid": section["evidence_chain_valid"],
        # recommendation + token
        "recommended_gate_kind": section["recommended_gate_kind"],
        "recommended_next_safe_task": section["recommended_next_safe_task"],
        "next_human_approval_token": section["next_human_approval_token"],
        "do_not_proceed_to_labels": section["do_not_proceed_to_labels"],
        "do_not_fabricate_data": section["do_not_fabricate_data"],
        "recommends_advancing_to_labels_while_blocked":
            section["recommends_advancing_to_labels_while_blocked"],
        # danger + runner safety
        "danger_locks_display": list(section["danger_locks_display"]),
        "danger_locks": dict(section["danger_locks"]),
        "runner_safety": _runner_safety(),
        "runner_safety_display": list(RUNNER_SAFETY_DISPLAY),
        # the embedded V2 section (full)
        "v2_morning_section": section,
        "requires_human_approval": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_execute": True, "no_git_io": True, "no_network_io": True,
        "no_git_commit": True, "no_git_push": True, "no_git_fetch": True,
        "no_broad_git_add": True, "no_data_fetch": True, "no_stage_dataset": True,
        "no_start_labels": True, "no_replay": True, "no_modify_strategy_rules": True,
        "no_reopen_closed_candidate": True, "no_start_c23": True, "no_signum": True,
        "no_mcp": True, "no_hyperliquid": True, "no_api_keys": True,
        "no_credentials": True, "no_bot_edits": True, "no_claude_routines": True,
        "no_send_trades": True, "no_broker": True, "no_order_logic": True,
        "no_paper_trading": True, "no_live_trading": True, "no_scheduler_install": True,
        "no_scheduler_trigger": True, "no_auto_advance": True, "no_auto_promote": True,
        "no_commit_artifact": True, "no_crossing_into_forbidden_gate": True,
    }
    record["report_markdown"] = render_daily_report_markdown(record)
    return record


def render_daily_report_markdown(report: dict) -> str:
    """PURE. The full daily report markdown (run header + the V2 section + runner
    safety). Deterministic for fixed inputs."""
    r = report or {}
    lines = ["# SPARTA Automation V2 -- Daily Decision Report",
             "",
             "- Run timestamp (UTC): %s" % r.get("run_timestamp_utc"),
             "- Git HEAD: `%s`" % r.get("git_head"),
             "- Origin: `%s`" % r.get("git_origin"),
             "- In sync: %s (ahead %s / behind %s)" % (r.get("in_sync"),
                                                       r.get("ahead"), r.get("behind")),
             "- Tree clean: %s | safe to automate: %s" % (r.get("tree_clean"),
                                                          r.get("git_safe_to_automate")),
             ""]
    section = r.get("v2_morning_section") or {}
    lines.append(_mi.render_v2_section_markdown(section))
    lines.append("")
    lines.append("## Runner safety")
    for s in (r.get("runner_safety_display") or []):
        lines.append("- %s" % s)
    return "\n".join(lines)


# --- a fixed, SHA-pinned SAMPLE for determinism verification ----------------
SAMPLE_TIMESTAMP = "2026-06-20T00:00:00Z"
SAMPLE_REPO_STATE = {
    "head": "0609d626348fcaf96060144e2384001ee055deec",
    "origin": "0609d626348fcaf96060144e2384001ee055deec",
    "ahead": 0, "behind": 0, "clean": True, "staged_count": 0,
    "untracked_clutter_present": True, "untracked_clutter_ignored_by_path": True,
}
# sha256 of render_daily_report_markdown(build_sample_report()); pinned for determinism.
SAMPLE_MARKDOWN_SHA256 = (
    "e05862f16b89240676a8eaeeec6ddb74b42357c1443ae3e0731b48ef7c8b0b30")


def build_sample_report() -> dict[str, Any]:
    """PURE. The fixed sample daily report (SAMPLE_REPO_STATE + SAMPLE_TIMESTAMP)."""
    return build_daily_report(dict(SAMPLE_REPO_STATE), SAMPLE_TIMESTAMP)


def validate_daily_report(report: dict) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the report is research-only, read-only,
    recommends-only; carries the run timestamp + git facts; surfaces the candidate state +
    (while blocked) the C22 DATA_NOT_READY DATASET-STAGING recommendation (never labels,
    never fabricate data); the C1-C21 (26) ledger; the danger-lock + runner-safety
    displays with every dangerous channel locked; targets the GITIGNORED artifact path
    (never committed to git); and pins every capability flag False."""
    failures: list = []
    if report.get("mode") != DR_MODE:
        failures.append("mode_not_research_only")
    if report.get("is_read_only_report") is not True:
        failures.append("not_read_only_report")
    if report.get("recommends_only") is not True:
        failures.append("not_recommends_only")
    if report.get("executes_nothing") is not True:
        failures.append("executes_something")

    # run + git facts present
    if not report.get("run_timestamp_utc"):
        failures.append("run_timestamp_missing")
    if "git_head" not in report:
        failures.append("git_head_missing")

    # artifact targets the gitignored reports path, never committed
    art = report.get("artifact") or {}
    if art.get("dir") != ARTIFACT_DIR:
        failures.append("artifact_dir_wrong")
    if not str(art.get("dir", "")).startswith("reports/"):
        failures.append("artifact_not_under_reports")
    if art.get("gitignored") is not True:
        failures.append("artifact_not_gitignored")
    if art.get("committed_to_git") is not False:
        failures.append("artifact_must_not_be_committed")

    # ledger + candidate state surfaced
    if report.get("rejected_ledger_count") != 26:
        failures.append("ledger_not_26")
    if not report.get("candidate_status_line"):
        failures.append("candidate_status_line_missing")
    if not report.get("last_verdict"):
        failures.append("last_verdict_missing")

    # C22 DATA_NOT_READY -> dataset staging only, never labels / fabricate. The STAGING
    # recommendation governs only when the repo is SAFE + not ahead (a dirty repo or a
    # pending push legitimately takes higher priority -- RESOLVE_REPO / PUSH); but the
    # report must NEVER claim labels or recommend advancing to labels while blocked.
    if report.get("c22_data_not_ready") is True:
        git_safe = (report.get("git_safe_to_automate") is True
                    and int(report.get("ahead", 0) or 0) == 0)
        if git_safe and report.get("recommended_gate_kind") != _mi._v2.REC_STAGE_DATA:
            failures.append("blocked_must_recommend_staging_when_repo_safe")
        if report.get("recommended_gate_kind") == _mi._v2.REC_ADVANCE and git_safe:
            failures.append("must_not_advance_while_data_not_ready")
        if report.get("do_not_proceed_to_labels") is not True:
            failures.append("must_say_do_not_proceed_to_labels")
        if report.get("do_not_fabricate_data") is not True:
            failures.append("must_say_do_not_fabricate_data")
        if report.get("recommends_advancing_to_labels_while_blocked") is not False:
            failures.append("must_not_advance_to_labels_while_blocked")
        tok = report.get("next_human_approval_token") or ""
        if "STAGE_FROZEN_TREND_RADAR_GC_DETECTOR_DATASET" not in tok:
            failures.append("next_token_not_dataset_staging")

    # danger-lock + runner-safety displays
    dl = report.get("danger_locks") or {}
    for k in ("live_trading_locked", "paper_trading_locked", "broker_locked",
              "signum_locked", "mcp_locked", "hyperliquid_locked", "scheduler_locked",
              "bot_edits_locked", "trades_locked", "no_automatic_commit",
              "no_automatic_push", "no_automatic_data_fetch", "never_skips_human_gates"):
        if dl.get(k) is not True:
            failures.append("danger_lock_off_%s" % k)
    rsf = report.get("runner_safety") or {}
    for k in ("read_only", "no_git_commit", "no_git_push", "no_git_fetch",
              "no_data_fetch", "no_scheduler_install", "no_scheduler_trigger",
              "writes_only_to_gitignored_reports_path", "artifact_not_committed_to_git"):
        if rsf.get(k) is not True:
            failures.append("runner_safety_off_%s" % k)

    # the embedded section is itself valid
    if not _mi.validate_v2_morning_section(
            report.get("v2_morning_section") or {})["valid"]:
        failures.append("embedded_v2_section_invalid")

    # the rendered markdown surfaces the key facts
    md = report.get("report_markdown") or ""
    for must in ("Automation V2", "Daily Decision Report", "Runner safety"):
        if must not in md:
            failures.append("markdown_missing_%s" % must.split()[0])

    locks = report.get("scope_locks") or {}
    for key in ("no_execute", "no_git_io", "no_git_commit", "no_git_push",
                "no_git_fetch", "no_broad_git_add", "no_data_fetch", "no_stage_dataset",
                "no_start_labels", "no_replay", "no_modify_strategy_rules",
                "no_start_c23", "no_reopen_closed_candidate", "no_signum", "no_mcp",
                "no_hyperliquid", "no_scheduler_install", "no_scheduler_trigger",
                "no_auto_advance", "no_commit_artifact"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if report.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
