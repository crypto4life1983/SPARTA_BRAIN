"""T1-T16 test suite for the s7 D1 cross-asset yfinance proxy input validator.

Run from repo root with stdlib unittest:
    python tests/external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_validator/test_validator.py

Plan anchor:
  docs/s7_d1_cross_asset_donchian_step_04_input_validator_specification_plan.md
  sha256 c1aad410b50e132540f66ee7c973048967b4f36a3cb0872bb5d55f25683466da
"""
from __future__ import annotations

import builtins
import dataclasses
import os
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
os.chdir(REPO_ROOT)

from external_research_hunter.s7_d1_cross_asset_donchian_yfinance_proxy_loader import (  # noqa: E402
    load_all,
    load_symbol,
)
from external_research_hunter.s7_d1_cross_asset_donchian_yfinance_proxy_validator import (  # noqa: E402
    CrossSymbolValidationReport,
    DONCHIAN_ENTRY_LOOKBACK,
    DONCHIAN_EXIT_LOOKBACK,
    IN_SAMPLE_WINDOW,
    OUT_OF_SAMPLE_WINDOW,
    POST_OOS_DIAGNOSTIC_WINDOW,
    ValidationReport,
    ValidatorCrossSymbolAlignmentError,
    ValidatorError,
    ValidatorInputError,
    WarmupInsufficientError,
    WindowMisfitError,
    validate_all,
    validate_loaded_symbol,
)

VALIDATOR_PKG = "external_research_hunter.s7_d1_cross_asset_donchian_yfinance_proxy_validator"


class T01_ValidateLoadedSymbolReturnsReport(unittest.TestCase):
    """T1: per symbol, returns ValidationReport with bar_count_total == 3116."""

    def test_each_symbol(self):
        for sym in ("SPY", "TLT", "GLD", "USO"):
            with self.subTest(symbol=sym):
                ls = load_symbol(sym)
                r = validate_loaded_symbol(ls)
                self.assertIsInstance(r, ValidationReport)
                self.assertEqual(r.bar_count_total, 3116)


class T02_InSampleBarCountConsistentAcrossSymbols(unittest.TestCase):
    """T2: bar_count_in_in_sample_window is consistent across symbols."""

    def test_consistent(self):
        counts = []
        for sym in ("SPY", "TLT", "GLD", "USO"):
            r = validate_loaded_symbol(load_symbol(sym))
            counts.append(r.bar_count_in_in_sample_window)
        self.assertEqual(len(set(counts)), 1, f"in-sample counts vary: {counts}")


class T03_OosBarCountConsistentAcrossSymbols(unittest.TestCase):
    """T3: bar_count_in_oos_window is consistent across symbols."""

    def test_consistent(self):
        counts = []
        for sym in ("SPY", "TLT", "GLD", "USO"):
            r = validate_loaded_symbol(load_symbol(sym))
            counts.append(r.bar_count_in_oos_window)
        self.assertEqual(len(set(counts)), 1, f"oos counts vary: {counts}")


class T04_WarmupAtLeast55(unittest.TestCase):
    """T4: warmup_bars_available_before_first_in_sample_signal_eligible_bar >= 55."""

    def test_warmup_adequate(self):
        for sym in ("SPY", "TLT", "GLD", "USO"):
            with self.subTest(symbol=sym):
                r = validate_loaded_symbol(load_symbol(sym))
                self.assertGreaterEqual(
                    r.warmup_bars_available_before_first_in_sample_signal_eligible_bar,
                    DONCHIAN_ENTRY_LOOKBACK,
                )


class T05_WarmupTruncationFlagTrueForEtfProxy(unittest.TestCase):
    """T5: this dataset starts 2014-01-02, in-sample window starts 2013-01-01;
    warmup_truncation_at_data_start must be True."""

    def test_flag_true(self):
        r = validate_loaded_symbol(load_symbol("SPY"))
        self.assertTrue(r.warmup_truncation_at_data_start)
        # And the verdict is PASS_WITH_WARMUP_TRUNCATION
        self.assertEqual(r.verdict, "PASS_WITH_WARMUP_TRUNCATION")


class T06_InSampleSummaryPresent(unittest.TestCase):
    """T6: in_sample_*_summary dicts have the expected keys."""

    def test_keys(self):
        r = validate_loaded_symbol(load_symbol("SPY"))
        self.assertIn("min", r.in_sample_close_summary)
        self.assertIn("max", r.in_sample_close_summary)
        self.assertIn("min", r.in_sample_adj_close_summary)
        self.assertIn("max", r.in_sample_adj_close_summary)
        self.assertIn("min", r.in_sample_volume_summary)
        self.assertIn("median", r.in_sample_volume_summary)
        self.assertIn("max", r.in_sample_volume_summary)
        self.assertIn("zero_volume_day_count", r.in_sample_volume_summary)


class T07_OosSummaryIntentionallyOmittedTrue(unittest.TestCase):
    """T7: oos_summary_intentionally_omitted is True; no oos_close_min-style
    field exists on the ValidationReport."""

    def test_attestation_and_no_oos_field(self):
        r = validate_loaded_symbol(load_symbol("SPY"))
        self.assertTrue(r.oos_summary_intentionally_omitted)
        self.assertTrue(r.post_oos_summary_intentionally_omitted)
        # Confirm no OOS numerical summary fields slipped onto the dataclass
        for forbidden in (
            "oos_close_min", "oos_close_max", "oos_close_median",
            "oos_volume_min", "oos_volume_max",
            "oos_adj_close_min", "oos_adj_close_max",
            "post_oos_close_min", "post_oos_close_max",
        ):
            self.assertFalse(hasattr(r, forbidden),
                             f"forbidden OOS field {forbidden} present")


