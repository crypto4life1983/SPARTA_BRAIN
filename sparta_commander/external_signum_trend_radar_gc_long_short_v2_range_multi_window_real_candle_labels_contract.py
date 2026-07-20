"""Candidate #22 -- Signum Trend Radar GC V2 RANGE MULTI-WINDOW REAL-CANDLE ENTRY-LABELS
(PURE, ADDITIVE, RESEARCH-ONLY, BUILD-GATED).

Human-approved build token:
HUMAN_APPROVED_BUILD_AND_VALIDATE_C22_26_WINDOW_LABEL_PIPELINE_V2_ONLY.

WHY V2 EXISTS: the committed V1 multi-window contract pins the window range to exactly the 20
windows 2026-06-20..2026-07-09 (module constants + validator). This V2 is an ADDITIVE sibling
that supports an EXPLICITLY FROZEN contiguous date range while REUSING V1's frozen labeling core
byte-for-byte -- it imports and calls V1's `label_window`, `extract_dataset_facts`,
`_structural_window_ok`, `_manifest_sha`, `_daterange`, and the V1 signal/threshold constants.
It changes NO label definition, threshold, detector logic, ordering, or serialization.

V1 IS PRESERVED: this module imports V1 read-only; it never edits V1 code, constants, tests, or
its artifacts. V2 writes a DISTINCT, V2-named, date-range-bound artifact and refuses to collide
with either V1 artifact name.

PROVENANCE HONESTY: retained raw top-100 and reduction sidecars were activated on real dates
(sidecar >= 2026-06-28; raw >= 2026-07-10). Windows before each activation legitimately lack
that evidence (a LEGACY gap, not corruption). V2 records an explicit provenance tier + per-window
evidence SHAs (or an explicit missing-by-design marker) and refuses to synthesize/backfill any
missing legacy evidence. Post-activation missing evidence is a HARD failure. The pre-build status
is LABEL_SOURCE_INTEGRITY_PASS_WITH_LEGACY_PROVENANCE_GAP -- NOT complete end-to-end provenance.

No network, credentials, replay, optimization, activation, paper/live, or commit/push.
"""
from __future__ import annotations

import hashlib as _hashlib
import json as _json
from typing import Any

import sparta_commander.external_signum_trend_radar_gc_long_short_v1_multi_window_real_candle_labels_contract as _v1  # noqa: E501

V2_SCHEMA_VERSION = 1
BUILDER_VERSION = "v2"

# --- provenance activation boundaries (verified: sidecars from 2026-06-28; raw-retention
#     remediation commit ed9cf755 dated 2026-07-10) -------------------------------------------
SIDECAR_MANDATORY_FROM = "2026-06-28"
RAW_MANDATORY_FROM = "2026-07-10"
PROVENANCE_TIERS = ("LEGACY_REDUCED_ONLY", "LEGACY_REDUCED_WITH_SIDECAR_NO_RAW",
                    "FULL_RAW_REDUCTION_PROVENANCE")
PRE_BUILD_STATUS = "LABEL_SOURCE_INTEGRITY_PASS_WITH_LEGACY_PROVENANCE_GAP"

V2_VERDICT_READY = "C22_V2_RANGE_MULTI_WINDOW_LABEL_MANIFEST_READY_BUILD_GATED"
V2_VERDICT_BLOCKED = "C22_V2_RANGE_MULTI_WINDOW_LABEL_MANIFEST_BLOCKED"
V2_ARTIFACT_BASENAME = "c22_gc_real_candle_entry_labels_multiwindow_v2"


def provenance_tier(run_date: str) -> str:
    """Tier is determined by the window date relative to each mechanism's activation date."""
    if run_date >= RAW_MANDATORY_FROM:
        return "FULL_RAW_REDUCTION_PROVENANCE"
    if run_date >= SIDECAR_MANDATORY_FROM:
        return "LEGACY_REDUCED_WITH_SIDECAR_NO_RAW"
    return "LEGACY_REDUCED_ONLY"


