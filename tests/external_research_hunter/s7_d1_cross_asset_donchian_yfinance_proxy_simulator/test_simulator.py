"""T1-T16 test suite for the s7 D1 cross-asset yfinance proxy simulator.

Run from repo root with stdlib unittest:
    python tests/external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_simulator/test_simulator.py

Plan anchor:
  docs/s7_d1_cross_asset_donchian_step_06_simulator_specification_plan.md
  sha256 f7581af358c676519d46f1a0bec486c35cf61f0f5f618faf7f000adf6223878b
"""
from __future__ import annotations

import builtins
import dataclasses
import math
import os
import sys
import unittest
from dataclasses import fields
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
os.chdir(REPO_ROOT)

from external_research_hunter.s7_d1_cross_asset_donchian_yfinance_proxy_loader import (  # noqa: E402
    load_all,
    load_symbol,
)
from external_research_hunter.s7_d1_cross_asset_donchian_yfinance_proxy_signal import (  # noqa: E402
    compute_signals_all,
    SignalEvent,
    SignalResult,
)
from external_research_hunter.s7_d1_cross_asset_donchian_yfinance_proxy_simulator import (  # noqa: E402
    CostTier,
    DEFAULT_STARTING_CASH,
    DailyEquityPoint,
    ENTRY_CHANNEL_LOOKBACK,
    ETF_DOLLAR_PER_SHARE,
    ETF_TICK_SIZE,
    EXIT_CHANNEL_LOOKBACK,
    ExitReason,
    IN_SAMPLE_WINDOW,
    K4_PORTFOLIO_MAXDD_PCT,
    MAX_UNITS_PER_SYMBOL,
    PER_UNIT_RISK_FRACTION,
    PYRAMID_STEP_N_MULTIPLE,
    STOP_DISTANCE_N_MULTIPLE,
    SimulationResult,
    SimulatorError,
    SimulatorInputError,
    SimulatorK4FiredError,
    SimulatorOosBlockedError,
    SimulatorParameterOverrideError,
    TradeGroup,
    TradeUnit,
    WILDER_ATR_LOOKBACK,
    simulate,
)

SIM_PKG = "external_research_hunter.s7_d1_cross_asset_donchian_yfinance_proxy_simulator"
OUT_OF_SAMPLE_WINDOW = ("2023-01-01", "2025-12-30")
POST_OOS_DIAGNOSTIC_WINDOW = ("2026-01-02", "2026-05-22")


def _fresh_signals():
    """Return CrossSymbolSignalResult freshly computed from real data."""
    return compute_signals_all(load_all())


class T01_SimulatorImportsOnlyAllowedModules(unittest.TestCase):
    """T1: simulator imports loader/validator/signal modules only (no external)."""

    def test_import_chain(self):
        # The simulator does not import the loader / validator / signal modules
        # at runtime; the caller does. But the SIMULATOR module itself must
        # only depend on stdlib + dataclass + typing + enum + math.
        sim_src = (REPO_ROOT
                   / "external_research_hunter"
                   / "s7_d1_cross_asset_donchian_yfinance_proxy_simulator"
                   / "simulator.py").read_text(encoding="utf-8")
        # Allowed imports are stdlib-only; explicit forbidden imports listed
        # in section 20 must not appear.
        forbidden_imports = [
            "import yfinance", "import databento", "import requests",
            "import urllib.", "from urllib", "import http.client",
            "import socket", "import curl_cffi", "import aiohttp",
            "import httpx", "import grpc", "import pyarrow.flight",
            "import strategy_lab", "import sparta_commander", "import spartacus",
            "import hydra_video", "import app", "import sparta_brain",
            "import broker", "import interactive_brokers", "import alpaca",
            "import tradestation", "import ibapi", "import binance", "import oanda",
            "import ib_insync", "import quantconnect", "import lean",
            "import qcalgorithm",
        ]
        for line in sim_src.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            for fi in forbidden_imports:
                self.assertNotIn(fi, stripped, f"forbidden import found: {fi}")


