"""Portfolio Capital-Efficiency Overlap/Correlation Method v1 (P4) tests (research-only).

Pure stdlib + pytest. Asserts:
  * overlap_correlation_method.json + .md exist and validate
  * research_only + advisory_only + framework_only True; compute_enabled +
    eight execution flags pinned False
  * lane == 'portfolio_capital_efficiency'; phase == 'P4_overlap_correlation_method';
    self-declared status == WATCH
  * companion_documents reference P0 + P1 + P2 + P3
  * required_frozen_series present
  * the 8 required methods are present, each spec-only with formula + inputs +
    units + range + non-empty validation_rules
  * return_stream_correlation present (rho_ij)
  * independence_classification declares all 4 classes incl 'undefined', is
    not computed here, pins pre-declared thresholds
  * Candidate #10 deferred (c10_boundary deferred_not_connected + must_not_touch)
  * verdict ceiling max == WATCH
  * pass/watch/fail rules exist
  * no profitability / live-readiness / allocate-now / connect-c10 claim
  * validator catches computed method / tampered flag / connected-C10 /
    missing 'undefined' class / forbidden phrase
  * validator tool is stdlib-only; no network/broker/exchange imports
  * P0 + P1 + P2 + P3 validators still pass (companion bundles unaffected)
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

import portfolio_capital_efficiency_overlap_correlation_method_check as pocc  # noqa: E402
import portfolio_capital_efficiency_allocation_baseline_spec_check as pabc    # noqa: E402
import portfolio_capital_efficiency_metric_spec_check as pmsc                 # noqa: E402
import portfolio_capital_efficiency_input_contract_check as picc              # noqa: E402
import portfolio_capital_efficiency_protocol_check as pcec                    # noqa: E402

TOOL_FILE = _TOOLS_DIR / "portfolio_capital_efficiency_overlap_correlation_method_check.py"
METHOD_JSON_PATH = _REPO_ROOT / pocc.METHOD_DIR_REL / pocc.METHOD_JSON
METHOD_MD_PATH = _REPO_ROOT / pocc.METHOD_DIR_REL / pocc.METHOD_MD


# --- existence + validation ---------------------------------------------- #

def test_method_json_exists():
    assert METHOD_JSON_PATH.exists(), f"missing: {METHOD_JSON_PATH}"


def test_method_md_exists():
    assert METHOD_MD_PATH.exists(), f"missing: {METHOD_MD_PATH}"


def test_validator_passes_on_committed_method():
    ok, errs = pocc.validate(_REPO_ROOT)
    assert ok, errs


def test_flags_false_and_framework_only():
    data = json.loads(METHOD_JSON_PATH.read_text(encoding="utf-8"))
    for flag in pocc.MUST_BE_FALSE_FLAGS:
        assert data.get(flag) is False, f"{flag} must be False"
    assert data.get("research_only") is True
    assert data.get("advisory_only") is True
    assert data.get("framework_only") is True
    assert data.get("compute_enabled") is False


def test_required_top_level_sections_present():
    data = json.loads(METHOD_JSON_PATH.read_text(encoding="utf-8"))
    for k in pocc.REQUIRED_TOP_LEVEL_KEYS:
        assert k in data, f"missing top-level key: {k}"


def test_lane_phase_and_watch_status():
    data = json.loads(METHOD_JSON_PATH.read_text(encoding="utf-8"))
    assert data["lane"] == "portfolio_capital_efficiency"
    assert data["phase"] == "P4_overlap_correlation_method"
    assert data["lane_status_self_declared"] == "WATCH"


def test_companion_documents_reference_p0_p1_p2_p3():
    data = json.loads(METHOD_JSON_PATH.read_text(encoding="utf-8"))
    joined = " ".join(str(v) for v in data["companion_documents"].values())
    assert "portfolio_capital_efficiency_protocol_v1" in joined
    assert "portfolio_capital_efficiency_input_contract_v1" in joined
    assert "portfolio_capital_efficiency_metric_spec_v1" in joined
    assert "portfolio_capital_efficiency_allocation_baseline_spec_v1" in joined


def test_required_frozen_series_present():
    data = json.loads(METHOD_JSON_PATH.read_text(encoding="utf-8"))
    assert data["required_frozen_series"]["series"]


def test_eight_methods_present_and_spec_only():
    data = json.loads(METHOD_JSON_PATH.read_text(encoding="utf-8"))
    methods = data["methods"]
    ids = {m.get("id") for m in methods if isinstance(m, dict)}
    for mid in pocc.REQUIRED_METHOD_IDS:
        assert mid in ids, f"method missing: {mid}"
    for m in methods:
        assert m["computed_in_this_bundle"] is False, m
        assert m["formula"], m
        assert isinstance(m["inputs"], list) and m["inputs"], m
        assert m["units"], m
        assert m["range"], m
        assert isinstance(m["validation_rules"], list) and m["validation_rules"], m


def test_return_stream_correlation_is_rho_ij():
    data = json.loads(METHOD_JSON_PATH.read_text(encoding="utf-8"))
    rsc = next(m for m in data["methods"] if m.get("id") == "return_stream_correlation")
    assert "rho_ij" in rsc["formula"]


def test_independence_classification_four_classes_incl_undefined():
    data = json.loads(METHOD_JSON_PATH.read_text(encoding="utf-8"))
    ic = data["independence_classification"]
    assert ic["computed_in_this_bundle"] is False
    classes = {c["class"] for c in ic["classes"]}
    for cls in pocc.REQUIRED_INDEPENDENCE_CLASSES:
        assert cls in classes, f"missing class: {cls}"
    assert "undefined" in classes
    assert ic["thresholds_are_pre_declared_operator_constants"] is True


def test_c10_is_deferred_not_connected():
    data = json.loads(METHOD_JSON_PATH.read_text(encoding="utf-8"))
    c10b = data["c10_boundary"]
    assert c10b["must_not_touch_c10"] is True
    assert c10b["connection_status"] == "deferred_not_connected"


def test_verdict_ceiling_watch_max():
    data = json.loads(METHOD_JSON_PATH.read_text(encoding="utf-8"))
    vcr = data["verdict_ceiling_rules"]
    assert vcr["max_surfaced_verdict"] == "WATCH"
    assert vcr["pass_active_strong_forbidden"] is True


def test_pass_watch_fail_rules_present():
    data = json.loads(METHOD_JSON_PATH.read_text(encoding="utf-8"))
    pwf = data["pass_watch_fail_rules"]
    for k in ("PASS", "WATCH", "FAIL"):
        assert k in pwf, f"pass_watch_fail_rules missing: {k}"


def test_no_forbidden_claims():
    md = METHOD_MD_PATH.read_text(encoding="utf-8").lower()
    jsn = json.dumps(json.loads(METHOD_JSON_PATH.read_text(encoding="utf-8")),
                    ensure_ascii=False).lower()
    for phrase in pocc.FORBIDDEN_PHRASES:
        assert phrase.lower() not in md, f"forbidden phrase in MD: {phrase!r}"
        assert phrase.lower() not in jsn, f"forbidden phrase in JSON: {phrase!r}"


def test_distinction_phrases_present_in_md():
    md = METHOD_MD_PATH.read_text(encoding="utf-8")
    for phrase in pocc.DISTINCTION_PHRASES:
        assert phrase in md, f"distinction phrase missing: {phrase!r}"


# --- validator failure modes --------------------------------------------- #

def _stage_tmp(tmp_path: Path):
    tmp_dir = tmp_path / pocc.METHOD_DIR_REL
    tmp_dir.mkdir(parents=True, exist_ok=True)
    (tmp_dir / pocc.METHOD_MD).write_text(METHOD_MD_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    data = json.loads(METHOD_JSON_PATH.read_text(encoding="utf-8"))
    return tmp_dir, data


def test_validator_detects_computed_method(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["methods"][0]["computed_in_this_bundle"] = True
    (tmp_dir / pocc.METHOD_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = pocc.validate(tmp_path)
    assert not ok
    assert any("computed_in_this_bundle" in e for e in errs)


def test_validator_detects_compute_enabled_flag(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["compute_enabled"] = True
    (tmp_dir / pocc.METHOD_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = pocc.validate(tmp_path)
    assert not ok
    assert any("compute_enabled" in e for e in errs)


def test_validator_detects_connected_c10(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["c10_boundary"]["connection_status"] = "connected"
    (tmp_dir / pocc.METHOD_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = pocc.validate(tmp_path)
    assert not ok
    assert any("connection_status" in e for e in errs)


def test_validator_detects_missing_undefined_class(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["independence_classification"]["classes"] = [
        c for c in data["independence_classification"]["classes"] if c.get("class") != "undefined"
    ]
    (tmp_dir / pocc.METHOD_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = pocc.validate(tmp_path)
    assert not ok
    assert any("undefined" in e for e in errs)


def test_validator_detects_forbidden_phrase_in_md(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    (tmp_dir / pocc.METHOD_JSON).write_text(json.dumps(data), encoding="utf-8")
    md = METHOD_MD_PATH.read_text(encoding="utf-8") + "\nNote: deploy capital now.\n"
    (tmp_dir / pocc.METHOD_MD).write_text(md, encoding="utf-8")
    ok, errs = pocc.validate(tmp_path)
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
    assert pocc.main(["validate", "--repo-root", str(_REPO_ROOT)]) == 0
    assert pocc.main(["show", "--repo-root", str(_REPO_ROOT)]) == 0


# --- companion integration ----------------------------------------------- #

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
