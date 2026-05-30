# S30-D2 — Overnight Session-Return Decomposition / Overnight Drift · FROZEN STRATEGY SPEC (spec only)

**This is a frozen hypothesis specification. No strategy code, no backtest, no
IS/OOS run, no optimization, no parameter sweep, no data fetch, no paper/live, no
source/engine/test changes, no staging, no commit.** It freezes every parameter and
gate BEFORE any result is seen, so the later factory ladder is a genuine
out-of-sample test of a pre-registered rule.

- **Created:** 2026-05-30
- **HEAD at spec:** `9e1c565` — exactly the S30-D1 commit
  (`9e1c565f19c54ce00695de73aeff7560089f766c`). Factory tree clean except the known
  untracked `reports/crypto_d1_research_lane_protocol/` folder (untouched here);
  nothing staged; no automation-touched factory file since S30-D1.
- **Context read (read-only):** S30-D1 deep idea-source review; Factory-D11
  closeout; S29-D4 IS baseline; S26-D18 decision gate; S25-D1 Donchian Monte Carlo.

---

## 1. Strategy name

**Overnight Session-Return Decomposition / Overnight Drift.**

## 2. Market / timeframe

- **Primary:** NQ continuous futures, **daily** bars.
- **Independent confirmation (later step):** ES daily.
- **Daily bars only — no intraday data in v1.**
- **No 2026 data.**
- **IS:** 2013–2022. **OOS:** 2023–2025 — **SEALED** until the OOS protocol is
  pre-registered and committed.
- MNQ/MES are same-underlying proxies, descriptive only; never independent
  confirmation.

## 3. Core hypothesis

A systematic **overnight risk premium** may exist: the return earned from **prior
close → next open** (the overnight leg) may differ — and be more reliably positive —
than the **open → close** day-session leg. **The edge, if real, must come from many
small repeated overnight observations, not from a few large trend captures.** This
is the structural antidote to the failure that parked every prior branch: each was a
small-N directional trigger whose net hinged on 3 fat-tail winners (all failed the
top-3-removal gate). An every-session overnight harvest is the *average* of thousands
of independent daily bets and cannot be dominated by a handful of days — that
property is the whole point and is itself a **pre-registered gate** (§12).

## 4. Measurement definition (exact)

For trading date `t`, with daily bars indexed by date:

- `prior_close = close[t-1]`
- `next_open   = open[t]`
- **`overnight_return  = open[t]  − close[t-1]`** (the leg we harvest in v1)
- **`day_session_return = close[t] − open[t]`**
- **`total_day_return    = close[t] − close[t-1]`** (= overnight + day-session, by
  construction)

**Measurement validity is a HARD GATE, not a footnote.** Daily futures bars may use
session-specific open/close conventions (e.g. CME globex session vs RTH settlement);
the daily `open` and daily `close` prints may **not** cleanly bracket the intended
overnight (prior-settle → next-open) window. Before any edge is believed:

- **S30-D3/D4 must verify** that the offline daily `open`/`close` for NQ (and ES)
  actually represent the overnight/day boundary the hypothesis assumes — e.g. that
  `overnight + day_session` reconstructs `total_day_return` exactly, and that the
  open/close timestamps correspond to a consistent session convention across the
  whole 2013–2022 window.
- **If the daily bar open/close cannot be trusted to represent the overnight/day
  split, the branch MUST STOP** and either (a) be re-scoped as requiring
  intraday/session-level data we do not currently have offline, or (b) be parked.
  No edge claim may be made on a mis-measured leg.

## 5. Direction (v1)

**Long overnight exposure only.**

- **Enter long at `close[t-1]`, exit at `open[t]`.** Hold the overnight leg only.
- **One overnight position per eligible trading day.**
- **No shorting in v1.**
- **No day-session exposure in v1** (the open→close leg is *measured for
  comparison* per §11 but never traded in v1).

**Why long-only overnight for v1:** it is the single cleanest expression of the
risk-premium hypothesis, matches the documented direction of the equity-index
overnight anomaly, fades nothing, stacks no filters, and keeps the first frozen test
unambiguous. A short or day-session variant is a **separate later branch**, not a v1
tweak.

## 6. Eligibility / no-trade filters

