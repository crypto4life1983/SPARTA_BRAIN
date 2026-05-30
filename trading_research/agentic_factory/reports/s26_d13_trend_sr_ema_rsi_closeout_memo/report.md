# S26-D13 — S26 Closeout & Research-Readiness Memo

**Final closeout memo for the S26 "Trend + Support/Resistance + EMA/RSI" (long-only v1)
branch. MEMO ONLY — summarizes the committed S26 decision records and gives a disciplined
next-step recommendation. No new backtest, no new market test, no optimization, no strategy
rule change, no source/engine/test change.**

- **Created:** 2026-05-30 · **Reference commit:** `cfe841d` (S26-D12
  PARTIAL_SUPPORT_WITH_CAUTION)
- **Frozen engine:** `engine/trend_sr_ema_rsi_daily.py` — UNCHANGED.
- Sources summarized (committed reports only): S26-D1, D3, D4, D5, D6, D12. Analysis was
  **not** re-run.

---

## 1. Branch summary

- **Strategy:** Trend + support/retest + EMA/RSI confirmation (buy a controlled pullback
  toward recent support inside an established daily uptrend).
- **Market origin:** NQ continuous daily bars.
- **Direction:** long-only (v1).
- **Accounting:** R-only (1R = 2N stop distance).
- **No pyramiding** — one position at a time, flat-state entries only.
- **Fixed rules (pre-registered in S26-D1):** `close>EMA200` AND `EMA50>EMA200`;
  `low <= 20-day rolling low (excl. current) + 1.5*ATR20`; `40 <= RSI14 <= 55` AND
  (`RSI14[i] > RSI14[i-1]` OR `close > EMA20`); fill next-bar open; stop `entry − 2*ATR20`
  (1R = 2N); target +2R; EMA50 close-break backstop; exit precedence stop → target →
  ema50_break.

## 2. Why this branch was created

Donchian was conclusively parked across three steps:

| Step | Verdict | Weakness |
|---|---|---|
| S23 | **WATCH** | Made money IS+OOS but OOS n=16 too small → not deployable. |
| S24 | **ENTRY_EDGE_NOT_SUPPORTED** | Breakout entries fire *after* an extended move → NO_EDGE at all horizons, IS & OOS. |
| S25 | **SEQUENCE_RISK_FRAGILE** | Removing top-3 trades flips IS (−3.82R) and OOS (−1.93R) negative; OOS best trade = 50.3% of net. |

S26 was created to directly avoid those weaknesses:
- **Less winner dependence** via a capped **+2R** target that distributes outcomes.
- **More trades** than Donchian.
- **Pullback/retest** toward support instead of breakout-only entry — the opposite of the
  entry edge that was NOT_SUPPORTED.
- **Capped +2R target** as the deliberate antidote to single-winner dependence.

## 3. S26 evidence chain

| Step | Result |
|---|---|
| **D1** | Spec pre-registered (hypothesis, fixed rules, ladder, PASS/WATCH/FAIL gates). |
| **D2** | Engine + unit tests committed in new files (Donchian source untouched). |
| **D3** | IS baseline 2013–2022 → **IS_CONTINUE** (marginal). |
| **D4** | Sealed OOS protocol pre-registered and committed **before** any OOS run. |
| **D5** | OOS 2023–2025 run **once** → **PASS** (all 8 gates met; no WATCH/FAIL). |
| **D6** | Entry-rule significance → **ENTRY_EDGE_INCONCLUSIVE**. |
| **D11** | Multi-market data provisioned (ES/MES/MNQ from Databento). |
| **D12** | Multi-market robustness (frozen run) → **PARTIAL_SUPPORT_WITH_CAUTION**. |

*(Intermediate steps for completeness: D7 SEQUENCE_RISK_INCONCLUSIVE, D8
CONCENTRATED_SUPPORT, D9 DATA_LIMITED_INCONCLUSIVE, D10 PROTOCOL_REGISTERED.)*

## 4. Key metrics

**NQ IS (2013–2022):**
- 117 trades · **+7.6536R** · PF **1.2016** · expectancy **+0.0654R/trade** · max DD
  **10.5943R** · best-trade share **26.1%** · without top-3 **+1.6536R** · 6/10 positive
  years.

**NQ OOS (2023–2025):**
- 32 trades · **+7.9990R** · PF **1.7694** · expectancy **+0.2500R/trade** · max DD
  **2.1827R** · **3/3 positive years** · without top-3 **+1.9990R**.

**Entry significance:** **ENTRY_EDGE_INCONCLUSIVE** (positive tilt; no EDGE_LIKELY horizon
on IS; one significant OOS horizon at h=10, not to be over-read).

**Multi-market (D12):**
- **ES (independent S&P market) confirms direction, with caution:**
  - ES IS: **+7.6725R**, PF **1.2003**, max DD **16.7281R**.
  - ES OOS: **+11.4584R**, PF **2.2352**, max DD **2.0697R**.
- **MES / MNQ corroborate as proxy/micro only** (same underlying — MNQ↔NQ, MES↔ES — not
  independent markets).
- **Final D12 verdict: PARTIAL_SUPPORT_WITH_CAUTION.**

## 5. Final S26 verdict

- **S26 is the strongest candidate so far.**
- **S26 is research-promising.**
- **S26 is NOT deployable.**
- **S26 is NOT paper-ready yet.**
- **S26 should continue validation, but only under strict guardrails.**

## 6. Main weaknesses

- IS expectancy is thin (+0.0654R/trade; PF 1.20 marginal).
- IS max DD (10.59R) is high relative to total R (7.65R).
- Entry significance is inconclusive.
- ES IS max DD (16.73R) is high (exceeds 1.5× NQ IS DD).
- ES OOS has only 27 trades (< 30) and is 2025-dominated (72.8% of net).
- Multi-market support is partial, not robust.
- Only one independent extra market beyond NQ (the S&P via ES).

## 7. Correct next steps (in order)

- **A. S26-D14** — formal risk/readiness gate design, **still no paper trading**.
- **B. S26-D15** — regime breakdown across NQ and ES.
- **C. S26-D16** — walk-forward / rolling-window stability.
- **D. S26-D17** — execution realism / slippage and commission stress.
- **E.** Only after those, consider a **separate paper-readiness memo**.

## 8. Forbidden next steps

- Do not optimize parameters.
- Do not add filters based on OOS.
- Do not paper trade yet.
- Do not deploy.
- Do not market it as a profitable bot.
- Do not mix this with Donchian.

## 9. Final line

**S26 remains a research candidate with partial independent support, not a deployable
trading system.**

---

### Notes of record
- Memo only — built from the committed S26 decision records (D1/D3/D4/D5/D6/D12). No analysis
  re-run, no backtest, no market test, no optimization, no parameter/rule/source/engine/test
  change.
- Donchian/S23/S24/S25 untouched. `templates/base.html` is unrelated pre-existing repo-level
  drift and was not touched.
- Nothing staged, nothing committed by this step.
