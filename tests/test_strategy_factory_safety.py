"""Tests for the read-only Strategy Factory Safety Contract v1 validator.

``strategy_factory_safety.build(base)`` loads
``base/configs/strategy_factory_safety.json``, validates it fail-closed, and
returns a result object {valid, safe, blocked_reasons, warnings,
normalized_contract, safety_flags} plus a read-only queue integration. These
tests pin the Step-3 safety contract:

- a well-formed contract is SAFE;
- a missing file / malformed JSON / missing key / forbidden flag true /
  unknown runner|dataset|mode|market => UNSAFE (recorded, never raised);
- the contract forbids execution_authorized and paper/live authorization;
- broker/exchange/order/fetch tokens are screened as forbidden;
- the shipped queue item is allowed for LISTING but is never executable;
- the validator runs no subprocess, no network, imports no runner, and writes
  nothing except the explicit opt-in build report;
- normalized output is deterministic;
- the shipped registry + queue tests still pass (smoke import here).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]
_TOOLS_DIR = _REPO_ROOT / "tools"
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))

import strategy_factory_safety as sfs  # noqa: E402

_SAFETY_REL = "configs/strategy_factory_safety.json"
_QUEUE_REL = "configs/research_queue.json"


def _contract(**overrides) -> dict:
    c = {
        "schema_version": 1,
        "layer": "strategy_factory_safety_v1",
        "research_only": True,
        "safety_flags": {
            "research_only": True,
            "paper_live_authorized": False,
            "broker_path_enabled": False,
            "exchange_path_enabled": False,
            "order_path_enabled": False,
            "fetch_live_data_enabled": False,
            "dataset_mutation_allowed": False,
            "active_strong_promoted": False,
            "bundle_23_started": False,
            "execution_authorized": False,
        },
        "allowed_datasets": ["CRYPTO_D1_SPOT_BTC_ETH_SOL_V001_V002"],
        "allowed_runners": ["tools/crypto_d1_backtest_runner.py"],
        "allowed_modes": ["momentum_confirmation_v1"],
        "allowed_markets": ["crypto"],
        "forbidden_terms": list(sfs.REQUIRED_FORBIDDEN_TERMS),
        "human_approval": {
            "human_approval_required_for_execution": True,
            "human_approval_required_for_paper_live": True,
            "human_approval_required_for_promotion": True,
        },
    }
    c.update(overrides)
    return c


def _queue_item() -> dict:
    return {
        "task_id": "crypto_d1_momentum_n20_deeper_validation_v1",
        "strategy_id": "crypto_d1_momentum_confirmation_v1",
        "strategy_family": "crypto_d1_momentum",
        "market": "crypto",
        "dataset_id": "CRYPTO_D1_SPOT_BTC_ETH_SOL_V001_V002",
        "allowed_runner": "tools/crypto_d1_backtest_runner.py",
        "allowed_mode": "momentum_confirmation_v1",
        "execution_authorized": False,
        "next_action": "Create the N=20 deeper-validation plan.",
        "safety_flags": {
            "research_only": True,
            "paper_live_authorized": False,
            "broker_path_enabled": False,
            "exchange_path_enabled": False,
            "order_path_enabled": False,
            "fetch_live_data_enabled": False,
            "dataset_mutation_allowed": False,
            "active_strong_promoted": False,
            "bundle_23_started": False,
            "execution_authorized": False,
        },
    }


def _write(base: Path, rel: str, obj) -> None:
    p = base / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj) if not isinstance(obj, str) else obj,
                 encoding="utf-8")


def _seed(base: Path, contract: dict) -> None:
    _write(base, _SAFETY_REL, contract)


# --- Test 1: a valid contract is SAFE --------------------------------------

def test_valid_contract_is_safe(tmp_path):
    _seed(tmp_path, _contract())
    r = sfs.build(tmp_path)
    assert r["valid"] is True
    assert r["safe"] is True
    assert r["blocked_reasons"] == []
    assert r["read_only"] is True
    assert r["executes_anything"] is False
    nc = r["normalized_contract"]
    assert nc["allowed_runners"] == ["tools/crypto_d1_backtest_runner.py"]
    assert nc["allowed_markets"] == ["crypto"]


# --- Test 2: missing file fails closed -------------------------------------

def test_missing_safety_file_fails_closed(tmp_path):
    r = sfs.build(tmp_path)  # no file seeded
    assert r["valid"] is False
    assert r["safe"] is False
    assert any("not found" in x for x in r["blocked_reasons"])
    assert r["normalized_contract"] is None


# --- Test 3: malformed JSON fails closed -----------------------------------

def test_malformed_json_fails_closed(tmp_path):
    _write(tmp_path, _SAFETY_REL, "{ not valid json ")
    r = sfs.build(tmp_path)
    assert r["safe"] is False
    assert any("malformed JSON" in x for x in r["blocked_reasons"])


# --- Test 4: missing required key fails closed -----------------------------

@pytest.mark.parametrize("key", [
    "research_only", "safety_flags", "allowed_datasets", "allowed_runners",
    "allowed_modes", "allowed_markets", "forbidden_terms", "human_approval",
])
def test_missing_required_key_fails_closed(tmp_path, key):
    c = _contract()
    del c[key]
    _seed(tmp_path, c)
    r = sfs.build(tmp_path)
    assert r["safe"] is False
    assert any(key in x for x in r["blocked_reasons"])


# --- Test 5: any forbidden flag true fails closed --------------------------

@pytest.mark.parametrize("flag", [
    "paper_live_authorized", "broker_path_enabled", "exchange_path_enabled",
    "order_path_enabled", "fetch_live_data_enabled", "dataset_mutation_allowed",
    "active_strong_promoted", "bundle_23_started", "execution_authorized",
])
def test_forbidden_flag_true_fails_closed(tmp_path, flag):
    c = _contract()
    c["safety_flags"][flag] = True
    _seed(tmp_path, c)
    r = sfs.build(tmp_path)
    assert r["safe"] is False
    assert any(flag in x for x in r["blocked_reasons"])


def test_research_only_false_fails_closed(tmp_path):
    c = _contract(research_only=False)
    _seed(tmp_path, c)
    r = sfs.build(tmp_path)
    assert r["safe"] is False
    assert any("research_only must be true" in x for x in r["blocked_reasons"])


# --- Test 6: unknown runner/dataset/mode/market fails closed ---------------

@pytest.mark.parametrize("key,bad", [
    ("allowed_runners", "tools/live_broker_runner.py"),
    ("allowed_datasets", "SOME_OTHER_DATASET_V001"),
    ("allowed_modes", "live_execution_v9"),
    ("allowed_markets", "forex"),
])
def test_unknown_allowlist_entry_fails_closed(tmp_path, key, bad):
    c = _contract()
    c[key] = c[key] + [bad]
    _seed(tmp_path, c)
    r = sfs.build(tmp_path)
    assert r["safe"] is False
    assert any("not allowed by contract" in x for x in r["blocked_reasons"])


# --- Test 7: execution + paper/live are blocked at the contract level ------

def test_contract_blocks_execution_authorized(tmp_path):
    c = _contract()
    c["safety_flags"]["execution_authorized"] = True
    _seed(tmp_path, c)
    r = sfs.build(tmp_path)
    assert r["safe"] is False
    assert any("execution_authorized" in x for x in r["blocked_reasons"])


def test_contract_blocks_paper_live(tmp_path):
    c = _contract()
    c["safety_flags"]["paper_live_authorized"] = True
    _seed(tmp_path, c)
    r = sfs.build(tmp_path)
    assert r["safe"] is False
    assert any("paper_live_authorized" in x for x in r["blocked_reasons"])


# --- Test 8: broker/exchange/order/fetch paths are screened as forbidden ----

@pytest.mark.parametrize("term", ["broker", "exchange", "order", "fetch",
                                  "live", "kraken", "ACTIVE", "STRONG"])
def test_forbidden_terms_are_screened(term):
    terms = list(sfs.REQUIRED_FORBIDDEN_TERMS)
    assert sfs.screen_text(f"tools/{term}_path_runner.py", terms) != []


def test_task_with_forbidden_token_is_blocked():
    nc = sfs.validate_contract(_contract())["normalized_contract"]
    bad = _queue_item()
    bad["strategy_id"] = "crypto_d1_live_order_broker_strategy"
    res = sfs.validate_task_against_contract(bad, nc)
    assert res["contract_conformant"] is False
    assert res["allowed_for_listing"] is False
    assert res["executable"] is False
    assert any("forbidden term" in x for x in res["blocked_reasons"])


def test_task_with_unlisted_runner_is_blocked():
    nc = sfs.validate_contract(_contract())["normalized_contract"]
    bad = _queue_item()
    bad["allowed_runner"] = "tools/broker_exchange_order_runner.py"
    res = sfs.validate_task_against_contract(bad, nc)
    assert res["contract_conformant"] is False
    assert any("runner not allowed" in x for x in res["blocked_reasons"])


# --- Test 9: queue item is allowed for listing but NOT executable ----------

def test_queue_item_allowed_for_listing_but_not_executable(tmp_path):
    _seed(tmp_path, _contract())
    _write(tmp_path, _QUEUE_REL, {"items": [_queue_item()]})
    r = sfs.build(tmp_path)
    qi = r["queue_integration"]
    assert qi["checked"] is True
    e = qi["items"][0]
    assert e["task_id"] == "crypto_d1_momentum_n20_deeper_validation_v1"
    assert e["contract_conformant"] is True
    assert e["allowed_for_listing"] is True
    assert e["executable"] is False


# --- Test 10: read-only — no subprocess/network/runner import/stray writes --

def test_no_subprocess_no_runner_import_no_writes(tmp_path, monkeypatch):
    _seed(tmp_path, _contract())
    _write(tmp_path, _QUEUE_REL, {"items": [_queue_item()]})

    def _boom(*a, **k):  # pragma: no cover - must never be called
        raise AssertionError("safety validator must not run subprocesses")

    monkeypatch.setattr(subprocess, "run", _boom)
    monkeypatch.setattr(subprocess, "Popen", _boom)

    before = {p for p in tmp_path.rglob("*") if p.is_file()}
    r = sfs.build(tmp_path)
    after = {p for p in tmp_path.rglob("*") if p.is_file()}
    assert before == after
    assert not (tmp_path / "reports" / "strategy_factory_safety_v1_build").exists()
    assert r["safety_flags"]["execution_authorized"] is False
    assert "crypto_d1_backtest_runner" not in sys.modules


# --- Test 11: deterministic normalized output ------------------------------

def test_normalized_output_is_deterministic(tmp_path):
    # allowlists in a scrambled order must normalize identically
    c = _contract()
    c["forbidden_terms"] = list(reversed(c["forbidden_terms"]))
    _seed(tmp_path, c)
    r1 = sfs.build(tmp_path)
    r2 = sfs.build(tmp_path)
    assert sfs.to_stable_json(r1) == sfs.to_stable_json(r2)
    assert r1["normalized_contract"]["forbidden_terms"] == \
        sorted(set(sfs.REQUIRED_FORBIDDEN_TERMS))


# --- Test 12: opt-in write goes ONLY to the allowed build folder -----------

def test_write_build_report_confined_to_build_folder(tmp_path):
    _seed(tmp_path, _contract())
    r = sfs.build(tmp_path)
    written = sfs.write_build_report(tmp_path, r)
    assert written == [
        "reports/strategy_factory_safety_v1_build/safety.json",
        "reports/strategy_factory_safety_v1_build/safety.md"]
    out_dir = tmp_path / "reports" / "strategy_factory_safety_v1_build"
    assert (out_dir / "safety.json").is_file()
    assert (out_dir / "safety.md").is_file()
    assert not (tmp_path / "data").exists()
    assert not (tmp_path / "templates").exists()


# --- Test 13: the SHIPPED contract is SAFE and the shipped queue conforms ---

def test_shipped_contract_is_safe_and_queue_conforms():
    r = sfs.build(_REPO_ROOT)
    assert r["safe"] is True, r["blocked_reasons"]
    qi = r["queue_integration"]
    assert qi["checked"] is True
    by_id = {e["task_id"]: e for e in qi["items"]}
    task = by_id.get("crypto_d1_momentum_n20_deeper_validation_v1")
    assert task is not None
    assert task["contract_conformant"] is True
    assert task["allowed_for_listing"] is True
    assert task["executable"] is False
