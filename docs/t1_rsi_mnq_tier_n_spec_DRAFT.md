# T1 RSI MNQ.c.0 Bi-Directional Mean-Reversion — Tier-N Specification DRAFT

**Status:** DRAFT (not sealed; operator confirms DRAFT ambiguities DA1-DA14 at SEAL; no code, no fetch, no run by this DRAFT).
**Authored (UTC):** `2026-05-27T17:30:00Z`
**Authorization:** *"Authorize T1 RSI MNQ Tier-N spec DRAFT only."*
**Controller session:** THIS_SESSION_ONLY

**PLAN source:** `docs/t1_rsi_mnq_tier_n_spec_plan.md` (committed at `729207f`; seal `70549a9ac2c15f361a4cb7319b1bde2e963cbbfe8aa4e4757eebedbd77eeca4d`).

**Parent reference chain (READ-ONLY; byte-stable; not modified by this DRAFT):**
- T1 PLAN commit `729207f`; seal `70549a9ac2c15f36`
- S12-D1 P11 PARK memo (this session): `ce279cf` seal `321b8940a5516762`
- S12-D1 P11 PARK memo (parallel canonical): `ecbd0011` seal `b9722d424f6faabe`
- S12-D1 sealed Tier-N spec (this session): `9ce4d66` seal `422bbbff75f24816`
- S10-D2 lifecycle park report (this session): `b580aedb` seal `8d59e94a736aa82d`
- Parallel post-park selection plan: `0e3f9d49` (`docs/next_research_track_selection_plan_after_s12_d1_park.md`)
- Parallel `s13-d1` DRAFT (distinct chain at non-colliding paths): `8fcefaf` (read-only awareness; not anchored)
- Audit-clean MNQ.c.0 CSV: `data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_1d_2019-05-13_2025-12-30.csv` (sha256 `8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e`; 2,066 rows; 2019-05-13 → 2025-12-29)

**HARD BOUNDARIES** (held by this DRAFT). Plan/spec DRAFT only. No strategy code. No backtest. No simulator. No signal computation. No RSI computation. No data fetch. No yfinance / Yahoo Finance call. No Databento call. No `DATABENTO_API_KEY` access. No QC / LEAN call. No network IO. No `review_queue.json` mutation. No production `idea_memory` mutation. No Strategy Lab run. No candidate promotion. No T1 PLAN / s11-d1 / s12-d1 / parallel s13-d1 sealed-artifact modification. No s10-d2 / s10-d1 / s9 / s7-d1 / s8-d1 / B005_NNN / B006_NNN / T8 sealed-artifact modification. No ORB branch mutation. No Step 30 cost constant mutation. No CLAUDE.md modification. No `docs/decisions.md` modification. No RUNBOOK modification. No `pipeline_manifest` modification. No `.gitignore` modification. **No `brain_memory/projects/trading_bot/lessons.md` modification or staging.** No branch change. No branch creation. No git push. No live trading. No profitability claim. **Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES. FRC NEVER GRANTED. Advisory label permanent: `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE`. `verdict_never_means_live_ready: True`.**

----

## 1. Mechanic family + RSI parameters LOCKED at PLAN — DRAFT does NOT reopen

This DRAFT does **NOT** reopen mechanic-family selection nor RSI period nor entry/exit framework directionality. All were LOCKED at PLAN (commit `729207f`) as the load-bearing structural property of the T1 `candidate_record_id`.

The DRAFT confirms and carries forward (without revision option):

| Field | LOCKED at PLAN | Carried byte-equivalent into this DRAFT |
|---|---|---|
| `candidate_record_id` | `t1-rsi-mnq-c0-mean-reversion-2-period-databento-long-history` | yes |
| Mechanic family | **F3** — Long+Short Bi-Directional RSI Mean-Reversion, No Pyramid, ATR-Based Stop, Single MNQ.c.0 Contract Per Signal | yes |
| Universe | `{MNQ.c.0}` only | yes |
| **RSI period** | **2** (Connors canonical; load-bearing departure from F1 trend) | yes |
| Signal direction | Long + Short bi-directional | yes |
| Entry framework | Long when RSI(2) < oversold_threshold; Short when RSI(2) > overbought_threshold | yes |
| Exit framework | RSI(2) recross to centerline (default 50); OR ATR stop; OR max-bars time stop | yes |
| Pyramid mechanism | NONE / `max_units_per_market = 1` | yes |
| Schema | `ohlcv-1d` | yes |
| `stype_in` | `continuous` | yes |
| IS window | `2019-05-13 → 2023-12-29` | yes |
| OOS window | `2024-01-02 → 2025-12-30` (never inspected at IS) | yes |

A SEAL revision authorization that attempts to alter any of these PLAN-locked fields shall be rejected by the controller and require either (a) a fresh PLAN revision turn, or (b) a fresh `candidate_record_id` per the same first-principles burden that gave rise to T1 itself.

