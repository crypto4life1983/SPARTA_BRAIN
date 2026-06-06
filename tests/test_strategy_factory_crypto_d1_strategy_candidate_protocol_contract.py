"""Tests for the Crypto-D1 Strategy Candidate Protocol Contract (Block 97).

The module is a PURE, stdlib-only, read-only *paper contract* that VALIDATES
whether a proposed candidate-strategy research plan follows the Crypto-D1
Strategy Candidate Protocol v1 (Block 95). It evaluates the SHAPE of a proposed
plan only -- it acquires/fetches/inspects/loads no data, runs no QA/baseline/
backtest/simulation, produces no trade signal, reaches no broker/exchange/order/
account/API, trades no paper/live, triggers no automation, and writes nothing.

Coverage:
- pure stdlib import-root audit + forbidden-surface audit
- exported constants / schema version / verdict + state / safety posture
- activation rule: AWAIT unless upstream protocol is the expected v1 protocol
- READY only for a fully-specified research-only BTC/ETH/SOL spot D1 plan with
  all four candidate families and every real-world capability blocked
- NEEDS_MORE_INFO for empty / incomplete plans (missing field, missing
  affirmation, missing universe member, missing family)
- REJECTED for any forbidden allow flag, relaxed affirmation, disallowed mode,
  off-scope market type / timeframe, non-core asset, non-protocol family,
  single-favorite family masquerading as a comparison, automated decider,
  granted authority
- PARKED when an operator explicitly parks/defers
- verdict precedence: REJECTED > PARKED > NEEDS_MORE_INFO > READY; AWAIT first
- verdict -> next_gate mapping in build_*
- validation valid for a real contract, invalid when tampered
- deterministic repeated calls; mutation-isolated copies
- read_only True, executes False, human_approval_required True, auth all False
- scope mirrors the protocol (universe/market/timeframe/families)
- render markdown is non-empty and names key sections
- commander_2_safety allowlist includes the new module + test paths
"""

from __future__ import annotations

import ast
import pathlib

from sparta_commander.strategy_factory_crypto_d1_next_research_protocol import (
    get_protocol,
)
from sparta_commander.strategy_factory_crypto_d1_strategy_candidate_protocol_contract import (  # noqa: E501
    STRATEGY_CANDIDATE_PROTOCOL_SCHEMA_VERSION,
    DEFAULT_STRATEGY_CANDIDATE_PROTOCOL_LABEL,
    STRATEGY_CANDIDATE_PROTOCOL_STATUS,
    STRATEGY_CANDIDATE_PROTOCOL_SAFETY_POSTURE,
    STRATEGY_CANDIDATE_PROTOCOL_STATE_ACTIVE,
    STRATEGY_CANDIDATE_PROTOCOL_STATE_BLOCKED,
    STRATEGY_CANDIDATE_PROTOCOL_VERDICT_READY,
    STRATEGY_CANDIDATE_PROTOCOL_VERDICT_NEEDS_MORE_INFO,
    STRATEGY_CANDIDATE_PROTOCOL_VERDICT_REJECTED,
    STRATEGY_CANDIDATE_PROTOCOL_VERDICT_PARKED,
    STRATEGY_CANDIDATE_PROTOCOL_VERDICT_AWAIT,
    ALLOWED_STRATEGY_CANDIDATE_PROTOCOL_VERDICTS,
    UPSTREAM_REQUIRED_PROTOCOL_ID,
    UPSTREAM_REQUIRED_PROTOCOL_MODE,
    UPSTREAM_REQUIRED_PROTOCOL_NEXT_ACTION,
    STRATEGY_CANDIDATE_PROTOCOL_NEXT_REQUIRED_ACTION,
    STRATEGY_CANDIDATE_PROTOCOL_CURRENT_STAGE,
    NEXT_GATE_CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_READY,
    NEXT_GATE_CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_FIX_REQUIRED,
    NEXT_GATE_CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_PARKED,
    NEXT_GATE_CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_REJECTED,
    NEXT_GATE_AWAIT_CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_DEFINITION,
    REQUIRED_RESEARCH_UNIVERSE,
    REQUIRED_MARKET_TYPE,
    REQUIRED_TIMEFRAME,
    REQUIRED_STRATEGY_FAMILIES,
    REQUIRED_STRATEGY_CANDIDATE_PROTOCOL_FIELDS,
    STRATEGY_CANDIDATE_PROTOCOL_REQUIRED_TEXT_FIELDS,
    STRATEGY_CANDIDATE_PROTOCOL_REQUIRED_AFFIRMATIONS,
    STRATEGY_CANDIDATE_PROTOCOL_FORBIDDEN_ALLOW_FLAGS,
    ALLOWED_STRATEGY_CANDIDATE_PROTOCOL_MODES,
    AUTOMATED_APPROVAL_MARKERS,
    REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED,
    evaluate_crypto_d1_strategy_candidate_protocol,
    build_crypto_d1_strategy_candidate_protocol_contract,
    validate_crypto_d1_strategy_candidate_protocol_contract,
    render_crypto_d1_strategy_candidate_protocol_contract_markdown,
)

_MODPATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "sparta_commander"
    / "strategy_factory_crypto_d1_strategy_candidate_protocol_contract.py"
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
    """A fully-specified, safe, research-only candidate-plan packet."""
    packet: dict = {}
    for key in STRATEGY_CANDIDATE_PROTOCOL_REQUIRED_TEXT_FIELDS:
        packet[key] = f"value-for-{key}"
    packet["research_universe"] = list(REQUIRED_RESEARCH_UNIVERSE)
    packet["market_type"] = "SPOT"
    packet["timeframe"] = "D1"
    packet["proposed_strategy_families"] = list(REQUIRED_STRATEGY_FAMILIES)
    for flag in STRATEGY_CANDIDATE_PROTOCOL_REQUIRED_AFFIRMATIONS:
        packet[flag] = True
    return packet


def _active_protocol() -> dict:
    """The Block 95 protocol dict the contract activates from."""
    return get_protocol()


# --- 1: schema / identity ---------------------------------------------------

def test_01_schema_version_value():
    assert STRATEGY_CANDIDATE_PROTOCOL_SCHEMA_VERSION == (
        "strategy_factory_crypto_d1_strategy_candidate_protocol_contract.v1"
    )


def test_02_label_and_status_nonempty():
    assert DEFAULT_STRATEGY_CANDIDATE_PROTOCOL_LABEL
    assert STRATEGY_CANDIDATE_PROTOCOL_STATUS.startswith("READ_ONLY")


def test_03_states_distinct():
    assert (
        STRATEGY_CANDIDATE_PROTOCOL_STATE_ACTIVE
        != STRATEGY_CANDIDATE_PROTOCOL_STATE_BLOCKED
    )


def test_04_allowed_verdicts_exact():
    assert ALLOWED_STRATEGY_CANDIDATE_PROTOCOL_VERDICTS == (
        STRATEGY_CANDIDATE_PROTOCOL_VERDICT_READY,
        STRATEGY_CANDIDATE_PROTOCOL_VERDICT_NEEDS_MORE_INFO,
        STRATEGY_CANDIDATE_PROTOCOL_VERDICT_REJECTED,
        STRATEGY_CANDIDATE_PROTOCOL_VERDICT_PARKED,
        STRATEGY_CANDIDATE_PROTOCOL_VERDICT_AWAIT,
    )


def test_05_await_verdict_value():
    assert STRATEGY_CANDIDATE_PROTOCOL_VERDICT_AWAIT == (
        "AWAIT_CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_DEFINITION"
    )


# --- 2: upstream / scope mirrors the protocol -------------------------------

def test_06_upstream_required_protocol_id():
    assert UPSTREAM_REQUIRED_PROTOCOL_ID == (
        "CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_V1"
    )


