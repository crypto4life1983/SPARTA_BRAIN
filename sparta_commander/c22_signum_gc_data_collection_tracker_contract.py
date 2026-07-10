"""Candidate #22 -- Signum Trend Radar GC DATA-COLLECTION TRACKER
-- PURE, READ-ONLY, RESEARCH ONLY.

A progress tracker so Jarvis can remind the human to keep staging more frozen daily Signum
Trend Radar GC exports until C22 has enough windows to re-review its real-candle labels. It
is PURE: it operates on a list of DISCOVERED export FILENAMES (the runner / morning report /
panel do the read-only directory listing and pass basenames in); it performs NO file or
network I/O, connects to NO Signum / MCP / Hyperliquid, fetches NO data, stages NO file,
runs NO labels / replay, and installs / triggers NO scheduler.

It counts distinct frozen daily GC windows (one daily export == one decision date), compares
them against the committed re-review thresholds (single-sourced from the labels-review
contract: 20 windows / 20 decision dates / 30 preferred actionable labels), and shows the
current C22 state (HOLD_FOR_MORE_FROZEN_DATA_WINDOWS, replay locked), the windows collected,
the next export date to capture, and the human re-review token to use once enough windows
exist. Every dangerous capability is pinned False with a full scope_locks set.
"""
from __future__ import annotations

import datetime as _dt
from typing import Any

import sparta_commander.external_signum_trend_radar_gc_long_short_v1_real_candle_labels_review_contract as _lr  # noqa: E501

TRK_SCHEMA_VERSION = 1
TRK_MODE = "RESEARCH_ONLY"
TRK_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = _lr.CANDIDATE_ID

# the directory the (read-only) scanner lists; the tracker never writes here.
DATA_DIR = "data/external_signum_trend_radar_gc"
# frozen daily GC export filename shape: gc_crypto_trendradar_daily[_YYYYMMDD].json
EXPORT_PREFIX = "gc_crypto_trendradar_daily"
EXPORT_GLOB = "gc_crypto_trendradar_daily*.json"
# the first (undated) staged export's decision date (its runDate / latest closed candle).
FIRST_WINDOW_DATE = "2026-06-20"

# thresholds single-sourced from the committed labels-review contract.
REQUIRED_WINDOWS = _lr.MIN_FROZEN_DATA_WINDOWS_FOR_REPLAY            # 20
REQUIRED_DECISION_DATES = _lr.MIN_DISTINCT_DECISION_DATES_FOR_REPLAY  # 20
PREFERRED_ACTIONABLE_LABELS = _lr.MIN_ACTIONABLE_LABELS_FOR_REPLAY    # 30

C22_STATE = _lr.REC_HOLD                                  # HOLD_FOR_MORE_FROZEN_DATA_WINDOWS
NEXT_HUMAN_ACTION_WHEN_READY = _lr.NEXT_ACTION_HOLD       # stage-more-then-re-review token

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "performs_file_io", "performs_network_io",
    "fetches_data", "stages_data", "connects_signum", "uses_mcp", "accesses_hyperliquid",
    "calls_api", "uses_network", "uses_credentials", "uses_api_keys", "runs_labels",
    "runs_replay", "builds_replay", "optimizes_parameters", "modifies_c22_rules",
    "starts_c23", "reopens_c21", "auto_commits", "auto_pushes", "auto_fetches",
    "auto_promotes", "auto_advances", "modifies_scheduler", "installs_scheduler",
    "triggers_scheduler", "sends_notifications", "sends_email", "connects_broker",
    "connects_exchange", "sends_trades", "edits_bots", "creates_claude_routines",
    "places_orders", "contains_order_logic", "paper_trading", "live_trading",
    "deploys_capital", "unlocks_replay_gate", "crosses_into_forbidden_gate",
)


def next_calendar_date(iso_date: str) -> str | None:
    """PURE. The calendar day after an ISO date (YYYY-MM-DD). Deterministic; no clock
    read."""
    try:
        d = _dt.date.fromisoformat(str(iso_date))
    except Exception:  # noqa: BLE001
        return None
    return (d + _dt.timedelta(days=1)).isoformat()


