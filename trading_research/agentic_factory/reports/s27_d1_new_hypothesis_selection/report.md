# S27-D1 — New Strategy Hypothesis Selection Memo

**Compares five candidate strategy hypotheses and selects exactly one next branch to test.
MEMO ONLY — no code, no backtest, no optimization, no data fetch, no change to S26/Donchian,
no paper/live. The selection is a research direction, not an authorization to build.**

- **Created:** 2026-05-30 · **HEAD:** `f180e96` (S26 parked)
- **Donchian:** PARKED. **S26 Trend + S/R + EMA/RSI:** PARK_CANDIDATE (parked).

---

## 1. Why we are choosing a new branch

S26 was the strongest candidate so far but did not reach paper-readiness because of six
documented weaknesses:

1. **Entry edge inconclusive** — the entry was never shown to add edge beyond the trend filter.
2. **Thin IS edge** — PF ≈1.20, expectancy ≈0.065R.
3. **Shared 2014–2016 NQ/ES weakness** — both markets collapsed together in the choppy,
   non-trending regime; no diversification.
4. **OOS partly single-year dominated** — NQ 2024 = 61.7%, ES 2025 = 72.8% of OOS net.
5. **Friction-sensitive full-history edge** — IS break-even only ~0.06R/trade; IS negative at
   0.10R.
6. **Only partial independent market support** — ES is the *only* independent market vs NQ.

**The selection criteria below are deliberately chosen to ATTACK these weaknesses, not to
re-discover them.**

## 2. Data reality (a hard constraint on what is testable now)

- **Daily provisioned:** NQ, ES, MNQ, MES (2013–2025; micros from 2019).
- **Independent underlyings available:** Nasdaq (NQ/MNQ) and S&P (ES/MES) — same two as S26.
- **Intraday bars:** NOT provisioned. **Other index underlyings (YM/Dow, RTY/Russell):** NOT
  provisioned.
- **Implication:** any hypothesis needing intraday data or a new independent underlying
  requires a **separately-authorized data fetch** before it can be tested. Hypotheses on daily
  NQ/ES are testable **immediately**, with full independent multi-market coverage and no new
  data.

## 3. Selection criteria

