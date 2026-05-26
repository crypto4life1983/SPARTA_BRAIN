# s8-D1 No-Pyramid - P7 In-Sample Decision Memo (SEALED, PLAN-ONLY)

**Phase:** `P7_IN_SAMPLE_DECISION_MEMO_SEALED`
**Operational status:** `DECISION_MEMO_SEALED_AWAITING_P8_LIFECYCLE_TRANSITION`
**Report date UTC:** 2026-05-26T00:54:22Z

**Decision memo seal:** `e26d00587d39404d8db52717f66e5a2792aea34a59763e36da380ae9205561cb`
**Predecessor (P6.5 cost-stress matrix) seal:** `edae2e56cf16c92555bbf9dfaa2d773f49e3e68ce12141c6d541753f52d17ded`

> Labels: DIAGNOSTIC_ONLY_NOT_LIVE_GRADE, NO_FRC_GRANTED, S8_D1_P7_DECISION_MEMO_SEALED,
> SINGLE_DELTA_FROM_S7_D1_MAX_UNITS_1, NO_S7_D1_REVIVAL
> Trading: PAUSED | Live: BLOCKED_AT_6_GATES | FRC: not granted
> No profitability claim. READY_FOR_LONGER_BACKTEST is a research label only.

---

## Evidence summary: P6 in-sample baseline (S1 cost tier)

| Field | Value |
|---|---|
| C7 verdict | **READY_FOR_LONGER_BACKTEST** |
| K-fires | **NONE** (0 count) |
| closed_trades_portfolio | 111 |
| net_pnl_usd | $193,483 |
| expectancy_per_trade_usd | $1,743.09 |
| win_rate_pct | 39.6396% |
| win_rate_gap_to_breakeven_pp | +16.50pp |
| pl_ratio | 3.32 |
| sharpe_proxy_per_trade | +0.2250 |
| trade_curve_maxdd_pct | -23.8341% |
| all 4 markets profitable | **True** |
| no_pyramid_invariant_pass | True |
| safety_all_zero | True |

Per-market:

- **CL**: trades=17, net=$60,600, wr=47.06%
- **GC**: trades=28, net=$16,300, wr=35.71%
- **NQ**: trades=18, net=$30,111, wr=44.44%
- **ZN**: trades=48, net=$86,471, wr=37.50%

---

## Evidence summary: P6.5 cost-stress matrix

- A8 (cost-stress S0-S4 RUN AND DR not fired): **True**
- K12 (REJECT_FAST via DR2/DR3/DR5): **False**
- DR2-like in-sample S1->S2/S3 material degradation: False
- DR3 (zero-cost-only survival): False
- DR5 (S0->S1 edge flips negative): False
- No-pyramid invariant all 5 tiers pass: **True**

| Tier | trades | sharpe | expect/trade | MaxDD% | K-fires | survives? |
|---|---|---|---|---|---|---|
| S0 | 112 | 0.2296 | $1,769.78 | -22.94% | NONE | True |
| S1 | 111 | 0.2250 | $1,743.09 | -23.83% | NONE | True |
| S2 | 108 | 0.2071 | $1,477.38 | -20.76% | NONE | True |
| S3 | 107 | 0.1994 | $1,425.57 | -22.11% | NONE | True |
| S4 | 99 | 0.1571 | $1,001.09 | -23.92% | K9 | False |

- Survives all 5 tiers under K-gate eval: **False** (S4 K9 by 1 trade; S4 is 'informational only' per Tier-N spec)
- Total fresh-run wall: 1032.5s

---

## Contrast: s8-D1 vs s7-D1 (single-delta outcome comparison)

| Metric | s7-D1 (with pyramid 4u) | s8-D1 (no pyramid, max_units=1) |
|---|---|---|
| closed_trades | 313 | 111 |
| win_rate_pct | 43.13% | 39.64% |
| win_rate_gap_to_breakeven_pp | +14.17pp | +16.50pp |
| sharpe_proxy_per_trade | 0.1920 | **0.2250** (improved) |
| expectancy_per_trade_usd | $3,667 | $1,743 |
| pl_ratio | 2.45 | **3.32** (improved) |
| trade_curve_maxdd_pct | **-221.67%** | **-23.83%** |
| all_markets_profitable | False | True |
| K_fires | ['K4'] | NONE |
| C7 verdict | READY_FOR_LONGER_BACKTEST (with K4 firing in parallel) | READY_FOR_LONGER_BACKTEST (no K fires) |

