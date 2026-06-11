"""SPARTA Strategy Factory Automation Roadmap Contract (READ-ONLY, ROADMAP ONLY).

A PURE, stdlib-only, read-only module that DESIGNS -- and explicitly does NOT build --
the orchestration layer that connects the already-built SPARTA research components into
ONE automated research workflow:

    idea -> intake triage -> lane routing -> orchestrator queue -> approval packet ->
    human approval -> research-only run -> result review -> human gate decision.

The inventory finding this roadmap answers: the parts exist, the connecting links do
not. This contract freezes WHAT the links are, in WHAT order they are built, WHICH
automation levels are in scope, and -- most importantly -- WHAT can never be automated:
trading execution is EXCLUDED BY DESIGN (no level covers it, no future level may add it
without a top-level architecture authorization outside this roadmap), and every approval
checkpoint remains human.

It RUNS NOTHING and WRITES NOTHING: no data fetch, no scanner, no simulation, no
backtest, no API call, no credentials, no scheduler started, no queue touched. It is a
design document with a validator.

Public API:
  - ROADMAP_SCHEMA_VERSION / ROADMAP_LABEL / ROADMAP_MODE
  - VERDICT_ROADMAP_READY / NEXT_REQUIRED_ACTION
  - EXISTING_COMPONENTS / MISSING_AUTOMATION_LINKS / AUTOMATION_LEVELS
  - SAFETY_RULES / BUILD_SEQUENCE / AUTOMATIC_VS_HUMAN
  - get_automation_roadmap_label()
  - existing_components() / missing_automation_links() / automation_levels()
  - safety_rules() / build_sequence() / automatic_vs_human()
  - build_automation_roadmap()
  - validate_automation_roadmap(roadmap)
  - render_automation_roadmap_markdown(roadmap)
"""

from __future__ import annotations

import copy
from typing import Any

ROADMAP_SCHEMA_VERSION = "strategy_factory_automation_roadmap_contract.v1"
ROADMAP_LABEL = (
    "SPARTA Strategy Factory Automation Roadmap (READ-ONLY, ROADMAP ONLY)"
)
ROADMAP_MODE = "RESEARCH_ONLY"

VERDICT_ROADMAP_READY = "AUTOMATION_ROADMAP_READY"

# The roadmap's own first step: the intake-to-orchestrator adapter SPEC (a document).
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_INTAKE_TO_ORCHESTRATOR_ADAPTER_SPEC"

# --- 1: components already built ---------------------------------------------
EXISTING_COMPONENTS: list[dict[str, str]] = [
    {"component": "strategy_idea_intake_automation_contract",
     "role": "front door: idea -> YES/NO/MAYBE -> lane -> suggested next safe command"},
    {"component": "orchestrator / queue stack "
                  "(orchestrator_contract, queue_planner/reader/schema, run_queue*)",
     "role": "plans and sequences research bundles with approval packets"},
    {"component": "strategy_factory_research_bundle_automation_controller",
     "role": "sequences research bundle proposals (research-only, human-started)"},
    {"component": "strategy_factory_overnight_research_autopilot_controller",
     "role": "overnight research sequencing producing proposals, never actions"},
    {"component": "mission_flow_bundle_registry + mission_flow_status",
     "role": "single source of truth for stage, next action, lane states, gates"},
    {"component": "profit_brain + daily_profit_brain_runner",
     "role": "daily research-status snapshots, alerts, opportunity scoring"},
    {"component": "JARVIS / dashboard / Telegram surfaces",
     "role": "read-only status, briefs, and an approval ledger (no action execution)"},
    {"component": "arbitrage_factory_v1 readiness + scanner spec",
     "role": "second research lane with its own constitution and frozen scanner spec"},
]

# --- 2: missing automation links ----------------------------------------------
MISSING_AUTOMATION_LINKS: list[dict[str, Any]] = [
    {"link_id": "L1_intake_to_queue_adapter",
     "purpose": "turn an intake YES decision into a queued, lane-routed research "
                "proposal automatically (proposal only, runs nothing)",
     "human_gate": "queued proposals are inert until a human approves their packet"},
    {"link_id": "L2_lane_specific_approval_packet_generator",
     "purpose": "auto-generate the approval packet for a queued proposal using the "
                "lane's own contract chain (crypto-d1 pattern vs arbitrage roadmap)",
     "human_gate": "the packet is a request; only a human signature activates it"},
    {"link_id": "L3_batch_approval_schema",
     "purpose": "let ONE human approval cover a whole PRE-REGISTERED chain "
                "(spec -> runner build -> dry run -> persisted run -> review) with "
                "every step still self-gating and refuse-by-default",
     "human_gate": "the batch must be fully enumerated up front; any deviation from "
                   "the enumerated steps voids the batch and stops the chain"},
    {"link_id": "L4_scheduled_research_cycle_controller",
     "purpose": "run ALREADY-APPROVED research cycles on a schedule (research-only "
                "runners with frozen inputs), notify results, and stop",
     "human_gate": "only batches approved under L3 may be scheduled; the scheduler "
                   "can never approve, promote, or extend its own scope"},
    {"link_id": "L5_result_notification_reporting_layer",
     "purpose": "push run results, reviews, and PASS/WATCH/FAIL verdicts to "
                "dashboard/JARVIS/Telegram as read-only notifications",
     "human_gate": "notifications carry suggested next commands, never act on them"},
    {"link_id": "L6_stop_fail_refuse_rules",
     "purpose": "uniform halt semantics: any blocker, validator failure, missing "
                "input, or safety-flag anomaly stops the chain, writes a refusal "
                "record, and waits for a human",
     "human_gate": "a stopped chain can only be resumed by a fresh human approval"},
]

