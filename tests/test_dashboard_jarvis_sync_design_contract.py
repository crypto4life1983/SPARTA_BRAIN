"""Tests for the SPARTA Dashboard / JARVIS Sync DESIGN Contract (READ-ONLY).

Everything here is pure and in-memory; no dashboard write, no JARVIS runtime change,
no transport, no network, no credentials, no scheduler, no gate is unlocked. The
contract shapes display-only models from safe report payloads; no control in the
model can trigger work."""

from __future__ import annotations

import ast

import sparta_commander.dashboard_jarvis_sync_design_contract as dj
import sparta_commander.intake_to_orchestrator_adapter_contract as ad
import sparta_commander.research_cycle_scheduler_spec_contract as cy
import sparta_commander.result_notification_reporting_contract as rn
import sparta_commander.strategy_idea_approval_packet_schema_contract as pk
import sparta_commander.strategy_idea_batch_approval_contract as ba
import sparta_commander.strategy_idea_intake_automation_contract as it


def _ready_report(summary="contract tests passed on the research-only chain"):
    packet = pk.generate_approval_packet(ad.adapt_intake_decision(
        it.intake_strategy_idea("funding rate arbitrage research on btc basis")))
    steps = [
        {"seq": 1, "kind": "build_contract_module",
         "description": "build the lane data contract module"},
        {"seq": 2, "kind": "results_review_contract",
         "description": "review contract over the findings"},
    ]
    batch = ba.compose_batch(packet, steps)
    approval = ba.record_human_batch_decision(
        batch, ba.DECISION_APPROVE_BATCH, "Mahmoud")
    spec = cy.build_research_cycle_spec(batch, approval)
    return rn.build_result_report(spec, {
        "result_type": rn.RESULT_TYPE_CYCLE_COMPLETE, "summary": summary})


# --------------------------------------------------------------------------- #
# safe report -> display model
# --------------------------------------------------------------------------- #
def test_ready_report_yields_display_model():
    m = dj.build_sync_display_model(_ready_report())
    assert m["verdict"] == dj.VERDICT_SYNC_DISPLAY_READY
    assert m["blockers"] == []
    assert m["display_id"].startswith("display_")
    assert m["lane"] == it.LANE_ARBITRAGE


def test_dashboard_display_has_safe_fields_and_no_buttons():
    m = dj.build_sync_display_model(_ready_report())
    dash = m["dashboard_display"]
    assert dash["panel_title"] == "Strategy Factory Automation"
    assert "automation chain L1-L6" in dash["chain_state_line"]
    assert dash["next_required_action_display"].startswith("Next required action:")
    assert "human must issue it" in dash["recommendation_display"]
    assert "HUMAN ACTION NEEDED" in dash["human_action_needed_banner"]
    assert dash["display_only"] is True
    assert dash["action_buttons"] == []
    assert dash["buttons_forbidden_by_design"] is True


def test_jarvis_display_is_safe_and_cannot_act():
    m = dj.build_sync_display_model(_ready_report())
    jarv = m["jarvis_display"]
    assert "waiting for your review" in jarv["status_sentence"]
    assert "nothing will move until you decide" in jarv["status_sentence"]
    assert "I cannot act" in jarv["spoken_next_action"]
    assert jarv["contains_no_performance_claims"] is True
    assert jarv["display_only"] is True


def test_automation_chain_rows_cover_all_six_links():
    m = dj.build_sync_display_model(_ready_report())
    rows = m["dashboard_display"]["automation_roadmap_rows"]
    assert [r["link"] for r in rows] == [
        "L1_intake_to_queue_adapter",
        "L2_lane_specific_approval_packet_generator",
        "L3_batch_approval_schema",
        "L4_scheduled_research_cycle_controller",
        "L5_result_notification_reporting_layer",
        "L6_dashboard_jarvis_automation_sync",
    ]
    assert all(r["built"] for r in rows)


def test_display_model_is_deterministic():
    assert dj.build_sync_display_model(_ready_report()) == dj.build_sync_display_model(
        _ready_report())


# --------------------------------------------------------------------------- #
# refusals: unsafe display content
# --------------------------------------------------------------------------- #
def test_forbidden_display_tokens_refuse():
    for bad in ("leverage looks great here",
                "we are long btc on this signal",
                "stop loss hit overnight"):
        m = dj.build_sync_display_model(_ready_report(summary=bad))
        assert m["verdict"] == dj.VERDICT_SYNC_DISPLAY_REFUSED, bad
        assert any("forbidden_display_token" in b for b in m["blockers"])
        assert m["dashboard_display"] is None
        assert m["jarvis_display"] is None


def test_unlabeled_performance_claims_refuse():
    for bad in ("this was profitable", "win rate above 70 percent",
                "guaranteed returns of 5 percent"):
        m = dj.build_sync_display_model(_ready_report(summary=bad))
        assert m["verdict"] == dj.VERDICT_SYNC_DISPLAY_REFUSED, bad
        assert any("unlabeled_performance_claim" in b for b in m["blockers"])


