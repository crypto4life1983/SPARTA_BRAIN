"""SPARTA Crypto-D1 Candidate Research Lane -- STATUS / BUNDLE SURFACE v1
(PURE, RESEARCH ONLY).

A pure, stdlib-only, read-only status snapshot for the Crypto-D1 candidate-research
lane. It records -- deterministically, from already-committed contract state -- that
the C16 lifecycle is COMPLETE, that the canonical rejected ledger is C1-C18 (23
families), that C17 and C18 are both rejected/closed at fee-honest replay (kept on
record), and that Candidate #19 (OOS-validated beta-neutral cross-sectional relative
value) is now the ACTIVE open candidate at the family_proposal gate awaiting the
human candidate-spec decision. It is a map of state, not a controller.

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

# Canonical rejected ledger (reused, not redefined): C1-C18 = 23 families
# (C17 risk-adjusted portfolio construction AND C18 H4 trend-following were both
# rejected at the fee-honest replay stage).
REJECTED_FAMILIES_C1_TO_C18 = tuple(_rep.REJECTED_FAMILIES_C1_TO_C18)
REJECTED_LEDGER_COUNT = len(REJECTED_FAMILIES_C1_TO_C18)            # 23

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

# Candidate #17 -- CLOSED / REJECTED at the fee-honest replay stage (kept on
# record). Frozen facts pinned to the pushed C17 chain commits. Kept for provenance.
C17_CANDIDATE_ID = "C17"
C17_FAMILY = "risk_adjusted_portfolio_construction_vol_targeted_allocation"
C17_REJECTED_AT_STAGE = "fee_honest_replay"
C17_VERDICT = "C17_REJECTED_AT_FEE_HONEST_REPLAY"

# Candidate #18 -- CLOSED / REJECTED at the fee-honest replay stage (kept on record).
# It is the LAST rejected candidate (provenance). Frozen facts pinned to the pushed
# C18 chain commits.
C18_CANDIDATE_ID = "C18"
C18_FAMILY = "h4_trend_following_market_structure"
C18_NAME = "h4_trend_following_market_structure_v1"
C18_REJECTED_AT_STAGE = "fee_honest_replay"
C18_VERDICT = "C18_REJECTED_AT_FEE_HONEST_REPLAY"
C18_METHOD = "h4_market_structure_trend_following_add_to_winners_no_indicator"
C18_ASSETS = ("BTCUSD",)
C18_TIMEFRAME = "H4"
C18_LABEL = ("H4 market-structure trend-following — no-indicator, patience / "
             "low-frequency, add-to-winners (objective testable approximation of an "
             "observed profitable trader; NOT their exact private system)")
C18_REJECTION_REASON = (
    "REJECTED at fee-honest replay: made +95.4% net but FAILED the BTC "
    "buy-and-hold risk-adjusted comparison (Sharpe 0.52 vs 0.93, Calmar 0.25 vs "
    "0.60); its only structural win was a lower drawdown (-38.2% vs -77.0%), which "
    "alone is not an edge over simply holding BTC. The 2026 forward-OOS edge did "
    "not hold (Sharpe -2.27 vs -1.47); win rate 15.2%, total R -101.4, avg R "
    "-0.26 -- structural stops bled faster than pyramided winners recovered. This "
    "rejects the OBJECTIVE C18 approximation, NOT the observed trader's exact "
    "private system.")
C18_LABELS_REVIEW_COMMIT = "0e1377284ea865ac33a7988c61b5da7dc2417230"
C18_REPLAY_REVIEW_COMMIT = "e22510521c9d954b36e52200c1dbcee498be5f82"

# Candidate #19 -- the ACTIVE open candidate at the family_proposal gate. Promoted
# from the committed C19 research-direction recommendation. Frozen facts pinned to
# the pushed C19 proposal commit. The lane reports C19; it creates nothing and
# advances nothing. (Hardcoded -- the lane imports no candidate contract.)
C19_CANDIDATE_ID = "C19"
C19_FAMILY = "oos_validated_beta_neutral_cross_sectional_relative_value"
C19_NAME = "oos_validated_beta_neutral_cross_sectional_relative_value_v1"
C19_STAGE = "family_proposal"
C19_STAGE_LABEL = "PROPOSAL_FROZEN_FOR_HUMAN_REVIEW"
C19_VERDICT = "C19_PROPOSAL_FROZEN_FOR_HUMAN_REVIEW"
C19_TIMEFRAME = "D1"
C19_UNIVERSE = ("BTCUSD", "ETHUSD", "SOLUSD")
C19_LABEL = ("OOS-validated beta-neutral cross-sectional relative value — a "
             "continuous dollar+return-beta-neutral residual among BTC/ETH/SOL (D1, "
             "cached), market-neutral, with OOS neutrality validation as gate zero "
             "before any trading logic")
C19_SCOPE_NOTE = ("cached BTC/ETH/SOL D1 spot only; no new data fetch; no XAUUSD / "
                  "new instrument class; OOS neutrality validation is gate zero; "
                  "carries no buy-and-hold beta")
C19_PROPOSAL_COMMIT = "d7d7ac6c33712a9a46888bfc3338c79df299be41"
C19_NEXT_GATE = "HUMAN_DECISION_C19_ADVANCE_TO_CANDIDATE_SPEC_OR_REJECT"

# The candidate-research lane summary: C13-C18 all rejected (kept on record); C19 is
# now the ACTIVE open candidate at the family_proposal gate.
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
    {"candidate": "C18", "family": C18_FAMILY, "state": STATE_REJECTED,
     "rejected_at": C18_REJECTED_AT_STAGE},
    {"candidate": "C19", "family": C19_FAMILY, "state": STATE_ACTIVE_PROPOSAL,
     "stage": C19_STAGE, "verdict": C19_VERDICT},
)

# The PRIOR-stage automation-readiness token (stable; kept for provenance and for
# the automation-readiness prep/memo artifacts that belong to that stage).
AUTOMATION_READINESS_TOKEN = "BUILD_AUTOMATION_READINESS_STEP_RESEARCH_ONLY"

# C19 is the ACTIVE open candidate, so the CURRENT next stage is the C19 human spec
# decision (an open candidate gate), NOT automation readiness.
NEXT_REQUIRED_ACTION = C19_NEXT_GATE
NEXT_STAGE = "c19_candidate_spec_decision"

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
    Records C16 complete, the C1-C18 (23) rejected ledger (C17 and C18 rejected at
    replay, kept on record), and that Candidate #19 (OOS-validated beta-neutral
    cross-sectional relative value) is now the ACTIVE open candidate at the
    family_proposal gate awaiting the human candidate-spec decision. Executes
    nothing."""
    record: dict[str, Any] = {
        "version": LANE_STATUS_VERSION, "mode": LANE_STATUS_MODE, "lane": LANE,
        "is_pure_status_only": True,
        "label": (
            "Crypto-D1 candidate research lane status (READ-ONLY, RESEARCH ONLY). "
            "C16 lifecycle COMPLETE; rejected ledger C1-C18 (23 families); C17 and "
            "C18 closed / rejected at fee-honest replay (kept on record). Candidate "
            "#19 is now the ACTIVE open candidate at the family_proposal gate: "
            "OOS-validated beta-neutral cross-sectional relative value (BTC/ETH/SOL "
            "D1, cached) -- a market-neutral edge with OOS neutrality validation as "
            "gate zero -- awaiting the human candidate-spec decision. Overnight/"
            "morning automation stays research-only and human-gated. Executes "
            "nothing."),
        # C16 completion (unchanged)
        "c16_lifecycle_complete": True,
        "c16_candidate_family": "cointegration_pairs_market_neutral",
        "c16_rejection_verdict": "REJECT_C16_AT_LABELS",
        "c16_lifecycle_gates": [dict(g) for g in C16_LIFECYCLE_GATES],
        "c16_in_rejected_ledger":
            "cointegration_pairs_market_neutral" in REJECTED_FAMILIES_C1_TO_C18,
        # rejected ledger -- C1-C18 (23), UNCHANGED (C19 is a NEW active candidate)
        "rejected_ledger_count": REJECTED_LEDGER_COUNT,
        "rejected_ledger_is_c1_to_c18": REJECTED_LEDGER_COUNT == 23,
        "rejected_families": list(REJECTED_FAMILIES_C1_TO_C18),
        "c17_in_rejected_ledger": C17_FAMILY in REJECTED_FAMILIES_C1_TO_C18,
        "c18_in_rejected_ledger": C18_FAMILY in REJECTED_FAMILIES_C1_TO_C18,
        # candidate lane summary -- C19 is now the ACTIVE/open candidate
        "candidate_lane": [dict(c) for c in CANDIDATE_LANE],
        "active_candidate": C19_CANDIDATE_ID,
        "open_candidate_gate": True,
        "active_candidate_detail": {
            "candidate": C19_CANDIDATE_ID, "family": C19_FAMILY, "name": C19_NAME,
            "label": C19_LABEL, "verdict": C19_VERDICT,
            "stage": C19_STAGE, "stage_label": C19_STAGE_LABEL,
            "timeframe": C19_TIMEFRAME,
            "universe": list(C19_UNIVERSE),
            "scope_note": C19_SCOPE_NOTE,
            "is_market_neutral": True,
            "oos_neutrality_validation_is_gate_zero": True,
            "proposal_commit": C19_PROPOSAL_COMMIT,
            "next_action": C19_NEXT_GATE,
        },
        # C18 stays visible as the last rejected candidate (provenance)
        "last_rejected_candidate": C18_CANDIDATE_ID,
        "last_rejected_candidate_detail": {
            "candidate": C18_CANDIDATE_ID, "family": C18_FAMILY,
            "name": C18_NAME, "label": C18_LABEL, "verdict": C18_VERDICT,
            "rejected_at": C18_REJECTED_AT_STAGE, "method": C18_METHOD,
            "assets": list(C18_ASSETS), "timeframe": C18_TIMEFRAME,
            "rejection_reason": C18_REJECTION_REASON,
            "is_objective_approximation_not_exact_system": True,
            "labels_review_commit": C18_LABELS_REVIEW_COMMIT,
            "replay_review_commit": C18_REPLAY_REVIEW_COMMIT,
        },
        "prior_rejected_candidate": C17_CANDIDATE_ID,
        "prior_rejected_candidate_verdict": C17_VERDICT,
        # next stage = the C19 human candidate-spec decision (open gate), NOT
        # automation readiness and NOT a new candidate (no C20 here).
        "current_stage": "c19_family_proposal_frozen_for_human_review",
        "next_stage": NEXT_STAGE,
        "next_is_automation_readiness": False,
        "automation_readiness_was_prior_stage": True,
        "next_strategy_memo_led_to_c17": True,
        "c19_promoted_from_recommendation": "c19_research_direction_recommendation_v1",
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
    """Pure morning-report-ready block: C16 complete, ledger C1-C18 (23), C18
    rejected (kept on record, last rejected), and Candidate #19 now ACTIVE at the
    family_proposal gate awaiting the human candidate-spec decision. Read-only;
    executes nothing."""
    s = get_lane_status()
    rej = s["last_rejected_candidate_detail"]
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
        "active_candidate_timeframe": det["timeframe"],
        "active_candidate_scope_note": det["scope_note"],
        "active_candidate_is_market_neutral": det["is_market_neutral"],
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
    only, records C16 complete + C1-C18 (23) ledger (C17 and C18 rejected at replay,
    kept on record), marks Candidate #19 the ACTIVE open candidate at the
    family_proposal gate (OOS-validated beta-neutral cross-sectional relative value,
    market-neutral) whose next gate is the human candidate-spec decision (NOT
    automation readiness and NOT a new candidate), keeps C18 as the last rejected
    candidate, keeps the automation path research-only with all downstream capability
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

    # rejected ledger C1-C18 (23)
    if record.get("rejected_ledger_count") != 23:
        failures.append("rejected_ledger_not_23")
    if record.get("rejected_ledger_is_c1_to_c18") is not True:
        failures.append("ledger_not_marked_c1_to_c18")
    if "cointegration_pairs_market_neutral" not in (
            record.get("rejected_families") or []):
        failures.append("ledger_missing_c16_family")
    if C17_FAMILY not in (record.get("rejected_families") or []):
        failures.append("ledger_missing_c17_family")
    if C18_FAMILY not in (record.get("rejected_families") or []):
        failures.append("ledger_missing_c18_family")
    if record.get("c18_in_rejected_ledger") is not True:
        failures.append("c18_not_in_ledger")

    # C19 is the ACTIVE open candidate at the family_proposal gate; C18 stays
    # REJECTED (kept on record) as the last rejected candidate / provenance.
    if record.get("active_candidate") != C19_CANDIDATE_ID:
        failures.append("c19_not_active")
    if record.get("open_candidate_gate") is not True:
        failures.append("open_candidate_gate_expected")
    det = record.get("active_candidate_detail") or {}
    if det.get("family") != C19_FAMILY:
        failures.append("c19_family_mismatch")
    if det.get("verdict") != C19_VERDICT:
        failures.append("c19_verdict_not_proposal_frozen")
    if det.get("stage") != C19_STAGE:
        failures.append("c19_stage_not_family_proposal")
    if det.get("stage_label") != C19_STAGE_LABEL:
        failures.append("c19_stage_label_mismatch")
    if det.get("timeframe") != C19_TIMEFRAME:
        failures.append("c19_timeframe_not_d1")
    if det.get("is_market_neutral") is not True:
        failures.append("c19_must_be_market_neutral")
    if det.get("oos_neutrality_validation_is_gate_zero") is not True:
        failures.append("c19_oos_neutrality_not_gate_zero")
    if list(det.get("universe") or []) != ["BTCUSD", "ETHUSD", "SOLUSD"]:
        failures.append("c19_universe_not_btc_eth_sol")
    if not (isinstance(det.get("proposal_commit"), str)
            and len(det["proposal_commit"]) == 40):
        failures.append("c19_proposal_commit_bad")
    if det.get("next_action") != C19_NEXT_GATE:
        failures.append("c19_next_gate_mismatch")
    # C18 kept on record as the last rejected candidate (provenance)
    if record.get("last_rejected_candidate") != C18_CANDIDATE_ID:
        failures.append("last_rejected_not_c18")
    rej = record.get("last_rejected_candidate_detail") or {}
    if rej.get("family") != C18_FAMILY:
        failures.append("c18_family_mismatch")
    if rej.get("verdict") != C18_VERDICT:
        failures.append("c18_verdict_not_rejected_at_replay")
    if rej.get("rejected_at") != C18_REJECTED_AT_STAGE:
        failures.append("c18_not_rejected_at_fee_honest_replay")
    if not (isinstance(rej.get("replay_review_commit"), str)
            and len(rej["replay_review_commit"]) == 40):
        failures.append("c18_replay_review_commit_bad")
    # next stage = the C19 candidate-spec decision (open gate), NOT automation
    # readiness and NOT a new candidate.
    if record.get("next_stage") != NEXT_STAGE:
        failures.append("next_stage_not_c19_candidate_spec_decision")
    if record.get("next_is_automation_readiness") is not False:
        failures.append("must_not_be_automation_readiness_while_c19_open")
    if record.get("next_is_new_candidate") is not False:
        failures.append("next_must_not_be_new_candidate")
    if record.get("next_required_action") != C19_NEXT_GATE:
        failures.append("next_action_not_c19_gate")
    # C19 must appear in the candidate lane as an active frozen proposal; C18 still
    # rejected at fee-honest replay.
    lane_c19 = next((c for c in (record.get("candidate_lane") or [])
                     if c.get("candidate") == "C19"), None)
    if not lane_c19 or lane_c19.get("state") != STATE_ACTIVE_PROPOSAL:
        failures.append("c19_not_active_proposal_in_candidate_lane")
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