## 2. Why T1 RSI MNQ.c.0 is not rescuing s12-d1, s11-d1, s10-D2, s10-D1, s9, s7-D1, B006_NNN

The T1 PLAN section §3 enumerates the first-principles burden against each parked predecessor. T1 satisfies all 8 forbidden-track exclusions (T-FORBID-1 through T-FORBID-8) carried from `0e3f9d49`. Brief restatement at DRAFT:

### 2.1 vs s12-d1 (Donchian-15/8 MNQ.c.0; parked INSUFFICIENT_SAMPLE_AT_IS)

| s12-d1 feature | T1 F3 treatment |
|---|---|
| Donchian-15 entry / Donchian-8 exit channel breakout | RSI(2) oscillator-based mean-reversion entry/exit |
| K9 risk: ~7-10 trades/y fired K9 at IS (33 actual) | K9 risk: ~46-68 trades/y (5-6× higher signal density); IS clears with margin |
| Mechanic family F1 (trend-following) | Mechanic family F3 (mean-reversion); orthogonal |
| s12-d1 P3 BUILD / P4 SMOKE / P6 IS byte-stable | T1 does NOT modify any s12-d1 artifact |

### 2.2 vs s9 (RSI-2 mean-reversion on SPY/TLT/GLD/USO ETF-proxy; parked K1+K2)

| s9 feature | T1 F3 treatment |
|---|---|
| Universe `{SPY, TLT, GLD, USO}` (4 ETFs) | Universe `{MNQ.c.0}` only (single futures instrument) |
| Long-only RSI-2 | Bi-directional (long + short) |
| Asset class: equity ETFs | Asset class: micro-futures |
| Cost surface: per-share commission + bps | Cost surface: per-contract commission + tick slippage |
| s9 falsification: K1 sharpe<0 + K2 expectancy≤0 at S1 on ETF basket | T1 first-principles claim: s9 falsification was instrument-specific cost/edge interaction on the 4-ETF basket; does NOT transfer to MNQ futures |

### 2.3 vs s10-D2 (4-market Donchian-55/20 portfolio; parked OOS_INDETERMINATE)

| s10-D2 feature | T1 F3 treatment |
|---|---|
| Universe `{NQ, GC, ZN, CL}` (4 markets) | Universe `{MNQ.c.0}` only |
| Donchian-55/20 trend | RSI(2) mean-reversion; orthogonal mechanic |
| OOS K9 fired (53 trades on 3y OOS) | T1 OOS K9 borderline at lower bound (46/y vs 50/y); central/upper clear |

### 2.4 vs s10-D1 (MNQ+MGC Donchian; parked DR9)

| s10-D1 feature | T1 F3 treatment |
|---|---|
| Universe `{MNQ.c.0, MGC.c.0}` | Universe `{MNQ.c.0}` only; MGC structurally absent |
| MGC continuous-stitch DR9 fire | MGC absent; DR9 risk reduces to MNQ.c.0 (audit-clean) |
| Donchian mechanic | RSI(2) mechanic; orthogonal |

### 2.5 vs s7-D1 / s8-D1 / s11-d1 / B006_NNN / T8 / NKE

| Predecessor | T1 F3 treatment |
|---|---|
| s7-D1 (Donchian + pyramid 4-ETF) | NO pyramid; different mechanic; different universe |
| s8-D1 (Donchian no-pyramid 4-market) | Different mechanic; single instrument; sizing fix inherited |
| s11-d1 (Donchian-55/20 single MNQ.c.0; sealed but never ran) | Different mechanic; ~5-6× higher signal density |
| B006_001/002 (SPY vol-targeting) | Different asset class; F3 has no leverage cap; DR11 absent |
| T8 ETF-proxy umbrella | Different asset class |
| NKE Tier-1 Options Wheel | Different mechanic; strategy logic NOT inherited |

### 2.6 vs parallel session's `s13-d1` chain

| | Parallel `s13-d1` | T1 (this session) |
|---|---|---|
| `candidate_record_id` | `s13-d1-mnq-c0-rsi-2-bidirectional-...` (longer naming) | `t1-rsi-mnq-c0-mean-reversion-2-period-...` |
| File paths | `..._databento_long_history_...` prefix | `t1_rsi_mnq_...` prefix |
| Chain at | SEAL `262491c` → P1 `005cb8a` → P2 `beecd87` → P2 supplement `508285f` | PLAN `729207f` → DRAFT (this turn) |
| Substantive content | Likely converges (RSI(2) bi-directional MNQ.c.0 IS/OOS) | Same core; this session's chain at non-colliding paths |

T1 chain is **distinct** from parallel `s13-d1` chain. No path collision. No artifact modification.

T1 satisfies all first-principles-burden requirements. The candidate is **structurally fresh**, not a revision of any predecessor.

