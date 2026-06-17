"""Candidate #11 (CROSS_ASSET_DISPERSION_REVERSION_V1) formal rejection /
closeout record.

RESEARCH RECORD ONLY. This is the permanent ledger entry that closes Candidate
#11 as a REJECTED-KEPT-ON-RECORD family after it passed family proposal,
candidate spec, detector dry-run, and real-candle labels (which were strong --
cross-asset, cross-regime, weekday-neutral) but then FAILED the fee+slippage-
honest replay: the forward-OOS 2026 continuation check was negative for every
variant, the bear regime was negative/weak, and the result was horizon/drift
dominated rather than clean cross-sectional dispersion reversion.

Pure, in-memory record: NO file I/O, NO network, NO trading, NO PnL, NO relabel,
NO optimization, NO horizon/asset/regime reselection, NO regime-filter attempt,
NO robustness, NO portfolio compute, NO downstream gate unlock. It does NOT
approve paper or live, does NOT claim profitability, and does NOT keep C11 as an
active candidate or park it as active -- it is kept ONLY as a historical lesson /
research seed: strong real-candle labels are necessary but NOT sufficient; the
fee-honest replay forward-OOS + regime-symmetry checks are the real gate.

Chain gate: build_c11_rejection_record() requires build_c11_replay_review() to
return C11_REPLAY_RESULTS_FROZEN_FOR_HUMAN_REVIEW carrying
structural_rejection_pressure=True and forward_oos_continuation_passed=False; any
other state short-circuits to BLOCKED.

Full pushed evidence trail (origin/master), proposal -> ... -> replay failure:
  * candidate spec                 -> 748414f5 (strict pre-registered spec)
  * detector spec + synthetic dry  -> 6e1efd2b (cross-sectional laggard geometry)
  * real-candle labels review      -> 8e69956b (742 labels; battery PASS at labels)
  * fee+slippage-honest replay     -> cf39a553 (forward-OOS 2026 negative -> reject)
The originating family proposal stage precedes the spec locally (see
FAMILY_PROPOSAL_STAGE; its contract is not separately pushed on origin -- a
tracked-state gap recorded here for honesty, NOT part of the rejection basis).
"""
from __future__ import annotations

from typing import Any

from sparta_commander.cross_asset_dispersion_reversion_v1_replay_results_review_contract import (  # noqa: E501
    VERDICT_C11RR_FROZEN,
    build_c11_replay_review,
)

RJ11_SCHEMA_VERSION = 1
RJ11_MODE = "RESEARCH_ONLY"
CANDIDATE_ID = "CROSS_ASSET_DISPERSION_REVERSION_V1"
CANDIDATE_FAMILY = "cross_asset_dispersion_reversion"
CANDIDATE_NUMBER = 11

VERDICT_RJ11_RECORDED = (
    "C11_REJECTED_KEPT_ON_RECORD_FAILED_FEE_HONEST_REPLAY")
VERDICT_RJ11_BLOCKED = "C11_REJECTION_RECORD_BLOCKED"
REJECTION_STATUS = "REJECTED_KEPT_ON_RECORD"
NEXT_REQUIRED_ACTION = (
    "NONE__C11_CLOSED__KEPT_ON_RECORD_AS_HORIZON_DRIFT_DOMINATED_"
    "FORWARD_OOS_NEGATIVE_RESEARCH_LESSON")

HEAD_AT_REPLAY_REVIEW = "cf39a55392e50582b3ee2ea84b7d043459ca3afd"

# Full pushed evidence trail (each is a committed + pushed gate on master).
PUSHED_EVIDENCE_CHAIN = (
    {"stage": "candidate_spec",
     "commit": "748414f57eafc7dff543b7bbc5294e39fc074089",
     "result": ("strict pre-registered cross-asset dispersion-reversion spec "
                "(CANDIDATE_11_SPEC_READY); materially new vs C1-C10")},
    {"stage": "detector_spec_and_synthetic_dry_run",
     "commit": "6e1efd2bb6082aef038b6d0de5578e0f0bdd4519",
     "result": ("cross-sectional laggard geometry; z<=-1.0 + basket regime "
                "filter; 1.5xATR(14) stop; 2R/3R/4R; 81 bps floor "
                "(CANDIDATE_11_DETECTOR_DRY_RUN_READY)")},
    {"stage": "real_candle_labels_review",
     "commit": "8e69956ba10ea1c5dd80c2860b71142e2e9f512a",
     "result": ("742 accepted labels across BTC/ETH/SOL; cross-asset + "
                "cross-regime + weekday-neutral; sample-size + early "
                "generalization battery PASS at labels "
                "(C11_REAL_CANDLE_LABELS_FROZEN_FOR_HUMAN_REVIEW)")},
    {"stage": "fee_slippage_honest_replay_review",
     "commit": "cf39a55392e50582b3ee2ea84b7d043459ca3afd",
     "result": ("full-sample net-positive after 37 bps all-in (2R/3R/4R) BUT "
                "forward-OOS 2026 NEGATIVE for every variant, bear-regime "
                "negative, horizon/drift dominated -> STRUCTURAL REJECTION "
                "PRESSURE (C11_REPLAY_RESULTS_FROZEN_FOR_HUMAN_REVIEW)")},
)

