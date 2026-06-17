"""Candidate #13 (lead_lag_propagation_continuation_v1) formal rejection /
closeout record.

RESEARCH RECORD ONLY. This is the permanent ledger entry that closes Candidate
#13 as a REJECTED-KEPT-ON-RECORD family after it passed family proposal,
candidate spec, and detector dry-run but then FAILED the real-candle labels-stage
structural checks: the confirmed-leader-move + follower-lag trigger was too RARE
on daily data -- only 41 accepted labels (< the 100 minimum), ETHUSD 18 (< 20),
all three regimes under the 20 minimum (bear 4 / bull 19 / chop 18), and ZERO
forward-OOS 2026 labels. The labels-stage battery rejected it BEFORE any replay.

The human DECLINED the single one-edit allowance (lowering the z-threshold or lag
margin to manufacture more signals would risk curve-fitting an already too-rare
trigger). Pure, in-memory record: NO one-edit, NO file I/O, NO network, NO
trading, NO PnL, NO replay, NO relabel, NO data fetch, NO robustness, NO
portfolio compute, NO downstream gate unlock. It does NOT approve paper or live,
does NOT claim profitability, and does NOT keep C13 as an active candidate or
park it as active -- it is kept ONLY as a historical lesson / research seed: the
labels-stage structural battery (min sample/coverage + a reserved forward-OOS
window) is the EARLIEST and cheapest rejection gate and correctly killed an
under-powered signal before any replay spend.

Chain gate: build_c13_rejection_record() requires build_c13_labels_review() to
return C13_REAL_CANDLE_LABELS_STRUCTURAL_REJECTION carrying
structural_rejection_pressure=True and sample_size_passed=False; any other state
short-circuits to BLOCKED.

Full pushed evidence trail (origin/master), proposal -> ... -> labels failure
(C13 never reached the replay stage):
  * family proposal             -> ae97e896
  * candidate spec              -> 74f4906a
  * detector spec + synthetic   -> d32047c1
  * real-candle labels review   -> c976ed87 (41 labels; structural rejection)
"""
from __future__ import annotations

from typing import Any

from sparta_commander.lead_lag_propagation_continuation_v1_real_candle_labels_review_contract import (  # noqa: E501
    VERDICT_C13L_STRUCTURAL_REJECTION,
    build_c13_labels_review,
)

RJ13_SCHEMA_VERSION = 1
RJ13_MODE = "RESEARCH_ONLY"
CANDIDATE_ID = "LEAD_LAG_PROPAGATION_CONTINUATION_V1"
CANDIDATE_FAMILY = "lead_lag_propagation_continuation"
CANDIDATE_NUMBER = 13

VERDICT_RJ13_RECORDED = (
    "C13_REJECTED_KEPT_ON_RECORD_FAILED_LABELS_STRUCTURAL_CHECKS")
VERDICT_RJ13_BLOCKED = "C13_REJECTION_RECORD_BLOCKED"
REJECTION_STATUS = "REJECTED_KEPT_ON_RECORD"
NEXT_REQUIRED_ACTION = (
    "NONE__C13_CLOSED__KEPT_ON_RECORD_AS_UNDERPOWERED_SIGNAL_LABELS_STAGE_"
    "REJECTION_RESEARCH_LESSON")

HEAD_AT_LABELS_REVIEW = "c976ed87d1fc1bb97c3901883785ee87b5eccb4d"

# Full pushed evidence trail (each is a committed + pushed gate on master).
# C13 never reached the replay stage -- the labels-stage battery rejected it.
PUSHED_EVIDENCE_CHAIN = (
    {"stage": "family_proposal",
     "commit": "ae97e896ba2fc924df82e97beafb2ecdbaa4c739",
     "result": ("materially-new cross-asset lead-lag propagation family vs "
                "C1-C12; forward-OOS + regime symmetry + must-beat buy-and-hold "
                "AND random-entry AND buy-the-leader + target-capture dominance "
                "as hard gates (CANDIDATE_13_FAMILY_PROPOSAL_READY)")},
    {"stage": "candidate_spec",
     "commit": "74f4906a282756168ce4838383a18068d9d3591c",
     "result": ("frozen spec: BTC leader / ETH-SOL followers; r_L>0 & z_L>=1.5; "
                "lag r_F<0.5*r_L; ATR(14) stop; 1R/1.5R/2R; 81 bps floor; "
                "<=2-bar hold; per-follower non-overlap; 37 bps; 3 baselines "
                "(CANDIDATE_13_SPEC_READY)")},
    {"stage": "detector_spec_and_synthetic_dry_run",
     "commit": "d32047c124168b3e478d7e181dfe6155d14d3604",
     "result": ("synthetic dry-run proofs of the leader-move + follower-lag "
                "geometry + exit handling + non-overlap + leader!=follower "
                "(CANDIDATE_13_DETECTOR_DRY_RUN_READY)")},
    {"stage": "real_candle_labels_review",
     "commit": "c976ed87d1fc1bb97c3901883785ee87b5eccb4d",
     "result": ("ONLY 41 accepted labels (ETH 18 / SOL 23) over 2020-2026: "
                "total < 100, ETH < 20, ALL regimes < 20 (bear 4/bull 19/chop "
                "18), ZERO forward-OOS 2026 -> STRUCTURAL REJECTION "
                "(C13_REAL_CANDLE_LABELS_STRUCTURAL_REJECTION)")},
)

