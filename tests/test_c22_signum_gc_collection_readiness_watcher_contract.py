"""Tests for the Candidate #22 Signum GC collection readiness watcher (contract + tool).

Proves the watcher counts VALID distinct frozen GC windows, reports N/20 progress, stays
NOT_READY_COLLECTING below the threshold (no token surfaced), flips to READY_FOR_HUMAN_REVIEW
at the threshold surfacing the EXACT token HUMAN_APPROVED_C22_SIGNUM_GC_FROZEN_DATA_WINDOW_
REVIEW, NEVER auto-executes the token / auto-runs labels review / auto-runs replay, ignores
invalid windows, dedupes by date, fetches nothing (no Signum/GC/API/MCP/browser/network), and
keeps C22 HOLD with replay locked."""
from __future__ import annotations

import ast
import json
from pathlib import Path

import sparta_commander.c22_signum_gc_collection_readiness_watcher_contract as rw
import tools.c22_signum_gc_collection_readiness_watcher_once as watcher


def _facts(n_valid, *, invalid=0, dup_dates=False):
    out = []
    for i in range(1, n_valid + 1):
        d = "2026-06-%02d" % i if not dup_dates else "2026-06-20"
        out.append({"filename": "gc_crypto_trendradar_daily_2026%02d.json" % i,
                    "date": d, "valid": True, "reasons": []})
    for j in range(invalid):
        out.append({"filename": "bad_%d.json" % j, "date": "2026-07-%02d" % (j + 1),
                    "valid": False, "reasons": ["all_detector_gc"]})
    return out


# ---- progress + not-ready below threshold ----------------------------------

def test_not_ready_below_threshold():
    s = rw.build_readiness(_facts(1))
    assert s["status"] == "NOT_READY_COLLECTING"
    assert s["collected_valid_windows"] == 1
    assert s["progress"] == "1/20"
    assert s["windows_remaining"] == 19
    assert s["ready"] is False
    assert s["suggested_next_token"] is None    # token NOT surfaced yet
    assert rw.validate_readiness(s)["valid"] is True


def test_progress_counts_distinct_valid_dates():
    s = rw.build_readiness(_facts(5))
    assert s["progress"] == "5/20"
    assert s["collected_valid_windows"] == 5
    # duplicate dates collapse to one window
    sd = rw.build_readiness(_facts(5, dup_dates=True))
    assert sd["collected_valid_windows"] == 1


def test_invalid_windows_not_counted():
    s = rw.build_readiness(_facts(2, invalid=3))
    assert s["collected_valid_windows"] == 2
    assert len(s["invalid_windows"]) == 3
    assert rw.validate_readiness(s)["valid"] is True


# ---- ready at threshold surfaces the exact token ---------------------------

def test_ready_at_threshold_surfaces_token():
    s = rw.build_readiness(_facts(20))
    assert s["status"] == "READY_FOR_HUMAN_REVIEW"
    assert s["progress"] == "20/20"
    assert s["ready"] is True
    assert s["suggested_next_token"] == (
        "HUMAN_APPROVED_C22_SIGNUM_GC_FROZEN_DATA_WINDOW_REVIEW")
    assert rw.validate_readiness(s)["valid"] is True
    # also ready when above threshold
    assert rw.build_readiness(_facts(22))["status"] == "READY_FOR_HUMAN_REVIEW"


# ---- the token is a suggestion only, never auto-executed -------------------

def test_token_is_suggestion_only_never_executed():
    s = rw.build_readiness(_facts(20))
    assert s["is_suggestion_only"] is True
    assert s["token_is_suggestion_for_human_to_paste"] is True
    assert s["auto_executes_token"] is False
    for flag in ("auto_runs_labels_review", "auto_runs_replay", "auto_sends_token",
                 "auto_executes_token", "runs_labels", "runs_replay", "fetches_data",
                 "connects_signum", "uses_mcp", "uses_browser", "calls_api"):
        assert s[flag] is False, flag


# ---- anti-tamper: cannot fake READY or surface token early -----------------

