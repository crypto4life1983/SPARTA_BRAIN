"""Tests for the Crypto-D1 Strategy Candidate Family Selection Contract (Block
99).

The module is a PURE, stdlib-only, read-only *paper contract* that VALIDATES
whether a proposed family selection follows the Crypto-D1 Strategy Candidate
Protocol Contract (Block 97). It evaluates the SHAPE of a proposed selection
only -- it acquires/fetches/inspects/loads no data, runs no QA/baseline/backtest/
simulation, produces no trade signal, reaches no broker/exchange/order/account/
API, trades no paper/live, selects no live strategy, triggers no automation, and
writes nothing.

Coverage:
- pure stdlib import-root audit + forbidden-surface audit
- exported constants / schema version / verdict + state / safety posture
- activation rule: AWAIT unless upstream protocol-contract signal is READY for
  the family-selection gate (active + READY verdict + family-selection next_gate
  + RESEARCH_ONLY + read_only + non-executing)
- READY only for a fully-specified research-only BTC/ETH/SOL spot D1 selection
  with all four families selected or explicitly parked and every real-world
  capability blocked
- READY when one family is explicitly parked and the rest selected
- NEEDS_MORE_INFO for empty / incomplete selections (missing field, missing
  affirmation, missing universe member, an uncovered family)
- REJECTED for any forbidden allow flag, relaxed affirmation, disallowed mode,
  off-scope market type / timeframe, non-core asset, unknown selected family,
  single-favorite family masquerading as a comparison, regime-only selection,
  automated decider, granted authority
- PARKED when an operator explicitly parks/defers the whole selection
- verdict precedence: REJECTED > PARKED > NEEDS_MORE_INFO > READY; AWAIT first
- verdict -> next_gate mapping in build_*
- validation valid for a real contract, invalid when tampered
- deterministic repeated calls; mutation-isolated copies
- read_only True, executes False, human_approval_required True, auth all False
- scope mirrors the protocol contract (universe/market/timeframe/families)
- render markdown is non-empty and names key sections
- commander_2_safety allowlist includes the new module + test paths
"""

from __future__ import annotations

import ast
import pathlib

from sparta_commander.strategy_factory_crypto_d1_strategy_candidate_family_selection_contract import (  # noqa: E501
    STRATEGY_CANDIDATE_FAMILY_SELECTION_SCHEMA_VERSION,
    DEFAULT_STRATEGY_CANDIDATE_FAMILY_SELECTION_LABEL,
    STRATEGY_CANDIDATE_FAMILY_SELECTION_STATUS,
    STRATEGY_CANDIDATE_FAMILY_SELECTION_SAFETY_POSTURE,
    STRATEGY_CANDIDATE_FAMILY_SELECTION_STATE_ACTIVE,
    STRATEGY_CANDIDATE_FAMILY_SELECTION_STATE_BLOCKED,
    STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_READY,
    STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_NEEDS_MORE_INFO,
    STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_REJECTED,
    STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_PARKED,
    STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_AWAIT,
    ALLOWED_STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICTS,
    UPSTREAM_REQUIRED_PROTOCOL_CONTRACT_VERDICT,
    UPSTREAM_REQUIRED_PROTOCOL_CONTRACT_NEXT_GATE,
    UPSTREAM_REQUIRED_PROTOCOL_CONTRACT_MODE,
    STRATEGY_CANDIDATE_FAMILY_SELECTION_NEXT_REQUIRED_ACTION,
    STRATEGY_CANDIDATE_FAMILY_SELECTION_CURRENT_STAGE,
    NEXT_GATE_CRYPTO_D1_STRATEGY_CANDIDATE_FAMILY_SELECTION_READY,
    NEXT_GATE_CRYPTO_D1_STRATEGY_CANDIDATE_FAMILY_SELECTION_FIX_REQUIRED,
    NEXT_GATE_CRYPTO_D1_STRATEGY_CANDIDATE_FAMILY_SELECTION_PARKED,
    NEXT_GATE_CRYPTO_D1_STRATEGY_CANDIDATE_FAMILY_SELECTION_REJECTED,
    NEXT_GATE_AWAIT_CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_CONTRACT,
    REQUIRED_RESEARCH_UNIVERSE,
    REQUIRED_MARKET_TYPE,
    REQUIRED_TIMEFRAME,
    REQUIRED_STRATEGY_FAMILIES,
    REQUIRED_STRATEGY_CANDIDATE_FAMILY_SELECTION_FIELDS,
    STRATEGY_CANDIDATE_FAMILY_SELECTION_REQUIRED_TEXT_FIELDS,
    STRATEGY_CANDIDATE_FAMILY_SELECTION_REQUIRED_AFFIRMATIONS,
    STRATEGY_CANDIDATE_FAMILY_SELECTION_FORBIDDEN_ALLOW_FLAGS,
    ALLOWED_STRATEGY_CANDIDATE_FAMILY_SELECTION_MODES,
    AUTOMATED_APPROVAL_MARKERS,
    REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED,
    evaluate_crypto_d1_strategy_candidate_family_selection,
    build_crypto_d1_strategy_candidate_family_selection_contract,
    validate_crypto_d1_strategy_candidate_family_selection_contract,
    render_crypto_d1_strategy_candidate_family_selection_contract_markdown,
)

_MODPATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "sparta_commander"
    / "strategy_factory_crypto_d1_strategy_candidate_family_selection_contract.py"  # noqa: E501
)
_SAFETY_PATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "sparta_commander"
    / "commander_2_safety.py"
)

_EXPECTED_FAMILIES = (
    "MOMENTUM_TREND_CONTINUATION",
    "BREAKOUT_DONCHIAN_VOLATILITY_EXPANSION",
    "PULLBACK_MEAN_REVERSION_AFTER_STRONG_TREND",
    "REGIME_FILTER_LAYER",
)

_AUTH_FLAGS = (
    "approved_for_research",
    "execution_authorized",
    "paper_trading_authorized",
    "live_trading_authorized",
    "data_fetch_authorized",
    "backtest_authorized",
    "promotion_authorized",
)


def _valid_packet() -> dict:
    """A fully-specified, safe, research-only family-selection packet with all
    four families selected."""
    packet: dict = {}
    for key in STRATEGY_CANDIDATE_FAMILY_SELECTION_REQUIRED_TEXT_FIELDS:
        packet[key] = f"value-for-{key}"
    packet["universe"] = list(REQUIRED_RESEARCH_UNIVERSE)
    packet["market_type"] = "SPOT"
    packet["timeframe"] = "D1"
    packet["selection_mode"] = "RESEARCH_ONLY"
    packet["selected_families"] = list(REQUIRED_STRATEGY_FAMILIES)
    packet["parked_families"] = []
    for flag in STRATEGY_CANDIDATE_FAMILY_SELECTION_REQUIRED_AFFIRMATIONS:
        packet[flag] = True
    return packet


def _active_signal() -> dict:
    """An upstream protocol-contract signal that activates this contract."""
    return {
        "strategy_candidate_protocol_contract_active": True,
        "strategy_candidate_protocol_verdict": (
            UPSTREAM_REQUIRED_PROTOCOL_CONTRACT_VERDICT
        ),
        "next_gate": UPSTREAM_REQUIRED_PROTOCOL_CONTRACT_NEXT_GATE,
        "mode": UPSTREAM_REQUIRED_PROTOCOL_CONTRACT_MODE,
        "read_only": True,
        "executes": False,
    }


# --- 1: schema / identity ---------------------------------------------------

def test_01_schema_version_value():
    assert STRATEGY_CANDIDATE_FAMILY_SELECTION_SCHEMA_VERSION == (
        "strategy_factory_crypto_d1_strategy_candidate_family_selection_"
        "contract.v1"
    )


def test_02_label_and_status_nonempty():
    assert DEFAULT_STRATEGY_CANDIDATE_FAMILY_SELECTION_LABEL
    assert STRATEGY_CANDIDATE_FAMILY_SELECTION_STATUS.startswith("READ_ONLY")


def test_03_states_distinct():
    assert (
        STRATEGY_CANDIDATE_FAMILY_SELECTION_STATE_ACTIVE
        != STRATEGY_CANDIDATE_FAMILY_SELECTION_STATE_BLOCKED
    )


def test_04_allowed_verdicts_exact():
    assert ALLOWED_STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICTS == (
        STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_READY,
        STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_NEEDS_MORE_INFO,
        STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_REJECTED,
        STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_PARKED,
        STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_AWAIT,
    )


def test_05_await_verdict_value():
    assert STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_AWAIT == (
        "AWAIT_CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_CONTRACT"
    )