REJECTION_REASONS = (
    "Real-candle labels produced only 41 accepted labels, below the required "
    "100 minimum -- the confirmed-leader-move (z>=1.5) + follower-lag trigger is "
    "too RARE on daily data.",
    "ETHUSD follower had only 18 accepted labels, below the required 20 "
    "per-follower minimum.",
    "Bull (19), bear (4) AND chop (18) regimes ALL had fewer than the required "
    "20 labels -- no regime had adequate coverage.",
    "There were ZERO forward-OOS 2026 labels -- the reserved forward window "
    "could not be populated, so forward continuation could never be tested.",
    "The labels-stage structural battery FAILED before any replay -- the "
    "earliest, cheapest rejection gate did its job.",
    "Lowering the z-threshold or lag margin now (the single one-edit allowance) "
    "would risk CURVE-FITTING an already too-rare trigger; the human DECLINED "
    "the one-edit.",
    "Therefore C13 is NOT a viable candidate and must not continue to replay or "
    "promotion.",
)

KEPT_ON_RECORD_AS = (
    "Historical lesson: the labels-stage structural battery (minimum total / "
    "per-follower / per-regime sample + a reserved forward-OOS window) is the "
    "EARLIEST and cheapest rejection gate -- it killed an under-powered signal "
    "BEFORE any replay spend, the first candidate rejected at the labels stage "
    "(C10/C11/C12 all reached replay first).",
    "Research seed: a trigger that is too RARE to populate >=100 total / >=20 "
    "per-asset / >=20 per-regime labels AND a forward-OOS window is "
    "disqualified at the labels stage; manufacturing signals by loosening the "
    "threshold is curve-fitting and is declined, not pursued.",
)

EVIDENCE_HEADLINE = {
    "accepted_labels": 41,
    "min_labels_total": 100,
    "followers": ["ETHUSD", "SOLUSD"],
    "per_follower": {"ETHUSD": 18, "SOLUSD": 23},
    "min_per_follower": 20,
    "per_regime": {"bull": 19, "bear": 4, "chop": 18},
    "min_per_regime": 20,
    "forward_oos_2026_label_count": 0,
    "total_below_minimum": True,
    "eth_below_per_follower_minimum": True,
    "all_regimes_below_minimum": True,
    "zero_forward_oos_labels": True,
    "labels_stage_structural_battery_failed": True,
    "reached_replay_stage": False,
    "one_edit_allowance_invoked": False,
}

CLAIM_LOCKS = (
    "no_profitability_claim", "no_paper_approval", "no_live_approval",
    "no_execution_approval", "no_capital_deployment", "no_portfolio_allocation",
    "kept_on_record_not_active_candidate", "not_parked_as_active",
    "no_one_edit_invoked", "no_relabel_of_original_result", "no_replay",
    "no_robustness", "original_frozen_c13_result_unchanged",
    "labels_stage_structural_rejection_is_the_rejection_basis",
    "under_powered_sample_disclosed", "zero_forward_oos_labels_disclosed",
)

RJ13_LABEL = (
    "SPARTA Candidate #13 FORMAL REJECTION RECORD (READ-ONLY, RESEARCH ONLY). "
    "REJECTED_KEPT_ON_RECORD: passed proposal/spec/detector but FAILED the "
    "real-candle LABELS-stage structural checks -- only 41 labels (ETH 18 < 20), "
    "all regimes < 20, ZERO forward-OOS 2026 -> under-powered, too-rare signal, "
    "rejected BEFORE replay. One-edit allowance DECLINED (anti-curve-fit). NOT "
    "AN ACTIVE CANDIDATE. NOT PARKED AS ACTIVE. NOT A PROFITABILITY CLAIM. NOT "
    "AN APPROVAL FOR PAPER OR LIVE. KEPT ONLY AS A HISTORICAL LESSON / RESEARCH "
    "SEED."
)

