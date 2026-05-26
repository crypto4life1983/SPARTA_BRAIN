# s7 D1 Cross-Asset Donchian ETF-Proxy - PARK REPORT

> Terminal park artifact. Records the REJECT_FAST in-sample verdict
> from the Step 07 result aggregator and the operator's
> 'do not rescue this spec' decision. No code modification this turn.
> No simulator rerun. No OOS. No data fetch. No live trading.

**Schema:** `sparta.donchian.s7_d1_etf_proxy_park_report.v1`
**Phase:** `S7_D1_DONCHIAN_YFINANCE_PROXY_PARK_REPORT`
**Controller session:** THIS_SESSION_ONLY
**Report date (UTC):** 2026-05-26T02:11:05Z
**Candidate:** `s7-cross-asset-donchian-no-filter-spy-tlt-gld-uso-yfinance-proxy`
**Track:** s7 D1 cross-asset Donchian ETF-proxy

## Terminal verdict
**`REJECT_FAST`** -- from Step 07 result aggregator (sparta.donchian.step_07_aggregation_result.v1)

Clean Step 07 build commit: `aad1a2ebe23038aa29e9af6b5bde614043e349a2`

**Companion JSON:** `reports/s7_d1_cross_asset_donchian_yfinance_proxy_park_report.json` (sha256 + seal recorded only in JSON; recompute from JSON bytes to verify)

---

## 1. Full commit chain (Step 02b -> Step 07)

| Step | Commit | Description |
|---|---|---|
| 02b_plan | `efdc30753449c8b5` | Add s7 D1 cross-asset Donchian Step 02b alt-vendor data-fetch plan |
| 02c_plan | `faebd583955cf13f` | Add s7 D1 Donchian Step 02c next-phase plan |
| 02c_audit | `1b640d1520eeec5e` | Seal s7 D1 Donchian Step 02c raw-data audit (verdict PASS) |
| 03_plan | `f759251b238cd764` | Add s7 D1 Donchian Step 03 canonical-loader specification plan |
| 03_build | `d7b2a0c27c200b37` | Build s7 D1 Donchian Step 03 canonical loader (verdict PASS) |
| 04_plan | `a5acf59f497897c0` | Add s7 D1 Donchian Step 04 input-validator specification plan |
| 04_build | `a2ec1798e490d362` | Build s7 D1 Donchian Step 04 input validator (verdict PASS) |
| 05_plan | `7e76bb785fa9f75b` | Add s7 D1 Donchian Step 05 signal-computation specification plan |
| 05_build | `25d262fab0e89123` | Build s7 D1 Donchian Step 05 signal module (verdict PASS) |
| 06_plan | `c964c59ce0d499b7` | Add s7 D1 Donchian Step 06 simulator specification plan |
| 06_build | `ecd03e512aabed93` | Build s7 D1 Donchian Step 06 simulator (verdict PASS) |
| 07_plan | `b99151caceb307a3` | Add s7 D1 Donchian Step 07 result-aggregation specification plan |
| 07_build | `aad1a2ebe23038aa` | Build s7 D1 Donchian Step 07 result aggregator (verdict PASS; first IS verdict REJECT_FAST) |

## 2. Reason for rejection

- `K12_DR_FIRES`: **True**
- `DR2_S2_or_S3_degrades_materially`: **True**
- `DR3_zero_cost_only_survival`: **True**
- `DR5_S0_to_S1_edge_negative`: **False**
- `cost_stress_failure_summary`: **S2 and/or S3 cost-stress tier net PnL materially degrades vs S1 baseline (DR2). S0 baseline shows positive PnL while at least one stressed tier turns non-positive (DR3). The locked Faith System 1 mechanic does not survive cost stress on the ETF-proxy in-sample window at the parent-spec parameter pinning.**

## 3. Supporting metrics

| Metric | Value |
|---|---|
| S1 net PnL on $100k | **589.5904078177693** |
| trade-curve max drawdown pct | **69.10094005427824%** |
| total closed trades | **37** |
| effective independent bets | **3.5585269132770376** |
| avg pairwise dependence | **0.041353542957696436** |
| K9 sample-size below 100 | True |
| K4 trade-curve MaxDD above 50% | True |
| K10 avg pairwise dependence above 0.50 | False |
| K1 sharpe below zero | False |
| K2 expectancy non-positive | False |

