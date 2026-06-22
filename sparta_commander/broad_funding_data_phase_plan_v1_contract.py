"""BROAD MULTI-ASSET FUNDING DATA PHASE -- PLAN (PURE, RESEARCH ONLY, PREP ONLY).

Plans (does NOT execute) the broad multi-asset funding-rate data phase required before the
recommended next return-engine candidate (cross_sectional_crypto_funding_carry_market_neutral_v1)
can be evaluated. It records the approved public source/endpoint, the bounded funding symbol
allowlist (the perp-available subset of the 42-symbol broad OHLCV universe), the excluded
symbols + reasons, the proposed frozen directory / manifest / quality-report format, the date
range, the data-quality risks, and the exact next human token that would authorize the actual
fetch.

It FETCHES NOTHING, evaluates NOTHING, writes NO data, activates/promotes NOTHING, does NOT
advance C22, does NOT reactivate C23/C24, and modifies NO ledger/lifecycle/lane-status. Every
capability flag is pinned False with a full scope_locks set. The actual frozen-funding fetch
remains gated behind a SEPARATE human token.

PROBE FINDINGS (read-only, no data written): the approved funding source
https://fapi.binance.com/fapi/v1/fundingRate is reachable and returns
{symbol, fundingTime, fundingRate, markPrice}; 40 of the 42 broad-OHLCV symbols have a
currently-TRADING Binance USD-M USDT perpetual; EOSUSDT and MKRUSDT have NO current trading
perp (spot+perp delisted mid-2025) and are excluded.
"""
from __future__ import annotations

from typing import Any

FP_SCHEMA_VERSION = 1
FP_MODE = "RESEARCH_ONLY"
FP_LANE = "portfolio_sleeve_evaluation"

RECORD_ID = "BROAD_FUNDING_DATA_PHASE_PLAN_V1"
VERDICT = "BROAD_FUNDING_DATA_PHASE_PLANNED_AND_FEASIBLE__FETCH_GATED_ON_SEPARATE_TOKEN"

# --- approved public source (already used by SPARTA's 3-symbol carry fetcher) ----
FUNDING_ENDPOINT = "https://fapi.binance.com/fapi/v1/fundingRate"
PERP_EXCHANGE_INFO_ENDPOINT = "https://fapi.binance.com/fapi/v1/exchangeInfo"
EXISTING_FUNDING_TOOL = "tools/crypto_basis_funding_public_fetch_once.py"  # capped to 3 symbols
SOURCE_DESCRIPTION = (
    "Binance USD-M perpetual funding-rate history (public market data; no API key, no signed "
    "endpoints, no account/order endpoints). Same endpoint the committed 3-symbol carry fetcher "
    "uses; a broad-universe fetch needs a NEW bounded tool (the 3-symbol allowlist must not be "
    "widened).")

# --- proposed bounded funding allowlist (40 perp-available; aligned to the OHLCV universe) ----
PROPOSED_FUNDING_ALLOWLIST = (
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT", "TRXUSDT",
    "LINKUSDT", "AVAXUSDT", "DOTUSDT", "LTCUSDT", "BCHUSDT", "UNIUSDT", "ATOMUSDT", "ETCUSDT",
    "XLMUSDT", "ICPUSDT", "AAVEUSDT", "NEARUSDT", "FILUSDT", "ALGOUSDT", "VETUSDT", "XTZUSDT",
    "THETAUSDT", "HBARUSDT", "EGLDUSDT", "ZECUSDT", "MANAUSDT", "SANDUSDT", "CHZUSDT", "ENJUSDT",
    "ZILUSDT", "KAVAUSDT", "RUNEUSDT", "GRTUSDT", "CRVUSDT", "SNXUSDT", "COMPUSDT", "YFIUSDT",
)
EXCLUDED_SYMBOLS = {
    "EOSUSDT": "no current TRADING Binance USD-M USDT perp (spot+perp delisted ~2025-05-26)",
    "MKRUSDT": "no current TRADING Binance USD-M USDT perp (delisted ~2025-09; MKR->SKY era)",
}
OHLCV_UNIVERSE_SIZE = 42
PERP_AVAILABLE_COUNT = 40

