"""Bounded BROAD-UNIVERSE Binance daily klines fetcher (C23/C24 sleeve research).

A SEPARATE, dedicated fetcher for a bounded broad crypto daily frozen dataset, used ONLY for
exploratory C23 (low-vol) / C24 (illiquidity) cross-sectional portfolio-sleeve feasibility.
It does NOT modify and does NOT import the canonical 3-symbol fetcher
(`tools/fetch_binance_crypto_daily_frozen.py`), whose narrow allowlist stays intact as a
separate safety surface.

Public Binance daily market data ONLY:
- network surface restricted to https://api.binance.com/api/v3/klines
- symbols restricted to the human-approved BROAD allowlist below (42 names)
- interval restricted to 1d
- every URL passes `_assert_safe_url`, which rejects forbidden fragments
  (account / order / trade / userdata / signed / signature / apikey / secret)
- NO API key, NO signed endpoints, NO account endpoints, NO trading/broker/paper/live code
- reads NO environment variables or secrets
- writes ONLY into data/broad_crypto_universe_c23_c24/

It captures daily OHLCV + the quote-asset (USDT, i.e. DOLLAR) volume needed for C24's Amihud
illiquidity ratio. Missing candles are RECORDED, never forward-filled. Unavailable / delisted
/ short-history symbols are EXCLUDED with a recorded reason and never auto-substituted. Every
frozen output is SHA-256 pinned in a manifest + quality report.

SURVIVORSHIP NOTE (recorded in the manifest): Binance-public klines only return history for
CURRENTLY-LISTED symbols, so this universe carries survivorship bias. It is approved for
EXPLORATORY C23/C24 feasibility ONLY -- NOT sufficient for paper/live approval, which requires
a separate survivorship-aware / paid-data validation phase.

This tool runs NO strategy evaluation, NO labels, NO replay/backtest, NO optimization, NO
candidate activation/promotion, and NO commit/push.
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
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

REPO_ROOT = Path(__file__).resolve().parents[1]

BINANCE_PUBLIC_KLINES_URL = "https://api.binance.com/api/v3/klines"
ALLOWED_URL_PREFIXES = (BINANCE_PUBLIC_KLINES_URL,)
FORBIDDEN_URL_FRAGMENTS = (
    "account", "order", "trade", "userdata", "signed", "signature", "apikey", "secret",
)

# Human-approved BROAD allowlist (42 names). Any change requires fresh explicit authorization.
ALLOWED_SYMBOLS = (
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT", "TRXUSDT",
    "LINKUSDT", "AVAXUSDT", "DOTUSDT", "LTCUSDT", "BCHUSDT", "UNIUSDT", "ATOMUSDT", "ETCUSDT",
    "XLMUSDT", "ICPUSDT", "AAVEUSDT", "NEARUSDT", "FILUSDT", "ALGOUSDT", "VETUSDT", "XTZUSDT",
    "THETAUSDT", "HBARUSDT", "EGLDUSDT", "EOSUSDT", "ZECUSDT", "MANAUSDT", "SANDUSDT", "CHZUSDT",
    "ENJUSDT", "ZILUSDT", "KAVAUSDT", "RUNEUSDT", "GRTUSDT", "CRVUSDT", "SNXUSDT", "COMPUSDT",
    "MKRUSDT", "YFIUSDT",
)
ALLOWED_INTERVAL = "1d"
MAX_LIMIT = 1000
SAFETY_ITER_CAP = 200
OUTPUT_SUBDIR = "data/broad_crypto_universe_c23_c24"
_USER_AGENT = "SPARTA-BroadUniverse-Frozen-Fetcher/1 (public-market-data-only)"

# minimum daily rows for a symbol to enter the PRIMARY universe (else excluded: short history)
MIN_PRIMARY_ROWS = 365


class BroadFetchError(Exception):
    pass


def _normalize_for_url_check(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


def _assert_safe_url(url: str) -> None:
    if not isinstance(url, str) or not url:
        raise BroadFetchError("url must be a non-empty string")
    if not any(url.startswith(p) for p in ALLOWED_URL_PREFIXES):
        raise BroadFetchError("refusing non-allowlisted url: %s" % url)
    norm = _normalize_for_url_check(url)
    for frag in FORBIDDEN_URL_FRAGMENTS:
        if frag in norm:
            raise BroadFetchError("refusing url containing forbidden fragment %r" % frag)


def _http_get_json(url: str, timeout: float = 30.0) -> Any:
    _assert_safe_url(url)
    req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT}, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read()
    return json.loads(body.decode("utf-8"))


def _build_url(symbol: str, interval: str, start_ms: int, end_ms: int, limit: int) -> str:
    return ("%s?symbol=%s&interval=%s&startTime=%d&endTime=%d&limit=%d"
            % (BINANCE_PUBLIC_KLINES_URL, symbol, interval, start_ms, end_ms, limit))


_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _parse_date(s: str) -> datetime:
    if not isinstance(s, str) or not _DATE_RE.match(s):
        raise BroadFetchError("invalid date %r (want YYYY-MM-DD)" % s)
    return datetime.strptime(s, "%Y-%m-%d").replace(tzinfo=timezone.utc)


def _start_ms(s: str) -> int:
    return int(_parse_date(s).timestamp() * 1000)


def _end_ms(s: str) -> int:
    d = _parse_date(s).replace(hour=23, minute=59, second=59, microsecond=999000)
    return int(d.timestamp() * 1000)


def _ms_to_date(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000.0, tz=timezone.utc).strftime("%Y-%m-%d")


def _fmt(x: Any) -> str:
    s = ("%.10f" % float(x)).rstrip("0").rstrip(".")
    return s if s else "0"


def fetch_klines(symbol: str, interval: str, start_ms: int, end_ms: int,
                 http_get: Callable[[str], Any] | None = None) -> list[list]:
    """Paginate the public klines endpoint. Inject `http_get` for tests."""
    if symbol not in ALLOWED_SYMBOLS:
        raise BroadFetchError("symbol %r not in approved broad allowlist" % symbol)
    if interval != ALLOWED_INTERVAL:
        raise BroadFetchError("only %s interval supported" % ALLOWED_INTERVAL)
    if http_get is None:
        http_get = _http_get_json
    out: list[list] = []
    seen: set[int] = set()
    cursor = start_ms
    iters = 0
    while cursor <= end_ms:
        iters += 1
        if iters > SAFETY_ITER_CAP:
            raise BroadFetchError("pagination exceeded safety cap")
        url = _build_url(symbol, interval, cursor, end_ms, MAX_LIMIT)
        _assert_safe_url(url)
        page = http_get(url)
        if not isinstance(page, list):
            raise BroadFetchError("expected JSON array, got %s" % type(page).__name__)
        if not page:
            break
        last_ot = None
        added = 0
        for k in page:
            if not isinstance(k, list) or len(k) < 8:
                raise BroadFetchError("malformed kline (need >=8 fields): %r" % (k,))
            ot = int(k[0])
            last_ot = ot
            if ot in seen or ot > end_ms:
                continue
            float(k[1]); float(k[2]); float(k[3])
            if float(k[4]) <= 0:
                raise BroadFetchError("non-positive close at %s" % _ms_to_date(ot))
            float(k[5]); float(k[7])
            seen.add(ot)
            out.append(k)
            added += 1
        if last_ot is None:
            break
        nxt = last_ot + 1
        if nxt <= cursor or added == 0 or len(page) < MAX_LIMIT:
            break
        cursor = nxt
    out.sort(key=lambda k: int(k[0]))
    return out


def _out_dir() -> Path:
    d = (REPO_ROOT / OUTPUT_SUBDIR / "raw").resolve()
    base = (REPO_ROOT / OUTPUT_SUBDIR).resolve()
    d.relative_to(base)  # containment
    return d


def _hash_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def write_canonical_csv(klines: list[list], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["date", "open", "high", "low", "close", "volume", "quote_volume"])
        prev = None
        for k in klines:
            d = _ms_to_date(int(k[0]))
            if d == prev:
                raise BroadFetchError("duplicate daily bar at %s" % d)
            w.writerow([d, _fmt(k[1]), _fmt(k[2]), _fmt(k[3]), _fmt(k[4]),
                        _fmt(k[5]), _fmt(k[7])])
            prev = d


def _missing_candles(klines: list[list]) -> int:
    if len(klines) < 2:
        return 0
    dates = sorted(datetime.strptime(_ms_to_date(int(k[0])), "%Y-%m-%d") for k in klines)
    span = (dates[-1] - dates[0]).days + 1
    return max(0, span - len(dates))


def fetch_symbol(symbol: str, start: str, end: str,
                 http_get: Callable[[str], Any] | None = None) -> dict[str, Any]:
    """Fetch + freeze one symbol. Returns an inclusion record or an exclusion record."""
    try:
        kl = fetch_klines(symbol, ALLOWED_INTERVAL, _start_ms(start), _end_ms(end),
                          http_get=http_get)
    except (BroadFetchError, urllib.error.URLError, ValueError) as exc:
        return {"symbol": symbol, "included": False,
                "reason": "fetch_error:%s" % type(exc).__name__, "detail": str(exc)[:160]}
    if not kl:
        return {"symbol": symbol, "included": False,
                "reason": "no_data_unavailable_or_delisted", "rows": 0}
    rows = len(kl)
    first, last = _ms_to_date(int(kl[0][0])), _ms_to_date(int(kl[-1][0]))
    missing = _missing_candles(kl)
    short = rows < MIN_PRIMARY_ROWS
    if short:
        return {"symbol": symbol, "included": False,
                "reason": "short_history_below_%d_rows" % MIN_PRIMARY_ROWS,
                "rows": rows, "first_date": first, "last_date": last}
    out_path = _out_dir() / ("%s_1d.csv" % symbol)
    write_canonical_csv(kl, out_path)
    return {"symbol": symbol, "included": True,
            "path": str(out_path.relative_to(REPO_ROOT)).replace("\\", "/"),
            "rows": rows, "first_date": first, "last_date": last,
            "missing_candles": missing, "sha256": _hash_file(out_path),
            "started_after_range": first > start}


def assemble_universe(start: str, end: str, symbols: tuple = ALLOWED_SYMBOLS,
                      http_get: Callable[[str], Any] | None = None,
                      polite_delay: float = 0.25) -> dict[str, Any]:
    included, excluded = [], []
    for s in symbols:
        rec = fetch_symbol(s, start, end, http_get=http_get)
        (included if rec.get("included") else excluded).append(rec)
        if http_get is None and polite_delay:
            time.sleep(polite_delay)
    manifest = {
        "dataset": "broad_crypto_universe_c23_c24",
        "purpose": "EXPLORATORY C23 low-vol / C24 illiquidity cross-sectional sleeve "
                   "feasibility ONLY",
        "source": "binance_public_spot_klines",
        "endpoint": BINANCE_PUBLIC_KLINES_URL,
        "interval": ALLOWED_INTERVAL,
        "assembled_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "requested_date_range": {"start": start, "end": end},
        "approved_symbol_count": len(symbols),
        "included_symbol_count": len(included),
        "excluded_symbol_count": len(excluded),
        "included": sorted(included, key=lambda r: r["symbol"]),
        "excluded": sorted(excluded, key=lambda r: r["symbol"]),
        "fields": ["date", "open", "high", "low", "close", "volume", "quote_volume"],
        "quote_volume_is_dollar_volume_for_amihud": True,
        "no_forward_fill": True,
        "survivorship_bias": "PRESENT (Binance-public currently-listed only); EXPLORATORY "
                             "ONLY; NOT sufficient for paper/live; survivorship-aware "
                             "validation required before any deployment",
        "immutability": "frozen raw CSVs are write-once; re-run requires explicit overwrite",
    }
    return manifest


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Assemble bounded broad crypto daily frozen "
                                             "universe (public Binance klines only).")
    ap.add_argument("--start", default="2021-01-01")
    ap.add_argument("--end", default="2026-06-21")
    args = ap.parse_args(argv)

    raw = _out_dir()
    if raw.exists() and any(raw.glob("*.csv")):
        print("ERROR: raw outputs already exist; refusing to overwrite frozen data: %s" % raw,
              file=sys.stderr)
        return 1
    manifest = assemble_universe(args.start, args.end)

    base = _out_dir().parent
    man_p = base / "manifest.json"
    qa_p = base / "quality_report.json"
    man_p.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    qa = {
        "included_count": manifest["included_symbol_count"],
        "excluded_count": manifest["excluded_symbol_count"],
        "exclusions": [{k: r.get(k) for k in ("symbol", "reason", "rows", "first_date",
                                              "last_date")} for r in manifest["excluded"]],
        "short_histories": [r["symbol"] for r in manifest["included"]
                            if r.get("started_after_range")],
        "missing_candle_summary": {r["symbol"]: r.get("missing_candles", 0)
                                   for r in manifest["included"]},
        "total_missing_candles": sum(r.get("missing_candles", 0)
                                     for r in manifest["included"]),
    }
    qa_p.write_text(json.dumps(qa, indent=2, sort_keys=True), encoding="utf-8")
    manifest["manifest_sha256"] = _hash_file(man_p)
    manifest["quality_report_sha256"] = _hash_file(qa_p)

    print("included=%d excluded=%d" % (manifest["included_symbol_count"],
                                       manifest["excluded_symbol_count"]))
    print("manifest: %s" % man_p.relative_to(REPO_ROOT))
    print("manifest_sha256: %s" % manifest["manifest_sha256"])
    print("quality_report_sha256: %s" % manifest["quality_report_sha256"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
