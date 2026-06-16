"""Candidate #10 (INTRAWEEK_CALENDAR_SEASONALITY_DRIFT_V1) formal rejection /
closeout record.

RESEARCH RECORD ONLY. This is the permanent ledger entry that closes Candidate
#10 as a REJECTED-KEPT-ON-RECORD family after it passed labels, fee+slippage-
honest replay, and robustness, then FAILED the final cross-asset / cross-weekday
/ forward-OOS generalization gate. Pure, in-memory record: NO file I/O, NO
network, NO trading, NO PnL, NO relabel, NO optimization, NO weekday
re-selection, NO downstream gate unlock. It does NOT approve paper or live, does
NOT claim profitability, and does NOT keep C10 as an active candidate -- it is
kept only as a historical lesson / research seed about decaying long-drift
artifacts.

Chain gate: build_c10_rejection_record() requires build_c10_generalization_review()
to return C10_DOES_NOT_GENERALIZE; any other verdict short-circuits to BLOCKED.

Full pushed evidence trail (origin/master):
  * detector labels review        -> 0de0f7c1 (156 accepted Friday setups frozen)
  * fee+slippage-honest replay     -> 9a03e638 (net-positive full sample, 2025 -ve)
  * robustness / sensitivity       -> 85e2cd6a (cost+horizon robust, front-loaded)
  * cross-asset/weekday/forward-OOS-> 67f6d663 (DOES NOT GENERALIZE)
"""
from __future__ import annotations

from typing import Any

from sparta_commander.intraweek_calendar_seasonality_drift_v1_cross_asset_weekday_forward_oos_review_contract import (  # noqa: E501
    VERDICT_C10GEN_DOES_NOT_GENERALIZE,
    build_c10_generalization_review,
)

RJ10_SCHEMA_VERSION = 1
RJ10_MODE = "RESEARCH_ONLY"
CANDIDATE_ID = "INTRAWEEK_CALENDAR_SEASONALITY_DRIFT_V1"
CANDIDATE_FAMILY = "intraweek_calendar_seasonality_drift"
CANDIDATE_NUMBER = 10

VERDICT_RJ10_RECORDED = (
    "C10_REJECTED_KEPT_ON_RECORD_FAILED_GENERALIZATION_GATE")
VERDICT_RJ10_BLOCKED = "C10_REJECTION_RECORD_BLOCKED"
REJECTION_STATUS = "REJECTED_KEPT_ON_RECORD"
NEXT_REQUIRED_ACTION = (
    "NONE__C10_CLOSED__KEPT_ON_RECORD_AS_DECAYING_LONG_DRIFT_RESEARCH_LESSON")

HEAD_AT_GENERALIZATION_REVIEW = "67f6d66379b35b4b0092e9da7b7b494aaf0cbbe5"

# Full pushed evidence trail (each is a committed + pushed gate on master).
PUSHED_EVIDENCE_CHAIN = (
    {"stage": "detector_labels_review",
     "commit": "0de0f7c1089a9650204a786a983502b34b0417be",
     "result": "156 accepted Friday setups frozen (FROZEN_FOR_HUMAN_REVIEW)"},
    {"stage": "fee_slippage_honest_replay_review",
     "commit": "9a03e638610c371efe8bde1255f958277f7b5bbe",
     "result": ("net-positive full sample after 37 bps all-in (2R/3R/4R), "
                "but 2025 negative (FROZEN_FOR_HUMAN_REVIEW)")},
    {"stage": "robustness_sensitivity_review",
     "commit": "85e2cd6a4b49ec6e07f74ee920caab23516a14ca",
     "result": ("cost-robust to 75 bps (3R/4R to 100 bps) and horizon-robust "
                "3-10 bars, but front-loaded and decaying, 2025 negative "
                "(FROZEN_FOR_HUMAN_REVIEW, WARNING)")},
    {"stage": "cross_asset_weekday_forward_oos_generalization_review",
     "commit": "67f6d66379b35b4b0092e9da7b7b494aaf0cbbe5",
     "result": ("DOES_NOT_GENERALIZE: 6/7 weekdays positive (not Friday-"
                "specific), ETH/SOL weak, forward-OOS 2026 negative on "
                "BTC/ETH/SOL")},
)

