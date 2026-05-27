# s13 D1 MNQ.c.0 Single-Instrument RSI(2) Bi-Directional Databento Long-History -- Tier-N Specification DRAFT

Status: DRAFT (not sealed; operator confirms DRAFT ambiguities DA1-DA14 at SEAL; no code, no fetch, no run by this DRAFT).

Authored: 2026-05-27
Authorization phrase: "Authorize s13 D1 MNQ.c.0 single-instrument RSI(2) bi-directional Tier-N spec DRAFT."

Plan source: `docs/s13_d1_mnq_c0_single_instrument_rsi_2_bi_directional_databento_long_history_tier_n_spec_plan.md` (committed at `5e57984`).

Parent reference chain (READ-ONLY; byte-stable; not modified by this DRAFT):
- s13-d1 PLAN commit: `5e57984`
- Selection-plan commit: `0e3f9d4` (T1 RSI MNQ recommended at 41/50)
- s12-d1 P11 park (terminal; PARKED_SAFE_BUT_INSUFFICIENT_SAMPLE_AT_IS): commit `ecbd001`; seal `b9722d42...`
- s12-d1 SEAL: commit `66bbbd1`; seal `07c3200b...`
- s12-d1 P1 plan-lock: commit `d8bd359`; seal `eb72798e...`
- s12-d1 P2 phase-2 plan: commit `0b8d948`; seal `689dd3d0...`
- s11-d1 v1 spec: commit `9c63088`; seal `077e29e6...`
- s11-d1 rev2: commit `c110fd4`; seal `46659b4a...`
- s10-d2 park: commit `23c7164`
- s10-d1 MNQ+MGC park: commit `1a9acec`
- Audit-clean data anchor (MNQ.c.0; reused byte-equivalent): `data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_c_0_ohlcv_1d_20190513_20251230.csv` (sha256 `8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e`; 2066 rows; 2019-05-13 → 2025-12-29)

HARD BOUNDARIES (held by this DRAFT). Plan / spec DRAFT only. No strategy code. No backtest. No simulator. No signal computation. No data fetch. No yfinance / Yahoo Finance call. No Databento call. No `DATABENTO_API_KEY` access. No QC / LEAN call. No network IO. No `review_queue.json` mutation. No production `idea_memory` mutation. No Strategy Lab run. No candidate promotion. **No s12-d1 revival; no `_revN_` revision of s12-d1 authored by this DRAFT.** No s11-d1 / s12-d1 / s10-d2 / s10-d1 / s9 / s7-d1 / B005_NNN / B006_NNN / T8 sealed-artifact modification. No ORB branch mutation. No Step 30 cost constant mutation. No CLAUDE.md modification. No RUNBOOK modification. No `pipeline_manifest` modification. No `.gitignore` modification. **No `brain_memory/projects/trading_bot/lessons.md` modification or staging.** No branch change. No branch creation. No git push. No live trading. No profitability claim. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES. FRC `NEVER_GRANTED`.

----

## 1. Mechanic family + RSI parameters LOCKED at PLAN -- DRAFT does NOT reopen

Unlike the s11-d1 DRAFT (which RESOLVED mechanic family F1 at the DRAFT turn from a closed F1/F2/F3/F4 menu) and like the s12-d1 DRAFT (which LOCKED Donchian-15/8 at PLAN), this s13-d1 DRAFT does NOT reopen mechanic-family selection nor reopen RSI thresholds. Both were LOCKED at PLAN time (commit `5e57984`) as the load-bearing structural property of the fresh `candidate_record_id`.

The DRAFT confirms and carries forward (without revision option):

| Field | LOCKED at PLAN | Carried byte-equivalent into this DRAFT |
|---|---|---|
| `candidate_record_id` | `s13-d1-mnq-c0-single-instrument-rsi-2-bi-directional-databento-long-history` | yes |
| Mechanic family | **F3 RSI(2) bi-directional mean-reversion** | yes |
| Universe | `{MNQ.c.0}` only | yes |
| RSI period | **2 (Connors classic)** | yes |
| **RSI long entry threshold** | **`< 10`** | yes |
| **RSI long exit threshold** | **`> 50`** | yes |
| **RSI short entry threshold** | **`> 90`** | yes |
| **RSI short exit threshold** | **`< 50`** | yes |
| Signal direction | Long+Short bi-directional | yes |
| Pyramid mechanism | NONE / `max_units_per_market = 1` | yes |
| Schema | `ohlcv-1d` | yes |
| `stype_in` | `continuous` | yes |
| IS window | `2019-05-13 -> 2023-12-29` | yes |
| OOS window | `2024-01-02 -> 2025-12-30` (never inspected at IS) | yes |

