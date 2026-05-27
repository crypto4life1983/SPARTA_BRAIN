# S10-D2 Lifecycle Park Report (SEALED)

**Schema:** `sparta.s10.d2.lifecycle_park_report.v1`
**Phase:** `S10_D2_LIFECYCLE_PARK_REPORT`
**Phase prefix:** `PHASE2-S10-D2-XAD-RC-LIFECYCLE`
**Controller session:** THIS_SESSION_ONLY
**Report kind:** Lifecycle park report; synthesises prior sealed artifacts; no new computation.
**Sealed at (UTC):** `2026-05-27T04:05:00Z`

**Authorization:** *"Authorize S10-D2 lifecycle park report only."*

---

## 0. Candidate

| Field | Value |
|---|---|
| candidate_record_id | `s10-cross-asset-donchian-no-pyramid-reparam-cap-nq-gc-zn-cl` |
| Strategy class | Cross-asset Donchian breakout, no-pyramid, reparameterised capital |
| Universe | NQ, GC, ZN, CL (continuous futures) |
| Donchian entry / exit | 55 / 20 |
| ATR | Wilder, period 20 |
| Stop multiple | 2N |
| Portfolio risk / trade | 1.0% |
| Max units per market | 1 (no-pyramid) |
| AMB6 filter | NONE |
| Starting cash (MNQ-equiv) | $500,000 |
| Cost-stress tiers evaluated | S0 / S1 / S2 / S3 |
| algo_version_for_run_id | `s10_d2_v0_1_0` |

---

## 1. Final lifecycle status

| Field | Value |
|---|---|
| **park_status_enum** | **`PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED`** |
| Trading | `PAUSED` |
| Live | `BLOCKED_AT_6_GATES` |
| FRC granted | `False` |
| Advisory label (permanent) | `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` |
| `verdict_never_means_live_ready` | `True` |
| `live_promotion_path_closed` | `True` |
| Strategy Lab promotion | `NEVER_PROMOTED` |
| review_queue | `NEVER_INSERTED` |
| idea_memory | `NEVER_MUTATED` |

park_status_enum allowed (4 pre-anchored values, selected highlighted):
1. **`PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED`** ← selected
2. `PARKED_SAFE_BUT_NOT_MONEY_PROVEN_OOS_SIZING_UNDERSIZED`
3. `PARKED_OOS_REFUTED`
4. `PARKED_PENDING_LONGER_OOS_WINDOW`

---

## 2. Sealed-chain inventory

| Phase | Seal (first 16) | Commit |
|---|---|---|
| Tier-N spec | `f5ca5ee63024e9c8` | (foundational) |
| Plan-lock | `ba8bf954d44b373c` | — |
| Phase-2 plan | `7a48ad64236971e6` | — |
| Predecessor | `007110ff5a57dd04` | — |
| P3 BUILD in-sample driver | `ddd604c96508a0ab` | — |
| P3 BUILD runner | `1eb04aa312f40531` | — |
| P3.5 scaffold completion | `66d38f359b54882b` | — |
| **P3.6 OOS driver BUILD** | `c7d9d7888f2bc5df` | `f0b3721` |
| P4 smoke | `c31ded81f9a28835` | — |
| **P6 IS diagnostic** | `e6cdc7c68a9e2b7b` | `d6977631` |
| **P6.5 cost-stress matrix** (this session) | `04351ca093ec20b0` | `9211ab7c` |
| **P7 IS decision memo** | `87baa6e8c4cc1eb4` | `b466fbb` |
| **K10 pairwise dependence** | `8c620cc5bfe53f71` | `4ddaa84e` |
| K10 duplicate cleanup (this session) | `43d0b60983097233` | `ed046d54` |
| **P10 OOS gate** | `4038e5334feba9ea` | `15231cb` |
| **P11 PARK memo** | `e121b82b411697c7` | `23c71648` |
| **OOS scope reconciliation + gating review** (this session) | `c57bb806ca56e158` | `b6a22110` |

---

## 3. IS evidence summary (P6 @ `d6977631`)

