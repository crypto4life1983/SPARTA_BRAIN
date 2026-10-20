"""tools/ledger_calibration.py — How well is the hypothesis ledger learning? (observation only)

READ ONLY · OBSERVATION ONLY · NO LIVE READINESS CLAIM · NO STRATEGY APPROVAL · NO BROKER / NO ORDER

Reads data/trade_hypothesis_ledger.json and reports/trade_learning/hypothesis_history.jsonl and
writes reports/trade_learning/ledger_calibration.{md,json}. Per hypothesis: registration date, kind,
status, days since registration, forward n, days to any verdict, forward-evidence accrual rate
(signals per 30 days), projected days to the n >= 20 floor at that rate, and whether the sign of the
frozen in-sample evidence agrees with the sign of the forward delta. If
reports/trade_learning/replay_priors.json exists (produced elsewhere) its prior per hypothesis is
shown too; this tool never creates it.

Sign mapping for the frozen in-sample evidence (expected sign of the rule's delta_R if the evidence
were right):
  block / block_where : -avg_R or -mean_R of the trades the rule would remove
                        (-short_mean_R for the D-short record)
  stop_cap            : +total_excess_loss_R (the cap would have saved that much)
  partial             : mean_delta_R
  partial_2R          : mean_MFE_R - mean_realized_R (room the partial would capture)
  extend_timeout      : sum_delta_R / n_resolved, undefined when n_resolved == 0
  unblock             : mean_hyp_R of the resolved blocks the rule would admit
"""
from __future__ import annotations

import json
import statistics
import sys
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
LEDGER_PATH = ROOT / "data" / "trade_hypothesis_ledger.json"
HISTORY_PATH = ROOT / "reports" / "trade_learning" / "hypothesis_history.jsonl"
PRIORS_PATH = ROOT / "reports" / "trade_learning" / "replay_priors.json"
OUT_MD = ROOT / "reports" / "trade_learning" / "ledger_calibration.md"
OUT_JSON = ROOT / "reports" / "trade_learning" / "ledger_calibration.json"

BANNER = "READ ONLY · OBSERVATION ONLY · NO LIVE READINESS CLAIM · NO STRATEGY APPROVAL · NO BROKER / NO ORDER"
FLOOR_N = 20
VERDICT_STATUSES = ("CONFIRMED", "REJECTED", "APPLIED")


def _sign(x: float | None) -> str | None:
    if x is None:
        return None
    return "+" if x > 0 else ("-" if x < 0 else "0")


def in_sample_sign(hyp: dict[str, Any]) -> tuple[str | None, str]:
    """(sign, how it was derived) for the frozen in-sample evidence."""
    ev = hyp.get("registered_evidence") or {}
    kind = hyp.get("kind")
    if kind in ("block", "block_where"):
        for key in ("avg_R", "mean_R", "short_mean_R"):
            if ev.get(key) is not None:
                return _sign(-float(ev[key])), f"-{key}"
        return None, "no mean field"
    if kind == "stop_cap":
        v = ev.get("total_excess_loss_R")
        return (_sign(float(v)) if v is not None else None), "+total_excess_loss_R"
    if kind == "partial":
        v = ev.get("mean_delta_R")
        return (_sign(float(v)) if v is not None else None), "mean_delta_R"
    if kind == "partial_2R":
        if ev.get("mean_MFE_R") is not None and ev.get("mean_realized_R") is not None:
            return _sign(float(ev["mean_MFE_R"]) - float(ev["mean_realized_R"])), "mean_MFE_R - mean_realized_R"
        return None, "no MFE/realized fields"
    if kind == "extend_timeout":
        n = ev.get("n_resolved") or 0
        if n and ev.get("sum_delta_R") is not None:
            return _sign(float(ev["sum_delta_R"]) / float(n)), "sum_delta_R / n_resolved"
        return None, "n_resolved == 0"
    if kind == "unblock":
        v = ev.get("mean_hyp_R")
        return (_sign(float(v)) if v is not None else None), "mean_hyp_R"
    return None, f"unmapped kind {kind}"


def agreement(in_sign: str | None, fwd_mean: float | None) -> str:
    if fwd_mean is None:
        return "no forward data"
    if in_sign is None:
        return "no in-sample sign"
    f = _sign(fwd_mean)
    if f == "0" or in_sign == "0":
        return "flat"
    return "agree" if f == in_sign else "disagree"


