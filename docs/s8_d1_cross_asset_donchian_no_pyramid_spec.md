# s8 D1 — Cross-Asset Donchian No-Pyramid (NQ + GC + ZN + CL) — Spec DRAFT

**Status:** `DRAFT_SPEC_ONLY`
**Candidate record id (proposed):** `s8-cross-asset-donchian-no-pyramid-nq-gc-zn-cl`
**Phase:** Tier-N spec authoring — `BUILD_ONLY` track not yet authorized
**Authored:** 2026-05-25
**Author trace:** SPARTA Claude, drafting from sealed S8 selection plan
`reports/external_research_hunter/s8_next_candidate_selection_after_six_parks.md`
(seal `6b7bdb4c350f4a779611546dcb32f6a83db2371c66d7b6ba0118121783801441`)

> **HARD BOUNDARIES (held by this spec).** Spec only. No code. No backtest.
> No Databento call. No QuantConnect call. No data fetch. No live trading.
> No paper bot change. No scheduler change. No `review_queue.json`
> mutation. No `obsidian-trade-logger` mutation. **s7-D1 is permanently
> parked at commit `f08220a` and is NOT revived by this spec — only used
> as upstream evidence and mechanical baseline.** Rejected `B005_001`,
> `NKE Options Wheel`, and the s7 selection plan's D5 (YM-only) are NOT
> revived. Trading remains `PAUSED`. Live remains `BLOCKED_AT_6_GATES`.
> FRC never granted. No profitability claim.

> **Labels:** `EXTERNAL_CLAIM_ONLY` · `NEEDS_VERIFICATION` · `NOT_A_SIGNAL`
> · `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` · `PLAN_AND_SPEC_ONLY` ·
> `NO_FRC_GRANTED` · `S8_D1_CANDIDATE_DRAFT` ·
> `SINGLE_DELTA_FROM_S7_D1_MAX_UNITS_1`.

> **Inheritance.** All locked s7-D1 strategy parameters EXCEPT
> `max_units_per_market` are inherited byte-equivalent. The single delta
> is `max_units_per_market = 1` (was 4). The Phase 2 safety template
> C1-C8 is inherited byte-equivalent. A FRESH `candidate_record_id` +
> FRESH sealed chain is mandatory; this spec does NOT modify any s2-s7-D1
> sealed artifact.

---

## 1 · Strategy hypothesis

The s7-D1 sealed chain (Tier-N spec `72602305…34c3` → ... → PARKING_REPORT
`551fdce4…4b32`) produced the cleanest possible decomposition of the
cross-asset trend-following arc:

- **Signal layer (validated):** cross-asset diversification (NQ + GC + ZN
  + CL, avg pairwise correlation <0.5) produced **313 closed trades** over
  10 years with **expectancy +$3,667/trade**, **win rate 43.13%** (which
  is **+14.17 pp ABOVE** the P/L-ratio-implied breakeven of 28.96%), and
  **3 of 4 markets profitable** (CL +$580k, NQ +$225k, ZN +$370k; only GC
  losing −$27k). Sharpe proxy per-trade +0.192.
- **Sizing layer (falsified):** 4-unit Donchian pyramid at 0.5N spacing
  produced **trade-curve MaxDD = −221.67%** — catastrophically exceeds
  the K4 = −50% threshold. K4 fired; the s7-D1 candidate parked as
  `PARKED_SAFE_BUT_NOT_MONEY_PROVEN`.

The remaining unfixed hypothesis from the s7-D1 chain is:

> **H1 (s8-D1):** A cross-asset Donchian-55 / Donchian-20 strategy on the
> same NQ + GC + ZN + CL universe, with `max_units_per_market = 1` (no
> pyramiding) and all other s7-D1 parameters preserved byte-equivalent,
> will **simultaneously**:
> (a) clear K1 (`portfolio_sharpe_proxy_per_trade > 0`),
> (b) clear K2 (`expectancy_per_trade > 0`),
> (c) clear K4 (`trade_curve_maxdd_pct ≤ 50%`),
> (d) clear K6/K7/K8/K9/K11 (safety + sample),
> across the locked in-sample window (2013-01-01 → 2022-12-30).

The hypothesis is **falsifiable** by the K-criteria below. A pass is
**not** a profitability claim; it is permission to proceed to a separate
operator-authorized cost-stress matrix + OOS authorization turn.

**Null hypothesis (H0):** Removing pyramid removes Faith's primary
alpha-amplification mechanism (winners truncated at 1 unit); per-trade
expectancy collapses below zero or Sharpe goes negative. If H0 holds, the
cross-asset Donchian family is **decisively falsified** — the family
needs pyramid to be profitable, but pyramid causes catastrophic DD. The
family is unsalvageable; the natural s9 direction is **D3 (different
family entirely)** per the S8 selection plan §candidate_directions.

**Outcome decision-rule cited in the S8 selection plan
`recommendation.honest_interpretation_of_d1_possible_outcomes`:**

