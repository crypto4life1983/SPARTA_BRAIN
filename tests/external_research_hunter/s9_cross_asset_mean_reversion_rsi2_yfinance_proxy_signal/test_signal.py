"""T1-T16 test suite for the s9 cross-asset RSI-2 mean-reversion signal module.

Run from repo root:
    python tests/external_research_hunter/s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_signal/test_signal.py

Plan anchor:
  docs/s9_cross_asset_mean_reversion_rsi2_signal_module_specification_plan.md
  sha256 59e5f401232f19342777445a0d992d1df23dda95a71419379e1daded89e9a0c9
"""
from __future__ import annotations

import builtins
import dataclasses
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
from external_research_hunter.s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_signal import (  # noqa: E402
    CrossSymbolSignalResult,
    IN_SAMPLE_WINDOW,
    RSI_EXIT_THRESHOLD,
    RSI_LOOKBACK,
    RSI_OVERSOLD_ENTRY_THRESHOLD,
    SignalError,
    SignalEvent,
    SignalInputError,
    SignalOosBlockedError,
    SignalParameterOverrideError,
    SignalResult,
    compute_signals,
    compute_signals_all,
)

SIGNAL_PKG = "external_research_hunter.s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_signal"
OUT_OF_SAMPLE_WINDOW = ("2023-01-01", "2025-12-30")
POST_OOS_DIAGNOSTIC_WINDOW = ("2026-01-02", "2026-05-22")


class T01_ComputeSignalsReturnsResult(unittest.TestCase):
    """T1: compute_signals returns SignalResult for each symbol with bars_in_window > 0."""

    def test_each_symbol(self):
        for sym in ("SPY", "TLT", "GLD", "USO"):
            with self.subTest(symbol=sym):
                ls = load_symbol(sym)
                r = compute_signals(ls)
                self.assertIsInstance(r, SignalResult)
                self.assertGreater(r.bars_in_window, 0)
                self.assertGreater(len(r.signals), 0)


class T02_AllSignalDatesInInSampleWindow(unittest.TestCase):
    """T2: every SignalEvent.date is in IN_SAMPLE_WINDOW."""

    def test_each_symbol(self):
        for sym in ("SPY", "TLT", "GLD", "USO"):
            with self.subTest(symbol=sym):
                r = compute_signals(load_symbol(sym))
                for ev in r.signals:
                    self.assertGreaterEqual(ev.date, IN_SAMPLE_WINDOW[0])
                    self.assertLessEqual(ev.date, IN_SAMPLE_WINDOW[1])


class T03_AllBarIndexAtLeastRsiLookback(unittest.TestCase):
    """T3: every SignalEvent.bar_index >= RSI_LOOKBACK (= 2)."""

    def test_each_symbol(self):
        for sym in ("SPY", "TLT", "GLD", "USO"):
            with self.subTest(symbol=sym):
                r = compute_signals(load_symbol(sym))
                for ev in r.signals:
                    self.assertGreaterEqual(ev.bar_index, RSI_LOOKBACK)


class T04_FirstEligibleMatchesSpec(unittest.TestCase):
    """T4: first_signal_eligible_bar_index == 2 AND first_signal_eligible_date == 2014-01-06."""

    def test_each_symbol(self):
        for sym in ("SPY", "TLT", "GLD", "USO"):
            with self.subTest(symbol=sym):
                r = compute_signals(load_symbol(sym))
                self.assertEqual(r.first_signal_eligible_bar_index, 2)
                self.assertEqual(r.first_signal_eligible_date, "2014-01-06")


class T05_RsiArithmeticSpotCheck(unittest.TestCase):
    """T5: spot-check that the entry/exit flags match the RSI arithmetic.

    For SPY: find a SignalEvent where rsi < 10 -> assert entry_long_triggered True;
    find one where rsi > 50 -> assert exit_long_triggered True; find one between
    thresholds -> assert both flags False."""

    def test_entry_flag(self):
        r = compute_signals(load_symbol("SPY"))
        hit = next((ev for ev in r.signals if ev.rsi_value < RSI_OVERSOLD_ENTRY_THRESHOLD), None)
        self.assertIsNotNone(hit, "expected at least one bar with RSI < 10 on SPY 2014-2022")
        self.assertTrue(hit.entry_long_triggered)
        self.assertFalse(hit.exit_long_triggered)

    def test_exit_flag(self):
        r = compute_signals(load_symbol("SPY"))
        hit = next((ev for ev in r.signals if ev.rsi_value > RSI_EXIT_THRESHOLD), None)
        self.assertIsNotNone(hit, "expected at least one bar with RSI > 50 on SPY 2014-2022")
        self.assertFalse(hit.entry_long_triggered)
        self.assertTrue(hit.exit_long_triggered)

    def test_between_thresholds_no_flag(self):
        r = compute_signals(load_symbol("SPY"))
        between = next(
            (ev for ev in r.signals
             if RSI_OVERSOLD_ENTRY_THRESHOLD <= ev.rsi_value <= RSI_EXIT_THRESHOLD),
            None,
        )
        self.assertIsNotNone(between)
        self.assertFalse(between.entry_long_triggered)
        self.assertFalse(between.exit_long_triggered)


