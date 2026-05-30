# S26-D12 — Multi-Market Robustness (frozen engine, validation only)

**Runs the frozen S26-D2 engine ONCE per market/window (ES, MES, MNQ; IS + OOS) and
judges multi-market robustness strictly against the pre-registered S26-D10 gates.
VALIDATION ONLY — no optimization, no parameter changes, no variants, no new filters.
The engine, tests, and parameters are unchanged. ES is the only independent market beyond
NQ; MES/MNQ are same-underlying `proxy_micro` corroboration and cannot upgrade the verdict.**

- **Created:** 2026-05-30 · **Reference commit:** `fb4fecd` (S26-D11 DATA_PROVISIONED)
- **Frozen engine:** `engine/trend_sr_ema_rsi_daily.py` — UNCHANGED.
- **Data source:** `data_offline/` CSVs provisioned in S26-D11 (gitignored). NQ used as
  reference only via the committed D3–D9 reports — **NQ was not re-run here.**
- **Pre-registered ceiling (per S26-D10):** with only one independent underlying beyond
  NQ available (S&P via ES), the **maximum attainable verdict is PARTIAL_SUPPORT**.

---

## 1. S26 context (the chain so far)

The S26 branch tests a long-only "Trend + Support/Resistance + EMA/RSI" daily strategy.
Prior verdicts: D3 IS_CONTINUE (marginal) · D5 OOS PASS · D6 ENTRY_EDGE_INCONCLUSIVE ·
D7 SEQUENCE_RISK_INCONCLUSIVE · D8 CONCENTRATED_SUPPORT · D9 DATA_LIMITED_INCONCLUSIVE
(only NQ had clean local data) · D10 PROTOCOL_REGISTERED (pre-registered the multi-market
data + gates) · D11 DATA_PROVISIONED (clean ES/MES/MNQ daily CSVs sourced from Databento).
**D12 is the one-shot robustness test those steps set up.**

## 2. Exact data files used

| Market | Role | Coverage | IS files | OOS files |
|---|---|---|---|---|
| **ES** | independent_market (S&P 500) | FULL | `es_c0_ohlcv_1d_2013…2022.csv` (10) | `es_c0_ohlcv_1d_2023…2025.csv` (3) |
| **MES** | proxy_micro_of_ES | PARTIAL_IS | `mes_c0_ohlcv_1d_2019…2022.csv` (4) | `mes_c0_ohlcv_1d_2023…2025.csv` (3) |
| **MNQ** | proxy_micro_of_NQ | PARTIAL_IS | `mnq_c0_ohlcv_1d_2019…2022.csv` (4) | `mnq_c0_ohlcv_1d_2023…2025.csv` (3) |

IS and OOS were streamed **separately per market** (no pooling, no market mixing). No 2026
data. No CSV was overwritten. MES/MNQ IS begins **2019-05-05** (micro-contract launch) — a
genuinely shorter, different regime span than ES/NQ's 2013-2022, flagged honestly below.

## 3. Results — frozen engine, one run per market/window

### ES — independent market (S&P 500), coverage FULL

| Window | Range | Bars | Trades | Total R | PF | Win% | Exp R | Max DD R | Best/Worst | Median |
|---|---|---|---|---|---|---|---|---|---|---|
| **IS** | 2013-01-02 → 2022-12-30 | 3096 | 125 | **+7.6725** | 1.2003 | 38.4% | +0.0614 | **16.7281** | +2.0 / −1.0 | −0.1542 |
| **OOS** | 2023-01-02 → 2025-12-31 | 935 | 27 | **+11.4584** | 2.2352 | 59.3% | +0.4244 | 2.0697 | +2.0 / −1.0 | +0.0769 |

- **ES IS year R:** 2013 +3.91, 2014 −3.55, 2015 −4.59, 2016 **−8.34**, 2017 +7.01,
  2018 −0.79, 2019 +3.61, 2020 +5.05, 2021 +5.76, 2022 −0.38 → **5 positive / 5 negative
  years.** Exits: ema50_trend_break 91 / target 19 / stop 15.
- **ES IS without top-3 winners:** +1.6725 (still positive). Best-trade share of net 26.1%.
- **ES OOS year R:** 2023 −0.93, 2024 +4.05, 2025 **+8.34** → 2 positive / 1 negative.
  Exits: stop 9 / target 9 / ema50_break 8 / end_of_data 1.
- **ES OOS without top-3 winners:** +5.4584 (still positive). Best-trade share 17.5%.
- **QA:** 0 duplicate dates, 0 invalid OHLC rows in both windows.

### MES — proxy_micro of ES (S&P 500), coverage PARTIAL_IS (from 2019-05-05)

| Window | Range | Bars | Trades | Total R | PF | Win% | Exp R | Max DD R |
|---|---|---|---|---|---|---|---|---|
| **IS** | 2019-05-05 → 2022-12-30 | 1140 | 28 | +10.3681 | 2.6569 | 46.4% | +0.3703 | 1.8296 |
| **OOS** | 2023-01-02 → 2025-12-31 | 935 | 27 | +11.7895 | 2.3276 | 55.6% | +0.4366 | 2.0673 |

without-top3: IS +4.3681 / OOS +5.7895 (both positive). 0 dup / 0 invalid both windows.

### MNQ — proxy_micro of NQ (Nasdaq-100), coverage PARTIAL_IS (from 2019-05-05)

| Window | Range | Bars | Trades | Total R | PF | Win% | Exp R | Max DD R |
|---|---|---|---|---|---|---|---|---|
| **IS** | 2019-05-05 → 2022-12-30 | 1140 | 27 | +6.3671 | 1.9367 | 48.1% | +0.2358 | 2.6177 |
| **OOS** | 2023-01-02 → 2025-12-31 | 935 | 32 | +7.6833 | 1.7191 | 50.0% | +0.2401 | 2.1906 |

