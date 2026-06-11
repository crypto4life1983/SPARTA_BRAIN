"""Tests for the SPARTA Strategy Research Orchestrator Contract (READ-ONLY).

Everything here is pure and in-memory; no network, no credentials, no API call, no
scheduler/daemon/worker/loop, no transport, no file write, no gate is unlocked.
The orchestrator walks ideas through the REAL L1-L3 modules, drafts an UNSIGNED
batch, and always stops at the human signature."""

from __future__ import annotations

import ast

import sparta_commander.research_cycle_scheduler_spec_contract as cy
import sparta_commander.strategy_idea_batch_approval_contract as ba
import sparta_commander.strategy_idea_intake_automation_contract as it
import sparta_commander.strategy_research_orchestrator_contract as orc

ARB_IDEA = "Monitor BTC funding rate vs spot-perp basis and alert on positive carry"
D1_IDEA = "When fresh evidence accrues, evaluate RP4 under the trend filter rules."
BAD_IDEA = "Build a bot that auto-trades the spread with my api key"
VAGUE_IDEA = "Something interesting about markets"


# --------------------------------------------------------------------------- #
# manual idea -> planned, stops at the human signature
# --------------------------------------------------------------------------- #
def test_manual_arbitrage_idea_is_planned():
    p = orc.plan_orchestration(ARB_IDEA, orc.SOURCE_MANUAL)
    assert p["verdict"] == orc.VERDICT_ORCHESTRATION_PLANNED
    assert p["final_state"] == "BATCH_DRAFTED_AWAITING_HUMAN_SIGNATURE"
    assert p["blockers"] == []
    assert p["lane"] == it.LANE_ARBITRAGE
    assert p["source"] == orc.SOURCE_MANUAL


def test_planned_chain_walks_real_l1_l2_l3_artifacts():
    p = orc.plan_orchestration(ARB_IDEA)
    assert p["intake_decision"]["answer"] == it.ANSWER_YES
    assert p["adapter_record"]["verdict"] == "INTAKE_PROPOSAL_CREATED"
    assert p["approval_packet"]["verdict"] == "STRATEGY_IDEA_PACKET_GENERATED"
    assert p["drafted_batch"]["verdict"] == "STRATEGY_IDEA_BATCH_COMPOSED"
    # the drafted batch covers the generated packet
    assert (p["drafted_batch"]["covered_packet_id"]
            == p["approval_packet"]["packet_id"])
    # validated by each link's own validator
    assert ba.validate_batch(p["drafted_batch"])["valid"] is True


def test_drafted_batch_is_unsigned_and_stops_at_human():
    p = orc.plan_orchestration(ARB_IDEA)
    assert p["drafted_batch"]["signed"] is False
    assert p["drafted_batch"]["human_signature"] is None
    assert p["progress_record"][-1] == "STOP:human_signature_required"
    assert p["orchestrator_signs_nothing"] is True
    assert p["orchestrator_approves_nothing"] is True


def test_recommendation_names_the_batch_and_is_suggestion_only():
    p = orc.plan_orchestration(ARB_IDEA)
    rec = p["next_safe_command_recommendation"]
    assert rec.startswith("HUMAN_DECIDES_ON_DRAFTED_BATCH batch_")
    assert p["drafted_batch"]["batch_id"] in rec
    assert "APPROVE_BATCH_AS_ENUMERATED or DENY_BATCH" in rec
    assert "recommendation only" in rec


def test_crypto_d1_idea_routes_to_its_lane():
    p = orc.plan_orchestration(D1_IDEA)
    assert p["verdict"] == orc.VERDICT_ORCHESTRATION_PLANNED
    assert p["lane"] == it.LANE_CRYPTO_D1
    constraints = p["approval_packet"]["lane_constraints"]
    assert any("frozen_block_190_bars" in c for c in constraints)


def test_progress_record_traces_each_link_in_memory_only():
    p = orc.plan_orchestration(ARB_IDEA)
    trace = p["progress_record"]
    assert trace[0].startswith("L1_triage:")
    assert any(t.startswith("L1_adapter:") for t in trace)
    assert any(t.startswith("L2_packet:") for t in trace)
    assert any(t.startswith("L3_batch_draft:") for t in trace)
    assert p["records_in_memory_only"] is True


def test_plan_is_deterministic():
    assert orc.plan_orchestration(ARB_IDEA) == orc.plan_orchestration(ARB_IDEA)


