"""Candidate #18 -- h4_trend_following_market_structure_v1 -- FAMILY PROPOSAL
(PURE, RESEARCH ONLY).

The formal candidate-family proposal for the human-approved next research direction
(HUMAN_APPROVED_NEXT_RESEARCH_DIRECTION_H4_TREND_FOLLOWING_FROM_OBSERVED_PROFITABLE_
TRADER): an H4 MARKET-STRUCTURE TREND-FOLLOWING family, promoted from the committed
H4 discretionary trend-following research backlog note. Chain-gated on that backlog
note (it imports it, re-validates it, and requires status
BACKLOG_ONLY_NOT_CANDIDATE_YET).

HONESTY RULE (pinned): this is NOT the observed trader's exact system. The exact
entries, stops, and add points are UNAVAILABLE (the lead is screenshots/conversation
only, no annotated chart examples). This proposal is therefore an OBJECTIVE,
TESTABLE APPROXIMATION of the observed BEHAVIOUR (no indicators, market-structure
trend-following, patience / low trade frequency, do not overtrade, add to winners
only after profit confirmation) -- not a reproduction of a specific system.

It is a PROPOSAL only: it DECLARES the family thesis, why it differs from the
rejected C1-C17 families, the observed universe and the lane/data LIMITATIONS, the
six candidate SUB-FAMILIES to compare, the evaluation metrics, the cost assumptions,
the FUTURE data requirements (recorded, NOT fetched), the out-of-sample validation
requirement, the safety boundaries, and the next human gate. It builds NO detector,
NO labels, NO replay; runs NO PnL/optimization/data fetch; touches NO paper/live/
broker/order surface. Every capability flag is pinned False with a full scope_locks
set. Advancing to the candidate-spec gate needs an explicit human decision.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.h4_discretionary_trend_following_research_backlog_note_v1_contract as _note  # noqa: E501
import sparta_commander.research_expansion_plan_v1_contract as _rep

C18_SCHEMA_VERSION = 1
C18_MODE = "RESEARCH_ONLY"
C18_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = "C18"
CANDIDATE_FAMILY = "h4_trend_following_market_structure"
CANDIDATE_NAME = "h4_trend_following_market_structure_v1"

REJECTED_FAMILIES_C1_TO_C17 = tuple(_rep.REJECTED_FAMILIES_C1_TO_C17)   # 22

# --- the preserved, frozen gate sequence (each stage human-gated) -----------
GATE_SEQUENCE = (
    "family_proposal", "candidate_spec", "detector_spec_dry_run",
    "real_candle_labels_review", "fee_honest_replay_review",
    "rejection_or_promote_decision",
)

# --- observed universe + timeframe + lane/data limitations ------------------
OBSERVED_TIMEFRAME = "H4"
OBSERVED_INSTRUMENTS = ("BTCUSD", "XAUUSD")
# The current frozen local research data is BTC/ETH/SOL DAILY (D1) only -- there is
# NO H4 data and NO XAUUSD (gold) in the local dataset. The proposal RESPECTS that:
# the initial testable scope is crypto H4 (BTCUSD primary, ETH/SOL as in-lane
# proxies), and XAUUSD is recorded as a future cross-asset extension needing its own
# data sourcing and a separate human approval.
INITIAL_TESTABLE_SCOPE = ("crypto H4 -- BTCUSD primary (ETH/SOL as in-lane proxies); "
                          "XAUUSD recorded as a future cross-asset extension")
XAUUSD_OUTSIDE_CURRENT_LANE = True

# --- 1. family thesis -------------------------------------------------------
FAMILY_THESIS = (
    "On H4, follow the established market-structure trend (higher highs / higher "
    "lows for longs, the inverse for shorts) WITHOUT indicators as the primary "
    "signal: enter only in the direction of the prevailing structure, trade "
    "INFREQUENTLY and patiently (avoid overtrading), and ADD to a position only "
    "AFTER it is already in profit and structure confirms continuation (pyramiding "
    "on confirmed winners, never on losers). The thesis is that a disciplined, "
    "low-frequency, structure-defined trend-following program with profit-confirmed "
    "pyramiding can produce a durable risk-adjusted edge -- to be PROVEN, not "
    "assumed.")

# --- HONESTY: not the friend's exact system ---------------------------------
HONESTY = {
    "is_observed_traders_exact_system": False,
    "exact_entries_stops_add_points_available": False,
    "is_objective_testable_approximation_of_observed_behaviour": True,
    "lead_evidence": "screenshots/conversation only; no annotated chart examples",
    "statement": (
        "This is NOT the observed trader's exact system. Exact entries, stops, and "
        "add points are unavailable, so this is an objective, testable approximation "
        "of the observed BEHAVIOUR, not a reproduction of a specific system."),
}

# --- 2. why different from C1-C17 -------------------------------------------
WHY_DIFFERENT_FROM_C1_C17 = (
    "H4 timeframe -- every C1-C17 family was DAILY (D1) or a D1 allocator; this is "
    "the first intraday-structure (H4) trend family",
    "MARKET-STRUCTURE defined (swing highs/lows, breakout-retest, pullback), NOT an "
    "indicator/EMA/momentum-lookback signal like C4/C5/C15",
    "explicitly LOW-FREQUENCY / patience-gated (do not overtrade) -- a frequency "
    "discipline none of the rejected timing families imposed",
    "ADD-TO-WINNERS pyramiding only after profit confirmation -- a position-building "
    "mechanism absent from C1-C17",
    "not the C17 risk-parity allocator and not the C15 slow vol-targeted D1 "
    "momentum; a different timeframe AND a different mechanism",
)

# --- 4. the six candidate SUB-FAMILIES to compare ---------------------------
SUB_FAMILIES = (
    {"key": "h4_market_structure_trend_continuation",
     "desc": "enter on confirmed HH/HL (or LH/LL) continuation of H4 structure"},
    {"key": "h4_breakout_and_retest_continuation",
     "desc": "enter on a structure breakout that retests the broken level and holds"},
    {"key": "h4_pullback_in_trend",
     "desc": "enter on a pullback to structure support/resistance within the trend"},
    {"key": "h4_pyramiding_add_to_winners",
     "desc": "scale into a confirmed winner at successive structure confirmations"},
    {"key": "daily_trend_filter_plus_h4_entry",
     "desc": "gate H4 entries by the D1 trend direction (higher-timeframe filter)"},
    {"key": "strong_trend_regime_filter",
     "desc": "only trade when a strong-trend regime is in force; stand aside in chop"},
)

# --- 5. evaluation metrics --------------------------------------------------
EVALUATION_METRICS = {
    "primary_risk_adjusted": ("sharpe_ratio", "calmar_ratio", "max_drawdown"),
    "trend_following_diagnostics": ("net_return", "profit_factor", "win_rate",
                                    "avg_R_per_trade", "trade_frequency_low",
                                    "pyramiding_contribution"),
    "baseline": "matched buy-and-hold on the same instrument/window, net of cost",
    "win_condition": ("BEAT buy-and-hold on a RISK-ADJUSTED basis (Sharpe and/or "
                      "Calmar with no worse drawdown) AND survive forward-OOS -- not "
                      "merely positive raw return"),
    "patience_check": "low trade frequency is a REQUIREMENT, not a free parameter",
}

# --- 6. cost assumptions ----------------------------------------------------
FEE_ROUND_TRIP_BPS = 27.0
SLIPPAGE_ROUND_TRIP_BPS = 10.0
ALL_IN_ROUND_TRIP_BPS = FEE_ROUND_TRIP_BPS + SLIPPAGE_ROUND_TRIP_BPS   # 37.0
COST_ASSUMPTIONS = {
    "crypto_all_in_round_trip_bps": ALL_IN_ROUND_TRIP_BPS,
    "xauusd_cost_to_be_sourced_separately": True,
    "low_frequency_keeps_cost_drag_small": True,
    "cost_applied_only_at_replay_gate": True,
}

# --- 7. FUTURE data requirements (recorded, NOT fetched) --------------------
DATA_REQUIREMENTS = {
    "h4_ohlc_btcusd": {"required": True, "available_locally": False,
                       "note": "current local data is BTC/ETH/SOL DAILY only"},
    "h4_ohlc_eth_sol": {"required": False, "available_locally": False,
                        "note": "optional in-lane crypto proxies"},
    "h4_ohlc_xauusd": {"required": False, "available_locally": False,
                       "note": "gold; OUTSIDE the crypto-D1 lane; needs separate "
                               "sourcing + its own human approval"},
    "no_data_fetched_here": True,
    "data_sourcing_requires_separate_human_approval": True,
}

# --- 8. out-of-sample validation requirement --------------------------------
OOS_VALIDATION = {
    "forward_oos_required": True,
    "forward_oos_window": "unseen_continuation",
    "forward_oos_must_hold_risk_adjusted_edge": True,
    "no_parameter_optimization": True,
    "no_in_sample_only_fit": True,
}

# --- 9. safety boundaries ---------------------------------------------------
SAFETY_BOUNDARIES = (
    "research-only: no paper trading, no live trading, no broker/exchange, no "
    "orders, no credentials, no data fetch in this proposal",
    "no indicators as the PRIMARY signal -- structure first (an indicator may only "
    "ever be a secondary confirmation, declared not built)",
    "pyramiding ONLY after profit confirmation -- never add to a losing position",
    "low trade frequency / patience is a hard requirement, not an optimization knob",
    "every downstream gate (spec / detector / labels / replay / paper / live) stays "
    "human-gated and locked; promotion requires beating buy-and-hold risk-adjusted "
    "and surviving forward-OOS -- the same evidence bar that rejected C1-C17",
)

NEXT_HUMAN_GATE_AFTER_PROPOSAL = (
    "HUMAN_DECISION_C18_ADVANCE_TO_CANDIDATE_SPEC_OR_REJECT")

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "builds_candidate_files", "runs_detector",
    "runs_labels", "runs_replay", "runs_backtest", "computes_pnl",
    "optimizes_parameters", "reparameterizes", "runs_robustness", "fetches_data",
    "reads_real_data", "mutates_data", "stages_data", "auto_commits", "auto_pushes",
    "modifies_scheduler", "sends_notifications", "calls_api", "uses_network",
    "uses_credentials", "connects_broker", "connects_exchange", "uses_real_money",
    "places_orders", "contains_order_logic", "uses_indicators_as_primary_signal",
    "adds_to_losers", "paper_trading", "live_trading", "deploys_capital",
    "promotes_gate", "unlocks_downstream_gate", "skips_any_gate",
    "reproposes_rejected_family", "claims_friends_exact_system",
    "advances_without_human_approval", "claims_profitability", "claims_edge",
    "crosses_into_forbidden_gate",
)


def get_candidate_18_proposal_label() -> str:
    return (
        "Candidate #18 h4_trend_following_market_structure_v1 family proposal "
        "(READ-ONLY, RESEARCH ONLY, PURE PROPOSAL). An H4 market-structure "
        "trend-following family (no indicators primary, patience / low frequency, "
        "add-to-winners after profit confirmation) -- an OBJECTIVE TESTABLE "
        "APPROXIMATION of an observed profitable trader, NOT their exact system "
        "(exact entries/stops unavailable). Compares six sub-families. PROPOSAL "
        "ONLY: advancing to the candidate-spec gate needs an explicit human "
        "decision. NO detector, NO labels, NO replay, NO optimization, NO data "
        "fetch, NO paper/live. NOT a profitability claim.")


def get_candidate_18_proposal_next_action() -> str:
    return NEXT_HUMAN_GATE_AFTER_PROPOSAL


def _deepish(d: dict) -> dict:
    out: dict = {}
    for k, v in d.items():
        out[k] = dict(v) if isinstance(v, dict) else v
    return out


def build_c18_proposal(repo_root: Any = ".",
                       tracked_paths: list | None = None) -> dict[str, Any]:
    """Assemble the frozen Candidate #18 family-proposal record. Pure; no I/O;
    proposal only. Chain-gated on the committed H4 backlog note (must be a valid
    BACKLOG_ONLY_NOT_CANDIDATE_YET note)."""
    note = _note.build_h4_backlog_note()
    note_valid = _note.validate_h4_backlog_note(note)["valid"]
    note_is_backlog = note.get("status") == "BACKLOG_ONLY_NOT_CANDIDATE_YET"

    blockers: list = []
    if not note_valid:
        blockers.append("h4_backlog_note_invalid")
    if not note_is_backlog:
        blockers.append("source_note_not_backlog_status")
    if CANDIDATE_FAMILY in REJECTED_FAMILIES_C1_TO_C17:
        blockers.append("candidate_family_in_rejected_ledger")

    record: dict[str, Any] = {
        "schema_version": C18_SCHEMA_VERSION, "mode": C18_MODE, "lane": C18_LANE,
        "label": get_candidate_18_proposal_label(),
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "candidate_name": CANDIDATE_NAME,
        "is_pure_proposal_only": True,
        "blockers": blockers,
        "verdict": ("C18_PROPOSAL_FROZEN_FOR_HUMAN_REVIEW" if not blockers
                    else "C18_PROPOSAL_BLOCKED"),
        # chain provenance (promoted from the H4 backlog note)
        "promoted_from_backlog_note": note.get("note_id"),
        "source_note_valid": note_valid,
        "source_note_status": note.get("status"),
        "approved_via": ("HUMAN_APPROVED_NEXT_RESEARCH_DIRECTION_H4_TREND_FOLLOWING_"
                         "FROM_OBSERVED_PROFITABLE_TRADER"),
        # HONESTY rule (pinned)
        "honesty": dict(HONESTY),
        "is_observed_traders_exact_system": False,
        "is_objective_testable_approximation": True,
        # the required explanation sections
        "family_thesis": FAMILY_THESIS,                                # 1
        "why_different_from_c1_c17": list(WHY_DIFFERENT_FROM_C1_C17),   # 2
        "observed_timeframe": OBSERVED_TIMEFRAME,                       # 3
        "observed_instruments": list(OBSERVED_INSTRUMENTS),
        "initial_testable_scope": INITIAL_TESTABLE_SCOPE,
        "xauusd_outside_current_lane": XAUUSD_OUTSIDE_CURRENT_LANE,
        "sub_families": [dict(s) for s in SUB_FAMILIES],               # 4
        "evaluation_metrics": _deepish(EVALUATION_METRICS),           # 5
        "cost_assumptions": dict(COST_ASSUMPTIONS),                   # 6
        "data_requirements": _deepish(DATA_REQUIREMENTS),             # 7
        "oos_validation": dict(OOS_VALIDATION),                       # 8
        "safety_boundaries": list(SAFETY_BOUNDARIES),                 # 9
        "next_human_gate_after_proposal": NEXT_HUMAN_GATE_AFTER_PROPOSAL,
        # identity / anti-loop
        "is_h4_timeframe": True,
        "is_market_structure_based": True,
        "uses_indicators_as_primary": False,
        "is_low_frequency_patience_gated": True,
        "pyramids_only_on_confirmed_winners": True,
        "gate_sequence": list(GATE_SEQUENCE),
        "gate_sequence_preserved_unchanged": True,
        "rejected_families_c1_to_c17": list(REJECTED_FAMILIES_C1_TO_C17),
        "rejected_families_count": len(REJECTED_FAMILIES_C1_TO_C17),
        "candidate_not_in_rejected_ledger":
            CANDIDATE_FAMILY not in REJECTED_FAMILIES_C1_TO_C17,
        "all_in_round_trip_bps": ALL_IN_ROUND_TRIP_BPS,
        "human_review_required": True,
        "current_loop_stage": "family_proposal",
        "next_required_action": NEXT_HUMAN_GATE_AFTER_PROPOSAL,
        # downstream gates locked
        "spec_gate_locked": True, "detector_gate_locked": True,
        "labels_gate_locked": True, "replay_gate_locked": True,
        "paper_trading_gate_locked": True, "live_gate_locked": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_build": True, "no_write": True, "no_execute": True,
        "no_detector": True, "no_labels": True, "no_replay": True,
        "no_backtest": True, "no_pnl": True, "no_optimization": True,
        "no_reparameterization": True, "no_robustness": True, "no_data_fetch": True,
        "no_real_data_access": True, "no_stage": True, "no_commit": True,
        "no_push": True, "no_auto_commit": True, "no_auto_push": True,
        "no_scheduler_change": True, "no_broker": True, "no_credentials": True,
        "no_order_logic": True, "no_indicators_as_primary": True,
        "no_add_to_losers": True, "no_paper_trading": True, "no_live_trading": True,
        "no_gate_skip": True, "no_rejected_family_repropose": True,
        "no_friends_exact_system_claim": True, "no_downstream_gate_unlock": True,
        "no_profitability_claim": True, "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_c18_proposal(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the proposal is research-only, pure-
    proposal-only, chain-gated on the valid H4 backlog note, an H4 market-structure
    trend family NOT in the C1-C17 (22) ledger, carries the honesty disclosure (NOT
    the friend's exact system; objective testable approximation), the six
    sub-families, the future-data-requirements record (nothing fetched), the
    risk-adjusted evaluation + OOS requirement, preserves the gate sequence, keeps
    downstream gates locked, and pins every capability flag False."""
    failures: list = []
    if record.get("mode") != C18_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_pure_proposal_only") is not True:
        failures.append("not_pure_proposal_only")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("verdict") != "C18_PROPOSAL_FROZEN_FOR_HUMAN_REVIEW":
        failures.append("verdict_not_frozen")

    # chain gate on the backlog note
    if record.get("source_note_valid") is not True:
        failures.append("backlog_note_not_valid")
    if record.get("source_note_status") != "BACKLOG_ONLY_NOT_CANDIDATE_YET":
        failures.append("source_note_not_backlog_status")
    if record.get("promoted_from_backlog_note") != (
            "BACKLOG_H4_DISCRETIONARY_TREND_FOLLOWING_V1"):
        failures.append("promoted_from_wrong_note")

    # HONESTY rule -- cannot be flipped
    h = record.get("honesty") or {}
    if record.get("is_observed_traders_exact_system") is not False:
        failures.append("must_not_claim_exact_system")
    if h.get("is_observed_traders_exact_system") is not False:
        failures.append("honesty_exact_system_flag_wrong")
    if h.get("exact_entries_stops_add_points_available") is not False:
        failures.append("honesty_must_say_exacts_unavailable")
    if record.get("is_objective_testable_approximation") is not True:
        failures.append("must_be_objective_approximation")
    if not h.get("statement"):
        failures.append("honesty_statement_missing")

    # identity + anti-loop
    if record.get("is_h4_timeframe") is not True:
        failures.append("not_h4")
    if record.get("is_market_structure_based") is not True:
        failures.append("not_market_structure_based")
    if record.get("uses_indicators_as_primary") is not False:
        failures.append("indicators_must_not_be_primary")
    if record.get("is_low_frequency_patience_gated") is not True:
        failures.append("not_low_frequency_patience_gated")
    if record.get("pyramids_only_on_confirmed_winners") is not True:
        failures.append("must_pyramid_only_on_winners")
    if record.get("candidate_not_in_rejected_ledger") is not True:
        failures.append("candidate_in_rejected_ledger")
    if record.get("candidate_family") in REJECTED_FAMILIES_C1_TO_C17:
        failures.append("family_listed_as_rejected")
    if record.get("rejected_families_count") != 22:
        failures.append("ledger_not_22")
    if len(record.get("why_different_from_c1_c17") or []) < 5:
        failures.append("insufficient_difference_explanation")

    # observed universe + lane/data limitation respected
    if record.get("observed_timeframe") != "H4":
        failures.append("timeframe_not_h4")
    if list(record.get("observed_instruments") or []) != ["BTCUSD", "XAUUSD"]:
        failures.append("instruments_not_btc_xau")
    if record.get("xauusd_outside_current_lane") is not True:
        failures.append("xauusd_lane_limitation_missing")

    # the six sub-families
    subs = record.get("sub_families") or []
    if len(subs) != 6:
        failures.append("sub_families_not_six")
    keys = {s.get("key") for s in subs}
    for must in ("h4_market_structure_trend_continuation",
                 "h4_breakout_and_retest_continuation", "h4_pullback_in_trend",
                 "h4_pyramiding_add_to_winners",
                 "daily_trend_filter_plus_h4_entry", "strong_trend_regime_filter"):
        if must not in keys:
            failures.append("sub_family_missing_%s" % must)

    # evaluation: risk-adjusted; cost reserved for replay
    em = record.get("evaluation_metrics") or {}
    prim = em.get("primary_risk_adjusted") or ()
    for m in ("sharpe_ratio", "calmar_ratio", "max_drawdown"):
        if m not in prim:
            failures.append("metric_missing_%s" % m)
    if "risk-adjusted" not in str(em.get("win_condition", "")).lower():
        failures.append("win_condition_not_risk_adjusted")
    ct = record.get("cost_assumptions") or {}
    if ct.get("crypto_all_in_round_trip_bps") != 37.0:
        failures.append("cost_model_tampered")
    if ct.get("cost_applied_only_at_replay_gate") is not True:
        failures.append("cost_not_reserved_for_replay")

    # FUTURE data requirements recorded, nothing fetched
    dr = record.get("data_requirements") or {}
    if dr.get("no_data_fetched_here") is not True:
        failures.append("data_fetch_flag_wrong")
    if (dr.get("h4_ohlc_btcusd") or {}).get("available_locally") is not False:
        failures.append("h4_btc_should_not_be_local")
    if dr.get("data_sourcing_requires_separate_human_approval") is not True:
        failures.append("data_sourcing_not_human_gated")

    # OOS required, no optimization
    oos = record.get("oos_validation") or {}
    if oos.get("forward_oos_required") is not True:
        failures.append("forward_oos_not_required")
    if oos.get("no_parameter_optimization") is not True:
        failures.append("optimization_not_forbidden")

    # gate sequence + downstream locks
    if list(record.get("gate_sequence") or []) != list(GATE_SEQUENCE):
        failures.append("gate_sequence_tampered")
    if record.get("next_required_action") != NEXT_HUMAN_GATE_AFTER_PROPOSAL:
        failures.append("next_action_not_spec_gate")
    for gate in ("spec_gate_locked", "detector_gate_locked", "labels_gate_locked",
                 "replay_gate_locked", "paper_trading_gate_locked",
                 "live_gate_locked"):
        if record.get(gate) is not True:
            failures.append("downstream_gate_unlocked_%s" % gate)

    locks = record.get("scope_locks") or {}
    for key in ("no_build", "no_detector", "no_labels", "no_replay", "no_pnl",
                "no_optimization", "no_data_fetch", "no_commit", "no_push",
                "no_broker", "no_order_logic", "no_indicators_as_primary",
                "no_add_to_losers", "no_paper_trading", "no_live_trading",
                "no_gate_skip", "no_rejected_family_repropose",
                "no_friends_exact_system_claim"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
