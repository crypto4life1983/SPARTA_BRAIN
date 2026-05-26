"""Result-aggregation module for s7 D1 cross-asset Donchian yfinance proxy.

Third-tier boundary-crossing module. Consumes Step 06 simulator outputs
across S0/S1/S2/S3 cost tiers, computes portfolio-level performance
statistics, evaluates A1-A10 acceptance gates and K1-K11/K12 rejection
criteria per spec sections 13 and 14, and produces an IS-close verdict
from the closed 8-value VerdictReason enum.

The ELIGIBLE_FOR_OOS verdict does NOT auto-trigger OOS. It is a
structural attestation; OOS inspection requires a separately
authorized turn. Live trading, Strategy Lab promotion, brokerage
connection all remain blocked at separate plans regardless of verdict.

Spec: docs/s7_d1_cross_asset_donchian_step_07_result_aggregation_specification_plan.md
      sha256 fc0f0dcd34b75055405fc1ba2bbbf4a60e57e2bb1a692feb86999c31e3108983
      commit b99151caceb307a3708dcb5ac3a97e5131df02df
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
