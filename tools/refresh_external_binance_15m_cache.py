"""Additive monthly refresh of the external paper bot's Binance 15m kline cache.

The frozen-stack paper bot in C:\\Users\\mahmo\\obsidian-trade-logger loads daily bars by
aggregating monthly zips from ``data/binance_cache/<SYMBOL>/YYYY-MM.zip``. Between
2026-03 and 2026-09 nothing refreshed that cache, so the bot ran daily on stale data and
appended zero trades. This tool downloads only the MISSING months from Binance's free
public archive (data.binance.vision, no API key, no account, no trading endpoint) and
never overwrites an existing file.

Safety contract:
  * read-only against the external project except for writing NEW monthly zip files into
    the cache directory; nothing else is touched;
  * no credentials, no exchange API, no orders;
  * every download is validated (single CSV member with the expected name, plausible row
    count) before it is written; a failed validation is skipped and reported.

CLI:
    python tools/refresh_external_binance_15m_cache.py            # fill gaps up to last full month
    python tools/refresh_external_binance_15m_cache.py --dry-run  # report what would be fetched
"""
from __future__ import annotations

import argparse
import io
import json
import sys
import time
import urllib.request
import zipfile
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

EXTERNAL_ROOT = Path(r"C:\Users\mahmo\obsidian-trade-logger")
CACHE_ROOT = EXTERNAL_ROOT / "data" / "binance_cache"
SYMBOLS = ("BTCUSDT", "ETHUSDT", "XRPUSDT")
URL = "https://data.binance.vision/data/spot/monthly/klines/{sym}/15m/{sym}-15m-{y}-{m:02d}.zip"
REPORT_DIR = ROOT / "reports" / "binance_cache_refresh"
MIN_ROWS, MAX_ROWS = 2500, 3000  # 15m bars in a month: 28..31 days x 96


def months_between(start: str, end: str) -> list[str]:
    """Inclusive list of YYYY-MM strings from start to end."""
    y, m = (int(x) for x in start.split("-"))
    ey, em = (int(x) for x in end.split("-"))
    out: list[str] = []
    while (y, m) <= (ey, em):
        out.append(f"{y}-{m:02d}")
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


def last_full_month(today: date | None = None) -> str:
    today = today or datetime.now(timezone.utc).date()
    y, m = today.year, today.month - 1
    if m == 0:
        y, m = y - 1, 12
    return f"{y}-{m:02d}"


def missing_months(cache_root: Path, symbol: str, end_month: str) -> list[str]:
    """Months after the newest cached zip up to end_month (empty if cache absent)."""
    sym_dir = cache_root / symbol
    if not sym_dir.exists():
        return []
    cached = sorted(p.stem for p in sym_dir.glob("????-??.zip"))
    if not cached:
        return []
    newest = cached[-1]
    if newest >= end_month:
        return []
    y, m = (int(x) for x in newest.split("-"))
    m += 1
    if m == 13:
        y, m = y + 1, 1
    return months_between(f"{y}-{m:02d}", end_month)


def validate_zip_bytes(data: bytes, symbol: str, month: str) -> int:
    """Return row count if the zip is a valid Binance monthly 15m kline file, else raise."""
    z = zipfile.ZipFile(io.BytesIO(data))
    names = z.namelist()
    expected = f"{symbol}-15m-{month}.csv"
    if names != [expected]:
        raise ValueError(f"unexpected members {names}, expected [{expected}]")
    rows = z.read(expected).decode("utf-8", "replace").count("\n")
    if not (MIN_ROWS <= rows <= MAX_ROWS):
        raise ValueError(f"row count {rows} outside [{MIN_ROWS}, {MAX_ROWS}]")
    return rows


def refresh(
    cache_root: Path = CACHE_ROOT,
    symbols: tuple[str, ...] = SYMBOLS,
    end_month: str | None = None,
    dry_run: bool = False,
    fetch=None,
    sleep_s: float = 0.3,
) -> dict:
    """Download missing months per symbol. `fetch(url) -> bytes` is injectable for tests."""
    end_month = end_month or last_full_month()
    fetch = fetch or (lambda url: urllib.request.urlopen(url, timeout=60).read())
    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "cache_root": str(cache_root),
        "end_month": end_month,
        "dry_run": dry_run,
        "downloaded": [],
        "skipped_existing": [],
        "failed": [],
        "planned": [],
        "read_only_external": True,
        "no_credentials": True,
        "no_orders": True,
    }
    for symbol in symbols:
        for month in missing_months(cache_root, symbol, end_month):
            dest = cache_root / symbol / f"{month}.zip"
            if dest.exists():
                result["skipped_existing"].append(f"{symbol}/{month}")
                continue
            result["planned"].append(f"{symbol}/{month}")
            if dry_run:
                continue
            y, m = (int(x) for x in month.split("-"))
            url = URL.format(sym=symbol, y=y, m=m)
            try:
                data = fetch(url)
                rows = validate_zip_bytes(data, symbol, month)
                dest.write_bytes(data)
                result["downloaded"].append({"symbol": symbol, "month": month, "rows": rows})
            except Exception as exc:  # network error, 404 (month not published), bad zip
                result["failed"].append({"symbol": symbol, "month": month, "error": str(exc)[:160]})
            if sleep_s:
                time.sleep(sleep_s)
    result["status"] = "OK" if not result["failed"] else "PARTIAL"
    return result


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--end-month", default=None, help="YYYY-MM (default: last full month)")
    args = ap.parse_args(argv)
    res = refresh(end_month=args.end_month, dry_run=args.dry_run)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    (REPORT_DIR / "latest.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    with (REPORT_DIR / "history.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({k: res[k] for k in ("generated_at", "end_month", "status", "downloaded", "failed")}) + "\n")
    print(json.dumps(res, indent=2))
    return 0 if res["status"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
