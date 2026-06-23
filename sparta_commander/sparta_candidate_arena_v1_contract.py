"""SPARTA Candidate Arena v1 -- PURE, READ-ONLY normalized candidate comparison.

A repo-native "arena" that normalizes all active / on-deck / rejected / feasibility candidate
families into one comparison table, using ONLY frozen evidence + committed contracts/ledgers +
known SPARTA state (encoded here as an AS-OF snapshot). It is inspired by AI strategy loops but
connects to NOTHING: no exchange, no live orders, no data fetch, no optimization, no promotion,
no gate relaxation. Where evidence does not exist it is marked MISSING_EVIDENCE, never guessed.

Scores are NORMALIZED 0-5 qualitative reads of the committed evidence (5 = best on that axis),
or "MISSING_EVIDENCE" (not measured) / "N/A" (axis not applicable). They are NOT recomputed from
data and carry no promotion weight. The arena RANKS NOTHING for action; promotion stays 100%
human-gated.

AS-OF the snapshot below: C22 4/20 HOLD (replay locked); C23/C24 rejected as sleeves (and their
cross-sectional evals ran on a survivorship-biased broad crypto universe); C25 no-go; funding
SELECTION rejected; always-on funding carry kept as a diversifier finding (not an engine);
VRP Phase-1 index-level feasibility PROMISING but NOT promoted; VRP Phase-2 = data-pipeline
status only (one clean forward snapshot + a daily scheduler -- NOT backtest evidence).
"""
from __future__ import annotations

from typing import Any

ARENA_SCHEMA_VERSION = 1
ARENA_MODE = "RESEARCH_ONLY"
AS_OF = "2026-06-23"

COLUMNS = (
    "candidate_id", "family_name", "lane", "current_status", "evidence_status",
    "return_engine_score", "drawdown_score", "benchmark_score", "cost_sensitivity_score",
    "correlation_or_diversifier_score", "blocker_reason", "next_safe_action",
)

MISSING = "MISSING_EVIDENCE"
NA = "N/A"