# --- proposed frozen layout (gitignored at fetch time, like the OHLCV universe) ----
PROPOSED_DATA_DIR = "data/broad_crypto_funding_universe/"
PROPOSED_RAW_SUBDIR = "data/broad_crypto_funding_universe/raw/"
PROPOSED_CSV_FIELDS = ("datetime", "funding_time_ms", "symbol", "funding_rate", "mark_price")
PROPOSED_MANIFEST_FIELDS = (
    "dataset", "source", "endpoint", "interval_note", "assembled_utc", "requested_date_range",
    "allowlist", "included", "excluded", "per_symbol_rows", "per_symbol_first_last_funding_time",
    "per_symbol_funding_interval_hours", "per_symbol_sha256", "survivorship_note",
)
PROPOSED_QUALITY_REPORT_FIELDS = (
    "included_count", "excluded_count", "exclusions", "short_histories",
    "missing_funding_interval_summary", "non_8h_funding_interval_symbols",
    "total_missing_intervals",
)
PROPOSED_DATE_RANGE = {"start": "2021-01-01", "end": "2026-06-21"}  # aligned with OHLCV universe

# --- data-quality risks -----------------------------------------------------
DATA_QUALITY_RISKS = (
    "SURVIVORSHIP BIAS: Binance-public returns only currently-listed perps; delisted perps "
    "(EOS, MKR, and any never seen) are absent -- exploratory only, NOT deployment-grade.",
    "NON-UNIFORM FUNDING INTERVAL: Binance funding is NOT always 8h -- several symbols switched "
    "to 4h (and some to 1h) at various dates. The fetcher MUST record each symbol's actual "
    "funding cadence and annualize per-interval, NOT assume 3x/day, or the carry will be "
    "mis-scaled.",
    "PERP LISTING-DATE GAPS: perps for newer alts (e.g. ICP) and some others listed AFTER "
    "2021-01-01, so funding history is shorter -- record true first funding time, do not "
    "forward-fill.",
    "MARK-PRICE / BACKFILL: early mark_price fields can be 0 or sparse; treat mark_price as "
    "secondary (funding_rate is the primary field).",
    "SPOT-VS-PERP ALIGNMENT: a cross-sectional carry needs spot AND perp AND funding aligned "
    "per asset; the OHLCV universe is SPOT -- the future fetcher must also confirm perp klines "
    "or rely on the funding+mark series for the neutral construction.",
    "FUNDING-RATE OUTLIERS: deleveraging events produce extreme funding prints; keep raw, flag "
    "outliers in QA, never clip silently.",
)

FEASIBLE = True
FEASIBILITY_NOTE = (
    "FEASIBLE: the public funding endpoint is reachable and 40/42 symbols have a trading USD-M "
    "perp; a bounded broad-funding fetcher (mirroring the committed broad-OHLCV fetcher's safety "
    "architecture, with the funding endpoint + the 40-symbol allowlist + per-symbol funding-"
    "cadence capture) can assemble a frozen, SHA-pinned dataset. The 3-symbol carry fetcher must "
    "NOT be widened; a NEW dedicated tool + safety tests are required.")

NEXT_HUMAN_GATE = (
    "HUMAN_APPROVED_CREATE_BOUNDED_BROAD_FUNDING_FETCHER_AND_ASSEMBLE_FROZEN_DATA_ONLY")

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "fetches_data", "fetches_full_dataset", "writes_data",
    "reads_real_data_for_eval", "runs_labels", "runs_replay", "runs_backtest",
    "optimizes_parameters", "evaluates_strategy", "mutates_data", "stages_data", "auto_commits",
    "auto_pushes", "commits_data_files", "widens_existing_3_symbol_allowlist",
    "activates_any_candidate", "promotes_any_candidate", "advances_c22", "reactivates_c23",
    "reactivates_c24", "modifies_official_ledger", "modifies_lifecycle", "modifies_lane_status",
    "modifies_scheduler", "sends_notifications", "uses_credentials", "uses_signed_endpoints",
    "uses_account_endpoints", "connects_broker", "connects_exchange", "places_orders",
    "contains_order_logic", "paper_trading", "live_trading", "deploys_capital", "promotes_gate",
    "skips_any_gate", "advances_without_human_approval", "claims_profitability", "claims_edge",
    "claims_survivorship_free", "crosses_into_forbidden_gate",
)


def get_plan_label() -> str:
    return (
        "Broad multi-asset funding data phase PLAN (READ-ONLY, RESEARCH ONLY, PREP ONLY). Source: "
        "Binance public USD-M funding endpoint. Proposes a bounded 40-symbol funding allowlist "
        "(perp-available subset of the 42 broad-OHLCV symbols; EOS/MKR excluded -- delisted "
        "perps), a frozen gitignored directory + manifest + quality report + safety tests, and "
        "the date range 2021-01-01..2026-06-21. FETCHES NOTHING; the actual frozen-funding fetch "
        "is gated on a SEPARATE human token. Survivorship-biased exploratory data; NOT a "
        "deployment claim. Activates/promotes nothing; C22 unchanged; C23/C24 not reactivated.")


def get_plan_next_action() -> str:
    return NEXT_HUMAN_GATE


