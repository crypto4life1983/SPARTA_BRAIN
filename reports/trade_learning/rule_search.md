# Rule search — 2026-09-11

READ ONLY · OBSERVATION ONLY · NO LIVE READINESS CLAIM · NO STRATEGY APPROVAL · NO BROKER / NO ORDER

Signals (dedup): 31 · cells tested: 15 · correction: Bonferroni · p_adj ≤ 0.1 · budget 3/week

## Proposals this run

None. No cell survived the multiple-testing correction, or the weekly budget is used.

## Most negative cells (all tested)

| cell | n | mean R | win | p_raw | p_adj | candidate |
|---|---|---|---|---|---|---|
| hold_bucket=short | 6 | -0.7217 | 0.0 | 0.0805 | 1.0 | False |
| strategy=D2, direction=short | 8 | -0.7115 | 0.375 | 0.0435 | 0.6522 | False |
| strategy=D2, regime_at_open=TREND_DOWN | 7 | -0.6193 | 0.429 | 0.078 | 1.0 | False |
| strategy=G, direction=long | 7 | -0.3041 | 0.286 | 0.1939 | 1.0 | False |
| regime_at_open=TREND_DOWN, direction=short | 10 | -0.262 | 0.4 | 0.1554 | 1.0 | False |
| weekday=Tue | 5 | -0.111 | 0.2 | 0.3248 | 1.0 | False |
| regime_at_open=RANGE, direction=long | 5 | -0.0878 | 0.2 | 0.3348 | 1.0 | False |
| weekday=Thu | 6 | -0.0145 | 0.667 | 0.3503 | 1.0 | False |
| exchange=binance | 23 | -0.0054 | 0.348 | 0.095 | 1.0 | False |
| weekday=Sat | 5 | 0.0342 | 0.2 | 1.0 | 1.0 | False |
| weekday=Fri | 6 | 0.3325 | 0.5 | 1.0 | 1.0 | False |
| weekday=Wed | 6 | 0.4793 | 0.5 | 1.0 | 1.0 | False |
| hold_bucket=long | 22 | 0.524 | 0.591 | 1.0 | 1.0 | False |
| exchange=kraken | 8 | 0.9874 | 0.75 | 1.0 | 1.0 | False |
| regime_at_open=TREND_UP, direction=long | 5 | 1.0356 | 0.6 | 1.0 | 1.0 | False |

A proposal is a hypothesis for the ledger, scored only on trades that close after it was registered. Discovery evidence is frozen and never promotes anything. Nothing is applied.
