# S12-D1 P4 SMOKE Report (SEALED)

**Schema:** `sparta.s12.d1.mnq_c0.donchian_15_8.smoke_t1_t15_report.v1`
**Phase:** `S12_D1_P4_SMOKE`
**Phase prefix:** `PHASE2-S12-D1-P4`
**Controller session:** THIS_SESSION_ONLY
**Sealed at (UTC):** `2026-05-27T15:55:00Z`
**Authorization:** *"Authorize s12 D1 P4 SMOKE only."*

**Candidate:** `s12-d1-mnq-c0-single-instrument-donchian-15-8-databento-long-history`

---

## 0. Verdict: **`P4_SMOKE_PASS`**

- T1–T15 re-executed against the committed runner harness from P3 BUILD
- **15/15 PASSED** in 0.02s wall clock (faster than P3 BUILD's 0.07s; same outcome)
- Zero failures; zero errors
- All test durations < 5 ms (per pytest `--durations=15`)
- Deterministic verdict confirmed across two independent runs (P3 BUILD + P4 SMOKE)

---

## 1. Predecessor anchors (byte-stable at HEAD)

| Phase | Commit | Seal (first 16) |
|---|---|---|
| **P3 BUILD** | `b97331a` | `8c6ec346029ae8a9` |
| P2 phase-2 plan | `2b27acc2` | `0bcfe99ca1dc1010` |
| P1 plan-lock | `bd7245e` | `f19a7a4c9967cefb` |
| Sealed Tier-N spec | `9ce4d66` | `422bbbff75f24816` |
| DRAFT review | `07be7fc` | `860e766e6933751d` |
| Audit-clean MNQ.c.0 CSV | — | `8b7b832c62fae185` |

All anchors bit-identical at HEAD.

---

## 2. Runner harness files under test (byte-stable since P3 BUILD)

| File | sha256 (first 16) |
|---|---|
| `__init__.py` | `09bffa5995b18706` |
| `runner_main.py` | `25b0aaf7e29a360a` |
| `execution_guard.py` | `48d35501d66df5e1` |
| `in_sample_driver.py` | `88ac42ff8b611212` |
| `out_of_sample_driver.py` | `c0ebf7b93da6133c` |
| `main.py` | `992159e97ebe3c47` |
| `tests/.../test_smoke_t1_t15.py` | `7e731404c2924ce5` |

---

## 3. Smoke battery T1-T15 result: **15/15 PASS** (0.02s)

| Test | Outcome |
|---|---|
| T1 Donchian-15 entry long breakout (uptrend) | **PASS** |
| T2 Donchian-15 entry short breakout (downtrend) | **PASS** |
| T3 Donchian-8 exit long on reversal | **PASS** |
| T4 Wilder ATR(20) on known series | **PASS** |
| T5 ATR 2N stop placement | **PASS** |
| T6 Position sizing 1% on $100k (5 units at ATR=50) | **PASS** |
| T7 No-pyramid invariant: ExecutionGuard raises on 2nd open | **PASS** |
| T8 Cost-tier S0 zero commission + zero slippage | **PASS** |
| T9 Cost-tier S1 baseline ($0.74 / $0.36 / 1-1-1 ticks) | **PASS** |
| T10 Cost-tier S4 extreme (3× scalars) | **PASS** |
| T11 WARMUP_DAYS = 220 invariant (raises within warmup) | **PASS** |
| T12 RTH window 09:30-16:00 ET locked | **PASS** |
| T13 K4 max-drawdown threshold ($50k abs) tracking | **PASS** |
| T14 CSV sha + rowcount integrity | **PASS** |
| T15 IS/OOS window no-leakage | **PASS** |

pytest invoked with `--rootdir=tests/.../runner_harness/` to constrain collection (same tooling workaround as P3 BUILD; pre-existing repo-root path with unicode private-use-area character breaks default rootdir scan).

---

## 4. Comparison vs P3 BUILD smoke run

| Run | Verdict | Wall clock |
|---|---|---|
| P3 BUILD (`b97331a`) | 15/15 PASS | 0.07s |
| **P4 SMOKE** (this) | **15/15 PASS** | **0.02s** |

Identical verdicts confirm test determinism. P4 is faster (no `--durations` overhead per test compared to P3 BUILD's verbose mode; but both fully deterministic).

---

## 5. Audit-clean CSV attestation (T14)

| Field | Value |
|---|---|
| Path | `data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_1d_2019-05-13_2025-12-30.csv` |
| Expected sha256 | `8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e` |
| Expected data rows | 2,066 |
| Verified via T14 at this phase | True |
| CSV NOT modified by P4 SMOKE | True |
| Byte-stable since P3 BUILD | True |
| Verified via both `in_sample_driver.assert_csv_present_and_byte_stable()` and `out_of_sample_driver.assert_csv_present_and_byte_stable()` | True |

---

## 6. IS/OOS separation attestation (T15)

| Field | Value |
|---|---|
| IS window | 2019-05-13 → 2023-12-29 |
| OOS window | 2024-01-02 → 2025-12-30 |
| No overlap | True |
| OOS driver excludes IS dates | True |
| IS driver excludes OOS dates | True |
| Sibling-driver invariant preserved | True |

---

## 7. ExecutionGuard runtime invariants exercised

### T7 No-pyramid (`max_units_per_market = 1`)
- First open unit succeeds
- Second open unit on same symbol raises `GuardViolation` ✓
- Close unit decrements correctly
- Reopen after close succeeds

### T11 WARMUP_DAYS = 220
- `day_index` 0..219 raises `GuardViolation` ✓
- `day_index` 220 and after passes

### T15 Static invariants (composite)
- `assert_all_static_invariants_held()` succeeds (Donchian-15/8, ATR, risk, START_CASH, universe, no-pyramid, K4, WARMUP all locked) ✓

---

## 8. What this SMOKE did NOT do

`run_in_sample` invoked: **No** · `run_out_of_sample` invoked: **No** · Simulator: **No** · Backtest: **No** · Signal compute outside smoke tests: **No** · Data fetch: **No** · Databento call: **No** · API key access: **No** · Orders/brokerage/paper/live: **No** · `review_queue`/`idea_memory`/Strategy Lab: **No** · Cache/data mod: **No** · Predecessor mod (SEAL/P1/P2/P3 BUILD): **No** · Runner harness module mod: **No** · Test file mod: **No** · Parallel chain mod: **No** · `lessons.md` mod: **No** · Branch change/git push: **No** · New strategy code authored: **No**

---

## 9. Parallel-session chain (acknowledged; zero collision)

| Phase | Parallel commit |
|---|---|
| SEAL | `66bbbd15` |
| P1 | `d8bd359` |
| P2 | `0b8d948` |
| P3 BUILD | `91e740e` (16 files) |
| P4 SMOKE | `ea78845c` (29/29 PASS in 0.11s; sealed CSV not touched) |

Parallel chain uses `..._databento_long_history_...` naming. This session's chain uses operator-explicitly-specified shorter `..._single_instrument_donchian_15_8_...` naming. Both coexist at non-colliding paths. Parallel session's P4 used 29 tests (more granular battery); this session's P4 uses the 15-test battery specified in the operator's P2 plan.

---

## 10. V-gates (21 evaluated; all True)

V1 ASCII · V2 keyed sections consistent · V3 no execution language · V4 no self-auth to P6/P10/RUN · V5 no code mod · V6 no backtest · V7 no simulator · V8 no signal compute outside smoke · V9 no fetch · V10 no network IO · V11 no live trading · V12 P3/P2/P1/SEAL byte-stable · V13 exactly 2 new files staged · V14 `lessons.md` unstaged/untouched · V15 DA4=B carried · V16 C1.A + C1.D carried · V17 smoke 15/15 PASS · **V18 runner harness byte-stable since P3 BUILD** · V19 CSV byte-stable via T14 · V20 no Databento / API key at SMOKE · **V21 deterministic verdict consistent across P3 BUILD + P4 SMOKE runs**

---

## 11. Posture

| Field | Value |
|---|---|
| Trading | `PAUSED` |
| Live | `BLOCKED_AT_6_GATES` (permanent) |
| FRC granted | `False` |
| Advisory label permanent | `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` |
| `verdict_never_means_live_ready` | True |
| `live_promotion_path_closed` | True |
| This P4 SMOKE authorizes any RUN | **No** |

---

## 12. Exact next authorized phases (NONE pre-approved)

| Phase | Authorization phrase | Scope |
|---|---|---|
| **P6 IS diagnostic** | `"Authorize s12 D1 P6 IS diagnostic only"` | Invoke `run_in_sample(cost_tier='S1')`; produce sealed IS diagnostic. K9 expected to pass at central/upper trade-density estimates. |
| **Deferral** | `"Defer / Pause s12-d1 track"` | Hold S12-D1 at P4 SMOKE without advancing. |

---

## 13. Labels

`S12_D1_P4_SMOKE_COMPLETE` · `P4_SMOKE_PASS` · `T1_T15_15_15_PASS` · `DETERMINISTIC_VERDICT_CONFIRMED_VS_P3_BUILD_SMOKE` · `RUNNER_HARNESS_BYTE_STABLE_SINCE_P3_BUILD` · `CSV_BYTE_STABLE_VIA_T14` · `IS_OOS_NO_LEAKAGE_VIA_T15` · `EXECUTION_GUARD_INVARIANTS_EXERCISED` · `DA4_B_CARRIED` · `C1_A_C1_D_CARRIED` · `OOS_K9_RISK_WARNING_CARRIED_FORWARD` · `DR1_INCONCLUSIVE_HOLD_FOR_OOS_K9_SUB_THRESHOLD` · `NO_DRIVER_RUN` · `NO_SIMULATOR_RUN` · `NO_BACKTEST` · `NO_DATA_FETCH` · `NO_DATABENTO_CALL` · `NO_DATABENTO_API_KEY_ACCESS` · `NO_REVIEW_QUEUE_MUTATION` · `NO_STRATEGY_LAB_PROMOTION` · `NO_LIVE_TRADING` · `VERDICT_NEVER_MEANS_LIVE_READY`

---

## 14. Seal

```
seal_method = sha256 over json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False) EXCLUDING report_seal_sha256 + seal_method

report_seal_sha256 = <see JSON report_seal_sha256 field>
```

**S12-D1 P4 SMOKE sealed. Verdict: `P4_SMOKE_PASS`. T1-T15 15/15 PASS in 0.02s. Runner harness byte-stable. Trading: PAUSED. Live: BLOCKED_AT_6_GATES. FRC never granted.**