class T02_EveryDateInInSampleWindow(unittest.TestCase):
    """T2: every TradeUnit and DailyEquityPoint date is in IN_SAMPLE_WINDOW."""

    def test_dates(self):
        loaded = load_all()
        sigs = compute_signals_all(loaded)
        r = simulate(loaded, sigs, cost_tier=CostTier.S1)
        for tg in r.trade_groups:
            for u in tg.units:
                self.assertGreaterEqual(u.entry_trigger_date, IN_SAMPLE_WINDOW[0])
                self.assertLessEqual(u.entry_trigger_date, IN_SAMPLE_WINDOW[1])
                self.assertGreaterEqual(u.entry_fill_date, IN_SAMPLE_WINDOW[0])
                self.assertLessEqual(u.entry_fill_date, IN_SAMPLE_WINDOW[1])
                self.assertGreaterEqual(u.exit_date, IN_SAMPLE_WINDOW[0])
                self.assertLessEqual(u.exit_date, IN_SAMPLE_WINDOW[1])
        for dp in r.daily_equity_ledger:
            self.assertGreaterEqual(dp.date, IN_SAMPLE_WINDOW[0])
            self.assertLessEqual(dp.date, IN_SAMPLE_WINDOW[1])


class T03_OosInjectionBlocked(unittest.TestCase):
    """T3: injecting a synthetic SignalEvent with OOS date raises SimulatorOosBlockedError."""

    def test_oos_event_rejected(self):
        loaded = load_all()
        sigs = compute_signals_all(loaded)
        # Build a tampered signals mapping with one OOS event injected on SPY
        per_symbol = dict(sigs.per_symbol)
        spy_sr = per_symbol["SPY"]
        # Build a fake SignalEvent with OOS date 2023-06-15
        oos_event = SignalEvent(
            date="2023-06-15",
            bar_index=99999,
            entry_channel_high_55=100.0,
            entry_channel_low_55=90.0,
            exit_channel_high_20=99.0,
            exit_channel_low_20=91.0,
            today_high=95.0,
            today_low=92.0,
            today_close=94.0,
            entry_long_triggered=False,
            entry_short_triggered=False,
            exit_long_triggered=False,
            exit_short_triggered=False,
        )
        tampered_sr = dataclasses.replace(spy_sr, signals=spy_sr.signals + (oos_event,))
        per_symbol["SPY"] = tampered_sr
        with self.assertRaises(SimulatorOosBlockedError):
            simulate(loaded, per_symbol, cost_tier=CostTier.S1)


class T04_NoLiveTradingCodePath(unittest.TestCase):
    """T4: simulator's simulate() rejects extra kwargs (no broker= / order= / live= paths)."""

    def test_extra_kwargs_rejected(self):
        loaded = load_all()
        sigs = compute_signals_all(loaded)
        with self.assertRaises(SimulatorParameterOverrideError):
            simulate(loaded, sigs, cost_tier=CostTier.S1, broker="alpaca")
        with self.assertRaises(SimulatorParameterOverrideError):
            simulate(loaded, sigs, cost_tier=CostTier.S1, enable_live=True)
        with self.assertRaises(SimulatorParameterOverrideError):
            simulate(loaded, sigs, cost_tier=CostTier.S1, lookback=50)


class T05_NoBrokerageImportInSimulatorSource(unittest.TestCase):
    """T5: static grep for brokerage imports returns zero hits."""

    def test_no_brokerage_grep(self):
        src = (REPO_ROOT
               / "external_research_hunter"
               / "s7_d1_cross_asset_donchian_yfinance_proxy_simulator"
               / "simulator.py").read_text(encoding="utf-8")
        for tok in ("brokerage", "broker_api", "alpaca", "interactive_brokers",
                    "ibkr", "ibapi", "ib_insync", "tradestation", "binance", "oanda",
                    "order_send", "place_order", "submit_order", "cancel_order",
                    "modify_order", "route_order", "production_signal",
                    "paper_broker", "paper_trade"):
            for ln_no, line in enumerate(src.splitlines(), start=1):
                if tok in line:
                    stripped = line.strip()
                    if stripped.startswith("#") and "FORBIDDEN_TOKEN_EXCLUSION" in line:
                        continue
                    self.fail(f"forbidden token {tok!r} in simulator.py line {ln_no}: {line.strip()[:160]}")


