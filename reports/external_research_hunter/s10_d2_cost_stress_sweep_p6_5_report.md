# S10-D2 P6.5 Cost-Stress Sweep Report (SEALED)

**Schema:** `sparta.s10.d2.cost_stress_sweep_p6_5_report.v1`
**Phase:** `S10_D2_P6_5_COST_STRESS_SWEEP`
**Phase prefix:** `PHASE2-S10-D2-XAD-RC-P6.5`
**Controller session:** THIS_SESSION_ONLY
**Sealed at (UTC):** `2026-05-27T03:00:42Z`

**Candidate record id:** `s10-cross-asset-donchian-no-pyramid-reparam-cap-nq-gc-zn-cl`
**Tier-N spec seal:** `f5ca5ee63024e9c8b7b1e85762558ec35eb3d4ebb9ce2a160cbe0f1a0e80a679`
**Prior P6 IS diagnostic commit:** `d6977631c9ca8d851a357117794a183c3bf785fd`
**Prior P6.5 HALT (superseded; preserved in history):** `e89236f918b3ce7c70e87397488fb083dd38e24e`
**Cache restructure commit:** `1ddf441653b4ff385bc9405435532cf3f63337d6`

## Overall verdict: **`READY_FOR_LONGER_BACKTEST`**

**Summary label:** `S10_D2_P6_5_COST_STRESS_SURVIVES_READY_FOR_LONGER_BACKTEST_PRELIMINARY`

Cost-stress matrix survives (K12 does NOT fire; DR2/DR3/DR5 all clear). No other evaluated K fires at S1 baseline. Per Tier-N s8-D1 closed-enum, this maps to READY_FOR_LONGER_BACKTEST. Verdict_never_means_live_ready remains True.

> P6.5 cost-stress sweep only. No Databento call. No DATABENTO_API_KEY
> access. No data fetch. No OOS inspection. verdict_never_means_live_ready: True.

---

## 1. Cost-stress matrix (S0/S1/S2/S3)

| Tier | trades | net_pnl USD | sharpe pt | expectancy | maxdd % | wr % | wr gap pp | safety zero | cap binding |
|---|---|---|---|---|---|---|---|---|---|
| S0 | 200 | 987,241.79 | 0.14502 | 4,936.21 | -27.97 | 35.00 | 10.60 | True | 0 |
| S1 | 200 | 973,097.86 | 0.14311 | 4,865.49 | -28.31 | 35.00 | 10.48 | True | 0 |
| S2 | 200 | 913,849.33 | 0.14003 | 4,569.25 | -29.76 | 35.00 | 10.10 | True | 0 |
| S3 | 200 | 824,422.94 | 0.13004 | 4,122.11 | -30.35 | 34.50 | 9.31 | True | 0 |

Per-tier durations (seconds):
- S0: 264.769
- S1: 258.905
- S2: 245.449
- S3: 223.857

## 2. DR rule evaluation

- **DR2 (S2 or S3 degrades >= 50% vs S1 OR flips negative):** **False**
  - threshold_fraction: 0.5
  - `s1_net_pnl_usd`: 973097.8604674297
  - `s2_net_pnl_usd`: 913849.3343541666
  - `s3_net_pnl_usd`: 824422.9364594615
  - `s2_degraded`: False
  - `s3_degraded`: False
- **DR3 (S0 positive AND any of S1/S2/S3 non-positive):** **False**
  - `s0_positive`: True
  - `s0_net_pnl_usd`: 987241.7923144549
  - `s1_non_positive`: False
  - `s2_non_positive`: False
  - `s3_non_positive`: False
- **DR5 (S0 positive AND S1 non-positive):** **False**
  - `s0_net_pnl_usd`: 987241.7923144549
  - `s1_net_pnl_usd`: 973097.8604674297

### K12 (DR fires on cost stress): **`False`**

## 3. K-gate evaluation at S1 baseline + K12 matrix

- **K_fires_count:** 0
- **K_fires_list:** `[]`

| K | Fired | Value |
|---|---|---|
| K1 sharpe<0 | False | 0.14311192966266303 |
| K2 expectancy<=0 | False | 4865.489302337149 |
| K4 maxdd>50 magnitude | False | -28.305996161770587 |
| K6 safety_warnings>0 | False | safety_zero=True |
| K9 closed_trades<100 | False | 200 |
| K11 cap_binding>1000 | False | 0 |
| K12 DR_fires | False | DR2=False DR3=False DR5=False |

