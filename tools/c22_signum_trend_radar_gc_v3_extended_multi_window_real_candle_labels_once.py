"""Candidate #22 -- Signum Trend Radar GC V3_EXTENDED MULTI-WINDOW REAL-CANDLE LABELS RUNNER
(READ-ONLY DRY-RUN by default; FAILS CLOSED on build; RESEARCH ONLY; ADDITIVE to V2).

Reuses the UNCHANGED V2 range contract with explicitly frozen V3 run profiles. V3 is ADDITIONAL
evidence and diagnostics only: it never replaces the frozen V2 26-window artifact, never changes
the 88 V2 decisive signals, and every window dated after the accepted replay-spec entry cutoff
(2026-07-15, NO_NEW_ENTRY_AFTER) is tagged EXIT_ONLY in the manifest so it can never be silently
admitted as an entry into the V2 decisive experiment.

Because 2026-08-16 has no admitted export, continuity is NOT manufactured: the contiguous 82-window
profile is expected to fail the V2 contract's contiguity validation until (if ever) that window is
admitted through the guarded pickup chain. The two SEGMENT profiles (A: 2026-06-20..2026-08-15,
B: 2026-08-17..2026-09-09) are the honest representation of the collection today.

Writing an artifact requires BOTH --execute-build AND the exact token
HUMAN_APPROVED_BUILD_C22_V3_EXTENDED_LABEL_EVIDENCE_ONLY (via --build-token or C22_V3_BUILD_TOKEN).
Artifacts are written under a SEPARATE sub-directory (detector_labels/v3_extended/) with the V2
naming convention (validator requires the v2 basename), never overwriting. Never mutates frozen
sources; never fetches; never replays; never commits.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import date as _date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import sparta_commander.external_signum_trend_radar_gc_long_short_v2_range_multi_window_real_candle_labels_contract as _v2  # noqa: E402,E501
import tools.c22_signum_trend_radar_gc_v2_range_multi_window_real_candle_labels_once as _v2run  # noqa: E402

DATA_DIR = _v2run.DATA_DIR
OUT_DIR = _v2run.OUT_DIR / "v3_extended"
V3_BUILD_TOKEN = "HUMAN_APPROVED_BUILD_C22_V3_EXTENDED_LABEL_EVIDENCE_ONLY"
ENTRY_CUTOFF = "2026-07-15"           # accepted replay spec NO_NEW_ENTRY_AFTER (never changed here)
EXIT_ONLY_MARKER = "EXIT_ONLY"
MISSING_ADMITTED_WINDOW = "2026-08-16"  # no admitted export; continuity is never manufactured
V3_ROLE = "ADDITIONAL_EVIDENCE_AND_DIAGNOSTICS_ONLY_NEVER_REPLACES_V2"

RUN_PROFILES = {
    "V3_EXTENDED_82W":       {"start": "2026-06-20", "end": "2026-09-09", "windows": 82, "rows": 50, "total": 4100},
    "V3_EXTENDED_SEG_A_57W": {"start": "2026-06-20", "end": "2026-08-15", "windows": 57, "rows": 50, "total": 2850},
    "V3_EXTENDED_SEG_B_24W": {"start": "2026-08-17", "end": "2026-09-09", "windows": 24, "rows": 50, "total": 1200},
}


def authorize_v3_write(execute_build, token):
    """PURE. Both the explicit option and the exact V3 token are required. Consults no other flag."""
    if not execute_build:
        return {"authorized": False, "reason": "execute_build_not_requested"}
    if not token:
        return {"authorized": False, "reason": "missing_v3_build_token"}
    if token != V3_BUILD_TOKEN:
        return {"authorized": False, "reason": "wrong_v3_build_token"}
    return {"authorized": True, "reason": "option_plus_exact_v3_token"}


def artifact_name_for(profile: str) -> str:
    p = RUN_PROFILES[profile]
    return _v2.v2_artifact_filename(p["start"], p["end"], p["windows"])


def source_date_inventory(record: dict, inputs: list) -> dict:
    """Deterministic per-window inventory: run_date, sha256s, provenance tier, weekday flag,
    EXIT_ONLY tag for post-cutoff windows, plus expected-but-absent dates."""
    by_date = {i["run_date"]: i for i in inputs}
    rows = []
    for pw in record.get("per_window") or []:
        d = str(pw.get("run_date"))
        src = by_date.get(d, {})
        rows.append({
            "run_date": d,
            "weekday": _date.fromisoformat(d).strftime("%a"),
            "is_weekend": _date.fromisoformat(d).weekday() >= 5,
            "role": EXIT_ONLY_MARKER if d > ENTRY_CUTOFF else "ENTRY_WINDOW_UNDER_ACCEPTED_SPEC",
            "reduced_sha256": pw.get("reduced_sha256"),
            "raw_sha256": pw.get("raw_sha256"),
            "sidecar_sha256": pw.get("sidecar_sha256"),
            "provenance_tier": pw.get("provenance_tier"),
            "row_count": pw.get("row_count"),
            "label_counts": pw.get("label_counts"),
            "source_path": src.get("source_path"),
        })
    present = {r["run_date"] for r in rows}
    expected = list(record.get("expected_dates") or [])
    return {
        "windows": rows,
        "expected_dates_absent": [d for d in expected if d not in present],
        "present_not_expected": sorted(d for d in present if d not in set(expected)),
        "exit_only_window_count": sum(1 for r in rows if r["role"] == EXIT_ONLY_MARKER),
        "weekend_window_count": sum(1 for r in rows if r["is_weekend"]),
        "known_missing_admitted_window": MISSING_ADMITTED_WINDOW,
    }


def run_profile(profile: str) -> tuple:
    """READ-ONLY. Build the V3 manifest for one frozen profile through the unchanged V2 contract."""
    p = RUN_PROFILES[profile]
    expected = _v2._v1._daterange(p["start"], p["end"])
    inputs = _v2run.collect_v2_window_inputs(DATA_DIR, expected)
    record, labels = _v2.build_range_multi_window_manifest(
        inputs, start_date=p["start"], end_date=p["end"], expected_window_count=p["windows"],
        expected_rows_per_window=p["rows"], expected_total_rows=p["total"])
    record["v3_profile"] = profile
    record["v3_role"] = V3_ROLE
    record["entry_cutoff_for_replay"] = ENTRY_CUTOFF
    record["source_date_inventory"] = source_date_inventory(record, inputs)
    return record, labels


def summarize(profile: str, record: dict, check: dict, auth: dict) -> dict:
    inv = record["source_date_inventory"]
    return {
        "profile": profile, "v3_role": V3_ROLE,
        "mode": ("BUILD" if auth["authorized"] else "DRY_RUN_MANIFEST_ONLY"),
        "verdict": record["verdict"], "validator_valid": check["valid"],
        "validator_failures": check["failures"], "blockers": record["blockers"],
        "window_range": [record["window_start"], record["window_end"]],
        "expected_windows": record["expected_windows"],
        "windows_seen": len(record.get("per_window") or []),
        "expected_dates_absent": inv["expected_dates_absent"],
        "exit_only_window_count": inv["exit_only_window_count"],
        "weekend_window_count": inv["weekend_window_count"],
        "aggregate_manifest_sha256": record["aggregate_manifest_sha256"],
        "canonical_label_payload_sha256": record["canonical_label_payload_sha256"],
        "aggregate_label_counts": record["aggregate_label_counts"],
        "provenance_tier_counts": record["provenance_tier_counts"],
        "artifact_filename": record["mw_artifact_filename"],
        "build_authorization": auth,
        "replay_authorized": record["replay_authorized"],
        "execution_authorized": record["execution_authorized"],
        "artifact_written": False,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", default="V3_EXTENDED_SEG_A_57W", choices=sorted(RUN_PROFILES))
    ap.add_argument("--execute-build", action="store_true")
    ap.add_argument("--build-token", default=os.environ.get("C22_V3_BUILD_TOKEN"))
    a = ap.parse_args(argv)
    record, labels = run_profile(a.profile)
    check = _v2.validate_range_multi_window(record)
    auth = authorize_v3_write(a.execute_build, a.build_token)
    summary = summarize(a.profile, record, check, auth)
    if auth["authorized"]:
        if not _v2run.manifest_write_eligible(record, check):
            summary["build_refused"] = "manifest_not_ready_or_invalid: %s / %s" % (record["verdict"], check["failures"])
        else:
            res = _v2run.write_artifact(record, labels, OUT_DIR)
            summary["artifact_written"] = True
            ap_ = Path(res["path"])
            summary["artifact_path"] = str(ap_.relative_to(REPO_ROOT) if ap_.is_relative_to(REPO_ROOT) else ap_).replace("\\", "/")
            summary["artifact_sha256"] = res["sha256"]
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