def test_evidence_labeled_performance_text_is_allowed():
    m = dj.build_sync_display_model(_ready_report(
        summary="replay summary [evidence: rc2 report] mean return figures recorded"))
    assert m["verdict"] == dj.VERDICT_SYNC_DISPLAY_READY
    m2 = dj.build_sync_display_model(_ready_report(
        summary="[evidence: rc1 oos report] in-sample profit figures degraded oos"))
    assert m2["verdict"] == dj.VERDICT_SYNC_DISPLAY_READY


def test_secretlike_report_cannot_even_reach_display():
    # The L5 validator refuses first; the display layer refuses its invalidity.
    report = _ready_report()
    report["summary"] = "the api key is abc123"
    m = dj.build_sync_display_model(report)
    assert m["verdict"] == dj.VERDICT_SYNC_DISPLAY_REFUSED
    assert "result_report_invalid" in m["blockers"]


def test_missing_or_refused_report_refuses():
    m = dj.build_sync_display_model(None)
    assert m["verdict"] == dj.VERDICT_SYNC_DISPLAY_REFUSED
    assert "result_report_missing_or_not_a_dict" in m["blockers"]
    refused_report = rn.build_result_report(None, None)
    m2 = dj.build_sync_display_model(refused_report)
    assert m2["verdict"] == dj.VERDICT_SYNC_DISPLAY_REFUSED
    assert "no_ready_report_to_display" in m2["blockers"]


# --------------------------------------------------------------------------- #
# posture
# --------------------------------------------------------------------------- #
def test_model_is_inert_on_all_paths():
    models = [
        dj.build_sync_display_model(_ready_report()),
        dj.build_sync_display_model(None),
    ]
    for m in models:
        assert m["display_only_no_controls"] is True
        assert m["no_button_or_action_can_trigger_work"] is True
        assert m["display_modifies_no_dashboard"] is True
        assert m["display_modifies_no_jarvis_runtime"] is True
        assert m["no_transport_nothing_sent"] is True
        assert m["model_is_in_memory_only"] is True
        assert m["human_review_required"] is True
        assert m["next_required_action"] == "HUMAN_REVIEW_OF_COMPLETED_ROADMAP"
        for key in (
            "executes", "writes_files", "writes_queue", "writes_ledger",
            "writes_dashboard", "modifies_jarvis_runtime", "sends_notifications",
            "runs_research", "runs_scanner", "runs_simulation", "runs_backtest",
            "runs_optimization", "starts_scheduler", "starts_daemon",
            "starts_background_worker", "runs_loop", "advances_any_cycle",
            "fetches_data", "calls_api", "connects_broker", "connects_exchange",
            "uses_real_money", "uses_network", "uses_credentials",
            "contains_order_logic", "authorizes_paper_execution",
            "authorizes_micro_live", "authorizes_live_trading", "promotes_gate",
            "unlocks_downstream_gate",
        ):
            assert m[key] is False, key
        assert m["paper_trading_gate_locked"] is True
        assert m["micro_live_gate_locked"] is True
        assert m["live_gate_locked"] is True
    assert models[0]["roadmap_link_id"] == "L6_dashboard_jarvis_automation_sync"
    assert models[0]["roadmap_seq"] == 6


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #
def test_validate_passes_on_ready_and_refused():
    assert dj.validate_sync_display_model(
        dj.build_sync_display_model(_ready_report()))["valid"] is True
    assert dj.validate_sync_display_model(
        dj.build_sync_display_model(None))["valid"] is True


def test_validate_rejects_action_buttons():
    m = dj.build_sync_display_model(_ready_report())
    m["dashboard_display"]["action_buttons"] = [
        {"label": "Run next step", "command": "RUN_IT"}]
    v = dj.validate_sync_display_model(m)
    assert v["valid"] is False
    assert "dashboard_display_carries_action_buttons" in v["errors"]
    m2 = dj.build_sync_display_model(_ready_report())
    m2["dashboard_display"]["buttons_forbidden_by_design"] = False
    v2 = dj.validate_sync_display_model(m2)
    assert v2["valid"] is False
    assert "button_ban_dropped" in v2["errors"]


def test_validate_rejects_work_trigger_or_runtime_claims():
    m = dj.build_sync_display_model(_ready_report())
    m["no_button_or_action_can_trigger_work"] = False
    v = dj.validate_sync_display_model(m)
    assert v["valid"] is False
    assert "work_trigger_allowed" in v["errors"]
    m2 = dj.build_sync_display_model(_ready_report())
    m2["display_modifies_no_jarvis_runtime"] = False
    v2 = dj.validate_sync_display_model(m2)
    assert v2["valid"] is False
    assert "jarvis_modification_claimed" in v2["errors"]


