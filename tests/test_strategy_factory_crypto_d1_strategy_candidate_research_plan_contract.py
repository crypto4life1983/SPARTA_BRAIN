"""Tests for the Crypto-D1 External Bot Evidence Research Plan Contract (Block
103).

Pure stdlib, read-only, side-effect-free. These tests assert the contract
encodes the thirteen external-bot-evidence policy rules, stays gated behind the
Block 101 family-review READY signal, never authorizes anything real, and never
imports or touches anything outside __future__/typing/sparta_commander.
"""

from __future__ import annotations

import ast
import os

import sparta_commander.strategy_factory_crypto_d1_strategy_candidate_research_plan_contract as m  # noqa: E501

_MODULE_PATH = m.__file__
_TEST_PATH = os.path.abspath(__file__)


def _active_signal() -> dict:
    """A clean, READY Block 101 family-review signal."""
    return {
        "crypto_d1_strategy_candidate_family_review_contract_active": True,
        "strategy_candidate_family_review_verdict": (
            m.UPSTREAM_REQUIRED_FAMILY_REVIEW_VERDICT
        ),
        "next_gate": m.UPSTREAM_REQUIRED_FAMILY_REVIEW_NEXT_GATE,
        "mode": m.UPSTREAM_REQUIRED_FAMILY_REVIEW_MODE,
        "read_only": True,
        "executes": False,
    }


def _valid_packet() -> dict:
    """A fully-specified, in-scope, rule-honouring evidence-plan packet."""
    p: dict = {}
    for f in m.BOT_EVIDENCE_RESEARCH_PLAN_REQUIRED_TEXT_FIELDS:
        p[f] = f + "_value"
    p["plan_mode"] = "research_only"
    p["declared_bot_state"] = "safe_observe"
    p["watched_universe"] = ["BTC", "ETH", "SOL", "XRP"]
    p["planner_name_or_id"] = "mahmoud"
    for a in m.BOT_EVIDENCE_RESEARCH_PLAN_REQUIRED_AFFIRMATIONS:
        p[a] = True
    return p


# --------------------------------------------------------------------------- #
# Identity / constants
# --------------------------------------------------------------------------- #

def test_schema_version_preserved():
    assert m.BOT_EVIDENCE_RESEARCH_PLAN_SCHEMA_VERSION == (
        "strategy_factory_crypto_d1_strategy_candidate_research_plan_contract"
        ".v1"
    )


def test_label_is_external_bot_evidence():
    assert "External Bot Evidence" in m.DEFAULT_BOT_EVIDENCE_RESEARCH_PLAN_LABEL


def test_status_is_read_only_bot_evidence():
    assert m.BOT_EVIDENCE_RESEARCH_PLAN_STATUS == (
        "READ_ONLY_CRYPTO_D1_EXTERNAL_BOT_EVIDENCE_RESEARCH_PLAN_CONTRACT"
    )


def test_market_and_timeframe_scope_from_block_101():
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
    assert m.UPSTREAM_REQUIRED_FAMILY_REVIEW_NEXT_GATE == (
        "CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_PLAN_CONTRACT_REQUIRED"
    )
    assert m.UPSTREAM_REQUIRED_FAMILY_REVIEW_MODE == "RESEARCH_ONLY"


# --------------------------------------------------------------------------- #
# Upstream gating (Option 2 — keep Block 101 gating)
# --------------------------------------------------------------------------- #

def test_inactive_signal_awaits():
    c = m.build_crypto_d1_bot_evidence_research_plan_contract({}, None)
    assert c["bot_evidence_research_plan_verdict"] == (
        m.BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_AWAIT
    )
    assert c["crypto_d1_bot_evidence_research_plan_contract_active"] is False
    assert c["validation"]["valid"] is True


def test_none_signal_awaits():
    c = m.build_crypto_d1_bot_evidence_research_plan_contract(None, None)
    assert c["bot_evidence_research_plan_verdict"] == (
        m.BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_AWAIT
    )


def test_active_signal_activates():
    c = m.build_crypto_d1_bot_evidence_research_plan_contract(
        _active_signal(), _valid_packet()
    )
    assert c["crypto_d1_bot_evidence_research_plan_contract_active"] is True
    assert c["bot_evidence_research_plan_verdict"] == (
        m.BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_READY
    )


