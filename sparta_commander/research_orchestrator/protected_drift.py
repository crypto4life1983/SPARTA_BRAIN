"""Protected-file drift baseline tracking.

A "protected file" is one the orchestrator must never stage, commit, or modify.
But such a file may legitimately be dirty in the working tree for known
operator-accepted reasons (e.g., pre-existing drift from a prior session
intentionally left unstaged). This module distinguishes:

    KNOWN_PRE_EXISTING_DRIFT  -- working-tree hash matches an accepted baseline
    NEW_PROTECTED_DRIFT       -- working-tree hash differs from accepted baseline
                                 OR no baseline is recorded yet
    RESOLVED                  -- file is clean (no drift)

The safe_executor guard remains unchanged: protected files are NEVER staged
or committed regardless of baseline status. Baseline only affects how the
decision_engine reports the drift (warning vs HIGH halt).
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import pathlib
from dataclasses import asdict, dataclass, field
from typing import Any


# Classifications
CLASSIFICATION_KNOWN = "KNOWN_PRE_EXISTING_DRIFT"
CLASSIFICATION_NEW = "NEW_PROTECTED_DRIFT"
CLASSIFICATION_RESOLVED = "RESOLVED"
CLASSIFICATION_NO_BASELINE_DIRTY = "NEW_PROTECTED_DRIFT"  # alias; same handling

# Operator status values
OP_STATUS_ACCEPTED = "ACCEPTED"
OP_STATUS_PENDING_REVIEW = "PENDING_REVIEW"
OP_STATUS_REJECTED = "REJECTED"


@dataclass
class ProtectedDriftBaseline:
    """One operator-accepted baseline for a protected file."""

    path: str
    accepted_working_tree_sha256: str
    head_blob_sha256: str | None  # git's hash of the file at HEAD (if tracked)
    reason: str
    first_seen_utc: str
    last_seen_utc: str
    operator_status: str = OP_STATUS_ACCEPTED

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "ProtectedDriftBaseline":
        return cls(**d)


def sha256_of_file(path: str | pathlib.Path) -> str | None:
    """SHA-256 of file bytes. None if file missing."""
    p = pathlib.Path(path)
    if not p.exists():
        return None
    return hashlib.sha256(p.read_bytes()).hexdigest()


def head_blob_sha256_of_file(repo: pathlib.Path, path: str) -> str | None:
    """Return the SHA-256 of the file contents at HEAD, or None if not tracked.

    Uses `git show HEAD:<path>` to read the HEAD-version bytes, then hashes
    them with SHA-256 (NOT git's internal blob hash, which uses a different
    framing).
    """
    import subprocess
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), "show", f"HEAD:{path}"],
            capture_output=True, check=True,
        )
        return hashlib.sha256(result.stdout).hexdigest()
    except subprocess.CalledProcessError:
        return None


def classify(
    current_wt_sha256: str | None,
    baseline: ProtectedDriftBaseline | None,
    head_blob_sha256: str | None,
) -> str:
    """Classify a protected file's current state.

    current_wt_sha256 = None          -> file missing; RESOLVED, no drift
    untracked (no HEAD) + no baseline -> RESOLVED (nothing to drift from;
                                          never-touch guard handles it separately)
    matches HEAD blob (clean)         -> RESOLVED
    matches baseline                  -> KNOWN_PRE_EXISTING_DRIFT
    differs from baseline             -> NEW_PROTECTED_DRIFT
    no baseline + tracked + dirty     -> NEW_PROTECTED_DRIFT
    """
    if current_wt_sha256 is None:
        return CLASSIFICATION_RESOLVED
    if head_blob_sha256 is None and baseline is None:
        # File is untracked AND no operator baseline accepted. Not drift —
        # untracked files have no tracked version to drift from. The
        # never-touch guard (safe_executor) still prevents staging/commit.
        return CLASSIFICATION_RESOLVED
    if head_blob_sha256 and current_wt_sha256 == head_blob_sha256:
        return CLASSIFICATION_RESOLVED
    if baseline is None:
        return CLASSIFICATION_NEW
    if current_wt_sha256 == baseline.accepted_working_tree_sha256:
        return CLASSIFICATION_KNOWN
    return CLASSIFICATION_NEW


class BaselineStore:
    """File-backed baseline store under <storage_root>/protected_drift_baselines/."""

    def __init__(self, storage_root: str | pathlib.Path) -> None:
        self.root = pathlib.Path(storage_root) / "protected_drift_baselines"
        self.root.mkdir(parents=True, exist_ok=True)

    def _path_for(self, file_path: str) -> pathlib.Path:
        # Encode path so it's safe as a filename
        safe = file_path.replace("/", "__").replace("\\", "__")
        return self.root / f"{safe}.json"

    def get(self, file_path: str) -> ProtectedDriftBaseline | None:
        p = self._path_for(file_path)
        if not p.exists():
            return None
        try:
            return ProtectedDriftBaseline.from_dict(json.loads(p.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, TypeError):
            return None

    def save(self, baseline: ProtectedDriftBaseline) -> pathlib.Path:
        p = self._path_for(baseline.path)
        p.write_text(
            json.dumps(baseline.to_dict(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return p

    def list_all(self) -> list[ProtectedDriftBaseline]:
        out: list[ProtectedDriftBaseline] = []
        for p in sorted(self.root.glob("*.json")):
            try:
                out.append(ProtectedDriftBaseline.from_dict(json.loads(p.read_text(encoding="utf-8"))))
            except (json.JSONDecodeError, TypeError):
                continue
        return out

    def remove(self, file_path: str) -> bool:
        p = self._path_for(file_path)
        if p.exists():
            p.unlink()
            return True
        return False


def accept_drift(
    storage_root: str | pathlib.Path,
    repo: str | pathlib.Path,
    file_path: str,
    reason: str,
) -> ProtectedDriftBaseline:
    """Record the current working-tree hash of `file_path` as accepted baseline.

    Idempotent: re-accepting refreshes last_seen_utc; first_seen_utc preserved.
    Raises FileNotFoundError if the file doesn't exist in the working tree.
    """
    repo_path = pathlib.Path(repo)
    full_path = repo_path / file_path
    if not full_path.exists():
        raise FileNotFoundError(f"protected file does not exist at {full_path}")
    wt_sha = sha256_of_file(full_path)
    head_sha = head_blob_sha256_of_file(repo_path, file_path)
    if wt_sha is None:
        raise RuntimeError(f"could not hash {file_path}")

    now = _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="microseconds")
    store = BaselineStore(storage_root)
    existing = store.get(file_path)
    baseline = ProtectedDriftBaseline(
        path=file_path,
        accepted_working_tree_sha256=wt_sha,
        head_blob_sha256=head_sha,
        reason=reason,
        first_seen_utc=existing.first_seen_utc if existing else now,
        last_seen_utc=now,
        operator_status=OP_STATUS_ACCEPTED,
    )
    store.save(baseline)
    return baseline


def scan_protected_drift(
    repo: str | pathlib.Path,
    storage_root: str | pathlib.Path,
    protected_paths: list[str] | tuple[str, ...],
) -> list[dict[str, Any]]:
    """For each protected path, report classification + hash details.

    Returns one record per path. Records for clean files are still included
    (classification=RESOLVED) so the UI can show a green row.
    """
    repo_path = pathlib.Path(repo)
    store = BaselineStore(storage_root)
    out: list[dict[str, Any]] = []
    for rel in protected_paths:
        full = repo_path / rel
        wt_sha = sha256_of_file(full) if full.exists() else None
        head_sha = head_blob_sha256_of_file(repo_path, rel)
        baseline = store.get(rel)
        cls = classify(wt_sha, baseline, head_sha)
        record: dict[str, Any] = {
            "path": rel,
            "exists": full.exists(),
            "current_working_tree_sha256": wt_sha,
            "head_blob_sha256": head_sha,
            "classification": cls,
            "baseline_accepted_sha256": baseline.accepted_working_tree_sha256 if baseline else None,
            "baseline_reason": baseline.reason if baseline else None,
            "baseline_first_seen_utc": baseline.first_seen_utc if baseline else None,
            "baseline_last_seen_utc": baseline.last_seen_utc if baseline else None,
            "operator_status": baseline.operator_status if baseline else None,
            "is_dirty": wt_sha is not None and head_sha is not None and wt_sha != head_sha,
        }
        out.append(record)
    return out
