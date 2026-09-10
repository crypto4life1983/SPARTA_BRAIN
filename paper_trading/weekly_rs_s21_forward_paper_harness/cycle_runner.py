"""Stateful weekly paper-cycle runner (v2) for the s21 weekly relative-strength rotation.

BROKER-FREE, NETWORK-FREE, KEY-FREE. Reads operator-supplied LOCAL split_only CSVs through
``cycle._load_local_closes`` only; never fetches, never refreshes, never places orders.

Why this exists (audit 2026-09-09 of the ad-hoc ``tmp/run_s21_paper_cycle_002.py`` driver):
  1. ``holding_weeks`` was hard-coded; here it is ``(exit_idx - entry_idx) / R`` from bar distance.
  2. ``weekly_return`` was same-bar ``equity_after / equity_before``; here it is the actual path
     ``prev_cycle.equity_after -> this_cycle.equity_before`` (plus an incl-cost variant).
  3. A fresh DrawdownTracker saw 3 points; here book + tracker are persisted in ``harness_state.json``
     and the tracker is fed every daily mark between anchors plus every anchor's before/after equity.
  4. ``mechanic_drift`` / ``mean_shortfall_bps`` / ``data_integrity_ok`` were literals; here they are computed.
  5. ``ann_cost_drag`` divided by starting capital and calendar years; here it is against current equity
     and elapsed TRADING days.
  6. Off-grid anchors are refused (``NO_TRADE_OFF_GRID``); an anchor gap > R bars is a gap event that is
     either replayed one rebalance bar at a time (default) or refused (``GAP_NO_TRADE``).
  7. The 12/24-week gates in manifest.py now have a reader: ``evaluate_gates``.

Outputs go to a NEW state dir (default ``runs/cycles_v2/``); the legacy ``runs/dry_cycle_001/002`` outputs are
never read for state and never written. Every run requires ``operator_authorized_dry_run=True``.
"""

import argparse
import datetime as _dt
import json as _json
import math as _math
import os as _os
import pathlib as _pathlib

from . import safety
from .cycle import CycleNotAuthorized, StaleDataError, _load_local_closes, resolve_data_source
from .killswitch import check_killswitch
from .manifest import MANIFEST
from .paper_book import DrawdownTracker, PaperBook
from .paper_logging import append_closed_trade, append_order_record, read_all
from .portfolio import build_paper_orders
from .report import build_weekly_report, render_markdown
from .signal import cross_sectional_rank, is_rebalance_bar, select_top_m, trailing_return

HARNESS_DIR = _pathlib.Path(__file__).resolve().parent
DEFAULT_STATE_DIR = HARNESS_DIR / "runs" / "cycles_v2"
STATE_FILENAME = "harness_state.json"
STATE_VERSION = 2
TRADING_DAYS_PER_YEAR = 252
TRAILING_EXPECTANCY_WINDOW = 10

# Cycle statuses. Only STATUS_OK trades; every other status does nothing to the book.
STATUS_OK = "OK"
STATUS_NO_TRADE_OFF_GRID = "NO_TRADE_OFF_GRID"
STATUS_NO_TRADE_ANCHOR_NOT_NEWER = "NO_TRADE_ANCHOR_NOT_NEWER"
STATUS_NO_TRADE_KILLSWITCH_HALTED = "NO_TRADE_KILLSWITCH_HALTED"
STATUS_NO_TRADE_MECHANIC_DRIFT = "NO_TRADE_MECHANIC_DRIFT"
STATUS_GAP_NO_TRADE = "GAP_NO_TRADE"
STATUS_STALE_DATA_NO_TRADE = "STALE_DATA_NO_TRADE"
STATUS_DATA_INTEGRITY_NO_TRADE = "DATA_INTEGRITY_NO_TRADE"
STATUS_STATE_INTEGRITY_NO_TRADE = "STATE_INTEGRITY_NO_TRADE"

GATE_NOT_YET_EVALUABLE = "NOT_YET_EVALUABLE"
GATE_PASS = "PASS"
GATE_FAIL = "FAIL"

# Hard reference of the locked s21 mechanic. If manifest.py ever disagrees with this (or with the snapshot taken
# at the first cycle of a state), that is MECHANIC_DRIFT and the kill-switch halts. No tuning mid-test.
LOCKED_S21_REFERENCE = {
    "locked_mechanic": {
        "momentum_lookback_L": 126, "momentum_skip_S": 21, "top_m_held": 8, "rebalance_cadence_R_days": 5,
        "exit_rule": "ROTATION_RELATIVE_RANK", "exit_is_trailing_or_atr_stop": False, "sizing_method": "equal_weight",
        "per_position_weight_fraction": 1.0 / 8.0, "signal_direction": "long-only", "shorting_enabled": False,
        "leverage": "NONE", "pyramid_method": "NONE", "max_total_positions": 8, "start_cash_usd": 100000,
        "warmup_days": 160, "adjustment_convention": "split_only",
    },
    "cost_model_S1": {"commission_per_share_usd": 0.005, "min_commission_per_trade_usd": 1.0, "slippage_proxy_bps": 1.0},
    "universe_size": 48,
}

