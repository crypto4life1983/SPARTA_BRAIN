# s7 D1 -- P6.5a Patch Plan (SEALED, plan-only)

**Schema:** `sparta.external_research_hunter.s7_d1_cross_asset_donchian_p6_5a_patch_plan.v1`
**Status:** `SEALED`
**Candidate operational status:** `P6_5A_PATCH_PLAN_SEALED_NO_CODE_CHANGE`
**Sealed at (UTC):** `2026-05-25T19:48:03Z`
**Trading status:** `PAUSED`
**Live status:** `BLOCKED_AT_6_GATES`
**FRC granted:** `False`

> PLAN ONLY. No code modified. No driver run. No DBN decode. No backtest.
> No Databento API/network/QC call. No obsidian touch. No review_queue mutation.
> Prior P6.5 result REMAINS COMMITTED and SEALED -- this plan does not invalidate or relabel it.
> NO_BACKTEST_BEFORE_SEAL_AND_AUTHORIZATION_INVARIANT continues to hold.

## Inheritance chain (drift=0; 9 prior seals + driver byte sha)
- Predecessor (s7 selection plan): `8d8851bc365ef9a6eb7883b24f272d8462cb4bda9c9e725aa46415e1434f9eac`
- Tier-N spec seal:                `72602305ef8d678195f9ab91a6d4cb8e7a473ee1a641cf9e8f91b8d4e31134c3`
- Plan-lock seal:                  `0f8e9fe6bc4f50e4f17c41611dbd01b7f9df3047ed448a3e9dffe7533210572d`
- Phase-2 plan seal:               `e1800ee28bd99a27da94d048fce4512401bc6ecd66b89e9d184f6c3050e2669a`
- Runner build report seal:        `10610a6ad47c2fd584b556e773edb3ea09c8dfa9fb67aaa350b526938df03946`
- Execution guard build seal:      `5cfbfdbbb9fc695673e5d8dabce0019a67d053a7b18ad962962a9a97311b017e`
- Smoke pass report seal:          `ec244e92953ab850f68f7ec88945c80263bb40f154a90bba19bf930f4c9133e8`
- Blocked report seal:             `f0f465d4c9b9199c4a45c060b8ff2552368128c5086354307394d2f8999fccf0`
- Driver build report seal:        `26e9c6f0c217f1f2daf994445bcae0c4d1bfe1ef9e81cfc1133f41823816b38e`
- Diagnostic result seal:          `157ad1bf5a8994ea5364cffcf3f596728778f40ead2eb51615081c72e2b2bde5`
- Driver byte sha at plan time:    `ae0687559bf3d1734121fff32fb6d6d1752b95ade54c7da4c0f548bd78333394`  matches_committed=**True**
- Parent sha drift at plan:        **0**

## Bug identification
- **File:**  `external_research_hunter/s7_d1_cross_asset_donchian_runner_harness/in_sample_driver.py`
- **Function:** `run_in_sample`
- **Lines:** 324-325 (buf_len computation) vs 461-465 (entry-trigger usage)

### Current code at the bug site
```python
buf_len = max(CONFIG['entry_channel_length'], CONFIG['exit_channel_length'], CONFIG['stop_n_period'] + 1)
# Resolves to: max(55, 20, 21) = 55
deque(maxlen=buf_len)  -- maxlen = 55
```

### Consumer (entry trigger) requires len >= 56
```python
if len(buf['close']) >= CONFIG['entry_channel_length'] + 1:  -- requires len >= 56
hist_highs = list(buf['high'])[-(CONFIG['entry_channel_length'] + 1):-1]  -- slices [-56:-1] which gives 55 elements when buffer holds 56; the slicing is correct, but the buffer's maxlen is too small to ever reach 56 elements
```

### How it manifests
deque maxlen caps the buffer at 55 elements. After ~55+ bars of market history, the deque is full at 55 elements; each new append evicts the oldest. len(buf['close']) is therefore bounded above by 55 and NEVER reaches >= 56. Result: the `if len >= 56:` branch never executes, the entry trigger never fires, no entries pending, no units opened, no closed trades, no PnL.

### Why smoke tests didn't catch it
test_smoke_t1_t15.py T5 (test_t5_entry_trigger_synthetic_breakout) validates the donchian_high HELPER directly on a 55-bar slice -- it does NOT exercise run_in_sample's buffer-based bar loop. The smoke suite therefore validates the helpers and the PyramidManager state machine in isolation, but never the orchestration glue inside run_in_sample. The bug lives in the orchestration glue.

