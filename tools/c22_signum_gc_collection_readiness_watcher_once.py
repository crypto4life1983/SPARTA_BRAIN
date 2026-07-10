"""Candidate #22 -- Signum Trend Radar GC COLLECTION READINESS WATCHER tool
(LOCAL-ONLY; READ-ONLY; RESEARCH ONLY; ONE-SHOT).

Scans the approved dataset folder (data/external_signum_trend_radar_gc/) READ-ONLY, validates
each dated/bootstrap GC window locally (via the committed importer's structural validator),
counts the VALID distinct windows, and prints the readiness status + progress (N/20). When
the threshold is reached it surfaces the EXACT suggested human token to paste --
HUMAN_APPROVED_C22_SIGNUM_GC_FROZEN_DATA_WINDOW_REVIEW -- but NEVER auto-runs the review,
NEVER auto-runs replay, and NEVER auto-executes the token.

It fetches NOTHING (no Signum / GC / API / MCP / browser / network), writes NOTHING (read-only
parse), and does NO commit / push / git add. May be run by Windows Task Scheduler after the
importer task.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import sparta_commander.c22_signum_gc_data_collection_tracker_contract as _trk  # noqa: E402,E501
import sparta_commander.c22_signum_gc_local_export_importer_contract as _imp  # noqa: E402,E501
import sparta_commander.c22_signum_gc_collection_readiness_watcher_contract as _rw  # noqa: E402,E501

DATA_DIR = REPO_ROOT / _rw.DATA_DIR


def scan_window_facts() -> list:
    """READ-ONLY scan of the dataset folder -> per-window {filename, date, valid, reasons}.
    Parses each GC export file locally (no fetch, no write)."""
    if not DATA_DIR.is_dir():
        return []
    facts = []
    for p in sorted(DATA_DIR.glob(_trk.EXPORT_GLOB)):
        if not p.is_file():
            continue
        date = _trk._date_from_filename(p.name)
        valid = False
        reasons = []
        try:
            parsed = json.loads(p.read_text(encoding="utf-8"))
            v = _imp.validate_import_candidate(parsed)
            valid = bool(v["valid"])
            reasons = list(v["failures"])
        except Exception as exc:  # noqa: BLE001
            reasons = ["unparseable:%s" % type(exc).__name__]
        facts.append({"filename": p.name, "date": date, "valid": valid,
                      "reasons": reasons})
    return facts


def build_status() -> dict:
    # lifecycle-aware: pass the recorded facts so the consumed collection-review token is not
    # resurfaced once C22 is in the label-evidence HOLD (default-off in the pure contract).
    status = _rw.build_readiness(scan_window_facts(),
                                 review_consumed=_rw.COLLECTION_REVIEW_CONSUMED,
                                 label_review_decision=_rw.LABEL_REVIEW_DECISION)
    assert _rw.validate_readiness(status)["valid"], "readiness_failed_validation"
    return status


def main() -> int:
    s = build_status()
    print(json.dumps({
        "status": s["status"],
        "progress": s["progress"],
        "collected_valid_windows": s["collected_valid_windows"],
        "required_windows": s["required_windows"],
        "windows_remaining": s["windows_remaining"],
        "valid_window_dates": s["valid_window_dates"],
        "invalid_windows": s["invalid_windows"],
        "ready": s["ready"],
        "collection_review_consumed": s["collection_review_consumed"],
        "collection_review_gate_reached": s["collection_review_gate_reached"],
        "label_review_decision": s["label_review_decision"],
        "extension_windows": s["extension_windows"],
        "suggested_next_token": s["suggested_next_token"],
        "c22_state": s["c22_state"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
