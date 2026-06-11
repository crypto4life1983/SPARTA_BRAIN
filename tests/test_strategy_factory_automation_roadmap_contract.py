"""Tests for the SPARTA Strategy Factory Automation Roadmap Contract (READ-ONLY).

Everything here is pure and in-memory; no network, no credentials, no API call, no
scheduler, no queue, no file write, no gate is unlocked. The roadmap designs the
automation layer and builds none of it; trading execution is excluded outright."""

from __future__ import annotations

import ast

import sparta_commander.strategy_factory_automation_roadmap_contract as rm


# --------------------------------------------------------------------------- #
# the roadmap is READY, builds nothing, excludes execution
# --------------------------------------------------------------------------- #
def test_roadmap_ready_and_builds_nothing():
    r = rm.build_automation_roadmap()
    assert r["verdict"] == rm.VERDICT_ROADMAP_READY
    assert r["roadmap_builds_nothing"] is True
    assert r["execution_layer_excluded"] is True
    assert r["every_approval_remains_human"] is True
    assert r["modifies_crypto_d1_lane"] is False
    assert r["blockers"] == []
    assert r["next_required_action"] == (
        "HUMAN_APPROVED_INTAKE_TO_ORCHESTRATOR_ADAPTER_SPEC"
    )


def test_existing_components_cover_the_inventory():
    comps = " ".join(c["component"] for c in rm.existing_components())
    for needed in ("strategy_idea_intake_automation_contract", "orchestrator",
                   "research_bundle_automation_controller",
                   "overnight_research_autopilot_controller",
                   "mission_flow", "profit_brain", "JARVIS",
                   "arbitrage_factory_v1"):
        assert needed in comps, needed


def test_all_six_missing_links_have_human_gates():
    links = rm.missing_automation_links()
    assert [l["link_id"] for l in links] == [
        "L1_intake_to_queue_adapter",
        "L2_lane_specific_approval_packet_generator",
        "L3_batch_approval_schema",
        "L4_scheduled_research_cycle_controller",
        "L5_result_notification_reporting_layer",
        "L6_stop_fail_refuse_rules",
    ]
    for l in links:
        assert l["purpose"]
        assert l["human_gate"]


def test_batch_approval_requires_full_enumeration():
    l3 = next(l for l in rm.missing_automation_links()
              if l["link_id"] == "L3_batch_approval_schema")
    assert "PRE-REGISTERED" in l3["purpose"]
    assert "voids the batch" in l3["human_gate"]


def test_scheduler_can_never_extend_its_own_scope():
    l4 = next(l for l in rm.missing_automation_links()
              if l["link_id"] == "L4_scheduled_research_cycle_controller")
    assert "never approve, promote, or extend its own scope" in l4["human_gate"]


# --------------------------------------------------------------------------- #
# automation levels: 1-4 automatable, 5 human, execution EXCLUDED
# --------------------------------------------------------------------------- #
def test_levels_one_to_four_automated_level_five_human():
    levels = {l["level"]: l for l in rm.automation_levels() if l["level"] is not None}
    for n in (1, 2, 3, 4):
        assert levels[n]["automated"] is True
    assert levels[5]["automated"] is False
    assert "never make them" in levels[5]["note"]


def test_trading_execution_is_excluded_not_a_level():
    excluded = [l for l in rm.automation_levels() if l.get("excluded")]
    assert len(excluded) == 1
    e = excluded[0]
    assert e["name"] == "trading_execution"
    assert e["level"] is None
    assert e["automated"] is False
    assert "EXCLUDED" in e["note"]
    assert "top-level" in e["note"]


def test_only_level_one_and_five_already_built():
    levels = rm.automation_levels()
    built = {l["name"] for l in levels if l.get("already_built")}
    assert built == {"idea_review_automation", "human_review_and_gate_decisions"}


# --------------------------------------------------------------------------- #
# safety rules and build sequence
# --------------------------------------------------------------------------- #
def test_safety_rules_are_the_required_six():
    rules = rm.safety_rules()
    assert len(rules) == 6
    joined = " ".join(rules)
    assert "no_broker_or_exchange_credentials" in joined
    assert "no_order_placement" in joined
    assert "no_paper_micro_live_or_live" in joined
    assert "no_gate_unlock" in joined
    assert "no_autonomous_promotion" in joined
    assert "require_human_review" in joined


def test_build_sequence_is_binding_and_ordered():
    seq = rm.build_sequence()
    assert [b["seq"] for b in seq] == [1, 2, 3, 4, 5, 6]
    blocks = [b["block"] for b in seq]
    assert blocks == [
        "intake_to_orchestrator_adapter_contract",
        "strategy_idea_approval_packet_schema_contract",
        "batch_approval_contract",
        "research_cycle_scheduler_spec_contract",
        "notification_reporting_contract",
        "dashboard_jarvis_automation_sync",
    ]
    # the scheduler is spec-first
    s4 = seq[3]
    assert "spec first" in s4["delivers"]


def test_automatic_vs_human_split_is_explicit():
    avh = rm.automatic_vs_human()
    assert avh["becomes_automatic"]
    assert avh["remains_human_approved"]
    human = " ".join(avh["remains_human_approved"])
    assert "every approval" in human
    assert "every promotion" in human
    assert "excluded" in human
    automatic = " ".join(avh["becomes_automatic"])
    assert "triage" in automatic
    assert "APPROVED batches" in automatic
    assert "stopping on any blocker" in automatic


