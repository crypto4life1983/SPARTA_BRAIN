"""tools/replay_prior.py — an in-sample replay prior for every hypothesis in the ledger.

READ ONLY · OBSERVATION ONLY · NO LIVE READINESS CLAIM · NO STRATEGY APPROVAL · NO BROKER / NO ORDER

The ledger scores hypotheses forward only, on the paper bot's own closes, at ~2-3 closes a
week. This tool gives each hypothesis a fast in-sample prior from the replay of the bot's
own code (tools/replay_bot_rules.py: 42 symbols, 2.7 years, every signal simulated, blocked
or not) so that a plainly bad idea is visible the day it is registered instead of months
later. The prior is rendered next to the forward score and is NEVER used for promotion or
rejection: the pre-registered forward thresholds stay the only verdict.

Per kind:
  block / block_where : delta = -R on replay trades matching the rule (taken trades it would refuse)
  unblock             : delta = +R on replay signals the gate refused for that reason
                        (SLOT_OCCUPIED: allowed signals the one-slot book did not take)
  extend_timeout      : delta = R(40-day) - R(20-day) on trades that timed out at 20 days
  stop_cap / partial  : no replay prior (the replay never breaches the cap; its exits already
                        embed the live partial rule) -> note only
Stability: the sign of the mean delta in each half-year with >= 10 trades must match the
overall sign; `stable` is None when fewer than 2 half-years qualify.

Output: reports/trade_learning/replay_priors.json (+ .md); the ledger render reads the JSON.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tools import trade_hypothesis_ledger as thl  # noqa: E402
from tools.replay_bot_rules import PERIODS, STRATS, dedup, one_slot  # noqa: E402

REPORT_DIR = _REPO_ROOT / "reports" / "trade_learning"
MIN_PERIOD_N = 10
UNBLOCK_REASONS = {
    "TREND_DOWN_BLOCKS_LONG": "regime=TREND_DOWN blocks new longs",
    "TREND_UP_BLOCKS_SHORT": "regime=TREND_UP blocks new shorts",
    "CHOP_BLOCKS_ALL": "regime=CHOP",
    "RANGE_MID": "mid-range",
    "TREND_DOWN_STRATEGY_NOT_D2E2F2": "regime=TREND_DOWN only allows",
}


def load_signals(run_dir: Path) -> list[dict[str, Any]]:
    return json.loads((run_dir / "signals.json").read_text(encoding="utf-8"))


def _hold_bucket(res: dict[str, Any]) -> str | None:
    d = res.get("days")
    if d is None:
        return None
    return "short" if d <= 5 else ("mid" if d <= 12 else "long")


def _weekday(s: dict[str, Any]) -> str:
    return date.fromisoformat(s["date"]).strftime("%a").upper()[:3]


def signal_field(s: dict[str, Any], field: str, key: str = "res_base") -> str | None:
    """The replay signal's value of a ledger cell field, normalised like thl.trade_field."""
    if field == "strategy":
        return s["strat"]
    if field == "direction":
        return s["direction"].lower()
    if field == "regime_at_open":
        return str(s.get("regime") or "").upper()
    if field == "exchange":
        return "binance"
    if field == "weekday":
        return _weekday(s)
    if field == "hold_bucket":
        return _hold_bucket(s.get(key) or {})
    if field in thl.FEATURE_FIELDS:
        return (s.get("features") or {}).get(field)
    return None


def _stats(deltas: list[float], dates: list[str]) -> dict[str, Any]:
    if not deltas:
        return {"n": 0}
    arr = np.asarray(deltas, dtype=float)
    rng = np.random.default_rng(7)
    boots = rng.choice(arr, size=(4000, len(arr)), replace=True).mean(axis=1)
    by_period = {}
    signs = []
    overall = float(arr.mean())
    for a, b in PERIODS:
        sel = [x for x, d in zip(deltas, dates) if a <= d < b]
        if sel:
            m = float(np.mean(sel))
            by_period[f"{a}..{b}"] = {"n": len(sel), "mean": round(m, 3)}
            if len(sel) >= MIN_PERIOD_N:
                signs.append((m > 0) == (overall > 0))
    stable = None if len(signs) < 2 else all(signs)
    return {"n": int(len(arr)), "prior_delta_R_mean": round(overall, 3), "sum": round(float(arr.sum()), 2),
            "p_pos": round(float((boots > 0).mean()), 3), "by_period": by_period, "stable": stable}


def prior_for(hyp: dict[str, Any], taken: list[dict[str, Any]], blocked: list[dict[str, Any]],
              not_taken_by_slot: list[dict[str, Any]]) -> dict[str, Any]:
    kind = hyp.get("kind")
    p = hyp.get("params", {})
    if kind in ("block", "block_where"):
        where = dict(p.get("where", {})) if kind == "block_where" else (
            {"strategy": p["strategy"]} if "strategy" in p else {"direction": p.get("direction"), "regime_at_open": p.get("regime")})
        if "exchange" in where and str(where["exchange"]).lower() != "binance":
            return {"n": 0, "note": "replay is binance only"}
        sel = [s for s in taken if all(thl.where_matches(signal_field(s, f), v) for f, v in where.items() if f != "exchange")]
        return _stats([-s["res_base"]["R"] for s in sel], [s["date"] for s in sel]) | {"rule": f"block where {where}"}
    if kind == "unblock":
        reason = str(p.get("counted_reason") or "")
        if reason == "SLOT_OCCUPIED":
            sel = not_taken_by_slot
        else:
            frag = UNBLOCK_REASONS.get(reason)
            if frag is None:
                return {"n": 0, "note": f"no replay mapping for {reason}"}
            sel = [s for s in blocked if frag in str(s.get("reason") or "")]
        return _stats([s["res_base"]["R"] for s in sel], [s["date"] for s in sel]) | {"rule": f"take signals refused for {reason}"}
    if kind == "extend_timeout":
        h = int(p.get("horizon_days") or 0)
        if h != 40:
            return {"n": 0, "note": f"replay simulated 40 days only, not {h}"}
        sel = [s for s in taken if s["res_base"]["outcome"] == "TIMEOUT" and s.get("res_to40")]
        return _stats([s["res_to40"]["R"] - s["res_base"]["R"] for s in sel], [s["date"] for s in sel]) | {"rule": "hold 40 days instead of 20 on 20-day timeouts"}
    if kind == "stop_cap":
        return {"n": 0, "note": "replay never breaches the cap"}
    if kind in ("partial", "partial_2R"):
        return {"n": 0, "note": "replay exits embed the live partial rule"}
    return {"n": 0, "note": f"kind {kind} not replayable"}


