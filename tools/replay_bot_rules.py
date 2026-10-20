"""tools/replay_bot_rules.py — Replay of the paper bot's OWN code on Binance daily bars.

READ ONLY · OBSERVATION ONLY · NO LIVE READINESS CLAIM · NO STRATEGY APPROVAL · NO BROKER / NO ORDER

Imports the bot's signal, regime-gate and bar-hit functions from obsidian-trade-logger and
re-runs them bar by bar; nothing in the bot repo, its DB or its config is touched. Writes only
under reports/trade_learning/replay_<date>/ (plus a kline cache in the session scratchpad).

Strategies replayed: the ones the allocation currently lets trade — D, E, F, F2
(D2, E2 and G are quarantined). Exits are the bot's rules as of 2026-10-14 (half off at
1R + breakeven for D/E; Fibonacci ladder 40/40/20 at 1.618/2.618/4.236R with breakeven
after the first rung for F/F2), 20-day timeout, gap-honest fills, stop wins over target.
Entry at the signal bar's close (what build_trade records), 0.1% fee per side.
tests/test_replay_bot_rules.py checks sim_de / sim_f against the bot's manage_de / manage_f.

Pre-stated variants (4, all pre-existing candidates, nothing searched):
  longs_only  : refuse every short
  confirm     : the bot's own _evaluate_breakout_confirmation gate on Donchian entries
  f_rung_1r   : F/F2 first rung at 1.0R instead of 1.618R (rest of the ladder unchanged)
  timeout_40  : hold up to 40 days instead of 20
Windows: IS = signals before 2026-09-15 (pre partial-bar fix); OOS = 2026-09-15 onward
(the same window as the live journal's admissible evidence).
"""
import json
import logging
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

logging.disable(logging.CRITICAL)
BOT = Path(os.environ.get("OBSIDIAN_BOT_REPO", r"C:\Users\mahmo\obsidian-trade-logger"))
sys.path.insert(0, str(BOT))
from scripts.live_signals import compute_indicators, fetch_daily  # noqa: E402
from scripts.trade_bot import (  # noqa: E402
    detect_signal_d, detect_signal_e, detect_signal_f, detect_signal_f2, detect_signal_d2,
    _bar_hit, _evaluate_breakout_confirmation,
)
from scripts.regime_detector import detect_regime  # noqa: E402
from scripts.regime_control import is_signal_allowed  # noqa: E402

RUN_DATE = os.environ.get("REPLAY_RUN_DATE", "2026-10-20")
CACHE = Path(os.environ.get("REPLAY_KLINE_CACHE",
             r"C:\Users\mahmo\AppData\Local\Temp\claude\C--SPARTA-BRAIN\a2d37bdd-dc81-4b2f-a484-b80ef402874d\scratchpad\klines_1d"))
OUT = Path(r"C:\SPARTA_BRAIN\reports\trade_learning") / f"replay_{RUN_DATE}"
LOG = OUT / "progress.log"

SYMBOLS = json.loads((BOT / "config" / "live_config.json").read_text())["symbols"]
FEE = 0.001
WARMUP = 290
STRATS = ["D", "E", "F", "F2"]
OOS_FROM = "2026-09-15"
TODAY = RUN_DATE
RNG = np.random.default_rng(7)


def log(msg):
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(f"{time.strftime('%H:%M:%S')} {msg}\n")


# ── data ─────────────────────────────────────────────────────────────────────
def load(sym):
    CACHE.mkdir(parents=True, exist_ok=True)
    p = CACHE / f"{sym}.csv"
    if p.exists():
        df = pd.read_csv(p, index_col=0, parse_dates=True)
        if str(df.index[-1].date()) >= "2026-10-19":
            return df
    df = fetch_daily(sym, limit=1000)
    df.to_csv(p)
    time.sleep(0.15)
    return df


# ── exits (mirror manage_de / manage_f) ──────────────────────────────────────
def _delta(d, entry, px):
    return (px - entry) if d == "long" else (entry - px)


def _fee_R(frac, p_in, p_out, sd):
    return frac * FEE * (p_in + p_out) / sd