| Metric | Value |
|---|---|
| Window | 2013-01-01 to 2022-12-30 (10 years) |
| Cost tier | S1 |
| closed_trades_portfolio | **200** |
| net_pnl_usd | **+$973,098** |
| sharpe_proxy_per_trade | **+0.14311** |
| expectancy_per_trade_usd | **+$4,865** |
| trade_curve_maxdd_pct | −28.31% |
| win_rate_portfolio_pct | 35.0 |
| win_rate_gap_pp | +10.48 |
| breakeven_wr_pct | 24.52 |
| all_safety_warnings_zero | **True** |
| cap_binding_events | 0 |
| K-fires count | **0** |
| Verdict | **`READY_FOR_LONGER_BACKTEST`** |

Clean IS pass.

---

## 4. Cost-stress PASS summary (P6.5 @ `9211ab7c`)

Single deterministic-driver run across the four-tier sweep:

| Tier | trades | net_pnl_usd | sharpe pt | expectancy | maxdd % | wr % |
|---|---|---|---|---|---|---|
| **S0** | 200 | +987,242 | +0.14502 | +4,936 | −27.97 | 35.0 |
| **S1** | 200 | +973,098 | +0.14311 | +4,865 | −28.31 | 35.0 |
| **S2** | 200 | +913,849 | +0.14003 | +4,569 | −29.76 | 35.0 |
| **S3** | 200 | +824,423 | +0.13004 | +4,122 | −30.35 | 34.5 |

S2 is 93.9% of S1; S3 is 84.7% of S1. Smooth, monotonically-decreasing-but-always-positive across the cost-stress range.

**Decision rules:**
- DR2 (S2 or S3 degrades >50% OR flips negative): **False**
- DR3 (S0 positive AND S1/S2/S3 non-positive): **False**
- DR5 (S0 positive AND S1 non-positive): **False**
- **K12 (DR fires):** **False** ← *cost-stress survives*

All safety counters zero across all four tiers. Verdict: **`READY_FOR_NEXT_PHASE`**.

---

## 5. K10 PASS summary (K10 @ `4ddaa84e`)

| Field | Value |
|---|---|
| Method | `derive_rth_daily_bars` + simple daily returns + Pearson + unweighted mean of 6 pairs |
| Markets | NQ, GC, ZN, CL |
| Common dates | 2,253 (intersection over IS window) |
| **avg pairwise correlation (signed)** | **+0.052804** (well below 0.50 threshold) |
| effective_independent_bets (proxy) | ~3.55 |
| **K10 status** | **`K10_PASS_AVG_PAIRWISE_CORR_AT_OR_BELOW_0_50`** |
| Gap G2 status | **CLOSED** |

Independent corroboration: this controller session ran K10 with a small ordering variant (intersect on return-dates vs bar-dates) and got `avg = +0.040090 / eff_bets = 3.5706`. Verdict CLEARS by ~10× the threshold either way. The duplicate diagnostic_report was discarded at `ed046d54`.

---

## 6. OOS gating review summary (OOS review @ `b6a22110`)

| Field | Value |
|---|---|
| OOS window | 2023-01-01 to 2025-12-31 (3 years) |
| Cost tier | S1 single-tier |
| OOS driver | `out_of_sample_driver.py` (sibling at P3.6 `f0b3721`) |
| Driver byte-stable through run | **True** |
| Monkey patches applied | **0** |
| OOS closed_trades | **53** ← below K9 threshold of 100 |
| OOS net_pnl_usd | +$113,450 |
| OOS sharpe_proxy | +0.10051 |
| OOS expectancy_usd | +$2,141 |
| OOS maxdd_pct | **−12.96% (better than IS)** |
| OOS wr_gap_pp | +6.52 |
| OOS all_safety_warnings_zero | **True** |
| OOS cap_binding_events | 0 |
| K_fires | `K9_closed_trades_lt_100` |
| K_fires count | 1 |
| A_fails | `A1_closed_trades_ge_100` |
| **C7 verdict** | **`INSUFFICIENT_SAMPLE`** |
| **OOS qualitative verdict** | **`OOS_INDETERMINATE_BUT_DIRECTIONALLY_CONSISTENT`** |
| OOS structural enforcement | **8/8 held** |
| Chain-of-custody grade | AUDITABLE |
| Framework discipline grade | HIGH |
| Overinterpretation risk | NONE OBSERVED |
| Threshold loosening | NONE |
| Reconciliation verdict | **`CHAIN_RECONCILED_CLEAN`** |
| Observations logged | 6 (informational / affirmative; none are defects) |
| Defects identified | **0** |

### IS vs OOS ratios

