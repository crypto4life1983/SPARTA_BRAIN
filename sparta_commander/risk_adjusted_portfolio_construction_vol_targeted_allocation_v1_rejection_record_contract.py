"""Candidate #17 -- risk_adjusted_portfolio_construction_vol_targeted_allocation_v1
-- FORMAL REJECTION / CLOSEOUT RECORD (PURE, RESEARCH ONLY).

Records the formal closeout of Candidate #17 as REJECTED AT THE FEE-HONEST REPLAY
STAGE (kept on record). Chain-gated on the FROZEN replay results review carrying
all_decisive_gates_pass == False and decisive_rejection_pressure == True.

It does NOTHING else: NO re-replay, NO PnL, NO re-detect, NO relabel, NO
optimization, NO re-parameterization, NO data fetch, NO writes, NO stage/commit/
push, and NO paper/live/broker/order surface. It only PRESERVES the honest replay
result and the research lesson, anchors the rejection to the committed replay-review
commit, and preserves the labels-review commit reference. Every capability flag is
pinned False with a full scope_locks set.

HONEST RESULT PRESERVED: the allocator cleared the labels structural gate but was
rejected at fee-honest replay. Over 2020-10-12..2026-06-08, net of 37 bps, it cut
max drawdown to -37.8% and held ~20% vol, yet did NOT beat SOL buy-and-hold (Sharpe
0.80 vs 1.08, Calmar 0.47 vs 0.83) or the equal-weight basket (Sharpe 0.80 vs 1.04)
on a RISK-ADJUSTED basis, and the 2026 forward-OOS edge did not hold.

LESSON: in a 2020-2026 crypto bull, vol-targeting + risk-parity de-risk away from
the biggest winner and LOWER risk-adjusted return; lower drawdown ALONE -- while
also lower Sharpe AND Calmar -- is not an edge over simply holding the basket.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.risk_adjusted_portfolio_construction_vol_targeted_allocation_v1_replay_results_review_contract as _r17  # noqa: E501

RJ17_SCHEMA_VERSION = 1
RJ17_MODE = "RESEARCH_ONLY"
RJ17_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = _r17.CANDIDATE_ID
CANDIDATE_FAMILY = _r17.CANDIDATE_FAMILY
CANDIDATE_NAME = _r17.CANDIDATE_NAME

VERDICT_RJ17_RECORDED = "REJECT_C17_AT_FEE_HONEST_REPLAY"
VERDICT_C17R_FROZEN = _r17.VERDICT_C17R_FROZEN
REJECTION_STATUS = "REJECTED_AT_FEE_HONEST_REPLAY_KEPT_ON_RECORD"
REJECTED_AT_STAGE = "fee_honest_replay"
REJECTED_FAMILY_NAME = "risk_adjusted_portfolio_construction_vol_targeted_allocation"

# pinned commits the rejection is anchored to (committed + pushed on origin)
REPLAY_REVIEW_COMMIT = "329b56ce87de23899aa5ceb510d66eb1959bd3bf"
LABELS_REVIEW_COMMIT = "2064849719e7b09077ce2e983c6ecff22a24cd63"

NEXT_REQUIRED_ACTION = (
    "NONE__C17_CLOSED__REJECTED_AT_FEE_HONEST_REPLAY__KEPT_ON_RECORD_AS_RISK_"
    "ADJUSTED_ALLOCATION_DOES_NOT_BEAT_THE_BASKET_RESEARCH_LESSON")

CONCLUSION = (
    "Vol-targeted / risk-parity allocation cut max drawdown materially and held its "
    "~20% vol target, but it did not beat SOL buy-and-hold or the equal-weight "
    "basket on a risk-adjusted basis (Sharpe / Calmar) and its 2026 forward-OOS "
    "edge did not hold; in a crypto bull, de-risking away from the biggest winner "
    "lowers risk-adjusted return, so lower drawdown alone is not a durable edge over "
    "simply holding the basket.")

# --- pinned honest metrics (from the frozen replay review) ------------------
STRATEGY_METRICS = dict(_r17.STRATEGY_METRICS)
BUY_AND_HOLD_METRICS = {a: dict(_r17.BUY_AND_HOLD_METRICS[a])
                        for a in _r17.ASSETS}
EQUAL_WEIGHT_BASKET_METRICS = dict(_r17.EQUAL_WEIGHT_BASKET_METRICS)
STRATEGY_FORWARD_OOS_METRICS = dict(_r17.STRATEGY_FORWARD_OOS_METRICS)

# --- pushed evidence chain (the gates committed + pushed on origin) ----------
PUSHED_EVIDENCE_CHAIN = (
    {"stage": "family_proposal",
     "commit": "1c3a4671cb3a0d238825dd7d7b7070a50f40d419"},
    {"stage": "candidate_spec",
     "commit": "8c22e085198c1a63595f8f49abaf01f6e7f71ea3"},
    {"stage": "detector_spec_and_synthetic_dry_run",
     "commit": "ff4168aa63bb377cc84b480948678843c32c7e0d"},
    {"stage": "real_candle_labels_review",
     "commit": "2064849719e7b09077ce2e983c6ecff22a24cd63"},
    {"stage": "fee_honest_replay_review",
     "commit": "329b56ce87de23899aa5ceb510d66eb1959bd3bf"},
)

# This rejected family extends the canonical rejected ledger to 22 (C1-C17). This
# bundle applies that bump in the REP / SARA / lane / integration ledgers.
LEDGER_BUMP = {
    "from_count": 21, "to_count": 22, "add_family": REJECTED_FAMILY_NAME,
    "applied_in_this_bundle": True,
}

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "re_replays", "computes_pnl", "re_detects",
    "relabels", "re_allocates", "runs_labels", "runs_backtest",
    "optimizes_parameters", "reparameterizes", "runs_robustness", "fetches_data",
    "reads_real_data", "mutates_data", "stages_data", "auto_commits", "auto_pushes",
    "applies_cost_model", "modifies_scheduler", "sends_notifications", "calls_api",
    "uses_network", "uses_credentials", "connects_broker", "connects_exchange",
    "uses_real_money", "places_orders", "contains_order_logic", "auto_trading",
    "paper_trading", "live_trading", "deploys_capital", "promotes_gate",
    "unlocks_downstream_gate", "skips_any_gate", "reactivates_candidate",
    "parks_as_active", "advances_without_human_approval", "claims_profitability",
    "claims_edge", "crosses_into_forbidden_gate",
)


def get_candidate_17_rejection_record_label() -> str:
    return (
        "Candidate #17 risk_adjusted_portfolio_construction_vol_targeted_"
        "allocation_v1 rejection record (READ-ONLY, RESEARCH ONLY). "
        "REJECTED_AT_FEE_HONEST_REPLAY_KEPT_ON_RECORD -- NOT AN ACTIVE CANDIDATE. "
        "Cut drawdown to -37.8% but did not beat SOL buy-and-hold (Sharpe 0.80 vs "
        "1.08) or the equal-weight basket (0.80 vs 1.04) risk-adjusted and the 2026 "
        "forward-OOS edge did not hold: lower drawdown alone is not an edge over "
        "holding the basket. NOT a profitability claim. NOT a paper/live-readiness "
        "claim.")


def get_candidate_17_rejection_record_next_action() -> str:
    return NEXT_REQUIRED_ACTION


def build_c17_rejection_record(repo_root: Any = ".",
                               tracked_paths: list | None = None) -> dict[str, Any]:
    """Assemble the frozen C17 rejection / closeout record. Pure; no I/O; chain-
    gated on the frozen decisive-rejection replay review."""
    replay = _r17.build_c17_replay_review(repo_root, tracked_paths)
    replay_valid = _r17.validate_c17_replay_review(replay)["valid"]

    blockers: list = []
    if not replay_valid:
        blockers.append("c17_replay_review_invalid")
    if replay.get("verdict") != VERDICT_C17R_FROZEN:
        blockers.append("c17_replay_review_not_frozen")
    if replay.get("all_decisive_gates_pass") is not False:
        blockers.append("replay_unexpectedly_passed")
    if replay.get("decisive_rejection_pressure") is not True:
        blockers.append("replay_not_decisively_rejected")

    s = STRATEGY_METRICS
    ew = EQUAL_WEIGHT_BASKET_METRICS
    bh_best_sharpe = max(BUY_AND_HOLD_METRICS[a]["sharpe"] for a in BUY_AND_HOLD_METRICS)

    record: dict[str, Any] = {
        "schema_version": RJ17_SCHEMA_VERSION, "mode": RJ17_MODE, "lane": RJ17_LANE,
        "label": get_candidate_17_rejection_record_label(),
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "candidate_name": CANDIDATE_NAME,
        "is_rejection_record_only": True,
        "blockers": blockers,
        "verdict": (VERDICT_RJ17_RECORDED if not blockers
                    else "C17_REJECTION_BLOCKED"),
        "rejection_status": REJECTION_STATUS,
        "rejected_at_stage": REJECTED_AT_STAGE,
        "is_active_candidate": False,
        "parked_as_active": False,
        "kept_on_record": True,
        "original_frozen_c17_result_unchanged": True,
        "added_to_rejected_family_ledger": True,
        # chain provenance + anchors
        "replay_review_verdict": replay.get("verdict"),
        "replay_review_valid": replay_valid,
        "replay_all_decisive_gates_pass": replay.get("all_decisive_gates_pass"),
        "replay_decisive_rejection_pressure":
            replay.get("decisive_rejection_pressure"),
        "anchored_to_replay_review_commit": REPLAY_REVIEW_COMMIT,
        "labels_review_commit": LABELS_REVIEW_COMMIT,
        # verbatim conclusion + lesson
        "conclusion": CONCLUSION,
        "kept_on_record_as": [
            "RISK MANAGEMENT WORKED: max drawdown cut to -37.8% (vs -77% to -96% "
            "buy-and-hold / -85% basket) at the ~20% vol target",
            "but the RISK-ADJUSTED comparison FAILED: lower Sharpe AND lower Calmar "
            "than both buy-and-hold and the equal-weight basket",
            "and the 2026 forward-OOS edge did not hold -- lower drawdown alone is "
            "not an edge over simply holding the basket",
        ],
        "rejection_reasons": [
            "DID NOT BEAT SOL BUY-AND-HOLD risk-adjusted: strategy Sharpe %.2f / "
            "Calmar %.2f vs %.2f / %.2f" % (
                s["sharpe"], s["calmar"],
                BUY_AND_HOLD_METRICS["SOLUSD"]["sharpe"],
                BUY_AND_HOLD_METRICS["SOLUSD"]["calmar"]),
            "DID NOT BEAT THE EQUAL-WEIGHT BASKET risk-adjusted: strategy Sharpe "
            "%.2f / Calmar %.2f vs %.2f / %.2f" % (
                s["sharpe"], s["calmar"], ew["sharpe"], ew["calmar"]),
            "2026 FORWARD-OOS edge did not hold (strategy Sharpe %.2f)"
            % STRATEGY_FORWARD_OOS_METRICS["sharpe"],
            "lower drawdown ALONE is not an edge; raw return alone is not "
            "sufficient",
        ],
        "evidence_headline": {
            "did_not_beat_buy_and_hold_risk_adjusted": s["sharpe"] < bh_best_sharpe,
            "did_not_beat_equal_weight_risk_adjusted": s["sharpe"] < ew["sharpe"]
            and s["calmar"] < ew["calmar"],
            "forward_oos_edge_failed":
                STRATEGY_FORWARD_OOS_METRICS["sharpe"] < 0,
            "only_win_is_lower_drawdown": s["max_drawdown"] > ew["max_drawdown"],
            "cost_model_applied_37bps": True,
        },
        # pinned numbers
        "strategy_metrics": dict(STRATEGY_METRICS),
        "buy_and_hold_metrics": {a: dict(BUY_AND_HOLD_METRICS[a])
                                 for a in BUY_AND_HOLD_METRICS},
        "equal_weight_basket_metrics": dict(EQUAL_WEIGHT_BASKET_METRICS),
        "strategy_forward_oos_metrics": dict(STRATEGY_FORWARD_OOS_METRICS),
        # evidence chain + ledger bump
        "pushed_evidence_chain": [dict(e) for e in PUSHED_EVIDENCE_CHAIN],
        "rejected_family_name": REJECTED_FAMILY_NAME,
        "ledger_bump": dict(LEDGER_BUMP),
        "raw_return_alone_is_not_sufficient": True,
        "claim_locks": [
            "no_profitability_claim", "kept_on_record_not_active_candidate",
            "not_parked_as_active", "risk_adjusted_failure_disclosed",
            "forward_oos_failure_disclosed", "lower_drawdown_alone_not_an_edge",
            "conclusion_recorded_precisely",
        ],
        "human_review_required": True,
        "current_loop_stage": "rejection_record",
        "next_required_action": NEXT_REQUIRED_ACTION,
        # gates locked
        "replay_gate_locked": True, "robustness_gate_locked": True,
        "promote_gate_locked": True, "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True, "live_gate_locked": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_re_replay": True, "no_pnl": True, "no_re_detect": True,
        "no_relabel": True, "no_re_allocate": True, "no_optimization": True,
        "no_reparameterization": True, "no_robustness_run": True,
        "no_data_fetch": True, "no_data_mutation": True, "no_cost_recompute": True,
        "no_reactivation": True, "no_parking_as_active": True, "no_stage": True,
        "no_commit": True, "no_push": True, "no_auto_commit": True,
        "no_auto_push": True, "no_broker": True, "no_credentials": True,
        "no_order_logic": True, "no_auto_trading": True, "no_paper_trading": True,
        "no_live_trading": True, "no_gate_skip": True,
        "no_downstream_gate_unlock": True, "no_profitability_claim": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_c17_rejection_record(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the record is research-only,
    rejection-record-only, chain-gated on the frozen decisive-rejection replay
    review, keeps the candidate not-active / not-parked / kept-on-record, records
    REJECT_C17_AT_FEE_HONEST_REPLAY anchored to the pushed replay-review commit,
    preserves the verbatim conclusion + the risk-adjusted failure facts (none can be
    flipped), cites the 5 pushed gate commits, and pins every capability flag
    False."""
    failures: list = []
    if record.get("mode") != RJ17_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_rejection_record_only") is not True:
        failures.append("not_rejection_record_only")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("verdict") != VERDICT_RJ17_RECORDED:
        failures.append("verdict_not_reject_c17_at_replay")
    if record.get("rejection_status") != REJECTION_STATUS:
        failures.append("status_not_rejected_at_replay")
    if record.get("rejected_at_stage") != REJECTED_AT_STAGE:
        failures.append("rejected_stage_not_fee_honest_replay")

    # not active / not parked / kept on record
    if record.get("is_active_candidate") is not False:
        failures.append("must_not_be_active")
    if record.get("parked_as_active") is not False:
        failures.append("must_not_be_parked")
    if record.get("kept_on_record") is not True:
        failures.append("must_be_kept_on_record")

    # chain gate on the decisive-rejection replay review
    if record.get("replay_review_verdict") != VERDICT_C17R_FROZEN:
        failures.append("replay_review_not_frozen")
    if record.get("replay_review_valid") is not True:
        failures.append("replay_review_not_valid")
    if record.get("replay_all_decisive_gates_pass") is not False:
        failures.append("replay_unexpectedly_passed")
    if record.get("replay_decisive_rejection_pressure") is not True:
        failures.append("replay_not_decisively_rejected")

    # anchored to the pushed commits
    if record.get("anchored_to_replay_review_commit") != REPLAY_REVIEW_COMMIT:
        failures.append("replay_anchor_commit_tampered")
    if record.get("labels_review_commit") != LABELS_REVIEW_COMMIT:
        failures.append("labels_commit_reference_tampered")

    # verbatim conclusion
    if record.get("conclusion") != CONCLUSION:
        failures.append("conclusion_tampered")

    # preserved decisive failure facts -- cannot be flipped
    eh = record.get("evidence_headline") or {}
    for k in ("did_not_beat_buy_and_hold_risk_adjusted",
              "did_not_beat_equal_weight_risk_adjusted",
              "forward_oos_edge_failed", "only_win_is_lower_drawdown",
              "cost_model_applied_37bps"):
        if eh.get(k) is not True:
            failures.append("rejection_finding_cleared_%s" % k)
    if record.get("raw_return_alone_is_not_sufficient") is not True:
        failures.append("raw_return_sufficiency_flag_wrong")
    if len(record.get("rejection_reasons") or []) < 3:
        failures.append("rejection_reasons_missing")

    # pinned metrics intact + genuinely a rejection
    s = record.get("strategy_metrics") or {}
    ew = record.get("equal_weight_basket_metrics") or {}
    if s.get("sharpe") != STRATEGY_METRICS["sharpe"]:
        failures.append("strategy_sharpe_tampered")
    if s.get("sharpe", 9) >= ew.get("sharpe", 0) and s.get("calmar", 9) >= ew.get(
            "calmar", 0):
        failures.append("metrics_inconsistent_with_rejection")

    # pushed evidence chain: 5 gate commits, each a 40-char sha
    chain = record.get("pushed_evidence_chain") or []
    stages = {e.get("stage"): e.get("commit") for e in chain}
    for required in ("family_proposal", "candidate_spec",
                     "detector_spec_and_synthetic_dry_run",
                     "real_candle_labels_review", "fee_honest_replay_review"):
        if required not in stages:
            failures.append("pushed_chain_missing_%s" % required)
        elif not (isinstance(stages[required], str)
                  and len(stages[required]) == 40):
            failures.append("pushed_chain_bad_commit_%s" % required)

    # ledger bump applied in this bundle (21 -> 22)
    lb = record.get("ledger_bump") or {}
    if lb.get("to_count") != 22 or lb.get("from_count") != 21:
        failures.append("ledger_bump_counts_wrong")
    if lb.get("add_family") != REJECTED_FAMILY_NAME:
        failures.append("ledger_bump_family_wrong")

    # gates locked
    for gate in ("replay_gate_locked", "robustness_gate_locked",
                 "promote_gate_locked", "paper_trading_gate_locked",
                 "micro_live_gate_locked", "live_gate_locked"):
        if record.get(gate) is not True:
            failures.append("gate_unlocked_%s" % gate)

    locks = record.get("scope_locks") or {}
    for key in ("no_re_replay", "no_pnl", "no_re_detect", "no_relabel",
                "no_re_allocate", "no_optimization", "no_reparameterization",
                "no_reactivation", "no_commit", "no_push", "no_broker",
                "no_order_logic", "no_auto_trading", "no_paper_trading",
                "no_live_trading", "no_gate_skip"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
