"""Candidate #20 -- mechanically_neutral_spot_perp_basis_funding_carry_v1
-- REAL-CANDLE LABELS REVIEW (PURE, RESEARCH ONLY).

Records and validates the frozen real-candle LABELS for Candidate #20, produced by
`tools/c20_real_candle_labels_once.py` from the EXISTING, FROZEN, PUBLIC BTC/ETH/SOL
spot + USDT-perp + funding D1 dataset (no fetch). It pins the 9 source-data SHA
provenance hashes, the gitignored labels/summary artifact paths + SHAs, the frozen
per-asset + total label aggregates, the mechanical-neutrality validation counts, the
forward-OOS 2026 counts, and a STRUCTURAL verdict. Chain-gated on the committed C20
detector / spec / proposal.

LABELS STAGE ONLY: it records setup labels, per-asset entry reasons (funding_carry vs
basis_convergence), exits (convergence / carry_decay / negative_carry / divergence_stop
/ neutrality_break), turnover / rebalance labels, mechanical-neutrality validation
counts, forward-OOS 2026 counts, and structural counts. It runs NO replay, NO PnL,
applies NO fee (the 37 bps two-leg cost + funding/borrow/liquidation/basis execution are
RESERVED for replay), does NO optimization / tuning / rescue, touches NO XAUUSD, commits
NO data artifact, and does NOT start C21.

HONEST STRUCTURAL FINDING (preserved, not inflated): over the frozen windows the
detector produces 704 tradeable entries across BTC/ETH/SOL (well ABOVE the >= 100
structural sample-size gate), mechanical neutrality holds on 6614 / 6614 eval bars
(100% -- BY CONSTRUCTION, the whole point of C20 vs the estimated neutrality of C16/C19),
position mechanics are clean (gross capped at 1.0, one live position per asset, >= 5-bar
spacing), and forward-OOS 2026 has 35 entries. The structure is HEALTHY -- but this
LABELS stage does NOT establish a profitable edge: the carry is dominated by funding
(688 of 704 entries), and whether it survives the DOUBLED 37 bps two-leg cost plus
funding/borrow/liquidation and basis-convergence execution is decided ONLY at the
fee-honest replay gate. This is FROZEN for the human's advance-or-reject decision.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.mechanically_neutral_spot_perp_basis_funding_carry_v1_detector_spec_dry_run_contract as _d20  # noqa: E501

L20_SCHEMA_VERSION = 1
L20_MODE = "RESEARCH_ONLY"
L20_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = _d20.CANDIDATE_ID
CANDIDATE_FAMILY = _d20.CANDIDATE_FAMILY
CANDIDATE_NAME = _d20.CANDIDATE_NAME

VERDICT_C20L_FROZEN = "C20_LABELS_FROZEN_FOR_HUMAN_REVIEW"

# --- pinned artifact provenance (gitignored real-candle outputs) ------------
HEAD_AT_DETECTOR_DRY_RUN = "9b9cc18a7af4a914f067e59d3c5440960fb08cc8"
LABELS_PATH = ("data/mechanically_neutral_spot_perp_basis_funding_carry_c20/"
               "labels/c20_labels.json")
SUMMARY_PATH = ("data/mechanically_neutral_spot_perp_basis_funding_carry_c20/"
                "labels/c20_labels_summary.json")
EXPECTED_LABELS_SHA256 = (
    "e8282933ea1b07f14c7a09b72cc71632de2880d88e9105d3d0e91fe2702ca842")
EXPECTED_SUMMARY_SHA256 = (
    "f371b18a214eb5f1f52ffdccebda726bad6d11a0f3ca5796594d61fe424d48b5")
EXPECTED_SOURCE_SHA256 = {
    "BTCUSDT_spot": "0a214e5fae7f7b73b632193c23d633ab87114b7559e75111fa9ed7f1ef998f1a",
    "BTCUSDT_perp": "bfbaccb9056b2ea4c2136182333040bf9efca612f0440de902f79e5c31068a95",
    "BTCUSDT_funding": "7071f1484b3cd2e8d1ebe4abd1df93434f99646b1c9fd464a12251ac72d6869e",
    "ETHUSDT_spot": "45e6616e0753f7edf2c0e3aae03c9435e08a06999a6876c728a8b8237093554b",
    "ETHUSDT_perp": "e02bb1a874001932064ac00a31eafcdd41d7841702c2ac0d315c87a2b4cb5bed",
    "ETHUSDT_funding": "32804816434bcab09709086d7171c46136b2986affba5c19b7b0ef5b898531ed",
    "SOLUSDT_spot": "b1ac44dc763eb987b03265ca6d293b0ce2f29acdb6ab02eca1fbe744e55bb227",
    "SOLUSDT_perp": "a9810dfab32f210d18dd6a428f424a769eaf9c5449367adf795c95374c7c49a0",
    "SOLUSDT_funding": "520d28ebdd8142967bc1f9159a16934dc606621ad4c530315af6f2f608dcc759",
}
SOURCE_PATHS = {
    "BTCUSDT_spot": "data/crypto_basis_funding_research/raw/BTCUSDT_spot_1d.csv",
    "BTCUSDT_perp": "data/crypto_basis_funding_research/raw/BTCUSDT_perp_1d.csv",
    "BTCUSDT_funding": "data/crypto_basis_funding_research/raw/BTCUSDT_funding.csv",
    "ETHUSDT_spot": "data/crypto_basis_funding_research/raw/ETHUSDT_spot_1d.csv",
    "ETHUSDT_perp": "data/crypto_basis_funding_research/raw/ETHUSDT_perp_1d.csv",
    "ETHUSDT_funding": "data/crypto_basis_funding_research/raw/ETHUSDT_funding.csv",
    "SOLUSDT_spot": "data/crypto_basis_funding_research/raw/SOLUSDT_spot_1d.csv",
    "SOLUSDT_perp": "data/crypto_basis_funding_research/raw/SOLUSDT_perp_1d.csv",
    "SOLUSDT_funding": "data/crypto_basis_funding_research/raw/SOLUSDT_funding.csv",
}

# --- pinned frozen per-asset aggregates (from the real-candle labels run) ----
PER_ASSET = {
    "BTCUSDT": {
        "common_window": ("2020-01-02", "2026-06-08"), "n_eval_bars": 2290,
        "setup_count": 497, "entry_count": 243,
        "entry_reason_counts": {"funding_carry": 240, "basis_convergence": 3},
        "exit_counts": {"convergence": 224, "carry_decay": 4, "negative_carry": 3,
                        "divergence_stop": 11, "neutrality_break": 0,
                        "end_of_data": 1},
        "forward_oos_entry_count": 11,
        "mechanical_neutral_pass": 2290, "mechanical_neutral_fail": 0,
        "spacing_ok": True, "gross_cap_respected": True,
        "max_concurrent_positions": 1,
    },
    "ETHUSDT": {
        "common_window": ("2020-01-02", "2026-06-08"), "n_eval_bars": 2290,
        "setup_count": 518, "entry_count": 255,
        "entry_reason_counts": {"funding_carry": 253, "basis_convergence": 2},
        "exit_counts": {"convergence": 237, "carry_decay": 3, "negative_carry": 2,
                        "divergence_stop": 12, "neutrality_break": 0,
                        "end_of_data": 1},
        "forward_oos_entry_count": 12,
        "mechanical_neutral_pass": 2290, "mechanical_neutral_fail": 0,
        "spacing_ok": True, "gross_cap_respected": True,
        "max_concurrent_positions": 1,
    },
    "SOLUSDT": {
        "common_window": ("2020-09-14", "2026-06-08"), "n_eval_bars": 2034,
        "setup_count": 415, "entry_count": 206,
        "entry_reason_counts": {"funding_carry": 195, "basis_convergence": 11},
        "exit_counts": {"convergence": 179, "carry_decay": 5, "negative_carry": 15,
                        "divergence_stop": 7, "neutrality_break": 0,
                        "end_of_data": 0},
        "forward_oos_entry_count": 12,
        "mechanical_neutral_pass": 2034, "mechanical_neutral_fail": 0,
        "spacing_ok": True, "gross_cap_respected": True,
        "max_concurrent_positions": 1,
    },
}

# --- pinned frozen totals ---------------------------------------------------
TOTAL_EVAL_BARS = 6614
TOTAL_SETUP_COUNT = 1430
TOTAL_ENTRY_COUNT = 704
TOTAL_ENTRY_REASON_COUNTS = {"funding_carry": 688, "basis_convergence": 16}
TOTAL_EXIT_COUNTS = {"convergence": 640, "carry_decay": 12, "negative_carry": 20,
                     "divergence_stop": 30, "neutrality_break": 0, "end_of_data": 2}
TOTAL_MECHANICAL_NEUTRAL_PASS = 6614
TOTAL_MECHANICAL_NEUTRAL_FAIL = 0
TOTAL_FORWARD_OOS_ENTRY_COUNT = 35

# frozen gates / thresholds (reused, not redefined)
MIN_ENTRIES_STRUCTURAL = 100             # >= 100 structural sample-size gate
MAX_GROSS_CAP = _d20.MAX_GROSS           # 1.0
MIN_SPACING = _d20.MIN_SPACING           # 5
ALL_IN_ROUND_TRIP_BPS = _d20.ALL_IN_ROUND_TRIP_BPS   # 37.0 reserved (DOUBLED, two legs)

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "re_detects", "relabels", "runs_labels",
    "runs_replay", "runs_backtest", "computes_pnl", "applies_cost_model",
    "runs_baseline", "runs_optimization", "tunes_parameters", "runs_rescue",
    "runs_robustness", "fetches_data", "reads_real_data", "mutates_data",
    "stages_data", "commits_data_artifact", "auto_commits", "auto_pushes",
    "modifies_scheduler", "sends_notifications", "calls_api", "uses_network",
    "uses_credentials", "connects_broker", "connects_exchange", "uses_real_money",
    "places_orders", "contains_order_logic", "carries_net_market_beta",
    "uses_estimated_cross_asset_hedge", "uses_xauusd", "adds_new_instrument_class",
    "uses_leverage_above_cap", "allows_overlapping_positions", "paper_trading",
    "live_trading", "deploys_capital", "promotes_gate", "unlocks_downstream_gate",
    "skips_any_gate", "starts_c21", "advances_without_human_approval",
    "claims_profitability", "claims_edge", "crosses_into_forbidden_gate",
)


def _structural_verdict() -> dict[str, Any]:
    """Pure structural assessment of the frozen labels. Mechanics clean, ample sample,
    mechanical neutrality holds 100% by construction, forward-OOS coverage present --
    but the labels stage does NOT establish a profitable edge (that is the cost-honest
    replay gate's job)."""
    meets_sample_gate = TOTAL_ENTRY_COUNT >= MIN_ENTRIES_STRUCTURAL
    mechanical_neutrality_holds = TOTAL_MECHANICAL_NEUTRAL_FAIL == 0
    gross_cap_respected = all(a["gross_cap_respected"] for a in PER_ASSET.values())
    non_overlap_ok = all(a["max_concurrent_positions"] <= 1
                         for a in PER_ASSET.values())
    spacing_ok = all(a["spacing_ok"] for a in PER_ASSET.values())
    has_forward_oos_coverage = TOTAL_FORWARD_OOS_ENTRY_COUNT > 0
    exits_total = sum(TOTAL_EXIT_COUNTS.values())
    exits_reconcile = exits_total == TOTAL_ENTRY_COUNT
    reasons_reconcile = (sum(TOTAL_ENTRY_REASON_COUNTS.values())
                         == TOTAL_ENTRY_COUNT)
    mechanics_clean = (gross_cap_respected and non_overlap_ok and spacing_ok
                       and mechanical_neutrality_holds)
    structurally_healthy = (meets_sample_gate and mechanical_neutrality_holds
                            and mechanics_clean and has_forward_oos_coverage
                            and exits_reconcile and reasons_reconcile)
    return {
        "total_eval_bars": TOTAL_EVAL_BARS,
        "total_setup_count": TOTAL_SETUP_COUNT,
        "total_entry_count": TOTAL_ENTRY_COUNT,
        "min_entries_structural_gate": MIN_ENTRIES_STRUCTURAL,
        "meets_min_sample_gate": meets_sample_gate,
        "total_entry_reason_counts": dict(TOTAL_ENTRY_REASON_COUNTS),
        "total_exit_counts": dict(TOTAL_EXIT_COUNTS),
        "exits_reconcile_with_entries": exits_reconcile,
        "entry_reasons_reconcile_with_entries": reasons_reconcile,
        "total_mechanical_neutral_pass": TOTAL_MECHANICAL_NEUTRAL_PASS,
        "total_mechanical_neutral_fail": TOTAL_MECHANICAL_NEUTRAL_FAIL,
        "mechanical_neutrality_holds": mechanical_neutrality_holds,
        "mechanical_neutrality_pass_rate": round(
            TOTAL_MECHANICAL_NEUTRAL_PASS / TOTAL_EVAL_BARS, 4),
        "gross_cap_respected": gross_cap_respected,
        "non_overlap_ok": non_overlap_ok,
        "spacing_ok": spacing_ok,
        "forward_oos_entry_count": TOTAL_FORWARD_OOS_ENTRY_COUNT,
        "has_forward_oos_coverage": has_forward_oos_coverage,
        "mechanics_clean": mechanics_clean,
        "structurally_healthy": structurally_healthy,
        # honest caveat: the labels stage NEVER establishes profitability
        "profitability_established": False,
        "edge_established": False,
        "decisive_gate_is_fee_honest_replay": True,
        "carry_dominated_by_funding": (
            TOTAL_ENTRY_REASON_COUNTS["funding_carry"]
            > TOTAL_ENTRY_REASON_COUNTS["basis_convergence"]),
        "replay_must_apply_doubled_two_leg_cost_plus_perp_frictions": True,
    }


def get_candidate_20_labels_review_label() -> str:
    return (
        "Candidate #20 mechanically_neutral_spot_perp_basis_funding_carry_v1 "
        "real-candle labels review (READ-ONLY, RESEARCH ONLY). FROZEN labels from the "
        "PUBLIC BTC/ETH/SOL spot+perp+funding D1 dataset (no fetch, 9 source SHAs "
        "verified). STRUCTURALLY HEALTHY: 704 entries across 3 assets (>= 100 gate), "
        "mechanical neutrality holds 6614/6614 bars (100%, by construction -- the C20 "
        "answer to C16/C19 estimated-neutrality failure), gross capped 1.0, one live "
        "position per asset, >= 5-bar spacing, 35 forward-OOS 2026 entries. BUT this "
        "LABELS stage does NOT establish a profitable edge: carry is funding-dominated "
        "(688/704) and survival of the DOUBLED 37 bps two-leg cost + funding/borrow/"
        "liquidation + basis execution is decided ONLY at fee-honest replay. No replay, "
        "no PnL, no fee here. Frozen for the human advance-or-reject decision. NOT a "
        "profitability claim.")


def get_candidate_20_labels_review_next_action() -> str:
    return "HUMAN_DECISION_C20_ADVANCE_TO_FEE_HONEST_REPLAY_OR_REJECT"


def build_c20_labels_review(repo_root: Any = ".",
                            tracked_paths: list | None = None) -> dict[str, Any]:
    """Assemble the frozen C20 real-candle labels review record. Pure; no I/O;
    chain-gated on the frozen C20 detector dry-run (and thus spec / proposal)."""
    detector = _d20.build_c20_detector_dry_run(repo_root, tracked_paths)
    detector_valid = _d20.validate_c20_detector_dry_run(detector)["valid"]
    detector_verdict = detector.get("verdict")

    blockers: list = []
    if not detector_valid:
        blockers.append("c20_detector_dry_run_invalid")
    if detector_verdict != "C20_DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW":
        blockers.append("c20_detector_dry_run_not_frozen")

    sv = _structural_verdict()

    record: dict[str, Any] = {
        "schema_version": L20_SCHEMA_VERSION, "mode": L20_MODE, "lane": L20_LANE,
        "label": get_candidate_20_labels_review_label(),
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "candidate_name": CANDIDATE_NAME,
        "is_labels_review_only": True,
        "blockers": blockers,
        "verdict": (VERDICT_C20L_FROZEN if not blockers
                    else "C20_LABELS_BLOCKED"),
        # chain provenance
        "detector_dry_run_verdict": detector_verdict,
        "detector_dry_run_valid": detector_valid,
        "head_at_detector_dry_run": HEAD_AT_DETECTOR_DRY_RUN,
        # frozen source data provenance (public, no fetch, 9 SHAs verified)
        "uses_frozen_public_data_only": True,
        "no_new_data_fetch": True,
        "uses_xauusd": False,
        "source_paths": dict(SOURCE_PATHS),
        "expected_source_sha256": dict(EXPECTED_SOURCE_SHA256),
        "universe": ["BTCUSDT", "ETHUSDT", "SOLUSDT"],
        # gitignored labels artifacts (SHA-pinned, NOT committed)
        "labels_path": LABELS_PATH, "summary_path": SUMMARY_PATH,
        "expected_labels_sha256": EXPECTED_LABELS_SHA256,
        "expected_summary_sha256": EXPECTED_SUMMARY_SHA256,
        "artifacts_gitignored_not_committed": True,
        # frozen detector params honoured exactly
        "basis_zscore_window_bars": _d20.BASIS_Z_WINDOW,
        "funding_lookback_bars": _d20.FUNDING_LOOKBACK,
        "entry_basis_zscore_threshold": _d20.ENTRY_BASIS_Z,
        "entry_min_annualized_carry_bps": _d20.ENTRY_CARRY_BPS,
        "exit_basis_zscore_threshold": _d20.EXIT_BASIS_Z,
        "stop_basis_zscore_threshold": _d20.STOP_BASIS_Z,
        "max_gross_exposure": MAX_GROSS_CAP,
        "min_bars_between_rebalances": MIN_SPACING,
        "basis_formula": "(perp_close - spot_close) / spot_close",
        "is_market_neutral": True, "is_mechanically_neutral_same_asset": True,
        "is_estimated_cross_asset_neutral": False,
        "return_source_is_carry_not_timing": True,
        "mechanical_neutrality_is_gate_zero": True,
        # per-asset + total frozen aggregates
        "per_asset": {s: {k: (list(v) if isinstance(v, tuple) else v)
                          for k, v in a.items()}
                      for s, a in PER_ASSET.items()},
        "total_eval_bars": TOTAL_EVAL_BARS,
        "total_setup_count": TOTAL_SETUP_COUNT,
        "total_entry_count": TOTAL_ENTRY_COUNT,
        "total_entry_reason_counts": dict(TOTAL_ENTRY_REASON_COUNTS),
        "total_exit_counts": dict(TOTAL_EXIT_COUNTS),
        "total_mechanical_neutral_pass": TOTAL_MECHANICAL_NEUTRAL_PASS,
        "total_mechanical_neutral_fail": TOTAL_MECHANICAL_NEUTRAL_FAIL,
        "total_forward_oos_entry_count": TOTAL_FORWARD_OOS_ENTRY_COUNT,
        # the structural verdict (healthy; profitability NOT established here)
        "structural_verdict": sv,
        "structural_mechanics_clean": sv["mechanics_clean"],
        "structurally_healthy": sv["structurally_healthy"],
        "meets_min_sample_gate": sv["meets_min_sample_gate"],
        "mechanical_neutrality_holds": sv["mechanical_neutrality_holds"],
        "profitability_established": False,
        # cost reserved, not applied
        "cost_model_reserved_for_replay": True,
        "cost_model_applied_here": False,
        "fee_applied": False,
        "all_in_round_trip_bps_reserved": ALL_IN_ROUND_TRIP_BPS,
        "perp_frictions_reserved_for_replay": True,
        "does_not_start_c21": True, "c21_candidate_id": None,
        "human_review_required": True,
        "current_loop_stage": "real_candle_labels_review",
        "next_required_action": get_candidate_20_labels_review_next_action(),
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
        "no_estimated_cross_asset_hedge": True, "no_net_market_beta": True,
        "no_leverage_above_cap": True, "no_overlapping_positions": True,
        "no_stage": True, "no_commit": True, "no_push": True, "no_auto_commit": True,
        "no_auto_push": True, "no_scheduler_change": True, "no_broker": True,
        "no_credentials": True, "no_order_logic": True, "no_paper_trading": True,
        "no_live_trading": True, "no_gate_skip": True, "no_start_c21": True,
        "no_downstream_gate_unlock": True, "no_profitability_claim": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_c20_labels_review(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the unit is research-only,
    labels-review-only, chain-gated on the frozen C20 detector dry-run, uses ONLY the
    frozen PUBLIC BTC/ETH/SOL spot+perp+funding data (no fetch; 9 SHA-pinned sources +
    gitignored artifacts not committed), honours the exact same-asset basis/funding
    params, pins the frozen per-asset + total aggregates and a structural verdict
    (mechanics clean, ample sample, mechanical neutrality holds 100%, forward-OOS
    coverage) that explicitly does NOT claim profitability or edge (reserved for
    replay), reserves the 37 bps (no fee applied), keeps downstream gates locked, does
    not start C21, and pins every capability flag False."""
    failures: list = []
    if record.get("mode") != L20_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_labels_review_only") is not True:
        failures.append("not_labels_review_only")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("verdict") != VERDICT_C20L_FROZEN:
        failures.append("verdict_not_frozen")

    # chain gate on the frozen detector dry-run
    if record.get("detector_dry_run_valid") is not True:
        failures.append("detector_not_valid")
    if record.get("detector_dry_run_verdict") != (
            "C20_DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW"):
        failures.append("detector_not_frozen")
    if record.get("candidate_id") != "C20":
        failures.append("candidate_id_not_c20")

    # frozen public data provenance, no fetch, 9 SHAs pinned
    if record.get("uses_frozen_public_data_only") is not True:
        failures.append("not_frozen_public_only")
    if record.get("no_new_data_fetch") is not True:
        failures.append("must_not_fetch")
    if record.get("uses_xauusd") is not False:
        failures.append("must_not_use_xauusd")
    if record.get("expected_source_sha256") != EXPECTED_SOURCE_SHA256:
        failures.append("source_sha_tampered")
    if len(record.get("expected_source_sha256") or {}) != 9:
        failures.append("source_sha_count_not_9")

    # gitignored artifacts SHA-pinned and NOT committed
    if record.get("expected_labels_sha256") != EXPECTED_LABELS_SHA256:
        failures.append("labels_sha_tampered")
    if record.get("expected_summary_sha256") != EXPECTED_SUMMARY_SHA256:
        failures.append("summary_sha_tampered")
    if record.get("artifacts_gitignored_not_committed") is not True:
        failures.append("artifacts_must_not_be_committed")
    if not str(record.get("labels_path", "")).startswith("data/"):
        failures.append("labels_path_not_under_data")

    # exact params + mechanical (not estimated) identity
    if record.get("basis_zscore_window_bars") != 60:
        failures.append("basis_z_window_not_60")
    if record.get("funding_lookback_bars") != 30:
        failures.append("funding_lookback_not_30")
    if record.get("entry_basis_zscore_threshold") != 2.0:
        failures.append("entry_basis_z_not_2")
    if record.get("entry_min_annualized_carry_bps") != 50.0:
        failures.append("entry_carry_not_50")
    if record.get("max_gross_exposure") != 1.0:
        failures.append("gross_cap_not_1")
    if record.get("basis_formula") != "(perp_close - spot_close) / spot_close":
        failures.append("basis_formula_tampered")
    if record.get("is_mechanically_neutral_same_asset") is not True:
        failures.append("must_be_mechanically_neutral_same_asset")
    if record.get("is_estimated_cross_asset_neutral") is not False:
        failures.append("must_not_be_estimated_cross_asset_neutral")
    if record.get("mechanical_neutrality_is_gate_zero") is not True:
        failures.append("neutrality_not_gate_zero")

    # per-asset + total aggregates pinned exactly (anti-tamper)
    pa = record.get("per_asset") or {}
    if set(pa) != {"BTCUSDT", "ETHUSDT", "SOLUSDT"}:
        failures.append("per_asset_universe_tampered")
    if sum((pa.get(s, {}).get("entry_count", 0)) for s in pa) != TOTAL_ENTRY_COUNT:
        failures.append("per_asset_entries_do_not_sum_to_total")
    if record.get("total_entry_count") != TOTAL_ENTRY_COUNT:
        failures.append("total_entry_count_tampered")
    if record.get("total_entry_reason_counts") != TOTAL_ENTRY_REASON_COUNTS:
        failures.append("entry_reason_counts_tampered")
    if record.get("total_exit_counts") != TOTAL_EXIT_COUNTS:
        failures.append("exit_counts_tampered")
    if record.get("total_mechanical_neutral_fail") != 0:
        failures.append("mechanical_neutral_fail_tampered")
    if record.get("total_forward_oos_entry_count") != TOTAL_FORWARD_OOS_ENTRY_COUNT:
        failures.append("forward_oos_count_tampered")

    # structural verdict: healthy, reconciles, but NOT a profitability claim
    sv = record.get("structural_verdict") or {}
    if sv.get("total_entry_count") != TOTAL_ENTRY_COUNT:
        failures.append("sv_entry_count_tampered")
    if sv.get("meets_min_sample_gate") is not True:        # 704 >= 100
        failures.append("sample_gate_should_pass")
    if sv.get("mechanical_neutrality_holds") is not True:  # 0 fails (by construction)
        failures.append("mechanical_neutrality_should_hold")
    if sv.get("exits_reconcile_with_entries") is not True:
        failures.append("exits_do_not_reconcile")
    if sv.get("entry_reasons_reconcile_with_entries") is not True:
        failures.append("entry_reasons_do_not_reconcile")
    if sv.get("mechanics_clean") is not True:
        failures.append("mechanics_should_be_clean")
    if sv.get("structurally_healthy") is not True:
        failures.append("should_be_structurally_healthy")
    # the labels stage NEVER claims profitability / edge
    if sv.get("profitability_established") is not False:
        failures.append("must_not_claim_profitability")
    if sv.get("edge_established") is not False:
        failures.append("must_not_claim_edge")
    if sv.get("decisive_gate_is_fee_honest_replay") is not True:
        failures.append("replay_must_be_decisive_gate")
    if record.get("profitability_established") is not False:
        failures.append("top_level_profitability_claimed")

    # cost reserved, not applied
    if record.get("cost_model_applied_here") is not False:
        failures.append("cost_applied_in_labels")
    if record.get("fee_applied") is not False:
        failures.append("fee_applied_in_labels")
    if record.get("all_in_round_trip_bps_reserved") != 37.0:
        failures.append("cost_reserve_tampered")
    if record.get("perp_frictions_reserved_for_replay") is not True:
        failures.append("perp_frictions_not_reserved")

    # no C21 + next action + downstream locks
    if record.get("does_not_start_c21") is not True:
        failures.append("must_not_start_c21")
    if record.get("c21_candidate_id") is not None:
        failures.append("c21_must_be_none")
    if record.get("next_required_action") != (
            "HUMAN_DECISION_C20_ADVANCE_TO_FEE_HONEST_REPLAY_OR_REJECT"):
        failures.append("next_action_not_replay_gate")
    for gate in ("replay_gate_locked", "paper_trading_gate_locked",
                 "live_gate_locked"):
        if record.get(gate) is not True:
            failures.append("downstream_gate_unlocked_%s" % gate)

    locks = record.get("scope_locks") or {}
    for key in ("no_re_detect", "no_relabel", "no_replay", "no_pnl",
                "no_cost_application", "no_optimization", "no_tuning", "no_rescue",
                "no_data_fetch", "no_data_commit", "no_xauusd",
                "no_estimated_cross_asset_hedge", "no_overlapping_positions",
                "no_commit", "no_push", "no_paper_trading", "no_live_trading",
                "no_start_c21", "no_gate_skip"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
