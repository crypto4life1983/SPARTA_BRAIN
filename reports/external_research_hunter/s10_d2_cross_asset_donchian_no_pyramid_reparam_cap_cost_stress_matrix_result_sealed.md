# S10-D2 P6.5 cost-stress matrix S0..S4 (consolidated; V2 rerun under Option 2)

**Candidate:** `s10-cross-asset-donchian-no-pyramid-reparam-cap-nq-gc-zn-cl`
**Phase prefix:** `PHASE2-S10-D2-XAD-RC`
**Authored (UTC):** `2026-05-27T02:56:42.712481Z`
**Matrix verdict:** **READY_FOR_NEXT_PHASE**
**K12_DR_fires_on_cost_stress:** not_fired
**A8_cost_stress_S0_S4_run:** PASS
**Total DR fires across S0/S2/S3/S4:** 0
**Total wall (S0/S2/S3/S4 only):** 967.786s
**Report seal sha256:** `f9a34674de4f7fdf8098b39959032d152bf2282e9ad57cedd68bc33cee2099ab`

## Prior attempt note

An earlier P6.5 attempt by this orchestrator (V1) executed all 4 tiers successfully against data/databento_cache_is_only/ via CACHE_ROOT monkey-patch, but failed to write a sealed report because the post-state orig-cache pristine guard raised when external/parallel-session activity (commit 1ddf441 'Seal S10-D2 cache directory restructure (IS/OOS split; 624 sha preserved)') moved 144 OOS month-directories out of data/databento_cache/ DURING the V1 sweep. The V1 stdout output is informative but non-canonical (no sealed JSON; full driver_return_payload lost on process exit). This V2 rerun supersedes the V1 attempt and uses the now-restructured data/databento_cache/ directly with NO CACHE_ROOT monkey-patch, per operator Option 2.

## Cache-view decision

Per operator Option 2 authorization. The parallel-session commit 1ddf441 restructured the cache so data/databento_cache/ is now exactly the IS-only 480-file subset (129,790,451 bytes) that matches the driver's hardcoded EXPECTED_FILES_PER_ROOT (120) and EXPECTED_CACHE_BYTES. The driver reads its own default CACHE_ROOT with no monkey-patching of any kind. assert_cache_complete() validates the default location directly. The 144 OOS files now live separately at data/databento_cache_oos/ and are NOT read by my code at any point.

## Per-tier results

| Tier | Source | Wall (s) | Closed trades | Net PnL | Expectancy | Sharpe | Max DD % | DR fires |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `S0` | this turn (V2 rerun) | 226.664 | 200 | $987,241.79 | $4,936.21 | 0.1450 | -27.9740% | none |
| `S1` | S1 baseline (P6 seal) | 277.547 | 200 | $973,097.86 | $4,865.49 | 0.1431 | -28.3060% | none |
| `S2` | this turn (V2 rerun) | 255.419 | 200 | $913,849.33 | $4,569.25 | 0.1400 | -29.7591% | none |
| `S3` | this turn (V2 rerun) | 241.867 | 200 | $824,422.94 | $4,122.11 | 0.1300 | -30.3483% | none |
| `S4` | this turn (V2 rerun) | 243.836 | 200 | $567,872.41 | $2,839.36 | 0.1056 | -36.9263% | none |

## DR rule details per tier (S0/S2/S3/S4 only)

### S0

- `DR2_tier_net_pnl_le_0`: ok (False)
- `DR3_tier_sharpe_proxy_le_0`: ok (False)
- `DR4_tier_expectancy_le_0`: ok (False)
- `DR5_tier_closed_trades_lt_100`: ok (False)

### S2

- `DR2_tier_net_pnl_le_0`: ok (False)
- `DR3_tier_sharpe_proxy_le_0`: ok (False)
- `DR4_tier_expectancy_le_0`: ok (False)
- `DR5_tier_closed_trades_lt_100`: ok (False)

### S3

- `DR2_tier_net_pnl_le_0`: ok (False)
- `DR3_tier_sharpe_proxy_le_0`: ok (False)
- `DR4_tier_expectancy_le_0`: ok (False)
- `DR5_tier_closed_trades_lt_100`: ok (False)

