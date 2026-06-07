"""Tests for the Crypto-D1 Bitcoin Cycle Timing Evidence Contract (Bundle 64
Block 123). Verifies the read-only conversion of the BTC 364-day / 1064-day
cycle idea into research-only timing evidence: days-since-ATH, distance to the
~364-day cycle-bottom window, previous-duration comparisons, the
early/active/late/expired watch zones, the optional drawdown-from-ATH, and the
caution / accumulation-watch / recovery-watch / no-signal evidence stances. The
contract fetches no BTC data, calls no API, inspects no dataset, authorizes
nothing, and unlocks no gate."""

from __future__ import annotations

from sparta_commander.strategy_factory_crypto_d1_bitcoin_cycle_timing_evidence_contract import (  # noqa: E501
    BITCOIN_CYCLE_TIMING_EVIDENCE_SCHEMA_VERSION,
    DEFAULT_BITCOIN_CYCLE_TIMING_EVIDENCE_LABEL,
    BITCOIN_CYCLE_TIMING_EVIDENCE_STATUS,
    BITCOIN_CYCLE_TIMING_EVIDENCE_MODE,
    BITCOIN_CYCLE_TIMING_EVIDENCE_SAFETY_POSTURE,
    BITCOIN_CYCLE_TIMING_WATCH_ZONES,
    WATCH_ZONE_EARLY,
    WATCH_ZONE_ACTIVE,
    WATCH_ZONE_LATE,
    WATCH_ZONE_EXPIRED,
    WATCH_ZONE_UNDETERMINED,
    BITCOIN_CYCLE_TIMING_EVIDENCE_STANCES,
    STANCE_CAUTION,
    STANCE_ACCUMULATION_WATCH,
    STANCE_RECOVERY_WATCH,
    STANCE_NO_SIGNAL,
    CANONICAL_ATH_TO_BOTTOM_DAYS,
    CANONICAL_BOTTOM_TO_NEXT_ATH_DAYS,
    BITCOIN_CYCLE_TIMING_CORE_RULE,
    BITCOIN_CYCLE_TIMING_EVIDENCE_FORBIDDEN_ALLOW_FLAGS,
    BITCOIN_CYCLE_TIMING_REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED,
    BITCOIN_CYCLE_TIMING_EVIDENCE_NEXT_REQUIRED_ACTION,
    BITCOIN_CYCLE_TIMING_EVIDENCE_CURRENT_STAGE,
    DEFAULT_SAMPLE_OBSERVATION,
    assess_bitcoin_cycle_timing_evidence,
    build_crypto_d1_bitcoin_cycle_timing_evidence_contract,
    validate_crypto_d1_bitcoin_cycle_timing_evidence_contract,
    render_crypto_d1_bitcoin_cycle_timing_evidence_contract_markdown,
)


# --------------------------------------------------------------------------
# Schema / constants
# --------------------------------------------------------------------------

def test_schema_version_is_v1():
    assert BITCOIN_CYCLE_TIMING_EVIDENCE_SCHEMA_VERSION == (
        "strategy_factory_crypto_d1_bitcoin_cycle_timing_evidence_contract.v1"
    )


def test_mode_is_research_only():
    assert BITCOIN_CYCLE_TIMING_EVIDENCE_MODE == "RESEARCH_ONLY"


def test_status_constant():
    assert BITCOIN_CYCLE_TIMING_EVIDENCE_STATUS == (
        "READ_ONLY_CRYPTO_D1_BITCOIN_CYCLE_TIMING_EVIDENCE_CONTRACT"
    )


def test_label_constant():
    assert DEFAULT_BITCOIN_CYCLE_TIMING_EVIDENCE_LABEL == (
        "Strategy Factory Crypto-D1 Bitcoin Cycle Timing Evidence Contract"
    )


def test_core_rule_attention_not_buy():
    assert BITCOIN_CYCLE_TIMING_CORE_RULE == (
        "Cycle timing tells us when to pay attention, not when to buy."
    )


def test_four_watch_zones_plus_undetermined():
    assert BITCOIN_CYCLE_TIMING_WATCH_ZONES == (
        WATCH_ZONE_EARLY,
        WATCH_ZONE_ACTIVE,
        WATCH_ZONE_LATE,
        WATCH_ZONE_EXPIRED,
        WATCH_ZONE_UNDETERMINED,
    )


