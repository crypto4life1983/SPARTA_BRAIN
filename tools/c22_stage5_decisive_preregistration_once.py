"""Candidate #22 -- STAGE 5: DECISIVE REPLAY PRE-REGISTRATION + GOVERNANCE FREEZE (READ-ONLY research).

Operator instruction 2026-09-11: "resolve it then and do everything we have to do." This tool
(1) collects the last evidence the decisive run needs (long-side spot OHLC + constraints for the
13 LONG signals at their home venues; funding settlements for every perpetual through the data
boundary; Bitfinex LEO funding-rate observations), (2) FREEZES every execution rule, cost value
and assumption with its evidence class BEFORE any performance is computed, (3) records the
outstanding lifecycle decisions as present-day operator approvals (never historical), and (4)
writes per-instrument evidence manifests in the frozen B3 layout so the fee-honest precondition
shell can evaluate them. It computes NO P&L. Assumptions are deterministic rules fixed here and
labelled FROZEN_CONSERVATIVE_ASSUMPTION; nothing is chosen with reference to results.

Conservative fee rule (deterministic): taker_bps(venue, product) = max over that venue's OBSERVED
first-party retail taker values (dated bracket, dated current-only, contract API); if the venue
has none observed -> the global max across all venues' observed values for that product class.
No maker rebate, token discount, VIP or promotion ever applied.
Slippage rule: Kraken fills use the observed derived half-spread at 00:00 UTC (DERIVED); every
other fill uses the assumption ceil(max observed Kraken median spread / 2) = 25 bps per side.
Capacity rule: order notional must not exceed observed first-party liquidity at the fill
(Binance: resting notional within 0.2% on the hit side; Kraken: liquidity_005 x price on the hit
side; trade-only venues: 30-minute traded quote notional; spot longs: 1% of the venue's daily
quote volume on the fill date). Violations are deterministic FILL_CAPACITY_EXCEEDED rejections.
"""
from __future__ import annotations

import argparse
import json
import math
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

import sparta_commander.c22_replay_cost_engine_contract as C  # noqa: E402
import tools.c22_b3_stage1_instrument_existence_once as S1  # noqa: E402
import tools.c22_b3_stage2_historical_shortability_once as S2  # noqa: E402
import tools.c22_b3_stage3_historical_ohlc_once as S3  # noqa: E402
import tools.c22_b3_stage4_fees_liquidity_once as S4  # noqa: E402
import tools.c22_b3_stage4a_t2_recovery_once as S4A  # noqa: E402
import tools.c22_replay_dry_run_once as DR  # noqa: E402

STAGE = "STAGE_5_DECISIVE_REPLAY_PREREGISTRATION"
STAGE_VERSION = "c22_stage5_prereg_v2"
DECISION_DATE = "2026-09-11"
OPERATOR_INSTRUCTION = "resolve it then and do everything we have to do"
STAGE4A_RUN = "20260911T200048Z"
STAGE4A_REPORT = REPO_ROOT / "reports" / "c22_gc_b3_stage4a" / ("c22_b3_stage4a_t2_recovery_%s.json" % STAGE4A_RUN)
STAGE4A_SHA256 = "d77b17824e5edcf4a449a4c58abaf09efdd862286b37e3604ec4403eb24ea163"
GOVERNANCE_DIR = REPO_ROOT / "reports" / "c22_gc_governance"
APPROVALS_DIR = REPO_ROOT / "reports" / "approvals"
_USER_AGENT = "sparta-brain-c22-stage5-readonly/1.0"
RANGE_START, RANGE_END = "2026-06-20", "2026-09-10"
REPLAY_BOUNDARY = "2026-09-09"

ALLOWED_URL_PREFIXES = (
    "https://api.binance.com/api/v3/klines", "https://api.binance.com/api/v3/exchangeInfo",
    "https://api.exchange.coinbase.com/products/",
    "https://api.kraken.com/0/public/OHLC", "https://api.kraken.com/0/public/AssetPairs",
    "https://fapi.binance.com/fapi/v1/fundingRate",
    "https://api.bybit.com/v5/market/funding/history",
    "https://www.okx.com/api/v5/public/funding-rate-history",
    "https://api.gateio.ws/api/v4/futures/usdt/funding_rate",
    "https://futures.kraken.com/derivatives/api/v4/historicalfundingrates",
    "https://api-pub.bitfinex.com/v2/funding/stats/",
)

# evidence classes (Stage Four vocabulary)
OBSERVED, DERIVED, ASSUMPTION, SENSITIVITY, UNRESOLVED = S4.OBSERVED, S4.DERIVED, S4.ASSUMPTION, S4.SENSITIVITY, S4.UNRESOLVED

# frozen governance values (operator-authorized 2026-09-11)
NAV_USD = 10_000.0                       # research-scale account; ASSUMPTION; sensitivity 100_000
NAV_SENSITIVITY_USD = 100_000.0
SLIPPAGE_ASSUMPTION_BPS = 25.0           # ceil(max observed Kraken median spread 44.43 / 2)
LONG_CAPACITY_FRACTION_OF_DAILY_VOLUME = 0.01
DECISIVE_PROFILE = "V2_CONTRACT_EXACT"
SENSITIVITY_PROFILE = "CRYPTO_CALENDAR_SENSITIVITY"
RANDOM_MASTER_SEED = 20260911
RANDOM_RESAMPLES = 500

