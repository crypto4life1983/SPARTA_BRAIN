# S26-D1 — Strategy Hypothesis Spec: Trend + Support/Resistance + EMA/RSI

**SPEC ONLY — pre-registration. No engine, no backtest, no results, no
optimization.** No code for this branch exists yet.

- **Created:** 2026-05-29
- **Branch label:** `trend_sr_ema_rsi_v1`
- **Market (v1):** NQ continuous daily bars · **Direction (v1):** LONG-ONLY
- **Accounting:** R-only (1R = 2N stop distance)

---

## 1. Why Donchian was parked

| Step | Verdict | Lesson the new branch must respect |
|---|---|---|
| S23 | **WATCH** | System made money IS+OOS but OOS n=16 too small → not deployable. |
| S24 | **ENTRY_EDGE_NOT_SUPPORTED** | Breakout entries fire *after* an extended move → mean-reversion drag; NO_EDGE at all horizons, IS & OOS. |
| S25 | **SEQUENCE_RISK_FRAGILE** | Removing top-3 trades flips IS (−3.82R) and OOS (−1.93R) negative; OOS best trade = 50.3% of net; realized DD at ~11th pct of shuffles; IS bootstrap ~21% prob of ≤0. |

**Design responses, one per weakness:**
1. **Weak entry edge →** enter on a **pullback/retest toward support**, the
   opposite of breakout extension.
2. **Few-winner dependence →** **fixed 2R take-profit** to distribute outcomes,
   plus an explicit *no top-3 dependence* PASS gate.
3. **Sequence fragility →** require **D7 sequence-risk ≠ FRAGILE** as a gate.
4. **Low OOS n →** pre-fix **min trade thresholds** (IS ≥ 40, OOS ≥ 30); a
   sub-threshold OOS is an automatic WATCH.

---

## 2. New hypothesis

> In an established daily uptrend, a controlled pullback toward recent support
> that shows momentum stabilizing (RSI in a mid band, then turning up or price
> reclaiming EMA20) offers a positive-expectancy, **distributed-outcome** long
> entry, with risk fixed at 2N and reward capped at 2R.

The hypothesized edge is in **buying the retest** (mean-reversion-into-trend) —
deliberately the opposite of Donchian's breakout entry, whose edge was not
supported. **Long-only v1** to minimize degrees of freedom; symmetric short is a
later branch with its own fresh OOS, only if v1 survives.

---

## 3. Exact fixed rules

**Indicators (all Wilder/standard, prior-bar-only, lookahead-safe):**
EMA20, EMA50, EMA200, RSI(14), ATR(20). Support reference = **rolling 20-day low**
= lowest low over `bars[i-20:i]` (excludes current bar). Warmup: no signal until
`i ≥ 200` and ATR/RSI seeded.

**Support method — chosen: Option B (rolling 20-day low).** Rejected A (swing
pivots — needs fractal detection, more DOF) and C (rolling pivots — needs
lookback+lookforward, extra params + lookahead risk). Option B is fully
deterministic, parameter-light, lookahead-safe, and needs no subjective drawing.
*Note:* this reuses a Donchian-style level only as a **support reference** — the
entry buys a pullback *toward* it, not a breakout *above* it, so it does not
inherit Donchian's NOT_SUPPORTED entry edge.

**Entry (LONG) — all conditions must hold on signal bar `i`:**
- **C1 Trend:** `close[i] > EMA200[i]` AND `EMA50[i] > EMA200[i]`
- **C2 Support proximity:** `low[i] <= support_ref[i] + 1.5*ATR20[i]` (price
  retraced to within 1.5 ATR of the prior 20-day low)
- **C3 RSI band:** `40 <= RSI14[i] <= 55`
- **C4 Confirmation:** `RSI14[i] > RSI14[i-1]` **OR** `close[i] > EMA20[i]`
- **Execution:** fill at **next bar (i+1) OPEN**. No subjective inputs.

**Stop (one fixed rule):** `stop = entry − 2.0*ATR20[i]`. **1R = 2N.** Checked
intrabar on bar low, management starts the bar after entry, stop checked before
target. (Support-minus-buffer alt rejected to keep a clean constant 1R.)

