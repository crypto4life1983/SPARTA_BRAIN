"""Tests for the Crypto-D1 Hyperliquid Whale Evidence Contract (Bundle 62
Block 119). Verifies the read-only classification of Hyperliquid whale-tracking
ideas into observation-only evidence buckets, the explicit per-feature stances,
the execution-safety override, the all-false safety posture, and the
independent-confirmation requirement. The contract authorizes nothing, unlocks
no gate, and connects to no exchange/API/wallet."""

from __future__ import annotations

from sparta_commander.strategy_factory_crypto_d1_hyperliquid_whale_evidence_contract import (  # noqa: E501
    WHALE_EVIDENCE_SCHEMA_VERSION,
    DEFAULT_WHALE_EVIDENCE_LABEL,
    WHALE_EVIDENCE_STATUS,
    WHALE_EVIDENCE_MODE,
    WHALE_EVIDENCE_SAFETY_POSTURE,
    WHALE_EVIDENCE_CLASSIFICATION_BUCKETS,
    BUCKET_USEFUL_FOR_RESEARCH,
    BUCKET_RISKY_REQUIRES_VALIDATION,
    BUCKET_BLOCKED_EXECUTION_FEATURE,
    BUCKET_IGNORE_OR_MARKETING_CLAIM,
    BUCKET_NEEDS_INDEPENDENT_CONFIRMATION,
    WHALE_CANONICAL_FEATURE_CLASSIFICATIONS,
    WHALE_EVIDENCE_FORBIDDEN_ALLOW_FLAGS,
    WHALE_REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED,
    WHALE_EVIDENCE_NEXT_REQUIRED_ACTION,
    WHALE_EVIDENCE_CURRENT_STAGE,
    classify_whale_evidence_claim,
    build_crypto_d1_hyperliquid_whale_evidence_contract,
    validate_crypto_d1_hyperliquid_whale_evidence_contract,
    render_crypto_d1_hyperliquid_whale_evidence_contract_markdown,
)


# --------------------------------------------------------------------------
# Schema / constants
# --------------------------------------------------------------------------

def test_schema_version_is_v1():
    assert WHALE_EVIDENCE_SCHEMA_VERSION == (
        "strategy_factory_crypto_d1_hyperliquid_whale_evidence_contract.v1"
    )


def test_mode_is_research_only():
    assert WHALE_EVIDENCE_MODE == "RESEARCH_ONLY"


def test_status_constant():
    assert WHALE_EVIDENCE_STATUS == (
        "READ_ONLY_CRYPTO_D1_HYPERLIQUID_WHALE_EVIDENCE_CONTRACT"
    )


def test_five_buckets_exact():
    assert WHALE_EVIDENCE_CLASSIFICATION_BUCKETS == (
        BUCKET_USEFUL_FOR_RESEARCH,
        BUCKET_RISKY_REQUIRES_VALIDATION,
        BUCKET_BLOCKED_EXECUTION_FEATURE,
        BUCKET_IGNORE_OR_MARKETING_CLAIM,
        BUCKET_NEEDS_INDEPENDENT_CONFIRMATION,
    )


def test_safety_posture_all_false():
    posture = WHALE_EVIDENCE_SAFETY_POSTURE
    assert len(posture) > 0
    assert all(v is False for v in posture.values())


def test_next_required_action_is_build_whale():
    assert WHALE_EVIDENCE_NEXT_REQUIRED_ACTION == (
        "BUILD_CRYPTO_D1_HYPERLIQUID_WHALE_EVIDENCE_CONTRACT"
    )


def test_current_stage_constant():
    assert WHALE_EVIDENCE_CURRENT_STAGE == (
        "CRYPTO_D1_HYPERLIQUID_WHALE_EVIDENCE_CONTRACT_REQUIRED"
    )


def test_remaining_capabilities_block_execution_surfaces():
    blocked = WHALE_REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED
    for cap in (
        "hyperliquid_api_connection",
        "wallet_monitoring",
        "account_or_portfolio_access",
        "exchange_connection",
        "order_placement",
        "copy_or_follow_whale_execution",
        "whale_alert_automation",
        "paper_or_live_trading",
        "strategy_promotion",
        "downstream_gate_unlock",
    ):
        assert cap in blocked