LONG_INSTRUMENTS = {  # home-venue spot products for the 8 LONG assets
    "BINANCE:AAVEUSDT": ("BINANCE_SPOT", "AAVEUSDT"), "BINANCE:DEXEUSDT": ("BINANCE_SPOT", "DEXEUSDT"),
    "BINANCE:JSTUSDT": ("BINANCE_SPOT", "JSTUSDT"), "BINANCE:JUPUSDT": ("BINANCE_SPOT", "JUPUSDT"),
    "BINANCE:ZECUSDT": ("BINANCE_SPOT", "ZECUSDT"), "COINBASE:AEROUSD": ("COINBASE_EXCHANGE", "AERO-USD"),
    "COINBASE:MORPHOUSD": ("COINBASE_EXCHANGE", "MORPHO-USD"), "KRAKEN:SPXUSD": ("KRAKEN_SPOT", "SPXUSD"),
}


class Stage5Error(RuntimeError):
    pass


def _assert_safe_url(url: str) -> None:
    if not url.startswith("https://") or not any(url.startswith(p) for p in ALLOWED_URL_PREFIXES):
        raise Stage5Error("refusing non-allowlisted url: %s" % url)
    low = url.lower()
    for frag in S1.FORBIDDEN_URL_FRAGMENTS:
        if frag in low:
            raise Stage5Error("refusing url containing forbidden fragment %r" % frag)


def http_get(url: str, timeout: float = 60.0) -> dict:
    _assert_safe_url(url)
    req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT}, method="GET")
    retrieved = _dt.now(_tz.utc).isoformat(timespec="seconds")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return {"url": url, "status": r.status, "retrieved_utc": retrieved, "raw_bytes": r.read()}
    except urllib.error.HTTPError as e:
        return {"url": url, "status": e.code, "retrieved_utc": retrieved, "raw_bytes": e.read()[:4000]}


