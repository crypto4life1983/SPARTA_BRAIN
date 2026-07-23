"""C22 Phase B3 historical-evidence acquisition-plan tests. The 22-asset feasibility matrix is
DERIVED from the frozen V2 -> Phase-B2 records (data-dependent; skips cleanly if absent). Pure-
logic tests need no data. Verifies: all 22 assets, no cross-venue substitution, SPX collision +
venue-locked + sensitive retained, 6 Binance partial insufficient, no current-availability
inference, external assumptions marked, source hierarchy enforced (T5 never decisive),
credential permissions read-only/no-auth, no fetch/admission capability, deterministic
serialization, stable hash, byte-identical report rerender, no lifecycle/replay-token reuse."""
import hashlib
import json

import pytest

import sparta_commander.c22_historical_evidence_acquisition_plan_contract as ap
import sparta_commander.c22_short_instrument_evidence_request_contract as er
import sparta_commander.external_signum_trend_radar_gc_long_short_v1_replay_spec_contract as spec
import tools.c22_historical_evidence_acquisition_plan_report_once as rpt

_HAS_DATA = rpt.V2_ARTIFACT.exists()
needs_data = pytest.mark.skipif(not _HAS_DATA, reason="frozen V2 artifact not present")


# ---------------- pure-logic (no data) ----------------
def test_difficulty_is_deterministic_and_honest():
    # venue-locked native + high-collision -> POSSIBLY_UNAVAILABLE
    assert ap.acquisition_difficulty("GATE", er.MAPPING_RISK_VENUE_LOCKED, False) == \
        "POSSIBLY_UNAVAILABLE"
    assert ap.acquisition_difficulty("KRAKEN", er.MAPPING_RISK_HIGH_COLLISION, False) == \
        "POSSIBLY_UNAVAILABLE"
    # mapping-sensitive -> HIGH; non-Binance standard -> HIGH
    assert ap.acquisition_difficulty("BYBIT", er.MAPPING_RISK_SENSITIVE, False) == "HIGH"
    assert ap.acquisition_difficulty("KRAKEN", er.MAPPING_RISK_STANDARD, False) == "HIGH"
    # Binance partial -> MEDIUM; Binance standard -> LOW
    assert ap.acquisition_difficulty("BINANCE", er.MAPPING_RISK_STANDARD, True) == "MEDIUM"
    assert ap.acquisition_difficulty("BINANCE", er.MAPPING_RISK_STANDARD, False) == "LOW"


def test_source_hierarchy_t5_never_decisive():
    assert ap.SOURCE_HIERARCHY[-1].endswith("EXPLORATORY_ONLY_NOT_DECISIVE")
    rules = ap._source_hierarchy_rules()
    # every category rule marks T5 unacceptable and requires sha256 + admission review
    for rule in rules.values():
        assert rule["unacceptable_source_class"] == ap.SOURCE_HIERARCHY[4]
        assert "SHA-256" in rule["sha256_or_content_manifest_requirement"]
        assert "admission review" in rule["admission_review_requirement"]


def test_prohibited_permissions_and_credential_classes():
    for perm in ("trading_permissions", "withdrawal_permissions", "order_permissions",
                 "unrestricted_api_keys", "secrets_committed_to_repository",
                 "credentials_in_reports_or_logs"):
        assert perm in ap.PROHIBITED_PERMISSIONS
    assert "PUBLIC_NO_AUTH" in ap.CREDENTIAL_CLASSES
    assert "AUTHENTICATED_READ_ONLY_API" in ap.CREDENTIAL_CLASSES


# ---------------- data-derived ----------------
@needs_data
def test_all_22_assets_and_fail_closed():
    plan = ap.build_acquisition_plan(rpt.b2_records())
    assert plan["asset_count"] == 22
    assert all(r["currently_fail_closed_both"] for r in plan["feasibility_matrix"])
    assert plan["verdict"] == ap.VERDICT_READY, plan["blockers"]
    assert plan["blockers"] == []


