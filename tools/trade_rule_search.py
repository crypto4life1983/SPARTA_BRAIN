"""Phase 3 of the self-improving trading loop: bounded rule search with multiple-testing
deflation. READ ONLY · OBSERVATION ONLY · NO LIVE READINESS CLAIM · NO STRATEGY APPROVAL ·
NO BROKER / NO ORDER.

What it does
------------
Scans the PAPER trade journal (read-only) for cells where the realized R is unusually
negative — regime × direction, strategy × direction, strategy × regime, exchange, weekday,
holding-day bucket — and proposes at most MAX_NEW_PER_WEEK new "block this cell" hypotheses to
the hypothesis ledger, which then scores them FORWARD only (tools/trade_hypothesis_ledger.py).

Honesty controls
----------------
* every cell is tested, and the count of cells tested (M) deflates every p-value
  (Bonferroni: p_adj = min(1, p × M)); a cell is proposed only if p_adj <= P_ADJ_MAX and it
  has at least MIN_CELL_SIGNALS dedup signals;
* significance is a permutation test (PERMUTATIONS shuffles of R across signals, fixed seed),
  not a parametric assumption;
* only NEGATIVE cells become hypotheses (a "block" rule is a counterfactual the ledger can
  score on future trades; "prefer" rules are not);
* at most MAX_NEW_PER_WEEK registrations per ISO week, so the ledger cannot flood itself;
* in-sample discovery evidence is frozen at registration and never used for promotion.
"""
from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tools import trade_hypothesis_ledger as thl  # noqa: E402
from tools.trade_journal_adapter import _REL_TRADES_DB, external_root  # noqa: E402
from tools.trade_journal_learning_report import (  # noqa: E402
    BANNER,
    _pnl,
    _signal_key,
    load_journal_ro,
)

REPORT_DIR = _REPO_ROOT / "reports" / "trade_learning"
JSON_NAME = "rule_search.json"
MD_NAME = "rule_search.md"
HISTORY_NAME = "rule_search_history.jsonl"

CUTS: tuple[tuple[str, ...], ...] = (
    ("regime_at_open", "direction"),
    ("strategy", "direction"),
    ("strategy", "regime_at_open"),
    ("exchange",),
    ("weekday",),
    ("hold_bucket",),
)
MIN_CELL_SIGNALS = 5
P_ADJ_MAX = 0.10
PERMUTATIONS = 2000
SEED = 42
MAX_NEW_PER_WEEK = 3
FORBIDDEN_WORDS = ("validated", "ready", "approved", "profitable strategy", "deploy")


# ── data prep ──────────────────────────────────────────────────────────────

