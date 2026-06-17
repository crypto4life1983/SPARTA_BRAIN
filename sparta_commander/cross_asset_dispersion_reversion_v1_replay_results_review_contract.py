"""Candidate #11 (CROSS_ASSET_DISPERSION_REVERSION_V1) fee+slippage-honest
replay-results review / evidence-freeze contract.

RESEARCH ONLY. Reviews the FROZEN, SHA-pinned replay artifacts produced by
tools/c11_fee_honest_replay_once.py against the pushed, chain-gated C11
detector-labels review. Pure, in-memory evidence record: NO file I/O, NO network,
NO data fetch, NO relabel, NO detector change, NO PnL execution, NO robustness,
NO portfolio compute, NO trading. It does NOT claim profitability or paper/live
readiness. It freezes the replay aggregates + the rejection-warning evaluation
for human review and locks every downstream gate.

Chain gate: build_c11_replay_review() requires build_c11_labels_review() to
return the FROZEN labels verdict; any broken upstream gate short-circuits to a
BLOCKED verdict carrying a named blocker.

HUMAN-FIXED REPLAY ASSUMPTION (disclosed): the C11 spec pre-declared entry, stop,
2R/3R/4R targets, the 81 bps floor and the 37 bps cost model, but did NOT
pre-declare a holding horizon. The human fixed a 5-bar / 5-day horizon at the
replay gate, chosen to match the 5-day dispersion lookback and to avoid C10's
long-drift trap; it was NOT optimized after seeing results.

Replay assumptions reviewed here (locked at the runner):
  * Long the relative laggard, BTC/ETH/SOL 1d, fixed 5-bar horizon exit;
    1.5*ATR(14) structure stop; target variants 2R/3R/4R; entry at the
    signal-bar close.
  * MISS = low<=stop -> -1R; HIT = high>=target -> +variant_r; same-bar straddle
    = STOP FIRST (conservative) -> -1R; otherwise HORIZON exit at the +5 close ->
    (exit_close-entry)/stop_distance. Every outcome is decisive.
  * Costs as R-units of the setup stop distance: 27 bps round-trip fee + 10 bps
    round-trip slippage = 37 bps all-in. net_r_all_in = gross_r - 37/stop_bps.
  * One position per asset: per-asset replay-time non-overlap = reduce-or-keep-
    only (different assets may overlap).

HEADLINE FINDING (frozen, honest): full-sample net R is POSITIVE after 37 bps
costs for all three variants, BUT the FORWARD-OOS 2026 continuation check -- the
single early-generalization check reserved from the labels stage -- FAILS (net
all-in R is negative in 2026 for every variant). The edge is also NOT
regime-symmetric (bear-regime net R is negative for 2R/3R) and is horizon-
dominated (73-75% horizon exits, hit rate ~2-4%), i.e. it leans on bull/chop
holding drift rather than clean cross-sectional reversion. Per the pre-registered
C11 spec ("Edge does not continue in forward-OOS -> structural rejection";
"regime symmetry required, not long drift"), this is STRUCTURAL REJECTION
PRESSURE. The REJECT/keep decision is the human's at the next gate.
"""
from __future__ import annotations

from typing import Any

from sparta_commander.cross_asset_dispersion_reversion_v1_real_candle_labels_review_contract import (  # noqa: E501
    VERDICT_C11L_FROZEN,
    build_c11_labels_review,
)

C11RR_SCHEMA_VERSION = 1
C11RR_MODE = "RESEARCH_ONLY"
CANDIDATE_ID = "CROSS_ASSET_DISPERSION_REVERSION_V1"
CANDIDATE_FAMILY = "cross_asset_dispersion_reversion"
SYMBOLS = ("BTCUSD", "ETHUSD", "SOLUSD")
TIMEFRAME = "1d"
DIRECTION = "long_only"

VERDICT_C11RR_FROZEN = "C11_REPLAY_RESULTS_FROZEN_FOR_HUMAN_REVIEW"
VERDICT_C11RR_BLOCKED = "C11_REPLAY_RESULTS_BLOCKED"
NEXT_REQUIRED_ACTION = "HUMAN_DECISION_C11_PROMOTE_TO_ROBUSTNESS_OR_REJECT"