Note: K10 (avg pairwise dependence) is a separate diagnostic; not evaluated by this sweep (pre-existing gap).

## 4. S1 parity check vs previously sealed P6 IS diagnostic

- previously sealed commit: `d6977631c9ca8d851a357117794a183c3bf785fd`

| Metric | Previously sealed | Observed this sweep | Match |
|---|---|---|---|
| `closed_trades_portfolio` | 200 | 200 | True |
| `expectancy_per_trade_usd` | 4865.49 | 4865.49 | True |
| `sharpe_proxy_per_trade` | 0.143112 | 0.143112 | True |
| `trade_curve_maxdd_pct` | -28.31 | -28.31 | True |
| `win_rate_gap_to_breakeven_pp` | 10.48 | 10.48 | True |
- **match_closed_trades:** True
- **match_expectancy_within_1_dollar:** True
- **match_sharpe_within_001:** True
- **match_maxdd_within_01_pct:** True

## 5. Negative invariants (all True)

- `no_branch_change`: **True**
- `no_brokerage_connection`: **True**
- `no_cache_modification`: **True**
- `no_cache_restructure_report_modification`: **True**
- `no_candidate_promoted`: **True**
- `no_data_fetch`: **True**
- `no_databento_api_key_access`: **True**
- `no_databento_call`: **True**
- `no_git_push`: **True**
- `no_idea_memory_mutation`: **True**
- `no_in_sample_driver_code_modification`: **True**
- `no_key_leakage`: **True**
- `no_lessons_md_staged_or_modified`: **True**
- `no_live_trading`: **True**
- `no_oos_cache_touched`: **True**
- `no_oos_computation`: **True**
- `no_oos_inspection`: **True**
- `no_orb_artifact_modified`: **True**
- `no_paper_order_placed`: **True**
- `no_phase2_plan_modification`: **True**
- `no_plan_lock_modification`: **True**
- `no_real_order_placed`: **True**
- `no_review_queue_mutation`: **True**
- `no_runner_harness_code_modification`: **True**
- `no_s10_d1_artifact_modified`: **True**
- `no_s10_d2_p6_5_halt_report_in_history_modified`: **True**
- `no_s10_d2_p6_is_diagnostic_committed_artifact_modification`: **True**
- `no_s4_tier_run`: **True**
- `no_s7_artifact_modified`: **True**
- `no_s8_d1_artifact_modified`: **True**
- `no_s9_artifact_modified`: **True**
- `no_step_30_cost_constant_modified`: **True**
- `no_strategy_lab_invoked`: **True**
- `no_tier_n_spec_modification`: **True**

## 6. Status

- Trading status: `PAUSED`
- Live status: `BLOCKED_AT_6_GATES`
- FRC granted: `False`
- Advisory label permanent: `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE`

## 7. Labels

- `S10_D2_P6_5_COST_STRESS_SWEEP_COMPLETE`
- `S0_S1_S2_S3_COST_TIERS_EVALUATED`
- `K12_DR2_DR3_DR5_REPORTED`
- `K12_FIRES=False`
- `K_FIRES_COUNT=0`
- `OVERALL_VERDICT_READY_FOR_LONGER_BACKTEST`
- `NO_S4_RUN`
- `NO_DATABENTO_CALL`
- `NO_DATABENTO_API_KEY_ACCESS`
- `NO_OOS_COMPUTATION`
- `NO_REVIEW_QUEUE_MUTATION`
- `NO_STRATEGY_LAB_PROMOTION`
- `NO_LIVE_TRADING`
- `VERDICT_NEVER_MEANS_LIVE_READY`

## 8. Seal verification

```
seal_method = sha256 over json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False) EXCLUDING report_seal_sha256 + seal_method

report_seal_sha256 = <see JSON report_seal_sha256 field>
```

**P6.5 cost-stress sweep sealed. K12 fires: False. Verdict: READY_FOR_LONGER_BACKTEST. Trading: PAUSED. Live: BLOCKED_AT_6_GATES. FRC never granted.**

