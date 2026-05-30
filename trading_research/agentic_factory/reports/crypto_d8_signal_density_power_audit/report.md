# Crypto-D8 — Signal-Density / Statistical-Power Audit (BTC/ETH/SOL spot, 2020–2023 IS)

**This is a READ-ONLY SIGNAL-DENSITY / STATISTICAL-POWER AUDIT only.** It **counts
candidate entry events** on the frozen IS data. There is **NO trade simulation, NO PnL,
NO backtest, NO optimization, NO parameter sweep, NO entry/exit modeling, NO old-strategy
rerun, NO network, NO data fetch, NO exchange API, NO broker, NO paper, NO live.** No OOS
and **no 2024/2025/2026 row** is read. Frozen data read **read-only**, not modified.
S30/futures untouched; JARVIS/`templates/base.html`/hydra untouched. **Not staged, not
committed.**

- **Created:** 2026-05-30
- **HEAD at audit:** `344a7e7` (Crypto-D7 closeout) or descendant — factory tree clean,
  nothing staged.

---

## 1. Crypto-D7 closeout reference

Crypto-D7 (`344a7e7`) closed out **CODR-1 v1 = PARKED after IS_FAIL** (Crypto-D6 `27b0620`)
and recommended **NO_STRATEGY_SELECTED_NEED_MORE_RESEARCH**, explicitly proposing this D8
**read-only signal-density / power audit** before any next hypothesis is frozen. D7's core
open question: *can daily spot ever yield ≥30 BTC IS events for an event-driven mechanism
with a friction-survivable, top-3-robust edge — or is a more frequent timeframe (4H) the
real prerequisite?* D8 answers the **counting half** of that question only.

## 2. Frozen data reference

Immutable, SHA256-pinned, 2026-sealed **BTC/ETH/SOL spot daily USDT** snapshot at
`data_crypto/spot_binance_usdt_1d_2020_2025/` (D3b `5b3d94c`, ratified D3c `fe5594f`).
Read **read-only**; not modified. CODR-1's failure was a strategy failure, not a data
failure — this snapshot stays valid for the next separately-authorized hypothesis.

## 3. IS-only confirmation

| Symbol | IS window | IS rows (≤2023) | rows>2023 read |
|---|---|---|---|
| BTC | 2020-01-01 .. 2023-12-31 | 1461 | **0** |
| ETH | 2020-01-01 .. 2023-12-31 | 1461 | **0** |
| SOL | 2020-08-11 .. 2023-12-31 (partial) | 1238 | **0** |

Only year ≤ 2023 bars entered the audit. **No 2024/2025/2026 bar was read.** SOL is a
partial IS (starts 2020-08-11), reported separately, never padded or stitched.

## 4. Event family count tables (counts only — no PnL)

Counts are candidate-event frequencies on the IS slice. `p100` = events per 100 IS days.
`maxYr` = largest single-year share of that symbol's events (concentration proxy).

### Family 1 — daily crash / liquidation candle (`ret_1d ≤ thr`)

| Threshold | BTC (by year) | BTC p100 / maxYr | ETH | SOL |
|---|---|---|---|---|
| ≤ −5% | **81** (16/35/24/6) | 5.54 / 0.43 | 123 | 192 |
| ≤ −7% | **33** (6/14/12/1) | 2.26 / 0.42 | 65 | 119 |
| ≤ −10% | 12 (2/5/5/0) | 0.82 / 0.42 | 27 | 50 |

### Family 2 — multi-day liquidation

| Threshold | BTC (by year) | BTC p100 / maxYr | ETH | SOL |
|---|---|---|---|---|
| 2d ≤ −10% | **30** (8/13/9/0) | 2.05 / 0.43 | 57 | 105 |
| 3d ≤ −15% | 14 (3/4/7/0) | 0.96 / 0.50 | 35 | 55 |

### Family 3 — volatility compression (10d range/close ≤ thr) [+ next-day expansion subset]

