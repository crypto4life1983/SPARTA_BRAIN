# T1 RSI MNQ - Terminal Disposition Memo

**Schema:** `sparta.t1.rsi_mnq.terminal_disposition_memo.v1`
**Phase prefix:** `PHASE2-T1-TERMINAL-DISPOSITION`
**Controller session:** THIS SESSION ONLY
**Report kind:** Terminal disposition memo for this session's T1 RSI MNQ track
**Report date (UTC):** 2026-05-27T19:30:00Z
**Authorization:** Authorize T1 terminal disposition memo only.

**Candidate record id:** `t1-rsi-mnq-c0-mean-reversion-2-period-databento-long-history`
**Track name:** T1 RSI MNQ (this session)
**Lifecycle state before this memo:** SEALED_PLUS_ALIGNMENT_REVIEW_PLUS_AUDIT_COMPLETE
**Lifecycle state after this memo:** TERMINAL_DEFER_TO_PARALLEL_CANONICAL_REJECT_FAST_DR10
**Final disposition:** `TERMINAL_DEFER_TO_PARALLEL_CANONICAL_REJECT_FAST_DR10`

This disposition is **terminal** for this session's T1 chain.

---

## 1. T1 chain (this session) - anchors

| Phase | Commit | Seal sha256 |
|---|---|---|
| PLAN seal | `729207f` | `70549a9ac2c15f36...` |
| DRAFT | `fb1079a` | (no seal) |
| SEAL canonical | `d7fc7f5` | `abe9718d2f7f89db...` |
| Alignment review | `c6bf9ae` | `bfd8d23ed3483c0a...` |
| P6.5 reproducibility audit | `54873eb` | `ff9155f63664c4f4...` |

T1 chain phases executed: **0** of 10 (P1, P2, P3 BUILD, P4 SMOKE, P6 IS, P6.5, P7, P10, P10.5, P11 - **none executed**).

T1 chain progression is **review-and-verification only**, per Option C in alignment review at `c6bf9ae`.

---

## 2. Parallel s13-d1 chain - canonical execution chain for this candidate

| Phase | Commit | Status |
|---|---|---|
| SEAL | `262491c` | seal sha256 `2f9d1763...` |
| P1 plan-lock | `005cb8a` | LOCKED |
| P2 phase-2 plan | `beecd87` | PUBLISHED |
| P3 BUILD | `24625c6` | BUILT |
| P4 SMOKE | `c44fb13` | PASSED |
| P6 IS diagnostic | `3fa479a` | `READY_FOR_LONGER_BACKTEST` (159 closed_trades; sharpe +0.1076; expectancy +$540.73; maxdd 17.68%) |
| P6.5 cost-stress | `15c4fb1e` | **`REJECT_FAST`** (DR10 branch-a `annual_turnover` = 84.7851 vs 0.50 threshold = **169.6x over**) |
| P7 decision memo | `cc1817bf` | TERMINAL per SEAL `fail_safety_outcomes_terminal_for_this_candidate_record_id=True` |

s13-d1 is the **canonical execution chain** for this candidate record id. Its lifecycle is structurally closed.

---

## 3. Relationship of T1 to parallel s13-d1

Per the alignment review at commit `c6bf9ae`:

- **T1 and s13-d1 are materially the same candidate.**
- 25 of 25 substantive parameters are IDENTICAL.
- Cosmetic differences only (candidate-id naming, file paths, DA-register layout).
- Both chains carry the same: RSI(2) bi-directional mean-reversion; MNQ.c.0; 0.5% per-trade risk; $200k cash; 50% K4 maxdd; 220-bar WARMUP; RTH 09:30-16:00 ET; cost tiers S0-S4; IS 2019-05-13 -> 2023-12-29; OOS 2024-01-02 -> 2025-12-30; audit-clean MNQ.c.0 CSV (sha `8b7b832c62fae185...`); K9 threshold 100; OOS-K9-sub-threshold disposition DR1 INCONCLUSIVE_HOLD.

Per the P6.5 reproducibility audit at commit `54873eb`:

- T1 audit corroborated parallel s13-d1 P6.5 verdict.
- Strength: **HIGH**.
- S1 byte-reproduces P6 IS sealed metrics across all 6 measured fields.
- DR10 `annual_turnover` 84.7851 vs 0.50 threshold = 169.6x over - **arithmetically decisive**.

