from __future__ import annotations

import json
from pathlib import Path

import pytest

import strategy_lab.human_review as human_review_module
import strategy_lab.registry as registry_module
from strategy_lab.discovery_inbox import StrategyIdea, add_idea, convert_idea_to_candidate
from strategy_lab.human_review import approve_for_research, load_review_log, reject_candidate


def _patch_roots(monkeypatch, leaf: str) -> Path:
    data_root = Path("strategy_lab/data")
    review_root = data_root / "human_review" / leaf
    monkeypatch.setattr(human_review_module, "DATA_ROOT", data_root)
    monkeypatch.setattr(human_review_module, "HUMAN_REVIEW_ROOT", review_root)
    monkeypatch.setattr(human_review_module, "REVIEW_LOG_FILE", review_root / "review_log.json")
    monkeypatch.setattr(registry_module, "DATA_ROOT", data_root)
    monkeypatch.setattr(registry_module, "CANDIDATES_FILE", data_root / "candidates.json")
    return review_root


def _seed_idea(monkeypatch, leaf: str, idea_id: str) -> None:
    from strategy_lab.discovery_inbox import DISCOVERY_INBOX_ROOT, IDEAS_FILE
    inbox_root = Path("strategy_lab/data/discovery_inbox") / leaf
    monkeypatch.setattr(human_review_module, "DATA_ROOT", Path("strategy_lab/data"))
    monkeypatch.setattr(registry_module, "DATA_ROOT", Path("strategy_lab/data"))
    monkeypatch.setattr(registry_module, "CANDIDATES_FILE", Path("strategy_lab/data/candidates.json"))
    add_idea(
        StrategyIdea(
            idea_id=idea_id,
            title="Test Idea",
            hypothesis="Test hypothesis",
            source="test",
        )
    )


def test_approve_idea_to_in_research(monkeypatch):
    review_root = _patch_roots(monkeypatch, "approve")
    from strategy_lab.discovery_inbox import DISCOVERY_INBOX_ROOT, IDEAS_FILE
    monkeypatch.setattr(registry_module, "DATA_ROOT", Path("strategy_lab/data"))
    monkeypatch.setattr(registry_module, "CANDIDATES_FILE", Path("strategy_lab/data/candidates.json"))
    inbox_root = Path("strategy_lab/data/discovery_inbox") / "approve"
    from strategy_lab import discovery_inbox as inbox_module
    monkeypatch.setattr(inbox_module, "DATA_ROOT", Path("strategy_lab/data"))
    monkeypatch.setattr(inbox_module, "DISCOVERY_INBOX_ROOT", inbox_root)
    monkeypatch.setattr(inbox_module, "IDEAS_FILE", inbox_root / "ideas.json")
    add_idea(
        StrategyIdea(
            idea_id="idea_hr_01",
            title="Human Review Idea",
            hypothesis="Human review should unlock research only.",
            source="manual",
        )
    )
    convert_idea_to_candidate("idea_hr_01")
    logged = approve_for_research("idea_hr_01", reviewer="alice", notes="Approved for research")
    assert logged["decision"] == "APPROVE_FOR_RESEARCH"
    assert registry_module.get_candidate("idea_hr_01")["lifecycle_state"] == "IN_RESEARCH"
    assert load_review_log()[-1]["candidate_id"] == "idea_hr_01"
    (inbox_root / "ideas.json").unlink(missing_ok=True)
    (Path("strategy_lab/data/candidates.json")).unlink(missing_ok=True)
    (review_root / "review_log.json").unlink(missing_ok=True)


def test_cannot_approve_backtested_to_paper_testing(monkeypatch):
    review_root = _patch_roots(monkeypatch, "block")
    from strategy_lab import discovery_inbox as inbox_module
    inbox_root = Path("strategy_lab/data/discovery_inbox") / "block"
    monkeypatch.setattr(inbox_module, "DATA_ROOT", Path("strategy_lab/data"))
    monkeypatch.setattr(inbox_module, "DISCOVERY_INBOX_ROOT", inbox_root)
    monkeypatch.setattr(inbox_module, "IDEAS_FILE", inbox_root / "ideas.json")
    add_idea(
        StrategyIdea(
            idea_id="idea_hr_02",
            title="Blocked Idea",
            hypothesis="Blocked transitions should stay blocked.",
            source="manual",
        )
    )
    convert_idea_to_candidate("idea_hr_02")
    approve_for_research("idea_hr_02", reviewer="alice", notes="Unlock research only")
    registry_module.update_candidate_state("idea_hr_02", "BACKTESTED")
    with pytest.raises(ValueError):
        approve_for_research("idea_hr_02", reviewer="alice", notes="Try to force paper testing")
    (inbox_root / "ideas.json").unlink(missing_ok=True)
    (Path("strategy_lab/data/candidates.json")).unlink(missing_ok=True)
    (review_root / "review_log.json").unlink(missing_ok=True)


