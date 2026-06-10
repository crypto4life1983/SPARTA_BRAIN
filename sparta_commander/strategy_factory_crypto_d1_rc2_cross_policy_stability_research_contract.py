"""Crypto-D1 V2 RC2 Cross-Policy Stability Research Contract (READ-ONLY, PLAN ONLY).

A PURE, stdlib-only, read-only module that SPECIFIES (but never runs) the RC2 research
direction the human selected in the Block 183 evidence decision: compare the FIXED
resume-policy candidate set (RP1..RP6, parameters strictly UNCHANGED, read verbatim from
the Block 175 research plan) over the SAME four FIXED out-of-sample windows RC1 used
(read verbatim from the Block 180 spec), to answer ONE question:

    Is the RC1 evidence leader still the strongest policy compared with the other fixed
    candidates across the same out-of-sample windows?

It consumes the Block 183 human evidence decision (which chains read-only through Blocks
182/181 to the persisted RC1 replay report), re-validates it with Block 183's own
validator, confirms the human selected the RC2 direction, and emits a FIXED comparison
plan: one planned replay per candidate policy, each covering every RC2 window, each NOT
RUN here (``is_run=False``) and each gated on a SEPARATE explicit human command. Ranking
is fixed in advance (mean return / worst drawdown / mean Sharpe across windows) -- a
pre-registered comparison, never a search: no fitting, no tuning, no parameter change,
and no selection-by-results inside this contract.

The contract strictly PRESERVES ``DO_NOT_PROMOTE_RESUME_POLICY_YET``. It RUNS NOTHING and
WRITES NOTHING: no data fetch, no replay, no simulation, no backtest, no optimization, no
parameter search, no broker/exchange, no network, no credentials, no real order, no file
write. It UNLOCKS no gate: paper_trading_gate, micro_live_gate and the live gate all stay
LOCKED.

Public API:
  - RC2_SCHEMA_VERSION / RC2_LABEL / RC2_MODE / SELECTED_DIRECTION_ID
  - VERDICT_RC2_SPEC_READY / VERDICT_RC2_SPEC_BLOCKED
  - HUMAN_DECISION_PRESERVED / NEXT_REQUIRED_ACTION / SELECTED_VARIANT_ID
  - RC2_STABILITY_QUESTION / RANKING_CATEGORIES
  - get_rc2_cross_policy_stability_contract_label()
  - candidate_policies() / evaluation_windows() / planned_cross_policy_replays()
  - record_rc2_cross_policy_stability_spec(human_evidence_decision)
  - build_rc2_cross_policy_stability_spec(repo_root)
  - validate_rc2_cross_policy_stability_spec(spec)
  - render_rc2_cross_policy_stability_spec_markdown(spec)
"""

from __future__ import annotations

import copy
from typing import Any

from sparta_commander.strategy_factory_crypto_d1_paper_trading_prep_contract import (
    SELECTED_VARIANT_ID,
)
from sparta_commander.strategy_factory_crypto_d1_resume_policy_research_plan import (
    resume_policy_candidates,
)
from sparta_commander.strategy_factory_crypto_d1_rc1_out_of_sample_robustness_research_contract import (
    WINDOW_TYPE_HELD_OUT,
    out_of_sample_windows,
)
from sparta_commander.strategy_factory_crypto_d1_rc1_oos_human_evidence_decision_contract import (
    DECISION_DO_NOT_PROMOTE,
    DIRECTION_RC2_CROSS_POLICY_STABILITY,
    VERDICT_DECISION_RECORDED,
    build_rc1_oos_human_evidence_decision,
    validate_rc1_oos_human_evidence_decision,
)

RC2_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_rc2_cross_policy_stability_research_contract.v1"
)
RC2_LABEL = (
    "Crypto-D1 V2 RC2 Cross-Policy Stability Research Contract (READ-ONLY, PLAN ONLY)"
)
RC2_MODE = "RESEARCH_ONLY"

# The Block 183 research direction this contract realizes; the human selected it.
SELECTED_DIRECTION_ID = DIRECTION_RC2_CROSS_POLICY_STABILITY

