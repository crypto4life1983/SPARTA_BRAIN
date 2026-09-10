"""C22 fill + lifecycle engine: next-open convention, no-lookahead, frozen exit rules, out-of-radar,
missing execution price, data gap, instrument verification, open-at-end-of-data, weekend
profiles, deterministic rerun, full reconciliation."""
from __future__ import annotations

import json
from datetime import date, timedelta

import pytest

import sparta_commander.c22_replay_lifecycle_engine_contract as E
import sparta_commander.c22_replay_ledger_contract as L
import sparta_commander.c22_replay_cost_engine_contract as C
import sparta_commander.external_signum_trend_radar_gc_long_short_v1_candidate_spec_contract as CAND


# --------------------------------------------------------------------------------------------
# synthetic export builder: export D carries candles D-3, D-2, D-1 for each listed symbol
# --------------------------------------------------------------------------------------------
def _candle(d, o, c, upper=10.0, filt=9.0, trend="Green"):
    return {"date": d, "ohlc": {"o": o, "h": max(o, c) * 1.01, "l": min(o, c) * 0.99, "c": c}, "volume": 1.0,
            "gc": {"upper": upper, "filter": filt, "lower": 8.0, "trend": trend}}


def _build_index(first, last, series, membership=None, missing_exports=()):
    """series: {symbol: {candle_date: (o, c, upper, filter)}}. membership: {export_date: set(symbols)}
    (default: every symbol that has all 3 candles)."""
    idx = {}
    d0, d1 = date.fromisoformat(first), date.fromisoformat(last)
    d = d0
    while d <= d1:
        ex = d.isoformat()
        d += timedelta(days=1)
        if ex in missing_exports:
            continue
        rows = {}
        for sym, cd in series.items():
            if membership and sym not in membership.get(ex, set()):
                continue
            cds = [(date.fromisoformat(ex) - timedelta(days=k)).isoformat() for k in (3, 2, 1)]
            if not all(x in cd for x in cds):
                continue
            data = [_candle(x, *cd[x]) for x in cds]
            rows[sym] = {"symbol": sym, "runDate": ex, "marketRank": 1, "marketCap": 1.0, "breakoutDate": None,
                         "indicators": {"data": data, "cmcRefPriceUsd": data[-1]["ohlc"]["c"]}}
        idx[ex] = rows
    return idx


def _flat(sym_o_c, first="2026-06-25", last="2026-07-20", **kw):
    """constant candles (o, c, upper, filter) for every day in [first-3, last]."""
    out = {}
    for sym, vals in sym_o_c.items():
        cd = {}
        d = date.fromisoformat(first) - timedelta(days=3)
        while d <= date.fromisoformat(last):
            cd[d.isoformat()] = vals(d.isoformat()) if callable(vals) else vals
            d += timedelta(days=1)
        out[sym] = cd
    return out


def _sig(sym, d, signal, rank=1):
    return {"symbol": sym, "decision_date": d, "signal": signal, "market_rank": rank}


VERIFIED = {"A": {"verified": True}, "S": {"verified": True}, "B": {"verified": True}}


# --------------------------------------------------------------------------------------------
def test_frozen_constants_single_sourced():
    assert E.SHORT_TP_MULT == CAND.SHORT_EXIT["take_profit_multiple"] == 0.65
    assert E.BREAKOUT_WINDOW_DAYS == 25
    assert set(E.LIFECYCLE_STATUSES) == {"PENDING_ENTRY", "OPEN", "CLOSED", "REJECTED", "DATA_GAP",
                                         "MISSING_EXECUTION_PRICE", "INSTRUMENT_UNVERIFIED", "OPEN_AT_END_OF_DATA"}