def _date_from_filename(name: str) -> str | None:
    """PURE. Extract the decision date from an export filename, or None if it is not a
    frozen daily GC export. `gc_crypto_trendradar_daily.json` -> the first window date;
    `gc_crypto_trendradar_daily_YYYYMMDD.json` -> YYYY-MM-DD."""
    if not isinstance(name, str) or not name.endswith(".json"):
        return None
    stem = name[:-len(".json")]
    if stem == EXPORT_PREFIX:
        return FIRST_WINDOW_DATE
    suffix = EXPORT_PREFIX + "_"
    if stem.startswith(suffix):
        tail = stem[len(suffix):]
        if len(tail) == 8 and tail.isdigit():
            return "%s-%s-%s" % (tail[0:4], tail[4:6], tail[6:8])
    return None


def build_collection_status(discovered_filenames: list) -> dict[str, Any]:
    """PURE. Build the C22 GC collection progress status from discovered export basenames.
    No I/O. One daily export == one decision date == one window."""
    names = sorted({n for n in (discovered_filenames or []) if isinstance(n, str)})
    export_files = [n for n in names if _date_from_filename(n) is not None]
    collected_dates = sorted({_date_from_filename(n) for n in export_files})

    n_windows = len(collected_dates)
    windows_remaining = max(0, REQUIRED_WINDOWS - n_windows)
    pct_complete = round(min(100.0, n_windows / REQUIRED_WINDOWS * 100.0), 1)
    latest_collected_date = collected_dates[-1] if collected_dates else None
    next_export_date = (next_calendar_date(latest_collected_date)
                        if latest_collected_date else FIRST_WINDOW_DATE)
    ready_for_rereview = (n_windows >= REQUIRED_WINDOWS
                          and n_windows >= REQUIRED_DECISION_DATES)

    record: dict[str, Any] = {
        "schema_version": TRK_SCHEMA_VERSION, "mode": TRK_MODE, "lane": TRK_LANE,
        "section": "c22_signum_gc_data_collection_tracker",
        "candidate_id": CANDIDATE_ID,
        "is_tracker_only": True, "read_only": True,
        "label": (
            "Candidate #22 Signum Trend Radar GC data-collection tracker (READ-ONLY, "
            "RESEARCH ONLY). Counts frozen daily GC export windows vs the committed "
            "re-review thresholds and reminds the human which date to export next. Fetches "
            "nothing; advances nothing."),
        "data_dir": DATA_DIR,
        "export_glob": EXPORT_GLOB,
        # progress
        "collected_windows": n_windows,
        "collected_decision_dates": list(collected_dates),
        "export_files_seen": list(export_files),
        "latest_collected_date": latest_collected_date,
        "next_export_date": next_export_date,
        # thresholds
        "required_windows": REQUIRED_WINDOWS,
        "required_decision_dates": REQUIRED_DECISION_DATES,
        "preferred_actionable_labels": PREFERRED_ACTIONABLE_LABELS,
        "windows_remaining": windows_remaining,
        "pct_complete": pct_complete,
        "ready_for_rereview": ready_for_rereview,
        # current candidate state
        "c22_state": C22_STATE,
        "replay_locked": True,
        "next_human_action_when_ready": NEXT_HUMAN_ACTION_WHEN_READY,
        "advances_nothing": True,
        "human_review_required": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_execute": True, "no_file_io": True, "no_network_io": True,
        "no_data_fetch": True, "no_stage_data": True, "no_signum_connection": True,
        "no_mcp": True, "no_hyperliquid": True, "no_api_keys": True,
        "no_credentials": True, "no_run_labels": True, "no_replay": True,
        "no_build_replay": True, "no_optimization": True, "no_modify_c22_rules": True,
        "no_start_c23": True, "no_reopen_c21": True, "no_auto_commit": True,
        "no_auto_push": True, "no_auto_fetch": True, "no_auto_promote": True,
        "no_auto_advance": True, "no_scheduler_change": True,
        "no_scheduler_install": True, "no_scheduler_trigger": True, "no_broker": True,
        "no_order_logic": True, "no_paper_trading": True, "no_live_trading": True,
        "no_unlock_replay_gate": True, "no_crossing_into_forbidden_gate": True,
    }
    return record


