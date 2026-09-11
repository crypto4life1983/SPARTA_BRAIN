"""Candidate #22 -- B3 STAGE THREE: EXECUTION-INSTRUMENT HISTORICAL OHLC (READ-ONLY; RESEARCH ONLY).

This is EXACTLY the frozen B3 plan's acquisition step 4 ("4_historical_ohlc", authorization batch
C22_EXECUTION_OHLC_FETCH_READY_FOR_HUMAN_AUTHORIZATION, token
HUMAN_DECISION_C22_EXECUTION_OHLC_FETCH_AUTHORIZE): fetch execution-instrument historical daily OHLC
for every instrument that survived steps 1-3 (existence, mapping, funding/borrow availability) and
the Stage Two governance closure (HOME_VENUE_ONLY), from the home venue's official public API,
into the frozen layout ohlc/<asset>/ with the frozen filename convention and .sha256 sidecars,
listed in a manifest with per-file sha256 + coverage. Never overwrites.

Required inputs: sealed Stage Two governance closure (decisive executable signals/instruments),
sealed Stage Two report (instrument identities), sealed no-P&L dry run (per-signal holding windows).
Date coverage requirement (frozen): MIN_ACQUISITION_RANGE_START 2026-06-20 through the forward
horizon (initial 30 days to 2026-08-14, then 15-day extensions, append-only); the current replay
data boundary is the last admitted export (2026-09-09) inside extension #2.

Outputs: raw responses (preserved), canonical normalized OHLC files, per-instrument coverage
records, per-signal coverage outcomes over each signal's dry-run holding window
(PASS_OHLC_COVERAGE / FAIL_OHLC_COVERAGE_GAP / UNRESOLVED_OHLC_SOURCE / NOT_ELIGIBLE_*), a run
manifest, and a sealed report. Failure states are fail-closed; UNRESOLVED never becomes PASS.

Not done here (later frozen steps): 5 fee/tick/lot/minimum rules, 6 liquidity/spread, 7 full
holding-period coverage sign-off, cost arithmetic, admission, performance.
"""
from __future__ import annotations

import argparse
import hashlib
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

import sparta_commander.c22_historical_evidence_acquisition_plan_contract as B3  # noqa: E402
import sparta_commander.c22_forward_exit_data_readiness_contract as FED  # noqa: E402
import tools.c22_b3_stage1_instrument_existence_once as S1  # noqa: E402
import tools.c22_b3_stage2_historical_shortability_once as S2  # noqa: E402

STAGE = "B3_STAGE_THREE_HISTORICAL_OHLC"
STAGE_VERSION = "c22_b3_stage3_v1"
FROZEN_STEP = B3.ACQUISITION_ORDER[3]                                   # "4_historical_ohlc"
FROZEN_BATCH = "C22_EXECUTION_OHLC_FETCH_READY_FOR_HUMAN_AUTHORIZATION"
FROZEN_TOKEN = "HUMAN_DECISION_C22_EXECUTION_OHLC_FETCH_AUTHORIZE"
FROZEN_CATEGORY_PERP = "historical_ohlc"                                # B3.PERP_EVIDENCE_CATEGORIES
FROZEN_CATEGORY_MARGIN = "historical_volume"                            # B3.MARGIN_EVIDENCE_CATEGORIES (pair OHLC+volume)
OHLC_DIR = S1.EVIDENCE_ROOT / "ohlc"
CANONICAL_DIR = S1.EVIDENCE_ROOT / "canonical"
REPORT_DIR = REPO_ROOT / "reports" / "c22_gc_b3_stage3"
DRY_RUN_REPORT = REPO_ROOT / "reports" / "c22_gc_replay_dry_run" / "c22_replay_dry_run_no_pnl.json"
DRY_RUN_SHA256 = "f76f8330f72e454fe507b38ac76c67d5eec8a2417c7faef620330a4c620102ef"
GOVERNANCE_DIR = REPO_ROOT / "reports" / "c22_gc_governance"
_USER_AGENT = "sparta-brain-c22-b3-stage3-readonly/1.0"

