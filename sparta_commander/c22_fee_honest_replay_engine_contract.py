"""Candidate #22 -- FEE-HONEST REPLAY ENGINE (PURE over sealed inputs; RESEARCH ONLY).

Runs the frozen V2 cohort through the lifecycle engine + portfolio ledger with P&L enabled under
the SEALED pre-registration (cost base case, venue prices, constraints, capacity, funding/borrow,
session profile, NAV). Every value is either OBSERVED / DERIVED from sealed evidence or a labelled
FROZEN_CONSERVATIVE_ASSUMPTION fixed before any result existed. Produces: the decisive variant,
labelled sensitivities, benchmarks (BTC buy-and-hold, flat, matched fixed-seed random-entry null,
signal-off), per-trade cost attribution at the three frozen result levels, and the pre-committed
rejection gates. Positions open at the data boundary are never force-closed: they appear only in
a mark-to-market diagnostic and make the decisive conclusion INCOMPLETE_FOLLOWUP.
"""
from __future__ import annotations

import json
import math
import random
from datetime import date as _date, timedelta as _td
from pathlib import Path

import sparta_commander.c22_replay_cost_engine_contract as _C
import sparta_commander.c22_replay_ledger_contract as _L
import sparta_commander.c22_replay_lifecycle_engine_contract as _E

ENGINE_VERSION = "c22_fee_honest_replay_engine_v1"
STATUS_FROZEN = _C.MODEL_STATUS_FROZEN
LEVELS = ("gross", "transaction_cost_only_net", "fully_net_after_funding_or_borrow")
CONCLUSION_INCOMPLETE = "INCOMPLETE_FOLLOWUP"
CONCLUSION_REJECT = "REJECT"
CONCLUSION_PASS_NON_CONCLUSIVE = "PASS_ECONOMIC_GATES_NON_CONCLUSIVE_LOW_POWER"

PERP_VENUE_OF = {"BINANCE": "BINANCE", "BYBIT": "BYBIT", "OKX": "OKX", "GATE": "GATE", "KRAKEN": "KRAKEN_FUTURES", "BITFINEX": "BITFINEX"}
SPOT_VENUE_OF = {"BINANCE": "BINANCE_SPOT", "COINBASE": "COINBASE_EXCHANGE", "KRAKEN": "KRAKEN_SPOT", "OKX": "OKX_SPOT"}
GLOBAL_FEE_FALLBACK = {"perp": "GATE", "spot": "KRAKEN_SPOT"}     # global max observed (frozen rule)


# --------------------------------------------------------------------------------------------
# execution hooks from sealed inputs
# --------------------------------------------------------------------------------------------
def _short_instrument(prereg: dict, asset: str):
    c = prereg["cost_base_case"]["constraints"].get("SHORT|" + asset)
    return (c["instrument"], c["venue"]) if c else (None, None)


