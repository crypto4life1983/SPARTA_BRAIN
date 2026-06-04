# Crypto-D1 Momentum N=20 — Deeper Validation Plan (PLAN ONLY)

- **Plan date:** 2026-06-04
- **Official master at plan time:** `6812bebc1505149f4f6d6d453973ed118cc89fef`
- **Task:** `crypto_d1_momentum_n20_deeper_validation_v1`
- **Strategy:** `crypto_d1_momentum_confirmation_v1`
- **Lane:** Crypto-D1 — **WATCH / MIXED**, **NOT_READY_FOR_REAL_DATA** (unchanged)
- **Status:** `PLAN_ONLY_NOT_EXECUTED`

> This is a plan only. It runs no backtest, executes no orchestrator, changes no
> dataset/runner/dashboard/queue, and authorizes no paper, live, broker,
> exchange, order, or fetch action. No ACTIVE/STRONG promotion. No Bundle 23.

---

## 1. Current evidence summary

Source: confirmation run `2a3be425522a04ec`
(`reports/crypto_d1_momentum_confirmation_v1/.../crypto_d1_momentum_confirmation_report.json`).
Registry: stage **EXECUTED**, verdict **WATCH** (classifier ceiling; never
auto-PASS). Per-asset OOS trade floor = 20; per-family floor = 30. OOS window
2024-06-17 .. 2025-12-31 (563 OOS bars/asset).

**N=20 OOS (the candidate):**

| Asset | OOS total return | OOS trades | OOS max DD | Sharpe-like* | Clears 20-trade floor |
|---|---|---|---|---|---|
| BTC | +1.393 | 32 | -0.146 | 2.60 | yes |
| ETH | +1.609 | 31 | -0.329 | 1.89 | yes |
| SOL | +2.442 | 23 | -0.222 | 2.41 | yes |
| **Family** | — | **86 total** | — | — | **meets family floor** |

**N=30 OOS (secondary reference):** BTC +1.343 (27 trades, clears), ETH +2.135
(**19 trades, under floor**), SOL +2.593 (**18 trades, under floor**).
Directionally positive on all three but sample-thin on ETH/SOL.

**Buy-and-hold OOS benchmark:** BTC +0.316, ETH **-0.155**, SOL **-0.131**,
equal-weight allocate-once basket **-0.0226**.

**Headline:** N=20 is positive OOS on all three assets, beats same-asset
buy-and-hold OOS on all three, and is the only lookback clearing the per-asset
20-trade floor on all three. This is the best-sampled, most floor-robust
candidate — but **WATCH-ceiling evidence only**, not a trading authorization.

*Sharpe-like = rf=0 daily-return approximation, NOT a true Sharpe; OOS sample is
small.

**Known caveats:** single OOS period (no yearly/monthly split yet); taker costs
with no stress view yet; SOL clears the floor by only 3 trades; BTC has one
flagged true missing day (2024-03-31, never forward-filled).

---

## 2. Why N=20 is the focus

- **Only lookback floor-robust on all three assets** (BTC 32 / ETH 31 / SOL 23).
  N=30 misses the floor on ETH (19) and SOL (18), so its OOS verdict rests on a
  thinner sample.
- **Positive OOS and beats buy-and-hold OOS on every asset**, while two of three
  buy-and-hold legs (ETH, SOL) are negative OOS.
- **Pre-registered, not freshly searched** — N=20 and N=30 came from the
  `momentum_robustness_v1` memo, so deeper validation of N=20 is confirmation of
  a pre-declared candidate, not a new parameter hunt that would invite
  overfitting.
- **Honest narrowing:** validating the single best-sampled candidate is safer
  than widening the lookback grid, which re-opens multiple-comparison risk. N=30
  stays a reference, not the deep-validation focus, until its OOS sample clears
  the floor under a separately approved design.

---

## 3. What must remain frozen

- **Dataset:** `data/crypto_d1_research/CRYPTO_D1_SPOT_BTC_ETH_SOL_V001/V002`
  (`CRYPTO_D1_SPOT_BTC_ETH_SOL_V001_V002`). V002 `CHECKSUMS.txt` must still pass;
  no new rows, no re-fetch, no synthetic data. BTC 2024-03-31 stays a flagged
  true gap.
- **Split:** IS 2021-06-17 .. 2024-06-16; OOS 2024-06-17 .. 2025-12-31; explicit
  UTC date windows. No re-splitting, no rolling re-optimization, no OOS peeking
  to tune N.
- **Cost assumptions:** 40 fee + 10 slippage + 10 spread = 60 bps/side, 120 bps
  round-trip, taker on every leg, from frozen V002 `fees.json`. The baseline is
  unchanged; cost **stress** is an additive labeled sensitivity (test 5), never a
  redefinition.
- **Safety flags:** research_only=true; data_fetch / exchange_connection /
  live_trading / broker_control / paper_order_execution / order_placement /
  dataset_mutation / active_strong / bundle_23 / execution_authorized all
  **false**.
- **No paper / no live:** offline stdlib backtest-analysis only, behind the
  Step-3 safety contract and the human-approval gates.
- Conservative `classify_run` unchanged — WATCH ceiling, never auto-PASS.

---

## 4. Validation tests to run later

*(What a future, separately-approved execution step would compute. None run here.)*

1. **Yearly OOS breakdown** — split the OOS window into per-year sub-returns per
   asset; is the edge one-year-driven or persistent? (read-only slice; no
   re-split).
2. **Monthly return / drawdown profile** — per-asset monthly OOS returns +
   rolling max-drawdown; worst month, longest drawdown, recovery (descriptive).
3. **Per-asset consistency BTC/ETH/SOL** — side-by-side N=20 OOS table (sign,
   floor clearance, drawdown, turnover); flag any single asset carrying the
   basket.
