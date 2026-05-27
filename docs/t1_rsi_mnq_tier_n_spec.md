# T1 RSI MNQ.c.0 Bi-Directional Mean-Reversion — Tier-N Specification (SEALED)

**Status:** SEALED.
**Schema:** `sparta.t1.rsi_mnq_c0.mean_reversion_2.tier_n_spec.v1`
**Phase:** `T1_RSI_MNQ_TIER_N_SPEC_SEALED`
**Phase prefix:** `PHASE2-T1-RSI-MNQ-SEAL`
**Controller session:** THIS_SESSION_ONLY
**Sealed at (UTC):** `2026-05-27T17:55:00Z`

**Authorization:** *"Authorize T1 RSI MNQ Tier-N spec SEAL with revisions: DA8=B; DA9=B; all others as default A."*

**Source PLAN:** `docs/t1_rsi_mnq_tier_n_spec_plan.md` @ commit `729207f` (seal `70549a9ac2c15f361a4cb7319b1bde2e963cbbfe8aa4e4757eebedbd77eeca4d`; bit-identical at HEAD)

**Source DRAFT:** `docs/t1_rsi_mnq_tier_n_spec_DRAFT.md` @ commit `fb1079a` (bit-identical at HEAD)

**HARD BOUNDARIES** (held by this SEAL). Spec SEAL only. No strategy code. No backtest. No simulator. No signal computation. No RSI computation. No data fetch. No yfinance / Yahoo Finance call. No Databento call. No `DATABENTO_API_KEY` access. No QC / LEAN call. No network IO. No `review_queue.json` mutation. No production `idea_memory` mutation. No Strategy Lab run. No candidate promotion. No T1 PLAN / T1 DRAFT / s11-d1 / s12-d1 / parallel s13-d1 / s10-d2 / s10-d1 / s9 / s7-d1 / s8-d1 / B005_NNN / B006_NNN / T8 / NKE / ORB sealed-artifact modification. No Step 30 cost constant mutation. No CLAUDE.md modification. No docs/decisions.md modification. No RUNBOOK modification. No pipeline_manifest modification. No .gitignore modification. **No `brain_memory/projects/trading_bot/lessons.md` modification or staging.** No branch change. No branch creation. No git push. No live trading. No profitability claim. No live-readiness claim. **Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES. FRC NEVER GRANTED. Advisory label permanent: DIAGNOSTIC_ONLY_NOT_LIVE_GRADE. `verdict_never_means_live_ready: True`.**

---

## 0. SEAL summary — DA-register resolution

| DA | Field | Selection | Value at SEAL | Note |
|---|---|---|---|---|
| DA1 | RSI period P | (PLAN-LOCK) | **`2`** | Connors canonical; LOCKED at PLAN |
| DA2 | RSI oversold entry threshold | **A** | `10` | DRAFT default |
| DA3 | RSI overbought entry threshold | **A** | `90` | DRAFT default (mirror of DA2) |
| DA4 | RSI exit centerline | **A** | `50` | Symmetric mean-reversion target |
| DA5 | Exit-by-time max bars | **A** | `5` | Connors short-term mean-reversion |
| DA6 | ATR window P | **A** | Wilder `20` | Carried byte-equivalent from s12-d1 |
| DA7 | ATR stop multiplier K | **A** | `2.0` (2N stop) | Carried byte-equivalent |
| **DA8** | **Per-trade risk %** | **B** | **`0.5%`** | **OPERATOR-REVISED at SEAL** (DR10 mitigation; halves contracts-per-trade vs s12-d1 baseline) |
| **DA9** | **`START_CASH_USD`** | **B** | **`$200,000`** | **OPERATOR-REVISED at SEAL** (DR10 mitigation; doubles base capital vs s12-d1; reduces per-dollar turnover pressure) |
| DA10 | K4 max-drawdown threshold | **A** | `0.50` (50% × $200k = **$100,000 absolute**) | Note absolute K4 threshold doubled vs s12-d1 due to DA9=B |
| DA11 | Output schema name | **A** | `sparta.t1.rsi_mnq_c0.mean_reversion_2.diagnostic_run_report.v1` | Framework-locked |
| DA12 | Cost-stress tier set | **A** | 5-tier `S0/S1/S2/S3/S4` (`0.0/1.0/1.5/2.0/3.0`) | Framework-locked |
| DA13 | Commission per round-trip | **A** | `$0.74` | Framework-locked |
| DA14 | Fees per round-trip | **A** | `$0.36` | Framework-locked |
| DA15 | Slippage entry/stop/exit ticks | **A** | `1 / 1 / 1` | Framework-locked |
| DA16 | `WARMUP_DAYS` | **A** | `220` | Framework-consistent with s11-d1/s12-d1 lineage |
| DA17 | RTH window | **A** | `09:30-16:00 ET America/New_York` | Framework-locked |
| DA18 | DR9 thresholds | **A** | `0.95 / 0.30 / 5 / 5` | Framework-locked |
| DA19 | DR10 thresholds | **A** | `annual_turnover ≤ 0.50` AND `s2_cost_drag ≤ 0.05` | Default kept (NOT recalibrated; trade-off vs DA8+DA9 mitigation accepted) |
| DA20 | OOS K9 sub-threshold disposition | **A** | `DR1 INCONCLUSIVE_HOLD` (NOT REJECT_FAST) | Locked per C1.D lineage |