def test_sessions_and_next_session_by_profile():
    assert E.expected_sessions("2026-07-10", "2026-07-13", E.PROFILE_CRYPTO_CALENDAR) == ["2026-07-10", "2026-07-11", "2026-07-12", "2026-07-13"]
    assert E.expected_sessions("2026-07-10", "2026-07-13", E.PROFILE_V2_CONTRACT_EXACT) == ["2026-07-10", "2026-07-13"]
    assert E.next_session_date("2026-07-10", E.PROFILE_CRYPTO_CALENDAR) == "2026-07-11"     # Fri -> Sat
    assert E.next_session_date("2026-07-10", E.PROFILE_V2_CONTRACT_EXACT) == "2026-07-13"    # Fri -> Mon
    with pytest.raises(ValueError):
        E.is_session("2026-07-10", "LUNAR")


def test_next_open_comes_from_the_following_admitted_export_only():
    idx = _build_index("2026-07-01", "2026-07-06", _flat({"A": lambda d: (float(d[-2:]), 5.0, 10.0, 9.0)}, "2026-07-01", "2026-07-06"))
    f = E.fill_at_next_open(idx, "2026-07-02", "A", E.PROFILE_CRYPTO_CALENDAR, "2026-07-06")
    assert f == {"fill_date": "2026-07-03", "price": 3.0, "source_export": "2026-07-04", "status": "OK"}
    # fill candle beyond boundary -> END_OF_DATA, never a price
    f2 = E.fill_at_next_open(idx, "2026-07-05", "A", E.PROFILE_CRYPTO_CALENDAR, "2026-07-06")
    assert f2["status"] == "END_OF_DATA" and f2["price"] is None


def test_no_lookahead_fill_is_strictly_after_decision_and_uses_later_export():
    idx = _build_index("2026-07-01", "2026-07-06", _flat({"A": lambda d: (float(d[-2:]), 5.0, 10.0, 9.0)}, "2026-07-01", "2026-07-06"))
    f = E.fill_at_next_open(idx, "2026-07-02", "A", E.PROFILE_CRYPTO_CALENDAR, "2026-07-06")
    assert f["fill_date"] > "2026-07-02" and f["source_export"] > "2026-07-02"
    # decision export 07-02 only knows candles <= 07-01; the fill price (open of 07-03) is not in it
    assert all(c["date"] <= "2026-07-01" for c in idx["2026-07-02"]["A"]["indicators"]["data"])


def test_missing_execution_price_when_symbol_absent_from_carrier_exports():
    series = _flat({"A": (1.0, 5.0, 10.0, 9.0)}, "2026-07-01", "2026-07-08")
    members = {d: {"A"} for d in ["2026-07-01", "2026-07-02", "2026-07-03"]}       # A drops out after 07-03
    idx = _build_index("2026-07-01", "2026-07-08", series, membership=members)
    f = E.fill_at_next_open(idx, "2026-07-03", "A", E.PROFILE_CRYPTO_CALENDAR, "2026-07-08")
    assert f["status"] == "MISSING_EXECUTION_PRICE" and f["price"] is None


def test_data_gap_when_expected_carrier_export_is_missing():
    series = _flat({"A": (1.0, 5.0, 10.0, 9.0)}, "2026-07-01", "2026-07-08")
    idx = _build_index("2026-07-01", "2026-07-08", series, missing_exports=("2026-07-04",))
    f = E.fill_at_next_open(idx, "2026-07-02", "A", E.PROFILE_CRYPTO_CALENDAR, "2026-07-08")
    # candle 07-03 is also inside exports 07-05 (data[-2]) -> still found from an admitted export
    assert f["status"] == "OK" and f["source_export"] == "2026-07-05"
    idx2 = _build_index("2026-07-01", "2026-07-08", series, missing_exports=("2026-07-04", "2026-07-05", "2026-07-06"))
    f2 = E.fill_at_next_open(idx2, "2026-07-02", "A", E.PROFILE_CRYPTO_CALENDAR, "2026-07-08")
    assert f2["status"] == "DATA_GAP" and f2["missing_export"] == "2026-07-04"


