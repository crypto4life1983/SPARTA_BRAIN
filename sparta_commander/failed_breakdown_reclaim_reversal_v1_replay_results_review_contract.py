"""Candidate #12 (failed_breakdown_reclaim_reversal_v1) fee+slippage-honest
replay-results review / evidence-freeze contract.

RESEARCH ONLY. Reviews the FROZEN, SHA-pinned replay artifacts produced by
tools/c12_fee_honest_replay_once.py against the pushed, chain-gated C12 real-
candle labels review. Pure, in-memory evidence record: NO file I/O, NO network,
NO data fetch, NO relabel, NO parameter optimization, NO PnL execution, NO
robustness, NO portfolio compute, NO trading. It does NOT claim profitability or
paper/live readiness. It freezes the replay aggregates + the decisive-gate
evaluation for human review and locks every downstream gate.

Chain gate: build_c12_replay_review() requires build_c12_labels_review() to
return the FROZEN labels verdict; any broken upstream gate short-circuits to a
BLOCKED verdict carrying a named blocker.

DECISIVE OUTCOME (frozen, honest): C12 FAILS the replay gates. Across all three
variants the net-all-in R after 37 bps is NEGATIVE (1.5R -48.8R, 2R -47.0R, 3R
-45.4R over 204 resolved trades); the strategy is WORSE than a matched random-
entry baseline (it beats only 2-5% of deterministic random resamples); ALL three
regimes are net-negative (bull/bear/chop) with bear (~-30R) and chop (~-15R)
structurally weak; the forward-OOS 2026 window is net-negative (-13.0R); and
target capture does NOT dominate (hits << horizon exits). The only gate that is
nominally "True" is beats-buy-and-hold -- but only because a passive hold of the
same post-reclaim windows is even MORE negative (-86.7R), so it is meaningless.
No variant passes all decisive gates -> STRUCTURAL REJECTION PRESSURE. The
reject/keep decision is the human's at the next gate.
"""
from __future__ import annotations

from typing import Any

from sparta_commander.failed_breakdown_reclaim_reversal_v1_real_candle_labels_review_contract import (  # noqa: E501
    VERDICT_C12L_FROZEN,
    build_c12_labels_review,
)

C12RR_SCHEMA_VERSION = 1
C12RR_MODE = "RESEARCH_ONLY"
CANDIDATE_ID = "FAILED_BREAKDOWN_RECLAIM_REVERSAL_V1"
CANDIDATE_FAMILY = "failed_breakdown_reclaim_reversal"
SYMBOLS = ("BTCUSD", "ETHUSD", "SOLUSD")
TIMEFRAME = "1d"
DIRECTION = "long_only"

VERDICT_C12RR_FROZEN = "C12_REPLAY_RESULTS_FROZEN_FOR_HUMAN_REVIEW"
VERDICT_C12RR_BLOCKED = "C12_REPLAY_RESULTS_BLOCKED"
NEXT_REQUIRED_ACTION = "HUMAN_DECISION_C12_PROMOTE_TO_ROBUSTNESS_OR_REJECT"

HEAD_AT_LABELS_REVIEW = "f9b510d9d8a4cb50bfb17bad5e5fa47f8e7b4038"

EXPECTED_SOURCE_SHA256 = {
    "BTCUSD": "043fb722b35e738a0c2050f9388defc7ca99322ed2f153989746ee28bbb89b88",
    "ETHUSD": "1bfd0ca86137747f0fe4c3fb127b00dcbd4885bf76056dbc9c091a9d4681c1a3",
    "SOLUSD": "4716d4d124bd7d5327fdc4230f7b2eaea70085df88c182dd129232ce802c0113",
}
EXPECTED_LABELS_SHA256 = (
    "503bfe4f1b72279c5472fde335d97446aad37303b029ea82ed5c4f50af299764")
EXPECTED_REPLAY_LEDGER_SHA256 = (
    "e1582e638b5a54d486d94c4254f12dcbfc7e1b9ff183e54a08066d5d04543126")
EXPECTED_REPLAY_SUMMARY_SHA256 = (
    "a2438be67b1f060c46bc7cb338a0698593fbcca4bb639d97fcb5273b3d268886")

LEDGER_PATH = ("data/failed_breakdown_reclaim_reversal_c12/replay_results/"
               "c12_replay_ledger.json")
SUMMARY_PATH = ("data/failed_breakdown_reclaim_reversal_c12/replay_results/"
                "c12_replay_summary.json")

FEE_ROUND_TRIP_BPS = 27.0
SLIPPAGE_ROUND_TRIP_BPS = 10.0
ALL_IN_ROUND_TRIP_BPS = 37.0
MAX_HOLD_BARS = 3
MAX_HORIZON_EXIT_SHARE = 0.50
REPLAYED_LABEL_COUNT = 206
FORWARD_OOS_START = "2026-01-01"
RANDOM_MASTER_SEED = 20260617
RANDOM_RESAMPLES = 200