T1 serves as an independent **review/verification lane** only. Both chains converge on the DR10 `REJECT_FAST` verdict via different methodologies (parallel ran the simulator; this session audited methodology + arithmetic + provenance read-only).

---

## 4. Why T1 should not continue independently

**Primary reason:** Substantive parameters of T1 and parallel s13-d1 are IDENTICAL. Executing T1 P1 through P6.5 would produce byte-equivalent verdict to parallel (`REJECT_FAST` on DR10 `annual_turnover`).

**Supporting reasons:**

1. Parallel s13-d1 has reached P7 decision memo (lifecycle TERMINAL).
2. T1 chain advancement under Option C (alignment review at `c6bf9ae`) does NOT include independent execution; the advancement plan specified review/verification only.
3. T1 P6.5 audit at `54873eb` already CORROBORATED the DR10 finding read-only with HIGH strength. Further verification would not change the substantive verdict.
4. DR10 firing on `annual_turnover` branch (84.7851 vs 0.50 threshold; 169.6x over) is mathematically decisive; no reasonable implementation variation could move the ratio below threshold.
5. T1 chain advancement would consume multiple subsequent operator authorizations (P1, P2, P3 BUILD, P4 SMOKE, P6 IS, P6.5) for negligible new information beyond the audit's corroboration.

This reasoning is **terminal** for T1 independent advancement.

---

## 5. Why s13-d1 is canonical execution chain

**Primary reason:** Parallel session executed s13-d1 from PLAN through P7 decision memo on the same audit-clean CSV with documented methodology, byte-verified pre-auth drafts, and chain-of-custody preserved across 6+ predecessor anchors.

**Supporting reasons:**

1. s13-d1 P6 IS produced READY_FOR_LONGER_BACKTEST with 159 closed_trades (clears K9 by 1.59x).
2. s13-d1 P6.5 fired DR10 RF1 -> REJECT_FAST.
3. s13-d1 P7 decision memo formalized REJECT_FAST as TERMINAL per SEAL `fail_safety_outcomes_terminal_for_this_candidate_record_id=True`.
4. Resolution of DR10 firing is FORBIDDEN post-seal per `no_dr_redefinition_post_seal` invariant; s13-d1 lifecycle is structurally closed.
5. Parallel chain is presumed to advance to P11 PARK next, completing the s13-d1 lifecycle archive.

---

## 6. Why RSI(2) solved K9 but failed DR10

### K9 solved at IS

| Field | Value |
|---|---|
| K9 threshold | 100 closed_trades over IS window |
| s13-d1 P6 IS closed_trades | **159** |
| IS window | 4.6297 years |
| K9 clearance ratio | 1.59x |
| K9 status at IS | **CLEARS WITH MARGIN** |

### K9 borderline at OOS (proportional)

| Field | Value |
|---|---|
| OOS proportional trades at actual IS rate | 68.7 |
| OOS K9 threshold | 100 |
| OOS K9 status | **LIKELY FIRES at proportional scaling** |
| Disposition per DA20=A | DR1 `INCONCLUSIVE_HOLD` (not REJECT_FAST) |

### DR10 fails at P6.5 IS

| Field | Value |
|---|---|
| DR10 branch (a) `annual_turnover` | 84.7851 |
| DR10 branch (a) threshold | 0.50 |
| DR10 branch (a) ratio over | **169.6x** |
| DR10 branch (a) fires | **YES** |
| DR10 branch (b) `s2_cost_drag` | 2.35% |
| DR10 branch (b) threshold | 5.00% |
| DR10 branch (b) fires | NO |

### Structural tension

RSI(2) bi-directional mean-reversion on MNQ.c.0 produces ~34 trades/year on the 4.6y IS window (159 over 4.6297y), which is 4-5x more than s12-d1's Donchian-15/8 mechanic (~7-10/y). This higher signal frequency CLEARED IS K9 (159 > 100 threshold). However, the same higher frequency drove `annual_turnover` to 84.7851 - **169x over the DR10 threshold of 0.50**. The structural tension is: K9 demands MORE trades; DR10 demands LESS turnover. These constraints are in tension for any per-trade-sized strategy on a single instrument over a finite history window.

