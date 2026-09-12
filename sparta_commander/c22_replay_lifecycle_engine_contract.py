"""Candidate #22 -- DETERMINISTIC FILL + LIFECYCLE ENGINE (PURE; RESEARCH ONLY; NO NETWORK).

Drives frozen C22 signals through the frozen entry/exit mechanics over the admitted Signum
export collection, using the pure ledger for capital accounting. Two session profiles are
implemented and BOTH are always reportable; neither is selected here:

  * V2_CONTRACT_EXACT          -- decision/evaluation sessions are WEEKDAY export dates (the frozen
                                  B1 forward-exit contract rule); weekend exports are admitted
                                  price sources but never sessions.
  * CRYPTO_CALENDAR_SENSITIVITY -- every calendar day with an admitted export is a session
                                  (diagnostic only; crypto trades seven days a week).

Fill convention (single implementation, no alternative): an entry or exit decided on export D
(whose latest CLOSED candle is D-1) fills at the OPEN of the candle dated F = the next session
strictly after D. That open is taken ONLY from an admitted export that carries candle F
(export F+1 data[-1], F+2 data[-2] or F+3 data[-3]). No price is ever manufactured: absent
candle -> MISSING_EXECUTION_PRICE; absent expected export -> DATA_GAP; F beyond the last admitted
export -> unresolved at END_OF_DATA.

No-lookahead: a decision on export D consumes only export D (candle <= D-1) and fills strictly
after D; exits are evaluated only on candles dated >= the position's entry date.

P&L can be DISABLED (dry run): lifecycle, sizing, cap and ordering run in full, every price
observed is recorded, but the ledger closes positions at their entry price so realized and
unrealized P&L stay exactly zero and no performance number exists.
"""
from __future__ import annotations

import json
from datetime import date as _date, timedelta as _td
from pathlib import Path

import sparta_commander.c22_replay_ledger_contract as _L
import sparta_commander.c22_replay_cost_engine_contract as _C
import sparta_commander.c22_signum_gc_data_collection_tracker_contract as _trk
import sparta_commander.external_signum_trend_radar_gc_long_short_v1_candidate_spec_contract as _cand

ENGINE_VERSION = "c22_replay_lifecycle_engine_v1"
PROFILE_V2_CONTRACT_EXACT = "V2_CONTRACT_EXACT"
PROFILE_CRYPTO_CALENDAR = "CRYPTO_CALENDAR_SENSITIVITY"
PROFILES = (PROFILE_V2_CONTRACT_EXACT, PROFILE_CRYPTO_CALENDAR)
PROFILE_ROLE = {PROFILE_V2_CONTRACT_EXACT: "FROZEN_CONTRACT_INTERPRETATION",
                PROFILE_CRYPTO_CALENDAR: "DIAGNOSTIC_SENSITIVITY_ONLY_NEVER_SELECTED_ON_PERFORMANCE"}
FILL_CONVENTION = "OPEN_OF_NEXT_SESSION_STRICTLY_AFTER_DECISION_DATE_FROM_ADMITTED_EXPORT_ONLY"
CANDLE_LOOKUP_MAX_EXPORT_OFFSET = 3       # exports carry 3 closed candles

# lifecycle statuses (exactly one terminal status per signal)
ST_PENDING_ENTRY = "PENDING_ENTRY"
ST_OPEN = "OPEN"
ST_CLOSED = "CLOSED"
ST_REJECTED = "REJECTED"
ST_DATA_GAP = "DATA_GAP"
ST_MISSING_EXECUTION_PRICE = "MISSING_EXECUTION_PRICE"
ST_INSTRUMENT_UNVERIFIED = "INSTRUMENT_UNVERIFIED"
ST_OPEN_AT_END_OF_DATA = "OPEN_AT_END_OF_DATA"
LIFECYCLE_STATUSES = (ST_PENDING_ENTRY, ST_OPEN, ST_CLOSED, ST_REJECTED, ST_DATA_GAP,
                      ST_MISSING_EXECUTION_PRICE, ST_INSTRUMENT_UNVERIFIED, ST_OPEN_AT_END_OF_DATA)