# The originating proposal stage (local, pre-spec). Recorded for honesty: its
# contract file is NOT separately committed on origin -- a tracked-state gap, NOT
# part of the rejection basis. The earliest PUSHED C11 gate is the candidate spec.
FAMILY_PROPOSAL_STAGE = {
    "stage": "family_proposal",
    "pushed_separately_on_origin": False,
    "earliest_pushed_ancestor_commit":
        "748414f57eafc7dff543b7bbc5294e39fc074089",
    "note": ("originating cross_asset_dispersion_reversion family proposal; "
             "exists locally and gates the spec import, but its contract is not "
             "separately tracked on origin; recorded for honesty only -- not the "
             "rejection basis"),
}

REJECTION_REASONS = (
    "Failed the fee+slippage-honest replay forward-OOS continuation check: net "
    "all-in R in the truly-post-2026-01-01 window was NEGATIVE for all three "
    "variants (2R -0.95R, 3R -0.12R, 4R -0.12R) -- the edge did not continue "
    "forward.",
    "Not regime-symmetric: bear-regime net all-in R was negative for 2R/3R "
    "(and only marginally positive for 4R), so the result is not the "
    "regime-symmetric cross-sectional reversion the spec required.",
    "Horizon/drift dominated: 65-75% of resolved trades exited at the 5-bar "
    "horizon and the target hit rate was only ~2-11%, so the positive full "
    "sample leans on bull/chop holding drift, not target capture.",
    "Concentration: BTCUSD was net negative across all variants; the positive "
    "full-sample total was carried by ETH and SOL, and 2022 was strongly "
    "negative.",
    "Therefore C11 is NOT a clean tradeable cross-sectional dispersion-"
    "reversion edge and must not continue to robustness or promotion.",
)

KEPT_ON_RECORD_AS = (
    "Historical lesson: strong real-candle labels (cross-asset, cross-regime, "
    "weekday-neutral, sample-size PASS) are NECESSARY but NOT SUFFICIENT -- a "
    "candidate can pass the entire labels-stage early-generalization battery "
    "and still fail the fee-honest replay on forward-OOS continuation and "
    "regime symmetry.",
    "Research seed: keep the forward-OOS 2026 continuation check and the "
    "regime-symmetry (bear must hold) check as HARD replay-stage gates, and "
    "treat horizon-exit dominance as a long-drift warning, for every future "
    "relative/cross-sectional candidate.",
)

EVIDENCE_HEADLINE = {
    "accepted_labels": 742,
    "symbols": ["BTCUSD", "ETHUSD", "SOLUSD"],
    "labels_battery_passed": True,
    "all_in_cost_bps": 37.0,
    "holding_horizon_bars": 5,
    "holding_horizon_human_fixed_spec_silent": True,
    "replay_net_r_3r_full_sample": 30.9979,
    "replay_forward_oos_2026_net_r_2r": -0.9540,
    "replay_forward_oos_2026_net_r_3r": -0.1178,
    "replay_forward_oos_2026_net_r_4r": -0.1178,
    "forward_oos_2026_positive_any_variant": False,
    "bear_regime_net_r_3r": -2.4449,
    "regime_symmetry_passed": False,
    "horizon_exit_share_3r": 0.7299,
    "hit_rate_3r": 0.0401,
    "btc_net_negative_all_variants": True,
}

CLAIM_LOCKS = (
    "no_profitability_claim", "no_paper_approval", "no_live_approval",
    "no_execution_approval", "no_capital_deployment", "no_portfolio_allocation",
    "kept_on_record_not_active_candidate", "not_parked_as_active",
    "no_relabel_of_original_result",
    "no_optimization_or_horizon_asset_regime_reselection",
    "no_regime_filter_attempt",
    "original_frozen_c11_result_unchanged",
    "fee_honest_replay_forward_oos_failure_is_the_rejection_basis",
)