**Exit:**
- **Primary:** fixed **+2R** target (`entry + 2R`, where 1R = 2N).
- **Risk:** hard stop at **−1R**.
- **Backstop:** if still open at a bar **close** and `close < EMA50`, exit at that
  close (trend invalidation).
- **Precedence per bar:** (1) −1R hard stop intrabar → (2) +2R target intrabar →
  (3) EMA50 close-exit if still open.
- **Why capped:** the 2R cap is the deliberate antidote to S25 single-winner
  dependence — it distributes outcomes rather than relying on rare runners. This
  intentionally tests a *different* edge than Donchian's let-winners-run profile.

**Risk/accounting:** R-only · no compounding · no pyramiding · one position at a
time · flat-state entries only.

---

## 4. Data windows

- **IS:** 2013–2022   **OOS:** 2023–2025.
- OOS **sealed/unseen** until the D4 protocol is committed.
- Same anti-overfit rule as S23: **no parameter changes after OOS**, run OOS once,
  no subperiod cherry-picking.

---

## 5. Validation ladder

| Step | What |
|---|---|
| **D2** | Implement engine + tests in NEW files (do **not** modify Donchian source). |
| **D3** | Run IS 2013–2022 baseline (single continuous stream). |
| **D4** | Pre-register the sealed OOS protocol and **commit it before any OOS run** (mirror S23-D15). |
| **D5** | Run OOS 2023–2025 exactly **once**, judged strictly against D4. |
| **D6** | Entry-rule significance (reuse `signal_significance`). Must clear the NOT_SUPPORTED bar. |
| **D7** | Trade-order Monte Carlo + bootstrap sequence-risk (mirror S25). Must clear FRAGILE. |
| **D8** | Regime breakdown (trend vs chop / by year / by volatility). |
| **D9** | Multi-market robustness (MNQ/ES/MES) as fresh future OOS — only if it survives D5–D8. |

---

## 6. Pass / Watch / Fail criteria (pre-fixed, precedence FAIL → WATCH → PASS)

**Trade-count gates:** IS ≥ 40 (prefer ≥ 60); OOS ≥ 30. OOS in 1–29 → automatic
WATCH (the exact trigger that held Donchian at WATCH — not repeating it silently).

**PASS — all must hold:**
- IS ≥ 40 AND OOS ≥ 30 trades
- OOS expectancy > 0
- OOS profit factor ≥ 1.20
- OOS max DD ≤ 1.5× IS max DD
- majority of IS years positive AND ≥ 1 positive OOS year
- **OOS total R stays positive after removing the top 3 winners**
- D6 entry significance **≠ NOT_SUPPORTED**
- D7 sequence risk **≠ FRAGILE**
- no data-QA defect

**WATCH — any trigger:** OOS 1–29 trades · PF 1.05–1.20 · expectancy 0..+0.05R ·
top-3 removal only marginally positive · one year dominates · D6 INCONCLUSIVE.

**FAIL — any trigger:** OOS expectancy ≤ 0 · PF < 1.05 · OOS max DD materially >
1.5× IS without recovery · **top-3 removal flips OOS negative** (the Donchian S25
failure) · D6 NOT_SUPPORTED · D7 FRAGILE · all OOS years negative · structural
data issue.

---

## 7. Anti-overfit guardrails

- No parameter sweeps in v1 — every constant above is **fixed before testing**.
- No changing the Option-B support definition after seeing results.
- No adding filters after OOS; no tuning RSI band / ATR multiple / EMA lengths /
  target to results.
- If a change is genuinely needed → **new branch + fresh pre-registered OOS**,
  never a retrofit of this one.
- IS and OOS kept separate; no pooling. Donchian source/reports/verdicts untouched.

---

## 8. Proposed next implementation step

**S26-D2:** implement the engine and unit tests in **new** module files (e.g.
`engine/trend_sr_ema_rsi.py` + tests), without touching any Donchian source. No
backtest results in D2 beyond test fixtures.

---

## 9. Clear line

**No backtest has been run. This is a pre-registered hypothesis/specification
only.** No engine code for this branch exists yet. No optimization, no results,
no trading or paper-promotion claims.
