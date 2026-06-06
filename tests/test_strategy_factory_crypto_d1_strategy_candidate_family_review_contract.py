"""Tests for the Crypto-D1 Strategy Candidate Family Review Contract (Block
101).

The module is a PURE, stdlib-only, read-only *paper contract* that VALIDATES
whether a proposed family-selection review is reasonable under the Crypto-D1
Strategy Candidate Family Selection Contract (Block 99). It evaluates the SHAPE
of a proposed review only -- it acquires/fetches/inspects/loads no data, runs no
QA/baseline/backtest/simulation, produces no trade signal, reaches no broker/
exchange/order/account/API, trades no paper/live, selects no live strategy,
triggers no automation, and writes nothing.

Coverage:
- pure stdlib import-root audit + forbidden-surface audit
- exported constants / schema version / verdict + state / safety posture
- activation rule: AWAIT unless upstream family-selection signal is READY for the
  family-review gate (active + READY verdict + family-review next_gate +
  RESEARCH_ONLY + read_only + non-executing)
- READY only for a fully-specified research-only BTC/ETH/SOL spot D1 review with
  all four families reviewed-selected or reviewed-parked and every real-world
  capability blocked
- READY when one family is explicitly parked (with a research-only reason) and
  the rest reviewed-selected
- NEEDS_MORE_INFO for empty / incomplete reviews (missing field, missing
  affirmation, missing universe member, an uncovered family, missing rationale,
  missing parked-family rationale)
- REJECTED for any forbidden allow flag, relaxed affirmation, disallowed mode,
  off-scope market type / timeframe, non-core asset, unknown reviewed family,
  single-favorite family masquerading as full coverage, regime-only selection,
  automated reviewer, granted authority
- PARKED when a reviewer explicitly parks/defers the whole family-review lane
- verdict precedence: REJECTED > PARKED > NEEDS_MORE_INFO > READY; AWAIT first
- verdict -> next_gate mapping in build_*
- validation valid for a real contract, invalid when tampered
- deterministic repeated calls; mutation-isolated copies
- read_only True, executes False, human_approval_required True, auth all False
- scope mirrors the family-selection contract (universe/market/timeframe/families)
- render markdown is non-empty and names key sections
- commander_2_safety allowlist includes the new module + test paths
"""

from __future__ import annotations

import ast
import pathlib

from sparta_commander.strategy_factory_crypto_d1_strategy_candidate_family_review_contract import (  # noqa: E501
    STRATEGY_CANDIDATE_FAMILY_REVIEW_SCHEMA_VERSION,
    DEFAULT_STRATEGY_CANDIDATE_FAMILY_REVIEW_LABEL,
    STRATEGY_CANDIDATE_FAMILY_REVIEW_STATUS,
    STRATEGY_CANDIDATE_FAMILY_REVIEW_SAFETY_POSTURE,
    STRATEGY_CANDIDATE_FAMILY_REVIEW_STATE_ACTIVE,
    STRATEGY_CANDIDATE_FAMILY_REVIEW_STATE_BLOCKED,
    STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_READY,
    STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_NEEDS_MORE_INFO,
    STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_REJECTED,
    STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_PARKED,
    STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_AWAIT,
    ALLOWED_STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICTS,
    UPSTREAM_REQUIRED_FAMILY_SELECTION_VERDICT,
    UPSTREAM_REQUIRED_FAMILY_SELECTION_NEXT_GATE,
    UPSTREAM_REQUIRED_FAMILY_SELECTION_MODE,
    STRATEGY_CANDIDATE_FAMILY_REVIEW_NEXT_REQUIRED_ACTION,
    STRATEGY_CANDIDATE_FAMILY_REVIEW_CURRENT_STAGE,
    NEXT_GATE_CRYPTO_D1_STRATEGY_CANDIDATE_FAMILY_REVIEW_READY,
    NEXT_GATE_CRYPTO_D1_STRATEGY_CANDIDATE_FAMILY_REVIEW_FIX_REQUIRED,
    NEXT_GATE_CRYPTO_D1_STRATEGY_CANDIDATE_FAMILY_REVIEW_PARKED,
    NEXT_GATE_CRYPTO_D1_STRATEGY_CANDIDATE_FAMILY_REVIEW_REJECTED,
    NEXT_GATE_AWAIT_CRYPTO_D1_STRATEGY_CANDIDATE_FAMILY_SELECTION_CONTRACT,
    REQUIRED_RESEARCH_UNIVERSE,
    REQUIRED_MARKET_TYPE,
    REQUIRED_TIMEFRAME,
    REQUIRED_STRATEGY_FAMILIES,
    REQUIRED_STRATEGY_CANDIDATE_FAMILY_REVIEW_FIELDS,
    STRATEGY_CANDIDATE_FAMILY_REVIEW_REQUIRED_TEXT_FIELDS,
    STRATEGY_CANDIDATE_FAMILY_REVIEW_REQUIRED_AFFIRMATIONS,
    STRATEGY_CANDIDATE_FAMILY_REVIEW_FORBIDDEN_ALLOW_FLAGS,
    ALLOWED_STRATEGY_CANDIDATE_FAMILY_REVIEW_MODES,
    AUTOMATED_APPROVAL_MARKERS,
    REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED,
    evaluate_crypto_d1_strategy_candidate_family_review,
    build_crypto_d1_strategy_candidate_family_review_contract,
    validate_crypto_d1_strategy_candidate_family_review_contract,
    render_crypto_d1_strategy_candidate_family_review_contract_markdown,
)

_MODPATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "sparta_commander"
    / "strategy_factory_crypto_d1_strategy_candidate_family_review_contract.py"
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
    """A fully-specified, safe, research-only family-review packet with all four
    families reviewed-selected."""
    packet: dict = {}
    for key in STRATEGY_CANDIDATE_FAMILY_REVIEW_REQUIRED_TEXT_FIELDS:
        packet[key] = f"value-for-{key}"
    packet["reviewed_universe"] = list(REQUIRED_RESEARCH_UNIVERSE)
    packet["reviewed_market_type"] = "SPOT"
    packet["reviewed_timeframe"] = "D1"
    packet["review_mode"] = "RESEARCH_ONLY"
    packet["reviewed_selected_families"] = list(REQUIRED_STRATEGY_FAMILIES)
    packet["reviewed_parked_families"] = []
    for flag in STRATEGY_CANDIDATE_FAMILY_REVIEW_REQUIRED_AFFIRMATIONS:
        packet[flag] = True
    return packet


def _active_signal() -> dict:
    """An upstream family-selection signal that activates this contract."""
    return {
        "strategy_candidate_family_selection_contract_active": True,
        "strategy_candidate_family_selection_verdict": (
            UPSTREAM_REQUIRED_FAMILY_SELECTION_VERDICT
        ),
        "next_gate": UPSTREAM_REQUIRED_FAMILY_SELECTION_NEXT_GATE,
        "mode": UPSTREAM_REQUIRED_FAMILY_SELECTION_MODE,
        "read_only": True,
        "executes": False,
    }


# --- 1: schema / identity ---------------------------------------------------

def test_01_schema_version_value():
    assert STRATEGY_CANDIDATE_FAMILY_REVIEW_SCHEMA_VERSION == (
        "strategy_factory_crypto_d1_strategy_candidate_family_review_"
        "contract.v1"
    )


def test_02_label_and_status_nonempty():
    assert DEFAULT_STRATEGY_CANDIDATE_FAMILY_REVIEW_LABEL
    assert STRATEGY_CANDIDATE_FAMILY_REVIEW_STATUS.startswith("READ_ONLY")


def test_03_states_distinct():
    assert (
        STRATEGY_CANDIDATE_FAMILY_REVIEW_STATE_ACTIVE
        != STRATEGY_CANDIDATE_FAMILY_REVIEW_STATE_BLOCKED
    )


def test_04_allowed_verdicts_exact():
    assert ALLOWED_STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICTS == (
        STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_READY,
        STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_NEEDS_MORE_INFO,
        STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_REJECTED,
        STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_PARKED,
        STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_AWAIT,
    )


def test_05_await_verdict_value():
    assert STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_AWAIT == (
        "AWAIT_CRYPTO_D1_STRATEGY_CANDIDATE_FAMILY_SELECTION_CONTRACT"
    )


def test_06_verdict_values_are_family_review_named():
    assert STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_READY == (
        "STRATEGY_CANDIDATE_FAMILY_REVIEW_READY"
    )
    assert STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_NEEDS_MORE_INFO == (
        "STRATEGY_CANDIDATE_FAMILY_REVIEW_NEEDS_MORE_INFO"
    )
    assert STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_REJECTED == (
        "STRATEGY_CANDIDATE_FAMILY_REVIEW_REJECTED"
    )
    assert STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_PARKED == (
        "STRATEGY_CANDIDATE_FAMILY_REVIEW_PARKED"
    )


def test_07_all_five_verdicts_distinct():
    assert len(set(ALLOWED_STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICTS)) == 5


# --- 2: upstream / scope mirrors the family-selection contract ---------------

def test_08_upstream_required_verdict_is_family_selection_ready():
    assert UPSTREAM_REQUIRED_FAMILY_SELECTION_VERDICT == (
        "STRATEGY_CANDIDATE_FAMILY_SELECTION_READY"
    )


def test_09_upstream_required_next_gate():
    assert UPSTREAM_REQUIRED_FAMILY_SELECTION_NEXT_GATE == (
        "CRYPTO_D1_STRATEGY_CANDIDATE_FAMILY_REVIEW_CONTRACT_REQUIRED"
    )


def test_10_upstream_required_mode_research_only():
    assert UPSTREAM_REQUIRED_FAMILY_SELECTION_MODE == "RESEARCH_ONLY"


def test_11_required_universe_btc_eth_sol():
    assert REQUIRED_RESEARCH_UNIVERSE == ("BTC", "ETH", "SOL")


def test_12_required_market_spot_only():
    assert REQUIRED_MARKET_TYPE == "SPOT"


def test_13_required_timeframe_d1_only():
    assert REQUIRED_TIMEFRAME == "D1"


def test_14_required_families_all_four():
    assert REQUIRED_STRATEGY_FAMILIES == _EXPECTED_FAMILIES


def test_15_required_fields_text_plus_affirmations():
    assert REQUIRED_STRATEGY_CANDIDATE_FAMILY_REVIEW_FIELDS == (
        STRATEGY_CANDIDATE_FAMILY_REVIEW_REQUIRED_TEXT_FIELDS
        + STRATEGY_CANDIDATE_FAMILY_REVIEW_REQUIRED_AFFIRMATIONS
    )


def test_16_next_action_and_stage_values():
    assert STRATEGY_CANDIDATE_FAMILY_REVIEW_NEXT_REQUIRED_ACTION == (
        "BUILD_CRYPTO_D1_STRATEGY_CANDIDATE_FAMILY_REVIEW_CONTRACT"
    )
    assert STRATEGY_CANDIDATE_FAMILY_REVIEW_CURRENT_STAGE == (
        "CRYPTO_D1_STRATEGY_CANDIDATE_FAMILY_REVIEW_CONTRACT_REQUIRED"
    )


def test_17_required_text_fields_include_review_fields():
    for field in (
        "family_review_packet_id",
        "upstream_family_selection_id",
        "family_selection_contract_version",
        "review_scope",
        "review_mode",
        "reviewed_selected_families",
        "reviewed_family_selection_rationale",
        "reviewed_family_priority_order",
        "reviewed_family_comparison_method",
        "reviewed_family_balance_policy",
        "reviewed_universe",
        "reviewed_market_type",
        "reviewed_timeframe",
        "reviewer_name_or_id",
        "review_decision_rationale",
        "next_step_boundary",
        "review_notes",
    ):
        assert field in STRATEGY_CANDIDATE_FAMILY_REVIEW_REQUIRED_TEXT_FIELDS


