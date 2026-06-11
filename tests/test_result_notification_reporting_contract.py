"""Tests for the SPARTA Result Notification / Reporting Contract (READ-ONLY).

Everything here is pure and in-memory; no network, no credentials, no API call, no
telegram/email send, no dashboard write, no scheduler, no gate is unlocked. The
contract shapes safe report payloads from cycle outcomes and sends nothing."""

from __future__ import annotations

import ast

import sparta_commander.intake_to_orchestrator_adapter_contract as ad
import sparta_commander.research_cycle_scheduler_spec_contract as cy
import sparta_commander.result_notification_reporting_contract as rn
import sparta_commander.strategy_idea_approval_packet_schema_contract as pk
import sparta_commander.strategy_idea_batch_approval_contract as ba
import sparta_commander.strategy_idea_intake_automation_contract as it


def _ready_cycle_spec():
    packet = pk.generate_approval_packet(ad.adapt_intake_decision(
        it.intake_strategy_idea("funding rate arbitrage research on btc basis")))
    steps = [
        {"seq": 1, "kind": "build_contract_module",
         "description": "build the lane data contract module"},
        {"seq": 2, "kind": "run_contract_tests",
         "description": "run the new tests plus the safety suite"},
        {"seq": 3, "kind": "results_review_contract",
         "description": "review contract over the findings"},
    ]
    batch = ba.compose_batch(packet, steps)
    approval = ba.record_human_batch_decision(
        batch, ba.DECISION_APPROVE_BATCH, "Mahmoud")
    return cy.build_research_cycle_spec(batch, approval)


def _refused_cycle_spec():
    return cy.build_research_cycle_spec(None, None)


# --------------------------------------------------------------------------- #
# accepted results -> safe payloads
# --------------------------------------------------------------------------- #
def test_step_done_yields_ready_report():
    spec = _ready_cycle_spec()
    r = rn.build_result_report(spec, {
        "result_type": rn.RESULT_TYPE_STEP_DONE, "step_seq": 2,
        "summary": "contract tests passed on the research-only chain"})
    assert r["verdict"] == rn.VERDICT_REPORT_READY
    assert r["report_state"] == "REPORT_READY_FOR_HUMAN"
    assert r["blockers"] == []
    assert r["report_id"].startswith("report_")
    assert r["cycle_id"] == spec["cycle_id"]
    assert r["lane"] == it.LANE_ARBITRAGE
    assert r["step_seq"] == 2


def test_all_result_types_in_closed_set_are_reportable():
    spec = _ready_cycle_spec()
    for rt in (rn.RESULT_TYPE_STEP_DONE, rn.RESULT_TYPE_CYCLE_STOPPED,
               rn.RESULT_TYPE_CYCLE_COMPLETE,
               rn.RESULT_TYPE_HUMAN_REVIEW_REQUIRED):
        event = {"result_type": rt, "summary": "an update for the human"}
        if rt == rn.RESULT_TYPE_STEP_DONE:
            event["step_seq"] = 1
        r = rn.build_result_report(spec, event)
        assert r["verdict"] == rn.VERDICT_REPORT_READY, rt


def test_cycle_refused_reports_against_a_refused_spec():
    r = rn.build_result_report(_refused_cycle_spec(), {
        "result_type": rn.RESULT_TYPE_CYCLE_REFUSED,
        "summary": "the cycle was refused because the batch was never signed"})
    assert r["verdict"] == rn.VERDICT_REPORT_READY
    assert r["result_type"] == rn.RESULT_TYPE_CYCLE_REFUSED


def test_payloads_are_shaped_for_all_three_channels():
    spec = _ready_cycle_spec()
    r = rn.build_result_report(spec, {
        "result_type": rn.RESULT_TYPE_CYCLE_COMPLETE,
        "summary": "all enumerated steps reported done"})
    dash = r["dashboard_payload"]
    assert dash["human_action_needed"] is True
    assert dash["payload_only_nothing_sent"] is True
    assert dash["cycle_id"] == spec["cycle_id"]
    jarv = r["jarvis_payload"]
    assert "No performance claims" in jarv["spoken_summary"]
    assert jarv["contains_no_performance_claims"] is True
    tele = r["telegram_payload"]
    assert tele["payload_only_not_sent"] is True
    assert tele["send_requires_separate_human_approved_transport"] is True
    assert tele["text"].startswith("[SPARTA research]")
    assert len(tele["text"]) <= rn.TELEGRAM_TEXT_MAX_CHARS


