"""Tests for the Crypto-D1 Strategy Candidate Research Plan Approval Contract
(Block 107).

Pure stdlib, read-only, side-effect-free. These tests assert the contract records
the separate human approval of the Block 105-reviewed external-bot-evidence
research plan, stays gated behind a clean READY research-plan-review signal pointed
at this approval gate, upholds every external-bot-evidence safety stance, never
authorizes anything real, and never imports or touches anything outside
__future__/typing/sparta_commander.
"""

from __future__ import annotations

import ast
import os

import sparta_commander.strategy_factory_crypto_d1_strategy_candidate_research_plan_approval_contract as m  # noqa: E501

_MODULE_PATH = m.__file__
_TEST_PATH = os.path.abspath(__file__)


def _active_signal() -> dict:
    """A clean, READY Block 105 research-plan-review signal pointed at this gate."""
    return {
        "crypto_d1_strategy_candidate_research_plan_review_contract_active": (
            True
        ),
        "research_plan_review_verdict": (
            m.UPSTREAM_REQUIRED_RESEARCH_PLAN_REVIEW_VERDICT
        ),
        "next_gate": m.UPSTREAM_REQUIRED_RESEARCH_PLAN_REVIEW_NEXT_GATE,
        "mode": m.UPSTREAM_REQUIRED_RESEARCH_PLAN_REVIEW_MODE,
        "read_only": True,
        "executes": False,
    }


def _valid_packet() -> dict:
    """A fully-specified, in-scope, stance-upholding approval packet."""
    p: dict = {}
    for f in m.RESEARCH_PLAN_APPROVAL_REQUIRED_TEXT_FIELDS:
        p[f] = f + "_value"
    p["approval_mode"] = "research_only"
    p["approved_declared_bot_state"] = "safe_observe"
    p["approved_watched_universe"] = ["BTC", "ETH", "SOL", "XRP"]
    p["approver_name_or_id"] = "mahmoud"
    for a in m.RESEARCH_PLAN_APPROVAL_REQUIRED_AFFIRMATIONS:
        p[a] = True
    return p


# --------------------------------------------------------------------------- #
# Identity / constants
# --------------------------------------------------------------------------- #

def test_schema_version_preserved():
    assert m.RESEARCH_PLAN_APPROVAL_SCHEMA_VERSION == (
        "strategy_factory_crypto_d1_strategy_candidate_research_plan_approval_"
        "contract.v1"
    )


def test_label_is_research_plan_approval():
    assert "Research Plan Approval" in m.DEFAULT_RESEARCH_PLAN_APPROVAL_LABEL


def test_status_is_read_only_research_plan_approval():
    assert m.RESEARCH_PLAN_APPROVAL_STATUS == (
        "READ_ONLY_CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_PLAN_APPROVAL_CONTRACT"
    )


def test_market_and_timeframe_scope_from_block_105():
    assert m.REQUIRED_MARKET_TYPE == "SPOT"
    assert m.REQUIRED_TIMEFRAME == "D1"


def test_watched_universe_includes_xrp():
    assert m.WATCHED_UNIVERSE == ("BTC", "ETH", "SOL", "XRP")


def test_asset_stances_cover_all_four_assets():
    assert set(m.ASSET_EVIDENCE_STANCES) == {"BTC", "ETH", "SOL", "XRP"}
    assert m.ASSET_EVIDENCE_STANCES["SOL"] == (
        "MAIN_CANDIDATE_BLOCKED_FROM_EXECUTION"
    )
    assert m.ASSET_EVIDENCE_STANCES["XRP"] == "WATCHLIST_ONLY"
    assert m.ASSET_EVIDENCE_STANCES["BTC"] == "DORMANT_BLOCKED_FROM_EXPANSION"
    assert m.ASSET_EVIDENCE_STANCES["ETH"] == "EARLY_PRESSURE_ONLY"


def test_sync_thresholds_are_60_and_2():
    assert m.MIN_MULTI_ASSET_SYNC_SCORE == 60
    assert m.MIN_SYNCHRONIZED_ASSETS == 2