DISCLOSURE = "DIAGNOSTIC_ONLY_NOT_LIVE_GRADE; PAUSED; BLOCKED_AT_6_GATES; FRC NEVER_GRANTED; simulated paper only"


# --------------------------------------------------------------------------------------------------------------
# mechanic / params
# --------------------------------------------------------------------------------------------------------------

def _params():
    lm = MANIFEST["locked_mechanic"]
    return {"L": int(lm["momentum_lookback_L"]), "S": int(lm["momentum_skip_S"]), "M": int(lm["top_m_held"]),
            "R": int(lm["rebalance_cadence_R_days"]), "warmup": int(lm["warmup_days"]),
            "start_cash": float(lm["start_cash_usd"]), "cost": dict(MANIFEST["cost_model_S1"])}


def mechanic_snapshot():
    """The subset of manifest.py that defines the mechanic. Stored in state at cycle 1; compared every cycle."""
    lm = MANIFEST["locked_mechanic"]
    return {
        "locked_mechanic": {k: lm.get(k) for k in LOCKED_S21_REFERENCE["locked_mechanic"]},
        "cost_model_S1": dict(MANIFEST["cost_model_S1"]),
        "universe_size": len(MANIFEST["universe_48"]),
    }


def detect_mechanic_drift(state=None):
    """Return (drift: bool, diffs: list[str]). Compares the live manifest against the hard reference AND against the
    snapshot the state took at its first cycle (params must be identical for the whole paper test)."""
    live = mechanic_snapshot()
    diffs = []
    for ref_name, ref in (("reference", LOCKED_S21_REFERENCE), ("state_snapshot", (state or {}).get("mechanic_snapshot"))):
        if not ref:
            continue
        for section in ("locked_mechanic", "cost_model_S1"):
            for k, v in ref[section].items():
                lv = live[section].get(k)
                if isinstance(v, float) or isinstance(lv, float):
                    same = (lv is not None) and abs(float(lv) - float(v)) < 1e-12
                else:
                    same = (lv == v)
                if not same:
                    diffs.append("%s:%s.%s live=%r expected=%r" % (ref_name, section, k, lv, v))
        if live["universe_size"] != ref["universe_size"]:
            diffs.append("%s:universe_size live=%r expected=%r" % (ref_name, live["universe_size"], ref["universe_size"]))
    return bool(diffs), diffs


# --------------------------------------------------------------------------------------------------------------
# state
# --------------------------------------------------------------------------------------------------------------

def new_state():
    p = _params()
    return {
        "state_version": STATE_VERSION, "harness_id": MANIFEST["harness_id"], "disclosure": DISCLOSURE,
        "mechanic_snapshot": mechanic_snapshot(),
        "book": {"cash": p["start_cash"], "holdings": {}},   # holdings: sym -> {shares, cashflow}
        "entry_meta": {},                                    # sym -> {entry_idx, entry_date, entry_price}
        "drawdown": {"peak": None, "max_dd": 0.0},
        "cycles_completed": 0, "first_asof_index": None, "last_asof_index": None, "last_signal_date": None,
        "last_equity_after": None, "cost_cumulative_usd": 0.0,
        "closed_trades_total": 0, "closed_trades_net_pnl_usd": [],   # ordered net pnl of every closed trade
        "fills_total": 0, "shortfall_usd_sum": 0.0, "notional_traded_usd_sum": 0.0,   # notional-weighted shortfall
        "equity_path": [],                                   # one row per cycle: before/after/weekly_return
        "halted": False, "halt_reasons": [], "halt_history": [], "manual_stop": False,
    }


def state_path(state_dir):
    return _pathlib.Path(state_dir) / STATE_FILENAME


def load_state(state_dir):
    """Return the persisted state dict, or None when this state dir has never completed a cycle."""
    sp = state_path(state_dir)
    if not sp.exists():
        return None
    st = _json.loads(sp.read_text(encoding="utf-8"))
    if st.get("state_version") != STATE_VERSION:
        raise ValueError("STATE_VERSION mismatch at %s: %r != %r" % (sp, st.get("state_version"), STATE_VERSION))
    return st


def save_state(state_dir, state):
    """Atomic write (tmp + os.replace) so a crash never leaves a half-written state file."""
    sp = state_path(state_dir)
    sp.parent.mkdir(parents=True, exist_ok=True)
    tmp = sp.with_suffix(".json.tmp")
    tmp.write_text(_json.dumps(state, indent=2, sort_keys=True, default=str), encoding="utf-8")
    _os.replace(tmp, sp)
    return str(sp)


def book_from_state(state):
    p = _params()
    book = PaperBook(p["start_cash"])
    book.cash = float(state["book"]["cash"])
    book.holdings = {s: {"shares": float(h["shares"]), "cashflow": float(h["cashflow"])} for s, h in state["book"]["holdings"].items()}
    return book