**Per-symbol summary:**
- **USO**: net positive ($96,538 approx); standout contributor
- **TLT**: net negative (~-$8,000)
- **GLD**: net negative (~-$43,000)
- **SPY**: net negative (~-$45,000)

## 4. Honest interpretation

- **diversification_hypothesis_supported:** `True`
  - Cross-family diversification with avg pairwise dependence 0.041 and effective independent bets 3.56 EMPIRICALLY VALIDATES the load-bearing hypothesis from spec section 1 H1. This is a real positive finding from the s2-s7 research arc even though the strategy itself did not survive cost stress.

- **trading_edge_robustness:**
  - Not robust enough. The +$589 net PnL on $100k over ~9 in-sample years is technically positive but trivially small relative to the 69.10% trade-curve max drawdown. The edge does not survive realistic transaction cost stress (DR2/DR3 fire).

- **cost_stress_vulnerability_terminal_under_locked_rules:** `True`
- **money_proven:** `False`
  - Per spec sec 14 K12, REJECT_FAST is a terminal IS-side verdict. Per the threshold-lock invariant, loosening any K threshold post-seal is forbidden. The strategy is not money-proven at this spec pinning.

- **oos_not_inspected:** `True`
  - Out-of-sample data exists on disk (2023-01-03 through 2025-12-30) but was never inspected. The K12 fire on the in-sample cost-stress matrix triggered the fail-fast path before any OOS authorization could be considered. OOS remains structurally blocked at separate plans.

- **live_trading_implication:** NONE. Live trading remains blocked at six gates regardless of any in-sample verdict.

- **uneven_per_market_performance:**
  - USO contributed +$96,538 single-handedly; SPY, TLT, and GLD were all net losers. A diversified PORTFOLIO that depends on ONE market for its PnL is not a diversified edge; it is concentrated single-market risk wearing a portfolio costume.

## 5. Final status flags (all True)

- `PARKED_REJECT_FAST`: **True**
- `DO_NOT_RESCUE_THIS_SPEC`: **True**
- `OOS_BLOCKED`: **True**
- `STRATEGY_LAB_BLOCKED`: **True**
- `LIVE_TRADING_BLOCKED`: **True**
- `CANDIDATE_RECORD_ID`: **s7-cross-asset-donchian-no-filter-spy-tlt-gld-uso-yfinance-proxy**
- `TERMINAL_VERDICT_AT_IS_CLOSE`: **REJECT_FAST**
- `BROKER_INTEGRATION_BLOCKED`: **True**
- `REVIEW_QUEUE_INTENTIONALLY_NOT_MUTATED`: **True**

## 6. Recommended next actions (each requires SEPARATE authorization)

### next-1: Move to the next research track
The s7 D1 ETF-proxy candidate is terminally parked. The diversification hypothesis is validated; the next research track should preserve that finding and explore a different edge family or a different parameterization that requires its OWN fresh sealed spec (per the threshold-lock invariant in parent spec section 14).
- auto_initiated_this_turn: **False**
- requires_separate_authorization: **True**

### next-2: Optional separate lesson append
Append a one-paragraph lesson to brain_memory/projects/trading_bot/lessons.md and a decision to brain_memory/projects/trading_bot/decisions.md and a next action to brain_memory/projects/trading_bot/next_actions.md per CLAUDE.md guidance. These files were NOT touched this turn or any prior turn; the hard boundaries forbid modifying them without explicit authorization.
- auto_initiated_this_turn: **False**
- requires_separate_authorization: **True**

### next-3: Optional separate F1 remediation
Step 02c audit finding F1 (manifest divergence-metric clarification) remains documented but untouched. A separate authorization could choose: (a) re-author Step 02c plan section 10 J1 with corrected metric description, (b) add an absolute-divergence field to fetch_run_manifest.json alongside the existing relative field, or (c) accept the F1 finding as documented and proceed without further change.
- auto_initiated_this_turn: **False**
- requires_separate_authorization: **True**

### next-4: No automatic continuation
This park report is a terminal artifact for the s7 D1 ETF-proxy track. No future phase of this chain is auto-authorized. Each onward step requires an explicit fresh operator authorization in the established controller-session pattern. The chain is closed at this commit.
- auto_initiated_this_turn: **False**
- requires_separate_authorization: **True**

