"""Tests for the SPARTA Strategy Idea Batch Approval Contract (READ-ONLY).

Everything here is pure and in-memory; no network, no credentials, no API call, no
queue/ledger write, no scheduler, no gate is unlocked. A batch binds one unsigned
packet to one fully enumerated research-only step chain; one human signature covers
exactly that chain and any deviation voids it."""

from __future__ import annotations

import ast

import sparta_commander.intake_to_orchestrator_adapter_contract as ad
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


# --------------------------------------------------------------------------- #
# composing a batch
# --------------------------------------------------------------------------- #
def test_packet_plus_steps_composes_batch():
    b = ba.compose_batch(_packet(), _steps())
    assert b["verdict"] == ba.VERDICT_BATCH_COMPOSED
    assert b["blockers"] == []
    assert b["batch_id"].startswith("batch_")
    assert b["covered_packet_id"] == _packet()["packet_id"]
    assert b["lane"] == it.LANE_ARBITRAGE
    assert b["step_count"] == 5


def test_batch_is_born_unsigned_with_deviation_rule():
    b = ba.compose_batch(_packet(), _steps())
    assert b["signed"] is False
    assert b["human_signature"] is None
    assert b["human_decision"] is None
    assert b["one_signature_covers_only_the_enumerated_steps"] is True
    assert b["deviation_voids_batch"] is True
    assert b["resume_after_stop_requires_fresh_human_approval"] is True
    assert b["no_implied_or_extended_grants"] is True
    assert b["composing_a_batch_starts_no_work"] is True


def test_batch_id_is_deterministic_and_chain_sensitive():
    a = ba.compose_batch(_packet(), _steps())
    b = ba.compose_batch(_packet(), _steps())
    assert a == b
    different = _steps()
    different[0]["description"] = "a different first step"
    c = ba.compose_batch(_packet(), different)
    assert c["batch_id"] != a["batch_id"]


def test_every_step_keeps_its_own_refuse_by_default_runner():
    b = ba.compose_batch(_packet(), _steps())
    for s in b["enumerated_steps"]:
        assert s["step_runs_via_its_own_refuse_by_default_runner"] is True


# --------------------------------------------------------------------------- #
# refusals at composition
# --------------------------------------------------------------------------- #
def test_refused_packet_cannot_be_batched():
    refused_packet = pk.generate_approval_packet(None)
    b = ba.compose_batch(refused_packet, _steps())
    assert b["verdict"] == ba.VERDICT_BATCH_REFUSED
    assert "no_generated_packet_to_batch" in b["blockers"]
    assert b["enumerated_steps"] == []


def test_missing_or_invalid_packet_refuses():
    assert "packet_missing_or_not_a_dict" in ba.compose_batch(None, _steps())["blockers"]
    tampered = _packet()
    tampered["signed"] = True
    b = ba.compose_batch(tampered, _steps())
    assert b["verdict"] == ba.VERDICT_BATCH_REFUSED
    assert "packet_invalid" in b["blockers"]


def test_empty_or_oversized_steps_refuse():
    assert "steps_missing_or_empty" in ba.compose_batch(_packet(), [])["blockers"]
    too_many = [
        {"seq": i + 1, "kind": "build_contract_module", "description": "step"}
        for i in range(ba.MAX_BATCH_STEPS + 1)
    ]
    b = ba.compose_batch(_packet(), too_many)
    assert "too_many_steps_for_one_signature" in b["blockers"]


def test_non_contiguous_steps_refuse():
    steps = _steps()
    steps[2]["seq"] = 7
    b = ba.compose_batch(_packet(), steps)
    assert b["verdict"] == ba.VERDICT_BATCH_REFUSED
    assert any("step_sequence_not_contiguous" in x for x in b["blockers"])


def test_step_kind_outside_catalog_refuses():
    steps = _steps()
    steps[1]["kind"] = "send_live_orders"
    b = ba.compose_batch(_packet(), steps)
    assert b["verdict"] == ba.VERDICT_BATCH_REFUSED
    assert any("step_kind_not_in_closed_catalog" in x for x in b["blockers"])


def test_forbidden_token_in_description_refuses_whole_batch():
    for bad in ("then execute the trades", "place an order", "use my api key",
                "go live with it", "promote to micro"):
        steps = _steps()
        steps[4]["description"] = "review results and " + bad
        b = ba.compose_batch(_packet(), steps)
        assert b["verdict"] == ba.VERDICT_BATCH_REFUSED, bad
        assert any("forbidden_step_token" in x for x in b["blockers"])


