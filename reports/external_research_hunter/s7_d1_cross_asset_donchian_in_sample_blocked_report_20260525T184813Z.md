# s7 D1 -- P6 In-Sample BLOCKED Report (SEALED)

**Schema:** `sparta.external_research_hunter.s7_d1_cross_asset_donchian_in_sample_blocked_report.v1`
**Status:** `SEALED`
**Candidate operational status:** `IN_SAMPLE_BLOCKED_RUNNER_NOT_EXECUTABLE_UNDER_AUTHORIZED_SCOPE`
**Sealed at (UTC):** `2026-05-25T18:48:13Z`
**Trading status:** `PAUSED`
**Live status:** `BLOCKED_AT_6_GATES`

> P6 in-sample run was authorized; the committed P3 runner cannot execute it under the
> authorized hard boundaries. Per operator's failure rule, this script stopped, did NOT
> patch any code, and is producing this sealed BLOCKED report. K1-K12 / A1-A10 / verdict
> are explicitly NOT evaluated -- reporting them on a runner that did not execute would
> be a false fire. NO_BACKTEST_BEFORE_SEAL_AND_AUTHORIZATION_INVARIANT continues to hold.

## Chain attestation (drift = 0)
- Parent sha drift at P6: **0**
- Tier-N spec seal:                  `72602305ef8d678195f9ab91a6d4cb8e7a473ee1a641cf9e8f91b8d4e31134c3`
- Plan-lock seal:                    `0f8e9fe6bc4f50e4f17c41611dbd01b7f9df3047ed448a3e9dffe7533210572d`
- Phase-2 plan seal:                 `e1800ee28bd99a27da94d048fce4512401bc6ecd66b89e9d184f6c3050e2669a`
- Runner build report seal:          `10610a6ad47c2fd584b556e773edb3ea09c8dfa9fb67aaa350b526938df03946`
- Execution guard build report seal: `5cfbfdbbb9fc695673e5d8dabce0019a67d053a7b18ad962962a9a97311b017e`
- Smoke pass report seal:            `ec244e92953ab850f68f7ec88945c80263bb40f154a90bba19bf930f4c9133e8`

## Cache attestation (matches operator P5 report)
| Root | file_count_observed | bytes_observed | bytes_expected | match |
|---|---:|---:|---:|---|
| `NQ` | 120 | 53,148,359 | 53,148,359 | OK |
| `GC` | 120 | 2,162,216 | 2,162,216 | OK |
| `ZN` | 120 | 27,939,222 | 27,939,222 | OK |
| `CL` | 120 | 46,540,654 | 46,540,654 | OK |

- All 4 roots present with 120 files each: **True**
- Cache matches operator P5 report:        **True**

## Runner executability assessment
- `main.py` byte sha:           `6330c2e1f81bcbda9e88bbd4bca63c613cb45c7b40020f345cc31f58b79ddd69`
- `main.py` lines:              `468`
- imports `databento`?          `False`
- imports any `dbn`?            `False`
- has `if __name__ == '__main__':`? `False`
- has top-level `def main()`?   `False`
- has DBN reader for local cache: **False**
- has standalone entry point:     **False**
- has real (non-stub) strategy loop: **False**
- **can_execute_in_sample_standalone:** **False**
- only available path with current committed code: `qc_lean_cloud_upload`

### Algorithm class methods
- `OnData`: body_statements=1  is_stub=True
- `OnOrderEvent`: body_statements=1  is_stub=True
- `OnEndOfAlgorithm`: body_statements=1  is_stub=True

## Blocker summary
The committed P3 runner (main.py at 6330c2e1f81bcbda...) is BUILD-only scaffolding: its OnData/OnOrderEvent/OnEndOfAlgorithm are stubs that return immediately, it has no databento import (cannot decode the local DBN cache), and no standalone main() / if __name__=='__main__' entry point. Per the runner's own inline comment at line ~452, 'the real wiring is QC-runtime-specific and verified during P4 smoke or P6 in-sample.' P4 smoke ran the helpers against synthetic CSV fixtures (passing); P6 in-sample against real DBN bars requires either (a) QC LEAN Cloud upload OR (b) a local DBN-reader + bar-loop driver added to the runner harness. BOTH paths are forbidden by the P6 authorization scope:

### Forbidden paths under P6 scope
- (a) QC LEAN Cloud upload -- forbidden by 'No QuantConnect call' boundary
- (b) Adding a local DBN-reader + bar-loop driver -- forbidden by 'Do not modify strategy code unless the run fails and a separate patch authorization is given'

### What a capable runner would need
- Import `databento` or a python-dbn decoder
- A standalone entry point (`if __name__ == '__main__':` or a `def main()`)
- A bar-loop orchestrator that loads .dbn.zst per root per month, derives daily RTH bars per market, and invokes the existing helpers (wilder_atr, donchian_high/low, PyramidManager, PortfolioCapTracker, compute_unit_contracts)
- A non-stub OnData OR a local-engine driver that bypasses QC
- Diagnostic emission per Phase-2 C6 schema with cost-stress matrix S0..S4 and verdict per C7

## Failure-rule invocation
Per operator's explicit P6 authorization: 'If the runner fails due to code/data decode/path issues, stop and report the failure. Do not patch code unless separately authorized.' Runner cannot consume DBN files = code/data path issue = failure rule fires. This report is the 'stop and report' artifact. No code patched.

- `code_patched_in_response_to_failure`: **False**
- `strategy_code_modified`:              **False**
- `runner_harness_files_modified`:       **False**
- `any_committed_file_modified`:         **False**

