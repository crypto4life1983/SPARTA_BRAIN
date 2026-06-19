"""Candidate #20 -- mechanically_neutral_spot_perp_basis_funding_carry_v1
-- FAMILY PROPOSAL (PURE, RESEARCH ONLY).

The formal candidate-family proposal for the human-approved C20 research direction
(HUMAN_APPROVED_C20_RESEARCH_DIRECTION__OPEN_CANDIDATE_FAMILY_PROPOSAL), built on the
frozen PUBLIC BTCUSDT/ETHUSDT/SOLUSDT spot + USDT-perp + funding dataset. Chain-gated
on the committed data-readiness review (the dataset must be FROZEN_AND_READY).

THESIS: hold a MECHANICALLY market-neutral, SAME-ASSET position -- long spot and short
the USDT-perp of the SAME underlying in equal notional -- so price exposure cancels by
CONSTRUCTION (not by an estimated cross-asset hedge), and harvest the BASIS / FUNDING
CARRY (the perp premium/discount and the funding payments). The return source is carry,
not directional OHLCV timing; the neutrality is mechanical, not estimated.

It is a PROPOSAL only: it DECLARES the family thesis, why it differs from the rejected
C1-C19 families (especially the buy-and-hold-beta trap of C17/C18 and the
ESTIMATED-neutrality failure of C16/C19), the universe and the gate-zero
mechanical-neutrality requirement, the six candidate SUB-FAMILIES to compare, the
evaluation metrics, the cost assumptions (incl. perp-specific frictions reserved for
replay), the data requirements (the frozen dataset; nothing fetched), the out-of-sample
requirement, the safety boundaries, and the next human gate. It builds NO detector, NO
labels, NO replay; runs NO PnL/optimization/tuning/rescue/data fetch; touches NO
paper/live/broker/order surface; and does NOT start C21. Every capability flag is pinned
False with a full scope_locks set. Advancing to the candidate-spec gate needs an
explicit human decision.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.crypto_basis_funding_data_readiness_review_v1_contract as _dr
import sparta_commander.research_expansion_plan_v1_contract as _rep

C20_SCHEMA_VERSION = 1
C20_MODE = "RESEARCH_ONLY"
C20_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = "C20"
CANDIDATE_FAMILY = "mechanically_neutral_spot_perp_basis_funding_carry"
CANDIDATE_NAME = "mechanically_neutral_spot_perp_basis_funding_carry_v1"

REJECTED_FAMILIES_C1_TO_C19 = tuple(_rep.REJECTED_FAMILIES_C1_TO_C19)   # 24
EXPECTED_DATA_VERDICT = "FROZEN_AND_READY_FOR_RESEARCH_ONLY_BASIS_FUNDING_STUDY"

# --- the preserved, frozen gate sequence (each stage human-gated) -----------
GATE_SEQUENCE = (
    "family_proposal", "candidate_spec", "detector_spec_dry_run",
    "real_candle_labels_review", "fee_honest_replay_review",
    "rejection_or_promote_decision",
)

# --- universe + data (frozen public spot/perp/funding; nothing fetched) -----
UNIVERSE = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
TIMEFRAME = "D1"
DATA_SOURCE = ("frozen PUBLIC Binance spot + USDT-perp + funding (the committed "
               "data-readiness review dataset) -- already present, no fetch")

# --- 1. family thesis -------------------------------------------------------
FAMILY_THESIS = (
    "Hold a MECHANICALLY market-neutral SAME-ASSET position: long spot and short the "
    "USDT-perpetual of the SAME underlying in equal notional, so the directional price "
    "exposure cancels BY CONSTRUCTION (the residual is the spot-perp BASIS, not an "
    "estimated cross-asset hedge). Harvest the BASIS / FUNDING CARRY -- the perp "
    "premium/discount that converges, plus the funding payments the short-perp leg "
    "receives when funding is positive. The thesis is that a same-asset basis/funding "
    "carry has a return source ORTHOGONAL to spot direction whose neutrality cannot "
    "'fail out of sample' -- to be PROVEN net of all-in and perp-specific costs, not "
    "assumed.")

# --- 2. why different from C1-C19 -------------------------------------------
WHY_DIFFERENT_FROM_C1_C19 = (
    "NOT long-only buy-and-hold beta: the position is dollar- AND price-neutral by "
    "construction, so it does not have to beat buy-and-hold risk-adjusted (the rock "
    "C17 and C18 died on)",
    "NOT cross-asset ESTIMATED neutrality: C16 (cointegration level-OLS hedge) and C19 "
    "(return-beta hedge) both failed because their estimated cross-asset neutrality did "
    "not persist OUT OF SAMPLE; here neutrality is SAME-ASSET and MECHANICAL (long "
    "spot / short perp of the identical underlying) -- it cannot drift OOS",
    "RETURN SOURCE IS CARRY, not directional OHLCV timing: the edge is the basis/"
    "funding the short-perp leg earns, not a price-pattern signal like C1-C13/C18",
    "USES A NEW INFORMATION SOURCE: perp basis + funding (committed frozen public data) "
    "rather than the spot-only OHLCV every prior family relied on",
)

# --- 3. gate-zero: mechanical (not estimated) neutrality --------------------
MECHANICAL_NEUTRALITY_GATE_ZERO = {
    "is_gate_zero": True,
    "requirement": ("the position is long 1 unit spot and short 1 unit USDT-perp of "
                    "the SAME asset in equal notional, so net price beta is ~0 BY "
                    "CONSTRUCTION (not by estimation); the only residual exposure is "
                    "the spot-perp basis itself"),
    "neutrality_is_mechanical_not_estimated": True,
    "fixes_c16_c19_estimated_neutrality_failure": True,
    "no_cross_asset_hedge_estimation": True,
}

# --- 4. the six candidate SUB-FAMILIES to compare ---------------------------
SUB_FAMILIES = (
    {"key": "funding_carry_directional",
     "desc": "hold the neutral basis position to harvest persistently positive "
             "funding (short-perp receives funding); sign by funding sign"},
    {"key": "basis_zscore_mean_reversion",
     "desc": "enter the basis position when the spot-perp basis z-score is extreme and "
             "exit on convergence toward the mean"},
    {"key": "funding_extreme_fade",
     "desc": "fade extreme funding rates expecting normalization (size the neutral "
             "position by funding-rate extremity)"},
    {"key": "basis_term_structure_regime",
     "desc": "gate the carry by the basis/funding regime -- stand aside in inverted / "
             "negative-carry regimes"},
    {"key": "cross_symbol_basis_relative_value",
     "desc": "compare-only: relative basis carry across BTC/ETH/SOL (each leg still "
             "same-asset neutral); secondary, to check breadth"},
    {"key": "funding_carry_with_basis_divergence_stop",
     "desc": "harvest carry with a basis-divergence invalidation (close if the basis "
             "blows out beyond a structural band)"},
)

# --- 5. evaluation metrics --------------------------------------------------
EVALUATION_METRICS = {
    "primary_market_neutral": ("net_price_beta_mechanical", "net_positive_vs_random",
                               "net_positive_vs_null"),
    "carry_diagnostics": ("annualized_carry", "funding_collected", "basis_convergence",
                          "negative_carry_regime_share"),
    "risk_adjusted": ("sharpe_ratio", "calmar_ratio", "max_drawdown"),
    "baseline": ("a random/zero-edge null on the SAME neutral basis position, net of "
                 "ALL-IN and perp-specific cost -- NOT buy-and-hold (there is no net "
                 "market exposure)"),
    "win_condition": ("a NET-POSITIVE carry edge vs random / null on a RISK-ADJUSTED "
                      "basis AND surviving forward-OOS, net of funding/borrow/"
                      "liquidation-aware costs -- not raw carry before costs"),
    "neutrality_is_mechanical_precondition": True,
    "judged_against_buy_and_hold": False,
}

# --- 6. cost assumptions ----------------------------------------------------
FEE_ROUND_TRIP_BPS = 27.0
SLIPPAGE_ROUND_TRIP_BPS = 10.0
ALL_IN_ROUND_TRIP_BPS = FEE_ROUND_TRIP_BPS + SLIPPAGE_ROUND_TRIP_BPS   # 37.0
COST_ASSUMPTIONS = {
    "all_in_round_trip_bps": ALL_IN_ROUND_TRIP_BPS,
    "two_legs_spot_and_perp_so_cost_counts_double": True,
    "perp_specific_frictions_reserved_for_replay": (
        "funding paid/received, perp borrow, and liquidation-aware margin must be "
        "modelled at the replay gate -- carry before these costs is NOT the edge"),
    "cost_applied_only_at_replay_gate": True,
    "applied_here": False,
}

# --- 7. data requirements (frozen; nothing fetched) -------------------------
DATA_REQUIREMENTS = {
    "spot_perp_funding_d1": {"required": True, "available_locally": True,
                             "note": "the committed data-readiness review dataset "
                                     "(BTC/ETH/SOL spot+perp+funding) -- frozen, "
                                     "SHA-pinned, gitignored"},
    "no_data_fetched_here": True,
    "no_new_data_fetch_required": True,
    "no_xauusd_or_new_instrument_class": True,
}

# --- 8. out-of-sample validation requirement --------------------------------
OOS_VALIDATION = {
    "forward_oos_required": True,
    "forward_oos_window": "2026_unseen_continuation",
    "forward_oos_must_hold_carry_edge_net_of_cost": True,
    "neutrality_is_mechanical_so_cannot_fail_oos": True,
    "no_parameter_optimization": True,
    "no_in_sample_only_fit": True,
}

# --- 9. safety boundaries ---------------------------------------------------
SAFETY_BOUNDARIES = (
    "research-only: no paper trading, no live trading, no broker/exchange, no orders, "
    "no credentials, no data fetch in this proposal",
    "frozen public spot/perp/funding ONLY -- no new fetch, no XAUUSD / new instrument "
    "class",
    "mechanical same-asset neutrality is GATE ZERO: the construction is long spot / "
    "short perp of the IDENTICAL asset; no estimated cross-asset hedge",
    "carry is judged NET of all-in AND perp-specific costs (funding/borrow/liquidation) "
    "at the replay gate -- raw carry is never the edge",
    "no detector / labels / replay / optimization / rescue / parameter tuning in or "
    "after this proposal until each downstream gate is separately human-approved; "
    "promotion requires a net-positive carry edge vs random/null risk-adjusted and "
    "surviving forward-OOS; this proposal does NOT start C21",
)

NEXT_HUMAN_GATE_AFTER_PROPOSAL = (
    "HUMAN_DECISION_C20_ADVANCE_TO_CANDIDATE_SPEC_OR_REJECT")

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "builds_candidate_files", "runs_detector",
    "runs_labels", "runs_replay", "runs_backtest", "computes_pnl",
    "optimizes_parameters", "reparameterizes", "tunes_parameters", "runs_rescue",
    "runs_robustness", "fetches_data", "reads_real_data", "mutates_data",
    "stages_data", "auto_commits", "auto_pushes", "modifies_scheduler",
    "sends_notifications", "calls_api", "uses_network", "uses_credentials",
    "connects_broker", "connects_exchange", "uses_real_money", "places_orders",
    "contains_order_logic", "carries_net_market_beta",
    "uses_estimated_cross_asset_hedge", "adds_new_instrument_class", "uses_xauusd",
    "paper_trading", "live_trading", "deploys_capital", "promotes_gate",
    "unlocks_downstream_gate", "skips_any_gate", "reproposes_rejected_family",
    "starts_c21", "advances_without_human_approval", "claims_profitability",
    "claims_edge", "crosses_into_forbidden_gate",
)


def get_candidate_20_proposal_label() -> str:
    return (
        "Candidate #20 mechanically_neutral_spot_perp_basis_funding_carry_v1 family "
        "proposal (READ-ONLY, RESEARCH ONLY, PURE PROPOSAL). A SAME-ASSET long-spot / "
        "short-perp basis + funding carry on frozen public BTC/ETH/SOL data -- "
        "MECHANICALLY neutral (not estimated, so it cannot fail OOS like C16/C19) and a "
        "CARRY return source (not buy-and-hold beta like C17/C18, not OHLCV timing). "
        "Compares six sub-families. PROPOSAL ONLY: advancing to the candidate-spec gate "
        "needs an explicit human decision. NO detector, NO labels, NO replay, NO "
        "optimization, NO data fetch, NO XAUUSD, NO paper/live, does NOT start C21. NOT "
        "a profitability claim.")


def get_candidate_20_proposal_next_action() -> str:
    return NEXT_HUMAN_GATE_AFTER_PROPOSAL


def _deepish(d: dict) -> dict:
    out: dict = {}
    for k, v in d.items():
        out[k] = dict(v) if isinstance(v, dict) else v
    return out


def build_c20_proposal(repo_root: Any = ".",
                       tracked_paths: list | None = None) -> dict[str, Any]:
    """Assemble the frozen Candidate #20 family-proposal record. Pure; no I/O;
    proposal only. Chain-gated on the committed data-readiness review (the frozen
    spot/perp/funding dataset must be FROZEN_AND_READY)."""
    dr = _dr.build_data_readiness_review()
    dr_valid = _dr.validate_data_readiness_review(dr)["valid"]
    dr_verdict = dr.get("readiness_verdict")

    blockers: list = []
    if not dr_valid:
        blockers.append("data_readiness_review_invalid")
    if dr_verdict != EXPECTED_DATA_VERDICT:
        blockers.append("dataset_not_frozen_and_ready")
    if dr.get("assigns_c20") is not False:
        blockers.append("data_review_should_not_have_assigned_c20")
    if CANDIDATE_FAMILY in REJECTED_FAMILIES_C1_TO_C19:
        blockers.append("candidate_family_in_rejected_ledger")

    record: dict[str, Any] = {
        "schema_version": C20_SCHEMA_VERSION, "mode": C20_MODE, "lane": C20_LANE,
        "label": get_candidate_20_proposal_label(),
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "candidate_name": CANDIDATE_NAME,
        "is_pure_proposal_only": True,
        "blockers": blockers,
        "verdict": ("C20_PROPOSAL_FROZEN_FOR_HUMAN_REVIEW" if not blockers
                    else "C20_PROPOSAL_BLOCKED"),
        # chain provenance (built on the frozen dataset)
        "data_readiness_verdict": dr_verdict,
        "data_readiness_valid": dr_valid,
        "promoted_from_data_readiness_review":
            "crypto_basis_funding_data_readiness_review_v1",
        "approved_via": "HUMAN_APPROVED_C20_RESEARCH_DIRECTION__OPEN_CANDIDATE_FAMILY_PROPOSAL",
        # the required explanation sections
        "family_thesis": FAMILY_THESIS,                                  # 1
        "why_different_from_c1_c19": list(WHY_DIFFERENT_FROM_C1_C19),     # 2
        "mechanical_neutrality_gate_zero": dict(MECHANICAL_NEUTRALITY_GATE_ZERO),  # 3
        "sub_families": [dict(s) for s in SUB_FAMILIES],                # 4
        "evaluation_metrics": _deepish(EVALUATION_METRICS),            # 5
        "cost_assumptions": dict(COST_ASSUMPTIONS),                    # 6
        "data_requirements": _deepish(DATA_REQUIREMENTS),              # 7
        "oos_validation": dict(OOS_VALIDATION),                        # 8
        "safety_boundaries": list(SAFETY_BOUNDARIES),                  # 9
        # universe + data
        "universe": list(UNIVERSE),
        "timeframe": TIMEFRAME,
        "data_source": DATA_SOURCE,
        "uses_frozen_public_spot_perp_funding_only": True,
        "no_new_data_fetch": True,
        "no_new_instrument_class": True,
        # identity / anti-loop
        "is_market_neutral": True,
        "is_mechanically_neutral_same_asset": True,
        "is_estimated_cross_asset_neutral": False,
        "return_source_is_carry_not_timing": True,
        "carries_buy_and_hold_beta": False,
        "is_directional_timing_signal": False,
        "gate_sequence": list(GATE_SEQUENCE),
        "gate_sequence_preserved_unchanged": True,
        "rejected_families_c1_to_c19": list(REJECTED_FAMILIES_C1_TO_C19),
        "rejected_families_count": len(REJECTED_FAMILIES_C1_TO_C19),
        "candidate_not_in_rejected_ledger":
            CANDIDATE_FAMILY not in REJECTED_FAMILIES_C1_TO_C19,
        "all_in_round_trip_bps": ALL_IN_ROUND_TRIP_BPS,
        "human_review_required": True,
        "current_loop_stage": "family_proposal",
        "next_required_action": NEXT_HUMAN_GATE_AFTER_PROPOSAL,
        "next_human_gate_after_proposal": NEXT_HUMAN_GATE_AFTER_PROPOSAL,
        "does_not_start_c21": True,
        "c21_candidate_id": None,
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
        "no_reparameterization": True, "no_tuning": True, "no_rescue": True,
        "no_robustness": True, "no_data_fetch": True, "no_real_data_access": True,
        "no_new_instrument_class": True, "no_xauusd": True, "no_stage": True,
        "no_commit": True, "no_push": True, "no_auto_commit": True,
        "no_auto_push": True, "no_scheduler_change": True, "no_broker": True,
        "no_credentials": True, "no_order_logic": True, "no_net_market_beta": True,
        "no_estimated_cross_asset_hedge": True, "no_paper_trading": True,
        "no_live_trading": True, "no_gate_skip": True,
        "no_rejected_family_repropose": True, "no_start_c21": True,
        "no_downstream_gate_unlock": True, "no_profitability_claim": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_c20_proposal(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the proposal is research-only, pure-
    proposal-only, chain-gated on the FROZEN_AND_READY data-readiness review, a
    MECHANICALLY-neutral same-asset spot/perp basis-funding-carry family NOT in the
    C1-C19 (24) ledger, with mechanical (not estimated) neutrality as gate zero and a
    carry (not buy-and-hold-beta, not timing) return source, the frozen public
    spot/perp/funding-only universe (no fetch, no new instrument class), the six
    sub-families, the market-neutral + risk-adjusted + forward-OOS evaluation (judged
    vs random/null, NOT buy-and-hold) with 37 bps + perp frictions reserved for replay,
    preserves the gate sequence, keeps downstream gates locked, does not start C21, and
    pins every capability flag False."""
    failures: list = []
    if record.get("mode") != C20_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_pure_proposal_only") is not True:
        failures.append("not_pure_proposal_only")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("verdict") != "C20_PROPOSAL_FROZEN_FOR_HUMAN_REVIEW":
        failures.append("verdict_not_frozen")

    # chain gate on the frozen dataset
    if record.get("data_readiness_valid") is not True:
        failures.append("data_readiness_not_valid")
    if record.get("data_readiness_verdict") != EXPECTED_DATA_VERDICT:
        failures.append("dataset_not_frozen_and_ready")
    if record.get("promoted_from_data_readiness_review") != (
            "crypto_basis_funding_data_readiness_review_v1"):
        failures.append("promoted_from_wrong_source")

    # identity: candidate #20, mechanically neutral same-asset, carry source
    if record.get("candidate_id") != "C20":
        failures.append("candidate_id_not_c20")
    if record.get("candidate_family") != CANDIDATE_FAMILY:
        failures.append("family_mismatch")
    for k in ("is_market_neutral", "is_mechanically_neutral_same_asset",
              "return_source_is_carry_not_timing"):
        if record.get(k) is not True:
            failures.append("identity_flag_off_%s" % k)
    if record.get("is_estimated_cross_asset_neutral") is not False:
        failures.append("must_not_be_estimated_cross_asset_neutral")
    if record.get("carries_buy_and_hold_beta") is not False:
        failures.append("must_not_carry_buy_and_hold_beta")
    if record.get("is_directional_timing_signal") is not False:
        failures.append("must_not_be_directional_timing")
    gz = record.get("mechanical_neutrality_gate_zero") or {}
    if gz.get("is_gate_zero") is not True:
        failures.append("gate_zero_flag_wrong")
    if gz.get("neutrality_is_mechanical_not_estimated") is not True:
        failures.append("neutrality_must_be_mechanical")
    if gz.get("no_cross_asset_hedge_estimation") is not True:
        failures.append("must_not_estimate_cross_asset_hedge")

    # anti-loop + materially different (esp. vs C16/C17/C18/C19)
    if record.get("candidate_not_in_rejected_ledger") is not True:
        failures.append("candidate_in_rejected_ledger")
    if record.get("candidate_family") in REJECTED_FAMILIES_C1_TO_C19:
        failures.append("family_listed_as_rejected")
    if record.get("rejected_families_count") != 24:
        failures.append("ledger_not_24")
    diffs = record.get("why_different_from_c1_c19") or []
    if len(diffs) < 4:
        failures.append("insufficient_difference_explanation")
    joined = " ".join(diffs)
    for must in ("buy-and-hold", "ESTIMATED", "CARRY", "MECHANICAL"):
        if must not in joined:
            failures.append("difference_missing_%s" % must)

    # universe + data: frozen public spot/perp/funding only, no fetch, no new instrument
    if list(record.get("universe") or []) != ["BTCUSDT", "ETHUSDT", "SOLUSDT"]:
        failures.append("universe_not_btc_eth_sol_perp")
    if record.get("uses_frozen_public_spot_perp_funding_only") is not True:
        failures.append("not_frozen_public_only")
    if record.get("no_new_data_fetch") is not True:
        failures.append("must_not_fetch_data")
    if record.get("no_new_instrument_class") is not True:
        failures.append("must_not_add_instrument_class")
    dr = record.get("data_requirements") or {}
    if dr.get("no_data_fetched_here") is not True:
        failures.append("data_fetch_flag_wrong")
    if (dr.get("spot_perp_funding_d1") or {}).get("available_locally") is not True:
        failures.append("data_should_be_local")
    if dr.get("no_xauusd_or_new_instrument_class") is not True:
        failures.append("data_adds_new_instrument_class")

    # the six sub-families, incl. the gate-zero funding-carry directional
    subs = record.get("sub_families") or []
    if len(subs) != 6:
        failures.append("sub_families_not_six")
    keys = {s.get("key") for s in subs}
    for must in ("funding_carry_directional", "basis_zscore_mean_reversion",
                 "funding_extreme_fade", "basis_term_structure_regime",
                 "cross_symbol_basis_relative_value",
                 "funding_carry_with_basis_divergence_stop"):
        if must not in keys:
            failures.append("sub_family_missing_%s" % must)

    # evaluation: carry vs random/null + risk-adjusted, NOT vs buy-and-hold; cost reserved
    em = record.get("evaluation_metrics") or {}
    if "net_price_beta_mechanical" not in (em.get("primary_market_neutral") or ()):
        failures.append("missing_mechanical_neutrality_metric")
    for m in ("sharpe_ratio", "calmar_ratio", "max_drawdown"):
        if m not in (em.get("risk_adjusted") or ()):
            failures.append("metric_missing_%s" % m)
    if "random" not in str(em.get("win_condition", "")).lower():
        failures.append("win_condition_not_vs_random_null")
    if em.get("judged_against_buy_and_hold") is not False:
        failures.append("must_not_be_judged_vs_buy_and_hold")
    ct = record.get("cost_assumptions") or {}
    if ct.get("all_in_round_trip_bps") != 37.0:
        failures.append("cost_model_tampered")
    if ct.get("cost_applied_only_at_replay_gate") is not True:
        failures.append("cost_not_reserved_for_replay")
    if not ct.get("perp_specific_frictions_reserved_for_replay"):
        failures.append("perp_frictions_not_reserved")

    # OOS required, mechanical neutrality, no optimization
    oos = record.get("oos_validation") or {}
    if oos.get("forward_oos_required") is not True:
        failures.append("forward_oos_not_required")
    if oos.get("neutrality_is_mechanical_so_cannot_fail_oos") is not True:
        failures.append("oos_neutrality_claim_missing")
    if oos.get("no_parameter_optimization") is not True:
        failures.append("optimization_not_forbidden")

    # gate sequence + downstream locks + no C21
    if list(record.get("gate_sequence") or []) != list(GATE_SEQUENCE):
        failures.append("gate_sequence_tampered")
    if record.get("next_required_action") != NEXT_HUMAN_GATE_AFTER_PROPOSAL:
        failures.append("next_action_not_spec_gate")
    if record.get("does_not_start_c21") is not True:
        failures.append("must_not_start_c21")
    if record.get("c21_candidate_id") is not None:
        failures.append("c21_must_be_none")
    for gate in ("spec_gate_locked", "detector_gate_locked", "labels_gate_locked",
                 "replay_gate_locked", "paper_trading_gate_locked",
                 "live_gate_locked"):
        if record.get(gate) is not True:
            failures.append("downstream_gate_unlocked_%s" % gate)

    locks = record.get("scope_locks") or {}
    for key in ("no_build", "no_detector", "no_labels", "no_replay", "no_pnl",
                "no_optimization", "no_tuning", "no_rescue", "no_data_fetch",
                "no_new_instrument_class", "no_xauusd", "no_commit", "no_push",
                "no_broker", "no_order_logic", "no_net_market_beta",
                "no_estimated_cross_asset_hedge", "no_paper_trading",
                "no_live_trading", "no_gate_skip", "no_rejected_family_repropose",
                "no_start_c21"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
