"""One-page daily digest of the self-improving trading loop.

Reads the three loop artifacts (learning report, hypothesis ledger, rule search, paper-system
scorecard) and writes reports/trade_learning/LOOP_STATUS.md so the operator reads ONE page.
READ ONLY · OBSERVATION ONLY · NO LIVE READINESS CLAIM · NO STRATEGY APPROVAL · NO BROKER / NO ORDER.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

REPORT_DIR = _REPO_ROOT / "reports" / "trade_learning"
LEDGER_PATH = _REPO_ROOT / "data" / "trade_hypothesis_ledger.json"
OUT_NAME = "LOOP_STATUS.md"
BANNER = "READ ONLY · OBSERVATION ONLY · NO LIVE READINESS CLAIM · NO STRATEGY APPROVAL · NO BROKER / NO ORDER"
FORBIDDEN_WORDS = ("validated", "ready", "approved", "profitable strategy", "deploy")
# Below this many admissible forward trades, the headline expectancy is carried
# almost entirely by the retired pre-partial-bar-fix record, so the digest says
# so explicitly. Matches MIN_SIGNALS in trade_journal_learning_report.py.
MIN_VALID_EVIDENCE = 30
# Mirrors APPLIED_MIN_N / EVIDENCE_VALID_FROM in trade_hypothesis_ledger.py;
# used only for wording in section 2.
MIN_APPLIED_N = 20
EVIDENCE_VALID_FROM = "2026-09-15"


def _load(path: Path) -> dict[str, Any] | list | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _f(v: Any, nd: int = 3) -> str:
    if v is None:
        return "-"
    if isinstance(v, float):
        return f"{v:.{nd}f}"
    return str(v)


def _evidence_split_lines(ev: dict[str, Any] | None) -> list[str]:
    """One-glance pre/post partial-bar-fix split for section 1.

    The line above it counts every closed trade, including the ones the
    operator retired from evidence. Without this, a voided record reads as a
    live track record. Observation only."""
    if not ev:
        return []
    v, rt = ev.get("valid_forward") or {}, ev.get("retired") or {}
    lines = [
        f"- **valid forward evidence (opened on/after {ev.get('cutoff')})**: "
        f"closed {v.get('closed')} · sum R {_f(v.get('sum_R_raw'))} · "
        f"expectancy {_f(v.get('expectancy_R'))} R · win rate {_f(v.get('win_rate'))}",
        f"- retired (opened before {ev.get('cutoff')}, {ev.get('cutoff_field')}): "
        f"closed {rt.get('closed')} · sum R {_f(rt.get('sum_R_raw'))} · "
        f"expectancy {_f(rt.get('expectancy_R'))} R — "
        f"{rt.get('outcome_WIN')} WIN vs {rt.get('outcome_TIMEOUT_positive')} "
        f"profitable TIMEOUT",
    ]
    if (v.get("closed") or 0) < MIN_VALID_EVIDENCE:
        lines.append(
            f"- ⚠ the expectancy/win-rate on the line above is computed over ALL "
            f"closed rows; only {v.get('closed')} of them are admissible forward "
            f"evidence (< {MIN_VALID_EVIDENCE}), so it is NOT a track record of "
            f"the system now running"
        )
    return lines


def build_digest(learning: dict | None, ledger: dict | None, search: dict | None,
                 scorecard: dict | list | None, as_of: str) -> str:
    L = [f"# Trading loop status — {as_of}", "", BANNER, ""]

    # 1. journal
    L += ["## 1. Journal (paper bot) — what the last learning pass measured", ""]
    if learning:
        c = learning.get("counts", {})
        L += [f"- closed rows {c.get('closed')} · distinct signals {c.get('distinct_signals_closed')} · "
              f"sum R (dedup best) {_f(c.get('sum_R_dedup_best'))} · expectancy {_f(c.get('expectancy_R'))} R · "
              f"win rate {_f(c.get('win_rate'))} · sample label {learning.get('sample_quality', {}).get('overall_label', '-')}",
              f"- suggestions emitted: {len(learning.get('suggestions', []))} (all SUGGESTION_ONLY)"]
        L += _evidence_split_lines(learning.get("evidence_split"))
    else:
        L.append("- learning report missing")

    # 2. ledger
    L += ["", "## 2. Hypotheses under forward test", ""]
    hyps = (ledger or {}).get("hypotheses", {})
    if hyps:
        L += ["| id | status | registered | forward n | mean ΔR | p(>0) | next |", "|---|---|---|---|---|---|---|"]
        for hid, h in sorted(hyps.items(), key=lambda kv: (kv[1].get("status", ""), kv[0])):
            fw = h.get("forward", {})
            th = h.get("thresholds", {})
            if h.get("status") == "APPLIED":
                ap = h.get("applied", {})
                flag = " ⚠ regression" if ap.get("regression_flag") else ""
                retired = ap.get("baseline_is_retired_evidence")
                # Never print "vs base X" as if X were admissible evidence.
                if ap.get("baseline_mean_R") is None:
                    base_cell = "no admissible baseline"
                elif retired:
                    base_cell = f"vs ⚠RETIRED base {_f(ap.get('baseline_mean_R'))}"
                else:
                    base_cell = f"vs base {_f(ap.get('baseline_mean_R'))}"
                nxt = ap.get("rollback_rule") or f"rollback check at n≥{MIN_APPLIED_N}"
                L.append(f"| `{hid}` | APPLIED {ap.get('applied_as_of', '')} | {h.get('registered_as_of')} | "
                         f"{ap.get('n_after', 0)} after | {_f(ap.get('mean_R_after'))} {base_cell} | "
                         f"{_f(ap.get('p_after_ge_baseline'))} | {nxt}{flag} |")
                continue
            nxt = (f"n≥{th.get('min_forward_signals', '?')} & p≥{th.get('min_p_positive', '?')}"
                   if h.get("status") in ("SHADOW", "CONFIRMED") else "terminal")
            L.append(f"| `{hid}` | {h.get('status')} | {h.get('registered_as_of')} | {fw.get('n_signals', 0)} | "
                     f"{_f(fw.get('delta_R_mean'))} | {_f(fw.get('bootstrap_p_positive'))} | {nxt} |")
        n_conf = sum(1 for h in hyps.values() if h.get("status") == "CONFIRMED")
        L += ["", f"CONFIRMED rules awaiting the operator: **{n_conf}**. A CONFIRMED rule is a recommendation "
              "to change the paper bot; nothing is applied by the loop."]
        n_retired = sum(
            1 for h in hyps.values()
            if h.get("status") == "APPLIED"
            and (h.get("applied") or {}).get("baseline_is_retired_evidence")
        )
        if n_retired:
            L += ["", f"⚠ **{n_retired} APPLIED rule(s) are still scored against a baseline frozen from "
                  f"retired pre-{EVIDENCE_VALID_FROM} evidence.** Their rollback check therefore compares "
                  "admissible forward evidence against a record the operator has voided, and will produce a "
                  f"verdict that says nothing about the rule once n reaches {MIN_APPLIED_N}. Re-dating those "
                  "records is a pending operator decision (spec step 4): "
                  "`reports/trade_learning/spec_killswitch_and_ledger_baseline_2026-09-21.md`."]
    else:
        L.append("- no hypotheses registered yet")

    # 3. search
    L += ["", "## 3. Rule search (bounded, multiple-testing corrected)", ""]
    if search:
        props = [p["id"] for p in search.get("proposals", [])]
        L.append(f"- signals {search.get('n_signals')} · cells tested {search.get('cells_tested')} · "
                 f"proposals this run: {props if props else 'none survived correction'}")
        cells = search.get("cells", [])[:3]
        for r in cells:
            cell = ", ".join(f"{f}={v}" for f, v in r["cell"].items())
            L.append(f"  - most negative: {cell} (n={r['n_signals']}, mean {_f(r['mean_R'])} R, p_adj {_f(r['p_adj'])})")
    else:
        L.append("- rule search report missing")

    # 4. paper systems
    L += ["", "## 4. Paper systems vs their own pre-registered gates", ""]
    recs = None
    if isinstance(scorecard, list):
        recs = scorecard
    elif isinstance(scorecard, dict):
        recs = scorecard.get("lines") or scorecard.get("records") or scorecard.get("systems")
    if recs:
        L += ["| line | status | sign | window | reason |", "|---|---|---|---|---|"]
        for r in recs:
            w = r.get("window", {})
            L.append(f"| {r.get('line')} | {r.get('status')} | {r.get('sign')} | "
                     f"{'satisfied' if w.get('satisfied') else 'open'} | {str(r.get('reason', ''))[:110]} |")
    else:
        L.append("- scorecard missing")

    # 5. operator queue
    L += ["", "## 5. Decisions only a human can take", ""]
    queue: list[str] = []
    for hid, h in hyps.items():
        if h.get("status") == "CONFIRMED":
            queue.append(f"apply CONFIRMED rule `{hid}` to the paper bot (spec: bot_rule_changes_spec)")
        if h.get("status") == "APPLIED" and (h.get("applied") or {}).get("regression_flag"):
            ap = h["applied"]
            queue.append(f"consider ROLLBACK of applied rule `{hid}`: post-apply mean R "
                         f"{_f(ap.get('mean_R_after'))} vs baseline {_f(ap.get('baseline_mean_R'))} "
                         f"over {ap.get('n_after')} signals")
    for r in recs or []:
        # A line already closed by a recorded operator decision needs nothing further:
        # asking for its closure again would make it a permanent queue item.
        already_closed = "closed by recorded operator decision" in str(r.get("reason", ""))
        if r.get("status") == "REJECTED" and not already_closed:
            queue.append(f"record closure of {r.get('line')} (REJECTED by its own gates)")
        if r.get("status") == "BLOCKED":
            queue.append(f"unblock or retire {r.get('line')}: {str(r.get('reason', ''))[:80]}")
    if not queue:
        queue.append("none today — the loop is accumulating forward evidence")
    L += [f"- {q}" for q in queue]
    L += ["", "Generated by tools/trade_loop_digest.py. Sources: latest.json, trade_hypothesis_ledger.json, "
          "rule_search.json, paper_systems_scorecard.json."]
    return "\n".join(L) + "\n"


def forbidden_words_found(text: str) -> list[str]:
    low = text.lower()
    return [w for w in FORBIDDEN_WORDS if w in low]


def main() -> int:
    as_of = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    md = build_digest(
        _load(REPORT_DIR / "latest.json"),
        _load(LEDGER_PATH),
        _load(REPORT_DIR / "rule_search.json"),
        _load(REPORT_DIR / "paper_systems_scorecard.json"),
        as_of,
    )
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    (REPORT_DIR / OUT_NAME).write_text(md, encoding="utf-8")
    print(f"wrote {REPORT_DIR / OUT_NAME}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
