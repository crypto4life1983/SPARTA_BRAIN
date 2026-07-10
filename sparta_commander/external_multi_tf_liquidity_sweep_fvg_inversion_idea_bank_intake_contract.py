"""External intake / IDEA-BANK record -- multi-timeframe liquidity-sweep + rapid FVG/
imbalance-failure (ICT-style) hypothesis -- PURE, READ-ONLY, RECORD-ONLY.

Durable idea-bank record for the human-approved intake conclusion (token
HUMAN_APPROVED_IDEA_BANK_RECORD_ONLY). It is NOT a candidate, NOT a proposal, and it opens
NO lane. It records that the model materially overlaps already-rejected families, that
claimed payouts/win-rates/trader results are non-evidence, that the full discretionary ICT
implementation is not mechanically testable as presented, that no independent return-engine
axis is demonstrated, and that the ONLY retained hypothesis is a future *diagnostic ablation*
that stays blocked until a full frozen/cost-honest/no-lookahead harness + a new explicit human
approval exist. Options / zero-DTE overlays are out of scope (required historical chain +
execution data are absent).

It creates/numbers NO candidate; modifies NO C8/C12/C18/C22 or any candidate; runs NO
backtest/replay/detector/labels/optimization/event-study; fetches/copies NO ES/NQ data; does
NOT touch the separate NQ/MNQ opening-range lab; changes NO queue/gate/lifecycle/approval/
decision state; opens NO options lane; and changes NO SPARTA research standard. Every
capability flag is pinned False with a full scope_locks set. Advances nothing.
"""
from __future__ import annotations

from typing import Any

IB_SCHEMA_VERSION = 1
IB_MODE = "RESEARCH_ONLY"
IB_LANE = "crypto_d1_auto_research"

RECORD_ID = "IDEA_BANK_MULTI_TF_LIQUIDITY_SWEEP_FVG_INVERSION"
REVIEWED_FAMILY = "multi_timeframe_liquidity_sweep_rapid_fvg_imbalance_failure_inversion"
SOURCE = ("external strategy intake (ICT-style multi-timeframe liquidity-sweep + "
          "fair-value-gap inversion); trader-claimed results treated as non-evidence")
APPROVAL_TOKEN = "HUMAN_APPROVED_IDEA_BANK_RECORD_ONLY"

VERDICT_IDEA_BANK_DIAGNOSTIC_ONLY = "IDEA_BANK_DIAGNOSTIC_ONLY"
RECOMMENDATION = "PRESERVE_AS_IDEA_BANK_DIAGNOSTIC_ONLY_NOT_A_CANDIDATE"

# (1) materially-overlapping ALREADY-REJECTED families (real ledger records, cited, not fabricated)
OVERLAPPING_REJECTED_FAMILIES = (
    {"family": "liquidity_sweep_mean_reversion", "candidate": "C8",
     "status": "REJECTED_KEPT_ON_RECORD",
     "note": "liquidity-sweep reversal: net-negative after costs, worse than random entry"},
    {"family": "failed_breakdown_reclaim_reversal", "candidate": "C12",
     "status": "REJECTED_KEPT_ON_RECORD",
     "note": "sweep-then-reclaim/reversal economics: net-negative after costs, worse than "
             "random entry, horizon/drift dominated"},
    {"family": "h4_trend_following_market_structure", "candidate": "C18",
     "status": "REJECTED_AT_FEE_HONEST_REPLAY_KEPT_ON_RECORD",
     "note": "multi-timeframe market structure: did not beat buy-and-hold, low win rate, "
             "structural stops bled"},
    {"family": "ny_session_fvg_choch", "candidate": "NY_SESSION_FVG_CHOCH",
     "status": "REJECTED_KEPT_ON_RECORD_COST_NON_VIABLE_RISK_GEOMETRY",
     "note": "explicit FVG + market-structure + liquidity-sweep model: tight-stop risk "
             "geometry did not survive taker cost"},
)

