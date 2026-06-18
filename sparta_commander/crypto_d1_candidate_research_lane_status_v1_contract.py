"""SPARTA Crypto-D1 Candidate Research Lane -- STATUS / BUNDLE SURFACE v1
(PURE, RESEARCH ONLY).

A pure, stdlib-only, read-only status snapshot for the Crypto-D1 candidate-research
lane (the C10-C16 candidate-rejection lane that lives in the Research Expansion
Plan / Safe Research Autopilot / Integration Spec / Gate Decision Coordinator
cluster). It records -- deterministically, from already-committed contract state --
that the C16 lifecycle is COMPLETE, that the canonical rejected ledger is now
C1-C16 (21 families), and that the next stage is AUTOMATION READINESS (not another
candidate). It is a map of state, not a controller.

It executes NOTHING: no detector, no labels, no replay, no PnL, no optimization,
no data fetch, no writes, no stage/commit/push, no paper/live/broker/order surface.
The overnight/morning automation path stays RESEARCH-ONLY and human-gated; every
real-world capability remains blocked/locked. Every capability flag is pinned False
with a full scope_locks set.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.research_expansion_plan_v1_contract as _rep

LANE_STATUS_VERSION = "v1"
LANE_STATUS_MODE = "RESEARCH_ONLY"
LANE = "crypto_d1_auto_research"

# Canonical rejected ledger (reused, not redefined): C1-C16 = 21 families.
REJECTED_FAMILIES_C1_TO_C16 = tuple(_rep.REJECTED_FAMILIES_C1_TO_C16)
REJECTED_LEDGER_COUNT = len(REJECTED_FAMILIES_C1_TO_C16)            # 21

# Status vocabulary (display-only).
STATE_COMPLETE = "COMPLETE"
STATE_REJECTED = "REJECTED_KEPT_ON_RECORD"
STATE_CURRENT = "CURRENT"
STATE_NEXT = "NEXT"
STATE_BLOCKED = "BLOCKED"
STATE_LOCKED = "LOCKED"

# The C16 lifecycle gates, all shipped on origin/master (read-only provenance).
C16_LIFECYCLE_GATES = (
    {"stage": "family_proposal",
     "commit": "38ccce6296e93b92dffcfa4a46d02349ebe40e76"},
    {"stage": "candidate_spec",
     "commit": "9c2b39cc64e156167d28621403e1b5892e2a308a"},
    {"stage": "detector_spec_and_synthetic_dry_run",
     "commit": "0c5f27a0e749f0842b99874b95d37f38f88a9887"},
    {"stage": "real_candle_labels_review",
     "commit": "ae16daf0a8c139cee1f6a1bb177ca99be027d198"},
    {"stage": "rejection_record",
     "commit": "c256c24fdc7c08f02afb4c08855216861372ece1"},
    {"stage": "canonical_ledger_bump",
     "commit": "1d0b0dcd5fe7a40fe8bdcec906f955170c8039c4"},
)

STATE_ACTIVE_PROPOSAL = "PROPOSED_FROZEN_FOR_HUMAN_REVIEW"
STATE_ACTIVE_SPEC = "SPEC_FROZEN_FOR_HUMAN_REVIEW"

# Candidate #17 -- the ACTIVE open candidate. It has now advanced through the
# human spec gate: the candidate SPEC is committed and frozen for human review.
# Frozen facts pinned to the pushed C17 proposal + spec commits. The lane reports
# C17; it creates nothing and advances nothing. (Hardcoded -- the C17 proposal
# imports the lane via the memo, so the lane must not import the C17 proposal or
# spec.)
C17_CANDIDATE_ID = "C17"
C17_FAMILY = "risk_adjusted_portfolio_construction_vol_targeted_allocation"
C17_NAME = "risk_adjusted_portfolio_construction_vol_targeted_allocation_v1"
C17_STAGE = "candidate_spec"
C17_STAGE_LABEL = STATE_ACTIVE_SPEC                  # SPEC_FROZEN_FOR_HUMAN_REVIEW
C17_VERDICT = "C17_SPEC_FROZEN_FOR_HUMAN_REVIEW"
C17_METHOD = "volatility_targeted_risk_parity_allocation"
C17_ASSETS = ("BTCUSD", "ETHUSD", "SOLUSD")
C17_TIMEFRAME = "D1"
C17_LABEL = ("Risk-adjusted portfolio construction — vol-targeted / risk-parity "
             "allocation across BTC/ETH/SOL")
C17_PROPOSAL_COMMIT = "1c3a4671cb3a0d238825dd7d7b7070a50f40d419"
C17_SPEC_COMMIT = "8c22e085198c1a63595f8f49abaf01f6e7f71ea3"
C17_NEXT_GATE = "HUMAN_DECISION_C17_ADVANCE_TO_DETECTOR_SPEC_DRY_RUN_OR_REJECT"

# The candidate-research lane summary: C13-C16 rejected (kept on record), C17 now
# ACTIVE with a frozen candidate SPEC awaiting the human detector-spec decision.
CANDIDATE_LANE = (
    {"candidate": "C13", "family": "lead_lag_propagation_continuation",
     "state": STATE_REJECTED, "rejected_at": "real_candle_labels"},
    {"candidate": "C14", "family": "conviction_bar_follow_through",
     "state": STATE_REJECTED, "rejected_at": "fee_honest_replay"},
    {"candidate": "C15", "family": "slow_vol_targeted_time_series_momentum",
     "state": STATE_REJECTED, "rejected_at": "fee_honest_replay"},
    {"candidate": "C16", "family": "cointegration_pairs_market_neutral",
     "state": STATE_REJECTED, "rejected_at": "real_candle_labels"},
    {"candidate": "C17", "family": C17_FAMILY, "state": STATE_ACTIVE_SPEC,
     "stage": C17_STAGE, "verdict": C17_VERDICT},
)

# The PRIOR-stage automation-readiness token (stable; kept for provenance and for
# the automation-readiness prep/memo artifacts that belong to that stage).
AUTOMATION_READINESS_TOKEN = "BUILD_AUTOMATION_READINESS_STEP_RESEARCH_ONLY"

# The CURRENT next stage is the C17 human detector-spec decision (an open candidate
# gate), NOT automation readiness any more -- automation readiness was the PRIOR
# stage that produced the research memo that led to C17, and the spec gate has
# already been cleared (the candidate SPEC is committed and frozen).
NEXT_REQUIRED_ACTION = C17_NEXT_GATE
NEXT_STAGE = "c17_detector_spec_dry_run_decision"

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "runs_detector", "runs_labels", "runs_replay",
    "computes_pnl", "optimizes_parameters", "runs_robustness",
    "runs_portfolio_compute", "fetches_data", "reads_real_data", "mutates_data",
    "stages_data", "auto_commits", "auto_pushes", "starts_a_new_candidate",
    "modifies_scheduler", "starts_scheduler", "sends_notifications", "calls_api",
    "uses_network", "uses_credentials", "connects_broker", "connects_exchange",
    "uses_real_money", "places_orders", "contains_order_logic", "paper_trading",
    "live_trading", "deploys_capital", "promotes_gate", "unlocks_downstream_gate",
    "skips_any_gate", "advances_without_human_approval", "claims_profitability",
    "claims_edge", "crosses_into_forbidden_gate",
)


def safety_flags() -> dict[str, Any]:
    """Read-only safety posture: nothing here executes or mutates anything; the
    overnight/morning automation path stays research-only and human-gated."""
    return {
        "mode": LANE_STATUS_MODE, "read_only": True, "executes": False,
        "human_approval_required": True,
        "overnight_automation_research_only": True,
        "morning_report_research_only": True,
        "runs_detector": False, "runs_labels": False, "runs_replay": False,
        "computes_pnl": False, "fetches_data": False,
        "touches_broker_or_exchange": False, "paper_or_live": False,
        "starts_a_new_candidate": False,
        "real_data_qa_blocked": True, "replay_blocked": True,
        "paper_locked": True, "micro_live_locked": True, "live_locked": True,
    }


def get_lane_status() -> dict[str, Any]:
    """Deterministic, read-only snapshot of the Crypto-D1 candidate research lane
    after C16. Records C16 complete, the C1-C16 (21) rejected ledger, and that the
    next stage is automation readiness. Executes nothing."""
    record: dict[str, Any] = {
        "version": LANE_STATUS_VERSION, "mode": LANE_STATUS_MODE, "lane": LANE,
        "is_pure_status_only": True,
        "label": (
            "Crypto-D1 candidate research lane status (READ-ONLY, RESEARCH ONLY). "
            "C16 lifecycle COMPLETE; rejected ledger C1-C16 (21 families). "
            "Candidate #17 is the ACTIVE open candidate with a frozen candidate "
            "SPEC: Risk-adjusted portfolio construction — vol-targeted / risk-parity "
            "allocation across BTC/ETH/SOL on D1, awaiting the human detector-spec "
            "decision. Overnight/morning automation stays research-only and "
            "human-gated. Executes nothing."),
        # C16 completion (unchanged)
        "c16_lifecycle_complete": True,
        "c16_candidate_family": "cointegration_pairs_market_neutral",
        "c16_rejection_verdict": "REJECT_C16_AT_LABELS",
        "c16_lifecycle_gates": [dict(g) for g in C16_LIFECYCLE_GATES],
        "c16_in_rejected_ledger":
            "cointegration_pairs_market_neutral" in REJECTED_FAMILIES_C1_TO_C16,
        # rejected ledger (unchanged)
        "rejected_ledger_count": REJECTED_LEDGER_COUNT,
        "rejected_ledger_is_c1_to_c16": REJECTED_LEDGER_COUNT == 21,
        "rejected_families": list(REJECTED_FAMILIES_C1_TO_C16),
        # candidate lane summary -- C17 is now ACTIVE/open
        "candidate_lane": [dict(c) for c in CANDIDATE_LANE],
        "active_candidate": C17_CANDIDATE_ID,
        "open_candidate_gate": True,
        "active_candidate_detail": {
            "candidate": C17_CANDIDATE_ID, "family": C17_FAMILY,
            "name": C17_NAME, "label": C17_LABEL, "verdict": C17_VERDICT,
            "stage": C17_STAGE, "stage_label": C17_STAGE_LABEL,
            "method": C17_METHOD, "assets": list(C17_ASSETS),
            "timeframe": C17_TIMEFRAME,
            "proposal_commit": C17_PROPOSAL_COMMIT, "spec_commit": C17_SPEC_COMMIT,
            "next_action": C17_NEXT_GATE,
        },
        # next stage = the C17 human detector-spec decision (open gate), NOT
        # automation readiness. Automation readiness was the PRIOR stage that
        # produced the research memo that led to C17 (still visible as provenance,
        # below). The candidate SPEC gate has already been cleared.
        "current_stage": "c17_candidate_spec_frozen_for_human_review",
        "next_stage": NEXT_STAGE,
        "next_is_automation_readiness": False,
        "automation_readiness_was_prior_stage": True,
        "next_strategy_memo_led_to_c17": True,
        "next_is_new_candidate": False,
        "next_required_action": NEXT_REQUIRED_ACTION,
        "requires_human_approval": True,
        # automation path posture
        "overnight_automation_research_only": True,
        "morning_report_research_only": True,
        "safety_flags": safety_flags(),
        # downstream real-world capability stays blocked/locked
        "real_data_qa_state": STATE_BLOCKED,
        "replay_state": STATE_BLOCKED,
        "paper_trading_state": STATE_LOCKED,
        "live_trading_state": STATE_LOCKED,
        "human_review_required": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_execute": True, "no_write": True, "no_detector": True,
        "no_labels": True, "no_replay": True, "no_pnl": True,
        "no_optimization": True, "no_robustness": True, "no_portfolio_compute": True,
        "no_data_fetch": True, "no_real_data_access": True, "no_stage": True,
        "no_commit": True, "no_push": True, "no_auto_commit": True,
        "no_auto_push": True, "no_new_candidate": True, "no_scheduler_change": True,
        "no_broker": True, "no_credentials": True, "no_order_logic": True,
        "no_paper_trading": True, "no_live_trading": True, "no_gate_skip": True,
        "no_downstream_gate_unlock": True, "no_profitability_claim": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return record


def summarize_for_morning_report() -> dict[str, Any]:
    """Pure morning-report-ready block: C16 complete, ledger C1-C16 (21), and
    Candidate #17 ACTIVE with a frozen candidate SPEC awaiting the human
    detector-spec decision. Read-only; executes nothing."""
    s = get_lane_status()
    det = s["active_candidate_detail"]
    return {
        "section": "candidate_research_lane_status",
        "c16_lifecycle_complete": s["c16_lifecycle_complete"],
        "rejected_ledger_count": s["rejected_ledger_count"],
        "active_candidate": s["active_candidate"],
        "active_candidate_label": det["label"],
        "active_candidate_verdict": det["verdict"],
        "active_candidate_stage": det["stage"],
        "active_candidate_stage_label": det["stage_label"],
        "active_candidate_method": det["method"],
        "active_candidate_assets": det["assets"],
        "active_candidate_timeframe": det["timeframe"],
        "open_candidate_gate": s["open_candidate_gate"],
        "current_stage": s["current_stage"],
        "next_stage": s["next_stage"],
        "next_is_automation_readiness": s["next_is_automation_readiness"],
        "next_is_new_candidate": s["next_is_new_candidate"],
        "next_required_action": s["next_required_action"],
        "overnight_automation_research_only": s["overnight_automation_research_only"],
        "requires_human_approval": True,
        "executes_nothing": True,
    }


def validate_lane_status(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the status is research-only, status-
    only, records C16 complete + C1-C16 (21) ledger, marks Candidate #17 the ACTIVE
    open candidate with a frozen candidate SPEC (vol-targeted risk-parity, BTC/ETH/
    SOL, D1) whose next gate is the human detector-spec decision (NOT automation
    readiness and NOT a new candidate), keeps the automation path research-only with
    all downstream capability blocked/locked, and pins every capability flag
    False."""
    failures: list = []
    if record.get("mode") != LANE_STATUS_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_pure_status_only") is not True:
        failures.append("not_pure_status_only")

    # C16 completion
    if record.get("c16_lifecycle_complete") is not True:
        failures.append("c16_not_complete")
    if record.get("c16_in_rejected_ledger") is not True:
        failures.append("c16_not_in_ledger")
    if len(record.get("c16_lifecycle_gates") or []) != 6:
        failures.append("c16_lifecycle_gates_count_unexpected")
    for g in (record.get("c16_lifecycle_gates") or []):
        if not (isinstance(g.get("commit"), str) and len(g["commit"]) == 40):
            failures.append("c16_gate_bad_commit_%s" % g.get("stage"))

    # rejected ledger C1-C16 (21)
    if record.get("rejected_ledger_count") != 21:
        failures.append("rejected_ledger_not_21")
    if record.get("rejected_ledger_is_c1_to_c16") is not True:
        failures.append("ledger_not_marked_c1_to_c16")
    if "cointegration_pairs_market_neutral" not in (
            record.get("rejected_families") or []):
        failures.append("ledger_missing_c16_family")

    # C17 is the ACTIVE open candidate; next stage = the C17 human spec decision,
    # NOT automation readiness and NOT a new candidate.
    if record.get("active_candidate") != C17_CANDIDATE_ID:
        failures.append("c17_not_active")
    if record.get("open_candidate_gate") is not True:
        failures.append("open_candidate_gate_expected")
    det = record.get("active_candidate_detail") or {}
    if det.get("family") != C17_FAMILY:
        failures.append("c17_family_mismatch")
    if det.get("verdict") != C17_VERDICT:
        failures.append("c17_verdict_mismatch")
    if det.get("stage") != C17_STAGE:
        failures.append("c17_stage_not_candidate_spec")
    if det.get("stage_label") != STATE_ACTIVE_SPEC:
        failures.append("c17_stage_label_not_spec_frozen")
    if det.get("method") != C17_METHOD:
        failures.append("c17_method_mismatch")
    if list(det.get("assets") or []) != list(C17_ASSETS):
        failures.append("c17_assets_not_btc_eth_sol")
    if det.get("timeframe") != C17_TIMEFRAME:
        failures.append("c17_timeframe_not_d1")
    if det.get("next_action") != C17_NEXT_GATE:
        failures.append("c17_next_gate_mismatch")
    if record.get("next_stage") != NEXT_STAGE:
        failures.append("next_stage_not_c17_detector_spec_decision")
    if record.get("next_is_automation_readiness") is not False:
        failures.append("must_not_be_automation_readiness_while_c17_open")
    if record.get("next_is_new_candidate") is not False:
        failures.append("next_must_not_be_new_candidate")
    if record.get("next_required_action") != C17_NEXT_GATE:
        failures.append("next_action_not_c17_gate")
    # C17 must appear in the candidate lane as an active frozen SPEC
    lane_c17 = next((c for c in (record.get("candidate_lane") or [])
                     if c.get("candidate") == "C17"), None)
    if not lane_c17 or lane_c17.get("state") != STATE_ACTIVE_SPEC:
        failures.append("c17_not_active_spec_in_candidate_lane")

    # automation path research-only + downstream blocked/locked
    if record.get("overnight_automation_research_only") is not True:
        failures.append("overnight_not_research_only")
    if record.get("real_data_qa_state") != STATE_BLOCKED:
        failures.append("real_data_qa_not_blocked")
    if record.get("replay_state") != STATE_BLOCKED:
        failures.append("replay_not_blocked")
    if record.get("paper_trading_state") != STATE_LOCKED:
        failures.append("paper_not_locked")
    if record.get("live_trading_state") != STATE_LOCKED:
        failures.append("live_not_locked")

    sf = record.get("safety_flags") or {}
    for k in ("read_only", "human_approval_required",
              "overnight_automation_research_only"):
        if sf.get(k) is not True:
            failures.append("safety_flag_off_%s" % k)
    for k in ("executes", "starts_a_new_candidate", "paper_or_live"):
        if sf.get(k) is not False:
            failures.append("safety_flag_on_%s" % k)

    locks = record.get("scope_locks") or {}
    for key in ("no_execute", "no_detector", "no_labels", "no_replay", "no_pnl",
                "no_optimization", "no_data_fetch", "no_commit", "no_push",
                "no_new_candidate", "no_broker", "no_order_logic",
                "no_paper_trading", "no_live_trading", "no_gate_skip"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
