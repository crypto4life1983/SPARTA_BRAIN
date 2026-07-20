"""V2 range multi-window label contract tests: V1 compatibility, determinism, provenance tiers,
and 26-window acceptance. Data-dependent tests skip cleanly if the frozen windows are absent
(e.g. a clean checkout where the gitignored dataset is not present)."""
import hashlib
import json
from pathlib import Path

import pytest

import sparta_commander.external_signum_trend_radar_gc_long_short_v2_range_multi_window_real_candle_labels_contract as v2
import tools.c22_signum_trend_radar_gc_v2_range_multi_window_real_candle_labels_once as runner

DATA_DIR = runner.DATA_DIR
V1_ARTIFACT = DATA_DIR / "detector_labels" / v2._v1.MW_ARTIFACT_FILENAME
_HAS_DATA = DATA_DIR.exists() and V1_ARTIFACT.exists()
needs_data = pytest.mark.skipif(not _HAS_DATA, reason="frozen GC windows / V1 artifact not present")


def _inputs(start, end):
    return runner.collect_v2_window_inputs(DATA_DIR, v2._v1._daterange(start, end))


def _build(start, end, n, rows, total):
    return v2.build_range_multi_window_manifest(
        _inputs(start, end), start_date=start, end_date=end, expected_window_count=n,
        expected_rows_per_window=rows, expected_total_rows=total)


# ---- structural / API tests (no dataset needed) --------------------------------------------
def test_explicit_frozen_params_are_required_keyword_only():
    # no silent "use everything" mode: the five frozen params are mandatory kw-only
    with pytest.raises(TypeError):
        v2.build_range_multi_window_manifest([])  # missing required kw-only args


def test_artifact_name_is_v2_distinct_from_v1():
    name = v2.v2_artifact_filename("2026-06-20", "2026-07-15", 26)
    assert name == "c22_gc_real_candle_entry_labels_multiwindow_v2_26w_2026-06-20_2026-07-15.json"
    assert "_v2_" in name and "26w" in name
    assert name != v2._v1.MW_ARTIFACT_FILENAME
    assert name != v2._v1.SINGLE_WINDOW_ARTIFACT_FILENAME


def test_provenance_tier_boundaries():
    assert v2.provenance_tier("2026-06-27") == "LEGACY_REDUCED_ONLY"
    assert v2.provenance_tier("2026-06-28") == "LEGACY_REDUCED_WITH_SIDECAR_NO_RAW"
    assert v2.provenance_tier("2026-07-09") == "LEGACY_REDUCED_WITH_SIDECAR_NO_RAW"
    assert v2.provenance_tier("2026-07-10") == "FULL_RAW_REDUCTION_PROVENANCE"
    assert v2.provenance_tier("2026-07-15") == "FULL_RAW_REDUCTION_PROVENANCE"


def test_missing_mandatory_post_activation_evidence_hard_fails():
    # a post-activation window missing raw evidence must BLOCK + fail validation
    win = {"run_date": "2026-07-11", "row_count": 50, "sha256": "x", "raw_sha256": None,
           "sidecar_sha256": "s", "parsed": {"results": [{"runDate": "2026-07-11"}] * 50}}
    rec, _ = v2.build_range_multi_window_manifest(
        [win], start_date="2026-07-11", end_date="2026-07-11", expected_window_count=1,
        expected_rows_per_window=50, expected_total_rows=50)
    assert any(b.startswith("missing_mandatory_raw") for b in rec["blockers"])
    assert v2.validate_range_multi_window(rec)["valid"] is False


# ---- data-dependent: V1 compatibility ------------------------------------------------------
@needs_data
def test_v1_compat_20_window_label_payload_identical():
    rec, labels = _build("2026-06-20", "2026-07-09", 20, 50, 1000)
    assert rec["verdict"] == v2.V2_VERDICT_READY, rec["blockers"]
    assert len(labels) == 1000
    v1 = json.loads(V1_ARTIFACT.read_text(encoding="utf-8"))
    v1_labels = v1["labels"]
    assert len(v1_labels) == 1000
    # identical content + order
    assert labels == v1_labels
    # identical canonical label payload bytes + SHA-256
    v2_bytes = v2.canonical_label_payload_bytes(labels)
    v1_bytes = v2.canonical_label_payload_bytes(v1_labels)
    assert v2_bytes == v1_bytes
    assert hashlib.sha256(v2_bytes).hexdigest() == hashlib.sha256(v1_bytes).hexdigest()


