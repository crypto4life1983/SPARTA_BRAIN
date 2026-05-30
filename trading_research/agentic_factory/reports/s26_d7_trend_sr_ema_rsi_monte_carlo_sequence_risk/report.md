# S26-D7 — Monte Carlo / Sequence-Risk: Trend + S/R + EMA/RSI

**Fragility stress of the ALREADY-RECORDED S26 trade results under trade-order
shuffle + bootstrap resampling. NOT a new strategy test, NOT optimization, NOT a
parameter change.** The frozen engine was run once per window only to *regenerate*
the realized R-lists; counts/totals were asserted against the committed D3/D5
reports before any stress was applied.

- **Created:** 2026-05-29 · **Direction:** LONG-ONLY · **Market:** NQ daily
- **n_iter:** 10000 · **seeds:** IS 2671, OOS 2672, combined 2673 (bootstrap uses
  seed+500).

## S26 context

| Step | Commit | Result |
|---|---|---|
| D1 spec | `af643ae` | pre-registered |
| D2 engine | `1b1174e` | implemented |
| D3 IS baseline | `1bb70f9` | IS_CONTINUE (marginal) |
| D4 OOS protocol | `a5d90c6` | pre-registered |
| D5 OOS run | `30f2190` | **OOS PASS** |
| D6 entry significance | `cc73d6a` | ENTRY_EDGE_INCONCLUSIVE |

---

## 1. Trade sources & R-list summary

R-lists **regenerated** via the frozen S26-D2 engine, run once per window, ordered
by exit date. Asserted equal to the committed reports (proves same frozen result):

| Set | Count | Total R |
|---|---|---|
| IS 2013–2022 | 117 | +7.6536 |
| OOS 2023–2025 | 32 | +7.9990 |
| Combined 2013–2025 *(descriptive only)* | 149 | +15.6526 |

Combined is **descriptive only — not additional OOS proof.**

---

## 2. Trade-order shuffle MC (total R fixed; path risk)

| Metric | IS | OOS | Combined |
|---|---|---|---|
| Realized max DD (R) | 10.5943 | 2.1827 | 10.5943 |
| Shuffled median max DD | 7.9879 | 3.5366 | 8.0319 |
| Shuffled p90 | 11.5679 | 5.2123 | 11.5263 |
| Shuffled p95 | 12.6463 | 5.7786 | 12.8311 |
| Shuffled p99 | 15.0067 | 6.8776 | 15.4947 |
| **Realized DD percentile** | **83.67** | **5.21** | 84.00 |
| Realized longest losing streak | 6 | 4 | 6 |

- **IS realized DD sits at the 84th percentile of shuffles** — the realized order
  was *rougher* than median, not flattered by ordering luck. (This is the opposite
  of Donchian S25, whose gentle realized path was ~11th-percentile luck.)
- **OOS realized DD is at the 5th percentile** — the realized OOS path was
  unusually *shallow*; a typical reordering shows a deeper median DD (3.54R vs
  realized 2.18R). The OOS 2.18R max DD is therefore ordering-flattered and should
  not be read as a robust ceiling.

---

## 3. Bootstrap resample MC (expectancy fragility)

| Metric | IS | OOS | Combined |
|---|---|---|---|
| **P(total R ≤ 0)** | **0.2389** | **0.1025** | 0.1020 |
| Median total R | 7.4197 | 7.9231 | 15.3216 |
| 5th pct total R | −9.7706 | −2.3159 | −4.4899 |
| 95th pct total R | 25.0847 | 18.6012 | 36.2968 |
| Median max DD | 8.2624 | 3.5933 | 8.2682 |
| 95th pct max DD | 16.7574 | 7.4198 | 15.8477 |
| P(max DD > IS realized 10.59R) | 0.2772 | 0.0052 | 0.2648 |
| P(max DD > 1.5× IS, 15.89R) | 0.0624 | 0.0000 | 0.0492 |

- **IS bootstrap P(total R ≤ 0) = 23.9%** — roughly a 1-in-4 chance the IS edge
  resamples to a non-positive total. This directly reflects the marginal IS edge
  (PF 1.20) and is the main reason this is not clean-ACCEPTABLE.
- OOS bootstrap is healthier (P≤0 = 10.3%) but rests on only 32 trades.

---

## 4. Winner-dependence

| Metric | IS | OOS | Combined |
|---|---|---|---|
| Best trade | +2.0 | +2.0 | +2.0 |
| Best-trade share of net | 26.1% | 25.0% | 12.8% |
| Top-3 share of net | 78.4% | 75.0% | 38.3% |
| Total without best | +5.6536 | +5.9990 | +13.6526 |
| Total without top-3 | +1.6536 | +1.9990 | +9.6526 |
| **Positive without top-3?** | **yes** | **yes** | **yes** |

**Low winner-dependence — every set stays positive after removing the top 3
winners.** This is the clearest improvement over Donchian S25, where top-3 removal
flipped both IS (−3.82R) and OOS (−1.93R) negative. The capped +2R target did its
job of distributing outcomes.

---

## 5. Loss-cluster / pain

| Metric | IS | OOS | Combined |
|---|---|---|---|
| Longest losing streak | 6 | 4 | 6 |
| Worst 3-trade window (R) | −2.5165 | −1.9684 | −2.5165 |
| Worst 5-trade window (R) | −3.9537 | −2.0643 | −3.9537 |
| Worst 10-trade window (R) | −4.9863 | −1.4760 | −4.9863 |
| Realized max DD (R) | 10.5943 | 2.1827 | 10.5943 |

---

## 6. Verdict — **SEQUENCE_RISK_INCONCLUSIVE**

- **Not FRAGILE:** no fragility flag fired. Both IS and OOS stay **positive without
  the top-3 winners**; IS bootstrap P≤0 (23.9%) is below the 25% fragility line;
  realized DDs are not in the extreme (≥95th pct) shuffle tail. This is a
  materially stronger result than Donchian S25 (which *was* FRAGILE).
- **Not ACCEPTABLE:** two reservations keep it short of clean-acceptable —
  (1) **IS bootstrap P(total R ≤ 0) = 23.9%** is elevated (the marginal IS edge
  showing through), and (2) **OOS n = 32 is a small sample**, so its more
  favorable risk metrics are noisy.

---

## 7. Conservative interpretation

- **OOS sample is small (32 trades)** — its sequence-risk metrics are noisy and
  must not be over-read; the shallow realized OOS DD (5th pct) is partly ordering
  luck.
- **OOS PASS (D5) does not erase the IS bootstrap fragility.** ~1-in-4 IS
  resamples are non-positive; the PASS should be held with that in mind.
- **Winner-dependence is genuinely low** and bootstrap DD risk is contained
  (P(DD > 1.5× IS) ≈ 5–6%), which supports *continuing validation* — not
  deployment.
- **No trading recommendation. No paper or live promotion.**

---

## 8. Recommendation

Verdict is **INCONCLUSIVE**, so: **continue cautiously, or widen the evidence**
(e.g. let OOS accrue more trades over time, and proceed to S26-D8 regime breakdown
only to *characterize* where the edge lives — not to tune it). Do **not** promote.
If future evidence weakens, park the branch or open a new one with a fresh
protocol. A jump straight to deployment is not justified.

---

### Notes of record
- R-lists regenerated only (engine run once per window); engine/tests unchanged;
  no optimization, no parameter changes, no OOS rerun variants.
- IS/OOS kept separate; combined is descriptive only. Donchian untouched.
- `_mc_raw.json` (regenerated R-lists) is a generated artifact — left untracked.
