# s13 D1 MNQ.c.0 Single-Instrument RSI(2) Bi-Directional Databento Long-History Tier-N Specification Plan

Status: PLAN_ONLY (no code written, no spec sealed, no data fetched by this plan; the next step is a separate operator authorization to DRAFT the Tier-N spec).

Authored: 2026-05-27
Authorization phrase: "Authorize s13 D1 MNQ.c.0 single-instrument RSI(2) bi-directional Tier-N spec plan only."

Selection-plan source: `docs/next_research_track_selection_plan_after_s12_d1_park.md` (committed at `0e3f9d4`; T1 recommended at 41/50)

Predecessor parked candidates (READ-ONLY; not modified by this plan):
- `s12-d1-mnq-c0-single-instrument-donchian-15-8-databento-long-history` parked `PARKED_SAFE_BUT_INSUFFICIENT_SAMPLE_AT_IS` at commit `ecbd001` (P11 park memo seal `b9722d42...`)
- `s11-d1-mnq-c0-single-instrument-databento-long-history` sealed at commit `9c63088` (v1) + rev2 at `c110fd4`
- `s9-rsi-2-etf-proxy` parked SAFE_BUT_NOT_MONEY_PROVEN (negative S0 edge on SPY/TLT/GLD/USO long-only)
- `s10-d1-cross-asset-trend-or-meanrev-mnq-mgc` parked INCONCLUSIVE_HOLD (`1a9acec`)
- `s10-d2-cross-asset-donchian` parked PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED (`23c7164`)
- B005_NNN / B006_001 / B006_002 / s7-d1 / s8-d1 / T8 / NKE archive byte-stable

Audit-clean data anchor (MNQ.c.0; reused byte-equivalent): `data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_c_0_ohlcv_1d_20190513_20251230.csv` (sha256 `8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e`; 2066 rows; 2019-05-13 -> 2025-12-29)

HARD BOUNDARIES (held by this plan). PLAN only. No DRAFT. No SEAL. No code. No backtest. No simulator. No signal computation. No data fetch. No yfinance / Yahoo Finance call. No Databento call. No `DATABENTO_API_KEY` access. No QC / LEAN call. No network IO. No `review_queue.json` mutation. No production `idea_memory` mutation. No Strategy Lab run. No candidate promotion. **No s12-d1 revival.** **No `_revN_` revision of s12-d1 authored by this plan.** No s11-d1 v1 / P1 / P2 / clarification / rev2 sealed-artifact modification. No s12-d1 SEAL `66bbbd1` / P1 `d8bd359` / P2 `0b8d948` / P3 `91e740e` / P4 `ea78845` / P6 IS `9241ed6` / P11 `ecbd001` sealed-artifact modification. No s10-d2 / s10-d1 / s9 / s7-d1 / B005_NNN / B006_NNN / T8 sealed-artifact modification. No ORB branch mutation. No Step 30 cost constant mutation. No CLAUDE.md modification. No RUNBOOK modification. No `pipeline_manifest` modification. No `.gitignore` modification. **No `brain_memory/projects/trading_bot/lessons.md` modification or staging.** No branch change. No git push. No live trading. No profitability claim. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES. FRC `NEVER_GRANTED`.

----

## 1. Purpose

Author a sealed plan-to-spec for the first Tier-N specification of a fresh single-instrument candidate on MNQ.c.0 Databento daily-bar data using the **Connors RSI(2) bi-directional mean-reversion mechanic** (F3 family). The fresh candidate is authored per the selection-plan revision at `0e3f9d4` (T1 recommended at 41/50; the only track that clears K9 at BOTH IS AND OOS under the new K9-reachability discipline).

The plan does NOT seal the spec; it authors the plan-to-DRAFT that will inform a subsequent operator-authorized DRAFT turn. No code, no data fetch, no Databento call is performed by this plan. The s12-d1 candidate (Donchian-15/8 single-instrument) remains terminally parked under `PARKED_SAFE_BUT_INSUFFICIENT_SAMPLE_AT_IS` and is NOT revived by this plan.

## 2. Candidate identification

