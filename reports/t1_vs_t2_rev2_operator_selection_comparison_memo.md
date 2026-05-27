# T1-vs-T2 rev2 Operator Selection Comparison Memo

**Memo ID:** `T1_VS_T2_OPERATOR_SELECTION_COMPARISON_V1`
**Schema:** `sparta.next_research_track.t1_vs_t2_operator_selection_comparison.v1`
**Phase:** `T1_VS_T2_OPERATOR_SELECTION_COMPARISON`
**Lifecycle state:** `T1_VS_T2_OPERATOR_SELECTION_COMPARISON_MEMO_SEALED`
**Authored at (UTC):** `2026-05-27T21:50:00.000000+00:00`
**Sealed JSON:** `reports/t1_vs_t2_rev2_operator_selection_comparison_memo.json`
**Report seal sha-256:** `9d8d6a80c0302f5a9d08a530021e3498d1946b813e1040a0e0b62a7fe81d511b`

**OPERATOR-ADVISORY ONLY.** Does NOT ratify T1, T2, or co-primary. Does NOT
modify any prior commit. Does NOT compute correlations, A7, or signals.
Does NOT fetch data. 5376de7 remains `PROVISIONAL_NOT_FULLY_RATIFIED`
regardless of this memo's recommendation.

## Parent references

| Anchor | Commit | Sha (prefix) |
|---|---|---|
| DR10 v2 SEAL | `78cd22e` | report_seal: `7794bb52…` |
| DR10 v2 governance supplement | `fdf9d6e` | report_seal: `953ad6f3…` |
| Master reconciliation memo | `1e51680` | report_seal: `e2714c8e…` |
| Rev2 next-track plan | `ee2bfc1` | md: `11dffb7b…` |
| Rev2 governance supplement | `7d7bb52` | report_seal: `eba24331…` |
| S14-D1 T1 rev2 PLAN (PROVISIONAL) | `5376de7` | md: `be53ca7e…` |
| S13-D1 P7 decision memo | `cc1817b` | file: `ec5addcc…` |
| S13-D1 SEAL | `262491c` | report_seal: `2f9d1763…` |

## 1. Provisional status of 5376de7 (preserved)

Per supplement 7d7bb52 §6: `PROVISIONAL_NOT_FULLY_RATIFIED`. Rollback not
authorized. Treated as structurally legitimate PLAN-only artifact, NOT as
operator-side ratified selection. **This memo preserves 5376de7 byte-stable
and does not ratify it.**

## 2. T1 rev2 advantages

- **Futures continuity:** reuses sealed MNQ.c.0 CSV (anchor `8b7b832c…23e`)
  for 1 of 4 instruments
- **Existing MNQ lineage:** s13-d1 P3 BUILD + P6 IS already characterized
  RSI(2) on MNQ (159 trades / 4.63y; expectancy $540.73)
- **Multi-instrument RSI(2):** ~136 trades/y portfolio per linear
  extrapolation (4 × 34/y per instrument)
- **K9 potential:** even with conservative A7=1.5-2 adjustment, effective
  trade count is 51-68/y portfolio — still clears K9 OOS floor (≥50/y) at
  high end
- **DR10 v2 clean at DA4=C $200k:** at DA4=C cost_drag is ~2.35% (s13-d1
  observed) — comfortably below 5%

## 3. T1 rev2 risks

- **High correlation** across MNQ/MES/MYM/M2K (all US equity-index micros;
  pairwise corr typically >0.90-0.95 normal, →1.0 in stress)
- **Effective independent bets likely far below 4** (structurally expected
  1.5-2.0 via A7 eigenvalue decomposition); rev2 plan's 4×34=136/y assumes
  A7=4 implicitly
- **K9 margin may be overestimated:** rev2 plan §5.1's 9/10 score is
  conditional on A7=4; honest score after A7 adjustment is 6-7/10
- **S2 cost_drag ~4.7% near 5% threshold** at DA4=B $100k; 0.3pp estimation
  error flips DR10 v2 verdict from CLEARS to REJECT_FAST —
  calibration-fragility on the load-bearing branch
