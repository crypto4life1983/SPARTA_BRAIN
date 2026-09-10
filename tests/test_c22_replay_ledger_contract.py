"""C22 pure portfolio ledger: frozen sizing single-sourced, cash/NAV/exposure mechanics,
long/short winners and losers, cap + cash + duplicate + one-position rejections, deterministic
ordering, carry components, deterministic rerun equality, invariants."""
from __future__ import annotations

import copy
import json

import pytest

import sparta_commander.c22_replay_ledger_contract as L
import sparta_commander.c22_execution_data_short_instrument_feasibility_contract as X
import sparta_commander.external_signum_trend_radar_gc_long_short_v1_replay_spec_contract as SPEC


def _order(symbol, signal, price, decision_date="2026-07-01", rank=1, breakout=False, fee=0.0, slip=0.0,
           verified=True, fill_date="2026-07-02"):
    return {"symbol": symbol, "decision_date": decision_date, "signal": signal, "market_rank": rank,
            "fill_price": price, "fill_date": fill_date, "breakout_within_window": breakout,
            "entry_fee": fee, "entry_slippage": slip, "instrument_verified": verified}


# --- frozen-rule single sourcing ---------------------------------------------------------------

def test_sizing_equals_frozen_replay_spec():
    s = SPEC.build_replay_spec()["signal_handling"]["position_sizing_pct_nav"]
    assert L.SIZING_PCT_NAV["BEAR_SHORT"] == s["bear_short"] == 5.0
    assert L.SIZING_PCT_NAV["HEDGE_SHORT"] == s["hedge_short"] == 3.0
    assert L.SIZING_PCT_NAV["LONG_ENTRY_BREAKOUT_WITHIN_25D"] == s["long_breakout_within_25d"] == 8.0
    assert L.SIZING_PCT_NAV["LONG_ENTRY"] == s["long_otherwise"] == 2.0
    assert L.sizing_pct_nav("LONG_ENTRY", True) == 8.0 and L.sizing_pct_nav("LONG_ENTRY", False) == 2.0
    assert L.sizing_pct_nav("BEAR_SHORT", True) == 5.0 and L.sizing_pct_nav("HEDGE_SHORT", False) == 3.0


def test_cap_and_leverage_equal_frozen_contracts():
    assert L.MAX_GROSS_EXPOSURE_PCT_NAV == X.EXECUTION_FEASIBILITY_RULES["max_gross_exposure_pct_nav"] == 100.0
    assert L.MAX_GROSS_EXPOSURE_PCT_NAV == SPEC.build_replay_spec()["signal_handling"]["max_gross_exposure_pct_nav"]
    assert L.LEVERAGE == 1.0 and L.ONE_POSITION_PER_ASSET is True
    assert X.EXECUTION_FEASIBILITY_RULES["insufficient_nav_deterministic_rejection"] is True
    assert X.EXECUTION_FEASIBILITY_RULES["no_proportional_resizing"] is True


def test_unknown_signal_rejected_not_sized():
    with pytest.raises(KeyError):
        L.sizing_pct_nav("MYSTERY", False)
    led = L.new_ledger(1000.0)
    r = L.open_position(led, _order("A", "MYSTERY", 10.0))
    assert r["status"] == "REJECTED" and r["reason"] == "UNKNOWN_SIGNAL"


# --- mechanics -----------------------------------------------------------------------------------

def test_long_winner_realized_and_cash_reconcile():
    led = L.new_ledger(1000.0)
    p = L.open_position(led, _order("A", "LONG_ENTRY", 10.0, breakout=True, fee=1.0, slip=0.5))
    assert p["status"] == "OPEN" and p["size_pct_nav"] == 8.0 and p["notional_at_entry"] == 80.0 and p["quantity"] == 8.0
    assert led["cash"] == pytest.approx(1000.0 - 80.0 - 1.5)
    assert L.snapshot(led, {"A": 12.0})["unrealized_pnl"] == pytest.approx(16.0)
    c = L.close_position(led, "A", 12.0, "2026-07-10", "LONG_BELOW_UPPER", exit_fee=1.0, exit_slippage=0.5)
    assert c["gross_pnl"] == pytest.approx(16.0) and c["realized_pnl"] == pytest.approx(16.0 - 3.0)
    assert led["cash"] == pytest.approx(1000.0 + 13.0) and led["realized_pnl"] == pytest.approx(13.0)
    assert L.validate_ledger(led)["valid"]


