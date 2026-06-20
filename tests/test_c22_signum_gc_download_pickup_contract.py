"""Tests for the Candidate #22 Signum GC download-pickup orchestration (contract + tool).

Proves the pickup validates drop-folder candidates with the importer rules and copies only
valid GC exports into the inbox; it never overwrites, never mutates JSON, is duplicate-safe
(same date not re-copied), ignores wrong/unrelated JSON, chains the existing import
automation + readiness watcher to report N/20 progress, and surfaces the review token only at
the threshold as a SUGGESTION ONLY (never auto-executed). No Signum login / fetch / browser /
API / MCP / network / credential storage. C22 stays HOLD_FOR_MORE_FROZEN_DATA_WINDOWS."""
from __future__ import annotations

import ast
import json
from pathlib import Path

import sparta_commander.c22_signum_gc_download_pickup_contract as pk
import sparta_commander.c22_signum_gc_local_export_importer_contract as imp
import sparta_commander.c22_signum_gc_collection_readiness_watcher_contract as rw
import tools.c22_signum_gc_download_pickup_once as pickup
import tools.c22_signum_gc_local_export_importer_once as importer
import tools.c22_signum_gc_collection_readiness_watcher_once as watcher


# ---- fixtures --------------------------------------------------------------

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


# ---- contract: classify drop candidate -------------------------------------

def test_classify_valid_duplicate_invalid():
    ok = pk.classify_drop_candidate(_valid_export("2026-06-21"), set())
    assert ok["verdict"] == "PICKUP_OK" and ok["should_pickup"] is True
    assert ok["inbox_filename"] == "gc_crypto_trendradar_daily_20260621.json"
    dup = pk.classify_drop_candidate(_valid_export("2026-06-21"), {"2026-06-21"})
    assert dup["verdict"] == "PICKUP_DUPLICATE_WINDOW" and dup["should_pickup"] is False
    bad = dict(_valid_export("2026-06-21"))
    bad["results"][0]["detector"] = "tr"
    inv = pk.classify_drop_candidate(bad, set())
    assert inv["verdict"] == "PICKUP_IGNORED_INVALID" and inv["should_pickup"] is False


# ---- contract: chain summary + token suggestion only -----------------------

def test_summary_token_only_when_ready():
    not_ready = rw.build_readiness([{"filename": "a", "date": "2026-06-20", "valid": True}])
    s = pk.summarize_pickup_chain(0, [], not_ready)
    assert s["overall_status"] == "NOT_READY_COLLECTING"
    assert s["suggested_next_token"] is None
    assert pk.validate_pickup_chain(s)["valid"] is True

    ready = rw.build_readiness([{"filename": "w%d" % i, "date": "2026-06-%02d" % i,
                                 "valid": True} for i in range(1, 21)])
    s2 = pk.summarize_pickup_chain(0, [], ready)
    assert s2["overall_status"] == "READY_FOR_HUMAN_REVIEW"
    assert s2["suggested_next_token"] == (
        "HUMAN_APPROVED_C22_SIGNUM_GC_FROZEN_DATA_WINDOW_REVIEW")
    assert s2["auto_executes_token"] is False
    assert pk.validate_pickup_chain(s2)["valid"] is True


def test_tamper_surface_token_early_rejected():
    not_ready = rw.build_readiness([{"filename": "a", "date": "2026-06-20", "valid": True}])
    s = pk.summarize_pickup_chain(0, [], not_ready)
    bad = {**s, "suggested_next_token": rw.SUGGESTED_REVIEW_TOKEN}
    assert pk.validate_pickup_chain(bad)["valid"] is False
    bad2 = {**s, "auto_executes_token": True}
    assert pk.validate_pickup_chain(bad2)["valid"] is False


# ---- tool: end-to-end pickup -> import -> readiness over tmp dirs -----------

def _wire(tmp_path, monkeypatch):
    drop = tmp_path / "drop"
    inbox = tmp_path / "inbox"
    dataset = tmp_path / "dataset"
    for d in (drop, inbox, dataset):
        d.mkdir()
    monkeypatch.setattr(pickup, "DROP_FOLDER", drop)
    monkeypatch.setattr(pickup, "DROP_GLOB", "*trendradar*.json")
    monkeypatch.setattr(importer, "INBOX", inbox)
    monkeypatch.setattr(importer, "DEST", dataset)
    monkeypatch.setattr(watcher, "DATA_DIR", dataset)
    return drop, inbox, dataset


