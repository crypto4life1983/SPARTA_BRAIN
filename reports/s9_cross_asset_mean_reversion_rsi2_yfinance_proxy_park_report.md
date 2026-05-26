# s9 RSI-2 (ETF-Proxy) -- Lifecycle Park Report (SEALED)

**Schema:** `sparta.s9.rsi2.etf_proxy_park_report.v1`
**Phase:** `S9_RSI2_YFINANCE_PROXY_PARK_REPORT`
**Candidate name:** `s9-cross-asset-mean-reversion-rsi2-spy-tlt-gld-uso-yfinance-proxy`
**Track:** `s9 cross-asset RSI-2 mean-reversion ETF-proxy (Connors canonical)`
**Sealed at (UTC):** `2026-05-26T20:48:36Z`
**Terminal verdict:** **`PARKED_SAFE_BUT_NOT_MONEY_PROVEN`**
**Verdict source:** s9 result aggregator (sparta.s9.rsi2.aggregation_result.v1) sealed at commit 95edc4780e39542fbfda1c00b12b6bc9b84e5f56; corroborated by the s9 IS decision memo sealed at commit 2e9a96dc9a02e64c8a51afaed8b73f8924f859ff.
**Trading status:** `PAUSED`
**Live status:** `BLOCKED_AT_6_GATES`
**FRC granted:** `False`
**Advisory label permanent:** `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE`

> Park-report-only turn. No simulator re-run. No signal
> re-computation. No aggregator re-run. No backtest. No OOS.
> No data fetch. No network. No brokerage. No live order.
> No Strategy Lab. No promotion. No review_queue mutation.

---

## 1. Terminal verdict and source

### **`PARKED_SAFE_BUT_NOT_MONEY_PROVEN`**

**Explanation:** Park: K1 Sharpe<0, K2 expectancy<=0.

- Verdict source: s9 result aggregator (sparta.s9.rsi2.aggregation_result.v1) sealed at commit 95edc4780e39542fbfda1c00b12b6bc9b84e5f56; corroborated by the s9 IS decision memo sealed at commit 2e9a96dc9a02e64c8a51afaed8b73f8924f859ff.
- Priority order applied: `K8 > K12 > K6/K7 > K10 > K9 > K11 > K1/K2/K4 > A-gates > ELIGIBLE_FOR_OOS`
- Active K path: `K1 (Sharpe<0) OR K2 (expectancy<=0) AT S1 BASELINE`

## 2. Reason for park

**Primary:** K1 (Sharpe proxy per trade < 0) AND K2 (expectancy per trade <= 0) fire at S1 baseline cost-stress. The mean-reversion edge itself is negative on this universe at canonical Connors RSI-2 parameters.

**Smoking gun (S0 row):** net PnL = **$-1211.030033** over 414 trades.

