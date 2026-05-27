# Next Research-Track Selection Plan -- Hygiene Review (SEALED)

**Schema:** `sparta.s9.next_track_selection_plan_hygiene_review.v1`
**Phase:** `S9_NEXT_TRACK_SELECTION_PLAN_HYGIENE_REVIEW`
**Controller session:** THIS_SESSION_ONLY
**Sealed at (UTC):** `2026-05-26T23:58:29Z`

> Hygiene-review-only turn. No reversion. No overwrite. No new
> strategy work. No simulator. No backtest. No signal. No data
> fetch. No vendor calls. No live trading.

---

## 1. Accepted plan

- **Path:** `docs/next_research_track_selection_plan_after_s9_park.md`
- **Commit:** `2ec93304dc4c00edceafaab4bd0bb06501f01290` (short: `2ec9330`)
- **Blob sha256 (at 2ec9330):** `34dba4be675ad766b8d285bca2f5c468bbd600c6e024eeac356080c86af84cfb`
- **Blob bytes (at 2ec9330):** 38,409
- **Blob alignment confirmed:** **True**
- **Authored by:** parallel agent session (same ryahai git identity; distinct conversational context)

### Accepted recommendation

- **Recommendation:** `T8 + T7-Path-A`
- **Description:** Formally park SPY/TLT/GLD/USO 2014-2022 simple canonical mechanics at the family level (T8), AND open a parallel new research track on a structurally different universe via the Databento micro-futures Path A (long-history MNQ+MGC two-market candidate; T7-Path-A; per S10-D1 micro-availability memo).
- **Score:** `46 / 50`
- **Proposed candidate_record_id:** `s10-d1-cross-asset-trend-or-meanrev-mnq-mgc-databento-long-history`

## 2. ASCII hygiene fix

- **ASCII issue observed at 2ec9330 blob:** `True`
- **Non-ASCII count at 2ec9330 blob:** 2 (UTF-8 bytes; 1 codepoint)
- **Codepoint:** `U+00A7 (SECTION SIGN; §)`
- **Byte offsets:** `[21063, 21064]`
- **Context:** *T7. Pivot to a Databento micro-futures track ... Three sub-options inherited from S10-D1 §6: Path A ...*

- **Fix applied:** **True**
- **Method:** `single Edit-tool surgical replacement`
- **Replacement:** `§6 -> section 6`
- **Byte delta:** `+6 bytes (single occurrence)`
- **Meaning preserved:** **True**
  - Replacement preserves the semantic reference to a numbered section of the upstream S10-D1 memo. Reading 'inherited from S10-D1 section 6' is equivalent to 'inherited from S10-D1 §6' for any human or automated reader.

- **Post-fix working-copy sha256:** `ea578e0eb5912f31ee6afabcddf091085160c5b3b213ae22c3c6d3eb0ed985d7`
- **Post-fix bytes:** 38,415
- **Post-fix non-ASCII count:** 0
- **Post-fix ASCII-clean:** **True**
- **`S10-D1 section 6` present exactly once:** **True**

## 3. Parallel-session race condition (documented)

**Summary:** During the hygiene-review turn's drafting phase, a parallel agent session (operating under the same ryahai git identity but in a distinct conversational context) authored and committed its own version of the same plan file at commit 2ec9330 (subject: 'Add next research-track selection plan after s9 park'). The parallel session had visibility into work this controller-session did NOT, specifically the s10_d1_micro_availability_probe_result_memo.md and downstream s10-d1 MNQ+MGC tier-N planning.

**Evidence:**
- git reflog HEAD@{2} shows commit 2ec9330 with the operator-suggested subject line.
- Two follow-up commits from the same parallel session: 2a53b19 (Seal S10 availability attestation analysis) and 5c13821 (Add ETF-proxy family park memo and s10 d1 MNQ MGC plan).
- The 2ec9330 commit contains references to files this controller-session had no prior context for (e.g., reports/external_research_hunter/s10_d1_micro_availability_probe_result_memo.md).
- The 2ec9330 commit's body is single-line ('Add next research-track selection plan after s9 park') matching the operator's suggested commit message, but with no body content -- consistent with the parallel session using `git commit -m "<subject>"` without a here-doc multi-line body.

**This controller-session intended recommendation:** T1 cross-asset rotation on SPY/TLT/GLD/USO (47/50). My draft was overwritten on disk before any of my git commands fired.

**Parallel session actual recommendation (accepted):** T8 + T7-Path-A (46/50). Adopted as source of truth per operator decision.

**Resolution:** Operator accepted the parallel session's committed plan as source of truth in this hygiene-review authorization. This controller-session does NOT revert, overwrite, amend, or supersede the parallel session's commit; it only applies the single ASCII fix and records this race-condition note.

**Process-risk lesson:** Multiple concurrent agent sessions sharing the same git identity, same working tree, and the same active authorization can race on the same file path. Mitigations identified: (a) confirm staged index immediately before commit (this turn caught it after the fact, not in time to prevent the race); (b) check 'git log' shortly before git add to detect concurrent HEAD movement; (c) use per-session scratch paths and finalize-move into canonical paths only at commit time; (d) coordinate authorizations across sessions to prevent overlapping scope. None of these mitigations is enforced by the current protocol; the race remains a known process risk.

