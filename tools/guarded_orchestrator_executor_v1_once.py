"""Guarded Orchestrator Executor v1 -- ONE-OFF TOOL (DISABLED BY DEFAULT).

A one-off, human-run command-line tool that EXECUTES an already runner-APPROVED,
explicitly human-AUTHORIZED bounded research unit through the same gates the Guarded
Orchestrator Executor v1 CONTRACT declares: safety precheck -> run declared tests ->
explicit-path `git add` (allowlist only) -> `git commit -F` declared message ->
`git push origin master` -> post-push verification -> final report.

HARD SAFETY POSTURE:
  * DISABLED BY DEFAULT. It does nothing unless `enabled=True` (CLI: --enable) is
    explicitly passed, together with explicit human authorization and the separate
    EXECUTION_TOKEN.
  * It is NOT a scheduler and is never wired to run automatically / overnight. It is
    a single manual invocation that exits when done.
  * Every execution is gated by the Executor v1 CONTRACT's authorize_execution(),
    which re-derives the plan from the dry-run runner, so a hand-edited request
    cannot smuggle anything past it. The tool performs side effects ONLY when the
    contract returns AUTHORIZED_TO_EXECUTE.
  * It stops at the FIRST failed gate or failed command and performs no further side
    effects.

It REFUSES (no side effects) for: new-candidate / C19 start, advance/reject, network
fetch execution, labels->replay advance, replay-verdict decisions, optimization/
rescue/tuning, XAUUSD / any new instrument class, scheduler changes, credentials /
private APIs, all paper/live/broker/order/trading code, broad staging, unexpected
files, un-exempted data/report artifacts, a dirty tracked tree, SHA drift, and
failing or un-run tests. Pre-existing untracked clutter is tolerated only because
staging is explicit per-path.

TESTABILITY: all side effects go through an injected `command_runner(cmd, cwd)` and
an explicit `repo_root`. The safety test suite injects a FAKE runner and a temp repo
so it NEVER runs real git and NEVER mutates the real repository. The real subprocess
runner is used only by main() at the actual command line.
"""
from __future__ import annotations

import json
import subprocess
import sys
from typing import Any, Callable

import sparta_commander.guarded_orchestrator_executor_v1_contract as _goe

TOOL_NAME = "guarded_orchestrator_executor_v1_once"
ENABLED_BY_DEFAULT = False           # the whole point: off unless explicitly enabled
IS_SCHEDULER = False
RUNS_OVERNIGHT = False

# Execution outcomes.
OUTCOME_DISABLED = "DISABLED_NO_OP"
OUTCOME_REFUSED = "REFUSED_STOP_FOR_HUMAN"
OUTCOME_DRY_RUN = "DRY_RUN_PLAN_ONLY"
OUTCOME_EXECUTED = "EXECUTED"

CommandRunner = Callable[[list, str], dict]


def _real_command_runner(cmd: list, cwd: str) -> dict:
    """The REAL runner (subprocess). Used only by main() at the command line; the
    tests inject a fake instead and never call this."""
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return {"returncode": proc.returncode, "stdout": proc.stdout,
            "stderr": proc.stderr}


def gather_live_precheck(repo_root: str, expected_files: list,
                         runner: CommandRunner) -> dict[str, Any]:
    """Read the LIVE git state via the injected runner and derive the precheck
    booleans. clean_working_tree here means a clean TRACKED tree (no tracked
    modifications OUTSIDE the declared allowlist); untracked clutter is tolerated."""
    expected = {str(f).replace("\\", "/") for f in (expected_files or [])}
    head = runner(["git", "rev-parse", "HEAD"], repo_root)
    origin = runner(["git", "rev-parse", "origin/master"], repo_root)
    status = runner(["git", "status", "--porcelain"], repo_root)

    head_sha = (head.get("stdout") or "").strip()
    origin_sha = (origin.get("stdout") or "").strip()

    changed_tracked: list = []
    untracked: list = []
    for line in (status.get("stdout") or "").splitlines():
        if not line.strip():
            continue
        code, _, name = line.partition(" ")
        path = line[3:].strip() if len(line) > 3 else name.strip()
        path = path.replace("\\", "/")
        if line.startswith("??"):
            untracked.append(path)
        else:
            changed_tracked.append(path)

    unexpected_tracked = [p for p in changed_tracked if p not in expected]
    return {
        "head_sha": head_sha, "origin_sha": origin_sha,
        "head_equals_origin_master": bool(head_sha) and head_sha == origin_sha,
        "clean_working_tree": len(unexpected_tracked) == 0,
        "expected_files_only": len(unexpected_tracked) == 0,
        "no_mutating_shell_pending": True,
        "untracked_clutter_present": len(untracked) > 0,
        "unexpected_tracked": unexpected_tracked,
        "changed_tracked": changed_tracked,
    }