HEAD_AT_LABELS_REVIEW = "8e69956ba10ea1c5dd80c2860b71142e2e9f512a"

EXPECTED_SOURCE_SHA256 = {
    "BTCUSD": "043fb722b35e738a0c2050f9388defc7ca99322ed2f153989746ee28bbb89b88",
    "ETHUSD": "1bfd0ca86137747f0fe4c3fb127b00dcbd4885bf76056dbc9c091a9d4681c1a3",
    "SOLUSD": "4716d4d124bd7d5327fdc4230f7b2eaea70085df88c182dd129232ce802c0113",
}
EXPECTED_LABELS_SHA256 = (
    "2a1273eb9a093a3e75a48748afd6a533954165de403b3dba7ebde291e38dc231")
EXPECTED_REPLAY_LEDGER_SHA256 = (
    "46f003e37fff4365af408ea077582ec989e27011efac113f48d51bd6950d35b1")
EXPECTED_REPLAY_SUMMARY_SHA256 = (
    "b55e6df673b135031d2d57447572066f8b4055deea0e3015b84d75a06834feab")

LEDGER_PATH = ("data/cross_asset_dispersion_reversion_c11/replay_results/"
               "c11_replay_ledger.json")
SUMMARY_PATH = ("data/cross_asset_dispersion_reversion_c11/replay_results/"
                "c11_replay_summary.json")

FEE_ROUND_TRIP_BPS = 27.0
SLIPPAGE_ROUND_TRIP_BPS = 10.0
ALL_IN_ROUND_TRIP_BPS = 37.0
TARGET_DISTANCE_FLOOR_BPS = 81.0
HOLDING_HORIZON_BARS = 5
HORIZON_SOURCE = "human_fixed_at_replay_gate_spec_did_not_predeclare"
SPEC_PREDECLARED_HORIZON = False
ACCEPTED_LABEL_INPUT_COUNT = 742
COMMON_WINDOW = ("2020-08-11", "2026-06-08")
FORWARD_OOS_START = "2026-01-01"

# Frozen replay aggregates (from tools/c11_fee_honest_replay_once.py over the
# SHA-pinned inputs above). All R figures are out-of-sample real-candle; the
# all-in column is after 37 bps round-trip costs. Rounded for the record; the
# gitignored ledger carries full precision. kept = post per-asset non-overlap.
REPLAY_AGGREGATES = {
    "2r": {
        "kept_count": 275, "dropped_overlap_count": 467, "trade_count": 275,
        "hit": 31, "miss": 64, "horizon": 180, "straddle": 0,
        "win_rate_net_all_in": 0.4691, "hit_rate": 0.1127,
        "horizon_exit_share": 0.6545,
        "gross_r_total": 35.8014, "net_r_total_fee_only": 26.0233,
        "net_r_total_all_in": 22.4018, "net_r_mean_all_in": 0.0815,
        "max_drawdown_r_all_in": 18.4986, "worst_losing_streak": 15,
        "net_all_in_positive_full_sample": True,
        "per_year_net_all_in": {"2020": 5.0191, "2021": 17.3558,
                                "2022": -12.7655, "2023": 11.2278,
                                "2024": -0.5901, "2025": 3.1087,
                                "2026": -0.9540},
        "per_asset_net_all_in": {"BTCUSD": -5.1577, "ETHUSD": 11.9571,
                                 "SOLUSD": 15.6024},
        "per_regime_net_all_in": {"bull": 11.5326, "bear": -5.2779,
                                  "chop": 16.1470},
        "forward_oos_net_all_in": {"in_sample": 23.3558, "forward_oos": -0.9540},
    },
    "3r": {
        "kept_count": 274, "dropped_overlap_count": 468, "trade_count": 274,
        "hit": 11, "miss": 63, "horizon": 200, "straddle": 0,
        "win_rate_net_all_in": 0.4672, "hit_rate": 0.0401,
        "horizon_exit_share": 0.7299,
        "gross_r_total": 44.3720, "net_r_total_fee_only": 34.6125,
        "net_r_total_all_in": 30.9979, "net_r_mean_all_in": 0.1131,
        "max_drawdown_r_all_in": 18.6151, "worst_losing_streak": 15,
        "net_all_in_positive_full_sample": True,
        "per_year_net_all_in": {"2020": 7.3925, "2021": 18.3915,
                                "2022": -14.1534, "2023": 14.2580,
                                "2024": 1.3754, "2025": 3.8515,
                                "2026": -0.1178},
        "per_asset_net_all_in": {"BTCUSD": -1.9252, "ETHUSD": 12.3255,
                                 "SOLUSD": 20.5975},
        "per_regime_net_all_in": {"bull": 14.7168, "bear": -2.4449,
                                  "chop": 18.7260},
        "forward_oos_net_all_in": {"in_sample": 31.1156, "forward_oos": -0.1178},
    },
    "4r": {
        "kept_count": 274, "dropped_overlap_count": 468, "trade_count": 274,
        "hit": 6, "miss": 63, "horizon": 205, "straddle": 0,
        "win_rate_net_all_in": 0.4672, "hit_rate": 0.0219,
        "horizon_exit_share": 0.7482,
        "gross_r_total": 50.1961, "net_r_total_fee_only": 40.4366,
        "net_r_total_all_in": 36.8220, "net_r_mean_all_in": 0.1344,
        "max_drawdown_r_all_in": 18.6151, "worst_losing_streak": 15,
        "net_all_in_positive_full_sample": True,
        "per_year_net_all_in": {"2020": 8.8541, "2021": 20.3915,
                                "2022": -14.1534, "2023": 16.1133,
                                "2024": 1.3774, "2025": 4.3569,
                                "2026": -0.1178},
        "per_asset_net_all_in": {"BTCUSD": -1.1455, "ETHUSD": 14.3255,
                                 "SOLUSD": 23.6419},
        "per_regime_net_all_in": {"bull": 14.3498, "bear": 0.2847,
                                  "chop": 22.1875},
        "forward_oos_net_all_in": {"in_sample": 36.9398, "forward_oos": -0.1178},
    },
}

