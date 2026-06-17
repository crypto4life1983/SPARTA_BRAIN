"""Candidate #14 (conviction_bar_follow_through_v1) formal rejection / closeout
record.

RESEARCH RECORD ONLY. This is the permanent ledger entry that closes Candidate
#14 as a REJECTED-KEPT-ON-RECORD family after it passed family proposal,
candidate spec, detector dry-run, real-candle labels (the structural sample-size
gate -- the C13 lesson -- PASSED) and then FAILED the fee+slippage-honest replay.

C14 is the STRONGEST candidate so far and its positives are preserved on record:
it is the FIRST SPARTA candidate to BEAT a matched random-entry baseline (every
variant; percentile 0.61 / 0.835 / 0.905), it is net-positive after 37 bps at
1.5R (+1.3R) and 2R (+13.5R), the 2R variant is positive across bull/bear/chop,
and the bear regime is positive in all variants. BUT it FAILED the decisive
gates: it LOSES to buy-and-hold in every variant (B&H +39.7R), the forward-OOS
2026 window is net-negative in every variant (-2.0R / -3.7R / -3.7R), and target
capture does not dominate (hits << horizon exits) -> STRUCTURAL REJECTION
PRESSURE.

Conclusion (recorded precisely): "Conviction-bar follow-through appears to
contain timing information, but the timing advantage was insufficient to produce
a durable tradeable edge after fees and forward validation."

Pure, in-memory record: NO file I/O, NO network, NO trading, NO PnL, NO new
replay, NO relabel, NO data fetch, NO robustness, NO portfolio compute, NO
optimization, NO one-edit, NO downstream gate unlock. It does NOT approve paper or
live, does NOT claim profitability, and does NOT keep C14 as an active candidate
or park it as active -- it is kept ONLY as a historical lesson / research seed.

Chain gate: build_c14_rejection_record() requires build_c14_replay_review() to
return C14_REPLAY_RESULTS_FROZEN_FOR_HUMAN_REVIEW carrying
structural_rejection_pressure=True and any_variant_passes_all_decisive_gates=
False; any other state short-circuits to BLOCKED.

Pushed evidence trail (origin/master): family proposal 127d959a -> candidate spec
563b9c32 -> detector dry-run 989f2ead -> real-candle labels bc69e4f0. The
fee-honest replay review is BUILT LOCALLY and committed PENDING at the time this
record was authored; it is chain-gated here on build_c14_replay_review and
anchored to the SHA-pinned replay artifacts (recorded for honesty).
"""
from __future__ import annotations

from typing import Any

from sparta_commander.conviction_bar_follow_through_v1_replay_results_review_contract import (  # noqa: E501
    EXPECTED_REPLAY_LEDGER_SHA256,
    EXPECTED_REPLAY_SUMMARY_SHA256,
    VERDICT_C14RR_FROZEN,
    build_c14_replay_review,
)

RJ14_SCHEMA_VERSION = 1
RJ14_MODE = "RESEARCH_ONLY"
CANDIDATE_ID = "CONVICTION_BAR_FOLLOW_THROUGH_V1"
CANDIDATE_FAMILY = "conviction_bar_follow_through"
CANDIDATE_NUMBER = 14

VERDICT_RJ14_RECORDED = (
    "C14_REJECTED_KEPT_ON_RECORD_FAILED_FEE_HONEST_REPLAY")
VERDICT_RJ14_BLOCKED = "C14_REJECTION_RECORD_BLOCKED"
REJECTION_STATUS = "REJECTED_KEPT_ON_RECORD"
NEXT_REQUIRED_ACTION = (
    "NONE__C14_CLOSED__KEPT_ON_RECORD_AS_TIMING_SIGNAL_WITHOUT_DURABLE_EDGE_"
    "RESEARCH_LESSON")

HEAD_AT_LABELS_REVIEW = "bc69e4f0b0cf1e63ed00d6cb02b991f3d9d22ac6"

# The precise recorded conclusion (verbatim, must never be altered).
CONCLUSION = (
    "Conviction-bar follow-through appears to contain timing information, but the "
    "timing advantage was insufficient to produce a durable tradeable edge after "
    "fees and forward validation.")