def days_to_verdict(hyp: dict[str, Any], history_lines: list[dict[str, Any]]) -> int | None:
    """Days from registration to the first CONFIRMED/REJECTED/APPLIED, from the hypothesis history
    list first, else from the nightly history's status_changes."""
    reg = date.fromisoformat(hyp["registered_as_of"])
    for h in hyp.get("history") or []:
        if h.get("status") in VERDICT_STATUSES and h.get("as_of"):
            return (date.fromisoformat(h["as_of"]) - reg).days
    for line in history_lines:
        for ch in line.get("status_changes") or []:
            sid = ch.get("id") if isinstance(ch, dict) else None
            st = ch.get("to") or ch.get("status") if isinstance(ch, dict) else None
            if sid == hyp["id"] and st in VERDICT_STATUSES and line.get("as_of"):
                return (date.fromisoformat(line["as_of"]) - reg).days
    return None


def accrual(n: int, days: int) -> float:
    return round(n / max(days, 1) * 30.0, 2)


def projected_days_to_floor(n: int, rate_per_30d: float) -> str:
    if n >= FLOOR_N:
        return "reached"
    if rate_per_30d <= 0:
        return "never at current rate"
    return str(int(round((FLOOR_N - n) / rate_per_30d * 30.0)))


def load_history(path: Path) -> list[dict[str, Any]]:
    lines: list[dict[str, Any]] = []
    if not path.exists():
        return lines
    for raw in path.read_text(encoding="utf-8").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        try:
            lines.append(json.loads(raw))
        except json.JSONDecodeError:
            continue
    return lines