## 3. Universe (LOCKED at PLAN; restated at SEAL)

| Field | LOCKED value |
|---|---|
| Universe type | `single_fixed_instrument_continuous_micro_futures` |
| Symbol 1 (only symbol) | **`MNQ.c.0`** (Micro E-mini Nasdaq-100, continuous front-month) |
| `AddUniverse` calls | **0** (structurally absent) |
| `removed_from_universe` events | **0** (structurally absent) |
| Symbol count | exactly 1 |
| Symbol substitution clause at later phases | FORBIDDEN (LOCKED at SEAL via `single_instrument_universe_NO_widening_post_seal`) |
| Universe widening at later phases | FORBIDDEN (any wider basket requires a fresh `candidate_record_id`) |
| Common-history start (verified by s10-D1 audit) | **2019-05-13** |
| Diversification claim by this candidate | NONE (single-instrument; explicit first-principles justification) |

## 4. Dataset (LOCKED at SEAL)

| Field | LOCKED value |
|---|---|
| Vendor | **Databento Historical API** (vendor-level; controller never calls at runtime) |
| Dataset | **`GLBX.MDP3`** |
| Schema | **`ohlcv-1d`** |
| `stype_in` | **`continuous`** |
| Symbol requested | `["MNQ.c.0"]` |
| Re-use of existing audit-clean CSV | **TRUE** — `data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_1d_2019-05-13_2025-12-30.csv` (sha256 `8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e`) reused byte-equivalent. **ZERO new Databento call required.** |
| Step 02b for this candidate | manifest cross-link only (separately authorized; no fresh fetch) |
| API key handling | NOT REQUIRED at any phase |
| Controller-side Databento call | LOCKED OFF at every phase |

## 5. Schema (LOCKED at SEAL)

| Field | LOCKED value |
|---|---|
| Schema | `ohlcv-1d` |
| Records expected per trading day | 1 (daily bar) |
| Fields | `ts_event`, `open`, `high`, `low`, `close`, `volume` |
| Intraday schemas | OUT OF SCOPE for this Tier-N |

## 6. stype_in (LOCKED at SEAL)

| Field | LOCKED value |
|---|---|
| `stype_in` | `continuous` |
| Continuous roll stitch | Databento native continuous-front-month synthesis |
| `no_continuous_roll_stitch_modification_post_seal` invariant | TRUE |

## 7. IS / OOS windows (LOCKED at SEAL)

| Field | LOCKED value |
|---|---|
| **IS window start** | **`2019-05-13`** |
| **IS window end** | **`2023-12-29`** |
| IS window length | ~4.6 years (~1,140 trading days; 1,443 audit-confirmed rows) |
| **OOS window start (never inspected at IS)** | **`2024-01-02`** |
| **OOS window end (never inspected at IS)** | **`2025-12-30`** |
| OOS window length | ~2 years (622 structural-only rows) |
| Post-OOS data | `2026-01-02 onward` (informational only) |
| OOS inspection at IS-phase | FORBIDDEN (`oos_inspection_blocked_at_in_sample`) |

## 8. Data availability assumptions and DR gates

### 8.1 Assumptions inherited from s10-D1 audits

- `MNQ.c.0` over `2019-05-13 → 2025-12-30` is **DR9-clean** under both audit variants (strict + holiday-aware; 0 calendar gaps > 5 days; max single-day abs-log-return 0.1164).
- DR9 thresholds carried byte-equivalent (`0.95 / 0.30 / 5 / 5`).
- Step 02c for this candidate is a re-confirmation pass against the same CSV (no fresh Databento call).

### 8.2 DR rules adapted for single-instrument F3 RSI(2) (LOCKED at SEAL)

| Rule | Trigger | Severity | F3-RSI(2) note |
|---|---|---|---|
| DR1 | `oos_rebalance_count < 36` OR `oos_closed_trades < K9_threshold` (OOS phase) | `INCONCLUSIVE_HOLD` | Extended at SEAL per C1.D lineage |
| DR2 | `oos_metrics_degrade_materially_under_cost_stress` | `REJECT_FAST` | **ELEVATED prior probability** under mean-reversion |
| DR3 | `zero_cost_only_survival` (S0 > 0 AND all S1..S4 ≤ 0) | `REJECT_FAST` | **ELEVATED prior probability** under mean-reversion |
| DR4 | `oos_negative_while_is_positive_unexplained` | `REJECT_FAST` | OOS-only |
| DR5 | `cost_stress_turns_edge_negative` (tier flip) | `REJECT_FAST` / carveout | **ELEVATED prior probability** under mean-reversion |
| DR6 | `post_warmup_sizing_ambiguity_or_invalid` | `REJECT_FAST` | unchanged; carried from B006_002 lineage |
| DR7 | `missing_oos_or_date_window_evidence` | `INCONCLUSIVE_HOLD` | unchanged |
| DR8 | `live_or_order_routing_path_detected` at Initialize | `HARD_FAIL_VOIDED` | unchanged |
| **DR9** | `mnq_c0_only_data_continuity_integrity_check` (0.95 / 0.30 / 5 / 5) | `INCONCLUSIVE_HOLD` | MNQ-only; MGC absent |
| **DR10** | `turnover_cost_explosion` (`annual_turnover > 0.50` OR `S2 cost drag > 0.05`) | `REJECT_FAST` | **ELEVATED prior probability vs s12-d1** because RSI(2) trades 5-6× as often as Donchian-15/8; per-trade dollar move smaller; dollar-turnover ~30-40× higher. Load-bearing trade-off accepted at PLAN. |
| DR11 | NOT IN CHAIN | — | F3 has no leverage cap; DR11 structurally absent |