### Why static validation didn't catch it
P3.5 static validation (ast.parse + compile + AST forbidden-import scan + no-module-level-side-effects + required-functions-present + embedded-seals + AMB6/cap-bugfix attestation) is structural, not semantic. It cannot detect that an arithmetic max() over the channel lengths is off by one relative to the consumer's `+ 1` slice requirement. Static checks verified the driver was IMPORTABLE and SAFE, not that it would produce nonzero trades.

### Empirical evidence from the prior P6.5 run
- `runtime_seconds`: `241.2`
- `trading_days_in_union`: `2574`
- `per_market_daily_bar_counts`: `{'NQ': 2526, 'GC': 2290, 'ZN': 2571, 'CL': 2567}`
- `closed_trades_portfolio`: `0`
- `pending_entries_observed`: `0 (entry trigger branch never executed)`
- `safety_counters`: `all 0 (no entry => no pyramid/N-drift events)`
- `cap_binding_events`: `0`
- `diagnostic_result_seal`: `157ad1bf5a8994ea5364cffcf3f596728778f40ead2eb51615081c72e2b2bde5`

### Why 0 trades is strategy-implausible
A 10-year no-filter Donchian-55 breakout on 4 cross-asset markets (NQ + GC + ZN + CL) with realistic volatility produces dozens to hundreds of breakouts per market: every trending move > 55 prior days' high/low fires. s5 (single-market NQ) produced 64 trades. s6 (3-market same-family) produced 191 trades. s7 D1 (4-market cross-asset) on this universe over the same 10-year window cannot produce 0. The 0 result is mechanically impossible from a working bar loop and is therefore driver-driven.

## Proposed minimal fix
- **Change kind:** two-character addition (`+ 1` to two terms inside the max() call)
- **Lines to change:** 1
- **Files to modify:** 1
- **All other lines unchanged:** True

### Diff
```python
# BEFORE:
    buf_len = max(CONFIG['entry_channel_length'], CONFIG['exit_channel_length'],
                  CONFIG['stop_n_period'] + 1)

# AFTER:
    buf_len = max(CONFIG['entry_channel_length'] + 1, CONFIG['exit_channel_length'] + 1,
                  CONFIG['stop_n_period'] + 1)
# Resolves to: max(56, 21, 21) = 56
```

### Additional self-test recommended (insert immediately after line 325)
- Kind: runtime assertion inserted immediately after buf_len computation
- Purpose: Fail loud at function entry if the buffer-size invariant regresses. Pure invariant check; no I/O, no decode, no network.

```python
    if buf_len < CONFIG['entry_channel_length'] + 1:
        raise RuntimeError(f'P6.5a regression: buf_len={buf_len} < entry_channel_length+1={CONFIG[\'entry_channel_length\']+1}; entry trigger would never fire')
```

## Preservation invariants required in patch (must all remain True)
- `donchian_entry_length_55`: `True`
- `donchian_exit_length_20`: `True`
- `stop_n_multiplier_2`: `True`
- `pyramid_max_units_per_market_4`: `True`
- `pyramid_spacing_n_multiplier_0_5`: `True`
- `risk_pct_per_unit_0_01`: `True`
- `starting_cash_mnq_equivalent_100000`: `True`
- `portfolio_cap_max_units_16`: `True`
- `portfolio_cap_uses_unit_count_not_total_quantity_s6_bugfix`: `True`
- `amb6_filter_none`: `True`
- `rth_per_market_windows_NQ_GC_ZN_09_30_16_00_CL_09_30_14_30`: `True`
- `in_sample_window_2013_01_01_to_2022_12_30`: `True`
- `cost_stress_tiers_S0_S1_S2_S3_S4`: `True`
- `all_8_inherited_seals_embedded`: `True`
- `lazy_databento_import_inside_load_dbn_local`: `True`
- `no_db_Historical_client_anywhere`: `True`
- `use_db_DBNStore_from_file_for_local_decode_only`: `True`
- `no_module_level_side_effects`: `True`
- `lessons_hunter_004_canonical_seal_recipe_unchanged`: `True`

## Files modified by P6.5a patch
- `external_research_hunter/s7_d1_cross_asset_donchian_runner_harness/in_sample_driver.py`

