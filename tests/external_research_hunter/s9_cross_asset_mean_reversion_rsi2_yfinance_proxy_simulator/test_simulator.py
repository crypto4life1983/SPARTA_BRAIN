"""T1-T16 test suite for the s9 RSI-2 simulator module.

Renames forbidden. Each top-level TestCase class is prefixed Tnn_ so the
build orchestrator can map result rows to T-IDs.
"""
from __future__ import annotations

import builtins
import dataclasses
import sys
import unittest
from pathlib import Path
from typing import Mapping

# Make the repo importable regardless of how the test runner is launched.
REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from external_research_hunter.s7_d1_cross_asset_donchian_yfinance_proxy_loader import (
    load_all, load_symbol,
)
from external_research_hunter.s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_signal import (
    SignalEvent,
    SignalResult,
    CrossSymbolSignalResult,
    compute_signals,
    compute_signals_all,
)
from external_research_hunter.s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_simulator import (
    CostTier,
    DailyEquityPoint,
    ExitReason,
    IN_SAMPLE_WINDOW,
    K4_PORTFOLIO_MAXDD_PCT,
    MAX_UNITS_PER_SYMBOL,
    PER_SIGNAL_ALLOCATION_FRACTION,
    RSI_EXIT_THRESHOLD,
    RSI_LOOKBACK,
    RSI_OVERSOLD_ENTRY_THRESHOLD,
    SimulationResult,
    SimulatorError,
    SimulatorInputError,
    SimulatorK4FiredError,
    SimulatorOosBlockedError,
    SimulatorParameterOverrideError,
    TradeRecord,
    simulate,
)


# Shared fixture cached at module-import scope (loader/signal computation
# is deterministic; loading once is acceptable for a unittest run).
_DATA = load_all()
_SIG = compute_signals_all(_DATA)


def _run_all_tiers():
    return {
        tier: simulate(_DATA, _SIG, cost_tier=tier)
        for tier in (CostTier.S0, CostTier.S1, CostTier.S2, CostTier.S3)
    }


class T01_SchemaAndTierSensitivity(unittest.TestCase):
    def test_schema(self):
        r = simulate(_DATA, _SIG, cost_tier=CostTier.S1)
        self.assertIsInstance(r, SimulationResult)
        self.assertGreater(r.num_closed_trades_total, 0)
        self.assertEqual(r.cost_tier, "S1")
        self.assertEqual(r.in_sample_window, IN_SAMPLE_WINDOW)
        self.assertEqual(
            r.per_signal_allocation_fraction, PER_SIGNAL_ALLOCATION_FRACTION,
        )

    def test_tier_sensitivity(self):
        all_r = _run_all_tiers()
        # Final cash should differ monotonically with cost: as slippage
        # rises (S0 -> S1 -> S2 -> S3), final cash should not increase.
        cashes = [all_r[t].final_cash_balance
                  for t in (CostTier.S0, CostTier.S1, CostTier.S2, CostTier.S3)]
        for a, b in zip(cashes, cashes[1:]):
            self.assertGreaterEqual(a, b,
                f"cash should be non-increasing across tiers: {cashes}")


class T02_TradeRecordISOnlyDates(unittest.TestCase):
    def test_record_dates_in_is(self):
        r = simulate(_DATA, _SIG, cost_tier=CostTier.S1)
        for rec in r.trade_records:
            for d in (rec.entry_trigger_date, rec.entry_fill_date,
                      rec.exit_trigger_date, rec.exit_fill_date):
                self.assertGreaterEqual(d, IN_SAMPLE_WINDOW[0])
                self.assertLessEqual(d, IN_SAMPLE_WINDOW[1])


class T03_DailyEquityPointISOnlyDates(unittest.TestCase):
    def test_daily_points_in_is(self):
        r = simulate(_DATA, _SIG, cost_tier=CostTier.S1)
        self.assertGreater(len(r.daily_equity_ledger), 0)
        for pt in r.daily_equity_ledger:
            self.assertGreaterEqual(pt.date, IN_SAMPLE_WINDOW[0])
            self.assertLessEqual(pt.date, IN_SAMPLE_WINDOW[1])


