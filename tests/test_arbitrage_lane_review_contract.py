"""Tests for the SPARTA Arbitrage Factory V1 Lane Review Contract (READ-ONLY).

Everything here is pure and in-memory; no network, no credentials, no API call, no
exchange connection, no staged-file read, no persistence, no scanner, no scheduler,
no gate is unlocked. Acceptance means lane coherence only -- never a scanner
authorization."""

from __future__ import annotations

import ast

import sparta_commander.arbitrage_alert_report_schema_contract as rs
import sparta_commander.arbitrage_data_contract as dc
import sparta_commander.arbitrage_factory_v1_research_readiness_contract as ar
import sparta_commander.arbitrage_fee_slippage_model_contract as fm
import sparta_commander.arbitrage_lane_review_contract as lr
import sparta_commander.arbitrage_scanner_spec_contract as sp


def _chain():
    readiness = ar.build_arbitrage_factory_v1_readiness()
    spec = sp.record_arbitrage_scanner_spec(readiness)
    contract = dc.record_arbitrage_data_contract(spec)
    model = fm.record_arbitrage_fee_slippage_model(contract)
    schema = rs.record_arbitrage_alert_report_schema(model)
    return readiness, spec, contract, model, schema


# --------------------------------------------------------------------------- #
# the coherent lane is ACCEPTED with a full passing checklist
# --------------------------------------------------------------------------- #
def test_real_lane_review_is_accepted():
    r = lr.build_arbitrage_lane_review()
    assert r["verdict"] == lr.VERDICT_LANE_REVIEW_ACCEPTED
    assert r["blockers"] == []
    assert r["lane"] == "arbitrage_factory_v1"
    assert r["roadmap_seq"] == 5
    assert r["next_required_action"] == (
        "HUMAN_APPROVED_LANE_MISSION_FLOW_REGISTRATION")


def test_all_twelve_checks_pass_on_the_real_lane():
    r = lr.build_arbitrage_lane_review()
    assert set(r["checklist_results"]) == set(lr.LANE_REVIEW_CHECKLIST)
    assert all(r["checklist_results"][name] is True
               for name in lr.LANE_REVIEW_CHECKLIST)
    assert len(lr.LANE_REVIEW_CHECKLIST) == 12


def test_seq_verdicts_cover_the_whole_chain():
    r = lr.build_arbitrage_lane_review()
    assert r["seq_verdicts"] == {
        "seq0_readiness": ar.VERDICT_READINESS_READY,
        "seq1_scanner_spec": sp.VERDICT_SPEC_READY,
        "seq2_data_contract": dc.VERDICT_DATA_CONTRACT_READY,
        "seq3_fee_slippage_model": fm.VERDICT_MODEL_READY,
        "seq4_alert_report_schema": rs.VERDICT_REPORT_SCHEMA_READY,
    }


def test_acceptance_is_coherence_only_never_scanner_authorization():
    r = lr.build_arbitrage_lane_review()
    assert r["acceptance_means_lane_coherence_only"] is True
    assert r["acceptance_is_not_a_scanner_authorization"] is True
    assert r["scanner_build_requires_its_own_human_approval"] is True
    assert r["every_future_scanner_run_needs_per_run_human_approval"] is True
    assert r["seq6_registration_requires_its_own_human_approval"] is True


def test_review_is_deterministic():
    assert lr.build_arbitrage_lane_review() == lr.build_arbitrage_lane_review()


def test_review_lane_matches_build_on_real_objects():
    assert lr.review_lane(*_chain()) == lr.build_arbitrage_lane_review()


# --------------------------------------------------------------------------- #
# broken lanes are BLOCKED with named failed checks
# --------------------------------------------------------------------------- #
def test_missing_objects_block():
    r = lr.review_lane(None, None, None, None, None)
    assert r["verdict"] == lr.VERDICT_LANE_REVIEW_BLOCKED
    assert "chain_objects_missing_or_not_dicts" in r["blockers"]


