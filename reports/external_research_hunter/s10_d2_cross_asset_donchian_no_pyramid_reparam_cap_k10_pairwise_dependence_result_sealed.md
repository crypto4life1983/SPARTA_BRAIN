# S10-D2 K10 pairwise dependence — result (sealed)

**Schema:** `sparta.external_research_hunter.s10_d2_k10_pairwise_dependence_result_sealed.v1`  
**Phase prefix:** `PHASE2-S10-D2-XAD-RC-K10`  
**Candidate record id:** `s10-cross-asset-donchian-no-pyramid-reparam-cap-nq-gc-zn-cl`  
**Authored at (UTC):** `2026-05-27T03:16:16Z`  
**Authorization:** *"Authorize S10-D2 K10 pairwise dependence computation."*  
**Report seal sha256:** `8c620cc5bfe53f71d4ededba45b3d8cee0de54992db6819103875811cbdb99e4`

## Verdict

**`K10_PASS_AVG_PAIRWISE_CORR_AT_OR_BELOW_0_50`**

- K10 metric: `K10_avg_pairwise_corr_gt_0_50`
- Threshold: `0.5` (fires when avg strictly > threshold)
- Average pairwise correlation: **`+0.052804`**
- K10 fires: **`False`**

## Pairwise Pearson correlations

| Pair | Correlation |
|------|-------------|
| `CL__GC` | `+0.040105` |
| `CL__NQ` | `+0.112892` |
| `CL__ZN` | `-0.062184` |
| `GC__NQ` | `+0.021195` |
| `GC__ZN` | `+0.357209` |
| `NQ__ZN` | `-0.152390` |

## Data inputs

- IS window UTC: `2013-01-01` .. `2022-12-30`
- Cache root: `C:\SPARTA_BRAIN\data\databento_cache`
- Cache assertion: `True`  ·  Seal-inheritance assertion: `True`
- Tier-N spec seal (pinned): `f5ca5ee63024e9c8b7b1e85762558ec35eb3d4ebb9ce2a160cbe0f1a0e80a679`
- Plan-lock seal (pinned): `ba8bf954d44b373c0ffdc38a1cf8f73dec31a9fc538f0b7584a20659d79ea354`
- Phase-2 plan seal (pinned): `7a48ad64236971e6fd2a2fa58ab7ab746a71543778ed0a868f3cdf9ff8f74ac3`
- Predecessor seal (pinned): `007110ff5a57dd04b184409bad64fd667374cd049155416c869a73f7af0c1f97`

- Common-date count (after inner join across 4 symbols): `2253`
- Daily-return count per symbol (n-1): `2252`

## Method

- Return kind: `simple_daily_return`
- Alignment: `inner_join_on_calendar_date_after_per_market_rth_aggregation`
- Correlation: `pearson`
- Aggregation: `unweighted_arithmetic_mean_of_pair_correlations`
- RTH aggregation source: `external_research_hunter.s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_runner_harness.in_sample_driver.derive_rth_daily_bars`

## Hard boundaries (all held this run)

- `no_backtest_run`: `True`
- `no_broker_call`: `True`
- `no_cache_mutation`: `True`
- `no_candidate_promoted`: `True`
- `no_databento_api_key_access`: `True`
- `no_databento_call`: `True`
- `no_databento_historical_instantiation`: `True`
- `no_external_network_call`: `True`
- `no_file_content_modification_under_data_databento_cache`: `True`
- `no_file_content_modification_under_data_databento_cache_oos`: `True`
- `no_idea_memory_mutation`: `True`
- `no_lessons_md_staged_or_modified`: `True`
- `no_live_trading`: `True`
- `no_oos_computation`: `True`
- `no_oos_inspection`: `True`
- `no_paper_trading`: `True`
- `no_parameter_changes`: `True`
- `no_review_queue_mutation`: `True`
- `no_signal_computed`: `True`
- `no_simulator_run`: `True`
- `no_socket_open_attempt`: `True`
- `no_strategy_lab_invoked`: `True`
- `no_strategy_optimization_authorized`: `True`
- `no_tier_n_spec_mutation`: `True`

## Posture invariants (unchanged by this evaluation)

- Trading status: `PAUSED`
- Live status: `BLOCKED_AT_6_GATES`
- FRC granted: `False`
- Advisory label (permanent): `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE`
- verdict_never_means_live_ready: `True`
- live_promotion_path_closed: `True`