## Files created by P6.5a patch
- `reports/external_research_hunter/s7_d1_cross_asset_donchian_in_sample_driver_patch_build_report.json`
- `reports/external_research_hunter/s7_d1_cross_asset_donchian_in_sample_driver_patch_build_report.md`

## Files NOT modified (must be byte-stable through patch)
- `external_research_hunter/s7_d1_cross_asset_donchian_runner_harness/main.py`
- `external_research_hunter/s7_d1_cross_asset_donchian_runner_harness/execution_guard.py`
- `external_research_hunter/s7_d1_cross_asset_donchian_runner_harness/README.md`
- `external_research_hunter/s7_d1_cross_asset_donchian_runner_harness/__init__.py`
- `external_research_hunter/s7_d1_cross_asset_donchian_runner_harness/requirements.txt`
- `external_research_hunter/s7_d1_cross_asset_donchian_runner_harness/tests/*`
- `ANY prior sealed report`
- `ANY parent artifact`
- `ANY committed code outside in_sample_driver.py`
- `obsidian-trade-logger/**`

## Regression proofs proposed
### RP1_static_invariant -- static-source-grep

After patch, source must declare buf_len with explicit `+ 1` on entry_channel_length term.

**Check:** `grep -n "buf_len = max(CONFIG\['entry_channel_length'\] \+ 1" in_sample_driver.py returns >= 1 line`

### RP2_inline_runtime_assertion -- static-source-grep

After patch, run_in_sample raises RuntimeError if buf_len ever regresses below entry+1.

**Check:** `grep -n "P6.5a regression: buf_len=" in_sample_driver.py returns >= 1 line`

### RP3_synthetic_entry_fires -- new-pytest-test-OR-orchestrator-side-smoke