# --------------------------------------------------------------------------
# Explicit per-feature classification rules
# --------------------------------------------------------------------------

def test_hyperliquid_whale_tracking_is_useful_never_execution():
    r = classify_whale_evidence_claim("Hyperliquid whale tracking")
    assert r["bucket"] == BUCKET_USEFUL_FOR_RESEARCH
    assert r["execution_capable"] is False
    assert "never execution" in r["reason"].lower()


def test_whale_position_observation_needs_confirmation():
    r = classify_whale_evidence_claim("Whale position observation")
    assert r["bucket"] == BUCKET_NEEDS_INDEPENDENT_CONFIRMATION
    assert r["execution_capable"] is False


def test_large_whale_movement_is_risky():
    r = classify_whale_evidence_claim("Large whale movement alert")
    assert r["bucket"] == BUCKET_RISKY_REQUIRES_VALIDATION
    assert r["execution_capable"] is False


def test_whale_offline_study_is_useful_research():
    r = classify_whale_evidence_claim("Offline historical whale evidence study")
    assert r["bucket"] == BUCKET_USEFUL_FOR_RESEARCH
    assert r["execution_capable"] is False


def test_wallet_monitoring_is_blocked():
    r = classify_whale_evidence_claim("Hyperliquid API wallet monitoring")
    assert r["bucket"] == BUCKET_BLOCKED_EXECUTION_FEATURE
    assert r["execution_capable"] is True


def test_copy_whale_execution_is_blocked():
    r = classify_whale_evidence_claim("Copy profitable whale wallets")
    assert r["bucket"] == BUCKET_BLOCKED_EXECUTION_FEATURE
    assert r["execution_capable"] is True


def test_follow_whale_execution_is_blocked():
    r = classify_whale_evidence_claim("Follow whale and mirror trades")
    assert r["bucket"] == BUCKET_BLOCKED_EXECUTION_FEATURE
    assert r["execution_capable"] is True


def test_account_portfolio_access_is_blocked():
    r = classify_whale_evidence_claim("Account and portfolio access")
    assert r["bucket"] == BUCKET_BLOCKED_EXECUTION_FEATURE
    assert r["execution_capable"] is True


def test_exchange_connection_is_blocked():
    r = classify_whale_evidence_claim("Exchange connection")
    assert r["bucket"] == BUCKET_BLOCKED_EXECUTION_FEATURE
    assert r["execution_capable"] is True


def test_whale_alert_automation_is_blocked():
    r = classify_whale_evidence_claim("Live whale alert automation")
    assert r["bucket"] == BUCKET_BLOCKED_EXECUTION_FEATURE
    assert r["execution_capable"] is True


def test_smart_money_certainty_is_marketing():
    r = classify_whale_evidence_claim("Smart money certainty")
    assert r["bucket"] == BUCKET_IGNORE_OR_MARKETING_CLAIM


def test_guaranteed_whale_signal_is_marketing():
    r = classify_whale_evidence_claim("Guaranteed whale signal")
    assert r["bucket"] == BUCKET_IGNORE_OR_MARKETING_CLAIM


# --------------------------------------------------------------------------
# Heuristic + safety override behavior
# --------------------------------------------------------------------------

def test_marketing_claim_is_ignored():
    r = classify_whale_evidence_claim(
        "guaranteed smart money certainty, can't lose"
    )
    assert r["bucket"] == BUCKET_IGNORE_OR_MARKETING_CLAIM


def test_unknown_whale_claim_defaults_to_risky():
    r = classify_whale_evidence_claim("a brand new whale alpha edge idea")
    assert r["bucket"] == BUCKET_RISKY_REQUIRES_VALIDATION


def test_execution_keyword_forces_blocked():
    r = classify_whale_evidence_claim(
        "whale tracker that will place order automatically"
    )
    assert r["bucket"] == BUCKET_BLOCKED_EXECUTION_FEATURE
    assert r["execution_capable"] is True


