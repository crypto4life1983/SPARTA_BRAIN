"""Commander Research Autopilot v2 — read-only watcher CLI.

Usage:
    # One-shot scan + audit
    python tools/research_orchestrator_watch.py

    # Loop mode (poll every 60s)
    python tools/research_orchestrator_watch.py --loop --interval 60

    # Custom storage root
    python tools/research_orchestrator_watch.py --storage /path/to/storage

The watcher NEVER mutates anything. It:
    1. Scans repo state via git_sentinel
    2. Classifies recent commits
    3. Verifies seals on recent sealed reports
    4. Extracts K9/DR metrics
    5. Detects missing REC1_T1 carry
    6. Generates pending decisions
    7. Persists state to storage/research_orchestrator/

Operator reviews decisions via UI (/command/research-orchestrator) or by
reading the JSON files directly under storage/research_orchestrator/pending_decisions/
"""

from __future__ import annotations

import argparse
import pathlib
import sys
import time
from typing import Any

# Ensure repo root is importable
_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from sparta_commander.research_orchestrator import (  # noqa: E402
    anchor_verifier,
    decision_engine,
    gate_evaluator,
    git_sentinel,
    l1_checker,
    phase_classifier,
    protected_drift,
    seal_verifier,
)
from sparta_commander.research_orchestrator.state import (  # noqa: E402
    CandidateState,
    HARD_GUARD_FORBIDDEN_ALWAYS,
    K9_NOT_EVALUATED,
    K9_PASS,
    K9_FAIL,
    L1_FULL,
    L1_MISSING,
    L1_PARTIAL,
)
from sparta_commander.research_orchestrator.storage import Storage  # noqa: E402


# Heuristic: pull candidate_record_id from a sealed JSON if present
def _candidate_id_from_report(report_path: pathlib.Path) -> str | None:
    try:
        import json
        body = json.loads(report_path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, ValueError):
        return None
    if isinstance(body, dict):
        return body.get("candidate_record_id")
    return None


def _find_sealed_reports(repo: pathlib.Path, since_n_commits: int = 30) -> list[pathlib.Path]:
    """Find recent sealed report JSONs (last N commits' deltas).

    Conservative: only looks at currently-tracked files matching `*_sealed.json`
    under reports/. Does not scan the full history.
    """
    out: list[pathlib.Path] = []
    reports_dir = repo / "reports"
    if not reports_dir.exists():
        return out
    for p in reports_dir.rglob("*_sealed.json"):
        out.append(p)
    # Also catch the non-_sealed.json convention used by some reports
    for p in reports_dir.rglob("*_report.json"):
        out.append(p)
    return sorted(out)[-since_n_commits:]


