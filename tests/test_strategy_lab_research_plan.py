from __future__ import annotations

from pathlib import Path

import pytest

import strategy_lab.discovery_inbox as inbox_module
import strategy_lab.human_review as human_review_module
import strategy_lab.registry as registry_module
import strategy_lab.research_plan as plan_module
from strategy_lab.discovery_inbox import StrategyIdea, add_idea, convert_idea_to_candidate
from strategy_lab.human_review import approve_for_research
from strategy_lab.registry import create_candidate, get_candidate
from strategy_lab.research_plan import create_research_plan, get_research_plan, load_research_plans


def _patch_roots(monkeypatch, leaf: str) -> tuple[Path, Path, Path]:
    data_root = Path("strategy_lab/data")
    inbox_root = data_root / "discovery_inbox" / leaf
    review_root = data_root / "human_review" / leaf
    plans_root = data_root / "research_plans" / leaf
    monkeypatch.setattr(inbox_module, "DATA_ROOT", data_root)
    monkeypatch.setattr(inbox_module, "DISCOVERY_INBOX_ROOT", inbox_root)
    monkeypatch.setattr(inbox_module, "IDEAS_FILE", inbox_root / "ideas.json")
    monkeypatch.setattr(human_review_module, "DATA_ROOT", data_root)
    monkeypatch.setattr(human_review_module, "HUMAN_REVIEW_ROOT", review_root)
    monkeypatch.setattr(human_review_module, "REVIEW_LOG_FILE", review_root / "review_log.json")
    monkeypatch.setattr(registry_module, "DATA_ROOT", data_root)
    monkeypatch.setattr(registry_module, "CANDIDATES_FILE", data_root / "candidates.json")
    monkeypatch.setattr(plan_module, "DATA_ROOT", data_root)
    monkeypatch.setattr(plan_module, "RESEARCH_PLANS_ROOT", plans_root)
    monkeypatch.setattr(plan_module, "PLANS_FILE", plans_root / "plans.json")
    return inbox_root, review_root, plans_root


def _cleanup(*paths: Path) -> None:
    for path in paths:
        if path.is_file():
            path.unlink(missing_ok=True)
        elif path.is_dir():
            for item in sorted(path.rglob("*"), reverse=True):
                if item.is_file():
                    item.unlink(missing_ok=True)
                elif item.is_dir():
                    item.rmdir()
            path.rmdir()


def test_creates_plan_for_in_research_candidate(monkeypatch):
    inbox_root, review_root, plans_root = _patch_roots(monkeypatch, "in_research")
    add_idea(
        StrategyIdea(
            idea_id="idea_rp_01",
            title="Research Plan Idea",
            hypothesis="Research should verify whether trend continuation survives compression.",
            source="manual",
            symbols=["BTCUSDT", "ETHUSDT"],
            timeframe="1D",
        )
    )
    convert_idea_to_candidate("idea_rp_01")
    approve_for_research("idea_rp_01", reviewer="alice", notes="Approve for research only")
    plan = create_research_plan("idea_rp_01")
    assert plan["candidate_id"] == "idea_rp_01"
    assert plan["symbols_to_test"]
    assert plan["timeframes_to_test"]
    assert plan["regimes_to_test"]
    assert plan["status"] == "EXPERIMENTAL"
    assert get_research_plan("idea_rp_01")["candidate_id"] == "idea_rp_01"
    assert load_research_plans()
    assert get_candidate("idea_rp_01")["lifecycle_state"] == "IN_RESEARCH"
    _cleanup(inbox_root, review_root, plans_root, Path("strategy_lab/data/candidates.json"))