| Field | Proposed value (subject to operator confirmation at DRAFT/SEAL) |
|---|---|
| `candidate_record_id` | **`s13-d1-mnq-c0-single-instrument-rsi-2-bi-directional-databento-long-history`** |
| `candidate_family` | **F3 RSI mean-reversion bi-directional** (LOCKED at PLAN -- defining mechanic of the fresh candidate) |
| `is_a_trade_candidate` | true |
| `is_a_single_instrument_candidate` | **true** (load-bearing structural property) |
| `is_a_s12_d1_revision` | **false** (per s12-d1 terminal park; s12-d1 mechanic was F1 trend-no-pyramid Donchian-15/8; F3 is structurally orthogonal) |
| `is_a_s12_d1_revN_revision` | **false** (s12-d1 revival forbidden per its terminal park) |
| `is_a_s11_d1_revision` | false |
| `is_a_s10_d2_revision` | false |
| `is_a_s10_d1_revision` | false |
| `is_a_s9_revision` | **false** (s9 was LONG-ONLY RSI-2 on SPY/TLT/GLD/USO 4-ETF basket; s13-d1 is BI-DIRECTIONAL on single MNQ.c.0 futures contract; different universe + different cost surface + different signal direction) |
| `is_a_s7_d1_revision` | false |
| `is_a_b006_NNN_extension` | false |
| `predecessor_lineage_references_read_only` | `s12_d1_park`, `s11_d1_v1_rev2_chain`, `s10_d2_park`, `s10_d1_park`, `s9_rsi2_etf_proxy_park`, `s7_d1_park`, `b006_001_002_archival`, `t8_etf_proxy_family_park`, `phase_2_safety_contract_template_C1_C8` |
| `diagnostic_only` | true |
| `not_promotable_via_this_diagnostic` | true |
| `default_advisory_label` | `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` |
| Selection-plan score | 41 / 50 (highest among T1-T4 alternatives) |
| K9-reachability discipline applied at PLAN time (NEW framework requirement) | **TRUE** |
| REC1 OOS-K9-reachability discipline (carried byte-equivalent from s12-d1 chain as new framework standard) | **TRUE** |

## 3. Universe (proposed; LOCKED at SEAL)

| Field | Proposed value (LOCKED at SEAL) |
|---|---|
| Universe type | `single_fixed_instrument_continuous_micro_futures` |
| Symbol 1 (only symbol) | **`MNQ.c.0`** (Micro E-mini Nasdaq-100, continuous front-month) |
| `AddUniverse` calls | **0** (structurally absent) |
| `removed_from_universe` events | **0** (structurally absent) |
| Symbol count | exactly 1 |
| Symbol substitution clause at later phases | FORBIDDEN |
| Universe widening at later phases | FORBIDDEN (any wider basket requires fresh `candidate_record_id`) |
| Common-history start (verified by s10-d1 audit + s12-d1 chain) | **2019-05-13** |
| Diversification claim | NONE (single-instrument; explicit first-principles justification) |
| Diversification metrics A7 / K10 / K6 | **NOT APPLICABLE** for single-instrument |

## 4. Data assumptions (proposed; LOCKED at SEAL)

| Field | Proposed value (LOCKED at SEAL) |
|---|---|
| Vendor | **Databento Historical API** (vendor-level; controller-side never calls) |
| Dataset | **`GLBX.MDP3`** |
| Schema | **`ohlcv-1d`** |
| `stype_in` | **`continuous`** |
| Symbol requested | `["MNQ.c.0"]` |
| **Re-use of existing audit-clean CSV** | **TRUE** -- `data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_c_0_ohlcv_1d_20190513_20251230.csv` (sha256 `8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e`) reused byte-equivalent. **ZERO new Databento call required.** |
| Step 02b for this candidate | manifest cross-link only (no fresh fetch) |
| API key handling at any phase | NOT REQUIRED |
| Controller-side Databento call at any phase | LOCKED OFF |

## 5. Schema (LOCKED at SEAL)

| Field | LOCKED value |
|---|---|
| Schema | `ohlcv-1d` |
| Fields | `ts_event`, `open`, `high`, `low`, `close`, `volume` |
| Intraday schemas | OUT OF SCOPE for this candidate's Tier-N |

## 6. stype_in (LOCKED at SEAL)

| Field | LOCKED value |
|---|---|
| `stype_in` | `continuous` |
| `no_continuous_roll_stitch_modification_post_seal` invariant | TRUE |

## 7. IS / OOS windows (LOCKED at SEAL)

Carried byte-equivalent from s11-d1 / s12-d1 chain; the underlying CSV already covers both windows.

| Field | LOCKED value |
|---|---|
| **IS window start** | **`2019-05-13`** |
| **IS window end** | **`2023-12-29`** |
| IS window length | ~4.6 years |
| MNQ.c.0 IS-window row count (audit-confirmed) | **1,443** |
| **OOS window start (never inspected at IS)** | **`2024-01-02`** |
| **OOS window end (never inspected at IS)** | **`2025-12-30`** |
| OOS window length | ~2.0 years |
| MNQ.c.0 OOS-window row count (structural only) | **622** |
| OOS inspection at IS-phase | FORBIDDEN (`oos_inspection_blocked_at_in_sample` invariant) |

## 8. Strategy mechanic family LOCKED at PLAN: F3 Connors RSI(2) bi-directional

Unlike the s11-d1 PLAN (which deferred mechanic family selection to its DRAFT turn) and like the s12-d1 PLAN (which locked F1 Donchian-15/8 at PLAN), this s13-d1 PLAN locks the mechanic family AT PLAN. The candidate's load-bearing structural property is "Connors RSI(2) bi-directional mean-reversion on MNQ.c.0 single-instrument" — changing mechanic family would defeat the fresh-candidate justification.

