"""Candidate #22 -- SIGNUM official Trend Radar SOURCE DISCOVERY FINDINGS
-- PURE, READ-ONLY, RESEARCH ONLY, DISCOVERY-ONLY.

Records the read-only findings of investigating how to obtain the daily SIGNUM Trend Radar GC
payload for C22. It is a FINDINGS record: it implements NO live fetch, connects to NO SIGNUM
account/MCP, calls NO trading/write tool, and stores NO credentials. C22 stays
HOLD_FOR_MORE_FROZEN_DATA_WINDOWS with replay locked.

Findings (June 2026):
  * MANUAL JSON EXPORT: no manual download/export button was found in SIGNUM. SIGNUM exposes
    the Trend Radar via Model Context Protocol (MCP), not a file download.
  * OFFICIAL READ-ONLY EXPORT: YES -- `get-trendradar-daily` is an official SIGNUM MCP tool
    that READS the Trend Radar (read-only, permission-based). It is NOT configured in THIS
    SPARTA environment (only the `exa` MCP server is configured here).
  * CRITICAL SAFETY: the SIGNUM MCP, once connected, exposes BOTH read tools (Trend Radar)
    AND write/trading tools (list bots + holdings, pick trading pair, place trades through
    connected bots). Wiring the SIGNUM MCP directly into SPARTA would import that
    trading/write capability into SPARTA -- which violates the C22 read-only boundary.

Recommendation: obtain the payload via the EXISTING external read-only Claude Routine (run in
a separate Claude+SIGNUM-MCP environment) calling ONLY get-trendradar-daily, save the JSON
locally, and let SPARTA's existing local pickup/import/readiness pipeline handle it. Do NOT
connect the SIGNUM MCP to SPARTA. Every dangerous capability is pinned False.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.c22_signum_gc_local_export_importer_contract as _imp

DISC_SCHEMA_VERSION = 1
DISC_MODE = "RESEARCH_ONLY"
DISC_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = _imp.CANDIDATE_ID
C22_STATE = _imp.C22_STATE                              # HOLD_FOR_MORE_FROZEN_DATA_WINDOWS

# --- findings ---------------------------------------------------------------
MANUAL_JSON_EXPORT_FOUND = False
OFFICIAL_READ_ONLY_TOOL = "get-trendradar-daily"
OFFICIAL_READ_ONLY_TOOL_KIND = "MCP (read-only, permission-based)"
SIGNUM_MCP_CONFIGURED_IN_THIS_ENV = False
MCP_SERVERS_CONFIGURED_IN_THIS_ENV = ("exa",)          # observed via the MCP resource list
# the SIGNUM MCP, when connected, also exposes write/trading tools -- so it must NOT be
# wired into SPARTA.
SIGNUM_MCP_EXPOSES_WRITE_TRADING_TOOLS = True
SIGNUM_MCP_WRITE_TOOL_EXAMPLES = (
    "list-bots-and-holdings", "pick-trading-pair", "send-trading-signal",
    "place-trade-through-connected-bot")
SOURCES = (
    "https://signum.money/",
    "https://www.trendtrack.io/features/mcp",
    "https://docs.trendtrack.io/connect/claude",
)

# --- the authoritative importer-required schema (single-sourced semantics) ---
EXPECTED_TOP_LEVEL_KEYS = ("limited", "total", "results")
EXPECTED_ROW_COUNT = _imp.EXPECTED_ROW_COUNT           # 50
EXPECTED_DETECTOR = _imp.EXPECTED_DETECTOR             # "gc"
EXPECTED_ASSET_CLASS = _imp.EXPECTED_ASSET_CLASS       # "crypto"
# required fields per the importer's validate_import_candidate gate.
IMPORTER_REQUIRED_CHECKS = (
    "has_50_rows",                      # total >= 50 OR len(results) >= 50
    "all_detector_gc",                  # every row detector == "gc"
    "all_asset_class_crypto",           # every row assetClass == "crypto"
    "run_date_present",                 # single distinct runDate across rows
    "indicators_data_present",          # every row indicators.data present
    "latest_and_previous_candles_present",  # >= 2 closed daily candles
    "gc_trend_upper_filter_present",    # latest + previous gc.trend/upper/filter
    "market_rank_present",              # every row marketRank present (numeric)
    "cmc_ref_price_usd_present",        # every row indicators.cmcRefPriceUsd present
)
# the nested per-row schema the importer + labeler read.
EXPECTED_ROW_SCHEMA = {
    "symbol": "str (e.g. BINANCE:QNTUSDT)",
    "detector": '"gc"',
    "assetClass": '"crypto"',
    "runDate": "ISO date 'YYYY-MM-DD' (single distinct value across rows)",
    "marketRank": "number (uniqueness resolved by human tie-breaker)",
    "marketCap": "number (used by the marketRank tie-breaker)",
    "indicators": {
        "cmcRefPriceUsd": "number (USD reference price)",
        "data": ("array of >= 2 closed daily candles; [-1]=latest, [-2]=previous; "
                 "each: {date: 'YYYY-MM-DD', ohlc:{o,h,l,c numbers}, "
                 "gc:{lower, trend in Green|Grey|Red, upper, filter numbers}, "
                 "volume: number}"),
    },
}

RECOMMENDED_METHOD = "external_read_only_get_trendradar_daily_claude_routine_save_local"
# the safest next human decision: choose the export/save method (recommend the external
# read-only routine; do NOT wire SIGNUM MCP into SPARTA).
RECOMMENDED_NEXT_TOKEN = "HUMAN_DECISION_C22_EXPORT_SAVE_AUTOMATION_METHOD_OR_HOLD"

VERDICT_DISCOVERY_READY = (
    "C22_SIGNUM_OFFICIAL_TRENDRADAR_SOURCE_DISCOVERY_READY_FOR_REVIEW")

_CAPABILITY_FLAGS_FALSE = (
    "executes", "implements_live_fetch", "performs_signum_login", "connects_signum_mcp",
    "wires_signum_mcp_into_sparta", "fetches_data", "performs_network_io", "calls_api",
    "calls_get_trendradar_daily", "calls_write_or_trading_tool", "sends_trading_signal",
    "places_trades", "manages_bots", "edits_bots", "rotates_bots", "rebalances_bots",
    "connects_exchange", "stores_credentials", "stores_cookies", "stores_tokens",
    "stores_passwords", "stores_session_files", "uses_api_keys", "opens_browser",
    "performs_browser_automation", "runs_labels", "runs_replay", "builds_replay",
    "optimizes_parameters", "paper_trading", "live_trading", "connects_broker",
    "contains_order_logic", "modifies_c22_rules", "starts_c23", "reopens_c21",
    "auto_commits", "auto_pushes", "auto_advances", "crosses_into_forbidden_gate",
)


def build_source_discovery() -> dict[str, Any]:
    """Assemble the read-only SIGNUM Trend Radar source-discovery findings. Pure; no I/O;
    implements no live fetch; connects to nothing; calls no trading/write tool."""
    record: dict[str, Any] = {
        "schema_version": DISC_SCHEMA_VERSION, "mode": DISC_MODE, "lane": DISC_LANE,
        "candidate_id": CANDIDATE_ID,
        "is_discovery_only": True, "implements_nothing_live": True,
        "label": (
            "Candidate #22 SIGNUM official Trend Radar source-discovery findings (READ-ONLY, "
            "RESEARCH ONLY, DISCOVERY ONLY). No manual JSON export found; the official "
            "read-only source is the get-trendradar-daily MCP tool (not configured in this "
            "SPARTA env). The SIGNUM MCP also exposes write/trading tools, so it must NOT be "
            "wired into SPARTA; use the external read-only Routine + local pipeline. "
            "Implements no live fetch; calls no trading tool; stores no credentials."),
        # findings
        "manual_json_export_found": MANUAL_JSON_EXPORT_FOUND,
        "official_read_only_tool": OFFICIAL_READ_ONLY_TOOL,
        "official_read_only_tool_kind": OFFICIAL_READ_ONLY_TOOL_KIND,
        "official_read_only_export_exists": True,
        "signum_mcp_configured_in_this_env": SIGNUM_MCP_CONFIGURED_IN_THIS_ENV,
        "mcp_servers_configured_in_this_env": list(MCP_SERVERS_CONFIGURED_IN_THIS_ENV),
        "signum_mcp_exposes_write_trading_tools": SIGNUM_MCP_EXPOSES_WRITE_TRADING_TOOLS,
        "signum_mcp_write_tool_examples": list(SIGNUM_MCP_WRITE_TOOL_EXAMPLES),
        "must_not_wire_signum_mcp_into_sparta": True,
        "sources": list(SOURCES),
        # schema
        "expected_top_level_keys": list(EXPECTED_TOP_LEVEL_KEYS),
        "expected_row_count": EXPECTED_ROW_COUNT,
        "expected_detector": EXPECTED_DETECTOR,
        "expected_asset_class": EXPECTED_ASSET_CLASS,
        "importer_required_checks": list(IMPORTER_REQUIRED_CHECKS),
        "expected_row_schema": dict(EXPECTED_ROW_SCHEMA),
        # recommendation
        "recommended_method": RECOMMENDED_METHOD,
        "recommended_next_token": RECOMMENDED_NEXT_TOKEN,
        "recommendation_summary": (
            "An official READ-ONLY source exists -- the get-trendradar-daily MCP tool -- but "
            "the SIGNUM MCP also carries write/trading tools, so do NOT connect it to SPARTA. "
            "Safest path: keep using the EXTERNAL read-only Claude Routine (separate "
            "Claude+SIGNUM-MCP session) that calls ONLY get-trendradar-daily, save the full "
            "JSON locally, and let SPARTA's existing pickup/import/readiness pipeline ingest "
            "it. A manual JSON export button does not appear to exist."),
        "verdict": VERDICT_DISCOVERY_READY,
        # preserved state
        "c22_state": C22_STATE, "replay_locked": True,
        "advances_nothing": True, "human_review_required": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_execute": True, "no_live_fetch": True, "no_signum_login": True,
        "no_connect_signum_mcp": True, "no_wire_signum_mcp_into_sparta": True,
        "no_network_io": True, "no_api_call": True, "no_call_get_trendradar_daily": True,
        "no_write_or_trading_tool": True, "no_send_trading_signal": True,
        "no_place_trades": True, "no_manage_bots": True, "no_connect_exchange": True,
        "no_store_credentials": True, "no_store_cookies": True, "no_store_tokens": True,
        "no_store_session_files": True, "no_api_keys": True, "no_browser_automation": True,
        "no_run_labels": True, "no_replay": True, "no_optimization": True,
        "no_paper_trading": True, "no_live_trading": True, "no_broker": True,
        "no_order_logic": True, "no_modify_c22_rules": True, "no_start_c23": True,
        "no_reopen_c21": True, "no_auto_commit": True, "no_auto_push": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_source_discovery(record: Any) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when research-only, discovery-only (implements no
    live fetch, connects to nothing, calls no trading/write tool, stores no credentials);
    the findings hold (no manual export; official read-only get-trendradar-daily MCP tool
    exists but is not wired into SPARTA; the SIGNUM MCP exposes write/trading tools and must
    not be connected to SPARTA); the importer-required schema is recorded; the recommendation
    is the external read-only routine; C22 stays HOLD with replay locked; and every
    capability flag is False."""
    failures: list = []
    if not isinstance(record, dict):
        return {"valid": False, "failures": ["record_not_a_dict"]}
    r = record

    if r.get("mode") != DISC_MODE:
        failures.append("mode_not_research_only")
    if r.get("is_discovery_only") is not True:
        failures.append("not_discovery_only")
    if r.get("implements_nothing_live") is not True:
        failures.append("implements_something_live")
    if r.get("verdict") != VERDICT_DISCOVERY_READY:
        failures.append("bad_verdict")

    # findings
    if r.get("manual_json_export_found") is not False:
        failures.append("manual_export_finding_wrong")
    if r.get("official_read_only_tool") != OFFICIAL_READ_ONLY_TOOL:
        failures.append("official_tool_wrong")
    if r.get("official_read_only_export_exists") is not True:
        failures.append("official_export_existence_wrong")
    if r.get("signum_mcp_configured_in_this_env") is not False:
        failures.append("signum_mcp_should_not_be_configured_here")
    if r.get("signum_mcp_exposes_write_trading_tools") is not True:
        failures.append("must_note_signum_mcp_write_tools")
    if r.get("must_not_wire_signum_mcp_into_sparta") is not True:
        failures.append("must_forbid_wiring_signum_mcp")
    if not r.get("sources"):
        failures.append("sources_missing")

    # schema recorded
    if tuple(r.get("expected_top_level_keys") or ()) != EXPECTED_TOP_LEVEL_KEYS:
        failures.append("top_level_keys_wrong")
    if r.get("expected_row_count") != EXPECTED_ROW_COUNT:
        failures.append("row_count_wrong")
    if r.get("expected_detector") != EXPECTED_DETECTOR:
        failures.append("detector_wrong")
    if r.get("expected_asset_class") != EXPECTED_ASSET_CLASS:
        failures.append("asset_class_wrong")
    if tuple(r.get("importer_required_checks") or ()) != IMPORTER_REQUIRED_CHECKS:
        failures.append("required_checks_wrong")
    rs = r.get("expected_row_schema") or {}
    for k in ("detector", "assetClass", "runDate", "marketRank", "indicators"):
        if k not in rs:
            failures.append("row_schema_missing_%s" % k)

    # recommendation
    if r.get("recommended_method") != RECOMMENDED_METHOD:
        failures.append("recommended_method_wrong")
    if r.get("recommended_next_token") != RECOMMENDED_NEXT_TOKEN:
        failures.append("recommended_token_wrong")

    # state
    if r.get("c22_state") != C22_STATE:
        failures.append("c22_state_changed")
    if r.get("replay_locked") is not True:
        failures.append("replay_not_locked")
    if r.get("advances_nothing") is not True:
        failures.append("must_advance_nothing")

    locks = r.get("scope_locks") or {}
    for key in ("no_execute", "no_live_fetch", "no_signum_login", "no_connect_signum_mcp",
                "no_wire_signum_mcp_into_sparta", "no_network_io", "no_api_call",
                "no_call_get_trendradar_daily", "no_write_or_trading_tool",
                "no_send_trading_signal", "no_place_trades", "no_manage_bots",
                "no_connect_exchange", "no_store_credentials", "no_store_tokens",
                "no_api_keys", "no_run_labels", "no_replay", "no_optimization",
                "no_paper_trading", "no_live_trading", "no_order_logic",
                "no_modify_c22_rules", "no_start_c23", "no_reopen_c21"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if r.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
