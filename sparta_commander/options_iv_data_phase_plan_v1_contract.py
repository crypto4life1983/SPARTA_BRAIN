"""OPTIONS / IMPLIED-VOL DATA PHASE -- PLAN (PURE, RESEARCH ONLY, PREP ONLY).

Plans (does NOT execute) the options / implied-vol data phase required before the preferred V2
return-engine candidate (crypto_volatility_risk_premium_delta_hedged_short_vol_v1) can be
evaluated. Records the approved public source/endpoints, the required fields, the symbols/date
range, a PHASED feasibility split (free index-level vs paid per-strike), the crash-stress
windows for later validation, the data-quality risks, and the exact next human token.

It FETCHES NOTHING, evaluates NOTHING, writes NO data, activates/promotes NOTHING, does NOT
advance C22, does NOT reactivate C23/C24 or the funding selection, and modifies NO ledger/
lifecycle/lane-status. Every capability flag is pinned False. The actual frozen options/IV
fetch remains gated behind a SEPARATE human token.

PROBE FINDINGS (read-only, no data written): the Deribit public API is reachable --
  - get_volatility_index_data (DVOL implied-vol index) -> [ts,open,high,low,close]
  - get_instruments (BTC option chain) -> 890 live instruments w/ strike, option_type,
    expiration_timestamp, settlement_period, tick_size
  - ticker -> mark_iv, mark_price, greeks.delta, open_interest, underlying_price
all public, no API key, no signed/account/private endpoints.

HONEST FEASIBILITY SPLIT: the DVOL implied-vol INDEX history is FREE + sufficient for an
EXPLORATORY index-level VRP feasibility study (implied DVOL vs realized vol from our existing
spot OHLCV). A FULL delta-hedged short-straddle backtest needs PER-STRIKE historical option
chains + greeks + settlement, which the free public API does not provide deeply over years ->
likely PAID (Tardis/Amberdata/Kaiko) or forward-collected snapshots. NOTE: DVOL launched ~2021,
so March-2020 IV is NOT available via DVOL (a known gap).
"""
from __future__ import annotations

from typing import Any

OP_SCHEMA_VERSION = 1
OP_MODE = "RESEARCH_ONLY"
OP_LANE = "portfolio_sleeve_evaluation"

RECORD_ID = "OPTIONS_IV_DATA_PHASE_PLAN_V1"
VERDICT = "OPTIONS_IV_DATA_PHASE_PLANNED__PHASE1_FREE_FEASIBLE__PHASE2_LIKELY_PAID__FETCH_GATED"

# --- approved public source (Deribit public market data; no auth) -----------
DVOL_ENDPOINT = "https://www.deribit.com/api/v2/public/get_volatility_index_data"
INSTRUMENTS_ENDPOINT = "https://www.deribit.com/api/v2/public/get_instruments"
TICKER_ENDPOINT = "https://www.deribit.com/api/v2/public/ticker"
PUBLIC_ENDPOINTS = (DVOL_ENDPOINT, INSTRUMENTS_ENDPOINT, TICKER_ENDPOINT)
SOURCE_DESCRIPTION = (
    "Deribit public API (api/v2/public/...). Public market data only: NO API key, NO signed "
    "endpoints, NO /private/ (trading/account/order) endpoints. A broad/options fetch needs a "
    "NEW bounded fetcher restricted to the /public/ DVOL + instruments + ticker endpoints.")
NO_EXISTING_INFRA = True   # repo has no options/IV/Deribit/DVOL fetcher today

# --- required fields --------------------------------------------------------
REQUIRED_FIELDS_INDEX_LEVEL = (   # Phase 1 (free): DVOL implied-vol index
    "timestamp", "dvol_open", "dvol_high", "dvol_low", "dvol_close",
    "+ realized_vol (computed from existing frozen spot OHLCV)",
)
REQUIRED_FIELDS_FULL_VRP = (      # Phase 2 (paid/heavier): per-strike option chain history
    "instrument_name", "strike", "option_type(call/put)", "expiration_timestamp",
    "implied_vol(mark_iv)", "mark_price/settlement_price", "underlying/index_price",
    "greeks.delta", "greeks.gamma", "greeks.vega", "greeks.theta",
    "open_interest", "volume", "settlement_period", "tick_size",
)