# fill lookup statuses
FILL_OK = "OK"
FILL_MISSING_PRICE = "MISSING_EXECUTION_PRICE"
FILL_DATA_GAP = "DATA_GAP"
FILL_END_OF_DATA = "END_OF_DATA"
FILL_VENUE_PRICE_MISSING = "VENUE_EXECUTION_PRICE_MISSING"

# frozen exit reasons (rule text single-sourced from the candidate spec; asserted in tests)
EXIT_LONG_BELOW_UPPER = "LONG_CLOSE_BELOW_GC_UPPER"
EXIT_SHORT_STOP = "SHORT_STOP_CLOSE_ABOVE_GC_FILTER"
EXIT_SHORT_TP = "SHORT_TAKE_PROFIT_0_65"
EXIT_OUT_OF_RADAR = "OUT_OF_RADAR"
SHORT_TP_MULT = float(_cand.SHORT_EXIT["take_profit_multiple"])                    # 0.65
BREAKOUT_WINDOW_DAYS = int(_cand.LONG_ENTRY["sizing_by_breakout_recency"]["breakout_recent_window_calendar_days"])  # 25

INSTRUMENT_VERIFIED = "VERIFIED"
INSTRUMENT_UNVERIFIED = "UNVERIFIED"
PERFORMANCE_CONCLUSION_INCOMPLETE = "INCOMPLETE_FOLLOWUP"
PERFORMANCE_CONCLUSION_NOT_COMPUTED = "NOT_COMPUTED_PNL_DISABLED"


# --------------------------------------------------------------------------------------------
# exports / sessions
# --------------------------------------------------------------------------------------------
def load_session_index(data_dir) -> dict:
    """{run_date: {symbol: row}} from admitted exports (dated files; the undated legacy file
    fills its content runDate only if no dated file covers it)."""
    index: dict = {}
    undated = []
    for p in sorted(Path(data_dir).glob(_trk.EXPORT_GLOB)):
        if not p.is_file():
            continue
        parsed = json.loads(p.read_bytes().decode("utf-8"))
        rows = [r for r in parsed.get("results") or [] if isinstance(r, dict)]
        d = _trk._date_from_filename(p.name)
        if d is None:
            undated.append(rows)
            continue
        index[d] = {r["symbol"]: r for r in rows}
    for rows in undated:
        rd = {r.get("runDate") for r in rows}
        if len(rd) == 1:
            d = next(iter(rd))
            if d and d not in index:
                index[d] = {r["symbol"]: r for r in rows}
    return index


def latest_candle(row: dict) -> dict:
    d = row["indicators"]["data"][-1]
    return {"date": d["date"], "o": d["ohlc"]["o"], "h": d["ohlc"]["h"], "l": d["ohlc"]["l"],
            "c": d["ohlc"]["c"], "upper": d["gc"]["upper"], "filter": d["gc"]["filter"],
            "trend": d["gc"]["trend"]}


def _iso(d: _date) -> str:
    return d.isoformat()


def is_session(date_iso: str, profile: str) -> bool:
    if profile == PROFILE_CRYPTO_CALENDAR:
        return True
    if profile == PROFILE_V2_CONTRACT_EXACT:
        return _date.fromisoformat(date_iso).weekday() < 5
    raise ValueError("unknown_profile:%s" % profile)


def expected_sessions(first_iso: str, last_iso: str, profile: str) -> list:
    out, d, last = [], _date.fromisoformat(first_iso), _date.fromisoformat(last_iso)
    while d <= last:
        if is_session(_iso(d), profile):
            out.append(_iso(d))
        d += _td(days=1)
    return out


def next_session_date(date_iso: str, profile: str) -> str:
    d = _date.fromisoformat(date_iso) + _td(days=1)
    while not is_session(_iso(d), profile):
        d += _td(days=1)
    return _iso(d)


