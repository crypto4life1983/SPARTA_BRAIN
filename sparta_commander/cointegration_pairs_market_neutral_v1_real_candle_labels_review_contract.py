"""Candidate #16 -- cointegration_pairs_market_neutral_v1 -- REAL-CANDLE LABELS
REVIEW (PURE, RESEARCH ONLY).

Pins the FROZEN real-candle labels artifact produced by
tools/c16_real_candle_detection_once.py (rolling cointegration-pairs labeling over
the SHA-pinned local BTC/ETH/SOL 1d data) and records the labels-stage structural
verdict. A C16 label is a market-neutral pair-trade ENTRY (dollar/beta-neutral two
legs), non-overlapping per pair.

It is chain-gated on the frozen C16 detector synthetic dry-run. It does NOTHING
with real data here: NO re-detect, NO relabel, NO replay, NO PnL, NO cost, NO
baseline, NO robustness/portfolio, NO writes, NO stage/commit/push, NO paper/live/
broker/order surface. It only PINS the SHAs + aggregate counts and re-states the
structural verdict. Every capability flag is pinned False with a full scope_locks
set.

HONEST OUTCOME (FROZEN): the labels-stage STRUCTURAL gate is FAILED -- a
labels-stage STRUCTURAL REJECTION before any replay. Only 43 accepted labels
(< 100), every pair below 20 (ETHBTC 17 / SOLBTC 15 / SOLETH 11), the chop regime
below 20 (bull 18 / bear 21 / chop 4), AND the observed net beta (2.82) blows past
the 0.10 market-neutral cap -- the level-OLS hedge ratio is NOT return-beta-neutral
on real crypto pairs. Cointegration in crypto is intermittent, so valid entries
are too few AND the "market-neutral" construction does not hold out of sample.
This is the C13 structural-rejection class (too few labels) compounded by a
neutrality failure. NOT a profitability claim.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.cointegration_pairs_market_neutral_v1_detector_spec_dry_run_contract as _d16  # noqa: E501

L16_SCHEMA_VERSION = 1
L16_MODE = "RESEARCH_ONLY"
L16_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = _d16.CANDIDATE_ID
CANDIDATE_FAMILY = _d16.CANDIDATE_FAMILY
CANDIDATE_NAME = _d16.CANDIDATE_NAME
PAIR_UNIVERSE = tuple(_d16.PAIR_UNIVERSE)   # ETHBTC / SOLETH / SOLBTC

VERDICT_C16L_FROZEN = "C16_LABELS_FROZEN_FOR_HUMAN_REVIEW"

# --- pinned artifact provenance ---------------------------------------------
HEAD_AT_DETECTOR_DRY_RUN = "0c5f27a0e749f0842b99874b95d37f38f88a9887"
LABELS_PATH = ("data/cointegration_pairs_market_neutral_c16/"
               "detector_labels/c16_detector_labels.json")
SUMMARY_PATH = ("data/cointegration_pairs_market_neutral_c16/"
                "detector_labels/c16_detector_summary.json")
EXPECTED_LABELS_SHA256 = (
    "f7472619812158583110e12bf9de40704f350e08a12c3d8163f7f913de1b4c61")
EXPECTED_SUMMARY_SHA256 = (
    "8c091915a95ab0ac3e3fcdd69c6c073de156d8714e5b5c288aedaa97290aac5e")
EXPECTED_SOURCE_SHA256 = {
    "BTCUSD": "043fb722b35e738a0c2050f9388defc7ca99322ed2f153989746ee28bbb89b88",
    "ETHUSD": "1bfd0ca86137747f0fe4c3fb127b00dcbd4885bf76056dbc9c091a9d4681c1a3",
    "SOLUSD": "4716d4d124bd7d5327fdc4230f7b2eaea70085df88c182dd129232ce802c0113",
}

# --- pinned frozen aggregates -----------------------------------------------
ACCEPTED_LABEL_COUNT = 43
PER_PAIR = {"ETHBTC": 17, "SOLBTC": 15, "SOLETH": 11}
PER_REGIME = {"bull": 18, "bear": 21, "chop": 4}
FORWARD_OOS_LABEL_COUNT = 9
MAX_ABS_NET_BETA_OBSERVED = 2.824495

MIN_LABELS_TOTAL = 100
MIN_PER_PAIR = 20
MIN_PER_REGIME = 20
MAX_ABS_NET_BETA_CAP = _d16.MAX_ABS_NET_BETA   # 0.10

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "re_detects", "relabels", "runs_labels",
    "runs_replay", "runs_backtest", "computes_pnl", "applies_cost_model",
    "runs_baseline", "runs_robustness", "runs_portfolio_compute", "fetches_data",
    "reads_real_data", "mutates_data", "stages_data", "auto_commits", "auto_pushes",
    "modifies_scheduler", "sends_notifications", "calls_api", "uses_network",
    "uses_credentials", "connects_broker", "connects_exchange", "uses_real_money",
    "places_orders", "contains_order_logic", "paper_trading", "live_trading",
    "deploys_capital", "promotes_gate", "unlocks_downstream_gate", "skips_any_gate",
    "advances_without_human_approval", "claims_profitability", "claims_edge",
    "claims_market_neutral_holds", "crosses_into_forbidden_gate",
)


def _structural_verdict() -> dict[str, Any]:
    total_ok = ACCEPTED_LABEL_COUNT >= MIN_LABELS_TOTAL
    per_pair_ok = all(PER_PAIR.get(p, 0) >= MIN_PER_PAIR for p in PAIR_UNIVERSE)
    per_regime_ok = all(PER_REGIME.get(r, 0) >= MIN_PER_REGIME
                        for r in ("bull", "bear", "chop"))
    fwd_ok = FORWARD_OOS_LABEL_COUNT > 0
    net_beta_ok = MAX_ABS_NET_BETA_OBSERVED <= MAX_ABS_NET_BETA_CAP
    passed = total_ok and per_pair_ok and per_regime_ok and fwd_ok and net_beta_ok
    return {
        "total": ACCEPTED_LABEL_COUNT, "min_total": MIN_LABELS_TOTAL,
        "total_ok": total_ok,
        "per_pair": dict(sorted(PER_PAIR.items())), "min_per_pair": MIN_PER_PAIR,
        "per_pair_ok": per_pair_ok,
        "per_regime": dict(sorted(PER_REGIME.items())),
        "min_per_regime": MIN_PER_REGIME, "per_regime_ok": per_regime_ok,
        "forward_oos_label_count": FORWARD_OOS_LABEL_COUNT,
        "forward_oos_populated": fwd_ok,
        "max_abs_net_beta_observed": MAX_ABS_NET_BETA_OBSERVED,
        "max_abs_net_beta_cap": MAX_ABS_NET_BETA_CAP,
        "net_beta_within_cap": net_beta_ok,
        "passed": passed,
    }


def get_candidate_16_labels_review_label() -> str:
    return (
        "Candidate #16 cointegration_pairs_market_neutral_v1 real-candle labels "
        "review (READ-ONLY, RESEARCH ONLY, PURE). Pins the FROZEN entry-label "
        "artifact over SHA-pinned local BTC/ETH/SOL 1d data and the labels-stage "
        "STRUCTURAL verdict: REJECTED -- only 43 labels (< 100), every pair and the "
        "chop regime below 20, and observed net beta 2.82 above the 0.10 cap (the "
        "level-OLS hedge is not return-beta-neutral on real crypto pairs). NO "
        "replay, NO PnL, NO cost. NOT a profitability claim.")


def get_candidate_16_labels_review_next_action() -> str:
    return "HUMAN_DECISION_C16_REJECT_AT_LABELS_OR_REVIEW"


def build_c16_labels_review(repo_root: Any = ".",
                            tracked_paths: list | None = None) -> dict[str, Any]:
    """Assemble the frozen C16 real-candle labels review record. Pure; no I/O; pins
    SHAs + counts + the structural verdict; chain-gated on the frozen C16 detector
    dry-run."""
    dry = _d16.build_c16_detector_dry_run(repo_root, tracked_paths)
    dry_valid = _d16.validate_c16_detector_dry_run(dry)["valid"]
    sv = _structural_verdict()

    blockers: list = []
    if not dry_valid:
        blockers.append("c16_detector_dry_run_invalid")
    if dry.get("verdict") != "C16_DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW":
        blockers.append("c16_detector_dry_run_not_frozen")

    record: dict[str, Any] = {
        "schema_version": L16_SCHEMA_VERSION, "mode": L16_MODE, "lane": L16_LANE,
        "label": get_candidate_16_labels_review_label(),
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "candidate_name": CANDIDATE_NAME,
        "is_labels_review_only": True,
        "blockers": blockers,
        "verdict": (VERDICT_C16L_FROZEN if not blockers
                    else "C16_LABELS_BLOCKED"),
        # chain provenance
        "detector_dry_run_verdict": dry.get("verdict"),
        "detector_dry_run_valid": dry_valid,
        # pinned artifact provenance
        "head_at_detector_dry_run": HEAD_AT_DETECTOR_DRY_RUN,
        "labels_path": LABELS_PATH, "summary_path": SUMMARY_PATH,
        "expected_labels_sha256": EXPECTED_LABELS_SHA256,
        "expected_summary_sha256": EXPECTED_SUMMARY_SHA256,
        "expected_source_sha256": dict(EXPECTED_SOURCE_SHA256),
        # pinned frozen aggregates
        "pair_universe": list(PAIR_UNIVERSE),
        "label_definition":
            "market_neutral_pair_trade_entry_two_leg_non_overlapping",
        "labels_are_non_overlapping_by_construction": True,
        "accepted_label_count": ACCEPTED_LABEL_COUNT,
        "per_pair": dict(sorted(PER_PAIR.items())),
        "per_regime": dict(sorted(PER_REGIME.items())),
        "forward_oos_label_count": FORWARD_OOS_LABEL_COUNT,
        "max_abs_net_beta_observed": MAX_ABS_NET_BETA_OBSERVED,
        "max_abs_net_beta_cap": MAX_ABS_NET_BETA_CAP,
        # structural verdict -- HONEST REJECTION
        "structural_sample_size": sv,
        "structural_sample_size_passed": sv["passed"],
        "structural_rejection_pressure": not sv["passed"],
        "net_beta_within_cap": sv["net_beta_within_cap"],
        "rejection_reasons": [
            "INSUFFICIENT sample size: only 43 labels (< 100); every pair below 20 "
            "(ETHBTC 17 / SOLBTC 15 / SOLETH 11); chop regime below 20 (4) -- the "
            "C13 structural-rejection class",
            "MARKET-NEUTRAL construction FAILS out of sample: observed net beta "
            "2.82 >> 0.10 cap (the level-OLS hedge is not return-beta-neutral on "
            "real crypto pairs)",
            "cointegration in crypto is INTERMITTENT, so valid rolling-cointegrated "
            "entries are too rare to support a tradeable program",
        ],
        # cost model still reserved (no PnL here)
        "cost_model_reserved_for_replay": True,
        "cost_model_applied_here": False,
        "human_review_required": True,
        "current_loop_stage": "real_candle_labels_review",
        "next_required_action": get_candidate_16_labels_review_next_action(),
        # downstream gates locked
        "replay_gate_locked": True, "robustness_gate_locked": True,
        "portfolio_gate_locked": True, "paper_trading_gate_locked": True,
        "live_gate_locked": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_data_fetch": True, "no_re_detect": True, "no_relabel": True,
        "no_replay": True, "no_pnl": True, "no_cost_application": True,
        "no_baseline": True, "no_robustness": True, "no_portfolio_compute": True,
        "no_real_data_mutation": True, "no_parameter_fitting": True,
        "no_stage": True, "no_commit": True, "no_push": True,
        "no_auto_commit": True, "no_auto_push": True, "no_scheduler_change": True,
        "no_broker": True, "no_credentials": True, "no_order_logic": True,
        "no_paper_trading": True, "no_live_trading": True, "no_gate_skip": True,
        "no_downstream_gate_unlock": True, "no_profitability_claim": True,
        "no_market_neutral_claim": True, "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_c16_labels_review(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the review is research-only, labels-
    review-only, chain-gated on the frozen C16 detector dry-run, pins the exact
    SHAs + frozen aggregates, HONESTLY records the structural REJECTION (sample-size
    failed AND net-beta cap exceeded -> cannot be flipped to 'passed'), applies no
    PnL/cost, locks downstream gates, and pins every capability flag False."""
    failures: list = []
    if record.get("mode") != L16_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_labels_review_only") is not True:
        failures.append("not_labels_review_only")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("verdict") != VERDICT_C16L_FROZEN:
        failures.append("verdict_not_frozen")

    # chain gate
    if record.get("detector_dry_run_valid") is not True:
        failures.append("detector_dry_run_not_valid")
    if record.get("detector_dry_run_verdict") != (
            "C16_DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW"):
        failures.append("detector_dry_run_not_frozen")

    # SHA pins
    if record.get("expected_labels_sha256") != EXPECTED_LABELS_SHA256:
        failures.append("labels_sha_tampered")
    if record.get("expected_summary_sha256") != EXPECTED_SUMMARY_SHA256:
        failures.append("summary_sha_tampered")
    for s in ("BTCUSD", "ETHUSD", "SOLUSD"):
        if (record.get("expected_source_sha256") or {}).get(s) != \
                EXPECTED_SOURCE_SHA256[s]:
            failures.append("source_sha_tampered_%s" % s)

    # frozen aggregates
    if record.get("accepted_label_count") != ACCEPTED_LABEL_COUNT:
        failures.append("label_count_tampered")
    if record.get("per_pair") != dict(sorted(PER_PAIR.items())):
        failures.append("per_pair_tampered")
    if record.get("per_regime") != dict(sorted(PER_REGIME.items())):
        failures.append("per_regime_tampered")
    if record.get("max_abs_net_beta_observed") != MAX_ABS_NET_BETA_OBSERVED:
        failures.append("net_beta_observed_tampered")

    # HONEST structural rejection -- cannot be flipped to passed
    sv = record.get("structural_sample_size") or {}
    if sv.get("passed") is not False:
        failures.append("structural_gate_must_be_failed")
    if record.get("structural_sample_size_passed") is not False:
        failures.append("structural_passed_flag_must_be_false")
    if record.get("structural_rejection_pressure") is not True:
        failures.append("structural_rejection_pressure_must_be_true")
    if record.get("net_beta_within_cap") is not False:
        failures.append("net_beta_within_cap_must_be_false")
    for k, want in (("total_ok", False), ("per_pair_ok", False),
                    ("per_regime_ok", False), ("net_beta_within_cap", False),
                    ("forward_oos_populated", True)):
        if sv.get(k) is not want:
            failures.append("structural_subcheck_tampered_%s" % k)
    if len(record.get("rejection_reasons") or []) < 3:
        failures.append("rejection_reasons_missing")

    # no PnL / cost here
    if record.get("cost_model_applied_here") is not False:
        failures.append("cost_model_applied")
    if record.get("cost_model_reserved_for_replay") is not True:
        failures.append("cost_model_not_reserved")

    # downstream gates locked
    for gate in ("replay_gate_locked", "robustness_gate_locked",
                 "portfolio_gate_locked", "paper_trading_gate_locked",
                 "live_gate_locked"):
        if record.get(gate) is not True:
            failures.append("downstream_gate_unlocked_%s" % gate)

    locks = record.get("scope_locks") or {}
    for key in ("no_data_fetch", "no_re_detect", "no_relabel", "no_replay",
                "no_pnl", "no_cost_application", "no_baseline", "no_robustness",
                "no_portfolio_compute", "no_commit", "no_push", "no_auto_commit",
                "no_auto_push", "no_broker", "no_order_logic", "no_paper_trading",
                "no_live_trading", "no_gate_skip", "no_parameter_fitting"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