| Outcome | Disposition |
|---|---|
| H1 holds (K1, K2, K4 all pass) | First viable candidate in the chain. Operator decides next step (cost-stress matrix, then OOS authorization). |
| H1 fails K1 or K2 (Sharpe ≤ 0 or expectancy ≤ 0) | Family decisively falsified. PARK_FAMILY_FALSIFIED. Move to D3 as s9. |
| H1 fails K4 anyway (DD > 50% even without pyramid) | Signal has intrinsic DD problems. PARK and move to D3 as s9. (Lower probability.) |
| H1 fails K6/K7/K8 (safety) | Implementation issue. Fail report, no patch without separate authorization. |

---

## 2 · Why s8-D1 was selected (from S8 selection plan)

Direct quote from the sealed S8 selection plan (`6b7bdb4c…`) scoring
matrix:

| Direction | Score | Rationale |
|---|---|---|
| **D1** cross-asset Donchian no-pyramid (max_units=1) | **39 / 40** | Directly tests the unfixed K4-root-cause from s7-D1. Single-parameter reduction (max_units 4→1) on the same universe. Uses existing 480-file local DBN cache. Uses well-validated helpers from main.py (PyramidManager works trivially with max_units=1). Strong first-principles motivation. No new tuning knobs introduced. |
| D2 reduced pyramid (max_units=2) | 29 / 40 | Ad-hoc compromise; risks overfitting to s7-D1 in-sample result. |
| D6 family-level park | 28 / 40 | Premature without D1's answer. |
| D5 ZN-only single-market | 25 / 40 | **OVERFIT TRAP** — recommended AGAINST (precedent: s7 plan D5 YM-only at 12/40). |
| D3 move OFF Donchian family entirely | 23 / 40 | Natural s9 if D1 parks; premature now. |
| D4 different channel lengths | 23 / 40 | Adds knobs without addressing K4. |

**Selection rule cited in the sealed S8 plan:** *"D1 is the only direction
that DIRECTLY tests the load-bearing remaining hypothesis from s7-D1: K4
fired at −221% DD; the proximate cause is pyramid amplification; the
direct fix is removing the pyramid (max_units = 1). Every other direction
either (a) doesn't address K4, (b) adds ad-hoc parameter knobs, (c) is a
known overfit trap, or (d) is premature without D1's answer."*

**D5 prohibition.** This spec inherits the explicit
`recommends_against_d5` invariant from the sealed S8 plan. D5 (ZN-only)
is not built, not specced, not benchmarked against, and not auditable
into D1 by ex-post market substitution.

**D3 deferred.** D3 (different family) is held as the natural **s9**
direction IF s8-D1 parks. Running s8-D1 first definitively closes
whether the trend-following family on cross-asset is salvageable.

---

## 3 · Single delta from s7-D1

| Parameter | s7-D1 value | s8-D1 value | Notes |
|---|---|---|---|
| `max_units_per_market` | **4** | **1** | THE SINGLE DELTA |
| `pyramid_spacing_n_multiplier` | 0.5 | 0.5 (vestigial — no second unit fires) | Kept in CONFIG for record; the PyramidManager helper handles `max_units=1` trivially |
| Entry channel length | 55 | **55** (unchanged) | |
| Exit channel length | 20 | **20** (unchanged) | |
| Stop multiplier | 2N | **2N** (unchanged) | |
| `stop_n_period` (Wilder ATR) | 20 | **20** (unchanged) | |
| `risk_pct_per_unit` | 0.01 (1% portfolio) | **0.01** (unchanged) | |
| Universe | NQ, GC, ZN, CL | **NQ, GC, ZN, CL** (unchanged) | |
| Filter | NONE (AMB6 locked) | **NONE** (unchanged) | |
| Entry timing | ONO (open-on-next-bar) | **ONO** (unchanged) | |
| In-sample window | 2013-01-01..2022-12-30 | **2013-01-01..2022-12-30** (unchanged) | |
| Per-market RTH windows | (see §4) | (unchanged) | |
| Cost stress matrix tiers | S0..S4 | **S0..S4** (unchanged) | |
| Starting cash | $100,000 MNQ-equiv | **$100,000 MNQ-equiv** (unchanged) | |
| `portfolio_cap_max_units` | 16 (= 4×4) | **4** (= 1×4) | DERIVED from max_units delta |
| `portfolio_cap_uses_unit_count_not_contract_count` (s6 bugfix) | True | **True** (preserved) | |
| All s7-D1 K-criteria thresholds | Tier-N spec §14 | **Identical** | No threshold loosening |

**Expected mechanical implications of the delta:**

- Per market, at most 1 unit open at a time. No pyramid additions.
- Entry trigger fires same as s7-D1; only the first unit opens.
- Stop is set once at entry at 2N; persists until exit.
- Exit on Donchian-20 reversal closes the single open unit at next RTH open.
- **No second-unit ATR re-use** (the s6 bugfix attestation about `n_entry` re-use across pyramid units is preserved but trivially satisfied since only one unit per trade exists).
- Trade count should be roughly similar to s7-D1 (~150-300 trades expected; entries fire on same Donchian-55 breakouts; only the number of UNITS per trade changes).
- Per-trade winners no longer amplified by pyramid → expected per-trade expectancy may be smaller in absolute terms than s7-D1's +$3,667, but DD should be substantially lower.