def test_long_loser():
    led = L.new_ledger(1000.0)
    L.open_position(led, _order("A", "LONG_ENTRY", 10.0))          # 2% -> 20 notional, qty 2
    c = L.close_position(led, "A", 9.0, "2026-07-10", "LONG_BELOW_UPPER")
    assert c["realized_pnl"] == pytest.approx(-2.0) and led["cash"] == pytest.approx(998.0)


def test_short_winner_and_loser():
    led = L.new_ledger(1000.0)
    p = L.open_position(led, _order("S", "BEAR_SHORT", 20.0))       # 5% -> 50 notional, qty 2.5
    assert p["side"] == "SHORT" and led["cash"] == pytest.approx(950.0)
    assert L.nav(led) == pytest.approx(1000.0)                        # collateral counted, no mark change
    assert L.snapshot(led, {"S": 15.0})["unrealized_pnl"] == pytest.approx(12.5)
    c = L.close_position(led, "S", 15.0, "2026-07-10", "SHORT_TP_0_65")
    assert c["realized_pnl"] == pytest.approx(12.5) and led["cash"] == pytest.approx(1012.5)
    led2 = L.new_ledger(1000.0)
    L.open_position(led2, _order("S", "HEDGE_SHORT", 20.0))          # 3% -> 30, qty 1.5
    c2 = L.close_position(led2, "S", 24.0, "2026-07-10", "SHORT_STOP_ABOVE_FILTER")
    assert c2["realized_pnl"] == pytest.approx(-6.0) and led2["cash"] == pytest.approx(994.0)
    assert L.validate_ledger(led2)["valid"]


def test_funding_and_borrow_components_flow_to_cash_and_pnl():
    led = L.new_ledger(1000.0)
    L.open_position(led, _order("S", "BEAR_SHORT", 20.0))
    L.accrue_carry(led, "S", funding=0.4, borrow=0.1)
    assert led["cash"] == pytest.approx(950.0 - 0.5) and led["funding_paid"] == 0.4 and led["borrow_paid"] == 0.1
    c = L.close_position(led, "S", 20.0, "2026-07-10", "OUT_OF_RADAR")
    assert c["funding"] == 0.4 and c["borrow"] == 0.1 and c["realized_pnl"] == pytest.approx(-0.5)
    assert L.validate_ledger(led)["valid"]


def test_slippage_and_fees_are_separate_components():
    led = L.new_ledger(1000.0)
    L.open_position(led, _order("A", "LONG_ENTRY", 10.0, fee=0.3, slip=0.7))
    assert led["fees_paid"] == 0.3 and led["slippage_paid"] == 0.7
    L.close_position(led, "A", 10.0, "2026-07-10", "OUT_OF_RADAR", exit_fee=0.3, exit_slippage=0.7)
    assert led["fees_paid"] == pytest.approx(0.6) and led["slippage_paid"] == pytest.approx(1.4)
    assert led["closed"][0]["realized_pnl"] == pytest.approx(-2.0)


# --- rejections ----------------------------------------------------------------------------------

def test_one_position_per_asset_rejection():
    led = L.new_ledger(1000.0)
    L.open_position(led, _order("A", "LONG_ENTRY", 10.0))
    r = L.open_position(led, _order("A", "BEAR_SHORT", 10.0, decision_date="2026-07-03"))
    assert r["status"] == "REJECTED" and r["reason"] == "ONE_POSITION_PER_ASSET"


def test_duplicate_order_rejected():
    led = L.new_ledger(1000.0)
    L.open_position(led, _order("A", "LONG_ENTRY", 10.0))
    L.close_position(led, "A", 10.0, "2026-07-05", "OUT_OF_RADAR")
    r = L.open_position(led, _order("A", "LONG_ENTRY", 10.0))
    assert r["reason"] == "DUPLICATE_ORDER"


def test_exposure_cap_rejects_and_never_resizes():
    led = L.new_ledger(1000.0)
    for i in range(12):                                       # 12 x 8% = 96%
        assert L.open_position(led, _order("L%02d" % i, "LONG_ENTRY", 10.0, rank=i + 1, breakout=True))["status"] == "OPEN"
    r = L.open_position(led, _order("S1", "BEAR_SHORT", 10.0, rank=50))     # 96 + 5 > 100
    assert r["reason"] == "EXPOSURE_CAP_EXCEEDED"
    ok = L.open_position(led, _order("S2", "HEDGE_SHORT", 10.0, rank=51))   # 96 + 3 <= 100
    assert ok["status"] == "OPEN" and ok["size_pct_nav"] == 3.0
    assert L.snapshot(led)["gross_exposure_pct_nav"] == pytest.approx(99.0)