def _evidence_status(run_date: str, activation_from: str, sha: Any, kind: str,
                     blockers: list) -> str:
    """Post-activation evidence is mandatory (hard fail if missing). Pre-activation absence is a
    legitimate legacy gap recorded as MISSING_BY_DESIGN; a present pre-activation file is still
    recorded/validated."""
    if run_date >= activation_from:
        if sha:
            return "PRESENT_MANDATORY"
        blockers.append("missing_mandatory_%s:%s" % (kind, run_date))
        return "MISSING_MANDATORY"
    return "PRESENT_PRE_ACTIVATION" if sha else "MISSING_BY_DESIGN"


def v2_artifact_filename(start_date: str, end_date: str, window_count: int) -> str:
    """V2-named, window-count + date-range bound; distinct from every V1 artifact name."""
    return "%s_%dw_%s_%s.json" % (V2_ARTIFACT_BASENAME, window_count, start_date, end_date)


def canonical_label_payload_bytes(labels: list) -> bytes:
    """Byte-stable serialization of the LABELS-ONLY payload (indent=2, sort_keys, trailing
    newline). This is the surface compared for V1 compatibility -- it excludes all manifest /
    provenance metadata so a V2 run over the V1 range is byte-identical to V1's labels."""
    return (_json.dumps(labels, indent=2, sort_keys=True).encode("utf-8") + b"\n")