# --------------------------------------------------------------------------- #
# scout source: same pipeline, no shortcut, scout not built
# --------------------------------------------------------------------------- #
def test_scout_idea_walks_the_identical_pipeline():
    manual = orc.plan_orchestration(ARB_IDEA, orc.SOURCE_MANUAL)
    scout = orc.plan_orchestration(ARB_IDEA, orc.SOURCE_SCOUT)
    assert scout["verdict"] == orc.VERDICT_ORCHESTRATION_PLANNED
    # identical chain artifacts -- the source grants no shortcut
    assert scout["drafted_batch"] == manual["drafted_batch"]
    assert scout["approval_packet"] == manual["approval_packet"]
    assert scout["same_pipeline_for_all_sources"] is True


def test_scout_source_adds_extra_human_review_and_is_not_built():
    scout = orc.plan_orchestration(ARB_IDEA, orc.SOURCE_SCOUT)
    assert scout["scout_sourced_requires_extra_human_review"] is True
    assert scout["scout_is_built"] is False
    manual = orc.plan_orchestration(ARB_IDEA, orc.SOURCE_MANUAL)
    assert manual["scout_sourced_requires_extra_human_review"] is False


def test_scout_hard_no_is_refused_like_any_other():
    p = orc.plan_orchestration(BAD_IDEA, orc.SOURCE_SCOUT)
    assert p["verdict"] == orc.VERDICT_ORCHESTRATION_REFUSED
    assert p["drafted_batch"] is None


def test_unknown_source_is_refused():
    p = orc.plan_orchestration(ARB_IDEA, "autonomous_self_directed")
    assert p["verdict"] == orc.VERDICT_ORCHESTRATION_REFUSED
    assert any("idea_source_not_in_closed_set" in b for b in p["blockers"])


# --------------------------------------------------------------------------- #
# refusals and clarifications propagate from the front door
# --------------------------------------------------------------------------- #
def test_execution_credential_idea_is_refused_with_no_artifacts():
    p = orc.plan_orchestration(BAD_IDEA)
    assert p["verdict"] == orc.VERDICT_ORCHESTRATION_REFUSED
    assert p["final_state"] == "REFUSED_STOPPED"
    assert "idea_rejected_at_the_front_door" in p["blockers"]
    assert p["adapter_record"] is None
    assert p["approval_packet"] is None
    assert p["drafted_batch"] is None
    assert p["next_safe_command_recommendation"] is None


def test_vague_idea_needs_human_clarification():
    p = orc.plan_orchestration(VAGUE_IDEA)
    assert p["verdict"] == orc.VERDICT_ORCHESTRATION_NEEDS_CLARIFICATION
    assert p["final_state"] == "NEEDS_HUMAN_CLARIFICATION"
    assert p["clarifications"]
    assert p["drafted_batch"] is None


def test_every_hard_no_class_is_refused():
    for bad in ("place orders on binance for me",
                "connect my exchange account api key",
                "guaranteed profit, cannot lose",
                "use a paid signal group's private feed",
                "tune rp6 and re-run the old windows"):
        p = orc.plan_orchestration(bad)
        assert p["verdict"] == orc.VERDICT_ORCHESTRATION_REFUSED, bad


# --------------------------------------------------------------------------- #
# constitution: references not duplication, forbidden forever, boundaries
# --------------------------------------------------------------------------- #
def test_chain_links_are_referenced_by_module_name():
    p = orc.plan_orchestration(ARB_IDEA)
    refs = {r["link"]: r["module"] for r in p["chain_link_references"]}
    assert set(refs) == {"L1", "L2", "L3", "L4", "L5", "L6"}
    assert "strategy_idea_intake_automation_contract" in refs["L1"]
    assert "strategy_idea_approval_packet_schema_contract" in refs["L2"]
    assert "strategy_idea_batch_approval_contract" in refs["L3"]
    assert "research_cycle_scheduler_spec_contract" in refs["L4"]
    assert "result_notification_reporting_contract" in refs["L5"]
    assert "dashboard_jarvis_sync_design_contract" in refs["L6"]


def test_l4_rules_are_imported_not_redefined():
    p = orc.plan_orchestration(ARB_IDEA)
    assert tuple(p["l4_auto_advance_eligible_kinds"]) == cy.AUTO_ADVANCE_ELIGIBLE_KINDS
    assert tuple(p["l4_human_stop_kinds"]) == cy.HUMAN_STOP_KINDS
    assert p["l4_max_cycle_steps"] == cy.MAX_CYCLE_STEPS
    assert p["auto_progress_is_theory_only_nothing_advances_here"] is True