def run_declared_tests(test_files: list, repo_root: str,
                       runner: CommandRunner) -> dict[str, Any]:
    """Run the declared test files via the injected runner (read-only w.r.t. the
    repo). Returns {ran, passed, returncode}."""
    files = [str(t) for t in (test_files or [])]
    if not files:
        return {"ran": False, "passed": False, "returncode": None,
                "note": "no_test_files_declared"}
    cmd = (["python", "-m", "pytest"] + files
           + ["-q", "-p", "no:cacheprovider", "--rootdir=tests"])
    res = runner(cmd, repo_root)
    rc = res.get("returncode")
    return {"ran": rc is not None, "passed": rc == 0, "returncode": rc,
            "command": " ".join(cmd)}


def _build_request(plan_spec: dict, precheck: dict, tests_result: dict,
                   human_authorized: bool, execution_token: str) -> dict:
    unit = {
        "category": plan_spec.get("category"),
        "description": plan_spec.get("description"),
        "expected_files": plan_spec.get("expected_files") or [],
        "relevant_tests": plan_spec.get("relevant_tests") or [],
        "precheck": {
            "clean_working_tree": precheck.get("clean_working_tree"),
            "head_equals_origin_master": precheck.get("head_equals_origin_master"),
            "no_mutating_shell_pending": precheck.get("no_mutating_shell_pending"),
            "expected_files_only": precheck.get("expected_files_only"),
        },
        "tests": {"ran": tests_result.get("ran"),
                  "passed": tests_result.get("passed")},
        "staging_command": plan_spec.get("staging_command"),
        "staged_files": plan_spec.get("expected_files") or [],
        "exemptions": plan_spec.get("exemptions") or [],
        "commit_message_ref": plan_spec.get("commit_message_ref"),
        "untracked_clutter_present": precheck.get("untracked_clutter_present"),
    }
    return {"unit": unit, "mode": "execute",
            "human_authorized": bool(human_authorized),
            "execution_token": execution_token}


def _structural_refusal(plan_spec: dict) -> list:
    """Detect HARD (non-test) refusals BEFORE running tests, by re-deriving the plan
    with optimistic precheck/tests. Returns the structural refusal reasons (category,
    broad staging, unexpected files, artifacts, missing allowlist) -- but NOT
    test/precheck-state reasons, which are evaluated live afterwards."""
    import sparta_commander.guarded_orchestrator_runner_v1_contract as _gor
    unit = {
        "category": plan_spec.get("category"),
        "expected_files": plan_spec.get("expected_files") or [],
        "relevant_tests": plan_spec.get("relevant_tests") or [],
        "precheck": {"clean_working_tree": True, "head_equals_origin_master": True,
                     "no_mutating_shell_pending": True, "expected_files_only": True},
        "tests": {"ran": True, "passed": True},
        "staging_command": plan_spec.get("staging_command"),
        "staged_files": plan_spec.get("expected_files") or [],
        "exemptions": plan_spec.get("exemptions") or [],
        "commit_message_ref": plan_spec.get("commit_message_ref"),
        "untracked_clutter_present": False,
    }
    plan = _gor.plan_bounded_research_unit(unit)
    return list(plan.get("refusal_reasons") or [])


