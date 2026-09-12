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
                L.append(f"| `{hid}` | APPLIED {ap.get('applied_as_of', '')} | {h.get('registered_as_of')} | "
                         f"{ap.get('n_after', 0)} after | {_f(ap.get('mean_R_after'))} vs base {_f(ap.get('baseline_mean_R'))} | "
                         f"{_f(ap.get('p_after_ge_baseline'))} | rollback check at n≥20{flag} |")
                continue
            nxt = (f"n≥{th.get('min_forward_signals', '?')} & p≥{th.get('min_p_positive', '?')}"
                   if h.get("status") in ("SHADOW", "CONFIRMED") else "terminal")
            L.append(f"| `{hid}` | {h.get('status')} | {h.get('registered_as_of')} | {fw.get('n_signals', 0)} | "
                     f"{_f(fw.get('delta_R_mean'))} | {_f(fw.get('bootstrap_p_positive'))} | {nxt} |")
        n_conf = sum(1 for h in hyps.values() if h.get("status") == "CONFIRMED")
        L += ["", f"CONFIRMED rules awaiting the operator: **{n_conf}**. A CONFIRMED rule is a recommendation "
              "to change the paper bot; nothing is applied by the loop."]
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
        if r.get("status") == "REJECTED":
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
