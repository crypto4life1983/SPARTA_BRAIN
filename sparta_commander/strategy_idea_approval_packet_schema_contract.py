"""SPARTA Strategy Idea Approval Packet Schema Contract (READ-ONLY, PACKET ONLY).

Roadmap link L2 (build sequence seq 2) of the Strategy Factory Automation Roadmap:
the second connecting piece in the automation chain.

    idea text
      -> intake (YES / NO / MAYBE)                       [built, link upstream]
      -> adapter (in-memory PROPOSED queue entry)        [built, link L1]
      -> THIS MODULE: a lane-aware APPROVAL PACKET       [link L2]
      -> human signature (NEVER produced here)
      -> batch approval (L3) / scheduled runs (L4)       [future, separate blocks]

What a packet is: a fully scoped, human-readable REQUEST. It enumerates exactly
ONE grant (the suggested next safe command, copied verbatim through the whole
chain), states explicitly what approval does NOT grant, embeds the lane's own
constitution constraints, and ships UNSIGNED. Generating a packet approves
nothing, runs nothing, persists nothing.

What this module can never do (validator-enforced):
  - It only packets adapter records whose verdict is INTAKE_PROPOSAL_CREATED;
    refused/invalid adapter records are refused again here -- a rejected idea can
    never reach a signature request.
  - Every packet is born UNSIGNED: signed=False, human_signature=None, and the
    validator rejects any packet that claims a signature at generation time.
  - The single grant must equal the proposal's verbatim command; a packet that
    grants anything else, or more than one thing, is invalid.
  - The does-not-grant list must always include execution, credentials,
    promotion, and gate movement.
  - In-memory only: nothing is written to disk, queue, or ledger.

Public API:
  - PACKET_SCHEMA_VERSION / PACKET_LABEL / PACKET_MODE
  - ROADMAP_LINK_ID / ROADMAP_SEQ
  - VERDICT_PACKET_GENERATED / VERDICT_PACKET_REFUSED
  - NEXT_REQUIRED_ACTION / DECISION_OPTIONS / APPROVAL_DOES_NOT_GRANT
  - LANE_CONSTRAINTS
  - get_strategy_idea_approval_packet_label()
  - generate_approval_packet(adapter_record)
  - validate_approval_packet(packet)
  - render_approval_packet_markdown(packet)
"""

from __future__ import annotations

import hashlib
from typing import Any

from sparta_commander.intake_to_orchestrator_adapter_contract import (
    VERDICT_PROPOSAL_CREATED,
    validate_adapter_record,
)
from sparta_commander.strategy_idea_intake_automation_contract import (
    KNOWN_LANES,
    LANE_ARBITRAGE,
    LANE_CRYPTO_D1,
)

PACKET_SCHEMA_VERSION = "strategy_idea_approval_packet_schema_contract.v1"
PACKET_LABEL = (
    "SPARTA Strategy Idea Approval Packet Schema (READ-ONLY, PACKET ONLY)"
)
PACKET_MODE = "RESEARCH_ONLY"

ROADMAP_LINK_ID = "L2_lane_specific_approval_packet_generator"
ROADMAP_SEQ = 2

VERDICT_PACKET_GENERATED = "STRATEGY_IDEA_PACKET_GENERATED"
VERDICT_PACKET_REFUSED = "STRATEGY_IDEA_PACKET_REFUSED"

# The roadmap's seq 3 block: one signature covering one fully enumerated chain.
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_BATCH_APPROVAL_DESIGN"

# The only decisions a human can record against a packet. No silent approval.
DECISION_OPTIONS = (
    "APPROVE_AS_SCOPED",
    "DENY",
    "REQUEST_CHANGES",
)

# What signing a packet can NEVER mean, regardless of lane or wording.
APPROVAL_DOES_NOT_GRANT = (
    "no_trading_of_any_kind_no_real_money",
    "no_paper_micro_live_or_live_runs",
    "no_credentials_and_no_authenticated_endpoints",
    "no_data_purchases_or_subscriptions",
    "no_gate_movement_and_no_promotion_of_anything",
    "no_steps_beyond_the_single_enumerated_grant",
)

# Lane constitutions embedded so the packet carries its own constraints.
LANE_CONSTRAINTS: dict[str, tuple[str, ...]] = {
    LANE_ARBITRAGE: (
        "alerts_and_reports_only_execution_is_absent_by_construction",
        "no_exchange_credentials_ever",
        "binding_roadmap_order_must_be_respected",
        "every_scanner_run_needs_its_own_per_run_human_approval",
    ),
    LANE_CRYPTO_D1: (
        "resume_policy_thread_is_closed_only_fresh_evidence_work_qualifies",
        "evaluation_only_under_the_frozen_block_190_bars",
        "consumed_oos_windows_may_never_be_re_mined",
        "do_not_promote_resume_policy_yet_remains_in_force",
    ),
}