def test_validate_rejects_smuggled_forbidden_content():
    m = dj.build_sync_display_model(_ready_report())
    m["dashboard_display"]["report_summary"] = "open position on eth"
    v = dj.validate_sync_display_model(m)
    assert v["valid"] is False
    assert any("forbidden_display_content_in_dashboard" in e for e in v["errors"])
    m2 = dj.build_sync_display_model(_ready_report())
    m2["jarvis_display"]["status_sentence"] = "your wallet balance is 3 btc"
    v2 = dj.validate_sync_display_model(m2)
    assert v2["valid"] is False
    assert any("forbidden_display_content_in_jarvis" in e for e in v2["errors"])


def test_validate_rejects_smuggled_performance_claim():
    m = dj.build_sync_display_model(_ready_report())
    m["dashboard_display"]["report_summary"] = "this strategy is profitable"
    v = dj.validate_sync_display_model(m)
    assert v["valid"] is False
    assert any("unlabeled_performance_claim_in_dashboard" in e for e in v["errors"])


def test_validate_rejects_missing_banner_or_cannot_act_line():
    m = dj.build_sync_display_model(_ready_report())
    m["dashboard_display"]["human_action_needed_banner"] = "all good"
    v = dj.validate_sync_display_model(m)
    assert v["valid"] is False
    assert "human_action_banner_missing" in v["errors"]
    m2 = dj.build_sync_display_model(_ready_report())
    m2["jarvis_display"]["spoken_next_action"] = "I will handle it for you"
    v2 = dj.validate_sync_display_model(m2)
    assert v2["valid"] is False
    assert "jarvis_cannot_act_line_missing" in v2["errors"]


def test_validate_rejects_tampered_chain_rows():
    m = dj.build_sync_display_model(_ready_report())
    m["automation_chain_display"].append(
        {"link": "L7_auto_trading", "display": "trade it", "built": True})
    v = dj.validate_sync_display_model(m)
    assert v["valid"] is False
    assert "automation_chain_display_tampered" in v["errors"]


def test_validate_rejects_refused_model_with_display():
    m = dj.build_sync_display_model(None)
    m["jarvis_display"] = {"status_sentence": "hi"}
    v = dj.validate_sync_display_model(m)
    assert v["valid"] is False
    assert "refused_model_carries_jarvis_display" in v["errors"]


def test_validate_rejects_unlocked_gate_or_capability():
    m = dj.build_sync_display_model(_ready_report())
    m["micro_live_gate_locked"] = False
    v = dj.validate_sync_display_model(m)
    assert v["valid"] is False
    assert any("gate_not_locked:micro_live_gate_locked" in e for e in v["errors"])
    for cap in ("writes_dashboard", "modifies_jarvis_runtime", "sends_notifications"):
        m2 = dj.build_sync_display_model(_ready_report())
        m2[cap] = True
        v2 = dj.validate_sync_display_model(m2)
        assert v2["valid"] is False, cap
        assert any("capability_not_false:" + cap in e for e in v2["errors"])


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #
def test_render_markdown_ready_and_refused():
    md = dj.render_sync_display_markdown(dj.build_sync_display_model(_ready_report()))
    assert md.startswith(
        "# SPARTA Dashboard / JARVIS Sync Display Model (DISPLAY ONLY)")
    assert "Controls/buttons: NONE (forbidden by design)" in md
    assert "HUMAN ACTION NEEDED" in md
    assert "I cannot act" in md
    assert "LOCKED" in md
    md2 = dj.render_sync_display_markdown(dj.build_sync_display_model(None))
    assert "refused; nothing is displayed" in md2


# --------------------------------------------------------------------------- #
# label / posture / no banned imports
# --------------------------------------------------------------------------- #
def test_label_is_read_only_display_label():
    assert dj.get_dashboard_jarvis_sync_design_label() == dj.SYNC_LABEL
    assert "READ-ONLY" in dj.SYNC_LABEL
    assert "DISPLAY MODEL ONLY" in dj.SYNC_LABEL
    assert dj.SYNC_MODE == "RESEARCH_ONLY"


def test_action_carries_no_execution_or_promotion_verbs():
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE", "EXECUTION",
                   "BACKTEST", "BASELINE", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in dj.NEXT_REQUIRED_ACTION.upper(), banned


def test_module_imports_no_ui_transport_scheduler_or_credential_modules():
    with open(dj.__file__, "r", encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    banned = {"urllib", "requests", "socket", "http", "ftplib", "ccxt", "databento",
              "dotenv", "smtplib", "subprocess", "websocket", "websockets", "aiohttp",
              "schedule", "apscheduler", "threading", "multiprocessing", "asyncio",
              "sched", "time", "telegram", "email", "fastapi", "flask", "jinja2",
              "starlette"}
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imported.add(n.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert not (imported & banned)