def scan_once(repo: pathlib.Path, storage: Storage, verbose: bool = True) -> dict[str, Any]:
    """One pass: scan, classify, verify, generate pending decisions."""
    snap = git_sentinel.scan(repo)

    # Augment snapshot with protected-drift baseline classification
    drift_details = protected_drift.scan_protected_drift(
        repo=repo,
        storage_root=storage.root,
        protected_paths=git_sentinel.PROTECTED_FILES_NEVER_TOUCH,
    )
    snap.protected_drift_details = drift_details
    new_drift = [d for d in drift_details if d["classification"] == "NEW_PROTECTED_DRIFT"]
    known_drift = [d for d in drift_details if d["classification"] == "KNOWN_PRE_EXISTING_DRIFT"]

    if verbose:
        print(f"[orchestrator] HEAD = {snap.head_sha[:7]} {snap.head_subject[:80]}")
        print(f"[orchestrator] staged={len(snap.staged_files)} untracked={len(snap.untracked_files)}"
              f" modified={len(snap.modified_files)}"
              f" dirty_protected={len(snap.dirty_protected_files)}"
              f" (known_baseline={len(known_drift)} new_drift={len(new_drift)})"
              f" tmp_helpers={len(snap.untracked_tmp_helpers)}"
              f" duplicate_chain_files={len(snap.duplicate_chain_files)}")

    # Audit recent reports
    reports = _find_sealed_reports(repo)
    seal_results = {}
    for r in reports[-10:]:  # only the most recent 10 to keep scans fast
        seal_results[str(r.relative_to(repo))] = seal_verifier.verify_seal(r)

    # Group reports by candidate_record_id
    by_candidate: dict[str, list[pathlib.Path]] = {}
    for r in reports:
        cid = _candidate_id_from_report(r)
        if cid:
            by_candidate.setdefault(cid, []).append(r)

    # For each known candidate, build / refresh state
    candidates_updated: list[str] = []
    for cid, candidate_reports in by_candidate.items():
        state = storage.load_candidate(cid) or CandidateState(candidate_id=cid)

        # Use the latest report (by path) as the "current phase" proxy
        latest_report = candidate_reports[-1]
        latest_subject = snap.head_subject
        # Better phase classification from filename
        phase = phase_classifier.classify(latest_subject, [str(latest_report.relative_to(repo))])
        state.current_phase = phase

        gates = gate_evaluator.extract_gates(latest_report)
        state.latest_verdict = gates.get("verdict")
        state.closed_trades_observed = gates.get("closed_trades")
        if gates.get("k9_threshold"):
            state.k9_threshold = gates["k9_threshold"]
        state.k9_status = gates.get("k9_status", K9_NOT_EVALUATED)
        state.dr_gate_status = gates.get("dr_gates_fired", {})

        l1 = l1_checker.check_l1(latest_report)
        state.rec1_t1_carry_status = l1["status"]

        state.forbidden_actions = list(HARD_GUARD_FORBIDDEN_ALWAYS)

        # Decisions
        decisions = decision_engine.evaluate(state, latest_audit=gates, repo_snapshot=snap.to_dict())
        if decisions:
            # Save the highest-priority decision's action as next_recommended
            decisions.sort(key=lambda d: {"HIGH": 0, "MEDIUM": 1, "LOW": 2}.get(d.get("priority", "LOW"), 3))
            state.next_recommended_action = decisions[0]["action"]

        storage.save_candidate(state)
        candidates_updated.append(cid)

        # Persist each pending decision (idempotent overwrite by decision_id)
        for d in decisions:
            d.setdefault("decision_id", f"{cid}__{d['action']}__{snap.head_sha[:7]}")
            storage.save_pending_decision(d)

        if verbose:
            print(f"[orchestrator]   candidate={cid[:50]:50s} phase={state.current_phase:25s}"
                  f" k9={state.k9_status:8s} l1={state.rec1_t1_carry_status[:30]:30s}"
                  f" decisions={len(decisions)}")

    # Audit-log this scan
    storage.append_audit_log({
        "event": "scan",
        "head_sha": snap.head_sha,
        "head_subject": snap.head_subject,
        "staged_count": len(snap.staged_files),
        "untracked_count": len(snap.untracked_files),
        "dirty_protected_count": len(snap.dirty_protected_files),
        "protected_drift_known_count": len(known_drift),
        "protected_drift_new_count": len(new_drift),
        "duplicate_chain_files_count": len(snap.duplicate_chain_files),
        "tmp_helpers_count": len(snap.untracked_tmp_helpers),
        "reports_scanned": len(reports),
        "candidates_updated": candidates_updated,
        "seal_verify_summary": {
            "total": len(seal_results),
            "pass": sum(1 for v in seal_results.values() if v["status"] == "PASS"),
            "fail": sum(1 for v in seal_results.values() if v["status"] == "FAIL"),
            "missing": sum(1 for v in seal_results.values() if v["status"] == "MISSING"),
        },
    })

    return {
        "head_sha": snap.head_sha,
        "head_subject": snap.head_subject,
        "candidates_updated": candidates_updated,
        "reports_scanned": len(reports),
        "snapshot": snap.to_dict(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Commander Research Autopilot v2 watcher")
    parser.add_argument("--repo", default=str(_REPO_ROOT),
                       help="Repo root (default: this script's parent)")
    parser.add_argument("--storage", default=str(_REPO_ROOT / "storage" / "research_orchestrator"),
                       help="Storage root for state + pending decisions")
    parser.add_argument("--loop", action="store_true", help="Poll continuously")
    parser.add_argument("--interval", type=int, default=60, help="Loop interval in seconds")
    parser.add_argument("--quiet", action="store_true", help="Suppress per-scan stdout")
    parser.add_argument(
        "--accept-protected-drift", metavar="PATH",
        help="Record current working-tree hash of PATH as accepted baseline. "
             "Future scans with the same hash classify as KNOWN_PRE_EXISTING_DRIFT "
             "rather than NEW_PROTECTED_DRIFT. Requires --reason.",
    )
    parser.add_argument(
        "--reason", default="",
        help="Required when --accept-protected-drift is used: human-readable "
             "explanation of why the drift is accepted.",
    )
    args = parser.parse_args()

    repo = pathlib.Path(args.repo)
    storage = Storage(args.storage)

    # Subcommand: accept a protected-drift baseline
    if args.accept_protected_drift:
        if not args.reason.strip():
            print(
                "[orchestrator] error: --accept-protected-drift requires --reason "
                "to explain why the drift is accepted.",
                file=sys.stderr,
            )
            return 2
        try:
            baseline = protected_drift.accept_drift(
                storage_root=storage.root,
                repo=repo,
                file_path=args.accept_protected_drift,
                reason=args.reason,
            )
        except FileNotFoundError as e:
            print(f"[orchestrator] error: {e}", file=sys.stderr)
            return 1
        storage.append_audit_log({
            "event": "accept_protected_drift",
            "path": baseline.path,
            "accepted_working_tree_sha256": baseline.accepted_working_tree_sha256,
            "head_blob_sha256": baseline.head_blob_sha256,
            "reason": baseline.reason,
        })
        print(f"[orchestrator] accepted baseline for {baseline.path}")
        print(f"  accepted_working_tree_sha256 = {baseline.accepted_working_tree_sha256}")
        print(f"  head_blob_sha256             = {baseline.head_blob_sha256}")
        print(f"  reason                       = {baseline.reason}")
        print(f"  first_seen_utc               = {baseline.first_seen_utc}")
        print(f"  last_seen_utc                = {baseline.last_seen_utc}")
        return 0

    if not args.loop:
        scan_once(repo, storage, verbose=not args.quiet)
        return 0

    print(f"[orchestrator] entering loop mode, interval={args.interval}s. Ctrl-C to exit.")
    try:
        while True:
            scan_once(repo, storage, verbose=not args.quiet)
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("[orchestrator] interrupted; exiting cleanly.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
