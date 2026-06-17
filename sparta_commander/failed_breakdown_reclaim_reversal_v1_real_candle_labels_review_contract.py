"""Candidate #12 (failed_breakdown_reclaim_reversal_v1) real-candle detector
labels review / evidence-freeze contract.

RESEARCH ONLY. Reviews the FROZEN, SHA-pinned real-candle detector labels +
summary produced by tools/c12_real_candle_detection_once.py against the pushed,
chain-gated C12 detector spec + synthetic dry-run. Pure, in-memory evidence
record: NO file I/O, NO network, NO data fetch, NO replay, NO PnL, NO baseline
comparison, NO robustness, NO portfolio compute, NO trading. It does NOT claim
profitability or paper/live readiness. It freezes the labels-stage structural
evidence (counts, sample-size, cross-asset/cross-regime coverage, the
weekday-neutral DEPENDENCY test) + a human-review verdict, and locks every
downstream gate.

Chain gate: build_c12_labels_review() requires
build_candidate_12_detector_spec_dry_run() to return
CANDIDATE_12_DETECTOR_DRY_RUN_READY.

Labels-stage result (frozen): 206 accepted real-candle failed-breakdown reclaim
labels across BTC/ETH/SOL (all three assets >= 20), all three regimes
(bull/bear/chop, all >= 20 -- with bear the LARGEST bucket, not bull-carry), and
a near-uniform weekday distribution (max share ~21%, no weekday dependence).
Sample-size and the structural checks BOTH PASS; there is NO structural rejection
pressure. NO replay, NO PnL, and NO baseline comparison were computed in this
gate -- the must-beat buy-and-hold / random-entry baselines and the
horizon-exit-share cap run at the REPLAY stage, where the forward-OOS 2026
continuation check (reserved here) is also evaluated.
"""
from __future__ import annotations

from typing import Any

from sparta_commander.failed_breakdown_reclaim_reversal_v1_detector_spec_dry_run_contract import (  # noqa: E501
    VERDICT_C12DD_READY,
    build_candidate_12_detector_spec_dry_run,
)

C12L_SCHEMA_VERSION = 1
C12L_MODE = "RESEARCH_ONLY"
CANDIDATE_ID = "FAILED_BREAKDOWN_RECLAIM_REVERSAL_V1"
CANDIDATE_FAMILY = "failed_breakdown_reclaim_reversal"

VERDICT_C12L_FROZEN = "C12_REAL_CANDLE_LABELS_FROZEN_FOR_HUMAN_REVIEW"
VERDICT_C12L_STRUCTURAL_REJECTION = "C12_REAL_CANDLE_LABELS_STRUCTURAL_REJECTION"
VERDICT_C12L_BLOCKED = "C12_REAL_CANDLE_LABELS_BLOCKED"
NEXT_REQUIRED_ACTION = "HUMAN_DECISION_C12_ADVANCE_TO_FEE_HONEST_REPLAY_OR_REJECT"

HEAD_AT_DETECTOR_DRY_RUN = "c29c165cf0fc95dabf2da828c16977b4866df994"

EXPECTED_SOURCE_SHA256 = {
    "BTCUSD": "043fb722b35e738a0c2050f9388defc7ca99322ed2f153989746ee28bbb89b88",
    "ETHUSD": "1bfd0ca86137747f0fe4c3fb127b00dcbd4885bf76056dbc9c091a9d4681c1a3",
    "SOLUSD": "4716d4d124bd7d5327fdc4230f7b2eaea70085df88c182dd129232ce802c0113",
}
EXPECTED_LABELS_SHA256 = (
    "503bfe4f1b72279c5472fde335d97446aad37303b029ea82ed5c4f50af299764")
EXPECTED_SUMMARY_SHA256 = (
    "3682b756f2a929b84265b8c803103baa3c12cfba183c45008c5f82e4da5cce31")
LABELS_PATH = ("data/failed_breakdown_reclaim_reversal_c12/detector_labels/"
               "c12_detector_labels.json")
SUMMARY_PATH = ("data/failed_breakdown_reclaim_reversal_c12/detector_labels/"
                "c12_detector_summary.json")

