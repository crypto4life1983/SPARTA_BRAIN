# S10-D2 P10 OOS gate (sealed)

**Candidate:** `s10-cross-asset-donchian-no-pyramid-reparam-cap-nq-gc-zn-cl`
**Phase prefix:** `PHASE2-S10-D2-XAD-RC`
**Authored (UTC):** `2026-05-27T03:33:05.686812Z`
**OOS window:** **2023-01-01 → 2025-12-31** (3 years)
**Markets:** NQ, GC, ZN, CL
**Cost tier run:** S1 (baseline)
**Driver used:** committed `out_of_sample_driver.py` (P3.6 BUILD `c7d9d7888f2bc5df...`); NO monkey-patching
**C7 verdict:** **INSUFFICIENT_SAMPLE**
**OOS qualitative verdict:** **OOS_INDETERMINATE_BUT_DIRECTIONALLY_CONSISTENT**
**Wall time:** 81.816s
**Report seal sha256:** `4038e5334feba9ea61b91dcb47287a7a8f9f8fdfd8ad35990866bc9fbd106137`

## Executive summary

Closed-trade count fell below the K9 threshold of 100 (expected on a 3-year OOS window vs 10-year IS). Headline metrics (sharpe, expectancy, net PnL) remain positive and directionally consistent with the IS edge. This is NOT a confirmation — it is an absence of refutation under a structurally small sample.

## OOS metrics

| Metric | Value |
|---|---|
| Starting cash | $500,000 |
| Final equity | $613,450.34 |
| Net PnL | $113,450.34 |
| Closed trades | 53 |
| Wins / Losses | 18 / 35 |
| Win rate | 33.96% (vs breakeven 27.44%; gap +6.52 pp) |
| Expectancy / trade | $2140.57 |
| PL ratio | 2.6439 |
| Sharpe proxy / trade | 0.100510 |
| Trade curve max DD | -12.9574% / $-64,786.97 |
| Long / Short PnL | $183,682.24 / $-70,231.91 |
| Safety counters all zero | **True** |
| Cap binding events | 0 |

### Per-market contribution (OOS)

| Market | Trades | Net PnL | Win rate |
|---|---:|---:|---:|
| `CL` | 16 | $-113,275.07 | 12.50% |
| `GC` | 12 | $136,025.06 | 33.33% |
| `NQ` | 10 | $75,396.38 | 50.00% |
| `ZN` | 15 | $15,303.96 | 46.67% |

## Comparison: OOS vs IS S1 (baseline)

| Metric | IS (10y) | OOS (3y) | Ratio |
|---|---:|---:|---:|
| Closed trades | 200 | 53 | 0.265x |
| Trades / year | 20.0 | 17.7 | 0.883x |
| Net PnL | $973,097.86 | $113,450.34 | 0.117x |
| Expectancy / trade | $4,865.49 | $2,140.57 | 0.440x |
| Sharpe proxy | 0.1431 | 0.1005 | 0.702x |
| Win rate | 35.00% | 33.96% | — |
| WR gap to breakeven | 10.48pp | 6.52pp | — |
| Trade curve max DD | -28.31% | -12.96% | — |

## Comparison vs P6.5 cost-stress

- P6.5 matrix verdict: **READY_FOR_NEXT_PHASE**
- P6.5 A8 (cost-stress S0/S2/S3/S4 run): **PASS**
- P6.5 K12 (DR fires on cost stress): **not_fired**
- P6.5 was evaluated against IS data, not OOS. An OOS cost-stress sweep (S0/S2/S3/S4) would be a separate phase if pursued.

## Gate pass/fail table

### K-gates (rejection criteria; should not fire)

| K-gate | Fires? |
|---|:-:|
| `K10_avg_pairwise_corr_gt_0_50` | skip (None) |
| `K11_cap_binding_events_gt_1000` | ok (False) |
| `K12_DR_fires_on_cost_stress` | skip ('NOT_EVALUATED_THIS_TURN_ONLY_S1_OOS_RUN') |
| `K1_sharpe_proxy_lt_0` | ok (False) |
| `K2_expectancy_le_0` | ok (False) |
| `K4_trade_curve_maxdd_gt_50` | ok (False) |
| `K6_safety_warning_count_gt_0` | ok (False) |
| `K7_correlation_gate_silently_introduced` | ok (False) |
| `K7_filter_silently_introduced` | ok (False) |
| `K8_sealed_parent_drift` | skip (0) |
| `K9_closed_trades_lt_100` | FIRED (True) |