# Full pushed evidence trail (each is a committed + pushed gate on master).
PUSHED_EVIDENCE_CHAIN = (
    {"stage": "family_proposal",
     "commit": "127d959a0aea695ba42993a1fb046a4c2c96823a",
     "result": ("materially-new conviction-bar follow-through family vs C1-C13; "
                "structural labels sample-size gate + forward-OOS + regime "
                "symmetry + must-beat buy-and-hold AND random-entry + target-"
                "capture dominance as hard gates "
                "(CANDIDATE_14_FAMILY_PROPOSAL_READY)")},
    {"stage": "candidate_spec",
     "commit": "563b9c320ba12977c7b0112f07341ecd41b9b8af",
     "result": ("frozen spec: TR>=1.5*ATR & top-quartile close; ATR(14) stop; "
                "1R/1.5R/2R; 81 bps floor; <=2-bar hold; per-asset non-overlap; "
                "37 bps; structural sample-size gate FIRST "
                "(CANDIDATE_14_SPEC_READY)")},
    {"stage": "detector_spec_and_synthetic_dry_run",
     "commit": "989f2ead937d368061b879c599edd4faf5110bba",
     "result": ("synthetic dry-run proofs of the conviction-bar geometry + exit "
                "handling + non-overlap (CANDIDATE_14_DETECTOR_DRY_RUN_READY)")},
    {"stage": "real_candle_labels_review",
     "commit": "bc69e4f0b0cf1e63ed00d6cb02b991f3d9d22ac6",
     "result": ("347 accepted labels across BTC/ETH/SOL; the STRUCTURAL "
                "sample-size gate PASSED (>=100 total, >=20 per asset, >=20 per "
                "regime, forward-OOS 2026 populated) "
                "(C14_REAL_CANDLE_LABELS_FROZEN_FOR_HUMAN_REVIEW)")},
)

# The fee-honest replay review (built locally; commit PENDING at authoring time;
# chain-gated here and anchored to the immutable replay-artifact SHAs).
REPLAY_RESULTS_REVIEW_STAGE = {
    "stage": "fee_slippage_honest_replay_review",
    "pushed_separately_on_origin": False,
    "earliest_pushed_ancestor_commit":
        "bc69e4f0b0cf1e63ed00d6cb02b991f3d9d22ac6",
    "replay_ledger_sha256": EXPECTED_REPLAY_LEDGER_SHA256,
    "replay_summary_sha256": EXPECTED_REPLAY_SUMMARY_SHA256,
    "chain_gated_on": ("build_c14_replay_review FROZEN + "
                       "structural_rejection_pressure True + "
                       "any_variant_passes_all_decisive_gates False"),
    "note": ("the replay-results review unit was built locally and its commit "
             "was pending when this rejection record was authored; the evidence "
             "is anchored to the SHA-pinned replay artifacts -- recorded for "
             "honesty"),
}

# KEY POSITIVE FINDINGS -- preserved exactly as required.
KEY_POSITIVE_FINDINGS = (
    "First SPARTA candidate to BEAT the matched random-entry baseline (every "
    "variant; percentile 0.61 / 0.835 / 0.905) -- the conviction-bar signal "
    "carries genuine entry-timing information.",
    "Net-positive after 37 bps all-in costs at 1.5R (+1.29R) and 2R (+13.54R).",
    "The 2R variant is net-positive across bull (+3.25R), bear (+2.20R) AND chop "
    "(+8.09R) -- regime-symmetric at 2R.",
    "Bear regime is net-positive in ALL variants (+2.27R / +0.85R / +2.20R).",
)

# DECISIVE REJECTION REASONS -- preserved exactly as required.
REJECTION_REASONS = (
    "Failed the buy-and-hold comparison in EVERY variant: matched buy-and-hold "
    "is +39.70R vs the strategy's -15.58R / +1.29R / +13.54R -- the absolute "
    "return is market CARRY that passive holding captures more cheaply.",
    "Forward-OOS 2026 is NET-NEGATIVE in EVERY variant (-2.03R / -3.72R / "
    "-3.72R) -- the edge does not continue forward.",
    "Target-capture dominance FAILED in every variant: hits (53-108) are far "
    "fewer than horizon exits (140-191); 2R is also horizon-dominated (55%).",
    "Structural rejection pressure remains TRUE: no variant passes ALL the "
    "decisive gates, so the candidate is not promotable.",
    "'Beats random but loses to buy-and-hold' is the carry signature: a real "
    "entry-timing signal whose money is still just long carry.",
)

