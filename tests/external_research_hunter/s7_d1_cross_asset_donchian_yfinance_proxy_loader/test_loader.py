"""T1-T16 test suite for the s7 D1 cross-asset yfinance proxy loader.

Run from repo root with stdlib unittest:
    python -m unittest tests.external_research_hunter.s7_d1_cross_asset_donchian_yfinance_proxy_loader.test_loader

Plan anchor: docs/s7_d1_cross_asset_donchian_step_03_canonical_loader_specification_plan.md
"""
from __future__ import annotations

import builtins
import hashlib
import json
import os
import sys
import unittest
from pathlib import Path
from unittest import mock

# Ensure repo root is importable
REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Ensure cwd is repo root so the loader's RAW_DIR (relative) resolves
os.chdir(REPO_ROOT)

from external_research_hunter.s7_d1_cross_asset_donchian_yfinance_proxy_loader import (  # noqa: E402
    AUDIT_MANIFEST_PATH,
    EXPECTED_FIRST_DATE,
    EXPECTED_LAST_DATE,
    EXPECTED_ROWS,
    LOCKED_COLS,
    LoadedSymbol,
    LoaderCrossSymbolAlignmentError,
    LoaderError,
    LoaderManifestMissingError,
    LoaderShaMismatchError,
    LoaderShapeMismatchError,
    RAW_DIR,
    SYMBOLS,
    load_all,
    load_symbol,
)

LOADER_PKG = "external_research_hunter.s7_d1_cross_asset_donchian_yfinance_proxy_loader"


class T01_LoadSymbolReturnsExpectedRows(unittest.TestCase):
    """T1: load_symbol returns LoadedSymbol with EXPECTED_ROWS rows for each symbol."""

    def test_each_symbol(self):
        for sym in sorted(SYMBOLS):
            with self.subTest(symbol=sym):
                ls = load_symbol(sym)
                self.assertIsInstance(ls, LoadedSymbol)
                self.assertEqual(len(ls.dates), EXPECTED_ROWS)
                self.assertEqual(len(ls.open), EXPECTED_ROWS)
                self.assertEqual(len(ls.high), EXPECTED_ROWS)
                self.assertEqual(len(ls.low), EXPECTED_ROWS)
                self.assertEqual(len(ls.close), EXPECTED_ROWS)
                self.assertEqual(len(ls.adj_close), EXPECTED_ROWS)
                self.assertEqual(len(ls.volume), EXPECTED_ROWS)


class T02_DatesAreIsoStringsStrictlyIncreasing(unittest.TestCase):
    """T2: dates are 10-char YYYY-MM-DD strings, strictly monotonic."""

    def test_for_one_symbol(self):
        ls = load_symbol("SPY")
        for d in ls.dates:
            self.assertIsInstance(d, str)
            self.assertEqual(len(d), 10)
        for i in range(1, len(ls.dates)):
            self.assertLess(ls.dates[i - 1], ls.dates[i])


class T03_FirstAndLastDateMatchPins(unittest.TestCase):
    """T3: dates[0] == EXPECTED_FIRST_DATE, dates[-1] == EXPECTED_LAST_DATE."""

    def test_each_symbol(self):
        for sym in sorted(SYMBOLS):
            with self.subTest(symbol=sym):
                ls = load_symbol(sym)
                self.assertEqual(ls.dates[0], EXPECTED_FIRST_DATE)
                self.assertEqual(ls.dates[-1], EXPECTED_LAST_DATE)


class T04_LoadedSymbolFieldsMatchLockedCols(unittest.TestCase):
    """T4: LoadedSymbol exposes the seven locked column fields plus metadata.
    Note: the date-column LOCKED_COL name 'date' maps to the LoadedSymbol
    field name 'dates' (plural, for the tuple of values across rows). The
    six numeric columns keep their LOCKED_COL names as field names."""

    LOCKED_COL_TO_FIELD = {
        "date": "dates",
        "open": "open",
        "high": "high",
        "low": "low",
        "close": "close",
        "adj_close": "adj_close",
        "volume": "volume",
    }

    def test_dataclass_fields(self):
        ls = load_symbol("SPY")
        # Field for each locked column (per LOCKED_COL_TO_FIELD mapping)
        for col in LOCKED_COLS:
            field_name = self.LOCKED_COL_TO_FIELD[col]
            self.assertTrue(hasattr(ls, field_name),
                            f"missing field {field_name} for LOCKED_COL {col}")
        # Metadata fields
        for meta in ("symbol", "csv_path", "csv_sha256"):
            self.assertTrue(hasattr(ls, meta), f"missing metadata field {meta}")