# (5) the ONLY retained hypothesis -- a FUTURE mechanically-frozen diagnostic ablation
RETAINED_DIAGNOSTIC_ABLATION = (
    "fixed_higher_timeframe_sweep",
    "fixed_rapid_imbalance_failure",
    "optional_fixed_retracement",
)

# (6) hard preconditions -- ALL required before any future study; none exist yet
FUTURE_STUDY_BLOCKED_UNTIL = (
    "mechanically_frozen_definitions",
    "provenance_sealed_es_nq_one_minute_data",
    "strict_no_lookahead_handling",
    "next_bar_conservative_execution",
    "commissions_and_slippage",
    "minimum_sample_gate",
    "random_entry_and_appropriate_benchmark_comparisons",
    "explicit_new_human_approval",
)

# (8) realistic prior -- an EXPECTATION, explicitly NOT a proven ES/NQ result
REALISTIC_PRIOR = (
    "likely to reproduce the earlier cost-sensitive C8/C12/C18/FVG rejection; this is a prior "
    "expectation ONLY and must NOT be stated as already proven for ES/NQ")

_CAPABILITY_FLAGS_FALSE = (
    "creates_candidate", "numbers_candidate", "is_proposal", "activates_candidate",
    "modifies_c8", "modifies_c12", "modifies_c18", "modifies_c22", "modifies_any_candidate",
    "runs_backtest", "runs_replay", "runs_detector", "runs_labels", "runs_event_study",
    "optimizes_parameters", "fetches_data", "copies_es_nq_data",
    "touches_nq_mnq_opening_range_lab", "changes_queue_state", "changes_gate_state",
    "changes_lifecycle_state", "changes_approval_state", "changes_decision_state",
    "opens_options_lane", "changes_research_standards", "treats_claims_as_evidence",
    "auto_commits", "auto_pushes", "advances_without_human_approval",
    "crosses_into_forbidden_gate",
)


