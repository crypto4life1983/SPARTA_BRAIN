# Strategy Lab Seed Candidate Batch

Generated at: 2026-05-12T13:38:52.326033+00:00
Idea count: 5
Candidate count: 5

## Lifecycle Distribution
- IDEA: 5

## Seed Ideas
- seed_donchian_breakout_confirmation: Donchian Breakout Confirmation
  - hypothesis: A breakout only counts when Donchian expansion is confirmed by ATR expansion and follow-through, reducing false expansion signals.
  - symbols: BTCUSDT, ETHUSDT, XRPUSDT
  - timeframe: 1D
  - risk_notes: Can whipsaw in choppy compression regimes and may lag in fast reversals.
- seed_atr_compression_expansion: ATR Compression Expansion
  - hypothesis: Compression in ATR followed by directional release can signal a tradable expansion event before the move becomes crowded.
  - symbols: BTCUSDT, ETHUSDT, XRPUSDT
  - timeframe: 1D
  - risk_notes: May underperform in persistently trendless range conditions.
- seed_trend_pullback_continuation: Trend Pullback Continuation
  - hypothesis: A trend filter plus pullback entry can catch continuation moves after brief retracements without chasing extended moves.
  - symbols: BTCUSDT, ETHUSDT, XRPUSDT
  - timeframe: 1D
  - risk_notes: Can fail when pullbacks become full reversals or when trend filters lag too much.
- seed_extreme_expansion_mean_reversion: Extreme Expansion Mean Reversion
  - hypothesis: After abnormal expansion, exhaustion often creates a short-term reversion window back toward fair value.
  - symbols: BTCUSDT, ETHUSDT, XRPUSDT
  - timeframe: 1D
  - risk_notes: Can be dangerous in strong trend continuation or news-driven breakouts.
- seed_regime_filter_overlay: Regime Filter Overlay
  - hypothesis: A regime overlay can switch between behavior modes based on volatility regime and suppress poor-fit entries when the market environment is unfavorable.
  - symbols: BTCUSDT, ETHUSDT, XRPUSDT
  - timeframe: 1D
  - risk_notes: Requires reliable regime detection and can over-block if the filter is too strict.

## Safety
- isolated: true
- frozen_stack_touched: false
- profit_brain_touched: false
- execution_imports: false
- lifecycle_state: IDEA only
