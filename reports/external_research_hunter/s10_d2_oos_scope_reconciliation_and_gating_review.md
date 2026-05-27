# S10-D2 OOS Scope Reconciliation and Gating Review (SEALED)

**Schema:** `sparta.s10.d2.oos_scope_reconciliation_and_gating_review.v1`
**Phase:** `S10_D2_OOS_SCOPE_RECONCILIATION_AND_GATING_REVIEW`
**Phase prefix:** `PHASE2-S10-D2-XAD-RC-REVIEW`
**Report kind:** Read-only review. No re-run. No modification.
**Controller session:** THIS_SESSION_ONLY
**Sealed at (UTC):** `2026-05-27T03:50:00Z`

**Authorization:** *"Authorize S10-D2 OOS scope reconciliation and gating review only."*

**Candidate:** `s10-cross-asset-donchian-no-pyramid-reparam-cap-nq-gc-zn-cl`

---

## 0. Executive

S10-D2 (cross-asset Donchian no-pyramid reparam-cap NQ+GC+ZN+CL @ $500k starting cash) has been driven through the complete sealed Tier-N research lifecycle (P3 BUILD → P11 PARK) across **10+ commits**. The parallel session executed P3.6 OOS driver BUILD, P10 OOS gate, and P11 PARK memo. This review reconciles the full chain and audits the gating structure.

**Verdict: `CHAIN_RECONCILED_CLEAN`**
- 8/8 OOS structural enforcement invariants held
- 6 minor observations logged (all informational or affirmative; none defects)
- Final candidate status: **`PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED`**
- Permanent invariants held: `verdict_never_means_live_ready`, `live_promotion_path_closed`, `frc_never_granted`, `BLOCKED_AT_6_GATES`

---

## 1. Full sealed-chain inventory

| Phase | Commit | Seal (first 16) | Verdict |
|---|---|---|---|
| P3 BUILD in-sample driver | (prior) | `ddd604c96508a0ab` | — |
| P3 BUILD runner | (prior) | `1eb04aa312f40531` | — |
| P3.5 scaffold completion | (prior) | `66d38f359b54882b` | — |
| P3.6 OOS driver BUILD | `f0b3721` | `c7d9d7888f2bc5df` | — |
| P4 smoke | (prior) | `c31ded81f9a28835` | — |
| P6 IS diagnostic | `d6977631` | `e6cdc7c68a9e2b7b` | `READY_FOR_LONGER_BACKTEST` |
| P6.5 cost-stress matrix | `912d332` (canonical) + `9211ab7c` (this session) | `f9a34674de4f7fdf` | `READY_FOR_NEXT_PHASE` / K12 not fired |
| P7 decision memo | `b466fbb` | `87baa6e8c4cc1eb4` | `ADVANCE_TO_P10_OOS_GATE` |
| K10 pairwise dependence | `4ddaa84e` | `8c620cc5bfe53f71` | `K10_PASS` |
| K10 duplicate cleanup (this session) | `ed046d54` | `43d0b60983097233` | — |
| **P10 OOS gate** | **`15231cb`** | **`4038e5334feba9ea`** | **`INSUFFICIENT_SAMPLE`** |
| **P11 PARK memo** | **`23c71648`** | **`e121b82b411697c7`** | **`PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED`** |

**Anchors (drift = 0 through every phase):**
- Tier-N spec: `f5ca5ee63024e9c8b7b1e85762558ec35eb3d4ebb9ce2a160cbe0f1a0e80a679`
- Plan-lock: `ba8bf954d44b373c0ffdc38a1cf8f73dec31a9fc538f0b7584a20659d79ea354`
- Phase-2 plan: `7a48ad64236971e6fd2a2fa58ab7ab746a71543778ed0a868f3cdf9ff8f74ac3`
- Predecessor: `007110ff5a57dd04b184409bad64fd667374cd049155416c869a73f7af0c1f97`

---

## 2. OOS driver BUILD review (P3.6 @ `f0b3721`)

**Design choice:** `OPTION_1_SIBLING_DRIVER` — preserves `in_sample_driver.py` byte-stable on disk (P3 BUILD sha `19749ada4d98e1b2` unchanged); auditable diff in git; single-purpose drivers.

**21 mechanical substitutions** applied to operational config only:

| What changed | IS | OOS |
|---|---|---|
| `CACHE_ROOT` | `data/databento_cache` | `data/databento_cache_oos` |
| Window start | `2013-01-01` | `2023-01-01` |
| Window end | `2022-12-30` | `2025-12-31` |
| `EXPECTED_FILES_PER_ROOT` | 120 | 36 |
| `EXPECTED_CACHE_BYTES` | per-symbol IS bytes | per-symbol OOS bytes |
| Run function | `run_in_sample` | `run_out_of_sample` |
| Output paths | `in_sample_diagnostic` | `out_of_sample_diagnostic` |

