# s12 D1 MNQ.c.0 Single-Instrument Donchian-15/8 Databento Long-History -- Tier-N Specification DRAFT

Status: DRAFT (not sealed; operator confirms DRAFT ambiguities DA1-DA14 at SEAL; no code, no fetch, no run by this DRAFT).
Authored: 2026-05-27
Authorization: "Authorize s12 D1 MNQ.c.0 single-instrument Donchian-15/8 Tier-N spec DRAFT."

Plan source: `docs/s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_tier_n_spec_plan.md` (committed at `b4eac65`).

Parent reference chain (READ-ONLY; byte-stable; not modified by this DRAFT):
- s11-d1 v1 spec commit: `9c63088`; seal sha256: `077e29e62f23dbc31823bad8447e5ef8d6f1a8c350d4f0c130c4f8f08be61a24`
- s11-d1 P1 plan-lock commit: `7d86486`
- s11-d1 P2 phase-2 plan commit: `f64f984`
- s11-d1 clarification memo commit: `d13b56a`
- s11-d1 rev2 commit: `c110fd4`; seal sha256: `46659b4a8a73cb72fbe0153efed80aaf97b40557f8dfed51a9ba3199c243ed8d`
- s10-d2 park commit: `23c7164` (status `PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED`)
- s10-d1 MNQ+MGC park commit: `1a9acec`; park report seal sha256: `32c1a87146264197fd852e53ba45baf6d6d45e40355b716e5a4d41a08edf1b2f`
- Audit-clean data anchor (MNQ.c.0): `data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_c_0_ohlcv_1d_20190513_20251230.csv` (sha256 `8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e`; 2066 rows; 2019-05-13 -> 2025-12-29)

HARD BOUNDARIES (held by this DRAFT). Plan / spec DRAFT only. No strategy code. No backtest. No simulator. No signal computation. No data fetch. No yfinance / Yahoo Finance call. No Databento call. No DATABENTO_API_KEY access. No QC / LEAN call. No network IO. No review_queue.json mutation. No production idea_memory mutation. No Strategy Lab run. No candidate promotion. No s11-d1 v1 / P1 / P2 / clarification / rev2 sealed-artifact modification. No s10-d2 / s10-d1 / s9 / s7-d1 / B006_NNN / T8 sealed-artifact modification. No ORB branch artifact mutation. No Step 30 cost constant mutation. No CLAUDE.md modification. No docs/decisions.md modification. No RUNBOOK modification. No pipeline_manifest modification. No .gitignore modification. No `brain_memory/projects/trading_bot/lessons.md` modification or staging. No branch change. No branch creation. No git push. No live trading. No profitability claim. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES. FRC never granted.

----

## 1. Mechanic family + Donchian parameters LOCKED at PLAN -- DRAFT does NOT reopen

Unlike the s11-d1 DRAFT (which resolved mechanic family F1 at the DRAFT turn from a closed F1/F2/F3/F4 menu), this s12-d1 DRAFT does **NOT** reopen mechanic-family selection nor reopen the Donchian-N/M parameter pair. Both were LOCKED at PLAN time (commit `b4eac65`) as the load-bearing structural property of the fresh `candidate_record_id`.

The DRAFT confirms and carries forward (without revision option):