At S0 (zero slippage, zero commission), the strategy still loses money over 414 trades. The edge is negative even without cost friction; costs only make a negative edge more negative. This is structurally distinct from a cost-stress failure mode (s7 D1's REJECT_FAST was a cost-stress failure with a positive S0 edge).

**Secondary observations:**
- A2 fails: Sharpe proxy per trade is -0.097, below A2 threshold 0.
- A3 fails: expectancy per trade is -$3.22, below A3 threshold $0.
- A5 fails: portfolio WR gap to breakeven is -9.30pp, below +0.5pp threshold.
- Win rate 53.14% above absolute breakeven, but P/L-implied breakeven is 62.44%.

**What did NOT fail (every other safety / structure dimension cleared):**
- K4 (max drawdown > 50%): clears with margin (1.64%).
- K9 (closed trades < 100): clears comfortably (414).
- K10 (avg pairwise dependence > 0.50): clears (0.041).
- K11 (cap binding events > 1000): structurally zero on no-pyramid s9.
- K12 (DR2/DR3/DR5 cost-stress fail-fast): all DR rules clear.
- K6/K7 (safety): C1-C8 all True; no silent filter/dependence-gate.
- K8 (provenance drift): zero drift; all sealed shas match.

## 3. Supporting metrics (S1 baseline; sourced from sealed aggregator)

| Metric | Value |
|---|---|
| total_closed_trades_portfolio | 414 |
| total_net_pnl_dollars_s1_baseline | -1334.870032 |
| sharpe_proxy_per_trade_s1 | **-0.097135** (K1 fires) |
| expectancy_per_trade_dollars_s1 | **-3.224324** (K2 fires) |
| portfolio_win_rate_s1 | 0.531401 |
| portfolio_pl_ratio_s1 | 0.601472 |
| portfolio_implied_breakeven_win_rate_s1 | 0.624425 |
| portfolio_win_rate_gap_to_breakeven_pp_s1 | -9.302437 |
| trade_curve_max_drawdown_pct_vs_starting_cash_s1 | 1.64225% (K4 clears) |
| cap_binding_events_count | 0 (structurally zero on s9) |
| avg_pairwise_dependence_measure | 0.041354 (K10 threshold 0.50) |
| effective_independent_bets | 3.558527 (A7 threshold 2.5) |
| dr_rules_fired | `[]` |

### Cost-stress matrix (smooth degradation; DRs clear)

| Tier | total_net_pnl_dollars | K4 |
|---|---|---|
| S0 | -1211.030033 | False |
| S1 | -1334.870032 | False |
| S2 | -1578.440026 | False |
| S3 | -1825.78003 | False |

### Per-symbol net PnL (S1)

| Symbol | net_pnl_dollars_s1 | observed_win_rate_s1 |
|---|---|---|
| SPY | 140.090297 | 0.643564 |
| TLT | -104.229948 | 0.466019 |
| GLD | -194.130359 | 0.563107 |
| USO | -1176.600021 | 0.457944 |

## 4. Honest interpretation

**Headline:** s9 solved every structural failure mode of s7 D1 but did not solve the edge problem. The strategy is safe, well-diversified, trade-dense, low-drawdown, cost-stress robust, and provenance-clean. It is also unprofitable.

**s7 D1 -> s9 progression:**
- `trade_count_problem`: **SOLVED (414 trades vs 37; clears K9 by 4x)**
- `drawdown_problem`: **SOLVED (1.64% MaxDD vs cap-binding; clears K4 by 30x)**
- `cost_stress_problem`: **SOLVED (DR2/DR3/DR5 all clear; K12 does NOT fire)**
- `diversification_finding`: **REVALIDATED (3.56 eff bets, 0.041 avg dep)**
- `safety_warnings`: **NONE (C1-C8 all True; K6/K7/K8 all clear)**
- `edge_problem`: **NOT SOLVED (S0 negative; K1+K2 fire)**

**Universe-level conclusion:** Two structurally orthogonal mechanics (trend-following s7 D1, mean-reversion s9) empirically falsified on the same ETF universe (SPY/TLT/GLD/USO 2014-2022) at canonical parameters with realistic ETF-proxy cost assumptions. The universe-level conclusion strengthens: current ETF-proxy cost structure does not support either family at canonical parameters on this universe. The diversification finding (avg pairwise dependence ~0.041) holds across both mechanics and is a universe property.

**What this park does NOT mean:**
- Does NOT mean the RSI-2 mechanic is universally broken. It means this specific instantiation (canonical parameters, this universe, this cost regime, this window) does not produce a positive edge.
- Does NOT mean iterating s9 thresholds will fix the edge. A parameter sweep without a first-principles justification would invite K7 silent-introduction risk on future iterations.
- Does NOT change the diversification finding. The four-ETF universe remains validated as essentially independent return series.
- Does NOT change live trading posture. Live remains BLOCKED at 6 gates; FRC never granted; this park does not gate any onward promotion path.

**What this park DOES mean:**
- The s9 ETF-proxy chain is terminally closed at canonical parameters.
- Revival of canonical-parameter s9 is not authorized; would require a fresh _revN_ Tier-N spec with first-principles justification.
- Future research on this universe should consider: different mechanic family (rotation, carry, vol-of-vol), or different cost-structure assumption, or different universe entirely.
- Sealed empirical record preserved; all build artifacts immutable.
- All upstream sealed-sha pins documented for future provenance audits.

**Decision-memo corroboration:** The IS decision memo (commit 2e9a96dc9a02e64c8a51afaed8b73f8924f859ff; sha 30da17f4d9f04a07; seal 0d7b3561c16cf7cb) records the same verdict and the same evidence; this park report is the lifecycle-transition seal that terminally closes the chain.

## 5. Chain commits (chronological)

| Phase | Commit | Path |
|---|---|---|
| `selection_plan` | `530b54598fa7098eb746f2122b4002db2c984422` | `docs/next_research_track_selection_plan_after_s7_d1_park.md` |
| `tier_n_spec` | `5bd8e62a1a614042a30e44f4060e54c7cdd20401` | `docs/s9_cross_asset_mean_reversion_rsi2_tier_n_specification_plan.md` |
| `signal_spec` | `c5393ab31a58059004b8cd337cd428eacbcbaece` | `docs/s9_cross_asset_mean_reversion_rsi2_signal_module_specification_plan.md` |
| `signal_build` | `1a055bd1adecf30408de99971bf6e9f22cf53866` | `external_research_hunter/s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_signal/` |
| `simulator_spec` | `3a9a0de9eba9e448d0440fa45fb40e8107fb8e0f` | `docs/s9_cross_asset_mean_reversion_rsi2_simulator_specification_plan.md` |
| `simulator_build` | `1de75e576c9878a2dfc2568b8f5747fda7eb84cf` | `external_research_hunter/s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_simulator/` |
| `aggregator_decision_plan` | `113f5b954e189088e6ddda18a2138abb27ff92e2` | `docs/s9_cross_asset_mean_reversion_rsi2_aggregator_reuse_decision_plan.md` |
| `aggregator_build` | `95edc4780e39542fbfda1c00b12b6bc9b84e5f56` | `external_research_hunter/s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_aggregator/` |
| `is_decision_memo` | `2e9a96dc9a02e64c8a51afaed8b73f8924f859ff` | `reports/s9_cross_asset_mean_reversion_rsi2_is_decision_memo.{json,md}` |
| `park_report` | `(this commit)` | `reports/s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_park_report.{json,md}` |

## 6. Upstream integrity pins (drift count = 0)

**Upstream integrity match:** `True`
**Mismatch count:** `0`

| Artifact | sha256 (first 16) | seal (first 16) |
|---|---|---|
| Tier-N spec | `6690c0d789285598` | n/a (spec doc) |
| Signal-module spec | `59e5f401232f1934` | n/a (spec doc) |
| Simulator-module spec | `c64bbe7525ad06d5` | n/a (spec doc) |
| Aggregator decision plan | `af6f8fd6d1de1b91` | n/a (spec doc) |
| Selection plan | `d8753155d47c36e0` | n/a (spec doc) |
| Signal build report (PASS) | `d78ad857ffc26a43` | `f553ae8a31ec0ff1` |
| Simulator build report (PASS) | `0bdbde0e2a0d6522` | `957b685110ec11e1` |
| Aggregator build report (PASS) | `1f6e827f03af8cb2` | `74b6dc24dcd85ea6` |
| IS decision memo | `30da17f4d9f04a07` | `0d7b3561c16cf7cb` |
| Step 03 loader.py (reused byte-equiv) | `e0609e404cadca1c` | n/a (code) |
| Step 04 validator.py (reused byte-equiv) | `bae0fc410ad3d659` | n/a (code) |
| audit_manifest.json | `794a9386abc68fdf` | n/a (data) |

**Predecessor park anchor (s7 D1 ETF-proxy, parked at REJECT_FAST via K12):**
- commit `a5ac092`
- sha256 `5eb4309096a8377943799b7cc164cbbb13a86f327a813520255d0fa3b3e00263`
- seal `e7f3fce5239d18f7cff78ddda81dde060b6842c54ddb1fdba95bfdcd584eb326`
- terminal verdict `REJECT_FAST`
- Predecessor track parked at REJECT_FAST via K12 (DR2+DR3 cost-stress catastrophic). Different failure mode from s9 ETF-proxy (which fails at K1/K2 with cost-stress benign). Both close the chapter on canonical-parameter structurally-pure mechanics on this universe.

## 7. Recommended next actions (each requires fresh authorization)

### `APPEND_TERMINAL_LESSON`
- **target:** brain_memory/projects/trading_bot/lessons.md
- **scope:** Universe-level finding: two structurally orthogonal mechanics empirically falsified on SPY/TLT/GLD/USO 2014-2022 at canonical parameters with realistic ETF-proxy costs. Diversification finding holds across both.
- **requires_separate_authorization:** True

### `SELECT_NEXT_RESEARCH_TRACK`
- **scope:** Choose from: (a) different mechanic family on same universe (rotation, carry, vol-of-vol); (b) different universe entirely (international ETFs, sector ETFs, equity single names); (c) different cost-structure assumption with first-principles justification; (d) operator-directed pivot.
- **requires_separate_authorization:** True

### `DO_NOT_PROCEED_TO_OOS`
- **rationale:** Park verdict PARKED_SAFE_BUT_NOT_MONEY_PROVEN does not gate onward to OOS by design. Running OOS on a strategy that lost money at S0 in-sample would be a research anti-pattern.

### `DO_NOT_ITERATE_S9_PARAMETERS_WITHOUT_REVN_SPEC`
- **rationale:** Parameter sweep without first-principles justification would invite K7 silent-introduction risk. Any revision of locked Tier-N parameters requires a fresh _revN_ spec under separate authorization.

## 8. Final status

- `candidate_operational_status`: **PARKED_SAFE_BUT_NOT_MONEY_PROVEN**
- `chain_terminally_closed`: **True**
- `revival_requires_fresh_revN_spec`: **True**
- `live_promotion_path_closed`: **True**
- `strategy_lab_promotion_blocked`: **True**
- `review_queue_untouched`: **True**
- `production_idea_memory_untouched`: **True**
- `frc_never_granted`: **True**
- `trading_paused_continues`: **True**

## 9. Boundaries held (all True)

- `no_CLAUDE_md_modification`
- `no_RUNBOOK_modification`
- `no_aggregator_build_report_modification`
- `no_aggregator_decision_plan_modification`
- `no_aggregator_module_modification`
- `no_aggregator_re_run`
- `no_autopilot_invocation`
- `no_backtest`
- `no_branch_change`
- `no_branch_creation`
- `no_brokerage_connection`
- `no_candidate_promotion_to_production`
- `no_commit_beyond_two_park_outputs`
- `no_data_fetch`
- `no_databento_api_key_accessed`
- `no_databento_called`
- `no_docs_decisions_md_modification`
- `no_full_window_simulation`
- `no_git_push`
- `no_gitignore_modification`
- `no_is_decision_memo_modification`
- `no_live_trading`
- `no_loader_modification`
- `no_network_call`
- `no_oos_computation`
- `no_oos_signal_computed`
- `no_oos_simulation_run`
- `no_orb_branch_artifact_mutation`
- `no_order_creation`
- `no_paper_order_placed`
- `no_pipeline_manifest_modification`
- `no_post_oos_inspection`
- `no_production_idea_memory_mutation`
- `no_real_order_placed`
- `no_review_queue_mutation`
- `no_rsi_recomputation`
- `no_s7_d1_artifact_modification`
- `no_s7_d1_resurrection`
- `no_scheduler_invocation`
- `no_selection_plan_modification`
- `no_signal_build_report_modification`
- `no_signal_module_modification`
- `no_signal_re_computation`
- `no_signal_spec_modification`
- `no_simulator_build_report_modification`
- `no_simulator_module_modification`
- `no_simulator_re_run`
- `no_simulator_spec_modification`
- `no_ssl_verification_disabled`
- `no_step_30_cost_constant_mutation`
- `no_strategy_lab_promotion`
- `no_strategy_lab_run`
- `no_tier_n_spec_modification`
- `no_validator_modification`
- `no_vendor_sdk_imported`
- `no_yahoo_finance_called`
- `no_yfinance_called`
- `two_outputs_only`

## 10. Negative invariants (all False)

- `aggregator_module_modified`
- `aggregator_re_run`
- `audit_manifest_modified`
- `backtest_run`
- `branch_changed`
- `branch_created`
- `brokerage_connection`
- `candidate_promoted_to_production`
- `csv_modified`
- `data_fetched`
- `databento_api_key_accessed`
- `databento_called`
- `fetch_manifest_modified`
- `file_io_outside_two_park_outputs`
- `git_pushed`
- `idea_memory_mutated`
- `is_memo_modified`
- `live_order_placed`
- `live_trading`
- `loader_modified`
- `network_used`
- `oos_signal_computed`
- `oos_simulation_run`
- `orb_branch_mutated`
- `paper_order_placed`
- `review_queue_mutated`
- `rsi_recomputed`
- `s7_d1_artifact_modified`
- `signal_module_modified`
- `signal_re_computation`
- `simulator_module_modified`
- `simulator_re_run`
- `strategy_lab_invoked`
- `strategy_lab_promoted`
- `tier_n_spec_modified`
- `validator_modified`
- `yfinance_called`

## 11. Labels

- `S9_RSI2_YFINANCE_PROXY_PARK_REPORT`
- `TERMINAL_VERDICT_PARKED_SAFE_BUT_NOT_MONEY_PROVEN`
- `K1_FIRED`
- `K2_FIRED`
- `K12_DID_NOT_FIRE`
- `K4_DID_NOT_FIRE`
- `DIVERSIFICATION_REVALIDATED`
- `EDGE_NEGATIVE_AT_ZERO_COST`
- `CHAIN_TERMINALLY_CLOSED`
- `REVIVAL_REQUIRES_FRESH_revN_SPEC`
- `OOS_BLOCKED`
- `LIVE_BLOCKED_AT_6_GATES`
- `FRC_NEVER_GRANTED`
- `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE`
- `UNIVERSE_LEVEL_CONCLUSION_TWO_ORTHOGONAL_MECHANICS_FALSIFIED`

## 12. Seal verification

```
seal_method = sha256 over json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False) EXCLUDING report_seal_sha256 + seal_method

report_seal_sha256 = <see JSON report_seal_sha256 field>
```

Companion JSON sha256 = recompute sha256 of the JSON bytes on disk.

**Chain terminally closed. Trading: PAUSED. Live: BLOCKED_AT_6_GATES. FRC never granted.**

