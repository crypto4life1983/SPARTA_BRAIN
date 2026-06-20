"""Tests for the Candidate #22 SIGNUM official Trend Radar source-discovery findings.

Proves the discovery is DISCOVERY-ONLY and SAFE: no manual JSON export found; the official
read-only source is the get-trendradar-daily MCP tool (not configured in this env); the
SIGNUM MCP also exposes write/trading tools and must NOT be wired into SPARTA; the
importer-required schema is recorded faithfully; the recommendation is the external read-only
Routine; it implements no live fetch, connects to nothing, calls no trading/write tool,
stores no credentials; and C22 stays HOLD_FOR_MORE_FROZEN_DATA_WINDOWS with replay locked."""
from __future__ import annotations

import ast
from pathlib import Path

import sparta_commander.c22_signum_official_trendradar_source_discovery_contract as disc
import sparta_commander.c22_signum_gc_local_export_importer_contract as imp

_D = disc.build_source_discovery()


# ---- builds + validates ----------------------------------------------------

def test_discovery_builds_and_validates():
    assert _D["mode"] == "RESEARCH_ONLY"
    assert _D["is_discovery_only"] is True
    assert _D["implements_nothing_live"] is True
    assert _D["verdict"] == (
        "C22_SIGNUM_OFFICIAL_TRENDRADAR_SOURCE_DISCOVERY_READY_FOR_REVIEW")
    assert disc.validate_source_discovery(_D)["valid"] is True


# ---- finding 1: no manual JSON export --------------------------------------

def test_no_manual_export():
    assert _D["manual_json_export_found"] is False


# ---- finding 2: official read-only MCP export exists (not wired to SPARTA) --

def test_official_read_only_export_exists():
    assert _D["official_read_only_export_exists"] is True
    assert _D["official_read_only_tool"] == "get-trendradar-daily"
    assert "read-only" in _D["official_read_only_tool_kind"].lower()
    assert _D["signum_mcp_configured_in_this_env"] is False
    assert _D["mcp_servers_configured_in_this_env"] == ["exa"]


# ---- finding 3: SIGNUM MCP carries write/trading -> must not wire to SPARTA -

def test_signum_mcp_write_risk_flagged():
    assert _D["signum_mcp_exposes_write_trading_tools"] is True
    assert _D["must_not_wire_signum_mcp_into_sparta"] is True
    assert any("trade" in x or "signal" in x or "bot" in x
               for x in _D["signum_mcp_write_tool_examples"])


# ---- the exact importer-required schema is recorded ------------------------

def test_importer_schema_recorded():
    assert _D["expected_top_level_keys"] == ["limited", "total", "results"]
    assert _D["expected_row_count"] == imp.EXPECTED_ROW_COUNT == 50
    assert _D["expected_detector"] == "gc"
    assert _D["expected_asset_class"] == "crypto"
    assert _D["importer_required_checks"] == [
        "has_50_rows", "all_detector_gc", "all_asset_class_crypto", "run_date_present",
        "indicators_data_present", "latest_and_previous_candles_present",
        "gc_trend_upper_filter_present", "market_rank_present", "cmc_ref_price_usd_present"]
    rs = _D["expected_row_schema"]
    for k in ("detector", "assetClass", "runDate", "marketRank", "marketCap",
              "indicators"):
        assert k in rs, k
    assert "cmcRefPriceUsd" in rs["indicators"]
    assert "data" in rs["indicators"]


# ---- recommendation: external read-only routine, safest next token ----------

def test_recommendation_and_next_token():
    assert _D["recommended_method"] == (
        "external_read_only_get_trendradar_daily_claude_routine_save_local")
    assert _D["recommended_next_token"] == (
        "HUMAN_DECISION_C22_EXPORT_SAVE_AUTOMATION_METHOD_OR_HOLD")
    assert "do NOT connect" in _D["recommendation_summary"] \
        or "do NOT wire" in _D["recommendation_summary"] \
        or "do not connect" in _D["recommendation_summary"].lower()


# ---- implements nothing live; no trading/credentials; state preserved ------

def test_no_live_no_trading_no_credentials_state_preserved():
    for flag in ("implements_live_fetch", "performs_signum_login", "connects_signum_mcp",
                 "wires_signum_mcp_into_sparta", "fetches_data", "calls_get_trendradar_daily",
                 "calls_write_or_trading_tool", "sends_trading_signal", "places_trades",
                 "manages_bots", "stores_credentials", "stores_tokens", "uses_api_keys"):
        assert _D[flag] is False, flag
    assert _D["c22_state"] == "HOLD_FOR_MORE_FROZEN_DATA_WINDOWS"
    assert _D["replay_locked"] is True
    for flag in disc._CAPABILITY_FLAGS_FALSE:
        assert _D[flag] is False, flag
        assert disc.validate_source_discovery({**_D, flag: True})["valid"] is False
    for key, val in _D["scope_locks"].items():
        assert val is True, key


# ---- anti-tamper: cannot flip a finding --------------------------------------

def test_tamper_findings_rejected():
    assert disc.validate_source_discovery(
        {**_D, "must_not_wire_signum_mcp_into_sparta": False})["valid"] is False
    assert disc.validate_source_discovery(
        {**_D, "manual_json_export_found": True})["valid"] is False


# ---- module purity: no live fetch / network / trading tokens in source ------

def test_module_purity_no_live_access_tokens():
    src = Path(disc.__file__).read_text(encoding="utf-8")
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "open(",
                 "subprocess", "Popen", "urlopen", "requests.", "httpx",
                 "socket.connect", ".login(", "json.load", "ListMcpResources",
                 "ReadMcpResource"):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
              "subprocess", "websockets", "aiohttp", "schedule", "threading",
              "asyncio", "telegram", "os", "io", "shutil", "ssl", "ftplib",
              "json", "hashlib", "pathlib", "numpy", "pandas", "selenium"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned), imported & banned
