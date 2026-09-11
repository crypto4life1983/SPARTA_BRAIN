from __future__ import annotations

import io
import sys
import zipfile
from datetime import date
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import refresh_external_binance_15m_cache as rf  # noqa: E402

ROWS = {"15m": 2880, "1m": 43200}  # a 30-day month


def _zip_bytes(symbol: str, month: str, interval: str = "15m", rows: int | None = None,
               member: str | None = None) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr(member or f"{symbol}-{interval}-{month}.csv", "1,2,3\n" * (rows or ROWS[interval]))
    return buf.getvalue()


def _cache(root: Path, months: dict[str, list[str]]) -> Path:
    """months keyed by cache dir name, e.g. 'BTCUSDT' (15m) or 'BTCUSDT_1m'."""
    for key, ms in months.items():
        d = root / key
        d.mkdir(parents=True)
        for m in ms:
            (d / f"{m}.zip").write_bytes(b"PK")
    return root


def _fake_fetch(calls: list[str]):
    def fetch(url: str) -> bytes:
        calls.append(url)
        parts = url.split("/klines/")[1].split("/")  # sym, interval, file
        sym, interval = parts[0], parts[1]
        month = url[-11:-4]
        return _zip_bytes(sym, month, interval)
    return fetch


def test_months_between_and_last_full_month():
    assert rf.months_between("2025-11", "2026-02") == ["2025-11", "2025-12", "2026-01", "2026-02"]
    assert rf.last_full_month(date(2026, 9, 10)) == "2026-08"
    assert rf.last_full_month(date(2026, 1, 5)) == "2025-12"


def test_missing_months_only_after_newest_cached(tmp_path: Path):
    cache = _cache(tmp_path, {"BTCUSDT": ["2026-02", "2026-03"]})
    assert rf.missing_months(cache, "BTCUSDT", "2026-05") == ["2026-04", "2026-05"]
    assert rf.missing_months(cache, "BTCUSDT", "2026-03") == []
    assert rf.missing_months(cache, "NOPE", "2026-05") == []  # absent dir: never created


def test_validate_rejects_wrong_member_and_row_count():
    with pytest.raises(ValueError):
        rf.validate_zip_bytes(_zip_bytes("BTCUSDT", "2026-04", member="other.csv"), "BTCUSDT", "2026-04")
    with pytest.raises(ValueError):
        rf.validate_zip_bytes(_zip_bytes("BTCUSDT", "2026-04", rows=10), "BTCUSDT", "2026-04")
    assert rf.validate_zip_bytes(_zip_bytes("BTCUSDT", "2026-04"), "BTCUSDT", "2026-04") == 2880
    # 1m bounds are different: a 15m-sized file must be rejected as 1m
    with pytest.raises(ValueError):
        rf.validate_zip_bytes(_zip_bytes("BTCUSDT", "2026-04", "1m", rows=2880), "BTCUSDT", "2026-04", "1m")
    assert rf.validate_zip_bytes(_zip_bytes("BTCUSDT", "2026-04", "1m"), "BTCUSDT", "2026-04", "1m") == 43200


def test_refresh_fills_both_intervals_and_never_overwrites(tmp_path: Path):
    cache = _cache(tmp_path, {"BTCUSDT": ["2026-03"], "BTCUSDT_1m": ["2026-04"], "ETHUSDT_1m": ["2026-05"]})
    calls: list[str] = []
    before = (cache / "BTCUSDT" / "2026-03.zip").read_bytes()
    res = rf.refresh(cache_root=cache, symbols=("BTCUSDT", "ETHUSDT"), end_month="2026-05",
                     fetch=_fake_fetch(calls), sleep_s=0)
    assert res["status"] == "OK"
    got = {(d["symbol"], d["interval"], d["month"]) for d in res["downloaded"]}
    assert got == {
        ("BTCUSDT", "15m", "2026-04"), ("BTCUSDT", "15m", "2026-05"),
        ("BTCUSDT", "1m", "2026-05"),
    }  # ETHUSDT has no 15m dir and its 1m dir is already current
    assert (cache / "BTCUSDT" / "2026-03.zip").read_bytes() == before
    assert (cache / "BTCUSDT_1m" / "2026-05.zip").exists()
    assert any("/1m/" in c for c in calls) and any("/15m/" in c for c in calls)
    assert len(calls) == 3


def test_refresh_dry_run_writes_nothing(tmp_path: Path):
    cache = _cache(tmp_path, {"BTCUSDT_1m": ["2026-03"]})
    res = rf.refresh(cache_root=cache, symbols=("BTCUSDT",), end_month="2026-04",
                     dry_run=True, fetch=lambda u: (_ for _ in ()).throw(AssertionError("no fetch")))
    assert res["planned"] == ["BTCUSDT_1m/2026-04"]
    assert not (cache / "BTCUSDT_1m" / "2026-04.zip").exists()


def test_refresh_reports_failed_month_without_writing(tmp_path: Path):
    cache = _cache(tmp_path, {"XRPUSDT": ["2026-07"]})

    def bad_fetch(url: str) -> bytes:
        raise OSError("HTTP 404")

    res = rf.refresh(cache_root=cache, symbols=("XRPUSDT",), end_month="2026-08",
                     fetch=bad_fetch, sleep_s=0)
    assert res["status"] == "PARTIAL"
    assert res["failed"][0]["month"] == "2026-08"
    assert not (cache / "XRPUSDT" / "2026-08.zip").exists()