def test_trade_coordinator_rules_exact():
    assert m.TRADE_COORDINATOR_RULES == (
        "max_one_open_trade_per_symbol",
        "no_same_direction_adds",
        "treat_exchanges_as_same_symbol",
        "block_opposite_direction",
    )


def test_go_state_is_forbidden_value():
    assert "go" in m.FORBIDDEN_BOT_STATE_VALUES
    assert "watch" in m.ALLOWED_BOT_STATE_VALUES
    assert "safe_observe" in m.ALLOWED_BOT_STATE_VALUES


def test_upstream_gating_constants():
    assert m.UPSTREAM_REQUIRED_RESEARCH_PLAN_REVIEW_NEXT_GATE == (
        "CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_PLAN_REVIEW_READY_SEPARATE_HUMAN_"
        "NEXT_STEP_REQUIRED"
    )
    assert m.UPSTREAM_REQUIRED_RESEARCH_PLAN_REVIEW_MODE == "RESEARCH_ONLY"
    assert m.UPSTREAM_REQUIRED_RESEARCH_PLAN_REVIEW_VERDICT == (
        "STRATEGY_CANDIDATE_RESEARCH_PLAN_REVIEW_READY"
    )


def test_verdict_constants_distinct():
    assert len(set(m.ALLOWED_RESEARCH_PLAN_APPROVAL_VERDICTS)) == 5


def test_stage_and_action_match_registry_values():
    assert m.RESEARCH_PLAN_APPROVAL_CURRENT_STAGE == (
        "CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_PLAN_APPROVAL_CONTRACT_REQUIRED"
    )
    assert m.RESEARCH_PLAN_APPROVAL_NEXT_REQUIRED_ACTION == (
        "BUILD_CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_PLAN_APPROVAL_CONTRACT"
    )


# --------------------------------------------------------------------------- #
# Upstream gating (only a clean Block 105 READY-for-this-gate signal activates)
# --------------------------------------------------------------------------- #

def test_inactive_signal_awaits():
    c = m.build_crypto_d1_strategy_candidate_research_plan_approval_contract(
        {}, None
    )
    assert c["research_plan_approval_verdict"] == (
        m.RESEARCH_PLAN_APPROVAL_VERDICT_AWAIT
    )
    assert c[
        "crypto_d1_strategy_candidate_research_plan_approval_contract_active"
    ] is False
    assert c["validation"]["valid"] is True


def test_none_signal_awaits():
    c = m.build_crypto_d1_strategy_candidate_research_plan_approval_contract(
        None, None
    )
    assert c["research_plan_approval_verdict"] == (
        m.RESEARCH_PLAN_APPROVAL_VERDICT_AWAIT
    )


def test_active_signal_activates_and_is_ready():
    c = m.build_crypto_d1_strategy_candidate_research_plan_approval_contract(
        _active_signal(), _valid_packet()
    )
    assert c[
        "crypto_d1_strategy_candidate_research_plan_approval_contract_active"
    ] is True
    assert c["research_plan_approval_verdict"] == (
        m.RESEARCH_PLAN_APPROVAL_VERDICT_READY
    )


def test_dirty_signal_missing_active_flag_awaits():
    sig = _active_signal()
    del sig[
        "crypto_d1_strategy_candidate_research_plan_review_contract_active"
    ]
    c = m.build_crypto_d1_strategy_candidate_research_plan_approval_contract(
        sig, _valid_packet()
    )
    assert c["research_plan_approval_verdict"] == (
        m.RESEARCH_PLAN_APPROVAL_VERDICT_AWAIT
    )


def test_wrong_verdict_awaits():
    sig = _active_signal()
    sig["research_plan_review_verdict"] = "SOMETHING_ELSE"
    c = m.build_crypto_d1_strategy_candidate_research_plan_approval_contract(
        sig, _valid_packet()
    )
    assert c["research_plan_approval_verdict"] == (
        m.RESEARCH_PLAN_APPROVAL_VERDICT_AWAIT
    )


