"""SPARTA Crypto-D1 Candidate Research Lane -- STATUS / BUNDLE SURFACE v1
(PURE, RESEARCH ONLY).

A pure, stdlib-only, read-only status snapshot for the Crypto-D1 candidate-research
lane. It records -- deterministically, from already-committed contract state -- that
the C16 lifecycle is COMPLETE, that the canonical rejected ledger is C1-C19 (24
families), that C17/C18 are rejected at fee-honest replay and C19 is rejected at the
real-candle labels / neutrality gate (all kept on record), and that Candidate #20
(mechanically-neutral spot/perp basis + funding carry) is now the ACTIVE open
candidate at the family_proposal gate awaiting the human candidate-spec decision. It
is a map of state, not a controller.

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

# Canonical rejected ledger (reused, not redefined): C1-C20 = 25 families.
REJECTED_FAMILIES_C1_TO_C20 = tuple(_rep.REJECTED_FAMILIES_C1_TO_C20)
REJECTED_LEDGER_COUNT = len(REJECTED_FAMILIES_C1_TO_C20)            # 25

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

# Candidate #20 -- now CLOSED / REJECTED at the FEE-HONEST REPLAY stage (kept on
# record). It is the LAST rejected candidate. The structure was clean (704 entries,
# mechanical neutrality 100% by construction) but the entry/exit TIMING over-trades:
# 704 round-trips x 74 bps two-leg cost = 521% cost drag turned a +21.2% raw carry
# into net -74.5% (Sharpe -12.84), 2026 forward-OOS net -8.3% / 0% win, all four
# decisive gates failing and losing to the random/null always-on carry (+21.2%,
# Sharpe 1.09). The CARRY THESIS is real -- this rejects the TIMING/churn, not the
# carry. Frozen facts pinned to the pushed C20 chain commits.
C20_CANDIDATE_ID = "C20"
C20_FAMILY = "mechanically_neutral_spot_perp_basis_funding_carry"
C20_NAME = "mechanically_neutral_spot_perp_basis_funding_carry_v1"
C20_REJECTED_AT_STAGE = "fee_honest_replay"
C20_VERDICT = "C20_REJECTED_AT_FEE_HONEST_REPLAY"
C20_METHOD = "same_asset_long_spot_short_perp_basis_and_funding_carry"
C20_ASSETS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
C20_TIMEFRAME = "D1"
C20_LABEL = ("Mechanically-neutral spot/perp basis + funding carry — a SAME-ASSET "
             "long-spot / short-perp basis + funding carry on frozen public "
             "BTC/ETH/SOL (D1), mechanically neutral by construction")
C20_REJECTION_REASON = (
    "REJECTED at the fee-honest replay stage: structure clean (704 entries, mechanical "
    "neutrality 100% by construction, gross capped 1.0, one position per asset, >= "
    "5-bar spacing) but the entry/exit TIMING over-trades -- 704 round-trips x 74 bps "
    "two-leg cost = 521% cost drag turned a +21.2% raw carry into net -74.5% (Sharpe "
    "-12.84, Calmar -0.285, max DD -74.5%), 2026 forward-OOS net -8.3% / 0% win rate, "
    "all four decisive gates failing and losing badly to the random/null always-on "
    "neutral carry (+21.2%, Sharpe 1.09). The carry is real; the TIMING/churn is the "
    "killer. A low-turnover always-on carry is a SEPARATE future candidate only with "
    "explicit human approval.")
C20_REPLAY_REVIEW_COMMIT = "59de8da7deb3cc25f951702bce63155235313052"

# Candidate #21 -- the ACTIVE open candidate now at the CANDIDATE-SPEC review stage.
# The C21 family proposal (low-turnover same-asset spot/perp funding carry) was
# human-approved to advance into candidate-spec review; the candidate-spec contract is
# committed and FROZEN_FOR_HUMAN_REVIEW. Built ON the preserved C20 lesson (the
# always-on neutral carry is real; C20's high-turnover TIMING failed on churn cost) --
# but it is NOT a rescue/retune of C20: C20 stays rejected. Frozen facts pinned to the
# pushed C21 proposal + spec commits. The lane reports C21; it creates nothing, builds
# no detector, runs no labels/replay, and advances nothing.
C21_CANDIDATE_ID = "C21"
C21_FAMILY = "low_turnover_same_asset_spot_perp_funding_carry"
C21_NAME = "low_turnover_same_asset_spot_perp_funding_carry_v1"
C21_STAGE = "candidate_spec"
C21_STAGE_LABEL = "SPEC_FROZEN_FOR_HUMAN_REVIEW"
C21_VERDICT = "C21_SPEC_FROZEN_FOR_HUMAN_REVIEW"
C21_TIMEFRAME = "D1"
C21_UNIVERSE = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
C21_LABEL = ("Low-turnover same-asset spot/perp funding carry — harvest the SAME "
             "mechanically-neutral same-asset CARRY that C20's always-on benchmark "
             "proved real (+21.2%, Sharpe 1.09) but with LOW TURNOVER / HOLD "
             "PERSISTENCE (regime-gated, hysteresis, durable-breakdown exits) so the "
             "74 bps two-leg cost that killed C20 cannot dominate")
C21_SCOPE_NOTE = ("frozen public BTC/ETH/SOL spot+perp+funding D1 only; no new data "
                  "fetch; no XAUUSD / new instrument class; same-asset mechanical "
                  "neutrality is gate zero; LOW TURNOVER is a first-class design "
                  "constraint; carry source; NOT a rescue/retune of C20 (C20 stays "
                  "rejected); candidate spec FROZEN for human review -- detector / "
                  "labels / replay remain locked and unauthorized")
C21_PROPOSAL_COMMIT = "896a16eeee6ed1abd58b28fa75ebadaaff05d7bf"
C21_SPEC_COMMIT = "316ebce733be0ce0496edf44219c6fe717bb2afd"
C21_NEXT_GATE = "HUMAN_DECISION_C21_ADVANCE_TO_DETECTOR_SPEC_DRY_RUN_OR_REJECT"

# The candidate-research lane summary: C13-C20 all rejected (kept on record); C21 is
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
    {"candidate": "C17",
     "family": "risk_adjusted_portfolio_construction_vol_targeted_allocation",
     "state": STATE_REJECTED, "rejected_at": "fee_honest_replay"},
    {"candidate": "C18", "family": C18_FAMILY, "state": STATE_REJECTED,
     "rejected_at": C18_REJECTED_AT_STAGE},
    {"candidate": "C19", "family": C19_FAMILY, "state": STATE_REJECTED,
     "rejected_at": C19_REJECTED_AT_STAGE},
    {"candidate": "C20", "family": C20_FAMILY, "state": STATE_REJECTED,
     "rejected_at": C20_REJECTED_AT_STAGE},
    {"candidate": "C21", "family": C21_FAMILY, "state": STATE_ACTIVE_PROPOSAL,
     "stage": C21_STAGE, "verdict": C21_VERDICT},
)

# The PRIOR-stage automation-readiness token (stable; kept for provenance).
AUTOMATION_READINESS_TOKEN = "BUILD_AUTOMATION_READINESS_STEP_RESEARCH_ONLY"

# C21 is the ACTIVE open candidate at the candidate-spec review stage, so the CURRENT
# next human gate is the C21 detector-spec dry-run decision (an open candidate gate),
# NOT automation readiness. Detector / labels / replay stay locked until that gate.
NEXT_REQUIRED_ACTION = C21_NEXT_GATE
NEXT_STAGE = "c21_detector_spec_dry_run_decision"

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
    Records C16 complete, the C1-C20 (25) rejected ledger (C17/C18/C20 rejected at
    fee-honest replay and C19 at the labels/neutrality gate, all kept on record), and
    that Candidate #21 (low-turnover same-asset spot/perp funding carry) is now the
    ACTIVE open candidate at the CANDIDATE-SPEC review stage (spec frozen for human
    review) awaiting the human detector-spec-dry-run decision. Detector / labels /
    replay stay LOCKED. C20 stays rejected (not rescued/retuned). Executes nothing."""
    record: dict[str, Any] = {
        "version": LANE_STATUS_VERSION, "mode": LANE_STATUS_MODE, "lane": LANE,
        "is_pure_status_only": True,
        "label": (
            "Crypto-D1 candidate research lane status (READ-ONLY, RESEARCH ONLY). "
            "C16 lifecycle COMPLETE; rejected ledger C1-C20 (25 families); C20 stays "
            "CLOSED / REJECTED at fee-honest replay (kept on record, not rescued). "
            "Candidate #21 is now the ACTIVE open candidate at the CANDIDATE-SPEC "
            "review stage: low-turnover same-asset spot/perp funding carry (BTC/ETH/SOL "
            "D1, frozen public data) -- harvests the SAME carry C20's always-on "
            "benchmark proved real (+21.2%, Sharpe 1.09) but with LOW TURNOVER / hold "
            "persistence so the 74 bps two-leg cost that killed C20 cannot dominate. "
            "The candidate spec is FROZEN for human review; the next human gate is the "
            "detector-spec dry-run decision and detector / labels / replay stay LOCKED "
            "and unauthorized. Overnight/morning automation stays research-only and "
            "human-gated. Executes nothing."),
        # C16 completion (unchanged)
        "c16_lifecycle_complete": True,
        "c16_candidate_family": "cointegration_pairs_market_neutral",
        "c16_rejection_verdict": "REJECT_C16_AT_LABELS",
        "c16_lifecycle_gates": [dict(g) for g in C16_LIFECYCLE_GATES],
        "c16_in_rejected_ledger":
            "cointegration_pairs_market_neutral" in REJECTED_FAMILIES_C1_TO_C20,
        # rejected ledger -- now C1-C20 (25), C20 added
        "rejected_ledger_count": REJECTED_LEDGER_COUNT,
        "rejected_ledger_is_c1_to_c20": REJECTED_LEDGER_COUNT == 25,
        "rejected_families": list(REJECTED_FAMILIES_C1_TO_C20),
        "c18_in_rejected_ledger": C18_FAMILY in REJECTED_FAMILIES_C1_TO_C20,
        "c19_in_rejected_ledger": C19_FAMILY in REJECTED_FAMILIES_C1_TO_C20,
        "c20_in_rejected_ledger": C20_FAMILY in REJECTED_FAMILIES_C1_TO_C20,
        # candidate lane summary -- C21 is now the ACTIVE/open candidate
        "candidate_lane": [dict(c) for c in CANDIDATE_LANE],
        "active_candidate": C21_CANDIDATE_ID,
        "open_candidate_gate": True,
        "active_candidate_detail": {
            "candidate": C21_CANDIDATE_ID, "family": C21_FAMILY, "name": C21_NAME,
            "label": C21_LABEL, "verdict": C21_VERDICT,
            "stage": C21_STAGE, "stage_label": C21_STAGE_LABEL,
            "timeframe": C21_TIMEFRAME,
            "universe": list(C21_UNIVERSE),
            "scope_note": C21_SCOPE_NOTE,
            "is_market_neutral": True,
            "is_mechanically_neutral_same_asset": True,
            "is_low_turnover": True,
            "return_source_is_carry_not_timing": True,
            "is_rescue_or_retune_of_c20": False,
            "proposal_commit": C21_PROPOSAL_COMMIT,
            "spec_commit": C21_SPEC_COMMIT,
            "spec_frozen_for_human_review": True,
            "detector_labels_replay_locked": True,
            "next_action": C21_NEXT_GATE,
        },
        # C20 stays the last rejected candidate (provenance); C19 before it.
        "last_rejected_candidate": C20_CANDIDATE_ID,
        "last_rejected_candidate_detail": {
            "candidate": C20_CANDIDATE_ID, "family": C20_FAMILY,
            "name": C20_NAME, "label": C20_LABEL, "verdict": C20_VERDICT,
            "rejected_at": C20_REJECTED_AT_STAGE, "method": C20_METHOD,
            "assets": list(C20_ASSETS), "timeframe": C20_TIMEFRAME,
            "rejection_reason": C20_REJECTION_REASON,
            "is_market_neutral": True,
            "replay_review_commit": C20_REPLAY_REVIEW_COMMIT,
        },
        "prior_rejected_candidate": C20_CANDIDATE_ID,
        "prior_rejected_candidate_verdict": C20_VERDICT,
        # next stage = the C21 human candidate-spec decision (open gate), NOT
        # automation readiness and NOT a new candidate (no C22 here).
        "current_stage": "c21_candidate_spec_frozen_for_human_review",
        "next_stage": NEXT_STAGE,
        "next_is_automation_readiness": False,
        "automation_readiness_was_prior_stage": True,
        "next_strategy_memo_led_to_c17": True,
        "c21_promoted_from_proposal":
            "low_turnover_same_asset_spot_perp_funding_carry_v1_proposal",
        "c20_remains_rejected_not_rescued": True,
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
    """Pure morning-report-ready block: C16 complete, ledger C1-C20 (25), C20 rejected
    (kept on record, last rejected), and Candidate #21 now ACTIVE at the family_proposal
    gate awaiting the human candidate-spec decision. Read-only; executes nothing."""
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
        "active_candidate_is_low_turnover": det["is_low_turnover"],
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
    only, records C16 complete + C1-C20 (25) ledger (C18/C20 rejected at fee-honest
    replay and C19 at the labels/neutrality gate, kept on record), marks Candidate #21
    the ACTIVE open candidate at the CANDIDATE-SPEC review stage (low-turnover
    same-asset spot/perp funding carry, market-neutral, low-turnover, carry source, NOT
    a rescue/retune of C20; spec frozen for human review with detector/labels/replay
    locked) whose next gate is the human detector-spec-dry-run decision (NOT automation
    readiness and NOT a new candidate), keeps C20 as the last rejected candidate, keeps
    the automation path research-only with all downstream capability blocked/locked, and
    pins every capability flag False."""
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

    # rejected ledger C1-C20 (25), C20 added
    if record.get("rejected_ledger_count") != 25:
        failures.append("rejected_ledger_not_25")
    if record.get("rejected_ledger_is_c1_to_c20") is not True:
        failures.append("ledger_not_marked_c1_to_c20")
    if "cointegration_pairs_market_neutral" not in (
            record.get("rejected_families") or []):
        failures.append("ledger_missing_c16_family")
    if C18_FAMILY not in (record.get("rejected_families") or []):
        failures.append("ledger_missing_c18_family")
    if C19_FAMILY not in (record.get("rejected_families") or []):
        failures.append("ledger_missing_c19_family")
    if C20_FAMILY not in (record.get("rejected_families") or []):
        failures.append("ledger_missing_c20_family")
    if record.get("c20_in_rejected_ledger") is not True:
        failures.append("c20_not_in_ledger")

    # C21 is the ACTIVE open candidate at the CANDIDATE-SPEC review stage (spec frozen,
    # detector/labels/replay locked); C20 stays REJECTED (kept on record) as the last
    # rejected candidate / provenance.
    if record.get("active_candidate") != C21_CANDIDATE_ID:
        failures.append("c21_not_active")
    if record.get("open_candidate_gate") is not True:
        failures.append("open_candidate_gate_expected")
    det = record.get("active_candidate_detail") or {}
    if det.get("family") != C21_FAMILY:
        failures.append("c21_family_mismatch")
    if det.get("verdict") != C21_VERDICT:
        failures.append("c21_verdict_not_spec_frozen")
    if det.get("stage") != C21_STAGE:
        failures.append("c21_stage_not_candidate_spec")
    if det.get("stage_label") != C21_STAGE_LABEL:
        failures.append("c21_stage_label_mismatch")
    if det.get("timeframe") != C21_TIMEFRAME:
        failures.append("c21_timeframe_not_d1")
    if det.get("is_market_neutral") is not True:
        failures.append("c21_must_be_market_neutral")
    if det.get("is_mechanically_neutral_same_asset") is not True:
        failures.append("c21_must_be_mechanically_neutral_same_asset")
    if det.get("is_low_turnover") is not True:
        failures.append("c21_must_be_low_turnover")
    if det.get("return_source_is_carry_not_timing") is not True:
        failures.append("c21_return_source_not_carry")
    if det.get("is_rescue_or_retune_of_c20") is not False:
        failures.append("c21_must_not_be_c20_rescue")
    if det.get("spec_frozen_for_human_review") is not True:
        failures.append("c21_spec_not_frozen_for_review")
    if det.get("detector_labels_replay_locked") is not True:
        failures.append("c21_detector_labels_replay_not_locked")
    if list(det.get("universe") or []) != ["BTCUSDT", "ETHUSDT", "SOLUSDT"]:
        failures.append("c21_universe_not_btc_eth_sol")
    if not (isinstance(det.get("proposal_commit"), str)
            and len(det["proposal_commit"]) == 40):
        failures.append("c21_proposal_commit_bad")
    if not (isinstance(det.get("spec_commit"), str)
            and len(det["spec_commit"]) == 40):
        failures.append("c21_spec_commit_bad")
    if det.get("next_action") != C21_NEXT_GATE:
        failures.append("c21_next_gate_mismatch")
    if record.get("c20_remains_rejected_not_rescued") is not True:
        failures.append("c20_must_remain_rejected_not_rescued")
    # C20 kept on record as the last rejected candidate (provenance)
    if record.get("last_rejected_candidate") != C20_CANDIDATE_ID:
        failures.append("last_rejected_not_c20")
    rej = record.get("last_rejected_candidate_detail") or {}
    if rej.get("family") != C20_FAMILY:
        failures.append("c20_family_mismatch")
    if rej.get("verdict") != C20_VERDICT:
        failures.append("c20_verdict_not_rejected_at_replay")
    if rej.get("rejected_at") != C20_REJECTED_AT_STAGE:
        failures.append("c20_not_rejected_at_replay_gate")
    if not (isinstance(rej.get("replay_review_commit"), str)
            and len(rej["replay_review_commit"]) == 40):
        failures.append("c20_replay_review_commit_bad")
    # next stage = the C21 detector-spec dry-run decision (open gate), NOT automation
    # readiness and NOT a new candidate.
    if record.get("next_stage") != NEXT_STAGE:
        failures.append("next_stage_not_c21_detector_spec_dry_run_decision")
    if record.get("next_is_automation_readiness") is not False:
        failures.append("must_not_be_automation_readiness_while_c21_open")
    if record.get("next_is_new_candidate") is not False:
        failures.append("next_must_not_be_new_candidate")
    if record.get("next_required_action") != C21_NEXT_GATE:
        failures.append("next_action_not_c21_gate")
    # C21 must appear in the candidate lane as an active frozen proposal; C20 still
    # rejected at fee-honest replay; C19 at the labels gate; C18 at replay.
    lane_c21 = next((c for c in (record.get("candidate_lane") or [])
                     if c.get("candidate") == "C21"), None)
    if not lane_c21 or lane_c21.get("state") != STATE_ACTIVE_PROPOSAL:
        failures.append("c21_not_active_proposal_in_candidate_lane")
    lane_c20 = next((c for c in (record.get("candidate_lane") or [])
                     if c.get("candidate") == "C20"), None)
    if not lane_c20 or lane_c20.get("state") != STATE_REJECTED \
            or lane_c20.get("rejected_at") != C20_REJECTED_AT_STAGE:
        failures.append("c20_not_rejected_in_candidate_lane")
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
