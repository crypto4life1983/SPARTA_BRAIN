"""RETURN-ENGINE GAP -- NEXT CANDIDATE RECOMMENDATION (PURE, RESEARCH ONLY, ADVISORY).

After C23 (low-vol) and C24 (illiquidity) failed as neutral cross-sectional portfolio sleeves,
the portfolio still lacks a durable RETURN ENGINE (only the always-on neutral carry null is a
confirmed diversifier-grade dampener). This contract DISTILS the recurring C1-C25 failure modes
and RECOMMENDS exactly one preferred next candidate family + two backups for HUMAN REVIEW.

It is RECOMMENDATION-ONLY: it proposes a direction, cites why it is materially distinct from the
26-family rejected ledger AND from C22/C23/C24/C25, and explains how it avoids each known failure
mode. It builds NO spec/detector/labels/replay, runs NO optimization / data fetch, activates /
promotes NOTHING, does NOT advance C22, does NOT reactivate C23/C24, and modifies NO ledger /
lifecycle / lane-status. Every capability flag is pinned False with a full scope_locks set.

PREFERRED: cross_sectional_crypto_funding_carry_market_neutral_v1 -- rank the liquid perp
universe by funding rate and harvest the cross-sectional funding DISPERSION as a DELTA-NEUTRAL
multi-asset carry (long-spot/short-perp on the highest-funding names; the perp leg is a HEDGE,
not a directional short), rebalanced at LOW turnover. The C20/C21 lessons proved the always-on
neutral carry NULL is genuinely positive (+21.2%, Sharpe ~1.09) and explicitly flagged the
always-on carry as a SEPARATE future candidate; this is the cross-sectional, dispersion-harvesting
return-engine form of that proven positive premium -- distinct from the same-asset carry TIMING
that C20/C21 rejected.

MAIN BLOCKER (disclosed): a cross-sectional funding carry needs BROAD multi-asset FUNDING data;
only 3 names (BTC/ETH/SOL) have frozen funding today, and the broad universe carries OHLCV+volume
but NO funding. So this direction is DATA-GATED on a separate, human-approved broad-funding data
phase before it can be evaluated.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.research_expansion_plan_v1_contract as _rep

REC_SCHEMA_VERSION = 1
REC_MODE = "RESEARCH_ONLY"
REC_LANE = "portfolio_sleeve_evaluation"

RECORD_ID = "RETURN_ENGINE_GAP_NEXT_CANDIDATE_RECOMMENDATION_V1"
VERDICT = "RECOMMEND_NEXT_RETURN_ENGINE_CANDIDATE_FOR_HUMAN_REVIEW"

REJECTED_FAMILIES_C1_TO_C21 = tuple(_rep.REJECTED_FAMILIES_C1_TO_C21)   # 26
C22_FAMILY = "external_signum_trend_radar_gc_long_short"
C23_FAMILY = "crypto_cross_sectional_low_volatility_anomaly_beta_neutral"
C24_FAMILY = "crypto_cross_sectional_illiquidity_premium_beta_neutral"
C25_FAMILY = "intraday_momentum_breakout_retest_reversal_scalping_directional"

# --- recurring failure modes distilled from C1-C25 --------------------------
FAILURE_MODES = (
    {"mode": "overtrading_cost_drag",
     "seen_in": "C20 (704 trades, 521% cost drag), C23 (14.8x turnover, 29.5% drag)"},
    {"mode": "short_leg_bleed",
     "seen_in": "C23 (short high-vol melts up), C24 (short liquid majors melt up)"},
    {"mode": "benchmark_mismatch_loses_to_buy_and_hold_risk_adjusted",
     "seen_in": "C14, C15, C17, C18 (directional, beaten by BTC/SOL buy-and-hold)"},
    {"mode": "non_stationary_single_regime_2021_artifact",
     "seen_in": "C24 (entire edge is 2021; ex-2021 -45.7%; negative 2024-2026)"},
    {"mode": "weak_durability_after_top_period_removal_or_forward_oos",
     "seen_in": "C11, C14, C17, C18, C19, C21, C24"},
    {"mode": "directional_systems_fail_after_fees",
     "seen_in": "C1-C5, C12-C15, C18, C22-shape, C25"},
    {"mode": "neutral_systems_lose_via_bad_directional_short_leg",
     "seen_in": "C23, C24 (neutral construction, but the short leg was directional poison)"},
)

# --- preferred next candidate ------------------------------------------------
PREFERRED_FAMILY = "cross_sectional_crypto_funding_carry_market_neutral"
PREFERRED = {
    "family": PREFERRED_FAMILY,
    "name": "cross_sectional_crypto_funding_carry_market_neutral_v1",
    "thesis": (
        "Rank the liquid crypto perp universe by funding rate and harvest the cross-sectional "
        "funding DISPERSION as a DELTA-NEUTRAL multi-asset carry: long-spot/short-perp on the "
        "highest-funding names (and the mirror on persistently-negative-funding names). The perp "
        "leg is a price HEDGE, not a directional short, so the position collects funding while "
        "carrying ~zero net market beta. Rebalanced at LOW turnover. The edge source is the "
        "cross-sectional funding-rate premium -- a structural, persistent, POSITIVE crypto carry "
        "(the C20/C21 always-on neutral null earned +21.2% at Sharpe ~1.09 across 2020-2026)."),
    "edge_axis": "cross_sectional_funding_rate_dispersion_delta_neutral_carry",
    "is_market_neutral": True,
    "has_directional_short_leg": False,   # short perp is a hedge, not a directional bet
    "targets_return_engine_gap": True,
}

# why distinct + how it avoids each failure mode
PREFERRED_DISTINCTNESS = (
    "vs C20/C21 (mechanically_neutral / low_turnover SAME-ASSET spot/perp funding carry): those "
    "TIMED a single asset's carry and were rejected because the timing added no edge over the "
    "always-on null -- this is a CROSS-SECTIONAL rank-and-harvest of funding DISPERSION across "
    "MANY assets (a carry FACTOR), the always-on positive premium the C20/C21 lessons explicitly "
    "flagged as a separate future candidate, NOT same-asset timing",
    "vs C23/C24 (cross-sectional low-vol / illiquidity): same robust NEUTRAL high-breadth shape, "
    "but the sort variable is FUNDING (a proven-positive, persistent premium) not realized vol or "
    "Amihud illiquidity (which proved non-durable / cost-fragile), and the short leg is a delta "
    "HEDGE rather than a directional short",
    "vs all DIRECTIONAL families (C1-C5, C13-C15, C18, C22, C25): it is delta-neutral with no "
    "directional price-timing trigger, so buy-and-hold is not its benchmark and it does not bleed "
    "when crypto melts up",
    "not in the 26-family rejected ledger; distinct from the C22/C23/C24 families and the C25 "
    "no-go",
)
PREFERRED_AVOIDS = {
    "overtrading_cost_drag": "always-on / low-turnover (<= monthly) -> minimal turnover & drag",
    "short_leg_bleed": "the short perp is a delta hedge offset by long spot -> no melt-up bleed",
    "benchmark_mismatch": "market-neutral -> judged vs a random neutral null, not buy-and-hold",
    "non_stationary_2021_artifact": "funding carry is structural & persistent across regimes "
                                    "(the always-on null was positive over the full 2020-2026 "
                                    "window, Sharpe ~1.09), not a single-regime relic",
    "weak_durability": "must STILL pass forward-OOS + top-period-removal, but the premium has a "
                       "structural source (funding) rather than a transient anomaly",
    "directional_fail_after_fees": "not directional; delta-neutral by construction",
    "neutral_bad_short_leg": "the short leg is a hedge, not a directional short -> avoids the "
                             "exact C23/C24 trap",
}

# --- two backup ideas --------------------------------------------------------
BACKUPS = (
    {"family": "always_on_multi_asset_neutral_funding_carry_sleeve",
     "idea": "Productionize the PROVEN positive null itself: an always-on, multi-asset, "
             "delta-neutral funding-carry sleeve (no timing, no cross-sectional sort) -- the "
             "C20/C21 null earned +21.2% / Sharpe ~1.09. Lower return than the preferred but "
             "highest confidence; a USEFUL_DIVERSIFIER-grade dampener, not a full engine.",
     "distinct_note": "the un-timed always-on form the C20/C21 lessons flagged as a separate "
                      "future candidate; not the same-asset TIMING that was rejected",
     "main_blocker": "needs broad multi-asset funding data (same data gate as preferred)"},
    {"family": "long_or_flat_trend_drawdown_controlled_contribution_sleeve",
     "idea": "A NEVER-SHORT trend system: long the crypto basket in uptrends, FLAT (cash) in "
             "downtrends -- judged on portfolio CONTRIBUTION (drawdown reduction + low "
             "correlation), NOT on beating buy-and-hold standalone. Avoids the short-leg bleed "
             "entirely by going to cash rather than shorting.",
     "distinct_note": "OVERLAP RISK: shares mechanism with C15/C18 (trend) which lost to B&H; "
                      "distinct ONLY via never-short + the contribution (not dominance) lens. "
                      "Weaker recommendation -- flagged honestly.",
     "main_blocker": "must demonstrate it is not just a re-skin of the rejected C15/C18 trend "
                     "families; OHLCV is available so it is the most data-ready of the three"},
)

NEXT_HUMAN_GATE = (
    "HUMAN_DECISION_OPEN_CROSS_SECTIONAL_FUNDING_CARRY_AS_NEXT_RETURN_ENGINE_CANDIDATE_AFTER_"
    "BROAD_FUNDING_DATA_PHASE")
MAIN_BLOCKER = (
    "DATA-GATED: a cross-sectional funding carry needs BROAD multi-asset FUNDING data; only "
    "BTC/ETH/SOL funding is frozen today and the broad universe has OHLCV+volume but NO funding. "
    "A separate, human-approved broad-funding data phase (survivorship caveats apply) is required "
    "before evaluation -- this recommendation does NOT authorize that fetch.")

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "builds_spec", "builds_detector", "runs_labels", "runs_replay",
    "runs_backtest", "computes_pnl", "optimizes_parameters", "reparameterizes", "fetches_data",
    "reads_real_data", "mutates_data", "stages_data", "auto_commits", "auto_pushes",
    "commits_data_files", "activates_any_candidate", "promotes_any_candidate", "advances_c22",
    "reactivates_c23", "reactivates_c24", "modifies_official_ledger", "modifies_lifecycle",
    "modifies_lane_status", "modifies_scheduler", "sends_notifications", "calls_api",
    "uses_network", "uses_credentials", "connects_broker", "connects_exchange", "places_orders",
    "contains_order_logic", "paper_trading", "live_trading", "deploys_capital", "promotes_gate",
    "unlocks_downstream_gate", "skips_any_gate", "reproposes_rejected_family",
    "advances_without_human_approval", "claims_profitability", "claims_edge",
    "crosses_into_forbidden_gate",
)


def get_recommendation_label() -> str:
    return (
        "Return-engine gap -- next candidate recommendation (READ-ONLY, RESEARCH ONLY, ADVISORY). "
        "PREFERRED: cross_sectional_crypto_funding_carry_market_neutral_v1 -- harvest the "
        "cross-sectional funding-rate dispersion as a delta-neutral multi-asset carry (the proven "
        "positive crypto premium), distinct from the rejected SAME-ASSET carry timing (C20/C21) "
        "and the failed vol/illiquidity sorts (C23/C24); avoids overtrading, short-leg bleed, "
        "benchmark mismatch, and 2021-artifact failure modes. DATA-GATED on a broad-funding data "
        "phase. Recommendation only: activates/promotes nothing, C22 unchanged, C23/C24 not "
        "reactivated, ledger/lifecycle unchanged. NOT a profitability claim.")


def get_recommendation_next_action() -> str:
    return NEXT_HUMAN_GATE


def build_recommendation() -> dict[str, Any]:
    """Assemble the frozen return-engine recommendation. Pure; no I/O; recommendation only.
    Gated on the preferred family being materially distinct from the rejected ledger + C22-C25."""
    blockers: list = []
    if PREFERRED_FAMILY in REJECTED_FAMILIES_C1_TO_C21:
        blockers.append("preferred_in_rejected_ledger")
    if PREFERRED_FAMILY in (C22_FAMILY, C23_FAMILY, C24_FAMILY, C25_FAMILY):
        blockers.append("preferred_collides_with_c22_c25")
    if len(REJECTED_FAMILIES_C1_TO_C21) != 26:
        blockers.append("ledger_not_26")
    for b in BACKUPS:
        if b["family"] in REJECTED_FAMILIES_C1_TO_C21:
            blockers.append("backup_in_rejected_ledger:%s" % b["family"])

    record: dict[str, Any] = {
        "schema_version": REC_SCHEMA_VERSION, "mode": REC_MODE, "lane": REC_LANE,
        "record_id": RECORD_ID,
        "label": get_recommendation_label(),
        "is_recommendation_only": True,
        "blockers": blockers,
        "verdict": (VERDICT if not blockers else "RECOMMENDATION_BLOCKED"),
        "failure_modes": [dict(f) for f in FAILURE_MODES],
        "preferred_candidate": dict(PREFERRED),
        "preferred_distinctness": list(PREFERRED_DISTINCTNESS),
        "preferred_avoids_failure_modes": dict(PREFERRED_AVOIDS),
        "backups": [dict(b) for b in BACKUPS],
        "main_blocker": MAIN_BLOCKER,
        "is_data_gated": True,
        "preferred_not_in_rejected_ledger": PREFERRED_FAMILY not in REJECTED_FAMILIES_C1_TO_C21,
        "preferred_distinct_from_c22_c25": PREFERRED_FAMILY not in (
            C22_FAMILY, C23_FAMILY, C24_FAMILY, C25_FAMILY),
        "preferred_is_market_neutral": True,
        "preferred_has_no_directional_short_leg": True,
        "targets_return_engine_gap": True,
        "rejected_families_count": len(REJECTED_FAMILIES_C1_TO_C21),
        # preservation
        "activates_nothing": True,
        "promotes_nothing": True,
        "c22_unchanged": True,
        "c23_c24_not_reactivated": True,
        "does_not_modify_official_ledger": True,
        "does_not_modify_lifecycle": True,
        "does_not_modify_lane_status": True,
        "is_profitability_claim": False,
        "human_review_required": True,
        "current_loop_stage": "next_candidate_recommendation",
        "next_required_action": NEXT_HUMAN_GATE,
        # downstream gates locked
        "proposal_gate_locked_until_human_opens": True,
        "data_fetch_gate_locked": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_build": True, "no_spec": True, "no_detector": True, "no_labels": True,
        "no_replay": True, "no_backtest": True, "no_pnl": True, "no_optimization": True,
        "no_data_fetch": True, "no_data_mutation": True, "no_commit_data": True,
        "no_activate_candidate": True, "no_promote_candidate": True, "no_advance_c22": True,
        "no_reactivate_c23": True, "no_reactivate_c24": True, "no_modify_official_ledger": True,
        "no_modify_lifecycle": True, "no_modify_lane_status": True, "no_stage": True,
        "no_commit": True, "no_push": True, "no_broker": True, "no_order_logic": True,
        "no_paper_trading": True, "no_live_trading": True, "no_gate_skip": True,
        "no_repropose_rejected_family": True, "no_profitability_claim": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_recommendation(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the record is research-only, recommendation-only;
    distils >= 6 failure modes; recommends a PREFERRED family that is market-neutral with NO
    directional short leg, targets the return-engine gap, is NOT in the 26-family ledger and is
    distinct from C22-C25; includes 2 backups; discloses the data-gated blocker; activates /
    promotes NOTHING, leaves C22 / C23 / C24 / ledger / lifecycle / lane-status unchanged; makes
    no profitability claim; and pins every capability flag False."""
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
    fm_names = {f.get("mode") for f in (record.get("failure_modes") or [])}
    for must in ("overtrading_cost_drag", "short_leg_bleed",
                 "non_stationary_single_regime_2021_artifact",
                 "neutral_systems_lose_via_bad_directional_short_leg"):
        if must not in fm_names:
            failures.append("failure_mode_missing_%s" % must)

    pref = record.get("preferred_candidate") or {}
    if not pref.get("family"):
        failures.append("preferred_missing")
    if pref.get("is_market_neutral") is not True:
        failures.append("preferred_not_neutral")
    if pref.get("has_directional_short_leg") is not False:
        failures.append("preferred_has_directional_short")
    if pref.get("targets_return_engine_gap") is not True:
        failures.append("preferred_not_targeting_gap")
    if record.get("preferred_not_in_rejected_ledger") is not True:
        failures.append("preferred_in_ledger")
    if pref.get("family") in REJECTED_FAMILIES_C1_TO_C21:
        failures.append("preferred_family_listed_rejected")
    if record.get("preferred_distinct_from_c22_c25") is not True:
        failures.append("preferred_collides_c22_c25")
    if len(record.get("preferred_distinctness") or []) < 3:
        failures.append("distinctness_insufficient")
    if len(record.get("preferred_avoids_failure_modes") or {}) < 6:
        failures.append("avoids_map_incomplete")

    if len(record.get("backups") or []) != 2:
        failures.append("must_have_2_backups")
    for b in (record.get("backups") or []):
        if b.get("family") in REJECTED_FAMILIES_C1_TO_C21:
            failures.append("backup_in_ledger:%s" % b.get("family"))

    if record.get("is_data_gated") is not True or not record.get("main_blocker"):
        failures.append("data_gated_blocker_missing")

    # preservation
    for k in ("activates_nothing", "promotes_nothing", "c22_unchanged",
              "c23_c24_not_reactivated", "does_not_modify_official_ledger",
              "does_not_modify_lifecycle", "does_not_modify_lane_status"):
        if record.get(k) is not True:
            failures.append("preservation_off_%s" % k)
    if record.get("is_profitability_claim") is not False:
        failures.append("must_not_claim_profitability")
    if record.get("rejected_families_count") != 26:
        failures.append("ledger_not_26")
    if record.get("next_required_action") != NEXT_HUMAN_GATE:
        failures.append("next_gate_wrong")

    locks = record.get("scope_locks") or {}
    for key in ("no_build", "no_spec", "no_labels", "no_replay", "no_optimization",
                "no_data_fetch", "no_commit_data", "no_activate_candidate",
                "no_promote_candidate", "no_advance_c22", "no_reactivate_c23",
                "no_reactivate_c24", "no_modify_official_ledger", "no_modify_lifecycle",
                "no_commit", "no_push", "no_broker", "no_order_logic", "no_paper_trading",
                "no_live_trading", "no_repropose_rejected_family", "no_profitability_claim"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