# --- 3: automation levels (execution is EXCLUDED, not merely locked) ----------
AUTOMATION_LEVELS: list[dict[str, Any]] = [
    {"level": 1, "name": "idea_review_automation",
     "scope": "intake triage answers YES/NO/MAYBE deterministically",
     "automated": True, "already_built": True},
    {"level": 2, "name": "routing_automation",
     "scope": "YES ideas are routed to a lane and queued as proposals (link L1)",
     "automated": True, "already_built": False},
    {"level": 3, "name": "approval_packet_generation",
     "scope": "packets for queued proposals are generated automatically (link L2/L3)",
     "automated": True, "already_built": False},
    {"level": 4, "name": "research_only_scheduled_runs",
     "scope": "approved batches run on schedule with frozen inputs (link L4/L5)",
     "automated": True, "already_built": False},
    {"level": 5, "name": "human_review_and_gate_decisions",
     "scope": "every approval, every review verdict, every gate decision",
     "automated": False, "already_built": True,
     "note": "permanently human; automation may PREPARE these decisions, never make them"},
    {"level": None, "name": "trading_execution",
     "scope": "order placement, paper/micro-live/live, broker/exchange connectivity",
     "automated": False, "already_built": False, "excluded": True,
     "note": "EXCLUDED from this roadmap entirely; requires a future top-level "
             "architecture authorization after full risk review, outside this design"},
]

# --- 4: safety rules (apply to every link and level) ---------------------------
SAFETY_RULES: list[str] = [
    "no_broker_or_exchange_credentials_anywhere_in_the_automation_chain",
    "no_order_placement_code_may_exist_in_any_linked_module",
    "no_paper_micro_live_or_live_runs_are_ever_schedulable",
    "no_gate_unlock_may_be_performed_or_prepared_by_automation",
    "no_autonomous_promotion_verdict_upgrades_require_a_human",
    "all_research_outputs_require_human_review_before_any_next_step",
]

# --- 5: recommended build sequence (binding order) -----------------------------
BUILD_SEQUENCE: list[dict[str, Any]] = [
    {"seq": 1, "block": "intake_to_orchestrator_adapter_contract",
     "delivers": "link L1: intake YES -> queued lane-routed proposal"},
    {"seq": 2, "block": "strategy_idea_approval_packet_schema_contract",
     "delivers": "link L2: auto-generated, lane-aware approval packets"},
    {"seq": 3, "block": "batch_approval_contract",
     "delivers": "link L3: one signature covers one fully enumerated chain"},
    {"seq": 4, "block": "research_cycle_scheduler_spec_contract",
     "delivers": "link L4 spec first (a document); the scheduler itself is a later, "
                 "separately approved build"},
    {"seq": 5, "block": "notification_reporting_contract",
     "delivers": "link L5: results -> dashboard/JARVIS/Telegram, read-only"},
    {"seq": 6, "block": "dashboard_jarvis_automation_sync",
     "delivers": "surfaces the whole automation state in /guide and JARVIS answers"},
]

# --- what becomes automatic vs what stays human --------------------------------
AUTOMATIC_VS_HUMAN: dict[str, list[str]] = {
    "becomes_automatic": [
        "idea triage (YES/NO/MAYBE) and lane routing",
        "queuing routed proposals and generating their approval packets",
        "running APPROVED batches on schedule with frozen inputs",
        "producing reports, reviews drafts, and notifications",
        "stopping on any blocker and writing the refusal record",
    ],
    "remains_human_approved": [
        "every approval packet signature (single or batch)",
        "every review verdict acceptance and every gate decision",
        "every schedule activation and every scope change",
        "every promotion of anything, ever",
        "anything touching execution, which is excluded outright",
    ],
}


def get_automation_roadmap_label() -> str:
    """Human label for the recognized automation roadmap contract."""
    return ROADMAP_LABEL


