"""Bundle 17 -- Crypto-D1 Local Data Acquisition Authorization tests (research-only).

Pure stdlib + pytest. Asserts:
  * authorization_plan.json exists and validates
  * all seven execution / fetch / connection / backtest-execution /
    dataset-processing flags are pinned False
  * all required top-level sections exist
  * target assets include BTC, ETH, SOL
  * timeframe is daily only; intraday explicitly out of scope
  * spot-only / perps-forbidden distinction is preserved
  * required_csv_schema.required_columns contains all 9 Bundle-12 fields
  * expected_file_layout documents the placeholder filenames + asserts
    no_real_files_created_in_this_bundle = True
  * approval_gates include operator authorization, manifest, checksums,
    QA / freeze, no-credentials, no-paper/live-trading phrases
  * manifest_requirements pin Bundle 11/12/13/14/15/16 versions
  * QA_freeze_requirements pin Bundle 14 spec + QA_PASS-or-approved-WARN
  * checksum_requirements declare sha256-per-file
  * no real data files were created
  * no data directory was created (data/crypto_d1_research/ MUST NOT exist
    as a side effect of this bundle)
  * no profitability / fetch / backtest-authorize claims
  * validator catches tampered safety flag, missing required asset,
    missing CSV field, forbidden phrase
  * validator tool is stdlib-only; no network/broker/exchange imports
  * Crypto-D1 backtest runner tests still pass (smoke: import works)
  * Crypto-D1 prior validators still pass (Bundles 11-15)
  * arbitrage readiness validator still passes (parallel lane unaffected)
  * candidate registry can build after authorization docs exist, crypto_d1
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

import crypto_d1_data_acquisition_authorization_check as cda  # noqa: E402
import crypto_d1_backtest_plan_check as cbp                    # noqa: E402
import crypto_d1_qa_freeze_spec_check as cqf                   # noqa: E402
import crypto_d1_dataset_manifest_check as cdm                 # noqa: E402
import crypto_d1_data_contract_check as cdc                    # noqa: E402
import crypto_d1_protocol_check as cdpc                        # noqa: E402
import crypto_d1_backtest_runner as cbr                        # noqa: E402
import arbitrage_readiness_gate_check as argc                  # noqa: E402
import strategy_candidate_registry as scr                      # noqa: E402
import strategy_next_bundle as snb                             # noqa: E402

TOOL_FILE = _TOOLS_DIR / "crypto_d1_data_acquisition_authorization_check.py"
PLAN_JSON_PATH = _REPO_ROOT / cda.PLAN_DIR_REL / cda.PLAN_JSON
PLAN_MD_PATH = _REPO_ROOT / cda.PLAN_DIR_REL / cda.PLAN_MD


# --- existence + validation ---------------------------------------------- #

def test_plan_json_exists():
    assert PLAN_JSON_PATH.exists(), f"missing: {PLAN_JSON_PATH}"


def test_plan_md_exists():
    assert PLAN_MD_PATH.exists(), f"missing: {PLAN_MD_PATH}"


def test_validator_passes_on_committed_plan():
    ok, errs = cda.validate(_REPO_ROOT)
    assert ok, errs


def test_seven_flags_all_false():
    data = json.loads(PLAN_JSON_PATH.read_text(encoding="utf-8"))
    for flag in cda.MUST_BE_FALSE_FLAGS:
        assert data.get(flag) is False, f"{flag} must be False"
    assert data.get("research_only") is True


def test_required_top_level_sections_present():
    data = json.loads(PLAN_JSON_PATH.read_text(encoding="utf-8"))
    for k in cda.REQUIRED_TOP_LEVEL_KEYS:
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


def test_required_csv_schema_has_all_bundle12_columns():
    data = json.loads(PLAN_JSON_PATH.read_text(encoding="utf-8"))
    rc = {str(c).strip().lower()
          for c in data["required_csv_schema"]["required_columns"]}
    for col in cda.REQUIRED_CSV_COLUMNS:
        assert col in rc, f"required_csv_schema missing column: {col}"


def test_expected_file_layout_documents_placeholders():
    data = json.loads(PLAN_JSON_PATH.read_text(encoding="utf-8"))
    layout = data["expected_file_layout"]
    layout_blob = json.dumps(layout, ensure_ascii=False)
    for needle in cda.REQUIRED_FILE_LAYOUT_NEEDLES:
        assert needle in layout_blob, f"expected_file_layout missing reference: {needle!r}"
    assert layout["no_real_files_created_in_this_bundle"] is True
    assert layout["no_data_directory_created_in_this_bundle"] is True


def test_approval_gates_require_operator_auth_and_manifest_and_checksums_and_qa():
    data = json.loads(PLAN_JSON_PATH.read_text(encoding="utf-8"))
    joined = " ".join(data["approval_gates"]).lower()
    for needle in cda.REQUIRED_APPROVAL_GATE_NEEDLES:
        assert needle in joined, f"approval_gates missing phrase: {needle!r}"


def test_manifest_requirements_pin_all_prior_bundles():
    data = json.loads(PLAN_JSON_PATH.read_text(encoding="utf-8"))
    mr = data["manifest_requirements"]
    for k in cda.REQUIRED_MANIFEST_REQ_KEYS:
        assert k in mr, f"manifest_requirements missing: {k}"
    # The references must point at real prior-bundle IDs.
    assert "crypto_d1_protocol_v1" in mr["must_reference_protocol_version"]
    assert "crypto_d1_data_contract_v1" in mr["must_reference_data_contract_version"]
    assert "crypto_d1_qa_freeze_spec_v1" in mr["must_reference_qa_freeze_spec_version"]
    assert "crypto_d1_baseline_backtest_plan_v1" in mr["must_reference_backtest_plan_version"]
    assert "crypto_d1_backtest_runner_v1" in mr["must_reference_runner_version"]


def test_qa_freeze_requirements_pin_bundle14_spec_and_qa_pass():
    data = json.loads(PLAN_JSON_PATH.read_text(encoding="utf-8"))
    qa = data["QA_freeze_requirements"]
    for k in cda.REQUIRED_QA_FREEZE_KEYS:
        assert k in qa, f"QA_freeze_requirements missing: {k}"
    assert "crypto_d1_qa_freeze_spec_v1" in qa["must_follow"]
    assert "QA_PASS" in qa["qa_status_must_be"]
    assert qa["qa_fail_blocks_runner_use"] is True
    assert qa["qa_blocked_blocks_runner_use"] is True
    assert qa["no_lookahead_check_must_be_in_checks_passed"] is True


def test_checksum_requirements_declare_sha256_per_file():
    data = json.loads(PLAN_JSON_PATH.read_text(encoding="utf-8"))
    cs = data["checksum_requirements"]
    for k in cda.REQUIRED_CHECKSUM_KEYS:
        assert k in cs, f"checksum_requirements missing: {k}"
    assert cs["sha256_per_file_required"] is True
    assert cs["file_hash_verification_before_runner_use"] is True


def test_no_real_data_files_created():
    bundle_dir = _REPO_ROOT / cda.PLAN_DIR_REL
    files = sorted(p.name for p in bundle_dir.iterdir() if p.is_file())
    expected = {"authorization_plan.json", "authorization_plan.md",
                "report.json", "report.md"}
    forbidden_extensions = (".csv", ".parquet", ".pq", ".pickle",
                            ".feather", ".h5", ".npz", ".pkl")
    for name in files:
        for ext in forbidden_extensions:
            assert not name.lower().endswith(ext), f"unexpected data file: {name}"
    assert set(files) == expected, f"unexpected files in bundle dir: {sorted(set(files) - expected)}"


def test_no_data_directory_created():
    """Crypto-D1 storage root must NOT exist as a side effect of this bundle.
    Per the plan, the parent dir 'data/crypto_d1_research/' is created ONLY
    when the operator manually places a real dataset."""
    p = _REPO_ROOT / "data" / "crypto_d1_research"
    if not p.exists():
        return
    # If the directory exists for any reason (e.g., operator pre-staged), it
    # MUST be empty of any committed payload created by this bundle. This
    # bundle does not author any file under that path.
    for f in p.rglob("*"):
        if f.is_file():
            pytest.fail(
                f"Bundle 17 must NOT create data/crypto_d1_research/ contents; "
                f"found {f.as_posix()}. If this file pre-existed, it was NOT "
                f"authored by this bundle, but the test still flags for review."
            )


def test_no_profitability_or_fetch_or_backtest_claims():
    md = PLAN_MD_PATH.read_text(encoding="utf-8").lower()
    jsn = json.dumps(json.loads(PLAN_JSON_PATH.read_text(encoding="utf-8")),
                    ensure_ascii=False).lower()
    for phrase in cda.FORBIDDEN_PHRASES:
        assert phrase.lower() not in md, f"forbidden phrase in MD: {phrase!r}"
        assert phrase.lower() not in jsn, f"forbidden phrase in JSON: {phrase!r}"


def test_distinction_phrases_present_in_md():
    md = PLAN_MD_PATH.read_text(encoding="utf-8")
    for phrase in cda.DISTINCTION_PHRASES:
        assert phrase in md, f"distinction phrase missing: {phrase!r}"


# --- validator failure modes --------------------------------------------- #

def _stage_tmp(tmp_path: Path):
    tmp_dir = tmp_path / cda.PLAN_DIR_REL
    tmp_dir.mkdir(parents=True, exist_ok=True)
    (tmp_dir / cda.PLAN_MD).write_text(
        PLAN_MD_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    data = json.loads(PLAN_JSON_PATH.read_text(encoding="utf-8"))
    return tmp_dir, data


def test_validator_detects_tampered_safety_flag(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["data_fetch_enabled"] = True
    (tmp_dir / cda.PLAN_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = cda.validate(tmp_path)
    assert not ok
    assert any("data_fetch_enabled" in e for e in errs)


def test_validator_detects_missing_required_asset(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["target_assets"] = [a for a in data["target_assets"]
                             if a.get("symbol_canonical") != "BTC"]
    (tmp_dir / cda.PLAN_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = cda.validate(tmp_path)
    assert not ok
    assert any("BTC" in e for e in errs)


def test_validator_detects_missing_csv_field(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["required_csv_schema"]["required_columns"] = [
        c for c in data["required_csv_schema"]["required_columns"]
        if c != "quote_currency"
    ]
    (tmp_dir / cda.PLAN_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = cda.validate(tmp_path)
    assert not ok
    assert any("quote_currency" in e for e in errs)


def test_validator_detects_non_spot_market(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["allowed_market_type"] = "perp_futures"
    (tmp_dir / cda.PLAN_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = cda.validate(tmp_path)
    assert not ok
    assert any("allowed_market_type must be 'spot'" in e for e in errs)


def test_validator_detects_forbidden_phrase_in_md(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    (tmp_dir / cda.PLAN_JSON).write_text(json.dumps(data), encoding="utf-8")
    md = PLAN_MD_PATH.read_text(encoding="utf-8") + "\nNote: live-ready.\n"
    (tmp_dir / cda.PLAN_MD).write_text(md, encoding="utf-8")
    ok, errs = cda.validate(tmp_path)
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
    assert cda.main(["validate", "--repo-root", str(_REPO_ROOT)]) == 0
    assert cda.main(["show", "--repo-root", str(_REPO_ROOT)]) == 0


# --- integration tests --------------------------------------------------- #

def test_crypto_d1_backtest_runner_module_imports_ok():
    # Smoke test: runner is importable + its CLI helpers still work.
    plan = cbr.show_plan()
    assert plan["allowed_market_type"] == "spot"
    ok, _ = cbr.validate_config()
    assert ok


def test_crypto_d1_backtest_plan_validator_still_passes():
    ok, errs = cbp.validate(_REPO_ROOT)
    assert ok, errs


def test_crypto_d1_qa_freeze_spec_validator_still_passes():
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


def test_candidate_registry_classifies_crypto_d1_as_WATCH_after_authorization():
    payload = scr.generate(_REPO_ROOT)
    cd1 = next(c for c in payload["candidates"]
              if c["candidate_id"] == "crypto_d1_protocol")
    assert cd1["status"] == "WATCH", cd1
    assert cd1["status"] != "ACTIVE"
    assert cd1["evidence_level"] != "STRONG"
    assert cd1["evidence_level"] in ("NONE", "MIXED"), cd1
    for needed in ("authorization_plan.md", "authorization_plan.json"):
        assert needed in cd1["source_reports"], cd1["source_reports"]
    for prior in ("protocol.md", "protocol.json",
                  "data_contract.md", "data_contract.json",
                  "dataset_manifest.md", "dataset_manifest.json",
                  "qa_freeze_spec.md", "qa_freeze_spec.json",
                  "backtest_plan.md", "backtest_plan.json"):
        assert prior in cd1["source_reports"]


def test_next_bundle_generator_still_validates_after_authorization():
    snb.generate(_REPO_ROOT)
    ok, errs = snb.validate(_REPO_ROOT)
    assert ok, errs