**Revisions vs DRAFT defaults:** DA8 (A→B) + DA9 (A→B); all other DAs default A.

**Rationale (per operator authorization):** DA8=B + DA9=B is the recommended DR10-mitigation revision identified in DRAFT §16.2. Halves per-dollar turnover risk by reducing contracts-per-trade (0.5% risk) and increasing base capital ($200k). Matches parallel session's `s13-d1` SEAL choice direction.

---

## 1. Candidate identification (LOCKED at PLAN; carried byte-equivalent through DRAFT/SEAL)

| Field | LOCKED value |
|---|---|
| `candidate_record_id` | `t1-rsi-mnq-c0-mean-reversion-2-period-databento-long-history` |
| Track family | T-series higher-frequency mean-reversion |
| Successor to | S12-D1 (PARKED_SAFE_BUT_INSUFFICIENT_SAMPLE_AT_IS) |
| Algo version | `t1_v0_1_0` |

---

## 2. Mechanic family + RSI parameters (LOCKED at PLAN; SEAL does NOT reopen)

| Field | LOCKED value |
|---|---|
| Mechanic family | **F3** — Long+Short Bi-Directional RSI Mean-Reversion, No Pyramid, ATR(20) 2N Stop, Single MNQ.c.0 Contract Per Signal |
| RSI period | **2** (Connors canonical) |
| Signal direction | Long + Short bi-directional |
| Long entry trigger | RSI(2) < `10` (DA2=A) |
| Long exit trigger | RSI(2) > `50` (DA4=A) |
| Short entry trigger | RSI(2) > `90` (DA3=A) |
| Short exit trigger | RSI(2) < `50` (DA4=A) |
| Exit-by-time failsafe | `5` bars (DA5=A) |
| Pyramid mechanism | NONE / `max_units_per_market = 1` |

---

## 3. Universe (SEALED; non-reopenable)

| Field | LOCKED value |
|---|---|
| Universe type | `single_fixed_instrument_continuous_micro_futures` |
| Symbol 1 (only symbol) | `MNQ.c.0` |
| Symbol count | exactly 1 |
| `AddUniverse` calls | 0 |
| `removed_from_universe` events | 0 |
| Symbol substitution post-seal | FORBIDDEN |
| Universe widening post-seal | FORBIDDEN (any wider basket requires a fresh `candidate_record_id`) |
| Common-history start | 2019-05-13 |
| Diversification claim | NONE |

---

## 4. Dataset (SEALED)

| Field | LOCKED value |
|---|---|
| Vendor | Databento Historical API (vendor-level; controller never calls at runtime) |
| Dataset | `GLBX.MDP3` |
| Schema | `ohlcv-1d` |
| `stype_in` | `continuous` |
| Symbol requested | `["MNQ.c.0"]` |
| Re-use of existing audit-clean CSV | **TRUE** — `data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_1d_2019-05-13_2025-12-30.csv` (sha256 `8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e`; 2,066 rows; 2019-05-13 → 2025-12-29) reused byte-equivalent. **ZERO new Databento call required.** |
| API key handling | NOT REQUIRED at any phase |
| Controller-side Databento call | LOCKED OFF at every phase |