class T04_FirstSignalDateAlignment(unittest.TestCase):
    def test_first_signal_date(self):
        r = simulate(_DATA, _SIG, cost_tier=CostTier.S1)
        self.assertEqual(r.first_signal_date_processed, "2014-01-06")
        # Last signal date must be the latest IS event from the signal
        # module; cross-symbol-aligned should match across symbols.
        per_sym_last = sorted(
            _SIG.per_symbol[s].last_signal_eligible_date
            for s in ("SPY", "TLT", "GLD", "USO")
        )
        self.assertEqual(r.last_signal_date_processed, per_sym_last[-1])
        self.assertLessEqual(r.last_signal_date_processed, IN_SAMPLE_WINDOW[1])


class T05_ExitReasonInvariant(unittest.TestCase):
    def test_only_three_legitimate_exit_reasons(self):
        allowed = {
            ExitReason.RSI_EXIT_TRIGGER,
            ExitReason.K4_FORCED_PARK,
            ExitReason.IN_SAMPLE_END_FLAT,
        }
        for tier in (CostTier.S0, CostTier.S1, CostTier.S2, CostTier.S3):
            r = simulate(_DATA, _SIG, cost_tier=tier)
            for rec in r.trade_records:
                self.assertIn(rec.exit_reason, allowed,
                    f"forbidden exit reason {rec.exit_reason}")


class T06_SimulatorInputError_BadLoaded(unittest.TestCase):
    def test_non_mapping_loaded(self):
        with self.assertRaises(SimulatorInputError):
            simulate(None, _SIG, cost_tier=CostTier.S1)
        with self.assertRaises(SimulatorInputError):
            simulate("not a mapping", _SIG, cost_tier=CostTier.S1)

    def test_wrong_keys(self):
        bad = {"SPY": _DATA["SPY"], "FOO": _DATA["TLT"]}
        with self.assertRaises(SimulatorInputError):
            simulate(bad, _SIG, cost_tier=CostTier.S1)


class T07_SimulatorInputError_BadSignals(unittest.TestCase):
    def test_non_mapping_signals(self):
        with self.assertRaises(SimulatorInputError):
            simulate(_DATA, None, cost_tier=CostTier.S1)
        with self.assertRaises(SimulatorInputError):
            simulate(_DATA, 12345, cost_tier=CostTier.S1)

    def test_signal_wrong_keys(self):
        bad = {"SPY": _SIG.per_symbol["SPY"], "FOO": _SIG.per_symbol["TLT"]}
        with self.assertRaises(SimulatorInputError):
            simulate(_DATA, bad, cost_tier=CostTier.S1)


class T08_OosInjectionRefusal(unittest.TestCase):
    def test_synthetic_oos_event_raises(self):
        # Build a synthetic SignalResult with one OOS-dated event and
        # confirm the simulator HALTs.
        spy = _SIG.per_symbol["SPY"]
        bad_event = SignalEvent(
            date="2023-06-15",
            bar_index=spy.signals[-1].bar_index + 100,
            rsi_value=5.0,
            today_adj_close=400.0,
            entry_long_triggered=True,
            exit_long_triggered=False,
        )
        bad_sig = SignalResult(
            symbol=spy.symbol,
            csv_sha256_observed=spy.csv_sha256_observed,
            window=spy.window,
            bars_in_window=spy.bars_in_window,
            first_signal_eligible_bar_index=spy.first_signal_eligible_bar_index,
            first_signal_eligible_date=spy.first_signal_eligible_date,
            last_signal_eligible_bar_index=spy.last_signal_eligible_bar_index,
            last_signal_eligible_date=spy.last_signal_eligible_date,
            signals=tuple(list(spy.signals) + [bad_event]),
            oos_signal_intentionally_omitted=True,
            post_oos_signal_intentionally_omitted=True,
        )
        bad_map = dict(_SIG.per_symbol)
        bad_map["SPY"] = bad_sig
        with self.assertRaises(SimulatorOosBlockedError):
            simulate(_DATA, bad_map, cost_tier=CostTier.S1)


