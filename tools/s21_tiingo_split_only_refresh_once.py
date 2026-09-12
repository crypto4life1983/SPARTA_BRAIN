"""s21 weekly RS — Tiingo split-only daily refresh for the LOCKED 48 universe (READ-ONLY fetch).

Operator-authorized 2026-09-12. Pulls split-adjusted-only (dividends NOT reinvested) daily bars
for the locked 48 symbols from Tiingo's official public API into a NEW dated source directory.
Never overwrites an existing source dir, never touches the sealed baseline, never places an order,
never edits the harness manifest (that is a separate explicit step the operator reviews).

Split-only is the harness's required basis: Tiingo's adjusted fields reinvest dividends, so this
tool takes the RAW open/high/low/close/volume columns, which Tiingo serves split-adjusted only.

Integrity gate (from the harness OPERATIONS_CHECKLIST §2): the new source must reproduce the
sealed baseline `sealed_baseline_20251230` on the overlapping window for 47 of 48 symbols, with
BKNG expected to differ because of its 25:1 split on 2026-04-06. A failure is reported, never
silently accepted.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import date as _date, datetime as _dt, timezone as _tz
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from paper_trading.weekly_rs_s21_forward_paper_harness.manifest import (  # noqa: E402
    DATA_SOURCES, LOCKED_UNIVERSE_48)

TOOL_VERSION = "s21_tiingo_split_only_refresh_v1"
API = "https://api.tiingo.com/tiingo/daily/%s/prices?startDate=%s&endDate=%s&format=json"
START_DATE = "2019-01-02"
SEALED_KEY = "sealed_baseline_20251230"
BKNG_SPLIT_NOTE = "BKNG 25:1 split 2026-04-06; split-only history is re-scaled from that date, so the sealed baseline (ends 2025-12-30, pre-split scale) legitimately differs"
_UA = "sparta-brain-s21-refresh-readonly/1.0"


class RefreshError(RuntimeError):
    pass


def _token() -> str:
    t = os.environ.get("TIINGO_API_KEY") or os.environ.get("TIINGO_TOKEN")
    if not t:
        raise RefreshError("no TIINGO_API_KEY / TIINGO_TOKEN in the environment")
    return t


def _assert_safe_url(url: str) -> None:
    if not url.startswith("https://api.tiingo.com/tiingo/daily/"):
        raise RefreshError("refusing non-allowlisted url: %s" % url)
    for frag in ("order", "account", "trade", "withdraw", "wallet"):
        if frag in url.lower():
            raise RefreshError("refusing url containing %r" % frag)


def split_only(payload: list) -> list:
    """Convert Tiingo daily rows to SPLIT-ONLY bars.

    Tiingo's raw open/high/low/close are UNADJUSTED traded prices; adjClose applies splits AND
    reinvests dividends. Neither is what the harness needs. Split-only is built here from the raw
    price and the per-row splitFactor: a bar is divided by the product of every split factor that
    occurs AFTER it, so a 5:1 split re-scales all prior history by 1/5 and leaves dividends alone.
    """
    rows = sorted(payload, key=lambda x: str(x["date"])[:10])
    n = len(rows)
    cum = [1.0] * n                      # cum[i] = product of splitFactor for bars strictly after i
    running = 1.0
    for i in range(n - 1, -1, -1):
        cum[i] = running
        running *= float(rows[i].get("splitFactor") or 1.0)
    out = []
    for i, x in enumerate(rows):
        f = cum[i] or 1.0
        out.append({"date": str(x["date"])[:10],
                    "open": round(float(x["open"]) / f, 6), "high": round(float(x["high"]) / f, 6),
                    "low": round(float(x["low"]) / f, 6), "close": round(float(x["close"]) / f, 6),
                    "volume": int(round(float(x.get("volume") or 0) * f))})
    return out


def fetch_symbol(sym: str, end_date: str, token: str, timeout: float = 60.0, max_wait_s: float = 3900.0) -> list:
    """Daily SPLIT-ONLY bars ascending. Backs off on HTTP 429 (Tiingo hourly quota) rather than
    failing the whole run; the caller is resumable so nothing already written is refetched."""
    url = API % (sym, START_DATE, end_date)
    _assert_safe_url(url)
    waited = 0.0
    while True:
        req = urllib.request.Request(url, headers={"User-Agent": _UA, "Authorization": "Token " + token,
                                                   "Content-Type": "application/json"}, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return split_only(json.loads(r.read().decode("utf-8")))
        except urllib.error.HTTPError as e:
            if e.code != 429 or waited >= max_wait_s:
                raise
            nap = 300.0
            print("  rate limited on %s; sleeping %ds (waited %ds)" % (sym, nap, waited), flush=True)
            time.sleep(nap)
            waited += nap


def write_csv(out_dir: Path, sym: str, suffix: str, rows: list) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / (sym + suffix)
    if p.exists():
        raise RefreshError("refuse_overwrite:%s" % p.name)
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=["date", "open", "high", "low", "close", "volume"], lineterminator="\n")
    w.writeheader()
    for r in rows:
        w.writerow(r)
    blob = buf.getvalue().encode("utf-8")
    p.write_bytes(blob)
    sha = hashlib.sha256(blob).hexdigest()
    p.with_suffix(p.suffix + ".sha256").write_text(sha + "\n", encoding="utf-8")
    return {"symbol": sym, "path": str(p.relative_to(REPO_ROOT)).replace("\\", "/"), "sha256": sha,
            "rows": len(rows), "first": rows[0]["date"] if rows else None, "last": rows[-1]["date"] if rows else None}


def _read_closes(path: Path) -> dict:
    out = {}
    with open(path, "r", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            out[r["date"]] = float(r["close"])
    return out


def verify_against_sealed(new_dir: Path, new_suffix: str, tol_bps: float = 5.0) -> dict:
    """Overlap check vs the READ-ONLY sealed baseline. 47/48 must agree within tol; BKNG may differ."""
    sealed = DATA_SOURCES[SEALED_KEY]
    sdir, ssuf = REPO_ROOT / sealed["dir"], sealed["filename_suffix"]
    agree, differ, missing = [], [], []
    for sym in LOCKED_UNIVERSE_48:
        sp, np_ = sdir / (sym + ssuf), new_dir / (sym + new_suffix)
        if not sp.exists() or not np_.exists():
            missing.append(sym)
            continue
        a, b = _read_closes(sp), _read_closes(np_)
        common = sorted(set(a) & set(b))
        if not common:
            missing.append(sym)
            continue
        worst = max(abs(b[d] / a[d] - 1.0) * 1e4 for d in common if a[d])
        (agree if worst <= tol_bps else differ).append({"symbol": sym, "overlap_bars": len(common), "worst_bps": round(worst, 3)})
    ok = len(agree) >= 47 and all(d["symbol"] == "BKNG" for d in differ)
    return {"agree": len(agree), "differ": [d["symbol"] for d in differ], "missing": missing,
            "worst_agreeing_bps": max([a["worst_bps"] for a in agree], default=None),
            "differ_detail": differ, "expected_differ": ["BKNG"], "bkng_note": BKNG_SPLIT_NOTE,
            "passes_47_of_48_rule": bool(ok), "tolerance_bps": tol_bps}


def run(end_date: str, sleep_s: float = 0.15) -> dict:
    token = _token()
    key = "refreshed_%s" % end_date.replace("-", "")
    if key in DATA_SOURCES:
        raise RefreshError("data source %s already registered in the manifest" % key)
    out_dir = REPO_ROOT / "data" / ("s21_weekly_rs_paper_refresh_%s" % end_date.replace("-", "")) / "raw"
    suffix = "_ohlcv_1d_%s_%s.csv" % (START_DATE.replace("-", ""), end_date.replace("-", ""))
    files, cal_ref, misaligned = [], None, []
    for sym in LOCKED_UNIVERSE_48:
        existing = out_dir / (sym + suffix)
        if existing.exists():                      # resume: never refetch or overwrite
            with open(existing, "r", encoding="utf-8") as f:
                rows = [{"date": r["date"], "open": float(r["open"]), "high": float(r["high"]),
                         "low": float(r["low"]), "close": float(r["close"]), "volume": int(r["volume"])}
                        for r in csv.DictReader(f)]
            files.append({"symbol": sym, "path": str(existing.relative_to(REPO_ROOT)).replace("\\", "/"),
                          "sha256": hashlib.sha256(existing.read_bytes()).hexdigest(), "rows": len(rows),
                          "first": rows[0]["date"] if rows else None, "last": rows[-1]["date"] if rows else None,
                          "resumed": True})
        else:
            rows = fetch_symbol(sym, end_date, token)
            if not rows:
                raise RefreshError("empty series for %s" % sym)
            files.append(write_csv(out_dir, sym, suffix, rows))
        ds = [r["date"] for r in rows]
        if cal_ref is None:
            cal_ref = ds
        elif ds != cal_ref:
            misaligned.append({"symbol": sym, "bars": len(ds), "ref_bars": len(cal_ref)})
        if sleep_s:
            time.sleep(sleep_s)
    verify = verify_against_sealed(out_dir, suffix)
    manifest_entry = {"dir": str(out_dir.relative_to(REPO_ROOT)).replace("\\", "/"), "filename_suffix": suffix,
                      "last_date": cal_ref[-1] if cal_ref else None, "read_only": False,
                      "note": "Tiingo split-only daily, fetched %s by %s" % (_dt.now(_tz.utc).date().isoformat(), TOOL_VERSION)}
    rec = {"tool": TOOL_VERSION, "fetched_utc": _dt.now(_tz.utc).isoformat(timespec="seconds"),
           "source_key_proposed": key, "manifest_entry_proposed": manifest_entry,
           "symbols": len(files), "calendar_bars": len(cal_ref or []),
           "first_date": cal_ref[0] if cal_ref else None, "last_date": cal_ref[-1] if cal_ref else None,
           "calendar_misalignment": misaligned, "sealed_baseline_verification": verify, "files": files,
           "basis": "SPLIT_ONLY (raw OHLC; adjClose deliberately NOT used because it reinvests dividends)",
           "manifest_edited_by_this_tool": False, "orders_placed": False}
    mp = out_dir.parent / "refresh_manifest.json"
    blob = json.dumps(rec, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    mp.write_bytes(blob)
    mp.with_suffix(".json.sha256").write_text(hashlib.sha256(blob).hexdigest() + "\n", encoding="utf-8")
    rec["refresh_manifest"] = str(mp.relative_to(REPO_ROOT)).replace("\\", "/")
    return rec


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--end-date", required=True)
    ap.add_argument("--operator-authorized", action="store_true", help="required; this fetch uses a vendor credential")
    a = ap.parse_args(argv)
    if not a.operator_authorized:
        print(json.dumps({"status": "REFUSED", "reason": "missing --operator-authorized"}, indent=2))
        return 1
    r = run(a.end_date)
    print(json.dumps({k: v for k, v in r.items() if k != "files"}, indent=2, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
