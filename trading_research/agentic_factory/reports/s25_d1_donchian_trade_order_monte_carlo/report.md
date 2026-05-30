# S25-D1 — Donchian Trade-Order Monte Carlo & Drawdown Sequence-Risk

**This is a sequence-risk validation, not a new backtest and not optimization.**
It resamples the *frozen* realized R-multiple lists from S23 to characterize how
fragile or lucky the realized trade sequence is. No engine, data, parameter, or
strategy logic was changed. The engine was **not** rerun — exact R-lists were
read from the existing local `_run.json` outputs.

- **Created:** 2026-05-29
- **Frozen params:** entry 55 / exit 20 / ATR 20 / stop 2.0 / no pyramiding / R-only

---

## 1. S23 context

- **Final S23 verdict: WATCH.** The full Donchian system was positive both IS
  (+10.54R) and OOS (+11.37R), but OOS had only **16 trades** — too small for
  confidence. **Not deployable.**

## 2. S24 context

- **ENTRY_EDGE_NOT_SUPPORTED.** The raw entry rule shows no predictive edge vs
  random-entry darts. **Therefore S25 cannot upgrade this candidate to deployable
  or paper status.** S25 only measures sequence fragility/luck.

---

## 3. Trade sources (exact)

| Set | Source | Count | Total R |
|---|---|---|---|
| IS 2013-2022 | `s23_d14_.../_run.json` `trades[].r_multiple` (git-ignored) | 66 | +10.5421 |
| OOS 2023-2025 | `s23_d17_.../_run.json` `trades[].r_multiple` (git-ignored) | 16 | +11.3738 |
| Combined 2013-2025 (descriptive only) | IS + OOS concatenated chronologically | 82 | +21.9160 |

Engine rerun: **No.** Frozen R-lists were already present locally.

---

## 4. Monte Carlo settings

- Trade-order shuffle: n_iter = 10000. Seeds: IS 2501, OOS 2502, combined 2503.
- Bootstrap resample (with replacement, same length): n_iter = 10000. Same per-set
  seeds (separate independent RNG draw).
- IS realized max DD reference for DD-tail probabilities: **6.34 R**.

---

## 5. Trade-order shuffle (path risk; total R is invariant)

| Metric | IS | OOS | Combined |
|---|---|---|---|
| Realized max DD (R) | 6.34 | 3.00 | 6.34 |
| Shuffle max DD median (R) | 8.78 | 3.05 | 8.78 |
| Shuffle max DD p95 (R) | 14.02 | 5.98 | 14.18 |
| Shuffle max DD p99 (R) | 16.96 | 7.00 | 16.63 |
| Realized-DD percentile vs shuffle | 11.1% | 30.0% | 10.8% |
| Longest losing streak (realized) | 5 | 3 | 5 |
| Longest losing streak p95 | 10 | 6 | 10 |
| Worst 10-trade window realized (R) | -5.88 | +3.34 | -5.88 |
| Worst 10-trade window p05 (R) | -8.91 | -3.20 | -9.05 |

**Read:** the realized path was *gentler than typical*. In IS and combined the
realized drawdown sits near the ~11th percentile of shuffles — i.e. most
re-orderings of the very same trades produce a **worse** drawdown (p95 ~14R, more
than 2x the realized 6.34R). The same total R can deliver materially deeper pain
under a different order. This is path luck, not robustness.

---

## 6. Bootstrap resample (expectancy fragility under same trade distribution)

| Metric | IS | OOS | Combined |
|---|---|---|---|
| Prob(total R <= 0) | **20.9%** | 8.4% | 8.0% |
| Median total R | 10.17 | 11.08 | 21.48 |
| p05 total R | -10.17 | -1.98 | -3.36 |
| p95 total R | 32.94 | 26.71 | 49.27 |
| Median max DD (R) | 9.00 | 3.10 | 8.91 |
| p95 max DD (R) | 18.15 | 7.05 | 17.45 |
| Prob(max DD > IS 6.34R) | 81.4% | 8.3% | 82.1% |
| Prob(max DD > 1.5x IS = 9.51R) | 44.3% | 1.0% | 43.1% |

**Read:** under resampling of its own trade distribution, **IS has a ~21% chance
of finishing at or below break-even**, and a ~44% chance of a drawdown worse than
1.5x the realized IS max DD. That is a fragile expectancy. OOS looks cleaner
(8.4% prob <=0) but rests on only 16 trades, so its tightness is not trustworthy.

---

## 7. Single-winner dependence

| Metric | IS | OOS | Combined |
|---|---|---|---|
| Best trade (R) | 6.85 | 5.72 | 6.85 |
| Best-trade share of net | 64.9% | **50.3%** | 31.2% |
| Top-3 share of net | 136.3% | 117.0% | 81.8% |
| Total R without best | +3.70 (still +) | +5.66 (still +) | +15.07 (still +) |
| Total R without top 3 | **-3.82 (negative)** | **-1.93 (negative)** | +3.99 (still +) |

**Read:** both IS and OOS go **negative once the top 3 trades are removed**
(top-3 share > 100% of net). OOS net is ~50% one trade. The system's profit is
concentrated in a handful of fat-tailed winners — consistent with S24's finding
that entry timing carries no edge; the money comes from a few large captured
trends, not from a repeatable per-trade advantage.

---

## 8. Loss-cluster / pain test

| Metric | IS | OOS | Combined |
|---|---|---|---|
| Longest losing streak | 5 | 3 | 5 |
| Worst 3-trade window (R) | -2.56 | -3.00 | -3.00 |
| Worst 5-trade window (R) | -4.10 | +0.24 | -4.10 |
| Worst 10-trade window (R) | -5.88 | +3.34 | -5.88 |
| Realized max DD (R) | 6.34 | 3.00 | 6.34 |

Realized drawdown is modest **only because of favorable ordering** (Section 5);
the shuffle tail shows the same trades could cluster into much deeper pain.

---

## 9. S25 verdict — **SEQUENCE_RISK_FRAGILE**

Fragility flags fired:

- IS bootstrap **prob(total R <= 0) = 20.9%** (>= 20% threshold).
- IS turns **non-positive when the top 3 trades are removed**.
- OOS **best trade is >= 50% of net** (single-winner dependence).

---

## 10. Conservative interpretation

- **OOS n = 16 is too small.** Its clean bootstrap (8% prob <=0) and shallow DD
  must **not** be overstated — small samples look tight by accident.
- **Single-winner dependence is the dominant risk.** Removing the top 3 trades
  flips both IS and OOS negative; OOS is half one trade.
- **Expectancy is fragile in-sample:** ~1-in-5 bootstrap paths end <= 0.
- **Drawdown tail is much worse than realized:** the realized 6.34R IS DD sits at
  ~11th percentile of shuffles (p95 ~14R, p99 ~17R). The gentle realized path was
  luck of ordering, not a structural property.

## 11. Final recommendation

- **Do NOT optimize Donchian** based on these results.
- **Do NOT trade or paper-promote.**
- S24 already established the entry edge is not supported; **S25 cannot change
  that** — it confirms the result is carried by a few winners and a lucky path.
- **Treat Donchian 55/20/20/2.0 as a parked reference baseline.**
- Move research effort toward a **stronger entry hypothesis with its own
  pre-registered OOS**.

---

### Notes of record
- Sequence-risk validation only; no engine rerun, no parameter change, no optimization.
- Trade R-lists sourced from frozen S23 local run outputs (git-ignored).
- Combined 2013-2025 is descriptive only and is **not** an OOS proof.
