# S12-D1 MNQ.c.0 Single-Instrument Donchian-15/8 — Tier-N Specification (SEALED)

**Status:** SEALED.
**Schema:** `sparta.s12.d1.mnq_c0.donchian_15_8.tier_n_spec.v1`
**Phase:** `S12_D1_TIER_N_SPEC_SEALED`
**Phase prefix:** `PHASE2-S12-D1-SEAL`
**Controller session:** THIS_SESSION_ONLY
**Sealed at (UTC):** `2026-05-27T14:50:00Z`

**Authorization:** *"Authorize s12 D1 MNQ.c.0 Tier-N spec SEAL with revisions: DA4=B; all others as default A. At SEAL also affirm C1.A + C1.D from review."*

**Source DRAFT:** `docs/s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_tier_n_spec_DRAFT.md` @ commit `7e9c86799e5d9b0cecfb34a0de16bdda4eaf9b71` (sha256 `9f09ec94028659ebe45b8fb5c8d22cd9fc5397022f5b1f865d8c780d1ed08578`; bit-identical at HEAD)

**Source review:** `reports/s12_d1_fresh_candidate_tier_n_draft_review.{json,md}` @ commit `07be7fc5561c51f1af09b82b6e593e9c24ba08cd` (verdict: `DRAFT_REVIEW_PASS_WITH_CLARIFICATIONS`; seal `860e766e6933751d97cd7821fff6911de133772aaec3ac778754d62e6889b8d8`)

**HARD BOUNDARIES** (held by this SEAL). Spec SEAL only. No strategy code. No backtest. No simulator. No signal computation. No data fetch. No yfinance / Yahoo Finance call. No Databento call. No DATABENTO_API_KEY access. No QC / LEAN call. No network IO. No review_queue.json mutation. No production idea_memory mutation. No Strategy Lab run. No candidate promotion. No s7 / s8-D1 / s9 / s10-D1 / s10-D2 / s11-d1 / B005 / B006 / T8 sealed-artifact modification. No ORB branch artifact mutation. No Step 30 cost constant mutation. No CLAUDE.md modification. No docs/decisions.md modification. No RUNBOOK modification. No pipeline_manifest modification. No .gitignore modification. No `brain_memory/projects/trading_bot/lessons.md` modification or staging. No branch change. No branch creation. No git push. No live trading. No profitability claim. **Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES. FRC NEVER GRANTED. Advisory label permanent: DIAGNOSTIC_ONLY_NOT_LIVE_GRADE. `verdict_never_means_live_ready: True`.**

---

## 0. SEAL summary (operator-selected values vs DRAFT defaults)

| DA | Field | Selection | Value at SEAL | Notes |
|---|---|---|---|---|
| DA1 | ATR stop window P | **A** | `Wilder ATR(20)` | DRAFT default; carried byte-equivalent from s11-d1 v1 |
| DA2 | ATR stop multiplier K | **A** | `2.0` (2N stop) | DRAFT default |
| DA3 | Per-trade risk % | **A** | `1.0%` of portfolio equity | DRAFT default |
| **DA4** | **START_CASH_USD** | **B** | **`$100,000`** | **Revised at SEAL per operator** (mitigates DR10 risk by halving contracts-per-trade for given ATR) |
| DA5 | K4 max-drawdown threshold | **A** | `0.50` (50% of START_CASH = $50,000 absolute) | DRAFT default; carried byte-equivalent from s11-d1 v1 K4 formula |
| DA6 | Output schema name | **A** | `sparta.s12.d1.mnq_c0.donchian_15_8.diagnostic_run_report.v1` | framework-locked |
| DA7 | Cost-stress tier set | **A** | 5-tier `S0/S1/S2/S3/S4` with scalars `0.0/1.0/1.5/2.0/3.0` | framework-locked |
| DA8 | Commission per round-trip | **A** | `$0.74` | framework-locked |
| DA9 | Fees per round-trip | **A** | `$0.36` | framework-locked |
| DA10 | Slippage entry/stop/exit ticks | **A** | `1/1/1` | framework-locked |
| DA11 | WARMUP_DAYS | **A** | `220` | framework-locked |
| DA12 | RTH window | **A** | `09:30-16:00 ET America/New_York` | framework-locked |
| DA13 | DR9 thresholds | **A** | `0.95 / 0.30 / 5 / 5` | framework-locked |
| DA14 | DR10 thresholds | **A** | `annual_turnover_threshold = 0.50` AND `s2_cost_drag_threshold = 0.05` | framework-locked |

