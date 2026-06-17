"""Candidate #14 (conviction_bar_follow_through_v1) fee+slippage-honest replay-
results review / evidence-freeze contract.

RESEARCH ONLY. Reviews the FROZEN, SHA-pinned replay artifacts produced by
tools/c14_fee_honest_replay_once.py against the pushed, chain-gated C14 real-
candle labels review. Pure, in-memory evidence record: NO file I/O, NO network,
NO data fetch, NO relabel, NO parameter optimization, NO PnL execution, NO
robustness, NO portfolio compute, NO trading. It does NOT claim profitability or
paper/live readiness.

Chain gate: build_c14_replay_review() requires build_c14_labels_review() to return
the FROZEN labels verdict; any broken upstream gate short-circuits to BLOCKED.

DECISIVE OUTCOME (frozen, honest): C14 FAILS the replay gates -> STRUCTURAL
REJECTION PRESSURE. The NOTABLE POSITIVE: it is the FIRST candidate to BEAT a
matched random-entry baseline for every variant (percentile 0.61 / 0.835 / 0.905)
-- the conviction-bar SIGNAL adds genuine timing value over random. BUT it LOSES
to buy-and-hold for EVERY variant (B&H +39.7R vs strategy -15.6R / +1.3R /
+13.5R) -- the absolute return is market CARRY that passive holding captures more
cheaply; the forward-OOS 2026 window is NET-NEGATIVE for every variant (-2.0R /
-3.7R / -3.7R); and target capture does NOT dominate (hits << horizon exits). So
even though 1.5R/2R are net-positive after costs and 2R is regime-symmetric, no
variant passes ALL the decisive gates. "Beats random but loses to buy-and-hold"
is the carry signature: a real entry-timing signal whose money is still just long
carry. The reject/keep decision is the human's at the next gate.
"""
from __future__ import annotations

from typing import Any

from sparta_commander.conviction_bar_follow_through_v1_real_candle_labels_review_contract import (  # noqa: E501
    VERDICT_C14L_FROZEN,
    build_c14_labels_review,
)

C14RR_SCHEMA_VERSION = 1
C14RR_MODE = "RESEARCH_ONLY"
CANDIDATE_ID = "CONVICTION_BAR_FOLLOW_THROUGH_V1"
CANDIDATE_FAMILY = "conviction_bar_follow_through"
SYMBOLS = ("BTCUSD", "ETHUSD", "SOLUSD")
TIMEFRAME = "1d"
DIRECTION = "long_only"

VERDICT_C14RR_FROZEN = "C14_REPLAY_RESULTS_FROZEN_FOR_HUMAN_REVIEW"
VERDICT_C14RR_BLOCKED = "C14_REPLAY_RESULTS_BLOCKED"
NEXT_REQUIRED_ACTION = "HUMAN_DECISION_C14_PROMOTE_TO_ROBUSTNESS_OR_REJECT"

HEAD_AT_LABELS_REVIEW = "bc69e4f0b0cf1e63ed00d6cb02b991f3d9d22ac6"

EXPECTED_SOURCE_SHA256 = {
    "BTCUSD": "043fb722b35e738a0c2050f9388defc7ca99322ed2f153989746ee28bbb89b88",
    "ETHUSD": "1bfd0ca86137747f0fe4c3fb127b00dcbd4885bf76056dbc9c091a9d4681c1a3",
    "SOLUSD": "4716d4d124bd7d5327fdc4230f7b2eaea70085df88c182dd129232ce802c0113",
}
EXPECTED_LABELS_SHA256 = (
    "9797558c96e6b937098ee84447c74f7adb206519a49143b9834af0cd99f372d6")
EXPECTED_REPLAY_LEDGER_SHA256 = (
    "30982b9723d1711dd209d2d752981ce15372e2d8a1e0d52db2484cb7594d7fee")
EXPECTED_REPLAY_SUMMARY_SHA256 = (
    "7a4307883163df7441eeaaa20a878b7cbab94de9fb1e4c0385fde2ecaf706f64")

LEDGER_PATH = ("data/conviction_bar_follow_through_c14/replay_results/"
               "c14_replay_ledger.json")
SUMMARY_PATH = ("data/conviction_bar_follow_through_c14/replay_results/"
                "c14_replay_summary.json")

