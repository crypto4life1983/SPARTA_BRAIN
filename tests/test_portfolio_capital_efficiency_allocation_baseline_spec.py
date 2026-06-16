"""Portfolio Capital-Efficiency Allocation Baseline Spec v1 (P3) tests (research-only).

Pure stdlib + pytest. Asserts:
  * allocation_baseline_spec.json + .md exist and validate
  * research_only + advisory_only + framework_only True; compute_enabled +
    capital_deployment_enabled + eight execution flags pinned False
  * lane == 'portfolio_capital_efficiency'; phase == 'P3_allocation_baseline_spec';
    self-declared status == WATCH
  * companion_documents reference P0 + P1 + P2
  * the 6 required baselines are present, each spec-only with method + inputs +
    constraints + non-empty validation_rules
  * ranking_only_marginal_efficiency is ranking_only
  * zero_for_inadmissible + cash_unallocated_bucket are hard_constraint
  * allocation_constraints carry the core invariants
  * Candidate #10 deferred (c10_boundary deferred_not_connected + must_not_touch)
  * verdict ceiling max == WATCH
  * pass/watch/fail rules exist
  * no profitability / live-readiness / allocate-now / deploy-now / connect-c10 claim
  * validator catches computed baseline / tampered flag / connected-C10 /
    ranking-only flip / forbidden phrase
  * validator tool is stdlib-only; no network/broker/exchange imports
  * P0 + P1 + P2 validators still pass (companion bundles unaffected)
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

import portfolio_capital_efficiency_allocation_baseline_spec_check as pabc  # noqa: E402
import portfolio_capital_efficiency_metric_spec_check as pmsc              # noqa: E402
import portfolio_capital_efficiency_input_contract_check as picc           # noqa: E402
import portfolio_capital_efficiency_protocol_check as pcec                 # noqa: E402

TOOL_FILE = _TOOLS_DIR / "portfolio_capital_efficiency_allocation_baseline_spec_check.py"
SPEC_JSON_PATH = _REPO_ROOT / pabc.SPEC_DIR_REL / pabc.SPEC_JSON
SPEC_MD_PATH = _REPO_ROOT / pabc.SPEC_DIR_REL / pabc.SPEC_MD


# --- existence + validation ---------------------------------------------- #

def test_spec_json_exists():
    assert SPEC_JSON_PATH.exists(), f"missing: {SPEC_JSON_PATH}"


def test_spec_md_exists():
    assert SPEC_MD_PATH.exists(), f"missing: {SPEC_MD_PATH}"


def test_validator_passes_on_committed_spec():
    ok, errs = pabc.validate(_REPO_ROOT)
    assert ok, errs


def test_flags_false_and_framework_only():
    data = json.loads(SPEC_JSON_PATH.read_text(encoding="utf-8"))
    for flag in pabc.MUST_BE_FALSE_FLAGS:
        assert data.get(flag) is False, f"{flag} must be False"
    assert data.get("research_only") is True
    assert data.get("advisory_only") is True
    assert data.get("framework_only") is True
    assert data.get("compute_enabled") is False
    assert data.get("capital_deployment_enabled") is False


def test_required_top_level_sections_present():
    data = json.loads(SPEC_JSON_PATH.read_text(encoding="utf-8"))
    for k in pabc.REQUIRED_TOP_LEVEL_KEYS:
        assert k in data, f"missing top-level key: {k}"


def test_lane_phase_and_watch_status():
    data = json.loads(SPEC_JSON_PATH.read_text(encoding="utf-8"))
    assert data["lane"] == "portfolio_capital_efficiency"
    assert data["phase"] == "P3_allocation_baseline_spec"
    assert data["lane_status_self_declared"] == "WATCH"


def test_companion_documents_reference_p0_p1_p2():
    data = json.loads(SPEC_JSON_PATH.read_text(encoding="utf-8"))
    joined = " ".join(str(v) for v in data["companion_documents"].values())
    assert "portfolio_capital_efficiency_protocol_v1" in joined
    assert "portfolio_capital_efficiency_input_contract_v1" in joined
    assert "portfolio_capital_efficiency_metric_spec_v1" in joined


def test_six_baselines_present_and_spec_only():
    data = json.loads(SPEC_JSON_PATH.read_text(encoding="utf-8"))
    baselines = data["allocation_baselines"]
    ids = {b.get("id") for b in baselines if isinstance(b, dict)}
    for bid in pabc.REQUIRED_BASELINE_IDS:
        assert bid in ids, f"baseline missing: {bid}"
    for b in baselines:
        assert b["computed_in_this_bundle"] is False, b
        assert b["method"], b
        assert isinstance(b["inputs"], list) and b["inputs"], b
        assert isinstance(b["constraints"], list) and b["constraints"], b
        assert isinstance(b["validation_rules"], list) and b["validation_rules"], b


def test_ranking_only_baseline_is_ranking_only():
    data = json.loads(SPEC_JSON_PATH.read_text(encoding="utf-8"))
    rk = next(b for b in data["allocation_baselines"] if b.get("id") == "ranking_only_marginal_efficiency")
    assert rk["ranking_only"] is True


def test_zero_and_cash_are_hard_constraints():
    data = json.loads(SPEC_JSON_PATH.read_text(encoding="utf-8"))
    by_id = {b.get("id"): b for b in data["allocation_baselines"]}
    assert by_id["zero_for_inadmissible"]["status"] == "hard_constraint"
    assert by_id["cash_unallocated_bucket"]["status"] == "hard_constraint"


def test_allocation_constraints_core_invariants():
    data = json.loads(SPEC_JSON_PATH.read_text(encoding="utf-8"))
    ac = data["allocation_constraints"]
    for k in pabc.REQUIRED_ALLOCATION_CONSTRAINT_KEYS:
        assert k in ac, f"allocation_constraints missing: {k}"


def test_c10_is_deferred_not_connected():
    data = json.loads(SPEC_JSON_PATH.read_text(encoding="utf-8"))
    c10b = data["c10_boundary"]
    assert c10b["must_not_touch_c10"] is True
    assert c10b["connection_status"] == "deferred_not_connected"


def test_verdict_ceiling_watch_max():
    data = json.loads(SPEC_JSON_PATH.read_text(encoding="utf-8"))
    vcr = data["verdict_ceiling_rules"]
    assert vcr["max_surfaced_verdict"] == "WATCH"
    assert vcr["pass_active_strong_forbidden"] is True


def test_pass_watch_fail_rules_present():
    data = json.loads(SPEC_JSON_PATH.read_text(encoding="utf-8"))
    pwf = data["pass_watch_fail_rules"]
    for k in ("PASS", "WATCH", "FAIL"):
        assert k in pwf, f"pass_watch_fail_rules missing: {k}"


def test_no_forbidden_claims():
    md = SPEC_MD_PATH.read_text(encoding="utf-8").lower()
    jsn = json.dumps(json.loads(SPEC_JSON_PATH.read_text(encoding="utf-8")),
                    ensure_ascii=False).lower()
    for phrase in pabc.FORBIDDEN_PHRASES:
        assert phrase.lower() not in md, f"forbidden phrase in MD: {phrase!r}"
        assert phrase.lower() not in jsn, f"forbidden phrase in JSON: {phrase!r}"


def test_distinction_phrases_present_in_md():
    md = SPEC_MD_PATH.read_text(encoding="utf-8")
    for phrase in pabc.DISTINCTION_PHRASES:
        assert phrase in md, f"distinction phrase missing: {phrase!r}"


# --- validator failure modes --------------------------------------------- #

def _stage_tmp(tmp_path: Path):
    tmp_dir = tmp_path / pabc.SPEC_DIR_REL
    tmp_dir.mkdir(parents=True, exist_ok=True)
    (tmp_dir / pabc.SPEC_MD).write_text(SPEC_MD_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    data = json.loads(SPEC_JSON_PATH.read_text(encoding="utf-8"))
    return tmp_dir, data


def test_validator_detects_computed_baseline(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["allocation_baselines"][0]["computed_in_this_bundle"] = True
    (tmp_dir / pabc.SPEC_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = pabc.validate(tmp_path)
    assert not ok
    assert any("computed_in_this_bundle" in e for e in errs)


def test_validator_detects_capital_deployment_flag(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["capital_deployment_enabled"] = True
    (tmp_dir / pabc.SPEC_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = pabc.validate(tmp_path)
    assert not ok
    assert any("capital_deployment_enabled" in e for e in errs)


def test_validator_detects_connected_c10(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["c10_boundary"]["connection_status"] = "connected"
    (tmp_dir / pabc.SPEC_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = pabc.validate(tmp_path)
    assert not ok
    assert any("connection_status" in e for e in errs)


def test_validator_detects_ranking_only_flip(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    for b in data["allocation_baselines"]:
        if b.get("id") == "ranking_only_marginal_efficiency":
            b["ranking_only"] = False
    (tmp_dir / pabc.SPEC_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = pabc.validate(tmp_path)
    assert not ok
    assert any("ranking_only" in e for e in errs)


def test_validator_detects_missing_inadmissible_zero_constraint(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    del data["allocation_constraints"]["inadmissible_weight_zero"]
    (tmp_dir / pabc.SPEC_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = pabc.validate(tmp_path)
    assert not ok
    assert any("inadmissible_weight_zero" in e for e in errs)


def test_validator_detects_forbidden_phrase_in_md(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    (tmp_dir / pabc.SPEC_JSON).write_text(json.dumps(data), encoding="utf-8")
    md = SPEC_MD_PATH.read_text(encoding="utf-8") + "\nNote: deploy capital now.\n"
    (tmp_dir / pabc.SPEC_MD).write_text(md, encoding="utf-8")
    ok, errs = pabc.validate(tmp_path)
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
    assert pabc.main(["validate", "--repo-root", str(_REPO_ROOT)]) == 0
    assert pabc.main(["show", "--repo-root", str(_REPO_ROOT)]) == 0


# --- companion integration ----------------------------------------------- #

def test_p2_metric_spec_validator_still_passes():
    ok, errs = pmsc.validate(_REPO_ROOT)
    assert ok, errs


def test_p1_input_contract_validator_still_passes():
    ok, errs = picc.validate(_REPO_ROOT)
    assert ok, errs


def test_p0_protocol_validator_still_passes():
    ok, errs = pcec.validate(_REPO_ROOT)
    assert ok, errs
