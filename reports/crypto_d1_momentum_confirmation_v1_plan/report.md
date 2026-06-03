# Crypto-D1 Momentum Confirmation v1 — Runner / Report PLAN (PLAN ONLY)

- **Plan date:** 2026-06-03
- **Official master at plan time:** `49d9f1b1ce082966de420c55077850af80b023f8`
- **Status:** `PLAN_ONLY_NOT_EXECUTED`
- **Lane (unchanged):** Crypto-D1 = **WATCH / MIXED**, `readiness_status` = **NOT_READY_FOR_REAL_DATA**
- **This document authorizes nothing.** No backtest, no dataset change, no runner-logic change, no QA change, no dashboard change, no promotion, no paper/live. See the non-authorization statement at the end.

---

## 1. Why this is the correct next step

The `momentum_robustness_v1` sweep (run_id `458a1e7764fff90d`, status **WATCH**)
established that momentum is **positive out-of-sample on every lookback**
(N = 20, 30, 45, 60, 90) across **all three assets** (BTC / ETH / SOL), and
beat per-asset buy-and-hold OOS everywhere. But two facts make a *focused
confirmation* — not a wider search — the honest next move:

1. **Reliability lives at the short end.** OOS magnitude decays monotonically as
   the lookback lengthens, and the per-asset 20-trade OOS floor is only cleared
   by **N=20** on all three assets; **N=30** clears it on BTC only (ETH 19,
   SOL 18 — just under). Longer lookbacks are thin-sample. Widening the grid now
   would invite overfitting; narrowing to the best-sampled lookbacks is the
   conservative move.
2. **A reporting defect blocks a clean read.** The allocate-once equal-weight
   basket currently reports `OOS_ret = None` (single equity stream, no per-basket
   IS/OOS split), so it cannot yet be compared against per-asset OOS strategy
   returns. This must be fixed/clarified before drawing benchmark conclusions.

Confirmation v1 therefore re-runs **only N=20 and N=30** on the *same frozen
setup*, fixes the basket OOS reporting, and asks a single, pre-registered
question.

---

## 2. Exact hypothesis being tested

- **H1 (primary):** On the frozen V002 dataset, with the unchanged IS/OOS split
  and the 120 bps round-trip cost model, time-series momentum at **N=20 and
  N=30** produces a **positive, floor-clearing OOS edge** that beats both
  same-asset buy-and-hold OOS and the allocate-once equal-weight basket OOS.
- **H0 (null):** Once costs and the per-asset 20-trade floor are applied, the
  N=20/N=30 OOS edge is not distinguishable from the buy-and-hold benchmarks.
- **Decision relevance:** confirmation keeps Crypto-D1 primary for a deeper
  branch; non-confirmation parks momentum and re-opens lane direction. **Neither
  outcome authorizes trading.**

No new lookbacks are searched — N=20 and N=30 are **pre-registered** from the
robustness memo.

---

## 3. Exact runner / reporting design

**Approach:** an **additive** new config mode, mirroring how
`momentum_robustness_v1` was added. It does **not** modify `default`,
`v002_addendum`, or `momentum_robustness_v1` behavior.

- **Proposed config name:** `momentum_confirmation_v1`
- **Lookback constant:** `MOMENTUM_CONFIRMATION_LOOKBACKS = (20, 30)`
- **Family plan:** per-asset `buy_and_hold` benchmark + `momentum_continuation`
  families `momentum_20`, `momentum_30` only. Volatility-regime gate and mean
  reversion remain **DEFERRED**.
- **Basket:** reuse the existing allocate-once
  `_basket_buy_and_hold_equal_weight` (construction unchanged) and add an OOS
  basket figure (see §6).
- **Reuses unchanged:** the V002 cost loader, the explicit date-window splitter,
  the missing-day detector, and the conservative `classify_run` (WATCH ceiling).
- **Output basename:** `crypto_d1_momentum_confirmation_report`
- **Distinct output dir:**
  `reports/crypto_d1_momentum_confirmation_v1/CRYPTO_D1_SPOT_BTC_ETH_SOL_V001_V002/`
  — never overwrites the baseline or robustness reports.

---

## 4. Exact files a FUTURE execution step would create or change

*(NONE are created or changed by this plan. Listed so the future step is fully
scoped in advance.)*

**Code changed (additive):**
- `tools/crypto_d1_backtest_runner.py` — add `MOMENTUM_CONFIRMATION_LOOKBACKS`,
  `_momentum_confirmation_family_plan()`, a basket-OOS reporting helper, an
  `is_confirmation` flag wired into the existing `uses_date_window_protocol`
  path, a `momentum_confirmation_v1_mode` show-plan block, and the CLI
  `--config` choice.

**Tests changed (additive):**
- `tests/test_crypto_d1_backtest_runner.py` — confirmation config exists; only
  N=20/N=30 run; `v002_addendum` and `momentum_robustness_v1` modes remain
  unchanged; basket OOS figure present and correctly labelled; safety flags
  locked; no network/broker/paper/live paths.

**Result files created by the run (only when executed, separately approved):**
- `…/crypto_d1_momentum_confirmation_v1/…_V002/crypto_d1_momentum_confirmation_report.json`
- `…/crypto_d1_momentum_confirmation_v1/…_V002/crypto_d1_momentum_confirmation_report.md`

