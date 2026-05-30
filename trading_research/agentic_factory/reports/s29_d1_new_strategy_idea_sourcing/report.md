# S29-D1 — New Strategy Idea-Sourcing Memo (selection / research only)

**This is an idea-sourcing memo. No strategy code, no backtest, no IS/OOS run, no
optimization, no parameter sweep, no data fetch, no paper/live, no
source/engine/test changes, no staging, no commit.** It compares candidate
hypotheses against the lessons of the completed validation factory and selects
exactly one next S29 branch.

- **Created:** 2026-05-30
- **HEAD at memo:** `42b5db7` — exactly the Factory-D11 commit
  (`42b5db7e849e3a9c4aa03d6c5ecfea631afd8887`). Factory tree clean, nothing
  staged, no automation-touched factory files since D11.
- **Reports read (read-only):** Factory-D11 closeout; S25-D1 Donchian MC; S26-D18
  decision gate; S27-D4 IS baseline; S28-D4 IS baseline.

---

## 1. Current factory-complete context

The reusable research-validation factory (Factory-D1 → D11) is **complete,
committed, and demonstrated end-to-end on synthetic data** — report writer, IS
runner with a hard OOS seal, OOS protocol/one-shot enforcement, entry
significance, sequence-risk Monte Carlo, regime / walk-forward / friction, the
final decision/readiness gate, the CLI, and the synthetic E2E smoke. It is **not**
a paper/live system. Any new *frozen* S29 hypothesis can now be put through the
same anti-overfit ladder with uniform reports and identical git/data guardrails.
**The bottleneck is a strong hypothesis, not tooling.**

## 2. Parked branch lessons → what S29 must avoid

| Branch | Outcome | Core lesson |
|---|---|---|
| Donchian (S23–S25) | PARKED | Profit hid a weak entry — `ENTRY_EDGE_NOT_SUPPORTED`; net flips negative without the top 3 trades; gentle DD was path luck; OOS only 16 trades. **A profitable curve is not an edge.** |
| S26 Trend/SR/EMA/RSI | PARKED (`PARK_CANDIDATE`) | OOS PASS but thin ~0.06R IS edge, `FRICTION_SENSITIVE`; entry significance `INCONCLUSIVE` (not distinct from the trend filter); whole record in the post-2016 trend with a 2014–2016 collapse; OOS single-year-dominated. |
| S27 Mean-reversion-in-bull | PARKED (`IS_FAIL`) | Net −1.75R, **18 trades** (<25 floor), PF 0.84, exp −0.097R, 3/10 positive years, top-3 removal −6.25R. Over-restrictive confirmation starved the sample. |
| S28 Breakout-retest | PARKED (`IS_FAIL`) | Net −0.72R, **12 trades in 10 years**, PF 0.91, exp −0.06R, top-3 removal −6.72R. A 5-filter stack on a raw breakout = clean negative. |

**S29 must avoid:** raw-breakout fragility · weak/inconclusive entry edge not
distinct from a trend filter · top-winner/fat-tail dependence · low trade count
from over-stacked filters · 2014–2016 chop collapse / post-2016 concentration ·
thin IS expectancy with no friction headroom · friction sensitivity · OOS or
single-year concentration.

## 3. Candidate comparison

| # | Idea | Entry edge (direction?) | Avoids prior failures | Trade count | Friction | Regime risk | NQ/ES testable | Data | Entry-sig testable |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Bad-regime no-trade classifier (overlay) | None (a filter) | Encodes chop lesson but no entries | **Zero standalone** | N/A | Is a regime model | Overlay only | Daily OHLC | **No** |
| 2 | Vol compression → expansion | Magnitude, **not direction** | Regime-agnostic state | Moderate–good | Decent | Lower | High | Daily OHLC | Yes (dir. weak) |
| 3 | **Failed-breakout (false-break) reversal** | **Direction, causal** | Inverse of breakout failures; counter-trend | Moderate | Reasonable | Chop-concentrated (opposite of S26) | High | Daily OHLC | **Yes, cleanly** |
| 4 | Trend-day continuation | Hard to separate from trend | Weak (S26 redux) | High | **High (thin)** | **High (trend)** | High | Daily OHLC | Partial |
| 5 | Pullback-to-VWAP/EMA + breadth | Mean-revert in trend | Poor — parked family | Moderate | Likely thin | Trend-dependent | Moderate | Needs breadth | Already INCONCLUSIVE |
| 6 | Opening-gap fade | Mean-revert (small) | Distinct | Moderate | **High (thin)** | Moderate | Daily-imperfect | Daily OHLC | Yes (small effect) |

## 4. Ranking (best → worst)

1. **Idea 3 — Failed-breakout (false-break) reversal:** directional structural edge, anti-trend-concentration, daily-testable on NQ/ES, distinct from every parked branch, entry significance cleanly testable.
2. **Idea 2 — Vol compression → expansion:** robust vol-clustering basis and lower regime concentration, but the directional break entry re-inherits the unproven raw-breakout edge.
3. **Idea 4 — Trend-day continuation:** high count but thin, friction-sensitive, trend-regime-dependent (S26 redux).
4. **Idea 1 — Bad-regime no-trade classifier:** conceptually valuable but not a standalone branch (no entries, entry significance untestable); better repurposed later as an overlay/factory module.
5. **Idea 6 — Opening-gap fade:** distinct but thin and poorly served by daily bars (instrument mismatch).
6. **Idea 5 — Pullback-to-VWAP/EMA + breadth:** too close to the already-parked S26/S27 family and needs breadth data NQ may lack.

