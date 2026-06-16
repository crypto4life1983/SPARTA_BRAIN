"""Portfolio Capital-Efficiency Input Contract v1 (P1) tests (research-only).

Pure stdlib + pytest. Asserts:
  * input_contract.json + input_contract.md exist and validate
  * research_only + advisory_only + framework_only are True
  * the eight execution / fetch / connection / allocation / sizing / backtest
    flags are pinned False
  * lane == 'portfolio_capital_efficiency'; phase == 'P1_input_contract';
    self-declared status == WATCH
  * companion_documents reference the P0 protocol
  * admissible_input_classes are all read_only + frozen_required
  * Candidate #10 is a DEFERRED, NOT-CONNECTED input (deferred_inputs +
    c10_boundary both say deferred_not_connected; must_not_touch_c10 True)
  * inadmissible_inputs name live + uncommitted
  * verdict ceiling max == WATCH; PASS/ACTIVE/STRONG forbidden
  * pass/watch/fail rules exist
  * no profitability / live-readiness / allocate-now / connect-c10 claim
  * validator catches tampered flag / connected-C10 / bypassed verdict
    ceiling / non-frozen input / forbidden phrase
  * validator tool is stdlib-only; no network/broker/exchange imports
  * P0 protocol validator still passes (companion bundle unaffected)
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

import portfolio_capital_efficiency_input_contract_check as picc  # noqa: E402
import portfolio_capital_efficiency_protocol_check as pcec        # noqa: E402

TOOL_FILE = _TOOLS_DIR / "portfolio_capital_efficiency_input_contract_check.py"
CONTRACT_JSON_PATH = _REPO_ROOT / picc.CONTRACT_DIR_REL / picc.CONTRACT_JSON
CONTRACT_MD_PATH = _REPO_ROOT / picc.CONTRACT_DIR_REL / picc.CONTRACT_MD


# --- existence + validation ---------------------------------------------- #

def test_contract_json_exists():
    assert CONTRACT_JSON_PATH.exists(), f"missing: {CONTRACT_JSON_PATH}"


def test_contract_md_exists():
    assert CONTRACT_MD_PATH.exists(), f"missing: {CONTRACT_MD_PATH}"


def test_validator_passes_on_committed_contract():
    ok, errs = picc.validate(_REPO_ROOT)
    assert ok, errs


def test_eight_flags_all_false_and_framework_only():
    data = json.loads(CONTRACT_JSON_PATH.read_text(encoding="utf-8"))
    for flag in picc.MUST_BE_FALSE_FLAGS:
        assert data.get(flag) is False, f"{flag} must be False"
    assert data.get("research_only") is True
    assert data.get("advisory_only") is True
    assert data.get("framework_only") is True


def test_required_top_level_sections_present():
    data = json.loads(CONTRACT_JSON_PATH.read_text(encoding="utf-8"))
    for k in picc.REQUIRED_TOP_LEVEL_KEYS:
        assert k in data, f"missing top-level key: {k}"


def test_lane_phase_and_watch_status():
    data = json.loads(CONTRACT_JSON_PATH.read_text(encoding="utf-8"))
    assert data["lane"] == "portfolio_capital_efficiency"
    assert data["phase"] == "P1_input_contract"
    assert data["lane_status_self_declared"] == "WATCH"


def test_companion_documents_reference_p0_protocol():
    data = json.loads(CONTRACT_JSON_PATH.read_text(encoding="utf-8"))
    joined = " ".join(str(v) for v in data["companion_documents"].values())
    assert "portfolio_capital_efficiency_protocol_v1" in joined


def test_admissible_input_classes_read_only_and_frozen():
    data = json.loads(CONTRACT_JSON_PATH.read_text(encoding="utf-8"))
    aic = data["admissible_input_classes"]
    ids = {c.get("id") for c in aic if isinstance(c, dict)}
    for cid in picc.REQUIRED_INPUT_CLASS_IDS:
        assert cid in ids, f"missing input class: {cid}"
    for c in aic:
        assert c["access"] == "read_only", c
        assert c["frozen_required"] is True, c


def test_c10_is_deferred_not_connected():
    data = json.loads(CONTRACT_JSON_PATH.read_text(encoding="utf-8"))
    # deferred_inputs entry
    di = data["deferred_inputs"]
    c10 = next(d for d in di if d.get("id") == "c10_frozen_replay_output")
    assert c10["connection_status"] == "deferred_not_connected", c10
    # c10_boundary
    c10b = data["c10_boundary"]
    assert c10b["must_not_touch_c10"] is True
    assert c10b["connection_status"] == "deferred_not_connected"


def test_inadmissible_inputs_name_live_and_uncommitted():
    data = json.loads(CONTRACT_JSON_PATH.read_text(encoding="utf-8"))
    joined = " ".join(data["inadmissible_inputs"]).lower()
    assert "live" in joined
    assert "uncommitted" in joined


def test_verdict_ceiling_watch_max():
    data = json.loads(CONTRACT_JSON_PATH.read_text(encoding="utf-8"))
    vcr = data["verdict_ceiling_rules"]
    assert vcr["max_surfaced_verdict"] == "WATCH"
    assert vcr["pass_active_strong_forbidden"] is True


def test_pass_watch_fail_rules_present():
    data = json.loads(CONTRACT_JSON_PATH.read_text(encoding="utf-8"))
    pwf = data["pass_watch_fail_rules"]
    for k in ("PASS", "WATCH", "FAIL"):
        assert k in pwf, f"pass_watch_fail_rules missing: {k}"


def test_no_profitability_or_alloc_now_or_connect_c10_claims():
    md = CONTRACT_MD_PATH.read_text(encoding="utf-8").lower()
    jsn = json.dumps(json.loads(CONTRACT_JSON_PATH.read_text(encoding="utf-8")),
                    ensure_ascii=False).lower()
    for phrase in picc.FORBIDDEN_PHRASES:
        assert phrase.lower() not in md, f"forbidden phrase in MD: {phrase!r}"
        assert phrase.lower() not in jsn, f"forbidden phrase in JSON: {phrase!r}"


def test_distinction_phrases_present_in_md():
    md = CONTRACT_MD_PATH.read_text(encoding="utf-8")
    for phrase in picc.DISTINCTION_PHRASES:
        assert phrase in md, f"distinction phrase missing: {phrase!r}"


# --- validator failure modes --------------------------------------------- #

def _stage_tmp(tmp_path: Path):
    tmp_dir = tmp_path / picc.CONTRACT_DIR_REL
    tmp_dir.mkdir(parents=True, exist_ok=True)
    (tmp_dir / picc.CONTRACT_MD).write_text(CONTRACT_MD_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    data = json.loads(CONTRACT_JSON_PATH.read_text(encoding="utf-8"))
    return tmp_dir, data


def test_validator_detects_tampered_safety_flag(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["live_capital_allocation_enabled"] = True
    (tmp_dir / picc.CONTRACT_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = picc.validate(tmp_path)
    assert not ok
    assert any("live_capital_allocation_enabled" in e for e in errs)


def test_validator_detects_connected_c10(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["c10_boundary"]["connection_status"] = "connected"
    (tmp_dir / picc.CONTRACT_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = picc.validate(tmp_path)
    assert not ok
    assert any("connection_status" in e for e in errs)


def test_validator_detects_deferred_input_flip(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    for d in data["deferred_inputs"]:
        if d.get("id") == "c10_frozen_replay_output":
            d["connection_status"] = "connected"
    (tmp_dir / picc.CONTRACT_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = picc.validate(tmp_path)
    assert not ok
    assert any("deferred_not_connected" in e for e in errs)


def test_validator_detects_bypassed_verdict_ceiling(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["verdict_ceiling_rules"]["max_surfaced_verdict"] = "STRONG"
    (tmp_dir / picc.CONTRACT_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = picc.validate(tmp_path)
    assert not ok
    assert any("max_surfaced_verdict" in e for e in errs)


def test_validator_detects_non_frozen_input(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    data["admissible_input_classes"][0]["frozen_required"] = False
    (tmp_dir / picc.CONTRACT_JSON).write_text(json.dumps(data), encoding="utf-8")
    ok, errs = picc.validate(tmp_path)
    assert not ok
    assert any("frozen_required" in e for e in errs)


def test_validator_detects_forbidden_phrase_in_md(tmp_path):
    tmp_dir, data = _stage_tmp(tmp_path)
    (tmp_dir / picc.CONTRACT_JSON).write_text(json.dumps(data), encoding="utf-8")
    md = CONTRACT_MD_PATH.read_text(encoding="utf-8") + "\nNote: connect c10 now.\n"
    (tmp_dir / picc.CONTRACT_MD).write_text(md, encoding="utf-8")
    ok, errs = picc.validate(tmp_path)
    assert not ok
    assert any("connect c10 now" in e for e in errs)


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
    assert picc.main(["validate", "--repo-root", str(_REPO_ROOT)]) == 0
    assert picc.main(["show", "--repo-root", str(_REPO_ROOT)]) == 0


# --- companion integration ----------------------------------------------- #

def test_p0_protocol_validator_still_passes():
    ok, errs = pcec.validate(_REPO_ROOT)
    assert ok, errs