RJ11_LABEL = (
    "SPARTA Candidate #11 FORMAL REJECTION RECORD (READ-ONLY, RESEARCH ONLY). "
    "REJECTED_KEPT_ON_RECORD: passed proposal/spec/detector/labels (strong "
    "cross-asset, cross-regime, weekday-neutral labels) but FAILED the "
    "fee-honest replay (forward-OOS 2026 negative for every variant, "
    "bear-regime negative, horizon/drift dominated). NOT AN ACTIVE CANDIDATE. "
    "NOT PARKED AS ACTIVE. NOT A PROFITABILITY CLAIM. NOT AN APPROVAL FOR PAPER "
    "OR LIVE. KEPT ONLY AS A HISTORICAL LESSON / RESEARCH SEED."
)

_CAPABILITY_FLAGS_FALSE = (
    "is_active_candidate", "keeps_as_active_candidate", "parks_as_active",
    "promotes_to_robustness", "promotes_to_paper", "promotes_to_live",
    "promotes_gate", "unlocks_downstream_gate", "relabels_original_result",
    "reselects_horizon", "reselects_asset", "reselects_regime",
    "fits_parameters", "optimizes", "applies_regime_filter",
    "runs_detection_now", "runs_replay_now", "runs_robustness",
    "runs_portfolio_compute", "scores_live", "stages_data_now", "fetches_data",
    "mutates_source_data", "calls_api", "uses_network", "uses_credentials",
    "uses_wallet", "uses_account", "connects_broker", "connects_exchange",
    "uses_real_money", "contains_order_logic",
    "contains_portfolio_allocation_logic", "deploys_capital",
    "starts_scheduler", "sends_notifications", "auto_commits", "auto_pushes",
    "modifies_frozen_labels", "modifies_replay_artifacts", "computes_live_pnl",
    "authorizes_paper_execution", "authorizes_micro_live",
    "authorizes_live_trading", "claims_profitability", "claims_edge",
    "executes", "writes_files",
)


def get_candidate_11_rejection_record_label() -> str:
    return RJ11_LABEL


def get_candidate_11_rejection_record_next_action() -> str:
    return NEXT_REQUIRED_ACTION


def build_c11_rejection_record(repo_root: Any = ".",
                               tracked_paths: list | None = None
                               ) -> dict[str, Any]:
    """Assemble the permanent C11 rejection / closeout record. Chain-gated on the
    pushed fee-honest replay review (must be FROZEN with
    structural_rejection_pressure=True and forward_oos_continuation_passed=False).
    Pure; no I/O."""
    record: dict[str, Any] = {
        "schema_version": RJ11_SCHEMA_VERSION,
        "label": RJ11_LABEL, "mode": RJ11_MODE,
        "lane": "crypto_d1_auto_research",
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "candidate_number": CANDIDATE_NUMBER,
        "verdict": None, "blockers": [], "failures": [],
        "rejection_status": REJECTION_STATUS,
        "is_active_candidate": False,
        "parked_as_active": False,
        "kept_on_record": True,
        "kept_on_record_as": list(KEPT_ON_RECORD_AS),
        "head_at_replay_review": HEAD_AT_REPLAY_REVIEW,
        "pushed_evidence_chain": [dict(e) for e in PUSHED_EVIDENCE_CHAIN],
        "family_proposal_stage": dict(FAMILY_PROPOSAL_STAGE),
        "rejection_reasons": list(REJECTION_REASONS),
        "evidence_headline": dict(EVIDENCE_HEADLINE),
        "claim_locks": list(CLAIM_LOCKS),
        "original_frozen_c11_result_unchanged": True,
        "current_loop_stage": "closed_rejected_kept_on_record",
        "human_review_required": False,
        "robustness_gate_locked": True,
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
        "no_portfolio_compute": True, "no_api": True, "no_network": True,
        "no_fetch": True, "no_data_mutation": True, "no_notification": True,
        "no_scheduler": True, "no_relabel": True, "no_horizon_reselection": True,
        "no_asset_reselection": True, "no_regime_reselection": True,
        "no_parameter_fitting": True, "no_optimization": True,
        "no_regime_filter": True, "no_robustness_run": True,
        "no_detector_change": True, "no_profitability_claim": True,
        "no_downstream_gate_unlock": True,
    }

    # Chain gate: the pushed replay review must certify FROZEN with structural
    # rejection pressure and a FAILED forward-OOS continuation check.
    rr = build_c11_replay_review(repo_root, tracked_paths or [])
    record["replay_review_verdict"] = rr.get("verdict")
    record["replay_structural_rejection_pressure"] = rr.get(
        "structural_rejection_pressure")
    record["replay_forward_oos_continuation_passed"] = rr.get(
        "forward_oos_continuation_passed")
    if rr.get("verdict") != VERDICT_C11RR_FROZEN:
        record["verdict"] = VERDICT_RJ11_BLOCKED
        record["blockers"].append("replay_review_not_frozen")
        return record
    if rr.get("structural_rejection_pressure") is not True:
        record["verdict"] = VERDICT_RJ11_BLOCKED
        record["blockers"].append("replay_review_no_structural_rejection_pressure")
        return record
    if rr.get("forward_oos_continuation_passed") is not False:
        record["verdict"] = VERDICT_RJ11_BLOCKED
        record["blockers"].append("replay_forward_oos_did_not_fail")
        return record

    record["verdict"] = VERDICT_RJ11_RECORDED
    return record