ROWS = (
    {"candidate_id": "C22", "family_name": "external_signum_trend_radar_gc_long_short",
     "lane": "crypto_d1_auto_research", "current_status": "ACTIVE_HOLD",
     "evidence_status": "COLLECTING_4_OF_20_WINDOWS",
     "return_engine_score": MISSING, "drawdown_score": MISSING, "benchmark_score": MISSING,
     "cost_sensitivity_score": MISSING, "correlation_or_diversifier_score": MISSING,
     "blocker_reason": "insufficient frozen windows (4/20); replay LOCKED until the 20/20 "
                       "frozen-window review gate",
     "next_safe_action": "continue daily GC import toward 20/20; no replay/eval until review"},

    {"candidate_id": "C23", "family_name": "crypto_cross_sectional_low_volatility_anomaly_beta_neutral",
     "lane": "portfolio_sleeve_evaluation", "current_status": "REJECTED",
     "evidence_status": "EXPLORATORY_SURVIVORSHIP_BIASED",
     "return_engine_score": 0, "drawdown_score": 2, "benchmark_score": 0,
     "cost_sensitivity_score": 1, "correlation_or_diversifier_score": 3,
     "blocker_reason": "net-negative neutral sleeve (short high-vol leg bled, 14.8x turnover / "
                       "29.5% cost drag); evaluated only on a SURVIVORSHIP-BIASED broad crypto "
                       "universe",
     "next_safe_action": "keep rejected; no action"},

    {"candidate_id": "C24", "family_name": "crypto_cross_sectional_illiquidity_premium_beta_neutral",
     "lane": "portfolio_sleeve_evaluation", "current_status": "REJECTED",
     "evidence_status": "EXPLORATORY_SURVIVORSHIP_BIASED",
     "return_engine_score": 1, "drawdown_score": 1, "benchmark_score": 1,
     "cost_sensitivity_score": 3, "correlation_or_diversifier_score": 4,
     "blocker_reason": "non-stationary 2021-only artifact (ex-2021 -45.7%); does not beat BTC "
                       "risk-adjusted; evaluated only on a SURVIVORSHIP-BIASED broad crypto "
                       "universe",
     "next_safe_action": "keep rejected; no action"},

    {"candidate_id": "C25", "family_name": "intraday_momentum_breakout_retest_reversal_scalping_directional",
     "lane": "idea_bank", "current_status": "NO_GO",
     "evidence_status": "NO_GO_NEAR_DUPLICATE",
     "return_engine_score": 0, "drawdown_score": MISSING, "benchmark_score": MISSING,
     "cost_sensitivity_score": 0, "correlation_or_diversifier_score": 0,
     "blocker_reason": "near-duplicate recombination of already-rejected directional families "
                       "(C3/C4/C14/C15/C18); 5m scalping cost; not a new edge axis",
     "next_safe_action": "keep no-go in idea-bank; no action"},

    {"candidate_id": "FUNDING_SELECTION", "family_name": "cross_sectional_crypto_funding_carry_market_neutral",
     "lane": "portfolio_sleeve_evaluation", "current_status": "REJECTED",
     "evidence_status": "EXPLORATORY_FUNDING_CASHFLOW_ONLY",
     "return_engine_score": 1, "drawdown_score": 4, "benchmark_score": 1,
     "cost_sensitivity_score": 2, "correlation_or_diversifier_score": 5,
     "blocker_reason": "selection/timing does NOT beat the always-on funding null (7.0% < 8.7%) "
                       "and is 2021-concentrated (ex-2021 +0.3%); funding-cashflow-only proxy",
     "next_safe_action": "keep rejected; no action"},

    {"candidate_id": "ALWAYS_ON_CARRY", "family_name": "always_on_broad_multi_asset_neutral_funding_carry",
     "lane": "portfolio_sleeve_evaluation", "current_status": "DIVERSIFIER_FINDING",
     "evidence_status": "EXPLORATORY_FUNDING_CASHFLOW_ONLY",
     "return_engine_score": 1, "drawdown_score": 4, "benchmark_score": NA,
     "cost_sensitivity_score": 4, "correlation_or_diversifier_score": 5,
     "blocker_reason": "useful uncorrelated DAMPENER (CAGR ~8.7%, corr-to-BTC ~0.05, durable "
                       "ex-2021/recent) but NOT a return engine; funding-cashflow-only upper "
                       "bound; survivorship-biased",
     "next_safe_action": "diversifier on record; deployment-grade revalidation needs perp-basis "
                         "+ survivorship-aware data (separate human gate)"},

    {"candidate_id": "VRP_PHASE1", "family_name": "crypto_volatility_risk_premium_index_level_feasibility",
     "lane": "portfolio_sleeve_evaluation", "current_status": "FEASIBILITY_FINDING_NOT_PROMOTED",
     "evidence_status": "PROMISING_INDEX_LEVEL_PROXY",
     "return_engine_score": 3, "drawdown_score": MISSING, "benchmark_score": 3,
     "cost_sensitivity_score": MISSING, "correlation_or_diversifier_score": 5,
     "blocker_reason": "INDEX-LEVEL PROXY only (DVOL implied vs realized) -- NOT a tradeable "
                       "delta-hedged backtest; short-vol tail risk; needs per-strike options "
                       "data; durable for BTC (avg +8.8, hit 72.7%, ex-2021 +7.2) but unproven "
                       "tradeable",
     "next_safe_action": "proceed to per-strike options data phase (hybrid: forward collector "
                         "running + paid Tardis decision); NOT promoted"},

    {"candidate_id": "VRP_PHASE2_DATA", "family_name": "deribit_btc_option_chain_forward_collection",
     "lane": "phase_2_data_pipeline", "current_status": "DATA_COLLECTION_STATUS",
     "evidence_status": "NOT_BACKTEST_EVIDENCE",
     "return_engine_score": NA, "drawdown_score": NA, "benchmark_score": NA,
     "cost_sensitivity_score": NA, "correlation_or_diversifier_score": NA,
     "blocker_reason": "one clean forward snapshot (892 rows, 2026-06-23) + daily 00:20 "
                       "scheduler = DATA PIPELINE STATUS ONLY; forward-only (no backfill); a "
                       "single snapshot is NOT backtest/strategy/promotion evidence",
     "next_safe_action": "accumulate forward snapshots; human decision on the paid Tardis "
                         "historical path for a true backtest"},
)

_CAPABILITY_FLAGS_FALSE = (
    "executes", "fetches_data", "connects_exchange", "connects_broker", "places_orders",
    "contains_order_logic", "uses_private_endpoints", "uses_credentials", "optimizes_parameters",
    "promotes_any_candidate", "activates_any_candidate", "advances_c22", "relaxes_any_gate",
    "unlocks_replay", "paper_trading", "live_trading", "modifies_official_ledger",
    "modifies_lifecycle", "ranks_for_action", "treats_snapshot_as_backtest_evidence",
    "claims_profitability", "crosses_into_forbidden_gate",
)