# --- symbols / date range ---------------------------------------------------
PROPOSED_SYMBOLS = ("BTC", "ETH")   # the only liquid crypto options
PROPOSED_DATE_RANGE = {"start": "2021-03-24", "end": "2026-06-21",
                       "note": "DVOL launched ~2021 (BTC ~Mar-2021; ETH later); pre-2021 IV "
                               "not available via DVOL"}

# --- phased feasibility -----------------------------------------------------
PHASE_1 = {
    "name": "index_level_vrp_feasibility",
    "source": "Deribit public DVOL (get_volatility_index_data) + existing frozen spot OHLCV",
    "free": True, "feasible": True,
    "what": "measure the implied(DVOL) - realized vol SPREAD over time; is the VRP positive, "
            "durable ex-2021, and present in the recent regime? a cheap go/no-go BEFORE any "
            "paid data",
    "limitation": "DVOL is a 30-day constant-maturity index, a PROXY -- not the tradeable "
                  "delta-hedged straddle P&L",
}
PHASE_2 = {
    "name": "full_delta_hedged_vrp_backtest",
    "source": "per-strike historical option chains + greeks + settlement (Deribit deep history "
              "is limited via free API -> likely PAID: Tardis.dev / Amberdata / Kaiko, OR "
              "forward-collected daily snapshots)",
    "free": False, "feasible": "only_with_paid_or_forward_collected_data",
    "what": "true delta-hedged short-straddle/strangle replay with realistic option marks, "
            "greeks, settlement, and execution",
}
PUBLIC_DATA_SUFFICIENCY = (
    "SUFFICIENT for Phase 1 (DVOL index-level VRP). NOT sufficient for Phase 2 (full "
    "delta-hedged backtest) -> paid or forward-collected per-strike data required.")

# --- proposed frozen layout (gitignored at fetch time) ----------------------
PROPOSED_DATA_DIR = "data/deribit_iv_universe/"
PROPOSED_CSV_FIELDS_PHASE1 = ("date", "dvol_open", "dvol_high", "dvol_low", "dvol_close",
                              "currency")
PROPOSED_MANIFEST_FIELDS = ("source", "endpoints", "currencies", "date_range", "per_currency_rows",
                            "first_last_timestamp", "resolution", "sha256", "dvol_launch_note")
PROPOSED_QUALITY_REPORT_FIELDS = ("currencies_included", "short_histories", "missing_days",
                                  "dvol_prehistory_gap", "feasible_for_index_level_vrp")

# --- data-quality risks -----------------------------------------------------
DATA_QUALITY_RISKS = (
    "DVOL PRE-HISTORY GAP: DVOL launched ~2021, so March-2020 (COVID) implied vol is NOT "
    "available via DVOL -- that crash window needs reconstructed IV from option chains (paid).",
    "INDEX-vs-TRADEABLE: DVOL is a 30-day constant-maturity implied-vol INDEX, a PROXY for the "
    "premium -- it is NOT the realizable delta-hedged short-straddle P&L; Phase 1 is feasibility, "
    "not a tradeable backtest.",
    "PAID DEPTH: full per-strike historical chains + greeks + settlement are not deeply free via "
    "the public API -> Phase 2 likely needs a paid vendor or forward-collected snapshots.",
    "LIQUIDITY: crypto options liquidity is concentrated in BTC/ETH and thins for far strikes / "
    "early years -> marks unreliable in tails / early data.",
    "SURVIVORSHIP: low concern for BTC/ETH DVOL (majors), higher for per-strike instruments that "
    "expire/delist; record true first/last and do not forward-fill.",
)

