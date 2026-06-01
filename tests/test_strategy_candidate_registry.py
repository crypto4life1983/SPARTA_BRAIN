"""Tests for tools/strategy_candidate_registry.py (Candidate Registry v1).

Pure stdlib + pytest. All builds run against a synthetic temp repo root so the
real reports/ tree is never touched. Asserts the v1 safety contract (research-
only, stdlib only, no network/broker imports, pinned-False flags), graceful
handling of missing reports, deterministic output, conservative classification
(never STRONG without explicit support), and gitignore correctness.
"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]
_TOOLS_DIR = _REPO_ROOT / "tools"
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))

import strategy_candidate_registry as scr  # noqa: E402

TOOL_FILE = _TOOLS_DIR / "strategy_candidate_registry.py"


# --- helpers ---------------------------------------------------------------

def _make_dir_report(repo_root: Path, name: str, payload: dict | None = None) -> None:
    p = repo_root / scr.AGENTIC_REPORTS_REL / name
    p.mkdir(parents=True, exist_ok=True)
    if payload is not None:
        (p / "report.json").write_text(json.dumps(payload), encoding="utf-8")


def _make_file_report(repo_root: Path, name: str, content: str = "") -> None:
    p = repo_root / scr.AGENTIC_REPORTS_REL / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


# --- tests -----------------------------------------------------------------

def test_build_with_missing_reports(tmp_path):
    # No agentic_factory dir; tool must seed with defaults and not crash.
    payload = scr.generate(tmp_path)
    assert payload["candidate_count"] == len(scr.SEED_LANES)
    assert any("missing:" in w for w in payload["warnings"])
    # Every seed lane present.
    ids = {c["candidate_id"] for c in payload["candidates"]}
    assert {"crypto_d1_protocol", "crypto_4h_protocol", "nq_es_futures_trend",
           "donchian_variants", "vol_confirmed_trend_continuation",
           "arbitrage_research_protocol", "data_qa_freeze",
           "jarvis_automation", "strategy_factory_infra"}.issubset(ids)
    # With no reports, every candidate is IDEA / NONE.
    for c in payload["candidates"]:
        assert c["status"] == "IDEA"
        assert c["evidence_level"] == "NONE"


def test_build_with_sample_reports(tmp_path):
    # Seed enough reports to exercise classifier branches.
    _make_dir_report(tmp_path, "crypto_d14_lane_closeout_and_next_roadmap")
    _make_dir_report(tmp_path, "crypto_d11_crash_candle_is_baseline")
    _make_dir_report(tmp_path, "s29_d4_failed_breakout_reversal_is_baseline")
    _make_dir_report(tmp_path, "s23_d18_donchian_watch_closeout_memo")
    _make_dir_report(tmp_path, "crypto_d4_first_strategy_spec")
    _make_file_report(tmp_path, "data_quality_nq_c0_2013_20260529_210942.md")
    payload = scr.generate(tmp_path)
    by_id = {c["candidate_id"]: c for c in payload["candidates"]}
    # crypto_d1 lane saw closeout + baseline + spec -> PARKED wins (closeout).
    assert by_id["crypto_d1_protocol"]["status"] == "PARKED"
    # donchian lane saw a closeout memo -> PARKED.
    assert by_id["donchian_variants"]["status"] == "PARKED"
    # vol_confirmed lane has no reports -> still IDEA.
    assert by_id["vol_confirmed_trend_continuation"]["status"] == "IDEA"
    # nq/es lane picked up a data_quality_* file -> at least IDEA/MIXED.
    assert by_id["nq_es_futures_trend"]["status"] in ("IDEA", "ACTIVE")


def test_failed_reports_classify_as_failed(tmp_path):
    _make_dir_report(tmp_path, "crypto_d2_failed_test_inventory")
    payload = scr.generate(tmp_path)
    by_id = {c["candidate_id"]: c for c in payload["candidates"]}
    assert by_id["crypto_d1_protocol"]["status"] == "FAILED"
    assert by_id["crypto_d1_protocol"]["evidence_level"] == "WEAK"
    assert by_id["crypto_d1_protocol"]["failure_reason"] is not None


def test_never_marked_strong_automatically(tmp_path):
    # Even with many baseline / oos_result reports, evidence never reaches STRONG.
    for n in (
        "crypto_d6_codr1_is_baseline", "crypto_d11_crash_candle_is_baseline",
        "crypto_d13_crash_candle_oos_result", "crypto_d12_crash_candle_oos_protocol",
    ):
        _make_dir_report(tmp_path, n)
    payload = scr.generate(tmp_path)
    for c in payload["candidates"]:
        assert c["evidence_level"] != "STRONG", f"{c['candidate_id']} marked STRONG"


def test_candidate_schema_keys_present(tmp_path):
    payload = scr.generate(tmp_path)
    for c in payload["candidates"]:
        for k in scr.REQUIRED_CANDIDATE_KEYS:
            assert k in c, f"{c.get('candidate_id')}: missing {k}"
        assert c["status"] in scr.VALID_STATUSES
        assert c["evidence_level"] in scr.VALID_EVIDENCE
        assert c["safety_level"] == "research_only"


def test_validate_passes_after_build(tmp_path):
    scr.generate(tmp_path)
    ok, errs = scr.validate(tmp_path)
    assert ok, errs


def test_validate_detects_missing(tmp_path):
    ok, errs = scr.validate(tmp_path)
    assert not ok
    assert any("missing" in e for e in errs)


def test_validate_detects_strong_evidence_tamper(tmp_path):
    scr.generate(tmp_path)
    jpath = tmp_path / scr.OUTPUT_DIR_REL / scr.OUTPUT_JSON
    data = json.loads(jpath.read_text(encoding="utf-8"))
    data["candidates"][0]["evidence_level"] = "STRONG"
    jpath.write_text(json.dumps(data), encoding="utf-8")
    ok, errs = scr.validate(tmp_path)
    assert not ok
    assert any("STRONG" in e for e in errs)


def test_validate_detects_unpinned_safety_flag(tmp_path):
    scr.generate(tmp_path)
    jpath = tmp_path / scr.OUTPUT_DIR_REL / scr.OUTPUT_JSON
    data = json.loads(jpath.read_text(encoding="utf-8"))
    data["safety_flags"]["live_trading_enabled"] = True
    jpath.write_text(json.dumps(data), encoding="utf-8")
    ok, errs = scr.validate(tmp_path)
    assert not ok
    assert any("live_trading_enabled" in e for e in errs)


def test_deterministic_across_two_builds(tmp_path):
    _make_dir_report(tmp_path, "crypto_d14_lane_closeout_and_next_roadmap")
    _make_dir_report(tmp_path, "s23_d10_2013_donchian_baseline")
    p1 = scr.generate(tmp_path)
    p2 = scr.generate(tmp_path)
    # generated_at moves; everything else must match.
    for k in ("candidate_count", "status_counts", "evidence_counts", "candidates",
             "input_inventory", "warnings"):
        assert p1[k] == p2[k], f"non-deterministic field: {k}"


def test_only_writes_inside_output_folder(tmp_path):
    scr.generate(tmp_path)
    written = sorted(p.relative_to(tmp_path).as_posix() for p in tmp_path.rglob("*") if p.is_file())
    for w in written:
        # Build may create the (empty) AGENTIC_REPORTS_REL directory if a test pre-seeds it,
        # but it must never write *files* outside OUTPUT_DIR_REL.
        assert w.startswith(scr.OUTPUT_DIR_REL), f"file written outside output folder: {w}"


def test_markdown_is_human_readable(tmp_path):
    scr.generate(tmp_path)
    md = (tmp_path / scr.OUTPUT_DIR_REL / scr.OUTPUT_MD).read_text(encoding="utf-8")
    assert "# Strategy Candidate Registry v1" in md
    assert "## Status counts" in md
    assert "## Candidates" in md
    # Every seed lane appears in the table.
    for seed in scr.SEED_LANES:
        assert seed["candidate_id"] in md


def test_runtime_output_folder_is_gitignored():
    gi = (_REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "reports/strategy_factory_routines/candidate_registry/" in gi


def test_no_network_or_broker_imports_in_source():
    src = TOOL_FILE.read_text(encoding="utf-8")
    forbidden = (
        "import requests", "from requests",
        "import urllib", "from urllib",
        "import http", "from http",
        "import socket", "import ssl",
        "import tiingo", "from tiingo",
        "import ccxt", "from ccxt",
        "import alpaca", "from alpaca",
        "import binance", "from binance",
        "import dotenv", "from dotenv",
        "import subprocess", "from subprocess",
        "import os\n", "import os ",
        "os.environ", "getenv",
        "urlopen", "api.telegram.org",
    )
    for tok in forbidden:
        assert tok not in src, f"forbidden token in source: {tok!r}"


def test_only_stdlib_imports():
    tree = ast.parse(TOOL_FILE.read_text(encoding="utf-8"))
    stdlib_ok = {
        "argparse", "json", "re", "datetime", "pathlib", "typing", "__future__",
    }
    seen = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                seen.add(n.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            mod = (node.module or "").split(".")[0]
            seen.add(mod)
    extra = seen - stdlib_ok
    assert not extra, f"unexpected imports: {extra}"


def test_cli_build_show_validate(tmp_path):
    assert scr.main(["build", "--repo-root", str(tmp_path)]) == 0
    assert scr.main(["show", "--repo-root", str(tmp_path)]) == 0
    assert scr.main(["validate", "--repo-root", str(tmp_path)]) == 0