Solving K9 by increasing signal frequency necessarily increases turnover; if turnover exceeds DR10 threshold, the candidate is rejected on cost-stress regardless of edge survival.

---

## 7. Key evidence

| Metric | Value | Source |
|---|---|---|
| s13-d1 P6 IS verdict | `READY_FOR_LONGER_BACKTEST` | commit `3fa479a` |
| s13-d1 P6 IS closed_trades | 159 | parallel sealed |
| s13-d1 P6 IS sharpe (proxy) | +0.1076 | parallel sealed |
| s13-d1 P6 IS expectancy | +$540.73 | parallel sealed |
| s13-d1 P6 IS maxdd | -17.68% | parallel sealed |
| s13-d1 P6.5 verdict | `REJECT_FAST` | commit `15c4fb1e` |
| s13-d1 P6.5 DR10 fires | YES | parallel sealed |
| s13-d1 P6.5 DR10 branch | `annual_turnover` | parallel sealed |
| s13-d1 P6.5 annual_turnover | 84.7851 | parallel sealed |
| s13-d1 P6.5 annual_turnover threshold | 0.50 | DR10 definition |
| s13-d1 P6.5 ratio over threshold | 169.6x | arithmetic |
| s13-d1 P7 decision | TERMINAL by DR10 | commit `cc1817bf` |
| T1 alignment review verdict | `MATERIALLY_THE_SAME_CANDIDATE` | commit `c6bf9ae` |
| T1 P6.5 audit verdict | **`CORROBORATED (HIGH)`** | commit `54873eb` |
| Cross-chain arithmetic check | All 5 cost tiers verified within rounding | this session audit |
| S1 byte-reproduces P6 IS check | All 6 metrics match | this session audit |

---

## 8. Lesson: higher-frequency RSI solved sample size but created turnover explosion

### Sample size problem (recap)

s12-d1 (Donchian-15/8 MNQ.c.0) parked at P6 IS with `INSUFFICIENT_SAMPLE` (33 closed_trades < K9 threshold 100). Donchian-15/8 was conjectured at PLAN to produce 80-200 IS trades; actual was 33 (well below P2 lower bound).

### Higher-frequency pivot to RSI(2)

s13-d1 / T1 pivoted mechanic family from F1 (Donchian trend) to F3 (RSI mean-reversion), specifically Connors RSI(2) bi-directional. K9-reachability discipline at PLAN/SEAL conjectured 46-68 IS trades/year (210-313 over 4.6y).

### Actual RSI(2) trade density

Parallel s13-d1 P6 IS produced 159 closed_trades over 4.6297y = ~34 trades/year. This is BELOW the K9-reachability PLAN/SEAL lower bound of 46/y, but ABOVE the K9 threshold (159 > 100 over IS window).

### K9 problem solved, turnover explosion problem created

- IS K9 clears with margin (1.59x threshold).
- OOS K9 at proportional scaling (34/y x 2.0y = 68.7) BELOW threshold of 100 (per alignment review revision). Per DA20=A disposition is DR1 `INCONCLUSIVE_HOLD`; not REJECT_FAST.
- Same signal density that solved K9 drove `annual_turnover` to 84.7851 - 169x over DR10 threshold of 0.50.
- DR10 RF1 fires REJECT_FAST regardless of edge survival (DR3 does not fire; all 4 cost tiers retain positive expectancy + net PnL).

### Load-bearing lesson

For single-instrument strategies on multi-year windows, K9 and DR10 thresholds form a **structural tension**. Solving K9 by increasing signal density (faster mechanic) typically pushes turnover ratio above DR10 threshold. The two thresholds need to be **jointly satisfiable**: either DR10 threshold raised at SEAL (DA19=B at T1 DRAFT was offered; not chosen), or mechanic chosen with structurally just-sufficient signal density (above K9, below DR10).

### Arithmetic of the tension

For DR10 threshold 0.50 with $200k equity, max acceptable annual dollar-turnover is $100k/year. With per-trade notional ~$75k (typical for MNQ.c.0 at 0.5% risk), this caps max trades-per-year at ~1.33. K9 requires >=22 trades/year over 4.6y IS. The **22 vs 1.33 trades-per-year gap** is the K9/DR10 structural tension exposed by this candidate.