class T06_RaisesOnNonLoadedSymbolInput(unittest.TestCase):
    """T6: SignalInputError on non-LoadedSymbol input."""

    def test_none(self):
        with self.assertRaises(SignalInputError):
            compute_signals(None)

    def test_dict(self):
        with self.assertRaises(SignalInputError):
            compute_signals({"symbol": "SPY"})

    def test_string(self):
        with self.assertRaises(SignalInputError):
            compute_signals("SPY")


class T07_RaisesOnNonMappingAllInput(unittest.TestCase):
    """T7: SignalInputError on non-Mapping input to compute_signals_all."""

    def test_list(self):
        with self.assertRaises(SignalInputError):
            compute_signals_all([load_symbol("SPY")])

    def test_string(self):
        with self.assertRaises(SignalInputError):
            compute_signals_all("not a mapping")

    def test_wrong_keys(self):
        with self.assertRaises(SignalInputError):
            compute_signals_all({"AAPL": load_symbol("SPY")})


class T08_ComputeSignalsAllReturnsCrossResult(unittest.TestCase):
    """T8: compute_signals_all returns CrossSymbolSignalResult with 4 keys;
    cross-symbol consistency holds for the real ETF-proxy data."""

    def test_real_data(self):
        data = load_all()
        r = compute_signals_all(data)
        self.assertIsInstance(r, CrossSymbolSignalResult)
        self.assertEqual(set(r.per_symbol.keys()), {"SPY", "TLT", "GLD", "USO"})
        self.assertTrue(r.cross_symbol_bars_in_window_equal)
        self.assertTrue(r.cross_symbol_first_eligible_date_equal)
        self.assertTrue(r.cross_symbol_last_eligible_date_equal)


class T09_OosAttestationAndNoOosDates(unittest.TestCase):
    """T9: oos_signal_intentionally_omitted is True AND no SignalEvent date in
    OUT_OF_SAMPLE_WINDOW or POST_OOS_DIAGNOSTIC_WINDOW."""

    def test_attestation_and_no_oos_dates(self):
        data = load_all()
        r = compute_signals_all(data)
        self.assertTrue(r.oos_signal_intentionally_omitted)
        self.assertTrue(r.post_oos_signal_intentionally_omitted)
        for sym, sr in r.per_symbol.items():
            with self.subTest(symbol=sym):
                self.assertTrue(sr.oos_signal_intentionally_omitted)
                self.assertTrue(sr.post_oos_signal_intentionally_omitted)
                for ev in sr.signals:
                    self.assertFalse(
                        OUT_OF_SAMPLE_WINDOW[0] <= ev.date <= OUT_OF_SAMPLE_WINDOW[1],
                        f"{sym} signal date {ev.date} in OUT_OF_SAMPLE_WINDOW",
                    )
                    self.assertFalse(
                        POST_OOS_DIAGNOSTIC_WINDOW[0] <= ev.date <= POST_OOS_DIAGNOSTIC_WINDOW[1],
                        f"{sym} signal date {ev.date} in POST_OOS_DIAGNOSTIC_WINDOW",
                    )


class T10_DataclassesHaveNoForbiddenFields(unittest.TestCase):
    """T10: SignalEvent / SignalResult / CrossSymbolSignalResult have no
    field suggestive of downstream computation OR short side. Long-only
    enforcement at type level."""

    FORBIDDEN_FIELD_SUBSTRINGS = (
        "pnl", "profit", "_return", "sharpe", "sortino", "calmar",
        "drawdown", "correl", "covar", "position_size", "wilder_atr",
        "stop", "slippage", "commission", "fill", "order_id",
        "trade_id", "pyramid",
        # Long-only enforcement: no short-side fields
        "short", "borrow",
    )

    def _assert_no_forbidden(self, cls):
        field_names = [f.name for f in fields(cls)]
        for name in field_names:
            low = name.lower()
            for sub in self.FORBIDDEN_FIELD_SUBSTRINGS:
                self.assertNotIn(
                    sub, low,
                    f"{cls.__name__} field {name!r} matches forbidden substring {sub!r}",
                )

    def test_signal_event(self):
        self._assert_no_forbidden(SignalEvent)

    def test_signal_result(self):
        self._assert_no_forbidden(SignalResult)

    def test_cross_symbol_signal_result(self):
        self._assert_no_forbidden(CrossSymbolSignalResult)


