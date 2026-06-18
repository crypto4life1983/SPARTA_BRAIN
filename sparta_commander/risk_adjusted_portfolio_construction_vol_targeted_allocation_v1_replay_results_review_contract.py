"""Candidate #17 -- risk_adjusted_portfolio_construction_vol_targeted_allocation_v1
-- FEE-HONEST REPLAY RESULTS REVIEW (PURE, RESEARCH ONLY).

Pins the FROZEN fee-honest replay artifact produced by
tools/c17_fee_honest_replay_once.py (the FROZEN C17 weekly allocation labels
replayed into a daily EQUITY CURVE over the SHA-pinned local BTC/ETH/SOL 1d data,
net of the reserved 37 bps cost) and records the replay-stage decisive verdict.

It is chain-gated on the frozen C17 real-candle labels review. It does NOTHING with
real data here: NO re-replay, NO relabel, NO re-allocation, NO optimization, NO
re-parameterization, NO robustness, NO writes, NO stage/commit/push, NO paper/live/
broker/order surface. It only PINS the SHAs + the risk-adjusted metrics and re-states
the decisive verdict. Every capability flag is pinned False with a full scope_locks
set. The next gate (reject / human review) needs an explicit human decision.

HONEST OUTCOME (FROZEN): the decisive RISK-ADJUSTED gates are FAILED -- a replay-stage
REJECTION. The allocator does exactly what it was built to do on the RISK axis: over
2020-10-12..2026-06-08 it runs at ~20% vol (realized 23.8%) and cuts max drawdown to
-37.8% (vs -76.6%/-79.3%/-96.3% for BTC/ETH/SOL buy-and-hold and -85.0% for the
equal-weight basket). BUT it does NOT clear the thesis bar -- it must BEAT
buy-and-hold AND the equal-weight basket on a RISK-ADJUSTED basis (Sharpe and/or
Calmar) with no worse drawdown, and it does not: strategy Sharpe 0.80 / Calmar 0.47
vs basket Sharpe 1.04 / Calmar 0.74 and best buy-and-hold (SOL) Sharpe 1.08 / Calmar
0.83. In a 2020-2026 crypto bull, de-risking and risk-parity weighting away from the
biggest winner LOWERED risk-adjusted return rather than raising it, and the 2026
forward-OOS edge does not hold (every sleeve is negative; the low-vol strategy's
Sharpe is not better than the basket's). Lower drawdown ALONE -- while also lower
Sharpe AND Calmar -- is not an edge over simply holding the basket. NOT a
profitability claim.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.risk_adjusted_portfolio_construction_vol_targeted_allocation_v1_real_candle_labels_review_contract as _l17  # noqa: E501

R17_SCHEMA_VERSION = 1
R17_MODE = "RESEARCH_ONLY"
R17_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = _l17.CANDIDATE_ID
CANDIDATE_FAMILY = _l17.CANDIDATE_FAMILY
CANDIDATE_NAME = _l17.CANDIDATE_NAME
ASSETS = tuple(_l17.ASSETS)                  # BTCUSD / ETHUSD / SOLUSD

VERDICT_C17R_FROZEN = "C17_REPLAY_FROZEN_FOR_HUMAN_REVIEW"

# --- pinned artifact provenance ---------------------------------------------
HEAD_AT_LABELS_REVIEW = "2064849719e7b09077ce2e983c6ecff22a24cd63"
LEDGER_PATH = ("data/risk_adjusted_portfolio_construction_vol_targeted_allocation_"
               "c17/replay_results/c17_replay_ledger.json")
SUMMARY_PATH = ("data/risk_adjusted_portfolio_construction_vol_targeted_allocation_"
                "c17/replay_results/c17_replay_summary.json")
EXPECTED_LEDGER_SHA256 = (
    "249ad4bf44ddb0b37b9018110509caafdde01c2ddcfc3377e365d5a09cde38ca")
EXPECTED_SUMMARY_SHA256 = (
    "b389d02d6367003ace96827ac0190d036738d21031e49146e026c049ea1c45d7")
EXPECTED_LABELS_SHA256 = _l17.EXPECTED_LABELS_SHA256
EXPECTED_SOURCE_SHA256 = dict(_l17.EXPECTED_SOURCE_SHA256)

# --- cost model (the reserved 37 bps, now APPLIED) --------------------------
FEE_ROUND_TRIP_BPS = 27.0
SLIPPAGE_ROUND_TRIP_BPS = 10.0
ALL_IN_ROUND_TRIP_BPS = 37.0
ONE_WAY_COST_BPS = 18.5

# --- pinned frozen metrics (from the real-candle replay) ---------------------
REPLAY_WINDOW = ("2020-10-12", "2026-06-08")
N_DAYS = 2066

STRATEGY_METRICS = {
    "n_days": 2066, "net_return": 1.503209, "cagr": 0.175987,
    "ann_vol": 0.237588, "sharpe": 0.80148, "max_drawdown": -0.377617,
    "calmar": 0.466046}
STRATEGY_FORWARD_OOS_METRICS = {
    "n_days": 159, "net_return": -0.241106, "cagr": -0.469184,
    "ann_vol": 0.241768, "sharpe": -2.496078, "max_drawdown": -0.303187,
    "calmar": -1.547504}
BUY_AND_HOLD_METRICS = {
    "BTCUSD": {"net_return": 4.538815, "cagr": 0.35313, "ann_vol": 0.583195,
               "sharpe": 0.809745, "max_drawdown": -0.766293, "calmar": 0.460829},
    "ETHUSD": {"net_return": 3.510002, "cagr": 0.304888, "ann_vol": 0.783567,
               "sharpe": 0.730777, "max_drawdown": -0.793025, "calmar": 0.384462},
    "SOLUSD": {"net_return": 26.532951, "cagr": 0.796299, "ann_vol": 1.132429,
               "sharpe": 1.079089, "max_drawdown": -0.962699, "calmar": 0.827152},
}
EQUAL_WEIGHT_BASKET_METRICS = {
    "net_return": 15.001686, "cagr": 0.632074, "ann_vol": 0.737415,
    "sharpe": 1.035569, "max_drawdown": -0.849797, "calmar": 0.743794}
EQUAL_WEIGHT_BASKET_FORWARD_OOS_METRICS = {
    "net_return": -0.394613, "cagr": -0.684037, "ann_vol": 0.604333,
    "sharpe": -1.600638, "max_drawdown": -0.498884, "calmar": -1.371134}

TOTAL_COST_DRAG = 0.016247
TOTAL_TURNOVER = 8.782086

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "re_replays", "relabels", "re_allocates",
    "runs_labels", "runs_detector", "runs_optimization", "reparameterizes",
    "runs_robustness", "fetches_data", "reads_real_data", "mutates_data",
    "stages_data", "auto_commits", "auto_pushes", "modifies_scheduler",
    "sends_notifications", "calls_api", "uses_network", "uses_credentials",
    "connects_broker", "connects_exchange", "uses_real_money", "places_orders",
    "contains_order_logic", "auto_trading", "paper_trading", "live_trading",
    "deploys_capital", "promotes_gate", "unlocks_downstream_gate", "skips_any_gate",
    "advances_without_human_approval", "claims_profitability", "claims_edge",
    "drops_cost_model", "crosses_into_forbidden_gate",
)


def _decisive_verdict() -> dict[str, Any]:
    """Recompute the decisive RISK-ADJUSTED gates from the pinned metrics (pure)."""
    s = STRATEGY_METRICS
    bh_best_sharpe = max(BUY_AND_HOLD_METRICS[a]["sharpe"] for a in ASSETS)
    bh_best_calmar = max(BUY_AND_HOLD_METRICS[a]["calmar"] for a in ASSETS)
    bh_worst_mdd = min(BUY_AND_HOLD_METRICS[a]["max_drawdown"] for a in ASSETS)
    ew = EQUAL_WEIGHT_BASKET_METRICS
    no_worse_mdd_bh = s["max_drawdown"] >= bh_worst_mdd
    no_worse_mdd_ew = s["max_drawdown"] >= ew["max_drawdown"]
    beats_bh = ((s["sharpe"] > bh_best_sharpe or s["calmar"] > bh_best_calmar)
                and no_worse_mdd_bh)
    beats_ew = ((s["sharpe"] > ew["sharpe"] or s["calmar"] > ew["calmar"])
                and no_worse_mdd_ew)
    fwd_edge = (STRATEGY_FORWARD_OOS_METRICS["sharpe"]
                > EQUAL_WEIGHT_BASKET_FORWARD_OOS_METRICS["sharpe"])
    cost_tolerable = TOTAL_COST_DRAG < abs(s["net_return"])
    gates = {
        "beats_buy_and_hold_risk_adjusted": beats_bh,
        "beats_equal_weight_basket_risk_adjusted": beats_ew,
        "max_drawdown_no_worse_than_buy_and_hold": no_worse_mdd_bh,
        "max_drawdown_no_worse_than_equal_weight": no_worse_mdd_ew,
        "forward_oos_risk_adjusted_edge_holds": fwd_edge,
        "turnover_cost_drag_tolerable": cost_tolerable,
    }
    return {"gates": gates, "all_decisive_gates_pass": all(gates.values())}


def get_candidate_17_replay_review_label() -> str:
    return (
        "Candidate #17 risk_adjusted_portfolio_construction_vol_targeted_"
        "allocation_v1 fee-honest replay review (READ-ONLY, RESEARCH ONLY, PURE). "
        "Pins the FROZEN equity-curve replay over SHA-pinned local BTC/ETH/SOL 1d "
        "data (net of 37 bps) and the decisive RISK-ADJUSTED verdict: REJECTED -- "
        "the allocator cuts max drawdown to -37.8% (vs -77% to -96% buy-and-hold / "
        "-85% basket) and holds ~20% vol, but does NOT beat buy-and-hold or the "
        "equal-weight basket on Sharpe (0.80 vs 1.04-1.08) or Calmar (0.47 vs "
        "0.74-0.83), and the 2026 forward-OOS edge does not hold. Lower drawdown "
        "alone is not an edge. NOT a profitability claim.")


def get_candidate_17_replay_review_next_action() -> str:
    return "HUMAN_DECISION_C17_REJECT_AT_REPLAY_OR_REVIEW"


def build_c17_replay_review(repo_root: Any = ".",
                            tracked_paths: list | None = None) -> dict[str, Any]:
    """Assemble the frozen C17 fee-honest replay results review record. Pure; no
    I/O; pins SHAs + risk-adjusted metrics + the decisive verdict; chain-gated on
    the frozen C17 labels review."""
    labels = _l17.build_c17_labels_review(repo_root, tracked_paths)
    labels_valid = _l17.validate_c17_labels_review(labels)["valid"]
    dv = _decisive_verdict()

    blockers: list = []
    if not labels_valid:
        blockers.append("c17_labels_review_invalid")
    if labels.get("verdict") != "C17_LABELS_FROZEN_FOR_HUMAN_REVIEW":
        blockers.append("c17_labels_review_not_frozen")

    record: dict[str, Any] = {
        "schema_version": R17_SCHEMA_VERSION, "mode": R17_MODE, "lane": R17_LANE,
        "label": get_candidate_17_replay_review_label(),
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "candidate_name": CANDIDATE_NAME,
        "is_replay_review_only": True,
        "blockers": blockers,
        "verdict": (VERDICT_C17R_FROZEN if not blockers else "C17_REPLAY_BLOCKED"),
        # chain provenance
        "labels_review_verdict": labels.get("verdict"),
        "labels_review_valid": labels_valid,
        # pinned artifact provenance (frozen local data + frozen labels)
        "head_at_labels_review": HEAD_AT_LABELS_REVIEW,
        "ledger_path": LEDGER_PATH, "summary_path": SUMMARY_PATH,
        "expected_ledger_sha256": EXPECTED_LEDGER_SHA256,
        "expected_summary_sha256": EXPECTED_SUMMARY_SHA256,
        "expected_labels_sha256": EXPECTED_LABELS_SHA256,
        "expected_source_sha256": dict(EXPECTED_SOURCE_SHA256),
        "uses_frozen_local_data_only": True,
        # cost model APPLIED (the reserved 37 bps)
        "fee_round_trip_bps": FEE_ROUND_TRIP_BPS,
        "slippage_round_trip_bps": SLIPPAGE_ROUND_TRIP_BPS,
        "all_in_round_trip_bps": ALL_IN_ROUND_TRIP_BPS,
        "one_way_cost_bps": ONE_WAY_COST_BPS,
        "cost_model_applied_here": True,
        "no_parameter_optimization": True, "no_reparameterization": True,
        # pinned risk-adjusted metrics
        "assets": list(ASSETS), "timeframe": "D1",
        "replay_window": list(REPLAY_WINDOW), "n_days": N_DAYS,
        "strategy_metrics": dict(STRATEGY_METRICS),
        "strategy_forward_oos_metrics": dict(STRATEGY_FORWARD_OOS_METRICS),
        "buy_and_hold_metrics": {a: dict(BUY_AND_HOLD_METRICS[a]) for a in ASSETS},
        "equal_weight_basket_metrics": dict(EQUAL_WEIGHT_BASKET_METRICS),
        "equal_weight_basket_forward_oos_metrics":
            dict(EQUAL_WEIGHT_BASKET_FORWARD_OOS_METRICS),
        "total_cost_drag": TOTAL_COST_DRAG, "total_turnover": TOTAL_TURNOVER,
        # decisive verdict -- HONEST REJECTION
        "decisive_gate_results": dv["gates"],
        "all_decisive_gates_pass": dv["all_decisive_gates_pass"],
        "decisive_rejection_pressure": not dv["all_decisive_gates_pass"],
        "rejection_reasons": [
            "DOES NOT BEAT BUY-AND-HOLD RISK-ADJUSTED: strategy Sharpe 0.80 / Calmar "
            "0.47 vs best buy-and-hold (SOL) Sharpe 1.08 / Calmar 0.83",
            "DOES NOT BEAT THE EQUAL-WEIGHT BASKET RISK-ADJUSTED: strategy Sharpe "
            "0.80 / Calmar 0.47 vs basket Sharpe 1.04 / Calmar 0.74",
            "FORWARD-OOS 2026 EDGE DOES NOT HOLD: every sleeve is negative and the "
            "low-vol strategy's Sharpe is not better than the basket's",
            "in a 2020-2026 crypto bull, vol-targeting + risk-parity de-risked away "
            "from the biggest winner (SOL) and LOWERED risk-adjusted return; lower "
            "max drawdown ALONE (while also lower Sharpe AND Calmar) is not an edge "
            "over simply holding the basket",
        ],
        "only_win_is_lower_drawdown": True,
        "raw_return_alone_is_not_sufficient": True,
        "human_review_required": True,
        "current_loop_stage": "fee_honest_replay_review",
        "next_required_action": get_candidate_17_replay_review_next_action(),
        # downstream gates locked
        "promote_gate_locked": True, "robustness_gate_locked": True,
        "paper_trading_gate_locked": True, "live_gate_locked": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_data_fetch": True, "no_re_replay": True, "no_relabel": True,
        "no_re_allocate": True, "no_optimization": True, "no_reparameterization": True,
        "no_robustness": True, "no_real_data_mutation": True, "no_cost_drop": True,
        "no_stage": True, "no_commit": True, "no_push": True, "no_auto_commit": True,
        "no_auto_push": True, "no_scheduler_change": True, "no_broker": True,
        "no_credentials": True, "no_order_logic": True, "no_auto_trading": True,
        "no_paper_trading": True, "no_live_trading": True, "no_gate_skip": True,
        "no_downstream_gate_unlock": True, "no_profitability_claim": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_c17_replay_review(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the review is research-only, replay-
    review-only, chain-gated on the frozen C17 labels review, uses frozen local data
    only, pins the exact SHAs + metrics, APPLIES the 37 bps cost (cannot be dropped),
    records the decisive verdict consistently with the pinned metrics (the HONEST
    rejection cannot be flipped to a pass), makes no profitability claim, locks
    downstream gates, and pins every capability flag False."""
    failures: list = []
    if record.get("mode") != R17_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_replay_review_only") is not True:
        failures.append("not_replay_review_only")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("verdict") != VERDICT_C17R_FROZEN:
        failures.append("verdict_not_frozen")

    # chain gate
    if record.get("labels_review_valid") is not True:
        failures.append("labels_review_not_valid")
    if record.get("labels_review_verdict") != "C17_LABELS_FROZEN_FOR_HUMAN_REVIEW":
        failures.append("labels_review_not_frozen")

    # frozen local data + pinned SHAs
    if record.get("uses_frozen_local_data_only") is not True:
        failures.append("not_frozen_local_data_only")
    if record.get("expected_ledger_sha256") != EXPECTED_LEDGER_SHA256:
        failures.append("ledger_sha_tampered")
    if record.get("expected_summary_sha256") != EXPECTED_SUMMARY_SHA256:
        failures.append("summary_sha_tampered")
    if record.get("expected_source_sha256") != EXPECTED_SOURCE_SHA256:
        failures.append("source_sha_tampered")

    # cost model applied + not droppable
    if record.get("all_in_round_trip_bps") != 37.0:
        failures.append("cost_model_tampered")
    if record.get("cost_model_applied_here") is not True:
        failures.append("cost_not_applied")
    if record.get("no_parameter_optimization") is not True:
        failures.append("optimization_not_forbidden")

    # decisive verdict consistent with the pinned metrics (HONEST rejection)
    dv = _decisive_verdict()
    if record.get("decisive_gate_results") != dv["gates"]:
        failures.append("decisive_gates_tampered")
    if record.get("all_decisive_gates_pass") != dv["all_decisive_gates_pass"]:
        failures.append("all_pass_inconsistent")
    if dv["all_decisive_gates_pass"] is not False:
        failures.append("gates_should_not_all_pass")     # honest rejection is frozen
    if record.get("decisive_rejection_pressure") is not True:
        failures.append("rejection_pressure_must_be_true")
    if record.get("raw_return_alone_is_not_sufficient") is not True:
        failures.append("raw_return_sufficiency_flag_wrong")
    # the pinned strategy must genuinely NOT beat the baselines risk-adjusted
    s = record.get("strategy_metrics") or {}
    ew = record.get("equal_weight_basket_metrics") or {}
    if s.get("sharpe", 9) >= ew.get("sharpe", 0) and s.get("calmar", 9) >= ew.get(
            "calmar", 0):
        failures.append("strategy_metrics_inconsistent_with_rejection")

    if record.get("next_required_action") != (
            "HUMAN_DECISION_C17_REJECT_AT_REPLAY_OR_REVIEW"):
        failures.append("next_action_not_reject_or_review")

    # downstream gates locked
    for gate in ("promote_gate_locked", "robustness_gate_locked",
                 "paper_trading_gate_locked", "live_gate_locked"):
        if record.get(gate) is not True:
            failures.append("downstream_gate_unlocked_%s" % gate)

    locks = record.get("scope_locks") or {}
    for key in ("no_data_fetch", "no_re_replay", "no_relabel", "no_re_allocate",
                "no_optimization", "no_reparameterization", "no_cost_drop",
                "no_commit", "no_push", "no_broker", "no_order_logic",
                "no_auto_trading", "no_paper_trading", "no_live_trading",
                "no_gate_skip"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