def test_wrong_next_gate_awaits():
    sig = _active_signal()
    sig["next_gate"] = "SOME_OTHER_GATE"
    c = m.build_crypto_d1_strategy_candidate_research_plan_approval_contract(
        sig, _valid_packet()
    )
    assert c["research_plan_approval_verdict"] == (
        m.RESEARCH_PLAN_APPROVAL_VERDICT_AWAIT
    )


def test_wrong_mode_awaits():
    sig = _active_signal()
    sig["mode"] = "EXECUTION"
    c = m.build_crypto_d1_strategy_candidate_research_plan_approval_contract(
        sig, _valid_packet()
    )
    assert c["research_plan_approval_verdict"] == (
        m.RESEARCH_PLAN_APPROVAL_VERDICT_AWAIT
    )


def test_read_only_false_awaits():
    sig = _active_signal()
    sig["read_only"] = False
    c = m.build_crypto_d1_strategy_candidate_research_plan_approval_contract(
        sig, _valid_packet()
    )
    assert c["research_plan_approval_verdict"] == (
        m.RESEARCH_PLAN_APPROVAL_VERDICT_AWAIT
    )


def test_executes_true_awaits():
    sig = _active_signal()
    sig["executes"] = True
    c = m.build_crypto_d1_strategy_candidate_research_plan_approval_contract(
        sig, _valid_packet()
    )
    assert c["research_plan_approval_verdict"] == (
        m.RESEARCH_PLAN_APPROVAL_VERDICT_AWAIT
    )


# --------------------------------------------------------------------------- #
# READY path + completeness
# --------------------------------------------------------------------------- #

def test_valid_packet_is_ready():
    r = m.evaluate_crypto_d1_strategy_candidate_research_plan_approval(
        _valid_packet()
    )
    assert r["verdict"] == m.RESEARCH_PLAN_APPROVAL_VERDICT_READY


def test_empty_packet_needs_more_info():
    r = m.evaluate_crypto_d1_strategy_candidate_research_plan_approval({})
    assert r["verdict"] == m.RESEARCH_PLAN_APPROVAL_VERDICT_NEEDS_MORE_INFO


def test_missing_text_field_needs_more_info():
    p = _valid_packet()
    del p["approval_decision_rationale"]
    r = m.evaluate_crypto_d1_strategy_candidate_research_plan_approval(p)
    assert r["verdict"] == m.RESEARCH_PLAN_APPROVAL_VERDICT_NEEDS_MORE_INFO


def test_missing_affirmation_needs_more_info():
    p = _valid_packet()
    del p["approved_sol_main_candidate_blocked_from_execution"]
    r = m.evaluate_crypto_d1_strategy_candidate_research_plan_approval(p)
    assert r["verdict"] == m.RESEARCH_PLAN_APPROVAL_VERDICT_NEEDS_MORE_INFO


def test_missing_watched_asset_needs_more_info():
    p = _valid_packet()
    p["approved_watched_universe"] = ["BTC", "ETH", "SOL"]
    r = m.evaluate_crypto_d1_strategy_candidate_research_plan_approval(p)
    assert r["verdict"] == m.RESEARCH_PLAN_APPROVAL_VERDICT_NEEDS_MORE_INFO
    assert any("XRP" in x for x in r["reasons"])


# --------------------------------------------------------------------------- #
# Approved bot state must be WATCH / SAFE_OBSERVE, never GO
# --------------------------------------------------------------------------- #

def test_go_approved_bot_state_rejected():
    p = _valid_packet()
    p["approved_declared_bot_state"] = "go"
    r = m.evaluate_crypto_d1_strategy_candidate_research_plan_approval(p)
    assert r["verdict"] == m.RESEARCH_PLAN_APPROVAL_VERDICT_REJECTED
    assert "approved_bot_state_go_not_permitted" in r["reasons"]


def test_live_approved_bot_state_rejected():
    p = _valid_packet()
    p["approved_declared_bot_state"] = "live"
    r = m.evaluate_crypto_d1_strategy_candidate_research_plan_approval(p)
    assert r["verdict"] == m.RESEARCH_PLAN_APPROVAL_VERDICT_REJECTED