def test_catalog_has_no_execution_kind():
    joined = " ".join(ba.ALLOWED_STEP_KINDS)
    for absent in ("execution", "order", "trade", "fetch", "credential",
                   "paper", "micro", "promote"):
        assert absent not in joined, absent


# --------------------------------------------------------------------------- #
# recording the human decision
# --------------------------------------------------------------------------- #
def test_human_approval_is_recorded_with_signer():
    b = ba.compose_batch(_packet(), _steps())
    r = ba.record_human_batch_decision(b, ba.DECISION_APPROVE_BATCH, "Mahmoud")
    assert r["verdict"] == ba.VERDICT_DECISION_RECORDED
    assert r["decision"] == ba.DECISION_APPROVE_BATCH
    assert r["signed_by"] == "Mahmoud"
    assert r["batch_id"] == b["batch_id"]
    assert r["recording_a_decision_starts_no_work"] is True


def test_denial_is_recorded_too():
    b = ba.compose_batch(_packet(), _steps())
    r = ba.record_human_batch_decision(b, ba.DECISION_DENY_BATCH, "Mahmoud")
    assert r["verdict"] == ba.VERDICT_DECISION_RECORDED
    assert r["decision"] == ba.DECISION_DENY_BATCH


def test_decision_outside_closed_options_is_refused():
    b = ba.compose_batch(_packet(), _steps())
    r = ba.record_human_batch_decision(b, "AUTO_APPROVE_EVERYTHING", "Mahmoud")
    assert r["verdict"] == ba.VERDICT_DECISION_REFUSED
    assert "decision_not_in_closed_options" in r["blockers"]


def test_decision_without_signer_is_refused():
    b = ba.compose_batch(_packet(), _steps())
    for bad in (None, "", "   ", 42):
        r = ba.record_human_batch_decision(b, ba.DECISION_APPROVE_BATCH, bad)
        assert r["verdict"] == ba.VERDICT_DECISION_REFUSED
        assert "signature_missing_a_decision_needs_a_human_name" in r["blockers"]


def test_decision_on_refused_or_tampered_batch_is_refused():
    refused = ba.compose_batch(None, _steps())
    r = ba.record_human_batch_decision(refused, ba.DECISION_APPROVE_BATCH, "Mahmoud")
    assert r["verdict"] == ba.VERDICT_DECISION_REFUSED
    assert "no_composed_batch_to_decide_on" in r["blockers"]
    tampered = ba.compose_batch(_packet(), _steps())
    tampered["deviation_voids_batch"] = False
    r2 = ba.record_human_batch_decision(tampered, ba.DECISION_APPROVE_BATCH, "Mahmoud")
    assert r2["verdict"] == ba.VERDICT_DECISION_REFUSED
    assert "batch_invalid" in r2["blockers"]


# --------------------------------------------------------------------------- #
# posture
# --------------------------------------------------------------------------- #
def test_batch_is_inert_on_all_paths():
    batches = [
        ba.compose_batch(_packet(), _steps()),
        ba.compose_batch(None, _steps()),
    ]
    for b in batches:
        assert b["batch_is_in_memory_only"] is True
        assert b["human_review_required"] is True
        assert b["next_required_action"] == "HUMAN_APPROVED_RESEARCH_CYCLE_SPEC"
        for key in (
            "executes", "writes_files", "writes_queue", "writes_ledger",
            "runs_research", "runs_scanner", "runs_simulation", "runs_backtest",
            "runs_optimization", "starts_scheduler", "fetches_data", "calls_api",
            "connects_broker", "connects_exchange", "uses_real_money",
            "uses_network", "uses_credentials", "contains_order_logic",
            "authorizes_paper_execution", "authorizes_micro_live",
            "authorizes_live_trading", "promotes_gate", "unlocks_downstream_gate",
        ):
            assert b[key] is False, key
        assert b["paper_trading_gate_locked"] is True
        assert b["micro_live_gate_locked"] is True
        assert b["live_gate_locked"] is True
    assert batches[0]["roadmap_link_id"] == "L3_batch_approval_schema"
    assert batches[0]["roadmap_seq"] == 3


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #
def test_validate_passes_on_composed_and_refused():
    assert ba.validate_batch(ba.compose_batch(_packet(), _steps()))["valid"] is True
    assert ba.validate_batch(ba.compose_batch(None, _steps()))["valid"] is True


def test_validate_decision_passes_on_recorded_and_refused():
    b = ba.compose_batch(_packet(), _steps())
    rec = ba.record_human_batch_decision(b, ba.DECISION_APPROVE_BATCH, "Mahmoud")
    ref = ba.record_human_batch_decision(b, "BAD", "Mahmoud")
    assert ba.validate_batch_decision(rec)["valid"] is True
    assert ba.validate_batch_decision(ref)["valid"] is True