def test_dirty_signal_missing_active_flag_awaits():
    sig = _active_signal()
    del sig["crypto_d1_strategy_candidate_family_review_contract_active"]
    c = m.build_crypto_d1_bot_evidence_research_plan_contract(
        sig, _valid_packet()
    )
    assert c["bot_evidence_research_plan_verdict"] == (
        m.BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_AWAIT
    )


def test_wrong_verdict_awaits():
    sig = _active_signal()
    sig["strategy_candidate_family_review_verdict"] = "SOMETHING_ELSE"
    c = m.build_crypto_d1_bot_evidence_research_plan_contract(
        sig, _valid_packet()
    )
    assert c["bot_evidence_research_plan_verdict"] == (
        m.BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_AWAIT
    )


def test_wrong_next_gate_awaits():
    sig = _active_signal()
    sig["next_gate"] = "SOME_OTHER_GATE"
    c = m.build_crypto_d1_bot_evidence_research_plan_contract(
        sig, _valid_packet()
    )
    assert c["bot_evidence_research_plan_verdict"] == (
        m.BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_AWAIT
    )


def test_wrong_mode_awaits():
    sig = _active_signal()
    sig["mode"] = "EXECUTION"
    c = m.build_crypto_d1_bot_evidence_research_plan_contract(
        sig, _valid_packet()
    )
    assert c["bot_evidence_research_plan_verdict"] == (
        m.BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_AWAIT
    )


def test_read_only_false_awaits():
    sig = _active_signal()
    sig["read_only"] = False
    c = m.build_crypto_d1_bot_evidence_research_plan_contract(
        sig, _valid_packet()
    )
    assert c["bot_evidence_research_plan_verdict"] == (
        m.BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_AWAIT
    )


def test_executes_true_awaits():
    sig = _active_signal()
    sig["executes"] = True
    c = m.build_crypto_d1_bot_evidence_research_plan_contract(
        sig, _valid_packet()
    )
    assert c["bot_evidence_research_plan_verdict"] == (
        m.BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_AWAIT
    )


# --------------------------------------------------------------------------- #
# READY path + completeness
# --------------------------------------------------------------------------- #

def test_valid_packet_is_ready():
    r = m.evaluate_crypto_d1_bot_evidence_research_plan(_valid_packet())
    assert r["verdict"] == m.BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_READY


def test_empty_packet_needs_more_info():
    r = m.evaluate_crypto_d1_bot_evidence_research_plan({})
    assert r["verdict"] == (
        m.BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_NEEDS_MORE_INFO
    )


def test_missing_text_field_needs_more_info():
    p = _valid_packet()
    del p["evidence_source_description"]
    r = m.evaluate_crypto_d1_bot_evidence_research_plan(p)
    assert r["verdict"] == (
        m.BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_NEEDS_MORE_INFO
    )


def test_missing_affirmation_needs_more_info():
    p = _valid_packet()
    del p["sol_main_candidate_blocked_from_execution"]
    r = m.evaluate_crypto_d1_bot_evidence_research_plan(p)
    assert r["verdict"] == (
        m.BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_NEEDS_MORE_INFO
    )


def test_missing_watched_asset_needs_more_info():
    p = _valid_packet()
    p["watched_universe"] = ["BTC", "ETH", "SOL"]
    r = m.evaluate_crypto_d1_bot_evidence_research_plan(p)
    assert r["verdict"] == (
        m.BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_NEEDS_MORE_INFO
    )
    assert any("XRP" in x for x in r["reasons"])


# --------------------------------------------------------------------------- #
# Rule 1 — bot state must be WATCH / SAFE_OBSERVE, never GO
# --------------------------------------------------------------------------- #

def test_go_bot_state_rejected():
    p = _valid_packet()
    p["declared_bot_state"] = "go"
    r = m.evaluate_crypto_d1_bot_evidence_research_plan(p)
    assert r["verdict"] == m.BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_REJECTED
    assert "bot_state_go_not_permitted" in r["reasons"]


def test_live_bot_state_rejected():
    p = _valid_packet()
    p["declared_bot_state"] = "live"
    r = m.evaluate_crypto_d1_bot_evidence_research_plan(p)
    assert r["verdict"] == m.BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_REJECTED


def test_unknown_bot_state_rejected():
    p = _valid_packet()
    p["declared_bot_state"] = "turbo"
    r = m.evaluate_crypto_d1_bot_evidence_research_plan(p)
    assert r["verdict"] == m.BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_REJECTED
    assert "disallowed_bot_state" in r["reasons"]