# Forward-OOS 2026 continuation (the reserved labels-stage check, RUN here):
# negative net all-in R for every variant -> the continuation check FAILS.
FORWARD_OOS_CONTINUATION_PASSED = False
# Regime symmetry: bear-regime net all-in R is negative for 2R and 3R -> the
# edge is NOT regime-symmetric (4R only marginally positive in bear, +0.28R).
REGIME_SYMMETRY_PASSED = False
# Full-sample sign survives 37 bps costs for all variants (fee-only and all-in
# both positive); but the per-trade net mean is thin (0.08-0.13 R).
FULL_SAMPLE_SIGN_SURVIVES_COSTS = True

# The six pre-registered hard rejection warnings, evaluated honestly.
REJECTION_WARNINGS = {
    "negative_all_in_net_full_sample": False,   # all variants positive full-sample
    "profit_only_from_one_asset": False,        # ETH + SOL positive; BTC negative
    "profit_only_from_one_regime": False,       # bull + chop positive; bear negative
    "negative_forward_oos_2026": True,          # TRIGGERED: all variants negative
    "explained_by_long_drift": True,            # TRIGGERED: 73-75% horizon, bear<=0
    "too_cost_sensitive": False,                # full-sample sign survives costs
}
# Disclosure flags that are TRUE but did not, alone, trip a hard warning.
DISCLOSURES = {
    "btc_negative_all_variants": True,
    "bear_regime_negative_2r_3r": True,
    "horizon_dominated_holding_drift": True,
    "thin_per_trade_net_mean_0p08_to_0p13r": True,
    "year_2022_strongly_negative": True,
}
STRUCTURAL_REJECTION_PRESSURE = True

HONEST_CAVEATS = (
    "Out-of-sample real-candle replay only; not a live result and not a "
    "profitability claim.",
    "The 5-bar holding horizon is a HUMAN-FIXED replay assumption -- the C11 "
    "spec did NOT pre-declare a horizon. It was chosen to match the 5-day "
    "dispersion lookback and was not optimized after seeing results.",
    "Full-sample net R is positive after 37 bps all-in costs for all three "
    "variants, BUT the FORWARD-OOS 2026 continuation check FAILS (net all-in R "
    "is negative in 2026 for every variant). This is the single "
    "early-generalization check reserved from the labels stage.",
    "The edge is NOT regime-symmetric: bear-regime net R is negative (2R/3R); "
    "and it is horizon-dominated (73-75% horizon exits, hit rate ~2-4%), i.e. "
    "it leans on bull/chop holding drift, not clean cross-sectional reversion.",
    "BTCUSD is net negative across all variants; the positive total is carried "
    "by ETH and SOL. 2022 is strongly negative across variants.",
    "Per the pre-registered C11 spec (forward-OOS continuation required; "
    "regime-symmetry-not-long-drift required), this is STRUCTURAL REJECTION "
    "PRESSURE. The reject/keep decision is the human's at the next gate.",
)