def test_four_evidence_stances_exact():
    assert BITCOIN_CYCLE_TIMING_EVIDENCE_STANCES == (
        STANCE_CAUTION,
        STANCE_ACCUMULATION_WATCH,
        STANCE_RECOVERY_WATCH,
        STANCE_NO_SIGNAL,
    )


def test_canonical_cycle_constants():
    assert CANONICAL_ATH_TO_BOTTOM_DAYS == 364
    assert CANONICAL_BOTTOM_TO_NEXT_ATH_DAYS == 1064


def test_safety_posture_all_false():
    posture = BITCOIN_CYCLE_TIMING_EVIDENCE_SAFETY_POSTURE
    assert len(posture) > 0
    assert all(v is False for v in posture.values())


def test_next_required_action_is_build_cycle_timing():
    assert BITCOIN_CYCLE_TIMING_EVIDENCE_NEXT_REQUIRED_ACTION == (
        "BUILD_CRYPTO_D1_BITCOIN_CYCLE_TIMING_EVIDENCE_CONTRACT"
    )


def test_current_stage_constant():
    assert BITCOIN_CYCLE_TIMING_EVIDENCE_CURRENT_STAGE == (
        "CRYPTO_D1_BITCOIN_CYCLE_TIMING_EVIDENCE_CONTRACT_REQUIRED"
    )


def test_no_data_fetch_in_safety_posture():
    posture = BITCOIN_CYCLE_TIMING_EVIDENCE_SAFETY_POSTURE
    for key in (
        "fetches_btc_data",
        "calls_api",
        "inspects_dataset",
        "acquires_data",
        "loads_dataset",
        "loads_file",
        "opens_network",
    ):
        assert posture[key] is False


def test_remaining_capabilities_block_data_and_execution_surfaces():
    blocked = BITCOIN_CYCLE_TIMING_REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED
    for cap in (
        "btc_data_fetch",
        "api_call",
        "dataset_inspection",
        "real_data_acquisition",
        "qa_run",
        "baseline_run",
        "backtest_run",
        "simulation_run",
        "order_placement",
        "paper_or_live_trading",
        "strategy_promotion",
        "downstream_gate_unlock",
    ):
        assert cap in blocked


def test_forbidden_flag_list_covers_data_and_execution_surfaces():
    flags = BITCOIN_CYCLE_TIMING_EVIDENCE_FORBIDDEN_ALLOW_FLAGS
    for f in (
        "allow_execution",
        "allow_data_fetch",
        "allow_api_call",
        "allow_dataset_inspection",
        "allow_real_data",
        "allow_qa",
        "allow_backtest",
        "allow_paper_live",
        "allow_broker",
        "allow_order",
        "allow_automation",
        "allow_strategy_promotion",
        "allow_downstream_gate_unlock",
    ):
        assert f in flags


# --------------------------------------------------------------------------
# Watch-zone calculation
# --------------------------------------------------------------------------

def _obs(ath: str, now: str) -> dict:
    return {"latest_btc_ath_date": ath, "current_observation_date": now}


def test_early_zone_before_window_is_caution():
    a = assess_bitcoin_cycle_timing_evidence(
        _obs("2025-01-20", "2025-06-01")
    )
    assert a["watch_zone"] == WATCH_ZONE_EARLY
    assert a["evidence_stance"] == STANCE_CAUTION


def test_active_zone_in_window_is_accumulation_watch():
    a = assess_bitcoin_cycle_timing_evidence(
        _obs("2025-01-20", "2026-01-10")
    )
    assert a["watch_zone"] == WATCH_ZONE_ACTIVE
    assert a["evidence_stance"] == STANCE_ACCUMULATION_WATCH
    assert a["days_since_ath"] == 355


def test_late_zone_just_past_window_is_recovery_watch():
    # 2025-01-20 + ~470 days lands past window_high (424) within late_high (544)
    a = assess_bitcoin_cycle_timing_evidence(
        _obs("2025-01-20", "2026-05-05")
    )
    assert a["watch_zone"] == WATCH_ZONE_LATE
    assert a["evidence_stance"] == STANCE_RECOVERY_WATCH


