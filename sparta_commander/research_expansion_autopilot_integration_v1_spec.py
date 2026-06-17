"""Research Expansion -> Safe Autopilot INTEGRATION SPEC v1 -- PURE PLANNER/SPEC.

RESEARCH ONLY. This contract is the minimal, additive, pure bridge that wires the
already-pushed Research Expansion Plan v1 (multi-idea generate / score / rank /
select-best-few) into the existing Safe Research Autopilot v1 (single-candidate
chain planner with hard stops) and the morning-report surface -- WITHOUT enabling
any execution.

It does NOTHING beyond planning: it does NOT build candidate files, NOT write
files, NOT run any detector / labels / replay / robustness / portfolio compute,
NOT fetch data, NOT read real data, NOT stage / commit / push, and NOT touch any
paper / live / broker / credential / order surface. Every capability flag is
pinned False and a full scope_locks set is attached.

WHAT IT ACTIVATES (once the human adopts the spec):
  * overnight GENERATION of multiple DECLARED candidate ideas,
  * SCORING + RANKING by REP priority weights (durability weighted ABOVE timing,
    per the C14 lesson),
  * SELECT-BEST-FEW (top_k, default 1, max 3),
  * anti-loop using the canonical 19-family rejected ledger (C1-C14),
  * portfolio-fit fields surfaced in the morning report.

WHAT STAYS LOCKED (unchanged from the existing system):
  * SARA's chain hard stops are preserved EXACTLY -- the batch selection only ever
    feeds SARA's LOW-RISK proposal gate, and ONLY when SARA itself is already
    auto-advanceable at the "open / no active candidate" stage with a clean repo.
    The batch can NEVER override a SARA stop, NEVER cross detector->labels,
    NEVER reach replay / pnl / robustness / portfolio compute / paper / live.
  * No build, no labels, no replay, no data fetch, no broker, no paper/live, no
    orders, no auto-commit, no auto-push.

THE INTEGRATION IS A SPEC: this module computes the combined plan PURELY (so it
is fully testable), and DECLARES -- but does not apply -- the two minimal wiring
changes (a morning-report section, and a proposed SARA ledger bump 18->19). Those
remain `applied: False` until separately approved.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.research_expansion_plan_v1_contract as _rep
import sparta_commander.safe_research_autopilot_v1_contract as _sara

REI_SCHEMA_VERSION = 1
REI_MODE = "RESEARCH_ONLY"

# The canonical rejected/closed ledger for the EXPANDED system = REP's 19 (C1-C14;
# it already includes conviction_bar_follow_through / C14). The integrated planner
# uses THIS for anti-loop so C14 can never be re-proposed.
CANONICAL_REJECTED_FAMILIES = tuple(_rep.REJECTED_FAMILIES_C1_TO_C14)

# The integrated batch may ONLY ever feed SARA's lowest-risk build gate.
INTEGRATION_FEEDS_ONLY = _sara.ACTION_BUILD_PROPOSAL
ALLOWED_BATCH_RECOMMENDED_TOKEN = "BUILD_NEXT_CANDIDATE_FAMILY_PROPOSAL_ONLY"

# Minimal proposed wiring changes -- DECLARED, not applied.
PROPOSED_MORNING_REPORT_CHANGE = {
    "file": "tools/sparta_autopilot_morning_report.py",
    "change": ("add a pure §14 'Overnight Research Expansion (planner-only)' "
               "block that renders plan_overnight_expansion(...) -> generated / "
               "ranked / selected-best-few + per-idea portfolio-fit fields"),
    "additive_only": True,
    "touches_execution_surface": False,
    "applied": False,
}
PROPOSED_SARA_LEDGER_CHANGE = {
    "file": "sparta_commander/safe_research_autopilot_v1_contract.py",
    "change": ("bump DEFAULT_REJECTED_FAMILIES 18 -> 19 by appending "
               "'conviction_bar_follow_through' (C14) so the single-chain planner "
               "also refuses to re-propose C14"),
    "tests_that_would_update": (
        "tests/test_safe_research_autopilot_v1_contract.py (len == 18 -> 19)",
        "tests/test_sparta_autopilot_morning_report.py "
        "(excluded_rejected_families_count == 18 -> 19)"),
    "additive_only": False,
    "touches_execution_surface": False,
    "applied": False,
    "requires_separate_token": "UPDATE_SARA_REJECTED_LEDGER_ADD_C14",
}

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "builds_candidate_files", "runs_detector",
    "runs_labels", "runs_replay", "runs_robustness", "runs_portfolio_compute",
    "fetches_data", "reads_real_data", "mutates_data", "stages_data",
    "auto_commits", "auto_pushes", "modifies_scheduler", "starts_scheduler",
    "modifies_sara", "modifies_morning_report", "modifies_rep",
    "sends_notifications", "calls_api", "uses_network", "uses_credentials",
    "connects_broker", "connects_exchange", "uses_real_money", "places_orders",
    "contains_order_logic", "paper_trading", "live_trading", "deploys_capital",
    "promotes_gate", "unlocks_downstream_gate", "skips_any_gate",
    "overrides_sara_stop", "reproposes_rejected_family",
    "advances_without_human_approval", "crosses_into_forbidden_gate",
    "claims_profitability", "claims_edge",
)


def reconcile_rejected_ledger() -> dict[str, Any]:
    """Pure reconciliation proving the canonical 19-family ledger == SARA's 18
    (C1-C13) PLUS conviction_bar_follow_through (C14). No I/O."""
    sara = list(_sara.DEFAULT_REJECTED_FAMILIES)
    canonical = list(CANONICAL_REJECTED_FAMILIES)
    extra = [f for f in canonical if f not in sara]
    return {
        "sara_count": len(sara),
        "canonical_count": len(canonical),
        "missing_from_sara": extra,
        "c14_in_canonical": "conviction_bar_follow_through" in canonical,
        "reconciles_with_c14_added":
            sorted(sara + ["conviction_bar_follow_through"]) == sorted(canonical),
    }


def plan_overnight_expansion(chain_state: dict, repo_state: dict,
                             candidate_ideas: list, build_top_k: int = 1
                             ) -> dict[str, Any]:
    """PURE. The combined overnight plan: ask SARA for the single next safe chain
    action AND ask REP for the ranked best-few over the DECLARED candidate ideas,
    using the canonical 19-family ledger for anti-loop. Builds / fetches / commits
    NOTHING.

    Integration rule (safety): the batch's selected ideas are ACTIONABLE only when
    SARA itself is already auto-advanceable at the open/no-active-candidate stage
    with a clean repo and SARA's action is exactly BUILD_NEXT_CANDIDATE_FAMILY_
    PROPOSAL. Otherwise the batch is INFORMATIONAL ONLY and the system defers to
    SARA's single action (e.g. a hard stop, a dirty-repo stop, or a mid-chain
    gate). The batch can never override a SARA stop or reach a real-data gate."""
    sara_decision = _sara.decide_next_safe_action(
        chain_state, repo_state, rejected_families=CANONICAL_REJECTED_FAMILIES)
    batch = _rep.overnight_batch_plan(
        candidate_ideas, build_top_k=build_top_k,
        rejected_families=CANONICAL_REJECTED_FAMILIES)

    sara_action = sara_decision.get("next_safe_action")
    actionable = bool(
        sara_decision.get("auto_advanceable") is True
        and sara_decision.get("is_hard_stop") is False
        and sara_action == INTEGRATION_FEEDS_ONLY
        and chain_state.get("stage") == _sara.STAGE_NONE)

    selected = batch["selected_to_build"] if actionable else []
    if actionable and selected:
        recommended_token = ALLOWED_BATCH_RECOMMENDED_TOKEN
        unified_action = INTEGRATION_FEEDS_ONLY
        reason = ("SARA is auto-advanceable at the open proposal gate with a "
                  "clean repo; the overnight batch recommends opening a proposal "
                  "for the top-ranked idea %r (human still approves each gate)"
                  % selected[0]["family"])
    else:
        recommended_token = sara_decision.get("recommended_token")
        unified_action = sara_action
        reason = ("batch is informational only; deferring to SARA's single safe "
                  "action %r (%s)" % (sara_action, sara_decision.get("decision")))

    record: dict[str, Any] = {
        "schema_version": REI_SCHEMA_VERSION, "mode": REI_MODE,
        "lane": "crypto_d1_auto_research",
        "is_pure_planner_only": True,
        "sara_decision": sara_decision,
        "sara_action": sara_action,
        "batch": batch,
        "integration_actionable": actionable,
        "batch_feeds_only": INTEGRATION_FEEDS_ONLY,
        "unified_next_safe_action": unified_action,
        "recommended_token": recommended_token,
        "selected_to_build": selected,
        "selected_families": [s["family"] for s in selected],
        "excluded_rejected_families_count": len(CANONICAL_REJECTED_FAMILIES),
        "anti_loop_ledger_is_19_c1_to_c14":
            len(CANONICAL_REJECTED_FAMILIES) == 19,
        "reason": reason,
        "requires_human_approval": True,
        "executes_nothing": True,
        "batch_can_override_sara_stop": False,
        "crosses_into_forbidden_gate": False,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = _scope_locks()
    return record


def summarize_for_morning_report(plan: dict) -> dict[str, Any]:
    """PURE morning-report-ready §14 block: generate -> rank -> select-best-few,
    WITH per-idea portfolio-fit fields. Read-only; executes nothing."""
    batch = plan.get("batch") or {}
    ranked_view = []
    for s in (batch.get("ranked") or []):
        comp = s.get("components") or {}
        ranked_view.append({
            "family": s.get("family"),
            "priority_score": s.get("priority_score"),
            "durability_proxy": comp.get("durability_proxy"),
            "timing_signal_proxy": comp.get("timing_signal_proxy"),
            "portfolio_fit": comp.get("portfolio_fit"),
        })
    return {
        "section": "overnight_research_expansion",
        "planner_only": True,
        "generated_count": batch.get("generated_count"),
        "buildable_count": batch.get("buildable_count"),
        "ranked": ranked_view,
        "selected_to_build": plan.get("selected_families"),
        "integration_actionable": plan.get("integration_actionable"),
        "unified_next_safe_action": plan.get("unified_next_safe_action"),
        "recommended_token": plan.get("recommended_token"),
        "excluded_rejected_families_count":
            plan.get("excluded_rejected_families_count"),
        "portfolio_fit_tracked_dimensions":
            list(_rep.PORTFOLIO_OBJECTIVE["tracked_dimensions"]),
        "executes_nothing": True,
    }


def _scope_locks() -> dict[str, bool]:
    return {
        "no_build": True, "no_write": True, "no_execute": True,
        "no_detector_run": True, "no_labels": True, "no_replay": True,
        "no_robustness": True, "no_portfolio_compute": True, "no_data_fetch": True,
        "no_real_data_access": True, "no_stage": True, "no_commit": True,
        "no_push": True, "no_auto_push": True, "no_auto_commit": True,
        "no_scheduler_change": True, "no_broker": True, "no_credentials": True,
        "no_order_logic": True, "no_paper_trading": True, "no_live_trading": True,
        "no_gate_skip": True, "no_sara_stop_override": True,
        "no_rejected_family_repropose": True, "no_param_only_buildable": True,
        "no_downstream_gate_unlock": True, "no_profitability_claim": True,
        "no_mutation_of_sara_or_morning_report_or_rep": True,
        "no_crossing_into_forbidden_gate": True,
    }


def get_integration_spec_label() -> str:
    return (
        "Research Expansion -> Safe Autopilot Integration Spec v1 (READ-ONLY, "
        "RESEARCH ONLY, PURE PLANNER). Wires multi-idea generate/score/rank/"
        "select-best-few into the safe autopilot's LOW-RISK proposal gate only, "
        "with anti-loop over the canonical 19-family (C1-C14) ledger and "
        "portfolio-fit fields in the morning report. Preserves EVERY SARA hard "
        "stop; the batch can NEVER override a stop or reach labels/replay/paper/"
        "live. BUILDS NOTHING, COMMITS NOTHING, PUSHES NOTHING, FETCHES NOTHING. "
        "The two wiring changes are DECLARED, not applied.")


def build_integration_spec(repo_root: Any = ".",
                           tracked_paths: list | None = None) -> dict[str, Any]:
    """Assemble the frozen integration spec record. Pure; no I/O; spec only."""
    recon = reconcile_rejected_ledger()
    record: dict[str, Any] = {
        "schema_version": REI_SCHEMA_VERSION, "mode": REI_MODE,
        "label": get_integration_spec_label(),
        "lane": "crypto_d1_auto_research",
        "is_pure_planner_only": True,
        "is_integration_spec_only": True,
        "bridges": {
            "research_expansion_plan":
                "sparta_commander.research_expansion_plan_v1_contract",
            "safe_research_autopilot":
                "sparta_commander.safe_research_autopilot_v1_contract",
            "morning_report": "tools.sparta_autopilot_morning_report",
        },
        "what_activates": [
            "overnight generation of multiple declared candidate ideas",
            "scoring + ranking (durability weighted above timing, C14 lesson)",
            "select-best-few (top_k default 1, max 3)",
            "anti-loop over the canonical 19-family (C1-C14) rejected ledger",
            "portfolio-fit fields surfaced in the morning report",
        ],
        "what_stays_locked": [
            "all SARA chain hard stops preserved exactly",
            "batch feeds ONLY the low-risk proposal gate, never labels/replay",
            "batch can never override a SARA stop",
            "no build, no labels, no replay, no data fetch",
            "no broker, no paper/live, no orders, no auto-commit, no auto-push",
        ],
        "gate_sequence_preserved_unchanged":
            list(_rep.GATE_SEQUENCE) == [
                "family_proposal", "candidate_spec", "detector_spec_dry_run",
                "real_candle_labels_review", "fee_honest_replay_review",
                "rejection_or_promote_decision"],
        "sara_hard_stops_preserved": True,
        "batch_feeds_only": INTEGRATION_FEEDS_ONLY,
        "canonical_rejected_families_count": len(CANONICAL_REJECTED_FAMILIES),
        "canonical_includes_c14":
            "conviction_bar_follow_through" in CANONICAL_REJECTED_FAMILIES,
        "rejected_ledger_reconciliation": recon,
        "proposed_changes": {
            "morning_report": dict(PROPOSED_MORNING_REPORT_CHANGE),
            "sara_ledger": dict(PROPOSED_SARA_LEDGER_CHANGE),
        },
        "proposed_changes_applied": False,
        "human_review_required": True,
        "current_loop_stage": "integration_spec",
        "next_required_action":
            "HUMAN_DECISION_ADOPT_INTEGRATION_SPEC_OR_AMEND",
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = _scope_locks()
    return record


def validate_integration_spec(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the spec is pure-planner/integration
    -only, preserves the REP gate sequence + every SARA hard stop, feeds only the
    proposal gate, carries the canonical 19-family ledger that reconciles with
    SARA+C14, keeps both wiring changes UNAPPLIED, and pins every capability flag
    False."""
    failures: list = []
    if record.get("mode") != REI_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_pure_planner_only") is not True:
        failures.append("not_pure_planner_only")
    if record.get("is_integration_spec_only") is not True:
        failures.append("not_integration_spec_only")

    if record.get("gate_sequence_preserved_unchanged") is not True:
        failures.append("gate_sequence_not_preserved")
    if record.get("sara_hard_stops_preserved") is not True:
        failures.append("sara_hard_stops_not_preserved")
    if record.get("batch_feeds_only") != INTEGRATION_FEEDS_ONLY:
        failures.append("batch_feeds_more_than_proposal_gate")

    if record.get("canonical_rejected_families_count") != 19:
        failures.append("canonical_ledger_not_19")
    if record.get("canonical_includes_c14") is not True:
        failures.append("canonical_missing_c14")
    recon = record.get("rejected_ledger_reconciliation") or {}
    if recon.get("reconciles_with_c14_added") is not True:
        failures.append("ledger_does_not_reconcile_with_c14")

    if record.get("proposed_changes_applied") is not False:
        failures.append("proposed_changes_must_not_be_applied")
    pc = record.get("proposed_changes") or {}
    for key in ("morning_report", "sara_ledger"):
        ch = pc.get(key) or {}
        if ch.get("applied") is not False:
            failures.append("proposed_change_applied_%s" % key)

    locks = record.get("scope_locks") or {}
    for key in ("no_build", "no_write", "no_execute", "no_labels", "no_replay",
                "no_data_fetch", "no_commit", "no_push", "no_auto_push",
                "no_auto_commit", "no_paper_trading", "no_live_trading",
                "no_broker", "no_gate_skip", "no_sara_stop_override",
                "no_rejected_family_repropose",
                "no_mutation_of_sara_or_morning_report_or_rep"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