_CAPABILITY_FLAGS_FALSE = (
    "is_active_candidate", "keeps_as_active_candidate", "parks_as_active",
    "invokes_one_edit_allowance", "uses_one_edit_allowance",
    "promotes_to_replay", "promotes_to_robustness", "promotes_to_paper",
    "promotes_to_live", "promotes_gate", "unlocks_downstream_gate",
    "relabels_original_result", "runs_replay", "runs_new_labels",
    "reselects_z_threshold", "reselects_lag_margin", "fits_parameters",
    "optimizes", "runs_detection_now", "runs_replay_now", "runs_robustness",
    "runs_portfolio_compute", "scores_live", "stages_data_now", "fetches_data",
    "mutates_source_data", "calls_api", "uses_network", "uses_credentials",
    "uses_wallet", "uses_account", "connects_broker", "connects_exchange",
    "uses_real_money", "contains_order_logic",
    "contains_portfolio_allocation_logic", "deploys_capital", "starts_scheduler",
    "sends_notifications", "auto_commits", "auto_pushes", "modifies_frozen_labels",
    "computes_live_pnl", "authorizes_paper_execution", "authorizes_micro_live",
    "authorizes_live_trading", "claims_profitability", "claims_edge",
    "executes", "writes_files",
)


def get_candidate_13_rejection_record_label() -> str:
    return RJ13_LABEL


def get_candidate_13_rejection_record_next_action() -> str:
    return NEXT_REQUIRED_ACTION


def build_c13_rejection_record(repo_root: Any = ".",
                               tracked_paths: list | None = None
                               ) -> dict[str, Any]:
    """Assemble the permanent C13 rejection / closeout record. Chain-gated on the
    pushed C13 labels review (must be STRUCTURAL_REJECTION with
    structural_rejection_pressure=True and sample_size_passed=False). Pure; no
    I/O."""
    record: dict[str, Any] = {
        "schema_version": RJ13_SCHEMA_VERSION,
        "label": RJ13_LABEL, "mode": RJ13_MODE,
        "lane": "crypto_d1_auto_research",
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "candidate_number": CANDIDATE_NUMBER,
        "verdict": None, "blockers": [], "failures": [],
        "rejection_status": REJECTION_STATUS,
        "rejection_stage": "real_candle_labels_review",
        "reached_replay_stage": False,
        "one_edit_allowance_invoked": False,
        "is_active_candidate": False,
        "parked_as_active": False,
        "kept_on_record": True,
        "kept_on_record_as": list(KEPT_ON_RECORD_AS),
        "head_at_labels_review": HEAD_AT_LABELS_REVIEW,
        "pushed_evidence_chain": [dict(e) for e in PUSHED_EVIDENCE_CHAIN],
        "rejection_reasons": list(REJECTION_REASONS),
        "evidence_headline": dict(EVIDENCE_HEADLINE),
        "claim_locks": list(CLAIM_LOCKS),
        "original_frozen_c13_result_unchanged": True,
        "current_loop_stage": "closed_rejected_kept_on_record",
        "human_review_required": False,
        "one_edit_gate_locked": True,
        "labels_relabel_gate_locked": True,
        "replay_gate_locked": True,
        "robustness_gate_locked": True,
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
        "no_scheduler": True, "no_relabel": True, "no_one_edit": True,
        "no_replay": True, "no_robustness_run": True,
        "no_z_threshold_reselection": True, "no_lag_margin_reselection": True,
        "no_parameter_fitting": True, "no_optimization": True,
        "no_detector_change": True, "no_profitability_claim": True,
        "no_downstream_gate_unlock": True,
    }

    # Chain gate: the pushed labels review must certify STRUCTURAL_REJECTION with
    # the failing facts intact.
    lr = build_c13_labels_review(repo_root, tracked_paths or [])
    record["labels_review_verdict"] = lr.get("verdict")
    record["labels_structural_rejection_pressure"] = lr.get(
        "structural_rejection_pressure")
    record["labels_sample_size_passed"] = lr.get("sample_size_passed")
    if lr.get("verdict") != VERDICT_C13L_STRUCTURAL_REJECTION:
        record["verdict"] = VERDICT_RJ13_BLOCKED
        record["blockers"].append("labels_review_not_structural_rejection")
        return record
    if lr.get("structural_rejection_pressure") is not True:
        record["verdict"] = VERDICT_RJ13_BLOCKED
        record["blockers"].append("labels_no_structural_rejection_pressure")
        return record
    if lr.get("sample_size_passed") is not False:
        record["verdict"] = VERDICT_RJ13_BLOCKED
        record["blockers"].append("labels_sample_size_unexpectedly_passed")
        return record

    record["verdict"] = VERDICT_RJ13_RECORDED
    return record