1. **Separable entry edge** — the entry is a discrete, measurable event that can be
   significance-tested *against* the regime filter (fixes weakness #1).
2. **Counter-cyclical or robust to the 2014–2016 choppy regime** (fixes #3).
3. **Friction headroom** — fewer, larger-R trades, not many marginal ones (fixes #5).
4. **Immediate independent multi-market testability on daily NQ/ES** (fixes #6, avoids a data
   fetch).
5. **Distinct mechanism from Donchian breakout and S26 trend-pullback** (avoids re-testing a
   parked family).

## 4. Candidate comparison

### Idea 1 — Volatility-confirmed trend continuation
- **Edge thesis:** continuation moves backed by expanding volatility persist further.
- **Trade count:** moderate · **Friction:** moderate · **Regime risk:** **HIGH** (same
  trending dependence as S26) · **Multi-market:** good · **Data:** none new.
- **Biggest failure mode:** re-discovers S26's trend dependence — entry significance
  inconclusive again, 2014–2016 collapse again.
- **Verdict: WEAK** — too close to the parked S26 family.

### Idea 2 — Opening range breakout with regime filter
- **Edge thesis:** intraday opening-range momentum, restricted to favorable days.
- **Trade count:** high · **Friction:** **HIGH** (tight intraday stops; most likely to FAIL
  friction stress) · **Regime risk:** new unmodeled intraday microstructure risk ·
  **Multi-market:** data-heavy · **Data:** **HEAVY — intraday bars not provisioned; needs a
  new data fetch and a new intraday engine.**
- **Biggest failure mode:** friction destroys the edge; large data/engine cost before any
  signal is visible.
- **Verdict: WEAK NOW** — blocked on data + worst-case friction profile (the exact weakness we
  are trying to escape).

### Idea 3 — Pullback with NQ/ES cross-confirmation
- **Edge thesis:** require both NQ and ES to confirm, to filter noise.
- **Trade count:** low · **Friction:** low–moderate · **Regime risk:** **HIGH** for the exact
  failure regime (both fell together 2014–2016) · **Multi-market:** **POOR by construction** ·
  **Data:** none new.
- **Critical flaw:** coupling NQ and ES into the *entry* consumes the only independent
  validation market — nothing independent remains to validate against, collapsing multi-market
  robustness testing. And cross-confirmation would **not** have avoided the shared 2014–2016
  collapse.
- **Verdict: REJECT** — breaks the validation methodology.

### Idea 4 — Mean reversion after overextension inside a bull trend  ★ SELECTED
- **Edge thesis:** within an established uptrend (e.g. `close>EMA200`), enter when price is
  statistically **over-extended to the downside** (e.g. close well below a short MA / oversold
  band) expecting a snap-back. The over-extension trigger is a **discrete, measurable event,
  distinct from the trend filter**, so its marginal edge can be significance-tested directly —
  the exact thing S26 could not show.
- **Trade count:** moderate · **Friction:** moderate (manageable with defined targets + R-stop;
  not the tight-stop intraday trap) · **Regime risk:** **different and complementary** — weak
  in sustained downtrends/crashes but **stronger in the choppy regime where S26 was weakest** ·
  **Multi-market:** **EXCELLENT now** (daily NQ + independent ES, plus MNQ/MES corroboration) ·
  **Data:** none new.
- **Biggest failure mode:** catching falling knives in a true sustained downtrend — bounded by
  the bull-trend gate + fixed R-stop; must be stress-tested in 2018/2020/2022 drawdowns.
- **Verdict: STRONGEST** — separable entry edge + counter-cyclical regime profile + immediate
  independent testability.

### Idea 5 — Support/resistance breakout-retest with volatility confirmation
- **Edge thesis:** enter on the **retest** of a broken S/R level (not the breakout), with a
  vol-confirmation gate.
- **Trade count:** low–moderate · **Friction:** low–moderate (good headroom — bigger moves,
  wider stops) · **Regime risk:** **HIGH in chop** (false breakouts) · **Multi-market:** good ·
  **Data:** none new.
- **Biggest failure mode:** choppy regime generates false breakouts and failed retests →
  2014–2016 repeat; also overlaps the parked Donchian breakout family.
- **Verdict: MODERATE** — good friction headroom but shares S26's chop weakness and overlaps
  Donchian.

## 5. Ranking (best → worst)

**4 → 5 → 1 → 2 → 3.**

## 6. Final recommendation — select **Idea 4: Mean reversion after overextension inside a bull trend**

It is the only candidate that **attacks** S26's documented weaknesses rather than
re-discovering them:

- **Entry edge (fixes #1):** the over-extension trigger is a discrete, measurable event that
  can be significance-tested against the regime filter.
- **Regime profile (fixes #3):** counter-cyclical to the 2014–2016 chop that collapsed both
  S26 and Donchian — a genuinely different regime profile, not the same trend dependence.
- **Friction (fixes #5):** selective entries with defined R-targets give better headroom than
  the intraday idea.
- **Independent testability (fixes #6, avoids data fetch):** immediately testable on
  provisioned daily NQ + independent ES, preserving clean multi-market validation — which Idea
  3 would have destroyed and Idea 2 lacks.

**Primary risk to watch:** falling-knife risk in a sustained downtrend — stress-test through
2018/2020/2022 drawdowns; gate with the bull-trend filter and a fixed R-stop.

**Next step (S27-D2):** pre-register the **frozen** S27 mean-reversion strategy spec — exact
trend gate, over-extension trigger, stop/target, exit precedence — on daily **NQ IS
2013–2022**, with the entry-significance test design fixed **before** any OOS. No optimization;
the spec is frozen before any results are seen. S27-D2 is itself a separate, to-be-authorized
step.

## 7. Guardrails

- **No code. No backtest. No optimization. No S26 modification. No paper/live. No broker/API.
  No data fetch without separate authorization.**
- This memo selects a direction only. S26 stays PARKED; Donchian stays PARKED; no new strategy
  is validated.

## 8. Trading recommendation

**NONE.** This is a research-direction memo. No deployment, no paper, no live.

---

### Notes of record
- Memo only — comparison built from committed S26/Donchian outcomes and the provisioned daily
  data inventory. No code, backtest, optimization, or data fetch.
- Donchian/S23/S24/S25, S26, JARVIS, and `templates/base.html` untouched.