# ---- data-dependent: full 26-window acceptance ---------------------------------------------
@needs_data
def test_full_26_window_build_and_validate():
    rec, labels = _build("2026-06-20", "2026-07-15", 26, 50, 1300)
    assert rec["verdict"] == v2.V2_VERDICT_READY, rec["blockers"]
    assert rec["blockers"] == []
    assert len(rec["per_window"]) == 26
    assert len(labels) == 1300
    assert all(p["row_count"] == 50 and p["structurally_valid"] for p in rec["per_window"])
    assert [p["run_date"] for p in rec["per_window"]] == list(rec["expected_dates"])
    assert v2.validate_range_multi_window(rec)["valid"] is True


@needs_data
def test_determinism_two_independent_builds_byte_identical():
    r1, l1 = _build("2026-06-20", "2026-07-15", 26, 50, 1300)
    r2, l2 = _build("2026-06-20", "2026-07-15", 26, 50, 1300)
    b1 = v2.canonical_v2_artifact_bytes(v2.build_v2_aggregate_payload(r1, l1))
    b2 = v2.canonical_v2_artifact_bytes(v2.build_v2_aggregate_payload(r2, l2))
    assert b1 == b2
    assert hashlib.sha256(b1).hexdigest() == hashlib.sha256(b2).hexdigest()
    assert r1["aggregate_manifest_sha256"] == r2["aggregate_manifest_sha256"]
    assert r1["canonical_label_payload_sha256"] == r2["canonical_label_payload_sha256"]
    assert l1 == l2


@needs_data
def test_provenance_tier_counts_8_12_6():
    rec, _ = _build("2026-06-20", "2026-07-15", 26, 50, 1300)
    assert rec["provenance_tier_counts"] == {
        "LEGACY_REDUCED_ONLY": 8, "LEGACY_REDUCED_WITH_SIDECAR_NO_RAW": 12,
        "FULL_RAW_REDUCTION_PROVENANCE": 6}
    assert rec["end_to_end_provenance_complete_all_windows"] is False
    assert rec["pre_build_status"] == "LABEL_SOURCE_INTEGRITY_PASS_WITH_LEGACY_PROVENANCE_GAP"
    by_date = {p["run_date"]: p for p in rec["per_window"]}
    assert by_date["2026-06-20"]["raw_status"] == "MISSING_BY_DESIGN"
    assert by_date["2026-06-20"]["sidecar_status"] == "MISSING_BY_DESIGN"
    assert by_date["2026-06-28"]["sidecar_status"] == "PRESENT_MANDATORY"
    assert by_date["2026-06-28"]["raw_status"] == "MISSING_BY_DESIGN"
    assert by_date["2026-07-10"]["raw_status"] == "PRESENT_MANDATORY"
    assert by_date["2026-07-10"]["sidecar_status"] == "PRESENT_MANDATORY"


@needs_data
def test_original_20_subset_unchanged_within_26():
    _, l20 = _build("2026-06-20", "2026-07-09", 20, 50, 1000)
    _, l26 = _build("2026-06-20", "2026-07-15", 26, 50, 1300)
    assert l26[:1000] == l20  # first 20 windows identical inside the 26-window build


@needs_data
def test_six_new_windows_contribute_exactly_300_rows():
    _, l26 = _build("2026-06-20", "2026-07-15", 26, 50, 1300)
    ext = [r for r in l26 if r["source_date"] >= "2026-07-10"]
    assert len(ext) == 300
    dates = sorted({r["source_date"] for r in ext})
    assert dates == ["2026-07-10", "2026-07-11", "2026-07-12", "2026-07-13",
                     "2026-07-14", "2026-07-15"]


@needs_data
def test_deterministic_row_ordering_stable():
    _, l26 = _build("2026-06-20", "2026-07-15", 26, 50, 1300)
    # rows are grouped by ascending source_date, and order_index 0..49 within each window
    prev_date = ""
    for i in range(0, 1300, 50):
        window = l26[i:i + 50]
        d = window[0]["source_date"]
        assert d >= prev_date
        assert [r["order_index"] for r in window] == list(range(50))
        assert all(r["source_date"] == d for r in window)
        prev_date = d