KEPT_ON_RECORD_AS = (
    "Historical lesson: a candidate can carry genuine ENTRY-TIMING information "
    "(beat random entry) and still NOT be a tradeable edge -- the timing "
    "advantage must beat BUY-AND-HOLD and survive forward-OOS, not merely beat "
    "random. C14 is the cleanest demonstration of the 'beats random, loses to "
    "buy-and-hold' carry signature.",
    "Research seed: keep must-beat-buy-and-hold AND must-beat-random-entry as "
    "SEPARATE hard gates -- beating random alone is necessary but not "
    "sufficient; the buy-and-hold and forward-OOS gates are what separate a "
    "timing signal from a durable edge.",
)

EVIDENCE_HEADLINE = {
    "accepted_labels": 347,
    "resolved_trades": 346,
    "symbols": ["BTCUSD", "ETHUSD", "SOLUSD"],
    "labels_sample_size_gate_passed": True,
    "all_in_cost_bps": 37.0,
    "holding_horizon_bars": 2,
    "buy_and_hold_net_all_in_total": 39.6973,
    "net_r_all_in_1r": -15.5789,
    "net_r_all_in_1_5r": 1.2914,
    "net_r_all_in_2r": 13.544,
    "beats_random_entry_all_variants": True,
    "random_entry_percentile_1r_1_5r_2r": [0.61, 0.835, 0.905],
    "loses_to_buy_and_hold_all_variants": True,
    "forward_oos_2026_net_r_all_variants": [-2.0319, -3.7161, -3.7161],
    "forward_oos_2026_positive_any_variant": False,
    "target_capture_dominates_any_variant": False,
    "regime_symmetric_at_2r": True,
    "bear_regime_net_positive_all_variants": True,
}

CLAIM_LOCKS = (
    "no_profitability_claim", "no_paper_approval", "no_live_approval",
    "no_execution_approval", "no_capital_deployment", "no_portfolio_allocation",
    "kept_on_record_not_active_candidate", "not_parked_as_active",
    "no_relabel_of_original_result", "no_new_replay", "no_optimization",
    "no_one_edit_invoked", "no_robustness_promotion",
    "original_frozen_c14_result_unchanged",
    "fee_honest_replay_failure_is_the_rejection_basis",
    "beats_random_entry_positive_preserved",
    "loses_to_buy_and_hold_disclosed",
    "negative_forward_oos_disclosed",
    "conclusion_recorded_precisely",
)

RJ14_LABEL = (
    "SPARTA Candidate #14 FORMAL REJECTION RECORD (READ-ONLY, RESEARCH ONLY). "
    "REJECTED_KEPT_ON_RECORD: passed proposal/spec/detector/labels (347 labels, "
    "structural sample-size gate PASS) and is the FIRST candidate to BEAT "
    "random-entry, net-positive at 1.5R/2R, 2R regime-symmetric -- but FAILED "
    "the fee-honest replay (loses to buy-and-hold every variant, forward-OOS "
    "2026 negative, target capture does not dominate). NOT AN ACTIVE CANDIDATE. "
    "NOT PARKED AS ACTIVE. NOT A PROFITABILITY CLAIM. NOT AN APPROVAL FOR PAPER "
    "OR LIVE. KEPT ONLY AS A HISTORICAL LESSON / RESEARCH SEED."
)

_CAPABILITY_FLAGS_FALSE = (
    "is_active_candidate", "keeps_as_active_candidate", "parks_as_active",
    "promotes_to_robustness", "promotes_to_paper", "promotes_to_live",
    "promotes_gate", "unlocks_downstream_gate", "relabels_original_result",
    "runs_new_replay", "reselects_threshold", "reselects_close_location",
    "fits_parameters", "optimizes", "uses_one_edit_allowance",
    "runs_detection_now", "runs_replay_now", "runs_robustness",
    "runs_portfolio_compute", "scores_live", "stages_data_now", "fetches_data",
    "mutates_source_data", "calls_api", "uses_network", "uses_credentials",
    "uses_wallet", "uses_account", "connects_broker", "connects_exchange",
    "uses_real_money", "contains_order_logic",
    "contains_portfolio_allocation_logic", "deploys_capital", "starts_scheduler",
    "sends_notifications", "auto_commits", "auto_pushes", "modifies_frozen_labels",
    "modifies_replay_artifacts", "computes_live_pnl",
    "authorizes_paper_execution", "authorizes_micro_live",
    "authorizes_live_trading", "claims_profitability", "claims_edge",
    "executes", "writes_files",
)