# Matched buy-and-hold (passive hold of the same windows to +3 close) net-all-in
# total -- identical for every variant (variant only changes the target).
BUY_AND_HOLD_NET_ALL_IN_TOTAL = -86.6632

# Frozen replay aggregates (from tools/c12_fee_honest_replay_once.py over the
# SHA-pinned inputs). All R figures are out-of-sample real-candle, net of 37 bps.
# Rounded; the gitignored ledger carries full precision.
REPLAY_AGGREGATES = {
    "1.5r": {
        "trade_count": 204, "hit": 27, "horizon": 93, "horizon_exit_share": 0.4559,
        "net_r_total_all_in": -48.7963, "net_r_mean_all_in": -0.2392,
        "max_drawdown_r_all_in": 50.579, "worst_losing_streak": 13,
        "random_entry_mean_net_all_in": -23.3255, "random_entry_percentile": 0.05,
        "target_capture_dominates": False, "beats_buy_and_hold": True,
        "beats_random_entry_mean": False, "net_all_in_positive": False,
        "per_regime_net_all_in": {"bull": -3.4398, "bear": -30.1971,
                                  "chop": -15.1593},
        "forward_oos_net_all_in": -12.9812, "in_sample_net_all_in": -35.8151,
    },
    "2r": {
        "trade_count": 204, "hit": 17, "horizon": 102, "horizon_exit_share": 0.5,
        "net_r_total_all_in": -47.0458, "net_r_mean_all_in": -0.2306,
        "max_drawdown_r_all_in": 48.573, "worst_losing_streak": 13,
        "random_entry_mean_net_all_in": -17.917, "random_entry_percentile": 0.04,
        "target_capture_dominates": False, "beats_buy_and_hold": True,
        "beats_random_entry_mean": False, "net_all_in_positive": False,
        "per_regime_net_all_in": {"bull": -4.6286, "bear": -28.0032,
                                  "chop": -14.4141},
        "forward_oos_net_all_in": -12.9812, "in_sample_net_all_in": -34.0646,
    },
    "3r": {
        "trade_count": 204, "hit": 6, "horizon": 113, "horizon_exit_share": 0.5539,
        "net_r_total_all_in": -45.4211, "net_r_mean_all_in": -0.2226,
        "max_drawdown_r_all_in": 46.949, "worst_losing_streak": 13,
        "random_entry_mean_net_all_in": -12.0263, "random_entry_percentile": 0.02,
        "target_capture_dominates": False, "beats_buy_and_hold": True,
        "beats_random_entry_mean": False, "net_all_in_positive": False,
        "per_regime_net_all_in": {"bull": -2.2021, "bear": -28.7519,
                                  "chop": -14.4672},
        "forward_oos_net_all_in": -12.9812, "in_sample_net_all_in": -32.4399,
    },
}

ANY_VARIANT_PASSES_ALL_DECISIVE_GATES = False
STRUCTURAL_REJECTION_PRESSURE = True

# The decisive gates, evaluated honestly (True = gate satisfied).
DECISIVE_GATE_RESULTS = {
    "net_after_costs_positive_any_variant": False,
    "beats_random_entry_any_variant": False,        # worse than random timing
    "regime_symmetry_all_positive_any_variant": False,
    "bear_not_structurally_weak_any_variant": False,
    "chop_not_structurally_weak_any_variant": False,
    "forward_oos_2026_positive_any_variant": False,
    "target_capture_dominates_any_variant": False,
    "horizon_exit_within_cap_all_variants": False,  # 3R = 55.4% > 50%
    "beats_buy_and_hold_any_variant": True,         # meaningless: B&H even worse
}

REJECTION_WARNINGS = {
    "negative_all_in_net_all_variants": True,        # TRIGGERED
    "worse_than_random_entry_baseline": True,        # TRIGGERED (pctl 0.02-0.05)
    "all_regimes_net_negative": True,                # TRIGGERED
    "bear_and_chop_structurally_weak": True,         # TRIGGERED
    "negative_forward_oos_2026": True,               # TRIGGERED
    "target_capture_does_not_dominate": True,        # TRIGGERED (hits << horizons)
    "buy_and_hold_only_beaten_because_it_is_more_negative": True,
}