CLAIM_LOCKS = (
    "no_profitability_claim", "no_paper_approval", "no_live_approval",
    "no_execution_approval", "no_winner_wording",
    "no_promotion_decision_made_by_this_gate",
    "no_relabel_authorized_by_this_gate",
    "forward_oos_continuation_failed_disclosed",
    "regime_asymmetry_disclosed",
    "long_drift_dominance_disclosed",
    "human_fixed_horizon_disclosed",
    "structural_rejection_pressure_disclosed",
)

C11RR_LABEL = (
    "C11 REPLAY RESULTS (READ-ONLY, RESEARCH ONLY). FEE+SLIPPAGE HONEST (37 BPS "
    "ALL-IN). OUT-OF-SAMPLE REAL-CANDLE, BTC/ETH/SOL 1D, 5-BAR HORIZON "
    "(HUMAN-FIXED; SPEC DID NOT PRE-DECLARE). FULL-SAMPLE NET POSITIVE AFTER "
    "COSTS BUT FORWARD-OOS 2026 NEGATIVE FOR EVERY VARIANT, BEAR-REGIME "
    "NEGATIVE, HORIZON-DOMINATED -> STRUCTURAL REJECTION PRESSURE. NOT A "
    "PROFITABILITY CLAIM. NOT AN APPROVAL FOR PAPER OR LIVE."
)

_CAPABILITY_FLAGS_FALSE = (
    "runs_real_candle_detection", "runs_detection_now", "labels_now",
    "runs_replay_now", "runs_relabel", "relabels_now", "scores_live",
    "stages_data_now", "fetches_data", "mutates_source_data", "calls_api",
    "uses_network", "uses_credentials", "uses_wallet", "uses_account",
    "connects_broker", "connects_exchange", "uses_real_money",
    "contains_order_logic", "contains_portfolio_allocation_logic",
    "runs_portfolio_compute", "deploys_capital", "starts_scheduler",
    "sends_notifications", "auto_commits", "auto_pushes", "creates_runners_now",
    "modifies_canonical_source", "modifies_detector_labels_artifacts",
    "modifies_replay_artifacts", "computes_live_pnl", "fits_parameters",
    "optimizes_horizon", "selects_best_asset",
    "authorizes_paper_execution", "authorizes_micro_live",
    "authorizes_live_trading", "promotes_gate", "unlocks_downstream_gate",
    "claims_profitability", "claims_edge", "claims_paper_or_live_readiness",
    "executes", "writes_files",
)


def get_candidate_11_replay_review_label() -> str:
    return C11RR_LABEL


def get_candidate_11_replay_review_next_action() -> str:
    return NEXT_REQUIRED_ACTION