**Strategy parameters changed:** **NONE.** All strategy params live in `runner_main.CONFIG` which is the SAME module both drivers lazy-import. Donchian 55/20, Wilder ATR(20), 2N stop, 1% portfolio risk sizing, max_units_per_market=1 (no-pyramid invariant), AMB6 filter NONE, starting_cash_mnq_equivalent $500,000, S0..S4 cost-stress tiers — **all preserved byte-equivalent**.

**Tests:** 19/19 PASSED in 0.05s. **Source byte-stability:** 13/13 guarded source files held; 0 drift.

---

## 3. OOS execution review (P10 @ `15231cb`)

**Driver used:** `out_of_sample_driver.py` (committed at P3.6 BUILD).
**Driver byte-stability through run:** `7941ff28e0dbad0f` (start) == `7941ff28e0dbad0f` (end). **True.**
**Monkey patches applied:** **0.**
**Hard boundaries held:** **30.**
**Cost tier:** S1 single-tier.
**Duration:** 81.8 s.
**Run error:** None.

### 3.1 OOS metrics (window 2023-01-01 to 2025-12-31; 3 years)

| Metric | Value |
|---|---|
| closed_trades_portfolio | **53** |
| net_pnl_usd | +$113,450 |
| sharpe_proxy_per_trade | **+0.10051** |
| expectancy_per_trade_usd | +$2,141 |
| trade_curve_maxdd_pct | **−12.96%** |
| win_rate_portfolio_pct | 33.96 |
| breakeven_wr_pct | 27.44 |
| win_rate_gap_pp | +6.52 |
| avg_win_usd | +$23,823 |
| avg_loss_usd | −$9,011 |
| cap_binding_events | 0 |
| all_safety_warnings_zero | **True** |
| starting_cash | $500,000 |
| final_equity | $613,450 (+22.7%) |

### 3.2 K-gate evaluation

| K-gate | Status | Notes |
|---|---|---|
| K1 sharpe<0 | clear | +0.10051 |
| K2 expectancy≤0 | clear | +$2,141 |
| K4 maxdd>50% | clear | −12.96% |
| K6 safety>0 | clear | all safety zero |
| **K9 closed_trades<100** | **FIRES** | **53 < 100** |
| K11 cap_binding>1000 | clear | 0 |
| K12 DR fires | clear | n/a single tier |
| **K_fires_count** | **1** | |

### 3.3 A-gate evaluation

| A-gate | Status | Value |
|---|---|---|
| **A1 closed_trades≥100** | **FAIL** | 53 |
| A2 sharpe>0 | PASS | +0.10051 |
| A3 expectancy>0 | PASS | +$2,141 |
| A4 maxdd≤50% | PASS | −12.96% |
| A5 wr_gap | PASS | +6.52pp |
| A6 validator | PASS | no-pyramid + plan-lock |
| A8 cost_stress | n/a this turn | IS-side at P6.5 |
| A9 phase2 inheritance | PASS | C1-C8 byte-equivalent |
| A10 cap_binding=0 | PASS | 0 |

### 3.4 Verdicts

- **C7 enum allowed:** `FAIL_SAFETY` / `INSUFFICIENT_SAMPLE` / `READY_FOR_LONGER_BACKTEST`
- **C7 verdict (P10):** **`INSUFFICIENT_SAMPLE`**
- **OOS qualitative:** **`OOS_INDETERMINATE_BUT_DIRECTIONALLY_CONSISTENT`**

### 3.5 Cache attestation

| Cache | Byte-stable through run | Dir |
|---|---|---|
| OOS | True | `data/databento_cache_oos` |
| IS (orig) | True | `data/databento_cache` |

---

## 4. IS vs OOS comparison

| Metric | IS S1 (10y) | OOS S1 (3y) | Ratio |
|---|---|---|---|
| closed_trades | 200 | **53** | 0.27 |
| trades/year | 20.0 | 17.7 | **0.88** |
| net_pnl_usd | +973,098 | +113,450 | 0.12 (0.39/y) |
| sharpe_proxy | +0.14311 | +0.10051 | **0.70** |
| expectancy_usd | +4,865 | +2,141 | **0.44** |
| maxdd_pct | −28.31 | −12.96 | **0.46 (better)** |
| wr_gap_pp | +10.48 | +6.52 | 0.62 |

**What survived:**
- Direction of edge (positive sharpe, expectancy, net PnL)
- All safety counters held zero across IS + 5 cost tiers + OOS
- No-pyramid invariant
- Starting cash invariant ($500,000)
- Trade-density (88% of IS rate; **sizing fix worked**)
- Drawdown actually improved on OOS

