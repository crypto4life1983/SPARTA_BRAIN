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

import datetime as _dt
import hashlib
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import sparta_commander.c22_signum_gc_local_export_importer_contract as _imp  # noqa: E402,E501
import sparta_commander.c22_signum_gc_data_collection_tracker_contract as _trk  # noqa: E402,E501

INBOX = REPO_ROOT / _imp.INBOX_DIR
DEST = REPO_ROOT / _imp.DEST_DIR
# Quarantine lives INSIDE the (gitignored) inbox dir so it is auto-ignored without editing
# .gitignore; a subfolder + non-EXPORT_GLOB filenames keep it invisible to every importer/
# tracker scan (all of which use a non-recursive glob of EXPORT_GLOB).
QUARANTINE_DIR = INBOX / "_quarantine"
# Reduction provenance lives in a subfolder of the (gitignored) dataset dir, off the
# EXPORT_GLOB pattern + in a subfolder, so the tracker's non-recursive window scan never sees
# it and no provenance file is ever counted as a window or tracked by git.
REDUCTION_LOG_DIR = DEST / "_reductions"

# Immutable raw top-100 retention (ADDITIVE). Only reduced (top-100 -> top-50) windows get a
# byte-identical raw archive; native top-50 windows never do. Lives in a subfolder of the
# gitignored dataset dir, off EXPORT_GLOB, so the tracker's non-recursive window scan never
# counts it and it is never a git-tracked artifact. It NEVER replaces the canonical top-50.
RAW_TOP100_DIRNAME = "_raw_top100"
SOURCE_TYPE_NATIVE = "native_top50"
SOURCE_TYPE_REDUCED = "reduced_top50"
SOURCE_TYPE_RAW_RETAINED = "raw_top100_retained"


def _raw_top100_dir() -> Path:
    """Resolved at call time from the (test-monkeypatchable) DEST global."""
    return DEST / RAW_TOP100_DIRNAME


def _raw_top100_name(run_date: str) -> str:
    return "gc_crypto_trendradar_daily_%s_raw_top100.json" % str(run_date).replace("-", "")


def _write_raw_top100(raw: bytes, run_date: str, row_count: int) -> dict:
    """Preserve a BYTE-IDENTICAL copy of the original 100-row vendor file as immutable
    evidence. Atomic (temp + os.replace); refuses to overwrite an existing archive; never
    touches the canonical top-50 dataset. Returns {path, sha256, row_count, source_type}."""
    out_dir = _raw_top100_dir()
    out_path = out_dir / _raw_top100_name(run_date)
    if out_path.exists():                        # immutable after admission: never overwrite
        raise RuntimeError("refuse_overwrite_raw_top100:%s" % out_path.name)
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_path.with_suffix(".json.tmp")
    with open(tmp, "wb") as f:
        f.write(raw)                             # byte-identical original vendor bytes
    os.replace(tmp, out_path)                    # atomic finalize
    return {"path": _rel(out_path), "sha256": _sha256_bytes(raw),
            "row_count": row_count, "source_type": SOURCE_TYPE_RAW_RETAINED}


def _today_iso() -> str:
    """The local machine date (ISO YYYY-MM-DD). The only clock read in the import path; the
    pure contract stays clock-free and receives this value as `today`."""
    return _dt.date.today().isoformat()


