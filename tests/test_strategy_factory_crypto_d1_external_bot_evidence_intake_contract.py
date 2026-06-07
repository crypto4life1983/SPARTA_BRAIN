"""Tests for the Crypto-D1 External Bot Evidence Intake Contract (Bundle 61
Block 117). Verifies the read-only classification of external AI trading bot /
video / tool claims into observation-only evidence buckets, the explicit
per-feature stances, the execution-safety override, and the all-false safety
posture. The contract authorizes nothing and unlocks no gate."""

from __future__ import annotations

from sparta_commander.strategy_factory_crypto_d1_external_bot_evidence_intake_contract import (  # noqa: E501
    EXTERNAL_BOT_EVIDENCE_INTAKE_SCHEMA_VERSION,
    DEFAULT_EXTERNAL_BOT_EVIDENCE_INTAKE_LABEL,
    EXTERNAL_BOT_EVIDENCE_INTAKE_MODE,
    EXTERNAL_BOT_EVIDENCE_INTAKE_SAFETY_POSTURE,
    EVIDENCE_CLASSIFICATION_BUCKETS,
    BUCKET_USEFUL_FOR_RESEARCH,
    BUCKET_RISKY_REQUIRES_VALIDATION,
    BUCKET_BLOCKED_EXECUTION_FEATURE,
    BUCKET_DASHBOARD_OR_BRIEF_CANDIDATE,
    BUCKET_IGNORE_OR_MARKETING_CLAIM,
    CANONICAL_FEATURE_CLASSIFICATIONS,
    EXTERNAL_BOT_EVIDENCE_INTAKE_FORBIDDEN_ALLOW_FLAGS,
    REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED,
    EXTERNAL_BOT_EVIDENCE_INTAKE_NEXT_REQUIRED_ACTION,
    EXTERNAL_BOT_EVIDENCE_INTAKE_CURRENT_STAGE,
    classify_external_bot_evidence_claim,
    build_crypto_d1_external_bot_evidence_intake_contract,
    validate_crypto_d1_external_bot_evidence_intake_contract,
    render_crypto_d1_external_bot_evidence_intake_contract_markdown,
)


# --------------------------------------------------------------------------
# Schema / constants
# --------------------------------------------------------------------------

def test_schema_version_is_v1():
    assert EXTERNAL_BOT_EVIDENCE_INTAKE_SCHEMA_VERSION == (
        "strategy_factory_crypto_d1_external_bot_evidence_intake_contract.v1"
    )


def test_mode_is_research_only():
    assert EXTERNAL_BOT_EVIDENCE_INTAKE_MODE == "RESEARCH_ONLY"


def test_five_buckets_exact():
    assert EVIDENCE_CLASSIFICATION_BUCKETS == (
        BUCKET_USEFUL_FOR_RESEARCH,
        BUCKET_RISKY_REQUIRES_VALIDATION,
        BUCKET_BLOCKED_EXECUTION_FEATURE,
        BUCKET_DASHBOARD_OR_BRIEF_CANDIDATE,
        BUCKET_IGNORE_OR_MARKETING_CLAIM,
    )


def test_safety_posture_all_false():
    posture = EXTERNAL_BOT_EVIDENCE_INTAKE_SAFETY_POSTURE
    assert len(posture) > 0
    assert all(v is False for v in posture.values())


def test_next_required_action_is_build_intake():
    assert EXTERNAL_BOT_EVIDENCE_INTAKE_NEXT_REQUIRED_ACTION == (
        "BUILD_CRYPTO_D1_STRATEGY_CANDIDATE_EXTERNAL_BOT_EVIDENCE_INTAKE_"
        "CONTRACT"
    )


def test_current_stage_constant():
    assert EXTERNAL_BOT_EVIDENCE_INTAKE_CURRENT_STAGE == (
        "CRYPTO_D1_STRATEGY_CANDIDATE_EXTERNAL_BOT_EVIDENCE_INTAKE_CONTRACT_"
        "REQUIRED"
    )