def test_07_upstream_required_mode_research_only():
    assert UPSTREAM_REQUIRED_PROTOCOL_MODE == "RESEARCH_ONLY"


def test_08_upstream_required_next_action():
    assert UPSTREAM_REQUIRED_PROTOCOL_NEXT_ACTION == (
        "BUILD_CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_CONTRACT"
    )


def test_09_required_universe_btc_eth_sol():
    assert REQUIRED_RESEARCH_UNIVERSE == ("BTC", "ETH", "SOL")


def test_10_required_market_spot_only():
    assert REQUIRED_MARKET_TYPE == "SPOT"


def test_11_required_timeframe_d1_only():
    assert REQUIRED_TIMEFRAME == "D1"


def test_12_required_families_all_four():
    assert REQUIRED_STRATEGY_FAMILIES == _EXPECTED_FAMILIES


def test_13_required_fields_text_plus_affirmations():
    assert REQUIRED_STRATEGY_CANDIDATE_PROTOCOL_FIELDS == (
        STRATEGY_CANDIDATE_PROTOCOL_REQUIRED_TEXT_FIELDS
        + STRATEGY_CANDIDATE_PROTOCOL_REQUIRED_AFFIRMATIONS
    )


def test_14_scope_matches_protocol():
    proto = _active_protocol()
    assert tuple(
        a.upper() for a in proto["research_universe"]
    ) == REQUIRED_RESEARCH_UNIVERSE
    assert proto["market_type"].upper() == REQUIRED_MARKET_TYPE
    assert proto["timeframe"].upper() == REQUIRED_TIMEFRAME
    assert tuple(
        f["family_id"].upper() for f in proto["candidate_strategy_families"]
    ) == REQUIRED_STRATEGY_FAMILIES


# --- 3: activation rule (AWAIT) ---------------------------------------------

def test_15_await_on_missing_protocol():
    c = build_crypto_d1_strategy_candidate_protocol_contract(None, None)
    assert c["strategy_candidate_protocol_verdict"] == (
        STRATEGY_CANDIDATE_PROTOCOL_VERDICT_AWAIT
    )
    assert c["crypto_d1_strategy_candidate_protocol_contract_active"] is False


def test_16_await_on_empty_protocol():
    c = build_crypto_d1_strategy_candidate_protocol_contract({}, _valid_packet())
    assert c["strategy_candidate_protocol_verdict"] == (
        STRATEGY_CANDIDATE_PROTOCOL_VERDICT_AWAIT
    )


def test_17_await_on_wrong_protocol_id():
    proto = _active_protocol()
    proto["protocol_id"] = "SOMETHING_ELSE"
    c = build_crypto_d1_strategy_candidate_protocol_contract(
        proto, _valid_packet()
    )
    assert c["strategy_candidate_protocol_verdict"] == (
        STRATEGY_CANDIDATE_PROTOCOL_VERDICT_AWAIT
    )


def test_18_await_on_wrong_mode():
    proto = _active_protocol()
    proto["protocol_mode"] = "LIVE"
    c = build_crypto_d1_strategy_candidate_protocol_contract(
        proto, _valid_packet()
    )
    assert c["strategy_candidate_protocol_verdict"] == (
        STRATEGY_CANDIDATE_PROTOCOL_VERDICT_AWAIT
    )


def test_19_await_on_executable_protocol():
    proto = _active_protocol()
    proto["executes"] = True
    c = build_crypto_d1_strategy_candidate_protocol_contract(
        proto, _valid_packet()
    )
    assert c["strategy_candidate_protocol_verdict"] == (
        STRATEGY_CANDIDATE_PROTOCOL_VERDICT_AWAIT
    )


def test_20_await_on_non_read_only_protocol():
    proto = _active_protocol()
    proto["read_only"] = False
    c = build_crypto_d1_strategy_candidate_protocol_contract(
        proto, _valid_packet()
    )
    assert c["strategy_candidate_protocol_verdict"] == (
        STRATEGY_CANDIDATE_PROTOCOL_VERDICT_AWAIT
    )