def existing_components() -> list[dict[str, str]]:
    """Return fresh copies of the already-built component inventory. Pure."""
    return [dict(c) for c in EXISTING_COMPONENTS]


def missing_automation_links() -> list[dict[str, Any]]:
    """Return fresh copies of the missing-link definitions. Pure."""
    return [dict(l) for l in MISSING_AUTOMATION_LINKS]


def automation_levels() -> list[dict[str, Any]]:
    """Return fresh copies of the automation levels. Pure."""
    return [dict(l) for l in AUTOMATION_LEVELS]


def safety_rules() -> list[str]:
    """Return a fresh copy of the safety rules. Pure."""
    return list(SAFETY_RULES)


def build_sequence() -> list[dict[str, Any]]:
    """Return fresh copies of the binding build sequence. Pure."""
    return [dict(b) for b in BUILD_SEQUENCE]


def automatic_vs_human() -> dict[str, list[str]]:
    """Return a fresh copy of the automatic-vs-human split. Pure."""
    return copy.deepcopy(AUTOMATIC_VS_HUMAN)


def build_automation_roadmap() -> dict[str, Any]:
    """Assemble the full read-only automation roadmap. PURE: designs everything,
    builds nothing, starts nothing, authorizes nothing."""
    return {
        "schema_version": ROADMAP_SCHEMA_VERSION,
        "label": ROADMAP_LABEL,
        "mode": ROADMAP_MODE,
        "verdict": VERDICT_ROADMAP_READY,
        "existing_components": existing_components(),
        "missing_automation_links": missing_automation_links(),
        "automation_levels": automation_levels(),
        "safety_rules": safety_rules(),
        "build_sequence": build_sequence(),
        "automatic_vs_human": automatic_vs_human(),
        # Roadmap constitution, stated structurally:
        "execution_layer_excluded": True,
        "every_approval_remains_human": True,
        "roadmap_builds_nothing": True,
        "modifies_crypto_d1_lane": False,
        "blockers": [],
        "risk_notes": [
            "this_is_a_design_document_no_automation_exists_after_it",
            "each_link_is_its_own_future_human_approved_block",
            "the_scheduler_is_spec_first_build_later_under_its_own_approval",
            "execution_is_excluded_not_deferred",
        ],
        # Capability posture (this roadmap runs / fetches / schedules nothing):
        "executes": False,
        "writes_files": False,
        "runs_scanner": False,
        "runs_simulation": False,
        "runs_backtest": False,
        "runs_optimization": False,
        "starts_scheduler": False,
        "queues_anything": False,
        "fetches_data": False,
        "calls_api": False,
        "connects_broker": False,
        "connects_exchange": False,
        "uses_real_money": False,
        "uses_network": False,
        "uses_credentials": False,
        "contains_order_logic": False,
        "authorizes_paper_execution": False,
        "authorizes_micro_live": False,
        "authorizes_live_trading": False,
        "promotes_gate": False,
        "unlocks_downstream_gate": False,
        # Gate posture (UNTOUCHED by this roadmap):
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
        "live_gate_locked": True,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }


def validate_automation_roadmap(roadmap: Any) -> dict[str, Any]:
    """Validate (read-only) an automation roadmap's shape and safety invariants.
    Returns {"valid": bool, "errors": [...]}; never raises."""
    errors: list[str] = []
    if not isinstance(roadmap, dict):
        return {"valid": False, "errors": ["roadmap_not_a_dict"]}
    r = roadmap

    if r.get("verdict") != VERDICT_ROADMAP_READY:
        errors.append("bad_verdict")
    if r.get("schema_version") != ROADMAP_SCHEMA_VERSION:
        errors.append("bad_schema_version")

    comps = r.get("existing_components")
    if not isinstance(comps, list) or len(comps) < 8:
        errors.append("existing_components_incomplete")

    links = r.get("missing_automation_links")
    if not isinstance(links, list) or len(links) != 6:
        errors.append("missing_links_not_six")
    else:
        for l in links:
            if not (l.get("link_id") and l.get("purpose") and l.get("human_gate")):
                errors.append("link_missing_human_gate_or_fields")
                break

    levels = r.get("automation_levels")
    if not isinstance(levels, list) or len(levels) != 6:
        errors.append("levels_not_six")
        levels = []
    excluded = [l for l in levels if l.get("excluded")]
    if len(excluded) != 1 or excluded[0].get("name") != "trading_execution":
        errors.append("trading_execution_not_excluded")
    l5 = next((l for l in levels if l.get("level") == 5), None)
    if not l5 or l5.get("automated") is not False:
        errors.append("human_review_level_marked_automated")

    rules = r.get("safety_rules")
    if not isinstance(rules, list) or len(rules) != 6:
        errors.append("safety_rules_not_six")
    else:
        joined = " ".join(rules)
        for token in ("no_broker_or_exchange_credentials", "no_order_placement",
                      "no_paper_micro_live_or_live", "no_gate_unlock",
                      "no_autonomous_promotion", "require_human_review"):
            if token not in joined:
                errors.append("safety_rule_missing:" + token)

    seq = r.get("build_sequence")
    if not isinstance(seq, list) or [b.get("seq") for b in seq] != [1, 2, 3, 4, 5, 6]:
        errors.append("build_sequence_broken")

    avh = r.get("automatic_vs_human") or {}
    if not (avh.get("becomes_automatic") and avh.get("remains_human_approved")):
        errors.append("automatic_vs_human_incomplete")
    elif not any("every approval" in h for h in avh["remains_human_approved"]):
        errors.append("approvals_not_reserved_for_humans")

    # Roadmap constitution invariants.
    if r.get("execution_layer_excluded") is not True:
        errors.append("execution_not_excluded")
    if r.get("every_approval_remains_human") is not True:
        errors.append("approvals_not_human")
    if r.get("roadmap_builds_nothing") is not True:
        errors.append("roadmap_claims_to_build")
    if r.get("modifies_crypto_d1_lane") is not False:
        errors.append("crypto_d1_lane_touched")

    must_be_locked = ("paper_trading_gate_locked", "micro_live_gate_locked", "live_gate_locked")
    for key in must_be_locked:
        if r.get(key) is not True:
            errors.append("gate_not_locked:" + key)

    must_be_false = (
        "executes",
        "writes_files",
        "runs_scanner",
        "runs_simulation",
        "runs_backtest",
        "runs_optimization",
        "starts_scheduler",
        "queues_anything",
        "fetches_data",
        "calls_api",
        "connects_broker",
        "connects_exchange",
        "uses_real_money",
        "uses_network",
        "uses_credentials",
        "contains_order_logic",
        "authorizes_paper_execution",
        "authorizes_micro_live",
        "authorizes_live_trading",
        "promotes_gate",
        "unlocks_downstream_gate",
    )
    for key in must_be_false:
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)

    return {"valid": not errors, "errors": errors}


def render_automation_roadmap_markdown(roadmap: Any) -> str:
    """Render an automation roadmap as deterministic markdown. Pure string work."""
    r = roadmap if isinstance(roadmap, dict) else {}
    lines: list[str] = []
    lines.append("# SPARTA Strategy Factory Automation Roadmap (ROADMAP ONLY)")
    lines.append("")
    lines.append("- Verdict: " + str(r.get("verdict", "")))
    lines.append("- Execution layer: EXCLUDED (not deferred)")
    lines.append("- Every approval remains human: "
                 + str(r.get("every_approval_remains_human", "")))
    lines.append("- Roadmap builds nothing: " + str(r.get("roadmap_builds_nothing", "")))
    lines.append("- Next required action: " + str(r.get("next_required_action", "")))
    lines.append("")
    lines.append("## 1. Components already built")
    for c in r.get("existing_components") or []:
        lines.append("- " + str(c.get("component")) + " -- " + str(c.get("role")))
    lines.append("")
    lines.append("## 2. Missing automation links")
    for l in r.get("missing_automation_links") or []:
        lines.append("### " + str(l.get("link_id")))
        lines.append("- Purpose: " + str(l.get("purpose")))
        lines.append("- Human gate: " + str(l.get("human_gate")))
    lines.append("")
    lines.append("## 3. Automation levels")
    for l in r.get("automation_levels") or []:
        tag = "EXCLUDED" if l.get("excluded") else (
            "automated" if l.get("automated") else "human")
        lines.append("- Level " + str(l.get("level")) + " " + str(l.get("name"))
                     + " [" + tag + "]: " + str(l.get("scope")))
    lines.append("")
    lines.append("## 4. Safety rules")
    for s in r.get("safety_rules") or []:
        lines.append("- " + str(s))
    lines.append("")
    lines.append("## 5. Recommended build sequence")
    for b in r.get("build_sequence") or []:
        lines.append("- " + str(b.get("seq")) + ". " + str(b.get("block"))
                     + " -- " + str(b.get("delivers")))
    lines.append("")
    avh = r.get("automatic_vs_human") or {}
    lines.append("## Becomes automatic")
    for a in avh.get("becomes_automatic") or []:
        lines.append("- " + str(a))
    lines.append("")
    lines.append("## Remains human-approved")
    for h in avh.get("remains_human_approved") or []:
        lines.append("- " + str(h))
    lines.append("")
    lines.append("## Gates (read-only metadata, UNCHANGED)")
    lines.append("- paper_trading_gate: LOCKED")
    lines.append("- micro_live_gate: LOCKED")
    lines.append("- live_gate: LOCKED")
    return "\n".join(lines)
