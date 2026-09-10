"""The frozen-stack cycle must flag a stale Binance cache instead of reporting OK.

Background: between 2026-03 and 2026-09 the external paper bot's 15m cache stopped at
March while the daily cycle kept logging paper_bot_status=OK with zero appended rows.
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sparta_commander import frozen_stack_daily_evidence_cycle as cycle  # noqa: E402


def _make_cache(root: Path, months_by_symbol: dict[str, list[str]]) -> Path:
    for symbol, months in months_by_symbol.items():
        d = root / "data" / "binance_cache" / symbol
        d.mkdir(parents=True, exist_ok=True)
        for m in months:
            (d / f"{m}.zip").write_bytes(b"PK")
    return root


def test_stale_cache_is_flagged(tmp_path: Path):
    ext = _make_cache(tmp_path / "ext", {s: ["2026-02", "2026-03"] for s in cycle.FRESHNESS_SYMBOLS})
    res = cycle._data_freshness_step(
        external_root=ext, step_dir=tmp_path / "log", today=datetime(2026, 9, 10, tzinfo=timezone.utc)
    )
    assert res["status"] == "STALE_DATA"
    assert res["per_symbol"]["BTCUSDT"]["last_month"] == "2026-03"
    assert res["oldest_symbol_age_days"] > cycle.FRESHNESS_MAX_AGE_DAYS
    assert (tmp_path / "log" / "data_freshness.json").exists()


def test_fresh_cache_is_ok(tmp_path: Path):
    ext = _make_cache(tmp_path / "ext", {s: ["2026-07", "2026-08"] for s in cycle.FRESHNESS_SYMBOLS})
    res = cycle._data_freshness_step(
        external_root=ext, step_dir=tmp_path / "log", today=datetime(2026, 9, 10, tzinfo=timezone.utc)
    )
    assert res["status"] == "OK"
    assert res["oldest_symbol_age_days"] == 9  # 2026-09-10 minus month end 2026-09-01


def test_one_stale_symbol_makes_step_stale(tmp_path: Path):
    ext = _make_cache(
        tmp_path / "ext",
        {"BTCUSDT": ["2026-08"], "ETHUSDT": ["2026-08"], "XRPUSDT": ["2026-03"]},
    )
    res = cycle._data_freshness_step(
        external_root=ext, step_dir=tmp_path / "log", today=datetime(2026, 9, 10, tzinfo=timezone.utc)
    )
    assert res["status"] == "STALE_DATA"
    assert res["per_symbol"]["XRPUSDT"]["status"] == "STALE_DATA"
    assert res["per_symbol"]["BTCUSDT"]["status"] == "OK"


def test_missing_cache_is_reported(tmp_path: Path):
    res = cycle._data_freshness_step(
        external_root=tmp_path / "nowhere", step_dir=tmp_path / "log", today=datetime(2026, 9, 10, tzinfo=timezone.utc)
    )
    assert res["status"] == "MISSING"


def test_snapshot_and_markdown_carry_freshness():
    steps = {
        "paper_bot": {"status": "OK"},
        "data_freshness": {"status": "STALE_DATA", "oldest_symbol_age_days": 162},
        "validation": {"status": "OK"},
    }
    snap = cycle._build_snapshot(steps, {}, {}, {})
    assert snap["data_freshness_status"] == "STALE_DATA"
    assert snap["data_oldest_symbol_age_days"] == 162
    md = cycle._render_markdown({"steps": [], "snapshot": snap})
    assert "data_freshness_status: STALE_DATA" in md