DR precedence chain (LOCKED at SEAL): `DR7 → DR1 → DR9 → DR10 → DR6 → DR4 → DR2 → DR3 → DR5` (carried byte-equivalent from s12-d1 lineage).

## 9. Cost stress from day 1 (LOCKED at SEAL)

Cost-stress matrix S0/S1/S2/S3/S4 LOCKED in the first IS diagnostic; deferral forbidden. Carried byte-equivalent from s11-d1 / s12-d1 v1 (5-tier set).

### 9.1 Cost tiers (5-tier; carried byte-equivalent)

| Tier | `cost_scalar` | `slippage_scalar` | Note |
|---|---:|---:|---|
| `S0` | 0.0 | 0.0 | zero-cost ideal; tests if a profitable kernel exists |
| `S1` | 1.0 | 1.0 | baseline retail; commission + fees + slip @ 1.0× |
| `S2` | 1.5 | 1.5 | stressed retail |
| `S3` | 2.0 | 2.0 | adversarial |
| `S4` | 3.0 | 3.0 | extreme adversarial |

### 9.2 Tick / contract specs (LOCKED at SEAL; framework-locked DA8-DA10)

| Symbol | Tick size | Dollar per tick |
|---|---|---|
| `MNQ.c.0` | 0.25 index points | **$0.50 per contract** |

### 9.3 Pre-registered S0 edge sign and magnitude (DRAFT-time)

| Field | DRAFT-proposed value |
|---|---|
| Expected S0 net PnL sign | open question (no a-priori claim); **elevated risk of S2/S3 flip-negative under RSI(2) cost sensitivity** |
| Acceptance threshold S0 net PnL | `> 0` after ≥ 100 trades |
| Acceptance threshold S1 net PnL | `> 0` (K1 / K2 fire if `≤ 0`) |
| Pre-registered max-drawdown tolerance | K4 = 50% of `START_CASH_USD` (DA10 default; carried byte-equivalent from s12-d1) |
| Pre-registered cost-stress survival | all five cost tiers OOS Sharpe > 0 → `ELIGIBLE_FOR_HUMAN_REVIEW`; S0/S1 positive but S2/S3/S4 degrade > 50% → K12 REJECT_FAST |

## 10. Sample-size / K9 rules (LOCKED at SEAL)

| Field | LOCKED value (DRAFT) |
|---|---|
| K9 threshold | `total_closed_trades ≥ 100` over IS window AND over OOS window (LOCKED non-negotiable; `no_k9_relaxation`) |
| Expected trade count for F3 RSI(2) bi-directional on MNQ.c.0 over 4.6y IS | **210–313 portfolio trades** (lower 210, central 262, upper 313; ~46–68 trades/y) |
| Comparison to s12-d1 (Donchian-15/8) | s12-d1 actual = 33 IS trades (fired K9); T1 expects 6–9× more signals (clears IS K9 with margin) |
| Expected OOS trade count (proportional 2.0y/4.6y) | ~91–136 trades (~46–68/y × 2.0y) |
| **OOS K9 risk at lower bound** | **46 trades/y × 2.0y = 92 trades** ≈ K9 = 100 threshold; **BORDERLINE; fires at lower bound** |
| OOS K9 risk at central | 57 × 2.0y = 114 trades > 100 → CLEARS |
| OOS K9 risk at upper | 68 × 2.0y = 136 trades > 100 → CLEARS with margin |
| If OOS K9 fires anyway | DR1 `INCONCLUSIVE_HOLD` (NOT REJECT_FAST); candidate archived per C1.D lineage |

## 11. Diversification expectations — single-instrument scope (LOCKED at SEAL)

| Field | LOCKED value |
|---|---|
| `A7_effective_independent_bets_min` | **NOT APPLICABLE** (trivially 1 by construction; removed from acceptance gate set) |
| `K10_avg_pairwise_dependence_max` | **NOT APPLICABLE** (no pairs; removed from K-gate set) |
| `K6_per_symbol_observed_win_rate_dispersion` | **NOT APPLICABLE** (no dispersion to measure) |
| Per-symbol contribution distribution | trivially 100% to MNQ.c.0 |
| Diversification claim by this candidate | NONE |
| Disclaimer | "Diversification independence does NOT imply positive edge" (LESSON_B006_002_002) — applies trivially here |

