# s18-d1 weekly RS rotation — P6 IS diagnostic (sealed)

**Authored (UTC):** `2026-05-29T02:13:49.792046Z` · **report_seal:** `42c8c0f4070eece800bb13386b2e05332644736d4f7118ca8b2fd27302316161`
**Verdict: `READY_FOR_LONGER_BACKTEST`**

IS 2019-01-02..2023-12-29 (1258 bars) ONLY; OOS hard-excluded. Weekly R=5, top-8, 126-21, long-only, relative-rank exit. Cost S1.

| metric | value |
|---|---|
| rebalances | 220 |
| closed_trades | 229 (45.9/y) |
| net P&L (closed) | $84,793.57 |
| expectancy/trade | $370.2776 |
| sharpe_proxy/trade | 0.186665 |
| win rate | 56.33% |
| profit factor | 1.940923 |
| P/L ratio | 1.504591 |
| max drawdown | 32.19% |
| total return | 132.18% |
| final equity | $232,184.12 |

**Gates:** K1(sharpe<0)=False · K2(expectancy<=0)=False · K4(maxdd>50%)=False · K9(closed_trades<100)=False (n=229).
K9 already measured-PASS at the pre-SEAL gate; this run is the weekly EDGE re-proof (NOT inherited from monthly s17).

## Status
PAUSED · BLOCKED_AT_6_GATES · FRC NEVER_GRANTED · DIAGNOSTIC_ONLY_NOT_LIVE_GRADE. lessons.md NOT touched.
