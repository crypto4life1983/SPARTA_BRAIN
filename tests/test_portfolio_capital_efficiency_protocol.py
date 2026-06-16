"""Portfolio Capital-Efficiency Protocol Memo v1 tests (research-only).

Pure stdlib + pytest. Asserts:
  * protocol.json + protocol.md exist and validate
  * research_only + advisory_only are True
  * the eight execution / fetch / connection / allocation / sizing / backtest
    flags are pinned False
  * all required top-level sections exist
  * lane == 'portfolio_capital_efficiency'; self-declared status == WATCH
  * c10_boundary.must_not_touch_c10 is True
  * scope.out_of_scope names live capital + order placement exclusions
  * input_sources are all read_only; inadmissible_inputs names live +
    uncommitted
  * the 5 capital-efficiency metrics are present + definition_only
  * the 4 allocation baselines are present; discretionary_human is WATCH_only
  * validation phases include P0..P8
  * pass/watch/fail rules exist
  * no profitability claim, no live-readiness claim, no allocate-now claim
  * validator catches tampered flag / bypassed WATCH status / dropped C10
    boundary / non-read-only input / computed metric / forbidden phrase
  * validator tool is stdlib-only; no network/broker/exchange imports
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

import portfolio_capital_efficiency_protocol_check as pcec  # noqa: E402

TOOL_FILE = _TOOLS_DIR / "portfolio_capital_efficiency_protocol_check.py"
PROTO_JSON_PATH = _REPO_ROOT / pcec.PROTO_DIR_REL / pcec.PROTO_JSON
PROTO_MD_PATH = _REPO_ROOT / pcec.PROTO_DIR_REL / pcec.PROTO_MD


# --- existence + validation ---------------------------------------------- #

def test_protocol_json_exists():
    assert PROTO_JSON_PATH.exists(), f"missing: {PROTO_JSON_PATH}"


def test_protocol_md_exists():
    assert PROTO_MD_PATH.exists(), f"missing: {PROTO_MD_PATH}"


def test_validator_passes_on_committed_protocol():
    ok, errs = pcec.validate(_REPO_ROOT)
    assert ok, errs


def test_eight_flags_all_false():
    data = json.loads(PROTO_JSON_PATH.read_text(encoding="utf-8"))
    for flag in pcec.MUST_BE_FALSE_FLAGS:
        assert data.get(flag) is False, f"{flag} must be False"
    assert data.get("research_only") is True
    assert data.get("advisory_only") is True


def test_required_top_level_sections_present():
    data = json.loads(PROTO_JSON_PATH.read_text(encoding="utf-8"))
    for k in pcec.REQUIRED_TOP_LEVEL_KEYS:
        assert k in data, f"missing top-level key: {k}"


def test_lane_and_self_declared_watch_status():
    data = json.loads(PROTO_JSON_PATH.read_text(encoding="utf-8"))
    assert data["lane"] == "portfolio_capital_efficiency"
    assert data["lane_status_self_declared"] == "WATCH"


def test_c10_boundary_pinned():
    data = json.loads(PROTO_JSON_PATH.read_text(encoding="utf-8"))
    assert data["c10_boundary"]["must_not_touch_c10"] is True


def test_scope_excludes_live_capital_and_execution():
    data = json.loads(PROTO_JSON_PATH.read_text(encoding="utf-8"))
    oos = " ".join(data["scope"]["out_of_scope"]).lower()
    assert "live capital" in oos
    assert "order placement" in oos


def test_input_sources_all_read_only():
    data = json.loads(PROTO_JSON_PATH.read_text(encoding="utf-8"))
    assert data["input_sources"], "input_sources must be non-empty"
    for s in data["input_sources"]:
        assert s["access"] == "read_only", s


def test_inadmissible_inputs_name_live_and_uncommitted():
    data = json.loads(PROTO_JSON_PATH.read_text(encoding="utf-8"))
    joined = " ".join(data["inadmissible_inputs"]).lower()
    assert "live" in joined
    assert "uncommitted" in joined


def test_five_metrics_present_and_definition_only():
    data = json.loads(PROTO_JSON_PATH.read_text(encoding="utf-8"))
    cem = data["capital_efficiency_metrics"]
    ids = {m.get("id") for m in cem if isinstance(m, dict)}
    for mid in pcec.REQUIRED_METRIC_IDS:
        assert mid in ids, f"metric missing: {mid}"
    for m in cem:
        assert m["definition_only"] is True, m


def test_four_baselines_with_discretionary_human_watch_only():
    data = json.loads(PROTO_JSON_PATH.read_text(encoding="utf-8"))
    ab = data["allocation_baselines"]
    ids = {b.get("id") for b in ab if isinstance(b, dict)}
    for bid in pcec.REQUIRED_BASELINE_IDS:
        assert bid in ids, f"baseline missing: {bid}"
    dh = next(b for b in ab if b.get("id") == "discretionary_human")
    assert dh["status"] == "WATCH_only"


def test_validation_phases_p0_through_p8_present():
    data = json.loads(PROTO_JSON_PATH.read_text(encoding="utf-8"))
    phase_ids = {p["phase"] for p in data["validation_phases"] if isinstance(p, dict)}
    for required in pcec.REQUIRED_VALIDATION_PHASES:
        assert required in phase_ids, f"missing phase: {required}"


def test_pass_watch_fail_rules_present():
    data = json.loads(PROTO_JSON_PATH.read_text(encoding="utf-8"))
    pwf = data["pass_watch_fail_rules"]
    for k in ("PASS", "WATCH", "FAIL"):
        assert k in pwf, f"pass_watch_fail_rules missing: {k}"


def test_no_profitability_or_alloc_now_claims():
    md = PROTO_MD_PATH.read_text(encoding="utf-8").lower()
    jsn = json.dumps(json.loads(PROTO_JSON_PATH.read_text(encoding="utf-8")),
                    ensure_ascii=False).lower()
    for phrase in pcec.FORBIDDEN_PHRASES:
        assert phrase.lower() not in md, f"forbidden phrase in MD: {phrase!r}"
        assert phrase.lower() not in jsn, f"forbidden phrase in JSON: {phrase!r}"


def test_distinction_phrases_present_in_md():
    md = PROTO_MD_PATH.read_text(encoding="utf-8")
    for phrase in pcec.DISTINCTION_PHRASES:
        assert phrase in md, f"distinction phrase missing: {phrase!r}"


# --- validator failure modes --------------------------------------------- #

def _stage_tmp(tmp_path: Path):
    tmp_dir = tmp_path / pcec.PROTO_DIR_REL
    tmp_dir.mkdir(parents=True, exist_ok=True)
    (tmp_dir / pcec.PROTO_MD).write_text(PROTO_MD_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    data = json.loads(PROTO_JSON_PATH.read_text(encoding="utf-8"))
    return tmp_dir, data


def test_validator_detects_tampered_safety_flag(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["live_capital_allocation_enabled"] = True
    (tmp_dir / pcec.PROTO_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = pcec.validate(tmp_path)
    assert not ok
    assert any("live_capital_allocation_enabled" in e for e in errs)


def test_validator_detects_bypassed_watch_status(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["lane_status_self_declared"] = "ACTIVE"
    (tmp_dir / pcec.PROTO_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = pcec.validate(tmp_path)
    assert not ok
    assert any("lane_status_self_declared" in e for e in errs)


def test_validator_detects_dropped_c10_boundary(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["c10_boundary"]["must_not_touch_c10"] = False
    (tmp_dir / pcec.PROTO_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = pcec.validate(tmp_path)
    assert not ok
    assert any("must_not_touch_c10" in e for e in errs)


def test_validator_detects_non_read_only_input(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["input_sources"][0]["access"] = "read_write"
    (tmp_dir / pcec.PROTO_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = pcec.validate(tmp_path)
    assert not ok
    assert any("read_only" in e for e in errs)


def test_validator_detects_computed_metric(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["capital_efficiency_metrics"][0]["definition_only"] = False
    (tmp_dir / pcec.PROTO_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = pcec.validate(tmp_path)
    assert not ok
    assert any("definition_only" in e for e in errs)


def test_validator_detects_forbidden_phrase_in_md(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    (tmp_dir / pcec.PROTO_JSON).write_text(json.dumps(data), encoding="utf-8")
    md = PROTO_MD_PATH.read_text(encoding="utf-8") + "\nNote: allocate capital now.\n"
    (tmp_dir / pcec.PROTO_MD).write_text(md, encoding="utf-8")
    ok, errs = pcec.validate(tmp_path)
    assert not ok
    assert any("allocate capital now" in e for e in errs)


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
    assert pcec.main(["validate", "--repo-root", str(_REPO_ROOT)]) == 0
    assert pcec.main(["show", "--repo-root", str(_REPO_ROOT)]) == 0