| Threshold | BTC (by year) | BTC p100 / maxYr | BTC next-day-exp | ETH | SOL |
|---|---|---|---|---|---|
| ≤ 8% | 196 (44/1/26/125) | 13.42 / 0.64 | 9 | 91 | 1 |
| ≤ 12% | **609** (145/56/149/259) | 41.68 / 0.43 | 22 | 345 | 46 |
| ≤ 16% | **851** (210/125/213/303) | 58.25 / 0.36 | 26 | 598 | 135 |

### Family 4 — trend continuation (`close>SMA200` & `ret_1d ≥ thr`)

| Threshold | BTC (by year) | BTC p100 / maxYr | ETH | SOL |
|---|---|---|---|---|
| ≥ +5% | **52** (9/29/**0**/14) | 3.56 / 0.56 | 99 | 109 |
| ≥ +7% | **30** (6/18/**0**/6) | 2.05 / 0.60 | 57 | 78 |

### Family 5 — mean-reversion in uptrend (`close>SMA200` & `ret_1d ≤ thr`) — the CODR-1 family

| Threshold | BTC (by year) | BTC p100 / maxYr | ETH | SOL |
|---|---|---|---|---|
| ≤ −5% | **30** (3/22/**0**/5) | 2.05 / 0.73 | 67 | 67 |
| ≤ −7% (CODR-1 trigger) | **9** (2/7/**0**/0) | 0.62 / 0.78 | 33 | 39 |
| ≤ −10% | 4 (1/3/0/0) | 0.27 / 0.75 | 13 | 11 |

> **BTC −7% in-uptrend = 9 events — exactly the CODR-1 D6 trade-pool driver.** This is the
> smoking gun: the `close>SMA200` gate (zero 2022 events) is what starved CODR-1.

### Family 6 — cross-asset leadership (aligned 1237 IS days)

| Signal | Count (by year) | per-100 aligned | maxYr |
|---|---|---|---|
| BTC up-lead ≥+5% (ETH,SOL <+5%) | 22 (5/11/2/4) | 1.78 | 0.50 |
| BTC down-lead ≤−5% (ETH,SOL >−5%) | **4** (0/3/1/0) | 0.32 | 0.75 |

### Family 7 — calendar / weekday sample counts

BTC/ETH: each weekday ≈ 208–209 bars, weekend 418, weekday 1043, total 1461. SOL: each
weekday ≈ 176–177, weekend 354, weekday 884, total 1238. **Near-perfectly uniform** (24/7
market) — no structural day-of-week sample skew.

## 5. Power verdicts

Criteria: BTC ≥30 IS events **and** not one-year-concentrated (maxYr <0.60) → **POWER_OK**;
BTC 15–29 → **POWER_LOW**; BTC <15 → **POWER_TOO_LOW**; BTC <15 but concept plausible →
**NEEDS_4H_DATA**.

| Family (representative threshold) | BTC count | BTC maxYr | Verdict |
|---|---|---|---|
| **daily_crash_candle [−5%]** | **81** | 0.43 | **POWER_OK** ✅ |
| daily_crash_candle [−7%] | 33 | 0.42 | **POWER_OK** ✅ |
| daily_crash_candle [−10%] | 12 | 0.42 | NEEDS_4H_DATA |
| multiday_liquidation [2d −10%] | 30 | 0.43 | POWER_OK (borderline) |
| multiday_liquidation [3d −15%] | 14 | 0.50 | NEEDS_4H_DATA |
| vol_compression [12%] | 609 | 0.43 | POWER_OK* (parameter-freedom) |
| trend_continuation [+5%] | 52 | 0.56 | POWER_OK* (bull-only, top-winner) |
| mean_reversion_in_uptrend [−7%] (CODR-1) | 9 | 0.78 | NEEDS_4H_DATA |
| cross_asset_leadership [down −5%] | 4 | 0.75 | POWER_TOO_LOW |
| calendar_seasonality | 1461 | — | POWER_OK count, friction-dominated |

\* count-OK but carries the structural defect Crypto-D7 already flagged (A parameter
freedom / C top-winner dependence).

## 6. Year-concentration notes