FEE_ROUND_TRIP_BPS = 27.0
SLIPPAGE_ROUND_TRIP_BPS = 10.0
ALL_IN_ROUND_TRIP_BPS = 37.0
MAX_HOLD_BARS = 2
MAX_HORIZON_EXIT_SHARE = 0.50
REPLAYED_LABEL_COUNT = 347
FORWARD_OOS_START = "2026-01-01"
RANDOM_MASTER_SEED = 20260617
RANDOM_RESAMPLES = 200

# Matched buy-and-hold (passive hold to +2 close) net-all-in total -- identical
# for every variant (variant only changes the target).
BUY_AND_HOLD_NET_ALL_IN_TOTAL = 39.6973

# Frozen replay aggregates (from tools/c14_fee_honest_replay_once.py over the
# SHA-pinned inputs). All R figures are out-of-sample real-candle, net of 37 bps.
REPLAY_AGGREGATES = {
    "1r": {
        "trade_count": 346, "hit": 108, "horizon": 140, "horizon_exit_share": 0.4046,
        "net_r_total_all_in": -15.5789, "net_r_mean_all_in": -0.0450,
        "max_drawdown_r_all_in": 20.225, "worst_losing_streak": 7,
        "random_entry_mean_net_all_in": -18.7237, "random_entry_percentile": 0.61,
        "target_capture_dominates": False, "beats_buy_and_hold": False,
        "beats_random_entry_mean": True, "net_all_in_positive": False,
        "per_regime_net_all_in": {"bull": -17.4672, "bear": 2.2737,
                                  "chop": -0.3854},
        "forward_oos_net_all_in": -2.0319, "in_sample_net_all_in": -13.547,
    },
    "1.5r": {
        "trade_count": 346, "hit": 74, "horizon": 170, "horizon_exit_share": 0.4913,
        "net_r_total_all_in": 1.2914, "net_r_mean_all_in": 0.0037,
        "max_drawdown_r_all_in": 11.301, "worst_losing_streak": 7,
        "random_entry_mean_net_all_in": -12.418, "random_entry_percentile": 0.835,
        "target_capture_dominates": False, "beats_buy_and_hold": False,
        "beats_random_entry_mean": True, "net_all_in_positive": True,
        "per_regime_net_all_in": {"bull": -3.8218, "bear": 0.8475,
                                  "chop": 4.2658},
        "forward_oos_net_all_in": -3.7161, "in_sample_net_all_in": 5.0075,
    },
    "2r": {
        "trade_count": 346, "hit": 53, "horizon": 191, "horizon_exit_share": 0.552,
        "net_r_total_all_in": 13.544, "net_r_mean_all_in": 0.0391,
        "max_drawdown_r_all_in": 12.636, "worst_losing_streak": 7,
        "random_entry_mean_net_all_in": -8.6951, "random_entry_percentile": 0.905,
        "target_capture_dominates": False, "beats_buy_and_hold": False,
        "beats_random_entry_mean": True, "net_all_in_positive": True,
        "per_regime_net_all_in": {"bull": 3.249, "bear": 2.2011, "chop": 8.0939},
        "forward_oos_net_all_in": -3.7161, "in_sample_net_all_in": 17.2601,
    },
}

ANY_VARIANT_PASSES_ALL_DECISIVE_GATES = False
STRUCTURAL_REJECTION_PRESSURE = True

DECISIVE_GATE_RESULTS = {
    "net_after_costs_positive_any_variant": True,        # 1.5R/2R positive
    "beats_buy_and_hold_any_variant": False,             # all lose to B&H
    "beats_random_entry_any_variant": True,              # all beat random (notable)
    "regime_symmetry_all_positive_any_variant": True,    # 2R symmetric
    "bear_not_structurally_weak_any_variant": True,      # bear positive all variants
    "forward_oos_2026_positive_any_variant": False,
    "target_capture_dominates_any_variant": False,
    "horizon_exit_within_cap_all_variants": False,       # 2R = 55.2% > 50%
}

# Notable POSITIVES recorded honestly (do NOT make it pass; the human sees them).
NOTABLE_POSITIVES = {
    "beats_random_entry_all_variants": True,            # pctl 0.61 / 0.835 / 0.905
    "net_positive_after_costs_1_5r_and_2r": True,
    "regime_symmetric_at_2r": True,
    "bear_regime_net_positive_all_variants": True,
}

# Hard rejection warnings, evaluated honestly.
REJECTION_WARNINGS = {
    "loses_to_buy_and_hold_all_variants": True,          # TRIGGERED (carry)
    "negative_forward_oos_2026_all_variants": True,      # TRIGGERED
    "target_capture_does_not_dominate_all_variants": True,  # TRIGGERED
    "net_negative_at_1r": True,
    "beats_random_but_loses_to_buy_and_hold_is_carry_signature": True,
}

