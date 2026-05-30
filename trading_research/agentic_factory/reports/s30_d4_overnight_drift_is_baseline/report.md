# S30-D4 — Overnight Drift IS Baseline (NQ daily 2013–2022, IS only)

**This is an in-sample baseline measurement.** The frozen S30 rules (S30-D2,
`275540f`) were executed by the committed S30-D3 engine (`3c8dfff`) on **IS data
only**. **No engine/test/spec change, no optimization, no parameter change, no OOS
data, no data fetch, no paper/live, no staging, no commit.** The measurement-validity
gate is reported **before** any edge interpretation.

- **Created:** 2026-05-30
- **HEAD at run:** `3c8dfff` (the S30-D3 commit).
- **Source commits:**
  - S30-D1 idea selection — `9e1c565f19c54ce00695de73aeff7560089f766c`
  - S30-D2 frozen spec — `275540f301b4478fdfdb29393e12c42ef1f6f6fa`
  - S30-D3 engine + tests — `3c8dfff0c01eaea4fd38865d34240c33f6be987d`

---

## 4. Input files (IS only)

`data_offline/nq_c0_ohlcv_1d_2013.csv` … `…_2022.csv` (ten yearly NQ daily CSVs,
2013–2022).

## 5. OOS exclusion

**2023 / 2024 / 2025 CSVs were NOT read.** Enforced at two layers via
`validation_is_runner`: `assert_is_only_paths` (path seal refusing 2023/2024/2025)
**and** `assert_bars_in_is_range(2013…2022)` (bar-date seal). **OOS remains sealed.**

## 6. Data QA

| Field | Value |
|---|---|
| Total bars | **3079** |
| Date range | 2013-01-02 → 2022-12-30 |
| Duplicate dates | 0 |
| Invalid OHLC rows | 0 |
| QA verdict | **CLEAN** |

Per-year row counts: 2013=289, 2014=302, 2015=312, 2016=310, 2017=309, 2018=312,
2019=312, 2020=312, 2021=311, 2022=310.

## 7. Measurement validity — gate FIRST

| Field | Value |
|---|---|
| Observations | 3078 |
| Candidate pairs | 3078 |
| Skipped invalid pairs | 0 |
| Max abs reconstruction error | **0.0** |
| Tolerance | 1e-6 |
| **Verdict** | **MEASUREMENT_VALID** |

**Critical caveat — what this PASS does and does not prove.** The reconstruction
check `overnight + day_session == total_day` is an **algebraic identity**
(`(open−prevclose) + (close−open) ≡ close−prevclose`) for any finite-price bar, so an
error of `0.0` only confirms **internal arithmetic consistency**. It does **not**
prove that the NQ daily-bar `open`/`close` prints bracket the **true cash overnight
session** (≈ 4 pm → 9:30 am ET) where the documented overnight-drift anomaly lives.
NQ trades nearly 24h on Globex with a 00:00 UTC daily boundary; the strongly negative
result below is consistent with the daily-bar open/close **not** representing the cash
overnight window — exactly the **S30-D2 §4 representativeness risk**. Settling that
question would require intraday/session-level data not held offline.

## 8. Distribution metrics (IS, points unless noted)

| Metric | Value |
|---|---|
| Observation / trade count | **3078** |
| Total overnight points | **−2262.0** |
| Average overnight points | −0.7349 |
| Median overnight points | 0.0 |
| Total overnight return (Σ simple %) | −35.56% |
| Average overnight return % | −0.01155% / night |
| Median overnight return % | 0.0% |
| Win rate (positive nights) | 37.85% |
| Profit factor (gain/loss) | **0.650** |
| Best / worst night (points) | +323.5 / −655.5 |
| Best / worst night (%) | +2.298% / −8.795% |
| Positive years | **3 / 10** (2017, 2021, 2022) |

**Year-by-year overnight points:** 2013 −67.0 · 2014 −157.0 · 2015 −308.5 ·
2016 −48.25 · 2017 **+15.5** · 2018 −83.25 · 2019 −191.5 · **2020 −1513.25** ·
2021 **+12.0** · 2022 **+79.25**.

**Top-day dependence gate:**

| Field | Value |
|---|---|
| Net points | −2262.0 |
| Top-3-day contribution | +621.75 |
| Net without top-3 days | **−2883.75** |
| Top-1% day count | 30 |
| Top-1% day contribution | +2002.75 |
| Net without top-1% days | **−4264.75** |
| Passes ex-top-3 | **FALSE** |
| Passes ex-top-1% | **FALSE** |

The gate fails not because a thin positive net collapses, but because **net is already
negative** before any winner is removed; removing the top winners only deepens the
loss.

**ATR20-normalized overnight (secondary):** warm obs 3058 · avg normalized R −0.00732
· median 0.0 · best +1.2522 · worst −1.9070. (Negative, consistent with the points
result.)

## 9. S30-D2 pre-screen

| Pre-screen criterion | Result |
|---|---|
| High observation count | **PASS** — 3078 (count is not the problem) |
| Positive average overnight return | **FAIL** — negative (−0.735 pts / −0.0116%) |
| Positive after top-day removal | **FAIL** — −2883.75 (ex-top-3), −4264.75 (ex-top-1%) |
| Enough positive years | **FAIL** — 3/10 |
| Friction headroom (preliminary) | **FAIL** — net negative *before* any cost; no edge to erode |

## 10. Verdict

# **IS_FAIL**

## 11. Conservative interpretation

- **IS_FAIL ⇒ PARK or redesign as a NEW branch — not tune this one.** No parameter,
  leg, filter, or direction change may be applied to S30 to rescue it; any such change
  is a brand-new branch with a fresh frozen spec and its own pre-registration.
- **Why it failed:** the frozen long-overnight hypothesis is **net negative in-sample**
  on NQ daily futures bars (PF 0.65, avg −0.735 pts, 3/10 positive years, fails the
  top-day gate). The hypothesized positive overnight risk premium is **not present as
  measured**.
- **Measurement nuance:** `MEASUREMENT_VALID` here is only arithmetic consistency. The
  negative result most plausibly reflects that NQ futures daily open/close do **not**
  represent the cash overnight window where the anomaly is documented (the §4 risk) —
  a measurement-representativeness limitation of the *data for this hypothesis*, not an
  engine bug.
- **OOS stays SEALED.** An IS_FAIL never advances to OOS. **No paper/live promotion.**

## 12. Recommended next step

**STOP / PARK** S30 overnight-drift (long-only, NQ daily futures). **Do NOT
pre-register S30-D5 OOS** — an IS_FAIL is not eligible for an OOS protocol. The branch
is parked alongside Donchian, S26, S27, S28, S29.

If the overnight-drift idea is ever revisited it requires (a) cash-session/intraday
data that actually brackets the true overnight window (**not held offline**) and (b) a
**new** frozen spec and branch id — a separate, separately-authorized effort, never a
tune of S30. **S30-D5 is not authorized.**

---

**Trading recommendation:** NONE. IS baseline result only. S30 overnight-drift
(long-only, NQ daily futures) is **IS_FAIL** and is **PARKED**. Donchian, S26, S27,
S28, S29 remain PARKED. No active strategy; no paper/live system exists or is
authorized. OOS remains sealed.