@needs_data
def test_no_cross_venue_substitution_everywhere():
    plan = ap.build_acquisition_plan(rpt.b2_records())
    assert all(r["no_cross_venue_substitution"] for r in plan["feasibility_matrix"])
    assert plan["cross_venue_substitution"] is False


@needs_data
def test_identity_risks_and_difficulty_retained():
    plan = ap.build_acquisition_plan(rpt.b2_records())
    byd = {r["signal_symbol"]: r for r in plan["feasibility_matrix"]}
    assert byd["KRAKEN:SPXUSD"]["mapping_risk_class"] == "HIGH_COLLISION_RISK"
    assert byd["KRAKEN:SPXUSD"]["expected_acquisition_difficulty"] == "POSSIBLY_UNAVAILABLE"
    for s in ("GATE:GTUSDT", "OKX:OKBUSDT", "BITFINEX:LEOUSD"):
        assert byd[s]["mapping_risk_class"] == "VENUE_LOCKED_NATIVE"
        assert byd[s]["expected_acquisition_difficulty"] == "POSSIBLY_UNAVAILABLE"
    for s in ("BYBIT:GRAMUSDT", "BYBIT:TELUSDT", "GATE:ASTERUSDT", "BINANCE:VIRTUALUSDT"):
        assert byd[s]["mapping_risk_class"] == "MAPPING_SENSITIVE"
        assert byd[s]["expected_acquisition_difficulty"] == "HIGH"
    # SPX gets the S&P-500 prohibition as a mandatory human decision + external mark
    assert any("prohibit_sp500" in d for d in byd["KRAKEN:SPXUSD"]["mandatory_human_decisions"])
    assert any("S&P 500" in a for a in byd["KRAKEN:SPXUSD"]["externally_unverified_assumptions"])


@needs_data
def test_six_binance_partial_and_no_current_inference():
    plan = ap.build_acquisition_plan(rpt.b2_records())
    byd = {r["signal_symbol"]: r for r in plan["feasibility_matrix"]}
    six = ("BINANCE:AAVEUSDT", "BINANCE:CRVUSDT", "BINANCE:LINKUSDT", "BINANCE:SOLUSDT",
           "BINANCE:TRXUSDT", "BINANCE:ZECUSDT")
    for s in six:
        assert byd[s]["current_local_evidence"]["funding_status"] == \
            "PARTIAL_EXPLORATORY_EVIDENCE_INSUFFICIENT"
        assert byd[s]["expected_acquisition_difficulty"] == "MEDIUM"
    # borrow absent for all; every asset carries an existence + borrow external mark
    for r in plan["feasibility_matrix"]:
        assert r["current_local_evidence"]["borrow_status"] == "ABSENT"
        joined = " ".join(r["externally_unverified_assumptions"])
        assert "existence" in joined and "borrow availability" in joined
        assert "REQUIRES_EXTERNAL_VERIFICATION" in joined
    # no capability infers existence from current listing
    assert plan["infers_existence_from_current_listing"] is False


@needs_data
def test_acquisition_groups_and_order():
    plan = ap.build_acquisition_plan(rpt.b2_records())
    g = plan["acquisition_groups"]
    assert set(g["VENUE_NATIVE_TOKENS"]) == {"GATE:GTUSDT", "OKX:OKBUSDT", "BITFINEX:LEOUSD"}
    assert g["HIGH_COLLISION_IDENTIFIERS"] == ["KRAKEN:SPXUSD"]
    assert set(g["MAPPING_SENSITIVE_OR_NEWER_ASSETS"]) == {
        "BYBIT:GRAMUSDT", "BYBIT:TELUSDT", "GATE:ASTERUSDT", "BINANCE:VIRTUALUSDT"}
    assert len(g["ASSETS_WITH_PARTIAL_LOCAL_EVIDENCE"]) == 6
    # every asset appears in exactly one of partial/no-local-evidence (disjoint cover)
    assert len(g["ASSETS_WITH_PARTIAL_LOCAL_EVIDENCE"]) + \
        len(g["ASSETS_WITH_NO_LOCAL_EVIDENCE"]) == 22
    assert plan["grouping_preserves_per_asset_validation"] is True
    # fail-close-early order: registry + mapping + funding/borrow gate before OHLC/fees
    assert plan["acquisition_order"][0] == "1_historical_instrument_existence_registry"
    assert "3_funding_or_borrow_availability" in plan["early_fail_close_steps"]


