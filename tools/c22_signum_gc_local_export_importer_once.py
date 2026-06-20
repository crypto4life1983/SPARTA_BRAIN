"""Candidate #22 -- Signum Trend Radar GC LOCAL EXPORT IMPORTER tool
(LOCAL-ONLY; RESEARCH ONLY).

Scans the local inbox (data/external_signum_trend_radar_gc_inbox/) for saved Signum GC daily
export files, parses each LOCALLY, validates + decides via the pure importer contract, and
-- for IMPORT_OK files -- BYTE-COPIES them into the C22 dataset folder
(data/external_signum_trend_radar_gc/) under the deterministic runDate filename. It NEVER
overwrites an existing destination file, NEVER mutates the JSON contents (it copies the raw
bytes), and reports the SHA256 of each imported file.

It connects to NO Signum / MCP / Hyperliquid, makes NO network call, uses NO API keys /
credentials, runs NO labels / replay, installs / triggers NO scheduler, and does NO commit /
push / git add. Originals are left in the inbox (the operator may archive them).
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import sparta_commander.c22_signum_gc_local_export_importer_contract as _imp  # noqa: E402,E501
import sparta_commander.c22_signum_gc_data_collection_tracker_contract as _trk  # noqa: E402,E501

INBOX = REPO_ROOT / _imp.INBOX_DIR
DEST = REPO_ROOT / _imp.DEST_DIR


def _sha256_bytes(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def _rel(path: Path) -> str:
    """Repo-relative posix path when possible; otherwise the plain path (e.g. tmp dirs)."""
    try:
        return str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def _already_collected_dates() -> set:
    """Decision-dates already present in the destination folder (read-only listing),
    using the tracker's filename->date mapping so the importer and tracker agree."""
    if not DEST.is_dir():
        return set()
    dates = set()
    for p in DEST.glob(_trk.EXPORT_GLOB):
        if p.is_file():
            d = _trk._date_from_filename(p.name)
            if d:
                dates.add(d)
    return dates


def import_one(src: Path, already_dates: set) -> dict:
    """Validate + (if IMPORT_OK) byte-copy one inbox file. Never overwrites, never
    mutates."""
    raw = src.read_bytes()
    try:
        parsed = json.loads(raw.decode("utf-8"))
    except Exception as exc:  # noqa: BLE001
        return {"source": src.name, "verdict": _imp.VERDICT_INVALID,
                "reasons": ["unparseable_json:%s" % type(exc).__name__],
                "imported": False}

    decision = _imp.build_import_decision(parsed, already_dates)
    check = _imp.validate_import_decision(decision)
    out = {"source": src.name, "verdict": decision["verdict"],
           "run_date": decision["run_date"],
           "destination_filename": decision["destination_filename"],
           "reasons": decision["reasons"],
           "decision_valid": check["valid"], "imported": False}

    if decision["verdict"] != _imp.VERDICT_IMPORT_OK or not check["valid"]:
        return out

    dest_path = DEST / decision["destination_filename"]
    if dest_path.exists():  # belt-and-suspenders: never overwrite
        out["verdict"] = _imp.VERDICT_DUPLICATE
        out["reasons"] = ["destination_exists:%s" % decision["destination_filename"]]
        return out

    DEST.mkdir(parents=True, exist_ok=True)
    dest_path.write_bytes(raw)   # byte-identical copy; JSON contents never mutated
    out["imported"] = True
    out["destination_path"] = _rel(dest_path)
    out["sha256"] = _sha256_bytes(raw)
    return out


def main() -> int:
    if not INBOX.is_dir():
        print(json.dumps({"inbox": _rel(INBOX),
                          "scanned": 0, "results": [],
                          "note": "inbox folder does not exist yet"}, indent=2))
        return 0
    already = _already_collected_dates()
    files = sorted(p for p in INBOX.glob(_trk.EXPORT_GLOB) if p.is_file())
    results = []
    for src in files:
        res = import_one(src, already)
        if res.get("imported") and res.get("run_date"):
            already.add(res["run_date"])   # subsequent same-date files -> duplicate
        results.append(res)

    summary = {
        "inbox": _rel(INBOX),
        "dest": _rel(DEST),
        "scanned": len(files),
        "imported": sum(1 for r in results if r.get("imported")),
        "duplicates": sum(1 for r in results
                          if r.get("verdict") == _imp.VERDICT_DUPLICATE),
        "invalid": sum(1 for r in results
                       if r.get("verdict") == _imp.VERDICT_INVALID),
        "results": results,
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