# --- crash-stress windows for FUTURE validation -----------------------------
CRASH_STRESS_WINDOWS = (
    {"window": "2020-03 COVID crash", "in_dvol": False,
     "note": "pre-DVOL; needs reconstructed IV (paid) -- a known gap"},
    {"window": "2021-05 China-ban / leverage flush", "in_dvol": True},
    {"window": "2022-06 3AC/Luna contagion", "in_dvol": True},
    {"window": "2022-11 FTX collapse", "in_dvol": True},
    {"window": "2024-08 yen-carry unwind", "in_dvol": True},
    {"window": "any later 2025-2026 drawdowns present in the data", "in_dvol": True},
)

FEASIBLE = True
FEASIBILITY_NOTE = (
    "FEASIBLE in two phases: Phase 1 (DVOL index-level VRP) is fully feasible now with public "
    "Deribit data + existing spot; Phase 2 (full delta-hedged backtest) needs paid/forward "
    "per-strike data. Recommend Phase 1 FIRST as a cheap go/no-go before any paid commitment. A "
    "NEW bounded /public/-only Deribit fetcher + safety tests is required (no existing infra).")

NEXT_HUMAN_GATE = (
    "HUMAN_APPROVED_CREATE_BOUNDED_DERIBIT_DVOL_IV_INDEX_FETCHER_AND_ASSEMBLE_FROZEN_DATA_ONLY")

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "fetches_data", "fetches_full_dataset", "writes_data",
    "reads_real_data_for_eval", "runs_labels", "runs_replay", "runs_backtest",
    "optimizes_parameters", "evaluates_strategy", "mutates_data", "stages_data", "auto_commits",
    "auto_pushes", "commits_data_files", "uses_private_endpoints", "uses_signed_endpoints",
    "uses_account_endpoints", "uses_credentials", "sells_options", "activates_any_candidate",
    "promotes_any_candidate", "advances_c22", "reactivates_c23", "reactivates_c24",
    "reactivates_funding_selection", "modifies_official_ledger", "modifies_lifecycle",
    "modifies_lane_status", "modifies_scheduler", "connects_broker", "connects_exchange",
    "places_orders", "contains_order_logic", "paper_trading", "live_trading", "deploys_capital",
    "promotes_gate", "skips_any_gate", "advances_without_human_approval", "claims_profitability",
    "claims_edge", "claims_deployment_grade", "crosses_into_forbidden_gate",
)


def get_plan_label() -> str:
    return (
        "Options/implied-vol data phase PLAN (READ-ONLY, RESEARCH ONLY, PREP ONLY). Source: "
        "Deribit public DVOL + option-chain + ticker endpoints (no auth). Phased: Phase 1 (FREE) "
        "= DVOL index-level VRP feasibility (implied vs realized vol) -- feasible now; Phase 2 "
        "(PAID/forward) = full delta-hedged per-strike backtest. Symbols BTC/ETH; range "
        "~2021-2026 (DVOL launch; March-2020 gap). FETCHES NOTHING; actual fetch gated on a "
        "SEPARATE token. Activates/promotes nothing; C22 unchanged; C23/C24 + funding selection "
        "not reactivated.")


def get_plan_next_action() -> str:
    return NEXT_HUMAN_GATE