### S4

- `DR2_tier_net_pnl_le_0`: ok (False)
- `DR3_tier_sharpe_proxy_le_0`: ok (False)
- `DR4_tier_expectancy_le_0`: ok (False)
- `DR5_tier_closed_trades_lt_100`: ok (False)

## Cache state snapshots

**data/databento_cache/ (IS-only, post-1ddf441)** drift during run: **False**

| Market | Pre files | Pre bytes | Post files | Post bytes |
|---|---:|---:|---:|---:|
| `NQ` | 120 | 53,148,359 | 120 | 53,148,359 |
| `GC` | 120 | 2,162,216 | 120 | 2,162,216 |
| `ZN` | 120 | 27,939,222 | 120 | 27,939,222 |
| `CL` | 120 | 46,540,654 | 120 | 46,540,654 |

**data/databento_cache_oos/ (separate; NOT touched by my code)** drift during run: **False**

| Market | Pre files | Pre bytes | Post files | Post bytes |
|---|---:|---:|---:|---:|
| `NQ` | 36 | 19,770,364 | 36 | 19,770,364 |
| `GC` | 36 | 540,803 | 36 | 540,803 |
| `ZN` | 36 | 8,573,282 | 36 | 8,573,282 |
| `CL` | 36 | 13,779,406 | 36 | 13,779,406 |

## Starting-cash invariant ($500,000 across all tiers)

- `S1`: None
- `S0`: $500,000
- `S2`: $500,000
- `S3`: $500,000
- `S4`: $500,000

All match 500000: **True**

## No-pyramid invariant attestation

- max_units_per_market_config: 1
- S1 (baseline): no_pyramid_invariant_held = True
- S0: no_pyramid_invariant_held = True
- S2: no_pyramid_invariant_held = True
- S3: no_pyramid_invariant_held = True
- S4: no_pyramid_invariant_held = True

## Hard boundaries held

- no_code_patch: True
- no_commit: True
- no_d5_b005_001_nke_revival: True
- no_databento_api_call: True
- no_db_historical: True
- no_fetch: True
- no_live_trading: True
- no_monkey_patch_of_any_kind: True
- no_network_call: True
- no_obsidian_touched: True
- no_oos_cache_mutation: True
- no_oos_file_read_or_written: True
- no_oos_inspection: True
- no_orig_cache_mutation_by_my_code: True
- no_paper_trading: True
- no_profitability_claim: True
- no_promotion_to_live: True
- no_qc_runtime: True
- no_review_queue_mutation: True
- no_s8_d1_or_s7_d1_modified: True
- no_scheduler_change: True
- no_source_file_modification: True
- no_threshold_loosening: True

## Inherited seals

- `tier_n_spec_seal_sha256`: `f5ca5ee63024e9c8b7b1e85762558ec35eb3d4ebb9ce2a160cbe0f1a0e80a679`
- `plan_lock_seal_sha256`: `ba8bf954d44b373c0ffdc38a1cf8f73dec31a9fc538f0b7584a20659d79ea354`
- `phase2_plan_seal_sha256`: `7a48ad64236971e6fd2a2fa58ab7ab746a71543778ed0a868f3cdf9ff8f74ac3`
- `p3_build_runner_report_seal_sha256`: `1eb04aa312f4053134c1e9387be7716aa4564c019168ee2cedcf789063d96405`
- `p3_build_in_sample_driver_report_seal_sha256`: `ddd604c96508a0ab835bcbae6e72fabc2993cd3f0dc459898ca326617dd96443`
- `p3_5_scaffold_completion_seal_sha256`: `66d38f359b54882b3107c4ad4291673d63f05f5b0d3daa19088b4a4c76469261`
- `p4_smoke_seal_sha256`: `c31ded81f9a2883586883aadda4d64d629a047917fcebd56169ca42eccf4fdde`
- `p6_is_baseline_S1_seal_sha256`: `e6cdc7c68a9e2b7b6d749b73ff433e585c9de55890af5dce3dca51d74430c1b8`
