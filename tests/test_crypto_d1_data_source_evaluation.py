"""Bundle 18 -- Crypto-D1 Data Source Evaluation Memo v1 tests (research-only).

Pure stdlib + pytest. Asserts:
  * data_source_evaluation.json exists and validates
  * all seven execution / fetch / connection / backtest-execution /
    dataset-processing flags are pinned False
  * all required top-level sections exist
  * target assets include BTC, ETH, SOL
  * timeframe is daily only; intraday explicitly out of scope
  * spot-only / perps-forbidden distinction is preserved
  * 6 source classes (A_..F_) all present with explicit status field
  * E status starts with 'REJECTED'
  * F status starts with 'REJECTED'
  * preferred_source_class_for_crypto_d1.preferred_does_not_mean_approved = True
  * decision_matrix has all 6 rows; every row has required fields and
    allowed_now = False
  * approval gates include explicit operator authorization + version pins +
    no-credentials + no-network-call clauses
  * forbidden_data_sources_or_methods covers live exchange API / scraping /
    credentials / SPARTA-runtime network call / synthetic / E / F
  * required_provenance_fields includes source_class + source_name +
    license_or_tos_reference + sha256 + freeze_record
  * no real data files were created
  * no data directory was created (data/crypto_d1_research/ MUST NOT exist
    as a side effect of this bundle)
  * no profitability / fetch / backtest-authorize claims in MD or JSON
  * validator catches tampered safety flag, missing required asset, missing
    source class, decision_matrix tampered allowed_now=True, forbidden phrase
  * validator tool is stdlib-only; no network/broker/exchange imports
  * Crypto-D1 authorization plan validator still passes
  * Crypto-D1 backtest plan validator still passes
  * Crypto-D1 QA/freeze spec validator still passes
  * Crypto-D1 dataset manifest validator still passes
  * Crypto-D1 data contract validator still passes
  * Crypto-D1 protocol validator still passes
  * Crypto-D1 backtest runner module imports + CLI helpers still work
  * arbitrage readiness validator still passes (parallel lane unaffected)
  * candidate registry can build after evaluation docs exist, crypto_d1
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

import crypto_d1_data_source_evaluation_check as cdse        # noqa: E402
import crypto_d1_data_acquisition_authorization_check as cda # noqa: E402
import crypto_d1_backtest_plan_check as cbp                   # noqa: E402
import crypto_d1_qa_freeze_spec_check as cqf                  # noqa: E402
import crypto_d1_dataset_manifest_check as cdm                # noqa: E402
import crypto_d1_data_contract_check as cdc                   # noqa: E402
import crypto_d1_protocol_check as cdpc                       # noqa: E402
import crypto_d1_backtest_runner as cbr                       # noqa: E402
import arbitrage_readiness_gate_check as argc                 # noqa: E402
import strategy_candidate_registry as scr                     # noqa: E402
import strategy_next_bundle as snb                            # noqa: E402

TOOL_FILE = _TOOLS_DIR / "crypto_d1_data_source_evaluation_check.py"
EVAL_JSON_PATH = _REPO_ROOT / cdse.EVAL_DIR_REL / cdse.EVAL_JSON
EVAL_MD_PATH = _REPO_ROOT / cdse.EVAL_DIR_REL / cdse.EVAL_MD


# --- existence + validation ---------------------------------------------- #

def test_evaluation_json_exists():
    assert EVAL_JSON_PATH.exists(), f"missing: {EVAL_JSON_PATH}"


def test_evaluation_md_exists():
    assert EVAL_MD_PATH.exists(), f"missing: {EVAL_MD_PATH}"


def test_validator_passes_on_committed_evaluation():
    ok, errs = cdse.validate(_REPO_ROOT)
    assert ok, errs


def test_seven_flags_all_false():
    data = json.loads(EVAL_JSON_PATH.read_text(encoding="utf-8"))
    for flag in cdse.MUST_BE_FALSE_FLAGS:
        assert data.get(flag) is False, f"{flag} must be False"
    assert data.get("research_only") is True


def test_required_top_level_sections_present():
    data = json.loads(EVAL_JSON_PATH.read_text(encoding="utf-8"))
    for k in cdse.REQUIRED_TOP_LEVEL_KEYS:
        assert k in data, f"missing top-level key: {k}"


def test_target_assets_include_btc_eth_sol():
    data = json.loads(EVAL_JSON_PATH.read_text(encoding="utf-8"))
    canonical = {a.get("symbol_canonical")
                 for a in data["target_assets"] if isinstance(a, dict)}
    for asset in ("BTC", "ETH", "SOL"):
        assert asset in canonical, f"missing required canonical symbol: {asset}"


def test_timeframe_is_daily_only():
    data = json.loads(EVAL_JSON_PATH.read_text(encoding="utf-8"))
    tf = data["timeframe"]
    assert tf["primary"] == "1d"
    assert tf["intraday_explicitly_out_of_scope"] is True


def test_spot_only_perps_forbidden_distinction():
    data = json.loads(EVAL_JSON_PATH.read_text(encoding="utf-8"))
    assert data["allowed_market_type"] == "spot"
    joined = " ".join(data["forbidden_market_types"]).lower()
    for needle in ("perp", "dated_futures", "options", "leveraged"):
        assert needle in joined, f"missing forbidden needle: {needle!r}"


def test_six_source_classes_all_present_with_status():
    data = json.loads(EVAL_JSON_PATH.read_text(encoding="utf-8"))
    ids = [c.get("id") for c in data["source_classes"] if isinstance(c, dict)]
    for cid in cdse.REQUIRED_SOURCE_CLASS_IDS:
        assert cid in ids, f"source_classes missing id: {cid}"
    for c in data["source_classes"]:
        assert "status" in c, f"class {c.get('id')!r} missing 'status'"


def test_e_status_is_rejected_for_evidence():
    data = json.loads(EVAL_JSON_PATH.read_text(encoding="utf-8"))
    e = next(c for c in data["source_classes"]
             if c.get("id") == "E_web_scraped_or_unofficial_tables")
    assert e["status"].startswith("REJECTED"), e["status"]


def test_f_status_is_rejected_for_any_quantitative_claim():
    data = json.loads(EVAL_JSON_PATH.read_text(encoding="utf-8"))
    f = next(c for c in data["source_classes"]
             if c.get("id") == "F_manually_copied_prices_or_screenshots")
    assert f["status"].startswith("REJECTED"), f["status"]


def test_preferred_class_does_not_mean_approved():
    data = json.loads(EVAL_JSON_PATH.read_text(encoding="utf-8"))
    pref = data["preferred_source_class_for_crypto_d1"]
    assert pref["preferred_does_not_mean_approved"] is True
    assert pref["concrete_vendor_selection_requires_bundle_17_gates"] is True
    assert pref["class_id"] in cdse.REQUIRED_SOURCE_CLASS_IDS


def test_decision_matrix_all_six_rows_allowed_now_false():
    data = json.loads(EVAL_JSON_PATH.read_text(encoding="utf-8"))
    rows = data["decision_matrix"]["rows"]
    row_ids = {r["id"] for r in rows}
    for cid in cdse.REQUIRED_SOURCE_CLASS_IDS:
        assert cid in row_ids, f"decision_matrix row missing: {cid}"
    for r in rows:
        for fld in cdse.REQUIRED_DECISION_MATRIX_FIELDS:
            assert fld in r, f"decision_matrix row {r.get('id')!r} missing field {fld!r}"
        assert r["allowed_now"] is False, f"row {r['id']!r} allowed_now must be False"


def test_approval_gates_require_operator_auth_and_version_pins_and_no_credentials():
    data = json.loads(EVAL_JSON_PATH.read_text(encoding="utf-8"))
    joined = " ".join(data["approval_gates_before_any_source_use"]).lower()
    for needle in ("operator authorization", "protocol_version", "data_contract_version",
                   "manifest", "qa_freeze_spec_version", "checksums.txt",
                   "freeze_record.txt", "no credentials", "no network call",
                   "qa_pass"):
        assert needle in joined, f"approval_gates missing needle: {needle!r}"


def test_forbidden_data_sources_or_methods_cover_required_categories():
    data = json.loads(EVAL_JSON_PATH.read_text(encoding="utf-8"))
    joined = " ".join(data["forbidden_data_sources_or_methods"]).lower()
    for needle in ("live exchange apis", "scraping", "api key", "network call",
                   "synthetic", "provenance cannot be cited", "class e",
                   "class f"):
        assert needle in joined, f"forbidden_data_sources_or_methods missing needle: {needle!r}"


def test_required_provenance_fields_include_critical_fields():
    data = json.loads(EVAL_JSON_PATH.read_text(encoding="utf-8"))
    joined = " ".join(data["required_provenance_fields"]).lower()
    for needle in ("source_class", "source_name", "license_or_tos_reference",
                   "row_level_source_id", "file_hash_sha256",
                   "freeze_timestamp_utc", "operator_name"):
        assert needle in joined, f"required_provenance_fields missing needle: {needle!r}"


def test_no_real_data_files_created():
    bundle_dir = _REPO_ROOT / cdse.EVAL_DIR_REL
    files = sorted(p.name for p in bundle_dir.iterdir() if p.is_file())
    expected = {"data_source_evaluation.json", "data_source_evaluation.md",
                "report.json", "report.md"}
    forbidden_extensions = (".csv", ".parquet", ".pq", ".pickle",
                            ".feather", ".h5", ".npz", ".pkl")
    for name in files:
        for ext in forbidden_extensions:
            assert not name.lower().endswith(ext), f"unexpected data file: {name}"
    assert set(files) == expected, f"unexpected files in bundle dir: {sorted(set(files) - expected)}"


def test_no_data_directory_created():
    """Crypto-D1 storage root must NOT exist as a side effect of this bundle."""
    p = _REPO_ROOT / "data" / "crypto_d1_research"
    if not p.exists():
        return
    for f in p.rglob("*"):
        if f.is_file():
            pytest.fail(
                f"Bundle 18 must NOT create data/crypto_d1_research/ contents; "
                f"found {f.as_posix()}."
            )


def test_no_profitability_or_fetch_or_backtest_claims():
    md = EVAL_MD_PATH.read_text(encoding="utf-8").lower()
    jsn = json.dumps(json.loads(EVAL_JSON_PATH.read_text(encoding="utf-8")),
                    ensure_ascii=False).lower()
    for phrase in cdse.FORBIDDEN_PHRASES:
        assert phrase.lower() not in md, f"forbidden phrase in MD: {phrase!r}"
        assert phrase.lower() not in jsn, f"forbidden phrase in JSON: {phrase!r}"


def test_distinction_phrases_present_in_md():
    md = EVAL_MD_PATH.read_text(encoding="utf-8")
    for phrase in cdse.DISTINCTION_PHRASES:
        assert phrase in md, f"distinction phrase missing: {phrase!r}"


# --- validator failure modes --------------------------------------------- #

def _stage_tmp(tmp_path: Path):
    tmp_dir = tmp_path / cdse.EVAL_DIR_REL
    tmp_dir.mkdir(parents=True, exist_ok=True)
    (tmp_dir / cdse.EVAL_MD).write_text(
        EVAL_MD_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    data = json.loads(EVAL_JSON_PATH.read_text(encoding="utf-8"))
    return tmp_dir, data


def test_validator_detects_tampered_safety_flag(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["data_fetch_enabled"] = True
    (tmp_dir / cdse.EVAL_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = cdse.validate(tmp_path)
    assert not ok
    assert any("data_fetch_enabled" in e for e in errs)


def test_validator_detects_missing_required_asset(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["target_assets"] = [a for a in data["target_assets"]
                             if a.get("symbol_canonical") != "SOL"]
    (tmp_dir / cdse.EVAL_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = cdse.validate(tmp_path)
    assert not ok
    assert any("SOL" in e for e in errs)


def test_validator_detects_missing_source_class(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["source_classes"] = [c for c in data["source_classes"]
                              if c.get("id") != "C_paid_market_data_vendors"]
    data["decision_matrix"]["rows"] = [r for r in data["decision_matrix"]["rows"]
                                       if r.get("id") != "C_paid_market_data_vendors"]
    (tmp_dir / cdse.EVAL_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = cdse.validate(tmp_path)
    assert not ok
    assert any("C_paid_market_data_vendors" in e for e in errs)


def test_validator_detects_decision_matrix_allowed_now_true(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["decision_matrix"]["rows"][0]["allowed_now"] = True
    (tmp_dir / cdse.EVAL_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = cdse.validate(tmp_path)
    assert not ok
    assert any("allowed_now must be False" in e for e in errs)


def test_validator_detects_e_not_rejected(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    for c in data["source_classes"]:
        if c.get("id") == "E_web_scraped_or_unofficial_tables":
            c["status"] = "ACCEPTABLE"
    (tmp_dir / cdse.EVAL_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = cdse.validate(tmp_path)
    assert not ok
    assert any("E status must start with REJECTED" in e for e in errs)


def test_validator_detects_forbidden_phrase_in_md(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    (tmp_dir / cdse.EVAL_JSON).write_text(json.dumps(data), encoding="utf-8")
    md = EVAL_MD_PATH.read_text(encoding="utf-8") + "\nNote: guaranteed profit.\n"
    (tmp_dir / cdse.EVAL_MD).write_text(md, encoding="utf-8")
    ok, errs = cdse.validate(tmp_path)
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
    assert cdse.main(["validate", "--repo-root", str(_REPO_ROOT)]) == 0
    assert cdse.main(["show", "--repo-root", str(_REPO_ROOT)]) == 0


# --- integration tests --------------------------------------------------- #

def test_crypto_d1_authorization_validator_still_passes():
    ok, errs = cda.validate(_REPO_ROOT)
    assert ok, errs


def test_crypto_d1_backtest_plan_validator_still_passes():
    ok, errs = cbp.validate(_REPO_ROOT)
    assert ok, errs


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


def test_crypto_d1_backtest_runner_smoke():
    plan = cbr.show_plan()
    assert plan["allowed_market_type"] == "spot"
    ok, _ = cbr.validate_config()
    assert ok


def test_arbitrage_readiness_validator_still_passes():
    ok, errs = argc.validate(_REPO_ROOT)
    assert ok, errs


def test_candidate_registry_classifies_crypto_d1_as_WATCH_after_evaluation():
    payload = scr.generate(_REPO_ROOT)
    cd1 = next(c for c in payload["candidates"]
              if c["candidate_id"] == "crypto_d1_protocol")
    assert cd1["status"] == "WATCH", cd1
    assert cd1["status"] != "ACTIVE"
    assert cd1["evidence_level"] != "STRONG"
    assert cd1["evidence_level"] in ("NONE", "MIXED"), cd1
    for needed in ("data_source_evaluation.md", "data_source_evaluation.json"):
        assert needed in cd1["source_reports"], cd1["source_reports"]
    for prior in ("protocol.md", "protocol.json",
                  "data_contract.md", "data_contract.json",
                  "dataset_manifest.md", "dataset_manifest.json",
                  "qa_freeze_spec.md", "qa_freeze_spec.json",
                  "backtest_plan.md", "backtest_plan.json",
                  "authorization_plan.md", "authorization_plan.json"):
        assert prior in cd1["source_reports"]


def test_next_bundle_generator_still_validates_after_evaluation():
    snb.generate(_REPO_ROOT)
    ok, errs = snb.validate(_REPO_ROOT)
    assert ok, errs
