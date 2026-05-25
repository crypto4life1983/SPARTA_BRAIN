# s7 D1 — Cross-Asset Donchian No-Filter (NQ + GC + ZN + CL) — Spec DRAFT

**Status:** `DRAFT_SPEC_ONLY`
**Candidate record id (proposed):** `s7-cross-asset-donchian-no-filter-nq-gc-zn-cl`
**Phase:** Tier-N spec authoring — `BUILD_ONLY` track not yet authorized
**Authored:** 2026-05-25
**Author trace:** SPARTA Claude, drafting from sealed plan
`reports/external_research_hunter/s7_next_candidate_selection_after_five_parks.md`
(seal `8d8851bc365ef9a6eb7883b24f272d8462cb4bda9c9e725aa46415e1434f9eac`)

> **HARD BOUNDARIES (held by this spec).** Spec only. No code. No backtest.
> No Databento call. No QuantConnect call. No data fetch. No live trading.
> No paper bot change. No scheduler change. No `review_queue.json`
> mutation. No `obsidian-trade-logger` mutation. D5 (YM-only) is NOT
> revived. Rejected `B005_001` and `NKE Options Wheel` are NOT revived.
> Trading remains `PAUSED`. Live remains `BLOCKED_AT_6_GATES`. FRC never
> granted. No profitability claim.

> **Labels:** `EXTERNAL_CLAIM_ONLY` · `NEEDS_VERIFICATION` · `NOT_A_SIGNAL`
> · `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` · `PLAN_AND_SPEC_ONLY` ·
> `NO_FRC_GRANTED` · `S7_CANDIDATE_DRAFT`.

> **Inheritance.** All locked s6 strategy parameters and the Phase 2 safety
> template C1-C8 are inherited byte-equivalent. A fresh `candidate_record_id`
> + fresh sealed chain is mandatory; this spec does NOT modify any s2-s6
> sealed artifact.

---

## 1 · Strategy hypothesis

The s6 sealed parking report (`f6953c1f…`) falsified the hypothesis that
same-family 3-market diversification (NQ + ES + YM, ~0.88 avg pairwise
correlation) lifts a no-filter Donchian breakout strategy above breakeven
win-rate. The remaining unfixed hypothesis from the s5 → s6 chain is:

> **H1 (D1):** A cross-asset, no-filter Donchian breakout portfolio that
> samples four distinct Faith market families with average pairwise
> correlation < 0.5 — equity-index (NQ), metals (GC), bonds (ZN), and
> energy (CL) — will produce an effective independent-bet count
> ≥ 3.0 (vs s6's effective ~1.2-1.5), and that this true diversification
> will raise portfolio win rate above the P/L-implied breakeven threshold
> (estimated 16-18 % at P/L ≈ 4.7-5.2) and produce a portfolio Sharpe
> proxy > 0 across the locked in-sample window, without modifying any
> Faith mechanic.

The hypothesis is **falsifiable** by the K-criteria below. A pass is
**not** a profitability claim; it is permission to proceed to OOS
inspection under separate authorization.

**Null hypothesis (H0):** Diversification across Faith families does not
materially lift portfolio Sharpe, expectancy, or WR-vs-breakeven gap
relative to the parked s5 single-market and s6 same-family baselines. If
H0 holds, the trend-following family on this mechanic is empirically
exhausted across the s2-s7 chain and s8 should move to a different
strategy family (per s7 plan §"honest_qualification_for_operator").

---

## 2 · Why D1 was selected over D2 / D5

Direct quotes / paraphrase from the sealed plan (`s7_next_candidate_selection_after_five_parks.md`)
scoring matrix:

| Direction | Score | Rationale |
|---|---|---|
| **D1** Cross-asset Donchian (NQ+GC+ZN+CL) | **28 / 40** | Directly tests the **unfixed** s6 primary lesson (cross-family diversification with correlations <0.5). Preserves Faith's full mechanics. Strong first-principles rationale. Sample ≫ K9=100 likely (4 markets × ~64 trades ≈ 256). Per-market friction varies but no market is as high-friction as ES. |
| D2 No-pyramid (max_units=1) | 28 / 40 | Addresses s6 SECONDARY lesson (pyramid amplification) but **removes the alpha source** Faith designed in. Does **not** address s6 PRIMARY lesson. Reserved as data-cheap fallback. |
| D3 2-unit max | 25 / 40 | Ad-hoc tuning of Faith's deliberate 4-unit choice; no first-principles justification. |
| D4 Micro-only (MNQ+MES+MYM+M2K) | 23 / 40 | Same correlation structure as full-size (~0.88 same-family); does NOT address s6 PRIMARY lesson; same MES/MNQ friction ratio. |
| **D5 YM-only** | **12 / 40** | **EXPLICITLY RECOMMENDED AGAINST** — survivorship/cherry-pick overfit trap. Picking the best-performing market of 3 from a single in-sample run is textbook overfit. With 3 markets, a 1-of-3 positive result has ~50 % probability of being noise even at zero true edge. Sample inadequate (YM = 35 trades over 2013-2022, fails K9). |
| D6 Non-Donchian family | 21 / 40 | Premature without running D1; would discard 6 trend-following candidates without conclusive family-level falsification. |

**Selection rule cited in the sealed plan:** *"Choose the candidate that
MOST DIRECTLY tests the load-bearing remaining hypothesis from the parks.
5/5 parks have demonstrated that pyramid-based Donchian with
same-market-family universes does not lift above breakeven. The
remaining alternative — properly-diversified cross-family — has NOT been
tested. D1 is that test."*

**D5 prohibition.** This spec inherits the explicit `recommends_against_d5`
invariant from the sealed plan. D5 is not built, not specced, not
benchmarked against, and not auditable into D1 by ex-post substitution.

**Fallback.** If Databento downloads for GC, ZN, or CL are blocked or
priced out, the spec degrades to **D2** (`s7-no-pyramid-donchian-nq-es-ym`)
under a **separate fresh `candidate_record_id`** — never folded back into
this D1 chain. The fallback path is acknowledged here for operator
reference only and does not authorize D2 work.

---

## 3 · Exact markets and why each is included

All symbols stated as Databento `continuous-front-month` (`stype_in="continuous"`,
contract `.c.0`) on dataset `GLBX.MDP3` for NQ / GC / ZN / CL (CME group;
ZN is CBOT-listed but routes via the same GLBX MDP3 dataset on Databento).

| Symbol | Family | Exchange | Tick | Tick value | $/pt | Why included |
|---|---|---|---|---|---|---|
| **NQ.c.0** | Equity index (large-cap tech) | CME Globex | 0.25 | $5.00 | $20 | Cached locally (127 files); the only s5/s6 single-market with positive single-market signal in some windows. Anchor of the chain. |
| **GC.c.0** | Metals (gold) | COMEX (Globex) | 0.10 | $10.00 | $100 | Independent driver: safe-haven flows, real-rates, USD index inverse. Pairwise corr to NQ historically ≈ 0.0..0.2. Required for cross-family test. |
| **ZN.c.0** | Bonds (10-year Treasury note) | CBOT (Globex) | 1/64 of 1 % = $15.625 | $15.625 | $1000 (per 1 pt) | Independent driver: duration, Fed expectations, term-structure. Pairwise corr to equities is sign-variable depending on regime. **24h session — needs careful RTH-only filter (see §4).** |
| **CL.c.0** | Energy (WTI crude) | NYMEX (Globex) | 0.01 | $10.00 | $1000 | Independent driver: physical supply/demand, OPEC, geopolitics. Pairwise corr to equities low and unstable. **Front-month contango/backwardation affects continuous-front stitching nontrivially (see §12).** |

**Pairwise correlation prior (forecast at spec time, to be verified
empirically at smoke step).** Operator's prior, drawn from CFTC/QuantPedia
literature on cross-asset trend-following:

| | NQ | GC | ZN | CL |
|---|---|---|---|---|
| NQ | 1.00 | ~0.05–0.20 | sign-variable (regime) | low and unstable |
| GC | — | 1.00 | ~0.10–0.30 (real-rate cross) | low |
| ZN | — | — | 1.00 | low |
| CL | — | — | — | 1.00 |

Predicted average pairwise correlation: **<0.25** (vs s6 NQ+ES+YM
empirical ≈ 0.88). Predicted effective independent bets: **≥3.0** (vs
s6 ≈ 1.2-1.5). These predictions are testable at the in-sample smoke
step (§13.K-criteria K10 below).

**Symbols explicitly excluded** (and why):

- **ES, YM** — same family as NQ; s6 already falsified.
- **MES, MNQ, MYM, M2K** — micros; same family; D4 risk of same correlation.
- **Currencies (6E, 6J)** — out of scope for s7-D1; reserved for s8 if D1 parks.
- **VIX / VX** — term-structure carry, different mechanism, out of scope.
- **Anything not on GLBX.MDP3** — outside the locked Databento workflow.

---

## 4 · Session rules

| Field | Value | Rationale |
|---|---|---|
| Reference timezone | `America/New_York` (ET) | Match s6 + Faith convention. |
| Trading session per market | **RTH-only** (regular trading hours) | Avoids overnight illiquidity, halts, and the bond market's 24h session noise. |
| NQ RTH | 09:30 – 16:00 ET | CME equity-index futures RTH. |
| GC RTH | 09:30 – 16:00 ET (settlement window 13:30 ET pinned for daily close) | COMEX has overnight session; we restrict to RTH for daily-bar derivation. |
| ZN RTH | 09:30 – 16:00 ET | ZN trades nearly 24h; **explicit RTH filter required** to prevent overnight tape from polluting Donchian channels. |
| CL RTH | 09:30 – 14:30 ET (NYMEX pit-equivalent close window; CME extends to 17:00 but settlement is pinned at 14:30 ET) | Front-month CL settles 14:30 ET; daily bar derivation must align. |
| Daily-bar derivation | One daily OHLCV bar per market per RTH session | Donchian operates on daily bars (Faith standard). |
| Trade timezone for entry/exit | All decisions resolved at session close on the bar in question | Avoids look-ahead. |
| Holiday calendar | CME group holiday calendar (CME, COMEX, NYMEX, CBOT subsets) | A market is "closed" if its exchange is closed; portfolio simply does not trade that market that day. |
| Half-days | Skipped (do not count toward `trading_days_complete`) | Matches `path_to_live_decision.md` Track B rule. |
| Per-market trading-day count | Independent | A trading day for ZN may not be one for NQ; Donchian channel updates per-market on each market's own RTH bars. |
| Session boundary errors | Fail-closed: if RTH bar count for a session < expected (e.g., < 360 minutes for equities), drop the bar and flag in `session_warnings_per_market[symbol]` | s6 lesson: data warnings cannot silently pass. |

---

## 5 · Donchian breakout rule (inherited from s6 REV1, byte-equivalent)

> **Inheritance attestation.** The mechanic below is byte-equivalent to
> the s6 sealed REV1 Tier-N spec (`f3c727f627a5ff2c…`). Any deviation
> from these numbers is a parameter change and requires a fresh `_rev1_`
> chain off this spec.

| Parameter | Value | Inherited from |
|---|---|---|
| Entry channel length | **55 daily bars** | s4/s5/s6 (Faith System 1) |
| Exit channel length | **20 daily bars** | s4/s5/s6 (Faith System 1) |
| Channel construction | Donchian high/low over the **previous 55 closed RTH daily bars** (not including the current forming bar) | s6 REV1 |
| Long entry trigger | Today's RTH high > previous 55-bar high → market-on-close (MOC) entry on the breakout bar OR open-on-next-bar (ONO) at next RTH open, per `entry_timing_field` below | s6 REV1 |
| Short entry trigger | Today's RTH low < previous 55-bar low → MOC or ONO per `entry_timing_field` | s6 REV1 |
| Filter | **NONE** (no same-direction trend filter, no MA filter, no regime filter, no correlation gate) — `AMB6` structurally locked to NONE for any no-filter descendant per s6 REV1 | s6 REV1 |
| Pyramid step | **+0.5 N** above (long) / below (short) the prior unit's entry, where N = Wilder ATR(20) of the entry market | s6 REV1 |
| Max units per market | **4** | s6 REV1 |
| Exit on opposite Donchian | Long exits if today's RTH low < previous 20-bar low; short exits if today's RTH high > previous 20-bar high | s6 REV1 |
| `entry_timing_field` | `ONO` (open-on-next-bar) | s6 REV1; reduces close-of-bar slippage and matches Faith's lifecycle. The spec records this field explicitly so QC/local-engine implementations cannot drift. |

---

## 6 · Entry rule

1. At each market's RTH session close, evaluate the long and short
   Donchian-55 triggers (§5).
2. If a trigger fires AND the per-market open-unit count for this market
   is < 4 AND the global per-symbol coordinator does not block the side,
   queue an `ENTRY_PENDING` for the next RTH open (`ONO`).
3. At next RTH open, place a market order at the open price; record
   fill price for slippage accounting (see §10).
4. On fill, compute `N = WilderATR(20)` of the entry market at the
   triggering bar (NOT the fill bar). Store `N_entry_unit_<k>`.
5. Set initial stop at **2 × N** below long entry / above short entry
   (see §8).
6. Set the next pyramid trigger at **+0.5 × N** above (long) / below
   (short) the just-filled price.
7. **No same-symbol opposite-direction entry** while any unit is open
   for that market (matches `obsidian-trade-logger/config/trade_coordinator_config.json`
   `block_opposite_direction=true` convention; this spec does NOT touch
   that file, only mirrors its policy for its own portfolio coordinator).
8. Entries are evaluated per market independently — there is no
   cross-market gate, no correlation filter, no risk-budget rebalancing
   at entry time.

---

## 7 · Exit rule

1. At each market's RTH session close, evaluate the Donchian-20 exit
   trigger for every open unit in that market (§5).
2. If the trigger fires, queue an `EXIT_PENDING` for ALL open units in
   that market on that side; exit at next RTH open (`ONO`).
3. Stop-loss exit is handled separately (§8): if the stop is touched
   intra-bar, exit at the stop price plus slippage (no waiting for
   close).
4. There is **no time-stop**, **no profit target**, **no trailing rule
   above the Donchian-20**.
5. On final unit exit, mark the trade group closed and write the row
   to `trades.csv` (§15).

---

## 8 · Stop rule

| Parameter | Value | Source |
|---|---|---|
| Initial stop distance per unit | **2 × N** (Wilder ATR(20) of entry market at trigger bar) | Faith System 1 |
| Stop direction | Below entry for long; above entry for short | Faith |
| Per-unit stop persistence | Each unit has its own stop, locked at unit-entry time; does NOT trail on Donchian-20 (Faith System 1 default) | Faith / s6 REV1 |
| Stop hit handling | Intra-bar trigger → exit that unit at stop price + slippage immediately; remaining open units unaffected | s6 REV1 |
| Stop and exit-channel interaction | If BOTH the Donchian-20 exit and the stop fire on the same day, the **earlier intra-day timestamp wins**; if both at the close, exit-channel exits at next RTH open and stop exits intra-bar | spec-level disambiguation; consistent with s6 |
| No moving stop | Stops do not move with the channel; this is intentional inheritance | Faith |
| Catastrophic stop (chain-level) | Portfolio MaxDD > 50 % triggers K4 → park the candidate immediately at end-of-day (§14) | s6 K4 |

---

## 9 · Position sizing rule

| Parameter | Value | Source |
|---|---|---|
| Capital basis | **Portfolio equity** (mark-to-market, end of prior RTH day) — single shared equity across all 4 markets | s6 REV1 §13 |
| Per-unit dollar risk | **1.0 % of portfolio equity** | Faith; s6 REV1 |
| Per-unit contract count | `floor( (0.01 × portfolio_equity) / (N_entry × $/pt) )` where `$/pt` is the per-market dollar value (NQ $20, GC $100, ZN $1000, CL $1000) | Faith |
| Minimum contract size | If computed contract count < 1, **the unit is skipped** (do not partial-fill) and the skip is logged to `entry_skip_log.jsonl` | s6 REV1 |
| Pyramid units | Up to **4** per market; each subsequent unit re-uses the SAME `N_entry` value (the N at the first unit's entry — units 2-4 do NOT recompute N on their own entry bar; this matches Faith) | s6 REV1 |
| Portfolio cap | At most `4 markets × 4 units = 16 units` open across the portfolio at any one time. **`PortfolioCapTracker.update_market_units()` must pass `pyr.current_unit_count` (the UNIT count, max 4 per market), NOT `pyr.total_quantity` (the contract count).** This is the explicit fix from s6's `portfolio_cap_bugfix_report` (`fa232ca1…`) — any future implementation MUST inherit this fix; regression tests below enforce it. | s6 portfolio_cap_bugfix |
| Starting cash | **$100,000 MNQ-equivalent** notional accounting (so per-market dollar P&L converts to a unified portfolio number; NQ is the reference market) | s6 REV1 |
| Per-trade quantity field | Unit count, persisted alongside contract count, in `trades.csv` for cap auditability | s6 lesson |
| Sizing under data outage | If the entry-day Wilder ATR(20) cannot be computed (insufficient prior bars), the entry is skipped and logged | spec |

---

## 10 · Cost / slippage assumptions

Locked at spec time; loosening these post-seal is a `threshold_lock_invariant`
violation.

| Cost component | NQ | GC | ZN | CL | Source |
|---|---|---|---|---|---|
| Commission per RT | $3.00 | $3.00 | $3.00 | $3.00 | CME-typical broker commissions; conservative |
| Exchange + clearing fees per RT | $1.50 | $1.50 | $1.20 | $1.50 | CME fee schedules (front-month) |
| **Total per RT (commission + fees)** | **$4.50** | **$4.50** | **$4.20** | **$4.50** | sum |
| Slippage per entry | **1 tick** | **1 tick** | **1 tick** | **1 tick** | s6 baseline |
| Slippage per stop-out | **2 ticks** (adverse stop-fill assumption) | **2 ticks** | **2 ticks** | **2 ticks** | conservative |
| Slippage per Donchian-20 exit | **1 tick** | **1 tick** | **1 tick** | **1 tick** | s6 baseline |
| Funding / overnight | None (futures, no carry charged) | None | None | None | — |
| Roll cost | See §12 (roll handling); modeled as 1 spread tick at roll | same | same | same | spec |

**Slippage in dollar terms** (1 tick = NQ $5, GC $10, ZN $15.625, CL $10).

**Cost-stress matrix (locked at spec time).** Inherits the s6 / B005
DR2/DR3/DR5 stress pattern. The in-sample run produces five cost tiers:

| Tier | Slippage scalar | Commission/fee scalar | Purpose |
|---|---|---|---|
| **S0** | 0× (zero slippage) | 0× (zero costs) | Diagnostic floor — DR3 fires if survival is S0-only |
| **S1** | 1× (above) | 1× | Baseline preregistered |
| **S2** | 3× | 1.5× | Mild stress |
| **S3** | 5× | 2× | Realistic adverse |
| **S4** (reserved) | 8× | 3× | Tail stress — does not affect park verdict; reported for analysis only |

DR rules (inherited from B005_001 / NKE chain):

- **DR2** — `oos_metrics_degrade_materially_under_S2_or_S3_cost_stress` → `REJECT_FAST`
- **DR3** — `zero_cost_only_survival` (S0 positive, S1+ negative) → `REJECT_FAST`
- **DR4** — IS positive but OOS negative at S0 baseline → escalate to operator review
- **DR5** — `cost_stress_turns_edge_negative` between S0 and S1 → `REJECT_FAST`

**S5 stress (sizing stress)** — sizing scalar S1×S3 = 0.5× and 2× of
locked 1 %-risk sizing — REPORTED but informational at spec stage; the
park trigger remains S0-S3 cost cells.

---

## 11 · Data requirements

| Field | Value |
|---|---|
| Source of record | **Databento** `GLBX.MDP3` dataset (primary). QC Cloud history is the fallback ONLY for date gaps Databento doesn't cover. |
| Schema | `ohlcv-1m` (minute bars; daily bars derived RTH-only per §4) |
| `stype_in` (continuous) | `continuous` (front-month, `*.c.0`) |
| `stype_in` (per-contract, for diagnostics) | `parent` |
| Symbols | `NQ.c.0`, `GC.c.0`, `ZN.c.0`, `CL.c.0` |
| In-sample window | **2013-01-01 → 2022-12-30 (UTC)** — matches s4/s5/s6 lock |
| OOS window | **2023-01-01 → 2025-12-30 (UTC)** — DO NOT INSPECT until in-sample passes K-criteria (`oos_inspection_blocked_at_in_sample` invariant) |
| Local cache check (pre-fetch) | Probe `data/databento_cache/<symbol>/<YYYY-MM>/*.parquet` (or `.dbn.zst`) — abort the fetch step entirely if all four roots are fully cached |
| Fresh-download budget (operator-managed) | **GC, ZN, CL** — 3 fresh roots × ~10 years × ohlcv-1m. NQ is already cached. **Operator-side download only**; this spec does NOT authorize a fetch. |
| API-key handling | `os.environ.get("DATABENTO_API_KEY")` only. **NEVER print, log, echo, or persist the key.** Inherits the boundary from `docs/mnq_databento_first_qc_fallback_workflow.md`. |
| Data-quality gates at load time | Bar-count expectations per RTH session per market; NaN/zero-volume → bar dropped + logged in `data_quality_warnings.json`; ≥0.5 % bar-drop rate in any single year → fail-closed with `data_quality_failed` |
| Calendar alignment | CME group official holiday calendar; per-market trading days enumerated and persisted to `calendar_attestation.json` |
| Time zone of timestamps | All persistence in UTC; ET conversion only at session-boundary computation |

---

## 12 · Roll / contract handling assumptions

Continuous front-month series (`*.c.0` on Databento) implies pre-stitched
rolls. The spec **does not** re-roll inside the engine; it consumes the
stitched series. However:

| Topic | Assumption |
|---|---|
| Roll method | Databento `continuous` series, **`back-adjusted price-ratio` stitch** preferred. If Databento defaults to `back-adjusted price-difference`, accept that and log the choice in `data_provenance.json`. |
| Roll cost | Modeled as **1 spread-tick** per market on each roll date — added to that day's PnL (exit/re-enter assumption not used; we simulate carrying the position across the stitch and absorb 1 tick of artifact). |
| Roll calendar | Read from Databento's `definition` schema for each market's standard front-month roll convention (typically calendar-based: NQ Mar/Jun/Sep/Dec; GC Feb/Apr/Jun/Aug/Oct/Dec; ZN Mar/Jun/Sep/Dec; CL monthly). |
| Stitch artifact attestation | Each roll date is enumerated in `roll_attestation.json` with `(symbol, roll_date, prior_contract, next_contract, stitch_method, modeled_cost_dollar)`. |
| Carry / contango effect | For CL especially, contango/backwardation affects the back-adjusted series shape. The spec accepts this as a known continuous-series property and does not attempt to detrend. |
| OOS roll integrity | OOS roll calendar must match in-sample method (no method drift); enforced by `roll_method_drift == False` at OOS gate. |
| Manual roll override | **Disallowed.** Any manual override invalidates the chain and forces a fresh `_revN_` spec. |

---

## 13 · Acceptance gates (in-sample, locked)

A pass requires **ALL** of the following at the in-sample close-out:

| Gate id | Description | Threshold | Source |
|---|---|---|---|
| `A1` | Closed-trade portfolio sample size | `closed_trades_portfolio ≥ 100` (K9 inverse) | s6 K9 |
| `A2` | Portfolio Sharpe proxy (per-trade) | `sharpe_proxy_per_trade > 0` (K1 inverse) | s6 K1 |
| `A3` | Portfolio expectancy per trade | `expectancy_per_trade_mnq_equivalent > 0` (K2 inverse) | s6 K2 |
| `A4` | Trade-curve MaxDD | `trade_curve_maxdd_pct ≤ 50.0` (K4 inverse) | s6 K4 |
| `A5` | Per-market WR gap vs P/L-implied breakeven | At least **2 of 4** markets show `win_rate_gap_to_breakeven_pp ≥ 0` AND portfolio WR-gap `≥ +0.5 pp` | tightened from s5/s6 (where the gap was negative); falsifiable directional read |
| `A6` | Validator | `VALIDATOR_PASS` 16/16 (inherits s6 validator suite + s7-specific cross-market additions, e.g., `corr_attestation_present`) | s6 validator |
| `A7` | Effective independent bets | `effective_independent_bets ≥ 2.5` (estimated from empirical pairwise correlations across the in-sample window) | new for D1 — directly tests the load-bearing hypothesis |
| `A8` | Cost-stress survival | NOT a pass-gate; ALL FIVE tiers (S0..S4) are RUN and the cost-stress matrix is sealed. DR2/DR3/DR5 trigger REJECT_FAST (§14). Passing A1-A7 at S1 baseline AND not firing DR2/DR3/DR5 at S2/S3 is the practical pass band. | s6 / B005 |
| `A9` | Safety-template C1-C8 inheritance | All 8 Phase 2 safety contracts attestable as True | Phase 2 safety template |
| `A10` | Cap binding events | `cap_binding_events_count == 0` at portfolio level (cap structurally non-binding at 4 markets × 4 units = 16; the s6 bugfix must be inherited) | s6 portfolio_cap_bugfix |

If `A1` is missed (sample < 100 across the full 10-year in-sample), the
candidate parks as `PARKED_FAILED_AT_INSUFFICIENT_SAMPLE` (matches s4
pattern). If `A1` passes but ≥1 of `A2/A3/A4` fails, candidate parks as
`PARKED_SAFE_BUT_NOT_MONEY_PROVEN` (matches s5/s6 pattern). A combined
A1-A10 pass authorizes ONE further operator-decision turn to authorize
OOS inspection — **the spec does NOT pre-authorize OOS**.

---

## 14 · Rejection gates (kill criteria, locked)

K-criteria are evaluated at in-sample close and (if reached) at OOS close.
Any K firing **immediately** parks the candidate:

| K | Trigger | Park status |
|---|---|---|
| `K1` | `portfolio_sharpe_proxy_per_trade < 0` | `PARKED_SAFE_BUT_NOT_MONEY_PROVEN` |
| `K2` | `expectancy_per_trade ≤ 0` | `PARKED_SAFE_BUT_NOT_MONEY_PROVEN` |
| `K3` | (reserved, not used at D1) | — |
| `K4` | `trade_curve_maxdd_pct > 50` | `PARKED_SAFE_BUT_NOT_MONEY_PROVEN` |
| `K5` | (reserved) | — |
| `K6` | `safety_warning_count > 0` (any non-zero in §16 §C1-C8 checks) | `PARKED_SAFETY_FAILED` |
| `K7` | `filter_silently_introduced_attestation == True` OR `correlation_gate_silently_introduced_attestation == True` | `PARKED_SAFETY_FAILED` |
| `K8` | `sealed_parent_drift > 0` (any inherited s6 sealed sha changes during the run) | `PARKED_PROVENANCE_BROKEN` |
| `K9` | `closed_trades_portfolio < 100` | `PARKED_FAILED_AT_INSUFFICIENT_SAMPLE` |
| `K10` | `avg_pairwise_correlation > 0.50` over the in-sample window (i.e., the cross-asset hypothesis is itself wrong empirically) | `PARKED_FAILED_AT_DIVERSIFICATION_HYPOTHESIS` |
| `K11` | `cap_binding_events_count > 1000` (NOTE: in s6 this was a false positive resolved by the cap-bugfix; the threshold remains but the inherited fix should yield 0) | `PARKED_CAP_BINDING` |
| `K12` (REJECT_FAST) | DR2 / DR3 / DR5 fire on the cost-stress matrix | `REJECT_FAST` |

**Threshold-lock invariant.** Loosening any K threshold post-seal is
forbidden. Tightening is a fresh `_revN_` spec.

---

## 15 · Required output files (locked artifact set)

All paths relative to the SPARTA_BRAIN repo root unless noted. Naming
mirrors the s6 / B005 chains so the s7 chain can be validator-compared
to its predecessors.

| Path | Purpose |
|---|---|
| `external_research_hunter/s7_d1_cross_asset_donchian_runner_harness/main.py` | The locked LEAN/QC- (and/or local-engine-) compatible runner. Author in BUILD phase, not now. |
| `external_research_hunter/s7_d1_cross_asset_donchian_runner_harness/execution_guard.py` | The runtime safety guard (per Phase 2 §C5). |
| `external_research_hunter/s7_d1_cross_asset_donchian_runner_harness/README.md` | Runner README, including the sha-pinned spec hash. |
| `reports/external_research_hunter/s7_d1_cross_asset_donchian_tier_n_spec.{md,json}` | Sealed Tier-N spec authored in the next turn (after operator approval of this DRAFT). |
| `reports/external_research_hunter/s7_d1_cross_asset_donchian_plan_lock.{md,json}` | Sealed plan lock (BUILD/run authorization, post-spec-seal). |
| `reports/external_research_hunter/s7_d1_cross_asset_donchian_phase2_plan.{md,json}` | Sealed Phase 2 plan doc with the §C1-C8 safety inheritance. |
| `reports/external_research_hunter/s7_d1_cross_asset_donchian_runner_build_report.{md,json}` | After BUILD: file shas, lint, smoke-import. |
| `reports/external_research_hunter/s7_d1_cross_asset_donchian_execution_guard_build_report.{md,json}` | Guard build report. |
| `reports/external_research_hunter/s7_d1_cross_asset_donchian_pre_execution_local_verification_snapshot.{md,json}` | H3a-local-verify snapshot before any operator-side execution. |
| `reports/external_research_hunter/s7_d1_cross_asset_donchian_t1_t15_smoke_pass_report.{md,json}` | T1-T15 smoke harness pass. |
| `reports/external_research_hunter/s7_d1_cross_asset_donchian_in_sample_diagnostic_result_sealed.{md,json}` | In-sample run output; sealed canonically (per LESSON_HUNTER_004 roundtrip recipe). |
| `reports/external_research_hunter/s7_d1_cross_asset_donchian_in_sample_decision_memo.{md,json}` | Memo: K-fires, A-gates, verdict. |
| `reports/external_research_hunter/s7_d1_cross_asset_donchian_<PARKING_or_PROCEED>_report.{md,json}` | Lifecycle transition action (one of: PARKING / OOS-AUTHORIZED / REJECT_FAST). |
| `reports/external_research_hunter/s7_d1_cross_asset_donchian_local_backtests/PHASE2-S7-XAD-NF-<run_id_8>.json` | Raw per-run diagnostic JSON (matches s6 path convention). |
| `data/databento_cache/{NQ,GC,ZN,CL}/<YYYY-MM>/...` | Operator-side cache; this spec ONLY enumerates the path — no fetch is authorized. |
| `data/calendar_attestation/<run_id>.json` | Per-market RTH trading-day enumeration. |
| `data/roll_attestation/<run_id>.json` | Per-market roll enumeration. |
| `data/data_quality_warnings/<run_id>.json` | Bar-drop / NaN warnings per run. |
| `logs/entry_skip_log/<run_id>.jsonl` | Entries skipped due to contract-count < 1, ATR-unavailable, RTH-bar-count fail, etc. |

**Naming invariant.** `s7_d1_cross_asset_donchian_*` is the locked prefix.
No other s7-variant may write under this prefix.

**Seal recipe.** All `.json` outputs MUST use the LESSON_HUNTER_004 canonical
roundtrip: build the payload, `json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False)`,
`json.loads` it back, re-`dumps` for seal computation, hash with sha256, embed
`report_seal_sha256` at the top level. The companion `.md` carries the sha
in a `seal block` matching the s6 / B005 format.

---

## 16 · Validation checklist

A run is `VALIDATOR_PASS` iff all 16 items below resolve True. The
in-sample close cannot record a verdict without this.

1. `spec_sha_matches_recorded` — runner declares the Tier-N spec sha it
   inherited; matches the sealed spec.
2. `phase2_safety_template_inherited_byte_equivalent` — `phase2_safety_template_md_sha256` and `_json_sha256` MATCH the inherited values (`1812f485…8981` and `695a9fb6…4a32`).
3. `s2_through_s6_sealed_chains_byte_stable` — sha hashes of all 5 prior parking reports + their decision memos UNCHANGED at start AND end of run; `sealed_parent_drift == 0`.
4. `no_d5_revival` — no `s7-ym-only*` artifact exists.
5. `no_b005_001_revival` — `b005_001_archival_memo.{md,json}` byte-unchanged.
6. `no_nke_revival` — NKE sealed-chain shas byte-unchanged.
7. `markets_enumerated_exactly_4` — runner declares `markets = ['NQ','GC','ZN','CL']`; nothing else.
8. `rth_only_filter_attested` — each market shows non-empty `rth_session_window` config and zero non-RTH bars in the daily-bar derivation log.
9. `donchian_55_20_attested` — entry/exit channel lengths logged and == (55, 20).
10. `pyramid_max_4_attested` — at no point in the run did any market exceed 4 open units; max observed value logged.
11. `n_calculation_used_entry_market_at_trigger_bar` — `N` values logged and unique per unit-group; not recomputed mid-trade.
12. `portfolio_cap_uses_unit_count_not_contract_count` — the cap-bugfix inherited verbatim; regression test passes.
13. `cost_stress_matrix_S0_S1_S2_S3_S4_present` — all five tiers in the matrix; DR2/DR3/DR5 evaluated.
14. `seal_roundtrip_recompute_match` — Python-recompute of `report_seal_sha256` MATCHES the embedded value.
15. `no_oos_inspection_in_in_sample_run` — OOS window absent from any in-sample diagnostic JSON; the runner refuses to read 2023+ bars in the in-sample mode.
16. `boundaries_held` — `no_live_trading`, `no_brokerage_connection`, `no_review_queue_mutation`, `no_strategy_lab_promotion`, `no_obsidian_trade_logger_mutation`, `no_credential_logged`, `no_databento_key_printed`, `no_qc_api_call_in_local_path`. All True.

---

## 17 · What would count as overfitting

Each of the following is a **structural overfit** indicator. Any one
firing at decision time → the candidate must NOT be advanced regardless
of K/A status; the operator memo must record the indicator explicitly.

- **OI1** — Cherry-picking 1-of-N markets after seeing in-sample results
  (the D5 trap). At decision time, the verdict must be computed over
  the locked 4-market portfolio, never over a subset.
- **OI2** — Loosening any K threshold after seeing the in-sample
  result. The threshold-lock invariant fires.
- **OI3** — Re-running the in-sample with a tweaked parameter (entry
  length ≠ 55, exit ≠ 20, pyramid ≠ 4, stop ≠ 2N, sizing ≠ 1 %) and
  reading off the better number. Any parameter change requires a fresh
  `_revN_` chain.
- **OI4** — Substituting a market post-hoc (e.g., dropping CL when CL
  loses money, replacing with ES). Market list is locked at spec seal.
- **OI5** — Adjusting the in-sample window to dodge a bad stretch (the
  classic "let's start in 2015 instead of 2013"). Window is locked.
- **OI6** — Adding a regime filter, correlation gate, or
  same-direction-as-trend filter after seeing in-sample losses.
  `filter_silently_introduced_attestation` must remain False.
- **OI7** — Inspecting OOS before in-sample passes. Any OOS read
  contaminates the OOS window — even glancing at OOS numbers in an
  IDE counts.
- **OI8** — "Stress matrix bias review" used to overturn a REJECT_FAST.
  Per LESSON_HUNTER_007, the preregistered rule fires regardless of
  whether the stress matrix has known accounting bias; a separate
  operator-authorized turn can re-compute, but cannot retroactively
  unpark a candidate.
- **OI9** — Reading in-sample numbers for s7-D1 alongside the s7
  selection plan's "estimated benefit" qualitative language, then
  retro-fitting commentary. The estimates in §1/§3 are forecasts; the
  comparison is empirical, not narrative.
- **OI10** — Adopting D5 (YM-only) as a "sub-analysis" of D1. D5 stays
  prohibited.

---

## 18 · What would make us stop immediately

Any of the following triggers an **IMMEDIATE STOP** of the in-sample
run (mid-run) and a `PARKED_SAFETY_FAILED` or `PROVENANCE_BROKEN`
disposition. No data is read after the trigger fires.

- **S-STOP-1** — A sealed parent's sha256 changes mid-run
  (`sealed_parent_drift > 0`). Inheritance broken; chain invalid.
- **S-STOP-2** — Any non-zero safety warning from the Phase 2
  template §C1-C8 (pyramid state-machine violation, N drift, unsupported
  order type, stale fill, extended-hours fill, rollover violation,
  silently-introduced filter, silently-introduced correlation gate).
- **S-STOP-3** — DATABENTO_API_KEY appears in any log line. Hard stop;
  rotate the key.
- **S-STOP-4** — The runner attempts a network call to a host not on the
  Databento allowlist OR makes a QC API call from the local-engine path.
- **S-STOP-5** — Any write to `review_queue.json`, `idea_memory`, the
  Strategy Lab approval files, or `obsidian-trade-logger/**`.
- **S-STOP-6** — Any attempt to instantiate a broker, exchange, or
  Kraken/Binance/Alpaca adapter. Trading code must be unreachable from
  the diagnostic runner.
- **S-STOP-7** — Any K6/K7 (safety) fire during the run is the strongest
  stop signal; the run aborts and the per-event line is sealed into
  `s7_d1_..._safety_abort_report.json`.
- **S-STOP-8** — Data quality fail (data_quality_failed: bar-drop rate
  ≥0.5 % in any year, or NaN OHLCV bars > spec threshold). The run is
  paused, not failed; the operator is shown the `data_quality_warnings.json`
  and decides whether to re-fetch or rebuild the cache.
- **S-STOP-9** — Operator-issued `STOP_S7_D1` instruction in any
  upstream turn or in `staged/` (kill-switch convention).
- **S-STOP-10** — Detection that the spec sha shown in the runner ≠
  the sealed Tier-N spec sha (drift introduced between spec seal and
  BUILD). Force fresh `_revN_`.

---

## 19 · Next step after spec approval

The next operator-authorized turn — and ONLY the next — is:

1. **Operator reads this DRAFT** (`docs/s7_d1_cross_asset_donchian_spec.md`)
   and either:
   - returns specific change requests, OR
   - issues an explicit "AUTHORIZE TIER-N SPEC SEAL FOR `s7-cross-asset-donchian-no-filter-nq-gc-zn-cl`"
     instruction, with the spec content here treated as the input
     payload.

2. On AUTHORIZE, SPARTA Claude produces (in a single new turn) the
   **Tier-N spec** at `reports/external_research_hunter/s7_d1_cross_asset_donchian_tier_n_spec.{md,json}`
   with the LESSON_HUNTER_004 canonical seal recipe and the locked
   parameters above. **This is still spec-only**; no code, no fetch,
   no execution.

3. After Tier-N spec seal, the **separately-authorized** turns are
   (each its own operator approval):
   - (a) **Plan-lock authoring** (`s7_d1_..._plan_lock.{md,json}`).
   - (b) **Phase 2 plan doc authoring** (`s7_d1_..._phase2_plan.{md,json}`).
   - (c) **BUILD ONLY** — runner + execution_guard + tests scaffolded
     under `external_research_hunter/s7_d1_cross_asset_donchian_runner_harness/`.
     No fetch, no run.
   - (d) **T1-T15 smoke pass** on synthetic fixtures only.
   - (e) **Operator-side Databento fetch** (3 fresh roots: GC, ZN, CL).
     Operator-managed; SPARTA Claude only receives the post-fetch
     local cache state.
   - (f) **In-sample run** at S0-S4 cost tiers; produces the sealed
     diagnostic JSON.
   - (g) **In-sample decision memo** with K/A verdicts.
   - (h) **Lifecycle transition** (PARK or OOS-AUTHORIZE).

Steps (a)-(h) each require an explicit operator authorization line;
none are pre-approved by this spec.

**What this DRAFT does NOT do.** It does not seal a Tier-N spec. It
does not authorize any of steps (a)-(h). It does not authorize a
Databento fetch. It does not authorize a QC submit. It does not
authorize any change to the live or paper trading systems. It does
not modify `review_queue.json`. It does not modify or revive any
parked or rejected candidate.

---

## Appendix · Inherited constants registry (for re-verification at seal time)

The seal of this spec at the next turn will pin these inherited shas;
operator can re-verify byte-stability before authorizing BUILD:

| Inherited artifact | Recorded sha256 (from sealed s7 plan) | Inheritance reason |
|---|---|---|
| `s7_parking_chain_anchor` (= s6 parking report) | `f6953c1fb3c334d34572aa7dac29317b4ff412bf3648db62276707ef9de2894a` | s6 chain of parents |
| `s6_decision_memo` | `c2489d468a026a940a5e6f02c2243fccb6065dd37aace78a5498c342a68fac11` | s6 in-sample memo |
| `s6_phase2_plan` | `e9db90cc124058eebf72f950567664bdcc64b8c9070c312dad0e9b335a856493` | inherited phase-2 plan |
| `s6_plan_lock` | `e384e37990ac1c1be9ca7ad2ebdc4dd06fb8c0f3fd2b6cbe8861e52b878d12fd` | plan-lock inheritance |
| `s6_rev1_tier_n` (parameter inheritance) | `f3c727f627a5ff2c45365da4af51c21effad8bf5d62394bcb4687f5451bff1ee` | byte-equivalent Donchian params |
| `s5_parking_report` | `6c308b42da6854d5dd3f8e8936fb5299666dae3158904bec65ec6458156f234c` | upstream parking |
| `s5_decision_memo` | `9ee7981f26340f8ff8710a6e635d5337e5f6a8622fd8b63195db0bb7d9486e29` | upstream memo |
| `s4_parking_report` | `8cda3ca644524cd558cc3a1291a869d983a8c5fae9c1d0f15d6e56ba266a1cb4` | upstream |
| `s3_parking_report` | `1f557888e1212d6ffe0e305ac43308977f618db7473b22c90e407fe805d3f7ad` | upstream |
| `phase2_safety_template_md` | `1812f4854a23e7a148257c88133042ea1e383725f4875e762475260ae3658981` | C1-C8 inheritance |
| `phase2_safety_template_json` | `695a9fb6e0cb6ae5395d467471f2c55d3d90a7030443ca87e4c1d220335f4a32` | C1-C8 inheritance |
| `s7_selection_plan_seal` | `8d8851bc365ef9a6eb7883b24f272d8462cb4bda9c9e725aa46415e1434f9eac` | direct parent of this spec |

**Drift count at this DRAFT:** `0` (audit conducted 2026-05-25;
all parents byte-stable per the source plan).

---

*End of `s7_d1_cross_asset_donchian_spec.md` DRAFT. Spec only — no code,
no backtest, no Databento, no QuantConnect, no fetch, no live or paper
trading, no scheduler change, no obsidian-trade-logger mutation, no
review_queue mutation, no D5 revival, no rejected-candidate revival.
Awaiting operator approval before Tier-N spec seal.*
