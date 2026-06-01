"""Bundle 12 -- Crypto-D1 Data Contract v1 tests (research-only).

Pure stdlib + pytest. Asserts:
  * data_contract.json exists and validates
  * all seven execution / fetch / connection / backtest / dataset-processing
    flags are pinned False
  * all required top-level sections exist
  * target assets include BTC, ETH, SOL
  * timeframe is daily only; intraday explicitly out of scope
  * spot-only / perps-forbidden distinction is preserved
  * required OHLCV columns exist
  * UTC + 24/7 session rules exist
  * missing-day and duplicate rules exist
  * fee + slippage requirements exist
  * no profitability / fetch / backtest-authorize claims
  * validator catches tampered safety flag, missing required asset, missing
    required column, forbidden phrase
  * validator tool is stdlib-only; no network/broker/exchange imports
  * Crypto-D1 protocol validator still passes (companion document)
  * arbitrage readiness validator still passes (parallel lane unaffected)
  * candidate registry can build after the data contract exists, crypto_d1
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

import crypto_d1_data_contract_check as cdc       # noqa: E402
import crypto_d1_protocol_check as cdpc           # noqa: E402
import arbitrage_readiness_gate_check as argc     # noqa: E402
import strategy_candidate_registry as scr         # noqa: E402
import strategy_next_bundle as snb                # noqa: E402

TOOL_FILE = _TOOLS_DIR / "crypto_d1_data_contract_check.py"
CONTRACT_JSON_PATH = _REPO_ROOT / cdc.CONTRACT_DIR_REL / cdc.CONTRACT_JSON
CONTRACT_MD_PATH = _REPO_ROOT / cdc.CONTRACT_DIR_REL / cdc.CONTRACT_MD


# --- existence + validation ---------------------------------------------- #

def test_data_contract_json_exists():
    assert CONTRACT_JSON_PATH.exists(), f"missing: {CONTRACT_JSON_PATH}"


def test_data_contract_md_exists():
    assert CONTRACT_MD_PATH.exists(), f"missing: {CONTRACT_MD_PATH}"


def test_validator_passes_on_committed_contract():
    ok, errs = cdc.validate(_REPO_ROOT)
    assert ok, errs


def test_seven_flags_all_false():
    data = json.loads(CONTRACT_JSON_PATH.read_text(encoding="utf-8"))
    for flag in cdc.MUST_BE_FALSE_FLAGS:
        assert data.get(flag) is False, f"{flag} must be False"
    assert data.get("research_only") is True


def test_required_top_level_sections_present():
    data = json.loads(CONTRACT_JSON_PATH.read_text(encoding="utf-8"))
    for k in cdc.REQUIRED_TOP_LEVEL_KEYS:
        assert k in data, f"missing top-level key: {k}"


def test_target_assets_include_btc_eth_sol():
    data = json.loads(CONTRACT_JSON_PATH.read_text(encoding="utf-8"))
    canonical = {a.get("symbol_canonical")
                 for a in data["target_assets"] if isinstance(a, dict)}
    for asset in ("BTC", "ETH", "SOL"):
        assert asset in canonical, f"missing required canonical symbol: {asset}"


def test_timeframe_is_daily_only():
    data = json.loads(CONTRACT_JSON_PATH.read_text(encoding="utf-8"))
    tf = data["timeframe"]
    assert tf["primary"] == "1d"
    assert tf["intraday_explicitly_out_of_scope"] is True


def test_spot_only_perps_forbidden_distinction():
    data = json.loads(CONTRACT_JSON_PATH.read_text(encoding="utf-8"))
    assert data["allowed_market_type"] == "spot"
    forbidden_joined = " ".join(data["forbidden_market_types"]).lower()
    assert "perp" in forbidden_joined, "perp futures must be in forbidden_market_types"
    assert "dated_futures" in forbidden_joined
    assert "options" in forbidden_joined
    assert "leveraged" in forbidden_joined


def test_required_ohlcv_columns_present():
    data = json.loads(CONTRACT_JSON_PATH.read_text(encoding="utf-8"))
    rc = {str(c).strip().lower() for c in data["required_columns"]}
    for col in cdc.REQUIRED_COLUMNS:
        assert col in rc, f"required_columns missing column: {col}"


def test_utc_and_24_7_session_rules():
    data = json.loads(CONTRACT_JSON_PATH.read_text(encoding="utf-8"))
    ts = data["timestamp_requirements"]
    assert "UTC" in ts["primary_clock"]
    assert "24/7" in ts["session_handling"]
    sr = data["session_requirements"]
    assert "24/7" in sr["calendar"]
    assert sr["weekday_only_filters_forbidden"] is True


def test_missing_day_and_duplicate_rules_exist():
    data = json.loads(CONTRACT_JSON_PATH.read_text(encoding="utf-8"))
    md_rules = data["missing_data_rules"]
    assert md_rules["no_silent_forward_fill"] is True
    assert md_rules["missing_day_flagged_in_manifest"] is True
    assert md_rules["missing_close_invalid"] is True
    assert md_rules["missing_timestamp_invalid"] is True
    dup_rules = data["duplicate_data_rules"]
    assert dup_rules["duplicate_symbol_timestamp_rejected"] is True
    assert dup_rules["duplicate_row_rejected"] is True


def test_fee_slippage_requirements_exist():
    data = json.loads(CONTRACT_JSON_PATH.read_text(encoding="utf-8"))
    fs = data["fee_slippage_requirements"]
    for k in cdc.REQUIRED_FEE_SLIPPAGE_KEYS:
        assert k in fs, f"fee_slippage_requirements missing key: {k}"


def test_ohlcv_self_consistency_rules_encoded():
    data = json.loads(CONTRACT_JSON_PATH.read_text(encoding="utf-8"))
    oh = data["ohlcv_requirements"]
    assert "max(open" in oh["high_rule"]
    assert "min(open" in oh["low_rule"]
    assert oh["open_close_positive"] is True
    assert oh["volume_non_negative"] is True
    assert oh["duplicate_row_invalid"] is True


def test_minimum_viable_dataset_btc_required():
    data = json.loads(CONTRACT_JSON_PATH.read_text(encoding="utf-8"))
    mvd = data["minimum_viable_dataset"]
    assert "BTC" in mvd["assets_required"]
    assert mvd["frozen_sha256_required"] is True
    assert mvd["manifest_required"] is True
    assert mvd["contract_version_pinned"] is True
    assert mvd["is_window_sealed_before_run"] is True
    assert mvd["oos_window_sealed_before_run"] is True


def test_no_profitability_or_fetch_or_backtest_claims():
    md = CONTRACT_MD_PATH.read_text(encoding="utf-8").lower()
    jsn = json.dumps(json.loads(CONTRACT_JSON_PATH.read_text(encoding="utf-8")),
                    ensure_ascii=False).lower()
    for phrase in cdc.FORBIDDEN_PHRASES:
        assert phrase.lower() not in md, f"forbidden phrase in MD: {phrase!r}"
        assert phrase.lower() not in jsn, f"forbidden phrase in JSON: {phrase!r}"


def test_distinction_phrases_present_in_md():
    md = CONTRACT_MD_PATH.read_text(encoding="utf-8")
    for phrase in cdc.DISTINCTION_PHRASES:
        assert phrase in md, f"distinction phrase missing: {phrase!r}"


# --- validator failure modes --------------------------------------------- #

def _stage_tmp(tmp_path: Path):
    tmp_dir = tmp_path / cdc.CONTRACT_DIR_REL
    tmp_dir.mkdir(parents=True, exist_ok=True)
    (tmp_dir / cdc.CONTRACT_MD).write_text(
        CONTRACT_MD_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    data = json.loads(CONTRACT_JSON_PATH.read_text(encoding="utf-8"))
    return tmp_dir, data


def test_validator_detects_tampered_safety_flag(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["data_fetch_enabled"] = True
    (tmp_dir / cdc.CONTRACT_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = cdc.validate(tmp_path)
    assert not ok
    assert any("data_fetch_enabled" in e for e in errs)


def test_validator_detects_missing_required_asset(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["target_assets"] = [a for a in data["target_assets"]
                             if a.get("symbol_canonical") != "SOL"]
    (tmp_dir / cdc.CONTRACT_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = cdc.validate(tmp_path)
    assert not ok
    assert any("SOL" in e for e in errs)


def test_validator_detects_missing_required_column(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["required_columns"] = [c for c in data["required_columns"] if c != "volume"]
    (tmp_dir / cdc.CONTRACT_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = cdc.validate(tmp_path)
    assert not ok
    assert any("volume" in e for e in errs)


def test_validator_detects_non_spot_market(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["allowed_market_type"] = "perp_futures"
    (tmp_dir / cdc.CONTRACT_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = cdc.validate(tmp_path)
    assert not ok
    assert any("allowed_market_type must be 'spot'" in e for e in errs)


def test_validator_detects_forbidden_phrase_in_md(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    (tmp_dir / cdc.CONTRACT_JSON).write_text(json.dumps(data), encoding="utf-8")
    md = CONTRACT_MD_PATH.read_text(encoding="utf-8") + "\nNote: guaranteed profit.\n"
    (tmp_dir / cdc.CONTRACT_MD).write_text(md, encoding="utf-8")
    ok, errs = cdc.validate(tmp_path)
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
    assert cdc.main(["validate", "--repo-root", str(_REPO_ROOT)]) == 0
    assert cdc.main(["show", "--repo-root", str(_REPO_ROOT)]) == 0


# --- integration tests --------------------------------------------------- #

def test_crypto_d1_protocol_validator_still_passes():
    ok, errs = cdpc.validate(_REPO_ROOT)
    assert ok, errs


def test_arbitrage_readiness_validator_still_passes():
    ok, errs = argc.validate(_REPO_ROOT)
    assert ok, errs


def test_candidate_registry_classifies_crypto_d1_as_WATCH_after_data_contract():
    payload = scr.generate(_REPO_ROOT)
    cd1 = next(c for c in payload["candidates"]
              if c["candidate_id"] == "crypto_d1_protocol")
    # The protocol memo + data contract are on disk; lane_status_override
    # keeps crypto_d1 at WATCH. Never ACTIVE, never STRONG.
    assert cd1["status"] == "WATCH", cd1
    assert cd1["status"] != "ACTIVE"
    assert cd1["evidence_level"] != "STRONG"
    assert cd1["evidence_level"] in ("NONE", "MIXED"), cd1
    # The new data-contract docs should now appear in source_reports.
    for needed in ("data_contract.md", "data_contract.json"):
        assert needed in cd1["source_reports"], cd1["source_reports"]
    # The Bundle-11 protocol docs are still there.
    assert "protocol.md" in cd1["source_reports"]
    assert "protocol.json" in cd1["source_reports"]


def test_next_bundle_generator_still_validates_after_data_contract():
    snb.generate(_REPO_ROOT)
    ok, errs = snb.validate(_REPO_ROOT)
    assert ok, errs