VERDICT_RC2_SPEC_READY = "RC2_CROSS_POLICY_STABILITY_SPEC_READY"
VERDICT_RC2_SPEC_BLOCKED = "RC2_CROSS_POLICY_STABILITY_SPEC_BLOCKED"

# The human decision this spec must carry forward UNCHANGED; no promote branch exists.
HUMAN_DECISION_PRESERVED = DECISION_DO_NOT_PROMOTE

# After this spec is recorded, the only next step is a SEPARATE explicit human command to
# actually run the planned cross-policy replays. Nothing here authorizes execution.
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_RC2_CROSS_POLICY_REPLAY"

RC2_STABILITY_QUESTION = (
    "Is the RC1 evidence leader still the strongest policy compared with the other "
    "fixed candidates (RP1..RP5) across the SAME fixed out-of-sample windows?"
)

# Pre-registered ranking categories, fixed BEFORE any run. Reporting categories only --
# never an objective to optimize against.
RANKING_CATEGORIES: tuple[str, ...] = (
    "mean_total_return",
    "worst_max_drawdown",
    "mean_sharpe_ratio",
)


def get_rc2_cross_policy_stability_contract_label() -> str:
    """Human label for the recognized Crypto-D1 RC2 cross-policy stability contract."""
    return RC2_LABEL


def candidate_policies() -> list[dict[str, Any]]:
    """Return fresh deep copies of the FIXED resume-policy candidates, verbatim from the
    Block 175 research plan. Pure; parameters are never modified here."""
    return [copy.deepcopy(p) for p in resume_policy_candidates()]


def evaluation_windows() -> list[dict[str, Any]]:
    """Return fresh copies of the SAME fixed out-of-sample windows RC1 used, verbatim
    from the Block 180 spec. Pure."""
    return out_of_sample_windows()


def planned_cross_policy_replays() -> list[dict[str, Any]]:
    """Build the FIXED future comparison plan: one planned replay per candidate policy,
    each covering every RC2 window, parameters UNCHANGED, each NOT YET RUN and each gated
    on a separate explicit human command. Pure; runs nothing."""
    window_ids = [w["window_id"] for w in out_of_sample_windows()]
    plan: list[dict[str, Any]] = []
    for p in resume_policy_candidates():
        plan.append({
            "replay_id": "RC2_REPLAY_" + p["policy_id"],
            "policy_id": p["policy_id"],
            "selected_variant_id": SELECTED_VARIANT_ID,
            "policy_parameters_changed": False,
            "data_scope": "QA_PASSED_LOCAL_CSV_ONLY",
            "windows_to_cover": list(window_ids),
            "metrics_to_collect": [
                "total_return", "max_drawdown", "sharpe_ratio",
                "time_in_market", "num_resume_events", "post_resume_drawdown",
            ],
            "is_run": False,
            "requires_human_command": True,
            "authorization_required": NEXT_REQUIRED_ACTION,
        })
    return plan