REJECTION_REASONS = (
    "Failed the generalization gate: the apparent Friday edge is general "
    "bullish long-drift, NOT a Friday-specific calendar anomaly (6 of 7 BTC "
    "weekdays net-positive over OOS).",
    "Cross-asset: ETH and SOL Friday were far weaker than BTC and negative in "
    "2025 -- the same decaying drift, not independent confirmation.",
    "Forward-OOS (2026 H1, truly post-training): NEGATIVE on BTC, ETH, and SOL "
    "-- the edge did not continue forward.",
    "Robustness already flagged a front-loaded, monotonically decaying edge "
    "with a negative 2025; generalization confirmed it is not robust.",
    "Therefore C10 is NOT a robust tradeable calendar-seasonality edge.",
)

KEPT_ON_RECORD_AS = (
    "Historical lesson: a candidate can pass labels, cost-honest replay, and "
    "robustness yet still be a DECAYING LONG-DRIFT ARTIFACT that fails "
    "cross-weekday specificity and forward-OOS continuation.",
    "Research seed: future calendar/seasonality candidates must include a "
    "cross-weekday specificity check and a forward-OOS continuation check "
    "BEFORE any promotion consideration.",
)

EVIDENCE_HEADLINE = {
    "accepted_setups": 156,
    "symbol_in_sample": "BTCUSD",
    "weekday": "Friday(5)",
    "all_in_cost_bps": 37.0,
    "replay_net_r_3r_full_sample": 22.48,
    "replay_2025_net_r_3r": -3.29,
    "cross_weekday_positive_count_of_7": 6,
    "friday_is_unique_positive_weekday": False,
    "forward_oos_2026_positive_any_asset": False,
}

CLAIM_LOCKS = (
    "no_profitability_claim", "no_paper_approval", "no_live_approval",
    "no_execution_approval", "no_capital_deployment", "no_portfolio_allocation",
    "kept_on_record_not_active_candidate", "no_relabel_of_original_result",
    "no_optimization_or_weekday_reselection",
    "original_frozen_c10_result_unchanged",
    "generalization_failure_is_the_rejection_basis",
)

RJ10_LABEL = (
    "SPARTA Candidate #10 FORMAL REJECTION RECORD (READ-ONLY, RESEARCH ONLY). "
    "REJECTED_KEPT_ON_RECORD: passed labels/replay/robustness but FAILED "
    "generalization (general long-drift, not Friday-specific; forward-OOS "
    "negative on BTC/ETH/SOL). NOT AN ACTIVE CANDIDATE. NOT A PROFITABILITY "
    "CLAIM. NOT AN APPROVAL FOR PAPER OR LIVE. KEPT ONLY AS A HISTORICAL "
    "LESSON / RESEARCH SEED."
)

_CAPABILITY_FLAGS_FALSE = (
    "is_active_candidate", "keeps_as_active_candidate", "promotes_to_paper",
    "promotes_to_live", "promotes_gate", "unlocks_downstream_gate",
    "relabels_original_result", "reselects_weekday", "fits_parameters",
    "optimizes", "applies_regime_filter", "runs_detection_now",
    "runs_replay_now", "scores_live", "stages_data_now", "fetches_data",
    "calls_api", "uses_network", "uses_credentials", "uses_wallet",
    "uses_account", "connects_broker", "connects_exchange", "uses_real_money",
    "contains_order_logic", "contains_portfolio_allocation_logic",
    "deploys_capital", "starts_scheduler", "sends_notifications",
    "auto_commits", "auto_pushes", "modifies_frozen_labels",
    "modifies_replay_artifacts", "modifies_robustness_artifact",
    "modifies_generalization_artifact", "computes_live_pnl",
    "authorizes_paper_execution", "authorizes_micro_live",
    "authorizes_live_trading", "claims_profitability", "claims_edge",
    "executes", "writes_files",
)


def get_candidate_10_rejection_record_label() -> str:
    return RJ10_LABEL


def get_candidate_10_rejection_record_next_action() -> str:
    return NEXT_REQUIRED_ACTION