def test_21_await_on_wrong_next_action():
    proto = _active_protocol()
    proto["next_required_action"] = "DO_SOMETHING_REAL"
    c = build_crypto_d1_strategy_candidate_protocol_contract(
        proto, _valid_packet()
    )
    assert c["strategy_candidate_protocol_verdict"] == (
        STRATEGY_CANDIDATE_PROTOCOL_VERDICT_AWAIT
    )


def test_22_await_next_gate_when_inactive():
    c = build_crypto_d1_strategy_candidate_protocol_contract({}, None)
    assert c["next_gate"] == (
        NEXT_GATE_AWAIT_CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_DEFINITION
    )


def test_23_contract_active_with_real_protocol():
    c = build_crypto_d1_strategy_candidate_protocol_contract(
        _active_protocol(), _valid_packet()
    )
    assert c["crypto_d1_strategy_candidate_protocol_contract_active"] is True
    assert c["crypto_d1_strategy_candidate_protocol_contract_state"] == (
        STRATEGY_CANDIDATE_PROTOCOL_STATE_ACTIVE
    )


# --- 4: READY ---------------------------------------------------------------

def test_24_ready_for_valid_packet():
    ev = evaluate_crypto_d1_strategy_candidate_protocol(_valid_packet())
    assert ev["verdict"] == STRATEGY_CANDIDATE_PROTOCOL_VERDICT_READY


def test_25_ready_through_build():
    c = build_crypto_d1_strategy_candidate_protocol_contract(
        _active_protocol(), _valid_packet()
    )
    assert c["strategy_candidate_protocol_verdict"] == (
        STRATEGY_CANDIDATE_PROTOCOL_VERDICT_READY
    )
    assert c["next_gate"] == (
        NEXT_GATE_CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_READY
    )


def test_26_ready_accepts_market_spot_only_synonym():
    p = _valid_packet()
    p["market_type"] = "spot_only"
    assert evaluate_crypto_d1_strategy_candidate_protocol(p)["verdict"] == (
        STRATEGY_CANDIDATE_PROTOCOL_VERDICT_READY
    )


def test_27_ready_accepts_daily_timeframe_synonym():
    p = _valid_packet()
    p["timeframe"] = "daily"
    assert evaluate_crypto_d1_strategy_candidate_protocol(p)["verdict"] == (
        STRATEGY_CANDIDATE_PROTOCOL_VERDICT_READY
    )


def test_28_ready_universe_string_form():
    p = _valid_packet()
    p["research_universe"] = "BTC, ETH, SOL"
    assert evaluate_crypto_d1_strategy_candidate_protocol(p)["verdict"] == (
        STRATEGY_CANDIDATE_PROTOCOL_VERDICT_READY
    )


# --- 5: NEEDS_MORE_INFO -----------------------------------------------------

def test_29_empty_packet_needs_more_info():
    ev = evaluate_crypto_d1_strategy_candidate_protocol({})
    assert ev["verdict"] == (
        STRATEGY_CANDIDATE_PROTOCOL_VERDICT_NEEDS_MORE_INFO
    )


def test_30_non_dict_packet_needs_more_info():
    ev = evaluate_crypto_d1_strategy_candidate_protocol("nonsense")
    assert ev["verdict"] == (
        STRATEGY_CANDIDATE_PROTOCOL_VERDICT_NEEDS_MORE_INFO
    )


def test_31_missing_text_field_needs_more_info():
    p = _valid_packet()
    del p["rationale"]
    ev = evaluate_crypto_d1_strategy_candidate_protocol(p)
    assert ev["verdict"] == (
        STRATEGY_CANDIDATE_PROTOCOL_VERDICT_NEEDS_MORE_INFO
    )
    assert "rationale_required" in ev["reasons"]


def test_32_absent_affirmation_needs_more_info():
    p = _valid_packet()
    del p["no_backtest_run"]
    ev = evaluate_crypto_d1_strategy_candidate_protocol(p)
    assert ev["verdict"] == (
        STRATEGY_CANDIDATE_PROTOCOL_VERDICT_NEEDS_MORE_INFO
    )
    assert "no_backtest_run_must_be_affirmed_true" in ev["reasons"]


