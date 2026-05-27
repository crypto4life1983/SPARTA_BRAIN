# S12-D1 P2 Phase-2 Plan (SEALED)

**Schema:** `sparta.s12.d1.mnq_c0.donchian_15_8.p2_phase_2_plan.v1`
**Phase:** `S12_D1_P2_PHASE_2_PLAN`
**Phase prefix:** `PHASE2-S12-D1-P2`
**Controller session:** THIS_SESSION_ONLY
**Sealed at (UTC):** `2026-05-27T15:25:00Z`
**Authorization:** *"Authorize s12 D1 P2 phase-2 plan only."*

**Candidate:** `s12-d1-mnq-c0-single-instrument-donchian-15-8-databento-long-history`

---

## 0. Anchors

| Anchor | Commit | Seal / sha (first 16) | Bit-identical at HEAD |
|---|---|---|---|
| **P1 plan-lock** | `bd7245ee3906e04c` | `f19a7a4c9967cefb` | True |
| **Sealed Tier-N spec** | `9ce4d66e687943da` | `422bbbff75f24816` | True |
| Source DRAFT | `7e9c8679` | `9f09ec94028659eb` | True |
| Draft review | `07be7fc` | `860e766e6933751d` | True |
| Audit-clean MNQ.c.0 CSV | (data file) | `8b7b832c62fae185` | (preserved) |

This P2 anchors to **this session's** P1 (`bd7245e`) and SEAL (`9ce4d66`). The parallel session maintains a distinct S12-D1 chain (SEAL `66bbbd1` → P1 `d8bd359` → P2 `0b8d948`) at non-colliding paths; that chain is acknowledged for awareness and **not anchored or modified**.

---

## 1. Implementation / build boundaries for future P3

P2 defines what future P3 BUILD may produce. **P3 BUILD requires a separate fresh operator authorization block.** P3 BUILD is implementation only; it does **NOT** run anything.

### 1.1 P3 BUILD scope allowed

- Author runner harness modules + unit tests
- Author P3 BUILD report
- Author smoke battery unit tests
- Verify the unit-test smoke battery passes locally during BUILD
- Register runner harness in module path
- Author `__init__.py` files

### 1.2 P3 BUILD scope FORBIDDEN

- No simulator run, no backtest run, no signal compute outside unit-test fixtures
- No data fetch, no Databento call, no `DATABENTO_API_KEY` access, no external network call
- No cache modification, no data modification
- No strategy logic change from SEAL (lookbacks, ATR window, START_CASH, per-trade risk, max units, no-pyramid invariant all carry byte-equivalent)
- No universe widening, no pyramid introduction
- No Strategy Lab invocation, no review_queue mutation, no idea_memory mutation
- No brokerage connection, no orders created, no paper/live trade
- No `lessons.md` modification
- No sealed predecessor artifact modification
- No runbook / pipeline_manifest / decisions.md / .gitignore / CLAUDE.md modification
- No branch change, no git push
- No self-authorization of P4 SMOKE / P5 / RUN

---

## 2. Data-reuse plan

| Field | Value |
|---|---|
| **Data source strategy** | **REUSE_AUDIT_CLEAN_MNQ_C0_CSV_FROM_S10_D1_BYTE_EQUIVALENT** |
| CSV path | `data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_c_0_ohlcv_1d_20190513_20251230.csv` |
| CSV sha256 | `8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e` |
| CSV rows | 2,066 |
| CSV date range | 2019-05-13 → 2025-12-29 |
| **New Databento fetch at any phase** | **False** |
| Databento API key required | **False** |
| Controller-side Databento call at any phase | **LOCKED_OFF** |
| Step 02b for this candidate | manifest cross-link only; no fresh fetch |

**Cache strategy.** Since the audit-clean CSV from S10-D1 is the source of truth, P3 BUILD may either (a) read CSV directly and bypass binary cache entirely, or (b) author lightweight intermediate cache files derived from the CSV at build time. Either approach satisfies `no_new_databento_fetch` and `no_databento_api_key_access`. IS cache and OOS cache are planned at separate paths (`data/databento_cache_s12_d1_is/` and `data/databento_cache_s12_d1_oos/`) for runtime isolation.

---

## 3. Runner / build output path plan

### 3.1 Runner harness directory + modules

