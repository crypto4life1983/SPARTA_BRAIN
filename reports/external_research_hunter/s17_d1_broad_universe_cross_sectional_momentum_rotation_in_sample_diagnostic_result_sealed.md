# s17-d1 broad-universe cross-sectional momentum — P6 IS diagnostic (sealed)

**Authored (UTC):** `2026-05-29T01:03:14.170416Z` · **report_seal:** `7abe7a3f1c20df3cffff884157e2d9a8881e283da389146a400e29a43acc22c6`
**Verdict: `INSUFFICIENT_SAMPLE`**

IS window 2019-01-02 .. 2023-12-29 (1258 bars) ONLY; OOS rows hard-excluded (never in signal logic). Locked rule:
126-21 momentum, rank 24, top-6 equal-weight, monthly rebalance, relative-rank exit, long-only. Cost tier S1.

| metric | value |
|---|---|
| rebalances | 53 |
| closed_trades | 85 (= 17.0/yr) |
| net P&L (closed) | $96,114.08 |
| expectancy / trade | $1,130.7539 |
| sharpe_proxy / trade | 0.285318 |
| win rate | 63.53% |
| profit factor | 2.418182 |
| P/L ratio | 1.388216 |
| max drawdown | 31.40% |
| total return | 145.79% |
| final equity | $245,789.47 |

**Gates:** K1(sharpe<0)=False · K2(expectancy<=0)=False · K4(maxdd>50%)=False · K9(closed_trades<100)=True (n=85, floor 100).

K9 note: closed_trades counts completed rotations only (DA12); open positions at IS end marked-to-market, not counted.

## Status
trading PAUSED · live BLOCKED_AT_6_GATES · FRC NEVER_GRANTED · DIAGNOSTIC_ONLY_NOT_LIVE_GRADE. lessons.md NOT touched.
