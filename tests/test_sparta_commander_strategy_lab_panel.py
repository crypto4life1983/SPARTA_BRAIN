from __future__ import annotations

import re
from pathlib import Path

import sparta_commander.commander as commander
import sparta_commander.strategy_lab_readiness as strategy_lab_readiness
import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient


def test_missing_strategy_lab_report_handles_safely(monkeypatch, tmp_path):
    monkeypatch.setattr(strategy_lab_readiness, "LOCAL_STRATEGY_LAB_REPORT", tmp_path / "strategy_lab" / "reports" / "strategy_lab_master_readiness.json")
    monkeypatch.setattr(strategy_lab_readiness, "LOCAL_REPORTS_FALLBACK", tmp_path / "reports" / "strategy_lab_master_readiness.json")
    report = strategy_lab_readiness.load_strategy_lab_master_readiness_report()
    assert report["candidate_count"] == 0
    assert report["status"] == "INSUFFICIENT_DATA"
    assert report["safety_status"] == "ISOLATED / READ_ONLY"
    assert "LIVE_READY" not in str(report)


def test_strategy_lab_panel_renders_read_only_counts(monkeypatch):
    import app as app_module

    monkeypatch.setattr(
        commander,
        "load_strategy_lab_master_readiness_report",
        lambda: {
            "schema": "sparta_commander.strategy_lab_master_readiness.v1",
            "generated_at": "2026-05-12T12:34:56+00:00",
            "read_only": True,
            "status": "READY",
            "candidate_count": 3,
            "status_counts": {
                "REJECT": 1,
                "NEEDS_MORE_RESEARCH": 1,
                "PAPER_READY": 1,
                "WATCHLIST_READY": 0,
            },
            "latest_generated_at": "2026-05-12T12:34:56+00:00",
            "safety_status": "ISOLATED / READ_ONLY",
            "source_report": {"path": "C:\\SPARTA_BRAIN\\reports\\strategy_lab_master_readiness.json", "exists": True},
            "candidates": [],
        },
    )
    client = TestClient(app_module.app)
    response = client.get("/")
    assert response.status_code == 200
    body = response.text
    assert "Strategy Lab" in body
    assert "candidate_count" not in body.lower()
    assert "LIVE_READY" not in body
    assert "Reject: 1" in body
    assert "NEEDS_MORE_RESEARCH" in body or "Needs more research" in body
    assert "PAPER_READY" in body or "Paper ready" in body
    assert "ISOLATED / READ_ONLY" in body


def test_strategy_lab_panel_has_no_action_buttons(monkeypatch):
    import app as app_module

    monkeypatch.setattr(
        commander,
        "load_strategy_lab_master_readiness_report",
        lambda: {
            "schema": "sparta_commander.strategy_lab_master_readiness.v1",
            "generated_at": "2026-05-12T12:34:56+00:00",
            "read_only": True,
            "status": "INSUFFICIENT_DATA",
            "candidate_count": 0,
            "status_counts": {
                "REJECT": 0,
                "NEEDS_MORE_RESEARCH": 0,
                "PAPER_READY": 0,
                "WATCHLIST_READY": 0,
            },
            "latest_generated_at": None,
            "safety_status": "ISOLATED / READ_ONLY",
            "source_report": {"path": None, "exists": False},
            "candidates": [],
        },
    )
    client = TestClient(app_module.app)
    response = client.get("/")
    assert response.status_code == 200
    body = response.text
    match = re.search(r'<section id="strategy-lab-panel".*?</section>', body, flags=re.S)
    assert match is not None
    panel_html = match.group(0)
    assert "<button" not in panel_html.lower()
    assert "action" not in panel_html.lower()
    assert "trade" not in panel_html.lower()
    assert "execute" not in panel_html.lower()


def test_strategy_lab_panel_reads_report_data_only(monkeypatch):
    import app as app_module

    sample = {
        "schema": "sparta_commander.strategy_lab_master_readiness.v1",
        "generated_at": "2026-05-12T12:34:56+00:00",
        "read_only": True,
        "status": "READY",
        "candidate_count": 2,
        "status_counts": {
            "REJECT": 0,
            "NEEDS_MORE_RESEARCH": 1,
            "PAPER_READY": 1,
            "WATCHLIST_READY": 0,
        },
        "latest_generated_at": "2026-05-12T12:34:56+00:00",
        "safety_status": "ISOLATED / READ_ONLY",
        "source_report": {"path": "C:\\SPARTA_BRAIN\\reports\\strategy_lab_master_readiness.json", "exists": True},
        "candidates": [],
    }
    monkeypatch.setattr(commander, "load_strategy_lab_master_readiness_report", lambda: sample)
    summary = commander.dashboard_summary()
    assert summary["strategy_lab_master_readiness"] == sample
    client = TestClient(app_module.app)
    response = client.get("/")
    assert response.status_code == 200
    body = response.text
    assert "2" in body
    assert "PAPER_READY" in body or "Paper ready" in body