class T05_Sha256MatchesAuditManifestPin(unittest.TestCase):
    """T5: returned csv_sha256 equals the audit manifest per_symbol pin."""

    def test_each_symbol(self):
        manifest = json.loads(AUDIT_MANIFEST_PATH.read_bytes().decode("utf-8"))
        for sym in sorted(SYMBOLS):
            with self.subTest(symbol=sym):
                ls = load_symbol(sym)
                pinned = manifest["per_symbol"][sym]["observed_sha256"]
                self.assertEqual(ls.csv_sha256, pinned)


class T06_RaisesOnAuditManifestMissing(unittest.TestCase):
    """T6: LoaderManifestMissingError when audit_manifest.json missing."""

    def test_temp_rename(self):
        target = AUDIT_MANIFEST_PATH
        backup = target.with_suffix(target.suffix + ".t6_temp_backup")
        target.rename(backup)
        try:
            with self.assertRaises(LoaderManifestMissingError):
                load_symbol("SPY")
        finally:
            backup.rename(target)


class T07_RaisesOnCsvMissing(unittest.TestCase):
    """T7: LoaderShaMismatchError (subclass of LoaderError) when CSV missing."""

    def test_temp_rename(self):
        csv_path = RAW_DIR / "SPY_1d_2014-01-01_2026-05-25.csv"
        backup = csv_path.with_suffix(csv_path.suffix + ".t7_temp_backup")
        csv_path.rename(backup)
        try:
            with self.assertRaises(LoaderError):
                load_symbol("SPY")
        finally:
            backup.rename(csv_path)


class T08_RaisesOnCsvShaMismatch(unittest.TestCase):
    """T8: LoaderShaMismatchError when manifest sha for a symbol is wrong
    (in-memory tamper of the manifest dict; no disk write)."""

    def test_inmemory_tamper(self):
        # Patch _load_audit_manifest to return a manifest with a wrong sha
        from external_research_hunter.s7_d1_cross_asset_donchian_yfinance_proxy_loader import loader as L
        real_manifest = json.loads(AUDIT_MANIFEST_PATH.read_bytes().decode("utf-8"))
        tampered = json.loads(json.dumps(real_manifest))  # deep copy
        tampered["per_symbol"]["SPY"]["observed_sha256"] = "0" * 64
        with mock.patch.object(L, "_load_audit_manifest", return_value=tampered):
            with self.assertRaises(LoaderShaMismatchError):
                load_symbol("SPY")


class T09_RaisesOnUnknownSymbol(unittest.TestCase):
    """T9: LoaderError on unknown symbol input."""

    def test_unknown(self):
        with self.assertRaises(LoaderError):
            load_symbol("ZZZ")


class T10_PreservesCloseAndAdjCloseSeparately(unittest.TestCase):
    """T10: close and adj_close are distinct tuples; at least one row differs
    on SPY (per Step 02c finding F1 evidence)."""

    def test_spy(self):
        ls = load_symbol("SPY")
        # Distinct tuple identity
        self.assertIsNot(ls.close, ls.adj_close)
        # At least one row differs (SPY pays dividends → divergence > 0)
        diffs = sum(1 for c, ac in zip(ls.close, ls.adj_close) if c != ac)
        self.assertGreater(diffs, 0, "expected at least one SPY row with close != adj_close")


class T11_OhlcvSanityInvariantsPerRow(unittest.TestCase):
    """T11: per-row OHLC invariants (verified again at the test layer)."""

    def test_one_symbol(self):
        ls = load_symbol("GLD")
        for i, (o, h, lo, c, ac, v) in enumerate(
            zip(ls.open, ls.high, ls.low, ls.close, ls.adj_close, ls.volume)
        ):
            with self.subTest(row=i):
                self.assertGreater(o, 0)
                self.assertGreater(h, 0)
                self.assertGreater(lo, 0)
                self.assertGreater(c, 0)
                self.assertGreater(ac, 0)
                self.assertGreaterEqual(v, 0)
                self.assertGreaterEqual(h, max(o, c, lo))
                self.assertLessEqual(lo, min(o, c))


