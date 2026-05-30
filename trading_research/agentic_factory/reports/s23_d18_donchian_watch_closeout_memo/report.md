# S23-D18 — Donchian WATCH Closeout Memo

**This is a closeout record, not a new backtest.** It summarizes the S23 frozen
Donchian NQ-only daily baseline discovery branch and its final verdict.

- **Created:** 2026-05-29
- **Frozen params:** entry 55 / exit 20 / ATR 20 / stop 2.0 / no pyramiding / R-only
- **D15 protocol commit (pre-registered before OOS):** `18349fa`

---

## 1. S23 chain summary

| Step | What it did |
|---|---|
| **D13** | Transcoded local Databento-native NQ 2014–2022 into module-local daily CSVs (IS data prep). |
| **D14** | Ran the frozen daily Donchian baseline over the full **2013–2022 IS** window (continuous stream). |
| **D15** | **Pre-registered the OOS validation protocol and committed it (`18349fa`) BEFORE any OOS data was seen.** |
| **D16** | Transcoded sealed **2023–2025 OOS** data into daily CSVs; all years structural-QA PASS. |
| **D17** | Ran the frozen Donchian engine exactly **ONCE** over 2023–2025 and judged strictly against D15. |

---

## 2. In-sample result (2013–2022)

| Metric | Value |
|---|---|
| Trades | 66 |
| Total R | +10.5421 R |
| Profit factor | 1.31 |
| Win rate | 42.4% |
| Expectancy | +0.16 R/trade |
| Max drawdown | 6.34 R |
| Years | 5 positive / 5 negative |

---

## 3. Out-of-sample result (2023–2025)

| Metric | Value |
|---|---|
| Trades | 16 |
| Total R | +11.37 R |
| Profit factor | 2.41 |
| Win rate | 43.8% |
| Expectancy | +0.71 R/trade |
| Max drawdown | 3.00 R |
| Years | 3 positive / 0 negative |
| Best trade | +5.72 R |
| Worst trade | −1.0 R |
| Best-trade share of net | 50.3% |

---

## 4. Final S23 verdict — **WATCH**

Economics are green: expectancy > 0, PF > 1.05, max DD within 1.5× IS, at least
one positive year, no single trade over 80% of net, no data defect — and **no
FAIL trigger fires**. But the committed D15 protocol lists *"OOS trade count too
small for confidence"* as a WATCH trigger, and at **n = 16** that trigger is
live. Under the protocol's strict precedence (FAIL → WATCH → PASS), a live WATCH
trigger holds the verdict at **WATCH** even with every economic gate green.

**Reason:** economics are green, but OOS trade count is too small for confidence.

---

## 5. What WATCH means

- Do **not** trade live.
- Do **not** paper-promote yet.
- Do **not** optimize against OOS.
- Do **not** add filters using 2023–2025 data.

---

## 6. Correct next steps

- **S24** entry-rule significance on the frozen signals (`signal_significance`, currently parked).
- Trade-order Monte Carlo.
- Drawdown sequence-risk Monte Carlo.
- Wider evidence base / multi-market test (as fresh future OOS, not re-using 2023–2025).
- Regime breakdown.

---

## 7. Anti-overfit warning

This result is **promising but still fragile**: the OOS trade count is low
(n = 16) and the strategy is a trend-follower whose net result leans on a few
large winners (best trade alone = 50.3% of OOS net). Three strong OOS years are
encouraging, not conclusive — do not over-read them.

---

## 8. Final line

**S23 is complete as a frozen Donchian baseline discovery branch. It produced a
WATCH candidate, not a deployable strategy.**

---

### Commits of record
- D15 OOS protocol (pre-registration): `18349fa`
- D14 IS-baseline ignore: `4deb36b`
- D16/D17 OOS ignore: `81c4a64`