def build_c11_replay_review(repo_root: Any = ".",
                            tracked_paths: list | None = None
                            ) -> dict[str, Any]:
    """Assemble the C11 replay-results review record. Chain-gated on the pushed
    C11 detector-labels review (must return FROZEN). Pure; no I/O."""
    record: dict[str, Any] = {
        "schema_version": C11RR_SCHEMA_VERSION,
        "label": C11RR_LABEL, "mode": C11RR_MODE,
        "lane": "crypto_d1_auto_research",
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "symbols": list(SYMBOLS), "timeframe": TIMEFRAME, "direction": DIRECTION,
        "verdict": None, "blockers": [],
        "head_at_labels_review": HEAD_AT_LABELS_REVIEW,
        "expected_source_sha256": dict(EXPECTED_SOURCE_SHA256),
        "expected_labels_sha256": EXPECTED_LABELS_SHA256,
        "expected_replay_ledger_sha256": EXPECTED_REPLAY_LEDGER_SHA256,
        "expected_replay_summary_sha256": EXPECTED_REPLAY_SUMMARY_SHA256,
        "ledger_path": LEDGER_PATH, "summary_path": SUMMARY_PATH,
        "fee_round_trip_bps": FEE_ROUND_TRIP_BPS,
        "slippage_round_trip_bps": SLIPPAGE_ROUND_TRIP_BPS,
        "all_in_round_trip_bps": ALL_IN_ROUND_TRIP_BPS,
        "target_distance_floor_bps": TARGET_DISTANCE_FLOOR_BPS,
        "holding_horizon_bars": HOLDING_HORIZON_BARS,
        "horizon_source": HORIZON_SOURCE,
        "spec_predeclared_horizon": SPEC_PREDECLARED_HORIZON,
        "accepted_label_input_count": ACCEPTED_LABEL_INPUT_COUNT,
        "common_window": list(COMMON_WINDOW),
        "forward_oos_start": FORWARD_OOS_START,
        "replay_aggregates": REPLAY_AGGREGATES,
        "forward_oos_continuation_passed": FORWARD_OOS_CONTINUATION_PASSED,
        "regime_symmetry_passed": REGIME_SYMMETRY_PASSED,
        "full_sample_sign_survives_costs": FULL_SAMPLE_SIGN_SURVIVES_COSTS,
        "rejection_warnings": dict(REJECTION_WARNINGS),
        "rejection_warnings_triggered": sorted(
            k for k, v in REJECTION_WARNINGS.items() if v),
        "disclosures": dict(DISCLOSURES),
        "structural_rejection_pressure": STRUCTURAL_REJECTION_PRESSURE,
        "all_variants_net_positive_after_costs_full_sample": True,
        "any_variant_net_positive_forward_oos_2026": False,
        "honest_caveats": list(HONEST_CAVEATS),
        "claim_locks": list(CLAIM_LOCKS),
        "is_replay_review_only": True,
        "current_loop_stage": "replay_evaluation_review",
        "human_review_required": True,
        "robustness_gate_locked": True,
        "relabel_gate_locked": True,
        "data_fetch_gate_locked": True,
        "portfolio_compute_gate_locked": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
        "live_gate_locked": True,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_paper_trading": True, "no_micro_live": True,
        "no_live_trading": True, "no_broker": True, "no_exchange": True,
        "no_wallet": True, "no_account": True, "no_credentials": True,
        "no_order_logic": True, "no_portfolio_allocation": True,
        "no_portfolio_compute": True, "no_api": True, "no_network": True,
        "no_fetch": True, "no_data_mutation": True, "no_notification": True,
        "no_scheduler": True, "no_relabel": True, "no_detector_change": True,
        "no_parameter_fitting": True, "no_horizon_optimization": True,
        "no_best_asset_selection": True, "no_profitability_claim": True,
        "no_paper_live_readiness_claim": True, "no_downstream_gate_unlock": True,
    }

    # Chain gate: the pushed labels-review must certify FROZEN.
    labels = build_c11_labels_review(repo_root, tracked_paths or [])
    record["labels_review_verdict"] = labels.get("verdict")
    if labels.get("verdict") != VERDICT_C11L_FROZEN:
        record["verdict"] = VERDICT_C11RR_BLOCKED
        record["blockers"].append("labels_review_not_frozen")
        return record
    if labels.get("expected_labels_sha256") != EXPECTED_LABELS_SHA256:
        record["verdict"] = VERDICT_C11RR_BLOCKED
        record["blockers"].append("labels_sha_pin_mismatch")
        return record

    # The two replay artifacts must stay UNTRACKED (gitignored data).
    tracked = set(tracked_paths or [])
    if LEDGER_PATH in tracked or SUMMARY_PATH in tracked:
        record["verdict"] = VERDICT_C11RR_BLOCKED
        record["blockers"].append("replay_artifact_tracked")
        return record

    record["verdict"] = VERDICT_C11RR_FROZEN
    return record


