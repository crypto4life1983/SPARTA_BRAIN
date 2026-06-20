"""Candidate #22 -- Signum Trend Radar GC LOCAL IMPORT AUTOMATION tool
(LOCAL-ONLY; RESEARCH ONLY; ONE-SHOT).

Runs the existing local importer (tools/c22_signum_gc_local_export_importer_once.py) once
against the approved inbox and prints ONE clean overall status via the pure automation
contract:
  * NO_NEW_EXPORT     -- nothing in the inbox to scan;
  * IMPORTED          -- new valid export(s) imported into the dataset folder;
  * DUPLICATE_WINDOW  -- every scanned file was already imported;
  * INVALID_ONLY / MIXED_NO_IMPORT -- nothing new imported.

It is ONE-SHOT and IDEMPOTENT: it reuses the committed importer's byte-copy/never-overwrite
logic, so re-running after an import yields DUPLICATE_WINDOW with no new writes. It installs
/ triggers NO scheduler (a human may schedule THIS command externally), makes NO network
call, connects to NO Signum / MCP / Hyperliquid, uses NO API keys / credentials, runs NO
labels / replay / optimization, and does NO commit / push / git add.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import tools.c22_signum_gc_local_export_importer_once as _importer  # noqa: E402
import sparta_commander.c22_signum_gc_data_collection_tracker_contract as _trk  # noqa: E402,E501
import sparta_commander.c22_signum_gc_import_automation_contract as _auto  # noqa: E402,E501


def collect_import_results() -> tuple:
    """Run the committed importer over the approved inbox once (read-only listing + the
    importer's own validate/byte-copy/never-overwrite). Returns (scanned, results)."""
    inbox = _importer.INBOX
    if not inbox.is_dir():
        return 0, []
    already = _importer._already_collected_dates()
    files = sorted(p for p in inbox.glob(_trk.EXPORT_GLOB) if p.is_file())
    results = []
    for src in files:
        res = _importer.import_one(src, already)
        if res.get("imported") and res.get("run_date"):
            already.add(res["run_date"])   # same-date later files -> duplicate
        results.append(res)
    return len(files), results


def run_import_automation() -> dict:
    """One automation pass -> the validated clean status summary."""
    scanned, results = collect_import_results()
    summary = _auto.summarize_automation_run(scanned, results)
    assert _auto.validate_automation_summary(summary)["valid"], "summary_failed_validation"
    return summary


def main() -> int:
    summary = run_import_automation()
    print(json.dumps({
        "overall_status": summary["overall_status"],
        "scanned": summary["scanned"],
        "new_imports": summary["new_imports"],
        "duplicates": summary["duplicates"],
        "invalid": summary["invalid"],
        "imported_filenames": summary["imported_filenames"],
        "inbox_dir": summary["inbox_dir"],
        "dest_dir": summary["dest_dir"],
        "c22_state": summary["c22_state"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
