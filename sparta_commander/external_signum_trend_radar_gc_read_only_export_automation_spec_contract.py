"""Candidate #22 -- Signum Trend Radar GC READ-ONLY EXPORT AUTOMATION SPEC
-- PURE, DEFINITION-ONLY, RESEARCH ONLY.

DEFINES (does NOT create, does NOT run) a safe, human-reviewable automation spec for the
daily READ-ONLY export of Signum Trend Radar GC data that C22 needs to collect more frozen
windows. It is a SPEC: it produces the exact external Claude-Routine prompt to use, the
closed set of prohibited Signum actions, the operator workflow, the recommended schedule,
and the dashboard behaviour -- but it creates NO Claude Routine, connects to NO Signum / MCP
/ Hyperliquid, fetches NO data, stages NO file, runs NO labels / replay, and installs /
triggers NO scheduler. SPARTA never talks to Signum: the routine runs externally, the human
saves the resulting JSON into the local data directory, and SPARTA only VALIDATES local
files after they exist.

The only Signum tool the routine may use is `get-trendradar-daily` (detector=gc,
timeframe=daily, includeIndicators=true, full JSON, never summary-only). Every dangerous
Signum capability -- edit-bot, send-trading-signal, send-email, pair change, conversion,
any Hyperliquid action, API keys / credentials, trading, bot edits, routine
self-modification -- is explicitly forbidden. Every dangerous capability flag is pinned
False with a full scope_locks set, and C22 remains HOLD_FOR_MORE_FROZEN_DATA_WINDOWS.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.c22_signum_gc_data_collection_tracker_contract as _trk
import sparta_commander.external_signum_trend_radar_gc_long_short_v1_real_candle_labels_review_contract as _lr  # noqa: E501

XS_SCHEMA_VERSION = 1
XS_MODE = "RESEARCH_ONLY"
XS_LANE = "crypto_d1_auto_research"
BUNDLE_NAME = "C22_SIGNUM_GC_READ_ONLY_EXPORT_AUTOMATION_SPEC"

CANDIDATE_ID = _lr.CANDIDATE_ID

# the ONE Signum tool the routine may call -- a strictly READ-ONLY export.
ALLOWED_TOOL = "get-trendradar-daily"
ALLOWED_TOOLS = (ALLOWED_TOOL,)

# the export parameters (frozen).
EXPORT_PARAMS = {
    "detector": "gc",
    "timeframe": "daily",
    "includeIndicators": True,
    "output": "full_json",
    "summary_only": False,
}

# filename pattern + target directory single-sourced from the tracker contract.
FILENAME_PATTERN = _trk.EXPORT_PREFIX + "_YYYYMMDD.json"   # gc_crypto_trendradar_daily_*
TARGET_DIR = _trk.DATA_DIR                                 # data/external_signum_trend_radar_gc
TARGET_DIR_ABS = "C:/SPARTA_BRAIN/" + _trk.DATA_DIR

# the CLOSED set of Signum / external actions the routine must NEVER take.
PROHIBITED_ACTIONS = (
    "edit-bot", "send-trading-signal", "send-email", "change-trading-pair",
    "convert-funds", "hyperliquid-action", "place-order", "set-leverage",
    "use-api-keys", "use-credentials", "trade", "bot-edit",
    "claude-routine-self-modification", "write-to-sparta", "connect-to-sparta",
)

# recommended schedule (human-installed externally; this spec installs nothing).
SCHEDULE = {
    "cadence": "daily",
    "after": "the daily Signum Trend Radar data update",
    "suggested_time_utc": "00:30",
    "suggested_time_note": "00:30 UTC or later",
    "timezone_note": (
        "the suggested time is in UTC; convert to your local timezone (e.g. 00:30 UTC is "
        "20:30 US-Eastern the previous evening / 01:30 CET) and ensure it runs AFTER "
        "Signum's daily data refresh so the export captures the freshly closed daily "
        "candle"),
    "installs_scheduler": False,
    "triggers_scheduler": False,
    "schedule_is_human_installed_externally": True,
}

OPERATOR_WORKFLOW = (
    "The external Claude Routine (run in the Signum/Claude environment, NOT in SPARTA) "
    "calls get-trendradar-daily read-only and outputs the FULL JSON.",
    "The Routine / export produces JSON text or a downloadable artifact.",
    "The USER saves that file manually (or via an approved local file step) into "
    + TARGET_DIR_ABS + "\\ using the name gc_crypto_trendradar_daily_YYYYMMDD.json.",
    "SPARTA only VALIDATES the local file AFTER it exists (the existing C22 dataset "
    "validation + tracker contracts); SPARTA never connects to Signum or MCP directly.",
    "The Jarvis tracker updates the collected-windows count on the next read-only scan.",
)

DASHBOARD_BEHAVIOR = (
    "Jarvis continues tracking collection progress (1/20, 2/20, ...) from the read-only "
    "directory listing.",
    "A day with no saved export simply does not advance the count -- the missing window "
    "shows as 'not yet collected' (windows_remaining stays higher and the next export "
    "date is surfaced).",
    "No labels and no replay run until enough frozen windows are collected AND the human "
    "re-review gate is passed.",
)

C22_STATE = _trk.C22_STATE                              # HOLD_FOR_MORE_FROZEN_DATA_WINDOWS
NEXT_HUMAN_ACTION_WHEN_READY = _trk.NEXT_HUMAN_ACTION_WHEN_READY
REQUIRED_WINDOWS = _trk.REQUIRED_WINDOWS               # 20

VERDICT_SPEC_READY = "C22_SIGNUM_GC_READ_ONLY_EXPORT_AUTOMATION_SPEC_READY_FOR_HUMAN_REVIEW"
NEXT_REQUIRED_ACTION = (
    "HUMAN_DECISION_CREATE_C22_SIGNUM_GC_EXPORT_CLAUDE_ROUTINE_OR_HOLD")

_CAPABILITY_FLAGS_FALSE = (
    "executes", "is_claude_routine", "creates_claude_routine", "runs_claude_routine",
    "modifies_claude_routine", "sparta_connects_to_signum", "sparta_uses_mcp",
    "connects_signum", "uses_mcp", "accesses_hyperliquid", "fetches_data", "stages_data",
    "writes_files", "performs_network_io", "calls_api", "uses_credentials",
    "uses_api_keys", "edits_bots", "sends_trading_signal", "sends_email",
    "changes_trading_pair", "converts_funds", "places_orders", "sets_leverage",
    "contains_order_logic", "sends_trades", "paper_trading", "live_trading",
    "deploys_capital", "connects_broker", "connects_exchange", "runs_labels",
    "runs_replay", "builds_replay", "optimizes_parameters", "stages_dataset",
    "installs_scheduler", "triggers_scheduler", "modifies_scheduler",
    "modifies_c22_rules", "starts_c23", "reopens_c21", "auto_commits", "auto_pushes",
    "auto_fetches", "auto_promotes", "auto_advances", "crosses_into_forbidden_gate",
)


def get_claude_routine_prompt() -> str:
    """PURE. The exact external Claude-Routine prompt the human will use (in the
    Signum/Claude environment, NOT in SPARTA). Read-only export only."""
    return "\n".join([
        "ROLE: read-only data export assistant for Signum Trend Radar.",
        "",
        "TASK: export ONE daily Trend Radar GC snapshot as full JSON. Read-only. Do not "
        "trade, do not edit anything, do not send anything.",
        "",
        "ALLOWED TOOL (exactly one): get-trendradar-daily",
        "PARAMETERS:",
        "  - detector = gc",
        "  - timeframe = daily",
        "  - includeIndicators = true",
        "  - output the FULL JSON response (every row + indicators.data candles)",
        "  - do NOT summarise; no summary-only output; no truncation",
        "",
        "OUTPUT: return the complete raw JSON text. Save it with the filename:",
        "  " + FILENAME_PATTERN,
        "  (YYYYMMDD = the export date, e.g. gc_crypto_trendradar_daily_20260621.json)",
        "",
        "STRICTLY PROHIBITED -- never call or do any of these:",
        "  - edit-bot / any bot edit",
        "  - send-trading-signal / place any order / set leverage / trade",
        "  - send-email",
        "  - change trading pair / convert funds",
        "  - any Hyperliquid action",
        "  - use API keys or credentials",
        "  - modify this routine or any other routine",
        "  - write to or connect to SPARTA",
        "",
        "If anything other than a read-only get-trendradar-daily export is requested, "
        "STOP and return only the JSON (or an explanation), never an action.",
    ])


def build_export_automation_spec() -> dict[str, Any]:
    """Assemble the read-only export automation spec. Pure; no I/O; defines everything and
    executes nothing."""
    record: dict[str, Any] = {
        "schema_version": XS_SCHEMA_VERSION, "mode": XS_MODE, "lane": XS_LANE,
        "bundle_name": BUNDLE_NAME, "candidate_id": CANDIDATE_ID,
        "is_spec_only": True, "is_definition_only": True, "executes_nothing": True,
        "creates_no_claude_routine": True,
        "sparta_never_connects_to_signum_or_mcp": True,
        "label": (
            "Candidate #22 Signum Trend Radar GC read-only export automation SPEC "
            "(DEFINITION ONLY, RESEARCH ONLY). Defines the safe external Claude-Routine "
            "prompt (get-trendradar-daily, gc, daily, includeIndicators, full JSON), the "
            "prohibited actions, the operator workflow, the recommended schedule, and the "
            "dashboard behaviour. Creates no routine; connects to nothing; fetches "
            "nothing; installs no scheduler."),
        # (1) the safe routine prompt + its parameters
        "allowed_tools": list(ALLOWED_TOOLS),
        "export_params": dict(EXPORT_PARAMS),
        "filename_pattern": FILENAME_PATTERN,
        "target_dir": TARGET_DIR,
        "target_dir_abs": TARGET_DIR_ABS,
        "claude_routine_prompt": get_claude_routine_prompt(),
        "read_only_export_only": True,
        "full_json_required": True, "summary_only_output_forbidden": True,
        # (2) prohibited actions (closed set)
        "prohibited_actions": list(PROHIBITED_ACTIONS),
        # (3) operator workflow
        "operator_workflow": list(OPERATOR_WORKFLOW),
        "sparta_validates_local_files_only_after_they_exist": True,
        # (4) recommended schedule
        "schedule": dict(SCHEDULE),
        # (5) dashboard behaviour
        "dashboard_behavior": list(DASHBOARD_BEHAVIOR),
        "jarvis_tracks_progress": True,
        "missing_export_shows_as_missing": True,
        "no_labels_or_replay_until_rereview": True,
        # current candidate state
        "c22_state": C22_STATE,
        "replay_locked": True,
        "required_windows": REQUIRED_WINDOWS,
        "next_human_action_when_ready": NEXT_HUMAN_ACTION_WHEN_READY,
        # outcome
        "verdict": VERDICT_SPEC_READY,
        "next_required_action": NEXT_REQUIRED_ACTION,
        "advances_nothing": True,
        "human_review_required": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_execute": True, "no_create_claude_routine": True,
        "no_run_claude_routine": True, "no_modify_claude_routine": True,
        "no_sparta_connect_signum": True, "no_sparta_use_mcp": True,
        "no_signum_connection": True, "no_mcp": True, "no_hyperliquid": True,
        "no_data_fetch": True, "no_stage_dataset": True, "no_network_io": True,
        "no_file_write": True, "no_api_keys": True, "no_credentials": True,
        "no_bot_edits": True, "no_send_trading_signal": True, "no_send_email": True,
        "no_change_pair": True, "no_convert_funds": True, "no_place_orders": True,
        "no_set_leverage": True, "no_order_logic": True, "no_paper_trading": True,
        "no_live_trading": True, "no_broker": True, "no_run_labels": True,
        "no_replay": True, "no_build_replay": True, "no_optimization": True,
        "no_install_scheduler": True, "no_trigger_scheduler": True,
        "no_modify_scheduler": True, "no_modify_c22_rules": True, "no_start_c23": True,
        "no_reopen_c21": True, "no_auto_commit": True, "no_auto_push": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_export_automation_spec(record: Any) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the spec is research-only, definition-only
    (creates/runs no routine, connects to nothing), the ONLY allowed tool is
    get-trendradar-daily with the frozen read-only params, every dangerous Signum action is
    explicitly prohibited, SPARTA never connects to Signum/MCP, no scheduler is
    installed/triggered, no labels/replay, C22 stays HOLD, and every capability flag is
    False."""
    failures: list = []
    if not isinstance(record, dict):
        return {"valid": False, "failures": ["record_not_a_dict"]}
    r = record

    if r.get("mode") != XS_MODE:
        failures.append("mode_not_research_only")
    if r.get("is_spec_only") is not True:
        failures.append("not_spec_only")
    if r.get("executes_nothing") is not True:
        failures.append("executes_something")
    if r.get("creates_no_claude_routine") is not True:
        failures.append("must_create_no_routine")
    if r.get("sparta_never_connects_to_signum_or_mcp") is not True:
        failures.append("sparta_must_not_connect_signum_mcp")
    if r.get("verdict") != VERDICT_SPEC_READY:
        failures.append("bad_verdict")

    # (1) exactly one allowed tool: get-trendradar-daily
    if tuple(r.get("allowed_tools") or ()) != ALLOWED_TOOLS:
        failures.append("allowed_tools_tampered")
    if r.get("read_only_export_only") is not True:
        failures.append("not_read_only_export")
    params = r.get("export_params") or {}
    for k, v in EXPORT_PARAMS.items():
        if params.get(k) != v:
            failures.append("export_param_wrong_%s" % k)
    if r.get("summary_only_output_forbidden") is not True:
        failures.append("summary_only_not_forbidden")
    if r.get("filename_pattern") != FILENAME_PATTERN:
        failures.append("filename_pattern_wrong")

    # the prompt itself must encode the read-only directives + the allowed tool
    prompt = r.get("claude_routine_prompt") or ""
    for must in (ALLOWED_TOOL, "detector = gc", "timeframe = daily",
                 "includeIndicators = true", "FULL JSON", FILENAME_PATTERN,
                 "STRICTLY PROHIBITED"):
        if must not in prompt:
            failures.append("prompt_missing:%s" % must)
    # the prompt must NOT instruct any execution against SPARTA / trading
    for forbidden in ("place any order", "edit-bot", "send-email"):
        if forbidden not in prompt:
            failures.append("prompt_missing_prohibition:%s" % forbidden)

    # (2) prohibited actions: the closed dangerous set must all be present
    prohibited = set(r.get("prohibited_actions") or ())
    for must in ("edit-bot", "send-trading-signal", "send-email", "change-trading-pair",
                 "convert-funds", "hyperliquid-action", "use-api-keys", "use-credentials",
                 "trade", "bot-edit", "claude-routine-self-modification"):
        if must not in prohibited:
            failures.append("prohibited_action_missing:%s" % must)

    # (3) operator workflow: SPARTA validates only after files exist
    if r.get("sparta_validates_local_files_only_after_they_exist") is not True:
        failures.append("sparta_must_validate_after_only")
    if not (r.get("operator_workflow") or []):
        failures.append("operator_workflow_missing")

    # (4) schedule installs/triggers nothing
    sch = r.get("schedule") or {}
    if sch.get("installs_scheduler") is not False:
        failures.append("schedule_installs_scheduler")
    if sch.get("triggers_scheduler") is not False:
        failures.append("schedule_triggers_scheduler")
    if sch.get("schedule_is_human_installed_externally") is not True:
        failures.append("schedule_not_human_installed")
    if not sch.get("timezone_note"):
        failures.append("schedule_timezone_note_missing")

    # (5) dashboard behaviour: no labels/replay until re-review
    if r.get("no_labels_or_replay_until_rereview") is not True:
        failures.append("must_not_label_replay_until_rereview")
    if r.get("missing_export_shows_as_missing") is not True:
        failures.append("missing_export_not_shown")

    # current state + advances nothing
    if r.get("c22_state") != C22_STATE:
        failures.append("c22_state_wrong")
    if r.get("replay_locked") is not True:
        failures.append("replay_not_locked")
    if r.get("advances_nothing") is not True:
        failures.append("must_advance_nothing")

    locks = r.get("scope_locks") or {}
    for key in ("no_execute", "no_create_claude_routine", "no_run_claude_routine",
                "no_sparta_connect_signum", "no_sparta_use_mcp", "no_signum_connection",
                "no_mcp", "no_hyperliquid", "no_data_fetch", "no_stage_dataset",
                "no_network_io", "no_api_keys", "no_credentials", "no_bot_edits",
                "no_send_trading_signal", "no_send_email", "no_place_orders",
                "no_order_logic", "no_paper_trading", "no_live_trading", "no_run_labels",
                "no_replay", "no_install_scheduler", "no_trigger_scheduler",
                "no_modify_c22_rules", "no_start_c23", "no_reopen_c21"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if r.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