def validate_c11_rejection_record(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. RECORDED is valid only when the rejection status,
    kept-on-record-not-active (and not-parked-as-active) framing, the full pushed
    evidence chain, the replay forward-OOS failure basis, locks, and capability
    locks are all intact."""
    failures: list = []
    if record.get("verdict") != VERDICT_RJ11_RECORDED:
        failures.append("verdict_not_recorded")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("rejection_status") != REJECTION_STATUS:
        failures.append("rejection_status_tampered")
    if record.get("is_active_candidate") is not False:
        failures.append("is_active_candidate_must_be_false")
    if record.get("parked_as_active") is not False:
        failures.append("parked_as_active_must_be_false")
    if record.get("kept_on_record") is not True:
        failures.append("kept_on_record_must_be_true")
    if record.get("original_frozen_c11_result_unchanged") is not True:
        failures.append("original_result_unchanged_flag_tampered")

    if record.get("head_at_replay_review") != HEAD_AT_REPLAY_REVIEW:
        failures.append("head_tampered")

    # Rejection basis: replay FROZEN + structural rejection + forward-OOS failed.
    if record.get("replay_review_verdict") != VERDICT_C11RR_FROZEN:
        failures.append("replay_review_verdict_tampered")
    if record.get("replay_structural_rejection_pressure") is not True:
        failures.append("structural_rejection_pressure_tampered")
    if record.get("replay_forward_oos_continuation_passed") is not False:
        failures.append("forward_oos_pass_flag_tampered")

    # Evidence chain must cite all four pushed stages with 40-hex commits.
    chain = record.get("pushed_evidence_chain") or []
    stages = {e.get("stage") for e in chain if isinstance(e, dict)}
    for required in ("candidate_spec",
                     "detector_spec_and_synthetic_dry_run",
                     "real_candle_labels_review",
                     "fee_slippage_honest_replay_review"):
        if required not in stages:
            failures.append("evidence_chain_missing_%s" % required)
    for e in chain:
        if isinstance(e, dict):
            c = e.get("commit", "")
            if not (isinstance(c, str) and len(c) == 40):
                failures.append("evidence_chain_bad_commit_%s" % e.get("stage"))
    # The originating proposal stage must be cited (honestly marked not pushed).
    fp = record.get("family_proposal_stage") or {}
    if fp.get("stage") != "family_proposal":
        failures.append("family_proposal_stage_missing")
    if fp.get("pushed_separately_on_origin") is not False:
        failures.append("family_proposal_pushed_flag_tampered")

    if not record.get("rejection_reasons"):
        failures.append("rejection_reasons_missing")
    if not record.get("kept_on_record_as"):
        failures.append("kept_on_record_as_missing")
    eh = record.get("evidence_headline") or {}
    if eh.get("forward_oos_2026_positive_any_variant") is not False:
        failures.append("evidence_forward_oos_positive_flag_tampered")
    if eh.get("regime_symmetry_passed") is not False:
        failures.append("evidence_regime_symmetry_flag_tampered")

    locks = record.get("scope_locks") or {}
    for key, val in locks.items():
        if val is not True:
            failures.append("scope_lock_false_%s" % key)
    for key in ("robustness_gate_locked", "relabel_gate_locked",
                "paper_trading_gate_locked", "micro_live_gate_locked",
                "live_gate_locked"):
        if record.get(key) is not True:
            failures.append("gate_flag_tampered_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    for required in ("no_profitability_claim",
                     "kept_on_record_not_active_candidate",
                     "not_parked_as_active",
                     "no_relabel_of_original_result",
                     "no_optimization_or_horizon_asset_regime_reselection",
                     "no_regime_filter_attempt"):
        if required not in (record.get("claim_locks") or []):
            failures.append("claim_lock_missing_%s" % required)

    for banned in ("APPROVE", "PAPER", "LIVE", "EXECUTE", "BROKER", "ORDER",
                   "PROMOTE", "UNLOCK"):
        if banned in NEXT_REQUIRED_ACTION.upper():
            failures.append("next_action_banned_token_%s" % banned)

    return {"valid": not failures, "failures": failures}
