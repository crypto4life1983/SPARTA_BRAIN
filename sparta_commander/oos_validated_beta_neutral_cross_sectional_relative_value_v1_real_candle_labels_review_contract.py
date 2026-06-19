"""Candidate #19 -- oos_validated_beta_neutral_cross_sectional_relative_value_v1
-- REAL-CANDLE LABELS REVIEW (PURE, RESEARCH ONLY).

Records and validates the frozen real-candle LABELS for Candidate #19, produced by
`tools/c19_real_candle_labels_once.py` from the EXISTING, FROZEN, cached BTC/ETH/SOL
D1 spot OHLCV (no fetch). It pins the source-data SHA provenance, the gitignored
labels/summary artifact paths + SHAs, the frozen label aggregates, and a STRUCTURAL
verdict. Chain-gated on the committed C19 detector / spec / proposal.

LABELS STAGE ONLY: it records setup labels, OOS-neutrality pass/fail counts,
entries/exits/stops/invalidation, turnover, and structural counts. It runs NO replay,
NO PnL, applies NO fee (the 37 bps is RESERVED for replay), does NO optimization /
tuning / rescue, touches NO XAUUSD, commits NO data artifact, and does NOT start C20.

HONEST STRUCTURAL FINDING (preserved, not hidden): over 2020-08-11..2026-06-08 the
return-beta residual is beta-neutral out-of-sample on only a MINORITY of bars
(862 / 1977 ~ 44%), and the detector produces only 41 tradeable entries -- BELOW the
>= 100 structural sample-size gate. The position mechanics are clean (gross capped at
1.0, one live position, >= 5-bar spacing), but the intermittent OOS neutrality echoes
the exact C16 failure mode. This is FROZEN for the human's reject-or-advance decision.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.oos_validated_beta_neutral_cross_sectional_relative_value_v1_detector_spec_dry_run_contract as _d19  # noqa: E501

L19_SCHEMA_VERSION = 1
L19_MODE = "RESEARCH_ONLY"
L19_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = _d19.CANDIDATE_ID
CANDIDATE_FAMILY = _d19.CANDIDATE_FAMILY
CANDIDATE_NAME = _d19.CANDIDATE_NAME

VERDICT_C19L_FROZEN = "C19_LABELS_FROZEN_FOR_HUMAN_REVIEW"

# --- pinned artifact provenance (gitignored real-candle outputs) ------------
HEAD_AT_DETECTOR_DRY_RUN = "0662955c5904705f637f24abbb534b9aada7286c"
LABELS_PATH = ("data/oos_validated_beta_neutral_cross_sectional_relative_value_c19/"
               "labels/c19_labels.json")
SUMMARY_PATH = ("data/oos_validated_beta_neutral_cross_sectional_relative_value_c19/"
                "labels/c19_labels_summary.json")
EXPECTED_LABELS_SHA256 = (
    "92c8d3357247d00449d775f239fe0c9385743c1a6df18c4164a23bcb911e0def")
EXPECTED_SUMMARY_SHA256 = (
    "548788f474840e2601ab334b496fc13464d4a306ca9c611c067e2d8e33b81e30")
EXPECTED_SOURCE_SHA256 = {
    "BTCUSD": "043fb722b35e738a0c2050f9388defc7ca99322ed2f153989746ee28bbb89b88",
    "ETHUSD": "1bfd0ca86137747f0fe4c3fb127b00dcbd4885bf76056dbc9c091a9d4681c1a3",
    "SOLUSD": "4716d4d124bd7d5327fdc4230f7b2eaea70085df88c182dd129232ce802c0113",
}
SOURCE_PATHS = {
    "BTCUSD": "data/crypto_d1_spot/raw/BTC_1d.csv",
    "ETHUSD": "data/crypto_d1_spot/raw/ETH_1d.csv",
    "SOLUSD": "data/crypto_d1_spot/raw/SOL_1d.csv",
}

# --- pinned frozen aggregates (from the real-candle labels run) -------------
COMMON_WINDOW = ("2020-08-11", "2026-06-08")
N_COMMON_CANDLES = 2128
N_RETURN_BARS = 2127
N_EVAL_BARS = 1977
NEUTRALITY_PASS_COUNT = 862
NEUTRALITY_FAIL_COUNT = 1115
SETUP_COUNT = 46
ENTRY_COUNT = 41
EXIT_MEAN_REVERSION = 26
EXIT_DIVERGENCE_STOP = 0
EXIT_NEUTRALITY_BREAK = 15
EXIT_END_OF_DATA = 0
MAX_GROSS_OBSERVED = 1.0
SPACING_OK = True
MAX_CONCURRENT_POSITIONS = 1

# frozen gates / thresholds (reused, not redefined)
MIN_ENTRIES_STRUCTURAL = 100             # >= 100 structural sample-size gate
MAX_GROSS_CAP = _d19.MAX_GROSS           # 1.0
MIN_SPACING = _d19.MIN_SPACING           # 5
BETA_TOL = _d19.BETA_TOL                 # 0.10
ALL_IN_ROUND_TRIP_BPS = _d19.ALL_IN_ROUND_TRIP_BPS   # 37.0 reserved

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "re_detects", "relabels", "runs_labels",
    "runs_replay", "runs_backtest", "computes_pnl", "applies_cost_model",
    "runs_baseline", "runs_optimization", "tunes_parameters", "runs_rescue",
    "runs_robustness", "fetches_data", "reads_real_data", "mutates_data",
    "stages_data", "commits_data_artifact", "auto_commits", "auto_pushes",
    "modifies_scheduler", "sends_notifications", "calls_api", "uses_network",
    "uses_credentials", "connects_broker", "connects_exchange", "uses_real_money",
    "places_orders", "contains_order_logic", "carries_net_market_beta",
    "uses_price_level_hedge", "uses_xauusd", "adds_new_instrument_class",
    "uses_leverage_above_cap", "allows_overlapping_positions", "paper_trading",
    "live_trading", "deploys_capital", "promotes_gate", "unlocks_downstream_gate",
    "skips_any_gate", "starts_c20", "advances_without_human_approval",
    "claims_profitability", "claims_edge", "crosses_into_forbidden_gate",
)


def _structural_verdict() -> dict[str, Any]:
    """Pure structural assessment of the frozen labels. Mechanics-clean but honest
    about the sample-size and OOS-neutrality concerns (the C16 echo)."""
    meets_sample_gate = ENTRY_COUNT >= MIN_ENTRIES_STRUCTURAL
    neutrality_holds_majority = NEUTRALITY_PASS_COUNT > NEUTRALITY_FAIL_COUNT
    gross_cap_respected = MAX_GROSS_OBSERVED <= MAX_GROSS_CAP + 1e-9
    non_overlap_ok = MAX_CONCURRENT_POSITIONS <= 1
    spacing_ok = SPACING_OK
    neutrality_validated_at_all = NEUTRALITY_PASS_COUNT > 0
    exits_reconcile = (EXIT_MEAN_REVERSION + EXIT_DIVERGENCE_STOP
                       + EXIT_NEUTRALITY_BREAK + EXIT_END_OF_DATA) >= (ENTRY_COUNT - 1)
    # mechanics pass; the sample-size + neutrality-persistence are the open concerns
    mechanics_clean = (gross_cap_respected and non_overlap_ok and spacing_ok
                       and neutrality_validated_at_all)
    structural_concern = (not meets_sample_gate) or (not neutrality_holds_majority)
    return {
        "n_eval_bars": N_EVAL_BARS,
        "neutrality_pass_count": NEUTRALITY_PASS_COUNT,
        "neutrality_fail_count": NEUTRALITY_FAIL_COUNT,
        "neutrality_pass_rate": round(
            NEUTRALITY_PASS_COUNT / N_EVAL_BARS, 4),
        "neutrality_holds_majority": neutrality_holds_majority,
        "setup_count": SETUP_COUNT,
        "entry_count": ENTRY_COUNT,
        "min_entries_structural_gate": MIN_ENTRIES_STRUCTURAL,
        "meets_min_sample_gate": meets_sample_gate,
        "exit_mean_reversion": EXIT_MEAN_REVERSION,
        "exit_divergence_stop": EXIT_DIVERGENCE_STOP,
        "exit_neutrality_break": EXIT_NEUTRALITY_BREAK,
        "exits_reconcile_with_entries": exits_reconcile,
        "max_gross_observed": MAX_GROSS_OBSERVED,
        "gross_cap_respected": gross_cap_respected,
        "max_concurrent_positions": MAX_CONCURRENT_POSITIONS,
        "non_overlap_ok": non_overlap_ok,
        "spacing_ok": spacing_ok,
        "mechanics_clean": mechanics_clean,
        "structural_concern": structural_concern,
        "structural_concern_reasons": [
            r for r in (
                ("entry_count_%d_below_min_%d" % (ENTRY_COUNT,
                                                  MIN_ENTRIES_STRUCTURAL))
                if not meets_sample_gate else None,
                ("oos_neutrality_holds_only_%d_of_%d_bars"
                 % (NEUTRALITY_PASS_COUNT, N_EVAL_BARS))
                if not neutrality_holds_majority else None,
            ) if r],
    }


def get_candidate_19_labels_review_label() -> str:
    return (
        "Candidate #19 oos_validated_beta_neutral_cross_sectional_relative_value_v1 "
        "real-candle labels review (READ-ONLY, RESEARCH ONLY). FROZEN labels from "
        "cached BTC/ETH/SOL D1 (2020-08-11..2026-06-08, 2128 candles; no fetch, SHA "
        "verified). Mechanics clean (gross capped 1.0, one live position, >= 5-bar "
        "spacing) BUT a structural concern: only 41 tradeable entries (< 100 gate) "
        "and OOS beta-neutrality holds on only ~44% of bars (the C16 echo). LABELS "
        "STAGE ONLY -- no replay, no PnL, no fee (37 bps reserved), no optimization. "
        "Frozen for the human reject-or-advance decision. NOT a profitability claim.")


def get_candidate_19_labels_review_next_action() -> str:
    return "HUMAN_DECISION_C19_ADVANCE_TO_FEE_HONEST_REPLAY_OR_REJECT"


def build_c19_labels_review(repo_root: Any = ".",
                            tracked_paths: list | None = None) -> dict[str, Any]:
    """Assemble the frozen C19 real-candle labels review record. Pure; no I/O;
    chain-gated on the frozen C19 detector dry-run (and thus spec / proposal)."""
    detector = _d19.build_c19_detector_dry_run(repo_root, tracked_paths)
    detector_valid = _d19.validate_c19_detector_dry_run(detector)["valid"]
    detector_verdict = detector.get("verdict")

    blockers: list = []
    if not detector_valid:
        blockers.append("c19_detector_dry_run_invalid")
    if detector_verdict != "C19_DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW":
        blockers.append("c19_detector_dry_run_not_frozen")

    sv = _structural_verdict()

    record: dict[str, Any] = {
        "schema_version": L19_SCHEMA_VERSION, "mode": L19_MODE, "lane": L19_LANE,
        "label": get_candidate_19_labels_review_label(),
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "candidate_name": CANDIDATE_NAME,
        "is_labels_review_only": True,
        "blockers": blockers,
        "verdict": (VERDICT_C19L_FROZEN if not blockers
                    else "C19_LABELS_BLOCKED"),
        # chain provenance
        "detector_dry_run_verdict": detector_verdict,
        "detector_dry_run_valid": detector_valid,
        "head_at_detector_dry_run": HEAD_AT_DETECTOR_DRY_RUN,
        # frozen source data provenance (cached, no fetch, SHA-verified)
        "uses_frozen_cached_data_only": True,
        "no_new_data_fetch": True,
        "uses_xauusd": False,
        "source_paths": dict(SOURCE_PATHS),
        "expected_source_sha256": dict(EXPECTED_SOURCE_SHA256),
        "common_window": list(COMMON_WINDOW),
        "n_common_candles": N_COMMON_CANDLES,
        "n_return_bars": N_RETURN_BARS,
        # gitignored labels artifacts (SHA-pinned, NOT committed)
        "labels_path": LABELS_PATH, "summary_path": SUMMARY_PATH,
        "expected_labels_sha256": EXPECTED_LABELS_SHA256,
        "expected_summary_sha256": EXPECTED_SUMMARY_SHA256,
        "artifacts_gitignored_not_committed": True,
        # frozen detector params honoured exactly
        "beta_estimation_window_bars": _d19.BETA_WINDOW,
        "oos_neutrality_window_bars": _d19.OOS_WINDOW,
        "net_residual_beta_tolerance": BETA_TOL,
        "residual_zscore_window_bars": _d19.Z_WINDOW,
        "entry_zscore_threshold": _d19.ENTRY_Z,
        "exit_zscore_threshold": _d19.EXIT_Z,
        "stop_zscore_threshold": _d19.STOP_Z,
        "max_gross_exposure": MAX_GROSS_CAP,
        "min_bars_between_rebalances": MIN_SPACING,
        "is_market_neutral": True, "is_return_space": True,
        "uses_price_level_hedge": False,
        "oos_neutrality_is_gate_zero": True,
        # the structural verdict (mechanics clean; honest sample/neutrality concern)
        "structural_verdict": sv,
        "structural_mechanics_clean": sv["mechanics_clean"],
        "structural_concern": sv["structural_concern"],
        "meets_min_sample_gate": sv["meets_min_sample_gate"],
        "neutrality_holds_majority": sv["neutrality_holds_majority"],
        # cost reserved, not applied
        "cost_model_reserved_for_replay": True,
        "cost_model_applied_here": False,
        "fee_applied": False,
        "all_in_round_trip_bps_reserved": ALL_IN_ROUND_TRIP_BPS,
        "does_not_start_c20": True, "c20_candidate_id": None,
        "human_review_required": True,
        "current_loop_stage": "real_candle_labels_review",
        "next_required_action": get_candidate_19_labels_review_next_action(),
        # downstream gates locked
        "replay_gate_locked": True, "paper_trading_gate_locked": True,
        "live_gate_locked": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_build": True, "no_write": True, "no_execute": True,
        "no_re_detect": True, "no_relabel": True, "no_replay": True, "no_pnl": True,
        "no_cost_application": True, "no_baseline": True, "no_optimization": True,
        "no_tuning": True, "no_rescue": True, "no_robustness": True,
        "no_data_fetch": True, "no_real_data_access_beyond_frozen": True,
        "no_data_commit": True, "no_xauusd": True, "no_new_instrument_class": True,
        "no_price_level_hedge": True, "no_net_market_beta": True,
        "no_leverage_above_cap": True, "no_overlapping_positions": True,
        "no_stage": True, "no_commit": True, "no_push": True, "no_auto_commit": True,
        "no_auto_push": True, "no_scheduler_change": True, "no_broker": True,
        "no_credentials": True, "no_order_logic": True, "no_paper_trading": True,
        "no_live_trading": True, "no_gate_skip": True, "no_start_c20": True,
        "no_downstream_gate_unlock": True, "no_profitability_claim": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_c19_labels_review(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the unit is research-only,
    labels-review-only, chain-gated on the frozen C19 detector dry-run, uses ONLY the
    frozen cached BTC/ETH/SOL D1 data (no fetch, SHA-pinned source + gitignored
    artifacts not committed), honours the exact return-space market-neutral params,
    pins the honest frozen aggregates and a structural verdict (mechanics clean,
    sample/neutrality concern preserved -- it cannot be flipped to clear the >=100
    sample gate while entry_count is 41), reserves the 37 bps (no fee applied),
    keeps downstream gates locked, does not start C20, and pins every capability flag
    False."""
    failures: list = []
    if record.get("mode") != L19_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_labels_review_only") is not True:
        failures.append("not_labels_review_only")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("verdict") != VERDICT_C19L_FROZEN:
        failures.append("verdict_not_frozen")

    # chain gate on the frozen detector dry-run
    if record.get("detector_dry_run_valid") is not True:
        failures.append("detector_not_valid")
    if record.get("detector_dry_run_verdict") != (
            "C19_DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW"):
        failures.append("detector_not_frozen")
    if record.get("candidate_id") != "C19":
        failures.append("candidate_id_not_c19")

    # frozen cached data provenance, no fetch, SHA-pinned
    if record.get("uses_frozen_cached_data_only") is not True:
        failures.append("not_frozen_cached_only")
    if record.get("no_new_data_fetch") is not True:
        failures.append("must_not_fetch")
    if record.get("uses_xauusd") is not False:
        failures.append("must_not_use_xauusd")
    if record.get("expected_source_sha256") != EXPECTED_SOURCE_SHA256:
        failures.append("source_sha_tampered")
    if record.get("common_window") != list(COMMON_WINDOW):
        failures.append("common_window_tampered")
    if record.get("n_common_candles") != N_COMMON_CANDLES:
        failures.append("n_common_candles_tampered")

    # gitignored artifacts SHA-pinned and NOT committed
    if record.get("expected_labels_sha256") != EXPECTED_LABELS_SHA256:
        failures.append("labels_sha_tampered")
    if record.get("expected_summary_sha256") != EXPECTED_SUMMARY_SHA256:
        failures.append("summary_sha_tampered")
    if record.get("artifacts_gitignored_not_committed") is not True:
        failures.append("artifacts_must_not_be_committed")
    if not str(record.get("labels_path", "")).startswith("data/"):
        failures.append("labels_path_not_under_data")

    # exact params
    if record.get("beta_estimation_window_bars") != 90:
        failures.append("beta_window_not_90")
    if record.get("oos_neutrality_window_bars") != 60:
        failures.append("oos_window_not_60")
    if record.get("net_residual_beta_tolerance") != 0.10:
        failures.append("tolerance_not_0_10")
    if record.get("max_gross_exposure") != 1.0:
        failures.append("gross_cap_not_1")
    if record.get("uses_price_level_hedge") is not False:
        failures.append("must_not_use_price_level_hedge")
    if record.get("oos_neutrality_is_gate_zero") is not True:
        failures.append("neutrality_not_gate_zero")

    # structural verdict honesty -- cannot be flipped to clear the gate with 41 entries
    sv = record.get("structural_verdict") or {}
    if sv.get("entry_count") != ENTRY_COUNT:
        failures.append("entry_count_tampered")
    if sv.get("neutrality_pass_count") != NEUTRALITY_PASS_COUNT:
        failures.append("neutrality_pass_tampered")
    if sv.get("neutrality_fail_count") != NEUTRALITY_FAIL_COUNT:
        failures.append("neutrality_fail_tampered")
    if sv.get("meets_min_sample_gate") is not False:
        failures.append("sample_gate_falsely_passed")    # 41 < 100
    if sv.get("neutrality_holds_majority") is not False:
        failures.append("neutrality_majority_falsely_claimed")   # 862 < 1115
    if sv.get("gross_cap_respected") is not True:
        failures.append("gross_cap_finding_wrong")
    if sv.get("non_overlap_ok") is not True:
        failures.append("non_overlap_finding_wrong")
    if sv.get("spacing_ok") is not True:
        failures.append("spacing_finding_wrong")
    if record.get("structural_concern") is not True:
        failures.append("structural_concern_must_be_true")
    if record.get("meets_min_sample_gate") is not False:
        failures.append("top_level_sample_gate_wrong")

    # cost reserved, not applied
    if record.get("cost_model_applied_here") is not False:
        failures.append("cost_applied_in_labels")
    if record.get("fee_applied") is not False:
        failures.append("fee_applied_in_labels")
    if record.get("all_in_round_trip_bps_reserved") != 37.0:
        failures.append("cost_reserve_tampered")

    # no C20 + next action + downstream locks
    if record.get("does_not_start_c20") is not True:
        failures.append("must_not_start_c20")
    if record.get("c20_candidate_id") is not None:
        failures.append("c20_must_be_none")
    if record.get("next_required_action") != (
            "HUMAN_DECISION_C19_ADVANCE_TO_FEE_HONEST_REPLAY_OR_REJECT"):
        failures.append("next_action_not_replay_gate")
    for gate in ("replay_gate_locked", "paper_trading_gate_locked",
                 "live_gate_locked"):
        if record.get(gate) is not True:
            failures.append("downstream_gate_unlocked_%s" % gate)

    locks = record.get("scope_locks") or {}
    for key in ("no_re_detect", "no_relabel", "no_replay", "no_pnl",
                "no_cost_application", "no_optimization", "no_tuning", "no_rescue",
                "no_data_fetch", "no_data_commit", "no_xauusd", "no_price_level_hedge",
                "no_overlapping_positions", "no_commit", "no_push",
                "no_paper_trading", "no_live_trading", "no_start_c20",
                "no_gate_skip"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