| Metric | IS S1 | OOS S1 | Ratio |
|---|---|---|---|
| closed_trades | 200 | 53 | 0.27 |
| trades/year | 20.0 | 17.7 | **0.88** (sizing-fix worked) |
| sharpe | +0.14311 | +0.10051 | 0.70 |
| expectancy | +4,865 | +2,141 | **0.44** |
| maxdd | −28.31% | −12.96% | better |

---

## 7. Why parked

**Primary reason.** OOS sample insufficient. Closed-trade count on the 3-year OOS window was **53** (below K9 threshold of 100 and below A1 acceptance threshold of 100). This is a function of available history length, **not** a function of the strategy.

**Secondary observations:**
- OOS direction was consistent with IS (positive sharpe, expectancy, net PnL).
- All safety counters held zero across IS + 5 cost tiers + OOS.
- Drawdown actually improved on OOS (−12.96% vs IS −28.31%).
- Trade density preserved at 88% of IS rate — s8-D1 sizing-fix lesson correctly applied.
- Per-trade expectancy degraded to 0.44× of IS; per-trade sharpe degraded to 0.70× of IS.

**Why not ADVANCE.** Lacking statistical confirmation is not a basis for advancement. Advancing to a longer OOS, OOS cost-stress, or any tighter validation would each be a fresh research hypothesis requiring its own sealed authorization.

**Why not KILL.** Safety counters held zero throughout. Performance K-gates K1/K2/K4 did not fire on OOS. OOS direction is consistent with IS. The chain ran cleanly and produced an interpretable INDETERMINATE result; discarding usable evidence would be wrong.

---

## 8. Why not live-ready

1. `verdict_never_means_live_ready` is a permanent invariant on every Tier-N candidate; no verdict can promote a candidate to live or paper trading.
2. `live_promotion_path_closed: True`. The 6-gate live block is permanent regardless of any research verdict.
3. OOS sample was below the K9 threshold of 100 closed trades; `INSUFFICIENT_SAMPLE` is by definition not a confirmation of edge.
4. FRC (full research clearance) was never granted to this candidate.
5. No threshold loosening (e.g., relaxing K9 to claim OOS PASS) is permitted by the framework; P11 `explicit_blocked_actions` includes *"DO NOT relax K9 threshold to confirm OOS."*
6. Advisory label permanent: `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE`.
7. Trading status is and remains `PAUSED`.

---

## 9. Why no Strategy Lab promotion

1. The Tier-N research framework is structurally separated from Strategy Lab; promotion requires a verdict that explicitly authorizes promotion. `INSUFFICIENT_SAMPLE` / `PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED` is not such a verdict.
2. S10-D2 P11 `explicit_blocked_actions` includes *"DO NOT make any profitability claim outside this conservative PARK framing."*
3. Strategy Lab promotion would require FRC + a CONFIRMED OOS verdict + live-readiness, none of which exist for S10-D2.
4. The Strategy Lab path is reserved for a `READY_FOR_LIVE_PROMOTION` verdict (or equivalent), which is not in the s10-D2 chain's allowed enum.

---

## 10. Why no review_queue mutation

1. S10-D2 PARK is a research-side lifecycle decision; `review_queue.json` is a Strategy Lab operational artifact that controls trading flow.
2. Mutating `review_queue.json` would imply this candidate is queued for human review prior to trading; PARKED candidates are explicitly not queued for trading review.
3. P11 `explicit_blocked_actions` includes *"DO NOT mutate review_queue.json."*
4. S10-D2 has never been inserted into `review_queue` and will not be inserted by this PARK report.

---

## 11. Future options (listed; none authorized)

**NONE of these options is pre-approved.** Each requires a separate fresh sealed operator authorization. This list is purely informational.

1. **`s11_d1_mnq_single_instrument_fallback`** — Pursue S11-D1 MNQ.c.0 single-instrument long-history Tier-N as the next research track. Already specified at parallel-session commit `9c630886`.
2. **`longer_oos_window`** — Extend the OOS window past 2025-12-31 once additional Databento history is available. Today's data cut would add ~5 months of additional bars.
3. **`oos_cost_stress_sweep`** — Run the OOS cost-stress matrix S0–S4 against the OOS window (A8 was correctly skipped at P10 OOS gate). Tests whether the cost-stress robustness observed on IS holds on OOS data as well.
4. **`fresh_candidate_different_markets_or_regime_overlay`** — Author a new Tier-N candidate using a different universe (e.g., currency futures, agricultural futures, or a regime-overlay variant) and run it through the full sealed lifecycle.