def build_c10_rejection_record(repo_root: Any = ".",
                               tracked_paths: list | None = None
                               ) -> dict[str, Any]:
    """Assemble the permanent C10 rejection / closeout record. Chain-gated on
    the pushed generalization review (must be DOES_NOT_GENERALIZE). Pure; no
    I/O."""
    record: dict[str, Any] = {
        "schema_version": RJ10_SCHEMA_VERSION,
        "label": RJ10_LABEL, "mode": RJ10_MODE,
        "lane": "crypto_d1_auto_research",
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "candidate_number": CANDIDATE_NUMBER,
        "verdict": None, "blockers": [], "failures": [],
        "rejection_status": REJECTION_STATUS,
        "is_active_candidate": False,
        "kept_on_record": True,
        "kept_on_record_as": list(KEPT_ON_RECORD_AS),
        "head_at_generalization_review": HEAD_AT_GENERALIZATION_REVIEW,
        "pushed_evidence_chain": [dict(e) for e in PUSHED_EVIDENCE_CHAIN],
        "rejection_reasons": list(REJECTION_REASONS),
        "evidence_headline": dict(EVIDENCE_HEADLINE),
        "claim_locks": list(CLAIM_LOCKS),
        "original_frozen_c10_result_unchanged": True,
        "current_loop_stage": "closed_rejected_kept_on_record",
        "human_review_required": False,
        "relabel_gate_locked": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
        "live_gate_locked": True,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_paper_trading": True, "no_micro_live": True,
        "no_live_trading": True, "no_broker": True, "no_exchange": True,
        "no_wallet": True, "no_account": True, "no_credentials": True,
        "no_order_logic": True, "no_portfolio_allocation": True,
        "no_api": True, "no_network": True, "no_fetch": True,
        "no_notification": True, "no_scheduler": True, "no_relabel": True,
        "no_weekday_reselection": True, "no_parameter_fitting": True,
        "no_optimization": True, "no_regime_filter": True,
        "no_detector_change": True, "no_profitability_claim": True,
        "no_downstream_gate_unlock": True,
    }

    gen = build_c10_generalization_review(repo_root, tracked_paths or [])
    record["generalization_review_verdict"] = gen["verdict"]
    if gen["verdict"] != VERDICT_C10GEN_DOES_NOT_GENERALIZE:
        record["verdict"] = VERDICT_RJ10_BLOCKED
        record["blockers"].append("generalization_review_not_does_not_generalize")
        return record

    record["verdict"] = VERDICT_RJ10_RECORDED
    return record


def validate_c10_rejection_record(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. RECORDED is valid only when the rejection status,
    kept-on-record-not-active framing, the full evidence chain, locks, and
    capability locks are intact."""
    failures: list = []
    if record.get("verdict") != VERDICT_RJ10_RECORDED:
        failures.append("verdict_not_recorded")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("rejection_status") != REJECTION_STATUS:
        failures.append("rejection_status_tampered")
    if record.get("is_active_candidate") is not False:
        failures.append("is_active_candidate_must_be_false")
    if record.get("kept_on_record") is not True:
        failures.append("kept_on_record_must_be_true")
    if record.get("original_frozen_c10_result_unchanged") is not True:
        failures.append("original_result_unchanged_flag_tampered")

    if record.get("head_at_generalization_review") != (
            HEAD_AT_GENERALIZATION_REVIEW):
        failures.append("head_tampered")

    # Evidence chain must cite all four pushed stages with 40-hex commits.
    chain = record.get("pushed_evidence_chain") or []
    stages = {e.get("stage") for e in chain if isinstance(e, dict)}
    for required in ("detector_labels_review",
                     "fee_slippage_honest_replay_review",
                     "robustness_sensitivity_review",
                     "cross_asset_weekday_forward_oos_generalization_review"):
        if required not in stages:
            failures.append("evidence_chain_missing_%s" % required)
    for e in chain:
        if isinstance(e, dict):
            c = e.get("commit", "")
            if not (isinstance(c, str) and len(c) == 40):
                failures.append("evidence_chain_bad_commit_%s" % e.get("stage"))

    if not record.get("rejection_reasons"):
        failures.append("rejection_reasons_missing")
    if not record.get("kept_on_record_as"):
        failures.append("kept_on_record_as_missing")

    locks = record.get("scope_locks") or {}
    for key, val in locks.items():
        if val is not True:
            failures.append("scope_lock_false_%s" % key)
    for key in ("relabel_gate_locked", "paper_trading_gate_locked",
                "micro_live_gate_locked", "live_gate_locked"):
        if record.get(key) is not True:
            failures.append("gate_flag_tampered_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    for required in ("no_profitability_claim", "kept_on_record_not_active_candidate",
                     "no_relabel_of_original_result",
                     "no_optimization_or_weekday_reselection"):
        if required not in (record.get("claim_locks") or []):
            failures.append("claim_lock_missing_%s" % required)

    return {"valid": not failures, "failures": failures}
