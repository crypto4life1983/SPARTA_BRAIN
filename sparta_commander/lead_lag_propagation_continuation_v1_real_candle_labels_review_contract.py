"""Candidate #13 (lead_lag_propagation_continuation_v1) real-candle detector
labels review / evidence-freeze contract.

RESEARCH ONLY. Reviews the FROZEN, SHA-pinned real-candle detector labels +
summary produced by tools/c13_real_candle_detection_once.py against the pushed,
chain-gated C13 detector spec + synthetic dry-run. Pure, in-memory evidence
record: NO file I/O, NO network, NO data fetch, NO replay, NO PnL, NO baseline
comparison, NO robustness, NO portfolio compute, NO trading. It does NOT claim
profitability or paper/live readiness.

Chain gate: build_c13_labels_review() requires
build_candidate_13_detector_spec_dry_run() to return
CANDIDATE_13_DETECTOR_DRY_RUN_READY.

LABELS-STAGE OUTCOME (frozen, honest): C13 FAILS the labels-stage structural
checks -> STRUCTURAL REJECTION. The confirmed-leader-move (r_L>0, z_L>=1.5) +
follower-lag trigger is too RARE on daily data: only 41 accepted labels over
2020-2026 (< the 100 minimum), ETHUSD has 18 (< 20 per-follower minimum), and
ALL three regimes are under the 20 minimum (bear 4, bull 19, chop 18). There are
ZERO forward-OOS 2026 labels, so the reserved forward window could not even be
populated. The weekday distribution is near-uniform (max share ~24%), but the
sample is too under-powered to support the cross-asset / cross-regime /
forward-OOS generalization the pipeline requires. This is caught EARLY, before
any replay -- the labels-stage battery did its job. The reject / one-edit
decision is the human's at the next gate.
"""
from __future__ import annotations

from typing import Any

from sparta_commander.lead_lag_propagation_continuation_v1_detector_spec_dry_run_contract import (  # noqa: E501
    VERDICT_C13DD_READY,
    build_candidate_13_detector_spec_dry_run,
)

C13L_SCHEMA_VERSION = 1
C13L_MODE = "RESEARCH_ONLY"
CANDIDATE_ID = "LEAD_LAG_PROPAGATION_CONTINUATION_V1"
CANDIDATE_FAMILY = "lead_lag_propagation_continuation"

VERDICT_C13L_FROZEN = "C13_REAL_CANDLE_LABELS_FROZEN_FOR_HUMAN_REVIEW"
VERDICT_C13L_STRUCTURAL_REJECTION = "C13_REAL_CANDLE_LABELS_STRUCTURAL_REJECTION"
VERDICT_C13L_BLOCKED = "C13_REAL_CANDLE_LABELS_BLOCKED"
NEXT_REQUIRED_ACTION = "HUMAN_DECISION_C13_REJECT_OR_INVOKE_ONE_EDIT_ALLOWANCE"

HEAD_AT_DETECTOR_DRY_RUN = "d32047c124168b3e478d7e181dfe6155d14d3604"

EXPECTED_SOURCE_SHA256 = {
    "BTCUSD": "043fb722b35e738a0c2050f9388defc7ca99322ed2f153989746ee28bbb89b88",
    "ETHUSD": "1bfd0ca86137747f0fe4c3fb127b00dcbd4885bf76056dbc9c091a9d4681c1a3",
    "SOLUSD": "4716d4d124bd7d5327fdc4230f7b2eaea70085df88c182dd129232ce802c0113",
}
EXPECTED_LABELS_SHA256 = (
    "e9f71db9ffb7c66c6127e2c1b3560d0091696463ef157df111752fae4ff22883")
EXPECTED_SUMMARY_SHA256 = (
    "7cb5cfd148a3c26093f712be2fa8035fa9f8959d0826c9e4bd09671887315b4d")
LABELS_PATH = ("data/lead_lag_propagation_continuation_c13/detector_labels/"
               "c13_detector_labels.json")
SUMMARY_PATH = ("data/lead_lag_propagation_continuation_c13/detector_labels/"
                "c13_detector_summary.json")

# Frozen labels-stage aggregates (from the SHA-pinned run).
ACCEPTED_LABEL_COUNT = 41
ACCEPTED_PRE_OVERLAP_COUNT = 47
DROPPED_LABELS_STAGE_NON_OVERLAP = 6
PER_FOLLOWER = {"ETHUSD": 18, "SOLUSD": 23}
PER_REGIME = {"bull": 19, "bear": 4, "chop": 18}
MIN_LABELS_TOTAL = 100
MIN_PER_FOLLOWER = 20
MIN_PER_REGIME = 20
WEEKDAY_DISTRIBUTION = {1: 10, 2: 4, 3: 8, 4: 5, 5: 8, 6: 3, 7: 3}
MAX_WEEKDAY_SHARE = 0.2439
FORWARD_OOS_START = "2026-01-01"
FORWARD_OOS_LABEL_COUNT = 0
COMMON_WINDOW = ("2020-08-11", "2026-06-08")

