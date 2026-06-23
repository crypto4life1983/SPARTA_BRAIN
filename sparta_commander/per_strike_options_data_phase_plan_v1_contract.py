"""PER-STRIKE OPTIONS DATA PHASE -- PLAN (PURE, RESEARCH ONLY, PREP ONLY).

Plans (does NOT execute) the per-strike options data phase required for a TRUE delta-hedged
BTC-first VRP backtest -- the Phase-2 follow-on to the pushed Phase-1 index-level VRP feasibility
(which used DVOL index only and was promising for BTC: 30d avg spread +8.8, hit 72.7%, ex-2021
+7.2, 2024-2026 +5.4). Records the required fields, the FREE-data limitation, the paid/forward
data-path options, the BTC-first scope, the frozen layout, the crash-stress windows, the minimum
viable backtest design (incl. hard tail gates + cost model), and the exact next human DECISION
token.

It FETCHES NOTHING, BUYS NOTHING, evaluates NOTHING, runs NO backtest / delta-hedge / straddle
P&L, writes NO data, activates/promotes NOTHING, does NOT advance C22, does NOT reactivate
C23/C24/funding selection, and modifies NO ledger/lifecycle/lane-status. Every capability flag
is pinned False. The actual data procurement remains gated behind a SEPARATE human decision.

PROBE FINDING (read-only, no data written): Deribit public `get_instruments?expired=true` for
BTC options returns only ~44 instruments, ALL from the single most-recent expiry -> the free
public API exposes only LIVE + last-expiry snapshots, NOT multi-year per-strike chain history.
A historical delta-hedged backtest therefore needs PAID history (e.g. Tardis.dev, which carries
Deribit options back to ~2019 -- so even March-2020 becomes coverable) OR FORWARD-only daily
snapshot collection (clean go-forward, NO backfill). A free public approximation is insufficient.
"""
from __future__ import annotations

from typing import Any

PS_SCHEMA_VERSION = 1
PS_MODE = "RESEARCH_ONLY"
PS_LANE = "portfolio_sleeve_evaluation"

RECORD_ID = "PER_STRIKE_OPTIONS_DATA_PHASE_PLAN_V1"
VERDICT = ("PER_STRIKE_OPTIONS_DATA_PHASE_PLANNED__NOT_FREE__PAID_OR_FORWARD_REQUIRED__"
           "HUMAN_DATA_PATH_DECISION_GATED")

NO_EXISTING_INFRA = True
PROBE_FINDING = (
    "Deribit public get_instruments?expired=true (BTC options) returned ~44 instruments, all "
    "from the single most-recent expiry -> free public API = LIVE + last-expiry only, NO "
    "multi-year per-strike chain history.")

# --- required fields for a true delta-hedged VRP backtest -------------------
REQUIRED_FIELDS = (
    "instrument_name", "timestamp", "underlying_or_index_price", "expiration_timestamp",
    "strike", "option_type(call/put)", "mark_price_or_settlement_price", "implied_vol(mark_iv)",
    "greeks.delta", "greeks.gamma", "greeks.vega", "greeks.theta",
    "bid/ask (if available)", "volume (if available)", "open_interest (if available)",
    "settlement/expiry_behavior",
)

# --- free / public feasibility ----------------------------------------------
FREE_PUBLIC_FEASIBILITY = (
    "INSUFFICIENT for a historical backtest. Deribit public endpoints give LIVE chain "
    "(get_instruments + ticker: strike/expiry/type/mark_iv/greeks/mark/OI) and per-instrument "
    "OHLC (get_tradingview_chart_data), plus only a LIMITED last-expiry 'expired' listing -- NOT "
    "a queryable multi-year per-strike chain history. Cannot backfill 2021-2026 for free.")