Construct a synthetic 60-bar series for one market where bar 56 has a clear breakout (high > prev-55-bar max). Run a bounded simulated bar loop (using the same code path as run_in_sample's inner block, with a stub for DBN decode) and assert that pending_entries[market] becomes non-None on the breakout bar.

**Scope choice:** Preferred: ORCHESTRATOR-side check during the P6.5a patch turn's static validation (no new test file added to runner_harness, no smoke re-run authorization needed). Alternative: add new tests/test_bar_loop_regression.py and re-run the T1-T15 + new test suite (requires a fresh P4-equivalent authorization).
**Preferred:** `orchestrator_side_static_check_no_new_test_file`

### RP4_byte_sha_distinct_from_committed -- byte-sha-check

After patch, in_sample_driver.py byte sha MUST differ from the committed P3.5 sha.

**Check:** `byte_sha256(in_sample_driver.py) != ae0687559bf3d1734121fff32fb6d6d1752b95ade54c7da4c0f548bd78333394  (current committed)`

### RP5_compile_and_ast_parse_unchanged_pass -- static-validation

Patched driver must still pass ast.parse + compile + AST forbidden-import scan + no-module-level-side-effects + lazy-databento-import + all 8 embedded-seals checks (same validation as P3.5 driver build report). The fix is a numerical change, not a structural one.

### RP6_chain_drift_zero -- sealed-chain-byte-stability

All 9 prior sealed artifacts MUST remain byte-stable through the patch turn. Patch only touches in_sample_driver.py + creates 2 new BUILD report files.

### RP7_existing_p3_5_driver_build_report_invalidated_or_superseded -- provenance-note

The committed P3.5 driver_build_report (seal 26e9c6f0c217f1f2daf994445bcae0c4d1bfe1ef9e81cfc1133f41823816b38e) is byte-tied to the original driver sha. After patch, that report no longer reflects the live driver. The new P6.5a patch_build_report should explicitly cite the prior driver_build_report seal and record `superseded_by: <new_patch_build_report_seal>`. The prior report STAYS committed (chain integrity) and is referenced for history.


## Interpretation of the prior P6.5 result
- Diagnostic result seal: `157ad1bf5a8994ea5364cffcf3f596728778f40ead2eb51615081c72e2b2bde5`
- Remains committed: **True**
- Remains sealed: **True**
- Remains byte-stable: **True**
- **Strategy-falsifying:** False
- **Driver-implementation-incomplete:** True
- **Hypothesis status after prior result:** `UNTESTED_PENDING_DRIVER_FIX_AND_RERUN`

### Framing for downstream artifacts
The prior P6.5 sealed result (closed_trades_portfolio=0, K9 fired, verdict INSUFFICIENT_SAMPLE) is the honest record of what the committed P3.5 driver (byte sha ae068755...) produced when invoked against the local DBN cache. It is NOT a strategy-falsifying result. It is a driver-implementation-incomplete result. Any downstream P7 decision memo MUST distinguish 'PARKED_FAILED_AT_INSUFFICIENT_SAMPLE due to driver buffer-size off-by-one' from 'PARKED_FAILED_AT_INSUFFICIENT_SAMPLE because the strategy genuinely produced too few trades on real data'. The cross-asset Donchian hypothesis (s7 selection plan §D1 §1) has NOT been empirically tested by the prior result.

## Authorization ladder
### P6.5a_patch_authorization

Apply the buffer-size fix + inline runtime assertion to in_sample_driver.py; produce a sealed driver_patch_build_report.

**Scope files:**
- `external_research_hunter/s7_d1_cross_asset_donchian_runner_harness/in_sample_driver.py (MODIFY)`
- `reports/external_research_hunter/s7_d1_cross_asset_donchian_in_sample_driver_patch_build_report.{md,json} (CREATE)`

**Scope invariants:** no DBN decode, no driver run, no network, no QC, no obsidian touch, no committed file modified except in_sample_driver.py, all preservation_invariants_required_in_patch held.

**Validation:** ast.parse + compile + AST forbidden-import scan + no-module-level-side-effects + lazy-databento + all 8 embedded-seals + RP1 + RP2 + RP4 + orchestrator-side synthetic-entry-fires check (RP3 preferred form).

### P6.5a_commit_authorization

Commit the patched driver + patch_build_report.

**Scope files:**
- `same 1 modified + 2 new files`

### P6.5b_rerun_authorization

Re-invoke in_sample_driver.run_in_sample(cost_tier='S1') against the SAME local DBN cache, with the patched driver, producing a SECOND sealed in_sample_diagnostic_result. The prior result REMAINS committed for history; the new result lives at a distinct path (e.g. _in_sample_diagnostic_result_sealed_rev2.{md,json}).

**Scope invariants:** in-sample only, no OOS, no fetch, no QC, no network, no obsidian touch, no code patch this turn (driver already patched in P6.5a).

**Estimated runtime:** ~4 min S1 baseline only (same as prior run if the fix doesn't add overhead).

### P6.5b_commit_authorization

Commit the new sealed result + a brief comparison memo vs the prior 0-trade result.

### P7_decision_memo_authorization

Author the in_sample_decision_memo from the new (post-patch) result. Park or proceed per the K/A gates as actually evaluated.


## Negative invariants (this turn -- all False/pass)
- `code_modified`: `False`
- `driver_run`: `False`
- `dbn_decoded`: `False`
- `backtest_run`: `False`
- `databento_api_called`: `False`
- `db_historical_client_invoked`: `False`
- `data_fetched`: `False`
- `network_call`: `False`
- `qc_called`: `False`
- `qc_cloud_submitted`: `False`
- `oos_inspected`: `False`
- `obsidian_trade_logger_touched`: `False`
- `review_queue_mutated`: `False`
- `live_trading`: `False`
- `paper_trading_changed`: `False`
- `scheduler_changed`: `False`
- `broker_or_exchange_adapter_imported`: `False`
- `yfinance_used`: `False`
- `d5_revived`: `False`
- `b005_001_revived`: `False`
- `nke_revived`: `False`
- `threshold_loosened`: `False`
- `any_committed_file_modified`: `False`
- `any_prior_sealed_artifact_modified`: `False`
- `profitability_claim`: `False`
- `promotion_to_live`: `False`
- `prior_p6_5_result_invalidated_or_relabeled`: `False`

## Obsidian-trade-logger preserved through plan turn
- start == end: **True**

## Next step
- `operator_authorization_required_for_p6_5a_patch_apply`

## Seal block (canonical)
- **`report_seal_sha256`**: `d03201de481f8712b008e213e16e082a2f394a977f65540705b225f93523fe1f`
- **`seal_method`**: `sha256 over json.dumps(obj, sort_keys=True, separators=(',',':'), ensure_ascii=False, default=str) EXCLUDING report_seal_sha256 + seal_method`
- **`schema_id`**: `sparta.external_research_hunter.s7_d1_cross_asset_donchian_p6_5a_patch_plan.v1`
- **`schema_status`**: `SEALED`
- **`report_date_utc`**: `2026-05-25T19:48:03Z`

*End of patch plan. PLAN ONLY. No code modified. No driver run. No DBN decode. No backtest.*
