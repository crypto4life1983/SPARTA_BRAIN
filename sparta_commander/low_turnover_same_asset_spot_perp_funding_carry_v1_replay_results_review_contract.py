"""Candidate #21 -- low_turnover_same_asset_spot_perp_funding_carry_v1
-- FEE-HONEST REPLAY RESULTS REVIEW (PURE, RESEARCH ONLY).

Records and validates the frozen fee-honest REPLAY results for Candidate #21, produced by
`tools/c21_fee_honest_replay_once.py` from the 9 SHA-frozen PUBLIC BTC/ETH/SOL
spot+perp+funding files + the frozen C21 LOW-TURNOVER labels artifact (no fetch). It pins
the source + labels + replay artifact SHAs, the net AND gross portfolio + per-asset
metrics, the ALWAYS-ON neutral-carry null baseline + a flat-zero baseline (NOT
buy-and-hold), the 2026 forward-OOS results, the funding-vs-basis split, the cost drag,
the decisive-gate results, the SPARTA Pipeline Audit v1 cross-checks, and a verdict.
Chain-gated on the committed C21 labels / detector / spec / proposal / data-readiness
chain.

HONEST DECISIVE FINDING (preserved, not softened): the C21 LOW-TURNOVER design SUCCEEDS at
its stated goal -- unlike the rejected C20 (704 trades, 521% cost drag, net -74.5%), the
frozen C21 labels take only 20 trades over ~6 years (cost drag 14.8%), so the 74 bps
two-leg cost no longer dominates and the strategy stays NET-POSITIVE: portfolio net +20.2%
(Sharpe 1.05, max DD -8.5%), gross +25.7% (Sharpe 1.31). BUT the strategy DOES NOT BEAT
the trivial ALWAYS-ON neutral-carry null, which earns +21.2% (Sharpe 1.09) by simply
holding the same mechanically-neutral carry continuously -- so the detector's
regime-gating/timing adds NO edge (it marginally underperforms always-on), and the 2026
forward-OOS is negative for both (strategy -1.0%, null -0.5%). Two of four decisive gates
pass (net-positive-after-cost, positive Sharpe) but the two DECISIVE market-neutral gates
FAIL (beats-random-null-risk-adjusted, forward-OOS-positive). The SPARTA Pipeline Audit v1
cross-checks all pass (cost == 20 x 74 bps exactly; no duplicate trades; funding on the
correct side at the held bar; same-asset spot/perp/funding aligned; turnover <= 6/yr per
asset), so this is an EDGE-driven rejection -- NOT a fee/funding/lookahead/duplicate/
alignment artifact. The carry SOURCE is real (the null is positive), but C21 AS SPECIFIED
shows no timing edge over simply holding it. Recommended decision: REJECT. This is FROZEN
for the human's reject-or-promote decision.

NO replay re-run, NO PnL recompute, NO fee change, NO optimization / tuning / rescue /
parameter sweep, NO relabel, NO new data fetch, NO XAUUSD, NO rescue/retune of C20, NO
paper/live/broker/order surface, NO data artifact committed, and does NOT start C22.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.low_turnover_same_asset_spot_perp_funding_carry_v1_real_candle_labels_review_contract as _l21  # noqa: E501

R21_SCHEMA_VERSION = 1
R21_MODE = "RESEARCH_ONLY"
R21_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = _l21.CANDIDATE_ID
CANDIDATE_FAMILY = _l21.CANDIDATE_FAMILY
CANDIDATE_NAME = _l21.CANDIDATE_NAME

VERDICT_C21R_FROZEN = "C21_REPLAY_FROZEN_FOR_HUMAN_REVIEW"
RECOMMENDED_DECISION = "REJECT"

# --- pinned artifact provenance (gitignored real-candle + replay outputs) ----
HEAD_AT_LABELS_REVIEW = "668d06f20d6824cd62f07bc8b06f15f10576f46d"
LABELS_PATH = ("data/low_turnover_same_asset_spot_perp_funding_carry_c21/"
               "labels/c21_labels.json")
LEDGER_PATH = ("data/low_turnover_same_asset_spot_perp_funding_carry_c21/"
               "replay_results/c21_replay_ledger.json")
SUMMARY_PATH = ("data/low_turnover_same_asset_spot_perp_funding_carry_c21/"
                "replay_results/c21_replay_summary.json")
EXPECTED_LABELS_SHA256 = (
    "98e8665b239a6d7d32a30a34bc88b699a137fff23371567cc444369ccaa6cbad")
EXPECTED_LEDGER_SHA256 = (
    "4ed818ad9001e67abc8f3ce1c87e783ce7972c6331c6f67094b4004543691edb")
EXPECTED_SUMMARY_SHA256 = (
    "e47b702c68d8ca5025b3e82b3c4df849fe6ebc26a9b79546da28515d6b296287")
EXPECTED_SOURCE_SHA256 = dict(_l21.EXPECTED_SOURCE_SHA256)   # the 9 frozen sources

# --- cost model (reserved, now APPLIED at replay) ---------------------------
ALL_IN_ROUND_TRIP_BPS = 37.0
NUM_LEGS = 2
ROUND_TRIP_COST_PER_TRADE_BPS = NUM_LEGS * ALL_IN_ROUND_TRIP_BPS   # 74.0 (counts double)

# --- pinned frozen replay metrics (portfolio, equal-weight) -----------------
TRADE_COUNT = 20
WIN_RATE = 0.5
AVG_TRADE_NET = 0.03402823
FORWARD_OOS_TRADE_COUNT = 3
FORWARD_OOS_WIN_RATE = 0.0
FUNDING_CONTRIBUTION_TOTAL = 0.914196
BASIS_CONVERGENCE_CONTRIBUTION_TOTAL = -0.085631
TOTAL_COST_DRAG = 0.148

STRATEGY_METRICS = {
    "n_bars": 2093, "net_return": 0.202382, "cagr": 0.032663, "ann_vol": 0.031023,
    "sharpe": 1.052315, "max_drawdown": -0.084976, "calmar": 0.384379,
}
STRATEGY_GROSS_METRICS = {
    "n_bars": 2093, "net_return": 0.257014, "cagr": 0.040696, "ann_vol": 0.030806,
    "sharpe": 1.311072, "max_drawdown": -0.083843, "calmar": 0.485386,
}
RANDOM_NULL_METRICS = {
    "n_bars": 2093, "net_return": 0.211648, "cagr": 0.034047, "ann_vol": 0.031248,
    "sharpe": 1.087808, "max_drawdown": -0.101089, "calmar": 0.336797,
}
FLAT_ZERO_METRICS = {
    "n_bars": 2093, "net_return": 0.0, "cagr": 0.0, "ann_vol": 0.0,
    "sharpe": 0.0, "max_drawdown": 0.0, "calmar": 0.0,
}
STRATEGY_FORWARD_OOS_METRICS = {
    "n_bars": 159, "net_return": -0.010245, "cagr": -0.023362, "ann_vol": 0.007544,
    "sharpe": -3.12989, "max_drawdown": -0.01213, "calmar": -1.926001,
}
RANDOM_NULL_FORWARD_OOS_METRICS = {
    "n_bars": 159, "net_return": -0.0053, "cagr": -0.012124, "ann_vol": 0.006032,
    "sharpe": -2.019224, "max_drawdown": -0.007194, "calmar": -1.685285,
}

# --- per-asset pinned net/sharpe (strategy vs always-on null) ---------------
PER_ASSET = {
    "BTCUSDT": {"trade_count": 6, "round_trips_per_year": 0.943966,
                "strategy_net": 0.379927, "strategy_sharpe": 5.811251,
                "null_net": 0.454668, "null_sharpe": 8.07263,
                "strategy_forward_oos_net": -0.008762,
                "funding_pnl_total": 0.368988, "basis_pnl_total": -0.002296,
                "total_cost_drag": 0.0444},
    "ETHUSDT": {"trade_count": 5, "round_trips_per_year": 0.786638,
                "strategy_net": 0.508719, "strategy_sharpe": 6.288621,
                "null_net": 0.559681, "null_sharpe": 7.343632,
                "strategy_forward_oos_net": -0.009028,
                "funding_pnl_total": 0.455867, "basis_pnl_total": -0.007237,
                "total_cost_drag": 0.037},
    "SOLUSDT": {"trade_count": 9, "round_trips_per_year": 1.59157,
                "strategy_net": -0.077247, "strategy_sharpe": -0.103242,
                "null_net": -0.111108, "null_sharpe": -0.172597,
                "strategy_forward_oos_net": -0.012971,
                "funding_pnl_total": 0.089341, "basis_pnl_total": -0.076098,
                "total_cost_drag": 0.0666},
}

# --- decisive gates (market-neutral: vs always-on null, NOT buy-and-hold) ----
DECISIVE_GATE_RESULTS = {
    "strategy_net_return_positive_after_cost": True,
    "strategy_sharpe_positive": True,
    "beats_random_null_risk_adjusted": False,
    "forward_oos_net_return_positive": False,
}
ALL_DECISIVE_GATES_PASS = False
STRATEGY_BEATS_ALWAYS_ON_NULL_AFTER_COSTS = False

# --- SPARTA Pipeline Audit v1 cross-checks (frozen; all clean) --------------
AUDIT_CROSSCHECKS = {
    "fee_cost_matches_trade_count_x_74bps": True,
    "expected_cost_drag": 0.148,
    "funding_side_short_perp_receives_positive": True,
    "funding_applied_same_bar_no_lookahead": True,
    "no_duplicate_trades": True,
    "duplicate_trade_keys": [],
    "same_asset_spot_perp_funding_aligned": True,
    "turnover_ceiling_respected_all_assets": True,
    "max_round_trips_per_year_per_asset": 6,
    "not_a_pipeline_artifact": True,
}

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "re_replays", "recomputes_pnl", "changes_fee",
    "relabels", "re_detects", "runs_optimization", "tunes_parameters",
    "runs_rescue", "runs_parameter_sweep", "fetches_data", "reads_real_data",
    "mutates_data", "stages_data", "commits_data_artifact", "auto_commits",
    "auto_pushes", "modifies_scheduler", "sends_notifications", "calls_api",
    "uses_network", "uses_credentials", "connects_broker", "connects_exchange",
    "uses_real_money", "places_orders", "contains_order_logic",
    "carries_net_market_beta", "uses_estimated_cross_asset_hedge", "uses_xauusd",
    "adds_new_instrument_class", "drops_cost", "rescues_c20",
    "retunes_rejected_candidate", "paper_trading", "live_trading", "deploys_capital",
    "promotes_gate", "unlocks_downstream_gate", "skips_any_gate", "starts_c22",
    "advances_without_human_approval", "claims_profitability", "claims_edge",
    "claims_paper_live_readiness", "pivots_to_new_family_here",
    "crosses_into_forbidden_gate",
)


def _structural_verdict() -> dict[str, Any]:
    """Pure assessment of the frozen replay. The low-turnover design PRESERVES the carry
    (net-positive after cost, unlike C20) but the strategy does NOT beat the always-on
    null and the forward-OOS edge does not hold -> no timing edge -> REJECT. The audit
    cross-checks confirm this is not a pipeline artifact."""
    net_positive = STRATEGY_METRICS["net_return"] > 0
    sharpe_positive = STRATEGY_METRICS["sharpe"] > 0
    beats_null = (STRATEGY_METRICS["sharpe"] > RANDOM_NULL_METRICS["sharpe"]
                  and STRATEGY_METRICS["net_return"] > RANDOM_NULL_METRICS["net_return"])
    forward_oos_holds = STRATEGY_FORWARD_OOS_METRICS["net_return"] > 0
    null_carry_is_positive = RANDOM_NULL_METRICS["net_return"] > 0
    low_turnover_preserved_carry = (
        net_positive and TOTAL_COST_DRAG < FUNDING_CONTRIBUTION_TOTAL)
    cost_no_longer_dominates = TOTAL_COST_DRAG < FUNDING_CONTRIBUTION_TOTAL
    audit_clean = AUDIT_CROSSCHECKS["not_a_pipeline_artifact"] is True
    return {
        "trade_count": TRADE_COUNT,
        "win_rate": WIN_RATE,
        "avg_trade_net": AVG_TRADE_NET,
        "strategy_net_return": STRATEGY_METRICS["net_return"],
        "strategy_gross_return": STRATEGY_GROSS_METRICS["net_return"],
        "strategy_sharpe": STRATEGY_METRICS["sharpe"],
        "random_null_net_return": RANDOM_NULL_METRICS["net_return"],
        "random_null_sharpe": RANDOM_NULL_METRICS["sharpe"],
        "funding_contribution_total": FUNDING_CONTRIBUTION_TOTAL,
        "basis_convergence_contribution_total":
            BASIS_CONVERGENCE_CONTRIBUTION_TOTAL,
        "total_cost_drag": TOTAL_COST_DRAG,
        "round_trip_cost_per_trade_bps": ROUND_TRIP_COST_PER_TRADE_BPS,
        # the low-turnover design worked (the C20 lesson held):
        "strategy_net_positive_after_cost": net_positive,
        "strategy_sharpe_positive": sharpe_positive,
        "low_turnover_preserved_carry": low_turnover_preserved_carry,
        "cost_no_longer_dominates": cost_no_longer_dominates,
        "improves_on_c20_churn": True,   # +20.2% vs C20 -74.5% on the same carry
        # but there is no edge over the trivial always-on null, and OOS fails:
        "beats_always_on_null_after_costs": beats_null,
        "forward_oos_holds": forward_oos_holds,
        "carry_source_is_real": null_carry_is_positive,
        "timing_adds_no_edge_over_null": not beats_null,
        # honest provenance of the rejection:
        "audit_crosschecks_all_clean": audit_clean,
        "not_a_fee_funding_lookahead_duplicate_alignment_artifact": audit_clean,
        "rejects_lack_of_edge_vs_null_not_the_carry_source": True,
        "recommended_decision": RECOMMENDED_DECISION,
    }


def get_candidate_21_replay_review_label() -> str:
    return (
        "Candidate #21 low_turnover_same_asset_spot_perp_funding_carry_v1 fee-honest "
        "replay results review (READ-ONLY, RESEARCH ONLY). The LOW-TURNOVER design "
        "SUCCEEDS where C20 failed: only 20 trades (cost drag 14.8% vs C20's 521%), so "
        "the 74 bps two-leg cost no longer dominates and the strategy stays NET-POSITIVE "
        "(+20.2%, Sharpe 1.05; gross +25.7%, Sharpe 1.31). BUT it does NOT beat the "
        "trivial always-on neutral-carry null (+21.2%, Sharpe 1.09) -- the regime-timing "
        "adds no edge -- and the 2026 forward-OOS is negative (strategy -1.0%, null "
        "-0.5%). 2 of 4 decisive gates pass (net-positive, Sharpe-positive); the two "
        "decisive market-neutral gates FAIL (beats-null, forward-OOS). SPARTA Pipeline "
        "Audit v1 cross-checks all pass (cost==20x74bps, no duplicates, funding correct "
        "side/time, same-asset aligned, turnover<=6/yr), so this is an EDGE-driven "
        "rejection, NOT a fee/funding/lookahead/duplicate/alignment artifact. vs the "
        "always-on null + flat-zero, NOT buy-and-hold. Recommended: REJECT (no timing "
        "edge over the carry; the carry source itself is real). No optimization/tuning. "
        "Frozen for the human reject-or-promote decision. NOT a profitability claim.")


def get_candidate_21_replay_review_next_action() -> str:
    return "HUMAN_DECISION_C21_REJECT_OR_PROMOTE"


def build_c21_replay_review(repo_root: Any = ".",
                            tracked_paths: list | None = None) -> dict[str, Any]:
    """Assemble the frozen C21 fee-honest replay results review record. Pure; no I/O;
    chain-gated on the frozen C21 labels review (and thus detector / spec / proposal)."""
    labels = _l21.build_c21_labels_review(repo_root, tracked_paths)
    labels_valid = _l21.validate_c21_labels_review(labels)["valid"]
    labels_verdict = labels.get("verdict")

    blockers: list = []
    if not labels_valid:
        blockers.append("c21_labels_review_invalid")
    if labels_verdict != "C21_LABELS_FROZEN_FOR_HUMAN_REVIEW":
        blockers.append("c21_labels_review_not_frozen")

    sv = _structural_verdict()

    record: dict[str, Any] = {
        "schema_version": R21_SCHEMA_VERSION, "mode": R21_MODE, "lane": R21_LANE,
        "label": get_candidate_21_replay_review_label(),
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "candidate_name": CANDIDATE_NAME,
        "is_replay_review_only": True,
        "blockers": blockers,
        "verdict": (VERDICT_C21R_FROZEN if not blockers else "C21_REPLAY_BLOCKED"),
        "recommended_decision": RECOMMENDED_DECISION,
        # chain provenance
        "labels_review_verdict": labels_verdict,
        "labels_review_valid": labels_valid,
        "head_at_labels_review": HEAD_AT_LABELS_REVIEW,
        # frozen source + labels + replay artifacts (no fetch; SHA-pinned)
        "uses_frozen_public_data_only": True, "no_new_data_fetch": True,
        "uses_xauusd": False,
        "expected_source_sha256": dict(EXPECTED_SOURCE_SHA256),
        "labels_path": LABELS_PATH, "ledger_path": LEDGER_PATH,
        "summary_path": SUMMARY_PATH,
        "expected_labels_sha256": EXPECTED_LABELS_SHA256,
        "expected_ledger_sha256": EXPECTED_LEDGER_SHA256,
        "expected_summary_sha256": EXPECTED_SUMMARY_SHA256,
        "artifacts_gitignored_not_committed": True,
        # cost model (reserved -> now applied honestly)
        "all_in_round_trip_bps": ALL_IN_ROUND_TRIP_BPS,
        "round_trip_cost_per_trade_bps": ROUND_TRIP_COST_PER_TRADE_BPS,
        "cost_applied_not_dropped": True,
        "baseline_is_random_null_not_buy_and_hold": True,
        "includes_flat_zero_baseline": True,
        # the frozen replay metrics
        "trade_count": TRADE_COUNT, "win_rate": WIN_RATE,
        "avg_trade_net": AVG_TRADE_NET,
        "forward_oos_trade_count": FORWARD_OOS_TRADE_COUNT,
        "forward_oos_win_rate": FORWARD_OOS_WIN_RATE,
        "funding_contribution_total": FUNDING_CONTRIBUTION_TOTAL,
        "basis_convergence_contribution_total":
            BASIS_CONVERGENCE_CONTRIBUTION_TOTAL,
        "total_cost_drag": TOTAL_COST_DRAG,
        "strategy_metrics": dict(STRATEGY_METRICS),
        "strategy_gross_metrics": dict(STRATEGY_GROSS_METRICS),
        "random_null_metrics": dict(RANDOM_NULL_METRICS),
        "flat_zero_metrics": dict(FLAT_ZERO_METRICS),
        "strategy_forward_oos_metrics": dict(STRATEGY_FORWARD_OOS_METRICS),
        "random_null_forward_oos_metrics": dict(RANDOM_NULL_FORWARD_OOS_METRICS),
        "per_asset": {s: dict(a) for s, a in PER_ASSET.items()},
        "decisive_gate_results": dict(DECISIVE_GATE_RESULTS),
        "all_decisive_gates_pass": ALL_DECISIVE_GATES_PASS,
        "strategy_beats_always_on_null_after_costs":
            STRATEGY_BEATS_ALWAYS_ON_NULL_AFTER_COSTS,
        # SPARTA Pipeline Audit v1 guardrail (not a pipeline artifact)
        "audit_crosschecks": dict(AUDIT_CROSSCHECKS),
        "not_a_pipeline_artifact": True,
        # the structural verdict (honest: carry preserved, but no edge vs null)
        "structural_verdict": sv,
        "strategy_net_positive_after_cost": sv["strategy_net_positive_after_cost"],
        "low_turnover_preserved_carry": sv["low_turnover_preserved_carry"],
        "beats_always_on_null_after_costs": sv["beats_always_on_null_after_costs"],
        "forward_oos_holds": sv["forward_oos_holds"],
        "carry_source_is_real": sv["carry_source_is_real"],
        # NOT a profitability/edge claim (no edge over the null; OOS fails)
        "profitability_established": False, "edge_established": False,
        "no_parameter_optimization": True, "no_parameter_tuning": True,
        "no_rescue": True, "no_parameter_sweep": True, "no_relabel": True,
        "is_rescue_or_retune_of_c20": False, "c20_remains_rejected": True,
        "does_not_start_c22": True, "c22_candidate_id": None,
        "does_not_pivot_to_new_family_here": True,
        "human_review_required": True,
        "current_loop_stage": "fee_honest_replay_review",
        "next_required_action": get_candidate_21_replay_review_next_action(),
        # downstream gates locked
        "paper_trading_gate_locked": True, "live_gate_locked": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_build": True, "no_write": True, "no_execute": True,
        "no_re_replay": True, "no_recompute_pnl": True, "no_change_fee": True,
        "no_drop_cost": True, "no_relabel": True, "no_redetect": True,
        "no_optimization": True, "no_tuning": True, "no_rescue": True,
        "no_rescue_c20": True, "no_parameter_sweep": True, "no_data_fetch": True,
        "no_real_data_access_beyond_frozen": True, "no_data_commit": True,
        "no_xauusd": True, "no_new_instrument_class": True,
        "no_estimated_cross_asset_hedge": True, "no_net_market_beta": True,
        "no_pivot_to_new_family": True, "no_stage": True, "no_commit": True,
        "no_push": True, "no_auto_commit": True, "no_auto_push": True,
        "no_scheduler_change": True, "no_broker": True, "no_credentials": True,
        "no_order_logic": True, "no_paper_trading": True, "no_live_trading": True,
        "no_gate_skip": True, "no_start_c22": True, "no_downstream_gate_unlock": True,
        "no_profitability_claim": True, "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_c21_replay_review(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the unit is research-only,
    replay-review-only, chain-gated on the frozen C21 labels review, uses ONLY the frozen
    public data + frozen labels (no fetch; SHA-pinned sources + artifacts not committed),
    applies the 74 bps two-leg cost (not dropped), compares vs the always-on null
    market-neutral baseline (NOT buy-and-hold), pins the HONEST frozen metrics (the carry
    is preserved net-positive but does NOT beat the null and the forward-OOS fails, so
    NOT all decisive gates pass), confirms via the audit cross-checks that the result is
    not a pipeline artifact, recommends REJECT, makes no profitability/edge claim, does no
    optimization/tuning, does not rescue C20, does not start C22 or pivot, keeps
    downstream gates locked, and pins every capability flag False."""
    failures: list = []
    if record.get("mode") != R21_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_replay_review_only") is not True:
        failures.append("not_replay_review_only")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("verdict") != VERDICT_C21R_FROZEN:
        failures.append("verdict_not_frozen")
    if record.get("recommended_decision") != RECOMMENDED_DECISION:
        failures.append("recommended_decision_not_reject")

    # chain gate on the frozen labels review
    if record.get("labels_review_valid") is not True:
        failures.append("labels_review_not_valid")
    if record.get("labels_review_verdict") != "C21_LABELS_FROZEN_FOR_HUMAN_REVIEW":
        failures.append("labels_review_not_frozen")
    if record.get("candidate_id") != "C21":
        failures.append("candidate_id_not_c21")

    # frozen provenance, no fetch, SHA-pinned (9 sources + labels + replay)
    if record.get("no_new_data_fetch") is not True:
        failures.append("must_not_fetch")
    if record.get("uses_xauusd") is not False:
        failures.append("must_not_use_xauusd")
    if record.get("expected_source_sha256") != EXPECTED_SOURCE_SHA256:
        failures.append("source_sha_tampered")
    if len(record.get("expected_source_sha256") or {}) != 9:
        failures.append("source_sha_count_not_9")
    if record.get("expected_labels_sha256") != EXPECTED_LABELS_SHA256:
        failures.append("labels_sha_tampered")
    if record.get("expected_ledger_sha256") != EXPECTED_LEDGER_SHA256:
        failures.append("ledger_sha_tampered")
    if record.get("expected_summary_sha256") != EXPECTED_SUMMARY_SHA256:
        failures.append("summary_sha_tampered")
    if record.get("artifacts_gitignored_not_committed") is not True:
        failures.append("artifacts_must_not_be_committed")
    if not str(record.get("ledger_path", "")).startswith("data/"):
        failures.append("ledger_path_not_under_data")

    # cost honestly applied (74 bps, not dropped); baseline is always-on null
    if record.get("all_in_round_trip_bps") != 37.0:
        failures.append("cost_model_tampered")
    if record.get("round_trip_cost_per_trade_bps") != 74.0:
        failures.append("two_leg_cost_not_doubled")
    if record.get("cost_applied_not_dropped") is not True:
        failures.append("cost_must_be_applied")
    if record.get("baseline_is_random_null_not_buy_and_hold") is not True:
        failures.append("baseline_must_be_random_null")

    # frozen metrics pinned exactly (anti-tamper)
    if record.get("trade_count") != TRADE_COUNT:
        failures.append("trade_count_tampered")
    if record.get("strategy_metrics") != STRATEGY_METRICS:
        failures.append("strategy_metrics_tampered")
    if record.get("strategy_gross_metrics") != STRATEGY_GROSS_METRICS:
        failures.append("strategy_gross_metrics_tampered")
    if record.get("random_null_metrics") != RANDOM_NULL_METRICS:
        failures.append("null_metrics_tampered")
    if record.get("strategy_forward_oos_metrics") != STRATEGY_FORWARD_OOS_METRICS:
        failures.append("strategy_oos_metrics_tampered")
    if record.get("total_cost_drag") != TOTAL_COST_DRAG:
        failures.append("cost_drag_tampered")
    pa = record.get("per_asset") or {}
    if set(pa) != {"BTCUSDT", "ETHUSDT", "SOLUSDT"}:
        failures.append("per_asset_universe_tampered")
    if sum(pa.get(s, {}).get("trade_count", 0) for s in pa) != TRADE_COUNT:
        failures.append("per_asset_trades_do_not_sum")

    # the HONEST decisive-gate pattern: net-positive + Sharpe-positive PASS (the carry
    # is preserved), but beats-null + forward-OOS FAIL -> NOT all gates pass. The record
    # cannot be flipped to claim it beats the null or that all gates pass.
    if record.get("all_decisive_gates_pass") is not False:
        failures.append("gates_falsely_all_passed")
    g = record.get("decisive_gate_results") or {}
    if g.get("strategy_net_return_positive_after_cost") is not True:
        failures.append("net_positive_gate_should_be_true")
    if g.get("strategy_sharpe_positive") is not True:
        failures.append("sharpe_positive_gate_should_be_true")
    if g.get("beats_random_null_risk_adjusted") is not False:
        failures.append("beats_null_gate_should_be_false")
    if g.get("forward_oos_net_return_positive") is not False:
        failures.append("forward_oos_gate_should_be_false")
    if record.get("strategy_beats_always_on_null_after_costs") is not False:
        failures.append("must_not_claim_beats_null")
    # numeric guards: strategy net must actually be below the null net + Sharpe
    if record.get("strategy_metrics", {}).get("net_return", 0) \
            >= record.get("random_null_metrics", {}).get("net_return", 0):
        failures.append("strategy_net_should_be_below_null")
    if record.get("strategy_metrics", {}).get("sharpe", 0) \
            >= record.get("random_null_metrics", {}).get("sharpe", 0):
        failures.append("strategy_sharpe_should_be_below_null")
    if record.get("strategy_forward_oos_metrics", {}).get("net_return", 0) > 0:
        failures.append("forward_oos_should_be_negative")

    # no profitability/edge claim
    if record.get("profitability_established") is not False:
        failures.append("must_not_claim_profitability")
    if record.get("edge_established") is not False:
        failures.append("must_not_claim_edge")

    # audit guardrail: must confirm the result is not a pipeline artifact
    ac = record.get("audit_crosschecks") or {}
    for key in ("fee_cost_matches_trade_count_x_74bps",
                "funding_side_short_perp_receives_positive",
                "funding_applied_same_bar_no_lookahead", "no_duplicate_trades",
                "same_asset_spot_perp_funding_aligned",
                "turnover_ceiling_respected_all_assets", "not_a_pipeline_artifact"):
        if ac.get(key) is not True:
            failures.append("audit_crosscheck_false_%s" % key)
    if record.get("not_a_pipeline_artifact") is not True:
        failures.append("must_confirm_not_artifact")

    # structural verdict honesty
    sv = record.get("structural_verdict") or {}
    if sv.get("recommended_decision") != "REJECT":
        failures.append("sv_must_recommend_reject")
    if sv.get("carry_source_is_real") is not True:
        failures.append("sv_should_note_carry_real")     # honesty: the carry is real
    if sv.get("low_turnover_preserved_carry") is not True:
        failures.append("sv_should_note_low_turnover_worked")
    if sv.get("beats_always_on_null_after_costs") is not False:
        failures.append("sv_must_not_claim_beats_null")
    if sv.get("timing_adds_no_edge_over_null") is not True:
        failures.append("sv_should_scope_rejection_to_no_edge")
    if sv.get("not_a_fee_funding_lookahead_duplicate_alignment_artifact") is not True:
        failures.append("sv_should_confirm_not_artifact")

    # no optimization/tuning/rescue, no C22, no pivot, downstream locks
    for k in ("no_parameter_optimization", "no_parameter_tuning", "no_rescue",
              "no_parameter_sweep", "no_relabel", "does_not_start_c22",
              "does_not_pivot_to_new_family_here", "c20_remains_rejected"):
        if record.get(k) is not True:
            failures.append("flag_off_%s" % k)
    if record.get("is_rescue_or_retune_of_c20") is not False:
        failures.append("must_not_be_c20_rescue")
    if record.get("c22_candidate_id") is not None:
        failures.append("c22_must_be_none")
    if record.get("next_required_action") != "HUMAN_DECISION_C21_REJECT_OR_PROMOTE":
        failures.append("next_action_not_reject_or_promote")
    for gate in ("paper_trading_gate_locked", "live_gate_locked"):
        if record.get(gate) is not True:
            failures.append("downstream_gate_unlocked_%s" % gate)

    locks = record.get("scope_locks") or {}
    for key in ("no_re_replay", "no_recompute_pnl", "no_change_fee", "no_drop_cost",
                "no_optimization", "no_tuning", "no_rescue", "no_rescue_c20",
                "no_parameter_sweep", "no_data_fetch", "no_data_commit", "no_xauusd",
                "no_pivot_to_new_family", "no_commit", "no_push", "no_paper_trading",
                "no_live_trading", "no_start_c22", "no_gate_skip"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
