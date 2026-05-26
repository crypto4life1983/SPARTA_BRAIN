"""Signal-computation module for s7 D1 cross-asset entry/exit channel triggers.

Pure deterministic in-memory channel-breakout trigger detector over the
output of the Step 03 loader. In-sample-only. No simulator, no backtest,
no out-of-sample inspection. See signal.py for full docstring and
README.md for usage.

Spec: docs/s7_d1_cross_asset_donchian_step_05_signal_computation_specification_plan.md
      sha256 6e039d352af7a7f20c99b1e26173f07539417a7f65b3c458458aa3ca1c8e2ff4
      commit 7e76bb785fa9f75b9fa483e26e6b826cde244851
"""
from .signal import (
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

__all__ = (
    "CrossSymbolSignalResult",
    "ENTRY_CHANNEL_LOOKBACK",
    "EXIT_CHANNEL_LOOKBACK",
    "IN_SAMPLE_WINDOW",
    "SignalError",
    "SignalEvent",
    "SignalInputError",
    "SignalOosBlockedError",
    "SignalParameterOverrideError",
    "SignalResult",
    "compute_signals",
    "compute_signals_all",
)