def sim_de(bars, i, sig, timeout):
    entry, sl, tp1, d = sig["entry"], sig["sl"], sig["tp1"], sig["direction"]
    sd = abs(entry - sl)
    lvl_p = entry + sd if d == "long" else entry - sd            # PARTIAL_R = 1.0
    partial, realized, mfe = False, 0.0, 0.0
    for j in range(i + 1, len(bars)):
        o, h, l, c = bars[j]
        mfe = max(mfe, _delta(d, entry, h if d == "long" else l) / sd)
        days = j - i
        to = days >= timeout
        sl_hit, sl_fill = _bar_hit(d, entry if partial else sl, "stop", c, o, h, l)
        tp_hit, tp_fill = _bar_hit(d, tp1, "target", c, o, h, l)
        if partial:
            if sl_hit or tp_hit or to:
                px = sl_fill if sl_hit else (tp_fill if tp_hit else c)
                R = realized + 0.5 * _delta(d, entry, px) / sd - _fee_R(0.5, entry, px, sd)
                out = "TIMEOUT" if (to and not sl_hit and not tp_hit) else ("WIN" if R >= 0 else "LOSS")
                return dict(R=R, outcome=out, days=days, mfe=mfe, exit_i=j)
            continue
        if sl_hit:
            R = _delta(d, entry, sl_fill) / sd - _fee_R(1, entry, sl_fill, sd)
            return dict(R=R, outcome="LOSS", days=days, mfe=mfe, exit_i=j)
        p_hit, p_fill = _bar_hit(d, lvl_p, "target", c, o, h, l)
        if p_hit:
            realized = 0.5 * _delta(d, entry, p_fill) / sd - _fee_R(0.5, entry, p_fill, sd)
            partial = True
            if tp_hit:
                R = realized + 0.5 * _delta(d, entry, tp_fill) / sd - _fee_R(0.5, entry, tp_fill, sd)
                return dict(R=R, outcome="WIN", days=days, mfe=mfe, exit_i=j)
            continue
        if tp_hit:
            R = _delta(d, entry, tp_fill) / sd - _fee_R(1, entry, tp_fill, sd)
            return dict(R=R, outcome="WIN", days=days, mfe=mfe, exit_i=j)
        if to:
            R = _delta(d, entry, c) / sd - _fee_R(1, entry, c, sd)
            return dict(R=R, outcome="TIMEOUT", days=days, mfe=mfe, exit_i=j)
    return None


def sim_f(bars, i, sig, timeout, rungs=(1.618, 2.618, 4.236)):
    entry, sl, d = sig["entry"], sig["sl"], sig["direction"]
    sd = abs(entry - sl)
    tps = [entry + r * sd if d == "long" else entry - r * sd for r in rungs]
    fracs = [0.4, 0.4, 0.2]
    stage, realized, sl_cur, mfe = 0, 0.0, sl, 0.0
    for j in range(i + 1, len(bars)):
        o, h, l, c = bars[j]
        mfe = max(mfe, _delta(d, entry, h if d == "long" else l) / sd)
        days = j - i
        to = days >= timeout
        sl_hit, sl_fill = _bar_hit(d, sl_cur, "stop", c, o, h, l)
        tp_hit, tp_fill = _bar_hit(d, tps[stage], "target", c, o, h, l)
        rem = 1.0 - sum(fracs[:stage])
        if stage < 2:
            if sl_hit:
                R = realized + rem * _delta(d, entry, sl_fill) / sd - _fee_R(rem, entry, sl_fill, sd)
                out = "LOSS" if stage == 0 else ("WIN" if R >= 0 else "LOSS")
                return dict(R=R, outcome=out, days=days, mfe=mfe, exit_i=j)
            if tp_hit:
                realized += fracs[stage] * _delta(d, entry, tp_fill) / sd - _fee_R(fracs[stage], entry, tp_fill, sd)
                if stage == 0:
                    sl_cur = entry
                stage += 1
                continue
            if to:
                R = realized + rem * _delta(d, entry, c) / sd - _fee_R(rem, entry, c, sd)
                return dict(R=R, outcome="TIMEOUT", days=days, mfe=mfe, exit_i=j)
            continue
        if sl_hit or tp_hit or to:
            px = sl_fill if sl_hit else (tp_fill if tp_hit else c)
            R = realized + rem * _delta(d, entry, px) / sd - _fee_R(rem, entry, px, sd)
            out = ("WIN" if R >= 0 else "LOSS") if sl_hit else ("WIN" if tp_hit else "TIMEOUT")
            return dict(R=R, outcome=out, days=days, mfe=mfe, exit_i=j)
    return None