def build_options_iv_phase_plan() -> dict[str, Any]:
    """Assemble the frozen options/IV data-phase plan. Pure; no I/O; prep only; fetches nothing."""
    blockers: list = []
    if not all(e.startswith("https://www.deribit.com/api/v2/public/") for e in PUBLIC_ENDPOINTS):
        blockers.append("non_public_endpoint")
    if set(PROPOSED_SYMBOLS) != {"BTC", "ETH"}:
        blockers.append("symbols_not_btc_eth")

    record: dict[str, Any] = {
        "schema_version": OP_SCHEMA_VERSION, "mode": OP_MODE, "lane": OP_LANE,
        "record_id": RECORD_ID,
        "label": get_plan_label(),
        "is_plan_only": True,
        "blockers": blockers,
        "verdict": (VERDICT if not blockers else "OPTIONS_IV_PHASE_PLAN_BLOCKED"),
        "no_existing_options_iv_infra": NO_EXISTING_INFRA,
        # source
        "dvol_endpoint": DVOL_ENDPOINT,
        "instruments_endpoint": INSTRUMENTS_ENDPOINT,
        "ticker_endpoint": TICKER_ENDPOINT,
        "public_endpoints": list(PUBLIC_ENDPOINTS),
        "source_description": SOURCE_DESCRIPTION,
        "uses_public_endpoints_only": True,
        "must_not_use_private_endpoints": True,
        "requires_new_bounded_fetcher": True,
        # required fields
        "required_fields_index_level": list(REQUIRED_FIELDS_INDEX_LEVEL),
        "required_fields_full_vrp": list(REQUIRED_FIELDS_FULL_VRP),
        # symbols / range
        "proposed_symbols": list(PROPOSED_SYMBOLS),
        "proposed_date_range": dict(PROPOSED_DATE_RANGE),
        # phased feasibility
        "phase_1": dict(PHASE_1),
        "phase_2": dict(PHASE_2),
        "public_data_sufficiency": PUBLIC_DATA_SUFFICIENCY,
        "paid_data_likely_for_phase_2": True,
        # layout
        "proposed_data_dir": PROPOSED_DATA_DIR,
        "proposed_csv_fields_phase1": list(PROPOSED_CSV_FIELDS_PHASE1),
        "proposed_manifest_fields": list(PROPOSED_MANIFEST_FIELDS),
        "proposed_quality_report_fields": list(PROPOSED_QUALITY_REPORT_FIELDS),
        "data_will_be_gitignored": True,
        "no_forward_fill": True,
        # risks / crash windows / feasibility
        "data_quality_risks": list(DATA_QUALITY_RISKS),
        "crash_stress_windows": [dict(c) for c in CRASH_STRESS_WINDOWS],
        "is_feasible": FEASIBLE,
        "feasibility_note": FEASIBILITY_NOTE,
        "is_exploratory_only": True,
        "is_deployment_grade": False,
        # preservation
        "fetches_nothing_in_this_phase": True,
        "activates_nothing": True,
        "c22_unchanged": True,
        "c23_c24_not_reactivated": True,
        "funding_selection_not_reactivated": True,
        "does_not_modify_official_ledger": True,
        "does_not_modify_lifecycle": True,
        "does_not_modify_lane_status": True,
        "human_review_required": True,
        "current_loop_stage": "options_iv_data_phase_plan",
        "next_required_action": NEXT_HUMAN_GATE,
        "full_fetch_gate_locked": True,
        "short_vol_strategy_gate_locked": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_fetch": True, "no_full_dataset_fetch": True, "no_write_data": True,
        "no_strategy_eval": True, "no_labels": True, "no_replay": True, "no_optimization": True,
        "no_private_endpoints": True, "no_signed_endpoints": True, "no_account_endpoints": True,
        "no_credentials": True, "no_sell_options": True, "no_activate_candidate": True,
        "no_promote_candidate": True, "no_advance_c22": True, "no_reactivate_c23": True,
        "no_reactivate_c24": True, "no_reactivate_funding_selection": True,
        "no_modify_official_ledger": True, "no_modify_lifecycle": True,
        "no_modify_lane_status": True, "no_commit_data": True, "no_stage": True,
        "no_commit": True, "no_push": True, "no_broker": True, "no_order_logic": True,
        "no_paper_trading": True, "no_live_trading": True, "no_gate_skip": True,
        "no_deployment_grade_claim": True, "no_profitability_claim": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_options_iv_phase_plan(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the record is research-only, plan-only; names the
    PUBLIC Deribit endpoints (never /private/) and requires a NEW bounded fetcher; proposes
    BTC/ETH + the phased free(Phase1)/paid(Phase2) feasibility; specifies required fields, frozen
    layout (gitignored, no forward-fill), data-quality risks (incl. DVOL pre-history gap +
    index-vs-tradeable), and the crash-stress windows (incl. the March-2020 DVOL gap); fetches
    NOTHING; activates/promotes nothing and leaves C22/C23/C24/funding-selection/ledger/lifecycle
    unchanged; and pins every capability flag False."""
    failures: list = []
    if record.get("mode") != OP_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_plan_only") is not True:
        failures.append("not_plan_only")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("verdict") != VERDICT:
        failures.append("verdict_wrong")

    # public endpoints only, no private
    for e in (record.get("public_endpoints") or []):
        if not str(e).startswith("https://www.deribit.com/api/v2/public/"):
            failures.append("non_public_endpoint:%s" % e)
        if "/private/" in str(e):
            failures.append("private_endpoint_present")
    if record.get("uses_public_endpoints_only") is not True:
        failures.append("must_be_public_only")
    if record.get("must_not_use_private_endpoints") is not True:
        failures.append("must_forbid_private")
    if record.get("requires_new_bounded_fetcher") is not True:
        failures.append("must_require_new_fetcher")

    # symbols + phased feasibility
    if set(record.get("proposed_symbols") or []) != {"BTC", "ETH"}:
        failures.append("symbols_not_btc_eth")
    p1 = record.get("phase_1") or {}
    p2 = record.get("phase_2") or {}
    if not (p1.get("free") is True and p1.get("feasible") is True):
        failures.append("phase1_not_free_feasible")
    if p2.get("free") is not False:
        failures.append("phase2_must_not_be_free")
    if record.get("paid_data_likely_for_phase_2") is not True:
        failures.append("must_flag_paid_phase2")

    # required fields
    if "implied_vol(mark_iv)" not in (record.get("required_fields_full_vrp") or []):
        failures.append("required_iv_field_missing")
    if not any("delta" in f for f in (record.get("required_fields_full_vrp") or [])):
        failures.append("required_delta_field_missing")

    # layout + risks + crash windows
    if not str(record.get("proposed_data_dir", "")).startswith("data/deribit_iv"):
        failures.append("data_dir_wrong")
    if record.get("data_will_be_gitignored") is not True:
        failures.append("data_must_be_gitignored")
    risks = " ".join(record.get("data_quality_risks") or []).upper()
    if "DVOL" not in risks or "PROXY" not in risks:
        failures.append("required_risk_missing")
    cw = record.get("crash_stress_windows") or []
    if len(cw) < 4:
        failures.append("crash_windows_incomplete")
    march2020 = [c for c in cw if "2020-03" in str(c.get("window"))]
    if not march2020 or march2020[0].get("in_dvol") is not False:
        failures.append("march_2020_dvol_gap_not_flagged")
    if not any("FTX" in str(c.get("window")) or "2022-11" in str(c.get("window")) for c in cw):
        failures.append("ftx_window_missing")

    if record.get("is_feasible") is not True:
        failures.append("must_state_feasible")
    if record.get("is_deployment_grade") is not False:
        failures.append("must_not_claim_deployment_grade")

    # fetches nothing + preservation
    for k in ("fetches_nothing_in_this_phase", "activates_nothing", "c22_unchanged",
              "c23_c24_not_reactivated", "funding_selection_not_reactivated",
              "does_not_modify_official_ledger", "does_not_modify_lifecycle",
              "does_not_modify_lane_status", "full_fetch_gate_locked"):
        if record.get(k) is not True:
            failures.append("preservation_off_%s" % k)
    if record.get("next_required_action") != NEXT_HUMAN_GATE:
        failures.append("next_gate_wrong")

    locks = record.get("scope_locks") or {}
    for key in ("no_fetch", "no_full_dataset_fetch", "no_write_data", "no_strategy_eval",
                "no_replay", "no_optimization", "no_private_endpoints", "no_account_endpoints",
                "no_sell_options", "no_activate_candidate", "no_advance_c22", "no_reactivate_c23",
                "no_reactivate_c24", "no_reactivate_funding_selection",
                "no_modify_official_ledger", "no_commit_data", "no_commit", "no_push",
                "no_broker", "no_order_logic", "no_paper_trading", "no_live_trading"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