**What degraded:**
- Per-trade expectancy ~0.44× IS magnitude
- Per-trade sharpe ~0.70× IS magnitude
- Net PnL/year ~0.39× IS magnitude
- Closed-trade count 53 < K9 threshold of 100

---

## 5. PARK decision review (P11 @ `23c71648`)

**Park status enum:** **`PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED`**

**Park enum allowed (4 values, pre-anchored):**
1. `PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED` ← selected
2. `PARKED_SAFE_BUT_NOT_MONEY_PROVEN_OOS_SIZING_UNDERSIZED`
3. `PARKED_OOS_REFUTED`
4. `PARKED_PENDING_LONGER_OOS_WINDOW`

**Decision logic (8 steps):**
1. P6 IS clean (200 trades, 0 K-fires, all A-pass)
2. P6.5 cost-stress matrix clean (READY_FOR_NEXT_PHASE; A8 PASS; K12 not fired; 0 DR fires)
3. P7 correctly advanced to OOS gate
4. P10 OOS directionally consistent but K9 fired (53 < 100)
5. Safety counters held zero across IS + 5 cost tiers + OOS
6. OOS sample structurally limited by available 3-year window vs 10-year IS
7. Positive OOS direction is encouraging but is NOT proof
8. Conservative lifecycle decision is PARK — not ADVANCE, not KILL, not PROMOTE

### 5.1 Comparison vs s8-D1 PARK precedent

| | s8-D1 | s10-D2 |
|---|---|---|
| Park status | `PARKED_SAFE_BUT_NOT_MONEY_PROVEN_OOS_SIZING_UNDERSIZED` | `PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED` |
| Park commit | `6e7b491` | `23c71648` |
| Binding constraint | sizing (0 contracts at $100k for full-size futures) | OOS window length (3 years; 53 trades) |
| Sizing fix tried | n/a | **$500k starting cash → trade density preserved** |
| What didn't survive | OOS structural under-allocation | OOS sample sufficiency |

The s10-D2 sizing fix succeeded; what s10-D2 needed and did not have was a **longer OOS window**, not different sizing.

### 5.2 Future research options (NONE pre-approved)

1. `option_1_s11_d1_mnq_c_0_single_instrument_fallback`
2. `option_2_longer_oos_window`
3. `option_3_oos_cost_stress_sweep`
4. `option_4_fresh_candidate_different_markets_or_regime_overlay`

Per P11: `no_option_is_pre_approved_by_this_memo: True` / `all_options_require_separate_fresh_sealed_authorization: True`

---

## 6. Gating structure review

### 6.1 Closed verdict enums (pre-anchored in Tier-N spec)

- **C7 OOS gate (3 values):** `FAIL_SAFETY` / `INSUFFICIENT_SAMPLE` / `READY_FOR_LONGER_BACKTEST`
- **P11 PARK (4 values):** see §5
- No ad-hoc enum widening observed at any phase.

### 6.2 K-gates evaluated

`K1`/`K2`/`K4`/`K6`/`K9`/`K10`/`K11`/`K12`

### 6.3 A-gates evaluated

`A1`/`A2`/`A3`/`A4`/`A5`/`A6`/`A7`/`A8`/`A9`/`A10`

### 6.4 DR-rules

`DR2`/`DR3`/`DR5`/`DR9`

### 6.5 Permanent invariants (all True)

- `verdict_never_means_live_ready`
- `live_promotion_path_closed`
- `live_trading_remains_blocked_at_6_gates_permanently`
- `frc_never_granted`
- Advisory label permanent: `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE`

---

## 7. OOS structural enforcement validation (8/8 held)

| Invariant | Held | Evidence |
|---|---|---|
| **No re-fit on OOS** | True | CONFIG byte-stable across IS + cost-stress + OOS |
| **No winner-selection on OOS** | True | Single candidate, single S1 tier, no multi-candidate compare |
| **Single-shot OOS** | True | 81.8s once; no iteration; PARK terminal |
| **Cache isolation** | True | `data/databento_cache_oos/` separate dir; both caches byte-stable in attestation |
| **Sibling driver preserves IS byte-stability** | True | IS driver sha at P3.6 end == P3 BUILD baseline |
| **Pre-anchored verdict enum** | True | C7 (3 values), P11 (4 values), no widening |
| **No threshold loosening** | True | K9 threshold (100) not relaxed; explicit_blocked_actions includes "DO NOT relax K9" |
| **No monkey-patching during OOS** | True | monkey_patches_applied_count = 0; driver byte-stable through run |

---

## 8. Observations (6; none are defects)