def test_18_required_affirmations_include_safety_flags():
    for flag in (
        "explicit_human_review",
        "research_only_acknowledgement",
        "no_execution_acknowledgement",
        "no_real_data_acquisition",
        "no_data_fetch",
        "no_data_inspection",
        "no_dataset_loading",
        "no_qa_run",
        "no_baseline_run",
        "no_backtest_run",
        "no_simulation_run",
        "no_trade_signal",
        "no_paper_live",
        "no_broker_exchange",
        "no_order_capability",
        "no_account_access",
        "no_api_keys",
        "no_automation_trigger",
        "no_runtime_write",
        "no_registry_write",
        "no_dashboard_write",
    ):
        assert flag in STRATEGY_CANDIDATE_FAMILY_REVIEW_REQUIRED_AFFIRMATIONS


# --- 3: activation rule (AWAIT) ---------------------------------------------

def test_19_await_on_missing_signal():
    c = build_crypto_d1_strategy_candidate_family_review_contract(None, None)
    assert c["strategy_candidate_family_review_verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_AWAIT
    )
    assert c[
        "crypto_d1_strategy_candidate_family_review_contract_active"
    ] is False


def test_20_await_on_empty_signal():
    c = build_crypto_d1_strategy_candidate_family_review_contract(
        {}, _valid_packet()
    )
    assert c["strategy_candidate_family_review_verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_AWAIT
    )


def test_21_await_on_malformed_signal_string():
    c = build_crypto_d1_strategy_candidate_family_review_contract(
        "not-a-dict", _valid_packet()
    )
    assert c["strategy_candidate_family_review_verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_AWAIT
    )


def test_22_await_on_inactive_family_selection_contract():
    sig = _active_signal()
    sig["strategy_candidate_family_selection_contract_active"] = False
    c = build_crypto_d1_strategy_candidate_family_review_contract(
        sig, _valid_packet()
    )
    assert c["strategy_candidate_family_review_verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_AWAIT
    )


def test_23_await_on_non_ready_upstream_verdict():
    sig = _active_signal()
    sig["strategy_candidate_family_selection_verdict"] = (
        "STRATEGY_CANDIDATE_FAMILY_SELECTION_NEEDS_MORE_INFO"
    )
    c = build_crypto_d1_strategy_candidate_family_review_contract(
        sig, _valid_packet()
    )
    assert c["strategy_candidate_family_review_verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_AWAIT
    )


def test_24_await_on_parked_upstream_verdict():
    sig = _active_signal()
    sig["strategy_candidate_family_selection_verdict"] = (
        "STRATEGY_CANDIDATE_FAMILY_SELECTION_PARKED"
    )
    c = build_crypto_d1_strategy_candidate_family_review_contract(
        sig, _valid_packet()
    )
    assert c["strategy_candidate_family_review_verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_AWAIT
    )


def test_25_await_on_rejected_upstream_verdict():
    sig = _active_signal()
    sig["strategy_candidate_family_selection_verdict"] = (
        "STRATEGY_CANDIDATE_FAMILY_SELECTION_REJECTED"
    )
    c = build_crypto_d1_strategy_candidate_family_review_contract(
        sig, _valid_packet()
    )
    assert c["strategy_candidate_family_review_verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_AWAIT
    )


def test_26_await_on_wrong_next_gate():
    sig = _active_signal()
    sig["next_gate"] = (
        "CRYPTO_D1_STRATEGY_CANDIDATE_FAMILY_SELECTION_READY_SEPARATE_HUMAN_"
        "NEXT_STEP_REQUIRED"
    )
    c = build_crypto_d1_strategy_candidate_family_review_contract(
        sig, _valid_packet()
    )
    assert c["strategy_candidate_family_review_verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_AWAIT
    )


def test_27_await_on_wrong_mode():
    sig = _active_signal()
    sig["mode"] = "LIVE"
    c = build_crypto_d1_strategy_candidate_family_review_contract(
        sig, _valid_packet()
    )
    assert c["strategy_candidate_family_review_verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_AWAIT
    )


def test_28_await_on_executable_signal():
    sig = _active_signal()
    sig["executes"] = True
    c = build_crypto_d1_strategy_candidate_family_review_contract(
        sig, _valid_packet()
    )
    assert c["strategy_candidate_family_review_verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_AWAIT
    )


def test_29_await_on_non_read_only_signal():
    sig = _active_signal()
    sig["read_only"] = False
    c = build_crypto_d1_strategy_candidate_family_review_contract(
        sig, _valid_packet()
    )
    assert c["strategy_candidate_family_review_verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_AWAIT
    )


def test_30_await_on_missing_active_flag():
    sig = _active_signal()
    del sig["strategy_candidate_family_selection_contract_active"]
    c = build_crypto_d1_strategy_candidate_family_review_contract(
        sig, _valid_packet()
    )
    assert c["strategy_candidate_family_review_verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_AWAIT
    )


def test_31_await_next_gate_when_inactive():
    c = build_crypto_d1_strategy_candidate_family_review_contract({}, None)
    assert c["next_gate"] == (
        NEXT_GATE_AWAIT_CRYPTO_D1_STRATEGY_CANDIDATE_FAMILY_SELECTION_CONTRACT
    )


def test_32_await_state_blocked_when_inactive():
    c = build_crypto_d1_strategy_candidate_family_review_contract({}, None)
    assert c[
        "crypto_d1_strategy_candidate_family_review_contract_state"
    ] == STRATEGY_CANDIDATE_FAMILY_REVIEW_STATE_BLOCKED


