# S28-D4 — Breakout-Retest with Volatility Expansion + Mechanical Bad-Regime Gate · IN-SAMPLE Baseline (NQ daily, 2013–2022 ONLY)

**Baseline measurement only. The frozen S28-D3 engine was run ONCE over the
in-sample years 2013–2022. No OOS, no 2023–2025, no optimization, no parameter
change, no paper, no live. The engine was NOT modified.**

- **Created:** 2026-05-30
- **S28-D1 (hypothesis selection) commit:** `c8f5a46a0cd9a3732e0a9ed9c107d52c230e31d0`
- **S28-D2 (frozen spec) commit:** `5204fe1e3dafd40749769256abc3b77b6970f50f`
- **S28-D3 (engine + tests) commit:** `e7ce9a9e1cfb0209e34b03daf78774ef03aec5ea`
- **HEAD at run:** `bdcca5a` — a JARVIS-only background-automation commit
  (app.py, templates/jarvis.html, tests/test_jarvis_route.py,
  tools/jarvis_file_hygiene_report.py). It touched **no** agentic_factory file
  and S28-D3 (`e7ce9a9`) remains its ancestor; the frozen engine was run
  unmodified.

---

## 1. Inputs and OOS seal

| Item | Value |
|---|---|
| Market / timeframe | NQ continuous futures, daily bars |
| In-sample files | `data_offline/nq_c0_ohlcv_1d_2013.csv` … `_2022.csv` (10 files) |
| In-sample years | 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022 |
| OOS 2023–2025 | **NOT USED — SEALED.** The 2023/2024/2025 CSVs exist on disk but were never opened; the runner asserts no OOS year appears in any loaded path. |

## 2. Data QA (clean)

| Check | Result |
|---|---|
| Total bars | **3079** |
| Date range | 2013-01-02 → 2022-12-30 |
| Per-year rows | 2013:289 · 2014:302 · 2015:312 · 2016:310 · 2017:309 · 2018:312 · 2019:312 · 2020:312 · 2021:311 · 2022:310 |
| Rows outside 2013–2022 | 0 |
| Duplicate dates | 0 |
| Invalid OHLC rows | 0 |

**QA verdict: CLEAN.** Every bar falls in the IS window; no duplicates, no
malformed OHLC. (2013 has fewer rows because the provisioned series starts
2013-01-02 and ramps up; this is descriptive only and does not affect the run.)

## 3. Strategy result (R-only)

| Metric | Value |
|---|---|
| **Trade count** | **12** |
| **Total net R** | **−0.72R** |
| **Profit factor** | **0.91** |
| Wins / losses / flats | 4 / 8 / 0 |
| **Win rate** | 33.3% |
| **Expectancy** | **−0.06R / trade** |
| Average R | −0.06R |
| Median R | −1.00R |
| Best trade | +2.00R |
| Worst trade | −1.00R |
| **Max drawdown** | **4.00R** |
| Exit reasons | target ×3 · stop ×8 · time_stop ×1 |

**Exit detail:** all 8 losers were −1R hard stops. 3 winners hit the +2R target;
the 4th winner (2017) exited on the 20-bar **time stop** at +1.28R.

### Year-by-year net R (entry-date year)

| Year | Trades | Net R |
|---|---|---|
| 2013 | 0 | 0.00 |
| 2014 | 1 | **+2.00** |
| 2015 | 1 | −1.00 |
| 2016 | 1 | −1.00 |
| 2017 | 1 | **+1.28** |
| 2018 | 2 | **+1.00** |
| 2019 | 3 | 0.00 |
| 2020 | 1 | −1.00 |
| 2021 | 2 | −2.00 |
| 2022 | 0 | 0.00 |

**Positive years: 3/10** (2014, 2017, 2018). Negative: 4 (2015, 2016, 2020,
2021). Zero: 3 (2013, 2019, 2022).

### Fat-tail / top-3 dependence (anti-Donchian gate)

| Quantity | Value |
|---|---|
| Net R (all trades) | −0.72R |
| Sum of top 3 winners | +6.00R |
| **Net R without top 3 winners** | **−6.72R** |
| Anti-Donchian gate | **FAIL** |

The record is net-negative *with* the winners included, and collapses to −6.72R
once the three +2R winners are removed — the Donchian fat-tail-dependence failure
mode in its strongest form.

> **Diagnostic note (non-authoritative):** `find_setups_or_entries()` does not
> model the one-position rule, so its scan (30 raw breakouts → 14 entry
> candidates, 12 failed retests, 4 expired) is a superset. The authoritative
> trade count is **12**; 2 of the 14 diagnostic entry candidates were skipped
> because a position was already live.

## 4. S28-D2 pre-screen (pre-registered IS thresholds)

| Gate | PASS | Value | Result |
|---|---|---|---|
| IS trade count | ≥30 (FAIL <20) | 12 | **FAIL** |
| Profit factor | ≥1.40 (FAIL <1.15) | 0.91 | **FAIL** |
| Expectancy | >0 on IS | −0.06R | **FAIL** |
| Positive years | ≥6/10 (FAIL <5/10) | 3/10 | **FAIL** |
| Top-3 winner dependence | IS net positive without top 3 | −6.72R | **FAIL** |
| Max DD cap | IS max DD ≤ IS net R | 4.0R DD vs −0.72R net | **FAIL** (net negative; cap auto-breached) |

**Every pre-registered IS hard floor is breached.**

## 5. Verdict — **IS_FAIL**

S28 v1 shows **no in-sample edge**. The selective stack (rising-trend filter +
55-bar high + 1.25×ATR range expansion + 1.20×SMA volume expansion + retest-hold
+ near-mean bad-regime gate) is so restrictive it produced only **12 trades in
10 years**, and those 12 are **net-negative (−0.72R)** with **brittle fat-tail
dependence** (−6.72R without the top 3). Profit factor 0.91, expectancy −0.06R,
only 3/10 positive years.

## 6. Conservative interpretation

This is a **clean negative**, not "inconclusive." Per the S28-D2 anti-overfit
rules and the explicit instruction *"do not continue inconclusive like S26,"*
S28 is **PARKED as IS_FAIL**. No parameter change, no filter tweak, and no OOS
peek are permitted on this branch. Any new idea must open a **NEW pre-registered
branch** — S28 is not mutated in place.

## 7. Recommendation

**NONE.** No trading, no paper, no live, no OOS. PARK S28 as **IS_FAIL**.
Donchian, S26, and S27 remain PARKED. Do **NOT** proceed to S28-D5/OOS — the
2023–2025 seal stays intact. Do **NOT** optimize or re-tune S28 in place. A
future hypothesis starts a fresh pre-registered branch.

---

### Guardrails

`is_only` · `oos_sealed` · `no_optimization` · `no_parameter_sweeps` ·
`no_data_fetch` · `no_paper_or_live` · `no_broker_or_api` · `engine_unmodified`
· `s26_untouched` · `s27_untouched` · `donchian_untouched` ·
`jarvis_templates_hydra_untouched`.

**Trading recommendation:** NONE. S28 is PARKED IS_FAIL on a net-negative,
fat-tail-dependent in-sample record.