def test_unknown_approved_bot_state_rejected():
    p = _valid_packet()
    p["approved_declared_bot_state"] = "turbo"
    r = m.evaluate_crypto_d1_strategy_candidate_research_plan_approval(p)
    assert r["verdict"] == m.RESEARCH_PLAN_APPROVAL_VERDICT_REJECTED
    assert "disallowed_approved_bot_state" in r["reasons"]


def test_watch_approved_bot_state_ready():
    p = _valid_packet()
    p["approved_declared_bot_state"] = "watch"
    r = m.evaluate_crypto_d1_strategy_candidate_research_plan_approval(p)
    assert r["verdict"] == m.RESEARCH_PLAN_APPROVAL_VERDICT_READY


# --------------------------------------------------------------------------- #
# Forbidden allow flags + relaxed affirmations -> REJECTED
# --------------------------------------------------------------------------- #

def test_approve_plan_for_execution_rejected():
    p = _valid_packet()
    p["approve_plan_for_execution"] = True
    r = m.evaluate_crypto_d1_strategy_candidate_research_plan_approval(p)
    assert r["verdict"] == m.RESEARCH_PLAN_APPROVAL_VERDICT_REJECTED


def test_approval_grants_execution_rejected():
    p = _valid_packet()
    p["approval_grants_execution"] = True
    r = m.evaluate_crypto_d1_strategy_candidate_research_plan_approval(p)
    assert r["verdict"] == m.RESEARCH_PLAN_APPROVAL_VERDICT_REJECTED


def test_treat_approval_as_execution_permission_rejected():
    p = _valid_packet()
    p["treat_approval_as_execution_permission"] = True
    r = m.evaluate_crypto_d1_strategy_candidate_research_plan_approval(p)
    assert r["verdict"] == m.RESEARCH_PLAN_APPROVAL_VERDICT_REJECTED


def test_weaken_research_plan_review_rejected():
    p = _valid_packet()
    p["weaken_research_plan_review"] = True
    r = m.evaluate_crypto_d1_strategy_candidate_research_plan_approval(p)
    assert r["verdict"] == m.RESEARCH_PLAN_APPROVAL_VERDICT_REJECTED


def test_relax_research_plan_safety_rejected():
    p = _valid_packet()
    p["relax_research_plan_safety"] = True
    r = m.evaluate_crypto_d1_strategy_candidate_research_plan_approval(p)
    assert r["verdict"] == m.RESEARCH_PLAN_APPROVAL_VERDICT_REJECTED


def test_treat_evidence_as_execution_permission_rejected():
    p = _valid_packet()
    p["treat_evidence_as_execution_permission"] = True
    r = m.evaluate_crypto_d1_strategy_candidate_research_plan_approval(p)
    assert r["verdict"] == m.RESEARCH_PLAN_APPROVAL_VERDICT_REJECTED


def test_allow_sol_execution_rejected():
    p = _valid_packet()
    p["allow_sol_execution"] = True
    r = m.evaluate_crypto_d1_strategy_candidate_research_plan_approval(p)
    assert r["verdict"] == m.RESEARCH_PLAN_APPROVAL_VERDICT_REJECTED


def test_unblock_btc_expansion_rejected():
    p = _valid_packet()
    p["unblock_btc_expansion"] = True
    r = m.evaluate_crypto_d1_strategy_candidate_research_plan_approval(p)
    assert r["verdict"] == m.RESEARCH_PLAN_APPROVAL_VERDICT_REJECTED


def test_change_live_threshold_rejected():
    p = _valid_packet()
    p["change_live_threshold"] = True
    r = m.evaluate_crypto_d1_strategy_candidate_research_plan_approval(p)
    assert r["verdict"] == m.RESEARCH_PLAN_APPROVAL_VERDICT_REJECTED


def test_override_trade_coordinator_rejected():
    p = _valid_packet()
    p["override_trade_coordinator"] = True
    r = m.evaluate_crypto_d1_strategy_candidate_research_plan_approval(p)
    assert r["verdict"] == m.RESEARCH_PLAN_APPROVAL_VERDICT_REJECTED


