"""Portfolio Capital-Efficiency Advisory Memo Schema v1 (P5) tests (research-only).

Pure stdlib + pytest. Asserts:
  * advisory_memo_schema.json + .md exist and validate
  * research_only + advisory_only + framework_only True; compute_enabled +
    capital_deployment_enabled + eight execution flags pinned False;
    memo_produced_in_this_bundle False
  * lane == 'portfolio_capital_efficiency'; phase == 'P5_advisory_memo_schema';
    self-declared status == WATCH
  * companion_documents reference P0 + P1 + P2 + P3 + P4
  * the 10 required memo sections are present, each spec-only with purpose +
    non-empty required_fields
  * allowed_classifications are EXACTLY the five allowed WATCH/undefined labels
  * forbidden_verdict_language enumerates PASS/ACTIVE/STRONG + the approval /
    profit-guarantee / capital-deployment / broker tokens
  * Candidate #10 deferred (c10_boundary deferred_not_connected + must_not_touch)
  * verdict ceiling max == WATCH
  * pass/watch/fail rules exist
  * no capability-claim phrase in md/json
  * validator catches an extra non-allowed classification / dropped forbidden
    token / memo_produced flip / tampered flag / connected-C10 / capability claim
  * validator tool is stdlib-only; no network/broker/exchange imports
  * P0 + P1 + P2 + P3 + P4 validators still pass (companion bundles unaffected)
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

import portfolio_capital_efficiency_advisory_memo_schema_check as pams      # noqa: E402
import portfolio_capital_efficiency_overlap_correlation_method_check as pocc  # noqa: E402
import portfolio_capital_efficiency_allocation_baseline_spec_check as pabc    # noqa: E402
import portfolio_capital_efficiency_metric_spec_check as pmsc                 # noqa: E402
import portfolio_capital_efficiency_input_contract_check as picc              # noqa: E402
import portfolio_capital_efficiency_protocol_check as pcec                    # noqa: E402

TOOL_FILE = _TOOLS_DIR / "portfolio_capital_efficiency_advisory_memo_schema_check.py"
SCHEMA_JSON_PATH = _REPO_ROOT / pams.SCHEMA_DIR_REL / pams.SCHEMA_JSON
SCHEMA_MD_PATH = _REPO_ROOT / pams.SCHEMA_DIR_REL / pams.SCHEMA_MD


# --- existence + validation ---------------------------------------------- #

def test_schema_json_exists():
    assert SCHEMA_JSON_PATH.exists(), f"missing: {SCHEMA_JSON_PATH}"


def test_schema_md_exists():
    assert SCHEMA_MD_PATH.exists(), f"missing: {SCHEMA_MD_PATH}"


def test_validator_passes_on_committed_schema():
    ok, errs = pams.validate(_REPO_ROOT)
    assert ok, errs


def test_flags_false_and_framework_only():
    data = json.loads(SCHEMA_JSON_PATH.read_text(encoding="utf-8"))
    for flag in pams.MUST_BE_FALSE_FLAGS:
        assert data.get(flag) is False, f"{flag} must be False"
    assert data.get("research_only") is True
    assert data.get("advisory_only") is True
    assert data.get("framework_only") is True
    assert data.get("memo_produced_in_this_bundle") is False


def test_required_top_level_sections_present():
    data = json.loads(SCHEMA_JSON_PATH.read_text(encoding="utf-8"))
    for k in pams.REQUIRED_TOP_LEVEL_KEYS:
        assert k in data, f"missing top-level key: {k}"


def test_lane_phase_and_watch_status():
    data = json.loads(SCHEMA_JSON_PATH.read_text(encoding="utf-8"))
    assert data["lane"] == "portfolio_capital_efficiency"
    assert data["phase"] == "P5_advisory_memo_schema"
    assert data["lane_status_self_declared"] == "WATCH"


def test_companion_documents_reference_p0_through_p4():
    data = json.loads(SCHEMA_JSON_PATH.read_text(encoding="utf-8"))
    joined = " ".join(str(v) for v in data["companion_documents"].values())
    for needle in (
        "portfolio_capital_efficiency_protocol_v1",
        "portfolio_capital_efficiency_input_contract_v1",
        "portfolio_capital_efficiency_metric_spec_v1",
        "portfolio_capital_efficiency_allocation_baseline_spec_v1",
        "portfolio_capital_efficiency_overlap_correlation_method_v1",
    ):
        assert needle in joined, f"missing companion: {needle}"


def test_ten_memo_sections_present_and_spec_only():
    data = json.loads(SCHEMA_JSON_PATH.read_text(encoding="utf-8"))
    sections = data["memo_sections"]
    ids = {s.get("id") for s in sections if isinstance(s, dict)}
    for sid in pams.REQUIRED_MEMO_SECTION_IDS:
        assert sid in ids, f"memo section missing: {sid}"
    for s in sections:
        assert s["produced_in_this_bundle"] is False, s
        assert s["purpose"], s
        assert isinstance(s["required_fields"], list) and s["required_fields"], s


def test_allowed_classifications_exactly_five():
    data = json.loads(SCHEMA_JSON_PATH.read_text(encoding="utf-8"))
    ids = {c.get("id") for c in data["allowed_classifications"]}
    assert ids == set(pams.ALLOWED_CLASSIFICATION_IDS), ids
    for cid in ids:
        assert cid.startswith("watch_only_") or cid == "undefined_insufficient_data", cid


def test_forbidden_verdict_language_enumerated():
    data = json.loads(SCHEMA_JSON_PATH.read_text(encoding="utf-8"))
    fvl = set(data["forbidden_verdict_language"])
    for tok in pams.REQUIRED_FORBIDDEN_VERDICT_TOKENS:
        assert tok in fvl, f"forbidden_verdict_language missing: {tok}"


def test_c10_is_deferred_not_connected():
    data = json.loads(SCHEMA_JSON_PATH.read_text(encoding="utf-8"))
    c10b = data["c10_boundary"]
    assert c10b["must_not_touch_c10"] is True
    assert c10b["connection_status"] == "deferred_not_connected"


def test_verdict_ceiling_watch_max():
    data = json.loads(SCHEMA_JSON_PATH.read_text(encoding="utf-8"))
    vcr = data["verdict_ceiling_rules"]
    assert vcr["max_surfaced_verdict"] == "WATCH"
    assert vcr["pass_active_strong_forbidden"] is True


def test_pass_watch_fail_rules_present():
    data = json.loads(SCHEMA_JSON_PATH.read_text(encoding="utf-8"))
    pwf = data["pass_watch_fail_rules"]
    for k in ("PASS", "WATCH", "FAIL"):
        assert k in pwf, f"pass_watch_fail_rules missing: {k}"


def test_no_capability_claims():
    md = SCHEMA_MD_PATH.read_text(encoding="utf-8").lower()
    jsn = json.dumps(json.loads(SCHEMA_JSON_PATH.read_text(encoding="utf-8")),
                    ensure_ascii=False).lower()
    for phrase in pams.FORBIDDEN_PHRASES:
        assert phrase.lower() not in md, f"capability claim in MD: {phrase!r}"
        assert phrase.lower() not in jsn, f"capability claim in JSON: {phrase!r}"


def test_distinction_phrases_present_in_md():
    md = SCHEMA_MD_PATH.read_text(encoding="utf-8")
    for phrase in pams.DISTINCTION_PHRASES:
        assert phrase in md, f"distinction phrase missing: {phrase!r}"


# --- validator failure modes --------------------------------------------- #

def _stage_tmp(tmp_path: Path):
    tmp_dir = tmp_path / pams.SCHEMA_DIR_REL
    tmp_dir.mkdir(parents=True, exist_ok=True)
    (tmp_dir / pams.SCHEMA_MD).write_text(SCHEMA_MD_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    data = json.loads(SCHEMA_JSON_PATH.read_text(encoding="utf-8"))
    return tmp_dir, data


def test_validator_detects_extra_classification(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["allowed_classifications"].append({"id": "approved_for_live_trading", "tier": "STRONG", "meaning": "x"})
    (tmp_dir / pams.SCHEMA_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = pams.validate(tmp_path)
    assert not ok
    assert any("non-allowed labels" in e or "watch_only_" in e for e in errs)


def test_validator_detects_dropped_forbidden_token(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["forbidden_verdict_language"] = [t for t in data["forbidden_verdict_language"] if t != "STRONG"]
    (tmp_dir / pams.SCHEMA_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = pams.validate(tmp_path)
    assert not ok
    assert any("forbidden_verdict_language missing token" in e for e in errs)


def test_validator_detects_memo_produced_flip(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["memo_produced_in_this_bundle"] = True
    (tmp_dir / pams.SCHEMA_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = pams.validate(tmp_path)
    assert not ok
    assert any("memo_produced_in_this_bundle" in e for e in errs)


def test_validator_detects_capital_deployment_flag(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["capital_deployment_enabled"] = True
    (tmp_dir / pams.SCHEMA_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = pams.validate(tmp_path)
    assert not ok
    assert any("capital_deployment_enabled" in e for e in errs)


def test_validator_detects_connected_c10(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["c10_boundary"]["connection_status"] = "connected"
    (tmp_dir / pams.SCHEMA_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = pams.validate(tmp_path)
    assert not ok
    assert any("connection_status" in e for e in errs)


def test_validator_detects_capability_claim_in_md(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    (tmp_dir / pams.SCHEMA_JSON).write_text(json.dumps(data), encoding="utf-8")
    md = SCHEMA_MD_PATH.read_text(encoding="utf-8") + "\nNote: deploy capital now.\n"
    (tmp_dir / pams.SCHEMA_MD).write_text(md, encoding="utf-8")
    ok, errs = pams.validate(tmp_path)
    assert not ok
    assert any("deploy capital now" in e for e in errs)


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
        "import alpaca", "from alpaca",
        "import binance", "from binance",
        "import dotenv", "from dotenv",
        "import subprocess", "from subprocess",
        "os.environ", "getenv",
        "urlopen", "api.telegram.org",
    )
    for tok in forbidden:
        assert tok not in src, f"forbidden token: {tok!r}"


def test_validator_cli_show_and_validate():
    assert pams.main(["validate", "--repo-root", str(_REPO_ROOT)]) == 0
    assert pams.main(["show", "--repo-root", str(_REPO_ROOT)]) == 0


# --- companion integration ----------------------------------------------- #

def test_p4_overlap_correlation_validator_still_passes():
    ok, errs = pocc.validate(_REPO_ROOT)
    assert ok, errs


def test_p3_allocation_baseline_validator_still_passes():
    ok, errs = pabc.validate(_REPO_ROOT)
    assert ok, errs


def test_p2_metric_spec_validator_still_passes():
    ok, errs = pmsc.validate(_REPO_ROOT)
    assert ok, errs


def test_p1_input_contract_validator_still_passes():
    ok, errs = picc.validate(_REPO_ROOT)
    assert ok, errs


def test_p0_protocol_validator_still_passes():
    ok, errs = pcec.validate(_REPO_ROOT)
    assert ok, errs