def test_expired_zone_far_past_window_is_no_signal():
    a = assess_bitcoin_cycle_timing_evidence(
        _obs("2025-01-20", "2027-01-01")
    )
    assert a["watch_zone"] == WATCH_ZONE_EXPIRED
    assert a["evidence_stance"] == STANCE_NO_SIGNAL


def test_missing_dates_is_undetermined_no_signal():
    a = assess_bitcoin_cycle_timing_evidence({})
    assert a["watch_zone"] == WATCH_ZONE_UNDETERMINED
    assert a["evidence_stance"] == STANCE_NO_SIGNAL
    assert a["days_since_ath"] is None


def test_negative_days_since_ath_is_undetermined():
    # observation date BEFORE the ATH -> nonsensical -> undetermined
    a = assess_bitcoin_cycle_timing_evidence(
        _obs("2025-06-01", "2025-01-01")
    )
    assert a["watch_zone"] == WATCH_ZONE_UNDETERMINED


def test_distance_to_bottom_window_center():
    a = assess_bitcoin_cycle_timing_evidence(
        _obs("2025-01-20", "2026-01-10")
    )
    # 364 - 355 = 9 days until the window center
    assert a["distance_to_bottom_window_center_days"] == 9


def test_candidate_bottom_days_from_ath():
    a = assess_bitcoin_cycle_timing_evidence(DEFAULT_SAMPLE_OBSERVATION)
    assert a["candidate_bottom_days_from_ath"] == 364


# --------------------------------------------------------------------------
# Drawdown + duration comparisons
# --------------------------------------------------------------------------

def test_drawdown_from_ath_when_prices_present():
    a = assess_bitcoin_cycle_timing_evidence(DEFAULT_SAMPLE_OBSERVATION)
    assert a["drawdown_from_ath"] is not None
    assert round(a["drawdown_from_ath"], 4) == -0.5596


def test_drawdown_none_when_prices_absent():
    a = assess_bitcoin_cycle_timing_evidence(
        _obs("2025-01-20", "2026-01-10")
    )
    assert a["drawdown_from_ath"] is None


def test_drawdown_none_when_ath_price_zero():
    a = assess_bitcoin_cycle_timing_evidence(
        {
            "latest_btc_ath_date": "2025-01-20",
            "current_observation_date": "2026-01-10",
            "latest_btc_ath_price": 0,
            "current_observed_price": 48000,
        }
    )
    assert a["drawdown_from_ath"] is None


def test_ath_to_bottom_duration_comparison():
    a = assess_bitcoin_cycle_timing_evidence(DEFAULT_SAMPLE_OBSERVATION)
    cmp = a["previous_ath_to_bottom_comparison"]
    assert cmp["sample_count"] == 3
    assert cmp["canonical_days"] == CANONICAL_ATH_TO_BOTTOM_DAYS
    assert cmp["average_days"] == 369.0
    assert cmp["delta_vs_canonical_days"] == 5.0


def test_bottom_to_next_ath_duration_comparison():
    a = assess_bitcoin_cycle_timing_evidence(DEFAULT_SAMPLE_OBSERVATION)
    cmp = a["previous_bottom_to_next_ath_comparison"]
    assert cmp["canonical_days"] == CANONICAL_BOTTOM_TO_NEXT_ATH_DAYS
    assert cmp["sample_count"] == 3


def test_duration_comparison_none_when_absent():
    a = assess_bitcoin_cycle_timing_evidence(
        _obs("2025-01-20", "2026-01-10")
    )
    assert a["previous_ath_to_bottom_comparison"] is None
    assert a["previous_bottom_to_next_ath_comparison"] is None


def test_duration_comparison_ignores_non_numeric_samples():
    a = assess_bitcoin_cycle_timing_evidence(
        {
            "latest_btc_ath_date": "2025-01-20",
            "current_observation_date": "2026-01-10",
            "previous_ath_to_bottom_durations": [364, "bad", None, 386],
        }
    )
    cmp = a["previous_ath_to_bottom_comparison"]
    assert cmp["sample_count"] == 2
    assert cmp["average_days"] == 375.0


