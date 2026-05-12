from __future__ import annotations

import json
from pathlib import Path

import pytest

import strategy_lab.discovery_inbox as inbox_module
import strategy_lab.registry as registry_module
from strategy_lab.discovery_inbox import StrategyIdea, add_idea, convert_idea_to_candidate, get_idea, load_ideas


def _patch_inbox_roots(monkeypatch, leaf: str) -> Path:
    root = Path("strategy_lab/data/discovery_inbox") / leaf
    monkeypatch.setattr(inbox_module, "DATA_ROOT", Path("strategy_lab/data"))
    monkeypatch.setattr(inbox_module, "DISCOVERY_INBOX_ROOT", root)
    monkeypatch.setattr(inbox_module, "IDEAS_FILE", root / "ideas.json")
    monkeypatch.setattr(registry_module, "DATA_ROOT", Path("strategy_lab/data"))
    monkeypatch.setattr(registry_module, "CANDIDATES_FILE", Path("strategy_lab/data/candidates.json"))
    return root


def test_add_idea(monkeypatch):
    root = _patch_inbox_roots(monkeypatch, "phase9_add")
    idea = add_idea(
        StrategyIdea(
            idea_id="idea_01",
            title="Donchian Experiment",
            hypothesis="A wider breakout filter may improve trend capture.",
            source="research_note",
            symbols=["BTCUSDT", "ETHUSDT"],
            timeframe="1D",
            expected_edge="trend capture",
            risk_notes="Needs human review before research",
        )
    )
    assert idea["idea_id"] == "idea_01"
    assert idea["status"] == "IDEA"
    assert (root / "ideas.json").exists()
    (root / "ideas.json").unlink(missing_ok=True)


def test_load_idea(monkeypatch):
    root = _patch_inbox_roots(monkeypatch, "phase9_load")
    add_idea(
        StrategyIdea(
            idea_id="idea_02",
            title="RSI Reversal",
            hypothesis="Mean reversion may work after volatility spikes.",
            source="brainstorm",
            symbols=["BTCUSDT"],
            timeframe="4H",
            expected_edge="reversal",
            risk_notes="Experimental only",
        )
    )
    ideas = load_ideas()
    assert len(ideas) == 1
    assert get_idea("idea_02")["title"] == "RSI Reversal"
    (root / "ideas.json").unlink(missing_ok=True)


def test_convert_idea_to_candidate(monkeypatch):
    root = _patch_inbox_roots(monkeypatch, "phase9_convert")
    candidate_store = Path("strategy_lab/data/candidates.json")
    add_idea(
        StrategyIdea(
            idea_id="idea_03",
            title="Bollinger Snapback",
            hypothesis="Band compression may create short-term mean reversion entries.",
            source="research_note",
            symbols=["XRPUSDT"],
            timeframe="1D",
            expected_edge="snapback",
            risk_notes="Human approval required",
        )
    )
    candidate = convert_idea_to_candidate("idea_03")
    assert candidate["candidate_id"] == "idea_03"
    assert candidate["status"] == "IDEA"
    assert candidate["lifecycle_state"] == "IDEA"
    loaded = registry_module.get_candidate("idea_03")
    assert loaded["status"] == "IDEA"
    assert loaded["lifecycle_state"] == "IDEA"
    (root / "ideas.json").unlink(missing_ok=True)
    candidate_store.unlink(missing_ok=True)


def test_invalid_empty_hypothesis_rejected(monkeypatch):
    _patch_inbox_roots(monkeypatch, "phase9_invalid")
    with pytest.raises(ValueError):
        add_idea(
            StrategyIdea(
                idea_id="idea_04",
                title="Invalid",
                hypothesis="",
                source="research_note",
            )
        )


def test_no_live_ready_or_live_state_emitted(monkeypatch):
    root = _patch_inbox_roots(monkeypatch, "phase9_livecheck")
    add_idea(
        StrategyIdea(
            idea_id="idea_05",
            title="Trend Following",
            hypothesis="Trend continuation may survive regime shifts.",
            source="research_note",
        )
    )
    candidate = convert_idea_to_candidate("idea_05")
    payload = json.dumps(candidate)
    assert "LIVE_READY" not in payload
    assert candidate["status"] == "IDEA"
    assert candidate["lifecycle_state"] == "IDEA"
    (root / "ideas.json").unlink(missing_ok=True)
    Path("strategy_lab/data/candidates.json").unlink(missing_ok=True)


def test_safety_scan_still_passes():
    source = Path(inbox_module.__file__).read_text(encoding="utf-8").lower()
    for forbidden in ("broker", "place_order", "submit_order", "execute_order", "live execution", "exchange write"):
        assert forbidden not in source