HONEST_CAVEATS = (
    "Out-of-sample real-candle replay of the 206 frozen labels only; not a live "
    "result and not a profitability claim.",
    "C12 FAILS the replay: net-all-in R after 37 bps is NEGATIVE for every "
    "variant (1.5R -48.8R, 2R -47.0R, 3R -45.4R over 204 resolved trades).",
    "The strategy is WORSE than a matched random-entry baseline (it beats only "
    "2-5% of deterministic random resamples) -- the failed-breakdown reclaim "
    "trigger adds NEGATIVE value over random timing with identical geometry.",
    "ALL three regimes are net-negative (bull/bear/chop); bear (~-30R) and chop "
    "(~-15R) are structurally weak -- the opposite of the required regime "
    "symmetry.",
    "Forward-OOS 2026 is net-negative (-13.0R); target capture does NOT dominate "
    "(hits 6-27 vs horizon exits 93-113); 3R is horizon-dominated (55%).",
    "The only nominally-passing gate (beats buy-and-hold) passes ONLY because a "
    "passive hold of the same post-reclaim windows is even more negative "
    "(-86.7R); it is not evidence of an edge.",
    "Per the pre-registered C12 spec, failing the must-beat-baseline, "
    "regime-symmetry, forward-OOS, and target-capture gates is STRUCTURAL "
    "REJECTION PRESSURE. The reject/keep decision is the human's at the next "
    "gate.",
)

CLAIM_LOCKS = (
    "no_profitability_claim", "no_paper_approval", "no_live_approval",
    "no_execution_approval", "no_winner_wording",
    "no_promotion_decision_made_by_this_gate",
    "no_relabel_authorized_by_this_gate",
    "fails_must_beat_random_entry_disclosed",
    "all_regimes_negative_disclosed",
    "negative_forward_oos_disclosed",
    "target_capture_failure_disclosed",
    "structural_rejection_pressure_disclosed",
)

C12RR_LABEL = (
    "C12 REPLAY RESULTS (READ-ONLY, RESEARCH ONLY). FEE+SLIPPAGE HONEST (37 BPS "
    "ALL-IN). OUT-OF-SAMPLE REAL-CANDLE, BTC/ETH/SOL 1D, 206 LABELS, <=3-BAR "
    "HOLD. FAILS: NET NEGATIVE ALL VARIANTS, WORSE THAN RANDOM ENTRY, ALL "
    "REGIMES NEGATIVE (BEAR/CHOP WEAK), FORWARD-OOS 2026 NEGATIVE, TARGET "
    "CAPTURE DOES NOT DOMINATE -> STRUCTURAL REJECTION PRESSURE. NOT A "
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
    "optimizes_parameters", "uses_one_edit_allowance",
    "authorizes_paper_execution", "authorizes_micro_live",
    "authorizes_live_trading", "promotes_gate", "unlocks_downstream_gate",
    "claims_profitability", "claims_edge", "claims_paper_or_live_readiness",
    "executes", "writes_files",
)


def get_candidate_12_replay_review_label() -> str:
    return C12RR_LABEL


def get_candidate_12_replay_review_next_action() -> str:
    return NEXT_REQUIRED_ACTION


def build_c12_replay_review(repo_root: Any = ".",
                            tracked_paths: list | None = None
                            ) -> dict[str, Any]:
    """Assemble the C12 replay-results review record. Chain-gated on the pushed
    C12 labels review (must return FROZEN). Pure; no I/O."""
    record: dict[str, Any] = {
        "schema_version": C12RR_SCHEMA_VERSION,
        "label": C12RR_LABEL, "mode": C12RR_MODE,
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
        "max_hold_bars": MAX_HOLD_BARS,
        "max_horizon_exit_share": MAX_HORIZON_EXIT_SHARE,
        "replayed_label_count": REPLAYED_LABEL_COUNT,
        "forward_oos_start": FORWARD_OOS_START,
        "random_master_seed": RANDOM_MASTER_SEED,
        "random_resamples": RANDOM_RESAMPLES,
        "buy_and_hold_net_all_in_total": BUY_AND_HOLD_NET_ALL_IN_TOTAL,
        "replay_aggregates": REPLAY_AGGREGATES,
        "decisive_gate_results": dict(DECISIVE_GATE_RESULTS),
        "any_variant_passes_all_decisive_gates":
            ANY_VARIANT_PASSES_ALL_DECISIVE_GATES,
        "structural_rejection_pressure": STRUCTURAL_REJECTION_PRESSURE,
        "rejection_warnings": dict(REJECTION_WARNINGS),
        "rejection_warnings_triggered": sorted(
            k for k, v in REJECTION_WARNINGS.items() if v
            and k != "buy_and_hold_only_beaten_because_it_is_more_negative"),
        "honest_caveats": list(HONEST_CAVEATS),
        "claim_locks": list(CLAIM_LOCKS),
        "is_replay_review_only": True,
        "current_loop_stage": "replay_evaluation_review",
        "human_review_required": True,
        "robustness_gate_locked": True, "relabel_gate_locked": True,
        "data_fetch_gate_locked": True, "portfolio_compute_gate_locked": True,
        "paper_trading_gate_locked": True, "micro_live_gate_locked": True,
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
        "no_parameter_optimization": True, "no_one_edit_allowance_used": True,
        "no_profitability_claim": True, "no_paper_live_readiness_claim": True,
        "no_downstream_gate_unlock": True,
    }

    labels = build_c12_labels_review(repo_root, tracked_paths or [])
    record["labels_review_verdict"] = labels.get("verdict")
    if labels.get("verdict") != VERDICT_C12L_FROZEN:
        record["verdict"] = VERDICT_C12RR_BLOCKED
        record["blockers"].append("labels_review_not_frozen")
        return record
    if labels.get("expected_labels_sha256") != EXPECTED_LABELS_SHA256:
        record["verdict"] = VERDICT_C12RR_BLOCKED
        record["blockers"].append("labels_sha_pin_mismatch")
        return record

    tracked = set(tracked_paths or [])
    if LEDGER_PATH in tracked or SUMMARY_PATH in tracked:
        record["verdict"] = VERDICT_C12RR_BLOCKED
        record["blockers"].append("replay_artifact_tracked")
        return record

    record["verdict"] = VERDICT_C12RR_FROZEN
    return record


