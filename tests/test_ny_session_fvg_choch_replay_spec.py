"""Tests for the SPARTA NY-Session FVG+CHOCH Replay Spec."""

from __future__ import annotations

import ast

import sparta_commander.crypto_d1_auto_research_mutable_candidate_asset_spec as ca
import sparta_commander.crypto_d1_auto_research_strategy_optimizer_contract as op
import sparta_commander.ny_session_fvg_choch_detector_spec as dt
import sparta_commander.ny_session_fvg_choch_replay_spec as rp
import sparta_commander.ny_session_fvg_choch_strategy_spec_contract as fs


def _accepted_label():
    return {"detector_status": "SETUP_LABEL_ACCEPTED_FOR_REPLAY_REVIEW",
            "setup_id": "setup_001", "candidate_id": rp.CANDIDATE_ID}


def _request(**overrides):
    request = {"candles_provided": True, "fees_bps": 4.0, "spread_bps": 1.0,
               "slippage_bps": 1.0, "replay_start_time": "2026-06-11T13:30:00Z",
               "replay_end_time": "2026-06-11T17:00:00Z"}
    request.update(overrides)
    return request


def _output(**overrides):
    record = {f: None for f in rp.REPLAY_OUTPUT_FIELDS}
    record.update({"setup_id": "setup_001", "candidate_id": rp.CANDIDATE_ID,
                   "symbol": "BTC", "session_date": "2026-06-11",
                   "direction": "long", "entry_triggered": True,
                   "gross_r": 4.0, "net_r_after_costs": 3.7,
                   "gross_pnl_model": 240.0,
                   "net_pnl_model_after_costs": 222.0,
                   "replay_status": "REPLAY_READY_FOR_LOCKED_SCORER_REVIEW"})
    record.update(overrides)
    return record


def test_replay_spec_ready_and_runner_not_built():
    s = rp.build_ny_fvg_choch_replay_spec()
    assert s["verdict"] == rp.VERDICT_RP_READY
    assert s["blockers"] == []
    assert s["replay_runner_built"] is False
    assert s["runs_replay_now"] is False and s["scores_now"] is False
    assert s["next_required_action"] == "HUMAN_APPROVED_FVG_CHOCH_REPLAY_RUNNER"
    assert rp.validate_ny_fvg_choch_replay_spec(s)["valid"] is True


def test_schemas_and_statuses_closed():
    assert len(rp.REPLAY_INPUT_FIELDS) == 17
    assert len(rp.REPLAY_OUTPUT_FIELDS) == 24
    assert len(rp.REPLAY_STATUSES) == 8
    for needed in ("fees_bps", "spread_bps", "slippage_bps",
                   "proposed_entry_price", "replay_start_time"):
        assert needed in rp.REPLAY_INPUT_FIELDS, needed
    for needed in ("net_r_after_costs", "net_pnl_model_after_costs",
                   "max_adverse_excursion_r", "replay_status",
                   "rejection_reason", "audit_notes"):
        assert needed in rp.REPLAY_OUTPUT_FIELDS, needed
    s = rp.build_ny_fvg_choch_replay_spec()
    s["replay_statuses"].append("REPLAY_AUTO_TRADED")
    assert rp.validate_ny_fvg_choch_replay_spec(s)["valid"] is False


def test_valid_request_blocks_on_runner_not_built():
    r = rp.validate_replay_request(_accepted_label(), _request())
    assert r["status"] == "REPLAY_BLOCKED_REPLAY_RUNNER_NOT_BUILT"
    assert r["request_authorizes_nothing"] is True
    # deterministic
    assert r == rp.validate_replay_request(_accepted_label(), _request())


def test_rejected_detector_labels_cannot_replay():
    for status in ("SETUP_REJECTED_MISSING_CHOCH", "SETUP_REJECTED_AMBIGUOUS",
                   None):
        label = {"detector_status": status}
        r = rp.validate_replay_request(label, _request())
        assert r["status"] == "REPLAY_REJECTED_INVALID_LABEL", status
    assert rp.validate_replay_request(None, _request())["status"] == (
        "REPLAY_REJECTED_INVALID_LABEL")


def test_missing_candles_and_costs_reject():
    r = rp.validate_replay_request(_accepted_label(),
                                   _request(candles_provided=False))
    assert r["status"] == "REPLAY_REJECTED_MISSING_CANDLES"
    for cost in ("fees_bps", "spread_bps", "slippage_bps"):
        bad = _request(); del bad[cost]
        r2 = rp.validate_replay_request(_accepted_label(), bad)
        assert r2["status"] == "REPLAY_REJECTED_COSTS_UNDEFINED", cost
    r3 = rp.validate_replay_request(_accepted_label(), _request(fees_bps=-1))
    assert r3["status"] == "REPLAY_REJECTED_COSTS_UNDEFINED"


