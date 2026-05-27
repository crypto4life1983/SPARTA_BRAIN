# s11 D1 MNQ.c.0 Single-Instrument Databento Long-History Tier-N Specification Plan

Status: PLAN_ONLY (no code written, no spec sealed, no data fetched by this plan; the next step is a separate operator authorization to DRAFT the Tier-N spec, then SEAL it under separate authorization, then BUILD downstream modules each under separate authorization).
Authored: 2026-05-27
Authorization: "Authorize s11 D1 MNQ.c.0 single-instrument Databento long-history Tier-N specification plan only."

Selection plan source: `docs/next_research_track_selection_plan_after_s10_d1_park.md` section 15 (committed at `556ab3f`).
Predecessor parked candidate (read-only reference): `s10-d1-cross-asset-trend-or-meanrev-mnq-mgc-databento-long-history` parked `INCONCLUSIVE_HOLD` at commit `1a9acec`.
Audit-clean data anchor (MNQ.c.0): `data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_c_0_ohlcv_1d_20190513_20251230.csv` (sha256 `8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e`).
T8 family-park reference (read-only): `reports/external_research_hunter/t8_spy_tlt_gld_uso_2014_2022_family_park_memo.json` -- does NOT apply because this candidate's universe is NOT SPY/TLT/GLD/USO.
S10-D1 micro availability probe reference (read-only): `reports/external_research_hunter/s10_d1_micro_availability_probe_result_memo.json` (sha256 `76dcb833f89d3044547e0e361e03f39ae325a22a5c9c06baf1ec0f2e9df213fe`).

HARD BOUNDARIES (held by this plan). Plan only. No strategy code. No backtest. No simulator. No new signal computation. No OOS inspection. No data fetch. No yfinance / Yahoo Finance call. No Databento call. No DATABENTO_API_KEY access. No QC / LEAN call. No network IO. No review_queue.json mutation. No production idea_memory mutation. No Strategy Lab run. No candidate promotion. No s10 D1 / s9 / s7 D1 / B006_NNN sealed-artifact modification. No ORB branch artifact mutation. No Step 30 cost constant mutation. No CLAUDE.md modification. No docs/decisions.md modification. No RUNBOOK modification. No pipeline_manifest modification. No .gitignore modification. No `brain_memory/projects/trading_bot/lessons.md` modification or staging. No branch change. No branch creation. No commit beyond the single new plan file. No git push. No live trading. No profitability claim. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES. FRC never granted.

----

## 1. Purpose

Author a sealed plan-to-spec for the first Tier-N specification of a fresh single-instrument candidate on MNQ.c.0 Databento daily-bar data over the IS+OOS window inherited from the parked s10 D1 lifecycle. The plan does NOT seal the spec; it authors the plan-to-DRAFT that will inform a subsequent operator-authorized DRAFT turn, which will in turn inform a subsequent operator-authorized SEAL turn. No code, no data fetch, no Databento call is performed by this plan.

This is the T1 component from `docs/next_research_track_selection_plan_after_s10_d1_park.md` section 15 (recommended at 48/50 score). The candidate is structurally a fresh candidate id (NOT a revision of s10 D1 MNQ+MGC; NOT a revision of B006_001 / B006_002 SPY vol-targeting). The MNQ-clean-leg finding from the s10 D1 park report is preserved and reused; the MGC.c.0 DR9-fire pathology is structurally absent because MGC is not in this candidate's universe.

## 2. Candidate identification

