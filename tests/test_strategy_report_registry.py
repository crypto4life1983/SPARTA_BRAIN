"""Tests for the read-only Strategy Report Registry v1 scanner.

`strategy_report_registry.build_registry(base)` scans committed plan -> result
-> decision-memo artifacts under ``base/reports`` and returns a normalized,
deterministic registry. These tests pin the Step-1 safety contract:

- a plan + executed result resolves to stage EXECUTED with verdict/run_id;
- the verdict stays WATCH (the lane never promotes);
- a tampered ACTIVE/STRONG/PASS verdict is clamped to WATCH and flagged unsafe;
- a missing result report fails closed to PLAN_ONLY with a warning (no crash);
- an unknown/empty verdict becomes UNKNOWN, never PASS;
- output ordering and JSON bytes are deterministic;
- the build is read-only: no subprocess, no network, and nothing is written
  except the explicit opt-in build report under the single allowed folder.
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

import strategy_report_registry as srr  # noqa: E402

_PLAN_REL = "reports/crypto_d1_momentum_confirmation_v1_plan/report.json"
_RESULT_REL = ("reports/crypto_d1_momentum_confirmation_v1/"
               "CRYPTO_D1_SPOT_BTC_ETH_SOL_V001_V002/"
               "crypto_d1_momentum_confirmation_report.json")
_MEMO_REL = ("reports/crypto_d1_momentum_confirmation_v1/"
             "CRYPTO_D1_SPOT_BTC_ETH_SOL_V001_V002/decision_memo.md")


def _write(base: Path, rel: str, text: str) -> None:
    p = base / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def _write_json(base: Path, rel: str, obj) -> None:
    _write(base, rel, json.dumps(obj))


def _seed_plan(base: Path) -> None:
    _write_json(base, _PLAN_REL, {
        "plan_id": "crypto_d1_momentum_confirmation_v1_plan",
        "plan_version": "v1",
        "plan_date": "2026-06-03",
        "status": "PLAN_ONLY_NOT_EXECUTED",
        "lane_status_unchanged": "WATCH / MIXED",
        "frozen_inputs_must_remain_unchanged": {
            "dataset": "data/crypto_d1_research/"
                       "CRYPTO_D1_SPOT_BTC_ETH_SOL_V001/V002"},
        "runner_and_reporting_design": {
            "proposed_config_name": "momentum_confirmation_v1"},
    })


def _seed_result(base: Path, verdict: str = "WATCH",
                 run_id: str = "2a3be425522a04ec") -> None:
    _write_json(base, _RESULT_REL, {
        "config_mode": "momentum_confirmation_v1",
        "pass_watch_fail_status": verdict,
        "run_id": run_id,
        "generated_at": "2026-06-03T20:47:44Z",
        "input_data_dir": "data/crypto_d1_research/"
                          "CRYPTO_D1_SPOT_BTC_ETH_SOL_V001/V002",
    })


def _confirm_entry(reg: dict) -> dict:
    by_id = {e["strategy_id"]: e for e in reg["strategies"]}
    return by_id["crypto_d1_momentum_confirmation_v1"]


# --- Test 1: plan + executed result resolves to EXECUTED -------------------

def test_scans_plan_and_executed_report(tmp_path):
    _seed_plan(tmp_path)
    _seed_result(tmp_path)
    reg = srr.build_registry(tmp_path)

    assert reg["read_only"] is True
    assert reg["schema_version"] == srr.SCHEMA_VERSION
    e = _confirm_entry(reg)
    assert e["stage"] == "EXECUTED"
    assert e["status"] == "WATCH / MIXED"
    assert e["verdict"] == "WATCH"
    assert e["run_id"] == "2a3be425522a04ec"
    assert e["runner_mode"] == "momentum_confirmation_v1"
    assert e["strategy_family"] == "momentum_confirmation"
    assert e["market"] == "CRYPTO_D1_SPOT_BTC_ETH_SOL"
    assert e["dataset_id"] == "CRYPTO_D1_SPOT_BTC_ETH_SOL_V001/V002"
    assert e["report_path"].endswith(
        "crypto_d1_momentum_confirmation_report.json")
    assert e["plan_path"].endswith("report.json")
    assert e["decision_memo_path"] is None
    # deterministic timestamps from artifacts (no wall clock)
    assert e["created_at"] == "2026-06-03"
    assert e["updated_at"] == "2026-06-03T20:47:44Z"
    assert "Operator review" in e["next_action"]


# --- Test 2: a decision memo advances the stage ----------------------------

def test_decision_memo_advances_stage(tmp_path):
    _seed_plan(tmp_path)
    _seed_result(tmp_path)
    _write(tmp_path, _MEMO_REL, "# Decision: remain WATCH\n")
    e = _confirm_entry(srr.build_registry(tmp_path))
    assert e["stage"] == "DECISION_RECORDED"
    assert e["decision_memo_path"].endswith("decision_memo.md")
    assert "next checkpoint" in e["next_action"]


# --- Test 3: verdict stays WATCH (lane never promotes) ---------------------

def test_verdict_ceiling_is_watch(tmp_path):
    _seed_plan(tmp_path)
    _seed_result(tmp_path, verdict="WATCH")
    e = _confirm_entry(srr.build_registry(tmp_path))
    assert e["verdict"] == "WATCH"
    assert e["safety_flags"]["active_strong_promoted"] is False


# --- Test 4: ACTIVE/STRONG/PASS are clamped + flagged unsafe ----------------

@pytest.mark.parametrize("forbidden", ["ACTIVE", "STRONG", "PASS"])
def test_forbidden_verdicts_clamped_and_flagged(tmp_path, forbidden):
    _seed_plan(tmp_path)
    _seed_result(tmp_path, verdict=forbidden)
    reg = srr.build_registry(tmp_path)
    e = _confirm_entry(reg)
    assert e["verdict"] == "WATCH"
    assert e["verdict"] != forbidden
    assert e["verdict_clamped_from"] == forbidden
    assert e["unsafe_verdict_flagged"] is True
    assert any(forbidden in w and "clamped" in w for w in reg["warnings"])


# --- Test 5: missing result report fails closed ----------------------------

def test_missing_result_fails_closed(tmp_path):
    _seed_plan(tmp_path)  # plan only; NO result report
    reg = srr.build_registry(tmp_path)
    e = _confirm_entry(reg)
    assert e["stage"] == "PLAN_ONLY"
    assert e["verdict"] is None
    assert e["run_id"] is None
    assert e["report_path"] is None
    assert any("no result dir" in w for w in reg["warnings"])
    assert "Implement the runner" in e["next_action"]


def test_corrupt_result_json_fails_closed(tmp_path):
    _seed_plan(tmp_path)
    _write(tmp_path, _RESULT_REL, "{ this is not valid json ")
    reg = srr.build_registry(tmp_path)
    e = _confirm_entry(reg)
    # unreadable result => stays plan-only, never raises
    assert e["stage"] == "PLAN_ONLY"
    assert any("unreadable" in w for w in reg["warnings"])


def test_no_reports_dir_is_empty_not_crash(tmp_path):
    reg = srr.build_registry(tmp_path)
    assert reg["strategy_count"] == 0
    assert reg["strategies"] == []
    assert any("no reports/ directory" in w for w in reg["warnings"])


# --- Test 6: unknown/empty verdict becomes UNKNOWN, never PASS --------------

def test_unknown_verdict_becomes_unknown(tmp_path):
    _seed_plan(tmp_path)
    _seed_result(tmp_path, verdict="")  # empty verdict in an executed report
    e = _confirm_entry(srr.build_registry(tmp_path))
    assert e["stage"] == "EXECUTED"
    assert e["verdict"] == "UNKNOWN"
    assert e["verdict"] != "PASS"


# --- Test 7: deterministic ordering and stable JSON ------------------------

def test_output_is_deterministic(tmp_path):
    # Seed a second plan so ordering is observable.
    _seed_plan(tmp_path)
    _seed_result(tmp_path)
    _write_json(tmp_path, "reports/crypto_d1_baseline_backtest_v1_plan/report.json", {
        "plan_id": "crypto_d1_baseline_backtest_v1_plan",
        "plan_date": "2026-01-01",
        "lane_status_unchanged": "WATCH / MIXED"})

    reg1 = srr.build_registry(tmp_path)
    reg2 = srr.build_registry(tmp_path)
    # stable strategy ordering (sorted by strategy_id)
    ids = [e["strategy_id"] for e in reg1["strategies"]]
    assert ids == sorted(ids)
    assert ids == ["crypto_d1_baseline_backtest_v1",
                   "crypto_d1_momentum_confirmation_v1"]
    # byte-identical JSON across repeated builds (no wall-clock drift)
    assert srr.to_stable_json(reg1) == srr.to_stable_json(reg2)


# --- Test 8: read-only — no subprocess/network and no stray writes ----------

def test_build_writes_nothing_and_runs_no_subprocess(tmp_path, monkeypatch):
    _seed_plan(tmp_path)
    _seed_result(tmp_path)

    def _boom(*a, **k):  # pragma: no cover - must never be called
        raise AssertionError("registry scan must not run subprocesses")

    monkeypatch.setattr(subprocess, "run", _boom)
    monkeypatch.setattr(subprocess, "Popen", _boom)

    before = {p for p in tmp_path.rglob("*") if p.is_file()}
    reg = srr.build_registry(tmp_path)
    after = {p for p in tmp_path.rglob("*") if p.is_file()}
    # a pure read must not create or delete any file
    assert before == after
    # the build folder must not be materialized by a read-only scan
    assert not (tmp_path / "reports" / "strategy_factory_registry_v1_build"
                ).exists()
    assert reg["safety_flags"] == {
        "research_only": True,
        "paper_live_authorized": False,
        "broker_path_enabled": False,
        "exchange_path_enabled": False,
        "order_path_enabled": False,
        "active_strong_promoted": False,
        "bundle_23_started": False,
        "dataset_mutation_allowed": False,
    }


# --- Test 9: opt-in write goes ONLY to the allowed build folder ------------

def test_write_build_report_confined_to_build_folder(tmp_path):
    _seed_plan(tmp_path)
    _seed_result(tmp_path)
    reg = srr.build_registry(tmp_path)

    written = srr.write_build_report(tmp_path, reg)
    assert written == [
        "reports/strategy_factory_registry_v1_build/registry.json",
        "reports/strategy_factory_registry_v1_build/registry.md"]
    out_dir = tmp_path / "reports" / "strategy_factory_registry_v1_build"
    assert (out_dir / "registry.json").is_file()
    assert (out_dir / "registry.md").is_file()
    # nothing was written under data/ or any dashboard/template path
    assert not (tmp_path / "data").exists()
    assert not (tmp_path / "templates").exists()
    # the written JSON is the stable serialization
    assert (out_dir / "registry.json").read_text(encoding="utf-8") == \
        srr.to_stable_json(reg)
