"""Bundle 4 — Arbitrage Research Protocol v1 tests (research-only).

Pure stdlib + pytest. Asserts:
  * protocol.json exists and validates
  * the five execution-related flags are pinned False
  * all required top-level sections are present
  * all five required arbitrage categories are present and well-formed
  * pure-arbitrage / statistical-relative-value distinction is preserved
  * no profitability or live-readiness claims sneak in
  * the validator catches tampered safety flags
  * the validator tool is stdlib-only and forbids network/broker/exchange imports
  * the candidate registry builds after the protocol exists and arbitrage stays IDEA
  * the next bundle generator still validates
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

import arbitrage_protocol_check as apc  # noqa: E402
import strategy_candidate_registry as scr  # noqa: E402
import strategy_next_bundle as snb  # noqa: E402

TOOL_FILE = _TOOLS_DIR / "arbitrage_protocol_check.py"
PROTOCOL_JSON_PATH = _REPO_ROOT / apc.PROTOCOL_DIR_REL / apc.PROTOCOL_JSON
PROTOCOL_MD_PATH = _REPO_ROOT / apc.PROTOCOL_DIR_REL / apc.PROTOCOL_MD


# --- protocol document tests ---------------------------------------------- #

def test_protocol_json_exists():
    assert PROTOCOL_JSON_PATH.exists(), f"missing: {PROTOCOL_JSON_PATH}"


def test_protocol_md_exists():
    assert PROTOCOL_MD_PATH.exists(), f"missing: {PROTOCOL_MD_PATH}"


def test_validator_passes_on_committed_protocol():
    ok, errs = apc.validate(_REPO_ROOT)
    assert ok, errs


def test_execution_flags_all_false():
    data = json.loads(PROTOCOL_JSON_PATH.read_text(encoding="utf-8"))
    for flag in apc.MUST_BE_FALSE_FLAGS:
        assert data.get(flag) is False, f"{flag} must be False"
    assert data.get("research_only") is True


def test_required_sections_present():
    data = json.loads(PROTOCOL_JSON_PATH.read_text(encoding="utf-8"))
    for k in apc.REQUIRED_TOP_LEVEL_KEYS:
        assert k in data, f"missing top-level key: {k}"


def test_five_required_categories_present_and_well_formed():
    data = json.loads(PROTOCOL_JSON_PATH.read_text(encoding="utf-8"))
    categories = data.get("categories")
    assert isinstance(categories, list)
    ids = [c.get("id") for c in categories if isinstance(c, dict)]
    for required_id in apc.REQUIRED_CATEGORY_IDS:
        assert required_id in ids, f"missing category id: {required_id}"
    for c in categories:
        for field in apc.REQUIRED_CATEGORY_FIELDS:
            assert field in c, f"category {c.get('id')!r}: missing field {field}"


def test_pure_vs_statistical_distinction_preserved():
    data = json.loads(PROTOCOL_JSON_PATH.read_text(encoding="utf-8"))
    rv = next(c for c in data["categories"] if c.get("id") == "statistical_relative_value")
    # Self-labelled as NOT pure arbitrage:
    assert "NOT pure arbitrage" in rv["label"]
    # Markdown contains the same word discipline:
    md = PROTOCOL_MD_PATH.read_text(encoding="utf-8")
    assert "Pure arbitrage" in md
    assert "NOT pure arbitrage" in md
    assert "statistical_relative_value" in md
    # And the definitions section explicitly carries the apparent-edge != profit claim
    assert "Apparent edge" in md


def test_no_profitability_or_live_claims():
    md = PROTOCOL_MD_PATH.read_text(encoding="utf-8").lower()
    jsn = json.dumps(json.loads(PROTOCOL_JSON_PATH.read_text(encoding="utf-8")),
                    ensure_ascii=False).lower()
    for phrase in apc.FORBIDDEN_PHRASES:
        assert phrase.lower() not in md, f"forbidden phrase in protocol.md: {phrase!r}"
        assert phrase.lower() not in jsn, f"forbidden phrase in protocol.json: {phrase!r}"


def test_validator_detects_tampered_execution_flag(tmp_path):
    # Copy the real protocol to a temp tree, flip a flag, expect validate to fail.
    tmp_proto_dir = tmp_path / apc.PROTOCOL_DIR_REL
    tmp_proto_dir.mkdir(parents=True, exist_ok=True)
    data = json.loads(PROTOCOL_JSON_PATH.read_text(encoding="utf-8"))
    data["live_trading_enabled"] = True
    (tmp_proto_dir / apc.PROTOCOL_JSON).write_text(json.dumps(data), encoding="utf-8")
    # Also copy md so distinction-phrase check does not trip
    (tmp_proto_dir / apc.PROTOCOL_MD).write_text(PROTOCOL_MD_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    ok, errs = apc.validate(tmp_path)
    assert not ok
    assert any("live_trading_enabled" in e for e in errs)


def test_validator_detects_missing_required_category(tmp_path):
    tmp_proto_dir = tmp_path / apc.PROTOCOL_DIR_REL
    tmp_proto_dir.mkdir(parents=True, exist_ok=True)
    data = json.loads(PROTOCOL_JSON_PATH.read_text(encoding="utf-8"))
    # Drop the triangular category.
    data["categories"] = [c for c in data["categories"] if c.get("id") != "triangular"]
    (tmp_proto_dir / apc.PROTOCOL_JSON).write_text(json.dumps(data), encoding="utf-8")
    (tmp_proto_dir / apc.PROTOCOL_MD).write_text(PROTOCOL_MD_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    ok, errs = apc.validate(tmp_path)
    assert not ok
    assert any("triangular" in e for e in errs)


def test_validator_detects_forbidden_phrase(tmp_path):
    tmp_proto_dir = tmp_path / apc.PROTOCOL_DIR_REL
    tmp_proto_dir.mkdir(parents=True, exist_ok=True)
    data = json.loads(PROTOCOL_JSON_PATH.read_text(encoding="utf-8"))
    (tmp_proto_dir / apc.PROTOCOL_JSON).write_text(json.dumps(data), encoding="utf-8")
    md = PROTOCOL_MD_PATH.read_text(encoding="utf-8")
    md_bad = md + "\nNote: guaranteed profit available.\n"
    (tmp_proto_dir / apc.PROTOCOL_MD).write_text(md_bad, encoding="utf-8")
    ok, errs = apc.validate(tmp_path)
    assert not ok
    assert any("guaranteed profit" in e for e in errs)


# --- tool safety tests ---------------------------------------------------- #

def test_validator_tool_stdlib_only():
    tree = ast.parse(TOOL_FILE.read_text(encoding="utf-8"))
    stdlib_ok = {"argparse", "json", "pathlib", "__future__"}
    seen = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                seen.add(n.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            seen.add((node.module or "").split(".")[0])
    extra = seen - stdlib_ok
    assert not extra, f"unexpected imports: {extra}"


def test_validator_tool_no_network_or_broker_or_exchange_imports():
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
        assert tok not in src, f"forbidden token in validator source: {tok!r}"


def test_validator_cli_show_and_validate():
    # CLI smoke: both subcommands exit 0 on the committed protocol.
    assert apc.main(["validate", "--repo-root", str(_REPO_ROOT)]) == 0
    assert apc.main(["show", "--repo-root", str(_REPO_ROOT)]) == 0


# --- integration tests ---------------------------------------------------- #

def test_candidate_registry_builds_after_protocol_exists():
    payload = scr.generate(_REPO_ROOT)
    by_id = {c["candidate_id"]: c for c in payload["candidates"]}
    arb = by_id["arbitrage_research_protocol"]
    # Arbitrage stays IDEA (protocol/spec keyword) — never ACTIVE just because
    # docs exist. Evidence stays NONE; STRONG forbidden by registry.
    assert arb["status"] == "IDEA", arb
    assert arb["evidence_level"] in ("NONE", "MIXED"), arb
    assert arb["evidence_level"] != "STRONG"
    # The new protocol docs should now appear in source_reports.
    assert "protocol.md" in arb["source_reports"], arb["source_reports"]


def test_next_bundle_generator_still_validates_after_protocol():
    # Generate using the real repo; should still validate cleanly.
    snb.generate(_REPO_ROOT)
    ok, errs = snb.validate(_REPO_ROOT)
    assert ok, errs
