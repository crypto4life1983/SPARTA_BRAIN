"""Forward-only Deribit BTC option-chain daily SNAPSHOT collector (PUBLIC DATA ONLY).

The free FALLBACK/parallel data path for Phase-2 VRP: snapshot the CURRENTLY-LIVE BTC option
chain once per run and append a dated frozen snapshot. It builds per-strike history ONLY going
FORWARD (NO backfill) -- the deployment-grade backtest path is paid historical (see
`per_strike_options_paid_data_import_contract`).

Public Deribit market data ONLY:
- network surface restricted to:
    https://www.deribit.com/api/v2/public/get_instruments
    https://www.deribit.com/api/v2/public/get_book_summary_by_currency
- currency restricted to BTC
- every URL passes `_assert_safe_url`, rejecting forbidden fragments
  (private / account / order / buy / sell / signature / api_key / subaccount / withdraw)
- NO API key, NO /private/ endpoints, NO trading/account endpoints, reads NO secrets
- writes ONLY into data/deribit_options_chain_universe/snapshots/<date>/

Each snapshot row joins instrument metadata (strike, option_type, expiration) with the
book-summary marks (mark_iv, mark_price, open_interest, volume, underlying_index_price). Greeks
are NOT computed here (delta can be derived later from mark_iv + underlying via Black-Scholes,
or captured via a separate ticker pass) -- this collector only RECORDS public marks. It runs NO
backtest, NO delta-hedge / straddle P&L, NO optimization; activates/promotes NOTHING; performs
NO commit/push; and MUST be run only under explicit human approval to START collection.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

REPO_ROOT = Path(__file__).resolve().parents[1]

INSTRUMENTS_ENDPOINT = "https://www.deribit.com/api/v2/public/get_instruments"
BOOK_SUMMARY_ENDPOINT = "https://www.deribit.com/api/v2/public/get_book_summary_by_currency"
ALLOWED_URL_PREFIXES = (INSTRUMENTS_ENDPOINT, BOOK_SUMMARY_ENDPOINT)
FORBIDDEN_URL_FRAGMENTS = (
    "private", "account", "order", "buy", "sell", "signature", "apikey", "api_key",
    "subaccount", "withdraw", "userdata",
)
ALLOWED_CURRENCY = "BTC"
OUTPUT_SUBDIR = "data/deribit_options_chain_universe"
_USER_AGENT = "SPARTA-Deribit-ChainSnapshot-Fwd/1 (public-market-data-only)"


class ChainSnapshotError(Exception):
    pass


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


def _assert_safe_url(url: str) -> None:
    if not isinstance(url, str) or not url:
        raise ChainSnapshotError("url must be a non-empty string")
    if not any(url.startswith(p) for p in ALLOWED_URL_PREFIXES):
        raise ChainSnapshotError("refusing non-allowlisted url: %s" % url)
    n = _norm(url)
    for frag in FORBIDDEN_URL_FRAGMENTS:
        if frag in n:
            raise ChainSnapshotError("refusing url containing forbidden fragment %r" % frag)


def _http_get_json(url: str, timeout: float = 30.0) -> Any:
    _assert_safe_url(url)
    req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT}, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def build_snapshot_rows(http_get: Callable[[str], Any] | None = None) -> list[dict]:
    """Join live BTC option instruments with their book-summary marks. Inject http_get for
    tests. Public read-only; computes no greeks/PnL."""
    if http_get is None:
        http_get = _http_get_json
    if ALLOWED_CURRENCY != "BTC":
        raise ChainSnapshotError("currency restricted to BTC")
    iurl = "%s?currency=%s&kind=option&expired=false" % (INSTRUMENTS_ENDPOINT, ALLOWED_CURRENCY)
    burl = "%s?currency=%s&kind=option" % (BOOK_SUMMARY_ENDPOINT, ALLOWED_CURRENCY)
    _assert_safe_url(iurl)
    _assert_safe_url(burl)
    instruments = (http_get(iurl) or {}).get("result", [])
    summary = (http_get(burl) or {}).get("result", [])
    meta = {s["instrument_name"]: s for s in instruments}
    rows = []
    for b in summary:
        name = b.get("instrument_name")
        m = meta.get(name)
        if not m:
            continue
        rows.append({
            "instrument_name": name,
            "strike": m.get("strike"),
            "option_type": m.get("option_type"),
            "expiration_timestamp": m.get("expiration_timestamp"),
            "mark_iv": b.get("mark_iv"),
            "mark_price": b.get("mark_price"),
            "underlying_index_price": b.get("underlying_price") or b.get("estimated_delivery_price"),
            "open_interest": b.get("open_interest"),
            "volume": b.get("volume"),
        })
    rows.sort(key=lambda r: (r["expiration_timestamp"] or 0, r["strike"] or 0,
                             r["option_type"] or ""))
    return rows


FIELDS = ("instrument_name", "strike", "option_type", "expiration_timestamp", "mark_iv",
          "mark_price", "underlying_index_price", "open_interest", "volume")


def _out_dir(date: str) -> Path:
    d = (REPO_ROOT / OUTPUT_SUBDIR / "snapshots" / date).resolve()
    d.relative_to((REPO_ROOT / OUTPUT_SUBDIR).resolve())
    return d


def _hash(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def write_snapshot(rows: list[dict], date: str) -> dict:
    d = _out_dir(date)
    out_path = d / ("btc_option_chain_%s.csv" % date)
    if out_path.exists():
        raise ChainSnapshotError("snapshot already exists; refusing to overwrite: %s" % out_path)
    d.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(list(FIELDS))
        for r in rows:
            w.writerow([r.get(k) for k in FIELDS])
    return {"date": date, "path": str(out_path.relative_to(REPO_ROOT)).replace("\\", "/"),
            "rows": len(rows), "sha256": _hash(out_path)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Forward-only BTC option-chain daily snapshot "
                                             "(Deribit public endpoints only).")
    ap.add_argument("--date", default=_today(), help="snapshot date label (default: today UTC)")
    args = ap.parse_args(argv)
    try:
        rows = build_snapshot_rows()
    except (ChainSnapshotError, urllib.error.URLError, ValueError, KeyError) as exc:
        print("ERROR: %s: %s" % (type(exc).__name__, str(exc)[:160]), file=sys.stderr)
        return 1
    if not rows:
        print("ERROR: empty chain; refusing to write", file=sys.stderr)
        return 1
    rec = write_snapshot(rows, args.date)
    print("snapshot_date:  %s" % rec["date"])
    print("rows:           %d" % rec["rows"])
    print("path:           %s" % rec["path"])
    print("sha256:         %s" % rec["sha256"])
    print("note: forward-only (no backfill); deployment-grade backtest needs paid history")
    return 0


if __name__ == "__main__":
    sys.exit(main())