def get_candidate_14_rejection_record_label() -> str:
    return RJ14_LABEL


def get_candidate_14_rejection_record_next_action() -> str:
    return NEXT_REQUIRED_ACTION


def build_c14_rejection_record(repo_root: Any = ".",
                               tracked_paths: list | None = None
                               ) -> dict[str, Any]:
    """Assemble the permanent C14 rejection / closeout record. Chain-gated on the
    fee-honest replay review (must be FROZEN with structural_rejection_pressure=
    True and any_variant_passes_all_decisive_gates=False). Pure; no I/O."""
    record: dict[str, Any] = {
        "schema_version": RJ14_SCHEMA_VERSION,
        "label": RJ14_LABEL, "mode": RJ14_MODE,
        "lane": "crypto_d1_auto_research",
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "candidate_number": CANDIDATE_NUMBER,
        "verdict": None, "blockers": [], "failures": [],
        "rejection_status": REJECTION_STATUS,
        "conclusion": CONCLUSION,
        "is_active_candidate": False,
        "parked_as_active": False,
        "kept_on_record": True,
        "kept_on_record_as": list(KEPT_ON_RECORD_AS),
        "head_at_labels_review": HEAD_AT_LABELS_REVIEW,
        "pushed_evidence_chain": [dict(e) for e in PUSHED_EVIDENCE_CHAIN],
        "replay_results_review_stage": dict(REPLAY_RESULTS_REVIEW_STAGE),
        "key_positive_findings": list(KEY_POSITIVE_FINDINGS),
        "rejection_reasons": list(REJECTION_REASONS),
        "evidence_headline": dict(EVIDENCE_HEADLINE),
        "claim_locks": list(CLAIM_LOCKS),
        "original_frozen_c14_result_unchanged": True,
        "added_to_rejected_family_ledger": True,
        "current_loop_stage": "closed_rejected_kept_on_record",
        "human_review_required": False,
        "robustness_gate_locked": True,
        "relabel_gate_locked": True,
        "replay_gate_locked": True,
        "one_edit_gate_locked": True,
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
        "no_one_edit": True, "no_robustness_run": True,
        "no_threshold_reselection": True, "no_close_location_reselection": True,
        "no_parameter_fitting": True, "no_optimization": True,
        "no_detector_change": True, "no_profitability_claim": True,
        "no_downstream_gate_unlock": True,
    }

    # Chain gate: the replay review must certify FROZEN with structural rejection
    # pressure and no variant passing the decisive gates.
    rr = build_c14_replay_review(repo_root, tracked_paths or [])
    record["replay_review_verdict"] = rr.get("verdict")
    record["replay_structural_rejection_pressure"] = rr.get(
        "structural_rejection_pressure")
    record["replay_any_variant_passes_all_decisive_gates"] = rr.get(
        "any_variant_passes_all_decisive_gates")
    record["replay_beats_random_entry_any_variant"] = (
        rr.get("decisive_gate_results") or {}).get(
            "beats_random_entry_any_variant")
    if rr.get("verdict") != VERDICT_C14RR_FROZEN:
        record["verdict"] = VERDICT_RJ14_BLOCKED
        record["blockers"].append("replay_review_not_frozen")
        return record
    if rr.get("structural_rejection_pressure") is not True:
        record["verdict"] = VERDICT_RJ14_BLOCKED
        record["blockers"].append("replay_review_no_structural_rejection_pressure")
        return record
    if rr.get("any_variant_passes_all_decisive_gates") is not False:
        record["verdict"] = VERDICT_RJ14_BLOCKED
        record["blockers"].append("replay_had_a_passing_variant")
        return record

    record["verdict"] = VERDICT_RJ14_RECORDED
    return record


