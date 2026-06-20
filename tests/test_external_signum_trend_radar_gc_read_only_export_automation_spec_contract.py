"""Tests for the Candidate #22 Signum GC read-only export automation SPEC.

Proves the spec is DEFINITION-ONLY and SAFE: it is read-only; the ONLY allowed Signum tool
is get-trendradar-daily with the frozen read-only params (gc / daily / includeIndicators /
full JSON / never summary-only); every dangerous Signum action (edit-bot, send-trading-
signal, send-email, pair change, conversion, Hyperliquid, API keys/credentials, trading,
bot edits, routine self-modification) is explicitly forbidden; SPARTA never connects to
Signum/MCP and performs no data fetch; no scheduler is installed/triggered; no labels/replay
run; no trading/order/live/paper/broker code is present; and C22 remains
HOLD_FOR_MORE_FROZEN_DATA_WINDOWS. Creates NO Claude Routine."""
from __future__ import annotations

import ast
from pathlib import Path

import sparta_commander.external_signum_trend_radar_gc_read_only_export_automation_spec_contract as xs  # noqa: E501

_S = xs.build_export_automation_spec()


# ---- core: spec builds + validates -----------------------------------------

def test_spec_builds_and_validates():
    assert _S["mode"] == "RESEARCH_ONLY"
    assert _S["is_spec_only"] is True
    assert _S["executes_nothing"] is True
    assert _S["creates_no_claude_routine"] is True
    assert _S["verdict"] == (
        "C22_SIGNUM_GC_READ_ONLY_EXPORT_AUTOMATION_SPEC_READY_FOR_HUMAN_REVIEW")
    assert xs.validate_export_automation_spec(_S)["valid"] is True


# ---- (1) read-only + only allowed tool is get-trendradar-daily -------------

def test_only_allowed_tool_is_get_trendradar_daily():
    assert tuple(_S["allowed_tools"]) == ("get-trendradar-daily",)
    assert _S["read_only_export_only"] is True
    assert _S["export_params"] == {
        "detector": "gc", "timeframe": "daily", "includeIndicators": True,
        "output": "full_json", "summary_only": False}
    assert _S["full_json_required"] is True
    assert _S["summary_only_output_forbidden"] is True
    assert _S["filename_pattern"] == "gc_crypto_trendradar_daily_YYYYMMDD.json"
    # a second allowed tool must fail validation
    assert xs.validate_export_automation_spec(
        {**_S, "allowed_tools": ["get-trendradar-daily", "edit-bot"]})["valid"] is False


def test_routine_prompt_encodes_read_only_directives():
    p = _S["claude_routine_prompt"]
    assert p == xs.get_claude_routine_prompt()
    for must in ("get-trendradar-daily", "detector = gc", "timeframe = daily",
                 "includeIndicators = true", "FULL JSON",
                 "gc_crypto_trendradar_daily_YYYYMMDD.json", "STRICTLY PROHIBITED"):
        assert must in p, must


# ---- (2) dangerous Signum actions explicitly forbidden ---------------------

def test_dangerous_signum_actions_forbidden():
    prohibited = set(_S["prohibited_actions"])
    for must in ("edit-bot", "send-trading-signal", "send-email", "change-trading-pair",
                 "convert-funds", "hyperliquid-action", "use-api-keys", "use-credentials",
                 "trade", "bot-edit", "claude-routine-self-modification"):
        assert must in prohibited, must
    # removing a prohibition must fail validation
    weak = [a for a in _S["prohibited_actions"] if a != "send-trading-signal"]
    assert xs.validate_export_automation_spec(
        {**_S, "prohibited_actions": weak})["valid"] is False


# ---- no Signum/MCP execution in SPARTA; no data fetch ----------------------

def test_sparta_never_connects_and_no_fetch():
    assert _S["sparta_never_connects_to_signum_or_mcp"] is True
    assert _S["sparta_validates_local_files_only_after_they_exist"] is True
    for flag in ("sparta_connects_to_signum", "sparta_uses_mcp", "connects_signum",
                 "uses_mcp", "accesses_hyperliquid", "fetches_data", "stages_data",
                 "performs_network_io", "calls_api"):
        assert _S[flag] is False, flag


# ---- (4) schedule installs/triggers nothing + timezone note ----------------

def test_schedule_installs_nothing():
    sch = _S["schedule"]
    assert sch["cadence"] == "daily"
    assert sch["suggested_time_utc"] == "00:30"
    assert "UTC" in sch["timezone_note"]
    assert sch["installs_scheduler"] is False
    assert sch["triggers_scheduler"] is False
    assert sch["schedule_is_human_installed_externally"] is True
    assert _S["installs_scheduler"] is False and _S["triggers_scheduler"] is False


# ---- (5) dashboard behavior: no labels/replay until re-review --------------

def test_dashboard_behavior():
    assert _S["jarvis_tracks_progress"] is True
    assert _S["missing_export_shows_as_missing"] is True
    assert _S["no_labels_or_replay_until_rereview"] is True
    assert _S["c22_state"] == "HOLD_FOR_MORE_FROZEN_DATA_WINDOWS"
    assert _S["replay_locked"] is True
    assert _S["required_windows"] == 20


# ---- no labels/replay + no trading + capability flags ----------------------

def test_no_labels_replay_trading_capability():
    for flag in ("runs_labels", "runs_replay", "builds_replay", "places_orders",
                 "live_trading", "paper_trading", "connects_broker", "sends_trades",
                 "creates_claude_routine", "runs_claude_routine", "modifies_c22_rules",
                 "starts_c23", "reopens_c21", "installs_scheduler", "triggers_scheduler"):
        assert _S[flag] is False, flag
    for flag in xs._CAPABILITY_FLAGS_FALSE:
        assert _S[flag] is False, flag
        assert xs.validate_export_automation_spec({**_S, flag: True})["valid"] is False
    for key, val in _S["scope_locks"].items():
        assert val is True, key


# ---- module purity + no real Signum/MCP/network call in the SPEC source ----

def test_module_purity_no_io_no_signum_execution():
    src = Path(xs.__file__).read_text(encoding="utf-8")
    assert "__main__" not in src
    # actionable I/O / network call tokens (descriptive words like "mcp"/"signum" appear
    # only inside NEGATED safety flag names, e.g. no_mcp / uses_mcp=False, and are excluded
    # -- real MCP/network execution is precluded by the banned-imports AST check below).
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch(", "open(", "subprocess", "Popen", "urlopen",
                 "requests.", "httpx", "socket.connect"):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
              "subprocess", "websockets", "aiohttp", "schedule", "threading",
              "asyncio", "telegram", "os", "io", "shutil", "ssl", "ftplib",
              "json", "hashlib", "pathlib", "numpy", "pandas"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned), imported & banned
    for call in ast.walk(tree):
        if isinstance(call, ast.Call):
            name = (call.func.attr if isinstance(call.func, ast.Attribute)
                    else getattr(call.func, "id", ""))
            assert name not in ("open", "exec", "eval", "compile"), name