def test_cannot_approve_anything_to_live(monkeypatch):
    _patch_roots(monkeypatch, "live")
    from strategy_lab import discovery_inbox as inbox_module
    inbox_root = Path("strategy_lab/data/discovery_inbox") / "live"
    monkeypatch.setattr(inbox_module, "DATA_ROOT", Path("strategy_lab/data"))
    monkeypatch.setattr(inbox_module, "DISCOVERY_INBOX_ROOT", inbox_root)
    monkeypatch.setattr(inbox_module, "IDEAS_FILE", inbox_root / "ideas.json")
    add_idea(
        StrategyIdea(
            idea_id="idea_hr_03",
            title="Live Blocked Idea",
            hypothesis="Live is impossible.",
            source="manual",
        )
    )
    convert_idea_to_candidate("idea_hr_03")
    with pytest.raises(ValueError):
        registry_module.update_candidate_state("idea_hr_03", "LIVE")
    (inbox_root / "ideas.json").unlink(missing_ok=True)
    Path("strategy_lab/data/candidates.json").unlink(missing_ok=True)


def test_reject_candidate_logs_decision(monkeypatch):
    review_root = _patch_roots(monkeypatch, "reject")
    from strategy_lab import discovery_inbox as inbox_module
    inbox_root = Path("strategy_lab/data/discovery_inbox") / "reject"
    monkeypatch.setattr(inbox_module, "DATA_ROOT", Path("strategy_lab/data"))
    monkeypatch.setattr(inbox_module, "DISCOVERY_INBOX_ROOT", inbox_root)
    monkeypatch.setattr(inbox_module, "IDEAS_FILE", inbox_root / "ideas.json")
    add_idea(
        StrategyIdea(
            idea_id="idea_hr_04",
            title="Rejectable Idea",
            hypothesis="This idea should be rejected.",
            source="manual",
        )
    )
    convert_idea_to_candidate("idea_hr_04")
    logged = reject_candidate("idea_hr_04", reviewer="bob", notes="Not robust enough")
    assert logged["decision"] == "REJECT"
    assert registry_module.get_candidate("idea_hr_04")["lifecycle_state"] == "REJECTED"
    assert load_review_log()[-1]["candidate_id"] == "idea_hr_04"
    (inbox_root / "ideas.json").unlink(missing_ok=True)
    Path("strategy_lab/data/candidates.json").unlink(missing_ok=True)
    (review_root / "review_log.json").unlink(missing_ok=True)


def test_reviewer_required(monkeypatch):
    _patch_roots(monkeypatch, "reviewer")
    from strategy_lab import discovery_inbox as inbox_module
    inbox_root = Path("strategy_lab/data/discovery_inbox") / "reviewer"
    monkeypatch.setattr(inbox_module, "DATA_ROOT", Path("strategy_lab/data"))
    monkeypatch.setattr(inbox_module, "DISCOVERY_INBOX_ROOT", inbox_root)
    monkeypatch.setattr(inbox_module, "IDEAS_FILE", inbox_root / "ideas.json")
    add_idea(
        StrategyIdea(
            idea_id="idea_hr_05",
            title="Reviewer Check",
            hypothesis="Reviewer is required.",
            source="manual",
        )
    )
    convert_idea_to_candidate("idea_hr_05")
    with pytest.raises(ValueError):
        approve_for_research("idea_hr_05", reviewer="", notes="notes")
    (inbox_root / "ideas.json").unlink(missing_ok=True)
    Path("strategy_lab/data/candidates.json").unlink(missing_ok=True)


def test_notes_required(monkeypatch):
    _patch_roots(monkeypatch, "notes")
    from strategy_lab import discovery_inbox as inbox_module
    inbox_root = Path("strategy_lab/data/discovery_inbox") / "notes"
    monkeypatch.setattr(inbox_module, "DATA_ROOT", Path("strategy_lab/data"))
    monkeypatch.setattr(inbox_module, "DISCOVERY_INBOX_ROOT", inbox_root)
    monkeypatch.setattr(inbox_module, "IDEAS_FILE", inbox_root / "ideas.json")
    add_idea(
        StrategyIdea(
            idea_id="idea_hr_06",
            title="Notes Check",
            hypothesis="Notes are required.",
            source="manual",
        )
    )
    convert_idea_to_candidate("idea_hr_06")
    with pytest.raises(ValueError):
        reject_candidate("idea_hr_06", reviewer="alice", notes="")
    (inbox_root / "ideas.json").unlink(missing_ok=True)
    Path("strategy_lab/data/candidates.json").unlink(missing_ok=True)


def test_safety_scan_still_passes():
    source = Path(human_review_module.__file__).read_text(encoding="utf-8").lower()
    for forbidden in ("broker", "place_order", "submit_order", "execute_order", "live execution", "exchange write"):
        assert forbidden not in source