RANGE_START = B3.MIN_ACQUISITION_RANGE_START                            # 2026-06-20
REPLAY_BOUNDARY = "2026-09-09"                                          # last admitted export
ALLOWED_URL_PREFIXES = (
    "https://fapi.binance.com/fapi/v1/klines",
    "https://api.bybit.com/v5/market/kline",
    "https://www.okx.com/api/v5/market/history-candles",
    "https://api.gateio.ws/api/v4/futures/usdt/candlesticks",
    "https://futures.kraken.com/api/charts/v1/trade/",
    "https://api-pub.bitfinex.com/v2/candles/",
)

PASS = "PASS_OHLC_COVERAGE"
FAIL_GAP = "FAIL_OHLC_COVERAGE_GAP"
UNRES_SOURCE = "UNRESOLVED_OHLC_SOURCE"
NOT_ELIGIBLE_VENUE = "NOT_ELIGIBLE_EXCLUDED_VENUE_POLICY"
NOT_ELIGIBLE_S1 = "NOT_ELIGIBLE_STAGE_ONE_ELIMINATED"
NOT_ELIGIBLE_S2 = "NOT_ELIGIBLE_STAGE_TWO_NOT_PASSED"
VERDICTS = (PASS, FAIL_GAP, UNRES_SOURCE, NOT_ELIGIBLE_VENUE, NOT_ELIGIBLE_S1, NOT_ELIGIBLE_S2)


class Stage3Error(RuntimeError):
    pass


def _assert_safe_url(url: str) -> None:
    if not isinstance(url, str) or not url.startswith("https://") or not any(url.startswith(p) for p in ALLOWED_URL_PREFIXES):
        raise Stage3Error("refusing non-allowlisted url: %s" % url)
    low = url.lower()
    for frag in S1.FORBIDDEN_URL_FRAGMENTS:
        if frag in low and not (frag == "trade/" and "/charts/v1/trade/" in low):
            raise Stage3Error("refusing url containing forbidden fragment %r" % frag)


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


# --------------------------------------------------------------------------------------------
# inputs
# --------------------------------------------------------------------------------------------
def latest_closure() -> tuple:
    files = sorted(GOVERNANCE_DIR.glob("c22_b3_stage2_governance_closure_*.json"))
    if not files:
        raise Stage3Error("no_stage2_governance_closure_found")
    p = files[-1]
    raw = p.read_bytes()
    man = S1.MANIFEST_DIR / ("stage2_governance_closure_manifest__%s.json" % p.stem.rsplit("_", 1)[1])
    if not man.exists():
        raise Stage3Error("closure_manifest_missing:%s" % man.name)
    expected = json.loads(man.read_bytes().decode("utf-8"))["closure_sha256"]
    if S1._sha(raw) != expected:
        raise Stage3Error("closure_sha_mismatch")
    return json.loads(raw.decode("utf-8")), S1._sha(raw), S1._rel(p)


def load_dry_run() -> dict:
    raw = DRY_RUN_REPORT.read_bytes()
    if S1._sha(raw) != DRY_RUN_SHA256:
        raise Stage3Error("dry_run_report_sha_mismatch")
    return json.loads(raw.decode("utf-8"))


def required_end_date(today: str) -> dict:
    """Frozen forward horizon: initial range then 15-day extensions; the fetch end is the earlier of
    the extension end containing the replay boundary and the last complete UTC day."""
    n, rng = 0, FED.initial_exit_data_range()
    while rng["end"] < REPLAY_BOUNDARY:
        n += 1
        rng = FED.extension_range(n)
    last_complete = (_date.fromisoformat(today) - _td(days=1)).isoformat()
    return {"extension_index": n, "extension_range": rng, "replay_boundary": REPLAY_BOUNDARY,
            "fetch_end": min(rng["end"], last_complete), "required_coverage_end": REPLAY_BOUNDARY}


