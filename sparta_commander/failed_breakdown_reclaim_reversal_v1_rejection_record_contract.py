"""Candidate #12 (failed_breakdown_reclaim_reversal_v1) formal rejection /
closeout record.

RESEARCH RECORD ONLY. This is the permanent ledger entry that closes Candidate
#12 as a REJECTED-KEPT-ON-RECORD family after it passed family proposal,
candidate spec, detector dry-run, and real-candle labels (which were strong --
206 labels, cross-asset, cross-regime with BEAR the largest bucket, weekday-
neutral) but then FAILED the fee+slippage-honest replay outright: net-negative
after 37 bps across every target variant, WORSE than a matched random-entry
baseline, net-negative in bull AND bear AND chop, net-negative in the forward-OOS
2026 window, and target capture did not dominate horizon exits.

Pure, in-memory record: NO file I/O, NO network, NO trading, NO PnL, NO new
replay, NO relabel, NO data fetch, NO robustness, NO portfolio compute, NO
optimization, NO downstream gate unlock. It does NOT approve paper or live, does
NOT claim profitability, and does NOT keep C12 as an active candidate or park it
as active -- it is kept ONLY as a historical lesson / research seed: the
must-beat-RANDOM-ENTRY gate (new in C12) cleanly catches a non-edge that strong
labels alone would have hidden.

Chain gate: build_c12_rejection_record() requires build_c12_replay_review() to
return C12_REPLAY_RESULTS_FROZEN_FOR_HUMAN_REVIEW carrying
structural_rejection_pressure=True and any_variant_passes_all_decisive_gates=
False; any other state short-circuits to BLOCKED.

Full pushed evidence trail (origin/master), proposal -> ... -> replay failure:
  * family proposal             -> 710429b7
  * candidate spec              -> 6ad2c1b9
  * detector spec + synthetic   -> c29c165c
  * real-candle labels review   -> f9b510d9 (206 labels; battery PASS at labels)
  * fee+slippage-honest replay  -> 70116e70 (net negative / worse-than-random)
"""
from __future__ import annotations

from typing import Any

from sparta_commander.failed_breakdown_reclaim_reversal_v1_replay_results_review_contract import (  # noqa: E501
    VERDICT_C12RR_FROZEN,
    build_c12_replay_review,
)

RJ12_SCHEMA_VERSION = 1
RJ12_MODE = "RESEARCH_ONLY"
CANDIDATE_ID = "FAILED_BREAKDOWN_RECLAIM_REVERSAL_V1"
CANDIDATE_FAMILY = "failed_breakdown_reclaim_reversal"
CANDIDATE_NUMBER = 12

VERDICT_RJ12_RECORDED = (
    "C12_REJECTED_KEPT_ON_RECORD_FAILED_FEE_HONEST_REPLAY")
VERDICT_RJ12_BLOCKED = "C12_REJECTION_RECORD_BLOCKED"
REJECTION_STATUS = "REJECTED_KEPT_ON_RECORD"
NEXT_REQUIRED_ACTION = (
    "NONE__C12_CLOSED__KEPT_ON_RECORD_AS_NEGATIVE_EDGE_WORSE_THAN_RANDOM_"
    "RESEARCH_LESSON")

HEAD_AT_REPLAY_REVIEW = "70116e70e7770d6b9ef4ecb38d7106613e52861e"