def find_candle(index: dict, candle_date: str, symbol: str) -> dict:
    """The candle dated `candle_date` for `symbol` from the EARLIEST admitted export that carries
    it (export candle_date+k, k=1..3). Returns {found, candle, source_export, exports_checked}."""
    base = _date.fromisoformat(candle_date)
    checked = []
    for k in range(1, CANDLE_LOOKUP_MAX_EXPORT_OFFSET + 1):
        ex = _iso(base + _td(days=k))
        if ex not in index:
            continue
        checked.append(ex)
        row = index[ex].get(symbol)
        if row is None:
            continue
        for c in row["indicators"]["data"]:
            if c["date"] == candle_date:
                return {"found": True, "source_export": ex, "exports_checked": checked,
                        "candle": {"date": c["date"], "o": c["ohlc"]["o"], "h": c["ohlc"]["h"],
                                   "l": c["ohlc"]["l"], "c": c["ohlc"]["c"]}}
    return {"found": False, "source_export": None, "exports_checked": checked, "candle": None}


def fill_at_next_open(index: dict, decision_date: str, symbol: str, profile: str, last_export: str) -> dict:
    """Executable OPEN of the next session strictly after the decision date, from admitted exports
    only. Never manufactures a price."""
    fill_date = next_session_date(decision_date, profile)
    out = {"fill_date": fill_date, "price": None, "source_export": None, "status": None}
    if fill_date >= last_export:            # candle F needs export F+1 <= last admitted export
        out["status"] = FILL_END_OF_DATA
        return out
    fc = find_candle(index, fill_date, symbol)
    if fc["found"]:
        out.update({"status": FILL_OK, "price": float(fc["candle"]["o"]), "source_export": fc["source_export"]})
        return out
    first_carrier = _iso(_date.fromisoformat(fill_date) + _td(days=1))
    if first_carrier not in index and first_carrier <= last_export and not fc["exports_checked"]:
        out["status"] = FILL_DATA_GAP
        out["missing_export"] = first_carrier
        return out
    out["status"] = FILL_MISSING_PRICE
    out["exports_checked"] = fc["exports_checked"]
    return out


# --------------------------------------------------------------------------------------------
# frozen rules
# --------------------------------------------------------------------------------------------
def breakout_within_window(row: dict, as_of_candle_date: str) -> bool:
    """Frozen: size 8 % only if the row's breakoutDate is within 25 calendar days of the as-of
    (latest closed candle) date; otherwise 2 %. breakoutDate absent -> False."""
    bd = (row or {}).get("breakoutDate")
    if not bd:
        return False
    delta = (_date.fromisoformat(as_of_candle_date) - _date.fromisoformat(str(bd)[:10])).days
    return 0 <= delta <= BREAKOUT_WINDOW_DAYS


def evaluate_exit(position: dict, candle) -> str | None:
    """Frozen exit rules. `candle` None == asset absent from the (valid) export == out-of-radar."""
    if candle is None:
        return EXIT_OUT_OF_RADAR
    if position["side"] == _L.SIDE_LONG:
        return EXIT_LONG_BELOW_UPPER if candle["c"] < candle["upper"] else None
    if candle["c"] > candle["filter"]:
        return EXIT_SHORT_STOP
    if candle["c"] <= SHORT_TP_MULT * position["entry_price"]:
        return EXIT_SHORT_TP
    return None


# --------------------------------------------------------------------------------------------
# lifecycle run
# --------------------------------------------------------------------------------------------
def signal_id(sig: dict) -> str:
    return "%s|%s|%s" % (sig["decision_date"], sig["symbol"], sig["signal"])


def _new_record(sig: dict) -> dict:
    return {"signal_id": signal_id(sig), "symbol": sig["symbol"], "signal": sig["signal"],
            "side": _L.SIDE_OF_SIGNAL.get(sig["signal"]), "decision_date": sig["decision_date"],
            "market_rank": sig["market_rank"], "source_sha256": sig.get("source_sha256"),
            "lifecycle_status": None, "instrument_status": INSTRUMENT_UNVERIFIED, "instrument": None,
            "size_pct_nav": None, "breakout_within_window": None,
            "entry_fill": None, "entry_date": None, "entry_price": None, "entry_source_export": None,
            "exit_condition_date": None, "exit_reason": None, "exit_fill": None,
            "exit_date": None, "exit_price": None, "exit_source_export": None,
            "reject_reason": None, "crossed_data_gap_dates": [], "requires_external_ohlc": False,
            "mark_to_market": None, "notes": []}