def build_idea_bank_record() -> dict[str, Any]:
    """PURE. Assemble the durable idea-bank record. No I/O; authorizes/advances nothing."""
    blockers: list = []
    if len(OVERLAPPING_REJECTED_FAMILIES) < 4:
        blockers.append("must_cite_at_least_four_overlapping_rejected_families")

    record: dict[str, Any] = {
        "schema_version": IB_SCHEMA_VERSION, "mode": IB_MODE, "lane": IB_LANE,
        "record_id": RECORD_ID, "reviewed_family": REVIEWED_FAMILY, "source": SOURCE,
        "approved_via": APPROVAL_TOKEN,
        "is_idea_bank_record_only": True, "is_candidate": False, "is_proposal": False,
        "verdict": (VERDICT_IDEA_BANK_DIAGNOSTIC_ONLY if not blockers else "IDEA_BANK_BLOCKED"),
        "recommendation": RECOMMENDATION,
        "blockers": blockers,
        # (1)
        "materially_overlaps_rejected_families": True,
        "overlapping_rejected_families": [dict(r) for r in OVERLAPPING_REJECTED_FAMILIES],
        # (2)
        "claims_payouts_winrates_trader_results_are_non_evidence": True,
        # (3)
        "mechanically_testable_as_presented": False,
        "discretionary_reason": (
            "gap selection, liquidity hierarchy, timeframe selection, reaction speed, "
            "retracement quality, and lower-timeframe confirmation remain discretionary"),
        # (4)
        "new_return_engine_axis_demonstrated": False,
        # (5)
        "retained_hypothesis_diagnostic_ablation": list(RETAINED_DIAGNOSTIC_ABLATION),
        # (6)
        "future_study_blocked_until": list(FUTURE_STUDY_BLOCKED_UNTIL),
        # (7)
        "options_zero_dte_out_of_scope": True,
        "options_out_of_scope_reason": (
            "required historical option-chain / strike / expiry / implied-volatility / "
            "spread / realistic option-execution data are absent"),
        # (8)
        "realistic_prior": REALISTIC_PRIOR,
        "realistic_prior_is_proven_for_es_nq": False,
        # standing posture
        "creates_candidate": False, "advances_nothing": True, "human_review_required": True,
        "next_gate": ("NONE_IDEA_BANK_DIAGNOSTIC_ONLY_FUTURE_STUDY_REQUIRES_NEW_HUMAN_APPROVAL"),
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_create_candidate": True, "no_number_candidate": True, "no_proposal": True,
        "no_activate": True, "no_modify_c8_c12_c18_c22": True, "no_modify_any_candidate": True,
        "no_backtest": True, "no_replay": True, "no_detector": True, "no_labels": True,
        "no_event_study": True, "no_optimization": True, "no_data_fetch": True,
        "no_copy_es_nq_data": True, "no_touch_nq_mnq_opening_range_lab": True,
        "no_change_queue": True, "no_change_gate": True, "no_change_lifecycle": True,
        "no_change_approval": True, "no_change_decision": True, "no_options_lane": True,
        "no_change_research_standards": True, "no_treat_claims_as_evidence": True,
        "no_auto_commit": True, "no_auto_push": True, "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_idea_bank_record(record: Any) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when research-only, record-only (NOT a candidate/
    proposal), verdict IDEA_BANK_DIAGNOSTIC_ONLY, claims marked non-evidence, not mechanically
    testable as presented, no new axis demonstrated, options out of scope, the realistic prior
    NOT marked proven for ES/NQ, >= 4 real overlapping rejected families cited, the full
    precondition set present, and every capability flag False."""
    failures: list = []
    if not isinstance(record, dict):
        return {"valid": False, "failures": ["record_not_a_dict"]}
    r = record
    if r.get("mode") != IB_MODE:
        failures.append("mode_not_research_only")
    if r.get("is_idea_bank_record_only") is not True:
        failures.append("not_record_only")
    if r.get("is_candidate") is not False or r.get("is_proposal") is not False:
        failures.append("must_not_be_candidate_or_proposal")
    if r.get("verdict") != VERDICT_IDEA_BANK_DIAGNOSTIC_ONLY:
        failures.append("verdict_wrong")
    if r.get("blockers"):
        failures.append("has_blockers")
    if r.get("materially_overlaps_rejected_families") is not True:
        failures.append("must_flag_overlap")
    fams = {row.get("family") for row in (r.get("overlapping_rejected_families") or [])}
    for must in ("liquidity_sweep_mean_reversion", "failed_breakdown_reclaim_reversal",
                 "h4_trend_following_market_structure", "ny_session_fvg_choch"):
        if must not in fams:
            failures.append("missing_overlap_family:%s" % must)
    if r.get("claims_payouts_winrates_trader_results_are_non_evidence") is not True:
        failures.append("claims_must_be_non_evidence")
    if r.get("mechanically_testable_as_presented") is not False:
        failures.append("must_not_be_mechanically_testable_as_presented")
    if r.get("new_return_engine_axis_demonstrated") is not False:
        failures.append("must_not_claim_new_axis")
    if r.get("options_zero_dte_out_of_scope") is not True:
        failures.append("options_must_be_out_of_scope")
    if r.get("realistic_prior_is_proven_for_es_nq") is not False:
        failures.append("prior_must_not_be_marked_proven")
    if tuple(r.get("retained_hypothesis_diagnostic_ablation") or ()) \
            != RETAINED_DIAGNOSTIC_ABLATION:
        failures.append("retained_ablation_tampered")
    if tuple(r.get("future_study_blocked_until") or ()) != FUTURE_STUDY_BLOCKED_UNTIL:
        failures.append("preconditions_tampered")
    if r.get("advances_nothing") is not True:
        failures.append("must_advance_nothing")
    for flag in _CAPABILITY_FLAGS_FALSE:
        if r.get(flag) is not False:
            failures.append("capability_flag_true:%s" % flag)
    return {"valid": not failures, "failures": failures}
