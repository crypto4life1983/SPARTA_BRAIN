"""Candidate #15 -- slow_vol_targeted_time_series_momentum_v1 -- FEE-HONEST REPLAY
RESULTS REVIEW (PURE, RESEARCH ONLY).

Pins the FROZEN fee-honest replay artifact produced by
tools/c15_fee_honest_replay_once.py (replayed READ-ONLY over the SHA-pinned frozen
C15 labels + frozen sources) and records the decisive-gate outcome. R-unit
normalized; 37 bps all-in (27 fee + 10 slippage) applied to every trade and NOT
droppable; matched buy-and-hold + deterministic random-entry (fixed seed, 200
resamples) baselines.

It is chain-gated on the frozen C15 labels review. It does NOTHING with real data
here: it does NOT re-detect, NOT relabel, NOT re-run replay, NOT optimize, NOT run
robustness / portfolio, NOT write files, NOT stage / commit / push, and NOT touch
any paper / live / broker / order surface. It only PINS the SHAs + the replay
aggregates + the decisive-gate results.

HONEST OUTCOME (FROZEN): the strategy is net-POSITIVE full-sample (+111.03 R) and
BEATS the random-entry baseline at the 100th percentile (a real timing signal) --
BUT it LOSES to matched buy-and-hold (111.03 vs 286.53 R), the SHORT side is
net-negative (-1.16 R; the edge is essentially long-only), and the BEAR regime is
net-negative (-0.91 R). 3 of the 8 decisive gates fail -> REJECT_C15. This is the
same carry signature as C14: beats random, loses to buy-and-hold. NOT a
profitability claim.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.slow_vol_targeted_time_series_momentum_v1_real_candle_labels_review_contract as _l15  # noqa: E501

R15_SCHEMA_VERSION = 1
R15_MODE = "RESEARCH_ONLY"
R15_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = _l15.CANDIDATE_ID
CANDIDATE_FAMILY = _l15.CANDIDATE_FAMILY
CANDIDATE_NAME = _l15.CANDIDATE_NAME
SYMBOLS = ("BTCUSD", "ETHUSD", "SOLUSD")
REGIMES = ("bull", "bear", "chop")
SIDES = ("long", "short")

VERDICT_C15RR_FROZEN = "C15_REPLAY_RESULTS_FROZEN_FOR_HUMAN_REVIEW"

# --- cost model (not droppable) ---------------------------------------------
FEE_ROUND_TRIP_BPS = 27.0
SLIPPAGE_ROUND_TRIP_BPS = 10.0
ALL_IN_ROUND_TRIP_BPS = 37.0

# --- pinned artifact provenance ---------------------------------------------
HEAD_AT_LABELS_REVIEW = "36df56a32c20bd8e7d50b482450d281ddf1b0e00"
LEDGER_PATH = ("data/slow_vol_targeted_time_series_momentum_c15/"
               "replay_results/c15_replay_ledger.json")
SUMMARY_PATH = ("data/slow_vol_targeted_time_series_momentum_c15/"
                "replay_results/c15_replay_summary.json")
EXPECTED_LABELS_SHA256 = _l15.EXPECTED_LABELS_SHA256
EXPECTED_LEDGER_SHA256 = (
    "47abc515f92ec655a370286d16917873af060107564b540e1826f14e208d424c")
EXPECTED_SUMMARY_SHA256 = (
    "24ca1b852c0930e1ea100ad0938ce6cfb0c8dcba5de58447b9c40ec30177929e")
EXPECTED_SOURCE_SHA256 = dict(_l15.EXPECTED_SOURCE_SHA256)

# --- pinned frozen replay aggregates ----------------------------------------
TRADE_COUNT = 200
NET_R_TOTAL_ALL_IN = 111.034046
GROSS_R_TOTAL_PRE_COST = 115.94021
PER_ASSET_NET_R = {"BTCUSD": 41.262908, "ETHUSD": 35.369613, "SOLUSD": 34.401525}
PER_REGIME_NET_R = {"bull": 78.211007, "bear": -0.914353, "chop": 33.737392}
PER_SIDE_NET_R = {"long": 112.191436, "short": -1.15739}
FORWARD_OOS_NET_R = 0.269899
FORWARD_OOS_TRADE_COUNT = 5
BUY_AND_HOLD_NET_R_TOTAL = 286.528781
BUY_AND_HOLD_NET_R_PER_ASSET = {"BTCUSD": 129.83571, "ETHUSD": 71.004784,
                                "SOLUSD": 85.688287}
RANDOM_ENTRY_SEED = 20260617
RANDOM_ENTRY_RESAMPLES = 200
RANDOM_ENTRY_MEAN_NET_R = -4.309887
RANDOM_ENTRY_PERCENTILE = 1.0
AVG_HOLD_BARS = 23.01

TURNOVER_MIN_AVG_HOLD = 5.0

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "re_detects", "relabels", "re_runs_replay",
    "runs_labels", "runs_backtest", "optimizes_parameters", "runs_robustness",
    "runs_portfolio_compute", "fetches_data", "reads_real_data", "mutates_data",
    "stages_data", "auto_commits", "auto_pushes", "drops_cost_model",
    "modifies_scheduler", "sends_notifications", "calls_api", "uses_network",
    "uses_credentials", "connects_broker", "connects_exchange", "uses_real_money",
    "places_orders", "contains_order_logic", "paper_trading", "live_trading",
    "deploys_capital", "promotes_gate", "unlocks_downstream_gate", "skips_any_gate",
    "uses_one_edit_allowance", "advances_without_human_approval",
    "claims_profitability", "claims_edge", "passes_on_gross_only",
    "crosses_into_forbidden_gate",
)


def evaluate_decision_gates(m: dict) -> dict[str, Any]:
    """PURE decision-gate evaluation over a replay-metrics dict. ALL gates are
    NET-based (37 bps applied); a gross-only positive can NEVER pass because the
    net gates (net-positive, beats-buy-and-hold) use the net total. Returns the
    per-gate booleans + all_pass + the ADVANCE/REJECT outcome."""
    per_regime = m.get("per_regime_net_r") or {}
    per_asset = m.get("per_asset_net_r") or {}
    per_side = m.get("per_side_net_r") or {}
    gates = {
        "full_sample_net_positive": m.get("net_r_total_all_in", 0) > 0,
        "forward_oos_net_positive": m.get("forward_oos_net_r", 0) > 0,
        "no_single_regime_dependence": all(
            per_regime.get(r, -1) > 0 for r in REGIMES),
        "no_single_asset_dependence": all(
            per_asset.get(s, -1) > 0 for s in SYMBOLS),
        "no_one_sided_side_fragility": all(
            per_side.get(sd, -1) > 0 for sd in SIDES),
        "beats_buy_and_hold":
            m.get("net_r_total_all_in", 0) > m.get("buy_and_hold_net_r_total", 0),
        "beats_random_entry":
            m.get("net_r_total_all_in", 0) > m.get("random_entry_mean_net_r", 0),
        "turnover_sane_for_slow_strategy":
            m.get("avg_hold_bars", 0) >= TURNOVER_MIN_AVG_HOLD,
    }
    all_pass = all(gates.values())
    return {"gates": gates, "all_pass": all_pass,
            "decisive_outcome": "ADVANCE_C15" if all_pass else "REJECT_C15"}


def _pinned_metrics() -> dict[str, Any]:
    return {
        "net_r_total_all_in": NET_R_TOTAL_ALL_IN,
        "gross_r_total_pre_cost": GROSS_R_TOTAL_PRE_COST,
        "forward_oos_net_r": FORWARD_OOS_NET_R,
        "per_asset_net_r": dict(PER_ASSET_NET_R),
        "per_regime_net_r": dict(PER_REGIME_NET_R),
        "per_side_net_r": dict(PER_SIDE_NET_R),
        "buy_and_hold_net_r_total": BUY_AND_HOLD_NET_R_TOTAL,
        "random_entry_mean_net_r": RANDOM_ENTRY_MEAN_NET_R,
        "avg_hold_bars": AVG_HOLD_BARS,
    }


def get_candidate_15_replay_review_label() -> str:
    return (
        "Candidate #15 slow_vol_targeted_time_series_momentum_v1 fee-honest replay "
        "results review (READ-ONLY, RESEARCH ONLY, PURE). R-unit net of 37 bps "
        "all-in; matched buy-and-hold + deterministic random-entry baselines. "
        "Honest outcome: net-positive and beats random (real timing signal) but "
        "LOSES to buy-and-hold, short side and bear regime net-negative -> 3/8 "
        "decisive gates fail -> REJECT_C15. NOT A PROFITABILITY CLAIM. NOT a "
        "paper/live-readiness claim.")


def get_candidate_15_replay_review_next_action() -> str:
    return "HUMAN_DECISION_C15_REJECT_KEEP_ON_RECORD_OR_REVIEW"


def build_c15_replay_review(repo_root: Any = ".",
                            tracked_paths: list | None = None) -> dict[str, Any]:
    """Assemble the frozen C15 replay-results review record. Pure; no I/O; pins
    SHAs + aggregates + decisive-gate results; chain-gated on the frozen labels
    review."""
    labels = _l15.build_c15_labels_review(repo_root, tracked_paths)
    labels_valid = _l15.validate_c15_labels_review(labels)["valid"]
    decision = evaluate_decision_gates(_pinned_metrics())

    blockers: list = []
    if not labels_valid:
        blockers.append("c15_labels_review_invalid")
    if labels.get("verdict") != _l15.VERDICT_C15L_FROZEN:
        blockers.append("c15_labels_review_not_frozen")

    record: dict[str, Any] = {
        "schema_version": R15_SCHEMA_VERSION, "mode": R15_MODE, "lane": R15_LANE,
        "label": get_candidate_15_replay_review_label(),
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "candidate_name": CANDIDATE_NAME,
        "is_replay_review_only": True,
        "blockers": blockers,
        "verdict": (VERDICT_C15RR_FROZEN if not blockers
                    else "C15_REPLAY_RESULTS_BLOCKED"),
        # chain provenance
        "labels_review_verdict": labels.get("verdict"),
        "labels_review_valid": labels_valid,
        # pinned artifact provenance
        "head_at_labels_review": HEAD_AT_LABELS_REVIEW,
        "ledger_path": LEDGER_PATH, "summary_path": SUMMARY_PATH,
        "expected_labels_sha256": EXPECTED_LABELS_SHA256,
        "expected_ledger_sha256": EXPECTED_LEDGER_SHA256,
        "expected_summary_sha256": EXPECTED_SUMMARY_SHA256,
        "expected_source_sha256": dict(EXPECTED_SOURCE_SHA256),
        # cost model (not droppable)
        "fee_round_trip_bps": FEE_ROUND_TRIP_BPS,
        "slippage_round_trip_bps": SLIPPAGE_ROUND_TRIP_BPS,
        "all_in_round_trip_bps": ALL_IN_ROUND_TRIP_BPS,
        "r_unit_is_volatility_scale_invariant": True,
        # pinned aggregates
        "trade_count": TRADE_COUNT,
        "net_r_total_all_in": NET_R_TOTAL_ALL_IN,
        "gross_r_total_pre_cost": GROSS_R_TOTAL_PRE_COST,
        "per_asset_net_r": dict(sorted(PER_ASSET_NET_R.items())),
        "per_regime_net_r": dict(sorted(PER_REGIME_NET_R.items())),
        "per_side_net_r": dict(sorted(PER_SIDE_NET_R.items())),
        "forward_oos_net_r": FORWARD_OOS_NET_R,
        "forward_oos_trade_count": FORWARD_OOS_TRADE_COUNT,
        "buy_and_hold_net_r_total": BUY_AND_HOLD_NET_R_TOTAL,
        "buy_and_hold_net_r_per_asset": dict(sorted(
            BUY_AND_HOLD_NET_R_PER_ASSET.items())),
        "random_entry_seed": RANDOM_ENTRY_SEED,
        "random_entry_resamples": RANDOM_ENTRY_RESAMPLES,
        "random_entry_mean_net_r": RANDOM_ENTRY_MEAN_NET_R,
        "random_entry_percentile_of_strategy": RANDOM_ENTRY_PERCENTILE,
        "avg_hold_bars": AVG_HOLD_BARS,
        # decisive outcome
        "decisive_gate_results": decision["gates"],
        "all_decisive_gates_pass": decision["all_pass"],
        "decisive_outcome": decision["decisive_outcome"],
        "advance_recommended": decision["all_pass"],
        "structural_rejection_pressure": not decision["all_pass"],
        "gross_only_would_pass_diagnostic": GROSS_R_TOTAL_PRE_COST > 0,
        "gate_uses_net_not_gross": True,
        # honest framing both ways
        "notable_positives": [
            "full-sample net is POSITIVE after 37 bps (+111.03 R)",
            "BEATS the random-entry baseline at the 100th percentile "
            "(a real timing signal)",
            "all three assets are individually net-positive",
            "turnover is sane for a slow strategy (avg hold ~23 bars)",
            "forward-OOS 2026 is marginally net-positive (+0.27 R over 5 trades)",
        ],
        "rejection_reasons": [
            "LOSES to matched buy-and-hold in R units (111.03 vs 286.53) -- the "
            "carry signature: it does not beat simply holding",
            "SHORT side is net-NEGATIVE (-1.16 R): the edge is essentially "
            "long-only and one-sided fragile",
            "BEAR regime is net-NEGATIVE (-0.91 R): single-regime dependence on "
            "bull + chop",
        ],
        "honest_caveats": [
            "beats random but loses to buy-and-hold is the same CARRY SIGNATURE "
            "that rejected C14",
            "forward-OOS positivity rests on only 5 trades -- thin evidence",
        ],
        "claim_locks": [
            "no_profitability_claim", "loses_to_buy_and_hold_disclosed",
            "short_side_negative_disclosed", "bear_regime_negative_disclosed",
            "carry_signature_disclosed", "cost_model_not_droppable",
            "gates_use_net_not_gross",
        ],
        "human_review_required": True,
        "current_loop_stage": "fee_honest_replay_review",
        "next_required_action": get_candidate_15_replay_review_next_action(),
        # downstream gates locked
        "robustness_gate_locked": True, "relabel_gate_locked": True,
        "portfolio_gate_locked": True, "paper_trading_gate_locked": True,
        "live_gate_locked": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_data_fetch": True, "no_re_detect": True, "no_relabel": True,
        "no_re_replay": True, "no_parameter_optimization": True,
        "no_robustness": True, "no_portfolio_compute": True,
        "no_cost_drop": True, "no_gross_only_pass": True,
        "no_real_data_mutation": True, "no_stage": True, "no_commit": True,
        "no_push": True, "no_auto_commit": True, "no_auto_push": True,
        "no_scheduler_change": True, "no_broker": True, "no_credentials": True,
        "no_order_logic": True, "no_paper_trading": True, "no_live_trading": True,
        "no_gate_skip": True, "no_one_edit_invocation": True,
        "no_downstream_gate_unlock": True, "no_profitability_claim": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_c15_replay_review(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the review is research-only, replay-
    review-only, chain-gated on the frozen labels review, pins the exact SHAs +
    aggregates, keeps the 37 bps cost intact (NOT droppable), evaluates the gates
    on NET (never gross-only), preserves the negative findings AND the beats-random
    positive, records the honest REJECT outcome, locks downstream gates, and pins
    every capability flag False."""
    failures: list = []
    if record.get("mode") != R15_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_replay_review_only") is not True:
        failures.append("not_replay_review_only")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("verdict") != VERDICT_C15RR_FROZEN:
        failures.append("verdict_not_frozen")

    # chain gate
    if record.get("labels_review_valid") is not True:
        failures.append("labels_review_not_valid")
    if record.get("labels_review_verdict") != _l15.VERDICT_C15L_FROZEN:
        failures.append("labels_review_not_frozen")

    # SHA pins
    if record.get("expected_ledger_sha256") != EXPECTED_LEDGER_SHA256:
        failures.append("ledger_sha_tampered")
    if record.get("expected_summary_sha256") != EXPECTED_SUMMARY_SHA256:
        failures.append("summary_sha_tampered")
    if record.get("expected_labels_sha256") != EXPECTED_LABELS_SHA256:
        failures.append("labels_sha_tampered")

    # cost model not droppable
    if record.get("all_in_round_trip_bps") != 37.0:
        failures.append("cost_model_tampered")
    if (record.get("fee_round_trip_bps", 0)
            + record.get("slippage_round_trip_bps", 0)) != 37.0:
        failures.append("cost_split_tampered")

    # gates re-derived from the pinned aggregates must MATCH the record, on NET
    decision = evaluate_decision_gates({
        "net_r_total_all_in": record.get("net_r_total_all_in"),
        "forward_oos_net_r": record.get("forward_oos_net_r"),
        "per_asset_net_r": record.get("per_asset_net_r"),
        "per_regime_net_r": record.get("per_regime_net_r"),
        "per_side_net_r": record.get("per_side_net_r"),
        "buy_and_hold_net_r_total": record.get("buy_and_hold_net_r_total"),
        "random_entry_mean_net_r": record.get("random_entry_mean_net_r"),
        "avg_hold_bars": record.get("avg_hold_bars"),
    })
    if record.get("decisive_gate_results") != decision["gates"]:
        failures.append("gate_results_do_not_match_aggregates")
    if record.get("all_decisive_gates_pass") != decision["all_pass"]:
        failures.append("all_pass_flag_inconsistent")
    if record.get("decisive_outcome") != decision["decisive_outcome"]:
        failures.append("decisive_outcome_inconsistent")
    if record.get("gate_uses_net_not_gross") is not True:
        failures.append("gate_must_use_net")

    # honest outcome: this candidate REJECTS (do not flip the negatives)
    if record.get("all_decisive_gates_pass") is not False:
        failures.append("must_be_reject_all_gates_pass_set")
    if record.get("decisive_outcome") != "REJECT_C15":
        failures.append("decisive_outcome_not_reject")
    if record.get("advance_recommended") is not False:
        failures.append("advance_recommended_must_be_false")
    g = record.get("decisive_gate_results") or {}
    if g.get("beats_buy_and_hold") is not False:
        failures.append("beats_buy_and_hold_must_be_false")
    if g.get("no_one_sided_side_fragility") is not False:
        failures.append("side_fragility_must_be_disclosed")
    if g.get("no_single_regime_dependence") is not False:
        failures.append("regime_dependence_must_be_disclosed")
    # the genuine positive must remain disclosed (anti-tamper both ways)
    if g.get("beats_random_entry") is not True:
        failures.append("beats_random_positive_must_remain")

    # downstream gates locked
    for gate in ("robustness_gate_locked", "relabel_gate_locked",
                 "portfolio_gate_locked", "paper_trading_gate_locked",
                 "live_gate_locked"):
        if record.get(gate) is not True:
            failures.append("downstream_gate_unlocked_%s" % gate)

    locks = record.get("scope_locks") or {}
    for key in ("no_data_fetch", "no_re_detect", "no_relabel", "no_re_replay",
                "no_parameter_optimization", "no_robustness",
                "no_portfolio_compute", "no_cost_drop", "no_gross_only_pass",
                "no_commit", "no_push", "no_auto_commit", "no_auto_push",
                "no_broker", "no_order_logic", "no_paper_trading",
                "no_live_trading", "no_gate_skip"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