def validate_c14_rejection_record(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. RECORDED is valid only when the rejection status,
    kept-on-record-not-active framing, the full pushed evidence chain, the replay
    failure basis, the preserved positives + reasons + verbatim conclusion, the
    rejected-ledger flag, locks, and capability locks are all intact."""
    failures: list = []
    if record.get("verdict") != VERDICT_RJ14_RECORDED:
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
    if record.get("original_frozen_c14_result_unchanged") is not True:
        failures.append("original_result_unchanged_flag_tampered")
    if record.get("added_to_rejected_family_ledger") is not True:
        failures.append("not_added_to_rejected_ledger")
    if record.get("conclusion") != CONCLUSION:
        failures.append("conclusion_text_altered")

    if record.get("head_at_labels_review") != HEAD_AT_LABELS_REVIEW:
        failures.append("head_tampered")

    # Rejection basis: replay FROZEN + structural rejection + no passing variant.
    if record.get("replay_review_verdict") != VERDICT_C14RR_FROZEN:
        failures.append("replay_review_verdict_tampered")
    if record.get("replay_structural_rejection_pressure") is not True:
        failures.append("structural_rejection_pressure_tampered")
    if record.get("replay_any_variant_passes_all_decisive_gates") is not False:
        failures.append("variant_pass_flag_tampered")
    # the beats-random positive must remain preserved
    if record.get("replay_beats_random_entry_any_variant") is not True:
        failures.append("beats_random_positive_cleared")

    # Evidence chain must cite all four pushed stages with 40-hex commits.
    chain = record.get("pushed_evidence_chain") or []
    stages = {e.get("stage") for e in chain if isinstance(e, dict)}
    for required in ("family_proposal", "candidate_spec",
                     "detector_spec_and_synthetic_dry_run",
                     "real_candle_labels_review"):
        if required not in stages:
            failures.append("evidence_chain_missing_%s" % required)
    for e in chain:
        if isinstance(e, dict):
            c = e.get("commit", "")
            if not (isinstance(c, str) and len(c) == 40):
                failures.append("evidence_chain_bad_commit_%s" % e.get("stage"))
    # The replay-review stage must be cited + SHA-anchored.
    rs = record.get("replay_results_review_stage") or {}
    if rs.get("stage") != "fee_slippage_honest_replay_review":
        failures.append("replay_stage_missing")
    if rs.get("replay_ledger_sha256") != EXPECTED_REPLAY_LEDGER_SHA256:
        failures.append("replay_ledger_sha_tampered")
    if rs.get("replay_summary_sha256") != EXPECTED_REPLAY_SUMMARY_SHA256:
        failures.append("replay_summary_sha_tampered")

    if not record.get("key_positive_findings"):
        failures.append("key_positive_findings_missing")
    if not record.get("rejection_reasons"):
        failures.append("rejection_reasons_missing")
    if not record.get("kept_on_record_as"):
        failures.append("kept_on_record_as_missing")
    eh = record.get("evidence_headline") or {}
    if eh.get("beats_random_entry_all_variants") is not True:
        failures.append("evidence_beats_random_flag_tampered")
    if eh.get("loses_to_buy_and_hold_all_variants") is not True:
        failures.append("evidence_loses_bh_flag_tampered")
    if eh.get("forward_oos_2026_positive_any_variant") is not False:
        failures.append("evidence_forward_oos_flag_tampered")
    if eh.get("target_capture_dominates_any_variant") is not False:
        failures.append("evidence_target_capture_flag_tampered")

    locks = record.get("scope_locks") or {}
    for key, val in locks.items():
        if val is not True:
            failures.append("scope_lock_false_%s" % key)
    for key in ("robustness_gate_locked", "relabel_gate_locked",
                "replay_gate_locked", "one_edit_gate_locked",
                "paper_trading_gate_locked", "micro_live_gate_locked",
                "live_gate_locked"):
        if record.get(key) is not True:
            failures.append("gate_flag_tampered_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    for required in ("no_profitability_claim",
                     "kept_on_record_not_active_candidate",
                     "not_parked_as_active", "no_new_replay", "no_one_edit_invoked",
                     "beats_random_entry_positive_preserved",
                     "loses_to_buy_and_hold_disclosed",
                     "conclusion_recorded_precisely"):
        if required not in (record.get("claim_locks") or []):
            failures.append("claim_lock_missing_%s" % required)

    for banned in ("APPROVE", "PAPER", "LIVE", "EXECUTE", "BROKER", "ORDER",
                   "PROMOTE", "UNLOCK"):
        if banned in NEXT_REQUIRED_ACTION.upper():
            failures.append("next_action_banned_token_%s" % banned)

    return {"valid": not failures, "failures": failures}