def dedup_signals(trades: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """One row per open_date+symbol+direction: the best-R closed row (consistent with the
    learning report's dedup_best)."""
    best: dict[tuple[str, str, str], dict[str, Any]] = {}
    for t in trades:
        v = _pnl(t)
        if v is None:
            continue
        k = _signal_key(t)
        if k not in best or v > (_pnl(best[k]) or float("-inf")):
            best[k] = t
    return sorted(best.values(), key=lambda t: (str(t.get("open_date")), str(t.get("symbol")), str(t.get("direction"))))


def cell_key(trade: dict[str, Any], fields: tuple[str, ...]) -> tuple[tuple[str, str], ...] | None:
    out = []
    for f in fields:
        v = thl.trade_field(trade, f)
        if v is None:
            return None
        out.append((f, str(v)))
    return tuple(out)


def hypothesis_id(cell: tuple[tuple[str, str], ...]) -> str:
    return "blockwhere__" + "__".join(f"{f}={v}" for f, v in cell)


# ── statistics ─────────────────────────────────────────────────────────────

def permutation_p_negative(cell_vals: list[float], all_vals: list[float], n_perm: int = PERMUTATIONS,
                           seed: int = SEED) -> float:
    """One-sided p-value: probability that a random cell of the same size drawn from all
    signals has a mean <= the observed cell mean."""
    obs = statistics.fmean(cell_vals)
    k = len(cell_vals)
    rng = random.Random(seed)
    pool = list(all_vals)
    hits = 0
    for _ in range(n_perm):
        samp = rng.sample(pool, k)
        if statistics.fmean(samp) <= obs:
            hits += 1
    return (hits + 1) / (n_perm + 1)


def scan_cells(signals: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Every cell with >= MIN_CELL_SIGNALS signals, with raw and Bonferroni-adjusted p."""
    all_vals = [float(_pnl(t)) for t in signals]
    cells: dict[tuple[tuple[str, str], ...], list[float]] = defaultdict(list)
    for t in signals:
        for fields in CUTS:
            k = cell_key(t, fields)
            if k is not None:
                cells[k].append(float(_pnl(t)))
    tested = {k: v for k, v in cells.items() if len(v) >= MIN_CELL_SIGNALS}
    m = len(tested)
    rows: list[dict[str, Any]] = []
    for k, vals in sorted(tested.items(), key=lambda kv: statistics.fmean(kv[1])):
        mean = statistics.fmean(vals)
        p = permutation_p_negative(vals, all_vals) if mean < 0 else 1.0
        rows.append({
            "cell": dict(k),
            "id": hypothesis_id(k),
            "n_signals": len(vals),
            "sum_R": round(sum(vals), 3),
            "mean_R": round(mean, 4),
            "win_rate": round(sum(v > 0 for v in vals) / len(vals), 3),
            "p_raw": round(p, 4),
            "p_adj": round(min(1.0, p * m), 4),
            "cells_tested": m,
            "candidate": bool(mean < 0 and min(1.0, p * m) <= P_ADJ_MAX),
        })
    return rows


# ── registration budget ────────────────────────────────────────────────────

def iso_week(d: str) -> str:
    y, w, _ = date.fromisoformat(d).isocalendar()
    return f"{y}-W{w:02d}"


def registrations_this_week(ledger: dict[str, Any], as_of: str) -> int:
    wk = iso_week(as_of)
    n = 0
    for h in ledger.get("hypotheses", {}).values():
        if str(h.get("id", "")).startswith("blockwhere__") and iso_week(h.get("registered_as_of", as_of)) == wk:
            n += 1
    return n


def propose(rows: list[dict[str, Any]], ledger: dict[str, Any], as_of: str) -> list[dict[str, Any]]:
    """Candidates not yet in the ledger, most significant first, capped per ISO week."""
    budget = max(0, MAX_NEW_PER_WEEK - registrations_this_week(ledger, as_of))
    existing = set(ledger.get("hypotheses", {}).keys())
    out: list[dict[str, Any]] = []
    for r in sorted((r for r in rows if r["candidate"]), key=lambda r: (r["p_adj"], r["mean_R"])):
        if r["id"] in existing:
            continue
        if len(out) >= budget:
            break
        out.append({
            "id": r["id"],
            "rule": "block entries where " + ", ".join(f"{f}={v}" for f, v in r["cell"].items()),
            "evidence": {k: r[k] for k in ("n_signals", "sum_R", "mean_R", "win_rate", "p_raw", "p_adj", "cells_tested")},
            "label": "OK" if r["n_signals"] >= 20 else "PRELIMINARY",
            "sample_ok": r["n_signals"] >= 20,
            "status": "SUGGESTION_ONLY",
            "caveat": "observation only; not applied; discovered by search, scored forward only",
        })
    return out


# ── report ─────────────────────────────────────────────────────────────────

def build_report(signals: list[dict[str, Any]], ledger: dict[str, Any], as_of: str) -> dict[str, Any]:
    rows = scan_cells(signals)
    proposals = propose(rows, ledger, as_of)
    return {
        "as_of": as_of,
        "banner": BANNER,
        "n_signals": len(signals),
        "cells_tested": rows[0]["cells_tested"] if rows else 0,
        "controls": {
            "min_cell_signals": MIN_CELL_SIGNALS, "p_adj_max": P_ADJ_MAX, "permutations": PERMUTATIONS,
            "seed": SEED, "max_new_per_week": MAX_NEW_PER_WEEK, "correction": "bonferroni",
        },
        "cells": rows,
        "proposals": proposals,
        "registrations_this_week_before": registrations_this_week(ledger, as_of),
    }


def render_markdown(rep: dict[str, Any]) -> str:
    L = [f"# Rule search — {rep['as_of']}", "", rep["banner"], "",
         f"Signals (dedup): {rep['n_signals']} · cells tested: {rep['cells_tested']} · "
         f"correction: Bonferroni · p_adj ≤ {rep['controls']['p_adj_max']} · "
         f"budget {rep['controls']['max_new_per_week']}/week", "",
         "## Proposals this run", ""]
    if rep["proposals"]:
        L += ["| id | n | mean R | p_raw | p_adj |", "|---|---|---|---|---|"]
        for p in rep["proposals"]:
            e = p["evidence"]
            L.append(f"| `{p['id']}` | {e['n_signals']} | {e['mean_R']} | {e['p_raw']} | {e['p_adj']} |")
    else:
        L.append("None. No cell survived the multiple-testing correction, or the weekly budget is used.")
    L += ["", "## Most negative cells (all tested)", "", "| cell | n | mean R | win | p_raw | p_adj | candidate |",
          "|---|---|---|---|---|---|---|"]
    for r in rep["cells"][:15]:
        cell = ", ".join(f"{f}={v}" for f, v in r["cell"].items())
        L.append(f"| {cell} | {r['n_signals']} | {r['mean_R']} | {r['win_rate']} | {r['p_raw']} | {r['p_adj']} | {r['candidate']} |")
    L += ["", "A proposal is a hypothesis for the ledger, scored only on trades that close after it "
          "was registered. Discovery evidence is frozen and never promotes anything. Nothing is applied."]
    return "\n".join(L) + "\n"


def forbidden_words_found(text: str) -> list[str]:
    low = text.lower()
    return [w for w in FORBIDDEN_WORDS if w in low]


# ── cycle ──────────────────────────────────────────────────────────────────

def run_cycle(trades: list[dict[str, Any]], as_of: str, ledger_path: Path = thl.LEDGER_PATH,
              report_dir: Path = REPORT_DIR) -> dict[str, Any]:
    ledger = thl.load_ledger(ledger_path)
    signals = dedup_signals(trades)
    rep = build_report(signals, ledger, as_of)
    added = thl.register_from_report({"suggestions": rep["proposals"]}, as_of, ledger) if rep["proposals"] else []
    rep["registered"] = added
    if added:
        thl.save_ledger(ledger, ledger_path)
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / JSON_NAME).write_text(json.dumps(rep, indent=2, sort_keys=True), encoding="utf-8")
    (report_dir / MD_NAME).write_text(render_markdown(rep), encoding="utf-8")
    with (report_dir / HISTORY_NAME).open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"as_of": as_of, "n_signals": rep["n_signals"], "cells_tested": rep["cells_tested"],
                             "proposals": [p["id"] for p in rep["proposals"]], "registered": added}) + "\n")
    return rep


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Bounded rule search over the paper journal (observation only)")
    ap.add_argument("--as-of", default=datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    args = ap.parse_args(argv)
    db_path = external_root().joinpath(*_REL_TRADES_DB)
    if not db_path.exists():
        print(f"trades.db not found: {db_path}")
        return 2
    trades, _ = load_journal_ro(db_path)
    rep = run_cycle(trades, args.as_of)
    print(BANNER)
    print(f"signals={rep['n_signals']} cells_tested={rep['cells_tested']} proposals={[p['id'] for p in rep['proposals']]} registered={rep['registered']}")
    try:  # system manual row; never fail the run because of it
        import database as db
        db.upsert_manual_entry(
            "trade_rule_search", module_name="Trade Rule Search (bounded, deflated)", category="Trading",
            status="live",
            short_description="Daily bounded search for negative journal cells; Bonferroni-deflated permutation test; ≤3 new block hypotheses/week into the ledger.",
            how_it_works="tools/trade_rule_search.py dedups signals, tests regime/strategy/direction/exchange/weekday/holding cells (n≥5), proposes only p_adj≤0.10 negative cells; the ledger scores them forward only.",
            user_action="Read reports/trade_learning/rule_search.md; proposals are hypotheses, not rules; nothing is applied.",
        )
    except Exception as exc:  # pragma: no cover
        print(f"manual entry skipped: {exc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
