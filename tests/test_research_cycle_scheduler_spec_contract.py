"""Tests for the SPARTA Research Cycle Scheduler SPEC Contract (READ-ONLY).

Everything here is pure and in-memory; no network, no credentials, no API call, no
scheduler, no daemon, no worker, no loop, no file write, no gate is unlocked. The
spec derives a bounded cycle rulebook from a SIGNED batch and starts nothing."""

from __future__ import annotations

import ast

import sparta_commander.intake_to_orchestrator_adapter_contract as ad
import sparta_commander.research_cycle_scheduler_spec_contract as cy
import sparta_commander.strategy_idea_approval_packet_schema_contract as pk
import sparta_commander.strategy_idea_batch_approval_contract as ba
import sparta_commander.strategy_idea_intake_automation_contract as it


def _packet():
    return pk.generate_approval_packet(ad.adapt_intake_decision(
        it.intake_strategy_idea("funding rate arbitrage research on btc basis")))


def _steps():
    return [
        {"seq": 1, "kind": "build_contract_module",
         "description": "build the lane data contract module"},
        {"seq": 2, "kind": "write_contract_tests",
         "description": "write the contract test file"},
        {"seq": 3, "kind": "run_contract_tests",
         "description": "run the new tests plus the safety suite"},
        {"seq": 4, "kind": "dry_run_in_memory",
         "description": "in-memory dry walk of the contract chain"},
        {"seq": 5, "kind": "results_review_contract",
         "description": "review contract over the dry-walk findings"},
    ]


def _batch():
    return ba.compose_batch(_packet(), _steps())


def _approval(batch=None):
    return ba.record_human_batch_decision(
        batch if batch is not None else _batch(),
        ba.DECISION_APPROVE_BATCH, "Mahmoud")


# --------------------------------------------------------------------------- #
# signed batch -> READY cycle spec
# --------------------------------------------------------------------------- #
def test_signed_batch_yields_ready_cycle_spec():
    b = _batch()
    s = cy.build_research_cycle_spec(b, _approval(b))
    assert s["verdict"] == cy.VERDICT_CYCLE_SPEC_READY
    assert s["blockers"] == []
    assert s["cycle_id"].startswith("cycle_")
    assert s["covered_batch_id"] == b["batch_id"]
    assert s["signed_by"] == "Mahmoud"
    assert s["lane"] == it.LANE_ARBITRAGE
    assert s["step_count"] == 5


def test_cycle_steps_map_one_to_one_with_batch_steps():
    b = _batch()
    s = cy.build_research_cycle_spec(b, _approval(b))
    assert [st["seq"] for st in s["cycle_steps"]] == [1, 2, 3, 4, 5]
    assert [st["kind"] for st in s["cycle_steps"]] == [
        st["kind"] for st in b["enumerated_steps"]]


def test_first_step_requires_human_activation():
    b = _batch()
    s = cy.build_research_cycle_spec(b, _approval(b))
    first = s["cycle_steps"][0]
    assert first["must_stop_for_human"] is True
    assert first["stop_reason"] == "first_step_requires_human_activation"
    assert first["auto_advance_eligible_in_theory"] is False


def test_final_step_always_stops_for_human_review():
    b = _batch()
    s = cy.build_research_cycle_spec(b, _approval(b))
    last = s["cycle_steps"][-1]
    assert last["must_stop_for_human"] is True


def test_auto_advance_theory_only_for_mechanical_middle_steps():
    b = _batch()
    s = cy.build_research_cycle_spec(b, _approval(b))
    by_kind = {st["kind"]: st for st in s["cycle_steps"]}
    # mechanical middle steps are eligible in theory
    assert by_kind["run_contract_tests"]["auto_advance_eligible_in_theory"] is True
    assert by_kind["dry_run_in_memory"]["auto_advance_eligible_in_theory"] is True
    # non-mechanical kinds never are
    assert by_kind["write_contract_tests"]["auto_advance_eligible_in_theory"] is False
    # review kinds always stop
    assert by_kind["results_review_contract"]["must_stop_for_human"] is True
    assert s["auto_advance_is_theory_only_nothing_advances_here"] is True