### Review clarifications affirmed at SEAL

- **C1.A — Accept OOS K9 risk as part of structural test:** Pre-acknowledged. At expected IS trade densities (80-200 over 4.6y), proportional scaling to the 2.0y OOS window yields expected OOS trade counts of **35 / 61 / 87** at lower / central / upper IS bounds — **all below K9 = 100**. The candidate may park under `PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED` on OOS verdict. **This is the structural test of the fresh-candidate hypothesis, not a defect in the spec.** The IS evidence and cost-stress + universe-diversity findings remain valuable regardless of OOS K9 disposition.

- **C1.D — OOS K9 sub-threshold maps to DR1 INCONCLUSIVE_HOLD (not REJECT_FAST):** Affirmed. The OOS K9 sub-threshold case is governed by DR1 `oos_rebalance_count < 36` semantics (extended at SEAL to cover `oos_closed_trades < K9_threshold`). The verdict is `INCONCLUSIVE_HOLD`, not `REJECT_FAST`. The candidate is parked, not killed; IS evidence is preserved for future cross-reference.

- **C2 (informational; already applied):** DA4=B mitigation lever accepted to address elevated DR10 risk under Donchian-15/8.

---

## 1. Mechanic family + Donchian parameters (LOCKED at PLAN, sealed here)

| Field | LOCKED value |
|---|---|
| `candidate_record_id` | `s12-d1-mnq-c0-single-instrument-donchian-15-8-databento-long-history` |
| Mechanic family | F1 — Long+Short Bi-Directional Donchian Trend, No Pyramid, ATR(20)-Based Stop, Single MNQ.c.0 Contract Per Signal |
| Universe | `{MNQ.c.0}` only (single Micro E-mini Nasdaq-100 continuous front-month) |
| Donchian entry channel N | **15 days** |
| Donchian exit channel M | **8 days** |
| Signal direction | Long+Short bi-directional |
| Pyramid mechanism | NONE / `max_units_per_market = 1` |
| Schema | `ohlcv-1d` |
| `stype_in` | `continuous` |
| IS window | `2019-05-13 -> 2023-12-29` |
| OOS window | `2024-01-02 -> 2025-12-30` (never inspected at IS) |

---

## 2. Universe (SEALED; non-reopenable)

| Field | LOCKED value |
|---|---|
| Universe type | `single_fixed_instrument_continuous_micro_futures` |
| Symbol 1 (only symbol) | `MNQ.c.0` |
| `AddUniverse` calls | 0 |
| `removed_from_universe` events | 0 |
| Symbol count | exactly 1 |
| Symbol substitution post-seal | FORBIDDEN |
| Universe widening post-seal | FORBIDDEN (any wider basket requires a fresh `candidate_record_id`) |
| Common-history start | 2019-05-13 |
| Diversification claim | NONE |

---

## 3. Dataset (SEALED)

| Field | LOCKED value |
|---|---|
| Vendor | Databento Historical API (vendor-level; controller never calls at runtime) |
| Dataset | `GLBX.MDP3` |
| Schema | `ohlcv-1d` |
| `stype_in` | `continuous` |
| Symbol requested | `["MNQ.c.0"]` |
| Re-use of existing audit-clean CSV | **TRUE** — `data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_c_0_ohlcv_1d_20190513_20251230.csv` (sha256 `8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e`; 2,066 rows; 2019-05-13 → 2025-12-29) reused byte-equivalent. **ZERO new Databento call required.** |
| API key handling | NOT REQUIRED at any phase |
| Controller-side Databento call | LOCKED OFF at every phase |

---

## 4. IS / OOS windows (SEALED)

| Field | LOCKED value |
|---|---|
| IS window start | `2019-05-13` |
| IS window end | `2023-12-29` |
| IS window length | ~4.6 years (~1,140 trading days) |
| MNQ.c.0 IS row count (audit-confirmed) | 1,443 |
| OOS window start (never inspected at IS) | `2024-01-02` |
| OOS window end (never inspected at IS) | `2025-12-30` |
| OOS window length | ~2 years |
| MNQ.c.0 OOS row count (structural only) | 622 |
| Post-OOS data | `2026-01-02 onward` (informational only; locked-out from OOS scope by `oos_inspection_blocked_at_in_sample`) |
| OOS inspection at IS-phase | FORBIDDEN |

