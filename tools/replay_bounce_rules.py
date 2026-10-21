"""tools/replay_bounce_rules.py — pre-stated replay of "support bounce" entries the bot does not take.

READ ONLY · OBSERVATION ONLY · NO LIVE READINESS CLAIM · NO STRATEGY APPROVAL · NO BROKER / NO ORDER

Operator question (2026-10-21): "we had very good support at the Donchian low and the 50 EMA and we
didn't get entries?" True: every live strategy (D, E, F, F2) is a breakout or an EMA cross; a bounce
is a close inside the range and returns no signal. This study replays bounce rules on the same data
and exits as tools/replay_bot_rules.py so the idea gets a number before anyone touches the bot.

PRE-STATED RULES (fixed before the first run; nothing added after seeing results)
  Indicators: the bot's own compute_indicators (ema20/50/200, atr14, 20-day don_hi/don_lo of the
  PRIOR 20 bars). Entry at the signal bar's close, like the bot. Fee 0.1% a side, 1R per trade.
  Long rules ("support"):
    DON    low <= don_lo + 0.5*ATR  and close > don_lo  and close >= open
    DON_T  DON and close > ema200
    EMA50  low <= ema50 + 0.5*ATR   and close > ema50   and close >= open  and ema50 > ema200
  Mirror short rules ("resistance"), reported for regime-dependence only:
    DON_HI    high >= don_hi - 0.5*ATR and close < don_hi and close <= open
    DON_HI_T  DON_HI and close < ema200
    EMA50_S   high >= ema50 - 0.5*ATR  and close < ema50  and close <= open and ema50 < ema200
  Exits (both via the engine's sim_de, proven equal to the bot's manage_de):
    d_exit    the bot's D exit: stop 2*ATR, target 3x stop distance, half off at 1R + breakeven, 20-day timeout
    s_exit    structural: stop 0.5*ATR beyond the support level, target 3x stop distance, same management;
              skipped when the stop distance exceeds 4*ATR
  Gate: the live regime gate for strategy D in that direction (is_signal_allowed); gated and ungated reported.
  Book: dedup = one open trade per (symbol, rule) at a time.
  Benchmark: ANY_DAY = long at every bar's close with d_exit, dedup per symbol (the universe's drift with
             this exit). A bounce rule has to beat that, not zero.
  Headline test: DON_T with d_exit, gated, mean R minus ANY_DAY mean R, bootstrap p; six primary long
  cells (3 rules x 2 exits), so the headline counts as a finding only at p >= 0.99 and the same sign in
  every half-year with >= 10 trades. Anything else is "noted".

Outputs: reports/trade_learning/replay_bounce_<date>/bounce.json (+ progress.log) and
         reports/trade_learning/replay_bounce_<date>.md. Nothing is registered, nothing is changed.
"""
from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tools import replay_bot_rules as eng  # noqa: E402  (engine: data, exits, stats, periods)
from tools.replay_bot_rules import PERIODS, SYMBOLS, OOS_FROM, sim_de, stats, compute_indicators  # noqa: E402
from scripts.regime_detector import detect_regime  # noqa: E402
from scripts.regime_control import is_signal_allowed  # noqa: E402

BANNER = "READ ONLY · OBSERVATION ONLY · NO LIVE READINESS CLAIM · NO STRATEGY APPROVAL · NO BROKER / NO ORDER"
RUN_DATE = os.environ.get("BOUNCE_RUN_DATE", datetime.now(timezone.utc).strftime("%Y-%m-%d"))
REPORT_DIR = _REPO_ROOT / "reports" / "trade_learning"
OUT = REPORT_DIR / f"replay_bounce_{RUN_DATE}"
TOUCH_ATR = 0.5
STRUCT_STOP_ATR = 0.5
STRUCT_MAX_SD_ATR = 4.0
TIMEOUT = 20
LONG_RULES = ("DON", "DON_T", "EMA50")
SHORT_RULES = ("DON_HI", "DON_HI_T", "EMA50_S")
RULES = LONG_RULES + SHORT_RULES
HEADLINE = ("DON_T", "d_exit")
HEADLINE_P = 0.99
MIN_PERIOD_N = 10


def log(msg: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "progress.log").open("a", encoding="utf-8") as fh:
        fh.write(f"{time.strftime('%H:%M:%S')} {msg}\n")