def test_exit_rules_frozen():
    long_pos = {"side": "LONG", "entry_price": 10.0}
    short_pos = {"side": "SHORT", "entry_price": 10.0}
    assert E.evaluate_exit(long_pos, None) == "OUT_OF_RADAR"
    assert E.evaluate_exit(long_pos, {"c": 9.99, "upper": 10.0, "filter": 9.0}) == "LONG_CLOSE_BELOW_GC_UPPER"
    assert E.evaluate_exit(long_pos, {"c": 10.0, "upper": 10.0, "filter": 9.0}) is None
    assert E.evaluate_exit(short_pos, {"c": 9.01, "upper": 10.0, "filter": 9.0}) == "SHORT_STOP_CLOSE_ABOVE_GC_FILTER"
    assert E.evaluate_exit(short_pos, {"c": 6.5, "upper": 10.0, "filter": 9.0}) == "SHORT_TAKE_PROFIT_0_65"
    assert E.evaluate_exit(short_pos, {"c": 8.0, "upper": 10.0, "filter": 9.0}) is None


def test_breakout_window_reference_is_as_of_candle_date():
    assert E.breakout_within_window({"breakoutDate": "2026-06-20"}, "2026-07-15") is True
    assert E.breakout_within_window({"breakoutDate": "2026-06-19"}, "2026-07-15") is False
    assert E.breakout_within_window({"breakoutDate": None}, "2026-07-15") is False
    assert E.breakout_within_window({}, "2026-07-15") is False


# --------------------------------------------------------------------------------------------
# full lifecycle scenarios (calendar profile unless stated)
# --------------------------------------------------------------------------------------------
def _long_scenario():
    # A: price 10 flat; on candle 07-08 close drops to 9 (< upper 10) -> exit condition on export 07-09,
    # fills at open of 07-10 (=10.0), from export 07-11
    def a(d):
        return (10.0, 9.0 if d >= "2026-07-08" else 11.0, 10.0, 9.0)
    return _build_index("2026-07-01", "2026-07-14", _flat({"A": a}, "2026-07-01", "2026-07-14"))


def test_long_lifecycle_closes_on_frozen_exit_and_reconciles():
    idx = _long_scenario()
    r = E.run_lifecycle(idx, [_sig("A", "2026-07-02", "LONG_ENTRY")], E.PROFILE_CRYPTO_CALENDAR, VERIFIED)
    rec = r["records"][0]
    assert rec["lifecycle_status"] == "CLOSED"
    assert rec["entry_date"] == "2026-07-03" and rec["entry_source_export"] == "2026-07-04" and rec["entry_price"] == 10.0
    assert rec["exit_condition_date"] == "2026-07-09" and rec["exit_reason"] == "LONG_CLOSE_BELOW_GC_UPPER"
    assert rec["exit_date"] == "2026-07-10" and rec["exit_source_export"] == "2026-07-11"
    assert r["reconciles_to_input"] and r["lifecycle_counts"]["CLOSED"] == 1
    assert r["pnl_enabled"] is False and r["ledger_snapshot"]["realized_pnl"] == 0.0
    assert r["performance_conclusion"] == "NOT_COMPUTED_PNL_DISABLED"


def test_short_stop_and_take_profit():
    def stop(d):   # close climbs above filter on 07-08
        return (10.0, 9.5 if d >= "2026-07-08" else 8.5, 12.0, 9.0)
    def tp(d):     # close falls to 6 on 07-08 (<= 0.65*10)
        return (10.0, 6.0 if d >= "2026-07-08" else 8.5, 12.0, 9.0)
    for fn, reason in ((stop, "SHORT_STOP_CLOSE_ABOVE_GC_FILTER"), (tp, "SHORT_TAKE_PROFIT_0_65")):
        idx = _build_index("2026-07-01", "2026-07-14", _flat({"S": fn}, "2026-07-01", "2026-07-14"))
        r = E.run_lifecycle(idx, [_sig("S", "2026-07-02", "BEAR_SHORT")], E.PROFILE_CRYPTO_CALENDAR, VERIFIED)
        rec = r["records"][0]
        assert rec["lifecycle_status"] == "CLOSED" and rec["exit_reason"] == reason and rec["side"] == "SHORT"


