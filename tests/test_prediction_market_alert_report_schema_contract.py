"""Tests for the SPARTA PM Factory V1 Alert/Report Schema contract."""

from __future__ import annotations

import ast

import sparta_commander.prediction_market_alert_report_schema_contract as rs
import sparta_commander.prediction_market_cost_settlement_model_contract as cm


def _alert(**overrides):
    record = {
        "alert_id": "pm_alert_0001", "created_at_utc": "2026-06-11T18:00:00Z",
        "market_id": "mkt_123", "event_id": "evt_9",
        "question_label": "Will event X resolve YES by July?",
        "strategy_family": "PM_F1_yes_no_pricing_inefficiency",
        "gross_edge_bps": 500.0, "spread_cost_bps": 30.0, "fee_cost_bps": 20.0,
        "gas_cost_bps": 5.0, "settlement_cost_bps": 10.0,
        "liquidity_penalty_bps": 10.0, "resolution_risk_bps": 15.0,
        "net_edge_bps": 410.0, "verdict": "PASS", "market_status": "open",
        "resolution_date_utc": "2026-07-01T00:00:00Z",
        "provenance_label": "[evidence: staged pm csvs 2026-06-11]",
        "human_action_needed": True, "research_only_not_trade_signal": True,
        "mandatory_disclaimer": rs.MANDATORY_DISCLAIMER,
    }
    record.update(overrides)
    return record


def test_schema_ready_on_real_chain():
    s = rs.build_pm_alert_report_schema()
    assert s["verdict"] == rs.VERDICT_PM_RS_READY
    assert s["blockers"] == []
    assert s["cost_model_verdict"] == cm.VERDICT_PM_MODEL_READY
    assert s["roadmap_seq"] == 4
    assert s["reports_root"] == "reports/prediction_market_factory_v1/"
    assert s["next_required_action"] == "HUMAN_APPROVED_PM_LANE_REVIEW_CONTRACT"


def test_honest_pass_alert_accepted():
    v = rs.validate_pm_alert_record(_alert())
    assert v["acceptable"] is True and v["errors"] == []


def test_watch_and_fail_alerts_accepted_when_honest():
    watch = _alert(gross_edge_bps=100.0, net_edge_bps=10.0, verdict="WATCH")
    assert rs.validate_pm_alert_record(watch)["acceptable"] is True
    fail = _alert(gross_edge_bps=50.0, net_edge_bps=-40.0, verdict="FAIL")
    assert rs.validate_pm_alert_record(fail)["acceptable"] is True


def test_dishonest_pass_refused():
    lying = _alert(gross_edge_bps=50.0, net_edge_bps=-40.0, verdict="PASS")
    v = rs.validate_pm_alert_record(lying)
    assert v["acceptable"] is False
    assert "verdict_disagrees_with_seq3_model_classification" in v["errors"]
    padded = _alert(net_edge_bps=450.0)  # true net is 410
    v2 = rs.validate_pm_alert_record(padded)
    assert "net_edge_does_not_match_cost_stack" in v2["errors"]


def test_trade_language_and_private_fields_refused():
    for bad in ("buy YES now", "guaranteed winning market",
                "go long this outcome", "place order before resolution"):
        v = rs.validate_pm_alert_record(_alert(question_label=bad))
        assert v["acceptable"] is False, bad
        assert any("forbidden_alert_language" in e for e in v["errors"])
    for bad_key in ("wallet_address", "account_balance", "order_id",
                    "api_key", "deposit_tx"):
        v = rs.validate_pm_alert_record(_alert(**{bad_key: "x"}))
        assert v["acceptable"] is False, bad_key
        assert any("forbidden_alert_field" in e for e in v["errors"])


