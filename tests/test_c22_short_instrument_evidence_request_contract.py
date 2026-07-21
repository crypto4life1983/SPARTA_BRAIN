"""C22 Phase B2 short-instrument evidence-request tests. The 22-asset universe is DERIVED from
the frozen V2 artifact (data-dependent; skips cleanly if absent). Pure-logic tests need no data.
Verifies: 22 assets, 72 BEAR / 3 HEDGE, no dup/late dates, sign-flip assets retained, SPX
collision + GT/OKB/LEO venue-locked + 4 sensitive retained, 6 Binance partial-funding
insufficient, borrow absent for all, all fail-closed under both implementations, no
present-day inference, no fetch/select capability, deterministic serialization, stable hash,
byte-identical report rerender."""
import hashlib
import json

import pytest

import sparta_commander.c22_short_instrument_evidence_request_contract as er
import tools.c22_short_instrument_evidence_request_report_once as rpt

_HAS_DATA = rpt.V2_ARTIFACT.exists()
needs_data = pytest.mark.skipif(not _HAS_DATA, reason="frozen V2 artifact not present")


# ---------------- pure-logic (no data) ----------------
def test_mapping_risk_classes():
    assert er.mapping_risk_class("KRAKEN:SPXUSD") == "HIGH_COLLISION_RISK"
    for s in ("GATE:GTUSDT", "OKX:OKBUSDT", "BITFINEX:LEOUSD"):
        assert er.mapping_risk_class(s) == "VENUE_LOCKED_NATIVE"
    for s in ("BYBIT:GRAMUSDT", "BYBIT:TELUSDT", "GATE:ASTERUSDT", "BINANCE:VIRTUALUSDT"):
        assert er.mapping_risk_class(s) == "MAPPING_SENSITIVE"
    assert er.mapping_risk_class("BINANCE:TRXUSDT") == "STANDARD_MAPPING"


def test_parse_symbol():
    assert er.parse_symbol("BINANCE:TRXUSDT") == {
        "venue": "BINANCE", "pair": "TRXUSDT", "base": "TRX", "quote": "USDT"}
    assert er.parse_symbol("KRAKEN:SPXUSD") == {
        "venue": "KRAKEN", "pair": "SPXUSD", "base": "SPX", "quote": "USD"}


def test_asset_record_fails_closed_both_ways():
    rec = er.build_asset_record("BINANCE:TRXUSDT", ["2026-07-06", "2026-07-15"], 10, 0, [])
    assert rec["fail_closed_perp"] is True and rec["fail_closed_margin"] is True
    assert rec["borrow_status"] == "ABSENT"
    assert rec["required_entry_coverage"] == ["2026-06-20", "2026-07-15"]
    assert rec["required_exit_coverage"] == ["2026-07-16", "2026-08-14"]


def test_partial_funding_marker_only_for_six_binance():
    six = er.build_asset_record("BINANCE:AAVEUSDT", ["2026-06-26"], 1, 0, ["2026-06-27"])
    assert six["funding_status"] == "PARTIAL_EXPLORATORY_EVIDENCE_INSUFFICIENT"
    assert six["local_evidence"]["local_perp_funding_local_end"] == "2026-06-21"
    other = er.build_asset_record("GATE:GTUSDT", ["2026-07-04"], 12, 0, [])
    assert other["funding_status"] == "ABSENT"


def test_no_present_day_inference_marker():
    # the capability flag exists and is False; local evidence never asserts present availability
    recs = [er.build_asset_record("BINANCE:TRXUSDT", ["2026-07-06"], 1, 0, [])]
    # cannot build the full request from 1 record -> BLOCKED, but flags still present
    req = er.build_evidence_request(recs)
    assert req["infers_historical_from_present_availability"] is False


# ---------------- data-derived (frozen V2) ----------------
@needs_data
def test_derived_universe_exactly_22_and_counts():
    recs = rpt.derive_asset_records()
    req = er.build_evidence_request(recs)
    assert req["asset_count"] == 22
    assert sum(r["bear_short_count"] for r in req["asset_records"]) == 72
    assert sum(r["hedge_short_count"] for r in req["asset_records"]) == 3
    assert req["verdict"] == er.VERDICT_READY, req["blockers"]
    assert req["blockers"] == []


@needs_data
def test_derived_no_dupes_no_late_dates_no_conflicts():
    recs = rpt.derive_asset_records()
    seen = set()
    for r in recs:
        for d in r["short_signal_dates"]:
            assert d <= "2026-07-15"
            key = (r["signal_symbol"], d)
            assert key not in seen, "duplicate asset/date"
            seen.add(key)
        # per-asset dates unique (no same-day conflict rows collapsed to one asset)
        assert len(set(r["short_signal_dates"])) == len(r["short_signal_dates"])


