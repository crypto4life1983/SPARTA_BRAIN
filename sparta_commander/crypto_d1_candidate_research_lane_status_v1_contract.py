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

# Canonical rejected ledger (reused, not redefined): C1-C17 = 22 families
# (C17 risk-adjusted portfolio construction was rejected at the fee-honest replay).
REJECTED_FAMILIES_C1_TO_C17 = tuple(_rep.REJECTED_FAMILIES_C1_TO_C17)
REJECTED_LEDGER_COUNT = len(REJECTED_FAMILIES_C1_TO_C17)            # 22

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
STATE_ACTIVE_DETECTOR_DRY_RUN = "DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW"

# Candidate #17 -- now CLOSED / REJECTED at the fee-honest replay stage (kept on
# record). It is NO LONGER an active/open candidate. Frozen facts pinned to the
# pushed C17 chain commits. The lane reports C17 as rejected; it advances nothing.
# (Hardcoded -- the C17 proposal imports the lane via the memo, so the lane must not
# import the C17 proposal / spec / detector / labels / replay contracts.)
C17_CANDIDATE_ID = "C17"
C17_FAMILY = "risk_adjusted_portfolio_construction_vol_targeted_allocation"
C17_NAME = "risk_adjusted_portfolio_construction_vol_targeted_allocation_v1"
C17_REJECTED_AT_STAGE = "fee_honest_replay"
C17_VERDICT = "C17_REJECTED_AT_FEE_HONEST_REPLAY"
C17_METHOD = "volatility_targeted_risk_parity_allocation"
C17_ASSETS = ("BTCUSD", "ETHUSD", "SOLUSD")
C17_TIMEFRAME = "D1"
C17_LABEL = ("Risk-adjusted portfolio construction — vol-targeted / risk-parity "
             "allocation across BTC/ETH/SOL")
C17_REJECTION_REASON = (
    "REJECTED at fee-honest replay: cut max drawdown to -37.8% but failed to beat "
    "SOL buy-and-hold (Sharpe 0.80 vs 1.08, Calmar 0.47 vs 0.83) or the equal-weight "
    "basket (Sharpe 0.80 vs 1.04) on a RISK-ADJUSTED basis, and the 2026 forward-OOS "
    "edge did not hold -- lower drawdown alone is not an edge over holding the "
    "basket.")
C17_LABELS_REVIEW_COMMIT = "2064849719e7b09077ce2e983c6ecff22a24cd63"
C17_REPLAY_REVIEW_COMMIT = "329b56ce87de23899aa5ceb510d66eb1959bd3bf"

# The candidate-research lane summary: C13-C17 all rejected (kept on record). C17
# was rejected at the fee-honest replay stage -- there is NO active/open candidate.
CANDIDATE_LANE = (
    {"candidate": "C13", "family": "lead_lag_propagation_continuation",
     "state": STATE_REJECTED, "rejected_at": "real_candle_labels"},
    {"candidate": "C14", "family": "conviction_bar_follow_through",
     "state": STATE_REJECTED, "rejected_at": "fee_honest_replay"},
    {"candidate": "C15", "family": "slow_vol_targeted_time_series_momentum",
     "state": STATE_REJECTED, "rejected_at": "fee_honest_replay"},
    {"candidate": "C16", "family": "cointegration_pairs_market_neutral",
     "state": STATE_REJECTED, "rejected_at": "real_candle_labels"},
    {"candidate": "C17", "family": C17_FAMILY, "state": STATE_REJECTED,
     "rejected_at": C17_REJECTED_AT_STAGE},
)

# The PRIOR-stage automation-readiness token (stable; kept for provenance and for
# the automation-readiness prep/memo artifacts that belong to that stage).
AUTOMATION_READINESS_TOKEN = "BUILD_AUTOMATION_READINESS_STEP_RESEARCH_ONLY"