def test_06_verdict_values_are_family_selection_named():
    assert STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_READY == (
        "STRATEGY_CANDIDATE_FAMILY_SELECTION_READY"
    )
    assert STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_NEEDS_MORE_INFO == (
        "STRATEGY_CANDIDATE_FAMILY_SELECTION_NEEDS_MORE_INFO"
    )
    assert STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_REJECTED == (
        "STRATEGY_CANDIDATE_FAMILY_SELECTION_REJECTED"
    )
    assert STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_PARKED == (
        "STRATEGY_CANDIDATE_FAMILY_SELECTION_PARKED"
    )


# --- 2: upstream / scope mirrors the protocol contract ----------------------

def test_07_upstream_required_verdict_is_protocol_ready():
    assert UPSTREAM_REQUIRED_PROTOCOL_CONTRACT_VERDICT == (
        "STRATEGY_CANDIDATE_PROTOCOL_READY"
    )


def test_08_upstream_required_next_gate():
    assert UPSTREAM_REQUIRED_PROTOCOL_CONTRACT_NEXT_GATE == (
        "CRYPTO_D1_STRATEGY_CANDIDATE_FAMILY_SELECTION_CONTRACT_REQUIRED"
    )


def test_09_upstream_required_mode_research_only():
    assert UPSTREAM_REQUIRED_PROTOCOL_CONTRACT_MODE == "RESEARCH_ONLY"


def test_10_required_universe_btc_eth_sol():
    assert REQUIRED_RESEARCH_UNIVERSE == ("BTC", "ETH", "SOL")


def test_11_required_market_spot_only():
    assert REQUIRED_MARKET_TYPE == "SPOT"


def test_12_required_timeframe_d1_only():
    assert REQUIRED_TIMEFRAME == "D1"


def test_13_required_families_all_four():
    assert REQUIRED_STRATEGY_FAMILIES == _EXPECTED_FAMILIES


def test_14_required_fields_text_plus_affirmations():
    assert REQUIRED_STRATEGY_CANDIDATE_FAMILY_SELECTION_FIELDS == (
        STRATEGY_CANDIDATE_FAMILY_SELECTION_REQUIRED_TEXT_FIELDS
        + STRATEGY_CANDIDATE_FAMILY_SELECTION_REQUIRED_AFFIRMATIONS
    )


def test_15_next_action_and_stage_values():
    assert STRATEGY_CANDIDATE_FAMILY_SELECTION_NEXT_REQUIRED_ACTION == (
        "BUILD_CRYPTO_D1_STRATEGY_CANDIDATE_FAMILY_SELECTION_CONTRACT"
    )
    assert STRATEGY_CANDIDATE_FAMILY_SELECTION_CURRENT_STAGE == (
        "CRYPTO_D1_STRATEGY_CANDIDATE_FAMILY_SELECTION_CONTRACT_REQUIRED"
    )


# --- 3: activation rule (AWAIT) ---------------------------------------------

def test_16_await_on_missing_signal():
    c = build_crypto_d1_strategy_candidate_family_selection_contract(None, None)
    assert c["strategy_candidate_family_selection_verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_AWAIT
    )
    assert c[
        "crypto_d1_strategy_candidate_family_selection_contract_active"
    ] is False


def test_17_await_on_empty_signal():
    c = build_crypto_d1_strategy_candidate_family_selection_contract(
        {}, _valid_packet()
    )
    assert c["strategy_candidate_family_selection_verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_AWAIT
    )


def test_18_await_on_inactive_protocol_contract():
    sig = _active_signal()
    sig["strategy_candidate_protocol_contract_active"] = False
    c = build_crypto_d1_strategy_candidate_family_selection_contract(
        sig, _valid_packet()
    )
    assert c["strategy_candidate_family_selection_verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_AWAIT
    )


def test_19_await_on_non_ready_upstream_verdict():
    sig = _active_signal()
    sig["strategy_candidate_protocol_verdict"] = (
        "STRATEGY_CANDIDATE_PROTOCOL_NEEDS_MORE_INFO"
    )
    c = build_crypto_d1_strategy_candidate_family_selection_contract(
        sig, _valid_packet()
    )
    assert c["strategy_candidate_family_selection_verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_AWAIT
    )


def test_20_await_on_wrong_next_gate():
    sig = _active_signal()
    sig["next_gate"] = (
        "CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_READY_SEPARATE_HUMAN_NEXT_STEP_"
        "REQUIRED"
    )
    c = build_crypto_d1_strategy_candidate_family_selection_contract(
        sig, _valid_packet()
    )
    assert c["strategy_candidate_family_selection_verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_AWAIT
    )


