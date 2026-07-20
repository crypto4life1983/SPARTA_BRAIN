"""C22 V2 label evidence integrity report tests: pure concentration / accounting /
fail-closed recommendation logic, deterministic serialization, and (data-dependent,
skipped on a clean checkout) the full 26-window / 1,300-row report over the frozen range."""
import json

import pytest

import tools.c22_signum_gc_v2_label_evidence_integrity_report_once as rpt
import sparta_commander.external_signum_trend_radar_gc_long_short_v2_range_multi_window_real_candle_labels_contract as v2
import tools.c22_signum_trend_radar_gc_v2_range_multi_window_real_candle_labels_once as runner

_ART = runner.OUT_DIR / v2.v2_artifact_filename("2026-06-20", "2026-07-15", 26)
needs_data = pytest.mark.skipif(not _ART.exists(), reason="built V2 artifact not present")


def _lbl(date, sym, sig):
    return {"source_date": date, "symbol": sym, "signal": sig}


def test_signal_concentration_by_date_symbol_and_type():
    labels = [_lbl("2026-06-20", "BTC", "NONE"), _lbl("2026-06-20", "ETH", "BEAR_SHORT"),
              _lbl("2026-06-21", "ETH", "BEAR_SHORT"), _lbl("2026-06-21", "SOL", "LONG_ENTRY")]
    c = rpt.signal_concentration(labels)
    assert c["by_signal"] == {"NONE": 1, "BEAR_SHORT": 2, "LONG_ENTRY": 1}
    assert c["by_date"]["2026-06-20"] == {"NONE": 1, "BEAR_SHORT": 1}
    assert c["by_date"]["2026-06-21"] == {"BEAR_SHORT": 1, "LONG_ENTRY": 1}
    # NONE rows are excluded from the per-asset actionable view
    assert "BTC" not in c["by_symbol_non_none"]
    assert c["by_symbol_non_none"]["ETH"] == {"BEAR_SHORT": 2}
    assert c["by_symbol_non_none"]["SOL"] == {"LONG_ENTRY": 1}


def test_provenance_accounting_splits_by_design_vs_mandatory():
    per_window = [
        {"run_date": "2026-06-20", "raw_status": "MISSING_BY_DESIGN",
         "sidecar_status": "MISSING_BY_DESIGN"},
        {"run_date": "2026-06-28", "raw_status": "MISSING_BY_DESIGN",
         "sidecar_status": "PRESENT_MANDATORY"},
        {"run_date": "2026-07-10", "raw_status": "PRESENT_MANDATORY",
         "sidecar_status": "PRESENT_MANDATORY"},
        {"run_date": "2026-07-11", "raw_status": "MISSING_MANDATORY",
         "sidecar_status": "PRESENT_MANDATORY"},
    ]
    acc = rpt.provenance_accounting(per_window)
    assert acc["windows_missing_raw_by_design"] == ["2026-06-20", "2026-06-28"]
    assert acc["windows_missing_raw_mandatory"] == ["2026-07-11"]
    assert acc["windows_missing_sidecar_by_design"] == ["2026-06-20"]
    assert acc["windows_missing_sidecar_mandatory"] == []
    assert acc["windows_full_provenance"] == ["2026-07-10"]


def test_recommendation_fails_closed():
    ok_validator = {"valid": True, "failures": []}
    # wrong counts -> blocked
    d = rpt.decide_recommendation({"labels": [], "per_window": []}, ok_validator, True,
                                  v2.V2_VERDICT_READY, [])
    assert d["recommendation"] == rpt.RECOMMEND_BLOCKED
    assert any("window_count" in r for r in d["reasons"])
    # non-byte-identical rebuild -> blocked even with READY verdict
    art = {"labels": [{}] * 1300,
           "per_window": [{"run_date": "d", "raw_status": "PRESENT_MANDATORY",
                           "sidecar_status": "PRESENT_MANDATORY"}] * 26}
    d = rpt.decide_recommendation(art, ok_validator, False, v2.V2_VERDICT_READY, [])
    assert d["recommendation"] == rpt.RECOMMEND_BLOCKED
    assert "rebuild_not_byte_identical_to_artifact" in d["reasons"]
    # blocked verdict propagates
    d = rpt.decide_recommendation(art, ok_validator, True, v2.V2_VERDICT_BLOCKED, ["x"])
    assert d["recommendation"] == rpt.RECOMMEND_BLOCKED
    # all conditions hold -> ready
    d = rpt.decide_recommendation(art, ok_validator, True, v2.V2_VERDICT_READY, [])
    assert d["recommendation"] == rpt.RECOMMEND_READY
    assert d["reasons"] == []


def test_canonical_report_bytes_deterministic():
    r = {"b": 1, "a": {"z": 2, "y": 3}}
    assert rpt.canonical_report_bytes(r) == rpt.canonical_report_bytes(json.loads(
        json.dumps(r)))
    assert rpt.canonical_report_bytes(r).endswith(b"\n")


@needs_data
def test_full_report_over_frozen_range_is_ready_and_deterministic():
    r1 = rpt.run_report()
    r2 = rpt.run_report()
    assert rpt.canonical_report_bytes(r1) == rpt.canonical_report_bytes(r2)
    assert r1["window_count"] == 26
    assert r1["labels_total"] == 1300
    assert r1["window_start"] == "2026-06-20" and r1["window_end"] == "2026-07-15"
    assert sum(r1["aggregate_label_counts"].values()) == 1300
    assert r1["provenance_tier_counts"] == {
        "LEGACY_REDUCED_ONLY": 8, "LEGACY_REDUCED_WITH_SIDECAR_NO_RAW": 12,
        "FULL_RAW_REDUCTION_PROVENANCE": 6}
    assert r1["byte_identical_rebuild"] is True
    assert r1["validator_valid"] is True
    assert r1["recommendation"] == rpt.RECOMMEND_READY
    assert r1["recommendation_reasons"] == []
    # July 16/17 must not appear anywhere in the evidence
    assert "2026-07-16" not in r1["per_window_label_counts"]
    assert "2026-07-17" not in r1["per_window_label_counts"]
    assert all(d <= "2026-07-15" for d in r1["signal_concentration"]["by_date"])
    # accounting matches the honest tiers
    acc = r1["provenance_accounting"]
    assert len(acc["windows_missing_raw_by_design"]) == 20      # 06-20 .. 07-09
    assert acc["windows_missing_raw_mandatory"] == []
    assert len(acc["windows_missing_sidecar_by_design"]) == 8   # 06-20 .. 06-27
    assert acc["windows_missing_sidecar_mandatory"] == []
    assert len(acc["windows_full_provenance"]) == 6             # 07-10 .. 07-15
    # markdown render is deterministic and carries the verdict
    md1, md2 = rpt.render_markdown(r1), rpt.render_markdown(r2)
    assert md1 == md2
    assert rpt.RECOMMEND_READY in md1
    assert "token" not in md1.lower() or r1["token_issued"] is False