# --------------------------------------------------------------------------
# Safety / robustness
# --------------------------------------------------------------------------

def test_every_assessment_authorizes_nothing():
    a = assess_bitcoin_cycle_timing_evidence(DEFAULT_SAMPLE_OBSERVATION)
    assert a["authorizes_nothing"] is True


def test_assessment_stance_always_in_enum():
    for obs in (
        {},
        _obs("2025-01-20", "2025-06-01"),
        _obs("2025-01-20", "2026-01-10"),
        _obs("2025-01-20", "2027-01-01"),
        DEFAULT_SAMPLE_OBSERVATION,
    ):
        a = assess_bitcoin_cycle_timing_evidence(obs)
        assert a["evidence_stance"] in BITCOIN_CYCLE_TIMING_EVIDENCE_STANCES
        assert a["watch_zone"] in BITCOIN_CYCLE_TIMING_WATCH_ZONES


def test_malformed_observation_never_raises():
    for bad in (None, 123, [], "str", object()):
        a = assess_bitcoin_cycle_timing_evidence(bad)
        assert a["watch_zone"] in BITCOIN_CYCLE_TIMING_WATCH_ZONES
        assert a["authorizes_nothing"] is True


def test_malformed_dates_degrade_to_undetermined():
    a = assess_bitcoin_cycle_timing_evidence(
        {"latest_btc_ath_date": "not-a-date",
         "current_observation_date": "2026/01/10"}
    )
    assert a["watch_zone"] == WATCH_ZONE_UNDETERMINED


def test_forbidden_allow_flag_recorded_never_honored():
    a = assess_bitcoin_cycle_timing_evidence(
        {
            "latest_btc_ath_date": "2025-01-20",
            "current_observation_date": "2026-01-10",
            "allow_execution": True,
            "fetches_btc_data": True,
        }
    )
    assert "allow_execution" in a["requested_forbidden_flags"]
    assert "fetches_btc_data" in a["requested_forbidden_flags"]
    assert a["authorizes_nothing"] is True


# --------------------------------------------------------------------------
# Build / validate
# --------------------------------------------------------------------------

def test_build_default_is_active_accumulation_watch():
    c = build_crypto_d1_bitcoin_cycle_timing_evidence_contract()
    assert c["watch_zone"] == WATCH_ZONE_ACTIVE
    assert c["evidence_stance"] == STANCE_ACCUMULATION_WATCH


def test_build_is_valid():
    c = build_crypto_d1_bitcoin_cycle_timing_evidence_contract()
    v = validate_crypto_d1_bitcoin_cycle_timing_evidence_contract(c)
    assert v["valid"] is True


def test_build_core_rule_present():
    c = build_crypto_d1_bitcoin_cycle_timing_evidence_contract()
    assert c["core_rule"] == BITCOIN_CYCLE_TIMING_CORE_RULE


def test_build_safety_flags():
    c = build_crypto_d1_bitcoin_cycle_timing_evidence_contract()
    assert c["read_only"] is True
    assert c["executes"] is False
    assert c["authorizes_real_world_action"] is False
    assert c["unlocks_downstream_gate"] is False
    assert c["human_approval_required"] is True


def test_build_requires_independent_confirmation():
    c = build_crypto_d1_bitcoin_cycle_timing_evidence_contract()
    assert c["requires_independent_confirmation"] is True


def test_build_gates_remain_blocked_and_locked():
    c = build_crypto_d1_bitcoin_cycle_timing_evidence_contract()
    assert c["real_data_qa_blocked"] is True
    assert c["baseline_backtest_blocked"] is True
    assert c["paper_trading_gate_locked"] is True
    assert c["micro_live_gate_locked"] is True


def test_build_safety_posture_all_false():
    c = build_crypto_d1_bitcoin_cycle_timing_evidence_contract()
    posture = c["safety_posture"]
    assert len(posture) > 0
    assert all(v is False for v in posture.values())


def test_build_custom_observation_early_zone():
    c = build_crypto_d1_bitcoin_cycle_timing_evidence_contract(
        _obs("2025-01-20", "2025-06-01")
    )
    assert c["watch_zone"] == WATCH_ZONE_EARLY
    assert c["evidence_stance"] == STANCE_CAUTION
    v = validate_crypto_d1_bitcoin_cycle_timing_evidence_contract(c)
    assert v["valid"] is True


