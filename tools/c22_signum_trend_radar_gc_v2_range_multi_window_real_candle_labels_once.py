"""Candidate #22 -- Signum Trend Radar GC V2 RANGE MULTI-WINDOW REAL-CANDLE LABELS RUNNER
(READ-ONLY DRY-RUN by default; FAILS CLOSED on build; RESEARCH ONLY; ADDITIVE to V1).

Reads the EXPLICITLY FROZEN 26 GC windows (2026-06-20 .. 2026-07-15) READ-ONLY, plus each
window's retained raw top-100 + reduction sidecar WHERE THEY EXIST, computes SHA256s, and asks
the pure V2 range contract to assemble + validate the manifest. DRY-RUN by default (writes
nothing). Writing the canonical V2 artifact requires BOTH --execute-build AND the exact canonical
C22 label-build token HUMAN_DECISION_C22_ADVANCE_TO_REAL_CANDLE_LABELS_OR_REJECT (via
--build-token or C22_BUILD_TOKEN). Never overwrites; never collides with a V1 artifact name;
never mutates frozen sources; never fetches; never replays; never commits.

Provenance is honest: raw-retention activated 2026-07-10, sidecars 2026-06-28. Windows before
each activation legitimately lack that evidence (recorded, never synthesized).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import sparta_commander.c22_signum_gc_data_collection_tracker_contract as _trk  # noqa: E402
import sparta_commander.external_signum_trend_radar_gc_long_short_v2_range_multi_window_real_candle_labels_contract as _v2  # noqa: E402,E501

DATA_DIR = REPO_ROOT / _trk.DATA_DIR
RAW_DIR = DATA_DIR / "_raw_top100"
RED_DIR = DATA_DIR / "_reductions"
OUT_DIR = REPO_ROOT / _v2._v1.ARTIFACT_DIR
CANONICAL_BUILD_TOKEN = _v2._v1.NEXT_GATE_TOKEN  # HUMAN_DECISION_C22_ADVANCE_TO_REAL_CANDLE_LABELS_OR_REJECT

# --- EXPLICITLY FROZEN run parameters (no open-ended "use everything" mode) ------------------
RUN_START = "2026-06-20"
RUN_END = "2026-07-15"
RUN_EXPECTED_WINDOWS = 26
RUN_ROWS_PER_WINDOW = 50
RUN_EXPECTED_TOTAL_ROWS = 1300


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def collect_v2_window_inputs(data_dir: Path, expected_dates) -> list:
    """READ-ONLY: discover reduced windows via V1's export glob, derive each content runDate +
    SHA256 + row count, and attach retained raw top-100 + reduction sidecar SHA256s BY DATE where
    those files exist (None where they do not). Returns only windows whose runDate is in the
    expected range. Never mutates."""
    want = set(expected_dates)
    inputs = []
    for p in sorted(data_dir.glob(_trk.EXPORT_GLOB)):
        if not p.is_file():
            continue
        parsed = json.loads(p.read_text(encoding="utf-8"))
        results = parsed.get("results", [])
        run_dates = {r.get("runDate") for r in results if isinstance(r, dict)}
        run_date = next(iter(run_dates)) if len(run_dates) == 1 else "MIXED"
        if run_date not in want:
            continue
        ymd = str(run_date).replace("-", "")
        raw_files = sorted(RAW_DIR.glob("*%s*" % ymd)) if RAW_DIR.exists() else []
        sc_files = sorted(RED_DIR.glob("reduction_%s_*.json" % run_date)) if RED_DIR.exists() else []
        inputs.append({
            "source_path": str(p.relative_to(REPO_ROOT)).replace("\\", "/"),
            "run_date": run_date, "row_count": len(results), "sha256": _sha256(p),
            "parsed": parsed,
            "raw_sha256": _sha256(raw_files[0]) if raw_files else None,
            "sidecar_sha256": _sha256(sc_files[0]) if sc_files else None})
    return inputs


def authorize_artifact_write(execute_build: bool, token) -> dict:
    """PURE. Writing requires BOTH the explicit per-run build option AND the EXACT canonical
    token. Does NOT consult replay/optimization/activation/paper-live authorization. Fails closed
    on missing/wrong token or missing option."""
    if not execute_build:
        return {"authorized": False, "reason": "missing_execute_build_option"}
    if not token:
        return {"authorized": False, "reason": "missing_canonical_build_token"}
    if token != CANONICAL_BUILD_TOKEN:
        return {"authorized": False, "reason": "wrong_canonical_build_token"}
    return {"authorized": True, "reason": "authorized_by_option_and_exact_canonical_token"}


def manifest_write_eligible(record: dict, check: dict) -> bool:
    return bool(check.get("valid")) and record.get("verdict") == _v2.V2_VERDICT_READY


def write_artifact(record: dict, agg_labels: list, out_dir: Path) -> dict:
    """Write the canonical V2 artifact ATOMICALLY. Refuses to overwrite any existing file or to
    reuse either V1 artifact name."""
    out_path = Path(out_dir) / record["mw_artifact_filename"]
    if out_path.name in (_v2._v1.MW_ARTIFACT_FILENAME, _v2._v1.SINGLE_WINDOW_ARTIFACT_FILENAME):
        raise RuntimeError("refuse_collision_with_v1_artifact")
    if out_path.exists():
        raise RuntimeError("refuse_overwrite_existing_artifact:%s" % out_path.name)
    payload = _v2.build_v2_aggregate_payload(record, agg_labels)
    blob = _v2.canonical_v2_artifact_bytes(payload)
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    tmp = out_path.with_suffix(".json.tmp")
    with open(tmp, "wb") as f:
        f.write(blob)
    os.replace(tmp, out_path)
    return {"path": str(out_path), "sha256": hashlib.sha256(blob).hexdigest()}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--execute-build", action="store_true")
    ap.add_argument("--build-token", default=os.environ.get("C22_BUILD_TOKEN"))
    args = ap.parse_args()

    expected_dates = _v2._v1._daterange(RUN_START, RUN_END)
    inputs = collect_v2_window_inputs(DATA_DIR, expected_dates)
    record, agg_labels = _v2.build_range_multi_window_manifest(
        inputs, start_date=RUN_START, end_date=RUN_END,
        expected_window_count=RUN_EXPECTED_WINDOWS,
        expected_rows_per_window=RUN_ROWS_PER_WINDOW,
        expected_total_rows=RUN_EXPECTED_TOTAL_ROWS)
    check = _v2.validate_range_multi_window(record)
    auth = authorize_artifact_write(args.execute_build, args.build_token)
    eligible = manifest_write_eligible(record, check)

    summary = {
        "mode": ("BUILD" if auth["authorized"] else "DRY_RUN_MANIFEST_ONLY"),
        "verdict": record["verdict"], "validator_valid": check["valid"],
        "validator_failures": check["failures"], "blockers": record["blockers"],
        "windows_seen": len(inputs),
        "window_range": [record["window_start"], record["window_end"]],
        "expected_windows": record["expected_windows"],
        "aggregate_manifest_sha256": record["aggregate_manifest_sha256"],
        "canonical_label_payload_sha256": record["canonical_label_payload_sha256"],
        "aggregate_label_counts": record["aggregate_label_counts"],
        "aggregate_labels_built": record["aggregate_labels_built"],
        "provenance_tier_counts": record["provenance_tier_counts"],
        "pre_build_status": record["pre_build_status"],
        "mw_artifact_filename": record["mw_artifact_filename"],
        "build_authorization": auth, "manifest_write_eligible": eligible,
        "replay_authorized": record["replay_authorized"],
        "execution_authorized": record["execution_authorized"],
        "artifact_written": False}

    if auth["authorized"]:
        if not eligible:
            summary["build_refused"] = ("manifest_not_ready_or_invalid: %s / %s"
                                        % (record["verdict"], check["failures"]))
        else:
            res = write_artifact(record, agg_labels, OUT_DIR)
            summary["artifact_written"] = True
            summary["artifact_path"] = str(Path(res["path"]).relative_to(REPO_ROOT)).replace("\\", "/")
            summary["artifact_sha256"] = res["sha256"]
    else:
        summary["build_refused"] = auth["reason"]

    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