## 12. OOS locking policy (LOCKED at SEAL; carried byte-equivalent)

| Policy | Status |
|---|---|
| OOS data shall not be inspected, computed against, simulated over, or queried during IS phase | LOCKED |
| Post-OOS data is informational only; no diagnostic uses it | LOCKED |
| OOS inspection requires a separately authorized turn after IS verdict `ELIGIBLE_FOR_OOS` + explicit operator approval | LOCKED |
| Modules shall structurally enforce IS-only computation (sibling driver design) | LOCKED (`oos_inspection_blocked_at_in_sample`) |
| **OOS confirmation definition** | LOCKED at SEAL using **s11-d1 rev2 magnitude-based form** byte-equivalent (carried from `c110fd4`); v1 sign/inequality typo NOT re-introduced |

OOS CONFIRMED iff ALL of:
1. C7 verdict is READY_FOR_LONGER_BACKTEST
2. OOS closed_trades ≥ 100
3. OOS sharpe > 0
4. OOS expectancy > 0
5. OOS `trade_curve_maxdd_pct ≥ -30%` (i.e., `|maxdd| ≤ 30%`)
6. all safety counters zero
7. no-pyramid invariant held
8. starting_cash invariant held

## 13. No-live / no-Strategy-Lab / no-brokerage policy (LOCKED at SEAL)

Total invariants at SEAL: **25** for F3 RSI(2) single-instrument (no DR11; no C4 invariants).

**7 inherited B005_NNN framework:** `no_live_trading` · `no_strategy_lab_promotion` · `no_review_queue_mutation` · `no_brokerage_connection` · `no_external_network` · `no_databento_at_runtime` · `no_production_signal`

**4 inherited B006_001:** `no_strategy_optimization_authorized` · `no_profitability_claim` · `no_universe_membership_logic` · `no_dr_redefinition_post_seal`

**2 inherited B006_002:** `no_warmup_order_submission` · `dr6_warmup_contamination_blocked`

**5 inherited s10-D1-specific:** `no_continuous_roll_stitch_modification_post_seal` · `no_mcl_inclusion_under_long_history_scope` · `no_intraday_schema_ingest_under_daily_only_design` · `databento_api_key_read_from_env_only_never_logged_or_saved` · `no_pyramid_per_signal`

**3 inherited s11-d1-specific:** `single_instrument_universe_NO_widening_post_seal` · `no_substitution_of_any_symbol_into_this_universe_post_seal` · `mnq_c0_csv_reuse_byte_equivalent_no_fresh_fetch`

**4 NEW T1-specific (LOCKED at SEAL):**
- `rsi_period_2_locked_at_plan_no_retreat_to_3_4_or_other`
- `mean_reversion_centerline_50_locked_at_plan_no_drift_to_55_60`
- `bi_directional_locked_at_plan_no_retreat_to_long_only`
- `mechanic_family_f3_lock_at_plan_no_reopening_at_draft_or_seal`

Status surface (permanent for this candidate, independent of any future verdict):

| Field | Value |
|---|---|
| Trading | `PAUSED` |
| Live mode | `BLOCKED_AT_6_GATES` |
| FRC | `NEVER_GRANTED` |
| `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` | permanent |
| Six live-trading gates BLOCKED regardless of verdict | YES |

## 14. Reject-fast criteria (LOCKED at SEAL)

The candidate is REJECTED FAST if ANY of:

- **RF1** Any DR rule fires `REJECT_FAST` (DR2 / DR3 / DR4 / DR5 / DR6 / DR10)
- **RF2** DR9 `mnq_c0_only_data_continuity_integrity_failure` AND > 5 violations (extremely unlikely given audit-clean finding)
- **RF3** DR6 post-warmup invalid-sizing event count > 0
- **RF4** Any forbidden-verdict-token in runner output
- **RF5** Runner attempts `SetLiveMode` / `SetBrokerageModel` / `DeployAlgorithm` / unauthorized network call / unauthorized Databento call at runtime
- **RF6** Any order-submit attempt while in warmup window
- **RF7** Runner mutates any T1 PLAN / s11-d1 / s12-d1 / parallel s13-d1 / s10-d2 / s10-d1 / s9 / s7-d1 / s8-d1 / B006_NNN / T8 / NKE / ORB sealed artifact (byte-shift)
- **RF8** Runner makes a Databento API call at any phase (controller-side; this candidate is zero-fresh-fetch)
- **RF9** Runner caches `.dbn.zst` files anywhere
- **RF10** Runner accesses `DATABENTO_API_KEY` at any phase
- **RF11** Track silently re-introduces a filter, regime gate, or selection rule
- **RF12** Pyramid mechanism re-introduced in code
- **RF13** RSI period silently switched from the LOCKED 2 post-SEAL
- **RF14** Mean-reversion centerline silently switched from the LOCKED 50 post-SEAL
- **RF15** Universe widening or symbol substitution attempted at any phase
- **RF16** Track depends on a survivorship-cherry-pick rule
- **RF17** Any retroactive re-anchoring or modification of T1 PLAN / s11-d1 / s12-d1 caused by this candidate

