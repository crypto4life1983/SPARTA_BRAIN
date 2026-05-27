# Next-Research-Track Selection Plan — L1 Discount Revision Memo (sealed)

- **Seal SHA-256:** `e41690d6b1ecd824fa5521525f64cdd13e3e558c6b8a93123e4a83f1d515c5b3`
- **Authored at UTC:** 2026-05-27T16:40:53.824964+00:00
- **Status:** `PLAN_ONLY` — no build, no execution, no fetch authorized
- **Authorization phrase:** `Authorize a PLAN-only revision/comparison memo for 0e3f9d4`

## 1. S12-D1 predecessor acceptance

- Lifecycle state: **`PARKED_SAFE_BUT_INSUFFICIENT_SAMPLE_AT_IS`** at commit `ecbd001` (P11 PARK; seal `b9722d42…`)
- Chain byte-stable. No revival authorized.

## 2. `0e3f9d4` selection plan: PLAN_ONLY confirmed

Plan opener, §10 HARD BOUNDARIES, §11 boundary table, and §14 all attest no build/execution authorized. Plan enumerates explicit next-step authorization phrases requiring fresh operator action. **Confirmed PLAN_ONLY.**

## 3. L1 epistemic discount applied

Lesson L1 (verbatim from S12-D1 P11 PARK):

> *Linear-scaling extrapolation from S10-D2's NQ 10y (54 trades) to MNQ 4.6y was 2-3x over-optimistic. Per-instrument signal density does not scale linearly across instruments / windows.*

Discount factors applied: **2× and 3×**. Scope: any extrapolated estimate (instrument/window/mechanic). Calendar-rule estimates (weekly/bi-weekly rebalance counts) get a related trade-realization-fraction discount.

## 4. K9 floors

| Window | Length (y) | Required trades/y |
|---|---:|---:|
| IS | 4.6 | **21.74** |
| **OOS** | **2.0** | **50.0** (binding) |

## 5. Per-track K9-reachability analysis (central + 2× + 3× discount)

### T1 — RSI(2) bi-directional on MNQ.c.0

- **Source note:** Estimate sourced from 0e3f9d4 §5.2; **NO citation, NO hand-count, NO published reference provided**. Plausibly grounded in Connors RSI(2) literature for daily-bar mean-reversion on liquid markets (Larry Connors trade rates on S&P 500 stocks typically ~30-50 trades/year long-only), doubled approximately for bi-directional extension, but the transfer from equity stocks to a single futures index has NOT been validated by the plan. Per L1 lesson, single-instrument signal density does not scale linearly from analogous markets. CLASSIFY AS HEURISTIC ESTIMATE pending operator-supplied source or hand-count.

| Scenario | Trades/y (low-mid-high) | IS K9 reach (mid) | OOS K9 reach (mid) |
|---|---|---|---|
| central | 50.0 – 57.5 – 65.0 | 57.5/y vs floor 21.74/y (margin 2.645x) → **CLEARS_WITH_MARGIN** | 57.5/y vs floor 50.00/y (margin 1.15x) → **CLEARS_BORDERLINE** |
| 2x_discount | 25.0 – 28.75 – 32.5 | 28.75/y vs floor 21.74/y (margin 1.322x) → **CLEARS_BORDERLINE** | 28.75/y vs floor 50.00/y (margin 0.575x) → **FAILS** |
| 3x_discount | 16.67 – 19.17 – 21.67 | 19.17/y vs floor 21.74/y (margin 0.882x) → **FAILS** | 19.17/y vs floor 50.00/y (margin 0.383x) → **FAILS** |

### T2 — Multi-instrument Donchian-15/8 micro-futures basket

- **Source note:** Estimate is 4-instrument basket * (10 trades/year per instrument); the 10/y per-instrument figure is the OBSERVED s12-d1 P6 IS result for Donchian-15/8 on MNQ.c.0. The 4x multiplier ASSUMES the other 3 candidate instruments (MES, MYM, M2K) produce signal density similar to MNQ. This cross-instrument assumption is precisely the L1 failure mode (extrapolating density across instruments). Discount applies.

| Scenario | Trades/y (low-mid-high) | IS K9 reach (mid) | OOS K9 reach (mid) |
|---|---|---|---|
| central | 40.0 – 40.0 – 40.0 | 40.0/y vs floor 21.74/y (margin 1.84x) → **CLEARS_WITH_MARGIN** | 40.0/y vs floor 50.00/y (margin 0.8x) → **FAILS** |
| 2x_discount | 20.0 – 20.0 – 20.0 | 20.0/y vs floor 21.74/y (margin 0.92x) → **FAILS** | 20.0/y vs floor 50.00/y (margin 0.4x) → **FAILS** |
| 3x_discount | 13.33 – 13.33 – 13.33 | 13.33/y vs floor 21.74/y (margin 0.613x) → **FAILS** | 13.33/y vs floor 50.00/y (margin 0.267x) → **FAILS** |