def test_forbidden_forever_list_is_complete():
    joined = " ".join(orc.FORBIDDEN_FOREVER)
    assert "placing_or_preparing_any_order" in joined
    assert "broker_or_exchange_credentials" in joined
    assert "real_money" in joined
    assert "unlocking_any_trading_gate" in joined
    assert "promoting_anything_without_a_human" in joined
    assert "signing_or_approving_its_own_packets_or_batches" in joined
    assert "extending_its_own_scope_beyond_the_signed_batch" in joined


def test_future_block_boundaries_cover_all_four():
    blocks = [b["block"] for b in orc.FUTURE_BLOCK_BOUNDARIES]
    assert blocks == [
        "real_dashboard_jarvis_wiring",
        "manual_start_notification_transport",
        "real_scheduler_build_under_l4_rules",
        "arbitrage_data_contract_roadmap_seq_2",
    ]
    for b in orc.FUTURE_BLOCK_BOUNDARIES:
        assert "separate" in b["boundary"] or "own" in b["boundary"]


def test_human_escalation_points_are_the_closed_six():
    assert len(orc.HUMAN_ESCALATION_POINTS) == 6
    joined = " ".join(orc.HUMAN_ESCALATION_POINTS)
    assert "batch_signature" in joined
    assert "every_cycle_review_stop" in joined
    assert "every_gate_decision" in joined
    assert "any_blocker_or_deviation" in joined


def test_draft_steps_use_only_the_l3_closed_catalog():
    for step in orc._draft_steps_for_lane("arbitrage_factory_v1"):
        assert step["kind"] in ba.ALLOWED_STEP_KINDS


# --------------------------------------------------------------------------- #
# posture: nothing runs, gates untouched
# --------------------------------------------------------------------------- #
def test_plan_is_inert_on_all_paths():
    plans = [
        orc.plan_orchestration(ARB_IDEA),
        orc.plan_orchestration(BAD_IDEA),
        orc.plan_orchestration(VAGUE_IDEA),
        orc.plan_orchestration(ARB_IDEA, "bad_source"),
    ]
    for p in plans:
        assert p["plan_is_in_memory_only"] is True
        assert p["human_review_required"] is True
        assert p["next_required_action"] == "HUMAN_DECISION_ON_DRAFTED_BATCH"
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
            assert p[key] is False, key
        assert p["paper_trading_gate_locked"] is True
        assert p["micro_live_gate_locked"] is True
        assert p["live_gate_locked"] is True


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #
def test_validate_passes_on_all_three_outcomes():
    assert orc.validate_orchestration_plan(
        orc.plan_orchestration(ARB_IDEA))["valid"] is True
    assert orc.validate_orchestration_plan(
        orc.plan_orchestration(BAD_IDEA))["valid"] is True
    assert orc.validate_orchestration_plan(
        orc.plan_orchestration(VAGUE_IDEA))["valid"] is True


def test_validate_rejects_signed_drafted_batch():
    p = orc.plan_orchestration(ARB_IDEA)
    p["drafted_batch"]["signed"] = True
    v = orc.validate_orchestration_plan(p)
    assert v["valid"] is False
    assert "drafted_batch_claims_signature" in v["errors"]


def test_validate_rejects_plan_not_stopping_at_human():
    p = orc.plan_orchestration(ARB_IDEA)
    p["progress_record"].append("AUTO_PROCEEDING_TO_RUN")
    v = orc.validate_orchestration_plan(p)
    assert v["valid"] is False
    assert "plan_does_not_stop_at_human_signature" in v["errors"]


def test_validate_rejects_weakened_forbidden_forever():
    p = orc.plan_orchestration(ARB_IDEA)
    p["forbidden_forever"] = [
        f for f in p["forbidden_forever"] if "order" not in f]
    v = orc.validate_orchestration_plan(p)
    assert v["valid"] is False
    assert "forbidden_forever_weakened" in v["errors"]


def test_validate_rejects_scout_built_claim_or_dropped_review():
    p = orc.plan_orchestration(ARB_IDEA, orc.SOURCE_SCOUT)
    p["scout_is_built"] = True
    v = orc.validate_orchestration_plan(p)
    assert v["valid"] is False
    assert "scout_claimed_built" in v["errors"]
    p2 = orc.plan_orchestration(ARB_IDEA, orc.SOURCE_SCOUT)
    p2["scout_sourced_requires_extra_human_review"] = False
    v2 = orc.validate_orchestration_plan(p2)
    assert v2["valid"] is False
    assert "scout_extra_review_dropped" in v2["errors"]