def test_forbidden_capability_fields_reject():
    for bad in ("order_id", "api_key", "wallet_address", "account_balance",
                "login_token", "fetch_url", "live_authorized_flag",
                "scorer_patch"):
        r = rp.validate_replay_request(_accepted_label(),
                                       _request(**{bad: "x"}))
        assert r["status"] == "REPLAY_REJECTED_FORBIDDEN_CAPABILITY", bad


def test_net_after_costs_mandatory_and_gross_only_impossible():
    ok = rp.validate_replay_output_record(_output())
    assert ok["acceptable"] is True
    bad = rp.validate_replay_output_record(_output(net_r_after_costs=None))
    assert bad["acceptable"] is False
    assert "net_after_costs_mandatory_for_scorer_review" in bad["errors"]
    bad2 = rp.validate_replay_output_record(
        _output(net_pnl_model_after_costs=None))
    assert "net_pnl_after_costs_mandatory" in bad2["errors"]
    bad3 = rp.validate_replay_output_record(
        _output(gross_only_pass_claim=True))
    assert "gross_only_pass_claims_impossible" in bad3["errors"]
    incomplete = _output(); del incomplete["audit_notes"]
    assert rp.validate_replay_output_record(incomplete)["acceptable"] is False
    assert rp.validate_replay_output_record(None)["acceptable"] is False


def test_replay_cannot_fetch_trade_score_or_unlock():
    s = rp.build_ny_fvg_choch_replay_spec()
    for key in ("fetches_data", "uses_network", "calls_api", "executes",
                "contains_order_logic", "connects_broker", "connects_exchange",
                "uses_credentials", "uses_wallet", "scores_now",
                "runs_replay_now", "promotes_gate", "unlocks_downstream_gate"):
        assert s[key] is False, key
    assert s["paper_trading_gate_locked"] is True
    assert s["micro_live_gate_locked"] is True
    assert s["live_gate_locked"] is True
    joined = " ".join(s["forbidden"])
    for must in ("live_trading", "paper_trading_authorization",
                 "order_placement", "broker_or_exchange_api_calls",
                 "credential_access", "network_calls", "data_fetching",
                 "modifying_locked_scorer", "auto_promotion",
                 "unlocking_gates", "hiding_rejected_replays"):
        assert must in joined, must


def test_upstream_stack_and_pm_lane_untouched():
    assert op.build_optimizer_contract()["verdict"] == (
        op.VERDICT_OPT_CONTRACT_READY)
    assert ca.build_mutable_candidate_asset_spec()["verdict"] == (
        ca.VERDICT_CA_SPEC_READY)
    assert fs.build_ny_fvg_choch_strategy_spec()["verdict"] == (
        fs.VERDICT_FS_READY)
    assert dt.build_ny_fvg_choch_detector_spec()["verdict"] == (
        dt.VERDICT_DET_READY)
    from sparta_commander.strategy_factory_mission_flow_status import (
        LATEST_COMPLETED_PM_LANE_CHAIN)
    assert "Research Only" in LATEST_COMPLETED_PM_LANE_CHAIN


def test_validate_catches_tampering():
    s1 = rp.build_ny_fvg_choch_replay_spec()
    s1["replay_runner_built"] = True
    assert rp.validate_ny_fvg_choch_replay_spec(s1)["valid"] is False
    s2 = rp.build_ny_fvg_choch_replay_spec()
    s2["net_after_costs_mandatory"] = False
    assert rp.validate_ny_fvg_choch_replay_spec(s2)["valid"] is False
    s3 = rp.build_ny_fvg_choch_replay_spec()
    s3["forbidden"] = s3["forbidden"][:3]
    assert rp.validate_ny_fvg_choch_replay_spec(s3)["valid"] is False
    s4 = rp.build_ny_fvg_choch_replay_spec()
    s4["live_gate_locked"] = False
    assert rp.validate_ny_fvg_choch_replay_spec(s4)["valid"] is False


def test_label_action_and_imports_clean():
    assert rp.get_ny_fvg_choch_replay_spec_label() == rp.RP_LABEL
    assert "READ-ONLY" in rp.RP_LABEL and rp.RP_MODE == "RESEARCH_ONLY"
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in rp.NEXT_REQUIRED_ACTION.upper(), banned
    tree = ast.parse(open(rp.__file__, encoding="utf-8").read())
    banned_mods = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
                   "subprocess", "websockets", "aiohttp", "schedule",
                   "apscheduler", "threading", "asyncio", "time", "telegram",
                   "email", "csv", "pandas", "pathlib", "os", "io", "json"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods)
