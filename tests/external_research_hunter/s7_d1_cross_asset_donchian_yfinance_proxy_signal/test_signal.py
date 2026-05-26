"""T1-T16 test suite for the s7 D1 cross-asset yfinance proxy signal module.

Run from repo root with stdlib unittest:
    python tests/external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_signal/test_signal.py

Plan anchor:
  docs/s7_d1_cross_asset_donchian_step_05_signal_computation_specification_plan.md
  sha256 6e039d352af7a7f20c99b1e26173f07539417a7f65b3c458458aa3ca1c8e2ff4
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
from external_research_hunter.s7_d1_cross_asset_donchian_yfinance_proxy_signal import (  # noqa: E402
    CrossSymbolSignalResult,
    ENTRY_CHANNEL_LOOKBACK,
    EXIT_CHANNEL_LOOKBACK,
    IN_SAMPLE_WINDOW,
    SignalError,
    SignalEvent,
    SignalInputError,
    SignalOosBlockedError,
    SignalParameterOverrideError,
    SignalResult,
    compute_signals,
    compute_signals_all,
)

SIGNAL_PKG = "external_research_hunter.s7_d1_cross_asset_donchian_yfinance_proxy_signal"
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


class T02_AllSignalDatesInInSampleWindow(unittest.TestCase):
    """T2: every SignalEvent.date is in IN_SAMPLE_WINDOW."""

    def test_each_symbol(self):
        for sym in ("SPY", "TLT", "GLD", "USO"):
            with self.subTest(symbol=sym):
                r = compute_signals(load_symbol(sym))
                self.assertGreater(len(r.signals), 0)
                for ev in r.signals:
                    self.assertGreaterEqual(ev.date, IN_SAMPLE_WINDOW[0])
                    self.assertLessEqual(ev.date, IN_SAMPLE_WINDOW[1])


class T03_AllBarIndexAtLeastEntryLookback(unittest.TestCase):
    """T3: every SignalEvent.bar_index >= ENTRY_CHANNEL_LOOKBACK."""

    def test_each_symbol(self):
        for sym in ("SPY", "TLT", "GLD", "USO"):
            with self.subTest(symbol=sym):
                r = compute_signals(load_symbol(sym))
                for ev in r.signals:
                    self.assertGreaterEqual(ev.bar_index, ENTRY_CHANNEL_LOOKBACK)


class T04_FirstEligibleMatchesValidatorPin(unittest.TestCase):
    """T4: first_signal_eligible_bar_index == 55 and first_signal_eligible_date == 2014-03-24."""

    def test_each_symbol(self):
        for sym in ("SPY", "TLT", "GLD", "USO"):
            with self.subTest(symbol=sym):
                r = compute_signals(load_symbol(sym))
                self.assertEqual(r.first_signal_eligible_bar_index, 55)
                self.assertEqual(r.first_signal_eligible_date, "2014-03-24")


class T05_TriggerArithmeticSpotCheck(unittest.TestCase):
    """T5: spot-check trigger flag arithmetic on actual data.

    For SPY, find a SignalEvent where today_high > entry_channel_high_55 and
    assert entry_long_triggered is True. Then find one where today_low <
    entry_channel_low_55 and assert entry_short_triggered is True. The test
    inspects values rather than running a full simulator."""

    def test_long_trigger(self):
        r = compute_signals(load_symbol("SPY"))
        long_hit = next(
            (ev for ev in r.signals if ev.today_high > ev.entry_channel_high_55),
            None,
        )
        self.assertIsNotNone(long_hit, "expected at least one bar with today_high > entry_high_55 in SPY 2014-2022")
        self.assertTrue(long_hit.entry_long_triggered)

    def test_short_trigger(self):
        r = compute_signals(load_symbol("SPY"))
        short_hit = next(
            (ev for ev in r.signals if ev.today_low < ev.entry_channel_low_55),
            None,
        )
        self.assertIsNotNone(short_hit, "expected at least one bar with today_low < entry_low_55 in SPY 2014-2022")
        self.assertTrue(short_hit.entry_short_triggered)

    def test_no_false_positive_long(self):
        """A bar with today_high <= entry_channel_high_55 must have
        entry_long_triggered == False."""
        r = compute_signals(load_symbol("SPY"))
        no_long = next(
            (ev for ev in r.signals if ev.today_high <= ev.entry_channel_high_55),
            None,
        )
        self.assertIsNotNone(no_long)
        self.assertFalse(no_long.entry_long_triggered)


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
    """T8: compute_signals_all returns CrossSymbolSignalResult with the 4 expected keys;
    cross-symbol consistency holds for the real ETF-proxy data."""

    def test_real_data(self):
        data = load_all()
        r = compute_signals_all(data)
        self.assertIsInstance(r, CrossSymbolSignalResult)
        self.assertEqual(set(r.per_symbol.keys()), {"SPY", "TLT", "GLD", "USO"})
        self.assertTrue(r.cross_symbol_bars_in_window_equal)
        self.assertTrue(r.cross_symbol_first_eligible_date_equal)
        self.assertTrue(r.cross_symbol_last_eligible_date_equal)
        # All per-symbol windows match IN_SAMPLE_WINDOW
        for sr in r.per_symbol.values():
            self.assertEqual(sr.window, IN_SAMPLE_WINDOW)


class T09_OosAttestationAndNoOosDates(unittest.TestCase):
    """T9: oos_signal_intentionally_omitted is True; no SignalEvent.date is in
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
                        f"{sym} signal date {ev.date} found in OUT_OF_SAMPLE_WINDOW",
                    )
                    self.assertFalse(
                        POST_OOS_DIAGNOSTIC_WINDOW[0] <= ev.date <= POST_OOS_DIAGNOSTIC_WINDOW[1],
                        f"{sym} signal date {ev.date} found in POST_OOS_DIAGNOSTIC_WINDOW",
                    )