def test_tool_picks_up_valid_and_reports_progress(tmp_path, monkeypatch):
    drop, inbox, dataset = _wire(tmp_path, monkeypatch)
    # an arbitrarily-named valid GC download + an unrelated JSON
    blob = json.dumps(_valid_export("2026-06-21")).encode("utf-8")
    (drop / "trendradar (1).json").write_bytes(blob)
    (drop / "unrelated_trendradar_notes.json").write_text("{not json", encoding="utf-8")

    s = pickup.run_pickup_chain()
    assert s["picked_up"] == 1
    assert s["ignored_invalid"] == 1
    # copied into the dataset under the runDate name (via the chained importer)
    out = dataset / "gc_crypto_trendradar_daily_20260621.json"
    assert out.is_file()
    assert out.read_bytes() == blob            # never mutated
    assert s["readiness"]["collected_valid_windows"] == 1
    assert s["readiness"]["progress"] == "1/20"
    assert s["overall_status"] == "NOT_READY_COLLECTING"
    assert s["suggested_next_token"] is None


def test_tool_idempotent_no_overwrite_no_duplicate(tmp_path, monkeypatch):
    drop, inbox, dataset = _wire(tmp_path, monkeypatch)
    blob = json.dumps(_valid_export("2026-06-21")).encode("utf-8")
    (drop / "trendradar_export.json").write_bytes(blob)

    s1 = pickup.run_pickup_chain()
    assert s1["picked_up"] == 1
    out = dataset / "gc_crypto_trendradar_daily_20260621.json"
    first = out.read_bytes()

    # run 2: same drop file still present -> already collected -> no new copy/overwrite
    s2 = pickup.run_pickup_chain()
    assert s2["picked_up"] == 0
    assert s2["duplicates"] >= 1
    assert out.read_bytes() == first                  # destination untouched
    assert list(dataset.glob("*.json")) == [out]      # exactly one window, no dup


def test_tool_empty_drop_folder(tmp_path, monkeypatch):
    _wire(tmp_path, monkeypatch)
    monkeypatch.setattr(pickup, "DROP_FOLDER", tmp_path / "missing")
    s = pickup.run_pickup_chain()
    assert s["drop_scanned"] == 0
    assert s["overall_status"] == "NOT_READY_COLLECTING"


# ---- no login / fetch / browser / api / mcp / network / credential tokens ---

# actionable network/browser/credential CALL/IMPORT tokens. Descriptive words like
# "cookies"/"credentials" appear only in negated-safety prose + scope_locks keys (e.g.
# no_store_cookies, stores_cookies=False) and are excluded -- real storage/calls are
# precluded by the capability flags + the banned-imports check.
_FORBIDDEN_TOKENS = (
    "import requests", "from requests", "import ccxt", "from ccxt", "urlopen",
    "import websockets", "selenium", "playwright", "webdriver", ".login(",
    "get_trendradar", "api.binance", "place_order", "import keyring",
)


def test_no_login_fetch_browser_api_credential_tokens():
    for mod in (pk, pickup):
        src = Path(mod.__file__).read_text(encoding="utf-8")
        for tok in _FORBIDDEN_TOKENS:
            assert tok not in src, "%s: %s" % (Path(mod.__file__).name, tok)


# ---- capability flags + contract purity ------------------------------------

def test_capability_flags_and_state():
    not_ready = rw.build_readiness([{"filename": "a", "date": "2026-06-20", "valid": True}])
    s = pk.summarize_pickup_chain(0, [], not_ready)
    assert s["c22_state"] == "HOLD_FOR_MORE_FROZEN_DATA_WINDOWS"
    assert s["replay_locked"] is True
    for flag in pk._CAPABILITY_FLAGS_FALSE:
        assert s[flag] is False, flag
    for key, val in s["scope_locks"].items():
        assert val is True, key


def test_contract_module_purity():
    src = Path(pk.__file__).read_text(encoding="utf-8")
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "open(",
                 "subprocess", "Popen", "urlopen", "json.load", "read_text",
                 "read_bytes", "glob(", "os.environ", "import os"):
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
