"""Tests for the SPARTA Crypto-D1 Auto Research Mutable Candidate Asset Spec."""

from __future__ import annotations

import ast

import sparta_commander.crypto_d1_auto_research_mutable_candidate_asset_spec as ca
import sparta_commander.crypto_d1_auto_research_strategy_optimizer_contract as op


def _asset(extra_fields=None, **overrides):
    fields = {
        "candidate_id": "cand_0001",
        "candidate_family": "trend_continuation_research",
        "hypothesis": "daily momentum persists after volatility compression",
        "symbol_scope": "BTC,ETH,SOL", "timeframe_scope": "D1",
        "entry_rules_text": "research rule text", "exit_rules_text": "rule",
        "risk_rules_text": "rule", "parameters": {"lookback": 20},
        "rationale": "research note", "status": "draft",
    }
    if extra_fields:
        fields.update(extra_fields)
    asset = {
        "fields": fields, "research_only": True,
        "live_trading_authorized": False, "paper_trading_authorized": False,
        "human_review_required": True, "optimizer_may_edit": True,
        "locked_instructions_may_edit": False, "locked_scorer_may_edit": False,
    }
    asset.update(overrides)
    return asset


def test_spec_ready_on_real_chain():
    s = ca.build_mutable_candidate_asset_spec()
    assert s["verdict"] == ca.VERDICT_CA_SPEC_READY
    assert s["blockers"] == []
    assert s["optimizer_contract_verdict"] == op.VERDICT_OPT_CONTRACT_READY
    assert s["next_required_action"] == "HUMAN_APPROVED_NEXT_AUTO_RESEARCH_BLOCK"
    assert ca.validate_mutable_candidate_asset_spec(s)["valid"] is True


def test_allowed_fields_are_the_closed_sixteen():
    assert len(ca.ALLOWED_EDITABLE_FIELDS) == 16
    for f in ("candidate_id", "candidate_family", "hypothesis", "market_scope",
              "symbol_scope", "timeframe_scope", "session_filter",
              "entry_rules_text", "exit_rules_text", "risk_rules_text",
              "parameters", "constraints", "rationale", "lineage", "status",
              "audit_notes"):
        assert f in ca.ALLOWED_EDITABLE_FIELDS, f


def test_valid_candidate_asset_passes():
    r = ca.validate_candidate_asset(_asset())
    assert r["verdict"] == ca.VERDICT_ASSET_ACCEPTED
    assert r["errors"] == []
    assert r["acceptance_promotes_nothing"] is True
    assert r["human_review_required"] is True


def test_wallet_account_login_api_order_live_fields_rejected():
    for bad in ("wallet_address", "account_balance", "login_name", "api_key",
                "broker_endpoint", "exchange_endpoint_url", "order_id",
                "position_size_live", "live_config_path"):
        r = ca.validate_candidate_asset(_asset(extra_fields={bad: "x"}))
        assert r["verdict"] == ca.VERDICT_ASSET_REJECTED, bad
        assert any("forbidden_field" in e for e in r["errors"])


def test_candidate_cannot_modify_locked_scorer_or_instructions():
    r = ca.validate_candidate_asset(_asset(extra_fields={"scorer_patch": "x"}))
    assert r["verdict"] == ca.VERDICT_ASSET_REJECTED
    r2 = ca.validate_candidate_asset(
        _asset(extra_fields={"instructions_override": "x"}))
    assert r2["verdict"] == ca.VERDICT_ASSET_REJECTED
    r3 = ca.validate_candidate_asset(_asset(locked_scorer_may_edit=True))
    assert "asset_claims_scorer_edit_rights" in r3["errors"]
    r4 = ca.validate_candidate_asset(_asset(locked_instructions_may_edit=True))
    assert "asset_claims_instruction_edit_rights" in r4["errors"]


