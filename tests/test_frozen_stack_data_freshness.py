"""The frozen-stack cycle must flag a stale Binance cache instead of reporting OK.

Background: between 2026-03 and 2026-09 the external paper bot's kline cache stopped at
March while the daily cycle kept logging paper_bot_status=OK with zero appended rows.
The bot's daily loader reads the 1m cache (<SYMBOL>_1m/); the 15m cache (<SYMBOL>/) feeds
older backtests. Both are checked; a missing 1m cache is treated as stale.
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sparta_commander import frozen_stack_daily_evidence_cycle as cycle  # noqa: E402

TODAY = datetime(2026, 9, 10, tzinfo=timezone.utc)


def _make_cache(root: Path, months_by_key: dict[str, list[str]]) -> Path:
    for key, months in months_by_key.items():
        d = root / "data" / "binance_cache" / key
        d.mkdir(parents=True, exist_ok=True)
        for m in months:
            (d / f"{m}.zip").write_bytes(b"PK")
    return root


def _both(months: list[str]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for s in cycle.FRESHNESS_SYMBOLS:
        out[s] = list(months)
        out[f"{s}_1m"] = list(months)
    return out


def test_stale_cache_is_flagged(tmp_path: Path):
    ext = _make_cache(tmp_path / "ext", _both(["2026-02", "2026-03"]))
    res = cycle._data_freshness_step(external_root=ext, step_dir=tmp_path / "log", today=TODAY)
    assert res["status"] == "STALE_DATA"
    assert res["per_symbol"]["BTCUSDT_1m"]["last_month"] == "2026-03"
    assert res["oldest_symbol_age_days"] > cycle.FRESHNESS_MAX_AGE_DAYS
    assert (tmp_path / "log" / "data_freshness.json").exists()


def test_fresh_cache_is_ok(tmp_path: Path):
    ext = _make_cache(tmp_path / "ext", _both(["2026-07", "2026-08"]))
    res = cycle._data_freshness_step(external_root=ext, step_dir=tmp_path / "log", today=TODAY)
    assert res["status"] == "OK"
    assert res["oldest_symbol_age_days"] == 9  # 2026-09-10 minus month end 2026-09-01


def test_one_stale_symbol_makes_step_stale(tmp_path: Path):
    months = _both(["2026-08"])
    months["XRPUSDT_1m"] = ["2026-03"]
    ext = _make_cache(tmp_path / "ext", months)
    res = cycle._data_freshness_step(external_root=ext, step_dir=tmp_path / "log", today=TODAY)
    assert res["status"] == "STALE_DATA"
    assert res["per_symbol"]["XRPUSDT_1m"]["status"] == "STALE_DATA"
    assert res["per_symbol"]["BTCUSDT_1m"]["status"] == "OK"


def test_fresh_15m_but_stale_1m_is_stale(tmp_path: Path):
    """Regression for 2026-09-10: the 15m cache was refreshed but the bot reads 1m."""
    months = {s: ["2026-08"] for s in cycle.FRESHNESS_SYMBOLS}
    months.update({f"{s}_1m": ["2026-03"] for s in cycle.FRESHNESS_SYMBOLS})
    ext = _make_cache(tmp_path / "ext", months)
    res = cycle._data_freshness_step(external_root=ext, step_dir=tmp_path / "log", today=TODAY)
    assert res["status"] == "STALE_DATA"


def test_missing_1m_dir_is_stale_even_if_15m_fresh(tmp_path: Path):
    ext = _make_cache(tmp_path / "ext", {s: ["2026-08"] for s in cycle.FRESHNESS_SYMBOLS})
    res = cycle._data_freshness_step(external_root=ext, step_dir=tmp_path / "log", today=TODAY)
    assert res["status"] == "STALE_DATA"
    assert res["per_symbol"]["BTCUSDT_1m"]["status"] == "MISSING"


def test_missing_cache_is_reported(tmp_path: Path):
    res = cycle._data_freshness_step(external_root=tmp_path / "nowhere", step_dir=tmp_path / "log", today=TODAY)
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
