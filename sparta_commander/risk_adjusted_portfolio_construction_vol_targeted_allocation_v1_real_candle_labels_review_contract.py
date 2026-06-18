"""Candidate #17 -- risk_adjusted_portfolio_construction_vol_targeted_allocation_v1
-- REAL-CANDLE LABELS REVIEW (PURE, RESEARCH ONLY).

Pins the FROZEN real-candle allocation-labels artifact produced by
tools/c17_real_candle_allocation_once.py (the FROZEN C17 vol-targeted / risk-parity
allocator run over the SHA-pinned local BTC/ETH/SOL 1d data) and records the
labels-stage STRUCTURAL verdict. A C17 "label" is one WEEKLY REBALANCE ALLOCATION
OBSERVATION -- a long/flat weight vector, not an entry/exit signal.

It is chain-gated on the frozen C17 detector synthetic dry-run. It does NOTHING
with real data here: NO re-detect, NO relabel, NO replay, NO backtest, NO PnL, NO
cost, NO baseline, NO optimization, NO robustness, NO writes, NO stage/commit/push,
NO paper/live/broker/order surface. It only PINS the SHAs + aggregate counts and
re-states the structural verdict. Every capability flag is pinned False with a full
scope_locks set. The next gate (fee-honest replay) needs an explicit human decision.

HONEST OUTCOME (FROZEN): the labels-stage STRUCTURAL gate is PASSED -- a well-formed,
sufficiently sampled allocation on real candles: 296 weekly rebalances (>= 100),
every weight long-only (no shorting), gross exposure never above the 1.0 cap (no
leverage; max 0.936, min 0.123), the vol-target ACTIVE on every rebalance (real
crypto vol always exceeds the 20% target, so the allocator always de-risks below the
cap -- it never needs leverage), all three regimes populated (bull 153 / bear 105 /
chop 38), a populated forward-OOS 2026 window (23 rebalances), average weekly
turnover 0.0298 within the 0.20 cap, and near-equal risk contributions (avg ratio
1.28). This is the FIRST candidate to clear the labels structural gate. It is NOT a
profitability claim -- whether it BEATS buy-and-hold / an equal-weight basket on a
RISK-ADJUSTED, fee-honest basis is decided only at the reserved replay gate.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.risk_adjusted_portfolio_construction_vol_targeted_allocation_v1_detector_spec_dry_run_contract as _d17  # noqa: E501

L17_SCHEMA_VERSION = 1
L17_MODE = "RESEARCH_ONLY"
L17_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = _d17.CANDIDATE_ID
CANDIDATE_FAMILY = _d17.CANDIDATE_FAMILY
CANDIDATE_NAME = _d17.CANDIDATE_NAME
ASSETS = tuple(_d17.ASSETS)                  # BTCUSD / ETHUSD / SOLUSD

VERDICT_C17L_FROZEN = "C17_LABELS_FROZEN_FOR_HUMAN_REVIEW"

# --- pinned artifact provenance ---------------------------------------------
HEAD_AT_DETECTOR_DRY_RUN = "ff4168aa63bb377cc84b480948678843c32c7e0d"
LABELS_PATH = ("data/risk_adjusted_portfolio_construction_vol_targeted_allocation_"
               "c17/allocation_labels/c17_allocation_labels.json")
SUMMARY_PATH = ("data/risk_adjusted_portfolio_construction_vol_targeted_allocation_"
                "c17/allocation_labels/c17_allocation_summary.json")
EXPECTED_LABELS_SHA256 = (
    "32ffb538c09d0158027071df19ec4749e894bd568225f7503a4fa7d2f349a7c7")
EXPECTED_SUMMARY_SHA256 = (
    "6013a406e5f2762fe2018f8847a5fc565d297ad73da96005a94b23049f733530")
EXPECTED_SOURCE_SHA256 = {
    "BTCUSD": "043fb722b35e738a0c2050f9388defc7ca99322ed2f153989746ee28bbb89b88",
    "ETHUSD": "1bfd0ca86137747f0fe4c3fb127b00dcbd4885bf76056dbc9c091a9d4681c1a3",
    "SOLUSD": "4716d4d124bd7d5327fdc4230f7b2eaea70085df88c182dd129232ce802c0113",
}

# --- pinned frozen aggregates (from the real-candle run) ---------------------
COMMON_WINDOW = ("2020-08-11", "2026-06-08")
N_COMMON_CANDLES = 2128
N_REBALANCES = 296
N_EXECUTED = 58
N_SKIPPED_BY_BAND = 238
MAX_GROSS_EXPOSURE = 0.936137
MIN_GROSS_EXPOSURE = 0.123462
N_GROSS_SCALED_DOWN = 296
N_GROSS_CAPPED_AT_ONE = 0
PER_REGIME = {"bull": 153, "bear": 105, "chop": 38}
FORWARD_OOS_REBALANCE_COUNT = 23
AVG_WEEKLY_TURNOVER = 0.02977
AVG_RISK_CONTRIBUTION_RATIO = 1.28268

MIN_REBALANCES = 100
MAX_AVG_WEEKLY_TURNOVER_CAP = _d17.MAX_AVG_WEEKLY_TURNOVER   # 0.20
MAX_GROSS_CAP = _d17.MAX_GROSS                               # 1.0

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "re_detects", "relabels", "runs_labels",
    "runs_replay", "runs_backtest", "computes_pnl", "applies_cost_model",
    "runs_baseline", "runs_optimization", "runs_robustness",
    "runs_portfolio_compute", "fetches_data", "reads_real_data", "mutates_data",
    "stages_data", "auto_commits", "auto_pushes", "modifies_scheduler",
    "sends_notifications", "calls_api", "uses_network", "uses_credentials",
    "connects_broker", "connects_exchange", "uses_real_money", "places_orders",
    "contains_order_logic", "shorts", "uses_leverage_above_cap", "paper_trading",
    "live_trading", "deploys_capital", "auto_trading", "promotes_gate",
    "unlocks_downstream_gate", "skips_any_gate", "advances_without_human_approval",
    "claims_profitability", "claims_edge", "crosses_into_forbidden_gate",
)


def _structural_verdict() -> dict[str, Any]:
    rebalances_ok = N_REBALANCES >= MIN_REBALANCES
    long_only = True
    gross_ok = MAX_GROSS_EXPOSURE <= MAX_GROSS_CAP + 1e-9
    vol_target_active = N_GROSS_SCALED_DOWN > 0
    fwd_ok = FORWARD_OOS_REBALANCE_COUNT > 0
    turnover_ok = AVG_WEEKLY_TURNOVER <= MAX_AVG_WEEKLY_TURNOVER_CAP
    passed = (rebalances_ok and long_only and gross_ok and vol_target_active
              and fwd_ok)
    return {
        "n_rebalances": N_REBALANCES, "min_rebalances": MIN_REBALANCES,
        "rebalances_ok": rebalances_ok,
        "all_weights_long_only": long_only,
        "gross_never_exceeds_cap": gross_ok,
        "max_gross_exposure": MAX_GROSS_EXPOSURE,
        "min_gross_exposure": MIN_GROSS_EXPOSURE,
        "vol_target_active": vol_target_active,
        "n_gross_scaled_down": N_GROSS_SCALED_DOWN,
        "n_gross_capped_at_one": N_GROSS_CAPPED_AT_ONE,
        "per_regime": dict(sorted(PER_REGIME.items())),
        "forward_oos_rebalance_count": FORWARD_OOS_REBALANCE_COUNT,
        "forward_oos_populated": fwd_ok,
        "avg_weekly_turnover": AVG_WEEKLY_TURNOVER,
        "max_avg_weekly_turnover_cap": MAX_AVG_WEEKLY_TURNOVER_CAP,
        "turnover_within_cap": turnover_ok,
        "avg_risk_contribution_ratio": AVG_RISK_CONTRIBUTION_RATIO,
        "passed": passed,
    }


def get_candidate_17_labels_review_label() -> str:
    return (
        "Candidate #17 risk_adjusted_portfolio_construction_vol_targeted_"
        "allocation_v1 real-candle labels review (READ-ONLY, RESEARCH ONLY, PURE). "
        "Pins the FROZEN weekly-allocation-label artifact over SHA-pinned local "
        "BTC/ETH/SOL 1d data and the labels-stage STRUCTURAL verdict: PASSED -- 296 "
        "weekly rebalances (>= 100), all weights long-only, gross never above the "
        "1.0 cap (max 0.936, vol-target always de-risks on real crypto), all "
        "regimes populated, forward-OOS 2026 populated (23), avg weekly turnover "
        "0.0298 within the 0.20 cap, near-equal risk contributions (1.28). NO "
        "replay, NO PnL, NO cost. NOT a profitability claim -- risk-adjusted edge vs "
        "buy-and-hold / equal-weight is decided only at the replay gate.")


def get_candidate_17_labels_review_next_action() -> str:
    return "HUMAN_DECISION_C17_ADVANCE_TO_FEE_HONEST_REPLAY_OR_REJECT"


def build_c17_labels_review(repo_root: Any = ".",
                            tracked_paths: list | None = None) -> dict[str, Any]:
    """Assemble the frozen C17 real-candle labels review record. Pure; no I/O; pins
    SHAs + counts + the structural verdict; chain-gated on the frozen C17 detector
    dry-run."""
    dry = _d17.build_c17_detector_dry_run(repo_root, tracked_paths)
    dry_valid = _d17.validate_c17_detector_dry_run(dry)["valid"]
    sv = _structural_verdict()

    blockers: list = []
    if not dry_valid:
        blockers.append("c17_detector_dry_run_invalid")
    if dry.get("verdict") != "C17_DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW":
        blockers.append("c17_detector_dry_run_not_frozen")

    record: dict[str, Any] = {
        "schema_version": L17_SCHEMA_VERSION, "mode": L17_MODE, "lane": L17_LANE,
        "label": get_candidate_17_labels_review_label(),
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "candidate_name": CANDIDATE_NAME,
        "is_labels_review_only": True,
        "blockers": blockers,
        "verdict": (VERDICT_C17L_FROZEN if not blockers else "C17_LABELS_BLOCKED"),
        # chain provenance
        "detector_dry_run_verdict": dry.get("verdict"),
        "detector_dry_run_valid": dry_valid,
        # pinned artifact provenance (FROZEN local data only)
        "head_at_detector_dry_run": HEAD_AT_DETECTOR_DRY_RUN,
        "labels_path": LABELS_PATH, "summary_path": SUMMARY_PATH,
        "expected_labels_sha256": EXPECTED_LABELS_SHA256,
        "expected_summary_sha256": EXPECTED_SUMMARY_SHA256,
        "expected_source_sha256": dict(EXPECTED_SOURCE_SHA256),
        "uses_frozen_local_data_only": True,
        # pinned frozen aggregates
        "assets": list(ASSETS), "timeframe": "D1",
        "common_window": list(COMMON_WINDOW),
        "n_common_candles": N_COMMON_CANDLES,
        "label_definition": "weekly_rebalance_long_flat_allocation_observation",
        "n_rebalances": N_REBALANCES, "n_executed": N_EXECUTED,
        "n_skipped_by_band": N_SKIPPED_BY_BAND,
        "per_regime": dict(sorted(PER_REGIME.items())),
        "forward_oos_rebalance_count": FORWARD_OOS_REBALANCE_COUNT,
        "max_gross_exposure": MAX_GROSS_EXPOSURE,
        "avg_weekly_turnover": AVG_WEEKLY_TURNOVER,
        "avg_risk_contribution_ratio": AVG_RISK_CONTRIBUTION_RATIO,
        # structural verdict -- HONEST PASS
        "structural_review": sv,
        "structural_passed": sv["passed"],
        "structural_rejection_pressure": not sv["passed"],
        "turnover_within_cap": sv["turnover_within_cap"],
        "pass_reasons": [
            "WELL-FORMED, SUFFICIENTLY SAMPLED: 296 weekly rebalances (>= 100) over "
            "2020-08-11..2026-06-08, all three regimes populated (bull 153 / bear "
            "105 / chop 38), forward-OOS 2026 populated (23)",
            "LONG-ONLY, NO LEVERAGE: every weight >= 0 and gross exposure never "
            "above the 1.0 cap (max 0.936); on real crypto the vol-target always "
            "de-risks (min gross 0.123), so the cap never binds and leverage is "
            "never needed",
            "LOW TURNOVER: avg weekly turnover 0.0298 within the 0.20 cap (the "
            "no-trade band skipped 238 of 296 weeks); near-equal risk contributions "
            "(avg ratio 1.28) -- risk parity holds on real data",
        ],
        "not_yet_validated": (
            "this is a STRUCTURAL pass only; whether the allocator BEATS buy-and-hold "
            "and an equal-weight basket on a RISK-ADJUSTED, fee-honest basis (Sharpe "
            "/ Calmar / max-drawdown, net of 37 bps) is decided ONLY at the reserved "
            "replay gate -- NOT here"),
        # cost model still reserved (no PnL here)
        "cost_model_reserved_for_replay": True,
        "cost_model_applied_here": False,
        "human_review_required": True,
        "current_loop_stage": "real_candle_labels_review",
        "next_required_action": get_candidate_17_labels_review_next_action(),
        # downstream gates locked
        "replay_gate_locked": True, "robustness_gate_locked": True,
        "portfolio_gate_locked": True, "paper_trading_gate_locked": True,
        "live_gate_locked": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_data_fetch": True, "no_re_detect": True, "no_relabel": True,
        "no_replay": True, "no_backtest": True, "no_pnl": True,
        "no_cost_application": True, "no_baseline": True, "no_optimization": True,
        "no_robustness": True, "no_portfolio_compute": True,
        "no_real_data_mutation": True, "no_shorting": True,
        "no_leverage_above_cap": True, "no_stage": True, "no_commit": True,
        "no_push": True, "no_auto_commit": True, "no_auto_push": True,
        "no_scheduler_change": True, "no_broker": True, "no_credentials": True,
        "no_order_logic": True, "no_auto_trading": True, "no_paper_trading": True,
        "no_live_trading": True, "no_gate_skip": True,
        "no_downstream_gate_unlock": True, "no_profitability_claim": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_c17_labels_review(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the review is research-only, labels-
    review-only, chain-gated on the frozen C17 detector dry-run, uses frozen local
    data only, pins the exact SHAs + frozen aggregates, records the structural
    verdict consistently (passed iff the structural rules hold), applies no
    PnL/cost, makes no profitability claim, locks downstream gates, and pins every
    capability flag False."""
    failures: list = []
    if record.get("mode") != L17_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_labels_review_only") is not True:
        failures.append("not_labels_review_only")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("verdict") != VERDICT_C17L_FROZEN:
        failures.append("verdict_not_frozen")

    # chain gate
    if record.get("detector_dry_run_valid") is not True:
        failures.append("detector_dry_run_not_valid")
    if record.get("detector_dry_run_verdict") != (
            "C17_DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW"):
        failures.append("detector_dry_run_not_frozen")

    # frozen local data only + pinned SHAs
    if record.get("uses_frozen_local_data_only") is not True:
        failures.append("not_frozen_local_data_only")
    if record.get("expected_labels_sha256") != EXPECTED_LABELS_SHA256:
        failures.append("labels_sha_tampered")
    if record.get("expected_summary_sha256") != EXPECTED_SUMMARY_SHA256:
        failures.append("summary_sha_tampered")
    if record.get("expected_source_sha256") != EXPECTED_SOURCE_SHA256:
        failures.append("source_sha_tampered")

    # pinned aggregates consistent with the structural rules
    sv = record.get("structural_review") or {}
    if record.get("n_rebalances") != N_REBALANCES:
        failures.append("n_rebalances_tampered")
    if sv.get("rebalances_ok") is not True:
        failures.append("rebalances_not_ok")
    if sv.get("all_weights_long_only") is not True:
        failures.append("not_long_only")
    if sv.get("gross_never_exceeds_cap") is not True:
        failures.append("gross_exceeds_cap")
    if sv.get("max_gross_exposure", 9.9) > MAX_GROSS_CAP + 1e-9:
        failures.append("max_gross_above_cap")
    if sv.get("vol_target_active") is not True:
        failures.append("vol_target_not_active")
    if sv.get("forward_oos_populated") is not True:
        failures.append("forward_oos_not_populated")
    if sv.get("avg_weekly_turnover", 9.9) > MAX_AVG_WEEKLY_TURNOVER_CAP:
        failures.append("turnover_exceeds_cap")
    for r in ("bull", "bear", "chop"):
        if (sv.get("per_regime") or {}).get(r, 0) <= 0:
            failures.append("regime_unpopulated_%s" % r)
    # structural verdict must be internally consistent (passed iff rules hold)
    expected_pass = (sv.get("rebalances_ok") and sv.get("all_weights_long_only")
                     and sv.get("gross_never_exceeds_cap")
                     and sv.get("vol_target_active")
                     and sv.get("forward_oos_populated"))
    if record.get("structural_passed") != bool(expected_pass):
        failures.append("structural_passed_inconsistent")
    if sv.get("passed") != bool(expected_pass):
        failures.append("structural_review_passed_inconsistent")

    # no PnL/cost here; no profitability claim; next gate = replay decision
    if record.get("cost_model_applied_here") is not False:
        failures.append("cost_model_applied")
    if record.get("cost_model_reserved_for_replay") is not True:
        failures.append("cost_not_reserved")
    if not record.get("not_yet_validated"):
        failures.append("missing_not_yet_validated_caveat")
    if record.get("next_required_action") != (
            "HUMAN_DECISION_C17_ADVANCE_TO_FEE_HONEST_REPLAY_OR_REJECT"):
        failures.append("next_action_not_replay_gate")

    # downstream gates locked
    for gate in ("replay_gate_locked", "robustness_gate_locked",
                 "portfolio_gate_locked", "paper_trading_gate_locked",
                 "live_gate_locked"):
        if record.get(gate) is not True:
            failures.append("downstream_gate_unlocked_%s" % gate)

    locks = record.get("scope_locks") or {}
    for key in ("no_data_fetch", "no_re_detect", "no_relabel", "no_replay",
                "no_backtest", "no_pnl", "no_cost_application", "no_baseline",
                "no_optimization", "no_shorting", "no_leverage_above_cap",
                "no_commit", "no_push", "no_broker", "no_order_logic",
                "no_auto_trading", "no_paper_trading", "no_live_trading",
                "no_gate_skip"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