def test_validate_rejects_refused_plan_with_batch_or_recommendation():
    p = orc.plan_orchestration(BAD_IDEA)
    p["drafted_batch"] = {"batch_id": "x"}
    v = orc.validate_orchestration_plan(p)
    assert v["valid"] is False
    assert "refused_plan_carries_a_batch" in v["errors"]
    p2 = orc.plan_orchestration(BAD_IDEA)
    p2["next_safe_command_recommendation"] = "RUN_IT"
    v2 = orc.validate_orchestration_plan(p2)
    assert v2["valid"] is False
    assert "refused_plan_carries_a_recommendation" in v2["errors"]


def test_validate_rejects_self_approval_claims():
    p = orc.plan_orchestration(ARB_IDEA)
    p["orchestrator_signs_nothing"] = False
    v = orc.validate_orchestration_plan(p)
    assert v["valid"] is False
    assert "orchestrator_claims_to_sign" in v["errors"]
    p2 = orc.plan_orchestration(ARB_IDEA)
    p2["same_pipeline_for_all_sources"] = False
    v2 = orc.validate_orchestration_plan(p2)
    assert v2["valid"] is False
    assert "scout_shortcut_allowed" in v2["errors"]


def test_validate_rejects_tampered_states_or_escalations():
    p = orc.plan_orchestration(ARB_IDEA)
    p["orchestrator_states"].append("RUNNING_FOREVER")
    v = orc.validate_orchestration_plan(p)
    assert v["valid"] is False
    assert "orchestrator_states_tampered" in v["errors"]
    p2 = orc.plan_orchestration(ARB_IDEA)
    p2["human_escalation_points"] = p2["human_escalation_points"][:2]
    v2 = orc.validate_orchestration_plan(p2)
    assert v2["valid"] is False
    assert "escalation_points_tampered" in v2["errors"]


def test_validate_rejects_unlocked_gate_or_capability():
    p = orc.plan_orchestration(ARB_IDEA)
    p["live_gate_locked"] = False
    v = orc.validate_orchestration_plan(p)
    assert v["valid"] is False
    assert any("gate_not_locked:live_gate_locked" in e for e in v["errors"])
    for cap in ("starts_scheduler", "advances_any_cycle", "runs_loop"):
        p2 = orc.plan_orchestration(ARB_IDEA)
        p2[cap] = True
        v2 = orc.validate_orchestration_plan(p2)
        assert v2["valid"] is False, cap
        assert any("capability_not_false:" + cap in e for e in v2["errors"])


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #
def test_render_markdown_planned_refused_and_clarification():
    md = orc.render_orchestration_plan_markdown(orc.plan_orchestration(ARB_IDEA))
    assert md.startswith("# SPARTA Strategy Research Orchestrator Plan (PLAN ONLY)")
    assert "signs nothing and approves nothing" in md
    assert "Forbidden forever" in md
    assert "own separate human approval" in md
    assert "LOCKED" in md
    md2 = orc.render_orchestration_plan_markdown(orc.plan_orchestration(BAD_IDEA))
    assert "stopped; a fresh human approval is required" in md2
    md3 = orc.render_orchestration_plan_markdown(orc.plan_orchestration(VAGUE_IDEA))
    assert "Human clarification needed" in md3


# --------------------------------------------------------------------------- #
# label / posture / no banned imports
# --------------------------------------------------------------------------- #
def test_label_is_read_only_plan_label():
    assert orc.get_strategy_research_orchestrator_label() == orc.ORCHESTRATOR_LABEL
    assert "READ-ONLY" in orc.ORCHESTRATOR_LABEL
    assert "SIGNS NOTHING" in orc.ORCHESTRATOR_LABEL
    assert orc.ORCHESTRATOR_MODE == "RESEARCH_ONLY"


def test_action_carries_no_execution_or_promotion_verbs():
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE", "EXECUTION",
                   "BACKTEST", "BASELINE", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in orc.NEXT_REQUIRED_ACTION.upper(), banned


def test_module_imports_no_transport_scheduler_or_credential_modules():
    with open(orc.__file__, "r", encoding="utf-8") as fh:
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
