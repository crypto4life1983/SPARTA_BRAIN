"""Tests for the Crypto-D1 Funding Rate Evidence Contract (Bundle 63 Block 121).
Verifies the read-only classification of funding-rate scanner ideas into
observation-only evidence buckets, the explicit per-feature stances, the
execution-safety override, the all-false safety posture, and the
independent-confirmation requirement. The contract authorizes nothing, unlocks
no gate, and connects to no exchange/API/account."""

from __future__ import annotations

from sparta_commander.strategy_factory_crypto_d1_funding_rate_evidence_contract import (  # noqa: E501
    FUNDING_RATE_EVIDENCE_SCHEMA_VERSION,
    DEFAULT_FUNDING_RATE_EVIDENCE_LABEL,
    FUNDING_RATE_EVIDENCE_STATUS,
    FUNDING_RATE_EVIDENCE_MODE,
    FUNDING_RATE_EVIDENCE_SAFETY_POSTURE,
    FUNDING_RATE_EVIDENCE_CLASSIFICATION_BUCKETS,
    BUCKET_USEFUL_FOR_RESEARCH,
    BUCKET_RISKY_REQUIRES_VALIDATION,
    BUCKET_BLOCKED_EXECUTION_FEATURE,
    BUCKET_IGNORE_OR_MARKETING_CLAIM,
    BUCKET_NEEDS_INDEPENDENT_CONFIRMATION,
    FUNDING_RATE_CANONICAL_FEATURE_CLASSIFICATIONS,
    FUNDING_RATE_EVIDENCE_FORBIDDEN_ALLOW_FLAGS,
    FUNDING_RATE_REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED,
    FUNDING_RATE_EVIDENCE_NEXT_REQUIRED_ACTION,
    FUNDING_RATE_EVIDENCE_CURRENT_STAGE,
    classify_funding_rate_evidence_claim,
    build_crypto_d1_funding_rate_evidence_contract,
    validate_crypto_d1_funding_rate_evidence_contract,
    render_crypto_d1_funding_rate_evidence_contract_markdown,
)


# --------------------------------------------------------------------------
# Schema / constants
# --------------------------------------------------------------------------

def test_schema_version_is_v1():
    assert FUNDING_RATE_EVIDENCE_SCHEMA_VERSION == (
        "strategy_factory_crypto_d1_funding_rate_evidence_contract.v1"
    )


def test_mode_is_research_only():
    assert FUNDING_RATE_EVIDENCE_MODE == "RESEARCH_ONLY"


def test_status_constant():
    assert FUNDING_RATE_EVIDENCE_STATUS == (
        "READ_ONLY_CRYPTO_D1_FUNDING_RATE_EVIDENCE_CONTRACT"
    )


def test_five_buckets_exact():
    assert FUNDING_RATE_EVIDENCE_CLASSIFICATION_BUCKETS == (
        BUCKET_USEFUL_FOR_RESEARCH,
        BUCKET_RISKY_REQUIRES_VALIDATION,
        BUCKET_BLOCKED_EXECUTION_FEATURE,
        BUCKET_IGNORE_OR_MARKETING_CLAIM,
        BUCKET_NEEDS_INDEPENDENT_CONFIRMATION,
    )


def test_safety_posture_all_false():
    posture = FUNDING_RATE_EVIDENCE_SAFETY_POSTURE
    assert len(posture) > 0
    assert all(v is False for v in posture.values())


def test_next_required_action_is_build_funding_rate():
    assert FUNDING_RATE_EVIDENCE_NEXT_REQUIRED_ACTION == (
        "BUILD_CRYPTO_D1_FUNDING_RATE_EVIDENCE_CONTRACT"
    )


def test_current_stage_constant():
    assert FUNDING_RATE_EVIDENCE_CURRENT_STAGE == (
        "CRYPTO_D1_FUNDING_RATE_EVIDENCE_CONTRACT_REQUIRED"
    )


def test_remaining_capabilities_block_execution_surfaces():
    blocked = FUNDING_RATE_REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED
    for cap in (
        "exchange_api_connection",
        "futures_or_perps_account_access",
        "position_opening",
        "hedging",
        "carry_trade_execution",
        "arbitrage_execution",
        "live_funding_monitor",
        "order_placement",
        "paper_or_live_trading",
        "strategy_promotion",
        "downstream_gate_unlock",
    ):
        assert cap in blocked