def test_modify_external_bot_rejected():
    p = _valid_packet()
    p["modify_external_bot"] = True
    r = m.evaluate_crypto_d1_strategy_candidate_research_plan_approval(p)
    assert r["verdict"] == m.RESEARCH_PLAN_APPROVAL_VERDICT_REJECTED


def test_execution_authorized_flag_rejected():
    p = _valid_packet()
    p["execution_authorized"] = True
    r = m.evaluate_crypto_d1_strategy_candidate_research_plan_approval(p)
    assert r["verdict"] == m.RESEARCH_PLAN_APPROVAL_VERDICT_REJECTED


def test_relaxed_no_live_activation_rejected():
    p = _valid_packet()
    p["approved_no_live_activation"] = False
    r = m.evaluate_crypto_d1_strategy_candidate_research_plan_approval(p)
    assert r["verdict"] == m.RESEARCH_PLAN_APPROVAL_VERDICT_REJECTED
    assert any("affirmation_relaxed" in x for x in r["reasons"])


def test_relaxed_sol_blocked_affirmation_rejected():
    p = _valid_packet()
    p["approved_sol_main_candidate_blocked_from_execution"] = False
    r = m.evaluate_crypto_d1_strategy_candidate_research_plan_approval(p)
    assert r["verdict"] == m.RESEARCH_PLAN_APPROVAL_VERDICT_REJECTED


def test_relaxed_approval_research_only_affirmation_rejected():
    p = _valid_packet()
    p["approval_is_research_only_human_approved_for_next_planning_only"] = False
    r = m.evaluate_crypto_d1_strategy_candidate_research_plan_approval(p)
    assert r["verdict"] == m.RESEARCH_PLAN_APPROVAL_VERDICT_REJECTED


# --------------------------------------------------------------------------- #
# Multi-asset sync gate + non-core asset + automated approver + grants
# --------------------------------------------------------------------------- #

def test_market_confirmation_below_score_rejected():
    p = _valid_packet()
    p["approved_claims_market_confirmation"] = True
    p["approved_multi_asset_sync_score"] = 55
    p["approved_synchronized_asset_count"] = 2
    r = m.evaluate_crypto_d1_strategy_candidate_research_plan_approval(p)
    assert r["verdict"] == m.RESEARCH_PLAN_APPROVAL_VERDICT_REJECTED
    assert (
        "approved_market_confirmation_below_multi_asset_sync_threshold"
        in r["reasons"]
    )


def test_market_confirmation_below_asset_count_rejected():
    p = _valid_packet()
    p["approved_claims_market_confirmation"] = True
    p["approved_multi_asset_sync_score"] = 80
    p["approved_synchronized_asset_count"] = 1
    r = m.evaluate_crypto_d1_strategy_candidate_research_plan_approval(p)
    assert r["verdict"] == m.RESEARCH_PLAN_APPROVAL_VERDICT_REJECTED


def test_market_confirmation_meeting_threshold_ready():
    p = _valid_packet()
    p["approved_claims_market_confirmation"] = True
    p["approved_multi_asset_sync_score"] = 60
    p["approved_synchronized_asset_count"] = 2
    r = m.evaluate_crypto_d1_strategy_candidate_research_plan_approval(p)
    assert r["verdict"] == m.RESEARCH_PLAN_APPROVAL_VERDICT_READY


def test_non_core_asset_in_approved_watched_universe_rejected():
    p = _valid_packet()
    p["approved_watched_universe"] = ["BTC", "ETH", "SOL", "XRP", "DOGE"]
    r = m.evaluate_crypto_d1_strategy_candidate_research_plan_approval(p)
    assert r["verdict"] == m.RESEARCH_PLAN_APPROVAL_VERDICT_REJECTED
    assert "non_core_assets_in_approved_watched_universe" in r["reasons"]


def test_automated_approver_rejected():
    p = _valid_packet()
    p["approver_name_or_id"] = "bot"
    r = m.evaluate_crypto_d1_strategy_candidate_research_plan_approval(p)
    assert r["verdict"] == m.RESEARCH_PLAN_APPROVAL_VERDICT_REJECTED