def test_telegram_text_is_truncated_to_cap():
    spec = _ready_cycle_spec()
    r = rn.build_result_report(spec, {
        "result_type": rn.RESULT_TYPE_CYCLE_STOPPED,
        "summary": "x" * 2000})
    assert len(r["telegram_payload"]["text"]) == rn.TELEGRAM_TEXT_MAX_CHARS


def test_recommendation_is_carried_and_marked_suggestion_only():
    spec = _ready_cycle_spec()
    r = rn.build_result_report(spec, {
        "result_type": rn.RESULT_TYPE_HUMAN_REVIEW_REQUIRED,
        "summary": "a review gate was reached"})
    assert "recommendation only" in r["next_safe_command_recommendation"]
    assert r["recommendation_is_suggestion_only"] is True
    assert r["no_implied_approval_of_anything"] is True


def test_report_is_deterministic():
    spec = _ready_cycle_spec()
    event = {"result_type": rn.RESULT_TYPE_CYCLE_COMPLETE, "summary": "done"}
    assert rn.build_result_report(spec, event) == rn.build_result_report(spec, event)


# --------------------------------------------------------------------------- #
# refusals: unsafe content can never become a payload
# --------------------------------------------------------------------------- #
def test_secret_like_content_refuses_whole_report():
    spec = _ready_cycle_spec()
    for bad in ("here is the api key abc123",
                "wallet balance is 3.2 btc",
                "order id 9912 filled",
                "open position on eth",
                "the password is hunter2",
                "seed phrase: apple banana ...",
                "place order now",
                "buy now before it pumps"):
        r = rn.build_result_report(spec, {
            "result_type": rn.RESULT_TYPE_CYCLE_COMPLETE, "summary": bad})
        assert r["verdict"] == rn.VERDICT_REPORT_REFUSED, bad
        assert any("forbidden_content_token" in b for b in r["blockers"])
        assert r["dashboard_payload"] is None
        assert r["telegram_payload"] is None


def test_unknown_result_type_refuses():
    r = rn.build_result_report(_ready_cycle_spec(), {
        "result_type": "trade_executed", "summary": "x"})
    assert r["verdict"] == rn.VERDICT_REPORT_REFUSED
    assert any("result_type_not_in_closed_set" in b for b in r["blockers"])


def test_missing_inputs_refuse():
    assert "cycle_spec_missing_or_not_a_dict" in rn.build_result_report(
        None, {"result_type": rn.RESULT_TYPE_STEP_DONE, "summary": "x"})["blockers"]
    assert "result_event_missing_or_not_a_dict" in rn.build_result_report(
        _ready_cycle_spec(), None)["blockers"]
    assert "summary_missing" in rn.build_result_report(
        _ready_cycle_spec(),
        {"result_type": rn.RESULT_TYPE_CYCLE_COMPLETE, "summary": "  "})["blockers"]


def test_tampered_cycle_spec_refuses():
    spec = _ready_cycle_spec()
    spec["scheduler_built_by_this_contract"] = True
    r = rn.build_result_report(spec, {
        "result_type": rn.RESULT_TYPE_CYCLE_COMPLETE, "summary": "x"})
    assert r["verdict"] == rn.VERDICT_REPORT_REFUSED
    assert "cycle_spec_invalid" in r["blockers"]


def test_step_done_requires_valid_step_seq():
    spec = _ready_cycle_spec()
    for bad_seq in (None, 0, 99, "2"):
        r = rn.build_result_report(spec, {
            "result_type": rn.RESULT_TYPE_STEP_DONE, "step_seq": bad_seq,
            "summary": "a step finished"})
        assert r["verdict"] == rn.VERDICT_REPORT_REFUSED, bad_seq
        assert "step_done_needs_a_valid_step_seq" in r["blockers"]


def test_refusal_report_needs_refused_spec_and_vice_versa():
    r = rn.build_result_report(_ready_cycle_spec(), {
        "result_type": rn.RESULT_TYPE_CYCLE_REFUSED, "summary": "x"})
    assert "refusal_report_needs_a_refused_cycle_spec" in r["blockers"]
    r2 = rn.build_result_report(_refused_cycle_spec(), {
        "result_type": rn.RESULT_TYPE_CYCLE_COMPLETE, "summary": "x"})
    assert "result_needs_a_ready_cycle_spec" in r2["blockers"]


