# S10-D2 Terminal Lesson (SEALED)

**Schema:** `sparta.s10.d2.terminal_lesson_sealed.v1`
**Phase:** `S10_D2_TERMINAL_LESSON_SEALED_REPORT`
**Phase prefix:** `PHASE2-S10-D2-XAD-RC-TERMINAL-LESSON`
**Controller session:** THIS_SESSION_ONLY
**Report kind:** Terminal-lesson sealed report (Path B). **`lessons.md` left untouched.**
**Sealed at (UTC):** `2026-05-27T04:15:00Z`

**Authorization:** *"Authorize S10-D2 terminal-lesson sealed report only."*

---

## 0. Path B rationale

This terminal lesson is recorded as a **sealed report under `reports/external_research_hunter/`** rather than as an append to `brain_memory/projects/trading_bot/lessons.md`.

This preserves the **no-lessons-md invariant** that has held across every commit in this controller session:
- `lessons_md_path`: `brain_memory/projects/trading_bot/lessons.md`
- `lessons_md_status_this_turn`: `NOT_TOUCHED_NOT_STAGED_NOT_COMMITTED`
- `lessons_md_dirty_pre_existing`: `True` (working-tree dirty from another session; preserved untouched)

The sealed report has identical evidentiary weight to a lessons.md entry and is cross-linked by seal sha to the rest of the S10-D2 chain.

---

## 1. Candidate

| Field | Value |
|---|---|
| candidate_record_id | `s10-cross-asset-donchian-no-pyramid-reparam-cap-nq-gc-zn-cl` |
| Strategy class | Cross-asset Donchian breakout, no-pyramid, reparameterised capital |
| Universe | NQ, GC, ZN, CL (continuous futures) |
| Starting cash (MNQ-equiv) | $500,000 |
| algo_version_for_run_id | `s10_d2_v0_1_0` |

---

## 2. Final lifecycle status

| Field | Value |
|---|---|
| **park_status_enum** | **`PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED`** |
| Trading | `PAUSED` |
| Live | `BLOCKED_AT_6_GATES` (permanent) |
| FRC granted | `False` |
| Advisory label (permanent) | `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` |
| `verdict_never_means_live_ready` | `True` |
| `live_promotion_path_closed` | `True` |
| Strategy Lab promotion | `NEVER_PROMOTED` |
| review_queue | `NEVER_INSERTED` |
| idea_memory | `NEVER_MUTATED` |

---

## 3. Key IS evidence

| Metric | Value |
|---|---|
| Window | 2013-01-01 to 2022-12-30 (10 years) |
| Cost tier | S1 |
| closed_trades_portfolio | **200** |
| net_pnl_usd on $500k starting cash | **+$973,098** |
| sharpe_proxy_per_trade | **+0.14311** |
| expectancy_per_trade_usd | **+$4,865** |
| trade_curve_maxdd_pct | −28.31% |
| all_safety_warnings_zero | **True** |
| K-fires count | **0** |
| IS verdict | **`READY_FOR_LONGER_BACKTEST`** |

Cost-stress S0–S3 all positive:

| Tier | net_pnl_usd |
|---|---|
| S0 | +$987,242 |
| S1 | +$973,098 |
| S2 | +$913,849 |
| S3 | +$824,423 |

Decision rules at IS cost-stress: **DR2 / DR3 / DR5 / K12 all False.**

K10 pairwise dependence: **avg pair corr +0.0528** (threshold 0.50; clears by ~10×). **K10 PASS.** Effective independent bets ≈ 3.55.

---

## 4. Key OOS evidence

| Metric | Value |
|---|---|
| Window | 2023-01-01 to 2025-12-31 (3 years) |
| Cost tier | S1 |
| **closed_trades** | **53** |
| **K9 threshold (min)** | **100** |
| **closed_trades below K9 threshold** | **True** |
| net_pnl_usd | +$113,450 |
| sharpe_proxy | +0.10051 |
| expectancy_usd | +$2,141 |
| trade_curve_maxdd_pct | **−12.96% (better than IS)** |
| win_rate_gap_pp | +6.52 |
| all_safety_warnings_zero | **True** |
| OOS direction vs IS | **directionally consistent** |
| Drawdown vs IS | **improved (−12.96% vs −28.31%)** |
| Trade density vs IS | **88% preserved (s8-D1 sizing-fix worked)** |
| C7 verdict | **`INSUFFICIENT_SAMPLE`** |
| OOS qualitative verdict | **`OOS_INDETERMINATE_BUT_DIRECTIONALLY_CONSISTENT`** |

IS-vs-OOS ratios: expectancy 0.44×; sharpe 0.70×; trades-per-year 0.88×; drawdown improved.

---

## 5. Main lesson

**One sentence:**
> *This was not a rejected fake edge and not a confirmed live edge; it is a promising but statistically under-sampled candidate.*