def build_execution(prereg: dict, inputs: dict, short_ohlc: dict, use_venue_prices: bool = True,
                    fee_override_bps=None, slippage_override_bps=None, spot_fee_override_bps=None) -> dict:
    cb = prereg["cost_base_case"]
    fees, slip_asm = cb["fees"], cb["slippage"]["assumption_bps_per_side"]
    kraken_slip = cb["slippage"]["kraken_observed"]
    cap = cb["capacity"]
    funding = {a: sorted(v, key=lambda x: x["ts_ms"]) for a, v in inputs["funding"].items()}
    long_ohlc = {a: {r["date"]: r for r in rows} for a, rows in inputs["long_ohlc"].items()}
    borrow_daily = cb["borrow_leo"]["applied_daily_rate"]

    def venue_key(symbol, side):
        home = symbol.split(":")[0]
        if side == _L.SIDE_SHORT:
            _, v = _short_instrument(prereg, symbol)
            return v or PERP_VENUE_OF.get(home)
        return SPOT_VENUE_OF.get(home)

    def cost_for(symbol, side):
        vk = venue_key(symbol, side)
        f = fees.get(vk) or fees.get(GLOBAL_FEE_FALLBACK["perp" if side == _L.SIDE_SHORT else "spot"])
        taker = f["taker_bps"]
        if side == _L.SIDE_LONG and spot_fee_override_bps is not None:
            taker = spot_fee_override_bps
        if fee_override_bps is not None:
            taker = fee_override_bps
        s = slip_asm if slippage_override_bps is None else slippage_override_bps
        return {"model_id": "c22_frozen_base_case_v1", "status": STATUS_FROZEN, "trading_fee_bps_per_side": taker,
                "entry_slippage_bps": s, "exit_slippage_bps": s, "funding_mode": _C.FUNDING_MODE_PERP_SERIES if side == _L.SIDE_SHORT else _C.FUNDING_MODE_NONE,
                "borrow_mode": _C.BORROW_MODE_RATE_SERIES if vk == "BITFINEX" else _C.BORROW_MODE_NONE, "decisive": True, "venue_key": vk,
                "fee_class": f["class"]}

    def venue_open(symbol, fill_date, side):
        if side == _L.SIDE_SHORT:
            inst, _ = _short_instrument(prereg, symbol)
            row = (short_ohlc.get(symbol) or {}).get(fill_date)
            return {"price": row["open"], "source": "stage3:%s" % inst} if row and row.get("open") else None
        row = (long_ohlc.get(symbol) or {}).get(fill_date)
        return {"price": row["open"], "source": "stage5_spot"} if row and row.get("open") else None

    def half_spread_bps_for(symbol, fill_date, leg, side):
        if slippage_override_bps is not None:
            return None
        inst, vk = _short_instrument(prereg, symbol)
        if side == _L.SIDE_SHORT and vk == "KRAKEN_FUTURES":
            k = kraken_slip.get("%s|%s" % (inst, fill_date))
            return k["half_spread_bps_at_00_00"] if k else None
        return None

    def constraints_for(symbol, side):
        c = prereg["cost_base_case"]["constraints"].get(("SHORT|" if side == _L.SIDE_SHORT else "LONG|") + symbol)
        return dict(c["values"]) if c else None

    def capacity_for(symbol, fill_date, action, side):
        if side == _L.SIDE_SHORT:
            inst, vk = _short_instrument(prereg, symbol)
            k = cap.get("%s|%s" % (inst, fill_date))
            if not k:
                return None
            hit = "bid" if action == "ENTRY" else "ask"          # short entry sells into bids
            if "bid_notional_0_2pct" in k:
                return k["%s_notional_0_2pct" % hit]
            if "bid_notional_0_05pct" in k:
                return k["%s_notional_0_05pct" % hit]
            return k.get("traded_quote_notional_30min")
        row = (long_ohlc.get(symbol) or {}).get(fill_date)
        return (row.get("quote_volume") or 0.0) * LONG_CAPACITY_FRACTION if row else None

    def carry_for(symbol, prev_session, session, qty, mark, side):
        if side == _L.SIDE_LONG:
            return None
        inst, vk = _short_instrument(prereg, symbol)
        lo_ms = _ms(prev_session) if prev_session else 0
        hi_ms = _ms(session)
        if vk == "BITFINEX":
            days = max(0, (_date.fromisoformat(session) - _date.fromisoformat(prev_session)).days) if prev_session else 1
            amt = borrow_daily * qty * mark * days
            return {"funding": 0.0, "borrow": amt, "detail": {"days": days, "daily_rate": borrow_daily, "class": prereg["cost_base_case"]["borrow_leo"]["class"]}}
        recs = [r for r in funding.get(symbol, []) if lo_ms < r["ts_ms"] <= hi_ms]
        if not recs:
            return None
        total = 0.0
        for r in recs:
            m = r.get("mark") or mark
            total += _C.funding_cost(side, qty * m, [("s", r["rate"])])
        return {"funding": total, "borrow": 0.0, "detail": {"settlements": len(recs), "class": "OBSERVED_FIRST_PARTY"}}

    hooks = {"cost_for": cost_for, "half_spread_bps_for": half_spread_bps_for, "constraints_for": constraints_for,
             "capacity_for": capacity_for, "carry_for": carry_for}
    if use_venue_prices:
        hooks["venue_open"] = venue_open
    return hooks