def test_out_of_radar_exit_requires_admitted_price_else_missing_execution_price():
    series = _flat({"A": (10.0, 11.0, 10.0, 9.0)}, "2026-07-01", "2026-07-14")
    # A in radar through 07-06, absent 07-07 onward: exit condition on export 07-07 (absence);
    # fill needs candle 07-08 open from export 07-09.. but A is gone -> MISSING_EXECUTION_PRICE
    members = {d: ({"A"} if d <= "2026-07-06" else set()) for d in series and
               [(date(2026, 7, 1) + timedelta(days=i)).isoformat() for i in range(14)]}
    idx = _build_index("2026-07-01", "2026-07-14", series, membership=members)
    r = E.run_lifecycle(idx, [_sig("A", "2026-07-02", "LONG_ENTRY")], E.PROFILE_CRYPTO_CALENDAR, VERIFIED)
    rec = r["records"][0]
    assert rec["exit_reason"] == "OUT_OF_RADAR" and rec["exit_condition_date"] == "2026-07-07"
    assert rec["exit_fill"]["status"] == "MISSING_EXECUTION_PRICE" and rec["requires_external_ohlc"] is True
    assert rec["lifecycle_status"] == "OPEN_AT_END_OF_DATA"          # never force-closed, never invented
    assert rec["mark_to_market"]["reason"] == "symbol_absent_from_last_export"
    # reappearing symbol -> the admitted export carries the candle -> exit fills
    members2 = dict(members); members2.update({"2026-07-09": {"A"}, "2026-07-10": {"A"}})
    idx2 = _build_index("2026-07-01", "2026-07-14", series, membership=members2)
    r2 = E.run_lifecycle(idx2, [_sig("A", "2026-07-02", "LONG_ENTRY")], E.PROFILE_CRYPTO_CALENDAR, VERIFIED)
    assert r2["records"][0]["lifecycle_status"] == "CLOSED" and r2["records"][0]["exit_source_export"] == "2026-07-09"


def test_open_at_end_of_data_is_not_force_closed_and_marks_diagnostically():
    idx = _build_index("2026-07-01", "2026-07-10", _flat({"A": (10.0, 11.0, 10.0, 9.0)}, "2026-07-01", "2026-07-10"))
    r = E.run_lifecycle(idx, [_sig("A", "2026-07-02", "LONG_ENTRY")], E.PROFILE_CRYPTO_CALENDAR, VERIFIED)
    rec = r["records"][0]
    assert rec["lifecycle_status"] == "OPEN_AT_END_OF_DATA" and rec["exit_date"] is None
    assert rec["mark_to_market"] == {"mark_date": "2026-07-09", "mark_close": 11.0, "source_export": "2026-07-10",
                                     "unrealized_pnl_diagnostic": None, "decisive": False}
    assert r["ledger_snapshot"]["open_positions"] == 1


def test_entry_decided_but_fill_beyond_boundary_stays_pending():
    idx = _build_index("2026-07-01", "2026-07-10", _flat({"A": (10.0, 11.0, 10.0, 9.0)}, "2026-07-01", "2026-07-10"))
    r = E.run_lifecycle(idx, [_sig("A", "2026-07-09", "LONG_ENTRY")], E.PROFILE_CRYPTO_CALENDAR, VERIFIED)
    rec = r["records"][0]
    assert rec["lifecycle_status"] == "PENDING_ENTRY" and rec["entry_fill"]["status"] == "END_OF_DATA"


