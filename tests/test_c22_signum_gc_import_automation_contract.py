"""Tests for the Candidate #22 Signum GC local import automation (contract + tool).

Proves the automation runs the existing importer against the approved inbox and reports one
clean status; it is IDEMPOTENT (a second run after import yields DUPLICATE_WINDOW with zero
new writes, no overwrite, no mutation); an empty inbox returns NO_NEW_EXPORT; a fresh valid
export returns IMPORTED; and neither the contract nor the tool carries any network / Signum /
MCP / API / fetch / labels / replay / scheduler-install token. C22 stays
HOLD_FOR_MORE_FROZEN_DATA_WINDOWS."""
from __future__ import annotations

import ast
import json
from pathlib import Path

import sparta_commander.c22_signum_gc_import_automation_contract as auto
import sparta_commander.c22_signum_gc_local_export_importer_contract as imp
import tools.c22_signum_gc_import_automation_once as autorun
import tools.c22_signum_gc_local_export_importer_once as importer


# ---- fixtures: minimal-but-complete valid export ---------------------------

def _candle(c, h, trend="Green", upper=10.0, filt=8.0, date="2026-06-21"):
    return {"ohlc": {"o": c, "h": h, "l": c - 1, "c": c},
            "gc": {"lower": filt - 1, "trend": trend, "upper": upper, "filter": filt},
            "date": date, "volume": 1000.0}


def _row(symbol, rank, run_date):
    return {"symbol": symbol, "marketRank": rank, "marketCap": 1e9 / rank,
            "detector": "gc", "assetClass": "crypto", "runDate": run_date,
            "indicators": {"cmcRefPriceUsd": 5.0,
                           "data": [_candle(5.0, 5.5), _candle(6.0, 6.5)]}}


def _valid(run_date, total=50, n=3):
    return {"limited": False, "total": total,
            "results": [_row("SYM%d" % i, i, run_date) for i in range(1, n + 1)]}


# ---- contract: status mapping ----------------------------------------------

def test_status_no_new_export_on_empty_scan():
    s = auto.summarize_automation_run(0, [])
    assert s["overall_status"] == "NO_NEW_EXPORT"
    assert s["new_imports"] == 0
    assert auto.validate_automation_summary(s)["valid"] is True


def test_status_imported():
    results = [{"imported": True, "verdict": imp.VERDICT_IMPORT_OK,
                "destination_filename": "gc_crypto_trendradar_daily_20260621.json",
                "run_date": "2026-06-21"}]
    s = auto.summarize_automation_run(1, results)
    assert s["overall_status"] == "IMPORTED"
    assert s["new_imports"] == 1
    assert s["imported_filenames"] == ["gc_crypto_trendradar_daily_20260621.json"]
    assert auto.validate_automation_summary(s)["valid"] is True


def test_status_duplicate_window():
    results = [{"imported": False, "verdict": imp.VERDICT_DUPLICATE,
                "run_date": "2026-06-20"}]
    s = auto.summarize_automation_run(1, results)
    assert s["overall_status"] == "DUPLICATE_WINDOW"
    assert s["new_imports"] == 0 and s["duplicates"] == 1
    assert auto.validate_automation_summary(s)["valid"] is True


def test_status_invalid_only():
    results = [{"imported": False, "verdict": imp.VERDICT_INVALID,
                "reasons": ["all_detector_gc"]}]
    s = auto.summarize_automation_run(1, results)
    assert s["overall_status"] == "INVALID_ONLY"
    assert auto.validate_automation_summary(s)["valid"] is True


# ---- anti-tamper: status must match counts ---------------------------------

def test_tamper_status_count_mismatch_rejected():
    s = auto.summarize_automation_run(0, [])
    assert auto.validate_automation_summary(
        {**s, "overall_status": "IMPORTED"})["valid"] is False
    s2 = auto.summarize_automation_run(1, [{"imported": True,
        "verdict": imp.VERDICT_IMPORT_OK, "destination_filename": "x.json",
        "run_date": "2026-06-21"}])
    assert auto.validate_automation_summary({**s2, "new_imports": 0})["valid"] is False


# ---- tool: end-to-end idempotency over a tmp inbox/dataset -----------------

def test_tool_idempotent_no_overwrite_no_mutation(tmp_path, monkeypatch):
    inbox = tmp_path / "inbox"
    dest = tmp_path / "dest"
    inbox.mkdir()
    dest.mkdir()
    # both the importer and (via it) the automation use these patched paths
    monkeypatch.setattr(importer, "INBOX", inbox)
    monkeypatch.setattr(importer, "DEST", dest)

    blob = json.dumps(_valid("2026-06-21")).encode("utf-8")
    (inbox / "gc_crypto_trendradar_daily_drop1.json").write_bytes(blob)

    # run 1 -> IMPORTED
    s1 = autorun.run_import_automation()
    assert s1["overall_status"] == "IMPORTED"
    assert s1["new_imports"] == 1
    out = dest / "gc_crypto_trendradar_daily_20260621.json"
    assert out.is_file()
    assert out.read_bytes() == blob          # byte-identical (no mutation)
    sha_after_run1 = out.read_bytes()

    # run 2 (same inbox, file still there) -> DUPLICATE_WINDOW, no new writes
    s2 = autorun.run_import_automation()
    assert s2["overall_status"] == "DUPLICATE_WINDOW"
    assert s2["new_imports"] == 0
    assert out.read_bytes() == sha_after_run1   # destination untouched (no overwrite)
    assert list(dest.glob("*.json")) == [out]   # no extra files created

    # run 3 with the inbox emptied -> NO_NEW_EXPORT
    (inbox / "gc_crypto_trendradar_daily_drop1.json").unlink()
    s3 = autorun.run_import_automation()
    assert s3["overall_status"] == "NO_NEW_EXPORT"


def test_tool_empty_inbox_no_new_export(tmp_path, monkeypatch):
    monkeypatch.setattr(importer, "INBOX", tmp_path / "missing")
    s = autorun.run_import_automation()
    assert s["overall_status"] == "NO_NEW_EXPORT"
    assert s["scanned"] == 0


# ---- capability + state ----------------------------------------------------

def test_capability_flags_and_state():
    s = auto.summarize_automation_run(0, [])
    assert s["c22_state"] == "HOLD_FOR_MORE_FROZEN_DATA_WINDOWS"
    assert s["replay_locked"] is True
    assert s["is_idempotent"] is True
    for flag in auto._CAPABILITY_FLAGS_FALSE:
        assert s[flag] is False, flag
    for key, val in s["scope_locks"].items():
        assert val is True, key


# ---- no network / Signum / MCP / API / fetch / scheduler-install tokens -----

_FORBIDDEN_TOKENS = (
    "import requests", "from requests", "import ccxt", "from ccxt", "urlopen",
    "import socket", "import websockets", "schtasks", "Register-ScheduledTask",
    "ScheduledTaskTrigger", "BackgroundScheduler", "place_order", "create_order",
    "api.binance", "MetaTrader", "get_trendradar", "mcp_call",
)


def test_no_network_signum_api_scheduler_tokens():
    for mod in (auto, autorun):
        src = Path(mod.__file__).read_text(encoding="utf-8")
        for tok in _FORBIDDEN_TOKENS:
            assert tok not in src, "%s: %s" % (Path(mod.__file__).name, tok)


# ---- contract module purity ------------------------------------------------

def test_contract_module_purity():
    src = Path(auto.__file__).read_text(encoding="utf-8")
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch(", "open(", "subprocess", "Popen", "urlopen",
                 "json.load", "read_text", "read_bytes", "glob("):
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