- **daily_crash_candle (−5%, −7%):** BTC maxYr 0.43/0.42 → **not** one-year-concentrated;
  events in **all four** IS years incl. the **2022 bear** (24 and 12 BTC events). The only
  family that is both ≥30 on BTC **and** regime-diverse.
- **mean_reversion_in_uptrend (CODR-1 family):** BTC −7% = 9, maxYr 0.78, **zero 2022**.
  The uptrend gate starves and concentrates the signal — not a crash scarcity.
- **trend_continuation:** ≥30 on +5% (52) but **zero 2022** and 0.56 in 2021 → bull-only,
  structurally top-winner-dependent (D7 option C, already-parked trend family).
- **vol_compression:** high counts but threshold-driven (parameter freedom) and heavily
  2023-concentrated (8% share 0.64) — D7 option A defect.
- **cross_asset_leadership:** BTC-leads-down only 4 → too-low power; corroboration baked
  into signal (D7 option B paradox).
- **calendar:** uniform counts → any seasonal edge tiny and friction-dominated (D7 E).

## 7. Recommended next step

### **SELECT_FAMILY_FOR_CRYPTO_D9_SPEC**

- **Selected family:** **daily crash-candle (1-day-drop reversion), decoupled from the
  CODR-1 `close>SMA200` uptrend gate.**
- **Primary threshold:** `ret_1d ≤ −5%` (BTC **81** events, 4-year spread, maxYr 0.43).
- **Secondary threshold:** `ret_1d ≤ −7%` (BTC **33**, still POWER_OK).
- **Why:** Only the raw daily-crash family clears BTC ≥30 IS events **and** is
  regime-diverse (fires in the 2022 bear). D8 isolates CODR-1's root cause — the
  **combination** of −7% **and** the uptrend gate produced exactly 9 BTC events
  (maxYr 0.78, zero 2022). Removing the uptrend gate restores ≥30 cross-regime BTC events,
  giving a future spec a fighting chance at the ≥30-trade and not-one-year-concentrated
  gates. Trend-continuation and vol-compression are rejected for top-winner dependence /
  parameter-freedom; cross-asset and calendar for too-low power / friction domination
  (consistent with Crypto-D7).
- **Caveats:** This is a **counting** result only. It proves the family **can** fire ≥30×
  on BTC across regimes; it says **nothing** about whether those events carry a positive,
  friction-survivable, top-3-robust **edge** — that is a future, separately-authorized
  **Crypto-D9 IS baseline**. The −10% crash (BTC 12) and 3d ≤−15% (BTC 14) variants remain
  sub-30 → NEEDS_4H_DATA if a deeper-flush variant is ever wanted. **No spec is frozen
  here**; Crypto-D9 must write its own pre-registered spec with a fresh ladder and a new id.

## 8. Forbidden actions (this lane)

`no_oos_use` · `no_2024_2025_2026_rows` · `no_strategy_backtest` · `no_pnl_simulation` ·
`no_optimization` · `no_parameter_sweep` · `no_old_strategy_rerun` · `no_network` ·
`no_data_fetch` · `no_exchange_api_execution` · `no_broker` · `no_paper_or_live` ·
`no_modification_of_frozen_data` · `do_not_touch_s30_or_futures` ·
`jarvis_templates_base_hydra_untouched` · `no_staging` · `no_commit`.

## 9. Final line

**“Crypto-D8 is a signal-density and statistical-power audit only; no crypto strategy is
validated, backtested, paper-ready, live-ready, or authorized for execution.”**

---

**Trading recommendation:** NONE — read-only counting audit only. CODR-1 v1 stays
**PARKED after IS_FAIL**. Recommendation is **SELECT_FAMILY_FOR_CRYPTO_D9_SPEC** (daily
crash-reversion, −5% primary / −7% secondary, decoupled from the uptrend gate), but **no
spec is frozen** and **no edge is claimed** — that requires a separately-authorized
Crypto-D9 IS baseline. Frozen BTC/ETH/SOL spot data stays valid; perps remain blocked; OOS
2024–2025 and 2026 stay sealed; crypto stays a separate research lane; **S30 stays PARKED
and the futures branches are untouched.**
