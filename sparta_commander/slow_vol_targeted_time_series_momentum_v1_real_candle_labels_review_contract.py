"""Candidate #15 -- slow_vol_targeted_time_series_momentum_v1 -- REAL-CANDLE
LABELS REVIEW (PURE, RESEARCH ONLY).

Pins the FROZEN real-candle labels artifact produced by
tools/c15_real_candle_detection_once.py (run READ-ONLY over the SHA-pinned local
BTC/ETH/SOL 1d data) and records the labels-stage structural verdict. A C15 label
is a position-INITIATION transition (long/short) -- an entry event, not a fixed-
horizon setup.

It is chain-gated on the frozen C15 detector synthetic dry-run. It does NOTHING
with real data here: it does NOT fetch data, NOT re-detect, NOT relabel, NOT
replay, NOT compute PnL, NOT apply the cost model, NOT run baselines / robustness
/ portfolio, NOT write files, NOT stage / commit / push, and NOT touch any paper /
live / broker / order surface. It only PINS the SHAs + the aggregate counts and
re-states the structural sample-size verdict. Every capability flag is pinned
False with a full scope_locks set. The replay gate stays human-gated.

Labels-stage outcome (FROZEN): the STRUCTURAL sample-size gate PASSES -- 200
accepted entry labels; >=20 per asset (BTC 77 / ETH 59 / SOL 64); >=20 per regime
(bull 74 / bear 66 / chop 60); forward-OOS 2026 populated (5); and a near-balanced
long/short split (long 97 / short 103) consistent with the symmetric design. This
is NOT a profitability claim -- no replay / PnL has been computed.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.slow_vol_targeted_time_series_momentum_v1_detector_spec_dry_run_contract as _d15  # noqa: E501

L15_SCHEMA_VERSION = 1
L15_MODE = "RESEARCH_ONLY"
L15_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = _d15.CANDIDATE_ID
CANDIDATE_FAMILY = _d15.CANDIDATE_FAMILY
CANDIDATE_NAME = _d15.CANDIDATE_NAME
SYMBOLS = tuple(_d15.SYMBOLS)
TIMEFRAME = "1d"

VERDICT_C15L_FROZEN = "C15_LABELS_FROZEN_FOR_HUMAN_REVIEW"

# --- pinned artifact provenance ---------------------------------------------
HEAD_AT_DETECTOR_DRY_RUN = "5399925b1cb60260b5ed750b6ce3b5765e584a0b"
LABELS_PATH = ("data/slow_vol_targeted_time_series_momentum_c15/"
               "detector_labels/c15_detector_labels.json")
SUMMARY_PATH = ("data/slow_vol_targeted_time_series_momentum_c15/"
                "detector_labels/c15_detector_summary.json")
EXPECTED_LABELS_SHA256 = (
    "d659d970e883f9fc1bc0f921f97cffe70746b03fcd236ba7d425686d26ecb8a4")
EXPECTED_SUMMARY_SHA256 = (
    "8b5604cd5d0ada9143e9d7f3526b1161ea22c0e751f6450d956f361763311c87")
EXPECTED_SOURCE_SHA256 = {
    "BTCUSD": "043fb722b35e738a0c2050f9388defc7ca99322ed2f153989746ee28bbb89b88",
    "ETHUSD": "1bfd0ca86137747f0fe4c3fb127b00dcbd4885bf76056dbc9c091a9d4681c1a3",
    "SOLUSD": "4716d4d124bd7d5327fdc4230f7b2eaea70085df88c182dd129232ce802c0113",
}

# --- pinned frozen aggregates -----------------------------------------------
ACCEPTED_LABEL_COUNT = 200
PER_ASSET = {"BTCUSD": 77, "ETHUSD": 59, "SOLUSD": 64}
PER_REGIME = {"bull": 74, "bear": 66, "chop": 60}
PER_SIDE = {"long": 97, "short": 103}
FORWARD_OOS_LABEL_COUNT = 5

MIN_LABELS_TOTAL = 100
MIN_PER_ASSET = 20
MIN_PER_REGIME = 20

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "re_detects", "relabels", "runs_labels",
    "runs_replay", "runs_backtest", "computes_pnl", "applies_cost_model",
    "runs_baseline", "runs_robustness", "runs_portfolio_compute", "fetches_data",
    "reads_real_data", "mutates_data", "stages_data", "auto_commits",
    "auto_pushes", "modifies_scheduler", "sends_notifications", "calls_api",
    "uses_network", "uses_credentials", "connects_broker", "connects_exchange",
    "uses_real_money", "places_orders", "contains_order_logic", "paper_trading",
    "live_trading", "deploys_capital", "promotes_gate", "unlocks_downstream_gate",
    "skips_any_gate", "uses_one_edit_allowance", "advances_without_human_approval",
    "claims_profitability", "claims_edge", "crosses_into_forbidden_gate",
)


def _structural_verdict() -> dict[str, Any]:
    total_ok = ACCEPTED_LABEL_COUNT >= MIN_LABELS_TOTAL
    per_asset_ok = all(PER_ASSET.get(s, 0) >= MIN_PER_ASSET for s in SYMBOLS)
    per_regime_ok = all(PER_REGIME.get(r, 0) >= MIN_PER_REGIME
                        for r in ("bull", "bear", "chop"))
    fwd_ok = FORWARD_OOS_LABEL_COUNT > 0
    passed = total_ok and per_asset_ok and per_regime_ok and fwd_ok
    return {
        "total": ACCEPTED_LABEL_COUNT, "min_total": MIN_LABELS_TOTAL,
        "total_ok": total_ok,
        "per_asset": dict(sorted(PER_ASSET.items())),
        "min_per_asset": MIN_PER_ASSET, "per_asset_ok": per_asset_ok,
        "per_regime": dict(sorted(PER_REGIME.items())),
        "min_per_regime": MIN_PER_REGIME, "per_regime_ok": per_regime_ok,
        "forward_oos_label_count": FORWARD_OOS_LABEL_COUNT,
        "forward_oos_populated": fwd_ok,
        "passed": passed,
    }


def get_candidate_15_labels_review_label() -> str:
    return (
        "Candidate #15 slow_vol_targeted_time_series_momentum_v1 real-candle labels "
        "review (READ-ONLY, RESEARCH ONLY, PURE). Pins the FROZEN entry-label "
        "artifact over SHA-pinned local BTC/ETH/SOL 1d data and the labels-stage "
        "STRUCTURAL sample-size verdict (PASSED: 200 labels; >=20 per asset / "
        "regime; forward-OOS populated; symmetric long/short). NO replay, NO PnL, "
        "NO cost application, NO baseline. NOT a profitability claim.")


def get_candidate_15_labels_review_next_action() -> str:
    return "HUMAN_DECISION_C15_ADVANCE_TO_FEE_HONEST_REPLAY_OR_REJECT"


def build_c15_labels_review(repo_root: Any = ".",
                            tracked_paths: list | None = None) -> dict[str, Any]:
    """Assemble the frozen C15 real-candle labels review record. Pure; no I/O;
    pins SHAs + counts; chain-gated on the frozen C15 detector dry-run."""
    dry = _d15.build_c15_detector_dry_run(repo_root, tracked_paths)
    dry_valid = _d15.validate_c15_detector_dry_run(dry)["valid"]
    sv = _structural_verdict()

    blockers: list = []
    if not dry_valid:
        blockers.append("c15_detector_dry_run_invalid")
    if dry.get("verdict") != "C15_DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW":
        blockers.append("c15_detector_dry_run_not_frozen")

    record: dict[str, Any] = {
        "schema_version": L15_SCHEMA_VERSION, "mode": L15_MODE, "lane": L15_LANE,
        "label": get_candidate_15_labels_review_label(),
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "candidate_name": CANDIDATE_NAME,
        "is_labels_review_only": True,
        "blockers": blockers,
        "verdict": (VERDICT_C15L_FROZEN if not blockers
                    else "C15_LABELS_BLOCKED"),
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
        "symbols": list(SYMBOLS), "timeframe": TIMEFRAME,
        "label_definition": "state_transition_into_active_position_entry_event",
        "labels_are_non_overlapping_by_construction": True,
        "accepted_label_count": ACCEPTED_LABEL_COUNT,
        "per_asset": dict(sorted(PER_ASSET.items())),
        "per_regime": dict(sorted(PER_REGIME.items())),
        "per_side": dict(sorted(PER_SIDE.items())),
        "forward_oos_label_count": FORWARD_OOS_LABEL_COUNT,
        # structural verdict
        "structural_sample_size": sv,
        "structural_sample_size_passed": sv["passed"],
        "structural_rejection_pressure": not sv["passed"],
        "long_short_balanced": abs(PER_SIDE["long"] - PER_SIDE["short"])
        <= 0.2 * ACCEPTED_LABEL_COUNT,
        # cost model still reserved (no PnL here)
        "cost_model_reserved_for_replay": True,
        "cost_model_applied_here": False,
        "human_review_required": True,
        "current_loop_stage": "real_candle_labels_review",
        "next_required_action": get_candidate_15_labels_review_next_action(),
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
        "no_one_edit_invocation": True, "no_downstream_gate_unlock": True,
        "no_profitability_claim": True, "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_c15_labels_review(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the review is research-only, labels-
    review-only, chain-gated on the frozen C15 detector dry-run, pins the exact
    SHAs + frozen aggregates, the structural sample-size gate PASSES, no PnL/cost
    is applied, downstream gates are locked, and every capability flag is False."""
    failures: list = []
    if record.get("mode") != L15_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_labels_review_only") is not True:
        failures.append("not_labels_review_only")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("verdict") != VERDICT_C15L_FROZEN:
        failures.append("verdict_not_frozen")

    # chain gate
    if record.get("detector_dry_run_valid") is not True:
        failures.append("detector_dry_run_not_valid")
    if record.get("detector_dry_run_verdict") != (
            "C15_DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW"):
        failures.append("detector_dry_run_not_frozen")

    # SHA pins
    if record.get("expected_labels_sha256") != EXPECTED_LABELS_SHA256:
        failures.append("labels_sha_tampered")
    if record.get("expected_summary_sha256") != EXPECTED_SUMMARY_SHA256:
        failures.append("summary_sha_tampered")
    for s in SYMBOLS:
        if (record.get("expected_source_sha256") or {}).get(s) != \
                EXPECTED_SOURCE_SHA256[s]:
            failures.append("source_sha_tampered_%s" % s)

    # frozen aggregates
    if record.get("accepted_label_count") != ACCEPTED_LABEL_COUNT:
        failures.append("label_count_tampered")
    if record.get("per_asset") != dict(sorted(PER_ASSET.items())):
        failures.append("per_asset_tampered")
    if record.get("per_regime") != dict(sorted(PER_REGIME.items())):
        failures.append("per_regime_tampered")
    if record.get("per_side") != dict(sorted(PER_SIDE.items())):
        failures.append("per_side_tampered")

    # structural gate PASSES
    sv = record.get("structural_sample_size") or {}
    if sv.get("passed") is not True:
        failures.append("structural_gate_not_passed")
    if record.get("structural_sample_size_passed") is not True:
        failures.append("structural_passed_flag_tampered")
    if record.get("structural_rejection_pressure") is not False:
        failures.append("structural_rejection_pressure_set")
    for k in ("total_ok", "per_asset_ok", "per_regime_ok", "forward_oos_populated"):
        if sv.get(k) is not True:
            failures.append("structural_subcheck_off_%s" % k)

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