def test_build_is_deterministic():
    a = build_crypto_d1_bitcoin_cycle_timing_evidence_contract()
    b = build_crypto_d1_bitcoin_cycle_timing_evidence_contract()
    assert a == b


def test_build_returns_isolated_copies():
    a = build_crypto_d1_bitcoin_cycle_timing_evidence_contract()
    a["operator_notes"].append("tampered")
    a["safety_posture"]["places_order"] = True
    a["observation"]["latest_btc_ath_date"] = "1999-01-01"
    b = build_crypto_d1_bitcoin_cycle_timing_evidence_contract()
    assert "tampered" not in b["operator_notes"]
    assert b["safety_posture"]["places_order"] is False
    assert b["observation"]["latest_btc_ath_date"] == "2025-01-20"


def test_build_observation_echoes_only_known_fields():
    c = build_crypto_d1_bitcoin_cycle_timing_evidence_contract(
        {
            "latest_btc_ath_date": "2025-01-20",
            "current_observation_date": "2026-01-10",
            "allow_execution": True,
            "unknown_extra": "ignored",
        }
    )
    assert "allow_execution" not in c["observation"]
    assert "unknown_extra" not in c["observation"]
    assert c["observation"]["latest_btc_ath_date"] == "2025-01-20"


def test_validate_rejects_non_dict():
    v = validate_crypto_d1_bitcoin_cycle_timing_evidence_contract(None)
    assert v["valid"] is False


def test_validate_rejects_executes_true():
    c = build_crypto_d1_bitcoin_cycle_timing_evidence_contract()
    c["executes"] = True
    v = validate_crypto_d1_bitcoin_cycle_timing_evidence_contract(c)
    assert v["valid"] is False


def test_validate_rejects_unlocked_gate():
    c = build_crypto_d1_bitcoin_cycle_timing_evidence_contract()
    c["real_data_qa_blocked"] = False
    v = validate_crypto_d1_bitcoin_cycle_timing_evidence_contract(c)
    assert v["valid"] is False
    assert v["gates_locked"] is False


def test_validate_rejects_confirmation_disabled():
    c = build_crypto_d1_bitcoin_cycle_timing_evidence_contract()
    c["requires_independent_confirmation"] = False
    v = validate_crypto_d1_bitcoin_cycle_timing_evidence_contract(c)
    assert v["valid"] is False
    assert v["confirmation_required"] is False


def test_validate_rejects_bad_core_rule():
    c = build_crypto_d1_bitcoin_cycle_timing_evidence_contract()
    c["core_rule"] = "when to buy"
    v = validate_crypto_d1_bitcoin_cycle_timing_evidence_contract(c)
    assert v["valid"] is False
    assert v["core_rule_ok"] is False


def test_validate_rejects_unknown_stance():
    c = build_crypto_d1_bitcoin_cycle_timing_evidence_contract()
    c["evidence_stance"] = "buy-now"
    v = validate_crypto_d1_bitcoin_cycle_timing_evidence_contract(c)
    assert v["valid"] is False
    assert v["stance_ok"] is False


def test_validate_rejects_tainted_safety_posture():
    c = build_crypto_d1_bitcoin_cycle_timing_evidence_contract()
    c["safety_posture"]["places_order"] = True
    v = validate_crypto_d1_bitcoin_cycle_timing_evidence_contract(c)
    assert v["valid"] is False
    assert v["safety_all_false"] is False


# --------------------------------------------------------------------------
# Render
# --------------------------------------------------------------------------

def test_render_is_string_and_mentions_core_rule_and_gates():
    c = build_crypto_d1_bitcoin_cycle_timing_evidence_contract()
    md = render_crypto_d1_bitcoin_cycle_timing_evidence_contract_markdown(c)
    assert isinstance(md, str)
    assert "Bitcoin Cycle Timing Evidence" in md
    assert "pay attention" in md
    assert "real_data_qa blocked: True" in md
    assert "Watch zone: active" in md


def test_render_handles_non_dict():
    md = render_crypto_d1_bitcoin_cycle_timing_evidence_contract_markdown(None)
    assert isinstance(md, str)
