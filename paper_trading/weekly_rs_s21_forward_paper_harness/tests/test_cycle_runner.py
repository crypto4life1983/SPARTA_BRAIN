"""Tests for the stateful v2 cycle runner. Synthetic 48-name split_only CSVs written to tmp_path only; NO network,
NO fetch, NO broker, and the legacy runs/dry_cycle_001/002 outputs are never read for state nor written."""
import csv
import datetime as dt
import json
import math
import pathlib

import pytest

from paper_trading.weekly_rs_s21_forward_paper_harness import cycle_runner as cr
from paper_trading.weekly_rs_s21_forward_paper_harness.cycle import CycleNotAuthorized
from paper_trading.weekly_rs_s21_forward_paper_harness.manifest import DATA_SOURCES, DEFAULT_DATA_SOURCE, MANIFEST

UNI = MANIFEST["universe_48"]
SUFFIX = DATA_SOURCES[DEFAULT_DATA_SOURCE]["filename_suffix"]
LEADERS = UNI[:8]          # steady positive drift -> the default top-8
P = 200                    # first on-grid anchor used by most tests: (200-160) % 5 == 0
START = 100000.0


def business_calendar(n, start=dt.date(2024, 1, 2)):
    out, d = [], start
    while len(out) < n:
        if d.weekday() < 5:
            out.append(d.isoformat())
        d += dt.timedelta(days=1)
    return out


def drift_series(n, rate, px0=100.0):
    ser, px = [], px0
    for _ in range(n):
        ser.append(px); px *= (1.0 + rate)
    return ser


def default_universe(n):
    """8 leaders (UNI[0] strongest .. UNI[7] weakest positive drift) + 40 fillers with distinct slightly negative drifts."""
    prices = {}
    for k, sym in enumerate(UNI):
        if k < 8:
            prices[sym] = drift_series(n, 0.0010 - 0.0001 * k)      # 0.0010 .. 0.0003
        else:
            prices[sym] = drift_series(n, -0.0001 * (k - 7))        # -0.0001 .. -0.0040
    return prices


