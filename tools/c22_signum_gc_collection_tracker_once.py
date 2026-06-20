"""Candidate #22 -- Signum Trend Radar GC data-collection tracker RUNNER
(READ-ONLY; RESEARCH ONLY).

Lists the locally-staged frozen daily GC export files READ-ONLY (a directory listing only --
it opens / parses / fetches NOTHING), builds the pure collection-progress status, and prints
it. It connects to NO Signum / MCP / Hyperliquid, fetches NO data, stages NO file, runs NO
labels / replay, installs / triggers NO scheduler, and does NO commit / push / git add.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import sparta_commander.c22_signum_gc_data_collection_tracker_contract as _trk  # noqa: E402,E501


def scan_export_filenames(repo_root: Path = REPO_ROOT) -> list:
    """READ-ONLY directory listing of frozen daily GC export basenames. No file open, no
    parse, no fetch. Returns [] if the directory does not exist yet."""
    data_dir = Path(repo_root) / _trk.DATA_DIR
    if not data_dir.is_dir():
        return []
    return sorted(p.name for p in data_dir.glob(_trk.EXPORT_GLOB) if p.is_file())


def scan_collection_status(repo_root: Path = REPO_ROOT) -> dict:
    """Build the collection status from a read-only listing. No mutation."""
    return _trk.build_collection_status(scan_export_filenames(repo_root))


def main() -> int:
    status = scan_collection_status(REPO_ROOT)
    check = _trk.validate_collection_status(status)
    if not check["valid"]:
        raise RuntimeError("tracker_status_failed_validation: %s" % check["failures"])
    print(_trk.render_collection_section_markdown(status))
    print()
    print(json.dumps({
        "collected_windows": status["collected_windows"],
        "required_windows": status["required_windows"],
        "windows_remaining": status["windows_remaining"],
        "pct_complete": status["pct_complete"],
        "next_export_date": status["next_export_date"],
        "ready_for_rereview": status["ready_for_rereview"],
        "c22_state": status["c22_state"],
        "next_human_action_when_ready": status["next_human_action_when_ready"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
