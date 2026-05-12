from __future__ import annotations

import shutil
from pathlib import Path

import pytest

import strategy_lab.paper_testing_approval as paper_module
import strategy_lab.registry as registry_module
import strategy_lab.watchlist_approval as watch_module
from strategy_lab.registry import create_candidate, get_candidate


def _patch_roots(monkeypatch, leaf: str) -> Path:
    data_root = Path("strategy_lab/data") / leaf
    watch_root = data_root / "watchlist_approvals"
    paper_root = data_root / "paper_testing_approvals"
    if data_root.exists():
        shutil.rmtree(data_root, ignore_errors=True)
    monkeypatch.setattr(watch_module, "DATA_ROOT", data_root)
    monkeypatch.setattr(watch_module, "REPORT_ROOT", Path("strategy_lab/reports"))
    monkeypatch.setattr(watch_module, "WATCHLIST_APPROVAL_ROOT", watch_root)
    monkeypatch.setattr(watch_module, "DECISIONS_FILE", watch_root / "decisions.json")
    monkeypatch.setattr(watch_module, "REPORT_FILE", Path("strategy_lab/reports/strategy_lab_phase_15_watchlist_approval.md"))
    monkeypatch.setattr(paper_module, "DATA_ROOT", data_root)
    monkeypatch.setattr(paper_module, "REPORT_ROOT", Path("strategy_lab/reports"))
    monkeypatch.setattr(paper_module, "PAPER_TESTING_APPROVAL_ROOT", paper_root)
    monkeypatch.setattr(paper_module, "DECISIONS_FILE", paper_root / "decisions.json")
    monkeypatch.setattr(paper_module, "REPORT_FILE", Path("strategy_lab/reports/strategy_lab_phase_14_paper_testing_approval.md"))
    monkeypatch.setattr(registry_module, "DATA_ROOT", data_root)
    monkeypatch.setattr(registry_module, "CANDIDATES_FILE", data_root / "candidates.json")
    return data_root


def test_approve_paper_testing_to_watchlist(monkeypatch):
    _patch_roots(monkeypatch, "approve_watchlist")
    create_candidate({"candidate_id": "cand_wl_01", "status": "PAPER_TESTING", "lifecycle_state": "PAPER_TESTING"})
    decision = watch_module.approve_paper_testing_to_watchlist(
        "cand_wl_01",
        reviewer="alice",
        notes="Observation only",
        paper_summary="Paper testing observed and summarized.",
    )
    assert decision["decision"] == "APPROVE_FOR_WATCHLIST"
    assert decision["new_state"] == "WATCHLIST"
    assert get_candidate("cand_wl_01")["lifecycle_state"] == "WATCHLIST"
    assert watch_module.load_watchlist_decisions()


def test_block_robust_to_watchlist(monkeypatch):
    _patch_roots(monkeypatch, "block_robust")
    create_candidate({"candidate_id": "cand_wl_02", "status": "ROBUST", "lifecycle_state": "ROBUST"})
    with pytest.raises(ValueError):
        watch_module.approve_paper_testing_to_watchlist(
            "cand_wl_02",
            reviewer="alice",
            notes="Observation only",
            paper_summary="Summary",
        )


def test_block_idea_to_watchlist(monkeypatch):
    _patch_roots(monkeypatch, "block_idea")
    create_candidate({"candidate_id": "cand_wl_03", "status": "IDEA", "lifecycle_state": "IDEA"})
    with pytest.raises(ValueError):
        watch_module.approve_paper_testing_to_watchlist(
            "cand_wl_03",
            reviewer="alice",
            notes="Observation only",
            paper_summary="Summary",
        )


def test_require_paper_summary(monkeypatch):
    _patch_roots(monkeypatch, "require_summary")
    create_candidate({"candidate_id": "cand_wl_04", "status": "PAPER_TESTING", "lifecycle_state": "PAPER_TESTING"})
    with pytest.raises(ValueError):
        watch_module.approve_paper_testing_to_watchlist(
            "cand_wl_04",
            reviewer="alice",
            notes="Observation only",
            paper_summary="",
        )


def test_reject_logs_decision(monkeypatch):
    _patch_roots(monkeypatch, "reject")
    create_candidate({"candidate_id": "cand_wl_05", "status": "PAPER_TESTING", "lifecycle_state": "PAPER_TESTING"})
    decision = watch_module.reject_after_paper_testing(
        "cand_wl_05",
        reviewer="bob",
        notes="Reject before watchlist",
        paper_summary="Observation summary",
    )
    assert decision["decision"] == "REJECT"
    assert decision["new_state"] == "REJECTED"
    assert get_candidate("cand_wl_05")["lifecycle_state"] == "REJECTED"


def test_no_live_state_emitted(monkeypatch):
    _patch_roots(monkeypatch, "no_live")
    create_candidate({"candidate_id": "cand_wl_06", "status": "PAPER_TESTING", "lifecycle_state": "PAPER_TESTING"})
    decision = watch_module.approve_paper_testing_to_watchlist(
        "cand_wl_06",
        reviewer="alice",
        notes="Observation only",
        paper_summary="Paper summary",
    )
    assert decision["new_state"] == "WATCHLIST"
    source = Path(watch_module.__file__).read_text(encoding="utf-8").lower()
    assert "live_ready" not in source


def test_safety_scan_still_passes():
    source = Path(watch_module.__file__).read_text(encoding="utf-8").lower()
    for forbidden in ("broker", "place_order", "submit_order", "execute_order", "live execution"):
        assert forbidden not in source