def _signal_features(sub: pd.DataFrame, sig: dict) -> dict:
    """The same entry-bar buckets the live loop derives from the bot's context log
    (tools/trade_features.py), computed here from the replay's own bars, plus the raw
    values. Lets every feature-cell hypothesis get a replay prior."""
    try:
        from tools.trade_features import features_from_record
    except ImportError:
        sys.path.insert(0, r"C:\SPARTA_BRAIN")
        from tools.trade_features import features_from_record
    last = sub.iloc[-1]
    rng_ = float(last["high"] - last["low"])
    atr = float(sig.get("atr14") or 0.0)
    prev_atr = float(sub["atr14"].iloc[-4:-1].mean()) if len(sub) >= 4 else None
    vol_prev = float(sub["volume"].iloc[-21:-1].mean()) if "volume" in sub and len(sub) >= 21 else None
    try:
        from scripts.regime_detector import _price_position_in_range
        pos = _price_position_in_range(sub)
    except Exception:
        pos = None
    rec = {
        "candle_body_strength": (abs(float(last["close"] - last["open"])) / rng_) if rng_ > 0 else None,
        "atr_expansion": (atr / prev_atr) if (atr and prev_atr) else None,
        "volume_ratio": (float(last["volume"]) / vol_prev) if (vol_prev and "volume" in last) else None,
        "range_position": pos,
        "ema20_dist_atr": ((float(last["close"]) - float(last["ema20"])) / atr) if atr and last["ema20"] == last["ema20"] else None,
        "ema200_dist_atr": ((float(last["close"]) - float(last["ema200"])) / atr) if atr and last["ema200"] == last["ema200"] else None,
    }
    out = features_from_record(rec)
    out["raw"] = {k: (None if v is None or v != v else round(float(v), 4)) for k, v in rec.items()}
    return out


# ── scan ─────────────────────────────────────────────────────────────────────
def scan():
    signals = []
    t0 = time.time()
    for k, sym in enumerate(SYMBOLS):
        raw = load(sym)
        raw = raw[raw.index.strftime("%Y-%m-%d") < TODAY]      # completed bars only
        df = compute_indicators(raw)
        bars = df[["open", "high", "low", "close"]].to_numpy()
        dates = df.index.strftime("%Y-%m-%d").tolist()
        n_sig = 0
        for t in range(WARMUP, len(df)):
            sub = df.iloc[: t + 1]
            regime = None
            for strat in STRATS:
                if strat == "D":
                    sig = detect_signal_d(sub)
                elif strat == "E":
                    sig = detect_signal_e(sub)
                elif strat == "F":
                    sig = detect_signal_f(sub)
                else:
                    sig = detect_signal_f2(sub, sym)
                if sig is None:
                    continue
                if regime is None:
                    regime = detect_regime(sym, sub)["regime"]
                allowed, reason = is_signal_allowed(strat, sig["direction"], regime, sub)
                if strat == "F":
                    base = "D" if detect_signal_d(sub) is not None else "E"
                elif strat == "F2":
                    base = "D2" if detect_signal_d2(sub, sym) is not None else "E2"
                else:
                    base = strat
                breakout = base in ("D", "D2")
                confirm = bool(_evaluate_breakout_confirmation(sub)[0]) if breakout else True
                rec = dict(sym=sym, strat=strat, base=base, i=t, date=dates[t],
                           direction=sig["direction"], entry=float(sig["entry"]), sl=float(sig["sl"]),
                           tp1=float(sig["tp1"]), regime=regime, allowed=bool(allowed), reason=reason,
                           confirm=confirm, features=_signal_features(sub, sig))
                # Every signal is simulated, allowed or not: blocked ones are what the
                # ledger's unblock hypotheses are about (tools/replay_prior.py).
                f = sim_f if strat in ("F", "F2") else sim_de
                rec["res_base"] = f(bars, t, sig, 20)
                rec["res_to40"] = f(bars, t, sig, 40)
                rec["res_f1r"] = sim_f(bars, t, sig, 20, rungs=(1.0, 2.618, 4.236)) if strat in ("F", "F2") else rec["res_base"]
                for key in ("res_base", "res_to40", "res_f1r"):
                    if rec[key] is not None:
                        rec[key]["exit_date"] = dates[rec[key]["exit_i"]]
                if allowed:
                    n_sig += 1
                signals.append(rec)
        log(f"{k+1:2d}/{len(SYMBOLS)} {sym}: bars {len(df)}, allowed signals {n_sig}, {time.time()-t0:.0f}s")
    return signals