class T10_DataclassesHaveNoForbiddenSimulatorFields(unittest.TestCase):
    """T10: SignalEvent / SignalResult / CrossSymbolSignalResult have no field
    suggestive of simulator / backtest / sizing logic."""

    FORBIDDEN_FIELD_SUBSTRINGS = (
        "pnl", "profit", "_return", "sharpe", "sortino", "calmar",
        "drawdown", "correl", "covar", "position_size", "wilder",
        "atr", "stop", "slippage", "commission", "fill", "order_id",
        "trade_id", "unit_count", "pyramid",
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
    """T12: importing the signal module triggers no open() / Path.read_bytes."""

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
        self.assertEqual(suspect_open, [], f"unexpected open(): {suspect_open}")
        self.assertEqual(suspect_read_bytes, [],
                         f"unexpected read_bytes(): {suspect_read_bytes}")


class T13_NoForbiddenTokensInSignalSource(unittest.TestCase):
    """T13: static grep of signal.py for the Step 05 plan section 19 forbidden
    token list returns zero hits outside FORBIDDEN_TOKEN_EXCLUSION lines."""

    def test_grep(self):
        src = (REPO_ROOT
               / "external_research_hunter"
               / "s7_d1_cross_asset_donchian_yfinance_proxy_signal"
               / "signal.py")
        text = src.read_text(encoding="utf-8")
        forbidden = [
            # Vendor / credential / network
            "DATABENTO_API_KEY", "yfinance", "yahoo_finance", "databento",
            "requests.get", "urllib.request", "socket.connect", "http.client",
            "curl_cffi", "aiohttp",
            # Simulator / backtest / portfolio / trading-side
            "backtest", "portfolio", "pnl", "profit", "sharpe", "sortino",
            "calmar", "drawdown", "correlation", "covariance", "brokerage",
            "Strategy Lab", "review_queue", "live trading", "live_trading",
            # Return-computation tokens (specific, not Python keyword)
            "daily_return", "log_return", "pct_return", ".pct_change(",
            "compute_return", "cumulative_return", "annualized_return",
            "return_series", "_returns_", "_returns,", "returns_total",
            "arithmetic_return", "geometric_return",
            # Future-phase computation tokens
            "Wilder", "ATR(", ".rolling(", "wilder_atr", "wilder_n",
            "position_size", "position_state", "unit_count", "pyramid_unit",
            "stop_distance", "stop_price", "slippage", "commission",
            "fill_price", "order_id", "trade_id",
        ]
        violations = []
        for tok in forbidden:
            for i, line in enumerate(text.splitlines(), start=1):
                if tok in line:
                    stripped = line.strip()
                    if stripped.startswith("#") and "FORBIDDEN_TOKEN_EXCLUSION" in line:
                        continue
                    violations.append((tok, i, line.rstrip()))
        self.assertEqual(violations, [],
                         f"forbidden tokens found in signal.py: {violations}")


class T14_NoForbiddenImportsInSignalSource(unittest.TestCase):
    """T14: static grep of signal.py for forbidden imports returns zero hits."""

    def test_grep(self):
        src = (REPO_ROOT
               / "external_research_hunter"
               / "s7_d1_cross_asset_donchian_yfinance_proxy_signal"
               / "signal.py")
        text = src.read_text(encoding="utf-8")
        forbidden_imports = [
            "import yfinance", "import databento", "import requests",
            "import urllib.", "from urllib", "import http.client",
            "import socket", "import curl_cffi", "import aiohttp",
            "import httpx", "import grpc", "import pyarrow.flight",
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
    """T15: public API surface equals exactly the section 7 list."""

    EXPECTED = sorted([
        "CrossSymbolSignalResult", "ENTRY_CHANNEL_LOOKBACK",
        "EXIT_CHANNEL_LOOKBACK", "IN_SAMPLE_WINDOW",
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
