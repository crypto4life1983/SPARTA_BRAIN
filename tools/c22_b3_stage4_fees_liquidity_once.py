"""Candidate #22 -- B3 STAGE FOUR: FEE / TICK / LOT / MINIMUM RULES + LIQUIDITY / SPREAD EVIDENCE
(frozen B3 steps 5 and 6, authorization batch C22_FEES_AND_LIQUIDITY_FETCH_READY_FOR_HUMAN_AUTHORIZATION,
token name HUMAN_DECISION_C22_FEES_AND_LIQUIDITY_FETCH_AUTHORIZE). READ-ONLY; RESEARCH ONLY.

Evidence constraints (operator, 2026-09-11, additive to the frozen specification):
  * CURRENT FEES ARE NOT HISTORICAL FEES: fee values are classed HISTORICAL_FEE_PROVEN /
    HISTORICAL_FEE_UNRESOLVED / CURRENT_FEE_ONLY; nothing is manufactured.
  * Tick / lot / minimum rules: HISTORICAL_CONSTRAINT_PROVEN / CURRENT_CONSTRAINT_ONLY /
    HISTORICAL_CONSTRAINT_UNRESOLVED; current metadata is never back-projected.
  * Liquidity / spread: daily OHLC+volume is NOT sufficient. First-party historical trades,
    depth or book data at the frozen fill timestamps (00:00 UTC of the fill date) are collected
    where the venue publishes them; limitations are preserved; trades are never mislabelled as
    order-book spread; zero spread / infinite liquidity / full fill at open are never inferred.
  * Every value carries a class: OBSERVED_FIRST_PARTY / DERIVED_FROM_OBSERVED_DATA /
    FROZEN_CONSERVATIVE_ASSUMPTION / SENSITIVITY_ONLY / UNRESOLVED. No assumption is selected here.
  * Fail closed: an instrument/signal passes Stage Four only when every decisive element the
    frozen plan requires is historically proven; missing evidence is reported, not weakened.
No performance, no cost arithmetic, no admission change, no later stage.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import io
import json
import os
import sys
import time
import urllib.error
import urllib.request
import zipfile
from datetime import date as _date, datetime as _dt, timedelta as _td, timezone as _tz
from pathlib import Path
from typing import Callable

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import sparta_commander.c22_historical_evidence_acquisition_plan_contract as B3  # noqa: E402
import tools.c22_b3_stage1_instrument_existence_once as S1  # noqa: E402
import tools.c22_b3_stage2_historical_shortability_once as S2  # noqa: E402
import tools.c22_b3_stage3_historical_ohlc_once as S3  # noqa: E402

STAGE = "B3_STAGE_FOUR_FEES_TICK_LOT_MIN_LIQUIDITY_SPREAD"
STAGE_VERSION = "c22_b3_stage4_v1"
FROZEN_STEPS = (B3.ACQUISITION_ORDER[4], B3.ACQUISITION_ORDER[5])          # 5_fee_tick_lot_minimum_rules, 6_liquidity_and_spread_evidence
FROZEN_BATCH = "C22_FEES_AND_LIQUIDITY_FETCH_READY_FOR_HUMAN_AUTHORIZATION"
FROZEN_TOKEN = "HUMAN_DECISION_C22_FEES_AND_LIQUIDITY_FETCH_AUTHORIZE"
STAGE3_RUN_OF_RECORD = "20260911T130800Z"
STAGE3_REPORT = REPO_ROOT / "reports" / "c22_gc_b3_stage3" / ("c22_b3_stage3_historical_ohlc_%s.json" % STAGE3_RUN_OF_RECORD)
STAGE3_REPORT_SHA256 = "889be73018ee4d20a0031daf4797951b3bafa8245a59b4a805bc7eb59e48e763"
REPORT_DIR = REPO_ROOT / "reports" / "c22_gc_b3_stage4"
FEES_DIR = S1.EVIDENCE_ROOT / "fees"
LIQ_DIR = S1.EVIDENCE_ROOT / "liquidity"
_USER_AGENT = "sparta-brain-c22-b3-stage4-readonly/1.0"
FILL_WINDOW_MINUTES = 30                    # execution window after the frozen fill timestamp (00:00 UTC)
MAX_DOWNLOAD_BYTES = 40_000_000

ALLOWED_URL_PREFIXES = (
    "https://fapi.binance.com/fapi/v1/exchangeInfo",
    "https://data.binance.vision/data/futures/um/daily/bookDepth/",
    "https://data.binance.vision/data/futures/um/daily/metrics/",
    "https://api.bybit.com/v5/market/instruments-info",
    "https://public.bybit.com/trading/",
    "https://www.okx.com/api/v5/public/instruments",
    "https://www.okx.com/api/v5/market/history-trades",
    "https://api.gateio.ws/api/v4/futures/usdt/contracts/",
    "https://api.gateio.ws/api/v4/futures/usdt/trades",
    "https://futures.kraken.com/derivatives/api/v3/instruments",
    "https://futures.kraken.com/derivatives/api/v3/feeschedules",
    "https://futures.kraken.com/api/history/v3/market/",
    "https://api-pub.bitfinex.com/v2/conf/pub:info:pair",
    "https://api-pub.bitfinex.com/v2/trades/",
)

# evidence classes
OBSERVED = "OBSERVED_FIRST_PARTY"
DERIVED = "DERIVED_FROM_OBSERVED_DATA"
ASSUMPTION = "FROZEN_CONSERVATIVE_ASSUMPTION"
SENSITIVITY = "SENSITIVITY_ONLY"
UNRESOLVED = "UNRESOLVED"
# fee statuses
FEE_HIST_PROVEN, FEE_HIST_UNRESOLVED, FEE_CURRENT_ONLY = "HISTORICAL_FEE_PROVEN", "HISTORICAL_FEE_UNRESOLVED", "CURRENT_FEE_ONLY"
FEE_CURRENT_UNAVAILABLE = "CURRENT_FEE_NOT_EXPOSED_BY_PUBLIC_API"
# constraint statuses
CON_HIST_PROVEN, CON_CURRENT_ONLY, CON_HIST_UNRESOLVED = "HISTORICAL_CONSTRAINT_PROVEN", "CURRENT_CONSTRAINT_ONLY", "HISTORICAL_CONSTRAINT_UNRESOLVED"
# per-fill liquidity / spread statuses
LIQ_OBSERVED = "LIQUIDITY_OBSERVED_FIRST_PARTY"
LIQ_NONE_IN_WINDOW = "FAIL_NO_MARKET_ACTIVITY_IN_FILL_WINDOW"
LIQ_UNRESOLVED = "UNRESOLVED_LIQUIDITY_SOURCE"
SPREAD_DEPTH_PROXY = "DEPTH_AT_PERCENT_LEVELS_OBSERVED_NOT_BBO_SPREAD"
SPREAD_UNRESOLVED = "UNRESOLVED_NO_FIRST_PARTY_HISTORICAL_BOOK"
# per-signal composite verdicts (frozen plan requires steps 5 AND 6 proven)
PASS = "PASS_STAGE_FOUR"
UNRES_FEE = "UNRESOLVED_HISTORICAL_FEE"
UNRES_CON = "UNRESOLVED_HISTORICAL_CONSTRAINT"
UNRES_LIQ = "UNRESOLVED_LIQUIDITY_EVIDENCE"
UNRES_SPREAD = "UNRESOLVED_SPREAD_EVIDENCE"
FAIL_LIQ = "FAIL_NO_MARKET_ACTIVITY_AT_FILL"
NOT_ELIGIBLE = "NOT_ELIGIBLE_PRIOR_STAGE"
VERDICTS = (PASS, UNRES_FEE, UNRES_CON, UNRES_LIQ, UNRES_SPREAD, FAIL_LIQ, NOT_ELIGIBLE)


class Stage4Error(RuntimeError):
    pass


def _assert_safe_url(url: str) -> None:
    if not isinstance(url, str) or not url.startswith("https://") or not any(url.startswith(p) for p in ALLOWED_URL_PREFIXES):
        raise Stage4Error("refusing non-allowlisted url: %s" % url)
    low = url.lower()
    for frag in S1.FORBIDDEN_URL_FRAGMENTS:
        if frag in low and not (frag == "trade/" and ("/history/v3/market/" in low or "/trades/" in low)) and not (frag == "trade/" and "public.bybit.com/trading/" in low):
            raise Stage4Error("refusing url containing forbidden fragment %r" % frag)


def http_get(url: str, timeout: float = 60.0) -> dict:
    _assert_safe_url(url)
    req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT}, method="GET")
    retrieved = _dt.now(_tz.utc).isoformat(timespec="seconds")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = r.read(MAX_DOWNLOAD_BYTES + 1)
            if len(data) > MAX_DOWNLOAD_BYTES:
                return {"url": url, "status": 413, "retrieved_utc": retrieved, "raw_bytes": b'{"sparta_note":"download exceeded MAX_DOWNLOAD_BYTES; not preserved"}'}
            return {"url": url, "status": r.status, "retrieved_utc": retrieved, "raw_bytes": data}
    except urllib.error.HTTPError as e:
        return {"url": url, "status": e.code, "retrieved_utc": retrieved, "raw_bytes": e.read()[:4000]}


def _parse(resp):
    try:
        return json.loads(resp["raw_bytes"].decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return None


def _f(x):
    return S2._f(x)


def load_stage3_of_record() -> dict:
    raw = STAGE3_REPORT.read_bytes()
    if S1._sha(raw) != STAGE3_REPORT_SHA256:
        raise Stage4Error("stage3_report_sha_mismatch")
    return json.loads(raw.decode("utf-8"))


# --------------------------------------------------------------------------------------------
# required fills from the sealed dry run (entry and exit fills that actually executed in the lifecycle)
# --------------------------------------------------------------------------------------------
def required_fills(dry_run: dict, eligible_signal_ids: set) -> dict:
    """{signal_id: {"fills": [{"kind","date","profile"}]}} for eligible short signals."""
    out: dict = {}
    for prof, pr in dry_run["profiles"].items():
        for rec in pr["records"]:
            if rec["signal_id"] not in eligible_signal_ids:
                continue
            w = out.setdefault(rec["signal_id"], {"symbol": rec["symbol"], "fills": []})
            if rec["entry_date"]:
                w["fills"].append({"kind": "ENTRY", "date": rec["entry_date"], "profile": prof})
            if rec["exit_date"]:
                w["fills"].append({"kind": "EXIT", "date": rec["exit_date"], "profile": prof, "reason": rec["exit_reason"]})
            if not rec["entry_date"]:
                w["fills"].append({"kind": "NO_EXECUTION", "date": None, "profile": prof, "status": rec["lifecycle_status"], "reason": rec.get("reject_reason")})
    return out


# --------------------------------------------------------------------------------------------
# step 5: fees + constraints (current metadata; historical status fail-closed)
# --------------------------------------------------------------------------------------------
def fetch_fee_and_constraints(venue: str, inst: str, base: str, get: Callable, run_id: str, cache: dict, window: tuple) -> dict:
    lo, hi = window
    rec = {"venue": venue, "instrument": inst,
           "fee": {"class": UNRESOLVED, "historical_status": FEE_HIST_UNRESOLVED, "current_status": FEE_CURRENT_UNAVAILABLE, "current_values": None, "source": None,
                   "note": "no first-party dated historical fee schedule exposed; current values, where public, are CURRENT_FEE_ONLY"},
           "constraints": {"class": UNRESOLVED, "historical_status": CON_HIST_UNRESOLVED, "current_status": CON_CURRENT_ONLY, "current_values": None, "change_timestamp": None, "source": None},
           "metas": []}
    if venue == "BINANCE":
        if "binance_exchangeinfo" not in cache:
            r = get("https://fapi.binance.com/fapi/v1/exchangeInfo")
            cache["binance_exchangeinfo"] = (r, S1.preserve_raw("BINANCE", "_shared", "stage4_usdm_exchangeinfo", r, {}, run_id), _parse(r))
        r, m, j = cache["binance_exchangeinfo"]
        rec["metas"].append(m)
        row = next((s for s in ((j or {}).get("symbols") or []) if s.get("symbol") == inst), None)
        if row:
            f = {x["filterType"]: x for x in row.get("filters", [])}
            rec["constraints"].update(class_=None, current_values={"tick_size": _f(f.get("PRICE_FILTER", {}).get("tickSize")), "lot_step": _f(f.get("LOT_SIZE", {}).get("stepSize")),
                                                                    "min_qty": _f(f.get("LOT_SIZE", {}).get("minQty")), "min_notional": _f(f.get("MIN_NOTIONAL", {}).get("notional"))},
                                      source=m["raw_sha256"], note="fapi exchangeInfo filters carry no effective-date; current only")
            rec["constraints"]["class"] = OBSERVED
        rec["fee"]["note"] = "Binance USD-M commission rates require an authenticated endpoint; official fee page is not an API record; no historical schedule"
    elif venue == "BYBIT":
        r = get("https://api.bybit.com/v5/market/instruments-info?category=linear&symbol=%s" % inst)
        m = S1.preserve_raw("BYBIT", base, "stage4_linear_instruments_info", r, {"category": "linear", "symbol": inst}, run_id)
        rec["metas"].append(m)
        row = (((_parse(r) or {}).get("result") or {}).get("list") or [None])[0]
        if row:
            rec["constraints"].update(current_values={"tick_size": _f(row.get("priceFilter", {}).get("tickSize")), "lot_step": _f(row.get("lotSizeFilter", {}).get("qtyStep")),
                                                      "min_qty": _f(row.get("lotSizeFilter", {}).get("minOrderQty")), "min_notional": _f(row.get("lotSizeFilter", {}).get("minNotionalValue"))},
                                      source=m["raw_sha256"], note="instruments-info carries launchTime but no filter change history; current only")
            rec["constraints"]["class"] = OBSERVED
        rec["fee"]["note"] = "Bybit fee-rate endpoint is authenticated; no public historical schedule"
    elif venue == "OKX":
        r = get("https://www.okx.com/api/v5/public/instruments?instType=SWAP&instId=%s" % inst)
        m = S1.preserve_raw("OKX", base, "stage4_public_instruments_swap", r, {"instType": "SWAP", "instId": inst}, run_id)
        rec["metas"].append(m)
        row = ((_parse(r) or {}).get("data") or [None])[0]
        if row:
            rec["constraints"].update(current_values={"tick_size": _f(row.get("tickSz")), "lot_step": _f(row.get("lotSz")), "min_qty": _f(row.get("minSz")),
                                                      "contract_value": _f(row.get("ctVal")), "min_notional": None},
                                      source=m["raw_sha256"], note="public instruments carries listTime only; no filter change history; current only")
            rec["constraints"]["class"] = OBSERVED
        rec["fee"]["note"] = "OKX trade-fee endpoint is authenticated; no public historical schedule"
    elif venue == "GATE":
        r = get("https://api.gateio.ws/api/v4/futures/usdt/contracts/%s" % inst)
        m = S1.preserve_raw("GATE", base, "stage4_futures_usdt_contract", r, {"contract": inst}, run_id)
        rec["metas"].append(m)
        j = _parse(r) or {}
        if j.get("name") == inst:
            cct = S1._s_to_date(j.get("config_change_time"))
            rec["constraints"].update(current_values={"tick_size": _f(j.get("order_price_round")), "lot_step": 1.0, "min_qty": _f(j.get("order_size_min")),
                                                      "contract_multiplier": _f(j.get("quanto_multiplier")), "min_notional": None},
                                      change_timestamp=cct, source=m["raw_sha256"])
            rec["constraints"]["class"] = OBSERVED
            if cct and cct > hi:
                rec["constraints"]["historical_status"] = CON_HIST_UNRESOLVED
                rec["constraints"]["note"] = "official config_change_time %s is AFTER the required window %s..%s: current values demonstrably post-date the window" % (cct, lo, hi)
            elif cct and cct <= lo:
                rec["constraints"]["historical_status"] = CON_HIST_PROVEN
                rec["constraints"]["note"] = "official config_change_time %s precedes the required window and no later change is recorded" % cct
            rec["fee"].update(class_=None, current_status=FEE_CURRENT_ONLY, current_values={"maker": _f(j.get("maker_fee_rate")), "taker": _f(j.get("taker_fee_rate"))}, source=m["raw_sha256"],
                              note="contract endpoint exposes CURRENT maker/taker; config_change_time %s; no dated fee history -> historical unresolved" % cct)
            rec["fee"]["class"] = OBSERVED
    elif venue == "KRAKEN_FUTURES":
        if "kraken_instruments" not in cache:
            r = get("https://futures.kraken.com/derivatives/api/v3/instruments")
            cache["kraken_instruments"] = (r, S1.preserve_raw("KRAKEN", "_shared", "stage4_futures_instruments", r, {}, run_id), _parse(r))
        if "kraken_feeschedules" not in cache:
            r2 = get("https://futures.kraken.com/derivatives/api/v3/feeschedules")
            cache["kraken_feeschedules"] = (r2, S1.preserve_raw("KRAKEN", "_shared", "stage4_feeschedules_current", r2, {}, run_id), _parse(r2))
        r, m, j = cache["kraken_instruments"]
        r2, m2, j2 = cache["kraken_feeschedules"]
        rec["metas"] += [m, m2]
        row = next((x for x in ((j or {}).get("instruments") or []) if x.get("symbol") == inst), None)
        if row:
            rec["constraints"].update(current_values={"tick_size": _f(row.get("tickSize")), "lot_step": 10 ** -int(row.get("contractValueTradePrecision", 0)), "min_qty": None,
                                                      "impact_mid_size": _f(row.get("impactMidSize")), "min_notional": None},
                                      source=m["raw_sha256"], note="instruments endpoint has openingDate but no constraint change history; current only")
            rec["constraints"]["class"] = OBSERVED
            sched = next((s for s in ((j2 or {}).get("feeSchedules") or []) if s.get("uid") == row.get("feeScheduleUid")), None)
            if sched:
                t0 = (sched.get("tiers") or [{}])[0]
                rec["fee"].update(current_status=FEE_CURRENT_ONLY, current_values={"schedule": sched.get("name"), "tier0_maker": _f(t0.get("makerFee")), "tier0_taker": _f(t0.get("takerFee"))},
                                  source=m2["raw_sha256"], note="feeschedules is a CURRENT schedule without effective dates -> historical unresolved")
                rec["fee"]["class"] = OBSERVED
    elif venue == "BITFINEX":
        if "bitfinex_pair_info" not in cache:
            r = get("https://api-pub.bitfinex.com/v2/conf/pub:info:pair")
            cache["bitfinex_pair_info"] = (r, S1.preserve_raw("BITFINEX", "_shared", "stage4_conf_pub_info_pair", r, {}, run_id), _parse(r))
        r, m, j = cache["bitfinex_pair_info"]
        rec["metas"].append(m)
        row = next((x for x in ((j or [[]])[0] or []) if x and x[0] == inst[1:]), None)
        if row and isinstance(row[1], list):
            rec["constraints"].update(current_values={"tick_size": None, "lot_step": None, "min_qty": _f(row[1][3]), "max_qty": _f(row[1][4]), "min_notional": None},
                                      source=m["raw_sha256"], note="pub:info:pair carries min/max order size only, no history; current only")
            rec["constraints"]["class"] = OBSERVED
        rec["fee"]["note"] = "Bitfinex trading fee tiers are account-level and not exposed with effective dates; no historical schedule"
    for k in ("fee", "constraints"):
        rec[k].pop("class_", None)
    return rec


# --------------------------------------------------------------------------------------------
# step 6: liquidity / spread at the frozen fill timestamps
# --------------------------------------------------------------------------------------------
def _window_ms(fill_date: str) -> tuple:
    t0 = S1._ms(fill_date)
    return t0, t0 + FILL_WINDOW_MINUTES * 60_000


def _summarise_trades(trades: list) -> dict:
    """trades: [(ts_ms, price, qty)] within window. DERIVED_FROM_OBSERVED_DATA summary."""
    if not trades:
        return {"trade_count": 0}
    prices = [p for _, p, _ in trades if p is not None]
    qty = [q for _, _, q in trades if q is not None]
    notional = sum(p * q for _, p, q in trades if p is not None and q is not None)
    return {"trade_count": len(trades), "first_trade_utc": _dt.fromtimestamp(min(t for t, _, _ in trades) / 1000, _tz.utc).isoformat(),
            "last_trade_utc": _dt.fromtimestamp(max(t for t, _, _ in trades) / 1000, _tz.utc).isoformat(),
            "price_min": min(prices) if prices else None, "price_max": max(prices) if prices else None,
            "vwap": (notional / sum(qty)) if qty and sum(qty) > 0 else None, "base_volume": sum(qty) if qty else None, "quote_notional": notional,
            "seconds_from_open_to_first_trade": (min(t for t, _, _ in trades) - min(t for t, _, _ in trades) // 86_400_000 * 86_400_000) / 1000.0}


def fetch_fill_liquidity(venue: str, inst: str, base: str, fill_date: str, get: Callable, run_id: str) -> dict:
    lo, hi = _window_ms(fill_date)
    out = {"venue": venue, "instrument": inst, "fill_date": fill_date, "fill_timestamp_utc": fill_date + "T00:00:00Z",
           "window_minutes": FILL_WINDOW_MINUTES, "trades": None, "trades_class": UNRESOLVED, "trades_status": LIQ_UNRESOLVED,
           "depth": None, "depth_class": UNRESOLVED, "spread_status": SPREAD_UNRESOLVED, "metas": [], "limitations": []}
    trades: list = []
    if venue == "BINANCE":
        # official archived depth snapshots (percentage levels) -- first-party liquidity at the timestamp; NOT best-bid/ask spread
        r = get("https://data.binance.vision/data/futures/um/daily/bookDepth/%s/%s-bookDepth-%s.zip" % (inst, inst, fill_date))
        m = S1.preserve_raw("BINANCE", base, "stage4_bookdepth_%s" % fill_date, r, {"symbol": inst, "date": fill_date, "file": "bookDepth daily zip"}, run_id)
        out["metas"].append(m)
        if r["status"] == 200:
            try:
                z = zipfile.ZipFile(io.BytesIO(r["raw_bytes"]))
                rows = list(csv.DictReader(io.StringIO(z.read(z.namelist()[0]).decode("utf-8"))))
                snaps: dict = {}
                for x in rows:
                    ts = x["timestamp"]
                    if ts[:10] == fill_date and ts[11:16] <= "00:05":
                        snaps.setdefault(ts, {})[x["percentage"]] = {"depth": _f(x["depth"]), "notional": _f(x["notional"])}
                if snaps:
                    first = sorted(snaps)[0]
                    out["depth"] = {"snapshot_utc": first, "levels_pct": snaps[first],
                                    "bid_notional_within_0_2pct": (snaps[first].get("-0.20") or {}).get("notional"),
                                    "ask_notional_within_0_2pct": (snaps[first].get("0.20") or {}).get("notional"),
                                    "bid_notional_within_1pct": (snaps[first].get("-1.00") or {}).get("notional"),
                                    "ask_notional_within_1pct": (snaps[first].get("1.00") or {}).get("notional")}
                    out["depth_class"] = OBSERVED
                    out["spread_status"] = SPREAD_DEPTH_PROXY
                    out["trades_status"] = LIQ_OBSERVED if (out["depth"]["bid_notional_within_0_2pct"] or 0) > 0 and (out["depth"]["ask_notional_within_0_2pct"] or 0) > 0 else LIQ_UNRESOLVED
                    out["trades_class"] = DERIVED
                    out["limitations"].append("liquidity evidenced by official depth snapshot (notional resting within ±0.2%/±1% of mid), not by trades; best bid/ask not in this file")
                else:
                    out["limitations"].append("bookDepth file has no snapshot within the first 5 minutes of the fill date")
            except (zipfile.BadZipFile, KeyError, UnicodeDecodeError) as exc:
                out["limitations"].append("bookDepth unparseable:%s" % type(exc).__name__)
        else:
            out["limitations"].append("official bookDepth file not available (HTTP %s)" % r["status"])
        out["limitations"].append("Binance REST aggTrades restricted to the most recent 2 days; archived aggTrades daily files not fetched (size); trades not used")
    elif venue == "BYBIT":
        r = get("https://public.bybit.com/trading/%s/%s%s.csv.gz" % (inst, inst, fill_date))
        m = S1.preserve_raw("BYBIT", base, "stage4_public_trades_%s" % fill_date, r, {"symbol": inst, "date": fill_date, "file": "public trading csv.gz"}, run_id)
        out["metas"].append(m)
        if r["status"] == 200:
            try:
                txt = gzip.decompress(r["raw_bytes"]).decode("utf-8")
                for x in csv.DictReader(io.StringIO(txt)):
                    ts = int(float(x["timestamp"]) * 1000)
                    if lo <= ts < hi:
                        trades.append((ts, _f(x["price"]), _f(x["size"])))
                out["trades_class"] = OBSERVED
            except (OSError, ValueError, KeyError) as exc:
                out["limitations"].append("bybit csv unparseable:%s" % type(exc).__name__)
        else:
            out["limitations"].append("official public trade file not available (HTTP %s)" % r["status"])
        out["limitations"].append("no first-party historical order book published by Bybit; spread unresolved")
    elif venue == "OKX":
        after = hi
        for page in range(6):
            r = get("https://www.okx.com/api/v5/market/history-trades?instId=%s&type=2&after=%d&before=%d&limit=100" % (inst, after, lo - 1))
            m = S1.preserve_raw("OKX", base, "stage4_history_trades_%s_p%02d" % (fill_date, page), r, {"instId": inst, "type": 2, "after_ms": after, "before_ms": lo - 1, "page": page}, run_id)
            out["metas"].append(m)
            data = ((_parse(r) or {}).get("data") or [])
            for x in data:
                ts = int(x["ts"])
                if lo <= ts < hi:
                    trades.append((ts, _f(x["px"]), _f(x["sz"])))
            out["trades_class"] = OBSERVED
            if len(data) < 100:
                break
            after = min(int(x["ts"]) for x in data)
        out["limitations"].append("OKX history-trades (contracts, sz in contracts); no first-party historical order book; spread unresolved")
    elif venue == "GATE":
        r = get("https://api.gateio.ws/api/v4/futures/usdt/trades?contract=%s&from=%d&to=%d&limit=1000" % (inst, lo // 1000, hi // 1000))
        m = S1.preserve_raw("GATE", base, "stage4_futures_trades_%s" % fill_date, r, {"contract": inst, "from_s": lo // 1000, "to_s": hi // 1000, "limit": 1000}, run_id)
        out["metas"].append(m)
        j = _parse(r)
        if isinstance(j, list):
            for x in j:
                ts = int(float(x.get("create_time_ms") or x.get("create_time") or 0) * 1000)   # Gate reports seconds with ms fraction
                if lo <= ts < hi:
                    trades.append((ts, _f(x.get("price")), abs(_f(x.get("size")) or 0)))
            out["trades_class"] = OBSERVED
            if len(j) >= 1000:
                out["limitations"].append("gate trades response hit limit 1000; window may be truncated")
        else:
            out["limitations"].append("gate trades unavailable (HTTP %s)" % r["status"])
        out["limitations"].append("Gate trades size in contracts; no first-party historical order book; spread unresolved")
    elif venue == "KRAKEN_FUTURES":
        since = lo
        for page in range(6):
            r = get("https://futures.kraken.com/api/history/v3/market/%s/executions?since=%d&before=%d&sort=asc&count=1000" % (inst, since, hi))
            m = S1.preserve_raw("KRAKEN", base, "stage4_executions_%s_p%02d" % (fill_date, page), r, {"symbol": inst, "since_ms": since, "before_ms": hi, "page": page}, run_id)
            out["metas"].append(m)
            j = _parse(r) or {}
            els = j.get("elements") or []
            for e in els:
                ts = int(e.get("timestamp", 0))
                ex = ((e.get("event") or {}).get("Execution") or {}).get("execution") or {}
                if lo <= ts < hi and ex:
                    trades.append((ts, _f(ex.get("price")), _f(ex.get("quantity"))))
            out["trades_class"] = OBSERVED
            if len(els) < 1000:
                break
            since = max(int(e.get("timestamp", 0)) for e in els) + 1
        out["limitations"].append("Kraken Futures executions history; no first-party historical order book; spread unresolved")
    elif venue == "BITFINEX":
        r = get("https://api-pub.bitfinex.com/v2/trades/%s/hist?start=%d&end=%d&limit=10000&sort=1" % (inst, lo, hi))
        m = S1.preserve_raw("BITFINEX", base, "stage4_public_trades_%s" % fill_date, r, {"pair": inst, "start_ms": lo, "end_ms": hi, "limit": 10000}, run_id)
        out["metas"].append(m)
        j = _parse(r)
        if isinstance(j, list):
            for x in j:
                if isinstance(x, list) and len(x) >= 4 and lo <= int(x[1]) < hi:
                    trades.append((int(x[1]), _f(x[3]), abs(_f(x[2]) or 0)))
            out["trades_class"] = OBSERVED
        else:
            out["limitations"].append("bitfinex trades unavailable (HTTP %s)" % r["status"])
        out["limitations"].append("Bitfinex public trades; no first-party historical order book; spread unresolved")
    if venue != "BINANCE":
        out["trades"] = _summarise_trades(trades)
        out["trades"]["summary_class"] = DERIVED
        if out["trades_class"] == OBSERVED:
            out["trades_status"] = LIQ_OBSERVED if out["trades"]["trade_count"] > 0 else LIQ_NONE_IN_WINDOW
    out["never_inferred"] = ["zero_spread", "infinite_liquidity", "full_fill_at_candle_open", "zero_market_impact"]
    return out


# --------------------------------------------------------------------------------------------
def signal_verdict(fee: dict, con: dict, fills: list, fill_evidence: dict) -> dict:
    """PURE, fail-closed per frozen plan: steps 5 AND 6 must be historically proven for PASS."""
    executed = [f for f in fills if f["kind"] in ("ENTRY", "EXIT")]
    liq = [fill_evidence.get(f["date"]) for f in executed]
    missing = []
    if fee["historical_status"] != FEE_HIST_PROVEN:
        missing.append("historical_fee")
    if con["historical_status"] != CON_HIST_PROVEN:
        missing.append("historical_tick_lot_minimum")
    if not executed:
        missing.append("no_executed_fill_in_lifecycle")
    fail_liq = [x["fill_date"] for x in liq if x and x["trades_status"] == LIQ_NONE_IN_WINDOW]
    unres_liq = [f["date"] for f, x in zip(executed, liq) if not x or x["trades_status"] == LIQ_UNRESOLVED]
    unres_spread = [f["date"] for f, x in zip(executed, liq) if not x or x["spread_status"] == SPREAD_UNRESOLVED]
    if fail_liq:
        return {"verdict": FAIL_LIQ, "missing": missing, "detail": "no first-party market activity in the %d-minute window after the fill timestamp on %s" % (FILL_WINDOW_MINUTES, fail_liq)}
    if unres_liq:
        missing.append("liquidity_evidence_at_fill:%s" % unres_liq)
    if unres_spread:
        missing.append("spread_evidence_at_fill:%s" % unres_spread)
    if not missing:
        return {"verdict": PASS, "missing": [], "detail": "all frozen step 5 and 6 elements historically proven"}
    first = missing[0]
    v = UNRES_FEE if first == "historical_fee" else UNRES_CON if first == "historical_tick_lot_minimum" else UNRES_LIQ if first.startswith("liquidity") else UNRES_SPREAD if first.startswith("spread") else UNRES_LIQ
    return {"verdict": v, "missing": missing, "detail": "fail-closed: decisive historical evidence missing for %s" % ", ".join(missing)}


def run_stage4(get: Callable = http_get, run_id: str | None = None, sleep_s: float = 0.2, stage3: dict | None = None, dry_run: dict | None = None) -> dict:
    run_id = run_id or _dt.now(_tz.utc).strftime("%Y%m%dT%H%M%SZ")
    stage3 = stage3 or load_stage3_of_record()
    dry_run = dry_run or S3.load_dry_run()
    lo, hi = stage3["range_fetched"][0], stage3["horizon"]["required_coverage_end"]
    eligible = {p["signal_id"]: p for p in stage3["per_signal"] if p["verdict"] == S3.PASS}
    inst_by_asset = {i["c22_asset"]: i for i in stage3["instruments"]}
    fills = required_fills(dry_run, set(eligible))
    cache: dict = {}
    # step 5 per instrument
    step5: dict = {}
    for asset, i in sorted(inst_by_asset.items()):
        base = asset.split(":")[1]
        base = base[:-4] if base.endswith("USDT") else base[:-3]
        step5[asset] = fetch_fee_and_constraints(i["venue"], i["instrument"], base, get, run_id, cache, (lo, hi))
        if sleep_s:
            time.sleep(sleep_s)
    # step 6 per unique (asset, fill_date)
    step6: dict = {}
    for sid, w in sorted(fills.items()):
        asset = w["symbol"]
        i = inst_by_asset[asset]
        base = asset.split(":")[1]
        base = base[:-4] if base.endswith("USDT") else base[:-3]
        for f in w["fills"]:
            if f["date"] and (asset, f["date"]) not in step6:
                step6[(asset, f["date"])] = fetch_fill_liquidity(i["venue"], i["instrument"], base, f["date"], get, run_id)
                if sleep_s:
                    time.sleep(sleep_s)
    # per-signal verdicts over all 75 shorts
    per_signal = []
    for p in stage3["per_signal"]:
        sid = p["signal_id"]
        base_rec = {"signal_id": sid, "c22_asset": p["c22_asset"], "decision_date": p["decision_date"], "signal": p["signal"], "stage3_verdict": p["verdict"],
                    "fills": None, "fee_status": None, "constraint_status": None, "verdict": None, "missing_decisive_evidence": [], "detail": None}
        if sid not in eligible:
            base_rec.update(verdict=NOT_ELIGIBLE, detail="not eligible: %s" % p["verdict"])
            per_signal.append(base_rec)
            continue
        w = fills.get(sid, {"fills": []})
        asset = p["c22_asset"]
        s5 = step5[asset]
        fe = {d: step6.get((asset, d)) for d in {f["date"] for f in w["fills"] if f["date"]}}
        v = signal_verdict(s5["fee"], s5["constraints"], w["fills"], fe)
        base_rec.update(fills=w["fills"], fee_status=s5["fee"]["historical_status"], constraint_status=s5["constraints"]["historical_status"],
                        fill_evidence={d: {k: x[k] for k in ("trades_status", "spread_status", "trades_class", "depth_class")} | {"trades": x.get("trades"), "depth": x.get("depth")} for d, x in fe.items() if x},
                        verdict=v["verdict"], missing_decisive_evidence=v["missing"], detail=v["detail"])
        per_signal.append(base_rec)
    counts = {v: sum(1 for x in per_signal if x["verdict"] == v) for v in VERDICTS}
    assert sum(counts.values()) == len(per_signal) == 75, "stage4_accounting_broken"
    fills_all = list(step6.values())
    cov = {
        "fee_evidence": {"instruments": len(step5), "historical_fee_proven": sum(1 for s in step5.values() if s["fee"]["historical_status"] == FEE_HIST_PROVEN),
                         "historical_fee_unresolved": sum(1 for s in step5.values() if s["fee"]["historical_status"] == FEE_HIST_UNRESOLVED),
                         "current_fee_only_available": sum(1 for s in step5.values() if s["fee"]["current_status"] == FEE_CURRENT_ONLY),
                         "current_fee_not_exposed_by_public_api": sum(1 for s in step5.values() if s["fee"]["current_status"] == FEE_CURRENT_UNAVAILABLE)},
        "tick_lot_minimum_evidence": {"instruments": len(step5), "historical_constraint_proven": sum(1 for s in step5.values() if s["constraints"]["historical_status"] == CON_HIST_PROVEN),
                                      "current_constraint_only": sum(1 for s in step5.values() if s["constraints"]["current_values"] and s["constraints"]["historical_status"] != CON_HIST_PROVEN),
                                      "historical_constraint_unresolved": sum(1 for s in step5.values() if s["constraints"]["historical_status"] == CON_HIST_UNRESOLVED),
                                      "change_timestamp_after_window": [a for a, s in step5.items() if s["constraints"].get("change_timestamp") and s["constraints"]["change_timestamp"] > hi]},
        "spread_evidence": {"fill_windows": len(fills_all), "depth_proxy_observed_binance_bookdepth": sum(1 for x in fills_all if x["spread_status"] == SPREAD_DEPTH_PROXY),
                            "bbo_spread_observed": 0, "unresolved_no_first_party_book": sum(1 for x in fills_all if x["spread_status"] == SPREAD_UNRESOLVED)},
        "liquidity_evidence": {"fill_windows": len(fills_all), "observed_first_party": sum(1 for x in fills_all if x["trades_status"] == LIQ_OBSERVED),
                               "no_activity_in_window": sum(1 for x in fills_all if x["trades_status"] == LIQ_NONE_IN_WINDOW),
                               "unresolved": sum(1 for x in fills_all if x["trades_status"] == LIQ_UNRESOLVED)},
    }
    classes = {"observed_first_party": ["depth snapshots (Binance archived bookDepth)", "public trades (Bybit archive, OKX, Gate, Kraken Futures, Bitfinex)", "current instrument filters", "current fee values where public"],
               "derived_from_observed_data": ["trade-window summaries (count, VWAP, notional, price range)"],
               "frozen_conservative_assumption": [], "sensitivity_only": ["37 bps round-trip (pre-existing, not used here)"],
               "unresolved": ["historical fee schedules with effective dates (all venues)", "historical tick/lot/minimum effective dates (all venues)", "best-bid/ask spread at fill timestamps (all venues)", "order-book depth at fill (non-Binance venues)"]}
    funnel = dict(stage3["funnel"])
    funnel.update({"stage4_pass": counts[PASS], "stage4_unresolved": sum(v for k, v in counts.items() if k.startswith("UNRESOLVED")), "stage4_fail": counts[FAIL_LIQ],
                   "steps_remaining_before_admission": ["7_full_holding_period_coverage", "admission_review", "cost_base_case_governance"], "fee_honestly_replayable_trades": 0})
    blockers = [
        "historical fee schedules with effective dates are not exposed by any venue's public API (T2 archived fee records required, or a frozen conservative fee ASSUMPTION adopted through governance and labelled as such)",
        "historical tick/lot/minimum effective dates are not exposed (Gate's config_change_time proves changes AFTER the window for GT_USDT/ASTER_USDT); a governance decision is needed on CURRENT_CONSTRAINT_ONLY values",
        "best-bid/ask spread at the fill timestamps is unavailable first-party for every venue; Binance archived bookDepth provides a depth proxy only",
        "step 7 full-holding-period sign-off, admission review token, cost base case freeze, weekend-rule ruling, basis review, long-signal execution evidence",
    ]
    return {"report": "c22_b3_stage4_fees_liquidity", "stage": STAGE, "stage_version": STAGE_VERSION, "run_id": run_id,
            "mode": "READ_ONLY_FEE_CONSTRAINT_LIQUIDITY_SPREAD_EVIDENCE",
            "frozen_contract": {"module": "sparta_commander.c22_historical_evidence_acquisition_plan_contract", "acquisition_steps": list(FROZEN_STEPS), "authorization_batch": FROZEN_BATCH,
                                "human_token_name": FROZEN_TOKEN, "authorization_basis": "operator message 2026-09-11 (Stage Four under the frozen plan + additive evidence constraints); no approval record fabricated",
                                "categories_perp": ["fee_schedules_and_effective_dates", "tick_size", "lot_size", "minimum_notional", "historical_volume", "historical_spread_or_orderbook_proxy"],
                                "categories_margin": ["fee_schedules", "lot_tick_minimum_rules", "historical_volume", "historical_spread"],
                                "layout": {"fees": B3.PROPOSED_LAYOUT["fees"], "liquidity": B3.PROPOSED_LAYOUT["liquidity"]}},
            "inputs": {"stage3_report": {"run": STAGE3_RUN_OF_RECORD, "sha256": STAGE3_REPORT_SHA256}, "dry_run_sha256": S3.DRY_RUN_SHA256, "v2_artifact_sha256": stage3["inputs"]["v2_artifact_sha256"]},
            "required_window": [lo, hi], "fill_window_minutes": FILL_WINDOW_MINUTES,
            "step5_per_instrument": {a: {k: v for k, v in s.items() if k != "metas"} for a, s in step5.items()},
            "step6_per_fill": [{k: v for k, v in x.items() if k != "metas"} for x in fills_all],
            "per_signal": per_signal, "verdict_counts": counts, "coverage": cov, "evidence_classes": classes,
            "funnel": funnel, "blockers_before_admission": blockers,
            "raw_evidence_files": sorted({(m["raw_path"], m["raw_sha256"]) for s in step5.values() for m in s["metas"]} | {(m["raw_path"], m["raw_sha256"]) for x in fills_all for m in x["metas"]}),
            "assumptions_selected": [], "assumption_selection_against_pnl": False,
            "next_frozen_step": B3.ACQUISITION_ORDER[6], "next_step_started": False, "c22_performance_computed": False, "cost_arithmetic_performed": False,
            "strategy_rules_modified": False, "v2_modified": False, "exports_modified": False, "admission_state_changed": False}


def write_evidence_files(r: dict) -> list:
    """Frozen layout: fees/<venue>/ and liquidity/<asset>/ canonical files with sha256 sidecars."""
    written = []
    for asset, s in r["step5_per_instrument"].items():
        d = FEES_DIR / s["venue"]
        d.mkdir(parents=True, exist_ok=True)
        p = d / ("%s__%s__fee_and_constraints__%s_%s__%s.json" % (s["venue"], asset.split(":")[1], r["required_window"][0], r["required_window"][1], r["run_id"]))
        if p.exists():
            raise Stage4Error("refuse_overwrite:%s" % p.name)
        blob = S1._canon(s); p.write_bytes(blob); p.with_suffix(".json.sha256").write_text(S1._sha(blob) + "\n", encoding="utf-8")
        written.append({"path": S1._rel(p), "sha256": S1._sha(blob)})
    by_asset: dict = {}
    for x in r["step6_per_fill"]:
        by_asset.setdefault(x["instrument"], []).append(x)
    for inst, xs in by_asset.items():
        base = xs[0]["instrument"]
        d = LIQ_DIR / base
        d.mkdir(parents=True, exist_ok=True)
        p = d / ("%s__%s__fill_liquidity__%s_%s__%s.json" % (xs[0]["venue"], base, min(x["fill_date"] for x in xs), max(x["fill_date"] for x in xs), r["run_id"]))
        if p.exists():
            raise Stage4Error("refuse_overwrite:%s" % p.name)
        blob = S1._canon(sorted(xs, key=lambda x: x["fill_date"])); p.write_bytes(blob); p.with_suffix(".json.sha256").write_text(S1._sha(blob) + "\n", encoding="utf-8")
        written.append({"path": S1._rel(p), "sha256": S1._sha(blob)})
    return written


def render_markdown(r: dict) -> str:
    c, f = r["coverage"], r["funnel"]
    L = ["# C22 — B3 Stage Four: Fees / Tick-Lot-Min / Liquidity / Spread (run %s)" % r["run_id"], "",
         "Frozen steps %s (batch %s, token name %s). Read-only. No performance, no cost arithmetic, no assumptions selected, no admission change." % (r["frozen_contract"]["acquisition_steps"], r["frozen_contract"]["authorization_batch"], r["frozen_contract"]["human_token_name"]), "",
         "- Fee evidence: %s" % json.dumps(c["fee_evidence"], sort_keys=True),
         "- Tick/lot/minimum evidence: %s" % json.dumps(c["tick_lot_minimum_evidence"], sort_keys=True),
         "- Spread evidence: %s" % json.dumps(c["spread_evidence"], sort_keys=True),
         "- Liquidity evidence: %s" % json.dumps(c["liquidity_evidence"], sort_keys=True),
         "- Verdicts: %s" % json.dumps({k: v for k, v in r["verdict_counts"].items() if v}, sort_keys=True), "",
         "## Step 5 per instrument", "", "| asset | instrument | fee historical | fee current | fee values | constraint historical | current tick/lot/min | change ts |", "|---|---|---|---|---|---|---|---|"]
    for a, s in r["step5_per_instrument"].items():
        L.append("| %s | %s @ %s | %s | %s | %s | %s | %s | %s |" % (a, s["instrument"], s["venue"], s["fee"]["historical_status"], s["fee"]["current_status"], json.dumps(s["fee"]["current_values"]),
                                                              s["constraints"]["historical_status"], json.dumps(s["constraints"]["current_values"]), s["constraints"].get("change_timestamp")))
    L += ["", "## Step 6 per fill window (%d minutes after 00:00 UTC of the fill date)" % r["fill_window_minutes"], "", "| instrument | fill date | liquidity | class | trades / depth summary | spread |", "|---|---|---|---|---|---|"]
    for x in r["step6_per_fill"]:
        summ = x["trades"] if x["trades"] else (x["depth"] and {k: x["depth"][k] for k in ("snapshot_utc", "bid_notional_within_0_2pct", "ask_notional_within_0_2pct")})
        L.append("| %s @ %s | %s | %s | %s | %s | %s |" % (x["instrument"], x["venue"], x["fill_date"], x["trades_status"], x["trades_class"], json.dumps(summ, default=str)[:160], x["spread_status"]))
    L += ["", "## Per-signal verdicts", "", "| signal | S3 | fee | constraint | **S4** | missing |", "|---|---|---|---|---|---|"]
    for p in r["per_signal"]:
        L.append("| %s | %s | %s | %s | **%s** | %s |" % (p["signal_id"], p["stage3_verdict"], p["fee_status"], p["constraint_status"], p["verdict"], "; ".join(map(str, p["missing_decisive_evidence"]))[:140]))
    L += ["", "## Evidence classes", ""]
    for k, v in r["evidence_classes"].items():
        L.append("- %s: %s" % (k, "; ".join(v) if v else "none"))
    L += ["", "## Funnel", "", "| item | value |", "|---|---|"]
    for k, v in f.items():
        L.append("| %s | %s |" % (k, v))
    L += ["", "## Blockers before admission", ""] + ["- %s" % b for b in r["blockers_before_admission"]]
    L += ["", "## Raw sources", "", "| raw file | sha256 |", "|---|---|"] + ["| %s | `%s` |" % (p, s) for p, s in r["raw_evidence_files"]]
    return "\n".join(L) + "\n"


def write_report(r: dict) -> dict:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    base = REPORT_DIR / ("c22_b3_stage4_fees_liquidity_%s" % r["run_id"])
    jp, mp = base.with_suffix(".json"), base.with_suffix(".md")
    for p in (jp, mp):
        if p.exists():
            raise Stage4Error("refuse_overwrite_report:%s" % p.name)
    files = write_evidence_files(r)
    r["canonical_evidence_files"] = files
    blob = json.dumps(r, indent=2, sort_keys=True, default=str).encode("utf-8") + b"\n"
    tmp = jp.with_suffix(".tmp"); tmp.write_bytes(blob); os.replace(tmp, jp)
    tmp = mp.with_suffix(".tmp"); tmp.write_bytes(render_markdown(r).encode("utf-8")); os.replace(tmp, mp)
    S1.MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    man = S1.MANIFEST_DIR / ("stage4_run_manifest__%s.json" % r["run_id"])
    man.write_bytes(S1._canon({"stage": STAGE, "frozen_steps": list(FROZEN_STEPS), "run_id": r["run_id"], "report_json": S1._rel(jp), "report_sha256": S1._sha(blob),
                               "raw_evidence_files": r["raw_evidence_files"], "canonical_evidence_files": files,
                               "note": "STAGE FOUR ONLY (steps 5-6): not an admission manifest; no assumption selected; the fee-honest precondition shell must keep failing closed."}))
    return {"report_json": S1._rel(jp), "report_md": S1._rel(mp), "report_sha256": S1._sha(blob), "run_manifest": S1._rel(man)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", default=None)
    a = ap.parse_args(argv)
    r = run_stage4(run_id=a.run_id)
    w = write_report(r)
    print(json.dumps({"run_id": r["run_id"], "verdict_counts": {k: v for k, v in r["verdict_counts"].items() if v}, "coverage": r["coverage"], "funnel": r["funnel"], **w}, indent=2, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