def test_human_stop_kinds_always_stop_even_mid_cycle():
    steps = _steps()
    steps.append({"seq": 6, "kind": "human_decision_contract",
                  "description": "record the human decision"})
    steps.append({"seq": 7, "kind": "mission_flow_registration",
                  "description": "register the outcome in mission flow"})
    b = ba.compose_batch(_packet(), steps)
    s = cy.build_research_cycle_spec(b, _approval(b))
    by_kind = {st["kind"]: st for st in s["cycle_steps"]}
    # results_review is now mid-cycle (seq 5 of 7) and must still stop
    rr = by_kind["results_review_contract"]
    assert rr["must_stop_for_human"] is True
    assert rr["stop_reason"] == "kind_always_requires_a_human"
    assert by_kind["human_decision_contract"]["must_stop_for_human"] is True
    assert by_kind["mission_flow_registration"]["must_stop_for_human"] is True


def test_recommendation_is_recommendation_only():
    b = _batch()
    s = cy.build_research_cycle_spec(b, _approval(b))
    rec = s["next_safe_command_recommendation"]
    assert rec.startswith("HUMAN_ISSUES_STEP_1_COMMAND")
    assert "recommendation only" in rec
    assert s["output_is_a_recommendation_only"] is True


def test_spec_is_deterministic():
    b = _batch()
    a = cy.build_research_cycle_spec(b, _approval(b))
    c = cy.build_research_cycle_spec(b, _approval(b))
    assert a == c


# --------------------------------------------------------------------------- #
# refusals: unsigned / denied / tampered / mismatched / refused inputs
# --------------------------------------------------------------------------- #
def test_unsigned_batch_alone_yields_no_cycle():
    s = cy.build_research_cycle_spec(_batch(), None)
    assert s["verdict"] == cy.VERDICT_CYCLE_SPEC_REFUSED
    assert "human_decision_missing_or_not_a_dict" in s["blockers"]
    assert s["cycle_steps"] == []
    assert s["next_safe_command_recommendation"] is None


def test_denied_batch_yields_no_cycle():
    b = _batch()
    denial = ba.record_human_batch_decision(b, ba.DECISION_DENY_BATCH, "Mahmoud")
    s = cy.build_research_cycle_spec(b, denial)
    assert s["verdict"] == cy.VERDICT_CYCLE_SPEC_REFUSED
    assert "batch_was_denied_no_cycle_may_exist" in s["blockers"]


def test_refused_decision_yields_no_cycle():
    b = _batch()
    refused = ba.record_human_batch_decision(b, "AUTO_APPROVE", "Mahmoud")
    s = cy.build_research_cycle_spec(b, refused)
    assert s["verdict"] == cy.VERDICT_CYCLE_SPEC_REFUSED
    assert "human_decision_not_recorded" in s["blockers"]


def test_tampered_batch_yields_no_cycle():
    b = _batch()
    approval = _approval(b)
    b["deviation_voids_batch"] = False
    s = cy.build_research_cycle_spec(b, approval)
    assert s["verdict"] == cy.VERDICT_CYCLE_SPEC_REFUSED
    assert "batch_invalid" in s["blockers"]
    assert any(x.startswith("batch_error:") for x in s["blockers"])


def test_decision_for_a_different_batch_yields_no_cycle():
    b1 = _batch()
    other_steps = _steps()
    other_steps[0]["description"] = "a different chain entirely"
    b2 = ba.compose_batch(_packet(), other_steps)
    approval_for_b2 = _approval(b2)
    s = cy.build_research_cycle_spec(b1, approval_for_b2)
    assert s["verdict"] == cy.VERDICT_CYCLE_SPEC_REFUSED
    assert "decision_covers_a_different_batch" in s["blockers"]


def test_refused_batch_yields_no_cycle():
    refused_batch = ba.compose_batch(None, _steps())
    s = cy.build_research_cycle_spec(refused_batch, _approval())
    assert s["verdict"] == cy.VERDICT_CYCLE_SPEC_REFUSED
    assert "no_composed_batch_for_a_cycle" in s["blockers"]


def test_missing_batch_refuses():
    s = cy.build_research_cycle_spec(None, _approval())
    assert s["verdict"] == cy.VERDICT_CYCLE_SPEC_REFUSED
    assert "batch_missing_or_not_a_dict" in s["blockers"]


# --------------------------------------------------------------------------- #
# constitution and bounded model
# --------------------------------------------------------------------------- #
def test_scheduler_states_are_the_closed_six():
    assert cy.SCHEDULER_STATES == (
        "AWAITING_HUMAN_ACTIVATION",
        "CYCLE_STEP_PENDING",
        "CYCLE_STEP_DONE_REPORTED",
        "STOPPED_FOR_HUMAN_REVIEW",
        "VOIDED_BY_DEVIATION",
        "CYCLE_COMPLETE_AWAITING_HUMAN_REVIEW",
    )
    b = _batch()
    s = cy.build_research_cycle_spec(b, _approval(b))
    assert s["initial_state"] == "AWAITING_HUMAN_ACTIVATION"