def build(ledger: dict[str, Any], signals: list[dict[str, Any]], as_of: str, run_name: str) -> dict[str, Any]:
    allowed = [s for s in signals if s["allowed"] and s.get("res_base")]
    blocked_all = [s for s in signals if not s["allowed"] and s.get("res_base")]
    taken = dedup(allowed)
    blocked = dedup(blocked_all)
    slot_keys = {(s["sym"], s["strat"], s["date"]) for s, r in one_slot(allowed, "res_base")}
    not_taken = [s for s in taken if (s["sym"], s["strat"], s["date"]) not in slot_keys]
    priors = {}
    for hid, hyp in sorted(ledger["hypotheses"].items()):
        pr = prior_for(hyp, taken, blocked, not_taken)
        pr["computed_as_of"] = as_of
        pr["source"] = run_name
        priors[hid] = pr
    return {"as_of": as_of, "source": run_name, "banner": thl.BANNER,
            "replay_trades": len(taken), "replay_blocked": len(blocked), "not_taken_by_one_slot": len(not_taken),
            "priors": priors}


def render(res: dict[str, Any]) -> str:
    L = [f"# Replay priors for the hypothesis ledger — {res['as_of']}", "", f"**{res['banner']}**", "",
         "An in-sample prior per hypothesis from the replay of the bot's own code "
         f"({res['source']}: {res['replay_trades']} dedup trades taken, {res['replay_blocked']} refused by the gate, "
         f"{res['not_taken_by_one_slot']} allowed but not taken by the one-slot book). "
         "Rendered next to the forward score in the ledger; never used for promotion or rejection.", "",
         "| id | replay prior ΔR | n | p(Δ>0) | stable across half-years | by half-year | note |", "|---|---|---|---|---|---|---|"]
    for hid, pr in res["priors"].items():
        if not pr.get("n"):
            L.append(f"| {hid} | - | 0 | - | - | - | {pr.get('note', '')} |")
            continue
        byp = ", ".join(f"{k[:7]} {v['mean']:+.2f} (n={v['n']})" for k, v in pr["by_period"].items())
        stab = {True: "yes", False: "no", None: "n/a"}[pr["stable"]]
        L.append(f"| {hid} | {pr['prior_delta_R_mean']:+.3f} | {pr['n']} | {pr['p_pos']} | {stab} | {byp} | {pr.get('rule', '')} |")
    L += ["", "- stable = the sign of the mean delta in every half-year with >= 10 trades matches the overall sign.",
          "- A negative prior does not reject a hypothesis; a positive one does not confirm it. The forward thresholds decide.", "",
          f"_{res['banner']}_", ""]
    return "\n".join(L)


def _register_manual_entry() -> None:
    try:
        import database as db
        db.upsert_manual_entry(
            "replay_prior", module_name="Replay Priors for the Hypothesis Ledger", category="Trading", status="live",
            short_description="Gives every ledger hypothesis a fast in-sample prior from the replay of the bot's "
                              "own code, shown next to its forward score. Never promotes or rejects anything.",
            how_it_works="Reads the latest replay run (tools/replay_bot_rules.py signals.json, every signal "
                         "simulated), maps each hypothesis kind to a counterfactual on the replay trades "
                         "(block -> -R of matching trades, unblock -> +R of refused signals, extend_timeout -> "
                         "paired 40d-20d), bootstraps p, checks sign stability across half-years.",
            when_to_use="The morning a hypothesis is registered, to see whether history already argues "
                        "against it; and whenever the replay is re-run.",
            user_action="Run `.venv\\Scripts\\python tools\\replay_bot_rules.py` then "
                        "`.venv\\Scripts\\python tools\\replay_prior.py`; the ledger page shows the column.",
            sort_order=94)
    except Exception:
        pass


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Replay priors (observation only)")
    ap.add_argument("--run-dir", default=None, help="replay run directory (default: newest replay_* under reports/trade_learning)")
    ap.add_argument("--as-of", default=datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    a = ap.parse_args(argv)
    run_dir = Path(a.run_dir) if a.run_dir else sorted(REPORT_DIR.glob("replay_[0-9]*/"))[-1]   # dated engine runs only (not replay_bounce_*)
    ledger = thl.load_ledger()
    res = build(ledger, load_signals(run_dir), a.as_of, run_dir.name)
    (REPORT_DIR / thl.REPLAY_PRIORS_NAME).write_text(json.dumps(res, indent=1), encoding="utf-8")
    md = render(res)
    (REPORT_DIR / "replay_priors.md").write_text(md, encoding="utf-8")
    _register_manual_entry()
    print(thl.BANNER)
    for hid, pr in res["priors"].items():
        print(f"  {hid:42s} {thl._fmt_prior(pr)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
