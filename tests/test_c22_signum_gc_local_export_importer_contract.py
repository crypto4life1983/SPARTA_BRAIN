"""Tests for the Candidate #22 Signum GC local export importer (contract + tool).

Proves: a valid export imports (IMPORT_OK) with a runDate-derived destination filename; a
second file for the same date is DUPLICATE_WINDOW (no overwrite); structurally invalid files
(wrong detector, wrong assetClass, missing gc fields, <50 rows, missing marketRank/
cmcRefPriceUsd) are INVALID and not imported; the JSON contents are never mutated (byte
copy); the tool writes only into the dataset folder via tmp dirs (never the real one); the
imported file is SHA-reported; and the contract/tool carry no network/API/Signum/MCP/
trading/scheduler tokens. C22 stays HOLD_FOR_MORE_FROZEN_DATA_WINDOWS."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

import sparta_commander.c22_signum_gc_local_export_importer_contract as imp
import sparta_commander.c22_signum_gc_data_collection_tracker_contract as trk
import tools.c22_signum_gc_local_export_importer_once as runner


# ---- fixtures: a minimal-but-complete valid parsed export ------------------

def _candle(c, h, trend="Green", upper=10.0, filt=8.0, date="2026-06-21"):
    return {"ohlc": {"o": c, "h": h, "l": c - 1, "c": c},
            "gc": {"lower": filt - 1, "trend": trend, "upper": upper, "filter": filt},
            "date": date, "volume": 1000.0}


def _row(symbol, rank, run_date="2026-06-21"):
    return {"symbol": symbol, "marketRank": rank, "marketCap": 1e9 / rank,
            "detector": "gc", "assetClass": "crypto", "runDate": run_date,
            "indicators": {"cmcRefPriceUsd": 5.0,
                           "data": [_candle(5.0, 5.5), _candle(6.0, 6.5)]}}


def _valid_parsed(run_date="2026-06-21", total=50, n=3):
    return {"limited": False, "total": total,
            "results": [_row("SYM%d" % i, i, run_date) for i in range(1, n + 1)]}


# ---- valid import ----------------------------------------------------------

def test_valid_import_decision():
    d = imp.build_import_decision(_valid_parsed("2026-06-21"), already_collected_dates=set())
    assert d["verdict"] == imp.VERDICT_IMPORT_OK
    assert d["structurally_valid"] is True
    assert d["run_date"] == "2026-06-21"
    assert d["destination_filename"] == "gc_crypto_trendradar_daily_20260621.json"
    assert d["should_import"] is True
    assert imp.validate_import_decision(d)["valid"] is True


# ---- duplicate window (date already collected) -----------------------------

def test_duplicate_window_decision():
    d = imp.build_import_decision(_valid_parsed("2026-06-20"),
                                  already_collected_dates={"2026-06-20"})
    assert d["verdict"] == imp.VERDICT_DUPLICATE
    assert d["should_import"] is False
    assert imp.validate_import_decision(d)["valid"] is True


# ---- invalid: wrong detector / assetClass / missing fields / <50 -----------

def test_wrong_detector_is_invalid():
    p = _valid_parsed()
    p["results"][0]["detector"] = "tr"
    d = imp.build_import_decision(p, set())
    assert d["verdict"] == imp.VERDICT_INVALID
    assert "all_detector_gc" in d["reasons"]
    assert d["should_import"] is False


def test_wrong_asset_class_is_invalid():
    p = _valid_parsed()
    p["results"][1]["assetClass"] = "equity"
    d = imp.build_import_decision(p, set())
    assert d["verdict"] == imp.VERDICT_INVALID
    assert "all_asset_class_crypto" in d["reasons"]


def test_missing_gc_fields_is_invalid():
    p = _valid_parsed()
    p["results"][0]["indicators"]["data"][-1]["gc"].pop("filter")
    d = imp.build_import_decision(p, set())
    assert d["verdict"] == imp.VERDICT_INVALID
    assert "gc_trend_upper_filter_present" in d["reasons"]


def test_too_few_rows_is_invalid():
    p = _valid_parsed(total=10, n=2)   # total < 50 and only 2 rows
    d = imp.build_import_decision(p, set())
    assert d["verdict"] == imp.VERDICT_INVALID
    assert "has_50_rows" in d["reasons"]


def test_missing_market_rank_and_cmc_is_invalid():
    p = _valid_parsed()
    p["results"][0].pop("marketRank")
    p["results"][1]["indicators"].pop("cmcRefPriceUsd")
    d = imp.build_import_decision(p, set())
    assert d["verdict"] == imp.VERDICT_INVALID
    assert "market_rank_present" in d["reasons"]
    assert "cmc_ref_price_usd_present" in d["reasons"]


def test_mixed_run_dates_is_invalid():
    p = _valid_parsed()
    p["results"][0]["runDate"] = "2026-06-21"
    p["results"][1]["runDate"] = "2026-06-22"
    d = imp.build_import_decision(p, set())
    assert d["verdict"] == imp.VERDICT_INVALID


# ---- tool: real byte copy into a tmp dataset dir, never overwrites ---------

def test_tool_imports_and_never_overwrites(tmp_path, monkeypatch):
    inbox = tmp_path / "inbox"
    dest = tmp_path / "dest"
    inbox.mkdir()
    dest.mkdir()
    monkeypatch.setattr(runner, "INBOX", inbox)
    monkeypatch.setattr(runner, "DEST", dest)

    blob = json.dumps(_valid_parsed("2026-06-21")).encode("utf-8")
    src = inbox / "gc_crypto_trendradar_daily_anything.json"
    src.write_bytes(blob)

    res1 = runner.import_one(src, runner._already_collected_dates())
    assert res1["imported"] is True
    out = dest / "gc_crypto_trendradar_daily_20260621.json"
    assert out.is_file()
    # byte-identical copy (JSON never mutated)
    assert out.read_bytes() == blob
    assert res1["sha256"] == hashlib.sha256(blob).hexdigest()

    # a second file for the SAME date must NOT overwrite -> DUPLICATE
    src2 = inbox / "gc_crypto_trendradar_daily_copy.json"
    src2.write_bytes(json.dumps(_valid_parsed("2026-06-21")).encode("utf-8"))
    res2 = runner.import_one(src2, runner._already_collected_dates())
    assert res2["imported"] is False
    assert res2["verdict"] == imp.VERDICT_DUPLICATE
    assert out.read_bytes() == blob   # original untouched


def test_tool_empty_inbox(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, "INBOX", tmp_path / "missing_inbox")
    assert runner.main() == 0


# ---- tracker compatibility: imported filename is counted as a window -------

def test_imported_filename_is_tracked_window():
    # the importer's destination filename is exactly what the tracker counts as a window
    fname = imp.derive_destination_filename("2026-06-21")
    assert trk._date_from_filename(fname) == "2026-06-21"
    status = trk.build_collection_status(
        ["gc_crypto_trendradar_daily.json", fname])
    assert status["collected_windows"] == 2   # bootstrap (06-20) + imported (06-21)


# ---- no network / API / Signum / trading / scheduler tokens ----------------

_FORBIDDEN_TOKENS = (
    "import requests", "from requests", "import ccxt", "from ccxt", "urlopen",
    "import socket", "schtasks", "Register-ScheduledTask", "ScheduledTaskTrigger",
    "BackgroundScheduler", "place_order", "create_order", "api.binance", "MetaTrader",
    "get_trendradar", "import websockets",
)


def test_no_network_api_trading_scheduler_tokens():
    for mod in (imp, runner):
        src = Path(mod.__file__).read_text(encoding="utf-8")
        for tok in _FORBIDDEN_TOKENS:
            assert tok not in src, "%s: %s" % (Path(mod.__file__).name, tok)


# ---- capability flags + module purity (the pure contract) ------------------

def test_capability_flags_and_state():
    d = imp.build_import_decision(_valid_parsed(), set())
    assert d["c22_state"] == "HOLD_FOR_MORE_FROZEN_DATA_WINDOWS"
    assert d["replay_locked"] is True
    for flag in imp._CAPABILITY_FLAGS_FALSE:
        assert d[flag] is False, flag
    for key, val in d["scope_locks"].items():
        assert val is True, key


def test_contract_module_purity():
    src = Path(imp.__file__).read_text(encoding="utf-8")
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