def validate_c11_replay_review(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. FROZEN is valid only when the SHA pins, the cost
    basis, the FORWARD-OOS-FAILED + regime-asymmetry + structural-rejection-
    pressure disclosures, and all downstream locks are intact. The honest
    negative findings cannot be silently flipped to positive."""
    failures: list = []
    if record.get("verdict") != VERDICT_C11RR_FROZEN:
        failures.append("verdict_not_frozen")
    if record.get("blockers"):
        failures.append("has_blockers")

    for field, expected in (
            ("expected_labels_sha256", EXPECTED_LABELS_SHA256),
            ("expected_replay_ledger_sha256", EXPECTED_REPLAY_LEDGER_SHA256),
            ("expected_replay_summary_sha256", EXPECTED_REPLAY_SUMMARY_SHA256)):
        v = record.get(field)
        if not isinstance(v, str) or len(v) != 64 or v != expected:
            failures.append("bad_sha_%s" % field)
    src = record.get("expected_source_sha256") or {}
    for k, expected in EXPECTED_SOURCE_SHA256.items():
        if src.get(k) != expected:
            failures.append("bad_source_sha_%s" % k)
    if record.get("head_at_labels_review") != HEAD_AT_LABELS_REVIEW:
        failures.append("head_at_labels_review_tampered")
    if record.get("labels_review_verdict") != VERDICT_C11L_FROZEN:
        failures.append("labels_review_verdict_tampered")

    # Cost basis intact.
    if record.get("all_in_round_trip_bps") != ALL_IN_ROUND_TRIP_BPS:
        failures.append("all_in_cost_tampered")
    if (record.get("fee_round_trip_bps", 0)
            + record.get("slippage_round_trip_bps", 0)
            != ALL_IN_ROUND_TRIP_BPS):
        failures.append("cost_components_do_not_sum")

    # Human-fixed horizon disclosure intact.
    if record.get("spec_predeclared_horizon") is not False:
        failures.append("spec_predeclared_horizon_flag_tampered")
    if record.get("holding_horizon_bars") != HOLDING_HORIZON_BARS:
        failures.append("horizon_tampered")

    # Honest negative findings cannot be flipped.
    if record.get("forward_oos_continuation_passed") is not False:
        failures.append("forward_oos_pass_flag_tampered")
    if record.get("any_variant_net_positive_forward_oos_2026") is not False:
        failures.append("forward_oos_positive_flag_tampered")
    if record.get("regime_symmetry_passed") is not False:
        failures.append("regime_symmetry_flag_tampered")
    if record.get("structural_rejection_pressure") is not True:
        failures.append("structural_rejection_pressure_cleared")
    rw = record.get("rejection_warnings") or {}
    if rw.get("negative_forward_oos_2026") is not True:
        failures.append("forward_oos_warning_cleared")
    if rw.get("explained_by_long_drift") is not True:
        failures.append("long_drift_warning_cleared")

    # Per-variant aggregates: trade counts + the negative forward-OOS sign.
    agg = record.get("replay_aggregates") or {}
    for name in ("2r", "3r", "4r"):
        v = agg.get(name) or {}
        if v.get("net_all_in_positive_full_sample") is not True:
            failures.append("full_sample_sign_tampered_%s" % name)
        foos = (v.get("forward_oos_net_all_in") or {}).get("forward_oos")
        if not (isinstance(foos, (int, float)) and foos < 0):
            failures.append("forward_oos_sign_tampered_%s" % name)

    locks = record.get("scope_locks") or {}
    for key, val in locks.items():
        if val is not True:
            failures.append("scope_lock_false_%s" % key)
    for key in ("robustness_gate_locked", "relabel_gate_locked",
                "data_fetch_gate_locked", "portfolio_compute_gate_locked",
                "paper_trading_gate_locked", "micro_live_gate_locked",
                "live_gate_locked", "human_review_required",
                "is_replay_review_only"):
        if record.get(key) is not True:
            failures.append("gate_flag_tampered_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    for required in ("no_profitability_claim",
                     "forward_oos_continuation_failed_disclosed",
                     "regime_asymmetry_disclosed",
                     "structural_rejection_pressure_disclosed",
                     "human_fixed_horizon_disclosed"):
        if required not in (record.get("claim_locks") or []):
            failures.append("claim_lock_missing_%s" % required)

    for banned in ("APPROVE", "PAPER", "LIVE", "EXECUTE", "BROKER", "ORDER",
                   "FETCH", "UNLOCK"):
        if banned in NEXT_REQUIRED_ACTION.upper():
            failures.append("next_action_banned_token_%s" % banned)

    return {"valid": not failures, "failures": failures}
