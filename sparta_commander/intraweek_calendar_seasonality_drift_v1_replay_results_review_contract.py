"""Candidate #10 (INTRAWEEK_CALENDAR_SEASONALITY_DRIFT_V1) fee+slippage-honest
replay-results review / evidence-freeze contract.

RESEARCH ONLY. This module reviews the FROZEN, SHA-pinned replay artifacts
produced by tools/c10_fee_honest_replay_156_once.py against the pushed,
chain-gated C10 detector-labels review. It is a pure, in-memory evidence record
-- it performs NO file I/O, NO network, NO trading, NO PnL execution, NO
relabel, NO edit-token use, and NO downstream gate unlock. It does NOT claim
profitability. It freezes the replay aggregates for human review and locks every
downstream gate.

Chain gate: build_c10_replay_review() requires build_c10_labels_review() to
return the FROZEN labels verdict; any broken upstream gate short-circuits to a
BLOCKED verdict carrying a named blocker.

Replay assumptions reviewed here (locked at the runner):
  * Long-only, BTCUSD 1d, fixed 5-bar horizon exit; 1.5*ATR(14) structure stop;
    target variants 2R/3R/4R; entry at the trigger-bar close.
  * MISS = low<=stop -> -1R; HIT = high>=target -> +variant_r; same-bar straddle
    = STOP FIRST (conservative) -> -1R; otherwise HORIZON exit at the 5th bar
    close -> (exit_close-entry)/stop_distance. Every outcome is decisive.
  * Costs as R-units of the setup stop distance: 27 bps round-trip fee (locked)
    + 10 bps round-trip slippage (declared conservative 5 bps/side haircut) =
    37 bps all-in. net_r_all_in = gross_r - (37 / stop_distance_bps).
  * Replay-time same-symbol non-overlap = reduce-or-keep-only (0 drops; Friday
    spacing 7d > 5-bar hold).
"""
from __future__ import annotations

from typing import Any

from sparta_commander.intraweek_calendar_seasonality_drift_v1_real_candle_labels_review_contract import (  # noqa: E501
    VERDICT_C10L_FROZEN,
    build_c10_labels_review,
)

C10RR_SCHEMA_VERSION = 1
C10RR_MODE = "RESEARCH_ONLY"
CANDIDATE_ID = "INTRAWEEK_CALENDAR_SEASONALITY_DRIFT_V1"
CANDIDATE_FAMILY = "intraweek_calendar_seasonality_drift"
SYMBOL = "BTCUSD"
TIMEFRAME = "1d"
DIRECTION = "long_only"
SAMPLE_TAG = "2023-01-01_2025-12-31"

VERDICT_C10RR_FROZEN = "C10_REPLAY_RESULTS_FROZEN_FOR_HUMAN_REVIEW"
VERDICT_C10RR_BLOCKED = "C10_REPLAY_RESULTS_BLOCKED"
NEXT_REQUIRED_ACTION = "HUMAN_DECISION_C10_PROMOTE_TO_ROBUSTNESS_OR_REJECT"

HEAD_AT_LABELS_REVIEW = "0de0f7c1089a9650204a786a983502b34b0417be"

EXPECTED_LABELS_SHA256 = (
    "8276e9a6ee9bd9b89ff28a41f5c160973934bcc03ad8c5371095e62fb8f9c47d")
EXPECTED_SOURCE_SHA256 = (
    "043fb722b35e738a0c2050f9388defc7ca99322ed2f153989746ee28bbb89b88")
EXPECTED_REPLAY_LEDGER_SHA256 = (
    "4675f0fd28fc94db9504294a94186cff2576422802bc7f8fb38199aa8251c3ba")
EXPECTED_REPLAY_SUMMARY_SHA256 = (
    "78ca7dafcd3fe46ec252a43fa4153ec48cd32d2878cd7bebb54ebd5dad839d61")

LEDGER_PATH = ("data/intraweek_calendar_seasonality_c10/replay_results/"
               "c10_replay_ledger_2023-01-01_2025-12-31.json")
SUMMARY_PATH = ("data/intraweek_calendar_seasonality_c10/replay_results/"
                "c10_replay_summary_2023-01-01_2025-12-31.json")