without-top3: IS +0.3671 / OOS +1.6833 (both positive). 0 dup / 0 invalid both windows.

## 4. Comparison to NQ reference (committed D3–D9)

| | Trades | Total R | PF | Exp R | Max DD R |
|---|---|---|---|---|---|
| **NQ IS** (ref) | 117 | +7.6536 | 1.2016 | +0.0654 | 10.5943 |
| **ES IS** | 125 | +7.6725 | 1.2003 | +0.0614 | **16.7281** |
| **NQ OOS** (ref) | 32 | +7.9990 | 1.7694 | +0.2500 | 2.1827 |
| **ES OOS** | 27 | +11.4584 | 2.2352 | +0.4244 | 2.0697 |

- **ES IS mirrors NQ IS almost exactly in shape:** thin marginal edge (PF ≈ 1.20, expectancy
  ≈ +0.06R), positive net carried through a long 2014-2016 chop drawdown — but ES's IS
  drawdown (**16.73R**) is materially deeper than NQ's (10.59R) and exceeds **1.5× NQ IS DD**.
- **ES OOS confirms NQ OOS in direction and strengthens it** (PF 2.24 vs 1.77), but on a
  **smaller sample (27 < 30 ideal)** and **dominated by 2025 (+8.34R = 72.8% of OOS net)**.
- **Micro corroboration (same-underlying, NOT independent):** MNQ OOS (32 trades, +7.68R)
  ≈ NQ OOS (32 trades, +8.00R) — a faithful replica of NQ. MES OOS (27 trades, +11.79R)
  ≈ ES OOS (27 trades, +11.46R) — a faithful replica of ES. This is exactly what micros
  should look like; it is corroboration, **not** a second independent market.
- **MES IS apparent strength is an artifact:** its PF 2.66 / DD 1.83R reflects the **partial
  2019-2022 window that misses ES's 2014-2016 drawdown**, not a genuinely stronger edge.
  Judged honestly, MES IS is the same edge measured over a shorter, easier regime span.

## 5. Verdict — **PARTIAL_SUPPORT_WITH_CAUTION**

ES — the one independent market beyond NQ — **confirms the S26 edge in direction on both
IS and OOS** (es_is_positive = es_oos_positive = true; positive without top-3 winners in
both windows; floors met). That clears the bar for PARTIAL_SUPPORT, which per S26-D10 is
the **ceiling reachable from {NQ,MNQ,ES,MES}** (only one independent underlying). It does
**not** reach ROBUST_SUPPORT, which would require a second independent underlying.

The verdict is downgraded to **PARTIAL_SUPPORT_WITH_CAUTION**, not clean PARTIAL_SUPPORT,
on the following pre-registered weak flags (all substantively grounded, not cosmetic):

- **`is_pf_below_1_30`** — ES IS PF 1.20: the IS edge is thin/marginal, same fragile profile
  as NQ IS.
- **`is_dd_over_1_5x_nq_is`** — ES IS max drawdown 16.73R exceeds 1.5× NQ's IS DD (10.59R):
  the independent market endured a deeper equity dip to earn the same net.
- **`oos_trades_below_30`** — ES OOS only 27 trades: below the ideal-30 confirmation sample.
- **`es_oos_single_year_dominated`** — ES OOS 2025 = 72.8% of OOS net (> 50%): the strong
  OOS result leans heavily on a single year.

micros_both_positive (IS and OOS) = true, but per the no-proxy rule this corroboration
**cannot upgrade** the verdict past PARTIAL_SUPPORT.

## 6. Conservative interpretation

- The S26 edge **does transfer** to a genuinely independent market (S&P via ES) in
  direction — it is not a Nasdaq-only artifact. That is real, and better than NQ_ONLY_SUPPORT.
- But the transfer is **marginal and caveated**: thin IS profit factor, an IS drawdown
  deeper than NQ's, a sub-30 OOS sample, and an OOS result concentrated in one year (2025).
- The strong-looking micro results are **same-underlying replicas** (MNQ↔NQ, MES↔ES), not
  independent evidence; MES's especially strong IS is a **short-window artifact**.
- **This is the realistic best case** for this symbol set. To reach ROBUST_SUPPORT, the
  S26-D10 protocol must first be amended to add a **third distinct underlying** (a
  non-equity-index market), then provisioned and tested under the same frozen discipline.

## 7. Verdict — **PARTIAL_SUPPORT_WITH_CAUTION** · S26 NOT deployable

No deployment. No paper trading. No live/broker action. The edge has one independent
confirmation (caveated) and same-underlying corroboration; it does **not** meet the bar for
multi-market robustness sufficient to promote. **S26 remains research-only and held.**

---

### Notes of record
- Validation only — frozen engine run once per market/window. No optimization, no parameter
  change, no variants, no new filters, no engine/test change.
- ES = independent (S&P); MES/MNQ = `proxy_micro`, excluded from the independent-market
  count. Max attainable verdict = PARTIAL_SUPPORT (one independent underlying beyond NQ).
- NQ not re-run; NQ reference figures taken from the committed D3–D9 records.
- Data from `data_offline/` (gitignored, provisioned S26-D11). No CSV overwritten, no 2026
  data, no market pooling. 0 duplicate dates / 0 invalid OHLC across all six windows.
- The temp runner `_s26_d12_multimarket_runner.py` is a generated artifact — deleted after
  this report; `report.json` + `report.md` are the durable deliverables. Donchian/S23/S24
  and `templates/base.html` untouched.