---

## 4 · Session rules (inherited byte-equivalent from s7-D1)

| Field | Value |
|---|---|
| Reference timezone | `America/New_York` (ET) |
| Trading session per market | **RTH-only** |
| NQ RTH | 09:30 – 16:00 ET |
| GC RTH | 09:30 – 16:00 ET (settlement window 13:30 ET) |
| ZN RTH | 09:30 – 16:00 ET (24h tape filtered to RTH) |
| CL RTH | 09:30 – 14:30 ET |
| Daily-bar derivation | One daily OHLCV bar per market per RTH session |
| Trade timezone for entry/exit | All decisions resolved at session close on the bar in question |
| Holiday calendar | CME group official holiday calendar |
| Half-days | Skipped |
| Per-market trading-day count | Independent |
| Session boundary errors | Fail-closed |

(All identical to s7-D1 spec §4.)

---

## 5 · Donchian breakout rule (inherited byte-equivalent from s7-D1)

| Parameter | Value | Inherited from |
|---|---|---|
| Entry channel length | **55 daily bars** | s7-D1 / s6 REV1 (Faith System 1) |
| Exit channel length | **20 daily bars** | s7-D1 / s6 REV1 |
| Channel construction | Donchian high/low over the **previous 55 closed RTH daily bars** | s7-D1 / s6 REV1 |
| Long entry trigger | Today's RTH high > previous 55-bar high → MOC or ONO per `entry_timing_field` | s7-D1 / s6 REV1 |
| Short entry trigger | Today's RTH low < previous 55-bar low → MOC or ONO per `entry_timing_field` | s7-D1 / s6 REV1 |
| Filter | **NONE** (no same-direction trend filter, no MA filter, no regime filter, no correlation gate) — `AMB6` structurally locked NONE | s7-D1 / s6 REV1 |
| `entry_timing_field` | `ONO` (open-on-next-bar) | s7-D1 / s6 REV1 |
| `max_units_per_market` | **1** | **S8-D1 DELTA** (was 4 in s7-D1) |
| Pyramid step (vestigial) | +0.5 N (no second unit ever fires under max_units=1) | s7-D1 / s6 REV1 |
| Exit on opposite Donchian | Long exits if today's RTH low < previous 20-bar low; short exits if today's RTH high > previous 20-bar high | s7-D1 / s6 REV1 |

---

## 6 · Entry rule

1. At each market's RTH session close, evaluate the long and short
   Donchian-55 triggers (§5).
2. If a trigger fires AND the per-market open-unit count for this market
   is **0** (since `max_units = 1`, only one unit can be open at a time) AND
   the global per-symbol coordinator does not block the side, queue an
   `ENTRY_PENDING` for the next RTH open (`ONO`).
3. At next RTH open, place a market order at the open price; record
   fill price for slippage accounting (see §10).
4. On fill, compute `N = WilderATR(20)` of the entry market at the
   triggering bar (NOT the fill bar). Store `N_entry_unit_1`.
5. Set initial stop at **2 × N** below long entry / above short entry
   (see §8).
6. **No pyramid trigger is computed** (since `max_units = 1` makes
   pyramid additions impossible).
7. **No same-symbol opposite-direction entry** while the unit is open
   for that market.
8. Entries are evaluated per market independently — there is no
   cross-market gate, no correlation filter, no risk-budget rebalancing
   at entry time.

---

## 7 · Exit rule

1. At each market's RTH session close, evaluate the Donchian-20 exit
   trigger for the open unit (if any) in that market (§5).
2. If the trigger fires, queue an `EXIT_PENDING` for the open unit on
   that side; exit at next RTH open (`ONO`).
3. Stop-loss exit is handled separately (§8): if the stop is touched
   intra-bar, exit at the stop price plus slippage (no waiting for
   close).
4. There is **no time-stop**, **no profit target**, **no trailing rule
   above the Donchian-20**.
5. On exit, mark the trade closed and write the row to `trades.csv` (§15).

---

## 8 · Stop rule (inherited byte-equivalent from s7-D1)

| Parameter | Value |
|---|---|
| Initial stop distance per unit | **2 × N** (Wilder ATR(20) of entry market at trigger bar) |
| Stop direction | Below entry for long; above entry for short |
| Per-unit stop persistence | Locked at unit-entry time; does NOT trail on Donchian-20 |
| Stop hit handling | Intra-bar trigger → exit that unit at stop price + slippage |
| Stop and exit-channel interaction | If both fire on the same day, the **earlier intra-day timestamp wins** |
| No moving stop | Stops do not move with the channel |
| Catastrophic stop (chain-level) | Portfolio MaxDD > 50% triggers K4 → park the candidate immediately at end-of-day (§14) |

---

## 9 · Position sizing rule

