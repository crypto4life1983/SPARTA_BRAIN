"""Bundle 8 — Arbitrage Data Source Evaluation Memo v1 tests (research-only).

Pure stdlib + pytest. Asserts:
  * data_source_evaluation.json exists and validates
  * the seven execution / fetch / connection / backtest / dataset-processing
    flags are pinned False
  * all required top-level sections exist
  * all six required source classes are evaluated (A..F)
  * decision matrix has every required field for every row
  * `allowed_now` is False for every real data-fetching source class
  * manually-copied (F) and web-scraped (E) sources are REJECTED for evidence
  * approval gates include explicit operator authorization
  * no profitability claim, no fetch claim, no backtest-authorize claim
  * validator catches tampered flag / missing source class / allowed_now-True
    on a real source class / missing matrix row / forbidden phrase
  * validator tool is stdlib-only; no network/broker/exchange imports
  * Bundle 4 + 5 + 6 + 7 validators still pass
  * candidate registry builds after evaluation exists; arbitrage stays IDEA
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

import arbitrage_data_source_evaluation_check as adsec  # noqa: E402
import arbitrage_qa_harness_spec_check as aqhc          # noqa: E402
import arbitrage_dataset_manifest_check as admc         # noqa: E402
import arbitrage_data_contract_check as adc             # noqa: E402
import arbitrage_protocol_check as apc                  # noqa: E402
import strategy_candidate_registry as scr               # noqa: E402
import strategy_next_bundle as snb                      # noqa: E402

TOOL_FILE = _TOOLS_DIR / "arbitrage_data_source_evaluation_check.py"
EVAL_JSON_PATH = _REPO_ROOT / adsec.EVAL_DIR_REL / adsec.EVAL_JSON
EVAL_MD_PATH = _REPO_ROOT / adsec.EVAL_DIR_REL / adsec.EVAL_MD


# --- existence + validation ---------------------------------------------- #

def test_evaluation_json_exists():
    assert EVAL_JSON_PATH.exists(), f"missing: {EVAL_JSON_PATH}"


def test_evaluation_md_exists():
    assert EVAL_MD_PATH.exists(), f"missing: {EVAL_MD_PATH}"


def test_validator_passes_on_committed_evaluation():
    ok, errs = adsec.validate(_REPO_ROOT)
    assert ok, errs


def test_seven_flags_all_false():
    data = json.loads(EVAL_JSON_PATH.read_text(encoding="utf-8"))
    for flag in adsec.MUST_BE_FALSE_FLAGS:
        assert data.get(flag) is False, f"{flag} must be False"
    assert data.get("research_only") is True


def test_required_top_level_sections_present():
    data = json.loads(EVAL_JSON_PATH.read_text(encoding="utf-8"))
    for k in adsec.REQUIRED_TOP_LEVEL_KEYS:
        assert k in data, f"missing top-level key: {k}"


def test_all_six_source_classes_evaluated():
    data = json.loads(EVAL_JSON_PATH.read_text(encoding="utf-8"))
    src = data["evaluated_source_classes"]
    ids = [c.get("id") for c in src if isinstance(c, dict)]
    for cid in adsec.REQUIRED_SOURCE_CLASS_IDS:
        assert cid in ids, f"missing source class: {cid}"


def test_decision_matrix_complete():
    data = json.loads(EVAL_JSON_PATH.read_text(encoding="utf-8"))
    dm = data["data_source_decision_matrix"]
    assert isinstance(dm, dict)
    fields = set(dm["fields"])
    for f in adsec.REQUIRED_MATRIX_FIELDS:
        assert f in fields, f"matrix fields missing: {f}"
    row_ids = {r["source_class"] for r in dm["rows"] if isinstance(r, dict)}
    for cid in adsec.REQUIRED_SOURCE_CLASS_IDS:
        assert cid in row_ids, f"matrix row missing for source class: {cid}"
    for row in dm["rows"]:
        for f in adsec.REQUIRED_MATRIX_FIELDS:
            assert f in row, f"row {row.get('source_class')}: missing {f}"
        assert row["recommended_status"] in adsec.ALLOWED_RECOMMENDED_STATUSES


def test_allowed_now_false_for_every_row():
    data = json.loads(EVAL_JSON_PATH.read_text(encoding="utf-8"))
    for row in data["data_source_decision_matrix"]["rows"]:
        assert row["allowed_now"] is False, f"{row['source_class']}: allowed_now must be False"


def test_manually_copied_and_web_scraped_are_rejected():
    data = json.loads(EVAL_JSON_PATH.read_text(encoding="utf-8"))
    by_sc = {r["source_class"]: r for r in data["data_source_decision_matrix"]["rows"]}
    assert by_sc["E_web_scraped_or_unofficial_data"]["recommended_status"] == "REJECTED"
    assert by_sc["F_manually_copied_prices_or_screenshots"]["recommended_status"] == "REJECTED"


def test_approval_gates_include_operator_authorization():
    data = json.loads(EVAL_JSON_PATH.read_text(encoding="utf-8"))
    gates = data["approval_gates"]["must_all_be_satisfied_before_any_future_data_collection"]
    joined = " ".join(gates).lower()
    for marker in ("explicit_operator_authorization", "exact_source_named",
                  "exact_symbols_named", "exact_time_window_named",
                  "data_contract_version_referenced",
                  "dataset_manifest_version_referenced",
                  "qa_harness_spec_version_referenced",
                  "storage_path_named",
                  "no_credentials_unless_separately_authorized",
                  "no_trading_permissions",
                  "no_automatic_scheduler",
                  "no_live_or_paper_execution"):
        assert marker in joined, f"approval_gates missing: {marker}"


def test_no_profitability_or_fetch_or_backtest_claims():
    md = EVAL_MD_PATH.read_text(encoding="utf-8").lower()
    jsn = json.dumps(json.loads(EVAL_JSON_PATH.read_text(encoding="utf-8")),
                    ensure_ascii=False).lower()
    for phrase in adsec.FORBIDDEN_PHRASES:
        assert phrase.lower() not in md, f"forbidden phrase in MD: {phrase!r}"
        assert phrase.lower() not in jsn, f"forbidden phrase in JSON: {phrase!r}"


def test_distinction_phrases_present_in_md():
    md = EVAL_MD_PATH.read_text(encoding="utf-8")
    for phrase in adsec.DISTINCTION_PHRASES:
        assert phrase in md, f"distinction phrase missing: {phrase!r}"


# --- validator failure modes --------------------------------------------- #

def _stage_tmp(tmp_path: Path):
    tmp_dir = tmp_path / adsec.EVAL_DIR_REL
    tmp_dir.mkdir(parents=True, exist_ok=True)
    (tmp_dir / adsec.EVAL_MD).write_text(EVAL_MD_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    data = json.loads(EVAL_JSON_PATH.read_text(encoding="utf-8"))
    return tmp_dir, data


def test_validator_detects_tampered_safety_flag(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["data_fetch_enabled"] = True
    (tmp_dir / adsec.EVAL_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = adsec.validate(tmp_path)
    assert not ok
    assert any("data_fetch_enabled" in e for e in errs)


def test_validator_detects_missing_source_class(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["evaluated_source_classes"] = [
        c for c in data["evaluated_source_classes"]
        if c.get("id") != "C_paid_market_data_vendors"
    ]
    data["data_source_decision_matrix"]["rows"] = [
        r for r in data["data_source_decision_matrix"]["rows"]
        if r.get("source_class") != "C_paid_market_data_vendors"
    ]
    (tmp_dir / adsec.EVAL_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = adsec.validate(tmp_path)
    assert not ok
    assert any("C_paid_market_data_vendors" in e for e in errs)


def test_validator_detects_allowed_now_true(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    # Try to slip allowed_now=True on a real data-fetching source.
    for row in data["data_source_decision_matrix"]["rows"]:
        if row["source_class"] == "C_paid_market_data_vendors":
            row["allowed_now"] = True
            break
    (tmp_dir / adsec.EVAL_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = adsec.validate(tmp_path)
    assert not ok
    assert any("allowed_now must be False" in e for e in errs)


def test_validator_detects_manual_copy_not_rejected(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    for row in data["data_source_decision_matrix"]["rows"]:
        if row["source_class"] == "F_manually_copied_prices_or_screenshots":
            row["recommended_status"] = "ACCEPTABLE"
            break
    (tmp_dir / adsec.EVAL_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = adsec.validate(tmp_path)
    assert not ok
    assert any("must be REJECTED" in e for e in errs)


def test_validator_detects_forbidden_phrase_in_md(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    (tmp_dir / adsec.EVAL_JSON).write_text(json.dumps(data), encoding="utf-8")
    md = EVAL_MD_PATH.read_text(encoding="utf-8") + "\nNote: this is profitable.\n"
    (tmp_dir / adsec.EVAL_MD).write_text(md, encoding="utf-8")
    ok, errs = adsec.validate(tmp_path)
    assert not ok
    assert any("this is profitable" in e for e in errs)


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
    assert adsec.main(["validate", "--repo-root", str(_REPO_ROOT)]) == 0
    assert adsec.main(["show", "--repo-root", str(_REPO_ROOT)]) == 0


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


def test_bundle_7_qa_harness_spec_validator_still_passes():
    ok, errs = aqhc.validate(_REPO_ROOT)
    assert ok, errs


def test_candidate_registry_builds_after_evaluation_exists():
    payload = scr.generate(_REPO_ROOT)
    arb = next(c for c in payload["candidates"]
              if c["candidate_id"] == "arbitrage_research_protocol")
    # Lane still IDEA — never ACTIVE, never STRONG despite richer docs.
    assert arb["status"] == "IDEA", arb
    assert arb["evidence_level"] in ("NONE", "MIXED"), arb
    assert arb["evidence_level"] != "STRONG"
    # All five doc generations now appear in source_reports.
    for needed in ("data_source_evaluation.md", "data_source_evaluation.json",
                  "qa_harness_spec.md", "dataset_manifest.md",
                  "data_contract.md", "protocol.md"):
        assert needed in arb["source_reports"], arb["source_reports"]


def test_next_bundle_generator_still_validates_after_evaluation():
    snb.generate(_REPO_ROOT)
    ok, errs = snb.validate(_REPO_ROOT)
    assert ok, errs
