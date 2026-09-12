"""Candidate #22 -- PURE DETERMINISTIC PORTFOLIO LEDGER (RESEARCH ONLY; NO I/O; NO NETWORK).

A capital-constrained portfolio ledger for the C22 replay. It is deliberately NOT one of the
unlimited-notional per-asset return scripts used by other candidates: every order is sized from
NAV using the FROZEN C22 sizing rules, charged against cash, checked against the 100 % NAV gross
exposure cap, restricted to one position per asset, de-duplicated, and applied in the frozen
deterministic order (decision_date asc -> market_rank asc -> symbol asc). Rejections are
recorded with an explicit reason; nothing is ever resized.

Rules are single-sourced from the frozen replay specification / execution-data contract and
asserted equal in tests; this module adds no leverage and no sizing rule of its own.

Cash mechanics at 1x: LONG  -> cash -= notional + entry costs; close: cash += qty*exit - costs.
                      SHORT -> cash -= notional (collateral reserved) + entry costs;
                               close: cash += notional + (entry-exit)*qty - costs.
Carry (funding / borrow) is charged to cash when accrued and attributed to the position.
Marks: NAV/exposure use the caller-supplied marks; a position without a mark is carried at
its entry price and flagged (never an invented price -- the flag is reported).
"""
from __future__ import annotations

from typing import Any

LEDGER_SCHEMA_VERSION = 1
LEDGER_MODE = "RESEARCH_ONLY_PURE_LEDGER"

# --- FROZEN rules (asserted equal to the frozen spec in tests; never edited here) -------------
SIZING_PCT_NAV = {"BEAR_SHORT": 5.0, "HEDGE_SHORT": 3.0,
                  "LONG_ENTRY_BREAKOUT_WITHIN_25D": 8.0, "LONG_ENTRY": 2.0}
BREAKOUT_RECENT_WINDOW_CALENDAR_DAYS = 25
MAX_GROSS_EXPOSURE_PCT_NAV = 100.0
LEVERAGE = 1.0
ONE_POSITION_PER_ASSET = True

SIDE_LONG = "LONG"
SIDE_SHORT = "SHORT"
SIDE_OF_SIGNAL = {"LONG_ENTRY": SIDE_LONG, "HEDGE_SHORT": SIDE_SHORT, "BEAR_SHORT": SIDE_SHORT}

# --- order / position statuses -------------------------------------------------------------
STATUS_OPEN = "OPEN"
STATUS_CLOSED = "CLOSED"
STATUS_REJECTED = "REJECTED"

REJECT_ONE_POSITION_PER_ASSET = "ONE_POSITION_PER_ASSET"
REJECT_DUPLICATE_ORDER = "DUPLICATE_ORDER"
REJECT_EXPOSURE_CAP = "EXPOSURE_CAP_EXCEEDED"
REJECT_INSUFFICIENT_CASH = "INSUFFICIENT_AVAILABLE_NAV"
REJECT_INVALID_PRICE = "INVALID_FILL_PRICE"
REJECT_UNKNOWN_SIGNAL = "UNKNOWN_SIGNAL"
REJECT_INSTRUMENT_UNVERIFIED = "INSTRUMENT_UNVERIFIED"
REJECT_BELOW_MIN_ORDER_RULES = "BELOW_MIN_ORDER_RULES"
REJECT_FILL_CAPACITY = "FILL_CAPACITY_EXCEEDED"

_EPS = 1e-9


def apply_constraints(notional: float, price: float, side: str, constraints) -> dict:
    """PURE. Snap the fill price to tick (buys up, sells down) and the quantity DOWN to the lot
    step; report min-qty / min-notional violations. No constraints -> pass-through."""
    out = {"price": float(price), "quantity": notional / float(price), "ok": True, "reason": None, "applied": bool(constraints)}
    if not constraints:
        return out
    tick = constraints.get("tick_size")
    if tick:
        n = out["price"] / tick
        snapped = (int(n + 1 - _EPS) if side == SIDE_LONG else int(n + _EPS)) * tick
        out["price"] = float(snapped)
    lot = constraints.get("lot_step")
    qty = notional / out["price"]
    if lot:
        qty = int(qty / lot + _EPS) * lot
    out["quantity"] = qty
    if constraints.get("min_qty") and qty < constraints["min_qty"] - _EPS:
        out.update(ok=False, reason="qty_%s_below_min_qty_%s" % (qty, constraints["min_qty"]))
    elif constraints.get("min_notional") and qty * out["price"] < constraints["min_notional"] - _EPS:
        out.update(ok=False, reason="notional_%.4f_below_min_notional_%s" % (qty * out["price"], constraints["min_notional"]))
    elif qty <= 0:
        out.update(ok=False, reason="zero_quantity_after_lot_rounding")
    return out