`external_research_hunter/s12_d1_mnq_c0_single_instrument_donchian_15_8_runner_harness/`

| Module | Path |
|---|---|
| `runner_main.py` | `..._runner_harness/runner_main.py` |
| `in_sample_driver.py` | `..._runner_harness/in_sample_driver.py` |
| `out_of_sample_driver.py` | `..._runner_harness/out_of_sample_driver.py` |
| `__init__.py` | `..._runner_harness/__init__.py` |
| `execution_guard.py` | `..._runner_harness/execution_guard.py` |
| `main.py` | `..._runner_harness/main.py` |

### 3.2 Tests directory + files

`external_research_hunter/s12_d1_mnq_c0_single_instrument_donchian_15_8_runner_harness/tests/`

| Test file | Path |
|---|---|
| Smoke battery | `..._runner_harness/tests/test_smoke_t1_t15.py` |
| `conftest.py` | `..._runner_harness/tests/conftest.py` |
| `__init__.py` | `..._runner_harness/tests/__init__.py` |

### 3.3 Build reports + future diagnostic outputs

- `reports/external_research_hunter/s12_d1_..._runner_build_report.{json,md}`
- `reports/external_research_hunter/s12_d1_..._in_sample_driver_build_report.{json,md}`
- `reports/external_research_hunter/s12_d1_..._out_of_sample_driver_build_report.{json,md}`
- `reports/external_research_hunter/s12_d1_..._smoke_t1_t15_report.{json,md}`
- `reports/external_research_hunter/s12_d1_..._in_sample_diagnostic_result_sealed.{json,md}` (later, post-P6 IS run)
- `reports/external_research_hunter/s12_d1_..._out_of_sample_diagnostic_result_sealed.{json,md}` (later, post-P10 OOS run)

Path-collision avoidance: this session's paths use the shorter naming under `reports/external_research_hunter/`. The parallel chain uses the longer `..._databento_long_history_...` naming. Both chains coexist at distinct paths.

---

## 4. Expected tests / smoke battery plan

P3 BUILD authors 15 unit tests (T1–T15). 15/15 must PASS before P3 BUILD verdict can be PASS. P4 SMOKE phase (separate future authorization) will re-execute the battery as part of formal smoke.

| Test | Acceptance |
|---|---|
| T1 | Donchian-15/8 entry signal correctly detected on synthetic uptrend fixture |
| T2 | Donchian-15/8 entry signal correctly detected on synthetic downtrend fixture (short-side) |
| T3 | Donchian exit signal correctly detected on synthetic reversal fixture |
| T4 | Wilder ATR(20) computes correctly on known reference series |
| T5 | ATR 2N stop placement correctly distanced from entry |
| T6 | Position sizing computes correctly at 1% risk on $100k starting cash |
| T7 | `max_units_per_market = 1` invariant holds under multiple successive signals (no pyramid) |
| T8 | Cost-stress S0 produces zero commission + zero slippage path |
| T9 | Cost-stress S1 baseline retail commission $0.74 + fees $0.36 + slippage 1 tick applied correctly |
| T10 | Cost-stress S4 extreme adversarial (3× scalars) applied correctly |
| T11 | `WARMUP_DAYS = 220` invariant: no order submission within first 220 days |
| T12 | RTH window 09:30-16:00 ET correctly filters bar timestamps |
| T13 | K4 max-drawdown threshold ($50,000 = 50% of $100k) correctly tracked |
| T14 | Audit-clean MNQ.c.0 CSV loads with correct row count (2,066) and sha256 match |
| T15 | IS / OOS window boundaries correctly enforced (no leakage between phases) |

**P3 BUILD must author + execute these 15 unit tests.** Execution of unit tests during BUILD does **NOT** constitute signal compute or backtest — it is build-time verification only.

---

## 5. Cost-stress tiers plan

5-tier matrix locked at SEAL (carried byte-equivalent from s11-d1 v1):

| Tier | cost_scalar | slippage_scalar |
|---|---:|---:|
| S0 | 0.0 | 0.0 |
| S1 | 1.0 | 1.0 |
| S2 | 1.5 | 1.5 |
| S3 | 2.0 | 2.0 |
| S4 | 3.0 | 3.0 |