def test_insufficient_available_nav_is_distinct_from_the_exposure_cap():
    led = L.new_ledger(1000.0)
    for i in range(12):                                                        # 96% gross, cash 40
        L.open_position(led, _order("L%02d" % i, "LONG_ENTRY", 10.0, rank=i + 1, breakout=True))
    assert led["cash"] == pytest.approx(40.0)
    r = L.open_position(led, _order("H", "HEDGE_SHORT", 10.0, rank=50, fee=15.0))   # 30 + 15 > 40 cash; 99% <= cap
    assert r["reason"] == "INSUFFICIENT_AVAILABLE_NAV"
    ok = L.open_position(led, _order("H", "HEDGE_SHORT", 10.0, rank=50, decision_date="2026-07-02"))
    assert ok["status"] == "OPEN"


def test_invalid_price_and_unverified_instrument_rejections():
    led = L.new_ledger(1000.0)
    assert L.open_position(led, _order("A", "LONG_ENTRY", None))["reason"] == "INVALID_FILL_PRICE"
    assert L.open_position(led, _order("B", "BEAR_SHORT", 10.0, verified=False))["reason"] == "INSTRUMENT_UNVERIFIED"
    assert led["positions"] == {}


def test_size_override_that_differs_from_frozen_sizing_is_refused():
    led = L.new_ledger(1000.0)
    o = _order("A", "LONG_ENTRY", 10.0); o["size_pct_nav"] = 4.0
    with pytest.raises(ValueError):
        L.open_position(led, o)


# --- ordering / determinism ------------------------------------------------------------------------

def test_simultaneous_signals_apply_in_frozen_order_and_cap_hits_the_last():
    led = L.new_ledger(1000.0)
    orders = [_order("ZZZ", "LONG_ENTRY", 10.0, rank=3, breakout=True),
              _order("AAA", "LONG_ENTRY", 10.0, rank=3, breakout=True),
              _order("MMM", "LONG_ENTRY", 10.0, rank=1, breakout=True)]
    led["cash"] = 1000.0
    for i in range(11):
        L.open_position(led, _order("F%02d" % i, "LONG_ENTRY", 10.0, rank=100 + i, breakout=True))   # 88%
    res = L.process_orders(led, orders)
    assert [r["symbol"] for r in res] == ["MMM", "AAA", "ZZZ"]
    assert [r["status"] for r in res] == ["OPEN", "REJECTED", "REJECTED"]       # 88+8=96, then 104 > cap
    assert res[1]["reason"] == "EXPOSURE_CAP_EXCEEDED"


def test_deterministic_rerun_equality():
    def run():
        led = L.new_ledger(500.0)
        L.process_orders(led, [_order("B", "BEAR_SHORT", 3.0, rank=2), _order("A", "LONG_ENTRY", 2.0, rank=1, breakout=True)])
        L.accrue_carry(led, "B", funding=0.01)
        L.close_position(led, "A", 2.5, "2026-07-09", "LONG_BELOW_UPPER", exit_fee=0.1)
        return json.dumps(led, sort_keys=True)
    assert run() == run()


def test_snapshot_reports_all_required_fields_and_unmarked_positions():
    led = L.new_ledger(1000.0)
    L.open_position(led, _order("A", "LONG_ENTRY", 10.0))
    s = L.snapshot(led)
    for k in ("nav", "cash", "realized_pnl", "unrealized_pnl", "gross_exposure", "net_exposure",
              "open_positions", "fees_paid", "slippage_paid", "funding_paid", "borrow_paid"):
        assert k in s
    assert s["unmarked_positions"] == ["A"] and s["unrealized_pnl"] == 0.0
    assert L.snapshot(led, {"A": 11.0})["unmarked_positions"] == []


def test_validate_detects_tampering():
    led = L.new_ledger(1000.0)
    L.open_position(led, _order("A", "LONG_ENTRY", 10.0))
    bad = copy.deepcopy(led); bad["cash"] += 1.0
    assert L.validate_ledger(led)["valid"] and not L.validate_ledger(bad)["valid"]