---

## 5. IS / OOS windows (SEALED)

| Field | LOCKED value |
|---|---|
| IS window start | `2019-05-13` |
| IS window end | `2023-12-29` |
| IS window length | ~4.6 years (~1,140 trading days; 1,443 audit-confirmed rows) |
| OOS window start (never inspected at IS) | `2024-01-02` |
| OOS window end (never inspected at IS) | `2025-12-30` |
| OOS window length | ~2 years (622 structural-only rows) |
| Post-OOS data | `2026-01-02 onward` (informational only; locked-out from OOS scope) |
| OOS inspection at IS-phase | FORBIDDEN (`oos_inspection_blocked_at_in_sample`) |

---

## 6. Cost-stress matrix (SEALED; from day 1)

| Tier | `cost_scalar` | `slippage_scalar` | Note |
|---|---:|---:|---|
| S0 | 0.0 | 0.0 | zero-cost ideal |
| S1 | 1.0 | 1.0 | baseline retail |
| S2 | 1.5 | 1.5 | stressed retail |
| S3 | 2.0 | 2.0 | adversarial |
| S4 | 3.0 | 3.0 | extreme adversarial |

| Field | LOCKED value |
|---|---|
| Tick size (MNQ.c.0) | 0.25 index points |
| Dollar per tick (MNQ.c.0) | $0.50 |
| Commission per round-trip | $0.74 (DA13=A) |
| Fees per round-trip | $0.36 (DA14=A) |
| Slippage entry/stop/exit ticks | 1/1/1 (DA15=A) |
| Pre-registered K12 composite | DR2 + DR3 (S2/S3/S4 degrade >50% or sign flip) — **ELEVATED prior probability** under RSI(2) mean-reversion |
| Pre-registered S0 edge acceptance | `> 0` after ≥ 100 trades |
| Pre-registered S1 acceptance | `> 0` (K1/K2 fire if `≤ 0`) |

---

## 7. Sizing + execution (SEALED; DA8 + DA9 revised)

| Field | LOCKED value |
|---|---|
| **`START_CASH_USD`** | **`$200,000`** (DA9=B; operator-revised at SEAL) |
| **Per-trade risk fraction** | **`0.5%`** of portfolio equity (DA8=B; operator-revised at SEAL) |
| ATR stop window | Wilder ATR(20) (DA6=A) |
| ATR stop multiplier | `2.0` (2N stop) (DA7=A) |
| **K4 max-drawdown threshold (absolute)** | **`$100,000`** (50% × $200k START_CASH) (DA10=A applied to DA9=B) |
| Exit-by-time max bars | 5 (DA5=A) |
| WARMUP_DAYS | `220` (DA16=A) |
| RTH window | `09:30-16:00 ET America/New_York` (DA17=A) |
| `max_units_per_market` | `1` (no-pyramid invariant; structurally enforced) |

---

## 8. Sample-size / K9 rules (SEALED)