# --- data-path options ------------------------------------------------------
DATA_PATHS = (
    {"path": "paid_historical", "recommended_primary": True,
     "source": "Tardis.dev (primary; full Deribit options tick/chain history from ~2019), or "
               "Amberdata / Kaiko (alternatives)",
     "pros": "true historical backfill incl. March-2020; full greeks/marks/settlement",
     "cons": "COSTS MONEY (subscription/credits); requires a human purchase decision",
     "covers_march_2020": True},
    {"path": "forward_only_daily_snapshots", "recommended_primary": False,
     "source": "new bounded /public/ Deribit fetcher snapshotting the LIVE chain + ticker "
               "(mark_iv/greeks/mark/OI) once daily, going forward",
     "pros": "no cost; clean, fully-controlled go-forward data on the public boundary",
     "cons": "NO backfill -> builds history only from start date onward (slow; months/years to "
             "accumulate a testable sample); no crash-window history",
     "covers_march_2020": False},
    {"path": "limited_public_approximation", "recommended_primary": False,
     "source": "per-instrument get_tradingview_chart_data for currently/recently queryable "
               "instruments + ticker snapshots",
     "pros": "free, immediate",
     "cons": "PATCHY, survivorship-biased to queryable instruments, no full chain -> "
             "INSUFFICIENT for a credible delta-hedged backtest",
     "covers_march_2020": False},
)
RECOMMENDED_PATH = (
    "For a credible BTC delta-hedged VRP backtest over 2021-2026 (ideally 2020-2026 incl. the "
    "COVID crash), PAID historical (Tardis.dev) is the realistic path. FORWARD-only daily "
    "snapshots are a sound NO-COST fallback that builds clean go-forward data but cannot "
    "backtest history. The limited public approximation is NOT sufficient.")

# --- scope / date range / frozen layout -------------------------------------
BTC_FIRST_SCOPE = {
    "primary": "BTC", "secondary": "ETH (only if data quality + the Phase-1 ETH premium "
                                   "warrant it; Phase-1 showed ETH weaker/fading)",
    "rationale": "Phase-1 BTC VRP was clearly positive + durable; ETH was weaker/fading",
}
PROPOSED_DATE_RANGE = {"target": "2021-03-24..2026-06-21 (DVOL-aligned)",
                       "stretch": "2020-01-01..2026-06-21 if the paid source supports it "
                                  "(enables the March-2020 crash window)"}
PROPOSED_DATA_DIR = "data/deribit_options_chain_universe/"
PROPOSED_MANIFEST_FIELDS = ("source", "data_path_used", "currency", "date_range",
                            "instruments_count", "per_day_chain_rows", "first_last_date",
                            "fields", "sha256_per_file", "survivorship_note",
                            "settlement_convention_note")
PROPOSED_QUALITY_REPORT_FIELDS = ("missing_days", "missing_strikes_summary", "stale_mark_summary",
                                  "zero_bid_or_oi_summary", "delta_coverage", "crash_window_rows",
                                  "feasible_for_delta_hedged_backtest")

# --- crash-stress windows for later validation ------------------------------
CRASH_STRESS_WINDOWS = (
    {"window": "2020-03 COVID crash", "coverable": "only_with_paid_history (Tardis ~2019+)"},
    {"window": "2021-05 China-ban / leverage flush", "coverable": "yes"},
    {"window": "2022-06 Luna/3AC contagion", "coverable": "yes"},
    {"window": "2022-11 FTX collapse", "coverable": "yes"},
    {"window": "2024-08 yen-carry unwind", "coverable": "yes"},
    {"window": "later 2025-2026 drawdowns if present", "coverable": "yes"},
)