**K_fires_count:** 1
**K_fires:** ['K9_closed_trades_lt_100']

### A-gates (acceptance criteria)

| A-gate | Status |
|---|---|
| `A10_cap_binding_events_eq_0` | **PASS** ({'pass': True, 'value': 0}) |
| `A1_closed_trades_ge_100` | **FAIL** ({'pass': False, 'threshold': 100, 'value': 53, 'note': 'OOS context: 3-year window vs IS 10-year; closed_trades naturally ~30% of IS count. If A1 fails on OOS, that is sample-size, not strategy failure.'}) |
| `A2_sharpe_proxy_gt_0` | **PASS** ({'pass': True, 'threshold': 0.0, 'value': 0.10051032603779608}) |
| `A3_expectancy_gt_0` | **PASS** ({'pass': True, 'threshold': 0.0, 'value': 2140.572359798117}) |
| `A4_trade_curve_maxdd_pct_le_50` | **PASS** ({'pass': True, 'threshold': -50.0, 'value': -12.95739439763902}) |
| `A5_2of4_markets_wr_gap_ge_0_or_portfolio_wr_gap_ge_plus_half_pp` | **PASS** ({'pass': True, 'portfolio_wr_gap_pp': 6.519369348847115, 'note': 'evaluated from trade_diagnostics.win_rate_gap_to_breakeven_pp'}) |
| `A6_validator_pass` | **PASS** ({'pass': True, 'note': 'no-pyramid attestation + plan-lock validator inherited byte-equivalent from s8-D1'}) |
| `A8_cost_stress_S0_S4_run` | (not evaluated this turn) {'evaluated_this_turn': False, 'note': 'Cost-stress matrix evaluated against IS at P6.5. OOS cost-stress sweep would be a separate phase if pursued.'} |
| `A9_phase2_c1_c8_inheritance_attestable` | **PASS** ({'pass': True, 'note': 'C1-C8 inherited byte-equivalent from phase2_safety_contract_template'}) |

### DR rules

- DR rules are matrix-level evaluations applied to cost-stress sweep results (P6.5 territory). No DR evaluation at single-tier P10 OOS run.

## Verdict reasoning

**C7 verdict:** INSUFFICIENT_SAMPLE
- closed_trades=53 < 100 threshold (K9 fired). NOTE: OOS window is 3 years vs IS 10 years — natural sample-size constraint. This is INDETERMINATE about the strategy's edge, not a refutation.

**OOS qualitative verdict:** OOS_INDETERMINATE_BUT_DIRECTIONALLY_CONSISTENT
- Closed-trade count below K9 threshold (insufficient sample), BUT sharpe / expectancy / net PnL are all positive and directionally consistent with the IS edge. This is NOT a confirmation, just an absence of refutation under a structurally small sample.

## Whether OOS confirms, weakens, or kills the S10-D2 thesis

**Result:** **OOS_INDETERMINATE_BUT_DIRECTIONALLY_CONSISTENT**

Closed-trade count fell below the K9 threshold of 100 (expected on a 3-year OOS window vs 10-year IS). Headline metrics (sharpe, expectancy, net PnL) remain positive and directionally consistent with the IS edge. This is NOT a confirmation — it is an absence of refutation under a structurally small sample.

## What this result does NOT mean

- Does NOT mean the strategy is live-ready or paper-ready.
- Does NOT mean future P&L will resemble OOS P&L.
- Does NOT mean execution-cost frictions in production will match modeled S1.
- Does NOT mean the OOS regime is representative of all future regimes.
- Does NOT lift the permanent 6-gate live-block.
- Does NOT promote this candidate beyond research-diagnostic status.

## Explicit blocked actions