## 5. Selected hypothesis — S29: Failed-breakout (false-break) reversal on daily NQ/ES

When price breaks an N-day extreme intrabar but **closes back inside the prior
range** (a failed breakout), **fade the break**: enter in the reversal direction
with an R-based stop just beyond the false-break extreme and a fixed-R /
mean-revert target.

## 6. Why it won

- **Strongest, most distinct entry edge with a causal mechanism** — trapped
  breakout entrants forced to cover mechanically push price back. It predicts
  **direction**, not just magnitude, which is exactly what every parked branch
  lacked.
- **Most directly avoids the documented failure modes** — it is the *inverse* of
  the Donchian/S28 raw-breakout failures, and being counter-trend it does not ride
  a trend filter (S26/S27) and is not post-2016-trend-dependent; it may even
  profit in the 2014–2016 chop that sank S26.
- **Entry significance is cleanly testable** against both a random-day null and a
  raw-breakout null — the factory can prove the *failure* (not the breakout)
  carries the edge.
- **Daily-data testable** on NQ primary and ES independently; no intraday
  dependency.
- **Not a tweak of any parked branch** — none was a reversal/fade.

## 7. Why the others lost

- **Idea 2 (vol compression):** strong second, but compression predicts magnitude
  not direction; the break entry re-inherits the unproven raw-breakout edge and
  risks an INCONCLUSIVE entry-significance result like S26.
- **Idea 4 (trend continuation):** too close to S26; thin, friction-sensitive,
  trend-regime-concentrated.
- **Idea 1 (no-trade classifier):** no entries standalone; can't meet "strongest
  entry edge" or "entry significance testable"; only useful bolted onto a parked
  branch — a tweak, not a new branch.
- **Idea 6 (gap fade):** thin per-trade edge; daily bars are a poor instrument for
  an overnight/intraday effect.
- **Idea 5 (pullback + breadth):** the already-parked S26/S27 family (S26 entry
  significance was INCONCLUSIVE); needs breadth data NQ may lack.

## 8. Key risks

- **Regime concentration in chop** with losses in strong trends — the regime +
  walk-forward modules must check this (expected to be the opposite concentration
  to S26).
- **Definitional parameter risk** — "what counts as a failed break" (N,
  close-back threshold) must be **frozen** in S29-D2 before any run; no post-hoc
  tuning.
- **Trade-count risk** — do **not** stack confirmation filters (the S27/S28
  killer); keep **one** trigger + stop + target, target ≥40 IS trades.
- **Friction** — the **full-history** edge must stay positive under ≥0.10R/trade,
  not just OOS.
- **Top-winner dependence** — net must stay positive without the top 3 trades.
- **Year/OOS concentration** — profit must spread across years.

## 9. Proposed S29-D2 spec direction

- **Core trigger (single, frozen):** an N-day (e.g. 20-day) extreme exceeded
  intrabar but the bar closes back inside the prior range → fade the reversal
  direction; symmetric for failed upside and downside breaks.
- **Risk model:** R-based; stop just beyond the false-break extreme; target a
  fixed R and/or revert-to-mean (EMA20 / prior swing); R-only, one position at a
  time.
- **Anti-overfit pre-registration:** freeze N, the close-back-inside definition,
  stop and target **before** any run; no sweeps; any change opens a new branch.
- **Pre-registered IS gates:** trade count ≥40 (FAIL <25); PF ≥1.30; expectancy
  >0; positive years ≥6/10; net positive **without top 3**; IS max DD ≤ IS net.
- **Entry significance:** false-break forward returns vs (a) random-day and (b)
  raw-breakout nulls; require EDGE_LIKELY, not merely beating random.
- **Regime / walk-forward:** classify trend vs chop; expect chop concentration and
  test trend-regime survival; surface 2014–2016 specifically (the inverse of S26).
- **Friction:** full-history positive under ≥0.10R/trade.
- **Multi-market:** NQ primary; ES the one genuinely independent confirmation;
  micros descriptive only.
- **Discipline:** IS first under the sealed 2013–2022 window; pre-register and
  **commit** the OOS protocol before touching 2023–2025; one-shot OOS; no tuning
  after OOS.

## 10. Final line

**“S29-D1 is idea sourcing only; no strategy code, backtest, OOS, optimization,
paper trading, or live trading is authorized.”**

---

### Guardrails

`memo_only` · `no_code` · `no_backtest` · `no_is_oos_run` · `no_optimization` ·
`no_parameter_sweeps` · `no_data_fetch` · `no_paper_or_live` · `no_broker_or_api`
· `no_source_engine_test_changes` · `donchian_s26_s27_s28_read_only` ·
`jarvis_templates_hydra_untouched` · `no_staging` · `no_commit`.

**Trading recommendation:** NONE. Idea-sourcing memo only. Donchian, S26, S27, S28
remain PARKED; no active strategy; no paper/live system exists or is authorized.
The selected S29 hypothesis (failed-breakout reversal) is a research direction,
not a trade.