def test_33_contract_active_with_ready_signal():
    c = build_crypto_d1_strategy_candidate_family_review_contract(
        _active_signal(), _valid_packet()
    )
    assert c[
        "crypto_d1_strategy_candidate_family_review_contract_active"
    ] is True
    assert c[
        "crypto_d1_strategy_candidate_family_review_contract_state"
    ] == STRATEGY_CANDIDATE_FAMILY_REVIEW_STATE_ACTIVE


def test_34_await_packet_ignored_when_inactive():
    # Even a forbidden packet stays AWAIT when upstream is not READY.
    p = _valid_packet()
    p["allow_real_data_acquisition"] = True
    c = build_crypto_d1_strategy_candidate_family_review_contract({}, p)
    assert c["strategy_candidate_family_review_verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_AWAIT
    )


# --- 4: READY ---------------------------------------------------------------

def test_35_ready_for_valid_packet():
    ev = evaluate_crypto_d1_strategy_candidate_family_review(_valid_packet())
    assert ev["verdict"] == STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_READY


def test_36_ready_through_build():
    c = build_crypto_d1_strategy_candidate_family_review_contract(
        _active_signal(), _valid_packet()
    )
    assert c["strategy_candidate_family_review_verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_READY
    )
    assert c["next_gate"] == (
        NEXT_GATE_CRYPTO_D1_STRATEGY_CANDIDATE_FAMILY_REVIEW_READY
    )


def test_37_ready_when_one_family_parked_with_reason():
    p = _valid_packet()
    p["reviewed_selected_families"] = list(REQUIRED_STRATEGY_FAMILIES[:3])
    p["reviewed_parked_families"] = [REQUIRED_STRATEGY_FAMILIES[3]]
    p["reviewed_parked_family_rationale"] = "regime layer is a research gate"
    ev = evaluate_crypto_d1_strategy_candidate_family_review(p)
    assert ev["verdict"] == STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_READY


def test_38_ready_when_regime_parked_three_strategies_selected():
    p = _valid_packet()
    p["reviewed_selected_families"] = [
        "MOMENTUM_TREND_CONTINUATION",
        "BREAKOUT_DONCHIAN_VOLATILITY_EXPANSION",
        "PULLBACK_MEAN_REVERSION_AFTER_STRONG_TREND",
    ]
    p["reviewed_parked_families"] = ["REGIME_FILTER_LAYER"]
    p["reviewed_parked_family_rationale"] = (
        "regime filter treated as a research gate, not a live strategy"
    )
    ev = evaluate_crypto_d1_strategy_candidate_family_review(p)
    assert ev["verdict"] == STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_READY


def test_39_ready_accepts_market_spot_only_synonym():
    p = _valid_packet()
    p["reviewed_market_type"] = "spot_only"
    assert evaluate_crypto_d1_strategy_candidate_family_review(p)[
        "verdict"
    ] == STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_READY


def test_40_ready_accepts_daily_timeframe_synonym():
    p = _valid_packet()
    p["reviewed_timeframe"] = "daily"
    assert evaluate_crypto_d1_strategy_candidate_family_review(p)[
        "verdict"
    ] == STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_READY


def test_41_ready_universe_string_form():
    p = _valid_packet()
    p["reviewed_universe"] = "BTC, ETH, SOL"
    assert evaluate_crypto_d1_strategy_candidate_family_review(p)[
        "verdict"
    ] == STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_READY


def test_42_ready_reason_is_descriptive():
    ev = evaluate_crypto_d1_strategy_candidate_family_review(_valid_packet())
    assert len(ev["reasons"]) == 1
    assert "research_only_family_review_fully_specified" in ev["reasons"][0]


# --- 5: NEEDS_MORE_INFO -----------------------------------------------------

def test_43_empty_packet_needs_more_info():
    ev = evaluate_crypto_d1_strategy_candidate_family_review({})
    assert ev["verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_NEEDS_MORE_INFO
    )
    assert "strategy_candidate_family_review_packet_missing" in ev["reasons"]


def test_44_non_dict_packet_needs_more_info():
    ev = evaluate_crypto_d1_strategy_candidate_family_review("nonsense")
    assert ev["verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_NEEDS_MORE_INFO
    )


def test_45_none_packet_needs_more_info():
    ev = evaluate_crypto_d1_strategy_candidate_family_review(None)
    assert ev["verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_NEEDS_MORE_INFO
    )


def test_46_missing_text_field_needs_more_info():
    p = _valid_packet()
    del p["reviewed_family_selection_rationale"]
    ev = evaluate_crypto_d1_strategy_candidate_family_review(p)
    assert ev["verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_NEEDS_MORE_INFO
    )
    assert "reviewed_family_selection_rationale_required" in ev["reasons"]


def test_47_missing_review_decision_rationale_needs_more_info():
    p = _valid_packet()
    del p["review_decision_rationale"]
    ev = evaluate_crypto_d1_strategy_candidate_family_review(p)
    assert ev["verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_NEEDS_MORE_INFO
    )
    assert "review_decision_rationale_required" in ev["reasons"]


def test_48_missing_comparison_method_needs_more_info():
    p = _valid_packet()
    del p["reviewed_family_comparison_method"]
    ev = evaluate_crypto_d1_strategy_candidate_family_review(p)
    assert ev["verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_NEEDS_MORE_INFO
    )
    assert "reviewed_family_comparison_method_required" in ev["reasons"]


def test_49_missing_next_step_boundary_needs_more_info():
    p = _valid_packet()
    del p["next_step_boundary"]
    ev = evaluate_crypto_d1_strategy_candidate_family_review(p)
    assert ev["verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_NEEDS_MORE_INFO
    )
    assert "next_step_boundary_required" in ev["reasons"]


def test_50_absent_affirmation_needs_more_info():
    p = _valid_packet()
    del p["no_backtest_run"]
    ev = evaluate_crypto_d1_strategy_candidate_family_review(p)
    assert ev["verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_NEEDS_MORE_INFO
    )
    assert "no_backtest_run_must_be_affirmed_true" in ev["reasons"]


