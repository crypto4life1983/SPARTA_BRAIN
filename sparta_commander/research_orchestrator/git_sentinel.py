"""Read-only git inspection.

Watcher pattern: this module NEVER calls git mutating commands
(no add / commit / restore / reset / rm / clean / branch / push / merge).
All functions return plain dicts / lists. Caller may persist.
"""

from __future__ import annotations

import pathlib
import subprocess
from dataclasses import dataclass, field
from typing import Any


# Paths whose modification is hard-guarded across the orchestrator.
PROTECTED_FILES_NEVER_TOUCH = (
    "brain_memory/projects/trading_bot/lessons.md",
    "tmp/build_s12_d1_seal_artifacts.py",
    "tmp/run_s12_d1_p6_is_diagnostic.py",
)

# Slug fragments that identify SEAL-B-style duplicate-chain artifacts.
DUPLICATE_CHAIN_SLUG_HINTS = (
    # short slugs (no `databento_long_history` infix) on top-level reports/
    "/s12_d1_p11_lifecycle_memo_sealed",
    "/s13_d1_p11_lifecycle_memo_sealed",
    "/t1_rsi_mnq_",
    "/s12_d1_mnq_c0_single_instrument_donchian_15_8_in_sample_diagnostic_result_sealed",
    "/s12_d1_mnq_c0_single_instrument_donchian_15_8_smoke_t1_t15_report",
    "/s13_d1_mnq_c0_single_instrument_rsi_2_bi_directional_in_sample_diagnostic_result_sealed",
)


@dataclass
class RepoSnapshot:
    """Point-in-time read of repo state. All fields are static after construction."""

    head_sha: str
    head_subject: str
    recent_commits: list[tuple[str, str]] = field(default_factory=list)  # (sha, subject)
    staged_files: list[str] = field(default_factory=list)
    untracked_files: list[str] = field(default_factory=list)
    modified_files: list[str] = field(default_factory=list)
    dirty_protected_files: list[str] = field(default_factory=list)
    foreign_staged_files: list[str] = field(default_factory=list)
    untracked_tmp_helpers: list[str] = field(default_factory=list)
    duplicate_chain_files: list[str] = field(default_factory=list)
    # Per-protected-file drift detail (populated by caller via protected_drift.scan_protected_drift)
    protected_drift_details: list[dict[str, Any]] = field(default_factory=list)

    def is_clean(self) -> bool:
        return not (
            self.staged_files
            or self.modified_files
            or self.dirty_protected_files
            or self.foreign_staged_files
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "head_sha": self.head_sha,
            "head_subject": self.head_subject,
            "recent_commits": [list(t) for t in self.recent_commits],
            "staged_files": self.staged_files,
            "untracked_files": self.untracked_files,
            "modified_files": self.modified_files,
            "dirty_protected_files": self.dirty_protected_files,
            "foreign_staged_files": self.foreign_staged_files,
            "untracked_tmp_helpers": self.untracked_tmp_helpers,
            "duplicate_chain_files": self.duplicate_chain_files,
            "protected_drift_details": self.protected_drift_details,
        }


def _run(repo: pathlib.Path, args: list[str], check: bool = True) -> str:
    """Read-only git command runner. Refuses any mutating verb."""
    if not args:
        raise ValueError("empty git args")
    forbidden_verbs = {
        "add", "commit", "rm", "reset", "restore", "checkout", "branch",
        "clean", "stash", "merge", "rebase", "push", "tag", "config",
        "init", "clone", "submodule", "fetch", "pull", "mv",
    }
    if args[0] in forbidden_verbs:
        raise PermissionError(f"git_sentinel refuses mutating verb: {args[0]}")
    cmd = ["git", "-C", str(repo)] + args
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if check and result.returncode != 0:
        raise RuntimeError(
            f"git command failed: {' '.join(cmd)}\nstderr: {result.stderr.strip()}"
        )
    return result.stdout


def head_sha(repo: pathlib.Path) -> str:
    return _run(repo, ["log", "-1", "--format=%H"]).strip()


def head_subject(repo: pathlib.Path) -> str:
    return _run(repo, ["log", "-1", "--format=%s"]).strip()


def recent_commits(repo: pathlib.Path, n: int = 10) -> list[tuple[str, str]]:
    out = _run(repo, ["log", f"-{n}", "--format=%H%x09%s"])
    rows: list[tuple[str, str]] = []
    for line in out.splitlines():
        if "\t" not in line:
            continue
        sha, subject = line.split("\t", 1)
        rows.append((sha.strip(), subject.strip()))
    return rows


def staged_files(repo: pathlib.Path) -> list[str]:
    out = _run(repo, ["diff", "--cached", "--name-only"])
    return [p for p in out.splitlines() if p.strip()]


def untracked_files(repo: pathlib.Path) -> list[str]:
    out = _run(
        repo, ["ls-files", "--others", "--exclude-standard"], check=False
    )
    return [p for p in out.splitlines() if p.strip()]


def modified_files(repo: pathlib.Path) -> list[str]:
    out = _run(repo, ["diff", "--name-only"])
    return [p for p in out.splitlines() if p.strip()]


def detect_dirty_protected(
    modified: list[str], staged: list[str],
    protected: tuple[str, ...] = PROTECTED_FILES_NEVER_TOUCH,
) -> list[str]:
    seen = set(modified) | set(staged)
    return [p for p in protected if p in seen]


def detect_foreign_staged(
    staged: list[str], expected_paths: set[str]
) -> list[str]:
    """Returns staged files NOT in the expected_paths whitelist."""
    return [p for p in staged if p not in expected_paths]


def detect_untracked_tmp_helpers(
    untracked: list[str], hints: tuple[str, ...] = (".tmp_", "tmp/build_s", "tmp/run_s")
) -> list[str]:
    out: list[str] = []
    for p in untracked:
        for h in hints:
            if h in p:
                out.append(p)
                break
    return out


def detect_duplicate_chain_files(
    paths: list[str], hints: tuple[str, ...] = DUPLICATE_CHAIN_SLUG_HINTS
) -> list[str]:
    out: list[str] = []
    for p in paths:
        for h in hints:
            if h in p:
                out.append(p)
                break
    return out


def scan(repo: str | pathlib.Path, n_recent: int = 10) -> RepoSnapshot:
    """One-shot read-only scan. Pure: no side effects."""
    r = pathlib.Path(repo)
    staged = staged_files(r)
    untracked = untracked_files(r)
    modified = modified_files(r)
    return RepoSnapshot(
        head_sha=head_sha(r),
        head_subject=head_subject(r),
        recent_commits=recent_commits(r, n_recent),
        staged_files=staged,
        untracked_files=untracked,
        modified_files=modified,
        dirty_protected_files=detect_dirty_protected(modified, staged),
        foreign_staged_files=[],  # caller fills with expected_paths context
        untracked_tmp_helpers=detect_untracked_tmp_helpers(untracked),
        duplicate_chain_files=detect_duplicate_chain_files(untracked + staged),
    )