def test_remaining_capabilities_block_execution_surfaces():
    blocked = REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED
    for cap in (
        "order_placement",
        "broker_or_exchange_connection",
        "telegram_trade_command",
        "tradingview_execution_webhook",
        "portfolio_account_control",
        "live_strategy_deployment",
        "cloud_bot_operation",
        "paper_or_live_trading",
        "strategy_promotion",
        "downstream_gate_unlock",
    ):
        assert cap in blocked


# --------------------------------------------------------------------------
# Explicit per-feature classification rules
# --------------------------------------------------------------------------

def test_hyperliquid_whale_is_useful_research_never_execution():
    r = classify_external_bot_evidence_claim("Hyperliquid whale tracking")
    assert r["bucket"] == BUCKET_USEFUL_FOR_RESEARCH
    assert r["execution_capable"] is False
    assert "never execution" in r["reason"].lower()


def test_funding_rate_is_risky_not_free_money():
    r = classify_external_bot_evidence_claim("Funding-rate scanner")
    assert r["bucket"] == BUCKET_RISKY_REQUIRES_VALIDATION
    assert "free money" in r["reason"].lower()


def test_telegram_status_is_dashboard_candidate():
    r = classify_external_bot_evidence_claim("Telegram command assistant")
    assert r["bucket"] == BUCKET_DASHBOARD_OR_BRIEF_CANDIDATE
    assert r["execution_capable"] is False


def test_telegram_trade_command_is_blocked_execution():
    r = classify_external_bot_evidence_claim("Telegram trade command")
    assert r["bucket"] == BUCKET_BLOCKED_EXECUTION_FEATURE
    assert r["execution_capable"] is True


def test_tradingview_signal_logging_is_risky():
    r = classify_external_bot_evidence_claim("TradingView webhooks")
    assert r["bucket"] == BUCKET_RISKY_REQUIRES_VALIDATION


def test_tradingview_execution_webhook_is_blocked():
    r = classify_external_bot_evidence_claim("TradingView execution webhook")
    assert r["bucket"] == BUCKET_BLOCKED_EXECUTION_FEATURE
    assert r["execution_capable"] is True


def test_daily_alpha_brief_is_dashboard_candidate():
    r = classify_external_bot_evidence_claim("Daily alpha brief")
    assert r["bucket"] == BUCKET_DASHBOARD_OR_BRIEF_CANDIDATE


def test_portfolio_dashboard_is_dashboard_candidate():
    r = classify_external_bot_evidence_claim("Portfolio dashboard")
    assert r["bucket"] == BUCKET_DASHBOARD_OR_BRIEF_CANDIDATE
    assert r["execution_capable"] is False


def test_portfolio_account_control_is_blocked():
    r = classify_external_bot_evidence_claim("Portfolio account control")
    assert r["bucket"] == BUCKET_BLOCKED_EXECUTION_FEATURE
    assert r["execution_capable"] is True


def test_pine_script_generation_is_useful_research():
    r = classify_external_bot_evidence_claim(
        "Pine Script generation and debugging"
    )
    assert r["bucket"] == BUCKET_USEFUL_FOR_RESEARCH
    assert r["execution_capable"] is False


def test_pine_script_live_deployment_is_blocked():
    r = classify_external_bot_evidence_claim("deploy pine script live")
    assert r["bucket"] == BUCKET_BLOCKED_EXECUTION_FEATURE


def test_cloud_bot_operation_is_blocked():
    r = classify_external_bot_evidence_claim("Cloud bot operation")
    assert r["bucket"] == BUCKET_BLOCKED_EXECUTION_FEATURE
    assert r["execution_capable"] is True


def test_cloud_bot_offline_packaging_is_useful_research():
    r = classify_external_bot_evidence_claim(
        "cloud bot offline research packaging"
    )
    assert r["bucket"] == BUCKET_USEFUL_FOR_RESEARCH