def test_21_await_on_wrong_mode():
    sig = _active_signal()
    sig["mode"] = "LIVE"
    c = build_crypto_d1_strategy_candidate_family_selection_contract(
        sig, _valid_packet()
    )
    assert c["strategy_candidate_family_selection_verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_AWAIT
    )


def test_22_await_on_executable_signal():
    sig = _active_signal()
    sig["executes"] = True
    c = build_crypto_d1_strategy_candidate_family_selection_contract(
        sig, _valid_packet()
    )
    assert c["strategy_candidate_family_selection_verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_AWAIT
    )


def test_23_await_on_non_read_only_signal():
    sig = _active_signal()
    sig["read_only"] = False
    c = build_crypto_d1_strategy_candidate_family_selection_contract(
        sig, _valid_packet()
    )
    assert c["strategy_candidate_family_selection_verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_AWAIT
    )


def test_24_await_next_gate_when_inactive():
    c = build_crypto_d1_strategy_candidate_family_selection_contract({}, None)
    assert c["next_gate"] == (
        NEXT_GATE_AWAIT_CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_CONTRACT
    )


def test_25_contract_active_with_ready_signal():
    c = build_crypto_d1_strategy_candidate_family_selection_contract(
        _active_signal(), _valid_packet()
    )
    assert c[
        "crypto_d1_strategy_candidate_family_selection_contract_active"
    ] is True
    assert c[
        "crypto_d1_strategy_candidate_family_selection_contract_state"
    ] == STRATEGY_CANDIDATE_FAMILY_SELECTION_STATE_ACTIVE


# --- 4: READY ---------------------------------------------------------------

def test_26_ready_for_valid_packet():
    ev = evaluate_crypto_d1_strategy_candidate_family_selection(_valid_packet())
    assert ev["verdict"] == STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_READY


def test_27_ready_through_build():
    c = build_crypto_d1_strategy_candidate_family_selection_contract(
        _active_signal(), _valid_packet()
    )
    assert c["strategy_candidate_family_selection_verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_READY
    )
    assert c["next_gate"] == (
        NEXT_GATE_CRYPTO_D1_STRATEGY_CANDIDATE_FAMILY_SELECTION_READY
    )


def test_28_ready_when_one_family_parked():
    p = _valid_packet()
    p["selected_families"] = list(REQUIRED_STRATEGY_FAMILIES[:3])
    p["parked_families"] = [REQUIRED_STRATEGY_FAMILIES[3]]
    ev = evaluate_crypto_d1_strategy_candidate_family_selection(p)
    assert ev["verdict"] == STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_READY


def test_29_ready_when_regime_parked_three_strategies_selected():
    p = _valid_packet()
    p["selected_families"] = [
        "MOMENTUM_TREND_CONTINUATION",
        "BREAKOUT_DONCHIAN_VOLATILITY_EXPANSION",
        "PULLBACK_MEAN_REVERSION_AFTER_STRONG_TREND",
    ]
    p["parked_families"] = ["REGIME_FILTER_LAYER"]
    ev = evaluate_crypto_d1_strategy_candidate_family_selection(p)
    assert ev["verdict"] == STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_READY


def test_30_ready_accepts_market_spot_only_synonym():
    p = _valid_packet()
    p["market_type"] = "spot_only"
    assert evaluate_crypto_d1_strategy_candidate_family_selection(p)[
        "verdict"
    ] == STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_READY


def test_31_ready_accepts_daily_timeframe_synonym():
    p = _valid_packet()
    p["timeframe"] = "daily"
    assert evaluate_crypto_d1_strategy_candidate_family_selection(p)[
        "verdict"
    ] == STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_READY


def test_32_ready_universe_string_form():
    p = _valid_packet()
    p["universe"] = "BTC, ETH, SOL"
    assert evaluate_crypto_d1_strategy_candidate_family_selection(p)[
        "verdict"
    ] == STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_READY


# --- 5: NEEDS_MORE_INFO -----------------------------------------------------

def test_33_empty_packet_needs_more_info():
    ev = evaluate_crypto_d1_strategy_candidate_family_selection({})
    assert ev["verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_NEEDS_MORE_INFO
    )


def test_34_non_dict_packet_needs_more_info():
    ev = evaluate_crypto_d1_strategy_candidate_family_selection("nonsense")
    assert ev["verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_NEEDS_MORE_INFO
    )


