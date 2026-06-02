"""Bundle 21 — Crypto-D1 Readiness Gate / Operator Checklist v1 tests.

Pure stdlib + pytest. Research-only. Asserts:
  * readiness_gate.json + readiness_gate.md exist and validate
  * the eleven safety flags are pinned False; research_only + read_only True
  * readiness_status is one of the 5 lifecycle statuses and defaults to
    NOT_READY_FOR_REAL_DATA
  * all 10 audited Bundle 11-20 artifacts are referenced, exist on disk
  * all 20 readiness questions are present and numbered 1..20
  * missing_items is non-empty; blockers is a list
  * the gate authorizes nothing (trading gate explicitly forbidden)
  * lane stays WATCH / MIXED; never ACTIVE, never STRONG
  * required distinction phrases present; no forbidden phrase present
  * no real data created; data/crypto_d1_research/ absent
  * validator catches tampered flag / bad status / missing artifact / promotion
    tamper / removed question / forbidden phrase
  * validator tool is stdlib-only; no network/broker/exchange/subprocess/env
  * prior Crypto-D1 validators still pass; registry still shows crypto_d1 WATCH
"""
from __future__ import annotations

import ast
import copy
import json
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]
_TOOLS_DIR = _REPO_ROOT / "tools"
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))

import crypto_d1_readiness_gate_check as cdrg                 # noqa: E402
import crypto_d1_manual_dataset_intake_runbook_check as cmir  # noqa: E402
import crypto_d1_data_source_evaluation_check as cdse         # noqa: E402
import crypto_d1_data_acquisition_authorization_check as cda  # noqa: E402
import crypto_d1_qa_freeze_spec_check as cqf                  # noqa: E402
import crypto_d1_dataset_manifest_check as cdm                # noqa: E402
import crypto_d1_data_contract_check as cdc                   # noqa: E402
import crypto_d1_protocol_check as cdpc                       # noqa: E402
import crypto_d1_backtest_plan_check as cbp                   # noqa: E402
import strategy_candidate_registry as scr                     # noqa: E402

TOOL_FILE = _TOOLS_DIR / "crypto_d1_readiness_gate_check.py"
GATE_JSON_PATH = _REPO_ROOT / cdrg.GATE_DIR_REL / cdrg.GATE_JSON
GATE_MD_PATH = _REPO_ROOT / cdrg.GATE_DIR_REL / cdrg.GATE_MD


def _data():
    return json.loads(GATE_JSON_PATH.read_text(encoding="utf-8"))


# --- existence + validation --------------------------------------------- #

def test_gate_json_exists():
    assert GATE_JSON_PATH.exists(), f"missing: {GATE_JSON_PATH}"


def test_gate_md_exists():
    assert GATE_MD_PATH.exists(), f"missing: {GATE_MD_PATH}"


def test_validator_passes_on_committed_gate():
    ok, errs = cdrg.validate(_REPO_ROOT)
    assert ok, errs


# --- safety flags ------------------------------------------------------- #

def test_eleven_flags_all_false():
    data = _data()
    assert len(cdrg.MUST_BE_FALSE_FLAGS) == 11
    for flag in cdrg.MUST_BE_FALSE_FLAGS:
        assert data.get(flag) is False, f"{flag} must be False"
    assert data.get("research_only") is True
    assert data.get("read_only") is True


# --- readiness status --------------------------------------------------- #

def test_status_default_is_not_ready():
    assert _data().get("readiness_status") == "NOT_READY_FOR_REAL_DATA"


def test_status_options_are_the_five():
    expected = [
        "NOT_READY_FOR_REAL_DATA",
        "READY_FOR_OPERATOR_DATA_INTAKE",
        "READY_FOR_QA_RUN",
        "READY_FOR_BASELINE_BACKTEST_REVIEW",
        "BLOCKED",
    ]
    assert _data().get("readiness_status_options") == expected
    assert list(cdrg.ALLOWED_READINESS_STATUSES) == expected


def test_status_rules_define_all_five():
    rules = _data().get("readiness_status_rules")
    for s in cdrg.ALLOWED_READINESS_STATUSES:
        assert s in rules, f"missing rule for {s}"


# --- scope -------------------------------------------------------------- #

def test_scope_assets_market_timeframe_calendar():
    data = _data()
    assert data.get("target_assets") == ["BTC", "ETH", "SOL"]
    assert data.get("allowed_market_type") == "spot"
    assert data.get("timeframe") == "1d"
    assert data.get("session_calendar") == "24/7"
    assert data.get("lane") == "crypto_d1_protocol"


# --- audited artifacts -------------------------------------------------- #