SAMPLE_SIZE_PASSED = False
STRUCTURAL_CHECKS_BATTERY = {
    "both_followers_present_ok": False,     # ETHUSD 18 < 20
    "cross_regime_coverage_ok": False,      # all regimes < 20
    "no_weekday_dependence_ok": True,       # max share ~24% (informational)
    "forward_oos_window_reserved": False,   # 0 forward-OOS labels
    "passed": False,
}
STRUCTURAL_REJECTION_PRESSURE = True

# The structural-rejection reasons, recorded honestly.
REJECTION_REASONS = {
    "total_below_minimum": True,            # 41 < 100
    "per_follower_below_minimum": True,     # ETHUSD 18 < 20
    "per_regime_below_minimum": True,       # bear 4 / bull 19 / chop 18 < 20
    "zero_forward_oos_labels": True,        # 0 in the reserved 2026 window
    "signal_too_rare_on_daily_data": True,  # z>=1.5 + lag is infrequent
}

HONEST_CAVEATS = (
    "Real-candle labels only; the LEADER (BTC) confirmed-move + FOLLOWER-lag "
    "trigger fired only 41 times over 2020-2026 -- too RARE on daily data.",
    "Labels-stage structural checks FAIL: total 41 < 100 minimum; ETHUSD 18 < "
    "20 per-follower minimum; ALL regimes under the 20 minimum (bear 4, bull "
    "19, chop 18); and ZERO forward-OOS 2026 labels (the reserved replay window "
    "could not be populated).",
    "The weekday distribution is near-uniform (max share ~24%), so there is no "
    "weekday dependence -- but that is moot given the sample is under-powered.",
    "NO replay, NO PnL, and NO baseline comparison were computed; this is a "
    "STRUCTURAL REJECTION at the labels stage, caught BEFORE any replay -- the "
    "early battery did its job. NOT a profitability claim, NOT a paper/live "
    "claim.",
    "Per the pre-registered C13 spec, sample below the total/per-follower/"
    "per-regime minimums is a STRUCTURAL REJECTION. The reject / one-edit-"
    "allowance decision is the human's at the next gate.",
)

CLAIM_LOCKS = (
    "no_profitability_claim", "no_paper_approval", "no_live_approval",
    "no_replay_in_this_gate", "no_pnl_in_this_gate",
    "no_baseline_comparison_in_this_gate", "no_relabel_after_freeze",
    "structural_rejection_at_labels_stage",
    "under_powered_sample_disclosed",
    "zero_forward_oos_labels_disclosed",
    "signal_too_rare_disclosed",
)

C13L_LABEL = (
    "C13 REAL-CANDLE LABELS (READ-ONLY, RESEARCH ONLY). "
    "lead_lag_propagation_continuation: only 41 accepted labels (ETH 18 / SOL "
    "23) across BTC->ETH/SOL; total < 100, per-follower < 20 (ETH), all regimes "
    "< 20, ZERO forward-OOS 2026 -> STRUCTURAL REJECTION (under-powered signal, "
    "caught before replay). NO REPLAY, NO PnL, NO BASELINE IN THIS GATE. NOT A "
    "PROFITABILITY CLAIM. NOT AN APPROVAL FOR PAPER OR LIVE."
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
    "auto_commits", "auto_pushes", "fits_parameters", "relabels_after_freeze",
    "uses_weekday_or_calendar_trigger", "relies_on_long_drift_or_bull_carry",
    "modifies_detector_labels_artifacts", "authorizes_paper_execution",
    "authorizes_micro_live", "authorizes_live_trading", "promotes_gate",
    "unlocks_downstream_gate", "claims_profitability", "claims_edge",
    "claims_paper_or_live_readiness", "executes", "writes_files",
)


def get_candidate_13_labels_review_label() -> str:
    return C13L_LABEL


def get_candidate_13_labels_review_next_action() -> str:
    return NEXT_REQUIRED_ACTION