## 7. Upstream report integrity (all 6 byte-unchanged)

| Report | sha16 observed | sha16 pinned | match |
|---|---|---|---|
| step_07_report_sha16 | `ba82a5aa46f9cc13` | `ba82a5aa46f9cc13` | OK |
| step_06_report_sha16 | `cb826116c3a429fe` | `cb826116c3a429fe` | OK |
| step_05_report_sha16 | `65ee1b6a5c7635ab` | `65ee1b6a5c7635ab` | OK |
| step_04_report_sha16 | `fbabd75ea7ce1914` | `fbabd75ea7ce1914` | OK |
| step_03_report_sha16 | `137dd8534de84076` | `137dd8534de84076` | OK |
| step_02c_report_sha16 | `a17c90032fdab504` | `a17c90032fdab504` | OK |

## 8. Boundaries held (all True)
 - `no_CLAUDE_md_modification`  
 - `no_RUNBOOK_modification`  
 - `no_aggregator_modification`  
 - `no_audit_manifest_modification`  
 - `no_backtest`  
 - `no_branch_change`  
 - `no_branch_created`  
 - `no_brokerage_connection`  
 - `no_candidate_promotion`  
 - `no_csv_modification`  
 - `no_data_fetch`  
 - `no_databento_api_key_access`  
 - `no_databento_call`  
 - `no_docs_decisions_md_modification`  
 - `no_fetch_run_manifest_modification`  
 - `no_git_push`  
 - `no_gitignore_modification`  
 - `no_idea_memory_mutation`  
 - `no_live_trading`  
 - `no_loader_modification`  
 - `no_network_call`  
 - `no_new_signal_computation`  
 - `no_oos_computation`  
 - `no_oos_inspection_beyond_already_sealed_structural_counts`  
 - `no_orb_branch_mutation`  
 - `no_orb_step_30_cost_constant_mutation`  
 - `no_paper_order`  
 - `no_pipeline_manifest_modification`  
 - `no_real_order`  
 - `no_review_queue_mutation`  
 - `no_signal_module_modification`  
 - `no_simulator_modification`  
 - `no_simulator_rerun`  
 - `no_strategy_code_modification`  
 - `no_strategy_lab_promotion`  
 - `no_strategy_lab_run`  
 - `no_tests_modification`  
 - `no_validator_modification`  
 - `no_yahoo_finance_call`  
 - `no_yfinance_call`  
 - `park_report_only_under_operator_authorization`  
 - `park_report_seal_recomputable_from_disk`  
 - `upstream_reports_byte_unchanged`

## 9. Negative invariants (all False)
 - `aggregator_modified`  
 - `audit_manifest_modified`  
 - `backtest_run`  
 - `branch_changed`  
 - `branch_created`  
 - `brokerage_connection`  
 - `candidate_promoted`  
 - `csv_modified`  
 - `data_fetched`  
 - `databento_api_key_accessed`  
 - `databento_called`  
 - `fetch_manifest_modified`  
 - `git_pushed`  
 - `idea_memory_mutated`  
 - `live_trading`  
 - `loader_modified`  
 - `network_used`  
 - `new_signal_computed`  
 - `oos_value_inspected`  
 - `orb_branch_mutated`  
 - `paper_order_placed`  
 - `plan_modified`  
 - `real_order_placed`  
 - `review_queue_mutated`  
 - `signal_module_modified`  
 - `simulator_modified`  
 - `simulator_rerun`  
 - `spec_modified`  
 - `strategy_lab_promoted`  
 - `strategy_lab_run`  
 - `tests_modified`  
 - `validator_modified`  
 - `yahoo_finance_called`  
 - `yfinance_called`

## 10. Seal verification
```
seal_method = sha256 over json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False) EXCLUDING report_seal_sha256 + seal_method

report_seal_sha256 = <see JSON report_seal_sha256 field>
```

Companion JSON sha256 = <recompute sha256 of the JSON bytes on disk>

**Terminal verdict: `REJECT_FAST`.** Trading: PAUSED. Live: BLOCKED at 6 gates. Do not rescue this spec.

