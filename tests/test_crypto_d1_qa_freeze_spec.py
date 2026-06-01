"""Bundle 14 -- Crypto-D1 Data QA / Freeze Spec v1 tests (research-only).

Pure stdlib + pytest. Asserts:
  * qa_freeze_spec.json exists and validates
  * all seven execution / fetch / connection / backtest / dataset-processing
    flags are pinned False
  * all required top-level sections exist
  * target assets include BTC, ETH, SOL
  * timeframe is daily only; intraday explicitly out of scope
  * spot-only / perps-forbidden distinction is preserved
  * all 7 QA check groups (A_manifest_integrity .. G_freeze) exist
  * QA_status_model contains all 6 declared statuses
  * QA_report_schema.required_fields contains all 26 future report fields
  * freeze rules require frozen / checksums / dataset version / UTC daily
    bars / no weekday-only calendars
  * no real data files were created
  * no profitability / fetch / backtest-authorize claims
  * validator catches tampered safety flag, missing required asset, missing
    QA check group, missing QA report-schema field, forbidden phrase
  * validator tool is stdlib-only; no network/broker/exchange imports
  * Crypto-D1 dataset manifest validator still passes (companion document)
  * Crypto-D1 data contract validator still passes (companion document)
  * Crypto-D1 protocol validator still passes (companion document)
  * arbitrage readiness validator still passes (parallel lane unaffected)
  * candidate registry can build after the spec exists, crypto_d1 candidate
    remains WATCH (never ACTIVE, never STRONG)
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

import crypto_d1_qa_freeze_spec_check as cqf       # noqa: E402
import crypto_d1_dataset_manifest_check as cdm     # noqa: E402
import crypto_d1_data_contract_check as cdc        # noqa: E402
import crypto_d1_protocol_check as cdpc            # noqa: E402
import arbitrage_readiness_gate_check as argc      # noqa: E402
import strategy_candidate_registry as scr          # noqa: E402
import strategy_next_bundle as snb                 # noqa: E402

TOOL_FILE = _TOOLS_DIR / "crypto_d1_qa_freeze_spec_check.py"
SPEC_JSON_PATH = _REPO_ROOT / cqf.SPEC_DIR_REL / cqf.SPEC_JSON
SPEC_MD_PATH = _REPO_ROOT / cqf.SPEC_DIR_REL / cqf.SPEC_MD


# --- existence + validation ---------------------------------------------- #

def test_spec_json_exists():
    assert SPEC_JSON_PATH.exists(), f"missing: {SPEC_JSON_PATH}"


def test_spec_md_exists():
    assert SPEC_MD_PATH.exists(), f"missing: {SPEC_MD_PATH}"


def test_validator_passes_on_committed_spec():
    ok, errs = cqf.validate(_REPO_ROOT)
    assert ok, errs


def test_seven_flags_all_false():
    data = json.loads(SPEC_JSON_PATH.read_text(encoding="utf-8"))
    for flag in cqf.MUST_BE_FALSE_FLAGS:
        assert data.get(flag) is False, f"{flag} must be False"
    assert data.get("research_only") is True


def test_required_top_level_sections_present():
    data = json.loads(SPEC_JSON_PATH.read_text(encoding="utf-8"))
    for k in cqf.REQUIRED_TOP_LEVEL_KEYS:
        assert k in data, f"missing top-level key: {k}"


def test_target_assets_include_btc_eth_sol():
    data = json.loads(SPEC_JSON_PATH.read_text(encoding="utf-8"))
    canonical = {a.get("symbol_canonical")
                 for a in data["target_assets"] if isinstance(a, dict)}
    for asset in ("BTC", "ETH", "SOL"):
        assert asset in canonical, f"missing required canonical symbol: {asset}"


def test_timeframe_is_daily_only():
    data = json.loads(SPEC_JSON_PATH.read_text(encoding="utf-8"))
    tf = data["timeframe"]
    assert tf["primary"] == "1d"
    assert tf["intraday_explicitly_out_of_scope"] is True


def test_spot_only_perps_forbidden_distinction():
    data = json.loads(SPEC_JSON_PATH.read_text(encoding="utf-8"))
    assert data["allowed_market_type"] == "spot"
    forbidden_joined = " ".join(data["forbidden_market_types"]).lower()
    assert "perp" in forbidden_joined
    assert "dated_futures" in forbidden_joined
    assert "options" in forbidden_joined
    assert "leveraged" in forbidden_joined


def test_qa_check_groups_all_present():
    data = json.loads(SPEC_JSON_PATH.read_text(encoding="utf-8"))
    cg = data["QA_check_groups"]
    for grp in cqf.REQUIRED_QA_CHECK_GROUPS:
        assert grp in cg, f"QA_check_groups missing group: {grp}"


def test_per_group_qa_check_sections_populated():
    data = json.loads(SPEC_JSON_PATH.read_text(encoding="utf-8"))
    for section in cqf.REQUIRED_PER_GROUP_DICT_SECTIONS:
        v = data[section]
        assert isinstance(v, dict) and v, f"{section} must be a non-empty dict"


def test_qa_status_model_contains_all_required_statuses():
    data = json.loads(SPEC_JSON_PATH.read_text(encoding="utf-8"))
    qa = data["QA_status_model"]
    for status in cqf.REQUIRED_QA_STATUSES:
        assert status in qa, f"QA_status_model missing status: {status}"
    assert len(qa) >= 6


def test_qa_report_schema_required_fields_all_present():
    data = json.loads(SPEC_JSON_PATH.read_text(encoding="utf-8"))
    qrs = data["QA_report_schema"]
    rf = set(qrs["required_fields"])
    for fld in cqf.REQUIRED_QA_REPORT_FIELDS:
        assert fld in rf, f"QA_report_schema missing field: {fld}"
    assert len(qrs["required_fields"]) == 26
    assert qrs.get("field_count") == 26


def test_freeze_rules_require_frozen_checksums_version_utc_daily():
    data = json.loads(SPEC_JSON_PATH.read_text(encoding="utf-8"))
    fr = data["freeze_rules"]
    for k in cqf.REQUIRED_FREEZE_RULE_KEYS:
        assert k in fr, f"freeze_rules missing key: {k}"
    assert fr["daily_bars_must_be_utc_normalized"] is True
    assert fr["weekday_only_calendars_forbidden"] is True
    assert fr["data_change_creates_new_dataset_version"] is True
    assert fr["manual_edits_invalid_unless_documented_and_revalidated"] is True


def test_allowed_and_forbidden_next_steps_nonempty():
    data = json.loads(SPEC_JSON_PATH.read_text(encoding="utf-8"))
    assert isinstance(data["allowed_next_steps"], list) and data["allowed_next_steps"]
    assert isinstance(data["forbidden_next_steps"], list) and data["forbidden_next_steps"]


def test_no_real_data_files_created():
    bundle_dir = _REPO_ROOT / cqf.SPEC_DIR_REL
    files = sorted(p.name for p in bundle_dir.iterdir() if p.is_file())
    expected = {"qa_freeze_spec.json", "qa_freeze_spec.md",
                "report.json", "report.md"}
    forbidden_extensions = (".csv", ".parquet", ".pq", ".pickle", ".feather", ".h5")
    for name in files:
        for ext in forbidden_extensions:
            assert not name.lower().endswith(ext), f"unexpected real data file: {name}"
    assert set(files) == expected, f"unexpected files in bundle dir: {sorted(set(files) - expected)}"


def test_no_profitability_or_fetch_or_backtest_claims():
    md = SPEC_MD_PATH.read_text(encoding="utf-8").lower()
    jsn = json.dumps(json.loads(SPEC_JSON_PATH.read_text(encoding="utf-8")),
                    ensure_ascii=False).lower()
    for phrase in cqf.FORBIDDEN_PHRASES:
        assert phrase.lower() not in md, f"forbidden phrase in MD: {phrase!r}"
        assert phrase.lower() not in jsn, f"forbidden phrase in JSON: {phrase!r}"


def test_distinction_phrases_present_in_md():
    md = SPEC_MD_PATH.read_text(encoding="utf-8")
    for phrase in cqf.DISTINCTION_PHRASES:
        assert phrase in md, f"distinction phrase missing: {phrase!r}"


# --- validator failure modes --------------------------------------------- #

def _stage_tmp(tmp_path: Path):
    tmp_dir = tmp_path / cqf.SPEC_DIR_REL
    tmp_dir.mkdir(parents=True, exist_ok=True)
    (tmp_dir / cqf.SPEC_MD).write_text(
        SPEC_MD_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    data = json.loads(SPEC_JSON_PATH.read_text(encoding="utf-8"))
    return tmp_dir, data


def test_validator_detects_tampered_safety_flag(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["backtest_enabled"] = True
    (tmp_dir / cqf.SPEC_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = cqf.validate(tmp_path)
    assert not ok
    assert any("backtest_enabled" in e for e in errs)


def test_validator_detects_missing_required_asset(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["target_assets"] = [a for a in data["target_assets"]
                             if a.get("symbol_canonical") != "BTC"]
    (tmp_dir / cqf.SPEC_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = cqf.validate(tmp_path)
    assert not ok
    assert any("BTC" in e for e in errs)


def test_validator_detects_missing_qa_check_group(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    del data["QA_check_groups"]["F_fee_slippage"]
    (tmp_dir / cqf.SPEC_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = cqf.validate(tmp_path)
    assert not ok
    assert any("F_fee_slippage" in e for e in errs)


def test_validator_detects_missing_qa_report_schema_field(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["QA_report_schema"]["required_fields"] = [
        f for f in data["QA_report_schema"]["required_fields"]
        if f != "blocking_failures"
    ]
    (tmp_dir / cqf.SPEC_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = cqf.validate(tmp_path)
    assert not ok
    assert any("blocking_failures" in e for e in errs)


def test_validator_detects_non_spot_market(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["allowed_market_type"] = "perp_futures"
    (tmp_dir / cqf.SPEC_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = cqf.validate(tmp_path)
    assert not ok
    assert any("allowed_market_type must be 'spot'" in e for e in errs)


def test_validator_detects_missing_qa_status(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    del data["QA_status_model"]["QA_BLOCKED"]
    (tmp_dir / cqf.SPEC_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = cqf.validate(tmp_path)
    assert not ok
    assert any("QA_BLOCKED" in e for e in errs)


def test_validator_detects_forbidden_phrase_in_md(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    (tmp_dir / cqf.SPEC_JSON).write_text(json.dumps(data), encoding="utf-8")
    md = SPEC_MD_PATH.read_text(encoding="utf-8") + "\nNote: this is profitable.\n"
    (tmp_dir / cqf.SPEC_MD).write_text(md, encoding="utf-8")
    ok, errs = cqf.validate(tmp_path)
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
    assert cqf.main(["validate", "--repo-root", str(_REPO_ROOT)]) == 0
    assert cqf.main(["show", "--repo-root", str(_REPO_ROOT)]) == 0


# --- integration tests --------------------------------------------------- #

def test_crypto_d1_dataset_manifest_validator_still_passes():
    ok, errs = cdm.validate(_REPO_ROOT)
    assert ok, errs


def test_crypto_d1_data_contract_validator_still_passes():
    ok, errs = cdc.validate(_REPO_ROOT)
    assert ok, errs


def test_crypto_d1_protocol_validator_still_passes():
    ok, errs = cdpc.validate(_REPO_ROOT)
    assert ok, errs


def test_arbitrage_readiness_validator_still_passes():
    ok, errs = argc.validate(_REPO_ROOT)
    assert ok, errs


def test_candidate_registry_classifies_crypto_d1_as_WATCH_after_spec():
    payload = scr.generate(_REPO_ROOT)
    cd1 = next(c for c in payload["candidates"]
              if c["candidate_id"] == "crypto_d1_protocol")
    assert cd1["status"] == "WATCH", cd1
    assert cd1["status"] != "ACTIVE"
    assert cd1["evidence_level"] != "STRONG"
    assert cd1["evidence_level"] in ("NONE", "MIXED"), cd1
    # New qa/freeze docs should now appear in source_reports.
    for needed in ("qa_freeze_spec.md", "qa_freeze_spec.json"):
        assert needed in cd1["source_reports"], cd1["source_reports"]
    # Prior bundle docs still there.
    for prior in ("protocol.md", "protocol.json",
                  "data_contract.md", "data_contract.json",
                  "dataset_manifest.md", "dataset_manifest.json"):
        assert prior in cd1["source_reports"]


def test_next_bundle_generator_still_validates_after_spec():
    snb.generate(_REPO_ROOT)
    ok, errs = snb.validate(_REPO_ROOT)
    assert ok, errs