def tracker_from_state(state):
    t = DrawdownTracker()
    t.peak = state["drawdown"]["peak"]; t.max_dd = float(state["drawdown"]["max_dd"])
    return t


def resume_after_halt(state_dir, operator_reason):
    """The kill-switch never auto-resumes. Resuming needs a deliberate operator decision with a written reason
    (checklist section 6). This records the reason and clears the halt; nothing else changes."""
    if not operator_reason or not str(operator_reason).strip():
        raise ValueError("resume_after_halt requires a non-empty written operator reason")
    st = load_state(state_dir)
    if st is None:
        raise FileNotFoundError("no state at %s" % state_dir)
    st["halt_history"].append({"cleared_utc": _utc_now(), "reasons": list(st["halt_reasons"]), "operator_reason": str(operator_reason)})
    st["halted"] = False; st["halt_reasons"] = []; st["manual_stop"] = False
    save_state(state_dir, st)
    return st


def _assert_state_dir_is_not_legacy(state_dir):
    sd = _pathlib.Path(state_dir).resolve()
    for part in sd.parts:
        if part.startswith("dry_cycle_"):
            raise ValueError("REFUSED: state_dir %s points inside a legacy dry_cycle_NNN output dir; use a new dir (e.g. runs/cycles_v2)" % sd)


# --------------------------------------------------------------------------------------------------------------
# computed metrics (no literals)
# --------------------------------------------------------------------------------------------------------------

def check_data_integrity(closes, cal, asof_index, lookback_bars):
    """data_integrity_ok = bar continuity (strictly increasing ISO dates, no duplicates) + no NaN/None/non-positive
    close for any universe name over the window the signal and the fill actually use."""
    problems = []
    n = len(cal)
    if asof_index is None or asof_index < 0 or asof_index >= n:
        return False, ["asof_index %r outside calendar [0, %d)" % (asof_index, n)]
    lo = max(0, asof_index - lookback_bars)
    for i in range(lo + 1, asof_index + 1):
        if not (cal[i] > cal[i - 1]):
            problems.append("calendar not strictly increasing at %d (%s -> %s)" % (i, cal[i - 1], cal[i]))
            break
    for sym, ser in closes.items():
        if len(ser) != n:
            problems.append("%s length %d != calendar %d" % (sym, len(ser), n)); continue
        for i in range(lo, asof_index + 1):
            c = ser[i]
            if c is None or (isinstance(c, float) and (_math.isnan(c) or _math.isinf(c))) or c <= 0:
                problems.append("%s bad close at %d (%s): %r" % (sym, i, cal[i], c)); break
    return (not problems), problems


def fill_shortfall_bps(order, reference_close):
    """Implementation shortfall of one simulated fill vs the reference close, in bps, INCLUDING explicit costs.
    Positive = worse than reference (paid more on a buy / received less on a sell). Same-close fills therefore
    show exactly the cost model's drag; a divergent fill price adds its signed distance."""
    sh = abs(float(order["shares"]))
    if sh <= 0 or reference_close <= 0:
        return 0.0
    side = 1.0 if float(order["shares"]) > 0 else -1.0
    price_bps = side * (float(order["fill_price"]) - reference_close) / reference_close * 1e4
    cost_bps = (float(order.get("commission_usd", 0.0)) + float(order.get("slippage_usd", 0.0))) / (sh * reference_close) * 1e4
    return price_bps + cost_bps


def annualized_cost_drag(cost_cumulative, current_equity, elapsed_trading_days):
    """cost drag / yr = (cumulative cost / CURRENT equity) * (252 / elapsed trading days). Caller guarantees
    elapsed_trading_days >= 1 (one cycle's cost covers at least one rebalance period)."""
    if current_equity <= 0 or elapsed_trading_days <= 0:
        return 0.0
    return (cost_cumulative / current_equity) * (TRADING_DAYS_PER_YEAR / float(elapsed_trading_days))


def holding_weeks(entry_idx, exit_idx, rebalance_days):
    return (int(exit_idx) - int(entry_idx)) / float(rebalance_days)


def _trailing_expectancy(pnls, window=TRAILING_EXPECTANCY_WINDOW):
    if not pnls:
        return None
    w = pnls[-window:]
    return sum(w) / len(w)


def _utc_now():
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# --------------------------------------------------------------------------------------------------------------
# gates (12 / 24 week readers for manifest.gate_thresholds)
# --------------------------------------------------------------------------------------------------------------

def _weeks_elapsed(state):
    if not state or state.get("first_asof_index") is None or state.get("last_asof_index") is None:
        return 0.0
    R = _params()["R"]
    return (state["last_asof_index"] - state["first_asof_index"]) / float(R) + 1.0


