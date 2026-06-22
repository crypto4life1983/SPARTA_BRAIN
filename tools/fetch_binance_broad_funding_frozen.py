"""Bounded BROAD-UNIVERSE Binance USD-M funding-rate fetcher (C23r carry research).

A SEPARATE, dedicated fetcher for a bounded broad multi-asset FUNDING-RATE frozen dataset, used
ONLY for exploratory cross-sectional funding-carry return-engine feasibility. It does NOT modify
and does NOT import the canonical 3-symbol carry fetcher
(`tools/crypto_basis_funding_public_fetch_once.py`), whose narrow allowlist stays intact.

Public Binance USD-M funding data ONLY:
- network surface restricted to https://fapi.binance.com/fapi/v1/fundingRate
- symbols restricted to the human-approved 40-symbol allowlist below (EOSUSDT/MKRUSDT excluded:
  no current trading USD-M perp)
- every URL passes `_assert_safe_url`, rejecting forbidden fragments
  (account / order / trade / userdata / signed / signature / apikey / secret / private)
- NO API key, NO signed endpoints, NO account endpoints, NO order/trade/broker endpoints
- reads NO environment variables or secrets
- writes ONLY into data/broad_crypto_funding_universe/

It records RAW funding rows (no clip / no smooth / no forward-fill), the true first/last funding
time per symbol, the per-symbol funding CADENCE (interval hours) detecting non-8h intervals,
mark_price zero/sparse counts, and funding-rate outlier counts -- all SHA-256 pinned in a
manifest + quality report. funding_rate is the PRIMARY field; mark_price is secondary.

SURVIVORSHIP NOTE (recorded in the manifest): Binance-public funding returns history only for
CURRENTLY-LISTED perps -> survivorship bias. EXPLORATORY ONLY; NOT sufficient for paper/live.

Runs NO strategy evaluation, NO labels, NO replay/backtest, NO optimization, NO candidate
activation/promotion, NO commit/push.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import statistics
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

REPO_ROOT = Path(__file__).resolve().parents[1]

FUNDING_URL = "https://fapi.binance.com/fapi/v1/fundingRate"
ALLOWED_URL_PREFIXES = (FUNDING_URL,)
FORBIDDEN_URL_FRAGMENTS = (
    "account", "order", "trade", "userdata", "signed", "signature", "apikey", "secret",
    "private",
)

ALLOWED_SYMBOLS = (
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT", "TRXUSDT",
    "LINKUSDT", "AVAXUSDT", "DOTUSDT", "LTCUSDT", "BCHUSDT", "UNIUSDT", "ATOMUSDT", "ETCUSDT",
    "XLMUSDT", "ICPUSDT", "AAVEUSDT", "NEARUSDT", "FILUSDT", "ALGOUSDT", "VETUSDT", "XTZUSDT",
    "THETAUSDT", "HBARUSDT", "EGLDUSDT", "ZECUSDT", "MANAUSDT", "SANDUSDT", "CHZUSDT", "ENJUSDT",
    "ZILUSDT", "KAVAUSDT", "RUNEUSDT", "GRTUSDT", "CRVUSDT", "SNXUSDT", "COMPUSDT", "YFIUSDT",
)
EXCLUDED_SYMBOLS = {
    "EOSUSDT": "no current TRADING Binance USD-M USDT perp (delisted ~2025-05)",
    "MKRUSDT": "no current TRADING Binance USD-M USDT perp (delisted ~2025-09)",
}
MAX_LIMIT = 1000
SAFETY_ITER_CAP = 400
OUTPUT_SUBDIR = "data/broad_crypto_funding_universe"
OUTLIER_ABS_FUNDING = 0.003   # |funding_rate| > 0.3%/interval flagged (NOT clipped)
MIN_PRIMARY_ROWS = 90
_USER_AGENT = "SPARTA-BroadFunding-Frozen-Fetcher/1 (public-market-data-only)"


class BroadFundingError(Exception):
    pass


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


def _assert_safe_url(url: str) -> None:
    if not isinstance(url, str) or not url:
        raise BroadFundingError("url must be a non-empty string")
    if not any(url.startswith(p) for p in ALLOWED_URL_PREFIXES):
        raise BroadFundingError("refusing non-allowlisted url: %s" % url)
    n = _norm(url)
    for frag in FORBIDDEN_URL_FRAGMENTS:
        if frag in n:
            raise BroadFundingError("refusing url containing forbidden fragment %r" % frag)


def _http_get_json(url: str, timeout: float = 30.0) -> Any:
    _assert_safe_url(url)
    req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT}, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _ms(date_str: str, end: bool = False) -> int:
    if not _DATE_RE.match(date_str):
        raise BroadFundingError("invalid date %r" % date_str)
    d = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    if end:
        d = d.replace(hour=23, minute=59, second=59, microsecond=999000)
    return int(d.timestamp() * 1000)


def _ts_to_iso(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000.0, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _build_url(symbol: str, start_ms: int, end_ms: int, limit: int) -> str:
    return ("%s?symbol=%s&startTime=%d&endTime=%d&limit=%d"
            % (FUNDING_URL, symbol, start_ms, end_ms, limit))


def fetch_funding(symbol: str, start_ms: int, end_ms: int,
                  http_get: Callable[[str], Any] | None = None) -> list[dict]:
    """Paginate the public funding endpoint by startTime/endTime. Inject http_get for tests."""
    if symbol not in ALLOWED_SYMBOLS:
        raise BroadFundingError("symbol %r not in approved allowlist" % symbol)
    if http_get is None:
        http_get = _http_get_json
    out: list[dict] = []
    seen: set[int] = set()
    cursor = start_ms
    iters = 0
    while cursor <= end_ms:
        iters += 1
        if iters > SAFETY_ITER_CAP:
            raise BroadFundingError("pagination exceeded safety cap")
        url = _build_url(symbol, cursor, end_ms, MAX_LIMIT)
        _assert_safe_url(url)
        page = http_get(url)
        if not isinstance(page, list):
            raise BroadFundingError("expected JSON array, got %s" % type(page).__name__)
        if not page:
            break
        last_ft = None
        added = 0
        for r in page:
            ft = int(r["fundingTime"])
            last_ft = ft
            if ft in seen or ft > end_ms:
                continue
            seen.add(ft)
            out.append({"funding_time_ms": ft, "symbol": symbol,
                        "funding_rate": float(r["fundingRate"]),
                        "mark_price": float(r.get("markPrice") or 0.0)})
            added += 1
        if last_ft is None:
            break
        nxt = last_ft + 1
        if nxt <= cursor or added == 0 or len(page) < MAX_LIMIT:
            break
        cursor = nxt
    out.sort(key=lambda r: r["funding_time_ms"])
    return out


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
        w.writerow(["datetime", "funding_time_ms", "symbol", "funding_rate", "mark_price"])
        prev = None
        for r in rows:
            ft = r["funding_time_ms"]
            if prev is not None and ft == prev:
                raise BroadFundingError("duplicate funding_time at %d" % ft)
            w.writerow([_ts_to_iso(ft), ft, r["symbol"],
                        ("%.10f" % r["funding_rate"]).rstrip("0").rstrip(".") or "0",
                        ("%.8f" % r["mark_price"]).rstrip("0").rstrip(".") or "0"])
            prev = ft


def _interval_hours(rows: list[dict]) -> tuple:
    """(dominant_interval_h, distinct_intervals_h, missing_intervals)."""
    if len(rows) < 3:
        return (None, [], 0)
    deltas = [(rows[i]["funding_time_ms"] - rows[i - 1]["funding_time_ms"]) / 3600000.0
              for i in range(1, len(rows))]
    rounded = [round(d, 2) for d in deltas]
    dominant = round(statistics.median(rounded), 2)
    distinct = sorted({d for d in rounded if d > 0})
    # missing = gaps materially larger than the dominant cadence
    missing = sum(1 for d in rounded if d > dominant * 1.5)
    return (dominant, distinct, missing)


def fetch_symbol(symbol: str, start: str, end: str,
                 http_get: Callable[[str], Any] | None = None) -> dict[str, Any]:
    try:
        rows = fetch_funding(symbol, _ms(start), _ms(end, end=True), http_get=http_get)
    except (BroadFundingError, urllib.error.URLError, ValueError, KeyError) as exc:
        return {"symbol": symbol, "included": False,
                "reason": "fetch_error:%s" % type(exc).__name__, "detail": str(exc)[:160]}
    if not rows:
        return {"symbol": symbol, "included": False, "reason": "no_funding_data", "rows": 0}
    n = len(rows)
    if n < MIN_PRIMARY_ROWS:
        return {"symbol": symbol, "included": False,
                "reason": "short_history_below_%d" % MIN_PRIMARY_ROWS, "rows": n}
    dom, distinct, missing = _interval_hours(rows)
    mp_zero = sum(1 for r in rows if r["mark_price"] == 0.0)
    outliers = sum(1 for r in rows if abs(r["funding_rate"]) > OUTLIER_ABS_FUNDING)
    frs = [r["funding_rate"] for r in rows]
    out_path = _out_dir() / ("%s_funding.csv" % symbol)
    write_csv(rows, out_path)
    return {
        "symbol": symbol, "included": True,
        "path": str(out_path.relative_to(REPO_ROOT)).replace("\\", "/"),
        "rows": n,
        "first_funding": _ts_to_iso(rows[0]["funding_time_ms"]),
        "last_funding": _ts_to_iso(rows[-1]["funding_time_ms"]),
        "dominant_interval_h": dom, "distinct_intervals_h": distinct,
        "is_non_8h": (dom != 8.0) or any(abs(d - 8.0) > 0.01 for d in distinct),
        "missing_intervals": missing,
        "mark_price_zero": mp_zero,
        "funding_rate_min": min(frs), "funding_rate_max": max(frs),
        "outlier_count": outliers,
        # compare by DATE (funding timestamps carry a small ms offset), so only perps that
        # genuinely list AFTER the requested start day are flagged as short history
        "started_after_range": _ts_to_iso(rows[0]["funding_time_ms"])[:10] > start,
        "sha256": _hash(out_path),
    }


def assemble(start: str, end: str, http_get: Callable[[str], Any] | None = None,
             polite_delay: float = 0.2) -> dict[str, Any]:
    included, excluded = [], []
    for s in ALLOWED_SYMBOLS:
        rec = fetch_symbol(s, start, end, http_get=http_get)
        (included if rec.get("included") else excluded).append(rec)
        if http_get is None and polite_delay:
            time.sleep(polite_delay)
    manifest = {
        "dataset": "broad_crypto_funding_universe",
        "purpose": "EXPLORATORY cross-sectional funding-carry return-engine feasibility ONLY",
        "source": "binance_public_usdm_funding",
        "endpoint": FUNDING_URL,
        "interval_note": "Binance funding cadence is NOT uniformly 8h; per-symbol dominant "
                         "interval + distinct intervals recorded; funding_rate is per-interval.",
        "assembled_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "requested_date_range": {"start": start, "end": end},
        "allowlist": list(ALLOWED_SYMBOLS),
        "excluded": dict(EXCLUDED_SYMBOLS),
        "included": sorted(included, key=lambda r: r["symbol"]),
        "excluded_results": sorted(excluded, key=lambda r: r["symbol"]),
        "csv_fields": ["datetime", "funding_time_ms", "symbol", "funding_rate", "mark_price"],
        "funding_rate_is_primary_mark_price_secondary": True,
        "no_forward_fill": True, "no_clip_no_smooth": True,
        "survivorship_warning": "Binance-public currently-listed perps only -> survivorship "
                                "bias; EXPLORATORY ONLY; NOT sufficient for paper/live.",
    }
    return manifest


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Assemble bounded broad USD-M funding frozen "
                                             "dataset (public Binance funding endpoint only).")
    ap.add_argument("--start", default="2021-01-01")
    ap.add_argument("--end", default="2026-06-21")
    args = ap.parse_args(argv)

    raw = _out_dir()
    if raw.exists() and any(raw.glob("*_funding.csv")):
        print("ERROR: funding outputs already exist; refusing to overwrite frozen data: %s"
              % raw, file=sys.stderr)
        return 1
    m = assemble(args.start, args.end)
    base = _out_dir().parent
    man_p = base / "manifest.json"
    qa_p = base / "quality_report.json"
    man_p.write_text(json.dumps(m, indent=2, sort_keys=True), encoding="utf-8")
    inc = m["included"]
    qa = {
        "included_count": len(inc), "excluded_count": len(m["excluded_results"]),
        "exclusions": [{k: r.get(k) for k in ("symbol", "reason", "rows")}
                       for r in m["excluded_results"]] + [
            {"symbol": s, "reason": r} for s, r in EXCLUDED_SYMBOLS.items()],
        "short_histories": [r["symbol"] for r in inc if r.get("started_after_range")],
        "non_8h_cadence": {r["symbol"]: r["distinct_intervals_h"]
                           for r in inc if r.get("is_non_8h")},
        "missing_interval_summary": {r["symbol"]: r["missing_intervals"]
                                     for r in inc if r["missing_intervals"]},
        "total_missing_intervals": sum(r["missing_intervals"] for r in inc),
        "mark_price_zero_summary": {r["symbol"]: r["mark_price_zero"]
                                    for r in inc if r["mark_price_zero"]},
        "outlier_funding_summary": {r["symbol"]: r["outlier_count"]
                                    for r in inc if r["outlier_count"]},
        "feasible_for_cross_sectional_carry_eval": len(inc) >= 20,
    }
    qa_p.write_text(json.dumps(qa, indent=2, sort_keys=True), encoding="utf-8")
    print("included=%d excluded=%d" % (len(inc), len(EXCLUDED_SYMBOLS)))
    print("manifest_sha256: %s" % _hash(man_p))
    print("quality_report_sha256: %s" % _hash(qa_p))
    return 0


if __name__ == "__main__":
    sys.exit(main())
