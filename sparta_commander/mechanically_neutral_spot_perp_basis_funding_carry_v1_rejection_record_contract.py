"""Candidate #20 -- mechanically_neutral_spot_perp_basis_funding_carry_v1
-- FORMAL REJECTION / CLOSEOUT RECORD (PURE, RESEARCH ONLY).

Records the formal closeout of Candidate #20 as REJECTED AT THE FEE-HONEST REPLAY STAGE
(kept on record). Chain-gated on the FROZEN replay results review carrying
all_decisive_gates_pass == False and recommended_decision == REJECT.

It does NOTHING else: NO replay re-run, NO PnL recompute, NO fee change/drop, NO
re-detect, NO relabel, NO optimization / tuning / rescue / parameter change, NO data
fetch, NO writes, NO stage/commit/push, NO paper/live/broker/order surface, and it does
NOT start C21 and does NOT pivot to a new family. It only PRESERVES the honest replay
result and the research lesson, anchors the rejection to the committed replay-review
commit, and preserves the upstream C20 gate commit references. Every capability flag is
pinned False with a full scope_locks set.

HONEST RESULT PRESERVED: applying the reserved 37 bps all-in cost PER LEG (74 bps
round-trip per trade, two legs) to the 704 frozen trades produced a portfolio net return
of -74.5% (Sharpe -12.84, Calmar -0.285, max DD -74.5%); the 2026 forward-OOS failed (net
-8.3%, Sharpe -12.2, 35 trades, 0% win rate); all four decisive gates failed, and the
strategy lost badly to the random/null always-on neutral-carry baseline (+21.2%, Sharpe
1.09). The mechanically-neutral CARRY ITSELF is real -- the always-on null is positive
(BTC/ETH funding, null Sharpe ~8) -- so this rejects the C20 entry/exit TIMING (704
round-trips x 74 bps = 521% cost drag destroyed the carry), NOT the same-asset carry
thesis. PRESERVED POSITIVE LESSON: a LOW-TURNOVER always-on neutral carry appears
promising (especially BTC/ETH) and may deserve a SEPARATE future candidate ONLY under
explicit human approval.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.mechanically_neutral_spot_perp_basis_funding_carry_v1_replay_results_review_contract as _r20  # noqa: E501

RJ20_SCHEMA_VERSION = 1
RJ20_MODE = "RESEARCH_ONLY"
RJ20_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = _r20.CANDIDATE_ID
CANDIDATE_FAMILY = _r20.CANDIDATE_FAMILY
CANDIDATE_NAME = _r20.CANDIDATE_NAME

VERDICT_RJ20_RECORDED = "REJECT_C20_AT_FEE_HONEST_REPLAY"
VERDICT_C20R_FROZEN = _r20.VERDICT_C20R_FROZEN
REJECTION_STATUS = "REJECTED_AT_FEE_HONEST_REPLAY_KEPT_ON_RECORD"
REJECTED_AT_STAGE = "fee_honest_replay"
REJECTED_FAMILY_NAME = "mechanically_neutral_spot_perp_basis_funding_carry"

# pinned commit the rejection is anchored to (committed + pushed on origin)
REPLAY_REVIEW_COMMIT = "59de8da7deb3cc25f951702bce63155235313052"

# upstream C20 gate commits (preserved provenance)
PUSHED_EVIDENCE_CHAIN = (
    {"stage": "family_proposal",
     "commit": "ec8e95449a9ebc5b17e3a97a5d2333a560d4e3c5"},
    {"stage": "candidate_spec",
     "commit": "dfd4529aa30ad5c2da3caaceb52f987a2bb31c40"},
    {"stage": "detector_spec_dry_run",
     "commit": "9b9cc18a7af4a914f067e59d3c5440960fb08cc8"},
    {"stage": "real_candle_labels_review",
     "commit": "ead1bdb72ef5f9a78c1489f2a7701b5cd6e60c68"},
    {"stage": "fee_honest_replay_review",
     "commit": "59de8da7deb3cc25f951702bce63155235313052"},
)
# the preserved C20 labels commit (explicitly required to be preserved)
LABELS_COMMIT = "ead1bdb72ef5f9a78c1489f2a7701b5cd6e60c68"

# pinned honest replay metrics (from the frozen replay review)
TRADE_COUNT = _r20.TRADE_COUNT                         # 704
STRATEGY_NET_RETURN = _r20.STRATEGY_METRICS["net_return"]      # -0.7452
STRATEGY_SHARPE = _r20.STRATEGY_METRICS["sharpe"]             # -12.836936
STRATEGY_CALMAR = _r20.STRATEGY_METRICS["calmar"]            # -0.284585
STRATEGY_MAX_DD = _r20.STRATEGY_METRICS["max_drawdown"]       # -0.745453
NULL_NET_RETURN = _r20.RANDOM_NULL_METRICS["net_return"]      # 0.211648
NULL_SHARPE = _r20.RANDOM_NULL_METRICS["sharpe"]             # 1.087808
OOS_NET_RETURN = _r20.STRATEGY_FORWARD_OOS_METRICS["net_return"]   # -0.082992
OOS_SHARPE = _r20.STRATEGY_FORWARD_OOS_METRICS["sharpe"]      # -12.156854
OOS_WIN_RATE = _r20.FORWARD_OOS_WIN_RATE                      # 0.0
OOS_TRADE_COUNT = _r20.FORWARD_OOS_TRADE_COUNT               # 35
TOTAL_COST_DRAG = _r20.TOTAL_COST_DRAG                       # 5.2096
FUNDING_CONTRIBUTION = _r20.FUNDING_CONTRIBUTION_TOTAL        # 0.797538
ROUND_TRIP_COST_PER_TRADE_BPS = _r20.ROUND_TRIP_COST_PER_TRADE_BPS  # 74.0

NEXT_REQUIRED_ACTION = (
    "NONE__C20_CLOSED__REJECTED_AT_FEE_HONEST_REPLAY__KEPT_ON_RECORD__TIMING_CHURN_"
    "DESTROYS_REAL_CARRY__LOW_TURNOVER_ALWAYS_ON_CARRY_IS_A_SEPARATE_FUTURE_CANDIDATE_"
    "ONLY_WITH_EXPLICIT_HUMAN_APPROVAL")

CONCLUSION = (
    "The mechanically-neutral same-asset spot/perp basis + funding-carry family cleared "
    "every prior structural gate (704 entries, mechanical neutrality 100% by "
    "construction) but FAILED the fee-honest replay: applying the reserved 37 bps "
    "all-in cost PER LEG (74 bps round-trip per trade, two legs) to the 704 frozen "
    "trades produced a portfolio net -74.5% (Sharpe -12.84, Calmar -0.285, max DD "
    "-74.5%), and the 2026 forward-OOS failed (net -8.3%, Sharpe -12.2, 35 trades, 0% "
    "win rate). All four decisive gates failed and the strategy lost badly to the "
    "random/null always-on neutral-carry baseline (+21.2%, Sharpe 1.09). The carry "
    "itself is real -- the always-on null is positive (BTC/ETH funding) -- so the "
    "entry/exit TIMING is what fails: 704 round-trips x 74 bps = 521% cost drag "
    "destroyed the ~80% gross funding collected. This rejects the C20 TIMING/churn, NOT "
    "the same-asset carry thesis.")

# the preserved positive research lesson (explicitly required)
PRESERVED_POSITIVE_LESSON = (
    "The always-on neutral carry (zero timing skill: hold long-spot/short-perp every "
    "day, harvest funding) is POSITIVE and risk-adjusted attractive -- +21.2% net, "
    "Sharpe 1.09 at the portfolio level, with BTC and ETH null Sharpe ~8 each (SOL "
    "weaker). The killer for C20 was CHURN COST, not signal: a LOW-TURNOVER / always-on "
    "neutral carry (far fewer round-trips, so the 74 bps two-leg cost does not dominate) "
    "may deserve a SEPARATE future candidate -- but only under an explicit human "
    "open-candidate approval, and it must still clear fee-honest replay incl. funding "
    "regime risk, perp borrow, and liquidation-aware costs not fully charged to the "
    "always-on null here.")

# This rejected family extends the canonical rejected ledger to 25 (C1-C20). This
# bundle applies that bump in the REP / SARA / lane / integration ledgers.
LEDGER_BUMP = {
    "from_count": 24, "to_count": 25, "add_family": REJECTED_FAMILY_NAME,
    "applied_in_this_bundle": True,
}

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "runs_replay", "re_runs_replay", "computes_pnl",
    "recomputes_pnl", "changes_fee", "drops_cost", "re_detects", "relabels",
    "rebuilds_detector", "runs_labels", "runs_backtest", "optimizes_parameters",
    "reparameterizes", "tunes_parameters", "runs_rescue", "runs_parameter_sweep",
    "runs_robustness", "fetches_data", "reads_real_data", "mutates_data",
    "stages_data", "commits_data_artifact", "auto_commits", "auto_pushes",
    "applies_cost_model", "modifies_scheduler", "sends_notifications", "calls_api",
    "uses_network", "uses_credentials", "connects_broker", "connects_exchange",
    "uses_real_money", "places_orders", "contains_order_logic", "auto_trading",
    "uses_xauusd", "adds_new_instrument_class", "paper_trading", "live_trading",
    "deploys_capital", "promotes_gate", "unlocks_downstream_gate", "skips_any_gate",
    "reactivates_candidate", "parks_as_active", "starts_c21",
    "pivots_to_new_family", "advances_without_human_approval", "claims_profitability",
    "claims_edge", "crosses_into_forbidden_gate",
)


def get_candidate_20_rejection_record_label() -> str:
    return (
        "Candidate #20 mechanically_neutral_spot_perp_basis_funding_carry_v1 rejection "
        "record (READ-ONLY, RESEARCH ONLY). REJECTED_AT_FEE_HONEST_REPLAY_KEPT_ON_RECORD "
        "-- NOT AN ACTIVE CANDIDATE. The timed strategy net -74.5% (Sharpe -12.84) after "
        "the 74 bps two-leg cost on 704 trades (521% cost drag), 2026 forward-OOS -8.3% "
        "/ 0% win, all four decisive gates fail, losing to the random/null always-on "
        "carry (+21.2%, Sharpe 1.09). Rejects the TIMING/churn, NOT the carry thesis -- "
        "the always-on carry is real (BTC/ETH null Sharpe ~8) and a low-turnover version "
        "is a SEPARATE future candidate only with explicit human approval. NOT a "
        "profitability claim. NOT a paper/live-readiness claim.")


def get_candidate_20_rejection_record_next_action() -> str:
    return NEXT_REQUIRED_ACTION


def build_c20_rejection_record(repo_root: Any = ".",
                               tracked_paths: list | None = None) -> dict[str, Any]:
    """Assemble the frozen C20 rejection / closeout record. Pure; no I/O; chain-gated
    on the frozen replay review carrying the all-fail decisive gates + REJECT."""
    replay = _r20.build_c20_replay_review(repo_root, tracked_paths)
    replay_valid = _r20.validate_c20_replay_review(replay)["valid"]

    blockers: list = []
    if not replay_valid:
        blockers.append("c20_replay_review_invalid")
    if replay.get("verdict") != VERDICT_C20R_FROZEN:
        blockers.append("c20_replay_review_not_frozen")
    if replay.get("all_decisive_gates_pass") is not False:
        blockers.append("replay_gates_did_not_fail")
    if replay.get("recommended_decision") != "REJECT":
        blockers.append("replay_did_not_recommend_reject")
    if replay.get("strategy_metrics", {}).get("net_return", 0) >= 0:
        blockers.append("strategy_unexpectedly_profitable")

    record: dict[str, Any] = {
        "schema_version": RJ20_SCHEMA_VERSION, "mode": RJ20_MODE, "lane": RJ20_LANE,
        "label": get_candidate_20_rejection_record_label(),
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "candidate_name": CANDIDATE_NAME,
        "is_rejection_record_only": True,
        "blockers": blockers,
        "verdict": (VERDICT_RJ20_RECORDED if not blockers
                    else "C20_REJECTION_BLOCKED"),
        "rejection_status": REJECTION_STATUS,
        "rejected_at_stage": REJECTED_AT_STAGE,
        "is_active_candidate": False,
        "parked_as_active": False,
        "kept_on_record": True,
        "original_frozen_c20_result_unchanged": True,
        "added_to_rejected_family_ledger": True,
        "fee_honest_replay_was_run": True,
        # chain provenance + anchors
        "replay_review_verdict": replay.get("verdict"),
        "replay_review_valid": replay_valid,
        "replay_all_decisive_gates_pass": replay.get("all_decisive_gates_pass"),
        "replay_recommended_decision": replay.get("recommended_decision"),
        "anchored_to_replay_review_commit": REPLAY_REVIEW_COMMIT,
        "preserved_labels_commit": LABELS_COMMIT,
        # verbatim conclusion + lesson
        "conclusion": CONCLUSION,
        "preserved_positive_lesson": PRESERVED_POSITIVE_LESSON,
        "rejects_timing_not_carry_thesis": True,
        "carry_thesis_vindicated_by_positive_null": True,
        "low_turnover_carry_is_separate_future_candidate_only_with_approval": True,
        "kept_on_record_as": [
            "STRUCTURE CLEAN: 704 entries, mechanical neutrality 100% by construction, "
            "gross capped 1.0, one live position per asset, >= 5-bar spacing",
            "but the FEE-HONEST REPLAY FAILED: 74 bps round-trip per trade (two legs) "
            "x 704 trades = 521% cost drag turned +21.2% raw carry into net -74.5%",
            "2026 FORWARD-OOS FAILED: net -8.3%, Sharpe -12.2, 0% win rate",
            "LOST to the random/null always-on neutral carry (+21.2%, Sharpe 1.09) -- "
            "the carry is real, the TIMING/churn is the killer",
        ],
        "rejection_reasons": [
            "STRATEGY NET-NEGATIVE AFTER COST: portfolio net %.4f (Sharpe %.2f, Calmar "
            "%.3f, max DD %.4f)" % (STRATEGY_NET_RETURN, STRATEGY_SHARPE,
                                    STRATEGY_CALMAR, STRATEGY_MAX_DD),
            "2026 FORWARD-OOS FAILED: net %.4f, Sharpe %.2f, %d trades, %.0f%% win rate"
            % (OOS_NET_RETURN, OOS_SHARPE, OOS_TRADE_COUNT, 100.0 * OOS_WIN_RATE),
            "LOSES TO RANDOM/NULL ALWAYS-ON CARRY: null net %.4f (Sharpe %.2f) vs "
            "strategy Sharpe %.2f" % (NULL_NET_RETURN, NULL_SHARPE, STRATEGY_SHARPE),
            "COST DRAG %.2f from %d trades x %.0f bps two-leg cost destroyed the ~%.0f%% "
            "gross funding" % (TOTAL_COST_DRAG, TRADE_COUNT,
                               ROUND_TRIP_COST_PER_TRADE_BPS,
                               100.0 * FUNDING_CONTRIBUTION),
            "rejects the C20 TIMING/entry-exit, NOT the same-asset carry thesis",
        ],
        "evidence_headline": {
            "structure_clean": True,
            "strategy_net_negative_after_cost": STRATEGY_NET_RETURN < 0,
            "all_decisive_gates_failed": True,
            "forward_oos_failed": OOS_NET_RETURN <= 0,
            "loses_to_random_null_carry": STRATEGY_SHARPE < NULL_SHARPE,
            "cost_drag_dominates_funding": TOTAL_COST_DRAG > FUNDING_CONTRIBUTION,
            "carry_thesis_real_null_positive": NULL_NET_RETURN > 0,
        },
        # pinned numbers
        "trade_count": TRADE_COUNT,
        "strategy_net_return": STRATEGY_NET_RETURN,
        "strategy_sharpe": STRATEGY_SHARPE,
        "strategy_calmar": STRATEGY_CALMAR,
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
        "claim_locks": [
            "no_profitability_claim", "kept_on_record_not_active_candidate",
            "not_parked_as_active", "replay_failure_disclosed",
            "rejects_timing_not_carry_thesis", "carry_thesis_real_preserved",
            "low_turnover_carry_needs_separate_human_approval",
            "conclusion_recorded_precisely",
        ],
        "human_review_required": True,
        "current_loop_stage": "rejection_record",
        "next_required_action": NEXT_REQUIRED_ACTION,
        "does_not_start_c21": True, "c21_candidate_id": None,
        "does_not_pivot_to_new_family": True,
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
        "no_rescue": True, "no_parameter_sweep": True, "no_robustness_run": True,
        "no_data_fetch": True, "no_data_mutation": True, "no_data_commit": True,
        "no_cost_application": True, "no_xauusd": True, "no_new_instrument_class": True,
        "no_reactivation": True, "no_parking_as_active": True,
        "no_pivot_to_new_family": True, "no_stage": True, "no_commit": True,
        "no_push": True, "no_auto_commit": True, "no_auto_push": True,
        "no_broker": True, "no_credentials": True, "no_order_logic": True,
        "no_auto_trading": True, "no_paper_trading": True, "no_live_trading": True,
        "no_gate_skip": True, "no_start_c21": True, "no_downstream_gate_unlock": True,
        "no_profitability_claim": True, "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_c20_rejection_record(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the record is research-only,
    rejection-record-only, chain-gated on the frozen replay review carrying all-fail
    decisive gates + REJECT, keeps the candidate not-active / not-parked /
    kept-on-record, records REJECT_C20_AT_FEE_HONEST_REPLAY anchored to the pushed
    replay-review commit (and preserves the labels commit), preserves the verbatim
    conclusion + the positive carry lesson + the replay-failure facts (none can be
    flipped to a profitability claim while the strategy net return is negative), cites
    the 5 pushed gate commits, applies the 24->25 ledger bump, does not start C21 or
    pivot to a new family, and pins every capability flag False."""
    failures: list = []
    if record.get("mode") != RJ20_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_rejection_record_only") is not True:
        failures.append("not_rejection_record_only")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("verdict") != VERDICT_RJ20_RECORDED:
        failures.append("verdict_not_reject_c20_at_replay")
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

    # chain gate on the frozen replay review carrying the all-fail gates + REJECT
    if record.get("replay_review_verdict") != VERDICT_C20R_FROZEN:
        failures.append("replay_review_not_frozen")
    if record.get("replay_review_valid") is not True:
        failures.append("replay_review_not_valid")
    if record.get("replay_all_decisive_gates_pass") is not False:
        failures.append("replay_gates_should_have_failed")
    if record.get("replay_recommended_decision") != "REJECT":
        failures.append("replay_should_recommend_reject")

    # anchored to the pushed replay-review commit + labels commit preserved
    if record.get("anchored_to_replay_review_commit") != REPLAY_REVIEW_COMMIT:
        failures.append("replay_anchor_commit_tampered")
    if record.get("preserved_labels_commit") != LABELS_COMMIT:
        failures.append("labels_commit_not_preserved")

    # verbatim conclusion + preserved positive lesson
    if record.get("conclusion") != CONCLUSION:
        failures.append("conclusion_tampered")
    if record.get("preserved_positive_lesson") != PRESERVED_POSITIVE_LESSON:
        failures.append("positive_lesson_tampered")
    if record.get("rejects_timing_not_carry_thesis") is not True:
        failures.append("must_scope_rejection_to_timing")
    if record.get("carry_thesis_vindicated_by_positive_null") is not True:
        failures.append("must_preserve_carry_thesis_real")

    # preserved failure facts -- cannot be flipped
    eh = record.get("evidence_headline") or {}
    for k in ("structure_clean", "strategy_net_negative_after_cost",
              "all_decisive_gates_failed", "forward_oos_failed",
              "loses_to_random_null_carry", "cost_drag_dominates_funding",
              "carry_thesis_real_null_positive"):
        if eh.get(k) is not True:
            failures.append("rejection_finding_cleared_%s" % k)
    if len(record.get("rejection_reasons") or []) < 4:
        failures.append("rejection_reasons_missing")

    # pinned numbers intact + genuinely a rejection (net negative, gates fail)
    if record.get("trade_count") != TRADE_COUNT:
        failures.append("trade_count_tampered")
    if record.get("strategy_net_return") != STRATEGY_NET_RETURN:
        failures.append("strategy_net_tampered")
    if record.get("strategy_net_return", 0) >= 0:
        failures.append("strategy_net_should_be_negative")
    if record.get("random_null_net_return") != NULL_NET_RETURN:
        failures.append("null_net_tampered")
    if record.get("random_null_net_return", -1) <= 0:
        failures.append("null_should_be_positive_carry_real")
    if record.get("strategy_sharpe", 0) >= record.get("random_null_sharpe", -99):
        failures.append("strategy_should_lose_to_null")

    # pushed evidence chain: 5 gate commits, each a 40-char sha
    chain = record.get("pushed_evidence_chain") or []
    stages = {e.get("stage"): e.get("commit") for e in chain}
    for required in ("family_proposal", "candidate_spec", "detector_spec_dry_run",
                     "real_candle_labels_review", "fee_honest_replay_review"):
        if required not in stages:
            failures.append("pushed_chain_missing_%s" % required)
        elif not (isinstance(stages[required], str)
                  and len(stages[required]) == 40):
            failures.append("pushed_chain_bad_commit_%s" % required)

    # ledger bump applied in this bundle (24 -> 25)
    lb = record.get("ledger_bump") or {}
    if lb.get("to_count") != 25 or lb.get("from_count") != 24:
        failures.append("ledger_bump_counts_wrong")
    if lb.get("add_family") != REJECTED_FAMILY_NAME:
        failures.append("ledger_bump_family_wrong")

    # no C21, no pivot
    if record.get("does_not_start_c21") is not True:
        failures.append("must_not_start_c21")
    if record.get("c21_candidate_id") is not None:
        failures.append("c21_must_be_none")
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
                "no_rescue", "no_parameter_sweep", "no_data_fetch", "no_data_commit",
                "no_xauusd", "no_reactivation", "no_pivot_to_new_family", "no_commit",
                "no_push", "no_broker", "no_order_logic", "no_auto_trading",
                "no_paper_trading", "no_live_trading", "no_gate_skip", "no_start_c21"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
