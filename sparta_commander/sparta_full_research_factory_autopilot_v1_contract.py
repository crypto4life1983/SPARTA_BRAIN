"""SPARTA Full Research Factory Autopilot v1 -- PURE ARCHITECTURE DECLARATION.

RESEARCH ONLY. This contract ENCODES the long-term machine goal as a pure, in-memory
ARCHITECTURE DECLARATION + anti-tamper validator. It does NOT execute the factory: it
builds nothing, writes nothing, runs no detector / labels / replay, fetches no data,
reads no real data, stages / commits / pushes nothing, and touches no paper / live /
broker / credential / order / capital surface. Every execution capability flag is pinned
False and a full scope_locks set is attached, so "cannot paper/live/broker/allocate" is
STRUCTURAL here (there is no execution capability in this module at all), not a runtime
guard.

THE MACHINE GOAL (what SPARTA should become):
SPARTA should become an automatic strategy-research FACTORY that can, on its own,
DISCOVER, TEST, REJECT, and RANK strategy candidates -- but it must NEVER paper trade or
live trade without an explicit human approval, and again before any tiny live trading
after paper trading has proven a candidate.

The factory pipeline (declared, ordered). Each stage is either AUTONOMOUS_RESEARCH (the
factory may run it by itself, research-only, no human gate) or HUMAN_GATED (the factory
must STOP and wait for the exact human token before that stage runs):

  1. idea_intake                      AUTONOMOUS_RESEARCH  (idea bank + rejected-ledger
                                                            lessons feed proposals)
  2. candidate_proposal_generation    AUTONOMOUS_RESEARCH
  3. deterministic_spec_generation    AUTONOMOUS_RESEARCH
  4. detector_spec_and_synthetic_dry_run  AUTONOMOUS_RESEARCH  (synthetic only, no real
                                                                data)
  5. real_data_labels                 HUMAN_GATED  (only after the research/labels gate)
  6. fee_honest_replay                 HUMAN_GATED  (only after the replay gate)
  7. formal_rejection_on_failed_evidence   AUTONOMOUS_RESEARCH  (frozen evidence fails ->
                                                                 auto rejection record)
  8. ranking_on_passed_evidence       AUTONOMOUS_RESEARCH
  9. portfolio_capital_efficiency_review   AUTONOMOUS_RESEARCH  (research review only;
                                                                 BEFORE -- never during --
                                                                 paper trading)
 10. morning_report_and_dashboard_status  AUTONOMOUS_RESEARCH
 11. next_candidate_preparation_after_rejection  AUTONOMOUS_RESEARCH

HUMAN GATES (the factory must obtain the explicit human token BEFORE any of these; it can
never cross them silently):
  * real-data labels        (per-candidate research gate)
  * fee-honest replay       (per-candidate replay gate)
  * paper trading
  * live trading
  * broker / API-key use
  * order placement
  * capital allocation
  * any optimization / tuning / edit beyond the single permitted rule

HARD LOCKS (can NEVER happen autonomously -- structural, not configurable):
  * live trading, paper trading, broker connection, API-key use, order placement,
    automatic capital allocation, hidden optimization, retuning a rejected candidate,
    rescue of C20, crossing any human gate silently.

Authoritative current state is read from the committed candidate-research lane (single
source of truth): C21 is the active candidate, C20 stays rejected, the rejected ledger is
C1-C20 (25), and C22 is NOT started (and may only be created by the factory AFTER the
current candidate is resolved, through the normal gated pipeline).
"""
from __future__ import annotations

from typing import Any

import sparta_commander.crypto_d1_candidate_research_lane_status_v1_contract as _lane

FACTORY_SCHEMA_VERSION = 1
FACTORY_MODE = "RESEARCH_ONLY"
FACTORY_NAME = "SPARTA_FULL_RESEARCH_FACTORY_AUTOPILOT_V1"
FACTORY_LANE = "crypto_d1_auto_research_factory"

# --- autonomy classes -------------------------------------------------------
AUTONOMY_RESEARCH = "AUTONOMOUS_RESEARCH"   # factory may run by itself (research-only)
AUTONOMY_HUMAN_GATED = "HUMAN_GATED"        # factory must STOP for the human token

