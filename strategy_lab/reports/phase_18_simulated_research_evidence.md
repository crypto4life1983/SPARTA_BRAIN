# Strategy Lab Phase 18 Simulated Research Evidence

Generated at: 2026-05-12T13:43:20.361165+00:00

## Lifecycle Distribution
- Before: {}
- After: {'BACKTESTED': 1, 'IN_RESEARCH': 1}

## Pass Candidate
- seed_atr_compression_expansion
  - evidence recommendation: ready_for_review
  - lifecycle state: BACKTESTED
  - missing evidence: none

## Fail Candidate
- seed_regime_filter_overlay
  - evidence recommendation: reject_or_rework
  - lifecycle state: IN_RESEARCH
  - missing evidence: none

## Evidence Summary
- pass backtest total_return: 18.0
- fail backtest total_return: -4.0
- pass anti_overfit passed: True
- fail anti_overfit passed: False
- pass regime_score passed: True
- fail regime_score passed: False

## Safety
- isolated: true
- frozen_stack_touched: false
- profit_brain_touched: false
- execution_imports: false
- no_live_logic: true
