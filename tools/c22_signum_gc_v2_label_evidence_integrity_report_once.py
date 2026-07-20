"""Candidate #22 -- Signum Trend Radar GC V2 LABEL EVIDENCE INTEGRITY REPORT
(READ-ONLY over frozen sources + built V2 artifact; ADDITIVE; RESEARCH ONLY; ONE-SHOT).

Completes the C22 Label Pipeline V2 evidence package: reads the built 26-window V2 label
artifact READ-ONLY, independently rebuilds the canonical artifact bytes in memory from the
frozen sources (byte-identical check), and writes a deterministic human-readable integrity
report (JSON + Markdown) under reports/. The report contains:
  - label distribution summary (aggregate + per window);
  - signal concentration by date, by asset (non-NONE only), and by label type;
  - explicit per-window provenance-tier accounting, including exactly which windows lack
    raw top-100 or reduction sidecars and whether each absence is MISSING_BY_DESIGN
    (pre-activation legacy gap) or MISSING_MANDATORY (hard blocker);
  - determinism evidence (rebuilt SHA-256 vs on-disk SHA-256);
  - a fail-closed recommendation: READY_FOR_HUMAN_REVIEW_OF_REPLAY_APPROVAL only when the
    manifest is READY, the anti-tamper validator passes, the rebuild is byte-identical and
    all expected counts hold; otherwise BLOCKED_BY_SOURCE_INTEGRITY.

The report is a PURE function of the artifact + frozen sources (no timestamps, no
environment data), so repeated runs are byte-identical. It issues NO token, authorizes NO
replay/optimization/activation, changes NO collection state, and never modifies V1 or V2
artifacts or any frozen source.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import sparta_commander.external_signum_trend_radar_gc_long_short_v2_range_multi_window_real_candle_labels_contract as _v2  # noqa: E402,E501
import tools.c22_signum_trend_radar_gc_v2_range_multi_window_real_candle_labels_once as _runner  # noqa: E402,E501

REPORT_DIR = REPO_ROOT / "reports" / "c22_gc_label_pipeline_v2_evidence"
REPORT_BASENAME = "c22_gc_label_pipeline_v2_evidence_integrity_report"
RECOMMEND_READY = "READY_FOR_HUMAN_REVIEW_OF_REPLAY_APPROVAL"
RECOMMEND_BLOCKED = "BLOCKED_BY_SOURCE_INTEGRITY"


def signal_concentration(labels: list) -> dict:
    """PURE. Concentration of signals by date, by asset, and by label type. Asset view is
    restricted to rows with a non-NONE signal (the actionable surface); date view counts
    every signal class per window date."""
    by_date: dict = {}
    by_symbol: dict = {}
    by_signal: dict = {}
    for r in labels:
        sig = str(r.get("signal"))
        by_signal[sig] = by_signal.get(sig, 0) + 1
        d = str(r.get("source_date"))
        by_date.setdefault(d, {})
        by_date[d][sig] = by_date[d].get(sig, 0) + 1
        if sig != "NONE":
            sym = str(r.get("symbol"))
            by_symbol.setdefault(sym, {})
            by_symbol[sym][sig] = by_symbol[sym].get(sig, 0) + 1
    return {"by_date": by_date, "by_symbol_non_none": by_symbol, "by_signal": by_signal}


def provenance_accounting(per_window: list) -> dict:
    """PURE. Explicit accounting of which windows lack raw top-100 / reduction sidecars,
    split into legitimate pre-activation gaps (MISSING_BY_DESIGN) vs hard blockers
    (MISSING_MANDATORY)."""
    acc = {"windows_missing_raw_by_design": [], "windows_missing_raw_mandatory": [],
           "windows_missing_sidecar_by_design": [], "windows_missing_sidecar_mandatory": [],
           "windows_full_provenance": []}
    for p in per_window:
        rd = str(p.get("run_date"))
        raw_s, sc_s = p.get("raw_status"), p.get("sidecar_status")
        if raw_s == "MISSING_BY_DESIGN":
            acc["windows_missing_raw_by_design"].append(rd)
        if raw_s == "MISSING_MANDATORY":
            acc["windows_missing_raw_mandatory"].append(rd)
        if sc_s == "MISSING_BY_DESIGN":
            acc["windows_missing_sidecar_by_design"].append(rd)
        if sc_s == "MISSING_MANDATORY":
            acc["windows_missing_sidecar_mandatory"].append(rd)
        if raw_s == "PRESENT_MANDATORY" and sc_s == "PRESENT_MANDATORY":
            acc["windows_full_provenance"].append(rd)
    return acc


def decide_recommendation(artifact: dict, validator: dict, byte_identical: bool,
                          rebuilt_verdict: str, rebuilt_blockers: list) -> dict:
    """PURE, FAILS CLOSED. READY only when every integrity condition holds; any failure
    yields BLOCKED_BY_SOURCE_INTEGRITY with explicit reasons."""
    reasons: list = []
    labels = artifact.get("labels") or []
    per_window = artifact.get("per_window") or []
    if rebuilt_verdict != _v2.V2_VERDICT_READY:
        reasons.append("rebuild_verdict_not_ready:%s" % rebuilt_verdict)
    if rebuilt_blockers:
        reasons.append("rebuild_blockers_present")
    if not validator.get("valid"):
        reasons.append("validator_failed:%s" % ",".join(validator.get("failures") or []))
    if not byte_identical:
        reasons.append("rebuild_not_byte_identical_to_artifact")
    if len(per_window) != 26:
        reasons.append("window_count_%d_ne_26" % len(per_window))
    if len(labels) != 1300:
        reasons.append("label_count_%d_ne_1300" % len(labels))
    acc = provenance_accounting(per_window)
    if acc["windows_missing_raw_mandatory"] or acc["windows_missing_sidecar_mandatory"]:
        reasons.append("missing_mandatory_post_activation_evidence")
    return {"recommendation": (RECOMMEND_READY if not reasons else RECOMMEND_BLOCKED),
            "reasons": reasons}


def build_report(artifact: dict, on_disk_sha256: str, rebuilt_sha256: str,
                 rebuilt_record: dict, validator: dict) -> dict:
    """PURE. Assemble the full integrity report from the artifact + rebuild evidence."""
    labels = artifact.get("labels") or []
    per_window = artifact.get("per_window") or []
    byte_identical = (on_disk_sha256 == rebuilt_sha256)
    decision = decide_recommendation(artifact, validator, byte_identical,
                                     str(rebuilt_record.get("verdict")),
                                     list(rebuilt_record.get("blockers") or []))
    return {
        "report": "c22_gc_label_pipeline_v2_evidence_integrity_report",
        "mode": "RESEARCH_ONLY_READ_ONLY_EVIDENCE_REPORT",
        "artifact_filename": artifact.get("window_start") and _v2.v2_artifact_filename(
            str(artifact["window_start"]), str(artifact["window_end"]),
            len(artifact.get("expected_dates") or [])),
        "window_start": artifact.get("window_start"),
        "window_end": artifact.get("window_end"),
        "window_count": len(per_window),
        "labels_total": len(labels),
        "aggregate_label_counts": artifact.get("aggregate_label_counts"),
        "signal_concentration": signal_concentration(labels),
        "per_window_label_counts": {str(p.get("run_date")): p.get("label_counts")
                                    for p in per_window},
        "provenance_tier_counts": artifact.get("provenance_tier_counts"),
        "provenance_tiers_by_window": {str(p.get("run_date")): p.get("provenance_tier")
                                       for p in per_window},
        "provenance_accounting": provenance_accounting(per_window),
        "sidecar_mandatory_from": artifact.get("sidecar_mandatory_from"),
        "raw_mandatory_from": artifact.get("raw_mandatory_from"),
        "pre_build_status": artifact.get("pre_build_status"),
        "end_to_end_provenance_complete_all_windows":
            artifact.get("end_to_end_provenance_complete_all_windows"),
        "aggregate_manifest_sha256": artifact.get("aggregate_manifest_sha256"),
        "canonical_label_payload_sha256": artifact.get("canonical_label_payload_sha256"),
        "artifact_sha256_on_disk": on_disk_sha256,
        "artifact_sha256_rebuilt_from_frozen_sources": rebuilt_sha256,
        "byte_identical_rebuild": byte_identical,
        "validator_valid": bool(validator.get("valid")),
        "validator_failures": list(validator.get("failures") or []),
        "recommendation": decision["recommendation"],
        "recommendation_reasons": decision["reasons"],
        "token_issued": False, "replay_authorized": False, "optimization_authorized": False,
        "activation_authorized": False, "collection_state_changed": False,
        "human_review_required": True,
    }


def canonical_report_bytes(report: dict) -> bytes:
    return json.dumps(report, indent=2, sort_keys=True).encode("utf-8") + b"\n"


def render_markdown(report: dict) -> str:
    """PURE. Human-readable Markdown view of the integrity report (deterministic)."""
    acc = report["provenance_accounting"]
    conc = report["signal_concentration"]
    lines = [
        "# C22 GC Label Pipeline V2 — Evidence Integrity Report",
        "",
        "Read-only evidence report. Issues no token; authorizes no replay, optimization,",
        "or activation; changes no collection state.",
        "",
        "## Scope",
        "",
        "- Window range: %s .. %s (frozen)" % (report["window_start"], report["window_end"]),
        "- Windows: %d, labels: %d" % (report["window_count"], report["labels_total"]),
        "- Artifact: `%s`" % report["artifact_filename"],
        "",
        "## Label distribution",
        "",
    ]
    for sig in sorted(report["aggregate_label_counts"] or {}):
        lines.append("- %s: %d" % (sig, report["aggregate_label_counts"][sig]))
    lines += ["", "## Signal concentration by date (non-NONE only)", ""]
    for d in sorted(conc["by_date"]):
        nn = {k: v for k, v in conc["by_date"][d].items() if k != "NONE"}
        if nn:
            lines.append("- %s: %s" % (d, ", ".join("%s=%d" % (k, nn[k]) for k in sorted(nn))))
    lines += ["", "## Signal concentration by asset (non-NONE only)", ""]
    for s in sorted(conc["by_symbol_non_none"]):
        c = conc["by_symbol_non_none"][s]
        lines.append("- %s: %s" % (s, ", ".join("%s=%d" % (k, c[k]) for k in sorted(c))))
    lines += [
        "", "## Provenance tiers", "",
    ]
    for t in sorted(report["provenance_tier_counts"] or {}):
        lines.append("- %s: %d windows" % (t, report["provenance_tier_counts"][t]))
    lines += [
        "",
        "- Sidecars mandatory from: %s" % report["sidecar_mandatory_from"],
        "- Raw top-100 mandatory from: %s" % report["raw_mandatory_from"],
        "- Windows missing raw top-100 (by design, pre-activation): %s"
        % (", ".join(acc["windows_missing_raw_by_design"]) or "none"),
        "- Windows missing raw top-100 (MANDATORY — blocker): %s"
        % (", ".join(acc["windows_missing_raw_mandatory"]) or "none"),
        "- Windows missing sidecar (by design, pre-activation): %s"
        % (", ".join(acc["windows_missing_sidecar_by_design"]) or "none"),
        "- Windows missing sidecar (MANDATORY — blocker): %s"
        % (", ".join(acc["windows_missing_sidecar_mandatory"]) or "none"),
        "- Windows with full raw+sidecar provenance: %s"
        % (", ".join(acc["windows_full_provenance"]) or "none"),
        "- End-to-end provenance complete for all windows: %s"
        % report["end_to_end_provenance_complete_all_windows"],
        "- Pre-build status: %s" % report["pre_build_status"],
        "",
        "## Determinism and hashes",
        "",
        "- Aggregate manifest SHA-256: `%s`" % report["aggregate_manifest_sha256"],
        "- Canonical label payload SHA-256: `%s`" % report["canonical_label_payload_sha256"],
        "- Artifact SHA-256 on disk: `%s`" % report["artifact_sha256_on_disk"],
        "- Artifact SHA-256 rebuilt from frozen sources: `%s`"
        % report["artifact_sha256_rebuilt_from_frozen_sources"],
        "- Byte-identical rebuild: %s" % report["byte_identical_rebuild"],
        "- Anti-tamper validator: %s" % ("PASS" if report["validator_valid"] else
                                         "FAIL: %s" % report["validator_failures"]),
        "",
        "## Recommendation",
        "",
        "**%s**" % report["recommendation"],
        "",
    ]
    if report["recommendation_reasons"]:
        lines.append("Blocking reasons:")
        lines += ["- %s" % r for r in report["recommendation_reasons"]]
    else:
        lines.append("The V2 label evidence is internally consistent, provenance-honest, and")
        lines.append("deterministically rebuildable. A separate human replay-approval decision")
        lines.append("is still required before any replay; this report authorizes nothing.")
    lines.append("")
    return "\n".join(lines)


def _write_atomic(path: Path, blob: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "wb") as f:
        f.write(blob)
    os.replace(tmp, path)


def run_report() -> dict:
    """Read artifact + frozen sources READ-ONLY, rebuild in memory, assemble report."""
    expected = _v2._v1._daterange(_runner.RUN_START, _runner.RUN_END)
    inputs = _runner.collect_v2_window_inputs(_runner.DATA_DIR, expected)
    record, labels = _v2.build_range_multi_window_manifest(
        inputs, start_date=_runner.RUN_START, end_date=_runner.RUN_END,
        expected_window_count=_runner.RUN_EXPECTED_WINDOWS,
        expected_rows_per_window=_runner.RUN_ROWS_PER_WINDOW,
        expected_total_rows=_runner.RUN_EXPECTED_TOTAL_ROWS)
    validator = _v2.validate_range_multi_window(record)
    rebuilt = _v2.canonical_v2_artifact_bytes(_v2.build_v2_aggregate_payload(record, labels))
    art_path = _runner.OUT_DIR / record["mw_artifact_filename"]
    disk = art_path.read_bytes()
    artifact = json.loads(disk.decode("utf-8"))
    return build_report(artifact, hashlib.sha256(disk).hexdigest(),
                        hashlib.sha256(rebuilt).hexdigest(), record, validator)


def main() -> int:
    report = run_report()
    json_path = REPORT_DIR / (REPORT_BASENAME + ".json")
    md_path = REPORT_DIR / (REPORT_BASENAME + ".md")
    _write_atomic(json_path, canonical_report_bytes(report))
    _write_atomic(md_path, render_markdown(report).encode("utf-8"))
    print(json.dumps({
        "recommendation": report["recommendation"],
        "recommendation_reasons": report["recommendation_reasons"],
        "labels_total": report["labels_total"],
        "aggregate_label_counts": report["aggregate_label_counts"],
        "provenance_tier_counts": report["provenance_tier_counts"],
        "byte_identical_rebuild": report["byte_identical_rebuild"],
        "validator_valid": report["validator_valid"],
        "report_json": str(json_path.relative_to(REPO_ROOT)).replace("\\", "/"),
        "report_md": str(md_path.relative_to(REPO_ROOT)).replace("\\", "/"),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