# ── data: refresh the engine's cache so the last COMPLETED bar is yesterday's ─────────────
def load_fresh(sym: str, today: str) -> pd.DataFrame:
    p = eng.CACHE / f"{sym}.csv"
    if p.exists():
        df = pd.read_csv(p, index_col=0, parse_dates=True)
        if str(df.index[-1].date()) >= today:       # cache already holds today's partial bar
            return df
    df = eng.fetch_daily(sym, limit=1000)
    eng.CACHE.mkdir(parents=True, exist_ok=True)
    df.to_csv(p)
    time.sleep(0.15)
    return df


# ── rules ───────────────────────────────────────────────────────────────────────────────
def rule_mask(df: pd.DataFrame, rule: str) -> tuple[pd.Series, pd.Series]:
    """(boolean mask of qualifying bars, the support/resistance level per bar)."""
    lo, hi, c, o, atr = df["low"], df["high"], df["close"], df["open"], df["atr14"]
    touch = TOUCH_ATR * atr
    if rule in ("DON", "DON_T"):
        lvl = df["don_lo"]
        m = (lo <= lvl + touch) & (c > lvl) & (c >= o)
        if rule == "DON_T":
            m &= c > df["ema200"]
    elif rule == "EMA50":
        lvl = df["ema50"]
        m = (lo <= lvl + touch) & (c > lvl) & (c >= o) & (df["ema50"] > df["ema200"])
    elif rule in ("DON_HI", "DON_HI_T"):
        lvl = df["don_hi"]
        m = (hi >= lvl - touch) & (c < lvl) & (c <= o)
        if rule == "DON_HI_T":
            m &= c < df["ema200"]
    elif rule == "EMA50_S":
        lvl = df["ema50"]
        m = (hi >= lvl - touch) & (c < lvl) & (c <= o) & (df["ema50"] < df["ema200"])
    else:
        raise ValueError(rule)
    m &= lvl.notna() & atr.notna() & (atr > 0)
    return m.fillna(False), lvl


def direction_of(rule: str) -> str:
    return "long" if rule in LONG_RULES else "short"


def d_exit_sig(entry: float, atr: float, direction: str) -> dict[str, Any]:
    sl = entry - 2 * atr if direction == "long" else entry + 2 * atr
    sd = abs(entry - sl)
    tp1 = entry + 3 * sd if direction == "long" else entry - 3 * sd
    return dict(entry=entry, sl=sl, tp1=tp1, direction=direction)


def s_exit_sig(entry: float, atr: float, level: float, direction: str) -> dict[str, Any] | None:
    sl = level - STRUCT_STOP_ATR * atr if direction == "long" else level + STRUCT_STOP_ATR * atr
    sd = (entry - sl) if direction == "long" else (sl - entry)
    if sd <= 0 or sd > STRUCT_MAX_SD_ATR * atr:
        return None
    tp1 = entry + 3 * sd if direction == "long" else entry - 3 * sd
    return dict(entry=entry, sl=sl, tp1=tp1, direction=direction)


def _with_exit_date(res: dict | None, dates: list[str]) -> dict | None:
    if res is not None:
        res["exit_date"] = dates[res["exit_i"]]
    return res