def test_bad_labels_flags_and_disclaimer_refused():
    assert rs.validate_pm_alert_record(_alert(verdict="BUY"))["acceptable"] is False
    assert rs.validate_pm_alert_record(
        _alert(strategy_family="F7_made_up"))["acceptable"] is False
    assert rs.validate_pm_alert_record(
        _alert(market_status="trading"))["acceptable"] is False
    assert rs.validate_pm_alert_record(
        _alert(human_action_needed=False))["acceptable"] is False
    assert rs.validate_pm_alert_record(
        _alert(research_only_not_trade_signal=False))["acceptable"] is False
    assert rs.validate_pm_alert_record(
        _alert(mandatory_disclaimer="trust me"))["acceptable"] is False
    incomplete = _alert(); del incomplete["resolution_risk_bps"]
    assert rs.validate_pm_alert_record(incomplete)["acceptable"] is False
    assert rs.validate_pm_alert_record(None)["acceptable"] is False


def test_gating_blocks_on_bad_upstream():
    assert rs.record_pm_alert_report_schema(None)["verdict"] == (
        rs.VERDICT_PM_RS_BLOCKED)
    model = cm.build_pm_cost_settlement_model()
    model["contains_order_logic"] = True
    s = rs.record_pm_alert_report_schema(model)
    assert "cost_model_invalid" in s["blockers"]
    blocked = cm.record_pm_cost_settlement_model(None)
    s2 = rs.record_pm_alert_report_schema(blocked)
    assert "cost_model_not_ready" in s2["blockers"]


def test_inert_and_gates_locked_on_all_paths():
    for s in (rs.build_pm_alert_report_schema(),
              rs.record_pm_alert_report_schema(None)):
        assert s["alerts_are_research_only_never_trade_signals"] is True
        assert s["schema_writes_no_reports"] is True
        for key in ("executes", "writes_files", "writes_reports", "runs_scanner",
                    "fetches_data", "calls_api", "uses_network",
                    "uses_credentials", "uses_wallet", "contains_order_logic",
                    "starts_scheduler", "promotes_gate",
                    "unlocks_downstream_gate"):
            assert s[key] is False, key
        assert s["paper_trading_gate_locked"] is True
        assert s["micro_live_gate_locked"] is True
        assert s["live_gate_locked"] is True


def test_validate_passes_and_catches_tampering():
    ok = rs.build_pm_alert_report_schema()
    assert rs.validate_pm_alert_report_schema(ok)["valid"] is True
    assert rs.validate_pm_alert_report_schema(
        rs.record_pm_alert_report_schema(None))["valid"] is True
    s1 = rs.build_pm_alert_report_schema()
    s1["alert_verdict_states"] = ["PASS", "WATCH", "FAIL", "BUY"]
    assert rs.validate_pm_alert_report_schema(s1)["valid"] is False
    s2 = rs.build_pm_alert_report_schema()
    s2["forbidden_alert_language"] = [
        t for t in s2["forbidden_alert_language"] if t != "buy"]
    assert rs.validate_pm_alert_report_schema(s2)["valid"] is False
    s3 = rs.build_pm_alert_report_schema()
    s3["verdicts_must_agree_with_seq3_model"] = False
    assert rs.validate_pm_alert_report_schema(s3)["valid"] is False
    s4 = rs.build_pm_alert_report_schema()
    s4["live_gate_locked"] = False
    assert rs.validate_pm_alert_report_schema(s4)["valid"] is False


def test_build_is_deterministic():
    assert rs.build_pm_alert_report_schema() == rs.build_pm_alert_report_schema()


def test_label_action_and_imports_clean():
    assert rs.get_pm_alert_report_schema_label() == rs.PM_RS_LABEL
    assert "READ-ONLY" in rs.PM_RS_LABEL and rs.PM_RS_MODE == "RESEARCH_ONLY"
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in rs.NEXT_REQUIRED_ACTION.upper(), banned
    tree = ast.parse(open(rs.__file__, encoding="utf-8").read())
    banned_mods = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
                   "subprocess", "websockets", "aiohttp", "schedule",
                   "apscheduler", "threading", "asyncio", "time", "telegram",
                   "email", "csv", "pandas", "pathlib", "os", "io", "json"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods)
