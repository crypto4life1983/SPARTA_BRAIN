# s20-d1 combined-universe weekly RS rotation — P6 IS diagnostic (sealed)

**report_seal:** `5c24bb4b813c6832624388bd9690190b50f4dca302a15a0577667fc71b97817f` · **Verdict: `READY_FOR_LONGER_BACKTEST`** · driver `none_no_gate_fired`

IS 2019-01-02..2023-12-29 (1258 bars); 48-name union; fresh $100k; warmup 160; cost S1; OOS rows (idx>=1258) NEVER touched.

| metric | s20 IS | s18 IS | s19 IS |
|---|---|---|---|
| closed_trades | 284 (56.9/y) | 229 | 226 |
| net P&L | $115,347.30 | — | — |
| expectancy/trade | $272.3014 | $370.28 | $262.64 |
| sharpe_proxy/trade | 0.129009 | — | +0.114 |
| win rate | 53.17% | — | — |
| max drawdown | 30.64% | — | — |
| total return | 115.35% | — | +65.83% |

K1(sharpe<0)=False · K2(exp<=0)=False · K9(n<100)=False · K4(mdd>50)=False · DR1=False. **Edge re-proven on the union (not inherited).** Selection caveat binding (union includes the known-OOS-good s18 basket -> weak generalization evidence). PAUSED · BLOCKED_AT_6_GATES · FRC NEVER_GRANTED. lessons.md NOT touched.