# --------------------------------------------------------------------------
# Explicit per-feature classification rules
# --------------------------------------------------------------------------

def test_funding_rate_scanning_is_useful_never_execution():
    r = classify_funding_rate_evidence_claim("Funding rate scanning")
    assert r["bucket"] == BUCKET_USEFUL_FOR_RESEARCH
    assert r["execution_capable"] is False
    assert "never execution" in r["reason"].lower()


def test_funding_rate_observation_needs_confirmation():
    r = classify_funding_rate_evidence_claim("Funding rate observation")
    assert r["bucket"] == BUCKET_NEEDS_INDEPENDENT_CONFIRMATION
    assert r["execution_capable"] is False


def test_basis_spread_observation_needs_confirmation():
    r = classify_funding_rate_evidence_claim("Basis spread observation")
    assert r["bucket"] == BUCKET_NEEDS_INDEPENDENT_CONFIRMATION
    assert r["execution_capable"] is False


def test_positive_funding_claim_is_risky():
    r = classify_funding_rate_evidence_claim("Positive funding rate claim")
    assert r["bucket"] == BUCKET_RISKY_REQUIRES_VALIDATION
    assert r["execution_capable"] is False


def test_negative_funding_claim_is_risky():
    r = classify_funding_rate_evidence_claim("Negative funding rate claim")
    assert r["bucket"] == BUCKET_RISKY_REQUIRES_VALIDATION
    assert r["execution_capable"] is False


def test_funding_offline_study_is_useful_research():
    r = classify_funding_rate_evidence_claim(
        "Offline historical funding rate study"
    )
    assert r["bucket"] == BUCKET_USEFUL_FOR_RESEARCH
    assert r["execution_capable"] is False


def test_carry_trade_execution_is_blocked():
    r = classify_funding_rate_evidence_claim("Auto-carry bot execution")
    assert r["bucket"] == BUCKET_BLOCKED_EXECUTION_FEATURE
    assert r["execution_capable"] is True


def test_arbitrage_execution_is_blocked():
    r = classify_funding_rate_evidence_claim("Funding arbitrage execution")
    assert r["bucket"] == BUCKET_BLOCKED_EXECUTION_FEATURE
    assert r["execution_capable"] is True


def test_exchange_api_connection_is_blocked():
    r = classify_funding_rate_evidence_claim("Exchange API funding monitor")
    assert r["bucket"] == BUCKET_BLOCKED_EXECUTION_FEATURE
    assert r["execution_capable"] is True


def test_futures_account_access_is_blocked():
    r = classify_funding_rate_evidence_claim("Futures account access")
    assert r["bucket"] == BUCKET_BLOCKED_EXECUTION_FEATURE
    assert r["execution_capable"] is True


def test_position_opening_is_blocked():
    r = classify_funding_rate_evidence_claim("Open position on funding flip")
    assert r["bucket"] == BUCKET_BLOCKED_EXECUTION_FEATURE
    assert r["execution_capable"] is True


def test_hedging_logic_is_blocked():
    r = classify_funding_rate_evidence_claim("Hedging logic for funding carry")
    assert r["bucket"] == BUCKET_BLOCKED_EXECUTION_FEATURE
    assert r["execution_capable"] is True


def test_live_funding_monitor_is_blocked():
    r = classify_funding_rate_evidence_claim("Live funding monitor")
    assert r["bucket"] == BUCKET_BLOCKED_EXECUTION_FEATURE
    assert r["execution_capable"] is True


def test_guaranteed_yield_is_marketing():
    r = classify_funding_rate_evidence_claim("Guaranteed funding yield")
    assert r["bucket"] == BUCKET_IGNORE_OR_MARKETING_CLAIM


def test_risk_free_funding_is_marketing():
    r = classify_funding_rate_evidence_claim("Risk-free funding")
    assert r["bucket"] == BUCKET_IGNORE_OR_MARKETING_CLAIM


# --------------------------------------------------------------------------
# Heuristic + safety override behavior
# --------------------------------------------------------------------------

def test_marketing_claim_is_ignored():
    r = classify_funding_rate_evidence_claim(
        "guaranteed yield, risk-free, can't lose"
    )
    assert r["bucket"] == BUCKET_IGNORE_OR_MARKETING_CLAIM