K-gates carried byte-equivalent from s12-d1 with F3-RSI(2) adaptations:

- **K1** `sharpe_proxy_per_trade_below_zero_at_S1`
- **K2** `expectancy_per_trade_dollars_nonpositive_at_S1`
- **K4** `trade_curve_max_drawdown_above_threshold` (DA10 default: K4 = 50% of `START_CASH_USD`)
- **K6** NOT APPLICABLE (single-instrument)
- **K7** `silent_filter_introduction_after_lock`
- **K8** `runtime_safety_invariant_false`
- **K9** `closed_trades_below_100` (IS + OOS both)
- **K10** NOT APPLICABLE (single-instrument)
- **K11** NOT APPLICABLE (no leverage cap for F3)
- **K12** composite cost-stress fail (DR2 + DR3); **ELEVATED prior probability under mean-reversion**

K-gate firing priority order: `K8 > K12 > K7 > K9 > K1/K2/K4 > A-gates > ELIGIBLE_FOR_OOS`.

## 15. Validation gates

Validation gates the DRAFT-authoring turn satisfies:

- **V1** ASCII-only.
- **V2** Numbered sections in monotonic order (1..18).
- **V3** No execution language.
- **V4** No self-authorization (this DRAFT does NOT authorize SEAL; only a separate operator turn does that).
- **V5** No code modification.
- **V6** No backtest run.
- **V7** No simulator run.
- **V8** No signal computation (no RSI computation).
- **V9** No data fetch.
- **V10** No network IO.
- **V11** No live trading.
- **V12** No prior-phase artifact modification (T1 PLAN / s11-d1 / s12-d1 / parallel s13-d1 / s10-d2 / s10-d1 / s9 / s7-d1 / s8-d1 / B006_NNN / T8 byte-stable).
- **V13** The committed DRAFT file is the ONLY new file in this turn's commit.
- **V14** The brain_memory dirty `lessons.md` remains UNSTAGED and UNTOUCHED.
- **V15** Mechanic family + RSI period 2 + bi-directional + universe LOCKED at PLAN; DRAFT does NOT reopen these.
- **V16** Single-instrument adaptations explicit (A7/K10/K6 NOT APPLICABLE; DR11 structurally absent).
- **V17** DA register includes only the parameters NOT locked at PLAN.
- **V18** K9-reachability analysis carried byte-equivalent from PLAN.
- **V19** Forbidden-tracks list inherited from `0e3f9d49` (T-FORBID-1 through T-FORBID-8).

## 16. HALT conditions + DRAFT ambiguity register

HALT conditions:

- **H1** If any V-gate fails, the turn HALTs.
- **H2** If pre-stage git index is non-empty, the turn HALTs.
- **H3** If staged file count is anything other than 1 at commit time, the turn HALTs.
- **H4** If staged file is anything other than `docs/t1_rsi_mnq_tier_n_spec_DRAFT.md`, the turn HALTs.
- **H5** If `lessons.md` is accidentally staged, the turn HALTs and `git restore --staged brain_memory/projects/trading_bot/lessons.md` before retrying.
- **H6** If any T1 PLAN / s11-d1 / s12-d1 / parallel s13-d1 sealed artifact is detected as modified, the turn HALTs.

### 16.1 DRAFT ambiguity register (for operator confirmation at SEAL; operator types option letter)

Note: RSI period, mechanic family, signal direction, universe, and IS/OOS windows are LOCKED at PLAN and are intentionally NOT in this register. The DA register covers ONLY parameters deferred from PLAN to DRAFT/SEAL.

