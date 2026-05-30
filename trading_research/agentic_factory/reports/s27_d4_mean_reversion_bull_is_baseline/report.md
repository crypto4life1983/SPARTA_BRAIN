# S27-D4 — Mean Reversion After Overextension Inside Bull Trend · IS Baseline (NQ daily 2013–2022)

**Baseline measurement only — a single run of the FROZEN S27 engine over in-sample NQ daily
bars 2013–2022. No OOS, no 2023–2025, no optimization, no parameter change, no rule change.**

- **Created:** 2026-05-30
- **S27-D1 (hypothesis selection):** `dc53087468ab955c85dacb70241c8b3387593883`
- **S27-D2 (frozen spec):** `4a678ce935850164aec00e32f45390ee456d1fad`
- **S27-D3 (engine + tests):** `d016127c77cd46116f632064de850c1fa8f0b103`
- **Engine:** `engine/s27_mean_reversion_bull.py` — frozen, unchanged.

---

## 1. Inputs (IS only)

Ten NQ continuous daily CSVs, concatenated and time-sorted:

```
data_offline/nq_c0_ohlcv_1d_2013.csv … nq_c0_ohlcv_1d_2022.csv
```

**Excluded and NOT read for results** (OOS, sealed): `nq_c0_ohlcv_1d_2023.csv`,
`nq_c0_ohlcv_1d_2024.csv`, `nq_c0_ohlcv_1d_2025.csv`. The runner asserts the OOS files never
enter the IS set; **2023–2025 were not used.**

## 2. Data QA

| Check | Value |
|---|---|
| Total bars | 3079 |
| Date range | 2013-01-02 → 2022-12-30 |
| Duplicate dates | 0 |
| Invalid OHLC rows | 0 |

Per-year row counts: 2013 = 289, 2014 = 302, 2015 = 312, 2016 = 310, 2017 = 309, 2018 = 312,
2019 = 312, 2020 = 312, 2021 = 311, 2022 = 310.

## 3. Strategy metrics (R-only, IS 2013–2022)

| Metric | Value |
|---|---|
| Trade count | **18** |
| Total R | **−1.7506R** |
| Profit factor | **0.8372** |
| Win rate | 33.3% |
| Expectancy | **−0.0973R / trade** |
| Max drawdown | 2.50R |
| Best trade | +1.50R |
| Worst trade | −1.00R |
| Average R | −0.0973R |
| Median R | −1.00R |
| Positive years | **3 / 10** |
| Exit reasons | stop ×10, target ×6, time_stop ×2 |
| Top-3 winners R | +4.50R |
| Total R without top 3 | **−6.2506R** |
| Best-trade share of net | undefined (net R is negative) |
| Anti-Donchian top-3 gate | **FAIL** |

**Year-by-year R:** 2013 0.00 · 2014 0.00 · 2015 −1.01 · 2016 +0.50 · 2017 0.00 · 2018 +0.50 ·
2019 −0.74 · 2020 +1.50 · 2021 −2.50 · 2022 0.00.

## 4. S27-D2 pre-screen (gates were pre-registered BEFORE any result)

| Gate | Pre-registered | Observed | Result |
|---|---|---|---|
| IS trade-count floor | PASS ≥40 · WATCH 25–39 · FAIL <25 | 18 | **FAIL** |
| Profit factor | PASS ≥1.30 · WATCH 1.10–1.29 · FAIL <1.10 | 0.84 | **FAIL** |
| Expectancy > 0 | PASS >0 on IS | −0.097R | **FAIL** |
| Top-3 removal positive | net stays positive ex top-3 | −6.25R | **FAIL** |
| Positive years | PASS ≥6/10 · WATCH 5/10 · FAIL <5/10 | 3/10 | **FAIL** |
| Max DD vs net | DD ≤ net (pass) / >1.5× net (fail) | DD 2.50R, net −1.75R | moot — net is negative |

## 5. Verdict — **IS_FAIL**

The IS baseline breaches **five** independent pre-registered hard floors at once:

1. **Net-negative in-sample** (−1.75R) — the strategy loses money *with* its winners included.
2. **Trade count 18 < 25** hard floor — the two-step confirmation is even more restrictive than
   the spec's worst-case worry; the sample is too thin to support any edge claim.
3. **PF 0.84 < 1.10** — gross losses exceed gross wins.
4. **Expectancy −0.097R < 0**.
5. **Positive years 3/10 < 5/10**, and the **anti-Donchian top-3 gate fails** (−6.25R without the
   best three trades — already negative *with* them, the inverse of a winner-dependence problem:
   there is no winning core to depend on).

This is unambiguous. No single soft miss; multiple hard floors fail simultaneously.

## 6. Conservative interpretation

- **IS_CONTINUE** would *not* mean OOS will pass — it would only license pre-registering an OOS
  protocol. **Not applicable here.**
- **IS_WATCH** would mean minor misses, continue only if justified. **Not applicable here.**
- **IS_FAIL** means **park or redesign as a NEW branch — do NOT tune, sweep, or relax any S27
  parameter to rescue this one.** The S27-D2 anti-overfit rules forbid changing
  RSI/ATR/EMA/target/stop/slope/time-stop after seeing results; any change opens a new branch.

## 7. Recommendation for the next step

**STOP and PARK S27.** Do **not** pre-register or run the S27-D5 OOS protocol: there is no
in-sample edge to validate out-of-sample, and burning the sealed 2023–2025 OOS on a branch that
already failed IS would waste the one clean OOS look. Any future mean-reversion idea must be a
**new, separately-authorized branch** with its own frozen pre-registration — not a tuned S27.

S26 stays **PARKED**. Donchian stays **PARKED**. S27 is recommended for **PARK** (IS_FAIL).

---

### Notes of record
- Baseline IS measurement only — one frozen run on 2013–2022. No OOS/2023–2025 data used, no
  optimization, no parameter or rule change, no engine/test change.
- The generated `_run.json` (full trade list) is an untracked artifact, not relied upon for the
  committed verdict and not staged.
- S26, Donchian/S23/S24/S25, JARVIS, `templates/base.html`, and the hydra dir untouched.