def test_33_missing_universe_member_needs_more_info():
    p = _valid_packet()
    p["research_universe"] = ["BTC", "ETH"]
    ev = evaluate_crypto_d1_strategy_candidate_protocol(p)
    assert ev["verdict"] == (
        STRATEGY_CANDIDATE_PROTOCOL_VERDICT_NEEDS_MORE_INFO
    )
    assert "research_universe_missing_SOL" in ev["reasons"]


def test_34_missing_one_family_needs_more_info():
    p = _valid_packet()
    p["proposed_strategy_families"] = list(REQUIRED_STRATEGY_FAMILIES[:3])
    ev = evaluate_crypto_d1_strategy_candidate_protocol(p)
    assert ev["verdict"] == (
        STRATEGY_CANDIDATE_PROTOCOL_VERDICT_NEEDS_MORE_INFO
    )
    assert "strategy_family_missing_REGIME_FILTER_LAYER" in ev["reasons"]


def test_35_needs_more_info_next_gate():
    c = build_crypto_d1_strategy_candidate_protocol_contract(
        _active_protocol(), {}
    )
    assert c["strategy_candidate_protocol_verdict"] == (
        STRATEGY_CANDIDATE_PROTOCOL_VERDICT_NEEDS_MORE_INFO
    )
    assert c["next_gate"] == (
        NEXT_GATE_CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_FIX_REQUIRED
    )


# --- 6: REJECTED ------------------------------------------------------------

def test_36_every_forbidden_allow_flag_rejects():
    for flag in STRATEGY_CANDIDATE_PROTOCOL_FORBIDDEN_ALLOW_FLAGS:
        p = _valid_packet()
        p[flag] = True
        ev = evaluate_crypto_d1_strategy_candidate_protocol(p)
        assert ev["verdict"] == (
            STRATEGY_CANDIDATE_PROTOCOL_VERDICT_REJECTED
        ), f"{flag} should reject"
        assert f"forbidden_allow:{flag}" in ev["reasons"]


def test_37_relaxed_affirmation_rejects():
    p = _valid_packet()
    p["no_real_data_acquisition"] = False
    ev = evaluate_crypto_d1_strategy_candidate_protocol(p)
    assert ev["verdict"] == STRATEGY_CANDIDATE_PROTOCOL_VERDICT_REJECTED
    assert "affirmation_relaxed:no_real_data_acquisition" in ev["reasons"]


def test_38_disallowed_mode_rejects():
    p = _valid_packet()
    p["mode"] = "live_trading"
    ev = evaluate_crypto_d1_strategy_candidate_protocol(p)
    assert ev["verdict"] == STRATEGY_CANDIDATE_PROTOCOL_VERDICT_REJECTED
    assert "disallowed_mode" in ev["reasons"]


def test_39_non_spot_market_rejects():
    for mt in ("perp", "perpetual", "futures", "margin", "funding"):
        p = _valid_packet()
        p["market_type"] = mt
        ev = evaluate_crypto_d1_strategy_candidate_protocol(p)
        assert ev["verdict"] == (
            STRATEGY_CANDIDATE_PROTOCOL_VERDICT_REJECTED
        ), f"{mt} should reject"
        assert "disallowed_market_type" in ev["reasons"]


def test_40_intraday_timeframe_rejects():
    for tf in ("1h", "15m", "4h", "5m", "h1"):
        p = _valid_packet()
        p["timeframe"] = tf
        ev = evaluate_crypto_d1_strategy_candidate_protocol(p)
        assert ev["verdict"] == (
            STRATEGY_CANDIDATE_PROTOCOL_VERDICT_REJECTED
        ), f"{tf} should reject"
        assert "disallowed_timeframe" in ev["reasons"]


