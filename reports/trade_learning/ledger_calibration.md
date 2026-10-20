# Hypothesis ledger calibration — 2026-10-20

**READ ONLY · OBSERVATION ONLY · NO LIVE READINESS CLAIM · NO STRATEGY APPROVAL · NO BROKER / NO ORDER**

How fast the loop gathers forward evidence per hypothesis, how long verdicts take, and whether the frozen in-sample evidence has so far pointed the same way as the forward counterfactual. This measures the machine's judging, not the trades.

## Loop totals

- hypotheses 11 · by status {"APPLIED": 5, "SHADOW": 6} · nightly runs on record 59
- median forward accrual 10.0 signals per 30 days · share with any forward evidence 0.82
- cannot reach the n >= 20 floor at the current rate: blockwhere__strategy=D__direction=short, unblock__TREND_DOWN_BLOCKS_LONG
- APPLIED rules under the rollback check: 5 · post-apply n: {"block_long_in_TREND_DOWN": 12, "enforce_hard_stop": 12, "partial_tp_or_trail_1R": 2, "partial_tp_or_trail_2R": 12, "review_pause_D2": 12}
- in-sample vs forward sign: {"agree": 2, "disagree": 6, "flat": 0, "no forward data": 2, "no in-sample sign": 1}
- replay priors file (reports/trade_learning/replay_priors.json): present

## Per hypothesis

| id | kind | status | registered | days | fwd n | fwd mean ΔR | per 30d | days to n>=20 | days to verdict | in-sample sign (source) | agreement | replay prior |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| block_long_in_TREND_DOWN | block | APPLIED | 2026-09-11 | 39 | 12 | -0.553 | 10.29 | 23 | 0 | + (-avg_R) | disagree | - |
| blockwhere__hold_bucket=short | block_where | SHADOW | 2026-10-10 | 10 | 2 | +1.011 | 6.0 | 90 | - | + (-mean_R) | agree | - |
| blockwhere__strategy=D__direction=short | block_where | SHADOW | 2026-09-23 | 27 | 0 | - | 0.0 | never at current rate | - | + (-short_mean_R) | no forward data | - |
| enforce_hard_stop | stop_cap | APPLIED | 2026-09-11 | 39 | 12 | -0.553 | 10.29 | 23 | 0 | + (+total_excess_loss_R) | disagree | - |
| extend_timeout__40 | extend_timeout | SHADOW | 2026-10-10 | 10 | 1 | -1.032 | 3.0 | 190 | - | - (n_resolved == 0) | no in-sample sign | - |
| partial_tp_or_trail_1R | partial | APPLIED | 2026-10-11 | 9 | 2 | -1.059 | 10.0 | 54 | 3 | + (mean_delta_R) | disagree | - |
| partial_tp_or_trail_2R | partial_2R | APPLIED | 2026-09-11 | 39 | 12 | -0.553 | 10.29 | 23 | 0 | + (mean_MFE_R - mean_realized_R) | disagree | - |
| review_pause_D2 | block | APPLIED | 2026-09-11 | 39 | 12 | -0.553 | 10.29 | 23 | 0 | + (-avg_R) | disagree | - |
| unblock__SLOT_OCCUPIED | unblock | SHADOW | 2026-10-07 | 13 | 9 | -0.065 | 20.77 | 16 | - | - (mean_hyp_R) | agree | - |
| unblock__TREND_DOWN_BLOCKS_LONG | unblock | SHADOW | 2026-09-23 | 27 | 0 | - | 0.0 | never at current rate | - | + (mean_hyp_R) | no forward data | - |
| unblock__TREND_UP_BLOCKS_SHORT | unblock | SHADOW | 2026-09-23 | 27 | 8 | +0.059 | 8.89 | 40 | - | - (mean_hyp_R) | disagree | - |

## Reading it

- *per 30d* is forward signals accrued per 30 days since registration; *days to n>=20* projects the pre-registered floor at that rate. A row that says never at current rate is a hypothesis the paper book is not producing trades for; it cannot be judged forward without more evidence flow.
- For an APPLIED rule *fwd n* and *fwd mean* are the post-apply closes and their mean R (applied.n_after / mean_R_after, the rollback-check sample), counted from the apply date; for the others they are the counterfactual forward signals since registration.
- *agreement* compares the sign the frozen in-sample evidence implied for the rule with the sign of the forward counterfactual so far (for APPLIED rules: with the sign of the post-apply mean R, which is the system's result, not the rule's, so read it loosely). Small n makes this noisy; it is a calibration trace, not a verdict.
- Nothing here changes a status, a threshold or the paper bot.

_READ ONLY · OBSERVATION ONLY · NO LIVE READINESS CLAIM · NO STRATEGY APPROVAL · NO BROKER / NO ORDER_