def write_universe(tmp_path, prices, cal, name="raw"):
    d = tmp_path / name; d.mkdir(parents=True, exist_ok=True)
    for sym in UNI:
        with open(d / (sym + SUFFIX), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(["date", "open", "high", "low", "close", "volume"])
            for date, c in zip(cal, prices[sym]):
                w.writerow([date, c, c, c, c, 1000])
    return d


def make_universe(tmp_path, n=305, overrides=None, name="raw"):
    prices = default_universe(n)
    for sym, ser in (overrides or {}).items():
        prices[sym] = ser
    cal = business_calendar(n)
    return write_universe(tmp_path, prices, cal, name), cal, prices


def run(state_dir, csv_dir, **kw):
    kw.setdefault("operator_authorized_dry_run", True)
    return cr.run_cycle(state_dir=state_dir, local_csv_dir=str(csv_dir), filename_suffix=SUFFIX, **kw)


# ------------------------------------------------------------------------------------------------------------
# authorization / safety / legacy protection
# ------------------------------------------------------------------------------------------------------------

def test_refuses_without_authorization(tmp_path):
    with pytest.raises(CycleNotAuthorized):
        cr.run_cycle(state_dir=tmp_path / "s", local_csv_dir=str(tmp_path), filename_suffix=SUFFIX)
    with pytest.raises(CycleNotAuthorized):
        cr.main(["--state-dir", str(tmp_path / "s"), "--local-csv-dir", str(tmp_path), "--filename-suffix", SUFFIX])
    assert not (tmp_path / "s").exists()


def test_default_state_dir_is_new_and_legacy_dirs_are_refused(tmp_path):
    assert cr.DEFAULT_STATE_DIR.name == "cycles_v2"
    legacy = cr.HARNESS_DIR / "runs"
    assert cr.DEFAULT_STATE_DIR != legacy / "dry_cycle_001" and cr.DEFAULT_STATE_DIR != legacy / "dry_cycle_002"
    with pytest.raises(ValueError, match="legacy dry_cycle"):
        cr.run_cycle(state_dir=tmp_path / "dry_cycle_002" / "x", operator_authorized_dry_run=True)


# ------------------------------------------------------------------------------------------------------------
# grid / staleness / integrity refusals
# ------------------------------------------------------------------------------------------------------------

def test_off_grid_anchor_is_refused_and_writes_nothing(tmp_path):
    d, cal, _ = make_universe(tmp_path)
    assert (203 - 160) % 5 == 3
    res = run(tmp_path / "s", d, asof_index=203)
    assert res["status"] == cr.STATUS_NO_TRADE_OFF_GRID and res["traded"] is False and res["cycles"] == []
    assert "OFF the rebalance grid" in res["reason"] and "200 / 205" in res["reason"]
    assert not (tmp_path / "s").exists()
    # the legacy cycle-001 anchor (idx 1758) is off-grid too: (1758-160) % 5 == 3 -> would be refused by v2
    assert (1758 - 160) % 5 == 3


def test_stale_data_is_no_trade_and_never_refreshes(tmp_path):
    d, cal, _ = make_universe(tmp_path)
    res = run(tmp_path / "s", d, asof_index=P, min_last_date="2099-01-01")
    assert res["status"] == cr.STATUS_STALE_DATA_NO_TRADE and res["traded"] is False
    assert "NOT refreshed" in res["reason"]
    res2 = run(tmp_path / "s", d, asof_date="2099-01-05")
    assert res2["status"] == cr.STATUS_STALE_DATA_NO_TRADE
    assert not (tmp_path / "s").exists()
    assert sorted(x.name for x in d.iterdir()) == sorted(s + SUFFIX for s in UNI)   # no new files in the data dir


def test_nan_close_in_window_is_data_integrity_no_trade(tmp_path):
    n = 305; prices = default_universe(n); prices["MU"][190] = float("nan")
    d = write_universe(tmp_path, prices, business_calendar(n))
    res = run(tmp_path / "s", d, asof_index=P)
    assert res["status"] == cr.STATUS_DATA_INTEGRITY_NO_TRADE and "MU bad close at 190" in res["reason"]
    assert not (tmp_path / "s").exists()


def test_check_data_integrity_and_shortfall_and_drag_helpers():
    cal = business_calendar(10); closes = {"A": [1.0] * 10, "B": [1.0] * 10}
    assert cr.check_data_integrity(closes, cal, 9, 5) == (True, [])
    closes["B"][7] = 0.0
    ok, problems = cr.check_data_integrity(closes, cal, 9, 5)
    assert not ok and "B bad close at 7" in problems[0]
    bad_cal = list(cal); bad_cal[5] = bad_cal[4]
    ok, problems = cr.check_data_integrity({"A": [1.0] * 10}, bad_cal, 9, 9)
    assert not ok and "not strictly increasing" in problems[0]
    assert cr.check_data_integrity(closes, cal, 10, 5)[0] is False
    # shortfall: positive = worse than reference, costs included
    buy = {"shares": 10.0, "fill_price": 101.0, "commission_usd": 0.0, "slippage_usd": 0.0}
    sell = {"shares": -10.0, "fill_price": 99.0, "commission_usd": 0.0, "slippage_usd": 0.0}
    assert cr.fill_shortfall_bps(buy, 100.0) == pytest.approx(100.0)
    assert cr.fill_shortfall_bps(sell, 100.0) == pytest.approx(100.0)
    same = {"shares": 10.0, "fill_price": 100.0, "commission_usd": 1.0, "slippage_usd": 0.1}
    assert cr.fill_shortfall_bps(same, 100.0) == pytest.approx(11.0)
    # cost drag: against CURRENT equity and elapsed TRADING days
    assert cr.annualized_cost_drag(100.0, 100000.0, 252) == pytest.approx(0.001)
    assert cr.annualized_cost_drag(100.0, 200000.0, 126) == pytest.approx(0.001)
    assert cr.holding_weeks(1758, 1860, 5) == pytest.approx(20.4)


# ------------------------------------------------------------------------------------------------------------
# state persistence + weekly return path
# ------------------------------------------------------------------------------------------------------------

def test_state_persistence_round_trip_and_weekly_return_path(tmp_path):
    d, cal, _ = make_universe(tmp_path); s = tmp_path / "s"
    r1 = run(s, d, asof_index=P)
    assert r1["status"] == cr.STATUS_OK and len(r1["cycles"]) == 1
    c1 = r1["cycles"][0]
    assert c1["selected_top8"] == LEADERS and c1["cycle"] == 1 and c1["weekly_return"] == 0.0
    assert c1["equity_before"] == START and c1["equity_after"] < START           # only costs on cycle 1
    assert c1["elapsed_trading_days"] == 5 and c1["annualized_cost_drag"] == pytest.approx((START - c1["equity_after"]) / c1["equity_after"] * 252 / 5, rel=1e-6)
    st = cr.load_state(s)
    assert st["cycles_completed"] == 1 and sorted(st["book"]["holdings"]) == sorted(LEADERS)
    assert st["last_asof_index"] == P and st["first_asof_index"] == P and st["drawdown"]["peak"] == START
    assert all(st["entry_meta"][sym]["entry_idx"] == P for sym in LEADERS)
    # round trip: book/tracker rebuilt from disk equal what was persisted
    book = cr.book_from_state(st); tr = cr.tracker_from_state(st)
    assert book.cash == st["book"]["cash"] and tr.peak == START and tr.max_dd == st["drawdown"]["max_dd"]
    assert cr.load_state(s) == json.loads(cr.state_path(s).read_text(encoding="utf-8"))
    assert not cr.state_path(s).with_suffix(".json.tmp").exists()

    r2 = run(s, d, asof_index=P + 5)
    c2 = r2["cycles"][0]
    assert r2["status"] == cr.STATUS_OK and c2["cycle"] == 2 and c2["bars_since_prev_cycle"] == 5 and r2["gap_event"] is False
    # weekly_return = previous cycle's equity_after -> this cycle's equity_before (the actual path), NOT same-bar
    assert c2["prev_equity_after"] == c1["equity_after"]
    assert c2["weekly_return"] == pytest.approx(c2["equity_before"] / c1["equity_after"] - 1.0, abs=1e-7)   # record fields are cent-rounded
    assert c2["weekly_return"] > 0.003                                              # leaders drifted up for 5 bars
    assert abs(c2["cycle_cost_return"]) < 1e-3                                      # same-bar cost effect kept separate
    assert c2["closed_trades"] == [] and all(o["action"] == "REBALANCE" for o in c2["orders"])
    st2 = cr.load_state(s)
    assert st2["cycles_completed"] == 2 and len(st2["equity_path"]) == 2 and st2["last_equity_after"] == pytest.approx(c2["equity_after"], abs=0.01)
    led = cr.read_ledgers(s)
    assert len(led["orders"]) == 2 and len(led["equity"]) == 2 and led["closed"] == []
    assert (s / "cycle_001" / "paper_weekly_report_001.md").exists() and (s / "cycle_002" / "killswitch_status.json").exists()
    # never duplicate a traded anchor
    r3 = run(s, d, asof_index=P + 5)
    assert r3["status"] == cr.STATUS_NO_TRADE_ANCHOR_NOT_NEWER and cr.load_state(s)["cycles_completed"] == 2


def test_default_anchor_is_latest_grid_bar(tmp_path):
    d, cal, _ = make_universe(tmp_path, n=303)   # last idx 302 -> latest grid bar 300
    r = run(tmp_path / "s", d)
    assert r["status"] == cr.STATUS_OK and r["cycles"][0]["asof_index"] == 300 and r["cycles"][0]["signal_date"] == cal[300]


# ------------------------------------------------------------------------------------------------------------
# gap handling
# ------------------------------------------------------------------------------------------------------------

def test_gap_without_replay_is_gap_no_trade(tmp_path):
    d, cal, _ = make_universe(tmp_path); s = tmp_path / "s"
    run(s, d, asof_index=P)
    before = cr.state_path(s).read_text(encoding="utf-8")
    r = run(s, d, asof_index=P + 20, replay_missed_rebalances=False)
    assert r["status"] == cr.STATUS_GAP_NO_TRADE and r["traded"] is False and r["gap_bars"] == 20
    assert r["missed_anchors"] == [P + 5, P + 10, P + 15]
    assert cr.state_path(s).read_text(encoding="utf-8") == before
    assert len(cr.read_ledgers(s)["orders"]) == 1


def test_gap_replay_runs_every_intermediate_rebalance_with_continuous_equity_and_dd_sees_intra_gap_low(tmp_path):
    # leader UNI[0] halves over bars P+12..P+17 (covers the P+15 rebalance bar) and recovers -> weekly sampling at
    # P+15 sees part of it, daily marks see the trough at P+13/P+14 which no rebalance bar touches.
    n = 305; lead = drift_series(n, 0.0010)
    for b in range(P + 12, P + 18):
        lead[b] = lead[b] * 0.5
    d, cal, _ = make_universe(tmp_path, n=n, overrides={UNI[0]: lead}); s = tmp_path / "s"
    r1 = run(s, d, asof_index=P)
    r = run(s, d, asof_index=P + 30)
    assert r["status"] == cr.STATUS_OK and r["gap_event"] is True
    assert [c["asof_index"] for c in r["cycles"]] == [P + 5, P + 10, P + 15, P + 20, P + 25, P + 30]
    assert [c["cycle"] for c in r["cycles"]] == [2, 3, 4, 5, 6, 7]
    assert all(c["bars_since_prev_cycle"] == 5 for c in r["cycles"])
    assert "gap replay" in r["cycles"][0]["fill_basis"] and "gap replay" not in r["cycles"][-1]["fill_basis"]
    # continuous equity path: each cycle starts from the previous cycle's equity_after
    prev = r1["cycles"][0]["equity_after"]
    for c in r["cycles"]:
        assert c["prev_equity_after"] == pytest.approx(prev, abs=0.01); prev = c["equity_after"]
    c4 = r["cycles"][2]
    assert c4["asof_index"] == P + 15 and c4["weekly_return"] < -0.04                # the dip is in the return series
    assert c4["min_daily_mark_since_prev"] < c4["equity_before"]                    # daily trough below the anchor mark
    st = cr.load_state(s)
    assert st["drawdown"]["max_dd"] >= 0.055                                         # ~1/8 * 50% seen via daily marks
    assert st["cycles_completed"] == 7 and len(cr.read_ledgers(s)["equity"]) == 7
    # the intermediate low is bigger than what the rebalance-bar samples alone would show
    equity_marks = [r1["cycles"][0]["equity_after"]] + [c["equity_before"] for c in r["cycles"]]
    peak = max(equity_marks[:3]); sampled_dd = (peak - min(equity_marks)) / peak
    assert st["drawdown"]["max_dd"] > sampled_dd


def test_gap_replay_falls_back_to_gap_no_trade_when_intermediate_data_is_missing(tmp_path):
    n = 305; prices = default_universe(n); prices["TXN"][P + 8] = float("nan")   # inside the P+10 replay window
    d = write_universe(tmp_path, prices, business_calendar(n)); s = tmp_path / "s"
    # cycle 1 at P is fine (window ends at P)
    assert run(s, d, asof_index=P)["status"] == cr.STATUS_OK
    r = run(s, d, asof_index=P + 20)
    assert r["status"] == cr.STATUS_GAP_NO_TRADE and "TXN bad close" in r["reason"]
    assert cr.load_state(s)["cycles_completed"] == 1 and cr.load_state(s)["halted"] is False


# ------------------------------------------------------------------------------------------------------------
# closed trades: holding_weeks from bar distance
# ------------------------------------------------------------------------------------------------------------

def test_holding_weeks_from_bar_distance_on_rotation(tmp_path):
    # filler VLO triples at bar 230 -> its 126-21 signal jumps at anchor 255 (uses closes[234]/closes[108]) and it
    # displaces the weakest leader UNI[7], which entered at P=200 and exits at 255: 55 bars = 11 weeks.
    n = 305; vlo = [100.0] * n
    for b in range(230, n):
        vlo[b] = 300.0
    d, cal, _ = make_universe(tmp_path, n=n, overrides={"VLO": vlo}); s = tmp_path / "s"
    run(s, d, asof_index=P)
    r = run(s, d, asof_index=255)
    assert r["status"] == cr.STATUS_OK and len(r["cycles"]) == 11
    assert all(c["closed_trades"] == [] for c in r["cycles"][:-1])
    last = r["cycles"][-1]
    assert "VLO" in last["selected_top8"] and UNI[7] not in last["selected_top8"]
    assert len(last["closed_trades"]) == 1
    ct = last["closed_trades"][0]
    assert ct["symbol"] == UNI[7] and ct["entry_idx"] == P and ct["exit_idx"] == 255 and ct["holding_bars"] == 55
    assert ct["holding_weeks"] == pytest.approx(11.0) and ct["entry_date"] == cal[P] and ct["exit_date"] == cal[255]
    assert ct["net_pnl_usd"] == pytest.approx(ct["entry_cashflow_usd"] + ct["exit_cashflow_usd"], abs=0.02)
    led = cr.read_ledgers(s)
    assert len(led["closed"]) == 1 and led["closed"][0]["holding_weeks"] == pytest.approx(11.0)
    st = cr.load_state(s)
    assert st["closed_trades_total"] == 1 and st["entry_meta"]["VLO"]["entry_idx"] == 255 and UNI[7] not in st["entry_meta"]


# ------------------------------------------------------------------------------------------------------------
# regression: the cycle_001 -> cycle_002 situation, one position doubling over 100 bars
# ------------------------------------------------------------------------------------------------------------

def test_regression_cycle001_to_002_gap_holding_weeks_and_return_path(tmp_path):
    n = 305; X = UNI[0]; B = UNI[1:8]; J = UNI[8:16]
    x = [50.0] * n
    for b in range(P - 147, P - 21):                       # 126-bar rise 50 -> 100 makes X top-ranked at P
        x[b] = 50.0 + 50.0 * (b - (P - 147)) / 126.0
    for b in range(P - 21, P):
        x[b] = 100.0
    for b in range(P, n):                                  # doubles over [P, P+100]
        x[b] = 100.0 * (2.0 ** (min(b - P, 100) / 100.0))
    overrides = {X: x}
    for sym in B:
        overrides[sym] = drift_series(n, 0.0008)
    for sym in J:                                          # flat, then x3 at P+75 -> rank above X only from anchor P+100
        ser = [100.0] * n
        for b in range(P + 75, n):
            ser[b] = 300.0
        overrides[sym] = ser
    d, cal, _ = make_universe(tmp_path, n=n, overrides=overrides); s = tmp_path / "s"
    r1 = run(s, d, asof_index=P)
    assert r1["status"] == cr.STATUS_OK and sorted(r1["cycles"][0]["selected_top8"]) == sorted([X] + B)
    r2 = run(s, d, asof_index=P + 100)
    assert r2["status"] == cr.STATUS_OK and r2["gap_event"] is True and len(r2["cycles"]) == 20
    assert [c["asof_index"] for c in r2["cycles"]] == list(range(P + 5, P + 101, 5))
    last = r2["cycles"][-1]
    assert sorted(last["selected_top8"]) == sorted(J)
    closed = last["closed_trades"]
    assert sorted(c["symbol"] for c in closed) == sorted([X] + B)
    for c in closed:
        assert c["holding_bars"] == 100 and c["holding_weeks"] == pytest.approx(20.0)   # NOT the hard-coded 1
    xt = next(c for c in closed if c["symbol"] == X)
    assert xt["exit_price"] == pytest.approx(200.0) and xt["entry_price"] == pytest.approx(100.0) and xt["net_pnl_usd"] > 0
    # the return series IS the path: compounding it reproduces the total move exactly
    cycles = r1["cycles"] + r2["cycles"]
    total_move = last["equity_after"] / START - 1.0
    # X doubled inside an 8-name equal-weight book that trims it back to 1/8 every rebalance: the total move must exceed
    # what the 7 steady names alone deliver (7/8 * (1.0008^100 - 1) ~ 7.3%) and stay below an untrimmed buy-and-hold (~19.8%).
    assert 0.10 < total_move < 0.20
    compounded = 1.0
    for c in cycles:
        compounded *= (1.0 + c["weekly_return_incl_costs"])
    assert compounded - 1.0 == pytest.approx(total_move, abs=1e-6)
    assert sum(math.log1p(c["weekly_return_incl_costs"]) for c in cycles) == pytest.approx(math.log1p(total_move), abs=1e-6)
    # the spec series (prev equity_after -> equity_before) differs from it only by the same-bar cost effect
    spec = 1.0
    for c in cycles:
        spec *= (1.0 + c["weekly_return"])
    assert abs((spec - 1.0) - total_move) < 21 * 5e-4
    simple_sum = sum(c["weekly_return"] for c in cycles)                               # the move entered the series:
    assert simple_sum > 0.10 and abs(simple_sum - total_move) < 0.02                    # simple sum ~ total (2nd-order gap only)
    st = cr.load_state(s)
    assert st["cycles_completed"] == 21 and st["closed_trades_total"] == 8 and cr._weeks_elapsed(st) == pytest.approx(21.0)
    assert st["drawdown"]["peak"] >= last["equity_before"]
    assert r2["gates"]["gates"]["12wk"]["status"] == cr.GATE_NOT_YET_EVALUABLE            # 8 closed < 15


# ------------------------------------------------------------------------------------------------------------
# gates
# ------------------------------------------------------------------------------------------------------------

def _gate_state(closed, weeks, max_dd=0.01, halted=False, drag=0.0):
    st = cr.new_state()
    st["closed_trades_total"] = closed; st["first_asof_index"] = 200; st["last_asof_index"] = 200 + 5 * (weeks - 1)
    st["drawdown"] = {"peak": 1.0, "max_dd": max_dd}; st["halted"] = halted
    st["equity_path"] = [{"annualized_cost_drag": drag}]
    return st


def test_gates_read_thresholds_from_manifest(monkeypatch):
    T = MANIFEST["gate_thresholds"]
    assert (T["gate_12wk_min_closed_trades"], T["gate_24wk_min_closed_trades"]) == (15, 35)
    g = cr.evaluate_gates(None)
    assert g["gates"]["12wk"]["status"] == cr.GATE_NOT_YET_EVALUABLE and g["gates"]["24wk"]["status"] == cr.GATE_NOT_YET_EVALUABLE
    assert g["closed_trades_total"] == 0 and g["weeks_elapsed"] == 0.0
    # below 15 closed -> not evaluable even after 12 weeks
    g = cr.evaluate_gates(_gate_state(14, 12))
    assert g["gates"]["12wk"]["status"] == cr.GATE_NOT_YET_EVALUABLE and g["gates"]["12wk"]["reason"] == "closed 14/15 trades, 12.0/12 weeks"
    # 15 closed but only 11 weeks -> not evaluable
    assert cr.evaluate_gates(_gate_state(15, 11))["gates"]["12wk"]["status"] == cr.GATE_NOT_YET_EVALUABLE
    g = cr.evaluate_gates(_gate_state(15, 12))
    assert g["gates"]["12wk"]["status"] == cr.GATE_PASS and g["gates"]["24wk"]["status"] == cr.GATE_NOT_YET_EVALUABLE
    assert g["gates"]["12wk"]["closed_trades"] == 15 and g["gates"]["24wk"]["min_closed_trades"] == 35
    g = cr.evaluate_gates(_gate_state(35, 24))
    assert g["gates"]["12wk"]["status"] == cr.GATE_PASS and g["gates"]["24wk"]["status"] == cr.GATE_PASS
    # FAIL logic once evaluable
    assert cr.evaluate_gates(_gate_state(35, 24, max_dd=0.31))["gates"]["24wk"] ["status"] == cr.GATE_FAIL
    assert "MAX_DRAWDOWN_GE_KILL" in cr.evaluate_gates(_gate_state(35, 24, max_dd=0.31))["gates"]["24wk"]["reason"]
    assert cr.evaluate_gates(_gate_state(35, 24, halted=True))["gates"]["12wk"]["reason"] == "KILLSWITCH_HALTED"
    assert cr.evaluate_gates(_gate_state(35, 24, drag=0.06))["gates"]["12wk"]["status"] == cr.GATE_FAIL
    # thresholds really come from manifest.py (not a copied literal)
    monkeypatch.setitem(T, "gate_12wk_min_closed_trades", 3)
    assert cr.evaluate_gates(_gate_state(3, 12))["gates"]["12wk"]["status"] == cr.GATE_PASS
    assert "PASS is a diagnostic read only" in cr.evaluate_gates.__doc__


# ------------------------------------------------------------------------------------------------------------
# kill-switch / mechanic drift / halt persistence
# ------------------------------------------------------------------------------------------------------------

def test_mechanic_drift_is_computed_and_halts(tmp_path, monkeypatch):
    d, cal, _ = make_universe(tmp_path); s = tmp_path / "s"
    r1 = run(s, d, asof_index=P)
    assert r1["cycles"][0]["mechanic_drift"] is False and r1["cycles"][0]["killswitch_metrics"]["mechanic_drift"] is False
    monkeypatch.setitem(MANIFEST["locked_mechanic"], "top_m_held", 7)
    assert cr.detect_mechanic_drift(cr.load_state(s))[0] is True
    r = run(s, d, asof_index=P + 5)
    assert r["status"] == cr.STATUS_NO_TRADE_MECHANIC_DRIFT and "top_m_held live=7 expected=8" in r["reason"]
    st = cr.load_state(s)
    assert st["halted"] is True and st["halt_reasons"] == ["MECHANIC_DRIFT_FROM_LOCKED_S21"] and st["cycles_completed"] == 1
    monkeypatch.setitem(MANIFEST["locked_mechanic"], "top_m_held", 8)
    # halt never auto-resumes
    assert run(s, d, asof_index=P + 5)["status"] == cr.STATUS_NO_TRADE_KILLSWITCH_HALTED
    with pytest.raises(ValueError):
        cr.resume_after_halt(s, "")
    st = cr.resume_after_halt(s, "operator: manifest restored; drift was a test injection")
    assert st["halted"] is False and st["halt_history"][-1]["operator_reason"].startswith("operator:")
    assert run(s, d, asof_index=P + 5)["status"] == cr.STATUS_OK


def test_killswitch_halt_from_drawdown_persists_and_blocks(tmp_path):
    # every leader collapses 60% at P+3 -> daily marks + P+5 anchor show a >= 30% drawdown -> kill
    n = 305; overrides = {}
    for k, sym in enumerate(LEADERS):
        ser = drift_series(n, 0.0010 - 0.0001 * k)
        for b in range(P + 3, n):
            ser[b] = ser[b] * 0.4
        overrides[sym] = ser
    d, cal, _ = make_universe(tmp_path, n=n, overrides=overrides); s = tmp_path / "s"
    run(s, d, asof_index=P)
    r = run(s, d, asof_index=P + 10)
    assert r["status"] == cr.STATUS_OK and r["halted"] is True and len(r["cycles"]) == 1     # stops at the halting cycle
    assert r["cycles"][0]["killswitch"]["halt"] is True and "DRAWDOWN_KILL_GE_30_PCT" in r["cycles"][0]["killswitch"]["reasons"]
    assert r["cycles"][0]["verdict"] == "HALT"
    st = cr.load_state(s)
    assert st["halted"] and st["cycles_completed"] == 2 and st["drawdown"]["max_dd"] >= 0.30
    assert run(s, d, asof_index=P + 10)["status"] == cr.STATUS_NO_TRADE_KILLSWITCH_HALTED
    assert cr.evaluate_gates(st)["checks"]["halted"] is True


def test_metrics_are_computed_not_literals(tmp_path):
    d, cal, _ = make_universe(tmp_path); s = tmp_path / "s"
    c = run(s, d, asof_index=P)["cycles"][0]
    m = c["killswitch_metrics"]
    # same-close fills: shortfall == pure cost bps, strictly positive, per-fill list present
    assert len(c["fill_shortfall_bps"]) == 8 and all(x > 0 for x in c["fill_shortfall_bps"])
    cost = sum(o["commission_usd"] + o["slippage_usd"] for o in c["orders"]); notional = sum(abs(o["shares"]) * o["fill_price"] for o in c["orders"])
    assert m["mean_shortfall_bps"] == pytest.approx(cost / notional * 1e4, abs=1e-3) and 0 < m["mean_shortfall_bps"] < 5   # notional-weighted
    assert c["shortfall_weighting"] == "notional" and c["notional_traded_usd_cycle"] == pytest.approx(notional, abs=0.05)
    assert m["annualized_cost_drag"] == c["annualized_cost_drag"] > 0
    assert c["data_integrity_ok"] is True and m["data_integrity_ok"] is True and m["mechanic_drift"] is False
    assert m["trailing_expectancy"] is None and c["killswitch"]["status"] == "GREEN"
    ks = json.loads((s / "cycle_001" / "killswitch_status.json").read_text(encoding="utf-8"))
    assert ks["metrics"]["mean_shortfall_bps"] == pytest.approx(m["mean_shortfall_bps"]) and ks["result"] == c["killswitch"]