def test_51_absent_human_review_affirmation_needs_more_info():
    p = _valid_packet()
    del p["explicit_human_review"]
    ev = evaluate_crypto_d1_strategy_candidate_family_review(p)
    assert ev["verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_NEEDS_MORE_INFO
    )
    assert "explicit_human_review_must_be_affirmed_true" in ev["reasons"]


def test_52_missing_universe_member_needs_more_info():
    p = _valid_packet()
    p["reviewed_universe"] = ["BTC", "ETH"]
    ev = evaluate_crypto_d1_strategy_candidate_family_review(p)
    assert ev["verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_NEEDS_MORE_INFO
    )
    assert "reviewed_universe_missing_SOL" in ev["reasons"]


def test_53_uncovered_family_needs_more_info():
    p = _valid_packet()
    p["reviewed_selected_families"] = list(REQUIRED_STRATEGY_FAMILIES[:3])
    p["reviewed_parked_families"] = []
    ev = evaluate_crypto_d1_strategy_candidate_family_review(p)
    assert ev["verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_NEEDS_MORE_INFO
    )
    assert (
        "strategy_family_not_reviewed_selected_or_parked_REGIME_FILTER_LAYER"
        in ev["reasons"]
    )


def test_54_parked_family_without_rationale_needs_more_info():
    p = _valid_packet()
    p["reviewed_selected_families"] = list(REQUIRED_STRATEGY_FAMILIES[:3])
    p["reviewed_parked_families"] = [REQUIRED_STRATEGY_FAMILIES[3]]
    # No reviewed_parked_family_rationale provided.
    ev = evaluate_crypto_d1_strategy_candidate_family_review(p)
    assert ev["verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_NEEDS_MORE_INFO
    )
    assert "reviewed_parked_family_rationale_required" in ev["reasons"]


def test_55_needs_more_info_next_gate():
    c = build_crypto_d1_strategy_candidate_family_review_contract(
        _active_signal(), {}
    )
    assert c["strategy_candidate_family_review_verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_NEEDS_MORE_INFO
    )
    assert c["next_gate"] == (
        NEXT_GATE_CRYPTO_D1_STRATEGY_CANDIDATE_FAMILY_REVIEW_FIX_REQUIRED
    )


# --- 6: REJECTED ------------------------------------------------------------

def test_56_every_forbidden_allow_flag_rejects():
    for flag in STRATEGY_CANDIDATE_FAMILY_REVIEW_FORBIDDEN_ALLOW_FLAGS:
        p = _valid_packet()
        p[flag] = True
        ev = evaluate_crypto_d1_strategy_candidate_family_review(p)
        assert ev["verdict"] == (
            STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_REJECTED
        ), f"{flag} should reject"
        assert f"forbidden_allow:{flag}" in ev["reasons"]


def test_57_relaxed_affirmation_rejects():
    p = _valid_packet()
    p["no_real_data_acquisition"] = False
    ev = evaluate_crypto_d1_strategy_candidate_family_review(p)
    assert ev["verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_REJECTED
    )
    assert "affirmation_relaxed:no_real_data_acquisition" in ev["reasons"]


def test_58_disallowed_mode_rejects():
    p = _valid_packet()
    p["review_mode"] = "live_trading"
    ev = evaluate_crypto_d1_strategy_candidate_family_review(p)
    assert ev["verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_REJECTED
    )
    assert "disallowed_mode" in ev["reasons"]


def test_59_non_spot_market_rejects():
    for mt in ("perp", "perpetual", "futures", "margin", "funding"):
        p = _valid_packet()
        p["reviewed_market_type"] = mt
        ev = evaluate_crypto_d1_strategy_candidate_family_review(p)
        assert ev["verdict"] == (
            STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_REJECTED
        ), f"{mt} should reject"
        assert "disallowed_market_type" in ev["reasons"]


def test_60_intraday_timeframe_rejects():
    for tf in ("1h", "15m", "4h", "5m", "h1"):
        p = _valid_packet()
        p["reviewed_timeframe"] = tf
        ev = evaluate_crypto_d1_strategy_candidate_family_review(p)
        assert ev["verdict"] == (
            STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_REJECTED
        ), f"{tf} should reject"
        assert "disallowed_timeframe" in ev["reasons"]


def test_61_perps_flag_rejects():
    p = _valid_packet()
    p["uses_perps"] = True
    ev = evaluate_crypto_d1_strategy_candidate_family_review(p)
    assert ev["verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_REJECTED
    )
    assert "forbidden_allow:uses_perps" in ev["reasons"]


def test_62_funding_flag_rejects():
    p = _valid_packet()
    p["uses_funding"] = True
    ev = evaluate_crypto_d1_strategy_candidate_family_review(p)
    assert ev["verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_REJECTED
    )
    assert "forbidden_allow:uses_funding" in ev["reasons"]


def test_63_intraday_allow_flag_rejects():
    p = _valid_packet()
    p["allow_intraday"] = True
    ev = evaluate_crypto_d1_strategy_candidate_family_review(p)
    assert ev["verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_REJECTED
    )
    assert "forbidden_allow:allow_intraday" in ev["reasons"]


def test_64_non_core_asset_rejects():
    p = _valid_packet()
    p["reviewed_universe"] = ["BTC", "ETH", "SOL", "DOGE"]
    ev = evaluate_crypto_d1_strategy_candidate_family_review(p)
    assert ev["verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_REJECTED
    )
    assert "non_core_assets_in_universe" in ev["reasons"]


def test_65_unknown_selected_family_rejects():
    p = _valid_packet()
    p["reviewed_selected_families"] = list(REQUIRED_STRATEGY_FAMILIES) + [
        "MY_SECRET_ALPHA"
    ]
    ev = evaluate_crypto_d1_strategy_candidate_family_review(p)
    assert ev["verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_REJECTED
    )
    assert "unknown_reviewed_strategy_family" in ev["reasons"]


