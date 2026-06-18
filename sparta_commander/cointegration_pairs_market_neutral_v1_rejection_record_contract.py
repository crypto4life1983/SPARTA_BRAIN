"""Candidate #16 -- cointegration_pairs_market_neutral_v1 -- FORMAL REJECTION /
CLOSEOUT RECORD (PURE, RESEARCH ONLY).

Records the formal closeout of Candidate #16 as REJECTED AT THE LABELS STAGE
(kept on record) -- a structural rejection BEFORE any replay. Chain-gated on the
FROZEN real-candle labels review carrying structural_rejection_pressure == True
and structural_sample_size_passed == False.

It does NOTHING else: NO replay (none was ever run), NO PnL, NO re-detect, NO
relabel, NO optimization, NO data fetch, NO writes, NO stage/commit/push, and NO
paper/live/broker/order surface. It only PRESERVES the honest structural result
and the research lesson. Every capability flag is pinned False with a full
scope_locks set.

HONEST RESULT PRESERVED: the labels-stage structural gate FAILED on two
independent grounds -- (1) only 43 labels (< 100), every pair below 20 (ETHBTC 17
/ SOLBTC 15 / SOLETH 11) and the chop regime below 20 (bull 18 / bear 21 / chop 4),
with forward-OOS 2026 populated (9) but insufficient; and (2) the observed net beta
(2.82) blows past the 0.10 market-neutral cap. No replay and no PnL were run or
allowed.

LESSON: market-neutrality avoided the carry trap that rejected C14 and C15, but
cointegration in crypto is too INTERMITTENT to generate enough valid pair-trade
entries, AND a level-OLS hedge ratio is NOT return-beta-neutral out of sample --
so a market-neutral cointegration-pairs program is not structurally supportable on
daily crypto.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.cointegration_pairs_market_neutral_v1_real_candle_labels_review_contract as _l16  # noqa: E501

RJ16_SCHEMA_VERSION = 1
RJ16_MODE = "RESEARCH_ONLY"
RJ16_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = _l16.CANDIDATE_ID
CANDIDATE_FAMILY = _l16.CANDIDATE_FAMILY
CANDIDATE_NAME = _l16.CANDIDATE_NAME

VERDICT_RJ16_RECORDED = "REJECT_C16_AT_LABELS"
VERDICT_C16L_FROZEN = _l16.VERDICT_C16L_FROZEN
REJECTION_STATUS = "REJECTED_AT_LABELS_KEPT_ON_RECORD"
REJECTED_AT_STAGE = "real_candle_labels"

NEXT_REQUIRED_ACTION = (
    "NONE__C16_CLOSED__REJECTED_AT_LABELS__KEPT_ON_RECORD_AS_INTERMITTENT_"
    "COINTEGRATION_AND_NON_NEUTRAL_HEDGE_RESEARCH_LESSON")

CONCLUSION = (
    "Market-neutrality avoided the carry trap that rejected C14 and C15, but "
    "cointegration in crypto is too intermittent to generate enough valid "
    "pair-trade entries, and a level-OLS hedge ratio is not return-beta-neutral "
    "out of sample, so a market-neutral cointegration-pairs program is not "
    "structurally supportable on daily crypto.")

# --- pinned honest aggregates (from the frozen labels review) ---------------
ACCEPTED_LABEL_COUNT = _l16.ACCEPTED_LABEL_COUNT          # 43
PER_PAIR = dict(_l16.PER_PAIR)                            # ETHBTC 17/SOLBTC 15/SOLETH 11
PER_REGIME = dict(_l16.PER_REGIME)                        # bull 18/bear 21/chop 4
FORWARD_OOS_LABEL_COUNT = _l16.FORWARD_OOS_LABEL_COUNT    # 9
MAX_ABS_NET_BETA_OBSERVED = _l16.MAX_ABS_NET_BETA_OBSERVED  # 2.824495
MAX_ABS_NET_BETA_CAP = _l16.MAX_ABS_NET_BETA_CAP          # 0.10
MIN_LABELS_TOTAL = _l16.MIN_LABELS_TOTAL                  # 100
MIN_PER_PAIR = _l16.MIN_PER_PAIR                          # 20
MIN_PER_REGIME = _l16.MIN_PER_REGIME                      # 20

# --- pushed evidence chain (the gates committed + pushed on origin) ----------
PUSHED_EVIDENCE_CHAIN = (
    {"stage": "family_proposal",
     "commit": "38ccce6296e93b92dffcfa4a46d02349ebe40e76"},
    {"stage": "candidate_spec",
     "commit": "9c2b39cc64e156167d28621403e1b5892e2a308a"},
    {"stage": "detector_spec_and_synthetic_dry_run",
     "commit": "0c5f27a0e749f0842b99874b95d37f38f88a9887"},
    {"stage": "real_candle_labels_review",
     "commit": "ae16daf0a8c139cee1f6a1bb177ca99be027d198"},
)

# This rejected family would extend the canonical rejected ledger to 21 (C1-C16).
# Applying that bump to the REP / SARA / integration ledgers is a SEPARATE token.
REJECTED_FAMILY_NAME = "cointegration_pairs_market_neutral"
PROPOSED_LEDGER_BUMP = {
    "from_count": 20, "to_count": 21, "add_family": REJECTED_FAMILY_NAME,
    "applied_here": False,
    "requires_separate_token": "UPDATE_REJECTED_LEDGERS_ADD_C16",
}

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "runs_replay", "computes_pnl", "re_detects",
    "relabels", "runs_labels", "runs_backtest", "optimizes_parameters",
    "runs_robustness", "runs_portfolio_compute", "fetches_data", "reads_real_data",
    "mutates_data", "stages_data", "auto_commits", "auto_pushes",
    "applies_cost_model", "modifies_scheduler", "sends_notifications", "calls_api",
    "uses_network", "uses_credentials", "connects_broker", "connects_exchange",
    "uses_real_money", "places_orders", "contains_order_logic", "paper_trading",
    "live_trading", "deploys_capital", "promotes_gate", "unlocks_downstream_gate",
    "skips_any_gate", "reactivates_candidate", "parks_as_active",
    "advances_without_human_approval", "claims_profitability", "claims_edge",
    "claims_market_neutral_holds", "crosses_into_forbidden_gate",
)


def get_candidate_16_rejection_record_label() -> str:
    return (
        "Candidate #16 cointegration_pairs_market_neutral_v1 rejection record "
        "(READ-ONLY, RESEARCH ONLY). REJECTED_AT_LABELS_KEPT_ON_RECORD -- a "
        "structural rejection BEFORE replay (no replay/PnL run). NOT AN ACTIVE "
        "CANDIDATE. Too few cointegrated entries (43 < 100) and a non-neutral "
        "hedge (net beta 2.82 > 0.10): a market-neutral cointegration-pairs program "
        "is not structurally supportable on daily crypto. NOT a profitability "
        "claim. NOT a paper/live-readiness claim.")


def get_candidate_16_rejection_record_next_action() -> str:
    return NEXT_REQUIRED_ACTION


def build_c16_rejection_record(repo_root: Any = ".",
                               tracked_paths: list | None = None) -> dict[str, Any]:
    """Assemble the frozen C16 rejection / closeout record. Pure; no I/O; chain-
    gated on the frozen structural-rejection labels review. No replay was run."""
    labels = _l16.build_c16_labels_review(repo_root, tracked_paths)
    labels_valid = _l16.validate_c16_labels_review(labels)["valid"]

    blockers: list = []
    if not labels_valid:
        blockers.append("c16_labels_review_invalid")
    if labels.get("verdict") != VERDICT_C16L_FROZEN:
        blockers.append("c16_labels_review_not_frozen")
    if labels.get("structural_rejection_pressure") is not True:
        blockers.append("labels_not_structurally_rejected")
    if labels.get("structural_sample_size_passed") is not False:
        blockers.append("labels_unexpectedly_passed")

    record: dict[str, Any] = {
        "schema_version": RJ16_SCHEMA_VERSION, "mode": RJ16_MODE, "lane": RJ16_LANE,
        "label": get_candidate_16_rejection_record_label(),
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "candidate_name": CANDIDATE_NAME,
        "is_rejection_record_only": True,
        "blockers": blockers,
        "verdict": (VERDICT_RJ16_RECORDED if not blockers
                    else "C16_REJECTION_BLOCKED"),
        "rejection_status": REJECTION_STATUS,
        "rejected_at_stage": REJECTED_AT_STAGE,
        "is_active_candidate": False,
        "parked_as_active": False,
        "kept_on_record": True,
        "original_frozen_c16_result_unchanged": True,
        "added_to_rejected_family_ledger": True,
        "no_replay_was_run": True,
        "no_pnl_was_run": True,
        # chain provenance
        "labels_review_verdict": labels.get("verdict"),
        "labels_structural_rejection_pressure":
            labels.get("structural_rejection_pressure"),
        "labels_structural_sample_size_passed":
            labels.get("structural_sample_size_passed"),
        "labels_net_beta_within_cap": labels.get("net_beta_within_cap"),
        # verbatim conclusion + lesson
        "conclusion": CONCLUSION,
        "kept_on_record_as": [
            "MARKET-NEUTRALITY avoided the long-bull-carry trap (C14/C15), but ran "
            "into a different wall",
            "cointegration in crypto is INTERMITTENT -> too few valid rolling-"
            "cointegrated pair-trade entries to support a program",
            "a level-OLS hedge ratio is NOT return-beta-neutral out of sample "
            "(observed net beta 2.82 >> 0.10) -- the positions are not actually "
            "market-neutral on real crypto pairs",
        ],
        # preserved decisive rejection facts
        "rejection_reasons": [
            "INSUFFICIENT sample size: 43 labels (< 100); ETHBTC 17 / SOLBTC 15 / "
            "SOLETH 11 (all < 20); chop regime 4 (< 20) -- the C13 class",
            "NET-BETA failure: observed net beta 2.82 exceeds the 0.10 market-"
            "neutral cap (level-OLS hedge not return-beta-neutral out of sample)",
            "intermittent cointegration creates too few valid entries to be "
            "tradeable",
        ],
        "evidence_headline": {
            "total_below_100": ACCEPTED_LABEL_COUNT < MIN_LABELS_TOTAL,
            "every_pair_below_20": all(PER_PAIR[p] < MIN_PER_PAIR for p in PER_PAIR),
            "chop_regime_below_20": PER_REGIME["chop"] < MIN_PER_REGIME,
            "forward_oos_populated_but_insufficient": FORWARD_OOS_LABEL_COUNT > 0
            and ACCEPTED_LABEL_COUNT < MIN_LABELS_TOTAL,
            "net_beta_exceeds_cap":
                MAX_ABS_NET_BETA_OBSERVED > MAX_ABS_NET_BETA_CAP,
            "no_replay_or_pnl_run": True,
        },
        # pinned numbers
        "accepted_label_count": ACCEPTED_LABEL_COUNT,
        "per_pair": dict(sorted(PER_PAIR.items())),
        "per_regime": dict(sorted(PER_REGIME.items())),
        "forward_oos_label_count": FORWARD_OOS_LABEL_COUNT,
        "max_abs_net_beta_observed": MAX_ABS_NET_BETA_OBSERVED,
        "max_abs_net_beta_cap": MAX_ABS_NET_BETA_CAP,
        "min_labels_total": MIN_LABELS_TOTAL, "min_per_pair": MIN_PER_PAIR,
        "min_per_regime": MIN_PER_REGIME,
        # evidence chain
        "pushed_evidence_chain": [dict(e) for e in PUSHED_EVIDENCE_CHAIN],
        "rejected_family_name": REJECTED_FAMILY_NAME,
        "proposed_ledger_bump": dict(PROPOSED_LEDGER_BUMP),
        "claim_locks": [
            "no_profitability_claim", "kept_on_record_not_active_candidate",
            "not_parked_as_active", "no_replay_was_run", "no_pnl_was_run",
            "insufficient_sample_size_disclosed", "net_beta_failure_disclosed",
            "market_neutral_does_not_hold_disclosed", "conclusion_recorded_precisely",
        ],
        "human_review_required": True,
        "current_loop_stage": "rejection_record",
        "next_required_action": NEXT_REQUIRED_ACTION,
        # gates locked
        "replay_gate_locked": True, "robustness_gate_locked": True,
        "relabel_gate_locked": True, "portfolio_gate_locked": True,
        "paper_trading_gate_locked": True, "micro_live_gate_locked": True,
        "live_gate_locked": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_replay": True, "no_pnl": True, "no_re_detect": True, "no_relabel": True,
        "no_optimization": True, "no_robustness_run": True,
        "no_portfolio_compute": True, "no_data_fetch": True, "no_data_mutation": True,
        "no_cost_application": True, "no_reactivation": True,
        "no_parking_as_active": True, "no_stage": True, "no_commit": True,
        "no_push": True, "no_auto_commit": True, "no_auto_push": True,
        "no_broker": True, "no_credentials": True, "no_order_logic": True,
        "no_paper_trading": True, "no_live_trading": True, "no_gate_skip": True,
        "no_downstream_gate_unlock": True, "no_profitability_claim": True,
        "no_market_neutral_claim": True, "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_c16_rejection_record(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the record is research-only,
    rejection-record-only, chain-gated on the frozen structural-rejection labels
    review, keeps the candidate not-active / not-parked / kept-on-record, records
    REJECT_C16_AT_LABELS with no replay/PnL run, preserves the verbatim conclusion
    and the structural + net-beta failure facts (none can be flipped), cites the 4
    pushed gate commits, and pins every capability flag False."""
    failures: list = []
    if record.get("mode") != RJ16_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_rejection_record_only") is not True:
        failures.append("not_rejection_record_only")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("verdict") != VERDICT_RJ16_RECORDED:
        failures.append("verdict_not_reject_c16_at_labels")
    if record.get("rejection_status") != REJECTION_STATUS:
        failures.append("status_not_rejected_at_labels")
    if record.get("rejected_at_stage") != REJECTED_AT_STAGE:
        failures.append("rejected_stage_not_labels")

    # not active / not parked / kept on record
    if record.get("is_active_candidate") is not False:
        failures.append("must_not_be_active")
    if record.get("parked_as_active") is not False:
        failures.append("must_not_be_parked")
    if record.get("kept_on_record") is not True:
        failures.append("must_be_kept_on_record")

    # no replay / no pnl
    if record.get("no_replay_was_run") is not True:
        failures.append("replay_must_not_have_run")
    if record.get("no_pnl_was_run") is not True:
        failures.append("pnl_must_not_have_run")

    # chain gate on the structural-rejection labels review
    if record.get("labels_review_verdict") != VERDICT_C16L_FROZEN:
        failures.append("labels_review_not_frozen")
    if record.get("labels_structural_rejection_pressure") is not True:
        failures.append("labels_not_structurally_rejected")
    if record.get("labels_structural_sample_size_passed") is not False:
        failures.append("labels_unexpectedly_passed")
    if record.get("labels_net_beta_within_cap") is not False:
        failures.append("net_beta_failure_must_remain")

    # verbatim conclusion
    if record.get("conclusion") != CONCLUSION:
        failures.append("conclusion_tampered")

    # preserved decisive failure facts -- cannot be flipped
    eh = record.get("evidence_headline") or {}
    for k in ("total_below_100", "every_pair_below_20", "chop_regime_below_20",
              "net_beta_exceeds_cap", "no_replay_or_pnl_run"):
        if eh.get(k) is not True:
            failures.append("rejection_finding_cleared_%s" % k)

    # pinned numbers intact
    if record.get("accepted_label_count") != ACCEPTED_LABEL_COUNT:
        failures.append("label_count_tampered")
    if record.get("per_pair") != dict(sorted(PER_PAIR.items())):
        failures.append("per_pair_tampered")
    if record.get("per_regime") != dict(sorted(PER_REGIME.items())):
        failures.append("per_regime_tampered")
    if record.get("max_abs_net_beta_observed") != MAX_ABS_NET_BETA_OBSERVED:
        failures.append("net_beta_observed_tampered")
    if record.get("forward_oos_label_count") != FORWARD_OOS_LABEL_COUNT:
        failures.append("forward_oos_count_tampered")
    if len(record.get("rejection_reasons") or []) < 3:
        failures.append("rejection_reasons_missing")

    # pushed evidence chain: 4 gate commits, each a 40-char sha
    chain = record.get("pushed_evidence_chain") or []
    stages = {e.get("stage"): e.get("commit") for e in chain}
    for required in ("family_proposal", "candidate_spec",
                     "detector_spec_and_synthetic_dry_run",
                     "real_candle_labels_review"):
        if required not in stages:
            failures.append("pushed_chain_missing_%s" % required)
        elif not (isinstance(stages[required], str)
                  and len(stages[required]) == 40):
            failures.append("pushed_chain_bad_commit_%s" % required)

    # ledger bump deferred
    pb = record.get("proposed_ledger_bump") or {}
    if pb.get("applied_here") is not False:
        failures.append("ledger_bump_must_not_be_applied_here")

    # gates locked
    for gate in ("replay_gate_locked", "robustness_gate_locked",
                 "relabel_gate_locked", "portfolio_gate_locked",
                 "paper_trading_gate_locked", "micro_live_gate_locked",
                 "live_gate_locked"):
        if record.get(gate) is not True:
            failures.append("gate_unlocked_%s" % gate)

    locks = record.get("scope_locks") or {}
    for key in ("no_replay", "no_pnl", "no_re_detect", "no_relabel",
                "no_optimization", "no_robustness_run", "no_portfolio_compute",
                "no_reactivation", "no_commit", "no_push", "no_auto_commit",
                "no_auto_push", "no_broker", "no_order_logic", "no_paper_trading",
                "no_live_trading", "no_gate_skip"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