# --- the ordered factory pipeline (the COMPLETE declared stage list) --------
# autonomy = whether the factory may run this stage without a human gate.
# human_gate = the exact human token required first (None for autonomous stages).
PIPELINE_STAGES: tuple[dict[str, Any], ...] = (
    {"id": "idea_intake", "autonomy": AUTONOMY_RESEARCH, "human_gate": None,
     "summary": "auto-intake ideas from the idea bank + rejected-ledger lessons"},
    {"id": "candidate_proposal_generation", "autonomy": AUTONOMY_RESEARCH,
     "human_gate": None, "summary": "auto-generate the next candidate family proposal"},
    {"id": "deterministic_spec_generation", "autonomy": AUTONOMY_RESEARCH,
     "human_gate": None, "summary": "auto-generate the deterministic candidate spec"},
    {"id": "detector_spec_and_synthetic_dry_run", "autonomy": AUTONOMY_RESEARCH,
     "human_gate": None,
     "summary": "auto-generate detector spec + synthetic dry-run (no real data)"},
    {"id": "real_data_labels", "autonomy": AUTONOMY_HUMAN_GATED,
     "human_gate": "HUMAN_DECISION_ADVANCE_TO_REAL_CANDLE_LABELS_OR_REJECT",
     "summary": "real-data labels -- ONLY after the human research/labels gate"},
    {"id": "fee_honest_replay", "autonomy": AUTONOMY_HUMAN_GATED,
     "human_gate": "HUMAN_DECISION_ADVANCE_TO_FEE_HONEST_REPLAY_OR_REJECT",
     "summary": "fee-honest replay -- ONLY after the human replay gate"},
    {"id": "formal_rejection_on_failed_evidence", "autonomy": AUTONOMY_RESEARCH,
     "human_gate": None,
     "summary": "auto formal rejection record when frozen evidence fails"},
    {"id": "ranking_on_passed_evidence", "autonomy": AUTONOMY_RESEARCH,
     "human_gate": None, "summary": "auto-rank candidates when frozen evidence passes"},
    {"id": "portfolio_capital_efficiency_review", "autonomy": AUTONOMY_RESEARCH,
     "human_gate": None,
     "summary": "auto research review of portfolio/capital efficiency BEFORE paper "
                "trading (review only -- never trades)"},
    {"id": "morning_report_and_dashboard_status", "autonomy": AUTONOMY_RESEARCH,
     "human_gate": None, "summary": "auto morning report + dashboard status surface"},
    {"id": "next_candidate_preparation_after_rejection", "autonomy": AUTONOMY_RESEARCH,
     "human_gate": None,
     "summary": "auto-prepare the next candidate after a rejection closeout"},
)

# the research capabilities the factory MAY perform autonomously (discover/test/
# reject/rank) -- the affirmative "the factory can do research by itself" set.
AUTONOMOUS_RESEARCH_STAGE_IDS = tuple(
    s["id"] for s in PIPELINE_STAGES if s["autonomy"] == AUTONOMY_RESEARCH)
HUMAN_GATED_STAGE_IDS = tuple(
    s["id"] for s in PIPELINE_STAGES if s["autonomy"] == AUTONOMY_HUMAN_GATED)

# --- human gates required BEFORE these actions (never crossed silently) ------
HUMAN_GATES_BEFORE: tuple[str, ...] = (
    "real_data_labels",
    "fee_honest_replay",
    "paper_trading",
    "live_trading",
    "broker_or_api_key_use",
    "order_placement",
    "capital_allocation",
    "any_optimization_tuning_or_edit_beyond_permitted_rule",
)

# --- hard locks: can NEVER happen autonomously (structural) ------------------
HARD_LOCKS: tuple[str, ...] = (
    "no_live_trading",
    "no_paper_trading",
    "no_broker_connection",
    "no_api_key_use",
    "no_order_placement",
    "no_automatic_capital_allocation",
    "no_hidden_optimization",
    "no_retuning_rejected_candidates",
    "no_rescue_of_c20",
    "no_crossing_human_gates_silently",
)

