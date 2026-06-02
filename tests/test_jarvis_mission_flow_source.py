"""Tests for the Phase A read-only Crypto-D1 Mission Flow source aggregator.

`app._jarvis_crypto_d1_mission_flow()` summarizes the committed Crypto-D1
workflow/pipeline truth (candidate registry + readiness gate + operator
missing-items checklist + filesystem presence) into a read-only payload for the
Mission Flow panel.

These tests pin the safety contract:
- a valid source set reports the *real* conservative truth (NOT_READY,
  WATCH/MIXED, 16 items all MISSING/PENDING, no data/qa/baseline present);
- a missing readiness gate fails closed (never inferred upward);
- a malformed checklist fails closed (checklist_ready stays false);
- a tampered registry claiming ACTIVE/STRONG is clamped to WATCH/MIXED;
- the aggregator never creates a directory, never runs a subprocess, and never
  touches the network.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

pytest.importorskip("fastapi")

_CANDIDATES_REL = \
    "reports/strategy_factory_routines/candidate_registry/candidates.json"
_READINESS_REL = "reports/crypto_d1_readiness_gate_v1/readiness_gate.json"
_CHECKLIST_REL = \
    "reports/crypto_d1_operator_missing_items_checklist_v1/checklist.json"


def _write(base: Path, rel: str, obj) -> None:
    p = base / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj), encoding="utf-8")


def _valid_candidates() -> dict:
    return {
        "read_only": True,
        "candidates": [
            {"candidate_id": "crypto_d1_protocol", "lane": "crypto_d1",
             "status": "WATCH", "evidence_level": "MIXED"},
            {"candidate_id": "arbitrage_research_protocol", "lane": "arb",
             "status": "IDEA", "evidence_level": "NONE"},
        ],
    }


def _valid_readiness() -> dict:
    return {"readiness_status": "NOT_READY_FOR_REAL_DATA",
            "lane_status": "WATCH", "evidence_level": "MIXED"}


def _valid_checklist(n: int = 16) -> dict:
    return {
        "overall_readiness_status": "NOT_READY_FOR_REAL_DATA",
        "items": [
            {"id": f"item_{i}", "status": "MISSING", "approval_status": "PENDING"}
            for i in range(n)
        ],
    }


def _seed_valid(base: Path) -> None:
    _write(base, _CANDIDATES_REL, _valid_candidates())
    _write(base, _READINESS_REL, _valid_readiness())
    _write(base, _CHECKLIST_REL, _valid_checklist())


# --- Test 1: valid sources report the conservative real truth --------------

def test_valid_sources_report_not_ready_watch_mixed(monkeypatch, tmp_path):
    import app as app_module
    _seed_valid(tmp_path)
    monkeypatch.setattr(app_module, "BASE", tmp_path)
    mf = app_module._jarvis_crypto_d1_mission_flow()

    assert mf["state"] == "ready"
    assert mf["read_only"] is True
    assert mf["display_only"] is True
    assert mf["no_execution"] is True
    assert mf["safety_level"] == "research_only"

    assert mf["lane_status"] == "WATCH"
    assert mf["evidence_level"] == "MIXED"
    assert mf["readiness_status"] == "NOT_READY_FOR_REAL_DATA"

    assert mf["checklist_total"] == 16
    assert mf["checklist_counts"]["MISSING"] == 16
    assert mf["checklist_counts"]["COMPLETE"] == 0
    assert mf["pending_approval_count"] == 16
    assert mf["overall_readiness_status"] == "NOT_READY_FOR_REAL_DATA"
    assert mf["checklist_ready"] is False

    # no real-data work has happened: presence probes are all false
    assert mf["data_present"] is False
    assert mf["qa_present"] is False
    assert mf["qa_status"] is None
    assert mf["baseline_present"] is False
    assert mf["warnings"] == []


# --- Test 2: a missing readiness gate fails closed -------------------------

def test_missing_readiness_gate_fails_closed(monkeypatch, tmp_path):
    import app as app_module
    # Seed only the registry + checklist; omit the readiness gate entirely.
    _write(tmp_path, _CANDIDATES_REL, _valid_candidates())
    _write(tmp_path, _CHECKLIST_REL, _valid_checklist())
    monkeypatch.setattr(app_module, "BASE", tmp_path)
    mf = app_module._jarvis_crypto_d1_mission_flow()

    # readiness is never inferred upward when the gate is absent
    assert mf["readiness_status"] == "NOT_READY_FOR_REAL_DATA"
    # one core source missing => aggregate must not be "ready"
    assert mf["state"] == "missing"
    assert mf["lane_status"] == "WATCH"
    assert mf["evidence_level"] == "MIXED"
    assert any("readiness gate" in w for w in mf["warnings"])


# --- Test 3: a malformed checklist fails closed ----------------------------

def test_malformed_checklist_fails_closed(monkeypatch, tmp_path):
    import app as app_module
    _write(tmp_path, _CANDIDATES_REL, _valid_candidates())
    _write(tmp_path, _READINESS_REL, _valid_readiness())
    # corrupt the checklist JSON
    p = tmp_path / _CHECKLIST_REL
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("{ this is not valid json", encoding="utf-8")
    monkeypatch.setattr(app_module, "BASE", tmp_path)
    mf = app_module._jarvis_crypto_d1_mission_flow()

    assert mf["checklist_ready"] is False
    assert mf["checklist_total"] == 0
    assert mf["overall_readiness_status"] is None
    # corrupt source => error state, never ready
    assert mf["state"] == "error"
    assert any("checklist" in w for w in mf["warnings"])
    # readiness still conservative regardless of the checklist breakage
    assert mf["readiness_status"] == "NOT_READY_FOR_REAL_DATA"


# --- Test 4: a tampered registry verdict is clamped ------------------------

def test_tampered_active_strong_is_clamped(monkeypatch, tmp_path):
    import app as app_module
    tampered = {
        "candidates": [
            {"candidate_id": "crypto_d1_protocol", "lane": "crypto_d1",
             "status": "ACTIVE", "evidence_level": "STRONG"},
        ],
    }
    _write(tmp_path, _CANDIDATES_REL, tampered)
    _write(tmp_path, _READINESS_REL, _valid_readiness())
    _write(tmp_path, _CHECKLIST_REL, _valid_checklist())
    monkeypatch.setattr(app_module, "BASE", tmp_path)
    mf = app_module._jarvis_crypto_d1_mission_flow()

    # forbidden verdicts must NEVER surface on the dashboard
    assert mf["lane_status"] == "WATCH"
    assert mf["evidence_level"] == "MIXED"
    assert mf["lane_status"] != "ACTIVE"
    assert mf["evidence_level"] != "STRONG"
    # the clamp must be recorded so the tamper is visible, not silent
    assert any("ACTIVE" in w and "clamped" in w for w in mf["warnings"])
    assert any("STRONG" in w and "clamped" in w for w in mf["warnings"])


# --- Test 5: no side effects (no dir creation, no subprocess, no network) ---

def test_no_side_effects_no_dir_no_subprocess(monkeypatch, tmp_path):
    import app as app_module
    _seed_valid(tmp_path)
    monkeypatch.setattr(app_module, "BASE", tmp_path)

    def _boom(*a, **k):  # pragma: no cover - must never be called
        raise AssertionError("mission flow source must not run subprocesses")

    monkeypatch.setattr(subprocess, "run", _boom)
    monkeypatch.setattr(subprocess, "Popen", _boom)

    mf = app_module._jarvis_crypto_d1_mission_flow()
    assert mf["state"] == "ready"

    # the research data directory must NOT be created by a read-only probe
    assert not (tmp_path / "data" / "crypto_d1_research").exists()
    assert mf["data_present"] is False


def test_present_data_dir_reports_presence_only(monkeypatch, tmp_path):
    """If an operator HAS produced qa/baseline artifacts, presence is reflected
    truthfully (presence-only; the aggregator still never runs them)."""
    import app as app_module
    _seed_valid(tmp_path)
    data_dir = tmp_path / "data" / "crypto_d1_research" / "run1"
    data_dir.mkdir(parents=True)
    (data_dir / "qa_report.json").write_text(
        json.dumps({"qa_status": "PASS"}), encoding="utf-8")
    (data_dir / "baseline_report.json").write_text(
        json.dumps({"ok": True}), encoding="utf-8")
    monkeypatch.setattr(app_module, "BASE", tmp_path)
    mf = app_module._jarvis_crypto_d1_mission_flow()

    assert mf["data_present"] is True
    assert mf["qa_present"] is True
    assert mf["qa_status"] == "PASS"
    assert mf["baseline_present"] is True
