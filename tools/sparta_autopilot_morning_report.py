"""SPARTA Autopilot Morning Report / status surface (RESEARCH-ONLY REPORTING).

Produces a single human-readable morning report so the operator never has to
hand-inspect folders, logs, git status, or scheduled-task output. It READS the
latest overnight-autopilot run file, the local git status, and the committed
candidate-status constants, and WRITES:

  * reports/autopilot_morning/latest.md   (human-readable)
  * reports/autopilot_morning/latest.json (machine-readable)

It is a read-only reporting layer. It has NO trading, NO paper, NO live, NO
broker, NO exchange, NO order, NO credential, NO network-to-exchange, NO
detector/replay, and NO portfolio-compute capability. It NEVER claims paper or
live readiness. The only side effect is writing the two report files (inside
main(); the builder/renderer are pure).

Run-status rules:
  * No overnight run file present                       -> DID_NOT_RUN
  * Any task error / integrity != INTACT / status FAILED -> FAILED (stop safely)
  * Some tasks skipped/incomplete, no failures          -> PARTIAL
  * All attempted tasks completed, no errors            -> SUCCESS

Determinism: the report is a pure function of (run_state, git_summary,
candidate_status, report_generated_at) -- no wall-clock is read unless main()
explicitly passes one.
"""
from __future__ import annotations

import argparse
import glob
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
import sparta_commander.safe_research_autopilot_v1_contract as _sara  # noqa: E402,E501
OVERNIGHT_RUN_DIR = REPO_ROOT / "data" / "overnight_autopilot" / "reports"
OVERNIGHT_RUN_GLOB = "overnight_run_*.json"
OUT_DIR = REPO_ROOT / "reports" / "autopilot_morning"
OUT_MD = OUT_DIR / "latest.md"
OUT_JSON = OUT_DIR / "latest.json"

SCHEMA_VERSION = 1
MODE = "RESEARCH_ONLY_REPORTING"

RUN_STATUS_DID_NOT_RUN = "DID_NOT_RUN"
RUN_STATUS_FAILED = "FAILED"
RUN_STATUS_PARTIAL = "PARTIAL"
RUN_STATUS_SUCCESS = "SUCCESS"

# Pinned False everywhere -- this layer has no execution capability.
CAPABILITY_FLAGS = {
    "no_paper_trading": True, "no_live_trading": True, "no_broker": True,
    "no_exchange": True, "no_credentials": True, "no_orders": True,
    "no_order_logic": True, "no_network_to_exchange": True,
    "no_detector_run": True, "no_replay_run": True,
    "no_portfolio_compute": True, "no_data_fetch": True,
    "no_paper_live_readiness_claim": True,
}

# Map an open human gate to the exact text the operator should paste next.
GATE_PASTE_TEXT = {
    "HUMAN_DECISION_C11_ADVANCE_TO_SPEC_OR_REJECT_PROPOSAL": {
        "approve": "APPROVE_C11_ADVANCE_TO_CANDIDATE_SPEC",
        "reject": "REJECT_C11_FAMILY_PROPOSAL",
    },
}


# --------------------------------------------------------------------------- #
# Pure normalization + classification
# --------------------------------------------------------------------------- #

def normalize_overnight_run(raw: dict) -> dict:
    """Map an overnight_run_*.json into the canonical run_state the report
    builder consumes. Pure; tolerant of missing fields."""
    tasks = raw.get("tasks_executed") or []
    skipped = [t.get("task_id") for t in (raw.get("tasks_skipped") or [])
               if isinstance(t, dict)]
    attempted, completed, failed, errors = [], [], [], []
    for t in tasks:
        if not isinstance(t, dict):
            continue
        tid = t.get("task_id", "unknown_task")
        attempted.append(tid)
        outcome = t.get("outcome") or {}
        terrors = outcome.get("errors") or []
        if terrors or outcome.get("intact") is False:
            failed.append(tid)
            for e in (terrors or ["task_reported_not_intact"]):
                errors.append("%s: %s" % (tid, e))
        else:
            completed.append(tid)
    integrity = raw.get("integrity_status")
    if integrity and integrity != "INTACT":
        errors.append("integrity_status=%s" % integrity)
    return {
        "run_id": raw.get("run_id"),
        "run_time": raw.get("finished_utc") or raw.get("started_utc"),
        "started_utc": raw.get("started_utc"),
        "tasks_attempted": attempted,
        "tasks_completed": completed,
        "tasks_failed": failed,
        "tasks_skipped": skipped,
        "files_changed": list(raw.get("artifacts_produced") or []),
        "tests_run": list(raw.get("tests_run") or []),
        "errors": errors,
        "integrity_status": integrity,
        "explicit_status": raw.get("status"),
        "next_human_gate_from_run": raw.get("next_human_gate"),
        "no_commit_no_push": raw.get("no_commit_no_push"),
    }