def execute_bounded_plan(plan_spec: dict, *, enabled: bool = ENABLED_BY_DEFAULT,
                         human_authorized: bool = False,
                         execution_token: str | None = None,
                         repo_root: str = ".",
                         command_runner: CommandRunner = _real_command_runner
                         ) -> dict[str, Any]:
    """Run the gated bounded plan. Performs git side effects ONLY when DISABLED is
    off, the structural gates pass, the live precheck is clean, the declared tests
    pass, and the Executor v1 contract returns AUTHORIZED_TO_EXECUTE. Stops at the
    first failure. All side effects go through `command_runner`/`repo_root` so this
    is fully testable without touching the real repo."""
    report: dict[str, Any] = {
        "tool": TOOL_NAME, "enabled": bool(enabled),
        "is_scheduler": IS_SCHEDULER, "runs_overnight": RUNS_OVERNIGHT,
        "outcome": None, "refusal_reasons": [], "phases_performed": [],
        "files_changed": list(plan_spec.get("expected_files") or []),
        "tests_result": None, "authorization_decision": None,
        "commit_hash": None, "push_result": None,
        "head_equals_origin_master": None, "ahead_behind": None,
        "executed_side_effects": False,
    }

    # GATE 0: disabled by default
    if not enabled:
        report["outcome"] = OUTCOME_DISABLED
        report["refusal_reasons"] = ["tool_disabled_by_default"]
        return report

    # GATE 1: structural refusals (category / broad staging / artifacts / allowlist)
    structural = _structural_refusal(plan_spec)
    if structural:
        report["outcome"] = OUTCOME_REFUSED
        report["refusal_reasons"] = structural
        return report

    # GATE 2: live precheck (clean tracked tree + HEAD == origin/master)
    precheck = gather_live_precheck(
        repo_root, plan_spec.get("expected_files") or [], command_runner)
    report["head_equals_origin_master"] = precheck["head_equals_origin_master"]
    report["phases_performed"].append("safety_precheck")
    if not precheck["clean_working_tree"]:
        report["outcome"] = OUTCOME_REFUSED
        report["refusal_reasons"] = ["dirty_tracked_tree",
                                     *("unexpected:%s" % p
                                       for p in precheck["unexpected_tracked"])]
        return report
    if not precheck["head_equals_origin_master"]:
        report["outcome"] = OUTCOME_REFUSED
        report["refusal_reasons"] = ["sha_drift_head_not_origin_master"]
        return report

    # GATE 3: run declared tests BEFORE staging
    tests_result = run_declared_tests(
        plan_spec.get("relevant_tests") or [], repo_root, command_runner)
    report["tests_result"] = tests_result
    report["phases_performed"].append("run_declared_tests")
    if not (tests_result.get("ran") and tests_result.get("passed")):
        report["outcome"] = OUTCOME_REFUSED
        report["refusal_reasons"] = ["failing_or_unrun_tests"]
        return report

    # GATE 4: contract authorization (separate token + human auth + approved plan)
    request = _build_request(plan_spec, precheck, tests_result,
                             human_authorized, execution_token)
    auth = _goe.authorize_execution(request)
    report["authorization_decision"] = auth["decision"]
    if auth["decision"] == _goe.DECISION_REFUSED:
        report["outcome"] = OUTCOME_REFUSED
        report["refusal_reasons"] = auth["refusal_reasons"]
        return report
    if auth["decision"] != _goe.DECISION_AUTHORIZED_TO_EXECUTE:
        report["outcome"] = OUTCOME_DRY_RUN
        report["refusal_reasons"] = auth.get("dry_run_reasons") or [
            "not_authorized_default_dry_run"]
        return report

    # AUTHORIZED -> perform the bounded side effects, stopping at first failure.
    expected_files = plan_spec.get("expected_files") or []
    msg_ref = plan_spec.get("commit_message_ref")

    # phase: explicit-path git add (allowlist only) -- one explicit add, no globs
    add_cmd = ["git", "add", "--"] + [str(f) for f in expected_files]
    add = command_runner(add_cmd, repo_root)
    report["phases_performed"].append("explicit_path_git_add_allowlist_only")
    if add.get("returncode") not in (0, None):
        report["outcome"] = OUTCOME_REFUSED
        report["refusal_reasons"] = ["git_add_failed", add.get("stderr", "")]
        report["executed_side_effects"] = True
        return report

    # phase: commit with declared message
    commit = command_runner(["git", "commit", "-F", str(msg_ref)], repo_root)
    report["phases_performed"].append("git_commit_declared_message")
    report["executed_side_effects"] = True
    if commit.get("returncode") not in (0, None):
        report["outcome"] = OUTCOME_REFUSED
        report["refusal_reasons"] = ["git_commit_failed", commit.get("stderr", "")]
        return report

    head_after = command_runner(["git", "rev-parse", "HEAD"], repo_root)
    report["commit_hash"] = (head_after.get("stdout") or "").strip()

    # phase: push
    push = command_runner(["git", "push", "origin", "master"], repo_root)
    report["phases_performed"].append("git_push_origin_master")
    if push.get("returncode") not in (0, None):
        report["outcome"] = OUTCOME_REFUSED
        report["refusal_reasons"] = ["git_push_failed", push.get("stderr", "")]
        return report
    report["push_result"] = (push.get("stdout", "") + push.get("stderr", "")).strip()

    # phase: post-push verification (HEAD == origin/master, ahead/behind 0/0)
    verify_head = command_runner(["git", "rev-parse", "HEAD"], repo_root)
    verify_origin = command_runner(["git", "rev-parse", "origin/master"], repo_root)
    ab = command_runner(
        ["git", "rev-list", "--left-right", "--count", "origin/master...HEAD"],
        repo_root)
    in_sync = ((verify_head.get("stdout") or "").strip()
               == (verify_origin.get("stdout") or "").strip())
    report["head_equals_origin_master"] = in_sync
    report["ahead_behind"] = (ab.get("stdout") or "").strip()
    report["phases_performed"].append("post_push_verification")
    if not in_sync:
        report["outcome"] = OUTCOME_REFUSED
        report["refusal_reasons"] = ["post_push_not_in_sync"]
        return report

    # phase: final report
    report["phases_performed"].append("final_report")
    report["outcome"] = OUTCOME_EXECUTED
    return report


