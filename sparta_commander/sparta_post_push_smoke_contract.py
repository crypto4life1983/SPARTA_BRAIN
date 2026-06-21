"""SPARTA POST-PUSH SMOKE -- PURE, READ-ONLY, REPORTING ONLY.

The PURE core that folds the read-only post-push checks (gathered by the runner) into one
consolidated POST_PUSH_SMOKE_OK / POST_PUSH_SMOKE_NEEDS_ATTENTION verdict. It runs NOTHING:
the runner gathers the git facts + Bundle A/C/D findings + the /control route result
read-only and passes them in; this contract performs NO I/O, executes NO task / token / gate,
and modifies nothing.

Checks: repo in-sync (HEAD==origin, ahead/behind 0/0) + clean + no staged + artifact-guard
clean; Bundle A current-state HEALTHY; Bundle C watchdog severity NONE + safety flags
(no rerun / no scheduler change / no token exec); Bundle D lifecycle safety flags (no
candidate advance / no repo modify / no token exec) + a gate present; and the /control route
(HTTP 200, contains the panel + C22 HOLD + watchdog + lifecycle sections, and NO execution
affordances). The watchdog/lifecycle/control safety flags are SAFETY invariants -- a
violation is a hard NEEDS_ATTENTION. Every dangerous capability is pinned False.
"""
from __future__ import annotations

from typing import Any

PS_SCHEMA_VERSION = 1
PS_MODE = "RESEARCH_ONLY"

VERDICT_OK = "POST_PUSH_SMOKE_OK"
VERDICT_ATTENTION = "POST_PUSH_SMOKE_NEEDS_ATTENTION"

_CAPABILITY_FLAGS_FALSE = (
    "executes", "runs_tasks", "reruns_pickup", "reruns_import", "runs_scheduled_task",
    "changes_scheduled_task", "installs_scheduler", "auto_executes_any_token",
    "advances_any_candidate", "opens_c23_as_active", "modifies_repo", "modifies_files",
    "runs_labels", "runs_replay", "optimizes_parameters", "fetches_data",
    "performs_network_io", "connects_signum", "uses_mcp", "calls_api", "places_orders",
    "sends_trades", "paper_trading", "live_trading", "stages_files", "commits", "pushes",
    "crosses_into_forbidden_gate",
)


def _b(x: Any) -> bool:
    return x is True


def build_smoke_report(inputs: dict) -> dict[str, Any]:
    """PURE. Fold the gathered read-only inputs into a consolidated smoke verdict. No I/O."""
    i = dict(inputs or {})
    repo = dict(i.get("repo") or {})
    cs = dict(i.get("current_state") or {})
    wd = dict(i.get("watchdog") or {})
    lo = dict(i.get("lifecycle") or {})
    cr = dict(i.get("control_route") or {})

    in_sync = (repo.get("head") == repo.get("origin")
               and repo.get("ahead") == 0 and repo.get("behind") == 0)
    repo_clean = _b(repo.get("clean")) and (repo.get("staged_count", 0) == 0)
    guard_clean = (_b(i.get("artifact_guard_clean"))
                   and repo.get("dangerous_staged") is False)

    # SAFETY invariants (a violation here is a hard alarm, not a soft state)
    watchdog_safe = (wd.get("reran_any_task") is False
                     and wd.get("changed_any_scheduled_task") is False
                     and wd.get("auto_executes_any_token") is False)
    lifecycle_safe = (lo.get("advances_any_candidate") is False
                      and lo.get("opens_c23_as_active") is False
                      and lo.get("auto_executes_any_token") is False
                      and lo.get("modifies_repo") is False)
    control_no_exec = _b(cr.get("no_execution_affordances"))

    checks = {
        "repo_in_sync": in_sync,
        "repo_clean_no_staged": repo_clean,
        "artifact_guard_clean": guard_clean,
        "current_state_healthy": cs.get("overall_status") == "HEALTHY",
        "watchdog_clear": wd.get("severity") == "NONE",
        "watchdog_safe": watchdog_safe,
        "lifecycle_present": bool(lo.get("current_gate")
                                  and lo.get("suggested_human_token")),
        "lifecycle_safe": lifecycle_safe,
        "control_route_200": cr.get("status_code") == 200,
        "control_panel_present": _b(cr.get("has_control_panel")),
        "control_c22_hold_present": _b(cr.get("has_c22_hold")),
        "control_watchdog_section": _b(cr.get("has_watchdog_section")),
        "control_lifecycle_section": _b(cr.get("has_lifecycle_section")),
        "control_no_execution_affordances": control_no_exec,
    }
    # SAFETY checks (a failure is a critical alarm)
    safety_checks = ("watchdog_safe", "lifecycle_safe",
                     "control_no_execution_affordances")

    failed = [name for name, ok in checks.items() if not ok]
    safety_failed = [name for name in safety_checks if not checks[name]]
    attention_reasons = (["SAFETY:" + n for n in safety_failed]
                         + [n for n in failed if n not in safety_checks])
    overall = VERDICT_OK if not failed else VERDICT_ATTENTION

    record: dict[str, Any] = {
        "schema_version": PS_SCHEMA_VERSION, "mode": PS_MODE,
        "section": "sparta_post_push_smoke",
        "is_read_only_report": True,
        "verdict": overall,
        "overall": overall,
        "all_clear": overall == VERDICT_OK,
        "checks": checks,
        "failed_checks": failed,
        "safety_failed": safety_failed,
        "attention_reasons": attention_reasons,
        # compact echoes of the key facts (display)
        "repo": {"in_sync": in_sync, "clean": repo_clean,
                 "head": repo.get("head"), "ahead": repo.get("ahead"),
                 "behind": repo.get("behind"),
                 "dangerous_staged": repo.get("dangerous_staged")},
        "current_state": {"overall_status": cs.get("overall_status"),
                          "c22_progress": cs.get("c22_progress"),
                          "c22_state": cs.get("c22_state"),
                          "task_health_overall": cs.get("task_health_overall")},
        "watchdog": {"severity": wd.get("severity"),
                     "primary_recommendation": wd.get("primary_recommendation")},
        "lifecycle": {"current_gate": lo.get("current_gate"),
                      "suggested_human_token": lo.get("suggested_human_token")},
        "control_route": {"status_code": cr.get("status_code")},
        # the smoke itself runs nothing
        "executed_no_task": True, "executed_no_token": True, "advanced_no_gate": True,
        "advances_nothing": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_execute": True, "no_run_tasks": True, "no_rerun_pickup": True,
        "no_rerun_import": True, "no_change_scheduled_task": True,
        "no_install_scheduler": True, "no_auto_execute_token": True,
        "no_advance_candidate": True, "no_open_c23_active": True, "no_modify_repo": True,
        "no_modify_files": True, "no_run_labels": True, "no_replay": True,
        "no_optimization": True, "no_data_fetch": True, "no_network_io": True,
        "no_signum_connection": True, "no_mcp": True, "no_order_logic": True,
        "no_paper_trading": True, "no_live_trading": True, "no_stage": True,
        "no_commit": True, "no_push": True, "no_crossing_into_forbidden_gate": True,
    }
    return record