Commission $0.74 / Fees $0.36 / Slippage 1-1-1 ticks. MNQ.c.0 tick 0.25 / $0.50.

**P3 BUILD authors cost-tier implementation; P3 BUILD does NOT run cost-stress sweep.** IS cost-stress runs at future P6 (separate authorization). OOS cost-stress runs at future P10.5 (separate authorization). Cost-stress threshold changes post-P2 are FORBIDDEN per `no_dr_redefinition_post_seal`.

---

## 6. IS / OOS separation plan

| Field | Value |
|---|---|
| IS window (locked) | 2019-05-13 → 2023-12-29 (~4.6y) |
| OOS window (locked) | 2024-01-02 → 2025-12-30 (~2y) |
| IS / OOS strict separation | **Required** |
| OOS inspection at IS phase | **FORBIDDEN** |
| `oos_inspection_blocked_at_in_sample` invariant | Active |

**Sibling-driver design recommended for P3** (analogous to s10-D2 P3.6 BUILD pattern):
- Author `in_sample_driver.py` and `out_of_sample_driver.py` as siblings
- Each driver hard-codes its window constants
- OOS driver structurally cannot inspect IS data and vice versa
- IS cache and OOS cache live at separate directory paths at runtime

P3 BUILD authors both drivers but does NOT invoke them. P3 BUILD verifies each driver imports cleanly and that driver byte-stability invariants are enforced by unit tests.

---

## 7. OOS K9 risk warning at P2 (carried byte-equivalent from SEAL + P1)

| Estimate | IS trades (4.6y) | × (2.0/4.6) | OOS expected (2y) |
|---|---|---|---|
| Lower | 80 | 0.435 | **35** |
| Central | 140 | 0.435 | **61** |
| Upper | 200 | 0.435 | **87** |

**All three OOS proportional-scaling estimates below K9 = 100.**

- **C1.A** carried byte-equivalent: OOS K9 may fire; this is the structural test of the fresh-candidate hypothesis, not a defect.
- **C1.D** carried byte-equivalent: OOS K9 sub-threshold maps to DR1 `INCONCLUSIVE_HOLD` (NOT REJECT_FAST). DR1 extended at SEAL to cover `oos_closed_trades < K9_threshold`.

P3 BUILD will author K9 evaluation logic that fires at IS phase if `closed_trades < 100`; for OOS, sub-threshold maps to DR1 `INCONCLUSIVE_HOLD` per C1.D. **P3 BUILD does NOT alter K9 threshold or DR1 disposition.**

---

## 8. Locked invariants — no live / no Strategy Lab / no review_queue (25 total)

All 25 SEAL invariants carry byte-equivalent into P2 AND must carry byte-equivalent into P3 BUILD:

- **7 B005_NNN:** `no_live_trading` · `no_strategy_lab_promotion` · `no_review_queue_mutation` · `no_brokerage_connection` · `no_external_network` · `no_databento_at_runtime` · `no_production_signal`
- **4 B006_001:** `no_strategy_optimization_authorized` · `no_profitability_claim` · `no_universe_membership_logic` · `no_dr_redefinition_post_seal`
- **2 B006_002:** `no_warmup_order_submission` · `dr6_warmup_contamination_blocked`
- **5 s10-D1:** `no_continuous_roll_stitch_modification_post_seal` · `no_mcl_inclusion_under_long_history_scope` · `no_intraday_schema_ingest_under_daily_only_design` · `databento_api_key_read_from_env_only_never_logged_or_saved` · `no_pyramid_per_signal`
- **3 s11-d1:** `single_instrument_universe_NO_widening_post_seal` · `no_substitution_of_any_symbol_into_this_universe_post_seal` · `mnq_c0_csv_reuse_byte_equivalent_no_fresh_fetch`
- **4 s12-d1:** `donchian_15_8_locked_at_plan_no_retreat_to_55_20` · `no_revision_of_s11_d1_sealed_artifacts` · `s12_d1_does_not_supersede_s11_d1_v1_p1_p2_clarification_rev2` · `mechanic_family_lock_at_plan_no_reopening_at_draft_or_seal`

---

## 9. Exact next authorized phase

This P2 authorizes ONLY the existence of the planned BUILD scope. It does NOT authorize execution of P3 BUILD itself.