def test_validate_rejects_dropped_deviation_rule():
    b = ba.compose_batch(_packet(), _steps())
    b["deviation_voids_batch"] = False
    v = ba.validate_batch(b)
    assert v["valid"] is False
    assert "deviation_rule_dropped" in v["errors"]
    b2 = ba.compose_batch(_packet(), _steps())
    b2["one_signature_covers_only_the_enumerated_steps"] = False
    v2 = ba.validate_batch(b2)
    assert v2["valid"] is False
    assert "signature_scope_widened" in v2["errors"]
    b3 = ba.compose_batch(_packet(), _steps())
    b3["no_implied_or_extended_grants"] = False
    v3 = ba.validate_batch(b3)
    assert v3["valid"] is False
    assert "implied_grants_allowed" in v3["errors"]


def test_validate_rejects_signed_at_composition():
    b = ba.compose_batch(_packet(), _steps())
    b["signed"] = True
    v = ba.validate_batch(b)
    assert v["valid"] is False
    assert "batch_claims_to_be_signed" in v["errors"]


def test_validate_rejects_smuggled_step():
    b = ba.compose_batch(_packet(), _steps())
    b["enumerated_steps"].append({
        "seq": 6, "kind": "build_contract_module",
        "description": "then execute live orders",
        "step_runs_via_its_own_refuse_by_default_runner": True,
    })
    b["step_count"] = 6
    v = ba.validate_batch(b)
    assert v["valid"] is False
    assert "step_carries_forbidden_token" in v["errors"]


def test_validate_rejects_step_count_mismatch_and_bypass():
    b = ba.compose_batch(_packet(), _steps())
    b["step_count"] = 99
    v = ba.validate_batch(b)
    assert v["valid"] is False
    assert "step_count_mismatch" in v["errors"]
    b2 = ba.compose_batch(_packet(), _steps())
    b2["enumerated_steps"][0]["step_runs_via_its_own_refuse_by_default_runner"] = False
    v2 = ba.validate_batch(b2)
    assert v2["valid"] is False
    assert "step_bypasses_refuse_by_default_runner" in v2["errors"]


def test_validate_rejects_refused_decision_with_decision():
    b = ba.compose_batch(_packet(), _steps())
    r = ba.record_human_batch_decision(b, "BAD", "Mahmoud")
    r["decision"] = ba.DECISION_APPROVE_BATCH
    v = ba.validate_batch_decision(r)
    assert v["valid"] is False
    assert "refused_decision_carries_a_decision" in v["errors"]


def test_validate_rejects_unlocked_gate_or_capability():
    b = ba.compose_batch(_packet(), _steps())
    b["live_gate_locked"] = False
    v = ba.validate_batch(b)
    assert v["valid"] is False
    assert any("gate_not_locked:live_gate_locked" in e for e in v["errors"])
    b2 = ba.compose_batch(_packet(), _steps())
    b2["starts_scheduler"] = True
    v2 = ba.validate_batch(b2)
    assert v2["valid"] is False
    assert any("capability_not_false:starts_scheduler" in e for e in v2["errors"])


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #
def test_render_markdown_composed_and_refused():
    md = ba.render_batch_markdown(ba.compose_batch(_packet(), _steps()))
    assert md.startswith("# SPARTA Strategy Idea Batch Approval (UNSIGNED REQUEST)")
    assert "VOIDS the batch" in md
    assert "the ENTIRE grant, nothing else" in md
    assert "LOCKED" in md
    md2 = ba.render_batch_markdown(ba.compose_batch(None, _steps()))
    assert "refused; nothing can be signed" in md2


# --------------------------------------------------------------------------- #
# label / posture / no banned imports
# --------------------------------------------------------------------------- #
def test_label_is_read_only_label():
    assert ba.get_strategy_idea_batch_approval_label() == ba.BATCH_LABEL
    assert "READ-ONLY" in ba.BATCH_LABEL
    assert ba.BATCH_MODE == "RESEARCH_ONLY"


def test_action_carries_no_execution_or_promotion_verbs():
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE", "EXECUTION",
                   "BACKTEST", "BASELINE", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in ba.NEXT_REQUIRED_ACTION.upper(), banned


def test_module_imports_no_network_subprocess_or_credential_modules():
    with open(ba.__file__, "r", encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    banned = {"urllib", "requests", "socket", "http", "ftplib", "ccxt", "databento",
              "dotenv", "smtplib", "subprocess", "websocket", "websockets", "aiohttp",
              "schedule", "apscheduler"}
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imported.add(n.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert not (imported & banned)
