# Crypto-D1 V2 RC2 Cross-Policy REPLAY (READ-ONLY, NO LIVE MONEY)

- Verdict: RC2_CROSS_POLICY_REPLAYS_COMPLETE
- Authorization: HUMAN_APPROVED_RC2_CROSS_POLICY_REPLAY
- Selected variant: V2_trend_plus_cash_regime
- Human decision (preserved): DO_NOT_PROMOTE_RESUME_POLICY_YET
- Blockers: none
- Best by mean return: RP4_breadth_2of3_above_sma200
- Best by worst drawdown: RP5_half_then_full_on_confirmation
- Best by mean Sharpe: RP5_half_then_full_on_confirmation
- RC1 leader: RP6_resume_after_volatility_cools | leads categories: (none) | leads all: False

## RP1_wait_7d_trend_on (FULL)
- Mean return: 40.89% | Worst drawdown: -41.41% | Mean Sharpe: 1.43
  - OOS_W1_2020_early_held_out: return 47.74%, maxDD -4.98%, Sharpe 3.16, kills 0, resumes 0
  - OOS_W2_2021H2_2022H1_straddle: return 84.95%, maxDD -41.41%, Sharpe 1.44, kills 1, resumes 1
  - OOS_W3_2022H2_2023H1_straddle: return 34.32%, maxDD -23.86%, Sharpe 1.03, kills 0, resumes 0
  - OOS_W4_2024H2_2025H1_straddle: return -3.44%, maxDD -25.90%, Sharpe 0.10, kills 0, resumes 0
## RP2_wait_14d_trend_on (FULL)
- Mean return: 34.04% | Worst drawdown: -41.41% | Mean Sharpe: 1.36
  - OOS_W1_2020_early_held_out: return 47.74%, maxDD -4.98%, Sharpe 3.16, kills 0, resumes 0
  - OOS_W2_2021H2_2022H1_straddle: return 57.55%, maxDD -41.41%, Sharpe 1.15, kills 1, resumes 1
  - OOS_W3_2022H2_2023H1_straddle: return 34.32%, maxDD -23.86%, Sharpe 1.03, kills 0, resumes 0
  - OOS_W4_2024H2_2025H1_straddle: return -3.44%, maxDD -25.90%, Sharpe 0.10, kills 0, resumes 0
## RP3_wait_30d_trend_on (FULL)
- Mean return: 30.02% | Worst drawdown: -41.47% | Mean Sharpe: 1.31
  - OOS_W1_2020_early_held_out: return 47.74%, maxDD -4.98%, Sharpe 3.16, kills 0, resumes 0
  - OOS_W2_2021H2_2022H1_straddle: return 41.46%, maxDD -41.47%, Sharpe 0.95, kills 1, resumes 1
  - OOS_W3_2022H2_2023H1_straddle: return 34.32%, maxDD -23.86%, Sharpe 1.03, kills 0, resumes 0
  - OOS_W4_2024H2_2025H1_straddle: return -3.44%, maxDD -25.90%, Sharpe 0.10, kills 0, resumes 0
## RP4_breadth_2of3_above_sma200 (FULL)
- Mean return: 42.06% | Worst drawdown: -41.41% | Mean Sharpe: 1.43
  - OOS_W1_2020_early_held_out: return 47.74%, maxDD -4.98%, Sharpe 3.16, kills 0, resumes 0
  - OOS_W2_2021H2_2022H1_straddle: return 89.64%, maxDD -41.41%, Sharpe 1.43, kills 1, resumes 1
  - OOS_W3_2022H2_2023H1_straddle: return 34.32%, maxDD -23.86%, Sharpe 1.03, kills 0, resumes 0
  - OOS_W4_2024H2_2025H1_straddle: return -3.44%, maxDD -25.90%, Sharpe 0.10, kills 0, resumes 0
## RP5_half_then_full_on_confirmation (HALF_THEN_FULL)
- Mean return: 41.87% | Worst drawdown: -41.41% | Mean Sharpe: 1.44
  - OOS_W1_2020_early_held_out: return 47.74%, maxDD -4.98%, Sharpe 3.16, kills 0, resumes 0
  - OOS_W2_2021H2_2022H1_straddle: return 88.88%, maxDD -41.41%, Sharpe 1.46, kills 1, resumes 1
  - OOS_W3_2022H2_2023H1_straddle: return 34.32%, maxDD -23.86%, Sharpe 1.03, kills 0, resumes 0
  - OOS_W4_2024H2_2025H1_straddle: return -3.44%, maxDD -25.90%, Sharpe 0.10, kills 0, resumes 0
## RP6_resume_after_volatility_cools (FULL)
- Mean return: 27.67% | Worst drawdown: -45.35% | Mean Sharpe: 1.28
  - OOS_W1_2020_early_held_out: return 47.74%, maxDD -4.98%, Sharpe 3.16, kills 0, resumes 0
  - OOS_W2_2021H2_2022H1_straddle: return 32.08%, maxDD -45.35%, Sharpe 0.81, kills 1, resumes 1
  - OOS_W3_2022H2_2023H1_straddle: return 34.32%, maxDD -23.86%, Sharpe 1.03, kills 0, resumes 0
  - OOS_W4_2024H2_2025H1_straddle: return -3.44%, maxDD -25.90%, Sharpe 0.10, kills 0, resumes 0

## Risk notes
- policies_verbatim_from_block_175_no_fitting
- windows_verbatim_from_block_180_same_as_rc1
- rankings_are_pure_reporting_nothing_promoted_or_changed
- results_are_research_evidence_only_promotion_requires_separate_human_command

## Gates (read-only metadata, UNCHANGED)
- paper_trading_gate: LOCKED
- micro_live_gate: LOCKED
- live_gate: LOCKED
- uses_real_money: False | executes_real_orders: False | ran_optimization: False
- Next required action: HUMAN_REVIEW_OF_RC2_CROSS_POLICY_RESULTS