def test_support_resistance_is_useful_research():
    r = classify_external_bot_evidence_claim(
        "Support/resistance chart analysis"
    )
    assert r["bucket"] == BUCKET_USEFUL_FOR_RESEARCH
    assert "validation" in r["reason"].lower()


# --------------------------------------------------------------------------
# Heuristic + safety override behavior
# --------------------------------------------------------------------------

def test_marketing_claim_is_ignored():
    r = classify_external_bot_evidence_claim(
        "guaranteed 100x free money, can't lose"
    )
    assert r["bucket"] == BUCKET_IGNORE_OR_MARKETING_CLAIM


def test_unknown_attractive_claim_defaults_to_risky():
    r = classify_external_bot_evidence_claim("a brand new alpha edge idea")
    assert r["bucket"] == BUCKET_RISKY_REQUIRES_VALIDATION


def test_execution_keyword_forces_blocked():
    r = classify_external_bot_evidence_claim(
        "scanner that will place order automatically"
    )
    assert r["bucket"] == BUCKET_BLOCKED_EXECUTION_FEATURE
    assert r["execution_capable"] is True


def test_forbidden_allow_flag_forces_blocked():
    r = classify_external_bot_evidence_claim(
        {"claim": "daily alpha brief", "allow_execution": True}
    )
    assert r["bucket"] == BUCKET_BLOCKED_EXECUTION_FEATURE
    assert r["requested_forbidden_flags"] == ("allow_execution", "executes") or (
        "allow_execution" in r["requested_forbidden_flags"]
    )


def test_empty_claim_defaults_to_risky():
    r = classify_external_bot_evidence_claim("")
    assert r["bucket"] == BUCKET_RISKY_REQUIRES_VALIDATION


def test_malformed_claim_never_raises():
    for bad in (None, 123, [], {}, object()):
        r = classify_external_bot_evidence_claim(bad)
        assert r["bucket"] in EVIDENCE_CLASSIFICATION_BUCKETS
        assert r["authorizes_nothing"] is True


def test_every_classified_claim_authorizes_nothing():
    r = classify_external_bot_evidence_claim("Hyperliquid whale tracking")
    assert r["authorizes_nothing"] is True


def test_canonical_map_covers_nine_named_features():
    for feature_id in (
        "hyperliquid_whale_tracking",
        "funding_rate_scanning",
        "telegram_command_status_interface",
        "tradingview_signal_ingestion_logging",
        "daily_alpha_brief",
        "portfolio_dashboard",
        "pine_script_generation_debugging",
        "cloud_bot_operation",
        "support_resistance_chart_analysis",
    ):
        assert feature_id in CANONICAL_FEATURE_CLASSIFICATIONS


def test_every_canonical_execution_capable_is_blocked():
    for spec in CANONICAL_FEATURE_CLASSIFICATIONS.values():
        if spec["execution_capable"]:
            assert spec["bucket"] == BUCKET_BLOCKED_EXECUTION_FEATURE


# --------------------------------------------------------------------------
# Build / validate
# --------------------------------------------------------------------------

def test_build_default_classifies_nine_source_claims():
    c = build_crypto_d1_external_bot_evidence_intake_contract()
    assert len(c["classified_claims"]) == 9
    assert len(c["submitted_claims"]) == 9


def test_build_is_valid():
    c = build_crypto_d1_external_bot_evidence_intake_contract()
    v = validate_crypto_d1_external_bot_evidence_intake_contract(c)
    assert v["valid"] is True


def test_build_safety_flags():
    c = build_crypto_d1_external_bot_evidence_intake_contract()
    assert c["read_only"] is True
    assert c["executes"] is False
    assert c["authorizes_real_world_action"] is False
    assert c["unlocks_downstream_gate"] is False
    assert c["human_approval_required"] is True


def test_build_gates_remain_blocked_and_locked():
    c = build_crypto_d1_external_bot_evidence_intake_contract()
    assert c["real_data_qa_blocked"] is True
    assert c["baseline_backtest_blocked"] is True
    assert c["paper_trading_gate_locked"] is True
    assert c["micro_live_gate_locked"] is True