class T09_ParameterOverrideRefusal(unittest.TestCase):
    def test_unknown_kwarg_enable_short(self):
        with self.assertRaises(SimulatorParameterOverrideError):
            simulate(_DATA, _SIG, cost_tier=CostTier.S1, enable_short=True)

    def test_unknown_kwarg_window(self):
        with self.assertRaises(SimulatorParameterOverrideError):
            simulate(_DATA, _SIG, cost_tier=CostTier.S1,
                     window=("2024-01-01", "2025-12-31"))

    def test_unknown_kwarg_borrow(self):
        with self.assertRaises(SimulatorParameterOverrideError):
            simulate(_DATA, _SIG, cost_tier=CostTier.S1, borrow_cost_bps=25)

    def test_non_costtier_value(self):
        with self.assertRaises(SimulatorParameterOverrideError):
            simulate(_DATA, _SIG, cost_tier="S1")


class T10_DataclassFieldNameStructuralInvariants(unittest.TestCase):
    """Verify TradeRecord / DailyEquityPoint / SimulationResult have NO
    field suggestive of forbidden downstream computation, and DO have
    the expected execution-layer fields."""

    FORBIDDEN_FRAGMENTS = (
        "sharpe", "sortino", "calmar", "expectancy", "win_rate",
        "correl", "covar", "pairwise_depend", "effective_independent",
        "donchian", "atr(", "wilder",
        "stop_distance", "stop_price",
        "entry_short", "exit_short", "borrow",
        "daily_return", "log_return", "pct_return", "return_series",
    )
    EXPECTED_TRADE_FIELDS = (
        "symbol", "trade_id", "direction",
        "entry_trigger_date", "entry_fill_date", "entry_fill_price",
        "entry_slippage_dollars", "shares",
        "exit_trigger_date", "exit_fill_date", "exit_fill_price",
        "exit_slippage_dollars", "exit_reason",
        "commission_dollars",
        "gross_pnl_dollars", "net_pnl_dollars", "hold_days",
    )
    EXPECTED_DAILY_FIELDS = (
        "date", "cash_balance", "open_positions_count_total",
        "open_positions_per_symbol",
        "mark_to_market_equity",
        "drawdown_pct_from_high_water", "k4_armed",
    )

    def _names(self, cls):
        return tuple(f.name for f in dataclasses.fields(cls))

    def test_trade_record_no_forbidden(self):
        names = self._names(TradeRecord)
        for fragment in self.FORBIDDEN_FRAGMENTS:
            for n in names:
                self.assertNotIn(fragment.lower(), n.lower(),
                    f"forbidden fragment '{fragment}' in TradeRecord field '{n}'")

    def test_trade_record_expected_present(self):
        names = set(self._names(TradeRecord))
        for n in self.EXPECTED_TRADE_FIELDS:
            self.assertIn(n, names, f"missing expected field {n} on TradeRecord")

    def test_no_pyramid_or_unit_index_fields(self):
        # Explicitly verify the no-pyramid-amplification structural lock.
        for cls in (TradeRecord, DailyEquityPoint, SimulationResult):
            names = self._names(cls)
            for n in names:
                self.assertNotIn("pyramid", n.lower())
                self.assertNotIn("unit_index", n.lower())

    def test_daily_point_no_forbidden(self):
        names = self._names(DailyEquityPoint)
        for fragment in self.FORBIDDEN_FRAGMENTS:
            for n in names:
                self.assertNotIn(fragment.lower(), n.lower())

    def test_daily_point_expected_present(self):
        names = set(self._names(DailyEquityPoint))
        for n in self.EXPECTED_DAILY_FIELDS:
            self.assertIn(n, names)

    def test_simulation_result_no_forbidden(self):
        names = self._names(SimulationResult)
        for fragment in self.FORBIDDEN_FRAGMENTS:
            for n in names:
                self.assertNotIn(fragment.lower(), n.lower())

    def test_simulation_result_has_attestations(self):
        names = set(self._names(SimulationResult))
        self.assertIn("oos_simulation_intentionally_omitted", names)
        self.assertIn("post_oos_simulation_intentionally_omitted", names)
        self.assertIn("in_sample_window", names)

    def test_long_only_direction(self):
        r = simulate(_DATA, _SIG, cost_tier=CostTier.S1)
        for rec in r.trade_records:
            self.assertEqual(rec.direction, "long")


