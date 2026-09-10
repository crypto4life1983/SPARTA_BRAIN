"""Candidate #22 -- B3 STAGE TWO: HISTORICAL SHORTABILITY EVIDENCE (READ-ONLY; RESEARCH ONLY).

Primary question, per surviving Stage One short signal and per required historical execution
date: "could the frozen C22 short signal actually have been expressed as a NEW short position
using the candidate instrument on that date?" Existence (Stage One) is necessary, not sufficient.

Derivatives (home venue): launched <= decision date; not expired/delisted through the fill dates;
official daily market activity (candle with volume > 0) on the decision date AND on both fill
conventions (calendar D+1, next weekday); official funding settlements inside the decision->fill
window proving the perpetual mechanism was operational; short exposure supported by the
instrument type (linear perpetual / flexible futures permit sell-to-open by design). Any missing
element fails closed (FAIL_* or UNRESOLVED_*); UNRESOLVED never becomes PASS.

Spot-margin / borrow paths: pair existence is NOT sufficient. First-party historical margin or
borrow-market evidence on the required dates is required; present-day margin flags are recorded
as observations only. Venues that expose no historical margin/borrow state stay UNRESOLVED.

Venue policy: every candidate is classified HOME_VENUE (the Signum-named venue/platform) or
SUBSTITUTED_PLATFORM. The frozen B3 contract sets no_cross_venue_substitution=True and requires
a human decision "approve_home_venue_implementation_or_explicit_cross_venue_approval"; no such
approval exists, so substituted-platform candidates (MORPHO on Coinbase International) are
PENDING_VENUE_POLICY regardless of their evidence. No alternative venues are searched for
eliminated assets (TEL): the Stage One elimination is preserved.

Cost boundary: funding / borrow records are preserved as MECHANISM evidence only; no cost
arithmetic, no performance. Evidence discipline as Stage One (raw preserved with sha256,
endpoint, query, UTC time; deterministic normalized records; never overwritten).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import date as _date, datetime as _dt, timedelta as _td, timezone as _tz
from pathlib import Path
from typing import Callable

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import tools.c22_b3_stage1_instrument_existence_once as S1  # noqa: E402

STAGE = "B3_STAGE_TWO_HISTORICAL_SHORTABILITY"
STAGE_VERSION = "c22_b3_stage2_v1"
STAGE1_RUN_OF_RECORD = "20260910T225620Z"
STAGE1_REPORT = REPO_ROOT / "reports" / "c22_gc_b3_stage1" / ("c22_b3_stage1_instrument_existence_%s.json" % STAGE1_RUN_OF_RECORD)
STAGE1_REPORT_SHA256 = "95b135c3356809db971881f1ea91ed0accc7d7d595b986fca1728fad67b726d8"
REPORT_DIR = REPO_ROOT / "reports" / "c22_gc_b3_stage2"
CANDIDATE_ADMISSION_DIR = S1.EVIDENCE_ROOT / "candidate_admission"
_USER_AGENT = "sparta-brain-c22-b3-stage2-readonly/1.0"

WINDOW_START, WINDOW_END = "2026-06-15", "2026-07-25"     # covers all decision dates and both fill conventions

ALLOWED_URL_PREFIXES = (
    "https://fapi.binance.com/fapi/v1/klines",
    "https://fapi.binance.com/fapi/v1/fundingRate",
    "https://api.bybit.com/v5/market/kline",
    "https://api.bybit.com/v5/market/funding/history",
    "https://www.okx.com/api/v5/market/history-candles",
    "https://www.okx.com/api/v5/public/funding-rate-history",
    "https://api.gateio.ws/api/v4/futures/usdt/candlesticks",
    "https://api.gateio.ws/api/v4/futures/usdt/funding_rate",
    "https://futures.kraken.com/api/charts/v1/trade/",
    "https://futures.kraken.com/derivatives/api/v4/historicalfundingrates",
    "https://api.international.coinbase.com/api/v1/instruments/",
    "https://api-pub.bitfinex.com/v2/candles/",
    "https://api-pub.bitfinex.com/v2/funding/stats/",
)
FORBIDDEN_URL_FRAGMENTS = S1.FORBIDDEN_URL_FRAGMENTS

# verdicts
PASS = "PASS_HISTORICAL_SHORTABILITY"
FAIL_NOT_SHORTABLE = "FAIL_NOT_SHORTABLE"
FAIL_MARGIN = "FAIL_MARGIN_NOT_AVAILABLE"
FAIL_BORROW = "FAIL_BORROW_NOT_AVAILABLE"
FAIL_PRELAUNCH = "FAIL_PRELAUNCH"
FAIL_DELISTED = "FAIL_DELISTED_OR_CLOSED"
FAIL_NO_ACTIVITY = "FAIL_NO_MARKET_ACTIVITY"
FAIL_VENUE = "FAIL_WRONG_EXECUTION_VENUE"
PENDING_VENUE = "PENDING_VENUE_POLICY"
UNRES_MARGIN = "UNRESOLVED_HISTORICAL_MARGIN_STATE"
UNRES_BORROW = "UNRESOLVED_HISTORICAL_BORROW_STATE"
UNRES_MARKET = "UNRESOLVED_MARKET_STATE"
NOT_EVALUATED = "NOT_EVALUATED_STAGE_ONE_NOT_PASSED"
VERDICTS = (PASS, FAIL_NOT_SHORTABLE, FAIL_MARGIN, FAIL_BORROW, FAIL_PRELAUNCH, FAIL_DELISTED, FAIL_NO_ACTIVITY,
            FAIL_VENUE, PENDING_VENUE, UNRES_MARGIN, UNRES_BORROW, UNRES_MARKET, NOT_EVALUATED)
_RANK = {PASS: 0, PENDING_VENUE: 1, UNRES_MARKET: 2, UNRES_MARGIN: 3, UNRES_BORROW: 4, FAIL_NO_ACTIVITY: 5,
         FAIL_PRELAUNCH: 6, FAIL_DELISTED: 7, FAIL_MARGIN: 8, FAIL_BORROW: 9, FAIL_NOT_SHORTABLE: 10, FAIL_VENUE: 11, NOT_EVALUATED: 12}

PATH_DERIVATIVE = "DERIVATIVE_PERPETUAL_OR_FUTURES"
PATH_SPOT_MARGIN = "SPOT_MARGIN_BORROW"
VENUE_HOME = "HOME_VENUE"
VENUE_SUBSTITUTED = "SUBSTITUTED_PLATFORM"
DERIVATIVE_TYPES = ("linear_perpetual_futures", "linear_perpetual_swap")
HOME_VENUE_ALIASES = {"KRAKEN": ("KRAKEN", "KRAKEN_FUTURES")}   # Kraken Futures is Kraken's own derivatives platform for the same venue account family


class Stage2Error(RuntimeError):
    pass


# --------------------------------------------------------------------------------------------
def _assert_safe_url(url: str) -> None:
    if not isinstance(url, str) or not url.startswith("https://"):
        raise Stage2Error("refusing non-https url")
    if not any(url.startswith(p) for p in ALLOWED_URL_PREFIXES):
        raise Stage2Error("refusing non-allowlisted url: %s" % url)
    low = url.lower()
    for frag in FORBIDDEN_URL_FRAGMENTS:
        if frag in low and not (frag == "trade/" and "/charts/v1/trade/" in low):
            raise Stage2Error("refusing url containing forbidden fragment %r" % frag)


def http_get(url: str, timeout: float = 30.0) -> dict:
    _assert_safe_url(url)
    req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT}, method="GET")
    retrieved = _dt.now(_tz.utc).isoformat(timespec="seconds")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return {"url": url, "status": r.status, "retrieved_utc": retrieved, "raw_bytes": r.read()}
    except urllib.error.HTTPError as e:
        return {"url": url, "status": e.code, "retrieved_utc": retrieved, "raw_bytes": e.read()}


def _parse(resp):
    try:
        return json.loads(resp["raw_bytes"].decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return None


def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def load_stage1_of_record() -> dict:
    raw = STAGE1_REPORT.read_bytes()
    if S1._sha(raw) != STAGE1_REPORT_SHA256:
        raise Stage2Error("stage1_report_sha_mismatch")
    return json.loads(raw.decode("utf-8"))


# --------------------------------------------------------------------------------------------
# pure verdict logic
# --------------------------------------------------------------------------------------------
def derivative_verdict(existence_date, delisted_date, activity: dict, funding_dates: list, decision_date: str,
                       fill_dates: list, short_supported: bool = True, source_ok: bool = True) -> dict:
    """PURE. activity: {date: volume|None}; funding_dates: ISO dates of settlements. Fail-closed."""
    r = {"decision_date": decision_date, "fill_dates": sorted(set(fill_dates)), "verdict": None, "reason": None,
         "checks": {}}
    needed = sorted({decision_date, *fill_dates})
    latest = max(needed)
    if not source_ok:
        r.update(verdict=UNRES_MARKET, reason="official_activity_source_unavailable_or_unparseable")
        return r
    r["checks"]["launched_on_or_before_decision"] = bool(existence_date and existence_date <= decision_date)
    if not r["checks"]["launched_on_or_before_decision"]:
        r.update(verdict=FAIL_PRELAUNCH, reason="existence_%s_after_decision_%s" % (existence_date, decision_date))
        return r
    r["checks"]["not_delisted_through_fill"] = not (delisted_date and delisted_date != "UNKNOWN" and delisted_date <= latest)
    if not r["checks"]["not_delisted_through_fill"]:
        r.update(verdict=FAIL_DELISTED, reason="delisted_%s_on_or_before_%s" % (delisted_date, latest))
        return r
    r["checks"]["short_supported_by_instrument_type"] = bool(short_supported)
    if not short_supported:
        r.update(verdict=FAIL_NOT_SHORTABLE, reason="instrument_type_cannot_open_short")
        return r
    if not activity:
        r.update(verdict=UNRES_MARKET, reason="no_official_daily_activity_records_returned_for_window")
        return r
    missing = [d for d in needed if d not in activity]
    if missing:
        r.update(verdict=FAIL_NO_ACTIVITY, reason="no_official_candle_on_%s" % ",".join(missing))
        return r
    zero = [d for d in needed if not (activity[d] is not None and activity[d] > 0)]
    r["checks"]["market_activity_on_decision_and_fill_dates"] = not zero
    if zero:
        r.update(verdict=UNRES_MARKET, reason="candle_present_but_zero_or_unknown_volume_on_%s" % ",".join(zero))
        return r
    win_lo = decision_date
    win_hi = (_date.fromisoformat(latest) + _td(days=1)).isoformat()
    fund = [d for d in funding_dates if win_lo <= d <= win_hi]
    r["checks"]["funding_settlements_in_decision_to_fill_window"] = len(fund)
    if not fund:
        r.update(verdict=UNRES_MARKET, reason="no_official_funding_settlement_between_%s_and_%s" % (win_lo, win_hi))
        return r
    r.update(verdict=PASS, reason="launched<=D; activity on %s; %d funding settlements in [%s,%s]; perp sell-to-open by design"
             % (",".join(needed), len(fund), win_lo, win_hi))
    return r


def bitfinex_margin_verdict(activity: dict, funding_used_by_date: dict, funding_volume_by_date: dict,
                            decision_date: str, fill_dates: list, source_ok: bool = True) -> dict:
    """PURE. Bitfinex margin short of a pair requires borrowing the base currency on the venue's
    funding market. Evidence of historical borrow availability = official funding stats with
    funding_amount_used > 0 on the required dates AND official funding-market candles with
    volume > 0 in the window. Pair activity must also exist on the dates."""
    r = {"decision_date": decision_date, "fill_dates": sorted(set(fill_dates)), "verdict": None, "reason": None, "checks": {}}
    needed = sorted({decision_date, *fill_dates})
    if not source_ok:
        r.update(verdict=UNRES_BORROW, reason="official_funding_source_unavailable_or_unparseable")
        return r
    missing = [d for d in needed if d not in activity or not (activity[d] and activity[d] > 0)]
    r["checks"]["pair_activity_on_dates"] = not missing
    if missing:
        r.update(verdict=FAIL_NO_ACTIVITY, reason="no_official_pair_candle_volume_on_%s" % ",".join(missing))
        return r
    used = {d: funding_used_by_date.get(d) for d in needed}
    r["checks"]["funding_amount_used_on_dates"] = used
    lacking = [d for d in needed if not (used[d] is not None and used[d] > 0)]
    if lacking:
        r.update(verdict=UNRES_BORROW, reason="no_official_funding_stats_with_amount_used>0_on_%s" % ",".join(lacking))
        return r
    vol = {d: funding_volume_by_date.get(d) for d in needed}
    r["checks"]["funding_market_volume_on_dates"] = vol
    if not any(v and v > 0 for v in vol.values()):
        r.update(verdict=UNRES_BORROW, reason="no_official_funding_market_volume_on_required_dates")
        return r
    r["checks"]["margin_enablement_history_directly_exposed_by_api"] = False
    r.update(verdict=PASS, reason="base-currency borrow market active on %s (amount used>0, funding volume>0); margin enablement itself inferred from the active borrow market (second source recommended)" % ",".join(needed))
    return r


def signal_verdict(candidate_verdicts: list) -> str:
    home_pass = [v for v in candidate_verdicts if v["verdict"] == PASS and v["venue_class"] == VENUE_HOME]
    if home_pass:
        return PASS
    # a PASS on a substituted platform is never a signal PASS: it is a venue-policy question
    if any(v["verdict"] in (PENDING_VENUE, PASS) and v["venue_class"] == VENUE_SUBSTITUTED for v in candidate_verdicts):
        return PENDING_VENUE
    return sorted((v["verdict"] for v in candidate_verdicts), key=lambda x: _RANK.get(x, 99))[0] if candidate_verdicts else NOT_EVALUATED


# --------------------------------------------------------------------------------------------
# venue fetchers -> activity {date: volume}, funding dates [ISO]
# --------------------------------------------------------------------------------------------
def _act_from_rows(rows, ts_idx, vol_idx, ms=True) -> dict:
    out = {}
    for row in rows or []:
        try:
            d = S1._ms_to_date(row[ts_idx]) if ms else S1._s_to_date(row[ts_idx])
            if d:
                out[d] = _f(row[vol_idx])
        except (IndexError, TypeError):
            continue
    return out


def fetch_binance(base: str, get: Callable, run_id: str) -> dict:
    sym = "%sUSDT" % base
    r1 = get("https://fapi.binance.com/fapi/v1/klines?symbol=%s&interval=1d&startTime=%d&endTime=%d&limit=100" % (sym, S1._ms(WINDOW_START), S1._ms(WINDOW_END)))
    m1 = S1.preserve_raw("BINANCE", base, "usdm_daily_klines", r1, {"symbol": sym, "interval": "1d", "start": WINDOW_START, "end": WINDOW_END}, run_id)
    j1 = _parse(r1)
    r2 = get("https://fapi.binance.com/fapi/v1/fundingRate?symbol=%s&startTime=%d&endTime=%d&limit=1000" % (sym, S1._ms(WINDOW_START), S1._ms(WINDOW_END)))
    m2 = S1.preserve_raw("BINANCE", base, "usdm_funding_history", r2, {"symbol": sym, "start": WINDOW_START, "end": WINDOW_END}, run_id)
    j2 = _parse(r2)
    ok = isinstance(j1, list) and isinstance(j2, list)
    return {"instrument": sym, "activity": _act_from_rows(j1, 0, 5) if isinstance(j1, list) else {},
            "funding_dates": sorted({S1._ms_to_date(x.get("fundingTime")) for x in (j2 if isinstance(j2, list) else []) if S1._ms_to_date(x.get("fundingTime"))}),
            "funding_records": len(j2) if isinstance(j2, list) else 0, "source_ok": ok, "metas": [m1, m2]}


def fetch_bybit(base: str, get: Callable, run_id: str) -> dict:
    sym = "%sUSDT" % base
    r1 = get("https://api.bybit.com/v5/market/kline?category=linear&symbol=%s&interval=D&start=%d&end=%d&limit=200" % (sym, S1._ms(WINDOW_START), S1._ms(WINDOW_END)))
    m1 = S1.preserve_raw("BYBIT", base, "linear_daily_kline", r1, {"category": "linear", "symbol": sym, "interval": "D", "start": WINDOW_START, "end": WINDOW_END}, run_id)
    j1 = _parse(r1)
    fund, metas, end = [], [m1], S1._ms(WINDOW_END)
    for page in range(5):
        r2 = get("https://api.bybit.com/v5/market/funding/history?category=linear&symbol=%s&startTime=%d&endTime=%d&limit=200" % (sym, S1._ms(WINDOW_START), end))
        metas.append(S1.preserve_raw("BYBIT", base, "linear_funding_history_p%02d" % page, r2, {"category": "linear", "symbol": sym, "start": WINDOW_START, "end_ms": end, "page": page}, run_id))
        j2 = _parse(r2)
        lst = (j2 or {}).get("result", {}).get("list", []) if isinstance(j2, dict) else []
        fund += lst
        if len(lst) < 200:
            break
        end = min(int(x["fundingRateTimestamp"]) for x in lst) - 1
    rows = (j1 or {}).get("result", {}).get("list", []) if isinstance(j1, dict) else []
    return {"instrument": sym, "activity": _act_from_rows(rows, 0, 5), "funding_dates": sorted({S1._ms_to_date(x.get("fundingRateTimestamp")) for x in fund if S1._ms_to_date(x.get("fundingRateTimestamp"))}),
            "funding_records": len(fund), "source_ok": isinstance(j1, dict) and bool(rows), "metas": metas}


def fetch_okx(base: str, get: Callable, run_id: str) -> dict:
    inst = "%s-USDT-SWAP" % base
    r1 = get("https://www.okx.com/api/v5/market/history-candles?instId=%s&bar=1D&after=%d&before=%d&limit=100" % (inst, S1._ms(WINDOW_END) + 86_400_000, S1._ms(WINDOW_START) - 1))
    m1 = S1.preserve_raw("OKX", base, "swap_history_candles", r1, {"instId": inst, "bar": "1D", "start": WINDOW_START, "end": WINDOW_END}, run_id)
    j1 = _parse(r1)
    fund, metas, after = [], [m1], S1._ms(WINDOW_END) + 86_400_000
    for page in range(8):
        r2 = get("https://www.okx.com/api/v5/public/funding-rate-history?instId=%s&after=%d&before=%d&limit=100" % (inst, after, S1._ms(WINDOW_START) - 1))
        metas.append(S1.preserve_raw("OKX", base, "swap_funding_rate_history_p%02d" % page, r2, {"instId": inst, "after_ms": after, "before": WINDOW_START, "page": page}, run_id))
        j2 = _parse(r2)
        data = (j2 or {}).get("data", []) if isinstance(j2, dict) else []
        fund += data
        if len(data) < 100:
            break
        after = min(int(x["fundingTime"]) for x in data)
    rows = (j1 or {}).get("data", []) if isinstance(j1, dict) else []
    return {"instrument": inst, "activity": _act_from_rows(rows, 0, 5), "funding_dates": sorted({S1._ms_to_date(x.get("fundingTime")) for x in fund if S1._ms_to_date(x.get("fundingTime"))}),
            "funding_records": len(fund), "source_ok": isinstance(j1, dict) and bool(rows), "metas": metas}


def fetch_gate(base: str, get: Callable, run_id: str) -> dict:
    name = "%s_USDT" % base
    r1 = get("https://api.gateio.ws/api/v4/futures/usdt/candlesticks?contract=%s&interval=1d&from=%d&to=%d" % (name, S1._ms(WINDOW_START) // 1000, S1._ms(WINDOW_END) // 1000))
    m1 = S1.preserve_raw("GATE", base, "futures_daily_candlesticks", r1, {"contract": name, "interval": "1d", "from": WINDOW_START, "to": WINDOW_END}, run_id)
    j1 = _parse(r1)
    r2 = get("https://api.gateio.ws/api/v4/futures/usdt/funding_rate?contract=%s&from=%d&to=%d&limit=1000" % (name, S1._ms(WINDOW_START) // 1000, S1._ms(WINDOW_END) // 1000))
    m2 = S1.preserve_raw("GATE", base, "futures_funding_rate_history", r2, {"contract": name, "from": WINDOW_START, "to": WINDOW_END}, run_id)
    j2 = _parse(r2)
    act = {}
    for c in (j1 if isinstance(j1, list) else []):
        d = S1._s_to_date(c.get("t"))
        if d:
            act[d] = _f(c.get("v"))
    return {"instrument": name, "activity": act, "funding_dates": sorted({S1._s_to_date(x.get("t")) for x in (j2 if isinstance(j2, list) else []) if S1._s_to_date(x.get("t"))}),
            "funding_records": len(j2) if isinstance(j2, list) else 0, "source_ok": isinstance(j1, list) and isinstance(j2, list), "metas": [m1, m2]}


def fetch_kraken_futures(base: str, get: Callable, run_id: str, cache: dict) -> dict:
    sym = "PF_%sUSD" % base
    r1 = get("https://futures.kraken.com/api/charts/v1/trade/%s/1d?from=%d&to=%d" % (sym, S1._ms(WINDOW_START) // 1000, S1._ms(WINDOW_END) // 1000))
    m1 = S1.preserve_raw("KRAKEN", base, "futures_daily_chart_stage2", r1, {"symbol": sym, "resolution": "1d", "from": WINDOW_START, "to": WINDOW_END}, run_id)
    j1 = _parse(r1)
    r2 = get("https://futures.kraken.com/derivatives/api/v4/historicalfundingrates?symbol=%s" % sym)
    m2 = S1.preserve_raw("KRAKEN", base, "futures_historical_funding_rates", r2, {"symbol": sym}, run_id)
    j2 = _parse(r2)
    act = {}
    for c in ((j1 or {}).get("candles", []) if isinstance(j1, dict) else []):
        d = S1._ms_to_date(c.get("time"))
        if d:
            act[d] = _f(c.get("volume"))
    rates = (j2 or {}).get("rates", []) if isinstance(j2, dict) else []
    fdates = sorted({str(x.get("timestamp"))[:10] for x in rates if WINDOW_START <= str(x.get("timestamp"))[:10] <= WINDOW_END})
    return {"instrument": sym, "activity": act, "funding_dates": fdates, "funding_records": len(rates),
            "source_ok": isinstance(j1, dict) and isinstance(j2, dict), "metas": [m1, m2]}


def fetch_coinbase_intx(base: str, get: Callable, run_id: str) -> dict:
    perp = "%s-PERP" % base
    r1 = get("https://api.international.coinbase.com/api/v1/instruments/%s/candles?granularity=ONE_DAY&start=%sT00:00:00Z&end=%sT00:00:00Z" % (perp, WINDOW_START, WINDOW_END))
    m1 = S1.preserve_raw("COINBASE", base, "intx_daily_candles_stage2", r1, {"instrument": perp, "granularity": "ONE_DAY", "start": WINDOW_START, "end": WINDOW_END}, run_id)
    j1 = _parse(r1)
    act = {}
    for a in ((j1 or {}).get("aggregations", []) if isinstance(j1, dict) else []):
        d = S1._iso_to_date(a.get("start"))
        if d:
            act[d] = _f(a.get("volume"))
    return {"instrument": perp, "activity": act, "funding_dates": [], "funding_records": 0, "source_ok": isinstance(j1, dict), "metas": [m1]}


def fetch_bitfinex(base: str, get: Callable, run_id: str) -> dict:
    pair, fsym = "t%sUSD" % base, "f%s" % base
    r1 = get("https://api-pub.bitfinex.com/v2/candles/trade:1D:%s/hist?start=%d&end=%d&limit=200&sort=1" % (pair, S1._ms(WINDOW_START), S1._ms(WINDOW_END)))
    m1 = S1.preserve_raw("BITFINEX", base, "pair_daily_candles_stage2", r1, {"pair": pair, "tf": "1D", "start": WINDOW_START, "end": WINDOW_END}, run_id)
    j1 = _parse(r1)
    stats, metas, end = [], [m1], S1._ms(WINDOW_END)
    for page in range(12):
        r2 = get("https://api-pub.bitfinex.com/v2/funding/stats/%s/hist?start=%d&end=%d&limit=250" % (fsym, S1._ms(WINDOW_START), end))
        metas.append(S1.preserve_raw("BITFINEX", base, "funding_stats_history_p%02d" % page, r2, {"symbol": fsym, "start": WINDOW_START, "end_ms": end, "page": page}, run_id))
        j2 = _parse(r2)
        rows = j2 if isinstance(j2, list) else []
        stats += rows
        if len(rows) < 250:
            break
        end = min(int(x[0]) for x in rows) - 1
    r3 = get("https://api-pub.bitfinex.com/v2/candles/trade:1D:%s:a30:p2:p30/hist?start=%d&end=%d&limit=200&sort=1" % (fsym, S1._ms(WINDOW_START), S1._ms(WINDOW_END)))
    metas.append(S1.preserve_raw("BITFINEX", base, "funding_market_daily_candles", r3, {"symbol": fsym, "aggregation": "a30:p2:p30", "tf": "1D", "start": WINDOW_START, "end": WINDOW_END}, run_id))
    j3 = _parse(r3)
    act = _act_from_rows(j1, 0, 5) if isinstance(j1, list) else {}
    used_by_date: dict = {}
    for row in stats:
        d = S1._ms_to_date(row[0]) if isinstance(row, list) and row else None
        if d:
            u = _f(row[8]) if len(row) > 8 else None         # FUNDING_AMOUNT_USED
            used_by_date[d] = max(used_by_date.get(d) or 0.0, u or 0.0)
    fvol_by_date = _act_from_rows(j3, 0, 5) if isinstance(j3, list) else {}
    return {"instrument": pair, "funding_symbol": fsym, "activity": act, "funding_used_by_date": used_by_date,
            "funding_volume_by_date": fvol_by_date, "funding_records": len(stats),
            "source_ok": isinstance(j1, list) and isinstance(j2, list) and isinstance(j3, list), "metas": metas}


# --------------------------------------------------------------------------------------------
def classify_candidate(asset_symbol: str, cand: dict) -> tuple:
    home = asset_symbol.split(":")[0]
    aliases = HOME_VENUE_ALIASES.get(home, (home,))
    venue_class = VENUE_HOME if cand["venue"] in aliases else VENUE_SUBSTITUTED
    path = PATH_DERIVATIVE if cand["instrument_type"] in DERIVATIVE_TYPES else PATH_SPOT_MARGIN
    return venue_class, path


def evaluate_asset(asset: dict, get: Callable, run_id: str, cache: dict) -> dict:
    sym = asset["c22_asset"]
    base = sym.split(":")[1]
    base = {"USDT": base[:-4], "USD": base[:-3]}[("USDT" if base.endswith("USDT") else "USD")]
    per_cand = []
    for cand in asset["candidates"]:
        s1_pass_dates = {p["decision_date"] for p in asset["per_signal"] for v in p["candidate_verdicts"]
                         if v["venue_instrument_symbol"] == cand["venue_instrument_symbol"] and v["venue"] == cand["venue"] and v["verdict"] == S1.PASS}
        venue_class, path = classify_candidate(sym, cand)
        rec = {"venue": cand["venue"], "venue_instrument_symbol": cand["venue_instrument_symbol"], "instrument_type": cand["instrument_type"],
               "execution_path": path, "venue_class": venue_class, "stage1_existence_date": cand.get("existence_date"),
               "stage1_delisted_date": cand.get("delisted_date"), "stage1_pass_dates": sorted(s1_pass_dates),
               "evidence": None, "metas": [], "per_date": [], "note": None}
        if not s1_pass_dates:
            rec["note"] = "stage_one_did_not_pass_this_candidate_on_any_date"
            for p in asset["per_signal"]:
                rec["per_date"].append({"decision_date": p["decision_date"], "verdict": NOT_EVALUATED, "reason": rec["note"], "checks": {}})
            per_cand.append(rec)
            continue
        ev = None
        if path == PATH_DERIVATIVE and venue_class == VENUE_HOME:
            if cand["venue"] == "BINANCE":
                ev = fetch_binance(base, get, run_id)
            elif cand["venue"] == "BYBIT":
                ev = fetch_bybit(base, get, run_id)
            elif cand["venue"] == "OKX":
                ev = fetch_okx(base, get, run_id)
            elif cand["venue"] == "GATE":
                ev = fetch_gate(base, get, run_id)
            elif cand["venue"] == "KRAKEN_FUTURES":
                ev = fetch_kraken_futures(base, get, run_id, cache)
        elif path == PATH_DERIVATIVE and venue_class == VENUE_SUBSTITUTED and cand["venue"] == "COINBASE_INTERNATIONAL":
            ev = fetch_coinbase_intx(base, get, run_id)
        elif path == PATH_SPOT_MARGIN and cand["venue"] == "BITFINEX":
            ev = fetch_bitfinex(base, get, run_id)
        if ev is not None:
            rec["metas"] = ev.pop("metas")
            rec["evidence"] = ev
        for p in asset["per_signal"]:
            D, fills = p["decision_date"], [p["fill_date_calendar"], p["fill_date_weekday"]]
            if D not in s1_pass_dates:
                rec["per_date"].append({"decision_date": D, "verdict": NOT_EVALUATED, "reason": "stage_one_verdict_not_pass_for_this_candidate_on_this_date", "checks": {}})
                continue
            if venue_class == VENUE_SUBSTITUTED:
                v = derivative_verdict(cand.get("existence_date"), cand.get("delisted_date"), (ev or {}).get("activity", {}), (ev or {}).get("funding_dates", []), D, fills, source_ok=bool(ev and ev["source_ok"])) if ev else {"decision_date": D, "fill_dates": fills, "verdict": None, "reason": None, "checks": {}}
                evidence_only = v["verdict"]
                v.update(verdict=PENDING_VENUE, reason="substituted platform %s vs Signum-named venue %s; frozen B3 no_cross_venue_substitution=True and no explicit cross-venue approval recorded (evidence-only result kept in checks)" % (cand["venue"], sym.split(":")[0]))
                v["checks"]["evidence_only_result_if_policy_allowed"] = evidence_only
                v["checks"]["note"] = "Coinbase International perpetuals settle funding; funding history not collected here pending venue policy"
                rec["per_date"].append(v)
                continue
            if path == PATH_DERIVATIVE:
                rec["per_date"].append(derivative_verdict(cand.get("existence_date"), cand.get("delisted_date"), ev["activity"], ev["funding_dates"], D, fills, short_supported=True, source_ok=ev["source_ok"]))
            elif cand["venue"] == "BITFINEX":
                rec["per_date"].append(bitfinex_margin_verdict(ev["activity"], ev["funding_used_by_date"], ev["funding_volume_by_date"], D, fills, source_ok=ev["source_ok"]))
            elif cand["venue"] == "COINBASE" and cand["instrument_type"] == "spot_pair":
                rec["per_date"].append({"decision_date": D, "fill_dates": fills, "verdict": FAIL_NOT_SHORTABLE, "reason": "Coinbase Exchange spot product; margin_enabled=false; cannot open a short", "checks": {}})
            else:
                which = UNRES_BORROW if cand["venue"] in ("OKX",) else UNRES_MARGIN
                rec["per_date"].append({"decision_date": D, "fill_dates": fills, "verdict": which, "reason": "venue exposes no first-party HISTORICAL margin/borrow state for %s; present-day flag is non-decisive" % cand["venue_instrument_symbol"], "checks": {}})
        per_cand.append(rec)
    per_signal = []
    for p in asset["per_signal"]:
        cvs = []
        for rec in per_cand:
            pd = next(x for x in rec["per_date"] if x["decision_date"] == p["decision_date"])
            cvs.append({"venue": rec["venue"], "venue_instrument_symbol": rec["venue_instrument_symbol"], "execution_path": rec["execution_path"],
                        "venue_class": rec["venue_class"], "verdict": pd["verdict"], "reason": pd["reason"]})
        sv = signal_verdict([c for c in cvs if c["verdict"] != NOT_EVALUATED]) if any(c["verdict"] != NOT_EVALUATED for c in cvs) else NOT_EVALUATED
        per_signal.append({"decision_date": p["decision_date"], "signal": p["signal"], "fill_date_calendar": p["fill_date_calendar"], "fill_date_weekday": p["fill_date_weekday"],
                           "stage1_verdict": p["signal_verdict"], "stage2_verdict": sv,
                           "execution_path_used": next((c["execution_path"] for c in cvs if c["verdict"] == PASS and c["venue_class"] == VENUE_HOME), None),
                           "passing_instruments": [c["venue_instrument_symbol"] for c in cvs if c["verdict"] == PASS and c["venue_class"] == VENUE_HOME],
                           "candidate_verdicts": cvs})
    norm = {"stage": STAGE, "stage_version": STAGE_VERSION, "c22_asset": sym, "mapping_risk": asset["mapping_risk"],
            "stage1_run_of_record": STAGE1_RUN_OF_RECORD, "stage1_report_sha256": STAGE1_REPORT_SHA256,
            "candidates": [{k: v for k, v in rec.items() if k != "metas"} | {"evidence_sources": [
                {"endpoint": m["endpoint"], "query_params": m["query_params"], "raw_sha256": m["raw_sha256"], "http_status": m["http_status"]} for m in rec["metas"]]} for rec in per_cand],
            "per_signal": per_signal}
    out = dict(norm, normalized_evidence_sha256=S1._sha(S1._canon(norm)), run_id=run_id,
               raw_evidence_files={m["raw_sha256"]: m["raw_path"] for rec in per_cand for m in rec["metas"]},
               retrieval_utc=sorted({m["retrieved_utc"] for rec in per_cand for m in rec["metas"]}))
    for k in (PASS, PENDING_VENUE):
        out["signals_%s" % k.lower()] = sum(1 for p in per_signal if p["stage2_verdict"] == k)
    out["signals_failed"] = sum(1 for p in per_signal if p["stage2_verdict"].startswith("FAIL"))
    out["signals_unresolved"] = sum(1 for p in per_signal if p["stage2_verdict"].startswith("UNRESOLVED"))
    out["signals_not_evaluated"] = sum(1 for p in per_signal if p["stage2_verdict"] == NOT_EVALUATED)
    return out


def write_registry(rec: dict) -> Path:
    S1.REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
    venue, base = rec["c22_asset"].split(":")
    p = S1.REGISTRY_DIR / ("%s__%s__historical_shortability__%s.json" % (venue, base, rec["run_id"]))
    if p.exists():
        raise Stage2Error("refuse_overwrite_registry:%s" % p.name)
    tmp = p.with_suffix(".tmp")
    tmp.write_bytes(json.dumps(rec, indent=2, sort_keys=True, default=str).encode("utf-8") + b"\n")
    os.replace(tmp, p)
    p.with_suffix(".json.sha256").write_text(S1._sha(p.read_bytes()) + "\n", encoding="utf-8")
    return p


def write_candidate_admission(rec: dict) -> Path:
    """Candidate-admission artifact per frozen B3 evidence categories. NOT an admission: the
    fee-honest shell reads only manifests/<venue>__<base>__evidence_manifest.json carrying the
    human admission token, which this never writes."""
    CANDIDATE_ADMISSION_DIR.mkdir(parents=True, exist_ok=True)
    venue, base = rec["c22_asset"].split(":")
    passing = [c for c in rec["candidates"] if any(d["verdict"] == PASS for d in c["per_date"]) and c["venue_class"] == VENUE_HOME]
    art = {"stage": STAGE, "run_id": rec["run_id"], "c22_asset": rec["c22_asset"],
           "admission_status": "CANDIDATE_PENDING_HUMAN_ADMIT_NOT_ADMITTED",
           "required_human_token": "HUMAN_DECISION_C22_HISTORICAL_INSTRUMENT_EVIDENCE_ADMIT_OR_REJECT=ADMIT",
           "candidate_instruments": [{"venue": c["venue"], "symbol": c["venue_instrument_symbol"], "execution_path": c["execution_path"],
                                      "dates_pass": [d["decision_date"] for d in c["per_date"] if d["verdict"] == PASS]} for c in passing],
           "evidence_categories_covered": {
               "canonical_asset_identity": "STAGE_ONE", "historical_execution_instrument": "STAGE_ONE", "venue": "STAGE_ONE",
               "instrument_existence_on_required_dates": "STAGE_ONE",
               "historical_shortability_mechanism": "STAGE_TWO" if passing else "NOT_ESTABLISHED",
               "historical_ohlc_coverage": "STAGE_TWO_WINDOW_ONLY_%s_%s" % (WINDOW_START, WINDOW_END),
               "funding_or_borrow_requirement": "MECHANISM_EVIDENCE_ONLY_NO_COST_ARITHMETIC" if passing else "NOT_ESTABLISHED",
               "fee_schedule": "NOT_COLLECTED_LATER_STAGE", "minimum_quantity_or_notional": "NOT_COLLECTED_LATER_STAGE",
               "tick_lot_constraints": "NOT_COLLECTED_LATER_STAGE", "liquidity_spread_evidence": "NOT_COLLECTED_LATER_STAGE"},
           "registry_sha256": rec.get("registry_sha256"), "normalized_evidence_sha256": rec["normalized_evidence_sha256"]}
    p = CANDIDATE_ADMISSION_DIR / ("%s__%s__candidate_admission__%s.json" % (venue, base, rec["run_id"]))
    if p.exists():
        raise Stage2Error("refuse_overwrite_candidate_admission:%s" % p.name)
    p.write_bytes(S1._canon(art))
    return p


def run_stage2(get: Callable = http_get, run_id: str | None = None, sleep_s: float = 0.25, stage1: dict | None = None) -> dict:
    run_id = run_id or _dt.now(_tz.utc).strftime("%Y%m%dT%H%M%SZ")
    s1 = stage1 or load_stage1_of_record()
    cache: dict = {}
    records = []
    for asset in sorted(s1["assets"], key=lambda a: a["c22_asset"]):
        rec = evaluate_asset(asset, get, run_id, cache)
        p = write_registry(rec)
        rec["registry_path"], rec["registry_sha256"] = S1._rel(p), S1._sha(p.read_bytes())
        rec["candidate_admission_path"] = S1._rel(write_candidate_admission(rec))
        records.append(rec)
        if sleep_s:
            time.sleep(sleep_s)
    all_sig = [(r["c22_asset"], p) for r in records for p in r["per_signal"]]
    total = len(all_sig)
    s1_survivors = [x for x in all_sig if x[1]["stage1_verdict"] == S1.PASS]
    counts = {v: sum(1 for _, p in all_sig if p["stage2_verdict"] == v) for v in VERDICTS}
    assert total == 75 and sum(counts.values()) == 75, "stage2_accounting_broken"
    paths = {}
    for _, p in s1_survivors:
        if p["stage2_verdict"] == PASS:
            paths[p["execution_path_used"]] = paths.get(p["execution_path_used"], 0) + 1
    reasons = {}
    for a, p in all_sig:
        if p["stage2_verdict"] != PASS:
            for c in p["candidate_verdicts"]:
                if c["verdict"] != NOT_EVALUATED:
                    reasons["%s | %s | %s | %s" % (a, p["decision_date"], c["venue_instrument_symbol"], c["verdict"])] = c["reason"]
    further = {}
    for r in records:
        why = []
        if r["signals_pending_venue_policy"]:
            why.append("venue_policy_decision_required")
        if r["signals_unresolved"]:
            why.append("unresolved_historical_state")
        if any(c["venue"] == "BITFINEX" and any(d["verdict"] == PASS for d in c["per_date"]) for c in r["candidates"]):
            why.append("margin_enablement_history_inferred_from_borrow_market_second_source_recommended")
        if r["mapping_risk"] != "STANDARD_MAPPING":
            why.append("mapping_risk:%s" % r["mapping_risk"])
        if why:
            further[r["c22_asset"]] = why
    funnel = {"frozen_short_signals": 75, "stage1_survivors": len(s1_survivors), "stage2_pass": counts[PASS],
              "stage2_pending_venue_policy": counts[PENDING_VENUE],
              "stage2_fail": sum(v for k, v in counts.items() if k.startswith("FAIL")),
              "stage2_unresolved": sum(v for k, v in counts.items() if k.startswith("UNRESOLVED")),
              "stage1_eliminated_preserved": total - len(s1_survivors),
              "admitted_for_fee_honest_replay": 0, "admitted_note": "no human admission token; precondition shell must still fail closed"}
    stage3 = counts[PASS] > 0 and funnel["stage2_unresolved"] == 0
    return {"report": "c22_b3_stage2_historical_shortability", "stage": STAGE, "stage_version": STAGE_VERSION, "run_id": run_id,
            "mode": "READ_ONLY_HISTORICAL_SHORTABILITY_EVIDENCE_ONLY",
            "stage1_run_of_record": STAGE1_RUN_OF_RECORD, "stage1_report_sha256": STAGE1_REPORT_SHA256,
            "window": [WINDOW_START, WINDOW_END], "short_signals": total, "verdict_counts": counts, "execution_paths_used": paths,
            "assets": records, "reasons": reasons, "further_evidence_required": further, "funnel": funnel,
            "raw_evidence_files": sorted({(path, sha) for r in records for sha, path in r["raw_evidence_files"].items()}),
            "registry_files": [{"path": r["registry_path"], "sha256": r["registry_sha256"]} for r in records],
            "candidate_admission_files": [r["candidate_admission_path"] for r in records],
            "venue_policy": {"rule": "frozen B3: no_cross_venue_substitution=True per asset; human decision approve_home_venue_implementation_or_explicit_cross_venue_approval required", "explicit_cross_venue_approval_recorded": False},
            "tel_status": "STAGE_ONE_ELIMINATION_PRESERVED_NO_ALTERNATIVE_VENUE_SEARCHED",
            "stage_three_request_ready": bool(stage3), "stage_three_started": False,
            "c22_performance_computed": False, "cost_arithmetic_performed": False, "strategy_rules_modified": False,
            "v2_modified": False, "exports_modified": False, "admission_state_changed": False}


def render_markdown(r: dict) -> str:
    f = r["funnel"]
    L = ["# C22 — B3 Stage Two: Historical Shortability Evidence (run %s)" % r["run_id"], "",
         "Read-only. Answers only whether a NEW short could have been opened on the required dates. No performance, no cost arithmetic, no admission change.", "",
         "- Stage One of record: `%s` (sha `%s`)" % (r["stage1_run_of_record"], r["stage1_report_sha256"]),
         "- Funnel: frozen %d → Stage One survivors %d → Stage Two PASS **%d** · PENDING_VENUE_POLICY %d · FAIL %d · UNRESOLVED %d · Stage One eliminations preserved %d · admitted for fee-honest replay %d" % (
             f["frozen_short_signals"], f["stage1_survivors"], f["stage2_pass"], f["stage2_pending_venue_policy"], f["stage2_fail"], f["stage2_unresolved"], f["stage1_eliminated_preserved"], f["admitted_for_fee_honest_replay"]),
         "- Execution paths used by passing signals: %s" % json.dumps(r["execution_paths_used"], sort_keys=True),
         "- Venue policy: %s (explicit cross-venue approval recorded: %s)" % (r["venue_policy"]["rule"], r["venue_policy"]["explicit_cross_venue_approval_recorded"]),
         "- TEL: %s" % r["tel_status"],
         "- Stage Three request ready: **%s** · started: %s" % (r["stage_three_request_ready"], r["stage_three_started"]), ""]
    for a in r["assets"]:
        L += ["## %s (risk %s) — PASS %d · PENDING %d · FAIL %d · UNRESOLVED %d" % (a["c22_asset"], a["mapping_risk"], a["signals_pass_historical_shortability"], a["signals_pending_venue_policy"], a["signals_failed"], a["signals_unresolved"]), "",
              "| candidate | path | venue class | S1 existence | activity dates | funding records |", "|---|---|---|---|---|---|"]
        for c in a["candidates"]:
            ev = c.get("evidence") or {}
            L.append("| %s @ %s | %s | %s | %s | %d | %s |" % (c["venue_instrument_symbol"], c["venue"], c["execution_path"], c["venue_class"], c["stage1_existence_date"],
                                                           len(ev.get("activity") or {}), ev.get("funding_records", "—")))
        L += ["", "| date | signal | S1 | **S2** | path | passing | candidate verdicts |", "|---|---|---|---|---|---|---|"]
        for p in a["per_signal"]:
            L.append("| %s | %s | %s | **%s** | %s | %s | %s |" % (p["decision_date"], p["signal"], p["stage1_verdict"], p["stage2_verdict"], p["execution_path_used"] or "—",
                                                                ", ".join(p["passing_instruments"]) or "—", "; ".join("%s=%s" % (c["venue_instrument_symbol"], c["verdict"]) for c in p["candidate_verdicts"])))
        L.append("")
    L += ["## Sources and hashes", "", "| raw file | sha256 |", "|---|---|"]
    for path, sha in r["raw_evidence_files"]:
        L.append("| %s | `%s` |" % (path, sha))
    L += ["", "## Reasons for every non-PASS candidate verdict", ""]
    for k, v in sorted(r["reasons"].items()):
        L.append("- %s → %s" % (k, v))
    L += ["", "## Further evidence required", ""]
    for k, v in r["further_evidence_required"].items():
        L.append("- %s: %s" % (k, ", ".join(v)))
    return "\n".join(L) + "\n"


def write_report(r: dict) -> dict:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    base = REPORT_DIR / ("c22_b3_stage2_historical_shortability_%s" % r["run_id"])
    jp, mp = base.with_suffix(".json"), base.with_suffix(".md")
    for p in (jp, mp):
        if p.exists():
            raise Stage2Error("refuse_overwrite_report:%s" % p.name)
    blob = json.dumps(r, indent=2, sort_keys=True, default=str).encode("utf-8") + b"\n"
    tmp = jp.with_suffix(".tmp"); tmp.write_bytes(blob); os.replace(tmp, jp)
    tmp = mp.with_suffix(".tmp"); tmp.write_bytes(render_markdown(r).encode("utf-8")); os.replace(tmp, mp)
    S1.MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    man = S1.MANIFEST_DIR / ("stage2_run_manifest__%s.json" % r["run_id"])
    man.write_bytes(S1._canon({"stage": STAGE, "run_id": r["run_id"], "report_json": S1._rel(jp), "report_sha256": S1._sha(blob),
                               "raw_evidence_files": r["raw_evidence_files"], "registry_files": r["registry_files"],
                               "candidate_admission_files": r["candidate_admission_files"],
                               "note": "STAGE TWO ONLY: not an admission manifest; the fee-honest precondition shell must keep failing closed."}))
    return {"report_json": S1._rel(jp), "report_md": S1._rel(mp), "report_sha256": S1._sha(blob), "run_manifest": S1._rel(man)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", default=None)
    a = ap.parse_args(argv)
    r = run_stage2(run_id=a.run_id)
    w = write_report(r)
    print(json.dumps({"run_id": r["run_id"], "funnel": r["funnel"], "verdict_counts": {k: v for k, v in r["verdict_counts"].items() if v},
                      "execution_paths_used": r["execution_paths_used"], "stage_three_request_ready": r["stage_three_request_ready"], **w}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
