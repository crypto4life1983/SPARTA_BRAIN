# S30-D1 — Deep Strategy Idea-Source Review (selection / research only)

**This is a deep idea-source review memo. No strategy code, no backtest, no IS/OOS
run, no optimization, no parameter sweep, no data fetch, no paper/live, no
source/engine/test changes, no staging, no commit.** It re-derives the cross-branch
failure modes of the completed-and-parked factory branches, builds a 10-criterion
scoring framework, scores ten idea families, and selects exactly one structurally
distinct next branch (or declines to select).

- **Created:** 2026-05-30
- **HEAD at memo:** `73e1cb0` (descendant of the S29-D4 decision-record commit
  `9d5b9d8`; `9d5b9d8` verified ancestor of HEAD; no agentic_factory file touched
  by automation between `9d5b9d8` and HEAD; factory tree clean, nothing staged).
- **Reports read (read-only, for lessons only):** Factory-D11 closeout; S25-D1
  Donchian trade-order Monte Carlo; S26-D18 decision gate; S27-D4 IS baseline;
  S28-D4 IS baseline; S29-D4 IS baseline.

---

## 1. Summary of parked-branch lessons

Five strategy branches are PARKED. **All five share one dominant, repeating
failure**, and several share secondary failures. This is the single most important
input to S30: the *next* idea must be structurally chosen to break the pattern, not
merely be a fresh trigger.

| Branch | Outcome | Net (IS) | Trades | Top-3 removal | Other binding failures |
|---|---|---|---|---|---|
| Donchian (S23–S25) | PARKED | weak | OOS 16 | **net flips negative ex-top-3** (IS −3.82, OOS −1.93) | `ENTRY_EDGE_NOT_SUPPORTED`; bootstrap P(total≤0)=20.9%; DD = path luck |
| S26 Trend/SR/EMA/RSI | PARKED | thin ~0.06R | adequate | thin / fragile | `ENTRY_EDGE_INCONCLUSIVE` (not distinct from trend filter); `FRICTION_SENSITIVE` (neg at 0.10R); post-2016-only, 2014–2016 collapse; OOS single-year-dominated |
| S27 Mean-reversion-in-bull | PARKED (IS_FAIL) | −1.75R | **18** (<25 floor) | **−6.25R** | PF 0.84; exp −0.097R; 3/10 positive years; over-stacked confirmation starved sample |
| S28 Breakout-retest | PARKED (IS_FAIL) | −0.72R | **12** in 10y | **−6.72R** | PF 0.91; exp −0.06R; 3/10 positive; 5-filter stack on a raw breakout = clean negative |
| S29 Failed-breakout reversal | PARKED (IS_FAIL) | negative | low | fails | failed the IS gate despite being the *inverse* of a raw breakout |

**The universal killer — top-winner / fat-tail dependence.** Every parked branch's
net depends on a handful of large winners; remove the top 3 and the edge inverts.
This is the Donchian gate, and **it has failed on every single-instrument
directional-trigger branch tried so far.** The structural reason: each branch fires
a small number of directional bets and survives only if a few of them become
fat-tail captures. That is statistically indistinguishable from luck.

**Secondary repeating failures:**
- **Low trade count from over-stacked filters** (S27=18, S28=12). Confirmation
  filters added for "quality" starve the sample below the 25-trade floor.
- **Thin expectancy with no friction headroom** (S26 ~0.06R, S29). A ≤0.10R edge
  dies the moment realistic per-trade cost is applied (`FRICTION_SENSITIVE`).
- **Entry edge not distinct from the regime filter** (S26 `INCONCLUSIVE`). Profit
  came from the trend backdrop, not the trigger — entry significance never cleared.
- **Poor year distribution** (S27/S28 = 3/10 positive). Concentrated, not durable.
- **Regime / calendar concentration** (S26 post-2016-only; 2014–2016 chop sank it;
  OOS dominated by a single year).
- **Raw breakout/retest fragility** — every breakout-shaped idea (Donchian, S28,
  and even the S29 *anti*-breakout) failed IS. The breakout family is exhausted on
  this data.