def test_unknown_funding_claim_defaults_to_risky():
    r = classify_funding_rate_evidence_claim(
        "a brand new funding alpha edge idea"
    )
    assert r["bucket"] == BUCKET_RISKY_REQUIRES_VALIDATION


def test_execution_keyword_forces_blocked():
    r = classify_funding_rate_evidence_claim(
        "funding scanner that will place order automatically"
    )
    assert r["bucket"] == BUCKET_BLOCKED_EXECUTION_FEATURE
    assert r["execution_capable"] is True


def test_forbidden_allow_flag_forces_blocked():
    r = classify_funding_rate_evidence_claim(
        {"claim": "funding rate observation", "allow_execution": True}
    )
    assert r["bucket"] == BUCKET_BLOCKED_EXECUTION_FEATURE
    assert "allow_execution" in r["requested_forbidden_flags"]


def test_empty_claim_defaults_to_risky():
    r = classify_funding_rate_evidence_claim("")
    assert r["bucket"] == BUCKET_RISKY_REQUIRES_VALIDATION


def test_malformed_claim_never_raises():
    for bad in (None, 123, [], {}, object()):
        r = classify_funding_rate_evidence_claim(bad)
        assert r["bucket"] in FUNDING_RATE_EVIDENCE_CLASSIFICATION_BUCKETS
        assert r["authorizes_nothing"] is True


def test_every_classified_claim_authorizes_nothing():
    r = classify_funding_rate_evidence_claim("Funding rate scanning")
    assert r["authorizes_nothing"] is True


def test_canonical_map_covers_named_features():
    for feature_id in (
        "funding_rate_scanning",
        "funding_rate_observation",
        "positive_funding_claim",
        "negative_funding_claim",
        "basis_spread_observation",
        "funding_rate_offline_study",
        "carry_trade_execution",
        "arbitrage_execution",
        "exchange_api_connection",
        "futures_account_access",
        "position_opening",
        "hedging_logic",
        "live_funding_monitor",
        "guaranteed_yield_claim",
        "risk_free_funding_claim",
    ):
        assert feature_id in FUNDING_RATE_CANONICAL_FEATURE_CLASSIFICATIONS


def test_every_canonical_execution_capable_is_blocked():
    for spec in FUNDING_RATE_CANONICAL_FEATURE_CLASSIFICATIONS.values():
        if spec["execution_capable"]:
            assert spec["bucket"] == BUCKET_BLOCKED_EXECUTION_FEATURE


# --------------------------------------------------------------------------
# Build / validate
# --------------------------------------------------------------------------

def test_build_default_classifies_eight_source_claims():
    c = build_crypto_d1_funding_rate_evidence_contract()
    assert len(c["classified_claims"]) == 8
    assert len(c["submitted_claims"]) == 8


def test_build_default_bucket_distribution():
    c = build_crypto_d1_funding_rate_evidence_contract()
    counts = c["classification_counts"]
    assert counts[BUCKET_USEFUL_FOR_RESEARCH] == 2
    assert counts[BUCKET_NEEDS_INDEPENDENT_CONFIRMATION] == 1
    assert counts[BUCKET_RISKY_REQUIRES_VALIDATION] == 1
    assert counts[BUCKET_BLOCKED_EXECUTION_FEATURE] == 2
    assert counts[BUCKET_IGNORE_OR_MARKETING_CLAIM] == 2


def test_build_is_valid():
    c = build_crypto_d1_funding_rate_evidence_contract()
    v = validate_crypto_d1_funding_rate_evidence_contract(c)
    assert v["valid"] is True


def test_build_safety_flags():
    c = build_crypto_d1_funding_rate_evidence_contract()
    assert c["read_only"] is True
    assert c["executes"] is False
    assert c["authorizes_real_world_action"] is False
    assert c["unlocks_downstream_gate"] is False
    assert c["human_approval_required"] is True


def test_build_requires_independent_confirmation():
    c = build_crypto_d1_funding_rate_evidence_contract()
    assert c["requires_independent_confirmation"] is True