def render_smoke_markdown(report: dict) -> str:
    """PURE. A compact markdown summary."""
    r = report or {}
    lines = ["# SPARTA post-push smoke", "", "**%s**" % r.get("overall")]
    if r.get("attention_reasons"):
        lines.append("- Attention: %s" % ", ".join(r["attention_reasons"]))
    repo = r.get("repo") or {}
    cs = r.get("current_state") or {}
    wd = r.get("watchdog") or {}
    lo = r.get("lifecycle") or {}
    lines += [
        "- Repo: in_sync=%s clean=%s (ahead %s / behind %s) dangerous_staged=%s" % (
            repo.get("in_sync"), repo.get("clean"), repo.get("ahead"),
            repo.get("behind"), repo.get("dangerous_staged")),
        "- Current state: %s | C22 %s / %s | tasks %s" % (
            cs.get("overall_status"), cs.get("c22_progress"), cs.get("c22_state"),
            cs.get("task_health_overall")),
        "- Watchdog: %s (%s)" % (wd.get("severity"), wd.get("primary_recommendation")),
        "- Lifecycle gate: %s -> %s" % (lo.get("current_gate"),
                                        lo.get("suggested_human_token")),
        "- /control: HTTP %s" % (r.get("control_route") or {}).get("status_code"),
    ]
    return "\n".join(lines)


def validate_smoke_report(record: Any) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when research-only, read-only; the overall verdict
    is consistent with the checks (OK iff no failed check); the attention reasons match the
    failed checks; the smoke executed no task/token/gate; and every capability flag is
    False."""
    failures: list = []
    if not isinstance(record, dict):
        return {"valid": False, "failures": ["record_not_a_dict"]}
    r = record

    if r.get("mode") != PS_MODE:
        failures.append("mode_not_research_only")
    if r.get("is_read_only_report") is not True:
        failures.append("not_read_only_report")
    if r.get("overall") not in (VERDICT_OK, VERDICT_ATTENTION):
        failures.append("bad_overall")

    checks = r.get("checks") or {}
    failed = [n for n, ok in checks.items() if not ok]
    if r.get("failed_checks") != failed:
        failures.append("failed_checks_inconsistent")
    if r.get("all_clear") is not (not failed):
        failures.append("all_clear_inconsistent")
    if r.get("overall") != (VERDICT_OK if not failed else VERDICT_ATTENTION):
        failures.append("overall_inconsistent_with_checks")
    # attention reasons must reference real failed checks
    for reason in (r.get("attention_reasons") or []):
        name = reason.split(":", 1)[-1]
        if name not in failed:
            failures.append("attention_reason_not_failed:%s" % name)

    # the smoke itself ran nothing
    for k in ("executed_no_task", "executed_no_token", "advanced_no_gate",
              "advances_nothing"):
        if r.get(k) is not True:
            failures.append("must_be_true_%s" % k)

    locks = r.get("scope_locks") or {}
    for key in ("no_execute", "no_run_tasks", "no_rerun_pickup", "no_rerun_import",
                "no_change_scheduled_task", "no_auto_execute_token", "no_advance_candidate",
                "no_open_c23_active", "no_modify_repo", "no_run_labels", "no_replay",
                "no_data_fetch", "no_network_io", "no_signum_connection", "no_mcp",
                "no_order_logic", "no_paper_trading", "no_live_trading", "no_commit",
                "no_push"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if r.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
