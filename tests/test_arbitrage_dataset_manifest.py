"""Bundle 6 — Arbitrage Dataset Manifest v1 tests (research-only).

Pure stdlib + pytest. Asserts:
  * dataset_manifest.json exists and validates
  * the six execution / fetch / connection / backtest flags are pinned False
  * all required top-level sections exist
  * all five required arbitrage categories present + per-category requirements
  * manifest_schema lists every required future manifest field
  * QA status model contains all 7 statuses
  * freeze rules exist and reference FROZEN
  * pure-vs-statistical distinction preserved
  * no profitability claim, no live-readiness claim, no fetch claim
  * validator catches tampered safety flags / missing category / missing required
    future manifest field
  * validator tool is stdlib-only; no network/broker/exchange imports
  * Bundle 4 + Bundle 5 validators still pass
  * candidate registry builds after manifest exists; arbitrage stays IDEA
  * next-bundle generator still validates
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

import arbitrage_dataset_manifest_check as admc   # noqa: E402
import arbitrage_data_contract_check as adc      # noqa: E402
import arbitrage_protocol_check as apc           # noqa: E402
import strategy_candidate_registry as scr        # noqa: E402
import strategy_next_bundle as snb               # noqa: E402

TOOL_FILE = _TOOLS_DIR / "arbitrage_dataset_manifest_check.py"
MANIFEST_JSON_PATH = _REPO_ROOT / admc.MANIFEST_DIR_REL / admc.MANIFEST_JSON
MANIFEST_MD_PATH = _REPO_ROOT / admc.MANIFEST_DIR_REL / admc.MANIFEST_MD


# --- existence + validation ---------------------------------------------- #

def test_dataset_manifest_json_exists():
    assert MANIFEST_JSON_PATH.exists(), f"missing: {MANIFEST_JSON_PATH}"


def test_dataset_manifest_md_exists():
    assert MANIFEST_MD_PATH.exists(), f"missing: {MANIFEST_MD_PATH}"


def test_validator_passes_on_committed_manifest():
    ok, errs = admc.validate(_REPO_ROOT)
    assert ok, errs


def test_execution_fetch_backtest_flags_all_false():
    data = json.loads(MANIFEST_JSON_PATH.read_text(encoding="utf-8"))
    for flag in admc.MUST_BE_FALSE_FLAGS:
        assert data.get(flag) is False, f"{flag} must be False"
    assert data.get("research_only") is True


def test_required_top_level_sections_present():
    data = json.loads(MANIFEST_JSON_PATH.read_text(encoding="utf-8"))
    for k in admc.REQUIRED_TOP_LEVEL_KEYS:
        assert k in data, f"missing top-level key: {k}"


def test_five_required_categories_present_with_requirements():
    data = json.loads(MANIFEST_JSON_PATH.read_text(encoding="utf-8"))
    cats = data["supported_arbitrage_categories"]
    ids = [c.get("id") for c in cats if isinstance(c, dict)]
    for required_id in admc.REQUIRED_CATEGORY_IDS:
        assert required_id in ids, f"missing category id: {required_id}"
    for c in cats:
        for f in admc.REQUIRED_CATEGORY_FIELDS:
            assert f in c, f"category {c.get('id')!r}: missing field {f}"
        reqs = c["category_specific_manifest_requirements"]
        assert isinstance(reqs, list) and reqs


def test_manifest_schema_contains_all_required_future_fields():
    data = json.loads(MANIFEST_JSON_PATH.read_text(encoding="utf-8"))
    ms = data["manifest_schema"]
    req = ms["required_future_manifest_fields"]
    for f in admc.REQUIRED_FUTURE_MANIFEST_FIELDS:
        assert f in req, f"manifest_schema missing future field: {f}"
    fd = ms.get("field_descriptions") or {}
    # Field descriptions should cover at least the most important fields.
    for f in ("dataset_id", "dataset_version", "freeze_status", "qa_status",
             "source_location", "source_type"):
        assert f in fd, f"field_descriptions missing: {f}"


def test_qa_status_model_contains_all_seven_statuses():
    data = json.loads(MANIFEST_JSON_PATH.read_text(encoding="utf-8"))
    qa = data["qa_status_model"]
    for s in admc.REQUIRED_QA_STATUSES:
        assert s in qa, f"qa_status_model missing status: {s}"


def test_freeze_rules_exist_and_reference_frozen():
    data = json.loads(MANIFEST_JSON_PATH.read_text(encoding="utf-8"))
    fr = data["data_freeze_rules"]
    assert isinstance(fr, list) and fr
    assert "FROZEN" in " ".join(str(x) for x in fr)


def test_pure_vs_statistical_distinction_preserved():
    data = json.loads(MANIFEST_JSON_PATH.read_text(encoding="utf-8"))
    rv = next(c for c in data["supported_arbitrage_categories"]
             if c.get("id") == "statistical_relative_value")
    assert "NOT pure arbitrage" in rv["label"]
    md = MANIFEST_MD_PATH.read_text(encoding="utf-8")
    assert "NOT pure arbitrage" in md
    assert "RELATIVE_VALUE" in md
    assert "price gap is not profit" in md.lower() or "A price gap is **not** profit" in md
    assert "QA_PASS does not imply profitability" in md


def test_no_profitability_or_fetch_or_backtest_claims():
    md = MANIFEST_MD_PATH.read_text(encoding="utf-8").lower()
    jsn = json.dumps(json.loads(MANIFEST_JSON_PATH.read_text(encoding="utf-8")),
                    ensure_ascii=False).lower()
    for phrase in admc.FORBIDDEN_PHRASES:
        assert phrase.lower() not in md, f"forbidden phrase in dataset_manifest.md: {phrase!r}"
        assert phrase.lower() not in jsn, f"forbidden phrase in dataset_manifest.json: {phrase!r}"


# --- validator failure modes --------------------------------------------- #

def _stage_tmp(tmp_path: Path):
    tmp_dir = tmp_path / admc.MANIFEST_DIR_REL
    tmp_dir.mkdir(parents=True, exist_ok=True)
    (tmp_dir / admc.MANIFEST_MD).write_text(MANIFEST_MD_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    data = json.loads(MANIFEST_JSON_PATH.read_text(encoding="utf-8"))
    return tmp_dir, data


def test_validator_detects_tampered_safety_flag(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["backtest_enabled"] = True
    (tmp_dir / admc.MANIFEST_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = admc.validate(tmp_path)
    assert not ok
    assert any("backtest_enabled" in e for e in errs)


def test_validator_detects_missing_required_category(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["supported_arbitrage_categories"] = [
        c for c in data["supported_arbitrage_categories"] if c.get("id") != "triangular"
    ]
    (tmp_dir / admc.MANIFEST_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = admc.validate(tmp_path)
    assert not ok
    assert any("triangular" in e for e in errs)


def test_validator_detects_missing_required_future_manifest_field(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["manifest_schema"]["required_future_manifest_fields"] = [
        f for f in data["manifest_schema"]["required_future_manifest_fields"]
        if f != "checksum_policy"
    ]
    (tmp_dir / admc.MANIFEST_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = admc.validate(tmp_path)
    assert not ok
    assert any("checksum_policy" in e for e in errs)


def test_validator_detects_missing_qa_status(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    del data["qa_status_model"]["QA_WARN"]
    (tmp_dir / admc.MANIFEST_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = admc.validate(tmp_path)
    assert not ok
    assert any("QA_WARN" in e for e in errs)


def test_validator_detects_forbidden_phrase_in_md(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    (tmp_dir / admc.MANIFEST_JSON).write_text(json.dumps(data), encoding="utf-8")
    md = MANIFEST_MD_PATH.read_text(encoding="utf-8") + "\nNote: production-ready.\n"
    (tmp_dir / admc.MANIFEST_MD).write_text(md, encoding="utf-8")
    ok, errs = admc.validate(tmp_path)
    assert not ok
    assert any("production-ready" in e for e in errs)


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
    assert admc.main(["validate", "--repo-root", str(_REPO_ROOT)]) == 0
    assert admc.main(["show", "--repo-root", str(_REPO_ROOT)]) == 0


# --- integration tests --------------------------------------------------- #

def test_bundle_4_protocol_validator_still_passes():
    ok, errs = apc.validate(_REPO_ROOT)
    assert ok, errs


def test_bundle_5_data_contract_validator_still_passes():
    ok, errs = adc.validate(_REPO_ROOT)
    assert ok, errs


def test_candidate_registry_builds_after_manifest_exists():
    payload = scr.generate(_REPO_ROOT)
    arb = next(c for c in payload["candidates"]
              if c["candidate_id"] == "arbitrage_research_protocol")
    # Lane still IDEA — never ACTIVE, never STRONG despite richer docs.
    assert arb["status"] == "IDEA", arb
    assert arb["evidence_level"] in ("NONE", "MIXED"), arb
    assert arb["evidence_level"] != "STRONG"
    # All three doc generations now appear in source_reports.
    assert "dataset_manifest.md" in arb["source_reports"], arb["source_reports"]
    assert "dataset_manifest.json" in arb["source_reports"], arb["source_reports"]
    assert "data_contract.md" in arb["source_reports"]
    assert "protocol.md" in arb["source_reports"]


def test_next_bundle_generator_still_validates_after_manifest():
    snb.generate(_REPO_ROOT)
    ok, errs = snb.validate(_REPO_ROOT)
    assert ok, errs