**Must NOT change:** V002 dataset files, QA reports, operator acceptance memo,
IS/OOS addendum, readiness gate / checklist, dashboards, brain_memory, and the
existing baseline + robustness result files.

---

## 5. How N=20 and N=30 will be compared

For each asset (BTC / ETH / SOL) and each lookback, the report tabulates:

| Field | Purpose |
|---|---|
| IS total_return | regime context |
| OOS total_return | the headline edge |
| OOS trade_count | sample size vs. the 20-trade floor |
| OOS max_drawdown | risk |
| OOS sharpe_like (with caveat) | risk-adjusted shape |
| clears_20_trade_floor (bool) | reliability gate |
| IS→OOS shrinkage ratio | expected decay vs. suspicious collapse |

**Comparison rules (pre-registered):**
- Each strategy OOS return is compared to **(a)** the same-asset buy-and-hold
  OOS return and **(b)** the allocate-once equal-weight basket OOS return.
- N=20 and N=30 must **agree in sign/direction** per asset.
- **Confirmation** requires both lookbacks positive OOS on **≥2 of 3 assets**,
  clearing the per-asset floor where the claim is made, and beating same-asset
  buy-and-hold OOS.
- **No parameter tuning** occurs; the two lookbacks are fixed in advance.

---

## 6. How basket OOS reporting will be fixed / clarified

- **Current defect:** `buy_and_hold_basket_equal_weight` is a single equity
  stream with `is_metrics = None` and `oos_metrics = None`, so `OOS_ret` renders
  as `None` and the basket is not comparable to per-asset OOS strategy figures.
- **Fix options (decided at implementation):**
  - **Option A (preferred):** split the allocate-once basket equity curve by the
    same explicit OOS date window and report a basket OOS `total_return` /
    `max_drawdown` computed from the OOS sub-curve (entry value = basket equity
    at the first OOS date), as a **benchmark-only** figure.
  - **Option B:** keep `oos_metrics = None` but add an explicit
    `basket_oos_reporting = "single_stream_no_split"` field so `None` is never
    misread as zero.
- **Constraint:** the allocate-once (no daily rebalance) construction is
  **kept** — this is a reporting clarification, not a benchmark redefinition.
- **Optional future:** a monthly-rebalanced basket variant **may** be added
  later as an additive third benchmark; it is **not** part of confirmation v1.

---

## 7. What must remain unchanged from the prior Crypto-D1 setup

- **Dataset:** `…/CRYPTO_D1_SPOT_BTC_ETH_SOL_V001/V002` (no re-freeze; V002
  `CHECKSUMS.txt` must still pass).
- **IS/OOS split:** IS `2021-06-17 → 2024-06-16`, OOS `2024-06-17 → 2025-12-31`,
  explicit UTC date windows.
- **Cost model:** fee 40 bps + slippage 10 bps + spread proxy 10 bps =
  60 bps/side, **120 bps round-trip** (from the frozen V002 `fees.json`).
- **Floors:** per-asset OOS floor = 20 trades; per-family floor = 30 (reported,
  not enforced in `classify_run`).
- **Classifier:** conservative `classify_run` unchanged (WATCH ceiling, never
  auto-PASS).
- **BTC 2024-03-31:** remains a true gap — flagged, never forward-filled.
- **Deferred strategies:** volatility-regime gate and mean reversion stay
  deferred.

---

## 8. Pass / Watch / Fail criteria

- **Ceiling:** **WATCH** is the maximum verdict this pass can emit;
  `classify_run` is unchanged and never auto-PASSes.
- **CONFIRMED-WATCH (continue momentum branch):** both N=20 and N=30 positive
  OOS on ≥2 of 3 assets, clearing the per-asset floor where claimed, and beating
  same-asset buy-and-hold OOS.
- **WATCH / MIXED (no deeper branch yet):** positive but floor-clearing only
  intermittently (e.g. N=30 on BTC only, as in the robustness run).
- **FAIL (park momentum, re-open lane):** either lookback negative OOS on a
  majority of assets, or failing to beat buy-and-hold OOS after costs.
- **No promotion:** no criterion here can promote to ACTIVE/STRONG or authorize
  paper/live; those require separate gates and real-data readiness.

---

## 9. Safety gates

All pinned for the future execution step and unchanged by this plan:

`research_only = True`; `data_fetch_enabled = False`;
`exchange_connection_enabled = False`; `live_trading_enabled = False`;
`broker_control_enabled = False`; `paper_order_execution_enabled = False`;
`order_placement_enabled = False`; **no new data**; lane remains **WATCH /
MIXED**; readiness remains **NOT_READY_FOR_REAL_DATA**; **Bundle 23 not
started**.

---

## 10. Non-authorization statement

This document is a **PLAN ONLY**. It runs no backtest, creates no result files,
changes no dataset, QA file, runner logic, or dashboard, and authorizes no
paper, live, broker, or exchange action. It does not promote any lane to ACTIVE
or STRONG. Crypto-D1 remains **WATCH / MIXED** and **NOT_READY_FOR_REAL_DATA**.
A positive backtest result is **not** trading authorization. Implementation and
execution require **separate explicit operator approval**.