def test_accessors_return_copies():
    a = rm.missing_automation_links()
    a[0]["link_id"] = "tampered"
    assert rm.missing_automation_links()[0]["link_id"] != "tampered"
    s = rm.safety_rules()
    s.append("tampered")
    assert "tampered" not in rm.safety_rules()
    avh = rm.automatic_vs_human()
    avh["becomes_automatic"].append("tampered")
    assert "tampered" not in rm.automatic_vs_human()["becomes_automatic"]


# --------------------------------------------------------------------------- #
# capability posture
# --------------------------------------------------------------------------- #
def test_roadmap_runs_schedules_queues_nothing():
    r = rm.build_automation_roadmap()
    for key in (
        "executes", "writes_files", "runs_scanner", "runs_simulation", "runs_backtest",
        "runs_optimization", "starts_scheduler", "queues_anything", "fetches_data",
        "calls_api", "connects_broker", "connects_exchange", "uses_real_money",
        "uses_network", "uses_credentials", "contains_order_logic",
        "authorizes_paper_execution", "authorizes_micro_live",
        "authorizes_live_trading", "promotes_gate", "unlocks_downstream_gate",
    ):
        assert r[key] is False, key
    assert r["paper_trading_gate_locked"] is True
    assert r["micro_live_gate_locked"] is True
    assert r["live_gate_locked"] is True


def test_build_is_deterministic():
    assert rm.build_automation_roadmap() == rm.build_automation_roadmap()


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #
def test_validate_passes_on_built_roadmap():
    r = rm.build_automation_roadmap()
    assert rm.validate_automation_roadmap(r)["valid"] is True


def test_validate_rejects_unexcluded_execution():
    r = rm.build_automation_roadmap()
    for l in r["automation_levels"]:
        if l.get("excluded"):
            l["excluded"] = False
    v = rm.validate_automation_roadmap(r)
    assert v["valid"] is False
    assert "trading_execution_not_excluded" in v["errors"]


def test_validate_rejects_automated_human_level():
    r = rm.build_automation_roadmap()
    for l in r["automation_levels"]:
        if l.get("level") == 5:
            l["automated"] = True
    v = rm.validate_automation_roadmap(r)
    assert v["valid"] is False
    assert "human_review_level_marked_automated" in v["errors"]


def test_validate_rejects_link_without_human_gate():
    r = rm.build_automation_roadmap()
    r["missing_automation_links"][0]["human_gate"] = ""
    v = rm.validate_automation_roadmap(r)
    assert v["valid"] is False
    assert "link_missing_human_gate_or_fields" in v["errors"]


def test_validate_rejects_missing_safety_rule():
    r = rm.build_automation_roadmap()
    r["safety_rules"] = [x for x in r["safety_rules"]
                         if "no_order_placement" not in x]
    v = rm.validate_automation_roadmap(r)
    assert v["valid"] is False
    assert ("safety_rules_not_six" in v["errors"]
            or any("no_order_placement" in e for e in v["errors"]))


def test_validate_rejects_broken_sequence():
    r = rm.build_automation_roadmap()
    r["build_sequence"] = list(reversed(r["build_sequence"]))
    v = rm.validate_automation_roadmap(r)
    assert v["valid"] is False
    assert "build_sequence_broken" in v["errors"]


def test_validate_rejects_human_approvals_dropped():
    r = rm.build_automation_roadmap()
    r["every_approval_remains_human"] = False
    v = rm.validate_automation_roadmap(r)
    assert v["valid"] is False
    assert "approvals_not_human" in v["errors"]


def test_validate_rejects_building_roadmap():
    r = rm.build_automation_roadmap()
    r["roadmap_builds_nothing"] = False
    v = rm.validate_automation_roadmap(r)
    assert v["valid"] is False
    assert "roadmap_claims_to_build" in v["errors"]


def test_validate_rejects_started_scheduler_or_queue():
    r = rm.build_automation_roadmap()
    r["starts_scheduler"] = True
    v = rm.validate_automation_roadmap(r)
    assert v["valid"] is False
    assert any("capability_not_false:starts_scheduler" in e for e in v["errors"])
    r2 = rm.build_automation_roadmap()
    r2["queues_anything"] = True
    v2 = rm.validate_automation_roadmap(r2)
    assert v2["valid"] is False
    assert any("capability_not_false:queues_anything" in e for e in v2["errors"])


def test_validate_rejects_unlocked_gate():
    r = rm.build_automation_roadmap()
    r["micro_live_gate_locked"] = False
    v = rm.validate_automation_roadmap(r)
    assert v["valid"] is False
    assert any("gate_not_locked:micro_live_gate_locked" in e for e in v["errors"])


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #
def test_render_markdown_is_string():
    md = rm.render_automation_roadmap_markdown(rm.build_automation_roadmap())
    assert md.startswith("# SPARTA Strategy Factory Automation Roadmap")
    assert "EXCLUDED (not deferred)" in md
    assert "L3_batch_approval_schema" in md
    assert "Remains human-approved" in md
    assert "LOCKED" in md


# --------------------------------------------------------------------------- #
# label / posture / no banned imports
# --------------------------------------------------------------------------- #
def test_label_is_read_only_label():
    assert rm.get_automation_roadmap_label() == rm.ROADMAP_LABEL
    assert "READ-ONLY" in rm.ROADMAP_LABEL
    assert rm.ROADMAP_MODE == "RESEARCH_ONLY"


def test_action_carries_no_execution_or_promotion_verbs():
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE", "EXECUTION",
                   "BACKTEST", "BASELINE", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in rm.NEXT_REQUIRED_ACTION.upper(), banned


def test_module_imports_no_network_subprocess_or_credential_modules():
    with open(rm.__file__, "r", encoding="utf-8") as fh:
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