Removing pyramid (max_units 4 -> 1) reduced MaxDD by ~9.3x (from -221.67% to -23.83%) while preserving the cross-asset signal direction. Sharpe and P/L-ratio both IMPROVED. All 4 markets now profitable (vs s7-D1 had GC losing). Per-trade expectancy halved in absolute terms ($1,743 vs $3,667) because winners no longer pyramid-amplify, but risk-adjusted return is materially better. Trade count dropped from 313 to 111 (still >= K9=100).

s7-D1 parking status (cited for comparison only; NOT revived): `PARKED_SAFE_BUT_NOT_MONEY_PROVEN`

---

## Remaining caveats (honest qualifications)

### K10_correlation_not_computed

Tier-N spec rejection_gate K10 = `avg_pairwise_correlation > 0.50` over 2013-01-01..2022-12-30; the driver does NOT compute this at runtime; K10 status is UNKNOWN.

- **preregistered_status_in_tier_n_spec**: RejectionGate; firing -> PARKED_FAILED_AT_DIVERSIFICATION_HYPOTHESIS
- **consequence_if_fires_later**: The cross-asset diversification hypothesis that motivated D1 selection from the S8 plan would be falsified, mandating a park.
- **compute_feasibility**: Computing K10 is mechanically cheap: pairwise daily-return correlation across NQ/GC/ZN/CL over 10 years from the same DBN cache; ~minutes of additional runtime (4 markets -> 6 pairs).
- **recommended_disposition**: Compute K10 BEFORE any OOS authorization deliberation.

### OOS_window_not_inspected

OOS window 2023-01-01..2025-12-30 has NOT been loaded, decoded, or evaluated. Per plan-lock invariant `oos_inspection_during_in_sample_run_prohibited = True`, OOS remains untouchable until in-sample passes all preregistered gates AND a separate explicit OOS authorization is issued.

- **preregistered_status**: Hard boundary
- **consequence**: In-sample alone is INSUFFICIENT evidence for any live-trading recommendation, even at READY_FOR_LONGER_BACKTEST verdict.

### sample_size_modest

P6 baseline closed_trades_portfolio = 111 (margin of 11 above K9 threshold of 100). Cost-stress S4 dropped to 99 (K9 fires by 1 trade at S4 only; S4 is preregistered as 'tail stress, informational only').

- **implication**: Statistical power for per-market sub-analyses is constrained (NQ=18, GC=28, ZN=48, CL=17). Per-market expectancy estimates have wide confidence intervals at these sample sizes.
- **mitigation_options**:
  - Accept as-is (the candidate cleared K9 at S0/S1/S2/S3; tier_n_spec gates are met)
  - Schedule OOS-augmentation to grow effective sample (each OOS-confirmed trade adds independent information)
  - Author a fresh _revN_ that extends in-sample to 2010-2022 (would re-fetch ~3 years extra; requires separate operator-side fetch)

### live_remains_blocked_permanently

6-gate live-block applies regardless of any verdict in this memo. FRC has never been granted to this candidate or any candidate in the chain. live_promotion_path_closed = True.

- **no_profitability_claim**: True
- **READY_FOR_LONGER_BACKTEST_is_research_label_only**: True

### no_profitability_claim

This memo records what was observed in-sample under preregistered methodology. Past performance in-sample is NOT predictive of OOS performance or live performance. The result is DIAGNOSTIC ONLY.


### DR4_not_evaluable_this_chain

DR4 (IS positive but OOS negative at S0 baseline -> ESCALATE) is not evaluable in-sample-only. It becomes evaluable only after OOS is run, which is BLOCKED until separate authorization.


### K10_status_blocks_strong_OOS_recommendation

Because K10 has not been computed, the in-sample evidence is INCOMPLETE relative to the preregistered K-criteria set. A strong OOS-AUTHORIZATION recommendation requires K10 evidence either way.


---

## RECOMMENDATION

### Primary: **`PARK_PROVISIONAL_PENDING_K10`**

### Secondary fallback (if operator judges K10 unnecessary): `OOS_AUTHORIZATION_DELIBERATION`

### Rationale