## K-criteria / A-gates / verdict
- K1-K12: `NOT_EVALUATED_RUNNER_DID_NOT_EXECUTE`
- A1-A10: `NOT_EVALUATED_RUNNER_DID_NOT_EXECUTE`
- Verdict: `VERDICT_NOT_APPLICABLE_RUNNER_DID_NOT_EXECUTE`

> K1..K12 require closed-trade telemetry from a real strategy execution. The runner did NOT execute. Reporting any K-result would be dishonest (e.g. reporting K9 INSUFFICIENT_SAMPLE from 0 trades when no strategy logic was invoked would be a FALSE FIRE).

## Operator next-step options
### OPT_A -- Authorize P3.5 patch turn -- add local DBN driver

Operator authorizes a fresh, narrowly-scoped patch turn that adds (under external_research_hunter/s7_d1_cross_asset_donchian_runner_harness/) a new in_sample_driver.py that imports databento, loads the cached .dbn.zst files, decodes to RTH daily bars per market, runs the locked Donchian-55/exit-20/2N-stop/4-unit-0.5N-pyramid/1pct-portfolio-sizing strategy via the existing helpers, applies the cost-stress matrix S0..S4, and emits the C6 diagnostic. The new file is added to the BUILD scope under a fresh build_report (s7_d1_..._in_sample_driver_build_report). After the patch is committed, operator re-authorizes P6 in-sample run against the driver.

**Implications:** Extends the chain. Adds one file to the runner harness (in_sample_driver.py) and one BUILD report. Does NOT touch the existing committed runner files. Preserves all locked strategy parameters byte-equivalent.

**Boundaries required in patch authorization:**
- ONLY in_sample_driver.py + its build report may be created
- Driver MUST consume local DBN cache only -- no Databento fetch, no network
- Driver MUST NOT modify main.py, execution_guard.py, or any other committed runner file
- Driver MUST inherit AMB6 filter NONE invariant
- Driver MUST inherit 1pct portfolio sizing + 4-unit pyramid + 0.5N spacing + 2N stop byte-equivalent
- Driver MUST inherit s6 cap-bugfix (PortfolioCapTracker.update_market_units passes pyr.current_unit_count)
- Driver MUST NOT loosen any K threshold
- Driver MUST emit C6 diagnostic via LESSON_HUNTER_004 canonical roundtrip

### OPT_B -- Authorize operator-side QC LEAN Cloud submit

Operator authorizes a separately-scoped QC LEAN Cloud submit turn. The committed main.py is uploaded to QC Cloud (operator's account) and run there. Claude does not call QC; operator runs the submit. Result diagnostic is downloaded by operator, then ingested into a sealed P6 result report on a subsequent turn.

**Implications:** Keeps the committed runner unchanged (no code patch). Routes the in-sample run through QC's runtime where OnData is invoked per-bar. Cost: QC Cloud compute units. Operator-managed; Claude is not in the call path.

**Boundaries required in QC authorization:**
- Operator authorizes QC Cloud submit as a separate turn
- Claude does not call QC at any point
- QC submit limited to in-sample window 2013-01-01 to 2022-12-30
- OOS inspection blocked until in-sample passes

### OPT_C -- Park s7-d1 chain pending strategy on what runner is

Operator declines OPT_A and OPT_B. The s7-d1 chain stops at T1_T15_SYNTHETIC_SMOKE_PASS. The candidate is parked as PARKED_BLOCKED_AT_P6_IN_SAMPLE_RUNNER_NOT_EXECUTABLE pending a separate decision.

**Implications:** Preserves all sealed artifacts. No further work on s7-d1 until operator re-engages. All 6 sealed artifacts remain byte-stable; this blocked report joins them as the final entry in the chain unless OPT_A or OPT_B is later authorized.


## Negative invariants (this turn -- all True)
- `no_runner_invoked`: `True`
- `no_strategy_code_modified`: `True`
- `no_runner_harness_file_modified`: `True`
- `no_committed_file_modified`: `True`
- `no_in_sample_run_completed`: `True`
- `no_oos_inspection`: `True`
- `no_databento_call`: `True`
- `no_databento_fetch`: `True`
- `no_qc_call`: `True`
- `no_qc_cloud_submit`: `True`
- `no_network_call`: `True`
- `no_broker_or_exchange_adapter_imported`: `True`
- `no_live_trading`: `True`
- `no_paper_bot_change`: `True`
- `no_obsidian_trade_logger_mutation`: `True`
- `no_review_queue_mutation`: `True`
- `no_d5_revived`: `True`
- `no_b005_001_revived`: `True`
- `no_nke_revived`: `True`
- `no_threshold_loosened`: `True`
- `amb6_filter_none_invariant_preserved`: `True`
- `no_profitability_claim`: `True`
- `no_promotion_to_live`: `True`
- `no_committed_artifact_seal_mutated`: `True`

## Operator-side state
- `obsidian_trade_logger_unchanged_through_p6`: **True**

## Seal block (canonical)
- **`report_seal_sha256`**: `f0f465d4c9b9199c4a45c060b8ff2552368128c5086354307394d2f8999fccf0`
- **`seal_method`**: `sha256 over json.dumps(obj, sort_keys=True, separators=(',',':'), ensure_ascii=False, default=str) EXCLUDING report_seal_sha256 + seal_method`
- **`schema_id`**: `sparta.external_research_hunter.s7_d1_cross_asset_donchian_in_sample_blocked_report.v1`
- **`schema_status`**: `SEALED`
- **`report_date_utc`**: `2026-05-25T18:48:13Z`

*End of report. No code patched. No runner invoked. No data fetched. No backtest run.*