def test_ten_artifacts_present_and_on_disk():
    data = _data()
    arts = data.get("audited_artifacts")
    assert isinstance(arts, list) and len(arts) >= 10
    ids = {a["artifact_id"] for a in arts}
    for aid in cdrg.REQUIRED_AUDITED_ARTIFACT_IDS:
        assert aid in ids, f"missing audited artifact: {aid}"
    for a in arts:
        assert a.get("exists") is True
        assert (_REPO_ROOT / a["path"]).exists(), f"path missing on disk: {a['path']}"


def test_artifacts_cover_bundles_11_to_20():
    bundles = {a.get("bundle") for a in _data().get("audited_artifacts")}
    assert bundles == set(range(11, 21))


# --- 20 readiness questions --------------------------------------------- #

def test_twenty_questions_numbered_1_to_20():
    qs = _data().get("readiness_questions")
    assert isinstance(qs, list) and len(qs) == 20
    assert {q["number"] for q in qs} == set(range(1, 21))
    for q in qs:
        assert q.get("question")
        assert q.get("answer")


def test_question_20_reports_default_status():
    qs = _data().get("readiness_questions")
    q20 = next(q for q in qs if q["number"] == 20)
    assert q20["answer"] == "NOT_READY_FOR_REAL_DATA"


def test_question_19_paper_live_locked():
    qs = _data().get("readiness_questions")
    q19 = next(q for q in qs if q["number"] == 19)
    assert q19["answer"] == "YES"


# --- missing items / blockers ------------------------------------------- #

def test_missing_items_non_empty():
    assert len(_data().get("missing_items")) >= 10


def test_blockers_is_list():
    assert isinstance(_data().get("blockers"), list)


# --- future-authorization gates ----------------------------------------- #

def test_trading_gate_explicitly_forbidden():
    far = _data().get("future_authorization_requirements")
    assert far["trading_gate"]["explicitly_forbidden_by_this_readiness_gate"] is True


def test_intake_qa_backtest_gates_have_requirements():
    far = _data().get("future_authorization_requirements")
    for g in ("data_intake_gate", "qa_run_gate", "backtest_gate"):
        assert isinstance(far[g]["all_required"], list) and far[g]["all_required"]


# --- lane recommendation ------------------------------------------------ #

def test_lane_stays_watch_mixed_never_active_strong():
    lr = _data().get("lane_recommendation")
    assert lr["current_verdict"] == "WATCH"
    assert lr["evidence_level"] == "MIXED"
    assert lr["do_not_promote_to_ACTIVE"] is True
    assert lr["do_not_promote_to_STRONG_evidence"] is True


# --- distinction + forbidden phrases ------------------------------------ #

def test_distinction_phrases_present_in_both_docs():
    md = GATE_MD_PATH.read_text(encoding="utf-8")
    blob = json.dumps(_data(), ensure_ascii=False)
    for phrase in cdrg.DISTINCTION_PHRASES:
        assert phrase in md, f"md missing distinction phrase: {phrase!r}"
        assert phrase in blob, f"json missing distinction phrase: {phrase!r}"


def test_required_user_phrases_present():
    md = GATE_MD_PATH.read_text(encoding="utf-8")
    for phrase in (
        "NOT_READY_FOR_REAL_DATA is the honest default",
        "Specification completeness is not data readiness",
        "QA_PASS does not authorize live trading",
        "QA_PASS does not authorize paper trading",
        "QA_PASS does not authorize automatic backtesting",
        "A good historical chart does not imply future returns",
        "No real data has entered SPARTA",
        "Crypto-D1 remains WATCH / MIXED",
    ):
        assert phrase in md, f"required phrase missing: {phrase!r}"


def test_no_forbidden_phrases():
    md = GATE_MD_PATH.read_text(encoding="utf-8").lower()
    blob = json.dumps(_data(), ensure_ascii=False).lower()
    for phrase in cdrg.FORBIDDEN_PHRASES:
        assert phrase.lower() not in md, f"md has forbidden phrase: {phrase!r}"
        assert phrase.lower() not in blob, f"json has forbidden phrase: {phrase!r}"


# --- no real data / no data dir ----------------------------------------- #

def test_no_data_crypto_d1_research_directory():
    assert not (_REPO_ROOT / "data" / "crypto_d1_research").exists()


def test_gate_dir_contains_no_real_data_files():
    gate_dir = _REPO_ROOT / cdrg.GATE_DIR_REL
    bad = [p.name for p in gate_dir.iterdir()
           if p.suffix.lower() in (".csv", ".parquet", ".feather", ".db", ".sqlite")]
    assert not bad, f"unexpected data files in gate dir: {bad}"


# --- validator failure modes -------------------------------------------- #

