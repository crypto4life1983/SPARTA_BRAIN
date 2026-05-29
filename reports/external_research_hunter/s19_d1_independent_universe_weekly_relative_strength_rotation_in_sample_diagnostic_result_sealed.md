# s19-d1 independent-universe weekly RS rotation — P6 IS diagnostic (sealed; REPLICATION edge re-proof)

**Authored (UTC):** `2026-05-29T03:12:29.589328Z` · **report_seal:** `6ee2f41798a5b73b946375f62393cd3d9ea676b8ee9519fbbcb53abcba4c1c71`
**Verdict: `READY_FOR_LONGER_BACKTEST`**

IS 2019-01-02..2023-12-29 (1258 bars) ONLY; OOS hard-excluded. Weekly R=5, top-8, 126-21, long-only, relative-rank exit. Cost S1. INDEPENDENT universe; edge re-proven from scratch (NOT inherited from s18).

| metric | s19 | s18 (ref) |
|---|---|---|
| closed_trades | 226 (45.3/y) | 229 |
| expectancy/trade | $262.64 | $370.28 |
| sharpe_proxy/trade | 0.113516 | 0.187 |
| win rate | 54.42% | 56.33% |
| profit factor | 1.455241 | 1.94 |
| max drawdown | 30.74% | 32.19% |
| total return | 65.83% | 132.18% |

**Gates:** K1(sharpe<0)=False · K2(expectancy<=0)=False · K4(maxdd>50%)=False · K9(closed<100)=False (n=226).

## Status
PAUSED · BLOCKED_AT_6_GATES · FRC NEVER_GRANTED · DIAGNOSTIC_ONLY_NOT_LIVE_GRADE. lessons.md NOT touched.
