# Crypto-D1 V2 Resume-Policy SIMULATION (READ-ONLY, NO LIVE MONEY)

- Verdict: RESUME_POLICY_RERUNS_COMPLETE
- Authorization: APPROVE_RESUME_POLICY_SIMULATION_RERUN_READ_ONLY
- Selected variant: V2_trend_plus_cash_regime
- Blockers: none
- Best by mean return: RP6_resume_after_volatility_cools
- Best by worst drawdown: RP6_resume_after_volatility_cools
- Best by mean Sharpe: RP6_resume_after_volatility_cools

## RP1_wait_7d_trend_on (FULL)
- Resume after >= 7 days halted, only if the 200-day trend filter is back on for >= 2 of 3 sleeves.
- Mean return: 68.33% | Worst drawdown: -60.73% | Mean Sharpe: 0.09
  - 2021_bull_then_may_crash: return 14.10%, maxDD -60.73%, Sharpe 0.45, kills 29, resumes 29
  - 2022_bear: return -19.75%, maxDD -19.69%, Sharpe -1.87, kills 0, resumes 0
  - 2023_2024_recovery: return 277.79%, maxDD -37.20%, Sharpe 1.57, kills 1, resumes 1
  - 2025_2026_recent: return 1.18%, maxDD -26.58%, Sharpe 0.19, kills 1, resumes 1
## RP2_wait_14d_trend_on (FULL)
- Resume after >= 14 days halted, only if trend filter is back on for >= 2 of 3 sleeves.
- Mean return: 68.62% | Worst drawdown: -53.85% | Mean Sharpe: 0.08
  - 2021_bull_then_may_crash: return 16.01%, maxDD -53.85%, Sharpe 0.48, kills 13, resumes 12
  - 2022_bear: return -19.75%, maxDD -19.69%, Sharpe -1.87, kills 0, resumes 0
  - 2023_2024_recovery: return 279.03%, maxDD -36.99%, Sharpe 1.58, kills 1, resumes 1
  - 2025_2026_recent: return -0.82%, maxDD -26.58%, Sharpe 0.14, kills 1, resumes 1
## RP3_wait_30d_trend_on (FULL)
- Resume after >= 30 days halted, only if trend filter is back on for >= 2 of 3 sleeves.
- Mean return: 120.79% | Worst drawdown: -50.46% | Mean Sharpe: 0.40
  - 2021_bull_then_may_crash: return 122.74%, maxDD -50.46%, Sharpe 1.30, kills 3, resumes 3
  - 2022_bear: return -19.75%, maxDD -19.69%, Sharpe -1.87, kills 0, resumes 0
  - 2023_2024_recovery: return 372.22%, maxDD -28.84%, Sharpe 1.84, kills 1, resumes 1
  - 2025_2026_recent: return 7.93%, maxDD -26.58%, Sharpe 0.33, kills 1, resumes 0
## RP4_breadth_2of3_above_sma200 (FULL)
- Resume as soon as >= 2 of 3 assets close above their 200-day SMA (no minimum wait).
- Mean return: 127.48% | Worst drawdown: -49.52% | Mean Sharpe: 0.35
  - 2021_bull_then_may_crash: return 204.26%, maxDD -49.52%, Sharpe 1.42, kills 7, resumes 7
  - 2022_bear: return -19.75%, maxDD -19.69%, Sharpe -1.87, kills 0, resumes 0
  - 2023_2024_recovery: return 325.59%, maxDD -30.15%, Sharpe 1.67, kills 1, resumes 1
  - 2025_2026_recent: return -0.20%, maxDD -26.58%, Sharpe 0.17, kills 1, resumes 1
## RP5_half_then_full_on_confirmation (HALF_THEN_FULL)
- Resume at HALF exposure once breadth returns, then scale to FULL after 5 confirming days.
- Mean return: 130.46% | Worst drawdown: -45.85% | Mean Sharpe: 0.36
  - 2021_bull_then_may_crash: return 225.12%, maxDD -45.85%, Sharpe 1.55, kills 4, resumes 4
  - 2022_bear: return -19.75%, maxDD -19.69%, Sharpe -1.87, kills 0, resumes 0
  - 2023_2024_recovery: return 319.02%, maxDD -30.34%, Sharpe 1.67, kills 1, resumes 1
  - 2025_2026_recent: return -2.56%, maxDD -26.58%, Sharpe 0.11, kills 1, resumes 1
## RP6_resume_after_volatility_cools (FULL)
- Resume only when 30-day realized volatility falls back to/below its pre-halt median, with breadth >= 2.
- Mean return: 155.38% | Worst drawdown: -32.36% | Mean Sharpe: 0.57
  - 2021_bull_then_may_crash: return 303.42%, maxDD -32.36%, Sharpe 2.01, kills 2, resumes 2
  - 2022_bear: return -19.75%, maxDD -19.69%, Sharpe -1.87, kills 0, resumes 0
  - 2023_2024_recovery: return 329.91%, maxDD -28.53%, Sharpe 1.82, kills 1, resumes 1
  - 2025_2026_recent: return 7.93%, maxDD -26.58%, Sharpe 0.33, kills 1, resumes 0

## Gates (read-only metadata, UNCHANGED)
- paper_trading_gate: LOCKED
- micro_live_gate: LOCKED
- live_gate: LOCKED
- uses_real_money: False | executes_real_orders: False | ran_optimization: False
- Next required action: HUMAN_APPROVED_RESUME_POLICY_RESULTS_REVIEW