**v1 rule: ALL valid trading days are eligible. No trend filter. No RSI/EMA filter.
No volatility filter.** This tests the raw overnight effect directly and maximizes
the observation count (directly attacking the S27/S28 low-count failure).

- **Eligible day:** `close[t-1]` and `open[t]` both present, finite, and > 0;
  `t-1` and `t` are consecutive valid trading sessions (no gap across a data hole or
  holiday boundary that breaks the prior-close→next-open chain).
- **Excluded:** missing/invalid/zero open or close; the first bar of the dataset
  (no `t-1`); any bar where the session-consecutiveness assumption fails.
- **Considered and REJECTED for v1:** a volatility guard (e.g. skip when
  `ATR20[t-1]` is extreme). Rejected to avoid introducing a free parameter and an
  overfit surface; any such guard is a **new branch**, not a v1 option.

## 7. Entry and exit timing

- **Entry** at `close[t-1]`.
- **Exit** at `open[t]`.
- **Trade date = `t`.**
- **No same-bar lookahead** — the entry uses the known prior close; the exit is the
  next session's open.
- **No intraday stop or target in v1** — daily bars cannot observe the overnight
  path, so simulating an intra-overnight stop/target would be fabricated. The
  position is held flat from prior close to next open with **no path-dependent
  exit**.

## 8. R / accounting method

Because overnight drift is **small and frequent**, an R-based stop/target does not
fit v1 (there is no stop — §7). Accounting is therefore distribution-based:

- **Primary metric:** raw per-day overnight return in **points** and in **percent**
  (`(open[t] − close[t-1]) / close[t-1]`).
- **Secondary (normalized) metric:** an R-like volatility-normalized return,
  **`normalized_return = (open[t] − close[t-1]) / ATR20[t-1]`** (ATR20 = Wilder ATR
  over 20 daily bars, computed on data through `t-1` only — no lookahead).
- **Report both** raw and normalized where possible.
- **Do NOT force an artificial stop/target** if the daily data cannot support it.
  Frozen: `atr_period = 20`, normalization anchor = `ATR20[t-1]`.

## 9. Cost / friction assumptions

**Critical and pre-registered.** The overnight position is one round trip per day
(enter at prior close, exit at next open).

- Pre-register friction as a **per-round-trip cost** expressed in **points**, in
  **percent**, and as a **fraction of `ATR20[t-1]`**.
- Test at **multiple fixed cost levels** in the later friction module (§10, D12):
  **low / moderate / high / severe** (the exact point/percent values to be frozen in
  the S30-D3 engine constants before any run, then never changed).
- **Hard rule:** **if the expected per-day overnight edge is smaller than realistic
  friction, the branch FAILS.** A frequent tiny edge that does not clear cost is not
  a strategy — this is the explicit S26 (`FRICTION_SENSITIVE`) lesson applied up
  front.

## 10. Validation ladder plan (completed factory; nothing run now)

| Sub-step | Scope |
|---|---|
| S30-D3 | engine + tests only (frozen rules; no run) — **includes the §4 measurement-validity check as code** |
| S30-D4 | IS baseline 2013–2022 (`validation_is_runner`, hard 2023–2025 seal) + measurement-validity gate report |
| S30-D5 | OOS protocol pre-registration (`validation_oos_runner`); **commit before OOS** |
| S30-D6 | OOS run **once** (2023–2025) against the committed protocol |
| S30-D7 | distribution / overnight-significance (`validation_entry_significance`, adapted per §11) |
| S30-D8 | sequence risk / bootstrap + top-day dependence (`validation_sequence_risk`) |
| S30-D9 | regime breakdown (`validation_regime`) |
| S30-D10 | ES multi-market independent confirmation |
| S30-D11 | walk-forward stability (`validation_walk_forward`) |
| S30-D12 | friction stress at low/moderate/high/severe (`validation_friction`) |
| S30-D13 | final decision / readiness gate (`validation_decision`) |

## 11. Significance adaptation (pre-registered)

This is a **daily calendar exposure**, not sparse discrete entries, so the entry-
significance module is adapted to a **distribution test**:

- **Test A:** overnight returns vs **zero** (is the mean/median overnight return
  reliably positive?).