def test_rejects_idea_candidate(monkeypatch):
    inbox_root, review_root, plans_root = _patch_roots(monkeypatch, "idea_reject")
    add_idea(
        StrategyIdea(
            idea_id="idea_rp_02",
            title="Idea Only",
            hypothesis="Still just an idea.",
            source="manual",
        )
    )
    convert_idea_to_candidate("idea_rp_02")
    with pytest.raises(ValueError):
        create_research_plan("idea_rp_02")
    assert get_candidate("idea_rp_02")["lifecycle_state"] == "IDEA"
    _cleanup(inbox_root, review_root, plans_root, Path("strategy_lab/data/candidates.json"))


def test_rejects_backtested_candidate(monkeypatch):
    inbox_root, review_root, plans_root = _patch_roots(monkeypatch, "backtested_reject")
    create_candidate(
        {
            "candidate_id": "idea_rp_03",
            "name": "Backtested Candidate",
            "description": "Backtested candidate stays outside research-plan eligibility.",
            "status": "BACKTESTED",
            "lifecycle_state": "BACKTESTED",
        }
    )
    with pytest.raises(ValueError):
        create_research_plan("idea_rp_03")
    assert get_candidate("idea_rp_03")["lifecycle_state"] == "BACKTESTED"
    _cleanup(inbox_root, review_root, plans_root, Path("strategy_lab/data/candidates.json"))


def test_plan_includes_anti_overfit_requirements(monkeypatch):
    inbox_root, review_root, plans_root = _patch_roots(monkeypatch, "requirements")
    add_idea(
        StrategyIdea(
            idea_id="idea_rp_04",
            title="Requirements",
            hypothesis="Plan should include anti-overfit requirements.",
            source="manual",
        )
    )
    convert_idea_to_candidate("idea_rp_04")
    approve_for_research("idea_rp_04", reviewer="alice", notes="OK")
    plan = create_research_plan("idea_rp_04")
    assert plan["required_min_trades"] >= 30
    assert plan["required_oos_periods"] >= 3
    assert plan["required_walk_forward_windows"] >= 3
    assert any("out_of_sample_return" in item for item in plan["rejection_conditions"])
    _cleanup(inbox_root, review_root, plans_root, Path("strategy_lab/data/candidates.json"))


def test_plan_includes_regime_requirements(monkeypatch):
    inbox_root, review_root, plans_root = _patch_roots(monkeypatch, "regime")
    add_idea(
        StrategyIdea(
            idea_id="idea_rp_05",
            title="Regime Requirements",
            hypothesis="Plan should include regime testing.",
            source="manual",
        )
    )
    convert_idea_to_candidate("idea_rp_05")
    approve_for_research("idea_rp_05", reviewer="alice", notes="OK")
    plan = create_research_plan("idea_rp_05")
    assert set(plan["regimes_to_test"]) >= {"TREND", "RANGE", "HIGH_VOL", "LOW_VOL", "COMPRESSION", "EXPANSION"}
    assert plan["symbols_to_test"]
    assert plan["timeframes_to_test"]
    _cleanup(inbox_root, review_root, plans_root, Path("strategy_lab/data/candidates.json"))


def test_no_lifecycle_change_happens(monkeypatch):
    inbox_root, review_root, plans_root = _patch_roots(monkeypatch, "lifecycle")
    add_idea(
        StrategyIdea(
            idea_id="idea_rp_06",
            title="No Lifecycle Change",
            hypothesis="Creating a plan must not mutate lifecycle.",
            source="manual",
        )
    )
    convert_idea_to_candidate("idea_rp_06")
    approve_for_research("idea_rp_06", reviewer="alice", notes="OK")
    before = get_candidate("idea_rp_06")["lifecycle_state"]
    create_research_plan("idea_rp_06")
    after = get_candidate("idea_rp_06")["lifecycle_state"]
    assert before == after == "IN_RESEARCH"
    _cleanup(inbox_root, review_root, plans_root, Path("strategy_lab/data/candidates.json"))


def test_safety_scan_still_passes():
    source = Path(plan_module.__file__).read_text(encoding="utf-8").lower()
    for forbidden in ("broker", "place_order", "submit_order", "execute_order", "live execution"):
        assert forbidden not in source