def test_tampered_model_blocks_review():
    readiness, spec, contract, model, schema = _chain()
    model["costs_never_default_to_zero"] = False
    r = lr.review_lane(readiness, spec, contract, model, schema)
    assert r["verdict"] == lr.VERDICT_LANE_REVIEW_BLOCKED
    assert "check_failed:seq3_fee_slippage_model_ready_and_valid" in r["blockers"]


def test_tampered_schema_blocks_review():
    readiness, spec, contract, model, schema = _chain()
    schema["verdicts_must_agree_with_seq3_model"] = False
    r = lr.review_lane(readiness, spec, contract, model, schema)
    assert r["verdict"] == lr.VERDICT_LANE_REVIEW_BLOCKED
    assert ("check_failed:seq4_alert_report_schema_ready_and_valid"
            in r["blockers"])


def test_blocked_chain_objects_block_review():
    readiness = ar.build_arbitrage_factory_v1_readiness()
    blocked_spec = sp.record_arbitrage_scanner_spec(None)
    blocked_contract = dc.record_arbitrage_data_contract(blocked_spec)
    blocked_model = fm.record_arbitrage_fee_slippage_model(blocked_contract)
    blocked_schema = rs.record_arbitrage_alert_report_schema(blocked_model)
    r = lr.review_lane(readiness, blocked_spec, blocked_contract,
                       blocked_model, blocked_schema)
    assert r["verdict"] == lr.VERDICT_LANE_REVIEW_BLOCKED
    assert "check_failed:seq1_scanner_spec_ready_and_valid" in r["blockers"]


def test_foreign_chain_fails_rebuild_identity():
    readiness, spec, contract, model, schema = _chain()
    foreign_schema = rs.record_arbitrage_alert_report_schema(model)
    foreign_schema["mandatory_disclaimer"] = rs.MANDATORY_DISCLAIMER  # same
    foreign_schema["reports_root"] = "reports/elsewhere/"
    r = lr.review_lane(readiness, spec, contract, model, foreign_schema)
    assert r["verdict"] == lr.VERDICT_LANE_REVIEW_BLOCKED


# --------------------------------------------------------------------------- #
# posture
# --------------------------------------------------------------------------- #
def test_review_is_inert_on_all_paths():
    reviews = [
        lr.build_arbitrage_lane_review(),
        lr.review_lane(None, None, None, None, None),
    ]
    for r in reviews:
        assert r["review_reads_no_staged_files"] is True
        assert r["review_persists_nothing"] is True
        assert r["human_review_required"] is True
        for key in (
            "executes", "writes_files", "writes_reports", "sends_notifications",
            "runs_scanner", "runs_simulation", "runs_backtest",
            "runs_optimization", "starts_scheduler", "starts_daemon",
            "starts_background_worker", "runs_loop", "fetches_data", "calls_api",
            "connects_broker", "connects_exchange", "uses_real_money",
            "uses_network", "uses_credentials", "contains_order_logic",
            "authorizes_paper_execution", "authorizes_micro_live",
            "authorizes_live_trading", "promotes_gate", "unlocks_downstream_gate",
        ):
            assert r[key] is False, key
        assert r["paper_trading_gate_locked"] is True
        assert r["micro_live_gate_locked"] is True
        assert r["live_gate_locked"] is True


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #
def test_validate_passes_on_accepted_and_blocked():
    assert lr.validate_arbitrage_lane_review(
        lr.build_arbitrage_lane_review())["valid"] is True
    assert lr.validate_arbitrage_lane_review(
        lr.review_lane(None, None, None, None, None))["valid"] is True


def test_validate_rejects_accepted_with_failed_or_missing_check():
    r = lr.build_arbitrage_lane_review()
    r["checklist_results"]["constitution_intact_alerts_only_execution_absent"] = False
    v = lr.validate_arbitrage_lane_review(r)
    assert v["valid"] is False
    assert "accepted_with_failed_check" in v["errors"]
    r2 = lr.build_arbitrage_lane_review()
    del r2["checklist_results"]["reports_root_aligned_between_spec_and_schema"]
    v2 = lr.validate_arbitrage_lane_review(r2)
    assert v2["valid"] is False
    assert "accepted_without_full_checklist" in v2["errors"]