def test_watch_bot_state_ready():
    p = _valid_packet()
    p["declared_bot_state"] = "watch"
    r = m.evaluate_crypto_d1_bot_evidence_research_plan(p)
    assert r["verdict"] == m.BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_READY


# --------------------------------------------------------------------------- #
# Rules 2,3,4,13 — evidence/permission separation, promotion gating
# --------------------------------------------------------------------------- #

def test_treat_evidence_as_execution_permission_rejected():
    p = _valid_packet()
    p["treat_evidence_as_execution_permission"] = True
    r = m.evaluate_crypto_d1_bot_evidence_research_plan(p)
    assert r["verdict"] == m.BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_REJECTED


def test_skip_closed_trade_proof_rejected():
    p = _valid_packet()
    p["skip_closed_trade_proof"] = True
    r = m.evaluate_crypto_d1_bot_evidence_research_plan(p)
    assert r["verdict"] == m.BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_REJECTED


def test_allow_strategy_promotion_rejected():
    p = _valid_packet()
    p["allow_strategy_promotion"] = True
    r = m.evaluate_crypto_d1_bot_evidence_research_plan(p)
    assert r["verdict"] == m.BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_REJECTED


def test_allow_paper_expansion_rejected():
    p = _valid_packet()
    p["allow_paper_expansion"] = True
    r = m.evaluate_crypto_d1_bot_evidence_research_plan(p)
    assert r["verdict"] == m.BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_REJECTED


def test_allow_live_activation_rejected():
    p = _valid_packet()
    p["allow_live_activation"] = True
    r = m.evaluate_crypto_d1_bot_evidence_research_plan(p)
    assert r["verdict"] == m.BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_REJECTED


def test_relaxed_no_live_activation_rejected():
    p = _valid_packet()
    p["no_live_activation"] = False
    r = m.evaluate_crypto_d1_bot_evidence_research_plan(p)
    assert r["verdict"] == m.BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_REJECTED
    assert any("affirmation_relaxed" in x for x in r["reasons"])


# --------------------------------------------------------------------------- #
# Rules 5,6,7,8 — per-asset stances
# --------------------------------------------------------------------------- #

def test_allow_sol_execution_rejected():
    p = _valid_packet()
    p["allow_sol_execution"] = True
    r = m.evaluate_crypto_d1_bot_evidence_research_plan(p)
    assert r["verdict"] == m.BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_REJECTED


def test_unblock_btc_expansion_rejected():
    p = _valid_packet()
    p["unblock_btc_expansion"] = True
    r = m.evaluate_crypto_d1_bot_evidence_research_plan(p)
    assert r["verdict"] == m.BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_REJECTED


def test_relaxed_sol_blocked_affirmation_rejected():
    p = _valid_packet()
    p["sol_main_candidate_blocked_from_execution"] = False
    r = m.evaluate_crypto_d1_bot_evidence_research_plan(p)
    assert r["verdict"] == m.BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_REJECTED


def test_non_core_asset_in_watched_universe_rejected():
    p = _valid_packet()
    p["watched_universe"] = ["BTC", "ETH", "SOL", "XRP", "DOGE"]
    r = m.evaluate_crypto_d1_bot_evidence_research_plan(p)
    assert r["verdict"] == m.BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_REJECTED
    assert "non_core_assets_in_watched_universe" in r["reasons"]


# --------------------------------------------------------------------------- #
# Rule 9 — multi-asset sync gate
# --------------------------------------------------------------------------- #

def test_market_confirmation_below_score_rejected():
    p = _valid_packet()
    p["claims_market_confirmation"] = True
    p["claimed_multi_asset_sync_score"] = 55
    p["claimed_synchronized_asset_count"] = 2
    r = m.evaluate_crypto_d1_bot_evidence_research_plan(p)
    assert r["verdict"] == m.BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_REJECTED
    assert (
        "market_confirmation_below_multi_asset_sync_threshold" in r["reasons"]
    )


def test_market_confirmation_below_asset_count_rejected():
    p = _valid_packet()
    p["claims_market_confirmation"] = True
    p["claimed_multi_asset_sync_score"] = 80
    p["claimed_synchronized_asset_count"] = 1
    r = m.evaluate_crypto_d1_bot_evidence_research_plan(p)
    assert r["verdict"] == m.BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_REJECTED


def test_market_confirmation_meeting_threshold_ready():
    p = _valid_packet()
    p["claims_market_confirmation"] = True
    p["claimed_multi_asset_sync_score"] = 60
    p["claimed_synchronized_asset_count"] = 2
    r = m.evaluate_crypto_d1_bot_evidence_research_plan(p)
    assert r["verdict"] == m.BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_READY


