"""SPARTA Overnight Autopilot - ONE-SHOT queue processor.

Invoked by a Windows Task Scheduler task that the HUMAN installs manually
(see tools/install_overnight_autopilot_task.ps1). One invocation processes
the queue ONCE and exits: no daemon, no loop, no sleep.

Executes ONLY the contract's four safe offline task types. Human-gated
research actions found in the queue are surfaced as proposals in the
morning report -- never executed. No commit, no push, no network, no
trading capability, no claims. Every run ends with a validated run record
naming exactly what ran, the artifacts produced, and the next human gate.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import pathlib
import subprocess
import sys

REPO_ROOT = "C:/SPARTA_BRAIN"
sys.path.insert(0, REPO_ROOT)

from sparta_commander.overnight_autopilot_research_queue_contract import (  # noqa: E402
    ALLOWED_TASK_TYPES,
    PRESERVED_LEDGER,
    QUEUE_PATH,
    REPORTS_DIR,
    VERDICT_OA_READY,
    build_overnight_autopilot_contract,
    validate_overnight_autopilot_contract,
    validate_queue_task,
    validate_run_record,
)
from sparta_commander.ny_session_fvg_choch_additional_session_days_staged_candles_review import (  # noqa: E402
    observe_baseline_integrity,
    verify_append_only_integrity,
)

DEFAULT_QUEUE = [
    {"task_id": "nightly_integrity", "task_type": "integrity_audit",
     "status": "queued", "params": {}},
    {"task_id": "nightly_certification",
     "task_type": "contract_certification_sweep", "status": "queued",
     "params": {}},
    {"task_id": "nightly_safety_tests",
     "task_type": "safety_test_suite_report", "status": "queued",
     "params": {}},
    {"task_id": "nightly_seed_brief", "task_type":
     "seed_research_brief_draft", "status": "queued", "params": {}},
]

_EXTRA_PINNED = {
    "data/breakout_pullback/detector_labels/"
    "bp_detector_labels_2026-05-12_2026-06-10.jsonl":
        "80a4b45ff266ce0e63b68214be81933fb9f4f108c8f7d8d4b17adfda7728b202",
    "data/breakout_pullback/replay_results/"
    "bp_replay_results_2026-05-12_2026-06-10.jsonl":
        "9757cdda22b7dc0ad41e48d803df192dbe510c8af08ae4cb478197ad59e98806",
    "data/breakout_pullback/v2_1h_filter/"
    "bp_v2_replay_results_2026-05-12_2026-06-10.jsonl":
        "3a415c6da9002f5966da6cca6bc916caf4342cb1a10c4c0a8ec054fefab87a68",
}


def reseed_queue(queue):
    """Re-seed the 4 default safe tasks to "queued" at the start of every
    one-shot run, so nightly runs never no-op after night 1.
    proposal_for_human entries are preserved exactly; nothing else in the
    queue is touched."""
    reseeded = set()
    for task in queue:
        if not isinstance(task, dict):
            continue
        if task.get("status") == "proposal_for_human":
            continue
        for default in DEFAULT_QUEUE:
            if (task.get("task_id") == default["task_id"]
                    and task.get("task_type") == default["task_type"]):
                task["status"] = "queued"
                reseeded.add(default["task_id"])
    for default in DEFAULT_QUEUE:
        if default["task_id"] not in reseeded:
            queue.append(dict(default))
    return queue


def task_integrity_audit():
    check = verify_append_only_integrity(
        observe_baseline_integrity(REPO_ROOT))
    extra_errors = []
    for rel_path, expected in _EXTRA_PINNED.items():
        target = pathlib.Path(REPO_ROOT) / rel_path
        if not target.is_file():
            extra_errors.append("missing:" + rel_path)
        elif hashlib.sha256(target.read_bytes()).hexdigest() != expected:
            extra_errors.append("mutated:" + rel_path)
    intact = check["intact"] and not extra_errors
    return {"intact": intact,
            "errors": check["errors"] + extra_errors}


def task_certification_sweep():
    verdicts = {}
    # The original staged-files review certifies the FIRST 12-file snapshot
    # only. The human-approved batch2 append (126 more files in the same
    # directory) makes that snapshot contract reject BY DESIGN, so REJECTED
    # is the documented expected verdict; byte-integrity of the original 12
    # files is proven separately by the integrity_audit task.
    from sparta_commander.ny_session_fvg_choch_real_candle_staged_files_review_contract import (
        build_staged_files_review)
    verdicts["staged_files_original_snapshot_superseded"] = (
        build_staged_files_review(
            REPO_ROOT, tracked_paths=[]).get("verdict"))
    from sparta_commander.ny_session_fvg_choch_additional_session_days_staged_candles_review import (
        build_additional_session_days_review)
    verdicts["staged_files_batch2_append_policy"] = (
        build_additional_session_days_review().get("verdict"))
    from sparta_commander.ny_session_fvg_choch_accepted_labels_human_review_contract import (
        build_accepted_labels_human_review)
    verdicts["staged_files_current_state_batch2_manifest"] = (
        build_accepted_labels_human_review(
            REPO_ROOT, tracked_paths=[]).get("verdict"))
    from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
        build_rejection_record)
    verdicts["candidate_1_rejection"] = build_rejection_record(
        REPO_ROOT, tracked_paths=[]).get("verdict")
    from sparta_commander.crypto_intraday_breakout_pullback_structure_real_candle_detector_labels_review_contract import (
        build_bp_detector_labels_review)
    verdicts["bp_labels"] = build_bp_detector_labels_review(
        REPO_ROOT, tracked_paths=[]).get("verdict")
    from sparta_commander.crypto_intraday_breakout_pullback_structure_replay_results_review_contract import (
        build_bp_replay_results_review)
    verdicts["bp_replay_freeze"] = build_bp_replay_results_review(
        REPO_ROOT, tracked_paths=[]).get("verdict")
    from sparta_commander.crypto_intraday_breakout_pullback_structure_v2_result_and_rejection_record_contract import (
        build_bp_v2_rejection_record)
    verdicts["candidate_2_rejection"] = build_bp_v2_rejection_record(
        REPO_ROOT, tracked_paths=[]).get("verdict")
    expected = {
        "staged_files_original_snapshot_superseded":
            "REAL_CANDLE_STAGED_FILES_REJECTED",
        "staged_files_batch2_append_policy":
            "NY_FVG_CHOCH_ADDITIONAL_SESSION_DAYS_REVIEW_READY",
        "staged_files_current_state_batch2_manifest":
            "ACCEPTED_LABELS_HUMAN_REVIEW_APPROVED_FOR_REPLAY_DECISION",
        "candidate_1_rejection":
            "V3_RESULT_FROZEN_AND_CANDIDATE_REJECTED_KEPT_ON_RECORD",
        "bp_labels":
            "BP_REAL_CANDLE_DETECTOR_LABELS_ACCEPTED_FOR_REPLAY_REVIEW",
        "bp_replay_freeze":
            "BP_REPLAY_RESULTS_FROZEN_CANDIDATE_REJECTED_AS_IS",
        "candidate_2_rejection":
            "BP_V2_RESULT_FROZEN_AND_CANDIDATE_2_REJECTED_KEPT_ON_RECORD"}
    return {"verdicts": verdicts,
            "all_certify_unchanged": verdicts == expected}


def task_safety_tests():
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-p", "no:cacheprovider",
         "--rootdir", REPO_ROOT + "/tests",
         REPO_ROOT + "/tests/test_sparta_commander_2_safety.py", "-q"],
        capture_output=True, text=True, timeout=600,
        env={"PYTHONPATH": REPO_ROOT, "PATH": __import__("os").environ.get(
            "PATH", ""), "SYSTEMROOT": __import__("os").environ.get(
            "SYSTEMROOT", "")})
    tail = (proc.stdout or "").strip().splitlines()[-1:]
    return {"exit_code": proc.returncode,
            "result_line": tail[0] if tail else "no output"}


def task_seed_brief(reports_dir, stamp):
    seeds = PRESERVED_LEDGER["seeds_for_new_families_only"]
    brief_path = reports_dir / ("seed_brief_draft_%s.md" % stamp)
    lines = [
        "# Seed Research Brief (DRAFT, ADVISORY ONLY)", "",
        "Generated by the overnight autopilot from FROZEN evidence only.",
        "This brief proposes; the human decides. It is NOT a rescue of any",
        "rejected candidate and authorizes nothing.", "",
        "## Ledger (preserved)",
        "- Candidate #1: REJECTED_KEPT_ON_RECORD "
        "(COST_NON_VIABLE_RISK_GEOMETRY)",
        "- Candidate #2: REJECTED_KEPT_ON_RECORD "
        "(EDGE_FAILURE_SURVIVED_ONE_AUTHORIZED_FILTER_EXPERIMENT)", "",
        "## Frozen seeds (for NEW families only)"]
    lines += ["- " + s for s in seeds]
    lines += [
        "", "## Draft direction for human review",
        "A long-only, BTC/SOL-weighted candidate family built on the",
        "existing staged data, keeping the 81 bps floor and 27 bps cost",
        "discipline, would test the strongest frozen observations without",
        "touching either rejected candidate. Next human gate:",
        "HUMAN_DECISION_ON_NEXT_CANDIDATE_FAMILY.", ""]
    with open(brief_path, "x", encoding="utf-8", newline="") as handle:
        handle.write("\n".join(lines))
    return {"brief": str(brief_path)}


def main() -> int:
    contract = build_overnight_autopilot_contract()
    assert contract["verdict"] == VERDICT_OA_READY, contract["blockers"]
    assert validate_overnight_autopilot_contract(contract)["valid"] is True

    started = dt.datetime.now(dt.timezone.utc)
    stamp = started.strftime("%Y%m%dT%H%M%SZ")
    queue_file = pathlib.Path(REPO_ROOT) / QUEUE_PATH
    reports_dir = pathlib.Path(REPO_ROOT) / REPORTS_DIR
    reports_dir.mkdir(parents=True, exist_ok=True)
    if queue_file.is_file():
        queue = reseed_queue(
            json.loads(queue_file.read_text(encoding="utf-8")))
    else:
        queue = [dict(task) for task in DEFAULT_QUEUE]
        queue_file.parent.mkdir(parents=True, exist_ok=True)

    executed, skipped, proposals, artifacts = [], [], [], []
    integrity_status = "NOT_RUN"
    for task in queue:
        check = validate_queue_task(task)
        if check["is_human_proposal"]:
            proposals.append({"task_id": task.get("task_id"),
                              "task_type": task.get("task_type")})
            continue
        if not check["executable"]:
            if task.get("status") == "queued":
                task["status"] = "skipped_forbidden"
                skipped.append({"task_id": task.get("task_id"),
                                "task_type": task.get("task_type"),
                                "errors": check["errors"]})
            continue
        task_type = task["task_type"]
        if task_type == "integrity_audit":
            outcome = task_integrity_audit()
            integrity_status = "INTACT" if outcome["intact"] else (
                "VIOLATION:" + ";".join(outcome["errors"]))
        elif task_type == "contract_certification_sweep":
            outcome = task_certification_sweep()
        elif task_type == "safety_test_suite_report":
            outcome = task_safety_tests()
        elif task_type == "seed_research_brief_draft":
            outcome = task_seed_brief(reports_dir, stamp)
            artifacts.append(outcome["brief"])
        else:  # unreachable by construction; refuse anyway
            continue
        task["status"] = "done"
        executed.append({"task_id": task["task_id"],
                         "task_type": task_type, "outcome": outcome})

    finished = dt.datetime.now(dt.timezone.utc)
    run_record = {
        "run_id": "overnight_" + stamp,
        "started_utc": started.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "finished_utc": finished.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "tasks_executed": executed, "tasks_skipped": skipped,
        "proposals_surfaced_for_human": proposals,
        "artifacts_produced": artifacts,
        "integrity_status": integrity_status,
        "claims_made": "none",
        "no_commit_no_push": True,
        "next_human_gate": "HUMAN_DECISION_ON_NEXT_CANDIDATE_FAMILY",
    }
    check = validate_run_record(run_record)
    assert check["acceptable"] is True, check["errors"]

    report_path = reports_dir / ("overnight_run_%s.json" % stamp)
    with open(report_path, "x", encoding="utf-8", newline="") as handle:
        handle.write(json.dumps(run_record, indent=2, sort_keys=True) + "\n")
    run_record["artifacts_produced"].append(str(report_path))
    with open(queue_file, "w", encoding="utf-8", newline="") as handle:
        handle.write(json.dumps(queue, indent=2, sort_keys=True) + "\n")

    print(json.dumps(run_record, indent=2, sort_keys=True))
    print("ONE-SHOT COMPLETE - exiting. No commit, no push, no claims.")
    return 0 if integrity_status == "INTACT" else 1


if __name__ == "__main__":
    sys.exit(main())