# Full pushed evidence trail (each is a committed + pushed gate on master).
PUSHED_EVIDENCE_CHAIN = (
    {"stage": "family_proposal",
     "commit": "710429b7a71b7ba4d23567b64e16062f55bf3bc4",
     "result": ("materially-new failed-breakdown reclaim reversal family vs "
                "C1-C11; forward-OOS + regime symmetry + must-beat buy-and-hold "
                "AND random-entry + target-capture dominance as hard gates "
                "(CANDIDATE_12_FAMILY_PROPOSAL_READY)")},
    {"stage": "candidate_spec",
     "commit": "6ad2c1b97edb8985ab9d671130bdbc26afcec55c",
     "result": ("frozen spec: K=20 reclaim, ATR(14) stop, 1.5R/2R/3R, 81 bps "
                "floor, <=3-bar hold, per-asset non-overlap, 37 bps, both "
                "baseline gates + horizon cap (CANDIDATE_12_SPEC_READY)")},
    {"stage": "detector_spec_and_synthetic_dry_run",
     "commit": "c29c165cf0fc95dabf2da828c16977b4866df994",
     "result": ("synthetic dry-run proofs of the close-confirmed reclaim "
                "geometry + exit handling + non-overlap "
                "(CANDIDATE_12_DETECTOR_DRY_RUN_READY)")},
    {"stage": "real_candle_labels_review",
     "commit": "f9b510d9d8a4cb50bfb17bad5e5fa47f8e7b4038",
     "result": ("206 accepted labels across BTC/ETH/SOL; cross-asset + "
                "cross-regime (bear LARGEST) + weekday-neutral; sample-size + "
                "structural checks PASS at labels "
                "(C12_REAL_CANDLE_LABELS_FROZEN_FOR_HUMAN_REVIEW)")},
    {"stage": "fee_slippage_honest_replay_review",
     "commit": "70116e70e7770d6b9ef4ecb38d7106613e52861e",
     "result": ("net-negative after 37 bps EVERY variant (1.5R -48.8R / 2R "
                "-47.0R / 3R -45.4R), WORSE than random entry (pctl 0.02-0.05), "
                "all regimes negative, forward-OOS 2026 -13.0R, target capture "
                "does not dominate -> STRUCTURAL REJECTION PRESSURE "
                "(C12_REPLAY_RESULTS_FROZEN_FOR_HUMAN_REVIEW)")},
)

REJECTION_REASONS = (
    "Net-negative after 37 bps all-in across every target variant (1.5R -48.8R, "
    "2R -47.0R, 3R -45.4R over 204 resolved trades).",
    "WORSE than a matched random-entry baseline: the strategy beats only 2-5% of "
    "deterministic random resamples (random means -23.3 / -17.9 / -12.0R) -- the "
    "failed-breakdown reclaim trigger adds NEGATIVE value over random timing.",
    "Not regime-symmetric: bull, bear AND chop are ALL net-negative; bear "
    "(~-30R) and chop (~-15R) are structurally weak.",
    "Forward-OOS 2026 is net-negative (-13.0R) for every variant -- the edge "
    "does not continue forward.",
    "Target capture does NOT dominate: hits (6-27) are far fewer than horizon "
    "exits (93-113); 3R is horizon-dominated (55%).",
    "The only nominally-passing gate (beats buy-and-hold) passes only because a "
    "passive hold of the same post-reclaim windows is even more negative "
    "(-86.7R); it is not evidence of an edge.",
    "Therefore C12 is NOT a tradeable edge and must not continue to robustness "
    "or promotion.",
)

KEPT_ON_RECORD_AS = (
    "Historical lesson: the must-beat-RANDOM-ENTRY gate (new in C12) is the "
    "decisive filter -- it cleanly exposed a non-edge that strong labels (206, "
    "cross-asset, cross-regime, weekday-neutral, bear LARGEST) would otherwise "
    "have hidden. Strong labels remain NECESSARY BUT NOT SUFFICIENT.",
    "Research seed: keep must-beat-buy-and-hold AND must-beat-random-entry, "
    "cross-regime net symmetry, the horizon-exit cap / target-capture "
    "dominance, and forward-OOS continuation as HARD replay-stage gates for "
    "every future long-only candidate; they reject negative/zero edges before "
    "any robustness or promotion spend.",
)

EVIDENCE_HEADLINE = {
    "accepted_labels": 206,
    "resolved_trades": 204,
    "symbols": ["BTCUSD", "ETHUSD", "SOLUSD"],
    "labels_battery_passed": True,
    "all_in_cost_bps": 37.0,
    "holding_horizon_bars": 3,
    "net_r_all_in_1_5r": -48.7963,
    "net_r_all_in_2r": -47.0458,
    "net_r_all_in_3r": -45.4211,
    "net_negative_all_variants": True,
    "random_entry_percentile_3r": 0.02,
    "worse_than_random_entry": True,
    "regime_net_all_in_3r": {"bull": -2.2021, "bear": -28.7519, "chop": -14.4672},
    "all_regimes_negative": True,
    "forward_oos_2026_net_r": -12.9812,
    "forward_oos_2026_positive": False,
    "target_capture_dominates": False,
}