def test_tamper_rejected():
    not_ready = rw.build_readiness(_facts(3))
    # force READY on a sub-threshold count
    bad = {**not_ready, "status": "READY_FOR_HUMAN_REVIEW", "ready": True,
           "suggested_next_token": rw.SUGGESTED_REVIEW_TOKEN}
    assert rw.validate_readiness(bad)["valid"] is False
    # surface token while not ready
    bad2 = {**not_ready, "suggested_next_token": rw.SUGGESTED_REVIEW_TOKEN}
    assert rw.validate_readiness(bad2)["valid"] is False
    # claim auto-execute
    bad3 = {**not_ready, "auto_executes_token": True}
    assert rw.validate_readiness(bad3)["valid"] is False


# ---- capability flags + state ----------------------------------------------

def test_capability_flags_and_state():
    s = rw.build_readiness(_facts(1))
    assert s["c22_state"] == "HOLD_FOR_MORE_FROZEN_DATA_WINDOWS"
    assert s["replay_locked"] is True
    for flag in rw._CAPABILITY_FLAGS_FALSE:
        assert s[flag] is False, flag
    for key, val in s["scope_locks"].items():
        assert val is True, key


# ---- tool: read-only scan over a tmp dataset dir ---------------------------

def _valid_export(run_date):
    def candle(c, h):
        return {"ohlc": {"o": c, "h": h, "l": c - 1, "c": c},
                "gc": {"lower": 7.0, "trend": "Green", "upper": 10.0, "filter": 8.0},
                "date": run_date, "volume": 1000.0}
    return {"limited": False, "total": 50,
            "results": [{"symbol": "S%d" % i, "marketRank": i, "marketCap": 1e9 / i,
                         "detector": "gc", "assetClass": "crypto", "runDate": run_date,
                         "indicators": {"cmcRefPriceUsd": 5.0,
                                        "data": [candle(5.0, 5.5), candle(6.0, 6.5)]}}
                        for i in range(1, 4)]}


def test_tool_scans_and_reports(tmp_path, monkeypatch):
    d = tmp_path / "dataset"
    d.mkdir()
    monkeypatch.setattr(watcher, "DATA_DIR", d)
    (d / "gc_crypto_trendradar_daily_20260621.json").write_text(
        json.dumps(_valid_export("2026-06-21")), encoding="utf-8")
    (d / "gc_crypto_trendradar_daily_20260622.json").write_text(
        json.dumps(_valid_export("2026-06-22")), encoding="utf-8")
    # a malformed file is ignored / counted invalid
    (d / "gc_crypto_trendradar_daily_20260623.json").write_text("{not json", encoding="utf-8")

    s = watcher.build_status()
    assert s["collected_valid_windows"] == 2
    assert s["progress"] == "2/20"
    assert s["status"] == "NOT_READY_COLLECTING"
    assert any(w["filename"] == "gc_crypto_trendradar_daily_20260623.json"
               for w in s["invalid_windows"])


def test_tool_empty_dataset(tmp_path, monkeypatch):
    monkeypatch.setattr(watcher, "DATA_DIR", tmp_path / "missing")
    s = watcher.build_status()
    assert s["collected_valid_windows"] == 0
    assert s["status"] == "NOT_READY_COLLECTING"


# ---- no network / Signum / API / MCP / browser tokens ----------------------

_FORBIDDEN_TOKENS = (
    "import requests", "from requests", "import ccxt", "from ccxt", "urlopen",
    "import socket", "import websockets", "selenium", "playwright", "webdriver",
    "get_trendradar", "api.binance", "place_order",
)


def test_no_network_signum_api_browser_tokens():
    for mod in (rw, watcher):
        src = Path(mod.__file__).read_text(encoding="utf-8")
        for tok in _FORBIDDEN_TOKENS:
            assert tok not in src, "%s: %s" % (Path(mod.__file__).name, tok)


def test_contract_module_purity():
    src = Path(rw.__file__).read_text(encoding="utf-8")
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch(", "open(", "subprocess", "Popen", "urlopen",
                 "json.load", "read_text", "read_bytes", "glob("):
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