def test_41_non_core_asset_rejects():
    p = _valid_packet()
    p["research_universe"] = ["BTC", "ETH", "SOL", "DOGE"]
    ev = evaluate_crypto_d1_strategy_candidate_protocol(p)
    assert ev["verdict"] == STRATEGY_CANDIDATE_PROTOCOL_VERDICT_REJECTED
    assert "non_core_assets_in_universe" in ev["reasons"]


def test_42_non_protocol_family_rejects():
    p = _valid_packet()
    p["proposed_strategy_families"] = list(REQUIRED_STRATEGY_FAMILIES) + [
        "MY_SECRET_ALPHA"
    ]
    ev = evaluate_crypto_d1_strategy_candidate_protocol(p)
    assert ev["verdict"] == STRATEGY_CANDIDATE_PROTOCOL_VERDICT_REJECTED
    assert "non_protocol_strategy_family" in ev["reasons"]


def test_43_single_favorite_with_comparison_rejects():
    p = _valid_packet()
    p["proposed_strategy_families"] = [REQUIRED_STRATEGY_FAMILIES[0]]
    p["family_comparison_method"] = "pretend to compare"
    ev = evaluate_crypto_d1_strategy_candidate_protocol(p)
    assert ev["verdict"] == STRATEGY_CANDIDATE_PROTOCOL_VERDICT_REJECTED
    assert "single_family_masquerading_as_comparison" in ev["reasons"]


def test_44_automated_decider_rejects():
    for marker in ("bot", "llm", "automation", "autopilot"):
        p = _valid_packet()
        p["operator_name_or_id"] = marker
        ev = evaluate_crypto_d1_strategy_candidate_protocol(p)
        assert ev["verdict"] == (
            STRATEGY_CANDIDATE_PROTOCOL_VERDICT_REJECTED
        ), f"{marker} should reject"


def test_45_granted_capabilities_rejects():
    p = _valid_packet()
    p["grants_capabilities"] = ["real_data_acquisition"]
    ev = evaluate_crypto_d1_strategy_candidate_protocol(p)
    assert ev["verdict"] == STRATEGY_CANDIDATE_PROTOCOL_VERDICT_REJECTED
    assert "grants_listed:grants_capabilities" in ev["reasons"]


def test_46_rejected_next_gate():
    p = _valid_packet()
    p["allow_real_data_acquisition"] = True
    c = build_crypto_d1_strategy_candidate_protocol_contract(
        _active_protocol(), p
    )
    assert c["strategy_candidate_protocol_verdict"] == (
        STRATEGY_CANDIDATE_PROTOCOL_VERDICT_REJECTED
    )
    assert c["next_gate"] == (
        NEXT_GATE_CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_REJECTED
    )


# --- 7: PARKED --------------------------------------------------------------

def test_47_park_flag_parks():
    p = _valid_packet()
    p["park"] = True
    ev = evaluate_crypto_d1_strategy_candidate_protocol(p)
    assert ev["verdict"] == STRATEGY_CANDIDATE_PROTOCOL_VERDICT_PARKED


def test_48_operator_decision_parked():
    p = _valid_packet()
    p["operator_decision"] = "defer"
    ev = evaluate_crypto_d1_strategy_candidate_protocol(p)
    assert ev["verdict"] == STRATEGY_CANDIDATE_PROTOCOL_VERDICT_PARKED


def test_49_parked_next_gate():
    p = _valid_packet()
    p["parked"] = True
    c = build_crypto_d1_strategy_candidate_protocol_contract(
        _active_protocol(), p
    )
    assert c["strategy_candidate_protocol_verdict"] == (
        STRATEGY_CANDIDATE_PROTOCOL_VERDICT_PARKED
    )
    assert c["next_gate"] == (
        NEXT_GATE_CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_PARKED
    )


# --- 8: verdict precedence --------------------------------------------------

def test_50_reject_beats_park():
    p = _valid_packet()
    p["park"] = True
    p["allow_real_data_acquisition"] = True
    assert evaluate_crypto_d1_strategy_candidate_protocol(p)["verdict"] == (
        STRATEGY_CANDIDATE_PROTOCOL_VERDICT_REJECTED
    )


