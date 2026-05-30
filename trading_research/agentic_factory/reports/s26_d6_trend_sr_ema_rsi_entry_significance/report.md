# S26-D6 — Entry-Rule Significance: Trend + S/R + EMA/RSI signals

**Tests whether the FROZEN S26 entry signal carries edge versus same-count random
entries — separately on IS and OOS. NOT a new backtest, NOT optimization, NOT a
strategy change. Engine and significance module used UNCHANGED.**

- **Created:** 2026-05-29 · **Direction:** LONG-ONLY · **Market:** NQ daily

| Frozen artifact | Commit |
|---|---|
| S26-D1 spec | `af643aef58c63dd3bd904b4fb44406f4a2a55c3e` |
| S26-D2 engine | `1b1174e37c377b6331fa480a96115f286fb6a246` |
| S26-D3 IS baseline | `1bb70f9c3961cf4435d7953a69e06989f11a5dbb` |
| S26-D4 OOS protocol | `a5d90c63aa11f5c275fec4cae993ba6ab4ccb85f` |
| S26-D5 OOS PASS | `30f2190b8ced3cb08c3758d7da7215a9c36feb68` |

---

## 1. Data files used

- **IS:** `data_offline/nq_c0_ohlcv_1d_2013.csv` … `…_2022.csv` (10 files; 3079
  bars).
- **OOS:** `data_offline/nq_c0_ohlcv_1d_2023.csv`, `…_2024.csv`, `…_2025.csv` (3
  files; 934 bars).
- IS and OOS streamed separately (hard assertion: no file overlap). No pooling.

---

## 2. Signal extraction method

- **Signal logic:** the exact frozen S26 `long_signal_indices` — `close>EMA200`
  AND `EMA50>EMA200`; `low <= 20-day rolling low (excl. current) + 1.5*ATR20`;
  `40 <= RSI14 <= 55`; `RSI14[i] > RSI14[i-1]` OR `close > EMA20`.
- **Forward-return anchor — engine-consistent + conservative:** the engine fills
  at **open[i+1]**; the significance module is close-based. Forward returns are
  measured from the **entry/fill bar (signal_index+1), close[i+1] →
  close[i+1+horizon]**. This anchors on the *same bar* as the real fill, is
  lookahead-safe (the position is already open by close[i+1]), and does **not**
  credit the un-tradeable signal-close → next-open gap.
  - *Limitation:* close[i+1] is a proxy for the actual open[i+1] fill price.
- **Random baseline:** same-count random entries drawn (without replacement) from
  all indices with a full forward window; close-to-close; fully seeded.
- **n_iter:** 5000 · **seeds:** IS 2606, OOS 2607.

Raw signal counts: **IS 195**, **OOS 50** (each → that many usable entries before
per-horizon end-of-data trimming).

---

## 3. IS significance (2013–2022, seed 2606, 5000 draws)

| Horizon | n | Real mean | Random mean | Percentile | p-value | Module verdict |
|---|---|---|---|---|---|---|
| 5 | 195 | +0.00311 | +0.00257 | 62.7 | 0.3733 | INCONCLUSIVE |
| 10 | 195 | +0.00659 | +0.00513 | 72.7 | 0.2727 | INCONCLUSIVE |
| 20 | 195 | +0.01284 | +0.01039 | 78.4 | 0.2166 | INCONCLUSIVE |
| 40 | 195 | +0.02056 | +0.02105 | 45.8 | 0.5425 | **NO_EDGE** |

IS real entries beat random in *direction* at horizons 5/10/20 (percentiles
63–78) but never reach significance; at h=40 they slightly underperform random.

---

## 4. OOS significance (2023–2025, seed 2607, 5000 draws)

| Horizon | n | Real mean | Random mean | Percentile | p-value | Module verdict |
|---|---|---|---|---|---|---|
| 5 | 50 | +0.00806 | +0.00490 | 83.0 | 0.1698 | INCONCLUSIVE |
| 10 | 48 | +0.01937 | +0.00971 | 98.3 | 0.0168 | **EDGE_LIKELY** |
| 20 | 47 | +0.02222 | +0.01880 | 70.1 | 0.2991 | INCONCLUSIVE |
| 40 | 41 | +0.04186 | +0.03624 | 72.6 | 0.2741 | INCONCLUSIVE |

OOS real entries beat random in *direction* at every horizon, and clear
significance at **h=10** (p=0.0168, 98th percentile).

---

## 5. Verdict — **ENTRY_EDGE_INCONCLUSIVE**

**Why not SUPPORTED:** SUPPORTED requires strong evidence (an EDGE_LIKELY horizon)
on **both** IS and OOS. **IS has zero EDGE_LIKELY horizons** — the signal tilts
positive but never clears p≤0.05, and at h=40 it is indistinguishable from random.

**Why not NOT_SUPPORTED:** the real entries are **not worse than random** — they
beat the random baseline in direction on 7 of 8 horizon-side cells, and OOS h=10
is genuinely significant. This is materially better than Donchian (S24), whose
breakout entries were NO_EDGE at all horizons IS *and* OOS. The S26 pullback entry
clears the Donchian NOT_SUPPORTED bar; it just does not earn SUPPORTED.

**Net reading:** a weak, consistent positive entry tilt that reaches statistical
significance only in one OOS horizon. The single OOS EDGE_LIKELY at h=10 should not
be over-read (one of eight cells; multiple-comparison risk; OOS n is small).

---

## 6. Interpretation (pre-fixed)

- **SUPPORTED** (not reached) would authorize S26-D7 Monte Carlo / sequence-risk.
- **INCONCLUSIVE** (this result) means continue **cautiously** and only if the OOS
  PASS (S26-D5) and the risk tests (S26-D7) genuinely justify it — not on the
  entry edge alone.
- **NOT_SUPPORTED** (not reached) would mean full-strategy profit is likely
  exit/management/regime luck and the branch should not be promoted.
- **None of this means live or paper trading.**

---

### Notes of record
- Engine and `signal_significance.py` unchanged; no optimization; no parameter or
  rule changes; no OOS rerun variants.
- IS and OOS kept separate; no pooling. Donchian untouched.
- `_signals.json` (raw signal/entry indices) is a generated artifact — left
  untracked.