class T08_RaisesOnNonLoadedSymbolInput(unittest.TestCase):
    """T8: passing None or a plain dict raises ValidatorInputError."""

    def test_none(self):
        with self.assertRaises(ValidatorInputError):
            validate_loaded_symbol(None)

    def test_dict(self):
        with self.assertRaises(ValidatorInputError):
            validate_loaded_symbol({"symbol": "SPY"})

    def test_dict_for_all(self):
        with self.assertRaises(ValidatorInputError):
            validate_all("not a mapping")


class T09_RaisesOnBarCountMismatch(unittest.TestCase):
    """T9: LoadedSymbol with 3115 dates raises ValidatorInputError (W1)."""

    def test_truncated(self):
        ls = load_symbol("SPY")
        # dataclasses.replace to create a structural twin with 3115 entries
        tampered = dataclasses.replace(
            ls,
            dates=ls.dates[:-1],
            open=ls.open[:-1],
            high=ls.high[:-1],
            low=ls.low[:-1],
            close=ls.close[:-1],
            adj_close=ls.adj_close[:-1],
            volume=ls.volume[:-1],
        )
        with self.assertRaises((ValidatorInputError, WindowMisfitError)):
            validate_loaded_symbol(tampered)


class T10_VerdictInAllowedSet(unittest.TestCase):
    """T10: verdict is one of {PASS, PASS_WITH_WARMUP_TRUNCATION, FAIL}."""

    def test_each_symbol(self):
        allowed = {"PASS", "PASS_WITH_WARMUP_TRUNCATION", "FAIL"}
        for sym in ("SPY", "TLT", "GLD", "USO"):
            with self.subTest(symbol=sym):
                r = validate_loaded_symbol(load_symbol(sym))
                self.assertIn(r.verdict, allowed)


class T11_ValidateAllReturnsCrossReport(unittest.TestCase):
    """T11: load_all then validate_all returns CrossSymbolValidationReport with 4 entries."""

    def test_returns(self):
        data = load_all()
        report = validate_all(data)
        self.assertIsInstance(report, CrossSymbolValidationReport)
        self.assertEqual(set(report.per_symbol.keys()), {"SPY", "TLT", "GLD", "USO"})
        for r in report.per_symbol.values():
            self.assertIsInstance(r, ValidationReport)


class T12_ValidateAllCrossAlignedTrue(unittest.TestCase):
    """T12: cross_symbol_dates_aligned True for real data."""

    def test_aligned(self):
        data = load_all()
        report = validate_all(data)
        self.assertTrue(report.cross_symbol_dates_aligned)
        self.assertTrue(report.cross_symbol_bar_count_equal)
        self.assertTrue(report.cross_symbol_in_sample_bar_count_equal)
        self.assertTrue(report.cross_symbol_oos_bar_count_equal)


class T13_ValidateAllRaisesOnSyntheticMisalignment(unittest.TestCase):
    """T13: perturb one symbol's dates; expect ValidatorCrossSymbolAlignmentError."""

    def test_misalignment(self):
        data = dict(load_all())
        uso = data["USO"]
        new_dates = tuple(["1999-12-31"] + list(uso.dates[1:]))
        data["USO"] = dataclasses.replace(uso, dates=new_dates)
        with self.assertRaises(ValidatorError):
            validate_all(data)


class T14_PortfolioVerdictConsistent(unittest.TestCase):
    """T14: portfolio_verdict is FAIL iff any per-symbol verdict is FAIL OR any A-check fails.
    Real data should produce PASS_WITH_WARMUP_TRUNCATION (all four per-symbol verdicts equal)."""

    def test_real_data_pass_with_warmup_truncation(self):
        data = load_all()
        report = validate_all(data)
        self.assertEqual(report.portfolio_verdict, "PASS_WITH_WARMUP_TRUNCATION")
        for r in report.per_symbol.values():
            self.assertEqual(r.verdict, "PASS_WITH_WARMUP_TRUNCATION")


class T15_ImportPerformsNoFileIO(unittest.TestCase):
    """T15: importing the validator package triggers no open()/Path.read_bytes."""

    def test_no_io_at_import(self):
        keys_to_drop = [k for k in list(sys.modules) if VALIDATOR_PKG in k]
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
            importlib.import_module(VALIDATOR_PKG)
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


class T16_NoForbiddenTokensInValidatorSource(unittest.TestCase):
    """T16: static grep of validator.py source for the expanded forbidden-token
    list (Step 04 spec section V6). Zero hits outside comment-exclusion lines."""

    def test_grep(self):
        validator_src_path = (REPO_ROOT
                              / "external_research_hunter"
                              / "s7_d1_cross_asset_donchian_yfinance_proxy_validator"
                              / "validator.py")
        text = validator_src_path.read_text(encoding="utf-8")
        forbidden = [
            "DATABENTO_API_KEY",
            "yfinance",
            "yahoo_finance",
            "requests.get",
            "urllib.request",
            "socket.connect",
            "Donchian",
            "Wilder",
            "ATR(",
            "rolling(",
            "correlation",
            "covariance",
            ".pct_change(",
            "log_return",
            "ema(",
            "sma(",
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
                         f"forbidden tokens found in validator.py: {violations}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
