# S23-D15 — Pre-Registered Sealed OOS Validation Protocol

**Status: `PRE-REGISTERED` — frozen BEFORE any 2023–2025 OOS data is unsealed, transcoded, or run.**

- **Created:** 2026-05-29
- **Frozen strategy-code commit:** `f94dfe1` — `engine/donchian_daily.py`, unchanged
- **This step does NOT:** transcode 2023–2025, run any OOS backtest, change parameters, optimize, or touch parked S24 files.

The purpose of this document is to lock down **exactly how the 2023–2025 OOS
result will be judged** so that the verdict cannot be rationalized after the
data is seen.

---

## 1. Frozen strategy (no changes permitted)

| Item | Value |
|---|---|
| Market | NQ continuous daily bars (NQ.c.0, UTC-calendar daily) |
| Entry channel | 55 |
| Exit channel | 20 |
| ATR period (Wilder N) | 20 |
| Stop | 2.0 × ATR (2N hard stop) |
| Pyramiding | none (`max_units_per_market = 1`) |
| Accounting | R-only (1R = initial 2N stop distance); no dollar/point-value/cost/roll |
| Engine behavior | Identical to S23-D14 — continuous time-sorted stream, single `simulate()` call, channels/ATR/open positions carry across boundaries; lookahead-safe |

---

## 2. Frozen IS reference (2013–2022)

| Metric | Value |
|---|---|
| Bars | 3079 |
| Trade count | 66 |
| Total R | +10.5421 R |
| Profit factor | 1.31 |
| Win rate | 42.4% |
| Expectancy | +0.16 R/trade |
| Max drawdown | 6.34 R |
| Best trade | +6.85 R |
| Worst trade | −1.0 R |
| Positive / negative years | 5 / 5 |

Source: `reports/s23_d14_2013_2022_donchian_is_baseline/report.json` (frozen — not re-run for this protocol).

---

## 3. OOS window

- **2023–2025 only.** Treated as **sealed / unseen** until this protocol is committed.
- **No parameter changes** after viewing OOS.
- **Run ONCE only**, after this protocol is committed. No re-runs, no subperiod cherry-picking.
- **Prerequisite:** separate explicit approval to transcode 2023–2025 from local
  Databento-native source (mirroring the S23-D13 method) before the single OOS run.

---

## 4. Minimum evaluation metrics (must all be reported)

- OOS trade count
- OOS total R
- OOS expectancy R/trade
- OOS profit factor
- OOS win rate
- OOS max drawdown R
- OOS best trade R / worst trade R
- OOS year-by-year R (2023, 2024, 2025)
- OOS positive years count
- Comparison: OOS expectancy vs IS expectancy (+0.16 R)
- Comparison: OOS max drawdown vs IS max drawdown (6.34 R)

---

## 5. PASS / WATCH / FAIL decision rules

**Precedence:** evaluate FAIL first, then WATCH, then PASS. Any FAIL trigger ⇒ FAIL.
PASS requires ALL PASS conditions AND no FAIL/WATCH trigger.

### PASS — only if ALL hold
- OOS expectancy > 0
- OOS profit factor > 1.05
- OOS max drawdown ≤ 1.5 × IS max DD (**≤ 9.51 R**) — *unless* total R remains positive and the excess drawdown is explained by sequence risk
- at least one positive OOS year
- no single trade accounts for more than 80% of OOS net profit
- no data-QA defect invalidates the result

### WATCH — any trigger
- expectancy near flat, between −0.05 R and +0.05 R
- profit factor between 0.95 and 1.05
- OOS trade count too small for confidence
- positive result depends mostly on one trade
- one year strongly dominates the result

### FAIL — any trigger
- expectancy < −0.05 R
- profit factor < 0.95
- max drawdown materially exceeds IS max DD without recovery
- all OOS years negative
- structural data issue appears

---

## 6. Interpretation rules

- **PASS does NOT mean live trading.** It means proceed only to the validation
  layer: trade-order Monte Carlo, drawdown sequence-risk, entry significance,
  regime breakdown.
- **WATCH** ⇒ do not optimize immediately; first inspect data quality and trade
  distribution.
- **FAIL** ⇒ park the frozen Donchian baseline or move to a new hypothesis; do
  **not** tune against OOS.

---

## 7. Anti-overfit rules

- No changing parameters after OOS.
- No cherry-picking OOS subperiods.
- No adding filters after seeing OOS unless it becomes a NEW, separately-labeled
  branch with fresh FUTURE OOS.
- No paper or live promotion from this step.

---

## Git handling

This folder (`reports/s23_d15_oos_protocol/`) is intended to follow the same
git-inert convention as prior S23 report folders (ignored via `.gitignore`).
Whether to instead **track** the protocol as a committed pre-registration record
is a judgment call worth flagging — a pre-registration has more integrity value
when committed (timestamped, immutable) than when left as an ignored local file.
No staging or commit is performed in this step; exact files will be proposed
before any staging.
