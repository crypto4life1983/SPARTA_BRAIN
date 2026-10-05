# Rule search — 2026-10-05

READ ONLY · OBSERVATION ONLY · NO LIVE READINESS CLAIM · NO STRATEGY APPROVAL · NO BROKER / NO ORDER

Signals (dedup): 34 · cells tested: 15 · correction: Bonferroni · p_adj ≤ 0.1 · budget 3/week

## Proposals this run

None. No cell survived the multiple-testing correction, or the weekly budget is used.

## Most negative cells (all tested)

| cell | n | mean R | win | p_raw | p_adj | candidate |
|---|---|---|---|---|---|---|
| hold_bucket=short | 8 | -1.3759 | 0.0 | 0.0075 | 0.1124 | False |
| strategy=G, direction=long | 7 | -1.0551 | 0.286 | 0.06 | 0.8996 | False |
| strategy=D2, direction=short | 8 | -0.7115 | 0.375 | 0.1179 | 1.0 | False |
| strategy=D2, regime_at_open=TREND_DOWN | 7 | -0.6193 | 0.429 | 0.1849 | 1.0 | False |
| weekday=Tue | 5 | -0.5492 | 0.2 | 0.2484 | 1.0 | False |
| regime_at_open=RANGE, direction=long | 5 | -0.3982 | 0.2 | 0.3128 | 1.0 | False |
| weekday=Thu | 7 | -0.3944 | 0.571 | 0.2919 | 1.0 | False |
| regime_at_open=TREND_DOWN, direction=short | 12 | -0.3876 | 0.333 | 0.1949 | 1.0 | False |
| exchange=binance | 26 | -0.3243 | 0.308 | 0.045 | 0.6747 | False |
| weekday=Sat | 5 | -0.2902 | 0.2 | 0.3568 | 1.0 | False |
| weekday=Wed | 8 | 0.1321 | 0.375 | 1.0 | 1.0 | False |
| weekday=Fri | 6 | 0.3325 | 0.5 | 1.0 | 1.0 | False |
| hold_bucket=long | 22 | 0.4961 | 0.591 | 1.0 | 1.0 | False |
| exchange=kraken | 8 | 0.9874 | 0.75 | 1.0 | 1.0 | False |
| regime_at_open=TREND_UP, direction=long | 5 | 1.0356 | 0.6 | 1.0 | 1.0 | False |

A proposal is a hypothesis for the ledger, scored only on trades that close after it was registered. Discovery evidence is frozen and never promotes anything. Nothing is applied.
