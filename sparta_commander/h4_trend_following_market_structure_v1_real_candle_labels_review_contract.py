"""Candidate #18 -- h4_trend_following_market_structure_v1 -- REAL-CANDLE LABELS
REVIEW (PURE, RESEARCH ONLY).

Pins the FROZEN real-candle labels artifact produced by
tools/c18_h4_real_candle_labels_once.py (the FROZEN C18 H4 market-structure detector
run over the SHA-pinned local BTCUSDT 4h data) and records the labels-stage
STRUCTURAL verdict. A C18 "label" is one long market-structure setup -- an entry plus
its profit-confirmed pyramids and a structural exit.

It is chain-gated on the frozen C18 detector dry-run. It does NOTHING with real data
here: NO re-detect, NO relabel, NO replay, NO PnL, NO fee/cost, NO optimization, NO
re-parameterization, NO XAUUSD, NO writes, NO stage/commit/push, NO paper/live/broker/
order surface. It only PINS the SHAs + aggregate counts and re-states the structural
verdict. Every capability flag is pinned False with a full scope_locks set. The next
gate (fee-honest replay) needs an explicit human decision.

HONEST OUTCOME (FROZEN): the labels-stage STRUCTURAL gate is PASSED. Over
2019-01-01..2026-06-08 (16,286 H4 bars) the detector produced 389 long setups (>= 30),
every label long-only, max 3 units (243 profit-confirmed adds, capped), one position
per symbol, structural stops below the anchor, entries spaced >= 6 H4 bars, exits 330
stop / 59 structure-shift, and a populated forward-OOS 2026 window (23 labels). It is
NOT a profitability claim -- whether it BEATS buy-and-hold on a RISK-ADJUSTED,
fee-honest basis is decided ONLY at the reserved replay gate.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.h4_trend_following_market_structure_v1_detector_spec_dry_run_contract as _d18  # noqa: E501

L18_SCHEMA_VERSION = 1
L18_MODE = "RESEARCH_ONLY"
L18_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = _d18.CANDIDATE_ID
CANDIDATE_FAMILY = _d18.CANDIDATE_FAMILY
CANDIDATE_NAME = _d18.CANDIDATE_NAME

VERDICT_C18L_FROZEN = "C18_LABELS_FROZEN_FOR_HUMAN_REVIEW"

# --- pinned artifact provenance ---------------------------------------------
HEAD_AT_DETECTOR_DRY_RUN = "713c98a84de02826904c2ddb7d84c4b37a9e1469"
SOURCE_CSV = "data/h4_trend_following_market_structure_c18/raw/BTCUSDT_4h.csv"
LABELS_PATH = "data/h4_trend_following_market_structure_c18/labels/c18_h4_labels.json"
SUMMARY_PATH = ("data/h4_trend_following_market_structure_c18/labels/"
                "c18_h4_labels_summary.json")
EXPECTED_SOURCE_SHA256 = (
    "aec42241f47192ae29331f4b67a64500ca38aad1f403f13d0de5b405f7ecbaec")
EXPECTED_LABELS_SHA256 = (
    "907705d9506b1db79141118618b627248753cecab383d30564fbf5b7d8bc9e11")
EXPECTED_SUMMARY_SHA256 = (
    "6c656e9bab5be18abe96fbe88f8c21f6a2300a706de4fde4bc66e547aa149b2d")

# --- pinned frozen aggregates (from the real-candle run) ---------------------
SYMBOL = "BTCUSD"
TIMEFRAME = "4h"
WINDOW = ("2019-01-01T00:00:00Z", "2026-06-08T00:00:00Z")
N_CANDLES = 16286
N_LABELS = 389
TOTAL_ADDS = 243
MAX_UNITS = 3
EXITS_BY_REASON = {"stop": 330, "structure_shift": 59}
FORWARD_OOS_LABEL_COUNT = 23

MIN_LABELS_TOTAL = 30
MAX_UNITS_CAP = _d18.MAX_UNITS          # 3
MIN_SPACING = _d18.MIN_SPACING          # 6

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "re_detects", "relabels", "runs_labels_with_new_params",
    "runs_replay", "runs_backtest", "computes_pnl", "applies_fee_or_cost",
    "runs_optimization", "reparameterizes", "fetches_data", "reads_real_data",
    "uses_xauusd", "mutates_data", "stages_data", "auto_commits", "auto_pushes",
    "modifies_scheduler", "sends_notifications", "calls_api", "uses_network",
    "uses_credentials", "connects_broker", "connects_exchange", "uses_real_money",
    "places_orders", "contains_order_logic", "adds_to_losers", "paper_trading",
    "live_trading", "deploys_capital", "promotes_gate", "unlocks_downstream_gate",
    "skips_any_gate", "advances_without_human_approval", "claims_profitability",
    "claims_edge", "crosses_into_forbidden_gate",
)


def _structural_verdict() -> dict[str, Any]:
    labels_ok = N_LABELS >= MIN_LABELS_TOTAL
    max_units_ok = MAX_UNITS <= MAX_UNITS_CAP
    fwd_ok = FORWARD_OOS_LABEL_COUNT > 0
    passed = labels_ok and max_units_ok and fwd_ok
    return {
        "n_labels": N_LABELS, "min_labels": MIN_LABELS_TOTAL, "labels_ok": labels_ok,
        "all_long_only": True,
        "max_units": MAX_UNITS, "max_units_ok": max_units_ok,
        "one_position_per_symbol": True,
        "structural_stops_below_anchor": True,
        "spacing_min_6_bars": True,
        "total_adds": TOTAL_ADDS,
        "exits_by_reason": dict(EXITS_BY_REASON),
        "forward_oos_label_count": FORWARD_OOS_LABEL_COUNT,
        "forward_oos_populated": fwd_ok,
        "passed": passed,
    }


def get_candidate_18_labels_review_label() -> str:
    return (
        "Candidate #18 h4_trend_following_market_structure_v1 real-candle labels "
        "review (READ-ONLY, RESEARCH ONLY, PURE). Pins the FROZEN H4 setup-label "
        "artifact over SHA-pinned local BTCUSDT 4h data and the labels-stage "
        "STRUCTURAL verdict: PASSED -- 389 long setups (>= 30), all long-only, max 3 "
        "units (243 profit-confirmed adds), one position per symbol, structural stops, "
        ">= 6-bar spacing, forward-OOS 2026 populated (23). NO replay, NO PnL, NO fee. "
        "NOT a profitability claim -- risk-adjusted edge vs buy-and-hold is decided "
        "only at the replay gate.")


def get_candidate_18_labels_review_next_action() -> str:
    return "HUMAN_DECISION_C18_ADVANCE_TO_FEE_HONEST_REPLAY_OR_REJECT"


def build_c18_labels_review(repo_root: Any = ".",
                            tracked_paths: list | None = None) -> dict[str, Any]:
    """Assemble the frozen C18 real-candle labels review record. Pure; no I/O; pins
    SHAs + counts + the structural verdict; chain-gated on the frozen C18 detector
    dry-run."""
    dry = _d18.build_c18_detector_dry_run(repo_root, tracked_paths)
    dry_valid = _d18.validate_c18_detector_dry_run(dry)["valid"]
    sv = _structural_verdict()

    blockers: list = []
    if not dry_valid:
        blockers.append("c18_detector_dry_run_invalid")
    if dry.get("verdict") != "C18_DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW":
        blockers.append("c18_detector_dry_run_not_frozen")

    record: dict[str, Any] = {
        "schema_version": L18_SCHEMA_VERSION, "mode": L18_MODE, "lane": L18_LANE,
        "label": get_candidate_18_labels_review_label(),
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "candidate_name": CANDIDATE_NAME,
        "is_labels_review_only": True,
        "blockers": blockers,
        "verdict": (VERDICT_C18L_FROZEN if not blockers else "C18_LABELS_BLOCKED"),
        # chain provenance
        "detector_dry_run_verdict": dry.get("verdict"),
        "detector_dry_run_valid": dry_valid,
        # pinned artifact provenance (frozen local H4 data only)
        "head_at_detector_dry_run": HEAD_AT_DETECTOR_DRY_RUN,
        "source_csv": SOURCE_CSV, "labels_path": LABELS_PATH,
        "summary_path": SUMMARY_PATH,
        "expected_source_sha256": EXPECTED_SOURCE_SHA256,
        "expected_labels_sha256": EXPECTED_LABELS_SHA256,
        "expected_summary_sha256": EXPECTED_SUMMARY_SHA256,
        "uses_frozen_local_data_only": True,
        # pinned frozen aggregates
        "symbol": SYMBOL, "timeframe": TIMEFRAME, "window": list(WINDOW),
        "n_candles": N_CANDLES,
        "label_definition": "long_market_structure_trend_setup_with_pyramids",
        "n_labels": N_LABELS, "total_adds": TOTAL_ADDS, "max_units": MAX_UNITS,
        "exits_by_reason": dict(EXITS_BY_REASON),
        "forward_oos_label_count": FORWARD_OOS_LABEL_COUNT,
        # structural verdict -- HONEST PASS
        "structural_review": sv,
        "structural_passed": sv["passed"],
        "structural_rejection_pressure": not sv["passed"],
        "pass_reasons": [
            "WELL-FORMED, SUFFICIENTLY SAMPLED: 389 long setups (>= 30) over "
            "2019..2026-06-08, forward-OOS 2026 populated (23)",
            "RULE-CONSISTENT: every label long-only, max 3 units (243 "
            "profit-confirmed adds, capped), one position per symbol, structural "
            "stops below the anchor, entries spaced >= 6 H4 bars",
            "exits are structural: 330 stop / 59 structure-shift (no time/indicator "
            "exit)",
        ],
        "not_yet_validated": (
            "this is a STRUCTURAL pass only; whether the strategy BEATS buy-and-hold "
            "on a RISK-ADJUSTED, fee-honest basis (Sharpe / Calmar / max-drawdown, "
            "net of 37 bps) is decided ONLY at the reserved replay gate -- NOT here"),
        # cost reserved (no fee/PnL here)
        "cost_model_reserved_for_replay": True,
        "fee_applied_here": False,
        "human_review_required": True,
        "current_loop_stage": "real_candle_labels_review",
        "next_required_action": get_candidate_18_labels_review_next_action(),
        # downstream gates locked
        "replay_gate_locked": True, "robustness_gate_locked": True,
        "paper_trading_gate_locked": True, "live_gate_locked": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_data_fetch": True, "no_re_detect": True, "no_relabel": True,
        "no_replay": True, "no_backtest": True, "no_pnl": True,
        "no_fee_application": True, "no_optimization": True,
        "no_reparameterization": True, "no_robustness": True, "no_xauusd": True,
        "no_real_data_mutation": True, "no_add_to_losers": True, "no_stage": True,
        "no_commit": True, "no_push": True, "no_auto_commit": True,
        "no_auto_push": True, "no_scheduler_change": True, "no_broker": True,
        "no_credentials": True, "no_order_logic": True, "no_paper_trading": True,
        "no_live_trading": True, "no_gate_skip": True,
        "no_downstream_gate_unlock": True, "no_profitability_claim": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_c18_labels_review(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the review is research-only, labels-
    review-only, chain-gated on the frozen C18 detector dry-run, uses frozen local
    data only, pins the exact source + artifact SHAs, records the structural verdict
    consistently (passed iff the structural rules hold), applies no fee/PnL, makes no
    profitability claim, keeps XAUUSD out, locks downstream gates, and pins every
    capability flag False."""
    failures: list = []
    if record.get("mode") != L18_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_labels_review_only") is not True:
        failures.append("not_labels_review_only")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("verdict") != VERDICT_C18L_FROZEN:
        failures.append("verdict_not_frozen")

    # chain gate
    if record.get("detector_dry_run_valid") is not True:
        failures.append("detector_dry_run_not_valid")
    if record.get("detector_dry_run_verdict") != (
            "C18_DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW"):
        failures.append("detector_dry_run_not_frozen")

    # frozen local data + pinned SHAs
    if record.get("uses_frozen_local_data_only") is not True:
        failures.append("not_frozen_local_data_only")
    if record.get("expected_source_sha256") != EXPECTED_SOURCE_SHA256:
        failures.append("source_sha_tampered")
    if record.get("expected_labels_sha256") != EXPECTED_LABELS_SHA256:
        failures.append("labels_sha_tampered")
    if record.get("expected_summary_sha256") != EXPECTED_SUMMARY_SHA256:
        failures.append("summary_sha_tampered")

    # pinned aggregates consistent with the structural rules
    sv = record.get("structural_review") or {}
    if record.get("n_labels") != N_LABELS:
        failures.append("n_labels_tampered")
    if record.get("symbol") != "BTCUSD" or record.get("timeframe") != "4h":
        failures.append("symbol_timeframe_wrong")
    if sv.get("labels_ok") is not True:
        failures.append("labels_not_ok")
    if sv.get("all_long_only") is not True:
        failures.append("not_long_only")
    if sv.get("max_units_ok") is not True or sv.get("max_units", 9) > 3:
        failures.append("max_units_exceeded")
    if sv.get("one_position_per_symbol") is not True:
        failures.append("overlapping_positions")
    if sv.get("structural_stops_below_anchor") is not True:
        failures.append("stops_not_structural")
    if sv.get("spacing_min_6_bars") is not True:
        failures.append("spacing_violated")
    if sv.get("forward_oos_populated") is not True:
        failures.append("forward_oos_not_populated")
    expected_pass = (sv.get("labels_ok") and sv.get("all_long_only")
                     and sv.get("max_units_ok")
                     and sv.get("one_position_per_symbol")
                     and sv.get("structural_stops_below_anchor")
                     and sv.get("spacing_min_6_bars")
                     and sv.get("forward_oos_populated"))
    if record.get("structural_passed") != bool(expected_pass):
        failures.append("structural_passed_inconsistent")
    if sv.get("passed") != bool(expected_pass):
        failures.append("structural_review_passed_inconsistent")

    # no fee/PnL here; no profitability claim; next gate = replay decision
    if record.get("fee_applied_here") is not False:
        failures.append("fee_applied")
    if record.get("cost_model_reserved_for_replay") is not True:
        failures.append("cost_not_reserved")
    if not record.get("not_yet_validated"):
        failures.append("missing_not_yet_validated_caveat")
    if record.get("next_required_action") != (
            "HUMAN_DECISION_C18_ADVANCE_TO_FEE_HONEST_REPLAY_OR_REJECT"):
        failures.append("next_action_not_replay_gate")

    # downstream gates locked
    for gate in ("replay_gate_locked", "robustness_gate_locked",
                 "paper_trading_gate_locked", "live_gate_locked"):
        if record.get(gate) is not True:
            failures.append("downstream_gate_unlocked_%s" % gate)

    locks = record.get("scope_locks") or {}
    for key in ("no_data_fetch", "no_re_detect", "no_relabel", "no_replay",
                "no_pnl", "no_fee_application", "no_optimization", "no_xauusd",
                "no_add_to_losers", "no_commit", "no_push", "no_broker",
                "no_order_logic", "no_paper_trading", "no_live_trading",
                "no_gate_skip"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
