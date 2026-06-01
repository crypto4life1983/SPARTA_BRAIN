"""Bundle 13 -- Crypto-D1 Dataset Manifest v1 tests (research-only).

Pure stdlib + pytest. Asserts:
  * dataset_manifest.json exists and validates
  * all seven execution / fetch / connection / backtest / dataset-processing
    flags are pinned False
  * all required top-level sections exist
  * target assets include BTC, ETH, SOL
  * timeframe is daily only; intraday explicitly out of scope
  * spot-only / perps-forbidden distinction is preserved
  * manifest_schema.required_fields contains all 35 future manifest fields
  * qa_status_model contains all 7 declared statuses
  * freeze rules require UTC daily bars + forbid weekday-only calendars
  * allowed_file_formats includes CSV / Parquet / JSON manifest / Markdown
  * forbidden_inputs includes screenshots / manually copied / scraped / no-
    provenance / no-checksums / no-manifest / credentials
  * no real data files were created
  * no profitability / fetch / backtest-authorize claims in MD or JSON
  * validator catches tampered safety flag, missing required asset, missing
    required future-manifest field, forbidden phrase
  * validator tool is stdlib-only; no network/broker/exchange imports
  * Crypto-D1 data contract validator still passes (companion document)
  * Crypto-D1 protocol validator still passes (companion document)
  * arbitrage readiness validator still passes (parallel lane unaffected)
  * candidate registry can build after the manifest exists, crypto_d1
    candidate remains WATCH (never ACTIVE, never STRONG)
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

import crypto_d1_dataset_manifest_check as cdm     # noqa: E402
import crypto_d1_data_contract_check as cdc        # noqa: E402
import crypto_d1_protocol_check as cdpc            # noqa: E402
import arbitrage_readiness_gate_check as argc      # noqa: E402
import strategy_candidate_registry as scr          # noqa: E402
import strategy_next_bundle as snb                 # noqa: E402

TOOL_FILE = _TOOLS_DIR / "crypto_d1_dataset_manifest_check.py"
MANIFEST_JSON_PATH = _REPO_ROOT / cdm.MANIFEST_DIR_REL / cdm.MANIFEST_JSON
MANIFEST_MD_PATH = _REPO_ROOT / cdm.MANIFEST_DIR_REL / cdm.MANIFEST_MD


# --- existence + validation ---------------------------------------------- #

def test_dataset_manifest_json_exists():
    assert MANIFEST_JSON_PATH.exists(), f"missing: {MANIFEST_JSON_PATH}"


def test_dataset_manifest_md_exists():
    assert MANIFEST_MD_PATH.exists(), f"missing: {MANIFEST_MD_PATH}"


def test_validator_passes_on_committed_manifest():
    ok, errs = cdm.validate(_REPO_ROOT)
    assert ok, errs


def test_seven_flags_all_false():
    data = json.loads(MANIFEST_JSON_PATH.read_text(encoding="utf-8"))
    for flag in cdm.MUST_BE_FALSE_FLAGS:
        assert data.get(flag) is False, f"{flag} must be False"
    assert data.get("research_only") is True


def test_required_top_level_sections_present():
    data = json.loads(MANIFEST_JSON_PATH.read_text(encoding="utf-8"))
    for k in cdm.REQUIRED_TOP_LEVEL_KEYS:
        assert k in data, f"missing top-level key: {k}"


def test_target_assets_include_btc_eth_sol():
    data = json.loads(MANIFEST_JSON_PATH.read_text(encoding="utf-8"))
    canonical = {a.get("symbol_canonical")
                 for a in data["target_assets"] if isinstance(a, dict)}
    for asset in ("BTC", "ETH", "SOL"):
        assert asset in canonical, f"missing required canonical symbol: {asset}"


def test_timeframe_is_daily_only():
    data = json.loads(MANIFEST_JSON_PATH.read_text(encoding="utf-8"))
    tf = data["timeframe"]
    assert tf["primary"] == "1d"
    assert tf["intraday_explicitly_out_of_scope"] is True


def test_spot_only_perps_forbidden_distinction():
    data = json.loads(MANIFEST_JSON_PATH.read_text(encoding="utf-8"))
    assert data["allowed_market_type"] == "spot"
    forbidden_joined = " ".join(data["forbidden_market_types"]).lower()
    assert "perp" in forbidden_joined
    assert "dated_futures" in forbidden_joined
    assert "options" in forbidden_joined
    assert "leveraged" in forbidden_joined


def test_manifest_schema_required_fields_all_present():
    data = json.loads(MANIFEST_JSON_PATH.read_text(encoding="utf-8"))
    ms = data["manifest_schema"]
    rf = set(ms["required_fields"])
    for fld in cdm.REQUIRED_FUTURE_MANIFEST_FIELDS:
        assert fld in rf, f"required future-manifest field missing: {fld}"
    assert len(ms["required_fields"]) == 35
    assert ms.get("field_count") == 35


def test_qa_status_model_contains_all_required_statuses():
    data = json.loads(MANIFEST_JSON_PATH.read_text(encoding="utf-8"))
    qa = data["qa_status_model"]
    for status in cdm.REQUIRED_QA_STATUSES:
        assert status in qa, f"qa_status_model missing status: {status}"
    assert len(qa) >= 7


def test_freeze_rules_require_utc_daily_bars_and_forbid_weekday_only():
    data = json.loads(MANIFEST_JSON_PATH.read_text(encoding="utf-8"))
    fr = data["freeze_fields"]
    assert fr["daily_bars_must_be_utc_normalized"] is True
    assert fr["weekday_only_calendars_forbidden"] is True
    assert fr["no_mutable_data_in_backtest"]
    assert fr["data_change_creates_new_dataset_version"] is True
    assert fr["manual_edits_invalid_unless_documented_and_revalidated"] is True


def test_allowed_file_formats_include_csv_parquet_json_md():
    data = json.loads(MANIFEST_JSON_PATH.read_text(encoding="utf-8"))
    joined = " ".join(data["allowed_file_formats"])
    for needle in cdm.REQUIRED_ALLOWED_FILE_FORMAT_NEEDLES:
        assert needle in joined, f"allowed_file_formats missing: {needle!r}"


def test_forbidden_inputs_cover_required_categories():
    data = json.loads(MANIFEST_JSON_PATH.read_text(encoding="utf-8"))
    joined = " ".join(data["forbidden_inputs"]).lower()
    for needle in ("screenshot", "manually copied", "scraped",
                   "without provenance", "without checksums",
                   "without a manifest", "credentials"):
        assert needle in joined, f"forbidden_inputs missing needle: {needle!r}"


def test_no_real_data_files_created():
    # Only the four spec files should live under the bundle's reports dir.
    bundle_dir = _REPO_ROOT / cdm.MANIFEST_DIR_REL
    files = sorted(p.name for p in bundle_dir.iterdir() if p.is_file())
    expected = {"dataset_manifest.json", "dataset_manifest.md",
                "report.json", "report.md"}
    # No CSV / Parquet / OHLCV file should be present.
    forbidden_extensions = (".csv", ".parquet", ".pq", ".pickle", ".feather", ".h5")
    for name in files:
        for ext in forbidden_extensions:
            assert not name.lower().endswith(ext), f"unexpected real data file: {name}"
    assert set(files) == expected, f"unexpected files in bundle dir: {sorted(set(files) - expected)}"


def test_no_profitability_or_fetch_or_backtest_claims():
    md = MANIFEST_MD_PATH.read_text(encoding="utf-8").lower()
    jsn = json.dumps(json.loads(MANIFEST_JSON_PATH.read_text(encoding="utf-8")),
                    ensure_ascii=False).lower()
    for phrase in cdm.FORBIDDEN_PHRASES:
        assert phrase.lower() not in md, f"forbidden phrase in MD: {phrase!r}"
        assert phrase.lower() not in jsn, f"forbidden phrase in JSON: {phrase!r}"


def test_distinction_phrases_present_in_md():
    md = MANIFEST_MD_PATH.read_text(encoding="utf-8")
    for phrase in cdm.DISTINCTION_PHRASES:
        assert phrase in md, f"distinction phrase missing: {phrase!r}"


# --- validator failure modes --------------------------------------------- #

def _stage_tmp(tmp_path: Path):
    tmp_dir = tmp_path / cdm.MANIFEST_DIR_REL
    tmp_dir.mkdir(parents=True, exist_ok=True)
    (tmp_dir / cdm.MANIFEST_MD).write_text(
        MANIFEST_MD_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    data = json.loads(MANIFEST_JSON_PATH.read_text(encoding="utf-8"))
    return tmp_dir, data


def test_validator_detects_tampered_safety_flag(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["dataset_processing_enabled"] = True
    (tmp_dir / cdm.MANIFEST_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = cdm.validate(tmp_path)
    assert not ok
    assert any("dataset_processing_enabled" in e for e in errs)


def test_validator_detects_missing_required_asset(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["target_assets"] = [a for a in data["target_assets"]
                             if a.get("symbol_canonical") != "ETH"]
    (tmp_dir / cdm.MANIFEST_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = cdm.validate(tmp_path)
    assert not ok
    assert any("ETH" in e for e in errs)


def test_validator_detects_missing_required_future_manifest_field(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["manifest_schema"]["required_fields"] = [
        f for f in data["manifest_schema"]["required_fields"]
        if f != "checksum_policy"
    ]
    (tmp_dir / cdm.MANIFEST_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = cdm.validate(tmp_path)
    assert not ok
    assert any("checksum_policy" in e for e in errs)


def test_validator_detects_non_spot_market(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["allowed_market_type"] = "perp_futures"
    (tmp_dir / cdm.MANIFEST_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = cdm.validate(tmp_path)
    assert not ok
    assert any("allowed_market_type must be 'spot'" in e for e in errs)


def test_validator_detects_missing_qa_status(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    del data["qa_status_model"]["QA_WARN"]
    (tmp_dir / cdm.MANIFEST_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = cdm.validate(tmp_path)
    assert not ok
    assert any("QA_WARN" in e for e in errs)


def test_validator_detects_forbidden_phrase_in_md(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    (tmp_dir / cdm.MANIFEST_JSON).write_text(json.dumps(data), encoding="utf-8")
    md = MANIFEST_MD_PATH.read_text(encoding="utf-8") + "\nNote: we have an edge.\n"
    (tmp_dir / cdm.MANIFEST_MD).write_text(md, encoding="utf-8")
    ok, errs = cdm.validate(tmp_path)
    assert not ok
    assert any("we have an edge" in e for e in errs)


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
    assert cdm.main(["validate", "--repo-root", str(_REPO_ROOT)]) == 0
    assert cdm.main(["show", "--repo-root", str(_REPO_ROOT)]) == 0


# --- integration tests --------------------------------------------------- #

def test_crypto_d1_data_contract_validator_still_passes():
    ok, errs = cdc.validate(_REPO_ROOT)
    assert ok, errs


def test_crypto_d1_protocol_validator_still_passes():
    ok, errs = cdpc.validate(_REPO_ROOT)
    assert ok, errs


def test_arbitrage_readiness_validator_still_passes():
    ok, errs = argc.validate(_REPO_ROOT)
    assert ok, errs


def test_candidate_registry_classifies_crypto_d1_as_WATCH_after_manifest():
    payload = scr.generate(_REPO_ROOT)
    cd1 = next(c for c in payload["candidates"]
              if c["candidate_id"] == "crypto_d1_protocol")
    # Protocol + data contract + dataset manifest are all on disk; the
    # lane_status_override keeps crypto_d1 at WATCH. Never ACTIVE, never STRONG.
    assert cd1["status"] == "WATCH", cd1
    assert cd1["status"] != "ACTIVE"
    assert cd1["evidence_level"] != "STRONG"
    assert cd1["evidence_level"] in ("NONE", "MIXED"), cd1
    # The new manifest docs should now appear in source_reports.
    for needed in ("dataset_manifest.md", "dataset_manifest.json"):
        assert needed in cd1["source_reports"], cd1["source_reports"]
    # The Bundle-11 protocol and Bundle-12 data-contract docs are still there.
    for prior in ("protocol.md", "protocol.json",
                  "data_contract.md", "data_contract.json"):
        assert prior in cd1["source_reports"]


def test_next_bundle_generator_still_validates_after_manifest():
    snb.generate(_REPO_ROOT)
    ok, errs = snb.validate(_REPO_ROOT)
    assert ok, errs
