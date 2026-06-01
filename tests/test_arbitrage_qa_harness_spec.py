"""Bundle 7 — Arbitrage QA Harness Spec v1 tests (research-only).

Pure stdlib + pytest. Asserts:
  * qa_harness_spec.json exists and validates
  * the seven execution / fetch / connection / backtest / dataset-processing
    flags are pinned False
  * all required top-level sections exist
  * all five required arbitrage categories present with per-category QA checks
  * all 8 QA check groups (A_manifest_integrity .. H_anomaly_detection) present
  * QA status model contains all 6 statuses
  * future QA report schema lists every required field
  * pure-vs-statistical distinction preserved
  * no profitability claim, no live-readiness claim, no QA-PASS-implies-edge claim
  * validator catches tampered flag / missing category / missing required QA
    report field / missing QA status / forbidden phrase
  * validator tool is stdlib-only; no network/broker/exchange imports
  * Bundle 4 + 5 + 6 validators still pass
  * candidate registry builds after spec exists; arbitrage stays IDEA
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

import arbitrage_qa_harness_spec_check as aqhc    # noqa: E402
import arbitrage_dataset_manifest_check as admc   # noqa: E402
import arbitrage_data_contract_check as adc      # noqa: E402
import arbitrage_protocol_check as apc           # noqa: E402
import strategy_candidate_registry as scr        # noqa: E402
import strategy_next_bundle as snb               # noqa: E402

TOOL_FILE = _TOOLS_DIR / "arbitrage_qa_harness_spec_check.py"
SPEC_JSON_PATH = _REPO_ROOT / aqhc.SPEC_DIR_REL / aqhc.SPEC_JSON
SPEC_MD_PATH = _REPO_ROOT / aqhc.SPEC_DIR_REL / aqhc.SPEC_MD


# --- existence + validation ---------------------------------------------- #

def test_spec_json_exists():
    assert SPEC_JSON_PATH.exists(), f"missing: {SPEC_JSON_PATH}"


def test_spec_md_exists():
    assert SPEC_MD_PATH.exists(), f"missing: {SPEC_MD_PATH}"


def test_validator_passes_on_committed_spec():
    ok, errs = aqhc.validate(_REPO_ROOT)
    assert ok, errs


def test_seven_flags_all_false():
    data = json.loads(SPEC_JSON_PATH.read_text(encoding="utf-8"))
    for flag in aqhc.MUST_BE_FALSE_FLAGS:
        assert data.get(flag) is False, f"{flag} must be False"
    assert data.get("research_only") is True


def test_required_top_level_sections_present():
    data = json.loads(SPEC_JSON_PATH.read_text(encoding="utf-8"))
    for k in aqhc.REQUIRED_TOP_LEVEL_KEYS:
        assert k in data, f"missing top-level key: {k}"


def test_five_categories_with_qa_checks_present():
    data = json.loads(SPEC_JSON_PATH.read_text(encoding="utf-8"))
    cats = data["supported_arbitrage_categories"]
    ids = [c.get("id") for c in cats if isinstance(c, dict)]
    for required_id in aqhc.REQUIRED_CATEGORY_IDS:
        assert required_id in ids, f"missing category id: {required_id}"
    for c in cats:
        for f in aqhc.REQUIRED_CATEGORY_FIELDS:
            assert f in c, f"category {c.get('id')!r}: missing field {f}"
        checks = c["category_specific_qa_checks"]
        assert isinstance(checks, list) and checks


def test_all_eight_qa_check_groups_present():
    data = json.loads(SPEC_JSON_PATH.read_text(encoding="utf-8"))
    qcg = data["qa_check_groups"]
    for grp in aqhc.REQUIRED_QA_CHECK_GROUPS:
        assert grp in qcg, f"missing QA check group: {grp}"
        g = qcg[grp]
        assert isinstance(g, dict)
        assert isinstance(g.get("checks"), list) and g["checks"]


def test_qa_status_model_contains_all_six_statuses():
    data = json.loads(SPEC_JSON_PATH.read_text(encoding="utf-8"))
    qsr = data["qa_status_rules"]
    for s in aqhc.REQUIRED_QA_STATUSES:
        assert s in qsr, f"missing QA status: {s}"


def test_future_qa_report_schema_contains_required_fields():
    data = json.loads(SPEC_JSON_PATH.read_text(encoding="utf-8"))
    fields = data["report_schema"]["required_future_qa_report_fields"]
    for f in aqhc.REQUIRED_QA_REPORT_FIELDS:
        assert f in fields, f"future QA report schema missing field: {f}"


def test_pure_vs_statistical_distinction_preserved():
    data = json.loads(SPEC_JSON_PATH.read_text(encoding="utf-8"))
    rv = next(c for c in data["supported_arbitrage_categories"]
             if c.get("id") == "statistical_relative_value")
    assert "NOT pure arbitrage" in rv["label"]
    md = SPEC_MD_PATH.read_text(encoding="utf-8")
    for phrase in ("NOT pure arbitrage", "RELATIVE_VALUE",
                  "price gap is not profit",
                  "QA is not strategy validation",
                  "QA_PASS does NOT"):
        assert phrase in md, f"distinction phrase missing: {phrase!r}"


def test_no_profitability_or_backtest_authorize_claims():
    md = SPEC_MD_PATH.read_text(encoding="utf-8").lower()
    jsn = json.dumps(json.loads(SPEC_JSON_PATH.read_text(encoding="utf-8")),
                    ensure_ascii=False).lower()
    for phrase in aqhc.FORBIDDEN_PHRASES:
        assert phrase.lower() not in md, f"forbidden phrase in qa_harness_spec.md: {phrase!r}"
        assert phrase.lower() not in jsn, f"forbidden phrase in qa_harness_spec.json: {phrase!r}"


# --- validator failure modes --------------------------------------------- #

def _stage_tmp(tmp_path: Path):
    tmp_dir = tmp_path / aqhc.SPEC_DIR_REL
    tmp_dir.mkdir(parents=True, exist_ok=True)
    (tmp_dir / aqhc.SPEC_MD).write_text(SPEC_MD_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    data = json.loads(SPEC_JSON_PATH.read_text(encoding="utf-8"))
    return tmp_dir, data


def test_validator_detects_tampered_safety_flag(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["dataset_processing_enabled"] = True
    (tmp_dir / aqhc.SPEC_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = aqhc.validate(tmp_path)
    assert not ok
    assert any("dataset_processing_enabled" in e for e in errs)


def test_validator_detects_missing_required_category(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["supported_arbitrage_categories"] = [
        c for c in data["supported_arbitrage_categories"] if c.get("id") != "futures_calendar"
    ]
    (tmp_dir / aqhc.SPEC_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = aqhc.validate(tmp_path)
    assert not ok
    assert any("futures_calendar" in e for e in errs)


def test_validator_detects_missing_qa_check_group(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    del data["qa_check_groups"]["H_anomaly_detection"]
    (tmp_dir / aqhc.SPEC_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = aqhc.validate(tmp_path)
    assert not ok
    assert any("H_anomaly_detection" in e for e in errs)


def test_validator_detects_missing_qa_status(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    del data["qa_status_rules"]["QA_WARN"]
    (tmp_dir / aqhc.SPEC_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = aqhc.validate(tmp_path)
    assert not ok
    assert any("QA_WARN" in e for e in errs)


def test_validator_detects_missing_required_qa_report_field(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["report_schema"]["required_future_qa_report_fields"] = [
        f for f in data["report_schema"]["required_future_qa_report_fields"]
        if f != "checksum_policy" and f != "qa_status"
    ]
    (tmp_dir / aqhc.SPEC_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = aqhc.validate(tmp_path)
    assert not ok
    assert any("qa_status" in e for e in errs)


def test_validator_detects_forbidden_phrase_in_md(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    (tmp_dir / aqhc.SPEC_JSON).write_text(json.dumps(data), encoding="utf-8")
    md = SPEC_MD_PATH.read_text(encoding="utf-8") + "\nNote: risk-free profit.\n"
    (tmp_dir / aqhc.SPEC_MD).write_text(md, encoding="utf-8")
    ok, errs = aqhc.validate(tmp_path)
    assert not ok
    assert any("risk-free profit" in e for e in errs)


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
    assert aqhc.main(["validate", "--repo-root", str(_REPO_ROOT)]) == 0
    assert aqhc.main(["show", "--repo-root", str(_REPO_ROOT)]) == 0


# --- integration tests --------------------------------------------------- #

def test_bundle_4_protocol_validator_still_passes():
    ok, errs = apc.validate(_REPO_ROOT)
    assert ok, errs


def test_bundle_5_data_contract_validator_still_passes():
    ok, errs = adc.validate(_REPO_ROOT)
    assert ok, errs


def test_bundle_6_dataset_manifest_validator_still_passes():
    ok, errs = admc.validate(_REPO_ROOT)
    assert ok, errs


def test_candidate_registry_builds_after_spec_exists():
    payload = scr.generate(_REPO_ROOT)
    arb = next(c for c in payload["candidates"]
              if c["candidate_id"] == "arbitrage_research_protocol")
    # Lane stays IDEA or (after Bundle 10) WATCH — NEVER ACTIVE / STRONG.
    assert arb["status"] in ("IDEA", "WATCH"), arb
    assert arb["evidence_level"] in ("NONE", "MIXED"), arb
    assert arb["evidence_level"] != "STRONG"
    # All four doc generations now appear in source_reports.
    for needed in ("qa_harness_spec.md", "qa_harness_spec.json",
                  "dataset_manifest.md", "data_contract.md", "protocol.md"):
        assert needed in arb["source_reports"], arb["source_reports"]


def test_next_bundle_generator_still_validates_after_spec():
    snb.generate(_REPO_ROOT)
    ok, errs = snb.validate(_REPO_ROOT)
    assert ok, errs
