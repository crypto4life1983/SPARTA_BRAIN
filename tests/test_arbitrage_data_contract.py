"""Bundle 5 — Arbitrage Data Contract v1 tests (research-only).

Pure stdlib + pytest. Asserts:
  * data_contract.json exists and validates
  * the five execution / fetch / connection flags are pinned False
  * all required top-level sections are present
  * all five required arbitrage categories are present with required fields
  * pure-arbitrage / statistical-relative-value distinction is preserved
  * no profitability claim, no live-readiness claim, no fetch claim
  * the validator catches tampered safety flags
  * the validator catches a missing required category
  * the validator catches a forbidden phrase in markdown
  * the validator tool is stdlib-only and forbids network/broker/exchange imports
  * the Bundle-4 arbitrage protocol validator still passes
  * the candidate registry builds after the data contract exists and arbitrage
    stays IDEA (never ACTIVE, never STRONG)
  * the next-bundle generator still validates
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

import arbitrage_data_contract_check as adc  # noqa: E402
import arbitrage_protocol_check as apc       # noqa: E402
import strategy_candidate_registry as scr    # noqa: E402
import strategy_next_bundle as snb           # noqa: E402

TOOL_FILE = _TOOLS_DIR / "arbitrage_data_contract_check.py"
CONTRACT_JSON_PATH = _REPO_ROOT / adc.CONTRACT_DIR_REL / adc.CONTRACT_JSON
CONTRACT_MD_PATH = _REPO_ROOT / adc.CONTRACT_DIR_REL / adc.CONTRACT_MD


# --- existence + validation ---------------------------------------------- #

def test_data_contract_json_exists():
    assert CONTRACT_JSON_PATH.exists(), f"missing: {CONTRACT_JSON_PATH}"


def test_data_contract_md_exists():
    assert CONTRACT_MD_PATH.exists(), f"missing: {CONTRACT_MD_PATH}"


def test_validator_passes_on_committed_contract():
    ok, errs = adc.validate(_REPO_ROOT)
    assert ok, errs


def test_execution_flags_all_false():
    data = json.loads(CONTRACT_JSON_PATH.read_text(encoding="utf-8"))
    for flag in adc.MUST_BE_FALSE_FLAGS:
        assert data.get(flag) is False, f"{flag} must be False"
    assert data.get("research_only") is True


def test_required_top_level_sections_present():
    data = json.loads(CONTRACT_JSON_PATH.read_text(encoding="utf-8"))
    for k in adc.REQUIRED_TOP_LEVEL_KEYS:
        assert k in data, f"missing top-level key: {k}"


def test_five_required_categories_present_and_well_formed():
    data = json.loads(CONTRACT_JSON_PATH.read_text(encoding="utf-8"))
    cats = data["supported_arbitrage_categories"]
    ids = [c.get("id") for c in cats if isinstance(c, dict)]
    for required_id in adc.REQUIRED_CATEGORY_IDS:
        assert required_id in ids, f"missing category id: {required_id}"
    for c in cats:
        for f in adc.REQUIRED_CATEGORY_FIELDS:
            assert f in c, f"category {c.get('id')!r}: missing field {f}"
        assert isinstance(c["data_needed"], list) and c["data_needed"]
        assert isinstance(c["category_specific_validity"], list) and c["category_specific_validity"]


def test_timestamp_requirements_present():
    data = json.loads(CONTRACT_JSON_PATH.read_text(encoding="utf-8"))
    ts = data["timestamp_requirements"]
    for k in ("primary_clock", "accepted_timestamp_fields", "max_skew_allowed",
             "stale_quote_rule", "alignment_rules", "timezone_normalization",
             "row_invalidity_criteria"):
        assert k in ts, f"timestamp_requirements missing: {k}"


def test_fee_funding_slippage_depth_requirements_present():
    data = json.loads(CONTRACT_JSON_PATH.read_text(encoding="utf-8"))
    fr = data["fee_requirements"]
    for k in ("maker_fee_bps", "taker_fee_bps", "withdrawal_fees", "network_fees",
             "fee_as_pnl_line"):
        assert k in fr, f"fee_requirements missing: {k}"
    fnd = data["funding_requirements"]
    for k in ("applies_to", "fields", "history_horizon"):
        assert k in fnd, f"funding_requirements missing: {k}"
    lr = data["liquidity_requirements"]
    for k in ("minimum_notional_depth_at_touch", "depth_at_size_calculation",
             "volume_filter", "stale_order_book_filter"):
        assert k in lr, f"liquidity_requirements missing: {k}"
    lat = data["latency_requirements"]
    for k in ("publish_to_recv_latency_estimate_per_venue",
             "decision_to_fill_latency", "no_zero_latency_assumption"):
        assert k in lat, f"latency_requirements missing: {k}"


def test_pure_vs_statistical_distinction_preserved():
    data = json.loads(CONTRACT_JSON_PATH.read_text(encoding="utf-8"))
    rv = next(c for c in data["supported_arbitrage_categories"]
             if c.get("id") == "statistical_relative_value")
    assert "NOT pure arbitrage" in rv["label"]
    md = CONTRACT_MD_PATH.read_text(encoding="utf-8")
    assert "NOT pure arbitrage" in md
    assert "RELATIVE_VALUE" in md
    assert "price gap is not profit" in md.lower() or "A price gap is **not** profit" in md
    assert "Apparent edge" in md


def test_no_profitability_or_fetch_claims():
    md = CONTRACT_MD_PATH.read_text(encoding="utf-8").lower()
    jsn = json.dumps(json.loads(CONTRACT_JSON_PATH.read_text(encoding="utf-8")),
                    ensure_ascii=False).lower()
    for phrase in adc.FORBIDDEN_PHRASES:
        assert phrase.lower() not in md, f"forbidden phrase in data_contract.md: {phrase!r}"
        assert phrase.lower() not in jsn, f"forbidden phrase in data_contract.json: {phrase!r}"


# --- validator failure modes --------------------------------------------- #

def _stage_tmp(tmp_path: Path):
    """Copy the real contract + md into a temp tree so we can tamper safely."""
    tmp_dir = tmp_path / adc.CONTRACT_DIR_REL
    tmp_dir.mkdir(parents=True, exist_ok=True)
    (tmp_dir / adc.CONTRACT_MD).write_text(CONTRACT_MD_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    data = json.loads(CONTRACT_JSON_PATH.read_text(encoding="utf-8"))
    return tmp_dir, data


def test_validator_detects_tampered_safety_flag(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["data_fetch_enabled"] = True
    (tmp_dir / adc.CONTRACT_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = adc.validate(tmp_path)
    assert not ok
    assert any("data_fetch_enabled" in e for e in errs)


def test_validator_detects_missing_required_category(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["supported_arbitrage_categories"] = [
        c for c in data["supported_arbitrage_categories"] if c.get("id") != "triangular"
    ]
    (tmp_dir / adc.CONTRACT_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = adc.validate(tmp_path)
    assert not ok
    assert any("triangular" in e for e in errs)


def test_validator_detects_forbidden_phrase_in_md(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    (tmp_dir / adc.CONTRACT_JSON).write_text(json.dumps(data), encoding="utf-8")
    md = CONTRACT_MD_PATH.read_text(encoding="utf-8") + "\nNote: guaranteed profit.\n"
    (tmp_dir / adc.CONTRACT_MD).write_text(md, encoding="utf-8")
    ok, errs = adc.validate(tmp_path)
    assert not ok
    assert any("guaranteed profit" in e for e in errs)


# --- tool safety tests --------------------------------------------------- #

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
        assert tok not in src, f"forbidden token: {tok!r}"


def test_validator_cli_show_and_validate():
    assert adc.main(["validate", "--repo-root", str(_REPO_ROOT)]) == 0
    assert adc.main(["show", "--repo-root", str(_REPO_ROOT)]) == 0


# --- integration tests --------------------------------------------------- #

def test_arbitrage_protocol_v4_validator_still_passes():
    ok, errs = apc.validate(_REPO_ROOT)
    assert ok, errs


def test_candidate_registry_builds_after_contract_exists():
    payload = scr.generate(_REPO_ROOT)
    arb = next(c for c in payload["candidates"]
              if c["candidate_id"] == "arbitrage_research_protocol")
    # Lane stays IDEA — never ACTIVE, never STRONG, despite richer docs.
    assert arb["status"] == "IDEA", arb
    assert arb["evidence_level"] in ("NONE", "MIXED"), arb
    assert arb["evidence_level"] != "STRONG"
    # The data contract docs should now appear in source_reports too.
    assert "data_contract.md" in arb["source_reports"], arb["source_reports"]
    assert "data_contract.json" in arb["source_reports"], arb["source_reports"]
    # And the Bundle-4 protocol docs are still there.
    assert "protocol.md" in arb["source_reports"]


def test_next_bundle_generator_still_validates_after_contract():
    snb.generate(_REPO_ROOT)
    ok, errs = snb.validate(_REPO_ROOT)
    assert ok, errs
