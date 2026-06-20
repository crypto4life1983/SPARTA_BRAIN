"""Candidate #21 -- low_turnover_same_asset_spot_perp_funding_carry_v1
-- FORMAL REJECTION / CLOSEOUT RECORD (PURE, RESEARCH ONLY).

Records the formal closeout of Candidate #21 as REJECTED AT THE FEE-HONEST REPLAY STAGE
(kept on record). Chain-gated on the FROZEN replay results review carrying
all_decisive_gates_pass == False and recommended_decision == REJECT.

It does NOTHING else: NO replay re-run, NO PnL recompute, NO fee change/drop, NO
re-detect, NO relabel, NO optimization / tuning / rescue / parameter change, NO data
fetch, NO writes, NO stage/commit/push, NO paper/live/broker/order surface, NO rescue of
C20, and it does NOT start C22 and does NOT pivot to a new family. It only PRESERVES the
honest replay result and the two research lessons, anchors the rejection to the frozen
replay artifacts (SHA-pinned) + the pushed C21 gate commits.

HONEST RESULT PRESERVED -- this rejection differs from C20's: unlike C20 (net -74.5%,
churned away by 521% cost), the LOW-TURNOVER C21 is NET-POSITIVE (+20.2%, Sharpe 1.05,
max DD -8.5%; gross +25.7%, Sharpe 1.31) on only 20 trades (cost drag 14.8%), so the
74 bps two-leg cost no longer dominates -- the low-turnover design WORKED. BUT C21 does
NOT beat the trivial always-on neutral-carry null (+21.2%, Sharpe 1.09) on return or
risk-adjusted basis, and the 2026 forward-OOS is negative for both (strategy -1.0%, null
-0.5%). Two of four decisive gates pass (net-positive, Sharpe-positive); the two decisive
market-neutral gates FAIL (beats-null, forward-OOS). The SPARTA Pipeline Audit v1
cross-checks all pass (cost == 20 x 74 bps; no duplicate trades; funding correct
side/time; same-asset aligned; turnover <= 6/yr), so this is an EDGE-driven rejection,
NOT a fee/funding/lookahead/duplicate/alignment artifact. The carry SOURCE is real (the
null is positive); C21's detector/timing simply adds NO edge over holding the carry.

PRESERVED LESSONS (two): (1) LOW TURNOVER FIXES THE CHURN -- +20.2% vs C20's -74.5% on
the same carry validates the C20->C21 lesson; the 74 bps cost is survivable at 20 trades.
(2) SAME-ASSET CARRY TIMING ADDS NO EDGE -- the regime-gating/hysteresis/durable-breakdown
timing marginally UNDERPERFORMS simply holding the always-on neutral carry, which is the
real (but free, and OOS-fragile) return source; a tradeable edge over the null was not
found. Any future pursuit of the always-on carry itself is a SEPARATE, new human-approved
candidate -- NOT a C21 promotion and NOT a C20 rescue.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.low_turnover_same_asset_spot_perp_funding_carry_v1_replay_results_review_contract as _r21  # noqa: E501

RJ21_SCHEMA_VERSION = 1
RJ21_MODE = "RESEARCH_ONLY"
RJ21_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = _r21.CANDIDATE_ID
CANDIDATE_FAMILY = _r21.CANDIDATE_FAMILY
CANDIDATE_NAME = _r21.CANDIDATE_NAME

VERDICT_RJ21_RECORDED = "REJECT_C21_AT_FEE_HONEST_REPLAY"
VERDICT_C21R_FROZEN = _r21.VERDICT_C21R_FROZEN
REJECTION_STATUS = "REJECTED_AT_FEE_HONEST_REPLAY_KEPT_ON_RECORD"
REJECTED_AT_STAGE = "fee_honest_replay"
REJECTED_FAMILY_NAME = "low_turnover_same_asset_spot_perp_funding_carry"
# the human-specified canonical rejection reason code.
REJECTION_REASON_CODE = (
    "EDGE_DOES_NOT_BEAT_ALWAYS_ON_NEUTRAL_CARRY_NULL_AND_FORWARD_OOS_FAILS")

# pinned frozen replay artifacts the rejection is anchored to (gitignored, SHA-pinned;
# the replay-review contract that pins them is committed in THIS same bundle).
ANCHORED_TO_REPLAY_LEDGER_SHA256 = _r21.EXPECTED_LEDGER_SHA256
ANCHORED_TO_REPLAY_SUMMARY_SHA256 = _r21.EXPECTED_SUMMARY_SHA256
ANCHORED_TO_LABELS_SHA256 = _r21.EXPECTED_LABELS_SHA256

# upstream C21 gate commits (preserved provenance; all pushed on origin/master).
PUSHED_EVIDENCE_CHAIN = (
    {"stage": "family_proposal",
     "commit": "896a16eeee6ed1abd58b28fa75ebadaaff05d7bf"},
    {"stage": "candidate_spec",
     "commit": "316ebce733be0ce0496edf44219c6fe717bb2afd"},
    {"stage": "detector_spec_dry_run",
     "commit": "ff4649ce8a14acf171f156ae11ddc57500ebad0f"},
    {"stage": "real_candle_labels_review",
     "commit": "668d06f20d6824cd62f07bc8b06f15f10576f46d"},
)
# the preserved C21 labels commit (explicitly required to be preserved).
LABELS_COMMIT = "668d06f20d6824cd62f07bc8b06f15f10576f46d"

# pinned honest replay metrics (from the frozen replay review)
TRADE_COUNT = _r21.TRADE_COUNT                              # 20
STRATEGY_NET_RETURN = _r21.STRATEGY_METRICS["net_return"]          # 0.202382
STRATEGY_SHARPE = _r21.STRATEGY_METRICS["sharpe"]                 # 1.052315
STRATEGY_GROSS_RETURN = _r21.STRATEGY_GROSS_METRICS["net_return"]  # 0.257014
STRATEGY_MAX_DD = _r21.STRATEGY_METRICS["max_drawdown"]           # -0.084976
NULL_NET_RETURN = _r21.RANDOM_NULL_METRICS["net_return"]          # 0.211648
NULL_SHARPE = _r21.RANDOM_NULL_METRICS["sharpe"]                 # 1.087808
OOS_NET_RETURN = _r21.STRATEGY_FORWARD_OOS_METRICS["net_return"]   # -0.010245
OOS_SHARPE = _r21.STRATEGY_FORWARD_OOS_METRICS["sharpe"]          # -3.12989
OOS_WIN_RATE = _r21.FORWARD_OOS_WIN_RATE                          # 0.0
OOS_TRADE_COUNT = _r21.FORWARD_OOS_TRADE_COUNT                   # 3
TOTAL_COST_DRAG = _r21.TOTAL_COST_DRAG                           # 0.148
FUNDING_CONTRIBUTION = _r21.FUNDING_CONTRIBUTION_TOTAL            # 0.914196
ROUND_TRIP_COST_PER_TRADE_BPS = _r21.ROUND_TRIP_COST_PER_TRADE_BPS  # 74.0

NEXT_REQUIRED_ACTION = (
    "NONE__C21_CLOSED__REJECTED_AT_FEE_HONEST_REPLAY__KEPT_ON_RECORD__LOW_TURNOVER_FIXES_"
    "CHURN_BUT_CARRY_TIMING_ADDS_NO_EDGE_OVER_ALWAYS_ON_NULL__ACTIVE_CANDIDATE_NONE__"
    "NEXT_IS_CANDIDATE_22_PROPOSAL_READINESS_ONLY_WITH_EXPLICIT_HUMAN_APPROVAL")

CONCLUSION = (
    "The low-turnover same-asset spot/perp funding-carry family cleared every prior "
    "structural gate and -- unlike the rejected C20 -- SURVIVED the fee-honest replay "
    "net-positive (+20.2%, Sharpe 1.05; gross +25.7%, Sharpe 1.31) on only 20 trades "
    "(cost drag 14.8%), proving the low-turnover design fixed C20's churn. BUT it was "
    "REJECTED at the fee-honest replay decisive market-neutral gates: it does NOT beat "
    "the trivial always-on neutral-carry null (+21.2%, Sharpe 1.09) on return or "
    "risk-adjusted basis, and the 2026 forward-OOS is negative (strategy -1.0%, null "
    "-0.5%). Two of four decisive gates pass (net-positive, Sharpe-positive); the two "
    "decisive gates FAIL (beats-null, forward-OOS). The SPARTA Pipeline Audit v1 "
    "cross-checks all pass (cost == 20 x 74 bps, no duplicate trades, funding correct "
    "side/time, same-asset aligned, turnover <= 6/yr), so this is an EDGE-driven "
    "rejection, NOT a fee/funding/lookahead/duplicate/alignment artifact. The carry "
    "SOURCE is real (the null is positive); C21's detector/timing adds NO edge over "
    "simply holding the neutral carry.")

# preserved research lessons (two; explicitly required)
PRESERVED_LESSON_LOW_TURNOVER = (
    "LOW TURNOVER FIXES THE CHURN: the same mechanically-neutral same-asset carry that "
    "C20 churned to net -74.5% (704 trades, 521% cost drag) is net +20.2% under C21's "
    "low-turnover regime-gating (20 trades, 14.8% cost drag). At <= 6 round-trips/yr/"
    "asset the 74 bps two-leg cost is survivable. The C20->C21 turnover lesson is "
    "VALIDATED: cost, not signal, killed C20.")
PRESERVED_LESSON_NO_TIMING_EDGE = (
    "SAME-ASSET CARRY TIMING ADDS NO EDGE: C21's regime-gate / hysteresis / "
    "durable-breakdown timing marginally UNDERPERFORMS simply holding the always-on "
    "neutral carry continuously (strategy +20.2% / Sharpe 1.05 vs null +21.2% / Sharpe "
    "1.09), and both are negative in the 2026 forward-OOS. The carry SOURCE is real but "
    "FREE (it is the null) and OOS-fragile; a tradeable TIMING edge over the null was "
    "not found. Pursuing the always-on carry itself would be a SEPARATE, new "
    "human-approved candidate -- NOT a C21 promotion and NOT a C20 rescue.")

# This rejected family extends the canonical rejected ledger to 26 (C1-C21). This
# bundle applies that bump in the REP / SARA / lane / integration ledgers.
LEDGER_BUMP = {
    "from_count": 25, "to_count": 26, "add_family": REJECTED_FAMILY_NAME,
    "applied_in_this_bundle": True,
}

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "runs_replay", "re_runs_replay", "computes_pnl",
    "recomputes_pnl", "changes_fee", "drops_cost", "re_detects", "relabels",
    "rebuilds_detector", "runs_labels", "runs_backtest", "optimizes_parameters",
    "reparameterizes", "tunes_parameters", "runs_rescue", "rescues_c20",
    "retunes_rejected_candidate", "runs_parameter_sweep", "runs_robustness",
    "fetches_data", "reads_real_data", "mutates_data", "stages_data",
    "commits_data_artifact", "auto_commits", "auto_pushes", "applies_cost_model",
    "modifies_scheduler", "sends_notifications", "calls_api", "uses_network",
    "uses_credentials", "connects_broker", "connects_exchange", "uses_real_money",
    "places_orders", "contains_order_logic", "auto_trading", "uses_xauusd",
    "adds_new_instrument_class", "paper_trading", "live_trading", "deploys_capital",
    "promotes_gate", "unlocks_downstream_gate", "skips_any_gate",
    "reactivates_candidate", "parks_as_active", "starts_c22", "pivots_to_new_family",
    "advances_without_human_approval", "claims_profitability", "claims_edge",
    "crosses_into_forbidden_gate",
)


def get_candidate_21_rejection_record_label() -> str:
    return (
        "Candidate #21 low_turnover_same_asset_spot_perp_funding_carry_v1 rejection "
        "record (READ-ONLY, RESEARCH ONLY). REJECTED_AT_FEE_HONEST_REPLAY_KEPT_ON_RECORD "
        "-- NOT AN ACTIVE CANDIDATE. The low-turnover design WORKED (net +20.2%, Sharpe "
        "1.05 on 20 trades, vs C20's -74.5% on 704), but it does NOT beat the always-on "
        "neutral-carry null (+21.2%, Sharpe 1.09) and the 2026 forward-OOS fails "
        "(strategy -1.0%, null -0.5%). 2 of 4 decisive gates pass; the decisive "
        "beats-null + forward-OOS gates FAIL. Audit cross-checks all clean (not a "
        "fee/funding/lookahead/duplicate/alignment artifact). Rejects the lack of EDGE "
        "over the trivial carry, NOT the carry source (which is real but free and "
        "OOS-fragile). The always-on carry itself is a SEPARATE future candidate only "
        "with explicit human approval. NOT a profitability claim. NOT a paper/live-"
        "readiness claim.")


def get_candidate_21_rejection_record_next_action() -> str:
    return NEXT_REQUIRED_ACTION


def build_c21_rejection_record(repo_root: Any = ".",
                               tracked_paths: list | None = None) -> dict[str, Any]:
    """Assemble the frozen C21 rejection / closeout record. Pure; no I/O; chain-gated
    on the frozen replay review carrying NOT-all-pass decisive gates + REJECT."""
    replay = _r21.build_c21_replay_review(repo_root, tracked_paths)
    replay_valid = _r21.validate_c21_replay_review(replay)["valid"]

    blockers: list = []
    if not replay_valid:
        blockers.append("c21_replay_review_invalid")
    if replay.get("verdict") != VERDICT_C21R_FROZEN:
        blockers.append("c21_replay_review_not_frozen")
    if replay.get("all_decisive_gates_pass") is not False:
        blockers.append("replay_gates_unexpectedly_all_passed")
    if replay.get("recommended_decision") != "REJECT":
        blockers.append("replay_did_not_recommend_reject")
    if replay.get("strategy_beats_always_on_null_after_costs") is not False:
        blockers.append("strategy_unexpectedly_beats_null")

    record: dict[str, Any] = {
        "schema_version": RJ21_SCHEMA_VERSION, "mode": RJ21_MODE, "lane": RJ21_LANE,
        "label": get_candidate_21_rejection_record_label(),
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "candidate_name": CANDIDATE_NAME,
        "is_rejection_record_only": True,
        "blockers": blockers,
        "verdict": (VERDICT_RJ21_RECORDED if not blockers
                    else "C21_REJECTION_BLOCKED"),
        "rejection_status": REJECTION_STATUS,
        "rejected_at_stage": REJECTED_AT_STAGE,
        "rejection_reason_code": REJECTION_REASON_CODE,
        "is_active_candidate": False,
        "parked_as_active": False,
        "kept_on_record": True,
        "original_frozen_c21_result_unchanged": True,
        "added_to_rejected_family_ledger": True,
        "fee_honest_replay_was_run": True,
        # chain provenance + anchors
        "replay_review_verdict": replay.get("verdict"),
        "replay_review_valid": replay_valid,
        "replay_all_decisive_gates_pass": replay.get("all_decisive_gates_pass"),
        "replay_recommended_decision": replay.get("recommended_decision"),
        "replay_strategy_beats_null": replay.get(
            "strategy_beats_always_on_null_after_costs"),
        "anchored_to_replay_ledger_sha256": ANCHORED_TO_REPLAY_LEDGER_SHA256,
        "anchored_to_replay_summary_sha256": ANCHORED_TO_REPLAY_SUMMARY_SHA256,
        "anchored_to_labels_sha256": ANCHORED_TO_LABELS_SHA256,
        "replay_review_committed_in_same_bundle": True,
        "preserved_labels_commit": LABELS_COMMIT,
        # verbatim conclusion + lessons
        "conclusion": CONCLUSION,
        "preserved_lesson_low_turnover_fixes_churn": PRESERVED_LESSON_LOW_TURNOVER,
        "preserved_lesson_no_timing_edge_over_null": PRESERVED_LESSON_NO_TIMING_EDGE,
        "low_turnover_design_worked": True,
        "rejects_lack_of_edge_not_the_carry_source": True,
        "carry_source_is_real_but_free_and_oos_fragile": True,
        "always_on_carry_is_separate_future_candidate_only_with_approval": True,
        "is_rescue_or_retune_of_c20": False,
        "c20_remains_rejected": True,
        "kept_on_record_as": [
            "LOW-TURNOVER DESIGN WORKED: 20 trades, cost drag 14.8%, net +20.2% "
            "(Sharpe 1.05) -- the same carry C20 churned to -74.5%",
            "but FAILED the decisive market-neutral gates at fee-honest replay: does "
            "NOT beat the always-on null (+21.2%, Sharpe 1.09)",
            "2026 FORWARD-OOS FAILED: strategy net -1.0% (both strategy and null "
            "slightly negative)",
            "AUDIT-CLEAN: not a fee/funding/lookahead/duplicate/alignment artifact -- "
            "an honest EDGE-driven rejection",
        ],
        "rejection_reasons": [
            "DOES NOT BEAT THE ALWAYS-ON NEUTRAL-CARRY NULL: strategy net %.4f / Sharpe "
            "%.2f vs null net %.4f / Sharpe %.2f (loses on both)"
            % (STRATEGY_NET_RETURN, STRATEGY_SHARPE, NULL_NET_RETURN, NULL_SHARPE),
            "2026 FORWARD-OOS FAILED: strategy net %.4f, Sharpe %.2f, %d trades, %.0f%% "
            "win rate" % (OOS_NET_RETURN, OOS_SHARPE, OOS_TRADE_COUNT,
                          100.0 * OOS_WIN_RATE),
            "NO TIMING EDGE: the regime-timing marginally underperforms simply holding "
            "the always-on carry -- the carry source is real but free",
            "AUDIT-CLEAN: cost == %d x %.0f bps, no duplicate trades, funding correct "
            "side/time, same-asset aligned, turnover <= 6/yr -- not a pipeline artifact"
            % (TRADE_COUNT, ROUND_TRIP_COST_PER_TRADE_BPS),
            "rejects the LACK OF EDGE over the null, NOT the same-asset carry source",
        ],
        "evidence_headline": {
            "low_turnover_preserved_carry_net_positive": STRATEGY_NET_RETURN > 0,
            "does_not_beat_always_on_null": STRATEGY_SHARPE < NULL_SHARPE
            and STRATEGY_NET_RETURN < NULL_NET_RETURN,
            "all_decisive_gates_passed": False,
            "forward_oos_failed": OOS_NET_RETURN <= 0,
            "carry_source_real_null_positive": NULL_NET_RETURN > 0,
            "cost_no_longer_dominates": TOTAL_COST_DRAG < FUNDING_CONTRIBUTION,
            "not_a_pipeline_artifact": True,
        },
        # pinned numbers
        "trade_count": TRADE_COUNT,
        "strategy_net_return": STRATEGY_NET_RETURN,
        "strategy_sharpe": STRATEGY_SHARPE,
        "strategy_gross_return": STRATEGY_GROSS_RETURN,
        "strategy_max_drawdown": STRATEGY_MAX_DD,
        "random_null_net_return": NULL_NET_RETURN,
        "random_null_sharpe": NULL_SHARPE,
        "forward_oos_net_return": OOS_NET_RETURN,
        "forward_oos_sharpe": OOS_SHARPE,
        "forward_oos_win_rate": OOS_WIN_RATE,
        "total_cost_drag": TOTAL_COST_DRAG,
        "funding_contribution_total": FUNDING_CONTRIBUTION,
        "round_trip_cost_per_trade_bps": ROUND_TRIP_COST_PER_TRADE_BPS,
        # evidence chain + ledger bump
        "pushed_evidence_chain": [dict(e) for e in PUSHED_EVIDENCE_CHAIN],
        "rejected_family_name": REJECTED_FAMILY_NAME,
        "ledger_bump": dict(LEDGER_BUMP),
        # active candidate none; next is C22 proposal readiness ONLY (not implementation)
        "active_candidate_after_rejection": None,
        "next_stage": "candidate_22_proposal_readiness",
        "c22_proposal_readiness_only_not_implementation": True,
        "does_not_start_c22": True, "c22_candidate_id": None,
        "does_not_pivot_to_new_family": True,
        "claim_locks": [
            "no_profitability_claim", "kept_on_record_not_active_candidate",
            "not_parked_as_active", "replay_no_edge_disclosed",
            "rejects_lack_of_edge_not_carry_source", "low_turnover_lesson_preserved",
            "no_timing_edge_lesson_preserved", "not_a_c20_rescue",
            "conclusion_recorded_precisely",
        ],
        "human_review_required": True,
        "current_loop_stage": "rejection_record",
        "next_required_action": NEXT_REQUIRED_ACTION,
        # gates locked
        "labels_gate_locked": True, "replay_gate_locked": True,
        "robustness_gate_locked": True, "promote_gate_locked": True,
        "paper_trading_gate_locked": True, "live_gate_locked": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_replay": True, "no_re_replay": True, "no_pnl": True,
        "no_recompute_pnl": True, "no_change_fee": True, "no_drop_cost": True,
        "no_re_detect": True, "no_relabel": True, "no_detector_rebuild": True,
        "no_optimization": True, "no_reparameterization": True, "no_tuning": True,
        "no_rescue": True, "no_rescue_c20": True, "no_parameter_sweep": True,
        "no_robustness_run": True, "no_data_fetch": True, "no_data_mutation": True,
        "no_data_commit": True, "no_cost_application": True, "no_xauusd": True,
        "no_new_instrument_class": True, "no_reactivation": True,
        "no_parking_as_active": True, "no_pivot_to_new_family": True, "no_stage": True,
        "no_commit": True, "no_push": True, "no_auto_commit": True,
        "no_auto_push": True, "no_broker": True, "no_credentials": True,
        "no_order_logic": True, "no_auto_trading": True, "no_paper_trading": True,
        "no_live_trading": True, "no_gate_skip": True, "no_start_c22": True,
        "no_downstream_gate_unlock": True, "no_profitability_claim": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_c21_rejection_record(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the record is research-only,
    rejection-record-only, chain-gated on the frozen replay review carrying NOT-all-pass
    decisive gates + REJECT + does-not-beat-null, keeps the candidate not-active /
    not-parked / kept-on-record, records REJECT_C21_AT_FEE_HONEST_REPLAY with the
    EDGE_DOES_NOT_BEAT... reason code anchored to the frozen replay artifact SHAs (and
    preserves the labels commit), preserves the verbatim conclusion + BOTH lessons + the
    honest replay facts (it cannot be flipped to a profitability/edge claim or to "beats
    the null" while the strategy loses to the null and the OOS fails), cites the 4 pushed
    gate commits, applies the 25->26 ledger bump, sets active candidate none / next =
    C22 proposal readiness only, is not a C20 rescue, does not start C22 or pivot, and
    pins every capability flag False."""
    failures: list = []
    if record.get("mode") != RJ21_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_rejection_record_only") is not True:
        failures.append("not_rejection_record_only")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("verdict") != VERDICT_RJ21_RECORDED:
        failures.append("verdict_not_reject_c21_at_replay")
    if record.get("rejection_status") != REJECTION_STATUS:
        failures.append("status_not_rejected_at_replay")
    if record.get("rejected_at_stage") != REJECTED_AT_STAGE:
        failures.append("rejected_stage_not_fee_honest_replay")
    if record.get("rejection_reason_code") != REJECTION_REASON_CODE:
        failures.append("rejection_reason_code_wrong")

    # not active / not parked / kept on record
    if record.get("is_active_candidate") is not False:
        failures.append("must_not_be_active")
    if record.get("parked_as_active") is not False:
        failures.append("must_not_be_parked")
    if record.get("kept_on_record") is not True:
        failures.append("must_be_kept_on_record")

    # chain gate on the frozen replay review carrying NOT-all-pass gates + REJECT
    if record.get("replay_review_verdict") != VERDICT_C21R_FROZEN:
        failures.append("replay_review_not_frozen")
    if record.get("replay_review_valid") is not True:
        failures.append("replay_review_not_valid")
    if record.get("replay_all_decisive_gates_pass") is not False:
        failures.append("replay_gates_should_not_all_pass")
    if record.get("replay_recommended_decision") != "REJECT":
        failures.append("replay_should_recommend_reject")
    if record.get("replay_strategy_beats_null") is not False:
        failures.append("replay_should_not_beat_null")

    # anchored to the frozen replay artifact SHAs + labels commit preserved
    if record.get("anchored_to_replay_ledger_sha256") != ANCHORED_TO_REPLAY_LEDGER_SHA256:
        failures.append("replay_ledger_anchor_tampered")
    if record.get("anchored_to_replay_summary_sha256") != ANCHORED_TO_REPLAY_SUMMARY_SHA256:
        failures.append("replay_summary_anchor_tampered")
    if record.get("preserved_labels_commit") != LABELS_COMMIT:
        failures.append("labels_commit_not_preserved")

    # verbatim conclusion + BOTH preserved lessons
    if record.get("conclusion") != CONCLUSION:
        failures.append("conclusion_tampered")
    if record.get("preserved_lesson_low_turnover_fixes_churn") != PRESERVED_LESSON_LOW_TURNOVER:
        failures.append("low_turnover_lesson_tampered")
    if record.get("preserved_lesson_no_timing_edge_over_null") != PRESERVED_LESSON_NO_TIMING_EDGE:
        failures.append("no_edge_lesson_tampered")
    if record.get("rejects_lack_of_edge_not_the_carry_source") is not True:
        failures.append("must_scope_rejection_to_lack_of_edge")
    if record.get("carry_source_is_real_but_free_and_oos_fragile") is not True:
        failures.append("must_preserve_carry_source_real")
    if record.get("low_turnover_design_worked") is not True:
        failures.append("must_credit_low_turnover_design")

    # preserved honest facts -- cannot be flipped
    eh = record.get("evidence_headline") or {}
    for k in ("low_turnover_preserved_carry_net_positive",
              "does_not_beat_always_on_null", "forward_oos_failed",
              "carry_source_real_null_positive", "cost_no_longer_dominates",
              "not_a_pipeline_artifact"):
        if eh.get(k) is not True:
            failures.append("rejection_finding_cleared_%s" % k)
    if eh.get("all_decisive_gates_passed") is not False:
        failures.append("evidence_must_not_claim_all_gates_passed")
    if len(record.get("rejection_reasons") or []) < 4:
        failures.append("rejection_reasons_missing")

    # pinned numbers intact + genuinely a rejection: net-positive BUT below the null +
    # OOS negative (the honest C21 shape -- distinct from C20's net-negative).
    if record.get("trade_count") != TRADE_COUNT:
        failures.append("trade_count_tampered")
    if record.get("strategy_net_return") != STRATEGY_NET_RETURN:
        failures.append("strategy_net_tampered")
    if record.get("strategy_net_return", -1) <= 0:
        failures.append("strategy_net_should_be_positive_low_turnover_worked")
    if record.get("random_null_net_return") != NULL_NET_RETURN:
        failures.append("null_net_tampered")
    if record.get("strategy_net_return", 0) >= record.get("random_null_net_return", 0):
        failures.append("strategy_should_not_beat_null_net")
    if record.get("strategy_sharpe", 0) >= record.get("random_null_sharpe", -99):
        failures.append("strategy_should_lose_to_null_sharpe")
    if record.get("forward_oos_net_return", 0) > 0:
        failures.append("forward_oos_should_be_negative")

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

    # ledger bump applied in this bundle (25 -> 26)
    lb = record.get("ledger_bump") or {}
    if lb.get("to_count") != 26 or lb.get("from_count") != 25:
        failures.append("ledger_bump_counts_wrong")
    if lb.get("add_family") != REJECTED_FAMILY_NAME:
        failures.append("ledger_bump_family_wrong")

    # active none; next = C22 proposal readiness only; not a C20 rescue; no C22/pivot
    if record.get("active_candidate_after_rejection") is not None:
        failures.append("active_candidate_should_be_none")
    if record.get("next_stage") != "candidate_22_proposal_readiness":
        failures.append("next_stage_not_c22_proposal_readiness")
    if record.get("c22_proposal_readiness_only_not_implementation") is not True:
        failures.append("c22_must_be_proposal_readiness_only")
    if record.get("is_rescue_or_retune_of_c20") is not False:
        failures.append("must_not_be_c20_rescue")
    if record.get("c20_remains_rejected") is not True:
        failures.append("c20_must_remain_rejected")
    if record.get("does_not_start_c22") is not True:
        failures.append("must_not_start_c22")
    if record.get("c22_candidate_id") is not None:
        failures.append("c22_must_be_none")
    if record.get("does_not_pivot_to_new_family") is not True:
        failures.append("must_not_pivot_to_new_family")

    # gates locked
    for gate in ("labels_gate_locked", "replay_gate_locked",
                 "robustness_gate_locked", "promote_gate_locked",
                 "paper_trading_gate_locked", "live_gate_locked"):
        if record.get(gate) is not True:
            failures.append("gate_unlocked_%s" % gate)

    locks = record.get("scope_locks") or {}
    for key in ("no_replay", "no_re_replay", "no_pnl", "no_change_fee", "no_drop_cost",
                "no_re_detect", "no_relabel", "no_optimization", "no_tuning",
                "no_rescue", "no_rescue_c20", "no_parameter_sweep", "no_data_fetch",
                "no_data_commit", "no_xauusd", "no_reactivation",
                "no_pivot_to_new_family", "no_commit", "no_push", "no_broker",
                "no_order_logic", "no_auto_trading", "no_paper_trading",
                "no_live_trading", "no_gate_skip", "no_start_c22"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