### 8.1 Mechanic primitives (LOCKED at PLAN)

| Field | LOCKED value at PLAN |
|---|---|
| Mechanic family | **F3 RSI(2) bi-directional mean-reversion** |
| RSI computation | **Connors RSI(2)** (2-period RSI using Wilder smoothing on close-to-close returns) |
| **RSI long entry threshold** | **`< 10`** (oversold) |
| **RSI long exit threshold** | **`> 50`** (mean-reversion complete) |
| **RSI short entry threshold** | **`> 90`** (overbought; bi-directional symmetric) |
| **RSI short exit threshold** | **`< 50`** (mean-reversion complete) |
| Signal direction | **bi-directional** (long+short symmetric thresholds) |
| Pyramid | NONE / `max_units_per_market = 1` |
| Stop method | ATR-based 2N stop (carried byte-equivalent from s12-d1 v1 / s11-d1 v1 chain) |
| Risk method | per-trade risk percentage of portfolio equity, sized via ATR (carried byte-equivalent) |

### 8.2 Why s13-d1 is NOT a rescue of s9 (first-principles burden)

| s9 falsification feature | s13-d1 treatment |
|---|---|
| Universe = SPY/TLT/GLD/USO (4-ETF basket; equity-class ETFs) | Universe = `{MNQ.c.0}` (single futures; micro-Nasdaq-100 contract; **different asset class**) |
| Long-only | **Bi-directional** (long when RSI<10 AND short when RSI>90); structural asymmetry break |
| Cost surface: per-share commission + bps slippage on ETFs | Cost surface: **per-contract commission + tick slippage on micro-futures** (carried byte-equivalent from s12-d1) |
| Negative S0 edge over 414 trades | S0 edge sign on s13-d1 is an **open question**; no a-priori claim |
| Falsification cause was instrument-specific cost/edge interaction on equity ETFs, NOT the RSI(2) signal generator itself | s13-d1 tests the RSI(2) signal on a structurally different instrument |

**First-principles claim:** the s9 falsification does NOT transfer to s13-d1 because (a) the asset class differs (futures vs equity ETFs), (b) the cost surface differs (per-contract vs per-share + bps), (c) the signal direction differs (bi-directional vs long-only), and (d) the universe differs (single MNQ vs 4-ETF basket). The diagnostic question s13-d1 asks is structurally fresh.

### 8.3 Why s13-d1 is NOT a rescue of s12-d1

| s12-d1 falsification feature | s13-d1 treatment |
|---|---|
| Mechanic family F1 (Donchian-15/8 trend, no pyramid, ATR-stop) | Mechanic family **F3 (RSI mean-reversion bi-directional, no pyramid, ATR-stop)** — STRUCTURALLY ORTHOGONAL (mean-reversion is the OPPOSITE direction of trend) |
| K9-mitigation hypothesis (DRAFT 80-200 IS trades; actual 48) | s13-d1 expects 230-300 IS trades + 100-130 OOS trades (substantially above K9=100 at both windows) |
| Donchian-15/8 single-instrument signal density ~10/y | RSI(2) bi-directional ~50-65/y (~5-6x higher signal density) |
| Single-instrument MNQ.c.0 | Single-instrument MNQ.c.0 (same universe; different mechanic) |

**First-principles claim:** s12-d1 falsified Donchian-15/8 mechanic on MNQ.c.0 with structurally-low signal density (~10/y). s13-d1 tests the inverse mechanic (mean-reversion) which produces structurally-higher signal density (~50-65/y), independent of any Donchian falsification. The two candidates are orthogonal.

## 9. K9-reachability table at PLAN time (NEW framework discipline; carried byte-equivalent from selection-plan revision)

Per the K9-reachability discipline introduced in `docs/next_research_track_selection_plan_after_s12_d1_park.md` (commit `0e3f9d4` §3), every Tier-N spec PLAN shall include an explicit K9-reachability calculation for BOTH IS and OOS windows.

### 9.1 Required trade-count thresholds

| Window | Length (y) | Required closed_trades/year for K9=100 | Status threshold |
|---|---:|---|---|
| IS (s11-d1 lineage carried) | 4.6 | **>= 21.74 trades/y** | K9_IS_REACHABLE if true |
| **OOS (s11-d1 lineage carried)** | **2.0** | **>= 50.00 trades/y** (BINDING) | **K9_OOS_REACHABLE if true** |

### 9.2 Expected trade count for s13-d1 RSI(2) bi-directional on MNQ.c.0

Estimated signal density basis (DRAFT-time; subject to P6 IS confirmation):