def record_rc2_cross_policy_stability_spec(
    human_evidence_decision: Any,
) -> dict[str, Any]:
    """Record the RC2 cross-policy stability spec over the Block 183 human evidence
    decision. PURE: takes the decision dict (or None), returns a spec dict. Never raises.
    The carried human decision is ALWAYS DO_NOT_PROMOTE; this contract has no promote
    branch, changes no parameter, and unlocks nothing."""
    blockers: list[str] = []
    risk_notes: list[str] = []

    if not isinstance(human_evidence_decision, dict):
        blockers.append("human_evidence_decision_missing")
        return _spec(VERDICT_RC2_SPEC_BLOCKED, blockers, risk_notes,
                     rc1_leader_policy_id=None, report_found=False)

    hed = human_evidence_decision

    decision_validation = validate_rc1_oos_human_evidence_decision(hed)
    if not decision_validation.get("valid"):
        blockers.append("human_evidence_decision_invalid")
        blockers.extend("decision:" + e for e in decision_validation.get("errors", []))

    if hed.get("verdict") != VERDICT_DECISION_RECORDED:
        blockers.append("human_evidence_decision_not_recorded")

    if hed.get("human_decision") != HUMAN_DECISION_PRESERVED:
        blockers.append("human_decision_not_do_not_promote")

    if hed.get("selected_research_direction") != SELECTED_DIRECTION_ID:
        blockers.append("rc2_direction_not_selected_by_human")

    rc1_leader = hed.get("policy_id")
    if rc1_leader:
        risk_notes.append("rc1_evidence_leader_to_test:" + str(rc1_leader))
        risk_notes.append("leader_status_is_the_question_not_the_assumption")
    else:
        blockers.append("no_rc1_leader_policy_to_compare_against")

    risk_notes.append("candidate_parameters_verbatim_from_block_175_no_fitting")
    risk_notes.append("windows_verbatim_from_block_180_same_as_rc1")
    risk_notes.append("ranking_categories_fixed_before_any_run")
    risk_notes.append("running_any_replay_requires_separate_human_command")
    risk_notes.append("promotion_requires_separate_explicit_human_command")

    ready = (
        not blockers
        and hed.get("verdict") == VERDICT_DECISION_RECORDED
        and hed.get("selected_research_direction") == SELECTED_DIRECTION_ID
    )
    verdict = VERDICT_RC2_SPEC_READY if ready else VERDICT_RC2_SPEC_BLOCKED
    return _spec(verdict, blockers, risk_notes,
                 rc1_leader_policy_id=rc1_leader,
                 report_found=bool(hed.get("rc1_oos_replay_report_found")))


def _spec(
    verdict: str,
    blockers: list[str],
    risk_notes: list[str],
    *,
    rc1_leader_policy_id: Any,
    report_found: bool,
) -> dict[str, Any]:
    """Assemble an RC2 spec dict carrying the read-only safety posture. This contract
    authorizes nothing: paper / micro-live / live stay LOCKED unconditionally and the
    carried human decision is always DO_NOT_PROMOTE."""
    policies = candidate_policies()
    return {
        "schema_version": RC2_SCHEMA_VERSION,
        "label": RC2_LABEL,
        "mode": RC2_MODE,
        "verdict": verdict,
        "selected_direction_id": SELECTED_DIRECTION_ID,
        "selected_variant_id": SELECTED_VARIANT_ID,
        "human_decision": HUMAN_DECISION_PRESERVED,
        "approved_for_execution": False,
        "human_review_required": True,
        "rc1_leader_policy_id": rc1_leader_policy_id,
        "rc2_stability_question": RC2_STABILITY_QUESTION,
        "ranking_categories": list(RANKING_CATEGORIES),
        "candidate_policy_ids": [p["policy_id"] for p in policies],
        "candidate_policies": policies,
        "candidate_parameters_changed": False,
        "evaluation_windows": evaluation_windows(),
        "planned_replays": planned_cross_policy_replays(),
        "blockers": list(blockers),
        "risk_notes": list(risk_notes),
        "rc1_oos_replay_report_found": report_found,
        # Capability posture (this is a SPEC; it executes / runs / authorizes nothing):
        "executes": False,
        "writes_files": False,
        "runs_replay": False,
        "runs_simulation": False,
        "runs_backtest": False,
        "runs_optimization": False,
        "ran_parameter_search": False,
        "parameters_changed_based_on_results": False,
        "fetches_data": False,
        "connects_broker": False,
        "connects_exchange": False,
        "uses_real_money": False,
        "uses_network": False,
        "uses_credentials": False,
        "authorizes_paper_execution": False,
        "authorizes_micro_live": False,
        "authorizes_live_trading": False,
        "promotes_gate": False,
        "promotes_resume_policy": False,
        "unlocks_downstream_gate": False,
        # Gate posture (UNCHANGED by this spec):
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
        "live_gate_locked": True,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }


def build_rc2_cross_policy_stability_spec(repo_root: str = ".") -> dict[str, Any]:
    """Load the Block 183 human evidence decision (read-only via Blocks 182/181) and
    record the RC2 spec over it. Reads nothing itself beyond what the upstream chain
    reads; writes nothing; runs no replay; unlocks no gate."""
    decision = build_rc1_oos_human_evidence_decision(repo_root)
    spec = record_rc2_cross_policy_stability_spec(decision)
    spec["human_evidence_decision_verdict"] = decision.get("verdict")
    return spec


def validate_rc2_cross_policy_stability_spec(spec: Any) -> dict[str, Any]:
    """Validate (read-only) an RC2 spec's shape and safety invariants. Returns
    {"valid": bool, "errors": [...]}; never raises."""
    errors: list[str] = []
    if not isinstance(spec, dict):
        return {"valid": False, "errors": ["spec_not_a_dict"]}
    s = spec

    if s.get("verdict") not in (VERDICT_RC2_SPEC_READY, VERDICT_RC2_SPEC_BLOCKED):
        errors.append("bad_verdict")
    if s.get("schema_version") != RC2_SCHEMA_VERSION:
        errors.append("bad_schema_version")
    if s.get("selected_variant_id") != SELECTED_VARIANT_ID:
        errors.append("bad_selected_variant")
    if s.get("selected_direction_id") != SELECTED_DIRECTION_ID:
        errors.append("bad_selected_direction")

    if s.get("human_decision") != HUMAN_DECISION_PRESERVED:
        errors.append("human_decision_not_do_not_promote")
    if s.get("approved_for_execution") is not False:
        errors.append("spec_marked_approved")
    if s.get("human_review_required") is not True:
        errors.append("spec_not_flagging_human_review")
    if s.get("candidate_parameters_changed") is not False:
        errors.append("candidate_parameters_changed")

    policies = s.get("candidate_policies")
    if not isinstance(policies, list) or not policies:
        errors.append("no_candidate_policies")
        policies = []
    policy_ids: set[str] = set()
    for p in policies:
        if not isinstance(p, dict):
            errors.append("policy_not_a_dict")
            continue
        pid = p.get("policy_id")
        if pid in policy_ids:
            errors.append("duplicate_policy_id:" + str(pid))
        if isinstance(pid, str):
            policy_ids.add(pid)
    # A cross-policy comparison needs more than one candidate.
    if policies and len(policy_ids) < 2:
        errors.append("fewer_than_two_candidates")

    windows = s.get("evaluation_windows")
    if not isinstance(windows, list) or not windows:
        errors.append("no_evaluation_windows")
        windows = []
    held_out_count = sum(
        1 for w in windows
        if isinstance(w, dict) and w.get("window_type") == WINDOW_TYPE_HELD_OUT
    )
    if windows and held_out_count == 0:
        errors.append("no_truly_held_out_window")

    replays = s.get("planned_replays")
    if not isinstance(replays, list) or not replays:
        errors.append("no_planned_replays")
        replays = []
    referenced: set[str] = set()
    for r in replays:
        if not isinstance(r, dict):
            errors.append("replay_not_a_dict")
            continue
        # No replay may be marked as already run -- this is a spec, nothing has executed.
        if r.get("is_run") is not False:
            errors.append("replay_marked_run:" + str(r.get("replay_id")))
        if r.get("requires_human_command") is not True:
            errors.append("replay_not_human_gated:" + str(r.get("replay_id")))
        if r.get("policy_parameters_changed") is not False:
            errors.append("replay_changes_parameters:" + str(r.get("replay_id")))
        if r.get("data_scope") != "QA_PASSED_LOCAL_CSV_ONLY":
            errors.append("replay_bad_data_scope:" + str(r.get("replay_id")))
        rpid = r.get("policy_id")
        if rpid not in policy_ids:
            errors.append("replay_references_unknown_policy:" + str(rpid))
        if isinstance(rpid, str):
            referenced.add(rpid)
    missing = policy_ids - referenced
    if missing:
        errors.append("policies_without_replay:" + ",".join(sorted(missing)))

    if s.get("verdict") == VERDICT_RC2_SPEC_READY and (s.get("blockers") or []):
        errors.append("ready_with_blockers")
    if s.get("verdict") == VERDICT_RC2_SPEC_BLOCKED and not (s.get("blockers") or []):
        errors.append("blocked_without_blockers")

    must_be_locked = ("paper_trading_gate_locked", "micro_live_gate_locked", "live_gate_locked")
    for key in must_be_locked:
        if s.get(key) is not True:
            errors.append("gate_not_locked:" + key)

    must_be_false = (
        "executes",
        "writes_files",
        "runs_replay",
        "runs_simulation",
        "runs_backtest",
        "runs_optimization",
        "ran_parameter_search",
        "parameters_changed_based_on_results",
        "fetches_data",
        "connects_broker",
        "connects_exchange",
        "uses_real_money",
        "uses_network",
        "uses_credentials",
        "authorizes_paper_execution",
        "authorizes_micro_live",
        "authorizes_live_trading",
        "promotes_gate",
        "promotes_resume_policy",
        "unlocks_downstream_gate",
    )
    for key in must_be_false:
        if s.get(key) is not False:
            errors.append("capability_not_false:" + key)

    return {"valid": not errors, "errors": errors}


