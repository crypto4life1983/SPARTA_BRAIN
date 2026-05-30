# S26-D3 — Trend + S/R + EMA/RSI IS Baseline (2013–2022 only)

**In-sample baseline measurement. Single frozen run on IS data only. No
optimization, no parameter changes, no OOS data used.**

- **Created:** 2026-05-29
- **S26-D1 spec commit:** `af643aef58c63dd3bd904b4fb44406f4a2a55c3e`
- **S26-D2 engine commit:** `1b1174e37c377b6331fa480a96115f286fb6a246`
- **Direction:** LONG-ONLY · **Accounting:** R-only · **Market:** NQ daily

---

## 1. Inputs (IS only)

`data_offline/nq_c0_ohlcv_1d_2013.csv` … `…_2022.csv` (10 files, 2013–2022),
concatenated into one continuous time-sorted stream.

**2023–2025 files were NOT used** (`…_2023/2024/2025.csv` explicitly excluded; a
hard assertion in the runner refused any overlap). OOS remains sealed.

---

## 2. Data QA

| Check | Value |
|---|---|
| Total bars | 3079 |
| Date range | 2013-01-02 → 2022-12-30 |
| Duplicate dates | 0 |
| Invalid OHLC rows | 0 |
| Per-year rows sum = total | yes |

Per-year rows: 2013=289, 2014=302, 2015=312, 2016=310, 2017=309, 2018=312,
2019=312, 2020=312, 2021=311, 2022=310.

---

## 3. Strategy metrics (IS 2013–2022)

| Metric | Value |
|---|---|
| Trade count | 117 |
| Total R | +7.6536 |
| Profit factor | 1.2016 |
| Win rate | 39.32% |
| Expectancy | +0.0654 R/trade |
| Max drawdown | 10.5943 R |
| Best trade | +2.0 R |
| Worst trade | −1.0 R |
| Average R | +0.0654 |
| Median R | −0.1726 |
| Positive / negative years | 6 / 4 |

**Year-by-year R (by exit/realization year):**

| Year | R |
|---|---|
| 2013 | +3.29 |
| 2014 | −1.25 |
| 2015 | −2.73 |
| 2016 | −4.45 |
| 2017 | +4.29 |
| 2018 | +0.35 |
| 2019 | +1.78 |
| 2020 | +4.82 |
| 2021 | +2.54 |
| 2022 | −0.99 |

**Exit-reason counts:** EMA50 trend-break = 75, stop (−1R) = 22, target (+2R) = 20.

---

## 4. S26-D1 IS pre-screen (informational — NOT the OOS gate)

| Pre-fixed check | Result |
|---|---|
| IS trades ≥ 40 | ✅ 117 |
| PF ≥ 1.20 | ✅ 1.2016 (marginal) |
| Expectancy > 0 | ✅ +0.065R |
| Majority of years positive | ✅ 6 of 10 |
| Positive after removing top-3 winners | ✅ +1.65R (best trade only 26.1% of net) |

**Winner-dependence is much healthier than Donchian:** best trade = 26.1% of net
(Donchian IS was 64.9%), and removing the top 3 still leaves +1.65R positive
(Donchian IS flipped to −3.82R). The capped +2R target distributed outcomes as
intended.

---

## 5. Verdict — **IS_CONTINUE**

All pre-screen gates pass: 117 trades, PF 1.20, expectancy > 0, 6/10 positive
years, and no top-3 winner dependence.

**But read the caveats — this is in-sample and marginal:**
- **PF 1.20 only just meets the threshold** (1.2016). Little margin.
- **Max drawdown 10.59R exceeds total net (7.65R).** The equity path is choppy —
  it makes money but takes a deep dip getting there. This is a real fragility to
  watch in D7 sequence-risk.
- **Win rate is low (39%)** and median trade is **negative (−0.17R)**: most trades
  are small EMA50 trend-break losses (75 of 117), carried by 20 full +2R targets
  and −1R-capped stops. The edge is in the asymmetry (capped loss / 2R win), not
  in hit rate — consistent with the design.
- 2014–2016 was a sustained 3-year IS drawdown (−1.25, −2.73, −4.45R).

---

## 6. Conservative interpretation

- **IS_CONTINUE does NOT mean OOS will pass.** It only means the IS baseline
  justifies pre-registering an OOS protocol.
- In-sample numbers are the easy case and must not be over-read.
- No tuning is permitted from here: the rules are frozen. If OOS fails, the branch
  is parked — not retrofitted.

---

## 7. Recommended next step

Verdict is IS_CONTINUE, so the correct next step is **S26-D4: pre-register the
sealed OOS (2023–2025) validation protocol and commit it BEFORE any OOS data is
run** — mirroring the S23-D15 discipline. **Awaiting explicit approval; D4 is not
started.**

---

### Notes of record
- Single frozen engine run; no optimization; no parameter changes; engine/tests unchanged.
- OOS 2023–2025 untouched and sealed.
- IS pre-screen thresholds are informational; the binding PASS/WATCH/FAIL gate is the committed D4 OOS protocol.
