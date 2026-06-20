"""Candidate #21 -- low_turnover_same_asset_spot_perp_funding_carry_v1
-- REAL-CANDLE LABELS REVIEW (PURE, RESEARCH ONLY).

Records and validates the frozen real-candle LABELS for Candidate #21, produced by
`tools/c21_real_candle_labels_once.py` from the frozen PUBLIC BTC/ETH/SOL spot+perp+funding
D1 dataset (no fetch) by applying the FROZEN C21 detector rules EXACTLY (reused from the
committed detector -- not re-parameterized). It pins the 9 source-data SHA provenance
hashes, the gitignored labels/summary artifact paths + SHAs, the frozen per-asset + total
label aggregates (detected setups = accepted entries + rejected/blocked signals, hold
lengths, exit-reason counts, mechanical-neutrality counts, turnover, forward-OOS 2026
counts), and a STRUCTURAL verdict. Chain-gated on the committed C21 detector / spec /
proposal.

LABELS STAGE ONLY: it records label counts and turnover/mechanical-neutrality evidence.
It runs NO replay, NO PnL, applies NO fee (37/74 bps RESERVED for replay), does NO
optimization / tuning / rescue / parameter change, touches NO XAUUSD, commits NO data
artifact, does NOT rescue/retune C20 (C20 stays rejected), and does NOT start C22. It
makes NO fee-honest performance or profitability claim -- that is the (still-LOCKED)
replay gate's job.

STRUCTURAL FINDING (preserved, not a performance claim): the FROZEN low-turnover detector
applied to real candles is GENUINELY LOW TURNOVER -- across BTC/ETH/SOL it accepted only
20 entries (vs 113 candidate signals rejected by the rebalance cadence), with round-trips
of 0.79 / 0.94 / 1.59 per year (all far under the 6/yr ceiling) and LONG average holds
(172-421 bars). Mechanical neutrality holds on 6704/6704 eval bars (100%, by
construction). This is the structural OPPOSITE of C20's high-turnover 704 trades -- the
DESIGN INTENT. Whether this low-turnover carry actually WINS net of the doubled 74 bps
two-leg cost + funding/borrow/liquidation is decided ONLY at the fee-honest replay gate.
This is FROZEN for the human's advance-or-reject decision.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.low_turnover_same_asset_spot_perp_funding_carry_v1_detector_spec_dry_run_contract as _d21  # noqa: E501

L21_SCHEMA_VERSION = 1
L21_MODE = "RESEARCH_ONLY"
L21_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = _d21.CANDIDATE_ID
CANDIDATE_FAMILY = _d21.CANDIDATE_FAMILY
CANDIDATE_NAME = _d21.CANDIDATE_NAME

VERDICT_C21L_FROZEN = "C21_LABELS_FROZEN_FOR_HUMAN_REVIEW"

# --- pinned artifact provenance (gitignored real-candle outputs) ------------
HEAD_AT_DETECTOR_DRY_RUN = "ff4649ce8a14acf171f156ae11ddc57500ebad0f"
LABELS_PATH = ("data/low_turnover_same_asset_spot_perp_funding_carry_c21/"
               "labels/c21_labels.json")
SUMMARY_PATH = ("data/low_turnover_same_asset_spot_perp_funding_carry_c21/"
                "labels/c21_labels_summary.json")
EXPECTED_LABELS_SHA256 = (
    "98e8665b239a6d7d32a30a34bc88b699a137fff23371567cc444369ccaa6cbad")
EXPECTED_SUMMARY_SHA256 = (
    "37ba8cc8e9e20c18dc2e8336cf87eb73d76f16948b78056d0f324bf70424777c")
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
    "%s_%s" % (s, kind): "data/crypto_basis_funding_research/raw/%s_%s.csv" % (
        s, {"spot": "spot_1d", "perp": "perp_1d", "funding": "funding"}[kind])
    for s in ("BTCUSDT", "ETHUSDT", "SOLUSDT") for kind in ("spot", "perp", "funding")
}

# --- pinned frozen per-asset aggregates (from the real-candle labels run) ----
PER_ASSET = {
    "BTCUSDT": {
        "common_window": ("2020-01-02", "2026-06-08"), "n_eval_bars": 2320,
        "detected_setup_count": 78, "accepted_label_count": 6,
        "rejected_label_count": 72, "rejected_by_cadence": 72,
        "rejected_by_turnover_ceiling": 0, "round_trips": 6,
        "round_trips_per_year": 0.944, "avg_hold_bars": 357.6667,
        "exit_counts": {"durable_carry_regime_breakdown": 5, "end_of_data": 1},
        "forward_oos_accepted_count": 1,
        "mechanical_neutral_pass": 2320, "mechanical_neutral_fail": 0,
        "gross_cap_respected": True, "max_concurrent_positions": 1,
    },
    "ETHUSDT": {
        "common_window": ("2020-01-02", "2026-06-08"), "n_eval_bars": 2320,
        "detected_setup_count": 41, "accepted_label_count": 5,
        "rejected_label_count": 36, "rejected_by_cadence": 36,
        "rejected_by_turnover_ceiling": 0, "round_trips": 5,
        "round_trips_per_year": 0.7866, "avg_hold_bars": 421.4,
        "exit_counts": {"durable_carry_regime_breakdown": 4, "end_of_data": 1},
        "forward_oos_accepted_count": 1,
        "mechanical_neutral_pass": 2320, "mechanical_neutral_fail": 0,
        "gross_cap_respected": True, "max_concurrent_positions": 1,
    },
    "SOLUSDT": {
        "common_window": ("2020-09-14", "2026-06-08"), "n_eval_bars": 2064,
        "detected_setup_count": 14, "accepted_label_count": 9,
        "rejected_label_count": 5, "rejected_by_cadence": 5,
        "rejected_by_turnover_ceiling": 0, "round_trips": 9,
        "round_trips_per_year": 1.5916, "avg_hold_bars": 172.2222,
        "exit_counts": {"durable_carry_regime_breakdown": 8, "end_of_data": 1},
        "forward_oos_accepted_count": 1,
        "mechanical_neutral_pass": 2064, "mechanical_neutral_fail": 0,
        "gross_cap_respected": True, "max_concurrent_positions": 1,
    },
}

# --- pinned frozen totals ---------------------------------------------------
TOTAL_EVAL_BARS = 6704
TOTAL_DETECTED_SETUP_COUNT = 133
TOTAL_ACCEPTED_LABEL_COUNT = 20
TOTAL_REJECTED_LABEL_COUNT = 113
TOTAL_EXIT_COUNTS = {"durable_carry_regime_breakdown": 17, "end_of_data": 3}
TOTAL_ROUND_TRIPS = 20
TOTAL_MECHANICAL_NEUTRAL_PASS = 6704
TOTAL_MECHANICAL_NEUTRAL_FAIL = 0
TOTAL_FORWARD_OOS_ACCEPTED_COUNT = 3

# frozen gates / thresholds (reused, not redefined)
MAX_GROSS_CAP = _d21.MAX_GROSS                          # 1.0
MAX_ROUND_TRIPS_PER_YEAR = _d21.MAX_ROUND_TRIPS_PER_YEAR  # 6
ALL_IN_ROUND_TRIP_BPS = _d21.ALL_IN_ROUND_TRIP_BPS     # 37.0 reserved
ROUND_TRIP_COST_PER_TRADE_BPS = _d21.ROUND_TRIP_COST_PER_TRADE_BPS   # 74.0 reserved

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "re_detects", "relabels", "runs_labels",
    "runs_replay", "runs_backtest", "computes_pnl", "applies_cost_model",
    "runs_baseline", "runs_optimization", "tunes_parameters", "runs_rescue",
    "rescues_c20", "retunes_c20", "runs_robustness", "fetches_data",
    "reads_real_data", "mutates_data", "stages_data", "commits_data_artifact",
    "auto_commits", "auto_pushes", "modifies_scheduler", "sends_notifications",
    "calls_api", "uses_network", "uses_credentials", "connects_broker",
    "connects_exchange", "uses_real_money", "places_orders", "contains_order_logic",
    "carries_net_market_beta", "uses_estimated_cross_asset_hedge", "is_high_turnover",
    "uses_basis_z_stop", "uses_drawdown_stop", "uses_xauusd",
    "adds_new_instrument_class", "uses_leverage_above_cap", "allows_overlapping_positions",
    "paper_trading", "live_trading", "deploys_capital", "promotes_gate",
    "unlocks_downstream_gate", "skips_any_gate", "starts_c22",
    "advances_without_human_approval", "claims_profitability", "claims_edge",
    "claims_fee_honest_performance", "crosses_into_forbidden_gate",
)


def _structural_verdict() -> dict[str, Any]:
    """Pure structural assessment of the frozen labels. Genuinely LOW turnover, long
    holds, mechanical neutrality 100% -- the design opposite of C20 -- but the labels
    stage makes NO fee-honest performance / profitability claim (that is the replay
    gate's job, which remains LOCKED)."""
    low_turnover = all(a["round_trips_per_year"] <= MAX_ROUND_TRIPS_PER_YEAR + 1e-9
                       for a in PER_ASSET.values())
    mechanical_neutrality_holds = TOTAL_MECHANICAL_NEUTRAL_FAIL == 0
    gross_cap_respected = all(a["gross_cap_respected"] for a in PER_ASSET.values())
    non_overlap_ok = all(a["max_concurrent_positions"] <= 1
                         for a in PER_ASSET.values())
    labels_reconcile = (TOTAL_ACCEPTED_LABEL_COUNT + TOTAL_REJECTED_LABEL_COUNT
                        == TOTAL_DETECTED_SETUP_COUNT)
    exits_reconcile = sum(TOTAL_EXIT_COUNTS.values()) == TOTAL_ACCEPTED_LABEL_COUNT
    has_forward_oos = TOTAL_FORWARD_OOS_ACCEPTED_COUNT > 0
    much_fewer_than_c20 = TOTAL_ACCEPTED_LABEL_COUNT < 704   # C20 had 704 entries
    mechanics_clean = (low_turnover and mechanical_neutrality_holds
                       and gross_cap_respected and non_overlap_ok)
    return {
        "total_eval_bars": TOTAL_EVAL_BARS,
        "total_detected_setup_count": TOTAL_DETECTED_SETUP_COUNT,
        "total_accepted_label_count": TOTAL_ACCEPTED_LABEL_COUNT,
        "total_rejected_label_count": TOTAL_REJECTED_LABEL_COUNT,
        "labels_reconcile": labels_reconcile,
        "exits_reconcile_with_accepted": exits_reconcile,
        "total_round_trips": TOTAL_ROUND_TRIPS,
        "is_genuinely_low_turnover": low_turnover,
        "round_trips_under_ceiling": low_turnover,
        "fewer_trades_than_c20_high_turnover": much_fewer_than_c20,
        "total_mechanical_neutral_pass": TOTAL_MECHANICAL_NEUTRAL_PASS,
        "mechanical_neutrality_holds": mechanical_neutrality_holds,
        "gross_cap_respected": gross_cap_respected,
        "non_overlap_ok": non_overlap_ok,
        "forward_oos_accepted_count": TOTAL_FORWARD_OOS_ACCEPTED_COUNT,
        "has_forward_oos_coverage": has_forward_oos,
        "uses_basis_z_stop": False, "uses_drawdown_stop": False,
        "mechanics_clean": mechanics_clean,
        # the labels stage makes NO performance / profitability claim
        "profitability_established": False,
        "edge_established": False,
        "fee_honest_performance_claimed": False,
        "decisive_gate_is_fee_honest_replay": True,
        "replay_remains_locked": True,
        "is_rescue_or_retune_of_c20": False,
        "c20_remains_rejected": True,
    }


def get_candidate_21_labels_review_label() -> str:
    return (
        "Candidate #21 low_turnover_same_asset_spot_perp_funding_carry_v1 real-candle "
        "labels review (READ-ONLY, RESEARCH ONLY). FROZEN labels from the PUBLIC "
        "BTC/ETH/SOL spot+perp+funding D1 dataset (no fetch, 9 source SHAs verified), "
        "applying the FROZEN C21 detector EXACTLY (no re-parameterization). GENUINELY "
        "LOW TURNOVER: only 20 accepted entries (113 candidate signals rejected by the "
        "rebalance cadence), round-trips 0.79-1.59/yr (all under the 6/yr ceiling), long "
        "holds (172-421 bars), mechanical neutrality 6704/6704 bars (100%) -- the design "
        "opposite of C20's 704-trade churn. LABELS STAGE ONLY: no replay, no PnL, no fee "
        "(37/74 bps reserved), no optimization; makes NO fee-honest performance or "
        "profitability claim -- the replay gate (still LOCKED) decides. NOT a "
        "rescue/retune of C20 (C20 stays rejected). Frozen for the human "
        "advance-or-reject decision. NOT a profitability claim.")


def get_candidate_21_labels_review_next_action() -> str:
    return "HUMAN_DECISION_C21_ADVANCE_TO_FEE_HONEST_REPLAY_OR_REJECT"


def build_c21_labels_review(repo_root: Any = ".",
                            tracked_paths: list | None = None) -> dict[str, Any]:
    """Assemble the frozen C21 real-candle labels review record. Pure; no I/O;
    chain-gated on the frozen C21 detector dry-run (and thus spec / proposal)."""
    detector = _d21.build_c21_detector_dry_run(repo_root, tracked_paths)
    detector_valid = _d21.validate_c21_detector_dry_run(detector)["valid"]
    detector_verdict = detector.get("verdict")

    blockers: list = []
    if not detector_valid:
        blockers.append("c21_detector_dry_run_invalid")
    if detector_verdict != "C21_DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW":
        blockers.append("c21_detector_dry_run_not_frozen")

    sv = _structural_verdict()

    record: dict[str, Any] = {
        "schema_version": L21_SCHEMA_VERSION, "mode": L21_MODE, "lane": L21_LANE,
        "label": get_candidate_21_labels_review_label(),
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "candidate_name": CANDIDATE_NAME,
        "is_labels_review_only": True,
        "blockers": blockers,
        "verdict": (VERDICT_C21L_FROZEN if not blockers else "C21_LABELS_BLOCKED"),
        # chain provenance
        "detector_dry_run_verdict": detector_verdict,
        "detector_dry_run_valid": detector_valid,
        "head_at_detector_dry_run": HEAD_AT_DETECTOR_DRY_RUN,
        # frozen source data provenance (public, no fetch, 9 SHAs verified)
        "uses_frozen_public_data_only": True, "no_new_data_fetch": True,
        "uses_xauusd": False,
        "source_paths": dict(SOURCE_PATHS),
        "expected_source_sha256": dict(EXPECTED_SOURCE_SHA256),
        "universe": ["BTCUSDT", "ETHUSDT", "SOLUSDT"],
        # gitignored labels artifacts (SHA-pinned, NOT committed)
        "labels_path": LABELS_PATH, "summary_path": SUMMARY_PATH,
        "expected_labels_sha256": EXPECTED_LABELS_SHA256,
        "expected_summary_sha256": EXPECTED_SUMMARY_SHA256,
        "artifacts_gitignored_not_committed": True,
        # frozen detector rules reused exactly (no re-parameterization)
        "rules_frozen_reused_from_committed_detector": True,
        "no_parameter_optimization": True, "no_parameter_tuning": True,
        "carry_regime_window_bars": _d21.CARRY_REGIME_WINDOW,
        "annualized_carry_enter_bps": _d21.ENTER_CARRY_BPS,
        "carry_regime_breakdown_bars": _d21.BREAKDOWN_BARS,
        "min_hold_bars": _d21.MIN_HOLD_BARS,
        "rebalance_cadence_bars": _d21.REBALANCE_CADENCE,
        "max_round_trips_per_year_per_asset": MAX_ROUND_TRIPS_PER_YEAR,
        "max_gross_exposure": MAX_GROSS_CAP,
        "is_market_neutral": True, "is_mechanically_neutral_same_asset": True,
        "is_low_turnover": True, "is_high_turnover": False,
        "uses_basis_z_stop": False, "uses_drawdown_stop": False,
        "return_source_is_carry_not_timing": True,
        # NOT a rescue/retune of C20
        "is_rescue_or_retune_of_c20": False, "c20_remains_rejected": True,
        # per-asset + total frozen aggregates
        "per_asset": {s: {k: (list(v) if isinstance(v, tuple) else v)
                          for k, v in a.items()}
                      for s, a in PER_ASSET.items()},
        "total_eval_bars": TOTAL_EVAL_BARS,
        "total_detected_setup_count": TOTAL_DETECTED_SETUP_COUNT,
        "total_accepted_label_count": TOTAL_ACCEPTED_LABEL_COUNT,
        "total_rejected_label_count": TOTAL_REJECTED_LABEL_COUNT,
        "total_exit_counts": dict(TOTAL_EXIT_COUNTS),
        "total_round_trips": TOTAL_ROUND_TRIPS,
        "total_mechanical_neutral_pass": TOTAL_MECHANICAL_NEUTRAL_PASS,
        "total_mechanical_neutral_fail": TOTAL_MECHANICAL_NEUTRAL_FAIL,
        "total_forward_oos_accepted_count": TOTAL_FORWARD_OOS_ACCEPTED_COUNT,
        # the structural verdict (low turnover; NO performance/profitability claim)
        "structural_verdict": sv,
        "structural_mechanics_clean": sv["mechanics_clean"],
        "is_genuinely_low_turnover": sv["is_genuinely_low_turnover"],
        "mechanical_neutrality_holds": sv["mechanical_neutrality_holds"],
        "profitability_established": False,
        "fee_honest_performance_claimed": False,
        # cost reserved, not applied; replay LOCKED
        "cost_model_reserved_for_replay": True,
        "cost_model_applied_here": False,
        "fee_applied": False,
        "all_in_round_trip_bps_reserved": ALL_IN_ROUND_TRIP_BPS,
        "round_trip_cost_per_trade_bps_reserved": ROUND_TRIP_COST_PER_TRADE_BPS,
        "replay_remains_locked": True,
        "does_not_start_c22": True, "c22_candidate_id": None,
        "human_review_required": True,
        "current_loop_stage": "real_candle_labels_review",
        "next_required_action": get_candidate_21_labels_review_next_action(),
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
        "no_tuning": True, "no_rescue": True, "no_rescue_c20": True,
        "no_robustness": True, "no_data_fetch": True,
        "no_real_data_access_beyond_frozen": True, "no_data_commit": True,
        "no_xauusd": True, "no_new_instrument_class": True,
        "no_estimated_cross_asset_hedge": True, "no_net_market_beta": True,
        "no_high_turnover": True, "no_basis_z_stop": True, "no_drawdown_stop": True,
        "no_leverage_above_cap": True, "no_overlapping_positions": True,
        "no_fee_honest_performance_claim": True, "no_stage": True, "no_commit": True,
        "no_push": True, "no_auto_commit": True, "no_auto_push": True,
        "no_scheduler_change": True, "no_broker": True, "no_credentials": True,
        "no_order_logic": True, "no_paper_trading": True, "no_live_trading": True,
        "no_gate_skip": True, "no_start_c22": True, "no_downstream_gate_unlock": True,
        "no_profitability_claim": True, "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_c21_labels_review(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the unit is research-only,
    labels-review-only, chain-gated on the frozen C21 detector dry-run, uses ONLY the
    frozen public data + frozen labels (no fetch; 9 SHA-pinned sources + gitignored
    artifacts not committed), applies the FROZEN detector rules with NO re-parameter-
    ization, pins the frozen per-asset + total aggregates and a structural verdict
    (genuinely low turnover, mechanical neutrality 100%, NO performance/profitability/
    fee-honest claim -- replay still LOCKED), reserves the 37/74 bps (no fee applied),
    is NOT a rescue/retune of C20 (C20 stays rejected), keeps downstream gates locked,
    does not start C22, and pins every capability flag False."""
    failures: list = []
    if record.get("mode") != L21_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_labels_review_only") is not True:
        failures.append("not_labels_review_only")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("verdict") != VERDICT_C21L_FROZEN:
        failures.append("verdict_not_frozen")

    # chain gate on the frozen detector dry-run
    if record.get("detector_dry_run_valid") is not True:
        failures.append("detector_not_valid")
    if record.get("detector_dry_run_verdict") != (
            "C21_DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW"):
        failures.append("detector_not_frozen")
    if record.get("candidate_id") != "C21":
        failures.append("candidate_id_not_c21")

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

    # frozen detector rules reused exactly (NO re-parameterization / optimization)
    if record.get("rules_frozen_reused_from_committed_detector") is not True:
        failures.append("rules_not_frozen_reused")
    if record.get("no_parameter_optimization") is not True:
        failures.append("optimization_not_forbidden")
    if record.get("annualized_carry_enter_bps") != 100.0:
        failures.append("enter_carry_not_100")
    if record.get("min_hold_bars") != 20:
        failures.append("min_hold_not_20")
    if record.get("max_round_trips_per_year_per_asset") != 6:
        failures.append("turnover_ceiling_not_6")
    if record.get("is_mechanically_neutral_same_asset") is not True:
        failures.append("must_be_mechanically_neutral_same_asset")
    if record.get("is_low_turnover") is not True:
        failures.append("must_be_low_turnover")
    if record.get("uses_basis_z_stop") is not False:
        failures.append("must_not_use_basis_z_stop")
    if record.get("uses_drawdown_stop") is not False:
        failures.append("must_not_use_drawdown_stop")

    # per-asset + total aggregates pinned exactly (anti-tamper)
    pa = record.get("per_asset") or {}
    if set(pa) != {"BTCUSDT", "ETHUSDT", "SOLUSDT"}:
        failures.append("per_asset_universe_tampered")
    if sum(pa.get(s, {}).get("accepted_label_count", 0) for s in pa) != (
            TOTAL_ACCEPTED_LABEL_COUNT):
        failures.append("per_asset_accepted_do_not_sum_to_total")
    if record.get("total_accepted_label_count") != TOTAL_ACCEPTED_LABEL_COUNT:
        failures.append("total_accepted_tampered")
    if record.get("total_detected_setup_count") != TOTAL_DETECTED_SETUP_COUNT:
        failures.append("total_detected_tampered")
    if record.get("total_rejected_label_count") != TOTAL_REJECTED_LABEL_COUNT:
        failures.append("total_rejected_tampered")
    if record.get("total_exit_counts") != TOTAL_EXIT_COUNTS:
        failures.append("exit_counts_tampered")
    if record.get("total_mechanical_neutral_fail") != 0:
        failures.append("mechanical_neutral_fail_tampered")
    if record.get("total_round_trips") != TOTAL_ROUND_TRIPS:
        failures.append("round_trips_tampered")

    # structural verdict: low turnover, reconciles, NO performance/profitability claim
    sv = record.get("structural_verdict") or {}
    if sv.get("is_genuinely_low_turnover") is not True:
        failures.append("must_be_genuinely_low_turnover")
    if sv.get("round_trips_under_ceiling") is not True:
        failures.append("round_trips_should_be_under_ceiling")
    if sv.get("mechanical_neutrality_holds") is not True:
        failures.append("mechanical_neutrality_should_hold")
    if sv.get("labels_reconcile") is not True:
        failures.append("labels_do_not_reconcile")
    if sv.get("exits_reconcile_with_accepted") is not True:
        failures.append("exits_do_not_reconcile")
    if sv.get("mechanics_clean") is not True:
        failures.append("mechanics_should_be_clean")
    # the labels stage NEVER claims performance / profitability / fee-honest result
    if sv.get("profitability_established") is not False:
        failures.append("must_not_claim_profitability")
    if sv.get("edge_established") is not False:
        failures.append("must_not_claim_edge")
    if sv.get("fee_honest_performance_claimed") is not False:
        failures.append("must_not_claim_fee_honest_performance")
    if sv.get("decisive_gate_is_fee_honest_replay") is not True:
        failures.append("replay_must_be_decisive_gate")
    if sv.get("replay_remains_locked") is not True:
        failures.append("replay_must_remain_locked")
    if record.get("profitability_established") is not False:
        failures.append("top_level_profitability_claimed")
    if record.get("fee_honest_performance_claimed") is not False:
        failures.append("top_level_fee_honest_claimed")

    # NOT a rescue/retune of C20
    if record.get("is_rescue_or_retune_of_c20") is not False:
        failures.append("must_not_be_c20_rescue")
    if record.get("c20_remains_rejected") is not True:
        failures.append("c20_must_remain_rejected")

    # cost reserved, not applied; replay LOCKED
    if record.get("cost_model_applied_here") is not False:
        failures.append("cost_applied_in_labels")
    if record.get("fee_applied") is not False:
        failures.append("fee_applied_in_labels")
    if record.get("all_in_round_trip_bps_reserved") != 37.0:
        failures.append("cost_reserve_tampered")
    if record.get("round_trip_cost_per_trade_bps_reserved") != 74.0:
        failures.append("two_leg_cost_reserve_tampered")
    if record.get("replay_remains_locked") is not True:
        failures.append("replay_must_remain_locked_top")

    # no C22 + next action + downstream locks
    if record.get("does_not_start_c22") is not True:
        failures.append("must_not_start_c22")
    if record.get("c22_candidate_id") is not None:
        failures.append("c22_must_be_none")
    if record.get("next_required_action") != (
            "HUMAN_DECISION_C21_ADVANCE_TO_FEE_HONEST_REPLAY_OR_REJECT"):
        failures.append("next_action_not_replay_gate")
    for gate in ("replay_gate_locked", "paper_trading_gate_locked",
                 "live_gate_locked"):
        if record.get(gate) is not True:
            failures.append("downstream_gate_unlocked_%s" % gate)

    locks = record.get("scope_locks") or {}
    for key in ("no_re_detect", "no_relabel", "no_replay", "no_pnl",
                "no_cost_application", "no_optimization", "no_tuning", "no_rescue",
                "no_rescue_c20", "no_data_fetch", "no_data_commit", "no_xauusd",
                "no_high_turnover", "no_basis_z_stop", "no_drawdown_stop",
                "no_fee_honest_performance_claim", "no_overlapping_positions",
                "no_commit", "no_push", "no_paper_trading", "no_live_trading",
                "no_start_c22", "no_gate_skip"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