def render_rc2_cross_policy_stability_spec_markdown(spec: Any) -> str:
    """Render an RC2 spec as deterministic markdown. Pure string work."""
    s = spec if isinstance(spec, dict) else {}
    lines: list[str] = []
    lines.append("# Crypto-D1 V2 RC2 Cross-Policy Stability Research Spec (PLAN ONLY)")
    lines.append("")
    lines.append("- Verdict: " + str(s.get("verdict", "")))
    lines.append("- Selected direction: " + str(s.get("selected_direction_id", "")))
    lines.append("- Selected variant: " + str(s.get("selected_variant_id", "")))
    lines.append("- Human decision (preserved): " + str(s.get("human_decision", "")))
    lines.append("- Approved for execution: " + str(s.get("approved_for_execution", "")))
    lines.append("- RC1 evidence leader to test: " + str(s.get("rc1_leader_policy_id", "")))
    lines.append("- Next required action: " + str(s.get("next_required_action", "")))
    lines.append("")
    lines.append("## Stability question")
    lines.append(str(s.get("rc2_stability_question", "")))
    lines.append("")
    lines.append("## Ranking categories (fixed before any run)")
    for c in s.get("ranking_categories") or []:
        lines.append("- " + str(c))
    lines.append("")
    lines.append("## Candidate policies (verbatim from Block 175, parameters UNCHANGED)")
    for pid in s.get("candidate_policy_ids") or []:
        lines.append("- " + str(pid))
    lines.append("")
    lines.append("## Evaluation windows (verbatim from Block 180, same as RC1)")
    for w in s.get("evaluation_windows") or []:
        lines.append("- " + str(w.get("window_id")) + " (" + str(w.get("window"))
                     + ", " + str(w.get("window_type")) + ")")
    lines.append("")
    lines.append("## Planned cross-policy replays (NOT YET RUN)")
    for r in s.get("planned_replays") or []:
        lines.append("- " + str(r.get("replay_id")) + " -> policy " + str(r.get("policy_id"))
                     + " | is_run: " + str(r.get("is_run"))
                     + " | requires_human_command: " + str(r.get("requires_human_command")))
    lines.append("")
    lines.append("## Blockers")
    for b in (s.get("blockers") or ["(none)"]):
        lines.append("- " + str(b))
    lines.append("")
    lines.append("## Risk notes")
    for note in s.get("risk_notes") or ["(none)"]:
        lines.append("- " + str(note))
    lines.append("")
    lines.append("## Gates (read-only metadata, UNCHANGED)")
    lines.append("- paper_trading_gate: LOCKED")
    lines.append("- micro_live_gate: LOCKED")
    lines.append("- live_gate: LOCKED")
    lines.append("- runs_replay: False (a separate human command is required to run any replay)")
    return "\n".join(lines)
