"""Tests for the SPARTA PM Factory V1 Lane Review contract."""

from __future__ import annotations

import ast

import sparta_commander.prediction_market_factory_v1_lane_review_contract as lr
import sparta_commander.prediction_market_factory_v1_research_readiness_contract as pr
import sparta_commander.prediction_market_scanner_spec_contract as ps
import sparta_commander.prediction_market_data_contract as pd
import sparta_commander.prediction_market_cost_settlement_model_contract as cm
import sparta_commander.prediction_market_alert_report_schema_contract as rs


def _chain():
    readiness = pr.build_prediction_market_factory_v1_readiness()
    spec = ps.record_prediction_market_scanner_spec(readiness)
    data = pd.record_prediction_market_data_contract(spec)
    model = cm.record_pm_cost_settlement_model(data)
    schema = rs.record_pm_alert_report_schema(model)
    return readiness, spec, data, model, schema


def test_real_lane_review_is_accepted_all_checks_pass():
    r = lr.build_pm_lane_review()
    assert r["verdict"] == lr.VERDICT_PM_LANE_REVIEW_ACCEPTED
    assert r["blockers"] == []
    assert r["roadmap_seq"] == 5
    assert len(lr.PM_LANE_REVIEW_CHECKLIST) == 10
    assert all(r["checklist_results"][n] is True
               for n in lr.PM_LANE_REVIEW_CHECKLIST)
    assert r["seq_verdicts"]["seq0_readiness"] == pr.VERDICT_PM_READINESS_READY
    assert r["seq_verdicts"]["seq4_alert_schema"] == rs.VERDICT_PM_RS_READY
    assert r["next_required_action"] == (
        "HUMAN_APPROVED_PM_MISSION_FLOW_REGISTRATION")


def test_acceptance_is_coherence_only_not_authorization():
    r = lr.build_pm_lane_review()
    assert r["acceptance_means_lane_coherence_only"] is True
    assert r["acceptance_is_not_a_scanner_authorization"] is True
    assert r["seq6_registration_requires_its_own_human_approval"] is True
    assert r["modifies_mission_flow"] is False


def test_review_lane_matches_build_and_is_deterministic():
    assert lr.review_pm_lane(*_chain()) == lr.build_pm_lane_review()
    assert lr.build_pm_lane_review() == lr.build_pm_lane_review()


def test_missing_or_tampered_chain_blocks():
    r = lr.review_pm_lane(None, None, None, None, None)
    assert r["verdict"] == lr.VERDICT_PM_LANE_REVIEW_BLOCKED
    assert "chain_objects_missing_or_not_dicts" in r["blockers"]
    readiness, spec, data, model, schema = _chain()
    model["costs_never_default_to_zero"] = False
    r2 = lr.review_pm_lane(readiness, spec, data, model, schema)
    assert r2["verdict"] == lr.VERDICT_PM_LANE_REVIEW_BLOCKED
    assert "check_failed:seq3_cost_model_ready_and_valid" in r2["blockers"]
    readiness2, spec2, data2, model2, schema2 = _chain()
    schema2["verdicts_must_agree_with_seq3_model"] = False
    r3 = lr.review_pm_lane(readiness2, spec2, data2, model2, schema2)
    assert "check_failed:seq4_alert_schema_ready_and_valid" in r3["blockers"]


def test_blocked_upstream_chain_blocks_review():
    readiness = pr.build_prediction_market_factory_v1_readiness()
    blocked_spec = ps.record_prediction_market_scanner_spec(None)
    blocked_data = pd.record_prediction_market_data_contract(blocked_spec)
    blocked_model = cm.record_pm_cost_settlement_model(blocked_data)
    blocked_schema = rs.record_pm_alert_report_schema(blocked_model)
    r = lr.review_pm_lane(readiness, blocked_spec, blocked_data,
                          blocked_model, blocked_schema)
    assert r["verdict"] == lr.VERDICT_PM_LANE_REVIEW_BLOCKED
    assert "check_failed:seq1_scanner_spec_ready_and_valid" in r["blockers"]


def test_inert_and_gates_locked_on_all_paths():
    for r in (lr.build_pm_lane_review(),
              lr.review_pm_lane(None, None, None, None, None)):
        assert r["review_persists_nothing"] is True
        assert r["review_reads_no_staged_files"] is True
        for key in ("executes", "writes_files", "writes_reports", "runs_scanner",
                    "fetches_data", "calls_api", "uses_network",
                    "uses_credentials", "uses_wallet", "contains_order_logic",
                    "starts_scheduler", "promotes_gate",
                    "unlocks_downstream_gate"):
            assert r[key] is False, key
        assert r["paper_trading_gate_locked"] is True
        assert r["micro_live_gate_locked"] is True
        assert r["live_gate_locked"] is True


def test_validate_passes_and_catches_tampering():
    ok = lr.build_pm_lane_review()
    assert lr.validate_pm_lane_review(ok)["valid"] is True
    assert lr.validate_pm_lane_review(
        lr.review_pm_lane(None, None, None, None, None))["valid"] is True
    r1 = lr.build_pm_lane_review()
    r1["checklist_results"]["honesty_rules_intact_model_agreement_and_cost_stack"] = False
    v1 = lr.validate_pm_lane_review(r1)
    assert v1["valid"] is False and "accepted_with_failed_check" in v1["errors"]
    r2 = lr.build_pm_lane_review()
    r2["acceptance_is_not_a_scanner_authorization"] = False
    assert lr.validate_pm_lane_review(r2)["valid"] is False
    r3 = lr.build_pm_lane_review()
    r3["modifies_mission_flow"] = True
    assert lr.validate_pm_lane_review(r3)["valid"] is False
    r4 = lr.build_pm_lane_review()
    r4["live_gate_locked"] = False
    assert lr.validate_pm_lane_review(r4)["valid"] is False


def test_label_action_and_imports_clean():
    assert lr.get_pm_lane_review_label() == lr.PM_LR_LABEL
    assert "READ-ONLY" in lr.PM_LR_LABEL and lr.PM_LR_MODE == "RESEARCH_ONLY"
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in lr.NEXT_REQUIRED_ACTION.upper(), banned
    tree = ast.parse(open(lr.__file__, encoding="utf-8").read())
    banned_mods = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
                   "subprocess", "websockets", "aiohttp", "schedule",
                   "apscheduler", "threading", "asyncio", "time", "telegram",
                   "email", "csv", "pandas", "pathlib", "os", "io", "json"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods)