**Full reading.**
S10-D2 is the first multi-phase Tier-N candidate in this research stream to clear every IS-side gate cleanly (IS performance, full cost-stress matrix S0–S3, K10 universe diversification, all safety counters zero, 0 K-fires on IS) and produce a directionally-consistent OOS result.

- It is **NOT a rejected fake edge**: OOS pointed the same way as IS on every observable metric (positive sharpe, positive expectancy, positive net PnL, drawdown actually improved, safety counters still zero).
- It is **NOT a confirmed live edge**: OOS sample of 53 closed trades over the 3-year window was below the K9 threshold of 100 that the framework requires to convert *directional* evidence into *statistical* confirmation.
- The correct epistemic label is **`PROMISING_BUT_STATISTICALLY_UNDER_SAMPLED`**.

**Why this framing matters.**
- Calling it a "fake edge" (rejection) would discard the cleanest end-to-end research lifecycle in the stream.
- Calling it a "confirmed edge" (advancement) would require loosening K9, which the framework explicitly forbids.
- The third label — promising but under-sampled — is the only honest reading.

---

## 6. Structural lesson

**One sentence:**
> *OOS window length / sample size was the binding constraint, not cost-stress, not K10, not safety.*

**Full reading.**
The binding constraint that prevented S10-D2 from earning a CONFIRMED OOS verdict was the available OOS history length (3 years; 2023-01-01 to 2025-12-31). At a per-year trade frequency of **17.7 trades/year** (88% of the IS rate, confirming the s8-D1 sizing-fix lesson worked), a 3-year window yielded **53 trades** — structurally below the 100-trade K9 threshold.

| Candidate constraint | Binding here? |
|---|---|
| Cost-stress | NO (S0–S3 all positive; K12 did not fire) |
| K10 universe diversification | NO (avg corr 0.05 ≪ 0.50 threshold) |
| Safety (K6) | NO (all counters held zero across IS + 5 cost tiers + OOS) |
| **OOS window length** | **YES** |

**Operational implication.**
Future Tier-N candidates with similar trade-frequency characteristics (~20 trades/year) need an OOS window of **≥ 5 years** to comfortably clear K9 at S1. For 3-year OOS windows, only candidates with **> 33 trades/year per market** will reliably clear K9. This is a calibration insight about Tier-N candidate design relative to available history.

**S8-D1 relationship.**
S8-D1 parked because sizing produced 0 contracts for most signals at $100,000 starting cash. S10-D2 fixed that by raising to $500,000 starting cash. The S10-D2 trade-density ratio of 0.88× (OOS/IS) confirms the sizing fix worked. The fix opened a **different downstream constraint** (OOS window length), which is a structurally different problem.

---

## 7. Discipline lesson

**One sentence:**
> *The framework correctly parked instead of weakening K9 or claiming confirmation.*

**Full reading.**
At the moment of the P10 OOS verdict, three temptations existed and were all rejected:

1. **Lowering K9 from 100 to e.g. 50** "because the direction is encouraging" — *rejected* (P11 `explicit_blocked_actions`: *"DO NOT relax K9 threshold to confirm OOS"*).
2. **Waving the qualitative result through as a 'soft confirmation'** because all OOS metrics were positive — *rejected* (qualitative verdict explicitly enum-bounded to `OOS_INDETERMINATE_BUT_DIRECTIONALLY_CONSISTENT`, not `OOS_CONFIRMED`).
3. **Advancing to a longer-OOS rerun by quietly re-using existing chain artifacts as priors** without a fresh authorization — *rejected* (each future option requires separate sealed authorization).

The discipline that held was:
- **Pre-anchored verdict enums** (C7 has 3 fixed values; P11 has 4 fixed values, declared in Tier-N spec)
- **Pre-anchored thresholds** (K9 = 100 was set in Tier-N spec long before P10 ran)
- The cultural rule that *"lacking statistical confirmation is not a basis for advancement."*

**Why this matters long-term.**
Each time the framework refuses to loosen a threshold or widen an enum, it accumulates trust. Every candidate that gets a fair conservative verdict makes the next candidate's verdict more credible. Conversely, **one threshold-loosening event** would invalidate the chain-of-custody discipline for every prior verdict (s7-D1 reject, s8-D1 park, s9 park, s10-D1 park, s10-D2 park) and call into question whether any future PASS verdict actually means PASS.

---

## 8. Future research options (listed; NONE pre-approved)

Ordered by informational gain per unit of new scope/cost:

| # | Option | Cost | Information | Reuses |
|---|---|---|---|---|
| 1 | **`oos_cost_stress_sweep`** | lowest | Tests whether IS-side cost-robustness survives the OOS regime; orthogonal evidence to K9 sample-size | existing OOS cache + OOS driver |
| 2 | **`s11_d1_mnq_single_instrument_fallback`** | medium | Tests whether single-instrument simpler universe sidesteps the multi-asset sample-density problem | S11-D1 Tier-N spec already sealed at parallel-session `9c630886` |
| 3 | **`longer_oos_window`** | medium-high | Direct attack on the binding constraint (window length) | strategy code + IS driver; requires Databento fetch for ~5 months of additional bars |
| 4 | **`fresh_candidate_different_markets_or_regime_overlay`** | highest | Maximum diversification of evidence | framework discipline patterns only |

