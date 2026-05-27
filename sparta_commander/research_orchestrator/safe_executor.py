"""Approval-level-gated action runner.

Refuses on policy violations. Never auto-escalates approval level. Never
runs strategy diagnostics or fetches data, ever.

Approval levels:
    LEVEL_0 — read-only auto (no operator approval needed)
    LEVEL_1 — housekeeping (delete exact untracked tmp helpers / unstage exact paths)
    LEVEL_2 — memo authoring + commit of exact paths only
    LEVEL_3 — real diagnostic execution (P6 IS / P6.5 / P10 / real CSV read /
              Databento fetch) — IMPLEMENTED AS REFUSAL in this version,
              because the orchestrator never runs strategy diagnostics itself.
              Operator runs diagnostics manually; orchestrator only audits.
"""

from __future__ import annotations

import json
import pathlib
import subprocess
from dataclasses import dataclass, field
from typing import Any, Callable

from .git_sentinel import PROTECTED_FILES_NEVER_TOUCH, staged_files
from .state import HARD_GUARD_FORBIDDEN_ALWAYS


LEVEL_0_READ_ONLY = 0
LEVEL_1_HOUSEKEEPING = 1
LEVEL_2_MEMO_COMMIT = 2
LEVEL_3_REAL_DIAGNOSTIC = 3


@dataclass
class ExecutionResult:
    status: str  # OK | REFUSED | FAILED
    action: str
    reason: str
    artifacts: dict[str, Any] = field(default_factory=dict)
    refused_because: str | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "action": self.action,
            "reason": self.reason,
            "artifacts": self.artifacts,
            "refused_because": self.refused_because,
            "error": self.error,
        }


def _refuse(action: str, reason: str, refused_because: str) -> ExecutionResult:
    return ExecutionResult(
        status="REFUSED", action=action, reason=reason, refused_because=refused_because
    )


def _check_lessons_md_not_staged(repo: pathlib.Path) -> str | None:
    """Return an error reason if lessons.md is staged. None if clean."""
    try:
        staged = staged_files(repo)
    except RuntimeError as e:
        return f"git error checking staged: {e!s}"
    for path in PROTECTED_FILES_NEVER_TOUCH:
        if path in staged:
            return f"protected file staged: {path}"
    return None


def _check_no_unexpected_staged(repo: pathlib.Path, expected_paths: list[str]) -> str | None:
    """Return an error reason if index contains anything outside expected_paths."""
    try:
        staged = staged_files(repo)
    except RuntimeError as e:
        return f"git error checking staged: {e!s}"
    expected_set = set(expected_paths)
    unexpected = [p for p in staged if p not in expected_set]
    if unexpected:
        return f"unexpected staged files: {unexpected}"
    return None


# ---- LEVEL_0: read-only actions (orchestration only; no side effects) ----

def execute_read_only(
    action: str, reason: str, fn: Callable[[], dict[str, Any]]
) -> ExecutionResult:
    """Run a side-effect-free function and wrap its result."""
    try:
        artifacts = fn()
    except (RuntimeError, ValueError, OSError) as e:
        return ExecutionResult(
            status="FAILED", action=action, reason=reason, error=str(e)
        )
    return ExecutionResult(status="OK", action=action, reason=reason, artifacts=artifacts)


# ---- LEVEL_1: housekeeping ----

def execute_delete_untracked_helper(
    repo: pathlib.Path, path: str, approval_level: int
) -> ExecutionResult:
    """Delete one exact untracked file. Refuses if path looks unsafe."""
    action = "DELETE_UNTRACKED_HELPER"
    reason = f"delete untracked author helper: {path}"
    if approval_level < LEVEL_1_HOUSEKEEPING:
        return _refuse(action, reason, "approval level < LEVEL_1")
    # Hard guards
    if not (path.startswith(".tmp_") or path.endswith(".tmp_helper.py")):
        return _refuse(action, reason, "path does not look like a .tmp_ author helper")
    if any(g in path.lower() for g in ("lessons.md", "trading_bot", "broker", "live", "paper")):
        return _refuse(action, reason, "path matches a hard-guarded substring")
    full = pathlib.Path(repo) / path
    if not full.exists():
        return ExecutionResult(status="OK", action=action, reason=reason,
                              artifacts={"already_absent": True, "path": path})
    # Verify it's untracked
    try:
        from .git_sentinel import untracked_files
        if path not in untracked_files(pathlib.Path(repo)):
            return _refuse(action, reason, "path is tracked or staged; refuse to delete")
    except RuntimeError as e:
        return ExecutionResult(status="FAILED", action=action, reason=reason, error=str(e))
    try:
        full.unlink()
    except OSError as e:
        return ExecutionResult(status="FAILED", action=action, reason=reason, error=str(e))
    return ExecutionResult(
        status="OK", action=action, reason=reason,
        artifacts={"deleted": path, "absolute_path": str(full)}
    )