def test_35_missing_text_field_needs_more_info():
    p = _valid_packet()
    del p["family_selection_rationale"]
    ev = evaluate_crypto_d1_strategy_candidate_family_selection(p)
    assert ev["verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_NEEDS_MORE_INFO
    )
    assert "family_selection_rationale_required" in ev["reasons"]


def test_36_absent_affirmation_needs_more_info():
    p = _valid_packet()
    del p["no_backtest_run"]
    ev = evaluate_crypto_d1_strategy_candidate_family_selection(p)
    assert ev["verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_NEEDS_MORE_INFO
    )
    assert "no_backtest_run_must_be_affirmed_true" in ev["reasons"]


def test_37_missing_universe_member_needs_more_info():
    p = _valid_packet()
    p["universe"] = ["BTC", "ETH"]
    ev = evaluate_crypto_d1_strategy_candidate_family_selection(p)
    assert ev["verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_NEEDS_MORE_INFO
    )
    assert "universe_missing_SOL" in ev["reasons"]


def test_38_uncovered_family_needs_more_info():
    p = _valid_packet()
    p["selected_families"] = list(REQUIRED_STRATEGY_FAMILIES[:3])
    p["parked_families"] = []
    ev = evaluate_crypto_d1_strategy_candidate_family_selection(p)
    assert ev["verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_NEEDS_MORE_INFO
    )
    assert (
        "strategy_family_not_selected_or_parked_REGIME_FILTER_LAYER"
        in ev["reasons"]
    )


def test_39_needs_more_info_next_gate():
    c = build_crypto_d1_strategy_candidate_family_selection_contract(
        _active_signal(), {}
    )
    assert c["strategy_candidate_family_selection_verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_NEEDS_MORE_INFO
    )
    assert c["next_gate"] == (
        NEXT_GATE_CRYPTO_D1_STRATEGY_CANDIDATE_FAMILY_SELECTION_FIX_REQUIRED
    )


# --- 6: REJECTED ------------------------------------------------------------

def test_40_every_forbidden_allow_flag_rejects():
    for flag in STRATEGY_CANDIDATE_FAMILY_SELECTION_FORBIDDEN_ALLOW_FLAGS:
        p = _valid_packet()
        p[flag] = True
        ev = evaluate_crypto_d1_strategy_candidate_family_selection(p)
        assert ev["verdict"] == (
            STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_REJECTED
        ), f"{flag} should reject"
        assert f"forbidden_allow:{flag}" in ev["reasons"]


def test_41_relaxed_affirmation_rejects():
    p = _valid_packet()
    p["no_real_data_acquisition"] = False
    ev = evaluate_crypto_d1_strategy_candidate_family_selection(p)
    assert ev["verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_REJECTED
    )
    assert "affirmation_relaxed:no_real_data_acquisition" in ev["reasons"]


def test_42_disallowed_mode_rejects():
    p = _valid_packet()
    p["selection_mode"] = "live_trading"
    ev = evaluate_crypto_d1_strategy_candidate_family_selection(p)
    assert ev["verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_REJECTED
    )
    assert "disallowed_mode" in ev["reasons"]


def test_43_non_spot_market_rejects():
    for mt in ("perp", "perpetual", "futures", "margin", "funding"):
        p = _valid_packet()
        p["market_type"] = mt
        ev = evaluate_crypto_d1_strategy_candidate_family_selection(p)
        assert ev["verdict"] == (
            STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_REJECTED
        ), f"{mt} should reject"
        assert "disallowed_market_type" in ev["reasons"]


def test_44_intraday_timeframe_rejects():
    for tf in ("1h", "15m", "4h", "5m", "h1"):
        p = _valid_packet()
        p["timeframe"] = tf
        ev = evaluate_crypto_d1_strategy_candidate_family_selection(p)
        assert ev["verdict"] == (
            STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_REJECTED
        ), f"{tf} should reject"
        assert "disallowed_timeframe" in ev["reasons"]


def test_45_non_core_asset_rejects():
    p = _valid_packet()
    p["universe"] = ["BTC", "ETH", "SOL", "DOGE"]
    ev = evaluate_crypto_d1_strategy_candidate_family_selection(p)
    assert ev["verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_REJECTED
    )
    assert "non_core_assets_in_universe" in ev["reasons"]


