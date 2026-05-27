# S12-D1 P3 BUILD Report (SEALED)

**Schema:** `sparta.s12.d1.mnq_c0.donchian_15_8.runner_build_report.v1`
**Phase:** `S12_D1_P3_BUILD`
**Phase prefix:** `PHASE2-S12-D1-P3`
**Controller session:** THIS_SESSION_ONLY
**Sealed at (UTC):** `2026-05-27T15:50:00Z`
**Authorization:** *"Authorize s12 D1 P3 BUILD only."*

**Candidate:** `s12-d1-mnq-c0-single-instrument-donchian-15-8-databento-long-history`

---

## 0. Build verdict: **`P3_BUILD_PASS`**

- 6 runner-harness modules authored ✓
- 3 test files authored ✓
- **Smoke battery 15/15 PASS** (0.07s wall clock) ✓
- ExecutionGuard static invariants all held ✓
- Audit-clean MNQ.c.0 CSV byte-equivalent verified (sha + rowcount) ✓
- DA4=B + all other DAs default A carried byte-equivalent ✓
- C1.A + C1.D carried byte-equivalent ✓
- All 20 V-gates True ✓
- Zero parallel-session path collision ✓
- Zero predecessor artifact modification ✓
- Driver entrypoints raise `NotImplementedError` at BUILD time ✓

---

## 1. Predecessor anchors (byte-stable at HEAD)

| Phase | Commit | Seal (first 16) |
|---|---|---|
| Sealed Tier-N spec | `9ce4d66` | `422bbbff75f24816` |
| P1 plan-lock | `bd7245e` | `f19a7a4c9967cefb` |
| P2 phase-2 plan | `2b27acc2` | `0bcfe99ca1dc1010` |
| DRAFT review | `07be7fc` | `860e766e6933751d` |
| Audit-clean MNQ.c.0 CSV (file) | — | `8b7b832c62fae185` |

## 2. Parallel-session chain (acknowledged; not anchored to; zero collision)

| Phase | Parallel commit |
|---|---|
| SEAL | `66bbbd15` (under `..._databento_long_history_..._sealed.json`) |
| P1 | `d8bd359` |
| P2 | `0b8d948` |
| P3 BUILD | `91e740e` (16 files; longer naming prefix `..._databento_long_history_runner_harness/`) |

This session's chain uses operator-explicitly-specified shorter naming under `external_research_hunter/.../runner_harness/` (modules) and `tests/external_research_hunter/.../runner_harness/` (tests). Both chains coexist at distinct paths.

## 3. Files authored at P3 BUILD (11 total)

### 3.1 Runner harness modules (6)

| File | sha256 (first 16) | bytes |
|---|---|---|
| `..._runner_harness/__init__.py` | `09bffa5995b18706` | 1,453 |
| `..._runner_harness/runner_main.py` | `25b0aaf7e29a360a` | 12,545 |
| `..._runner_harness/execution_guard.py` | `48d35501d66df5e1` | 7,284 |
| `..._runner_harness/in_sample_driver.py` | `88ac42ff8b611212` | 8,917 |
| `..._runner_harness/out_of_sample_driver.py` | `c0ebf7b93da6133c` | 7,688 |
| `..._runner_harness/main.py` | `992159e97ebe3c47` | 1,404 |

### 3.2 Test files (3)

| File | sha256 (first 16) | bytes |
|---|---|---|
| `tests/.../__init__.py` | `e0601d44e2a034e8` | 67 |
| `tests/.../conftest.py` | `da144146a99b58e9` | 835 |
| `tests/.../test_smoke_t1_t15.py` | `7e731404c2924ce5` | 15,330 |

### 3.3 Build reports (2)

- `reports/external_research_hunter/s12_d1_..._runner_build_report.json` (this JSON)
- `reports/external_research_hunter/s12_d1_..._runner_build_report.md` (companion)

---

## 4. Smoke battery T1-T15 result: **15/15 PASS** (0.07s)