def sizing_pct_nav(signal: str, breakout_within_window: bool) -> float:
    """FROZEN sizing: 5 / 3 / 8 (long, breakout within 25 calendar days) / 2 % NAV."""
    if signal == "LONG_ENTRY":
        return SIZING_PCT_NAV["LONG_ENTRY_BREAKOUT_WITHIN_25D" if breakout_within_window else "LONG_ENTRY"]
    if signal in SIZING_PCT_NAV:
        return SIZING_PCT_NAV[signal]
    raise KeyError("unknown_signal:%s" % signal)


def order_sort_key(order: dict) -> tuple:
    """FROZEN deterministic ordering: decision_date asc -> market_rank asc -> symbol asc."""
    return (str(order["decision_date"]), int(order["market_rank"]), str(order["symbol"]))


def order_key(order: dict) -> tuple:
    return (str(order["symbol"]), str(order["decision_date"]), str(order["signal"]))


def new_ledger(starting_nav: float) -> dict:
    if not (isinstance(starting_nav, (int, float)) and starting_nav > 0):
        raise ValueError("starting_nav_must_be_positive")
    return {"schema_version": LEDGER_SCHEMA_VERSION, "mode": LEDGER_MODE,
            "starting_nav": float(starting_nav), "cash": float(starting_nav),
            "positions": {}, "closed": [], "rejected": [], "seen_order_keys": [],
            "realized_pnl": 0.0, "fees_paid": 0.0, "slippage_paid": 0.0,
            "funding_paid": 0.0, "borrow_paid": 0.0, "seq": 0}


def _mark_of(pos: dict, marks) -> tuple:
    if marks and pos["symbol"] in marks and marks[pos["symbol"]] is not None:
        return float(marks[pos["symbol"]]), True
    return float(pos["entry_price"]), False


def position_value(pos: dict, marks=None) -> dict:
    """Notional and unrealized P&L at the given mark (entry price if no mark; flagged)."""
    mark, marked = _mark_of(pos, marks)
    qty = pos["quantity"]
    notional = qty * mark
    unreal = (mark - pos["entry_price"]) * qty if pos["side"] == SIDE_LONG else (pos["entry_price"] - mark) * qty
    return {"symbol": pos["symbol"], "side": pos["side"], "quantity": qty, "mark": mark,
            "marked": marked, "notional": notional, "unrealized_pnl": unreal}


def exposures(ledger: dict, marks=None) -> dict:
    vals = [position_value(p, marks) for _, p in sorted(ledger["positions"].items())]
    gross = sum(v["notional"] for v in vals)
    net = sum(v["notional"] if v["side"] == SIDE_LONG else -v["notional"] for v in vals)
    return {"gross_exposure": gross, "net_exposure": net, "per_position": vals,
            "unmarked_positions": [v["symbol"] for v in vals if not v["marked"]]}


def nav(ledger: dict, marks=None) -> float:
    """NAV = cash + long market value + short collateral + short unrealized P&L."""
    total = ledger["cash"]
    for _, p in sorted(ledger["positions"].items()):
        v = position_value(p, marks)
        if p["side"] == SIDE_LONG:
            total += v["notional"]
        else:
            total += p["notional_at_entry"] + v["unrealized_pnl"]
    return total


def snapshot(ledger: dict, marks=None) -> dict:
    ex = exposures(ledger, marks)
    unreal = sum(v["unrealized_pnl"] for v in ex["per_position"])
    n = nav(ledger, marks)
    return {"nav": n, "cash": ledger["cash"], "realized_pnl": ledger["realized_pnl"],
            "unrealized_pnl": unreal, "gross_exposure": ex["gross_exposure"],
            "net_exposure": ex["net_exposure"],
            "gross_exposure_pct_nav": (ex["gross_exposure"] / n * 100.0) if n > 0 else None,
            "open_positions": len(ledger["positions"]), "closed_positions": len(ledger["closed"]),
            "rejected_orders": len(ledger["rejected"]),
            "fees_paid": ledger["fees_paid"], "slippage_paid": ledger["slippage_paid"],
            "funding_paid": ledger["funding_paid"], "borrow_paid": ledger["borrow_paid"],
            "unmarked_positions": ex["unmarked_positions"]}


