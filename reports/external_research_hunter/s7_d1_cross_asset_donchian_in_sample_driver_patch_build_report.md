# s7 D1 -- In-Sample Driver Patch Build Report (SEALED)

**Schema:** `sparta.external_research_hunter.s7_d1_cross_asset_donchian_in_sample_driver_patch_build_report.v1`
**Status:** `SEALED`
**Candidate operational status:** `IN_SAMPLE_DRIVER_PATCHED_NOT_EXECUTED`
**Sealed at (UTC):** `2026-05-25T20:01:43Z`
**Trading status:** `PAUSED`
**Live status:** `BLOCKED_AT_6_GATES`

> PATCH-only. No driver run. No DBN decode. No backtest. No real data loaded.
> No Databento API/network/QC call. No obsidian touch. No review_queue mutation.
> No filter introduced. AMB6 NONE preserved. s6 cap-bugfix preserved.
> Prior `_diagnostic_result_sealed` stays committed and byte-stable.
> NO_BACKTEST_BEFORE_SEAL_AND_AUTHORIZATION_INVARIANT continues to hold.

## Driver file (post-patch)
- Path:                       `external_research_hunter/s7_d1_cross_asset_donchian_runner_harness/in_sample_driver.py`
- byte sha256 PRIOR committed: `ae0687559bf3d1734121fff32fb6d6d1752b95ade54c7da4c0f548bd78333394`
- byte sha256 POST patch:     `8741bc5182e227336a5c0e75afa9d037fc1c633b12eae97577ef98b6eea31ea9`
- bytes:                       33,116
- lines:                       656

## Supersession
- Supersedes prior driver_build_report seal: `26e9c6f0c217f1f2daf994445bcae0c4d1bfe1ef9e81cfc1133f41823816b38e`
- Supersedes prior driver byte sha: `ae0687559bf3d1734121fff32fb6d6d1752b95ade54c7da4c0f548bd78333394`

This patch_build_report supersedes the prior driver_build_report (seal 26e9c6f0c217f1f2daf994445bcae0c4d1bfe1ef9e81cfc1133f41823816b38e) which was byte-tied to the prior driver sha ae0687559bf3d1734121fff32fb6d6d1752b95ade54c7da4c0f548bd78333394. The prior report remains committed for history and chain integrity. The live driver is now at sha 8741bc5182e227336a5c0e75afa9d037fc1c633b12eae97577ef98b6eea31ea9 which reflects this P6.5a patch.

## Inheritance chain (drift=0; 10 prior seals)
- Predecessor (s7 selection plan): `8d8851bc365ef9a6eb7883b24f272d8462cb4bda9c9e725aa46415e1434f9eac`
- Tier-N spec seal:                `72602305ef8d678195f9ab91a6d4cb8e7a473ee1a641cf9e8f91b8d4e31134c3`
- Plan-lock seal:                  `0f8e9fe6bc4f50e4f17c41611dbd01b7f9df3047ed448a3e9dffe7533210572d`
- Phase-2 plan seal:               `e1800ee28bd99a27da94d048fce4512401bc6ecd66b89e9d184f6c3050e2669a`
- Runner build report seal:        `10610a6ad47c2fd584b556e773edb3ea09c8dfa9fb67aaa350b526938df03946`
- Execution guard build seal:      `5cfbfdbbb9fc695673e5d8dabce0019a67d053a7b18ad962962a9a97311b017e`
- Smoke pass report seal:          `ec244e92953ab850f68f7ec88945c80263bb40f154a90bba19bf930f4c9133e8`
- Blocked report seal:             `f0f465d4c9b9199c4a45c060b8ff2552368128c5086354307394d2f8999fccf0`
- Prior driver build seal:         `26e9c6f0c217f1f2daf994445bcae0c4d1bfe1ef9e81cfc1133f41823816b38e`
- Diagnostic result seal:          `157ad1bf5a8994ea5364cffcf3f596728778f40ead2eb51615081c72e2b2bde5`
- Patch plan seal:                 `d03201de481f8712b008e213e16e082a2f394a977f65540705b225f93523fe1f`
- Parent sha drift at patch:       **0**

## Static validation
- ast.parse ok:                  **True**
- compile ok:                    **True**
- forbidden imports pass:        **True**
- no module-level side effects:  **True**
- top-level side effects:        `[]`
- databento lazy:                **True**
- db.Historical used:            **False**  (must be False)
- db.DBNStore.from_file used:    **True**
- required functions present:    ['assert_cache_complete', 'assert_seal_inheritance', 'derive_rth_daily_bars', 'iterate_market_minute_bars', 'load_dbn_local', 'run_in_sample']
- AMB6 filter NONE mentioned:    **True**
- s6 cap-bugfix attested:        **True**
- Donchian 55 referenced:        **True**
- Donchian 20 referenced:        **True**