def evaluate_gates(state):
    """Read the 12-week (>= gate_12wk_min_closed_trades) and 24-week (>= gate_24wk_min_closed_trades) milestones
    from manifest.py and report each as NOT_YET_EVALUABLE / PASS / FAIL with counts.
    A milestone is evaluable only when BOTH its week horizon and its minimum closed-trade sample are reached
    (checklist section 8: never evaluate an under-powered sample). Once evaluable it PASSes iff the checklist
    assessments hold: not halted, annualized cost drag <= max, max drawdown < kill, no mechanic drift.
    PASS is a diagnostic read only -- never live readiness, never promotion, never FRC."""
    T = MANIFEST["gate_thresholds"]
    closed = int((state or {}).get("closed_trades_total", 0))
    weeks = _weeks_elapsed(state)
    last = ((state or {}).get("equity_path") or [{}])[-1]
    drift, drift_diffs = detect_mechanic_drift(state)
    checks = {
        "halted": bool((state or {}).get("halted", False)),
        "annualized_cost_drag": float(last.get("annualized_cost_drag", 0.0) or 0.0),
        "annualized_cost_drag_max": T["annualized_cost_drag_max"],
        "max_drawdown": float(((state or {}).get("drawdown") or {}).get("max_dd", 0.0) or 0.0),
        "drawdown_kill": T["drawdown_kill"],
        "mechanic_drift": drift, "mechanic_drift_diffs": drift_diffs,
    }
    fail_reasons = []
    if checks["halted"]:
        fail_reasons.append("KILLSWITCH_HALTED")
    if checks["annualized_cost_drag"] > checks["annualized_cost_drag_max"]:
        fail_reasons.append("COST_DRAG_GT_MAX")
    if checks["max_drawdown"] >= checks["drawdown_kill"]:
        fail_reasons.append("MAX_DRAWDOWN_GE_KILL")
    if drift:
        fail_reasons.append("MECHANIC_DRIFT")

    out = {"closed_trades_total": closed, "weeks_elapsed": weeks, "checks": checks, "disclosure": DISCLOSURE, "gates": {}}
    for name, horizon_weeks, key in (("12wk", 12, "gate_12wk_min_closed_trades"), ("24wk", 24, "gate_24wk_min_closed_trades")):
        min_trades = int(T[key])
        g = {"horizon_weeks": horizon_weeks, "min_closed_trades": min_trades, "closed_trades": closed,
             "weeks_elapsed": weeks, "sample_reached": closed >= min_trades, "horizon_reached": weeks >= horizon_weeks}
        if not (g["sample_reached"] and g["horizon_reached"]):
            g["status"] = GATE_NOT_YET_EVALUABLE
            g["reason"] = "closed %d/%d trades, %.1f/%d weeks" % (closed, min_trades, weeks, horizon_weeks)
        elif fail_reasons:
            g["status"] = GATE_FAIL; g["reason"] = ",".join(fail_reasons)
        else:
            g["status"] = GATE_PASS; g["reason"] = "sample and horizon reached; assessments hold (diagnostic read only)"
        out["gates"][name] = g
    return out


# --------------------------------------------------------------------------------------------------------------
# one cycle
# --------------------------------------------------------------------------------------------------------------

