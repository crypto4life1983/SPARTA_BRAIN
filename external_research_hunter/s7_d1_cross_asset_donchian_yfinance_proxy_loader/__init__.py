"""Canonical loader for s7 D1 cross-asset daily-bar CSVs (ETF proxy track).

Public API re-exported here. Importing this package performs no file IO.
See loader.py for full docstring and README.md for usage.

Spec:  docs/s7_d1_cross_asset_donchian_step_03_canonical_loader_specification_plan.md
       sha256 a713354bdb81dd10f5621aae18ab8f92adac5c3340a82e9d09bdb5ae1bbe2107
       commit f759251b238cd764fc96e0d62d814fd6c5ab3656
"""
from .loader import (
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

__all__ = (
    "AUDIT_MANIFEST_PATH",
    "EXPECTED_FIRST_DATE",
    "EXPECTED_LAST_DATE",
    "EXPECTED_ROWS",
    "LOCKED_COLS",
    "LoadedSymbol",
    "LoaderCrossSymbolAlignmentError",
    "LoaderError",
    "LoaderManifestMissingError",
    "LoaderShaMismatchError",
    "LoaderShapeMismatchError",
    "RAW_DIR",
    "SYMBOLS",
    "load_all",
    "load_symbol",
)
