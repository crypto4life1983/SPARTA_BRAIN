"""C22 V3_EXTENDED integrity report: rebuild check, V2-unchanged pin, V2-subset identity,
read-only unless --execute-write."""
from __future__ import annotations

import importlib
import json

import pytest

rep = importlib.import_module("tools.c22_signum_gc_v3_label_evidence_integrity_report_once")


def _mk(rows):
    return [{"source_date": d, "order_index": i, "symbol": s, "signal": sig} for d, i, s, sig in rows]


def test_v2_subset_check_identical_when_v3_reproduces_v2():
    v2 = {"window_start": "2026-06-20", "window_end": "2026-06-21",
          "labels": _mk([("2026-06-20", 0, "A", "LONG_ENTRY"), ("2026-06-21", 0, "A", "NONE")])}
    v3 = _mk([("2026-06-21", 0, "A", "NONE"), ("2026-06-20", 0, "A", "LONG_ENTRY"), ("2026-06-22", 0, "A", "BEAR_SHORT")])
    r = rep.v2_subset_check(v3, v2)
    assert r["canonical_identical"] is True
    assert (r["v3_rows_in_v2_range"], r["v2_rows"], r["v2_actionable"], r["v3_actionable_after_v2_range"]) == (2, 2, 1, 1)


def test_v2_subset_check_detects_any_signal_change():
    v2 = {"window_start": "2026-06-20", "window_end": "2026-06-20", "labels": _mk([("2026-06-20", 0, "A", "LONG_ENTRY")])}
    v3 = _mk([("2026-06-20", 0, "A", "NONE")])
    assert rep.v2_subset_check(v3, v2)["canonical_identical"] is False


def test_frozen_v2_pin_is_the_known_hash():
    assert rep.V2_FROZEN_ARTIFACT_SHA256 == "b6a28a4873d1aff17014a9d598702c67047b4ebe023b8cfddce05094f9ce9dd8"
    assert rep.V2_FROZEN_ACTIONABLE == 88


def test_report_is_read_only_without_execute_write(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(rep, "REPORT_DIR", tmp_path)
    out = rep.main_with_args(["--profile", "V3_EXTENDED_SEG_B_24W"])
    assert out["written"] is False
    assert list(tmp_path.glob("*.json")) == [] and list(tmp_path.glob("*.md")) == []
    assert out["labels_total"] == 1200


def test_live_82w_report_passes_if_artifact_built():
    r = rep.run_v3_report("V3_EXTENDED_82W")
    if r["artifact_sha256_on_disk"] is None:
        pytest.skip("82w artifact not built in this checkout")
    assert r["byte_identical_rebuild"] is True
    assert r["v2_unchanged"] is True
    assert r["v2_subset_check"]["canonical_identical"] is True
    assert r["v2_subset_check"]["v2_actionable"] == 88
    assert r["recommendation"] == "V3_EVIDENCE_INTEGRITY_PASS_DIAGNOSTIC_ONLY"
    assert r["exit_only_window_count"] == 56 and r["window_count"] == 82