- **Connors RSI(2) signal frequency on equity-index futures (daily bars):** historically ~50-65 trades/year per symbol when bi-directional (long thresholds RSI<10 + short thresholds RSI>90 both fire)
- This estimate is informed by: (a) Larry Connors' published RSI(2) research suggesting 50-100 entries/year on liquid equity indices, (b) bi-directional symmetric thresholds typically each contribute roughly equally to total trade count, (c) MNQ.c.0 vol profile is broadly similar to NQ.c.0 (scaled-down notional)

### 9.3 K9-reachability assessment for s13-d1

| Window | Required trades/y | Expected trades/y (low / central / high) | Expected total trades | K9 status |
|---|---|---|---|---|
| IS (4.6y) | >= 21.74 | 50 / 57 / 65 | 230 / 262 / 300 | **CLEARS K9 WITH MARGIN** (2.3-3.0x the floor) |
| OOS (2.0y) | >= 50.00 | 50 / 57 / 65 | 100 / 114 / 130 | **CLEARS K9** (1.0-1.3x the floor at the lower bound; BORDERLINE-TO-CLEARING) |

### 9.4 K9-reachability disclosure

- **s13-d1 is the first Tier-N spec PLAN to explicitly satisfy the K9-reachability discipline AT PLAN time.**
- IS K9 reachable with significant margin.
- **OOS K9 reachable at the lower bound (~50 trades/year)** but with thin margin. If P6 IS reveals actual trade rate below 50/y, OOS K9 would fire under the K9-reachability discipline framework.
- The OOS K9 risk is materially LOWER than s12-d1's structural unreachability (s12-d1 expected ~21 OOS trades at observed IS rate; s13-d1 expects ~100-130 OOS trades at DRAFT band).
- **REC1-equivalent disclosure for s13-d1:** if observed IS rate falls below 25/year on RSI(2) bi-directional, OOS K9 unreachability becomes structurally probable. The expected band is 50-65/y; lower-bound observation below 25/y would require parking.

### 9.5 Mitigation options NOT pre-approved by this plan

The following mitigations are explicitly NOT authorized by this PLAN (per `no_strategy_optimization_authorized` invariant):

- Tighten RSI thresholds (e.g., `< 5` for long entry instead of `< 10`) — would alter signal density; requires fresh `candidate_record_id`
- Widen RSI thresholds (e.g., `< 15` for long entry) — same restriction
- Switch RSI period (e.g., RSI(3) or RSI(4)) — would alter signal density; requires fresh `candidate_record_id`
- Add filter (e.g., trend regime overlay) — would introduce a filter; forbidden post-SEAL
- Convert to long-only or short-only — would defeat bi-directional design; structurally different mechanic

## 10. Locked parameter values (DEFERRED to DRAFT/SEAL turns except where LOCKED at PLAN)

| Class | LOCKED at PLAN | Locked at SEAL | Notes |
|---|---|---|---|
| `candidate_record_id` | **`s13-d1-mnq-c0-single-instrument-rsi-2-bi-directional-databento-long-history`** | -- | LOCKED at PLAN |
| Universe | `{MNQ.c.0}` only | yes | LOCKED at PLAN |
| Mechanic family | F3 RSI(2) bi-directional mean-reversion | -- | LOCKED at PLAN |
| RSI period | **2 (Connors classic)** | yes | LOCKED at PLAN |
| RSI long entry threshold | **`< 10`** | yes | LOCKED at PLAN |
| RSI long exit threshold | **`> 50`** | yes | LOCKED at PLAN |
| RSI short entry threshold | **`> 90`** | yes | LOCKED at PLAN |
| RSI short exit threshold | **`< 50`** | yes | LOCKED at PLAN |
| Signal direction | Long+Short bi-directional | yes | LOCKED at PLAN |
| Pyramid mechanism | NONE / `max_units_per_market = 1` | yes | LOCKED at PLAN |
| `IS_WINDOW_START` | -- | yes | `2019-05-13` (carried) |
| `IS_WINDOW_END` | -- | yes | `2023-12-29` (carried) |
| `OOS_WINDOW_START` | -- | yes | `2024-01-02` (carried; never inspected) |
| `OOS_WINDOW_END` | -- | yes | `2025-12-30` (carried; never inspected) |
| ATR stop window P | -- | yes | TBD at DRAFT; proposed 20 (Wilder; carried byte-equivalent) |
| ATR stop multiplier K | -- | yes | TBD at DRAFT; proposed 2.0 (carried byte-equivalent) |
| Per-trade risk percentage | -- | yes | TBD at DRAFT; proposed 1.0% portfolio equity (carried byte-equivalent) |
| `START_CASH_USD` | -- | yes | TBD at DRAFT; proposed `100000` (s12-d1 DA4=B carried; operator may revisit) |
| `WARMUP_DAYS` | -- | yes | TBD at DRAFT; proposed `MAX(longest_lookback, 220)` -> 220 |
| K4 max-drawdown threshold | -- | yes | TBD at DRAFT; proposed 50% magnitude (carried byte-equivalent) |
| K9 minimum trade-count threshold | LOCKED at `>= 100` | -- | non-negotiable per `no_k9_relaxation` |
| Cost-stress tier set | -- | yes | TBD at DRAFT; proposed 5-tier S0..S4 (carried byte-equivalent) |
| Output schema name | -- | yes | TBD at DRAFT; proposed `sparta.s13.d1.mnq_c0.rsi_2_bidir.diagnostic_run_report.v1` |
| DR9 thresholds | -- | yes | carried byte-equivalent (`0.95 / 0.30 / 5 / 5`) |
| DR10 thresholds | -- | yes | carried byte-equivalent (`annual_turnover > 0.50 OR S2 cost drag > 0.05`) |