def execute_unstage_exact(
    repo: pathlib.Path, paths: list[str], approval_level: int
) -> ExecutionResult:
    """Index-only unstage. Preserves working-tree bytes. Refuses on protected paths."""
    action = "UNSTAGE_EXACT"
    reason = f"index-only unstage of {len(paths)} explicit paths"
    if approval_level < LEVEL_1_HOUSEKEEPING:
        return _refuse(action, reason, "approval level < LEVEL_1")
    for p in paths:
        if p in PROTECTED_FILES_NEVER_TOUCH:
            return _refuse(action, reason, f"refuse to touch protected path: {p}")
        if any(g in p.lower() for g in ("lessons.md", "broker", "live_trading", "paper_trading")):
            return _refuse(action, reason, f"path matches a hard-guarded substring: {p}")
    try:
        subprocess.run(
            ["git", "-C", str(repo), "restore", "--staged"] + paths,
            check=True, capture_output=True, text=True,
        )
    except subprocess.CalledProcessError as e:
        return ExecutionResult(
            status="FAILED", action=action, reason=reason,
            error=f"git restore --staged failed: {e.stderr.strip()}"
        )
    return ExecutionResult(
        status="OK", action=action, reason=reason,
        artifacts={"unstaged": paths}
    )


# ---- LEVEL_2: memo authoring + commit ----

def execute_write_memo_pair(
    repo: pathlib.Path, json_path: str, json_body: dict[str, Any], md_path: str,
    md_content: str, approval_level: int
) -> ExecutionResult:
    """Write a JSON+MD pair to disk. Does NOT stage or commit."""
    action = "WRITE_MEMO_PAIR"
    reason = f"write sealed memo pair to {json_path} + {md_path}"
    if approval_level < LEVEL_2_MEMO_COMMIT:
        return _refuse(action, reason, "approval level < LEVEL_2")
    for p in (json_path, md_path):
        if p in PROTECTED_FILES_NEVER_TOUCH:
            return _refuse(action, reason, f"protected path: {p}")
        if any(g in p.lower() for g in ("lessons.md", "broker", "live_trading", "paper_trading")):
            return _refuse(action, reason, f"path matches a hard-guarded substring: {p}")
        full = pathlib.Path(repo) / p
        if full.exists():
            return _refuse(action, reason, f"path already exists; refuse to overwrite: {p}")

    json_full = pathlib.Path(repo) / json_path
    md_full = pathlib.Path(repo) / md_path
    json_full.parent.mkdir(parents=True, exist_ok=True)
    md_full.parent.mkdir(parents=True, exist_ok=True)
    try:
        json_full.write_text(
            json.dumps(json_body, indent=2, ensure_ascii=False, default=str) + "\n",
            encoding="utf-8",
        )
        md_full.write_text(md_content, encoding="utf-8")
    except OSError as e:
        return ExecutionResult(status="FAILED", action=action, reason=reason, error=str(e))
    return ExecutionResult(
        status="OK", action=action, reason=reason,
        artifacts={"json_path": json_path, "md_path": md_path,
                  "json_bytes": json_full.stat().st_size,
                  "md_bytes": md_full.stat().st_size}
    )


