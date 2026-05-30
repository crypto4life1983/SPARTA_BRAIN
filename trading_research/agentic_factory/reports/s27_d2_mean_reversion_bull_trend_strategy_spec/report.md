# S27-D2 — Mean Reversion After Overextension Inside Bull Trend (frozen strategy spec)

**Pre-registers a fixed, testable specification for the S27 mean-reversion branch selected in
S27-D1. SPEC ONLY — no code, no backtest, no IS/OOS run, no optimization, no parameter sweeps,
no data fetch. Every parameter below is frozen before any result is seen.**

- **Created:** 2026-05-30 · **Reference commit:** `dc53087` (S27-D1 hypothesis selection)
- **S26 Trend + S/R + EMA/RSI:** PARKED. **Donchian:** PARKED. Neither is touched here.

---

## Design context (why these choices)

This spec is built to **fix S26's documented weaknesses** and to **avoid Donchian's
winner-dependence**:

- **S26 entry edge was inconclusive** → the S27 entry is a **discrete two-step event**
  (overextension *then* one-bar reversal) that can be significance-tested against random
  bull-trend entries.
- **Donchian made its money from a few fat-tail winners** (S24 ENTRY_EDGE_NOT_SUPPORTED, S25
  SEQUENCE_RISK_FRAGILE — removing the top 3 trades flipped IS and OOS negative). S27 uses a
  **capped +1.5R target** so per-trade outcomes are bounded and repeatable, plus a **hard gate:
  IS net must stay positive after removing the top 3 winners.**
- **S26 collapsed in the 2014–2016 chop** → mean reversion is **counter-cyclical** to chop;
  the regime step (D9) checks this explicitly.

---

## 1. Strategy name
**Mean Reversion After Overextension Inside Bull Trend.**

## 2. Market and timeframe
- **Primary:** NQ continuous futures, **daily** bars.
- **Independent confirmation later:** ES daily (D10 only — **never** folded into the entry).
- **No intraday data** in v1. **No 2026 data.**
- **IS:** 2013–2022. **OOS:** 2023–2025, **sealed** until the OOS protocol step is committed.
- MNQ/MES (from 2019) are descriptive corroboration only, never independent.

## 3. Core hypothesis
In a confirmed bull trend, sharp short-term overextensions to the downside tend to mean-revert
over the next several bars. **The edge must come from the discrete overextension-then-reversal
event, not from broad trend drift** — which is exactly why the entry is built to be
significance-testable against random bull-trend entries.

## 4. Fixed bull-trend filter (long-only)
- `close > EMA200`
- `EMA50 > EMA200`
- **`EMA200 slope >= 0`** over the last 20 bars, defined as `EMA200[i] − EMA200[i−20] >= 0`.

**EMA200 slope is INCLUDED.** Falling-knife risk in a rolling-over top is the #1 failure mode
of buying dips. Requiring a non-negative EMA200 slope restricts entries to a genuinely *rising*
trend, not a topping market. It is a fixed, mechanical, binary gate — no optimization, no sweep
— and directly tightens the otherwise-loose bull filter.

## 5. Fixed overextension trigger (all must hold on the signal bar)
1. `close <= EMA20 − 1.0 × ATR20` (close at least 1.0 ATR20 below EMA20)
2. `RSI14 <= 35`
3. `close` is the **lowest close of the last 5 bars** (current bar inclusive)

No subjective support/resistance drawing — every clause is mechanical and reproducible.

## 6. Fixed reversal confirmation
**Option B — one-bar reversal confirmation.** After the overextension trigger on bar *i*,
require `close[i+1] > close[i]`. If satisfied, the setup is confirmed on bar *i+1*. If
`close[i+1] <= close[i]`, the setup is **abandoned** (expires; no entry).

**Why B over A:** Option B gives (1) **less falling-knife risk** — we wait for one up-bar
before committing; and (2) **cleaner entry-significance testing** — the entry is a discrete,
datable two-step event (overextension *then* reversal) that can be compared against random
entries drawn from the same bull-trend bars to isolate the trigger's marginal edge.

## 7. Entry timing (no same-bar lookahead)
- **Signal bar:** *i* (overextension trigger true).
- **Confirmation bar:** *i+1* (`close[i+1] > close[i]`).
- **Entry:** next bar open = **open of bar *i+2***.
- **Expiry:** if confirmation fails at *i+1*, no entry; a new signal must form fresh.