def validate_c12_replay_review(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. FROZEN is valid only when the SHA pins, the cost
    basis, the honest negative findings (net negative all variants, worse than
    random entry, all regimes negative, negative forward-OOS, structural
    rejection pressure, no variant passes), and all downstream locks are intact.
    The negative findings cannot be silently flipped to positive."""
    failures: list = []
    if record.get("verdict") != VERDICT_C12RR_FROZEN:
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
    if record.get("labels_review_verdict") != VERDICT_C12L_FROZEN:
        failures.append("labels_review_verdict_tampered")

    if record.get("all_in_round_trip_bps") != ALL_IN_ROUND_TRIP_BPS:
        failures.append("all_in_cost_tampered")
    if (record.get("fee_round_trip_bps", 0)
            + record.get("slippage_round_trip_bps", 0)
            != ALL_IN_ROUND_TRIP_BPS):
        failures.append("cost_components_do_not_sum")

    # Honest negative findings cannot be flipped.
    if record.get("any_variant_passes_all_decisive_gates") is not False:
        failures.append("variant_pass_flag_tampered")
    if record.get("structural_rejection_pressure") is not True:
        failures.append("structural_rejection_pressure_cleared")
    dg = record.get("decisive_gate_results") or {}
    for key in ("net_after_costs_positive_any_variant",
                "beats_random_entry_any_variant",
                "regime_symmetry_all_positive_any_variant",
                "forward_oos_2026_positive_any_variant",
                "target_capture_dominates_any_variant"):
        if dg.get(key) is not False:
            failures.append("decisive_gate_flipped_%s" % key)
    rw = record.get("rejection_warnings") or {}
    for key in ("negative_all_in_net_all_variants",
                "worse_than_random_entry_baseline",
                "all_regimes_net_negative", "negative_forward_oos_2026",
                "target_capture_does_not_dominate"):
        if rw.get(key) is not True:
            failures.append("rejection_warning_cleared_%s" % key)

    # Per-variant: net negative + all regimes negative + forward-OOS negative.
    agg = record.get("replay_aggregates") or {}
    for name in ("1.5r", "2r", "3r"):
        v = agg.get(name) or {}
        if not (isinstance(v.get("net_r_total_all_in"), (int, float))
                and v["net_r_total_all_in"] < 0):
            failures.append("net_sign_tampered_%s" % name)
        if v.get("beats_random_entry_mean") is not False:
            failures.append("beats_random_flipped_%s" % name)
        pr = v.get("per_regime_net_all_in") or {}
        for r in ("bull", "bear", "chop"):
            if not (isinstance(pr.get(r), (int, float)) and pr[r] < 0):
                failures.append("regime_sign_tampered_%s_%s" % (name, r))
        if not (isinstance(v.get("forward_oos_net_all_in"), (int, float))
                and v["forward_oos_net_all_in"] < 0):
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
                     "fails_must_beat_random_entry_disclosed",
                     "all_regimes_negative_disclosed",
                     "negative_forward_oos_disclosed",
                     "structural_rejection_pressure_disclosed"):
        if required not in (record.get("claim_locks") or []):
            failures.append("claim_lock_missing_%s" % required)

    for banned in ("APPROVE", "PAPER", "LIVE", "EXECUTE", "BROKER", "ORDER",
                   "FETCH", "UNLOCK"):
        if banned in NEXT_REQUIRED_ACTION.upper():
            failures.append("next_action_banned_token_%s" % banned)

    return {"valid": not failures, "failures": failures}