@needs_data
def test_layout_proposed_not_created_and_gitignore_untouched():
    plan = ap.build_acquisition_plan(rpt.b2_records())
    assert plan["layout_created_this_phase"] is False
    assert plan["creates_evidence_layout"] is False
    assert plan["modifies_gitignore"] is False
    # proposed root sits under data/ (already gitignored) -> no .gitignore edit needed
    assert plan["proposed_evidence_root"].startswith("data/")


@needs_data
def test_forward_horizon_and_authorization_sequence():
    plan = ap.build_acquisition_plan(rpt.b2_records())
    assert plan["no_new_entry_after"] == "2026-07-15"
    assert plan["initial_range_end"] == "2026-08-14"
    assert plan["extension_increment_days"] == 15
    assert plan["final_exit_end_date_known"] is False
    assert plan["frozen_entry_dates_immutable"] is True
    seq = [b["batch"] for b in plan["proposed_authorization_sequence"]]
    assert seq == [
        "C22_INSTRUMENT_REGISTRY_FETCH_READY_FOR_HUMAN_AUTHORIZATION",
        "C22_FUNDING_AND_BORROW_FETCH_READY_FOR_HUMAN_AUTHORIZATION",
        "C22_EXECUTION_OHLC_FETCH_READY_FOR_HUMAN_AUTHORIZATION",
        "C22_FEES_AND_LIQUIDITY_FETCH_READY_FOR_HUMAN_AUTHORIZATION",
        "C22_HISTORICAL_INSTRUMENT_EVIDENCE_READY_FOR_ADMISSION_REVIEW"]
    assert plan["authorization_sequence_activated"] is False
    for b in plan["proposed_authorization_sequence"]:
        assert b["human_token"] != spec.REPLAY_ADVANCE_TOKEN


@needs_data
def test_capability_flags_false_and_validator():
    plan = ap.build_acquisition_plan(rpt.b2_records())
    for flag in ap._CAPABILITY_FLAGS_FALSE:
        assert plan[flag] is False, flag
    v = ap.validate_acquisition_plan(plan)
    assert v["valid"] is True, v["failures"]
    assert plan["acquisition_status"] == "NOT_AUTHORIZED"


@needs_data
def test_validator_rejects_tamper():
    # authorize acquisition -> invalid
    t = ap.build_acquisition_plan(rpt.b2_records()); t["acquisition_status"] = "AUTHORIZED"
    assert ap.validate_acquisition_plan(t)["valid"] is False
    # allow T5 decisive -> invalid
    t2 = ap.build_acquisition_plan(rpt.b2_records()); t2["t5_never_decisive"] = False
    assert ap.validate_acquisition_plan(t2)["valid"] is False
    # create layout -> invalid
    t3 = ap.build_acquisition_plan(rpt.b2_records()); t3["layout_created_this_phase"] = True
    assert ap.validate_acquisition_plan(t3)["valid"] is False


@needs_data
def test_deterministic_serialization_and_stable_hash():
    p1 = ap.build_acquisition_plan(rpt.b2_records())
    p2 = ap.build_acquisition_plan(rpt.b2_records())
    assert ap.canonical_plan_bytes(p1) == ap.canonical_plan_bytes(p2)
    assert p1["contract_sha256"] == p2["contract_sha256"]
    assert p1["contract_sha256"] == hashlib.sha256(ap.canonical_plan_bytes(p1)).hexdigest()
    assert "contract_sha256" not in json.loads(ap.canonical_plan_bytes(p1))


@needs_data
def test_report_deterministic_and_22_rows():
    r1 = rpt.build_report(); r2 = rpt.build_report()
    assert rpt.canonical_report_bytes(r1) == rpt.canonical_report_bytes(r2)
    assert rpt.render_markdown(r1) == rpt.render_markdown(r2)
    assert len(r1["acquisition_plan"]["feasibility_matrix"]) == 22
