# S26-D8 — Regime / Time Breakdown: Trend + S/R + EMA/RSI (diagnostic only)

**Characterizes WHERE the frozen S26 edge lives — by time and by regime. DIAGNOSTIC
ONLY: not optimization, not a strategy/parameter change, not a new variant.** The
frozen engine was run once per window to regenerate the realized trades (same as
D7); counts/totals asserted against the committed reports. Regime buckets reuse
ONLY existing frozen outputs (ATR, EMA50/EMA200), sliced into descriptive
terciles — no threshold is fit to results.

- **Created:** 2026-05-29 · **Direction:** LONG-ONLY · **Market:** NQ daily
- **Reference:** S26-D7 commit `8a613e8`
- Prior verdicts: D3 IS_CONTINUE (marginal) · D5 OOS PASS · D6
  ENTRY_EDGE_INCONCLUSIVE · D7 SEQUENCE_RISK_INCONCLUSIVE.

## R-list summary (regenerated, assert-verified)

| Set | Count | Total R |
|---|---|---|
| IS 2013–2022 | 117 | +7.6536 |
| OOS 2023–2025 | 32 | +7.9990 |
| Combined 2013–2025 *(descriptive)* | 149 | +15.6526 |

---

## 1. By year

| Year | IS R | | Year | OOS R |
|---|---|---|---|---|
| 2013 | +3.2897 | | 2023 | +0.6547 |
| 2014 | −1.2545 | | 2024 | +4.9348 |
| 2015 | −2.7328 | | 2025 | +2.4094 |
| 2016 | −4.4470 | | | |
| 2017 | +4.2862 | | | |
| 2018 | +0.3501 | | | |
| 2019 | +1.7840 | | | |
| 2020 | +4.8232 | | | |
| 2021 | +2.5430 | | | |
| 2022 | −0.9883 | | | |

- **IS is time-concentrated:** profit lives in **2017 (+4.29) and 2020 (+4.82)**.
  Remove just those two years and IS is **net −1.46R**. 2014–2016 was a sustained
  **3-year drawdown** (−1.25, −2.73, −4.45 = −8.43R cumulative).
- **OOS is also concentrated:** **2024 (+4.93) = 62%** of the OOS total; 2023 was
  barely positive (+0.65).

---

## 2. By volatility regime (ATR/price terciles, combined cuts)

Tercile cuts (ATR/entry): low < 0.01173 ≤ mid < 0.01517 ≤ high.

| Regime | IS R (n) | OOS R (n) | Combined R (n) |
|---|---|---|---|
| vol_low | +2.9109 (46) | +3.0 (3) | +5.9109 (49) |
| vol_mid | +6.1251 (35) | +3.7686 (15) | **+9.8937 (50)** |
| vol_high | −1.3824 (36) | +1.2304 (14) | −0.1520 (50) |

**The edge is a low/mid-volatility phenomenon.** High-volatility entries are net
flat-to-negative (combined −0.15R over 50 trades). This is the clearest regime
signal in the breakdown.

---

## 3. By trend regime ((EMA50−EMA200)/EMA200 terciles, combined cuts)

Tercile cuts: weak < 0.04811 ≤ mid < 0.06327 ≤ strong.

| Regime | IS R (n) | OOS R (n) | Combined R (n) |
|---|---|---|---|
| trend_weak | +2.8891 (47) | +2.7651 (2) | +5.6542 (49) |
| trend_mid | +3.2134 (38) | +0.9400 (12) | +4.1534 (50) |
| trend_strong | +1.5511 (32) | +4.2939 (18) | +5.8450 (50) |

**Broad across trend strength** — all three terciles are positive in combined. The
pullback entry is not confined to one trend-strength band.

---

## 4. Signal clustering & side

| Bucket | IS R (n) | OOS R (n) | Combined R (n) |
|---|---|---|---|
| clustered (entry ≤10 bars after prior) | +3.8534 (64) | +5.4472 (16) | +9.5202 (81) |
| spaced | +3.8002 (53) | +2.5518 (16) | +6.1324 (68) |