def _sha256_bytes(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


# map a rejection verdict -> the human-readable quarantine reason
_QUARANTINE_REASON = {
    _imp.VERDICT_FUTURE_DATED: "future_dated_export_decision_date_after_local_machine_date",
    _imp.VERDICT_ANOMALOUS: "anomalous_shape_non_canonical_or_oversize_export",
}


def _quarantine_rejected_export(src: Path, decision: dict) -> dict:
    """Move a rejected inbox export (future-dated OR anomalous-shape) OUT of active collection
    into the gitignored quarantine area, writing a sidecar note (reason, timestamp, source,
    destination, size, SHA-256). Never overwrites, never deletes the payload (it is MOVED, not
    removed), and never writes into the dataset folder."""
    raw = src.read_bytes()
    sha = _sha256_bytes(raw)
    size = len(raw)
    run_date = decision.get("run_date") or "unknown_date"
    qdir = QUARANTINE_DIR / str(run_date)
    qdir.mkdir(parents=True, exist_ok=True)
    # unique, non-EXPORT_GLOB destination name (timestamp-stamped) -> never collides/overwrites
    stamp = _dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    q_payload = qdir / ("inbox__%s__%s" % (stamp, src.name))
    note = {
        "quarantine_reason": _QUARANTINE_REASON.get(decision["verdict"], "rejected_export"),
        "verdict": decision["verdict"],
        "detail": decision.get("reasons"),
        "run_date": run_date,
        "local_machine_date": decision.get("today"),
        "raw_bytes": decision.get("raw_bytes"),
        "compact_bytes": decision.get("compact_bytes"),
        "quarantined_at": _dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "source_path": _rel(src),
        "destination_path": _rel(q_payload),
        "size_bytes": size,
        "sha256": sha,
        "status": "QUARANTINED_NOT_DELETED",
        "restore_note": ("a human must re-validate and re-run the standard import to "
                         "re-admit this window; it never entered the active dataset"),
    }
    (qdir / (q_payload.name + ".note.json")).write_text(
        json.dumps(note, indent=2, sort_keys=True), encoding="utf-8")
    src.rename(q_payload)   # MOVE out of the inbox (not a delete); payload bytes preserved
    return {"source": src.name, "verdict": decision["verdict"],
            "run_date": run_date, "reasons": decision["reasons"],
            "imported": False, "quarantined": True,
            "quarantine_path": _rel(q_payload), "sha256": sha, "size_bytes": size}


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


def _canonical_bytes(derived: dict) -> bytes:
    """Deterministic minified bytes for a derived canonical window (same compact form as the
    legacy 50-row files: no extra whitespace, UTF-8)."""
    return json.dumps(derived, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _write_reduction_provenance(src: Path, raw: bytes, parsed: dict, derived: dict,
                                derived_bytes: bytes, dest_path: Path,
                                raw_top100_info: dict | None = None) -> str:
    """Write the ignored provenance sidecar for a top-100 -> top-50 reduction. Returns the
    repo-relative provenance path. Lives under the gitignored dataset dir, off EXPORT_GLOB.
    Extended additively with source_type + the retained raw top-100 provenance."""
    run_date = _imp.extract_run_date(parsed) or "unknown_date"
    REDUCTION_LOG_DIR.mkdir(parents=True, exist_ok=True)
    info = raw_top100_info or {}
    note = {
        "source_type": SOURCE_TYPE_REDUCED,
        "reducer": _imp.REDUCER_ID,
        "vendor_instruction_quote": (
            "Signum/Michael: users got a nice upgrade (50 -> 100 rows); "
            "if you need 50 simply take the first 50 rows only."),
        "original_filename": src.name,
        "original_sha256": _sha256_bytes(raw),
        "original_total": parsed.get("total"),
        "original_results": len(parsed.get("results") or []),
        "canonical_total": derived.get("total"),
        "canonical_results": len(derived.get("results") or []),
        "canonical_destination": _rel(dest_path),
        "canonical_sha256": _sha256_bytes(derived_bytes),
        # additive raw top-100 retention provenance
        "raw_top100_retained": bool(raw_top100_info),
        "raw_top100_path": info.get("path"),
        "raw_top100_sha256": info.get("sha256"),
        "raw_top100_row_count": info.get("row_count"),
        "raw_top100_source_type": (SOURCE_TYPE_RAW_RETAINED if raw_top100_info else None),
        "run_date": run_date,
        "reduced_at": _dt.datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    stamp = _dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    prov = REDUCTION_LOG_DIR / ("reduction_%s_%s.json" % (run_date, stamp))
    prov.write_text(json.dumps(note, indent=2, sort_keys=True), encoding="utf-8")
    return _rel(prov)


def _reduce_and_import(src: Path, raw: bytes, parsed: dict, decision: dict,
                       already_dates: set, today: str) -> dict:
    """Derive the canonical top-50 window from a reducible top-100 export and import THAT
    (never the raw 100-row file). Re-validates the derived window through the same guarded
    decision path; writes a provenance sidecar. Never overwrites."""
    derived = _imp.derive_canonical_top50(parsed)
    derived_bytes = _canonical_bytes(derived)
    dd = _imp.build_import_decision(derived, already_dates, today=today,
                                    raw_bytes=len(derived_bytes),
                                    compact_bytes=len(derived_bytes))
    dcheck = _imp.validate_import_decision(dd)
    out = {"source": src.name, "verdict": decision["verdict"],
           "run_date": decision["run_date"],
           "destination_filename": dd["destination_filename"],
           "reasons": decision["reasons"], "reduced": True, "reducer": _imp.REDUCER_ID,
           "original_total": parsed.get("total"),
           "original_sha256": _sha256_bytes(raw),
           "decision_valid": dcheck["valid"], "imported": False}

    # derived window must be a clean, non-duplicate IMPORT_OK to land in the dataset
    if dd["verdict"] == _imp.VERDICT_DUPLICATE:
        out["verdict"] = _imp.VERDICT_DUPLICATE
        out["reasons"] = list(dd["reasons"])
        return out
    if dd["verdict"] != _imp.VERDICT_IMPORT_OK or not dcheck["valid"]:
        out["reasons"] = ["derived_window_not_importable:%s" % dd["verdict"]]
        return out

    dest_path = DEST / dd["destination_filename"]
    if dest_path.exists():            # never overwrite
        out["verdict"] = _imp.VERDICT_DUPLICATE
        out["reasons"] = ["destination_exists:%s" % dd["destination_filename"]]
        return out

    DEST.mkdir(parents=True, exist_ok=True)
    dest_path.write_bytes(derived_bytes)          # write the DERIVED canonical 50-row window
    out["imported"] = True
    out["destination_path"] = _rel(dest_path)
    out["sha256"] = _sha256_bytes(derived_bytes)
    out["source_type"] = SOURCE_TYPE_REDUCED
    # ADDITIVE: preserve the immutable raw top-100 evidence (never replaces the canonical
    # top-50; collision-refusing + atomic). Retention is supplementary -- a failure here never
    # breaks or reverts the already-succeeded canonical import.
    raw_info = None
    try:
        raw_info = _write_raw_top100(
            raw, out["run_date"] or _imp.extract_run_date(parsed),
            len(parsed.get("results") or []))
        out["raw_top100_retained"] = True
        out["raw_top100_path"] = raw_info["path"]
        out["raw_top100_sha256"] = raw_info["sha256"]
        out["raw_top100_row_count"] = raw_info["row_count"]
    except Exception as exc:  # noqa: BLE001
        out["raw_top100_retained"] = False
        out["raw_top100_retention_error"] = "%s:%s" % (type(exc).__name__, exc)
    out["provenance_path"] = _write_reduction_provenance(
        src, raw, parsed, derived, derived_bytes, dest_path, raw_top100_info=raw_info)
    return out


def import_one(src: Path, already_dates: set, today: str | None = None) -> dict:
    """Validate + (if IMPORT_OK) byte-copy one inbox file. Never overwrites, never mutates.
    A future-dated export (decision date after the local machine date) is QUARANTINED out of
    the inbox and never enters the dataset. `today` defaults to the real local date."""
    today = today or _today_iso()
    raw = src.read_bytes()
    try:
        parsed = json.loads(raw.decode("utf-8"))
    except Exception as exc:  # noqa: BLE001
        return {"source": src.name, "verdict": _imp.VERDICT_INVALID,
                "reasons": ["unparseable_json:%s" % type(exc).__name__],
                "imported": False}

    # raw size + minified ("compact") size feed the same-day shape/size anomaly guard
    raw_bytes = len(raw)
    compact_bytes = len(json.dumps(parsed, separators=(",", ":")).encode("utf-8"))
    decision = _imp.build_import_decision(parsed, already_dates, today=today,
                                          raw_bytes=raw_bytes, compact_bytes=compact_bytes)
    check = _imp.validate_import_decision(decision)

    # data-integrity guards: future-dated OR anomalous-shape valid export -> quarantine
    if decision["verdict"] in (_imp.VERDICT_FUTURE_DATED, _imp.VERDICT_ANOMALOUS) and \
            check["valid"]:
        res = _quarantine_rejected_export(src, decision)
        res["decision_valid"] = check["valid"]
        return res

    # vendor top-100 export -> derive + import the canonical top-50 window (first 50 rows)
    if decision["verdict"] == _imp.VERDICT_REDUCIBLE and check["valid"]:
        return _reduce_and_import(src, raw, parsed, decision, already_dates, today)

    out = {"source": src.name, "verdict": decision["verdict"],
           "run_date": decision["run_date"],
           "destination_filename": decision["destination_filename"],
           "reasons": decision["reasons"],
           "shape_warnings": decision.get("shape_warnings") or [],
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
    out["source_type"] = SOURCE_TYPE_NATIVE   # native top-50: NO raw-top-100 archive created
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
        "reduced_top100_to_top50": sum(1 for r in results if r.get("reduced")),
        "duplicates": sum(1 for r in results
                          if r.get("verdict") == _imp.VERDICT_DUPLICATE),
        "invalid": sum(1 for r in results
                       if r.get("verdict") == _imp.VERDICT_INVALID),
        "quarantined": sum(1 for r in results if r.get("quarantined")),
        "quarantined_future_dated": sum(
            1 for r in results
            if r.get("quarantined") and r.get("verdict") == _imp.VERDICT_FUTURE_DATED),
        "quarantined_anomalous": sum(
            1 for r in results
            if r.get("quarantined") and r.get("verdict") == _imp.VERDICT_ANOMALOUS),
        "results": results,
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
