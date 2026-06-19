"""Candidate #18 -- h4_trend_following_market_structure_v1 -- FEE-HONEST REPLAY
RESULTS REVIEW (PURE, RESEARCH ONLY).

Pins the FROZEN fee-honest replay artifact produced by
tools/c18_h4_fee_honest_replay_once.py (the FROZEN C18 H4 setups replayed into a
daily-bar EQUITY CURVE over the SHA-pinned local BTCUSDT 4h data, net of the reserved
37 bps cost, vs matched BTC buy-and-hold) and records the replay-stage decisive
verdict.

It is chain-gated on the frozen C18 real-candle labels review. It does NOTHING with
real data here: NO re-replay, NO relabel, NO re-detection, NO optimization, NO
re-parameterization, NO parameter sweep, NO XAUUSD, NO writes, NO stage/commit/push,
NO paper/live/broker/order surface. It only PINS the SHAs + the risk-adjusted metrics
and re-states the decisive verdict. Every capability flag is pinned False with a full
scope_locks set. The next gate (reject / human review) needs an explicit human
decision.

HONEST OUTCOME (FROZEN): the decisive RISK-ADJUSTED gates are FAILED -- a replay-stage
REJECTION. Over 2019-01-01..2026-06-08, net of 37 bps, the strategy runs at ~22% vol
and cuts max drawdown to -38.2% (vs -77.0% for BTC buy-and-hold), but it does NOT beat
BTC buy-and-hold on a RISK-ADJUSTED basis -- strategy Sharpe 0.52 / Calmar 0.25 vs
buy-and-hold Sharpe 0.93 / Calmar 0.60 -- the win rate is low (15.2%) with a negative
total R (-101.4, structural-stop bleed), the cost drag is heavy (0.78), and the 2026
forward-OOS edge does not hold (strategy Sharpe -2.27 vs buy-and-hold -1.47). Lower
drawdown alone is not an edge over simply holding BTC. NOT a profitability claim.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.h4_trend_following_market_structure_v1_real_candle_labels_review_contract as _l18  # noqa: E501

R18_SCHEMA_VERSION = 1
R18_MODE = "RESEARCH_ONLY"
R18_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = _l18.CANDIDATE_ID
CANDIDATE_FAMILY = _l18.CANDIDATE_FAMILY
CANDIDATE_NAME = _l18.CANDIDATE_NAME

VERDICT_C18R_FROZEN = "C18_REPLAY_FROZEN_FOR_HUMAN_REVIEW"

# --- pinned artifact provenance ---------------------------------------------
HEAD_AT_LABELS_REVIEW = "0e1377284ea865ac33a7988c61b5da7dc2417230"
LEDGER_PATH = ("data/h4_trend_following_market_structure_c18/replay_results/"
               "c18_h4_replay_ledger.json")
SUMMARY_PATH = ("data/h4_trend_following_market_structure_c18/replay_results/"
                "c18_h4_replay_summary.json")
EXPECTED_LEDGER_SHA256 = (
    "d8bf47406db01acf35507f9a6ff3c55d692cf11a464e969bbdf5c54ec20b8456")
EXPECTED_SUMMARY_SHA256 = (
    "402c93a2b2e631c8a573e6efa54c3365e7909234a1ce526f128f13e0b17d442e")
EXPECTED_SOURCE_SHA256 = _l18.EXPECTED_SOURCE_SHA256
EXPECTED_LABELS_SHA256 = _l18.EXPECTED_LABELS_SHA256

# --- cost model (the reserved 37 bps, now APPLIED) --------------------------
FEE_ROUND_TRIP_BPS = 27.0
SLIPPAGE_ROUND_TRIP_BPS = 10.0
ALL_IN_ROUND_TRIP_BPS = 37.0
ONE_WAY_COST_BPS = 18.5

# --- pinned frozen metrics (from the real-candle replay) ---------------------
WINDOW = ("2019-01-01T00:00:00Z", "2026-06-08T00:00:00Z")
TRADE_COUNT = 389
WIN_RATE = 0.151671
TOTAL_R = -101.4122
AVG_R = -0.2607
TOTAL_COST_DRAG = 0.779467

STRATEGY_METRICS = {
    "n_bars": 16285, "net_return": 0.954079, "cagr": 0.094273,
    "ann_vol": 0.222184, "sharpe": 0.5158, "max_drawdown": -0.382027,
    "calmar": 0.246771}
STRATEGY_FORWARD_OOS_METRICS = {
    "n_bars": 949, "net_return": -0.107407, "cagr": -0.230651,
    "ann_vol": 0.112588, "sharpe": -2.272515, "max_drawdown": -0.154718,
    "calmar": -1.490781}
BUY_AND_HOLD_METRICS = {
    "n_bars": 16285, "net_return": 16.062486, "cagr": 0.464484,
    "ann_vol": 0.606741, "sharpe": 0.933316, "max_drawdown": -0.770434,
    "calmar": 0.602886}
BUY_AND_HOLD_FORWARD_OOS_METRICS = {
    "n_bars": 949, "net_return": -0.279733, "cagr": -0.531037,
    "ann_vol": 0.447679, "sharpe": -1.467162, "max_drawdown": -0.380057,
    "calmar": -1.397255}

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "re_replays", "relabels", "re_detects",
    "runs_optimization", "reparameterizes", "runs_parameter_sweep", "fetches_data",
    "reads_real_data", "uses_xauusd", "mutates_data", "stages_data", "auto_commits",
    "auto_pushes", "modifies_scheduler", "sends_notifications", "calls_api",
    "uses_network", "uses_credentials", "connects_broker", "connects_exchange",
    "uses_real_money", "places_orders", "contains_order_logic", "paper_trading",
    "live_trading", "deploys_capital", "promotes_gate", "unlocks_downstream_gate",
    "skips_any_gate", "advances_without_human_approval", "claims_profitability",
    "claims_edge", "drops_cost_model", "crosses_into_forbidden_gate",
)


def _decisive_verdict() -> dict[str, Any]:
    s, bh = STRATEGY_METRICS, BUY_AND_HOLD_METRICS
    no_worse_mdd = s["max_drawdown"] >= bh["max_drawdown"]
    beats_bh = ((s["sharpe"] > bh["sharpe"] or s["calmar"] > bh["calmar"])
                and no_worse_mdd)
    fwd_edge = (STRATEGY_FORWARD_OOS_METRICS["sharpe"]
                > BUY_AND_HOLD_FORWARD_OOS_METRICS["sharpe"])
    cost_tolerable = TOTAL_COST_DRAG < abs(s["net_return"])
    gates = {
        "beats_buy_and_hold_risk_adjusted": beats_bh,
        "max_drawdown_no_worse_than_buy_and_hold": no_worse_mdd,
        "forward_oos_risk_adjusted_edge_holds": fwd_edge,
        "turnover_cost_drag_tolerable": cost_tolerable,
    }
    return {"gates": gates, "all_decisive_gates_pass": all(gates.values())}


def get_candidate_18_replay_review_label() -> str:
    return (
        "Candidate #18 h4_trend_following_market_structure_v1 fee-honest replay "
        "review (READ-ONLY, RESEARCH ONLY, PURE). Pins the FROZEN equity-curve replay "
        "over SHA-pinned local BTCUSDT 4h data (net of 37 bps) and the decisive "
        "RISK-ADJUSTED verdict: REJECTED -- cuts max drawdown to -38.2% (vs -77.0% "
        "BTC buy-and-hold) but does NOT beat buy-and-hold on Sharpe (0.52 vs 0.93) or "
        "Calmar (0.25 vs 0.60); low 15.2% win rate, negative total R, heavy cost "
        "drag, and the 2026 forward-OOS edge does not hold. Lower drawdown alone is "
        "not an edge. NOT a profitability claim.")


def get_candidate_18_replay_review_next_action() -> str:
    return "HUMAN_DECISION_C18_REJECT_AT_REPLAY_OR_REVIEW"


def build_c18_replay_review(repo_root: Any = ".",
                            tracked_paths: list | None = None) -> dict[str, Any]:
    """Assemble the frozen C18 fee-honest replay results review record. Pure; no I/O;
    pins SHAs + risk-adjusted metrics + the decisive verdict; chain-gated on the
    frozen C18 labels review."""
    labels = _l18.build_c18_labels_review(repo_root, tracked_paths)
    labels_valid = _l18.validate_c18_labels_review(labels)["valid"]
    dv = _decisive_verdict()

    blockers: list = []
    if not labels_valid:
        blockers.append("c18_labels_review_invalid")
    if labels.get("verdict") != "C18_LABELS_FROZEN_FOR_HUMAN_REVIEW":
        blockers.append("c18_labels_review_not_frozen")

    record: dict[str, Any] = {
        "schema_version": R18_SCHEMA_VERSION, "mode": R18_MODE, "lane": R18_LANE,
        "label": get_candidate_18_replay_review_label(),
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "candidate_name": CANDIDATE_NAME,
        "is_replay_review_only": True,
        "blockers": blockers,
        "verdict": (VERDICT_C18R_FROZEN if not blockers else "C18_REPLAY_BLOCKED"),
        # chain provenance
        "labels_review_verdict": labels.get("verdict"),
        "labels_review_valid": labels_valid,
        # pinned artifact provenance (frozen local data + frozen labels)
        "head_at_labels_review": HEAD_AT_LABELS_REVIEW,
        "ledger_path": LEDGER_PATH, "summary_path": SUMMARY_PATH,
        "expected_ledger_sha256": EXPECTED_LEDGER_SHA256,
        "expected_summary_sha256": EXPECTED_SUMMARY_SHA256,
        "expected_source_sha256": EXPECTED_SOURCE_SHA256,
        "expected_labels_sha256": EXPECTED_LABELS_SHA256,
        "uses_frozen_local_data_only": True,
        # cost model APPLIED (the reserved 37 bps)
        "fee_round_trip_bps": FEE_ROUND_TRIP_BPS,
        "slippage_round_trip_bps": SLIPPAGE_ROUND_TRIP_BPS,
        "all_in_round_trip_bps": ALL_IN_ROUND_TRIP_BPS,
        "one_way_cost_bps": ONE_WAY_COST_BPS,
        "cost_model_applied_here": True,
        "no_parameter_optimization": True, "no_reparameterization": True,
        "no_parameter_sweep": True,
        # pinned risk-adjusted metrics
        "symbol": "BTCUSD", "timeframe": "4h",
        "window": list(WINDOW), "trade_count": TRADE_COUNT,
        "win_rate": WIN_RATE, "total_R": TOTAL_R, "avg_R": AVG_R,
        "total_cost_drag": TOTAL_COST_DRAG,
        "strategy_metrics": dict(STRATEGY_METRICS),
        "strategy_forward_oos_metrics": dict(STRATEGY_FORWARD_OOS_METRICS),
        "buy_and_hold_metrics": dict(BUY_AND_HOLD_METRICS),
        "buy_and_hold_forward_oos_metrics": dict(BUY_AND_HOLD_FORWARD_OOS_METRICS),
        # decisive verdict -- HONEST REJECTION
        "decisive_gate_results": dv["gates"],
        "all_decisive_gates_pass": dv["all_decisive_gates_pass"],
        "decisive_rejection_pressure": not dv["all_decisive_gates_pass"],
        "rejection_reasons": [
            "DOES NOT BEAT BTC BUY-AND-HOLD RISK-ADJUSTED: strategy Sharpe 0.52 / "
            "Calmar 0.25 vs buy-and-hold Sharpe 0.93 / Calmar 0.60",
            "LOW WIN RATE (15.2%) with NEGATIVE total R (-101.4): structural stops "
            "bleed R faster than the pyramided winners recover it",
            "FORWARD-OOS 2026 EDGE DOES NOT HOLD: strategy Sharpe -2.27 vs "
            "buy-and-hold -1.47",
            "lower max drawdown ALONE (vs -77% buy-and-hold) is not an edge; raw "
            "return alone is not sufficient",
        ],
        "only_win_is_lower_drawdown": True,
        "raw_return_alone_is_not_sufficient": True,
        "human_review_required": True,
        "current_loop_stage": "fee_honest_replay_review",
        "next_required_action": get_candidate_18_replay_review_next_action(),
        # downstream gates locked
        "promote_gate_locked": True, "robustness_gate_locked": True,
        "paper_trading_gate_locked": True, "live_gate_locked": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_data_fetch": True, "no_re_replay": True, "no_relabel": True,
        "no_re_detect": True, "no_optimization": True, "no_reparameterization": True,
        "no_parameter_sweep": True, "no_robustness": True, "no_xauusd": True,
        "no_real_data_mutation": True, "no_cost_drop": True, "no_stage": True,
        "no_commit": True, "no_push": True, "no_auto_commit": True,
        "no_auto_push": True, "no_scheduler_change": True, "no_broker": True,
        "no_credentials": True, "no_order_logic": True, "no_paper_trading": True,
        "no_live_trading": True, "no_gate_skip": True,
        "no_downstream_gate_unlock": True, "no_profitability_claim": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_c18_replay_review(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the review is research-only, replay-
    review-only, chain-gated on the frozen C18 labels review, uses frozen local data
    only, pins the exact SHAs + metrics, APPLIES the 37 bps cost (cannot be dropped),
    records the decisive verdict consistently with the pinned metrics (the HONEST
    rejection cannot be flipped to a pass), makes no profitability claim, keeps
    XAUUSD out, locks downstream gates, and pins every capability flag False."""
    failures: list = []
    if record.get("mode") != R18_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_replay_review_only") is not True:
        failures.append("not_replay_review_only")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("verdict") != VERDICT_C18R_FROZEN:
        failures.append("verdict_not_frozen")

    # chain gate
    if record.get("labels_review_valid") is not True:
        failures.append("labels_review_not_valid")
    if record.get("labels_review_verdict") != "C18_LABELS_FROZEN_FOR_HUMAN_REVIEW":
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
    if record.get("expected_labels_sha256") != EXPECTED_LABELS_SHA256:
        failures.append("labels_sha_tampered")

    # cost model applied + not droppable + no optimization
    if record.get("all_in_round_trip_bps") != 37.0:
        failures.append("cost_model_tampered")
    if record.get("cost_model_applied_here") is not True:
        failures.append("cost_not_applied")
    if record.get("no_parameter_optimization") is not True:
        failures.append("optimization_not_forbidden")
    if record.get("no_reparameterization") is not True:
        failures.append("reparameterization_not_forbidden")
    if record.get("no_parameter_sweep") is not True:
        failures.append("parameter_sweep_not_forbidden")

    # decisive verdict consistent with the pinned metrics (HONEST rejection)
    dv = _decisive_verdict()
    if record.get("decisive_gate_results") != dv["gates"]:
        failures.append("decisive_gates_tampered")
    if record.get("all_decisive_gates_pass") != dv["all_decisive_gates_pass"]:
        failures.append("all_pass_inconsistent")
    if dv["all_decisive_gates_pass"] is not False:
        failures.append("gates_should_not_all_pass")
    if record.get("decisive_rejection_pressure") is not True:
        failures.append("rejection_pressure_must_be_true")
    if record.get("raw_return_alone_is_not_sufficient") is not True:
        failures.append("raw_return_sufficiency_flag_wrong")
    # the pinned strategy must genuinely NOT beat buy-and-hold risk-adjusted
    s = record.get("strategy_metrics") or {}
    bh = record.get("buy_and_hold_metrics") or {}
    if s.get("sharpe", 9) >= bh.get("sharpe", 0) and s.get("calmar", 9) >= bh.get(
            "calmar", 0):
        failures.append("strategy_metrics_inconsistent_with_rejection")
    if record.get("next_required_action") != (
            "HUMAN_DECISION_C18_REJECT_AT_REPLAY_OR_REVIEW"):
        failures.append("next_action_not_reject_or_review")

    # downstream gates locked
    for gate in ("promote_gate_locked", "robustness_gate_locked",
                 "paper_trading_gate_locked", "live_gate_locked"):
        if record.get(gate) is not True:
            failures.append("downstream_gate_unlocked_%s" % gate)

    locks = record.get("scope_locks") or {}
    for key in ("no_data_fetch", "no_re_replay", "no_relabel", "no_re_detect",
                "no_optimization", "no_reparameterization", "no_parameter_sweep",
                "no_xauusd", "no_cost_drop", "no_commit", "no_push", "no_broker",
                "no_order_logic", "no_paper_trading", "no_live_trading",
                "no_gate_skip"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