HONEST_CAVEATS = (
    "Out-of-sample real-candle replay of the 347 frozen labels; not a live "
    "result and not a profitability claim.",
    "NOTABLE: C14 is the FIRST candidate to BEAT a matched random-entry baseline "
    "for every variant (percentile 0.61 / 0.835 / 0.905) -- the conviction-bar "
    "SIGNAL adds genuine timing value over random; and 1.5R/2R are net-positive "
    "after 37 bps (2R +13.5R), with 2R regime-symmetric (bull/bear/chop all "
    "positive).",
    "BUT it LOSES to buy-and-hold for EVERY variant (B&H +39.7R vs -15.6R / "
    "+1.3R / +13.5R): the absolute return is market CARRY that passive holding "
    "captures more cheaply -- 'beats random but loses to buy-and-hold' is the "
    "carry signature.",
    "Forward-OOS 2026 is NET-NEGATIVE for every variant (-2.0R / -3.7R / -3.7R) "
    "-- the edge does not continue forward.",
    "Target capture does NOT dominate (hits 53-108 vs horizon exits 140-191); "
    "1R/1.5R are within the 50% horizon cap but 2R is horizon-dominated (55%).",
    "Per the pre-registered C14 spec (must beat buy-and-hold AND random-entry, "
    "forward-OOS continuation, target-capture dominance, horizon cap), no "
    "variant passes ALL the decisive gates -> STRUCTURAL REJECTION PRESSURE. "
    "The reject/keep decision is the human's at the next gate.",
)

CLAIM_LOCKS = (
    "no_profitability_claim", "no_paper_approval", "no_live_approval",
    "no_execution_approval", "no_winner_wording",
    "no_promotion_decision_made_by_this_gate",
    "no_relabel_authorized_by_this_gate",
    "loses_to_buy_and_hold_disclosed",
    "negative_forward_oos_disclosed",
    "target_capture_failure_disclosed",
    "beats_random_entry_disclosed_as_notable_positive",
    "carry_signature_disclosed",
    "structural_rejection_pressure_disclosed",
)