LONG_CAPACITY_FRACTION = 0.01      # frozen: 1% of the venue's daily quote volume on the fill date


def _ms(d):
    from datetime import datetime, timezone
    return int(datetime.fromisoformat(d + "T00:00:00+00:00").timestamp() * 1000)


# --------------------------------------------------------------------------------------------
# metrics / attribution
# --------------------------------------------------------------------------------------------
def metrics(nav_series: list, starting_nav: float) -> dict:
    navs = [starting_nav] + [x["nav"] for x in nav_series]
    rets = [(b / a - 1.0) for a, b in zip(navs, navs[1:]) if a > 0]
    n = len(rets)
    mean = sum(rets) / n if n else 0.0
    var = sum((r - mean) ** 2 for r in rets) / (n - 1) if n > 1 else 0.0
    sd = math.sqrt(var)
    peak, mdd = navs[0], 0.0
    for v in navs:
        peak = max(peak, v)
        mdd = min(mdd, v / peak - 1.0)
    return {"sessions": n, "total_return": navs[-1] / navs[0] - 1.0 if navs[0] else None, "final_nav": navs[-1],
            "mean_session_return": mean, "session_return_sd": sd, "sharpe_annualised_sqrt365": (mean / sd * math.sqrt(365)) if sd > 0 else None,
            "max_drawdown": mdd, "annualisation_warning": "NON-CONCLUSIVE: short low-power path (frozen spec point 9)"}


def trade_attribution(closed: list, open_pos: list) -> dict:
    rows = []
    for p in closed:
        gross = p["gross_pnl"]
        rows.append({"symbol": p["symbol"], "side": p["side"], "signal": p["signal"], "decision_date": p["decision_date"], "entry_date": p["entry_date"], "exit_date": p["exit_date"],
                     "exit_reason": p["exit_reason"], "entry_price": p["entry_price"], "exit_price": p["exit_price"], "quantity": p["quantity"], "notional": p["notional_at_entry"],
                     "gross": gross, "fees": p["fees"], "slippage": p["slippage"], "funding": p["funding"], "borrow": p["borrow"],
                     "transaction_cost_only_net": gross - p["fees"] - p["slippage"], "fully_net_after_funding_or_borrow": p["realized_pnl"],
                     "constraints_applied": p.get("constraints_applied")})
    totals = {lvl: sum(r[lvl] if lvl != "gross" else r["gross"] for r in rows) for lvl in LEVELS}
    return {"closed_trades": rows, "closed_count": len(rows), "wins_fully_net": sum(1 for r in rows if r["fully_net_after_funding_or_borrow"] > 0),
            "totals": totals, "fees_total": sum(r["fees"] for r in rows), "slippage_total": sum(r["slippage"] for r in rows),
            "funding_total": sum(r["funding"] for r in rows), "borrow_total": sum(r["borrow"] for r in rows),
            "open_at_boundary": [{"symbol": p["symbol"], "side": p["side"], "entry_date": p["entry_date"], "entry_price": p["entry_price"], "notional": p["notional_at_entry"],
                                  "fees_so_far": p["fees"], "slippage_so_far": p["slippage"], "funding_so_far": p["funding"], "borrow_so_far": p["borrow"]} for p in open_pos]}