| Test | Outcome |
|---|---|
| T1 Donchian-15 entry long breakout | **PASS** |
| T2 Donchian-15 entry short breakout | **PASS** |
| T3 Donchian-8 exit long on reversal | **PASS** |
| T4 Wilder ATR(20) on known series | **PASS** |
| T5 ATR 2N stop placement | **PASS** |
| T6 Position sizing 1% on $100k | **PASS** |
| T7 No-pyramid invariant held | **PASS** |
| T8 Cost-tier S0 zero | **PASS** |
| T9 Cost-tier S1 baseline | **PASS** |
| T10 Cost-tier S4 extreme | **PASS** |
| T11 WARMUP_DAYS = 220 invariant | **PASS** |
| T12 RTH window locked | **PASS** |
| T13 K4 max-drawdown threshold | **PASS** |
| T14 CSV row + sha integrity | **PASS** |
| T15 IS/OOS window no-leakage | **PASS** |

pytest was invoked with `--rootdir=tests/external_research_hunter/.../` to constrain collection (a pre-existing path under repo root contains an invalid unicode character that trips pytest's default rootdir scan; the constrained invocation isolates collection to the S12-D1 test directory).

## 5. ExecutionGuard result

| Invariant | Held |
|---|---|
| Donchian-15/8 locked | True |
| Wilder ATR(20), 2N locked | True |
| Per-trade risk 1.0% locked | True |
| START_CASH $100,000 locked | True |
| Universe `{MNQ.c.0}` locked | True |
| No-pyramid + max_units=1 | True |
| K4 50% / $50,000 abs | True |
| WARMUP 220 | True |
| `assert_warmup_passed` raises within warmup, passes after | True |
| `attempt_open_unit` raises on second open same symbol | True |
| `register_close_unit` decrements correctly | True |
| Negative-action sentinels raise on call (live, brokerage, Databento, Strategy Lab) | True |

## 6. Locked strategy parameters (carried byte-equivalent from SEAL)

| Field | Value |
|---|---|
| Donchian entry N | 15 |
| Donchian exit M | 8 |
| ATR period / kind / multiplier | 20 / wilder / 2.0 |
| Per-trade risk | 1.0% |
| max_units_per_market | 1 |
| START_CASH | $100,000 |
| K4 fraction / abs | 0.50 / $50,000 |
| WARMUP_DAYS | 220 |
| RTH | 09:30-16:00 ET America/New_York |
| Tick / $-per-tick (MNQ.c.0) | 0.25 / $0.50 |
| Commission / Fees | $0.74 / $0.36 |
| Slippage e/s/x ticks | 1 / 1 / 1 |
| K9 threshold (IS + OOS) | 100 closed trades |
| Universe | `{MNQ.c.0}` |
| IS window | 2019-05-13 → 2023-12-29 |
| OOS window | 2024-01-02 → 2025-12-30 |
| Cost tiers | S0/S1/S2/S3/S4 (0.0/1.0/1.5/2.0/3.0) |

## 7. What this BUILD did **not** do

`run_in_sample` driver invoked: **No** (raises `NotImplementedError` at BUILD)
`run_out_of_sample` driver invoked: **No** (raises `NotImplementedError` at BUILD)
Simulator run: **No** · Backtest run: **No** · Signal compute outside smoke: **No**
Data fetch: **No** · Databento call: **No** · API key access: **No**
Orders created: **No** · Brokerage connection: **No** · Paper/live trade: **No**
review_queue mutation: **No** · idea_memory mutation: **No** · Strategy Lab: **No**
Candidate promoted: **No** · Cache mod: **No** · Data file mod: **No**
Sealed predecessor mod: **No** · Parallel session chain mod: **No**
`lessons.md` modification: **No** · git push / branch change: **No**

---

## 8. Observations (4; all informational/affirmative; none are defects)

### OBS-1 (informational): CSV filename discrepancy vs sealed-spec reference

The sealed Tier-N spec text referenced `data/.../MNQ_c_0_ohlcv_1d_20190513_20251230.csv`. The actual on-disk file is at `data/.../MNQ_1d_2019-05-13_2025-12-30.csv`. **Content is byte-identical** (sha256 `8b7b832c62fae185...` matches exactly; rowcount 2066 matches). The operative invariant locked at SEAL is the sha256, not the filename. P3 BUILD locks the actual on-disk path in `runner_main.CONFIG['data_csv_path']`. T14 verifies sha + rowcount; both PASS.

### OBS-2 (informational): Pytest rootdir constraint

pytest's default rootdir scan walks up from repo root and trips on a pre-existing path containing a unicode private-use-area character + trailing space (`uf022hydra `). P3 BUILD uses `--rootdir=tests/.../runner_harness/` to constrain collection. Tooling workaround; not a strategy change. Smoke battery 15/15 PASS under the constraint.

### OBS-3 (informational): Tests path differs slightly from P2 plan

P2 tentatively located tests at `external_research_hunter/.../runner_harness/tests/`. The operator's P3 BUILD authorization explicitly specifies tests at `tests/external_research_hunter/.../runner_harness/`. P3 BUILD follows the operator's explicit P3 authorization path (sibling `tests/` tree).

### OBS-4 (affirmative): Sibling driver design preserves IS byte-stability

In-sample and out-of-sample drivers are siblings (each hard-codes its own window constants). OOS driver structurally cannot inspect IS data and vice versa. T15 verifies this. Pattern carried from s10-D2 P3.6 BUILD lineage.

---

## 9. V-gates (all True)

V1 ASCII · V2 keyed sections consistent · V3 no execution language in drivers · V4 no self-auth to P4 SMOKE / P6 / P10 · V5 no code mod outside P3 outputs · V6 no backtest · V7 no simulator · V8 no signal compute outside smoke synthetic fixtures · V9 no data fetch · V10 no network IO · V11 no live trading · V12 P2/P1/SEAL byte-stable · V13 exactly 11 files staged · V14 `lessons.md` unstaged/untouched · V15 DA4=B carried · V16 C1.A + C1.D carried · V17 smoke battery 15/15 PASS · V18 ExecutionGuard static invariants held · V19 CSV sha + rowcount byte-equivalent · V20 no Databento / API key at BUILD

---

## 10. Posture

| Field | Value |
|---|---|
| Trading | `PAUSED` |
| Live | `BLOCKED_AT_6_GATES` (permanent) |
| FRC granted | `False` |
| Advisory label permanent | `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` |
| `verdict_never_means_live_ready` | True |
| `live_promotion_path_closed` | True |
| This P3 BUILD authorizes any RUN | **No** |

---

## 11. Exact next authorized phases (NONE pre-approved)

| Phase | Authorization phrase | Scope |
|---|---|---|
| **P4 SMOKE** | `"Authorize s12 D1 P4 SMOKE only"` | Re-execute T1-T15 + author P4 SMOKE report. No driver run; tests only. |
| **P6 IS diagnostic** | `"Authorize s12 D1 P6 IS diagnostic only"` | Invoke `run_in_sample(cost_tier='S1')`; produce sealed IS diagnostic. |
| **Deferral** | `"Defer / Pause s12-d1 track"` | Hold S12-D1 at P3 BUILD without advancing. |

---

## 12. Labels

`S12_D1_P3_BUILD_COMPLETE` · `RUNNER_HARNESS_BUILT` · `T1_T15_SMOKE_PASS` · `EXECUTION_GUARD_PASS` · `DRIVER_BYTE_STABLE_AT_BUILD` · `SIBLING_DRIVER_DESIGN` · `AUDIT_CLEAN_CSV_BYTE_VERIFIED` · `DA4_B_CARRIED` · `C1_A_C1_D_CARRIED` · `OOS_K9_RISK_WARNING_CARRIED_FORWARD` · `DR1_INCONCLUSIVE_HOLD_FOR_OOS_K9_SUB_THRESHOLD` · `NO_IS_DIAGNOSTIC_RUN` · `NO_OOS_DIAGNOSTIC_RUN` · `NO_SIMULATOR_RUN` · `NO_BACKTEST` · `NO_SIGNAL_COMPUTED_OUTSIDE_SMOKE_TESTS` · `NO_DATA_FETCH` · `NO_DATABENTO_CALL` · `NO_DATABENTO_API_KEY_ACCESS` · `NO_REVIEW_QUEUE_MUTATION` · `NO_STRATEGY_LAB_PROMOTION` · `NO_LIVE_TRADING` · `VERDICT_NEVER_MEANS_LIVE_READY`

---

## 13. Seal

```
seal_method = sha256 over json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False) EXCLUDING report_seal_sha256 + seal_method

report_seal_sha256 = <see JSON report_seal_sha256 field>
```

**S12-D1 P3 BUILD sealed. Verdict: P3_BUILD_PASS. Smoke battery 15/15 PASS. No execution. Trading: PAUSED. Live: BLOCKED_AT_6_GATES. FRC never granted.**