FEE_ROUND_TRIP_BPS = 27.0
SLIPPAGE_ROUND_TRIP_BPS = 10.0
ALL_IN_ROUND_TRIP_BPS = 37.0
HOLDING_HORIZON_BARS = 5
ACCEPTED_INPUT_COUNT = 156

# Frozen replay aggregates (from tools/c10_fee_honest_replay_156_once.py over
# the SHA-pinned inputs above). All R figures are out-of-sample; net_all_in is
# after 37 bps round-trip costs. Rounded for the record; the gitignored ledger
# carries full precision.
REPLAY_AGGREGATES = {
    "2r": {
        "trade_count": 156, "hit": 16, "miss": 30, "horizon": 110,
        "straddle": 0, "win_rate_net_all_in": 0.5, "hit_rate": 0.1026,
        "gross_r_total": 26.6833, "net_r_total_fee_only": 18.1399,
        "net_r_total_all_in": 14.9757, "net_r_mean_all_in": 0.096,
        "max_drawdown_r_all_in": 6.3406,
        "net_all_in_positive_full_sample": True,
        "per_year_net_all_in": {"2023": 11.1608, "2024": 7.1033,
                                "2025": -3.2884},
    },
    "3r": {
        "trade_count": 156, "hit": 8, "miss": 30, "horizon": 118,
        "straddle": 0, "win_rate_net_all_in": 0.5, "hit_rate": 0.0513,
        "gross_r_total": 34.1916, "net_r_total_fee_only": 25.6482,
        "net_r_total_all_in": 22.484, "net_r_mean_all_in": 0.1441,
        "max_drawdown_r_all_in": 7.1498,
        "net_all_in_positive_full_sample": True,
        "per_year_net_all_in": {"2023": 16.7943, "2024": 8.9788,
                                "2025": -3.2891},
    },
    "4r": {
        "trade_count": 156, "hit": 4, "miss": 30, "horizon": 122,
        "straddle": 0, "win_rate_net_all_in": 0.5, "hit_rate": 0.0256,
        "gross_r_total": 36.2306, "net_r_total_fee_only": 27.6872,
        "net_r_total_all_in": 24.5229, "net_r_mean_all_in": 0.1572,
        "max_drawdown_r_all_in": 7.1498,
        "net_all_in_positive_full_sample": True,
        "per_year_net_all_in": {"2023": 16.8332, "2024": 10.9788,
                                "2025": -3.2891},
    },
}

# Honest caveats -- this is NOT a profitability claim or an approval.
HONEST_CAVEATS = (
    "Out-of-sample replay only; not a live result and not a profitability "
    "claim.",
    "Every variant's full-sample net R is positive AFTER 37 bps all-in costs, "
    "but the edge is regime-dependent and DECAYS to NEGATIVE in 2025 for all "
    "three variants (regime_decay_2025).",
    "Single asset (BTCUSD) and a single weekday bucket (Friday); no "
    "cross-asset or cross-weekday robustness has been demonstrated.",
    "Horizon exits dominate (110-122 of 156); the edge is largely a 5-day "
    "holding drift, not target capture (hit rate 2.6-10.3%).",
    "Costs are conservative-but-modeled; a higher slippage assumption would "
    "erode the thin per-trade net mean (0.096-0.157 R).",
)

CLAIM_LOCKS = (
    "no_profitability_claim", "no_paper_approval", "no_live_approval",
    "no_execution_approval", "no_winner_wording",
    "no_promotion_decision_made_by_this_gate",
    "no_relabel_authorized_by_this_gate",
    "no_edit_token_applied_by_this_gate",
    "regime_decay_2025_disclosed",
    "single_asset_single_weekday_disclosed",
)

C10RR_LABEL = (
    "C10 REPLAY RESULTS (READ-ONLY, RESEARCH ONLY). "
    "FEE+SLIPPAGE HONEST (37 BPS ALL-IN). "
    "OUT-OF-SAMPLE 156 TRADES, 2023-2025, BTCUSD 1D FRIDAY DRIFT. "
    "NET POSITIVE AFTER COSTS FULL-SAMPLE BUT NEGATIVE IN 2025 (REGIME DECAY). "
    "NOT A PROFITABILITY CLAIM. NOT AN APPROVAL FOR PAPER OR LIVE."
)