def test_build_gates_remain_blocked_and_locked():
    c = build_crypto_d1_funding_rate_evidence_contract()
    assert c["real_data_qa_blocked"] is True
    assert c["baseline_backtest_blocked"] is True
    assert c["paper_trading_gate_locked"] is True
    assert c["micro_live_gate_locked"] is True


def test_build_safety_posture_all_false():
    c = build_crypto_d1_funding_rate_evidence_contract()
    posture = c["safety_posture"]
    assert len(posture) > 0
    assert all(v is False for v in posture.values())


def test_build_counts_sum_to_claim_total():
    c = build_crypto_d1_funding_rate_evidence_contract()
    counts = c["classification_counts"]
    assert set(counts.keys()) == set(
        FUNDING_RATE_EVIDENCE_CLASSIFICATION_BUCKETS
    )
    assert sum(counts.values()) == len(c["classified_claims"])


def test_build_custom_claims():
    c = build_crypto_d1_funding_rate_evidence_contract(
        ["Auto-carry bot execution", "Funding rate scanning"]
    )
    buckets = [item["bucket"] for item in c["classified_claims"]]
    assert BUCKET_BLOCKED_EXECUTION_FEATURE in buckets
    assert BUCKET_USEFUL_FOR_RESEARCH in buckets


def test_build_is_deterministic():
    a = build_crypto_d1_funding_rate_evidence_contract()
    b = build_crypto_d1_funding_rate_evidence_contract()
    assert a == b


def test_build_returns_isolated_copies():
    a = build_crypto_d1_funding_rate_evidence_contract()
    a["classified_claims"].append({"bucket": "tampered"})
    a["safety_posture"]["places_order"] = True
    b = build_crypto_d1_funding_rate_evidence_contract()
    assert len(b["classified_claims"]) == 8
    assert b["safety_posture"]["places_order"] is False


def test_validate_rejects_non_dict():
    v = validate_crypto_d1_funding_rate_evidence_contract(None)
    assert v["valid"] is False


def test_validate_rejects_executes_true():
    c = build_crypto_d1_funding_rate_evidence_contract()
    c["executes"] = True
    v = validate_crypto_d1_funding_rate_evidence_contract(c)
    assert v["valid"] is False


def test_validate_rejects_unlocked_gate():
    c = build_crypto_d1_funding_rate_evidence_contract()
    c["real_data_qa_blocked"] = False
    v = validate_crypto_d1_funding_rate_evidence_contract(c)
    assert v["valid"] is False
    assert v["gates_locked"] is False


def test_validate_rejects_confirmation_disabled():
    c = build_crypto_d1_funding_rate_evidence_contract()
    c["requires_independent_confirmation"] = False
    v = validate_crypto_d1_funding_rate_evidence_contract(c)
    assert v["valid"] is False
    assert v["confirmation_required"] is False


def test_validate_rejects_execution_capable_in_wrong_bucket():
    c = build_crypto_d1_funding_rate_evidence_contract()
    c["classified_claims"].append(
        {
            "claim": "tampered",
            "bucket": BUCKET_USEFUL_FOR_RESEARCH,
            "execution_capable": True,
            "authorizes_nothing": True,
        }
    )
    v = validate_crypto_d1_funding_rate_evidence_contract(c)
    assert v["valid"] is False
    assert v["execution_safe"] is False


def test_forbidden_flag_list_covers_execution_surfaces():
    flags = FUNDING_RATE_EVIDENCE_FORBIDDEN_ALLOW_FLAGS
    for f in (
        "allow_execution",
        "allow_exchange_api",
        "allow_futures_account",
        "allow_position_opening",
        "allow_hedging",
        "allow_carry_execution",
        "allow_arbitrage_execution",
        "allow_live_funding_monitor",
        "allow_downstream_gate_unlock",
    ):
        assert f in flags


# --------------------------------------------------------------------------
# Render
# --------------------------------------------------------------------------

def test_render_is_string_and_mentions_blocked_gates():
    c = build_crypto_d1_funding_rate_evidence_contract()
    md = render_crypto_d1_funding_rate_evidence_contract_markdown(c)
    assert isinstance(md, str)
    assert "Funding Rate Evidence" in md
    assert "real_data_qa blocked: True" in md


def test_label_constant():
    assert DEFAULT_FUNDING_RATE_EVIDENCE_LABEL == (
        "Strategy Factory Crypto-D1 Funding Rate Evidence Contract"
    )