# Frozen labels-stage aggregates (from the SHA-pinned run).
ACCEPTED_LABEL_COUNT = 206
ACCEPTED_PRE_OVERLAP_COUNT = 294
DROPPED_LABELS_STAGE_NON_OVERLAP = 88
PER_ASSET = {"BTCUSD": 76, "ETHUSD": 64, "SOLUSD": 66}
PER_REGIME = {"bull": 80, "bear": 90, "chop": 36}
MIN_LABELS_TOTAL = 100
MIN_PER_ASSET = 20
MIN_PER_REGIME = 20
WEEKDAY_DISTRIBUTION = {1: 44, 2: 39, 3: 22, 4: 29, 5: 33, 6: 27, 7: 12}
MAX_WEEKDAY_SHARE = 0.2136
FORWARD_OOS_START = "2026-01-01"
FORWARD_OOS_LABEL_COUNT = 22

SAMPLE_SIZE_PASSED = True
STRUCTURAL_CHECKS_BATTERY = {
    "cross_asset_coverage_ok": True,
    "cross_regime_coverage_ok": True,
    "no_weekday_dependence_ok": True,
    "forward_oos_window_reserved": True,
    "passed": True,
}
STRUCTURAL_REJECTION_PRESSURE = False

HONEST_CAVEATS = (
    "Real-candle labels only; a single-asset structural EVENT (a close-confirmed "
    "reclaim of a pierced 20-day low), NOT long-drift and NOT a calendar/weekday "
    "edge.",
    "Labels-stage structural checks PASS: cross-asset (3 assets, all >= 20), "
    "cross-regime (bull/bear/chop, all >= 20 -- bear is the LARGEST bucket, so "
    "the labels are NOT bull-carry concentrated), no weekday dependence (max "
    "weekday share ~21%).",
    "NO replay, NO PnL, and NO baseline comparison were computed in this gate; "
    "profitability is unknown and NOT claimed. Passing the labels gate is NOT a "
    "paper/live-readiness claim.",
    "The decisive C12 gates -- must-beat matched BUY-AND-HOLD and matched "
    "RANDOM-ENTRY baselines, the <=50% horizon-exit-share cap (target capture "
    "must dominate), the forward-OOS 2026 continuation check, and cross-regime "
    "net symmetry -- still have to be RUN at the replay stage; passing "
    "labels-stage coverage does NOT pre-judge them.",
)

CLAIM_LOCKS = (
    "no_profitability_claim", "no_paper_approval", "no_live_approval",
    "no_capital_deployment", "no_portfolio_allocation", "no_replay_in_this_gate",
    "no_pnl_in_this_gate", "no_baseline_comparison_in_this_gate",
    "no_parameter_fitting", "no_best_asset_selection",
    "single_asset_event_not_long_drift",
    "structural_checks_passed_at_labels",
    "baselines_and_horizon_cap_still_required_at_replay",
    "forward_oos_still_required_at_replay",
)

C12L_LABEL = (
    "C12 REAL-CANDLE LABELS (READ-ONLY, RESEARCH ONLY). "
    "failed_breakdown_reclaim_reversal: 206 close-confirmed reclaim labels across "
    "BTC/ETH/SOL; cross-asset + cross-regime (bull/bear/chop, bear largest) + "
    "weekday-neutral coverage PASS; sample-size PASS; NO structural rejection "
    "pressure. NO REPLAY, NO PnL, NO BASELINE IN THIS GATE. NOT A PROFITABILITY "
    "CLAIM. NOT AN APPROVAL FOR PAPER OR LIVE."
)

_CAPABILITY_FLAGS_FALSE = (
    "runs_detection_now", "labels_now", "fetches_data", "stages_data_now",
    "mutates_source_data", "runs_replay", "runs_replay_now", "computes_pnl",
    "runs_baseline_comparison_now", "runs_robustness",
    "runs_generalization_now", "runs_portfolio_compute", "calls_api",
    "uses_network", "uses_credentials", "uses_wallet", "uses_account",
    "connects_broker", "connects_exchange", "uses_real_money",
    "contains_order_logic", "contains_portfolio_allocation_logic",
    "deploys_capital", "starts_scheduler", "sends_notifications",
    "auto_commits", "auto_pushes", "fits_parameters", "selects_best_asset",
    "uses_weekday_or_calendar_trigger", "relies_on_long_drift_or_bull_carry",
    "modifies_detector_labels_artifacts", "authorizes_paper_execution",
    "authorizes_micro_live", "authorizes_live_trading", "promotes_gate",
    "unlocks_downstream_gate", "claims_profitability", "claims_edge",
    "claims_paper_or_live_readiness", "executes", "writes_files",
)