| Field | Proposed value (subject to operator confirmation at DRAFT, then SEAL) |
|---|---|
| `candidate_record_id` | `s11-d1-mnq-c0-single-instrument-databento-long-history` |
| `candidate_family` | TBD at DRAFT/SEAL (one of: F1 trend-no-pyramid / F2 vol-targeting / F3 RSI mean-reversion / F4 other; operator picks at the DRAFT turn from a closed menu) |
| `is_a_trade_candidate` | true |
| `is_an_equity_universe_candidate` | false |
| `is_a_b006_001_revision` | false |
| `is_a_b006_002_revision` | false |
| `is_a_s7_d1_revision` | false |
| `is_a_s9_revision` | false |
| `is_a_s10_d1_revision` | false |
| `is_a_b006_NNN_extension` | false |
| `is_a_single_instrument_candidate` | **true** (load-bearing structural property) |
| `predecessor_lineage_references_read_only` | `s10_d1_mnq_mgc_park`, `s9_rsi2_etf_proxy_park`, `s7_d1_etf_proxy_park`, `b006_001_archival`, `b006_002_archival`, `t8_etf_proxy_family_park`, `s10_d1_micro_availability_probe` |
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
| Universe widening at later phases | FORBIDDEN (any wider basket requires a fresh candidate id, NOT a revision) |
| Symbols explicitly excluded for any future phase of this candidate | MGC.c.0 (DR9-failed per s10 D1 park), MCL.c.0 (S10-D1 memo: unreliable before 2021-07), and all other Databento micros (would require fresh availability probes under separate authorization to add to a future fresh-candidate-id) |
| Common-history start (verified by s10 D1 audit cycle) | **2019-05-13** (1,301 records on this date for MNQ.c.0 on ohlcv-1m confirmed; ohlcv-1d equivalence verified at sha-pin) |
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
| API key handling at any phase of this candidate | NOT REQUIRED (no fresh fetch); `DATABENTO_API_KEY` environment-variable presence is OPTIONAL at every controller-side phase; `databento_api_key_read_from_env_only_never_logged_or_saved` invariant carried byte-equivalent from s10 D1 |
| Controller-side Databento call at any phase | LOCKED OFF |

## 5. Schema (LOCKED at SEAL)

| Field | LOCKED value |
|---|---|
| Schema | `ohlcv-1d` |
| Records expected per trading day | 1 (daily bar) |
| Fields | `ts_event`, `open`, `high`, `low`, `close`, `volume` (required columns set; carried byte-equivalent from s10 D1) |
| Intraday schemas (`1s` / `1m` / `1h`) | OUT OF SCOPE for this candidate's Tier-N; future `_revN_` of this candidate may include intraday separately under fresh operator authorization |

## 6. stype_in (LOCKED at SEAL)

| Field | LOCKED value |
|---|---|
| `stype_in` | `continuous` |
| Continuous roll stitch | Databento native continuous-front-month synthesis; details out of operator's modification scope |
| `no_continuous_roll_stitch_modification_post_seal` invariant | TRUE |

## 7. IS / OOS windows (LOCKED at SEAL)

Carried byte-equivalent from s10 D1 sealed spec; the underlying CSV already covers both windows.

