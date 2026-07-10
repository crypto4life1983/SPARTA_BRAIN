"""Candidate #22 -- Signum Trend Radar GC MULTI-WINDOW REAL-CANDLE ENTRY-LABELS RUNNER
(READ-ONLY DRY-RUN by default; FAILS CLOSED on build; RESEARCH ONLY).

Reads the 20 locally-staged frozen GC windows (2026-06-20 .. 2026-07-09) READ-ONLY, computes
each window's SHA256 + runDate + row count, and asks the pure multi-window labels contract to
assemble + validate the manifest. By default it performs a DRY-RUN ONLY: it prints the
manifest summary and does NOT build the 1,000-row aggregate artifact and writes nothing.

ARTIFACT-WRITE AUTHORIZATION (corrected gate) -- writing the canonical artifact requires BOTH:
  (1) the explicit per-run build option  --execute-build ; AND
  (2) the EXACT canonical C22 label-build human token, supplied via --build-token or the
      C22_BUILD_TOKEN env var, equal to
      "HUMAN_DECISION_C22_ADVANCE_TO_REAL_CANDLE_LABELS_OR_REJECT".
The write gate DOES NOT require EXECUTION_AUTHORIZED / replay / optimization / activation /
paper-live authorization: EXECUTION_AUTHORIZED means TRADE/ORDER/BROKER execution only and
stays permanently False at this stage -- it must never gate an analytical label build.

The repo stays FAIL-CLOSED by default (committed BUILD_AUTHORIZED=False; no committed True
state; no tracked mutation merely to run a build): authorization is a per-run CLI/env signal,
never a committed flag flip. Even when authorized, the runner still fails closed if the
manifest is not READY/valid, if any source/schema/date/SHA check fails, or on output
collision (never overwrites). It never mutates frozen sources, never date-tags the artifact
with today's date (name is bound to the window range), and never touches the historical 06-20
single-window artifact. No network, credentials, replay, or commit/push.
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

import sparta_commander.c22_signum_gc_data_collection_tracker_contract as _trk  # noqa: E402,E501
import sparta_commander.external_signum_trend_radar_gc_long_short_v1_multi_window_real_candle_labels_contract as _mw  # noqa: E402,E501

DATA_DIR = REPO_ROOT / _trk.DATA_DIR
OUT_DIR = REPO_ROOT / _mw.ARTIFACT_DIR

# the exact canonical human token that (with --execute-build) authorizes an artifact write.
CANONICAL_BUILD_TOKEN = _mw.NEXT_GATE_TOKEN  # HUMAN_DECISION_C22_ADVANCE_TO_REAL_CANDLE_LABELS_OR_REJECT


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


def authorize_artifact_write(execute_build: bool, token) -> dict:
    """PURE. The corrected artifact-write authorization gate. Writing requires BOTH the
    explicit per-run build option AND the EXACT canonical token. It does NOT consult
    EXECUTION_AUTHORIZED / replay / optimization / activation / paper-live authorization.
    Returns {'authorized': bool, 'reason': str}. Fails closed on missing/wrong token or
    missing option -- the option alone is never sufficient."""
    if not execute_build:
        return {"authorized": False, "reason": "missing_execute_build_option"}
    if not token:
        return {"authorized": False, "reason": "missing_canonical_build_token"}
    if token != CANONICAL_BUILD_TOKEN:
        return {"authorized": False, "reason": "wrong_canonical_build_token"}
    return {"authorized": True, "reason": "authorized_by_option_and_exact_canonical_token"}


def manifest_write_eligible(record: dict, check: dict) -> bool:
    """PURE. Independent of authorization: the manifest must be READY + validator-valid before
    any write is even considered (fail closed on any source/schema/date/SHA/manifest failure)."""
    return bool(check.get("valid")) and record.get("verdict") == _mw.VERDICT_MANIFEST_READY


def write_artifact(record: dict, agg_labels: list, out_dir: Path) -> dict:
    """Write the canonical multi-window artifact ATOMICALLY into out_dir. Refuses to overwrite
    an existing file or to use the single-window artifact name. Returns {path, sha256}. Callers
    MUST have already checked authorize_artifact_write() + manifest_write_eligible()."""
    out_path = Path(out_dir) / _mw.MW_ARTIFACT_FILENAME
    if out_path.name == _mw.SINGLE_WINDOW_ARTIFACT_FILENAME:
        raise RuntimeError("refuse_collision_with_single_window_artifact")
    if out_path.exists():
        raise RuntimeError("refuse_overwrite_existing_artifact:%s" % out_path.name)
    payload = _mw.build_aggregate_payload(record, agg_labels)
    blob = _mw.canonical_payload_bytes(payload)
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    tmp = out_path.with_suffix(".json.tmp")
    with open(tmp, "wb") as f:
        f.write(blob)
    os.replace(tmp, out_path)                       # atomic finalize
    return {"path": str(out_path), "sha256": hashlib.sha256(blob).hexdigest()}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--execute-build", action="store_true",
                    help="per-run build option; REQUIRED together with --build-token to write")
    ap.add_argument("--build-token", default=os.environ.get("C22_BUILD_TOKEN"),
                    help="exact canonical C22 label-build token (or C22_BUILD_TOKEN env var)")
    args = ap.parse_args()

    inputs = collect_window_inputs()
    record, agg_labels = _mw.build_multi_window_manifest(inputs)
    check = _mw.validate_multi_window(record)
    auth = authorize_artifact_write(args.execute_build, args.build_token)
    eligible = manifest_write_eligible(record, check)

    summary = {
        "mode": ("BUILD" if auth["authorized"] else "DRY_RUN_MANIFEST_ONLY"),
        "verdict": record["verdict"], "validator_valid": check["valid"],
        "blockers": record["blockers"], "windows_seen": len(inputs),
        "window_range": [record["window_start"], record["window_end"]],
        "aggregate_manifest_sha256": record["aggregate_manifest_sha256"],
        "aggregate_label_counts": record["aggregate_label_counts"],
        "aggregate_labels_built_in_memory": record["aggregate_labels_built"],
        "mw_artifact_filename": record["mw_artifact_filename"],
        "build_authorization": auth,
        "manifest_write_eligible": eligible,
        "committed_build_authorized_default": _mw.BUILD_AUTHORIZED,     # stays False
        "execution_authorized": _mw.EXECUTION_AUTHORIZED,              # stays False; not a gate
        "artifact_written": False,
    }

    if auth["authorized"]:
        if not eligible:
            summary["build_refused"] = ("manifest_not_ready_or_invalid: %s / %s"
                                        % (record["verdict"], check["failures"]))
        else:
            res = write_artifact(record, agg_labels, OUT_DIR)   # raises on collision/overwrite
            summary["artifact_written"] = True
            summary["artifact_path"] = str(Path(res["path"]).relative_to(REPO_ROOT)).replace("\\", "/")
            summary["artifact_sha256"] = res["sha256"]
    else:
        summary["build_refused"] = auth["reason"]

    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