CLAIM_LOCKS = (
    "no_profitability_claim", "no_paper_approval", "no_live_approval",
    "no_execution_approval", "no_capital_deployment", "no_portfolio_allocation",
    "kept_on_record_not_active_candidate", "not_parked_as_active",
    "no_relabel_of_original_result", "no_new_replay", "no_optimization",
    "no_robustness_promotion",
    "original_frozen_c12_result_unchanged",
    "fee_honest_replay_negative_edge_is_the_rejection_basis",
    "worse_than_random_entry_disclosed",
)

RJ12_LABEL = (
    "SPARTA Candidate #12 FORMAL REJECTION RECORD (READ-ONLY, RESEARCH ONLY). "
    "REJECTED_KEPT_ON_RECORD: passed proposal/spec/detector/labels (206 strong "
    "cross-asset, cross-regime, weekday-neutral labels) but FAILED the fee-honest "
    "replay -- net-negative every variant, WORSE than random entry, all regimes "
    "negative, forward-OOS 2026 negative, target capture does not dominate. NOT "
    "AN ACTIVE CANDIDATE. NOT PARKED AS ACTIVE. NOT A PROFITABILITY CLAIM. NOT AN "
    "APPROVAL FOR PAPER OR LIVE. KEPT ONLY AS A HISTORICAL LESSON / RESEARCH SEED."
)