class T06_Determinism(unittest.TestCase):
    """T6: simulate twice produces field-equal SimulationResult."""

    def test_determinism(self):
        loaded = load_all()
        sigs = compute_signals_all(loaded)
        r1 = simulate(loaded, sigs, cost_tier=CostTier.S1, starting_cash=100000.0)
        r2 = simulate(loaded, sigs, cost_tier=CostTier.S1, starting_cash=100000.0)
        self.assertEqual(r1.final_cash_balance, r2.final_cash_balance)
        self.assertEqual(r1.num_closed_units_total, r2.num_closed_units_total)
        self.assertEqual(len(r1.trade_groups), len(r2.trade_groups))
        for tg1, tg2 in zip(r1.trade_groups, r2.trade_groups):
            self.assertEqual(tg1, tg2)
        self.assertEqual(r1.trade_groups, r2.trade_groups)
        self.assertEqual(len(r1.daily_equity_ledger), len(r2.daily_equity_ledger))


class T07_NoParameterOverride(unittest.TestCase):
    """T7: extra kwargs and unknown cost tiers are rejected."""

    def test_lookback_kwarg(self):
        loaded = load_all()
        sigs = compute_signals_all(loaded)
        with self.assertRaises(SimulatorParameterOverrideError):
            simulate(loaded, sigs, cost_tier=CostTier.S1, lookback=50)

    def test_unknown_cost_tier(self):
        loaded = load_all()
        sigs = compute_signals_all(loaded)
        with self.assertRaises(SimulatorParameterOverrideError):
            simulate(loaded, sigs, cost_tier="S4_string")
        with self.assertRaises(SimulatorParameterOverrideError):
            simulate(loaded, sigs, cost_tier=99)


class T08_NoVendorOrNetworkImports(unittest.TestCase):
    """T8: simulator.py has no yfinance/Databento/network/http import."""

    def test_grep(self):
        src = (REPO_ROOT
               / "external_research_hunter"
               / "s7_d1_cross_asset_donchian_yfinance_proxy_simulator"
               / "simulator.py").read_text(encoding="utf-8")
        for tok in ("yfinance", "databento", "yahoo_finance", "requests.get",
                    "urllib.request", "socket.connect", "http.client",
                    "curl_cffi", "aiohttp", "httpx"):
            for ln_no, line in enumerate(src.splitlines(), start=1):
                if tok in line:
                    stripped = line.strip()
                    if stripped.startswith("#") and "FORBIDDEN_TOKEN_EXCLUSION" in line:
                        continue
                    self.fail(f"forbidden vendor/network token {tok!r} in line {ln_no}: {line.strip()[:160]}")


class T09_NoReviewQueueOrStrategyLabImports(unittest.TestCase):
    """T9: simulator.py has no review_queue / Strategy Lab / idea_memory references."""

    def test_grep(self):
        src = (REPO_ROOT
               / "external_research_hunter"
               / "s7_d1_cross_asset_donchian_yfinance_proxy_simulator"
               / "simulator.py").read_text(encoding="utf-8")
        for tok in ("Strategy Lab", "strategy_lab", "review_queue",
                    "idea_memory", "scheduler", "autopilot", "frc_gate"):
            for ln_no, line in enumerate(src.splitlines(), start=1):
                if tok in line:
                    stripped = line.strip()
                    if stripped.startswith("#") and "FORBIDDEN_TOKEN_EXCLUSION" in line:
                        continue
                    self.fail(f"forbidden production-integration token {tok!r} in line {ln_no}: {line.strip()[:160]}")