## 8. Stop
- **stop = entry − 1.5 × ATR20** (ATR20 as of signal bar *i*).
- **R unit:** `1R = 1.5 × ATR20` = the stop distance. All results in **R only**.
- **Why 1.5 ATR:** tighter than S26's 2N because mean-reversion entries sit near a local
  extreme right after a reversal bar, so the invalidation level (a fresh low below the reversal)
  is closer. 1.5×ATR still leaves friction headroom comparable to S26's 2N.

## 9. Exit (conservative first version)
- **Target:** **+1.5R** (= entry + 1.5 × 1R = entry + 2.25 × ATR20).
- **Stop:** **−1R** (the 1.5×ATR20 stop above).
- **Time stop:** exit at the **close of the 10th bar held** if neither stop nor target hit.
- **EMA20-reclaim exit:** **not used** in v1 (kept out to keep the exit fixed and simple).
- **Exit precedence:** **stop → target → time_stop.** If stop and target are both touched on the
  same bar, **stop fills first** (conservative).
- **Why a capped target:** a fixed +1.5R cap makes per-trade outcomes bounded and repeatable,
  deliberately avoiding Donchian's fat-tail-winner dependence.

## 10. Position rules
One position at a time · no pyramiding · no compounding · R-only accounting · **no shorting in
v1**.

## 11. Pre-registered validation ladder
| Step | Purpose |
|---|---|
| **D3** | implement engine + tests only (no results) |
| **D4** | IS baseline 2013–2022 |
| **D5** | OOS protocol pre-registration |
| **D6** | OOS run **once** (2023–2025) |
| **D7** | entry significance (overextension+reversal vs random-in-bull-trend) |
| **D8** | Monte Carlo / sequence risk |
| **D9** | regime breakdown (incl. explicit 2014–2016 chop check) |
| **D10** | ES multi-market robustness (independent confirmation) |
| **D11** | walk-forward stability |
| **D12** | friction stress |
| **D13** | decision gate |

## 12. Pass / watch / fail thresholds (pre-registered, conservative)
| Gate | PASS | WATCH | FAIL |
|---|---|---|---|
| IS trade count | ≥40 | 25–39 | <25 |
| OOS trade count | ≥20 | 12–19 | <12 |
| Expectancy | >0 on IS **and** OOS | — | ≤0 on either |
| Profit factor | ≥1.30 | 1.10–1.29 | <1.10 |
| Max DD cap | IS max DD ≤ IS net R | — | IS max DD > 1.5× IS net R |
| Positive years | ≥6/10 IS years | 5/10 | <5/10 |
| **Top-3 winner dependence** | IS net **stays positive** after removing top 3 winners | — | IS net negative without top 3 (Donchian failure) |
| Entry significance | EDGE_LIKELY | INCONCLUSIVE (not disproven) | NOT_SUPPORTED |
| Sequence risk | bootstrap P(total R≤0) <10% | 10–20% | ≥20% (Donchian was 20.9%) |
| Friction | IS positive at 0.05R **and** OOS positive at 0.10R/trade | — | OOS negative at ≤0.05R |

## 13. Anti-overfit rules
- No parameter sweeps.
- No changing RSI/ATR/EMA/target/stop/slope/time-stop after seeing results.
- If any rule changes, **open a new branch** (do not mutate S27 in place).
- No OOS peeking before the OOS protocol is committed.
- No paper/live promotion from this spec or from IS results.

## 14. Main expected failure modes
- **Falling-knife risk** (dips inside a rolling-over trend) — mitigated by the EMA200 slope
  gate + reversal confirmation + R-stop.
- **Bull filter too loose** — mitigated by the slope gate.
- **Signal count too low** (two-step confirmation is restrictive) — watch the IS/OOS trade
  floors.
- **Target too optimistic** (+1.5R rarely reached on snap-backs) — watch win rate vs time-stop
  exits.
- **Choppy-regime false positives** (oversold keeps going) — D9 regime check.
- **Friction sensitivity** on a tighter 1.5×ATR stop — D12 friction stress.

## 15. Final line
**“S27-D2 is a frozen hypothesis specification only; no backtest, OOS, paper, or live trading
is authorized.”**

---

### Notes of record
- Spec only — frozen pre-registration. No code, backtest, IS/OOS run, optimization, parameter
  sweep, or data fetch.
- S26, Donchian/S23/S24/S25, JARVIS, `templates/base.html`, and the hydra dir untouched.
