"""SPARTA Automation Readiness -- NEXT-STRATEGY RESEARCH MEMO v1
(PURE, READ-ONLY, RESEARCH ONLY).

The first automation-readiness research OUTPUT: a human-gated next-strategy
research memo distilled from the lessons of the rejected families C1-C16. It
PREPARES the next strategy direction only -- it does NOT create a candidate (no
C17), authorizes nothing, and executes nothing.

It composes (read-only) the rejected-ledger lessons (research_expansion_plan_v1),
the automation-readiness research-prep charter, and the candidate-research-lane
status, and summarizes: what failed across C1-C16, the common failure patterns,
the now-excluded strategy types, the traits the next idea must avoid and should
prefer, 3-5 ranked next research directions, one recommended direction, why it is
different from C1-C16, and the human approval required before any candidate
proposal.

Every capability flag is pinned False with a full scope_locks set. Real-data-QA /
replay stay BLOCKED; paper / micro-live / live stay LOCKED. The next_required_action
remains BUILD_AUTOMATION_READINESS_STEP_RESEARCH_ONLY; turning a direction into a
candidate needs a separate, explicit human decision.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.research_expansion_plan_v1_contract as _rep
import sparta_commander.automation_readiness_research_prep_v1_contract as _arp
import sparta_commander.crypto_d1_candidate_research_lane_status_v1_contract as _lane

MEMO_VERSION = "v1"
MEMO_MODE = "RESEARCH_ONLY"
MEMO_LANE = "crypto_d1_auto_research"

REJECTED_FAMILIES_C1_TO_C16 = tuple(_rep.REJECTED_FAMILIES_C1_TO_C16)
REJECTED_LEDGER_COUNT = len(REJECTED_FAMILIES_C1_TO_C16)            # 21
REJECTED_FAMILY_LESSONS = dict(_rep.REJECTED_FAMILY_LESSONS)

# The next_required_action does NOT advance to a candidate; the memo is itself the
# automation-readiness research output.
NEXT_REQUIRED_ACTION = _lane.AUTOMATION_READINESS_TOKEN  # the memo's own stage
# Turning ANY direction below into a candidate requires this separate human gate.
HUMAN_APPROVAL_BEFORE_CANDIDATE = (
    "HUMAN_DECISION_APPROVE_NEXT_RESEARCH_DIRECTION_THEN_BUILD_CANDIDATE_PROPOSAL")

# --- 1. what failed across C1-C16 -------------------------------------------
WHAT_FAILED = {
    "c1_to_c9_early_variants": (
        "fvg/choch, intraday breakout-pullback, long-biased & btc/sol trend "
        "continuation, 1h swing structure, eth/sol & multi-symbol relative "
        "strength, volatility compression-expansion, liquidity-sweep and "
        "low-volume-capitulation mean reversion -- rejected for cost-non-viable "
        "risk geometry, edge failure, or long-drift dressed as edge"),
    "calendar_seasonality_c10": REJECTED_FAMILY_LESSONS["calendar_seasonality"],
    "cross_sectional_reversion_c11":
        REJECTED_FAMILY_LESSONS["cross_sectional_reversion"],
    "single_asset_reclaim_reversion_c12":
        REJECTED_FAMILY_LESSONS["single_asset_reclaim_reversion"],
    "cross_asset_lead_lag_c13": REJECTED_FAMILY_LESSONS["cross_asset_lead_lag"],
    "single_bar_conviction_continuation_c14":
        REJECTED_FAMILY_LESSONS["single_bar_conviction_continuation"],
    "slow_time_series_momentum_carry_c15":
        REJECTED_FAMILY_LESSONS["slow_time_series_momentum_carry"],
    "cointegration_pairs_market_neutral_c16":
        REJECTED_FAMILY_LESSONS["cointegration_pairs_market_neutral"],
}

# --- 2. common failure patterns ---------------------------------------------
COMMON_FAILURE_PATTERNS = (
    "BUY-AND-HOLD / LONG-BULL CARRY TRAP: directional edges reduce to crypto beta "
    "and lose to simply holding (C10, C14, C15)",
    "FORWARD-OOS COLLAPSE: in-sample looked fine, out-of-sample went negative "
    "(C11, C14)",
    "COST EROSION: net-negative after 37 bps (and worse on two legs); sometimes "
    "worse than random entry (C12, C16)",
    "STRUCTURAL RARITY: too few valid events to support a tradeable program -- "
    "rejected at the labels sample-size gate before replay (C13, C16)",
    "CONSTRUCTION DOES NOT HOLD OUT-OF-SAMPLE: e.g. a level-OLS hedge that is not "
    "return-beta-neutral on real data (C16)",
)

# --- 3. strategy types now excluded -----------------------------------------
EXCLUDED_STRATEGY_TYPES = (
    "directional trend / continuation / breakout / swing timing signals",
    "calendar / seasonality drift",
    "single-shot event mean reversion (sweep, capitulation, reclaim)",
    "cross-sectional dispersion reversion",
    "cross-asset lead-lag continuation",
    "single-bar conviction continuation",
    "slow long-only / long-bull vol-targeted time-series momentum",
    "naive cointegration pairs with an unvalidated neutrality assumption",
)

# --- 4. traits the next idea MUST AVOID -------------------------------------
TRAITS_TO_AVOID = (
    "dependence on net long / directional crypto beta (would lose to buy-and-hold)",
    "rare events that cannot clear the >=100 / >=20-per-asset / >=20-per-regime "
    "structural sample-size gate",
    "thin edges eroded by fees/slippage or multi-leg / high-turnover cost",
    "in-sample-only fit with no forward-OOS survival",
    "neutrality/hedge assumptions that are not validated out-of-sample",
    "reusing any C1-C16 mechanism (anti-loop)",
)

# --- 5. traits the next idea SHOULD PREFER ----------------------------------
TRAITS_TO_PREFER = (
    "evaluation on a RISK-ADJUSTED basis vs buy-and-hold (Sharpe / Calmar / "
    "max-drawdown), not raw return alone",
    "a continuous / frequent signal with ample sample size across bull/bear/chop",
    "low turnover so the 37 bps cost cannot dominate",
    "an edge structurally orthogonal to buy-and-hold beta (or explicitly "
    "risk-managing it)",
    "a mechanism genuinely NEW versus C1-C16, and feasible on the cached "
    "BTC/ETH/SOL D1 data without new data fetch",
    "forward-OOS survival designed in from the start",
)

# --- 6. ranked next research directions (NONE is a rejected family) ---------
NEXT_RESEARCH_DIRECTIONS = (
    {
        "key": "risk_adjusted_portfolio_construction_vol_targeted_allocation",
        "rank": 1,
        "name": "Risk-adjusted portfolio construction (vol-targeted / risk-parity "
                "allocation across BTC/ETH/SOL)",
        "rationale": ("manage ALLOCATION and risk rather than time entries; judge "
                      "on a risk-adjusted basis (Sharpe / Calmar / max-drawdown) "
                      "vs buy-and-hold -- a win is achievable without out-"
                      "predicting direction"),
        "avoids": ("carry trap (judged risk-adjusted, diversified)",
                   "rarity (continuous)", "cost erosion (low turnover)"),
        "sample_size_outlook": "ample (continuous daily allocation)",
        "evaluation_axis": "risk_adjusted_vs_buy_and_hold",
        "is_directional_timing_signal": False,
        "distinct_from_c1_c16": ("every C1-C16 candidate was a directional/MR/pairs "
                                 "TIMING signal judged on raw net return; this is a "
                                 "portfolio-construction / risk-management edge "
                                 "judged risk-adjusted -- a different mechanism AND "
                                 "a different success axis"),
    },
    {
        "key": "out_of_sample_validated_market_neutral_relative_value",
        "rank": 2,
        "name": "Out-of-sample-validated market-neutral relative value "
                "(BTC/ETH/SOL)",
        "rationale": ("a dollar/beta-neutral relative-value spread whose "
                      "NEUTRALITY is validated out-of-sample first -- fixing the "
                      "exact failure that rejected C16 -- so there is no "
                      "buy-and-hold beta to lose to"),
        "avoids": ("carry trap (market-neutral)",
                   "C16 neutrality failure (validated OOS)"),
        "sample_size_outlook": "moderate -- must clear the structural gate",
        "evaluation_axis": "net_positive_market_neutral_vs_random_and_null",
        "is_directional_timing_signal": False,
        "distinct_from_c1_c16": ("C16 assumed neutrality from a level-OLS hedge "
                                 "that failed OOS; this REQUIRES validated "
                                 "neutrality before any trading logic"),
    },
    {
        "key": "drawdown_control_regime_derisking_overlay",
        "rank": 3,
        "name": "Drawdown-control / regime de-risking overlay",
        "rationale": ("a risk OVERLAY that de-risks in confirmed risk-off regimes "
                      "to improve Calmar / max-drawdown vs buy-and-hold -- not an "
                      "entry-timing signal"),
        "avoids": ("carry trap (judged on drawdown/Calmar, not raw return)",
                   "rarity (continuous overlay)"),
        "sample_size_outlook": "ample (continuous)",
        "evaluation_axis": "calmar_and_max_drawdown_vs_buy_and_hold",
        "is_directional_timing_signal": False,
        "distinct_from_c1_c16": ("C15 was a directional regime-aware SIGNAL judged "
                                 "on raw return; this is a risk-management overlay "
                                 "judged on drawdown control"),
    },
    {
        "key": "orthogonal_residual_alpha_ensemble_meta_study",
        "rank": 4,
        "name": "Orthogonal residual-alpha ensemble meta-study (research-only)",
        "rationale": ("a purely descriptive study of whether the rejected signals "
                      "carry any orthogonal residual alpha when combined -- "
                      "informs whether an ensemble is worth proposing at all"),
        "avoids": ("premature candidate creation (study first)",),
        "sample_size_outlook": "n/a (descriptive meta-study)",
        "evaluation_axis": "descriptive_only_no_promotion",
        "is_directional_timing_signal": False,
        "distinct_from_c1_c16": ("studies the C1-C16 corpus rather than proposing a "
                                 "new single mechanism; never traded"),
    },
)

RECOMMENDED_DIRECTION_KEY = (
    "risk_adjusted_portfolio_construction_vol_targeted_allocation")

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "creates_candidate", "creates_candidate_id",
    "runs_detector", "runs_labels", "runs_replay", "computes_pnl",
    "optimizes_parameters", "relabels", "fetches_data", "reads_real_data",
    "mutates_data", "stages_data", "auto_commits", "auto_pushes",
    "modifies_scheduler", "sends_notifications", "calls_api", "uses_network",
    "uses_credentials", "connects_broker", "connects_exchange", "uses_real_money",
    "places_orders", "contains_order_logic", "paper_trading", "live_trading",
    "deploys_capital", "promotes_gate", "unlocks_downstream_gate", "skips_any_gate",
    "advances_without_human_approval", "authorizes_autonomous_trading",
    "claims_profitability", "claims_edge", "crosses_into_forbidden_gate",
)


def _recommended() -> dict[str, Any]:
    for d in NEXT_RESEARCH_DIRECTIONS:
        if d["key"] == RECOMMENDED_DIRECTION_KEY:
            return dict(d)
    return {}


def get_next_strategy_research_memo_label() -> str:
    return (
        "Automation Readiness next-strategy research memo v1 (READ-ONLY, RESEARCH "
        "ONLY). Distils the C1-C16 (21) rejected-family lessons into traits to "
        "avoid/prefer and ranked next research directions, recommending one -- "
        "WITHOUT creating a candidate. Real-data-QA/replay BLOCKED, paper/micro-"
        "live/live LOCKED. Turning a direction into a candidate needs a separate "
        "human decision. Executes nothing; not a profitability claim.")


def build_next_strategy_research_memo() -> dict[str, Any]:
    """Assemble the frozen next-strategy research memo. Pure; composes the rejected
    ledger lessons + prep charter + lane status (read-only). Executes nothing;
    creates no candidate."""
    lane = _lane.get_lane_status()
    prep = _arp.build_automation_readiness_research_prep()
    directions = [dict(d) for d in NEXT_RESEARCH_DIRECTIONS]
    # anti-loop: no proposed direction may BE a rejected family.
    none_is_rejected = all(d["key"] not in REJECTED_FAMILIES_C1_TO_C16
                           for d in directions)

    record: dict[str, Any] = {
        "version": MEMO_VERSION, "mode": MEMO_MODE, "lane": MEMO_LANE,
        "is_research_memo_only": True,
        "label": get_next_strategy_research_memo_label(),
        "is_active_candidate": False,
        "creates_candidate_id": False,
        "candidate_id": None,
        # source truth
        "rejected_ledger_count": REJECTED_LEDGER_COUNT,
        "rejected_families_c1_to_c16": list(REJECTED_FAMILIES_C1_TO_C16),
        "uses_c1_to_c16_ledger": REJECTED_LEDGER_COUNT == 21,
        "c16_lifecycle_complete": lane.get("c16_lifecycle_complete"),
        "prep_charter_next_action": prep.get("next_required_action"),
        # 1-9 memo body
        "what_failed": dict(WHAT_FAILED),
        "common_failure_patterns": list(COMMON_FAILURE_PATTERNS),
        "excluded_strategy_types": list(EXCLUDED_STRATEGY_TYPES),
        "traits_to_avoid": list(TRAITS_TO_AVOID),
        "traits_to_prefer": list(TRAITS_TO_PREFER),
        "next_research_directions": directions,
        "recommended_direction": _recommended(),
        "recommended_direction_key": RECOMMENDED_DIRECTION_KEY,
        "why_recommended_is_different": (
            "every C1-C16 candidate was a directional / mean-reversion / pairs "
            "TIMING signal judged on raw net return, and most either lost to "
            "buy-and-hold's raw crypto-beta return (C10/C14/C15), were too rare "
            "(C13/C16), or were eroded by cost (C12/C16). The recommended "
            "direction is a PORTFOLIO-CONSTRUCTION / RISK-MANAGEMENT edge "
            "(allocation, not entry timing) judged on a RISK-ADJUSTED basis "
            "(Sharpe / Calmar / max-drawdown) vs buy-and-hold -- a different "
            "mechanism AND a different success axis, continuous (ample sample) and "
            "low-turnover (cost-tolerant). The same gates still apply: it must "
            "still beat its baselines and survive forward-OOS."),
        "directions_are_distinct_from_rejected_ledger": none_is_rejected,
        # human gate -- nothing becomes a candidate without this
        "requires_human_approval_before_candidate": True,
        "human_approval_before_candidate": HUMAN_APPROVAL_BEFORE_CANDIDATE,
        "next_required_action": NEXT_REQUIRED_ACTION,
        # posture / locks (from the lane)
        "overnight_automation_research_only": lane.get(
            "overnight_automation_research_only"),
        "real_data_qa_state": lane.get("real_data_qa_state"),
        "replay_state": lane.get("replay_state"),
        "paper_trading_state": lane.get("paper_trading_state"),
        "live_trading_state": lane.get("live_trading_state"),
        "human_review_required": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_execute": True, "no_write": True, "no_create_candidate": True,
        "no_candidate_id": True, "no_detector": True, "no_labels": True,
        "no_replay": True, "no_pnl": True, "no_optimization": True,
        "no_relabel": True, "no_data_fetch": True, "no_real_data_access": True,
        "no_stage": True, "no_commit": True, "no_push": True, "no_auto_commit": True,
        "no_auto_push": True, "no_broker": True, "no_credentials": True,
        "no_order_logic": True, "no_paper_trading": True, "no_live_trading": True,
        "no_autonomous_trading": True, "no_gate_skip": True,
        "no_reuse_of_rejected_family": True, "no_downstream_gate_unlock": True,
        "no_profitability_claim": True, "no_crossing_into_forbidden_gate": True,
    }
    return record


def summarize_for_morning_report() -> dict[str, Any]:
    """Pure morning-report-ready memo block. Read-only; executes nothing."""
    r = build_next_strategy_research_memo()
    return {
        "section": "next_strategy_research_memo",
        "rejected_ledger_count": r["rejected_ledger_count"],
        "recommended_direction": r["recommended_direction"].get("name"),
        "recommended_direction_key": r["recommended_direction_key"],
        "ranked_directions": [d["name"] for d in r["next_research_directions"]],
        "requires_human_approval_before_candidate":
            r["requires_human_approval_before_candidate"],
        "human_approval_before_candidate": r["human_approval_before_candidate"],
        "next_required_action": r["next_required_action"],
        "creates_candidate_id": r["creates_candidate_id"],
        "executes_nothing": True,
    }


def validate_next_strategy_research_memo(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the memo is research-only, memo-only,
    uses the C1-C16 (21) ledger, creates NO candidate / no candidate id, proposes
    only directions distinct from the rejected ledger, requires human approval
    before any candidate, keeps the automation-readiness directive + downstream
    locks, and pins every capability flag False."""
    failures: list = []
    if record.get("mode") != MEMO_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_research_memo_only") is not True:
        failures.append("not_research_memo_only")

    # uses C1-C16 / 21 ledger
    if record.get("rejected_ledger_count") != 21:
        failures.append("ledger_not_21")
    if record.get("uses_c1_to_c16_ledger") is not True:
        failures.append("not_using_c1_to_c16_ledger")
    led = record.get("rejected_families_c1_to_c16") or []
    if "cointegration_pairs_market_neutral" not in led:
        failures.append("ledger_missing_c16")

    # creates NO candidate / no candidate id
    if record.get("is_active_candidate") is not False:
        failures.append("must_not_be_active_candidate")
    if record.get("creates_candidate_id") is not False:
        failures.append("must_not_create_candidate_id")
    if record.get("candidate_id") is not None:
        failures.append("candidate_id_must_be_none")

    # proposed directions are NOT rejected families (no excluded family included)
    if record.get("directions_are_distinct_from_rejected_ledger") is not True:
        failures.append("a_direction_is_a_rejected_family")
    for d in record.get("next_research_directions") or []:
        if d.get("key") in REJECTED_FAMILIES_C1_TO_C16:
            failures.append("direction_in_rejected_ledger_%s" % d.get("key"))
    if len(record.get("next_research_directions") or []) < 3:
        failures.append("need_3_to_5_directions")
    if not (record.get("recommended_direction") or {}).get("key"):
        failures.append("no_recommended_direction")

    # human approval required before any candidate
    if record.get("requires_human_approval_before_candidate") is not True:
        failures.append("human_approval_not_required")
    if not str(record.get("human_approval_before_candidate") or "").strip():
        failures.append("human_approval_token_missing")

    # automation-readiness directive unchanged
    if record.get("next_required_action") != NEXT_REQUIRED_ACTION:
        failures.append("next_action_not_automation_readiness")

    # downstream locks
    if record.get("overnight_automation_research_only") is not True:
        failures.append("overnight_not_research_only")
    if record.get("real_data_qa_state") != _lane.STATE_BLOCKED:
        failures.append("real_data_qa_not_blocked")
    if record.get("replay_state") != _lane.STATE_BLOCKED:
        failures.append("replay_not_blocked")
    if record.get("paper_trading_state") != _lane.STATE_LOCKED:
        failures.append("paper_not_locked")
    if record.get("live_trading_state") != _lane.STATE_LOCKED:
        failures.append("live_not_locked")

    locks = record.get("scope_locks") or {}
    for key in ("no_execute", "no_create_candidate", "no_candidate_id",
                "no_detector", "no_labels", "no_replay", "no_pnl",
                "no_optimization", "no_data_fetch", "no_commit", "no_push",
                "no_broker", "no_order_logic", "no_paper_trading",
                "no_live_trading", "no_autonomous_trading",
                "no_reuse_of_rejected_family"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