**Each option requires a separate fresh sealed operator authorization. None is pre-approved by this report.**

---

## 9. No-live / No-Strategy-Lab / No-review_queue confirmation

| Item | Status | Reason |
|---|---|---|
| Live trading | `BLOCKED_AT_6_GATES` | Permanent invariant; cannot be lifted by any research verdict |
| Paper trading | `NOT_AUTHORIZED` | `verdict_never_means_live_ready`; no broker / paper-trade route for PARKED candidates |
| Strategy Lab promotion | `NEVER_PROMOTED` | Requires FRC + CONFIRMED OOS + live-readiness, none of which exist |
| review_queue mutation | `NEVER_INSERTED` | Strategy Lab operational artifact; PARKED candidates not queued |
| idea_memory mutation | `NEVER_MUTATED` | Production-side; PARKED research candidates do not write to it |
| Brokerage connection | `NEVER_CONNECTED` | `DO NOT call Databento API, QuantConnect, or any broker/exchange/wallet API` |

---

## 10. Sealed-chain inventory referenced

| Artifact | Seal (first 16) |
|---|---|
| Tier-N spec | `f5ca5ee63024e9c8` |
| Plan-lock | `ba8bf954d44b373c` |
| Phase-2 plan | `7a48ad64236971e6` |
| P6 IS diagnostic | `e6cdc7c68a9e2b7b` |
| P6.5 cost-stress | `04351ca093ec20b0` |
| P7 IS decision memo | `87baa6e8c4cc1eb4` |
| K10 pairwise dependence | `8c620cc5bfe53f71` |
| P10 OOS gate | `4038e5334feba9ea` |
| P11 PARK memo | `e121b82b411697c7` |
| OOS scope reconciliation (this session) | `c57bb806ca56e158` |
| Lifecycle park report (this session) | `8d59e94a736aa82d` |

---

## 11. Negative invariants (all True)

`no_lessons_md_modification` · `no_lessons_md_staging` · `no_lessons_md_commit` · `no_databento_call` · `no_databento_api_key_access` · `no_data_fetch` · `no_oos_re_run` · `no_p10_re_run` · `no_p11_modification` · `no_oos_driver_modification` · `no_in_sample_driver_modification` · `no_runner_harness_modification` · `no_cache_modification` · `no_strategy_code_modification` · `no_canonical_k10_modification` · `no_simulator_run` · `no_backtest_run` · `no_signal_compute` · `no_strategy_lab_invoked` · `no_candidate_promoted` · `no_brokerage_connection` · `no_orders_created` · `no_paper_or_live_trade` · `no_review_queue_mutation` · `no_idea_memory_mutation` · `no_tier_n_spec_modification` · `no_plan_lock_modification` · `no_phase2_plan_modification` · `no_runbook_modification` · `no_pipeline_manifest_modification` · `no_decisions_md_modification` · `no_gitignore_modification` · `no_claude_md_modification` · `no_branch_change` · `no_git_push` · `no_s7_artifact_modified` · `no_s8_d1_artifact_modified` · `no_s9_artifact_modified` · `no_s10_d1_artifact_modified` · `no_s11_d1_artifact_modified` · `no_orb_artifact_modified` · `no_step_30_cost_constant_modified` · `no_threshold_loosening` · `no_k9_threshold_relaxation_proposed` · `no_frc_grant` · `no_live_readiness_claim` · `no_profitability_claim` · `no_pre_approval_of_future_options` · `no_key_leakage` · `no_external_network_call`

---

## 12. Labels

- `S10_D2_TERMINAL_LESSON_SEALED_REPORT_COMPLETE`
- `LESSONS_MD_LEFT_UNTOUCHED`
- `OOS_SAMPLE_LIMITATION_RECORDED`
- `PROMISING_BUT_NOT_CONFIRMED_RECORDED`
- `FRAMEWORK_DISCIPLINE_RECORDED`
- `NOT_FAKE_EDGE_NOT_CONFIRMED_EDGE`
- `BINDING_CONSTRAINT_OOS_WINDOW_LENGTH`
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

## 13. Seal

```
seal_method = sha256 over json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False) EXCLUDING report_seal_sha256 + seal_method

report_seal_sha256 = <see JSON report_seal_sha256 field>
```

**S10-D2 terminal lesson sealed. `lessons.md` untouched. Promising-but-not-confirmed status durably recorded. Trading: PAUSED. Live: BLOCKED_AT_6_GATES. FRC never granted. Advisory label permanent: `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE`.**
