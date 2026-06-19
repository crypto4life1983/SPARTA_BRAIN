"""SPARTA Crypto-D1 Candidate Research Lane -- STATUS / BUNDLE SURFACE v1
(PURE, RESEARCH ONLY).

A pure, stdlib-only, read-only status snapshot for the Crypto-D1 candidate-research
lane. It records -- deterministically, from already-committed contract state -- that
the C16 lifecycle is COMPLETE, that the canonical rejected ledger is now C1-C19 (24
families), that C17/C18 are rejected at fee-honest replay and C19 is rejected at the
real-candle labels / neutrality gate (all kept on record), and that there is NO
active/open candidate -- the next stage is AUTOMATION READINESS. It is a map of
state, not a controller.

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

# Canonical rejected ledger (reused, not redefined): C1-C19 = 24 families.
REJECTED_FAMILIES_C1_TO_C19 = tuple(_rep.REJECTED_FAMILIES_C1_TO_C19)
REJECTED_LEDGER_COUNT = len(REJECTED_FAMILIES_C1_TO_C19)            # 24

# Status vocabulary (display-only).
STATE_COMPLETE = "COMPLETE"
STATE_REJECTED = "REJECTED_KEPT_ON_RECORD"
STATE_CURRENT = "CURRENT"
STATE_NEXT = "NEXT"
STATE_BLOCKED = "BLOCKED"
STATE_LOCKED = "LOCKED"
STATE_ACTIVE_PROPOSAL = "PROPOSED_FROZEN_FOR_HUMAN_REVIEW"

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

# Candidate #18 -- CLOSED / REJECTED at fee-honest replay (kept on record). Prior.
C18_CANDIDATE_ID = "C18"
C18_FAMILY = "h4_trend_following_market_structure"
C18_REJECTED_AT_STAGE = "fee_honest_replay"
C18_VERDICT = "C18_REJECTED_AT_FEE_HONEST_REPLAY"

# Candidate #19 -- now CLOSED / REJECTED at the real-candle labels / neutrality gate
# (kept on record). It is the LAST rejected candidate. The position mechanics were
# clean but only 41 tradeable entries (< 100 structural sample gate) and the
# return-beta residual was beta-neutral out-of-sample on only 862/1977 bars (~44%) --
# echoing the C16 failure that neutrality does not persist out of sample; no
# fee-honest replay was run. Frozen facts pinned to the pushed C19 chain commits.
C19_CANDIDATE_ID = "C19"
C19_FAMILY = "oos_validated_beta_neutral_cross_sectional_relative_value"
C19_NAME = "oos_validated_beta_neutral_cross_sectional_relative_value_v1"
C19_REJECTED_AT_STAGE = "real_candle_labels_neutrality_gate"
C19_VERDICT = "C19_REJECTED_AT_REAL_CANDLE_LABELS"
C19_METHOD = "return_space_beta_neutral_cross_sectional_relative_value"
C19_ASSETS = ("BTCUSD", "ETHUSD", "SOLUSD")
C19_TIMEFRAME = "D1"
C19_LABEL = ("OOS-validated beta-neutral cross-sectional relative value — a "
             "continuous dollar+return-beta-neutral residual among BTC/ETH/SOL (D1, "
             "cached), market-neutral, with OOS neutrality validation as gate zero")
C19_REJECTION_REASON = (
    "REJECTED at the real-candle labels / neutrality gate: mechanics clean (gross "
    "capped 1.0, one live position, >= 5-bar spacing) but only 41 tradeable entries "
    "(< 100 structural sample gate) and OOS beta-neutrality held on only 862/1977 "
    "bars (~44%), with 15 positions closed by neutrality-break -- echoing the C16 "
    "failure that return-beta neutrality does not persist out of sample. No "
    "fee-honest replay was run; the neutral residual is not stable enough to justify "
    "it.")
C19_LABELS_REVIEW_COMMIT = "c9470c085555bbbb0928b178a86181a95a76088e"

# The candidate-research lane summary: C13-C19 all rejected (kept on record). C19 was
# rejected at the real-candle labels / neutrality gate -- there is NO active/open
# candidate.
CANDIDATE_LANE = (
    {"candidate": "C13", "family": "lead_lag_propagation_continuation",
     "state": STATE_REJECTED, "rejected_at": "real_candle_labels"},
    {"candidate": "C14", "family": "conviction_bar_follow_through",
     "state": STATE_REJECTED, "rejected_at": "fee_honest_replay"},
    {"candidate": "C15", "family": "slow_vol_targeted_time_series_momentum",
     "state": STATE_REJECTED, "rejected_at": "fee_honest_replay"},
    {"candidate": "C16", "family": "cointegration_pairs_market_neutral",
     "state": STATE_REJECTED, "rejected_at": "real_candle_labels"},
    {"candidate": "C17",
     "family": "risk_adjusted_portfolio_construction_vol_targeted_allocation",
     "state": STATE_REJECTED, "rejected_at": "fee_honest_replay"},
    {"candidate": "C18", "family": C18_FAMILY, "state": STATE_REJECTED,
     "rejected_at": C18_REJECTED_AT_STAGE},
    {"candidate": "C19", "family": C19_FAMILY, "state": STATE_REJECTED,
     "rejected_at": C19_REJECTED_AT_STAGE},
)

# The PRIOR-stage automation-readiness token (stable; kept for provenance).
AUTOMATION_READINESS_TOKEN = "BUILD_AUTOMATION_READINESS_STEP_RESEARCH_ONLY"

# With C19 rejected and NO active/open candidate, the CURRENT next stage is again
# AUTOMATION READINESS (research-only, human-gated) -- NOT a new candidate (no C20).
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
    """Deterministic, read-only snapshot of the Crypto-D1 candidate research lane.
    Records C16 complete, the C1-C19 (24) rejected ledger, and that there is NO
    active/open candidate after Candidate #19 (OOS-validated beta-neutral
    cross-sectional relative value) was rejected at the real-candle labels /
    neutrality gate -- the next stage is AUTOMATION READINESS. Executes nothing."""
    record: dict[str, Any] = {
        "version": LANE_STATUS_VERSION, "mode": LANE_STATUS_MODE, "lane": LANE,
        "is_pure_status_only": True,
        "label": (
            "Crypto-D1 candidate research lane status (READ-ONLY, RESEARCH ONLY). "
            "C16 lifecycle COMPLETE; rejected ledger C1-C19 (24 families). "
            "Candidate #19 (OOS-validated beta-neutral cross-sectional relative "
            "value) is now CLOSED / REJECTED at the real-candle labels / neutrality "
            "gate (kept on record): mechanics clean but only 41 entries (< 100 gate) "
            "and OOS beta-neutrality held on only ~44% of bars -- the C16 echo; no "
            "fee-honest replay was run. There is NO active/open candidate; the next "
            "stage is AUTOMATION READINESS. Overnight/morning automation stays "
            "research-only and human-gated. Executes nothing."),
        # C16 completion (unchanged)
        "c16_lifecycle_complete": True,
        "c16_candidate_family": "cointegration_pairs_market_neutral",
        "c16_rejection_verdict": "REJECT_C16_AT_LABELS",
        "c16_lifecycle_gates": [dict(g) for g in C16_LIFECYCLE_GATES],
        "c16_in_rejected_ledger":
            "cointegration_pairs_market_neutral" in REJECTED_FAMILIES_C1_TO_C19,
        # rejected ledger -- now C1-C19 (24), C19 added
        "rejected_ledger_count": REJECTED_LEDGER_COUNT,
        "rejected_ledger_is_c1_to_c19": REJECTED_LEDGER_COUNT == 24,
        "rejected_families": list(REJECTED_FAMILIES_C1_TO_C19),
        "c18_in_rejected_ledger": C18_FAMILY in REJECTED_FAMILIES_C1_TO_C19,
        "c19_in_rejected_ledger": C19_FAMILY in REJECTED_FAMILIES_C1_TO_C19,
        # candidate lane summary -- C19 is now REJECTED; NO active/open candidate
        "candidate_lane": [dict(c) for c in CANDIDATE_LANE],
        "active_candidate": None,
        "open_candidate_gate": False,
        "active_candidate_detail": None,
        # C19 is now the last rejected candidate (provenance); C18 before it.
        "last_rejected_candidate": C19_CANDIDATE_ID,
        "last_rejected_candidate_detail": {
            "candidate": C19_CANDIDATE_ID, "family": C19_FAMILY,
            "name": C19_NAME, "label": C19_LABEL, "verdict": C19_VERDICT,
            "rejected_at": C19_REJECTED_AT_STAGE, "method": C19_METHOD,
            "assets": list(C19_ASSETS), "timeframe": C19_TIMEFRAME,
            "rejection_reason": C19_REJECTION_REASON,
            "is_market_neutral": True,
            "labels_review_commit": C19_LABELS_REVIEW_COMMIT,
        },
        "prior_rejected_candidate": C18_CANDIDATE_ID,
        "prior_rejected_candidate_verdict": C18_VERDICT,
        # next stage = AUTOMATION READINESS (C19 rejected, no active candidate, no C20)
        "current_stage": "c19_rejected_at_real_candle_labels_neutrality_gate",
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
    """Pure morning-report-ready block: C16 complete, ledger C1-C19 (24), and
    Candidate #19 now REJECTED at the real-candle labels / neutrality gate (no
    active/open candidate; next stage = automation readiness). Read-only; executes
    nothing."""
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
    only, records C16 complete + C1-C19 (24) ledger (C18 rejected at replay and C19
    at the labels/neutrality gate, kept on record), marks Candidate #19 REJECTED at
    the real-candle labels / neutrality gate (kept on record, NOT active/open),
    reports NO active candidate with the next stage = AUTOMATION READINESS (NOT a new
    candidate), keeps the automation path research-only with all downstream capability
    blocked/locked, and pins every capability flag False."""
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

    # rejected ledger C1-C19 (24), C19 added
    if record.get("rejected_ledger_count") != 24:
        failures.append("rejected_ledger_not_24")
    if record.get("rejected_ledger_is_c1_to_c19") is not True:
        failures.append("ledger_not_marked_c1_to_c19")
    if "cointegration_pairs_market_neutral" not in (
            record.get("rejected_families") or []):
        failures.append("ledger_missing_c16_family")
    if C18_FAMILY not in (record.get("rejected_families") or []):
        failures.append("ledger_missing_c18_family")
    if C19_FAMILY not in (record.get("rejected_families") or []):
        failures.append("ledger_missing_c19_family")
    if record.get("c19_in_rejected_ledger") is not True:
        failures.append("c19_not_in_ledger")

    # C19 is REJECTED at the labels/neutrality gate (kept on record); NO active/open
    # candidate; next stage = AUTOMATION READINESS and NOT a new candidate.
    if record.get("active_candidate") is not None:
        failures.append("must_have_no_active_candidate")
    if record.get("open_candidate_gate") is not False:
        failures.append("open_candidate_gate_must_be_false")
    if record.get("active_candidate_detail") is not None:
        failures.append("active_candidate_detail_must_be_none")
    if record.get("last_rejected_candidate") != C19_CANDIDATE_ID:
        failures.append("last_rejected_not_c19")
    rej = record.get("last_rejected_candidate_detail") or {}
    if rej.get("family") != C19_FAMILY:
        failures.append("c19_family_mismatch")
    if rej.get("verdict") != C19_VERDICT:
        failures.append("c19_verdict_not_rejected_at_labels")
    if rej.get("rejected_at") != C19_REJECTED_AT_STAGE:
        failures.append("c19_not_rejected_at_labels_gate")
    if not rej.get("rejection_reason"):
        failures.append("c19_rejection_reason_missing")
    if not (isinstance(rej.get("labels_review_commit"), str)
            and len(rej["labels_review_commit"]) == 40):
        failures.append("c19_labels_review_commit_bad")
    if record.get("next_stage") != NEXT_STAGE:
        failures.append("next_stage_not_automation_readiness")
    if record.get("next_is_automation_readiness") is not True:
        failures.append("next_must_be_automation_readiness")
    if record.get("next_is_new_candidate") is not False:
        failures.append("next_must_not_be_new_candidate")
    if record.get("next_required_action") != AUTOMATION_READINESS_TOKEN:
        failures.append("next_action_not_automation_readiness")
    # C19 must appear in the candidate lane as REJECTED at the labels gate; C18 also
    # still rejected at fee-honest replay.
    lane_c19 = next((c for c in (record.get("candidate_lane") or [])
                     if c.get("candidate") == "C19"), None)
    if not lane_c19 or lane_c19.get("state") != STATE_REJECTED \
            or lane_c19.get("rejected_at") != C19_REJECTED_AT_STAGE:
        failures.append("c19_not_rejected_in_candidate_lane")
    lane_c18 = next((c for c in (record.get("candidate_lane") or [])
                     if c.get("candidate") == "C18"), None)
    if not lane_c18 or lane_c18.get("state") != STATE_REJECTED \
            or lane_c18.get("rejected_at") != C18_REJECTED_AT_STAGE:
        failures.append("c18_not_rejected_in_candidate_lane")

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