def test_51_reject_beats_missing():
    p = {"allow_qa_run": True}
    assert evaluate_crypto_d1_strategy_candidate_protocol(p)["verdict"] == (
        STRATEGY_CANDIDATE_PROTOCOL_VERDICT_REJECTED
    )


def test_52_park_beats_missing():
    p = {"park": True}
    assert evaluate_crypto_d1_strategy_candidate_protocol(p)["verdict"] == (
        STRATEGY_CANDIDATE_PROTOCOL_VERDICT_PARKED
    )


# --- 9: contract metadata / safety ------------------------------------------

def test_53_contract_read_only_and_non_executing():
    c = build_crypto_d1_strategy_candidate_protocol_contract(
        _active_protocol(), _valid_packet()
    )
    assert c["read_only"] is True
    assert c["executes"] is False
    assert c["human_approval_required"] is True


def test_54_all_auth_flags_false():
    c = build_crypto_d1_strategy_candidate_protocol_contract(
        _active_protocol(), _valid_packet()
    )
    for flag in _AUTH_FLAGS:
        assert c[flag] is False, flag


def test_55_safety_posture_all_false():
    assert STRATEGY_CANDIDATE_PROTOCOL_SAFETY_POSTURE
    assert all(
        v is False for v in STRATEGY_CANDIDATE_PROTOCOL_SAFETY_POSTURE.values()
    )
    c = build_crypto_d1_strategy_candidate_protocol_contract(
        _active_protocol(), _valid_packet()
    )
    assert all(v is False for v in c["safety_posture"].values())


def test_56_remaining_capabilities_blocked_nonempty():
    assert len(REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED) >= 1
    c = build_crypto_d1_strategy_candidate_protocol_contract(
        _active_protocol(), _valid_packet()
    )
    assert c["remaining_real_world_capabilities_blocked"] == (
        REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED
    )


def test_57_contract_next_action_and_stage():
    c = build_crypto_d1_strategy_candidate_protocol_contract(
        _active_protocol(), _valid_packet()
    )
    assert c["strategy_candidate_protocol_next_required_action"] == (
        STRATEGY_CANDIDATE_PROTOCOL_NEXT_REQUIRED_ACTION
    )
    assert c["strategy_candidate_protocol_current_stage"] == (
        STRATEGY_CANDIDATE_PROTOCOL_CURRENT_STAGE
    )


def test_58_no_verdict_unlocks_anything():
    for packet in (
        {},
        _valid_packet(),
        {"allow_real_data_acquisition": True},
        {"park": True},
    ):
        c = build_crypto_d1_strategy_candidate_protocol_contract(
            _active_protocol(), packet
        )
        assert c["executes"] is False
        assert all(c[flag] is False for flag in _AUTH_FLAGS)
        assert all(v is False for v in c["safety_posture"].values())


# --- 10: validation ---------------------------------------------------------

def test_59_valid_contract_validates():
    c = build_crypto_d1_strategy_candidate_protocol_contract(
        _active_protocol(), _valid_packet()
    )
    assert validate_crypto_d1_strategy_candidate_protocol_contract(c)["valid"]
    assert c["validation"]["valid"] is True


def test_60_tampered_schema_invalidates():
    c = build_crypto_d1_strategy_candidate_protocol_contract(
        _active_protocol(), _valid_packet()
    )
    c["schema_version"] = "bogus"
    assert not validate_crypto_d1_strategy_candidate_protocol_contract(c)[
        "valid"
    ]


def test_61_tampered_read_only_invalidates():
    c = build_crypto_d1_strategy_candidate_protocol_contract(
        _active_protocol(), _valid_packet()
    )
    c["read_only"] = False
    assert not validate_crypto_d1_strategy_candidate_protocol_contract(c)[
        "valid"
    ]