| Phase | Authorization phrase | Scope |
|---|---|---|
| **P3 BUILD only** | `"Authorize s12 D1 P3 BUILD only"` | Author runner harness modules + tests + build reports per this P2 plan. BUILD authors code; BUILD verifies unit-test smoke battery passes locally; BUILD does **NOT** run the strategy on IS or OOS data. **NO automatic RUN.** P4 SMOKE and later phases are separate. |
| **Deferral** | `"Defer / Pause s12-d1 track"` | Hold S12-D1 at P2 without advancing further. |

### P3 BUILD must carry byte-equivalent

All 25 SEAL invariants · all 14 DA-register values · DA4=B · C1.A acknowledgment · C1.D disposition · K9 threshold (100) · K4 max-drawdown (50% of START_CASH) · per-trade risk (1.0%) · Donchian periods (15/8) · ATR (Wilder 20, 2N) · `max_units_per_market = 1` · `START_CASH = $100,000` · WARMUP (220) · RTH (09:30-16:00 ET) · 5-tier cost set · Commission/Fees/Slippage · IS/OOS windows · audit-clean CSV reuse · no new Databento fetch · no API key access.

### No automatic build or run

This P2 does **NOT** authorize: build, run, simulator, backtest, signal compute, data fetch, Databento call, `DATABENTO_API_KEY` access, Strategy Lab promotion, review_queue mutation, idea_memory mutation, brokerage connection, orders, paper trade, live trade. Each subsequent phase requires a separate fresh operator authorization block.

---

## 10. Validation V-gates (this P2 turn)

V1 ASCII · V2 keyed sections consistent · V3 no execution language · V4 no self-authorization to P3 BUILD or RUN · V5 no code modification · V6 no backtest · V7 no simulator · V8 no signal compute · V9 no fetch · V10 no network IO · V11 no live trading · V12 P1 + sealed spec byte-stable at HEAD · V13 exactly 2 new files staged · V14 `lessons.md` unstaged + untouched · V15 DA4=B carried from P1 · V16 C1.A + C1.D carried byte-equivalent from P1

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

---

## 12. Labels

`S12_D1_P2_PHASE_2_PLAN_COMPLETE` · `P3_BUILD_SCOPE_DEFINED` · `ANCHORS_TO_P1_AT_BD7245E_AND_SEAL_AT_9CE4D66` · `DATA_REUSE_AUDIT_CLEAN_MNQ_C0_CSV_FROM_S10_D1` · `NO_NEW_DATABENTO_FETCH` · `NO_API_KEY_ACCESS` · `RUNNER_HARNESS_BUILD_OUTPUT_PATHS_PLANNED` · `TESTS_SMOKE_BATTERY_15_PLANNED` · `COST_STRESS_5_TIER_LOCKED` · `IS_OOS_SEPARATION_LOCKED` · `SIBLING_DRIVER_DESIGN_RECOMMENDED` · `OOS_K9_RISK_WARNING_CARRIED_FORWARD` · `DR1_INCONCLUSIVE_HOLD_FOR_OOS_K9_SUB_THRESHOLD` · `NO_AUTOMATIC_BUILD_OR_RUN` · `P3_BUILD_REQUIRES_SEPARATE_AUTHORIZATION` · `NO_BUILD` · `NO_SIMULATOR_RUN` · `NO_BACKTEST` · `NO_SIGNAL_COMPUTED` · `NO_DATA_FETCH` · `NO_DATABENTO_CALL` · `NO_DATABENTO_API_KEY_ACCESS` · `NO_REVIEW_QUEUE_MUTATION` · `NO_STRATEGY_LAB_PROMOTION` · `NO_LIVE_TRADING` · `VERDICT_NEVER_MEANS_LIVE_READY`

---

## 13. Seal

```
seal_method = sha256 over json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False) EXCLUDING report_seal_sha256 + seal_method

report_seal_sha256 = <see JSON report_seal_sha256 field>
```

**S12-D1 P2 phase-2 plan sealed. Anchors to P1 at `bd7245e` + SEAL at `9ce4d66`. P3 BUILD scope defined (runner harness + 15-test smoke battery + sibling drivers + audit-clean CSV reuse + zero new Databento fetch). NO automatic BUILD or RUN. Trading: PAUSED. Live: BLOCKED_AT_6_GATES. FRC never granted.**
