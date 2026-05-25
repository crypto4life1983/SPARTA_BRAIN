"""Input validator for s7 D1 cross-asset daily-bar LoadedSymbol structures.

Pure in-memory checker over the output of the Step 03 canonical loader.
Public API re-exported here. Importing this package performs no file IO.
See validator.py for full docstring and README.md for usage.

Spec: docs/s7_d1_cross_asset_donchian_step_04_input_validator_specification_plan.md
      sha256 c1aad410b50e132540f66ee7c973048967b4f36a3cb0872bb5d55f25683466da
      commit a5acf59f497897c0c579b584e287f0e44139e337
"""
from .validator import (
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

__all__ = (
    "CrossSymbolValidationReport",
    "DONCHIAN_ENTRY_LOOKBACK",
    "DONCHIAN_EXIT_LOOKBACK",
    "IN_SAMPLE_WINDOW",
    "OUT_OF_SAMPLE_WINDOW",
    "POST_OOS_DIAGNOSTIC_WINDOW",
    "ValidationReport",
    "ValidatorCrossSymbolAlignmentError",
    "ValidatorError",
    "ValidatorInputError",
    "WarmupInsufficientError",
    "WindowMisfitError",
    "validate_all",
    "validate_loaded_symbol",
)
