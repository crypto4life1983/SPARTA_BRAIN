"""tools/trade_exit_pairs.py — the paper bot's own paired exit experiment.

READ ONLY · OBSERVATION ONLY · NO LIVE READINESS CLAIM · NO STRATEGY APPROVAL · NO BROKER / NO ORDER

D, F and F2 open the same entry on the same bar most of the time (replay 2026-10-20: F fires
with D on the same bar 93% of the time, F2 66%). Each such triplet is one entry with three
different exits booked side by side: D = half off at 1R + breakeven, 3R target; F = Fibonacci
ladder 40/40/20 at 1.618/2.618/4.236R; F2 = the same ladder on the loose entry. That is a
paired experiment the journal has been running for free. This tool scores it: per paired
signal, the R difference between exits, with a bootstrap on the differences, split at the
2026-09-15 evidence cutoff. It also measures the "best-of-three" bias the learning report's
signal dedup carries (it keeps the best-R row per entry).

Outputs: reports/trade_learning/exit_pairs.md / .json. Nothing is applied by this tool.
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tools.trade_journal_adapter import _REL_TRADES_DB, external_root  # noqa: E402
from tools.trade_journal_learning_report import BANNER, _pnl, load_journal_ro  # noqa: E402

REPORT_DIR = _REPO_ROOT / "reports" / "trade_learning"
EVIDENCE_VALID_FROM = "2026-09-15"
PAIRS: tuple[tuple[str, str], ...] = (("F", "D"), ("F2", "D"), ("F2", "F"), ("F", "E"), ("F2", "E"), ("F2", "D2"))
FORBIDDEN_WORDS = ("validated", "ready", "approved", "profitable strategy", "deploy")


def group_entries(trades: list[dict[str, Any]]) -> dict[tuple[str, str, str, str], dict[str, float]]:
    """{(exchange, symbol, open_date, direction): {strategy: pnl_r}} over CLOSED rows.
    A strategy that somehow has two closed rows on one key keeps the first (oldest id)."""
    groups: dict[tuple[str, str, str, str], dict[str, float]] = defaultdict(dict)
    for t in sorted(trades, key=lambda r: int(r.get("id") or 0)):
        v = _pnl(t)
        if v is None or not t.get("close_date"):
            continue
        k = (str(t.get("exchange") or "").lower(), str(t.get("symbol") or ""),
             str(t.get("open_date") or ""), str(t.get("direction") or "").lower())
        s = str(t.get("strategy") or "")
        groups[k].setdefault(s, float(v))
    return dict(groups)


def _boot_p(deltas: list[float], seed: int = 7, n: int = 4000) -> float | None:
    if not deltas:
        return None
    rng = np.random.default_rng(seed)
    arr = np.asarray(deltas, dtype=float)
    boots = rng.choice(arr, size=(n, len(arr)), replace=True).mean(axis=1)
    return round(float((boots > 0).mean()), 3)


def pair_stats(groups: dict, a: str, b: str, *, since: str | None = None, before: str | None = None) -> dict[str, Any]:
    """Paired delta = R(a) - R(b) over entries that hold BOTH exits."""
    deltas, keys = [], []
    for k, exits in groups.items():
        if a in exits and b in exits:
            od = k[2]
            if since and od < since:
                continue
            if before and od >= before:
                continue
            deltas.append(exits[a] - exits[b])
            keys.append(k)
    if not deltas:
        return {"n": 0}
    return {
        "n": len(deltas),
        "mean_delta_R": round(statistics.fmean(deltas), 3),
        "sum_delta_R": round(sum(deltas), 2),
        "p_positive": _boot_p(deltas),
        "a_mean_R": round(statistics.fmean(groups[k][a] for k in keys), 3),
        "b_mean_R": round(statistics.fmean(groups[k][b] for k in keys), 3),
        "a_wins": sum(1 for d in deltas if d > 0),
        "b_wins": sum(1 for d in deltas if d < 0),
    }


def best_of_bias(groups: dict, *, since: str | None = None) -> dict[str, Any]:
    """Mean of the best-R row per entry vs the mean of each strategy's own row on the
    SAME entries: how much the dedup-best convention flatters the journal."""
    fam = ("D", "F", "F2")
    best, own = [], defaultdict(list)
    for k, exits in groups.items():
        present = [s for s in fam if s in exits]
        if len(present) < 2 or (since and k[2] < since):
            continue
        best.append(max(exits[s] for s in present))
        for s in present:
            own[s].append(exits[s])
    if not best:
        return {"n_entries": 0}
    return {
        "n_entries": len(best),
        "best_of_mean_R": round(statistics.fmean(best), 3),
        "own_mean_R": {s: round(statistics.fmean(v), 3) for s, v in own.items()},
        "all_rows_mean_R": round(statistics.fmean(x for v in own.values() for x in v), 3),
    }


def build(trades: list[dict[str, Any]], as_of: str) -> dict[str, Any]:
    groups = group_entries(trades)
    multi = {k: v for k, v in groups.items() if len(v) >= 2}
    out: dict[str, Any] = {
        "as_of": as_of, "banner": BANNER,
        "entries_closed": len(groups), "entries_with_2plus_exits": len(multi),
        "pairs": {}, "best_of_bias": {
            "all": best_of_bias(groups), "post_fix": best_of_bias(groups, since=EVIDENCE_VALID_FROM)},
    }
    for a, b in PAIRS:
        out["pairs"][f"{a}-{b}"] = {
            "all": pair_stats(groups, a, b),
            "retired_pre_fix": pair_stats(groups, a, b, before=EVIDENCE_VALID_FROM),
            "post_fix": pair_stats(groups, a, b, since=EVIDENCE_VALID_FROM),
        }
    return out


def render(res: dict[str, Any]) -> str:
    L = [f"# Paired exit experiment (D / F / F2 on the same entry) — {res['as_of']}", "",
         f"**{BANNER}**", "",
         "Each closed entry (exchange, symbol, open_date, direction) that the bot booked under more than "
         "one strategy is one signal with several exits. Delta = R(first) − R(second) on the same entry; "
         "p = bootstrap probability that the mean delta is positive. The post-fix window is the only "
         "admissible evidence; the retired window is history.", "",
         f"- closed entries {res['entries_closed']} · with two or more exits {res['entries_with_2plus_exits']}", "",
         "| pair | window | n | mean ΔR | sum ΔR | p(Δ>0) | first mean R | second mean R | first wins / second wins |",
         "|---|---|---|---|---|---|---|---|---|"]
    for name, w in res["pairs"].items():
        for win, st in w.items():
            if st.get("n", 0) == 0:
                L.append(f"| {name} | {win} | 0 | - | - | - | - | - | - |")
            else:
                L.append(f"| {name} | {win} | {st['n']} | {st['mean_delta_R']:+.3f} | {st['sum_delta_R']:+.2f} | "
                         f"{st['p_positive']} | {st['a_mean_R']:+.3f} | {st['b_mean_R']:+.3f} | {st['a_wins']} / {st['b_wins']} |")
    L += ["", "## Best-of-three bias in the journal's dedup", "",
          "The learning report and the ledger collapse mirrored rows to one signal by keeping the best-R row. "
          "When D, F and F2 hold the same entry, that is the best of up to three exits, not a trade anyone took.", ""]
    for win, b in res["best_of_bias"].items():
        if b.get("n_entries", 0) == 0:
            L.append(f"- {win}: no multi-exit entries")
        else:
            own = ", ".join(f"{s} {v:+.3f}" for s, v in b["own_mean_R"].items())
            L.append(f"- {win}: {b['n_entries']} entries · best-of mean {b['best_of_mean_R']:+.3f}R · "
                     f"own rows {own} · all rows {b['all_rows_mean_R']:+.3f}R")
    L += ["", "## Reading it", "",
          "- A pair with p ≥ 0.9 on the post-fix window and the same sign on the retired window is a real "
          "difference between two exits on identical entries; anything else is noise at this n.",
          "- This is evidence about exits only. It cannot say whether the entry has an edge.",
          "- Nothing here is applied. A persistent, same-sign difference is a candidate for the ledger as a "
          "partial / ladder hypothesis, forward-scored like every other.", "",
          f"_{BANNER}_", ""]
    return "\n".join(L)


def forbidden_words_found(text: str) -> list[str]:
    low = text.lower()
    return [w for w in FORBIDDEN_WORDS if w in low]


def _register_manual_entry() -> None:
    try:
        import database as db
        db.upsert_manual_entry(
            "trade_exit_pairs", module_name="Paired Exit Experiment (D/F/F2)", category="Trading",
            status="live",
            short_description="Scores the paper bot's own paired exit experiment: the same entry booked "
                              "under D, F and F2 with three different exits, compared pairwise.",
            how_it_works="Groups closed trades.db rows by (exchange, symbol, open_date, direction); per pair "
                         "of strategies computes the R difference on identical entries with a bootstrap p; "
                         "split at the 2026-09-15 evidence cutoff; also measures the best-of-three dedup bias.",
            when_to_use="When asking whether one exit rule beats another on the bot's own trades. Observation "
                        "only; nothing applied.",
            user_action="Run `.venv\\Scripts\\python tools\\trade_exit_pairs.py`; read "
                        "reports/trade_learning/exit_pairs.md or the Trade Loop dashboard page.",
            sort_order=95)
    except Exception:
        pass


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Paired exit experiment (observation only)")
    ap.add_argument("--db", default=None, help="trades.db path (default: external root)")
    ap.add_argument("--as-of", default=datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    ap.add_argument("--out-dir", default=str(REPORT_DIR))
    a = ap.parse_args(argv)
    db_path = Path(a.db) if a.db else external_root().joinpath(*_REL_TRADES_DB)
    trades, _ = load_journal_ro(db_path)
    res = build(trades, a.as_of)
    md = render(res)
    bad = forbidden_words_found(md)
    if bad:
        print(f"WARNING forbidden words in render: {bad}")
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "exit_pairs.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    (out / "exit_pairs.md").write_text(md, encoding="utf-8")
    _register_manual_entry()
    print(BANNER)
    print(f"entries {res['entries_closed']} · multi-exit {res['entries_with_2plus_exits']} · wrote {out / 'exit_pairs.md'}")
    for name, w in res["pairs"].items():
        st = w["post_fix"]
        if st.get("n"):
            print(f"  {name} post-fix n={st['n']} mean dR={st['mean_delta_R']:+.3f} p={st['p_positive']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