@needs_data
def test_derived_sign_flip_assets_retained():
    recs = {r["signal_symbol"]: r for r in rpt.derive_asset_records()}
    assert recs["BINANCE:AAVEUSDT"]["long_entry_dates"] == ["2026-06-27"]
    assert recs["BINANCE:ZECUSDT"]["long_entry_dates"] == ["2026-07-15"]
    assert recs["COINBASE:MORPHOUSD"]["long_entry_dates"] == ["2026-07-10"]
    assert recs["KRAKEN:SPXUSD"]["long_entry_dates"] == ["2026-07-04", "2026-07-07"]


@needs_data
def test_derived_identity_risks_retained():
    recs = {r["signal_symbol"]: r for r in rpt.derive_asset_records()}
    assert recs["KRAKEN:SPXUSD"]["mapping_risk_class"] == "HIGH_COLLISION_RISK"
    for s in ("GATE:GTUSDT", "OKX:OKBUSDT", "BITFINEX:LEOUSD"):
        assert recs[s]["mapping_risk_class"] == "VENUE_LOCKED_NATIVE"
    for s in ("BYBIT:GRAMUSDT", "BYBIT:TELUSDT", "GATE:ASTERUSDT", "BINANCE:VIRTUALUSDT"):
        assert recs[s]["mapping_risk_class"] == "MAPPING_SENSITIVE"


@needs_data
def test_derived_six_binance_partial_rest_absent_and_all_fail_closed():
    req = er.build_evidence_request(rpt.derive_asset_records())
    recs = {r["signal_symbol"]: r for r in req["asset_records"]}
    six = ("BINANCE:AAVEUSDT", "BINANCE:CRVUSDT", "BINANCE:LINKUSDT", "BINANCE:SOLUSDT",
           "BINANCE:TRXUSDT", "BINANCE:ZECUSDT")
    for s in six:
        assert recs[s]["funding_status"] == "PARTIAL_EXPLORATORY_EVIDENCE_INSUFFICIENT"
    for s, r in recs.items():
        if s not in six:
            assert r["funding_status"] == "ABSENT"
        assert r["borrow_status"] == "ABSENT"
        assert r["fail_closed_perp"] is True and r["fail_closed_margin"] is True
    assert req["all_assets_fail_closed_perp"] is True
    assert req["all_assets_fail_closed_margin"] is True
    assert req["borrow_local_status_all"] == "ABSENT_FOR_ALL_22"


@needs_data
def test_capability_flags_false_and_validator():
    req = er.build_evidence_request(rpt.derive_asset_records())
    for flag in er._CAPABILITY_FLAGS_FALSE:
        assert req[flag] is False, flag
    v = er.validate_evidence_request(req)
    assert v["valid"] is True, v["failures"]
    assert req["acquisition_status"] == "NOT_AUTHORIZED"
    assert req["lifecycle_gates_activated"] is False
    assert req["final_exit_end_date_known"] is False
    # gates do not reuse the replay token
    import sparta_commander.external_signum_trend_radar_gc_long_short_v1_replay_spec_contract as spec
    for g in req["proposed_lifecycle_gates"]:
        assert g["human_token"] != spec.REPLAY_ADVANCE_TOKEN


@needs_data
def test_validator_rejects_tamper():
    req = er.build_evidence_request(rpt.derive_asset_records())
    # drop an asset
    t = er.build_evidence_request(rpt.derive_asset_records()[:-1])
    assert er.validate_evidence_request(t)["valid"] is False
    # flip SPX risk to standard
    t2 = er.build_evidence_request(rpt.derive_asset_records())
    for rec in t2["asset_records"]:
        if rec["signal_symbol"] == "KRAKEN:SPXUSD":
            rec["mapping_risk_class"] = "STANDARD_MAPPING"
    assert er.validate_evidence_request(t2)["valid"] is False


@needs_data
def test_deterministic_serialization_and_stable_hash():
    r1 = er.build_evidence_request(rpt.derive_asset_records())
    r2 = er.build_evidence_request(rpt.derive_asset_records())
    assert er.canonical_request_bytes(r1) == er.canonical_request_bytes(r2)
    assert r1["contract_sha256"] == r2["contract_sha256"]
    assert r1["contract_sha256"] == hashlib.sha256(er.canonical_request_bytes(r1)).hexdigest()
    assert "contract_sha256" not in json.loads(er.canonical_request_bytes(r1))


@needs_data
def test_report_deterministic_and_22_rows():
    rep1 = rpt.build_report(); rep2 = rpt.build_report()
    assert rpt.canonical_report_bytes(rep1) == rpt.canonical_report_bytes(rep2)
    assert rpt.render_markdown(rep1) == rpt.render_markdown(rep2)
    # canonical JSON keeps all 22 separate records (never grouped away)
    assert len(rep1["evidence_request"]["asset_records"]) == 22