def test_validate_rejects_authorization_claims():
    r = lr.build_arbitrage_lane_review()
    r["acceptance_is_not_a_scanner_authorization"] = False
    v = lr.validate_arbitrage_lane_review(r)
    assert v["valid"] is False
    assert "acceptance_claims_scanner_authorization" in v["errors"]
    r2 = lr.build_arbitrage_lane_review()
    r2["every_future_scanner_run_needs_per_run_human_approval"] = False
    v2 = lr.validate_arbitrage_lane_review(r2)
    assert v2["valid"] is False
    assert "per_run_approval_dropped" in v2["errors"]
    r3 = lr.build_arbitrage_lane_review()
    r3["seq6_registration_requires_its_own_human_approval"] = False
    v3 = lr.validate_arbitrage_lane_review(r3)
    assert v3["valid"] is False
    assert "seq6_approval_dropped" in v3["errors"]


def test_validate_rejects_tampered_checklist():
    r = lr.build_arbitrage_lane_review()
    r["checklist"] = r["checklist"][:5]
    v = lr.validate_arbitrage_lane_review(r)
    assert v["valid"] is False
    assert "checklist_tampered" in v["errors"]


def test_validate_rejects_unlocked_gate_or_capability():
    r = lr.build_arbitrage_lane_review()
    r["micro_live_gate_locked"] = False
    v = lr.validate_arbitrage_lane_review(r)
    assert v["valid"] is False
    assert any("gate_not_locked:micro_live_gate_locked" in e for e in v["errors"])
    r2 = lr.build_arbitrage_lane_review()
    r2["runs_scanner"] = True
    v2 = lr.validate_arbitrage_lane_review(r2)
    assert v2["valid"] is False
    assert any("capability_not_false:runs_scanner" in e for e in v2["errors"])


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #
def test_render_markdown_accepted_and_blocked():
    md = lr.render_arbitrage_lane_review_markdown(lr.build_arbitrage_lane_review())
    assert md.startswith("# SPARTA Arbitrage Factory V1 Lane Review (REVIEW ONLY)")
    assert "lane coherence ONLY" in md
    assert "NOT a scanner" in md
    assert "[PASS]" in md and "[FAIL]" not in md
    assert "LOCKED" in md
    md2 = lr.render_arbitrage_lane_review_markdown(
        lr.review_lane(None, None, None, None, None))
    assert "review does not accept the lane" in md2


# --------------------------------------------------------------------------- #
# label / posture / no banned imports
# --------------------------------------------------------------------------- #
def test_label_is_read_only_review_label():
    assert lr.get_arbitrage_lane_review_label() == lr.LANE_REVIEW_LABEL
    assert "READ-ONLY" in lr.LANE_REVIEW_LABEL
    assert "REVIEW ONLY" in lr.LANE_REVIEW_LABEL
    assert lr.LANE_REVIEW_MODE == "RESEARCH_ONLY"


def test_action_carries_no_execution_or_promotion_verbs():
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE", "EXECUTION",
                   "BACKTEST", "BASELINE", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in lr.NEXT_REQUIRED_ACTION.upper(), banned


def test_module_imports_no_network_exchange_or_credential_modules():
    with open(lr.__file__, "r", encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    banned = {"urllib", "requests", "socket", "http", "ftplib", "ccxt", "databento",
              "dotenv", "smtplib", "subprocess", "websocket", "websockets", "aiohttp",
              "schedule", "apscheduler", "threading", "multiprocessing", "asyncio",
              "sched", "time", "telegram", "email", "csv", "sqlite3", "pandas"}
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imported.add(n.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert not (imported & banned)