# every execution capability this architecture declaration must pin False (the
# module itself executes nothing; the factory may NEVER do these autonomously).
_CAPABILITY_FLAGS_FALSE = (
    "executes", "builds_files", "writes_files", "runs_detector", "runs_labels",
    "runs_real_candle_detection", "runs_replay", "computes_pnl", "fetches_data",
    "reads_real_data", "mutates_data", "stages_data", "auto_commits", "auto_pushes",
    "modifies_scheduler", "starts_scheduler", "sends_notifications", "calls_api",
    "uses_network", "uses_credentials", "uses_api_keys", "connects_broker",
    "connects_exchange", "places_orders", "contains_order_logic", "uses_real_money",
    "paper_trades", "live_trades", "allocates_capital", "auto_allocates_capital",
    "hidden_optimization", "retunes_rejected_candidate", "rescues_c20",
    "crosses_human_gate_silently", "advances_without_human_approval",
    "unlocks_downstream_gate", "promotes_to_paper_without_human",
    "promotes_to_live_without_human", "claims_profitability", "claims_edge",
)


def _scope_locks() -> dict[str, bool]:
    return {
        "no_execute": True, "no_build": True, "no_write": True,
        "no_detector_run": True, "no_labels": True, "no_replay": True,
        "no_pnl": True, "no_data_fetch": True, "no_real_data_access": True,
        "no_stage": True, "no_commit": True, "no_push": True,
        "no_scheduler_change": True, "no_broker": True, "no_api_keys": True,
        "no_credentials": True, "no_order_logic": True, "no_order_placement": True,
        "no_paper_trading": True, "no_live_trading": True,
        "no_capital_allocation": True, "no_auto_capital_allocation": True,
        "no_hidden_optimization": True, "no_retune_rejected": True,
        "no_rescue_c20": True, "no_silent_gate_cross": True,
        "no_downstream_gate_unlock": True, "no_profitability_claim": True,
        "no_promote_to_paper_without_human": True,
        "no_promote_to_live_without_human": True,
    }


def factory_can_autonomously(stage_id: str) -> bool:
    """PURE. True only when `stage_id` is a declared AUTONOMOUS_RESEARCH stage the
    factory may run by itself. Real-data labels / fee-honest replay / anything trading
    are NOT autonomous -> False. Unknown stage -> False."""
    for s in PIPELINE_STAGES:
        if s["id"] == stage_id:
            return s["autonomy"] == AUTONOMY_RESEARCH
    return False


def human_gate_required_before(action: str) -> bool:
    """PURE. True when `action` requires an explicit human gate before the factory may
    perform it (paper/live/broker/order/capital/labels/replay/optimization)."""
    return action in HUMAN_GATES_BEFORE