def test_build_safety_posture_all_false():
    c = build_crypto_d1_external_bot_evidence_intake_contract()
    posture = c["safety_posture"]
    assert len(posture) > 0
    assert all(v is False for v in posture.values())


def test_build_counts_sum_to_claim_total():
    c = build_crypto_d1_external_bot_evidence_intake_contract()
    counts = c["classification_counts"]
    assert set(counts.keys()) == set(EVIDENCE_CLASSIFICATION_BUCKETS)
    assert sum(counts.values()) == len(c["classified_claims"])


def test_build_custom_claims():
    c = build_crypto_d1_external_bot_evidence_intake_contract(
        ["Telegram trade command", "Support/resistance chart analysis"]
    )
    buckets = [item["bucket"] for item in c["classified_claims"]]
    assert BUCKET_BLOCKED_EXECUTION_FEATURE in buckets
    assert BUCKET_USEFUL_FOR_RESEARCH in buckets


def test_build_is_deterministic():
    a = build_crypto_d1_external_bot_evidence_intake_contract()
    b = build_crypto_d1_external_bot_evidence_intake_contract()
    assert a == b


def test_build_returns_isolated_copies():
    a = build_crypto_d1_external_bot_evidence_intake_contract()
    a["classified_claims"].append({"bucket": "tampered"})
    a["safety_posture"]["places_order"] = True
    b = build_crypto_d1_external_bot_evidence_intake_contract()
    assert len(b["classified_claims"]) == 9
    assert b["safety_posture"]["places_order"] is False


def test_validate_rejects_non_dict():
    v = validate_crypto_d1_external_bot_evidence_intake_contract(None)
    assert v["valid"] is False


def test_validate_rejects_executes_true():
    c = build_crypto_d1_external_bot_evidence_intake_contract()
    c["executes"] = True
    v = validate_crypto_d1_external_bot_evidence_intake_contract(c)
    assert v["valid"] is False


def test_validate_rejects_unlocked_gate():
    c = build_crypto_d1_external_bot_evidence_intake_contract()
    c["real_data_qa_blocked"] = False
    v = validate_crypto_d1_external_bot_evidence_intake_contract(c)
    assert v["valid"] is False
    assert v["gates_locked"] is False


def test_validate_rejects_execution_capable_in_wrong_bucket():
    c = build_crypto_d1_external_bot_evidence_intake_contract()
    c["classified_claims"].append(
        {
            "claim": "tampered",
            "bucket": BUCKET_USEFUL_FOR_RESEARCH,
            "execution_capable": True,
            "authorizes_nothing": True,
        }
    )
    v = validate_crypto_d1_external_bot_evidence_intake_contract(c)
    assert v["valid"] is False
    assert v["execution_safe"] is False


def test_forbidden_flag_list_covers_execution_surfaces():
    flags = EXTERNAL_BOT_EVIDENCE_INTAKE_FORBIDDEN_ALLOW_FLAGS
    for f in (
        "allow_execution",
        "allow_order_placement",
        "allow_broker_exchange",
        "allow_telegram_trade_command",
        "allow_tradingview_execution_webhook",
        "allow_account_control",
        "allow_live_deployment",
        "allow_downstream_gate_unlock",
    ):
        assert f in flags


# --------------------------------------------------------------------------
# Render
# --------------------------------------------------------------------------

def test_render_is_string_and_mentions_blocked_gates():
    c = build_crypto_d1_external_bot_evidence_intake_contract()
    md = render_crypto_d1_external_bot_evidence_intake_contract_markdown(c)
    assert isinstance(md, str)
    assert "External Bot Evidence Intake" in md
    assert "real_data_qa blocked: True" in md


def test_label_constant():
    assert DEFAULT_EXTERNAL_BOT_EVIDENCE_INTAKE_LABEL == (
        "Strategy Factory Crypto-D1 External Bot Evidence Intake Contract"
    )
