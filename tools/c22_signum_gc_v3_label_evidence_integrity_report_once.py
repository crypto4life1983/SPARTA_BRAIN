"""Candidate #22 -- GC LABEL PIPELINE V3_EXTENDED EVIDENCE INTEGRITY REPORT
(READ-ONLY; RESEARCH ONLY; writes report files only with --execute-write).

For each frozen V3 profile: rebuilds the manifest from the frozen sources through the UNCHANGED
V2 contract, compares the on-disk artifact SHA-256 to the rebuilt bytes, accounts provenance,
counts labels, and -- critically -- proves that V3 does NOT alter V2: every V3 label row whose
source_date lies inside the frozen V2 range must be byte-identical (canonical form) to the
corresponding V2 row, and the frozen V2 artifact SHA-256 must be unchanged.

Issues no token; authorizes no replay; changes no collection state.
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

import sparta_commander.external_signum_trend_radar_gc_long_short_v2_range_multi_window_real_candle_labels_contract as _v2  # noqa: E402,E501
import tools.c22_signum_gc_v2_label_evidence_integrity_report_once as _v2rep  # noqa: E402
import tools.c22_signum_trend_radar_gc_v2_range_multi_window_real_candle_labels_once as _v2run  # noqa: E402
import tools.c22_signum_trend_radar_gc_v3_extended_multi_window_real_candle_labels_once as _v3run  # noqa: E402

REPORT_DIR = REPO_ROOT / "reports" / "c22_gc_label_pipeline_v3_evidence"
ARTIFACT_DIR = _v3run.OUT_DIR
V2_ARTIFACT_PATH = _v2run.OUT_DIR / _v2.v2_artifact_filename(
    _v2run.RUN_START, _v2run.RUN_END, _v2run.RUN_EXPECTED_WINDOWS)
V2_FROZEN_ARTIFACT_SHA256 = "b6a28a4873d1aff17014a9d598702c67047b4ebe023b8cfddce05094f9ce9dd8"
V2_FROZEN_ACTIONABLE = 88
RECOMMEND_OK = "V3_EVIDENCE_INTEGRITY_PASS_DIAGNOSTIC_ONLY"
RECOMMEND_BLOCKED = "V3_EVIDENCE_INTEGRITY_BLOCKED"


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _canon_rows(rows: list) -> bytes:
    return json.dumps(sorted(rows, key=lambda r: (r["source_date"], r["order_index"], r["symbol"])),
                      sort_keys=True, separators=(",", ":")).encode("utf-8")


def v2_subset_check(v3_labels: list, v2_artifact: dict) -> dict:
    """PURE. V3 rows inside the V2 range must reproduce the V2 rows exactly; V2 actionable = 88."""
    lo, hi = str(v2_artifact["window_start"]), str(v2_artifact["window_end"])
    v3_sub = [r for r in v3_labels if lo <= r["source_date"] <= hi]
    v2_rows = list(v2_artifact["labels"])
    actionable = lambda rows: [r for r in rows if r["signal"] in ("LONG_ENTRY", "BEAR_SHORT", "HEDGE_SHORT")]
    return {
        "v2_range": [lo, hi],
        "overlaps_v2_range": bool(v3_sub),
        "v3_rows_in_v2_range": len(v3_sub),
        "v2_rows": len(v2_rows),
        "canonical_identical": _canon_rows(v3_sub) == _canon_rows(v2_rows) if v3_sub else False,
        "v2_actionable": len(actionable(v2_rows)),
        "v3_actionable_in_v2_range": len(actionable(v3_sub)),
        "v3_actionable_after_v2_range": len([r for r in actionable(v3_labels) if r["source_date"] > hi]),
    }


def run_v3_report(profile: str) -> dict:
    p = _v3run.RUN_PROFILES[profile]
    record, labels = _v3run.run_profile(profile)
    validator = _v2.validate_range_multi_window(record)
    rebuilt = _v2.canonical_v2_artifact_bytes(_v2.build_v2_aggregate_payload(record, labels))
    art_path = ARTIFACT_DIR / _v3run.artifact_name_for(profile)
    disk_sha, artifact = None, None
    if art_path.exists():
        disk = art_path.read_bytes()
        disk_sha, artifact = _sha(disk), json.loads(disk.decode("utf-8"))
    v2_disk_sha = _sha(V2_ARTIFACT_PATH.read_bytes()) if V2_ARTIFACT_PATH.exists() else None
    v2_art = json.loads(V2_ARTIFACT_PATH.read_bytes().decode("utf-8")) if V2_ARTIFACT_PATH.exists() else None
    per_window = record.get("per_window") or []
    acc = _v2rep.provenance_accounting(per_window)
    subset = v2_subset_check(labels, v2_art) if v2_art else {"canonical_identical": False, "reason": "v2_artifact_absent"}
    reasons = []
    if record.get("verdict") != _v2.V2_VERDICT_READY:
        reasons.append("rebuild_verdict_not_ready:%s" % record.get("verdict"))
    if not validator.get("valid"):
        reasons.append("validator_failed:%s" % ",".join(validator.get("failures") or []))
    if disk_sha is None:
        reasons.append("artifact_absent_on_disk")
    elif disk_sha != _sha(rebuilt):
        reasons.append("rebuild_not_byte_identical_to_artifact")
    if len(per_window) != p["windows"]:
        reasons.append("window_count_%d_ne_%d" % (len(per_window), p["windows"]))
    if len(labels) != p["total"]:
        reasons.append("label_count_%d_ne_%d" % (len(labels), p["total"]))
    if acc["windows_missing_raw_mandatory"] or acc["windows_missing_sidecar_mandatory"]:
        reasons.append("missing_mandatory_post_activation_evidence")
    if v2_disk_sha != V2_FROZEN_ARTIFACT_SHA256:
        reasons.append("v2_frozen_artifact_sha_changed_or_absent")
    overlaps_v2 = bool(v2_art) and p["start"] <= str(v2_art["window_end"])
    if overlaps_v2 and not subset.get("canonical_identical"):
        reasons.append("v3_rows_inside_v2_range_differ_from_v2")
    if overlaps_v2 and subset.get("v2_actionable") != V2_FROZEN_ACTIONABLE:
        reasons.append("v2_actionable_%s_ne_88" % subset.get("v2_actionable"))
    inv = record["source_date_inventory"]
    return {
        "report": "c22_gc_label_pipeline_v3_extended_evidence_integrity_report",
        "mode": "RESEARCH_ONLY_READ_ONLY_EVIDENCE_REPORT",
        "v3_role": _v3run.V3_ROLE,
        "profile": profile, "window_start": p["start"], "window_end": p["end"],
        "expected_windows": p["windows"], "window_count": len(per_window), "labels_total": len(labels),
        "entry_cutoff_for_replay": _v3run.ENTRY_CUTOFF,
        "exit_only_window_count": inv["exit_only_window_count"],
        "weekend_window_count": inv["weekend_window_count"],
        "expected_dates_absent": inv["expected_dates_absent"],
        "aggregate_label_counts": record.get("aggregate_label_counts"),
        "signal_concentration": _v2rep.signal_concentration(labels),
        "per_window_label_counts": {str(w.get("run_date")): w.get("label_counts") for w in per_window},
        "provenance_tier_counts": record.get("provenance_tier_counts"),
        "provenance_accounting": acc,
        "source_date_inventory": inv["windows"],
        "aggregate_manifest_sha256": record.get("aggregate_manifest_sha256"),
        "canonical_label_payload_sha256": record.get("canonical_label_payload_sha256"),
        "artifact_filename": art_path.name,
        "artifact_sha256_on_disk": disk_sha,
        "artifact_sha256_rebuilt_from_frozen_sources": _sha(rebuilt),
        "byte_identical_rebuild": disk_sha == _sha(rebuilt),
        "validator_valid": bool(validator.get("valid")),
        "validator_failures": list(validator.get("failures") or []),
        "v2_frozen_artifact_sha256_expected": V2_FROZEN_ARTIFACT_SHA256,
        "v2_frozen_artifact_sha256_on_disk": v2_disk_sha,
        "v2_unchanged": v2_disk_sha == V2_FROZEN_ARTIFACT_SHA256,
        "v2_subset_check": subset,
        "recommendation": RECOMMEND_OK if not reasons else RECOMMEND_BLOCKED,
        "recommendation_reasons": reasons,
        "token_issued": False, "replay_authorized": False, "optimization_authorized": False,
        "activation_authorized": False, "collection_state_changed": False, "human_review_required": True,
    }


def canonical_bytes(report: dict) -> bytes:
    return json.dumps(report, indent=2, sort_keys=True).encode("utf-8") + b"\n"


def render_markdown(r: dict) -> str:
    L = ["# C22 GC Label Pipeline V3_EXTENDED — Evidence Integrity Report (%s)" % r["profile"], "",
         "Read-only diagnostic evidence. V3 never replaces V2. Issues no token; authorizes nothing.", "",
         "- Role: %s" % r["v3_role"],
         "- Range: %s .. %s · windows %d/%d · labels %d" % (r["window_start"], r["window_end"], r["window_count"], r["expected_windows"], r["labels_total"]),
         "- Entry cutoff for replay: %s · EXIT_ONLY windows: %d · weekend windows: %d" % (r["entry_cutoff_for_replay"], r["exit_only_window_count"], r["weekend_window_count"]),
         "- Expected dates absent: %s" % (r["expected_dates_absent"] or "none"),
         "- Aggregate label counts: %s" % json.dumps(r["aggregate_label_counts"], sort_keys=True),
         "- Provenance tiers: %s" % json.dumps(r["provenance_tier_counts"], sort_keys=True),
         "- Artifact sha256 on disk: `%s`" % r["artifact_sha256_on_disk"],
         "- Artifact sha256 rebuilt: `%s`" % r["artifact_sha256_rebuilt_from_frozen_sources"],
         "- Byte-identical rebuild: %s · validator valid: %s" % (r["byte_identical_rebuild"], r["validator_valid"]),
         "- V2 frozen artifact unchanged: %s (`%s`)" % (r["v2_unchanged"], r["v2_frozen_artifact_sha256_on_disk"]),
         "- V2 subset check: %s" % json.dumps(r["v2_subset_check"], sort_keys=True),
         "", "## Source-date inventory", "", "| run_date | dow | role | tier | reduced sha | raw | sidecar |", "|---|---|---|---|---|---|---|"]
    for w in r["source_date_inventory"]:
        L.append("| %s | %s | %s | %s | `%s` | %s | %s |" % (
            w["run_date"], w["weekday"], w["role"], w["provenance_tier"], str(w["reduced_sha256"])[:12],
            "yes" if w["raw_sha256"] else "no", "yes" if w["sidecar_sha256"] else "no"))
    L += ["", "## Recommendation", "", "**%s**" % r["recommendation"], ""]
    for x in r["recommendation_reasons"]:
        L.append("- %s" % x)
    return "\n".join(L) + "\n"


def _write_atomic(path: Path, blob: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "wb") as fh:
        fh.write(blob)
    os.replace(tmp, path)


def main_with_args(argv=None) -> dict:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", default="V3_EXTENDED_82W", choices=sorted(_v3run.RUN_PROFILES))
    ap.add_argument("--execute-write", action="store_true")
    a = ap.parse_args(argv)
    r = run_v3_report(a.profile)
    out = {"profile": a.profile, "recommendation": r["recommendation"], "reasons": r["recommendation_reasons"],
           "byte_identical_rebuild": r["byte_identical_rebuild"], "v2_unchanged": r["v2_unchanged"],
           "v2_subset_identical": r["v2_subset_check"].get("canonical_identical"),
           "labels_total": r["labels_total"], "aggregate_label_counts": r["aggregate_label_counts"],
           "written": False}
    if a.execute_write:
        base = REPORT_DIR / ("c22_gc_label_pipeline_v3_evidence_integrity_report_%s" % a.profile.lower())
        _write_atomic(base.with_suffix(".json"), canonical_bytes(r))
        _write_atomic(base.with_suffix(".md"), render_markdown(r).encode("utf-8"))
        out["written"] = True
        out["report_json"] = str(base.with_suffix(".json").relative_to(REPO_ROOT)).replace("\\", "/")
    print(json.dumps(out, indent=2, sort_keys=True))
    return out


if __name__ == "__main__":
    main_with_args()
    sys.exit(0)
