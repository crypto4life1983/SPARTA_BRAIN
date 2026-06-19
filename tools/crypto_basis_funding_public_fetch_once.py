"""Crypto spot / perp basis + funding PUBLIC read-only fetch one-off runner
(SAFE, PUBLIC MARKET DATA ONLY; RESEARCH ONLY).

Approved via HUMAN_APPROVED_FETCH_PUBLIC_PERP_SPOT_BASIS_AND_FUNDING_DATA_RESEARCH_ONLY.
Fetches PUBLIC, UNAUTHENTICATED Binance market data for BTCUSDT / ETHUSDT / SOLUSDT:
  * spot daily klines   (https://api.binance.com/api/v3/klines)
  * USDT-perp daily klines (https://fapi.binance.com/fapi/v1/klines)
  * perp funding-rate history (https://fapi.binance.com/fapi/v1/fundingRate)
and writes canonical FROZEN CSVs + SHA256 provenance under a GITIGNORED research
directory. It exists to support a research-only study of spot-perp basis / funding
carry -- the recommended first universe expansion (a mechanically market-neutral,
non-beta return source). It opens NO candidate and runs no detector/labels/replay.

PUBLIC MARKET DATA ONLY. NO API key. NO credentials. Reads NO environment variables or
secrets. NO signed / account / order / trade / userdata / private endpoints. NO broker
/ exchange SDK, no Telegram / webhook / scheduler. Only BTCUSDT / ETHUSDT / SOLUSDT and
only interval 1d (+ funding history). No XAUUSD / no gold. All network access lives
inside functions called from main(); there is NO network call at import time. Building
/ importing this runner does NOT fetch -- the fetch happens only when main() runs.

Hard boundaries (verified by AST + source-literal safety tests):
  * network surface restricted to the three PUBLIC market-data URL prefixes below;
  * every URL passes _assert_safe_url, which requires an allowed prefix AND rejects
    forbidden fragments (account / order / trade / userdata / signed / signature /
    apikey / secret / withdraw / deposit / listenkey / private);
  * symbols restricted to BTCUSDT / ETHUSDT / SOLUSDT; interval restricted to 1d;
  * no credential / env / secret reads; no broker/exchange SDK imports;
  * writes only into data/crypto_basis_funding_research/raw/ (gitignored).
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

SPOT_KLINES_URL = "https://api.binance.com/api/v3/klines"
PERP_KLINES_URL = "https://fapi.binance.com/fapi/v1/klines"
FUNDING_URL = "https://fapi.binance.com/fapi/v1/fundingRate"
ALLOWED_URL_PREFIXES = (SPOT_KLINES_URL, PERP_KLINES_URL, FUNDING_URL)
FORBIDDEN_URL_FRAGMENTS = (
    "account", "order", "trade", "userdata", "signed", "signature", "apikey",
    "apisecret", "secret", "withdraw", "deposit", "listenkey", "private", "margin",
)
ALLOWED_SYMBOLS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
ALLOWED_INTERVAL = "1d"
MAX_LIMIT = 1000
SAFETY_ITER_CAP = 600
_USER_AGENT = "SPARTA-Basis-Funding-Frozen-Fetcher/1 (public-market-data-only)"

DEFAULT_START = "2020-01-01"
DEFAULT_END = "2026-06-08"

OUT_DIR = REPO_ROOT / "data" / "crypto_basis_funding_research" / "raw"
MANIFEST_PATH = OUT_DIR / "fetch_manifest.json"


class FetchSafetyError(Exception):
    """Raised when a safety boundary would be crossed."""


def _normalize_for_url_check(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


def _assert_safe_url(url: str) -> None:
    if not any(url.startswith(p) for p in ALLOWED_URL_PREFIXES):
        raise FetchSafetyError("url not in the public market-data allowlist: %s" % url)
    norm = _normalize_for_url_check(url)
    for frag in FORBIDDEN_URL_FRAGMENTS:
        if frag in norm:
            raise FetchSafetyError("forbidden url fragment %r in %s" % (frag, url))


def _assert_safe_symbol_interval(symbol: str, interval: str) -> None:
    if symbol not in ALLOWED_SYMBOLS:
        raise FetchSafetyError("symbol not allowed: %s" % symbol)
    if interval != ALLOWED_INTERVAL:
        raise FetchSafetyError("interval not allowed: %s" % interval)


def _to_ms(date_str: str) -> int:
    y, m, d = (int(x) for x in date_str.split("-"))
    return int(time.mktime(time.struct_time((y, m, d, 0, 0, 0, 0, 0, 0))) * 1000)


def _http_get_json(url: str, params: dict) -> list:
    """Public GET only -- the URL is asserted safe; no headers carry any credential."""
    query = "&".join("%s=%s" % (k, v) for k, v in params.items())
    full = "%s?%s" % (url, query)
    _assert_safe_url(full)
    req = urllib.request.Request(full, headers={"User-Agent": _USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:   # nosec - public allowlist
        return json.loads(resp.read().decode("utf-8"))


def _fetch_klines(base_url: str, symbol: str, interval: str, start_ms: int,
                  end_ms: int) -> list:
    _assert_safe_symbol_interval(symbol, interval)
    rows, cursor, it = {}, start_ms, 0
    while cursor < end_ms and it < SAFETY_ITER_CAP:
        it += 1
        batch = _http_get_json(base_url, {
            "symbol": symbol, "interval": interval, "startTime": cursor,
            "endTime": end_ms, "limit": MAX_LIMIT})
        if not batch:
            break
        for k in batch:
            ot = int(k[0])
            rows[ot] = (ot, float(k[1]), float(k[2]), float(k[3]), float(k[4]),
                        float(k[5]))
        last = int(batch[-1][0])
        nxt = last + 1
        if nxt <= cursor:
            break
        cursor = nxt
        if len(batch) < MAX_LIMIT:
            break
    return [rows[k] for k in sorted(rows)]


def _fetch_funding(symbol: str, start_ms: int, end_ms: int) -> list:
    if symbol not in ALLOWED_SYMBOLS:
        raise FetchSafetyError("symbol not allowed: %s" % symbol)
    rows, cursor, it = {}, start_ms, 0
    while cursor < end_ms and it < SAFETY_ITER_CAP:
        it += 1
        batch = _http_get_json(FUNDING_URL, {
            "symbol": symbol, "startTime": cursor, "endTime": end_ms,
            "limit": MAX_LIMIT})
        if not batch:
            break
        for f in batch:
            ft = int(f["fundingTime"])
            rows[ft] = (ft, symbol, float(f["fundingRate"]),
                        float(f.get("markPrice") or 0.0))
        last = int(batch[-1]["fundingTime"])
        nxt = last + 1
        if nxt <= cursor:
            break
        cursor = nxt
        if len(batch) < MAX_LIMIT:
            break
    return [rows[k] for k in sorted(rows)]


def _ms_to_date(ms: int) -> str:
    t = time.gmtime(ms / 1000.0)
    return time.strftime("%Y-%m-%d", t)


def _ms_to_datetime(ms: int) -> str:
    t = time.gmtime(ms / 1000.0)
    return time.strftime("%Y-%m-%d %H:%M:%S", t)


def _write_klines_csv(path: Path, rows: list, source: str, inst: str) -> None:
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["date", "open", "high", "low", "close", "volume", "source",
                    "instrument_type"])
        for ot, o, h, lo, c, v in rows:
            w.writerow([_ms_to_date(ot), o, h, lo, c, v, source, inst])


def _write_funding_csv(path: Path, rows: list) -> None:
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["datetime", "funding_time_ms", "symbol", "funding_rate",
                    "mark_price"])
        for ft, sym, fr, mp in rows:
            w.writerow([_ms_to_datetime(ft), ft, sym, fr, mp])


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main(argv: list | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Public Binance spot/perp/funding frozen fetch (research-only).")
    parser.add_argument("--start", default=DEFAULT_START)
    parser.add_argument("--end", default=DEFAULT_END)
    args = parser.parse_args(argv)

    start_ms, end_ms = _to_ms(args.start), _to_ms(args.end)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest: dict = {"window": [args.start, args.end], "symbols": list(ALLOWED_SYMBOLS),
                      "interval": ALLOWED_INTERVAL, "files": {}}

    for sym in ALLOWED_SYMBOLS:
        spot = _fetch_klines(SPOT_KLINES_URL, sym, ALLOWED_INTERVAL, start_ms, end_ms)
        perp = _fetch_klines(PERP_KLINES_URL, sym, ALLOWED_INTERVAL, start_ms, end_ms)
        funding = _fetch_funding(sym, start_ms, end_ms)

        spot_path = OUT_DIR / ("%s_spot_1d.csv" % sym)
        perp_path = OUT_DIR / ("%s_perp_1d.csv" % sym)
        fund_path = OUT_DIR / ("%s_funding.csv" % sym)
        _write_klines_csv(spot_path, spot, "binance_spot_public", "spot")
        _write_klines_csv(perp_path, perp, "binance_usdtperp_public", "perp")
        _write_funding_csv(fund_path, funding)

        for label, p, n in (("spot", spot_path, len(spot)),
                            ("perp", perp_path, len(perp)),
                            ("funding", fund_path, len(funding))):
            sha = compute_sha256(p)
            manifest["files"]["%s_%s" % (sym, label)] = {
                "path": str(p.relative_to(REPO_ROOT)).replace("\\", "/"),
                "rows": n, "sha256": sha}

    with open(MANIFEST_PATH, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, sort_keys=True)
    manifest["manifest_path"] = str(MANIFEST_PATH.relative_to(REPO_ROOT)).replace(
        "\\", "/")
    manifest["manifest_sha256"] = compute_sha256(MANIFEST_PATH)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
