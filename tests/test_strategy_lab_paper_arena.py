from __future__ import annotations

from pathlib import Path

import strategy_lab.paper_arena as arena_module
from strategy_lab.paper_arena import PaperArenaConfig, PaperArenaSnapshot, create_paper_arena, load_paper_arena, update_paper_snapshot


def test_paper_arena_creation():
    arena = create_paper_arena(
        PaperArenaConfig(
            candidate_id="cand_01",
            symbol="BTCUSDT",
            timeframe="1D",
            start_date="2024-01-01",
            initial_equity=100000.0,
            max_simulated_risk_per_trade=0.01,
        )
    )
    assert arena["candidate_id"] == "cand_01"
    assert arena["symbol"] == "BTCUSDT"
    assert arena["status"] == "EXPERIMENTAL"


def test_loading_snapshot():
    arena = load_paper_arena("cand_01")
    assert arena["candidate_id"] == "cand_01"


def test_updating_simulated_snapshot():
    snapshot = update_paper_snapshot(
        "cand_01",
        PaperArenaSnapshot(
            candidate_id="cand_01",
            symbol="BTCUSDT",
            simulated_equity=101250.0,
            simulated_open_positions=1,
            simulated_closed_trades=2,
            simulated_drawdown=0.03,
            status="EXPERIMENTAL",
            notes="first simulated update",
        ),
    )
    assert snapshot["candidate_id"] == "cand_01"
    assert snapshot["snapshots"][-1]["simulated_equity"] == 101250.0
    assert snapshot["snapshots"][-1]["simulated_closed_trades"] == 2


def test_output_path_remains_inside_paper_arena_root():
    root = Path("strategy_lab/data/paper_arena")
    assert root.resolve().is_relative_to(Path("strategy_lab/data").resolve())
    store = load_paper_arena()
    assert "arenas" in store
    assert "schema_version" in store


def test_safety_scan_still_passes():
    source = Path(arena_module.__file__).read_text(encoding="utf-8").lower()
    for forbidden in ("broker", "place_order", "submit_order", "execute_order", "live execution", "exchange"):
        assert forbidden not in source


def test_no_forbidden_live_execution_words_in_public_api():
    source = Path(arena_module.__file__).read_text(encoding="utf-8").lower()
    assert "order" not in source
    assert "execute" not in source

