from __future__ import annotations

import pytest

import strategy_lab.registry as registry
from strategy_lab.registry import build_strategy_library, create_candidate, get_candidate, load_candidates, normalize_strategy_record, update_candidate_state


def test_registry_normalizes_defaults():
    record = normalize_strategy_record({"strategy_id": "donchian_breakout"})
    assert record["strategy_id"] == "donchian_breakout"
    assert record["status"] == "IDEA"
    assert record["name"] == ""
    assert record["symbols_tested"] == []


def test_registry_builds_experimental_library():
    library = build_strategy_library([{"strategy_id": "rsi_reversal", "name": "RSI Reversal"}])
    assert library["mode"] == "EXPERIMENTAL"
    assert library["schema_version"] == "strategy_lab.library.v1"
    assert library["strategies"][0]["strategy_id"] == "rsi_reversal"
    assert library["strategies"][0]["status"] == "IDEA"


def test_registry_candidate_create_load_get_update(tmp_path, monkeypatch):
    monkeypatch.setattr(registry, "DATA_ROOT", tmp_path)
    monkeypatch.setattr(registry, "CANDIDATES_FILE", tmp_path / "candidates.json")

    created = create_candidate({"candidate_id": "donchian_01", "name": "Donchian", "status": "IDEA"})
    assert created["candidate_id"] == "donchian_01"
    assert (tmp_path / "candidates.json").exists()

    loaded = load_candidates()
    assert len(loaded) == 1
    assert get_candidate("donchian_01")["name"] == "Donchian"

    updated = update_candidate_state("donchian_01", "IN_RESEARCH")
    assert updated["status"] == "IN_RESEARCH"
    assert get_candidate("donchian_01")["status"] == "IN_RESEARCH"


def test_registry_invalid_live_transition_blocked(tmp_path, monkeypatch):
    monkeypatch.setattr(registry, "DATA_ROOT", tmp_path)
    monkeypatch.setattr(registry, "CANDIDATES_FILE", tmp_path / "candidates.json")
    create_candidate({"candidate_id": "mean_reversion_01"})
    with pytest.raises(ValueError):
        update_candidate_state("mean_reversion_01", "LIVE")