def get_strategy_idea_approval_packet_label() -> str:
    """Human label for the recognized approval packet schema contract."""
    return PACKET_LABEL


def _packet_id(entry: dict[str, Any]) -> str:
    """Stable packet id derived from the proposal it covers. Pure."""
    seed = str(entry.get("run_id")) + "|" + str(
        entry.get("suggested_next_safe_command")
    )
    return "packet_" + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:12]


def _base_packet() -> dict[str, Any]:
    return {
        "schema_version": PACKET_SCHEMA_VERSION,
        "label": PACKET_LABEL,
        "mode": PACKET_MODE,
        "roadmap_link_id": ROADMAP_LINK_ID,
        "roadmap_seq": ROADMAP_SEQ,
        "verdict": None,
        "blockers": [],
        "packet_id": None,
        "lane": None,
        "lane_constraints": [],
        "covered_proposal": None,
        # The grant: exactly one command, verbatim from the chain.
        "approval_grants_exactly": [],
        "approval_does_not_grant": list(APPROVAL_DOES_NOT_GRANT),
        "decision_options": list(DECISION_OPTIONS),
        # Born unsigned, always.
        "signed": False,
        "human_signature": None,
        "human_decision": None,
        "packet_is_a_request_not_an_authorization": True,
        "packet_is_in_memory_only": True,
        "generated_packet_activates_nothing": True,
        "human_review_required": True,
        # Capability posture (the generator shapes a dict and nothing else):
        "executes": False,
        "writes_files": False,
        "writes_queue": False,
        "writes_ledger": False,
        "runs_research": False,
        "runs_scanner": False,
        "runs_simulation": False,
        "runs_backtest": False,
        "runs_optimization": False,
        "starts_scheduler": False,
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
        # Gate posture (UNTOUCHED by this generator):
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
        "live_gate_locked": True,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }


def generate_approval_packet(adapter_record: Any) -> dict[str, Any]:
    """Turn a CREATED adapter proposal into an UNSIGNED, lane-aware approval
    packet; refuse everything else. PURE: never raises, never signs, never
    persists, never runs anything."""
    packet = _base_packet()

    if not isinstance(adapter_record, dict):
        packet["verdict"] = VERDICT_PACKET_REFUSED
        packet["blockers"].append("adapter_record_missing_or_not_a_dict")
        return packet

    validation = validate_adapter_record(adapter_record)
    if not validation.get("valid"):
        packet["verdict"] = VERDICT_PACKET_REFUSED
        packet["blockers"].append("adapter_record_invalid")
        packet["blockers"].extend(
            "adapter_error:" + str(e) for e in validation.get("errors") or []
        )
        return packet

    if adapter_record.get("verdict") != VERDICT_PROPOSAL_CREATED:
        packet["verdict"] = VERDICT_PACKET_REFUSED
        packet["blockers"].append("no_created_proposal_to_packet")
        return packet

    lane = adapter_record.get("lane")
    if lane not in KNOWN_LANES or lane not in LANE_CONSTRAINTS:
        packet["verdict"] = VERDICT_PACKET_REFUSED
        packet["blockers"].append("lane_has_no_registered_constraints")
        return packet

    entry = adapter_record.get("proposed_queue_entry") or {}
    command = entry.get("suggested_next_safe_command")
    if not command:
        packet["verdict"] = VERDICT_PACKET_REFUSED
        packet["blockers"].append("proposal_carries_no_command")
        return packet

    packet["verdict"] = VERDICT_PACKET_GENERATED
    packet["packet_id"] = _packet_id(entry)
    packet["lane"] = lane
    packet["lane_constraints"] = list(LANE_CONSTRAINTS[lane])
    packet["covered_proposal"] = dict(entry)
    packet["approval_grants_exactly"] = [command]
    return packet