def classify_run_status(run_state) -> str:
    if run_state is None:
        return RUN_STATUS_DID_NOT_RUN
    if (run_state.get("explicit_status") == "FAILED"
            or run_state.get("errors")
            or run_state.get("tasks_failed")
            or (run_state.get("integrity_status")
                and run_state["integrity_status"] != "INTACT")):
        return RUN_STATUS_FAILED
    if run_state.get("tasks_skipped") or (
            len(run_state.get("tasks_completed") or [])
            < len(run_state.get("tasks_attempted") or [])):
        return RUN_STATUS_PARTIAL
    return RUN_STATUS_SUCCESS


def _open_human_gate(candidate_status: dict) -> dict:
    """The most-forward open human gate across candidates. Returns the gate
    string + the exact approve/reject paste text."""
    for key in sorted(candidate_status.keys(), reverse=True):  # newest first
        c = candidate_status[key]
        action = c.get("next_action") or ""
        if action and not action.startswith("NONE"):
            paste = GATE_PASTE_TEXT.get(action, {})
            return {
                "candidate": key,
                "candidate_family": c.get("family"),
                "action": action,
                "approval_text_to_paste": paste.get("approve"),
                "reject_text_to_paste": paste.get("reject"),
            }
    return {"candidate": None, "action": "NONE", "approval_text_to_paste": None,
            "reject_text_to_paste": None}


def _what_to_do_next(run_status, gate, candidate_status) -> str:
    if run_status == RUN_STATUS_DID_NOT_RUN:
        return ("The overnight autopilot DID NOT RUN (no run file found). Check "
                "the scheduled task / launcher. No research candidate advanced; "
                "nothing was committed. No action needed on candidates.")
    if run_status == RUN_STATUS_FAILED:
        return ("The last run FAILED and stopped safely (no commit, no push). "
                "Review the error summary below and re-run once fixed. No "
                "candidate advanced and no trading of any kind occurred.")
    closed = [k for k, c in candidate_status.items()
              if not c.get("active") and str(c.get("status", "")).startswith(
                  "REJECTED")]
    closed_note = (" Closed/rejected: %s." % ", ".join(sorted(closed))
                   if closed else "")
    if gate.get("action", "NONE").startswith("NONE"):
        return ("Last run was %s. No open human decision right now.%s"
                % (run_status.lower(), closed_note))
    return ("Last run was %s.%s The open decision is %s on %s. "
            "To advance, paste: %s . To reject, paste: %s ."
            % (run_status.lower(), closed_note, gate["action"],
               gate.get("candidate"), gate.get("approval_text_to_paste"),
               gate.get("reject_text_to_paste")))