| Parameter | Value | Notes |
|---|---|---|
| Capital basis | **Portfolio equity** (mark-to-market, end of prior RTH day) | Unchanged from s7-D1 |
| Per-unit dollar risk | **1.0 % of portfolio equity** | Unchanged |
| Per-unit contract count | `floor( (0.01 × portfolio_equity) / (N_entry × $/pt) )` | Unchanged |
| Minimum contract size | If computed contract count < 1, **the unit is skipped** and logged to `entry_skip_log.jsonl` | Unchanged |
| Pyramid units | **N/A — `max_units_per_market = 1`. No second unit ever opens.** | **S8-D1 DELTA** |
| Portfolio cap | **At most `4 markets × 1 unit = 4 units` open across the portfolio at any one time** | DERIVED from `max_units = 1` |
| `PortfolioCapTracker.update_market_units()` | MUST pass `pyr.current_unit_count` (the UNIT count, max 1 per market under s8-D1), NOT `pyr.total_quantity` (the contract count). The s6 cap-bugfix attestation is preserved; cap is structurally non-binding at 4 markets × 1 unit = 4 units (< max 16). | Preserved |
| Starting cash | **$100,000 MNQ-equivalent** | Unchanged |
| Per-trade quantity field | Unit count (always 1 when open, 0 when closed) + contract count, persisted to `trades.csv` for cap auditability | Inherited |
| Sizing under data outage | If entry-day Wilder ATR(20) cannot be computed, entry is skipped and logged | Unchanged |

---

## 10 · Cost / slippage assumptions (inherited byte-equivalent from s7-D1)

Locked at spec time; loosening these post-seal is a
`threshold_lock_invariant` violation.

| Cost component | NQ | GC | ZN | CL |
|---|---|---|---|---|
| Commission per RT | $3.00 | $3.00 | $3.00 | $3.00 |
| Exchange + clearing fees per RT | $1.50 | $1.50 | $1.20 | $1.50 |
| **Total per RT (commission + fees)** | **$4.50** | **$4.50** | **$4.20** | **$4.50** |
| Slippage per entry | 1 tick | 1 tick | 1 tick | 1 tick |
| Slippage per stop-out | 2 ticks | 2 ticks | 2 ticks | 2 ticks |
| Slippage per Donchian-20 exit | 1 tick | 1 tick | 1 tick | 1 tick |
| Funding / overnight | None | None | None | None |
| Roll cost | 1 spread tick per market per roll | same | same | same |

**Cost-stress matrix (locked, identical to s7-D1):**

| Tier | Slippage scalar | Commission/fee scalar | Purpose |
|---|---|---|---|
| **S0** | 0× | 0× | Diagnostic floor — DR3 fires if survival is S0-only |
| **S1** | 1× | 1× | Baseline preregistered |
| **S2** | 3× | 1.5× | Mild stress |
| **S3** | 5× | 2× | Realistic adverse |
| **S4** (reserved) | 8× | 3× | Tail stress — informational only |

DR rules unchanged from s7-D1:
- **DR2** — `oos_metrics_degrade_materially_under_S2_or_S3_cost_stress` → `REJECT_FAST`
- **DR3** — `zero_cost_only_survival` → `REJECT_FAST`
- **DR4** — IS positive but OOS negative at S0 baseline → escalate to operator review
- **DR5** — `cost_stress_turns_edge_negative` between S0 and S1 → `REJECT_FAST`

---

## 11 · Data requirements (inherited byte-equivalent from s7-D1)

| Field | Value |
|---|---|
| Source of record | **Databento** `GLBX.MDP3` dataset; **local cache only at run time** (operator-confirmed P5 fetch already complete from s7-D1 chain: 480 .dbn.zst files, 129,789,451 bytes total) |
| Schema | `ohlcv-1m` (minute bars; daily bars derived RTH-only per §4) |
| `stype_in` (continuous) | `continuous` (front-month, `*.c.0`) |
| Symbols | `NQ.c.0`, `GC.c.0`, `ZN.c.0`, `CL.c.0` |
| In-sample window | **2013-01-01 → 2022-12-30 (UTC)** — locked, identical to s7-D1 |
| OOS window | **2023-01-01 → 2025-12-30 (UTC)** — DO NOT INSPECT until in-sample passes K-criteria |
| Local cache path | `data/databento_cache/{NQ,GC,ZN,CL}/<YYYY-MM>/*.dbn.zst` (operator P5 cache from s7-D1; **already complete**, no fresh fetch needed) |
| API-key handling | `os.environ.get("DATABENTO_API_KEY")` only — and only if any fresh fetch is later authorized; runtime decode uses `db.DBNStore.from_file()` (local-only, no API call) |
| Data-quality gates at load time | Bar-count expectations per RTH session per market; NaN/zero-volume → bar dropped + logged in `data_quality_warnings.json`; ≥0.5 % bar-drop rate in any single year → fail-closed |
| Calendar alignment | CME group official holiday calendar |
| Time zone of timestamps | All persistence in UTC; ET conversion only at session-boundary computation |

**Operator P5 fetch attestation (inherited from s7-D1 chain):**

| Root | file_count | bytes |
|---|---|---|
| NQ | 120 | 53,148,359 |
| GC | 120 | 2,162,216 |
| ZN | 120 | 27,939,222 |
| CL | 120 | 46,540,654 |
| **Total** | **480** | **129,789,451** |

