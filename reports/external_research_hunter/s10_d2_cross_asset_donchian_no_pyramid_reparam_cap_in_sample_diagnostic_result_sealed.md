# S10-D2 P6 IS diagnostic report (cost_tier='S1')

**Candidate:** `s10-cross-asset-donchian-no-pyramid-reparam-cap-nq-gc-zn-cl`
**Phase prefix:** `PHASE2-S10-D2-XAD-RC`
**Authored (UTC):** `2026-05-27T01:49:38.068589Z`
**Verdict finalized (UTC):** `2026-05-27T01:52:42.981221Z`
**Verdict (C7 closed enum):** **READY_FOR_LONGER_BACKTEST**
**Verdict reasons:** ['All safety counters zero AND closed_trades >= 100; research label only (live-block applies regardless).']
**Wall time:** 277.547s
**Report seal sha256:** `e6cdc7c68a9e2b7b6d749b73ff433e585c9de55890af5dce3dca51d74430c1b8`

## Performance summary

- Starting cash: $500,000
- Final equity:  $1,473,097.86
- Net PnL:       $973,097.86
- Win rate:      35.0000%
- Max drawdown:  -28.3060% / $-141,529.98

## Trade diagnostics

- Closed trades (portfolio): **200**
- Wins / Losses:             70 / 130
- n_long / n_short:          111 / 89
- Expectancy per trade:      $4865.49
- Avg win / Avg loss:        $35046.72 / $-11385.94
- PL ratio:                  3.0781
- Sharpe proxy per trade:    0.143112
- Breakeven WR:              24.5214%
- WR gap to breakeven:       10.4786 pp
- Long PnL / Short PnL:      $458,468.05 / $514,629.81

### Per-market breakdown

| Market | Trades | Net PnL (USD) | Win rate |
|---|---:|---:|---:|
| `CL` | 49 | $422,894.55 | 38.78% |
| `GC` | 49 | $-345.01 | 28.57% |
| `NQ` | 54 | $126,607.39 | 35.19% |
| `ZN` | 48 | $423,940.93 | 37.50% |

## Scan diagnostics

- Trading days in union:     2574
- Per-market daily bar counts: {'CL': 2567, 'GC': 2290, 'NQ': 2526, 'ZN': 2571}

## Safety diagnostics (all-zero expected)

- `all_safety_warnings_zero`: True
- `cap_binding_events_count`: 0
- `n_calculation_drift_detected_count`: 0
- `non_rth_fill_warning_count`: 0
- `per_market_unit_count_invariant_violation_count`: 0
- `pyramid_state_machine_violation_count`: 0
- `rollover_violation_count`: 0
- `stale_fill_warning_count`: 0
- `unsupported_order_type_detected_count`: 0

## No-pyramid attestation

- `max_units_observed_per_market`: {'CL': 1, 'GC': 1, 'NQ': 0, 'ZN': 0}
- `max_units_observed_per_market_max`: 1
- `max_units_per_market_config`: 1
- `no_pyramid_invariant_held`: True
- `per_market_unit_count_invariant_violation_count`: 0
- `second_unit_add_attempt_count`: 0

## K-gate evaluation (rejection criteria; none should fire)

**K_fires:** [] (count = 0)

| K-gate | Fires? |
|---|:-:|
| `K10_avg_pairwise_corr_gt_0_50` | skip (None) |
| `K11_cap_binding_events_gt_1000` | ok (False) |
| `K12_DR_fires_on_cost_stress` | skip ('NOT_EVALUATED_THIS_TURN_ONLY_S1_RUN') |
| `K1_sharpe_proxy_lt_0` | ok (False) |
| `K2_expectancy_le_0` | ok (False) |
| `K4_trade_curve_maxdd_gt_50` | ok (False) |
| `K6_safety_warning_count_gt_0` | ok (False) |
| `K7_correlation_gate_silently_introduced` | ok (False) |
| `K7_filter_silently_introduced` | ok (False) |
| `K8_sealed_parent_drift` | skip (0) |
| `K9_closed_trades_lt_100` | ok (False) |

## A-gate evaluation (acceptance criteria; all must pass)

