"""Candidate #22 -- B3 STAGE ONE: HISTORICAL INSTRUMENT-EXISTENCE EVIDENCE (READ-ONLY; RESEARCH ONLY).

Answers ONE question per frozen V2 short signal date: "did a correctly identified candidate
execution instrument exist, at the Signum-named venue, on the required historical date?"
It proves NOTHING about shortability, funding, borrow, fills, liquidity, spread, fees or
slippage (those are later B3 stages and are never collapsed into this one).

Evidence rule: CURRENT EXISTENCE IS NOT HISTORICAL EXISTENCE. A verdict of
PASS_HISTORICAL_EXISTENCE requires first-party dated evidence -- an authoritative launch /
listing / creation timestamp from the venue's official public API, or official historical
market data demonstrably preceding the required date. Present-day pair lists are recorded but
are NON-DECISIVE. Aggregators are never used.

Per official fetch: raw bytes preserved (never overwritten; timestamped filename), endpoint +
parameters + UTC retrieval time recorded, raw SHA-256, deterministic normalized record with its
own SHA-256, provenance from conclusion back to source bytes.

Only public, unauthenticated GET endpoints on an explicit allowlist are ever contacted; no
credentials, no account/order/trade endpoints, no environment secrets. Same-venue candidates
only (B3: no cross-venue substitution without a human venue selection).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date as _date, datetime as _dt, timedelta as _td, timezone as _tz
from pathlib import Path
from typing import Any, Callable

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import sparta_commander.c22_historical_evidence_acquisition_plan_contract as B3  # noqa: E402
import sparta_commander.c22_short_instrument_evidence_request_contract as B2  # noqa: E402
import tools.c22_replay_dry_run_once as DR  # noqa: E402

STAGE = "B3_STAGE_ONE_INSTRUMENT_EXISTENCE"
STAGE_VERSION = "c22_b3_stage1_v1"
EVIDENCE_ROOT = REPO_ROOT / B3.PROPOSED_EVIDENCE_ROOT
RAW_DIR = EVIDENCE_ROOT / "raw"
REGISTRY_DIR = EVIDENCE_ROOT / "registry"
MANIFEST_DIR = EVIDENCE_ROOT / "manifests"
REPORT_DIR = REPO_ROOT / "reports" / "c22_gc_b3_stage1"
_USER_AGENT = "sparta-brain-c22-b3-stage1-readonly/1.0"

ALLOWED_URL_PREFIXES = (
    "https://fapi.binance.com/fapi/v1/exchangeInfo",
    "https://api.bybit.com/v5/market/instruments-info",
    "https://api.bybit.com/v5/market/kline",
    "https://www.okx.com/api/v5/public/instruments",
    "https://api.gateio.ws/api/v4/futures/usdt/contracts/",
    "https://api.exchange.coinbase.com/products/",
    "https://api.international.coinbase.com/api/v1/instruments",
    "https://futures.kraken.com/derivatives/api/v3/instruments",
    "https://futures.kraken.com/api/charts/v1/trade/",
    "https://api.kraken.com/0/public/AssetPairs",
    "https://api-pub.bitfinex.com/v2/candles/",
    "https://api-pub.bitfinex.com/v2/conf/pub:list:pair:margin",
)
FORBIDDEN_URL_FRAGMENTS = ("account", "order", "trade/", "userdata", "signed", "signature", "apikey",
                           "api_key", "secret", "private", "withdraw", "position", "wallet", "auth")

# verdicts (fail-closed, deterministic)
PASS = "PASS_HISTORICAL_EXISTENCE"
FAIL_AFTER = "FAIL_LISTED_AFTER_SIGNAL"
FAIL_ASSET = "FAIL_WRONG_ASSET"
FAIL_TYPE = "FAIL_WRONG_INSTRUMENT_TYPE"
FAIL_DELISTED = "FAIL_DELISTED_BEFORE_SIGNAL"
UNRES_DATE = "UNRESOLVED_NO_AUTHORITATIVE_DATE"
UNRES_IDENTITY = "UNRESOLVED_IDENTITY_COLLISION"
UNRES_SOURCE = "UNRESOLVED_SOURCE_INSUFFICIENT"
FAIL_ABSENT = "FAIL_NO_SUCH_INSTRUMENT_AT_VENUE"
VERDICTS = (PASS, FAIL_AFTER, FAIL_ASSET, FAIL_TYPE, FAIL_DELISTED, FAIL_ABSENT, UNRES_DATE, UNRES_IDENTITY, UNRES_SOURCE)

# what an existence_date means (never conflate a launch timestamp with "seen trading since")
SEM_LAUNCH = "AUTHORITATIVE_LAUNCH_OR_LISTING_TIMESTAMP"
SEM_SEEN_SINCE = "EXISTENCE_PROVEN_AT_LEAST_SINCE_EARLIEST_OFFICIAL_CANDLE_IN_REQUESTED_WINDOW"

EVIDENCE_LAUNCH_TS = "AUTHORITATIVE_LAUNCH_TIMESTAMP"
EVIDENCE_HIST_DATA = "OFFICIAL_HISTORICAL_MARKET_DATA_PRECEDING_DATE"
EVIDENCE_PRESENT_ONLY = "PRESENT_DAY_LISTING_ONLY_NON_DECISIVE"

CANDLE_WINDOW_START = "2026-06-01"   # official history requested from before the first frozen signal
CANDLE_WINDOW_END = "2026-07-20"


class Stage1Error(RuntimeError):
    pass


# --------------------------------------------------------------------------------------------
# safe HTTP (read-only)
# --------------------------------------------------------------------------------------------
def _assert_safe_url(url: str) -> None:
    if not isinstance(url, str) or not url.startswith("https://"):
        raise Stage1Error("refusing non-https url")
    if not any(url.startswith(p) for p in ALLOWED_URL_PREFIXES):
        raise Stage1Error("refusing non-allowlisted url: %s" % url)
    low = url.lower()
    for frag in FORBIDDEN_URL_FRAGMENTS:
        if frag in low and not (frag == "trade/" and "/charts/v1/trade/" in low):
            raise Stage1Error("refusing url containing forbidden fragment %r" % frag)


def http_get(url: str, timeout: float = 30.0) -> dict:
    """Read-only GET. Returns {url, status, retrieved_utc, raw_bytes}. Never raises on HTTP
    error codes (the body is evidence too); raises only on refusal/network failure."""
    _assert_safe_url(url)
    req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT}, method="GET")
    retrieved = _dt.now(_tz.utc).isoformat(timespec="seconds")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return {"url": url, "status": r.status, "retrieved_utc": retrieved, "raw_bytes": r.read()}
    except urllib.error.HTTPError as e:
        return {"url": url, "status": e.code, "retrieved_utc": retrieved, "raw_bytes": e.read()}


# --------------------------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------------------------
def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _rel(p: Path) -> str:
    return str(p.relative_to(REPO_ROOT) if p.is_relative_to(REPO_ROOT) else p).replace("\\", "/")


def _canon(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")


def _ms_to_date(ms: Any) -> str | None:
    try:
        v = int(ms)
    except (TypeError, ValueError):
        return None
    if v <= 0:
        return None
    return _dt.fromtimestamp(v / 1000.0, _tz.utc).date().isoformat()


def _s_to_date(s: Any) -> str | None:
    try:
        v = int(s)
    except (TypeError, ValueError):
        return None
    return _dt.fromtimestamp(v, _tz.utc).date().isoformat() if v > 0 else None


def _iso_to_date(s: Any) -> str | None:
    if not isinstance(s, str) or len(s) < 10:
        return None
    return s[:10]


def _ms(date_iso: str) -> int:
    return int(_dt.fromisoformat(date_iso + "T00:00:00+00:00").timestamp() * 1000)


def _next_weekday(d: str) -> str:
    x = _date.fromisoformat(d) + _td(days=1)
    while x.weekday() >= 5:
        x += _td(days=1)
    return x.isoformat()


# --------------------------------------------------------------------------------------------
# frozen cohort
# --------------------------------------------------------------------------------------------
def required_short_signals() -> list:
    sigs, sha = DR.load_frozen_v2_signals()
    shorts = [s for s in sigs if s["signal"] in B2.SHORT_SIGNALS]
    if len(shorts) != B2.EXPECTED_BEAR_SHORT + B2.EXPECTED_HEDGE_SHORT:
        raise Stage1Error("short_signal_count_%d_ne_75" % len(shorts))
    for s in shorts:
        s["fill_date_calendar"] = (_date.fromisoformat(s["decision_date"]) + _td(days=1)).isoformat()
        s["fill_date_weekday"] = _next_weekday(s["decision_date"])
    return sorted(shorts, key=lambda s: (s["symbol"], s["decision_date"]))


def assets_with_dates(shorts: list) -> dict:
    out: dict = {}
    for s in shorts:
        a = out.setdefault(s["symbol"], {"symbol": s["symbol"], "parsed": B2.parse_symbol(s["symbol"]),
                                         "mapping_risk": B2.mapping_risk_class(s["symbol"]), "signals": []})
        a["signals"].append({"decision_date": s["decision_date"], "signal": s["signal"], "market_rank": s["market_rank"],
                             "fill_date_calendar": s["fill_date_calendar"], "fill_date_weekday": s["fill_date_weekday"]})
    if len(out) != B2.EXPECTED_SHORT_ASSET_COUNT:
        raise Stage1Error("short_asset_count_%d_ne_22" % len(out))
    return out


# --------------------------------------------------------------------------------------------
# pure verdict logic
# --------------------------------------------------------------------------------------------
def verdict_for_date(candidate: dict, decision_date: str, fill_dates: list) -> dict:
    """PURE. candidate: {identity_ok, identity_collision_unresolved, instrument_type_ok,
    existence_date (ISO or None), existence_evidence (type), delisted_date (ISO or None),
    source_ok}. Fail-closed order: source -> identity -> type -> date -> delisting."""
    r = {"decision_date": decision_date, "fill_dates": fill_dates, "verdict": None, "reason": None}
    if not candidate.get("source_ok", False):
        r.update(verdict=UNRES_SOURCE, reason=candidate.get("source_note") or "official_source_unavailable_or_unparseable")
        return r
    if candidate.get("instrument_absent"):
        r.update(verdict=FAIL_ABSENT, reason=candidate.get("identity_note") or "official_source_lists_no_such_instrument")
        return r
    if candidate.get("identity_collision_unresolved"):
        r.update(verdict=UNRES_IDENTITY, reason=candidate.get("identity_note") or "ticker_collision_not_resolved_by_first_party_evidence")
        return r
    if not candidate.get("identity_ok", False):
        r.update(verdict=FAIL_ASSET, reason=candidate.get("identity_note") or "venue_base_asset_differs_from_c22_asset")
        return r
    if not candidate.get("instrument_type_ok", False):
        r.update(verdict=FAIL_TYPE, reason=candidate.get("type_note") or "instrument_cannot_express_a_short")
        return r
    ex = candidate.get("existence_date")
    if not ex or candidate.get("existence_evidence") == EVIDENCE_PRESENT_ONLY:
        r.update(verdict=UNRES_DATE, reason="no_authoritative_dated_existence_evidence_present_day_listing_is_non_decisive")
        return r
    if ex > decision_date:
        r.update(verdict=FAIL_AFTER, reason="existence_date_%s_after_decision_%s" % (ex, decision_date))
        return r
    dl = candidate.get("delisted_date")
    latest_needed = max([decision_date] + list(fill_dates))
    if dl and dl <= latest_needed:
        r.update(verdict=FAIL_DELISTED, reason="delisted_%s_on_or_before_required_%s" % (dl, latest_needed))
        return r
    r.update(verdict=PASS, reason="%s:%s<=%s" % (candidate.get("existence_evidence"), ex, decision_date))
    return r


# --------------------------------------------------------------------------------------------
# raw preservation
# --------------------------------------------------------------------------------------------
def preserve_raw(venue: str, asset: str, category: str, resp: dict, params: dict, run_id: str) -> dict:
    """Write raw bytes + .sha256 + .meta.json under raw/<venue>/<asset>/; never overwrites."""
    d = RAW_DIR / venue / asset
    d.mkdir(parents=True, exist_ok=True)
    stamp = resp["retrieved_utc"].replace(":", "").replace("+0000", "Z")
    base = d / ("%s__%s__%s__%s__%s" % (venue, asset, category, run_id, stamp))
    raw_path = base.with_suffix(".raw.json")
    if raw_path.exists():
        raise Stage1Error("refuse_overwrite_raw:%s" % raw_path.name)
    sha = _sha(resp["raw_bytes"])
    tmp = raw_path.with_suffix(".tmp")
    with open(tmp, "wb") as fh:
        fh.write(resp["raw_bytes"])
    os.replace(tmp, raw_path)
    (base.with_suffix(".raw.json.sha256")).write_text(sha + "\n", encoding="utf-8")
    meta = {"venue": venue, "asset": asset, "category": category, "endpoint": resp["url"].split("?")[0],
            "query_params": params, "full_url": resp["url"], "http_status": resp["status"],
            "retrieved_utc": resp["retrieved_utc"], "raw_sha256": sha, "raw_bytes": len(resp["raw_bytes"]),
            "raw_path": _rel(raw_path), "run_id": run_id, "stage": STAGE}
    (base.with_suffix(".meta.json")).write_bytes(_canon(meta))
    return meta


def _parse(resp: dict):
    try:
        return json.loads(resp["raw_bytes"].decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return None


# --------------------------------------------------------------------------------------------
# venue evaluators (each returns a list of candidate-instrument records + fetch metas)
# --------------------------------------------------------------------------------------------
def _cand(venue, inst_symbol, inst_type, base, quote, contract_type, **kw) -> dict:
    c = {"venue": venue, "venue_instrument_symbol": inst_symbol, "instrument_type": inst_type,
         "base_asset": base, "quote_or_settlement_asset": quote, "contract_type": contract_type,
         "identity_ok": False, "identity_collision_unresolved": False, "identity_note": None, "instrument_absent": False,
         "instrument_type_ok": False, "type_note": None, "existence_date": None, "existence_evidence": None,
         "existence_date_semantics": None,
         "existence_timestamp_raw": None, "delisted_date": None, "source_ok": False, "source_note": None,
         "evidence_sources": [], "present_day_only_observations": []}
    c.update(kw)
    return c


def eval_binance(asset: dict, get: Callable, run_id: str, cache: dict) -> list:
    base = asset["parsed"]["base"]
    sym = "%sUSDT" % base
    if "binance_exchangeinfo" not in cache:
        resp = get("https://fapi.binance.com/fapi/v1/exchangeInfo")
        meta = preserve_raw("BINANCE", "_shared", "usdm_exchangeinfo", resp, {}, run_id)
        cache["binance_exchangeinfo"] = (resp, meta, _parse(resp))
    resp, meta, j = cache["binance_exchangeinfo"]
    c = _cand("BINANCE", sym, "linear_perpetual_futures", base, "USDT", "PERPETUAL")
    c["evidence_sources"].append(meta)
    if not j or "symbols" not in j:
        c["source_note"] = "exchangeInfo_unparseable"
        return [c]
    row = next((s for s in j["symbols"] if s.get("symbol") == sym), None)
    if row is None:
        c.update(source_ok=True, instrument_absent=True, identity_ok=False, identity_note="no_usdm_perpetual_named_%s_in_official_exchangeInfo" % sym,
                 instrument_type_ok=False, type_note="instrument_absent")
        return [c]
    c.update(source_ok=True, identity_ok=(row.get("baseAsset") == base and row.get("quoteAsset") == "USDT"),
             identity_note="official_baseAsset=%s quoteAsset=%s" % (row.get("baseAsset"), row.get("quoteAsset")),
             instrument_type_ok=(row.get("contractType") == "PERPETUAL"), type_note="contractType=%s status=%s" % (row.get("contractType"), row.get("status")),
             existence_date=_ms_to_date(row.get("onboardDate")), existence_evidence=EVIDENCE_LAUNCH_TS,
             existence_timestamp_raw={"onboardDate_ms": row.get("onboardDate")},
             delisted_date=None if str(row.get("status")) == "TRADING" else _ms_to_date(row.get("deliveryDate")),
             contract_type=row.get("contractType"))
    if str(row.get("status")) != "TRADING":
        c["type_note"] += " (status not TRADING today; historical delisting date unknown from this endpoint)"
        c["delisted_date"] = c["delisted_date"] or "UNKNOWN"
    return [c]


def eval_bybit(asset: dict, get: Callable, run_id: str, cache: dict) -> list:
    base = asset["parsed"]["base"]
    sym = "%sUSDT" % base
    out = []
    # linear perpetual: authoritative launchTime
    r1 = get("https://api.bybit.com/v5/market/instruments-info?category=linear&symbol=%s" % sym)
    m1 = preserve_raw("BYBIT", base, "linear_instruments_info", r1, {"category": "linear", "symbol": sym}, run_id)
    j1 = _parse(r1)
    c = _cand("BYBIT", sym, "linear_perpetual_futures", base, "USDT", "LinearPerpetual")
    c["evidence_sources"].append(m1)
    lst = (j1 or {}).get("result", {}).get("list", []) if isinstance(j1, dict) else []
    if j1 is None:
        c["source_note"] = "unparseable"
    elif not lst:
        c.update(source_ok=True, instrument_absent=True, identity_ok=False, identity_note="no_linear_perpetual_%s (retMsg=%s)" % (sym, (j1 or {}).get("retMsg")),
                 type_note="instrument_absent")
    else:
        row = lst[0]
        c.update(source_ok=True, identity_ok=(row.get("baseCoin") == base and row.get("quoteCoin") == "USDT"),
                 identity_note="official_baseCoin=%s quoteCoin=%s" % (row.get("baseCoin"), row.get("quoteCoin")),
                 instrument_type_ok=(row.get("contractType") == "LinearPerpetual"), type_note="contractType=%s status=%s" % (row.get("contractType"), row.get("status")),
                 existence_date=_ms_to_date(row.get("launchTime")), existence_evidence=EVIDENCE_LAUNCH_TS,
                 existence_timestamp_raw={"launchTime_ms": row.get("launchTime")},
                 delisted_date=_ms_to_date(row.get("deliveryTime")) if str(row.get("status")) != "Trading" else None,
                 contract_type=row.get("contractType"))
    out.append(c)
    # spot pair: identity + marginTrading flag (present-day) + official daily klines (historical)
    r2 = get("https://api.bybit.com/v5/market/instruments-info?category=spot&symbol=%s" % sym)
    m2 = preserve_raw("BYBIT", base, "spot_instruments_info", r2, {"category": "spot", "symbol": sym}, run_id)
    j2 = _parse(r2)
    r3 = get("https://api.bybit.com/v5/market/kline?category=spot&symbol=%s&interval=D&start=%d&end=%d&limit=200"
             % (sym, _ms(CANDLE_WINDOW_START), _ms(CANDLE_WINDOW_END)))
    m3 = preserve_raw("BYBIT", base, "spot_daily_kline", r3, {"category": "spot", "symbol": sym, "interval": "D",
                                                              "start": CANDLE_WINDOW_START, "end": CANDLE_WINDOW_END}, run_id)
    j3 = _parse(r3)
    cs = _cand("BYBIT", sym, "spot_margin_pair", base, "USDT", "SPOT")
    cs["evidence_sources"] += [m2, m3]
    srow = ((j2 or {}).get("result", {}).get("list") or [None])[0] if isinstance(j2, dict) else None
    kl = (j3 or {}).get("result", {}).get("list", []) if isinstance(j3, dict) else []
    if srow is None:
        cs["source_note"] = "spot_instrument_absent_or_unparseable"
    else:
        margin = str(srow.get("marginTrading"))
        cs.update(source_ok=True, identity_ok=(srow.get("baseCoin") == base), identity_note="official_baseCoin=%s" % srow.get("baseCoin"),
                  instrument_type_ok=(margin not in ("none", "None", "")), type_note="marginTrading=%s (present-day flag; historical margin availability is Stage Two)" % margin)
        cs["present_day_only_observations"].append({"marginTrading": margin, "status": srow.get("status")})
        dates = sorted(_ms_to_date(k[0]) for k in kl if _ms_to_date(k[0]))
        if dates:
            cs.update(existence_date=dates[0], existence_evidence=EVIDENCE_HIST_DATA,
                      existence_timestamp_raw={"earliest_official_daily_candle_in_window": dates[0], "candles_in_window": len(dates)})
    out.append(cs)
    return out


def eval_okx(asset: dict, get: Callable, run_id: str, cache: dict) -> list:
    base = asset["parsed"]["base"]
    out = []
    for inst_type, inst_id, itype, ctype in (("SWAP", "%s-USDT-SWAP" % base, "linear_perpetual_swap", "linear"),
                                             ("MARGIN", "%s-USDT" % base, "spot_margin_pair", "MARGIN")):
        r = get("https://www.okx.com/api/v5/public/instruments?instType=%s&instId=%s" % (inst_type, inst_id))
        m = preserve_raw("OKX", base, "public_instruments_%s" % inst_type.lower(), r, {"instType": inst_type, "instId": inst_id}, run_id)
        j = _parse(r)
        c = _cand("OKX", inst_id, itype, base, "USDT", ctype)
        c["evidence_sources"].append(m)
        data = (j or {}).get("data", []) if isinstance(j, dict) else []
        if j is None:
            c["source_note"] = "unparseable"
        elif not data:
            c.update(source_ok=True, instrument_absent=True, identity_ok=False, identity_note="instrument_absent_%s" % inst_id, type_note="instrument_absent")
        else:
            row = data[0]
            base_seen = row.get("baseCcy") or row.get("ctValCcy")
            c.update(source_ok=True, identity_ok=(base_seen == base), identity_note="official_base=%s instFamily=%s" % (base_seen, row.get("instFamily")),
                     instrument_type_ok=True, type_note="instType=%s ctType=%s state=%s" % (row.get("instType"), row.get("ctType"), row.get("state")),
                     existence_date=_ms_to_date(row.get("listTime")), existence_evidence=EVIDENCE_LAUNCH_TS,
                     existence_timestamp_raw={"listTime_ms": row.get("listTime")},
                     delisted_date=_ms_to_date(row.get("expTime")) if row.get("state") not in ("live", "preopen") else None)
        out.append(c)
    return out


def eval_gate(asset: dict, get: Callable, run_id: str, cache: dict) -> list:
    base = asset["parsed"]["base"]
    name = "%s_USDT" % base
    r = get("https://api.gateio.ws/api/v4/futures/usdt/contracts/%s" % name)
    m = preserve_raw("GATE", base, "futures_usdt_contract", r, {"contract": name}, run_id)
    j = _parse(r)
    c = _cand("GATE", name, "linear_perpetual_futures", base, "USDT", "direct")
    c["evidence_sources"].append(m)
    if not isinstance(j, dict) or "name" not in j:
        c.update(source_ok=(j is not None), instrument_absent=(j is not None), identity_ok=False,
                 identity_note="contract_absent_or_error:%s" % (j.get("label") if isinstance(j, dict) else "unparseable"),
                 type_note="instrument_absent")
        if j is None:
            c["source_note"] = "unparseable"
        return [c]
    c.update(source_ok=True, identity_ok=(j.get("name") == name), identity_note="official_contract_name=%s" % j.get("name"),
             instrument_type_ok=(j.get("type") == "direct"), type_note="type=%s status=%s in_delisting=%s" % (j.get("type"), j.get("status"), j.get("in_delisting")),
             existence_date=_s_to_date(j.get("create_time")), existence_evidence=EVIDENCE_LAUNCH_TS,
             existence_timestamp_raw={"create_time_s": j.get("create_time"), "launch_time_s": j.get("launch_time")},
             delisted_date=(_s_to_date(j.get("delisting_time")) or "UNKNOWN") if j.get("in_delisting") else None)
    return [c]


def eval_coinbase(asset: dict, get: Callable, run_id: str, cache: dict) -> list:
    base = asset["parsed"]["base"]
    out = []
    # Coinbase Exchange spot pair (the Signum-named product): identity + margin flag; not a short instrument
    pid = "%s-USD" % base
    r1 = get("https://api.exchange.coinbase.com/products/%s" % pid)
    m1 = preserve_raw("COINBASE", base, "exchange_product", r1, {"product_id": pid}, run_id)
    j1 = _parse(r1)
    c1 = _cand("COINBASE", pid, "spot_pair", base, "USD", "SPOT")
    c1["evidence_sources"].append(m1)
    if isinstance(j1, dict) and j1.get("id") == pid:
        c1.update(source_ok=True, identity_ok=(j1.get("base_currency") == base), identity_note="official_base_currency=%s" % j1.get("base_currency"),
                  instrument_type_ok=bool(j1.get("margin_enabled")), type_note="spot product; margin_enabled=%s (present-day); Coinbase Exchange spot cannot express a short" % j1.get("margin_enabled"))
        c1["present_day_only_observations"].append({"status": j1.get("status"), "margin_enabled": j1.get("margin_enabled")})
    else:
        c1["source_note"] = "product_absent_or_unparseable"
    out.append(c1)
    # Coinbase International Exchange perpetual: identity via instruments endpoint; existence via official daily candles
    perp = "%s-PERP" % base
    r2 = get("https://api.international.coinbase.com/api/v1/instruments/%s" % perp)
    m2 = preserve_raw("COINBASE", base, "intx_instrument", r2, {"instrument": perp}, run_id)
    j2 = _parse(r2)
    r3 = get("https://api.international.coinbase.com/api/v1/instruments/%s/candles?granularity=ONE_DAY&start=%sT00:00:00Z&end=%sT00:00:00Z"
             % (perp, CANDLE_WINDOW_START, CANDLE_WINDOW_END))
    m3 = preserve_raw("COINBASE", base, "intx_daily_candles", r3, {"instrument": perp, "granularity": "ONE_DAY",
                                                                  "start": CANDLE_WINDOW_START, "end": CANDLE_WINDOW_END}, run_id)
    j3 = _parse(r3)
    c2 = _cand("COINBASE_INTERNATIONAL", perp, "linear_perpetual_futures", base, "USDC", "PERP")
    c2["evidence_sources"] += [m2, m3]
    if isinstance(j2, dict) and j2.get("symbol") == perp:
        c2.update(source_ok=True, identity_ok=(j2.get("base_asset_name") == base), identity_note="official_base_asset_name=%s quote=%s (platform: Coinbase International Exchange, distinct from Coinbase Exchange spot)" % (j2.get("base_asset_name"), j2.get("quote_asset_name")),
                  instrument_type_ok=(j2.get("type") == "PERP"), type_note="type=%s mode=%s" % (j2.get("type"), j2.get("mode")))
        aggs = (j3 or {}).get("aggregations", []) if isinstance(j3, dict) else []
        dates = sorted(_iso_to_date(a.get("start")) for a in aggs if _iso_to_date(a.get("start")))
        if dates:
            c2.update(existence_date=dates[0], existence_evidence=EVIDENCE_HIST_DATA,
                      existence_timestamp_raw={"earliest_official_daily_candle_in_window": dates[0], "candles_in_window": len(dates)})
    else:
        c2["source_note"] = "intx_instrument_absent_or_unparseable"
    out.append(c2)
    return out


def eval_kraken(asset: dict, get: Callable, run_id: str, cache: dict) -> list:
    base = asset["parsed"]["base"]
    out = []
    if "kraken_fut_instruments" not in cache:
        r = get("https://futures.kraken.com/derivatives/api/v3/instruments")
        m = preserve_raw("KRAKEN", "_shared", "futures_instruments", r, {}, run_id)
        cache["kraken_fut_instruments"] = (r, m, _parse(r))
    r, m, j = cache["kraken_fut_instruments"]
    sym = "PF_%sUSD" % base
    c = _cand("KRAKEN_FUTURES", sym, "linear_perpetual_futures", base, "USD", "flexible_futures")
    c["evidence_sources"].append(m)
    rows = (j or {}).get("instruments", []) if isinstance(j, dict) else []
    row = next((x for x in rows if x.get("symbol") == sym), None)
    if j is None:
        c["source_note"] = "unparseable"
    elif row is None:
        c.update(source_ok=True, instrument_absent=True, identity_ok=False, identity_note="no_futures_instrument_%s" % sym, type_note="instrument_absent")
    else:
        collision = asset["mapping_risk"] == B2.MAPPING_RISK_HIGH_COLLISION
        resolved_note = None
        if collision:
            # first-party disambiguation: the venue classifies the instrument (category / tradfi flag)
            if row.get("tradfi") is False and str(row.get("category", "")).lower() in ("meme", "layer 1", "defi", "ai", "gaming", "layer 2", "infrastructure"):
                resolved_note = "collision_resolved_by_first_party_classification:category=%s tradfi=%s (crypto asset, not an equity index)" % (row.get("category"), row.get("tradfi"))
            else:
                resolved_note = "collision_unresolved:category=%s tradfi=%s" % (row.get("category"), row.get("tradfi"))
        c.update(source_ok=True, identity_ok=(row.get("base") == base), identity_collision_unresolved=bool(collision and resolved_note and resolved_note.startswith("collision_unresolved")),
                 identity_note="official_base=%s pair=%s category=%s tradfi=%s%s" % (row.get("base"), row.get("pair"), row.get("category"), row.get("tradfi"), ("; " + resolved_note) if resolved_note else ""),
                 instrument_type_ok=(row.get("type") == "flexible_futures"), type_note="type=%s tradeable=%s isExpired=%s" % (row.get("type"), row.get("tradeable"), row.get("isExpired")),
                 existence_date=_iso_to_date(row.get("openingDate")), existence_evidence=EVIDENCE_LAUNCH_TS,
                 existence_timestamp_raw={"openingDate": row.get("openingDate")},
                 delisted_date="UNKNOWN" if row.get("isExpired") else None)
        # corroborating official historical market activity (charts) inside the frozen window
        r2 = get("https://futures.kraken.com/api/charts/v1/trade/%s/1d?from=%d&to=%d" % (sym, _ms(CANDLE_WINDOW_START) // 1000, _ms(CANDLE_WINDOW_END) // 1000))
        m2 = preserve_raw("KRAKEN", base, "futures_daily_chart", r2, {"symbol": sym, "resolution": "1d", "from": CANDLE_WINDOW_START, "to": CANDLE_WINDOW_END}, run_id)
        c["evidence_sources"].append(m2)
        j2 = _parse(r2)
        cd = sorted(_ms_to_date(x.get("time")) for x in ((j2 or {}).get("candles", []) if isinstance(j2, dict) else []) if _ms_to_date(x.get("time")))
        c["existence_timestamp_raw"]["earliest_official_daily_candle_in_window"] = cd[0] if cd else None
        c["existence_timestamp_raw"]["candles_in_window"] = len(cd)
    out.append(c)
    # Kraken spot margin pair (secondary candidate): AssetPairs gives leverage_sell (present-day) -- no listing date
    pair = "%sUSD" % base
    r3 = get("https://api.kraken.com/0/public/AssetPairs?pair=%s" % pair)
    m3 = preserve_raw("KRAKEN", base, "spot_assetpairs", r3, {"pair": pair}, run_id)
    j3 = _parse(r3)
    cs = _cand("KRAKEN", pair, "spot_margin_pair", base, "USD", "SPOT")
    cs["evidence_sources"].append(m3)
    res = (j3 or {}).get("result", {}) if isinstance(j3, dict) else {}
    prow = next(iter(res.values()), None) if res else None
    if prow:
        cs.update(source_ok=True, identity_ok=(prow.get("base") == base), identity_note="official_base=%s wsname=%s" % (prow.get("base"), prow.get("wsname")),
                  instrument_type_ok=bool(prow.get("leverage_sell")), type_note="leverage_sell=%s (present-day margin flag; Stage Two)" % prow.get("leverage_sell"),
                  existence_evidence=EVIDENCE_PRESENT_ONLY)
        cs["present_day_only_observations"].append({"status": prow.get("status"), "leverage_sell": prow.get("leverage_sell")})
        if asset["mapping_risk"] == B2.MAPPING_RISK_HIGH_COLLISION:
            cs["identity_collision_unresolved"] = True
            cs["identity_note"] += "; spot AssetPairs carries no classification to resolve the SPX collision"
    else:
        cs["source_note"] = "assetpairs_absent_or_unparseable"
    out.append(cs)
    return out


def eval_bitfinex(asset: dict, get: Callable, run_id: str, cache: dict) -> list:
    base = asset["parsed"]["base"]
    pair = "t%sUSD" % base
    r1 = get("https://api-pub.bitfinex.com/v2/candles/trade:1D:%s/hist?start=%d&end=%d&limit=200&sort=1" % (pair, _ms(CANDLE_WINDOW_START), _ms(CANDLE_WINDOW_END)))
    m1 = preserve_raw("BITFINEX", base, "daily_candles", r1, {"pair": pair, "tf": "1D", "start": CANDLE_WINDOW_START, "end": CANDLE_WINDOW_END}, run_id)
    j1 = _parse(r1)
    if "bitfinex_margin_list" not in cache:
        r2 = get("https://api-pub.bitfinex.com/v2/conf/pub:list:pair:margin")
        m2 = preserve_raw("BITFINEX", "_shared", "margin_pair_list_present_day", r2, {}, run_id)
        cache["bitfinex_margin_list"] = (r2, m2, _parse(r2))
    r2, m2, j2 = cache["bitfinex_margin_list"]
    c = _cand("BITFINEX", pair, "spot_margin_pair", base, "USD", "SPOT")
    c["evidence_sources"] += [m1, m2]
    if not isinstance(j1, list):
        c["source_note"] = "candles_unparseable"
        return [c]
    dates = sorted(_ms_to_date(x[0]) for x in j1 if isinstance(x, list) and x and _ms_to_date(x[0]))
    margin_now = isinstance(j2, list) and j2 and isinstance(j2[0], list) and ("%sUSD" % base) in j2[0]
    c.update(source_ok=True, identity_ok=True, identity_note="pair symbol %s is venue-native (LEO is Bitfinex's own token); base inferred from official pair naming" % pair,
             instrument_type_ok=bool(margin_now), type_note="present-day margin list contains %sUSD=%s; historical margin enablement date NOT proven (Stage Two)" % (base, margin_now))
    c["present_day_only_observations"].append({"in_margin_pair_list_today": bool(margin_now)})
    if dates:
        c.update(existence_date=dates[0], existence_evidence=EVIDENCE_HIST_DATA,
                 existence_timestamp_raw={"earliest_official_daily_candle_in_window": dates[0], "candles_in_window": len(dates)})
    return [c]


VENUE_EVALUATORS = {"BINANCE": eval_binance, "BYBIT": eval_bybit, "OKX": eval_okx, "GATE": eval_gate,
                    "COINBASE": eval_coinbase, "KRAKEN": eval_kraken, "BITFINEX": eval_bitfinex}


# --------------------------------------------------------------------------------------------
# registry + report
# --------------------------------------------------------------------------------------------
def build_asset_record(asset: dict, candidates: list, run_id: str) -> dict:
    for c in candidates:
        if c.get("existence_evidence") == EVIDENCE_LAUNCH_TS:
            c["existence_date_semantics"] = SEM_LAUNCH
        elif c.get("existence_evidence") == EVIDENCE_HIST_DATA:
            c["existence_date_semantics"] = SEM_SEEN_SINCE
    per_signal = []
    for s in asset["signals"]:
        fills = [s["fill_date_calendar"], s["fill_date_weekday"]]
        vs = [dict(verdict_for_date(c, s["decision_date"], fills), venue_instrument_symbol=c["venue_instrument_symbol"],
                   instrument_type=c["instrument_type"], venue=c["venue"]) for c in candidates]
        passing = [v for v in vs if v["verdict"] == PASS]
        per_signal.append({"decision_date": s["decision_date"], "signal": s["signal"], "market_rank": s["market_rank"],
                           "fill_date_calendar": s["fill_date_calendar"], "fill_date_weekday": s["fill_date_weekday"],
                           "candidate_verdicts": vs,
                           "signal_verdict": PASS if passing else _worst(vs),
                           "passing_instruments": [v["venue_instrument_symbol"] for v in passing]})
    norm = {"stage": STAGE, "stage_version": STAGE_VERSION, "c22_asset": asset["symbol"],
            "canonical_name": None, "canonical_symbol": asset["parsed"]["base"], "signum_venue": asset["parsed"]["venue"],
            "mapping_risk": asset["mapping_risk"], "required_signal_dates": [s["decision_date"] for s in asset["signals"]],
            "candidates": [{k: v for k, v in c.items() if k != "evidence_sources"} | {"evidence_sources": [
                {"endpoint": m["endpoint"], "query_params": m["query_params"], "raw_sha256": m["raw_sha256"], "http_status": m["http_status"]}
                for m in c["evidence_sources"]]} for c in candidates],
            "per_signal": per_signal}
    norm_hash = _sha(_canon(norm))          # run-independent: no paths, no timestamps, only source bytes hashes
    rec = dict(norm, normalized_evidence_sha256=norm_hash, run_id=run_id,
               raw_evidence_files={m["raw_sha256"]: m["raw_path"] for c in candidates for m in c["evidence_sources"]},
               retrieval_utc=sorted({m["retrieved_utc"] for c in candidates for m in c["evidence_sources"]}),
               surviving_signals=sum(1 for p in per_signal if p["signal_verdict"] == PASS),
               eliminated_signals=sum(1 for p in per_signal if p["signal_verdict"].startswith("FAIL")),
               unresolved_signals=sum(1 for p in per_signal if p["signal_verdict"].startswith("UNRESOLVED")),
               second_source_recommended=_second_source_needed(asset, candidates, per_signal))
    return rec


_RANK = {PASS: 0, UNRES_IDENTITY: 1, UNRES_DATE: 2, UNRES_SOURCE: 3, FAIL_TYPE: 4, FAIL_AFTER: 5, FAIL_DELISTED: 6, FAIL_ABSENT: 7, FAIL_ASSET: 8}


def _worst(vs: list) -> str:
    """Asset-date verdict when no candidate passes: the least-bad non-PASS verdict, so an
    UNRESOLVED candidate keeps the date UNRESOLVED rather than FAILED."""
    return sorted((v["verdict"] for v in vs), key=lambda x: _RANK.get(x, 9))[0] if vs else UNRES_SOURCE


def _second_source_needed(asset: dict, candidates: list, per_signal: list) -> list:
    reasons = []
    if any(c.get("identity_collision_unresolved") for c in candidates):
        reasons.append("identity_collision_unresolved_on_a_candidate")
    if any(c.get("existence_evidence") == EVIDENCE_HIST_DATA and c.get("identity_ok") and c.get("instrument_type_ok") for c in candidates):
        reasons.append("existence_rests_on_official_market_data_not_a_launch_timestamp")
    if any(p["signal_verdict"].startswith("UNRESOLVED") for p in per_signal):
        reasons.append("unresolved_signal_dates")
    if asset["mapping_risk"] != B2.MAPPING_RISK_STANDARD:
        reasons.append("mapping_risk:%s" % asset["mapping_risk"])
    if any(c.get("venue") == "COINBASE_INTERNATIONAL" and c.get("identity_ok") for c in candidates):
        reasons.append("execution_platform_differs_from_signum_named_venue")
    return sorted(set(reasons))


def write_registry(rec: dict) -> Path:
    REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
    ps = B2.parse_symbol(rec["c22_asset"])
    p = REGISTRY_DIR / ("%s__%s__instrument_existence__%s.json" % (ps.get("venue"), ps.get("base"), rec["run_id"]))
    if p.exists():
        raise Stage1Error("refuse_overwrite_registry:%s" % p.name)
    tmp = p.with_suffix(".tmp")
    tmp.write_bytes(json.dumps(rec, indent=2, sort_keys=True, default=str).encode("utf-8") + b"\n")
    os.replace(tmp, p)
    (p.with_suffix(".json.sha256")).write_text(_sha(p.read_bytes()) + "\n", encoding="utf-8")
    return p


def run_stage1(get: Callable = http_get, run_id: str | None = None, sleep_s: float = 0.25) -> dict:
    run_id = run_id or _dt.now(_tz.utc).strftime("%Y%m%dT%H%M%SZ")
    shorts = required_short_signals()
    assets = assets_with_dates(shorts)
    cache: dict = {}
    records, files = [], []
    for sym in sorted(assets):
        a = assets[sym]
        ev = VENUE_EVALUATORS.get(a["parsed"]["venue"])
        if ev is None:
            raise Stage1Error("no_evaluator_for_venue:%s" % a["parsed"]["venue"])
        cands = ev(a, get, run_id, cache)
        rec = build_asset_record(a, cands, run_id)
        p = write_registry(rec)
        rec["registry_path"] = _rel(p)
        rec["registry_sha256"] = _sha(p.read_bytes())
        records.append(rec)
        files.append({"path": rec["registry_path"], "sha256": rec["registry_sha256"]})
        if sleep_s:
            time.sleep(sleep_s)
    raw_files = sorted({(path, sha) for rec in records for sha, path in rec["raw_evidence_files"].items()})
    total = sum(len(r["per_signal"]) for r in records)
    surviving = sum(r["surviving_signals"] for r in records)
    eliminated = sum(r["eliminated_signals"] for r in records)
    unresolved = sum(r["unresolved_signals"] for r in records)
    assert total == surviving + eliminated + unresolved == 75, "stage1_signal_accounting_broken"
    reasons = {}
    for r in records:
        for p in r["per_signal"]:
            if p["signal_verdict"] != PASS:
                for v in p["candidate_verdicts"]:
                    key = "%s | %s | %s | %s" % (r["c22_asset"], p["decision_date"], v["venue_instrument_symbol"], v["verdict"])
                    reasons[key] = v["reason"]
    complete_enough = unresolved == 0 or all(
        all(v["verdict"] in (PASS, FAIL_TYPE, FAIL_AFTER, FAIL_ASSET, FAIL_DELISTED, FAIL_ABSENT) for v in p["candidate_verdicts"])
        for r in records for p in r["per_signal"])
    report = {
        "report": "c22_b3_stage1_instrument_existence", "stage": STAGE, "stage_version": STAGE_VERSION, "run_id": run_id,
        "mode": "READ_ONLY_HISTORICAL_INSTRUMENT_EXISTENCE_EVIDENCE_ONLY",
        "not_proven_here": ["shortability", "funding_availability", "borrow_availability", "fill_realism", "liquidity", "spread", "historical_fee", "slippage"],
        "v2_artifact_sha256": DR.V2_FROZEN_SHA256, "short_signals_required": total, "short_assets_required": len(records),
        "surviving_stage1": surviving, "eliminated": eliminated, "unresolved": unresolved,
        "verdict_counts": {v: sum(1 for r in records for p in r["per_signal"] if p["signal_verdict"] == v) for v in VERDICTS},
        "assets": records, "elimination_and_unresolved_reasons": reasons,
        "assets_requiring_second_authoritative_source": {r["c22_asset"]: r["second_source_recommended"] for r in records if r["second_source_recommended"]},
        "raw_evidence_files": [{"path": p, "sha256": s} for p, s in raw_files], "registry_files": files,
        "stage_two_request_ready": bool(complete_enough), "stage_two_started": False,
        "allowed_endpoints": list(ALLOWED_URL_PREFIXES), "candle_window": [CANDLE_WINDOW_START, CANDLE_WINDOW_END],
        "c22_performance_computed": False, "strategy_rules_modified": False, "v2_modified": False, "exports_modified": False,
    }
    return report


def render_markdown(r: dict) -> str:
    L = ["# C22 — B3 Stage One: Historical Instrument-Existence Evidence (run %s)" % r["run_id"], "",
         "Read-only. Proves existence only; NOT shortability, funding, borrow, fills, liquidity, spread, fees or slippage.", "",
         "- Short signals required: %d across %d assets (V2 artifact `%s`)" % (r["short_signals_required"], r["short_assets_required"], r["v2_artifact_sha256"]),
         "- Surviving Stage One: **%d** · eliminated: **%d** · unresolved: **%d**" % (r["surviving_stage1"], r["eliminated"], r["unresolved"]),
         "- Verdict counts: %s" % json.dumps({k: v for k, v in r["verdict_counts"].items() if v}, sort_keys=True),
         "- Stage Two request ready: **%s** · Stage Two started: %s" % (r["stage_two_request_ready"], r["stage_two_started"]), "",
         "## A/B/C/D/E/F — per asset", ""]
    for a in r["assets"]:
        L += ["### %s (risk: %s) — dates %s" % (a["c22_asset"], a["mapping_risk"], ", ".join(a["required_signal_dates"])),
              "", "| candidate | type | base/quote | identity | type ok | existence date | evidence | delisted |", "|---|---|---|---|---|---|---|---|"]
        for c in a["candidates"]:
            L.append("| %s @ %s | %s | %s/%s | %s (%s) | %s | %s | %s | %s |" % (
                c["venue_instrument_symbol"], c["venue"], c["instrument_type"], c["base_asset"], c["quote_or_settlement_asset"],
                "ok" if c["identity_ok"] and not c["identity_collision_unresolved"] else ("COLLISION" if c["identity_collision_unresolved"] else "NO"),
                (c["identity_note"] or "")[:90], c["instrument_type_ok"], c["existence_date"], c["existence_evidence"], c["delisted_date"]))
        L += ["", "| signal date | signal | verdict | passing instruments | candidate verdicts |", "|---|---|---|---|---|"]
        for p in a["per_signal"]:
            L.append("| %s | %s | **%s** | %s | %s |" % (p["decision_date"], p["signal"], p["signal_verdict"], ", ".join(p["passing_instruments"]) or "—",
                                                       "; ".join("%s=%s" % (v["venue_instrument_symbol"], v["verdict"]) for v in p["candidate_verdicts"])))
        if a["second_source_recommended"]:
            L.append("\nSecond authoritative source recommended: %s" % ", ".join(a["second_source_recommended"]))
        L.append("")
    L += ["## G — sources used and hashes", "", "| raw file | sha256 |", "|---|---|"]
    for f in r["raw_evidence_files"]:
        L.append("| %s | `%s` |" % (f["path"], f["sha256"]))
    L += ["", "## K — exact reasons for every non-PASS candidate verdict", ""]
    for k, v in sorted(r["elimination_and_unresolved_reasons"].items()):
        L.append("- %s → %s" % (k, v))
    L += ["", "## L — assets requiring a second authoritative source", ""]
    for k, v in r["assets_requiring_second_authoritative_source"].items():
        L.append("- %s: %s" % (k, ", ".join(v)))
    L += ["", "## M — Stage Two", "", "Stage Two request ready: **%s**. Stage Two NOT started. No performance computed; no rules, V2 or exports modified." % r["stage_two_request_ready"], ""]
    return "\n".join(L) + "\n"


def write_report(r: dict) -> dict:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    base = REPORT_DIR / ("c22_b3_stage1_instrument_existence_%s" % r["run_id"])
    jp, mp = base.with_suffix(".json"), base.with_suffix(".md")
    for p in (jp, mp):
        if p.exists():
            raise Stage1Error("refuse_overwrite_report:%s" % p.name)
    blob = json.dumps(r, indent=2, sort_keys=True, default=str).encode("utf-8") + b"\n"
    tmp = jp.with_suffix(".tmp"); tmp.write_bytes(blob); os.replace(tmp, jp)
    tmp = mp.with_suffix(".tmp"); tmp.write_bytes(render_markdown(r).encode("utf-8")); os.replace(tmp, mp)
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    man = MANIFEST_DIR / ("stage1_run_manifest__%s.json" % r["run_id"])
    man.write_bytes(_canon({"stage": STAGE, "run_id": r["run_id"], "report_json": _rel(jp),
                            "report_sha256": _sha(blob), "raw_evidence_files": r["raw_evidence_files"], "registry_files": r["registry_files"],
                            "note": "STAGE ONE ONLY: this is not an admission manifest; the fee-honest precondition shell must keep failing closed."}))
    return {"report_json": _rel(jp), "report_md": _rel(mp), "report_sha256": _sha(blob), "run_manifest": _rel(man)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", default=None)
    a = ap.parse_args(argv)
    r = run_stage1(run_id=a.run_id)
    w = write_report(r)
    print(json.dumps({"run_id": r["run_id"], "surviving_stage1": r["surviving_stage1"], "eliminated": r["eliminated"],
                      "unresolved": r["unresolved"], "verdict_counts": {k: v for k, v in r["verdict_counts"].items() if v},
                      "stage_two_request_ready": r["stage_two_request_ready"], **w}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