# ── stats ────────────────────────────────────────────────────────────────────
def stats(rs):
    rs = np.asarray(rs, dtype=float)
    if len(rs) == 0:
        return dict(n=0)
    boots = RNG.choice(rs, size=(4000, len(rs)), replace=True).mean(axis=1)
    cum = np.cumsum(rs)
    dd = float((np.maximum.accumulate(cum) - cum).max()) if len(rs) else 0.0
    return dict(n=int(len(rs)), sum=round(float(rs.sum()), 2), mean=round(float(rs.mean()), 3),
                win=round(float((rs > 0).mean()), 2), p_pos=round(float((boots > 0).mean()), 3),
                max_dd=round(dd, 1))


def paired(a, b):
    """p(mean(b - a) > 0) for same-signal exit variants."""
    d = np.asarray(b, dtype=float) - np.asarray(a, dtype=float)
    if len(d) == 0:
        return None
    boots = RNG.choice(d, size=(4000, len(d)), replace=True).mean(axis=1)
    return dict(n=int(len(d)), sum_delta=round(float(d.sum()), 2), mean_delta=round(float(d.mean()), 3),
                p_pos=round(float((boots > 0).mean()), 3))


def one_slot(sigs, key, slots: int = 1):
    """The bot's reality on one exchange: `slots` positions per strategy (1 until
    2026-10-20, config paper_slots_per_strategy after), first allowed signals of the day
    in config symbol order win, a slot frees the day after the exit, AND the coordinator's
    one-position-per-symbol rule: a symbol held by any strategy is not opened by another
    (config/trade_coordinator_config.json max_open_trades_per_symbol = 1; the first
    2026-10-20 run of this model lacked that rule and over-counted D/F/F2 triplets)."""
    order = {s: i for i, s in enumerate(SYMBOLS)}
    by_day: dict[str, list] = {}
    for x in sigs:
        by_day.setdefault(x["date"], []).append(x)
    open_pos: list[tuple] = []     # (strat, sym, exit_date or "9999", sig, res)
    taken = []
    for d in sorted(by_day):
        open_pos = [p for p in open_pos if p[2] >= d]          # frees the day after exit_date
        held_syms = {p[1] for p in open_pos}
        for strat in STRATS:
            n_open = sum(1 for p in open_pos if p[0] == strat)
            for s in sorted((x for x in by_day[d] if x["strat"] == strat), key=lambda x: order[x["sym"]]):
                if n_open >= slots or s["sym"] in held_syms:
                    continue
                r = s.get(key)
                exit_d = r["exit_date"] if r is not None else "9999"
                open_pos.append((strat, s["sym"], exit_d, s, r))
                held_syms.add(s["sym"])
                n_open += 1
                taken.append((s, r))
    return taken


def dedup(sigs, key="res_base", filt=lambda s: True):
    """One trade per (symbol, strategy) at a time: no re-entry while that trade is open.
    Removes the overlap of consecutive breakout days without the slot's symbol-order artefact."""
    out, busy = [], {}
    for s in sorted(sigs, key=lambda x: (x["date"], x["sym"])):
        if not filt(s) or s.get(key) is None:
            continue
        k = (s["sym"], s["strat"])
        if s["date"] <= busy.get(k, ""):
            continue
        busy[k] = s[key]["exit_date"]
        out.append(s)
    return out