def test_instrument_unverified_is_reported_and_enforced_only_in_strict_mode():
    idx = _build_index("2026-07-01", "2026-07-10", _flat({"S": (10.0, 8.5, 12.0, 9.0)}, "2026-07-01", "2026-07-10"))
    loose = E.run_lifecycle(idx, [_sig("S", "2026-07-02", "BEAR_SHORT")], E.PROFILE_CRYPTO_CALENDAR, {})
    assert loose["records"][0]["instrument_status"] == "UNVERIFIED"
    assert loose["records"][0]["lifecycle_status"] == "OPEN_AT_END_OF_DATA"       # lifecycle evidence still produced
    strict = E.run_lifecycle(idx, [_sig("S", "2026-07-02", "BEAR_SHORT")], E.PROFILE_CRYPTO_CALENDAR, {},
                             enforce_instrument_verification=True)
    assert strict["records"][0]["lifecycle_status"] == "INSTRUMENT_UNVERIFIED"
    assert strict["ledger_snapshot"]["open_positions"] == 0


def test_data_gap_session_flags_open_positions():
    series = _flat({"A": (10.0, 11.0, 10.0, 9.0)}, "2026-07-01", "2026-07-14")
    idx = _build_index("2026-07-01", "2026-07-14", series, missing_exports=("2026-07-08",))
    r = E.run_lifecycle(idx, [_sig("A", "2026-07-02", "LONG_ENTRY")], E.PROFILE_CRYPTO_CALENDAR, VERIFIED)
    assert r["data_gap_sessions"] == ["2026-07-08"]
    assert r["records"][0]["crossed_data_gap_dates"] == ["2026-07-08"]


def test_simultaneous_signals_cap_and_one_position_rejections_reconcile():
    series = _flat({"A": (10.0, 11.0, 10.0, 9.0), "S": (10.0, 8.5, 12.0, 9.0), "B": (10.0, 11.0, 10.0, 9.0)}, "2026-07-01", "2026-07-10")
    idx = _build_index("2026-07-01", "2026-07-10", series)
    sigs = [_sig("A", "2026-07-02", "LONG_ENTRY", rank=2), _sig("S", "2026-07-02", "BEAR_SHORT", rank=1),
            _sig("A", "2026-07-04", "LONG_ENTRY", rank=2)]        # second A while A open -> ONE_POSITION_PER_ASSET
    r = E.run_lifecycle(idx, sigs, E.PROFILE_CRYPTO_CALENDAR, VERIFIED)
    by = {x["signal_id"]: x for x in r["records"]}
    assert by["2026-07-02|S|BEAR_SHORT"]["lifecycle_status"] == "OPEN_AT_END_OF_DATA"
    assert by["2026-07-02|A|LONG_ENTRY"]["lifecycle_status"] == "OPEN_AT_END_OF_DATA"
    assert by["2026-07-04|A|LONG_ENTRY"]["lifecycle_status"] == "REJECTED"
    assert by["2026-07-04|A|LONG_ENTRY"]["reject_reason"] == "ONE_POSITION_PER_ASSET"
    assert r["reconciles_to_input"] and sum(r["lifecycle_counts"].values()) == 3
    # cap: 13 x 8% longs would exceed 100% -> the 13th (highest rank number) is rejected at fill
    many = {"L%02d" % i: (10.0, 11.0, 10.0, 9.0) for i in range(13)}
    idx2 = _build_index("2026-07-01", "2026-07-10", _flat(many, "2026-07-01", "2026-07-10"))
    for ex in idx2.values():
        for row in ex.values():
            row["breakoutDate"] = "2026-06-30"
    reg = {k: {"verified": True} for k in many}
    r2 = E.run_lifecycle(idx2, [_sig(k, "2026-07-02", "LONG_ENTRY", rank=i + 1) for i, k in enumerate(sorted(many))],
                         E.PROFILE_CRYPTO_CALENDAR, reg)
    assert r2["lifecycle_counts"]["REJECTED"] == 1 and r2["lifecycle_counts"]["OPEN_AT_END_OF_DATA"] == 12
    rej = [x for x in r2["records"] if x["lifecycle_status"] == "REJECTED"][0]
    assert rej["symbol"] == "L12" and rej["reject_reason"] == "EXPOSURE_CAP_EXCEEDED" and rej["size_pct_nav"] == 8.0


