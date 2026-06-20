"""Tests for the Candidate #22 Signum GC data-collection tracker contract.

Proves the tracker counts frozen daily GC export windows from discovered filenames, compares
them to the committed re-review thresholds (single-sourced from the labels-review contract:
20 / 20 / 30), surfaces the current C22 HOLD state + replay-locked + the next export date +
the re-review token, flips ready_for_rereview only when >= 20 windows exist, and exposes NO
Signum / MCP / API / data-fetch / trading / scheduler / replay capability. Pure: no file or
network I/O."""
from __future__ import annotations

import ast
from pathlib import Path

import sparta_commander.c22_signum_gc_data_collection_tracker_contract as trk
import sparta_commander.external_signum_trend_radar_gc_long_short_v1_real_candle_labels_review_contract as lr  # noqa: E501


# ---- thresholds single-sourced from the committed review contract ----------

def test_thresholds_single_sourced():
    assert trk.REQUIRED_WINDOWS == lr.MIN_FROZEN_DATA_WINDOWS_FOR_REPLAY == 20
    assert trk.REQUIRED_DECISION_DATES == lr.MIN_DISTINCT_DECISION_DATES_FOR_REPLAY == 20
    assert trk.PREFERRED_ACTIONABLE_LABELS == lr.MIN_ACTIONABLE_LABELS_FOR_REPLAY == 30
    assert trk.C22_STATE == "HOLD_FOR_MORE_FROZEN_DATA_WINDOWS"
    assert trk.NEXT_HUMAN_ACTION_WHEN_READY == (
        "HUMAN_STAGE_MORE_FROZEN_DAILY_TREND_RADAR_GC_WINDOWS_THEN_REREVIEW_C22_LABELS")


# ---- filename -> date extraction -------------------------------------------

def test_date_from_filename():
    assert trk._date_from_filename("gc_crypto_trendradar_daily.json") == "2026-06-20"
    assert trk._date_from_filename(
        "gc_crypto_trendradar_daily_20260621.json") == "2026-06-21"
    # non-export files are ignored
    assert trk._date_from_filename("c22_gc_real_candle_entry_labels_2026-06-20.json") is None
    assert trk._date_from_filename("readme.txt") is None
    assert trk._date_from_filename("gc_crypto_trendradar_daily_2026.json") is None


def test_next_calendar_date():
    assert trk.next_calendar_date("2026-06-20") == "2026-06-21"
    assert trk.next_calendar_date("2026-06-30") == "2026-07-01"   # month boundary
    assert trk.next_calendar_date("2026-12-31") == "2027-01-01"   # year boundary
    assert trk.next_calendar_date("not-a-date") is None


# ---- empty + single + multi window counts ----------------------------------

def test_empty_collection():
    s = trk.build_collection_status([])
    assert s["collected_windows"] == 0
    assert s["next_export_date"] == "2026-06-20"   # the first window date
    assert s["windows_remaining"] == 20
    assert s["ready_for_rereview"] is False
    assert trk.validate_collection_status(s)["valid"] is True


def test_single_window_today():
    s = trk.build_collection_status(["gc_crypto_trendradar_daily.json"])
    assert s["collected_windows"] == 1
    assert s["collected_decision_dates"] == ["2026-06-20"]
    assert s["latest_collected_date"] == "2026-06-20"
    assert s["next_export_date"] == "2026-06-21"
    assert s["windows_remaining"] == 19
    assert s["pct_complete"] == 5.0
    assert s["ready_for_rereview"] is False
    assert trk.validate_collection_status(s)["valid"] is True


def test_non_export_files_ignored():
    s = trk.build_collection_status([
        "gc_crypto_trendradar_daily.json", "detector_labels", "notes.md",
        "c22_gc_real_candle_entry_labels_2026-06-20.json"])
    assert s["collected_windows"] == 1


def test_ready_when_twenty_windows():
    names = ["gc_crypto_trendradar_daily.json"] + [
        "gc_crypto_trendradar_daily_202606%02d.json" % d for d in range(1, 20)]
    s = trk.build_collection_status(names)
    assert s["collected_windows"] == 20
    assert s["windows_remaining"] == 0
    assert s["pct_complete"] == 100.0
    assert s["ready_for_rereview"] is True
    assert trk.validate_collection_status(s)["valid"] is True


# ---- current state + capability safety -------------------------------------

def test_state_locks_and_capability_flags():
    s = trk.build_collection_status(["gc_crypto_trendradar_daily.json"])
    assert s["c22_state"] == "HOLD_FOR_MORE_FROZEN_DATA_WINDOWS"
    assert s["replay_locked"] is True
    assert s["advances_nothing"] is True
    for flag in trk._CAPABILITY_FLAGS_FALSE:
        assert s[flag] is False, flag
    for key, val in s["scope_locks"].items():
        assert val is True, key
    # explicitly: no signum / mcp / api / data-fetch / trading / scheduler / replay
    for flag in ("connects_signum", "uses_mcp", "accesses_hyperliquid", "calls_api",
                 "fetches_data", "runs_replay", "builds_replay", "runs_labels",
                 "installs_scheduler", "triggers_scheduler", "places_orders",
                 "live_trading", "paper_trading"):
        assert s[flag] is False, flag


# ---- anti-tamper validator -------------------------------------------------

def test_tamper_rejected():
    s = trk.build_collection_status(["gc_crypto_trendradar_daily.json"])
    assert trk.validate_collection_status({**s, "required_windows": 1})["valid"] is False
    assert trk.validate_collection_status(
        {**s, "ready_for_rereview": True})["valid"] is False
    assert trk.validate_collection_status({**s, "replay_locked": False})["valid"] is False
    assert trk.validate_collection_status({**s, "fetches_data": True})["valid"] is False
    assert trk.validate_collection_status({**s, "c22_state": "ADVANCE"})["valid"] is False


# ---- rendered sections surface the facts -----------------------------------

def test_render_markdown_and_html():
    s = trk.build_collection_status(["gc_crypto_trendradar_daily.json"])
    md = trk.render_collection_section_markdown(s)
    assert "C22 Signum GC data-collection tracker" in md
    assert "1 / 20" in md
    assert "2026-06-21" in md
    assert "HOLD_FOR_MORE_FROZEN_DATA_WINDOWS" in md
    html = trk.render_collection_section_html(s)
    assert "C22 Signum GC data-collection tracker" in html
    assert "2026-06-21" in html
    assert "<script" not in html.lower()


# ---- module purity (pure; datetime allowed but no clock read) --------------

def test_module_purity_no_io_no_clock_no_banned_imports():
    src = Path(trk.__file__).read_text(encoding="utf-8")
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch(", "open(", "subprocess", "Popen", "urlopen",
                 "glob(", ".now(", ".today(", ".utcnow(", "read_text", "read_bytes"):
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