def execute_commit_exact_paths(
    repo: pathlib.Path, paths: list[str], commit_message: str, approval_level: int
) -> ExecutionResult:
    """Stage exact paths only + commit. Refuses if:
       - any path is hard-guarded
       - index is not clean before stage
       - any unexpected file remains staged after our stage
       - lessons.md is anywhere in index
    """
    action = "COMMIT_EXACT_PATHS"
    reason = f"stage + commit exactly {len(paths)} path(s)"
    if approval_level < LEVEL_2_MEMO_COMMIT:
        return _refuse(action, reason, "approval level < LEVEL_2")

    # Hard-guard path checks
    for p in paths:
        if p in PROTECTED_FILES_NEVER_TOUCH:
            return _refuse(action, reason, f"refuse to stage protected path: {p}")
        if any(g in p.lower() for g in ("lessons.md", "broker", "live_trading", "paper_trading")):
            return _refuse(action, reason, f"path matches a hard-guarded substring: {p}")
        full = pathlib.Path(repo) / p
        if not full.exists():
            return _refuse(action, reason, f"path does not exist; refuse to stage: {p}")

    # Index must be clean before we start
    err = _check_no_unexpected_staged(pathlib.Path(repo), [])
    if err:
        return _refuse(action, reason, f"index not clean before stage: {err}")

    # Stage exact paths
    try:
        subprocess.run(
            ["git", "-C", str(repo), "add"] + paths,
            check=True, capture_output=True, text=True,
        )
    except subprocess.CalledProcessError as e:
        return ExecutionResult(
            status="FAILED", action=action, reason=reason,
            error=f"git add failed: {e.stderr.strip()}"
        )

    # Confirm exactly the expected paths are staged
    err = _check_no_unexpected_staged(pathlib.Path(repo), paths)
    if err:
        # Best effort: try to leave the index empty for the next attempt
        try:
            subprocess.run(
                ["git", "-C", str(repo), "restore", "--staged"] + paths,
                check=False, capture_output=True, text=True,
            )
        except (subprocess.SubprocessError, OSError):
            pass
        return _refuse(action, reason, f"unexpected staged set after add: {err}")

    err = _check_lessons_md_not_staged(pathlib.Path(repo))
    if err:
        return _refuse(action, reason, err)

    # Commit
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), "commit", "-m", commit_message],
            check=True, capture_output=True, text=True,
        )
        new_head = subprocess.run(
            ["git", "-C", str(repo), "log", "-1", "--format=%H"],
            check=True, capture_output=True, text=True,
        ).stdout.strip()
    except subprocess.CalledProcessError as e:
        return ExecutionResult(
            status="FAILED", action=action, reason=reason,
            error=f"git commit failed: {e.stderr.strip()}"
        )

    return ExecutionResult(
        status="OK", action=action, reason=reason,
        artifacts={"committed_paths": paths, "new_head_sha": new_head,
                  "commit_message": commit_message, "stdout": result.stdout}
    )


# ---- LEVEL_3: real diagnostic execution — REFUSED in v2 ----

def execute_real_diagnostic(action: str, reason: str, approval_level: int) -> ExecutionResult:
    """The orchestrator does NOT run strategy diagnostics. Always refuses.

    Operator runs P6 IS / P6.5 / P10 / data fetches manually outside the
    orchestrator. The orchestrator only audits the resulting committed
    sealed reports.
    """
    return _refuse(
        action, reason,
        "LEVEL_3 diagnostic execution is not implemented by the orchestrator. "
        "Operator runs real diagnostics manually outside this system; "
        "orchestrator audits the resulting committed sealed reports. "
        f"approval_level={approval_level} (would be insufficient regardless)"
    )


# ---- Action dispatch table ----

def dispatch(
    action: str,
    payload: dict[str, Any],
    approval_level: int,
    repo: str | pathlib.Path,
) -> ExecutionResult:
    """Route an approved action to its implementation.

    `payload` is the pending-decision dict (with at least 'action' key).
    """
    repo_path = pathlib.Path(repo)
    reason = payload.get("reason", action)

    # Universal hard-guard check
    for guard in HARD_GUARD_FORBIDDEN_ALWAYS:
        if guard in payload.get("forbidden_overrides", []):
            return _refuse(action, reason, f"refused: hard-guard override attempted: {guard}")

    if action == "DELETE_UNTRACKED_TMP_HELPER":
        path = payload.get("path", "")
        return execute_delete_untracked_helper(repo_path, path, approval_level)

    if action == "UNSTAGE_EXACT":
        paths = payload.get("paths", [])
        return execute_unstage_exact(repo_path, paths, approval_level)

    if action == "WRITE_MEMO_PAIR":
        return execute_write_memo_pair(
            repo_path,
            payload["json_path"], payload["json_body"],
            payload["md_path"], payload["md_content"],
            approval_level,
        )

    if action == "COMMIT_EXACT_PATHS":
        return execute_commit_exact_paths(
            repo_path,
            payload["paths"], payload["commit_message"],
            approval_level,
        )

    # Anything resembling a real-data action gets refused
    if any(token in action.upper() for token in
           ("RUN_P6", "RUN_P10", "FETCH", "BACKTEST", "DIAGNOSTIC_RUN", "BROKER", "LIVE", "PAPER")):
        return execute_real_diagnostic(action, reason, approval_level)

    return _refuse(action, reason, f"unknown action: {action}")