The s8-D1 candidate is the cleanest in-sample result in the entire chain: 0 K-fires at S1 baseline, A8 PASS on cost-stress matrix, K12 not fired, no-pyramid invariant pass across all 5 tiers, all 4 markets profitable, MaxDD ~9.3x lower than s7-D1. HOWEVER, the preregistered K10 rejection_gate (avg_pairwise_correlation > 0.50) has NOT been computed; the entire premise of cross-asset Donchian selection (D1 at 39/40 in the S8 plan) rests on the assumption that the 4-market universe maintains low average correlation, enabling diversification. Going to OOS without K10 risks the failure mode where OOS deliberation is granted, then K10 is computed and fires, then the candidate parks anyway -- wasting operator attention. Computing K10 first is cheap and high-information: pass -> strengthens the OOS-AUTHORIZE case substantially; fire -> PARKED_FAILED_AT_DIVERSIFICATION_HYPOTHESIS per Tier-N spec, ending the candidate's lifecycle cleanly.

### Why other options were not selected

- **OOS_AUTHORIZATION_DELIBERATION**: Premature without K10 evidence. The cross-asset diversification hypothesis is load-bearing to the entire D1 selection (S8 plan scored 39/40 specifically because D1 'directly tests the unfixed K4 root cause' on a low-correlation universe). K10 should be evidenced before OOS attention is invested.
- **PARK_SAFE_BUT_NOT_MONEY_PROVEN**: Overly conservative. K10 not computed is an OPEN evidence gap, not a fire. Parking this candidate as PARKED_SAFE_BUT_NOT_MONEY_PROVEN before computing K10 would prematurely lock in a parking-with-known-unevaluated-gate state when the gate is cheap to evaluate.
- **FRESH_S9_REQUIRED**: Unwarranted by the evidence. The s8-D1 candidate cleared every preregistered K-gate that was evaluated. Nothing in the result mandates a fresh candidate. A fresh s9-* should be reserved for cases where the candidate's evidence is exhausted negative.

### What this memo does NOT authorize

- OOS data load / decode / inspection / metric compute
- K10 computation (requires separate authorization)
- P8 lifecycle transition (requires separate authorization based on K10 outcome)
- Code patch or driver modification
- Cost-stress matrix re-run
- Live trading change
- Paper trading change
- Scheduler change
- review_queue.json mutation
- obsidian-trade-logger touch
- Strategy Lab promotion
- FRC grant

### Honest qualification

READY_FOR_LONGER_BACKTEST is a research label only; 6-gate live-block applies regardless. This memo does NOT recommend live trading. This memo does NOT recommend paper trading. This memo records the s8-D1 candidate's in-sample diagnostic posture and recommends the next research step, which is K10 computation.

---

## K10 computation plan (separate authorization required)

**Purpose**: Compute K10 (avg_pairwise_correlation > 0.50) over 2013-01-01..2022-12-30 across NQ/GC/ZN/CL daily returns.

**Required authorization line**: `AUTHORIZE S8-D1 P7.5 K10 correlation computation (PLAN+RUN combined; mechanical compute only)`

**Inputs**:

- data_source: Existing local Databento cache only (480 files, 129,789,451 bytes; s7-D1 P5 cache reused; no fetch)
- decode: db.DBNStore.from_file via the existing in_sample_driver's derive_rth_daily_bars (or a fresh helper that mirrors it)
- computation: For each market, derive daily RTH OHLCV per existing driver semantics; compute daily log-returns; compute Pearson correlation across the 6 unique market pairs (NQ-GC, NQ-ZN, NQ-CL, GC-ZN, GC-CL, ZN-CL); report per-pair correlation + average pairwise correlation.
- K10_criterion: K10 fires iff avg_pairwise_correlation_over_in_sample > 0.50

**Outputs**:

- json_md_pair: reports/external_research_hunter/s8_d1_cross_asset_donchian_no_pyramid_k10_correlation_result_sealed.{md,json}
- sealed_via: LESSON_HUNTER_004 canonical roundtrip
- contents: per-pair correlation matrix, average pairwise correlation, K10 fire status, sealed-chain inheritance

**Expected runtime**: ~5-10 minutes wall (decoding for correlation needs the full daily-bar set, same as the s8-D1 driver does)

**Boundaries for the K10 run**:

- Local cache only
- No fetch
- No db.Historical
- No QC
- No network
- No OOS inspection
- No live/paper trading change
- No code patch
- No s7-D1 file modification
- No D5/B005_001/NKE/s7-D1 revival
- No profitability claim
- Do not commit until separately authorized

**Downstream after K10**:

- **if_K10_pass_avg_corr_le_0_50**: P8 lifecycle transition becomes OOS-AUTHORIZATION_DELIBERATION candidate; would require fresh operator authorization for both the P8 sealed transition and the actual OOS run plan.
- **if_K10_fires_avg_corr_gt_0_50**: P8 lifecycle transition records PARKED_FAILED_AT_DIVERSIFICATION_HYPOTHESIS per Tier-N rejection_gates; s8-D1 candidate parks permanently; chain continues to s9-* alternative direction (e.g., D3 from S8 plan).

---

## P8 lifecycle transition decision tree

- **if_K10_passes** -> `READY_FOR_OOS_AUTHORIZATION_DELIBERATION`; next authorization: `AUTHORIZE S8-D1 P8 lifecycle transition + OOS authorization plan (PLAN-ONLY)`
- **if_K10_fires** -> `PARKED_FAILED_AT_DIVERSIFICATION_HYPOTHESIS`; next authorization: `AUTHORIZE S8-D1 P8 lifecycle transition to PARKED_FAILED_AT_DIVERSIFICATION_HYPOTHESIS`
- **if_K10_computation_blocked_for_any_reason** -> `DEFAULT_PARK_SAFE_BUT_NOT_MONEY_PROVEN_PENDING_K10`; next authorization: `AUTHORIZE S8-D1 P8 default park (preserves all evidence; no live/paper changes)`

---

## s7-D1 non-revival attestation

- `s7_d1_chain_status`: PERMANENTLY_PARKED_AT_COMMIT_f08220a
- `s7_d1_revived_by_this_memo`: False
- `s7_d1_used_as`: UPSTREAM_EVIDENCE_AND_PARKED_REFERENCE_ONLY (parking_status=PARKED_SAFE_BUT_NOT_MONEY_PROVEN; cited for delta-contrast only)
- `s7_d1_strategy_logic_not_revived`: True
- `no_max_units_iteration_under_s8_d1_namespace`: True
- `any_future_max_units_value_neq_1_requires_fresh_candidate_record_id`: True

---

## Parent chain (10 parents byte-stable at authorship)

- `P6_5_cost_stress_matrix`: `edae2e56cf16c925...`
- `P6_in_sample_diagnostic`: `07a3fa91509f2206...`
- `P4_smoke_pass`: `1ab57a67f1a81be5...`
- `in_sample_driver_build`: `d7b82d7adad62979...`
- `runner_build`: `e1f2a13cb860a629...`
- `phase2_plan`: `5e6fccd1aeb40db7...`
- `plan_lock`: `612abbbda7235c8c...`
- `tier_n_spec`: `8cff6babf8e4a451...`
- `selection_plan`: `6b7bdb4c350f4a77...`
- `s7_d1_parking_report_comparison`: `551fdce46c0e373e...`

Drift count: **0**

---

## Negative invariants this turn (all True)

- `no_b005_001_revival`: True
- `no_code_patch`: True
- `no_cost_stress_rerun`: True
- `no_d5_revival_neither_s7_ym_only_nor_s8_zn_only`: True
- `no_data_fetch`: True
- `no_databento_api_call`: True
- `no_db_historical_instantiated`: True
- `no_frc_granted`: True
- `no_live_trading_change`: True
- `no_network_call`: True
- `no_new_backtest`: True
- `no_nke_revival`: True
- `no_obsidian_trade_logger_mutation`: True
- `no_oos_inspection`: True
- `no_paper_trading_change`: True
- `no_profitability_claim`: True
- `no_qc_call`: True
- `no_review_queue_mutation`: True
- `no_s7_d1_file_modification`: True
- `no_s7_d1_revival`: True
- `no_scheduler_change`: True
- `no_strategy_lab_promotion`: True
- `no_threshold_loosening`: True

---

*End of s8-D1 P7 in-sample decision memo. Plan-only; sealed at `e26d00587d39404d8db52717f66e5a2792aea34a59763e36da380ae9205561cb`. No new backtest. No OOS. No code patch. No live or paper trading change. No s7-D1 revival.*
