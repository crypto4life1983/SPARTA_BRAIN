# S29-D2 — Failed-Breakout / False-Break Reversal · FROZEN STRATEGY SPEC (spec only)

**This is a frozen hypothesis specification. No strategy code, no backtest, no
IS/OOS run, no optimization, no parameter sweep, no data fetch, no paper/live, no
source/engine/test changes, no staging, no commit.** It freezes every parameter
BEFORE any result is seen, so the later factory ladder is a genuine out-of-sample
test of a pre-registered rule.

- **Created:** 2026-05-30
- **HEAD at spec:** `139bb60` — exactly the S29-D1 commit. Factory tree clean,
  nothing staged, no automation-touched factory files since S29-D1.
- **Context read (read-only):** S29-D1 idea sourcing; S28-D4 IS baseline; S26-D18
  decision gate; Factory-D11 closeout.

---

## 1. Strategy name

**Failed-Breakout / False-Break Reversal.**

## 2. Market / timeframe

- **Primary:** NQ continuous futures, **daily** bars.
- **Independent confirmation (later step):** ES daily.
- **Daily bars only — no intraday data in v1.**
- **No 2026 data.**
- **IS:** 2013–2022. **OOS:** 2023–2025 — **SEALED** until the OOS protocol is
  pre-registered and committed.
- MNQ/MES are same-underlying proxies, descriptive only; never independent.

## 3. Core hypothesis

A daily bar that violates a prior daily extreme **intrabar** but **fails to close
beyond the prior range** (a false break) traps breakout traders, who are then
forced to cover — mechanically reverting price over the next several bars. **The
edge must come from the failure event, not from broad trend drift.** The
entry-significance test (vs random entries inside the same eligible regime
universe, and vs raw prior-extreme touches) is designed to prove exactly that.

## 4. Direction — **LONG-ONLY false DOWNSIDE break** (v1)

Price breaks **below** the prior 20-day low intrabar but **closes back above it**,
trapping breakout-shorts → **go long** the reversal.

**Why long-only for v1:**
- Simpler and safer — one direction, one frozen trigger, an unambiguous clean test.
- Index futures carry a structural upward drift over 2013–2022; a long-only
  false-downside-break fades a failed flush **with** the drift rather than fighting
  it (short-only / symmetric would fight the drift and behave asymmetrically,
  muddying the test).
- The falling-knife risk is handled by the minimal regime guard (§6), which blocks
  only **confirmed** downtrends — not the edge itself.
- Distinct from every parked branch: S26/S27 were trend/pullback **continuation**
  longs; this is a **failure-event reversal** long whose edge is isolated from the
  trend filter by the entry-significance control.

**Symmetric (adding false-upside-break shorts) is deferred** to a future,
separately-authorized branch.

## 5. False-break level

- **Prior 20-day low, excluding the current bar** (a 20-bar rolling low shifted by
  one bar).
- **Long trigger:** `low_t < prior_20_low_t  AND  close_t > prior_20_low_t`.
- Frozen: `lookback_n = 20`, prior (shifted) low, current bar excluded.
- (Deferred short trigger, for the record: `high_t > prior_20_high_t AND close_t <
  prior_20_high_t`.)

## 6. Regime / background filter — **Option B: avoid a confirmed downtrend**

- **Rule:** block a long entry if `close_t < EMA200_t  AND  EMA50_t < EMA200_t`.
  Otherwise eligible.
- Frozen: `ema_fast = 50`, `ema_slow = 200`.
- **Rationale:** by De Morgan this equals Option A (allow when `close ≥ EMA200 OR
  EMA50 ≥ EMA200`); chosen in the "avoid confirmed downtrend" framing because it is
  the **most permissive** guard — it blocks only the both-bearish falling-knife
  regime. Maximizing eligibility directly attacks the **S27 (18 trades) / S28 (12
  trades) low-count failure**: the filter is a **guard, not an edge driver**. It
  avoids the **S26** failure (edge indistinguishable from the trend filter) because
  entry significance is tested **within** this eligible universe.

## 7. Entry timing

- **Signal bar** = the false-break bar (low pierces `prior_20_low`, close returns
  above it, eligible regime).
- **Entry** = **next bar open** (`t+1` open).
- **No same-bar lookahead** — the signal is known only at the signal-bar close.

## 8. Stop — **level-based (thesis-invalidation)**

- **`stop_price = signal_bar_low − 0.25 × ATR20_at_signal_bar`.**
- Frozen: `atr_period = 20`, `buffer = 0.25 × ATR`, anchor = signal-bar low.
- **1R = `entry_open − stop_price`.**
- Level-based because the thesis is that the false-break extreme holds; if price
  takes out that low (plus a 0.25·ATR noise buffer), the setup is invalidated.

## 9. Target / exit

