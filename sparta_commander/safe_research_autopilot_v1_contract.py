"""SPARTA Safe Research Autopilot v1 -- PURE PLANNER / DECIDER.

RESEARCH ONLY. This contract is a PURE, in-memory PLANNER. Given the declared
candidate-chain state + repo cleanliness + the rejected-family ledger, it EMITS a
single recommended next SAFE action (and the human-pasteable token). It does
NOTHING else: it does NOT build files, NOT write files, NOT run any detector /
labels / replay / robustness / portfolio compute, NOT fetch data, NOT read real
data, NOT stage / commit / push, and NOT touch any paper/live/broker/credential/
order surface. Every capability flag is pinned False and a full scope_locks set
is attached, so "cannot cross into labels/replay/paper/live" is STRUCTURAL (there
is no execution capability here at all), not a runtime guard.

Auto-advance (LOW-RISK research build gates only -- the planner may recommend
these WITHOUT a human decision gate, but the planner itself still executes
nothing):
  * stage "none"               -> BUILD_NEXT_CANDIDATE_FAMILY_PROPOSAL
  * stage "proposal_ready"     -> BUILD_CANDIDATE_SPEC
  * stage "spec_ready"         -> BUILD_DETECTOR_SPEC_DRY_RUN

Hard stops (require a human decision; the planner REFUSES to auto-advance):
  * stage "detector_dry_run_ready" -> STOP_BEFORE_REAL_CANDLE_LABELS
  * stage "labels_structural_rejection"  -> RECOMMEND_REJECTION_CLOSEOUT
  * stage "replay_structural_rejection"  -> RECOMMEND_REJECTION_CLOSEOUT
  * any stage pointing at real-candle labels / replay / pnl / baseline /
    robustness / portfolio compute / paper / live / broker -> HARD_STOP
  * dirty repo or uncommitted candidate artifacts -> STOP_DIRTY_REPO
  * a proposed family that is in the rejected ledger -> HALT_PROPOSED_FAMILY_REJECTED

The planner never recommends an EDIT or ADVANCE for a structurally-rejected
candidate -- only a rejection closeout. It never emits an action that performs a
forbidden gate; at worst it emits a STOP.
"""
from __future__ import annotations

from typing import Any

SARA_SCHEMA_VERSION = 1
SARA_MODE = "RESEARCH_ONLY"

# --- canonical stages -------------------------------------------------------
STAGE_NONE = "none"
STAGE_PROPOSAL_READY = "proposal_ready"
STAGE_SPEC_READY = "spec_ready"
STAGE_DETECTOR_DRY_RUN_READY = "detector_dry_run_ready"
STAGE_LABELS_STRUCTURAL_REJECTION = "labels_structural_rejection"
STAGE_REPLAY_STRUCTURAL_REJECTION = "replay_structural_rejection"

# Stages that point at (or are at/after) a real-data / execution gate -> hard
# stop. The planner must NEVER auto-advance any of these.
FORBIDDEN_STAGES = (
    "real_candle_labels", "labels_pending", "labels_review",
    "replay", "replay_pending", "fee_honest_replay", "pnl", "baseline",
    "robustness", "portfolio_compute", "paper_trading", "micro_live",
    "live_trading", "broker", "credentials", "orders",
)

# Forbidden gate keywords the planner must never recommend crossing.
FORBIDDEN_GATES = (
    "real_candle_labels", "replay", "pnl", "baseline", "robustness",
    "portfolio_compute", "paper_trading", "live_trading", "broker",
    "credentials", "orders", "data_fetch", "real_data", "commit", "push",
)

# --- emittable actions (the COMPLETE allowlist) -----------------------------
ACTION_BUILD_PROPOSAL = "BUILD_NEXT_CANDIDATE_FAMILY_PROPOSAL"
ACTION_BUILD_SPEC = "BUILD_CANDIDATE_SPEC"
ACTION_BUILD_DETECTOR = "BUILD_DETECTOR_SPEC_DRY_RUN"
ACTION_STOP_BEFORE_LABELS = "STOP_BEFORE_REAL_CANDLE_LABELS"
ACTION_RECOMMEND_CLOSEOUT = "RECOMMEND_REJECTION_CLOSEOUT"
ACTION_STOP_DIRTY_REPO = "STOP_DIRTY_REPO"
ACTION_HALT_FAMILY_REJECTED = "HALT_PROPOSED_FAMILY_REJECTED"
ACTION_HARD_STOP_FORBIDDEN = "HARD_STOP_FORBIDDEN_GATE"

