# S26-D4 — Pre-registered Sealed OOS Protocol: Trend + S/R + EMA/RSI (long-only)

**PROTOCOL ONLY — pre-registration. Committed BEFORE any OOS data is run. No OOS
results, no OOS run, no optimization, no rule changes.**

- **Created:** 2026-05-29
- **Direction:** LONG-ONLY · **Accounting:** R-only · **Market:** NQ daily
- **Purpose:** fix the binding PASS/WATCH/FAIL gate for the 2023–2025 OOS run
  (S26-D5) *before* the OOS data is ever viewed — mirroring the S23-D15
  discipline.

---

## 1. Frozen strategy reference

| Artifact | Commit |
|---|---|
| S26-D1 spec | `af643aef58c63dd3bd904b4fb44406f4a2a55c3e` |
| S26-D2 engine | `1b1174e37c377b6331fa480a96115f286fb6a246` |
| S26-D3 IS baseline | `1bb70f9c3961cf4435d7953a69e06989f11a5dbb` |

No code, parameters, or rules may change between these commits and the OOS run.

---

## 2. Frozen strategy rules

- **Direction:** long-only.
- **Trend filter:** `close[i] > EMA200[i]` AND `EMA50[i] > EMA200[i]`.
- **Support reference:** prior **20-day rolling low** = lowest low over
  `bars[i-20:i]`, **excludes the current bar** (lookahead-safe).
- **Pullback gate:** `low[i] <= support_ref[i] + 1.5 * ATR20[i]`.
- **Confirmation:** RSI14 in band `40 <= RSI <= 55` **AND**
  (`RSI14[i] > RSI14[i-1]` OR `close[i] > EMA20[i]`).
- **Entry:** fill at **next bar (i+1) OPEN**.
- **Stop:** `entry − 2.0 * ATR20[i]` (hard **−1R** intrabar; 1R = 2N).
- **Target:** fixed **+2R**.
- **Backstop:** if still open at a bar **close** and `close < EMA50`, exit at
  that close (trend invalidation).
- **Per-bar exit precedence:** (1) −1R stop intrabar → (2) +2R target intrabar →
  (3) EMA50 close-break if still open.
- **Risk:** one position at a time · no pyramiding · R-only · flat-state entries
  only · management begins the bar *after* the fill bar.

---

## 3. IS reference result (2013–2022)

| Metric | Value |
|---|---|
| Trade count | 117 |
| Total R | +7.6536 |
| Profit factor | 1.2016 |
| Win rate | 39.32% |
| Expectancy | +0.0654 R/trade |
| Max drawdown | 10.5943 R |
| Best / worst trade | +2.0 R / −1.0 R |
| Median R | −0.1726 |
| Positive / negative years | 6 / 4 |
| Best-trade share of net | 26.1% |
| Total R without top-3 winners | +1.6536 |
| Verdict | **IS_CONTINUE (marginal)** |

---

## 4. OOS window

- **2023–2025 only.** Sealed/unseen until **this protocol is committed**.
- Run **exactly once** after commit. **No parameter changes after OOS. No added
  filters after OOS. No subperiod cherry-picking.**
- OOS files: `data_offline/nq_c0_ohlcv_1d_2023.csv`, `…_2024.csv`, `…_2025.csv`.
- OOS is judged **standalone** — the 10 IS CSVs are NOT pooled into the OOS run.

---

## 5. OOS metrics to judge

Trade count · total R · PF · win rate · expectancy R/trade · max DD R · best/worst
trade · median R · year-by-year R · positive-years count · exit-reason counts ·
best-trade share of net · top-3-removal result · and a direct **comparison to the
IS metrics** above.

---

## 6. PASS / WATCH / FAIL (pre-fixed; precedence FAIL → WATCH → PASS)

**PASS — all must hold:**
- OOS expectancy > 0
- OOS profit factor ≥ **1.10**
- OOS trade count ≥ 20 (ideally ≥ 30)
- OOS max DD ≤ 1.5 × IS max DD (**≤ 15.8915 R**)
- at least **2 of 3** OOS years positive
- best-trade share of net ≤ **50%**
- result remains **positive after removing the top 3 winners**
- no data-QA defect

**WATCH — any trigger:**
- OOS expectancy between −0.03R and +0.03R
- PF between 0.95 and 1.10
- trade count below 20
- one year dominates most of the result
- best-trade share > 50%
- top-3 removal turns result negative
- max DD worse than IS but not catastrophic

**FAIL — any trigger:**
- OOS expectancy < −0.03R
- PF < 0.95
- all or most OOS years negative
- max DD > 1.5 × IS max DD (> 15.8915 R) with no recovery
- result depends almost entirely on one or a few trades
- structural data issue appears

*Derived ceiling fixed here, before any OOS run:* `1.5 × 10.5943 = 15.8915 R`.

---

## 7. Interpretation rules

- **PASS does NOT mean live trading.**
- **PASS** only means continue to **S26-D6** (entry significance) and **S26-D7**
  (Monte Carlo / sequence-risk).
- **WATCH** means do NOT optimize; inspect the evidence and continue only if
  genuinely justified.
- **FAIL** means **park** this branch or open a **new branch** with a fresh
  protocol — do NOT tune against OOS.

---

## 8. Anti-overfit rules

- No parameter changes.
- No post-OOS filters.
- No cherry-picking dates.
- No rerunning OOS with edited rules.
- If changing rules → a **NEW branch with a fresh pre-registered protocol**, never
  a retrofit of this one.

---

## 9. Clear line

**No OOS backtest has been run. No 2023–2025 results have been viewed.** This is a
pre-registered protocol only. The binding gate is this committed protocol; the
S26-D5 OOS run will be judged strictly against it, **exactly once**.