def signal_windows(dry_run: dict) -> dict:
    """{signal_id: {required_start, required_end, by_profile}} for SHORT records: decision date
    through exit fill date (or the replay boundary when open / unfilled), max across profiles."""
    out: dict = {}
    for prof, pr in dry_run["profiles"].items():
        for rec in pr["records"]:
            if rec["side"] != "SHORT":
                continue
            end = rec["exit_date"] or REPLAY_BOUNDARY
            if rec["lifecycle_status"] == "REJECTED":
                end = max(rec["entry_fill"]["fill_date"] if rec.get("entry_fill") and rec["entry_fill"].get("fill_date") else rec["decision_date"], rec["decision_date"])
            w = out.setdefault(rec["signal_id"], {"symbol": rec["symbol"], "decision_date": rec["decision_date"], "required_start": rec["decision_date"], "required_end": end, "by_profile": {}})
            w["by_profile"][prof] = {"lifecycle_status": rec["lifecycle_status"], "entry_date": rec["entry_date"], "exit_date": rec["exit_date"], "window_end": end}
            w["required_end"] = max(w["required_end"], end)
    return out


# --------------------------------------------------------------------------------------------
# fetchers -> canonical rows [{date, open, high, low, close, volume}]
# --------------------------------------------------------------------------------------------
def _rows_from(list_rows, ts_idx, o, h, l, c, v, ms=True) -> list:
    rows = []
    for r in list_rows or []:
        try:
            d = S1._ms_to_date(r[ts_idx]) if ms else S1._s_to_date(r[ts_idx])
            if d:
                rows.append({"date": d, "open": S2._f(r[o]), "high": S2._f(r[h]), "low": S2._f(r[l]), "close": S2._f(r[c]), "volume": S2._f(r[v])})
        except (IndexError, TypeError):
            continue
    return sorted({r["date"]: r for r in rows}.values(), key=lambda x: x["date"])