- **DA1** RSI period P (CONFIRMING PLAN LOCK; not reopenable): A `2` (default; Connors canonical; LOCKED at PLAN) — **this DA exists for sanity-recapture only; operator confirms by typing `DA1=A`**
- **DA2** RSI oversold entry threshold: A `10` (default; Connors canonical) / B `5` (more selective; fewer entries) / C `15` (more permissive; more entries) / D `20` (very permissive)
- **DA3** RSI overbought entry threshold: A `90` (default; mirror of DA2=A) / B `95` (more selective) / C `85` (more permissive) / D `80` (very permissive). **Operator may revise DA2 + DA3 jointly to maintain symmetry.**
- **DA4** RSI exit centerline: A `50` (default; symmetric mean-reversion target) / B `55` (slight asymmetric upward bias) / C `60` (asymmetric upward bias)
- **DA5** Exit-by-time max bars (failsafe; closes position if RSI never recrosses centerline within window): A `5` (default; Connors short-term mean-reversion) / B `3` (tighter) / C `7` (looser) / D `10` (very loose) / E `DISABLE` (no time-based exit; pure RSI-recross)
- **DA6** ATR stop window P (per-trade volatility stop): A `20` (default; carried byte-equivalent from s12-d1 Wilder ATR(20)) / B `14` (Wilder canonical alternative) / C `10` (faster stop)
- **DA7** ATR stop multiplier K: A `2.0` (default; carried byte-equivalent from s12-d1 "2N stop") / B `1.5` (tighter; appropriate for mean-reversion which typically exits before full ATR expansion) / C `2.5` (looser) / D `DISABLE` (no ATR stop; pure RSI/time-based exit)
- **DA8** Per-trade risk percentage: A `1.0%` of portfolio equity (default; carried byte-equivalent from s12-d1) / B `0.5%` (more conservative; **flagged for DR10 mitigation** under RSI(2) cost density; **parallel s13-d1 chose B**) / C `2.0%` (more aggressive; flagged for K4 risk)
- **DA9** `START_CASH_USD`: A `100000` (default; carried byte-equivalent from s12-d1 DA4=B) / B `200000` (**flagged for DR10 mitigation** under RSI(2) turnover density; **parallel s13-d1 chose this kind of revision**) / C `50000` (more aggressive; flagged for DR10 elevated risk) / D `500000` (large scale; for cross-reference vs s10-D2)
- **DA10** K4 max-drawdown threshold: A `0.50` (50% of `START_CASH_USD`; carried byte-equivalent from s12-d1 K4 formula) / B `0.30` (more conservative; s7-D1 / B006 lineage) / C `0.40` (intermediate)
- **DA11** Output schema name: A `sparta.t1.rsi_mnq_c0.mean_reversion_2.diagnostic_run_report.v1` (default) — LOCKED at SEAL
- **DA12** Cost-stress tier set: A 5-tier `S0/S1/S2/S3/S4` with scalars `0.0 / 1.0 / 1.5 / 2.0 / 3.0` (default; carried byte-equivalent) — LOCKED at SEAL non-negotiable per `no_dr_redefinition_post_seal`
- **DA13** Commission per round-trip: A `$0.74` (default; carried byte-equivalent from s12-d1) — LOCKED at SEAL
- **DA14** Fees per round-trip: A `$0.36` (default; carried byte-equivalent from s12-d1) — LOCKED at SEAL
- **DA15** Slippage entry/stop/exit ticks: A `1 / 1 / 1` (default; carried byte-equivalent from s12-d1) — LOCKED at SEAL
- **DA16** `WARMUP_DAYS`: A `220` (default; framework-consistent carrying from s11-d1/s12-d1 lineage; RSI(2) only needs ~5 bars but 220 carried for cross-candidate consistency) / B `30` (RSI(2)-appropriate minimum; would shorten warmup BUT breaks consistency with s11-d1/s12-d1 lineage) — operator decides at SEAL
- **DA17** RTH window: A `09:30-16:00 ET America/New_York` (default; carried byte-equivalent) — LOCKED at SEAL
- **DA18** DR9 thresholds (carried byte-equivalent from s10-D1 / s11-d1 / s12-d1 sealed chain): A `0.95 / 0.30 / 5 / 5` — LOCKED at SEAL non-negotiable per `no_dr_redefinition_post_seal`
- **DA19** DR10 thresholds: A `annual_turnover_threshold = 0.50` AND `s2_cost_drag_threshold = 0.05` (carried byte-equivalent) / B `annual_turnover_threshold = 1.00` AND `s2_cost_drag_threshold = 0.10` (more permissive; **MAY be required for RSI(2) due to elevated turnover**; flagged for operator review at SEAL)
- **DA20** OOS K9 sub-threshold disposition: A `DR1 INCONCLUSIVE_HOLD` (default; carry C1.D lineage from s12-d1 SEAL) — LOCKED at SEAL non-negotiable

The operator confirms DA1–DA20 at the SEAL turn by typing an explicit revision authorization (e.g., *"Authorize T1 RSI MNQ Tier-N spec SEAL. Confirm all DRAFT ambiguities as default A."*) or revises the genuinely-negotiable items (DA2–DA10, DA16, DA19 — since DA1/DA11/DA12/DA13/DA14/DA15/DA17/DA18/DA20 are framework-locked or PLAN-confirmed) with explicit per-item revisions.

### 16.2 Mitigation note for DR10 risk (informational; no parameter change authorized at DRAFT)

