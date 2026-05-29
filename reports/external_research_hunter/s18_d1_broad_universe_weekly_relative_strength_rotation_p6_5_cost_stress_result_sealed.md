# s18-d1 weekly RS rotation — P6.5 cost-stress (sealed)

**Authored (UTC):** `2026-05-29T02:16:05.277440Z` · **report_seal:** `28a4aa25b1634e44ef7c8e4b91084ff68c7a36190cfec65e4c91809403c12061`
**Verdict: `PASS_COST_STRESS_ELIGIBLE`** · DR fires: none

IS only; OOS hard-excluded. Weekly R=5, top-8 (highest cost_drag rung in the family).

| tier | net P&L | expectancy/trade | sharpe/trade | total costs |
|---|---|---|---|---|
| S0 | $88,458.44 | $386.28 | 0.1921 | $0 |
| S1 | $84,793.57 | $370.28 | 0.1867 | $3,166 |
| S2 | $82,972.82 | $362.33 | 0.1839 | $4,738 |
| S3 | $81,159.80 | $354.41 | 0.1811 | $6,303 |
| S4 | $77,556.75 | $338.68 | 0.1755 | $9,409 |

DR10 v2 inputs: annual_turnover(S1) ~20.16x · cost_drag_S2/capital annual 0.950% (edge-erosion 6.20%) · rule (turnover>0.50 AND S2_cost_drag>0.05). DR3=False DR5=False DR10v2=False.

## Status
PAUSED · BLOCKED_AT_6_GATES · FRC NEVER_GRANTED · DIAGNOSTIC_ONLY_NOT_LIVE_GRADE. lessons.md NOT touched.