def test_bypass_multi_asset_sync_threshold_rejected():
    p = _valid_packet()
    p["bypass_multi_asset_sync_threshold"] = True
    r = m.evaluate_crypto_d1_bot_evidence_research_plan(p)
    assert r["verdict"] == m.BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_REJECTED


# --------------------------------------------------------------------------- #
# Rule 10 — lead-lag / lagged-sync exclusion
# --------------------------------------------------------------------------- #

def test_use_lead_lag_as_confirmation_rejected():
    p = _valid_packet()
    p["use_lead_lag_as_confirmation"] = True
    r = m.evaluate_crypto_d1_bot_evidence_research_plan(p)
    assert r["verdict"] == m.BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_REJECTED


def test_use_lagged_sync_as_confirmation_rejected():
    p = _valid_packet()
    p["use_lagged_sync_as_confirmation"] = True
    r = m.evaluate_crypto_d1_bot_evidence_research_plan(p)
    assert r["verdict"] == m.BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_REJECTED


# --------------------------------------------------------------------------- #
# Rule 11 — ATR thresholds offline only
# --------------------------------------------------------------------------- #

def test_change_live_threshold_rejected():
    p = _valid_packet()
    p["change_live_threshold"] = True
    r = m.evaluate_crypto_d1_bot_evidence_research_plan(p)
    assert r["verdict"] == m.BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_REJECTED


def test_relaxed_no_live_threshold_changes_rejected():
    p = _valid_packet()
    p["no_live_threshold_changes"] = False
    r = m.evaluate_crypto_d1_bot_evidence_research_plan(p)
    assert r["verdict"] == m.BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_REJECTED


# --------------------------------------------------------------------------- #
# Rule 12 — trade-coordinator overrides
# --------------------------------------------------------------------------- #

def test_override_trade_coordinator_rejected():
    p = _valid_packet()
    p["override_trade_coordinator"] = True
    r = m.evaluate_crypto_d1_bot_evidence_research_plan(p)
    assert r["verdict"] == m.BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_REJECTED


def test_allow_opposite_direction_rejected():
    p = _valid_packet()
    p["allow_opposite_direction"] = True
    r = m.evaluate_crypto_d1_bot_evidence_research_plan(p)
    assert r["verdict"] == m.BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_REJECTED


def test_split_exchanges_as_different_symbols_rejected():
    p = _valid_packet()
    p["split_exchanges_as_different_symbols"] = True
    r = m.evaluate_crypto_d1_bot_evidence_research_plan(p)
    assert r["verdict"] == m.BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_REJECTED


# --------------------------------------------------------------------------- #
# External-bot protection + generic dangerous flags
# --------------------------------------------------------------------------- #

def test_modify_external_bot_rejected():
    p = _valid_packet()
    p["modify_external_bot"] = True
    r = m.evaluate_crypto_d1_bot_evidence_research_plan(p)
    assert r["verdict"] == m.BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_REJECTED


def test_write_to_external_bot_repo_rejected():
    p = _valid_packet()
    p["write_to_external_bot_repo"] = True
    r = m.evaluate_crypto_d1_bot_evidence_research_plan(p)
    assert r["verdict"] == m.BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_REJECTED


def test_execution_authorized_flag_rejected():
    p = _valid_packet()
    p["execution_authorized"] = True
    r = m.evaluate_crypto_d1_bot_evidence_research_plan(p)
    assert r["verdict"] == m.BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_REJECTED


def test_disallowed_mode_rejected():
    p = _valid_packet()
    p["plan_mode"] = "execution"
    r = m.evaluate_crypto_d1_bot_evidence_research_plan(p)
    assert r["verdict"] == m.BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_REJECTED


def test_automated_planner_rejected():
    p = _valid_packet()
    p["planner_name_or_id"] = "bot"
    r = m.evaluate_crypto_d1_bot_evidence_research_plan(p)
    assert r["verdict"] == m.BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_REJECTED


def test_granted_capabilities_rejected():
    p = _valid_packet()
    p["grants_capabilities"] = ["execution"]
    r = m.evaluate_crypto_d1_bot_evidence_research_plan(p)
    assert r["verdict"] == m.BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_REJECTED


# --------------------------------------------------------------------------- #
# Parking
# --------------------------------------------------------------------------- #