def test_automated_approver_type_rejected():
    p = _valid_packet()
    p["approver_type"] = "ai"
    r = m.evaluate_crypto_d1_strategy_candidate_research_plan_approval(p)
    assert r["verdict"] == m.RESEARCH_PLAN_APPROVAL_VERDICT_REJECTED


def test_granted_capabilities_rejected():
    p = _valid_packet()
    p["grants_capabilities"] = ["execution"]
    r = m.evaluate_crypto_d1_strategy_candidate_research_plan_approval(p)
    assert r["verdict"] == m.RESEARCH_PLAN_APPROVAL_VERDICT_REJECTED


def test_disallowed_mode_rejected():
    p = _valid_packet()
    p["approval_mode"] = "execution"
    r = m.evaluate_crypto_d1_strategy_candidate_research_plan_approval(p)
    assert r["verdict"] == m.RESEARCH_PLAN_APPROVAL_VERDICT_REJECTED


# --------------------------------------------------------------------------- #
# Parking + precedence
# --------------------------------------------------------------------------- #

def test_approver_parks_lane():
    p = _valid_packet()
    p["approval_decision"] = "parked"
    r = m.evaluate_crypto_d1_strategy_candidate_research_plan_approval(p)
    assert r["verdict"] == m.RESEARCH_PLAN_APPROVAL_VERDICT_PARKED


def test_reject_precedes_park():
    p = _valid_packet()
    p["approval_decision"] = "parked"
    p["allow_execution"] = True
    r = m.evaluate_crypto_d1_strategy_candidate_research_plan_approval(p)
    assert r["verdict"] == m.RESEARCH_PLAN_APPROVAL_VERDICT_REJECTED


# --------------------------------------------------------------------------- #
# Build-level safety posture / authorization
# --------------------------------------------------------------------------- #

def test_build_authorization_flags_all_false():
    c = m.build_crypto_d1_strategy_candidate_research_plan_approval_contract(
        _active_signal(), _valid_packet()
    )
    for flag in (
        "approved_for_research",
        "execution_authorized",
        "paper_trading_authorized",
        "live_trading_authorized",
        "data_fetch_authorized",
        "backtest_authorized",
        "promotion_authorized",
    ):
        assert c[flag] is False
    assert c["read_only"] is True
    assert c["executes"] is False
    assert c["human_approval_required"] is True


def test_build_safety_posture_all_false():
    c = m.build_crypto_d1_strategy_candidate_research_plan_approval_contract(
        _active_signal(), _valid_packet()
    )
    assert all(v is False for v in c["safety_posture"].values())
    assert len(c["safety_posture"]) == 24


def test_build_blocks_external_bot_modification():
    c = m.build_crypto_d1_strategy_candidate_research_plan_approval_contract(
        _active_signal(), _valid_packet()
    )
    assert "external_bot_modification" in c["blocked_capabilities"]
    assert "external_bot_repo_write" in c["blocked_capabilities"]


def test_build_returns_fresh_dicts():
    c1 = m.build_crypto_d1_strategy_candidate_research_plan_approval_contract(
        _active_signal(), _valid_packet()
    )
    c2 = m.build_crypto_d1_strategy_candidate_research_plan_approval_contract(
        _active_signal(), _valid_packet()
    )
    assert c1 is not c2
    assert c1["safety_posture"] is not c2["safety_posture"]


def test_build_recognizes_upstream_review_contract():
    c = m.build_crypto_d1_strategy_candidate_research_plan_approval_contract(
        _active_signal(), _valid_packet()
    )
    assert c[
        "crypto_d1_strategy_candidate_research_plan_review_contract_recognized"
    ] is True


# --------------------------------------------------------------------------- #
# Validation + render
# --------------------------------------------------------------------------- #

def test_validate_ready_contract():
    c = m.build_crypto_d1_strategy_candidate_research_plan_approval_contract(
        _active_signal(), _valid_packet()
    )
    v = (
        m
        .validate_crypto_d1_strategy_candidate_research_plan_approval_contract(
            c
        )
    )
    assert v["valid"] is True


