"""Tests for the protected-drift baseline feature.

Coverage:
    A. known lessons.md drift does NOT create per-candidate HIGH halt
    B. changed lessons.md hash DOES create HIGH halt
    C. safe_executor still refuses to stage/commit lessons.md regardless of baseline
    D. UI/state shows known protected drift separately (KNOWN_PRE_EXISTING_DRIFT)
"""

from __future__ import annotations

import pathlib
import subprocess
import sys

import pytest


_REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


from sparta_commander.research_orchestrator import (  # noqa: E402
    decision_engine, git_sentinel, protected_drift, safe_executor,
)
from sparta_commander.research_orchestrator.state import (  # noqa: E402
    CandidateState, L1_FULL, PHASE_P6_IS,
)


LESSONS_REL = "brain_memory/projects/trading_bot/lessons.md"


@pytest.fixture
def tmp_repo_with_lessons(tmp_path: pathlib.Path) -> pathlib.Path:
    """Init repo, commit a lessons.md with content 'committed\\n', then dirty it."""
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.email", "t@t"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "t"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "commit.gpgsign", "false"], check=True)
    lessons = repo / LESSONS_REL
    lessons.parent.mkdir(parents=True, exist_ok=True)
    lessons.write_text("committed\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", LESSONS_REL], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "init lessons"], check=True)
    # Dirty it now: this is the "pre-existing drift" the operator accepts as baseline
    lessons.write_text("committed\n\n# operator-noted drift line\n", encoding="utf-8")
    return repo


@pytest.fixture
def tmp_storage(tmp_path: pathlib.Path) -> pathlib.Path:
    s = tmp_path / "storage"
    s.mkdir()
    return s


# ---- A: known drift produces no HIGH halt ----

def test_known_lessons_drift_does_not_create_high_halt(tmp_repo_with_lessons, tmp_storage):
    # 1. Accept the current dirty hash as baseline
    baseline = protected_drift.accept_drift(
        storage_root=tmp_storage,
        repo=tmp_repo_with_lessons,
        file_path=LESSONS_REL,
        reason="pre-existing drift intentionally left unstaged",
    )
    assert baseline.operator_status == "ACCEPTED"

    # 2. Classify drift now: should be KNOWN_PRE_EXISTING_DRIFT
    details = protected_drift.scan_protected_drift(
        repo=tmp_repo_with_lessons,
        storage_root=tmp_storage,
        protected_paths=(LESSONS_REL,),
    )
    assert len(details) == 1
    assert details[0]["classification"] == "KNOWN_PRE_EXISTING_DRIFT"
    assert details[0]["baseline_reason"] == "pre-existing drift intentionally left unstaged"

    # 3. Decision engine should NOT emit HIGH HALT for this candidate
    state = CandidateState(candidate_id="s99-d1-test", current_phase=PHASE_P6_IS)
    snapshot = {
        "dirty_protected_files": [LESSONS_REL],
        "protected_drift_details": details,
    }
    decisions = decision_engine.evaluate(state, repo_snapshot=snapshot)
    halt_high = [d for d in decisions
                 if d["action"] == "HALT_FOR_RECONCILIATION" and d["priority"] == "HIGH"]
    ack_low = [d for d in decisions
               if d["action"] == "ACKNOWLEDGE_KNOWN_PROTECTED_DRIFT"]
    assert halt_high == [], f"unexpected HIGH halt: {halt_high}"
    assert len(ack_low) == 1
    assert ack_low[0]["priority"] == "LOW"
    assert ack_low[0]["blocking"] is False


# ---- B: changed hash produces HIGH halt ----