def run_lifecycle(index: dict, signals: list, profile: str, instrument_registry=None,
                  cost_model=None, starting_nav: float = 100_000.0, pnl_enabled: bool = False,
                  enforce_instrument_verification: bool = False, execution: dict | None = None) -> dict:
    """Run every signal to exactly one terminal lifecycle status. Deterministic for identical
    inputs. With pnl_enabled=False the ledger never realizes a price difference."""
    if profile not in PROFILES:
        raise ValueError("unknown_profile:%s" % profile)
    cost_model = cost_model or _C.ZERO_COST_MODEL
    if pnl_enabled and cost_model.get("status") == _C.MODEL_STATUS_ZERO:
        raise ValueError("pnl_enabled_requires_a_non_zero_cost_model_selection")
    registry = instrument_registry or {}
    ex = execution or {}
    # execution hooks (all optional, all pure): venue_open(symbol, fill_date)->{price,source}|None;
    # cost_for(symbol)->cost model; half_spread_bps_for(symbol, fill_date, leg)->bps|None;
    # constraints_for(symbol)->dict|None; capacity_for(symbol, fill_date, action)->notional|None;
    # carry_for(symbol, prev_session, session, qty, mark, side)->{"funding":x,"borrow":y,"detail":...}
    def _cm(symbol, side):
        return ex["cost_for"](symbol, side) if ex.get("cost_for") else cost_model

    def _slip(symbol, fill_date, leg, notional, model, side):
        bps = ex["half_spread_bps_for"](symbol, fill_date, leg, side) if ex.get("half_spread_bps_for") else None
        return abs(notional) * bps / 10000.0 if bps is not None else _C.slippage_cost(notional, model, leg)

    def _apply_venue(fill, symbol, side):
        if fill["status"] != FILL_OK or not ex.get("venue_open"):
            return fill
        v = ex["venue_open"](symbol, fill["fill_date"], side)
        if not v or v.get("price") is None:
            return dict(fill, status=FILL_VENUE_PRICE_MISSING, export_reference_price=fill["price"], price=None)
        return dict(fill, price=float(v["price"]), export_reference_price=fill["price"], venue_source=v.get("source"))

    nav_series = []
    prev_session_holder = {"prev": None}
    first_export, last_export = min(index), max(index)
    sessions = expected_sessions(first_export, last_export, profile)
    ledger = _L.new_ledger(starting_nav)
    records = {}
    for s in signals:
        rid = signal_id(s)
        if rid in records:
            raise ValueError("duplicate_signal_id:%s" % rid)
        records[rid] = _new_record(s)
    by_decision: dict = {}
    for s in signals:
        by_decision.setdefault(s["decision_date"], []).append(s)
    pending_entries: list = []      # {rid, fill}
    pending_exits: list = []        # {rid, fill, reason}
    open_rid_by_symbol: dict = {}
    data_gap_sessions: list = []
    seen_ids = set()

    def _instrument(symbol: str) -> tuple:
        ent = registry.get(symbol)
        return (INSTRUMENT_VERIFIED, ent) if ent and ent.get("verified") else (INSTRUMENT_UNVERIFIED, ent)

    def _decide_entries(S: str, snapshot: dict) -> None:
        """Entry decisions for signals dated S. No lookahead: only export S (candles <= S-1)."""
        cand_date = _iso(_date.fromisoformat(S) - _td(days=1))
        for sig in sorted(by_decision.get(S, []), key=_L.order_sort_key):
            rid = signal_id(sig)
            if rid in seen_ids:
                continue
            seen_ids.add(rid)
            rec = records[rid]
            row = snapshot.get(sig["symbol"], {})
            rec["breakout_within_window"] = breakout_within_window(row, cand_date) if sig["signal"] == "LONG_ENTRY" else False
            rec["size_pct_nav"] = _L.sizing_pct_nav(sig["signal"], rec["breakout_within_window"])
            rec["instrument_status"], rec["instrument"] = _instrument(sig["symbol"])
            if S not in session_set:
                rec["notes"].append("decision_date_is_not_a_session_under_profile:%s" % profile)
            fill = _apply_venue(fill_at_next_open(index, S, sig["symbol"], profile, last_export), sig["symbol"], _L.SIDE_OF_SIGNAL.get(sig["signal"]))
            rec["entry_fill"] = fill
            if fill["status"] == FILL_OK:
                rec["lifecycle_status"] = ST_PENDING_ENTRY
                pending_entries.append({"rid": rid, "fill": fill})
            elif fill["status"] == FILL_DATA_GAP:
                rec["lifecycle_status"] = ST_DATA_GAP
                rec["crossed_data_gap_dates"].append(fill.get("missing_export"))
            elif fill["status"] == FILL_MISSING_PRICE:
                rec["lifecycle_status"] = ST_MISSING_EXECUTION_PRICE
                rec["requires_external_ohlc"] = True
            elif fill["status"] == FILL_VENUE_PRICE_MISSING:
                rec["lifecycle_status"] = ST_MISSING_EXECUTION_PRICE
                rec["notes"].append("venue_execution_price_missing_on_fill_date")
            else:
                rec["lifecycle_status"] = ST_PENDING_ENTRY
                rec["notes"].append("entry_fill_beyond_end_of_data")

    session_set = set(sessions)
    # Frozen V2 signals dated on non-session days (weekends under V2_CONTRACT_EXACT) are still
    # frozen decisions: they are decided on their own export date and fill at the next session.
    event_dates = sorted(session_set | {d for d in by_decision if first_export <= d <= last_export})
    for S in event_dates:
        if S not in session_set:
            snapshot = index.get(S)
            if snapshot is None:
                continue
            _decide_entries(S, snapshot)
            continue
        # (a) settle EXITS filling at the open of S (exits before entries)
        for pe in sorted([x for x in pending_exits if x["fill"]["fill_date"] == S], key=lambda x: x["rid"]):
            pending_exits.remove(pe)
            rec = records[pe["rid"]]
            pos = ledger["positions"][rec["symbol"]]
            close_px = pe["fill"]["price"] if pnl_enabled else pos["entry_price"]
            model = _cm(rec["symbol"], pos["side"])
            fee = _C.trading_fee(pos["quantity"] * pe["fill"]["price"], model) if pnl_enabled else 0.0
            slip = _slip(rec["symbol"], S, "exit", pos["quantity"] * pe["fill"]["price"], model, pos["side"]) if pnl_enabled else 0.0
            _L.close_position(ledger, rec["symbol"], close_px, S, pe["reason"], fee, slip, pe["fill"]["source_export"])
            open_rid_by_symbol.pop(rec["symbol"], None)
            rec.update({"lifecycle_status": ST_CLOSED, "exit_date": S, "exit_price": pe["fill"]["price"],
                        "exit_source_export": pe["fill"]["source_export"], "exit_fill": pe["fill"]})
        # (b) settle ENTRIES filling at the open of S, in frozen order
        due = [x for x in pending_entries if x["fill"]["fill_date"] == S]
        for pe in sorted(due, key=lambda x: _L.order_sort_key(records[x["rid"]])):
            pending_entries.remove(pe)
            rec = records[pe["rid"]]
            verified = rec["instrument_status"] == INSTRUMENT_VERIFIED
            order = {"symbol": rec["symbol"], "decision_date": rec["decision_date"], "signal": rec["signal"],
                     "market_rank": rec["market_rank"], "fill_price": pe["fill"]["price"], "fill_date": S,
                     "fill_source_export": pe["fill"]["source_export"],
                     "breakout_within_window": rec["breakout_within_window"],
                     "entry_fee": 0.0, "entry_slippage": 0.0,
                     "instrument_verified": verified if enforce_instrument_verification else True,
                     "instrument": rec["instrument"]}
            if pnl_enabled:
                model = _cm(rec["symbol"], rec["side"])
                notional_est = _L.nav(ledger) * rec["size_pct_nav"] / 100.0
                order["entry_fee"] = _C.trading_fee(notional_est, model)
                order["entry_slippage"] = _slip(rec["symbol"], S, "entry", notional_est, model, rec["side"])
                if ex.get("constraints_for"):
                    order["constraints"] = ex["constraints_for"](rec["symbol"], rec["side"])
                if ex.get("capacity_for"):
                    order["capacity_notional"] = ex["capacity_for"](rec["symbol"], S, "ENTRY", rec["side"])
            res = _L.open_position(ledger, order)
            if res["status"] == _L.STATUS_OPEN:
                open_rid_by_symbol[rec["symbol"]] = pe["rid"]
                rec.update({"lifecycle_status": ST_OPEN, "entry_date": S, "entry_price": pe["fill"]["price"],
                            "entry_source_export": pe["fill"]["source_export"], "entry_fill": pe["fill"]})
            else:
                rec["lifecycle_status"] = (ST_INSTRUMENT_UNVERIFIED if res["reason"] == _L.REJECT_INSTRUMENT_UNVERIFIED
                                           else ST_REJECTED)
                rec["reject_reason"] = res["reason"]
                rec["notes"].append("rejected_at_fill:%s" % json.dumps(res.get("detail"), sort_keys=True, default=str))
        # (c) session export present?
        snapshot = index.get(S)
        if snapshot is None:
            data_gap_sessions.append(S)
            for sym, rid in open_rid_by_symbol.items():
                records[rid]["crossed_data_gap_dates"].append(S)
            continue
        # (d) exit evaluation on export S (candle S-1) for positions entered on/before S-1
        cand_date = _iso(_date.fromisoformat(S) - _td(days=1))
        for sym in sorted(open_rid_by_symbol):
            rid = open_rid_by_symbol[sym]
            rec = records[rid]
            if rec["entry_date"] > cand_date or any(x["rid"] == rid for x in pending_exits):
                continue
            if rec["exit_condition_date"] is not None:
                continue        # condition already met and unfillable: fail closed at the FIRST next bar, never retried
            row = snapshot.get(sym)
            reason = evaluate_exit(ledger["positions"][sym], latest_candle(row) if row else None)
            if reason is None:
                continue
            rec["exit_condition_date"] = S
            rec["exit_reason"] = reason
            fill = _apply_venue(fill_at_next_open(index, S, sym, profile, last_export), sym, ledger["positions"][sym]["side"])
            if fill["status"] == FILL_OK:
                pending_exits.append({"rid": rid, "fill": fill, "reason": reason})
            else:
                rec["exit_fill"] = fill
                rec["requires_external_ohlc"] = fill["status"] == FILL_MISSING_PRICE
                rec["notes"].append("exit_unfillable:%s" % fill["status"])
        # (d2) carry accrual on open positions over (prev session, S]; marks = latest export close
        if pnl_enabled and ex.get("carry_for"):
            for sym in sorted(open_rid_by_symbol):
                pos = ledger["positions"][sym]
                row = snapshot.get(sym)
                mark = latest_candle(row)["c"] if row else pos["entry_price"]
                c = ex["carry_for"](sym, prev_session_holder["prev"], S, pos["quantity"], mark, pos["side"])
                if c and (c.get("funding") or c.get("borrow")):
                    _L.accrue_carry(ledger, sym, c.get("funding", 0.0), c.get("borrow", 0.0))
                    records[open_rid_by_symbol[sym]].setdefault("carry_events", []).append({"session": S, **{k: v for k, v in c.items() if k != "detail"}})
        prev_session_holder["prev"] = S
        marks = {sym: latest_candle(snapshot[sym])["c"] for sym in open_rid_by_symbol if snapshot.get(sym)}
        nav_series.append({"session": S, **{k: v for k, v in _L.snapshot(ledger, marks).items() if k in ("nav", "cash", "realized_pnl", "unrealized_pnl", "gross_exposure", "open_positions")}})
        # (e) entry decisions from signals dated S (no lookahead: only export S is consulted)
        _decide_entries(S, snapshot)
    # END OF DATA: never force-close; mark-to-market diagnostic only where a real close exists
    last_snap = index[last_export]
    for sym, rid in sorted(open_rid_by_symbol.items()):
        rec = records[rid]
        rec["lifecycle_status"] = ST_OPEN_AT_END_OF_DATA
        row = last_snap.get(sym)
        if row:
            c = latest_candle(row)
            pos = ledger["positions"][sym]
            unreal = ((c["c"] - pos["entry_price"]) if pos["side"] == _L.SIDE_LONG else (pos["entry_price"] - c["c"])) * pos["quantity"]
            rec["mark_to_market"] = {"mark_date": c["date"], "mark_close": c["c"], "source_export": last_export,
                                     "unrealized_pnl_diagnostic": unreal if pnl_enabled else None,
                                     "decisive": False}
        else:
            rec["mark_to_market"] = {"mark_date": None, "mark_close": None, "source_export": None,
                                     "reason": "symbol_absent_from_last_export", "decisive": False}
    for pe in pending_entries:
        records[pe["rid"]]["notes"].append("pending_entry_unfilled_at_end_of_data")
    for pe in pending_exits:
        records[pe["rid"]]["notes"].append("pending_exit_unfilled_at_end_of_data")
    for sig in signals:                       # signals dated after the last session never decided
        rec = records[signal_id(sig)]
        if rec["lifecycle_status"] is None:
            rec["lifecycle_status"] = ST_PENDING_ENTRY
            rec["notes"].append("decision_date_outside_admitted_sessions")
    recs = [records[signal_id(s)] for s in sorted(signals, key=_L.order_sort_key)]
    counts = {st: sum(1 for r in recs if r["lifecycle_status"] == st) for st in LIFECYCLE_STATUSES}
    open_at_end = counts[ST_OPEN_AT_END_OF_DATA]
    return {
        "engine_version": ENGINE_VERSION, "profile": profile, "profile_role": PROFILE_ROLE[profile],
        "fill_convention": FILL_CONVENTION, "pnl_enabled": pnl_enabled, "cost_model_id": cost_model["model_id"],
        "cost_model_status": cost_model["status"], "enforce_instrument_verification": enforce_instrument_verification,
        "data_boundary_last_admitted_export": last_export, "first_admitted_export": first_export,
        "sessions_expected": len(sessions), "data_gap_sessions": data_gap_sessions,
        "signals_in": len(signals), "records": recs, "lifecycle_counts": counts,
        "reconciles_to_input": len(recs) == len(signals) and sum(counts.values()) == len(signals),
        "performance_conclusion": (PERFORMANCE_CONCLUSION_NOT_COMPUTED if not pnl_enabled
                                   else (PERFORMANCE_CONCLUSION_INCOMPLETE if open_at_end else "COMPLETE_SUBJECT_TO_PRECONDITIONS")),
        "ledger_snapshot": _L.snapshot(ledger), "ledger_validation": _L.validate_ledger(ledger),
        "nav_series": nav_series if pnl_enabled else None,
        "closed_positions": ledger["closed"] if pnl_enabled else None,
        "open_positions": list(ledger["positions"].values()) if pnl_enabled else None,
        "ledger_rejections": ledger["rejected"],
    }