def build_range_multi_window_manifest(window_inputs: Any, *, start_date: str, end_date: str,
                                      expected_window_count: int, expected_rows_per_window: int,
                                      expected_total_rows: int):
    """PURE. Validate the supplied windows against an EXPLICITLY FROZEN range and assemble the V2
    manifest + aggregate labels (reusing V1's frozen per-window core). All five frozen
    parameters are REQUIRED keyword-only args -- there is deliberately NO open-ended
    'use everything available' mode. FAILS CLOSED (verdict BLOCKED + blockers) on any range
    mismatch, missing/duplicate/gap date, invalid window, wrong row count, count mismatch, or
    missing MANDATORY post-activation provenance. Builds NO file; authorizes nothing."""
    blockers: list = []
    expected_dates = _v1._daterange(start_date, end_date)
    if len(expected_dates) != expected_window_count:
        blockers.append("range_length_%d_ne_expected_window_count_%d"
                        % (len(expected_dates), expected_window_count))
    if expected_window_count * expected_rows_per_window != expected_total_rows:
        blockers.append("expected_total_rows_%d_inconsistent_with_%dx%d"
                        % (expected_total_rows, expected_window_count, expected_rows_per_window))

    wins = sorted(list(window_inputs or []), key=lambda w: str(w.get("run_date")))
    dates = [str(w.get("run_date")) for w in wins]
    if len(wins) != expected_window_count:
        blockers.append("expected_%d_windows_got_%d" % (expected_window_count, len(wins)))
    if len(set(dates)) != len(dates):
        blockers.append("duplicate_window_dates")
    if tuple(dates) != expected_dates:
        blockers.append("dates_not_exactly_expected_contiguous_range")

    per_window: list = []
    agg_labels: list = []
    agg_counts = {_v1.SIGNAL_LONG: 0, _v1.SIGNAL_HEDGE: 0, _v1.SIGNAL_BEAR: 0,
                  _v1.SIGNAL_NONE: 0, _v1.SIGNAL_SKIP: 0}
    tier_counts = {t: 0 for t in PROVENANCE_TIERS}

    for w in wins:
        parsed = w.get("parsed") or {}
        sha = str(w.get("sha256"))
        rd = str(w.get("run_date"))
        facts = _v1.extract_dataset_facts(parsed)
        struct = _v1._structural_window_ok(facts)
        row_dates = {r.get("runDate") for r in parsed.get("results", []) if isinstance(r, dict)}
        single_date = (len(row_dates) == 1 and next(iter(row_dates)) == rd)
        window_ok = (struct["ok"] and single_date
                     and facts.get("row_count") == expected_rows_per_window)
        if not window_ok:
            blockers.append("invalid_window:%s" % rd)
        built = _v1.label_window(parsed, sha, rd) if window_ok else {
            "labels": [], "label_counts": dict(agg_counts),
            "btc_present": False, "btc_downtrend": False}
        if window_ok and len(built["labels"]) != expected_rows_per_window:
            blockers.append("window_%s_did_not_produce_%d_labels" % (rd, expected_rows_per_window))
        for k, v in built["label_counts"].items():
            agg_counts[k] = agg_counts.get(k, 0) + v
        agg_labels.extend(built["labels"])

        tier = provenance_tier(rd)
        tier_counts[tier] = tier_counts.get(tier, 0) + 1
        raw_sha = w.get("raw_sha256")
        sc_sha = w.get("sidecar_sha256")
        raw_status = _evidence_status(rd, RAW_MANDATORY_FROM, raw_sha, "raw", blockers)
        sc_status = _evidence_status(rd, SIDECAR_MANDATORY_FROM, sc_sha, "sidecar", blockers)
        per_window.append({
            "run_date": rd, "source_path": w.get("source_path"),
            "reduced_sha256": sha, "row_count": facts.get("row_count"),
            "structurally_valid": window_ok, "structural_checks": struct["checks"],
            "btc_present": built["btc_present"], "btc_downtrend": built["btc_downtrend"],
            "label_counts": built["label_counts"],
            "raw_sha256": raw_sha, "raw_status": raw_status,
            "sidecar_sha256": sc_sha, "sidecar_status": sc_status,
            "provenance_tier": tier})

    if not blockers and len(agg_labels) != expected_total_rows:
        blockers.append("aggregate_label_count_%d_ne_%d" % (len(agg_labels), expected_total_rows))

    manifest_sha = _v1._manifest_sha(
        [{"run_date": p["run_date"], "sha256": p["reduced_sha256"],
          "row_count": p["row_count"] or 0} for p in per_window])
    label_payload_sha = _hashlib.sha256(canonical_label_payload_bytes(agg_labels)).hexdigest()

    record: dict[str, Any] = {
        "schema_version": V2_SCHEMA_VERSION, "mode": _v1.MWL22_MODE, "lane": _v1.MWL22_LANE,
        "builder_version": BUILDER_VERSION, "candidate_id": _v1.CANDIDATE_ID,
        "window_start": start_date, "window_end": end_date,
        "expected_windows": expected_window_count, "labels_per_window": expected_rows_per_window,
        "total_labels_expected": expected_total_rows, "expected_dates": list(expected_dates),
        "is_multi_window_spec_and_impl_only": True, "reuses_single_window_core": True,
        "reuses_v1_labeling_functions": True,
        "v1_contract_module":
            "external_signum_trend_radar_gc_long_short_v1_multi_window_real_candle_labels_contract",
        "single_window_artifact_preserved": _v1.SINGLE_WINDOW_ARTIFACT_FILENAME,
        "v1_multiwindow_artifact_preserved": _v1.MW_ARTIFACT_FILENAME,
        "bear_high_multiple_single_sourced": _v1.BEAR_HIGH_MULT,
        "market_rank_tiebreaker": list(_v1.MARKET_RANK_TIEBREAKER),
        "per_window": per_window,
        "aggregate_manifest_sha256": manifest_sha,
        "canonical_label_payload_sha256": label_payload_sha,
        "aggregate_label_counts": agg_counts, "aggregate_labels_built": len(agg_labels),
        "provenance_tier_counts": tier_counts,
        "sidecar_mandatory_from": SIDECAR_MANDATORY_FROM, "raw_mandatory_from": RAW_MANDATORY_FROM,
        "pre_build_status": PRE_BUILD_STATUS,
        "end_to_end_provenance_complete_all_windows": False,
        "verdict": (V2_VERDICT_READY if not blockers else V2_VERDICT_BLOCKED),
        "blockers": blockers,
        "artifact_dir": _v1.ARTIFACT_DIR,
        "mw_artifact_filename": v2_artifact_filename(start_date, end_date, expected_window_count),
        "never_date_tagged_today": True, "never_overwrites_v1_artifacts": True,
        "build_authorized": False, "replay_authorized": False, "optimization_authorized": False,
        "activation_authorized": False, "paper_live_authorized": False,
        "execution_authorized": False, "replay_gate_locked": True,
        "paper_trading_gate_locked": True, "live_gate_locked": True, "advances_nothing": True,
        "next_gate_token": _v1.NEXT_GATE_TOKEN, "human_review_required": True,
    }
    for flag in _v1._CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    return record, agg_labels