| Field | LOCKED value |
|---|---|
| **IS window start** | **`2019-05-13`** |
| **IS window end** | **`2023-12-29`** |
| IS window length | ~4.6 years (~1,140 trading days) |
| MNQ.c.0 IS-window observed row count (audit-confirmed) | **1,443** (per s10 D1 audit; `is_pct_observed = 1.2365` PASS) |
| **OOS window start (never inspected at IS)** | **`2024-01-02`** |
| **OOS window end (never inspected at IS)** | **`2025-12-30`** |
| OOS window length | ~2 years |
| MNQ.c.0 OOS-window observed row count (structural only; NO return analysis at IS phase) | **622** (recorded by s10 D1 audit; the candidate's IS-phase modules MUST NOT slice OOS rows) |
| Post-OOS data | `2026-01-02 onward` (informational only; no diagnostic) |
| OOS inspection at IS-phase | FORBIDDEN (`oos_inspection_blocked_at_in_sample` invariant carried byte-equivalent from s10 D1) |

## 8. Strategy mechanic-family selection (DEFERRED to DRAFT turn; operator picks from closed menu)

This plan does NOT lock the mechanic family. The DRAFT turn will resolve the family from one of the following four candidates, each of which is structurally compatible with a single-instrument MNQ.c.0 futures design and has a falsifiable first-principles rationale:

### 8.1 Option F1 -- Long+Short Bi-Directional Donchian Trend, No Pyramid, ATR-Based Stop

| Field | Value |
|---|---|
| Mechanic | Donchian-N entry / Donchian-M exit; bi-directional (long+short); single contract per signal (no pyramid); ATR(P)-based stop |
| Carried from | s10 D1 sealed spec mechanic family F1 byte-equivalent (with universe collapsed to single instrument) |
| First-principles for forward survival | s10 D1 never reached signal phase (parked at audit on MGC); the F1 mechanic on MNQ-only futures is structurally untested by the framework; cost surface differs from ETF Donchian |
| Expected trade count over 4.6y IS | ~50-150 portfolio trades (single-symbol, bi-directional; Donchian-20/10 default; depends on operator's DA confirmation at SEAL) |
| K9 risk | borderline; needs careful Donchian-N choice |
| Notes | Direct continuation of s10 D1 design intent on the clean leg only |

### 8.2 Option F2 -- Volatility-Targeted Long-Only with Realized-Vol Sizing (B006_002 lineage on MNQ futures)

| Field | Value |
|---|---|
| Mechanic | Long MNQ at position size targeting X% annualized realized volatility; realized vol computed from trailing 60-day simple stdev of daily log returns; monthly rebalance; leverage cap; no risk-off rule |
| Carried from | B006_002 archival memo + sealed spec lineage (with MNQ futures substituted for SPY equity) |
| First-principles for forward survival | B006_001 produced REQUEST_FULL_PREREGISTRATION_REVIEW on SPY-only vol-targeting; B006_002 with DR11 C4 enforcement produced REJECT_FAST because the SPY leverage-cap-bound rate exceeded 10%. On MNQ futures the cost surface differs and the leverage cap can be set higher (futures use margin not cash); the C4 binding pattern may not recur |
| Expected trade count over 4.6y IS | ~55 monthly rebalances per first-day-of-month schedule |
| K9 risk | borderline at 55 trades; below A1's 100-trade floor (would force `INCONCLUSIVE_HOLD` on DR1) |
| Notes | Tests sizing; carries LESSON_B006_001_002 (warmup guard) + LESSON_B006_001_003 (DR6 narrowing) + LESSON_B006_002_001 (DR11 C4 enforcement) byte-equivalent |

### 8.3 Option F3 -- RSI(2) Mean-Reversion (s9 lineage on MNQ futures)

| Field | Value |
|---|---|
| Mechanic | Connors RSI(2) oversold-bounce on close; enter long when RSI(2) < 10; exit when RSI(2) > 50; bi-directional optional (short entry when RSI(2) > 90); single contract per signal; ATR-based stop |
| Carried from | s9 RSI-2 ETF-proxy sealed spec mechanic family (with universe collapsed to single MNQ futures) |
| First-principles for forward survival | s9 RSI-2 failed at S0 (negative edge before any cost friction) on the SPY/TLT/GLD/USO ETF-proxy universe; the s9 finding does NOT transfer to MNQ futures by default (different universe, different cost surface, different intraday vol profile) |
| Expected trade count over 4.6y IS | ~200-300 portfolio trades (RSI-2 fires more frequently than Donchian or monthly rebal) |
| K9 risk | clears comfortably |
| Notes | Tests an orthogonal-family signal on the clean MNQ leg; risk that the s9 universe-falsification carries to MNQ is a genuine open question, not an a-priori claim |

### 8.4 Option F4 -- Volatility-Premium / Term-Structure / Carry (speculative)

| Field | Value |
|---|---|
| Mechanic | TBD; could be MNQ vs MNQ-next-month basis (requires next-month contract data beyond `ohlcv-1d`), or MNQ realized-vs-implied (requires VIX or VXN data) |
| First-principles for forward survival | Carry / term-structure is a structurally different mechanic family from trend, mean-reversion, and vol-targeting |
| Expected trade count | depends on rebalance frequency |
| K9 risk | TBD |
| Notes | **Requires data beyond the existing audit-clean CSV** (next-month contract or volatility-index series); higher data-scope friction; defer to a future cycle. NOT recommended as default at DRAFT. |

The operator picks ONE of F1-F4 at the **DRAFT turn**. The DRAFT turn will list all four options with DRAFT-default-primary recommendations and operator confirms (or revises) at the **SEAL turn** in the standard pattern.

## 9. Locked parameter values (DEFERRED to DRAFT/SEAL turns)

This plan does NOT lock any strategy parameter. The full parameter set is locked by the operator at the SEAL turn after the DRAFT turn resolves the mechanic family (section 8) and enumerates the parameter ambiguities.

Anticipated parameter classes (with mechanic-family-conditional values):

| Class | Will be locked at SEAL | Mechanic-family-conditional notes |
|---|---|---|
| `IS_WINDOW_START` | yes | `2019-05-13` (carried) |
| `IS_WINDOW_END` | yes | `2023-12-29` (carried) |
| `OOS_WINDOW_START` | yes | `2024-01-02` (carried; never inspected) |
| `OOS_WINDOW_END` | yes | `2025-12-30` (carried; never inspected) |
| Mechanic-specific signal parameters | yes | depends on F1-F4 selection (Donchian N/M / RSI thresholds / TARGET_VOL / lookback / basis windows) |
| Sizing rule | yes | per-contract notional; per-trade risk = 1% portfolio equity (proposed; revisable at SEAL); ATR-based stop distance; **single contract per signal (no pyramid)** (LOCKED non-negotiable) |
| Per-symbol cap | yes | 1 contract per signal (LOCKED; `no_pyramid_per_signal` invariant) |
| `START_CASH_USD` | yes | TBD; proposed `100000` (carried byte-equivalent from B006/s10 D1 lineage) |
| `WARMUP_DAYS` | yes | TBD; minimum `MAX(longest_lookback_in_mechanic, 220)` (B006 lineage); for F1 with N=20: resolved to 220 |
| `REBALANCES_PER_YEAR` (iff F2 vol-targeting) | yes | 12 (monthly) if F2 selected |

## 10. Cost stress + sizing stress matrices (LOCKED at SEAL)

Cost-stress S0/S1/S2/S3 carried byte-equivalent from s10 D1 sealed spec with single-instrument adaptation. The matrix is locked in the first IS diagnostic; deferral is forbidden.

### 10.1 Cost tiers (futures-specific; identical to s10 D1)

| Tier | Label | Commission per contract USD | Slippage ticks one-way |
|---|---|---|---|
| S0 | `source_or_default` | 0.00 | 0.0 |
| S1 | `futures_low_slippage` | **`0.85`** (typical micro futures) | **`0.5`** |
| S2 | `futures_mid_slippage` | 0.85 | **`1.5`** |
| S3 | `futures_high_slippage` | 0.85 | **`3.0`** |

### 10.2 Tick / contract specs (LOCKED at SEAL)

| Symbol | Tick size | Dollar per tick | Notes |
|---|---|---|---|
| `MNQ.c.0` | 0.25 index points | **$0.50 per contract** | Micro E-mini Nasdaq-100 (carried from s10 D1) |

### 10.3 Pre-registered S0 edge sign and magnitude (DRAFT-time decision; LOCKED at SEAL)

Per LESSON_B006_002_002 (favorable economic numbers do not override fail-closed verdicts by design) and the s9 lesson (negative S0 edge = parked), the operator pre-registers the expected S0 edge sign at SEAL time:

| Field | DRAFT-proposed value |
|---|---|
| Expected S0 net PnL sign | open question (no a-priori claim) |
| Acceptance threshold S0 net PnL | `> 0` after >= 100 trades |
| Acceptance threshold S1 net PnL | `> 0` (K1 / K2 fire if `<= 0` at S1 baseline) |
| Pre-registered max-drawdown tolerance | TBD; proposed K4 = 30% of `START_CASH_USD` (carried from s10 D1 default) |
| Pre-registered cost-stress survival | S0/S1/S2/S3 all positive Sharpe (C5+) -> `ELIGIBLE_FOR_HUMAN_REVIEW`; S0/S1 positive but S2/S3 degrade > 50% -> K12 REJECT_FAST |

## 11. DR rules adapted for single-instrument MNQ.c.0 (LOCKED at SEAL)

Carried byte-equivalent from s10 D1 sealed spec section 11 with single-instrument simplifications:

| Rule | Trigger | Severity | Single-instrument adaptation |
|---|---|---|---|
| DR1 | `oos_rebalance_count < 36` (or equivalent for chosen frequency; evaluated only at OOS phase) | `INCONCLUSIVE_HOLD` | unchanged |
| DR2 | `oos_metrics_degrade_materially_under_cost_stress` (S0 Sharpe > 0 AND (S2 or S3 degrades > 50%)) | `REJECT_FAST` | unchanged |
| DR3 | `zero_cost_only_survival` (S0 > 0 AND all S1/S2/S3 <= 0) | `REJECT_FAST` | unchanged |
| DR4 | `oos_negative_while_is_positive_unexplained` | `REJECT_FAST` | unchanged; OOS-only |
| DR5 | `cost_stress_turns_edge_negative` (tier flip) | `REJECT_FAST` / `INCONCLUSIVE_HOLD` (carveout) | unchanged |
| DR6 | `post_warmup_sizing_ambiguity_or_invalid` (NARROWED post-warmup only) | `REJECT_FAST` | unchanged; carried byte-equivalent from B006_002 |
| DR7 | `missing_oos_or_date_window_evidence` | `INCONCLUSIVE_HOLD` | unchanged |
| DR8 | `live_or_order_routing_path_detected` at Initialize | `HARD_FAIL_VOIDED` | unchanged |
| **DR9** | **`mnq_c0_only_data_continuity_integrity_check`** (REDEFINED for single-instrument scope) | `INCONCLUSIVE_HOLD` | thresholds carried byte-equivalent from s10 D1 (`0.95` / `0.30` / `5` / `5`); MGC-side fire pathology STRUCTURALLY ABSENT because MGC is not in the universe; MNQ.c.0 is already known to be DR9-clean per s10 D1 audit |
| DR10 | `turnover_cost_explosion` (`annual_turnover > 0.50` OR `S2 cost drag > 0.05`) | `REJECT_FAST` | unchanged |
| DR11 | `c4_leverage_cap_bound_rate_exceeded` (threshold 0.10; severity REJECT_FAST; precedence position 3) | `REJECT_FAST` | **ONLY IF F2 vol-targeting mechanic is selected at DRAFT**; structurally absent for F1 / F3 / F4 (no leverage cap to bind) |

DR precedence chain (LOCKED at SEAL after mechanic-family choice):

- If F1 / F3 / F4 chosen (no leverage cap): `DR7 -> DR1 -> DR9 -> DR10 -> DR6 -> DR4 -> DR2 -> DR3 -> DR5` (carried byte-equivalent from s10 D1)
- If F2 chosen (vol-targeting with leverage cap): `DR7 -> DR1 -> DR11 -> DR9 -> DR10 -> DR6 -> DR4 -> DR2 -> DR3 -> DR5` (carried byte-equivalent from B006_002 with DR11 at precedence position 3)

## 12. Sample-size / K9 rules (LOCKED at SEAL)

| Field | LOCKED value |
|---|---|
| K9 threshold | `total_closed_trades >= 100` over IS window |
| Expected trade count (mechanic-family-conditional) | F1 Donchian-20/10 bi-directional: 50-150 trades (borderline; may force `INCONCLUSIVE_HOLD` on K9). F2 monthly vol-targeting: ~55 rebalances (below K9 floor; K9 will fire). F3 RSI-2 mean-reversion: 200-300 trades (clears comfortably). F4 carry / term-structure: TBD. |
| **K9 risk per mechanic family** | F2 is at high K9 risk; the operator should factor this into the DRAFT-time mechanic selection. K9 fire forces `INCONCLUSIVE_HOLD` (not REJECT_FAST); the candidate is archived under that verdict without parameter modification. |
| Per-symbol minimum | NOT APPLICABLE for single-instrument; the K9 threshold IS the per-symbol minimum |

## 13. Diversification expectations -- single-instrument scope (LOCKED at SEAL)

| Field | LOCKED value |
|---|---|
| A7 (`effective_independent_bets >= X`) | **NOT APPLICABLE** for single-instrument scope; `effective_independent_bets` is trivially 1 by construction; A7 is structurally removed from the acceptance gate set for this candidate |
| K10 (`avg_pairwise_dependence`) | **NOT APPLICABLE** for single-instrument scope; no pairs exist; K10 is structurally removed from the K-gate set |
| K6 (`per_symbol_observed_win_rate_dispersion`) | **NOT APPLICABLE** for single-instrument scope; no per-symbol dispersion to measure; K6 is structurally removed |
| Per-symbol contribution distribution | trivially 100% to the single symbol (MNQ.c.0); the diagnostic reports MNQ's standalone risk profile (Sharpe / expectancy / MaxDD / win-rate / trade-count) as the entire diagnostic surface |
| Diversification claim by this candidate | NONE; the candidate is explicitly a single-instrument diagnostic with first-principles justification: "the s10 D1 MNQ-clean-leg is the only structurally-useful finding preserved by the parked candidate; test it on its own merits before extending to any multi-symbol design" |
| Disclaimer carried byte-equivalent | "Diversification independence does NOT imply positive edge" (carried from s9; LESSON_B006_002_002 reinforces) -- applies trivially here because no diversification claim is made |

## 14. OOS-locking policy (LOCKED at SEAL; carried byte-equivalent)

| Policy | Status |
|---|---|
| OOS data (`2024-01-02 -> 2025-12-30`) shall not be inspected, computed against, simulated over, or queried in any form during the in-sample diagnostic phase | LOCKED |
| Post-OOS data (`2026-01-02 onward`) is informational only; no diagnostic uses it | LOCKED |
| OOS inspection requires a separately authorized turn after IS verdict `ELIGIBLE_FOR_OOS` plus explicit operator approval | LOCKED |
| Loader / validator / signal / simulator / aggregator modules shall structurally enforce IS-only computation | LOCKED (`oos_inspection_blocked_at_in_sample` invariant) |

## 15. No-live / no-Strategy-Lab / no-brokerage policy (LOCKED at SEAL; carried byte-equivalent)

Inheritable invariants set, single-instrument adapted:

7 inherited B005_NNN framework:
- `no_live_trading`
- `no_strategy_lab_promotion`
- `no_review_queue_mutation`
- `no_brokerage_connection`
- `no_external_network` (runtime)
- `no_databento_at_runtime_only_at_optional_explicit_ingest_phase` (NOTE: this candidate's Step 02b is a manifest cross-link; no fresh Databento call required at any phase)
- `no_production_signal`

4 inherited B006_001:
- `no_strategy_optimization_authorized`
- `no_profitability_claim`
- `no_universe_membership_logic`
- `no_dr_redefinition_post_seal`

3 inherited B006_002 (carried iff mechanic family uses leverage cap, i.e., F2):
- `no_warmup_order_submission`
- `dr6_warmup_contamination_blocked`
- `c4_leverage_cap_bound_rate_must_be_enforced` (iff F2)

5 inherited s10 D1-specific (all carry byte-equivalent):
- `no_continuous_roll_stitch_modification_post_seal`
- `no_mcl_inclusion_under_long_history_scope`
- `no_intraday_schema_ingest_under_daily_only_design`
- `databento_api_key_read_from_env_only_never_logged_or_saved`
- `no_pyramid_per_signal`

3 NEW s11-D1-specific (proposed; LOCKED at SEAL):
- `single_instrument_universe_NO_widening_post_seal`
- `no_substitution_of_any_symbol_into_this_universe_post_seal`
- `mnq_c0_csv_reuse_from_s10_d1_byte_equivalent_no_fresh_fetch`

Total invariants at SEAL: 19-22 depending on mechanic-family selection (F1 / F3 / F4 = 19 invariants; F2 = 22 invariants including 3 B006_002-leverage-cap-related).

Status surface (permanent for this candidate, independent of any future verdict):

| Field | Value |
|---|---|
| Trading | `PAUSED` |
| Live mode | `BLOCKED_AT_6_GATES` |
| FRC | `NEVER_GRANTED` |
| `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` advisory label | permanent |
| Six live-trading gates remain BLOCKED regardless of any verdict | YES |

## 16. Reject-fast criteria (LOCKED at SEAL; carried byte-equivalent + single-instrument adaptations)

The candidate is REJECTED FAST if ANY of:

- **RF1** Any DR rule fires `REJECT_FAST` (DR2 / DR3 / DR4 / DR5 / DR6 / DR10; DR11 iff F2)
- **RF2** DR9 `mnq_c0_only_data_continuity_integrity_failure` AND > 5 violations (extremely unlikely given the MNQ-clean-leg finding)
- **RF3** DR6 post-warmup invalid-sizing event count > 0 (single event = REJECT_FAST per LESSON_B006_002_002)
- **RF4** Any forbidden-verdict-token in runner output
- **RF5** Runner attempts `SetLiveMode` / `SetBrokerageModel` / `DeployAlgorithm` / unauthorized network call / unauthorized Databento call at runtime
- **RF6** Any order-submit attempt while in warmup window (iff F2)
- **RF7** Runner mutates any s10 D1 / s9 / s7 D1 / B006_NNN / T8 / s11 D1 sealed artifact (byte-shift)
- **RF8** Runner makes a Databento API call at runtime (controller-side; this candidate's Step 02b is manifest cross-link only, no runtime API call)
- **RF9** Runner caches `.dbn.zst` files anywhere
- **RF10** Runner accesses `DATABENTO_API_KEY` at runtime
- **RF11** Track silently re-introduces a filter, regime gate, or selection rule that this DRAFT/SEAL locked to NONE
- **RF12** Pyramid mechanism re-introduced in code (multi-contract pyramid)
- **RF13** Mechanic family silently switched from the DRAFT/SEAL-locked choice post-SEAL
- **RF14** Track depends on a survivorship-cherry-pick rule
- **RF15** Universe widening or symbol substitution attempted at any phase

K-gates carried byte-equivalent from s10 D1 with single-instrument simplifications:

- **K1** `sharpe_proxy_per_trade_below_zero_at_S1`
- **K2** `expectancy_per_trade_dollars_nonpositive_at_S1`
- **K4** `trade_curve_max_drawdown_above_threshold` (DRAFT-proposed K4 = 30% of `START_CASH_USD`)
- **K6** NOT APPLICABLE for single-instrument
- **K7** `silent_filter_introduction_after_lock`
- **K8** `runtime_safety_invariant_false`
- **K9** `closed_trades_below_100` (mechanic-family-conditional risk; see section 12)
- **K10** NOT APPLICABLE for single-instrument
- **K11** `cap_binding_events_above_threshold` (iff F2 vol-targeting; via DR11)
- **K12** composite cost-stress fail (DR2 + DR3)

K-gate firing priority order: `K8 > K12 > K7 > K9 > K1/K2/K4 > A-gates > ELIGIBLE_FOR_OOS` (single-instrument-adapted; K6 / K10 removed).

## 17. Phase ladder (each phase separately authorized)

| # | Phase | Status (this turn) | Authorization template |
|---|---|---|---|
| 0 | Selection plan | implicit (`docs/next_research_track_selection_plan_after_s10_d1_park.md` at `556ab3f`) | -- |
| 1 | Tier-N spec PLAN (this document) | **COMPLETE THIS TURN** | -- |
| 2 | Tier-N spec DRAFT | NOT AUTHORIZED | `Authorize s11 D1 MNQ.c.0 single-instrument Tier-N spec DRAFT` |
| 3 | Tier-N spec SEAL | NOT AUTHORIZED | `Authorize s11 D1 MNQ.c.0 single-instrument Tier-N spec SEAL` |
| 4 | Step 02b -- manifest cross-link (no fresh Databento fetch) | NOT AUTHORIZED | `Authorize s11 D1 MNQ.c.0 Step 02b manifest cross-link only` |
| 5 | Step 02c -- MNQ-only audit re-confirmation | NOT AUTHORIZED | `Authorize s11 D1 MNQ.c.0 Step 02c raw-data audit only` |
| 6 | Step 03 -- loader BUILD ONLY | NOT AUTHORIZED | `Authorize s11 D1 MNQ.c.0 Step 03 loader BUILD only` |
| 7 | Step 04 -- validator BUILD ONLY | NOT AUTHORIZED | `Authorize s11 D1 MNQ.c.0 Step 04 validator BUILD only` |
| 8 | Step 05 -- signal BUILD ONLY (NEW; mechanic-family-specific) | NOT AUTHORIZED | `Authorize s11 D1 MNQ.c.0 Step 05 signal BUILD only` |
| 9 | Step 06 -- simulator BUILD ONLY | NOT AUTHORIZED | `Authorize s11 D1 MNQ.c.0 Step 06 simulator BUILD only` |
| 10 | Step 07 -- aggregator BUILD ONLY | NOT AUTHORIZED | `Authorize s11 D1 MNQ.c.0 Step 07 aggregator BUILD only` |
| 11 | IS decision memo + park or eligibility | NOT AUTHORIZED | `Authorize s11 D1 MNQ.c.0 IS decision memo only` |

This plan authors ONLY phase 1 (the spec PLAN). Every subsequent phase requires its own separately authorized turn. **No Databento call is required at any phase** because the existing MNQ.c.0 CSV (sha-pinned `8b7b832c…fa23e`) is reused byte-equivalent.

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
| No modification of s10 D1 / s9 / s7 D1 / B006_NNN / T8 sealed artifacts | met -- byte-stable |
| No modification of ORB branch artifacts | met |
| No modification of CLAUDE.md / docs/decisions.md / RUNBOOK / pipeline_manifest / .gitignore | met |
| No modification or staging of `brain_memory/projects/trading_bot/lessons.md` (dirty + unstaged from prior session; left untouched) | met |
| No mutation of `review_queue.json` | met |
| No mutation of production `idea_memory` | met |
| No profitability claim | met |
| Trading status | `PAUSED` |
| Live status | `BLOCKED_AT_6_GATES` |
| FRC | `NEVER_GRANTED` |
| `no_strategy_optimization_authorized` | TRUE |

## 19. Files written this PLAN turn (this document scope)

| File | Purpose |
|---|---|
| `docs/s11_d1_mnq_c0_single_instrument_databento_long_history_tier_n_spec_plan.md` | This Tier-N spec PLAN (the plan to DRAFT-to-SEAL; no spec is sealed by this plan) |

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
V10. No prior-phase artifact modification.
V11. The committed plan file is the ONLY new file changed in this turn's commit.
V12. The brain_memory dirty `lessons.md` remains UNSTAGED and UNTOUCHED.
V13. The candidate is structurally single-instrument; A7 / K10 / K6 are explicitly NOT APPLICABLE.
V14. The candidate is NOT a revision of any parked predecessor.
V15. The candidate's universe is LOCKED at `{MNQ.c.0}` only; substitution / widening clauses are FORBIDDEN at any future phase of this candidate.

HALT conditions:

H1. If any V-gate fails, the turn HALTs.
H2. If the pre-stage git index is non-empty, the turn HALTs and remediates.
H3. If the staged file count is anything other than 1, the turn HALTs.
H4. If the staged file is anything other than `docs/s11_d1_mnq_c0_single_instrument_databento_long_history_tier_n_spec_plan.md`, the turn HALTs.
H5. If `lessons.md` is accidentally staged, the turn HALTs and `git restore --staged brain_memory/projects/trading_bot/lessons.md` before retrying.

## 21. Next-step authorization scope

The next operator authorization in the established controller-session pattern shall use one of these scopes:

- **"Authorize s11 D1 MNQ.c.0 single-instrument Tier-N spec DRAFT"** -- begin the DRAFT turn that enumerates DRAFT ambiguities (mechanic-family choice F1/F2/F3/F4 + per-family parameter defaults) and recommends DRAFT-default-primaries.
- **"Authorize alternative track selection plan revision only"** -- reject the T1 recommendation and ask for a different recommendation among T2-T9 from the predecessor selection plan.
- **"Authorize cross-domain pivot only"** -- pivot to a different project entirely.
- **"Defer / Pause trading-bot track"** -- hold this plan on file without authorizing the DRAFT turn at this time.

This plan is the source of truth for the s11 D1 MNQ.c.0 single-instrument Databento long-history candidate's intended Tier-N spec scope. Future DRAFTs, SEALs, or BUILDs that contradict this plan require either a fresh plan revision or an out-of-band justification.

## 22. No-live status carried forward

| Field | Value |
|---|---|
| Trading | `PAUSED` |
| Live mode | `BLOCKED_AT_6_GATES` |
| FRC | `NEVER_GRANTED` |
| Six live-trading gates remain BLOCKED regardless of any future verdict | TRUE |
| `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` advisory label applies to any candidate descended from this plan | TRUE |
| `no_strategy_optimization_authorized` | TRUE |

----

End of plan. Plan-authoring turn only. No code. No backtest. No simulator. No signal. No data fetch. No yfinance. No Yahoo Finance. No Databento. No DATABENTO_API_KEY access. No QC. No LEAN. No brokerage. No real order. No paper order. No Strategy Lab promotion. No review_queue mutation. No production idea_memory mutation. No ORB branch mutation. No lessons.md modification or staging. No live trading. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES.