---

## 5. Cost-stress matrix (SEALED; from day 1)

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
| Commission per round-trip | $0.74 |
| Fees per round-trip | $0.36 |
| Slippage entry/stop/exit ticks | 1/1/1 |
| Pre-registered K12 composite | DR2 + DR3 (S2/S3/S4 degrade >50% or sign flip) |
| Pre-registered S0 edge acceptance | `> 0` after ≥ 100 trades |
| Pre-registered S1 acceptance | `> 0` (K1/K2 fire if `≤ 0`) |

---

## 6. Sizing + execution (SEALED; revised DA4)

| Field | LOCKED value |
|---|---|
| **`START_CASH_USD`** | **`$100,000`** (DA4=B; revised at SEAL) |
| Per-trade risk fraction | `1.0%` of portfolio equity (DA3=A) |
| ATR stop window | Wilder ATR(20) (DA1=A) |
| ATR stop multiplier | `2.0` (2N stop) (DA2=A) |
| K4 max-drawdown threshold (absolute) | `$50,000` (50% of $100k START_CASH) (DA5=A) |
| WARMUP_DAYS | `220` (DA11=A; MAX(longest_lookback, 220) = 220) |
| RTH window | `09:30-16:00 ET America/New_York` (DA12=A) |
| `max_units_per_market` | `1` (no-pyramid invariant; structurally enforced) |

---

## 7. Sample-size / K9 rules (SEALED)

| Field | LOCKED value |
|---|---|
| K9 threshold (IS + OOS both apply) | `total_closed_trades >= 100` |
| Expected IS trade count (Donchian-15/8 / MNQ.c.0 / 4.6y / bi-directional) | 80-200 (central ~140); 3-4× s11-d1 v1's ~25-50 |
| **Expected OOS trade count (proportional scaling)** | **35-87** (central ~61); **likely below K9 = 100** |
| IS K9 expected outcome | borderline-to-clearing (passes at central + upper estimate) |
| **OOS K9 expected outcome (C1.A acknowledged at SEAL)** | **may fire; structural test of fresh-candidate hypothesis** |
| **OOS K9 sub-threshold disposition (C1.D affirmed at SEAL)** | **DR1 `INCONCLUSIVE_HOLD`** (NOT `REJECT_FAST`); candidate parks but IS evidence is preserved |
| Per-symbol minimum | trivially equals portfolio minimum (single-instrument) |
| K9 relaxation | FORBIDDEN (`no_k9_relaxation` invariant; threshold is 100 non-negotiable) |

---

## 8. Diversification (SEALED; trivially N/A)

| Field | LOCKED value |
|---|---|
| `A7_effective_independent_bets_min` | NOT APPLICABLE (trivially 1; removed from acceptance gate set) |
| `K10_avg_pairwise_dependence_max` | NOT APPLICABLE (no pairs; removed from K-gate set) |
| `K6_per_symbol_observed_win_rate_dispersion` | NOT APPLICABLE (no dispersion to measure) |
| Diversification claim by this candidate | NONE |
| Disclaimer | "Diversification independence does NOT imply positive edge" (LESSON_B006_002_002) applies trivially |

---

## 9. Data-availability / DR-gate rules (SEALED)

### 9.1 Assumptions

- `MNQ.c.0` over `2019-05-13 → 2025-12-30` is **DR9-clean** under both audit variants (strict + holiday-aware) per s10-D1 audit (0 calendar gaps > 5 days; max single-day abs-log-return 0.1164).
- DR9 thresholds carried byte-equivalent.

### 9.2 DR rules (single-instrument F1 Donchian-15/8)

