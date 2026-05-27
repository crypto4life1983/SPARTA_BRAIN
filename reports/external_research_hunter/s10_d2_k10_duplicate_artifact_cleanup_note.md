# S10-D2 K10 Duplicate Artifact Cleanup Note (SEALED)

**Schema:** `sparta.s10.d2.k10_duplicate_artifact_cleanup_note.v1`
**Phase:** `S10_D2_K10_DUPLICATE_ARTIFACT_CLEANUP`
**Controller session:** THIS_SESSION_ONLY
**Sealed at (UTC):** `2026-05-27T03:15:00Z`

## 1. Why this cleanup

Two independent controller sessions executed the S10-D2 K10 pairwise dependence diagnostic in parallel. The parallel session **sealed first** at commit `4ddaa84e42a4623aa54c1d298d0eaa7d24cf0a14` (canonical paths `..._result_sealed.{json,md}` plus evaluator + 24 unit tests; 920 insertions / 4 files).

This controller session's independent run produced an **agreeing verdict** (K10 CLEARS / A7 PASS) at **non-colliding** paths (`..._diagnostic_report.{json,md}`) but was **redundant**.

Per operator invariant *"If parallel-session changes appear during execution, halt and report rather than silently merging scopes,"* this session **HALTED its commit** and the operator authorized **Option 1 — discard the duplicates**. This note records the discard.

## 2. Canonical K10 result (preserved untouched)

- **Commit:** `4ddaa84e42a4623aa54c1d298d0eaa7d24cf0a14`
- **Seal:** `8c620cc5bfe53f71d4ededba45b3d8cee0de54992db6819103875811cbdb99e4`
- **Verdict:** `K10_PASS_AVG_PAIRWISE_CORR_AT_OR_BELOW_0_50`
- **avg_pairwise_corr (canonical):** `+0.052804` (≪ 0.50 threshold)
- **Common IS dates (canonical):** 2253
- **Gap G2 status:** `CLOSED_BY_4DDAA84E`

## 3. Files discarded (only these two, only this session)

| Path | pre-delete sha256 | pre-delete bytes |
|---|---|---|
| `reports/external_research_hunter/s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_k10_pairwise_dependence_diagnostic_report.json` | `01705cf71333fbc370238446921f8dbd472234ebff0a3b43ed03c869a43db290` | 5,017 |
| `reports/external_research_hunter/s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_k10_pairwise_dependence_diagnostic_report.md` | `77405f019ee1639ffef3de6bc2d850dc2b9a25bcbe45971f8306b8d9c9116c8f` | 5,969 |

Both were **unstaged and uncommitted** at the moment of deletion. The diagnostic_report files' aggregate seal (this session's run, never committed) was `8b8f7a6e18cbd68a9e7d111804d46acf73023ede92f62c3eaea79f8d17ff88a6`.

This session's run produced: `avg_pair_dep = +0.040090`, `eff_independent_bets = 3.5706`, common dates = 2251. The +0.0127 delta vs canonical is attributable to a small ordering difference (inner-join vs return-computation sequencing); both share `derive_rth_daily_bars` + simple daily returns + Pearson + unweighted mean of 6 pairs and both clear K10 by ~10× the threshold.

## 4. Canonical K10 file integrity (4/4 intact after CRLF/LF normalization)

| File | LF-normalized sha (first 16) | intact |
|---|---|---|
| `..._result_sealed.json` | `015b3ff061327adc` | True |
| `..._result_sealed.md`   | `a8bd316c3533cbdd` | True |
| `tools/external_research_hunter/s10_d2_k10_pairwise_dependence.py` | `09dcf075634840eb` | True |
| `tests/test_s10_d2_k10_pairwise_dependence.py` | `8184171824aec3c6` | True |

`git diff --quiet HEAD --` reports **CLEAN** for all 4 canonical files. The raw-byte sha differences observed in checkout-time bytes are pure autocrlf line-ending artifacts; the canonical commit content is unmodified.

## 5. Parallel-session activity observed during this authorization

- `4ddaa84e` — `Seal S10-D2 K10 pairwise dependence: PASS (avg=+0.0528, threshold=0.50)`
- `f0b3721`  — `Add native S10-D2 OOS driver support`
- `488579e`  — `Add s11 D1 MNQ.c.0 single-instrument Databento long-history Tier-N spec plan`

Race count for this session: **5**. None of the new commits touched my discard scope.

## 6. Negative invariants (all True)

`no_databento_call` · `no_databento_api_key_access` · `no_data_fetch` · `no_oos_inspection` · `no_oos_computation` · `no_cache_modification` · `no_canonical_k10_evaluator_modification` · `no_canonical_k10_tests_modification` · `no_canonical_k10_result_sealed_modification` · `no_canonical_k10_result_md_modification` · `no_k10_re_run` · `no_simulator_run` · `no_backtest_run` · `no_signal_compute` · `no_strategy_lab_invoked` · `no_candidate_promoted` · `no_brokerage_connection` · `no_paper_or_live_trade` · `no_review_queue_mutation` · `no_idea_memory_mutation` · `no_lessons_md_staged_or_modified` · `no_branch_change` · `no_git_push` · `no_s7_artifact_modified` · `no_s8_d1_artifact_modified` · `no_s9_artifact_modified` · `no_s10_d1_artifact_modified` · `no_orb_artifact_modified` · `no_step_30_cost_constant_modified` · `no_key_leakage` · `only_two_unstaged_duplicate_files_deleted`

## 7. Status

- Trading: `PAUSED`
- Live: `BLOCKED_AT_6_GATES`
- FRC granted: `False`
- Advisory label permanent: `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE`
- Gap G2 status: `CLOSED_BY_4DDAA84E`

## 8. Labels

- `S10_D2_K10_DUPLICATE_ARTIFACTS_DISCARDED`
- `CANONICAL_K10_PASS_AT_4DDAA84E_LEFT_INTACT`
- `GAP_G2_REMAINS_CLOSED`
- `TWO_INDEPENDENT_SESSIONS_AGREED_K10_CLEARS`
- `NO_DATABENTO_CALL`
- `NO_DATABENTO_API_KEY_ACCESS`
- `NO_OOS_COMPUTATION`
- `NO_SIMULATOR_RUN`
- `NO_BACKTEST`
- `NO_REVIEW_QUEUE_MUTATION`
- `NO_STRATEGY_LAB_PROMOTION`
- `NO_LIVE_TRADING`

## 9. Seal

```
seal_method = sha256 over json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False) EXCLUDING report_seal_sha256 + seal_method

report_seal_sha256 = <see JSON report_seal_sha256 field>
```

**Cleanup complete. Canonical K10 PASS sealed at 4ddaa84e remains intact. Trading: PAUSED. Live: BLOCKED_AT_6_GATES. FRC never granted.**