# --- minimum viable backtest design (DESIGN ONLY; not run here) --------------
MVP_BACKTEST_DESIGN = {
    "scope": "BTC only first",
    "tenor": "30-day tenor approximation (nearest listed ~30d expiry)",
    "structure": "delta-hedged short straddle (ATM) OR short-variance proxy; perp/spot "
                 "delta-hedge -- the short leg is short VOL, not short PRICE",
    "entry_schedule": "FIXED (e.g. monthly roll into the ~30d ATM straddle); no timing/selection",
    "hard_tail_gates": ("max-loss circuit breaker per cycle", "position-size cap (small gross)",
                        "vol-spike stop / de-risk on DVOL jump", "no naked exposure -- "
                        "delta-hedged + capped"),
    "cost_model": "fee + bid/ask spread on options + delta-hedge transaction/slippage on the "
                  "perp/spot leg (realistic, not droppable)",
    "no_optimization": True,
    "decisive_gates": ("net-positive after realistic cost", "survives the crash-stress windows "
                       "without ruin", "durable forward-OOS + ex-2021", "beats a cash/null "
                       "baseline risk-adjusted"),
    "is_design_only_not_run": True,
}

# --- feasibility ------------------------------------------------------------
FEASIBLE_WITH_FREE_DATA = False
FEASIBILITY_NOTE = (
    "NOT feasible with free public data (no multi-year per-strike history). FEASIBLE with PAID "
    "historical (backfill, recommended) OR FORWARD-only daily snapshots (no backfill). The data "
    "path is a human cost/time DECISION -- this contract does not buy or fetch anything.")

NEXT_HUMAN_GATE = (
    "HUMAN_DECISION_CHOOSE_PER_STRIKE_OPTIONS_DATA_PATH_PAID_OR_FORWARD_FOR_BTC_VRP")

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "fetches_data", "fetches_full_dataset", "buys_data",
    "makes_purchase", "writes_data", "runs_backtest", "runs_delta_hedge_sim",
    "runs_straddle_pnl", "evaluates_strategy", "runs_labels", "runs_replay",
    "optimizes_parameters", "mutates_data", "stages_data", "auto_commits", "auto_pushes",
    "commits_data_files", "uses_private_endpoints", "uses_signed_endpoints",
    "uses_account_endpoints", "uses_credentials", "sells_options", "activates_any_candidate",
    "promotes_any_candidate", "advances_c22", "reactivates_c23", "reactivates_c24",
    "reactivates_funding_selection", "modifies_official_ledger", "modifies_lifecycle",
    "modifies_lane_status", "connects_broker", "connects_exchange", "places_orders",
    "contains_order_logic", "paper_trading", "live_trading", "deploys_capital", "promotes_gate",
    "skips_any_gate", "advances_without_human_approval", "claims_profitability", "claims_edge",
    "claims_deployment_grade", "crosses_into_forbidden_gate",
)


def get_plan_label() -> str:
    return (
        "Per-strike options data phase PLAN (READ-ONLY, RESEARCH ONLY, PREP ONLY). A true "
        "delta-hedged BTC-first VRP backtest needs per-strike option chains + greeks + "
        "settlement, which the FREE Deribit public API does NOT provide historically (live + "
        "last-expiry only). Realistic path: PAID historical (Tardis.dev, covers ~2019+ incl. "
        "March-2020) or FORWARD-only daily snapshots (no backfill). BTC-first; ETH secondary. "
        "FETCHES/BUYS NOTHING; the data path is a human cost decision. Activates/promotes "
        "nothing; C22 unchanged; C23/C24 + funding selection not reactivated. NOT a deployment "
        "claim.")


def get_plan_next_action() -> str:
    return NEXT_HUMAN_GATE