**No data loss:** The parallel session's plan content fully covers the operator's required-include checklist (21 sections, all required content categories present) and is more informed than this controller-session's draft because of its visibility into the s10-d1 work.

**Predecessor chain integrity unaffected:** All prior sealed predecessors remain byte-stable: s9 park report (commit 9cf2f56c9fd840846b72745f04dbf83bab59b7c1), s9 IS decision memo (commit 2e9a96dc9a02e64c8a51afaed8b73f8924f859ff), s9 terminal lesson (commit efa3076e530c71d9b3e87fb98e40985d2ece104c), s7 D1 ETF-proxy park (commit a5ac092). Trading remains PAUSED; live remains BLOCKED_AT_6_GATES; FRC never granted.

## 4. Parallel-session follow-up commits (informational)

| Commit | Short | Title | Date |
|---|---|---|---|
| `2a53b19adf00b668e3f263cfbc9f9936e0c5c544` | `2a53b19` | Seal S10 availability attestation analysis | 2026-05-26 18:22:03 -0300 |
| `5c13821b148dfa791acf44f4b784b0a7e941af3b` | `5c13821` | Add ETF-proxy family park memo and s10 d1 MNQ MGC plan | 2026-05-26 18:32:05 -0300 |

## 5. HEAD at hygiene review

- **Commit:** `d6cc4512263792ada4cf146d740a6817a3bb93e3`
- **Subject:** Seal S10-D2 cross-asset Donchian no-pyramid reparam-cap Tier-N spec

## 6. Dirty lessons.md left untouched

- **Status:** dirty in working tree; unstaged; unmodified by this turn
- **`git status --short`:** `M brain_memory/projects/trading_bot/lessons.md`
- **Working-copy sha256:** `cec4b35890305428006e45587617ba159de2c1b392cf1438361cb85271e6c92b`
- **HEAD blob sha256:** `8bcde78cf5391efae42629482d00f237392c47b62647042380381ff29347cf79`
- **Byte-for-byte unchanged by this turn:** **True**
- **Is in staged index:** **False**

## 7. Negative invariants (all True)

- `no_2ec9330_amended`: **True**
- `no_2ec9330_overwritten`: **True**
- `no_2ec9330_reverted`: **True**
- `no_CLAUDE_md_modification`: **True**
- `no_RUNBOOK_modification`: **True**
- `no_b005_artifact_modified`: **True**
- `no_b006_artifact_modified`: **True**
- `no_backtest_run`: **True**
- `no_branch_change`: **True**
- `no_branch_creation`: **True**
- `no_brokerage_connection`: **True**
- `no_candidate_promotion`: **True**
- `no_data_fetch`: **True**
- `no_databento_api_key_accessed`: **True**
- `no_databento_called`: **True**
- `no_docs_decisions_md_modification`: **True**
- `no_frc_granted`: **True**
- `no_git_push`: **True**
- `no_gitignore_modification`: **True**
- `no_lessons_md_modified`: **True**
- `no_lessons_md_staged`: **True**
- `no_live_trading`: **True**
- `no_network_io`: **True**
- `no_oos_inspection`: **True**
- `no_orb_branch_artifact_mutation`: **True**
- `no_paper_order`: **True**
- `no_parallel_session_commit_modified`: **True**
- `no_pipeline_manifest_modification`: **True**
- `no_production_idea_memory_mutation`: **True**
- `no_real_order`: **True**
- `no_review_queue_mutation`: **True**
- `no_s10_artifact_modified`: **True**
- `no_s7_artifact_modified`: **True**
- `no_s9_artifact_modified`: **True**
- `no_signal_computation`: **True**
- `no_simulator_run`: **True**
- `no_step_30_cost_constant_mutation`: **True**
- `no_strategy_code_written`: **True**
- `no_strategy_lab_invoked`: **True**
- `no_strategy_lab_promotion`: **True**
- `no_strategy_module_built`: **True**
- `no_vendor_sdk_imported`: **True**
- `no_yahoo_finance_called`: **True**
- `no_yfinance_called`: **True**

## 8. Labels

- `NEXT_TRACK_SELECTION_PLAN_ACCEPTED_AS_SOURCE_OF_TRUTH`
- `ASCII_HYGIENE_FIXED`
- `PARALLEL_SESSION_RACE_DOCUMENTED`
- `DIRTY_LESSONS_MD_LEFT_UNTOUCHED`
- `S9_ETF_PROXY_CHAIN_TERMINALLY_CLOSED`
- `TRADING_PAUSED`
- `LIVE_BLOCKED_AT_6_GATES`
- `FRC_NEVER_GRANTED`

## 9. Seal verification

```
seal_method = sha256 over json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False) EXCLUDING report_seal_sha256 + seal_method

report_seal_sha256 = <see JSON report_seal_sha256 field>
```

Companion JSON sha256 = recompute sha256 of the JSON bytes on disk.

**Hygiene review sealed. Plan at 2ec9330 accepted as source of truth. Trading: PAUSED. Live: BLOCKED_AT_6_GATES. FRC never granted.**