def build_v2_aggregate_payload(record: dict, agg_labels: list) -> dict[str, Any]:
    """PURE. The canonical V2 artifact payload a gated build writes. Carries the provenance
    manifest + tier counts alongside the labels. Writes NOTHING."""
    return {
        "builder_version": BUILDER_VERSION, "candidate_id": _v1.CANDIDATE_ID,
        "window_start": record["window_start"], "window_end": record["window_end"],
        "expected_dates": record["expected_dates"],
        "aggregate_manifest_sha256": record["aggregate_manifest_sha256"],
        "canonical_label_payload_sha256": record["canonical_label_payload_sha256"],
        "market_rank_tiebreaker": list(_v1.MARKET_RANK_TIEBREAKER),
        "bear_high_multiple_single_sourced": _v1.BEAR_HIGH_MULT,
        "provenance_tier_counts": record["provenance_tier_counts"],
        "sidecar_mandatory_from": record["sidecar_mandatory_from"],
        "raw_mandatory_from": record["raw_mandatory_from"],
        "pre_build_status": record["pre_build_status"],
        "end_to_end_provenance_complete_all_windows": False,
        "per_window": [{k: p[k] for k in (
            "run_date", "source_path", "reduced_sha256", "row_count", "btc_present",
            "btc_downtrend", "label_counts", "raw_sha256", "raw_status", "sidecar_sha256",
            "sidecar_status", "provenance_tier")} for p in record["per_window"]],
        "aggregate_label_counts": record["aggregate_label_counts"],
        "labels": agg_labels}


def canonical_v2_artifact_bytes(payload: dict) -> bytes:
    """Full V2 artifact bytes, reusing V1's byte convention (indent=2, sort_keys, newline)."""
    return _v1.canonical_payload_bytes(payload)


