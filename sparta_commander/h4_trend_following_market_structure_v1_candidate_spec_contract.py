"""Candidate #18 -- h4_trend_following_market_structure_v1 -- CANDIDATE SPEC
(PURE, RESEARCH ONLY).

The human-approved (HUMAN_DECISION_C18_ADVANCE_TO_CANDIDATE_SPEC) formal candidate
specification for the frozen C18 family proposal: an H4 MARKET-STRUCTURE
trend-following strategy. This is a pure, in-memory specification: it DECLARES the
EXACT rules (trend definition / entry / stop / exit / pyramiding / invalidation /
non-overlap), the universe and lane/data limitations, the risk-adjusted evaluation,
the reserved fee-honest replay cost, the future data requirements (recorded, NOT
fetched), the out-of-sample requirement, the rejection criteria, and the next human
gate. It is chain-gated on the committed C18 proposal.

HONESTY RULE (pinned): this is NOT the observed trader's exact system. The exact
entries/stops/add-points are UNAVAILABLE, so these rules are an OBJECTIVE, TESTABLE
APPROXIMATION of the observed behaviour (no indicators, market-structure
trend-following, patience / low frequency, do not overtrade, add to winners only
after profit confirmation) -- a falsifiable rule set, not a reproduction.

It builds NO detector, NO labels, NO replay; runs NO PnL/optimization/data fetch;
touches NO paper/live/broker/order surface. Every capability flag is pinned False
with a full scope_locks set. The next gate (detector spec + synthetic dry-run) still
requires an explicit human decision.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.h4_trend_following_market_structure_v1_proposal_contract as _c18p  # noqa: E501

C18S_SCHEMA_VERSION = 1
C18S_MODE = "RESEARCH_ONLY"
C18S_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = _c18p.CANDIDATE_ID
CANDIDATE_FAMILY = _c18p.CANDIDATE_FAMILY
CANDIDATE_NAME = _c18p.CANDIDATE_NAME

EXPECTED_PROPOSAL_VERDICT = "C18_PROPOSAL_FROZEN_FOR_HUMAN_REVIEW"

# --- the preserved, frozen gate sequence (each stage human-gated) -----------
GATE_SEQUENCE = (
    "family_proposal", "candidate_spec", "detector_spec_dry_run",
    "real_candle_labels_review", "fee_honest_replay_review",
    "rejection_or_promote_decision",
)

# --- universe + timeframe + lane/data limitations ---------------------------
TIMEFRAME = "H4"
INITIAL_TESTABLE_SYMBOLS = ("BTCUSD",)          # crypto H4, in-lane primary
OPTIONAL_IN_LANE_PROXIES = ("ETHUSD", "SOLUSD")
OBSERVED_BUT_OUT_OF_LANE = ("XAUUSD",)          # gold; separate sourcing + approval
HIGHER_TIMEFRAME_FILTER = "D1"                  # daily trend filter (sub-family 5)

# --- declared (NOT fitted) structure parameters -----------------------------
# A pre-registered starting specification, not optimized values. No parameter
# search is performed or permitted at this gate.
SPEC_PARAMS = {
    "swing_pivot_strength_k": 2,        # a swing high/low = extreme of +/-K bars (5-bar pivot)
    "trend_confirmation_swings": 2,     # 2 rising swing highs AND 2 rising swing lows
    "stop_buffer_frac": 0.0015,         # structural stop buffer below/above the anchor swing
    "max_units_total": 3,               # base unit + up to 2 pyramids
    "max_concurrent_positions_per_symbol": 1,   # non-overlap
    "min_bars_between_entries": 6,      # patience / low-frequency floor (in H4 bars)
    "uses_indicators": False,           # structure-only; no EMA/RSI/MACD/etc
    "no_parameter_optimization": True,
}

# --- 1. EXACT trend definition ----------------------------------------------
TREND_RULE = (
    "Market structure on H4, no indicators. A swing HIGH is a bar whose high is the "
    "highest of the surrounding +/-K bars (K = swing_pivot_strength_k); a swing LOW "
    "is symmetric. UPTREND = the last two CONFIRMED swing highs are rising AND the "
    "last two CONFIRMED swing lows are rising (higher highs + higher lows). DOWNTREND "
    "= the mirror (lower highs + lower lows). Anything else is RANGE / NO-TRADE.")

# --- 2. EXACT entry rule (pullback-in-trend, primary) -----------------------
ENTRY_RULE = (
    "Trade ONLY with the confirmed trend. LONG: in an uptrend, after price pulls back "
    "toward the most recent confirmed swing low (structure support) WITHOUT breaking "
    "it, enter at the close of the first bar that confirms a new HIGHER LOW (closes "
    "back up while holding above the prior swing low). SHORT: the mirror in a "
    "downtrend. No indicator triggers. Entries are spaced by at least "
    "min_bars_between_entries H4 bars (patience / no overtrade).")

# --- 3. EXACT stop rule -----------------------------------------------------
STOP_RULE = (
    "Structural stop. LONG: just below the confirmed higher-low anchor "
    "(anchor_low * (1 - stop_buffer_frac)). SHORT: just above the confirmed "
    "lower-high anchor. If that anchor breaks, the structure that justified the trade "
    "is invalidated and the position is out -- no averaging down.")

# --- 4. EXACT exit rule -----------------------------------------------------
EXIT_RULE = (
    "Patience: let winners run while structure holds. Exit on a MARKET-STRUCTURE "
    "SHIFT against the position -- LONG exits when a confirmed LOWER LOW forms "
    "(uptrend structure broken / change-of-character); SHORT mirror -- or when the "
    "structural stop is hit. No fixed time/horizon exit; no indicator exit.")

# --- 5. EXACT pyramiding / add-to-winners rule ------------------------------
PYRAMID_RULE = (
    "Add to WINNERS ONLY after profit confirmation: add ONE unit only when (a) the "
    "position is already in OPEN PROFIT, AND (b) a NEW higher-low (long) / lower-high "
    "(short) confirms trend continuation. On each add, trail the whole-position stop "
    "up to below the new anchor. NEVER add when the position is flat or at a loss; "
    "NEVER add to losers. Total size is capped at max_units_total.")

# --- 6. EXACT invalidation rule ---------------------------------------------
INVALIDATION_RULE = (
    "A setup is INVALIDATED (no entry; or immediate exit if already entered) if the "
    "structure anchor (the prior swing low for longs / swing high for shorts) is "
    "broken before confirmation, or if market structure shifts to the opposite "
    "direction (opposite trend confirmed). Invalidation is structural, not a "
    "drawdown threshold.")

# --- 7. EXACT non-overlap rule ----------------------------------------------
NON_OVERLAP_RULE = (
    "At most max_concurrent_positions_per_symbol (= 1) live position per symbol. A "
    "new base entry cannot open while a position is live; pyramiding adds belong to "
    "the SAME position (one trade lifecycle), not separate overlapping trades. Trades "
    "are non-overlapping per symbol by construction.")

# --- sub-families declared in the proposal (variants to compare later) ------
SUB_FAMILIES = tuple(s["key"] for s in _c18p.SUB_FAMILIES)

# --- evaluation metrics (risk-adjusted) -------------------------------------
EVALUATION_METRICS = {
    "primary_risk_adjusted": ("sharpe_ratio", "calmar_ratio", "max_drawdown"),
    "trend_following_diagnostics": ("net_return", "profit_factor", "win_rate",
                                    "avg_R_per_trade", "trade_frequency_low",
                                    "pyramiding_contribution"),
    "baseline": "matched per-symbol buy-and-hold over the same window, net of cost",
    "win_condition": ("BEAT buy-and-hold on a RISK-ADJUSTED basis (Sharpe and/or "
                      "Calmar, no worse drawdown) AND survive forward-OOS -- not "
                      "merely positive raw return"),
    "patience_is_a_requirement_not_a_parameter": True,
}

# --- cost (reserved for the replay gate) ------------------------------------
FEE_ROUND_TRIP_BPS = 27.0
SLIPPAGE_ROUND_TRIP_BPS = 10.0
ALL_IN_ROUND_TRIP_BPS = FEE_ROUND_TRIP_BPS + SLIPPAGE_ROUND_TRIP_BPS  # 37.0
COST_RESERVED = {
    "crypto_all_in_round_trip_bps": ALL_IN_ROUND_TRIP_BPS,
    "applied_at_replay_gate_only": True,
    "applied_here": False,
    "xauusd_cost_to_be_sourced_separately": True,
}

# --- future data requirements (recorded, NOT fetched) -----------------------
DATA_REQUIREMENTS = {
    "h4_ohlc_btcusd": {"required": True, "available_locally": False,
                       "note": "current local data is BTC/ETH/SOL DAILY only"},
    "h4_ohlc_eth_sol": {"required": False, "available_locally": False},
    "h4_ohlc_xauusd": {"required": False, "available_locally": False,
                       "note": "gold; OUTSIDE the crypto-D1 lane; separate sourcing "
                               "+ its own human approval"},
    "no_data_fetched_here": True,
    "data_sourcing_requires_separate_human_approval": True,
}

# --- out-of-sample validation -----------------------------------------------
OOS_VALIDATION = {
    "forward_oos_required": True,
    "forward_oos_window": "unseen_continuation",
    "forward_oos_must_hold_risk_adjusted_edge": True,
    "no_parameter_optimization": True,
    "no_in_sample_only_fit": True,
}

# --- rejection criteria (decisive, evaluated only at the replay gate) -------
REJECTION_CRITERIA = {
    "reject_if_not_beat_buy_and_hold_risk_adjusted": True,
    "reject_if_max_drawdown_worse_than_buy_and_hold": True,
    "reject_if_forward_oos_risk_adjusted_edge_fails": True,
    "reject_if_trade_frequency_not_low": True,        # patience requirement
    "reject_if_pyramiding_adds_to_losers": True,
    "raw_return_alone_is_not_sufficient": True,
}

NEXT_HUMAN_GATE_AFTER_SPEC = (
    "HUMAN_DECISION_C18_ADVANCE_TO_DETECTOR_SPEC_DRY_RUN_OR_REJECT")

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "builds_candidate_files", "runs_detector",
    "runs_labels", "runs_replay", "runs_backtest", "computes_pnl",
    "optimizes_parameters", "reparameterizes", "runs_robustness", "fetches_data",
    "reads_real_data", "mutates_data", "stages_data", "auto_commits", "auto_pushes",
    "modifies_scheduler", "sends_notifications", "calls_api", "uses_network",
    "uses_credentials", "connects_broker", "connects_exchange", "uses_real_money",
    "places_orders", "contains_order_logic", "uses_indicators_as_primary_signal",
    "adds_to_losers", "allows_overlapping_positions", "paper_trading",
    "live_trading", "deploys_capital", "promotes_gate", "unlocks_downstream_gate",
    "skips_any_gate", "claims_friends_exact_system",
    "advances_without_human_approval", "claims_profitability", "claims_edge",
    "crosses_into_forbidden_gate",
)


def _scope_locks() -> dict[str, bool]:
    return {
        "no_build": True, "no_write": True, "no_execute": True,
        "no_detector": True, "no_labels": True, "no_replay": True,
        "no_backtest": True, "no_pnl": True, "no_optimization": True,
        "no_reparameterization": True, "no_robustness": True, "no_data_fetch": True,
        "no_real_data_access": True, "no_stage": True, "no_commit": True,
        "no_push": True, "no_auto_commit": True, "no_auto_push": True,
        "no_scheduler_change": True, "no_broker": True, "no_credentials": True,
        "no_order_logic": True, "no_indicators_as_primary": True,
        "no_add_to_losers": True, "no_overlapping_positions": True,
        "no_paper_trading": True, "no_live_trading": True, "no_gate_skip": True,
        "no_friends_exact_system_claim": True, "no_downstream_gate_unlock": True,
        "no_profitability_claim": True, "no_crossing_into_forbidden_gate": True,
    }


def get_candidate_18_spec_label() -> str:
    return (
        "Candidate #18 h4_trend_following_market_structure_v1 (READ-ONLY, RESEARCH "
        "ONLY, PURE CANDIDATE SPEC). EXACT H4 market-structure trend-following rules "
        "(no-indicator trend definition, pullback entry, structural stop, "
        "structure-shift exit, profit-confirmed add-to-winners, structural "
        "invalidation, one-position-per-symbol non-overlap) -- an OBJECTIVE TESTABLE "
        "APPROXIMATION of an observed profitable trader, NOT their exact system. SPEC "
        "ONLY: the next gate (detector spec + synthetic dry-run) needs an explicit "
        "human decision. NO data fetch, NO detector, NO labels, NO replay, NO PnL, NO "
        "optimization, NO paper/live. NOT a profitability claim.")


def get_candidate_18_spec_next_action() -> str:
    return NEXT_HUMAN_GATE_AFTER_SPEC


def build_c18_spec(repo_root: Any = ".",
                   tracked_paths: list | None = None) -> dict[str, Any]:
    """Assemble the frozen Candidate #18 candidate-spec record. Pure; no I/O; spec
    only. Chain-gated on the committed C18 proposal (frozen, this exact family)."""
    proposal = _c18p.build_c18_proposal(repo_root, tracked_paths)
    proposal_valid = _c18p.validate_c18_proposal(proposal)["valid"]
    proposal_verdict = proposal.get("verdict")
    proposal_family = proposal.get("candidate_family")

    blockers: list = []
    if not proposal_valid:
        blockers.append("c18_proposal_invalid")
    if proposal_verdict != EXPECTED_PROPOSAL_VERDICT:
        blockers.append("c18_proposal_not_frozen")
    if proposal_family != CANDIDATE_FAMILY:
        blockers.append("proposal_family_mismatch")

    record: dict[str, Any] = {
        "schema_version": C18S_SCHEMA_VERSION, "mode": C18S_MODE, "lane": C18S_LANE,
        "label": get_candidate_18_spec_label(),
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "candidate_name": CANDIDATE_NAME,
        "is_pure_spec_only": True,
        "blockers": blockers,
        "verdict": ("C18_SPEC_FROZEN_FOR_HUMAN_REVIEW" if not blockers
                    else "C18_SPEC_BLOCKED"),
        # chain provenance
        "source_proposal_verdict": proposal_verdict,
        "source_proposal_valid": proposal_valid,
        "source_proposal_family": proposal_family,
        # HONESTY -- objective approximation, not the exact system
        "is_objective_testable_approximation": True,
        "is_observed_traders_exact_system": False,
        "honesty_statement": (
            "Exact entries/stops/add-points are unavailable; these are an objective, "
            "testable approximation of the observed behaviour, NOT a reproduction of "
            "a specific system."),
        # the spec
        "gate_sequence": list(GATE_SEQUENCE),
        "gate_sequence_preserved_unchanged": True,
        "timeframe": TIMEFRAME,
        "initial_testable_symbols": list(INITIAL_TESTABLE_SYMBOLS),
        "optional_in_lane_proxies": list(OPTIONAL_IN_LANE_PROXIES),
        "observed_but_out_of_lane": list(OBSERVED_BUT_OUT_OF_LANE),
        "higher_timeframe_filter": HIGHER_TIMEFRAME_FILTER,
        "spec_params": dict(SPEC_PARAMS),
        # the EXACT rules
        "trend_rule": TREND_RULE,
        "entry_rule": ENTRY_RULE,
        "stop_rule": STOP_RULE,
        "exit_rule": EXIT_RULE,
        "pyramid_rule": PYRAMID_RULE,
        "invalidation_rule": INVALIDATION_RULE,
        "non_overlap_rule": NON_OVERLAP_RULE,
        "sub_families": list(SUB_FAMILIES),
        # identity
        "is_h4_market_structure": True,
        "uses_indicators_as_primary": False,
        "is_low_frequency_patience_gated": True,
        "pyramids_only_on_confirmed_winners": True,
        "positions_non_overlapping_per_symbol": True,
        # evaluation + cost reserved
        "evaluation_metrics": _deepish(EVALUATION_METRICS),
        "cost_reserved": dict(COST_RESERVED),
        "fee_round_trip_bps": FEE_ROUND_TRIP_BPS,
        "slippage_round_trip_bps": SLIPPAGE_ROUND_TRIP_BPS,
        "all_in_round_trip_bps": ALL_IN_ROUND_TRIP_BPS,
        # future data requirements (nothing fetched)
        "data_requirements": _deepish(DATA_REQUIREMENTS),
        # OOS + rejection criteria
        "oos_validation": dict(OOS_VALIDATION),
        "rejection_criteria": dict(REJECTION_CRITERIA),
        "next_human_gate_after_spec": NEXT_HUMAN_GATE_AFTER_SPEC,
        "human_review_required": True,
        "current_loop_stage": "candidate_spec",
        "next_required_action": NEXT_HUMAN_GATE_AFTER_SPEC,
        # downstream gates locked
        "detector_gate_locked": True, "labels_gate_locked": True,
        "replay_gate_locked": True, "paper_trading_gate_locked": True,
        "live_gate_locked": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = _scope_locks()
    return record


def _deepish(d: dict) -> dict:
    out: dict = {}
    for k, v in d.items():
        out[k] = dict(v) if isinstance(v, dict) else v
    return out


def validate_c18_spec(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the spec is research-only, pure-spec-
    only, chain-gated on the frozen C18 proposal for this exact family, carries the
    honesty disclosure (objective approximation, NOT the exact system), defines all
    seven EXACT rules (trend / entry / stop / exit / pyramiding / invalidation /
    non-overlap) with the H4 market-structure identity (no indicators primary, low
    frequency, pyramids only on winners, non-overlap), records the future data
    requirements (nothing fetched), reserves the 37 bps replay cost, carries the
    risk-adjusted evaluation + OOS + rejection criteria, preserves the gate sequence,
    keeps downstream gates locked, and pins every capability flag False."""
    failures: list = []
    if record.get("mode") != C18S_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_pure_spec_only") is not True:
        failures.append("not_pure_spec_only")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("verdict") != "C18_SPEC_FROZEN_FOR_HUMAN_REVIEW":
        failures.append("verdict_not_frozen")

    # chain gate
    if record.get("source_proposal_verdict") != EXPECTED_PROPOSAL_VERDICT:
        failures.append("proposal_not_frozen")
    if record.get("source_proposal_valid") is not True:
        failures.append("proposal_not_valid")
    if record.get("source_proposal_family") != CANDIDATE_FAMILY:
        failures.append("proposal_family_mismatch")

    # HONESTY
    if record.get("is_objective_testable_approximation") is not True:
        failures.append("must_be_objective_approximation")
    if record.get("is_observed_traders_exact_system") is not False:
        failures.append("must_not_claim_exact_system")
    if not record.get("honesty_statement"):
        failures.append("honesty_statement_missing")

    # the SEVEN exact rules present
    for field in ("trend_rule", "entry_rule", "stop_rule", "exit_rule",
                  "pyramid_rule", "invalidation_rule", "non_overlap_rule"):
        if not record.get(field):
            failures.append("rule_missing_%s" % field)
    # rule content anchors (the observed behaviour)
    if "no indicators" not in str(record.get("trend_rule", "")).lower():
        failures.append("trend_rule_not_no_indicator")
    if "higher low" not in str(record.get("entry_rule", "")).lower():
        failures.append("entry_rule_not_structure_pullback")
    if "structural stop" not in str(record.get("stop_rule", "")).lower():
        failures.append("stop_rule_not_structural")
    pyr = str(record.get("pyramid_rule", "")).lower()
    if "profit" not in pyr or "never add to losers" not in pyr:
        failures.append("pyramid_rule_not_profit_confirmed_no_losers")
    if "opposite" not in str(record.get("invalidation_rule", "")).lower():
        failures.append("invalidation_rule_incomplete")
    if "non-overlapping" not in str(record.get("non_overlap_rule", "")).lower():
        failures.append("non_overlap_rule_incomplete")

    # identity
    if record.get("is_h4_market_structure") is not True:
        failures.append("not_h4_market_structure")
    if record.get("uses_indicators_as_primary") is not False:
        failures.append("indicators_must_not_be_primary")
    if record.get("is_low_frequency_patience_gated") is not True:
        failures.append("not_low_frequency")
    if record.get("pyramids_only_on_confirmed_winners") is not True:
        failures.append("must_pyramid_only_on_winners")
    if record.get("positions_non_overlapping_per_symbol") is not True:
        failures.append("positions_must_be_non_overlapping")
    sp = record.get("spec_params") or {}
    if sp.get("uses_indicators") is not False:
        failures.append("spec_params_indicators_on")
    if sp.get("max_concurrent_positions_per_symbol") != 1:
        failures.append("non_overlap_param_wrong")
    if sp.get("no_parameter_optimization") is not True:
        failures.append("optimization_not_forbidden_in_params")

    # timeframe + lane/data limits
    if record.get("timeframe") != "H4":
        failures.append("timeframe_not_h4")
    if "XAUUSD" not in (record.get("observed_but_out_of_lane") or []):
        failures.append("xauusd_not_flagged_out_of_lane")
    dr = record.get("data_requirements") or {}
    if dr.get("no_data_fetched_here") is not True:
        failures.append("data_fetch_flag_wrong")
    if (dr.get("h4_ohlc_btcusd") or {}).get("available_locally") is not False:
        failures.append("h4_btc_should_not_be_local")

    # cost reserved (37 bps, not applied here)
    cr = record.get("cost_reserved") or {}
    if cr.get("crypto_all_in_round_trip_bps") != 37.0:
        failures.append("cost_model_tampered")
    if cr.get("applied_here") is not False:
        failures.append("cost_must_not_be_applied_here")
    if cr.get("applied_at_replay_gate_only") is not True:
        failures.append("cost_not_reserved_for_replay")

    # OOS + rejection criteria (risk-adjusted; raw return not sufficient)
    oos = record.get("oos_validation") or {}
    if oos.get("forward_oos_required") is not True:
        failures.append("forward_oos_not_required")
    if oos.get("no_parameter_optimization") is not True:
        failures.append("optimization_not_forbidden")
    rc = record.get("rejection_criteria") or {}
    for k in ("reject_if_not_beat_buy_and_hold_risk_adjusted",
              "reject_if_forward_oos_risk_adjusted_edge_fails",
              "reject_if_trade_frequency_not_low",
              "reject_if_pyramiding_adds_to_losers",
              "raw_return_alone_is_not_sufficient"):
        if rc.get(k) is not True:
            failures.append("rejection_criterion_off_%s" % k)
    em = record.get("evaluation_metrics") or {}
    for m in ("sharpe_ratio", "calmar_ratio", "max_drawdown"):
        if m not in (em.get("primary_risk_adjusted") or ()):
            failures.append("primary_metric_missing_%s" % m)

    # gate sequence + next gate + downstream locks
    if list(record.get("gate_sequence") or []) != list(GATE_SEQUENCE):
        failures.append("gate_sequence_tampered")
    if record.get("next_required_action") != NEXT_HUMAN_GATE_AFTER_SPEC:
        failures.append("next_action_not_detector_gate")
    for gate in ("detector_gate_locked", "labels_gate_locked",
                 "replay_gate_locked", "paper_trading_gate_locked",
                 "live_gate_locked"):
        if record.get(gate) is not True:
            failures.append("downstream_gate_unlocked_%s" % gate)

    locks = record.get("scope_locks") or {}
    for key in ("no_build", "no_detector", "no_labels", "no_replay", "no_pnl",
                "no_optimization", "no_data_fetch", "no_commit", "no_push",
                "no_broker", "no_order_logic", "no_indicators_as_primary",
                "no_add_to_losers", "no_overlapping_positions", "no_paper_trading",
                "no_live_trading", "no_gate_skip"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