| A-gate | Status |
|---|---|
| `A10_cap_binding_events_eq_0` | **PASS** {'value': 0} |
| `A1_closed_trades_ge_100` | **PASS** {'threshold': 100, 'value': 200} |
| `A2_sharpe_proxy_gt_0` | **PASS** {'threshold': 0.0, 'value': 0.14311192966266303} |
| `A3_expectancy_gt_0` | **PASS** {'threshold': 0.0, 'value': 4865.489302337149} |
| `A4_trade_curve_maxdd_pct_le_50` | **PASS** {'threshold': -50.0, 'value': -28.305996161770587} |
| `A5_2of4_markets_wr_gap_ge_0_or_portfolio_wr_gap_ge_plus_half_pp` | **PASS** {'portfolio_wr_gap_pp': 10.478591202045537, 'note': 'evaluated from trade_diagnostics.win_rate_gap_to_breakeven_pp'} |
| `A6_validator_pass` | **PASS** {'note': 'no-pyramid attestation + plan-lock validator inherited byte-equivalent from s8-D1'} |
| `A8_cost_stress_S0_S4_run` | (not evaluated this turn) {'evaluated_this_turn': False, 'note': 'only S1 baseline executed this turn; S0/S2/S3/S4 require separate authorization (P6.5)'} |
| `A9_phase2_c1_c8_inheritance_attestable` | **PASS** {'note': 'C1-C8 inherited byte-equivalent from phase2_safety_contract_template'} |

## Cache-view decision (loud — repeated for the finalized report)

- Decision: **COPY_IS_ONLY_SUBSET_INTO_FRESH_DIR**

The original databento_cache contains 624 files (480 IS + 144 OOS) as a parallel-session-augmented mixed cache, but the driver's assert_cache_complete() requires exactly 480 IS files / 129,790,451 bytes (EXPECTED_FILES_PER_ROOT=120 per market, EXPECTED_CACHE_BYTES locked at P3 BUILD time). The operator authorized copying the IS-only subset into a fresh sibling directory (databento_cache_is_only) and monkey-patching ONLY in_sample_driver.CACHE_ROOT at runtime to point there. The EXPECTED_FILES_PER_ROOT and EXPECTED_CACHE_BYTES constants are NOT monkey-patched, so the driver's hard cache-completeness guard validates the copied IS-only subset against the original IS-only dimensions. The original 624-file cache directory is left untouched and pristine. This preserves chain-of-custody while allowing P6 IS to execute against an IS-only view.

- Original cache (pristine): `C:\SPARTA_BRAIN\data\databento_cache`
- IS-only cache (P6 view):   `C:\SPARTA_BRAIN\data\databento_cache_is_only`
- IS files copied:           480 files / 129,790,451 bytes
- Original cache pristine through run: True
- Monkey-patched attrs:      ['CACHE_ROOT']
- NOT monkey-patched:        ['EXPECTED_FILES_PER_ROOT', 'EXPECTED_CACHE_BYTES']

## Hard boundaries held

- no_broker_adapter_touched: True
- no_commit: True
- no_d5_b005_001_nke_revival: True
- no_databento_api_call: True
- no_db_historical: True
- no_fetch: True
- no_live_trading: True
- no_monkey_patch_of_expected_constants: True
- no_network_call: True
- no_obsidian_touched: True
- no_oos_file_touched: True
- no_oos_inspection: True
- no_orig_cache_mutation: True
- no_p6_5_cost_stress_sweep: True
- no_p7_decision_memo: True
- no_paper_trading: True
- no_profitability_claim: True
- no_promotion_to_live: True
- no_pytest: True
- no_qc_runtime: True
- no_review_queue_mutation: True
- no_s8_d1_or_s7_d1_modified: True
- no_scheduler_change: True
- no_source_file_modification: True

## Inherited seals

- `tier_n_spec_seal_sha256`: `f5ca5ee63024e9c8b7b1e85762558ec35eb3d4ebb9ce2a160cbe0f1a0e80a679`
- `plan_lock_seal_sha256`: `ba8bf954d44b373c0ffdc38a1cf8f73dec31a9fc538f0b7584a20659d79ea354`
- `phase2_plan_seal_sha256`: `7a48ad64236971e6fd2a2fa58ab7ab746a71543778ed0a868f3cdf9ff8f74ac3`
- `p3_build_runner_report_seal_sha256`: `1eb04aa312f4053134c1e9387be7716aa4564c019168ee2cedcf789063d96405`
- `p3_build_in_sample_driver_report_seal_sha256`: `ddd604c96508a0ab835bcbae6e72fabc2993cd3f0dc459898ca326617dd96443`
- `p3_5_scaffold_completion_seal_sha256`: `66d38f359b54882b3107c4ad4291673d63f05f5b0d3daa19088b4a4c76469261`
- `p4_smoke_seal_sha256`: `c31ded81f9a2883586883aadda4d64d629a047917fcebd56169ca42eccf4fdde`

## Verdict finalizer note

Verdict computed in a post-processing pass after driver run. The driver returns raw stats; the orchestrator applies K-gate (rejection) and A-gate (acceptance) logic inherited from the s8-D1 phase-2 plan to derive the C7 closed enum verdict. Driver output (driver_return_payload) is the deterministic ground truth; no re-run was performed.
