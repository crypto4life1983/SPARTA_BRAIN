"""Candidate #22 -- external_signum_trend_radar_gc_long_short_v1
-- FAMILY PROPOSAL (PURE, RESEARCH ONLY).

The formal candidate-family proposal for the human-approved C22 research direction
(HUMAN_DECISION_OPEN_CANDIDATE_22_FAMILY_PROPOSAL_OR_HOLD -> OPEN_CANDIDATE_22_FAMILY_
PROPOSAL). Chain-gated on the committed candidate-research-lane being at the Candidate #22
family-proposal READINESS state: C21 rejected (kept on record), NO active candidate,
rejected ledger C1-C21 (26), next_required_action == the C22 readiness token.

SOURCE (EXTERNAL, REFERENCE-ONLY): a user-provided Signum strategy prompt
"TR-GC-Crypto-LS-2" for Bot ID 25792. This proposal treats that prompt purely as an
EXTERNAL CLAIM to be independently VALIDATED under SPARTA's own fee-honest gates. It does
NOT connect to Signum, does NOT use MCP, does NOT access Hyperliquid, sends NO trades,
edits NO bots, creates NO Claude routines, and uses NO API keys / credentials. The EXACT
rule set (Trend-Radar composite trend signal + GC confirmation + long/short logic +
parameters) is transcribed VERBATIM and READ-ONLY at the separate candidate-spec gate --
this proposal declares the family at the thesis level only and invents no specific rule
numbers.

THESIS (honest, external-validation framing): internal directional trend/momentum families
have REPEATEDLY FAILED SPARTA's fee-honest replay -- C5 (long-biased trend continuation),
C14 (conviction-bar follow-through, beat random but lost to buy-and-hold + failed OOS),
C15 (slow vol-targeted TS-momentum, lost to buy-and-hold), C18 (H4 trend-following, +95.4%
but failed BTC buy-and-hold risk-adjusted + OOS). C22 is therefore NOT another internal
trend derivation; it is an EXTERNAL-STRATEGY VALIDATION candidate whose DISTINCT axis is:
an independently-developed, productized THIRD-PARTY multi-confirmation trend system
(Trend-Radar + GC), evaluated SYMMETRICALLY LONG/SHORT (not long-biased), as a faithful
replication held to the exact gates the internal trend attempts failed. The value is
adjudicating an external claim with the same rigor -- the prior is SKEPTICAL (directional
crypto trend is a graveyard), and an edge must be PROVEN net of cost vs random/null AND
buy-and-hold AND in forward-OOS, not assumed because a vendor productized it.

It is a PROPOSAL only: it DECLARES the family thesis, the external source + read-only
boundary, why it is materially different from the rejected C1-C21 families (with an honest
directional-trend-graveyard disclosure), the universe/timeframe (to be confirmed at spec),
six evaluation VARIANTS/ABLATIONS to compare, the evaluation metrics (vs random/null AND
buy-and-hold, risk-adjusted, turnover-aware, forward-OOS), the cost assumptions (reserved
for replay), the data boundary (frozen/own data only; no Signum/exchange fetch), the
out-of-sample requirement, the safety boundaries, and the next human gate. It builds NO
spec, NO detector, NO labels, NO replay; runs NO PnL/optimization/tuning/data fetch;
connects NOTHING; touches NO paper/live/broker/order/scheduler surface; and does NOT
advance itself. Every capability flag is pinned False with a full scope_locks set.
Advancing to the candidate-spec gate needs an explicit human decision.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.crypto_d1_candidate_research_lane_status_v1_contract as _lane
import sparta_commander.research_expansion_plan_v1_contract as _rep

C22_SCHEMA_VERSION = 1
C22_MODE = "RESEARCH_ONLY"
C22_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = "C22"
CANDIDATE_TOKEN = "C22_EXTERNAL_SIGNUM_TREND_RADAR_GC_LONG_SHORT_V1"
CANDIDATE_FAMILY = "external_signum_trend_radar_gc_long_short"
CANDIDATE_NAME = "external_signum_trend_radar_gc_long_short_v1"

REJECTED_FAMILIES_C1_TO_C21 = tuple(_rep.REJECTED_FAMILIES_C1_TO_C21)   # 26
LANE_C22_READINESS_TOKEN = "HUMAN_DECISION_OPEN_CANDIDATE_22_FAMILY_PROPOSAL_OR_HOLD"

# --- the preserved, frozen gate sequence (each stage human-gated) -----------
GATE_SEQUENCE = (
    "family_proposal", "candidate_spec", "detector_spec_dry_run",
    "real_candle_labels_review", "fee_honest_replay_review",
    "rejection_or_promote_decision",
)

# --- the EXTERNAL source (reference-only; nothing connected) -----------------
EXTERNAL_SOURCE = {
    "provider": "Signum",
    "strategy_prompt_id": "TR-GC-Crypto-LS-2",
    "bot_id": "25792",
    "provided_by": "user",
    "treated_as": "EXTERNAL_CLAIM_TO_BE_INDEPENDENTLY_VALIDATED",
    "reference_only_not_connected": True,
    "exact_rules_transcribed_verbatim_readonly_at_spec_gate": True,
    "no_rule_numbers_invented_in_this_proposal": True,
    # hard boundaries on the external integration surface
    "connects_to_signum": False,
    "uses_mcp": False,
    "accesses_hyperliquid": False,
    "sends_trades": False,
    "edits_bots": False,
    "creates_claude_routines": False,
    "uses_api_keys_or_credentials": False,
}

# --- 1. family thesis (external-validation, skeptical prior) ----------------
FAMILY_THESIS = (
    "Independently VALIDATE an external, productized third-party crypto trend system "
    "(Signum 'Trend-Radar + GC', evaluated SYMMETRICALLY LONG/SHORT) under SPARTA's own "
    "fee-honest gates. This is NOT a new internal trend derivation: it is an EXTERNAL "
    "claim treated as a faithful replication, held to the exact gates that the internal "
    "directional families (C5/C14/C15/C18) failed. The DISTINCT axis is the external, "
    "independently-developed, multi-confirmation trend signal + symmetric long/short "
    "execution -- the hypothesis being that a third-party composite confirmation system "
    "may avoid the single-mechanism long-biased pitfalls that sank the internal attempts. "
    "The prior is SKEPTICAL: directional crypto trend is a graveyard; any edge must be "
    "PROVEN net of cost vs random/null AND buy-and-hold AND in forward-OOS, never assumed "
    "because a vendor productized it.")

# --- 2. why materially different from C1-C21 (HONEST disclosure) ------------
WHY_DIFFERENT_FROM_C1_C21 = (
    "HONEST DIRECTIONAL-TREND DISCLOSURE: internal directional trend/momentum families "
    "were repeatedly REJECTED at fee-honest replay -- C5 long-biased trend continuation, "
    "C14 conviction-bar follow-through (beat random but lost to buy-and-hold + failed "
    "OOS), C15 slow vol-targeted TS-momentum (lost to buy-and-hold), C18 H4 "
    "trend-following (+95.4% but failed BTC buy-and-hold risk-adjusted + OOS). C22 does "
    "NOT assume it escapes this; it is explicitly designed to be ADJUDICATED against the "
    "same gates",
    "DISTINCT EDGE AXIS = EXTERNAL PRODUCTIZED MULTI-CONFIRMATION SIGNAL: the rule set "
    "is an independently-developed third-party system (Trend-Radar + GC confirmation), "
    "not a SPARTA-internal derivation -- the candidate tests whether an external composite "
    "confirmation system has an edge the internal single-mechanism attempts lacked",
    "SYMMETRIC LONG/SHORT, not long-biased: unlike C5 (long-biased) and the largely "
    "long-tilted internal attempts, C22 trades BOTH directions, so it is judged on short "
    "as well as long performance and is not merely a dressed-up bull-beta proxy",
    "EXTERNAL-VALIDATION METHODOLOGY (replication, not invention): C22 is a faithful "
    "replication-and-test of a specified external system, NOT a re-parameterization of a "
    "rejected internal family; the exact rules are transcribed read-only at the spec gate "
    "and held fixed -- it cannot be a retune of C5/C14/C15/C18 because it does not reuse "
    "their rules at all",
    "NOT a market-neutral carry family (C16/C19/C20/C21): C22 is DIRECTIONAL with net "
    "market exposure, so buy-and-hold IS a mandatory benchmark here (it was not for the "
    "neutral-carry families) -- a different evaluation contract entirely",
)

# --- 3. identity (directional, external, long/short) ------------------------
STRATEGY_IDENTITY = {
    "is_external_sourced": True,
    "is_replication_and_validation_of_external_claim": True,
    "is_directional": True,
    "is_long_short_symmetric": True,
    "is_long_biased": False,
    "is_market_neutral": False,
    "carries_net_market_beta": True,
    "return_source_is_directional_trend_timing": True,
    "is_internal_derivation": False,
    "is_reparameterization_of_a_rejected_family": False,
    "distinct_edge_axis": "external_productized_multi_confirmation_trend_radar_long_short",
    "skeptical_prior_directional_trend_is_a_graveyard": True,
}

# --- 4. the six evaluation VARIANTS / ABLATIONS to compare ------------------
# (these are evaluation comparisons of the FAITHFUL external rules, NOT parameter retunes)
EVALUATION_VARIANTS = (
    {"key": "faithful_replication_as_specified",
     "desc": "the external Trend-Radar + GC long/short rules transcribed verbatim and "
             "run exactly as specified (the primary object under test)"},
    {"key": "fee_honest_cost_overlay",
     "desc": "the same faithful rules with SPARTA's fee-honest crypto perp cost + "
             "slippage + funding model applied (the decisive net-of-cost view)"},
    {"key": "long_short_vs_long_only_ablation",
     "desc": "compare symmetric long/short against a long-only restriction to isolate "
             "whether the short side adds genuine edge or just bull beta"},
    {"key": "trend_radar_only_vs_plus_gc_confirmation_ablation",
     "desc": "compare the Trend-Radar signal alone vs Trend-Radar + GC confirmation to "
             "test whether the multi-confirmation actually improves net-of-cost result"},
    {"key": "turnover_capped_variant",
     "desc": "the faithful rules with an explicit round-trip / turnover cap, to test "
             "robustness to the cost drag that sank C18/C20-style churn"},
    {"key": "forward_oos_holdout",
     "desc": "the faithful rules evaluated only on an unseen forward-OOS window, never "
             "fit in-sample -- the durability test the internal trend families failed"},
)

# --- 5. evaluation metrics (directional: vs random/null AND buy-and-hold) ---
EVALUATION_METRICS = {
    "primary_directional": ("net_return_after_cost", "beats_random_entry",
                            "beats_buy_and_hold_risk_adjusted"),
    "long_short_diagnostics": ("long_side_net", "short_side_net",
                               "short_adds_edge_over_long_only"),
    "risk_adjusted": ("sharpe_ratio", "calmar_ratio", "max_drawdown"),
    "turnover_efficiency": ("round_trips_per_year", "all_in_cost_drag",
                            "cost_drag_as_share_of_gross"),
    "baseline": ("a random/zero-edge entry null AND BUY-AND-HOLD (mandatory here because "
                 "the strategy carries net market beta), net of all-in cost"),
    "win_condition": ("a NET-POSITIVE edge after cost that beats random entry AND beats "
                      "buy-and-hold on a RISK-ADJUSTED basis AND survives forward-OOS -- "
                      "the exact bar C14/C15/C18 failed; beating random alone is "
                      "necessary but NOT sufficient"),
    "buy_and_hold_is_mandatory_benchmark": True,
    "low_turnover_is_evaluation_dimension": True,
    "judged_against_buy_and_hold": True,
}

# --- 6. cost assumptions (reserved for replay) ------------------------------
FEE_ROUND_TRIP_BPS = 27.0
SLIPPAGE_ROUND_TRIP_BPS = 10.0
ALL_IN_ROUND_TRIP_BPS = FEE_ROUND_TRIP_BPS + SLIPPAGE_ROUND_TRIP_BPS   # 37.0
COST_ASSUMPTIONS = {
    "all_in_round_trip_bps": ALL_IN_ROUND_TRIP_BPS,
    "directional_single_leg_per_entry": True,
    "funding_paid_on_held_perp_exposure_reserved_for_replay": True,
    "cost_applied_only_at_replay_gate": True,
    "applied_here": False,
    "turnover_is_a_first_class_cost_risk": (
        "directional trend systems can over-trade; the turnover-capped variant + the "
        "cost overlay exist specifically to expose cost drag before any promotion"),
}

# --- 7. data boundary (own/frozen data only; no Signum/exchange fetch) ------
DATA_REQUIREMENTS = {
    "uses_own_or_frozen_data_only": True,
    "no_signum_connection": True,
    "no_exchange_or_hyperliquid_fetch": True,
    "no_mcp": True,
    "no_api_keys_or_credentials": True,
    "exact_universe_and_timeframe_confirmed_at_spec_gate": True,
    "no_new_data_fetched_in_this_proposal": True,
}

# --- 8. out-of-sample validation requirement --------------------------------
OOS_VALIDATION = {
    "forward_oos_required": True,
    "forward_oos_window": "unseen_continuation_holdout",
    "forward_oos_must_beat_buy_and_hold_risk_adjusted": True,
    "no_parameter_optimization": True,
    "no_in_sample_only_fit": True,
    "faithful_external_rules_held_fixed": True,
}

# --- 9. safety boundaries ---------------------------------------------------
SAFETY_BOUNDARIES = (
    "research-only: no paper trading, no live trading, no broker/exchange, no orders, "
    "no credentials, no data fetch, no scheduler in this proposal",
    "EXTERNAL INTEGRATION HARD-LOCKED: no Signum connection, no MCP, no Hyperliquid "
    "access, no API keys, no bot edits, no Claude routines, no sending trades -- the "
    "Signum prompt is a reference-only external claim",
    "DIRECTIONAL with net market beta: buy-and-hold is a MANDATORY benchmark; an edge "
    "must beat random/null AND buy-and-hold AND hold forward-OOS, net of cost -- the "
    "internal trend families (C5/C14/C15/C18) failed exactly this bar",
    "FAITHFUL REPLICATION, not invention: the exact external rules are transcribed "
    "verbatim and READ-ONLY at the spec gate and held fixed; no re-parameterization of "
    "any rejected internal family",
    "no spec / detector / labels / replay / optimization / tuning in or after this "
    "proposal until each downstream gate is separately human-approved; promotion requires "
    "beating buy-and-hold risk-adjusted net of cost AND forward-OOS; this proposal "
    "advances NOTHING and connects NOTHING",
)

NEXT_HUMAN_GATE_AFTER_PROPOSAL = (
    "HUMAN_DECISION_C22_ADVANCE_TO_CANDIDATE_SPEC_OR_REJECT")

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "builds_candidate_files", "builds_spec",
    "runs_detector", "runs_labels", "runs_replay", "runs_backtest", "computes_pnl",
    "optimizes_parameters", "reparameterizes", "tunes_parameters", "runs_rescue",
    "reproposes_rejected_family", "runs_robustness", "fetches_data", "reads_real_data",
    "mutates_data", "stages_data", "auto_commits", "auto_pushes", "modifies_scheduler",
    "installs_scheduler", "sends_notifications", "calls_api", "uses_network",
    "uses_credentials", "uses_api_keys", "connects_signum", "uses_mcp",
    "accesses_hyperliquid", "connects_broker", "connects_exchange", "sends_trades",
    "edits_bots", "creates_claude_routines", "uses_real_money", "places_orders",
    "contains_order_logic", "adds_new_instrument_class", "paper_trading",
    "live_trading", "deploys_capital", "promotes_gate", "unlocks_downstream_gate",
    "skips_any_gate", "advances_without_human_approval", "claims_profitability",
    "claims_edge", "crosses_into_forbidden_gate",
)


def get_candidate_22_proposal_label() -> str:
    return (
        "Candidate #22 external_signum_trend_radar_gc_long_short_v1 family proposal "
        "(READ-ONLY, RESEARCH ONLY, PURE PROPOSAL). Independently VALIDATE an external "
        "Signum 'Trend-Radar + GC' crypto LONG/SHORT system (prompt TR-GC-Crypto-LS-2, "
        "Bot 25792) under SPARTA's own fee-honest gates -- reference-only, NOT connected "
        "to Signum/MCP/Hyperliquid, no trades, no bot edits, no credentials. HONEST prior: "
        "internal directional trend families (C5/C14/C15/C18) all FAILED fee-honest "
        "replay; C22's distinct axis is an external productized multi-confirmation signal "
        "+ symmetric long/short, held to the same gates (beat random AND buy-and-hold AND "
        "forward-OOS, net of cost). PROPOSAL ONLY: advancing to the candidate-spec gate "
        "needs an explicit human decision. NO spec/detector/labels/replay, NO "
        "optimization, NO data fetch, NO connection, NO paper/live. NOT a profitability "
        "claim.")


def get_candidate_22_proposal_next_action() -> str:
    return NEXT_HUMAN_GATE_AFTER_PROPOSAL


def _deepish(d: dict) -> dict:
    out: dict = {}
    for k, v in d.items():
        out[k] = dict(v) if isinstance(v, dict) else v
    return out


def build_c22_proposal() -> dict[str, Any]:
    """Assemble the frozen Candidate #22 family-proposal record. Pure; no I/O; proposal
    only. Chain-gated on the committed lane being at the C22 family-proposal READINESS
    state (C21 rejected, no active candidate, ledger C1-C21 = 26)."""
    lane = _lane.get_lane_status()
    lane_valid = _lane.validate_lane_status(lane)["valid"]
    nxt = lane.get("next_candidate_readiness") or {}
    last_rej = lane.get("last_rejected_candidate_detail") or {}

    blockers: list = []
    if not lane_valid:
        blockers.append("lane_status_invalid")
    if lane.get("active_candidate") is not None:
        blockers.append("lane_has_active_candidate")
    if lane.get("next_required_action") != LANE_C22_READINESS_TOKEN:
        blockers.append("lane_not_at_c22_proposal_readiness")
    if nxt.get("candidate") != "C22":
        blockers.append("lane_next_candidate_not_c22")
    if lane.get("last_rejected_candidate") != "C21":
        blockers.append("c21_not_last_rejected")
    if last_rej.get("verdict") != "C21_REJECTED_AT_FEE_HONEST_REPLAY":
        blockers.append("c21_not_rejected_at_replay")
    if lane.get("rejected_ledger_count") != 26:
        blockers.append("ledger_not_26")
    if CANDIDATE_FAMILY in REJECTED_FAMILIES_C1_TO_C21:
        blockers.append("candidate_family_in_rejected_ledger")

    record: dict[str, Any] = {
        "schema_version": C22_SCHEMA_VERSION, "mode": C22_MODE, "lane": C22_LANE,
        "label": get_candidate_22_proposal_label(),
        "candidate_id": CANDIDATE_ID, "candidate_token": CANDIDATE_TOKEN,
        "candidate_family": CANDIDATE_FAMILY, "candidate_name": CANDIDATE_NAME,
        "is_pure_proposal_only": True,
        "blockers": blockers,
        "verdict": ("C22_PROPOSAL_FROZEN_FOR_HUMAN_REVIEW" if not blockers
                    else "C22_PROPOSAL_BLOCKED"),
        # chain provenance (opened from the approved lane readiness state)
        "lane_status_valid": lane_valid,
        "lane_active_candidate": lane.get("active_candidate"),
        "lane_next_required_action": lane.get("next_required_action"),
        "lane_last_rejected_candidate": lane.get("last_rejected_candidate"),
        "opened_from_lane_c22_proposal_readiness": not blockers,
        "approved_via": LANE_C22_READINESS_TOKEN,
        # the external source + read-only boundary
        "external_source": _deepish(EXTERNAL_SOURCE),
        "is_external_sourced": True,
        "reference_only_not_connected": True,
        # the required explanation sections
        "family_thesis": FAMILY_THESIS,                                  # 1
        "why_different_from_c1_c21": list(WHY_DIFFERENT_FROM_C1_C21),     # 2
        "strategy_identity": dict(STRATEGY_IDENTITY),                     # 3
        "evaluation_variants": [dict(s) for s in EVALUATION_VARIANTS],    # 4
        "evaluation_metrics": _deepish(EVALUATION_METRICS),              # 5
        "cost_assumptions": dict(COST_ASSUMPTIONS),                      # 6
        "data_requirements": dict(DATA_REQUIREMENTS),                    # 7
        "oos_validation": dict(OOS_VALIDATION),                          # 8
        "safety_boundaries": list(SAFETY_BOUNDARIES),                    # 9
        # identity / anti-loop
        "is_directional": True,
        "is_long_short_symmetric": True,
        "is_market_neutral": False,
        "is_reparameterization_of_a_rejected_family": False,
        "honest_directional_trend_graveyard_disclosure": True,
        "distinct_edge_axis":
            "external_productized_multi_confirmation_trend_radar_long_short",
        "buy_and_hold_is_mandatory_benchmark": True,
        "gate_sequence": list(GATE_SEQUENCE),
        "gate_sequence_preserved_unchanged": True,
        "rejected_families_c1_to_c21": list(REJECTED_FAMILIES_C1_TO_C21),
        "rejected_families_count": len(REJECTED_FAMILIES_C1_TO_C21),
        "candidate_not_in_rejected_ledger":
            CANDIDATE_FAMILY not in REJECTED_FAMILIES_C1_TO_C21,
        "all_in_round_trip_bps": ALL_IN_ROUND_TRIP_BPS,
        "human_review_required": True,
        "current_loop_stage": "family_proposal",
        "next_required_action": NEXT_HUMAN_GATE_AFTER_PROPOSAL,
        "next_human_gate_after_proposal": NEXT_HUMAN_GATE_AFTER_PROPOSAL,
        "advances_nothing": True,
        # downstream gates locked
        "spec_gate_locked": True, "detector_gate_locked": True,
        "labels_gate_locked": True, "replay_gate_locked": True,
        "paper_trading_gate_locked": True, "live_gate_locked": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_build": True, "no_write": True, "no_execute": True,
        "no_spec": True, "no_detector": True, "no_labels": True, "no_replay": True,
        "no_backtest": True, "no_pnl": True, "no_optimization": True,
        "no_reparameterization": True, "no_tuning": True, "no_rescue": True,
        "no_robustness": True, "no_data_fetch": True, "no_real_data_access": True,
        "no_new_instrument_class": True, "no_stage": True, "no_commit": True,
        "no_push": True, "no_auto_commit": True, "no_auto_push": True,
        "no_scheduler_change": True, "no_scheduler_install": True,
        "no_signum_connection": True, "no_mcp": True, "no_hyperliquid": True,
        "no_api_keys": True, "no_credentials": True, "no_bot_edits": True,
        "no_claude_routines": True, "no_send_trades": True, "no_broker": True,
        "no_order_logic": True, "no_paper_trading": True, "no_live_trading": True,
        "no_gate_skip": True, "no_rejected_family_repropose": True,
        "no_downstream_gate_unlock": True, "no_profitability_claim": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_c22_proposal(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the proposal is research-only, pure-
    proposal-only, chain-gated on the lane's C22 family-proposal readiness state (C21
    rejected, no active candidate, ledger 26), an EXTERNAL reference-only validation of
    the Signum TR-GC-Crypto-LS-2 system that connects NOTHING (no Signum/MCP/Hyperliquid/
    API/credentials/orders/bots/routines), a DIRECTIONAL long/short family NOT in the
    C1-C21 (26) ledger with a distinct external-productized edge axis and an HONEST
    directional-trend-graveyard disclosure, judged vs random/null AND buy-and-hold AND
    forward-OOS (cost reserved for replay), preserves the gate sequence, keeps downstream
    gates locked, advances nothing, and pins every capability flag False."""
    failures: list = []
    if record.get("mode") != C22_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_pure_proposal_only") is not True:
        failures.append("not_pure_proposal_only")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("verdict") != "C22_PROPOSAL_FROZEN_FOR_HUMAN_REVIEW":
        failures.append("verdict_not_frozen")

    # chain gate on the lane C22 readiness state
    if record.get("lane_status_valid") is not True:
        failures.append("lane_status_not_valid")
    if record.get("lane_active_candidate") is not None:
        failures.append("lane_must_have_no_active_candidate")
    if record.get("lane_next_required_action") != LANE_C22_READINESS_TOKEN:
        failures.append("lane_not_at_c22_readiness")
    if record.get("lane_last_rejected_candidate") != "C21":
        failures.append("c21_not_last_rejected")
    if record.get("opened_from_lane_c22_proposal_readiness") is not True:
        failures.append("not_opened_from_readiness")

    # identity: candidate #22, directional long/short, external, not internal retune
    if record.get("candidate_id") != "C22":
        failures.append("candidate_id_not_c22")
    if record.get("candidate_token") != CANDIDATE_TOKEN:
        failures.append("candidate_token_mismatch")
    if record.get("candidate_family") != CANDIDATE_FAMILY:
        failures.append("family_mismatch")
    ident = record.get("strategy_identity") or {}
    for k in ("is_external_sourced", "is_replication_and_validation_of_external_claim",
              "is_directional", "is_long_short_symmetric",
              "skeptical_prior_directional_trend_is_a_graveyard"):
        if ident.get(k) is not True:
            failures.append("identity_flag_off_%s" % k)
    if ident.get("is_market_neutral") is not False:
        failures.append("must_not_be_market_neutral")
    if ident.get("is_long_biased") is not False:
        failures.append("must_not_be_long_biased")
    if ident.get("is_reparameterization_of_a_rejected_family") is not False:
        failures.append("must_not_be_reparameterization")
    if ident.get("distinct_edge_axis") != (
            "external_productized_multi_confirmation_trend_radar_long_short"):
        failures.append("distinct_edge_axis_wrong")

    # external source: reference-only, connects nothing
    ext = record.get("external_source") or {}
    if ext.get("provider") != "Signum":
        failures.append("external_provider_wrong")
    if ext.get("strategy_prompt_id") != "TR-GC-Crypto-LS-2":
        failures.append("external_prompt_id_wrong")
    if ext.get("bot_id") != "25792":
        failures.append("external_bot_id_wrong")
    if ext.get("reference_only_not_connected") is not True:
        failures.append("external_must_be_reference_only")
    if ext.get("exact_rules_transcribed_verbatim_readonly_at_spec_gate") is not True:
        failures.append("rules_must_be_transcribed_at_spec")
    for k in ("connects_to_signum", "uses_mcp", "accesses_hyperliquid", "sends_trades",
              "edits_bots", "creates_claude_routines", "uses_api_keys_or_credentials"):
        if ext.get(k) is not False:
            failures.append("external_lock_off_%s" % k)

    # materially different + HONEST disclosure
    if record.get("candidate_not_in_rejected_ledger") is not True:
        failures.append("candidate_in_rejected_ledger")
    if record.get("candidate_family") in REJECTED_FAMILIES_C1_TO_C21:
        failures.append("family_listed_as_rejected")
    if record.get("rejected_families_count") != 26:
        failures.append("ledger_not_26")
    if record.get("honest_directional_trend_graveyard_disclosure") is not True:
        failures.append("missing_honest_directional_disclosure")
    diffs = record.get("why_different_from_c1_c21") or []
    if len(diffs) < 4:
        failures.append("insufficient_difference_explanation")
    joined = " ".join(diffs)
    for must in ("C5", "C14", "C15", "C18", "EXTERNAL", "LONG/SHORT"):
        if must not in joined:
            failures.append("difference_missing_%s" % must)

    # the six evaluation variants
    subs = record.get("evaluation_variants") or []
    if len(subs) != 6:
        failures.append("evaluation_variants_not_six")
    keys = {s.get("key") for s in subs}
    for must in ("faithful_replication_as_specified", "fee_honest_cost_overlay",
                 "long_short_vs_long_only_ablation",
                 "trend_radar_only_vs_plus_gc_confirmation_ablation",
                 "turnover_capped_variant", "forward_oos_holdout"):
        if must not in keys:
            failures.append("variant_missing_%s" % must)

    # evaluation: directional -> vs random/null AND buy-and-hold (mandatory), OOS
    em = record.get("evaluation_metrics") or {}
    if "beats_buy_and_hold_risk_adjusted" not in (em.get("primary_directional") or ()):
        failures.append("missing_buy_and_hold_benchmark")
    if em.get("buy_and_hold_is_mandatory_benchmark") is not True:
        failures.append("buy_and_hold_not_mandatory")
    if em.get("judged_against_buy_and_hold") is not True:
        failures.append("must_be_judged_vs_buy_and_hold")
    for m in ("sharpe_ratio", "calmar_ratio", "max_drawdown"):
        if m not in (em.get("risk_adjusted") or ()):
            failures.append("metric_missing_%s" % m)
    if "random" not in str(em.get("win_condition", "")).lower():
        failures.append("win_condition_not_vs_random")
    if "buy-and-hold" not in str(em.get("win_condition", "")).lower():
        failures.append("win_condition_not_vs_buy_and_hold")

    # cost reserved for replay; OOS required + faithful rules held fixed
    ct = record.get("cost_assumptions") or {}
    if ct.get("all_in_round_trip_bps") != 37.0:
        failures.append("cost_model_tampered")
    if ct.get("cost_applied_only_at_replay_gate") is not True:
        failures.append("cost_not_reserved_for_replay")
    if ct.get("applied_here") is not False:
        failures.append("cost_must_not_be_applied_here")
    oos = record.get("oos_validation") or {}
    if oos.get("forward_oos_required") is not True:
        failures.append("forward_oos_not_required")
    if oos.get("forward_oos_must_beat_buy_and_hold_risk_adjusted") is not True:
        failures.append("oos_must_beat_buy_and_hold")
    if oos.get("no_parameter_optimization") is not True:
        failures.append("optimization_not_forbidden")
    if oos.get("faithful_external_rules_held_fixed") is not True:
        failures.append("rules_not_held_fixed")

    # data boundary: own/frozen only, no connection/fetch
    drq = record.get("data_requirements") or {}
    for k in ("uses_own_or_frozen_data_only", "no_signum_connection",
              "no_exchange_or_hyperliquid_fetch", "no_mcp",
              "no_api_keys_or_credentials", "no_new_data_fetched_in_this_proposal"):
        if drq.get(k) is not True:
            failures.append("data_boundary_off_%s" % k)

    # gate sequence + downstream locks + advances nothing
    if list(record.get("gate_sequence") or []) != list(GATE_SEQUENCE):
        failures.append("gate_sequence_tampered")
    if record.get("next_required_action") != NEXT_HUMAN_GATE_AFTER_PROPOSAL:
        failures.append("next_action_not_spec_gate")
    if record.get("advances_nothing") is not True:
        failures.append("must_advance_nothing")
    for gate in ("spec_gate_locked", "detector_gate_locked", "labels_gate_locked",
                 "replay_gate_locked", "paper_trading_gate_locked",
                 "live_gate_locked"):
        if record.get(gate) is not True:
            failures.append("downstream_gate_unlocked_%s" % gate)

    locks = record.get("scope_locks") or {}
    for key in ("no_build", "no_spec", "no_detector", "no_labels", "no_replay",
                "no_pnl", "no_optimization", "no_tuning", "no_rescue", "no_data_fetch",
                "no_new_instrument_class", "no_commit", "no_push",
                "no_scheduler_change", "no_scheduler_install", "no_signum_connection",
                "no_mcp", "no_hyperliquid", "no_api_keys", "no_credentials",
                "no_bot_edits", "no_claude_routines", "no_send_trades", "no_broker",
                "no_order_logic", "no_paper_trading", "no_live_trading", "no_gate_skip",
                "no_rejected_family_repropose"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
