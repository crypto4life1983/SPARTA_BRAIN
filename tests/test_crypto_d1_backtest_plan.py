"""Bundle 15 -- Crypto-D1 Baseline Backtest Plan v1 tests (research-only).

Pure stdlib + pytest. Asserts:
  * backtest_plan.json exists and validates
  * all seven execution / fetch / connection / backtest-execution /
    dataset-processing flags are pinned False
  * all required top-level sections exist
  * target assets include BTC, ETH, SOL
  * timeframe is daily only; intraday explicitly out of scope
  * spot-only / perps-forbidden distinction is preserved
  * all 6 baseline strategy families exist (buy_and_hold_benchmark /
    donchian / ma_trend_filter / momentum / vol_regime_gate / mean_reversion)
  * mean_reversion family carries WATCH_only status
  * buy_and_hold_benchmark carries benchmark status
  * parameter_policy forbids unlimited optimization / genetic search /
    AI-selected best on OOS / repeated tuning
  * required_dataset_gate enforces FROZEN + QA_PASS-or-approved-WARN +
    no-lookahead-check
  * report_schema.required_fields contains all 27 future report fields
  * metrics_required contains all 17 declared metrics
  * cost_model + slippage_model + position_sizing requirements populated
  * pass_watch_fail_rules + kill_conditions + forbidden_actions populated
  * no real data files or backtest output files were created
  * no profitability / fetch / backtest-authorize claims
  * validator catches tampered safety flag, missing required asset, missing
    strategy family, missing report-schema field, forbidden phrase
  * validator tool is stdlib-only; no network/broker/exchange imports
  * Crypto-D1 QA / Freeze validator still passes (companion document)
  * Crypto-D1 dataset manifest validator still passes (companion document)
  * Crypto-D1 data contract validator still passes (companion document)
  * Crypto-D1 protocol validator still passes (companion document)
  * arbitrage readiness validator still passes (parallel lane unaffected)
  * candidate registry can build after plan exists, crypto_d1 candidate
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

import crypto_d1_backtest_plan_check as cbp        # noqa: E402
import crypto_d1_qa_freeze_spec_check as cqf       # noqa: E402
import crypto_d1_dataset_manifest_check as cdm     # noqa: E402
import crypto_d1_data_contract_check as cdc        # noqa: E402
import crypto_d1_protocol_check as cdpc            # noqa: E402
import arbitrage_readiness_gate_check as argc      # noqa: E402
import strategy_candidate_registry as scr          # noqa: E402
import strategy_next_bundle as snb                 # noqa: E402

TOOL_FILE = _TOOLS_DIR / "crypto_d1_backtest_plan_check.py"
PLAN_JSON_PATH = _REPO_ROOT / cbp.PLAN_DIR_REL / cbp.PLAN_JSON
PLAN_MD_PATH = _REPO_ROOT / cbp.PLAN_DIR_REL / cbp.PLAN_MD


# --- existence + validation ---------------------------------------------- #

def test_plan_json_exists():
    assert PLAN_JSON_PATH.exists(), f"missing: {PLAN_JSON_PATH}"


def test_plan_md_exists():
    assert PLAN_MD_PATH.exists(), f"missing: {PLAN_MD_PATH}"


def test_validator_passes_on_committed_plan():
    ok, errs = cbp.validate(_REPO_ROOT)
    assert ok, errs


def test_seven_flags_all_false():
    data = json.loads(PLAN_JSON_PATH.read_text(encoding="utf-8"))
    for flag in cbp.MUST_BE_FALSE_FLAGS:
        assert data.get(flag) is False, f"{flag} must be False"
    assert data.get("research_only") is True


def test_required_top_level_sections_present():
    data = json.loads(PLAN_JSON_PATH.read_text(encoding="utf-8"))
    for k in cbp.REQUIRED_TOP_LEVEL_KEYS:
        assert k in data, f"missing top-level key: {k}"


def test_target_assets_include_btc_eth_sol():
    data = json.loads(PLAN_JSON_PATH.read_text(encoding="utf-8"))
    canonical = {a.get("symbol_canonical")
                 for a in data["target_assets"] if isinstance(a, dict)}
    for asset in ("BTC", "ETH", "SOL"):
        assert asset in canonical, f"missing required canonical symbol: {asset}"


def test_timeframe_is_daily_only():
    data = json.loads(PLAN_JSON_PATH.read_text(encoding="utf-8"))
    tf = data["timeframe"]
    assert tf["primary"] == "1d"
    assert tf["intraday_explicitly_out_of_scope"] is True


def test_spot_only_perps_forbidden_distinction():
    data = json.loads(PLAN_JSON_PATH.read_text(encoding="utf-8"))
    assert data["allowed_market_type"] == "spot"
    joined = " ".join(data["forbidden_market_types"]).lower()
    for needle in ("perp", "dated_futures", "options", "leveraged"):
        assert needle in joined, f"missing forbidden needle: {needle!r}"


def test_six_baseline_strategy_families_all_present():
    data = json.loads(PLAN_JSON_PATH.read_text(encoding="utf-8"))
    ids = {f.get("id") for f in data["baseline_strategy_families"] if isinstance(f, dict)}
    for fid in cbp.REQUIRED_STRATEGY_FAMILY_IDS:
        assert fid in ids, f"baseline_strategy_families missing id: {fid}"


def test_mean_reversion_is_watch_only_and_benchmark_is_benchmark():
    data = json.loads(PLAN_JSON_PATH.read_text(encoding="utf-8"))
    sf = {f.get("id"): f for f in data["baseline_strategy_families"] if isinstance(f, dict)}
    assert sf["mean_reversion"]["status"] == "WATCH_only"
    assert sf["buy_and_hold_benchmark"]["status"] == "benchmark"


def test_parameter_policy_forbids_unlimited_optimization():
    data = json.loads(PLAN_JSON_PATH.read_text(encoding="utf-8"))
    pp = data["parameter_policy"]
    for k in cbp.REQUIRED_PARAMETER_POLICY_KEYS:
        assert k in pp, f"parameter_policy missing: {k}"
    assert pp["no_unlimited_optimization"] is True
    assert pp["no_genetic_search"] is True
    assert pp["no_ai_selected_best_parameter_after_seeing_oos"] is True
    assert pp["no_repeated_tuning_on_oos"] is True
    assert pp["all_combinations_logged"] is True


def test_required_dataset_gate_enforces_frozen_qa_pass_no_lookahead():
    data = json.loads(PLAN_JSON_PATH.read_text(encoding="utf-8"))
    dg = data["required_dataset_gate"]
    for k in cbp.REQUIRED_DATASET_GATE_KEYS:
        assert k in dg, f"required_dataset_gate missing: {k}"


def test_report_schema_required_fields_all_present():
    data = json.loads(PLAN_JSON_PATH.read_text(encoding="utf-8"))
    rs = data["report_schema"]
    rf = set(rs["required_fields"])
    for fld in cbp.REQUIRED_REPORT_SCHEMA_FIELDS:
        assert fld in rf, f"report_schema missing field: {fld}"
    assert len(rs["required_fields"]) == 27
    assert rs.get("field_count") == 27


def test_metrics_required_contains_all_declared():
    data = json.loads(PLAN_JSON_PATH.read_text(encoding="utf-8"))
    mr = set(data["metrics_required"])
    for m in cbp.REQUIRED_METRICS:
        assert m in mr, f"metrics_required missing: {m}"
    assert len(data["metrics_required"]) == 17


def test_cost_and_slippage_and_position_sizing_requirements_populated():
    data = json.loads(PLAN_JSON_PATH.read_text(encoding="utf-8"))
    cm = data["cost_model_requirements"]
    for k in cbp.REQUIRED_COST_MODEL_KEYS:
        assert k in cm, f"cost_model_requirements missing: {k}"
    assert cm["no_pass_if_costs_ignored"] is True
    assert cm["fees_as_distinct_pnl_line_required"] is True
    sm = data["slippage_model_requirements"]
    for k in cbp.REQUIRED_SLIPPAGE_KEYS:
        assert k in sm, f"slippage_model_requirements missing: {k}"
    assert sm["no_zero_slippage_baseline"] is True
    ps = data["position_sizing_policy"]
    for k in cbp.REQUIRED_POSITION_SIZING_KEYS:
        assert k in ps, f"position_sizing_policy missing: {k}"
    assert ps["no_leverage"] is True
    assert ps["long_only_spot_first"] is True
    assert ps["no_shorting_in_this_protocol"] is True


def test_pass_watch_fail_rules_and_kill_conditions_populated():
    data = json.loads(PLAN_JSON_PATH.read_text(encoding="utf-8"))
    pwf = data["pass_watch_fail_rules"]
    for k in ("PASS", "WATCH", "FAIL"):
        assert k in pwf
    assert isinstance(data["kill_conditions"], list) and data["kill_conditions"]
    assert isinstance(data["forbidden_actions"], list) and data["forbidden_actions"]


def test_no_real_data_files_or_backtest_outputs_created():
    bundle_dir = _REPO_ROOT / cbp.PLAN_DIR_REL
    files = sorted(p.name for p in bundle_dir.iterdir() if p.is_file())
    expected = {"backtest_plan.json", "backtest_plan.md",
                "report.json", "report.md"}
    forbidden_extensions = (".csv", ".parquet", ".pq", ".pickle",
                            ".feather", ".h5", ".npz", ".pkl")
    for name in files:
        for ext in forbidden_extensions:
            assert not name.lower().endswith(ext), f"unexpected data/output file: {name}"
    assert set(files) == expected, f"unexpected files in bundle dir: {sorted(set(files) - expected)}"


def test_no_profitability_or_fetch_or_backtest_claims():
    md = PLAN_MD_PATH.read_text(encoding="utf-8").lower()
    jsn = json.dumps(json.loads(PLAN_JSON_PATH.read_text(encoding="utf-8")),
                    ensure_ascii=False).lower()
    for phrase in cbp.FORBIDDEN_PHRASES:
        assert phrase.lower() not in md, f"forbidden phrase in MD: {phrase!r}"
        assert phrase.lower() not in jsn, f"forbidden phrase in JSON: {phrase!r}"


def test_distinction_phrases_present_in_md():
    md = PLAN_MD_PATH.read_text(encoding="utf-8")
    for phrase in cbp.DISTINCTION_PHRASES:
        assert phrase in md, f"distinction phrase missing: {phrase!r}"


# --- validator failure modes --------------------------------------------- #

def _stage_tmp(tmp_path: Path):
    tmp_dir = tmp_path / cbp.PLAN_DIR_REL
    tmp_dir.mkdir(parents=True, exist_ok=True)
    (tmp_dir / cbp.PLAN_MD).write_text(
        PLAN_MD_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    data = json.loads(PLAN_JSON_PATH.read_text(encoding="utf-8"))
    return tmp_dir, data


def test_validator_detects_tampered_safety_flag(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["backtest_execution_enabled"] = True
    (tmp_dir / cbp.PLAN_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = cbp.validate(tmp_path)
    assert not ok
    assert any("backtest_execution_enabled" in e for e in errs)


def test_validator_detects_missing_required_asset(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["target_assets"] = [a for a in data["target_assets"]
                             if a.get("symbol_canonical") != "ETH"]
    (tmp_dir / cbp.PLAN_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = cbp.validate(tmp_path)
    assert not ok
    assert any("ETH" in e for e in errs)


def test_validator_detects_missing_strategy_family(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["baseline_strategy_families"] = [
        f for f in data["baseline_strategy_families"]
        if f.get("id") != "donchian_channel_breakout"
    ]
    (tmp_dir / cbp.PLAN_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = cbp.validate(tmp_path)
    assert not ok
    assert any("donchian_channel_breakout" in e for e in errs)


def test_validator_detects_missing_report_schema_field(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["report_schema"]["required_fields"] = [
        f for f in data["report_schema"]["required_fields"]
        if f != "QA_report_id"
    ]
    (tmp_dir / cbp.PLAN_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = cbp.validate(tmp_path)
    assert not ok
    assert any("QA_report_id" in e for e in errs)


def test_validator_detects_non_spot_market(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["allowed_market_type"] = "perp_futures"
    (tmp_dir / cbp.PLAN_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = cbp.validate(tmp_path)
    assert not ok
    assert any("allowed_market_type must be 'spot'" in e for e in errs)


def test_validator_detects_forbidden_phrase_in_md(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    (tmp_dir / cbp.PLAN_JSON).write_text(json.dumps(data), encoding="utf-8")
    md = PLAN_MD_PATH.read_text(encoding="utf-8") + "\nNote: guaranteed alpha.\n"
    (tmp_dir / cbp.PLAN_MD).write_text(md, encoding="utf-8")
    ok, errs = cbp.validate(tmp_path)
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
    assert cbp.main(["validate", "--repo-root", str(_REPO_ROOT)]) == 0
    assert cbp.main(["show", "--repo-root", str(_REPO_ROOT)]) == 0


# --- integration tests --------------------------------------------------- #

def test_crypto_d1_qa_freeze_validator_still_passes():
    ok, errs = cqf.validate(_REPO_ROOT)
    assert ok, errs


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


def test_candidate_registry_classifies_crypto_d1_as_WATCH_after_plan():
    payload = scr.generate(_REPO_ROOT)
    cd1 = next(c for c in payload["candidates"]
              if c["candidate_id"] == "crypto_d1_protocol")
    assert cd1["status"] == "WATCH", cd1
    assert cd1["status"] != "ACTIVE"
    assert cd1["evidence_level"] != "STRONG"
    assert cd1["evidence_level"] in ("NONE", "MIXED"), cd1
    for needed in ("backtest_plan.md", "backtest_plan.json"):
        assert needed in cd1["source_reports"], cd1["source_reports"]
    for prior in ("protocol.md", "protocol.json",
                  "data_contract.md", "data_contract.json",
                  "dataset_manifest.md", "dataset_manifest.json",
                  "qa_freeze_spec.md", "qa_freeze_spec.json"):
        assert prior in cd1["source_reports"]


def test_next_bundle_generator_still_validates_after_plan():
    snb.generate(_REPO_ROOT)
    ok, errs = snb.validate(_REPO_ROOT)
    assert ok, errs