class T11_Determinism(unittest.TestCase):
    """T11: compute_signals(load_symbol('SPY')) produces field-equal results twice."""

    def test_determinism_single(self):
        a = compute_signals(load_symbol("SPY"))
        b = compute_signals(load_symbol("SPY"))
        self.assertEqual(a.symbol, b.symbol)
        self.assertEqual(a.csv_sha256_observed, b.csv_sha256_observed)
        self.assertEqual(a.window, b.window)
        self.assertEqual(a.bars_in_window, b.bars_in_window)
        self.assertEqual(a.first_signal_eligible_bar_index, b.first_signal_eligible_bar_index)
        self.assertEqual(a.first_signal_eligible_date, b.first_signal_eligible_date)
        self.assertEqual(a.last_signal_eligible_bar_index, b.last_signal_eligible_bar_index)
        self.assertEqual(a.last_signal_eligible_date, b.last_signal_eligible_date)
        self.assertEqual(len(a.signals), len(b.signals))
        for ev_a, ev_b in zip(a.signals, b.signals):
            self.assertEqual(ev_a, ev_b)


class T12_ImportPerformsNoFileIO(unittest.TestCase):
    """T12: importing the signal package triggers no open() / Path.read_bytes."""

    def test_no_io_at_import(self):
        keys_to_drop = [k for k in list(sys.modules) if SIGNAL_PKG in k]
        saved = {k: sys.modules[k] for k in keys_to_drop}
        for k in keys_to_drop:
            del sys.modules[k]

        captured_open = []
        captured_read_bytes = []
        real_open = builtins.open
        real_read_bytes = Path.read_bytes

        def patched_open(*a, **kw):
            captured_open.append(a[0] if a else None)
            return real_open(*a, **kw)

        def patched_read_bytes(self):
            captured_read_bytes.append(str(self))
            return real_read_bytes(self)

        builtins.open = patched_open
        Path.read_bytes = patched_read_bytes
        try:
            import importlib
            importlib.import_module(SIGNAL_PKG)
        finally:
            builtins.open = real_open
            Path.read_bytes = real_read_bytes
            for k, v in saved.items():
                sys.modules[k] = v

        suspect_open = [
            p for p in captured_open
            if isinstance(p, (str, Path)) and not str(p).endswith((".py", ".pyc"))
        ]
        suspect_read_bytes = [
            p for p in captured_read_bytes
            if not p.endswith((".py", ".pyc"))
        ]
        self.assertEqual(suspect_open, [],
                         f"unexpected open(): {suspect_open}")
        self.assertEqual(suspect_read_bytes, [],
                         f"unexpected read_bytes(): {suspect_read_bytes}")


