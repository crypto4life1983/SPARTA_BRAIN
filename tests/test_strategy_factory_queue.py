"""Tests for the read-only Strategy Factory Research Queue v1 loader/validator.

``strategy_factory_queue.build(base)`` loads ``base/configs/research_queue.json``
and returns a normalized, deterministic, fail-closed validation report. These
tests pin the Step-2 safety contract:

- a well-formed item validates and is listed but is NEVER executable;
- a missing required field blocks the item (recorded, not raised);
- an unknown runner / unknown dataset / unknown mode blocks the item;
- any forbidden safety flag set true blocks the item;
- execution_authorized=true is rejected (never accepted, never executable);
- approved_for_research only confers listing eligibility, never execution;
- the loader runs no subprocess, no network, imports no runner module, and
  writes nothing except the explicit opt-in build report;
- output ordering and JSON bytes are deterministic;
- the shipped registry scanner is unaffected (smoke import).
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

import strategy_factory_queue as sfq  # noqa: E402

_QUEUE_REL = "configs/research_queue.json"


def _flags(**overrides) -> dict:
    base = {
        "research_only": True,
        "paper_live_authorized": False,
        "broker_path_enabled": False,
        "exchange_path_enabled": False,
        "order_path_enabled": False,
        "active_strong_promoted": False,
        "bundle_23_started": False,
        "dataset_mutation_allowed": False,
        "execution_authorized": False,
    }
    base.update(overrides)
    return base


def _item(**overrides) -> dict:
    item = {
        "task_id": "crypto_d1_momentum_n20_deeper_validation_v1",
        "strategy_id": "crypto_d1_momentum_confirmation_v1",
        "strategy_family": "momentum_confirmation",
        "market": "crypto",
        "dataset_id": "CRYPTO_D1_SPOT_BTC_ETH_SOL_V001_V002",
        "allowed_runner": "tools/crypto_d1_backtest_runner.py",
        "allowed_mode": "momentum_confirmation_v1",
        "priority": 1,
        "status": "QUEUED_OR_BLOCKED",
        "approved_for_research": False,
        "blocked_reasons": [],
        "max_runtime_seconds": 1800,
        "expected_outputs": ["reports/.../report.json"],
        "safety_flags": _flags(),
        "created_at": "2026-06-04",
        "updated_at": "2026-06-04",
        "next_action": "Create the N=20 deeper-validation plan or await approval.",
    }
    item.update(overrides)
    return item


def _write_queue(base: Path, obj: dict) -> None:
    p = base / _QUEUE_REL
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj), encoding="utf-8")


def _queue(items) -> dict:
    return {
        "schema_version": 1,
        "layer": "strategy_factory_queue_v1",
        "items": items,
    }


def _first(report: dict) -> dict:
    return report["items"][0]


# --- Test 1: a valid queue loads and validates -----------------------------

def test_valid_queue_loads_successfully(tmp_path):
    _write_queue(tmp_path, _queue([_item()]))
    report = sfq.build(tmp_path)

    assert report["read_only"] is True
    assert report["executes_anything"] is False
    assert report["schema_version"] == sfq.SCHEMA_VERSION
    assert report["item_count"] == 1
    assert report["valid_item_count"] == 1
    assert report["blocked_item_count"] == 0

    e = _first(report)
    assert e["valid"] is True
    assert e["blocked_reasons"] == []
    # listed but NEVER executable
    assert e["executable"] is False
    assert e["allowed_runner"] == "tools/crypto_d1_backtest_runner.py"
    assert e["allowed_mode"] == "momentum_confirmation_v1"


# --- Test 2: missing required field blocks the item ------------------------

def test_missing_required_field_blocks_item(tmp_path):
    bad = _item()
    del bad["max_runtime_seconds"]
    _write_queue(tmp_path, _queue([bad]))
    e = _first(sfq.build(tmp_path))
    assert e["valid"] is False
    assert e["executable"] is False
    assert any("missing required field: max_runtime_seconds" in r
               for r in e["blocked_reasons"])


# --- Test 3: unknown runner blocks the item --------------------------------

def test_unknown_runner_blocks_item(tmp_path):
    _write_queue(tmp_path, _queue([_item(allowed_runner="tools/evil_runner.py")]))
    e = _first(sfq.build(tmp_path))
    assert e["valid"] is False
    assert any("unknown runner not in allowlist" in r
               for r in e["blocked_reasons"])


# --- Test 4: unknown dataset blocks the item -------------------------------

def test_unknown_dataset_blocks_item(tmp_path):
    _write_queue(tmp_path, _queue([_item(dataset_id="SOME_OTHER_DATASET_V001")]))
    e = _first(sfq.build(tmp_path))
    assert e["valid"] is False
    assert any("unknown dataset not in allowlist" in r
               for r in e["blocked_reasons"])


def test_unknown_mode_blocks_item(tmp_path):
    _write_queue(tmp_path, _queue([_item(allowed_mode="live_execution_v9")]))
    e = _first(sfq.build(tmp_path))
    assert e["valid"] is False
    assert any("unknown mode not in allowlist" in r
               for r in e["blocked_reasons"])


# --- Test 5: any forbidden safety flag true blocks the item ----------------

@pytest.mark.parametrize("flag", [
    "paper_live_authorized", "broker_path_enabled", "exchange_path_enabled",
    "order_path_enabled", "active_strong_promoted", "bundle_23_started",
    "dataset_mutation_allowed", "execution_authorized",
])
def test_forbidden_safety_flag_true_blocks_item(tmp_path, flag):
    _write_queue(tmp_path, _queue([_item(safety_flags=_flags(**{flag: True}))]))
    e = _first(sfq.build(tmp_path))
    assert e["valid"] is False
    assert e["executable"] is False
    assert any(flag in r for r in e["blocked_reasons"])


def test_research_only_false_blocks_item(tmp_path):
    _write_queue(tmp_path, _queue([_item(safety_flags=_flags(research_only=False))]))
    e = _first(sfq.build(tmp_path))
    assert e["valid"] is False
    assert any("research_only must be true" in r for r in e["blocked_reasons"])


# --- Test 6: execution_authorized true is rejected, never executable -------

def test_execution_authorized_true_is_rejected(tmp_path):
    # set both the top-level field and the flag to be thorough
    bad = _item(safety_flags=_flags(execution_authorized=True))
    bad["execution_authorized"] = True
    _write_queue(tmp_path, _queue([bad]))
    e = _first(sfq.build(tmp_path))
    assert e["valid"] is False
    assert e["executable"] is False
    assert e["eligible_for_research_listing"] is False
    assert any("execution_authorized" in r for r in e["blocked_reasons"])


def test_approved_for_research_grants_listing_not_execution(tmp_path):
    _write_queue(tmp_path, _queue([_item(approved_for_research=True)]))
    e = _first(sfq.build(tmp_path))
    # a valid + approved item is eligible to be LISTED for research...
    assert e["valid"] is True
    assert e["eligible_for_research_listing"] is True
    # ...but is still NOT executable in v1.
    assert e["executable"] is False


# --- Test 7: loader runs no subprocess / no stray writes / no runner import -

def test_loader_runs_no_subprocess_and_writes_nothing(tmp_path, monkeypatch):
    _write_queue(tmp_path, _queue([_item()]))

    def _boom(*a, **k):  # pragma: no cover - must never be called
        raise AssertionError("queue loader must not run subprocesses")

    monkeypatch.setattr(subprocess, "run", _boom)
    monkeypatch.setattr(subprocess, "Popen", _boom)

    before = {p for p in tmp_path.rglob("*") if p.is_file()}
    report = sfq.build(tmp_path)
    after = {p for p in tmp_path.rglob("*") if p.is_file()}
    assert before == after
    assert not (tmp_path / "reports" / "strategy_factory_queue_v1_build").exists()
    assert report["safety_flags"] == {
        "research_only": True,
        "paper_live_authorized": False,
        "broker_path_enabled": False,
        "exchange_path_enabled": False,
        "order_path_enabled": False,
        "active_strong_promoted": False,
        "bundle_23_started": False,
        "dataset_mutation_allowed": False,
        "execution_authorized": False,
    }


def test_loader_imports_no_runner_module():
    # The queue module must not pull a runner into the import graph.
    assert "crypto_d1_backtest_runner" not in sys.modules


# --- Test 8: deterministic ordering and stable JSON ------------------------

def test_output_is_deterministic(tmp_path):
    a = _item(task_id="bbb_task", priority=2)
    b = _item(task_id="aaa_task", priority=1)
    _write_queue(tmp_path, _queue([a, b]))
    r1 = sfq.build(tmp_path)
    r2 = sfq.build(tmp_path)
    ids = [e["task_id"] for e in r1["items"]]
    # ordered by (priority, task_id): priority 1 first
    assert ids == ["aaa_task", "bbb_task"]
    assert sfq.to_stable_json(r1) == sfq.to_stable_json(r2)


# --- Test 9: missing / corrupt file fails closed (no crash) ----------------

def test_missing_queue_file_is_empty_not_crash(tmp_path):
    report = sfq.build(tmp_path)
    assert report["item_count"] == 0
    assert report["items"] == []
    assert any("not found" in w for w in report["warnings"])


def test_corrupt_queue_file_fails_closed(tmp_path):
    p = tmp_path / _QUEUE_REL
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("{ this is not valid json ", encoding="utf-8")
    report = sfq.build(tmp_path)
    assert report["item_count"] == 0
    assert any("unreadable" in w for w in report["warnings"])


# --- Test 10: the SHIPPED config validates and the N=20 task is non-exec ----

def test_shipped_config_validates_and_n20_task_not_executable():
    report = sfq.build(_REPO_ROOT)
    assert report["item_count"] >= 1
    by_id = {e["task_id"]: e for e in report["items"]}
    task = by_id.get("crypto_d1_momentum_n20_deeper_validation_v1")
    assert task is not None, "the initial N=20 task must appear in the queue"
    assert task["valid"] is True
    assert task["approved_for_research"] is False
    # appears, but is NOT executable.
    assert task["executable"] is False
    assert task["eligible_for_research_listing"] is False


# --- Test 11: opt-in write goes ONLY to the allowed build folder -----------

def test_write_build_report_confined_to_build_folder(tmp_path):
    _write_queue(tmp_path, _queue([_item()]))
    report = sfq.build(tmp_path)

    written = sfq.write_build_report(tmp_path, report)
    assert written == [
        "reports/strategy_factory_queue_v1_build/queue.json",
        "reports/strategy_factory_queue_v1_build/queue.md"]
    out_dir = tmp_path / "reports" / "strategy_factory_queue_v1_build"
    assert (out_dir / "queue.json").is_file()
    assert (out_dir / "queue.md").is_file()
    # nothing written under data/ or any dashboard/template path
    assert not (tmp_path / "data").exists()
    assert not (tmp_path / "templates").exists()
    assert (out_dir / "queue.json").read_text(encoding="utf-8") == \
        sfq.to_stable_json(report)