def test_62_missing_required_field_invalidates():
    c = build_crypto_d1_strategy_candidate_protocol_contract(
        _active_protocol(), _valid_packet()
    )
    del c["safety_posture"]
    res = validate_crypto_d1_strategy_candidate_protocol_contract(c)
    assert not res["valid"]
    assert "safety_posture" in res["missing_required_fields"]


def test_63_non_dict_contract_invalid():
    res = validate_crypto_d1_strategy_candidate_protocol_contract("nope")
    assert res["valid"] is False


# --- 11: determinism + mutation isolation -----------------------------------

def test_64_evaluate_is_deterministic():
    p = _valid_packet()
    a = evaluate_crypto_d1_strategy_candidate_protocol(p)
    b = evaluate_crypto_d1_strategy_candidate_protocol(p)
    assert a == b


def test_65_build_is_deterministic():
    proto = _active_protocol()
    a = build_crypto_d1_strategy_candidate_protocol_contract(
        proto, _valid_packet()
    )
    b = build_crypto_d1_strategy_candidate_protocol_contract(
        proto, _valid_packet()
    )
    assert a == b


def test_66_echoed_packet_is_a_copy():
    p = _valid_packet()
    c = build_crypto_d1_strategy_candidate_protocol_contract(
        _active_protocol(), p
    )
    c["evaluated_candidate_plan_packet"]["candidate_protocol_packet_id"] = "x"
    assert p["candidate_protocol_packet_id"] != "x"


def test_67_safety_posture_copies_independent():
    c1 = build_crypto_d1_strategy_candidate_protocol_contract(
        _active_protocol(), _valid_packet()
    )
    c2 = build_crypto_d1_strategy_candidate_protocol_contract(
        _active_protocol(), _valid_packet()
    )
    c1["safety_posture"]["acquires_data"] = True
    assert c2["safety_posture"]["acquires_data"] is False
    assert STRATEGY_CANDIDATE_PROTOCOL_SAFETY_POSTURE["acquires_data"] is False


# --- 12: render -------------------------------------------------------------

def test_68_render_markdown_nonempty():
    c = build_crypto_d1_strategy_candidate_protocol_contract(
        _active_protocol(), _valid_packet()
    )
    md = render_crypto_d1_strategy_candidate_protocol_contract_markdown(c)
    assert isinstance(md, str) and len(md) > 200


def test_69_render_markdown_names_sections():
    c = build_crypto_d1_strategy_candidate_protocol_contract(
        _active_protocol(), _valid_packet()
    )
    md = render_crypto_d1_strategy_candidate_protocol_contract_markdown(c)
    assert "Strategy Candidate Protocol Verdict Reasons" in md
    assert "Required Research Scope" in md
    assert "Remaining Real-World Capabilities Blocked" in md
    assert "Mode: RESEARCH_ONLY" in md


# --- 13: pure stdlib import-root audit --------------------------------------

def test_70_import_roots_are_allowed_only():
    src = _MODPATH.read_text(encoding="utf-8")
    roots: set[str] = set()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    allowed = {"__future__", "typing", "sparta_commander"}
    assert roots <= allowed, f"unexpected import roots: {sorted(roots - allowed)}"
    for banned in ("os", "sys", "subprocess", "socket", "requests",
                   "urllib", "pathlib", "json", "http", "asyncio",
                   "datetime", "time", "random", "glob", "importlib",
                   "shutil", "io", "ccxt", "freqtrade"):
        assert banned not in roots, f"banned import root present: {banned}"


# --- 14: forbidden-surface audit --------------------------------------------

def test_71_no_forbidden_call_surface():
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

def test_72_commander_2_safety_allowlist_includes_new_paths():
    src = _SAFETY_PATH.read_text(encoding="utf-8")
    assert (
        '"sparta_commander/strategy_factory_crypto_d1_strategy_candidate_'
        'protocol_contract.py"'
    ) in src
    assert (
        '"tests/test_strategy_factory_crypto_d1_strategy_candidate_protocol_'
        'contract.py"'
    ) in src