def _reject(ledger: dict, order: dict, reason: str, detail: Any = None) -> dict:
    rec = {"status": STATUS_REJECTED, "reason": reason, "detail": detail,
           "symbol": order.get("symbol"), "decision_date": order.get("decision_date"),
           "signal": order.get("signal"), "market_rank": order.get("market_rank")}
    ledger["rejected"].append(rec)
    return rec


def open_position(ledger: dict, order: dict, marks=None) -> dict:
    """Apply ONE entry order. Required order keys: symbol, decision_date, signal, market_rank,
    fill_price, fill_date, breakout_within_window (bool), entry_fee, entry_slippage,
    instrument_verified (bool). Optional: fill_source_export, instrument (dict), size_pct_nav
    (must equal the frozen sizing; it is recomputed and checked). Returns the position (OPEN) or
    the rejection record (REJECTED). Never resizes."""
    key = order_key(order)
    if key in ledger["seen_order_keys"]:
        return _reject(ledger, order, REJECT_DUPLICATE_ORDER, list(key))
    ledger["seen_order_keys"].append(key)
    sig = order["signal"]
    if sig not in SIDE_OF_SIGNAL:
        return _reject(ledger, order, REJECT_UNKNOWN_SIGNAL, sig)
    if not order.get("instrument_verified", False):
        return _reject(ledger, order, REJECT_INSTRUMENT_UNVERIFIED, order.get("instrument"))
    if order["symbol"] in ledger["positions"]:
        return _reject(ledger, order, REJECT_ONE_POSITION_PER_ASSET, order["symbol"])
    price = order.get("fill_price")
    if not isinstance(price, (int, float)) or price <= 0:
        return _reject(ledger, order, REJECT_INVALID_PRICE, price)
    size_pct = sizing_pct_nav(sig, bool(order.get("breakout_within_window", False)))
    if "size_pct_nav" in order and abs(float(order["size_pct_nav"]) - size_pct) > _EPS:
        raise ValueError("order_size_pct_nav_differs_from_frozen_sizing")
    current_nav = nav(ledger, marks)
    notional = current_nav * size_pct / 100.0 * LEVERAGE
    gross_after = exposures(ledger, marks)["gross_exposure"] + notional
    if gross_after > current_nav * MAX_GROSS_EXPOSURE_PCT_NAV / 100.0 + _EPS:
        return _reject(ledger, order, REJECT_EXPOSURE_CAP,
                       {"gross_after_pct_nav": gross_after / current_nav * 100.0, "cap": MAX_GROSS_EXPOSURE_PCT_NAV})
    cap = order.get("capacity_notional")
    if cap is not None and notional > float(cap) + _EPS:
        return _reject(ledger, order, REJECT_FILL_CAPACITY, {"notional": notional, "observed_capacity_notional": float(cap)})
    snap = apply_constraints(notional, float(price), SIDE_OF_SIGNAL[sig], order.get("constraints"))
    if not snap["ok"]:
        return _reject(ledger, order, REJECT_BELOW_MIN_ORDER_RULES, snap["reason"])
    price, qty = snap["price"], snap["quantity"]
    notional = qty * price                      # actual notional after lot rounding (never above the sized notional)
    fee = float(order.get("entry_fee", 0.0))
    slip = float(order.get("entry_slippage", 0.0))
    cash_needed = notional + fee + slip
    if cash_needed > ledger["cash"] + _EPS:
        return _reject(ledger, order, REJECT_INSUFFICIENT_CASH,
                       {"cash": ledger["cash"], "needed": cash_needed})
    ledger["seq"] += 1
    pos = {"position_id": "P%04d" % ledger["seq"], "status": STATUS_OPEN,
           "symbol": order["symbol"], "side": SIDE_OF_SIGNAL[sig], "signal": sig,
           "decision_date": order["decision_date"], "market_rank": order["market_rank"],
           "size_pct_nav": size_pct, "nav_at_decision": current_nav,
           "quantity": qty, "entry_price": float(price), "constraints_applied": snap["applied"],
           "entry_date": order["fill_date"], "entry_source_export": order.get("fill_source_export"),
           "notional_at_entry": notional, "instrument": order.get("instrument"),
           "fees": fee, "slippage": slip, "funding": 0.0, "borrow": 0.0,
           "exit_price": None, "exit_date": None, "exit_reason": None, "realized_pnl": None}
    ledger["cash"] -= cash_needed
    ledger["fees_paid"] += fee
    ledger["slippage_paid"] += slip
    ledger["positions"][order["symbol"]] = pos
    return pos