def build_factory_architecture() -> dict[str, Any]:
    """Assemble the read-only factory architecture record. Pure; no I/O. Reads the
    committed candidate-research lane for the authoritative current state. Declares the
    machine goal; executes nothing."""
    lane = _lane.get_lane_status()
    active = lane.get("active_candidate")
    detail = lane.get("active_candidate_detail") or {}
    rejected = lane.get("last_rejected_candidate")
    rej_detail = lane.get("last_rejected_candidate_detail") or {}
    prior_detail = lane.get("prior_rejected_candidate_detail") or {}
    ledger_count = lane.get("rejected_ledger_count")

    record: dict[str, Any] = {
        "schema_version": FACTORY_SCHEMA_VERSION, "mode": FACTORY_MODE,
        "factory_name": FACTORY_NAME, "lane": FACTORY_LANE,
        "is_pure_architecture_declaration_only": True,
        "label": (
            "SPARTA Full Research Factory Autopilot v1 (READ-ONLY, RESEARCH ONLY). "
            "Encodes the machine goal: auto-discover / test / reject / rank strategy "
            "candidates by itself, but NEVER paper trade or live trade without explicit "
            "human approval (and again before any tiny live trade after paper proves a "
            "candidate). Declares the pipeline + human gates + hard locks. Executes "
            "nothing."),
        "machine_goal": (
            "SPARTA becomes an automatic strategy-research factory that discovers, "
            "tests, rejects, and ranks candidates autonomously; human approval is "
            "required only to enter paper trading, and again before tiny live trading "
            "once paper trading proves the candidate."),
        # --- the declared pipeline ---------------------------------------------
        "pipeline_stages": [dict(s) for s in PIPELINE_STAGES],
        "autonomous_research_stage_ids": list(AUTONOMOUS_RESEARCH_STAGE_IDS),
        "human_gated_stage_ids": list(HUMAN_GATED_STAGE_IDS),
        # affirmative research autonomy: discover / test / reject / rank by itself
        "can_discover_candidates": True,
        "can_propose_candidates": True,
        "can_generate_specs": True,
        "can_generate_detector_and_dry_run": True,
        "can_reject_on_failed_evidence": True,
        "can_rank_on_passed_evidence": True,
        "can_review_portfolio_before_paper": True,
        "can_prepare_next_candidate_after_rejection": True,
        # real-data labels + replay are research, but only AFTER the human gate
        "real_data_labels_requires_human_gate": True,
        "fee_honest_replay_requires_human_gate": True,
        # --- human gates + hard locks ------------------------------------------
        "human_gates_before": list(HUMAN_GATES_BEFORE),
        "requires_human_before_paper_trading": True,
        "requires_human_before_live_trading": True,
        "requires_human_before_broker_or_api_keys": True,
        "requires_human_before_order_placement": True,
        "requires_human_before_capital_allocation": True,
        "requires_human_before_optimization": True,
        "hard_locks": list(HARD_LOCKS),
        # --- rejected-ledger lessons are respected -----------------------------
        "respects_rejected_ledger": True,
        "rejected_ledger_count": ledger_count,
        "rejected_ledger_is_c1_to_c21": ledger_count == 26,
        "never_reproposes_rejected_family": True,
        "never_retunes_rejected_candidate": True,
        # --- authoritative current state (from the lane) -----------------------
        # C21 is now REJECTED at fee-honest replay (kept on record, last rejected); there
        # is NO active candidate. The next candidate (C22) is proposal-readiness only and
        # NOT started -- it may only be created after this resolution, human-gated.
        "active_candidate": active,                            # None
        "active_candidate_is_none_authoritative": active is None,
        "last_rejected_candidate": rejected,                  # C21
        "c21_remains_rejected": (
            rejected == "C21"
            and rej_detail.get("verdict") == "C21_REJECTED_AT_FEE_HONEST_REPLAY"),
        "c20_remains_rejected": (
            prior_detail.get("verdict") == "C20_REJECTED_AT_FEE_HONEST_REPLAY"),
        "c22_started": False,
        "c22_candidate_id": None,
        "c22_is_next_proposal_readiness_only": (
            (lane.get("next_candidate_readiness") or {}).get("candidate") == "C22"),
        "c22_only_created_after_current_candidate_resolved": True,
        # --- posture -----------------------------------------------------------
        "requires_human_approval": True,
        "executes_nothing": True,
        "human_review_required": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = _scope_locks()
    return record


def summarize_for_morning_report() -> dict[str, Any]:
    """Pure morning-report-ready summary of the factory architecture: what it may do
    autonomously and where it must stop for a human. Read-only."""
    r = build_factory_architecture()
    return {
        "section": "sparta_full_research_factory_autopilot_v1",
        "factory_name": FACTORY_NAME,
        "machine_goal": r["machine_goal"],
        "autonomous_research_stages": r["autonomous_research_stage_ids"],
        "human_gated_stages": r["human_gated_stage_ids"],
        "human_gates_before": r["human_gates_before"],
        "hard_locks": r["hard_locks"],
        "active_candidate": r["active_candidate"],
        "active_candidate_is_none_authoritative": r["active_candidate_is_none_authoritative"],
        "last_rejected_candidate": r["last_rejected_candidate"],
        "c21_remains_rejected": r["c21_remains_rejected"],
        "c20_remains_rejected": r["c20_remains_rejected"],
        "c22_started": r["c22_started"],
        "requires_human_before_paper_trading": True,
        "requires_human_before_live_trading": True,
        "executes_nothing": True,
    }


def validate_factory_architecture(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the record is a research-only, pure
    architecture declaration that: keeps discover/propose/spec/dry-run/reject/rank
    AUTONOMOUS; keeps real-data labels + fee-honest replay + paper + live + broker +
    order + capital + optimization HUMAN-GATED; carries the full hard-lock set; respects
    the rejected ledger (C1-C20 / 25) and never retunes a rejected candidate; keeps C21
    authoritative, C20 rejected, and C22 not started; and pins every execution
    capability flag False with the full scope_locks True."""
    failures: list = []
    if record.get("mode") != FACTORY_MODE:
        failures.append("mode_not_research_only")
    if record.get("factory_name") != FACTORY_NAME:
        failures.append("factory_name_mismatch")
    if record.get("is_pure_architecture_declaration_only") is not True:
        failures.append("not_pure_architecture_declaration")

    # the affirmative research autonomy must hold (discover / test / reject / rank)
    for cap in ("can_discover_candidates", "can_propose_candidates",
                "can_generate_specs", "can_generate_detector_and_dry_run",
                "can_reject_on_failed_evidence", "can_rank_on_passed_evidence"):
        if record.get(cap) is not True:
            failures.append("research_autonomy_missing_%s" % cap)

    # the gated stages must stay gated (labels + replay never autonomous)
    for sid in ("real_data_labels", "fee_honest_replay"):
        if sid not in (record.get("human_gated_stage_ids") or []):
            failures.append("gated_stage_not_gated_%s" % sid)
        if sid in (record.get("autonomous_research_stage_ids") or []):
            failures.append("gated_stage_marked_autonomous_%s" % sid)
    if record.get("real_data_labels_requires_human_gate") is not True:
        failures.append("labels_not_human_gated")
    if record.get("fee_honest_replay_requires_human_gate") is not True:
        failures.append("replay_not_human_gated")

    # trading / broker / capital must NOT be autonomous research stages
    for forbidden in ("paper_trading", "live_trading", "broker", "order",
                      "capital_allocation"):
        for sid in (record.get("autonomous_research_stage_ids") or []):
            if forbidden in sid:
                failures.append("trading_stage_marked_autonomous_%s" % forbidden)

    # every human gate must be declared before paper / live / broker / order / capital
    for must in ("paper_trading", "live_trading", "broker_or_api_key_use",
                 "order_placement", "capital_allocation"):
        if must not in (record.get("human_gates_before") or []):
            failures.append("human_gate_missing_%s" % must)
    for flag in ("requires_human_before_paper_trading",
                 "requires_human_before_live_trading",
                 "requires_human_before_broker_or_api_keys",
                 "requires_human_before_order_placement",
                 "requires_human_before_capital_allocation",
                 "requires_human_before_optimization"):
        if record.get(flag) is not True:
            failures.append("human_requirement_false_%s" % flag)

    # hard locks must all be present
    for lock in HARD_LOCKS:
        if lock not in (record.get("hard_locks") or []):
            failures.append("hard_lock_missing_%s" % lock)

    # rejected-ledger lessons respected
    if record.get("respects_rejected_ledger") is not True:
        failures.append("does_not_respect_rejected_ledger")
    if record.get("rejected_ledger_count") != 26:
        failures.append("rejected_ledger_count_not_26")
    if record.get("never_retunes_rejected_candidate") is not True:
        failures.append("retunes_rejected_candidate")

    # authoritative state: NO active candidate (C21 rejected); C21+C20 rejected; C22 not
    # started (it is the next proposal-readiness candidate only).
    if record.get("active_candidate") is not None:
        failures.append("active_candidate_must_be_none")
    if record.get("active_candidate_is_none_authoritative") is not True:
        failures.append("active_none_not_authoritative")
    if record.get("c21_remains_rejected") is not True:
        failures.append("c21_not_rejected")
    if record.get("c20_remains_rejected") is not True:
        failures.append("c20_not_rejected")
    if record.get("c22_started") is not False:
        failures.append("c22_started_true")
    if record.get("c22_candidate_id") is not None:
        failures.append("c22_candidate_id_set")

    # scope locks + capability flags
    locks = record.get("scope_locks") or {}
    for key in ("no_execute", "no_build", "no_labels", "no_replay", "no_data_fetch",
                "no_commit", "no_push", "no_broker", "no_api_keys", "no_order_logic",
                "no_paper_trading", "no_live_trading", "no_capital_allocation",
                "no_auto_capital_allocation", "no_hidden_optimization",
                "no_retune_rejected", "no_rescue_c20", "no_silent_gate_cross",
                "no_promote_to_paper_without_human",
                "no_promote_to_live_without_human"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