### T3 — Vol-targeting MNQ.c.0 bi-weekly rebalance

- **Source note:** Estimate is a CALENDAR rule (52 weeks / 2 = 26 bi-weekly rebalances). Not an extrapolated signal-density estimate. However, not every rebalance produces a contract turnover (if target matches current position, no trade is executed). The 26/y figure is an UPPER BOUND on trade count, not a central estimate. L1 discount is conceptually different here: it represents the fraction of rebalances that actually produce trades, which could plausibly be 50-66% for a slowly-drifting vol regime. Discount applied as such.

| Scenario | Trades/y (low-mid-high) | IS K9 reach (mid) | OOS K9 reach (mid) |
|---|---|---|---|
| central | 26.0 – 26.0 – 26.0 | 26.0/y vs floor 21.74/y (margin 1.196x) → **CLEARS_BORDERLINE** | 26.0/y vs floor 50.00/y (margin 0.52x) → **FAILS** |
| 2x_discount | 13.0 – 13.0 – 13.0 | 13.0/y vs floor 21.74/y (margin 0.598x) → **FAILS** | 13.0/y vs floor 50.00/y (margin 0.26x) → **FAILS** |
| 3x_discount | 8.67 – 8.67 – 8.67 | 8.67/y vs floor 21.74/y (margin 0.399x) → **FAILS** | 8.67/y vs floor 50.00/y (margin 0.173x) → **FAILS** |

### T3-weekly (alternate) — Vol-targeting MNQ.c.0 weekly rebalance

- **Source note:** Calendar rule (52 weekly rebalances). Same upper-bound caveat as bi-weekly variant: not every rebalance produces a trade. L1-equivalent discount represents trade-realization fraction.

| Scenario | Trades/y (low-mid-high) | IS K9 reach (mid) | OOS K9 reach (mid) |
|---|---|---|---|
| central | 52.0 – 52.0 – 52.0 | 52.0/y vs floor 21.74/y (margin 2.392x) → **CLEARS_WITH_MARGIN** | 52.0/y vs floor 50.00/y (margin 1.04x) → **AT_FLOOR_INDETERMINATE** |
| 2x_discount | 26.0 – 26.0 – 26.0 | 26.0/y vs floor 21.74/y (margin 1.196x) → **CLEARS_BORDERLINE** | 26.0/y vs floor 50.00/y (margin 0.52x) → **FAILS** |
| 3x_discount | 17.33 – 17.33 – 17.33 | 17.33/y vs floor 21.74/y (margin 0.797x) → **FAILS** | 17.33/y vs floor 50.00/y (margin 0.347x) → **FAILS** |

## 6. Likely terminal risk under L1 discount

| Track | Likely terminal risk |
|---|---|
| T1 | `INSUFFICIENT_SAMPLE_LIKELY_AT_OOS_UNDER_L1_2X_DISCOUNT` |
| T2 | `INSUFFICIENT_SAMPLE_LIKELY_AT_OOS_EVEN_AT_CENTRAL_ESTIMATE` |
| T3_biweekly | `INSUFFICIENT_SAMPLE_LIKELY_AT_OOS_EVEN_AT_CENTRAL_ESTIMATE` |
| T3_weekly | `INSUFFICIENT_SAMPLE_LIKELY_AT_OOS_UNDER_L1_2X_DISCOUNT` |

## 7. T1 estimate source inquiry (required before authorization)

The 0e3f9d4 plan does NOT cite a source for T1's `50–65 trades/year` estimate. Source classes requested, in order of preference:

1. **PUBLISHED_LITERATURE** — peer-reviewed or vendor-published Connors RSI(2) trade rates on daily-bar liquid futures index instruments. If provided, L1 discount drops to 1.5×.
2. **HAND_COUNT_ON_SEALED_CSV** — operator-side manual count of RSI(2) signals in a representative 1-year slice of the sealed MNQ.c.0 CSV under the proposed entry/exit rules. If provided, L1 discount drops to 1.0× (empirical, not extrapolated).
3. **EXPLICIT_HEURISTIC_ADMISSION** — operator or plan author admits the figure is heuristic. Full L1 2–3× discount applies; conservative scenarios are binding.

Default classification until source provided: `HEURISTIC_ESTIMATE_L1_DISCOUNT_APPLIES`.

## 8. Conservative re-scoring summary

