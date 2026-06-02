"""Bundle 20 -- Crypto-D1 Manual Dataset Intake Runbook v1 tests (research-only).

Pure stdlib + pytest. Asserts:
  * runbook.json + runbook.md exist and validate
  * research_only True; all eleven execution / fetch / connection / order /
    backtest-execution / dataset-processing / scheduler / network / credential
    flags pinned False
  * authorization_disclaimer pins the six "authorizes nothing" booleans True
  * target assets BTC/ETH/SOL; spot only; 1d only; 24/7 calendar
  * 9 required CSV columns documented
  * operator decisions non-empty
  * all 6 Bundle-18 source classes have a disposition; E + F are rejected
  * required concrete inputs cover the mandated field set
  * QA CLI commands include validate-spec / show-spec / run (with
    --dataset-dir + --out-dir)
  * all 6 QA statuses documented
  * forbidden list covers perps / leverage / intraday / scraping /
    screenshots / broker / credentials / network automation
  * registry status stays WATCH (never STRONG, never ACTIVE)
  * no real data files created; no data/crypto_d1_research/ created
  * no profitability / fetch / backtest-authorize claims in MD or JSON
  * distinction phrases present in MD
  * validator catches tampered safety flag, tampered disclaimer flag, missing
    required asset, missing source class, un-rejected E, missing QA status,
    registry STRONG tamper, forbidden phrase
  * validator tool is stdlib-only; no network/broker/exchange imports
  * Bundle 19 QA runtime tool docs validator still passes (companion intact)
  * Crypto-D1 data source evaluation validator still passes
  * Crypto-D1 authorization plan validator still passes
  * Crypto-D1 QA/freeze spec validator still passes
  * Crypto-D1 dataset manifest validator still passes
  * Crypto-D1 data contract validator still passes
  * Crypto-D1 protocol validator still passes
  * arbitrage readiness validator still passes (parallel lane unaffected)
  * candidate registry builds; crypto_d1 remains WATCH (never ACTIVE/STRONG)
    and now lists the runbook docs
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

import crypto_d1_manual_dataset_intake_runbook_check as cmir  # noqa: E402
import crypto_d1_data_source_evaluation_check as cdse          # noqa: E402
import crypto_d1_data_acquisition_authorization_check as cda   # noqa: E402
import crypto_d1_qa_freeze_spec_check as cqf                   # noqa: E402
import crypto_d1_dataset_manifest_check as cdm                 # noqa: E402
import crypto_d1_data_contract_check as cdc                    # noqa: E402
import crypto_d1_protocol_check as cdpc                        # noqa: E402
import arbitrage_readiness_gate_check as argc                  # noqa: E402
import strategy_candidate_registry as scr                      # noqa: E402
import strategy_next_bundle as snb                             # noqa: E402

TOOL_FILE = _TOOLS_DIR / "crypto_d1_manual_dataset_intake_runbook_check.py"
RUNBOOK_JSON_PATH = _REPO_ROOT / cmir.RUNBOOK_DIR_REL / cmir.RUNBOOK_JSON
RUNBOOK_MD_PATH = _REPO_ROOT / cmir.RUNBOOK_DIR_REL / cmir.RUNBOOK_MD


def _data():
    return json.loads(RUNBOOK_JSON_PATH.read_text(encoding="utf-8"))


# --- existence + validation ---------------------------------------------- #

def test_runbook_json_exists():
    assert RUNBOOK_JSON_PATH.exists(), f"missing: {RUNBOOK_JSON_PATH}"


def test_runbook_md_exists():
    assert RUNBOOK_MD_PATH.exists(), f"missing: {RUNBOOK_MD_PATH}"


def test_validator_passes_on_committed_runbook():
    ok, errs = cmir.validate(_REPO_ROOT)
    assert ok, errs


def test_all_safety_flags_false():
    data = _data()
    for flag in cmir.MUST_BE_FALSE_FLAGS:
        assert data.get(flag) is False, f"{flag} must be False"
    assert data.get("research_only") is True
    assert data.get("read_only") is True


def test_required_top_level_sections_present():
    data = _data()
    for k in cmir.REQUIRED_TOP_LEVEL_KEYS:
        assert k in data, f"missing top-level key: {k}"


def test_authorization_disclaimer_pins_authorizes_nothing():
    disc = _data()["authorization_disclaimer"]
    for flag in cmir.REQUIRED_DISCLAIMER_FLAGS:
        assert disc.get(flag) is True, f"disclaimer flag must be True: {flag}"
    assert str(disc.get("statement", "")).strip()


def test_scope_assets_market_timeframe_calendar():
    data = _data()
    for asset in ("BTC", "ETH", "SOL"):
        assert asset in data["target_assets"], f"missing asset: {asset}"
    assert data["allowed_market_type"] == "spot"
    assert data["timeframe"] == "1d"
    assert str(data["session_calendar"]) == "24/7"


def test_nine_required_csv_columns_documented():
    cols = _data()["required_csv_columns"]
    for c in cmir.REQUIRED_CSV_COLUMNS:
        assert c in cols, f"missing required CSV column: {c}"


def test_operator_decisions_non_empty():
    assert len(_data()["operator_decisions_before_data_enters"]) >= 1


def test_all_six_source_classes_disposed_e_and_f_rejected():
    scd = _data()["source_class_dispositions"]
    present, rejected = set(), set()
    for bucket in ("preferred", "acceptable", "watch", "rejected"):
        for e in scd.get(bucket, []):
            present.add(e["id"])
            if bucket == "rejected":
                rejected.add(e["id"])
    for cid in cmir.REQUIRED_SOURCE_CLASS_IDS:
        assert cid in present, f"source class not disposed: {cid}"
    assert "E_web_scraped_or_unofficial_tables" in rejected
    assert "F_manually_copied_prices_or_screenshots" in rejected


def test_required_concrete_inputs_cover_mandated_fields():
    rci = _data()["required_concrete_inputs"]
    fields = {e.get("field") for e in rci}
    for fld in cmir.REQUIRED_CONCRETE_INPUT_FIELDS:
        assert fld in fields, f"missing required concrete input: {fld}"


def test_qa_cli_commands_present():
    cli = _data()["qa_cli_commands"]
    for k in cmir.REQUIRED_QA_CLI_KEYS:
        assert str(cli.get(k, "")).strip(), f"missing CLI command: {k}"
    assert "validate-spec" in cli["validate_spec"]
    assert "show-spec" in cli["show_spec"]
    assert "--dataset-dir" in cli["run"] and "--out-dir" in cli["run"]


def test_all_six_qa_statuses_documented():
    qsm = _data()["qa_status_meanings"]
    for st in cmir.REQUIRED_QA_STATUSES:
        assert st in qsm, f"missing QA status: {st}"


def test_qa_pass_authorizes_nothing_block():
    joined = " ".join(_data()["why_qa_pass_authorizes_nothing"]).lower()
    for needle in ("backtest", "paper", "live"):
        assert needle in joined, f"why_qa_pass_authorizes_nothing missing: {needle}"


def test_forbidden_list_covers_required_categories():
    joined = " ".join(_data()["forbidden_list"]).lower()
    for needle in cmir.FORBIDDEN_LIST_NEEDLES:
        assert needle in joined, f"forbidden_list missing category: {needle}"


def test_registry_status_after_doc_stays_watch():
    crs = _data()["candidate_registry_status_after_doc"]
    assert crs["status"] == "WATCH"
    assert crs.get("evidence_level") != "STRONG"


def test_distinction_phrases_present_in_md():
    md = RUNBOOK_MD_PATH.read_text(encoding="utf-8")
    for phrase in cmir.DISTINCTION_PHRASES:
        assert phrase in md, f"distinction phrase missing: {phrase!r}"


def test_no_profitability_or_fetch_or_backtest_claims():
    md = RUNBOOK_MD_PATH.read_text(encoding="utf-8").lower()
    jsn = json.dumps(_data(), ensure_ascii=False).lower()
    for phrase in cmir.FORBIDDEN_PHRASES:
        assert phrase.lower() not in md, f"forbidden phrase in MD: {phrase!r}"
        assert phrase.lower() not in jsn, f"forbidden phrase in JSON: {phrase!r}"


# --- no real data side effects ------------------------------------------- #

def test_no_real_data_files_created():
    bundle_dir = _REPO_ROOT / cmir.RUNBOOK_DIR_REL
    files = sorted(p.name for p in bundle_dir.iterdir() if p.is_file())
    expected = {"runbook.json", "runbook.md", "report.json", "report.md"}
    forbidden_extensions = (".csv", ".parquet", ".pq", ".pickle",
                            ".feather", ".h5", ".npz", ".pkl")
    for name in files:
        for ext in forbidden_extensions:
            assert not name.lower().endswith(ext), f"unexpected data file: {name}"
    assert set(files) == expected, f"unexpected files: {sorted(set(files) - expected)}"


def test_no_data_directory_created():
    p = _REPO_ROOT / "data" / "crypto_d1_research"
    if not p.exists():
        return
    for f in p.rglob("*"):
        if f.is_file():
            pytest.fail(
                f"Bundle 20 must NOT create data/crypto_d1_research/ contents; "
                f"found {f.as_posix()}."
            )


# --- validator failure modes --------------------------------------------- #

def _stage_tmp(tmp_path: Path):
    tmp_dir = tmp_path / cmir.RUNBOOK_DIR_REL
    tmp_dir.mkdir(parents=True, exist_ok=True)
    (tmp_dir / cmir.RUNBOOK_MD).write_text(
        RUNBOOK_MD_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    return tmp_dir, _data()


def test_validator_detects_tampered_safety_flag(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["data_fetch_enabled"] = True
    (tmp_dir / cmir.RUNBOOK_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = cmir.validate(tmp_path)
    assert not ok
    assert any("data_fetch_enabled" in e for e in errs)


def test_validator_detects_tampered_disclaimer_flag(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["authorization_disclaimer"]["qa_pass_does_not_authorize_live_trading"] = False
    (tmp_dir / cmir.RUNBOOK_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = cmir.validate(tmp_path)
    assert not ok
    assert any("qa_pass_does_not_authorize_live_trading" in e for e in errs)


def test_validator_detects_missing_required_asset(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["target_assets"] = [a for a in data["target_assets"] if a != "SOL"]
    (tmp_dir / cmir.RUNBOOK_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = cmir.validate(tmp_path)
    assert not ok
    assert any("SOL" in e for e in errs)


def test_validator_detects_missing_source_class(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["source_class_dispositions"]["preferred"] = []
    (tmp_dir / cmir.RUNBOOK_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = cmir.validate(tmp_path)
    assert not ok
    assert any("C_paid_market_data_vendors" in e for e in errs)


def test_validator_detects_e_not_rejected(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    scd = data["source_class_dispositions"]
    scd["rejected"] = [e for e in scd["rejected"]
                       if e["id"] != "E_web_scraped_or_unofficial_tables"]
    scd["watch"].append({"id": "E_web_scraped_or_unofficial_tables",
                         "disposition": "WATCH", "note": "tampered"})
    (tmp_dir / cmir.RUNBOOK_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = cmir.validate(tmp_path)
    assert not ok
    assert any("E_web_scraped_or_unofficial_tables" in e for e in errs)


def test_validator_detects_missing_qa_status(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["qa_status_meanings"].pop("QA_BLOCKED", None)
    (tmp_dir / cmir.RUNBOOK_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = cmir.validate(tmp_path)
    assert not ok
    assert any("QA_BLOCKED" in e for e in errs)


def test_validator_detects_registry_strong_tamper(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["candidate_registry_status_after_doc"]["evidence_level"] = "STRONG"
    (tmp_dir / cmir.RUNBOOK_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = cmir.validate(tmp_path)
    assert not ok
    assert any("STRONG" in e for e in errs)


def test_validator_detects_forbidden_phrase_in_md(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    (tmp_dir / cmir.RUNBOOK_JSON).write_text(json.dumps(data), encoding="utf-8")
    md = RUNBOOK_MD_PATH.read_text(encoding="utf-8") + "\nNote: guaranteed profit.\n"
    (tmp_dir / cmir.RUNBOOK_MD).write_text(md, encoding="utf-8")
    ok, errs = cmir.validate(tmp_path)
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
        "import ccxt", "from ccxt",
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
    assert cmir.main(["validate", "--repo-root", str(_REPO_ROOT)]) == 0
    assert cmir.main(["show", "--repo-root", str(_REPO_ROOT)]) == 0


# --- integration tests --------------------------------------------------- #

def test_crypto_d1_qa_runtime_tool_docs_still_validate():
    # The Bundle 19 QA runtime tool docs are companion artifacts; confirm the
    # doc JSON still parses and pins research_only true.
    p = _REPO_ROOT / "reports" / "crypto_d1_data_qa_runtime_tool_v1" / "qa_runtime_tool.json"
    assert p.exists(), f"missing companion: {p}"
    doc = json.loads(p.read_text(encoding="utf-8"))
    assert doc.get("research_only") is True


def test_crypto_d1_data_source_evaluation_validator_still_passes():
    ok, errs = cdse.validate(_REPO_ROOT)
    assert ok, errs


def test_crypto_d1_authorization_validator_still_passes():
    ok, errs = cda.validate(_REPO_ROOT)
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


def test_arbitrage_readiness_validator_still_passes():
    ok, errs = argc.validate(_REPO_ROOT)
    assert ok, errs


def test_candidate_registry_classifies_crypto_d1_as_WATCH_after_runbook():
    payload = scr.generate(_REPO_ROOT)
    cd1 = next(c for c in payload["candidates"]
               if c["candidate_id"] == "crypto_d1_protocol")
    assert cd1["status"] == "WATCH", cd1
    assert cd1["status"] != "ACTIVE"
    assert cd1["evidence_level"] != "STRONG"
    for needed in ("runbook.md", "runbook.json"):
        assert needed in cd1["source_reports"], cd1["source_reports"]


def test_next_bundle_generator_still_validates_after_runbook():
    snb.generate(_REPO_ROOT)
    ok, errs = snb.validate(_REPO_ROOT)
    assert ok, errs