The PLAN §5 flagged that RSI(2) trades 5–6× as often as Donchian-15/8; per-trade dollar move smaller; dollar-turnover ~30–40× higher. The DRAFT-level mitigation levers (NOT a DR-threshold change beyond DA19, which is offered as a SEAL revision option) are:

- **DA8=B** (per-trade risk 0.5% instead of 1.0%): halves contracts-per-trade for given ATR → halves dollar-turnover per trade. Parallel `s13-d1` chose this.
- **DA9=B** (START_CASH $200k instead of $100k): doubles contracts-per-trade for given ATR but spreads risk across larger base → reduces *per-dollar-of-equity* turnover. Parallel `s13-d1` chose this kind of revision.
- **DA19=B** (DR10 turnover threshold 1.00 instead of 0.50): explicitly accommodates RSI(2)'s higher turnover at the rule level, with the trade-off that DR10 risk is recalibrated rather than mitigated by sizing.

Operator decides at SEAL. Default DA8=A + DA9=A + DA19=A keeps the candidate closest to s12-d1 structural baseline; recommended-for-DR10-mitigation alternative is DA8=B + DA9=B + DA19=A.

## 17. K9-reachability analysis (carried byte-equivalent from PLAN)

The K9-reachability analysis from PLAN is restated for DRAFT visibility:

| Window | Length (y) | Required trades/y for K9 = 100 |
|---|---:|---|
| IS | 4.6 | ≥ 21.74 |
| **OOS** | **2.0** | **≥ 50.00** (BINDING) |

T1 expected RSI(2) bi-directional MNQ.c.0:
- Lower: 46 trades/y → 92 OOS trades < 100 → **fires OOS K9**
- Central: 57/y → 114 OOS trades → clears
- Upper: 68/y → 136 OOS trades → clears with margin

**K9 status at SEAL: BORDERLINE_TO_CLEARING.** OOS K9 fires at lower-bound estimate (ratio 0.92). Central/upper clear. Per C1.D / DA20: OOS K9 sub-threshold maps to DR1 `INCONCLUSIVE_HOLD` (not REJECT_FAST).

## 18. Next authorization language

A future operator authorization is required to proceed beyond this DRAFT. That authorization shall reference this DRAFT by exact path:

`docs/t1_rsi_mnq_tier_n_spec_DRAFT.md`

The next operator authorization in the established controller-session pattern shall use one of these scopes:

- **"Authorize T1 RSI MNQ Tier-N spec SEAL. Confirm all DRAFT ambiguities as default A."** — begin the SEAL flow with DRAFT defaults accepted (RSI period 2 LOCKED from PLAN; oversold 10; overbought 90; centerline 50; exit-by-time 5 bars; ATR-20 K=2.0; bi-directional; 1.0% risk; no pyramid; K4 50%; K9 100; START_CASH $100k; WARMUP 220; RTH 09:30-16:00 ET; DR9 thresholds carried; DR10 thresholds carried; 5-tier cost stress; OOS K9 → DR1 INCONCLUSIVE_HOLD).
- **"Authorize T1 RSI MNQ Tier-N spec SEAL with revisions: DA8=B; DA9=B; all others as default A."** — DR10-mitigation recommended-revision SEAL: 0.5% risk + $200k cash (matches parallel `s13-d1`'s revisions; address RSI(2) turnover cost density).
- **"Authorize T1 RSI MNQ Tier-N spec SEAL with revisions: DA<X>=<L>, ...; all others as default A."** — begin the SEAL flow with arbitrary per-item revisions on the genuinely-negotiable DA2–DA10, DA16, DA19 register.
- **"Authorize alternative track selection plan revision only"** — if the operator rejects the T1 candidate entirely and wants a fresh selection-plan revision.
- **"Authorize cross-domain pivot only"** — if the operator pivots to a different project entirely.
- **"Defer / Pause T1 track"** — if the operator holds the DRAFT on file without advancing.

This DRAFT is the source of truth for the T1 MNQ.c.0 single-instrument RSI(2) bi-directional candidate's intended Tier-N spec scope at DRAFT time. Future SEAL / BUILD / RUN phases that contradict this DRAFT require either a fresh DRAFT revision or an out-of-band justification.

No phase of this chain confers any standing authorization for live trading, brokerage connection, Strategy Lab promotion, OOS inspection, or production candidate registration. Each remains BLOCKED at separate phases. Trading remains `PAUSED`. Live remains `BLOCKED_AT_6_GATES`. FRC `NEVER_GRANTED`.

----

End of DRAFT. Plan/spec DRAFT only. No code. No backtest. No simulator. No signal. No RSI computation. No data fetch. No yfinance. No Yahoo Finance. No Databento. No `DATABENTO_API_KEY` access. No QC. No LEAN. No brokerage. No real order. No paper order. No Strategy Lab promotion. No `review_queue` mutation. No production `idea_memory` mutation. No ORB branch mutation. No `lessons.md` modification or staging. No live trading. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES.