def validate_approval_packet(packet: Any) -> dict[str, Any]:
    """Validate (read-only) a packet's shape and safety invariants.
    Returns {"valid": bool, "errors": [...]}; never raises."""
    errors: list[str] = []
    if not isinstance(packet, dict):
        return {"valid": False, "errors": ["packet_not_a_dict"]}
    p = packet

    verdict = p.get("verdict")
    if verdict not in (VERDICT_PACKET_GENERATED, VERDICT_PACKET_REFUSED):
        errors.append("bad_verdict")

    if verdict == VERDICT_PACKET_REFUSED:
        if p.get("covered_proposal") is not None:
            errors.append("refused_packet_covers_a_proposal")
        if p.get("approval_grants_exactly"):
            errors.append("refused_packet_grants_something")
        if not p.get("blockers"):
            errors.append("refused_packet_without_blockers")

    if verdict == VERDICT_PACKET_GENERATED:
        if p.get("blockers"):
            errors.append("generated_packet_carries_blockers")
        if not p.get("packet_id"):
            errors.append("generated_packet_without_id")
        if p.get("lane") not in KNOWN_LANES:
            errors.append("generated_packet_without_known_lane")
        if not p.get("lane_constraints"):
            errors.append("generated_packet_without_lane_constraints")
        proposal = p.get("covered_proposal")
        grants = p.get("approval_grants_exactly")
        if not isinstance(proposal, dict):
            errors.append("generated_packet_without_proposal")
        elif not isinstance(grants, list) or len(grants) != 1:
            errors.append("grant_not_exactly_one_command")
        elif grants[0] != proposal.get("suggested_next_safe_command"):
            errors.append("grant_diverges_from_proposal_command")

    # Born unsigned -- a generator output claiming a signature is invalid.
    if p.get("signed") is not False:
        errors.append("packet_claims_to_be_signed")
    if p.get("human_signature") is not None:
        errors.append("packet_carries_a_signature")
    if p.get("human_decision") is not None:
        errors.append("packet_carries_a_decision")

    options = p.get("decision_options")
    if tuple(options or ()) != DECISION_OPTIONS:
        errors.append("decision_options_tampered")

    not_granted = " ".join(p.get("approval_does_not_grant") or [])
    for token in ("no_trading", "no_paper_micro_live_or_live",
                  "no_credentials", "no_gate_movement",
                  "no_steps_beyond_the_single_enumerated_grant"):
        if token not in not_granted:
            errors.append("does_not_grant_missing:" + token)

    if p.get("packet_is_a_request_not_an_authorization") is not True:
        errors.append("packet_claims_to_authorize")
    if p.get("packet_is_in_memory_only") is not True:
        errors.append("packet_not_in_memory_only")
    if p.get("generated_packet_activates_nothing") is not True:
        errors.append("packet_claims_to_activate")
    if p.get("human_review_required") is not True:
        errors.append("human_review_dropped")

    must_be_locked = ("paper_trading_gate_locked", "micro_live_gate_locked", "live_gate_locked")
    for key in must_be_locked:
        if p.get(key) is not True:
            errors.append("gate_not_locked:" + key)

    must_be_false = (
        "executes",
        "writes_files",
        "writes_queue",
        "writes_ledger",
        "runs_research",
        "runs_scanner",
        "runs_simulation",
        "runs_backtest",
        "runs_optimization",
        "starts_scheduler",
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
        if p.get(key) is not False:
            errors.append("capability_not_false:" + key)

    return {"valid": not errors, "errors": errors}


def render_approval_packet_markdown(packet: Any) -> str:
    """Render an approval packet as deterministic markdown. Pure string work."""
    p = packet if isinstance(packet, dict) else {}
    lines: list[str] = []
    lines.append("# SPARTA Strategy Idea Approval Packet (UNSIGNED REQUEST)")
    lines.append("")
    lines.append("- Verdict: " + str(p.get("verdict", "")))
    lines.append("- Packet id: " + str(p.get("packet_id")))
    lines.append("- Lane: " + str(p.get("lane")))
    lines.append("- Signed: " + str(p.get("signed", "")) + " (a packet is a request; "
                 "only a human signature recorded elsewhere activates anything)")
    lines.append("- Next required action: " + str(p.get("next_required_action", "")))
    lines.append("")
    blockers = p.get("blockers") or []
    if blockers:
        lines.append("## Blockers (refused; no signature request exists)")
        for b in blockers:
            lines.append("- " + str(b))
        lines.append("")
    proposal = p.get("covered_proposal")
    if isinstance(proposal, dict):
        lines.append("## Covered proposal")
        lines.append("- run_id: " + str(proposal.get("run_id")))
        lines.append("- phase: " + str(proposal.get("phase")))
        lines.append("- status: " + str(proposal.get("status")))
        lines.append("")
        lines.append("## Approving this packet grants EXACTLY")
        for g in p.get("approval_grants_exactly") or []:
            lines.append("- " + str(g))
        lines.append("")
    lines.append("## Approving this packet does NOT grant")
    for n in p.get("approval_does_not_grant") or []:
        lines.append("- " + str(n))
    lines.append("")
    constraints = p.get("lane_constraints") or []
    if constraints:
        lines.append("## Lane constraints (carried inside the packet)")
        for c in constraints:
            lines.append("- " + str(c))
        lines.append("")
    lines.append("## Decision options")
    for d in p.get("decision_options") or []:
        lines.append("- " + str(d))
    lines.append("")
    lines.append("## Gates (read-only metadata, UNCHANGED)")
    lines.append("- paper_trading_gate: LOCKED")
    lines.append("- micro_live_gate: LOCKED")
    lines.append("- live_gate: LOCKED")
    return "\n".join(lines)
