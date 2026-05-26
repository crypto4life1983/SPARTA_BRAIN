"""s9 cross-asset RSI-2 mean-reversion simulator module (ETF-proxy track).

Pure deterministic in-memory long-only RSI-2 mechanic executor. Consumes
LoadedSymbol structures (Step 03 loader) and SignalResult /
CrossSymbolSignalResult structures (s9 P6 signal module). Public API
re-exported here. Importing this package performs no file IO.

Spec anchors:
  Tier-N spec:    docs/s9_cross_asset_mean_reversion_rsi2_tier_n_specification_plan.md
                  sha256 6690c0d789285598c400495f90ec0aa2c6db5165d449608762d9689bf807f409
                  commit 5bd8e62a1a614042a30e44f4060e54c7cdd20401
  Signal spec:    docs/s9_cross_asset_mean_reversion_rsi2_signal_module_specification_plan.md
                  sha256 59e5f401232f19342777445a0d992d1df23dda95a71419379e1daded89e9a0c9
                  commit c5393ab31a58059004b8cd337cd428eacbcbaece
  Simulator spec: docs/s9_cross_asset_mean_reversion_rsi2_simulator_specification_plan.md
                  sha256 c64bbe7525ad06d5d870b51b6c5b8c9ba45a17675acc5ecc3e2faa4c545f83bf
                  commit 3a9a0de9eba9e448d0440fa45fb40e8107fb8e0f
"""
from .simulator import (
    CostTier,
    DEFAULT_STARTING_CASH,
    DailyEquityPoint,
    ETF_DOLLAR_PER_SHARE,
    ETF_TICK_SIZE,
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

__all__ = (
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
)