def test_forbidden_allow_flag_forces_blocked():
    r = classify_whale_evidence_claim(
        {"claim": "whale position observation", "allow_execution": True}
    )
    assert r["bucket"] == BUCKET_BLOCKED_EXECUTION_FEATURE
    assert "allow_execution" in r["requested_forbidden_flags"]


def test_empty_claim_defaults_to_risky():
    r = classify_whale_evidence_claim("")
    assert r["bucket"] == BUCKET_RISKY_REQUIRES_VALIDATION


def test_malformed_claim_never_raises():
    for bad in (None, 123, [], {}, object()):
        r = classify_whale_evidence_claim(bad)
        assert r["bucket"] in WHALE_EVIDENCE_CLASSIFICATION_BUCKETS
        assert r["authorizes_nothing"] is True


def test_every_classified_claim_authorizes_nothing():
    r = classify_whale_evidence_claim("Hyperliquid whale tracking")
    assert r["authorizes_nothing"] is True


def test_canonical_map_covers_named_features():
    for feature_id in (
        "hyperliquid_whale_tracking",
        "whale_position_observation",
        "large_whale_movement_claim",
        "whale_evidence_offline_study",
        "wallet_monitoring",
        "hyperliquid_api_connection",
        "copy_whale_execution",
        "copy_profitable_wallets",
        "whale_alert_automation",
        "account_portfolio_access",
        "exchange_connection",
        "smart_money_certainty_claim",
        "guaranteed_whale_signal",
    ):
        assert feature_id in WHALE_CANONICAL_FEATURE_CLASSIFICATIONS


def test_every_canonical_execution_capable_is_blocked():
    for spec in WHALE_CANONICAL_FEATURE_CLASSIFICATIONS.values():
        if spec["execution_capable"]:
            assert spec["bucket"] == BUCKET_BLOCKED_EXECUTION_FEATURE


# --------------------------------------------------------------------------
# Build / validate
# --------------------------------------------------------------------------

def test_build_default_classifies_eight_source_claims():
    c = build_crypto_d1_hyperliquid_whale_evidence_contract()
    assert len(c["classified_claims"]) == 8
    assert len(c["submitted_claims"]) == 8


def test_build_default_bucket_distribution():
    c = build_crypto_d1_hyperliquid_whale_evidence_contract()
    counts = c["classification_counts"]
    assert counts[BUCKET_USEFUL_FOR_RESEARCH] == 2
    assert counts[BUCKET_NEEDS_INDEPENDENT_CONFIRMATION] == 1
    assert counts[BUCKET_RISKY_REQUIRES_VALIDATION] == 1
    assert counts[BUCKET_BLOCKED_EXECUTION_FEATURE] == 2
    assert counts[BUCKET_IGNORE_OR_MARKETING_CLAIM] == 2


def test_build_is_valid():
    c = build_crypto_d1_hyperliquid_whale_evidence_contract()
    v = validate_crypto_d1_hyperliquid_whale_evidence_contract(c)
    assert v["valid"] is True


def test_build_safety_flags():
    c = build_crypto_d1_hyperliquid_whale_evidence_contract()
    assert c["read_only"] is True
    assert c["executes"] is False
    assert c["authorizes_real_world_action"] is False
    assert c["unlocks_downstream_gate"] is False
    assert c["human_approval_required"] is True


def test_build_requires_independent_confirmation():
    c = build_crypto_d1_hyperliquid_whale_evidence_contract()
    assert c["requires_independent_confirmation"] is True


def test_build_gates_remain_blocked_and_locked():
    c = build_crypto_d1_hyperliquid_whale_evidence_contract()
    assert c["real_data_qa_blocked"] is True
    assert c["baseline_backtest_blocked"] is True
    assert c["paper_trading_gate_locked"] is True
    assert c["micro_live_gate_locked"] is True


def test_build_safety_posture_all_false():
    c = build_crypto_d1_hyperliquid_whale_evidence_contract()
    posture = c["safety_posture"]
    assert len(posture) > 0
    assert all(v is False for v in posture.values())