# With C17 rejected and NO active/open candidate, the CURRENT next stage is again
# AUTOMATION READINESS (research-only, human-gated) -- NOT a new candidate (no C18
# is proposed here).
NEXT_REQUIRED_ACTION = AUTOMATION_READINESS_TOKEN
NEXT_STAGE = "automation_readiness"

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
    after C16. Records C16 complete, the C1-C16 (21) rejected ledger, and that
    Candidate #17 is the ACTIVE open candidate at the detector-spec + synthetic
    dry-run stage awaiting the human real-candle-labels decision. Executes
    nothing."""
    record: dict[str, Any] = {
        "version": LANE_STATUS_VERSION, "mode": LANE_STATUS_MODE, "lane": LANE,
        "is_pure_status_only": True,
        "label": (
            "Crypto-D1 candidate research lane status (READ-ONLY, RESEARCH ONLY). "
            "C16 lifecycle COMPLETE; rejected ledger C1-C17 (22 families). "
            "Candidate #17 (risk-adjusted portfolio construction) is now CLOSED / "
            "REJECTED at the fee-honest replay stage (kept on record): it cut "
            "drawdown but did not beat buy-and-hold / the equal-weight basket "
            "risk-adjusted and the 2026 forward-OOS edge did not hold. There is NO "
            "active/open candidate; the next stage is AUTOMATION READINESS. "
            "Overnight/morning automation stays research-only and human-gated. "
            "Executes nothing."),
        # C16 completion (unchanged)
        "c16_lifecycle_complete": True,
        "c16_candidate_family": "cointegration_pairs_market_neutral",
        "c16_rejection_verdict": "REJECT_C16_AT_LABELS",
        "c16_lifecycle_gates": [dict(g) for g in C16_LIFECYCLE_GATES],
        "c16_in_rejected_ledger":
            "cointegration_pairs_market_neutral" in REJECTED_FAMILIES_C1_TO_C17,
        # rejected ledger -- now C1-C17 (22), C17 added
        "rejected_ledger_count": REJECTED_LEDGER_COUNT,
        "rejected_ledger_is_c1_to_c17": REJECTED_LEDGER_COUNT == 22,
        "rejected_families": list(REJECTED_FAMILIES_C1_TO_C17),
        "c17_in_rejected_ledger": C17_FAMILY in REJECTED_FAMILIES_C1_TO_C17,
        # candidate lane summary -- C17 is now REJECTED; NO active/open candidate
        "candidate_lane": [dict(c) for c in CANDIDATE_LANE],
        "active_candidate": None,
        "open_candidate_gate": False,
        "active_candidate_detail": None,
        "last_rejected_candidate": C17_CANDIDATE_ID,
        "last_rejected_candidate_detail": {
            "candidate": C17_CANDIDATE_ID, "family": C17_FAMILY,
            "name": C17_NAME, "label": C17_LABEL, "verdict": C17_VERDICT,
            "rejected_at": C17_REJECTED_AT_STAGE, "method": C17_METHOD,
            "assets": list(C17_ASSETS), "timeframe": C17_TIMEFRAME,
            "rejection_reason": C17_REJECTION_REASON,
            "labels_review_commit": C17_LABELS_REVIEW_COMMIT,
            "replay_review_commit": C17_REPLAY_REVIEW_COMMIT,
        },
        # next stage = AUTOMATION READINESS again (C17 rejected, no active candidate,
        # and NO new candidate / C18 is proposed here).
        "current_stage": "c17_rejected_at_fee_honest_replay",
        "next_stage": NEXT_STAGE,
        "next_is_automation_readiness": True,
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
    """Pure morning-report-ready block: C16 complete, ledger C1-C17 (22), and
    Candidate #17 now REJECTED at fee-honest replay (no active/open candidate; next
    stage = automation readiness). Read-only; executes nothing."""
    s = get_lane_status()
    rej = s["last_rejected_candidate_detail"]
    return {
        "section": "candidate_research_lane_status",
        "c16_lifecycle_complete": s["c16_lifecycle_complete"],
        "rejected_ledger_count": s["rejected_ledger_count"],
        "active_candidate": s["active_candidate"],
        "open_candidate_gate": s["open_candidate_gate"],
        "last_rejected_candidate": s["last_rejected_candidate"],
        "last_rejected_candidate_verdict": rej["verdict"],
        "last_rejected_candidate_rejected_at": rej["rejected_at"],
        "last_rejected_candidate_reason": rej["rejection_reason"],
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
    only, records C16 complete + C1-C17 (22) ledger, marks Candidate #17 REJECTED at
    the fee-honest replay stage (kept on record, NOT active/open), reports NO active
    candidate with the next stage = AUTOMATION READINESS (NOT a new candidate), keeps
    the automation path research-only with all downstream capability blocked/locked,
    and pins every capability flag False."""
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

    # rejected ledger C1-C17 (22), C17 added
    if record.get("rejected_ledger_count") != 22:
        failures.append("rejected_ledger_not_22")
    if record.get("rejected_ledger_is_c1_to_c17") is not True:
        failures.append("ledger_not_marked_c1_to_c17")
    if "cointegration_pairs_market_neutral" not in (
            record.get("rejected_families") or []):
        failures.append("ledger_missing_c16_family")
    if C17_FAMILY not in (record.get("rejected_families") or []):
        failures.append("ledger_missing_c17_family")
    if record.get("c17_in_rejected_ledger") is not True:
        failures.append("c17_not_in_ledger")

    # C17 is REJECTED at fee-honest replay (kept on record); NO active/open
    # candidate; next stage = AUTOMATION READINESS and NOT a new candidate.
    if record.get("active_candidate") is not None:
        failures.append("must_have_no_active_candidate")
    if record.get("open_candidate_gate") is not False:
        failures.append("open_candidate_gate_must_be_false")
    if record.get("active_candidate_detail") is not None:
        failures.append("active_candidate_detail_must_be_none")
    if record.get("last_rejected_candidate") != C17_CANDIDATE_ID:
        failures.append("last_rejected_not_c17")
    rej = record.get("last_rejected_candidate_detail") or {}
    if rej.get("family") != C17_FAMILY:
        failures.append("c17_family_mismatch")
    if rej.get("verdict") != C17_VERDICT:
        failures.append("c17_verdict_not_rejected_at_replay")
    if rej.get("rejected_at") != C17_REJECTED_AT_STAGE:
        failures.append("c17_not_rejected_at_fee_honest_replay")
    if not rej.get("rejection_reason"):
        failures.append("c17_rejection_reason_missing")
    if not (isinstance(rej.get("replay_review_commit"), str)
            and len(rej["replay_review_commit"]) == 40):
        failures.append("c17_replay_review_commit_bad")
    if not (isinstance(rej.get("labels_review_commit"), str)
            and len(rej["labels_review_commit"]) == 40):
        failures.append("c17_labels_review_commit_bad")
    if record.get("next_stage") != NEXT_STAGE:
        failures.append("next_stage_not_automation_readiness")
    if record.get("next_is_automation_readiness") is not True:
        failures.append("next_must_be_automation_readiness")
    if record.get("next_is_new_candidate") is not False:
        failures.append("next_must_not_be_new_candidate")
    if record.get("next_required_action") != AUTOMATION_READINESS_TOKEN:
        failures.append("next_action_not_automation_readiness")
    # C17 must appear in the candidate lane as REJECTED at fee-honest replay
    lane_c17 = next((c for c in (record.get("candidate_lane") or [])
                     if c.get("candidate") == "C17"), None)
    if not lane_c17 or lane_c17.get("state") != STATE_REJECTED \
            or lane_c17.get("rejected_at") != C17_REJECTED_AT_STAGE:
        failures.append("c17_not_rejected_in_candidate_lane")

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