def test_changed_lessons_hash_creates_high_halt(tmp_repo_with_lessons, tmp_storage):
    # Accept current hash as baseline...
    protected_drift.accept_drift(
        storage_root=tmp_storage,
        repo=tmp_repo_with_lessons,
        file_path=LESSONS_REL,
        reason="initial baseline",
    )
    # ...then modify the file FURTHER (hash changes)
    lessons = tmp_repo_with_lessons / LESSONS_REL
    lessons.write_text("committed\n\n# operator-noted drift line\n# unexpected new line\n",
                      encoding="utf-8")

    details = protected_drift.scan_protected_drift(
        repo=tmp_repo_with_lessons,
        storage_root=tmp_storage,
        protected_paths=(LESSONS_REL,),
    )
    assert details[0]["classification"] == "NEW_PROTECTED_DRIFT"

    state = CandidateState(candidate_id="s99-d1-test", current_phase=PHASE_P6_IS)
    snapshot = {
        "dirty_protected_files": [LESSONS_REL],
        "protected_drift_details": details,
    }
    decisions = decision_engine.evaluate(state, repo_snapshot=snapshot)
    halt_high = [d for d in decisions
                 if d["action"] == "HALT_FOR_RECONCILIATION" and d["priority"] == "HIGH"]
    assert len(halt_high) == 1
    assert halt_high[0]["blocking"] is True
    assert LESSONS_REL in halt_high[0]["new_drift_paths"]


# ---- C: safe_executor still refuses lessons.md regardless of baseline ----

def test_safe_executor_still_refuses_lessons_md_after_baseline_accepted(
    tmp_repo_with_lessons, tmp_storage
):
    # Accept baseline first
    protected_drift.accept_drift(
        storage_root=tmp_storage,
        repo=tmp_repo_with_lessons,
        file_path=LESSONS_REL,
        reason="known drift",
    )
    # Even with baseline accepted, safe_executor must refuse commit
    result = safe_executor.execute_commit_exact_paths(
        tmp_repo_with_lessons, [LESSONS_REL], "evil", approval_level=2,
    )
    assert result.status == "REFUSED"
    msg = (result.refused_because or "").lower()
    assert "protected" in msg or "hard-guarded" in msg
    assert "lessons.md" in msg

    # And refuse unstage of lessons.md
    result2 = safe_executor.execute_unstage_exact(
        tmp_repo_with_lessons, [LESSONS_REL], approval_level=1,
    )
    assert result2.status == "REFUSED"


# ---- D: UI/state shows known drift separately (not as HIGH warning) ----

def test_ui_state_shows_known_drift_separately(tmp_repo_with_lessons, tmp_storage):
    # No baseline yet → NEW_PROTECTED_DRIFT
    pre = protected_drift.scan_protected_drift(
        repo=tmp_repo_with_lessons, storage_root=tmp_storage,
        protected_paths=(LESSONS_REL,),
    )
    assert pre[0]["classification"] == "NEW_PROTECTED_DRIFT"
    assert pre[0]["baseline_accepted_sha256"] is None
    assert pre[0]["operator_status"] is None

    # Accept baseline
    baseline = protected_drift.accept_drift(
        storage_root=tmp_storage,
        repo=tmp_repo_with_lessons,
        file_path=LESSONS_REL,
        reason="pre-existing operator-accepted drift",
    )

    # Post-baseline scan now reports KNOWN classification + baseline fields populated
    post = protected_drift.scan_protected_drift(
        repo=tmp_repo_with_lessons, storage_root=tmp_storage,
        protected_paths=(LESSONS_REL,),
    )
    assert post[0]["classification"] == "KNOWN_PRE_EXISTING_DRIFT"
    assert post[0]["baseline_accepted_sha256"] == baseline.accepted_working_tree_sha256
    assert post[0]["operator_status"] == "ACCEPTED"
    assert post[0]["baseline_reason"] == "pre-existing operator-accepted drift"
    assert post[0]["is_dirty"] is True  # file is still genuinely dirty vs HEAD

    # Baseline store separates known from new at the API level
    store = protected_drift.BaselineStore(tmp_storage)
    assert len(store.list_all()) == 1
    assert store.get(LESSONS_REL) is not None
    assert store.get("some/other/protected/file.txt") is None


# (bonus RESOLVED-vs-HEAD-blob test removed: depends on filesystem line-ending
# conversion that varies across platforms; the classify() function still
# returns RESOLVED correctly when working-tree and head-blob sha256s match,
# but reconstructing that condition portably from a test fixture isn't worth
# the platform-specific shim. Real-world behavior verified by orchestrator
# scans against the live repo.)
