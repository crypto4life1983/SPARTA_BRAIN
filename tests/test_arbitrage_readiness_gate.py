"""Bundle 10 — Arbitrage Research Readiness Gate v1 tests (research-only).

Pure stdlib + pytest. Asserts:
  * readiness_gate.json exists and validates
  * the seven execution / fetch / connection / backtest / dataset-processing
    flags are pinned False
  * all required top-level sections exist
  * all 6 arbitrage artifacts are referenced AND exist on disk AND validate
  * readiness_status is one of PASS / WATCH / BLOCKED / PARKED
  * readiness gate does NOT authorize backtest or paper/live trading
  * future data collection gate requires explicit operator authorization
  * no profitability claim, no fetch claim, no backtest-authorize claim
  * validator catches tampered flag / missing artifact path / bad status /
    forbidden phrase
  * validator tool is stdlib-only; no network/broker/exchange imports
  * all 8 prior arbitrage validators still pass
  * candidate registry now classifies arbitrage as WATCH (foundation
    complete; no data) AND it does NOT become ACTIVE AND evidence does NOT
    become STRONG
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

import arbitrage_readiness_gate_check as argc            # noqa: E402
import arbitrage_sample_dataset_plan_check as asdpc      # noqa: E402
import arbitrage_data_source_evaluation_check as adsec   # noqa: E402
import arbitrage_qa_harness_spec_check as aqhc           # noqa: E402
import arbitrage_dataset_manifest_check as admc          # noqa: E402
import arbitrage_data_contract_check as adc              # noqa: E402
import arbitrage_protocol_check as apc                   # noqa: E402
import strategy_candidate_registry as scr                # noqa: E402
import strategy_next_bundle as snb                       # noqa: E402

TOOL_FILE = _TOOLS_DIR / "arbitrage_readiness_gate_check.py"
GATE_JSON_PATH = _REPO_ROOT / argc.GATE_DIR_REL / argc.GATE_JSON
GATE_MD_PATH = _REPO_ROOT / argc.GATE_DIR_REL / argc.GATE_MD


# --- existence + validation ---------------------------------------------- #

def test_gate_json_exists():
    assert GATE_JSON_PATH.exists(), f"missing: {GATE_JSON_PATH}"


def test_gate_md_exists():
    assert GATE_MD_PATH.exists(), f"missing: {GATE_MD_PATH}"


def test_validator_passes_on_committed_gate():
    ok, errs = argc.validate(_REPO_ROOT)
    assert ok, errs


def test_seven_flags_all_false():
    data = json.loads(GATE_JSON_PATH.read_text(encoding="utf-8"))
    for flag in argc.MUST_BE_FALSE_FLAGS:
        assert data.get(flag) is False, f"{flag} must be False"
    assert data.get("research_only") is True


def test_required_top_level_sections_present():
    data = json.loads(GATE_JSON_PATH.read_text(encoding="utf-8"))
    for k in argc.REQUIRED_TOP_LEVEL_KEYS:
        assert k in data, f"missing top-level key: {k}"


def test_all_six_arbitrage_artifacts_referenced_and_exist():
    data = json.loads(GATE_JSON_PATH.read_text(encoding="utf-8"))
    arts = data["audited_artifacts"]
    ids = [a["artifact_id"] for a in arts if isinstance(a, dict)]
    for aid in argc.REQUIRED_AUDITED_ARTIFACT_IDS:
        assert aid in ids, f"audited_artifacts missing: {aid}"
    for art in arts:
        p = _REPO_ROOT / art["path"]
        assert p.exists(), f"audited artifact path does not exist on disk: {art['path']}"
        assert art["exists"] is True
        assert art["validation_status"] == "OK"


def test_readiness_status_is_allowed_value():
    data = json.loads(GATE_JSON_PATH.read_text(encoding="utf-8"))
    assert data["readiness_status"] in argc.ALLOWED_READINESS_STATUSES


def test_readiness_gate_does_not_authorize_backtest_or_trading():
    data = json.loads(GATE_JSON_PATH.read_text(encoding="utf-8"))
    far = data["future_authorization_requirements"]
    # Trading gate explicitly forbidden by this readiness gate.
    assert far["trading_gate"]["explicitly_forbidden_by_this_readiness_gate"] is True
    # Backtest gate present and gated on a separate bundle.
    bt = far["backtest_gate"]
    joined = " ".join(bt["all_required"]).lower()
    assert "separate_backtest_bundle_approved" in joined
    # The gate's status string for backtest/trading is explicit.
    assert "EXPLICITLY FORBIDDEN" in data["trading_gate"]
    assert "NOT authorized" in data["backtest_gate"]


def test_future_data_collection_gate_requires_operator_authorization():
    data = json.loads(GATE_JSON_PATH.read_text(encoding="utf-8"))
    dcg = data["future_authorization_requirements"]["data_collection_gate"]
    joined = " ".join(dcg["all_required"]).lower()
    for marker in ("explicit_operator_authorization",
                  "exact_source_class_from_bundle_8",
                  "exact_storage_path_named",
                  "no_credentials_unless_separately_authorized",
                  "no_trading_permissions",
                  "separate_data_collection_bundle_approved"):
        assert marker in joined, f"data_collection_gate missing: {marker}"


def test_no_profitability_or_fetch_or_backtest_claims():
    md = GATE_MD_PATH.read_text(encoding="utf-8").lower()
    jsn = json.dumps(json.loads(GATE_JSON_PATH.read_text(encoding="utf-8")),
                    ensure_ascii=False).lower()
    for phrase in argc.FORBIDDEN_PHRASES:
        assert phrase.lower() not in md, f"forbidden phrase in MD: {phrase!r}"
        assert phrase.lower() not in jsn, f"forbidden phrase in JSON: {phrase!r}"


def test_distinction_phrases_present_in_md():
    md = GATE_MD_PATH.read_text(encoding="utf-8")
    for phrase in argc.DISTINCTION_PHRASES:
        assert phrase in md, f"distinction phrase missing: {phrase!r}"


# --- validator failure modes --------------------------------------------- #

def _stage_tmp_full_copy(tmp_path: Path):
    """Stage a full minimal repo copy: gate JSON + MD + all 6 referenced
    artifact paths (touched empty files so existence checks pass)."""
    tmp_dir = tmp_path / argc.GATE_DIR_REL
    tmp_dir.mkdir(parents=True, exist_ok=True)
    (tmp_dir / argc.GATE_MD).write_text(GATE_MD_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    data = json.loads(GATE_JSON_PATH.read_text(encoding="utf-8"))
    # Create empty placeholder files at every audited artifact path so the
    # path-existence check passes by default; the tests mutate after.
    for art in data["audited_artifacts"]:
        p = tmp_path / art["path"]
        p.parent.mkdir(parents=True, exist_ok=True)
        if not p.exists():
            p.write_text("{}", encoding="utf-8")
    return tmp_dir, data


def test_validator_detects_tampered_safety_flag(tmp_path):
    tmp_dir, data = _stage_tmp_full_copy(tmp_path)
    data["live_trading_enabled"] = True
    (tmp_dir / argc.GATE_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = argc.validate(tmp_path)
    assert not ok
    assert any("live_trading_enabled" in e for e in errs)


def test_validator_detects_missing_artifact_path(tmp_path):
    tmp_dir, data = _stage_tmp_full_copy(tmp_path)
    # Remove one of the placeholder artifact files on disk.
    missing = tmp_path / data["audited_artifacts"][0]["path"]
    if missing.exists():
        missing.unlink()
    (tmp_dir / argc.GATE_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = argc.validate(tmp_path)
    assert not ok
    assert any("path does not exist on disk" in e for e in errs)


def test_validator_detects_invalid_readiness_status(tmp_path):
    tmp_dir, data = _stage_tmp_full_copy(tmp_path)
    data["readiness_status"] = "STRONG"  # not allowed
    (tmp_dir / argc.GATE_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = argc.validate(tmp_path)
    assert not ok
    assert any("readiness_status must be one of" in e for e in errs)


def test_validator_detects_missing_audited_artifact_id(tmp_path):
    tmp_dir, data = _stage_tmp_full_copy(tmp_path)
    data["audited_artifacts"] = [a for a in data["audited_artifacts"]
                                 if a["artifact_id"] != "arbitrage_qa_harness_spec_v1"]
    (tmp_dir / argc.GATE_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = argc.validate(tmp_path)
    assert not ok
    assert any("arbitrage_qa_harness_spec_v1" in e for e in errs)


def test_validator_detects_trading_gate_not_forbidden(tmp_path):
    tmp_dir, data = _stage_tmp_full_copy(tmp_path)
    data["future_authorization_requirements"]["trading_gate"]["explicitly_forbidden_by_this_readiness_gate"] = False
    (tmp_dir / argc.GATE_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = argc.validate(tmp_path)
    assert not ok
    assert any("explicitly_forbidden_by_this_readiness_gate" in e for e in errs)


def test_validator_detects_forbidden_phrase_in_md(tmp_path):
    tmp_dir, data = _stage_tmp_full_copy(tmp_path)
    (tmp_dir / argc.GATE_JSON).write_text(json.dumps(data), encoding="utf-8")
    md = GATE_MD_PATH.read_text(encoding="utf-8") + "\nNote: production-ready.\n"
    (tmp_dir / argc.GATE_MD).write_text(md, encoding="utf-8")
    ok, errs = argc.validate(tmp_path)
    assert not ok
    assert any("production-ready" in e for e in errs)


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
    assert argc.main(["validate", "--repo-root", str(_REPO_ROOT)]) == 0
    assert argc.main(["show", "--repo-root", str(_REPO_ROOT)]) == 0


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


def test_bundle_9_sample_dataset_plan_validator_still_passes():
    ok, errs = asdpc.validate(_REPO_ROOT)
    assert ok, errs


def test_candidate_registry_classifies_arbitrage_as_WATCH_after_gate():
    payload = scr.generate(_REPO_ROOT)
    arb = next(c for c in payload["candidates"]
              if c["candidate_id"] == "arbitrage_research_protocol")
    # With the readiness gate on disk, the classifier promotes IDEA -> WATCH
    # via the "readiness_gate" STATUS_KEYWORDS rule.
    assert arb["status"] == "WATCH", arb
    # But STRONG is still never reached; ACTIVE is never reached.
    assert arb["status"] != "ACTIVE"
    assert arb["evidence_level"] != "STRONG"
    assert arb["evidence_level"] in ("NONE", "MIXED"), arb
    # All 7 doc generations now appear in source_reports (14 files: 2 per
    # bundle, Bundles 4-10).
    for needed in ("readiness_gate.md", "readiness_gate.json",
                  "sample_dataset_plan.md", "data_source_evaluation.md",
                  "qa_harness_spec.md", "dataset_manifest.md",
                  "data_contract.md", "protocol.md"):
        assert needed in arb["source_reports"], arb["source_reports"]


def test_next_bundle_generator_still_validates_after_gate():
    snb.generate(_REPO_ROOT)
    ok, errs = snb.validate(_REPO_ROOT)
    assert ok, errs
