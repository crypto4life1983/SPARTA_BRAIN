"""Simulator module for s7 D1 cross-asset entry/exit channel execution.

Pure deterministic in-memory Faith System 1 mechanic executor over
LoadedSymbol + SignalResult inputs. In-sample only. Read-only over
loaded data. No file IO. No network. No vendor SDK. No brokerage.
No live trading.

See simulator.py for full docstring and README.md for usage.

Spec: docs/s7_d1_cross_asset_donchian_step_06_simulator_specification_plan.md
      sha256 f7581af358c676519d46f1a0bec486c35cf61f0f5f618faf7f000adf6223878b
      commit c964c59ce0d499b7feb24611d5ea2f6c7a840e08
"""
from .simulator import (
    CostTier,
    DEFAULT_STARTING_CASH,
    DailyEquityPoint,
    ENTRY_CHANNEL_LOOKBACK,
    ETF_DOLLAR_PER_SHARE,
    ETF_TICK_SIZE,
    EXIT_CHANNEL_LOOKBACK,
    ExitReason,
    IN_SAMPLE_WINDOW,
    K4_PORTFOLIO_MAXDD_PCT,
    MAX_UNITS_PER_SYMBOL,
    PER_UNIT_RISK_FRACTION,
    PYRAMID_STEP_N_MULTIPLE,
    STOP_DISTANCE_N_MULTIPLE,
    SimulationResult,
    SimulatorError,
    SimulatorInputError,
    SimulatorK4FiredError,
    SimulatorOosBlockedError,
    SimulatorParameterOverrideError,
    TradeGroup,
    TradeUnit,
    WILDER_ATR_LOOKBACK,
    simulate,
)

__all__ = (
    "CostTier",
    "DEFAULT_STARTING_CASH",
    "DailyEquityPoint",
    "ENTRY_CHANNEL_LOOKBACK",
    "ETF_DOLLAR_PER_SHARE",
    "ETF_TICK_SIZE",
    "EXIT_CHANNEL_LOOKBACK",
    "ExitReason",
    "IN_SAMPLE_WINDOW",
    "K4_PORTFOLIO_MAXDD_PCT",
    "MAX_UNITS_PER_SYMBOL",
    "PER_UNIT_RISK_FRACTION",
    "PYRAMID_STEP_N_MULTIPLE",
    "STOP_DISTANCE_N_MULTIPLE",
    "SimulationResult",
    "SimulatorError",
    "SimulatorInputError",
    "SimulatorK4FiredError",
    "SimulatorOosBlockedError",
    "SimulatorParameterOverrideError",
    "TradeGroup",
    "TradeUnit",
    "WILDER_ATR_LOOKBACK",
    "simulate",
)