_CAPABILITY_FLAGS_FALSE = (
    "is_active_candidate", "keeps_as_active_candidate", "parks_as_active",
    "promotes_to_robustness", "promotes_to_paper", "promotes_to_live",
    "promotes_gate", "unlocks_downstream_gate", "relabels_original_result",
    "runs_new_replay", "reselects_horizon", "reselects_asset",
    "reselects_regime", "fits_parameters", "optimizes", "uses_one_edit_allowance",
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


def get_candidate_12_rejection_record_label() -> str:
    return RJ12_LABEL


def get_candidate_12_rejection_record_next_action() -> str:
    return NEXT_REQUIRED_ACTION


def build_c12_rejection_record(repo_root: Any = ".",
                               tracked_paths: list | None = None
                               ) -> dict[str, Any]:
    """Assemble the permanent C12 rejection / closeout record. Chain-gated on the
    pushed fee-honest replay review (must be FROZEN with
    structural_rejection_pressure=True and any_variant_passes_all_decisive_gates=
    False). Pure; no I/O."""
    record: dict[str, Any] = {
        "schema_version": RJ12_SCHEMA_VERSION,
        "label": RJ12_LABEL, "mode": RJ12_MODE,
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
        "rejection_reasons": list(REJECTION_REASONS),
        "evidence_headline": dict(EVIDENCE_HEADLINE),
        "claim_locks": list(CLAIM_LOCKS),
        "original_frozen_c12_result_unchanged": True,
        "current_loop_stage": "closed_rejected_kept_on_record",
        "human_review_required": False,
        "robustness_gate_locked": True,
        "relabel_gate_locked": True,
        "replay_gate_locked": True,
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
        "no_scheduler": True, "no_relabel": True, "no_new_replay": True,
        "no_robustness_run": True, "no_horizon_reselection": True,
        "no_asset_reselection": True, "no_regime_reselection": True,
        "no_parameter_fitting": True, "no_optimization": True,
        "no_detector_change": True, "no_profitability_claim": True,
        "no_downstream_gate_unlock": True,
    }

    # Chain gate: the pushed replay review must certify FROZEN with structural
    # rejection pressure and no variant passing the decisive gates.
    rr = build_c12_replay_review(repo_root, tracked_paths or [])
    record["replay_review_verdict"] = rr.get("verdict")
    record["replay_structural_rejection_pressure"] = rr.get(
        "structural_rejection_pressure")
    record["replay_any_variant_passes_all_decisive_gates"] = rr.get(
        "any_variant_passes_all_decisive_gates")
    if rr.get("verdict") != VERDICT_C12RR_FROZEN:
        record["verdict"] = VERDICT_RJ12_BLOCKED
        record["blockers"].append("replay_review_not_frozen")
        return record
    if rr.get("structural_rejection_pressure") is not True:
        record["verdict"] = VERDICT_RJ12_BLOCKED
        record["blockers"].append("replay_review_no_structural_rejection_pressure")
        return record
    if rr.get("any_variant_passes_all_decisive_gates") is not False:
        record["verdict"] = VERDICT_RJ12_BLOCKED
        record["blockers"].append("replay_had_a_passing_variant")
        return record

    record["verdict"] = VERDICT_RJ12_RECORDED
    return record


def validate_c12_rejection_record(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. RECORDED is valid only when the rejection status,
    kept-on-record-not-active (and not-parked-as-active) framing, the full pushed
    evidence chain, the replay negative-edge basis, locks, and capability locks
    are all intact."""
    failures: list = []
    if record.get("verdict") != VERDICT_RJ12_RECORDED:
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
    if record.get("original_frozen_c12_result_unchanged") is not True:
        failures.append("original_result_unchanged_flag_tampered")

    if record.get("head_at_replay_review") != HEAD_AT_REPLAY_REVIEW:
        failures.append("head_tampered")

    # Rejection basis: replay FROZEN + structural rejection + no passing variant.
    if record.get("replay_review_verdict") != VERDICT_C12RR_FROZEN:
        failures.append("replay_review_verdict_tampered")
    if record.get("replay_structural_rejection_pressure") is not True:
        failures.append("structural_rejection_pressure_tampered")
    if record.get("replay_any_variant_passes_all_decisive_gates") is not False:
        failures.append("variant_pass_flag_tampered")

    # Evidence chain must cite all five pushed stages with 40-hex commits.
    chain = record.get("pushed_evidence_chain") or []
    stages = {e.get("stage") for e in chain if isinstance(e, dict)}
    for required in ("family_proposal", "candidate_spec",
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

    if not record.get("rejection_reasons"):
        failures.append("rejection_reasons_missing")
    if not record.get("kept_on_record_as"):
        failures.append("kept_on_record_as_missing")
    eh = record.get("evidence_headline") or {}
    if eh.get("net_negative_all_variants") is not True:
        failures.append("evidence_net_negative_flag_tampered")
    if eh.get("worse_than_random_entry") is not True:
        failures.append("evidence_worse_than_random_flag_tampered")
    if eh.get("all_regimes_negative") is not True:
        failures.append("evidence_all_regimes_negative_flag_tampered")
    if eh.get("forward_oos_2026_positive") is not False:
        failures.append("evidence_forward_oos_flag_tampered")

    locks = record.get("scope_locks") or {}
    for key, val in locks.items():
        if val is not True:
            failures.append("scope_lock_false_%s" % key)
    for key in ("robustness_gate_locked", "relabel_gate_locked",
                "replay_gate_locked", "paper_trading_gate_locked",
                "micro_live_gate_locked", "live_gate_locked"):
        if record.get(key) is not True:
            failures.append("gate_flag_tampered_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    for required in ("no_profitability_claim",
                     "kept_on_record_not_active_candidate",
                     "not_parked_as_active",
                     "no_relabel_of_original_result", "no_new_replay",
                     "worse_than_random_entry_disclosed"):
        if required not in (record.get("claim_locks") or []):
            failures.append("claim_lock_missing_%s" % required)

    for banned in ("APPROVE", "PAPER", "LIVE", "EXECUTE", "BROKER", "ORDER",
                   "PROMOTE", "UNLOCK"):
        if banned in NEXT_REQUIRED_ACTION.upper():
            failures.append("next_action_banned_token_%s" % banned)

    return {"valid": not failures, "failures": failures}