def test_66_unknown_parked_family_rejects():
    p = _valid_packet()
    p["reviewed_selected_families"] = list(REQUIRED_STRATEGY_FAMILIES)
    p["reviewed_parked_families"] = ["MADE_UP_FAMILY"]
    ev = evaluate_crypto_d1_strategy_candidate_family_review(p)
    assert ev["verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_REJECTED
    )
    assert "unknown_parked_strategy_family" in ev["reasons"]


def test_67_single_favorite_with_comparison_rejects():
    p = _valid_packet()
    p["reviewed_selected_families"] = [REQUIRED_STRATEGY_FAMILIES[0]]
    p["reviewed_parked_families"] = list(REQUIRED_STRATEGY_FAMILIES[1:])
    p["reviewed_family_comparison_method"] = "pretend to compare"
    p["reviewed_parked_family_rationale"] = "parked for later"
    ev = evaluate_crypto_d1_strategy_candidate_family_review(p)
    assert ev["verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_REJECTED
    )
    assert "single_family_masquerading_as_full_coverage" in ev["reasons"]


def test_68_regime_only_selection_rejects():
    p = _valid_packet()
    p["reviewed_selected_families"] = ["REGIME_FILTER_LAYER"]
    p["reviewed_parked_families"] = list(REQUIRED_STRATEGY_FAMILIES[:3])
    del p["reviewed_family_comparison_method"]
    p["reviewed_parked_family_rationale"] = "parked for later"
    ev = evaluate_crypto_d1_strategy_candidate_family_review(p)
    assert ev["verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_REJECTED
    )
    assert "regime_filter_layer_not_standalone_strategy" in ev["reasons"]


def test_69_automated_reviewer_rejects():
    for marker in ("bot", "llm", "automation", "autopilot"):
        p = _valid_packet()
        p["reviewer_name_or_id"] = marker
        ev = evaluate_crypto_d1_strategy_candidate_family_review(p)
        assert ev["verdict"] == (
            STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_REJECTED
        ), f"{marker} should reject"


def test_70_automated_reviewer_type_rejects():
    p = _valid_packet()
    p["reviewer_type"] = "agent"
    ev = evaluate_crypto_d1_strategy_candidate_family_review(p)
    assert ev["verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_REJECTED
    )
    assert "automated_reviewer:reviewer_type" in ev["reasons"]


def test_71_granted_capabilities_rejects():
    p = _valid_packet()
    p["grants_capabilities"] = ["live_strategy_selection"]
    ev = evaluate_crypto_d1_strategy_candidate_family_review(p)
    assert ev["verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_REJECTED
    )
    assert "grants_listed:grants_capabilities" in ev["reasons"]


def test_72_live_strategy_selection_flag_rejects():
    p = _valid_packet()
    p["selects_live_strategy"] = True
    ev = evaluate_crypto_d1_strategy_candidate_family_review(p)
    assert ev["verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_REJECTED
    )
    assert "forbidden_allow:selects_live_strategy" in ev["reasons"]


def test_73_real_data_acquisition_flag_rejects():
    p = _valid_packet()
    p["allow_real_data_acquisition"] = True
    ev = evaluate_crypto_d1_strategy_candidate_family_review(p)
    assert ev["verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_REJECTED
    )
    assert "forbidden_allow:allow_real_data_acquisition" in ev["reasons"]


def test_74_data_fetch_flag_rejects():
    p = _valid_packet()
    p["allow_data_fetch"] = True
    ev = evaluate_crypto_d1_strategy_candidate_family_review(p)
    assert ev["verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_REJECTED
    )


def test_75_data_inspection_flag_rejects():
    p = _valid_packet()
    p["allow_data_inspection"] = True
    ev = evaluate_crypto_d1_strategy_candidate_family_review(p)
    assert ev["verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_REJECTED
    )


def test_76_dataset_loading_flag_rejects():
    p = _valid_packet()
    p["allow_dataset_loading"] = True
    ev = evaluate_crypto_d1_strategy_candidate_family_review(p)
    assert ev["verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_REJECTED
    )


def test_77_qa_baseline_backtest_simulation_flags_reject():
    for flag in (
        "allow_qa_run",
        "allow_baseline_run",
        "allow_backtest_run",
        "allow_simulation_run",
    ):
        p = _valid_packet()
        p[flag] = True
        ev = evaluate_crypto_d1_strategy_candidate_family_review(p)
        assert ev["verdict"] == (
            STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_REJECTED
        ), f"{flag} should reject"


def test_78_trade_signal_flag_rejects():
    p = _valid_packet()
    p["generates_trade_signal"] = True
    ev = evaluate_crypto_d1_strategy_candidate_family_review(p)
    assert ev["verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_REJECTED
    )


def test_79_broker_exchange_account_api_order_flags_reject():
    for flag in (
        "allow_broker_exchange",
        "allow_account_access",
        "allow_api_keys",
        "allow_order_capability",
        "allow_paper_live",
    ):
        p = _valid_packet()
        p[flag] = True
        ev = evaluate_crypto_d1_strategy_candidate_family_review(p)
        assert ev["verdict"] == (
            STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_REJECTED
        ), f"{flag} should reject"


def test_80_automation_trigger_flag_rejects():
    p = _valid_packet()
    p["allow_automation_trigger"] = True
    ev = evaluate_crypto_d1_strategy_candidate_family_review(p)
    assert ev["verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_REJECTED
    )


def test_81_runtime_registry_dashboard_write_flags_reject():
    for flag in (
        "allow_runtime_write",
        "allow_registry_write",
        "allow_dashboard_write",
    ):
        p = _valid_packet()
        p[flag] = True
        ev = evaluate_crypto_d1_strategy_candidate_family_review(p)
        assert ev["verdict"] == (
            STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_REJECTED
        ), f"{flag} should reject"