- **Requires actual MES/MYM/M2K cost precommit at SEAL** (per 7d7bb52 §9):
  per-contract commission from broker fee schedule + half-bid-ask slippage
  measured from sealed CSV bar data — not extrapolated from MNQ
- **Concentration risk explicit:** s7-D1 USO concentration lesson directly
  applies to 4-correlated-equity-index-micros basket
- **Ratifying T1 post-facto-ratifies 5376de7's autonomous implicit
  selection,** weakening `GOV-RULE-CO-PRIMARY-OPERATOR-SELECTION-PHRASE-V1`
  before it has any track record

## 4. T2 rev2 advantages

- **Cleaner DR10 v2 cost_drag margin:** per-share commissions ~$0.005/share
  vs $200/share notional → ~0.0025% commission as fraction; total S2
  cost_drag (commission + half-bid-ask + exchange fees + SEC fees + FINRA
  TAF) typically 0.3-0.5% — **far below 5% threshold**
- **Load-bearing branch no longer fragile:** AND-conjunction cost_drag
  branch never fires at this margin; even 1-2pp calibration error doesn't
  flip verdict
- **Lower transaction cost** as fraction of notional vs micro-futures
- **No contract-quantization problem:** cash equities allow share-level
  granularity (1 share = $200 for AAPL) vs micro-futures' contract minimum
  (1 MNQ = $30k notional)
- **True universe diversification:** cash-equity single-name basket is
  truly orthogonal to ALL prior parked candidates (s7-D1/s9/s10-D1/s10-D2
  ETF or futures; s11/s12/s13 single MNQ); brings NEW asset class to the
  diagnostic series for the first time
- **RSI(3) slower than RSI(2)** reduces signal density, produces more
  selective entries
- **Demonstrates governance rule has teeth:** choosing T2 over T1
  establishes precedent that autonomous-PLAN-progression doesn't constrain
  operator selection

## 5. T2 rev2 risks

- **Fresh data scope:** requires daily OHLCV fetch for 3-name basket;
  source TBD (Databento equities / yfinance / Polygon / Alpaca / IEX); each
  requires its own DR9-equivalent audit
- **Different cost model:** equity cost surface structurally different from
  futures; new cost calibration at SEAL; C1-C8 contracts need minor
  adaptation
- **Equity-specific corporate action handling (C5):** splits, dividends,
  mergers, spin-offs, special dividends — C5 contract needs explicit
  authoring/extension for equities; non-trivial framework work
- **Possible overfit to mega-cap tech:** AAPL/MSFT/NVDA placeholder
  carries survivorship bias risk; 2019-2025 mega-cap tech outperformed;
  RSI mean-reversion edge may not generalize to other sectors or future
  regimes. Operator must precommit universe-selection rationale at SEAL
- **First-principles burden vs s9:** s9 was 4-ETF RSI(2) bi-directional;
  T2 must argue why 3-name single-name basket with RSI(3) is a DIFFERENT
  test (defensible: different universe + different mechanic period; but
  requires careful framing)
- **Discards 5376de7 work implicitly:** structurally legitimate T1 PLAN
  remains in repo as PROVISIONAL but is not advanced

## 6. Decision matrix

Honest scoring (incorporating 7d7bb52 supplement caveats):

| Dimension | T1 score | T2 score | Notes |
|---|---:|---:|---|
| K9 reachability | 6 | 8 | T1 after A7=1.5-2 adjustment; T2 single-name vs basket |
| DR10 v2 reachability | 6 | 9 | T1 borderline 4.7%@DA4=B; T2 <<5% structurally |
| Data friction | 4 | 3 | T1 reuses 1 CSV; T2 fresh OHLCV for 3 names |
| Operational meaningfulness | 6 | 8 | T2 expands diagnostic series to new asset class |
| Framework integrity | 4 | 9 | T1 weakens new gov-rule; T2 demonstrates it |
| Expected diagnostic value | 6 | 8 | T2's cross-asset evidence is broader |
| **TOTAL (out of 60)** | **32** | **45** | T2 wins 5 of 6 dimensions |