| # | Topic | Severity | Note |
|---|---|---|---|
| OBS-1 | A8 cost-stress not run at OOS | informational | Correctly scoped; option_3 if pursued |
| OBS-2 | K10 timing vs P10 inheritance | informational | K10 sealed independently; not in P10/P11 inherited_seals, but auditable separately. Minor chain-of-custody gap. |
| OBS-3 | OOS window cutoff 2025-12-31 vs today 2026-05-27 | informational | ~5 months of additional data theoretically available; option_2 if pursued |
| OBS-4 | Trade-density consistency | affirmative | OOS 17.7 trades/year vs IS 20.0 (0.88×); s8-D1 sizing-fix lesson successfully applied; sizing was NOT the binding constraint |
| OBS-5 | Verdict consistency with framework | affirmative | Strongest-IS candidate correctly PARKED on OOS; framework refused to overinterpret directionally-consistent small-sample data |
| OBS-6 | DR9 implicit at OOS | informational | OOS cache passed EXPECTED_CACHE_BYTES check (36 files per root, exact bytes); serves as implicit DR9 enforcement |

**The only observation that warrants future framework attention is OBS-2** (K10 seal not appearing in P10/P11 `inherited_seals`). It's auditable via separate commit references and doesn't affect this verdict, but for future Tier-N candidates with universe-property gates, including K10 in the standard inherited_seals dict would tighten chain-of-custody.

---

## 9. Reconciliation verdict

**`CHAIN_RECONCILED_CLEAN`**

- 10+ sealed commits form a complete S10-D2 lifecycle (P3 BUILD → P11 PARK)
- All anchor seals inherited byte-equivalent through every phase
- OOS structural enforcement: **8/8** invariants held
- All safety K-gates held zero across IS + 5 cost tiers + OOS
- Conservative PARK decision appropriate for `INSUFFICIENT_SAMPLE` result
- s8-D1 PARK precedent comparison correctly differentiates binding constraints

| Grade | Value |
|---|---|
| Chain-of-custody | **AUDITABLE** |
| Framework discipline | **HIGH** |
| Overinterpretation risk | NONE OBSERVED |
| Threshold loosening | NONE |

---

## 10. Negative invariants (all True)

`no_databento_call` · `no_databento_api_key_access` · `no_data_fetch` · `no_oos_re_run` · `no_p10_re_run` · `no_p11_modification` · `no_oos_driver_modification` · `no_in_sample_driver_modification` · `no_runner_harness_modification` · `no_cache_modification` · `no_canonical_k10_modification` · `no_simulator_run` · `no_backtest_run` · `no_signal_compute` · `no_strategy_lab_invoked` · `no_candidate_promoted` · `no_brokerage_connection` · `no_paper_or_live_trade` · `no_review_queue_mutation` · `no_idea_memory_mutation` · `no_lessons_md_staged_or_modified` · `no_tier_n_spec_modification` · `no_plan_lock_modification` · `no_phase2_plan_modification` · `no_branch_change` · `no_git_push` · `no_s7_artifact_modified` · `no_s8_d1_artifact_modified` · `no_s9_artifact_modified` · `no_s10_d1_artifact_modified` · `no_s11_d1_artifact_modified` · `no_orb_artifact_modified` · `no_step_30_cost_constant_modified` · `no_threshold_loosening` · `no_k9_threshold_relaxation_proposed` · `no_frc_grant` · `no_live_readiness_claim` · `no_profitability_claim` · `no_pre_approval_of_future_options` · `no_key_leakage` · `no_external_network_call`

---

## 11. Status

- Trading: `PAUSED`
- Live: `BLOCKED_AT_6_GATES`
- FRC granted: `False`
- Advisory label permanent: `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE`
- S10-D2 final status: `PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED`
- Next step: NONE pre-approved; any future research requires fresh authorization.

---

## 12. Labels

- `S10_D2_OOS_SCOPE_RECONCILIATION_REVIEW_COMPLETE`
- `S10_D2_GATING_STRUCTURE_REVIEW_COMPLETE`
- `CHAIN_RECONCILED_CLEAN`
- `OOS_STRUCTURAL_ENFORCEMENT_8_OF_8_HELD`
- `OBSERVATIONS_LOGGED_6`
- `NO_DEFECTS_IDENTIFIED`
- `NO_RE_RUN`
- `NO_DATABENTO_CALL`
- `NO_DATABENTO_API_KEY_ACCESS`
- `NO_OOS_COMPUTATION`
- `NO_SIMULATOR_RUN`
- `NO_BACKTEST`
- `NO_LIVE_TRADING`
- `VERDICT_NEVER_MEANS_LIVE_READY`

---

## 13. Seal

```
seal_method = sha256 over json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False) EXCLUDING report_seal_sha256 + seal_method

report_seal_sha256 = <see JSON report_seal_sha256 field>
```

**Reconciliation review sealed. Chain CLEAN. OOS enforcement 8/8. Six observations logged, none are defects. S10-D2 remains PARKED. Trading: PAUSED. Live: BLOCKED_AT_6_GATES. FRC never granted.**