# --------------------------------------------------------------------------- #
# posture: nothing sent, nothing run, gates untouched
# --------------------------------------------------------------------------- #
def test_report_is_inert_on_all_paths():
    spec = _ready_cycle_spec()
    reports = [
        rn.build_result_report(spec, {
            "result_type": rn.RESULT_TYPE_CYCLE_COMPLETE, "summary": "done"}),
        rn.build_result_report(None, None),
    ]
    for r in reports:
        assert r["payload_only_nothing_sent"] is True
        assert r["report_sends_no_telegram"] is True
        assert r["report_sends_no_email"] is True
        assert r["report_writes_no_dashboard"] is True
        assert r["report_is_in_memory_only"] is True
        assert r["human_review_required"] is True
        assert r["next_required_action"] == (
            "HUMAN_APPROVED_DASHBOARD_JARVIS_SYNC_DESIGN")
        for key in (
            "executes", "writes_files", "writes_queue", "writes_ledger",
            "sends_notifications", "runs_research", "runs_scanner",
            "runs_simulation", "runs_backtest", "runs_optimization",
            "starts_scheduler", "starts_daemon", "starts_background_worker",
            "runs_loop", "advances_any_cycle", "fetches_data", "calls_api",
            "connects_broker", "connects_exchange", "uses_real_money",
            "uses_network", "uses_credentials", "contains_order_logic",
            "authorizes_paper_execution", "authorizes_micro_live",
            "authorizes_live_trading", "promotes_gate", "unlocks_downstream_gate",
        ):
            assert r[key] is False, key
        assert r["paper_trading_gate_locked"] is True
        assert r["micro_live_gate_locked"] is True
        assert r["live_gate_locked"] is True
    assert reports[0]["roadmap_link_id"] == "L5_result_notification_reporting_layer"
    assert reports[0]["roadmap_seq"] == 5


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #
def test_validate_passes_on_ready_and_refused():
    spec = _ready_cycle_spec()
    ready = rn.build_result_report(spec, {
        "result_type": rn.RESULT_TYPE_CYCLE_COMPLETE, "summary": "done"})
    refused = rn.build_result_report(None, None)
    assert rn.validate_result_report(ready)["valid"] is True
    assert rn.validate_result_report(refused)["valid"] is True


def test_validate_rejects_smuggled_secret_into_payload():
    spec = _ready_cycle_spec()
    r = rn.build_result_report(spec, {
        "result_type": rn.RESULT_TYPE_CYCLE_COMPLETE, "summary": "done"})
    r["telegram_payload"]["text"] = "the api key is abc123"
    v = rn.validate_result_report(r)
    assert v["valid"] is False
    assert "forbidden_content_in_telegram_text" in v["errors"]
    r2 = rn.build_result_report(spec, {
        "result_type": rn.RESULT_TYPE_CYCLE_COMPLETE, "summary": "done"})
    r2["dashboard_payload"]["summary"] = "open position on btc"
    v2 = rn.validate_result_report(r2)
    assert v2["valid"] is False
    assert "forbidden_content_in_dashboard_payload" in v2["errors"]


def test_validate_rejects_sent_claim_or_transport_drop():
    spec = _ready_cycle_spec()
    r = rn.build_result_report(spec, {
        "result_type": rn.RESULT_TYPE_CYCLE_COMPLETE, "summary": "done"})
    r["telegram_payload"]["payload_only_not_sent"] = False
    v = rn.validate_result_report(r)
    assert v["valid"] is False
    assert "telegram_payload_claims_sent" in v["errors"]
    r2 = rn.build_result_report(spec, {
        "result_type": rn.RESULT_TYPE_CYCLE_COMPLETE, "summary": "done"})
    r2["telegram_payload"]["send_requires_separate_human_approved_transport"] = False
    v2 = rn.validate_result_report(r2)
    assert v2["valid"] is False
    assert "telegram_transport_boundary_dropped" in v2["errors"]
    r3 = rn.build_result_report(spec, {
        "result_type": rn.RESULT_TYPE_CYCLE_COMPLETE, "summary": "done"})
    r3["payload_only_nothing_sent"] = False
    v3 = rn.validate_result_report(r3)
    assert v3["valid"] is False
    assert "report_claims_to_send" in v3["errors"]


def test_validate_rejects_refused_report_with_payload():
    r = rn.build_result_report(None, None)
    r["telegram_payload"] = {"text": "hi"}
    v = rn.validate_result_report(r)
    assert v["valid"] is False
    assert "refused_report_carries_payload:telegram_payload" in v["errors"]


