"""Tests for the read-only DRY-RUN Strategy Factory Orchestrator v1.

``strategy_factory_orchestrator.build_dry_run_plan(base)`` joins the three
shipped read-only layers — registry (Step 1), queue (Step 2), safety contract
(Step 3) — into a deterministic "what would run / what is blocked / why" plan.
These tests pin the Step-4 safety contract:

- the dry-run loads all three layers and lists the known Crypto-D1 task;
- the task joins to the registry's EXECUTED / WATCH entry;
- ``executable`` is ALWAYS false and no real command is ever emitted;
- a missing or unsafe safety contract halts execution-readiness for everything;
- an unknown strategy_id, an execution_authorized=true item, and a forbidden
  broker/order/fetch/live/paper item are each blocked;
- the orchestrator runs no subprocess, no network, and imports no runner;
- output ordering is deterministic and the writer is confined to its folder.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_TOOLS_DIR = _REPO_ROOT / "tools"
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))

import strategy_factory_orchestrator as sfo  # noqa: E402

_PLAN_REL = "reports/crypto_d1_momentum_confirmation_v1_plan/report.json"
_RESULT_REL = ("reports/crypto_d1_momentum_confirmation_v1/"
               "CRYPTO_D1_SPOT_BTC_ETH_SOL_V001_V002/"
               "crypto_d1_momentum_confirmation_report.json")
_QUEUE_REL = "configs/research_queue.json"
_SAFETY_REL = "configs/strategy_factory_safety.json"

_TASK_ID = "crypto_d1_momentum_n20_deeper_validation_v1"
_STRATEGY_ID = "crypto_d1_momentum_confirmation_v1"


def _write(base: Path, rel: str, obj) -> None:
    p = base / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj) if not isinstance(obj, str) else obj,
                 encoding="utf-8")


def _seed_registry(base: Path, verdict: str = "WATCH") -> None:
    _write(base, _PLAN_REL, {
        "plan_id": "crypto_d1_momentum_confirmation_v1_plan",
        "plan_date": "2026-06-03",
        "lane_status_unchanged": "WATCH / MIXED",
        "frozen_inputs_must_remain_unchanged": {
            "dataset": "data/crypto_d1_research/"
                       "CRYPTO_D1_SPOT_BTC_ETH_SOL_V001/V002"},
        "runner_and_reporting_design": {
            "proposed_config_name": "momentum_confirmation_v1"},
    })
    _write(base, _RESULT_REL, {
        "config_mode": "momentum_confirmation_v1",
        "pass_watch_fail_status": verdict,
        "run_id": "2a3be425522a04ec",
        "generated_at": "2026-06-03T20:47:44Z",
        "input_data_dir": "data/crypto_d1_research/"
                          "CRYPTO_D1_SPOT_BTC_ETH_SOL_V001/V002",
    })


def _flags(**overrides) -> dict:
    base = {
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
    }
    base.update(overrides)
    return base


def _queue_item(**overrides) -> dict:
    item = {
        "task_id": _TASK_ID,
        "strategy_id": _STRATEGY_ID,
        "strategy_family": "crypto_d1_momentum",
        "market": "crypto",
        "dataset_id": "CRYPTO_D1_SPOT_BTC_ETH_SOL_V001_V002",
        "allowed_runner": "tools/crypto_d1_backtest_runner.py",
        "allowed_mode": "momentum_confirmation_v1",
        "priority": 1,
        "status": "NEEDS_PLAN",
        "approved_for_research": False,
        "execution_authorized": False,
        "blocked_reasons": [],
        "max_runtime_seconds": 1800,
        "expected_outputs": ["reports/.../report.json"],
        "safety_flags": _flags(),
        "created_at": "2026-06-04",
        "updated_at": "2026-06-04",
        "next_action": "Create the N=20 deeper-validation plan before any "
                       "execution (no execution in Step 2).",
    }
    item.update(overrides)
    return item


def _seed_queue(base: Path, items=None) -> None:
    if items is None:
        items = [_queue_item()]
    _write(base, _QUEUE_REL, {
        "schema_version": 1,
        "layer": "strategy_factory_queue_v1",
        "items": items,
    })


def _safety_contract() -> dict:
    return {
        "schema_version": 1,
        "layer": "strategy_factory_safety_v1",
        "research_only": True,
        "safety_flags": _flags(),
        "allowed_datasets": ["CRYPTO_D1_SPOT_BTC_ETH_SOL_V001_V002"],
        "allowed_runners": ["tools/crypto_d1_backtest_runner.py"],
        "allowed_modes": ["momentum_confirmation_v1"],
        "allowed_markets": ["crypto"],
        "forbidden_terms": ["broker", "exchange", "order", "live", "paper",
                            "fetch", "kraken", "binance live", "ACTIVE",
                            "STRONG", "Bundle 23"],
        "human_approval": {
            "human_approval_required_for_execution": True,
            "human_approval_required_for_paper_live": True,
            "human_approval_required_for_promotion": True,
        },
    }


def _seed_safety(base: Path, contract=None) -> None:
    _write(base, _SAFETY_REL, contract if contract is not None
           else _safety_contract())


def _seed_all(base: Path, verdict="WATCH", items=None, contract=None) -> None:
    _seed_registry(base, verdict=verdict)
    _seed_queue(base, items=items)
    _seed_safety(base, contract=contract)


def _task(plan, task_id=_TASK_ID):
    by_id = {t["task_id"]: t for t in plan["tasks"]}
    return by_id.get(task_id)


# --- Test 1: dry-run loads all three layers --------------------------------

def test_dry_run_loads_all_three_layers(tmp_path):
    _seed_all(tmp_path)
    plan = sfo.build_dry_run_plan(tmp_path)
    assert plan["dry_run"] is True
    assert plan["executes_anything"] is False
    assert plan["execution_halted"] is False
    inp = plan["inputs"]
    assert inp["registry_strategy_count"] >= 1
    assert inp["queue_item_count"] == 1
    assert inp["contract_safe"] is True


# --- Test 2 & 3: known task appears and joins to registry EXECUTED/WATCH ----

def test_known_task_joins_registry_executed_watch(tmp_path):
    _seed_all(tmp_path)
    e = _task(sfo.build_dry_run_plan(tmp_path))
    assert e is not None
    assert e["strategy_id"] == _STRATEGY_ID
    assert e["current_stage"] == "EXECUTED"
    assert e["current_verdict"] == "WATCH"
    assert e["queue_status"] == "NEEDS_PLAN"
    assert e["contract_conformant"] is True
    assert e["allowed_for_listing"] is True
    assert e["executable"] is False
    assert "deeper-validation plan" in " ".join(e["blocked_reasons"])
    assert any("execution not authorized" in r for r in e["blocked_reasons"])
    assert "plan" in e["next_action"].lower()


# --- Test 4: executable is always false ------------------------------------

def test_executable_always_false(tmp_path):
    _seed_all(tmp_path, items=[_queue_item(), _queue_item(
        task_id="another_task", approved_for_research=True)])
    plan = sfo.build_dry_run_plan(tmp_path)
    assert plan["tasks"]
    for e in plan["tasks"]:
        assert e["executable"] is False


# --- Test 5: no real command is emitted ------------------------------------

def test_no_real_command_emitted(tmp_path):
    _seed_all(tmp_path)
    plan = sfo.build_dry_run_plan(tmp_path)
    assert plan["would_run_command"] is None
    blob = sfo.to_stable_json(plan)
    e = _task(plan)
    assert e["would_run_command"] is None
    assert e["would_write_outputs"] == []
    # the only command-ish field must be a clearly-disabled, non-executable note
    assert e["disabled_preview"].startswith("DISABLED_PREVIEW")
    # no copy-pasteable interpreter invocation anywhere in the serialized plan
    for token in ("python ", ".venv", "python.exe", "&& ", "subprocess"):
        assert token not in blob


# --- Test 6: missing safety contract halts everything ----------------------

def test_missing_safety_contract_blocks_everything(tmp_path):
    _seed_registry(tmp_path)
    _seed_queue(tmp_path)
    # NO safety contract seeded
    plan = sfo.build_dry_run_plan(tmp_path)
    assert plan["execution_halted"] is True
    assert plan["inputs"]["contract_safe"] is False
    assert any("safety contract" in h for h in plan["halt_reasons"])
    e = _task(plan)
    assert e["contract_conformant"] is False
    assert e["allowed_for_listing"] is False
    assert e["executable"] is False
    assert any("safety contract" in r for r in e["blocked_reasons"])


# --- Test 7: unsafe safety contract halts everything -----------------------

def test_unsafe_safety_contract_blocks_everything(tmp_path):
    bad = _safety_contract()
    bad["safety_flags"]["execution_authorized"] = True  # makes the contract UNSAFE
    _seed_all(tmp_path, contract=bad)
    plan = sfo.build_dry_run_plan(tmp_path)
    assert plan["execution_halted"] is True
    assert plan["inputs"]["contract_safe"] is False
    e = _task(plan)
    assert e["contract_conformant"] is False
    assert e["executable"] is False


# --- Test 8: unknown strategy_id blocks the item ---------------------------

def test_unknown_strategy_id_blocks_item(tmp_path):
    _seed_registry(tmp_path)
    _seed_safety(tmp_path)
    _seed_queue(tmp_path, items=[_queue_item(
        task_id="ghost_task", strategy_id="crypto_d1_does_not_exist_v9")])
    e = _task(sfo.build_dry_run_plan(tmp_path), task_id="ghost_task")
    assert e is not None
    assert e["current_stage"] is None
    assert e["executable"] is False
    assert any("unknown strategy_id" in r for r in e["blocked_reasons"])


# --- Test 9: execution_authorized=true item is blocked ---------------------

def test_execution_authorized_item_is_blocked(tmp_path):
    bad = _queue_item(safety_flags=_flags(execution_authorized=True))
    bad["execution_authorized"] = True
    _seed_registry(tmp_path)
    _seed_safety(tmp_path)
    _seed_queue(tmp_path, items=[bad])
    e = _task(sfo.build_dry_run_plan(tmp_path))
    assert e["contract_conformant"] is False
    assert e["executable"] is False
    assert any("execution_authorized" in r for r in e["blocked_reasons"])


# --- Test 10: forbidden broker/order/fetch/live/paper path is blocked ------

def test_forbidden_path_item_is_blocked(tmp_path):
    bad = _queue_item(strategy_id="crypto_d1_live_order_broker_strategy",
                      allowed_runner="tools/broker_order_runner.py")
    _seed_registry(tmp_path)
    _seed_safety(tmp_path)
    _seed_queue(tmp_path, items=[bad])
    e = _task(sfo.build_dry_run_plan(tmp_path))
    assert e["contract_conformant"] is False
    assert e["executable"] is False
    joined = " ".join(e["blocked_reasons"])
    assert "contract:" in joined  # contract screen rejected it


# --- Test 11: no subprocess / no network / no runner import ----------------

def test_no_subprocess_no_runner_import(tmp_path, monkeypatch):
    _seed_all(tmp_path)

    def _boom(*a, **k):  # pragma: no cover - must never be called
        raise AssertionError("orchestrator must not run subprocesses")

    monkeypatch.setattr(subprocess, "run", _boom)
    monkeypatch.setattr(subprocess, "Popen", _boom)

    before = {p for p in tmp_path.rglob("*") if p.is_file()}
    plan = sfo.build_dry_run_plan(tmp_path)
    after = {p for p in tmp_path.rglob("*") if p.is_file()}
    assert before == after
    assert not (tmp_path / "reports"
                / "strategy_factory_orchestrator_v1_build").exists()
    assert "crypto_d1_backtest_runner" not in sys.modules
    assert plan["safety_flags"]["execution_authorized"] is False


# --- Test 12: deterministic ordering + stable JSON -------------------------

def test_output_is_deterministic(tmp_path):
    items = [_queue_item(task_id="bbb", priority=2),
             _queue_item(task_id="aaa", priority=1)]
    _seed_all(tmp_path, items=items)
    p1 = sfo.build_dry_run_plan(tmp_path)
    p2 = sfo.build_dry_run_plan(tmp_path)
    ids = [t["task_id"] for t in p1["tasks"]]
    assert ids == ["aaa", "bbb"]  # sorted by task_id
    assert sfo.to_stable_json(p1) == sfo.to_stable_json(p2)


# --- Test 13: opt-in writer confined to the orchestrator build folder ------

def test_write_build_report_confined(tmp_path):
    _seed_all(tmp_path)
    plan = sfo.build_dry_run_plan(tmp_path)
    written = sfo.write_build_report(tmp_path, plan)
    assert written == [
        "reports/strategy_factory_orchestrator_v1_build/dry_run_plan.json",
        "reports/strategy_factory_orchestrator_v1_build/dry_run_plan.md"]
    out_dir = tmp_path / "reports" / "strategy_factory_orchestrator_v1_build"
    assert (out_dir / "dry_run_plan.json").is_file()
    assert (out_dir / "dry_run_plan.md").is_file()
    assert not (tmp_path / "data").exists()
    assert not (tmp_path / "templates").exists()


# --- Test 14: the SHIPPED repo produces the expected dry-run for the N=20 task

def test_shipped_repo_dry_run_for_n20_task():
    plan = sfo.build_dry_run_plan(_REPO_ROOT)
    e = _task(plan)
    assert e is not None
    assert e["strategy_id"] == _STRATEGY_ID
    assert e["current_stage"] == "EXECUTED"
    assert e["current_verdict"] == "WATCH"
    assert e["queue_status"] == "PLAN_EXISTS_AWAITING_EXECUTION_APPROVAL"
    assert e["contract_conformant"] is True
    assert e["allowed_for_listing"] is True
    assert e["executable"] is False
    assert e["would_run_command"] is None