A SEAL revision authorization that attempts to alter any of these PLAN-locked fields shall be rejected by the controller and require either (a) a fresh PLAN revision turn, or (b) a fresh `candidate_record_id` per the same first-principles burden that gave rise to s13-d1 itself.

## 2. Why s13-d1 is not rescuing s9, s12-d1, s11-d1, s10-d2, s10-d1, B006_NNN, s7-d1

### 2.1 s13-d1 is not a rescue of s9 (RSI-2 long-only on SPY/TLT/GLD/USO ETF-proxy; PARKED)

| s9 falsification feature | s13-d1 treatment |
|---|---|
| Universe = SPY/TLT/GLD/USO (4-ETF basket; equity-class ETFs) | Universe = `{MNQ.c.0}` (single futures; micro-Nasdaq-100; **different asset class**) |
| Long-only | **Bi-directional** (long when RSI<10 AND short when RSI>90); structural asymmetry break |
| Cost surface: per-share commission + bps slippage on ETFs | Cost surface: **per-contract commission + tick slippage** on micro-futures (carried byte-equivalent from s12-d1) |
| Negative S0 edge over 414 trades | S0 edge sign on s13-d1 is an **open question**; no a-priori claim |
| Falsification cause was instrument-specific cost/edge interaction on equity ETFs, NOT the RSI(2) signal generator itself | s13-d1 tests the RSI(2) signal on a structurally different instrument |

**First-principles claim:** the s9 falsification does NOT transfer to s13-d1 because (a) asset class differs (futures vs equity ETFs), (b) cost surface differs (per-contract vs per-share + bps), (c) signal direction differs (bi-directional vs long-only), and (d) universe differs (single MNQ vs 4-ETF basket).

### 2.2 s13-d1 is not a rescue of s12-d1 (Donchian-15/8 single-MNQ; PARKED INSUFFICIENT_SAMPLE)

| s12-d1 falsification feature | s13-d1 treatment |
|---|---|
| Mechanic family F1 (trend; Donchian-15/8 entry/exit) | Mechanic family **F3 (mean-reversion; RSI(2) bi-directional)** -- STRUCTURALLY ORTHOGONAL (mean-reversion is the OPPOSITE direction of trend) |
| K9-mitigation hypothesis (DRAFT 80-200 IS trades; actual 48 → falsified) | s13-d1 expects 230-300 IS trades + 100-130 OOS trades (substantially above K9=100 at both windows) |
| Donchian-15/8 single-instrument signal density ~10/y | RSI(2) bi-directional ~50-65/y (~5-6× higher signal density) |
| Single-instrument MNQ.c.0 | Single-instrument MNQ.c.0 (same universe; orthogonal mechanic) |

**First-principles claim:** s12-d1 falsified Donchian-15/8 mechanic on MNQ.c.0 with structurally-low signal density (~10/y). s13-d1 tests the INVERSE mechanic (mean-reversion) which produces structurally-higher signal density (~50-65/y), independent of any Donchian falsification. The two candidates are orthogonal.

### 2.3 s13-d1 is not a rescue of s11-d1, s10-d2, s10-d1, B006_NNN, s7-d1, T8

| Predecessor | Why s13-d1 differs |
|---|---|
| s11-d1 (Donchian-55/20 single MNQ; v1 sealed; OOS K9 disclosed unreachable) | Different mechanic family (F1 vs F3); s11-d1 was never executed at IS |
| s10-d2 (Donchian-55/20 4-market; PARKED OOS K9) | Different mechanic family; different universe scope (4-market vs single) |
| s10-d1 (Donchian on MNQ+MGC; INCONCLUSIVE_HOLD via MGC DR9 fire) | Different mechanic family; different universe (MGC structurally absent) |
| B006_001 / B006_002 (SPY vol-targeting) | Different mechanic family (F2 vs F3); different asset class; no DR11 for s13-d1 |
| s7-d1 (Donchian + pyramid on 4-ETF basket) | Different mechanic family; NO pyramid in s13-d1; different universe |
| T8 (ETF-proxy umbrella park) | s13-d1 universe is MNQ futures, not ETFs |

s13-d1 satisfies the first-principles burden against every parked / archived predecessor. The candidate is **structurally fresh**.