def load_priors(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def build(ledger: dict[str, Any], history_lines: list[dict[str, Any]], as_of: str,
          priors: dict[str, Any] | None) -> dict[str, Any]:
    today = date.fromisoformat(as_of)
    rows = []
    for sid in sorted(ledger["hypotheses"]):
        h = ledger["hypotheses"][sid]
        reg = date.fromisoformat(h["registered_as_of"])
        days = (today - reg).days
        fwd = h.get("forward") or {}
        ap = h.get("applied") or {}
        if h.get("status") == "APPLIED" and ap.get("applied_as_of"):
            # An applied rule is judged on post-apply closes (applied.n_after), not on the
            # counterfactual forward block, which the ledger leaves untouched once applied.
            n = int(ap.get("n_after") or 0)
            days_for_rate = (today - date.fromisoformat(ap["applied_as_of"])).days
            fwd_mean = ap.get("mean_R_after")
            n_source = "applied.n_after (post-apply closes)"
        else:
            n = int(fwd.get("n_signals") or 0)
            days_for_rate = days
            fwd_mean = fwd.get("delta_R_mean")
            n_source = "forward.n_signals"
        rate = accrual(n, days_for_rate)
        in_sign, how = in_sample_sign(h)
        prior = (priors or {}).get(sid) if priors else None
        rows.append({
            "id": sid,
            "kind": h.get("kind"),
            "status": h.get("status"),
            "registered_as_of": h["registered_as_of"],
            "days_since_registration": days,
            "forward_n": n,
            "forward_n_source": n_source,
            "forward_delta_R_mean": fwd_mean,
            "days_to_verdict": days_to_verdict(h, history_lines),
            "accrual_per_30d": rate,
            "projected_days_to_floor": projected_days_to_floor(n, rate),
            "in_sample_sign": in_sign,
            "in_sample_sign_source": how,
            "sign_agreement": agreement(in_sign, fwd_mean),
            "applied_n_after": ap.get("n_after") if h.get("status") == "APPLIED" else None,
            "applied_regression_flag": ap.get("regression_flag") if h.get("status") == "APPLIED" else None,
            "replay_prior_delta_R_mean": (prior or {}).get("prior_delta_R_mean") if prior else None,
            "replay_prior_stable": (prior or {}).get("stable") if prior else None,
        })
    by_status: dict[str, int] = {}
    for r in rows:
        by_status[r["status"]] = by_status.get(r["status"], 0) + 1
    rates = [r["accrual_per_30d"] for r in rows]
    applied = [r for r in rows if r["status"] == "APPLIED"]
    totals = {
        "as_of": as_of,
        "n_hypotheses": len(rows),
        "by_status": by_status,
        "median_accrual_per_30d": round(statistics.median(rates), 2) if rates else 0.0,
        "share_with_forward_evidence": round(sum(1 for r in rows if r["forward_n"] > 0) / len(rows), 2) if rows else 0.0,
        "never_reach_floor_at_current_rate": [r["id"] for r in rows if r["projected_days_to_floor"] == "never at current rate"],
        "applied_under_rollback_check": len(applied),
        "applied_n_after": {r["id"]: r["applied_n_after"] for r in applied},
        "sign_agreement_counts": {k: sum(1 for r in rows if r["sign_agreement"] == k)
                                  for k in ("agree", "disagree", "flat", "no forward data", "no in-sample sign")},
        "nightly_runs_on_record": len(history_lines),
        "replay_priors_file": "present" if priors is not None else "absent",
    }
    return {"banner": BANNER, "totals": totals, "rows": rows}


def _f(x: Any) -> str:
    if x is None:
        return "-"
    if isinstance(x, float):
        return f"{x:+.3f}" if abs(x) < 100 else f"{x:.0f}"
    return str(x)


def render_markdown(rep: dict[str, Any]) -> str:
    t = rep["totals"]
    L = [
        f"# Hypothesis ledger calibration — {t['as_of']}",
        "",
        f"**{BANNER}**",
        "",
        "How fast the loop gathers forward evidence per hypothesis, how long verdicts take, and whether the "
        "frozen in-sample evidence has so far pointed the same way as the forward counterfactual. This "
        "measures the machine's judging, not the trades.",
        "",
        "## Loop totals",
        "",
        f"- hypotheses {t['n_hypotheses']} · by status {json.dumps(t['by_status'], sort_keys=True)} · nightly runs on record {t['nightly_runs_on_record']}",
        f"- median forward accrual {t['median_accrual_per_30d']} signals per 30 days · share with any forward evidence {t['share_with_forward_evidence']}",
        f"- cannot reach the n >= {FLOOR_N} floor at the current rate: {', '.join(t['never_reach_floor_at_current_rate']) or 'none'}",
        f"- APPLIED rules under the rollback check: {t['applied_under_rollback_check']} · post-apply n: {json.dumps(t['applied_n_after'], sort_keys=True)}",
        f"- in-sample vs forward sign: {json.dumps(t['sign_agreement_counts'], sort_keys=True)}",
        f"- replay priors file (reports/trade_learning/replay_priors.json): {t['replay_priors_file']}",
        "",
        "## Per hypothesis",
        "",
        "| id | kind | status | registered | days | fwd n | fwd mean ΔR | per 30d | days to n>=20 | days to verdict | in-sample sign (source) | agreement | replay prior |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in rep["rows"]:
        prior = "-" if r["replay_prior_delta_R_mean"] is None else f"{_f(r['replay_prior_delta_R_mean'])} ({'stable' if r['replay_prior_stable'] else 'unstable'})"
        L.append(
            f"| {r['id']} | {r['kind']} | {r['status']} | {r['registered_as_of']} | {r['days_since_registration']} | "
            f"{r['forward_n']} | {_f(r['forward_delta_R_mean'])} | {r['accrual_per_30d']} | {r['projected_days_to_floor']} | "
            f"{_f(r['days_to_verdict'])} | {r['in_sample_sign'] or '-'} ({r['in_sample_sign_source']}) | {r['sign_agreement']} | {prior} |"
        )
    L += [
        "",
        "## Reading it",
        "",
        "- *per 30d* is forward signals accrued per 30 days since registration; *days to n>=20* projects the "
        "pre-registered floor at that rate. A row that says never at current rate is a hypothesis the paper "
        "book is not producing trades for; it cannot be judged forward without more evidence flow.",
        "- For an APPLIED rule *fwd n* and *fwd mean* are the post-apply closes and their mean R "
        "(applied.n_after / mean_R_after, the rollback-check sample), counted from the apply date; for "
        "the others they are the counterfactual forward signals since registration.",
        "- *agreement* compares the sign the frozen in-sample evidence implied for the rule with the sign of "
        "the forward counterfactual so far (for APPLIED rules: with the sign of the post-apply mean R, which "
        "is the system's result, not the rule's, so read it loosely). Small n makes this noisy; it is a "
        "calibration trace, not a verdict.",
        "- Nothing here changes a status, a threshold or the paper bot.",
        "",
        f"_{BANNER}_",
        "",
    ]
    return "\n".join(L)


def main(argv: list[str] | None = None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Hypothesis ledger calibration (observation only)")
    ap.add_argument("--as-of", default=date.today().isoformat())
    ap.add_argument("--ledger", default=str(LEDGER_PATH))
    ap.add_argument("--history", default=str(HISTORY_PATH))
    ap.add_argument("--priors", default=str(PRIORS_PATH))
    ap.add_argument("--out-md", default=str(OUT_MD))
    ap.add_argument("--out-json", default=str(OUT_JSON))
    a = ap.parse_args(argv)
    ledger = json.loads(Path(a.ledger).read_text(encoding="utf-8"))
    rep = build(ledger, load_history(Path(a.history)), a.as_of, load_priors(Path(a.priors)))
    md = render_markdown(rep)
    sys.path.insert(0, str(ROOT))
    from tools.trade_hypothesis_ledger import forbidden_words_found
    bad = forbidden_words_found(md)
    if bad:
        print(f"WARNING forbidden words in output: {bad}")
    Path(a.out_md).write_text(md, encoding="utf-8")
    Path(a.out_json).write_text(json.dumps(rep, indent=1), encoding="utf-8")
    print(BANNER)
    print(f"wrote {a.out_md}, {a.out_json}")
    print(json.dumps(rep["totals"], indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