| Field | LOCKED value |
|---|---|
| K9 threshold (IS + OOS both apply) | `total_closed_trades ≥ 100` (LOCKED non-negotiable; `no_k9_relaxation`) |
| Expected IS trade count (RSI(2) bi-directional on MNQ.c.0 / 4.6y) | **210-313** (lower 210; central 262; upper 313) |
| Expected IS trades/year | 46-68 (5-6× s12-d1's ~7-10/y) |
| IS K9 expected outcome | **CLEARS WITH MARGIN** (lower-bound 46/y >> 21.74/y required) |
| Expected OOS trade count (proportional to 2.0y) | **92-136** |
| OOS K9 expected outcome | **BORDERLINE_TO_CLEARING** |
| OOS K9 status at lower-bound (46/y × 2y = 92) | **fires K9** (92 < 100; ratio 0.92) |
| OOS K9 status at central (57/y × 2y = 114) | **clears K9** (ratio 1.14) |
| OOS K9 status at upper (68/y × 2y = 136) | **clears K9 with margin** (ratio 1.36) |
| OOS K9 sub-threshold disposition (DA20=A) | **DR1 `INCONCLUSIVE_HOLD`** (NOT REJECT_FAST); candidate parks but IS evidence is preserved |
| K9 relaxation | FORBIDDEN (threshold 100 non-negotiable) |

---

## 9. Diversification (SEALED; trivially N/A)

| Field | LOCKED value |
|---|---|
| `A7_effective_independent_bets_min` | NOT APPLICABLE (trivially 1 by construction) |
| `K10_avg_pairwise_dependence_max` | NOT APPLICABLE (no pairs) |
| `K6_per_symbol_observed_win_rate_dispersion` | NOT APPLICABLE (no dispersion to measure) |
| Diversification claim by this candidate | NONE |
| Disclaimer | "Diversification independence does NOT imply positive edge" (LESSON_B006_002_002) applies trivially |

---

## 10. Data-availability / DR-gate rules (SEALED)

### 10.1 Assumptions

- `MNQ.c.0` over `2019-05-13 → 2025-12-30` is **DR9-clean** under both audit variants per s10-D1 audit (0 calendar gaps > 5 days; max single-day abs-log-return 0.1164).
- DR9 thresholds carried byte-equivalent (DA18=A: `0.95 / 0.30 / 5 / 5`).

### 10.2 DR rules (single-instrument F3 RSI(2) bi-directional)

| Rule | Trigger | Severity | F3-RSI(2) note |
|---|---|---|---|
| **DR1** | `oos_rebalance_count < 36` OR `oos_closed_trades < K9_threshold` (OOS phase) | `INCONCLUSIVE_HOLD` | **Extended at SEAL per DA20=A / C1.D lineage** to cover OOS K9 sub-threshold |
| DR2 | `oos_metrics_degrade_materially_under_cost_stress` | `REJECT_FAST` | **ELEVATED prior probability** under mean-reversion |
| DR3 | `zero_cost_only_survival` (S0 > 0 AND all S1..S4 ≤ 0) | `REJECT_FAST` | **ELEVATED prior probability** under mean-reversion |
| DR4 | `oos_negative_while_is_positive_unexplained` | `REJECT_FAST` | OOS-only |
| DR5 | `cost_stress_turns_edge_negative` (tier flip) | `REJECT_FAST` / carveout | **ELEVATED prior probability** under mean-reversion |
| DR6 | `post_warmup_sizing_ambiguity_or_invalid` | `REJECT_FAST` | unchanged |
| DR7 | `missing_oos_or_date_window_evidence` | `INCONCLUSIVE_HOLD` | unchanged |
| DR8 | `live_or_order_routing_path_detected` at Initialize | `HARD_FAIL_VOIDED` | unchanged |
| DR9 | `mnq_c0_only_data_continuity_integrity_check` (0.95 / 0.30 / 5 / 5) | `INCONCLUSIVE_HOLD` | MNQ-only |
| **DR10** | `turnover_cost_explosion` (`annual_turnover > 0.50` OR `S2 cost drag > 0.05`) (DA19=A) | `REJECT_FAST` | **ELEVATED prior probability**; **partially mitigated by DA8=B + DA9=B** but threshold itself unchanged at framework default. The mitigation lever is sizing-based (halve contracts-per-trade) + capital-based (double base capital), not threshold-based. |
| DR11 | NOT IN CHAIN | — | F3 has no leverage cap |

DR precedence chain (LOCKED): `DR7 → DR1 → DR9 → DR10 → DR6 → DR4 → DR2 → DR3 → DR5`.

---

## 11. K-gates + A-gates (SEALED)

K-gates (carried byte-equivalent from s12-d1 with F3-RSI(2) adaptations):

| Gate | Trigger | Notes |
|---|---|---|
| K1 | `sharpe_proxy_per_trade < 0` at S1 | — |
| K2 | `expectancy_per_trade_usd ≤ 0` at S1 | — |
| K4 | `trade_curve_max_drawdown_abs > 50% × START_CASH` | K4 = **$100,000** (50% × $200k) |
| K6 | NOT APPLICABLE (single-instrument) | — |
| K7 | `silent_filter_introduction_after_lock` | — |
| K8 | `runtime_safety_invariant_false` | — |
| K9 | `closed_trades < 100` | IS + OOS both; **OOS K9 sub-threshold → DR1 INCONCLUSIVE_HOLD per DA20=A** |
| K10 | NOT APPLICABLE (single-instrument) | — |
| K11 | NOT APPLICABLE (no leverage cap for F3) | — |
| K12 | composite cost-stress fail (DR2 + DR3) | **ELEVATED prior probability under mean-reversion** |

K-gate firing priority order: `K8 > K12 > K7 > K9 > K1/K2/K4 > A-gates > ELIGIBLE_FOR_OOS`.

---

## 12. OOS locking policy (SEALED)

| Policy | Status |
|---|---|
| OOS data shall not be inspected, computed against, simulated over, or queried during IS phase | LOCKED |
| Post-OOS data is informational only | LOCKED |
| OOS inspection requires separately authorized turn after IS verdict `ELIGIBLE_FOR_OOS` + explicit operator approval | LOCKED |
| Modules shall structurally enforce IS-only computation (sibling driver design) | LOCKED (`oos_inspection_blocked_at_in_sample`) |
| OOS confirmation definition | LOCKED (s11-d1 rev2 magnitude-based form, byte-equivalent) |

**OOS CONFIRMED only iff ALL of:**
1. C7 verdict is `READY_FOR_LONGER_BACKTEST`
2. OOS closed_trades ≥ 100
3. OOS sharpe > 0
4. OOS expectancy > 0
5. OOS `trade_curve_maxdd_pct ≥ -30%` (i.e., `|maxdd| ≤ 30%`)
6. all safety counters zero
7. no-pyramid invariant held
8. starting_cash invariant held

---

## 13. No-live / no-Strategy-Lab / no-brokerage invariants (SEALED; 25 total)

**7 inherited B005_NNN framework:**
`no_live_trading` · `no_strategy_lab_promotion` · `no_review_queue_mutation` · `no_brokerage_connection` · `no_external_network` · `no_databento_at_runtime` · `no_production_signal`

**4 inherited B006_001:**
`no_strategy_optimization_authorized` · `no_profitability_claim` · `no_universe_membership_logic` · `no_dr_redefinition_post_seal`

**2 inherited B006_002:**
`no_warmup_order_submission` · `dr6_warmup_contamination_blocked`

**5 inherited s10-D1-specific:**
`no_continuous_roll_stitch_modification_post_seal` · `no_mcl_inclusion_under_long_history_scope` · `no_intraday_schema_ingest_under_daily_only_design` · `databento_api_key_read_from_env_only_never_logged_or_saved` · `no_pyramid_per_signal`

**3 inherited s11-d1-specific:**
`single_instrument_universe_NO_widening_post_seal` · `no_substitution_of_any_symbol_into_this_universe_post_seal` · `mnq_c0_csv_reuse_byte_equivalent_no_fresh_fetch`

**4 new T1-specific:**
`rsi_period_2_locked_at_plan_no_retreat_to_3_4_or_other` · `mean_reversion_centerline_50_locked_at_plan_no_drift_to_55_60` · `bi_directional_locked_at_plan_no_retreat_to_long_only` · `mechanic_family_f3_lock_at_plan_no_reopening_at_draft_or_seal`

---

## 14. Reject-fast criteria (SEALED)

The candidate is REJECTED FAST if ANY of:

- **RF1** Any DR rule fires `REJECT_FAST` (DR2 / DR3 / DR4 / DR5 / DR6 / DR10)
- **RF2** DR9 `mnq_c0_only_data_continuity_integrity_failure` AND > 5 violations
- **RF3** DR6 post-warmup invalid-sizing event count > 0
- **RF4** Any forbidden-verdict-token in runner output
- **RF5** Runner attempts `SetLiveMode` / `SetBrokerageModel` / `DeployAlgorithm` / unauthorized network call / unauthorized Databento call at runtime
- **RF6** Any order-submit attempt while in warmup window
- **RF7** Runner mutates any sealed predecessor artifact (byte-shift)
- **RF8** Runner makes a Databento API call at any phase
- **RF9** Runner caches `.dbn.zst` files anywhere
- **RF10** Runner accesses `DATABENTO_API_KEY` at any phase
- **RF11** Track silently re-introduces a filter, regime gate, or selection rule
- **RF12** Pyramid mechanism re-introduced in code
- **RF13** RSI period silently switched from the LOCKED 2 post-SEAL
- **RF14** Mean-reversion centerline silently switched from the LOCKED 50 post-SEAL
- **RF15** Universe widening or symbol substitution attempted at any phase
- **RF16** Track depends on a survivorship-cherry-pick rule
- **RF17** Any retroactive re-anchoring or modification of T1 PLAN / T1 DRAFT / s11-d1 / s12-d1

**Note (DA20=A):** OOS K9 sub-threshold is NOT a REJECT_FAST condition; it maps to DR1 `INCONCLUSIVE_HOLD`.

---

## 15. Validation gates (this SEAL turn)

- **V1** ASCII-only
- **V2** Numbered sections in monotonic order
- **V3** No execution language
- **V4** No self-authorization to BUILD or RUN
- **V5** No code modification
- **V6** No backtest run
- **V7** No simulator run
- **V8** No signal computation (no RSI computation)
- **V9** No data fetch
- **V10** No network IO
- **V11** No live trading
- **V12** PLAN (`729207f`) + DRAFT (`fb1079a`) byte-stable at HEAD
- **V13** Exactly 3 new files staged: this `docs/` spec + 2 `reports/external_research_hunter/` sealed pair
- **V14** `lessons.md` unstaged and untouched
- **V15** DA8=B + DA9=B applied; DA19=A; all other DAs at default A
- **V16** PLAN-locked decisions (mechanic family F3, RSI period 2, bi-directional, universe MNQ.c.0, IS/OOS windows) NOT reopened at SEAL
- **V17** K9-reachability analysis carried byte-equivalent into SEAL
- **V18** RSI(2) cost-sensitivity disclosure (DR10 elevated prior; mitigation via DA8+DA9) explicit at SEAL

---

## 16. Predecessor anchors (byte-stable)

| Anchor | Seal / sha (first 16) |
|---|---|
| Source PLAN | `70549a9ac2c15f36` |
| Source DRAFT (`docs/.../t1_..._DRAFT.md`) | (computed at SEAL-time; see JSON) |
| s12-d1 P11 PARK memo (this session) | `321b8940a5516762` |
| s12-d1 sealed Tier-N spec (this session) | `422bbbff75f24816` |
| s12-d1 P11 PARK memo (parallel canonical) | `b9722d424f6faabe` |
| s10-D2 lifecycle park report (this session) | `8d59e94a736aa82d` |
| s11-d1 v1 spec | `077e29e62f23dbc3` |
| s11-d1 rev2 | `46659b4a8a73cb72` |
| Audit-clean MNQ.c.0 CSV | `8b7b832c62fae185` |

---

## 17. Posture (permanent for this candidate)

| Field | Value |
|---|---|
| Trading | `PAUSED` |
| Live mode | `BLOCKED_AT_6_GATES` |
| FRC | `NEVER_GRANTED` |
| Advisory label | `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` (permanent) |
| `verdict_never_means_live_ready` | `True` |
| `live_promotion_path_closed` | `True` |
| Six live-trading gates BLOCKED regardless of verdict | `Yes` |

---

## 18. Next authorization language

A future operator authorization is required to advance beyond this SEAL. Reference this SEAL by exact path: `docs/t1_rsi_mnq_tier_n_spec.md`.

Natural next scopes (each requires its own fresh sealed authorization; NONE is pre-approved by this SEAL):

- *"Authorize T1 P1 plan-lock spec only"*
- *"Authorize T1 P2 phase-2 plan only"*
- *"Authorize T1 P3 BUILD only"*
- *"Defer / Pause T1 track"*

---

**T1 RSI MNQ Tier-N spec SEALED. DA8=B (0.5% per-trade risk) + DA9=B ($200,000 START_CASH) applied; DA19=A (DR10 thresholds at default); all other DAs at default A. K9-reachability: IS clears with margin; OOS BORDERLINE_TO_CLEARING (lower-bound fires; central/upper clear). DR10 mitigation via DA8+DA9 sizing levers; DR2/DR3/DR5/K12 ELEVATED prior probability acknowledged. Trading: PAUSED. Live: BLOCKED_AT_6_GATES. FRC never granted.**
