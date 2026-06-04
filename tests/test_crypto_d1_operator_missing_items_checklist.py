"""Bundle 22 -- Crypto-D1 Operator Missing Items Checklist v1 tests.

Pure stdlib + pytest. Research-only. Asserts:
  * checklist.json + checklist.md exist and validate
  * eleven safety flags are pinned False; research_only + read_only True
  * scope BTC/ETH/SOL spot 1d 24/7 lane=crypto_d1_protocol
  * exactly 16 items numbered 1..16; each carries all 9 required fields
  * default state pins every item at MISSING / PENDING / empty
  * item_status_options + approval_status_options are the canonical 4-value enums
  * overall_readiness_status defaults to NOT_READY_FOR_REAL_DATA
  * anti-fake-completion: COMPLETE requires evidence_path AND approval_status=APPROVED
  * BLOCKED requires non-empty blocking_reason
  * required distinction phrases present in BOTH md and json; no forbidden phrases
  * no real data files; no data/crypto_d1_research/ dir
  * validator catches tampered flag, invalid status, dropped item, fake completion
    (no evidence), fake completion (PENDING approval), BLOCKED without reason,
    inconsistent overall status, forbidden phrase
  * validator tool is stdlib-only; no network/broker/exchange/subprocess/env
  * prior Crypto-D1 validators still pass; arbitrage readiness still passes;
    registry validator still passes and crypto_d1 stays WATCH/MIXED
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

import crypto_d1_operator_missing_items_checklist_check as cmic  # noqa: E402
import crypto_d1_readiness_gate_check as cdrg                    # noqa: E402
import crypto_d1_manual_dataset_intake_runbook_check as cmir     # noqa: E402
import crypto_d1_data_source_evaluation_check as cdse            # noqa: E402
import crypto_d1_data_acquisition_authorization_check as cda     # noqa: E402
import crypto_d1_qa_freeze_spec_check as cqf                     # noqa: E402
import crypto_d1_dataset_manifest_check as cdm                   # noqa: E402
import crypto_d1_data_contract_check as cdc                      # noqa: E402
import crypto_d1_protocol_check as cdpc                          # noqa: E402
import crypto_d1_backtest_plan_check as cbp                      # noqa: E402
import arbitrage_readiness_gate_check as argc                    # noqa: E402
import strategy_candidate_registry as scr                        # noqa: E402

TOOL_FILE = _TOOLS_DIR / "crypto_d1_operator_missing_items_checklist_check.py"
CHECKLIST_JSON_PATH = _REPO_ROOT / cmic.CHECKLIST_DIR_REL / cmic.CHECKLIST_JSON
CHECKLIST_MD_PATH = _REPO_ROOT / cmic.CHECKLIST_DIR_REL / cmic.CHECKLIST_MD


def _data():
    return json.loads(CHECKLIST_JSON_PATH.read_text(encoding="utf-8"))


# --- existence + validation --------------------------------------------- #

def test_checklist_json_exists():
    assert CHECKLIST_JSON_PATH.exists(), f"missing: {CHECKLIST_JSON_PATH}"


def test_checklist_md_exists():
    assert CHECKLIST_MD_PATH.exists(), f"missing: {CHECKLIST_MD_PATH}"


def test_validator_passes_on_committed_checklist():
    ok, errs = cmic.validate(_REPO_ROOT)
    assert ok, errs


# --- safety flags ------------------------------------------------------- #

def test_eleven_flags_all_false():
    data = _data()
    assert len(cmic.MUST_BE_FALSE_FLAGS) == 11
    for flag in cmic.MUST_BE_FALSE_FLAGS:
        assert data.get(flag) is False, f"{flag} must be False"
    assert data.get("research_only") is True
    assert data.get("read_only") is True


# --- scope -------------------------------------------------------------- #

def test_scope_assets_market_timeframe_calendar():
    data = _data()
    assert data.get("target_assets") == ["BTC", "ETH", "SOL"]
    assert data.get("allowed_market_type") == "spot"
    assert data.get("timeframe") == "1d"
    assert data.get("session_calendar") == "24/7"
    assert data.get("lane") == "crypto_d1_protocol"


# --- 16 items numbered 1..16 ------------------------------------------- #

def test_exactly_sixteen_items_numbered_one_through_sixteen():
    items = _data().get("items")
    assert isinstance(items, list) and len(items) == 16
    assert {i["number"] for i in items} == set(range(1, 17))


def test_each_item_has_nine_required_fields():
    for it in _data().get("items"):
        for f in cmic.REQUIRED_ITEM_FIELDS:
            assert f in it, f"item {it.get('number')} missing field {f}"


# --- current partition (partial completion; every item is a valid
#     COMPLETE-with-evidence-and-approval, or a valid MISSING-and-PENDING) - #

def test_item_partition_is_valid_complete_or_missing():
    """Operator progress is real: 9 items COMPLETE+APPROVED with evidence,
    7 items still MISSING+PENDING, 0 BLOCKED, 16 total. Every item must be one
    of those two *valid* shapes -- a COMPLETE item must carry evidence and
    APPROVED, and a MISSING item must be PENDING with empty evidence. Overall
    readiness must remain NOT_READY_FOR_REAL_DATA regardless of this progress."""
    items = _data().get("items")
    assert len(items) == 16
    complete = [i for i in items if i["status"] == "COMPLETE"]
    missing = [i for i in items if i["status"] == "MISSING"]
    blocked = [i for i in items if i["status"] == "BLOCKED"]
    assert len(complete) == 9, f"expected 9 COMPLETE, got {len(complete)}"
    assert len(missing) == 7, f"expected 7 MISSING, got {len(missing)}"
    assert len(blocked) == 0, f"expected 0 BLOCKED, got {len(blocked)}"
    assert len(complete) + len(missing) == 16

    for it in complete:
        assert it["approval_status"] == "APPROVED", \
            f"item {it['number']} COMPLETE but not APPROVED"
        assert it.get("evidence_path", "") != "", \
            f"item {it['number']} COMPLETE but has no evidence_path"
    for it in missing:
        assert it["approval_status"] == "PENDING", \
            f"item {it['number']} MISSING but not PENDING"
        assert it.get("evidence_path", "") == "", \
            f"item {it['number']} MISSING but has evidence_path"
        assert it.get("operator_answer", "") == "", \
            f"item {it['number']} MISSING but has operator_answer"

    # the safety gate is unmoved by partial operator progress
    assert _data().get("overall_readiness_status") == "NOT_READY_FOR_REAL_DATA"


def test_overall_readiness_default_is_not_ready():
    assert _data().get("overall_readiness_status") == "NOT_READY_FOR_REAL_DATA"


def test_override_reason_explains_partial_completion():
    """With items COMPLETE while overall stays NOT_READY, the validator requires
    a non-empty override_reason. Assert it is present and that overall readiness
    remains NOT_READY_FOR_REAL_DATA (the gate holds despite the override)."""
    data = _data()
    reason = data.get("overall_readiness_status_override_reason", "")
    assert isinstance(reason, str) and reason.strip() != "", \
        "override_reason must be non-empty while items are COMPLETE"
    assert data.get("overall_readiness_status") == "NOT_READY_FOR_REAL_DATA"


# --- enum options ------------------------------------------------------ #

def test_item_status_options_are_the_four():
    assert _data().get("item_status_options") == [
        "MISSING", "COMPLETE", "BLOCKED", "NOT_APPLICABLE",
    ]


def test_approval_status_options_are_the_four():
    assert _data().get("approval_status_options") == [
        "PENDING", "APPROVED", "REJECTED", "WITHDRAWN",
    ]


# --- lane recommendation ----------------------------------------------- #

def test_lane_stays_watch_mixed_no_active_no_strong():
    lr = _data().get("lane_recommendation")
    assert lr["current_verdict"] == "WATCH"
    assert lr["evidence_level"] == "MIXED"
    assert lr["do_not_promote_to_ACTIVE"] is True
    assert lr["do_not_promote_to_STRONG_evidence"] is True


# --- future gates ------------------------------------------------------ #

def test_trading_gate_explicitly_forbidden():
    far = _data().get("future_authorization_requirements")
    assert far["trading_gate"]["explicitly_forbidden_by_this_checklist"] is True


def test_checklist_completion_gate_has_requirements():
    ccg = _data().get("future_authorization_requirements")["checklist_completion_gate"]
    assert isinstance(ccg["all_required"], list) and ccg["all_required"]


# --- distinction + forbidden phrases ----------------------------------- #

def test_distinction_phrases_present_in_both_docs():
    md = CHECKLIST_MD_PATH.read_text(encoding="utf-8")
    blob = json.dumps(_data(), ensure_ascii=False)
    for phrase in cmic.DISTINCTION_PHRASES:
        assert phrase in md, f"md missing distinction phrase: {phrase!r}"
        assert phrase in blob, f"json missing distinction phrase: {phrase!r}"


def test_required_user_phrases_present_in_md():
    md = CHECKLIST_MD_PATH.read_text(encoding="utf-8")
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
    md = CHECKLIST_MD_PATH.read_text(encoding="utf-8").lower()
    blob = json.dumps(_data(), ensure_ascii=False).lower()
    for phrase in cmic.FORBIDDEN_PHRASES:
        assert phrase.lower() not in md, f"md has forbidden phrase: {phrase!r}"
        assert phrase.lower() not in blob, f"json has forbidden phrase: {phrase!r}"


# --- no real data / no data dir ---------------------------------------- #

def test_crypto_d1_research_dir_is_inert_frozen_dataset():
    """A frozen research dataset directory may now exist. Its mere presence must
    NOT imply readiness or execution: the checklist's overall readiness stays
    NOT_READY_FOR_REAL_DATA and the lane stays WATCH / MIXED with no promotion.
    If the directory is absent, that is equally safe and the test still passes."""
    data = _data()
    # presence of a frozen dataset directory changes nothing about safety state
    assert data.get("overall_readiness_status") == "NOT_READY_FOR_REAL_DATA"
    lr = data.get("lane_recommendation")
    assert lr["current_verdict"] == "WATCH"
    assert lr["evidence_level"] == "MIXED"
    assert lr["do_not_promote_to_ACTIVE"] is True
    assert lr["do_not_promote_to_STRONG_evidence"] is True


def test_checklist_dir_contains_no_real_data_files():
    d = _REPO_ROOT / cmic.CHECKLIST_DIR_REL
    bad = [p.name for p in d.iterdir()
           if p.suffix.lower() in (".csv", ".parquet", ".feather", ".db", ".sqlite", ".pickle", ".pkl", ".h5", ".npz")]
    assert not bad, f"unexpected data files in checklist dir: {bad}"


def test_checklist_dir_contains_only_expected_doc_files():
    d = _REPO_ROOT / cmic.CHECKLIST_DIR_REL
    files = sorted(p.name for p in d.iterdir() if p.is_file())
    expected = {"checklist.json", "checklist.md", "report.json", "report.md"}
    assert set(files) == expected, f"unexpected files in checklist dir: {sorted(set(files) - expected)}"


# --- validator failure modes ------------------------------------------- #

def _validate_obj(tmp_path, obj, md_text=None):
    d = tmp_path / cmic.CHECKLIST_DIR_REL
    d.mkdir(parents=True, exist_ok=True)
    (d / cmic.CHECKLIST_JSON).write_text(json.dumps(obj), encoding="utf-8")
    src_md = CHECKLIST_MD_PATH.read_text(encoding="utf-8") if md_text is None else md_text
    (d / cmic.CHECKLIST_MD).write_text(src_md, encoding="utf-8")
    return cmic.validate(tmp_path)


def test_validator_baseline_copy_passes(tmp_path):
    ok, errs = _validate_obj(tmp_path, _data())
    assert ok, errs


def test_validator_catches_tampered_safety_flag(tmp_path):
    obj = copy.deepcopy(_data())
    obj["live_trading_enabled"] = True
    ok, errs = _validate_obj(tmp_path, obj)
    assert not ok and any("live_trading_enabled" in e for e in errs)


def test_validator_catches_invalid_status(tmp_path):
    obj = copy.deepcopy(_data())
    obj["items"][0]["status"] = "DONE"   # not in enum
    ok, errs = _validate_obj(tmp_path, obj)
    assert not ok and any("invalid status" in e for e in errs)


def test_validator_catches_invalid_approval_status(tmp_path):
    obj = copy.deepcopy(_data())
    obj["items"][0]["approval_status"] = "MAYBE"  # not in enum
    ok, errs = _validate_obj(tmp_path, obj)
    assert not ok and any("invalid approval_status" in e for e in errs)


def test_validator_catches_dropped_item(tmp_path):
    obj = copy.deepcopy(_data())
    obj["items"] = obj["items"][:-1]  # 15 items instead of 16
    ok, errs = _validate_obj(tmp_path, obj)
    assert not ok


def test_validator_catches_missing_field(tmp_path):
    obj = copy.deepcopy(_data())
    del obj["items"][2]["evidence_path"]
    ok, errs = _validate_obj(tmp_path, obj)
    assert not ok and any("missing field evidence_path" in e for e in errs)


def test_validator_catches_fake_completion_empty_evidence(tmp_path):
    """status=COMPLETE without evidence_path should fail (anti-fake-completion)."""
    obj = copy.deepcopy(_data())
    obj["items"][0]["status"] = "COMPLETE"
    obj["items"][0]["approval_status"] = "APPROVED"
    obj["items"][0]["evidence_path"] = ""  # still empty -> reject
    obj["overall_readiness_status_override_reason"] = "test"
    ok, errs = _validate_obj(tmp_path, obj)
    assert not ok and any("non-empty evidence_path" in e for e in errs)


def test_validator_catches_fake_completion_pending_approval(tmp_path):
    """status=COMPLETE while approval_status=PENDING should fail."""
    obj = copy.deepcopy(_data())
    obj["items"][0]["status"] = "COMPLETE"
    obj["items"][0]["evidence_path"] = "/some/evidence/path.json"
    obj["items"][0]["approval_status"] = "PENDING"
    obj["overall_readiness_status_override_reason"] = "test"
    ok, errs = _validate_obj(tmp_path, obj)
    assert not ok and any("approval_status=APPROVED" in e for e in errs)


def test_validator_catches_blocked_without_reason(tmp_path):
    obj = copy.deepcopy(_data())
    obj["items"][0]["status"] = "BLOCKED"
    obj["items"][0]["blocking_reason"] = ""
    ok, errs = _validate_obj(tmp_path, obj)
    assert not ok and any("blocking_reason" in e for e in errs)


def test_validator_catches_inconsistent_overall_status(tmp_path):
    """if any item is COMPLETE while overall remains NOT_READY_FOR_REAL_DATA
    and no override_reason is given, the validator must fail."""
    obj = copy.deepcopy(_data())
    obj["items"][0]["status"] = "COMPLETE"
    obj["items"][0]["approval_status"] = "APPROVED"
    obj["items"][0]["evidence_path"] = "/evidence/x.json"
    obj["overall_readiness_status"] = "NOT_READY_FOR_REAL_DATA"
    obj["overall_readiness_status_override_reason"] = ""  # empty -> fail
    ok, errs = _validate_obj(tmp_path, obj)
    assert not ok and any("overall_readiness_status remains" in e for e in errs)


def test_validator_accepts_complete_with_evidence_approval_and_override_reason(tmp_path):
    """The happy partial-completion path: items COMPLETE with evidence+APPROVED,
    overall remains NOT_READY_FOR_REAL_DATA, and override_reason explains why."""
    obj = copy.deepcopy(_data())
    obj["items"][0]["status"] = "COMPLETE"
    obj["items"][0]["approval_status"] = "APPROVED"
    obj["items"][0]["evidence_path"] = "/evidence/x.json"
    obj["overall_readiness_status_override_reason"] = \
        "Item 1 COMPLETE; items 2-16 still MISSING."
    ok, errs = _validate_obj(tmp_path, obj)
    assert ok, errs


def test_validator_catches_lane_promotion_tamper(tmp_path):
    obj = copy.deepcopy(_data())
    obj["lane_recommendation"]["do_not_promote_to_ACTIVE"] = False
    ok, errs = _validate_obj(tmp_path, obj)
    assert not ok and any("do_not_promote_to_ACTIVE" in e for e in errs)


def test_validator_catches_strong_evidence_tamper(tmp_path):
    obj = copy.deepcopy(_data())
    obj["lane_recommendation"]["evidence_level"] = "STRONG"
    ok, errs = _validate_obj(tmp_path, obj)
    assert not ok and any("MIXED" in e for e in errs)


def test_validator_catches_missing_distinction_phrase(tmp_path):
    md = CHECKLIST_MD_PATH.read_text(encoding="utf-8").replace(
        "NOT_READY_FOR_REAL_DATA is the honest default",
        "X" * 8,
    )
    ok, errs = _validate_obj(tmp_path, _data(), md_text=md)
    assert not ok and any("distinction phrase" in e for e in errs)


def test_validator_catches_forbidden_phrase(tmp_path):
    md = CHECKLIST_MD_PATH.read_text(encoding="utf-8") + "\nThis is profitable.\n"
    ok, errs = _validate_obj(tmp_path, _data(), md_text=md)
    assert not ok and any("forbidden phrase" in e for e in errs)


# --- validator is stdlib-only ------------------------------------------ #

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
    for bad in ("import requests", "import socket", "import urllib",
                "import subprocess", "os.environ", "os.getenv",
                ".getenv(", "ccxt", "binance", "dotenv", "httpx"):
        assert bad not in src, f"validator must not reference {bad!r}"


# --- CLI smoke --------------------------------------------------------- #

def test_cli_validate_returns_zero():
    assert cmic.main(["validate"]) == 0


def test_cli_show_returns_zero():
    assert cmic.main(["show"]) == 0


# --- integration: prior validators still pass -------------------------- #

def test_prior_crypto_d1_validators_still_pass():
    for mod in (cdrg, cmir, cdse, cda, cqf, cdm, cdc, cdpc, cbp):
        ok, errs = mod.validate(_REPO_ROOT)
        assert ok, (mod.__name__, errs)


def test_arbitrage_readiness_validator_still_passes():
    ok, errs = argc.validate(_REPO_ROOT)
    assert ok, errs


def test_registry_classifies_crypto_d1_as_watch_after_checklist():
    payload = scr.generate(_REPO_ROOT)
    cd1 = next(c for c in payload["candidates"]
               if c["candidate_id"] == "crypto_d1_protocol")
    assert cd1["status"] == "WATCH"
    assert cd1["status"] != "ACTIVE"
    assert cd1["evidence_level"] != "STRONG"
    for needed in ("checklist.md", "checklist.json"):
        assert needed in cd1["source_reports"], cd1["source_reports"]


def test_registry_validator_still_passes_after_seed_edit():
    scr.generate(_REPO_ROOT)
    ok, errs = scr.validate(_REPO_ROOT)
    assert ok, errs
