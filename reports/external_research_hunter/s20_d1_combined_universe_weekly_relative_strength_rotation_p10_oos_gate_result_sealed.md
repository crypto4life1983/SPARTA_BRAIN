# s20-d1 combined-universe weekly RS rotation — P10 OOS gate (sealed)

**report_seal:** `529b224dc42b628df0778303763a52c313261f01de26a31a90895b99cfaab88f` · **Verdict: `OOS_CONFIRMED_DIAGNOSTIC`** · driver `none_no_dr_fired`

OOS 2024-01-02..2025-12-30 (501 bars); 48-name union; fresh $100k; warmup from prior bars only; cost S1.

| metric | s20 OOS | s18 OOS | s19 OOS |
|---|---|---|---|
| closed_trades | 134 (67.2/y) | 117 (58.7/y) | 87 (43.6/y) |
| net P&L | $60,003.60 | +$39,786 | +$44,050 |
| expectancy/trade | $353.1933 | +$210 | +$336 |
| sharpe/trade | 0.214428 | +0.125 | +0.238 |
| win rate | 55.22% | 59.8% | 59.8% |
| max drawdown | 20.93% | — | 21.09% |
| total return | 60.00% | +39.79% | +44.05% |
| OOS verdict | **OOS_CONFIRMED_DIAGNOSTIC** | OOS_CONFIRMED | INSUFFICIENT_SAMPLE/K9 |

IS ref (ab7b232): +$115,347.30, +$272.3/trade. DR1=False · K9_insuf=False (n=134, 67.2/y) · DR4=False. **Solves the s19 OOS-K9 blocker WITH P&L: True** (134 >= 100, 67.2 >= 50/y). Selection caveat binding (union includes known-OOS-good s18). PAUSED · BLOCKED_AT_6_GATES · FRC NEVER_GRANTED. lessons.md NOT touched.