def _validate_obj(tmp_path, obj, md_text=None):
    d = tmp_path / cdrg.GATE_DIR_REL
    d.mkdir(parents=True, exist_ok=True)
    (d / cdrg.GATE_JSON).write_text(json.dumps(obj), encoding="utf-8")
    src_md = GATE_MD_PATH.read_text(encoding="utf-8") if md_text is None else md_text
    (d / cdrg.GATE_MD).write_text(src_md, encoding="utf-8")
    # mirror the audited artifact paths so on-disk existence checks pass
    for a in obj.get("audited_artifacts", []):
        p = tmp_path / a.get("path", "")
        if a.get("path"):
            p.parent.mkdir(parents=True, exist_ok=True)
            if not p.exists():
                p.write_text("{}", encoding="utf-8")
    return cdrg.validate(tmp_path)


def test_validator_baseline_copy_passes(tmp_path):
    ok, errs = _validate_obj(tmp_path, _data())
    assert ok, errs


def test_validator_catches_tampered_flag(tmp_path):
    obj = _data()
    obj["live_trading_enabled"] = True
    ok, errs = _validate_obj(tmp_path, obj)
    assert not ok and any("live_trading_enabled" in e for e in errs)


def test_validator_catches_bad_status(tmp_path):
    obj = _data()
    obj["readiness_status"] = "READY_FOR_QA_RUN"
    ok, errs = _validate_obj(tmp_path, obj)
    assert not ok and any("default" in e for e in errs)


def test_validator_catches_unknown_status(tmp_path):
    obj = _data()
    obj["readiness_status"] = "TOTALLY_READY"
    ok, errs = _validate_obj(tmp_path, obj)
    assert not ok


def test_validator_catches_missing_artifact(tmp_path):
    obj = _data()
    obj["audited_artifacts"] = obj["audited_artifacts"][:-1]
    ok, errs = _validate_obj(tmp_path, obj)
    assert not ok


def test_validator_catches_dropped_question(tmp_path):
    obj = _data()
    obj["readiness_questions"] = obj["readiness_questions"][:-1]
    ok, errs = _validate_obj(tmp_path, obj)
    assert not ok


def test_validator_catches_promotion_tamper(tmp_path):
    obj = _data()
    obj["lane_recommendation"]["do_not_promote_to_ACTIVE"] = False
    ok, errs = _validate_obj(tmp_path, obj)
    assert not ok and any("do_not_promote_to_ACTIVE" in e for e in errs)


def test_validator_catches_empty_missing_items(tmp_path):
    obj = _data()
    obj["missing_items"] = []
    ok, errs = _validate_obj(tmp_path, obj)
    assert not ok and any("missing_items" in e for e in errs)


def test_validator_catches_forbidden_phrase(tmp_path):
    md = GATE_MD_PATH.read_text(encoding="utf-8") + "\nThis is profitable.\n"
    ok, errs = _validate_obj(tmp_path, _data(), md_text=md)
    assert not ok and any("forbidden phrase" in e for e in errs)


# --- validator is stdlib-only ------------------------------------------- #

def test_validator_is_stdlib_only():
    tree = ast.parse(TOOL_FILE.read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imported.add(n.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported.add(node.module.split(".")[0])
    allowed = {"argparse", "json", "pathlib", "__future__"}
    assert imported <= allowed, f"unexpected imports: {imported - allowed}"


def test_validator_no_network_broker_subprocess_env():
    src = TOOL_FILE.read_text(encoding="utf-8").lower()
    # Match real code usage, not docstring prose ("no subprocess", "env reads").
    for bad in ("import requests", "import socket", "import urllib",
                "import subprocess", "os.environ", "os.getenv",
                ".getenv(", "ccxt", "binance", "dotenv", "httpx"):
        assert bad not in src, f"validator must not reference {bad!r}"


# --- CLI smoke ---------------------------------------------------------- #

def test_cli_validate_returns_zero():
    assert cdrg.main(["validate"]) == 0


def test_cli_show_returns_zero():
    assert cdrg.main(["show"]) == 0


# --- integration: prior validators still pass --------------------------- #

def test_prior_crypto_d1_validators_still_pass():
    for mod in (cmir, cdse, cda, cqf, cdm, cdc, cdpc, cbp):
        ok, errs = mod.validate(_REPO_ROOT)
        assert ok, (mod.__name__, errs)


def test_registry_still_lists_crypto_d1_as_watch():
    ok, errs = scr.validate(_REPO_ROOT)
    assert ok, errs
    lanes = {l["candidate_id"]: l for l in scr.SEED_LANES}
    assert lanes["crypto_d1_protocol"]["lane_status_override"] == "WATCH"