def build_per_strike_options_phase_plan() -> dict[str, Any]:
    """Assemble the frozen per-strike options data-phase plan. Pure; no I/O; prep only; fetches
    and buys nothing."""
    blockers: list = []
    if FREE_PUBLIC_FEASIBILITY.split()[0] != "INSUFFICIENT":
        blockers.append("free_feasibility_not_assessed")
    if not any(p["recommended_primary"] for p in DATA_PATHS):
        blockers.append("no_recommended_path")

    record: dict[str, Any] = {
        "schema_version": PS_SCHEMA_VERSION, "mode": PS_MODE, "lane": PS_LANE,
        "record_id": RECORD_ID,
        "label": get_plan_label(),
        "is_plan_only": True,
        "blockers": blockers,
        "verdict": (VERDICT if not blockers else "PER_STRIKE_PHASE_PLAN_BLOCKED"),
        "no_existing_per_strike_infra": NO_EXISTING_INFRA,
        "probe_finding": PROBE_FINDING,
        "required_fields": list(REQUIRED_FIELDS),
        "free_public_feasibility": FREE_PUBLIC_FEASIBILITY,
        "free_data_sufficient": False,
        "data_paths": [dict(p) for p in DATA_PATHS],
        "recommended_path": RECOMMENDED_PATH,
        "paid_or_forward_required": True,
        "btc_first_scope": dict(BTC_FIRST_SCOPE),
        "proposed_date_range": dict(PROPOSED_DATE_RANGE),
        "proposed_data_dir": PROPOSED_DATA_DIR,
        "proposed_manifest_fields": list(PROPOSED_MANIFEST_FIELDS),
        "proposed_quality_report_fields": list(PROPOSED_QUALITY_REPORT_FIELDS),
        "data_will_be_gitignored": True,
        "crash_stress_windows": [dict(c) for c in CRASH_STRESS_WINDOWS],
        "mvp_backtest_design": _deep(MVP_BACKTEST_DESIGN),
        "is_feasible_with_free_data": FEASIBLE_WITH_FREE_DATA,
        "feasibility_note": FEASIBILITY_NOTE,
        "is_exploratory_only": True,
        "is_deployment_grade": False,
        # preservation
        "fetches_nothing_in_this_phase": True,
        "buys_nothing_in_this_phase": True,
        "activates_nothing": True,
        "c22_unchanged": True,
        "c23_c24_not_reactivated": True,
        "funding_selection_not_reactivated": True,
        "does_not_modify_official_ledger": True,
        "does_not_modify_lifecycle": True,
        "does_not_modify_lane_status": True,
        "human_review_required": True,
        "current_loop_stage": "per_strike_options_data_phase_plan",
        "next_required_action": NEXT_HUMAN_GATE,
        "data_procurement_gate_locked": True,
        "backtest_gate_locked": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_fetch": True, "no_full_dataset_fetch": True, "no_buy_data": True,
        "no_purchase": True, "no_write_data": True, "no_backtest": True,
        "no_delta_hedge_sim": True, "no_straddle_pnl": True, "no_strategy_eval": True,
        "no_labels": True, "no_replay": True, "no_optimization": True,
        "no_private_endpoints": True, "no_account_endpoints": True, "no_credentials": True,
        "no_sell_options": True, "no_activate_candidate": True, "no_promote_candidate": True,
        "no_advance_c22": True, "no_reactivate_c23": True, "no_reactivate_c24": True,
        "no_reactivate_funding_selection": True, "no_modify_official_ledger": True,
        "no_modify_lifecycle": True, "no_modify_lane_status": True, "no_commit_data": True,
        "no_stage": True, "no_commit": True, "no_push": True, "no_broker": True,
        "no_order_logic": True, "no_paper_trading": True, "no_live_trading": True,
        "no_gate_skip": True, "no_deployment_grade_claim": True, "no_profitability_claim": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return record


def _deep(d: dict) -> dict:
    out: dict = {}
    for k, v in d.items():
        out[k] = list(v) if isinstance(v, tuple) else (dict(v) if isinstance(v, dict) else v)
    return out


def validate_per_strike_options_phase_plan(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the record is research-only, plan-only; states
    free data is INSUFFICIENT and paid/forward is required (recommending PAID primary, FORWARD
    fallback); lists the required per-strike fields (incl. greeks delta/gamma/vega/theta + IV);
    is BTC-first; defines the MVP backtest design with hard tail gates + a cost model and
    no-optimization; lists crash windows (incl. March-2020 paid-only); fetches/buys NOTHING;
    activates/promotes nothing and leaves C22/C23/C24/funding-selection/ledger/lifecycle
    unchanged; and pins every capability flag False."""
    failures: list = []
    if record.get("mode") != PS_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_plan_only") is not True:
        failures.append("not_plan_only")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("verdict") != VERDICT:
        failures.append("verdict_wrong")

    # free insufficient + paid/forward required
    if record.get("free_data_sufficient") is not False:
        failures.append("free_must_be_insufficient")
    if record.get("is_feasible_with_free_data") is not False:
        failures.append("free_feasibility_must_be_false")
    if record.get("paid_or_forward_required") is not True:
        failures.append("must_require_paid_or_forward")
    paths = record.get("data_paths") or []
    if not any(p.get("path") == "paid_historical" and p.get("recommended_primary") is True
               for p in paths):
        failures.append("paid_historical_not_recommended_primary")
    if not any(p.get("path") == "forward_only_daily_snapshots" for p in paths):
        failures.append("forward_fallback_missing")

    # required fields incl. greeks + IV
    rf = record.get("required_fields") or []
    if "implied_vol(mark_iv)" not in rf:
        failures.append("iv_field_missing")
    for g in ("greeks.delta", "greeks.gamma", "greeks.vega", "greeks.theta"):
        if g not in rf:
            failures.append("greek_missing_%s" % g)
    if "strike" not in rf or "option_type(call/put)" not in rf:
        failures.append("strike_or_type_missing")

    # BTC-first + MVP design
    if (record.get("btc_first_scope") or {}).get("primary") != "BTC":
        failures.append("not_btc_first")
    mvp = record.get("mvp_backtest_design") or {}
    if mvp.get("scope") != "BTC only first":
        failures.append("mvp_not_btc_only")
    if mvp.get("no_optimization") is not True:
        failures.append("mvp_optimization_not_forbidden")
    if not mvp.get("hard_tail_gates"):
        failures.append("mvp_tail_gates_missing")
    if not mvp.get("cost_model"):
        failures.append("mvp_cost_model_missing")
    if mvp.get("is_design_only_not_run") is not True:
        failures.append("mvp_must_be_design_only")

    # crash windows incl March-2020 paid-only
    cw = record.get("crash_stress_windows") or []
    if len(cw) < 4:
        failures.append("crash_windows_incomplete")
    m20 = [c for c in cw if "2020-03" in str(c.get("window"))]
    if not m20 or "paid" not in str(m20[0].get("coverable")).lower():
        failures.append("march_2020_paid_only_not_flagged")

    # data layout
    if not str(record.get("proposed_data_dir", "")).startswith("data/deribit_options"):
        failures.append("data_dir_wrong")
    if record.get("data_will_be_gitignored") is not True:
        failures.append("data_must_be_gitignored")
    if record.get("is_deployment_grade") is not False:
        failures.append("must_not_claim_deployment_grade")

    # fetches/buys nothing + preservation
    for k in ("fetches_nothing_in_this_phase", "buys_nothing_in_this_phase", "activates_nothing",
              "c22_unchanged", "c23_c24_not_reactivated", "funding_selection_not_reactivated",
              "does_not_modify_official_ledger", "does_not_modify_lifecycle",
              "does_not_modify_lane_status", "data_procurement_gate_locked",
              "backtest_gate_locked"):
        if record.get(k) is not True:
            failures.append("preservation_off_%s" % k)
    if record.get("next_required_action") != NEXT_HUMAN_GATE:
        failures.append("next_gate_wrong")

    locks = record.get("scope_locks") or {}
    for key in ("no_fetch", "no_buy_data", "no_purchase", "no_write_data", "no_backtest",
                "no_delta_hedge_sim", "no_straddle_pnl", "no_strategy_eval", "no_optimization",
                "no_private_endpoints", "no_sell_options", "no_activate_candidate",
                "no_advance_c22", "no_reactivate_c23", "no_reactivate_c24",
                "no_reactivate_funding_selection", "no_modify_official_ledger", "no_commit_data",
                "no_commit", "no_push", "no_broker", "no_order_logic", "no_paper_trading",
                "no_live_trading"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
