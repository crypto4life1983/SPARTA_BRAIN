"""Candidate #22 -- Signum Trend Radar GC MULTI-WINDOW REAL-CANDLE ENTRY-LABELS RUNNER
(READ-ONLY DRY-RUN by default; FAILS CLOSED on build; RESEARCH ONLY).

Reads the 20 locally-staged frozen GC windows (2026-06-20 .. 2026-07-09) READ-ONLY, computes
each window's SHA256 + runDate + row count, and asks the pure multi-window labels contract to
assemble + validate the manifest. By default it performs a DRY-RUN ONLY: it prints the
manifest summary and does NOT build the 1,000-row aggregate and does NOT write any artifact.

It FAILS CLOSED on the real build: the aggregate artifact is written ONLY when BOTH the
contract's BUILD_AUTHORIZED flag is True AND the operator passes --execute-build. Today
BUILD_AUTHORIZED is False (execution is a separate human gate), so this runner can only
dry-run. It never mutates the frozen source files, never date-tags the artifact with today's
date (the name is bound to the window date range), and never overwrites the historical
single-window 06-20 artifact. No network, no credentials, no replay, no commit/push.
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import sparta_commander.c22_signum_gc_data_collection_tracker_contract as _trk  # noqa: E402,E501
import sparta_commander.external_signum_trend_radar_gc_long_short_v1_multi_window_real_candle_labels_contract as _mw  # noqa: E402,E501

DATA_DIR = REPO_ROOT / _trk.DATA_DIR
OUT_DIR = REPO_ROOT / _mw.ARTIFACT_DIR


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def collect_window_inputs() -> list:
    """READ-ONLY: load each frozen window file, deriving its content runDate + SHA256 + row
    count. Never mutates. Returns the list the pure contract validates."""
    inputs = []
    for p in sorted(DATA_DIR.glob(_trk.EXPORT_GLOB)):
        if not p.is_file():
            continue
        parsed = json.loads(p.read_text(encoding="utf-8"))
        results = parsed.get("results", [])
        run_dates = {r.get("runDate") for r in results if isinstance(r, dict)}
        run_date = next(iter(run_dates)) if len(run_dates) == 1 else "MIXED"
        inputs.append({
            "source_path": str(p.relative_to(REPO_ROOT)).replace("\\", "/"),
            "run_date": run_date, "row_count": len(results),
            "sha256": _sha256(p), "parsed": parsed})
    return inputs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--execute-build", action="store_true",
                    help="attempt the real 1000-row build (refused unless BUILD_AUTHORIZED)")
    args = ap.parse_args()

    inputs = collect_window_inputs()
    record, agg_labels = _mw.build_multi_window_manifest(inputs)
    check = _mw.validate_multi_window(record)

    summary = {
        "mode": "DRY_RUN_MANIFEST_ONLY",
        "verdict": record["verdict"],
        "validator_valid": check["valid"],
        "validator_failures": check["failures"],
        "blockers": record["blockers"],
        "windows_seen": len(inputs),
        "expected_windows": record["expected_windows"],
        "window_range": [record["window_start"], record["window_end"]],
        "aggregate_manifest_sha256": record["aggregate_manifest_sha256"],
        "aggregate_label_counts": record["aggregate_label_counts"],
        "aggregate_labels_built_in_memory": record["aggregate_labels_built"],
        "mw_artifact_filename": record["mw_artifact_filename"],
        "build_authorized": record["build_authorized"],
        "execution_authorized": record["execution_authorized"],
        "per_window": [{k: p[k] for k in ("run_date", "sha256", "row_count",
                                          "structurally_valid", "label_counts")}
                       for p in record["per_window"]],
        "artifact_written": False,
    }

    # FAIL CLOSED: only a future authorized gate (BUILD_AUTHORIZED True) + explicit flag writes.
    if args.execute_build:
        if not _mw.BUILD_AUTHORIZED or not _mw.EXECUTION_AUTHORIZED:
            summary["build_refused"] = (
                "BUILD_AUTHORIZED/EXECUTION_AUTHORIZED are False -- execution is a separate "
                "human gate (%s). No artifact written." % _mw.NEXT_GATE_TOKEN)
            print(json.dumps(summary, indent=2, sort_keys=True))
            return 0
        # (reached only under a future explicit authorization; kept minimal + collision-safe)
        if not check["valid"] or record["verdict"] != _mw.VERDICT_MANIFEST_READY:
            raise RuntimeError("manifest_not_ready_or_invalid: %s / %s"
                               % (record["verdict"], check["failures"]))
        out_path = OUT_DIR / _mw.MW_ARTIFACT_FILENAME
        if out_path.name == _mw.SINGLE_WINDOW_ARTIFACT_FILENAME or out_path.exists():
            raise RuntimeError("refuse_overwrite_or_collision: %s" % out_path.name)
        payload = _mw.build_aggregate_payload(record, agg_labels)
        blob = _mw.canonical_payload_bytes(payload)
        tmp = out_path.with_suffix(".json.tmp")
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        with open(tmp, "wb") as f:
            f.write(blob)
        os.replace(tmp, out_path)           # atomic finalize
        summary["artifact_written"] = True
        summary["artifact_path"] = str(out_path.relative_to(REPO_ROOT)).replace("\\", "/")
        summary["artifact_sha256"] = hashlib.sha256(blob).hexdigest()

    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