def _autopilot_plan(candidate_status: dict, git_summary: dict) -> dict:
    """Pure, READ-ONLY. Derive the chain state + repo cleanliness from the
    already-gathered inputs and ask the Safe Research Autopilot v1 PLANNER for
    its recommended next safe action. Executes nothing -- the planner only emits
    a recommendation; no build/labels/replay/commit happens here."""
    cstat = candidate_status or {}
    active = sorted(k for k, c in cstat.items()
                    if c.get("active")
                    and not str(c.get("status", "")).startswith("REJECTED"))
    if active:
        key = active[-1]
        c = cstat[key]
        chain_state = {"active_candidate": key,
                       "stage": c.get("autopilot_stage", "unknown_gate"),
                       "proposed_family": c.get("family")}
    else:
        chain_state = {"active_candidate": None, "stage": _sara.STAGE_NONE,
                       "proposed_family": None}
    gs = git_summary or {}
    repo_state = {"clean": bool(gs.get("clean", False)),
                  "uncommitted_candidate_artifacts":
                      bool(gs.get("staged")) or bool(gs.get("modified"))}
    decision = _sara.decide_next_safe_action(chain_state, repo_state)
    plan = _sara.summarize_for_morning_report(decision)
    plan["chain_stage"] = chain_state["stage"]
    plan["recommended_token"] = decision.get("recommended_token")
    plan["excluded_rejected_families_count"] = len(
        _sara.DEFAULT_REJECTED_FAMILIES)
    plan["planner_is_read_only"] = True
    plan["planner_executes_nothing"] = True
    return plan


def build_morning_report(run_state, git_summary: dict,
                         candidate_status: dict,
                         report_generated_at=None) -> dict:
    """Pure. Assemble the morning-report dict from already-gathered inputs."""
    run_status = classify_run_status(run_state)
    gate = _open_human_gate(candidate_status)
    rs = run_state or {}
    report = {
        "schema_version": SCHEMA_VERSION,
        "mode": MODE,
        "report_generated_at": report_generated_at or rs.get("run_time"),
        "last_run_time": rs.get("run_time"),
        "run_id": rs.get("run_id"),
        "run_status": run_status,
        "tasks_attempted": list(rs.get("tasks_attempted") or []),
        "tasks_completed": list(rs.get("tasks_completed") or []),
        "tasks_failed": list(rs.get("tasks_failed") or []),
        "tasks_skipped": list(rs.get("tasks_skipped") or []),
        "files_created_or_changed": list(rs.get("files_changed") or []),
        "tests_run": list(rs.get("tests_run") or []),
        "candidate_status": candidate_status,
        "next_required_human_gate": gate,
        "git_status_summary": git_summary,
        "ahead_behind": git_summary.get("ahead_behind") if git_summary else None,
        "error_summary": list(rs.get("errors") or []),
        "what_to_do_next": _what_to_do_next(run_status, gate, candidate_status),
        "autopilot_plan": _autopilot_plan(candidate_status, git_summary),
        "capability_flags": dict(CAPABILITY_FLAGS),
        "no_paper_live_readiness_claim": True,
    }
    return report