def test_validate_rejects_tampered_schema():
    c = m.build_crypto_d1_strategy_candidate_research_plan_approval_contract(
        _active_signal(), _valid_packet()
    )
    c["schema_version"] = "tampered"
    v = (
        m
        .validate_crypto_d1_strategy_candidate_research_plan_approval_contract(
            c
        )
    )
    assert v["valid"] is False


def test_validate_rejects_tampered_posture():
    c = m.build_crypto_d1_strategy_candidate_research_plan_approval_contract(
        _active_signal(), _valid_packet()
    )
    c["safety_posture"]["acquires_data"] = True
    v = (
        m
        .validate_crypto_d1_strategy_candidate_research_plan_approval_contract(
            c
        )
    )
    assert v["valid"] is False


def test_validate_rejects_tampered_watched_universe():
    c = m.build_crypto_d1_strategy_candidate_research_plan_approval_contract(
        _active_signal(), _valid_packet()
    )
    c["watched_universe"] = ("BTC", "ETH")
    v = (
        m
        .validate_crypto_d1_strategy_candidate_research_plan_approval_contract(
            c
        )
    )
    assert v["valid"] is False


def test_render_markdown_non_empty():
    c = m.build_crypto_d1_strategy_candidate_research_plan_approval_contract(
        _active_signal(), _valid_packet()
    )
    md = (
        m
        .render_crypto_d1_strategy_candidate_research_plan_approval_contract_markdown(  # noqa: E501
            c
        )
    )
    assert isinstance(md, str)
    assert "Research Plan Approval" in md
    assert "SOL" in md
    assert "XRP" in md


def test_evaluate_never_raises_on_garbage():
    for junk in (None, 1, "x", [], (), 3.14, True):
        r = m.evaluate_crypto_d1_strategy_candidate_research_plan_approval(junk)
        assert r["verdict"] in m.ALLOWED_RESEARCH_PLAN_APPROVAL_VERDICTS


# --------------------------------------------------------------------------- #
# Purity audits
# --------------------------------------------------------------------------- #

def test_import_root_audit():
    """The module may only import from __future__, typing, sparta_commander."""
    with open(_MODULE_PATH, "r", encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    allowed_roots = {"__future__", "typing", "sparta_commander"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] in allowed_roots, alias.name
        elif isinstance(node, ast.ImportFrom):
            assert node.level == 0
            assert (node.module or "").split(".")[0] in allowed_roots, (
                node.module
            )


def test_forbidden_surface_audit():
    """The module source must not reference I/O, network, or subprocess."""
    with open(_MODULE_PATH, "r", encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    banned = {
        "exec", "eval", "compile", "__import__", "input",
        "socket", "subprocess", "requests", "urllib", "os", "sys",
        "pathlib", "shutil", "time", "random", "datetime",
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id not in banned, node.func.id
        if isinstance(node, ast.Name):
            assert node.id not in (
                "open", "exec", "eval", "compile", "__import__"
            ), node.id


def test_no_external_bot_path_written_in_source():
    """The module must never write or run anything (no file/proc constructs)."""
    with open(_MODULE_PATH, "r", encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            assert node.func.attr not in (
                "write", "writelines", "unlink", "mkdir", "rmdir",
                "system", "popen",
            ), node.func.attr


# --------------------------------------------------------------------------- #
# Commander 2 safety allowlist
# --------------------------------------------------------------------------- #

def test_module_and_test_in_commander_allowlist():
    from sparta_commander import commander_2_safety as safety

    mod_rel = (
        "sparta_commander/"
        "strategy_factory_crypto_d1_strategy_candidate_research_plan_approval_"
        "contract.py"
    )
    test_rel = (
        "tests/"
        "test_strategy_factory_crypto_d1_strategy_candidate_research_plan_"
        "approval_contract.py"
    )
    all_listed = []
    for name in dir(safety):
        value = getattr(safety, name)
        if isinstance(value, (list, tuple)):
            all_listed.extend(str(x) for x in value)
    assert mod_rel in all_listed
    assert test_rel in all_listed