def diff_profiles(run_a: dict, run_b: dict) -> dict:
    """Every per-signal lifecycle difference between two runs (same signals, different profile)."""
    ra = {r["signal_id"]: r for r in run_a["records"]}
    rb = {r["signal_id"]: r for r in run_b["records"]}
    fields = ("lifecycle_status", "entry_date", "entry_price", "exit_condition_date", "exit_reason",
              "exit_date", "exit_price", "reject_reason", "size_pct_nav", "requires_external_ohlc")
    diffs = []
    for sid in sorted(set(ra) | set(rb)):
        a, b = ra.get(sid), rb.get(sid)
        if a is None or b is None:
            diffs.append({"signal_id": sid, "field": "presence", "a": a is not None, "b": b is not None})
            continue
        for f in fields:
            if a[f] != b[f]:
                diffs.append({"signal_id": sid, "field": f, "a": a[f], "b": b[f]})
    by_field = {}
    for d in diffs:
        by_field[d["field"]] = by_field.get(d["field"], 0) + 1
    return {"profile_a": run_a["profile"], "profile_b": run_b["profile"], "signals_compared": len(ra),
            "signals_with_any_difference": len({d["signal_id"] for d in diffs}),
            "differences_by_field": by_field, "differences": diffs,
            "lifecycle_counts_a": run_a["lifecycle_counts"], "lifecycle_counts_b": run_b["lifecycle_counts"]}