**What S30 must therefore avoid, by construction:**
1. Single-instrument, small-N directional triggers (they all fail the top-3 gate).
2. Any breakout / breakout-retest / extreme-touch family.
3. Filter-stacking for "quality" (it starves trade count).
4. An edge whose expectancy is < ~0.10R or that rides a trend filter.
5. Anything that needs data we do not have offline.

## 2. Idea scoring framework (10 criteria, each Low / Med / High)

| # | Criterion | What a strong (High) score means |
|---|---|---|
| C1 | Causal reason for the edge | A concrete economic/structural mechanism (risk premium, forced flow, settlement mechanics), not a chart shape. |
| C2 | Entry-significance testable | The trigger can be tested against a random-day null *and* a structural null, cleanly isolating the claimed cause. |
| C3 | Expected trade count | Comfortably clears the ≥40 IS floor — ideally hundreds — so results are not a small-N fluke. |
| C4 | Friction headroom | Average edge per event large enough to survive ≥0.10R/trade realistic cost. |
| C5 | Multi-market testability | Independently confirmable on a genuinely separate instrument (NQ↔ES; micros are NOT independent). |
| C6 | Robustness across trend/chop regimes | Edge does not depend on one regime; survives 2014–2016 chop and post-2016 trend alike. |
| C7 | Daily-data suitability | Fully expressible on daily OHLCV with no intraday path dependency. |
| C8 | Low top-winner dependence | Edge is the *average* of many small bets; net stays positive after removing the top 3. **The gate that killed every parked branch.** |
| C9 | Distinctness from parked failures | Not a re-skin of Donchian/S26/S27/S28/S29 (trend-continuation, mean-reversion-in-bull, breakout, breakout-retest, failed-breakout). |
| C10 | Needs new data? | High = needs NO new data (uses existing offline NQ/ES/MNQ/MES daily CSVs). Low = requires data we do not have. |

**Offline data on hand (no fetch authorized):** daily OHLCV (`ts_event,open,high,
low,close,volume,symbol`) for NQ 2013–2025, ES 2013–2025, MNQ 2019–2025, MES
2019–2025. **No intraday, no term-structure/individual-contract series, no breadth,
no other markets (no YM/Dow, no RTY/Russell).** MNQ/MES are same-underlying proxies
— descriptive only, never independent confirmation.

## 3. Candidate comparison (10 idea families)

Each scored C1–C10; key per-idea fields below the table.

| # | Idea family | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C10 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Volatility-contraction breakout | Med | Med | Med | Med | High | Low | High | Low | Low | High |
| 2 | Gap continuation / fade | Med | High | High | **Low** | High | Med | Med | Med | Med | High |
| 3 | **Overnight session-return decomposition (overnight-drift)** | **High** | **High** | **High** | Med | **High** | **High** | **High** | **High** | **High** | **High** |
| 4 | Range expansion after inside-bar cluster | Med | Med | Med | Med | High | Med | High | Low | Med | High |
| 5 | Trend exhaustion after consecutive large-range days | Med | Med | Med | Med | High | Low | High | Low | Med | High |
| 6 | **Turn-of-month / weekday calendar tendency** | **High** | **High** | **High** | Med | **High** | **High** | **High** | **High** | **High** | **High** |
| 7 | Cross-market relative-strength NQ vs ES | Med | Med | Med | Med | **Low** | Med | High | Med | High | High |
| 8 | Vol-regime classifier no-trade overlay | High | **Low** | n/a | n/a | High | High | High | n/a | Low | High |
| 9 | Carry / term-structure | High | Med | Med | Med | High | High | High | Med | High | **Low** |
| 10 | Multi-day momentum crash / recovery | Med | Med | Med | Med | High | Low | High | Low | Med | High |

### Per-idea detail

**1. Volatility-contraction breakout.** *Hypothesis:* low-range compression
precedes a directional expansion; trade the break. *Why edge:* vol clusters
(magnitude), but the *direction* is unproven. *Data:* daily OHLC (have). *Daily
feasibility:* high. *Expected count:* moderate. *Friction:* moderate. *Regime
risk:* expansion direction is trend-dependent. *Entry-sig design:* break vs random
day in the same compressed universe. *Multi-market:* NQ→ES. *Biggest failure mode:*
re-inherits the unproven raw-breakout entry — the exhausted breakout family.
*Similarity to parked:* high (Donchian/S28 breakout DNA).

