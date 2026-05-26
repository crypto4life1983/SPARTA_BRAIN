"""s9 cross-asset RSI-2 mean-reversion result-aggregation module (ETF-proxy track).

Pure deterministic in-memory aggregator consuming the four cost-tier s9
SimulationResult instances plus the four LoadedSymbol structures plus
the C1-C8 safety attestations, producing the IS-close verdict from the
8-value closed VerdictReason enum per the s9 Tier-N spec sections 16-17.
Public API re-exported here. Importing this package performs no file IO.

Spec anchors:
  Tier-N spec:    docs/s9_cross_asset_mean_reversion_rsi2_tier_n_specification_plan.md
                  sha256 6690c0d789285598c400495f90ec0aa2c6db5165d449608762d9689bf807f409
                  commit 5bd8e62a1a614042a30e44f4060e54c7cdd20401
  Aggregator-reuse decision plan:
                  docs/s9_cross_asset_mean_reversion_rsi2_aggregator_reuse_decision_plan.md
                  sha256 af6f8fd6d1de1b91e07679a6ce6e54660d961b6d9c20efac2d7da964d60d50f6
                  commit 113f5b954e189088e6ddda18a2138abb27ff92e2
"""
from .aggregator import (
    A10_CAP_BINDING_EVENTS_MAX,
    A1_MIN_CLOSED_TRADES,
    A2_SHARPE_PROXY_MIN,
    A3_EXPECTANCY_MIN,
    A4_TRADE_CURVE_MAXDD_PCT_MAX,
    A5_PER_MARKET_WR_GAP_MIN_COUNT,
    A5_PORTFOLIO_WR_GAP_PP_MIN,
    A7_EFFECTIVE_INDEPENDENT_BETS_MIN,
    AGateResults,
    AggregationResult,
    AggregatorError,
    AggregatorInputError,
    AggregatorOosBlockedError,
    AggregatorParameterOverrideError,
    AggregatorProvenanceDriftError,
    CostStressRow,
    DR2_S2_S3_DEGRADATION_THRESHOLD_FRACTION,
    DR_STRESS_TIERS_REQUIRED,
    IN_SAMPLE_WINDOW,
    K10_AVG_PAIRWISE_DEPENDENCE_MAX,
    K11_CAP_BINDING_EVENTS_MAX,
    KCriteriaResults,
    PerSymbolStats,
    PerTradeStats,
    PortfolioStats,
    VerdictReason,
    aggregate,
)

__all__ = (
    "A10_CAP_BINDING_EVENTS_MAX",
    "A1_MIN_CLOSED_TRADES",
    "A2_SHARPE_PROXY_MIN",
    "A3_EXPECTANCY_MIN",
    "A4_TRADE_CURVE_MAXDD_PCT_MAX",
    "A5_PER_MARKET_WR_GAP_MIN_COUNT",
    "A5_PORTFOLIO_WR_GAP_PP_MIN",
    "A7_EFFECTIVE_INDEPENDENT_BETS_MIN",
    "AGateResults",
    "AggregationResult",
    "AggregatorError",
    "AggregatorInputError",
    "AggregatorOosBlockedError",
    "AggregatorParameterOverrideError",
    "AggregatorProvenanceDriftError",
    "CostStressRow",
    "DR2_S2_S3_DEGRADATION_THRESHOLD_FRACTION",
    "DR_STRESS_TIERS_REQUIRED",
    "IN_SAMPLE_WINDOW",
    "K10_AVG_PAIRWISE_DEPENDENCE_MAX",
    "K11_CAP_BINDING_EVENTS_MAX",
    "KCriteriaResults",
    "PerSymbolStats",
    "PerTradeStats",
    "PortfolioStats",
    "VerdictReason",
    "aggregate",
)
