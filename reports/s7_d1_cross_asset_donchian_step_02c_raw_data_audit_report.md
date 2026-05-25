# s7 D1 Donchian Step 02c - Raw-Data Audit Report

> Independent claude-side audit of the four canonical daily-bar CSVs at
> data/s7_d1_cross_asset_donchian/raw/ deposited by Step 02b.
> Audit only. No Donchian signal. No simulator. No backtest. No fetch.

**Phase:** `S7_D1_DONCHIAN_STEP_02C_RAW_DATA_AUDIT`
**Schema:** `sparta.donchian.step_02c_raw_data_audit_report.v1`
**Controller session:** THIS_SESSION_ONLY
**Report date (UTC):** 2026-05-25T22:47:05Z
**Audit verdict:** `PASS`

**Companion JSON:** `reports/s7_d1_cross_asset_donchian_step_02c_raw_data_audit_report.json` (sha256 + seal recorded only in JSON to break sha cycle; recompute from JSON bytes to verify)
**Report seal:** see JSON `report_seal_sha256` field (canonical seal_method also in JSON)

---

## 0. Anchors

- Plan: `docs/s7_d1_cross_asset_donchian_step_02c_next_phase_plan.md` (sha256 `c7dfd00784bbcb9bd8217ac88f4e5b440698e690dd67824f529403259140e5db`, commit `faebd583955cf13f8acece99da59fce6e95295fe`)
- Step 02b fetch_run_manifest.json sha256: `8fe210138dedcbaa07882b704cc3c3e30ba2ca4a1d4db7f05ca4dc782005a8f7`
- Step 02b paste-back report seal: `6328bae3ddf67e0045d2aac42b6abcac8948372d19e5f042f0a9d63e1db46c50`
- audit_manifest.json: `data/s7_d1_cross_asset_donchian/raw/audit_manifest.json` (sha256 `794a9386abc68fdffe411e5a54534852293c8ba9c9c14fc4a2443c67a374bdcb`, bytes 2488)

## 1. Per-symbol A-checks (A1-A14)

| Symbol | bytes | sha16 | rows | first | last | A1 | A2 | A4 | A5 | A6 | A7 | A8 | A9 | A10 | A11 | A12 | A13 | A14 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SPY | 340,390 | bad97abba5283694 | 3116 | 2014-01-02 | 2026-05-22 | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK |
| TLT | 342,022 | 2cab9fc3d2e26c62 | 3116 | 2014-01-02 | 2026-05-22 | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK |
| GLD | 343,015 | 7ff41cda6214d073 | 3116 | 2014-01-02 | 2026-05-22 | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK |
| USO | 333,701 | 0b5b5b9472e5bdf5 | 3116 | 2014-01-02 | 2026-05-22 | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK |

## 2. Manifest consistency (M1-M12)

- `M1_storage_path`: **OK**
- `M2_symbols_requested`: **OK**
- `M3_start_end_date`: **OK**
- `M4_frequency`: **OK**
- `M5_four_per_symbol_keys`: **OK**
- `M6_per_symbol_csv_sha256_matches_observed`: **OK**
- `M7_per_symbol_rows_match_observed`: **OK**
- `M8_per_symbol_first_date_match`: **OK**
- `M9_per_symbol_last_date_match`: **OK**
- `M10_safety_blocks_present_and_well_formed`: **OK**
- `M11_no_secret_substring_in_manifest`: **OK**
- `M12_fetch_manifest_sha256_matches_pin`: **OK**

## 3. Date-span checks (D1-D7)

- D1 span in 10..13.5 yr band per symbol: **OK** (per-symbol years: {'SPY': 12.383299, 'TLT': 12.383299, 'GLD': 12.383299, 'USO': 12.383299})
- D2 unique date count = 3116 per symbol: **OK** ({'SPY': 3116, 'TLT': 3116, 'GLD': 3116, 'USO': 3116})
- D3 cross-symbol date set aligned: **OK**
- D4 NYSE business-day gap diagnostic: weekday_count=3232, observed_sessions=3116, gap=116, gap/year=9.367 - within 7..13/yr band: **OK**
- D5 first observed = first business day on/after 2014-01-01 (2014-01-02): **OK**
- D6 last observed = pinned 2026-05-22: **OK**
- D7 no date out of band [2014-01-01, 2026-05-25]: **OK**

## 4. Adjusted-close divergence (J1-J5) per symbol

**Two divergence metrics are reported per symbol** (see Section 4a finding F1):

- **J1 max ABSOLUTE divergence** = `max(|close - adj_close|)` in dollars
- **J1b max RELATIVE divergence** = `max(|close - adj_close| / close)` as fraction
- The Step 02b manifest's `adjusted_vs_unadjusted_max_divergence` stores the **relative** metric, which is what J3 cross-checks against.

| Symbol | J1 max ABS ($) | J1b max REL | J2 mean ABS ($) | J2 median ABS ($) | J2 rows close!=adj | J3 matches manifest pin (rel) | J4 no_auto_adjust | J5 no_signal |
|---|---|---|---|---|---|---|---|---|
| SPY | 36.69218445 | 0.18773115 | 23.97613219 | 27.59138489 | 3071 | OK (pin 0.18773115) | OK | OK |
| TLT | 36.87542725 | 0.28787852 | 20.65845354 | 23.54914856 | 3100 | OK (pin 0.28787852) | OK | OK |
| GLD | 0.00000000 | 0.00000000 | 0.00000000 | 0.00000000 | 0 | OK (pin 0.0) | OK | OK |
| USO | 0.00000000 | 0.00000000 | 0.00000000 | 0.00000000 | 0 | OK (pin 0.0) | OK | OK |