- DO NOT advance to live trading.
- DO NOT advance to paper trading via broker connection.
- DO NOT re-tune any strategy parameter based on OOS results.
- DO NOT modify Donchian periods, ATR multiplier, risk %, max_units, AMB6 filter, starting_cash, or cost-tier definitions in response to this OOS result.
- DO NOT re-execute OOS with different parameters until a fresh sealed candidate (different candidate_record_id) is authored under a new chain.
- DO NOT make any profitability claim outside this conservative diagnostic framing.
- DO NOT touch obsidian-trade-logger.
- DO NOT mutate review_queue.json.
- DO NOT touch brain_memory/projects/trading_bot/lessons.md.
- DO NOT revive S8-D1, S7-D1, D5, B005_001, or NKE.
- DO NOT fetch additional Databento data or modify the OOS cache.
- DO NOT call Databento API, QuantConnect, or any broker/exchange/wallet API.

## Driver / cache attestation

- Driver source byte-stable through run: **True** (sha at start == sha at end)
- Monkey-patches applied: **0** (none)
- OOS cache byte-stable through run: **True**
- Original data/databento_cache/ byte-stable: **True** (not touched by my code)

## Hard boundaries held

- no_broker_exchange_api: True
- no_commit_in_orchestrator: True
- no_conftest_modified: True
- no_d5_b005_001_nke_revival: True
- no_data_fetch: True
- no_databento_api_call: True
- no_db_historical: True
- no_in_sample_driver_modified: True
- no_lessons_md_touched: True
- no_live_trading: True
- no_monkey_patch_of_any_kind: True
- no_network_call: True
- no_obsidian_touched: True
- no_oos_cache_mutation: True
- no_orig_cache_mutation: True
- no_out_of_sample_driver_modified: True
- no_paper_trading: True
- no_profitability_claim: True
- no_promotion_to_live: True
- no_qc_runtime: True
- no_review_queue_mutation: True
- no_runner_main_modified: True
- no_s11_d1_started: True
- no_s8_d1_or_s7_d1_modified: True
- no_source_modification: True
- no_strategy_optimization: True
- no_test_oos_invariants_modified: True
- no_test_smoke_modified: True
- no_threshold_loosening: True
- no_unrelated_tracked_file_modified: True

## Inherited seals

- `tier_n_spec_seal_sha256`: `f5ca5ee63024e9c8b7b1e85762558ec35eb3d4ebb9ce2a160cbe0f1a0e80a679`
- `plan_lock_seal_sha256`: `ba8bf954d44b373c0ffdc38a1cf8f73dec31a9fc538f0b7584a20659d79ea354`
- `phase2_plan_seal_sha256`: `7a48ad64236971e6fd2a2fa58ab7ab746a71543778ed0a868f3cdf9ff8f74ac3`
- `p3_build_runner_report_seal_sha256`: `1eb04aa312f4053134c1e9387be7716aa4564c019168ee2cedcf789063d96405`
- `p3_build_in_sample_driver_report_seal_sha256`: `ddd604c96508a0ab835bcbae6e72fabc2993cd3f0dc459898ca326617dd96443`
- `p3_5_scaffold_completion_seal_sha256`: `66d38f359b54882b3107c4ad4291673d63f05f5b0d3daa19088b4a4c76469261`
- `p3_6_oos_driver_build_seal_sha256`: `c7d9d7888f2bc5df6850ab37f9bde0b95c3c794486382c4b0d45f32b6bd1b73d`
- `p4_smoke_seal_sha256`: `c31ded81f9a2883586883aadda4d64d629a047917fcebd56169ca42eccf4fdde`
- `p6_is_diagnostic_seal_sha256`: `e6cdc7c68a9e2b7b6d749b73ff433e585c9de55890af5dce3dca51d74430c1b8`
- `p6_5_cost_stress_matrix_seal_sha256`: `f9a34674de4f7fdf8098b39959032d152bf2282e9ad57cedd68bc33cee2099ab`
- `p7_decision_memo_seal_sha256`: `87baa6e8c4cc1eb47c1345b97990eab86d5cefb37636e9fe57a029506d398c05`

## Recommended next phase

AUTHORIZE_S10_D2_P11_INSUFFICIENT_SAMPLE_PARK — OOS sample insufficient to draw firm conclusions. Park candidate and consider a successor or alternative validation approach. Could also fall back to S11-D1 MNQ.c.0 single-instrument track per parallel-session selection plan (commit 556ab3f).
