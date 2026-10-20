"""tools/replay_portfolio_rules.py — Portfolio-level rules on the 2026-10-20 replay series.

READ ONLY · OBSERVATION ONLY · NO LIVE READINESS CLAIM · NO STRATEGY APPROVAL · NO BROKER / NO ORDER

Reads the per-signal replay written by tools/replay_bot_rules.py (signals.json), builds the same
dedup trade series (one trade per symbol+strategy at a time, via replay_bot_rules.dedup) and runs a
chronological book model over it. Rules are fixed before the run; nothing is searched:

  same_dir_cap_N  skip a signal while N positions in the same direction are open (N = 3, 5, 10)
  total_cap_N     skip a signal while N positions are open, any direction (N = 10, 20; reference)
  rolling_skip    skip a signal when the mean R of the last 30 CLOSED signals of the pool (every
                  allowed dedup signal, taken or not, closed strictly before the signal date) is
                  below 0; inactive until 30 closes exist. The pool is what the paper bot can observe
                  through its shadow/hindsight rows.
  rolling_half    same condition, but take the trade at half size (booked R x 0.5) instead of skipping;
                  the rolling mean is measured on full-size R so both variants filter identically
  rolling_skip_book  the same filter keyed to the BOOK's own closes only (source="book"). Kept on the
                  record because it locks: once it skips, the book stops closing trades, the window
                  never refreshes, and it never trades again.

A position occupies its symbol+strategy from the signal date to the exit date inclusive. Signals on the
same date are processed in (date, symbol) order, so an earlier signal can fill the cap for a later one.
Outputs: reports/trade_learning/replay_2026-10-20/portfolio_rules.json. Writes nothing else.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, r"C:\SPARTA_BRAIN")
from tools.replay_bot_rules import PERIODS, dedup  # noqa: E402

ROOT = Path(r"C:\SPARTA_BRAIN")
REPLAY_DIR = ROOT / "reports" / "trade_learning" / "replay_2026-10-20"
OOS_FROM = "2026-09-15"
WINDOW = 30

RULES = {
    "baseline":       dict(kind="none"),
    "same_dir_cap_3": dict(kind="same_dir_cap", N=3),
    "same_dir_cap_5": dict(kind="same_dir_cap", N=5),
    "same_dir_cap_10": dict(kind="same_dir_cap", N=10),
    "total_cap_10":   dict(kind="total_cap", N=10),
    "total_cap_20":   dict(kind="total_cap", N=20),
    "rolling_skip":   dict(kind="rolling", mode="skip", window=WINDOW, source="pool"),
    "rolling_half":   dict(kind="rolling", mode="half", window=WINDOW, source="pool"),
    "rolling_skip_book": dict(kind="rolling", mode="skip", window=WINDOW, source="book"),
}


def load_trades(path: Path = REPLAY_DIR / "signals.json") -> list[dict]:
    sigs = [s for s in json.loads(path.read_text(encoding="utf-8")) if s.get("allowed") and s.get("res_base")]
    rows = []
    for s in dedup(sigs):
        rows.append(dict(sym=s["sym"], strat=s["strat"], direction=s["direction"], date=s["date"],
                         exit_date=s["res_base"]["exit_date"], R=float(s["res_base"]["R"]),
                         regime=s.get("regime"), base=s.get("base")))
    rows.sort(key=lambda t: (t["date"], t["sym"], t["strat"]))
    return rows


def simulate(trades: list[dict], rule: dict) -> list[dict]:
    """Run one rule over the chronological trade series.

    Returns one record per signal: the input fields plus `taken` (bool), `booked_R` (float or None)
    and `full_R`. Open positions are tracked with inclusive exit dates. The rolling window is built
    from signals whose exit_date is strictly before the signal date: every pool signal when
    rule["source"] == "pool" (default), only the book's own taken trades when "book"."""
    kind = rule.get("kind", "none")
    source = rule.get("source", "pool")
    open_pos: list[dict] = []          # taken trades still open (exit_date >= current date)
    pending: list[dict] = []           # signals seen (pool) or taken (book) that have not closed yet
    closed: list[dict] = []            # rolled off pending once exit_date < signal date
    out = []
    for t in trades:
        d = t["date"]
        # roll closed positions out of the open book (exit strictly before the signal date)
        open_pos = [p for p in open_pos if p["exit_date"] >= d]
        still = []
        for p in pending:
            (closed if p["exit_date"] < d else still).append(p)
        pending = still
        closed.sort(key=lambda p: (p["exit_date"], p["date"], p["sym"]))
        take, scale = True, 1.0
        if kind == "same_dir_cap":
            if sum(1 for p in open_pos if p["direction"] == t["direction"]) >= rule["N"]:
                take = False
        elif kind == "total_cap":
            if len(open_pos) >= rule["N"]:
                take = False
        elif kind == "rolling":
            w = rule.get("window", WINDOW)
            if len(closed) >= w:
                recent = closed[-w:]
                if float(np.mean([p["full_R"] for p in recent])) < 0.0:
                    if rule.get("mode") == "half":
                        scale = 0.5
                    else:
                        take = False
        rec = dict(t, taken=take, full_R=t["R"], booked_R=(t["R"] * scale if take else None))
        out.append(rec)
        if take:
            open_pos.append(rec)
        if source == "pool" or take:
            pending.append(rec)
    return out


def stats(rs, rng) -> dict:
    rs = np.asarray(rs, dtype=float)
    if len(rs) == 0:
        return dict(n=0)
    boots = rng.choice(rs, size=(4000, len(rs)), replace=True).mean(axis=1)
    cum = np.cumsum(rs)
    dd = float((np.maximum.accumulate(cum) - cum).max())
    return dict(n=int(len(rs)), sum=round(float(rs.sum()), 2), mean=round(float(rs.mean()), 3),
                win=round(float((rs > 0).mean()), 2), p_pos=round(float((boots > 0).mean()), 3),
                max_dd=round(dd, 1))


def summarize(recs: list[dict], rng) -> dict:
    windows = {"ALL": lambda r: True, "OOS": lambda r: r["date"] >= OOS_FROM}
    windows.update({f"{a}..{b}": (lambda r, a=a, b=b: a <= r["date"] < b) for a, b in PERIODS})
    taken = [r for r in recs if r["taken"]]
    skipped = [r for r in recs if not r["taken"]]
    out = {"taken": {}, "skipped_full_R": {}, "n_signals": len(recs)}
    for w, wf in windows.items():
        out["taken"][w] = stats([r["booked_R"] for r in taken if wf(r)], rng)
        sk = [r["full_R"] for r in skipped if wf(r)]
        out["skipped_full_R"][w] = dict(n=len(sk), sum=round(float(sum(sk)), 2),
                                        mean=(round(float(np.mean(sk)), 3) if sk else None))
    return out


def main() -> int:
    trades = load_trades()
    report = {"n_trades": len(trades), "window": WINDOW, "oos_from": OOS_FROM, "rules": {}}
    for name, rule in RULES.items():
        rng = np.random.default_rng(7)          # same seed per rule: bootstrap noise is comparable
        recs = simulate(trades, rule)
        report["rules"][name] = summarize(recs, rng)
    (REPLAY_DIR / "portfolio_rules.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    for name, r in report["rules"].items():
        a, o = r["taken"]["ALL"], r["taken"]["OOS"]
        print(f"{name:16s} ALL n={a.get('n')} sum={a.get('sum')} mean={a.get('mean')} p={a.get('p_pos')} dd={a.get('max_dd')}"
              f" | OOS n={o.get('n')} sum={o.get('sum')} mean={o.get('mean')} p={o.get('p_pos')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