class T11_Determinism(unittest.TestCase):
    def test_same_input_same_output(self):
        r1 = simulate(_DATA, _SIG, cost_tier=CostTier.S1)
        r2 = simulate(_DATA, _SIG, cost_tier=CostTier.S1)
        self.assertEqual(r1.num_closed_trades_total, r2.num_closed_trades_total)
        self.assertEqual(r1.final_cash_balance, r2.final_cash_balance)
        self.assertEqual(r1.max_drawdown_pct_observed,
                         r2.max_drawdown_pct_observed)
        self.assertEqual(r1.k4_fired, r2.k4_fired)
        self.assertEqual(r1.trade_records_per_symbol,
                         r2.trade_records_per_symbol)
        self.assertEqual(len(r1.daily_equity_ledger),
                         len(r2.daily_equity_ledger))
        # Spot check across trade records.
        for a, b in zip(r1.trade_records, r2.trade_records):
            self.assertEqual(a, b)


class T12_NoFileIoAtImport(unittest.TestCase):
    def test_no_io_at_import(self):
        SIM_PKG = ("external_research_hunter."
                   "s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_simulator")
        keys_to_drop = [k for k in list(sys.modules) if SIM_PKG in k]
        saved = {k: sys.modules[k] for k in keys_to_drop}
        for k in keys_to_drop:
            del sys.modules[k]
        captured_open = []
        captured_read = []
        real_open = builtins.open
        real_read = Path.read_bytes

        def _po(*a, **kw):
            if a:
                captured_open.append(a[0])
            return real_open(*a, **kw)

        def _pr(self):
            captured_read.append(str(self))
            return real_read(self)

        builtins.open = _po
        Path.read_bytes = _pr
        try:
            import importlib
            importlib.import_module(SIM_PKG)
        finally:
            builtins.open = real_open
            Path.read_bytes = real_read
            for k, v in saved.items():
                sys.modules[k] = v
        suspect_open = [
            p for p in captured_open
            if isinstance(p, (str, Path))
            and not str(p).endswith((".py", ".pyc"))
        ]
        suspect_read = [
            p for p in captured_read
            if not p.endswith((".py", ".pyc"))
        ]
        self.assertEqual(suspect_open, [],
            f"file IO at import: opens={suspect_open}")
        self.assertEqual(suspect_read, [],
            f"file IO at import: read_bytes={suspect_read}")


class T13_ForbiddenTokenGrep(unittest.TestCase):
    """Cross-check of the spec section 18 forbidden-token list against
    simulator.py source. The build orchestrator runs the same grep with
    inline FORBIDDEN_TOKEN_EXCLUSION handling; this test is a
    lightweight self-check."""

    # FORBIDDEN_TOKEN_EXCLUSION (the next 2 lines after this comment)
    # are excluded from the orchestrator's grep but the literal token
    # list is constructed here in Python source, which is fine: this
    # test file (test_simulator.py) is NOT subject to the V6 grep over
    # simulator.py. The orchestrator only greps simulator.py.

    TOKENS_THAT_MUST_NOT_APPEAR_IN_SIMULATOR = (
        "yfinance", "yahoo_finance", "databento", "DATABENTO_API_KEY",
        "Strategy Lab", "review_queue", "idea_memory",
        "live_trading", "brokerage",
        "alpaca", "ibapi", "ib_insync", "tradestation",
        "place_order", "submit_order", "cancel_order", "modify_order",
        "sharpe", "sortino", "calmar", "expectancy", "win_rate",
        "correlation", "covariance", "pearson",
        "effective_independent_bets",
        "Donchian", "wilder_atr",
        "daily_return", "log_return", ".pct_change(",
        "compute_return", "cumulative_return", "annualized_return",
        "entry_short_triggered", "exit_short_triggered",
        "short_position", "borrow_cost", "borrow_rate",
        "simulate_oos", "compute_oos", "oos_simulation",
        "post_oos_simulation", "simulate_full_window", "force_oos",
    )

    def setUp(self):
        path = (REPO_ROOT / "external_research_hunter"
                / "s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_simulator"
                / "simulator.py")
        self.lines = path.read_text(encoding="utf-8").splitlines()
        self.excluded = set()
        for i, line in enumerate(self.lines, start=1):
            if "FORBIDDEN_TOKEN_EXCLUSION" in line:
                self.excluded.add(i)
                self.excluded.add(i + 1)
                self.excluded.add(i + 2)

    def test_no_forbidden_tokens(self):
        for tok in self.TOKENS_THAT_MUST_NOT_APPEAR_IN_SIMULATOR:
            hits = []
            for i, line in enumerate(self.lines, start=1):
                if tok in line and i not in self.excluded:
                    hits.append((i, line.strip()[:160]))
            self.assertEqual(hits, [],
                f"forbidden token '{tok}' found in simulator.py: {hits}")


