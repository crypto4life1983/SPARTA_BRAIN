"""RETURN-ENGINE GAP -- NEXT CANDIDATE RECOMMENDATION V2 (PURE, RESEARCH ONLY, ADVISORY).

V1 recommended cross-sectional funding carry; its SELECTION form was then REJECTED as a return
engine (it did not beat the always-on funding null and was 2021-concentrated), and the always-on
funding carry was preserved only as a diversifier/dampener. The portfolio still lacks a durable
RETURN ENGINE. V2 distils the recurring C1-C25 + sleeve/funding failure modes and recommends a
FRESH return-engine direction that is materially distinct from every rejected family AND from the
funding diversifier finding.

PREFERRED: crypto_volatility_risk_premium_delta_hedged_short_vol_v1 -- harvest the crypto
VOLATILITY RISK PREMIUM (implied > realized vol, a persistent compensation for bearing variance
/ crash risk) via DELTA-HEDGED SHORT VOLATILITY on BTC/ETH options. The position is short VOL
(not short PRICE) and delta-hedged, so it does NOT bleed when crypto melts up; the return source
is a structural insurance premium, NOT price-timing, NOT carry, NOT a cross-sectional anomaly
sort, NOT a selection-vs-null. VRP is regime-spanning and is typically RICHEST in high-vol bear
regimes -- the opposite of a 2021-only artifact.

HONEST FRAMING (task item 6): the next best step is actually a DATA-SOURCE PHASE. VRP needs
OPTIONS / IMPLIED-VOL data (e.g. Deribit public BTC/ETH options IV + settlements), which is NOT
in the frozen spot+funding universe. So this is DATA-GATED: an options/IV data phase is the
prerequisite, and short-vol's TAIL RISK must be gated hard (it sells insurance -> large losses
in crashes). This contract RECOMMENDS only; it builds no spec/detector/labels/replay, runs no
optimization/data fetch, activates/promotes NOTHING, does not advance C22, does not reactivate
C23/C24 or the funding selection, and modifies no ledger/lifecycle/lane-status.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.research_expansion_plan_v1_contract as _rep

REC_SCHEMA_VERSION = 1
REC_MODE = "RESEARCH_ONLY"
REC_LANE = "portfolio_sleeve_evaluation"

RECORD_ID = "RETURN_ENGINE_GAP_NEXT_CANDIDATE_RECOMMENDATION_V2"
VERDICT = "RECOMMEND_NEXT_RETURN_ENGINE_CANDIDATE_V2_FOR_HUMAN_REVIEW"

REJECTED_FAMILIES_C1_TO_C21 = tuple(_rep.REJECTED_FAMILIES_C1_TO_C21)   # 26
# families/findings the preferred MUST differ from (incl. the explicit do-not-recommend list)
FORBIDDEN_DIRECTIONS = (
    "crypto_cross_sectional_low_volatility_anomaly_beta_neutral",        # C23
    "crypto_cross_sectional_illiquidity_premium_beta_neutral",           # C24
    "cross_sectional_crypto_funding_carry_market_neutral",               # rejected selection
    "always_on_broad_multi_asset_neutral_funding_carry",                 # diversifier finding
    "mechanically_neutral_spot_perp_basis_funding_carry",                # C20
    "low_turnover_same_asset_spot_perp_funding_carry",                   # C21
    "external_signum_trend_radar_gc_long_short",                         # C22
    "intraday_momentum_breakout_retest_reversal_scalping_directional",   # C25
)

# --- recurring failure modes (C1-C25 + sleeve/funding) ----------------------
FAILURE_MODES = (
    {"mode": "overtrading_cost_drag", "seen_in": "C20, C23, funding selection (10-15x turnover)"},
    {"mode": "non_stationary_2021_only_artifact", "seen_in": "C24, funding selection (ex-2021 ~0)"},
    {"mode": "short_leg_bleed", "seen_in": "C23, C24 (short high-vol/liquid melts up)"},
    {"mode": "selection_timing_loses_to_always_on_null",
     "seen_in": "C21, cross-sectional funding selection"},
    {"mode": "benchmark_mismatch_loses_to_buy_and_hold", "seen_in": "C14, C15, C17, C18"},
    {"mode": "directional_systems_fail_after_fees", "seen_in": "C1-C5, C12-C15, C18, C22, C25"},
    {"mode": "weak_forward_oos_durability", "seen_in": "C11, C14, C17-C19, C21, C24, funding sel."},
)

# --- preferred return-engine candidate --------------------------------------
PREFERRED_FAMILY = "crypto_volatility_risk_premium_delta_hedged_short_vol"
PREFERRED = {
    "family": PREFERRED_FAMILY,
    "name": "crypto_volatility_risk_premium_delta_hedged_short_vol_v1",
    "thesis": (
        "Harvest the crypto VOLATILITY RISK PREMIUM -- the persistent gap by which option-implied "
        "vol exceeds subsequently-realized vol (compensation for bearing variance / crash risk) -- "
        "via DELTA-HEDGED SHORT VOLATILITY on liquid BTC/ETH options (sell straddles/strangles, "
        "delta-hedge with perp/spot). The position is short VOL, not short PRICE, and delta-hedged, "
        "so it carries ~zero net price beta and does NOT bleed when crypto melts up. The return "
        "source is a structural insurance premium -- regime-spanning and typically RICHEST in "
        "high-vol bear regimes (not a 2021 artifact)."),
    "edge_axis": "implied_minus_realized_volatility_risk_premium_delta_hedged",
    "is_return_engine": True,
    "is_dampener_only": False,
    "is_market_neutral_ish": True,
    "has_directional_short_price_leg": False,   # short VOL, not short PRICE
    "targets_return_engine_gap": True,
}

PREFERRED_DISTINCTNESS = (
    "vs C23 low-vol (realized-vol SORT of spot) and C24 illiquidity: this is the IMPLIED-vs-"
    "REALIZED vol PREMIUM via OPTIONS -- a different instrument (options, not spot), a different "
    "edge (insurance premium, not an anomaly sort), and no cross-sectional short leg",
    "vs the funding families (C20/C21 same-asset carry, the rejected cross-sectional funding "
    "SELECTION, and the always-on funding diversifier): VRP is a VOLATILITY premium, not a "
    "FUNDING/basis carry; it is NOT a selection that competes with a free always-on null",
    "vs all DIRECTIONAL families (C1-C5, C13-C15, C18, C22, C25): delta-hedged -> no directional "
    "price-timing trigger, no buy-and-hold benchmark, no melt-up short bleed",
    "not in the 26-family rejected ledger and not any FORBIDDEN direction (low-vol/illiquidity/"
    "funding-selection/same-asset-carry/directional/2021-artifact)",
)
PREFERRED_AVOIDS = {
    "overtrading_cost_drag": "premium captured at expiry; only delta-hedge turnover (low-moderate)",
    "non_stationary_2021_only_artifact": "VRP is structural & regime-spanning, RICHEST in high-vol "
                                         "bear regimes -- not a 2021 phenomenon",
    "short_leg_bleed": "short VOLATILITY (delta-hedged), not short PRICE -> no melt-up bleed",
    "selection_loses_to_null": "a structural premium harvest, not a selection vs a free null",
    "benchmark_mismatch": "market-neutral-ish -> judged vs cost + the realized-vol cost of short "
                          "gamma, not vs buy-and-hold",
    "directional_fail_after_fees": "not directional; delta-neutral by construction",
    "weak_forward_oos": "durable economic source (variance/crash-risk compensation), but MUST "
                        "still pass forward-OOS + crash stress gates",
}

# --- the honest meta-conclusion: the next step is a DATA PHASE ---------------
NEXT_BEST_STEP_IS_DATA_PHASE = True
DATA_PHASE_NEEDED = (
    "OPTIONS / IMPLIED-VOL data phase: liquid crypto options IV + settlements (e.g. Deribit "
    "public BTC/ETH option chains / DVOL-style vol index) + spot/perp for delta-hedging. NOT in "
    "the frozen spot+funding universe. This is the binding prerequisite -- the preferred engine "
    "cannot be evaluated until it exists. (Survivorship is less acute for BTC/ETH majors, but the "
    "options data must be sourced + frozen + SHA-pinned under a separate human-approved phase.)")

# --- two backups ------------------------------------------------------------
BACKUPS = (
    {"family": "options_iv_data_phase_then_vrp_evaluation",
     "idea": "Treat the OPTIONS/IV DATA PHASE itself as the next concrete step (source + freeze "
             "Deribit-style BTC/ETH IV/settlement data), enabling the preferred VRP engine. This "
             "is arguably THE next action rather than a candidate.",
     "distinct_note": "infrastructure/data, not a strategy family; unblocks the preferred engine",
     "main_blocker": "requires a new bounded options-data fetcher + safety tests (new network "
                     "surface) under explicit human approval"},
    {"family": "deployment_grade_revalidation_of_always_on_funding_carry_diversifier",
     "idea": "Convert the ONE positive finding (always-on broad funding carry diversifier) into "
             "something trustworthy: re-evaluate it deployment-grade with PERP-BASIS "
             "mark-to-market + survivorship-aware data. Not a new engine, but de-risks the only "
             "durable positive result and could anchor a low-vol return sleeve.",
     "distinct_note": "hardens an existing diversifier finding; NOT a reactivation of the rejected "
                      "funding SELECTION -- it is the always-on (no-selection) form",
     "main_blocker": "needs perp-basis + survivorship-aware data (a separate paid/heavier phase)"},
)

NEXT_HUMAN_GATE = (
    "HUMAN_APPROVED_ASSESS_AND_PREPARE_OPTIONS_IMPLIED_VOL_DATA_PHASE_FOR_VRP_ENGINE_ONLY")
MAIN_BLOCKER = (
    "DATA-GATED: the preferred VRP engine needs options/implied-vol data that is NOT in the frozen "
    "spot+funding universe; an options/IV data phase is the binding prerequisite. SECOND RISK: "
    "short-vol sells insurance -> large tail losses in crashes; any future version must pass hard "
    "crash-stress + forward-OOS gates and is NOT deployable naked.")

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "builds_spec", "builds_detector", "runs_labels", "runs_replay",
    "runs_backtest", "computes_pnl", "optimizes_parameters", "fetches_data", "reads_real_data",
    "mutates_data", "stages_data", "auto_commits", "auto_pushes", "commits_data_files",
    "activates_any_candidate", "promotes_any_candidate", "advances_c22", "reactivates_c23",
    "reactivates_c24", "reactivates_funding_selection", "modifies_official_ledger",
    "modifies_lifecycle", "modifies_lane_status", "modifies_scheduler", "sends_notifications",
    "calls_api", "uses_network", "uses_credentials", "connects_broker", "connects_exchange",
    "places_orders", "contains_order_logic", "sells_options_live", "paper_trading",
    "live_trading", "deploys_capital", "promotes_gate", "unlocks_downstream_gate", "skips_any_gate",
    "reproposes_rejected_family", "advances_without_human_approval", "claims_profitability",
    "claims_edge", "claims_deployment_grade", "crosses_into_forbidden_gate",
)


def get_recommendation_label() -> str:
    return (
        "Return-engine gap V2 recommendation (READ-ONLY, RESEARCH ONLY, ADVISORY). PREFERRED: "
        "crypto VOLATILITY-RISK-PREMIUM delta-hedged short-vol engine -- a structural insurance "
        "premium (implied>realized vol), distinct from every rejected family and the funding "
        "diversifier, avoiding overtrading / 2021-artifact / short-price-bleed / selection-vs-null "
        "/ directional-fee failures. DATA-GATED: the real next step is an OPTIONS/IV data phase; "
        "short-vol tail risk must be gated hard. Recommendation only: activates/promotes nothing, "
        "C22 unchanged, C23/C24 + funding selection not reactivated, ledger/lifecycle unchanged. "
        "NOT a profitability or deployment claim.")


def get_recommendation_next_action() -> str:
    return NEXT_HUMAN_GATE


def build_recommendation_v2() -> dict[str, Any]:
    """Assemble the frozen V2 return-engine recommendation. Pure; no I/O; recommendation only.
    Gated on the preferred family being distinct from the rejected ledger AND every forbidden
    direction."""
    blockers: list = []
    if PREFERRED_FAMILY in REJECTED_FAMILIES_C1_TO_C21:
        blockers.append("preferred_in_rejected_ledger")
    if PREFERRED_FAMILY in FORBIDDEN_DIRECTIONS:
        blockers.append("preferred_is_forbidden_direction")
    if len(REJECTED_FAMILIES_C1_TO_C21) != 26:
        blockers.append("ledger_not_26")
    for b in BACKUPS:
        if b["family"] in REJECTED_FAMILIES_C1_TO_C21 or b["family"] in FORBIDDEN_DIRECTIONS:
            blockers.append("backup_collides:%s" % b["family"])

    record: dict[str, Any] = {
        "schema_version": REC_SCHEMA_VERSION, "mode": REC_MODE, "lane": REC_LANE,
        "record_id": RECORD_ID,
        "label": get_recommendation_label(),
        "is_recommendation_only": True,
        "supersedes": "RETURN_ENGINE_GAP_NEXT_CANDIDATE_RECOMMENDATION_V1",
        "blockers": blockers,
        "verdict": (VERDICT if not blockers else "RECOMMENDATION_V2_BLOCKED"),
        "failure_modes": [dict(f) for f in FAILURE_MODES],
        "preferred_candidate": dict(PREFERRED),
        "preferred_distinctness": list(PREFERRED_DISTINCTNESS),
        "preferred_avoids_failure_modes": dict(PREFERRED_AVOIDS),
        "backups": [dict(b) for b in BACKUPS],
        "next_best_step_is_data_phase": NEXT_BEST_STEP_IS_DATA_PHASE,
        "data_phase_needed": DATA_PHASE_NEEDED,
        "main_blocker": MAIN_BLOCKER,
        "is_data_gated": True,
        "preferred_not_in_rejected_ledger": PREFERRED_FAMILY not in REJECTED_FAMILIES_C1_TO_C21,
        "preferred_not_forbidden_direction": PREFERRED_FAMILY not in FORBIDDEN_DIRECTIONS,
        "preferred_is_return_engine_not_dampener": True,
        "preferred_has_no_directional_short_price_leg": True,
        "targets_return_engine_gap": True,
        "rejected_families_count": len(REJECTED_FAMILIES_C1_TO_C21),
        "forbidden_directions": list(FORBIDDEN_DIRECTIONS),
        # preservation
        "activates_nothing": True, "promotes_nothing": True, "c22_unchanged": True,
        "c23_c24_not_reactivated": True, "funding_selection_not_reactivated": True,
        "does_not_modify_official_ledger": True, "does_not_modify_lifecycle": True,
        "does_not_modify_lane_status": True, "is_profitability_claim": False,
        "is_deployment_claim": False,
        "human_review_required": True,
        "current_loop_stage": "next_candidate_recommendation_v2",
        "next_required_action": NEXT_HUMAN_GATE,
        "data_fetch_gate_locked": True, "options_short_vol_gate_locked": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_build": True, "no_spec": True, "no_detector": True, "no_labels": True,
        "no_replay": True, "no_backtest": True, "no_optimization": True, "no_data_fetch": True,
        "no_data_mutation": True, "no_commit_data": True, "no_activate_candidate": True,
        "no_promote_candidate": True, "no_advance_c22": True, "no_reactivate_c23": True,
        "no_reactivate_c24": True, "no_reactivate_funding_selection": True,
        "no_modify_official_ledger": True, "no_modify_lifecycle": True,
        "no_modify_lane_status": True, "no_stage": True, "no_commit": True, "no_push": True,
        "no_broker": True, "no_order_logic": True, "no_sell_options_live": True,
        "no_paper_trading": True, "no_live_trading": True, "no_gate_skip": True,
        "no_repropose_rejected_family": True, "no_profitability_claim": True,
        "no_deployment_claim": True, "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_recommendation_v2(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the record is research-only, recommendation-only;
    distils >= 6 failure modes (incl. the new selection-vs-null + 2021-artifact ones); recommends
    a PREFERRED RETURN-ENGINE family (not a dampener) that is delta-hedged with NO directional
    short-price leg, targets the gap, is NOT in the 26-family ledger AND not any forbidden
    direction; includes 2 backups (none forbidden); flags the data-phase prerequisite + the
    short-vol tail risk; activates/promotes NOTHING and leaves C22/C23/C24/funding-selection/
    ledger/lifecycle unchanged; makes no profitability/deployment claim; pins every capability
    flag False."""
    failures: list = []
    if record.get("mode") != REC_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_recommendation_only") is not True:
        failures.append("not_recommendation_only")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("verdict") != VERDICT:
        failures.append("verdict_wrong")

    if len(record.get("failure_modes") or []) < 6:
        failures.append("failure_modes_incomplete")
    fm = {f.get("mode") for f in (record.get("failure_modes") or [])}
    for must in ("overtrading_cost_drag", "non_stationary_2021_only_artifact",
                 "short_leg_bleed", "selection_timing_loses_to_always_on_null"):
        if must not in fm:
            failures.append("failure_mode_missing_%s" % must)

    pref = record.get("preferred_candidate") or {}
    if not pref.get("family"):
        failures.append("preferred_missing")
    if pref.get("is_return_engine") is not True:
        failures.append("preferred_not_return_engine")
    if pref.get("is_dampener_only") is not False:
        failures.append("preferred_must_not_be_dampener_only")
    if pref.get("has_directional_short_price_leg") is not False:
        failures.append("preferred_has_directional_short_price")
    if pref.get("targets_return_engine_gap") is not True:
        failures.append("preferred_not_targeting_gap")
    if record.get("preferred_not_in_rejected_ledger") is not True:
        failures.append("preferred_in_ledger")
    if pref.get("family") in REJECTED_FAMILIES_C1_TO_C21:
        failures.append("preferred_family_listed_rejected")
    if record.get("preferred_not_forbidden_direction") is not True:
        failures.append("preferred_forbidden")
    if pref.get("family") in FORBIDDEN_DIRECTIONS:
        failures.append("preferred_is_forbidden")
    if len(record.get("preferred_distinctness") or []) < 3:
        failures.append("distinctness_insufficient")
    if len(record.get("preferred_avoids_failure_modes") or {}) < 6:
        failures.append("avoids_map_incomplete")

    if len(record.get("backups") or []) != 2:
        failures.append("must_have_2_backups")
    for b in (record.get("backups") or []):
        if b.get("family") in REJECTED_FAMILIES_C1_TO_C21 or b.get("family") in FORBIDDEN_DIRECTIONS:
            failures.append("backup_collides:%s" % b.get("family"))

    # data-phase honesty + short-vol tail-risk disclosure
    if record.get("next_best_step_is_data_phase") is not True:
        failures.append("must_flag_data_phase")
    if not record.get("data_phase_needed"):
        failures.append("data_phase_not_described")
    if record.get("is_data_gated") is not True:
        failures.append("must_be_data_gated")
    mb = str(record.get("main_blocker", "")).lower()
    if "tail" not in mb and "crash" not in mb:
        failures.append("short_vol_tail_risk_not_disclosed")

    # preservation
    for k in ("activates_nothing", "promotes_nothing", "c22_unchanged",
              "c23_c24_not_reactivated", "funding_selection_not_reactivated",
              "does_not_modify_official_ledger", "does_not_modify_lifecycle",
              "does_not_modify_lane_status"):
        if record.get(k) is not True:
            failures.append("preservation_off_%s" % k)
    if record.get("is_profitability_claim") is not False:
        failures.append("must_not_claim_profitability")
    if record.get("is_deployment_claim") is not False:
        failures.append("must_not_claim_deployment")
    if record.get("rejected_families_count") != 26:
        failures.append("ledger_not_26")
    if record.get("next_required_action") != NEXT_HUMAN_GATE:
        failures.append("next_gate_wrong")

    locks = record.get("scope_locks") or {}
    for key in ("no_build", "no_labels", "no_replay", "no_optimization", "no_data_fetch",
                "no_commit_data", "no_activate_candidate", "no_promote_candidate",
                "no_advance_c22", "no_reactivate_c23", "no_reactivate_c24",
                "no_reactivate_funding_selection", "no_modify_official_ledger",
                "no_modify_lifecycle", "no_commit", "no_push", "no_broker", "no_order_logic",
                "no_sell_options_live", "no_paper_trading", "no_live_trading",
                "no_repropose_rejected_family", "no_profitability_claim", "no_deployment_claim"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