class T13_NoForbiddenTokensInSignalSource(unittest.TestCase):
    """T13: static grep of signal.py for forbidden tokens per spec section 20.
    Zero hits outside FORBIDDEN_TOKEN_EXCLUSION lines."""

    def test_grep(self):
        src = (REPO_ROOT
               / "external_research_hunter"
               / "s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_signal"
               / "signal.py")
        text = src.read_text(encoding="utf-8")
        forbidden = [
            # Vendor / credential / network
            "DATABENTO_API_KEY", "yfinance", "yahoo_finance", "databento",
            "requests.get", "urllib.request", "socket.connect", "http.client",
            "curl_cffi", "aiohttp", "httpx",
            # Live trading / brokerage / production
            "Strategy Lab", "strategy_lab", "review_queue", "idea_memory",
            "live trading", "live_trading",
            "brokerage", "broker_api", "broker_session",
            "alpaca", "interactive_brokers", "ibkr", "ibapi", "ib_insync",
            "tradestation", "binance", "oanda",
            "order_send", "place_order", "submit_order", "cancel_order",
            "modify_order", "route_order",
            "production_signal",
            "paper_broker", "paper_trade",
            "scheduler", "autopilot", "frc_gate",
            # Downstream computation (deferred to simulator/aggregator)
            "sharpe", "sortino", "calmar", "drawdown",
            "expectancy", "win_rate",
            "correlation", "covariance", "pearson",
            "effective_independent_bets", "avg_pairwise_correlation",
            "avg_pairwise_dependence_measure",
            "pnl", "profit",
            "portfolio_equity", "cash_balance", "mark_to_market",
            "position_size", "position_state", "pyramid_unit",
            "stop_distance", "stop_price", "slippage", "commission",
            "fill_price", "order_id", "trade_id",
            "gross_pnl", "net_pnl",
            # Return tokens (specific; avoid Python keyword false-match)
            "daily_return", "log_return", "pct_return", ".pct_change(",
            "compute_return", "cumulative_return", "annualized_return",
            "return_series", "_returns_", "_returns,", "returns_total",
            "arithmetic_return", "geometric_return",
            # Parent spec context
            "Donchian", "ATR(", "wilder_atr", "wilder_n", ".rolling(",
            # Optimization
            "_optimize_", "_sweep_", "_tune_", "_grid_search_",
            "_bayes_search_",
            "alternative_lookback", "alternative_threshold",
            "lookback_grid", "threshold_grid", "parameter_grid",
            "winner_selection", "asset_selection", "top_n_pick",
            # Filter / regime
            "regime_filter", "regime_gate", "ma_filter", "vol_filter",
            "dependence_filter", "correlation_filter", "trend_filter",
            "volume_filter",
            # Short-side (long-only enforcement)
            "entry_short_triggered", "exit_short_triggered",
            "short_position", "borrow_cost", "borrow_rate",
            "short_entry", "short_exit",
            # OOS-related
            "compute_signals_oos", "simulate_oos", "oos_simulation",
            "post_oos_simulation",
        ]
        # Build exclusion line numbers (inline FORBIDDEN_TOKEN_EXCLUSION
        # markers; line + next 2 lines per Step 07 convention).
        exclusion_line_nos = set()
        lines = text.splitlines()
        for i, line in enumerate(lines, start=1):
            if "FORBIDDEN_TOKEN_EXCLUSION" in line:
                exclusion_line_nos.add(i)
                exclusion_line_nos.add(i + 1)
                exclusion_line_nos.add(i + 2)
        violations = []
        for tok in forbidden:
            for ln_no, line in enumerate(lines, start=1):
                if tok in line:
                    if ln_no in exclusion_line_nos:
                        continue
                    violations.append((tok, ln_no, line.rstrip()))
        self.assertEqual(violations, [],
                         f"forbidden tokens found in signal.py: {violations}")


class T14_NoForbiddenImportsInSignalSource(unittest.TestCase):
    """T14: static grep for forbidden imports returns zero hits."""

    def test_grep(self):
        src = (REPO_ROOT
               / "external_research_hunter"
               / "s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_signal"
               / "signal.py")
        text = src.read_text(encoding="utf-8")
        forbidden_imports = [
            "import yfinance", "import databento", "import requests",
            "import urllib.", "from urllib", "import http.client",
            "import socket", "import curl_cffi", "import aiohttp",
            "import httpx", "import grpc", "import pyarrow.flight",
            "import strategy_lab", "import sparta_commander",
            "import broker", "import interactive_brokers", "import alpaca",
            "import ibapi", "import quantconnect", "import lean",
        ]
        hits = []
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            for f in forbidden_imports:
                if f in stripped:
                    hits.append((f, stripped[:160]))
        self.assertEqual(hits, [], f"forbidden imports in signal.py: {hits}")


class T15_PublicApiSurfaceExact(unittest.TestCase):
    """T15: public API surface equals exactly the spec section 7 list."""

    EXPECTED = sorted([
        "CrossSymbolSignalResult", "IN_SAMPLE_WINDOW",
        "RSI_EXIT_THRESHOLD", "RSI_LOOKBACK",
        "RSI_OVERSOLD_ENTRY_THRESHOLD",
        "SignalError", "SignalEvent", "SignalInputError",
        "SignalOosBlockedError", "SignalParameterOverrideError",
        "SignalResult", "compute_signals", "compute_signals_all",
    ])

    def test_all_exact(self):
        import importlib
        mod = importlib.import_module(SIGNAL_PKG)
        observed = set(getattr(mod, "__all__", ()))
        self.assertEqual(observed, set(self.EXPECTED))


class T16_NoSideEffectVendorImport(unittest.TestCase):
    """T16: calling compute_signals does not import any forbidden vendor /
    network package as a side effect."""

    def test_no_new_forbidden_module(self):
        before = set(sys.modules.keys())
        compute_signals(load_symbol("SPY"))
        after = set(sys.modules.keys())
        new = after - before
        forbidden_substrings = (
            "yfinance", "databento", "requests", "urllib3",
            "curl_cffi", "aiohttp", "httpx", "grpc",
        )
        bad = [m for m in new if any(s in m for s in forbidden_substrings)]
        self.assertEqual(bad, [], f"forbidden modules imported as side effect: {bad}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