def test_bounded_execution_model_is_complete():
    b = _batch()
    s = cy.build_research_cycle_spec(b, _approval(b))
    joined = " ".join(s["bounded_execution_model"])
    assert "one_pass_only" in joined
    assert "monotonic_forward" in joined
    assert "hard_cap" in joined
    assert "no_retries_without_a_fresh_human_approval" in joined
    assert "no_loops" in joined
    assert "deviation_voids_the_cycle" in joined
    assert s["max_cycle_steps"] == cy.MAX_CYCLE_STEPS == ba.MAX_BATCH_STEPS


def test_no_implied_approval_and_no_scheduler_built():
    b = _batch()
    s = cy.build_research_cycle_spec(b, _approval(b))
    assert s["no_implied_approval_beyond_signed_batch"] is True
    assert s["spec_only_no_scheduler_built"] is True
    assert s["scheduler_built_by_this_contract"] is False
    assert s["deviation_voids_cycle"] is True
    assert s["resume_requires_fresh_human_approval"] is True
    joined = " ".join(s["refusal_rules"])
    assert "no_implied_approval_beyond_the_signed_batch_ever" in joined


def test_spec_is_inert_on_all_paths():
    b = _batch()
    specs = [
        cy.build_research_cycle_spec(b, _approval(b)),
        cy.build_research_cycle_spec(None, None),
    ]
    for s in specs:
        assert s["spec_is_in_memory_only"] is True
        assert s["human_review_required"] is True
        assert s["next_required_action"] == "HUMAN_APPROVED_RESULT_REPORTING_DESIGN"
        for key in (
            "executes", "writes_files", "writes_queue", "writes_ledger",
            "runs_research", "runs_scanner", "runs_simulation", "runs_backtest",
            "runs_optimization", "starts_scheduler", "starts_daemon",
            "starts_background_worker", "runs_loop", "advances_any_cycle",
            "fetches_data", "calls_api", "connects_broker", "connects_exchange",
            "uses_real_money", "uses_network", "uses_credentials",
            "contains_order_logic", "authorizes_paper_execution",
            "authorizes_micro_live", "authorizes_live_trading", "promotes_gate",
            "unlocks_downstream_gate",
        ):
            assert s[key] is False, key
        assert s["paper_trading_gate_locked"] is True
        assert s["micro_live_gate_locked"] is True
        assert s["live_gate_locked"] is True
    assert specs[0]["roadmap_link_id"] == "L4_scheduled_research_cycle_controller"
    assert specs[0]["roadmap_seq"] == 4


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #
def test_validate_passes_on_ready_and_refused():
    b = _batch()
    assert cy.validate_research_cycle_spec(
        cy.build_research_cycle_spec(b, _approval(b)))["valid"] is True
    assert cy.validate_research_cycle_spec(
        cy.build_research_cycle_spec(None, None))["valid"] is True


def test_validate_rejects_scheduler_built_claim():
    b = _batch()
    s = cy.build_research_cycle_spec(b, _approval(b))
    s["scheduler_built_by_this_contract"] = True
    v = cy.validate_research_cycle_spec(s)
    assert v["valid"] is False
    assert "scheduler_claimed_built" in v["errors"]
    s2 = cy.build_research_cycle_spec(b, _approval(b))
    s2["spec_only_no_scheduler_built"] = False
    v2 = cy.validate_research_cycle_spec(s2)
    assert v2["valid"] is False
    assert "spec_claims_to_build_scheduler" in v2["errors"]


def test_validate_rejects_auto_advance_for_ineligible_kind():
    b = _batch()
    s = cy.build_research_cycle_spec(b, _approval(b))
    s["cycle_steps"][1]["auto_advance_eligible_in_theory"] = True  # write_contract_tests
    v = cy.validate_research_cycle_spec(s)
    assert v["valid"] is False
    assert "auto_advance_granted_to_ineligible_kind" in v["errors"]


def test_validate_rejects_human_stops_removed():
    b = _batch()
    s = cy.build_research_cycle_spec(b, _approval(b))
    s["cycle_steps"][0]["must_stop_for_human"] = False
    v = cy.validate_research_cycle_spec(s)
    assert v["valid"] is False
    assert "first_step_does_not_require_human_activation" in v["errors"]
    s2 = cy.build_research_cycle_spec(b, _approval(b))
    s2["cycle_steps"][-1]["must_stop_for_human"] = False
    v2 = cy.validate_research_cycle_spec(s2)
    assert v2["valid"] is False
    assert "final_step_does_not_stop_for_human" in v2["errors"]