def test_46_unknown_selected_family_rejects():
    p = _valid_packet()
    p["selected_families"] = list(REQUIRED_STRATEGY_FAMILIES) + [
        "MY_SECRET_ALPHA"
    ]
    ev = evaluate_crypto_d1_strategy_candidate_family_selection(p)
    assert ev["verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_REJECTED
    )
    assert "unknown_selected_strategy_family" in ev["reasons"]


def test_47_single_favorite_with_comparison_rejects():
    p = _valid_packet()
    p["selected_families"] = [REQUIRED_STRATEGY_FAMILIES[0]]
    p["parked_families"] = list(REQUIRED_STRATEGY_FAMILIES[1:])
    p["family_comparison_method"] = "pretend to compare"
    ev = evaluate_crypto_d1_strategy_candidate_family_selection(p)
    assert ev["verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_REJECTED
    )
    assert "single_family_masquerading_as_comparison" in ev["reasons"]


def test_48_regime_only_selection_rejects():
    p = _valid_packet()
    p["selected_families"] = ["REGIME_FILTER_LAYER"]
    p["parked_families"] = list(REQUIRED_STRATEGY_FAMILIES[:3])
    del p["family_comparison_method"]
    ev = evaluate_crypto_d1_strategy_candidate_family_selection(p)
    assert ev["verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_REJECTED
    )
    assert "regime_filter_layer_not_standalone_strategy" in ev["reasons"]


def test_49_automated_decider_rejects():
    for marker in ("bot", "llm", "automation", "autopilot"):
        p = _valid_packet()
        p["operator_name_or_id"] = marker
        ev = evaluate_crypto_d1_strategy_candidate_family_selection(p)
        assert ev["verdict"] == (
            STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_REJECTED
        ), f"{marker} should reject"


def test_50_granted_capabilities_rejects():
    p = _valid_packet()
    p["grants_capabilities"] = ["live_strategy_selection"]
    ev = evaluate_crypto_d1_strategy_candidate_family_selection(p)
    assert ev["verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_REJECTED
    )
    assert "grants_listed:grants_capabilities" in ev["reasons"]


def test_51_live_strategy_selection_flag_rejects():
    p = _valid_packet()
    p["selects_live_strategy"] = True
    ev = evaluate_crypto_d1_strategy_candidate_family_selection(p)
    assert ev["verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_REJECTED
    )
    assert "forbidden_allow:selects_live_strategy" in ev["reasons"]


def test_52_rejected_next_gate():
    p = _valid_packet()
    p["allow_real_data_acquisition"] = True
    c = build_crypto_d1_strategy_candidate_family_selection_contract(
        _active_signal(), p
    )
    assert c["strategy_candidate_family_selection_verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_REJECTED
    )
    assert c["next_gate"] == (
        NEXT_GATE_CRYPTO_D1_STRATEGY_CANDIDATE_FAMILY_SELECTION_REJECTED
    )


# --- 7: PARKED --------------------------------------------------------------

def test_53_park_flag_parks():
    p = _valid_packet()
    p["park"] = True
    ev = evaluate_crypto_d1_strategy_candidate_family_selection(p)
    assert ev["verdict"] == STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_PARKED


def test_54_operator_decision_parked():
    p = _valid_packet()
    p["operator_decision"] = "defer"
    ev = evaluate_crypto_d1_strategy_candidate_family_selection(p)
    assert ev["verdict"] == STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_PARKED


def test_55_selection_decision_parked():
    p = _valid_packet()
    p["selection_decision"] = "parked"
    ev = evaluate_crypto_d1_strategy_candidate_family_selection(p)
    assert ev["verdict"] == STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_PARKED


def test_56_parked_next_gate():
    p = _valid_packet()
    p["parked"] = True
    c = build_crypto_d1_strategy_candidate_family_selection_contract(
        _active_signal(), p
    )
    assert c["strategy_candidate_family_selection_verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_PARKED
    )
    assert c["next_gate"] == (
        NEXT_GATE_CRYPTO_D1_STRATEGY_CANDIDATE_FAMILY_SELECTION_PARKED
    )


# --- 8: verdict precedence --------------------------------------------------

def test_57_reject_beats_park():
    p = _valid_packet()
    p["park"] = True
    p["allow_real_data_acquisition"] = True
    assert evaluate_crypto_d1_strategy_candidate_family_selection(p)[
        "verdict"
    ] == STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_REJECTED


def test_58_reject_beats_missing():
    p = {"allow_qa_run": True}
    assert evaluate_crypto_d1_strategy_candidate_family_selection(p)[
        "verdict"
    ] == STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_REJECTED


