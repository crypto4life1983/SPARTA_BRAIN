# S26-D5 — Trend + S/R + EMA/RSI OOS Result (2023–2025 only)

**Sealed OOS result. Single frozen engine run on OOS data only. Judged strictly
against the pre-registered S26-D4 protocol. No optimization, no parameter changes,
no rule changes, no reruns.**

- **Created:** 2026-05-29
- **Direction:** LONG-ONLY · **Accounting:** R-only · **Market:** NQ daily

| Frozen artifact | Commit |
|---|---|
| S26-D1 spec | `af643aef58c63dd3bd904b4fb44406f4a2a55c3e` |
| S26-D2 engine | `1b1174e37c377b6331fa480a96115f286fb6a246` |
| S26-D3 IS baseline | `1bb70f9c3961cf4435d7953a69e06989f11a5dbb` |
| S26-D4 OOS protocol | `a5d90c63aa11f5c275fec4cae993ba6ab4ccb85f` |

---

## 1. Inputs (OOS only)

`data_offline/nq_c0_ohlcv_1d_2023.csv`, `…_2024.csv`, `…_2025.csv` (3 files),
concatenated into one continuous time-sorted stream.

**2013–2022 IS files were NOT used** (a hard assertion in the runner refused any
overlap with the 10 IS paths). OOS judged **standalone** — no IS pooling, exactly
as pre-registered in S26-D4.

---

## 2. Data QA

| Check | Value |
|---|---|
| Total bars | 934 |
| Date range | 2023-01-02 → 2025-12-30 |
| Duplicate dates | 0 |
| Invalid OHLC rows | 0 |
| Per-year rows sum = total | yes |

Per-year rows: 2023=310, 2024=313, 2025=311. **No QA defect.**

---

## 3. OOS strategy metrics (2023–2025)

| Metric | Value |
|---|---|
| Trade count | 32 |
| Total R | +7.9990 |
| Profit factor | 1.7694 |
| Win rate | 53.12% |
| Expectancy | +0.2500 R/trade |
| Max drawdown | 2.1827 R |
| Best trade | +2.0 R |
| Worst trade | −1.0 R |
| Average R | +0.2500 |
| Median R | +0.0304 |
| Positive / negative years | 3 / 0 |
| Best-trade share of net | 25.0% |
| Total R without top-3 winners | +1.9990 (still positive) |

**Year-by-year R (by exit/realization year):**

| Year | R |
|---|---|
| 2023 | +0.6547 |
| 2024 | +4.9348 |
| 2025 | +2.4094 |

**Exit-reason counts:** EMA50 trend-break = 16, target (+2R) = 8, stop (−1R) = 7,
end_of_data (forced close of one open position at 2025-12-30) = 1.

---

## 4. IS vs OOS comparison

| Metric | IS (2013–2022) | OOS (2023–2025) |
|---|---|---|
| Trade count | 117 | 32 |
| Total R | +7.6536 | +7.9990 |
| Profit factor | 1.2016 | 1.7694 |
| Win rate | 39.32% | 53.12% |
| Expectancy | +0.0654 R | +0.2500 R |
| Max drawdown | 10.5943 R | 2.1827 R |
| Median R | −0.1726 | +0.0304 |
| Best-trade share | 26.1% | 25.0% |
| Positive years | 6 / 10 | 3 / 3 |

OOS is **stronger than IS on every dimension** — higher PF, higher win rate, ~4×
expectancy, and far shallower drawdown (2.18R vs 10.59R). Fewer trades (32 vs 117)
because the standalone OOS stream spends its first ~200 bars on indicator warmup by
design.

---

## 5. Protocol decision — **PASS**

Judged strictly against the committed S26-D4 gate (precedence FAIL → WATCH → PASS).

**All eight PASS conditions hold:**

| PASS condition | Threshold | Actual | Met |
|---|---|---|---|
| OOS expectancy > 0 | > 0 | +0.2500 R | ✅ |
| OOS PF ≥ 1.10 | ≥ 1.10 | 1.7694 | ✅ |
| OOS trade count ≥ 20 | ≥ 20 (ideal ≥ 30) | 32 | ✅ |
| OOS max DD ≤ 1.5× IS DD | ≤ 15.8915 R | 2.1827 R | ✅ |
| ≥ 2 of 3 OOS years positive | ≥ 2 | 3 / 3 | ✅ |
| Best-trade share ≤ 50% | ≤ 50% | 25.0% | ✅ |
| Positive after removing top-3 | > 0 | +1.9990 R | ✅ |
| No data-QA defect | clean | clean | ✅ |

**FAIL conditions fired:** none.
**WATCH conditions fired:** none.

Because no FAIL or WATCH trigger fired and every PASS condition is satisfied, the
precedence resolves to **PASS**.

---

## 6. Honest reading of the PASS

- **OOS outperforming IS is a result to treat with caution, not celebration.** It
  is favorable, but a small-sample (32-trade) window over a specific 2023–2025
  regime (a strong tech/NQ uptrend) flatters a long-only trend-pullback system.
  The PASS authorizes more scrutiny, not confidence.
- **2024 carried 61.7% of net** (+4.93R of +7.999R). This did **not** trip the
  "one year dominates" WATCH trigger (threshold > 70%), but it is a concentration
  worth carrying into D7 sequence-risk.
- **Trade count is at the low end** (32; protocol prefers ≥ 30). The standalone
  warmup convention consumed most of 2023's signal opportunity.
- The capped +2R / −1R structure again distributed outcomes well (best trade only
  25% of net; positive without the top 3) — consistent with the design intent and
  the IS finding.

---

## 7. Conservative interpretation (pre-fixed in S26-D4)

- **PASS does NOT mean live or paper trading.** It only authorizes continuing to
  **S26-D6** (entry-rule significance — must clear the NOT_SUPPORTED bar that
  parked Donchian) and **S26-D7** (trade-order Monte Carlo / bootstrap
  sequence-risk — must clear FRAGILE).
- **WATCH** (not triggered here) would mean: do NOT optimize; inspect and continue
  only if justified.
- **FAIL** (not triggered here) would mean park or open a new branch — never tune
  against OOS.

---

### Notes of record
- Single frozen engine run; OOS run exactly once; no optimization; no parameter or
  rule changes; engine/tests unchanged.
- OOS standalone 2023–2025 as pre-registered; IS 2013–2022 not pooled.
- The binding gate was the committed S26-D4 protocol; this report does not alter it.