def get_candidate_12_labels_review_label() -> str:
    return C12L_LABEL


def get_candidate_12_labels_review_next_action() -> str:
    return NEXT_REQUIRED_ACTION


def build_c12_labels_review(repo_root: Any = ".",
                            tracked_paths: list | None = None) -> dict[str, Any]:
    """Assemble the C12 real-candle labels review record. Chain-gated on the
    READY detector dry-run. Pure; no I/O."""
    record: dict[str, Any] = {
        "schema_version": C12L_SCHEMA_VERSION, "label": C12L_LABEL,
        "mode": C12L_MODE, "lane": "crypto_d1_auto_research",
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "verdict": None, "blockers": [],
        "head_at_detector_dry_run": HEAD_AT_DETECTOR_DRY_RUN,
        "expected_source_sha256": dict(EXPECTED_SOURCE_SHA256),
        "expected_labels_sha256": EXPECTED_LABELS_SHA256,
        "expected_summary_sha256": EXPECTED_SUMMARY_SHA256,
        "labels_path": LABELS_PATH, "summary_path": SUMMARY_PATH,
        "accepted_label_count": ACCEPTED_LABEL_COUNT,
        "accepted_pre_overlap_count": ACCEPTED_PRE_OVERLAP_COUNT,
        "dropped_labels_stage_non_overlap": DROPPED_LABELS_STAGE_NON_OVERLAP,
        "per_asset": dict(PER_ASSET), "per_regime": dict(PER_REGIME),
        "min_labels_total": MIN_LABELS_TOTAL, "min_per_asset": MIN_PER_ASSET,
        "min_per_regime": MIN_PER_REGIME,
        "weekday_distribution": dict(WEEKDAY_DISTRIBUTION),
        "max_weekday_share": MAX_WEEKDAY_SHARE,
        "forward_oos_start": FORWARD_OOS_START,
        "forward_oos_label_count": FORWARD_OOS_LABEL_COUNT,
        "sample_size_passed": SAMPLE_SIZE_PASSED,
        "structural_checks_battery": dict(STRUCTURAL_CHECKS_BATTERY),
        "structural_rejection_pressure": STRUCTURAL_REJECTION_PRESSURE,
        "single_asset_event_not_long_drift": True,
        "no_replay_or_pnl_or_baseline_in_this_gate": True,
        "honest_caveats": list(HONEST_CAVEATS),
        "claim_locks": list(CLAIM_LOCKS),
        "is_labels_review_only": True,
        "current_loop_stage": "real_candle_labels_review",
        "human_review_required": True,
        "replay_gate_locked": True, "pnl_gate_locked": True,
        "baseline_gate_locked": True, "robustness_gate_locked": True,
        "data_fetch_gate_locked": True, "paper_trading_gate_locked": True,
        "live_gate_locked": True,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_data_fetch": True, "no_data_mutation": True, "no_replay": True,
        "no_pnl": True, "no_baseline_comparison": True, "no_robustness": True,
        "no_generalization_run": True, "no_portfolio_compute": True,
        "no_paper_trading": True, "no_live_trading": True, "no_broker": True,
        "no_credentials": True, "no_order_logic": True,
        "no_parameter_fitting": True, "no_best_asset_selection": True,
        "no_weekday_or_calendar_trigger": True,
        "no_long_drift_or_bull_carry_reliance": True,
        "no_profitability_claim": True, "no_paper_live_readiness_claim": True,
        "no_downstream_gate_unlock": True,
    }

    dd = build_candidate_12_detector_spec_dry_run(repo_root, tracked_paths or [])
    record["detector_dry_run_verdict"] = dd.get("verdict")
    if dd.get("verdict") != VERDICT_C12DD_READY:
        record["verdict"] = VERDICT_C12L_BLOCKED
        record["blockers"].append("detector_dry_run_not_ready")
        return record

    tracked = set(tracked_paths or [])
    if LABELS_PATH in tracked or SUMMARY_PATH in tracked:
        record["verdict"] = VERDICT_C12L_BLOCKED
        record["blockers"].append("labels_artifact_tracked")
        return record

    if STRUCTURAL_REJECTION_PRESSURE:
        record["verdict"] = VERDICT_C12L_STRUCTURAL_REJECTION
        return record
    record["verdict"] = VERDICT_C12L_FROZEN
    return record