def test_weekend_profiles_differ_only_in_session_mechanics_and_diff_is_explicit():
    # decision Friday 07-03: calendar fills Sat 07-04 open; V2-exact fills Mon 07-06 open
    idx = _build_index("2026-06-30", "2026-07-14", _flat({"A": lambda d: (float(d[-2:]), 11.0, 10.0, 9.0)}, "2026-06-30", "2026-07-14"))
    sigs = [_sig("A", "2026-07-03", "LONG_ENTRY")]
    cal = E.run_lifecycle(idx, sigs, E.PROFILE_CRYPTO_CALENDAR, VERIFIED)
    v2 = E.run_lifecycle(idx, sigs, E.PROFILE_V2_CONTRACT_EXACT, VERIFIED)
    assert cal["records"][0]["entry_date"] == "2026-07-04" and cal["records"][0]["entry_price"] == 4.0
    assert v2["records"][0]["entry_date"] == "2026-07-06" and v2["records"][0]["entry_price"] == 6.0
    d = E.diff_profiles(v2, cal)
    assert d["signals_with_any_difference"] == 1 and d["differences_by_field"] == {"entry_date": 1, "entry_price": 1}
    assert v2["profile_role"] == "FROZEN_CONTRACT_INTERPRETATION"
    assert cal["profile_role"].startswith("DIAGNOSTIC_SENSITIVITY_ONLY")


def test_weekend_decision_under_v2_exact_still_decides_and_fills_next_weekday():
    idx = _build_index("2026-06-30", "2026-07-14", _flat({"A": lambda d: (float(d[-2:]), 11.0, 10.0, 9.0)}, "2026-06-30", "2026-07-14"))
    v2 = E.run_lifecycle(idx, [_sig("A", "2026-07-04", "LONG_ENTRY")], E.PROFILE_V2_CONTRACT_EXACT, VERIFIED)  # Saturday signal
    rec = v2["records"][0]
    assert rec["entry_date"] == "2026-07-06" and rec["entry_price"] == 6.0       # Monday open, from export 07-07
    assert rec["lifecycle_status"] == "OPEN_AT_END_OF_DATA"
    assert "decision_date_is_not_a_session_under_profile:V2_CONTRACT_EXACT" in rec["notes"]
    assert rec["size_pct_nav"] == 2.0


def test_pnl_enabled_requires_non_zero_model_and_deterministic_rerun():
    idx = _long_scenario()
    with pytest.raises(ValueError):
        E.run_lifecycle(idx, [_sig("A", "2026-07-02", "LONG_ENTRY")], E.PROFILE_CRYPTO_CALENDAR, VERIFIED, pnl_enabled=True)
    a = E.run_lifecycle(idx, [_sig("A", "2026-07-02", "LONG_ENTRY")], E.PROFILE_CRYPTO_CALENDAR, VERIFIED,
                        cost_model=C.SENSITIVITY_37BPS_MODEL, pnl_enabled=True)
    b = E.run_lifecycle(idx, [_sig("A", "2026-07-02", "LONG_ENTRY")], E.PROFILE_CRYPTO_CALENDAR, VERIFIED,
                        cost_model=C.SENSITIVITY_37BPS_MODEL, pnl_enabled=True)
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
    assert a["cost_model_status"] == "SENSITIVITY_ONLY" and a["ledger_snapshot"]["fees_paid"] > 0
    assert a["ledger_snapshot"]["realized_pnl"] == pytest.approx(-(a["ledger_snapshot"]["fees_paid"] + a["ledger_snapshot"]["slippage_paid"]))


def test_duplicate_signal_ids_refused():
    idx = _long_scenario()
    with pytest.raises(ValueError):
        E.run_lifecycle(idx, [_sig("A", "2026-07-02", "LONG_ENTRY"), _sig("A", "2026-07-02", "LONG_ENTRY")],
                        E.PROFILE_CRYPTO_CALENDAR, VERIFIED)