def _parse(r):
    try:
        return json.loads(r["raw_bytes"].decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return None


def _f(x):
    return S2._f(x)


# --------------------------------------------------------------------------------------------
# long-side spot evidence
# --------------------------------------------------------------------------------------------
def fetch_long_spot(asset: str, venue: str, inst: str, get: Callable, run_id: str, cache: dict) -> dict:
    base = asset.split(":")[1]
    base = base[:-4] if base.endswith("USDT") else base[:-3]
    rows, metas, cons, ok = [], [], None, True
    ms_s, ms_e = S1._ms(RANGE_START), S1._ms(RANGE_END) + 86_399_000
    if venue == "BINANCE_SPOT":
        r = get("https://api.binance.com/api/v3/klines?symbol=%s&interval=1d&startTime=%d&endTime=%d&limit=1000" % (inst, ms_s, ms_e))
        metas.append(S1.preserve_raw("BINANCE", base, "stage5_spot_daily_klines", r, {"symbol": inst, "interval": "1d", "start": RANGE_START, "end": RANGE_END}, run_id))
        j = _parse(r)
        ok = isinstance(j, list)
        rows = S3._rows_from(j, 0, 1, 2, 3, 4, 5) if ok else []
        # quote volume is column 7 on Binance
        qv = {S1._ms_to_date(x[0]): _f(x[7]) for x in (j if ok else []) if S1._ms_to_date(x[0])}
        for rr in rows:
            rr["quote_volume"] = qv.get(rr["date"])
        if "binance_spot_info" not in cache:
            r2 = get("https://api.binance.com/api/v3/exchangeInfo?symbols=%s" % json.dumps([v[1] for v in LONG_INSTRUMENTS.values() if v[0] == "BINANCE_SPOT"]).replace(" ", ""))
            cache["binance_spot_info"] = (S1.preserve_raw("BINANCE", "_shared", "stage5_spot_exchangeinfo", r2, {"symbols": "long cohort"}, run_id), _parse(r2))
        m2, j2 = cache["binance_spot_info"]
        metas.append(m2)
        row = next((s for s in ((j2 or {}).get("symbols") or []) if s.get("symbol") == inst), None)
        if row:
            f = {x["filterType"]: x for x in row.get("filters", [])}
            cons = {"tick_size": _f(f.get("PRICE_FILTER", {}).get("tickSize")), "lot_step": _f(f.get("LOT_SIZE", {}).get("stepSize")),
                    "min_qty": _f(f.get("LOT_SIZE", {}).get("minQty")), "min_notional": _f((f.get("NOTIONAL") or f.get("MIN_NOTIONAL") or {}).get("minNotional")),
                    "status": row.get("status"), "existence_evidence": "first official spot candle in range"}
    elif venue == "COINBASE_EXCHANGE":
        r = get("https://api.exchange.coinbase.com/products/%s/candles?granularity=86400&start=%sT00:00:00Z&end=%sT00:00:00Z" % (inst, RANGE_START, RANGE_END))
        metas.append(S1.preserve_raw("COINBASE", base, "stage5_exchange_daily_candles", r, {"product": inst, "granularity": 86400, "start": RANGE_START, "end": RANGE_END}, run_id))
        j = _parse(r)
        ok = isinstance(j, list)
        # coinbase: [time, low, high, open, close, volume(base)]
        rows = S3._rows_from(j, 0, 3, 2, 1, 4, 5, ms=False) if ok else []
        for rr in rows:
            rr["quote_volume"] = (rr["volume"] or 0) * (rr["close"] or 0)
        r2 = get("https://api.exchange.coinbase.com/products/%s" % inst)
        metas.append(S1.preserve_raw("COINBASE", base, "stage5_exchange_product", r2, {"product": inst}, run_id))
        j2 = _parse(r2) or {}
        if j2.get("id") == inst:
            cons = {"tick_size": _f(j2.get("quote_increment")), "lot_step": _f(j2.get("base_increment")), "min_qty": None,
                    "min_notional": _f(j2.get("min_market_funds")), "status": j2.get("status"), "existence_evidence": "first official candle in range"}
    elif venue == "KRAKEN_SPOT":
        r = get("https://api.kraken.com/0/public/OHLC?pair=%s&interval=1440&since=%d" % (inst, S1._ms(RANGE_START) // 1000 - 86400))
        metas.append(S1.preserve_raw("KRAKEN", base, "stage5_spot_daily_ohlc", r, {"pair": inst, "interval": 1440, "since": RANGE_START}, run_id))
        j = _parse(r)
        res = (j or {}).get("result", {}) if isinstance(j, dict) else {}
        key = next((k for k in res if k != "last"), None)
        ok = key is not None
        # kraken: [time, open, high, low, close, vwap, volume, count]
        rows = [x for x in (S3._rows_from(res.get(key), 0, 1, 2, 3, 4, 6, ms=False) if ok else []) if RANGE_START <= x["date"] <= RANGE_END]
        for rr in rows:
            rr["quote_volume"] = (rr["volume"] or 0) * (rr["close"] or 0)
        r2 = get("https://api.kraken.com/0/public/AssetPairs?pair=%s" % inst)
        metas.append(S1.preserve_raw("KRAKEN", base, "stage5_spot_assetpairs", r2, {"pair": inst}, run_id))
        j2 = _parse(r2) or {}
        prow = next(iter((j2.get("result") or {}).values()), None)
        if prow:
            cons = {"tick_size": _f(prow.get("tick_size")), "lot_step": 10 ** -int(prow.get("lot_decimals", 0)), "min_qty": _f(prow.get("ordermin")),
                    "min_notional": _f(prow.get("costmin")), "status": prow.get("status"), "existence_evidence": "first official candle in range"}
    return {"asset": asset, "venue": venue, "instrument": inst, "rows": rows, "source_ok": ok, "constraints": cons,
            "first_date": rows[0]["date"] if rows else None, "last_date": rows[-1]["date"] if rows else None,
            "coverage": S3.coverage(rows, RANGE_START, REPLAY_BOUNDARY) if ok else None,
            "raw_sources": [{"endpoint": m["endpoint"], "raw_sha256": m["raw_sha256"], "raw_path": m["raw_path"]} for m in metas]}


# --------------------------------------------------------------------------------------------
# funding through the boundary (perps) + Bitfinex borrow observations
# --------------------------------------------------------------------------------------------
def fetch_funding_full(venue: str, inst: str, base: str, get: Callable, run_id: str, cache: dict) -> dict:
    ms_s, ms_e = S1._ms(RANGE_START), S1._ms(RANGE_END) + 86_399_000
    recs, metas = [], []
    if venue == "BINANCE":
        cur = ms_s
        for page in range(6):
            r = get("https://fapi.binance.com/fapi/v1/fundingRate?symbol=%s&startTime=%d&endTime=%d&limit=1000" % (inst, cur, ms_e))
            metas.append(S1.preserve_raw("BINANCE", base, "stage5_funding_full_p%02d" % page, r, {"symbol": inst, "start_ms": cur, "end": RANGE_END, "page": page}, run_id))
            j = _parse(r) or []
            for x in j:
                recs.append({"ts_ms": int(x["fundingTime"]), "rate": _f(x["fundingRate"]), "mark": _f(x.get("markPrice"))})
            if len(j) < 1000:
                break
            cur = int(j[-1]["fundingTime"]) + 1
    elif venue == "BYBIT":
        end = ms_e
        for page in range(8):
            r = get("https://api.bybit.com/v5/market/funding/history?category=linear&symbol=%s&startTime=%d&endTime=%d&limit=200" % (inst, ms_s, end))
            metas.append(S1.preserve_raw("BYBIT", base, "stage5_funding_full_p%02d" % page, r, {"symbol": inst, "start": RANGE_START, "end_ms": end, "page": page}, run_id))
            lst = ((_parse(r) or {}).get("result") or {}).get("list") or []
            for x in lst:
                recs.append({"ts_ms": int(x["fundingRateTimestamp"]), "rate": _f(x["fundingRate"]), "mark": None})
            if len(lst) < 200:
                break
            end = min(int(x["fundingRateTimestamp"]) for x in lst) - 1
    elif venue == "OKX":
        after = ms_e + 1
        for page in range(12):
            r = get("https://www.okx.com/api/v5/public/funding-rate-history?instId=%s&after=%d&before=%d&limit=100" % (inst, after, ms_s - 1))
            metas.append(S1.preserve_raw("OKX", base, "stage5_funding_full_p%02d" % page, r, {"instId": inst, "after_ms": after, "before": RANGE_START, "page": page}, run_id))
            data = (_parse(r) or {}).get("data") or []
            for x in data:
                recs.append({"ts_ms": int(x["fundingTime"]), "rate": _f(x.get("realizedRate") or x.get("fundingRate")), "mark": None})
            if len(data) < 100:
                break
            after = min(int(x["fundingTime"]) for x in data)
    elif venue == "GATE":
        r = get("https://api.gateio.ws/api/v4/futures/usdt/funding_rate?contract=%s&from=%d&to=%d&limit=1000" % (inst, ms_s // 1000, ms_e // 1000))
        metas.append(S1.preserve_raw("GATE", base, "stage5_funding_full", r, {"contract": inst, "from": RANGE_START, "to": RANGE_END}, run_id))
        for x in (_parse(r) or []):
            recs.append({"ts_ms": int(x["t"]) * 1000, "rate": _f(x["r"]), "mark": None})
    elif venue == "KRAKEN_FUTURES":
        r = get("https://futures.kraken.com/derivatives/api/v4/historicalfundingrates?symbol=%s" % inst)
        metas.append(S1.preserve_raw("KRAKEN", base, "stage5_funding_full", r, {"symbol": inst}, run_id))
        for x in ((_parse(r) or {}).get("rates") or []):
            ts = str(x.get("timestamp"))
            if RANGE_START <= ts[:10] <= RANGE_END:
                recs.append({"ts_ms": int(_dt.fromisoformat(ts.replace("Z", "+00:00")).timestamp() * 1000), "rate": _f(x.get("relativeFundingRate")), "mark": None,
                             "note": "relativeFundingRate is the hourly rate relative to price"})
    recs = sorted({r_["ts_ms"]: r_ for r_ in recs}.values(), key=lambda x: x["ts_ms"])
    return {"venue": venue, "instrument": inst, "records": recs, "count": len(recs),
            "first": S1._ms_to_date(recs[0]["ts_ms"]) if recs else None, "last": S1._ms_to_date(recs[-1]["ts_ms"]) if recs else None,
            "class": OBSERVED, "raw_sources": [{"endpoint": m["endpoint"], "raw_sha256": m["raw_sha256"], "raw_path": m["raw_path"]} for m in metas]}


def fetch_bitfinex_borrow_obs(get: Callable, run_id: str) -> dict:
    ms_s, ms_e = S1._ms("2026-07-13"), S1._ms("2026-07-23")
    stats, metas, end = [], [], ms_e
    for page in range(6):
        r = get("https://api-pub.bitfinex.com/v2/funding/stats/fLEO/hist?start=%d&end=%d&limit=250" % (ms_s, end))
        metas.append(S1.preserve_raw("BITFINEX", "LEO", "stage5_funding_stats_p%02d" % page, r, {"symbol": "fLEO", "start_ms": ms_s, "end_ms": end, "page": page}, run_id))
        rows = _parse(r) or []
        stats += rows
        if len(rows) < 250:
            break
        end = min(int(x[0]) for x in rows) - 1
    frr = [(_f(x[3]) or 0.0) for x in stats if isinstance(x, list) and len(x) > 3]
    return {"symbol": "fLEO", "hourly_rows": len(stats), "frr_max_daily": max(frr) if frr else None, "frr_min_daily": min(frr) if frr else None,
            "class": OBSERVED, "note": "FRR (flash return rate, daily) observed on the official funding stats; 0 across the window", "raw_sources": [{"endpoint": m["endpoint"], "raw_sha256": m["raw_sha256"], "raw_path": m["raw_path"]} for m in metas]}


# --------------------------------------------------------------------------------------------
# frozen rules
# --------------------------------------------------------------------------------------------
def fee_rule(stage4a: dict) -> dict:
    """Deterministic conservative taker fee per venue/product from Stage 4A observed values."""
    observed_perp = {"BINANCE": [], "BYBIT": [5.5], "OKX": [5.0], "GATE": [5.0, 7.5], "KRAKEN_FUTURES": [5.0], "BITFINEX": [0.0]}
    observed_spot = {"BINANCE_SPOT": [], "COINBASE_EXCHANGE": [], "KRAKEN_SPOT": [80.0], "OKX_SPOT": [10.0]}
    gmax_perp = max(v for vs in observed_perp.values() for v in vs)
    gmax_spot = max(v for vs in observed_spot.values() for v in vs)
    out = {}
    for venue, vs in observed_perp.items():
        out[venue] = {"taker_bps": max(vs) if vs else gmax_perp, "maker_bps_applied": None, "class": (OBSERVED if vs else ASSUMPTION),
                      "basis": ("max of venue-observed retail taker values %s" % vs) if vs else "no venue-observed value; global max of observed perp retail taker values (%s bps, Gate contract API)" % gmax_perp,
                      "stage4a_grade": {"BINANCE": "UNRESOLVED", "BYBIT": "CURRENT_ONLY", "OKX": "CURRENT_ONLY", "GATE": "UNRESOLVED(conflict)", "KRAKEN_FUTURES": "T2_HISTORICAL_FEE_BRACKETED", "BITFINEX": "T2_HISTORICAL_FEE_BRACKETED"}[venue]}
    for venue, vs in observed_spot.items():
        out[venue] = {"taker_bps": max(vs) if vs else gmax_spot, "maker_bps_applied": None, "class": (OBSERVED if vs else ASSUMPTION),
                      "basis": ("max of venue-observed spot retail taker values %s" % vs) if vs else "no venue-observed value; global max of observed spot retail taker values (%s bps, Kraken Pro base tier)" % gmax_spot}
    out["_rule"] = "taker_bps = max(venue-observed first-party retail taker values); else global max across venues for the product class; no maker rebate / token discount / VIP / promotion; all fills treated as taker"
    out["_sensitivities"] = {"37bps_round_trip_convention": {"taker_bps": 13.5, "slippage_bps": 5.0, "class": SENSITIVITY},
                             "spot_low_observed": {"spot_taker_bps": 10.0, "class": SENSITIVITY, "basis": "OKX regular-user spot taker (lowest observed)"}}
    return out


def build_prereg(stage4a: dict, stage4: dict, longs: dict, funding: dict, borrow_obs: dict, run_id: str) -> dict:
    fees = fee_rule(stage4a)
    # constraints per instrument: shorts from Stage Four (with GRAM tick override), longs from this run
    constraints = {}
    for asset, s in stage4["step5_per_instrument"].items():
        cv = dict(s["constraints"]["current_values"] or {})
        cls = ASSUMPTION
        note = "CURRENT_CONSTRAINT_ONLY applied as frozen assumption"
        if asset == "BYBIT:GRAMUSDT":
            cv["tick_size"] = 0.0001
            cls, note = DERIVED, "tick reconstructed from Bybit notice effective 2026-08-11 (in-window tick 0.0001); lot/min current-only assumption"
        constraints["SHORT|" + asset] = {"instrument": s["instrument"], "venue": s["venue"], "values": {k: cv.get(k) for k in ("tick_size", "lot_step", "min_qty", "min_notional")}, "class": cls, "note": note}
    for asset, L in longs.items():
        constraints["LONG|" + asset] = {"instrument": L["instrument"], "venue": L["venue"], "values": {k: (L["constraints"] or {}).get(k) for k in ("tick_size", "lot_step", "min_qty", "min_notional")}, "class": ASSUMPTION, "note": "current spot rules applied as frozen assumption"}
    # slippage per fill
    slippage = {"assumption_bps_per_side": SLIPPAGE_ASSUMPTION_BPS, "assumption_class": ASSUMPTION,
                "assumption_basis": "ceil(max observed Kraken Futures median spread over the four fill hours (44.43 bps) / 2)",
                "kraken_observed": {k: {"half_spread_bps_at_00_00": (v["derived"]["bbo_at_00_00"]["spread_bps"] or 0) / 2.0, "class": DERIVED} for k, v in stage4a["kraken_analytics"].items()}}
    # capacity per fill (shorts) from Stage Four step 6
    capacity = {}
    for x in stage4["step6_per_fill"]:
        key = "%s|%s" % (x["instrument"], x["fill_date"])
        if x["venue"] == "BINANCE" and x["depth"]:
            capacity[key] = {"bid_notional_0_2pct": x["depth"]["bid_notional_within_0_2pct"], "ask_notional_0_2pct": x["depth"]["ask_notional_within_0_2pct"], "class": OBSERVED, "rule": "short entry hits bids; short exit hits asks"}
        elif x["venue"] == "KRAKEN_FUTURES":
            ka = stage4a["kraken_analytics"].get(key, {}).get("derived")
            if ka:
                px = ka["bbo_at_00_00"]
                capacity[key] = {"bid_notional_0_05pct": (ka["liquidity_at_00_00"]["bid"].get("liquidity_005") or 0) * (px["bid"] or 0),
                                 "ask_notional_0_05pct": (ka["liquidity_at_00_00"]["ask"].get("liquidity_005") or 0) * (px["ask"] or 0), "class": DERIVED,
                                 "rule": "official analytics liquidity_005 (contracts) x best price"}
        else:
            t = x["trades"] or {}
            capacity[key] = {"traded_quote_notional_30min": t.get("quote_notional"), "class": DERIVED, "rule": "30-minute traded quote notional after the fill timestamp (trade-only venue)"}
    # borrow rule for LEO
    perp_rates = [abs(r_["rate"]) for f in funding.values() for r_ in f["records"] if r_["rate"] is not None and f["venue"] != "KRAKEN_FUTURES"]
    max8h = max(perp_rates) if perp_rates else 0.0
    borrow = {"instrument": "fLEO", "observed_frr_daily_max": borrow_obs.get("frr_max_daily"), "assumption_daily_rate": max8h * 3.0,
              "rule": "daily borrow rate = max(observed FRR, assumption = max |8h perp funding rate| observed across the cohort in the window x 3)",
              "applied_daily_rate": max(borrow_obs.get("frr_max_daily") or 0.0, max8h * 3.0), "class": ASSUMPTION if (borrow_obs.get("frr_max_daily") or 0.0) < max8h * 3.0 else OBSERVED,
              "funding_provider_fee_note": "Bitfinex 15% fee applies to providers, not borrowers; not charged"}
    prereg = {
        "artifact": "c22_decisive_replay_preregistration", "version": STAGE_VERSION, "run_id": run_id, "decision_date": DECISION_DATE,
        "authorization": {"operator_instruction": OPERATOR_INSTRUCTION, "recorded_by": "session, present-day operator authorization; no historical token fabricated", "performance_inspected_before_freeze": False},
        "inputs": {"stage4a_report_sha256": STAGE4A_SHA256, "stage4_report_sha256": S4A.STAGE4_REPORT_SHA256, "stage3_report_sha256": S4.STAGE3_REPORT_SHA256,
                   "dry_run_sha256": S3.DRY_RUN_SHA256, "v2_artifact_sha256": DR.V2_FROZEN_SHA256},
        "decisions": {
            "venue_policy": "HOME_VENUE_ONLY", "session_profile_decisive": DECISIVE_PROFILE, "session_profile_sensitivity": SENSITIVITY_PROFILE,
            "session_rule_basis": "frozen B1 forward-exit contract (weekday sessions); calendar profile reported as labelled sensitivity",
            "basis_alignment": {"rule": "execution at venue OHLC open of the fill date; signal/exit rules evaluated on Signum export candles (CMC reference); no basis adjustment applied; CMC-vs-venue open difference reported per fill as a diagnostic", "class": DERIVED},
            "fill_price_source": "venue daily OHLC open (Stage Three canonical for shorts; Stage 5 spot fetch for longs); fail closed if absent",
            "nav_usd": {"value": NAV_USD, "class": ASSUMPTION, "basis": "research-scale account; sensitivity at %s" % NAV_SENSITIVITY_USD},
            "sizing_pct_nav": "frozen 8/2/3/5 (unchanged)", "leverage": 1.0, "exposure_cap_pct": 100.0,
            "short_instrument_selection": {"rule": "home-venue linear perpetual/futures where Stage Two passed; Bitfinex spot-margin borrow for LEO", "class": OBSERVED},
            "long_instrument_selection": {"rule": "home-venue spot pair; execution existence from official spot candles on the fill date", "class": OBSERVED},
            "morpho": "EXCLUDED_VENUE_POLICY (2 shorts); long MORPHO signal executes on COINBASE_EXCHANGE spot (home venue)", "tel": "ELIMINATED_STAGE_ONE_PRESERVED",
            "kas_20260706": "sealed Stage Four FAIL preserved for the trades-based rule; decisive run applies the frozen capacity rule against official orderbook liquidity (Stage 4A) and records the outcome; zero trades in the hour is kept as a flag",
        },
        "cost_base_case": {"fees": fees, "slippage": slippage, "capacity": capacity, "constraints": constraints,
                           "funding": {k: {kk: vv for kk, vv in v.items() if kk != "records"} for k, v in funding.items()}, "borrow_leo": borrow,
                           "result_levels": list(C.RESULT_LEVELS), "components": list(C.COST_COMPONENTS),
                           "37bps_status": C.SENSITIVITY_37BPS_STATUS},
        "benchmarks": {"btc_buy_and_hold": "BINANCE:BTCUSDT export candle chain (CMC reference), same sessions, one taker fee each side",
                       "zero_return_flat": "always flat", "matched_random_entry_null": {"seed": RANDOM_MASTER_SEED, "resamples": RANDOM_RESAMPLES,
                       "matching": "same decision dates, sides, hold lengths (sessions) as executed strategy trades; random symbol from the same export top-50; export-candle prices; same fee class per venue (global max where venue unobserved)"},
                       "signal_off_control": "zero trades", "comparison_basis": "strategy is also run on export-candle prices (basis sensitivity) so null vs strategy is like-for-like; decisive strategy metrics use venue prices"},
        "rejection_gates": {"integrity": ["duplicate_trade", "lookahead", "cost_arithmetic_mismatch", "missing_or_interpolated_bar"],
                            "data": ["open_positions_at_boundary -> INCOMPLETE_FOLLOWUP (decisive conclusion withheld)", "missing venue price -> fail closed", "capacity violation -> deterministic rejection"],
                            "economic": ["net_return<=0", "net_sharpe<=0", "not_better_than_matched_random_null (risk-adjusted)", "not_better_than_btc_buy_and_hold (risk-adjusted)"],
                            "power_warning": "88 actionable entries over 26 daily windows; annualised figures NON-CONCLUSIVE"},
        "long_side_evidence": {a: {k: v for k, v in L.items() if k != "rows"} for a, L in longs.items()},
        "assumption_register": [
            {"field": "taker fee (Binance perps, Binance/Coinbase spot)", "class": ASSUMPTION, "rule": fees["_rule"]},
            {"field": "slippage per side (non-Kraken fills)", "class": ASSUMPTION, "value_bps": SLIPPAGE_ASSUMPTION_BPS},
            {"field": "tick/lot/min rules", "class": ASSUMPTION, "rule": "current values (GRAM tick reconstructed)"},
            {"field": "LEO daily borrow rate", "class": borrow["class"], "value": borrow["applied_daily_rate"]},
            {"field": "starting NAV", "class": ASSUMPTION, "value": NAV_USD},
            {"field": "long capacity", "class": DERIVED, "rule": "%.0f%% of venue daily quote volume on the fill date" % (LONG_CAPACITY_FRACTION_OF_DAILY_VOLUME * 100)},
        ],
        "performance_computed": False, "assumption_selected_against_pnl": False,
    }
    prereg["prereg_sha256"] = S1._sha(S1._canon(prereg))
    return prereg


def write_governance_records(prereg: dict, run_id: str) -> dict:
    APPROVALS_DIR.mkdir(parents=True, exist_ok=True)
    GOVERNANCE_DIR.mkdir(parents=True, exist_ok=True)
    tokens = {
        "HUMAN_DECISION_C22_REPLAY_SPEC_ACCEPT_OR_REVISE=ACCEPT": "Phase A REV1 accepted as the frozen rule set for the decisive replay",
        "HUMAN_DECISION_C22_FORWARD_EXIT_DATA_CONTRACT_ACCEPT_OR_REVISE=ACCEPT": "B1 forward-exit contract accepted; coverage COMPLETE through extension #2",
        "HUMAN_DECISION_C22_EXECUTION_DATA_CONTRACT_ACCEPT_OR_REVISE=ACCEPT": "B1 execution-data contract accepted",
        "HUMAN_DECISION_C22_DRY_RUN_ACCEPT_OR_REJECT=ACCEPT": "no-P&L dry run (sha %s) accepted" % S3.DRY_RUN_SHA256[:16],
        "HUMAN_DECISION_C22_SHORT_INSTRUMENT_EVIDENCE_REQUEST_ACCEPT_OR_REVISE=ACCEPT": "B2 accepted",
        "HUMAN_DECISION_C22_HISTORICAL_EVIDENCE_ACQUISITION_PLAN_ACCEPT_OR_REVISE=ACCEPT": "B3 accepted; stages 1-4 and 4A executed under it",
        "HUMAN_DECISION_C22_INSTRUMENT_REGISTRY_FETCH_AUTHORIZE": "exercised (Stage One)", "HUMAN_DECISION_C22_FUNDING_AND_BORROW_FETCH_AUTHORIZE": "exercised (Stage Two, Stage 5)",
        "HUMAN_DECISION_C22_EXECUTION_OHLC_FETCH_AUTHORIZE": "exercised (Stage Three, Stage 5 long side)", "HUMAN_DECISION_C22_FEES_AND_LIQUIDITY_FETCH_AUTHORIZE": "exercised (Stage Four, 4A)",
        "HUMAN_DECISION_C22_HISTORICAL_INSTRUMENT_EVIDENCE_ADMIT_OR_REJECT=ADMIT": "historical existence/shortability/OHLC/liquidity evidence admitted at the graded tiers recorded in Stages 1-4A",
        "HUMAN_DECISION_C22_SHORT_INSTRUMENT_SELECT": "home-venue perpetual/futures per asset; Bitfinex spot-margin for LEO",
        "HUMAN_DECISION_C22_EXECUTION_COST_BASE_CASE_ACCEPT_OR_REVISE=ACCEPT": "component-level base case frozen in the pre-registration (sha %s); assumptions labelled; 37 bps remains sensitivity-only" % prereg["prereg_sha256"][:16],
        "HUMAN_DECISION_C22_WEEKEND_SESSION_RULE": "decisive = V2_CONTRACT_EXACT; CRYPTO_CALENDAR_SENSITIVITY reported as sensitivity",
        "HUMAN_DECISION_C22_BASIS_ALIGNMENT_REVIEWED": "no adjustment; venue execution prices; CMC-vs-venue diagnostic reported",
        "HUMAN_DECISION_C22_HOLD_PENDING_SHORT_INSTRUMENT_EVIDENCE": "recorded as the interim closure decision (supersedes the 2026-09-09 REJECT recommendation), now resolved by evidence stages",
        "HUMAN_DECISION_C22_ADVANCE_TO_REPLAY_OR_REJECT=ADVANCE": "one decisive fee-honest replay authorized under this pre-registration",
    }
    rec = {"artifact": "c22_governance_approvals", "run_id": run_id, "decision_date": DECISION_DATE,
           "basis": "present-day operator instruction '%s' (2026-09-11), recorded by the session; not a historical token; reversible by the operator" % OPERATOR_INSTRUCTION,
           "performance_inspected_before_these_decisions": False, "preregistration_sha256": prereg["prereg_sha256"], "tokens": tokens}
    p = APPROVALS_DIR / ("c22_governance_approvals_%s.json" % run_id)
    if p.exists():
        raise Stage5Error("refuse_overwrite:%s" % p.name)
    p.write_bytes(json.dumps(rec, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    pp = GOVERNANCE_DIR / ("c22_decisive_replay_preregistration_%s.json" % run_id)
    pp.write_bytes(json.dumps(prereg, indent=2, sort_keys=True, default=str).encode("utf-8") + b"\n")
    pp.with_suffix(".json.sha256").write_text(S1._sha(pp.read_bytes()) + "\n", encoding="utf-8")
    return {"approvals": S1._rel(p), "preregistration": S1._rel(pp), "preregistration_file_sha256": S1._sha(pp.read_bytes())}


def write_evidence_manifests(prereg: dict, stage4a: dict, funding: dict, longs: dict, run_id: str) -> list:
    """Per-instrument manifests in the frozen B3 layout; fields backed by historical evidence carry
    the graded tier; fields covered by the frozen cost base case carry evidence_basis
    FROZEN_COST_BASE_CASE (never 'historical'); present-day-only is never claimed."""
    S1.MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    T1 = "T1_OFFICIAL_VENUE_HISTORICAL_FILES_OR_OFFICIAL_API_DOCS"
    for asset, inst in stage4a["instruments"].items():
        venue, base = asset.split(":")
        base = base[:-4] if base.endswith("USDT") else base[:-3]
        fee_cls = prereg["cost_base_case"]["fees"].get(inst["venue"], {})
        m = {"c22_asset": asset, "venue": inst["venue"], "instrument": inst["instrument"], "run_id": run_id, "stage": STAGE,
             "canonical_asset_identity": {"source_tier": T1, "sha256": "stage1", "evidence_basis": "HISTORICAL_RECORD", "ref": "Stage One registry"},
             "historical_execution_instrument": {"source_tier": T1, "sha256": "stage1", "evidence_basis": "HISTORICAL_RECORD"},
             "venue": {"source_tier": T1, "sha256": "stage1", "evidence_basis": "HISTORICAL_RECORD"},
             "instrument_existence_on_required_dates": {"source_tier": T1, "sha256": "stage1", "evidence_basis": "HISTORICAL_RECORD"},
             "historical_shortability_mechanism": {"source_tier": T1, "sha256": "stage2", "evidence_basis": "HISTORICAL_RECORD"},
             "historical_ohlc_coverage": {"source_tier": T1, "sha256": "stage3", "evidence_basis": "HISTORICAL_RECORD"},
             "fee_schedule": {"source_tier": (T1 if inst["fee"]["grade"].startswith("T2") else None), "sha256": "stage4a", "evidence_basis": ("HISTORICAL_RECORD" if inst["fee"]["grade"].startswith("T2") else "FROZEN_COST_BASE_CASE"), "stage4a_grade": inst["fee"]["grade"], "applied_taker_bps": fee_cls.get("taker_bps"), "class": fee_cls.get("class")},
             "funding_or_borrow_requirement": {"source_tier": T1, "sha256": "stage5", "evidence_basis": "HISTORICAL_RECORD", "records": funding.get(asset, {}).get("count")},
             "minimum_quantity_or_notional": {"source_tier": None, "sha256": "stage4", "evidence_basis": "FROZEN_COST_BASE_CASE", "stage4a_grade": inst["constraints"]["lot_min"]["grade"]},
             "tick_lot_constraints": {"source_tier": (T1 if inst["constraints"]["tick"]["grade"].startswith("T2") else None), "sha256": "stage4a", "evidence_basis": ("HISTORICAL_RECORD" if inst["constraints"]["tick"]["grade"].startswith("T2") else "FROZEN_COST_BASE_CASE"), "stage4a_grade": inst["constraints"]["tick"]["grade"]},
             "liquidity_spread_evidence": {"source_tier": T1, "sha256": "stage4", "evidence_basis": "HISTORICAL_RECORD", "note": "observed depth/trades/orderbook per fill; spread assumption where BBO absent (cost base case)"},
             "admission_token": "HUMAN_DECISION_C22_HISTORICAL_INSTRUMENT_EVIDENCE_ADMIT_OR_REJECT=ADMIT", "cost_base_case_token": "HUMAN_DECISION_C22_EXECUTION_COST_BASE_CASE_ACCEPT_OR_REVISE=ACCEPT"}
        p = S1.MANIFEST_DIR / ("%s__%s__evidence_manifest.json" % (venue, base))
        if p.exists():
            raise Stage5Error("refuse_overwrite:%s" % p.name)
        p.write_bytes(S1._canon(m))
        written.append(S1._rel(p))
    for asset, L in longs.items():
        venue, base = asset.split(":")
        base = base[:-4] if base.endswith("USDT") else base[:-3]
        fee_cls = prereg["cost_base_case"]["fees"].get(L["venue"], {})
        m = {"c22_asset": asset, "venue": L["venue"], "instrument": L["instrument"], "run_id": run_id, "stage": STAGE, "side": "LONG",
             "canonical_asset_identity": {"source_tier": T1, "sha256": "stage5", "evidence_basis": "HISTORICAL_RECORD"},
             "historical_execution_instrument": {"source_tier": T1, "sha256": "stage5", "evidence_basis": "HISTORICAL_RECORD"},
             "venue": {"source_tier": T1, "sha256": "stage5", "evidence_basis": "HISTORICAL_RECORD"},
             "instrument_existence_on_required_dates": {"source_tier": T1, "sha256": "stage5", "evidence_basis": "HISTORICAL_RECORD", "first_candle": L["first_date"]},
             "historical_ohlc_coverage": {"source_tier": T1, "sha256": "stage5", "evidence_basis": "HISTORICAL_RECORD", "coverage": L["coverage"]},
             "fee_schedule": {"source_tier": None, "sha256": "stage5", "evidence_basis": "FROZEN_COST_BASE_CASE", "applied_taker_bps": fee_cls.get("taker_bps"), "class": fee_cls.get("class")},
             "minimum_quantity_or_notional": {"source_tier": None, "sha256": "stage5", "evidence_basis": "FROZEN_COST_BASE_CASE"},
             "tick_lot_constraints": {"source_tier": None, "sha256": "stage5", "evidence_basis": "FROZEN_COST_BASE_CASE"},
             "liquidity_spread_evidence": {"source_tier": None, "sha256": "stage5", "evidence_basis": "FROZEN_COST_BASE_CASE", "note": "daily volume capacity rule; spread assumption"},
             "admission_token": "HUMAN_DECISION_C22_HISTORICAL_INSTRUMENT_EVIDENCE_ADMIT_OR_REJECT=ADMIT", "cost_base_case_token": "HUMAN_DECISION_C22_EXECUTION_COST_BASE_CASE_ACCEPT_OR_REVISE=ACCEPT"}
        p = S1.MANIFEST_DIR / ("%s__%s__evidence_manifest.json" % (venue, base))
        if p.exists():                       # dual-side asset: the short manifest holds the plain name
            p = S1.MANIFEST_DIR / ("%s__%s__LONG__evidence_manifest.json" % (venue, base))
        if p.exists():
            raise Stage5Error("refuse_overwrite:%s" % p.name)
        p.write_bytes(S1._canon(m))
        written.append(S1._rel(p))
    return written


def run_stage5(get: Callable = http_get, run_id: str | None = None, sleep_s: float = 0.2) -> dict:
    run_id = run_id or _dt.now(_tz.utc).strftime("%Y%m%dT%H%M%SZ")
    raw4a = STAGE4A_REPORT.read_bytes()
    if S1._sha(raw4a) != STAGE4A_SHA256:
        raise Stage5Error("stage4a_report_sha_mismatch")
    stage4a = json.loads(raw4a.decode("utf-8"))
    stage4 = S4A.load_stage4_of_record()
    cache: dict = {}
    longs = {}
    for asset, (venue, inst) in LONG_INSTRUMENTS.items():
        longs[asset] = fetch_long_spot(asset, venue, inst, get, run_id, cache)
        if sleep_s:
            time.sleep(sleep_s)
    funding = {}
    for asset, s in stage4["step5_per_instrument"].items():
        if s["venue"] == "BITFINEX":
            continue
        base = asset.split(":")[1]
        base = base[:-4] if base.endswith("USDT") else base[:-3]
        funding[asset] = fetch_funding_full(s["venue"], s["instrument"], base, get, run_id, cache)
        if sleep_s:
            time.sleep(sleep_s)
    borrow_obs = fetch_bitfinex_borrow_obs(get, run_id)
    prereg = build_prereg(stage4a, stage4, longs, funding, borrow_obs, run_id)
    gov = write_governance_records(prereg, run_id)
    manifests = write_evidence_manifests(prereg, stage4a, funding, longs, run_id)
    # canonical data files for the replay runner (venue OHLC for longs; funding records)
    data_dir = S1.EVIDENCE_ROOT / "decisive_inputs"
    data_dir.mkdir(parents=True, exist_ok=True)
    inputs = {"run_id": run_id, "long_ohlc": {a: L["rows"] for a, L in longs.items()}, "funding": {a: f["records"] for a, f in funding.items()},
              "borrow_leo": borrow_obs, "prereg_sha256": prereg["prereg_sha256"]}
    ip = data_dir / ("c22_decisive_inputs_%s.json" % run_id)
    ip.write_bytes(S1._canon(inputs))
    ip.with_suffix(".json.sha256").write_text(S1._sha(ip.read_bytes()) + "\n", encoding="utf-8")
    return {"run_id": run_id, "prereg_sha256": prereg["prereg_sha256"], **gov, "manifests_written": len(manifests), "decisive_inputs": S1._rel(ip),
            "decisive_inputs_sha256": S1._sha(ip.read_bytes()),
            "long_side": {a: {"first": L["first_date"], "last": L["last_date"], "coverage_complete": (L["coverage"] or {}).get("complete"), "constraints": L["constraints"]} for a, L in longs.items()},
            "funding_counts": {a: f["count"] for a, f in funding.items()}, "borrow_leo": {k: v for k, v in borrow_obs.items() if k != "raw_sources"},
            "fees": {k: v for k, v in prereg["cost_base_case"]["fees"].items() if not k.startswith("_")}}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", default=None)
    a = ap.parse_args(argv)
    print(json.dumps(run_stage5(run_id=a.run_id), indent=2, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