AUTO_ADVANCE_ACTIONS = (
    ACTION_BUILD_PROPOSAL, ACTION_BUILD_SPEC, ACTION_BUILD_DETECTOR)
STOP_ACTIONS = (
    ACTION_STOP_BEFORE_LABELS, ACTION_RECOMMEND_CLOSEOUT, ACTION_STOP_DIRTY_REPO,
    ACTION_HALT_FAMILY_REJECTED, ACTION_HARD_STOP_FORBIDDEN)
ALL_EMITTABLE_ACTIONS = AUTO_ADVANCE_ACTIONS + STOP_ACTIONS

# --- full rejected/closed ledger C1-C13 (planner must never re-propose these) -
DEFAULT_REJECTED_FAMILIES = (
    "ny_session_fvg_choch",
    "ny_session_fvg_choch_v3",
    "crypto_intraday_breakout_pullback_structure",
    "crypto_intraday_breakout_pullback_structure_v2",
    "long_biased_trend_continuation",
    "btc_sol_long_trend_continuation_v1",
    "long_1h_swing_structure",
    "sol_btc_long_1h_swing_structure",
    "eth_sol_relative_strength_pullback_continuation",
    "eth_sol_relative_strength_pullback_continuation_v1",
    "multi_symbol_relative_strength_rotation_filter",
    "volatility_compression_expansion",
    "liquidity_sweep_mean_reversion",
    "low_volume_downside_capitulation_mean_reversion",
    "intraweek_calendar_seasonality_drift",        # C10
    "cross_asset_dispersion_reversion",            # C11
    "failed_breakdown_reclaim_reversal",           # C12
    "lead_lag_propagation_continuation",           # C13
)

_CAPABILITY_FLAGS_FALSE = (
    "builds_files", "writes_files", "executes", "runs_detector",
    "runs_labels", "runs_real_candle_detection", "runs_replay", "computes_pnl",
    "runs_baseline", "runs_robustness", "runs_portfolio_compute",
    "fetches_data", "reads_real_data", "mutates_data", "stages_data",
    "auto_commits", "auto_pushes", "modifies_scheduler", "starts_scheduler",
    "sends_notifications", "calls_api", "uses_network", "uses_credentials",
    "connects_broker", "connects_exchange", "uses_real_money",
    "contains_order_logic", "authorizes_paper_execution",
    "authorizes_micro_live", "authorizes_live_trading", "promotes_gate",
    "unlocks_downstream_gate", "edits_rejected_candidate",
    "advances_rejected_candidate", "invokes_one_edit_allowance",
    "claims_profitability", "claims_edge", "crosses_into_forbidden_gate",
)