### Future design implication

Future candidates seeking K9 clearance on single futures instruments must either:

1. Accept DR10 threshold elevation at SEAL via DA19=B (turnover threshold 1.00 or higher).
2. Drastically reduce per-trade notional (e.g., 0.1% risk, single-contract sub-fractional sizing).
3. Use a multi-instrument universe to spread turnover across more equity.
4. Pivot to a different asset class (e.g., cash equities with lower per-trade notional).

---

## 9. Future direction (advisory only; not authorized by this memo)

### Lower-frequency mean-reversion options

| Option | Expected signal density | K9 status est. | DR10 status est. | Rationale |
|---|---|---|---|---|
| RSI-5 bi-directional MNQ.c.0 | ~20-25 trades/year | Borderline | Less likely to fire (turnover ~half) | Modest reduction may bring DR10 into clearance while keeping K9 marginally clearable |
| RSI-7 bi-directional MNQ.c.0 | ~12-18 trades/year | LIKELY FIRES K9 at IS | Likely clears DR10 | Trade-off may swing back to K9 problem; not clean |
| Stochastic-K oscillator MNQ.c.0 | varies | Same K9/DR10 tension | Same K9/DR10 tension | Different signal generator; same structural constraints |
| Longer-period bands (BB-20 / Keltner-20) | ~15-30 trades/year | Borderline | Borderline | Probably similar trade-off zone as RSI-5 |

### Alternative universes

| Option | Note |
|---|---|
| Multi-instrument futures basket (MNQ + MES + MGC) | K9 easier to clear; DR10 calculation per-portfolio needs careful thought |
| Cash-equity universe with sub-fractional sizing | Per-trade notional can be much smaller; reduces turnover ratio. Parallel session's post-s13-d1 selection plan at `30c836ed` explicitly recommended "T1 cash-equity nano-sizing" as primary path; this is substantively different from this session's T1 RSI MNQ. |

### Framework revision options

| Option | Detail |
|---|---|
| DA19=B (DR10 threshold revision at fresh SEAL) | Revise DR10 threshold from 0.50 to 1.00 or higher at fresh candidate's SEAL. Offered at T1 DRAFT but not selected at T1 SEAL. Requires fresh `candidate_record_id`; cannot revise T1 SEAL or s13-d1 SEAL post-seal per `no_dr_redefinition_post_seal`. |
| DR10 framework-level threshold revision | More substantive revision across ALL Tier-N candidates. Requires separate framework-level authorization. Touches structural framework invariants; not in this memo's scope. |

### Pause options

| Option | Detail |
|---|---|
| Defer / Pause T1 track | This terminal disposition memo IS the pause. T1 chain sealed terminal at this commit. |
| Defer / Pause trading-bot track | Pause the entire trading-bot research arc. s12-d1 PARK + s13-d1 REJECT_FAST + this T1 terminal disposition collectively suggest the RSI-2 single-instrument family on the s11-d1 lineage is exhausted; a separate Cooper revision or fresh-track plan would be required. |
| Authorize cross-domain pivot only | Pivot to a different project (Hydra/video, YouTube, affiliate). |

**This memo does NOT authorize any future direction.** All future directions require fresh sealed operator authorization.

---

## 10. No-promotion attestation

- 6-gate live block remains active.
- Permanent live block remains active.
- No promotion to live.
- No promotion to paper.
- No promotion to FRC.
- No promotion to review_queue.
- No promotion to Strategy Lab.
- No promotion to idea_memory.
- No promotion to brokerage.
- **This memo does not grant any promotion pathway.**

---

## 11. Posture invariants

- Trading status: **PAUSED**
- Live status: **BLOCKED_AT_6_GATES**
- FRC granted: **NEVER**
- Advisory label (permanent): **DIAGNOSTIC_ONLY_NOT_LIVE_GRADE**
- Verdict never means live ready: **TRUE**
- Live promotion path closed: **TRUE**
- This memo authorizes any phase: **FALSE**
- This memo authorizes build: **FALSE**
- This memo authorizes run: **FALSE**
- This memo authorizes strategy optimization: **FALSE**

