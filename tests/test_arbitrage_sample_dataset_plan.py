"""Bundle 9 — Arbitrage Sample Dataset Plan v1 tests (research-only).

Pure stdlib + pytest. Asserts:
  * sample_dataset_plan.json exists and validates
  * the seven execution / fetch / connection / backtest / dataset-processing
    flags are pinned False
  * all required top-level sections exist
  * proposed_sample_scope is TINY and conservative (primary cross_exchange_spot;
    symbols list <=4; explicit disclaimers)
  * naming_convention exists with required slots and files_are_examples_only flag
  * storage_plan exists with no_network_url + no_real_files flags
  * freeze_plan exists
  * approval_gates include explicit operator authorization + all five upstream
    version pins + sample plan version pin
  * future_collection_steps include 'explicit_operator_authorization' AND
    'data_collection_in_separate_bundle'
  * NO real data files are created in this bundle
  * no profitability claim, no fetch claim, no backtest-authorize claim
  * validator catches tampered flag / missing scope / missing future-step
    operator-authorization marker / forbidden phrase
  * validator tool is stdlib-only; no network/broker/exchange imports
  * Bundle 4 + 5 + 6 + 7 + 8 validators still pass
  * candidate registry builds after plan exists; arbitrage stays IDEA
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

import arbitrage_sample_dataset_plan_check as asdpc      # noqa: E402
import arbitrage_data_source_evaluation_check as adsec  # noqa: E402
import arbitrage_qa_harness_spec_check as aqhc          # noqa: E402
import arbitrage_dataset_manifest_check as admc         # noqa: E402
import arbitrage_data_contract_check as adc             # noqa: E402
import arbitrage_protocol_check as apc                  # noqa: E402
import strategy_candidate_registry as scr               # noqa: E402
import strategy_next_bundle as snb                      # noqa: E402

TOOL_FILE = _TOOLS_DIR / "arbitrage_sample_dataset_plan_check.py"
PLAN_JSON_PATH = _REPO_ROOT / asdpc.PLAN_DIR_REL / asdpc.PLAN_JSON
PLAN_MD_PATH = _REPO_ROOT / asdpc.PLAN_DIR_REL / asdpc.PLAN_MD
PLAN_DIR_REL = asdpc.PLAN_DIR_REL


# --- existence + validation ---------------------------------------------- #

def test_plan_json_exists():
    assert PLAN_JSON_PATH.exists(), f"missing: {PLAN_JSON_PATH}"


def test_plan_md_exists():
    assert PLAN_MD_PATH.exists(), f"missing: {PLAN_MD_PATH}"


def test_validator_passes_on_committed_plan():
    ok, errs = asdpc.validate(_REPO_ROOT)
    assert ok, errs


def test_seven_flags_all_false():
    data = json.loads(PLAN_JSON_PATH.read_text(encoding="utf-8"))
    for flag in asdpc.MUST_BE_FALSE_FLAGS:
        assert data.get(flag) is False, f"{flag} must be False"
    assert data.get("research_only") is True


def test_required_top_level_sections_present():
    data = json.loads(PLAN_JSON_PATH.read_text(encoding="utf-8"))
    for k in asdpc.REQUIRED_TOP_LEVEL_KEYS:
        assert k in data, f"missing top-level key: {k}"


def test_proposed_scope_is_tiny_and_conservative():
    data = json.loads(PLAN_JSON_PATH.read_text(encoding="utf-8"))
    pss = data["proposed_sample_scope"]
    assert pss["primary_category"] == "cross_exchange_spot"
    assert "TINY" in str(pss["scope_intent"]).upper()
    syms = pss["symbols_example_only"]
    assert isinstance(syms, list) and 1 <= len(syms) <= 4
    assert pss.get("explicit_disclaimers"), "explicit_disclaimers must be present"


def test_naming_convention_exists():
    data = json.loads(PLAN_JSON_PATH.read_text(encoding="utf-8"))
    nc = data["naming_convention"]
    for k in ("dataset_id_pattern", "dataset_version_pattern",
             "manifest_filename", "qa_report_filename", "checksum_filename"):
        assert k in nc, f"naming_convention missing: {k}"
    assert nc.get("files_are_examples_only_no_real_files_in_this_bundle") is True


def test_storage_plan_exists_and_forbids_real_files():
    data = json.loads(PLAN_JSON_PATH.read_text(encoding="utf-8"))
    sp = data["storage_plan"]
    assert sp.get("no_network_url_allowed") is True
    assert sp.get("no_real_data_files_created_in_this_bundle") is True


def test_freeze_plan_exists():
    data = json.loads(PLAN_JSON_PATH.read_text(encoding="utf-8"))
    fp = data["freeze_plan"]
    assert isinstance(fp, dict) and fp


def test_approval_gates_include_operator_authorization_and_version_pins():
    data = json.loads(PLAN_JSON_PATH.read_text(encoding="utf-8"))
    gates = data["approval_gates"]["must_all_be_satisfied_before_any_future_data_collection"]
    joined = " ".join(gates).lower()
    for marker in asdpc.REQUIRED_APPROVAL_GATE_MARKERS:
        assert marker in joined, f"approval_gates missing: {marker}"


def test_future_collection_steps_include_required_markers():
    data = json.loads(PLAN_JSON_PATH.read_text(encoding="utf-8"))
    steps = data["future_collection_steps"]
    joined = " ".join(steps).lower()
    for marker in asdpc.REQUIRED_FUTURE_COLLECTION_STEPS_MARKERS:
        assert marker in joined, f"future_collection_steps missing: {marker}"


def test_no_real_data_files_created():
    # Verify that no actual data files appear under the plan's output dir
    # beyond the four authored doc files.
    plan_dir = _REPO_ROOT / PLAN_DIR_REL
    allowed = {"sample_dataset_plan.json", "sample_dataset_plan.md",
              "report.json", "report.md"}
    if plan_dir.exists():
        actual = {p.name for p in plan_dir.iterdir() if p.is_file()}
        extra = actual - allowed
        assert not extra, f"unexpected files in plan dir: {extra}"


def test_no_profitability_or_fetch_or_backtest_claims():
    md = PLAN_MD_PATH.read_text(encoding="utf-8").lower()
    jsn = json.dumps(json.loads(PLAN_JSON_PATH.read_text(encoding="utf-8")),
                    ensure_ascii=False).lower()
    for phrase in asdpc.FORBIDDEN_PHRASES:
        assert phrase.lower() not in md, f"forbidden phrase in MD: {phrase!r}"
        assert phrase.lower() not in jsn, f"forbidden phrase in JSON: {phrase!r}"


def test_distinction_phrases_present_in_md():
    md = PLAN_MD_PATH.read_text(encoding="utf-8")
    for phrase in asdpc.DISTINCTION_PHRASES:
        assert phrase in md, f"distinction phrase missing: {phrase!r}"


# --- validator failure modes --------------------------------------------- #

def _stage_tmp(tmp_path: Path):
    tmp_dir = tmp_path / asdpc.PLAN_DIR_REL
    tmp_dir.mkdir(parents=True, exist_ok=True)
    (tmp_dir / asdpc.PLAN_MD).write_text(PLAN_MD_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    data = json.loads(PLAN_JSON_PATH.read_text(encoding="utf-8"))
    return tmp_dir, data


def test_validator_detects_tampered_safety_flag(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["backtest_enabled"] = True
    (tmp_dir / asdpc.PLAN_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = asdpc.validate(tmp_path)
    assert not ok
    assert any("backtest_enabled" in e for e in errs)


def test_validator_detects_missing_scope(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    del data["proposed_sample_scope"]
    (tmp_dir / asdpc.PLAN_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = asdpc.validate(tmp_path)
    assert not ok
    assert any("proposed_sample_scope" in e for e in errs)


def test_validator_detects_overbroad_symbol_list(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    # Inflate symbols beyond the 4-symbol "tiny" ceiling.
    data["proposed_sample_scope"]["symbols_example_only"] = [
        {"canonical": "BTC_USDT", "label": "x", "rationale": "y"},
        {"canonical": "ETH_USDT", "label": "x", "rationale": "y"},
        {"canonical": "SOL_USDT", "label": "x", "rationale": "y"},
        {"canonical": "ADA_USDT", "label": "x", "rationale": "y"},
        {"canonical": "XRP_USDT", "label": "x", "rationale": "y"},
    ]
    (tmp_dir / asdpc.PLAN_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = asdpc.validate(tmp_path)
    assert not ok
    assert any("too broad" in e for e in errs)


def test_validator_detects_missing_future_step_operator_authorization(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["future_collection_steps"] = [
        s for s in data["future_collection_steps"]
        if "explicit_operator_authorization" not in s
    ]
    (tmp_dir / asdpc.PLAN_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = asdpc.validate(tmp_path)
    assert not ok
    assert any("explicit_operator_authorization" in e for e in errs)


def test_validator_detects_storage_plan_allowing_network_url(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["storage_plan"]["no_network_url_allowed"] = False
    (tmp_dir / asdpc.PLAN_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = asdpc.validate(tmp_path)
    assert not ok
    assert any("no_network_url_allowed" in e for e in errs)


def test_validator_detects_forbidden_phrase_in_md(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    (tmp_dir / asdpc.PLAN_JSON).write_text(json.dumps(data), encoding="utf-8")
    md = PLAN_MD_PATH.read_text(encoding="utf-8") + "\nNote: live-ready.\n"
    (tmp_dir / asdpc.PLAN_MD).write_text(md, encoding="utf-8")
    ok, errs = asdpc.validate(tmp_path)
    assert not ok
    assert any("live-ready" in e for e in errs)


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
    assert asdpc.main(["validate", "--repo-root", str(_REPO_ROOT)]) == 0
    assert asdpc.main(["show", "--repo-root", str(_REPO_ROOT)]) == 0


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


def test_bundle_8_data_source_evaluation_validator_still_passes():
    ok, errs = adsec.validate(_REPO_ROOT)
    assert ok, errs


def test_candidate_registry_builds_after_plan_exists():
    payload = scr.generate(_REPO_ROOT)
    arb = next(c for c in payload["candidates"]
              if c["candidate_id"] == "arbitrage_research_protocol")
    # Lane stays IDEA or (after Bundle 10) WATCH — NEVER ACTIVE / STRONG.
    assert arb["status"] in ("IDEA", "WATCH"), arb
    assert arb["evidence_level"] in ("NONE", "MIXED"), arb
    assert arb["evidence_level"] != "STRONG"
    # All six doc generations now appear in source_reports.
    for needed in ("sample_dataset_plan.md", "sample_dataset_plan.json",
                  "data_source_evaluation.md", "qa_harness_spec.md",
                  "dataset_manifest.md", "data_contract.md", "protocol.md"):
        assert needed in arb["source_reports"], arb["source_reports"]


def test_next_bundle_generator_still_validates_after_plan():
    snb.generate(_REPO_ROOT)
    ok, errs = snb.validate(_REPO_ROOT)
    assert ok, errs
