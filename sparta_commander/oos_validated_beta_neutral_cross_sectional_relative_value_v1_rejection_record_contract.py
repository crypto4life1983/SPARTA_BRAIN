"""Candidate #19 -- oos_validated_beta_neutral_cross_sectional_relative_value_v1
-- FORMAL REJECTION / CLOSEOUT RECORD (PURE, RESEARCH ONLY).

Records the formal closeout of Candidate #19 as REJECTED AT THE REAL-CANDLE LABELS /
NEUTRALITY GATE (kept on record). Chain-gated on the FROZEN labels review carrying
structural_concern == True (the >= 100 sample gate not met AND OOS neutrality holding
on only a minority of bars). No fee-honest replay is run, because the labels /
neutrality gate already failed -- exactly as C16 was rejected at the labels stage
before replay.

It does NOTHING else: NO replay, NO PnL, NO re-detect, NO relabel, NO optimization /
tuning / rescue / parameter change, NO data fetch, NO writes, NO stage/commit/push,
NO paper/live/broker/order surface, and it does NOT start C20. It only PRESERVES the
honest labels result and the research lesson, anchors the rejection to the committed
labels-review commit, and preserves the upstream C19 gate commit references. Every
capability flag is pinned False with a full scope_locks set.

HONEST RESULT PRESERVED: the position mechanics were clean (gross capped at 1.0, one
live position, >= 5-bar spacing), but over the cached BTC/ETH/SOL D1 window
(2020-08-11..2026-06-08, 2128 candles) the detector produced only 41 tradeable entries
(< 100 structural sample gate) and the return-beta residual was beta-neutral
out-of-sample on only 862 of 1977 bars (~44%), with 15 positions closed by
neutrality-break. The neutral residual is not stable enough out of sample to justify a
fee-honest replay -- the same failure that rejected C16.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.oos_validated_beta_neutral_cross_sectional_relative_value_v1_real_candle_labels_review_contract as _l19  # noqa: E501

RJ19_SCHEMA_VERSION = 1
RJ19_MODE = "RESEARCH_ONLY"
RJ19_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = _l19.CANDIDATE_ID
CANDIDATE_FAMILY = _l19.CANDIDATE_FAMILY
CANDIDATE_NAME = _l19.CANDIDATE_NAME

VERDICT_RJ19_RECORDED = "REJECT_C19_AT_REAL_CANDLE_LABELS"
VERDICT_C19L_FROZEN = _l19.VERDICT_C19L_FROZEN
REJECTION_STATUS = "REJECTED_AT_REAL_CANDLE_LABELS_NEUTRALITY_GATE_KEPT_ON_RECORD"
REJECTED_AT_STAGE = "real_candle_labels_neutrality_gate"
REJECTED_FAMILY_NAME = "oos_validated_beta_neutral_cross_sectional_relative_value"

# pinned commit the rejection is anchored to (committed + pushed on origin)
LABELS_REVIEW_COMMIT = "c9470c085555bbbb0928b178a86181a95a76088e"

# upstream C19 gate commits (preserved provenance)
PUSHED_EVIDENCE_CHAIN = (
    {"stage": "family_proposal",
     "commit": "d7d7ac6c33712a9a46888bfc3338c79df299be41"},
    {"stage": "candidate_spec",
     "commit": "d5ce0444fd6494d65ccb6704ce4c080a87ac88f2"},
    {"stage": "detector_spec_dry_run",
     "commit": "0662955c5904705f637f24abbb534b9aada7286c"},
    {"stage": "real_candle_labels_review",
     "commit": "c9470c085555bbbb0928b178a86181a95a76088e"},
)

# pinned honest labels aggregates (from the frozen labels review)
N_COMMON_CANDLES = _l19.N_COMMON_CANDLES        # 2128
N_EVAL_BARS = _l19.N_EVAL_BARS                  # 1977
ENTRY_COUNT = _l19.ENTRY_COUNT                  # 41
SETUP_COUNT = _l19.SETUP_COUNT                  # 46
NEUTRALITY_PASS = _l19.NEUTRALITY_PASS_COUNT    # 862
NEUTRALITY_FAIL = _l19.NEUTRALITY_FAIL_COUNT    # 1115
EXIT_NEUTRALITY_BREAK = _l19.EXIT_NEUTRALITY_BREAK  # 15
MIN_ENTRIES_STRUCTURAL = _l19.MIN_ENTRIES_STRUCTURAL  # 100

NEXT_REQUIRED_ACTION = (
    "NONE__C19_CLOSED__REJECTED_AT_REAL_CANDLE_LABELS_NEUTRALITY_GATE__KEPT_ON_"
    "RECORD_AS_OOS_BETA_NEUTRALITY_DOES_NOT_PERSIST_RESEARCH_LESSON")

CONCLUSION = (
    "The OOS-validated beta-neutral cross-sectional relative-value family cleared the "
    "position mechanics (gross capped at 1.0, one live position, >= 5-bar spacing) but "
    "failed the real-candle labels / neutrality gate: only 41 tradeable entries (< 100 "
    "structural sample gate) and the return-beta residual was beta-neutral "
    "out-of-sample on only 862 of 1977 bars (~44%), with 15 positions closed by "
    "neutrality-break. This echoes the C16 failure -- return-beta neutrality does not "
    "persist out of sample -- so the neutral residual is not stable enough to justify "
    "a fee-honest replay, and none was run.")

# This rejected family extends the canonical rejected ledger to 24 (C1-C19). This
# bundle applies that bump in the REP / SARA / lane / integration ledgers.
LEDGER_BUMP = {
    "from_count": 23, "to_count": 24, "add_family": REJECTED_FAMILY_NAME,
    "applied_in_this_bundle": True,
}

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "runs_replay", "computes_pnl", "re_detects",
    "relabels", "rebuilds_detector", "runs_labels", "runs_backtest",
    "optimizes_parameters", "reparameterizes", "tunes_parameters", "runs_rescue",
    "runs_robustness", "fetches_data", "reads_real_data", "mutates_data",
    "stages_data", "commits_data_artifact", "auto_commits", "auto_pushes",
    "applies_cost_model", "modifies_scheduler", "sends_notifications", "calls_api",
    "uses_network", "uses_credentials", "connects_broker", "connects_exchange",
    "uses_real_money", "places_orders", "contains_order_logic", "auto_trading",
    "uses_xauusd", "adds_new_instrument_class", "paper_trading", "live_trading",
    "deploys_capital", "promotes_gate", "unlocks_downstream_gate", "skips_any_gate",
    "reactivates_candidate", "parks_as_active", "starts_c20",
    "advances_without_human_approval", "claims_profitability", "claims_edge",
    "crosses_into_forbidden_gate",
)


def get_candidate_19_rejection_record_label() -> str:
    return (
        "Candidate #19 oos_validated_beta_neutral_cross_sectional_relative_value_v1 "
        "rejection record (READ-ONLY, RESEARCH ONLY). "
        "REJECTED_AT_REAL_CANDLE_LABELS_NEUTRALITY_GATE_KEPT_ON_RECORD -- NOT AN "
        "ACTIVE CANDIDATE. Mechanics clean but only 41 entries (< 100 gate) and OOS "
        "beta-neutrality held on only ~44% of bars (the C16 echo) -- not stable enough "
        "to justify a fee-honest replay (none run). NOT a profitability claim. NOT a "
        "paper/live-readiness claim.")


def get_candidate_19_rejection_record_next_action() -> str:
    return NEXT_REQUIRED_ACTION


def build_c19_rejection_record(repo_root: Any = ".",
                               tracked_paths: list | None = None) -> dict[str, Any]:
    """Assemble the frozen C19 rejection / closeout record. Pure; no I/O; chain-gated
    on the frozen labels review carrying the structural concern."""
    labels = _l19.build_c19_labels_review(repo_root, tracked_paths)
    labels_valid = _l19.validate_c19_labels_review(labels)["valid"]

    blockers: list = []
    if not labels_valid:
        blockers.append("c19_labels_review_invalid")
    if labels.get("verdict") != VERDICT_C19L_FROZEN:
        blockers.append("c19_labels_review_not_frozen")
    if labels.get("structural_concern") is not True:
        blockers.append("labels_have_no_structural_concern")
    if labels.get("meets_min_sample_gate") is not False:
        blockers.append("sample_gate_unexpectedly_met")
    if labels.get("neutrality_holds_majority") is not False:
        blockers.append("neutrality_unexpectedly_held_majority")

    record: dict[str, Any] = {
        "schema_version": RJ19_SCHEMA_VERSION, "mode": RJ19_MODE, "lane": RJ19_LANE,
        "label": get_candidate_19_rejection_record_label(),
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "candidate_name": CANDIDATE_NAME,
        "is_rejection_record_only": True,
        "blockers": blockers,
        "verdict": (VERDICT_RJ19_RECORDED if not blockers
                    else "C19_REJECTION_BLOCKED"),
        "rejection_status": REJECTION_STATUS,
        "rejected_at_stage": REJECTED_AT_STAGE,
        "is_active_candidate": False,
        "parked_as_active": False,
        "kept_on_record": True,
        "original_frozen_c19_result_unchanged": True,
        "added_to_rejected_family_ledger": True,
        "no_fee_honest_replay_run": True,
        # chain provenance + anchors
        "labels_review_verdict": labels.get("verdict"),
        "labels_review_valid": labels_valid,
        "labels_structural_concern": labels.get("structural_concern"),
        "labels_meets_min_sample_gate": labels.get("meets_min_sample_gate"),
        "labels_neutrality_holds_majority": labels.get("neutrality_holds_majority"),
        "anchored_to_labels_review_commit": LABELS_REVIEW_COMMIT,
        # verbatim conclusion + lesson
        "conclusion": CONCLUSION,
        "kept_on_record_as": [
            "MECHANICS CLEAN: gross capped at 1.0, one live position, >= 5-bar "
            "spacing all held on real candles",
            "but the STRUCTURAL SAMPLE GATE FAILED: only 41 tradeable entries vs the "
            ">= 100 gate",
            "and OOS NEUTRALITY DID NOT PERSIST: beta-neutral on only 862 of 1977 "
            "bars (~44%), 15 positions closed by neutrality-break -- the C16 echo",
            "so NO fee-honest replay was run: the neutral residual is not stable "
            "enough out of sample to justify it",
        ],
        "rejection_reasons": [
            "STRUCTURAL SAMPLE GATE: only %d tradeable entries, below the >= %d gate"
            % (ENTRY_COUNT, MIN_ENTRIES_STRUCTURAL),
            "OOS NEUTRALITY INTERMITTENT: passed %d / %d bars (~%.0f%%), failed %d"
            % (NEUTRALITY_PASS, N_EVAL_BARS,
               100.0 * NEUTRALITY_PASS / N_EVAL_BARS, NEUTRALITY_FAIL),
            "%d open positions closed by NEUTRALITY-BREAK invalidation"
            % EXIT_NEUTRALITY_BREAK,
            "echoes the C16 failure: return-beta neutrality does not persist out of "
            "sample; no fee-honest replay justified",
        ],
        "evidence_headline": {
            "mechanics_clean": True,
            "sample_gate_failed": ENTRY_COUNT < MIN_ENTRIES_STRUCTURAL,
            "oos_neutrality_did_not_persist": NEUTRALITY_PASS < NEUTRALITY_FAIL,
            "closed_by_neutrality_break": EXIT_NEUTRALITY_BREAK > 0,
            "no_replay_run": True,
            "echoes_c16_neutrality_failure": True,
        },
        # pinned numbers
        "n_common_candles": N_COMMON_CANDLES, "n_eval_bars": N_EVAL_BARS,
        "entry_count": ENTRY_COUNT, "setup_count": SETUP_COUNT,
        "neutrality_pass_count": NEUTRALITY_PASS,
        "neutrality_fail_count": NEUTRALITY_FAIL,
        "exit_neutrality_break": EXIT_NEUTRALITY_BREAK,
        "min_entries_structural_gate": MIN_ENTRIES_STRUCTURAL,
        # evidence chain + ledger bump
        "pushed_evidence_chain": [dict(e) for e in PUSHED_EVIDENCE_CHAIN],
        "rejected_family_name": REJECTED_FAMILY_NAME,
        "ledger_bump": dict(LEDGER_BUMP),
        "claim_locks": [
            "no_profitability_claim", "kept_on_record_not_active_candidate",
            "not_parked_as_active", "labels_neutrality_failure_disclosed",
            "no_fee_honest_replay_run", "echoes_c16_neutrality_failure",
            "conclusion_recorded_precisely",
        ],
        "human_review_required": True,
        "current_loop_stage": "rejection_record",
        "next_required_action": NEXT_REQUIRED_ACTION,
        "does_not_start_c20": True, "c20_candidate_id": None,
        # gates locked
        "labels_gate_locked": True, "replay_gate_locked": True,
        "robustness_gate_locked": True, "promote_gate_locked": True,
        "paper_trading_gate_locked": True, "live_gate_locked": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_replay": True, "no_pnl": True, "no_re_detect": True, "no_relabel": True,
        "no_detector_rebuild": True, "no_optimization": True,
        "no_reparameterization": True, "no_tuning": True, "no_rescue": True,
        "no_robustness_run": True, "no_data_fetch": True, "no_data_mutation": True,
        "no_data_commit": True, "no_cost_application": True, "no_xauusd": True,
        "no_new_instrument_class": True, "no_reactivation": True,
        "no_parking_as_active": True, "no_stage": True, "no_commit": True,
        "no_push": True, "no_auto_commit": True, "no_auto_push": True,
        "no_broker": True, "no_credentials": True, "no_order_logic": True,
        "no_auto_trading": True, "no_paper_trading": True, "no_live_trading": True,
        "no_gate_skip": True, "no_start_c20": True, "no_downstream_gate_unlock": True,
        "no_profitability_claim": True, "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_c19_rejection_record(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the record is research-only,
    rejection-record-only, chain-gated on the frozen labels review carrying the
    structural concern (sample gate not met AND neutrality not majority), keeps the
    candidate not-active / not-parked / kept-on-record, records
    REJECT_C19_AT_REAL_CANDLE_LABELS anchored to the pushed labels-review commit,
    preserves the verbatim conclusion + the labels/neutrality failure facts (none can
    be flipped), confirms NO fee-honest replay was run, cites the 4 pushed gate
    commits, applies the 23->24 ledger bump, does not start C20, and pins every
    capability flag False."""
    failures: list = []
    if record.get("mode") != RJ19_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_rejection_record_only") is not True:
        failures.append("not_rejection_record_only")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("verdict") != VERDICT_RJ19_RECORDED:
        failures.append("verdict_not_reject_c19_at_labels")
    if record.get("rejection_status") != REJECTION_STATUS:
        failures.append("status_not_rejected_at_labels")
    if record.get("rejected_at_stage") != REJECTED_AT_STAGE:
        failures.append("rejected_stage_not_labels_neutrality_gate")

    # not active / not parked / kept on record
    if record.get("is_active_candidate") is not False:
        failures.append("must_not_be_active")
    if record.get("parked_as_active") is not False:
        failures.append("must_not_be_parked")
    if record.get("kept_on_record") is not True:
        failures.append("must_be_kept_on_record")

    # chain gate on the frozen labels review carrying the structural concern
    if record.get("labels_review_verdict") != VERDICT_C19L_FROZEN:
        failures.append("labels_review_not_frozen")
    if record.get("labels_review_valid") is not True:
        failures.append("labels_review_not_valid")
    if record.get("labels_structural_concern") is not True:
        failures.append("labels_concern_missing")
    if record.get("labels_meets_min_sample_gate") is not False:
        failures.append("sample_gate_should_not_be_met")
    if record.get("labels_neutrality_holds_majority") is not False:
        failures.append("neutrality_should_not_hold_majority")
    if record.get("no_fee_honest_replay_run") is not True:
        failures.append("replay_should_not_have_run")

    # anchored to the pushed labels-review commit
    if record.get("anchored_to_labels_review_commit") != LABELS_REVIEW_COMMIT:
        failures.append("labels_anchor_commit_tampered")

    # verbatim conclusion
    if record.get("conclusion") != CONCLUSION:
        failures.append("conclusion_tampered")

    # preserved failure facts -- cannot be flipped
    eh = record.get("evidence_headline") or {}
    for k in ("mechanics_clean", "sample_gate_failed",
              "oos_neutrality_did_not_persist", "closed_by_neutrality_break",
              "no_replay_run", "echoes_c16_neutrality_failure"):
        if eh.get(k) is not True:
            failures.append("rejection_finding_cleared_%s" % k)
    if len(record.get("rejection_reasons") or []) < 3:
        failures.append("rejection_reasons_missing")

    # pinned numbers intact + genuinely a rejection
    if record.get("entry_count") != ENTRY_COUNT:
        failures.append("entry_count_tampered")
    if record.get("entry_count", 999) >= record.get(
            "min_entries_structural_gate", 0):
        failures.append("entry_count_not_below_gate")
    if record.get("neutrality_pass_count") != NEUTRALITY_PASS:
        failures.append("neutrality_pass_tampered")
    if record.get("neutrality_pass_count", 9999) >= record.get(
            "neutrality_fail_count", 0):
        failures.append("metrics_inconsistent_with_rejection")

    # pushed evidence chain: 4 gate commits, each a 40-char sha
    chain = record.get("pushed_evidence_chain") or []
    stages = {e.get("stage"): e.get("commit") for e in chain}
    for required in ("family_proposal", "candidate_spec", "detector_spec_dry_run",
                     "real_candle_labels_review"):
        if required not in stages:
            failures.append("pushed_chain_missing_%s" % required)
        elif not (isinstance(stages[required], str)
                  and len(stages[required]) == 40):
            failures.append("pushed_chain_bad_commit_%s" % required)

    # ledger bump applied in this bundle (23 -> 24)
    lb = record.get("ledger_bump") or {}
    if lb.get("to_count") != 24 or lb.get("from_count") != 23:
        failures.append("ledger_bump_counts_wrong")
    if lb.get("add_family") != REJECTED_FAMILY_NAME:
        failures.append("ledger_bump_family_wrong")

    # no C20
    if record.get("does_not_start_c20") is not True:
        failures.append("must_not_start_c20")
    if record.get("c20_candidate_id") is not None:
        failures.append("c20_must_be_none")

    # gates locked
    for gate in ("labels_gate_locked", "replay_gate_locked",
                 "robustness_gate_locked", "promote_gate_locked",
                 "paper_trading_gate_locked", "live_gate_locked"):
        if record.get(gate) is not True:
            failures.append("gate_unlocked_%s" % gate)

    locks = record.get("scope_locks") or {}
    for key in ("no_replay", "no_pnl", "no_re_detect", "no_relabel",
                "no_detector_rebuild", "no_optimization", "no_tuning", "no_rescue",
                "no_data_fetch", "no_data_commit", "no_xauusd", "no_reactivation",
                "no_commit", "no_push", "no_broker", "no_order_logic",
                "no_auto_trading", "no_paper_trading", "no_live_trading",
                "no_gate_skip", "no_start_c20"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
