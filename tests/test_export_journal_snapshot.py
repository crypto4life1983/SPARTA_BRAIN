"""Tests for tools/export_journal_snapshot.py — read-only journal snapshot.

Coverage (per the approval spec):
  1. Export creates JSON and MD pair.
  2. Snapshot includes OBSERVATION_ONLY when closed_trades < 30.
  3. Snapshot includes stale-SI warning when present.
  4. Snapshot includes D/D2/F2/G closed counts from live DB fixture.
  5. Snapshot does NOT write to the real trades.db.
  6. Snapshot does NOT touch external trading project files.

Plus a sanity check that all five required posture phrases appear in
the rendered Markdown (READ ONLY, OBSERVATION ONLY,
NO LIVE READINESS CLAIM, NO STRATEGY APPROVAL,
NO BROKER / NO ORDER / NO OPTIMIZATION).
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest


_REPO_ROOT = Path(__file__).resolve().parents[1]
_REAL_EXTERNAL_DB = Path(r"C:\Users\mahmo\obsidian-trade-logger\data\trades.db")


# --- fixture data -----------------------------------------------------------

_FAKE_SI = {
    "generated_at": "2026-05-04T21:46:51.562257+00:00",
    "per_strategy": {
        "D2": {"closed_trades": 0, "total_trades": 2, "open_trades": 2},
        "F2": {"closed_trades": 0, "total_trades": 2, "open_trades": 2},
        "G":  {"closed_trades": 0, "total_trades": 1, "open_trades": 1},
    },
    "per_symbol": {},
    "global": {},
}


def _row(rid, strat, outcome, close_date, pnl_r, pnl_usd, symbol="XRPUSDT"):
    return {
        "id": rid, "exchange": "kraken", "symbol": symbol,
        "strategy": strat,
        "direction": "short" if strat in ("D2", "F2") else "long",
        "entry": 1.0, "sl": 1.05, "size_usd": 100.0,
        "open_date": "2026-04-28",
        "close_date": close_date,
        "outcome": outcome, "pnl_r": pnl_r, "pnl_usd": pnl_usd,
        "max_favorable_R": None, "max_adverse_R": None,
    }


# Mirrors the live DB shape: D=1, D2=2, F2=2, G=2 closed (+1 open) → 7 closed.
_FAKE_ROWS = [
    _row(13, "D2", "LOSS",    "2026-05-15", -1.357, -27.14),
    _row(15, "D2", "LOSS",    "2026-05-15", -1.415, -28.31),
    _row(14, "F2", "LOSS",    "2026-05-15", -1.357, -27.14),
    _row(16, "F2", "LOSS",    "2026-05-15", -1.415, -28.31),
    _row(18, "D",  "LOSS",    "2026-05-18", -1.082, -21.65, symbol="BNBUSDT"),
    _row(17, "G",  "TIMEOUT", "2026-05-19",  0.126,   2.51),
    _row(25, "G",  "LOSS",    "2026-05-23", -0.439,  -8.77),
    _row(99, "G",  None, None, None, None),
]


@pytest.fixture
def patched_adapter(monkeypatch, tmp_path):
    """Point the adapter at an in-test external root with fixture data.

    A separate `ext_dir` subtree is used for the patched external root so
    the output directory `out_dir` can be placed outside it. That lets the
    "does not touch external project" test be a true mtime audit.
    """
    from tools import trade_journal_adapter as _tja

    ext_dir = tmp_path / "ext"
    data_dir = ext_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "trades.db").write_bytes(b"")  # adapter checks .exists()

    monkeypatch.setattr(_tja, "external_root", lambda: ext_dir)
    monkeypatch.setattr(
        _tja,
        "_safe_load_json",
        lambda path: (
            dict(_FAKE_SI)
            if str(path).replace("\\", "/").endswith(
                "strategy_intelligence_report.json"
            )
            else None
        ),
    )
    monkeypatch.setattr(
        _tja, "_read_trades_ro", lambda _db_path: (list(_FAKE_ROWS), None),
    )
    return ext_dir


# --- (1) creates JSON + MD --------------------------------------------------

def test_snapshot_creates_json_and_md(patched_adapter, tmp_path):
    from tools.export_journal_snapshot import export_snapshot

    out_dir = tmp_path / "out"
    json_path, md_path = export_snapshot(out_dir)

    assert json_path.exists(), f"expected JSON file at {json_path}"
    assert md_path.exists(), f"expected MD file at {md_path}"
    assert json_path.name.startswith("journal_snapshot_")
    assert json_path.suffix == ".json"
    assert md_path.name.startswith("journal_snapshot_")
    assert md_path.suffix == ".md"
    # Filenames share the same UTC timestamp stem.
    assert json_path.stem == md_path.stem


# --- (2) OBSERVATION_ONLY ---------------------------------------------------

def test_snapshot_observation_only_with_seven_closed(patched_adapter, tmp_path):
    from tools.export_journal_snapshot import export_snapshot

    out_dir = tmp_path / "out"
    json_path, md_path = export_snapshot(out_dir)

    data = json.loads(json_path.read_text(encoding="utf-8"))
    assert data["evidence_quality"]["final_state"] == "OBSERVATION_ONLY"
    assert data["summary"]["closed_trade_count"] == 7

    md = md_path.read_text(encoding="utf-8")
    assert "OBSERVATION_ONLY" in md           # snake-cased label
    assert "OBSERVATION ONLY" in md           # banner phrasing


# --- (3) stale-SI warning ---------------------------------------------------

def test_snapshot_includes_stale_si_warning(patched_adapter, tmp_path):
    from tools.export_journal_snapshot import export_snapshot

    out_dir = tmp_path / "out"
    json_path, md_path = export_snapshot(out_dir)

    data = json.loads(json_path.read_text(encoding="utf-8"))
    stale_msgs = [
        m for m in data.get("missing", [])
        if "strategy_intelligence_report_stale" in m
    ]
    assert stale_msgs, (
        f"expected stale-SI warning in 'missing' list, got: "
        f"{data.get('missing')}"
    )

    md = md_path.read_text(encoding="utf-8")
    assert "strategy_intelligence_report_stale" in md


# --- (4) live DB closed counts ---------------------------------------------

def test_snapshot_includes_live_db_closed_counts(patched_adapter, tmp_path):
    from tools.export_journal_snapshot import export_snapshot

    out_dir = tmp_path / "out"
    json_path, md_path = export_snapshot(out_dir)

    data = json.loads(json_path.read_text(encoding="utf-8"))
    by_strat = {
        row["strategy"]: row["closed_trades"]
        for row in data["strategy_metrics"]
    }
    assert by_strat.get("D")  == 1, f"D closed = {by_strat.get('D')}"
    assert by_strat.get("D2") == 2, f"D2 closed = {by_strat.get('D2')}"
    assert by_strat.get("F2") == 2, f"F2 closed = {by_strat.get('F2')}"
    assert by_strat.get("G")  == 2, f"G closed = {by_strat.get('G')}"

    md = md_path.read_text(encoding="utf-8")
    for strat in ("D", "D2", "F2", "G"):
        assert strat in md, f"strategy {strat!r} missing from MD"


# --- (5) does not write to real trades.db -----------------------------------

def test_snapshot_does_not_write_to_real_trades_db(patched_adapter, tmp_path):
    """If the real external trades.db is on disk, its mtime and size must
    be byte-identical after the export runs. The adapter's URI mode=ro
    plus the patched `_read_trades_ro` both guarantee no write — this
    audits the guarantee end-to-end."""
    if not _REAL_EXTERNAL_DB.exists():
        pytest.skip(f"real external trades.db not on disk at {_REAL_EXTERNAL_DB}")

    from tools.export_journal_snapshot import export_snapshot

    before_mtime = _REAL_EXTERNAL_DB.stat().st_mtime_ns
    before_size = _REAL_EXTERNAL_DB.stat().st_size

    out_dir = tmp_path / "out"
    export_snapshot(out_dir)

    after_mtime = _REAL_EXTERNAL_DB.stat().st_mtime_ns
    after_size = _REAL_EXTERNAL_DB.stat().st_size
    assert before_mtime == after_mtime, "trades.db mtime changed — write detected"
    assert before_size == after_size, "trades.db size changed — write detected"


# --- (6) does not touch external project files ------------------------------

def test_snapshot_does_not_touch_external_project(patched_adapter, tmp_path):
    """Snapshot the mtime of every file under the patched external root
    before the export, then verify nothing changed afterwards. The output
    directory lives outside that subtree so it doesn't interfere."""
    from tools.export_journal_snapshot import export_snapshot

    ext_dir = patched_adapter
    out_dir = tmp_path / "out"
    assert out_dir != ext_dir
    assert ext_dir not in out_dir.parents

    before: dict[Path, int] = {}
    for path in ext_dir.rglob("*"):
        if path.is_file():
            try:
                before[path] = path.stat().st_mtime_ns
            except OSError:
                pass

    json_path, md_path = export_snapshot(out_dir)

    # Outputs must land under out_dir.
    assert out_dir in json_path.parents
    assert out_dir in md_path.parents

    # Nothing under the patched external root was modified or created.
    for path, mtime in before.items():
        assert path.exists(), f"file disappeared: {path}"
        assert path.stat().st_mtime_ns == mtime, f"file modified: {path}"

    # No NEW files appeared under ext_dir either (no upward escape).
    after: set[Path] = {
        p for p in ext_dir.rglob("*") if p.is_file()
    }
    assert after == set(before.keys()), (
        f"files appeared under external root: {after - set(before.keys())}"
    )


# --- bonus: posture phrases present -----------------------------------------

def test_snapshot_markdown_contains_all_required_posture_phrases(
    patched_adapter, tmp_path
):
    from tools.export_journal_snapshot import export_snapshot

    out_dir = tmp_path / "out"
    _json_path, md_path = export_snapshot(out_dir)
    md = md_path.read_text(encoding="utf-8")

    for phrase in (
        "READ ONLY",
        "OBSERVATION ONLY",
        "NO LIVE READINESS CLAIM",
        "NO STRATEGY APPROVAL",
        "NO BROKER / NO ORDER / NO OPTIMIZATION",
    ):
        assert phrase in md, f"missing posture phrase: {phrase!r}"