class T12_LoadAllReturnsFourKeys(unittest.TestCase):
    """T12: load_all returns dict with exactly {SPY,TLT,GLD,USO}."""

    def test_keys(self):
        d = load_all()
        self.assertEqual(set(d.keys()), set(SYMBOLS))
        for sym in SYMBOLS:
            self.assertIsInstance(d[sym], LoadedSymbol)


class T13_LoadAllCrossSymbolDatesAligned(unittest.TestCase):
    """T13: four dates tuples produce equal sets."""

    def test_sets_equal(self):
        d = load_all()
        sets = [frozenset(d[s].dates) for s in sorted(SYMBOLS)]
        canonical = sets[0]
        for s in sets[1:]:
            self.assertEqual(s, canonical)


class T14_LoadAllRaisesOnCrossSymbolMisalignment(unittest.TestCase):
    """T14: monkeypatch the inner loader so one symbol's dates differ;
    load_all then raises LoaderCrossSymbolAlignmentError."""

    def test_inmemory_misalignment(self):
        from external_research_hunter.s7_d1_cross_asset_donchian_yfinance_proxy_loader import loader as L
        real_load = L._load_symbol_with_manifest

        def patched_load(symbol, manifest):
            ls = real_load(symbol, manifest)
            if symbol == "USO":
                # Bend one date so the cross-symbol set diverges
                new_dates = tuple(["1999-12-31"] + list(ls.dates[1:]))
                # rebuild via dataclasses.replace-like behavior
                import dataclasses
                return dataclasses.replace(ls, dates=new_dates)
            return ls

        with mock.patch.object(L, "_load_symbol_with_manifest", side_effect=patched_load):
            with self.assertRaises(LoaderCrossSymbolAlignmentError):
                load_all()


class T15_ImportPerformsNoFileIO(unittest.TestCase):
    """T15: importing the loader package performs no file IO.
    Patches builtins.open + Path.read_bytes before fresh-importing."""

    def test_no_io_at_import(self):
        # Drop the loader from sys.modules to force fresh import
        keys_to_drop = [k for k in list(sys.modules) if LOADER_PKG in k]
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
            importlib.import_module(LOADER_PKG)
        finally:
            builtins.open = real_open
            Path.read_bytes = real_read_bytes
            # Restore the original sys.modules entries
            for k, v in saved.items():
                sys.modules[k] = v

        # Filter out Python internal opens (importlib reads pyc/py files).
        # We only care about opens of files INSIDE this codebase that are not .py / .pyc
        suspect_open = [
            p for p in captured_open
            if isinstance(p, (str, Path)) and not str(p).endswith((".py", ".pyc"))
        ]
        suspect_read_bytes = [
            p for p in captured_read_bytes
            if not p.endswith((".py", ".pyc"))
        ]
        self.assertEqual(suspect_open, [], f"unexpected open() during import: {suspect_open}")
        self.assertEqual(suspect_read_bytes, [], f"unexpected Path.read_bytes during import: {suspect_read_bytes}")


class T16_NoForbiddenTokensInLoaderSource(unittest.TestCase):
    """T16: static grep of loader.py source for forbidden tokens.
    Zero hits outside designated comment-exclusion lines."""

    def test_grep(self):
        loader_src_path = (REPO_ROOT
                           / "external_research_hunter"
                           / "s7_d1_cross_asset_donchian_yfinance_proxy_loader"
                           / "loader.py")
        text = loader_src_path.read_text(encoding="utf-8")
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
        ]
        violations = []
        for tok in forbidden:
            for i, line in enumerate(text.splitlines(), start=1):
                if tok in line:
                    # Allow only on a comment-exclusion line
                    stripped = line.strip()
                    if stripped.startswith("#") and "FORBIDDEN_TOKEN_EXCLUSION" in line:
                        continue
                    violations.append((tok, i, line.rstrip()))
        self.assertEqual(violations, [], f"forbidden tokens found in loader.py: {violations}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