_CAPABILITY_FLAGS_FALSE = (
    "runs_real_candle_detection", "runs_detection_now", "labels_now",
    "runs_replay_now", "runs_relabel", "relabels_now", "scores_live",
    "stages_data_now", "fetches_data", "calls_api", "uses_network",
    "uses_credentials", "uses_wallet", "uses_account", "connects_broker",
    "connects_exchange", "uses_real_money", "contains_order_logic",
    "contains_portfolio_allocation_logic", "starts_scheduler",
    "sends_notifications", "auto_commits", "auto_pushes",
    "creates_runners_now", "modifies_canonical_source",
    "modifies_detector_labels_artifacts", "modifies_replay_artifacts",
    "computes_live_pnl", "authorizes_paper_execution",
    "authorizes_micro_live", "authorizes_live_trading", "promotes_gate",
    "unlocks_downstream_gate", "unlocks_replay_now", "unlocks_relabel_now",
    "unlocks_edit_token_now", "claims_profitability", "claims_edge",
    "executes", "writes_files",
)


def get_candidate_10_replay_review_label() -> str:
    return C10RR_LABEL


def build_c10_replay_review(repo_root: Any,
                            tracked_paths: list) -> dict[str, Any]:
    """Assemble the C10 replay-results review record. Chain-gated on the pushed
    C10 detector-labels review (must return FROZEN). Pure; no I/O."""
    record: dict[str, Any] = {
        "schema_version": C10RR_SCHEMA_VERSION,
        "label": C10RR_LABEL, "mode": C10RR_MODE,
        "lane": "crypto_d1_auto_research",
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "symbol": SYMBOL, "timeframe": TIMEFRAME, "direction": DIRECTION,
        "sample_tag": SAMPLE_TAG,
        "verdict": None, "blockers": [], "failures": [],
        "head_at_labels_review": HEAD_AT_LABELS_REVIEW,
        "expected_labels_sha256": EXPECTED_LABELS_SHA256,
        "expected_source_sha256": EXPECTED_SOURCE_SHA256,
        "expected_replay_ledger_sha256": EXPECTED_REPLAY_LEDGER_SHA256,
        "expected_replay_summary_sha256": EXPECTED_REPLAY_SUMMARY_SHA256,
        "ledger_path": LEDGER_PATH, "summary_path": SUMMARY_PATH,
        "fee_round_trip_bps": FEE_ROUND_TRIP_BPS,
        "slippage_round_trip_bps": SLIPPAGE_ROUND_TRIP_BPS,
        "all_in_round_trip_bps": ALL_IN_ROUND_TRIP_BPS,
        "holding_horizon_bars": HOLDING_HORIZON_BARS,
        "accepted_input_count": ACCEPTED_INPUT_COUNT,
        "replay_aggregates": REPLAY_AGGREGATES,
        "honest_caveats": list(HONEST_CAVEATS),
        "claim_locks": list(CLAIM_LOCKS),
        "all_variants_net_positive_after_costs_full_sample": True,
        "any_variant_net_positive_in_2025": False,
        "regime_decay_2025": True,
        "is_replay_review_only": True,
        "current_loop_stage": "replay_evaluation_review",
        "human_review_required": True,
        "relabel_gate_locked": True,
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
        "no_api": True, "no_network": True, "no_fetch": True,
        "no_notification": True, "no_scheduler": True, "no_relabel": True,
        "no_detector_change": True, "no_edit_token_use": True,
        "no_profitability_claim": True, "no_downstream_gate_unlock": True,
    }

    # Chain gate: the pushed labels-review must certify FROZEN.
    labels = build_c10_labels_review(repo_root, tracked_paths)
    record["labels_review_verdict"] = labels["verdict"]
    if labels["verdict"] != VERDICT_C10L_FROZEN:
        record["verdict"] = VERDICT_C10RR_BLOCKED
        record["blockers"].append("labels_review_not_frozen")
        return record
    if labels.get("expected_labels_sha256") != EXPECTED_LABELS_SHA256:
        record["verdict"] = VERDICT_C10RR_BLOCKED
        record["blockers"].append("labels_sha_pin_mismatch")
        return record

    # The two replay artifacts must stay UNTRACKED (gitignored data).
    tracked = set(tracked_paths or [])
    if LEDGER_PATH in tracked or SUMMARY_PATH in tracked:
        record["verdict"] = VERDICT_C10RR_BLOCKED
        record["blockers"].append("replay_artifact_tracked")
        return record

    record["verdict"] = VERDICT_C10RR_FROZEN
    return record