| Field | LOCKED at PLAN | Carried byte-equivalent into this DRAFT |
|---|---|---|
| `candidate_record_id` | `s12-d1-mnq-c0-single-instrument-donchian-15-8-databento-long-history` | yes |
| Mechanic family | F1 -- Long+Short Bi-Directional Donchian Trend, No Pyramid, ATR(P)-Based Stop, Single MNQ.c.0 Contract Per Signal | yes |
| Universe | `{MNQ.c.0}` only | yes |
| Donchian entry channel N | **15 days** (load-bearing departure from s11-d1 v1's 55) | yes |
| Donchian exit channel M | **8 days** (load-bearing departure from s11-d1 v1's 20) | yes |
| Signal direction | Long+Short bi-directional | yes |
| Pyramid mechanism | NONE / `max_units_per_market = 1` | yes |
| Schema | `ohlcv-1d` | yes |
| `stype_in` | `continuous` | yes |
| IS window | `2019-05-13 -> 2023-12-29` | yes |
| OOS window | `2024-01-02 -> 2025-12-30` (never inspected at IS) | yes |

A SEAL revision authorization that attempts to alter any of these PLAN-locked fields shall be rejected by the controller and require either (a) a fresh PLAN revision turn, or (b) a fresh `candidate_record_id` per the same first-principles burden that gave rise to s12-d1 itself.

## 2. Why s12-d1 on MNQ.c.0-only is not rescuing s11-d1, s10-D2, s10-D1, s9, s7-D1, B006_NNN

The s11-d1 v1 SEAL section 9 explicitly states that shortening Donchian periods on the s11-d1 candidate REQUIRES A FRESH `candidate_record_id`. s12-d1 satisfies this clause structurally. Beyond that, s12-d1 satisfies the first-principles burden against each prior parked / sealed predecessor:

### 2.1 s12-d1 is not a rescue of s11-d1 (Donchian-55/20 sealed)

| s11-d1 v1 feature | s12-d1 F1 treatment |
|---|---|
| Donchian-55 entry / Donchian-20 exit | Donchian-15 entry / Donchian-8 exit -- materially faster channel; ~3-4x signal-density increase |
| K9 risk: ~25-50 expected closed trades (below floor 100; fires K9 with high prior probability) | K9 risk: ~80-200 expected closed trades (borderline-to-clearing) |
| DR10 turnover risk: low | DR10 turnover risk: ELEVATED (load-bearing trade-off accepted at PLAN) |
| s11-d1 v1 / P1 / P2 / clarification / rev2 byte-stable | s12-d1 does not modify any s11-d1 artifact |

### 2.2 s12-d1 is not a rescue of s10-D2 (4-market Donchian-55/20 portfolio; PARKED)

| s10-D2 feature | s12-d1 F1 treatment |
|---|---|
| Universe `{NQ, GC, ZN, CL}` (4 markets) | Universe `{MNQ.c.0}` only (single instrument; MNQ vs NQ ratio ~1/10 contract notional) |
| Per-market pyramid + per-market cap tracker | NONE; single instrument; max_units = 1 |
| Donchian-55/20 produced 53 OOS trades / 54 IS NQ trades over 10y -> K9 fired | Donchian-15/8 expected ~3-4x signal density |
| OOS verdict: INSUFFICIENT_SAMPLE / OOS_INDETERMINATE_BUT_DIRECTIONALLY_CONSISTENT | s12-d1 OOS not inspected at this DRAFT; no claim |

### 2.3 s12-d1 is not a rescue of s10-D1 MNQ+MGC

| s10-D1 feature | s12-d1 F1 treatment |
|---|---|
| Universe `{MNQ.c.0, MGC.c.0}` | Universe `{MNQ.c.0}` only |
| MGC continuous-stitch DR9 fire | MGC structurally absent |
| Tier-N sealed but never ran | s12-d1 may run only under future separately-authorized P3 BUILD |

### 2.4 s12-d1 is not a rescue of s9 / s7-D1 / B006_NNN

| Predecessor | s12-d1 F1 treatment |
|---|---|
| s9 (RSI-2 mean-reversion on SPY/TLT/GLD/USO ETF-proxy; PARKED) | Trend-following Donchian breakout; structurally orthogonal family; different universe / cost surface |
| s7-D1 (Donchian + pyramid on 4-ETF basket) | NO pyramid in s12-d1; different universe (MNQ futures vs ETFs) |
| B006_001 (SPY vol-targeting) | F1 has no leverage cap; B006_001 leverage-cap pathology structurally absent |
| B006_002 (SPY vol-targeting with DR11) | Same; DR11 NOT in s12-d1's chain |
| T8 family-park memo (ETF-proxy umbrella) | Universe is futures; T8 does not apply |

s12-d1 satisfies all first-principles-burden requirements. The candidate is **structurally fresh**, not a revision of any predecessor.

## 3. Universe (LOCKED at PLAN; restated at SEAL)

| Field | LOCKED value |
|---|---|
| Universe type | `single_fixed_instrument_continuous_micro_futures` |
| Symbol 1 (only symbol) | **`MNQ.c.0`** (Micro E-mini Nasdaq-100, continuous front-month) |
| `AddUniverse` calls | **0** (structurally absent) |
| `removed_from_universe` events | **0** (structurally absent) |
| Symbol count | exactly 1 |
| Symbol substitution clause at later phases | FORBIDDEN (LOCKED at SEAL via `single_instrument_universe_NO_widening_post_seal` invariant) |
| Universe widening at later phases | FORBIDDEN (any wider basket requires a fresh candidate_record_id) |
| Common-history start (verified by s10-D1 audit) | **2019-05-13** |
| Universe-membership integrity surface | structurally N/A |
| Diversification claim by this candidate | NONE (single-instrument; explicit first-principles justification) |

## 4. Dataset (LOCKED at SEAL)

| Field | LOCKED value |
|---|---|
| Vendor | **Databento Historical API** (vendor-level; controller-side never calls) |
| Dataset | **`GLBX.MDP3`** |
| Schema | **`ohlcv-1d`** |
| `stype_in` | **`continuous`** |
| Symbol requested | `["MNQ.c.0"]` |
| Re-use of existing audit-clean CSV | **TRUE** -- MNQ.c.0 CSV at `data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_c_0_ohlcv_1d_20190513_20251230.csv` (sha256 `8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e`) reused byte-equivalent. **ZERO new Databento call required.** |
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
| IS window length | ~4.6 years (~1,140 trading days) |
| MNQ.c.0 IS row count (audit-confirmed by s10-D1) | **1,443** (`is_pct_observed = 1.2365` PASS) |
| **OOS window start (never inspected at IS)** | **`2024-01-02`** |
| **OOS window end (never inspected at IS)** | **`2025-12-30`** |
| OOS window length | ~2 years |
| MNQ.c.0 OOS row count (structural only; NO return analysis) | **622** |
| Post-OOS data | `2026-01-02 onward` (informational only) |
| OOS inspection at IS-phase | FORBIDDEN (`oos_inspection_blocked_at_in_sample` invariant) |

## 8. Data availability assumptions and DR gates

### 8.1 Assumptions inherited from s10-D1 audits

- `MNQ.c.0` over `2019-05-13 -> 2025-12-30` is **DR9-clean under both audit variants** (strict + holiday-aware; 0 calendar gaps > 5 days; max single-day abs-log-return 0.1164).
- DR9 thresholds carried byte-equivalent (`0.95 / 0.30 / 5 / 5`).
- Step 02c for this candidate is a re-confirmation pass against the same CSV (no fresh Databento call).

### 8.2 DR rules adapted for single-instrument F1 Donchian-15/8 (LOCKED at SEAL)

| Rule | Trigger | Severity | F1-Donchian-15/8 note |
|---|---|---|---|
| DR1 | `oos_rebalance_count < 36` (OOS phase only) | `INCONCLUSIVE_HOLD` | OOS-only; not evaluated at IS |
| DR2 | `oos_metrics_degrade_materially_under_cost_stress` | `REJECT_FAST` | unchanged |
| DR3 | `zero_cost_only_survival` (S0 > 0 AND all S1..S4 <= 0) | `REJECT_FAST` | unchanged |
| DR4 | `oos_negative_while_is_positive_unexplained` | `REJECT_FAST` | OOS-only |
| DR5 | `cost_stress_turns_edge_negative` (tier flip) | `REJECT_FAST` / `INCONCLUSIVE_HOLD` carveout | unchanged |
| DR6 | `post_warmup_sizing_ambiguity_or_invalid` (NARROWED post-warmup only) | `REJECT_FAST` | unchanged; carried from B006_002 |
| DR7 | `missing_oos_or_date_window_evidence` | `INCONCLUSIVE_HOLD` | unchanged |
| DR8 | `live_or_order_routing_path_detected` at Initialize | `HARD_FAIL_VOIDED` | unchanged |
| **DR9** | **`mnq_c0_only_data_continuity_integrity_check`** | `INCONCLUSIVE_HOLD` | MNQ-only; MGC failure mode structurally absent |
| **DR10** | **`turnover_cost_explosion`** (`annual_turnover > 0.50` OR `S2 cost drag > 0.05`) | `REJECT_FAST` | **ELEVATED prior probability vs s11-d1 v1** because Donchian-15/8 raises annual turnover materially; this is the load-bearing trade-off accepted at PLAN |
| DR11 | NOT IN CHAIN | -- | F1 has no leverage cap; DR11 structurally absent |

DR precedence chain (LOCKED at SEAL): `DR7 -> DR1 -> DR9 -> DR10 -> DR6 -> DR4 -> DR2 -> DR3 -> DR5` (carried byte-equivalent from s11-d1 v1; DR11 omitted because F1 has no leverage cap).

## 9. Cost stress from day 1 (LOCKED at SEAL)

Cost-stress matrix S0/S1/S2/S3/S4 LOCKED in the first IS diagnostic; deferral forbidden. Carried byte-equivalent from s11-d1 v1 (5-tier set).

### 9.1 Cost tiers (5-tier; carried byte-equivalent from s11-d1 v1)

| Tier | `cost_scalar` | `slippage_scalar` | Note |
|---|---:|---:|---|
| `S0` | 0.0 | 0.0 | zero-cost ideal; tests if a profitable kernel exists |
| `S1` | 1.0 | 1.0 | baseline retail; commission + fees + slip @ 1.0x |
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
| Expected S0 net PnL sign | open question (no a-priori claim) |
| Acceptance threshold S0 net PnL | `> 0` after >= 100 trades |
| Acceptance threshold S1 net PnL | `> 0` (K1 / K2 fire if `<= 0`) |
| Pre-registered max-drawdown tolerance | K4 = 50% of `START_CASH_USD` (DRAFT_AMBIGUITY DA5; carried byte-equivalent from s11-d1 v1 K4 formula) |
| Pre-registered cost-stress survival | all five cost tiers OOS Sharpe > 0 -> `ELIGIBLE_FOR_HUMAN_REVIEW`; S0/S1 positive but S2/S3/S4 degrade > 50% -> K12 REJECT_FAST |

## 10. Sample-size / K9 rules (LOCKED at SEAL)

| Field | LOCKED value (DRAFT) |
|---|---|
| K9 threshold | `total_closed_trades >= 100` over IS window (LOCKED non-negotiable; `no_k9_relaxation`) |
| **Expected trade count for F1 Donchian-15/8 bi-directional on MNQ.c.0 over 4.6y IS** | **80-200 portfolio trades** (estimated; subject to Step 06 simulator) |
| Comparison to s11-d1 v1 (Donchian-55/20) | s11-d1 v1 disclosed ~25-50 expected (fires K9); s12-d1 expects ~3-4x more signals (borderline-to-clearing). The structural test of the fresh candidate. |
| K9 risk | **borderline at lower bound** -- lower estimate 80 < K9; central estimate ~140 clears; upper estimate 200 clears with margin |
| Per-symbol minimum | NOT APPLICABLE for single-instrument; K9 IS the per-symbol minimum |
| If K9 fires anyway | `DR1 INCONCLUSIVE_HOLD` (not REJECT_FAST); candidate archived without parameter modification; the K9-mitigation hypothesis is falsified by the diagnostic |

## 11. Diversification expectations -- single-instrument scope (LOCKED at SEAL)

| Field | LOCKED value |
|---|---|
| `A7_effective_independent_bets_min` | **NOT APPLICABLE** (trivially 1 by construction; removed from acceptance gate set) |
| `K10_avg_pairwise_dependence_max` | **NOT APPLICABLE** (no pairs; removed from K-gate set) |
| `K6_per_symbol_observed_win_rate_dispersion` | **NOT APPLICABLE** (no dispersion to measure) |
| Per-symbol contribution distribution | trivially 100% to MNQ.c.0; standalone risk profile IS the entire diagnostic surface |
| Diversification claim by this candidate | NONE |
| Disclaimer carried byte-equivalent | "Diversification independence does NOT imply positive edge" (LESSON_B006_002_002) -- applies trivially here |

## 12. OOS locking policy (LOCKED at SEAL; carried byte-equivalent)

| Policy | Status |
|---|---|
| OOS data shall not be inspected, computed against, simulated over, or queried during IS phase | LOCKED |
| Post-OOS data is informational only; no diagnostic uses it | LOCKED |
| OOS inspection requires a separately authorized turn after IS verdict `ELIGIBLE_FOR_OOS` + explicit operator approval | LOCKED |
| Modules shall structurally enforce IS-only computation | LOCKED (`oos_inspection_blocked_at_in_sample`) |
| **OOS confirmation definition** | LOCKED at SEAL using **s11-d1 rev2 magnitude-based form** (carried byte-equivalent from `c110fd4`); v1 sign/inequality typo NOT re-introduced |

s11-d1 rev2 oos_confirmation_definition adopted byte-equivalent at SEAL:

> *"OOS is CONFIRMED only iff ALL of: (a) C7 verdict is READY_FOR_LONGER_BACKTEST, (b) OOS closed_trades >= 100, (c) OOS sharpe > 0, (d) OOS expectancy > 0, (e) OOS trade_curve_maxdd_pct >= -30% (equivalently |trade_curve_maxdd_pct| <= 30%; i.e., the realized OOS drawdown shall not exceed 30% in magnitude), (f) all safety counters zero, (g) no-pyramid invariant held, (h) starting_cash invariant held."*

## 13. No-live / no-Strategy-Lab / no-brokerage policy (LOCKED at SEAL; carried byte-equivalent)

Total invariants at SEAL: **25** for F1 Donchian-15/8 single-instrument (no DR11; no C4 invariants).

7 inherited B005_NNN framework:
- `no_live_trading` * `no_strategy_lab_promotion` * `no_review_queue_mutation` * `no_brokerage_connection` * `no_external_network` * `no_databento_at_runtime` * `no_production_signal`

4 inherited B006_001:
- `no_strategy_optimization_authorized` * `no_profitability_claim` * `no_universe_membership_logic` * `no_dr_redefinition_post_seal`

2 inherited B006_002 (F1 has no leverage cap; leverage-cap-specific invariants do NOT carry):
- `no_warmup_order_submission`
- `dr6_warmup_contamination_blocked`

5 inherited s10-D1-specific:
- `no_continuous_roll_stitch_modification_post_seal`
- `no_mcl_inclusion_under_long_history_scope`
- `no_intraday_schema_ingest_under_daily_only_design`
- `databento_api_key_read_from_env_only_never_logged_or_saved` (vacuously true since no fresh fetch)
- `no_pyramid_per_signal`

3 inherited s11-d1-specific:
- `single_instrument_universe_NO_widening_post_seal`
- `no_substitution_of_any_symbol_into_this_universe_post_seal`
- `mnq_c0_csv_reuse_byte_equivalent_no_fresh_fetch`

4 NEW s12-d1-specific (LOCKED at SEAL):
- `donchian_15_8_locked_at_plan_no_retreat_to_55_20`
- `no_revision_of_s11_d1_sealed_artifacts`
- `s12_d1_does_not_supersede_s11_d1_v1_p1_p2_clarification_rev2`
- `mechanic_family_lock_at_plan_no_reopening_at_draft_or_seal`

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
- **RF7** Runner mutates any s11-d1 v1 / P1 / P2 / clarification / rev2 / s10-d2 / s10-d1 / s9 / s7-d1 / B006_NNN / T8 / s12-d1 sealed artifact (byte-shift)
- **RF8** Runner makes a Databento API call at any phase (controller-side; this candidate is zero-fresh-fetch)
- **RF9** Runner caches `.dbn.zst` files anywhere
- **RF10** Runner accesses `DATABENTO_API_KEY` at any phase
- **RF11** Track silently re-introduces a filter, regime gate, or selection rule
- **RF12** Pyramid mechanism re-introduced in code
- **RF13** Donchian-N or Donchian-M silently switched from the LOCKED 15/8 post-SEAL
- **RF14** Universe widening or symbol substitution attempted at any phase
- **RF15** Track depends on a survivorship-cherry-pick rule
- **RF16** Any retroactive re-anchoring or modification of s11-d1 v1 / P1 / P2 / clarification / rev2 caused by this candidate

K-gates carried byte-equivalent from s11-d1 v1 with single-instrument simplifications:

- **K1** `sharpe_proxy_per_trade_below_zero_at_S1`
- **K2** `expectancy_per_trade_dollars_nonpositive_at_S1`
- **K4** `trade_curve_max_drawdown_above_threshold` (DA5 default: K4 = 50% of `START_CASH_USD`)
- **K6** NOT APPLICABLE (single-instrument)
- **K7** `silent_filter_introduction_after_lock`
- **K8** `runtime_safety_invariant_false`
- **K9** `closed_trades_below_100`
- **K10** NOT APPLICABLE (single-instrument)
- **K11** NOT APPLICABLE (no leverage cap for F1)
- **K12** composite cost-stress fail (DR2 + DR3)

K-gate firing priority order: `K8 > K12 > K7 > K9 > K1/K2/K4 > A-gates > ELIGIBLE_FOR_OOS`.

## 15. Validation gates

Validation gates the DRAFT-authoring turn satisfies:

- **V1** ASCII-only.
- **V2** Numbered sections in monotonic order (1..17).
- **V3** No execution language.
- **V4** No self-authorization (this DRAFT does NOT authorize SEAL; only a separate operator turn does that).
- **V5** No code modification.
- **V6** No backtest run.
- **V7** No simulator run.
- **V8** No signal computation.
- **V9** No data fetch.
- **V10** No network IO.
- **V11** No live trading.
- **V12** No prior-phase artifact modification (s11-d1 v1 / P1 / P2 / clarification / rev2 byte-stable; s10-d2 / s10-d1 / s9 / s7-d1 / B006_NNN / T8 byte-stable).
- **V13** The committed DRAFT file is the ONLY new file in this turn's commit.
- **V14** The brain_memory dirty `lessons.md` remains UNSTAGED and UNTOUCHED.
- **V15** Mechanic family + Donchian-15/8 LOCKED at PLAN; DRAFT does NOT reopen these.
- **V16** Single-instrument adaptations explicit (A7/K10/K6 NOT APPLICABLE; DR11 structurally absent).
- **V17** DA register includes only the parameters NOT locked at PLAN.

## 16. HALT conditions + DRAFT ambiguity register

HALT conditions:

- **H1** If any V-gate fails, the turn HALTs.
- **H2** If pre-stage git index is non-empty, the turn HALTs.
- **H3** If staged file count is anything other than 1 at commit time, the turn HALTs.
- **H4** If staged file is anything other than `docs/s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_tier_n_spec_DRAFT.md`, the turn HALTs.
- **H5** If `lessons.md` is accidentally staged, the turn HALTs and `git restore --staged brain_memory/projects/trading_bot/lessons.md` before retrying.
- **H6** If any s11-d1 sealed artifact (v1 / P1 / P2 / clarification / rev2) is detected as modified, the turn HALTs.

### 16.1 DRAFT ambiguity register (for operator confirmation at SEAL; operator types option letter)

Note: Donchian N/M, mechanic family, universe, and IS/OOS windows are LOCKED at PLAN and are intentionally NOT in this register. The DA register covers ONLY parameters deferred from PLAN to DRAFT/SEAL.

- **DA1** ATR stop window P: A `20` (default; carried byte-equivalent from s11-d1 v1 Wilder ATR(20)) / B `14` (Wilder canonical alternative) / C `10` (faster stop)
- **DA2** ATR stop multiplier K: A `2.0` (default; carried byte-equivalent from s11-d1 v1 "2N stop") / B `1.5` (tighter) / C `2.5` (looser)
- **DA3** Per-trade risk percentage: A `1.0%` of portfolio equity (default; carried byte-equivalent from s11-d1 v1) / B `0.5%` (more conservative; flagged for K9 risk via lower contracts-per-trade) / C `2.0%` (more aggressive; flagged for K4 risk)
- **DA4** `START_CASH_USD`: A `50000` (default; carried byte-equivalent from s11-d1 v1) / B `100000` (s11-d1 DRAFT pre-SEAL default; would roughly halve contracts-per-trade for a given ATR; mitigates DR10 cost-drag risk via smaller absolute commissions/slip per dollar) / C `25000` (more aggressive)
- **DA5** K4 max-drawdown threshold: A `0.50` (50% of `START_CASH_USD`; carried byte-equivalent from s11-d1 v1 K4 formula) / B `0.30` (more conservative; s7-D1 / B006 lineage) / C `0.40` (intermediate)
- **DA6** Output schema name: A `sparta.s12.d1.mnq_c0.donchian_15_8.diagnostic_run_report.v1` (default) -- LOCKED at SEAL
- **DA7** Cost-stress tier set: A 5-tier `S0/S1/S2/S3/S4` with scalars `0.0 / 1.0 / 1.5 / 2.0 / 3.0` (default; carried byte-equivalent from s11-d1 v1) -- LOCKED at SEAL non-negotiable per `no_dr_redefinition_post_seal`
- **DA8** Commission per round-trip: A `$0.74` (default; carried byte-equivalent from s11-d1 v1) -- LOCKED at SEAL
- **DA9** Fees per round-trip: A `$0.36` (default; carried byte-equivalent from s11-d1 v1) -- LOCKED at SEAL
- **DA10** Slippage entry/stop/exit ticks: A `1 / 1 / 1` (default; carried byte-equivalent from s11-d1 v1) -- LOCKED at SEAL
- **DA11** `WARMUP_DAYS`: A `MAX(longest_lookback, 220)` resolved to `220` (default; carried byte-equivalent from s11-d1 v1 lineage; longest s12-d1 lookback is ATR(20) so floor at 220) -- LOCKED at SEAL
- **DA12** RTH window: A `09:30-16:00 ET America/New_York` (default; carried byte-equivalent from s11-d1 v1) -- LOCKED at SEAL
- **DA13** DR9 thresholds (carried byte-equivalent from s10-D1 / s11-d1 v1 sealed chain): A `0.95 / 0.30 / 5 / 5` -- LOCKED at SEAL non-negotiable per `no_dr_redefinition_post_seal`
- **DA14** DR10 thresholds (carried byte-equivalent; ELEVATED prior probability of DR10 fire flagged at PLAN): A `annual_turnover_threshold = 0.50` AND `s2_cost_drag_threshold = 0.05` -- LOCKED at SEAL non-negotiable per `no_dr_redefinition_post_seal`

The operator confirms DA1-DA14 at the SEAL turn by typing an explicit revision authorization (e.g., "Authorize s12 D1 MNQ.c.0 Tier-N spec SEAL. Confirm all DRAFT ambiguities as default A.") or revises the genuinely-negotiable items (DA1-DA5, since DA6-DA14 are framework-locked or schema-naming) with explicit per-item revisions.

### 16.2 Mitigation note for DR10 risk (informational; no parameter change authorized at DRAFT)

The PLAN section 11 flagged that Donchian-15/8 raises DR10 turnover-cost-explosion risk (S2 cost drag may exceed 5%). The DRAFT-level mitigation lever (NOT a DR-threshold change, which is forbidden) is **DA4=B** (raising START_CASH_USD from $50,000 to $100,000), which reduces per-dollar commission/slip pressure by roughly halving contracts-per-trade for a given ATR. This is presented as an alternative at SEAL; default DA4=A (carry $50k byte-equivalent) keeps the candidate closest to s11-d1 v1's structural baseline.

## 17. Next authorization language

A future operator authorization is required to proceed beyond this DRAFT. That authorization shall reference this DRAFT by exact path:

`docs/s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_tier_n_spec_DRAFT.md`

The next operator authorization in the established controller-session pattern shall use one of these scopes:

- **"Authorize s12 D1 MNQ.c.0 Tier-N spec SEAL. Confirm all DRAFT ambiguities as default A."** -- begin the SEAL flow with DRAFT defaults accepted (Donchian-15/8 LOCKED from PLAN; ATR-20 K=2.0; bi-directional; 1.0% risk; no pyramid; K4 50%; K9 100; START_CASH $50k; WARMUP 220; RTH 09:30-16:00 ET; DR9 thresholds carried; DR10 thresholds carried; 5-tier cost stress).
- **"Authorize s12 D1 MNQ.c.0 Tier-N spec SEAL with revisions: DA4=B; all others as default A."** -- begin the SEAL flow with START_CASH $100k mitigation for DR10 risk; all other DAs default.
- **"Authorize s12 D1 MNQ.c.0 Tier-N spec SEAL with revisions: DA<X>=<L>, ...; all others as default A."** -- begin the SEAL flow with arbitrary per-item revisions on the genuinely-negotiable DA1-DA5 register.
- **"Authorize alternative track selection plan revision only"** -- if the operator rejects the s12-d1 candidate entirely and wants a fresh selection-plan revision.
- **"Authorize cross-domain pivot only"** -- if the operator pivots to a different project entirely.
- **"Defer / Pause trading-bot track"** -- if the operator holds the DRAFT on file without advancing.

This DRAFT is the source of truth for the s12-d1 MNQ.c.0 single-instrument Donchian-15/8 candidate's intended Tier-N spec scope at DRAFT time. Future SEAL / BUILD / RUN phases that contradict this DRAFT require either a fresh DRAFT revision or an out-of-band justification.

No phase of this chain confers any standing authorization for live trading, brokerage connection, Strategy Lab promotion, OOS inspection, or production candidate registration. Each remains BLOCKED at separate phases. Trading remains `PAUSED`. Live remains `BLOCKED_AT_6_GATES`. FRC `NEVER_GRANTED`.

----

End of DRAFT. Plan / spec DRAFT only. No code. No backtest. No simulator. No signal. No data fetch. No yfinance. No Yahoo Finance. No Databento. No DATABENTO_API_KEY access. No QC. No LEAN. No brokerage. No real order. No paper order. No Strategy Lab promotion. No review_queue mutation. No production idea_memory mutation. No ORB branch mutation. No lessons.md modification or staging. No live trading. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES.