def render_markdown(report: dict) -> str:
    r = report
    lines = []
    lines.append("# SPARTA Autopilot — Morning Report")
    lines.append("")
    lines.append("> Research-only status surface. No paper/live/broker/order "
                 "capability. Never a paper/live-readiness claim.")
    lines.append("")
    lines.append("**Run status:** `%s`" % r["run_status"])
    lines.append("")
    lines.append("## 1. Last run time")
    lines.append("- %s (run_id: %s)" % (r.get("last_run_time") or "—",
                                        r.get("run_id") or "—"))
    lines.append("## 2. Run status")
    lines.append("- **%s**" % r["run_status"])
    lines.append("## 3. Tasks attempted")
    lines.append(_bullets(r["tasks_attempted"]))
    lines.append("## 4. Tasks completed")
    lines.append(_bullets(r["tasks_completed"]))
    if r["tasks_failed"]:
        lines.append("### Tasks FAILED")
        lines.append(_bullets(r["tasks_failed"]))
    if r["tasks_skipped"]:
        lines.append("### Tasks skipped")
        lines.append(_bullets(r["tasks_skipped"]))
    lines.append("## 5. Files created / changed")
    lines.append(_bullets(r["files_created_or_changed"]))
    lines.append("## 6. Tests run and results")
    if r["tests_run"]:
        for t in r["tests_run"]:
            if isinstance(t, dict):
                lines.append("- `%s` → %s" % (t.get("command", "?"),
                                              t.get("result", "?")))
            else:
                lines.append("- %s" % t)
    else:
        lines.append("- (none recorded for this run)")
    lines.append("## 7. Current candidate status")
    for key in sorted(r["candidate_status"].keys()):
        c = r["candidate_status"][key]
        lines.append("- **%s** (%s): %s — active=%s — next: %s"
                     % (key, c.get("family", "?"), c.get("status", "?"),
                        c.get("active"), c.get("next_action", "?")))
    lines.append("## 8. Current next required human gate")
    g = r["next_required_human_gate"]
    if g.get("action", "NONE").startswith("NONE"):
        lines.append("- None open.")
    else:
        lines.append("- **%s** on %s" % (g["action"], g.get("candidate")))
        lines.append("  - To advance, paste: `%s`"
                     % g.get("approval_text_to_paste"))
        lines.append("  - To reject, paste: `%s`"
                     % g.get("reject_text_to_paste"))
    lines.append("## 9. Git status summary")
    gs = r["git_status_summary"] or {}
    lines.append("- branch: %s | staged: %s | tracked-modified: %s | "
                 "untracked: %s | clean: %s"
                 % (gs.get("branch"), gs.get("staged"), gs.get("modified"),
                    gs.get("untracked"), gs.get("clean")))
    for ln in (gs.get("tracked_change_lines") or [])[:20]:
        lines.append("  - %s" % ln)
    lines.append("## 10. Ahead / behind")
    ab = r.get("ahead_behind") or {}
    lines.append("- upstream: %s | ahead: %s | behind: %s | in_sync: %s"
                 % (ab.get("upstream"), ab.get("ahead"), ab.get("behind"),
                    ab.get("in_sync")))
    lines.append("## 11. Error summary")
    lines.append(_bullets(r["error_summary"]) if r["error_summary"]
                 else "- (no errors)")
    lines.append("## 12. What I should do next")
    lines.append("> %s" % r["what_to_do_next"])
    lines.append("## 13. Safe Research Autopilot recommendation "
                 "(planner-only, read-only)")
    ap = r.get("autopilot_plan") or {}
    lines.append("- recommendation: **%s**" % ap.get("next_safe_action"))
    lines.append("- decision: %s" % ap.get("decision"))
    lines.append("- reason: %s" % ap.get("reason"))
    lines.append("- auto-advanceable: %s | requires human: %s | hard stop: %s"
                 % (ap.get("would_auto_advance"),
                    ap.get("requires_human_approval"), ap.get("is_hard_stop")))
    if ap.get("stopped_before"):
        lines.append("- **hard-stops before:** `%s`" % ap.get("stopped_before"))
    if ap.get("recommended_token"):
        lines.append("  - paste: `%s`" % ap.get("recommended_token"))
    if ap.get("next_safe_action") == "STOP_DIRTY_REPO":
        lines.append("- ⚠️ **DIRTY REPO** — commit/clean the working tree "
                     "before any auto-advance.")
    if ap.get("next_safe_action") == "BUILD_NEXT_CANDIDATE_FAMILY_PROPOSAL":
        lines.append("- candidate source EXCLUDES all %s rejected/closed "
                     "families (C1–C15)."
                     % ap.get("excluded_rejected_families_count"))
    lines.append("- planner executes nothing (read-only; no build / labels / "
                 "replay / portfolio / paper / live).")
    lines.append("")
    return "\n".join(lines) + "\n"


def _bullets(items) -> str:
    if not items:
        return "- (none)"
    return "\n".join("- %s" % x for x in items)


# --------------------------------------------------------------------------- #
# CLI gatherers (the only impure parts; read-only)
# --------------------------------------------------------------------------- #

def latest_run_file(run_dir: Path = OVERNIGHT_RUN_DIR):
    files = sorted(glob.glob(str(run_dir / OVERNIGHT_RUN_GLOB)))
    return Path(files[-1]) if files else None


def load_run_state(run_dir: Path = OVERNIGHT_RUN_DIR):
    f = latest_run_file(run_dir)
    if f is None or not f.exists():
        return None
    try:
        return normalize_overnight_run(json.loads(f.read_text(encoding="utf-8")))
    except Exception as exc:  # noqa: BLE001
        return {"run_id": None, "run_time": None, "tasks_attempted": [],
                "tasks_completed": [], "tasks_failed": ["report_parse"],
                "tasks_skipped": [], "files_changed": [], "tests_run": [],
                "errors": ["could_not_parse_run_file: %s" % type(exc).__name__],
                "integrity_status": None, "explicit_status": "FAILED"}