**2. Gap continuation / fade.** *Hypothesis:* the open-vs-prior-close gap either
continues or fades to the prior close. *Why edge:* overnight repricing + open
liquidity imbalance. *Data:* daily open/close (have). *Daily feasibility:* good (no
intraday needed for a close-to-open + open-to-close split). *Expected count:* high.
*Friction:* **low headroom — the per-gap effect on daily futures is small and cost
erodes it.** *Regime risk:* moderate. *Entry-sig:* gap-day fwd return vs random
day. *Multi-market:* NQ→ES. *Biggest failure mode:* thin per-event edge vs cost.
*Similarity to parked:* moderate (a directional small-edge bet, S26-like friction
risk).

**3. Overnight session-return decomposition (overnight-drift anomaly). — WINNER.**
*Hypothesis:* the equity-index risk premium is earned **overnight** (prior close →
next open), while the day session (open → close) carries little or negative drift.
Systematically harvest the overnight leg. *Why edge — causal:* a documented,
mechanistic risk-premium / inventory-rebalancing effect (overnight gap risk is
compensated; market-makers and leveraged funds shed/rebuild exposure around the
close/open), **not a chart shape.** *Data:* daily open & close only — exactly what
the offline CSVs contain. *Daily feasibility:* native — the close→open and
open→close legs are fully defined by daily bars with **no intraday path needed.**
*Expected count:* **hundreds of bets/year** (every session) → trivially clears the
≥40 floor by two orders of magnitude. *Friction:* moderate — small per-day edge, so
the **binding S30-D2 test is whether it survives ≥0.10R/trade and whether futures
settlement open/close approximates the cash overnight window.** *Regime risk:* low
— it is an average over all days, not a regime bet; spans 2014–2016 and post-2016
alike. *Entry-sig design:* overnight-leg returns vs (a) day-session returns and (b)
a random close-to-close null — cleanly isolates *when* the premium accrues.
*Multi-market:* NQ primary, ES genuinely independent (same effect, separate
contract). *Biggest failure mode:* per-day edge too small to clear friction; or the
futures open/close prints not matching the true overnight session → mis-measured
legs. *Similarity to parked:* **none** — every parked branch was a small-N
directional *trigger*; this is a many-bet *anomaly-harvest* whose net is the average
of hundreds of independent days. **This is the direct structural antidote to the
top-3-winner gate that killed all five parked branches.**

**4. Range expansion after inside-bar cluster.** *Hypothesis:* a cluster of
inside-bars (contracting range) precedes an expansion; trade the breakout of the
cluster. *Why edge:* compression→expansion (magnitude, not direction). *Data:*
daily OHLC (have). *Count:* moderate. *Friction:* moderate. *Regime:* direction is
trend-coupled. *Entry-sig:* expansion vs random. *Multi-market:* NQ→ES. *Biggest
failure mode:* directionless — same breakout-direction problem as #1. *Similarity:*
moderate-high (breakout family).

**5. Trend exhaustion after consecutive large-range days.** *Hypothesis:* N
consecutive large-range trend days exhaust; fade. *Why edge:* over-extension /
mean-reversion. *Data:* daily OHLC (have). *Count:* moderate. *Friction:* moderate.
*Regime:* strongly regime-dependent (fades trends → bleeds in persistent trends, an
S27 echo). *Entry-sig:* exhaustion bar fwd return vs random. *Multi-market:*
NQ→ES. *Biggest failure mode:* fighting the structural index drift (S27). *Similar
to parked:* mean-reversion-in-bull (S27).

**6. Turn-of-month / weekday calendar tendency. — RUNNER-UP.** *Hypothesis:* index
returns concentrate around the turn-of-month (last-/first-few sessions) and exhibit
weekday seasonality, driven by structural fund flows (payroll, index rebalancing,
month-end marking). *Why edge — causal:* recurring institutional cash flows, a
genuine structural mechanism. *Data:* daily close + the date index (have).
*Feasibility:* native daily. *Count:* high (every month contributes). *Friction:*
moderate (per-window edge is small but the windows are few-and-specific, improving
per-trade size vs the overnight idea). *Regime:* low — flow-driven, largely
regime-independent. *Entry-sig:* turn-of-month window returns vs random same-length
windows. *Multi-market:* NQ→ES. *Biggest failure mode:* **calendar-effect
overfitting** — many possible day-of-month/weekday cutoffs invite a "best-of-N"
search; **must hard-freeze the window definition before any run, no sweeps.**
*Similarity to parked:* none (no parked branch was calendar-based). Slightly behind
#3 only because its trade count, while high, is lower than the every-session
overnight harvest, and the overfit temptation is sharper.