def test_build_counts_sum_to_claim_total():
    c = build_crypto_d1_hyperliquid_whale_evidence_contract()
    counts = c["classification_counts"]
    assert set(counts.keys()) == set(WHALE_EVIDENCE_CLASSIFICATION_BUCKETS)
    assert sum(counts.values()) == len(c["classified_claims"])


def test_build_custom_claims():
    c = build_crypto_d1_hyperliquid_whale_evidence_contract(
        ["Copy profitable whale wallets", "Hyperliquid whale tracking"]
    )
    buckets = [item["bucket"] for item in c["classified_claims"]]
    assert BUCKET_BLOCKED_EXECUTION_FEATURE in buckets
    assert BUCKET_USEFUL_FOR_RESEARCH in buckets


def test_build_is_deterministic():
    a = build_crypto_d1_hyperliquid_whale_evidence_contract()
    b = build_crypto_d1_hyperliquid_whale_evidence_contract()
    assert a == b


def test_build_returns_isolated_copies():
    a = build_crypto_d1_hyperliquid_whale_evidence_contract()
    a["classified_claims"].append({"bucket": "tampered"})
    a["safety_posture"]["places_order"] = True
    b = build_crypto_d1_hyperliquid_whale_evidence_contract()
    assert len(b["classified_claims"]) == 8
    assert b["safety_posture"]["places_order"] is False


def test_validate_rejects_non_dict():
    v = validate_crypto_d1_hyperliquid_whale_evidence_contract(None)
    assert v["valid"] is False


def test_validate_rejects_executes_true():
    c = build_crypto_d1_hyperliquid_whale_evidence_contract()
    c["executes"] = True
    v = validate_crypto_d1_hyperliquid_whale_evidence_contract(c)
    assert v["valid"] is False


def test_validate_rejects_unlocked_gate():
    c = build_crypto_d1_hyperliquid_whale_evidence_contract()
    c["real_data_qa_blocked"] = False
    v = validate_crypto_d1_hyperliquid_whale_evidence_contract(c)
    assert v["valid"] is False
    assert v["gates_locked"] is False


def test_validate_rejects_confirmation_disabled():
    c = build_crypto_d1_hyperliquid_whale_evidence_contract()
    c["requires_independent_confirmation"] = False
    v = validate_crypto_d1_hyperliquid_whale_evidence_contract(c)
    assert v["valid"] is False
    assert v["confirmation_required"] is False


def test_validate_rejects_execution_capable_in_wrong_bucket():
    c = build_crypto_d1_hyperliquid_whale_evidence_contract()
    c["classified_claims"].append(
        {
            "claim": "tampered",
            "bucket": BUCKET_USEFUL_FOR_RESEARCH,
            "execution_capable": True,
            "authorizes_nothing": True,
        }
    )
    v = validate_crypto_d1_hyperliquid_whale_evidence_contract(c)
    assert v["valid"] is False
    assert v["execution_safe"] is False


def test_forbidden_flag_list_covers_execution_surfaces():
    flags = WHALE_EVIDENCE_FORBIDDEN_ALLOW_FLAGS
    for f in (
        "allow_execution",
        "allow_hyperliquid_api",
        "allow_wallet_monitoring",
        "allow_account_access",
        "allow_exchange_connection",
        "allow_order_placement",
        "allow_copy_whale",
        "allow_whale_alert_automation",
        "allow_downstream_gate_unlock",
    ):
        assert f in flags


# --------------------------------------------------------------------------
# Render
# --------------------------------------------------------------------------

def test_render_is_string_and_mentions_blocked_gates():
    c = build_crypto_d1_hyperliquid_whale_evidence_contract()
    md = render_crypto_d1_hyperliquid_whale_evidence_contract_markdown(c)
    assert isinstance(md, str)
    assert "Whale Evidence" in md
    assert "real_data_qa blocked: True" in md


def test_label_constant():
    assert DEFAULT_WHALE_EVIDENCE_LABEL == (
        "Strategy Factory Crypto-D1 Hyperliquid Whale Evidence Contract"
    )