def build_candidate_arena() -> dict[str, Any]:
    """PURE. Assemble the normalized candidate-arena table from frozen/known SPARTA state. No
    I/O; ranks nothing for action; promotes nothing."""
    rows = [dict(r) for r in ROWS]
    # invariant checks fold into the record (no guessing)
    c22 = next(r for r in rows if r["candidate_id"] == "C22")
    vrp1 = next(r for r in rows if r["candidate_id"] == "VRP_PHASE1")
    vrp2 = next(r for r in rows if r["candidate_id"] == "VRP_PHASE2_DATA")

    record: dict[str, Any] = {
        "schema_version": ARENA_SCHEMA_VERSION, "mode": ARENA_MODE, "as_of": AS_OF,
        "is_read_only_arena": True,
        "columns": list(COLUMNS),
        "rows": rows,
        "row_count": len(rows),
        # explicit invariants the arena asserts about known state
        "c22_is_hold": c22["current_status"] == "ACTIVE_HOLD",
        "c23_c24_blocked_by_broad_universe": all(
            "SURVIVORSHIP-BIASED broad crypto universe" in r["blocker_reason"]
            for r in rows if r["candidate_id"] in ("C23", "C24")),
        "vrp_phase1_promising_not_promoted": (
            vrp1["evidence_status"] == "PROMISING_INDEX_LEVEL_PROXY"
            and "NOT_PROMOTED" in vrp1["current_status"]),
        "vrp_phase2_not_backtest_evidence": vrp2["evidence_status"] == "NOT_BACKTEST_EVIDENCE",
        "anything_ready_for_promotion": False,
        "anything_ready_for_human_review": False,
        "review_notes": [
            "Nothing is promotion-ready. Promotion remains 100% human-gated.",
            "VRP Phase-1 (BTC) is the most promising signal but is an INDEX-LEVEL PROXY -- its "
            "next step (per-strike options data phase) is human-gated, NOT promotion.",
            "C22 becomes review-eligible only at 20/20 frozen windows (currently 4/20).",
            "always-on funding carry is a diversifier finding, not a return engine.",
        ],
        "missing_evidence_cells": sum(
            1 for r in rows for c in COLUMNS if r.get(c) == MISSING),
        "human_review_required": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_execute": True, "no_fetch": True, "no_exchange": True, "no_broker": True,
        "no_orders": True, "no_private_endpoints": True, "no_credentials": True,
        "no_optimization": True, "no_promote": True, "no_activate": True, "no_advance_c22": True,
        "no_gate_relax": True, "no_replay_unlock": True, "no_paper_trading": True,
        "no_live_trading": True, "no_modify_ledger": True, "no_rank_for_action": True,
        "no_snapshot_as_backtest_evidence": True, "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_candidate_arena(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when read-only, every row carries all 12 columns, the
    known-state invariants hold (C22 HOLD; C23/C24 blocked by the broad-universe issue; VRP
    Phase-1 promising + NOT promoted; VRP Phase-2 NOT backtest evidence), nothing is marked
    promotion/review-ready, missing evidence is explicit (not guessed), and every capability flag
    is False."""
    failures: list = []
    if record.get("mode") != ARENA_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_read_only_arena") is not True:
        failures.append("not_read_only")
    rows = record.get("rows") or []
    if not rows:
        failures.append("no_rows")
    for r in rows:
        for c in COLUMNS:
            if c not in r:
                failures.append("row_missing_column:%s:%s" % (r.get("candidate_id"), c))

    by = {r.get("candidate_id"): r for r in rows}
    # C22 HOLD
    if not by.get("C22") or by["C22"]["current_status"] != "ACTIVE_HOLD":
        failures.append("c22_not_hold")
    if record.get("c22_is_hold") is not True:
        failures.append("c22_hold_flag_off")
    # C23/C24 blocked by broad-universe issue
    for cid in ("C23", "C24"):
        r = by.get(cid)
        if not r or "SURVIVORSHIP-BIASED broad crypto universe" not in r["blocker_reason"]:
            failures.append("%s_not_blocked_by_broad_universe" % cid)
        if r and r["current_status"] != "REJECTED":
            failures.append("%s_not_rejected" % cid)
    if record.get("c23_c24_blocked_by_broad_universe") is not True:
        failures.append("c23c24_block_flag_off")
    # VRP Phase-1 promising but NOT promoted
    v1 = by.get("VRP_PHASE1")
    if not v1 or v1["evidence_status"] != "PROMISING_INDEX_LEVEL_PROXY":
        failures.append("vrp1_not_promising")
    if not v1 or "NOT_PROMOTED" not in v1["current_status"]:
        failures.append("vrp1_marked_promoted")
    if record.get("vrp_phase1_promising_not_promoted") is not True:
        failures.append("vrp1_flag_off")
    # VRP Phase-2 NOT backtest evidence
    v2 = by.get("VRP_PHASE2_DATA")
    if not v2 or v2["evidence_status"] != "NOT_BACKTEST_EVIDENCE":
        failures.append("vrp2_treated_as_evidence")
    if v2 and v2["current_status"] != "DATA_COLLECTION_STATUS":
        failures.append("vrp2_not_data_status")
    if record.get("vrp_phase2_not_backtest_evidence") is not True:
        failures.append("vrp2_flag_off")
    # nothing promotion/review ready
    if record.get("anything_ready_for_promotion") is not False:
        failures.append("must_not_be_promotion_ready")
    if record.get("anything_ready_for_human_review") is not False:
        failures.append("must_not_be_review_ready")
    # missing evidence explicit (C22 return-engine etc. must be MISSING_EVIDENCE, not a number)
    if by.get("C22") and by["C22"]["return_engine_score"] != MISSING:
        failures.append("c22_return_engine_must_be_missing_evidence")
    if record.get("missing_evidence_cells", 0) <= 0:
        failures.append("no_missing_evidence_marked")

    locks = record.get("scope_locks") or {}
    for k in ("no_execute", "no_fetch", "no_exchange", "no_orders", "no_private_endpoints",
              "no_optimization", "no_promote", "no_activate", "no_advance_c22", "no_gate_relax",
              "no_replay_unlock", "no_paper_trading", "no_live_trading", "no_modify_ledger",
              "no_snapshot_as_backtest_evidence"):
        if locks.get(k) is not True:
            failures.append("scope_lock_false_%s" % k)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