def render_collection_section_markdown(status: dict) -> str:
    """PURE. The tracker section as markdown."""
    s = status or {}
    lines = [
        "### C22 Signum GC data-collection tracker (research-only)",
        "- State: **%s** (replay locked)" % s.get("c22_state"),
        "- Windows collected: **%s / %s** (%.1f%%), %s more needed" % (
            s.get("collected_windows"), s.get("required_windows"),
            s.get("pct_complete", 0.0), s.get("windows_remaining")),
        "- Decision dates: %s / %s | preferred actionable labels: %s" % (
            s.get("collected_windows"), s.get("required_decision_dates"),
            s.get("preferred_actionable_labels")),
        "- Latest collected date: %s" % (s.get("latest_collected_date") or "-"),
        "- Next export date to capture: **%s** "
        "(save as `%s/%s_YYYYMMDD.json`)" % (
            s.get("next_export_date"), s.get("data_dir"), EXPORT_PREFIX),
        "- Ready to re-review: **%s**" % s.get("ready_for_rereview"),
    ]
    if s.get("ready_for_rereview"):
        lines.append("- [ready] Enough windows -- next human action: `%s`"
                     % s.get("next_human_action_when_ready"))
    else:
        lines.append("- Keep exporting daily; when ready the human action is: `%s`"
                     % s.get("next_human_action_when_ready"))
    return "\n".join(lines)


def render_collection_section_html(status: dict) -> str:
    """PURE. The tracker section as a small HTML block (no external escaping deps)."""
    s = status or {}

    def esc(x: Any) -> str:
        return (str(x).replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;"))
    rows = [
        "<h3>C22 Signum GC data-collection tracker (research-only)</h3>",
        "<ul>",
        "<li>State: <b>%s</b> (replay locked)</li>" % esc(s.get("c22_state")),
        "<li>Windows collected: <b>%s / %s</b> (%.1f%%), %s more needed</li>" % (
            esc(s.get("collected_windows")), esc(s.get("required_windows")),
            s.get("pct_complete", 0.0), esc(s.get("windows_remaining"))),
        "<li>Latest collected date: %s</li>" % esc(s.get("latest_collected_date") or "—"),
        "<li>Next export date to capture: <b>%s</b></li>" % esc(s.get("next_export_date")),
        "<li>Ready to re-review: <b>%s</b></li>" % esc(s.get("ready_for_rereview")),
        "<li>When ready: <code>%s</code></li>" % esc(
            s.get("next_human_action_when_ready")),
        "</ul>",
    ]
    return "".join(rows)


def validate_collection_status(record: Any) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when research-only, tracker-only, read-only;
    thresholds match the committed review contract; the readiness flag is consistent with
    the collected window count; the replay gate stays locked; nothing is advanced; and every
    capability flag is False."""
    failures: list = []
    if not isinstance(record, dict):
        return {"valid": False, "failures": ["record_not_a_dict"]}
    r = record

    if r.get("mode") != TRK_MODE:
        failures.append("mode_not_research_only")
    if r.get("is_tracker_only") is not True:
        failures.append("not_tracker_only")
    if r.get("read_only") is not True:
        failures.append("not_read_only")

    # thresholds single-sourced (untampered)
    if r.get("required_windows") != REQUIRED_WINDOWS:
        failures.append("required_windows_tampered")
    if r.get("required_decision_dates") != REQUIRED_DECISION_DATES:
        failures.append("required_decision_dates_tampered")
    if r.get("preferred_actionable_labels") != PREFERRED_ACTIONABLE_LABELS:
        failures.append("preferred_actionable_labels_tampered")

    # readiness consistent with the window count
    n = r.get("collected_windows")
    if not isinstance(n, int) or n < 0:
        failures.append("bad_collected_windows")
    else:
        expect_ready = (n >= REQUIRED_WINDOWS and n >= REQUIRED_DECISION_DATES)
        if r.get("ready_for_rereview") is not expect_ready:
            failures.append("readiness_inconsistent_with_count")
        if r.get("windows_remaining") != max(0, REQUIRED_WINDOWS - n):
            failures.append("windows_remaining_inconsistent")

    # current state + locks
    if r.get("c22_state") != C22_STATE:
        failures.append("c22_state_wrong")
    if r.get("replay_locked") is not True:
        failures.append("replay_not_locked")
    if r.get("next_human_action_when_ready") != NEXT_HUMAN_ACTION_WHEN_READY:
        failures.append("next_action_token_wrong")
    if r.get("advances_nothing") is not True:
        failures.append("must_advance_nothing")

    locks = r.get("scope_locks") or {}
    for key in ("no_execute", "no_file_io", "no_network_io", "no_data_fetch",
                "no_stage_data", "no_signum_connection", "no_mcp", "no_hyperliquid",
                "no_api_keys", "no_run_labels", "no_replay", "no_build_replay",
                "no_optimization", "no_modify_c22_rules", "no_start_c23", "no_reopen_c21",
                "no_scheduler_install", "no_scheduler_trigger", "no_order_logic",
                "no_paper_trading", "no_live_trading", "no_unlock_replay_gate"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if r.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