## 3. Universe (LOCKED at PLAN; restated at SEAL)

| Field | LOCKED value |
|---|---|
| Universe type | `single_fixed_instrument_continuous_micro_futures` |
| Symbol 1 (only symbol) | **`MNQ.c.0`** (Micro E-mini Nasdaq-100, continuous front-month) |
| `AddUniverse` calls | **0** (structurally absent) |
| `removed_from_universe` events | **0** (structurally absent) |
| Symbol count | exactly 1 |
| Symbol substitution at later phases | FORBIDDEN |
| Universe widening at later phases | FORBIDDEN (any wider basket requires fresh `candidate_record_id`) |
| Common-history start | **2019-05-13** |
| Diversification claim | NONE |

## 4. Dataset (LOCKED at SEAL)

| Field | LOCKED value |
|---|---|
| Vendor | **Databento Historical API** (vendor-level; controller-side never calls) |
| Dataset | **`GLBX.MDP3`** |
| Schema | **`ohlcv-1d`** |
| `stype_in` | **`continuous`** |
| Symbol requested | `["MNQ.c.0"]` |
| Re-use of existing audit-clean CSV | **TRUE** (sha256 `8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e`; reused byte-equivalent from s10-d1 sealed fetch); **ZERO new Databento call required** |
| Step 02b for this candidate | manifest cross-link only |
| API key handling | NOT REQUIRED at any phase |
| Controller-side Databento call | LOCKED OFF |

## 5. Schema (LOCKED at SEAL)

| Field | LOCKED value |
|---|---|
| Schema | `ohlcv-1d` |
| Fields | `ts_event`, `open`, `high`, `low`, `close`, `volume` |
| Intraday schemas | OUT OF SCOPE |

## 6. stype_in (LOCKED at SEAL)

| Field | LOCKED value |
|---|---|
| `stype_in` | `continuous` |
| `no_continuous_roll_stitch_modification_post_seal` invariant | TRUE |

## 7. IS / OOS windows (LOCKED at SEAL)

| Field | LOCKED value |
|---|---|
| **IS window start** | **`2019-05-13`** |
| **IS window end** | **`2023-12-29`** |
| IS window length | ~4.6 years |
| MNQ.c.0 IS row count (audit-confirmed) | **1,443** |
| **OOS window start (never inspected at IS)** | **`2024-01-02`** |
| **OOS window end (never inspected at IS)** | **`2025-12-30`** |
| OOS window length | ~2.0 years |
| MNQ.c.0 OOS row count (structural only) | **622** |
| OOS inspection at IS-phase | FORBIDDEN |

## 8. Data availability assumptions + DR gates (LOCKED at SEAL)

### 8.1 Assumptions inherited from s10-d1 + s12-d1 audits

- `MNQ.c.0` over `2019-05-13 -> 2025-12-30` is DR9-clean under both strict and holiday-aware audits (0 calendar gaps > 5 days; max single-day abs-log-return 0.1164).
- DR9 thresholds carried byte-equivalent (`0.95 / 0.30 / 5 / 5`).
- Step 02c for this candidate is a re-confirmation pass against the same CSV (no fresh Databento call).

### 8.2 DR rules adapted for single-instrument F3 RSI(2) bi-directional (LOCKED at SEAL)