def test_candidate_cannot_authorize_trading_or_hide_or_unlock():
    r = ca.validate_candidate_asset(_asset(live_trading_authorized=True))
    assert "required_flag_wrong:live_trading_authorized" in r["errors"]
    r2 = ca.validate_candidate_asset(_asset(paper_trading_authorized=True))
    assert "required_flag_wrong:paper_trading_authorized" in r2["errors"]
    r3 = ca.validate_candidate_asset(
        _asset(extra_fields={"auto_promote_flag": True}))
    assert r3["verdict"] == ca.VERDICT_ASSET_REJECTED
    r4 = ca.validate_candidate_asset(
        _asset(extra_fields={"delete_rejected_runs": True}))
    assert r4["verdict"] == ca.VERDICT_ASSET_REJECTED
    r5 = ca.validate_candidate_asset(
        _asset(extra_fields={"unlock_paper_gate": True}))
    assert r5["verdict"] == ca.VERDICT_ASSET_REJECTED


def test_unknown_fields_bad_status_and_missing_id_rejected():
    r = ca.validate_candidate_asset(_asset(extra_fields={"magic_field": 1}))
    assert any("field_outside_closed_schema" in e for e in r["errors"])
    r2 = ca.validate_candidate_asset(_asset(extra_fields={"status": "live"}))
    assert any("status_outside_closed_set" in e for e in r2["errors"])
    no_id = _asset(); del no_id["fields"]["candidate_id"]
    r3 = ca.validate_candidate_asset(no_id)
    assert "candidate_id_required" in r3["errors"]
    assert ca.validate_candidate_asset(None)["verdict"] == (
        ca.VERDICT_ASSET_REJECTED)


def test_gating_blocks_on_bad_optimizer_contract():
    assert ca.record_mutable_candidate_asset_spec(None)["verdict"] == (
        ca.VERDICT_CA_SPEC_BLOCKED)
    bad = op.build_optimizer_contract()
    bad["scorer_locked"] = False
    s = ca.record_mutable_candidate_asset_spec(bad)
    assert "optimizer_contract_invalid" in s["blockers"]


def test_inert_gates_locked_and_lanes_untouched():
    s = ca.build_mutable_candidate_asset_spec()
    for key in ("executes", "writes_files", "runs_scanner", "fetches_data",
                "calls_api", "uses_network", "uses_credentials", "uses_wallet",
                "contains_order_logic", "starts_scheduler", "promotes_gate",
                "unlocks_downstream_gate"):
        assert s[key] is False, key
    assert s["paper_trading_gate_locked"] is True
    assert s["micro_live_gate_locked"] is True
    assert s["live_gate_locked"] is True
    assert s["modifies_mission_flow"] is False
    assert s["modifies_pm_lane"] is False
    from sparta_commander.strategy_factory_mission_flow_status import (
        LATEST_COMPLETED_PM_LANE_CHAIN)
    assert "Research Only" in LATEST_COMPLETED_PM_LANE_CHAIN


def test_validate_spec_catches_tampering():
    s1 = ca.build_mutable_candidate_asset_spec()
    s1["allowed_editable_fields"].append("broker_endpoint")
    assert ca.validate_mutable_candidate_asset_spec(s1)["valid"] is False
    s2 = ca.build_mutable_candidate_asset_spec()
    s2["forbidden_field_tokens"] = [
        t for t in s2["forbidden_field_tokens"] if t != "wallet"]
    assert ca.validate_mutable_candidate_asset_spec(s2)["valid"] is False
    s3 = ca.build_mutable_candidate_asset_spec()
    s3["locked_scorer_may_edit"] = True
    assert ca.validate_mutable_candidate_asset_spec(s3)["valid"] is False
    s4 = ca.build_mutable_candidate_asset_spec()
    s4["live_gate_locked"] = False
    assert ca.validate_mutable_candidate_asset_spec(s4)["valid"] is False


def test_no_fvg_choch_in_this_block():
    src = open(ca.__file__, encoding="utf-8").read().lower()
    assert "fvg" not in src and "choch" not in src


def test_label_action_and_imports_clean():
    assert ca.get_mutable_candidate_asset_spec_label() == ca.CA_LABEL
    assert "READ-ONLY" in ca.CA_LABEL and ca.CA_MODE == "RESEARCH_ONLY"
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in ca.NEXT_REQUIRED_ACTION.upper(), banned
    tree = ast.parse(open(ca.__file__, encoding="utf-8").read())
    banned_mods = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
                   "subprocess", "websockets", "aiohttp", "schedule",
                   "apscheduler", "threading", "asyncio", "time", "telegram",
                   "email", "csv", "pandas", "pathlib", "os", "io", "json"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods)
