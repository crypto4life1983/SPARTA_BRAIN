"""C18 H4 BTCUSD public read-only fetch one-off runner (SAFE, PUBLIC MARKET DATA
ONLY; RESEARCH ONLY).

Approved via HUMAN_DECISION_APPROVE_C18_H4_BTCUSD_PUBLIC_READONLY_FETCH_RUNNER_BUILD.
Fetches PUBLIC Binance spot klines for BTCUSDT at interval 4h and writes a canonical
FROZEN CSV + SHA256 provenance under the C18 H4 data directory. It is a peer to
tools/fetch_binance_crypto_daily_frozen.py; that tool is interval-locked to 1d, so
this separate runner is the 4h surface for C18.

Public market data only. NO API key. NO signed/account/order/trade/userdata
endpoints. Reads NO environment variables or secrets. Places NO orders. No broker /
exchange SDK, no Telegram/webhook/scheduler. Only BTCUSDT and only interval 4h. No
XAUUSD / no gold. All network access lives inside functions called from main(); there
is NO network call at import time. Building/importing this runner does NOT fetch --
the fetch happens only when main() is executed.

Hard boundaries (verified by AST + source-literal safety tests):
- network surface restricted to https://api.binance.com/api/v3/klines
- symbol restricted to BTCUSDT; interval restricted to 4h
- every URL passes _assert_safe_url, which rejects forbidden fragments
  (account / order / trade / userdata / signed / signature / apikey / secret)
- no credential / env / secret reads; no broker/exchange SDK imports
- writes only into data/h4_trend_following_market_structure_c18/raw/ (gitignored)
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

CANDIDATE_FAMILY = "h4_trend_following_market_structure"
BINANCE_PUBLIC_KLINES_URL = "https://api.binance.com/api/v3/klines"
ALLOWED_URL_PREFIXES = (BINANCE_PUBLIC_KLINES_URL,)
FORBIDDEN_URL_FRAGMENTS = (
    "account", "order", "trade", "userdata", "signed", "signature", "apikey",
    "secret", "withdraw", "deposit", "margin", "futures",
)
ALLOWED_SYMBOL = "BTCUSDT"           # BTCUSD; the only symbol this runner may fetch
ALLOWED_INTERVAL = "4h"              # the only interval this runner may fetch
MAX_LIMIT = 1000
SAFETY_ITER_CAP = 400
_USER_AGENT = "SPARTA-C18-H4-Frozen-Fetcher/1 (public-market-data-only)"

# fixed default window -> deterministic output for the same window
DEFAULT_START = "2019-01-01"
DEFAULT_END = "2026-06-08"

OUT_DIR = REPO_ROOT / "data" / "h4_trend_following_market_structure_c18" / "raw"
OUT_CSV = OUT_DIR / "BTCUSDT_4h.csv"
OUT_PROVENANCE = OUT_DIR / "BTCUSDT_4h.provenance.json"


class FetchSafetyError(Exception):
    """Raised when a safety boundary would be crossed."""


def _normalize_for_url_check(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


def _assert_safe_symbol_interval(symbol: str, interval: str) -> None:
    if symbol != ALLOWED_SYMBOL:
        raise FetchSafetyError("symbol restricted to %s, got %r"
                               % (ALLOWED_SYMBOL, symbol))
    if interval != ALLOWED_INTERVAL:
        raise FetchSafetyError("interval restricted to %s, got %r"
                               % (ALLOWED_INTERVAL, interval))


def _assert_safe_url(url: str) -> None:
    if not isinstance(url, str) or not url:
        raise FetchSafetyError("url must be a non-empty string")
    if not any(url.startswith(p) for p in ALLOWED_URL_PREFIXES):
        raise FetchSafetyError("refusing non-allowlisted url: %s" % url)
    normalized = _normalize_for_url_check(url)
    for frag in FORBIDDEN_URL_FRAGMENTS:
        if frag in normalized:
            raise FetchSafetyError("refusing url with forbidden fragment %r: %s"
                                   % (frag, url))


def _build_url(symbol: str, interval: str, start_ms: int, end_ms: int,
               limit: int) -> str:
    _assert_safe_symbol_interval(symbol, interval)
    return ("%s?symbol=%s&interval=%s&startTime=%d&endTime=%d&limit=%d"
            % (BINANCE_PUBLIC_KLINES_URL, symbol, interval, start_ms, end_ms,
               limit))


def _to_ms(date_str: str) -> int:
    # parse YYYY-MM-DD to epoch ms (UTC) without importing datetime: use a fixed
    # civil-to-days algorithm.
    y, m, d = (int(x) for x in date_str.split("-"))
    # days from civil (Howard Hinnant's algorithm)
    yy = y - (1 if m <= 2 else 0)
    era = (yy if yy >= 0 else yy - 399) // 400
    yoe = yy - era * 400
    doy = (153 * (m + (-3 if m > 2 else 9)) + 2) // 5 + d - 1
    doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
    days = era * 146097 + doe - 719468
    return days * 86400 * 1000


def _http_get_json(url: str, timeout: float = 30.0):
    """Public GET of the allowlisted klines endpoint. Network access lives here,
    never at import time."""
    _assert_safe_url(url)
    req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT},
                                 method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:   # noqa: S310
        body = resp.read()
    return json.loads(body.decode("utf-8"))


def fetch_klines(symbol: str, interval: str, start: str, end: str) -> list:
    """Paginate public klines over [start, end]. Pure-ish: only network egress is
    the allowlisted public GET. Returns canonical OHLCV rows."""
    _assert_safe_symbol_interval(symbol, interval)
    start_ms, end_ms = _to_ms(start), _to_ms(end)
    rows, cursor, iters = [], start_ms, 0
    while cursor < end_ms and iters < SAFETY_ITER_CAP:
        iters += 1
        url = _build_url(symbol, interval, cursor, end_ms, MAX_LIMIT)
        batch = _http_get_json(url)
        if not batch:
            break
        for k in batch:
            ot = int(k[0])
            rows.append({
                "date": time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                      time.gmtime(ot // 1000)),
                "open": float(k[1]), "high": float(k[2]), "low": float(k[3]),
                "close": float(k[4]), "volume": float(k[5]),
                "source": "binance_public_spot_klines_4h", "instrument_type": "spot",
            })
        last_open = int(batch[-1][0])
        nxt = last_open + 1
        if nxt <= cursor:
            break
        cursor = nxt
    # de-dup + sort by date
    seen, out = set(), []
    for r in sorted(rows, key=lambda x: x["date"]):
        if r["date"] not in seen:
            seen.add(r["date"])
            out.append(r)
    return out


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def write_frozen_csv(rows: list, path: Path) -> None:
    cols = ("date", "open", "high", "low", "close", "volume", "source",
            "instrument_type")
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(cols))
        w.writeheader()
        for r in rows:
            w.writerow(r)


def main(argv: list | None = None) -> dict:
    ap = argparse.ArgumentParser(description="C18 H4 BTCUSDT public read-only fetch")
    ap.add_argument("--start", default=DEFAULT_START)
    ap.add_argument("--end", default=DEFAULT_END)
    args = ap.parse_args(argv if argv is not None else [])

    _assert_safe_symbol_interval(ALLOWED_SYMBOL, ALLOWED_INTERVAL)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = fetch_klines(ALLOWED_SYMBOL, ALLOWED_INTERVAL, args.start, args.end)
    if not rows:
        raise FetchSafetyError("no rows returned for the requested window")
    write_frozen_csv(rows, OUT_CSV)
    sha = compute_sha256(OUT_CSV)
    provenance = {
        "candidate_family": CANDIDATE_FAMILY, "symbol": "BTCUSD",
        "binance_symbol": ALLOWED_SYMBOL, "interval": ALLOWED_INTERVAL,
        "path": str(OUT_CSV.relative_to(REPO_ROOT)).replace("\\", "/"),
        "sha256": sha, "row_count": len(rows),
        "window": [args.start, args.end],
        "source": "binance_public_spot_klines_4h",
        "public_market_data_only": True, "no_api_key": True,
        "no_credentials": True,
    }
    with open(OUT_PROVENANCE, "w", encoding="utf-8") as f:
        json.dump(provenance, f, indent=2, sort_keys=True)

    report = {
        "csv_path": provenance["path"], "sha256": sha, "row_count": len(rows),
        "window": [args.start, args.end], "symbol": "BTCUSD",
        "interval": ALLOWED_INTERVAL,
        "provenance_path": str(OUT_PROVENANCE.relative_to(REPO_ROOT)).replace(
            "\\", "/"),
    }
    for k, v in report.items():
        print("%s = %r" % (k, v))
    return report


if __name__ == "__main__":
    main(sys.argv[1:])