## 11. Cost stress + sizing stress matrices (LOCKED at SEAL)

Cost-stress matrix carried byte-equivalent from s12-d1 chain (5-tier S0..S4 with scalars `0.0/1.0/1.5/2.0/3.0`).

| Tier | `cost_scalar` | `slippage_scalar` | Note |
|---|---:|---:|---|
| `S0` | 0.0 | 0.0 | zero-cost ideal |
| `S1` | 1.0 | 1.0 | baseline retail (DEFAULT) |
| `S2` | 1.5 | 1.5 | stressed retail |
| `S3` | 2.0 | 2.0 | adversarial |
| `S4` | 3.0 | 3.0 | extreme adversarial |

### 11.1 Tick / contract specs (LOCKED at SEAL)

| Symbol | Tick size | Dollar per tick |
|---|---|---|
| `MNQ.c.0` | 0.25 index points | **$0.50 per contract** |

### 11.2 Pre-registered S0 edge sign and magnitude (DRAFT-time)

| Field | DRAFT-proposed value |
|---|---|
| Expected S0 net PnL sign | **open question (no a-priori claim)** -- s9's negative S0 finding on long-only ETF-proxy does NOT determine s13-d1 bi-directional MNQ futures result by first-principles |
| Acceptance threshold S0 net PnL | `> 0` after >= 100 trades (K9 clears reliably for s13-d1) |
| Acceptance threshold S1 net PnL | `> 0` (K1 / K2 fire if `<= 0`) |
| Pre-registered max-drawdown tolerance | TBD at DRAFT; proposed K4 = 50% (carried byte-equivalent) |
| Pre-registered cost-stress survival | S0/S1/S2/S3/S4 all positive Sharpe -> `ELIGIBLE_FOR_HUMAN_REVIEW`; degradation > 50% -> K12 REJECT_FAST |
| **DR10 turnover-cost-explosion risk** | **ELEVATED vs s11-d1 v1 baseline** (RSI(2) ~50-65 trades/year is ~5-10x s11-d1 v1's ~5-10 trades/year baseline); annual turnover scales accordingly; S2 cost drag at higher trade frequency is the binding DR10 test |

### 11.3 DR10 risk note explicit at PLAN

The s13-d1 RSI(2) bi-directional mechanic produces ~50-65 trades/year on MNQ.c.0 -- substantially higher than s11-d1 v1's ~5-10/y Donchian-55/20 baseline. Annual turnover scales with trade frequency; S2 cost drag (`>0.05` triggers DR10 REJECT_FAST) is the binding cost-stress test for s13-d1.

The DRAFT-level mitigation lever for DR10 (NOT a DR-threshold change, which is forbidden per `no_dr_redefinition_post_seal`) is `START_CASH_USD` revision (analogous to s12-d1's DA4=B mitigation; raising START_CASH halves per-dollar commission/slip pressure). Operator may consider DA4=B ($100k start cash byte-equivalent to s12-d1) at SEAL.

## 12. DR rules adapted for single-instrument F3 RSI(2) bi-directional (LOCKED at SEAL)

Carried byte-equivalent from s12-d1 chain section 11 with F3-specific notes:

| Rule | Trigger | Severity | F3 RSI(2) bi-directional note |
|---|---|---|---|
| DR1 | `oos_rebalance_count < 36` (OOS phase only) | `INCONCLUSIVE_HOLD` | OOS-only |
| DR2 | `oos_metrics_degrade_materially_under_cost_stress` | `REJECT_FAST` | unchanged |
| DR3 | `zero_cost_only_survival` (S0 > 0 AND all S1..S4 <= 0) | `REJECT_FAST` | **HIGHER prior probability for s13-d1** (RSI mean-reversion mechanics historically show DR3-style edge erosion under cost stress; s9 lineage observation) |
| DR4 | `oos_negative_while_is_positive_unexplained` | `REJECT_FAST` | OOS-only |
| DR5 | `cost_stress_turns_edge_negative` (tier flip) | `REJECT_FAST` / `INCONCLUSIVE_HOLD` carveout | unchanged; binding for high-frequency mechanics |
| DR6 | `post_warmup_sizing_ambiguity_or_invalid` | `REJECT_FAST` | unchanged |
| DR7 | `missing_oos_or_date_window_evidence` | `INCONCLUSIVE_HOLD` | unchanged |
| DR8 | `live_or_order_routing_path_detected` at Initialize | `HARD_FAIL_VOIDED` | unchanged |
| DR9 | `mnq_c0_only_data_continuity_integrity_check` | `INCONCLUSIVE_HOLD` | MNQ-clean per s10-d1 audit; thresholds byte-equivalent |
| **DR10** | `turnover_cost_explosion` (`annual_turnover > 0.50` OR `S2 cost drag > 0.05`) | `REJECT_FAST` | **ELEVATED prior probability** vs s11-d1 v1 / s12-d1; binding for s13-d1's higher-frequency mechanic |
| DR11 | NOT IN CHAIN | -- | F3 has no leverage cap; DR11 structurally absent |

DR precedence chain (LOCKED at SEAL): `DR7 -> DR1 -> DR9 -> DR10 -> DR6 -> DR4 -> DR2 -> DR3 -> DR5` (carried byte-equivalent from s12-d1 chain).

**DR3 + DR5 are the binding falsification candidates for s13-d1.** RSI mean-reversion historically shows S0-positive but S1+ cost-erosion (s9 lineage); if observed at s13-d1, DR3 fires REJECT_FAST. This is the load-bearing first-principles test of "does the s9 falsification transfer to MNQ futures with bi-directional thresholds?"

## 13. Sample-size / K9 rules (LOCKED at SEAL)

| Field | LOCKED value |
|---|---|
| K9 threshold | `total_closed_trades >= 100` over IS window |
| K9 threshold modification | FORBIDDEN |
| Expected IS trade count (4.6y) | **230 / 262 / 300 (low / central / high)** -- clears K9 with significant margin |
| Expected OOS trade count (2.0y) | **100 / 114 / 130 (low / central / high)** -- clears K9 at lower bound (marginal) |
| K9 risk at IS | LOW (significant margin) |
| K9 risk at OOS | LOW-TO-MODERATE (clears at lower bound; thin margin) |
| If K9 fires at IS anyway | `DR1 INCONCLUSIVE_HOLD`; candidate archived without parameter modification |
| If K9 fires at OOS anyway | `INSUFFICIENT_SAMPLE` / `OOS_INDETERMINATE` PARK; candidate archived without parameter modification |

## 14. Diversification expectations -- single-instrument scope (LOCKED at SEAL)

Carried byte-equivalent from s11-d1 / s12-d1 single-instrument framework:

| Field | LOCKED value |
|---|---|
| `A7_effective_independent_bets_min` | **NOT APPLICABLE** (trivially 1) |
| `K10_avg_pairwise_dependence_max` | **NOT APPLICABLE** (no pairs) |
| `K6_per_symbol_observed_win_rate_dispersion` | **NOT APPLICABLE** |
| Per-symbol contribution distribution | trivially 100% to MNQ.c.0 |
| Diversification claim by this candidate | NONE |

## 15. OOS-locking policy (LOCKED at SEAL; carried byte-equivalent)

| Policy | Status |
|---|---|
| OOS data shall not be inspected during IS phase | LOCKED |
| `oos_inspection_blocked_at_in_sample` invariant | LOCKED |
| OOS evaluation requires separately authorized turn after IS verdict `ELIGIBLE_FOR_OOS` | LOCKED |
| **OOS confirmation definition** | LOCKED at SEAL using s11-d1 rev2 magnitude-based form (`oos trade_curve_maxdd_pct >= -30%`; carried byte-equivalent) |

## 16. No-live / no-Strategy-Lab / no-brokerage policy (LOCKED at SEAL; carried byte-equivalent)

Total invariants at SEAL: **25** for F3 single-instrument (no DR11; no C4 invariants; same count as s12-d1; mechanic family substitution does not change invariant count).

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
| Six live-trading gates BLOCKED regardless of any verdict | YES |

## 17. Reject-fast criteria (LOCKED at SEAL; carried byte-equivalent + s13-d1-specific)

The candidate is REJECTED FAST if ANY of:

- **RF1** Any DR rule fires `REJECT_FAST` (DR2 / DR3 / **DR3 elevated for s13-d1 RSI lineage** / DR4 / DR5 / DR6 / DR10 **elevated for s13-d1 high-frequency**)
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
- **RF13** RSI thresholds silently switched from LOCKED 10/50/90/50 post-SEAL
- **RF14** Universe widening or symbol substitution at any phase
- **RF15** Track depends on a survivorship-cherry-pick rule
- **RF16** Any retroactive re-anchoring or modification of s12-d1 terminal park (revival forbidden)

K-gates carried byte-equivalent from s12-d1 chain with F3-specific notes:

- **K1** `sharpe_proxy_per_trade_below_zero_at_S1`
- **K2** `expectancy_per_trade_dollars_nonpositive_at_S1`
- **K4** `trade_curve_max_drawdown_above_threshold` (carried byte-equivalent K4 = 50%)
- **K6** NOT APPLICABLE (single-instrument)
- **K7** `silent_filter_introduction_after_lock`
- **K8** `runtime_safety_invariant_false`
- **K9** `closed_trades_below_100` (clears with significant margin for s13-d1 at both IS and OOS)
- **K10** NOT APPLICABLE (single-instrument)
- **K11** NOT APPLICABLE (no leverage cap)
- **K12** composite cost-stress fail (DR2 + DR3) -- **MORE LIKELY for s13-d1** given RSI lineage risk

K-gate firing priority order: `K8 > K12 > K7 > K9 > K1/K2/K4 > A-gates > ELIGIBLE_FOR_OOS`.

## 18. Phase ladder (each phase separately authorized)

| # | Phase | Status (this turn) | Authorization template |
|---|---|---|---|
| 0 | Selection plan | implicit (`docs/next_research_track_selection_plan_after_s12_d1_park.md` at `0e3f9d4`) | -- |
| 1 | s13-d1 Tier-N spec PLAN (this document) | **COMPLETE THIS TURN** | -- |
| 2 | s13-d1 Tier-N spec DRAFT | NOT AUTHORIZED | `Authorize s13 D1 MNQ.c.0 single-instrument RSI(2) bi-directional Tier-N spec DRAFT` |
| 3 | s13-d1 Tier-N spec SEAL | NOT AUTHORIZED | `Authorize s13 D1 MNQ.c.0 Tier-N spec SEAL` |
| 4 | s13-d1 Step 02b -- manifest cross-link (no fresh fetch) | NOT AUTHORIZED | `Authorize s13 D1 MNQ.c.0 Step 02b manifest cross-link only` |
| 5 | s13-d1 P1 plan-lock | NOT AUTHORIZED | `Authorize s13 D1 MNQ.c.0 P1 plan-lock` |
| 6 | s13-d1 P2 phase-2 plan | NOT AUTHORIZED | `Authorize s13 D1 MNQ.c.0 P2 phase-2 plan only` |
| 7 | s13-d1 P3 BUILD | NOT AUTHORIZED | `Authorize s13 D1 MNQ.c.0 P3 BUILD only` |
| 8 | s13-d1 P4 synthetic smoke | NOT AUTHORIZED | `Authorize s13 D1 MNQ.c.0 P4 synthetic smoke only` |
| 9 | s13-d1 P6 IS diagnostic | NOT AUTHORIZED | `Authorize s13 D1 MNQ.c.0 P6 IS diagnostic only` |
| 10 | s13-d1 P6.5 cost-stress | NOT AUTHORIZED | `Authorize s13 D1 MNQ.c.0 P6.5 cost-stress only` |
| 11 | s13-d1 P7 decision memo | NOT AUTHORIZED | `Authorize s13 D1 MNQ.c.0 P7 decision memo only` |
| 12 | s13-d1 P10 OOS gate | NOT AUTHORIZED | `Authorize s13 D1 MNQ.c.0 P10 OOS gate only` |
| 13 | s13-d1 P11 lifecycle decision | NOT AUTHORIZED | `Authorize s13 D1 MNQ.c.0 P11 lifecycle decision only` |

This plan authors ONLY phase 1 (the PLAN). Each subsequent phase requires its own separately authorized turn. **No Databento call is required at any phase** because the existing MNQ.c.0 CSV (sha-pinned `8b7b832c...`) is reused byte-equivalent.

## 19. Boundaries held this PLAN turn

| Boundary | Status |
|---|---|
| PLAN only (no spec DRAFT, no SEAL, no BUILD, no fetch) | met |
| No strategy code | met |
| No backtest / simulator / signal computation | met |
| No data fetch / Databento call / `DATABENTO_API_KEY` access | met |
| No network IO / live trading / paper trading / brokerage connection | met |
| No candidate promotion / Strategy Lab / review_queue mutation | met |
| **No s12-d1 revival** (terminal park preserved) | met |
| **No s12-d1 `_revN_` revision authored** | met |
| No s11-d1 / s10-d2 / s10-d1 / s9 / s7-d1 / B005 / B006 / T8 sealed-artifact modification | met -- byte-stable |
| No phase-2 safety contract template modification | met |
| No ORB / CLAUDE.md / RUNBOOK / pipeline_manifest / .gitignore modification | met |
| **No `brain_memory/projects/trading_bot/lessons.md` modification or staging** (per operator instruction) | met |
| Trading status | `PAUSED` |
| Live status | `BLOCKED_AT_6_GATES` |
| FRC | `NEVER_GRANTED` |
| `no_strategy_optimization_authorized` | TRUE |
| `no_dr_redefinition_post_seal` | TRUE |
| **K9-reachability discipline applied at PLAN time** | TRUE (NEW framework requirement satisfied) |
| **REC1-equivalent OOS K9 disclosure at PLAN time** | TRUE (NEW framework requirement satisfied) |

## 20. Files written this PLAN turn

| File | Purpose |
|---|---|
| `docs/s13_d1_mnq_c0_single_instrument_rsi_2_bi_directional_databento_long_history_tier_n_spec_plan.md` | This Tier-N spec PLAN (PLAN only; no JSON sidecar; no canonical seal sha256 since this is a planning document not a sealed Tier-N artifact) |

No other repository file is modified by this plan. The brain_memory `lessons.md` dirty + unstaged state remains **untouched**.

## 21. Validation gates and HALT conditions for this plan

V1. ASCII-only.
V2. Numbered sections in monotonic order (1..23).
V3. No execution language.
V4. No self-authorization (this plan does NOT authorize the Tier-N spec to be DRAFTed or SEALed).
V5. No code modification.
V6. No backtest / simulator / signal computation.
V7. No data fetch / Databento call / `DATABENTO_API_KEY` access.
V8. No network IO.
V9. No live trading.
V10. No prior-phase artifact modification.
V11. The committed plan file is the ONLY new file in this turn's commit.
V12. The brain_memory dirty `lessons.md` remains UNSTAGED and UNTOUCHED.
V13. The candidate is structurally single-instrument; A7/K10/K6 NOT APPLICABLE.
V14. The candidate is NOT a revision of any parked predecessor (s12-d1 terminal park preserved).
V15. The candidate's universe is LOCKED at `{MNQ.c.0}` only.
V16. Mechanic family F3 LOCKED at PLAN.
V17. RSI(2) parameters (10/50/90/50) LOCKED at PLAN; thresholds non-negotiable at SEAL.
V18. **K9-reachability discipline applied at PLAN time (NEW framework requirement).**
V19. **REC1-equivalent OOS K9 disclosure at PLAN time (NEW framework requirement).**
V20. First-principles burden satisfied vs s9 (different universe + different asset class + different cost surface + bi-directional vs long-only).
V21. First-principles burden satisfied vs s12-d1 (orthogonal mechanic family).

HALT conditions:

H1. If any V-gate fails, the turn HALTs.
H2. If pre-stage git index is non-empty, the turn HALTs and remediates.
H3. If staged file count is anything other than 1, the turn HALTs.
H4. If staged file is anything other than `docs/s13_d1_mnq_c0_single_instrument_rsi_2_bi_directional_databento_long_history_tier_n_spec_plan.md`, the turn HALTs.
H5. If `lessons.md` is accidentally staged, the turn HALTs and remediates.
H6. If any s11-d1 / s12-d1 / earlier-candidate sealed artifact is detected as modified, the turn HALTs.

## 22. Next-step authorization scope

The next operator authorization in the established controller-session pattern shall use one of these scopes:

### Most natural progression
```
Authorize s13 D1 MNQ.c.0 single-instrument RSI(2) bi-directional Tier-N spec DRAFT.
```
Authors the DRAFT turn that enumerates DRAFT ambiguities for parameters NOT locked at PLAN (ATR window/multiplier, per-trade risk %, START_CASH, K4 threshold, output schema name, cost-stress tier set, DR thresholds, WARMUP_DAYS, RTH window) and recommends DRAFT-default-primaries.

### Reject s13-d1 / pivot
```
Authorize alternative selection plan rev2 only.
```
or
```
Authorize cross-domain pivot only.
```
or
```
Defer / Pause trading-bot track.
```

This plan is the source of truth for the s13-d1 MNQ.c.0 single-instrument RSI(2) bi-directional candidate's intended Tier-N spec scope.

## 23. No-live status carried forward (UNCHANGED)

| Field | Value |
|---|---|
| Trading | `PAUSED` |
| Live mode | `BLOCKED_AT_6_GATES` |
| FRC | `NEVER_GRANTED` |
| Six live-trading gates remain BLOCKED regardless of any future verdict | TRUE |
| `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` advisory label applies to any candidate descended from this plan | TRUE |
| `no_strategy_optimization_authorized` | TRUE |
| `no_dr_redefinition_post_seal` | TRUE |
| s12-d1 lifecycle terminal at park | TRUE (NOT revived by this plan) |
| **K9-reachability discipline applied at PLAN time** | TRUE (carried into framework as new requirement) |
| **REC1-equivalent OOS K9 disclosure at PLAN time** | TRUE (carried into framework as new requirement) |

----

End of plan. PLAN-authoring turn only. No code. No backtest. No simulator. No signal. No data fetch. No yfinance. No Yahoo Finance. No Databento. No `DATABENTO_API_KEY` access. No QC. No LEAN. No brokerage. No real order. No paper order. No Strategy Lab promotion. No `review_queue` mutation. No production `idea_memory` mutation. No ORB branch mutation. **No `lessons.md` modification or staging.** No live trading. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES.
