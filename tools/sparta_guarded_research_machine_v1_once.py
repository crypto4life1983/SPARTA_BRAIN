"""SPARTA Guarded Research Machine v1 -- RUN-ONCE TOOL (DISABLED BY DEFAULT).

A single, human-run, run-once machine that turns the guarded automation stack into an
operational loop: one explicitly human-approved decision token drives ALL safe bounded
research steps until the next true human gate. It composes, in order, per step:

  * Autopilot Research Orchestrator v2   (the auto-continue / human-stop policy),
  * Guarded Runner v1                    (the dry-run plan for a bounded unit),
  * Guarded Executor v1 contract         (the authorization gate),
  * the disabled-by-default Executor v1 ONCE tool (the real precheck -> tests ->
    explicit-path add -> commit -> push -> verify executor),

and loops: read lane/state -> verify HEAD == origin/master -> verify a clean tracked
tree (untracked clutter tolerated only because staging is explicit-allowlist) -> take
the next DECLARED safe bounded unit -> run it through the executor tool -> record the
commit/push/tests -> verify sync -> continue to the next safe bounded step -> STOP at
the next true human gate, then emit ONE final report.

HARD SAFETY POSTURE:
  * DISABLED BY DEFAULT. It does nothing unless `enabled=True` (CLI: --enable) plus
    explicit human authorization (--i-am-human-authorized) plus a non-empty decision
    token (--decision-token).
  * It is NOT a scheduler and never runs automatically / overnight. It is a single
    manual invocation that exits when it reaches a human gate or the step budget.
  * It NEVER derives a strategy step on its own: it only executes already-built,
    DECLARED bounded units (the same descriptors the Runner/Executor consume). It
    cannot start C20 / a new candidate, advance/reject, fetch data, run replay,
    optimize/tune/rescue, add an instrument class, change a scheduler, touch
    credentials, or write paper/live/broker/order/trading code -- any such unit (or a
    broad-staging / unexpected-file / data-artifact / dirty-tree / SHA-drift /
    failing-test condition) is a HARD STOP, surfaced as the next human token.
  * All side effects go through an injected `command_runner` + `repo_root` and the
    injected executor; the safety test suite drives it entirely against a temp repo
    with fakes and never runs real git.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import sparta_commander.autopilot_research_orchestrator_v2_contract as _aro2  # noqa: E402,E501
import sparta_commander.guarded_orchestrator_executor_v1_contract as _goe  # noqa: E402,E501
import sparta_commander.crypto_d1_candidate_research_lane_status_v1_contract as _lane  # noqa: E402,E501
import tools.guarded_orchestrator_executor_v1_once as _exec_tool  # noqa: E402,E501

REPO_ROOT = Path(__file__).resolve().parents[1]

TOOL_NAME = "sparta_guarded_research_machine_v1_once"
ENABLED_BY_DEFAULT = False
IS_SCHEDULER = False
RUNS_OVERNIGHT = False
DEFAULT_MAX_SAFE_STEPS = 10

# machine outcomes
OUTCOME_DISABLED = "DISABLED_NO_OP"
OUTCOME_REFUSED = "REFUSED_STOP_FOR_HUMAN"
OUTCOME_STOPPED_AT_HUMAN_GATE = "STOPPED_AT_HUMAN_GATE"
OUTCOME_STOPPED_ON_GUARD = "STOPPED_ON_GUARD_REFUSAL"
OUTCOME_STEP_BUDGET_REACHED = "STEP_BUDGET_REACHED"

CommandRunner = Callable[[list, str], dict]


def _real_command_runner(cmd: list, cwd: str) -> dict:
    """REAL runner (subprocess) -- only used by main() at the command line; tests
    inject a fake and never call this."""
    import subprocess
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return {"returncode": proc.returncode, "stdout": proc.stdout,
            "stderr": proc.stderr}


def _sync_precheck(repo_root: str, runner: CommandRunner) -> dict[str, Any]:
    """Read live git state: HEAD == origin/master and a clean TRACKED tree (untracked
    clutter tolerated)."""
    head = (runner(["git", "rev-parse", "HEAD"], repo_root).get("stdout") or "").strip()
    origin = (runner(["git", "rev-parse", "origin/master"], repo_root).get("stdout")
              or "").strip()
    status = runner(["git", "status", "--porcelain"], repo_root).get("stdout") or ""
    tracked_changes, untracked = [], []
    for line in status.splitlines():
        if not line.strip():
            continue
        (untracked if line.startswith("??") else tracked_changes).append(
            line[3:].strip())
    return {
        "head": head, "origin": origin,
        "head_equals_origin_master": bool(head) and head == origin,
        "clean_tracked_tree": len(tracked_changes) == 0,
        "untracked_clutter_present": len(untracked) > 0,
        "tracked_changes": tracked_changes,
    }


def _next_human_token() -> dict[str, Any]:
    """Read the lane (pure) and report the next true human gate. With no active
    candidate the lane points at automation readiness; opening a new candidate (C20)
    is itself a hard human-stop that this machine can never take on its own."""
    ls = _lane.get_lane_status()
    return {
        "active_candidate": ls.get("active_candidate"),
        "last_rejected_candidate": ls.get("last_rejected_candidate"),
        "rejected_ledger_count": ls.get("rejected_ledger_count"),
        "next_required_action": ls.get("next_required_action"),
        "next_human_token": ls.get("next_required_action"),
        "opening_new_candidate_requires_explicit_token": True,
    }


def run_machine(plan_units: list | None, *, enabled: bool = ENABLED_BY_DEFAULT,
                human_authorized: bool = False, decision_token: str | None = None,
                max_safe_steps: int = DEFAULT_MAX_SAFE_STEPS,
                repo_root: str = ".",
                command_runner: CommandRunner = _real_command_runner,
                executor: Callable | None = None) -> dict[str, Any]:
    """Drive the declared safe bounded units through the guarded executor, one after
    another, stopping at the next human gate. Performs git side effects ONLY through
    the injected executor + command_runner; pure-loops otherwise. Fully testable
    without touching the real repo."""
    executor = executor or _exec_tool.execute_bounded_plan
    plan_units = list(plan_units or [])
    report: dict[str, Any] = {
        "tool": TOOL_NAME, "enabled": bool(enabled),
        "is_scheduler": IS_SCHEDULER, "runs_overnight": RUNS_OVERNIGHT,
        "decision_token_present": bool(decision_token),
        "max_safe_steps": int(max_safe_steps),
        "outcome": None, "refusal_reasons": [],
        "steps": [], "commits": [], "pushes": [], "tests": [],
        "steps_executed": 0,
        "stopped_at_human_gate": False, "stopped_reason": None,
        "next_human": _next_human_token(),
        "executed_side_effects": False,
    }

    # GATE 0: disabled by default
    if not enabled:
        report["outcome"] = OUTCOME_DISABLED
        report["refusal_reasons"] = ["machine_disabled_by_default"]
        return report
    # GATE 1: explicit human authorization + a decision token
    missing = []
    if not human_authorized:
        missing.append("missing_human_authorization")
    if not decision_token:
        missing.append("missing_decision_token")
    if missing:
        report["outcome"] = OUTCOME_REFUSED
        report["refusal_reasons"] = missing
        return report

    budget = max(0, int(max_safe_steps))
    for i, unit in enumerate(plan_units):
        if i >= budget:
            report["outcome"] = OUTCOME_STEP_BUDGET_REACHED
            report["stopped_reason"] = "max_safe_steps_reached"
            return report

        category = (unit or {}).get("category")
        # HARD STOP: any human-stop category (new candidate / advance-reject / fetch /
        # labels->replay / replay verdict / optimization / instrument class /
        # scheduler / credentials / trading) -- the machine never takes these.
        if category in _aro2.HUMAN_STOP_CATEGORIES:
            report["outcome"] = OUTCOME_STOPPED_AT_HUMAN_GATE
            report["stopped_at_human_gate"] = True
            report["stopped_reason"] = "human_stop_category__%s" % category
            return report

        # sync precheck before each step
        pc = _sync_precheck(repo_root, command_runner)
        if not pc["head_equals_origin_master"]:
            report["outcome"] = OUTCOME_STOPPED_ON_GUARD
            report["stopped_reason"] = "sha_drift_head_not_origin_master"
            return report
        if not pc["clean_tracked_tree"]:
            report["outcome"] = OUTCOME_STOPPED_ON_GUARD
            report["stopped_reason"] = "dirty_tracked_tree"
            return report

        # execute the bounded unit through the disabled-by-default executor tool,
        # supplying the executor's separate EXECUTION_TOKEN on the human's behalf.
        res = executor(unit, enabled=True, human_authorized=True,
                       execution_token=_goe.EXECUTION_TOKEN, repo_root=repo_root,
                       command_runner=command_runner)
        report["steps"].append({"category": category, "outcome": res.get("outcome"),
                                "refusal_reasons": res.get("refusal_reasons")})
        if res.get("executed_side_effects"):
            report["executed_side_effects"] = True
        if res.get("outcome") != "EXECUTED":
            report["outcome"] = OUTCOME_STOPPED_ON_GUARD
            report["stopped_reason"] = "executor_did_not_execute"
            report["refusal_reasons"] = res.get("refusal_reasons") or []
            return report

        report["steps_executed"] += 1
        if res.get("commit_hash"):
            report["commits"].append(res["commit_hash"])
        if res.get("push_result") is not None:
            report["pushes"].append(res["push_result"])
        if res.get("tests_result"):
            report["tests"].append(res["tests_result"])

        # post-step sync verify
        pc2 = _sync_precheck(repo_root, command_runner)
        if not pc2["head_equals_origin_master"]:
            report["outcome"] = OUTCOME_STOPPED_ON_GUARD
            report["stopped_reason"] = "post_step_not_in_sync"
            return report

    # all declared safe units done -> the next step is a human decision
    report["outcome"] = OUTCOME_STOPPED_AT_HUMAN_GATE
    report["stopped_at_human_gate"] = True
    report["stopped_reason"] = ("plan_exhausted_next_is_human_decision"
                                if plan_units else "no_safe_bounded_unit_declared")
    return report


def main(argv: list | None = None) -> int:
    """Command-line entry point. DISABLED BY DEFAULT: requires --enable plus explicit
    human authorization (--i-am-human-authorized) plus --decision-token. Reads the
    declared safe bounded units from --plan-file (a JSON list). Uses the REAL
    subprocess runner."""
    import argparse
    parser = argparse.ArgumentParser(
        description="SPARTA Guarded Research Machine v1 -- run-once, DISABLED BY "
                    "DEFAULT. Drives declared safe bounded research units through the "
                    "guarded stack until the next human gate.")
    parser.add_argument("--enable", action="store_true",
                        help="REQUIRED to do anything (disabled by default)")
    parser.add_argument("--i-am-human-authorized", action="store_true",
                        help="explicit human authorization")
    parser.add_argument("--decision-token", default=None,
                        help="the human-approved decision token authorizing this run")
    parser.add_argument("--max-safe-steps", type=int, default=DEFAULT_MAX_SAFE_STEPS)
    parser.add_argument("--plan-file", default=None,
                        help="JSON list of declared safe bounded unit descriptors")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args(argv)

    plan_units: list = []
    if args.plan_file:
        with open(args.plan_file, encoding="utf-8") as fh:
            plan_units = json.load(fh)

    report = run_machine(
        plan_units,
        enabled=args.enable,
        human_authorized=args.i_am_human_authorized,
        decision_token=args.decision_token,
        max_safe_steps=args.max_safe_steps,
        repo_root=args.repo_root,
        command_runner=_real_command_runner,
    )
    print(json.dumps(report, indent=2))
    return 0 if report["outcome"] in (
        OUTCOME_DISABLED, OUTCOME_STOPPED_AT_HUMAN_GATE, OUTCOME_STEP_BUDGET_REACHED
    ) else 1


if __name__ == "__main__":
    sys.exit(main())