This memo's scoring differs from rev2 plan §6 (which had T1=T2=43/60)
because it honestly incorporates the 7d7bb52 supplement caveats: T1 K9
adjusted for A7=1.5-2 (not assumed 4); T1 DR10 v2 scored at DA4=B (not
DA4=C clean); framework integrity added as new dimension reflecting
`GOV-RULE-CO-PRIMARY-OPERATOR-SELECTION-PHRASE-V1`.

## 7. Recommendation: **RATIFY_T2_PRIMARY**

T2 = 45/60 vs T1 = 32/60. T2 wins on **5 of 6** dimensions
(loses only data friction by 1 point). T2 has:

- the operationally most robust DR10 v2 cost_drag margin (the load-bearing
  branch under the new framework)
- demonstrates the new governance rule actually binds operator selection
- expands the diagnostic series to a new asset class (cash equity) for the
  first time
- preserves 5376de7 byte-stable as PROVISIONAL_NOT_FULLY_RATIFIED

### Why not the alternatives

- **RATIFY_T1_PRIMARY:** honest A7 adjustment reduces K9 OOS from "strong
  margin" to "borderline"; DR10 v2 calibration-fragile at DA4=B (0.3pp
  flips verdict); post-facto-ratifies 5376de7's autonomous implicit
  selection (weakens new gov-rule); data-friction advantage modest
- **RATIFY_T1_AND_T2_CO_PRIMARY:** doubles operator workload + data fetch
  + race surface area; co-primary is exactly what the new gov-rule was
  trying to gate; if T2 hits a wall, T1 can be re-evaluated sequentially
  (strictly safer than parallel under current autonomous-progression race
  environment)
- **HALT_OR_DEFER:** contradicts operator's just-recorded Reading A intent
  ("retail-scale tradable strategy discovery with fail-closed discipline"
  per fdf9d6e); 6 live-block gates already provide safety floor; halting
  adds no marginal safety vs ratifying T2 PLAN-only

### Suggested next operator authorization (per rev2 plan §10 second primary scope)

```
Authorize s14-d1 cash-equity 3-name basket RSI(3) bi-directional Tier-N
spec PLAN only — bound by DR10 v2.
```

### Treatment of 5376de7 under recommended option

5376de7 remains in repo as PROVISIONAL_NOT_FULLY_RATIFIED PLAN-only artifact
per 7d7bb52 §6. No rollback. No modification. If T2 ratification proceeds
and later hits a wall, operator may re-evaluate T1 in a future selection
turn; 5376de7's PLAN remains available for re-evaluation.

### This memo does NOT itself ratify anything

Per `GOV-RULE-CO-PRIMARY-OPERATOR-SELECTION-PHRASE-V1` (from 7d7bb52),
operator must type the explicit ratification phrase to actually ratify any
track. This memo is operator-advisory only.

## 8. Posture invariants

- Trading: **PAUSED**
- Live: **BLOCKED_AT_6_GATES**
- FRC: **NEVER_GRANTED**
- Research grade: **DIAGNOSTIC_ONLY_NOT_LIVE_GRADE**
- K9 inviolacy: PRESERVED (≥100 trades; OOS ≥50/y binding)
- K9-reachability + DR10-reachability disciplines: **BINDING**
- DR10 v1 binding for existing candidates · DR10 v2 binds future s14+
- s13-d1 REJECT_FAST: **TERMINAL under DR10 v1**
- All existing sealed candidates + framework artifacts + governance
  supplements: **BYTE-STABLE**
- 5376de7 S14-D1 T1 rev2 PLAN: **BYTE-STABLE and PROVISIONAL**
- `GOV-RULE-CO-PRIMARY-OPERATOR-SELECTION-PHRASE-V1`: **BINDING** (from 7d7bb52)
- `GOV-RULE-FRAMEWORK-REVISION-OPERATOR-PHRASE-V1`: **BINDING** (from fdf9d6e)
- Profitability claim: NONE · Live-readiness claim: NONE · OOS-confirmation
  claim: NONE
- Advisory only · Operator-typed authorization required for any action

## Seal

```
report_seal_sha256: 9d8d6a80c0302f5a9d08a530021e3498d1946b813e1040a0e0b62a7fe81d511b
seal_method:        LESSON_HUNTER_004 canonical roundtrip
```