---

## 12. Prior park precedents referenced

| Candidate | Status | Binding constraint |
|---|---|---|
| s7-D1 | REJECT_FAST | K12 fired on cost-stress |
| s8-D1 | `PARKED_SAFE_BUT_NOT_MONEY_PROVEN_OOS_SIZING_UNDERSIZED` | sizing |
| s9 | PARKED | K1+K2 fired on RSI-2 cross-asset ETF proxy |
| s10-D1 | PARKED | DR9 fired (cross-symbol data continuity) |
| **s10-D2** | **`PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED`** | **OOS window length (3 yrs; 53 trades < K9 100)** |

**Common lesson.** Each Tier-N candidate parks (or rejects) under a distinct, well-articulated binding-constraint root. The framework consistently refuses to overinterpret directionally-encouraging results when a specific gate fires.

---

## 13. Chain evidence summary

| Item | Status |
|---|---|
| phases_sealed_count | 10+ |
| IS passed | True |
| Cost-stress passed | True |
| K10 passed | True |
| OOS directional | True |
| OOS sample sufficient | **False** |
| OOS safety zero throughout | True |
| OOS structural enforcement complete | True (8/8) |
| Reconciliation clean | True |
| Defects identified | **0** |

---

## 14. Negative invariants (all True)

`no_databento_call` · `no_databento_api_key_access` · `no_data_fetch` · `no_oos_re_run` · `no_p10_re_run` · `no_p11_modification` · `no_oos_driver_modification` · `no_in_sample_driver_modification` · `no_runner_harness_modification` · `no_cache_modification` · `no_strategy_code_modification` · `no_canonical_k10_modification` · `no_simulator_run` · `no_backtest_run` · `no_signal_compute` · `no_strategy_lab_invoked` · `no_candidate_promoted` · `no_brokerage_connection` · `no_orders_created` · `no_paper_or_live_trade` · `no_review_queue_mutation` · `no_idea_memory_mutation` · `no_lessons_md_staged_or_modified` · `no_tier_n_spec_modification` · `no_plan_lock_modification` · `no_phase2_plan_modification` · `no_runbook_modification` · `no_pipeline_manifest_modification` · `no_decisions_md_modification` · `no_gitignore_modification` · `no_claude_md_modification` · `no_branch_change` · `no_git_push` · `no_s7_artifact_modified` · `no_s8_d1_artifact_modified` · `no_s9_artifact_modified` · `no_s10_d1_artifact_modified` · `no_s11_d1_artifact_modified` · `no_orb_artifact_modified` · `no_step_30_cost_constant_modified` · `no_threshold_loosening` · `no_k9_threshold_relaxation_proposed` · `no_frc_grant` · `no_live_readiness_claim` · `no_profitability_claim` · `no_pre_approval_of_future_options` · `no_key_leakage` · `no_external_network_call`

---

## 15. Labels

- `S10_D2_LIFECYCLE_PARK_REPORT_COMPLETE`
- `S10_D2_PARKED_ON_OOS_INSUFFICIENT_SAMPLE`
- `PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED`
- `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE`
- `NOT_LIVE_READY`
- `NOT_PAPER_READY`
- `NEVER_PROMOTED_TO_STRATEGY_LAB`
- `NEVER_INSERTED_INTO_REVIEW_QUEUE`
- `NO_OOS_RERUN`
- `NO_SIMULATOR_RERUN`
- `NO_BACKTEST`
- `NO_DATA_FETCH`
- `NO_DATABENTO_CALL`
- `NO_DATABENTO_API_KEY_ACCESS`
- `NO_REVIEW_QUEUE_MUTATION`
- `NO_STRATEGY_LAB_PROMOTION`
- `NO_LIVE_TRADING`
- `VERDICT_NEVER_MEANS_LIVE_READY`

---

## 16. Seal

```
seal_method = sha256 over json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False) EXCLUDING report_seal_sha256 + seal_method

report_seal_sha256 = <see JSON report_seal_sha256 field>
```

**S10-D2 lifecycle park report sealed. Candidate is PARKED. Trading: PAUSED. Live: BLOCKED_AT_6_GATES. FRC never granted. Advisory label permanent: `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE`. No promotion to Strategy Lab. No mutation of review_queue. Future research options listed but none authorized.**