def _run_one(state, closes, cal, idx, state_dir, run_utc, fill_basis="same_close (simulated)"):
    p = _params(); R, L, S, M = p["R"], p["L"], p["S"], p["M"]
    uni = MANIFEST["universe_48"]
    book = book_from_state(state); dd = tracker_from_state(state)
    cycle_no = state["cycles_completed"] + 1
    first_idx = state["first_asof_index"] if state["first_asof_index"] is not None else idx
    prev_idx = state["last_asof_index"]
    prev_equity_after = state["last_equity_after"] if state["last_equity_after"] is not None else p["start_cash"]

    # Daily marks between the previous anchor and this one: the drawdown tracker sees the intra-gap path.
    min_mark = None
    if prev_idx is not None:
        for b in range(prev_idx + 1, idx):
            eq_b = book.equity({s: closes[s][b] for s in uni})
            dd.update(eq_b)
            min_mark = eq_b if min_mark is None else min(min_mark, eq_b)

    prices = {s: closes[s][idx] for s in uni}
    equity_before = book.equity(prices)
    dd_before = dd.update(equity_before)
    weekly_return = equity_before / prev_equity_after - 1.0

    sigs = {s: trailing_return(closes[s], idx, L, S) for s in uni}
    selected = select_top_m(cross_sectional_rank(sigs), M)
    orders = build_paper_orders(book.holdings, selected, prices, equity_before, m=M,
                                per_share=p["cost"]["commission_per_share_usd"], min_comm=p["cost"]["min_commission_per_trade_usd"],
                                slip_bps=p["cost"]["slippage_proxy_bps"])

    # Closed trades = rotation exits; holding_weeks from bar distance.
    closed = []
    for o in orders:
        if o["action"] != "EXIT":
            continue
        sym = o["symbol"]; meta = state["entry_meta"].get(sym) or {}
        entry_idx = meta.get("entry_idx"); hw = holding_weeks(entry_idx, idx, R) if entry_idx is not None else None
        net = book.holdings[sym]["cashflow"] + o["cashflow_usd"]
        closed.append({"cycle": cycle_no, "symbol": sym, "entry_idx": entry_idx, "entry_date": meta.get("entry_date"),
                       "entry_price": meta.get("entry_price"), "exit_idx": idx, "exit_date": cal[idx],
                       "exit_price": round(o["fill_price"], 6), "shares": round(book.holdings[sym]["shares"], 6),
                       "entry_cashflow_usd": round(book.holdings[sym]["cashflow"], 2), "exit_cashflow_usd": round(o["cashflow_usd"], 2),
                       "net_pnl_usd": round(net, 2), "holding_bars": (idx - entry_idx) if entry_idx is not None else None,
                       "holding_weeks": hw})

    shortfalls = [fill_shortfall_bps(o, prices[o["symbol"]]) for o in orders]
    notionals = [abs(float(o["shares"])) * prices[o["symbol"]] for o in orders]
    shortfall_usd = [b / 1e4 * n for b, n in zip(shortfalls, notionals)]
    book.apply_orders(orders)
    for o in orders:
        if o["action"] == "EXIT":
            state["entry_meta"].pop(o["symbol"], None)
        elif o["action"] == "ENTER":
            state["entry_meta"][o["symbol"]] = {"entry_idx": idx, "entry_date": cal[idx], "entry_price": o["fill_price"]}
    equity_after = book.equity(prices)
    dd_after = dd.update(equity_after)

    cost_cycle = sum(o["commission_usd"] + o["slippage_usd"] for o in orders)
    cost_cum = state["cost_cumulative_usd"] + cost_cycle
    elapsed_td = (idx - first_idx) + R
    drag = annualized_cost_drag(cost_cum, equity_after, elapsed_td)
    # Implementation shortfall is NOTIONAL-weighted (total cost / total notional traded): an equal-weighted per-fill
    # mean is dominated by the $1 minimum commission on dust REBALANCE trims (thousands of bps on a $20 trade).
    fills_total = state["fills_total"] + len(orders)
    sf_usd_sum = state["shortfall_usd_sum"] + sum(shortfall_usd); notional_sum = state["notional_traded_usd_sum"] + sum(notionals)
    mean_sf_cycle = (sum(shortfall_usd) / sum(notionals) * 1e4) if sum(notionals) > 0 else 0.0
    mean_sf_cum = (sf_usd_sum / notional_sum * 1e4) if notional_sum > 0 else 0.0
    pnls = list(state["closed_trades_net_pnl_usd"]) + [c["net_pnl_usd"] for c in closed]
    drift, drift_diffs = detect_mechanic_drift(state)

    ks_metrics = {"current_drawdown": dd_after["current_drawdown"], "annualized_cost_drag": drag, "data_integrity_ok": True,
                  "mean_shortfall_bps": mean_sf_cum, "trailing_expectancy": _trailing_expectancy(pnls),
                  "mechanic_drift": drift, "manual_stop": bool(state.get("manual_stop", False))}
    ks = check_killswitch(ks_metrics)

    week_index = int(round((idx - first_idx) / R)) + 1
    rep = build_weekly_report(week=week_index, signal_date=cal[idx], fill_basis=fill_basis, equity=equity_after,
                              weekly_return=weekly_return, cumulative_return=equity_after / p["start_cash"] - 1.0,
                              rebalances_to_date=cycle_no, closed_this_week=len(closed), cumulative_closed=len(pnls),
                              turnover_names=sum(1 for o in orders if o["action"] in ("ENTER", "EXIT")),
                              cost_this_week=cost_cycle, cost_cumulative=cost_cum, annualized_cost_drag=drag,
                              mean_shortfall_bps=mean_sf_cum, holdings=book.positions(), drawdown_metrics=dd_after,
                              diagnostic_tracking={"realized_closed": len(pnls), "realized_mean_net_pnl": (sum(pnls) / len(pnls)) if pnls else None,
                                                   "trailing_expectancy_last_%d" % TRAILING_EXPECTANCY_WINDOW: ks_metrics["trailing_expectancy"]},
                              data_integrity_ok=True, killswitch_metrics=ks_metrics)

    record = {
        "cycle": cycle_no, "week_index": week_index, "run_executed_utc": run_utc, "signal_date": cal[idx], "asof_index": idx,
        "fill_basis": fill_basis, "on_rebalance_grid": True, "prev_asof_index": prev_idx, "bars_since_prev_cycle": (idx - prev_idx) if prev_idx is not None else None,
        "equity_before": round(equity_before, 2), "equity_after": round(equity_after, 2), "cash_after": round(book.cash, 2),
        "prev_equity_after": round(prev_equity_after, 2), "weekly_return": weekly_return,
        "weekly_return_incl_costs": equity_after / prev_equity_after - 1.0, "cycle_cost_return": equity_after / equity_before - 1.0,
        "min_daily_mark_since_prev": (round(min_mark, 2) if min_mark is not None else None),
        "selected_top8": selected, "signal_snapshot": {s: (round(v, 6) if v is not None else None) for s, v in sigs.items()},
        "orders": [{k: (round(v, 6) if isinstance(v, float) else v) for k, v in o.items()} for o in orders],
        "fill_shortfall_bps": [round(x, 4) for x in shortfalls], "fill_notional_usd": [round(x, 2) for x in notionals],
        "shortfall_usd_cycle": round(sum(shortfall_usd), 4), "notional_traded_usd_cycle": round(sum(notionals), 2),
        "mean_shortfall_bps_cycle": mean_sf_cycle, "mean_shortfall_bps_cumulative": mean_sf_cum, "shortfall_weighting": "notional",
        "holdings_after": {s: {"shares": round(h["shares"], 6), "mkt_value": round(h["shares"] * prices[s], 2), "entry_idx": state["entry_meta"][s]["entry_idx"]}
                           for s, h in book.holdings.items()},
        "closed_trades": closed, "closed_trades_total": len(pnls),
        "cost_this_cycle": round(cost_cycle, 4), "cost_cumulative": round(cost_cum, 4), "elapsed_trading_days": elapsed_td, "annualized_cost_drag": drag,
        "drawdown_before": dd_before, "drawdown_after": dd_after, "data_integrity_ok": True, "mechanic_drift": drift, "mechanic_drift_diffs": drift_diffs,
        "killswitch_metrics": ks_metrics, "killswitch": ks, "verdict": rep["verdict"], "disclosure": DISCLOSURE,
    }

    # persist ledgers (append-only) + per-cycle files, then state
    sd = _pathlib.Path(state_dir)
    cdir = sd / ("cycle_%03d" % cycle_no); cdir.mkdir(parents=True, exist_ok=True)
    append_order_record(sd / "paper_orders.jsonl", record)
    for c in closed:
        append_closed_trade(sd / "paper_trades_closed.jsonl", c)
    append_order_record(sd / "equity_ledger.jsonl", {k: record[k] for k in ("cycle", "week_index", "asof_index", "signal_date", "prev_equity_after", "equity_before",
                                                                            "equity_after", "weekly_return", "weekly_return_incl_costs", "min_daily_mark_since_prev", "drawdown_after")})
    (cdir / ("cycle_%03d.json" % cycle_no)).write_text(_json.dumps(record, indent=2, sort_keys=True, default=str), encoding="utf-8")
    (cdir / "killswitch_status.json").write_text(_json.dumps({"cycle": cycle_no, "week": week_index, "metrics": ks_metrics, "result": ks}, indent=2, sort_keys=True), encoding="utf-8")
    (cdir / ("paper_weekly_report_%03d.md" % cycle_no)).write_text(render_markdown(rep), encoding="utf-8")

    state["book"] = {"cash": book.cash, "holdings": {s: {"shares": h["shares"], "cashflow": h["cashflow"]} for s, h in book.holdings.items()}}
    state["drawdown"] = {"peak": dd.peak, "max_dd": dd.max_dd}
    state["cycles_completed"] = cycle_no; state["first_asof_index"] = first_idx; state["last_asof_index"] = idx
    state["last_signal_date"] = cal[idx]; state["last_equity_after"] = equity_after; state["cost_cumulative_usd"] = cost_cum
    state["closed_trades_total"] = len(pnls); state["closed_trades_net_pnl_usd"] = pnls
    state["fills_total"] = fills_total; state["shortfall_usd_sum"] = sf_usd_sum; state["notional_traded_usd_sum"] = notional_sum
    state["equity_path"].append({"cycle": cycle_no, "asof_index": idx, "signal_date": cal[idx], "equity_before": equity_before, "equity_after": equity_after,
                                 "weekly_return": weekly_return, "weekly_return_incl_costs": record["weekly_return_incl_costs"],
                                 "annualized_cost_drag": drag, "max_drawdown": dd.max_dd})
    if ks["halt"]:
        state["halted"] = True; state["halt_reasons"] = list(ks["reasons"])
        state["halt_history"].append({"cycle": cycle_no, "signal_date": cal[idx], "reasons": list(ks["reasons"]), "utc": run_utc})
    save_state(state_dir, state)
    return record


