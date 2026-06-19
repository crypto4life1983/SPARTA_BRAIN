"""Candidate #18 -- h4_trend_following_market_structure_v1
-- FORMAL REJECTION / CLOSEOUT RECORD (PURE, RESEARCH ONLY).

Records the formal closeout of Candidate #18 as REJECTED AT THE FEE-HONEST REPLAY
STAGE (kept on record). Chain-gated on the FROZEN replay results review carrying
all_decisive_gates_pass == False and decisive_rejection_pressure == True.

It does NOTHING else: NO re-replay, NO PnL, NO re-detect, NO relabel, NO
optimization, NO re-parameterization, NO data fetch, NO writes, NO stage/commit/
push, and NO paper/live/broker/order surface. It only PRESERVES the honest replay
result and the research lesson, anchors the rejection to the committed replay-review
commit, and preserves the labels-review commit reference. Every capability flag is
pinned False with a full scope_locks set.

HONEST RESULT PRESERVED: the H4 market-structure trend-following detector cleared
the labels structural gate but was rejected at fee-honest replay. Over the frozen
BTCUSDT 4h window (2019-2026), net of 37 bps, it made +95.4% (CAGR ~9.4%) yet did
NOT beat BTC buy-and-hold (Sharpe 0.52 vs 0.93, Calmar 0.25 vs 0.60) on a
RISK-ADJUSTED basis; its only structural win was a lower max drawdown (-38.2% vs
-77.0%), and the 2026 forward-OOS edge did not hold (Sharpe -2.27 vs -1.47). Win
rate 15.2%, total R -101.4, avg R -0.26.

This rejects the OBJECTIVE C18 APPROXIMATION of an observed profitable trader's
H4 method -- it does NOT reject, reproduce, or disprove that trader's exact private
system; the approximation simply did not show a durable risk-adjusted edge over
holding BTC under honest costs.

LESSON: a no-indicator H4 trend-following / add-to-winners approximation can post a
large raw return in a bull window while still LOWERING risk-adjusted return vs simply
holding the asset; structural stops bled faster than pyramided winners recovered
(avg R negative), and lower drawdown ALONE -- while also lower Sharpe AND Calmar --
is not an edge.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.h4_trend_following_market_structure_v1_replay_results_review_contract as _r18  # noqa: E501

RJ18_SCHEMA_VERSION = 1
RJ18_MODE = "RESEARCH_ONLY"
RJ18_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = _r18.CANDIDATE_ID
CANDIDATE_FAMILY = _r18.CANDIDATE_FAMILY
CANDIDATE_NAME = _r18.CANDIDATE_NAME

VERDICT_RJ18_RECORDED = "REJECT_C18_AT_FEE_HONEST_REPLAY"
VERDICT_C18R_FROZEN = _r18.VERDICT_C18R_FROZEN
REJECTION_STATUS = "REJECTED_AT_FEE_HONEST_REPLAY_KEPT_ON_RECORD"
REJECTED_AT_STAGE = "fee_honest_replay"
REJECTED_FAMILY_NAME = "h4_trend_following_market_structure"

# pinned commits the rejection is anchored to (committed + pushed on origin)
REPLAY_REVIEW_COMMIT = "e22510521c9d954b36e52200c1dbcee498be5f82"
LABELS_REVIEW_COMMIT = "0e1377284ea865ac33a7988c61b5da7dc2417230"

NEXT_REQUIRED_ACTION = (
    "NONE__C18_CLOSED__REJECTED_AT_FEE_HONEST_REPLAY__KEPT_ON_RECORD_AS_H4_TREND_"
    "FOLLOWING_APPROXIMATION_DOES_NOT_BEAT_BTC_BUY_AND_HOLD_RISK_ADJUSTED_RESEARCH_"
    "LESSON")

CONCLUSION = (
    "The objective H4 market-structure trend-following approximation made +95.4% net "
    "of 37 bps but did not beat BTC buy-and-hold on a risk-adjusted basis (Sharpe "
    "0.52 vs 0.93, Calmar 0.25 vs 0.60); its only structural win was a lower max "
    "drawdown (-38.2% vs -77.0%) and the 2026 forward-OOS edge did not hold (Sharpe "
    "-2.27). Win rate was 15.2% with total R -101.4 (avg R -0.26): structural stops "
    "bled faster than pyramided winners recovered. Lower drawdown alone is not a "
    "durable edge over simply holding BTC. This rejects the OBJECTIVE approximation, "
    "NOT the observed trader's exact private system.")

# --- pinned honest metrics (from the frozen replay review) ------------------
STRATEGY_METRICS = dict(_r18.STRATEGY_METRICS)
BUY_AND_HOLD_METRICS = dict(_r18.BUY_AND_HOLD_METRICS)
STRATEGY_FORWARD_OOS_METRICS = dict(_r18.STRATEGY_FORWARD_OOS_METRICS)
BUY_AND_HOLD_FORWARD_OOS_METRICS = dict(_r18.BUY_AND_HOLD_FORWARD_OOS_METRICS)
WIN_RATE = _r18.WIN_RATE
TOTAL_R = _r18.TOTAL_R
AVG_R = _r18.AVG_R
TRADE_COUNT = _r18.TRADE_COUNT

# --- pushed evidence chain (the gates committed + pushed on origin) ----------
PUSHED_EVIDENCE_CHAIN = (
    {"stage": "family_proposal",
     "commit": "4e5aae809d7c02e51a6e0fc9f1de0385be6b6b4d"},
    {"stage": "candidate_spec",
     "commit": "6f994e2f00828773d17700d1ad427e72f1c4c336"},
    {"stage": "detector_spec_and_synthetic_dry_run",
     "commit": "713c98a84de02826904c2ddb7d84c4b37a9e1469"},
    {"stage": "real_candle_labels_review",
     "commit": "0e1377284ea865ac33a7988c61b5da7dc2417230"},
    {"stage": "fee_honest_replay_review",
     "commit": "e22510521c9d954b36e52200c1dbcee498be5f82"},
)

# This rejected family extends the canonical rejected ledger to 23 (C1-C18). This
# bundle applies that bump in the REP / SARA / lane / integration ledgers.
LEDGER_BUMP = {
    "from_count": 22, "to_count": 23, "add_family": REJECTED_FAMILY_NAME,
    "applied_in_this_bundle": True,
}

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "re_replays", "computes_pnl", "re_detects",
    "relabels", "re_allocates", "runs_labels", "runs_backtest",
    "optimizes_parameters", "reparameterizes", "runs_robustness", "fetches_data",
    "reads_real_data", "mutates_data", "stages_data", "auto_commits", "auto_pushes",
    "applies_cost_model", "modifies_scheduler", "sends_notifications", "calls_api",
    "uses_network", "uses_credentials", "connects_broker", "connects_exchange",
    "uses_real_money", "places_orders", "contains_order_logic", "auto_trading",
    "paper_trading", "live_trading", "deploys_capital", "promotes_gate",
    "unlocks_downstream_gate", "skips_any_gate", "reactivates_candidate",
    "parks_as_active", "advances_without_human_approval", "claims_profitability",
    "claims_edge", "rejects_observed_traders_exact_system",
    "crosses_into_forbidden_gate",
)


def get_candidate_18_rejection_record_label() -> str:
    return (
        "Candidate #18 h4_trend_following_market_structure_v1 rejection record "
        "(READ-ONLY, RESEARCH ONLY). "
        "REJECTED_AT_FEE_HONEST_REPLAY_KEPT_ON_RECORD -- NOT AN ACTIVE CANDIDATE. "
        "Made +95.4% but did not beat BTC buy-and-hold (Sharpe 0.52 vs 0.93, Calmar "
        "0.25 vs 0.60) risk-adjusted and the 2026 forward-OOS edge did not hold: "
        "lower drawdown alone is not an edge over holding BTC. Rejects the OBJECTIVE "
        "approximation, NOT the observed trader's exact private system. NOT a "
        "profitability claim. NOT a paper/live-readiness claim.")


def get_candidate_18_rejection_record_next_action() -> str:
    return NEXT_REQUIRED_ACTION


def build_c18_rejection_record(repo_root: Any = ".",
                               tracked_paths: list | None = None) -> dict[str, Any]:
    """Assemble the frozen C18 rejection / closeout record. Pure; no I/O; chain-
    gated on the frozen decisive-rejection replay review."""
    replay = _r18.build_c18_replay_review(repo_root, tracked_paths)
    replay_valid = _r18.validate_c18_replay_review(replay)["valid"]

    blockers: list = []
    if not replay_valid:
        blockers.append("c18_replay_review_invalid")
    if replay.get("verdict") != VERDICT_C18R_FROZEN:
        blockers.append("c18_replay_review_not_frozen")
    if replay.get("all_decisive_gates_pass") is not False:
        blockers.append("replay_unexpectedly_passed")
    if replay.get("decisive_rejection_pressure") is not True:
        blockers.append("replay_not_decisively_rejected")

    s = STRATEGY_METRICS
    bh = BUY_AND_HOLD_METRICS

    record: dict[str, Any] = {
        "schema_version": RJ18_SCHEMA_VERSION, "mode": RJ18_MODE, "lane": RJ18_LANE,
        "label": get_candidate_18_rejection_record_label(),
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "candidate_name": CANDIDATE_NAME,
        "is_rejection_record_only": True,
        "blockers": blockers,
        "verdict": (VERDICT_RJ18_RECORDED if not blockers
                    else "C18_REJECTION_BLOCKED"),
        "rejection_status": REJECTION_STATUS,
        "rejected_at_stage": REJECTED_AT_STAGE,
        "is_active_candidate": False,
        "parked_as_active": False,
        "kept_on_record": True,
        "original_frozen_c18_result_unchanged": True,
        "added_to_rejected_family_ledger": True,
        # honesty boundary: rejects the approximation, not the trader's system
        "rejects_objective_approximation_only": True,
        "does_not_reject_observed_traders_exact_system": True,
        "is_objective_approximation_not_exact_system": True,
        # chain provenance + anchors
        "replay_review_verdict": replay.get("verdict"),
        "replay_review_valid": replay_valid,
        "replay_all_decisive_gates_pass": replay.get("all_decisive_gates_pass"),
        "replay_decisive_rejection_pressure":
            replay.get("decisive_rejection_pressure"),
        "anchored_to_replay_review_commit": REPLAY_REVIEW_COMMIT,
        "labels_review_commit": LABELS_REVIEW_COMMIT,
        # verbatim conclusion + lesson
        "conclusion": CONCLUSION,
        "kept_on_record_as": [
            "RISK MANAGEMENT WORKED: max drawdown cut to -38.2% (vs -77.0% "
            "buy-and-hold) -- the strategy's only structural win",
            "but the RISK-ADJUSTED comparison FAILED: lower Sharpe AND lower Calmar "
            "than BTC buy-and-hold",
            "and the 2026 forward-OOS edge did not hold (Sharpe -2.27 vs -1.47) -- "
            "lower drawdown alone is not an edge over simply holding BTC",
            "win rate 15.2%, total R -101.4, avg R -0.26: structural stops bled "
            "faster than pyramided winners recovered",
        ],
        "rejection_reasons": [
            "DID NOT BEAT BTC BUY-AND-HOLD risk-adjusted: strategy Sharpe %.2f / "
            "Calmar %.2f vs %.2f / %.2f" % (
                s["sharpe"], s["calmar"], bh["sharpe"], bh["calmar"]),
            "2026 FORWARD-OOS edge did not hold (strategy Sharpe %.2f vs "
            "buy-and-hold %.2f)" % (
                STRATEGY_FORWARD_OOS_METRICS["sharpe"],
                BUY_AND_HOLD_FORWARD_OOS_METRICS["sharpe"]),
            "NEGATIVE expectancy under honest costs: win rate %.1f%%, total R %.1f, "
            "avg R %.2f" % (WIN_RATE * 100.0, TOTAL_R, AVG_R),
            "lower drawdown ALONE is not an edge; raw +95.4% return alone is not "
            "sufficient",
        ],
        "evidence_headline": {
            "did_not_beat_buy_and_hold_risk_adjusted":
                s["sharpe"] < bh["sharpe"] and s["calmar"] < bh["calmar"],
            "forward_oos_edge_failed":
                STRATEGY_FORWARD_OOS_METRICS["sharpe"] < 0,
            "negative_expectancy_under_costs": TOTAL_R < 0 and AVG_R < 0,
            "only_win_is_lower_drawdown": s["max_drawdown"] > bh["max_drawdown"],
            "cost_model_applied_37bps": True,
        },
        # pinned numbers
        "strategy_metrics": dict(STRATEGY_METRICS),
        "buy_and_hold_metrics": dict(BUY_AND_HOLD_METRICS),
        "strategy_forward_oos_metrics": dict(STRATEGY_FORWARD_OOS_METRICS),
        "buy_and_hold_forward_oos_metrics": dict(BUY_AND_HOLD_FORWARD_OOS_METRICS),
        "win_rate": WIN_RATE, "total_R": TOTAL_R, "avg_R": AVG_R,
        "trade_count": TRADE_COUNT,
        # evidence chain + ledger bump
        "pushed_evidence_chain": [dict(e) for e in PUSHED_EVIDENCE_CHAIN],
        "rejected_family_name": REJECTED_FAMILY_NAME,
        "ledger_bump": dict(LEDGER_BUMP),
        "raw_return_alone_is_not_sufficient": True,
        "claim_locks": [
            "no_profitability_claim", "kept_on_record_not_active_candidate",
            "not_parked_as_active", "risk_adjusted_failure_disclosed",
            "forward_oos_failure_disclosed", "negative_expectancy_disclosed",
            "lower_drawdown_alone_not_an_edge",
            "rejects_approximation_not_traders_exact_system",
            "conclusion_recorded_precisely",
        ],
        "human_review_required": True,
        "current_loop_stage": "rejection_record",
        "next_required_action": NEXT_REQUIRED_ACTION,
        # gates locked
        "replay_gate_locked": True, "robustness_gate_locked": True,
        "promote_gate_locked": True, "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True, "live_gate_locked": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_re_replay": True, "no_pnl": True, "no_re_detect": True,
        "no_relabel": True, "no_re_allocate": True, "no_optimization": True,
        "no_reparameterization": True, "no_robustness_run": True,
        "no_data_fetch": True, "no_data_mutation": True, "no_cost_recompute": True,
        "no_reactivation": True, "no_parking_as_active": True, "no_stage": True,
        "no_commit": True, "no_push": True, "no_auto_commit": True,
        "no_auto_push": True, "no_broker": True, "no_credentials": True,
        "no_order_logic": True, "no_auto_trading": True, "no_paper_trading": True,
        "no_live_trading": True, "no_xauusd": True, "no_gate_skip": True,
        "no_downstream_gate_unlock": True, "no_profitability_claim": True,
        "no_rejecting_traders_exact_system": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_c18_rejection_record(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the record is research-only,
    rejection-record-only, chain-gated on the frozen decisive-rejection replay
    review, keeps the candidate not-active / not-parked / kept-on-record, records
    REJECT_C18_AT_FEE_HONEST_REPLAY anchored to the pushed replay-review commit,
    preserves the verbatim conclusion + the risk-adjusted / forward-OOS / negative-
    expectancy failure facts (none can be flipped), states it rejects the OBJECTIVE
    approximation and NOT the observed trader's exact system, cites the 5 pushed gate
    commits, applies the 22->23 ledger bump, and pins every capability flag False."""
    failures: list = []
    if record.get("mode") != RJ18_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_rejection_record_only") is not True:
        failures.append("not_rejection_record_only")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("verdict") != VERDICT_RJ18_RECORDED:
        failures.append("verdict_not_reject_c18_at_replay")
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

    # honesty boundary: rejects the approximation, NOT the trader's exact system
    if record.get("rejects_objective_approximation_only") is not True:
        failures.append("must_reject_approximation_only")
    if record.get("does_not_reject_observed_traders_exact_system") is not True:
        failures.append("must_not_reject_traders_exact_system")

    # chain gate on the decisive-rejection replay review
    if record.get("replay_review_verdict") != VERDICT_C18R_FROZEN:
        failures.append("replay_review_not_frozen")
    if record.get("replay_review_valid") is not True:
        failures.append("replay_review_not_valid")
    if record.get("replay_all_decisive_gates_pass") is not False:
        failures.append("replay_unexpectedly_passed")
    if record.get("replay_decisive_rejection_pressure") is not True:
        failures.append("replay_not_decisively_rejected")

    # anchored to the pushed commits
    if record.get("anchored_to_replay_review_commit") != REPLAY_REVIEW_COMMIT:
        failures.append("replay_anchor_commit_tampered")
    if record.get("labels_review_commit") != LABELS_REVIEW_COMMIT:
        failures.append("labels_commit_reference_tampered")

    # verbatim conclusion
    if record.get("conclusion") != CONCLUSION:
        failures.append("conclusion_tampered")

    # preserved decisive failure facts -- cannot be flipped
    eh = record.get("evidence_headline") or {}
    for k in ("did_not_beat_buy_and_hold_risk_adjusted", "forward_oos_edge_failed",
              "negative_expectancy_under_costs", "only_win_is_lower_drawdown",
              "cost_model_applied_37bps"):
        if eh.get(k) is not True:
            failures.append("rejection_finding_cleared_%s" % k)
    if record.get("raw_return_alone_is_not_sufficient") is not True:
        failures.append("raw_return_sufficiency_flag_wrong")
    if len(record.get("rejection_reasons") or []) < 3:
        failures.append("rejection_reasons_missing")

    # pinned metrics intact + genuinely a rejection
    s = record.get("strategy_metrics") or {}
    bh = record.get("buy_and_hold_metrics") or {}
    if s.get("sharpe") != STRATEGY_METRICS["sharpe"]:
        failures.append("strategy_sharpe_tampered")
    if s.get("sharpe", 9) >= bh.get("sharpe", 0) and s.get("calmar", 9) >= bh.get(
            "calmar", 0):
        failures.append("metrics_inconsistent_with_rejection")
    if record.get("total_R", 0) >= 0 or record.get("avg_R", 0) >= 0:
        failures.append("expectancy_not_negative")

    # pushed evidence chain: 5 gate commits, each a 40-char sha
    chain = record.get("pushed_evidence_chain") or []
    stages = {e.get("stage"): e.get("commit") for e in chain}
    for required in ("family_proposal", "candidate_spec",
                     "detector_spec_and_synthetic_dry_run",
                     "real_candle_labels_review", "fee_honest_replay_review"):
        if required not in stages:
            failures.append("pushed_chain_missing_%s" % required)
        elif not (isinstance(stages[required], str)
                  and len(stages[required]) == 40):
            failures.append("pushed_chain_bad_commit_%s" % required)

    # ledger bump applied in this bundle (22 -> 23)
    lb = record.get("ledger_bump") or {}
    if lb.get("to_count") != 23 or lb.get("from_count") != 22:
        failures.append("ledger_bump_counts_wrong")
    if lb.get("add_family") != REJECTED_FAMILY_NAME:
        failures.append("ledger_bump_family_wrong")

    # gates locked
    for gate in ("replay_gate_locked", "robustness_gate_locked",
                 "promote_gate_locked", "paper_trading_gate_locked",
                 "micro_live_gate_locked", "live_gate_locked"):
        if record.get(gate) is not True:
            failures.append("gate_unlocked_%s" % gate)

    locks = record.get("scope_locks") or {}
    for key in ("no_re_replay", "no_pnl", "no_re_detect", "no_relabel",
                "no_re_allocate", "no_optimization", "no_reparameterization",
                "no_reactivation", "no_commit", "no_push", "no_broker",
                "no_order_logic", "no_auto_trading", "no_paper_trading",
                "no_live_trading", "no_xauusd", "no_gate_skip"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