| Rule | Trigger | Severity | Note |
|---|---|---|---|
| **DR1** | `oos_rebalance_count < 36` OR `oos_closed_trades < K9_threshold` (OOS phase) | `INCONCLUSIVE_HOLD` | **Extended at SEAL per C1.D** to cover OOS K9 sub-threshold disposition |
| DR2 | `oos_metrics_degrade_materially_under_cost_stress` | `REJECT_FAST` | unchanged |
| DR3 | `zero_cost_only_survival` (S0 > 0 AND all S1..S4 ≤ 0) | `REJECT_FAST` | unchanged |
| DR4 | `oos_negative_while_is_positive_unexplained` | `REJECT_FAST` | OOS-only |
| DR5 | `cost_stress_turns_edge_negative` (tier flip) | `REJECT_FAST` / carveout | unchanged |
| DR6 | `post_warmup_sizing_ambiguity_or_invalid` | `REJECT_FAST` | unchanged |
| DR7 | `missing_oos_or_date_window_evidence` | `INCONCLUSIVE_HOLD` | unchanged |
| DR8 | `live_or_order_routing_path_detected` at Initialize | `HARD_FAIL_VOIDED` | unchanged |
| DR9 | `mnq_c0_only_data_continuity_integrity_check` (0.95 / 0.30 / 5 / 5) | `INCONCLUSIVE_HOLD` | MNQ-only |
| DR10 | `turnover_cost_explosion` (`annual_turnover > 0.50` OR `S2 cost drag > 0.05`) | `REJECT_FAST` | ELEVATED prior probability under Donchian-15/8; **DA4=B mitigation applied at SEAL** |
| DR11 | NOT IN CHAIN | — | F1 has no leverage cap; structurally absent |

DR precedence chain (LOCKED): `DR7 → DR1 → DR9 → DR10 → DR6 → DR4 → DR2 → DR3 → DR5`.

---

## 10. K-gates + A-gates (SEALED)

K-gates (carried byte-equivalent from s11-d1 v1 with single-instrument simplifications):

| Gate | Trigger | Notes |
|---|---|---|
| K1 | `sharpe_proxy_per_trade < 0` at S1 | — |
| K2 | `expectancy_per_trade_usd ≤ 0` at S1 | — |
| K4 | `trade_curve_max_drawdown_abs > 50% × START_CASH` | K4 = $50,000 (50% × $100k) |
| K6 | NOT APPLICABLE (single-instrument) | — |
| K7 | `silent_filter_introduction_after_lock` | — |
| K8 | `runtime_safety_invariant_false` | — |
| K9 | `closed_trades < 100` | IS + OOS both; **OOS K9 sub-threshold → DR1 INCONCLUSIVE_HOLD per C1.D** |
| K10 | NOT APPLICABLE (single-instrument) | — |
| K11 | NOT APPLICABLE (no leverage cap for F1) | — |
| K12 | composite cost-stress fail (DR2 + DR3) | — |

K-gate firing priority order: `K8 > K12 > K7 > K9 > K1/K2/K4 > A-gates > ELIGIBLE_FOR_OOS`.

---

## 11. OOS locking policy (SEALED)

| Policy | Status |
|---|---|
| OOS data shall not be inspected, computed against, simulated over, or queried during IS phase | LOCKED |
| Post-OOS data is informational only | LOCKED |
| OOS inspection requires separately authorized turn after IS verdict `ELIGIBLE_FOR_OOS` + explicit operator approval | LOCKED |
| Modules shall structurally enforce IS-only computation | LOCKED (`oos_inspection_blocked_at_in_sample`) |
| OOS confirmation definition | LOCKED (s11-d1 rev2 magnitude-based form, byte-equivalent) |

**OOS CONFIRMED is reached only iff ALL of:**
1. C7 verdict is `READY_FOR_LONGER_BACKTEST`
2. OOS closed_trades ≥ 100
3. OOS sharpe > 0
4. OOS expectancy > 0
5. OOS `trade_curve_maxdd_pct ≥ -30%` (i.e., `|maxdd| ≤ 30%`)
6. all safety counters zero
7. no-pyramid invariant held
8. starting_cash invariant held

---

## 12. No-live / no-Strategy-Lab / no-brokerage invariants (SEALED; 25 total)

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

**4 new s12-d1-specific:**
`donchian_15_8_locked_at_plan_no_retreat_to_55_20` · `no_revision_of_s11_d1_sealed_artifacts` · `s12_d1_does_not_supersede_s11_d1_v1_p1_p2_clarification_rev2` · `mechanic_family_lock_at_plan_no_reopening_at_draft_or_seal`