---

## 12. Validation V-gates

V1 ASCII-only. V2 keyed sections consistent. V3 no execution language. V4 no self-authorization to any phase. V5 no code modification. V6 no backtest run. V7 no simulator run. V8 no signal computation. V9 no RSI computation. V10 no data fetch. V11 no network IO. V12 no live trading. V13 T1 chain byte-stable at HEAD. V14 parallel chain not modified. V15 exactly 2 new files staged. V16 lessons.md unstaged and untouched. V17 final disposition enumerated from allowed set. V18 chain of custody to predecessor anchors preserved.

---

## 13. Negative invariants

NO_BUILD. NO_SIMULATOR_RUN. NO_BACKTEST. NO_RSI_COMPUTED. NO_SIGNAL_COMPUTED. NO_DATA_FETCH. NO_DATABENTO_CALL. NO_DATABENTO_API_KEY_ACCESS. NO_EXTERNAL_NETWORK_CALL. NO_REVIEW_QUEUE_MUTATION. NO_IDEA_MEMORY_MUTATION. NO_STRATEGY_LAB_INVOKED. NO_CANDIDATE_PROMOTED. NO_BROKERAGE_CONNECTION. NO_ORDERS_CREATED. NO_PAPER_OR_LIVE_TRADE. NO_T1_CHAIN_MUTATION. NO_PARALLEL_CHAIN_MUTATION. NO_S7/S8/S9/S10/S11/S12_MUTATION. NO_DRIVER_MODIFICATION. NO_DATA_MODIFICATION. NO_CSV_MODIFICATION. NO_TEST_MODIFICATION. NO_DECISIONS_MD_MUTATION. NO_LESSONS_MD_MUTATION. NO_LESSONS_MD_STAGING. NO_LESSONS_MD_COMMIT. NO_BRANCH_CHANGE. NO_GIT_PUSH. NO_FRC_GRANT. NO_LIVE_READINESS_CLAIM. NO_PROFITABILITY_CLAIM. NO_OOS_CONFIRMATION_CLAIM. NO_OOS_INSPECTION. NO_K9_THRESHOLD_RELAXATION_PROPOSED. NO_DR10_THRESHOLD_RELAXATION_VIA_THIS_MEMO. NO_DR_REDEFINITION_POST_SEAL. NO_SELF_AUTHORIZATION_OF_ANY_PHASE. NO_KEY_LEAKAGE.

---

## 14. Labels

`T1_TERMINAL_DISPOSITION_MEMO_COMPLETE`
`T1_DEFERRED_TO_PARALLEL_S13_D1_CANONICAL`
`T1_NOT_CONTINUED_INDEPENDENTLY`
`RSI2_K9_SOLVED_BUT_DR10_FAILED_RECORDED`
`TERMINAL_DEFER_TO_PARALLEL_CANONICAL_REJECT_FAST_DR10`
`T1_CHAIN_TERMINAL_AT_AUDIT`
`S13_D1_CHAIN_CANONICAL_TERMINAL_REJECT_FAST_AT_P6_5`
`K9_DR10_STRUCTURAL_TENSION_RECORDED`
`DR10_TURNOVER_BRANCH_169X_OVER_THRESHOLD`
`PARALLEL_CANONICAL_VERDICT_CORROBORATED`
`CHAIN_OF_CUSTODY_PRESERVED`
`NO_BUILD`
`NO_SIMULATOR_RUN`
`NO_BACKTEST`
`NO_RSI_COMPUTED`
`NO_SIGNAL_COMPUTED`
`NO_DATA_FETCH`
`NO_DATABENTO_CALL`
`NO_DATABENTO_API_KEY_ACCESS`
`NO_REVIEW_QUEUE_MUTATION`
`NO_STRATEGY_LAB_PROMOTION`
`NO_LIVE_TRADING`
`VERDICT_NEVER_MEANS_LIVE_READY`

---

**Seal method:** `sha256 over json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False) EXCLUDING report_seal_sha256 + seal_method`

**Companion JSON:** `t1_rsi_mnq_terminal_disposition_memo.json` (carries the embedded `companion_md_sha256` and the canonical `report_seal_sha256`).