# --------------------------------------------------------------------------------------------------------------
# entry point
# --------------------------------------------------------------------------------------------------------------

def _refusal(status, reason, state=None, **extra):
    out = {"status": status, "reason": reason, "cycles": [], "traded": False, "state": state, "disclosure": DISCLOSURE}
    out.update(extra)
    return out


def _persist_pretrade_halt(state_dir, state, reasons, idx, cal):
    """Data-integrity failure and mechanic drift are kill-switch HALTs even though no trade happened (checklist s6)."""
    if state is None:
        return None
    state["halted"] = True; state["halt_reasons"] = list(reasons)
    state["halt_history"].append({"cycle": state["cycles_completed"], "attempted_asof_index": idx,
                                  "attempted_signal_date": (cal[idx] if (cal and idx is not None and 0 <= idx < len(cal)) else None),
                                  "reasons": list(reasons), "utc": _utc_now()})
    save_state(state_dir, state)
    return state


def run_cycle(asof_index=None, asof_date=None, state_dir=DEFAULT_STATE_DIR, local_csv_dir=None, filename_suffix=None, data_source=None,
              min_last_date=None, operator_authorized_dry_run=False, replay_missed_rebalances=True, live_mode=False, broker=None):
    """Run the weekly paper rebalance for ONE target anchor, persisting book + drawdown state across calls.

    Anchor: ``asof_index`` or ``asof_date`` (ISO); neither -> the latest on-grid bar in the local calendar.
    Refusals (nothing traded, book untouched): NO_TRADE_OFF_GRID, NO_TRADE_ANCHOR_NOT_NEWER, GAP_NO_TRADE,
    STALE_DATA_NO_TRADE (loader raised StaleDataError; data is NEVER refreshed here), DATA_INTEGRITY_NO_TRADE,
    NO_TRADE_MECHANIC_DRIFT, NO_TRADE_KILLSWITCH_HALTED, STATE_INTEGRITY_NO_TRADE.
    Gap: if the anchor is > R bars after the previous cycle, every intermediate on-grid bar is replayed as its own
    cycle in order (``replay_missed_rebalances=True``), each marking equity; otherwise GAP_NO_TRADE.
    Returns {"status", "reason", "cycles": [record, ...], "traded", "state", ...}."""
    safety.assert_safe_environment(live_mode=live_mode, broker=broker)
    if not operator_authorized_dry_run:
        raise CycleNotAuthorized("PAPER_CYCLE_NOT_AUTHORIZED: set operator_authorized_dry_run=True under a SEPARATE explicit operator authorization.")
    _assert_state_dir_is_not_legacy(state_dir)
    p = _params(); R, warmup = p["R"], p["warmup"]

    state = load_state(state_dir)
    if state is not None and state.get("halted"):
        return _refusal(STATUS_NO_TRADE_KILLSWITCH_HALTED, "kill-switch halted: %s (never auto-resumes; resume_after_halt needs a written reason)" % state.get("halt_reasons"), state)

    drift, drift_diffs = detect_mechanic_drift(state)
    if drift:
        return _refusal(STATUS_NO_TRADE_MECHANIC_DRIFT, "MECHANIC_DRIFT_FROM_LOCKED_S21: " + "; ".join(drift_diffs),
                        _persist_pretrade_halt(state_dir, state, ["MECHANIC_DRIFT_FROM_LOCKED_S21"], None, None), drift_diffs=drift_diffs)

    rdir, rsuffix, _ = resolve_data_source(local_csv_dir, filename_suffix, data_source)
    try:
        closes, cal = _load_local_closes(rdir, rsuffix, min_last_date=min_last_date)
    except StaleDataError as e:
        return _refusal(STATUS_STALE_DATA_NO_TRADE, "%s -- data is NOT refreshed by this runner (needs its own RUN_BOOK authorization)" % e, state)
    except (FileNotFoundError, ValueError) as e:
        return _refusal(STATUS_DATA_INTEGRITY_NO_TRADE, str(e), _persist_pretrade_halt(state_dir, state, ["DATA_INTEGRITY_FAILURE_NO_TRADE"], None, None))

    # resolve the target anchor
    if asof_index is None and asof_date is not None:
        if asof_date > cal[-1]:
            return _refusal(STATUS_STALE_DATA_NO_TRADE, "asof_date %s is after the last local bar %s (NO-TRADE; do not refresh here)" % (asof_date, cal[-1]), state)
        if asof_date not in cal:
            return _refusal(STATUS_DATA_INTEGRITY_NO_TRADE, "asof_date %s not in local calendar" % asof_date, state)
        asof_index = cal.index(asof_date)
    if asof_index is None:
        asof_index = len(cal) - 1
        while asof_index >= 0 and not is_rebalance_bar(asof_index, warmup, R):
            asof_index -= 1
    asof_index = int(asof_index)
    if asof_index < 0 or asof_index >= len(cal):
        return _refusal(STATUS_DATA_INTEGRITY_NO_TRADE, "asof_index %d outside local calendar [0, %d)" % (asof_index, len(cal)), state)
    if not is_rebalance_bar(asof_index, warmup, R):
        lo = asof_index - ((asof_index - warmup) % R) if asof_index >= warmup else None
        return _refusal(STATUS_NO_TRADE_OFF_GRID, "anchor idx %d (%s) is OFF the rebalance grid: (idx-%d) %% %d = %d; nearest grid bars %s / %s"
                        % (asof_index, cal[asof_index], warmup, R, (asof_index - warmup) % R if asof_index >= warmup else -1, lo, (lo + R) if lo is not None else warmup), state)
    if asof_index - p["S"] - p["L"] < 0:
        return _refusal(STATUS_DATA_INTEGRITY_NO_TRADE, "anchor idx %d has no full %d+%d signal window" % (asof_index, p["L"], p["S"]), state)

    # anchor sequence (gap handling)
    if state is None:
        state = new_state(); anchors = [asof_index]; gap_event = False
    else:
        prev = int(state["last_asof_index"])
        if not is_rebalance_bar(prev, warmup, R):
            return _refusal(STATUS_STATE_INTEGRITY_NO_TRADE, "persisted last_asof_index %d is off the rebalance grid; state is not trustworthy" % prev, state)
        if asof_index <= prev:
            return _refusal(STATUS_NO_TRADE_ANCHOR_NOT_NEWER, "anchor idx %d (%s) is not newer than last cycle idx %d (%s); never duplicate a traded anchor"
                            % (asof_index, cal[asof_index], prev, state["last_signal_date"]), state)
        gap_event = (asof_index - prev) > R
        anchors = list(range(prev + R, asof_index + 1, R))
        if gap_event and not replay_missed_rebalances:
            return _refusal(STATUS_GAP_NO_TRADE, "anchor gap %d bars > R=%d and replay_missed_rebalances=False; %d intermediate rebalance bars not traded"
                            % (asof_index - prev, R, len(anchors) - 1), state, gap_bars=asof_index - prev, missed_anchors=anchors[:-1])

    # integrity over every anchor we are about to trade (fallback for gap replay: any missing bar -> GAP_NO_TRADE)
    window = p["L"] + p["S"]
    for a in anchors:
        ok, problems = check_data_integrity(closes, cal, a, window)
        if not ok:
            if gap_event and a != asof_index:
                return _refusal(STATUS_GAP_NO_TRADE, "gap replay needs bar %d (%s) but data failed integrity: %s" % (a, cal[a] if a < len(cal) else "?", problems[:3]),
                                state if state.get("cycles_completed") else None, missed_anchors=anchors[:-1])
            return _refusal(STATUS_DATA_INTEGRITY_NO_TRADE, "; ".join(problems[:5]),
                            _persist_pretrade_halt(state_dir, state if state.get("cycles_completed") else None, ["DATA_INTEGRITY_FAILURE_NO_TRADE"], a, cal))

    run_utc = _utc_now(); records = []
    for a in anchors:
        rec = _run_one(state, closes, cal, a, state_dir, run_utc, fill_basis="same_close (simulated%s)" % ("; gap replay" if (gap_event and a != asof_index) else ""))
        records.append(rec)
        if rec["killswitch"]["halt"]:
            break
    out = {"status": STATUS_OK, "reason": ("gap replay of %d rebalance bars" % len(anchors)) if gap_event else "single weekly cycle",
           "cycles": records, "traded": True, "gap_event": gap_event, "anchors": anchors[:len(records)], "state": state,
           "gates": evaluate_gates(state), "disclosure": DISCLOSURE}
    if state["halted"]:
        out["halted"] = True; out["halt_reasons"] = state["halt_reasons"]
    return out