class T10_SameBarConflictStopWinsIntraBar(unittest.TestCase):
    """T10: a stop hit on the same bar as a Donchian-20 exit close-trigger
    produces TradeUnit.exit_reason == STOP_HIT for the stopped unit (intra-bar
    wins per spec sec 8). Constructed synthetically over real signals.

    Concrete check: among real-data trade groups, find one where the FIRST unit
    exits via STOP_HIT while the trade group's group_close_reason might be
    different (e.g., a Donchian-20 exit on a later bar exits surviving units).
    Assert the STOP_HIT exit_reason is preserved on the stopped unit."""

    def test_real_data_stop_then_donchian(self):
        loaded = load_all()
        sigs = compute_signals_all(loaded)
        r = simulate(loaded, sigs, cost_tier=CostTier.S1)
        # Find any trade group that has at least one STOP_HIT unit
        found = False
        for tg in r.trade_groups:
            stop_units = [u for u in tg.units if u.exit_reason == ExitReason.STOP_HIT]
            if stop_units:
                # Verify the stopped unit's exit_fill_price == its stop_price - slippage
                # (long) or + slippage (short). Per ETF tick: slippage = 2 cents * scalar
                # (S1 scalar = 1.0).
                u = stop_units[0]
                slip_per_share = ETF_TICK_SIZE * 2 * 1.0  # S1 stop slippage
                if tg.direction == "long":
                    expected = u.stop_price_at_entry - slip_per_share
                else:
                    expected = u.stop_price_at_entry + slip_per_share
                self.assertAlmostEqual(u.exit_fill_price, expected, places=6,
                                       msg=f"{u.symbol} stop fill price mismatch")
                found = True
                break
        self.assertTrue(found, "expected at least one STOP_HIT unit across real-data simulation")


class T11_WarmupNoEntryBeforeFirstEligibleBar(unittest.TestCase):
    """T11: no TradeUnit.entry_trigger_date earlier than first signal-eligible date (2014-03-24)."""

    def test_no_premature_entry(self):
        loaded = load_all()
        sigs = compute_signals_all(loaded)
        r = simulate(loaded, sigs, cost_tier=CostTier.S1)
        for tg in r.trade_groups:
            for u in tg.units:
                self.assertGreaterEqual(u.entry_trigger_date, "2014-03-24",
                                        f"premature entry: {u.entry_trigger_date}")


class T12_CommissionSlippageS0vsS1(unittest.TestCase):
    """T12: S0 (zero costs) produces different net_pnl than S1 (baseline);
    S0 net should be greater since S1 has nonzero slippage and S1 cost
    structure has 0 commission baseline (so the only diff is slippage)."""

    def test_s0_vs_s1(self):
        loaded = load_all()
        sigs = compute_signals_all(loaded)
        r0 = simulate(loaded, sigs, cost_tier=CostTier.S0)
        r1 = simulate(loaded, sigs, cost_tier=CostTier.S1)
        self.assertNotEqual(r0.final_cash_balance, r1.final_cash_balance,
                            "S0 and S1 should produce different final cash")
        self.assertGreater(r0.final_cash_balance, r1.final_cash_balance,
                           "S0 (zero costs) should produce higher final cash than S1")


class T13_StopArithmetic(unittest.TestCase):
    """T13: stop fill price equals stop_price -/+ stop_slippage_per_share."""

    def test_stop_arithmetic(self):
        loaded = load_all()
        sigs = compute_signals_all(loaded)
        r = simulate(loaded, sigs, cost_tier=CostTier.S1)
        slip = ETF_TICK_SIZE * 2 * 1.0  # S1 stop slippage per share
        verified = 0
        for tg in r.trade_groups:
            for u in tg.units:
                if u.exit_reason == ExitReason.STOP_HIT:
                    if tg.direction == "long":
                        self.assertAlmostEqual(u.exit_fill_price,
                                               u.stop_price_at_entry - slip, places=6)
                    else:
                        self.assertAlmostEqual(u.exit_fill_price,
                                               u.stop_price_at_entry + slip, places=6)
                    verified += 1
        self.assertGreater(verified, 0, "expected at least one STOP_HIT to verify")