def validate_range_multi_window(record: Any) -> dict[str, Any]:
    """Anti-tamper validator (range-parameterized analog of V1's). Valid only when research-only,
    spec+impl-only, reuses the frozen V1 core + frozen threshold/tiebreaker, expected_dates equals
    the explicit range, every authorization + capability flag is False, downstream gates locked,
    the artifact is V2-named / date-range-bound / distinct from both V1 artifact names, provenance
    tiers + counts are recorded with NO missing mandatory post-activation evidence, and (for a
    READY manifest) exactly expected_windows contiguous windows / expected_rows_per_window each /
    expected_total_rows aggregate with no blockers."""
    f: list = []
    if not isinstance(record, dict):
        return {"valid": False, "failures": ["record_not_a_dict"]}
    r = record
    if r.get("mode") != _v1.MWL22_MODE:
        f.append("mode_not_research_only")
    if r.get("builder_version") != BUILDER_VERSION:
        f.append("builder_version_not_v2")
    if r.get("is_multi_window_spec_and_impl_only") is not True:
        f.append("not_spec_impl_only")
    if r.get("reuses_single_window_core") is not True or r.get("reuses_v1_labeling_functions") is not True:
        f.append("must_reuse_v1_core")
    if r.get("bear_high_multiple_single_sourced") != _v1.BEAR_HIGH_MULT:
        f.append("bear_mult_drifted")
    if tuple(r.get("market_rank_tiebreaker") or ()) != tuple(_v1.MARKET_RANK_TIEBREAKER):
        f.append("tiebreaker_drifted")
    exp = _v1._daterange(str(r.get("window_start")), str(r.get("window_end")))
    if tuple(r.get("expected_dates") or ()) != exp:
        f.append("expected_dates_not_equal_explicit_range")
    if len(exp) != r.get("expected_windows"):
        f.append("range_length_ne_expected_windows")
    if r.get("expected_windows", 0) * r.get("labels_per_window", 0) != r.get("total_labels_expected"):
        f.append("total_rows_inconsistent")
    # provenance honesty
    if r.get("pre_build_status") != PRE_BUILD_STATUS:
        f.append("pre_build_status_wrong")
    if r.get("end_to_end_provenance_complete_all_windows") is not False:
        f.append("must_not_claim_complete_provenance")
    if r.get("sidecar_mandatory_from") != SIDECAR_MANDATORY_FROM \
            or r.get("raw_mandatory_from") != RAW_MANDATORY_FROM:
        f.append("provenance_activation_dates_wrong")
    tc = r.get("provenance_tier_counts") or {}
    if set(tc) != set(PROVENANCE_TIERS):
        f.append("provenance_tier_counts_keys_wrong")
    elif sum(tc.values()) != r.get("expected_windows"):
        f.append("provenance_tier_counts_do_not_sum_to_windows")
    for p in r.get("per_window") or []:
        if p.get("raw_status") == "MISSING_MANDATORY" or p.get("sidecar_status") == "MISSING_MANDATORY":
            f.append("missing_mandatory_post_activation_evidence:%s" % p.get("run_date"))
        if p.get("provenance_tier") != provenance_tier(str(p.get("run_date"))):
            f.append("provenance_tier_mismatch:%s" % p.get("run_date"))
    # authorization + safety
    for k in ("build_authorized", "replay_authorized", "optimization_authorized",
              "activation_authorized", "paper_live_authorized", "execution_authorized"):
        if r.get(k) is not False:
            f.append("authorization_flag_true:%s" % k)
    for k in ("replay_gate_locked", "paper_trading_gate_locked", "live_gate_locked",
              "advances_nothing", "never_date_tagged_today", "never_overwrites_v1_artifacts"):
        if r.get(k) is not True:
            f.append("safety_flag_wrong:%s" % k)
    # V2 artifact naming: v2, date-range bound, distinct from BOTH V1 artifact names
    name = str(r.get("mw_artifact_filename"))
    if "_v2_" not in name:
        f.append("artifact_name_not_v2")
    if str(r.get("window_start")) not in name or str(r.get("window_end")) not in name:
        f.append("artifact_name_not_date_range_bound")
    if name in (_v1.MW_ARTIFACT_FILENAME, _v1.SINGLE_WINDOW_ARTIFACT_FILENAME):
        f.append("artifact_name_collides_with_v1")
    if r.get("next_gate_token") != _v1.NEXT_GATE_TOKEN:
        f.append("next_gate_token_not_canonical_reused")
    # READY structural guarantees
    if r.get("verdict") == V2_VERDICT_READY:
        if r.get("blockers"):
            f.append("ready_with_blockers")
        if len(r.get("per_window") or []) != r.get("expected_windows"):
            f.append("ready_window_count_wrong")
        if r.get("aggregate_labels_built") != r.get("total_labels_expected"):
            f.append("ready_total_rows_wrong")
        if not all(p.get("structurally_valid") is True
                   and p.get("row_count") == r.get("labels_per_window")
                   for p in r.get("per_window") or []):
            f.append("ready_window_not_valid_or_wrong_rows")
        if [p["run_date"] for p in r.get("per_window") or []] != list(exp):
            f.append("ready_dates_not_contiguous_expected")
    for flag in _v1._CAPABILITY_FLAGS_FALSE:
        if r.get(flag) is not False:
            f.append("capability_flag_true:%s" % flag)
    return {"valid": not f, "failures": f}
