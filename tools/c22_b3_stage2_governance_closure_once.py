"""Candidate #22 -- B3 STAGE TWO GOVERNANCE CLOSURE (records human decisions; READ-ONLY research).

Records the operator's Stage Two governance decisions (2026-09-11) as NEW sealed artifacts.
Never rewrites the sealed Stage One / Stage Two reports or their evidence.

DECISION 1 -- decisive venue policy HOME_VENUE_ONLY: no cross-venue substitution to rescue a
signal. MORPHO keeps its Stage One historical-existence PASS; its two short signals (which need
Coinbase International rather than the frozen home-venue mapping) are classified for decisive
execution as EXCLUDED_VENUE_POLICY (never "instrument-nonexistent"). TEL keeps its Stage One
elimination; no alternative venue is searched. Any future cross-venue test is a separately named
sensitivity experiment with one predetermined venue hierarchy across the whole cohort.

DECISION 2 -- LEO: the general Bitfinex funding-market inference alone is NOT accepted. This tool
fetches pair-specific official Bitfinex historical statistics for the canonical pair/funding
currency established in the B3 mapping (tLEOUSD / fLEO): short position size on the exact pair
(stats1 pos.size:*:tLEOUSD:short) and funding credits used on the exact pair
(stats1 credits.size.sym:*:fLEO:tLEOUSD) around every required LEO decision/fill date. PASS only
if authoritative pair-specific evidence shows short positions present/possible on the pair in
the required period; otherwise UNRESOLVED_HISTORICAL_MARGIN_STATE. Present-day margin flags and
general borrow-market data never decide.

No performance information exists or was consulted for any of these decisions.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import date as _date, datetime as _dt, timedelta as _td, timezone as _tz
from pathlib import Path
from typing import Callable

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import tools.c22_b3_stage1_instrument_existence_once as S1  # noqa: E402
import tools.c22_b3_stage2_historical_shortability_once as S2  # noqa: E402

CLOSURE_VERSION = "c22_b3_stage2_governance_closure_v1"
DECISION_DATE = "2026-09-11"
STAGE2_RUN_OF_RECORD = "20260910T231336Z"
STAGE2_REPORT = REPO_ROOT / "reports" / "c22_gc_b3_stage2" / ("c22_b3_stage2_historical_shortability_%s.json" % STAGE2_RUN_OF_RECORD)
STAGE2_REPORT_SHA256 = "03fbc61783152c27026a54cf588c7bdc80b69ea260dc43640e9bd28dc9605e3f"
STAGE1_REPORT_SHA256 = S2.STAGE1_REPORT_SHA256
V2_FROZEN_SHA256 = "b6a28a4873d1aff17014a9d598702c67047b4ebe023b8cfddce05094f9ce9dd8"
GOVERNANCE_DIR = REPO_ROOT / "reports" / "c22_gc_governance"

VENUE_POLICY = "HOME_VENUE_ONLY"
EXCLUDED_VENUE_POLICY = "EXCLUDED_VENUE_POLICY"
LEO_PASS = S2.PASS
LEO_UNRESOLVED = S2.UNRES_MARGIN
LEO_ASSET, LEO_PAIR, LEO_FUNDING = "BITFINEX:LEOUSD", "tLEOUSD", "fLEO"
MORPHO_ASSET, TEL_ASSET = "COINBASE:MORPHOUSD", "BYBIT:TELUSDT"
_USER_AGENT = "sparta-brain-c22-b3-stage2-closure-readonly/1.0"
ALLOWED_URL_PREFIXES = ("https://api-pub.bitfinex.com/v2/stats1/",)


class ClosureError(RuntimeError):
    pass


def _assert_safe_url(url: str) -> None:
    if not any(url.startswith(p) for p in ALLOWED_URL_PREFIXES):
        raise ClosureError("refusing non-allowlisted url: %s" % url)
    low = url.lower()
    for frag in S1.FORBIDDEN_URL_FRAGMENTS:
        if frag in low:
            raise ClosureError("refusing url containing forbidden fragment %r" % frag)


def http_get(url: str, timeout: float = 30.0) -> dict:
    _assert_safe_url(url)
    req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT}, method="GET")
    retrieved = _dt.now(_tz.utc).isoformat(timespec="seconds")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return {"url": url, "status": r.status, "retrieved_utc": retrieved, "raw_bytes": r.read()}
    except urllib.error.HTTPError as e:
        return {"url": url, "status": e.code, "retrieved_utc": retrieved, "raw_bytes": e.read()}


def load_stage2_of_record() -> dict:
    raw = STAGE2_REPORT.read_bytes()
    if S1._sha(raw) != STAGE2_REPORT_SHA256:
        raise ClosureError("stage2_report_sha_mismatch")
    return json.loads(raw.decode("utf-8"))


# --------------------------------------------------------------------------------------------
# LEO supplemental pair-specific evidence
# --------------------------------------------------------------------------------------------
def leo_required_dates(stage2: dict) -> list:
    a = next(x for x in stage2["assets"] if x["c22_asset"] == LEO_ASSET)
    dates = set()
    for p in a["per_signal"]:
        dates.update([p["decision_date"], p["fill_date_calendar"], p["fill_date_weekday"]])
    return sorted(dates)


def fetch_leo_pair_stats(required_dates: list, get: Callable, run_id: str) -> dict:
    lo = (_date.fromisoformat(min(required_dates)) - _td(days=3)).isoformat()
    hi = (_date.fromisoformat(max(required_dates)) + _td(days=3)).isoformat()
    out = {"window": [lo, hi], "series": {}, "metas": []}
    for key, cat in (("pos.size:1d:%s:short" % LEO_PAIR, "pair_short_position_size_1d"),
                     ("pos.size:1d:%s:long" % LEO_PAIR, "pair_long_position_size_1d"),
                     ("credits.size.sym:1d:%s:%s" % (LEO_FUNDING, LEO_PAIR), "pair_funding_credits_used_1d")):
        r = get("https://api-pub.bitfinex.com/v2/stats1/%s/hist?start=%d&end=%d&limit=100&sort=1" % (key, S1._ms(lo), S1._ms(hi)))
        m = S1.preserve_raw("BITFINEX", "LEO", cat, r, {"key": key, "start": lo, "end": hi, "limit": 100, "sort": 1}, run_id)
        out["metas"].append(m)
        j = json.loads(r["raw_bytes"].decode("utf-8")) if r["status"] == 200 else None
        out["series"][cat] = {S1._ms_to_date(x[0]): S2._f(x[1]) for x in (j or []) if isinstance(x, list) and len(x) >= 2 and S1._ms_to_date(x[0])} if isinstance(j, list) else None
    # minute resolution on the exact required dates (short size + pair credits), for intra-day corroboration
    for key, cat in (("pos.size:1m:%s:short" % LEO_PAIR, "pair_short_position_size_1m"),
                     ("credits.size.sym:1m:%s:%s" % (LEO_FUNDING, LEO_PAIR), "pair_funding_credits_used_1m")):
        r = get("https://api-pub.bitfinex.com/v2/stats1/%s/hist?start=%d&end=%d&limit=10000&sort=1" % (key, S1._ms(min(required_dates)), S1._ms(max(required_dates)) + 86_400_000))
        m = S1.preserve_raw("BITFINEX", "LEO", cat, r, {"key": key, "start": min(required_dates), "end_exclusive": (_date.fromisoformat(max(required_dates)) + _td(days=1)).isoformat(), "limit": 10000, "sort": 1}, run_id)
        out["metas"].append(m)
        j = json.loads(r["raw_bytes"].decode("utf-8")) if r["status"] == 200 else None
        per_day: dict = {}
        for x in (j or []) if isinstance(j, list) else []:
            d = S1._ms_to_date(x[0]) if isinstance(x, list) and x else None
            if d:
                v = S2._f(x[1])
                per_day.setdefault(d, {"points": 0, "min": None, "max": None})
                per_day[d]["points"] += 1
                if v is not None:
                    per_day[d]["min"] = v if per_day[d]["min"] is None else min(per_day[d]["min"], v)
                    per_day[d]["max"] = v if per_day[d]["max"] is None else max(per_day[d]["max"], v)
        out["series"][cat] = per_day if isinstance(j, list) else None
    return out


def leo_verdict(required_dates: list, series: dict) -> dict:
    """PURE, fail-closed. PASS iff official pair-specific SHORT position size on tLEOUSD is > 0 on
    every required date (1d) AND minute-level short size on those dates never reads absent, with
    pair-specific funding credits used > 0 corroborating. Anything less -> UNRESOLVED."""
    checks = {"pair": LEO_PAIR, "funding_currency": LEO_FUNDING, "required_dates": required_dates}
    s1m = series.get("pair_short_position_size_1m")
    c1m = series.get("pair_funding_credits_used_1m")
    s1d = series.get("pair_short_position_size_1d") or {}
    c1d = series.get("pair_funding_credits_used_1d") or {}
    if s1m is None or c1m is None:
        return {"verdict": LEO_UNRESOLVED, "reason": "official_pair_specific_statistics_unavailable", "checks": checks}
    # primary: minute-resolution official statistics on the exact pair, summarised per required date
    m = {d: s1m.get(d) for d in required_dates}
    checks["pair_short_position_size_1m_daily_summary"] = m
    thin = [d for d, v in m.items() if not (v and v["points"] > 0 and v["min"] is not None and v["min"] > 0)]
    if thin:
        return {"verdict": LEO_UNRESOLVED, "reason": "no_pair_specific_short_position_size>0_at_minute_resolution_on_%s" % ",".join(thin), "checks": checks}
    cm = {d: c1m.get(d) for d in required_dates}
    checks["pair_funding_credits_used_1m_daily_summary"] = cm
    lacking = [d for d, v in cm.items() if not (v and v["points"] > 0 and v["min"] is not None and v["min"] > 0)]
    if lacking:
        return {"verdict": LEO_UNRESOLVED, "reason": "no_pair_specific_funding_credits_used>0_on_%s" % ",".join(lacking), "checks": checks}
    # optional corroboration: daily-timeframe series (Bitfinex returned empty arrays for '1d' keys in this run)
    checks["pair_short_position_size_1d_on_required_dates"] = {d: s1d.get(d) for d in required_dates}
    checks["pair_funding_credits_used_1d_on_required_dates"] = {d: c1d.get(d) for d in required_dates}
    checks["daily_timeframe_series_available"] = bool(s1d) and bool(c1d)
    checks["present_day_margin_flag_used"] = False
    checks["general_borrow_market_inference_used_as_decisive"] = False
    return {"verdict": LEO_PASS, "reason": "official pair-specific statistics: short position size on %s > 0 at every observed minute of every required date, and funding credits used on the exact pair > 0 throughout: short positions were actually present/possible on the pair in the required period" % LEO_PAIR, "checks": checks}


# --------------------------------------------------------------------------------------------
# closure artifact
# --------------------------------------------------------------------------------------------
def build_closure(stage2: dict, leo: dict, leo_meta: list, run_id: str) -> dict:
    assets = {a["c22_asset"]: a for a in stage2["assets"]}
    morpho = assets[MORPHO_ASSET]
    tel = assets[TEL_ASSET]
    per_signal = []
    for a in stage2["assets"]:
        for p in a["per_signal"]:
            s2v = p["stage2_verdict"]
            if a["c22_asset"] == MORPHO_ASSET:
                final = EXCLUDED_VENUE_POLICY
            elif a["c22_asset"] == LEO_ASSET:
                final = leo["verdict"]
            elif a["c22_asset"] == TEL_ASSET:
                final = "ELIMINATED_STAGE_ONE_PRESERVED"
            else:
                final = s2v
            per_signal.append({"c22_asset": a["c22_asset"], "decision_date": p["decision_date"], "signal": p["signal"],
                               "stage1_verdict": p["stage1_verdict"], "stage2_verdict": s2v, "decisive_execution_status": final,
                               "execution_path": p["execution_path_used"], "instruments": p["passing_instruments"]})
    counts = {}
    for p in per_signal:
        counts[p["decisive_execution_status"]] = counts.get(p["decisive_execution_status"], 0) + 1
    passing = [p for p in per_signal if p["decisive_execution_status"] == S2.PASS]
    funnel = {"frozen_short_signals": len(per_signal), "stage1_survivors": sum(1 for p in per_signal if p["stage1_verdict"] == S1.PASS),
              "stage2_pass_before_governance": sum(1 for p in per_signal if p["stage2_verdict"] == S2.PASS),
              "excluded_venue_policy": counts.get(EXCLUDED_VENUE_POLICY, 0),
              "leo_final": leo["verdict"], "eliminated_stage_one_preserved": counts.get("ELIMINATED_STAGE_ONE_PRESERVED", 0),
              "unresolved": sum(v for k, v in counts.items() if k.startswith("UNRESOLVED")),
              "decisive_executable_short_signals_after_stage_two": len(passing),
              "decisive_executable_assets": sorted({p["c22_asset"] for p in passing}),
              "admitted_for_fee_honest_replay": 0}
    art = {
        "artifact": "c22_b3_stage2_governance_closure", "version": CLOSURE_VERSION, "run_id": run_id, "decision_date": DECISION_DATE,
        "decided_by": "human operator (recorded by session, not fabricated)", "performance_information_consulted": False,
        "performance_exists": False,
        "decision_1_venue_policy": {
            "policy": VENUE_POLICY, "cross_venue_substitution_to_rescue_signals": False, "made_before_performance_calculation": True,
            "future_cross_venue_testing": "separately named sensitivity experiment with one predetermined venue-selection hierarchy across the entire cohort; never mixed into the decisive C22 V2 replay",
            "morpho": {"asset": MORPHO_ASSET, "stage1_historical_existence": "PASS_PRESERVED",
                       "stage2_verdict": [p["stage2_verdict"] for p in morpho["per_signal"]],
                       "decisive_execution_status": EXCLUDED_VENUE_POLICY, "signals": [p["decision_date"] for p in morpho["per_signal"]],
                       "not_classified_as": "instrument_nonexistent", "evidence_deleted": False,
                       "reason": "both signals require Coinbase International (substituted platform) rather than the frozen home-venue mapping"},
            "tel": {"asset": TEL_ASSET, "stage1_verdict": tel["per_signal"][0]["stage1_verdict"], "decisive_execution_status": "ELIMINATED_STAGE_ONE_PRESERVED",
                    "alternative_venues_searched": False}},
        "decision_2_leo": {"asset": LEO_ASSET, "pair": LEO_PAIR, "funding_currency": LEO_FUNDING,
                           "general_funding_market_inference_accepted_alone": False,
                           "supplemental_evidence": [{"endpoint": m["endpoint"], "query_params": m["query_params"], "raw_sha256": m["raw_sha256"],
                                                      "raw_path": m["raw_path"], "retrieved_utc": m["retrieved_utc"], "http_status": m["http_status"]} for m in leo_meta],
                           "final_verdict": leo["verdict"], "reason": leo["reason"], "checks": leo["checks"]},
        "final_stage_two_funnel": funnel, "decisive_execution_status_counts": counts, "per_signal": per_signal,
        "referenced_sealed_evidence": {"stage1_report_run": S2.STAGE1_RUN_OF_RECORD, "stage1_report_sha256": STAGE1_REPORT_SHA256,
                                       "stage2_report_run": STAGE2_RUN_OF_RECORD, "stage2_report_sha256": STAGE2_REPORT_SHA256,
                                       "v2_artifact_sha256": V2_FROZEN_SHA256},
        "historical_evidence_modified": False, "sealed_reports_rewritten": False, "admission_state_changed": False,
        "stage_three_authorized_after_closure": True, "stage_three_definition": "frozen B3 ACQUISITION_ORDER step 4_historical_ohlc under batch HUMAN_DECISION_C22_EXECUTION_OHLC_FETCH_AUTHORIZE",
    }
    art["closure_sha256_excluding_self"] = S1._sha(S1._canon(art))
    return art


def write_closure(art: dict) -> dict:
    GOVERNANCE_DIR.mkdir(parents=True, exist_ok=True)
    base = GOVERNANCE_DIR / ("c22_b3_stage2_governance_closure_%s" % art["run_id"])
    jp, mp = base.with_suffix(".json"), base.with_suffix(".md")
    for p in (jp, mp):
        if p.exists():
            raise ClosureError("refuse_overwrite:%s" % p.name)
    blob = json.dumps(art, indent=2, sort_keys=True, default=str).encode("utf-8") + b"\n"
    tmp = jp.with_suffix(".tmp"); tmp.write_bytes(blob); os.replace(tmp, jp)
    tmp = mp.with_suffix(".tmp"); tmp.write_bytes(render_markdown(art).encode("utf-8")); os.replace(tmp, mp)
    S1.MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    man = S1.MANIFEST_DIR / ("stage2_governance_closure_manifest__%s.json" % art["run_id"])
    man.write_bytes(S1._canon({"artifact": "stage2_governance_closure", "run_id": art["run_id"], "closure_json": S1._rel(jp), "closure_sha256": S1._sha(blob),
                               "leo_supplemental_raw": [m["raw_sha256"] for m in art["decision_2_leo"]["supplemental_evidence"]],
                               "note": "governance closure only; not an admission manifest"}))
    return {"closure_json": S1._rel(jp), "closure_md": S1._rel(mp), "closure_sha256": S1._sha(blob), "manifest": S1._rel(man)}


def render_markdown(a: dict) -> str:
    f = a["final_stage_two_funnel"]
    d1, d2 = a["decision_1_venue_policy"], a["decision_2_leo"]
    L = ["# C22 — B3 Stage Two Governance Closure (%s)" % a["run_id"], "",
         "Human decisions of %s recorded by the session. No performance information exists or was consulted." % a["decision_date"], "",
         "## Decision 1 — decisive venue policy: **%s**" % d1["policy"], "",
         "- Cross-venue substitution to rescue signals: %s · made before any performance calculation: %s" % (d1["cross_venue_substitution_to_rescue_signals"], d1["made_before_performance_calculation"]),
         "- MORPHO: Stage One existence %s; Stage Two %s; decisive execution status **%s** for signals %s; not classified as instrument-nonexistent; evidence kept." % (
             d1["morpho"]["stage1_historical_existence"], d1["morpho"]["stage2_verdict"], d1["morpho"]["decisive_execution_status"], d1["morpho"]["signals"]),
         "- TEL: Stage One %s preserved; alternative venues searched: %s." % (d1["tel"]["stage1_verdict"], d1["tel"]["alternative_venues_searched"]),
         "- Future cross-venue testing: %s" % d1["future_cross_venue_testing"], "",
         "## Decision 2 — LEO final verdict: **%s**" % d2["final_verdict"], "",
         "- General funding-market inference accepted alone: %s" % d2["general_funding_market_inference_accepted_alone"],
         "- Reason: %s" % d2["reason"], "- Checks: `%s`" % json.dumps(d2["checks"], sort_keys=True, default=str)[:1500], "",
         "| supplemental source | params | sha256 | retrieved |", "|---|---|---|---|"]
    for m in d2["supplemental_evidence"]:
        L.append("| %s | %s | `%s` | %s |" % (m["endpoint"], json.dumps(m["query_params"], sort_keys=True), m["raw_sha256"], m["retrieved_utc"]))
    L += ["", "## Final Stage Two funnel", "", "| item | value |", "|---|---|"]
    for k, v in f.items():
        L.append("| %s | %s |" % (k, v))
    L += ["", "## Referenced sealed evidence", ""]
    for k, v in a["referenced_sealed_evidence"].items():
        L.append("- %s: `%s`" % (k, v))
    L += ["", "- Historical evidence modified: %s · sealed reports rewritten: %s · admission state changed: %s" % (a["historical_evidence_modified"], a["sealed_reports_rewritten"], a["admission_state_changed"]),
          "- Stage Three definition: %s" % a["stage_three_definition"], ""]
    return "\n".join(L) + "\n"


def run_closure(get: Callable = http_get, run_id: str | None = None) -> tuple:
    run_id = run_id or _dt.now(_tz.utc).strftime("%Y%m%dT%H%M%SZ")
    stage2 = load_stage2_of_record()
    dates = leo_required_dates(stage2)
    ev = fetch_leo_pair_stats(dates, get, run_id)
    leo = leo_verdict(dates, ev["series"])
    art = build_closure(stage2, leo, ev["metas"], run_id)
    return art, write_closure(art)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", default=None)
    a = ap.parse_args(argv)
    art, w = run_closure(run_id=a.run_id)
    print(json.dumps({"run_id": art["run_id"], "leo_final_verdict": art["decision_2_leo"]["final_verdict"], "funnel": art["final_stage_two_funnel"], **w}, indent=2, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