def test_planner_parks_lane():
    p = _valid_packet()
    p["plan_decision"] = "parked"
    r = m.evaluate_crypto_d1_bot_evidence_research_plan(p)
    assert r["verdict"] == m.BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_PARKED


def test_reject_precedes_park():
    p = _valid_packet()
    p["plan_decision"] = "parked"
    p["allow_execution"] = True
    r = m.evaluate_crypto_d1_bot_evidence_research_plan(p)
    assert r["verdict"] == m.BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_REJECTED


# --------------------------------------------------------------------------- #
# Build-level safety posture / authorization
# --------------------------------------------------------------------------- #

def test_build_authorization_flags_all_false():
    c = m.build_crypto_d1_bot_evidence_research_plan_contract(
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
    c = m.build_crypto_d1_bot_evidence_research_plan_contract(
        _active_signal(), _valid_packet()
    )
    assert all(v is False for v in c["safety_posture"].values())


def test_build_blocks_external_bot_modification():
    c = m.build_crypto_d1_bot_evidence_research_plan_contract(
        _active_signal(), _valid_packet()
    )
    assert "external_bot_modification" in c["blocked_capabilities"]
    assert "external_bot_repo_write" in c["blocked_capabilities"]


def test_build_returns_fresh_dicts():
    c1 = m.build_crypto_d1_bot_evidence_research_plan_contract(
        _active_signal(), _valid_packet()
    )
    c2 = m.build_crypto_d1_bot_evidence_research_plan_contract(
        _active_signal(), _valid_packet()
    )
    assert c1 is not c2
    assert c1["safety_posture"] is not c2["safety_posture"]


# --------------------------------------------------------------------------- #
# Validation + render
# --------------------------------------------------------------------------- #

def test_validate_ready_contract():
    c = m.build_crypto_d1_bot_evidence_research_plan_contract(
        _active_signal(), _valid_packet()
    )
    v = m.validate_crypto_d1_bot_evidence_research_plan_contract(c)
    assert v["valid"] is True


def test_validate_rejects_tampered_schema():
    c = m.build_crypto_d1_bot_evidence_research_plan_contract(
        _active_signal(), _valid_packet()
    )
    c["schema_version"] = "tampered"
    v = m.validate_crypto_d1_bot_evidence_research_plan_contract(c)
    assert v["valid"] is False


def test_validate_rejects_tampered_posture():
    c = m.build_crypto_d1_bot_evidence_research_plan_contract(
        _active_signal(), _valid_packet()
    )
    c["safety_posture"]["acquires_data"] = True
    v = m.validate_crypto_d1_bot_evidence_research_plan_contract(c)
    assert v["valid"] is False


def test_validate_rejects_tampered_watched_universe():
    c = m.build_crypto_d1_bot_evidence_research_plan_contract(
        _active_signal(), _valid_packet()
    )
    c["watched_universe"] = ("BTC", "ETH")
    v = m.validate_crypto_d1_bot_evidence_research_plan_contract(c)
    assert v["valid"] is False


def test_render_markdown_non_empty():
    c = m.build_crypto_d1_bot_evidence_research_plan_contract(
        _active_signal(), _valid_packet()
    )
    md = m.render_crypto_d1_bot_evidence_research_plan_contract_markdown(c)
    assert isinstance(md, str)
    assert "External Bot Evidence" in md
    assert "SOL" in md
    assert "XRP" in md


def test_evaluate_never_raises_on_garbage():
    for junk in (None, 1, "x", [], (), 3.14, True):
        r = m.evaluate_crypto_d1_bot_evidence_research_plan(junk)
        assert r["verdict"] in m.ALLOWED_BOT_EVIDENCE_RESEARCH_PLAN_VERDICTS


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
        "open", "exec", "eval", "compile", "__import__", "input",
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
    """The module must never write to the external obsidian-trade-logger path
    (it may name it only inside string literals / comments for documentation)."""
    with open(_MODULE_PATH, "r", encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    # No file-writing constructs at all.
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
        "strategy_factory_crypto_d1_strategy_candidate_research_plan_contract"
        ".py"
    )
    test_rel = (
        "tests/"
        "test_strategy_factory_crypto_d1_strategy_candidate_research_plan_"
        "contract.py"
    )
    all_listed = []
    for name in dir(safety):
        value = getattr(safety, name)
        if isinstance(value, (list, tuple)):
            all_listed.extend(str(x) for x in value)
    assert mod_rel in all_listed
    assert test_rel in all_listed