C14RR_LABEL = (
    "C14 REPLAY RESULTS (READ-ONLY, RESEARCH ONLY). FEE+SLIPPAGE HONEST (37 BPS "
    "ALL-IN). OUT-OF-SAMPLE REAL-CANDLE, BTC/ETH/SOL 1D, 347 LABELS, <=2-BAR "
    "HOLD. BEATS RANDOM-ENTRY (FIRST CANDIDATE TO) BUT LOSES TO BUY-AND-HOLD "
    "(CARRY), FORWARD-OOS 2026 NEGATIVE, TARGET CAPTURE DOES NOT DOMINATE -> "
    "STRUCTURAL REJECTION PRESSURE. NOT A PROFITABILITY CLAIM. NOT AN APPROVAL "
    "FOR PAPER OR LIVE."
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


def get_candidate_14_replay_review_label() -> str:
    return C14RR_LABEL


def get_candidate_14_replay_review_next_action() -> str:
    return NEXT_REQUIRED_ACTION


def build_c14_replay_review(repo_root: Any = ".",
                            tracked_paths: list | None = None
                            ) -> dict[str, Any]:
    """Assemble the C14 replay-results review record. Chain-gated on the pushed
    C14 labels review (must return FROZEN). Pure; no I/O."""
    record: dict[str, Any] = {
        "schema_version": C14RR_SCHEMA_VERSION,
        "label": C14RR_LABEL, "mode": C14RR_MODE,
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
        "notable_positives": dict(NOTABLE_POSITIVES),
        "any_variant_passes_all_decisive_gates":
            ANY_VARIANT_PASSES_ALL_DECISIVE_GATES,
        "structural_rejection_pressure": STRUCTURAL_REJECTION_PRESSURE,
        "rejection_warnings": dict(REJECTION_WARNINGS),
        "rejection_warnings_triggered": sorted(
            k for k, v in REJECTION_WARNINGS.items() if v
            and k != "beats_random_but_loses_to_buy_and_hold_is_carry_signature"),
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

    labels = build_c14_labels_review(repo_root, tracked_paths or [])
    record["labels_review_verdict"] = labels.get("verdict")
    if labels.get("verdict") != VERDICT_C14L_FROZEN:
        record["verdict"] = VERDICT_C14RR_BLOCKED
        record["blockers"].append("labels_review_not_frozen")
        return record
    if labels.get("expected_labels_sha256") != EXPECTED_LABELS_SHA256:
        record["verdict"] = VERDICT_C14RR_BLOCKED
        record["blockers"].append("labels_sha_pin_mismatch")
        return record

    tracked = set(tracked_paths or [])
    if LEDGER_PATH in tracked or SUMMARY_PATH in tracked:
        record["verdict"] = VERDICT_C14RR_BLOCKED
        record["blockers"].append("replay_artifact_tracked")
        return record

    record["verdict"] = VERDICT_C14RR_FROZEN
    return record


def validate_c14_replay_review(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. FROZEN is valid only when the SHA pins, the cost
    basis, the honest decisive findings (loses to buy-and-hold, negative
    forward-OOS, target-capture failure, structural rejection pressure, no
    variant passes) and the beats-random-entry positive are intact. The negative
    findings cannot be silently flipped to a pass."""
    failures: list = []
    if record.get("verdict") != VERDICT_C14RR_FROZEN:
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
    if record.get("labels_review_verdict") != VERDICT_C14L_FROZEN:
        failures.append("labels_review_verdict_tampered")

    if record.get("all_in_round_trip_bps") != ALL_IN_ROUND_TRIP_BPS:
        failures.append("all_in_cost_tampered")
    if (record.get("fee_round_trip_bps", 0)
            + record.get("slippage_round_trip_bps", 0)
            != ALL_IN_ROUND_TRIP_BPS):
        failures.append("cost_components_do_not_sum")

    # Honest decisive findings cannot be flipped.
    if record.get("any_variant_passes_all_decisive_gates") is not False:
        failures.append("variant_pass_flag_tampered")
    if record.get("structural_rejection_pressure") is not True:
        failures.append("structural_rejection_pressure_cleared")
    dg = record.get("decisive_gate_results") or {}
    if dg.get("beats_buy_and_hold_any_variant") is not False:
        failures.append("beats_buy_and_hold_flipped")
    if dg.get("forward_oos_2026_positive_any_variant") is not False:
        failures.append("forward_oos_flipped")
    if dg.get("target_capture_dominates_any_variant") is not False:
        failures.append("target_capture_flipped")
    # the beats-random-entry positive must remain disclosed (honest both ways)
    if dg.get("beats_random_entry_any_variant") is not True:
        failures.append("beats_random_positive_cleared")
    rw = record.get("rejection_warnings") or {}
    for key in ("loses_to_buy_and_hold_all_variants",
                "negative_forward_oos_2026_all_variants",
                "target_capture_does_not_dominate_all_variants"):
        if rw.get(key) is not True:
            failures.append("rejection_warning_cleared_%s" % key)

    # Per-variant: lose-to-B&H + negative forward-OOS + target-capture-fails.
    agg = record.get("replay_aggregates") or {}
    bh = record.get("buy_and_hold_net_all_in_total")
    for name in ("1r", "1.5r", "2r"):
        v = agg.get(name) or {}
        if v.get("beats_buy_and_hold") is not False:
            failures.append("variant_beats_bh_flipped_%s" % name)
        if not (isinstance(v.get("net_r_total_all_in"), (int, float))
                and isinstance(bh, (int, float))
                and v["net_r_total_all_in"] < bh):
            failures.append("variant_not_below_bh_%s" % name)
        if not (isinstance(v.get("forward_oos_net_all_in"), (int, float))
                and v["forward_oos_net_all_in"] < 0):
            failures.append("variant_forward_oos_sign_tampered_%s" % name)
        if v.get("target_capture_dominates") is not False:
            failures.append("variant_target_capture_flipped_%s" % name)
        if v.get("beats_random_entry_mean") is not True:
            failures.append("variant_beats_random_cleared_%s" % name)

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
                     "loses_to_buy_and_hold_disclosed",
                     "negative_forward_oos_disclosed",
                     "carry_signature_disclosed",
                     "structural_rejection_pressure_disclosed"):
        if required not in (record.get("claim_locks") or []):
            failures.append("claim_lock_missing_%s" % required)

    for banned in ("APPROVE", "PAPER", "LIVE", "EXECUTE", "BROKER", "ORDER",
                   "FETCH", "UNLOCK"):
        if banned in NEXT_REQUIRED_ACTION.upper():
            failures.append("next_action_banned_token_%s" % banned)

    return {"valid": not failures, "failures": failures}