class T14_ForbiddenImportGrep(unittest.TestCase):
    FORBIDDEN_IMPORTS = (
        "import yfinance", "import databento", "import requests",
        "import urllib.", "from urllib", "import http.client",
        "import socket", "import curl_cffi", "import aiohttp",
        "import httpx", "import grpc", "import pyarrow.flight",
        "import strategy_lab", "import sparta_commander",
        "import spartacus", "import hydra_video", "import app",
        "import sparta_brain",
        "import broker", "import interactive_brokers", "import alpaca",
        "import tradestation", "import ibapi", "import binance",
        "import oanda", "import ib_insync",
        "import quantconnect", "import lean", "import qcalgorithm",
        "import pandas", "import numpy", "from pandas", "from numpy",
    )

    def test_no_forbidden_imports(self):
        path = (REPO_ROOT / "external_research_hunter"
                / "s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_simulator"
                / "simulator.py")
        text = path.read_text(encoding="utf-8")
        for f in self.FORBIDDEN_IMPORTS:
            for ln_no, line in enumerate(text.splitlines(), start=1):
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                self.assertNotIn(f, stripped,
                    f"forbidden import '{f}' at line {ln_no}: {stripped}")


class T15_PublicApiSurface(unittest.TestCase):
    EXPECTED = sorted([
        "CostTier",
        "DEFAULT_STARTING_CASH",
        "DailyEquityPoint",
        "ETF_DOLLAR_PER_SHARE",
        "ETF_TICK_SIZE",
        "ExitReason",
        "IN_SAMPLE_WINDOW",
        "K4_PORTFOLIO_MAXDD_PCT",
        "MAX_UNITS_PER_SYMBOL",
        "PER_SIGNAL_ALLOCATION_FRACTION",
        "RSI_EXIT_THRESHOLD",
        "RSI_LOOKBACK",
        "RSI_OVERSOLD_ENTRY_THRESHOLD",
        "SimulationResult",
        "SimulatorError",
        "SimulatorInputError",
        "SimulatorK4FiredError",
        "SimulatorOosBlockedError",
        "SimulatorParameterOverrideError",
        "TradeRecord",
        "simulate",
    ])

    def test_all_matches(self):
        import importlib
        mod = importlib.import_module(
            "external_research_hunter."
            "s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_simulator"
        )
        observed = sorted(getattr(mod, "__all__", ()))
        self.assertEqual(observed, self.EXPECTED)


class T16_NoSideEffectImportsOfForbiddenModules(unittest.TestCase):
    FORBIDDEN_PRESENCE = (
        "yfinance", "databento", "requests", "urllib3",
        "http.client", "socket",
        "alpaca", "ibapi", "ib_insync", "tradestation", "binance",
        "oanda", "quantconnect", "lean", "qcalgorithm",
        "pandas", "numpy",
    )

    def test_simulate_does_not_import_forbidden(self):
        before = set(sys.modules.keys())
        _ = simulate(_DATA, _SIG, cost_tier=CostTier.S1)
        after = set(sys.modules.keys())
        added = after - before
        for f in self.FORBIDDEN_PRESENCE:
            for k in added:
                self.assertNotIn(f, k,
                    f"forbidden module '{f}' imported as side effect via key '{k}'")


if __name__ == "__main__":
    unittest.main(verbosity=2)
