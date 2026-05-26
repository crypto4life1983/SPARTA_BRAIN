# s10 D1 MNQ+MGC Databento Long-History Tier-N Specification Plan

Status: PLAN_ONLY (no code written, no spec sealed, no data fetched by this plan; the next step is a separate operator authorization to SEAL the Tier-N spec).
Authored: 2026-05-26
Authorization: "Authorize T8 + T7-Path-A paired next step after s9 park."
Selection plan reference: docs/next_research_track_selection_plan_after_s9_park.md section 17 (committed at 2ec9330)
Sibling family-park memo: reports/external_research_hunter/t8_spy_tlt_gld_uso_2014_2022_family_park_memo.md (authored in the same controller turn)
Sibling availability evidence: reports/external_research_hunter/s10_d1_micro_availability_probe_result_memo.md (sha256 006d39df196f378064a0700d9e1dca90cacf94cb2e74ef8bccc44c8a469d70eb)

HARD BOUNDARIES (held by this plan). Plan only. No strategy code. No backtest. No simulator. No new signal computation. No OOS inspection. No data fetch. No yfinance import. No Yahoo Finance call. No Databento call. No DATABENTO_API_KEY access. No network IO. No review_queue.json mutation. No production idea_memory mutation. No Strategy Lab run. No candidate promotion. No s7 D1 / s9 / B006_001 / B006_002 sealed-artifact modification. No ORB branch artifact mutation. No Step 30 cost constant mutation. No CLAUDE.md modification. No docs/decisions.md modification. No RUNBOOK modification. No pipeline_manifest modification. No .gitignore modification. No lessons.md modification or staging. No branch change. No branch creation. No git push. No live trading. No profitability claim. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES. FRC never granted.

----

## 1. Purpose

Author a sealed plan for the first Tier-N specification of a fresh research track on the Databento micro futures universe (MNQ.c.0 + MGC.c.0 continuous front-month) over a long-history common-history window starting in 2019. The plan does NOT seal the spec; it authors the plan-to-seal that will inform a subsequent operator-authorized SEAL turn. No code, no data fetch, no Databento call is performed by this plan.

This is the T7-Path-A component of the T8 + T7-Path-A pair recommended in `docs/next_research_track_selection_plan_after_s9_park.md` section 15. The T8 component (record-only family-level park memo for SPY/TLT/GLD/USO 2014-2022 ETF-proxy universe) is authored separately as `reports/external_research_hunter/t8_spy_tlt_gld_uso_2014_2022_family_park_memo.md` in the same controller turn.

## 2. Candidate identification

| Field | Proposed value (subject to operator confirmation at SEAL) |
|---|---|
| `candidate_record_id` | `s10-d1-cross-asset-trend-or-meanrev-mnq-mgc-databento-long-history` |
| `candidate_family` | TBD at SEAL (one of: trend-following / mean-reversion / rotation / carry / vol-targeting -- the operator picks the mechanic family at SEAL based on the section 6 mechanic-family selection) |
| `is_a_trade_candidate` | true |
| `is_an_equity_universe_candidate` | false |
| `is_a_b006_001_revision` | false |
| `is_a_b006_002_revision` | false |
| `is_a_s7_d1_revision` | false |
| `is_a_s9_revision` | false |
| `predecessor_lineage_references_read_only` | `s7_d1_etf_proxy_park`, `s9_rsi2_etf_proxy_park`, `b006_001_archival`, `b006_002_archival`, `s10_d1_micro_availability_probe`, `t8_etf_proxy_family_park` |
| `diagnostic_only` | true |
| `not_promotable_via_this_diagnostic` | true |
| `default_advisory_label` | `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` |

## 3. Universe (proposed; LOCKED at SEAL)