def test_validate_rejects_tampered_states_or_cap():
    b = _batch()
    s = cy.build_research_cycle_spec(b, _approval(b))
    s["scheduler_states"].append("RUNNING_UNATTENDED_FOREVER")
    v = cy.validate_research_cycle_spec(s)
    assert v["valid"] is False
    assert "scheduler_states_tampered" in v["errors"]
    s2 = cy.build_research_cycle_spec(b, _approval(b))
    s2["max_cycle_steps"] = 999
    v2 = cy.validate_research_cycle_spec(s2)
    assert v2["valid"] is False
    assert "hard_cap_tampered" in v2["errors"]


def test_validate_rejects_refused_spec_with_recommendation():
    s = cy.build_research_cycle_spec(None, None)
    s["next_safe_command_recommendation"] = "HUMAN_ISSUES_STEP_1_COMMAND"
    v = cy.validate_research_cycle_spec(s)
    assert v["valid"] is False
    assert "refused_spec_carries_a_recommendation" in v["errors"]


def test_validate_rejects_dropped_constitution_flags():
    b = _batch()
    for flag, err in (
        ("no_implied_approval_beyond_signed_batch", "implied_approval_allowed"),
        ("deviation_voids_cycle", "deviation_rule_dropped"),
        ("resume_requires_fresh_human_approval", "resume_rule_dropped"),
        ("output_is_a_recommendation_only", "output_not_recommendation_only"),
    ):
        s = cy.build_research_cycle_spec(b, _approval(b))
        s[flag] = False
        v = cy.validate_research_cycle_spec(s)
        assert v["valid"] is False, flag
        assert err in v["errors"], flag


def test_validate_rejects_unlocked_gate_or_capability():
    b = _batch()
    s = cy.build_research_cycle_spec(b, _approval(b))
    s["micro_live_gate_locked"] = False
    v = cy.validate_research_cycle_spec(s)
    assert v["valid"] is False
    assert any("gate_not_locked:micro_live_gate_locked" in e for e in v["errors"])
    for cap in ("starts_scheduler", "starts_daemon", "starts_background_worker",
                "runs_loop", "advances_any_cycle"):
        s2 = cy.build_research_cycle_spec(b, _approval(b))
        s2[cap] = True
        v2 = cy.validate_research_cycle_spec(s2)
        assert v2["valid"] is False, cap
        assert any("capability_not_false:" + cap in e for e in v2["errors"])


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #
def test_render_markdown_ready_and_refused():
    b = _batch()
    md = cy.render_research_cycle_spec_markdown(
        cy.build_research_cycle_spec(b, _approval(b)))
    assert md.startswith(
        "# SPARTA Research Cycle Scheduler SPEC (SPEC ONLY, NO SCHEDULER BUILT)")
    assert "HUMAN STOP" in md
    assert "IN THEORY ONLY" in md
    assert "this spec starts nothing" in md
    assert "LOCKED" in md
    md2 = cy.render_research_cycle_spec_markdown(
        cy.build_research_cycle_spec(None, None))
    assert "refused; no cycle may exist" in md2


# --------------------------------------------------------------------------- #
# label / posture / no banned imports
# --------------------------------------------------------------------------- #
def test_label_is_read_only_spec_label():
    assert cy.get_research_cycle_scheduler_spec_label() == cy.CYCLE_SPEC_LABEL
    assert "READ-ONLY" in cy.CYCLE_SPEC_LABEL
    assert "NO SCHEDULER BUILT" in cy.CYCLE_SPEC_LABEL
    assert cy.CYCLE_SPEC_MODE == "RESEARCH_ONLY"


def test_action_carries_no_execution_or_promotion_verbs():
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE", "EXECUTION",
                   "BACKTEST", "BASELINE", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in cy.NEXT_REQUIRED_ACTION.upper(), banned


def test_module_imports_no_network_scheduler_or_credential_modules():
    with open(cy.__file__, "r", encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    banned = {"urllib", "requests", "socket", "http", "ftplib", "ccxt", "databento",
              "dotenv", "smtplib", "subprocess", "websocket", "websockets", "aiohttp",
              "schedule", "apscheduler", "threading", "multiprocessing", "asyncio",
              "sched", "time"}
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imported.add(n.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert not (imported & banned)