def test_59_park_beats_missing():
    p = {"park": True}
    assert evaluate_crypto_d1_strategy_candidate_family_selection(p)[
        "verdict"
    ] == STRATEGY_CANDIDATE_FAMILY_SELECTION_VERDICT_PARKED


# --- 9: contract metadata / safety ------------------------------------------

def test_60_contract_read_only_and_non_executing():
    c = build_crypto_d1_strategy_candidate_family_selection_contract(
        _active_signal(), _valid_packet()
    )
    assert c["read_only"] is True
    assert c["executes"] is False
    assert c["human_approval_required"] is True


def test_61_all_auth_flags_false():
    c = build_crypto_d1_strategy_candidate_family_selection_contract(
        _active_signal(), _valid_packet()
    )
    for flag in _AUTH_FLAGS:
        assert c[flag] is False, flag


def test_62_safety_posture_all_false():
    assert STRATEGY_CANDIDATE_FAMILY_SELECTION_SAFETY_POSTURE
    assert all(
        v is False
        for v in STRATEGY_CANDIDATE_FAMILY_SELECTION_SAFETY_POSTURE.values()
    )
    c = build_crypto_d1_strategy_candidate_family_selection_contract(
        _active_signal(), _valid_packet()
    )
    assert all(v is False for v in c["safety_posture"].values())


def test_63_remaining_capabilities_blocked_nonempty():
    assert len(REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED) >= 1
    c = build_crypto_d1_strategy_candidate_family_selection_contract(
        _active_signal(), _valid_packet()
    )
    assert c["remaining_real_world_capabilities_blocked"] == (
        REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED
    )


def test_64_contract_next_action_and_stage():
    c = build_crypto_d1_strategy_candidate_family_selection_contract(
        _active_signal(), _valid_packet()
    )
    assert c["strategy_candidate_family_selection_next_required_action"] == (
        STRATEGY_CANDIDATE_FAMILY_SELECTION_NEXT_REQUIRED_ACTION
    )
    assert c["strategy_candidate_family_selection_current_stage"] == (
        STRATEGY_CANDIDATE_FAMILY_SELECTION_CURRENT_STAGE
    )


def test_65_no_verdict_unlocks_anything():
    for packet in (
        {},
        _valid_packet(),
        {"allow_real_data_acquisition": True},
        {"selects_live_strategy": True},
        {"park": True},
    ):
        c = build_crypto_d1_strategy_candidate_family_selection_contract(
            _active_signal(), packet
        )
        assert c["executes"] is False
        assert all(c[flag] is False for flag in _AUTH_FLAGS)
        assert all(v is False for v in c["safety_posture"].values())


# --- 10: validation ---------------------------------------------------------

def test_66_valid_contract_validates():
    c = build_crypto_d1_strategy_candidate_family_selection_contract(
        _active_signal(), _valid_packet()
    )
    assert validate_crypto_d1_strategy_candidate_family_selection_contract(c)[
        "valid"
    ]
    assert c["validation"]["valid"] is True


def test_67_tampered_schema_invalidates():
    c = build_crypto_d1_strategy_candidate_family_selection_contract(
        _active_signal(), _valid_packet()
    )
    c["schema_version"] = "bogus"
    assert not (
        validate_crypto_d1_strategy_candidate_family_selection_contract(c)[
            "valid"
        ]
    )


def test_68_tampered_read_only_invalidates():
    c = build_crypto_d1_strategy_candidate_family_selection_contract(
        _active_signal(), _valid_packet()
    )
    c["read_only"] = False
    assert not (
        validate_crypto_d1_strategy_candidate_family_selection_contract(c)[
            "valid"
        ]
    )


def test_69_missing_required_field_invalidates():
    c = build_crypto_d1_strategy_candidate_family_selection_contract(
        _active_signal(), _valid_packet()
    )
    del c["safety_posture"]
    res = validate_crypto_d1_strategy_candidate_family_selection_contract(c)
    assert not res["valid"]
    assert "safety_posture" in res["missing_required_fields"]


def test_70_non_dict_contract_invalid():
    res = validate_crypto_d1_strategy_candidate_family_selection_contract("nope")
    assert res["valid"] is False


# --- 11: determinism + mutation isolation -----------------------------------

def test_71_evaluate_is_deterministic():
    p = _valid_packet()
    a = evaluate_crypto_d1_strategy_candidate_family_selection(p)
    b = evaluate_crypto_d1_strategy_candidate_family_selection(p)
    assert a == b


