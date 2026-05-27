# s12 D1 MNQ.c.0 Single-Instrument Donchian-15/8 Databento Long-History Tier-N Specification Plan

Status: PLAN_ONLY (no code written, no spec sealed, no data fetched by this plan; the next step is a separate operator authorization to DRAFT the Tier-N spec, then SEAL it under separate authorization, then BUILD downstream modules each under separate authorization).
Authored: 2026-05-27
Authorization: "Authorize s12 D1 MNQ.c.0 single-instrument Donchian-15/8 fresh-candidate Tier-N spec plan only."

Fresh-candidate justification: the s11-d1 sealed Tier-N spec at commit `9c63088` (v1 spec seal sha `077e29e62f23dbc31823bad8447e5ef8d6f1a8c350d4f0c130c4f8f08be61a24`) section 9 ("Mitigation options NOT pre-approved by this spec") states verbatim that "Shorten Donchian periods (e.g., 20/10 instead of 55/20) -- would change strategy logic; REQUIRES FRESH CANDIDATE_RECORD_ID; not authorized here." The operator's choice to test Donchian-15/8 (a strict shortening from s11-d1's Donchian-55/20) therefore requires a fresh `candidate_record_id`. This plan authors that fresh candidate.

Parent reference chain (READ-ONLY; byte-stable; not modified by this plan):

- s11-d1 v1 spec commit: `9c63088`
- s11-d1 v1 spec seal sha256: `077e29e62f23dbc31823bad8447e5ef8d6f1a8c350d4f0c130c4f8f08be61a24`
- s11-d1 P1 plan-lock commit: `7d86486` (anchored to v1)
- s11-d1 P2 phase-2 plan commit: `f64f984` (anchored to v1)
- s11-d1 clarification memo commit: `d13b56a`
- s11-d1 rev2 commit: `c110fd4`
- s11-d1 rev2 seal sha256: `46659b4a8a73cb72fbe0153efed80aaf97b40557f8dfed51a9ba3199c243ed8d`
- s10-d2 park commit: `23c7164`
- s10-d2 park status: `PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED`
- s10-d1 MNQ+MGC park commit: `1a9acec`
- s10-d1 MNQ+MGC park report seal sha256: `32c1a87146264197fd852e53ba45baf6d6d45e40355b716e5a4d41a08edf1b2f`
- Audit-clean data anchor (MNQ.c.0): `data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_c_0_ohlcv_1d_20190513_20251230.csv` (sha256 `8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e`; 2066 rows)

HARD BOUNDARIES (held by this plan). Plan only. No strategy code. No backtest. No simulator. No new signal computation. No OOS inspection. No data fetch. No yfinance / Yahoo Finance call. No Databento call. No DATABENTO_API_KEY access. No QC / LEAN call. No network IO. No review_queue.json mutation. No production idea_memory mutation. No Strategy Lab run. No candidate promotion. No s11-d1 v1 / P1 / P2 / clarification memo / rev2 sealed-artifact modification. No s10-d2 / s10-d1 / s9 / s7 D1 / B006_NNN sealed-artifact modification. No ORB branch artifact mutation. No Step 30 cost constant mutation. No CLAUDE.md modification. No docs/decisions.md modification. No RUNBOOK modification. No pipeline_manifest modification. No .gitignore modification. No `brain_memory/projects/trading_bot/lessons.md` modification or staging. No branch change. No branch creation. No commit beyond the single new plan file. No git push. No live trading. No profitability claim. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES. FRC never granted.

----

## 1. Purpose

Author a sealed plan-to-spec for the first Tier-N specification of a fresh single-instrument candidate on MNQ.c.0 Databento daily-bar data using a deliberately faster Donchian channel (15/8) than the s11-d1 sealed spec's Donchian-55/20. The fresh candidate's load-bearing structural property is a faster signal frequency intended to bring the expected IS-window closed-trade count above the K9 floor of 100; the s11-d1 v1 SEAL explicitly disclosed expected closed_trades of ~25-50 (below K9) for the Donchian-55/20 design, and explicitly stated that shortening Donchian periods requires a fresh `candidate_record_id`. This plan authors that fresh candidate.

The plan does NOT seal the spec; it authors the plan-to-DRAFT that will inform a subsequent operator-authorized DRAFT turn, which will in turn inform a subsequent operator-authorized SEAL turn. No code, no data fetch, no Databento call is performed by this plan. The s11-d1 v1 spec, P1 plan-lock, P2 phase-2 plan, clarification memo, and rev2 remain byte-stable, binding, and unmodified by this plan.

## 2. Candidate identification