def test_validate_rejects_performance_claim_flag_drop():
    spec = _ready_cycle_spec()
    r = rn.build_result_report(spec, {
        "result_type": rn.RESULT_TYPE_CYCLE_COMPLETE, "summary": "done"})
    r["jarvis_payload"]["contains_no_performance_claims"] = False
    v = rn.validate_result_report(r)
    assert v["valid"] is False
    assert "jarvis_payload_allows_performance_claims" in v["errors"]


def test_validate_rejects_oversized_telegram_text():
    spec = _ready_cycle_spec()
    r = rn.build_result_report(spec, {
        "result_type": rn.RESULT_TYPE_CYCLE_COMPLETE, "summary": "done"})
    r["telegram_payload"]["text"] = "x" * (rn.TELEGRAM_TEXT_MAX_CHARS + 1)
    v = rn.validate_result_report(r)
    assert v["valid"] is False
    assert "telegram_text_missing_or_too_long" in v["errors"]


def test_validate_rejects_dropped_human_action_or_implied_approval():
    spec = _ready_cycle_spec()
    r = rn.build_result_report(spec, {
        "result_type": rn.RESULT_TYPE_CYCLE_COMPLETE, "summary": "done"})
    r["human_action_needed"] = False
    v = rn.validate_result_report(r)
    assert v["valid"] is False
    assert "human_action_dropped" in v["errors"]
    r2 = rn.build_result_report(spec, {
        "result_type": rn.RESULT_TYPE_CYCLE_COMPLETE, "summary": "done"})
    r2["no_implied_approval_of_anything"] = False
    v2 = rn.validate_result_report(r2)
    assert v2["valid"] is False
    assert "implied_approval_allowed" in v2["errors"]


def test_validate_rejects_unlocked_gate_or_capability():
    spec = _ready_cycle_spec()
    r = rn.build_result_report(spec, {
        "result_type": rn.RESULT_TYPE_CYCLE_COMPLETE, "summary": "done"})
    r["live_gate_locked"] = False
    v = rn.validate_result_report(r)
    assert v["valid"] is False
    assert any("gate_not_locked:live_gate_locked" in e for e in v["errors"])
    r2 = rn.build_result_report(spec, {
        "result_type": rn.RESULT_TYPE_CYCLE_COMPLETE, "summary": "done"})
    r2["sends_notifications"] = True
    v2 = rn.validate_result_report(r2)
    assert v2["valid"] is False
    assert any("capability_not_false:sends_notifications" in e for e in v2["errors"])


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #
def test_render_markdown_ready_and_refused():
    spec = _ready_cycle_spec()
    md = rn.render_result_report_markdown(rn.build_result_report(spec, {
        "result_type": rn.RESULT_TYPE_CYCLE_COMPLETE, "summary": "done"}))
    assert md.startswith(
        "# SPARTA Research Result Report (PAYLOAD ONLY, NOTHING SENT)")
    assert "suggestion only, human must issue it" in md
    assert "payload only, NOT sent" in md
    assert "LOCKED" in md
    md2 = rn.render_result_report_markdown(rn.build_result_report(None, None))
    assert "refused; no payload exists" in md2


# --------------------------------------------------------------------------- #
# label / posture / no banned imports
# --------------------------------------------------------------------------- #
def test_label_is_read_only_payload_label():
    assert rn.get_result_notification_reporting_label() == rn.REPORT_LABEL
    assert "READ-ONLY" in rn.REPORT_LABEL
    assert "NOTHING SENT" in rn.REPORT_LABEL
    assert rn.REPORT_MODE == "RESEARCH_ONLY"


def test_action_carries_no_execution_or_promotion_verbs():
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE", "EXECUTION",
                   "BACKTEST", "BASELINE", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in rn.NEXT_REQUIRED_ACTION.upper(), banned


def test_module_imports_no_transport_scheduler_or_credential_modules():
    with open(rn.__file__, "r", encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    banned = {"urllib", "requests", "socket", "http", "ftplib", "ccxt", "databento",
              "dotenv", "smtplib", "subprocess", "websocket", "websockets", "aiohttp",
              "schedule", "apscheduler", "threading", "multiprocessing", "asyncio",
              "sched", "time", "telegram", "email", "imaplib", "poplib"}
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imported.add(n.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert not (imported & banned)