---

## 13. Reject-fast criteria (SEALED)

The candidate is REJECTED FAST if ANY of:

- **RF1** Any DR rule fires `REJECT_FAST` (DR2 / DR3 / DR4 / DR5 / DR6 / DR10)
- **RF2** DR9 `mnq_c0_only_data_continuity_integrity_failure` AND > 5 violations
- **RF3** DR6 post-warmup invalid-sizing event count > 0
- **RF4** Any forbidden-verdict-token in runner output
- **RF5** Runner attempts `SetLiveMode` / `SetBrokerageModel` / `DeployAlgorithm` / unauthorized network call / unauthorized Databento call at runtime
- **RF6** Any order-submit attempt while in warmup window
- **RF7** Runner mutates any sealed predecessor artifact (byte-shift) — see §12
- **RF8** Runner makes a Databento API call at any phase
- **RF9** Runner caches `.dbn.zst` files anywhere
- **RF10** Runner accesses `DATABENTO_API_KEY` at any phase
- **RF11** Track silently re-introduces a filter, regime gate, or selection rule
- **RF12** Pyramid mechanism re-introduced in code
- **RF13** Donchian-N or Donchian-M silently switched from the LOCKED 15/8 post-SEAL
- **RF14** Universe widening or symbol substitution attempted at any phase
- **RF15** Track depends on a survivorship-cherry-pick rule
- **RF16** Any retroactive re-anchoring or modification of s11-d1 v1 / P1 / P2 / clarification / rev2 caused by this candidate

**Note (C1.D):** OOS K9 sub-threshold is NOT a REJECT_FAST condition; it maps to DR1 `INCONCLUSIVE_HOLD` per the affirmed clarification at SEAL.

---

## 14. Validation gates (this SEAL turn)

- **V1** ASCII-only.
- **V2** Numbered sections in monotonic order.
- **V3** No execution language.
- **V4** No self-authorization to BUILD or RUN.
- **V5** No code modification.
- **V6** No backtest run.
- **V7** No simulator run.
- **V8** No signal computation.
- **V9** No data fetch.
- **V10** No network IO.
- **V11** No live trading.
- **V12** DRAFT (`7e9c8679`) byte-stable; review (`07be7fc`) byte-stable.
- **V13** Exactly 3 new files staged: this `docs/` spec + 2 `reports/external_research_hunter/` sealed pair.
- **V14** `lessons.md` unstaged and untouched.
- **V15** DA4 = B applied; all other DAs at default A.
- **V16** C1.A and C1.D explicitly affirmed in §0.

---

## 15. Predecessor anchors (byte-stable)

| Anchor | Seal / sha (first 16) |
|---|---|
| Source DRAFT (`docs/.../s12_d1_..._DRAFT.md`) | `9f09ec94028659eb` |
| Review report (`reports/s12_d1_fresh_candidate_tier_n_draft_review.json`) | `860e766e6933751d` |
| s11-d1 v1 spec | `077e29e62f23dbc3` |
| s11-d1 rev2 | `46659b4a8a73cb72` |
| s10-D2 P11 PARK | `e121b82b411697c7` |
| s10-D1 PARK report | `32c1a87146264197` |
| Audit-clean MNQ.c.0 CSV | `8b7b832c62fae185` |

---

## 16. Posture (permanent for this candidate)

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

## 17. Next authorization language

A future operator authorization is required to advance beyond this SEAL. Reference this SEAL by exact path: `docs/s12_d1_mnq_c0_single_instrument_donchian_15_8_tier_n_spec.md`.

Natural next scopes (each requires its own fresh sealed authorization; NONE is pre-approved by this SEAL):

- *"Authorize s12 D1 P1 plan-lock spec only"*
- *"Authorize s12 D1 P2 phase-2 plan only"*
- *"Authorize s12 D1 P3 BUILD only"*
- *"Defer / Pause s12-d1 track"*

---

**S12-D1 Tier-N spec SEALED. DA4=B applied (START_CASH = $100,000). All other DAs at default A. C1.A + C1.D affirmed. OOS K9 risk acknowledged as structural test (DR1 INCONCLUSIVE_HOLD disposition). Trading: PAUSED. Live: BLOCKED_AT_6_GATES. FRC never granted.**