def validate_c10_replay_review(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. FROZEN is valid only when verdict + locks +
    cost basis + decay disclosure + capability locks are all intact."""
    failures: list = []
    if record.get("verdict") != VERDICT_C10RR_FROZEN:
        failures.append("verdict_not_frozen")
    if record.get("blockers"):
        failures.append("has_blockers")

    for field, expected in (
            ("expected_labels_sha256", EXPECTED_LABELS_SHA256),
            ("expected_source_sha256", EXPECTED_SOURCE_SHA256),
            ("expected_replay_ledger_sha256", EXPECTED_REPLAY_LEDGER_SHA256),
            ("expected_replay_summary_sha256", EXPECTED_REPLAY_SUMMARY_SHA256)):
        v = record.get(field)
        if not isinstance(v, str) or len(v) != 64 or v != expected:
            failures.append("bad_sha_%s" % field)
    if record.get("head_at_labels_review") != HEAD_AT_LABELS_REVIEW:
        failures.append("head_at_labels_review_tampered")

    if record.get("all_in_round_trip_bps") != ALL_IN_ROUND_TRIP_BPS:
        failures.append("all_in_cost_tampered")
    if (record.get("fee_round_trip_bps", 0)
            + record.get("slippage_round_trip_bps", 0)
            != ALL_IN_ROUND_TRIP_BPS):
        failures.append("cost_components_do_not_sum")

    # Honest framing must be intact: net-positive full sample but decayed 2025.
    if record.get("all_variants_net_positive_after_costs_full_sample") is not True:
        failures.append("full_sample_positive_flag_tampered")
    if record.get("any_variant_net_positive_in_2025") is not False:
        failures.append("2025_positive_flag_tampered")
    if record.get("regime_decay_2025") is not True:
        failures.append("regime_decay_disclosure_removed")

    agg = record.get("replay_aggregates") or {}
    for name in ("2r", "3r", "4r"):
        v = agg.get(name) or {}
        if v.get("trade_count") != ACCEPTED_INPUT_COUNT:
            failures.append("trade_count_tampered_%s" % name)
        if v.get("net_all_in_positive_full_sample") is not True:
            failures.append("full_sample_sign_tampered_%s" % name)
        py = v.get("per_year_net_all_in") or {}
        if not (isinstance(py.get("2025"), (int, float)) and py["2025"] < 0):
            failures.append("2025_decay_sign_tampered_%s" % name)

    locks = record.get("scope_locks") or {}
    for key, val in locks.items():
        if val is not True:
            failures.append("scope_lock_false_%s" % key)
    for key in ("relabel_gate_locked", "paper_trading_gate_locked",
                "micro_live_gate_locked", "live_gate_locked",
                "human_review_required", "is_replay_review_only"):
        if record.get(key) is not True:
            failures.append("gate_flag_tampered_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    if "no_profitability_claim" not in (record.get("claim_locks") or []):
        failures.append("no_profitability_claim_lock_missing")
    if "regime_decay_2025_disclosed" not in (record.get("claim_locks") or []):
        failures.append("regime_decay_lock_missing")

    nra = record.get("next_required_action", "")
    for banned in ("PROMOTE_NOW", "APPROVE", "PAPER", "LIVE", "EXECUTE",
                   "BROKER", "ORDER", "FETCH", "UNLOCK"):
        if banned in NEXT_REQUIRED_ACTION.upper() and banned != "PROMOTE":
            failures.append("next_action_banned_token_%s" % banned)

    return {"valid": not failures, "failures": failures}


def get_candidate_10_replay_review_next_action() -> str:
    return NEXT_REQUIRED_ACTION