def scan_symbol(sym: str, raw: pd.DataFrame, today: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """All bounce signals for one symbol (every rule, gated flag attached) and the ANY_DAY benchmark trades."""
    raw = raw[raw.index.strftime("%Y-%m-%d") < today]
    df = compute_indicators(raw)
    bars = df[["open", "high", "low", "close"]].to_numpy()
    dates = df.index.strftime("%Y-%m-%d").tolist()
    sigs: list[dict[str, Any]] = []
    regime_cache: dict[int, str] = {}
    for rule in RULES:
        m, lvl = rule_mask(df, rule)
        d = direction_of(rule)
        for t in (int(x) for x in np.flatnonzero(m.to_numpy())):   # plain int: keeps exit records JSON-clean
            if t < eng.WARMUP:
                continue
            entry, atr, level = float(df["close"].iloc[t]), float(df["atr14"].iloc[t]), float(lvl.iloc[t])
            if t not in regime_cache:
                regime_cache[t] = detect_regime(sym, df.iloc[: t + 1])["regime"]
            regime = regime_cache[t]
            allowed, reason = is_signal_allowed("D", d, regime, df.iloc[: t + 1])
            sd = d_exit_sig(entry, atr, d)
            ss = s_exit_sig(entry, atr, level, d)
            rec = dict(sym=sym, rule=rule, i=int(t), date=dates[t], direction=d, entry=entry, atr=atr,
                       level=level, regime=regime, allowed=bool(allowed), reason=reason,
                       d_exit=_with_exit_date(sim_de(bars, t, sd, TIMEOUT), dates),
                       s_exit=_with_exit_date(sim_de(bars, t, ss, TIMEOUT), dates) if ss else None,
                       sl_d=sd["sl"], sl_s=ss["sl"] if ss else None)
            if rec["d_exit"] is None:            # still open at the end of the data: mark at last close
                last = float(df["close"].iloc[-1])
                rec["open_mark_R"] = round(((last - entry) if d == "long" else (entry - last)) / abs(entry - sd["sl"]), 2)
            sigs.append(rec)
    bench: list[dict[str, Any]] = []
    busy = ""
    for t in range(eng.WARMUP, len(df)):
        if dates[t] <= busy:
            continue
        atr = float(df["atr14"].iloc[t])
        if not np.isfinite(atr) or atr <= 0:
            continue
        r = sim_de(bars, t, d_exit_sig(float(df["close"].iloc[t]), atr, "long"), TIMEOUT)
        if r is None:
            break
        _with_exit_date(r, dates)
        busy = r["exit_date"]
        bench.append(dict(sym=sym, rule="ANY_DAY", date=dates[t], direction="long", d_exit=r))
    return sigs, bench


def dedup(sigs: list[dict[str, Any]], key: str, filt=lambda s: True) -> list[dict[str, Any]]:
    out, busy = [], {}
    for s in sorted(sigs, key=lambda x: (x["date"], x["sym"])):
        if not filt(s) or s.get(key) is None:
            continue
        k = (s["sym"], s["rule"])
        if s["date"] <= busy.get(k, ""):
            continue
        busy[k] = s[key]["exit_date"]
        out.append(s)
    return out


# ── stats ───────────────────────────────────────────────────────────────────────────────
def cell(sigs: list[dict[str, Any]], key: str) -> dict[str, Any]:
    rs = [s[key]["R"] for s in sigs]
    out = stats(rs)
    out["by_period"] = {}
    signs = []
    overall = float(np.mean(rs)) if rs else 0.0
    for a, b in PERIODS:
        sel = [s[key]["R"] for s in sigs if a <= s["date"] < b]
        if sel:
            m = float(np.mean(sel))
            out["by_period"][f"{a}..{b}"] = {"n": len(sel), "mean": round(m, 3)}
            if len(sel) >= MIN_PERIOD_N:
                signs.append((m > 0) == (overall > 0))
    out["stable"] = None if len(signs) < 2 else all(signs)
    oos = [s[key]["R"] for s in sigs if s["date"] >= OOS_FROM]
    out["oos"] = stats(oos)
    return out


def diff_means(a: list[float], b: list[float]) -> dict[str, Any]:
    """Bootstrap p(mean a > mean b) for two independent samples."""
    if not a or not b:
        return {"n_a": len(a), "n_b": len(b)}
    rng = np.random.default_rng(11)
    A, B = np.asarray(a, float), np.asarray(b, float)
    d = rng.choice(A, (4000, len(A))).mean(1) - rng.choice(B, (4000, len(B))).mean(1)
    return {"n_a": int(len(A)), "n_b": int(len(B)), "mean_a": round(float(A.mean()), 3), "mean_b": round(float(B.mean()), 3),
            "delta": round(float(A.mean() - B.mean()), 3), "p_a_gt_b": round(float((d > 0).mean()), 3),
            "ci95": [round(float(np.percentile(d, 2.5)), 3), round(float(np.percentile(d, 97.5)), 3)]}


def build(sigs: list[dict[str, Any]], bench: list[dict[str, Any]], as_of: str) -> dict[str, Any]:
    res: dict[str, Any] = {"as_of": as_of, "banner": BANNER, "rules": {}, "benchmark": cell(bench, "d_exit"),
                           "n_signals_raw": len(sigs)}
    bench_rs = [b["d_exit"]["R"] for b in bench]
    for rule in RULES:
        rr: dict[str, Any] = {}
        for key in ("d_exit", "s_exit"):
            for gated in (False, True):
                dd = dedup(sigs, key, lambda s, r=rule, g=gated: s["rule"] == r and (s["allowed"] or not g))
                c = cell(dd, key)
                if rule in LONG_RULES and key == "d_exit":
                    c["vs_any_day"] = diff_means([s[key]["R"] for s in dd], bench_rs)
                rr[f"{key}{'_gated' if gated else ''}"] = c
        res["rules"][rule] = rr
    h_rule, h_key = HEADLINE
    h = res["rules"][h_rule][f"{h_key}_gated"]
    vs = h.get("vs_any_day", {})
    res["headline"] = {"cell": f"{h_rule} {h_key} gated", "n": h.get("n", 0), "mean": h.get("mean"),
                       "delta_vs_any_day": vs.get("delta"), "p": vs.get("p_a_gt_b"), "stable": h.get("stable"),
                       "finding": bool(vs.get("p_a_gt_b", 0) >= HEADLINE_P and h.get("stable") is True)}
    recent = [s for s in sigs if s["rule"] in LONG_RULES and s["date"] >= "2026-10-01"]
    res["recent_long_signals"] = [
        {k: s.get(k) for k in ("date", "sym", "rule", "entry", "regime", "allowed", "reason")}
        | {"result": (f"{s['d_exit']['outcome']} {s['d_exit']['R']:+.2f}R" if s["d_exit"]
                      else f"open, {s.get('open_mark_R', 0):+.2f}R at last close")}
        for s in sorted(recent, key=lambda x: (x["date"], x["sym"]))]
    return res


def _fmt(c: dict[str, Any]) -> str:
    if not c.get("n"):
        return "| 0 | - | - | - | - | - |"
    byp = ", ".join(f"{v['mean']:+.2f}({v['n']})" for v in c["by_period"].values())
    oos = c["oos"]
    o = f"{oos['mean']:+.3f} (n={oos['n']})" if oos.get("n") else "-"
    stab = {True: "yes", False: "no", None: "n/a"}[c.get("stable")]
    return f"| {c['n']} | {c['mean']:+.3f} | {c['win']:.2f} | {c['p_pos']:.3f} | {o} | {byp} · stable {stab} |"


def render(res: dict[str, Any]) -> str:
    b = res["benchmark"]
    h = res["headline"]
    L = [f"# Replay study: support-bounce entries the bot does not take — {res['as_of']}", "", f"**{BANNER}**", "",
         "**Question (operator, 2026-10-21):** price bounced at the Donchian low and the 50 EMA and the bot took no "
         "entry. Correct by construction: D/E/F/F2 are breakout or EMA-cross rules and a bounce is a close inside "
         "the range. This replay gives the bounce idea a number on the same data and exits as the live rules "
         "(see the rule block at the top of `tools/replay_bounce_rules.py`; all rules and the headline test were "
         "fixed before the run).", "",
         f"**Headline ({h['cell']}):** n={h['n']}, mean {h['mean']:+.3f}R per trade; "
         f"minus the any-day benchmark {h['delta_vs_any_day']:+.3f}R, p={h['p']}, stable across half-years: "
         f"{ {True: 'yes', False: 'no', None: 'n/a'}[h['stable']] }. "
         + ("**Passes the pre-stated bar** (p >= 0.99 and same sign every half-year)." if h["finding"]
            else "**Does not pass the pre-stated bar** (p >= 0.99 and same sign in every half-year with >= 10 trades)."),
         "",
         "## Benchmark: long at any bar's close, D exit, one trade per symbol at a time", "",
         "| n | mean R | win | p(mean>0) | post-fix | by half-year |", "|---|---|---|---|---|---|",
         _fmt(b), "",
         "Every number below has to be read against this line: it is what buying on a random day with the same "
         "exit returned over the window. A rule that merely matches it has found nothing.", "",
         "## Long rules (support)", "",
         "| rule / exit / gate | n | mean R | win | p(mean>0) | post-fix | by half-year |", "|---|---|---|---|---|---|---|"]
    for rule in LONG_RULES:
        for k in ("d_exit", "d_exit_gated", "s_exit", "s_exit_gated"):
            L.append(f"| {rule} {k.replace('_', ' ')} " + _fmt(res["rules"][rule][k]))
    L += ["", "| rule (d_exit) | vs any-day Δ mean R | p(rule > any-day) | 95% CI |", "|---|---|---|---|"]
    for rule in LONG_RULES:
        for k in ("d_exit", "d_exit_gated"):
            v = res["rules"][rule][k].get("vs_any_day", {})
            if v.get("n_a"):
                L.append(f"| {rule} {k.replace('_', ' ')} | {v['delta']:+.3f} | {v['p_a_gt_b']} | [{v['ci95'][0]:+.3f}, {v['ci95'][1]:+.3f}] |")
    L += ["", "## Mirror short rules (resistance), for regime dependence only", "",
          "| rule / exit / gate | n | mean R | win | p(mean>0) | post-fix | by half-year |", "|---|---|---|---|---|---|---|"]
    for rule in SHORT_RULES:
        for k in ("d_exit", "d_exit_gated"):
            L.append(f"| {rule} {k.replace('_', ' ')} " + _fmt(res["rules"][rule][k]))
    L += ["", "## What the long rules would have fired since 2026-10-01 (every signal, before dedup)", "",
          "| date | symbol | rule | regime | live gate | result |", "|---|---|---|---|---|---|"]
    for s in res["recent_long_signals"]:
        gate = "allowed" if s["allowed"] else f"blocked: {s['reason']}"
        L.append(f"| {s['date']} | {s['sym']} | {s['rule']} | {s['regime']} | {gate} | {s['result']} |")
    L += ["", "## Reading", "",
          "- Six primary long cells were pre-stated (3 rules x 2 exits); the headline is one of them. Gated and "
          "ungated are shown so the live regime gate's effect on bounce longs is visible.",
          "- A bounce rule is a new strategy, not a tuning. Nothing here is registered, applied or shadowed; the "
          "operator's freeze on new registrations stands.",
          "- Caveats as in the 2026-10-20 replay: spot bars, universe chosen 2026-09-16, 2.7 years = three or four "
          "regime phases, entry at the close.", "",
          f"_{BANNER}_", ""]
    return "\n".join(L)


FORBIDDEN = ("validated", "ready", "approved", "profitable strategy", "deploy")


def check_words(text: str) -> list[str]:
    low = text.lower()
    return [w for w in FORBIDDEN if w in low]


def _register_manual_entry() -> None:
    try:
        import database as db
        db.upsert_manual_entry(
            "replay_bounce_rules", module_name="Replay Study: Support-Bounce Entries", category="Trading", status="live",
            short_description="Replays pre-stated 'bounce off the Donchian low / 50 EMA' entries the bot does not "
                              "take, on the bot's own data and exits, against an any-day benchmark. Observation only.",
            how_it_works="Reuses tools/replay_bot_rules.py (bars, sim_de exits, periods). Six long cells and three "
                         "mirror shorts fixed in the file header; dedup one trade per symbol and rule; live regime "
                         "gate shown on/off; headline test needs p >= 0.99 vs any-day and the same sign every half-year.",
            when_to_use="When someone asks why the bot did not buy a support bounce, or before anyone proposes a "
                        "mean-reversion entry.",
            user_action="Run `.venv\\Scripts\\python tools\\replay_bounce_rules.py`; read the report on /trade-loop.",
            sort_order=89)
    except Exception:
        pass


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "progress.log").write_text("")
    sigs_all, bench_all = [], []
    t0 = time.time()
    for k, sym in enumerate(SYMBOLS):
        s, b = scan_symbol(sym, load_fresh(sym, RUN_DATE), RUN_DATE)
        sigs_all += s
        bench_all += b
        log(f"{k+1:2d}/{len(SYMBOLS)} {sym}: bounce signals {len(s)}, any-day trades {len(b)}, {time.time()-t0:.0f}s")
    res = build(sigs_all, bench_all, RUN_DATE)
    (OUT / "bounce.json").write_text(json.dumps({"result": res, "signals": sigs_all}, indent=0), encoding="utf-8")
    md = render(res)
    bad = check_words(md)
    if bad:
        log(f"WARNING forbidden words in render: {bad}")
    (REPORT_DIR / f"replay_bounce_{RUN_DATE}.md").write_text(md, encoding="utf-8")
    _register_manual_entry()
    print(BANNER)
    print(json.dumps(res["headline"]))
    print("benchmark", {k: res["benchmark"].get(k) for k in ("n", "mean", "p_pos")})
    for rule in LONG_RULES:
        for k in ("d_exit", "d_exit_gated", "s_exit", "s_exit_gated"):
            c = res["rules"][rule][k]
            print(f"  {rule:6s} {k:13s} n={c.get('n',0):5d} mean={c.get('mean',0):+.3f} p={c.get('p_pos','-')} stable={c.get('stable')}")
    if bad:
        print("forbidden words:", bad)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