def validate_c12_labels_review(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. FROZEN is valid only when the SHA pins, the
    labels-stage pass facts, the single-asset-event-not-drift framing, the
    no-replay/PnL/baseline posture, and all downstream locks are intact."""
    failures: list = []
    if record.get("verdict") != VERDICT_C12L_FROZEN:
        failures.append("verdict_not_frozen")
    if record.get("blockers"):
        failures.append("has_blockers")

    for field, expected in (
            ("expected_labels_sha256", EXPECTED_LABELS_SHA256),
            ("expected_summary_sha256", EXPECTED_SUMMARY_SHA256)):
        v = record.get(field)
        if not isinstance(v, str) or len(v) != 64 or v != expected:
            failures.append("bad_sha_%s" % field)
    src = record.get("expected_source_sha256") or {}
    for k, expected in EXPECTED_SOURCE_SHA256.items():
        if src.get(k) != expected:
            failures.append("bad_source_sha_%s" % k)
    if record.get("head_at_detector_dry_run") != HEAD_AT_DETECTOR_DRY_RUN:
        failures.append("head_tampered")
    if record.get("detector_dry_run_verdict") != VERDICT_C12DD_READY:
        failures.append("detector_dry_run_verdict_tampered")

    # Sample-size + per-asset/per-regime minimums.
    if record.get("sample_size_passed") is not True:
        failures.append("sample_size_flag_tampered")
    if (record.get("accepted_label_count") or 0) < MIN_LABELS_TOTAL:
        failures.append("total_below_minimum")
    pa = record.get("per_asset") or {}
    for s in ("BTCUSD", "ETHUSD", "SOLUSD"):
        if pa.get(s, 0) < MIN_PER_ASSET:
            failures.append("per_asset_below_min_%s" % s)
    pr = record.get("per_regime") or {}
    for r in ("bull", "bear", "chop"):
        if pr.get(r, 0) < MIN_PER_REGIME:
            failures.append("per_regime_below_min_%s" % r)

    # Structural checks battery passed at labels.
    battery = record.get("structural_checks_battery") or {}
    for key in ("cross_asset_coverage_ok", "cross_regime_coverage_ok",
                "no_weekday_dependence_ok", "passed"):
        if battery.get(key) is not True:
            failures.append("battery_flag_%s" % key)
    if record.get("max_weekday_share", 1.0) > 0.25:
        failures.append("weekday_share_above_cap")
    if record.get("structural_rejection_pressure") is not False:
        failures.append("structural_rejection_pressure_set")

    # Single-asset event not drift + no replay/pnl/baseline + posture.
    if record.get("single_asset_event_not_long_drift") is not True:
        failures.append("event_not_drift_flag_tampered")
    if record.get("no_replay_or_pnl_or_baseline_in_this_gate") is not True:
        failures.append("no_replay_pnl_baseline_flag_tampered")
    if record.get("is_labels_review_only") is not True:
        failures.append("not_labels_review_only")

    locks = record.get("scope_locks") or {}
    for key in ("no_data_fetch", "no_replay", "no_pnl", "no_baseline_comparison",
                "no_portfolio_compute", "no_paper_trading", "no_live_trading",
                "no_best_asset_selection", "no_weekday_or_calendar_trigger",
                "no_long_drift_or_bull_carry_reliance", "no_data_mutation",
                "no_paper_live_readiness_claim"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for key in ("replay_gate_locked", "pnl_gate_locked", "baseline_gate_locked",
                "robustness_gate_locked", "data_fetch_gate_locked",
                "paper_trading_gate_locked", "live_gate_locked",
                "human_review_required"):
        if record.get(key) is not True:
            failures.append("gate_flag_tampered_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    for required in ("no_profitability_claim", "no_replay_in_this_gate",
                     "no_baseline_comparison_in_this_gate",
                     "single_asset_event_not_long_drift",
                     "baselines_and_horizon_cap_still_required_at_replay",
                     "forward_oos_still_required_at_replay"):
        if required not in (record.get("claim_locks") or []):
            failures.append("claim_lock_missing_%s" % required)

    return {"valid": not failures, "failures": failures}