def fetch_ohlc(venue: str, inst: str, base: str, start: str, end: str, get: Callable, run_id: str) -> dict:
    metas, rows, ok = [], [], True
    ms_s, ms_e = S1._ms(start), S1._ms(end) + 86_399_000
    if venue == "BINANCE":
        cur = ms_s
        for page in range(4):
            r = get("https://fapi.binance.com/fapi/v1/klines?symbol=%s&interval=1d&startTime=%d&endTime=%d&limit=1000" % (inst, cur, ms_e))
            metas.append(S1.preserve_raw("BINANCE", base, "stage3_usdm_daily_klines_p%02d" % page, r, {"symbol": inst, "interval": "1d", "start": start, "end": end, "page": page}, run_id))
            j = _parse(r)
            if not isinstance(j, list):
                ok = False
                break
            rows += _rows_from(j, 0, 1, 2, 3, 4, 5)
            if len(j) < 1000:
                break
            cur = int(j[-1][0]) + 1
    elif venue == "BYBIT":
        r = get("https://api.bybit.com/v5/market/kline?category=linear&symbol=%s&interval=D&start=%d&end=%d&limit=200" % (inst, ms_s, ms_e))
        metas.append(S1.preserve_raw("BYBIT", base, "stage3_linear_daily_kline", r, {"category": "linear", "symbol": inst, "interval": "D", "start": start, "end": end}, run_id))
        j = _parse(r)
        lst = (j or {}).get("result", {}).get("list", []) if isinstance(j, dict) else None
        ok = lst is not None
        rows = _rows_from(lst, 0, 1, 2, 3, 4, 5)
    elif venue == "OKX":
        after = ms_e + 1
        for page in range(6):
            r = get("https://www.okx.com/api/v5/market/history-candles?instId=%s&bar=1D&after=%d&before=%d&limit=100" % (inst, after, ms_s - 1))
            metas.append(S1.preserve_raw("OKX", base, "stage3_swap_history_candles_p%02d" % page, r, {"instId": inst, "bar": "1D", "start": start, "end": end, "page": page}, run_id))
            j = _parse(r)
            data = (j or {}).get("data", []) if isinstance(j, dict) else None
            if data is None:
                ok = False
                break
            rows += _rows_from(data, 0, 1, 2, 3, 4, 5)
            if len(data) < 100:
                break
            after = min(int(x[0]) for x in data)
    elif venue == "GATE":
        r = get("https://api.gateio.ws/api/v4/futures/usdt/candlesticks?contract=%s&interval=1d&from=%d&to=%d" % (inst, ms_s // 1000, ms_e // 1000))
        metas.append(S1.preserve_raw("GATE", base, "stage3_futures_daily_candlesticks", r, {"contract": inst, "interval": "1d", "from": start, "to": end}, run_id))
        j = _parse(r)
        ok = isinstance(j, list)
        for c in (j if ok else []):
            d = S1._s_to_date(c.get("t"))
            if d:
                rows.append({"date": d, "open": S2._f(c.get("o")), "high": S2._f(c.get("h")), "low": S2._f(c.get("l")), "close": S2._f(c.get("c")), "volume": S2._f(c.get("v"))})
        rows = sorted({r_["date"]: r_ for r_ in rows}.values(), key=lambda x: x["date"])
    elif venue == "KRAKEN_FUTURES":
        r = get("https://futures.kraken.com/api/charts/v1/trade/%s/1d?from=%d&to=%d" % (inst, ms_s // 1000, ms_e // 1000))
        metas.append(S1.preserve_raw("KRAKEN", base, "stage3_futures_daily_chart", r, {"symbol": inst, "resolution": "1d", "from": start, "to": end}, run_id))
        j = _parse(r)
        cs = (j or {}).get("candles") if isinstance(j, dict) else None
        ok = cs is not None
        for c in (cs or []):
            d = S1._ms_to_date(c.get("time"))
            if d:
                rows.append({"date": d, "open": S2._f(c.get("open")), "high": S2._f(c.get("high")), "low": S2._f(c.get("low")), "close": S2._f(c.get("close")), "volume": S2._f(c.get("volume"))})
        rows = sorted({r_["date"]: r_ for r_ in rows}.values(), key=lambda x: x["date"])
    elif venue == "BITFINEX":
        r = get("https://api-pub.bitfinex.com/v2/candles/trade:1D:%s/hist?start=%d&end=%d&limit=10000&sort=1" % (inst, ms_s, ms_e))
        metas.append(S1.preserve_raw("BITFINEX", base, "stage3_pair_daily_candles", r, {"pair": inst, "tf": "1D", "start": start, "end": end}, run_id))
        j = _parse(r)
        ok = isinstance(j, list)
        rows = _rows_from(j, 0, 1, 3, 4, 2, 5) if ok else []          # [MTS, OPEN, CLOSE, HIGH, LOW, VOLUME]
    else:
        raise Stage3Error("no_stage3_fetcher_for_venue:%s" % venue)
    return {"rows": rows, "source_ok": ok, "metas": metas}


def write_canonical(venue: str, asset: str, base: str, inst: str, rows: list, start: str, end: str, run_id: str, metas: list) -> dict:
    d = OHLC_DIR / base
    d.mkdir(parents=True, exist_ok=True)
    p = d / ("%s__%s__historical_ohlc__%s_%s__%s.json" % (venue, base, start, end, run_id))
    if p.exists():
        raise Stage3Error("refuse_overwrite_canonical:%s" % p.name)
    payload = {"stage": STAGE, "frozen_step": FROZEN_STEP, "c22_asset": asset, "venue": venue, "instrument": inst, "timeframe": "1d",
               "range_requested": [start, end], "rows": rows, "row_count": len(rows),
               "first_date": rows[0]["date"] if rows else None, "last_date": rows[-1]["date"] if rows else None,
               "source_raw_sha256": [m["raw_sha256"] for m in metas], "source_endpoints": sorted({m["endpoint"] for m in metas}),
               "provenance_note": "rows normalised from the preserved raw responses listed in source_raw_sha256; no interpolation; no fill"}
    blob = S1._canon(payload)
    tmp = p.with_suffix(".tmp"); tmp.write_bytes(blob); os.replace(tmp, p)
    p.with_suffix(".json.sha256").write_text(S1._sha(blob) + "\n", encoding="utf-8")
    return {"path": S1._rel(p), "sha256": S1._sha(blob), "row_count": len(rows), "first_date": payload["first_date"], "last_date": payload["last_date"]}


def coverage(rows: list, start: str, end: str) -> dict:
    have = {r["date"]: r for r in rows}
    days, d = [], _date.fromisoformat(start)
    while d <= _date.fromisoformat(end):
        days.append(d.isoformat())
        d += _td(days=1)
    missing = [x for x in days if x not in have]
    malformed = [x for x in days if x in have and any(have[x][k] is None for k in ("open", "high", "low", "close"))]
    return {"required_start": start, "required_end": end, "required_days": len(days), "present_days": len(days) - len(missing),
            "missing_days": missing, "malformed_days": malformed, "complete": not missing and not malformed}


# --------------------------------------------------------------------------------------------
def run_stage3(get: Callable = http_get, run_id: str | None = None, today: str | None = None, sleep_s: float = 0.25,
               closure: dict | None = None, closure_sha: str | None = None, closure_path: str | None = None,
               stage2: dict | None = None, dry_run: dict | None = None) -> dict:
    run_id = run_id or _dt.now(_tz.utc).strftime("%Y%m%dT%H%M%SZ")
    today = today or _dt.now(_tz.utc).date().isoformat()
    if closure is None:
        closure, closure_sha, closure_path = latest_closure()
    if stage2 is None:
        import tools.c22_b3_stage2_governance_closure_once as GC
        stage2 = GC.load_stage2_of_record()
    if dry_run is None:
        dry_run = load_dry_run()
    horizon = required_end_date(today)
    fetch_end = horizon["fetch_end"]
    windows = signal_windows(dry_run)
    s2_assets = {a["c22_asset"]: a for a in stage2["assets"]}
    # eligible instruments: decisive executable signals per closure, home-venue passing instrument per Stage Two
    eligible: dict = {}
    for p in closure["per_signal"]:
        if p["decisive_execution_status"] == S2.PASS:
            eligible.setdefault(p["c22_asset"], set()).update(p["instruments"])
    instruments, inst_cov = [], {}
    for asset in sorted(eligible):
        base = asset.split(":")[1]
        base = base[:-4] if base.endswith("USDT") else base[:-3]
        cands = {c["venue_instrument_symbol"]: c for c in s2_assets[asset]["candidates"]}
        for inst in sorted(eligible[asset]):
            c = cands[inst]
            ev = fetch_ohlc(c["venue"], inst, base, RANGE_START, fetch_end, get, run_id)
            can = write_canonical(c["venue"], asset, base, inst, ev["rows"], RANGE_START, fetch_end, run_id, ev["metas"]) if ev["source_ok"] else None
            cov = coverage(ev["rows"], RANGE_START, horizon["required_coverage_end"]) if ev["source_ok"] else None
            rec = {"c22_asset": asset, "venue": c["venue"], "instrument": inst, "execution_path": c["execution_path"],
                   "frozen_category": FROZEN_CATEGORY_PERP if c["execution_path"] == S2.PATH_DERIVATIVE else FROZEN_CATEGORY_MARGIN,
                   "source_ok": ev["source_ok"], "canonical_file": can, "coverage_full_range": cov,
                   "raw_sources": [{"endpoint": m["endpoint"], "query_params": m["query_params"], "raw_sha256": m["raw_sha256"], "raw_path": m["raw_path"], "http_status": m["http_status"]} for m in ev["metas"]],
                   "rows": ev["rows"]}
            instruments.append(rec)
            inst_cov[(asset, inst)] = rec
            if sleep_s:
                time.sleep(sleep_s)
    # per-signal outcomes (all 75 frozen shorts)
    per_signal = []
    for p in closure["per_signal"]:
        sid = "%s|%s|%s" % (p["decision_date"], p["c22_asset"], p["signal"])
        st = p["decisive_execution_status"]
        base_rec = {"signal_id": sid, "c22_asset": p["c22_asset"], "decision_date": p["decision_date"], "signal": p["signal"],
                    "decisive_execution_status": st, "instrument": None, "required_window": None, "verdict": None, "reason": None}
        if st == "EXCLUDED_VENUE_POLICY":
            base_rec.update(verdict=NOT_ELIGIBLE_VENUE, reason="excluded by HOME_VENUE_ONLY governance decision")
        elif st == "ELIMINATED_STAGE_ONE_PRESERVED":
            base_rec.update(verdict=NOT_ELIGIBLE_S1, reason="Stage One elimination preserved")
        elif st != S2.PASS:
            base_rec.update(verdict=NOT_ELIGIBLE_S2, reason="Stage Two status %s" % st)
        else:
            w = windows.get(sid)
            inst = sorted(p["instruments"])[0] if p["instruments"] else None
            rec = inst_cov.get((p["c22_asset"], inst)) if inst else None
            base_rec["instrument"] = inst
            if w is None:
                base_rec.update(verdict=UNRES_SOURCE, reason="no dry-run holding window for signal")
            elif rec is None or not rec["source_ok"]:
                base_rec.update(verdict=UNRES_SOURCE, reason="official OHLC source unavailable for %s" % inst)
            else:
                cov = coverage(rec["rows"], w["required_start"], w["required_end"])
                base_rec["required_window"] = {"start": w["required_start"], "end": w["required_end"], "by_profile": w["by_profile"]}
                base_rec["coverage"] = cov
                if cov["complete"]:
                    base_rec.update(verdict=PASS, reason="official daily OHLC present for every day %s..%s (%d days)" % (w["required_start"], w["required_end"], cov["required_days"]))
                else:
                    base_rec.update(verdict=FAIL_GAP, reason="missing %s malformed %s" % (cov["missing_days"][:10], cov["malformed_days"][:10]))
        per_signal.append(base_rec)
    counts = {v: sum(1 for x in per_signal if x["verdict"] == v) for v in VERDICTS}
    assert sum(counts.values()) == len(per_signal) == 75, "stage3_accounting_broken"
    longs = 88 - 75
    funnel = {"frozen_v2_signals": 88, "frozen_long_signals_no_execution_evidence_yet": longs, "frozen_short_signals": 75,
              "stage1_survivors": closure["final_stage_two_funnel"]["stage1_survivors"],
              "stage2_decisive_executable": closure["final_stage_two_funnel"]["decisive_executable_short_signals_after_stage_two"],
              "excluded_venue_policy": closure["final_stage_two_funnel"]["excluded_venue_policy"],
              "stage1_eliminated_preserved": closure["final_stage_two_funnel"]["eliminated_stage_one_preserved"],
              "stage3_ohlc_coverage_pass": counts[PASS], "stage3_fail_gap": counts[FAIL_GAP], "stage3_unresolved": counts[UNRES_SOURCE],
              "steps_remaining_before_admission": ["5_fee_tick_lot_minimum_rules", "6_liquidity_and_spread_evidence", "7_full_holding_period_coverage", "admission_review"],
              "fee_honestly_replayable_trades": 0}
    next_step_ok = counts[UNRES_SOURCE] == 0 and counts[PASS] > 0
    return {"report": "c22_b3_stage3_historical_ohlc", "stage": STAGE, "stage_version": STAGE_VERSION, "run_id": run_id, "today_utc": today,
            "mode": "READ_ONLY_EXECUTION_INSTRUMENT_HISTORICAL_OHLC_ACQUISITION",
            "frozen_contract": {"module": "sparta_commander.c22_historical_evidence_acquisition_plan_contract", "acquisition_step": FROZEN_STEP,
                                "authorization_batch": FROZEN_BATCH, "human_token_name": FROZEN_TOKEN,
                                "authorization_basis": "operator message 2026-09-11 authorizing Stage Three exactly as frozen; no approval record fabricated",
                                "evidence_categories": {"perp": FROZEN_CATEGORY_PERP, "margin": FROZEN_CATEGORY_MARGIN},
                                "layout": B3.PROPOSED_LAYOUT["ohlc"], "filename_convention": B3.FILENAME_CONVENTION,
                                "decisive_min_tier": B3.DECISIVE_MIN_TIER, "source_tier_used": B3.SOURCE_HIERARCHY[0],
                                "early_fail_close_steps_already_applied": list(B3.EARLY_FAIL_CLOSE_STEPS.keys()),
                                "steps_not_executed_here": [s for s in B3.ACQUISITION_ORDER if s != FROZEN_STEP]},
            "inputs": {"stage2_governance_closure": {"path": closure_path, "sha256": closure_sha},
                       "stage2_report": {"run": closure["referenced_sealed_evidence"]["stage2_report_run"], "sha256": closure["referenced_sealed_evidence"]["stage2_report_sha256"]},
                       "dry_run_report": {"sha256": DRY_RUN_SHA256}, "v2_artifact_sha256": closure["referenced_sealed_evidence"]["v2_artifact_sha256"]},
            "horizon": horizon, "range_fetched": [RANGE_START, fetch_end],
            "instruments": [{k: v for k, v in r.items() if k != "rows"} for r in instruments],
            "per_signal": per_signal, "verdict_counts": counts, "funnel": funnel,
            "raw_evidence_files": sorted({(s["raw_path"], s["raw_sha256"]) for r in instruments for s in r["raw_sources"]}),
            "canonical_files": [r["canonical_file"] for r in instruments if r["canonical_file"]],
            "next_frozen_step": B3.ACQUISITION_ORDER[4], "next_step_request_permitted_by_spec": bool(next_step_ok),
            "next_step_started": False, "c22_performance_computed": False, "cost_arithmetic_performed": False,
            "strategy_rules_modified": False, "v2_modified": False, "exports_modified": False, "admission_state_changed": False}


def render_markdown(r: dict) -> str:
    f, fc = r["funnel"], r["frozen_contract"]
    L = ["# C22 — B3 Stage Three: Execution-Instrument Historical OHLC (run %s)" % r["run_id"], "",
         "Frozen step **%s** (batch %s, token name %s). Read-only. No performance, no cost arithmetic, no admission change." % (fc["acquisition_step"], fc["authorization_batch"], fc["human_token_name"]), "",
         "- Inputs: closure `%s` (sha `%s`); Stage Two report sha `%s`; dry run sha `%s`; V2 `%s`" % (r["inputs"]["stage2_governance_closure"]["path"], r["inputs"]["stage2_governance_closure"]["sha256"], r["inputs"]["stage2_report"]["sha256"], r["inputs"]["dry_run_report"]["sha256"], r["inputs"]["v2_artifact_sha256"]),
         "- Range fetched %s..%s · required coverage end %s · extension #%d (%s..%s)" % (r["range_fetched"][0], r["range_fetched"][1], r["horizon"]["required_coverage_end"], r["horizon"]["extension_index"], r["horizon"]["extension_range"]["start"], r["horizon"]["extension_range"]["end"]),
         "- Verdicts: %s" % json.dumps({k: v for k, v in r["verdict_counts"].items() if v}, sort_keys=True),
         "- Next frozen step: %s · request permitted by spec: **%s** · started: %s" % (r["next_frozen_step"], r["next_step_request_permitted_by_spec"], r["next_step_started"]), "",
         "## Instruments", "", "| asset | instrument | path | category | rows | first | last | full-range coverage | canonical sha256 |", "|---|---|---|---|---|---|---|---|---|"]
    for i in r["instruments"]:
        c, cov = i["canonical_file"] or {}, i["coverage_full_range"] or {}
        L.append("| %s | %s @ %s | %s | %s | %s | %s | %s | %s/%s (missing %d) | `%s` |" % (i["c22_asset"], i["instrument"], i["venue"], i["execution_path"], i["frozen_category"], c.get("row_count"), c.get("first_date"), c.get("last_date"), cov.get("present_days"), cov.get("required_days"), len(cov.get("missing_days") or []), (c.get("sha256") or "")[:16]))
    L += ["", "## Per-signal outcomes", "", "| signal | status after Stage Two | instrument | window | **Stage Three** | reason |", "|---|---|---|---|---|---|"]
    for p in r["per_signal"]:
        w = p["required_window"]
        L.append("| %s | %s | %s | %s | **%s** | %s |" % (p["signal_id"], p["decisive_execution_status"], p["instrument"] or "—", ("%s..%s" % (w["start"], w["end"])) if w else "—", p["verdict"], (p["reason"] or "")[:100]))
    L += ["", "## Funnel", "", "| item | value |", "|---|---|"]
    for k, v in f.items():
        L.append("| %s | %s |" % (k, v))
    L += ["", "## Raw sources", "", "| raw file | sha256 |", "|---|---|"]
    for path, sha in r["raw_evidence_files"]:
        L.append("| %s | `%s` |" % (path, sha))
    return "\n".join(L) + "\n"


def write_report(r: dict) -> dict:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    base = REPORT_DIR / ("c22_b3_stage3_historical_ohlc_%s" % r["run_id"])
    jp, mp = base.with_suffix(".json"), base.with_suffix(".md")
    for p in (jp, mp):
        if p.exists():
            raise Stage3Error("refuse_overwrite_report:%s" % p.name)
    blob = json.dumps(r, indent=2, sort_keys=True, default=str).encode("utf-8") + b"\n"
    tmp = jp.with_suffix(".tmp"); tmp.write_bytes(blob); os.replace(tmp, jp)
    tmp = mp.with_suffix(".tmp"); tmp.write_bytes(render_markdown(r).encode("utf-8")); os.replace(tmp, mp)
    S1.MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    man = S1.MANIFEST_DIR / ("stage3_run_manifest__%s.json" % r["run_id"])
    man.write_bytes(S1._canon({"stage": STAGE, "frozen_step": FROZEN_STEP, "run_id": r["run_id"], "report_json": S1._rel(jp), "report_sha256": S1._sha(blob),
                               "raw_evidence_files": r["raw_evidence_files"], "canonical_files": r["canonical_files"],
                               "coverage": {i["instrument"]: i["coverage_full_range"] for i in r["instruments"]},
                               "note": "STAGE THREE ONLY (4_historical_ohlc): not an admission manifest; the fee-honest precondition shell must keep failing closed."}))
    return {"report_json": S1._rel(jp), "report_md": S1._rel(mp), "report_sha256": S1._sha(blob), "run_manifest": S1._rel(man)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", default=None)
    a = ap.parse_args(argv)
    r = run_stage3(run_id=a.run_id)
    w = write_report(r)
    print(json.dumps({"run_id": r["run_id"], "verdict_counts": {k: v for k, v in r["verdict_counts"].items() if v}, "funnel": r["funnel"],
                      "range_fetched": r["range_fetched"], "next_step_request_permitted_by_spec": r["next_step_request_permitted_by_spec"], **w}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