# --------------------------------------------------------------------------------------------
# variants / benchmarks / null
# --------------------------------------------------------------------------------------------
def run_variant(index: dict, signals: list, profile: str, hooks: dict, nav: float, label: str, role: str) -> dict:
    base_model = {"model_id": "c22_frozen_base_case_v1", "status": STATUS_FROZEN, "trading_fee_bps_per_side": 0.0, "entry_slippage_bps": 0.0, "exit_slippage_bps": 0.0,
                  "funding_mode": _C.FUNDING_MODE_PERP_SERIES, "borrow_mode": _C.BORROW_MODE_RATE_SERIES, "decisive": role == "DECISIVE"}
    r = _E.run_lifecycle(index, signals, profile, instrument_registry={}, cost_model=base_model, starting_nav=nav, pnl_enabled=True,
                         enforce_instrument_verification=False, execution=hooks)
    att = trade_attribution(r["closed_positions"], r["open_positions"])
    m = metrics(r["nav_series"], nav)
    counts = r["lifecycle_counts"]
    rej = {}
    for x in r["ledger_rejections"]:
        rej[x["reason"]] = rej.get(x["reason"], 0) + 1
    mtm = [dict(rec["mark_to_market"], symbol=rec["symbol"]) for rec in r["records"] if rec["lifecycle_status"] == _E.ST_OPEN_AT_END_OF_DATA and rec.get("mark_to_market")]
    return {"label": label, "role": role, "profile": profile, "starting_nav": nav, "lifecycle_counts": counts, "ledger_rejections": rej,
            "metrics": m, "attribution": att, "open_at_end_of_data": counts[_E.ST_OPEN_AT_END_OF_DATA], "mark_to_market_diagnostic": mtm,
            "performance_conclusion": r["performance_conclusion"], "ledger_validation": r["ledger_validation"], "nav_series": r["nav_series"],
            "records": r["records"], "basis_diagnostic": basis_diagnostic(r["records"])}