def build_c13_labels_review(repo_root: Any = ".",
                            tracked_paths: list | None = None) -> dict[str, Any]:
    """Assemble the C13 real-candle labels review record. Chain-gated on the
    READY detector dry-run. Pure; no I/O. The frozen labels FAIL the labels-stage
    structural checks -> STRUCTURAL REJECTION."""
    record: dict[str, Any] = {
        "schema_version": C13L_SCHEMA_VERSION, "label": C13L_LABEL,
        "mode": C13L_MODE, "lane": "crypto_d1_auto_research",
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "verdict": None, "blockers": [],
        "head_at_detector_dry_run": HEAD_AT_DETECTOR_DRY_RUN,
        "expected_source_sha256": dict(EXPECTED_SOURCE_SHA256),
        "expected_labels_sha256": EXPECTED_LABELS_SHA256,
        "expected_summary_sha256": EXPECTED_SUMMARY_SHA256,
        "labels_path": LABELS_PATH, "summary_path": SUMMARY_PATH,
        "common_window": list(COMMON_WINDOW),
        "accepted_label_count": ACCEPTED_LABEL_COUNT,
        "accepted_pre_overlap_count": ACCEPTED_PRE_OVERLAP_COUNT,
        "dropped_labels_stage_non_overlap": DROPPED_LABELS_STAGE_NON_OVERLAP,
        "per_follower": dict(PER_FOLLOWER), "per_regime": dict(PER_REGIME),
        "min_labels_total": MIN_LABELS_TOTAL,
        "min_per_follower": MIN_PER_FOLLOWER, "min_per_regime": MIN_PER_REGIME,
        "weekday_distribution": dict(WEEKDAY_DISTRIBUTION),
        "max_weekday_share": MAX_WEEKDAY_SHARE,
        "forward_oos_start": FORWARD_OOS_START,
        "forward_oos_label_count": FORWARD_OOS_LABEL_COUNT,
        "sample_size_passed": SAMPLE_SIZE_PASSED,
        "structural_checks_battery": dict(STRUCTURAL_CHECKS_BATTERY),
        "structural_rejection_pressure": STRUCTURAL_REJECTION_PRESSURE,
        "rejection_reasons": dict(REJECTION_REASONS),
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
        "no_parameter_fitting": True, "no_relabel_after_freeze": True,
        "no_weekday_or_calendar_trigger": True,
        "no_long_drift_or_bull_carry_reliance": True,
        "no_profitability_claim": True, "no_paper_live_readiness_claim": True,
        "no_downstream_gate_unlock": True,
    }

    dd = build_candidate_13_detector_spec_dry_run(repo_root, tracked_paths or [])
    record["detector_dry_run_verdict"] = dd.get("verdict")
    if dd.get("verdict") != VERDICT_C13DD_READY:
        record["verdict"] = VERDICT_C13L_BLOCKED
        record["blockers"].append("detector_dry_run_not_ready")
        return record

    tracked = set(tracked_paths or [])
    if LABELS_PATH in tracked or SUMMARY_PATH in tracked:
        record["verdict"] = VERDICT_C13L_BLOCKED
        record["blockers"].append("labels_artifact_tracked")
        return record

    if STRUCTURAL_REJECTION_PRESSURE:
        record["verdict"] = VERDICT_C13L_STRUCTURAL_REJECTION
        return record
    record["verdict"] = VERDICT_C13L_FROZEN
    return record


def validate_c13_labels_review(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. STRUCTURAL_REJECTION is valid only when the SHA
    pins, the failing labels-stage facts (under-powered sample, zero forward-OOS),
    the no-replay/PnL/baseline posture, and all downstream locks are intact. The
    honest failing findings cannot be silently flipped to a pass."""
    failures: list = []
    if record.get("verdict") != VERDICT_C13L_STRUCTURAL_REJECTION:
        failures.append("verdict_not_structural_rejection")
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
    if record.get("detector_dry_run_verdict") != VERDICT_C13DD_READY:
        failures.append("detector_dry_run_verdict_tampered")

    # Honest failing facts cannot be flipped.
    if record.get("sample_size_passed") is not False:
        failures.append("sample_size_pass_flag_tampered")
    if record.get("structural_rejection_pressure") is not True:
        failures.append("structural_rejection_pressure_cleared")
    if (record.get("accepted_label_count") or 0) >= MIN_LABELS_TOTAL:
        failures.append("total_not_below_minimum")
    pf = record.get("per_follower") or {}
    if pf.get("ETHUSD", 0) >= MIN_PER_FOLLOWER:
        failures.append("eth_not_below_minimum")
    pr = record.get("per_regime") or {}
    if not all((pr.get(r, 0) < MIN_PER_REGIME) for r in ("bull", "bear", "chop")):
        failures.append("regimes_not_all_below_minimum")
    if record.get("forward_oos_label_count") != 0:
        failures.append("forward_oos_count_tampered")
    battery = record.get("structural_checks_battery") or {}
    if battery.get("passed") is not False:
        failures.append("battery_pass_flag_tampered")
    rr = record.get("rejection_reasons") or {}
    for key in ("total_below_minimum", "per_follower_below_minimum",
                "per_regime_below_minimum", "zero_forward_oos_labels"):
        if rr.get(key) is not True:
            failures.append("rejection_reason_cleared_%s" % key)

    if record.get("no_replay_or_pnl_or_baseline_in_this_gate") is not True:
        failures.append("no_replay_pnl_baseline_flag_tampered")
    if record.get("is_labels_review_only") is not True:
        failures.append("not_labels_review_only")

    locks = record.get("scope_locks") or {}
    for key in ("no_data_fetch", "no_replay", "no_pnl", "no_baseline_comparison",
                "no_portfolio_compute", "no_paper_trading", "no_live_trading",
                "no_relabel_after_freeze", "no_weekday_or_calendar_trigger",
                "no_data_mutation", "no_paper_live_readiness_claim"):
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
                     "structural_rejection_at_labels_stage",
                     "zero_forward_oos_labels_disclosed"):
        if required not in (record.get("claim_locks") or []):
            failures.append("claim_lock_missing_%s" % required)

    return {"valid": not failures, "failures": failures}
