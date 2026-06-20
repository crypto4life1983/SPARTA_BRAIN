"""Candidate #22 -- Signum Trend Radar GC DOWNLOAD PICKUP tool
(LOCAL-ONLY; RESEARCH ONLY; ONE-SHOT).

Reduces the manual step to "download/export the daily GC JSON into a local drop folder". This
tool then, LOCALLY:
  1. scans the approved drop folder (default: the user's Downloads, override with the
     C22_GC_DROP_FOLDER env var) for candidate GC JSON files (default glob *trendradar*.json,
     override with C22_GC_DROP_GLOB);
  2. validates each candidate with the committed importer rules;
  3. BYTE-COPIES only valid, not-already-collected GC exports into the inbox under the
     deterministic runDate filename (never overwriting, never mutating);
  4. runs the existing import automation (inbox -> dataset);
  5. runs the existing readiness watcher and reports progress (N/20). At 20/20 it surfaces
     the suggested human token HUMAN_APPROVED_C22_SIGNUM_GC_FROZEN_DATA_WINDOW_REVIEW as a
     SUGGESTION ONLY -- it never auto-executes it.

It performs NO Signum login, NO fetch (Signum/GC/browser/API/MCP/network), stores NO
credentials/cookies/tokens/session files, implements NO browser automation, and does NO
commit / push / git add. May be run by Windows Task Scheduler if approved separately.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import sparta_commander.c22_signum_gc_data_collection_tracker_contract as _trk  # noqa: E402,E501
import sparta_commander.c22_signum_gc_download_pickup_contract as _pk  # noqa: E402,E501
import tools.c22_signum_gc_local_export_importer_once as _importer  # noqa: E402
import tools.c22_signum_gc_import_automation_once as _autorun  # noqa: E402
import tools.c22_signum_gc_collection_readiness_watcher_once as _watcher  # noqa: E402


def _default_drop_folder() -> Path:
    override = os.environ.get("C22_GC_DROP_FOLDER")
    if override:
        return Path(override)
    return Path(os.environ.get("USERPROFILE", str(Path.home()))) / "Downloads"


DROP_FOLDER = _default_drop_folder()
DROP_GLOB = os.environ.get("C22_GC_DROP_GLOB", "*trendradar*.json")


def _already_collected_dates() -> set:
    """Decision-dates already present in the dataset OR the inbox (read-only listing), so a
    candidate is never duplicated into the inbox."""
    dates = set()
    for folder in (_importer.DEST, _importer.INBOX):
        if folder.is_dir():
            for p in folder.glob(_trk.EXPORT_GLOB):
                if p.is_file():
                    d = _trk._date_from_filename(p.name)
                    if d:
                        dates.add(d)
    return dates


def pickup_drop_folder() -> tuple:
    """Scan the drop folder, validate, and byte-copy valid new GC exports into the inbox.
    Never overwrites, never mutates. Returns (scanned, results)."""
    if not DROP_FOLDER.is_dir():
        return 0, []
    already = _already_collected_dates()
    files = sorted(p for p in DROP_FOLDER.glob(DROP_GLOB) if p.is_file())
    results = []
    for src in files:
        res = {"source": src.name, "verdict": _pk.PICKUP_IGNORED_INVALID,
               "run_date": None, "inbox_filename": None, "reasons": [], "copied": False}
        try:
            raw = src.read_bytes()
            parsed = json.loads(raw.decode("utf-8"))
        except Exception as exc:  # noqa: BLE001
            res["reasons"] = ["unparseable:%s" % type(exc).__name__]
            results.append(res)
            continue
        cls = _pk.classify_drop_candidate(parsed, already)
        res.update({"verdict": cls["verdict"], "run_date": cls["run_date"],
                    "inbox_filename": cls["inbox_filename"], "reasons": cls["reasons"]})
        if cls["should_pickup"] and cls["inbox_filename"]:
            dest = _importer.INBOX / cls["inbox_filename"]
            if dest.exists():   # never overwrite
                res["verdict"] = _pk.PICKUP_DUPLICATE
                res["reasons"] = ["inbox_file_exists:%s" % cls["inbox_filename"]]
            else:
                _importer.INBOX.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(raw)   # byte-identical copy; never mutate
                res["copied"] = True
                res["sha256"] = hashlib.sha256(raw).hexdigest()
                already.add(cls["run_date"])   # same-date later drops -> duplicate
        results.append(res)
    return len(files), results


def run_pickup_chain() -> dict:
    """Full chain: pickup -> import automation -> readiness watcher -> validated summary."""
    scanned, pickup_results = pickup_drop_folder()
    _autorun.run_import_automation()          # inbox -> dataset (idempotent, no overwrite)
    readiness = _watcher.build_status()       # read-only progress report
    summary = _pk.summarize_pickup_chain(scanned, pickup_results, readiness)
    assert _pk.validate_pickup_chain(summary)["valid"], "pickup_summary_failed_validation"
    return summary


def main() -> int:
    s = run_pickup_chain()
    print(json.dumps({
        "drop_folder": str(DROP_FOLDER),
        "drop_glob": DROP_GLOB,
        "drop_scanned": s["drop_scanned"],
        "picked_up": s["picked_up"],
        "duplicates": s["duplicates"],
        "ignored_invalid": s["ignored_invalid"],
        "picked_up_filenames": s["picked_up_filenames"],
        "overall_status": s["overall_status"],
        "progress": s["readiness"]["progress"],
        "ready_for_human_review": s["ready_for_human_review"],
        "suggested_next_token": s["suggested_next_token"],
        "c22_state": s["c22_state"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