| Track | 0e3f9d4 central score | IS K9 (central) | OOS K9 (central) | IS K9 (2×) | OOS K9 (2×) | IS K9 (3×) | OOS K9 (3×) |
|---|---:|---|---|---|---|---|---|
| T1 RSI(2) bi-dir MNQ | 41/50 | CLEARS_WITH_MARGIN | CLEARS_BORDERLINE | CLEARS_BORDERLINE | **FAILS** | **FAILS** | **FAILS** |
| T2 multi-Donchian basket | 25/50 | CLEARS_WITH_MARGIN | **FAILS** | FAILS | FAILS | FAILS | FAILS |
| T3 vol-target bi-weekly | 35/50 | CLEARS_BORDERLINE | **FAILS** | FAILS | FAILS | FAILS | FAILS |
| T3 vol-target weekly (alt) | N/A | CLEARS_WITH_MARGIN | AT_FLOOR_INDETERMINATE | CLEARS_BORDERLINE | **FAILS** | FAILS | FAILS |

**Bold = FAILS or borderline-with-thin-margin.**

## 9. Does T1 still win after discounting?

**YES in relative terms but FRAGILE in absolute terms.** T1 is the best of T1/T2/T3 but only structurally clears OOS K9 if the 50–65/y estimate is real (not heuristic). Under 2× discount, T1 OOS K9 fails. Under 3× discount, T1 BOTH IS and OOS K9 fail.

## 10. REC1-style disclosure for T1 (if pursued)

If T1 is authored as a candidate without source validation, the following REC1_T1 binding shall be carried byte-equivalent through the new chain (SEAL → P1 → P2 → P3 → P4 → P6 → P11):

> *REC1_T1 (binding): Under L1 epistemic discipline applied to the T1 central estimate (50-65 trades/year heuristic, NOT empirically validated), the 2× conservative discount yields 25-32.5 trades/year and the 3× discount yields 16.7-21.7 trades/year. At the 2× discount, OOS K9 fires; expected OOS verdict is OOS_INSUFFICIENT_SAMPLE or PARKED_SAFE_BUT_OOS_INDETERMINATE. At the 3× discount, IS K9 also fires; expected IS verdict is INSUFFICIENT_SAMPLE analogous to s12-d1. The chain shall NOT relax K9 at any phase. Pursuing T1 without independent validation accepts the structural likelihood of an OOS PARK outcome analogous to s12-d1.*

## 11. Alternative paths (in honest order of preference)

- **ALT_A — Hand-count first.** Operator-side hand-count of RSI(2) signals on a representative slice of the sealed MNQ.c.0 CSV. Lowest cost; highest information value. If hand-count ≥ 50/y, T1 becomes safe.
- **ALT_B — Seek higher-density mechanic.** Search for mechanics that structurally exceed 100 trades/year on a single instrument daily WITHOUT fresh data fetch. Sub-options enumerated in JSON sidecar.
- **ALT_C — T4 universe pivot.** Crypto/Treasury/energy. High data scope friction.
- **ALT_D — HALT trading-track.** Pause for reflection. Eight consecutive Phase-2 candidates have parked; the structural common denominator may warrant framework revisit before another T-style attempt.
- ~~ALT_E — Relax K9 or extend OOS window~~ **FORBIDDEN** by Tier-N invariants.

## 12. Final recommendation

- **Primary:** Do NOT authorize T1 Tier-N spec PLAN until source-validated by hand-count or citation (**ALT_A**).
- **Secondary:** If hand-count not feasible, authorize ALT_B or ALT_D.
- **Tertiary:** If operator chooses to proceed with T1 despite heuristic estimate, authorize T1 Tier-N spec PLAN ONLY with REC1_T1 binding carried byte-equivalent through the chain.

## 13. Posture invariants

- Trading **PAUSED** · Live **BLOCKED_AT_6_GATES** · FRC **NEVER_GRANTED**
- DIAGNOSTIC_ONLY_NOT_LIVE_GRADE permanent
- No profitability / live-readiness / OOS-confirmation / paper-ready / money-proven claims
- K9 not relaxed · REC1 not demoted · No DR redefinition · No threshold loosening

## 14. Hard boundaries held this turn

~50 boundaries asserted in JSON sidecar (`hard_boundaries_held_this_memo_turn`). Highlights: memo-only / no code / no build / no tests / no diagnostics / no signal computation / no backtest / no data fetch / no SEAL-A or SEAL-B chain modified / no lessons.md touched / no tmp/ helpers touched / no T1/T2/T3/T4 authorized / no Tier-N spec authored / no new candidate record id authored / no K9 relaxation / no staging / no commit.

## 15. Next-step authorization (NONE pre-approved by this memo)

Operator must explicitly choose one of:
- `Authorize ALT_A hand-count protocol PLAN-only memo`
- `Authorize ALT_B higher-density mechanic search PLAN-only memo`
- `Authorize ALT_C T4 universe pivot PLAN-only memo`
- `Authorize T1 Tier-N spec PLAN only with REC1_T1 binding carried byte-equivalent`
- `Defer / Pause trading-bot track`
- Some other scope of the operator's choosing.