## 4a. Audit finding F1 - manifest divergence metric clarification

> **Finding ID:** `F1_manifest_divergence_metric_clarification`
>
> The Step 02b `fetch_run_manifest.json` field
> `per_symbol[sym].adjusted_vs_unadjusted_max_divergence` stores the **max
> RELATIVE** divergence `max(|close - adj_close| / close)`, not the max
> ABSOLUTE divergence `max(|close - adj_close|)`. The Step 02c plan section
> 10 J1 (sealed at commit `faebd58`) incorrectly described the manifest
> field as the absolute metric. Both metrics are legitimate; this audit
> reports both per symbol (J1 absolute, J1b relative) and uses the
> relative metric for the J3 cross-check because that matches the
> manifest's actual stored value.
>
> **Impact on data integrity:** NONE. The CSV data is sound under both
> metrics; this is a documentation/definition clarification, not a
> data-quality issue.

**Per-symbol evidence:**

| Symbol | manifest pin | observed max ABSOLUTE | observed max RELATIVE | relative matches manifest pin |
|---|---|---|---|---|
| SPY | 0.18773115 | 36.69218445 | 0.18773115 | OK |
| TLT | 0.28787852 | 36.87542725 | 0.28787852 | OK |
| GLD | 0.00000000 | 0.00000000 | 0.00000000 | OK |
| USO | 0.00000000 | 0.00000000 | 0.00000000 | OK |

**Remediation options (each requires separate authorization):**

- Option A: Re-author Step 02c plan section 10 J1 with corrected metric description (relative not absolute). Requires separate authorization.
- Option B: Add an absolute-divergence field to fetch_run_manifest.json alongside the existing relative field. Requires separate authorization (the plan boundary forbids fetch_run_manifest.json mutation in this audit phase).
- Option C: Accept the audit as documenting the clarification and proceed without changing plan or manifest. This audit's report records both metrics permanently.

## 5. VA gates (audit self-validation)

- `VA1_three_output_files_will_exist_at_locked_paths`: **OK**
- `VA2_schema_field_present`: **OK**
- `VA3_a_check_block_with_all_14_per_symbol`: **OK**
- `VA4_m_check_block_with_all_12`: **OK**
- `VA5_d_check_block_with_all_7`: **OK**
- `VA6_j_check_block_with_all_5_per_symbol`: **OK**
- `VA7_boundaries_held_block_present`: **OK**
- `VA8_negative_invariants_block_present`: **OK**
- `VA9_seal_method_and_report_seal_present`: **OK**
- `VA10_md_and_json_sha_cross_referenced`: **OK**

## 6. Boundaries held (all True)

 - `audit_only_under_operator_authorization`  
 - `no_20bar_channel_computed`  
 - `no_55bar_channel_computed`  
 - `no_CLAUDE_md_modification`  
 - `no_RUNBOOK_modification`  
 - `no_audit_script_left_behind`  
 - `no_backtest_run`  
 - `no_branch_change`  
 - `no_branch_created`  
 - `no_certificate_verification_bypass`  
 - `no_commit_beyond_audit_report_artifacts`  
 - `no_csv_modification`  
 - `no_databento_api_key_access`  
 - `no_databento_call`  
 - `no_docs_decisions_md_modification`  
 - `no_donchian_signal_computed`  
 - `no_existing_csv_modification`  
 - `no_fetch_manifest_modification`  
 - `no_git_push`  
 - `no_gitignore_modification`  
 - `no_idea_memory_mutation`  
 - `no_live_trading`  
 - `no_network_call`  
 - `no_orb_branch_artifact_mutation`  
 - `no_orb_step_30_cost_constant_mutation`  
 - `no_os_environ_DATABENTO_API_KEY_referenced`  
 - `no_pipeline_manifest_modification`  
 - `no_review_queue_mutation`  
 - `no_rolling_signal_statistic_computed`  
 - `no_simulator_run`  
 - `no_source_modification`  
 - `no_step_02b_artifact_modification`  
 - `no_step_02c_plan_modification`  
 - `no_strategy_lab_run`  
 - `no_tests_modification`  
 - `no_vendor_substitution`  
 - `no_wilder_atr_computed`  
 - `no_yahoo_finance_call`  
 - `no_yfinance_call`

## 7. Negative invariants (all False)

 - `backtest_run`  
 - `branch_changed`  
 - `branch_created`  
 - `commit_made_beyond_audit`  
 - `csv_modified`  
 - `databento_api_key_accessed`  
 - `databento_called`  
 - `donchian_signal_computed`  
 - `fetch_manifest_modified`  
 - `git_pushed`  
 - `live_trading`  
 - `manifest_modified`  
 - `network_used`  
 - `orb_branch_mutated`  
 - `plan_modified`  
 - `simulator_run`  
 - `yahoo_finance_called`  
 - `yfinance_called`

## 8. API-key safety confirmation

- `any_network_call_during_audit`: **False**
- `databento_api_key_accessed`: **False**
- `databento_called`: **False**
- `os_environ_DATABENTO_API_KEY_referenced`: **False**
- `yahoo_finance_called_during_audit`: **False**
- `yfinance_called_during_audit`: **False**

## 9. Seal verification

```
seal_method = sha256 over json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False) EXCLUDING report_seal_sha256 + seal_method

report_seal_sha256 = <see JSON report_seal_sha256 field; this MD does not embed it to avoid sha cycle>
```

Companion JSON sha256 = <recompute sha256 of the JSON bytes on disk>

**Audit verdict: `PASS`.** Trading: PAUSED. Live: BLOCKED at 6 gates.

