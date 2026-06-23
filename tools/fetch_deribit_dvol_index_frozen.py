"""Bounded Deribit DVOL implied-vol index fetcher (VRP Phase-1 research; PUBLIC DATA ONLY).

A SEPARATE, dedicated fetcher for the BTC/ETH DVOL (Deribit implied-volatility index) daily OHLC
history, used ONLY for exploratory Phase-1 volatility-risk-premium (VRP) feasibility (implied
DVOL vs realized vol from existing frozen spot). It imports/modifies NONE of the Binance
fetchers.

Public Deribit market data ONLY:
- network surface restricted to https://www.deribit.com/api/v2/public/get_volatility_index_data
- currencies restricted to the approved allowlist {BTC, ETH}
- every URL passes `_assert_safe_url`, rejecting forbidden fragments
  (private / account / order / trade / buy / sell / signature / api_key / subaccount)
- NO API key, NO /private/ endpoints, NO signed/account/order/trade endpoints
- reads NO environment variables or secrets
- writes ONLY into data/deribit_iv_universe/

It records RAW DVOL OHLC rows (no clip / no smooth / no forward-fill), the true first/last date
per series, the resolution used, and crash-window coverage flags -- all SHA-256 pinned in a
manifest + quality report. DVOL launched ~2021, so the March-2020 COVID crash is NOT covered
(disclosed as a pre-DVOL gap). DVOL is a 30-day constant-maturity implied-vol INDEX -- a PROXY,
not tradeable delta-hedged straddle P&L (index-vs-tradeable caveat recorded).

Runs NO VRP / strategy evaluation, NO labels, NO replay/backtest, NO optimization, NO
paper/live/broker/order code; activates/promotes NOTHING; performs NO commit/push.
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
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

REPO_ROOT = Path(__file__).resolve().parents[1]

DVOL_ENDPOINT = "https://www.deribit.com/api/v2/public/get_volatility_index_data"
ALLOWED_URL_PREFIXES = (DVOL_ENDPOINT,)
FORBIDDEN_URL_FRAGMENTS = (
    "private", "account", "order", "trade", "buy", "sell", "signature", "apikey", "api_key",
    "subaccount", "withdraw",
)
ALLOWED_CURRENCIES = ("BTC", "ETH")
RESOLUTION_SECONDS = 86400          # 1-day DVOL OHLC
RESOLUTION_LABEL = "1D"
PAGE_LIMIT_DAYS = 365               # paginate the date range in <=1y chunks
SAFETY_ITER_CAP = 60
OUTPUT_SUBDIR = "data/deribit_iv_universe"
TARGET_START = "2021-03-24"
_USER_AGENT = "SPARTA-Deribit-DVOL-Frozen-Fetcher/1 (public-market-data-only)"

CRASH_WINDOWS = (
    {"window": "2020-03 COVID crash", "expected_covered": False,
     "note": "pre-DVOL (DVOL launched ~2021) -> known gap"},
    {"window": "2021-05 China-ban / leverage flush", "expected_covered": True},
    {"window": "2022-06 Luna/3AC contagion", "expected_covered": True},
    {"window": "2022-11 FTX collapse", "expected_covered": True},
    {"window": "2024-08 yen-carry unwind", "expected_covered": True},
)


class DvolFetchError(Exception):
    pass


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


def _assert_safe_url(url: str) -> None:
    if not isinstance(url, str) or not url:
        raise DvolFetchError("url must be a non-empty string")
    if not any(url.startswith(p) for p in ALLOWED_URL_PREFIXES):
        raise DvolFetchError("refusing non-allowlisted url: %s" % url)
    n = _norm(url)
    for frag in FORBIDDEN_URL_FRAGMENTS:
        if frag in n:
            raise DvolFetchError("refusing url containing forbidden fragment %r" % frag)


def _http_get_json(url: str, timeout: float = 30.0) -> Any:
    _assert_safe_url(url)
    req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT}, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _ms(date_str: str, end: bool = False) -> int:
    if not _DATE_RE.match(date_str):
        raise DvolFetchError("invalid date %r" % date_str)
    d = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    if end:
        d = d.replace(hour=23, minute=59, second=59, microsecond=999000)
    return int(d.timestamp() * 1000)


def _ts_to_date(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000.0, tz=timezone.utc).strftime("%Y-%m-%d")


def _build_url(currency: str, start_ms: int, end_ms: int) -> str:
    return ("%s?currency=%s&start_timestamp=%d&end_timestamp=%d&resolution=%d"
            % (DVOL_ENDPOINT, currency, start_ms, end_ms, RESOLUTION_SECONDS))


def fetch_dvol(currency: str, start: str, end: str,
               http_get: Callable[[str], Any] | None = None) -> list[dict]:
    """Paginate DVOL OHLC between start/end (inclusive). Inject http_get for tests."""
    if currency not in ALLOWED_CURRENCIES:
        raise DvolFetchError("currency %r not in approved allowlist %s"
                             % (currency, ALLOWED_CURRENCIES))
    if http_get is None:
        http_get = _http_get_json
    start_ms, end_ms = _ms(start), _ms(end, end=True)
    out: dict[int, dict] = {}
    cursor = start_ms
    iters = 0
    while cursor <= end_ms:
        iters += 1
        if iters > SAFETY_ITER_CAP:
            raise DvolFetchError("pagination exceeded safety cap")
        chunk_end = min(cursor + PAGE_LIMIT_DAYS * 86400 * 1000, end_ms)
        url = _build_url(currency, cursor, chunk_end)
        _assert_safe_url(url)
        resp = http_get(url)
        rows = (resp or {}).get("result", {}).get("data", []) if isinstance(resp, dict) else []
        for r in rows:
            ts = int(r[0])
            if ts > end_ms or ts in out:
                continue
            out[ts] = {"timestamp_ms": ts, "currency": currency,
                       "open": float(r[1]), "high": float(r[2]),
                       "low": float(r[3]), "close": float(r[4])}
        nxt = chunk_end + 1
        if nxt <= cursor:
            break
        cursor = nxt
    return [out[k] for k in sorted(out)]


def _out_dir() -> Path:
    d = (REPO_ROOT / OUTPUT_SUBDIR / "raw").resolve()
    d.relative_to((REPO_ROOT / OUTPUT_SUBDIR).resolve())
    return d


def _hash(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def write_csv(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["datetime", "timestamp_ms", "currency", "open", "high", "low", "close"])
        prev = None
        for r in rows:
            d = _ts_to_date(r["timestamp_ms"])
            if d == prev:
                raise DvolFetchError("duplicate daily DVOL bar at %s" % d)
            w.writerow([d, r["timestamp_ms"], r["currency"],
                        ("%.6f" % r["open"]).rstrip("0").rstrip(".") or "0",
                        ("%.6f" % r["high"]).rstrip("0").rstrip(".") or "0",
                        ("%.6f" % r["low"]).rstrip("0").rstrip(".") or "0",
                        ("%.6f" % r["close"]).rstrip("0").rstrip(".") or "0"])
            prev = d


def _quality(rows: list[dict]) -> dict:
    dates = [_ts_to_date(r["timestamp_ms"]) for r in rows]
    span_days = ((datetime.strptime(dates[-1], "%Y-%m-%d")
                  - datetime.strptime(dates[0], "%Y-%m-%d")).days + 1) if rows else 0
    return {
        "rows": len(rows),
        "first_date": dates[0] if rows else None,
        "last_date": dates[-1] if rows else None,
        "missing_days": max(0, span_days - len(set(dates))),
        "duplicate_timestamps": len(rows) - len(set(r["timestamp_ms"] for r in rows)),
        "zero_or_null_close": sum(1 for r in rows if r["close"] <= 0),
    }


def fetch_currency(currency: str, start: str, end: str,
                   http_get: Callable[[str], Any] | None = None) -> dict[str, Any]:
    try:
        rows = fetch_dvol(currency, start, end, http_get=http_get)
    except (DvolFetchError, urllib.error.URLError, ValueError, KeyError) as exc:
        return {"currency": currency, "included": False,
                "reason": "fetch_error:%s" % type(exc).__name__, "detail": str(exc)[:160]}
    if not rows:
        return {"currency": currency, "included": False, "reason": "no_dvol_data", "rows": 0}
    q = _quality(rows)
    out_path = _out_dir() / ("%s_dvol_1d.csv" % currency)
    write_csv(rows, out_path)
    cov = {c["window"]: ((c["window"][:7] >= (q["first_date"] or "9999")[:7])
                         and c.get("expected_covered", True)) for c in CRASH_WINDOWS}
    return {"currency": currency, "included": True,
            "path": str(out_path.relative_to(REPO_ROOT)).replace("\\", "/"),
            "resolution": RESOLUTION_LABEL, **q,
            "crash_window_coverage": cov, "sha256": _hash(out_path)}


def assemble(start: str, end: str, http_get: Callable[[str], Any] | None = None,
             polite_delay: float = 0.3) -> dict[str, Any]:
    included, excluded = [], []
    for c in ALLOWED_CURRENCIES:
        rec = fetch_currency(c, start, end, http_get=http_get)
        (included if rec.get("included") else excluded).append(rec)
        if http_get is None and polite_delay:
            time.sleep(polite_delay)
    return {
        "dataset": "deribit_iv_universe",
        "purpose": "EXPLORATORY Phase-1 VRP feasibility (DVOL implied vs realized vol) ONLY",
        "source": "deribit_public_dvol_volatility_index",
        "endpoint": DVOL_ENDPOINT,
        "approved_currencies": list(ALLOWED_CURRENCIES),
        "resolution": RESOLUTION_LABEL,
        "assembled_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "requested_date_range": {"start": start, "end": end},
        "csv_fields": ["datetime", "timestamp_ms", "currency", "open", "high", "low", "close"],
        "included": sorted(included, key=lambda r: r["currency"]),
        "excluded": sorted(excluded, key=lambda r: r["currency"]),
        "no_forward_fill": True, "no_clip_no_smooth": True,
        "march_2020_gap_warning": "DVOL launched ~2021; the March-2020 COVID crash is NOT "
                                  "covered (pre-DVOL gap).",
        "index_vs_tradeable_caveat": "DVOL is a 30-day constant-maturity implied-vol INDEX -- a "
                                     "PROXY for the VRP, NOT tradeable delta-hedged straddle P&L.",
        "crash_windows": [dict(c) for c in CRASH_WINDOWS],
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Assemble frozen BTC/ETH DVOL implied-vol index "
                                             "(Deribit public endpoint only).")
    ap.add_argument("--start", default=TARGET_START)
    ap.add_argument("--end", default="2026-06-21")
    args = ap.parse_args(argv)

    raw = _out_dir()
    if raw.exists() and any(raw.glob("*_dvol_1d.csv")):
        print("ERROR: DVOL outputs already exist; refusing to overwrite frozen data: %s" % raw,
              file=sys.stderr)
        return 1
    m = assemble(args.start, args.end)
    base = _out_dir().parent
    man_p = base / "manifest.json"
    qa_p = base / "quality_report.json"
    man_p.write_text(json.dumps(m, indent=2, sort_keys=True), encoding="utf-8")
    inc = m["included"]
    qa = {
        "currencies_included": [r["currency"] for r in inc],
        "per_currency": {r["currency"]: {k: r[k] for k in
                         ("rows", "first_date", "last_date", "missing_days",
                          "duplicate_timestamps", "zero_or_null_close")} for r in inc},
        "short_histories": [r["currency"] for r in inc
                            if (r.get("first_date") or "") > TARGET_START],
        "total_missing_days": sum(r["missing_days"] for r in inc),
        "total_duplicate_timestamps": sum(r["duplicate_timestamps"] for r in inc),
        "total_zero_or_null": sum(r["zero_or_null_close"] for r in inc),
        "crash_window_coverage": {r["currency"]: r["crash_window_coverage"] for r in inc},
        "march_2020_covered": False,
        "feasible_for_phase1_iv_vs_realized_vol_study": len(inc) == 2,
    }
    qa_p.write_text(json.dumps(qa, indent=2, sort_keys=True), encoding="utf-8")
    print("included=%d excluded=%d" % (len(inc), len(m["excluded"])))
    print("manifest_sha256: %s" % _hash(man_p))
    print("quality_report_sha256: %s" % _hash(qa_p))
    return 0


if __name__ == "__main__":
    sys.exit(main())