## Regression proofs RP1-RP7
### RP1 - static buf_len += 1 on entry/exit/stop terms
- pass: **True**
- entry_channel_length+1 present: `True`
- exit_channel_length+1 present:  `True`
- stop_n_period+1 present:        `True`

### RP2 - inline runtime guard present
- pass: **True**
- runtime_guard_present: `True`

### RP3 - synthetic-entry-fires proof (NO DBN decode, NO real driver run)
- pass: **True**
- `A_deque_maxlen_56_holds_56_elements`: pass=True  detail={'len_after_60_appends': 56}
- `B_donchian_helpers_fire_long_on_synthetic_breakout`: pass=True  detail={'d_high_from_helper': 105.4, 'breakout_bar_high': 110.4, 'long_entry_would_fire': True}
- `C_patched_buf_len_resolves_to_56`: pass=True  detail={'entry_channel_length': 55, 'exit_channel_length': 20, 'stop_n_period': 20, 'computed_buf_len': 56, 'expected': 56}

### RP4 - byte sha distinct from prior committed
- pass: **True**
- prior:   `ae0687559bf3d1734121fff32fb6d6d1752b95ade54c7da4c0f548bd78333394`
- current: `8741bc5182e227336a5c0e75afa9d037fc1c633b12eae97577ef98b6eea31ea9`

### RP5 - same static-validation shape as P3.5 build report
- pass: **True**
- `compile_ok`: `True`
- `ast_parse_ok`: `True`
- `forbidden_imports`: `True`
- `no_side_effects`: `True`
- `lazy_databento`: `True`
- `no_db_historical`: `True`
- `db_dbnstore_present`: `True`
- `all_seals_embedded`: `True`

### RP6 - sealed-chain byte stability through patch
- pass: **True**
- drift_count_total_parents: 0
- all_10_sealed_chain_artifacts_match_recorded: **True**

### RP7 - supersession provenance note
- pass: **True**
- note: Prior driver_build_report stays committed for history; this report cites it via `supersedes.prior_driver_build_report_seal_sha256`.

**All RP1-RP7 pass: True**

## Other committed runner_harness files unchanged
- per git status (authoritative): **True**
- git status tracked-modified under runner_harness (must contain only in_sample_driver.py): `[' M external_research_hunter/s7_d1_cross_asset_donchian_runner_harness/in_sample_driver.py']`

## Obsidian-trade-logger baseline preserved
- start == end: **True**

## Negative invariants (this turn -- all False/pass)
- `driver_executed`: `False`
- `real_driver_run`: `False`
- `dbn_decoded`: `False`
- `real_data_loaded`: `False`
- `backtest_run`: `False`
- `p6_5b_executed`: `False`
- `databento_api_called`: `False`
- `databento_historical_client_invoked`: `False`
- `data_fetched`: `False`
- `network_call`: `False`
- `qc_called`: `False`
- `qc_cloud_submit`: `False`
- `oos_inspected`: `False`
- `yfinance_used`: `False`
- `obsidian_trade_logger_touched`: `False`
- `review_queue_mutated`: `False`
- `live_paper_bot_changed`: `False`
- `broker_or_exchange_adapter_imported`: `False`
- `scheduler_changed`: `False`
- `d5_revived`: `False`
- `b005_001_revived`: `False`
- `nke_revived`: `False`
- `any_committed_file_other_than_driver_modified`: `False`
- `any_prior_sealed_artifact_modified`: `False`
- `amb6_filter_none_violated`: `False`
- `s6_cap_bugfix_regressed`: `False`
- `donchian_55_changed`: `False`
- `donchian_20_changed`: `False`
- `threshold_loosened`: `False`
- `profitability_claim`: `False`
- `promotion_to_live`: `False`

## Authorization gates
- P6.5a authorizes nothing downstream: **True**
- P6.5a commit requires separate operator authorization: **True**
- P6.5b re-run requires separate operator authorization: **True**

## Next step
- `operator_authorization_required_for_p6_5a_commit`

## Seal block (canonical)
- **`report_seal_sha256`**: `2ab3ed5852de0dadcbe11da3aa7451a8c8a01372cb26395e4e28467628892522`
- **`seal_method`**: `sha256 over json.dumps(obj, sort_keys=True, separators=(',',':'), ensure_ascii=False, default=str) EXCLUDING report_seal_sha256 + seal_method`
- **`schema_id`**: `sparta.external_research_hunter.s7_d1_cross_asset_donchian_in_sample_driver_patch_build_report.v1`
- **`schema_status`**: `SEALED`
- **`report_date_utc`**: `2026-05-25T20:01:43Z`

*End of patch build report. PATCH-only. No driver run. No DBN decode. No backtest.*