**7. Cross-market relative-strength NQ vs ES.** *Hypothesis:* NQ−ES relative
strength mean-reverts or trends. *Why edge:* sector rotation / dispersion. *Data:*
NQ + ES daily (have). *Feasibility:* daily. *Count:* moderate. *Friction:*
moderate. *Regime:* moderate. *Entry-sig:* RS signal vs random. *Multi-market:*
**fails by construction — the strategy CONSUMES both NQ and ES as inputs, leaving
no independent instrument for confirmation (C5 Low).** *Biggest failure mode:* no
out-of-sample independent market; only two index futures exist offline. *Similar to
parked:* low, but the lost-independence flaw is disqualifying for our validation
discipline.

**8. Vol-regime classifier no-trade overlay.** *Hypothesis:* classify days as
trade/no-trade by volatility regime. *Why edge:* avoids bad regimes. *Standalone
entries:* **none — it is a filter, not a strategy; entry significance is
untestable (C2 Low).** Repurpose later as a factory overlay module, not an S30
branch. *Similar to parked:* it is the S29-D1 idea-1 reject again.

**9. Carry / term-structure.** *Hypothesis:* harvest futures roll/carry. *Why edge:*
strong, structural (term-structure premium). *Data:* **requires individual-contract
/ continuous-with-roll or front-vs-next term-structure series we DO NOT have offline
(C10 Low).** Disqualified on data availability, not merit.

**10. Multi-day momentum crash / recovery.** *Hypothesis:* sharp multi-day
sell-offs over-shoot and recover; buy the wash-out. *Why edge:* forced
deleveraging / liquidity-provision premium. *Data:* daily OHLC (have).
*Feasibility:* daily. *Count:* **low — crashes are rare → small-N (the S27/S28
trap).** *Friction:* moderate. *Regime:* event-concentrated → top-winner-dependent
(C8 Low). *Entry-sig:* wash-out fwd return vs random. *Biggest failure mode:*
small-N, fat-tail-dependent — exactly the gate that parked everything. *Similar to
parked:* moderate (rare-event reversal, S29 cousin).

## 4. Ranking (best → worst)

1. **#3 Overnight session-return decomposition** — only idea that *structurally*
   defeats the top-3-winner gate (hundreds of small independent bets), causal risk-
   premium mechanism, native daily-data fit, NQ/ES independent, regime-robust,
   cleanest entry-significance design. Binding open question = friction.
2. **#6 Turn-of-month / weekday calendar** — also a many-bet structural-flow edge,
   regime-robust, distinct from all parked branches; behind #3 only on count and a
   sharper overfit temptation that demands a hard-frozen window.
3. **#2 Gap continuation/fade** — high count, daily-feasible, but thin per-event
   edge → friction-fragile (S26 risk).
4. **#7 Cross-market RS NQ vs ES** — interesting and distinct, but consumes both
   instruments → no independent confirmation market (disqualifying for our gate).
5. **#1 / #4 Vol-contraction & inside-bar breakouts** — re-inherit the exhausted,
   IS-failing raw-breakout family (Donchian/S28).
6. **#5 / #10 Exhaustion fade & crash-recovery** — regime-/event-concentrated,
   small-N, top-winner-dependent (S27/S29 echoes).
7. **#9 Carry/term-structure** — strong idea, **no data offline** → cannot test.
8. **#8 Vol-regime overlay** — not a standalone strategy (no entries); a future
   factory overlay, not an S30 branch.

## 5. Final recommendation

**`SELECT_ONE_FOR_S30_D2` — Overnight session-return decomposition (overnight-drift
anomaly) on daily NQ (primary) / ES (independent confirmation).**

