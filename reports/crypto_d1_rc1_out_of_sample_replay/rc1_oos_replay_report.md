# Crypto-D1 V2 RC1 Out-of-Sample REPLAY (READ-ONLY, NO LIVE MONEY)

- Verdict: RC1_OUT_OF_SAMPLE_REPLAYS_COMPLETE
- Authorization: HUMAN_APPROVED_RC1_OUT_OF_SAMPLE_REPLAY
- Selected variant: V2_trend_plus_cash_regime
- Policy (parameters UNCHANGED): RP6_resume_after_volatility_cools
- Human decision (preserved): DO_NOT_PROMOTE_RESUME_POLICY_YET
- Blockers: none
- In-sample reference (carried, not recomputed): mean return 155.38%, worst maxDD -32.36%, mean Sharpe 0.57

## OOS_W1_2020_early_held_out (held_out_early_history)
- Window: 2020-01-01..2020-08-10 | Symbols: BTC, ETH
- Return: 47.74% | MaxDD: -4.98% | Sharpe: 3.16 | Kills: 0 | Resumes: 0
## OOS_W2_2021H2_2022H1_straddle (boundary_straddling_robustness)
- Window: 2021-07-01..2022-06-30 | Symbols: BTC, ETH, SOL
- Return: 32.08% | MaxDD: -45.35% | Sharpe: 0.81 | Kills: 1 | Resumes: 1
## OOS_W3_2022H2_2023H1_straddle (boundary_straddling_robustness)
- Window: 2022-07-01..2023-06-30 | Symbols: BTC, ETH, SOL
- Return: 34.32% | MaxDD: -23.86% | Sharpe: 1.03 | Kills: 0 | Resumes: 0
## OOS_W4_2024H2_2025H1_straddle (boundary_straddling_robustness)
- Window: 2024-07-01..2025-06-30 | Symbols: BTC, ETH, SOL
- Return: -3.44% | MaxDD: -25.90% | Sharpe: 0.10 | Kills: 0 | Resumes: 0

## Risk notes
- held_out_window_uses_btc_eth_only_sol_starts_2020_08_11
- held_out_window_sma_warmup_limits_exposure_no_pre_2020_history
- boundary_straddling_windows_are_window_robustness_not_strictly_out_of_sample
- results_are_research_evidence_only_promotion_requires_separate_human_command

## Gates (read-only metadata, UNCHANGED)
- paper_trading_gate: LOCKED
- micro_live_gate: LOCKED
- live_gate: LOCKED
- uses_real_money: False | executes_real_orders: False | ran_optimization: False
- Next required action: HUMAN_REVIEW_OF_RC1_OUT_OF_SAMPLE_RESULTS