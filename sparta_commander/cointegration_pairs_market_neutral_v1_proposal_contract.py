"""Candidate #16 -- cointegration_pairs_market_neutral_v1 -- FAMILY PROPOSAL
(PURE, RESEARCH ONLY).

The next research-only strategy family selected after C15, using the existing
SPARTA automation stack: the Strategy Family Tournament v1 ranking (durability-
weighted), the Research Expansion Plan rejected ledger (C1-C15 = 20), and the
anti-loop rules. trend_following (tournament #1) was built as C15 and REJECTED, so
the next-best UNATTEMPTED, NON-rejected family is statistical_arbitrage_pairs
(tournament #2, score 0.675) -- cointegration-based, market-neutral pairs.

This is a FAMILY PROPOSAL only: it DECLARES the family (core idea / symbols+
timeframes / expected regime / entry-exit-risk sketch / why it differs from the
rejected C1-C15 families / expected failure mode) and confirms the candidate is
NOT in the rejected ledger. It does NOTHING else: NO detector, NO labels, NO
replay, NO optimization, NO data fetch, NO writes, NO stage/commit/push, and NO
paper/live/broker/order surface. Every capability flag is pinned False with a full
scope_locks set. Advancing to the candidate-spec gate still needs an explicit
human decision.

Material difference from C1-C15 (the whole point): this is MARKET-NEUTRAL (a long/
short cointegrated spread), NOT a directional bet. It is distinct from C11
(cross_asset_dispersion_reversion, which traded cross-sectional dispersion, not a
two-leg cointegrated spread) and from C15 (slow_vol_targeted_time_series_momentum,
a directional long-bull-carry trend follower). It deliberately targets the carry
trap that rejected C14/C15: a dollar-neutral spread has no buy-and-hold beta to
lose to.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.research_expansion_plan_v1_contract as _rep
import sparta_commander.strategy_family_tournament_v1_proposal_contract as _sft

C16_SCHEMA_VERSION = 1
C16_MODE = "RESEARCH_ONLY"
C16_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = "C16"
CANDIDATE_FAMILY = "cointegration_pairs_market_neutral"
CANDIDATE_NAME = "cointegration_pairs_market_neutral_v1"

# Source: the tournament family this proposal instantiates.
TOURNAMENT_FAMILY_KEY = "statistical_arbitrage_pairs"
# Tournament families already ATTEMPTED (built into a candidate) before C16.
ALREADY_ATTEMPTED_TOURNAMENT_FAMILIES = ("trend_following",)  # -> C15 (rejected)

REJECTED_FAMILIES_C1_TO_C15 = tuple(_rep.REJECTED_FAMILIES_C1_TO_C15)
C14_LESSON = _rep.C14_LESSON

# --- the preserved, frozen gate sequence (each stage human-gated) -----------
GATE_SEQUENCE = (
    "family_proposal", "candidate_spec", "detector_spec_dry_run",
    "real_candle_labels_review", "fee_honest_replay_review",
    "rejection_or_promote_decision",
)

# --- proposal-level family declaration --------------------------------------
SYMBOLS = ("ETH/BTC", "SOL/ETH", "SOL/BTC")     # ratio spreads (D1)
LEG_SYMBOLS = ("BTCUSD", "ETHUSD", "SOLUSD")
TIMEFRAME = "D1"
HOLDING_PERIOD = "days_to_weeks"
EXPECTED_REGIME = "range/chop friendly; risk in structural regime breaks / de-peg"

CORE_IDEA = (
    "Trade the mean-reverting spread of a cointegrated crypto pair (e.g. ETH-BTC, "
    "SOL-ETH): when the cointegration-residual z-score is extreme, go LONG the "
    "cheap leg and SHORT the rich leg, dollar/beta-neutral, and exit as the spread "
    "reverts. Market-neutral -- the edge is the spread's reversion, not direction.")
ENTRY_LOGIC_SKETCH = (
    "enter when |rolling cointegration-residual z-score| >= a band (e.g. 2.0) AND "
    "the rolling cointegration test is still valid over the durability window; "
    "long the cheap leg / short the rich leg, dollar-neutral")
EXIT_LOGIC_SKETCH = (
    "spread z reverts toward 0 (take), a z-band stop on further widening, or a "
    "cointegration-break invalidation exit if the rolling p-value degrades")
RISK_LOGIC_SKETCH = (
    "dollar/beta-neutral legs, spread vol-stop, hard exit on cointegration break, "
    "per-pair risk cap; no directional market exposure carried")

MATERIAL_DIFFERENCE_FROM_C1_C15 = (
    "MARKET-NEUTRAL long/short cointegrated spread, NOT a directional bet",
    "distinct from C11 cross_asset_dispersion_reversion (cross-sectional "
    "dispersion, not a two-leg cointegrated spread)",
    "distinct from C15 slow_vol_targeted_time_series_momentum (directional "
    "long-bull-carry trend following)",
    "no buy-and-hold beta to lose to -- directly targets the carry trap that "
    "rejected C14 and C15",
    "rolling cointegration validation is a new mechanism never used in C1-C15",
)
EXPECTED_FAILURE_MODE = (
    "cointegration breaks in a structural regime shift (one leg de-pegs / "
    "decouples) so the spread trends instead of reverting; a thin spread edge is "
    "eroded by paying fees on TWO legs; too few valid-cointegration windows -> "
    "small sample (the C13 structural-rejection risk)")

WHY_SELECTED = (
    "tournament #2 (score 0.675) after trend_following (#1) was built as C15 and "
    "rejected; it carries the HIGHEST portfolio-fit (0.85: market-neutral, low-"
    "correlation, capital-efficient via offsetting legs), is materially NEW "
    "(cointegration pairs never tried), and -- being dollar-neutral -- structurally "
    "avoids the long-bull-carry trap that rejected C14 and C15")

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "builds_candidate_files", "runs_detector",
    "runs_labels", "runs_replay", "runs_backtest", "optimizes_parameters",
    "runs_robustness", "runs_portfolio_compute", "fetches_data", "reads_real_data",
    "mutates_data", "stages_data", "auto_commits", "auto_pushes",
    "modifies_scheduler", "sends_notifications", "calls_api", "uses_network",
    "uses_credentials", "connects_broker", "connects_exchange", "uses_real_money",
    "places_orders", "contains_order_logic", "paper_trading", "live_trading",
    "deploys_capital", "promotes_gate", "unlocks_downstream_gate", "skips_any_gate",
    "reproposes_rejected_family", "advances_without_human_approval",
    "claims_profitability", "claims_edge", "crosses_into_forbidden_gate",
)


def select_next_family() -> dict[str, Any]:
    """Pure: use the tournament ranking + the already-attempted set + the rejected
    ledger to select the next family. Returns the chosen tournament family key and
    its rank/score. Selects nothing executable."""
    ranked = _sft.rank_families()
    attempted = set(ALREADY_ATTEMPTED_TOURNAMENT_FAMILIES)
    chosen = None
    rank = None
    for i, r in enumerate(ranked):
        if r["key"] in attempted:
            continue
        chosen = r
        rank = i + 1
        break
    return {
        "selected_tournament_family": chosen["key"] if chosen else None,
        "tournament_rank": rank,
        "tournament_score": chosen["priority_score"] if chosen else None,
        "already_attempted": sorted(attempted),
        "candidate_family": CANDIDATE_FAMILY,
        "excluded_from_rejected_ledger":
            CANDIDATE_FAMILY not in REJECTED_FAMILIES_C1_TO_C15,
    }


def get_candidate_16_proposal_label() -> str:
    return (
        "Candidate #16 cointegration_pairs_market_neutral_v1 family proposal "
        "(READ-ONLY, RESEARCH ONLY, PURE PROPOSAL). Market-neutral cointegration "
        "pairs on crypto-D1 ratio spreads -- the tournament #2 family after C15, "
        "selected because it is dollar-neutral (no buy-and-hold beta to lose to, "
        "directly targeting the carry trap that rejected C14/C15) and materially "
        "new. PROPOSAL ONLY: advancing to the candidate-spec gate needs an explicit "
        "human decision. NO detector, NO labels, NO replay, NO optimization, NO "
        "paper/live. NOT a profitability claim.")


def get_candidate_16_proposal_next_action() -> str:
    return "HUMAN_DECISION_C16_ADVANCE_TO_CANDIDATE_SPEC_OR_REJECT"


def build_c16_family_proposal(repo_root: Any = ".",
                              tracked_paths: list | None = None) -> dict[str, Any]:
    """Assemble the frozen Candidate #16 family-proposal record. Pure; no I/O;
    proposal only. Chain-references the tournament ranking + the rejected ledger."""
    selection = select_next_family()
    tournament = _sft.build_strategy_family_tournament_proposal(repo_root, tracked_paths)
    tournament_valid = _sft.validate_strategy_family_tournament_proposal(
        tournament)["valid"]

    blockers: list = []
    if not tournament_valid:
        blockers.append("tournament_proposal_invalid")
    if selection["selected_tournament_family"] != TOURNAMENT_FAMILY_KEY:
        blockers.append("selected_family_not_statistical_arbitrage_pairs")
    if CANDIDATE_FAMILY in REJECTED_FAMILIES_C1_TO_C15:
        blockers.append("candidate_family_in_rejected_ledger")
    if "slow_vol_targeted_time_series_momentum" == CANDIDATE_FAMILY:
        blockers.append("must_not_reuse_c15")

    record: dict[str, Any] = {
        "schema_version": C16_SCHEMA_VERSION, "mode": C16_MODE, "lane": C16_LANE,
        "label": get_candidate_16_proposal_label(),
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "candidate_name": CANDIDATE_NAME,
        "is_pure_proposal_only": True,
        "blockers": blockers,
        "verdict": ("C16_PROPOSAL_FROZEN_FOR_HUMAN_REVIEW" if not blockers
                    else "C16_PROPOSAL_BLOCKED"),
        # selection provenance (the automation stack)
        "selected_via": ("strategy_family_tournament_v1 ranking + research_"
                         "expansion_plan rejected ledger (C1-C15) anti-loop"),
        "selection": selection,
        "tournament_family_key": TOURNAMENT_FAMILY_KEY,
        "tournament_proposal_valid": tournament_valid,
        "why_selected": WHY_SELECTED,
        # the family declaration
        "gate_sequence": list(GATE_SEQUENCE),
        "gate_sequence_preserved_unchanged": True,
        "core_idea": CORE_IDEA,
        "symbols": list(SYMBOLS), "leg_symbols": list(LEG_SYMBOLS),
        "timeframe": TIMEFRAME, "holding_period": HOLDING_PERIOD,
        "expected_regime": EXPECTED_REGIME,
        "entry_logic_sketch": ENTRY_LOGIC_SKETCH,
        "exit_logic_sketch": EXIT_LOGIC_SKETCH,
        "risk_logic_sketch": RISK_LOGIC_SKETCH,
        "material_difference_from_c1_c15": list(MATERIAL_DIFFERENCE_FROM_C1_C15),
        "expected_failure_mode": EXPECTED_FAILURE_MODE,
        "is_market_neutral": True,
        "is_directional": False,
        # anti-loop / ledger
        "rejected_families_c1_to_c15": list(REJECTED_FAMILIES_C1_TO_C15),
        "rejected_families_count": len(REJECTED_FAMILIES_C1_TO_C15),
        "candidate_not_in_rejected_ledger":
            CANDIDATE_FAMILY not in REJECTED_FAMILIES_C1_TO_C15,
        "does_not_reuse_c15":
            CANDIDATE_FAMILY != "slow_vol_targeted_time_series_momentum",
        "c14_lesson": C14_LESSON,
        "human_review_required": True,
        "current_loop_stage": "family_proposal",
        "next_required_action": get_candidate_16_proposal_next_action(),
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
        "no_backtest": True, "no_optimization": True, "no_robustness": True,
        "no_portfolio_compute": True, "no_data_fetch": True,
        "no_real_data_access": True, "no_stage": True, "no_commit": True,
        "no_push": True, "no_auto_commit": True, "no_auto_push": True,
        "no_scheduler_change": True, "no_broker": True, "no_credentials": True,
        "no_order_logic": True, "no_paper_trading": True, "no_live_trading": True,
        "no_gate_skip": True, "no_rejected_family_repropose": True,
        "no_reuse_of_c15": True, "no_downstream_gate_unlock": True,
        "no_profitability_claim": True, "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_c16_family_proposal(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the proposal is research-only, pure-
    proposal-only, selected statistical_arbitrage_pairs via the tournament, is
    materially different + market-neutral, is NOT in the C1-C15 rejected ledger and
    does not reuse C15, preserves the gate sequence, keeps downstream gates locked,
    and pins every capability flag False."""
    failures: list = []
    if record.get("mode") != C16_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_pure_proposal_only") is not True:
        failures.append("not_pure_proposal_only")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("verdict") != "C16_PROPOSAL_FROZEN_FOR_HUMAN_REVIEW":
        failures.append("verdict_not_frozen")

    # selection provenance
    if record.get("tournament_family_key") != TOURNAMENT_FAMILY_KEY:
        failures.append("tournament_family_not_stat_arb")
    sel = record.get("selection") or {}
    if sel.get("selected_tournament_family") != TOURNAMENT_FAMILY_KEY:
        failures.append("selection_not_stat_arb")
    if record.get("tournament_proposal_valid") is not True:
        failures.append("tournament_not_valid")

    # anti-loop: not in ledger, not reusing C15, ledger is 20
    if record.get("candidate_not_in_rejected_ledger") is not True:
        failures.append("candidate_in_rejected_ledger")
    if record.get("does_not_reuse_c15") is not True:
        failures.append("reuses_c15")
    led = record.get("rejected_families_c1_to_c15") or []
    if "slow_vol_targeted_time_series_momentum" not in led:
        failures.append("ledger_missing_c15")
    if record.get("rejected_families_count") != 20:
        failures.append("ledger_not_20")
    if record.get("candidate_family") in led:
        failures.append("candidate_family_listed_as_rejected")

    # market-neutral + materially different (the carry-trap avoidance)
    if record.get("is_market_neutral") is not True:
        failures.append("not_market_neutral")
    if record.get("is_directional") is not False:
        failures.append("must_not_be_directional")
    if len(record.get("material_difference_from_c1_c15") or []) < 5:
        failures.append("insufficient_material_difference")

    # full proposal-level declaration present
    for field in ("core_idea", "symbols", "timeframe", "entry_logic_sketch",
                  "exit_logic_sketch", "risk_logic_sketch",
                  "expected_failure_mode", "why_selected"):
        if not record.get(field):
            failures.append("proposal_missing_%s" % field)

    # gate sequence preserved
    if list(record.get("gate_sequence") or []) != list(GATE_SEQUENCE):
        failures.append("gate_sequence_tampered")

    # downstream gates locked
    for gate in ("spec_gate_locked", "detector_gate_locked", "labels_gate_locked",
                 "replay_gate_locked", "paper_trading_gate_locked",
                 "live_gate_locked"):
        if record.get(gate) is not True:
            failures.append("downstream_gate_unlocked_%s" % gate)

    locks = record.get("scope_locks") or {}
    for key in ("no_build", "no_detector", "no_labels", "no_replay",
                "no_optimization", "no_commit", "no_push", "no_broker",
                "no_order_logic", "no_paper_trading", "no_live_trading",
                "no_gate_skip", "no_rejected_family_repropose", "no_reuse_of_c15"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