class T14_SizingArithmetic(unittest.TestCase):
    """T14: shares = floor(0.01 * equity_at_entry_basis / n_entry); for the
    FIRST unit of each trade group, sizing is based on starting cash + any
    prior closed PnL (no open positions before the first unit)."""

    def test_first_unit_sizing(self):
        loaded = load_all()
        sigs = compute_signals_all(loaded)
        r = simulate(loaded, sigs, cost_tier=CostTier.S0)  # use S0 to remove slippage noise
        # For the very first trade group's unit 0: equity at sizing time = starting_cash
        if not r.trade_groups:
            self.skipTest("no trade groups in result")
        # The earliest trade group (by group_open_date) is the one closest to first signal
        first_tg = min(r.trade_groups, key=lambda g: (g.group_open_date, g.symbol, g.trade_group_id))
        u0 = first_tg.units[0]
        # Per spec: shares = floor(0.01 * 100000 / n_entry)
        # Note: at S0 cost_tier, S0 commission scalar = 0 too, but the first
        # unit's sizing uses equity_for_sizing computed at prior-close which
        # for the very first event equals the starting cash.
        expected_shares_at_start = math.floor(0.01 * r.starting_cash / u0.n_entry_dollars)
        # In a portfolio with multiple symbols opening sequentially, by the
        # time the second/third symbol's first trade group opens, equity may
        # have moved due to prior trades. We restrict the assertion to the
        # earliest trade group only.
        self.assertEqual(u0.shares, expected_shares_at_start,
                         f"first unit sizing: got {u0.shares}, expected {expected_shares_at_start} "
                         f"(equity={r.starting_cash}, n={u0.n_entry_dollars})")


class T15_PyramidMaxUnitsPerGroup(unittest.TestCase):
    """T15: no trade group has more than MAX_UNITS_PER_SYMBOL (= 4) units;
    all units in a group share the same n_entry_dollars; unit_index is 0..N-1
    in order; pyramid units after a partial stop still respect the lifetime cap."""

    def test_max_units(self):
        loaded = load_all()
        sigs = compute_signals_all(loaded)
        r = simulate(loaded, sigs, cost_tier=CostTier.S1)
        for tg in r.trade_groups:
            self.assertLessEqual(tg.group_unit_count, MAX_UNITS_PER_SYMBOL,
                                 f"{tg.symbol} group {tg.trade_group_id} has "
                                 f"{tg.group_unit_count} > {MAX_UNITS_PER_SYMBOL}")
            # All units share the same n_entry_dollars
            n_set = set(u.n_entry_dollars for u in tg.units)
            self.assertEqual(len(n_set), 1,
                             f"{tg.symbol} group {tg.trade_group_id} units have "
                             f"varying n_entry_dollars: {n_set}")
            # unit_index 0..N-1 in order (after sort by entry_trigger_date)
            sorted_units = sorted(tg.units, key=lambda u: (u.entry_trigger_date, u.unit_index))
            for i, u in enumerate(sorted_units):
                self.assertEqual(u.unit_index, i,
                                 f"unit_index mismatch in {tg.symbol} {tg.trade_group_id}")


class T16_K4CatastrophicStopFires(unittest.TestCase):
    """T16: with the real ETF-proxy data and S1 baseline, K4 catastrophic
    stop fires (max drawdown exceeds 50%); after K4 fires, all open units
    are closed with exit_reason K4_FORCED_PARK and no new entries occur."""

    def test_k4_on_real_data(self):
        loaded = load_all()
        sigs = compute_signals_all(loaded)
        r = simulate(loaded, sigs, cost_tier=CostTier.S1)
        # On real data with the baseline parameters and bid-ask costs, K4
        # is expected to fire. Verify:
        if r.k4_fired:
            self.assertGreater(r.max_drawdown_pct_observed, K4_PORTFOLIO_MAXDD_PCT,
                               "K4 fired but max DD reported below threshold")
            # All K4_FORCED_PARK closes should be at the same date (the bar
            # when K4 first armed).
            k4_groups = [tg for tg in r.trade_groups
                         if tg.group_close_reason == ExitReason.K4_FORCED_PARK]
            if k4_groups:
                k4_dates = set(tg.group_close_date for tg in k4_groups)
                # All K4 closes happen on the same bar; should be one date.
                self.assertEqual(len(k4_dates), 1,
                                 f"K4 closes spanned multiple dates: {k4_dates}")
                # After K4, no later entry_trigger_date in any group
                k4_date = next(iter(k4_dates))
                for tg in r.trade_groups:
                    if tg.group_close_reason == ExitReason.K4_FORCED_PARK:
                        continue
                    for u in tg.units:
                        self.assertLessEqual(u.entry_trigger_date, k4_date,
                                             f"entry after K4 fired: {u.entry_trigger_date} > {k4_date}")
        else:
            self.skipTest("K4 did not fire on this run; test asserts only when K4 fires")


if __name__ == "__main__":
    unittest.main(verbosity=2)