PERIODS = (("2024-11-01", "2025-05-01"), ("2025-05-01", "2025-11-01"), ("2025-11-01", "2026-05-01"),
           ("2026-05-01", "2026-09-15"), ("2026-09-15", "2027-01-01"))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    LOG.write_text("")
    signals = scan()
    (OUT / "signals.json").write_text(json.dumps(signals, indent=0), encoding="utf-8")
    allowed = [s for s in signals if s["allowed"]]
    log(f"signals total {len(signals)}, allowed {len(allowed)}")

    variants = {
        "baseline":   (lambda s: True,                      "res_base"),
        "longs_only": (lambda s: s["direction"] == "long",  "res_base"),
        "confirm":    (lambda s: s["confirm"],              "res_base"),
        "f_rung_1r":  (lambda s: True,                      "res_f1r"),
        "timeout_40": (lambda s: True,                      "res_to40"),
    }
    windows = {"ALL": lambda s: True, "IS": lambda s: s["date"] < OOS_FROM, "OOS": lambda s: s["date"] >= OOS_FROM}
    report = {"unlimited": {}, "dedup": {}, "one_slot": {}, "paired": {}, "breakdown": {}, "one_slot_trades_oos": []}

    for vname, (filt, key) in variants.items():
        report["unlimited"][vname] = {}
        report["dedup"][vname] = {}
        report["one_slot"][vname] = {}
        kept = [s for s in allowed if filt(s)]
        dd = dedup(allowed, key, filt)
        for wname, wf in windows.items():
            rs = [s[key]["R"] for s in kept if wf(s) and s[key] is not None]
            report["unlimited"][vname][wname] = stats(rs)
            report["dedup"][vname][wname] = stats([s[key]["R"] for s in dd if wf(s)])
            taken = one_slot([s for s in kept if wf(s)], key)
            rs1 = [r["R"] for s, r in taken if r is not None]
            st = stats(rs1)
            st["still_open"] = sum(1 for s, r in taken if r is None)
            report["one_slot"][vname][wname] = st
            if vname == "baseline" and wname == "OOS":
                report["one_slot_trades_oos"] = [
                    dict(sym=s["sym"], strat=s["strat"], dir=s["direction"], date=s["date"],
                         R=(round(r["R"], 2) if r else None), outcome=(r["outcome"] if r else "OPEN"),
                         mfe=(round(r["mfe"], 2) if r else None)) for s, r in taken]
        if vname in ("longs_only", "confirm"):
            removed = [s for s in allowed if not filt(s)]
            report["unlimited"][vname]["removed"] = {w: stats([s["res_base"]["R"] for s in removed if wf(s) and s["res_base"]])
                                                     for w, wf in windows.items()}
            report["unlimited"][vname]["removed_by_period"] = {
                f"{a}..{b}": stats([s["res_base"]["R"] for s in removed if a <= s["date"] < b and s["res_base"]])
                for a, b in PERIODS}

    for vname, key in (("f_rung_1r", "res_f1r"), ("timeout_40", "res_to40")):
        report["paired"][vname] = {}
        for wname, wf in windows.items():
            pairs = [(s["res_base"]["R"], s[key]["R"]) for s in allowed
                     if wf(s) and s["res_base"] is not None and s[key] is not None
                     and (vname != "f_rung_1r" or s["strat"] in ("F", "F2"))]
            report["paired"][vname][wname] = paired([a for a, b in pairs], [b for a, b in pairs])

    base_dd = dedup(allowed)
    for dim in ("strat", "direction", "regime", "base"):
        report["breakdown"][dim] = {}
        for val in sorted({s[dim] for s in allowed}):
            report["breakdown"][dim][val] = {w: stats([s["res_base"]["R"] for s in base_dd if s[dim] == val and wf(s)])
                                             for w, wf in windows.items()}
    report["breakdown"]["period"] = {f"{a}..{b}": stats([s["res_base"]["R"] for s in base_dd if a <= s["date"] < b])
                                     for a, b in PERIODS}
    report["breakdown"]["base_x_direction_by_period"] = {
        f"{bs}/{d}": {f"{a}..{b}": stats([s["res_base"]["R"] for s in base_dd
                                          if s["base"] == bs and s["direction"] == d and a <= s["date"] < b])
                      for a, b in PERIODS}
        for bs in ("D", "D2", "E", "E2") for d in ("long", "short")}
    dset = {(s["sym"], s["date"]) for s in allowed if s["strat"] == "D"}
    report["overlap"] = {st: dict(n=sum(1 for s in allowed if s["strat"] == st),
                                  with_D_same_bar=sum(1 for s in allowed if s["strat"] == st and (s["sym"], s["date"]) in dset))
                         for st in ("F", "F2")}
    report["blocked_reasons"] = {}
    for s in signals:
        if not s["allowed"]:
            k = s["reason"].split("(")[0].strip()
            report["blocked_reasons"][k] = report["blocked_reasons"].get(k, 0) + 1
    (OUT / "report.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    log("done")


if __name__ == "__main__":
    main()