def validate_c13_rejection_record(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. RECORDED is valid only when the rejection status,
    kept-on-record-not-active (and not-parked-as-active) framing, the declined
    one-edit, the full pushed evidence chain, the labels-stage structural-
    rejection basis, locks, and capability locks are all intact."""
    failures: list = []
    if record.get("verdict") != VERDICT_RJ13_RECORDED:
        failures.append("verdict_not_recorded")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("rejection_status") != REJECTION_STATUS:
        failures.append("rejection_status_tampered")
    if record.get("rejection_stage") != "real_candle_labels_review":
        failures.append("rejection_stage_tampered")
    if record.get("reached_replay_stage") is not False:
        failures.append("reached_replay_flag_tampered")
    if record.get("one_edit_allowance_invoked") is not False:
        failures.append("one_edit_invoked_flag_tampered")
    if record.get("is_active_candidate") is not False:
        failures.append("is_active_candidate_must_be_false")
    if record.get("parked_as_active") is not False:
        failures.append("parked_as_active_must_be_false")
    if record.get("kept_on_record") is not True:
        failures.append("kept_on_record_must_be_true")
    if record.get("original_frozen_c13_result_unchanged") is not True:
        failures.append("original_result_unchanged_flag_tampered")

    if record.get("head_at_labels_review") != HEAD_AT_LABELS_REVIEW:
        failures.append("head_tampered")

    # Rejection basis: labels STRUCTURAL_REJECTION + pressure + sample failed.
    if record.get("labels_review_verdict") != VERDICT_C13L_STRUCTURAL_REJECTION:
        failures.append("labels_review_verdict_tampered")
    if record.get("labels_structural_rejection_pressure") is not True:
        failures.append("structural_rejection_pressure_tampered")
    if record.get("labels_sample_size_passed") is not False:
        failures.append("sample_size_pass_flag_tampered")

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

    if not record.get("rejection_reasons"):
        failures.append("rejection_reasons_missing")
    if not record.get("kept_on_record_as"):
        failures.append("kept_on_record_as_missing")
    eh = record.get("evidence_headline") or {}
    for key in ("total_below_minimum", "eth_below_per_follower_minimum",
                "all_regimes_below_minimum", "zero_forward_oos_labels",
                "labels_stage_structural_battery_failed"):
        if eh.get(key) is not True:
            failures.append("evidence_flag_tampered_%s" % key)
    if eh.get("reached_replay_stage") is not False:
        failures.append("evidence_reached_replay_tampered")
    if eh.get("one_edit_allowance_invoked") is not False:
        failures.append("evidence_one_edit_tampered")

    locks = record.get("scope_locks") or {}
    for key, val in locks.items():
        if val is not True:
            failures.append("scope_lock_false_%s" % key)
    for key in ("one_edit_gate_locked", "labels_relabel_gate_locked",
                "replay_gate_locked", "robustness_gate_locked",
                "paper_trading_gate_locked", "micro_live_gate_locked",
                "live_gate_locked"):
        if record.get(key) is not True:
            failures.append("gate_flag_tampered_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    for required in ("no_profitability_claim",
                     "kept_on_record_not_active_candidate",
                     "not_parked_as_active", "no_one_edit_invoked",
                     "no_relabel_of_original_result", "no_replay",
                     "labels_stage_structural_rejection_is_the_rejection_basis"):
        if required not in (record.get("claim_locks") or []):
            failures.append("claim_lock_missing_%s" % required)

    for banned in ("APPROVE", "PAPER", "LIVE", "EXECUTE", "BROKER", "ORDER",
                   "PROMOTE", "UNLOCK"):
        if banned in NEXT_REQUIRED_ACTION.upper():
            failures.append("next_action_banned_token_%s" % banned)

    return {"valid": not failures, "failures": failures}
