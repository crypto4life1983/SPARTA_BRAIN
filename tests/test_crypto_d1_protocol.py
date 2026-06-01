"""Bundle 11 — Crypto-D1 Protocol Memo v1 tests (research-only).

Pure stdlib + pytest. Asserts:
  * protocol.json exists and validates
  * the seven execution / fetch / connection / backtest / dataset-processing
    flags are pinned False
  * all required top-level sections exist
  * target assets include BTC, ETH, SOL
  * timeframe is daily only; intraday explicitly out of scope
  * spot-first / perps-later distinction exists
  * 24/7 session handling + missing-day rules exist
  * validation phases include P0..P8
  * pass/watch/fail rules exist
  * no profitability claim, no fetch claim, no backtest-authorize claim
  * validator catches tampered flag / missing target asset / non-spot market /
    intraday allowed / forbidden phrase
  * validator tool is stdlib-only; no network/broker/exchange imports
  * candidate registry builds and classifies crypto_d1 as WATCH after the
    new v1 memo exists (lane_status_override applies because the seed's
    extra_files now exist on disk); guardrails held -- never ACTIVE / STRONG
  * arbitrage readiness validator still passes (parallel lane unaffected)
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

import crypto_d1_protocol_check as cdpc                  # noqa: E402
import arbitrage_readiness_gate_check as argc            # noqa: E402
import strategy_candidate_registry as scr                # noqa: E402
import strategy_next_bundle as snb                       # noqa: E402

TOOL_FILE = _TOOLS_DIR / "crypto_d1_protocol_check.py"
PROTO_JSON_PATH = _REPO_ROOT / cdpc.PROTO_DIR_REL / cdpc.PROTO_JSON
PROTO_MD_PATH = _REPO_ROOT / cdpc.PROTO_DIR_REL / cdpc.PROTO_MD


# --- existence + validation ---------------------------------------------- #

def test_protocol_json_exists():
    assert PROTO_JSON_PATH.exists(), f"missing: {PROTO_JSON_PATH}"


def test_protocol_md_exists():
    assert PROTO_MD_PATH.exists(), f"missing: {PROTO_MD_PATH}"


def test_validator_passes_on_committed_protocol():
    ok, errs = cdpc.validate(_REPO_ROOT)
    assert ok, errs


def test_seven_flags_all_false():
    data = json.loads(PROTO_JSON_PATH.read_text(encoding="utf-8"))
    for flag in cdpc.MUST_BE_FALSE_FLAGS:
        assert data.get(flag) is False, f"{flag} must be False"
    assert data.get("research_only") is True


def test_required_top_level_sections_present():
    data = json.loads(PROTO_JSON_PATH.read_text(encoding="utf-8"))
    for k in cdpc.REQUIRED_TOP_LEVEL_KEYS:
        assert k in data, f"missing top-level key: {k}"


def test_target_assets_include_btc_eth_sol():
    data = json.loads(PROTO_JSON_PATH.read_text(encoding="utf-8"))
    canonical = {a.get("symbol_canonical") for a in data["target_assets"] if isinstance(a, dict)}
    for asset in ("BTC", "ETH", "SOL"):
        assert asset in canonical, f"missing required canonical symbol: {asset}"


def test_timeframe_is_daily_only():
    data = json.loads(PROTO_JSON_PATH.read_text(encoding="utf-8"))
    tf = data["timeframe"]
    assert tf["primary"] == "1d"
    assert tf["intraday_explicitly_out_of_scope"] is True


def test_spot_first_perps_later_distinction():
    data = json.loads(PROTO_JSON_PATH.read_text(encoding="utf-8"))
    assert data["allowed_market_type"] == "spot"
    forbidden_joined = " ".join(data["forbidden_market_types"]).lower()
    assert "perp" in forbidden_joined, "perp futures must be in forbidden_market_types"


def test_24_7_session_handling_and_missing_day_rules():
    data = json.loads(PROTO_JSON_PATH.read_text(encoding="utf-8"))
    sm = data["session_model"]
    assert "24/7" in sm["market_calendar"]
    assert sm["weekday_only_filters_forbidden"] is True
    assert sm["missing_day_policy_documented_in_data_contract"] is True
    dr = data["data_requirements"]
    assert "24/7" in dr["session_handling"]
    assert "never silently forward-filled" in dr["missing_day_rules"].lower()


def test_validation_phases_p0_through_p8_present():
    data = json.loads(PROTO_JSON_PATH.read_text(encoding="utf-8"))
    phase_ids = {p["phase"] for p in data["validation_phases"] if isinstance(p, dict)}
    for required in cdpc.REQUIRED_VALIDATION_PHASES:
        assert required in phase_ids, f"missing phase: {required}"


def test_pass_watch_fail_rules_present():
    data = json.loads(PROTO_JSON_PATH.read_text(encoding="utf-8"))
    pwf = data["pass_watch_fail_rules"]
    for k in ("PASS", "WATCH", "FAIL"):
        assert k in pwf, f"pass_watch_fail_rules missing: {k}"


def test_seven_strategy_families_with_mean_reversion_watch_only():
    data = json.loads(PROTO_JSON_PATH.read_text(encoding="utf-8"))
    sf = data["candidate_strategy_families"]
    ids = {f.get("id") for f in sf if isinstance(f, dict)}
    for fid in cdpc.REQUIRED_STRATEGY_FAMILY_IDS:
        assert fid in ids, f"strategy family missing: {fid}"
    mr = next(f for f in sf if f.get("id") == "mean_reversion")
    assert mr["status"] == "WATCH_only"


def test_no_profitability_or_fetch_or_backtest_claims():
    md = PROTO_MD_PATH.read_text(encoding="utf-8").lower()
    jsn = json.dumps(json.loads(PROTO_JSON_PATH.read_text(encoding="utf-8")),
                    ensure_ascii=False).lower()
    for phrase in cdpc.FORBIDDEN_PHRASES:
        assert phrase.lower() not in md, f"forbidden phrase in MD: {phrase!r}"
        assert phrase.lower() not in jsn, f"forbidden phrase in JSON: {phrase!r}"


def test_distinction_phrases_present_in_md():
    md = PROTO_MD_PATH.read_text(encoding="utf-8")
    for phrase in cdpc.DISTINCTION_PHRASES:
        assert phrase in md, f"distinction phrase missing: {phrase!r}"


# --- validator failure modes --------------------------------------------- #

def _stage_tmp(tmp_path: Path):
    tmp_dir = tmp_path / cdpc.PROTO_DIR_REL
    tmp_dir.mkdir(parents=True, exist_ok=True)
    (tmp_dir / cdpc.PROTO_MD).write_text(PROTO_MD_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    data = json.loads(PROTO_JSON_PATH.read_text(encoding="utf-8"))
    return tmp_dir, data


def test_validator_detects_tampered_safety_flag(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["backtest_enabled"] = True
    (tmp_dir / cdpc.PROTO_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = cdpc.validate(tmp_path)
    assert not ok
    assert any("backtest_enabled" in e for e in errs)


def test_validator_detects_missing_target_asset(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["target_assets"] = [a for a in data["target_assets"]
                             if a.get("symbol_canonical") != "SOL"]
    (tmp_dir / cdpc.PROTO_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = cdpc.validate(tmp_path)
    assert not ok
    assert any("SOL" in e for e in errs)


def test_validator_detects_non_spot_market(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["allowed_market_type"] = "perp_futures"
    (tmp_dir / cdpc.PROTO_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = cdpc.validate(tmp_path)
    assert not ok
    assert any("allowed_market_type must be 'spot'" in e for e in errs)


def test_validator_detects_intraday_allowed(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["timeframe"]["intraday_explicitly_out_of_scope"] = False
    (tmp_dir / cdpc.PROTO_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = cdpc.validate(tmp_path)
    assert not ok
    assert any("intraday_explicitly_out_of_scope" in e for e in errs)


def test_validator_detects_forbidden_phrase_in_md(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    (tmp_dir / cdpc.PROTO_JSON).write_text(json.dumps(data), encoding="utf-8")
    md = PROTO_MD_PATH.read_text(encoding="utf-8") + "\nNote: guaranteed alpha.\n"
    (tmp_dir / cdpc.PROTO_MD).write_text(md, encoding="utf-8")
    ok, errs = cdpc.validate(tmp_path)
    assert not ok
    assert any("guaranteed alpha" in e for e in errs)


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
    assert cdpc.main(["validate", "--repo-root", str(_REPO_ROOT)]) == 0
    assert cdpc.main(["show", "--repo-root", str(_REPO_ROOT)]) == 0


# --- integration tests --------------------------------------------------- #

def test_arbitrage_readiness_validator_still_passes():
    ok, errs = argc.validate(_REPO_ROOT)
    assert ok, errs


def test_candidate_registry_classifies_crypto_d1_as_WATCH_after_v1_memo():
    payload = scr.generate(_REPO_ROOT)
    cd1 = next(c for c in payload["candidates"]
              if c["candidate_id"] == "crypto_d1_protocol")
    # With the v1 memo on disk, the seed's lane_status_override fires:
    # historically PARKED -> reset to WATCH.
    assert cd1["status"] == "WATCH", cd1
    # Never ACTIVE; STRONG forbidden by the registry's hard guardrail.
    assert cd1["status"] != "ACTIVE"
    assert cd1["evidence_level"] != "STRONG"
    assert cd1["evidence_level"] in ("NONE", "MIXED"), cd1
    # The new v1 memo should now appear in source_reports.
    for needed in ("protocol.md", "protocol.json"):
        assert needed in cd1["source_reports"], cd1["source_reports"]


def test_next_bundle_generator_still_validates_after_v1_memo():
    snb.generate(_REPO_ROOT)
    ok, errs = snb.validate(_REPO_ROOT)
    assert ok, errs