def accrue_carry(ledger: dict, symbol: str, funding: float = 0.0, borrow: float = 0.0) -> dict:
    """Charge funding (perp) / borrow (spot-margin) to cash and attribute to the position.
    Positive = cost paid; negative = received."""
    pos = ledger["positions"][symbol]
    pos["funding"] += float(funding)
    pos["borrow"] += float(borrow)
    ledger["cash"] -= float(funding) + float(borrow)
    ledger["funding_paid"] += float(funding)
    ledger["borrow_paid"] += float(borrow)
    return pos


def close_position(ledger: dict, symbol: str, fill_price: float, fill_date: str, reason: str,
                   exit_fee: float = 0.0, exit_slippage: float = 0.0, fill_source_export=None) -> dict:
    if symbol not in ledger["positions"]:
        raise KeyError("no_open_position:%s" % symbol)
    if not isinstance(fill_price, (int, float)) or fill_price <= 0:
        raise ValueError("invalid_exit_price")
    pos = ledger["positions"].pop(symbol)
    qty = pos["quantity"]
    gross = (fill_price - pos["entry_price"]) * qty if pos["side"] == SIDE_LONG else (pos["entry_price"] - fill_price) * qty
    fee, slip = float(exit_fee), float(exit_slippage)
    proceeds = (qty * fill_price) if pos["side"] == SIDE_LONG else (pos["notional_at_entry"] + gross)
    ledger["cash"] += proceeds - fee - slip
    pos.update({"status": STATUS_CLOSED, "exit_price": float(fill_price), "exit_date": fill_date,
                "exit_reason": reason, "exit_source_export": fill_source_export,
                "fees": pos["fees"] + fee, "slippage": pos["slippage"] + slip,
                "gross_pnl": gross,
                "realized_pnl": gross - pos["fees"] - fee - pos["slippage"] - slip - pos["funding"] - pos["borrow"]})
    ledger["realized_pnl"] += pos["realized_pnl"]
    ledger["fees_paid"] += fee
    ledger["slippage_paid"] += slip
    ledger["closed"].append(pos)
    return pos


def process_orders(ledger: dict, orders: list, marks=None) -> list:
    """Apply a batch of entry orders in the FROZEN deterministic order. Exits must be applied by
    the caller BEFORE calling this for the same session (exits-before-entries)."""
    return [open_position(ledger, o, marks) for o in sorted(orders, key=order_sort_key)]


def validate_ledger(ledger: dict) -> dict:
    """Invariants: one position per asset, gross exposure at entry never above cap of NAV at
    decision, cash accounting closes (starting + realized - open outlays == cash), no duplicates."""
    failures = []
    syms = [p["symbol"] for p in ledger["positions"].values()]
    if len(syms) != len(set(syms)):
        failures.append("duplicate_open_symbol")
    if len(ledger["seen_order_keys"]) != len(set(tuple(k) for k in ledger["seen_order_keys"])):
        failures.append("duplicate_order_key_recorded_twice")
    outlay = sum(p["notional_at_entry"] + p["fees"] + p["slippage"] + p["funding"] + p["borrow"]
                 for p in ledger["positions"].values())
    expected_cash = ledger["starting_nav"] + ledger["realized_pnl"] - outlay
    if abs(expected_cash - ledger["cash"]) > 1e-6:
        failures.append("cash_does_not_reconcile:%.10f_vs_%.10f" % (expected_cash, ledger["cash"]))
    for p in ledger["positions"].values():
        if p["size_pct_nav"] not in SIZING_PCT_NAV.values():
            failures.append("non_frozen_size:%s" % p["symbol"])
    return {"valid": not failures, "failures": failures}
