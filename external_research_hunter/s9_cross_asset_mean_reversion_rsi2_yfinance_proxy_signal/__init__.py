"""s9 cross-asset RSI-2 mean-reversion signal module (ETF-proxy track).

Pure deterministic in-memory long-only RSI-2 trigger emitter over the
output of the Step 03 canonical loader. Public API re-exported here.
Importing this package performs no file IO.

Spec anchors:
  Tier-N spec:   docs/s9_cross_asset_mean_reversion_rsi2_tier_n_specification_plan.md
                 sha256 6690c0d789285598c400495f90ec0aa2c6db5165d449608762d9689bf807f409
                 commit 5bd8e62a1a614042a30e44f4060e54c7cdd20401
  Signal spec:   docs/s9_cross_asset_mean_reversion_rsi2_signal_module_specification_plan.md
                 sha256 59e5f401232f19342777445a0d992d1df23dda95a71419379e1daded89e9a0c9
                 commit c5393ab31a58059004b8cd337cd428eacbcbaece
"""
from .signal import (
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

__all__ = (
    "CrossSymbolSignalResult",
    "IN_SAMPLE_WINDOW",
    "RSI_EXIT_THRESHOLD",
    "RSI_LOOKBACK",
    "RSI_OVERSOLD_ENTRY_THRESHOLD",
    "SignalError",
    "SignalEvent",
    "SignalInputError",
    "SignalOosBlockedError",
    "SignalParameterOverrideError",
    "SignalResult",
    "compute_signals",
    "compute_signals_all",
)