| Field | Proposed value (LOCKED at SEAL) |
|---|---|
| Universe type | `two_symbol_fixed_basket_continuous_micro_futures` |
| Symbol 1 | `MNQ.c.0` (Micro E-mini Nasdaq-100, continuous front-month) |
| Symbol 2 | `MGC.c.0` (Micro Gold, continuous front-month) |
| `AddUniverse` calls | 0 (fixed symbol basket, no universe selection logic) |
| `removed_from_universe` events | structurally 0 |
| Common-history start (verified by S10-D1 probe) | 2019 onward (MNQ launched May 2019; MGC available from 2013 but common-history of pair starts at MNQ launch) |
| Excluded symbol | `MCL.c.0` (per S10-D1 memo: unreliable before 2021; excluded from this candidate's universe to preserve a clean common-history window starting in 2019) |
| Universe-membership integrity surface | structurally N/A (fixed two-symbol basket) |
| Diversification (to be measured at run; expected balanced) | `effective_independent_bets >= 1.5` expected for a 2-symbol basket; `avg_pairwise_dependence_measure <= 0.50` |

## 4. Data assumptions (proposed; LOCKED at SEAL)

| Field | Proposed value (LOCKED at SEAL) |
|---|---|
| Vendor | Databento Historical API |
| Dataset | `GLBX.MDP3` |
| Schema | `ohlcv-1d` (daily close); intraday schemas DEFERRED to a possible follow-up cycle if Tier-N IS verdict warrants |
| `stype_in` | `continuous` |
| Symbols | `["MNQ.c.0", "MGC.c.0"]` |
| Resolution conceptually used by signal | daily close |
| IS window start (proposed) | `2019-05-13` (MNQ launch-adjacent; S10-D1 probe verified availability on this date: 1,301 records) |
| IS window end (proposed) | `2023-12-29` (~4.6 years; permits clearing K9 with daily-bar density on 2 symbols at reasonable signal-firing rates) |
| OOS window (LOCKED at SEAL; never inspected at IS) | `2024-01-02` through `2025-12-30` (~2 years) |
| Post-OOS data | `2026-01-02 onward` (informational only; no diagnostic) |
| Operator-side fetch authorization required | YES (Step 02b-equivalent; no controller-side Databento call) |
| Fresh paid data download | YES (Databento per-tick or per-symbol pricing applies; budget impact to operator) |
| Local cache writes | NO `.dbn.zst` cache files written outside operator's explicit ingest directory |
| API key handling | reads `DATABENTO_API_KEY` from environment only at operator's Step 02b fetch turn; never echoed, logged, or saved |

The S10-D1 availability probe matrix is the authoritative reference for which dates have data on these symbols. Per `reports/external_research_hunter/s10_d1_micro_availability_probe_result_memo.json`: MNQ.c.0 has 1,301 records on 2019-05-13 and 1,380 records (full CME Globex session) by 2021-07-19; MGC.c.0 has 990 records on 2019-05-13 scaling to 1,358 by 2021-07-19. Both symbols clear the canonical 1,380-minute full-session count by 2021-07.

## 5. Strategy mechanic-family selection (DEFERRED to SEAL turn)

This plan does NOT lock the mechanic family. The mechanic family is chosen by the operator at the SEAL turn from one of the following four candidates, each of which addresses BOTH the s7 D1 (cost-stress sensitivity) and s9 (negative S0 edge) failure modes (per family-level park memo section 5 first-principles burden):

### 5.1 Option F1 -- Long-only trend-following with no pyramid

| Field | Value |
|---|---|
| Mechanic | Donchian-N entry / Donchian-M exit; LONG side only; NO pyramid (single contract per symbol per signal); ATR-based stop |
| First-principles for surviving P1 (s7 D1 cost-stress) | No pyramid removes the s7 D1 amplification mechanism; per-contract commission scales differently than per-share ETF; futures slippage is in ticks not bps |
| First-principles for surviving P2 (s9 negative S0 edge) | Trend-following on futures has a different edge profile than mean-reversion on ETF proxies; futures term-structure and overnight gap behavior may contribute |
| Expected trade count | ~20-40 per symbol over 4.6-year IS = 40-80 portfolio trades (borderline K9; may need to lower entry threshold within first-principles bounds) |
| Notes | Tightest first-principles burden; closest to s7 D1 family but explicitly addresses the pyramid lesson |

### 5.2 Option F2 -- Cross-sectional momentum rotation

| Field | Value |
|---|---|
| Mechanic | Monthly rebalance; rank 2 symbols by trailing 6-month total return; hold top 1 |
| First-principles for surviving P1 | Different signal logic (relative-strength) than absolute trend-following |
| First-principles for surviving P2 | Different family than mean-reversion |
| Expected trade count | ~12 rebalances/year * (~50% rank-change rate) = ~6 trades/year * 2 = ~28 portfolio trades over 4.6 years (likely fails K9) |
| Notes | High K9 risk; on 2 symbols rank-rotation is binary and noisy |

### 5.3 Option F3 -- Vol-targeted two-asset basket

| Field | Value |
|---|---|
| Mechanic | Equal-risk-contribution between MNQ and MGC; monthly rebalance; vol-targeted to portfolio-level realized vol annualized |
| First-principles for surviving P1 | Vol-targeting sizing addresses leverage / risk profile not signal generation |
| First-principles for surviving P2 | Long-only basket relies on equity-premium + gold-premium; not a signal edge claim |
| Expected trade count | ~12 rebalances/year * 2 symbols = ~24 contract-direction changes (K9 borderline-to-fail) |
| Notes | Tests sizing not signal; benchmark-class; B006_002 lessons (warmup guard + DR11 C4 enforcement) inheritable; check leverage-cap-bound-rate carefully (LESSON_B006_002_001) |

### 5.4 Option F4 -- Carry / term-structure mechanic

| Field | Value |
|---|---|
| Mechanic | Long when front-month basis is in backwardation (positive carry); flat or short when in contango |
| First-principles for surviving P1 | Carry-based mechanic is structurally different from trend-following |
| First-principles for surviving P2 | Carry-based mechanic is structurally different from mean-reversion |
| Expected trade count | depends on basis regime persistence; could be very low |
| Notes | Requires basis / front-month-next-month data, not just close; may require additional Databento ingest beyond ohlcv-1d; defer if heavier data scope |

The operator picks ONE of F1-F4 at the SEAL turn. The operator MAY propose a different mechanic family not enumerated here, but it must satisfy the family-level park memo section 5 first-principles burden.

## 6. Locked parameter values (DEFERRED to SEAL turn)

This plan does NOT lock any strategy parameter (TARGET_VOL, lookback, leverage cap, threshold, etc.). The full parameter set is locked by the operator at the SEAL turn. The DRAFT-to-SEAL flow mirrors the B006_001 / B006_002 pattern: each parameter has 2-3 enumerated options at DRAFT time, and the operator confirms at SEAL via an "all defaults A" or "revised to B/C" choice.

Anticipated parameter classes (locked at SEAL with their values):

| Class | Will be locked at SEAL | Example domain (subject to family selection) |
|---|---|---|
| `IS_WINDOW_START` | yes | `2019-05-13` (proposed) |
| `IS_WINDOW_END` | yes | `2023-12-29` (proposed) |
| `OOS_WINDOW_START` | yes | `2024-01-02` (proposed; locked but never inspected at IS) |
| `OOS_WINDOW_END` | yes | `2025-12-30` (proposed; locked but never inspected at IS) |
| Mechanic-specific signal parameters | yes | depends on F1-F4 selection |
| Sizing rule | yes | per-contract notional; 1% portfolio-equity risk per signal; ATR(20) stop distance; NO pyramid |
| Per-symbol cap | yes | 1 contract per symbol per signal (no pyramid; LESSON_B006_001_002 plus s7 D1 sibling lesson) |
| `START_CASH_USD` | yes | TBD; proposed `100000` |
| `WARMUP_DAYS` | yes | TBD; min `MAX(longest-lookback-in-mechanic, 220)` (B006 lineage) |
| `REBALANCES_PER_YEAR` (if rotation) | yes | TBD |

## 7. Cost stress + sizing stress matrices (LOCKED at SEAL)

Cost stress S0/S1/S2/S3 inherited byte-equivalent from s7 D1 / s9 framework with futures-specific adaptation:

| Tier | Label | Commission per contract USD | Slippage ticks |
|---|---|---|---|
| S0 | source_or_default | 0.00 | 0.0 |
| S1 | futures_low_slippage | 0.85 (typical micro futures) | 0.5 |
| S2 | futures_mid_slippage | 0.85 | 1.5 |
| S3 | futures_high_slippage | 0.85 | 3.0 |

Tick sizes (LOCKED at SEAL): `MNQ_TICK_SIZE = 0.25` (index points; $0.50/contract); `MGC_TICK_SIZE = 0.10` (gold dollars/oz; $1.00/contract; 10-oz contract). Exact dollar values per tick are verified against CME contract specs at SEAL.

The K1 (S0 edge sign) and K12 (S2/S3 degradation) gates from s7 D1 / s9 carry into this candidate byte-equivalent. The first IS run MUST include all four tiers; deferral to follow-up cycle is forbidden.

## 8. DR rules and K-gates (LOCKED at SEAL; inherited byte-equivalent from s7 D1 / s9 / B006_002 lineage)

Carried diagnostic rules:

- DR1 -- insufficient_trades_or_rebalances (`OOS rebalances < 36` or equivalent for chosen frequency)
- DR2 -- oos_metrics_degrade_materially_under_cost_stress (K12 component)
- DR3 -- zero_cost_only_survival (K12 component)
- DR4 -- oos_negative_while_is_positive_unexplained
- DR5 -- cost_stress_turns_edge_negative
- DR6 -- post_warmup_sizing_ambiguity_or_invalid (NARROWED per LESSON_B006_001_003; severity REJECT_FAST per LESSON_B006_002_002)
- DR7 -- missing_oos_or_date_window_evidence
- DR8 -- live_or_order_routing_path_detected (HARD_FAIL_VOIDED at Initialize)
- DR9 -- data_continuity_integrity_check (REDEFINED for the chosen universe; details locked at SEAL)
- DR10 -- turnover_cost_explosion (`annual_turnover > 0.50` threshold inherited)
- DR11 -- IF mechanic uses leverage cap: `c4_leverage_cap_bound_rate_exceeded` (threshold 0.10; severity REJECT_FAST; precedence position 3 per LESSON_B006_002_001)

K-gates (carried from s7 D1 / s9 framework byte-equivalent):

- K1 -- sharpe_proxy_per_trade_below_zero_at_S1
- K2 -- expectancy_per_trade_dollars_nonpositive_at_S1
- K4 -- trade_curve_max_drawdown_above_50pct
- K6 -- per_symbol_observed_win_rate_dispersion_above_threshold
- K7 -- silent_filter_introduction_after_lock
- K8 -- runtime_safety_invariant_false
- K9 -- closed_trades_below_100
- K10 -- avg_pairwise_dependence_above_threshold (0.50)
- K11 -- cap_binding_events_above_threshold
- K12 -- composite cost-stress fail (DR2 + DR3)

DR precedence chain (proposed; LOCKED at SEAL): inherits from B006_002 byte-equivalent if mechanic uses leverage cap (`DR7 -> DR1 -> DR11 -> DR9 -> DR10 -> DR6 -> DR4 -> DR2 -> DR3 -> DR5`). For non-leverage-cap mechanics, DR11 is REMOVED from the chain and the chain becomes `DR7 -> DR1 -> DR9 -> DR10 -> DR6 -> DR4 -> DR2 -> DR3 -> DR5`.

## 9. Runtime safety invariants (LOCKED at SEAL)

Inherits 11+ invariants from the B006_002 lineage byte-equivalent, with extension for futures-specific scope:

7 inherited B005_NNN framework invariants:
- `no_live_trading`
- `no_strategy_lab_promotion`
- `no_review_queue_mutation`
- `no_brokerage_connection`
- `no_external_network` (runtime)
- `no_databento_at_runtime_only_at_explicit_ingest_phase`
- `no_production_signal`

4 inherited B006_001 invariants:
- `no_strategy_optimization_authorized`
- `no_profitability_claim`
- `no_universe_membership_logic`
- `no_dr_redefinition_post_seal`

4 inherited B006_002 invariants (carried iff mechanic uses leverage cap):
- `no_warmup_order_submission`
- `c4_leverage_cap_bound_rate_must_be_enforced`
- `dr6_warmup_contamination_blocked`
- `no_b006_NNN_sealed_artifact_mutation`

NEW s10 D1-specific invariants (proposed; LOCKED at SEAL):
- `no_continuous_roll_stitch_modification_post_seal`
- `no_mcl_inclusion_under_long_history_scope`
- `no_intraday_schema_ingest_under_daily_only_design`
- `databento_api_key_read_from_env_only_never_logged_or_saved`

Total invariants in scope at SEAL: 15-19 depending on mechanic family selection.

## 10. Acceptance gates A1-A10 (LOCKED at SEAL; inherited byte-equivalent)

- A1: `total_closed_trades >= 100` over IS window
- A2: `sharpe_proxy_per_trade > 0` at S1 baseline
- A3: `expectancy_per_trade_dollars > 0` at S1 baseline
- A4: `trade_curve_max_drawdown_pct <= 50%`
- A5: `portfolio_win_rate_gap_to_breakeven_pp_at_s1 >= +0.5pp` AND `>= 1/2 symbols` showing positive WR-gap
- A6: upstream PASS (Step 02c audit clean)
- A7: `effective_independent_bets >= 1.5` (lowered from 2.5 for 2-symbol basket; documented at SEAL)
- A8: cost-stress matrix complete (all 4 tiers run in IS)
- A9: C1-C8 safety attestations present (Phase 2 safety template)
- A10: `cap_binding_events == 0` if mechanic has a per-symbol cap

The lowered A7 threshold (1.5 vs s7 D1's 2.5) reflects the smaller 2-symbol basket; SEAL turn locks the exact value. The selection plan's diversification requirement DV1 ("operate on at least 4 distinct asset families UNLESS the candidate is explicitly a single-symbol diagnostic justified by first-principles") is relaxed here by first-principles for a 2-symbol futures basket (equity-index + metals) -- justification: the two asset families are structurally distinct and the small basket is itself a deliberate design choice to limit Databento ingest scope on the first cycle.

## 11. Closed verdict enum + forbidden-token blocklist (UNCHANGED from B005_NNN / B006_NNN lineage)

```
PERMITTED_VERDICTS = (
    "REJECT_FAST",
    "INCONCLUSIVE_HOLD",
    "ELIGIBLE_FOR_HUMAN_REVIEW",
    "REQUEST_FULL_PREREGISTRATION_REVIEW",
    "PARKED_SAFE_BUT_NOT_MONEY_PROVEN",
)
FORBIDDEN_VERDICT_TOKENS = (
    "PASS", "APPROVE", "LIVE", "PROMOTE",
    "SIGNAL", "FOR_PRODUCTION", "EXECUTE", "ROUTE_ORDER",
)
```

Note: `PARKED_SAFE_BUT_NOT_MONEY_PROVEN` is added to the closed enum based on the s9 precedent. The SEAL turn confirms the final enum membership; the operator MAY remove `PARKED_SAFE_BUT_NOT_MONEY_PROVEN` from this candidate's enum if the operator prefers strict 4-verdict enum.

## 12. Low-log v2 QC-64K emission pattern (carried byte-equivalent from B006_002)

Note: this candidate is a Databento-track candidate, not a QuantConnect-track candidate, so the QC 64,000-char source limit and the low-log emission pattern do NOT directly apply unless the operator chooses to also run the diagnostic on QuantConnect in parallel. The default first-cycle path is Databento ingest + local Python simulator (mirroring s7 D1 / s9 / s8 D1 patterns), in which case the low-log emission pattern is replaced by a `reports/` sealed-artifact emission pattern.

If the operator chooses a parallel QC path at SEAL, the low-log markers become:
- `S10_D1_MNQ_MGC_LOW_LOG_DIAGNOSTIC_SUMMARY_BEGIN`
- `S10_D1_MNQ_MGC_LOW_LOG_DIAGNOSTIC_SUMMARY_END`
- `S10_D1_MNQ_MGC_LOW_LOG_DIAGNOSTIC_SUMMARY_SHA256=<hex>`
- `S10_D1_MNQ_MGC_LOW_LOG_FULL_REPORT_SHA256=<hex>`
- `S10_D1_MNQ_MGC_LOW_LOG_RUNNER_BUILD_TAG=<tag>`

The default path is Databento ingest + local Python simulator; QC is OPTIONAL.

## 13. NO STRATEGY OPTIMIZATION (explicit prohibition; mirrors B006_002 section 13)

| Prohibition | Status |
|---|---|
| No parameter tuning of any strategy constant post-SEAL | locked |
| No DR9 redefinition post-SEAL | locked |
| No optimization of cost stress S0..S3 post-SEAL | locked |
| No optimization of DR11 threshold (if present) post-SEAL | locked |
| No optimization of DR6 severity / window post-SEAL | locked |
| If unfavorable verdict -> response | archive candidate under that verdict; do not modify any parameter or DR rule |
| Runner is a deterministic, parameter-free reproducer of the sealed spec | locked |

## 14. Kill criteria K1-K8+ (LOCKED at SEAL)

Inherits from B006_002 section 14 with futures-specific adaptation:

- K1 -- any DR rule fires REJECT_FAST
- K2 -- DR9 data_continuity_integrity_failure with > 5 violations
- K3 -- DR6 post-warmup invalid-sizing event count > 0
- K4 -- DR11 c4_leverage_cap_bound_rate_exceeded (only if mechanic uses leverage cap)
- K5 -- any forbidden-verdict-token in runner output
- K6 -- runner attempts SetLiveMode / SetBrokerageModel / DeployAlgorithm / unauthorized network call
- K7 -- order-submit attempt while in warmup window
- K8 -- runner mutates any B006_NNN / s7 D1 / s9 / t8 sealed artifact (byte-shift)
- NEW K9 -- runner makes a Databento API call outside the explicitly authorized Step 02b ingest phase
- NEW K10 -- runner caches `.dbn.zst` files outside the operator's explicit ingest directory
- NEW K11 -- runner accesses `DATABENTO_API_KEY` outside the explicitly authorized ingest phase

## 15. Continue criteria C1-C5+ (LOCKED at SEAL)

Inherits from B006_002 section 15 with futures-specific adaptation:

- C1 -- all DR latent-eval `would_have_fired = False`
- C2 -- OOS S0 Sharpe > 0 (deferred from IS-only diagnostic; IS-side equivalent: IS S0 Sharpe > 0)
- C3 -- OOS max drawdown >= -30% (IS-side equivalent: IS max drawdown >= -30%)
- C4 -- leverage cap binds at <= 10% of eligible rebalances (only if mechanic uses leverage cap; runner-enforced via DR11)
- C5 -- cost-stress matrix positive Sharpe at all tiers S0/S1/S2/S3 -> `ELIGIBLE_FOR_HUMAN_REVIEW`
- C5+ -- all 4 cost tiers Sharpe > 0.5 -> `REQUEST_FULL_PREREGISTRATION_REVIEW`

Even `REQUEST_FULL_PREREGISTRATION_REVIEW` does NOT unlock live, does NOT grant FRC, does NOT promote to Strategy Lab.

## 16. Phase ladder (each phase separately authorized)

| # | Phase | Status (this plan turn) | Authorization template |
|---|---|---|---|
| 0 | Selection plan | implicit via `docs/next_research_track_selection_plan_after_s9_park.md` | -- |
| 1 | Family-park memo (T8) | COMPLETE this controller turn (sibling artifact authored) | -- |
| 2 | Tier-N spec PLAN (this document) | COMPLETE this controller turn | -- |
| 3 | Tier-N spec DRAFT | NOT AUTHORIZED | `Authorize s10 D1 MNQ+MGC Databento long-history Tier-N spec DRAFT` |
| 4 | Tier-N spec SEAL | NOT AUTHORIZED | `Authorize s10 D1 MNQ+MGC Databento long-history Tier-N spec SEAL` |
| 5 | Step 02b -- Databento operator-side data fetch authorization | NOT AUTHORIZED | `Authorize s10 D1 MNQ+MGC Step 02b operator-side Databento fetch only` |
| 6 | Step 02c -- raw-data audit | NOT AUTHORIZED | `Authorize s10 D1 MNQ+MGC Step 02c raw-data audit only` |
| 7 | Step 03 -- loader module BUILD | NOT AUTHORIZED | `Authorize s10 D1 MNQ+MGC Step 03 loader BUILD only` |
| 8 | Step 04 -- validator module BUILD | NOT AUTHORIZED | `Authorize s10 D1 MNQ+MGC Step 04 validator BUILD only` |
| 9 | Step 05 -- signal module BUILD | NOT AUTHORIZED | `Authorize s10 D1 MNQ+MGC Step 05 signal BUILD only` |
| 10 | Step 06 -- simulator module BUILD | NOT AUTHORIZED | `Authorize s10 D1 MNQ+MGC Step 06 simulator BUILD only` |
| 11 | Step 07 -- aggregator module BUILD | NOT AUTHORIZED | `Authorize s10 D1 MNQ+MGC Step 07 aggregator BUILD only` |
| 12 | IS decision memo + park or eligibility | NOT AUTHORIZED | `Authorize s10 D1 MNQ+MGC IS decision memo only` |

This plan authors ONLY phase 2 (the spec PLAN). Every subsequent phase requires its own separately authorized turn. Phase 5 (Databento fetch) carries the explicit operator-side scope -- the controller does NOT call Databento at any phase.

## 17. Boundaries held this PLAN turn

| Boundary | Status |
|---|---|
| PLAN only (no spec SEAL, no BUILD, no fetch) | met |
| No strategy code | met |
| No backtest | met |
| No simulator run | met |
| No signal computation | met |
| No data fetch | met |
| No yfinance / Yahoo Finance call | met |
| No Databento call | met |
| No `DATABENTO_API_KEY` access | met |
| No network IO | met |
| No live trading | met |
| No candidate promotion | met |
| No modification of s7 D1 / s9 / B006_001 / B006_002 sealed artifacts | met -- byte-stable |
| No modification of ORB branch artifacts or Step 30 cost constants | met |
| No modification of CLAUDE.md / docs/decisions.md / RUNBOOK / pipeline_manifest / .gitignore | met |
| No modification or staging of `brain_memory/projects/trading_bot/lessons.md` (dirty + unstaged from prior session; left untouched) | met |
| No mutation of `review_queue.json` | met |
| No mutation of production `idea_memory` | met |
| No profitability claim | met |
| Trading status | `PAUSED` |
| Live status | `BLOCKED_AT_6_GATES` |
| FRC | `NEVER_GRANTED` |
| `no_strategy_optimization_authorized` | TRUE |

## 18. Files written this PLAN turn (this document scope)

| File | Purpose |
|---|---|
| `docs/s10_d1_mnq_mgc_databento_long_history_tier_n_spec_plan.md` | This Tier-N spec plan (the plan to seal; no spec is sealed by this plan) |

The sibling artifacts authored in the same controller turn under the same authorization (and committed together with this file by the operator's git sequence) are:

- `reports/external_research_hunter/t8_spy_tlt_gld_uso_2014_2022_family_park_memo.md` (T8 family-level park memo body)
- `reports/external_research_hunter/t8_spy_tlt_gld_uso_2014_2022_family_park_memo.json` (T8 memo companion JSON with `report_seal_sha256`)

No other repository file is modified by this plan. The `brain_memory/projects/trading_bot/lessons.md` dirty + unstaged state from prior controller-session appends remains untouched.

## 19. Validation gates and HALT conditions for this plan

Validation gates the plan-authoring turn satisfies:

V1. ASCII-only.
V2. Numbered sections in monotonic order (1..21).
V3. No execution language (no "seal the spec now"; no "fetch data now"; no "run the simulator now").
V4. No self-authorization (this plan does NOT authorize the Tier-N spec to be DRAFTed or SEALed; only a separate operator turn does that).
V5. No code modification.
V6. No backtest run.
V7. No simulator run.
V8. No signal computation.
V9. No data fetch.
V10. No network IO.
V11. No live trading.
V12. No prior-phase artifact modification.
V13. The committed plan file is the ONLY new docs/ file changed in this turn's commit (paired with the two T8 memo files in reports/).
V14. The brain_memory dirty `lessons.md` remains UNSTAGED and UNTOUCHED.

HALT conditions:

H1. If any V-gate fails, the plan-authoring turn HALTs.
H2. If the pre-stage git index is non-empty, the turn HALTs and remediates by unstaging contaminants before staging the planning files.
H3. If the staged file count is anything other than 3 at commit time, the turn HALTs and remediates.
H4. If a staged file is anything other than one of the three planning artifacts named in section 18, the turn HALTs and remediates.
H5. If the dirty `lessons.md` is accidentally staged, the turn HALTs and `git restore --staged brain_memory/projects/trading_bot/lessons.md` before retrying.

## 20. Next-step authorization scope

The next operator authorization in the established controller-session pattern shall use one of these scopes:

- `Authorize s10 D1 MNQ+MGC Databento long-history Tier-N spec DRAFT` -- begin the DRAFT-to-SEAL flow on the chosen mechanic family from section 5.
- `Authorize s10 D1 MNQ+MGC Step 02b operator-side Databento fetch only` -- skip directly to operator-side ingest if the operator wants to verify data scope before committing to a mechanic family (the DRAFT-to-SEAL flow would then follow with the ingested data confirmed available).
- `Authorize alternative track selection plan revision only` -- if the operator rejects the T7-Path-A direction in favor of a different track from `docs/next_research_track_selection_plan_after_s9_park.md` section 14.
- `Authorize family-level park only without opening new track` -- if the operator accepts the T8 memo as sufficient consolidation and chooses to NOT open the T7-Path-A futures track at this time.
- `Authorize cross-domain pivot only` -- if the operator pivots to a different project entirely.

This plan is the source of truth for the s10 D1 MNQ+MGC Databento long-history track's intended Tier-N spec scope. Future plans, DRAFTs, SEALs, or BUILDs that contradict this plan require either a fresh plan revision or an out-of-band justification.

## 21. No-live status carried forward

| Field | Value |
|---|---|
| Trading | `PAUSED` |
| Live mode | `BLOCKED_AT_6_GATES` |
| FRC | `NEVER_GRANTED` |
| Six live-trading gates remain BLOCKED regardless of any future verdict | TRUE |
| `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` advisory label applies to any candidate descended from this plan | TRUE |
| `no_strategy_optimization_authorized` | TRUE |

----

End of plan. Plan-authoring turn only. No code. No backtest. No simulator. No signal. No data fetch. No yfinance. No Yahoo Finance. No Databento. No DATABENTO_API_KEY access. No brokerage. No real order. No paper order. No Strategy Lab promotion. No review_queue mutation. No production idea_memory mutation. No ORB branch mutation. No lessons.md modification or staging. No live trading. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES.