def basis_diagnostic(records: list) -> dict:
    diffs = []
    for rec in records:
        for f in (rec.get("entry_fill"), rec.get("exit_fill")):
            if f and f.get("status") == _E.FILL_OK and f.get("export_reference_price") and f.get("price"):
                diffs.append({"symbol": rec["symbol"], "date": f["fill_date"], "venue_open": f["price"], "cmc_reference_open": f["export_reference_price"],
                              "diff_bps": (f["price"] / f["export_reference_price"] - 1.0) * 1e4})
    if not diffs:
        return {"fills_compared": 0}
    d = sorted(x["diff_bps"] for x in diffs)
    return {"fills_compared": len(d), "median_bps": d[len(d) // 2], "min_bps": d[0], "max_bps": d[-1], "abs_mean_bps": sum(abs(x) for x in d) / len(d), "fills": diffs}


def btc_buy_and_hold(index: dict, sessions: list, prereg: dict, nav: float) -> dict:
    sym = "BINANCE:BTCUSDT"
    closes = []
    for s in sessions:
        row = index.get(s, {}).get(sym)
        if row:
            closes.append((s, _E.latest_candle(row)["c"]))
    if len(closes) < 2:
        return {"available": False}
    fee = prereg["cost_base_case"]["fees"]["BINANCE_SPOT"]["taker_bps"] / 1e4
    slip = prereg["cost_base_case"]["slippage"]["assumption_bps_per_side"] / 1e4
    units = nav * (1 - fee - slip) / closes[0][1]
    series = [{"session": s, "nav": units * c} for s, c in closes[1:]]
    series[-1]["nav"] *= (1 - fee - slip)
    return {"available": True, "entry": closes[0], "exit": closes[-1], "cost_class": prereg["cost_base_case"]["fees"]["BINANCE_SPOT"]["class"], "metrics": metrics(series, nav)}


def matched_random_null(index: dict, executed: list, prereg: dict, nav: float, seed: int, resamples: int, profile: str) -> dict:
    """Matched null: same decision dates, sides, and hold lengths as the executed strategy trades;
    random symbol from the same export's top-50; export-candle prices; frozen fee class per venue;
    slippage assumption; no funding (unknown for arbitrary symbols -> labelled)."""
    fees = prereg["cost_base_case"]["fees"]
    slip = prereg["cost_base_case"]["slippage"]["assumption_bps_per_side"] / 1e4
    last_export = max(index)
    rng = random.Random(seed)
    results = []
    for i in range(resamples):
        pnl = 0.0
        for t in executed:
            snap = index.get(t["decision_date"], {})
            cands = sorted(snap)
            if not cands:
                continue
            sym = rng.choice(cands)
            home = sym.split(":")[0]
            vk = PERP_VENUE_OF.get(home) if t["side"] == _L.SIDE_SHORT else SPOT_VENUE_OF.get(home)
            f = fees.get(vk) or fees.get(GLOBAL_FEE_FALLBACK["perp" if t["side"] == _L.SIDE_SHORT else "spot"])
            fee = f["taker_bps"] / 1e4
            e = _E.fill_at_next_open(index, t["decision_date"], sym, profile, last_export)
            if e["status"] != _E.FILL_OK:
                continue
            x_date = t["exit_decision_date"]
            x = _E.fill_at_next_open(index, x_date, sym, profile, last_export) if x_date else {"status": "OPEN"}
            if x["status"] != _E.FILL_OK:
                continue
            notional = nav * t["size_pct_nav"] / 100.0
            ret = (x["price"] / e["price"] - 1.0) * (1 if t["side"] == _L.SIDE_LONG else -1)
            pnl += notional * (ret - 2 * fee - 2 * slip)
        results.append(pnl / nav)
    results.sort()
    return {"seed": seed, "resamples": resamples, "matched_trades": len(executed), "mean_return": sum(results) / len(results) if results else None,
            "p05": results[int(0.05 * len(results))] if results else None, "p50": results[len(results) // 2] if results else None, "p95": results[int(0.95 * len(results)) - 1] if results else None,
            "funding_note": "null carries no funding/borrow (unknown for arbitrary symbols); compare against the strategy's transaction-cost-only level", "price_basis": "export candles (CMC reference)"}


def executed_trades_for_matching(decisive: dict) -> list:
    out = []
    for rec in decisive["records"]:
        if rec["entry_date"]:
            out.append({"decision_date": rec["decision_date"], "side": rec["side"], "size_pct_nav": rec["size_pct_nav"], "exit_decision_date": rec["exit_condition_date"] if rec["exit_date"] else None})
    return out


def gates(decisive: dict, null: dict, btc: dict, strategy_export_basis: dict) -> dict:
    m = decisive["metrics"]
    att = decisive["attribution"]
    integrity = {"duplicate_trades": len({(r["symbol"], r["entry_date"]) for r in att["closed_trades"]}) != len(att["closed_trades"]),
                 "cost_arithmetic_mismatch": any(abs(r["gross"] - r["fees"] - r["slippage"] - r["funding"] - r["borrow"] - r["fully_net_after_funding_or_borrow"]) > 1e-6 for r in att["closed_trades"]),
                 "ledger_invalid": not decisive["ledger_validation"]["valid"]}
    data = {"open_positions_at_boundary": decisive["open_at_end_of_data"], "capacity_rejections": decisive["ledger_rejections"].get(_L.REJECT_FILL_CAPACITY, 0),
            "min_order_rejections": decisive["ledger_rejections"].get(_L.REJECT_BELOW_MIN_ORDER_RULES, 0)}
    tx_only_return = att["totals"]["transaction_cost_only_net"] / decisive["starting_nav"]
    econ = {"net_return_positive": (m["total_return"] or 0) > 0, "net_sharpe_positive": (m["sharpe_annualised_sqrt365"] or 0) > 0,
            "beats_matched_random_null_p95_tx_only_export_basis": (strategy_export_basis["attribution"]["totals"]["transaction_cost_only_net"] / strategy_export_basis["starting_nav"]) > (null["p95"] if null.get("p95") is not None else float("inf")),
            "beats_btc_buy_and_hold_total_return": btc.get("available") and (m["total_return"] or 0) > (btc["metrics"]["total_return"] or 0)}
    if any(integrity.values()):
        verdict = "REJECT_INTEGRITY"
    elif data["open_positions_at_boundary"] > 0:
        verdict = CONCLUSION_INCOMPLETE
    elif not all(econ.values()):
        verdict = CONCLUSION_REJECT
    else:
        verdict = CONCLUSION_PASS_NON_CONCLUSIVE
    return {"integrity": integrity, "data": data, "economic": econ, "realized_tx_only_return": tx_only_return, "verdict": verdict,
            "note": "decisive conclusion withheld (INCOMPLETE_FOLLOWUP) while any position is open at the boundary; economic gates reported on realized trades only; annualised figures NON-CONCLUSIVE"}