def test_82_rejected_next_gate():
    p = _valid_packet()
    p["allow_real_data_acquisition"] = True
    c = build_crypto_d1_strategy_candidate_family_review_contract(
        _active_signal(), p
    )
    assert c["strategy_candidate_family_review_verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_REJECTED
    )
    assert c["next_gate"] == (
        NEXT_GATE_CRYPTO_D1_STRATEGY_CANDIDATE_FAMILY_REVIEW_REJECTED
    )


# --- 7: PARKED --------------------------------------------------------------

def test_83_park_flag_parks():
    p = _valid_packet()
    p["park"] = True
    ev = evaluate_crypto_d1_strategy_candidate_family_review(p)
    assert ev["verdict"] == STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_PARKED


def test_84_reviewer_decision_parked():
    p = _valid_packet()
    p["reviewer_decision"] = "defer"
    ev = evaluate_crypto_d1_strategy_candidate_family_review(p)
    assert ev["verdict"] == STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_PARKED


def test_85_review_decision_parked():
    p = _valid_packet()
    p["review_decision"] = "parked"
    ev = evaluate_crypto_d1_strategy_candidate_family_review(p)
    assert ev["verdict"] == STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_PARKED


def test_86_deferred_flag_parks():
    p = _valid_packet()
    p["deferred"] = True
    ev = evaluate_crypto_d1_strategy_candidate_family_review(p)
    assert ev["verdict"] == STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_PARKED


def test_87_parked_next_gate():
    p = _valid_packet()
    p["parked"] = True
    c = build_crypto_d1_strategy_candidate_family_review_contract(
        _active_signal(), p
    )
    assert c["strategy_candidate_family_review_verdict"] == (
        STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_PARKED
    )
    assert c["next_gate"] == (
        NEXT_GATE_CRYPTO_D1_STRATEGY_CANDIDATE_FAMILY_REVIEW_PARKED
    )


# --- 8: verdict precedence --------------------------------------------------

def test_88_reject_beats_park():
    p = _valid_packet()
    p["park"] = True
    p["allow_real_data_acquisition"] = True
    assert evaluate_crypto_d1_strategy_candidate_family_review(p)[
        "verdict"
    ] == STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_REJECTED


def test_89_reject_beats_missing():
    p = {"allow_qa_run": True}
    assert evaluate_crypto_d1_strategy_candidate_family_review(p)[
        "verdict"
    ] == STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_REJECTED


def test_90_park_beats_missing():
    p = {"park": True}
    assert evaluate_crypto_d1_strategy_candidate_family_review(p)[
        "verdict"
    ] == STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_PARKED


# --- 9: contract metadata / safety ------------------------------------------

def test_91_contract_read_only_and_non_executing():
    c = build_crypto_d1_strategy_candidate_family_review_contract(
        _active_signal(), _valid_packet()
    )
    assert c["read_only"] is True
    assert c["executes"] is False
    assert c["human_approval_required"] is True


def test_92_all_auth_flags_false():
    c = build_crypto_d1_strategy_candidate_family_review_contract(
        _active_signal(), _valid_packet()
    )
    for flag in _AUTH_FLAGS:
        assert c[flag] is False, flag


def test_93_safety_posture_all_false():
    assert STRATEGY_CANDIDATE_FAMILY_REVIEW_SAFETY_POSTURE
    assert all(
        v is False
        for v in STRATEGY_CANDIDATE_FAMILY_REVIEW_SAFETY_POSTURE.values()
    )
    c = build_crypto_d1_strategy_candidate_family_review_contract(
        _active_signal(), _valid_packet()
    )
    assert all(v is False for v in c["safety_posture"].values())


def test_94_remaining_capabilities_blocked_nonempty():
    assert len(REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED) >= 1
    c = build_crypto_d1_strategy_candidate_family_review_contract(
        _active_signal(), _valid_packet()
    )
    assert c["remaining_real_world_capabilities_blocked"] == (
        REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED
    )


def test_95_contract_next_action_and_stage():
    c = build_crypto_d1_strategy_candidate_family_review_contract(
        _active_signal(), _valid_packet()
    )
    assert c["strategy_candidate_family_review_next_required_action"] == (
        STRATEGY_CANDIDATE_FAMILY_REVIEW_NEXT_REQUIRED_ACTION
    )
    assert c["strategy_candidate_family_review_current_stage"] == (
        STRATEGY_CANDIDATE_FAMILY_REVIEW_CURRENT_STAGE
    )


def test_96_contract_stage_and_mode():
    c = build_crypto_d1_strategy_candidate_family_review_contract(
        _active_signal(), _valid_packet()
    )
    assert c["stage"] == (
        "CRYPTO_D1_STRATEGY_CANDIDATE_FAMILY_REVIEW_CONTRACT_ONLY"
    )
    assert c["mode"] == "RESEARCH_ONLY"


def test_97_no_verdict_unlocks_anything():
    for packet in (
        {},
        _valid_packet(),
        {"allow_real_data_acquisition": True},
        {"selects_live_strategy": True},
        {"park": True},
        {"allow_qa_run": True},
        {"allow_backtest_run": True},
        {"triggers_automation": True},
    ):
        c = build_crypto_d1_strategy_candidate_family_review_contract(
            _active_signal(), packet
        )
        assert c["executes"] is False
        assert all(c[flag] is False for flag in _AUTH_FLAGS)
        assert all(v is False for v in c["safety_posture"].values())


def test_98_blocked_capabilities_present():
    c = build_crypto_d1_strategy_candidate_family_review_contract(
        _active_signal(), _valid_packet()
    )
    assert len(c["family_review_blocked_capabilities"]) >= 1
    assert len(c["blocked_capabilities"]) >= 1


def test_99_remaining_blocked_covers_key_capabilities():
    for cap in (
        "real_data_acquisition",
        "qa_run",
        "baseline_run",
        "backtest_run",
        "simulation_run",
        "broker_or_exchange_connection",
        "paper_or_live_trading",
        "automation_trigger",
        "runtime_write",
        "registry_write",
        "dashboard_write",
    ):
        assert cap in REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED


# --- 10: validation ---------------------------------------------------------

def test_100_valid_contract_validates():
    c = build_crypto_d1_strategy_candidate_family_review_contract(
        _active_signal(), _valid_packet()
    )
    assert validate_crypto_d1_strategy_candidate_family_review_contract(c)[
        "valid"
    ]
    assert c["validation"]["valid"] is True


def test_101_tampered_schema_invalidates():
    c = build_crypto_d1_strategy_candidate_family_review_contract(
        _active_signal(), _valid_packet()
    )
    c["schema_version"] = "bogus"
    assert not (
        validate_crypto_d1_strategy_candidate_family_review_contract(c)[
            "valid"
        ]
    )


def test_102_tampered_read_only_invalidates():
    c = build_crypto_d1_strategy_candidate_family_review_contract(
        _active_signal(), _valid_packet()
    )
    c["read_only"] = False
    assert not (
        validate_crypto_d1_strategy_candidate_family_review_contract(c)[
            "valid"
        ]
    )


def test_103_tampered_executes_invalidates():
    c = build_crypto_d1_strategy_candidate_family_review_contract(
        _active_signal(), _valid_packet()
    )
    c["executes"] = True
    assert not (
        validate_crypto_d1_strategy_candidate_family_review_contract(c)[
            "valid"
        ]
    )


def test_104_tampered_auth_flag_invalidates():
    c = build_crypto_d1_strategy_candidate_family_review_contract(
        _active_signal(), _valid_packet()
    )
    c["execution_authorized"] = True
    assert not (
        validate_crypto_d1_strategy_candidate_family_review_contract(c)[
            "valid"
        ]
    )


def test_105_missing_required_field_invalidates():
    c = build_crypto_d1_strategy_candidate_family_review_contract(
        _active_signal(), _valid_packet()
    )
    del c["safety_posture"]
    res = validate_crypto_d1_strategy_candidate_family_review_contract(c)
    assert not res["valid"]
    assert "safety_posture" in res["missing_required_fields"]


def test_106_non_dict_contract_invalid():
    res = validate_crypto_d1_strategy_candidate_family_review_contract("nope")
    assert res["valid"] is False


def test_107_await_contract_still_validates_structurally():
    # An AWAIT (inactive) contract is still a structurally valid template.
    c = build_crypto_d1_strategy_candidate_family_review_contract({}, None)
    assert c["validation"]["valid"] is True


# --- 11: determinism + mutation isolation -----------------------------------

def test_108_evaluate_is_deterministic():
    p = _valid_packet()
    a = evaluate_crypto_d1_strategy_candidate_family_review(p)
    b = evaluate_crypto_d1_strategy_candidate_family_review(p)
    assert a == b


def test_109_build_is_deterministic():
    sig = _active_signal()
    a = build_crypto_d1_strategy_candidate_family_review_contract(
        sig, _valid_packet()
    )
    b = build_crypto_d1_strategy_candidate_family_review_contract(
        sig, _valid_packet()
    )
    assert a == b


def test_110_echoed_packet_is_a_copy():
    p = _valid_packet()
    c = build_crypto_d1_strategy_candidate_family_review_contract(
        _active_signal(), p
    )
    c["evaluated_family_review_packet"]["family_review_packet_id"] = "x"
    assert p["family_review_packet_id"] != "x"


def test_111_safety_posture_copies_independent():
    c1 = build_crypto_d1_strategy_candidate_family_review_contract(
        _active_signal(), _valid_packet()
    )
    c2 = build_crypto_d1_strategy_candidate_family_review_contract(
        _active_signal(), _valid_packet()
    )
    c1["safety_posture"]["acquires_data"] = True
    assert c2["safety_posture"]["acquires_data"] is False
    assert (
        STRATEGY_CANDIDATE_FAMILY_REVIEW_SAFETY_POSTURE["acquires_data"]
        is False
    )


def test_112_evaluate_does_not_mutate_packet():
    p = _valid_packet()
    snapshot = dict(p)
    evaluate_crypto_d1_strategy_candidate_family_review(p)
    assert p == snapshot


# --- 12: render -------------------------------------------------------------

def test_113_render_markdown_nonempty():
    c = build_crypto_d1_strategy_candidate_family_review_contract(
        _active_signal(), _valid_packet()
    )
    md = render_crypto_d1_strategy_candidate_family_review_contract_markdown(c)
    assert isinstance(md, str) and len(md) > 200


def test_114_render_markdown_names_sections():
    c = build_crypto_d1_strategy_candidate_family_review_contract(
        _active_signal(), _valid_packet()
    )
    md = render_crypto_d1_strategy_candidate_family_review_contract_markdown(c)
    assert "Strategy Candidate Family Review Verdict Reasons" in md
    assert "Required Research Scope" in md
    assert "Remaining Real-World Capabilities Blocked" in md
    assert "Mode: RESEARCH_ONLY" in md


def test_115_render_markdown_deterministic():
    c = build_crypto_d1_strategy_candidate_family_review_contract(
        _active_signal(), _valid_packet()
    )
    a = render_crypto_d1_strategy_candidate_family_review_contract_markdown(c)
    b = render_crypto_d1_strategy_candidate_family_review_contract_markdown(c)
    assert a == b


# --- 13: pure stdlib import-root audit --------------------------------------

def test_116_import_roots_are_allowed_only():
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

def test_117_no_forbidden_call_surface():
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

def test_118_commander_2_safety_allowlist_includes_new_paths():
    src = _SAFETY_PATH.read_text(encoding="utf-8")
    assert (
        '"sparta_commander/strategy_factory_crypto_d1_strategy_candidate_'
        'family_review_contract.py"'
    ) in src
    assert (
        '"tests/test_strategy_factory_crypto_d1_strategy_candidate_family_'
        'review_contract.py"'
    ) in src