def _record_skeleton(chain_state: dict, repo_state: dict) -> dict[str, Any]:
    record: dict[str, Any] = {
        "schema_version": SARA_SCHEMA_VERSION, "mode": SARA_MODE,
        "lane": "crypto_d1_auto_research",
        "is_pure_planner_only": True,
        "active_candidate": chain_state.get("active_candidate"),
        "stage": chain_state.get("stage"),
        "proposed_family": chain_state.get("proposed_family"),
        "repo_clean": bool(repo_state.get("clean")),
        "uncommitted_candidate_artifacts":
            bool(repo_state.get("uncommitted_candidate_artifacts")),
        "decision": None, "next_safe_action": None,
        "auto_advanceable": False, "requires_human_approval": True,
        "is_hard_stop": False, "stops_before": None,
        "recommended_token": None, "reason": None,
        "crossed_into_forbidden_gate": False,
        "auto_advance_actions": list(AUTO_ADVANCE_ACTIONS),
        "stop_actions": list(STOP_ACTIONS),
        "forbidden_gates": list(FORBIDDEN_GATES),
        "human_review_required": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_build": True, "no_write": True, "no_execute": True,
        "no_detector_run": True, "no_labels": True, "no_replay": True,
        "no_pnl": True, "no_baseline": True, "no_robustness": True,
        "no_portfolio_compute": True, "no_data_fetch": True,
        "no_real_data_access": True, "no_stage": True, "no_commit": True,
        "no_push": True, "no_scheduler_change": True, "no_broker": True,
        "no_credentials": True, "no_order_logic": True, "no_paper_trading": True,
        "no_live_trading": True, "no_edit_of_rejected_candidate": True,
        "no_advance_of_rejected_candidate": True, "no_one_edit_invocation": True,
        "no_downstream_gate_unlock": True, "no_profitability_claim": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return record


def decide_next_safe_action(chain_state: dict, repo_state: dict,
                            rejected_families: Any = None) -> dict[str, Any]:
    """Pure planner. Returns the single recommended next SAFE action for the
    given declared state. Emits NOTHING that performs a forbidden gate; at worst
    it emits a STOP. Executes nothing."""
    rejected = tuple(rejected_families if rejected_families is not None
                     else DEFAULT_REJECTED_FAMILIES)
    r = _record_skeleton(chain_state, repo_state)
    stage = chain_state.get("stage")

    # 1) Dirty repo / uncommitted artifacts -> refuse everything.
    if (not r["repo_clean"]) or r["uncommitted_candidate_artifacts"]:
        r["decision"] = "STOP_DIRTY_REPO"
        r["next_safe_action"] = ACTION_STOP_DIRTY_REPO
        r["is_hard_stop"] = True
        r["recommended_token"] = "STOP_DIRTY_REPO_COMMIT_OR_CLEAN_FIRST"
        r["reason"] = ("repo is not clean or has uncommitted candidate "
                       "artifacts; refuse to auto-advance until clean")
        return r

    # 2) Structural-rejection stages -> recommend closeout, NOT edit/advance.
    if stage in (STAGE_LABELS_STRUCTURAL_REJECTION,
                 STAGE_REPLAY_STRUCTURAL_REJECTION):
        r["decision"] = "RECOMMEND_REJECTION_CLOSEOUT"
        r["next_safe_action"] = ACTION_RECOMMEND_CLOSEOUT
        r["recommended_token"] = "HUMAN_DECISION_REJECT_OR_REVIEW_CLOSEOUT"
        r["reason"] = ("candidate is structurally rejected at %s; recommend a "
                       "rejection closeout record -- NOT an edit or advance"
                       % stage)
        return r

    # 3) Low-risk auto-advance research build gates.
    if stage == STAGE_NONE:
        fam = chain_state.get("proposed_family")
        if fam is not None and fam in rejected:
            r["decision"] = "HALT_PROPOSED_FAMILY_REJECTED"
            r["next_safe_action"] = ACTION_HALT_FAMILY_REJECTED
            r["is_hard_stop"] = True
            r["recommended_token"] = "HALT_PROPOSED_FAMILY_IS_REJECTED"
            r["reason"] = ("proposed family %r is in the rejected/closed ledger "
                           "(C1-C13); refuse to re-propose" % fam)
            return r
        r["decision"] = "AUTO_ADVANCE_RESEARCH_BUILD"
        r["next_safe_action"] = ACTION_BUILD_PROPOSAL
        r["auto_advanceable"] = True
        r["requires_human_approval"] = False
        r["recommended_token"] = "BUILD_NEXT_CANDIDATE_FAMILY_PROPOSAL_ONLY"
        r["reason"] = ("no active candidate and ledger closed; recommend opening "
                       "the next candidate family proposal (excluding rejected)")
        return r
    if stage == STAGE_PROPOSAL_READY:
        r["decision"] = "AUTO_ADVANCE_RESEARCH_BUILD"
        r["next_safe_action"] = ACTION_BUILD_SPEC
        r["auto_advanceable"] = True
        r["requires_human_approval"] = False
        r["recommended_token"] = "BUILD_CANDIDATE_SPEC_ONLY"
        r["reason"] = "proposal ready; recommend building the spec contract"
        return r
    if stage == STAGE_SPEC_READY:
        r["decision"] = "AUTO_ADVANCE_RESEARCH_BUILD"
        r["next_safe_action"] = ACTION_BUILD_DETECTOR
        r["auto_advanceable"] = True
        r["requires_human_approval"] = False
        r["recommended_token"] = "BUILD_DETECTOR_SPEC_DRY_RUN_ONLY"
        r["reason"] = ("spec ready; recommend building the detector spec + "
                       "synthetic dry-run contract")
        return r

    # 4) Detector dry-run ready -> HARD STOP before real-candle labels.
    if stage == STAGE_DETECTOR_DRY_RUN_READY:
        r["decision"] = "HARD_STOP_HUMAN_DECISION_REQUIRED"
        r["next_safe_action"] = ACTION_STOP_BEFORE_LABELS
        r["is_hard_stop"] = True
        r["stops_before"] = "real_candle_labels"
        r["recommended_token"] = (
            "HUMAN_DECISION_ADVANCE_TO_REAL_CANDLE_LABELS_OR_REJECT")
        r["reason"] = ("detector dry-run ready; the next gate is real-candle "
                       "labels (a real-data gate) -- HARD STOP, human decision "
                       "required")
        return r

    # 5) Anything pointing at a real-data / execution gate -> hard stop.
    r["decision"] = "HARD_STOP_FORBIDDEN_GATE"
    r["next_safe_action"] = ACTION_HARD_STOP_FORBIDDEN
    r["is_hard_stop"] = True
    r["stops_before"] = stage if stage in FORBIDDEN_STAGES else "unknown_gate"
    r["recommended_token"] = "HUMAN_DECISION_REQUIRED_FORBIDDEN_GATE"
    r["reason"] = ("stage %r points at a real-data / execution gate the planner "
                   "must never auto-advance; HARD STOP" % stage)
    return r


def summarize_for_morning_report(decision: dict) -> dict[str, Any]:
    """Pure morning-report-ready summary: what the autopilot would advance and
    where it stops. The morning report can render this read-only."""
    advanced = (decision.get("next_safe_action") in AUTO_ADVANCE_ACTIONS)
    return {
        "autopilot_mode": "safe_research_planner_v1",
        "stage": decision.get("stage"),
        "decision": decision.get("decision"),
        "would_auto_advance": advanced,
        "next_safe_action": decision.get("next_safe_action"),
        "recommended_token": decision.get("recommended_token"),
        "stopped_before": decision.get("stops_before"),
        "requires_human_approval": decision.get("requires_human_approval"),
        "is_hard_stop": decision.get("is_hard_stop"),
        "reason": decision.get("reason"),
        "executes_nothing": True,
    }


def validate_safe_autopilot_decision(decision: dict) -> dict[str, Any]:
    """Anti-tamper validator. A decision is valid only when it is a pure-planner
    record that emits an action from the COMPLETE allowlist, never crosses into a
    forbidden gate, never auto-advances at the detector->labels hard stop, never
    advances/edits a rejected candidate, and pins every capability flag False."""
    failures: list = []
    if decision.get("mode") != SARA_MODE:
        failures.append("mode_not_research_only")
    if decision.get("is_pure_planner_only") is not True:
        failures.append("not_pure_planner_only")

    action = decision.get("next_safe_action")
    if action not in ALL_EMITTABLE_ACTIONS:
        failures.append("action_not_in_allowlist")
    # the action must never be a forbidden-gate executor
    if isinstance(action, str):
        low = action.lower()
        for g in ("run_labels", "run_replay", "compute_pnl", "fetch_data",
                  "paper", "live", "broker", "commit", "push"):
            if g in low:
                failures.append("action_is_forbidden_executor_%s" % g)

    if decision.get("crossed_into_forbidden_gate") is not False:
        failures.append("crossed_into_forbidden_gate_set")

    # auto-advance is only ever the 3 build gates
    if decision.get("auto_advanceable") is True:
        if action not in AUTO_ADVANCE_ACTIONS:
            failures.append("auto_advance_on_non_build_action")
        if decision.get("is_hard_stop") is True:
            failures.append("auto_advance_on_hard_stop")

    # A dirty repo / uncommitted artifacts is a legitimate higher-priority stop
    # that overrides the stage-specific action at ANY stage.
    dirty_override = (action == ACTION_STOP_DIRTY_REPO)

    # detector->labels must be a hard stop, never auto-advanced
    if decision.get("stage") == STAGE_DETECTOR_DRY_RUN_READY and not dirty_override:
        if decision.get("auto_advanceable") is not False:
            failures.append("detector_stage_auto_advanced")
        if decision.get("next_safe_action") != ACTION_STOP_BEFORE_LABELS:
            failures.append("detector_stage_not_stop_before_labels")

    # structural-rejection stages must recommend closeout (not advance/edit)
    if (decision.get("stage") in (STAGE_LABELS_STRUCTURAL_REJECTION,
                                  STAGE_REPLAY_STRUCTURAL_REJECTION)
            and not dirty_override):
        if decision.get("next_safe_action") != ACTION_RECOMMEND_CLOSEOUT:
            failures.append("rejection_stage_not_closeout")
        if decision.get("auto_advanceable") is not False:
            failures.append("rejection_stage_auto_advanced")

    # hard-stop / stop actions cannot be auto-advanceable
    if action in STOP_ACTIONS and decision.get("auto_advanceable") is not False:
        failures.append("stop_action_auto_advanceable")

    locks = decision.get("scope_locks") or {}
    for key in ("no_build", "no_write", "no_execute", "no_labels", "no_replay",
                "no_pnl", "no_baseline", "no_robustness", "no_portfolio_compute",
                "no_data_fetch", "no_real_data_access", "no_commit", "no_push",
                "no_paper_trading", "no_live_trading", "no_broker",
                "no_edit_of_rejected_candidate",
                "no_advance_of_rejected_candidate",
                "no_crossing_into_forbidden_gate"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if decision.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