def read_ledgers(state_dir):
    sd = _pathlib.Path(state_dir)
    return {"orders": read_all(sd / "paper_orders.jsonl"), "closed": read_all(sd / "paper_trades_closed.jsonl"), "equity": read_all(sd / "equity_ledger.jsonl")}


def main(argv=None):
    ap = argparse.ArgumentParser(description="s21 weekly RS stateful paper-cycle runner (broker-free; refuses without --operator-authorized-dry-run)")
    ap.add_argument("--asof-date"); ap.add_argument("--asof-index", type=int)
    ap.add_argument("--state-dir", default=str(DEFAULT_STATE_DIR)); ap.add_argument("--data-source"); ap.add_argument("--local-csv-dir"); ap.add_argument("--filename-suffix")
    ap.add_argument("--min-last-date"); ap.add_argument("--no-replay", action="store_true", help="gap -> GAP_NO_TRADE instead of replaying missed rebalances")
    ap.add_argument("--operator-authorized-dry-run", action="store_true")
    a = ap.parse_args(argv)
    res = run_cycle(asof_index=a.asof_index, asof_date=a.asof_date, state_dir=a.state_dir, local_csv_dir=a.local_csv_dir, filename_suffix=a.filename_suffix,
                    data_source=a.data_source, min_last_date=a.min_last_date, operator_authorized_dry_run=a.operator_authorized_dry_run,
                    replay_missed_rebalances=not a.no_replay)
    summary = {k: v for k, v in res.items() if k not in ("state", "cycles")}
    summary["cycles"] = [{"cycle": c["cycle"], "signal_date": c["signal_date"], "asof_index": c["asof_index"], "equity_before": c["equity_before"],
                          "equity_after": c["equity_after"], "weekly_return": c["weekly_return"], "closed": len(c["closed_trades"]), "verdict": c["verdict"]} for c in res["cycles"]]
    print(_json.dumps(summary, indent=2, sort_keys=True, default=str))
    return 0 if res["status"] == STATUS_OK else 1


if __name__ == "__main__":
    raise SystemExit(main())