- **Test B:** overnight returns vs **day-session returns** (is the overnight leg
  reliably *different from / better than* the open→close leg? — isolates *when* the
  premium accrues).
- **Test C:** the real overnight sequence vs a **sign-flip / permutation / bootstrap
  baseline** (is the observed mean beyond what random sign/order produces?).
- **Fixed tests only.** No cherry-picking weekdays or months in v1. Any
  weekday/month/turn-of-month conditioning is a **separate pre-registered branch**,
  never added to v1 after seeing results.

## 12. Pass / watch / fail gates (pre-registered)

| Gate | PASS | WATCH | FAIL |
|---|---|---|---|
| Measurement validity (§4) | open/close cleanly reconstruct overnight/day split on full IS | minor reconcilable gaps | split not representable → **STOP/PARK** |
| IS observation count | thousands (≈ every eligible day 2013–2022) | hundreds | dozens (a measurement bug) |
| Mean overnight return (IS) | reliably > 0 | ~0 / marginal | ≤ 0 |
| Distribution health | positive median or acceptable skew; not one-sided tail | borderline | median ≤ 0 with mean propped by tail |
| Gain/loss (PF-like) or win rate | favorable & reported | borderline | unfavorable |
| Net after fixed friction | positive at moderate cost | positive only at low cost | negative at moderate cost |
| Top-day / fat-tail dependence | net stays positive after removing **top 1% of days AND top 3 days** | thin without them | net flips negative ex-top-days (**the universal parked-branch killer**) |
| Positive years | ≥6/10 | 5/10 | <5/10 |
| OOS | positive **after friction** | positive only pre-friction | negative after friction |
| ES corroboration | same direction & sign on ES | weak/mixed | ES contradicts NQ |
| Walk-forward | edge present across multiple eras | concentrated | only one era carries the result |

## 13. Anti-overfit rules

- No adding weekday / month / turn-of-month filters after any result (each is a new
  branch).
- No switching from the **overnight** leg to the **day-session** leg after seeing
  results.
- No changing `atr_period` (20) or the frozen friction levels after any result.
- No parameter sweeps; no grid search; no "best of N".
- No OOS run before the OOS protocol is pre-registered **and committed**.
- No paper/live promotion from the spec or from IS — requires a separate readiness
  memo with explicit override fields.
- Any rule change opens a **new branch** — S30 is never tuned in place.

## 14. Main expected failure modes

- **Measurement failure:** daily bar open/close do not represent the desired session
  boundary (the binding §4 gate) → any edge is an artifact.
- **Friction failure:** the per-day edge is too small to clear realistic cost (the
  S26 failure).
- **Regime concentration:** edge concentrated in crisis / high-vol years rather than
  durable across 2013–2022.
- **Tail risk:** overnight gaps create fat-tail losses (and/or the apparent edge is
  itself a few extreme up-gaps — the top-day-dependence gate).
- **No multi-market corroboration:** ES does not confirm NQ's direction.
- **Distribution fragility:** the mean depends on a handful of extreme days (the
  inverse risk to the count advantage).
- **Calendar/holiday artifacts:** futures session calendar / holiday handling breaks
  the prior-close→next-open chain and injects spurious "overnight" returns.

## 15. Final line

**“S30-D2 is a frozen hypothesis specification only; no strategy code, backtest,
OOS, optimization, paper trading, or live trading is authorized.”**

---

### Guardrails

`spec_only` · `no_code` · `no_backtest` · `no_is_oos_run` · `no_optimization` ·
`no_parameter_sweeps` · `no_data_fetch` · `no_paper_or_live` · `no_broker_or_api` ·
`no_source_engine_test_changes` · `oos_2023_2025_sealed` · `no_2026` ·
`donchian_s26_s27_s28_s29_read_only` · `crypto_d1_untouched` ·
`jarvis_templates_hydra_untouched` · `no_staging` · `no_commit`.

**Trading recommendation:** NONE. Frozen specification only. Donchian, S26, S27,
S28, S29 remain PARKED; no active strategy code; no paper/live system exists or is
authorized. The frozen S30 overnight-drift rules are a research hypothesis to be
tested under the factory ladder — gated first on measurement validity and friction —
not a trade.