**Why it is genuinely better than S26/S27/S28/S29 — structurally, not just
freshly:**
- **It is the direct antidote to the one failure all five parked branches share.**
  Every parked branch failed the top-3-winner-removal gate because each was a
  small-N directional trigger whose net hinged on a few fat-tail captures. The
  overnight harvest is the *average of hundreds of independent daily bets* — its net
  cannot be dominated by 3 trades, so it attacks the universal killer at the root.
- **Causal, not chart-shaped (beats S26's `INCONCLUSIVE`).** The edge is a named
  economic mechanism (overnight risk premium / inventory rebalancing). Entry
  significance is cleanly testable: overnight leg vs day-session leg vs random
  close-to-close — it can *prove which session* carries the premium, unlike S26
  whose trigger was inseparable from its trend filter.
- **Trade count is a non-issue (beats S27=18 / S28=12).** Every session is a bet →
  thousands over 2013–2022; the ≥40 floor is cleared by orders of magnitude, with no
  filter-stacking that could starve the sample.
- **Not a breakout (beats Donchian/S28/S29).** The entire breakout / breakout-retest
  / failed-breakout family has now failed IS five times; this idea is not in that
  family at all.
- **Regime-robust (beats S26's post-2016/2014–2016 split).** Being an all-days
  average, it does not depend on a single regime or year.

**Honest caveat — the binding risk that S30-D2 must settle first.** The per-day
overnight edge is *small*, so the decisive, pre-registered S30-D2 test is **friction
survival at ≥0.10R/trade** AND **measurement validity** — whether the offline daily
futures *open* and *close* prints actually bracket the true overnight session (cash
close-to-open). If futures settlement timing smears the legs, the decomposition is
mis-measured. This must be checked *before* any optimism, and the friction floor must
be a hard pre-registered FAIL gate, exactly as for S26/S29. The idea is strong enough
to select honestly — but it is selected *with* this caveat front-and-center, not in
spite of hiding it.

(This is not a "force a winner" selection: #3 is a structurally distinct,
data-feasible, causal, high-count idea that breaks the documented failure pattern. Had
the field been only breakout re-skins and small-N fades, the correct answer would have
been `NO_STRATEGY_SELECTED`. It is not.)

## 6. Proposed next step (S30-D2, only if separately authorized)

**S30-D2 = frozen strategy specification (spec only) for the overnight session-return
decomposition** — mirroring the S29-D2 discipline:
- Freeze, before any run: the exact leg definitions (close→open overnight,
  open→close day), the position rule (long overnight leg, flat or measured day leg),
  R/accounting convention, and the **friction floor as a hard pre-registered FAIL
  gate (≥0.10R/trade)**.
- Pre-register the entry-significance protocol: overnight vs day-session vs random
  close-to-close null, fixed horizons, `EDGE_LIKELY` required (not `INCONCLUSIVE`).
- Pre-register the **measurement-validity check** (futures open/close vs true
  overnight window) as a gating step that can kill the branch before IS.
- IS 2013–2022 only; OOS 2023–2025 sealed until the OOS protocol is committed.
- NQ primary, ES independent confirmation; MNQ/MES descriptive only.
- No code, backtest, IS/OOS, optimization, sweep, data fetch, paper, or live in
  S30-D2 — spec only, exactly like S29-D2.

**S30-D2 is NOT authorized by this memo.** It requires a separate explicit
instruction.

## 7. Forbidden actions (this step)

`memo_only` · `no_code` · `no_backtest` · `no_is_oos_run` · `no_optimization` ·
`no_parameter_sweeps` · `no_data_fetch` · `no_paper_or_live` · `no_broker_or_api` ·
`no_source_engine_test_changes` · `donchian_s26_s27_s28_s29_read_only` ·
`jarvis_templates_hydra_untouched` · `no_staging` · `no_commit` ·
`do_not_start_s30_d2`.

## 8. Final line

**“S30-D1 is idea-source review only; no strategy code, backtest, OOS, optimization,
paper trading, or live trading is authorized.”**

---

**Trading recommendation:** NONE. Idea-source review only. Donchian, S26, S27, S28,
and S29 remain PARKED; no active strategy; no paper/live system exists or is
authorized. The selected hypothesis (overnight session-return decomposition) is a
research direction to be frozen and tested under the factory ladder, not a trade.