**No fresh Databento fetch authorized by this spec.** The s7-D1 P5 cache
is operator-confirmed complete and may be re-used; the s8-D1 in-sample
run would `assert_cache_complete()` against these exact sizes at runtime.

---

## 12 · Roll / contract handling assumptions (inherited byte-equivalent from s7-D1)

| Topic | Assumption |
|---|---|
| Roll method | Databento `continuous` series, **back-adjusted price-ratio** stitch preferred |
| Roll cost | Modeled as 1 spread-tick per market on each roll date |
| Roll calendar | Read from Databento's `definition` schema |
| Stitch artifact attestation | Each roll date enumerated in `roll_attestation.json` |
| Carry / contango effect | Accepted as continuous-series property; no detrend |
| OOS roll integrity | OOS roll calendar must match in-sample method |
| Manual roll override | **Disallowed** |

---

## 13 · Acceptance gates (in-sample, locked)

Pass requires **ALL** of:

| Gate id | Description | Threshold | Source |
|---|---|---|---|
| `A1` | `closed_trades_portfolio ≥ 100` | K9 inverse | s7-D1 |
| `A2` | `sharpe_proxy_per_trade > 0` | K1 inverse | s7-D1 |
| `A3` | `expectancy_per_trade > 0` | K2 inverse | s7-D1 |
| `A4` | `trade_curve_maxdd_pct ≤ 50.0` (in magnitude) | K4 inverse | s7-D1 |
| `A5` | ≥ 2 of 4 markets show `wr_gap_to_breakeven_pp ≥ 0` AND portfolio WR-gap ≥ +0.5 pp | (per Tier-N) | s7-D1 |
| `A6` | `VALIDATOR_PASS` 16/16 + s8-specific (no-pyramid attestation) | (per validator) | s8-D1 specific |
| `A7` | `effective_independent_bets ≥ 2.5` (estimated from empirical pairwise correlations) | Directional read | s7-D1 |
| `A8` | Cost-stress matrix S0-S4 RUN; DR2/DR3/DR5 not fired | (DR rules) | s7-D1 |
| `A9` | Phase 2 safety C1-C8 inheritance attestable | (per template) | s7-D1 |
| `A10` | `cap_binding_events_count == 0` at portfolio level (cap structurally non-binding at 4 markets × 1 unit = 4) | (per s6 cap-bugfix) | s7-D1 |

**Honest realism note**: A4 is the gate that fired in s7-D1 (−221.67%
exceeded 50%). The s8-D1 hypothesis is precisely that **A4 will pass
this time** because pyramid amplification is removed. If A4 fails again
at s8-D1, the chain has its decisive K4-still-fires answer regardless of
pyramid.

---

## 14 · Rejection gates (kill criteria, locked — inherited byte-equivalent from s7-D1)

| K | Trigger | Park status |
|---|---|---|
| `K1` | `portfolio_sharpe_proxy_per_trade < 0` | `PARKED_SAFE_BUT_NOT_MONEY_PROVEN` |
| `K2` | `expectancy_per_trade ≤ 0` | `PARKED_SAFE_BUT_NOT_MONEY_PROVEN` |
| `K4` | `trade_curve_maxdd_pct > 50` | `PARKED_SAFE_BUT_NOT_MONEY_PROVEN` |
| `K6` | `safety_warning_count > 0` | `PARKED_SAFETY_FAILED` |
| `K7` | `filter_silently_introduced_attestation == True` OR `correlation_gate_silently_introduced_attestation == True` | `PARKED_SAFETY_FAILED` |
| `K8` | `sealed_parent_drift > 0` | `PARKED_PROVENANCE_BROKEN` |
| `K9` | `closed_trades_portfolio < 100` | `PARKED_FAILED_AT_INSUFFICIENT_SAMPLE` |
| `K10` | `avg_pairwise_correlation > 0.50` over in-sample window | `PARKED_FAILED_AT_DIVERSIFICATION_HYPOTHESIS` |
| `K11` | `cap_binding_events_count > 1000` | `PARKED_CAP_BINDING` |
| `K12` (REJECT_FAST) | DR2 / DR3 / DR5 fire on cost-stress matrix | `REJECT_FAST` |

**Threshold-lock invariant:** Loosening any K threshold post-seal is
forbidden. Tightening is a fresh `_revN_` spec.

**Honest expectation note:** the most informative possible K-fires for
s8-D1 are:
- K4 fires AGAIN → signal has intrinsic DD even without pyramid
- K1 or K2 fires (Sharpe ≤ 0 or expectancy ≤ 0) → Faith's alpha needed pyramid amplification; family decisively falsified

If none of K1/K2/K4 fires AND A1-A10 all pass, the candidate becomes a
viable graduation prospect (operator decides next step).

---

## 15 · Required output files (locked artifact set)

Naming mirrors the s7-D1 chain for direct comparability:

| Path | Purpose |
|---|---|
| `docs/s8_d1_cross_asset_donchian_no_pyramid_spec.md` | THIS document (spec DRAFT) |
| `reports/external_research_hunter/s8_d1_cross_asset_donchian_no_pyramid_tier_n_spec.{md,json}` | Sealed Tier-N spec authored alongside this DRAFT (this turn's secondary outputs) |
| `reports/external_research_hunter/s8_d1_cross_asset_donchian_no_pyramid_plan_lock.{md,json}` | Sealed plan-lock (later, separate authorization) |
| `reports/external_research_hunter/s8_d1_cross_asset_donchian_no_pyramid_phase2_plan.{md,json}` | Sealed Phase-2 plan doc (later, separate authorization) |
| `external_research_hunter/s8_d1_cross_asset_donchian_no_pyramid_runner_harness/main.py` | BUILD turn (later, separate authorization) — may inherit from s7-D1 patched runner_harness as MECHANICAL BASELINE, but lives under s8-D1 namespace; not a revival of s7-D1 |
| `external_research_hunter/s8_d1_cross_asset_donchian_no_pyramid_runner_harness/execution_guard.py` | BUILD turn |
| `external_research_hunter/s8_d1_cross_asset_donchian_no_pyramid_runner_harness/in_sample_driver.py` | BUILD turn — directly reuses s7-D1 patched driver mechanic with `max_units = 1` CONFIG only |
| `external_research_hunter/s8_d1_cross_asset_donchian_no_pyramid_runner_harness/tests/test_smoke_t1_t15.py` | T1-T15 smoke; may inherit s7-D1 test patterns but lives under s8-D1 namespace |
| `reports/external_research_hunter/s8_d1_cross_asset_donchian_no_pyramid_runner_build_report.{md,json}` | After BUILD: file shas, lint, smoke-import |
| `reports/external_research_hunter/s8_d1_cross_asset_donchian_no_pyramid_in_sample_driver_build_report.{md,json}` | After driver patch (if any) |
| `reports/external_research_hunter/s8_d1_cross_asset_donchian_no_pyramid_t1_t15_smoke_pass_report.{md,json}` | After smoke pass |
| `reports/external_research_hunter/s8_d1_cross_asset_donchian_no_pyramid_in_sample_diagnostic_result_sealed.{md,json}` | After in-sample run |
| `reports/external_research_hunter/s8_d1_cross_asset_donchian_no_pyramid_in_sample_decision_memo.{md,json}` | After decision memo |
| `reports/external_research_hunter/s8_d1_cross_asset_donchian_no_pyramid_<PARKING_or_PROCEED>_report.{md,json}` | Lifecycle transition |
| `data/databento_cache/{NQ,GC,ZN,CL}/<YYYY-MM>/*.dbn.zst` | OPERATOR-MANAGED; already complete from s7-D1 P5 — re-used, NOT re-fetched by s8 |

**Naming invariant.** `s8_d1_cross_asset_donchian_no_pyramid_*` is the
locked prefix. No other s8 variant may write under this prefix.

**Seal recipe.** All `.json` outputs MUST use the LESSON_HUNTER_004
canonical roundtrip recipe (sort_keys=True, separators=(",",":"),
ensure_ascii=False, default=str, EXCLUDING `report_seal_sha256` +
`seal_method`).

---

## 16 · Validation checklist

A run is `VALIDATOR_PASS` iff all 21 items below resolve True (the s7-D1
V1-V21 set adapted for s8-D1):

1. `spec_sha_matches_recorded`
2. `phase2_safety_template_inherited_byte_equivalent`
3. `s2_through_s7_d1_sealed_chains_byte_stable` — **all 6 prior parking
   reports + the s7-D1 chain (14 sealed artifacts) byte-stable**
4. `no_d5_revival` (S7 plan's D5 YM-only AND S8 plan's D5 ZN-only)
5. `no_b005_001_revival`
6. `no_nke_revival`
7. `markets_enumerated_exactly_4_nq_gc_zn_cl` (same as s7-D1)
8. `rth_only_filter_attested` (per-market windows)
9. `donchian_55_20_attested`
10. **`max_units_per_market_equals_1_attested`** — **S8-D1 specific check**
11. `n_calculation_used_entry_market_at_trigger_bar`
12. `portfolio_cap_uses_unit_count_not_contract_count` (s6 bugfix
    preserved; cap structurally non-binding at 4 markets × 1 unit = 4)
13. `cost_stress_matrix_S0_S1_S2_S3_S4_present`
14. `seal_roundtrip_recompute_match`
15. `no_oos_inspection_in_in_sample_run`
16. `boundaries_held` — `no_live_trading`, `no_brokerage_connection`,
    `no_review_queue_mutation`, `no_strategy_lab_promotion`,
    `no_obsidian_trade_logger_mutation`, `no_credential_logged`,
    `no_databento_key_printed`, `no_qc_api_call_in_local_path`. All True.
17. `spec_md_unchanged_during_seal_turn`
18. `no_d5_artifact_present_in_repo` (both S7 D5 patterns and S8 D5 patterns)
19. `no_b005_001_chain_mutated_during_turn`
20. `no_nke_chain_mutated_during_turn`
21. **`no_s7_d1_chain_mutated_during_turn`** — **S8-D1 specific check**: all 14 s7-D1 sealed artifacts must remain byte-stable through the s8-D1 build/run; the s7-D1 chain is permanently parked

---

## 17 · What would count as overfitting

Each of the following is a **structural overfit** indicator:

- **OI1** — Cherry-picking 1-of-N markets after seeing in-sample results
  (the s7 D5 YM-only / s8 D5 ZN-only trap). Verdict computed over the
  locked 4-market portfolio, never over a subset.
- **OI2** — Loosening any K threshold after seeing the s8-D1 result.
- **OI3** — Re-running with a tweaked parameter (entry length ≠ 55, exit
  ≠ 20, stop ≠ 2N, sizing ≠ 1%, max_units ≠ 1) and reading off a better
  number. Any parameter change requires a fresh `_revN_` chain.
- **OI4** — Substituting a market post-hoc.
- **OI5** — Adjusting the in-sample window to dodge a bad stretch.
- **OI6** — Adding a regime filter, correlation gate, or
  same-direction-as-trend filter after seeing in-sample losses.
- **OI7** — Inspecting OOS before in-sample passes.
- **OI8** — "Stress matrix bias review" used to overturn a REJECT_FAST.
- **OI9** — Retro-fitting commentary to qualitative estimates from the
  S8 selection plan.
- **OI10** — Adopting s7-D5 (YM-only) or s8-D5 (ZN-only) as a
  "sub-analysis" of s8-D1.
- **OI11 (S8-D1 specific)** — **Reading s8-D1's result and then tuning
  max_units to 2 or 3 to "find the sweet spot"** — that would be the
  s8-D2 ad-hoc compromise that the S8 selection plan scored 29/40 with
  explicit ad-hoc-tuning critique. Any future max_units value other than
  1 requires a fresh candidate_record_id (e.g., s9-* or later) and fresh
  sealed chain.
- **OI12 (S8-D1 specific)** — **Citing s7-D1's positive per-trade
  economics as predictive evidence for s8-D1's per-trade economics.**
  The s7-D1 result is upstream evidence on the SIGNAL layer; s8-D1's
  per-trade economics are an empirically separate question because
  removing pyramid changes the per-trade winner amplification.

---

## 18 · What would make us stop immediately

Inherited byte-equivalent from s7-D1 spec §18:

- **S-STOP-1** — sealed parent sha changes mid-run
- **S-STOP-2** — any non-zero Phase 2 §C1-C8 safety warning
- **S-STOP-3** — DATABENTO_API_KEY in any log line
- **S-STOP-4** — network call to non-allowlisted host OR QC API call
  from local-engine path
- **S-STOP-5** — write to `review_queue.json`, `idea_memory`, Strategy
  Lab approval files, or `obsidian-trade-logger/**`
- **S-STOP-6** — broker, exchange, or Kraken/Binance/Alpaca adapter
  instantiated
- **S-STOP-7** — K6/K7 (safety) fire during run
- **S-STOP-8** — data-quality fail
- **S-STOP-9** — operator-issued `STOP_S8_D1` instruction
- **S-STOP-10** — spec sha shown in runner ≠ sealed Tier-N spec sha
- **S-STOP-11 (S8-D1 specific)** — `max_units_per_market != 1`
  detected anywhere in CONFIG, runner constants, or runtime state. The
  single delta from s7-D1 must hold byte-equivalent through the chain;
  any other value indicates either a CONFIG drift or an unauthorized
  modification.
- **S-STOP-12 (S8-D1 specific)** — Any s7-D1 chain artifact's byte sha
  changes during the s8-D1 turn (the s7-D1 chain is permanently parked
  and must remain byte-stable through all s8 work)

---

## 19 · Next step after spec approval

The next operator-authorized turn — and ONLY the next — is:

1. **Operator reads this DRAFT** and either:
   - Returns specific change requests, OR
   - Issues an explicit "AUTHORIZE S8-D1 TIER-N SPEC SEAL" instruction.

2. On AUTHORIZE, SPARTA Claude produces (in a single new turn) the
   **Tier-N spec** at
   `reports/external_research_hunter/s8_d1_cross_asset_donchian_no_pyramid_tier_n_spec.{md,json}`
   with the LESSON_HUNTER_004 canonical seal recipe and the locked
   parameters above. **This is still spec-only**; no code, no fetch,
   no execution.

   (Note: per the operator's combined-authorization in THIS turn, the
   Tier-N spec JSON + MD are authored alongside this DRAFT and the seal
   for the Tier-N is produced in this same turn. See companion files at
   the locked paths above.)

3. After Tier-N spec seal, the **separately-authorized** turns are
   each their own operator approval:

   - (a) **P1 Plan-lock authoring**
   - (b) **P2 Phase-2 plan-doc authoring**
   - (c) **P3 BUILD ONLY** — runner + execution_guard + tests scaffolded
     under
     `external_research_hunter/s8_d1_cross_asset_donchian_no_pyramid_runner_harness/`
   - (d) **P4 T1-T15 smoke pass** on synthetic fixtures only
   - (e) **(no P5 fetch needed)** — s7-D1 P5 cache is operator-confirmed
     complete and re-usable
   - (f) **P6 in-sample run** at S1 baseline (and optionally S0/S2/S3/S4)
   - (g) **P7 in-sample decision memo**
   - (h) **P8 lifecycle transition** (PARK or OOS-AUTHORIZE)

Steps (a)-(h) each require an explicit operator authorization line;
none are pre-approved by this spec.

**What this DRAFT does NOT do.** It does not seal a Tier-N spec on its
own (the companion sealed Tier-N JSON+MD authored alongside in this same
turn IS the seal authoring; see those files for the canonical seal). It
does not authorize any of steps (a)-(h). It does not authorize a
Databento fetch. It does not authorize a QC submit. It does not
authorize any change to the live or paper trading systems. It does
not modify `review_queue.json`. It does not modify or revive any
parked or rejected candidate. **It does not revive s7-D1.**

---

## Appendix A · Inherited constants registry (for re-verification at seal time)

The seal of the companion Tier-N JSON pins these inherited shas; operator
can re-verify byte-stability before authorizing BUILD:

| Inherited artifact | Recorded sha256 | Inheritance reason |
|---|---|---|
| `s8_selection_plan_seal` (direct predecessor) | `6b7bdb4c350f4a779611546dcb32f6a83db2371c66d7b6ba0118121783801441` | Direct parent of this spec |
| `s7_d1_PARKING_REPORT` | `551fdce46c0e373eac03d79597d6439d740ae56f4a0ba9f2c6f2b39d25974b32` | s7-D1 chain final state; load-bearing evidence |
| `s7_d1_in_sample_decision_memo` | `5354d3395319e309b953e112c85283bf7753bb3b13c6ae2403eaf502394afef3` | Decision rationale that led to S8 |
| `s7_d1_in_sample_diagnostic_result_sealed_rev2` | `2563ef93092171718b11291048181664a9653d4f7d9e33d0e9df5bf7b741f4f6` | Operative s7-D1 strategy result (313 trades, K4 fires) |
| `s7_d1_patch_build_report` | `2ab3ed5852de0dadcbe11da3aa7451a8c8a01372cb26395e4e28467628892522` | Patched driver build (mechanical baseline for s8-D1 driver) |
| `s7_d1_in_sample_driver_build_report` | `26e9c6f0c217f1f2daf994445bcae0c4d1bfe1ef9e81cfc1133f41823816b38e` | Prior driver build |
| `s7_d1_tier_n_spec` | `72602305ef8d678195f9ab91a6d4cb8e7a473ee1a641cf9e8f91b8d4e31134c3` | s7-D1 Tier-N (parameter inheritance baseline) |
| `s7_d1_plan_lock` | `0f8e9fe6bc4f50e4f17c41611dbd01b7f9df3047ed448a3e9dffe7533210572d` | s7-D1 plan-lock |
| `s7_d1_phase2_plan` | `e1800ee28bd99a27da94d048fce4512401bc6ecd66b89e9d184f6c3050e2669a` | s7-D1 Phase-2 plan (C1-C8 inheritance) |
| `s6_parking_report` | `f6953c1fb3c334d34572aa7dac29317b4ff412bf3648db62276707ef9de2894a` | Upstream lesson 3 (pyramid amplification) |
| `s5_parking_report` | `6c308b42da6854d5dd3f8e8936fb5299666dae3158904bec65ec6458156f234c` | Single-market baseline |
| `s4_parking_report` | `8cda3ca644524cd558cc3a1291a869d983a8c5fae9c1d0f15d6e56ba266a1cb4` | Turtle System 1 |
| `s3_parking_report` | `1f557888e1212d6ffe0e305ac43308977f618db7473b22c90e407fe805d3f7ad` | MNQ DRB |
| `phase2_safety_template_md` | `1812f4854a23e7a148257c88133042ea1e383725f4875e762475260ae3658981` | C1-C8 inheritance |
| `phase2_safety_template_json` | `695a9fb6e0cb6ae5395d467471f2c55d3d90a7030443ca87e4c1d220335f4a32` | C1-C8 inheritance |

**Drift count at this DRAFT:** `0` (audit conducted 2026-05-25; all
parents byte-stable per the sealed S8 selection plan + the committed
s7-D1 chain).

**s7-D1 explicit non-revival attestation:** the s7-D1 chain (14 sealed
artifacts ending at PARKING_REPORT `551fdce4…`) remains permanently
parked. This s8-D1 spec uses the s7-D1 chain as upstream evidence and
mechanical baseline (specifically, the s7-D1 patched driver's helper
functions and Phase-2 safety contracts) but does NOT modify, revive, or
re-test any s7-D1 artifact. The s7-D1 PARKING_REPORT
status (`PARKED_SAFE_BUT_NOT_MONEY_PROVEN`) is the final word on s7-D1.

---

*End of `s8_d1_cross_asset_donchian_no_pyramid_spec.md` DRAFT. Spec only
— no code, no backtest, no Databento, no QuantConnect, no fetch, no live
or paper trading, no scheduler change, no obsidian-trade-logger
mutation, no review_queue mutation, no D5 revival (s7 YM-only or s8
ZN-only), no rejected-candidate revival, no s7-D1 revival. Awaiting
operator approval before further chain work.*
