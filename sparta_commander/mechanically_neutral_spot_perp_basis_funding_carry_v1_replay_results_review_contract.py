"""Candidate #20 -- mechanically_neutral_spot_perp_basis_funding_carry_v1
-- FEE-HONEST REPLAY RESULTS REVIEW (PURE, RESEARCH ONLY).

Records and validates the frozen fee-honest REPLAY results for Candidate #20, produced by
`tools/c20_fee_honest_replay_once.py` from the 9 SHA-frozen PUBLIC BTC/ETH/SOL
spot+perp+funding files + the frozen C20 labels artifact (no fetch). It pins the source
+ labels + replay artifact SHAs, the net-of-cost portfolio + per-asset metrics, the
random/null market-neutral baseline (NOT buy-and-hold), the 2026 forward-OOS results, the
funding-vs-basis contribution split, the cost drag, the decisive-gate results, and a
verdict. Chain-gated on the committed C20 labels / detector / spec / proposal /
data-readiness chain.

HONEST DECISIVE FINDING (preserved, not softened): the C20 strategy AS SPECIFIED FAILS
the fee-honest replay. Applying the reserved 37 bps all-in cost PER LEG (74 bps
round-trip per trade, two legs) to the 704 frozen trades produces a portfolio net return
of -74.5% (Sharpe -12.8), and ALL FOUR decisive gates fail (net-positive-after-cost,
positive Sharpe, beats-random-null, forward-OOS-positive). The mechanically-neutral CARRY
ITSELF is real and positive -- the always-on neutral-carry NULL earns +21.2% (Sharpe
1.09), driven by BTC/ETH funding (null Sharpe ~8 each) -- which VINDICATES the C20 thesis
that a same-asset basis/funding carry has a genuine return source. BUT the C20 detector's
entry/exit TIMING over-trades: 704 round-trip trades x 74 bps = 521% cost drag, which
destroys the ~80% gross funding collected. This rejects the C20 DETECTOR/TIMING as
specified, NOT the carry thesis; pursuing a low-turnover always-on carry would be a
DIFFERENT, separately human-approved candidate. Recommended decision: REJECT. This is
FROZEN for the human's reject-or-promote decision.

NO replay re-run, NO PnL recompute, NO fee change, NO optimization / tuning / rescue /
parameter sweep, NO new data fetch, NO XAUUSD, NO paper/live/broker/order surface, NO
data artifact committed, and does NOT start C21.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.mechanically_neutral_spot_perp_basis_funding_carry_v1_real_candle_labels_review_contract as _l20  # noqa: E501

R20_SCHEMA_VERSION = 1
R20_MODE = "RESEARCH_ONLY"
R20_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = _l20.CANDIDATE_ID
CANDIDATE_FAMILY = _l20.CANDIDATE_FAMILY
CANDIDATE_NAME = _l20.CANDIDATE_NAME

VERDICT_C20R_FROZEN = "C20_REPLAY_FROZEN_FOR_HUMAN_REVIEW"
RECOMMENDED_DECISION = "REJECT"

# --- pinned artifact provenance (gitignored real-candle + replay outputs) ----
HEAD_AT_LABELS_REVIEW = "ead1bdb72ef5f9a78c1489f2a7701b5cd6e60c68"
LABELS_PATH = ("data/mechanically_neutral_spot_perp_basis_funding_carry_c20/"
               "labels/c20_labels.json")
LEDGER_PATH = ("data/mechanically_neutral_spot_perp_basis_funding_carry_c20/"
               "replay_results/c20_replay_ledger.json")
SUMMARY_PATH = ("data/mechanically_neutral_spot_perp_basis_funding_carry_c20/"
                "replay_results/c20_replay_summary.json")
EXPECTED_LABELS_SHA256 = (
    "e8282933ea1b07f14c7a09b72cc71632de2880d88e9105d3d0e91fe2702ca842")
EXPECTED_LEDGER_SHA256 = (
    "d0f5463a9c47b969a4461b7803f6b82e08c50dfd98f1c239df7dd7a7ee4b3daa")
EXPECTED_SUMMARY_SHA256 = (
    "cf6bedf9e5ed0a22ea4163fae51f54ad7ac4a16f16d3efdeb37232e949980b2c")
EXPECTED_SOURCE_SHA256 = dict(_l20.EXPECTED_SOURCE_SHA256)   # the 9 frozen sources

# --- cost model (reserved, now APPLIED at replay) ---------------------------
ALL_IN_ROUND_TRIP_BPS = 37.0
NUM_LEGS = 2
ROUND_TRIP_COST_PER_TRADE_BPS = NUM_LEGS * ALL_IN_ROUND_TRIP_BPS   # 74.0 (counts double)

# --- pinned frozen replay metrics (portfolio, equal-weight) -----------------
TRADE_COUNT = 704
WIN_RATE = 0.03267
AVG_TRADE_NET = -0.00626227
FORWARD_OOS_TRADE_COUNT = 35
FORWARD_OOS_WIN_RATE = 0.0
FUNDING_CONTRIBUTION_TOTAL = 0.797538
BASIS_CONVERGENCE_CONTRIBUTION_TOTAL = 0.003424
TOTAL_COST_DRAG = 5.2096

STRATEGY_METRICS = {
    "n_bars": 2093, "net_return": -0.7452, "cagr": -0.212145, "ann_vol": 0.018555,
    "sharpe": -12.836936, "max_drawdown": -0.745453, "calmar": -0.284585,
}
RANDOM_NULL_METRICS = {
    "n_bars": 2093, "net_return": 0.211648, "cagr": 0.034047, "ann_vol": 0.031248,
    "sharpe": 1.087808, "max_drawdown": -0.101089, "calmar": 0.336797,
}
STRATEGY_FORWARD_OOS_METRICS = {
    "n_bars": 159, "net_return": -0.082992, "cagr": -0.180359, "ann_vol": 0.016345,
    "sharpe": -12.156854, "max_drawdown": -0.082992, "calmar": -2.173206,
}
RANDOM_NULL_FORWARD_OOS_METRICS = {
    "n_bars": 159, "net_return": -0.0053, "cagr": -0.012124, "ann_vol": 0.006032,
    "sharpe": -2.019224, "max_drawdown": -0.007194, "calmar": -1.685285,
}

# --- per-asset pinned net/sharpe (strategy vs always-on null) ---------------
PER_ASSET = {
    "BTCUSDT": {"trade_count": 243, "strategy_net": -0.780058,
                "strategy_sharpe": -7.89265, "null_net": 0.454668,
                "null_sharpe": 8.07263, "funding_pnl_total": 0.289002,
                "basis_pnl_total": -0.001854, "total_cost_drag": 1.7982,
                "strategy_forward_oos_net": -0.075883},
    "ETHUSDT": {"trade_count": 255, "strategy_net": -0.789507,
                "strategy_sharpe": -7.921925, "null_net": 0.559681,
                "null_sharpe": 7.343632, "funding_pnl_total": 0.33612,
                "basis_pnl_total": -0.003909, "total_cost_drag": 1.887,
                "strategy_forward_oos_net": -0.085855},
    "SOLUSDT": {"trade_count": 206, "strategy_net": -0.739644,
                "strategy_sharpe": -7.974088, "null_net": -0.111108,
                "null_sharpe": -0.172597, "funding_pnl_total": 0.172416,
                "basis_pnl_total": 0.009187, "total_cost_drag": 1.5244,
                "strategy_forward_oos_net": -0.08743},
}

# --- decisive gates (market-neutral: vs random/null, NOT buy-and-hold) ------
DECISIVE_GATE_RESULTS = {
    "strategy_net_return_positive_after_cost": False,
    "strategy_sharpe_positive": False,
    "beats_random_null_risk_adjusted": False,
    "forward_oos_net_return_positive": False,
}
ALL_DECISIVE_GATES_PASS = False

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "re_replays", "recomputes_pnl", "changes_fee",
    "relabels", "re_detects", "runs_optimization", "tunes_parameters",
    "runs_rescue", "runs_parameter_sweep", "fetches_data", "reads_real_data",
    "mutates_data", "stages_data", "commits_data_artifact", "auto_commits",
    "auto_pushes", "modifies_scheduler", "sends_notifications", "calls_api",
    "uses_network", "uses_credentials", "connects_broker", "connects_exchange",
    "uses_real_money", "places_orders", "contains_order_logic",
    "carries_net_market_beta", "uses_estimated_cross_asset_hedge", "uses_xauusd",
    "adds_new_instrument_class", "drops_cost", "paper_trading", "live_trading",
    "deploys_capital", "promotes_gate", "unlocks_downstream_gate", "skips_any_gate",
    "starts_c21", "advances_without_human_approval", "claims_profitability",
    "claims_edge", "claims_paper_live_readiness", "pivots_to_new_family_here",
    "crosses_into_forbidden_gate",
)


def _structural_verdict() -> dict[str, Any]:
    """Pure assessment of the frozen replay. The strategy AS SPECIFIED fails all
    decisive gates after honest cost; the underlying carry is real (null positive) but
    the timing over-trades. Recommended: REJECT."""
    strategy_net_negative = STRATEGY_METRICS["net_return"] < 0
    fails_all_gates = not any(DECISIVE_GATE_RESULTS.values())
    null_carry_is_positive = RANDOM_NULL_METRICS["net_return"] > 0
    strategy_worse_than_null = (
        STRATEGY_METRICS["sharpe"] < RANDOM_NULL_METRICS["sharpe"])
    cost_drag_dominates = TOTAL_COST_DRAG > FUNDING_CONTRIBUTION_TOTAL
    forward_oos_fails = STRATEGY_FORWARD_OOS_METRICS["net_return"] <= 0
    return {
        "trade_count": TRADE_COUNT,
        "win_rate": WIN_RATE,
        "avg_trade_net": AVG_TRADE_NET,
        "strategy_net_return": STRATEGY_METRICS["net_return"],
        "strategy_sharpe": STRATEGY_METRICS["sharpe"],
        "random_null_net_return": RANDOM_NULL_METRICS["net_return"],
        "random_null_sharpe": RANDOM_NULL_METRICS["sharpe"],
        "funding_contribution_total": FUNDING_CONTRIBUTION_TOTAL,
        "basis_convergence_contribution_total":
            BASIS_CONVERGENCE_CONTRIBUTION_TOTAL,
        "total_cost_drag": TOTAL_COST_DRAG,
        "round_trip_cost_per_trade_bps": ROUND_TRIP_COST_PER_TRADE_BPS,
        "strategy_net_negative_after_cost": strategy_net_negative,
        "fails_all_decisive_gates": fails_all_gates,
        "carry_thesis_vindicated_by_positive_null": null_carry_is_positive,
        "strategy_worse_than_always_on_null": strategy_worse_than_null,
        "cost_drag_dominates_funding": cost_drag_dominates,
        "forward_oos_fails": forward_oos_fails,
        "rejects_timing_not_carry_thesis": True,
        "low_turnover_carry_would_be_separate_candidate": True,
        "recommended_decision": RECOMMENDED_DECISION,
    }


def get_candidate_20_replay_review_label() -> str:
    return (
        "Candidate #20 mechanically_neutral_spot_perp_basis_funding_carry_v1 "
        "fee-honest replay results review (READ-ONLY, RESEARCH ONLY). The strategy AS "
        "SPECIFIED FAILS at fee-honest replay: 74 bps round-trip per trade (two legs x "
        "37 bps) on 704 trades -> portfolio net -74.5% (Sharpe -12.8), ALL FOUR "
        "decisive gates fail (net-after-cost, Sharpe, beats-random-null, forward-OOS). "
        "The mechanically-neutral CARRY is real -- the always-on null earns +21.2% "
        "(Sharpe 1.09, BTC/ETH funding) -- so the C20 THESIS holds, but the detector's "
        "entry/exit TIMING over-trades and the cost destroys it (521% cost drag vs "
        "~80% gross funding). vs a random/null market-neutral baseline, NOT "
        "buy-and-hold. Recommended: REJECT (the timing, not the carry thesis). No "
        "optimization/tuning. Frozen for the human reject-or-promote decision. NOT a "
        "profitability claim.")


def get_candidate_20_replay_review_next_action() -> str:
    return "HUMAN_DECISION_C20_REJECT_OR_PROMOTE"


def build_c20_replay_review(repo_root: Any = ".",
                            tracked_paths: list | None = None) -> dict[str, Any]:
    """Assemble the frozen C20 fee-honest replay results review record. Pure; no I/O;
    chain-gated on the frozen C20 labels review (and thus detector / spec / proposal)."""
    labels = _l20.build_c20_labels_review(repo_root, tracked_paths)
    labels_valid = _l20.validate_c20_labels_review(labels)["valid"]
    labels_verdict = labels.get("verdict")

    blockers: list = []
    if not labels_valid:
        blockers.append("c20_labels_review_invalid")
    if labels_verdict != "C20_LABELS_FROZEN_FOR_HUMAN_REVIEW":
        blockers.append("c20_labels_review_not_frozen")

    sv = _structural_verdict()

    record: dict[str, Any] = {
        "schema_version": R20_SCHEMA_VERSION, "mode": R20_MODE, "lane": R20_LANE,
        "label": get_candidate_20_replay_review_label(),
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "candidate_name": CANDIDATE_NAME,
        "is_replay_review_only": True,
        "blockers": blockers,
        "verdict": (VERDICT_C20R_FROZEN if not blockers else "C20_REPLAY_BLOCKED"),
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
        "random_null_metrics": dict(RANDOM_NULL_METRICS),
        "strategy_forward_oos_metrics": dict(STRATEGY_FORWARD_OOS_METRICS),
        "random_null_forward_oos_metrics": dict(RANDOM_NULL_FORWARD_OOS_METRICS),
        "per_asset": {s: dict(a) for s, a in PER_ASSET.items()},
        "decisive_gate_results": dict(DECISIVE_GATE_RESULTS),
        "all_decisive_gates_pass": ALL_DECISIVE_GATES_PASS,
        # the structural verdict (honest: fails; carry real, timing churns)
        "structural_verdict": sv,
        "strategy_net_negative_after_cost": sv["strategy_net_negative_after_cost"],
        "fails_all_decisive_gates": sv["fails_all_decisive_gates"],
        "carry_thesis_vindicated_by_positive_null":
            sv["carry_thesis_vindicated_by_positive_null"],
        # NOT a profitability/edge claim
        "profitability_established": False, "edge_established": False,
        "no_parameter_optimization": True, "no_parameter_tuning": True,
        "no_rescue": True, "no_parameter_sweep": True,
        "does_not_start_c21": True, "c21_candidate_id": None,
        "does_not_pivot_to_new_family_here": True,
        "human_review_required": True,
        "current_loop_stage": "fee_honest_replay_review",
        "next_required_action": get_candidate_20_replay_review_next_action(),
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
        "no_parameter_sweep": True, "no_data_fetch": True,
        "no_real_data_access_beyond_frozen": True, "no_data_commit": True,
        "no_xauusd": True, "no_new_instrument_class": True,
        "no_estimated_cross_asset_hedge": True, "no_net_market_beta": True,
        "no_pivot_to_new_family": True, "no_stage": True, "no_commit": True,
        "no_push": True, "no_auto_commit": True, "no_auto_push": True,
        "no_scheduler_change": True, "no_broker": True, "no_credentials": True,
        "no_order_logic": True, "no_paper_trading": True, "no_live_trading": True,
        "no_gate_skip": True, "no_start_c21": True, "no_downstream_gate_unlock": True,
        "no_profitability_claim": True, "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_c20_replay_review(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the unit is research-only,
    replay-review-only, chain-gated on the frozen C20 labels review, uses ONLY the
    frozen public data + frozen labels (no fetch; SHA-pinned sources + artifacts not
    committed), applies the 74 bps two-leg cost (not dropped), compares vs the
    random/null market-neutral baseline (NOT buy-and-hold), pins the HONEST frozen
    metrics + the all-fail decisive gates (it cannot be flipped to claim profitability
    while the strategy net return is negative and all gates fail), recommends REJECT,
    does no optimization/tuning, does not start C21 or pivot to a new family, keeps
    downstream gates locked, and pins every capability flag False."""
    failures: list = []
    if record.get("mode") != R20_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_replay_review_only") is not True:
        failures.append("not_replay_review_only")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("verdict") != VERDICT_C20R_FROZEN:
        failures.append("verdict_not_frozen")
    if record.get("recommended_decision") != RECOMMENDED_DECISION:
        failures.append("recommended_decision_not_reject")

    # chain gate on the frozen labels review
    if record.get("labels_review_valid") is not True:
        failures.append("labels_review_not_valid")
    if record.get("labels_review_verdict") != "C20_LABELS_FROZEN_FOR_HUMAN_REVIEW":
        failures.append("labels_review_not_frozen")
    if record.get("candidate_id") != "C20":
        failures.append("candidate_id_not_c20")

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

    # cost honestly applied (74 bps, not dropped); baseline is random/null
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

    # the strategy genuinely FAILS -- cannot be flipped to a pass / profitability claim
    if record.get("strategy_metrics", {}).get("net_return", 0) >= 0:
        failures.append("strategy_net_should_be_negative")
    if record.get("all_decisive_gates_pass") is not False:
        failures.append("gates_falsely_passed")
    if any((record.get("decisive_gate_results") or {}).values()):
        failures.append("a_decisive_gate_falsely_true")
    if record.get("strategy_net_negative_after_cost") is not True:
        failures.append("net_negative_finding_wrong")
    if record.get("fails_all_decisive_gates") is not True:
        failures.append("fails_all_gates_finding_wrong")
    if record.get("profitability_established") is not False:
        failures.append("must_not_claim_profitability")
    if record.get("edge_established") is not False:
        failures.append("must_not_claim_edge")
    sv = record.get("structural_verdict") or {}
    if sv.get("recommended_decision") != "REJECT":
        failures.append("sv_must_recommend_reject")
    if sv.get("carry_thesis_vindicated_by_positive_null") is not True:
        failures.append("sv_should_note_null_positive")   # honesty: carry is real
    if sv.get("rejects_timing_not_carry_thesis") is not True:
        failures.append("sv_should_scope_rejection_to_timing")

    # no optimization/tuning, no C21, no pivot, downstream locks
    for k in ("no_parameter_optimization", "no_parameter_tuning", "no_rescue",
              "no_parameter_sweep", "does_not_start_c21",
              "does_not_pivot_to_new_family_here"):
        if record.get(k) is not True:
            failures.append("flag_off_%s" % k)
    if record.get("c21_candidate_id") is not None:
        failures.append("c21_must_be_none")
    if record.get("next_required_action") != "HUMAN_DECISION_C20_REJECT_OR_PROMOTE":
        failures.append("next_action_not_reject_or_promote")
    for gate in ("paper_trading_gate_locked", "live_gate_locked"):
        if record.get(gate) is not True:
            failures.append("downstream_gate_unlocked_%s" % gate)

    locks = record.get("scope_locks") or {}
    for key in ("no_re_replay", "no_recompute_pnl", "no_change_fee", "no_drop_cost",
                "no_optimization", "no_tuning", "no_rescue", "no_parameter_sweep",
                "no_data_fetch", "no_data_commit", "no_xauusd", "no_pivot_to_new_family",
                "no_commit", "no_push", "no_paper_trading", "no_live_trading",
                "no_start_c21", "no_gate_skip"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