def _git(args):
    try:
        return subprocess.check_output(["git"] + args, cwd=str(REPO_ROOT),
                                       stderr=subprocess.DEVNULL).decode(
                                           "utf-8", "replace")
    except Exception:  # noqa: BLE001
        return ""


def gather_git_summary() -> dict:
    branch = _git(["rev-parse", "--abbrev-ref", "HEAD"]).strip() or None
    staged = [ln for ln in _git(["diff", "--cached", "--name-only"]
                                ).splitlines() if ln]
    tracked = [ln for ln in _git(["status", "--short",
                                  "--untracked-files=no"]).splitlines() if ln]
    untracked_count = len([ln for ln in _git(
        ["status", "--short", "--untracked-files=all"]).splitlines()
        if ln.startswith("??")])
    ab = {"upstream": None, "ahead": None, "behind": None, "in_sync": None}
    up = _git(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"]
              ).strip()
    if up:
        counts = _git(["rev-list", "--left-right", "--count",
                       "%s...HEAD" % up]).split()
        if len(counts) == 2:
            behind, ahead = int(counts[0]), int(counts[1])
            ab = {"upstream": up, "ahead": ahead, "behind": behind,
                  "in_sync": ahead == 0 and behind == 0}
    return {
        "branch": branch,
        "staged": len(staged),
        "modified": len(tracked),
        "untracked": untracked_count,
        "clean": len(staged) == 0 and len(tracked) == 0,
        "tracked_change_lines": tracked[:20],
        "ahead_behind": ab,
    }


def gather_candidate_status() -> dict:
    """Read CURRENT candidate status from committed contract constants WITHOUT
    running any heavy build chain (constants only)."""
    status: dict = {}
    try:
        import sparta_commander.intraweek_calendar_seasonality_drift_v1_rejection_record_contract as c10rj  # noqa: E501
        status["C10"] = {
            "family": c10rj.CANDIDATE_FAMILY,
            "status": c10rj.REJECTION_STATUS,
            "active": False,
            "next_action": "NONE (closed, kept on record as research lesson)",
        }
    except Exception:  # noqa: BLE001
        pass
    try:
        import sparta_commander.cross_asset_dispersion_reversion_v1_rejection_record_contract as c11rj  # noqa: E501
        status["C11"] = {
            "family": c11rj.CANDIDATE_FAMILY,
            "status": c11rj.REJECTION_STATUS,
            "active": False,
            "next_action": "NONE (closed, kept on record as research lesson)",
        }
    except Exception:  # noqa: BLE001
        pass
    try:
        import sparta_commander.failed_breakdown_reclaim_reversal_v1_rejection_record_contract as c12rj  # noqa: E501
        status["C12"] = {
            "family": c12rj.CANDIDATE_FAMILY,
            "status": c12rj.REJECTION_STATUS,
            "active": False,
            "next_action": "NONE (closed, kept on record as research lesson)",
        }
    except Exception:  # noqa: BLE001
        pass
    return status


def generate(run_dir: Path = OVERNIGHT_RUN_DIR, write: bool = True):
    run_state = load_run_state(run_dir)
    git_summary = gather_git_summary()
    candidate_status = gather_candidate_status()
    report = build_morning_report(run_state, git_summary, candidate_status)
    md = render_markdown(report)
    if write:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True),
                            encoding="utf-8")
        OUT_MD.write_text(md, encoding="utf-8")
    return report, md


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="SPARTA Autopilot Morning Report (research-only)")
    parser.add_argument("command", nargs="?", default="generate",
                        choices=("generate", "show"))
    args = parser.parse_args(argv)
    report, md = generate(write=(args.command == "generate"))
    if args.command == "show":
        print(md)
    else:
        print("run_status = %s" % report["run_status"])
        print("wrote %s" % OUT_MD.relative_to(REPO_ROOT).as_posix())
        print("wrote %s" % OUT_JSON.relative_to(REPO_ROOT).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