Both clustered and spaced entries are positive — profit is **not** an artifact of
one repeated-signal cluster. **Side:** long-only; short side not applicable.

---

## 5. By exit reason (combined)

| Exit | Total R | n |
|---|---|---|
| target (+2R) | +56.0 | 28 |
| stop (−1R) | −29.0 | 29 |
| ema50_trend_break | −11.3767 | 91 |
| end_of_data | +0.0293 | 1 |

The entire net edge comes from the **28 full +2R targets**; the 91 EMA50
trend-break exits bleed −11.4R in aggregate (many small losers), and stops net
−29R. The asymmetry (capped +2R / −1R) is what makes the system positive — exactly
the designed profile.

---

## 6. Concentration diagnostics

| Metric | IS | OOS | Combined |
|---|---|---|---|
| Positive / negative years | 6 / 4 | 3 / 0 | 9 / 4 |
| Best year (share of total) | 2020 +4.82 (**63.0%**) | 2024 +4.93 (**61.7%**) | 2024 +4.93 (31.5%) |
| Worst year | 2016 −4.45 | 2023 +0.65 | 2016 −4.45 |
| Top quarter (share) | 2019-Q4 +4.37 (57.1%) | 2025-Q3 +3.0 (37.5%) | 2019-Q4 +4.37 (27.9%) |
| Top month (share) | 2013-12 +2.0 (26.1%) | 2023-11 +2.0 (25.0%) | 2013-12 +2.0 (12.8%) |
| IS total without top-2 years | — | — | **−1.4558** |

OOS contribution by year: 2023 +0.6547 · 2024 +4.9348 · 2025 +2.4094.

---

## 7. Verdict — **CONCENTRATED_SUPPORT**

The result is positive, but profit is **mostly from one/few periods** within each
window: IS best year = 63% of IS net (and IS is **negative** without its top-2
years); OOS best year = 62% of OOS net. The headline verdict is judged on
**per-window** concentration — the combined best-year share (31.5%) is descriptive
only and dilutes within-window concentration, so it is **not** used for the label.

**What IS broad:** the regime dimensions. Profit spans all three trend-strength
terciles and both low/mid-volatility regimes, and is present in both clustered and
spaced entries. So the edge is not tied to a single regime — but it *is* tied to a
few strong calendar periods, and it **fails in high volatility** and during
multi-year chop (2014–2016).

This is consistent with D3 (marginal), D6 (entry edge inconclusive), and D7
(sequence-risk inconclusive): a real-but-thin edge that depends on catching a few
strong trending windows and avoiding high-vol regimes.

---

## 8. Interpretation & recommendation

- **Diagnostic only** — nothing here is tuned, and nothing may be tuned *from*
  this breakdown (no parameter changes, no new filters; that would be overfitting
  to the very data just inspected).
- **No paper/live recommendation. No promotion.**
- **Recommendation for S26-D9:** the pre-registered ladder's D9 is **multi-market
  robustness (MNQ/ES/MES) as fresh future OOS**. Given CONCENTRATED_SUPPORT plus
  the inconclusive D6/D7, D9 is the right next *characterization* step — does the
  same frozen rule survive on a different market as genuinely unseen OOS? Run it
  pre-registered and once, like D4/D5. A PASS there would be the first
  independent corroboration; anything weaker confirms the edge is too thin/regime-
  bound to pursue. Do **not** deploy on the strength of a single-market in-sample-
  flattered window.

---

### Notes of record
- Trades regenerated only (engine run once per window); engine/tests unchanged; no
  optimization, no parameter changes, no new variants.
- The D8 verdict classifier was written to judge per-window concentration; the raw
  combined metrics are retained in `report.json` for transparency.
- IS/OOS kept separate; combined is descriptive only. Donchian untouched.