def test_72_build_is_deterministic():
    sig = _active_signal()
    a = build_crypto_d1_strategy_candidate_family_selection_contract(
        sig, _valid_packet()
    )
    b = build_crypto_d1_strategy_candidate_family_selection_contract(
        sig, _valid_packet()
    )
    assert a == b


def test_73_echoed_packet_is_a_copy():
    p = _valid_packet()
    c = build_crypto_d1_strategy_candidate_family_selection_contract(
        _active_signal(), p
    )
    c["evaluated_family_selection_packet"]["family_selection_packet_id"] = "x"
    assert p["family_selection_packet_id"] != "x"


def test_74_safety_posture_copies_independent():
    c1 = build_crypto_d1_strategy_candidate_family_selection_contract(
        _active_signal(), _valid_packet()
    )
    c2 = build_crypto_d1_strategy_candidate_family_selection_contract(
        _active_signal(), _valid_packet()
    )
    c1["safety_posture"]["acquires_data"] = True
    assert c2["safety_posture"]["acquires_data"] is False
    assert (
        STRATEGY_CANDIDATE_FAMILY_SELECTION_SAFETY_POSTURE["acquires_data"]
        is False
    )


# --- 12: render -------------------------------------------------------------

def test_75_render_markdown_nonempty():
    c = build_crypto_d1_strategy_candidate_family_selection_contract(
        _active_signal(), _valid_packet()
    )
    md = render_crypto_d1_strategy_candidate_family_selection_contract_markdown(
        c
    )
    assert isinstance(md, str) and len(md) > 200


def test_76_render_markdown_names_sections():
    c = build_crypto_d1_strategy_candidate_family_selection_contract(
        _active_signal(), _valid_packet()
    )
    md = render_crypto_d1_strategy_candidate_family_selection_contract_markdown(
        c
    )
    assert "Strategy Candidate Family Selection Verdict Reasons" in md
    assert "Required Research Scope" in md
    assert "Remaining Real-World Capabilities Blocked" in md
    assert "Mode: RESEARCH_ONLY" in md


# --- 13: pure stdlib import-root audit --------------------------------------

def test_77_import_roots_are_allowed_only():
    src = _MODPATH.read_text(encoding="utf-8")
    roots: set[str] = set()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    allowed = {"__future__", "typing", "sparta_commander"}
    assert roots <= allowed, (
        f"unexpected import roots: {sorted(roots - allowed)}"
    )
    for banned in ("os", "sys", "subprocess", "socket", "requests",
                   "urllib", "pathlib", "json", "http", "asyncio",
                   "datetime", "time", "random", "glob", "importlib",
                   "shutil", "io", "ccxt", "freqtrade"):
        assert banned not in roots, f"banned import root present: {banned}"


# --- 14: forbidden-surface audit --------------------------------------------

def test_78_no_forbidden_call_surface():
    src = _MODPATH.read_text(encoding="utf-8")
    forbidden = (
        "open(", "write_text(", "write_bytes(", ".write(", "read_text(",
        "read_bytes(", ".read(", "json.dump(", "json.load(",
        "import subprocess", "from subprocess", "Popen", "os.system",
        "os.listdir", "os.scandir", "os.walk", "listdir(", "scandir(",
        "glob(", "iglob(", "import socket", "socket.socket", "urllib",
        "requests", "httpx", "http.client", "asyncio", "place_order",
        "submit_order", "create_order", "cancel_order", "ccxt", "freqtrade",
        "paper_trade", "live_trade", "autopilot(", ".upload(", "datetime.",
        "time.time(", "random.", "subprocess.run", "check_output",
        "importlib", "__import__", "eval(", "exec(", "compile(",
        "os.environ", "os.getenv", "getenv(",
    )
    hits = [tok for tok in forbidden if tok in src]
    assert hits == [], f"forbidden surface tokens present: {hits}"


# --- 15: commander_2_safety allowlist ---------------------------------------

def test_79_commander_2_safety_allowlist_includes_new_paths():
    src = _SAFETY_PATH.read_text(encoding="utf-8")
    assert (
        '"sparta_commander/strategy_factory_crypto_d1_strategy_candidate_'
        'family_selection_contract.py"'
    ) in src
    assert (
        '"tests/test_strategy_factory_crypto_d1_strategy_candidate_family_'
        'selection_contract.py"'
    ) in src