| Rule | Trigger | Severity | F3 RSI(2) bi-directional note |
|---|---|---|---|
| DR1 | `oos_rebalance_count < 36` (OOS-phase only) | `INCONCLUSIVE_HOLD` | OOS-only |
| DR2 | `oos_metrics_degrade_materially_under_cost_stress` | `REJECT_FAST` | unchanged |
| **DR3** | `zero_cost_only_survival` (S0 > 0 AND all S1..S4 ≤ 0) | `REJECT_FAST` | **HIGHER prior probability for s13-d1** (RSI mean-reversion historically shows S0-positive but S1+ cost-erosion; s9 lineage observation); BINDING falsification candidate |
| DR4 | `oos_negative_while_is_positive_unexplained` | `REJECT_FAST` | OOS-only |
| **DR5** | `cost_stress_turns_edge_negative` (tier flip) | `REJECT_FAST` / `INCONCLUSIVE_HOLD` carveout | BINDING for high-frequency mechanics |
| DR6 | `post_warmup_sizing_ambiguity_or_invalid` (NARROWED post-warmup only) | `REJECT_FAST` | unchanged |
| DR7 | `missing_oos_or_date_window_evidence` | `INCONCLUSIVE_HOLD` | unchanged |
| DR8 | `live_or_order_routing_path_detected` at Initialize | `HARD_FAIL_VOIDED` | unchanged |
| DR9 | `mnq_c0_only_data_continuity_integrity_check` | `INCONCLUSIVE_HOLD` | MNQ-clean per s10-d1 audit; thresholds byte-equivalent |
| **DR10** | `turnover_cost_explosion` (`annual_turnover > 0.50` OR `S2 cost drag > 0.05`) | `REJECT_FAST` | **ELEVATED prior probability** vs s11-d1 v1 / s12-d1 (RSI ~50-65/y produces ~5-10× s11-d1's baseline turnover); BINDING |
| DR11 | NOT IN CHAIN | -- | F3 has no leverage cap; DR11 structurally absent |

DR precedence chain (LOCKED at SEAL): `DR7 -> DR1 -> DR9 -> DR10 -> DR6 -> DR4 -> DR2 -> DR3 -> DR5` (carried byte-equivalent from s12-d1 chain; DR11 omitted).

**DR3 + DR5 + DR10 are the binding falsification candidates for s13-d1** (RSI lineage s9 echo + high-frequency turnover risk). The cost-stress sweep at P6.5 is the dispositive test.

## 9. Cost stress from day 1 (LOCKED at SEAL)

Cost-stress matrix S0/S1/S2/S3/S4 LOCKED in the first IS diagnostic; deferral forbidden. Carried byte-equivalent from s12-d1 chain (5-tier set).

### 9.1 Cost tiers (5-tier; carried byte-equivalent)

| Tier | `cost_scalar` | `slippage_scalar` | Note |
|---|---:|---:|---|
| `S0` | 0.0 | 0.0 | zero-cost ideal |
| `S1` | 1.0 | 1.0 | baseline retail |
| `S2` | 1.5 | 1.5 | stressed retail |
| `S3` | 2.0 | 2.0 | adversarial |
| `S4` | 3.0 | 3.0 | extreme adversarial |

### 9.2 Tick / contract specs (LOCKED at SEAL)

| Symbol | Tick size | Dollar per tick |
|---|---|---|
| `MNQ.c.0` | 0.25 index points | **$0.50 per contract** |

### 9.3 Pre-registered S0 edge sign and magnitude (DRAFT-time)

| Field | DRAFT-proposed value |
|---|---|
| Expected S0 net PnL sign | **open question (no a-priori claim)** -- s9's negative S0 finding on long-only ETF-proxy does NOT determine s13-d1 bi-directional MNQ futures result by first-principles |
| Acceptance threshold S0 net PnL | `> 0` after >= 100 trades |
| Acceptance threshold S1 net PnL | `> 0` (K1 / K2 fire if `<= 0`) |
| Pre-registered max-drawdown tolerance | K4 = 50% magnitude (DRAFT_AMBIGUITY DA5; carried byte-equivalent) |
| Pre-registered cost-stress survival | all five cost tiers Sharpe > 0 → `ELIGIBLE_FOR_HUMAN_REVIEW`; S0/S1 positive but later degrade > 50% → K12 REJECT_FAST |
| **DR3 risk note** | **ELEVATED**; RSI mean-reversion mechanics historically show S0-positive but S1+ cost-erosion; this is the binding s9-lineage falsification test |
| **DR10 risk note** | **ELEVATED**; high-frequency mechanic (~50-65 trades/y) raises annual turnover; S2 cost drag > 5% triggers DR10 REJECT_FAST |

## 10. K9-reachability table at DRAFT time (NEW framework discipline; carried byte-equivalent from PLAN)

Per the NEW framework discipline introduced in the selection-plan revision at `0e3f9d4` and applied at PLAN at `5e57984`, this DRAFT carries the K9-reachability table forward as a load-bearing section.

| Window | Length (y) | Required closed_trades/year for K9=100 | Expected s13-d1 trades/year (low / central / high) | Expected total trades | K9 status |
|---|---:|---|---|---|---|
| IS | 4.6 | >= 21.74 | 50 / 57 / 65 | 230 / 262 / 300 | **CLEARS WITH MARGIN (2.3-3.0×)** |
| **OOS** | **2.0** | **>= 50.00** | 50 / 57 / 65 | **100 / 114 / 130** | **CLEARS (borderline at lower bound; 1.0-1.3×)** |

### 10.1 K9-reachability disclosure (binding at DRAFT)

- **s13-d1 satisfies K9-reachability at BOTH IS and OOS** (rare property among single-instrument candidates).
- IS K9 reachable with significant margin (2.3-3.0× the 21.74/y floor).
- **OOS K9 reachable at the lower bound (~50/y matches the 50/y floor exactly at low estimate).** Thin margin.
- OOS K9 risk MATERIALLY LOWER than s12-d1's structural unreachability (s12-d1 expected ~21 OOS trades at observed IS rate; s13-d1 expects 100-130 OOS trades at DRAFT band).

### 10.2 REC1-equivalent disclosure at DRAFT (binding)

- If observed IS rate falls below 25/year on RSI(2) bi-directional (vs DRAFT band 50-65/y), OOS K9 unreachability becomes structurally probable.
- Expected band: 50-65/y; lower-bound observation below 25/y would require parking per K9 inviolacy.
- The s9 RSI-2 baseline observed 414 trades over the long-only 4-ETF window; if MNQ.c.0 bi-directional rate falls below half that proportional rate, OOS K9 fires.

## 11. Sample-size / K9 rules (LOCKED at SEAL)

| Field | LOCKED value (DRAFT) |
|---|---|
| K9 threshold | `total_closed_trades >= 100` over IS window (LOCKED non-negotiable; `no_k9_relaxation`) |
| Expected IS trade count (4.6y) | 230 / 262 / 300 (low / central / high) -- clears K9 with significant margin |
| Expected OOS trade count (2.0y) | 100 / 114 / 130 (low / central / high) -- clears K9 at lower bound (marginal) |
| K9 risk at IS | LOW (significant margin) |
| K9 risk at OOS | LOW-TO-MODERATE (clears at lower bound; thin margin) |
| Per-symbol minimum | NOT APPLICABLE for single-instrument |
| If K9 fires at IS anyway | `DR1 INCONCLUSIVE_HOLD`; candidate archived without parameter modification |
| If K9 fires at OOS anyway | `INSUFFICIENT_SAMPLE` / `OOS_INDETERMINATE` PARK; candidate archived without parameter modification |

## 12. Diversification expectations -- single-instrument scope (LOCKED at SEAL)

| Field | LOCKED value |
|---|---|
| `A7_effective_independent_bets_min` | **NOT APPLICABLE** (trivially 1) |
| `K10_avg_pairwise_dependence_max` | **NOT APPLICABLE** (no pairs) |
| `K6_per_symbol_observed_win_rate_dispersion` | **NOT APPLICABLE** |
| Per-symbol contribution distribution | trivially 100% to MNQ.c.0 |
| Diversification claim by this candidate | NONE |
| Disclaimer carried byte-equivalent | "Diversification independence does NOT imply positive edge" (LESSON_B006_002_002) |

## 13. OOS locking policy (LOCKED at SEAL; carried byte-equivalent)

| Policy | Status |
|---|---|
| OOS data shall not be inspected during IS phase | LOCKED |
| `oos_inspection_blocked_at_in_sample` invariant | LOCKED |
| OOS inspection requires separately authorized turn after IS verdict `ELIGIBLE_FOR_OOS` | LOCKED |
| **OOS confirmation definition** | LOCKED at SEAL using s11-d1 rev2 magnitude-based form |

s11-d1 rev2 oos_confirmation_definition (carried byte-equivalent):

> *"OOS is CONFIRMED only iff ALL of: (a) C7 verdict is READY_FOR_LONGER_BACKTEST, (b) OOS closed_trades >= 100, (c) OOS sharpe > 0, (d) OOS expectancy > 0, (e) OOS trade_curve_maxdd_pct >= -30% (equivalently |trade_curve_maxdd_pct| <= 30%; i.e., the realized OOS drawdown shall not exceed 30% in magnitude), (f) all safety counters zero, (g) no-pyramid invariant held, (h) starting_cash invariant held."*

## 14. No-live / no-Strategy-Lab / no-brokerage policy (LOCKED at SEAL; carried byte-equivalent)

Total invariants at SEAL: **25** for F3 single-instrument (no DR11; same count as s12-d1; mechanic substitution does not change invariant count).

7 inherited B005_NNN framework:
- `no_live_trading` * `no_strategy_lab_promotion` * `no_review_queue_mutation` * `no_brokerage_connection` * `no_external_network` * `no_databento_at_runtime` * `no_production_signal`

4 inherited B006_001:
- `no_strategy_optimization_authorized` * `no_profitability_claim` * `no_universe_membership_logic` * `no_dr_redefinition_post_seal`

2 inherited B006_002 (no leverage cap for F3):
- `no_warmup_order_submission` * `dr6_warmup_contamination_blocked`

5 inherited s10-d1-specific:
- `no_continuous_roll_stitch_modification_post_seal` * `no_mcl_inclusion_under_long_history_scope` * `no_intraday_schema_ingest_under_daily_only_design` * `databento_api_key_read_from_env_only_never_logged_or_saved` * `no_pyramid_per_signal`

3 inherited s11-d1-specific:
- `single_instrument_universe_NO_widening_post_seal` * `no_substitution_of_any_symbol_into_this_universe_post_seal` * `mnq_c0_csv_reuse_byte_equivalent_no_fresh_fetch`

4 NEW s13-d1-specific (LOCKED at SEAL):
- `rsi_2_bi_directional_thresholds_locked_at_plan_no_retreat_to_long_only_or_different_thresholds`
- `mechanic_family_F3_lock_at_plan_no_reopening_at_draft_or_seal`
- `no_revision_of_s12_d1_terminal_park_via_this_candidate_id`
- `k9_reachability_discipline_applied_at_plan_time_per_new_framework_requirement`

Status surface (permanent for this candidate, independent of any future verdict):

| Field | Value |
|---|---|
| Trading | `PAUSED` |
| Live mode | `BLOCKED_AT_6_GATES` |
| FRC | `NEVER_GRANTED` |
| `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` | permanent |
| Six live-trading gates BLOCKED regardless of verdict | YES |

## 15. Reject-fast criteria (LOCKED at SEAL)

The candidate is REJECTED FAST if ANY of:

- **RF1** Any DR rule fires `REJECT_FAST` (**DR3 + DR5 + DR10 elevated for s13-d1** plus DR2/DR4/DR6)
- **RF2** DR9 `mnq_c0_only_data_continuity_integrity_failure`
- **RF3** DR6 post-warmup invalid-sizing event count > 0
- **RF4** Any forbidden-verdict-token in runner output
- **RF5** Runner attempts `SetLiveMode` / `SetBrokerageModel` / `DeployAlgorithm` / unauthorized network / Databento call at runtime
- **RF6** Any order-submit attempt while in warmup window
- **RF7** Runner mutates any s11-d1 / s12-d1 / s10-d2 / s10-d1 / s9 / s7-d1 / B006_NNN / T8 / s13-d1 sealed artifact (byte-shift)
- **RF8** Runner makes a Databento API call at any phase
- **RF9** Runner caches `.dbn.zst` files anywhere
- **RF10** Runner accesses `DATABENTO_API_KEY` at any phase
- **RF11** Track silently re-introduces a filter, regime gate, or selection rule
- **RF12** Pyramid mechanism re-introduced
- **RF13** **RSI thresholds silently switched from LOCKED 10/50/90/50 post-SEAL**
- **RF14** Universe widening or symbol substitution at any phase
- **RF15** Track depends on a survivorship-cherry-pick rule
- **RF16** Any retroactive re-anchoring or modification of s12-d1 terminal park (revival forbidden)

K-gates carried byte-equivalent with F3-specific notes:

- **K1** `sharpe_proxy_per_trade_below_zero_at_S1`
- **K2** `expectancy_per_trade_dollars_nonpositive_at_S1`
- **K4** `trade_curve_max_drawdown_above_threshold` (DA5 default: 50% magnitude)
- **K6** NOT APPLICABLE (single-instrument)
- **K7** `silent_filter_introduction_after_lock`
- **K8** `runtime_safety_invariant_false`
- **K9** `closed_trades_below_100` (clears with significant margin at IS; clears at lower bound at OOS)
- **K10** NOT APPLICABLE (single-instrument)
- **K11** NOT APPLICABLE (no leverage cap)
- **K12** composite cost-stress fail (DR2 + DR3) -- **MORE LIKELY for s13-d1** given RSI lineage risk

K-gate firing priority order: `K8 > K12 > K7 > K9 > K1/K2/K4 > A-gates > ELIGIBLE_FOR_OOS`.

## 16. Validation gates

Validation gates the DRAFT-authoring turn satisfies:

- **V1** ASCII-only.
- **V2** Numbered sections in monotonic order (1..17).
- **V3** No execution language.
- **V4** No self-authorization (this DRAFT does NOT authorize SEAL).
- **V5** No code modification.
- **V6** No backtest / simulator / signal computation.
- **V7** No data fetch / Databento call / `DATABENTO_API_KEY` access.
- **V8** No network IO.
- **V9** No live trading.
- **V10** No prior-phase artifact modification (s11-d1 / s12-d1 / s10-d2 / s10-d1 / s9 / s7-d1 / B005 / B006 / T8 all byte-stable).
- **V11** The committed DRAFT file is the ONLY new file in this turn's commit.
- **V12** `lessons.md` UNSTAGED and UNTOUCHED.
- **V13** Mechanic family F3 + RSI thresholds (10/50/90/50) LOCKED at PLAN; DRAFT does NOT reopen.
- **V14** Single-instrument adaptations explicit (A7/K10/K6 NOT APPLICABLE; DR11 structurally absent).
- **V15** DA register includes only the parameters NOT locked at PLAN.
- **V16** **K9-reachability table carried byte-equivalent from PLAN** (NEW framework discipline at DRAFT time).
- **V17** **REC1-equivalent OOS K9 disclosure carried byte-equivalent from PLAN** (NEW framework discipline).

## 17. HALT conditions + DRAFT ambiguity register

HALT conditions:

- **H1** If any V-gate fails, the turn HALTs.
- **H2** If pre-stage git index is non-empty, the turn HALTs.
- **H3** If staged file count is anything other than 1 at commit time, the turn HALTs.
- **H4** If staged file is anything other than `docs/s13_d1_mnq_c0_single_instrument_rsi_2_bi_directional_databento_long_history_tier_n_spec_DRAFT.md`, the turn HALTs.
- **H5** If `lessons.md` is accidentally staged, the turn HALTs and remediates.
- **H6** If any s11-d1 / s12-d1 / earlier-candidate sealed artifact is detected as modified, the turn HALTs.

### 17.1 DRAFT ambiguity register (for operator confirmation at SEAL; operator types option letter)

Note: RSI parameters (period=2, thresholds 10/50/90/50), mechanic family F3, universe, signal direction (bi-directional), pyramid (NONE), and IS/OOS windows are LOCKED at PLAN and are intentionally NOT in this register. The DA register covers ONLY parameters deferred from PLAN to DRAFT/SEAL.

- **DA1** ATR stop window P: A `20` (default; Wilder; carried byte-equivalent from s12-d1) / B `14` (Wilder canonical) / C `10` (faster stop)
- **DA2** ATR stop multiplier K: A `2.0` (default; 2N stop carried) / B `1.5` (tighter) / C `2.5` (looser)
- **DA3** Per-trade risk percentage: A `1.0%` of portfolio equity (default; carried byte-equivalent) / B `0.5%` (more conservative; reduces DR10 cost-drag exposure) / C `2.0%` (more aggressive; flagged for K4 risk)
- **DA4** `START_CASH_USD`: A `100000` (default; **s12-d1 DA4=B carried byte-equivalent**; halves per-dollar cost pressure under RSI's higher turnover) / B `50000` (s11-d1 v1 baseline; lower cash; higher DR10 risk) / C `200000` (more aggressive DR10 mitigation)
- **DA5** K4 max-drawdown threshold (magnitude): A `0.50` (50%; carried byte-equivalent from s12-d1 K4 formula) / B `0.30` (more conservative) / C `0.40` (intermediate)
- **DA6** Output schema name: A `sparta.s13.d1.mnq_c0.rsi_2_bidir.diagnostic_run_report.v1` (default) -- LOCKED at SEAL
- **DA7** Cost-stress tier set: A 5-tier `S0/S1/S2/S3/S4` with scalars `0.0 / 1.0 / 1.5 / 2.0 / 3.0` (default; carried byte-equivalent) -- LOCKED at SEAL non-negotiable per `no_dr_redefinition_post_seal`
- **DA8** Commission per round-trip: A `$0.74` (default; carried byte-equivalent) -- LOCKED at SEAL
- **DA9** Fees per round-trip: A `$0.36` (default; carried byte-equivalent) -- LOCKED at SEAL
- **DA10** Slippage entry/stop/exit ticks: A `1 / 1 / 1` (default; carried byte-equivalent) -- LOCKED at SEAL
- **DA11** `WARMUP_DAYS`: A `MAX(longest_lookback, 220)` resolved to `220` (default; longest s13-d1 lookback is ATR(20); floor at 220) -- LOCKED at SEAL
- **DA12** RTH window: A `09:30-16:00 ET America/New_York` (default; carried byte-equivalent) -- LOCKED at SEAL
- **DA13** DR9 thresholds: A `0.95 / 0.30 / 5 / 5` (carried byte-equivalent) -- LOCKED at SEAL non-negotiable per `no_dr_redefinition_post_seal`
- **DA14** DR10 thresholds: A `annual_turnover > 0.50` AND `s2_cost_drag > 0.05` (carried byte-equivalent) -- LOCKED at SEAL non-negotiable per `no_dr_redefinition_post_seal`

The operator confirms DA1-DA14 at the SEAL turn by typing an explicit revision authorization (e.g., "Authorize s13 D1 MNQ.c.0 Tier-N spec SEAL. Confirm all DRAFT ambiguities as default A.") or revises the genuinely-negotiable items (DA1-DA5; DA6-DA14 are framework-locked).

### 17.2 Mitigation note for DR3 + DR10 risk (informational; no parameter change authorized at DRAFT)

Two specific risks are elevated for s13-d1 and warrant operator awareness at SEAL:

1. **DR3 risk (zero-cost-only survival):** RSI mean-reversion mechanics historically show S0-positive but S1+ cost-erosion. The s9 ETF-proxy precedent fired DR2/DR3. DRAFT-level mitigation lever: DA3=B (0.5% per-trade risk; reduces per-trade cost-drag intensity); DA4=A or C (higher START_CASH; halves per-dollar cost pressure).

2. **DR10 risk (turnover-cost-explosion):** RSI ~50-65 trades/year produces ~5-10× s11-d1 v1's Donchian-55/20 turnover. S2 cost drag > 5% triggers DR10 REJECT_FAST. DRAFT-level mitigation lever: DA4=C ($200k START_CASH); DA3=B (0.5% risk).

Neither lever changes DR thresholds (forbidden); they change the strategy's economic profile.

----

## 18. Next authorization language

A future operator authorization is required to proceed beyond this DRAFT. That authorization shall reference this DRAFT by exact path:

`docs/s13_d1_mnq_c0_single_instrument_rsi_2_bi_directional_databento_long_history_tier_n_spec_DRAFT.md`

The next operator authorization shall use one of these scopes:

### Most natural progression (accept all DRAFT defaults)
```
Authorize s13 D1 MNQ.c.0 Tier-N spec SEAL. Confirm all DRAFT ambiguities as default A.
```
Locks: ATR-20 K=2.0, bi-directional (already locked), 1.0% risk, K4 50%, K9 100, START_CASH $100k (s12-d1 DA4=B carried), WARMUP 220, RTH 09:30-16:00 ET, output schema `sparta.s13.d1.mnq_c0.rsi_2_bidir.diagnostic_run_report.v1`, 5-tier cost stress, DR9 / DR10 thresholds carried byte-equivalent.

### Alternative: DR3/DR10 mitigation via risk-pct revision
```
Authorize s13 D1 MNQ.c.0 Tier-N spec SEAL with revisions: DA3=B; all others as default A.
```
Sets per-trade risk to 0.5%; reduces per-trade cost-drag intensity.

### Alternative: DR10 mitigation via START_CASH revision
```
Authorize s13 D1 MNQ.c.0 Tier-N spec SEAL with revisions: DA4=C; all others as default A.
```
Sets START_CASH at $200k (doubled vs s12-d1 baseline); halves per-dollar cost pressure relative to s12-d1.

### Alternative: combined DA3 + DA4 mitigation
```
Authorize s13 D1 MNQ.c.0 Tier-N spec SEAL with revisions: DA3=B, DA4=C; all others as default A.
```

### Reject / pivot
```
Authorize alternative selection plan rev2 only.
```
```
Authorize cross-domain pivot only.
```
```
Defer / Pause trading-bot track.
```

This DRAFT is the source of truth for the s13-d1 MNQ.c.0 single-instrument RSI(2) bi-directional candidate's intended Tier-N spec scope at DRAFT time.

----

End of DRAFT. Plan / spec DRAFT only. No code. No backtest. No simulator. No signal. No data fetch. No yfinance. No Yahoo Finance. No Databento. No `DATABENTO_API_KEY` access. No QC. No LEAN. No brokerage. No real order. No paper order. No Strategy Lab promotion. No `review_queue` mutation. No production `idea_memory` mutation. No ORB branch mutation. **No `lessons.md` modification or staging.** No live trading. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES.