| Field | Proposed value (subject to operator confirmation at DRAFT, then SEAL) |
|---|---|
| `candidate_record_id` | **`s12-d1-mnq-c0-single-instrument-donchian-15-8-databento-long-history`** |
| `candidate_family` | **F1 trend-no-pyramid** (LOCKED at PLAN -- the entire candidate is defined by being a faster-Donchian variant of s11-d1's F1; no mechanic-family menu) |
| `is_a_trade_candidate` | true |
| `is_an_equity_universe_candidate` | false |
| `is_a_b006_001_revision` | false |
| `is_a_b006_002_revision` | false |
| `is_a_s7_d1_revision` | false |
| `is_a_s9_revision` | false |
| `is_a_s10_d1_revision` | false |
| `is_a_s10_d2_revision` | false |
| `is_a_s11_d1_revision` | **false** -- structurally a fresh `candidate_record_id` per s11-d1 v1 SEAL section 9 forbidden-revision clause |
| `is_a_b006_NNN_extension` | false |
| `is_a_single_instrument_candidate` | **true** (load-bearing structural property) |
| `predecessor_lineage_references_read_only` | `s11_d1_v1_sealed_spec`, `s11_d1_rev2_sealed_spec`, `s11_d1_p1_plan_lock`, `s11_d1_p2_phase_2_plan`, `s11_d1_clarification_memo`, `s10_d2_park`, `s10_d1_mnq_mgc_park`, `s9_rsi2_etf_proxy_park`, `s7_d1_etf_proxy_park`, `b006_001_archival`, `b006_002_archival`, `t8_etf_proxy_family_park`, `s10_d1_micro_availability_probe` |
| `diagnostic_only` | true |
| `not_promotable_via_this_diagnostic` | true |
| `default_advisory_label` | `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` |

## 3. Universe (proposed; LOCKED at SEAL)

| Field | Proposed value (LOCKED at SEAL) |
|---|---|
| Universe type | `single_fixed_instrument_continuous_micro_futures` |
| Symbol 1 (only symbol) | **`MNQ.c.0`** (Micro E-mini Nasdaq-100, continuous front-month) |
| `AddUniverse` calls | **0** (structurally absent) |
| `removed_from_universe` events | **0** (structurally absent) |
| Symbol count | exactly 1 |
| Symbol substitution clause at later phases | FORBIDDEN (LOCKED at SEAL via `no_universe_substitution_post_seal` invariant) |
| Universe widening at later phases | FORBIDDEN (any wider basket requires a fresh `candidate_record_id`, NOT a revision) |
| Symbols explicitly excluded for any future phase of this candidate | MGC.c.0 (DR9-failed per s10-d1 park), MCL.c.0 (s10-d1 micro availability memo: unreliable before 2021-07), and all other Databento micros |
| Common-history start (verified by s10-d1 audit cycle) | **2019-05-13** |
| Universe-membership integrity surface | structurally N/A (fixed single-instrument; no point-in-time universe ledger) |
| Diversification claim | NONE (single-instrument; `effective_independent_bets = 1` trivially; per-instrument profile replaces multi-symbol diversification metric) |
| Per-symbol contribution distribution requirement | trivially satisfied (single instrument carries all PnL by definition; A4 MaxDD and K4 trade-curve MaxDD remain load-bearing as risk-profile diagnostics) |

## 4. Data assumptions (proposed; LOCKED at SEAL)

| Field | Proposed value (LOCKED at SEAL) |
|---|---|
| Vendor | **Databento Historical API** (vendor-level; controller-side never calls) |
| Dataset | **`GLBX.MDP3`** |
| Schema | **`ohlcv-1d`** |
| `stype_in` | **`continuous`** |
| Symbol requested | `["MNQ.c.0"]` |
| **Re-use of existing audit-clean CSV** | **TRUE** -- the MNQ.c.0 CSV at `data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_c_0_ohlcv_1d_20190513_20251230.csv` (sha256 `8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e`) is reused byte-equivalent. **ZERO new Databento call required for this candidate.** |
| Step 02b for this candidate | manifest cross-link only (no fresh fetch); separately authorized turn produces a candidate-specific manifest pinning the existing CSV sha |
| Local cache writes outside operator-explicit ingest directory | LOCKED OFF |
| API key handling at any phase of this candidate | NOT REQUIRED (no fresh fetch); `DATABENTO_API_KEY` environment-variable presence is OPTIONAL at every controller-side phase; `databento_api_key_read_from_env_only_never_logged_or_saved` invariant carried byte-equivalent from s10-d1 |
| Controller-side Databento call at any phase | LOCKED OFF |

## 5. Schema (LOCKED at SEAL)

| Field | LOCKED value |
|---|---|
| Schema | `ohlcv-1d` |
| Records expected per trading day | 1 (daily bar) |
| Fields | `ts_event`, `open`, `high`, `low`, `close`, `volume` (required columns set; carried byte-equivalent from s11-d1 v1) |
| Intraday schemas (`1s` / `1m` / `1h`) | OUT OF SCOPE for this candidate's Tier-N |

## 6. stype_in (LOCKED at SEAL)

| Field | LOCKED value |
|---|---|
| `stype_in` | `continuous` |
| Continuous roll stitch | Databento native continuous-front-month synthesis; details out of operator's modification scope |
| `no_continuous_roll_stitch_modification_post_seal` invariant | TRUE |

## 7. IS / OOS windows (LOCKED at SEAL)

Carried byte-equivalent from s11-d1 v1 sealed spec; the underlying CSV already covers both windows.

| Field | LOCKED value |
|---|---|
| **IS window start** | **`2019-05-13`** |
| **IS window end** | **`2023-12-29`** |
| IS window length | ~4.6 years (~1,140 trading days) |
| MNQ.c.0 IS-window observed row count (audit-confirmed by s10-d1 audit) | **1,443** (`is_pct_observed = 1.2365` PASS) |
| **OOS window start (never inspected at IS)** | **`2024-01-02`** |
| **OOS window end (never inspected at IS)** | **`2025-12-30`** |
| OOS window length | ~2 years |
| MNQ.c.0 OOS-window observed row count (structural only; NO return analysis at IS phase) | **622** |
| Post-OOS data | `2026-01-02 onward` (informational only; no diagnostic) |
| OOS inspection at IS-phase | FORBIDDEN (`oos_inspection_blocked_at_in_sample` invariant carried byte-equivalent from s11-d1 v1) |

## 8. Strategy mechanic family (LOCKED at PLAN)

Unlike the s11-d1 PLAN (which deferred mechanic-family selection to its DRAFT turn across F1-F4), this fresh candidate's mechanic family is LOCKED at PLAN. The candidate's load-bearing structural property is "Donchian-15/8 on MNQ.c.0 single-instrument" -- changing mechanic family would defeat the fresh-candidate justification. The DRAFT turn shall NOT reopen mechanic-family selection.

**Mechanic family: F1 -- Long+Short Bi-Directional Donchian-15 Entry / Donchian-8 Exit, No Pyramid, ATR(P)-Based Stop, Single MNQ.c.0 Contract Per Signal.**

Differences from s11-d1 v1 F1 (the parent reference):

| Aspect | s11-d1 v1 F1 (sealed at `9c63088`) | s12-d1 F1 (this plan, proposed at SEAL) |
|---|---|---|
| Donchian entry channel | **55 days** (LOCKED in v1) | **15 days** (LOCKED at this PLAN; load-bearing departure) |
| Donchian exit channel | **20 days** (LOCKED in v1) | **8 days** (LOCKED at this PLAN; load-bearing departure) |
| Signal direction | Long+Short bi-directional | **Long+Short bi-directional** (carried; LOCKED at PLAN) |
| Pyramid mechanism | NONE / `max_units_per_market = 1` | **NONE** (carried byte-equivalent; LOCKED at PLAN) |
| ATR stop method | Wilder ATR(20) * 2N | TBD at DRAFT (proposed Wilder ATR(20) * 2N carried byte-equivalent from v1; revisable at SEAL only via DA register) |
| Per-trade risk | 1% portfolio equity | TBD at DRAFT (proposed 1% carried byte-equivalent from v1) |
| RTH window | `09:30-16:00 ET` | TBD at DRAFT (proposed `09:30-16:00 ET` carried byte-equivalent from v1) |
| Roll method | Databento continuous front-month | Carried byte-equivalent |
| AMB6 filter | NONE | NONE (carried; LOCKED at PLAN) |
| Regime overlay | NONE | NONE (LOCKED at PLAN) |
| Correlation filter | NOT APPLICABLE (single-instrument) | NOT APPLICABLE (carried) |
| Vol-targeting | NONE | NONE (LOCKED at PLAN; not vol-targeting mechanic family) |
| Leverage cap | NONE (1% per-trade risk sizing only) | NONE (carried; DR11 structurally absent) |
| `START_CASH_USD` | $50,000 | TBD at DRAFT (proposed $50,000 carried byte-equivalent from v1; operator may revise at SEAL) |

The Donchian-15/8 choice is a deliberate K9-mitigation departure: s11-d1 v1 explicitly disclosed at SEAL that expected closed_trades over 4.6y IS is ~25-50 (below K9 floor of 100) for Donchian-55/20. Donchian-15/8 is expected to produce roughly 3-4x more signals than Donchian-55/20 (channel-length to signal-density scales sub-linearly but materially); the rough estimate is 80-200 IS trades, which puts the candidate at or above the K9 floor in the central scenario. This is the falsifiable structural test of the fresh candidate.

## 9. Locked parameter values (DEFERRED to DRAFT/SEAL turns except where LOCKED at PLAN)

| Class | LOCKED at PLAN | Locked at SEAL | Notes |
|---|---|---|---|
| `candidate_record_id` | **`s12-d1-mnq-c0-single-instrument-donchian-15-8-databento-long-history`** | -- | LOCKED at PLAN |
| Universe | `{MNQ.c.0}` only | yes | LOCKED at PLAN |
| Mechanic family | F1 trend-no-pyramid | -- | LOCKED at PLAN |
| Donchian entry N | **15** | yes | LOCKED at PLAN (load-bearing departure from s11-d1 v1's 55) |
| Donchian exit M | **8** | yes | LOCKED at PLAN (load-bearing departure from s11-d1 v1's 20) |
| Signal direction | Long+Short bi-directional | yes | LOCKED at PLAN |
| Pyramid mechanism | NONE / `max_units_per_market = 1` | yes | LOCKED at PLAN; `no_pyramid_per_signal` non-negotiable |
| `IS_WINDOW_START` | -- | yes | `2019-05-13` (carried) |
| `IS_WINDOW_END` | -- | yes | `2023-12-29` (carried) |
| `OOS_WINDOW_START` | -- | yes | `2024-01-02` (carried; never inspected) |
| `OOS_WINDOW_END` | -- | yes | `2025-12-30` (carried; never inspected) |
| ATR stop window P | -- | yes | TBD at DRAFT; proposed 20 (Wilder; carried byte-equivalent from s11-d1 v1) |
| ATR stop multiplier K | -- | yes | TBD at DRAFT; proposed 2.0 (carried byte-equivalent from s11-d1 v1) |
| Per-trade risk percentage | -- | yes | TBD at DRAFT; proposed 1.0% portfolio equity (carried byte-equivalent from s11-d1 v1) |
| `START_CASH_USD` | -- | yes | TBD at DRAFT; proposed `50000` (carried byte-equivalent from s11-d1 v1); operator may revise at SEAL |
| `WARMUP_DAYS` | -- | yes | TBD at DRAFT; proposed `MAX(longest_lookback, 220)` -> resolved to 220 (carried byte-equivalent from s11-d1 v1) |
| K4 max-drawdown threshold | -- | yes | TBD at DRAFT; proposed 50% (carried byte-equivalent from s11-d1 v1 K4 formula) |
| K9 minimum trade-count threshold | -- | yes | LOCKED at `>= 100` (framework byte-equivalent; non-negotiable per `no_k9_relaxation`) |
| Cost-stress tier set | -- | yes | TBD at DRAFT; proposed 5-tier S0/S1/S2/S3/S4 (carried byte-equivalent from s11-d1 v1) |
| Output schema name | -- | yes | TBD at DRAFT; proposed `sparta.s12.d1.mnq_c0.donchian_15_8.diagnostic_run_report.v1` |
| DR9 thresholds | -- | yes | TBD at DRAFT; proposed `0.95` / `0.30` / `5` / `5` (carried byte-equivalent from s11-d1 v1) |

## 10. Cost stress + sizing stress matrices (LOCKED at SEAL)

Cost-stress carried byte-equivalent from s11-d1 v1 sealed spec (which itself inherited byte-equivalent from S10-D2). The matrix is locked in the first IS diagnostic; deferral is forbidden.

### 10.1 Cost tiers (5-tier S0..S4; carried byte-equivalent from s11-d1 v1)

| Tier | `cost_scalar` | `slippage_scalar` | Note |
|---|---:|---:|---|
| `S0` | 0.0 | 0.0 | zero-cost ideal; tests if a profitable kernel exists |
| `S1` | 1.0 | 1.0 | baseline retail; commission + fees + slip @ 1.0x |
| `S2` | 1.5 | 1.5 | stressed retail; cost + slip @ 1.5x |
| `S3` | 2.0 | 2.0 | adversarial; cost + slip @ 2.0x |
| `S4` | 3.0 | 3.0 | extreme adversarial; cost + slip @ 3.0x |

### 10.2 Tick / contract specs (LOCKED at SEAL)

| Symbol | Tick size | Dollar per tick | Notes |
|---|---|---|---|
| `MNQ.c.0` | 0.25 index points | **$0.50 per contract** | Micro E-mini Nasdaq-100 (carried byte-equivalent from s11-d1 v1) |

### 10.3 Commission / fees / slippage defaults (proposed at PLAN; carried byte-equivalent from s11-d1 v1)

| Field | Value |
|---|---|
| Commission per round-trip (default) | `$0.74` |
| Fees per round-trip (default) | `$0.36` |
| Slippage entry / stop / exit ticks (default) | `1 / 1 / 1` |

### 10.4 Pre-registered S0 edge sign and magnitude (DRAFT-time decision; LOCKED at SEAL)

| Field | DRAFT-proposed value |
|---|---|
| Expected S0 net PnL sign | open question (no a-priori claim) |
| Acceptance threshold S0 net PnL | `> 0` after >= 100 trades |
| Acceptance threshold S1 net PnL | `> 0` (K1 / K2 fire if `<= 0` at S1 baseline) |
| Pre-registered max-drawdown tolerance | TBD at DRAFT; proposed K4 = 50% of `START_CASH_USD` (carried byte-equivalent from s11-d1 v1 K4 formula) |
| Pre-registered cost-stress survival | S0/S1/S2/S3/S4 all positive Sharpe (C5+) -> `ELIGIBLE_FOR_HUMAN_REVIEW`; S0/S1 positive but later tiers degrade > 50% -> K12 REJECT_FAST |

## 11. DR rules adapted for single-instrument MNQ.c.0 Donchian-15/8 (LOCKED at SEAL)

Carried byte-equivalent from s11-d1 v1 sealed spec section 11 with the load-bearing Donchian-15/8 substitution (which changes signal density, not DR semantics):

| Rule | Trigger | Severity | Notes |
|---|---|---|---|
| DR1 | `oos_rebalance_count < 36` (evaluated only at OOS phase) | `INCONCLUSIVE_HOLD` | unchanged |
| DR2 | `oos_metrics_degrade_materially_under_cost_stress` | `REJECT_FAST` | unchanged |
| DR3 | `zero_cost_only_survival` (S0 > 0 AND all S1..S4 <= 0) | `REJECT_FAST` | unchanged |
| DR4 | `oos_negative_while_is_positive_unexplained` | `REJECT_FAST` | unchanged; OOS-only |
| DR5 | `cost_stress_turns_edge_negative` (tier flip) | `REJECT_FAST` / `INCONCLUSIVE_HOLD` (carveout) | unchanged |
| DR6 | `post_warmup_sizing_ambiguity_or_invalid` (NARROWED post-warmup only) | `REJECT_FAST` | unchanged |
| DR7 | `missing_oos_or_date_window_evidence` | `INCONCLUSIVE_HOLD` | unchanged |
| DR8 | `live_or_order_routing_path_detected` at Initialize | `HARD_FAIL_VOIDED` | unchanged |
| **DR9** | **`mnq_c0_only_data_continuity_integrity_check`** | `INCONCLUSIVE_HOLD` | thresholds carried byte-equivalent (`0.95` / `0.30` / `5` / `5`); MNQ.c.0 already known DR9-clean per s10-d1 audit |
| DR10 | `turnover_cost_explosion` (`annual_turnover > 0.50` OR `S2 cost drag > 0.05`) | `REJECT_FAST` | unchanged; **higher prior probability of DR10 fire** than s11-d1 v1 because Donchian-15/8 raises annual turnover materially vs Donchian-55/20 |
| DR11 | NOT IN CHAIN | -- | F1 has no leverage cap; DR11 structurally absent |

DR precedence chain (LOCKED at SEAL): `DR7 -> DR1 -> DR9 -> DR10 -> DR6 -> DR4 -> DR2 -> DR3 -> DR5` (carried byte-equivalent from s11-d1 v1; DR11 omitted because F1 has no leverage cap).

**Turnover risk note carried explicit at PLAN:** the Donchian-15/8 choice that mitigates K9 risk materially RAISES DR10 turnover-cost-explosion risk. If S2 cost drag exceeds 5% of portfolio equity, DR10 fires REJECT_FAST. This is a known trade-off of the fresh-candidate K9-mitigation choice; the operator accepts this trade-off by authorizing this PLAN.

## 12. Sample-size / K9 rules (LOCKED at SEAL)

| Field | LOCKED value |
|---|---|
| K9 threshold | `total_closed_trades >= 100` over IS window |
| K9 threshold modification | FORBIDDEN (`no_k9_relaxation`; carried byte-equivalent from s11-d1 v1) |
| **Expected trade count over 4.6y IS for Donchian-15/8 bi-directional on MNQ.c.0** | **80-200 portfolio trades** (estimated; subject to Step 06 simulator at IS) |
| K9 risk | **borderline at lower bound** -- the lower estimate (80) is below K9; the central estimate (140) is comfortably above K9; the upper estimate (200) clears with margin |
| Comparison to s11-d1 v1 baseline (Donchian-55/20) | s11-d1 v1 expected ~25-50 trades (K9 fires); s12-d1 expects 80-200 trades (K9 borderline-to-clearing). This is the load-bearing structural improvement that motivates the fresh candidate. |
| Per-symbol minimum | NOT APPLICABLE for single-instrument; K9 IS the per-symbol minimum |
| If K9 fires anyway | `DR1 INCONCLUSIVE_HOLD` (not REJECT_FAST); candidate archived without parameter modification; the K9-mitigation hypothesis would be falsified by the diagnostic |
| If K9 clears but other K-gates fire | candidate handled per K-gate priority chain (section 16) |

## 13. Diversification expectations -- single-instrument scope (LOCKED at SEAL)

| Field | LOCKED value |
|---|---|
| A7 (`effective_independent_bets >= X`) | **NOT APPLICABLE** for single-instrument scope; trivially 1 by construction; A7 removed from acceptance gate set |
| K10 (`avg_pairwise_dependence`) | **NOT APPLICABLE** for single-instrument scope; no pairs exist; K10 removed from K-gate set |
| K6 (`per_symbol_observed_win_rate_dispersion`) | **NOT APPLICABLE** for single-instrument scope; no per-symbol dispersion to measure; K6 removed |
| Per-symbol contribution distribution | trivially 100% to MNQ.c.0; standalone risk profile IS the entire diagnostic surface |
| Diversification claim by this candidate | NONE; the candidate is explicitly a single-instrument diagnostic |
| Disclaimer carried byte-equivalent | "Diversification independence does NOT imply positive edge" (LESSON_B006_002_002) -- applies trivially because no diversification claim is made |

## 14. OOS-locking policy (LOCKED at SEAL; carried byte-equivalent)

| Policy | Status |
|---|---|
| OOS data (`2024-01-02 -> 2025-12-30`) shall not be inspected, computed against, simulated over, or queried in any form during the in-sample diagnostic phase | LOCKED |
| Post-OOS data (`2026-01-02 onward`) is informational only; no diagnostic uses it | LOCKED |
| OOS inspection requires a separately authorized turn after IS verdict `ELIGIBLE_FOR_OOS` plus explicit operator approval | LOCKED |
| Loader / validator / signal / simulator / aggregator modules shall structurally enforce IS-only computation | LOCKED (`oos_inspection_blocked_at_in_sample` invariant) |
| **OOS confirmation definition** (carried byte-equivalent from s11-d1 **rev2** at `c110fd4`, the CORRECTED magnitude-based form) | LOCKED at SEAL |

s11-d1 rev2 oos_confirmation_definition (carried byte-equivalent at SEAL):

> "OOS is CONFIRMED only iff ALL of: (a) C7 verdict is READY_FOR_LONGER_BACKTEST, (b) OOS closed_trades >= 100, (c) OOS sharpe > 0, (d) OOS expectancy > 0, (e) OOS trade_curve_maxdd_pct >= -30% (equivalently |trade_curve_maxdd_pct| <= 30%; i.e., the realized OOS drawdown shall not exceed 30% in magnitude), (f) all safety counters zero, (g) no-pyramid invariant held, (h) starting_cash invariant held."

The s12-d1 candidate adopts the rev2-corrected magnitude-based form directly at SEAL; the s11-d1 v1 sign/inequality typo is NOT re-introduced.

## 15. No-live / no-Strategy-Lab / no-brokerage policy (LOCKED at SEAL; carried byte-equivalent)

Inheritable invariants set, single-instrument adapted:

7 inherited B005_NNN framework:
- `no_live_trading`
- `no_strategy_lab_promotion`
- `no_review_queue_mutation`
- `no_brokerage_connection`
- `no_external_network` (runtime)
- `no_databento_at_runtime_only_at_optional_explicit_ingest_phase` (Step 02b is manifest cross-link only; no fresh fetch)
- `no_production_signal`

4 inherited B006_001:
- `no_strategy_optimization_authorized`
- `no_profitability_claim`
- `no_universe_membership_logic`
- `no_dr_redefinition_post_seal`

2 inherited B006_002 (F1 has no leverage cap; leverage-cap-specific invariants do NOT carry):
- `no_warmup_order_submission`
- `dr6_warmup_contamination_blocked`

5 inherited s10-d1-specific:
- `no_continuous_roll_stitch_modification_post_seal`
- `no_mcl_inclusion_under_long_history_scope`
- `no_intraday_schema_ingest_under_daily_only_design`
- `databento_api_key_read_from_env_only_never_logged_or_saved` (vacuously true since no fresh fetch)
- `no_pyramid_per_signal`

3 inherited s11-d1-specific (all carry byte-equivalent):
- `single_instrument_universe_NO_widening_post_seal`
- `no_substitution_of_any_symbol_into_this_universe_post_seal`
- `mnq_c0_csv_reuse_byte_equivalent_no_fresh_fetch`

4 NEW s12-d1-specific (proposed; LOCKED at SEAL):
- `donchian_15_8_locked_at_plan_no_retreat_to_55_20`
- `no_revision_of_s11_d1_sealed_artifacts`
- `s12_d1_does_not_supersede_s11_d1_v1_p1_p2_clarification_rev2`
- `mechanic_family_lock_at_plan_no_reopening_at_draft_or_seal`

Total invariants at SEAL: **25** (7 B005_NNN + 4 B006_001 + 2 B006_002 + 5 s10-d1 + 3 s11-d1 + 4 s12-d1; no DR11; no C4 invariants).

Status surface (permanent for this candidate, independent of any future verdict):

| Field | Value |
|---|---|
| Trading | `PAUSED` |
| Live mode | `BLOCKED_AT_6_GATES` |
| FRC | `NEVER_GRANTED` |
| `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` advisory label | permanent |
| Six live-trading gates remain BLOCKED regardless of any verdict | YES |

## 16. Reject-fast criteria (LOCKED at SEAL; carried byte-equivalent + s12-d1-specific extensions)

The candidate is REJECTED FAST if ANY of:

- **RF1** Any DR rule fires `REJECT_FAST` (DR2 / DR3 / DR4 / DR5 / DR6 / DR10)
- **RF2** DR9 `mnq_c0_only_data_continuity_integrity_failure` AND > 5 violations (extremely unlikely given MNQ-clean-leg)
- **RF3** DR6 post-warmup invalid-sizing event count > 0 (single event = REJECT_FAST per LESSON_B006_002_002)
- **RF4** Any forbidden-verdict-token in runner output
- **RF5** Runner attempts `SetLiveMode` / `SetBrokerageModel` / `DeployAlgorithm` / unauthorized network call / unauthorized Databento call at runtime
- **RF6** Any order-submit attempt while in warmup window
- **RF7** Runner mutates any s11-d1 v1 / P1 / P2 / clarification / rev2 / s10-d2 / s10-d1 / s9 / s7-d1 / B006_NNN / T8 / s12-d1 sealed artifact (byte-shift)
- **RF8** Runner makes a Databento API call at runtime (controller-side)
- **RF9** Runner caches `.dbn.zst` files anywhere
- **RF10** Runner accesses `DATABENTO_API_KEY` at runtime
- **RF11** Track silently re-introduces a filter, regime gate, or selection rule
- **RF12** Pyramid mechanism re-introduced in code (multi-contract pyramid)
- **RF13** Donchian-N or Donchian-M silently switched from the LOCKED 15/8 post-SEAL
- **RF14** Universe widening or symbol substitution attempted at any phase
- **RF15** Track depends on a survivorship-cherry-pick rule
- **RF16 (s12-d1-specific)** Any retroactive re-anchoring or modification of s11-d1 v1 / P1 / P2 / clarification / rev2 caused by this candidate

K-gates carried byte-equivalent from s11-d1 v1 with single-instrument simplifications:

- **K1** `sharpe_proxy_per_trade_below_zero_at_S1`
- **K2** `expectancy_per_trade_dollars_nonpositive_at_S1`
- **K4** `trade_curve_max_drawdown_above_threshold` (proposed K4 = 50% of `START_CASH_USD`; carried byte-equivalent from s11-d1 v1 K4 formula)
- **K6** NOT APPLICABLE for single-instrument
- **K7** `silent_filter_introduction_after_lock`
- **K8** `runtime_safety_invariant_false`
- **K9** `closed_trades_below_100` (K9 risk borderline at lower bound; see section 12)
- **K10** NOT APPLICABLE for single-instrument
- **K11** NOT APPLICABLE (no leverage cap for F1)
- **K12** composite cost-stress fail (DR2 + DR3)

K-gate firing priority order: `K8 > K12 > K7 > K9 > K1/K2/K4 > A-gates > ELIGIBLE_FOR_OOS`.

## 17. Phase ladder (each phase separately authorized)

| # | Phase | Status (this turn) | Authorization template |
|---|---|---|---|
| 0 | s11-d1 v1 / P1 / P2 / clarification / rev2 sealed | inherited (byte-stable; READ-ONLY) | -- |
| 1 | s12-d1 Tier-N spec PLAN (this document) | **COMPLETE THIS TURN** | -- |
| 2 | s12-d1 Tier-N spec DRAFT | NOT AUTHORIZED | `Authorize s12 D1 MNQ.c.0 single-instrument Donchian-15/8 Tier-N spec DRAFT` |
| 3 | s12-d1 Tier-N spec SEAL | NOT AUTHORIZED | `Authorize s12 D1 MNQ.c.0 single-instrument Donchian-15/8 Tier-N spec SEAL` |
| 4 | s12-d1 Step 02b -- manifest cross-link (no fresh Databento fetch) | NOT AUTHORIZED | `Authorize s12 D1 MNQ.c.0 Step 02b manifest cross-link only` |
| 5 | s12-d1 Step 02c -- MNQ-only audit re-confirmation | NOT AUTHORIZED | `Authorize s12 D1 MNQ.c.0 Step 02c raw-data audit only` |
| 6 | s12-d1 P3 BUILD (runner harness + drivers + tests) | NOT AUTHORIZED | `Authorize s12 D1 P3 BUILD only` |
| 7 | s12-d1 P4 synthetic smoke | NOT AUTHORIZED | `Authorize s12 D1 P4 synthetic smoke only` |
| 8 | s12-d1 P6 IS diagnostic | NOT AUTHORIZED | `Authorize s12 D1 P6 IS diagnostic only` |
| 9 | s12-d1 P6.5 cost-stress matrix | NOT AUTHORIZED | `Authorize s12 D1 P6.5 cost-stress matrix only` |
| 10 | s12-d1 P7 decision memo | NOT AUTHORIZED | `Authorize s12 D1 P7 decision memo only` |
| 11 | s12-d1 P10 OOS gate | NOT AUTHORIZED | `Authorize s12 D1 P10 OOS gate only` |
| 12 | s12-d1 P11 lifecycle decision | NOT AUTHORIZED | `Authorize s12 D1 P11 lifecycle decision only` |

This plan authors ONLY phase 1. Every subsequent phase requires its own separately authorized turn. **No Databento call is required at any phase** because the existing MNQ.c.0 CSV (sha-pinned `8b7b832c...fa23e`) is reused byte-equivalent.

## 18. Boundaries held this PLAN turn

| Boundary | Status |
|---|---|
| PLAN only (no spec DRAFT, no SEAL, no BUILD, no fetch) | met |
| No strategy code | met |
| No backtest | met |
| No simulator run | met |
| No signal computation | met |
| No data fetch | met |
| No Databento call | met |
| No `DATABENTO_API_KEY` access | met |
| No yfinance / Yahoo Finance call | met |
| No QC / LEAN call | met |
| No network IO | met |
| No live trading | met |
| No candidate promotion | met |
| **No modification of s11-d1 v1 / P1 / P2 / clarification / rev2 sealed artifacts** | met -- byte-stable on disk |
| No modification of s10-d2 / s10-d1 / s9 / s7-d1 / B006_NNN / T8 sealed artifacts | met -- byte-stable |
| No modification of ORB branch artifacts | met |
| No modification of CLAUDE.md / docs/decisions.md / RUNBOOK / pipeline_manifest / .gitignore | met |
| No modification or staging of `brain_memory/projects/trading_bot/lessons.md` (dirty + unstaged from prior session; left untouched) | met |
| No mutation of `review_queue.json` | met |
| No mutation of production `idea_memory` | met |
| No profitability claim | met |
| No deletion of the orphaned s11-d1 DRAFT at `74e254f` | met -- left in place untouched (would require separate authorization to delete) |
| Trading status | `PAUSED` |
| Live status | `BLOCKED_AT_6_GATES` |
| FRC | `NEVER_GRANTED` |
| `no_strategy_optimization_authorized` | TRUE |

## 19. Files written this PLAN turn (this document scope)

| File | Purpose |
|---|---|
| `docs/s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_tier_n_spec_plan.md` | This Tier-N spec PLAN (the plan to DRAFT-to-SEAL; no spec is sealed by this plan) |

No other repository file is modified by this plan. The brain_memory `lessons.md` dirty + unstaged state from prior controller-session appends remains untouched.

## 20. Validation gates and HALT conditions for this plan

Validation gates the plan-authoring turn satisfies:

V1. ASCII-only.
V2. Numbered sections in monotonic order (1..22).
V3. No execution language.
V4. No self-authorization (this plan does NOT authorize the Tier-N spec to be DRAFTed or SEALed).
V5. No code modification.
V6. No backtest / simulator / signal computation.
V7. No data fetch / Databento call / `DATABENTO_API_KEY` access.
V8. No network IO.
V9. No live trading.
V10. No prior-phase artifact modification (s11-d1 v1 / P1 / P2 / clarification / rev2 / s10-d2 / s10-d1 / s9 / s7-d1 / B006_NNN / T8 all byte-stable).
V11. The committed plan file is the ONLY new file changed in this turn's commit.
V12. The brain_memory dirty `lessons.md` remains UNSTAGED and UNTOUCHED.
V13. The candidate is structurally single-instrument; A7 / K10 / K6 are explicitly NOT APPLICABLE.
V14. The candidate is NOT a revision of any parked or sealed predecessor; it is a fresh `candidate_record_id` per s11-d1 v1's own "REQUIRES FRESH CANDIDATE_RECORD_ID" clause.
V15. The candidate's universe is LOCKED at `{MNQ.c.0}` only; substitution / widening FORBIDDEN at any future phase.
V16. Donchian-15/8 is LOCKED AT PLAN (load-bearing departure from s11-d1 v1's 55/20); the DRAFT turn shall NOT reopen this parameter pair.
V17. Mechanic family is LOCKED AT PLAN (F1); the DRAFT turn shall NOT reopen the F1/F2/F3/F4 selection menu.

HALT conditions:

H1. If any V-gate fails, the turn HALTs.
H2. If the pre-stage git index is non-empty, the turn HALTs and remediates.
H3. If the staged file count is anything other than 1, the turn HALTs.
H4. If the staged file is anything other than `docs/s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_tier_n_spec_plan.md`, the turn HALTs.
H5. If `lessons.md` is accidentally staged, the turn HALTs and `git restore --staged brain_memory/projects/trading_bot/lessons.md` before retrying.
H6. If any s11-d1 sealed artifact (v1 / P1 / P2 / clarification / rev2) shows as modified in `git status`, the turn HALTs and remediates.

## 21. Next-step authorization scope

The next operator authorization in the established controller-session pattern shall use one of these scopes:

- **"Authorize s12 D1 MNQ.c.0 single-instrument Donchian-15/8 Tier-N spec DRAFT"** -- begin the DRAFT turn that enumerates DRAFT ambiguities for the parameters NOT locked at PLAN (ATR window, ATR multiplier, per-trade risk %, START_CASH, K4 threshold, output schema name, etc.) and recommends DRAFT-default-primaries.
- **"Authorize alternative track selection plan revision only"** -- reject the s12-d1 fresh-candidate path and ask for a different alternative from the predecessor selection plan at `556ab3f`.
- **"Authorize cross-domain pivot only"** -- pivot to a different project entirely.
- **"Defer / Pause trading-bot track"** -- hold this plan on file without authorizing the DRAFT turn at this time.

This plan is the source of truth for the s12-d1 MNQ.c.0 single-instrument Donchian-15/8 fresh candidate's intended Tier-N spec scope. Future DRAFTs, SEALs, or BUILDs that contradict this plan require either a fresh plan revision or an out-of-band justification.

## 22. No-live status carried forward

| Field | Value |
|---|---|
| Trading | `PAUSED` |
| Live mode | `BLOCKED_AT_6_GATES` |
| FRC | `NEVER_GRANTED` |
| Six live-trading gates remain BLOCKED regardless of any future verdict | TRUE |
| `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` advisory label applies to any candidate descended from this plan | TRUE |
| `no_strategy_optimization_authorized` | TRUE |
| s11-d1 v1 / P1 / P2 / clarification / rev2 byte-stable | TRUE |

----

End of plan. Plan-authoring turn only. No code. No backtest. No simulator. No signal. No data fetch. No yfinance. No Yahoo Finance. No Databento. No DATABENTO_API_KEY access. No QC. No LEAN. No brokerage. No real order. No paper order. No Strategy Lab promotion. No review_queue mutation. No production idea_memory mutation. No ORB branch mutation. No lessons.md modification or staging. No live trading. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES.