def build_funding_phase_plan() -> dict[str, Any]:
    """Assemble the frozen broad-funding-data-phase plan. Pure; no I/O; prep only; fetches
    nothing. Gated on the allowlist being the perp-available subset with the delisted pair
    excluded."""
    blockers: list = []
    if len(PROPOSED_FUNDING_ALLOWLIST) != PERP_AVAILABLE_COUNT:
        blockers.append("allowlist_size_mismatch")
    if set(PROPOSED_FUNDING_ALLOWLIST) & set(EXCLUDED_SYMBOLS):
        blockers.append("excluded_symbol_in_allowlist")
    if len(PROPOSED_FUNDING_ALLOWLIST) + len(EXCLUDED_SYMBOLS) != OHLCV_UNIVERSE_SIZE:
        blockers.append("allowlist_plus_excluded_not_42")

    record: dict[str, Any] = {
        "schema_version": FP_SCHEMA_VERSION, "mode": FP_MODE, "lane": FP_LANE,
        "record_id": RECORD_ID,
        "label": get_plan_label(),
        "is_plan_only": True,
        "blockers": blockers,
        "verdict": (VERDICT if not blockers else "FUNDING_PHASE_PLAN_BLOCKED"),
        # source
        "funding_endpoint": FUNDING_ENDPOINT,
        "perp_exchange_info_endpoint": PERP_EXCHANGE_INFO_ENDPOINT,
        "existing_funding_tool": EXISTING_FUNDING_TOOL,
        "source_description": SOURCE_DESCRIPTION,
        "uses_public_endpoint_only": True,
        "must_not_widen_3_symbol_carry_fetcher": True,
        "requires_new_bounded_fetcher": True,
        # allowlist
        "proposed_funding_allowlist": list(PROPOSED_FUNDING_ALLOWLIST),
        "proposed_allowlist_size": len(PROPOSED_FUNDING_ALLOWLIST),
        "excluded_symbols": dict(EXCLUDED_SYMBOLS),
        "ohlcv_universe_size": OHLCV_UNIVERSE_SIZE,
        "perp_available_count": PERP_AVAILABLE_COUNT,
        "aligned_to_broad_ohlcv_universe": True,
        # layout
        "proposed_data_dir": PROPOSED_DATA_DIR,
        "proposed_raw_subdir": PROPOSED_RAW_SUBDIR,
        "proposed_csv_fields": list(PROPOSED_CSV_FIELDS),
        "proposed_manifest_fields": list(PROPOSED_MANIFEST_FIELDS),
        "proposed_quality_report_fields": list(PROPOSED_QUALITY_REPORT_FIELDS),
        "proposed_date_range": dict(PROPOSED_DATE_RANGE),
        "data_will_be_gitignored": True,
        "captures_per_symbol_funding_interval": True,   # the non-8h risk mitigation
        "no_forward_fill": True,
        # risks + feasibility
        "data_quality_risks": list(DATA_QUALITY_RISKS),
        "is_feasible": FEASIBLE,
        "feasibility_note": FEASIBILITY_NOTE,
        "is_exploratory_only": True,
        "is_survivorship_biased": True,
        "is_survivorship_free": False,
        "is_deployment_grade": False,
        # preservation
        "fetches_nothing_in_this_phase": True,
        "activates_nothing": True,
        "c22_unchanged": True,
        "c23_c24_not_reactivated": True,
        "does_not_modify_official_ledger": True,
        "does_not_modify_lifecycle": True,
        "does_not_modify_lane_status": True,
        "human_review_required": True,
        "current_loop_stage": "broad_funding_data_phase_plan",
        "next_required_action": NEXT_HUMAN_GATE,
        "full_fetch_gate_locked": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_fetch": True, "no_full_dataset_fetch": True, "no_write_data": True,
        "no_strategy_eval": True, "no_labels": True, "no_replay": True, "no_optimization": True,
        "no_widen_3_symbol_allowlist": True, "no_signed_endpoints": True,
        "no_account_endpoints": True, "no_credentials": True, "no_activate_candidate": True,
        "no_promote_candidate": True, "no_advance_c22": True, "no_reactivate_c23": True,
        "no_reactivate_c24": True, "no_modify_official_ledger": True, "no_modify_lifecycle": True,
        "no_modify_lane_status": True, "no_commit_data": True, "no_stage": True,
        "no_commit": True, "no_push": True, "no_broker": True, "no_order_logic": True,
        "no_paper_trading": True, "no_live_trading": True, "no_gate_skip": True,
        "no_survivorship_free_claim": True, "no_profitability_claim": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_funding_phase_plan(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the record is research-only, plan-only; names the
    PUBLIC funding endpoint and requires a NEW bounded fetcher (never widening the 3-symbol
    carry fetcher); proposes the 40-symbol perp-available allowlist (EOS/MKR excluded) aligned
    to the 42-symbol OHLCV universe; specifies the frozen dir / manifest / quality-report / CSV
    fields with per-symbol funding-interval capture and no forward-fill; discloses the survivor-
    ship + non-8h-interval risks; fetches NOTHING; activates/promotes nothing and leaves
    C22/C23/C24/ledger/lifecycle/lane-status unchanged; and pins every capability flag False."""
    failures: list = []
    if record.get("mode") != FP_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_plan_only") is not True:
        failures.append("not_plan_only")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("verdict") != VERDICT:
        failures.append("verdict_wrong")

    # source
    if record.get("funding_endpoint") != FUNDING_ENDPOINT:
        failures.append("funding_endpoint_tampered")
    if "fapi.binance.com" not in str(record.get("funding_endpoint")):
        failures.append("not_public_binance_funding")
    if record.get("uses_public_endpoint_only") is not True:
        failures.append("must_be_public_only")
    if record.get("must_not_widen_3_symbol_carry_fetcher") is not True:
        failures.append("must_not_widen_existing_fetcher")
    if record.get("requires_new_bounded_fetcher") is not True:
        failures.append("must_require_new_fetcher")

    # allowlist: 40 perp-available, EOS/MKR excluded, aligned to 42
    al = record.get("proposed_funding_allowlist") or []
    if len(al) != PERP_AVAILABLE_COUNT:
        failures.append("allowlist_not_40")
    ex = record.get("excluded_symbols") or {}
    if set(ex) != {"EOSUSDT", "MKRUSDT"}:
        failures.append("excluded_set_wrong")
    if set(al) & set(ex):
        failures.append("excluded_in_allowlist")
    if len(al) + len(ex) != OHLCV_UNIVERSE_SIZE:
        failures.append("allowlist_plus_excluded_not_42")
    if record.get("aligned_to_broad_ohlcv_universe") is not True:
        failures.append("not_aligned_to_ohlcv")

    # layout + interval capture + no forward fill
    for k in ("proposed_data_dir", "proposed_raw_subdir"):
        if not str(record.get(k, "")).startswith("data/broad_crypto_funding"):
            failures.append("layout_dir_wrong_%s" % k)
    if "funding_rate" not in (record.get("proposed_csv_fields") or []):
        failures.append("csv_missing_funding_rate")
    if record.get("captures_per_symbol_funding_interval") is not True:
        failures.append("must_capture_funding_interval")
    if record.get("no_forward_fill") is not True:
        failures.append("must_not_forward_fill")
    if record.get("data_will_be_gitignored") is not True:
        failures.append("data_must_be_gitignored")

    # risks disclosed (incl. the non-8h interval + survivorship)
    risks = " ".join(record.get("data_quality_risks") or [])
    if len(record.get("data_quality_risks") or []) < 4:
        failures.append("risks_incomplete")
    if "SURVIVORSHIP" not in risks.upper():
        failures.append("survivorship_risk_missing")
    if "8H" not in risks.upper() and "INTERVAL" not in risks.upper():
        failures.append("funding_interval_risk_missing")

    # feasibility + disclosures
    if record.get("is_feasible") is not True:
        failures.append("must_state_feasible")
    if record.get("is_survivorship_free") is not False:
        failures.append("must_not_claim_survivorship_free")
    if record.get("is_deployment_grade") is not False:
        failures.append("must_not_claim_deployment_grade")

    # fetches nothing + preservation
    for k in ("fetches_nothing_in_this_phase", "activates_nothing", "c22_unchanged",
              "c23_c24_not_reactivated", "does_not_modify_official_ledger",
              "does_not_modify_lifecycle", "does_not_modify_lane_status",
              "full_fetch_gate_locked"):
        if record.get(k) is not True:
            failures.append("preservation_off_%s" % k)
    if record.get("next_required_action") != NEXT_HUMAN_GATE:
        failures.append("next_gate_wrong")

    locks = record.get("scope_locks") or {}
    for key in ("no_fetch", "no_full_dataset_fetch", "no_write_data", "no_strategy_eval",
                "no_labels", "no_replay", "no_optimization", "no_widen_3_symbol_allowlist",
                "no_signed_endpoints", "no_account_endpoints", "no_activate_candidate",
                "no_advance_c22", "no_reactivate_c23", "no_reactivate_c24",
                "no_modify_official_ledger", "no_commit_data", "no_commit", "no_push",
                "no_broker", "no_order_logic", "no_paper_trading", "no_live_trading",
                "no_survivorship_free_claim"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