4. **Trade count & turnover** — re-confirm OOS counts (32/31/23), turnover, floor
   clearance, family total (86).
5. **Fee / slippage stress** — re-price the SAME N=20 OOS ledger at 150/180/240
   bps as an additive column; report each asset's breakeven cost. Baseline 120
   bps stays the headline.
6. **Outlier sensitivity** — recompute excluding best/worst (and small top-k) OOS
   trades per asset, especially SOL; is the edge outlier-dependent? (unmodified
   result stays official).
7. **Regime sensitivity** — bucket OOS bars by a pre-declared trend/vol proxy
   computed only from frozen V002 data; check the edge is not confined to one
   regime (no external data, no look-ahead).
8. **Basket vs per-asset behavior** — allocate-once equal-weight basket OOS
   (-0.0226) vs per-asset N=20; how much edge survives equal-weight basketing
   without rebalance? (construction unchanged).
9. **Robustness to small parameter changes around N=20** — *optional, only if
   explicitly authorized:* probe N in {18, 20, 22} as a stability neighborhood
   (NOT a re-optimization; winner is not re-selected). Skipped if not authorized.

---

## 5. Exact future files an execution step would create

*(None created by this plan.)*

- `reports/crypto_d1_momentum_n20_deeper_validation_v1/CRYPTO_D1_SPOT_BTC_ETH_SOL_V001_V002/crypto_d1_momentum_n20_deeper_validation_report.json`
- `reports/crypto_d1_momentum_n20_deeper_validation_v1/CRYPTO_D1_SPOT_BTC_ETH_SOL_V001_V002/crypto_d1_momentum_n20_deeper_validation_report.md`

Code that would change **only if additive and separately approved:**
`tools/crypto_d1_backtest_runner.py` (additive deeper-validation reporting mode
only — must not alter default / v002_addendum / momentum_robustness_v1 /
momentum_confirmation_v1 behavior), with additive tests in
`tests/test_crypto_d1_backtest_runner.py`.

**Must not change:** V002 dataset + CHECKSUMS, QA freeze reports, operator
acceptance memo, IS/OOS addendum, readiness gate, dashboards, brain_memory, and
all existing baseline/robustness/confirmation result files.

---

## 6. Runner / mode used later

- **Runner:** `tools/crypto_d1_backtest_runner.py`
- **Proposed config mode:** `momentum_n20_deeper_validation_v1` (additive, mirrors
  how `momentum_confirmation_v1` was added).
- **Lookback under deep analysis:** 20 (reference: 30).
- **Reuses** the same V002 cost loader, date-window splitter, missing-day
  detector, and conservative `classify_run`.
- Runner / dataset / mode / market all match the **Step-3 safety-contract
  allowlists**. No runner change is made by this plan.

---

## 7. Pass / Watch / Fail criteria

- **Ceiling:** WATCH is the maximum any deeper-validation pass can emit;
  `classify_run` never auto-PASSes.
- **CONFIRMED-WATCH (continue branch):** N=20 stays positive OOS on >=2/3 assets
  across the yearly/monthly breakdown, clears the per-asset 20-trade floor,
  survives fee/slippage stress at >=150 bps on a majority of assets, and is not
  outlier- or single-regime-dependent.
- **WATCH / MIXED (hold):** edge positive but fragile — floor cleared only
  intermittently across sub-periods, survives only at baseline cost, or one asset
  carries the basket.
- **FAIL (park momentum):** N=20 turns negative OOS on a majority of assets in the
  breakdown, fails to beat buy-and-hold OOS after stress, or collapses once a
  single outlier or single regime is removed.
- **No promotion:** nothing here can promote to ACTIVE/STRONG or authorize
  paper/live.

---

## 8. Safety gates

research_only=true; data_fetch / exchange_connection / live_trading /
broker_control / paper_order_execution / order_placement / dataset_mutation /
active_strong / bundle_23 / execution_authorized all **false**; no new data.
Human approval required for execution, for paper/live, and for ACTIVE/STRONG
promotion. Lane stays **WATCH / MIXED**; readiness stays
**NOT_READY_FOR_REAL_DATA**.

---

## 9. How this updates registry / queue / orchestrator later

- **Registry:** a future approved execution would add a deeper-validation result
  for `crypto_d1_momentum_confirmation_v1`, keeping stage EXECUTED and verdict
  clamped at WATCH. This plan adds only a PLAN_ONLY artifact and changes no
  verdict.
- **Queue:** `configs/research_queue.json` task
  `crypto_d1_momentum_n20_deeper_validation_v1` moves from `NEEDS_PLAN` toward
  approved-for-research **only via a separate operator edit** once this plan is
  approved. This plan does not modify the queue.
- **Orchestrator:** on its next read the Step-4 dry-run orchestrator would see the
  plan exists and surface the task as plan-backed; `executable` stays pinned
  false and `would_run_command` stays null. No orchestrator code changes.
- **Ordering (each arrow a human gate):** this plan -> operator approval -> queue
  flag edit -> separately-approved additive runner mode -> execution run ->
  registry deeper-validation result -> operator PASS/WATCH/FAIL review.

---

## 10. Non-authorization statement

This document is a **PLAN ONLY**. It runs no backtest, executes no orchestrator,
creates no result files, changes no dataset, QA file, runner logic, queue config,
or dashboard, and authorizes no paper, live, broker, exchange, order, or fetch
action. It does not promote any lane to ACTIVE or STRONG and does not start
Bundle 23. Crypto-D1 remains **WATCH / MIXED** and **NOT_READY_FOR_REAL_DATA**. A
positive backtest result is not trading authorization. Implementation and
execution require separate explicit operator approval.