- **Target = +1.5R** (`target_price = entry_open + 1.5 × R`).
- **Stop = −1R** (the level stop of §8, by construction).
- **Time stop:** exit at the **close of the 10th bar** after entry if neither hit.
- **Same-bar both-hit:** assume **stop first** (conservative).
- Frozen: `target_R = 1.5`, `stop_R = 1.0`, `time_stop_bars = 10`, `same_bar =
  stop_first`. No EMA20 / midpoint exit in v1 (avoids an extra free parameter).

## 10. Position rules

One position at a time · no pyramiding · no compounding · **R-only accounting** ·
no discretionary override.

## 11. Entry-significance protocol (pre-registered)

- **Primary:** real false-break entries vs the **same count of random entries**
  drawn from the same eligible regime universe (non-confirmed-downtrend days).
- **Secondary:** real false-break entries vs **raw prior-20-low touch** entries
  (`low_t < prior_20_low_t`, regardless of close) — the raw-breakout null, proving
  the **failure** (close back inside), not the touch, carries the edge.
- **Fixed horizons: 5, 10, 20, 40 bars** — no horizon shopping.
- **Promotion requires `EDGE_LIKELY`** (not merely `INCONCLUSIVE` — the S26 trap).

## 12. Validation ladder plan (completed factory; nothing run now)

| Sub-step | Scope |
|---|---|
| S29-D3 | engine + tests only (frozen rules; no run) |
| S29-D4 | IS baseline 2013–2022 (`validation_is_runner`, hard 2023–2025 seal) |
| S29-D5 | OOS protocol pre-registration (`validation_oos_runner`); **commit before OOS** |
| S29-D6 | OOS run **once** (2023–2025) against the committed protocol |
| S29-D7 | entry significance (`validation_entry_significance`, §11) |
| S29-D8 | sequence risk / Monte Carlo (`validation_sequence_risk`) |
| S29-D9 | regime breakdown (`validation_regime`) |
| S29-D10 | ES multi-market independent confirmation |
| S29-D11 | walk-forward (`validation_walk_forward`) |
| S29-D12 | friction stress (`validation_friction`) |
| S29-D13 | final decision / readiness gate (`validation_decision`) |

## 13. Pass / watch / fail gates (pre-registered)

| Gate | PASS | WATCH | FAIL |
|---|---|---|---|
| IS trade count | ≥40 | 25–39 | <25 |
| OOS trade count | ≥15 | 8–14 | <8 |
| Profit factor | ≥1.30 | 1.10–1.29 | <1.10 |
| Expectancy (IS) | >0 (required) | — | ≤0 |
| Max DD cap | DD ≤ net R | — | DD > 1.5× net R |
| Positive years | ≥6/10 | 5/10 | <5/10 |
| Top-3 winner dependence | net positive ex-top-3 | — | net flips negative ex-top-3 |
| Sequence-risk bootstrap P(total ≤ 0) | <10% | 10–20% | ≥20% |
| Entry significance | `EDGE_LIKELY` | — | `INCONCLUSIVE` / `NOT_SUPPORTED` |
| Friction | full-history positive at ≥0.10R/trade | — | negative at 0.10R |

## 14. Anti-overfit rules

- No changing lookback (20), ATR period (20), ATR buffer (0.25), target (1.5R),
  stop (1R), time stop (10 bars), or EMA periods (50/200) after any result.
- No OOS run before the OOS protocol is pre-registered **and committed**.
- No parameter sweeps; no grid search; no "best of N".
- No adding/removing filters after OOS.
- Any rule change opens a **new branch** — S29 is never tuned in place.
- No paper/live promotion from the spec or from IS — requires a separate readiness
  memo with explicit override fields.

## 15. Expected failure modes

- False breaks can keep breaking (failed flush resumes lower despite the guard).
- Low trade count if the event is rarer than expected (the S27/S28 risk).
- Level stop too tight around the volatile false-break extreme → premature stops
  (widening it later = a new branch).
- Mean reversion may depend on the volatility regime → regime concentration (the
  inverse of S26; surfaced by the regime + walk-forward modules).
- Daily bars hide the intraday path; the same-bar stop-first assumption may
  mis-state fills.
- A future symmetric short side may behave very differently from the long side
  (deferred for this reason).
- Friction sensitivity if the +1.5R target yields small average R (the S26 failure).

## 16. Final line

**“S29-D2 is a frozen hypothesis specification only; no strategy code, backtest,
OOS, optimization, paper trading, or live trading is authorized.”**

---

### Guardrails

`spec_only` · `no_code` · `no_backtest` · `no_is_oos_run` · `no_optimization` ·
`no_parameter_sweeps` · `no_data_fetch` · `no_paper_or_live` · `no_broker_or_api`
· `no_source_engine_test_changes` · `oos_2023_2025_sealed` · `no_2026` ·
`donchian_s26_s27_s28_read_only` · `jarvis_templates_hydra_untouched` ·
`no_staging` · `no_commit`.

**Trading recommendation:** NONE. Frozen specification only. Donchian, S26, S27,
S28 remain PARKED; no active strategy code; no paper/live system exists or is
authorized. The frozen S29 rules are a research hypothesis to be tested under the
factory ladder, not a trade.