def main(argv: list | None = None) -> int:
    """Command-line entry point. DISABLED BY DEFAULT: requires --enable plus explicit
    human authorization (--i-am-human-authorized) and --execution-token. Reads the
    plan spec from --plan-file (JSON). Uses the REAL subprocess runner."""
    import argparse
    parser = argparse.ArgumentParser(
        description="Guarded Orchestrator Executor v1 -- one-off, DISABLED BY "
                    "DEFAULT. Executes a runner-approved, human-authorized bounded "
                    "research unit.")
    parser.add_argument("--plan-file", required=True,
                        help="JSON file with the bounded research-unit plan spec")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--enable", action="store_true",
                        help="REQUIRED to do anything (disabled by default)")
    parser.add_argument("--i-am-human-authorized", action="store_true",
                        help="explicit human authorization")
    parser.add_argument("--execution-token", default=None,
                        help="the separate EXECUTION_TOKEN")
    args = parser.parse_args(argv)

    with open(args.plan_file, encoding="utf-8") as fh:
        plan_spec = json.load(fh)

    report = execute_bounded_plan(
        plan_spec,
        enabled=args.enable,
        human_authorized=args.i_am_human_authorized,
        execution_token=args.execution_token,
        repo_root=args.repo_root,
        command_runner=_real_command_runner,
    )
    print(json.dumps(report, indent=2))
    return 0 if report["outcome"] in (OUTCOME_EXECUTED, OUTCOME_DISABLED,
                                      OUTCOME_DRY_RUN) else 1


if __name__ == "__main__":
    sys.exit(main())
