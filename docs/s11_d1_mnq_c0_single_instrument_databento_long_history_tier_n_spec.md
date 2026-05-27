# S11-D1 Tier-N specification (sealed)

**Candidate record id:** `s11-d1-mnq-c0-single-instrument-databento-long-history`
**Phase prefix:** `PHASE2-S11-D1-MNQ-SI`
**Algo version:** `s11_d1_v0_1_0`
**Authored (UTC):** `2026-05-27T03:58:44.087523Z`
**Spec lifecycle state:** SEALED
**Report seal sha256:** `077e29e62f23dbc31823bad8447e5ef8d6f1a8c350d4f0c130c4f8f08be61a24`

## 1. Candidate purpose

Author a sealed Tier-N specification for a single-instrument MNQ.c.0 fallback research candidate, following the parallel-session selection plan at commit 556ab3f (which recommended T1: MNQ.c.0-only single-instrument on the existing audit-clean CSV) and following the S10-D2 PARK at commit 23c7164 (status PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED). The purpose is to evaluate whether a single-instrument design on MNQ.c.0 produces a different trade-density profile and a different OOS sample-sufficiency outcome than the S10-D2 4-market portfolio produced. This is a research diagnostic only. No promotion. No live trading. No paper trading. No FRC. No profitability claim.

## 2. Why MNQ.c.0 single-instrument fallback is being tested

- S10-D2 (cross-asset Donchian no-pyramid reparam-cap on NQ+GC+ZN+CL at $500,000 starting cash) parked at OOS because closed_trades=53 over the 3-year OOS window fell below the K9 threshold of 100. The verdict was INSUFFICIENT_SAMPLE / OOS_INDETERMINATE_BUT_DIRECTIONALLY_CONSISTENT.
- The parallel-session selection plan at 556ab3f explicitly identified MNQ.c.0 as the load-bearing usable finding preserved from the s10-D1 MNQ+MGC park (commit 1a9acec): MNQ.c.0 passed both s10-D1 audit variants cleanly (0 calendar gaps > 5 days; 0 consecutive abs-log-return violations; max single-day abs-log-return 0.1164; is_pct_observed = 1.2365).
- A single-instrument design eliminates by construction the per-market dominance pathology observed in s9 (USO -$1,177 of -$1,335 portfolio) and s7 D1 (USO +$96k of portfolio's only positive contribution).
- MNQ.c.0 has a structurally different cost profile from NQ (1/10th the contract size and tick value), which may produce different cost-stress sensitivity than S10-D2's NQ leg.
- Zero new data fetch is required: the sealed MNQ.c.0 CSV (sha 8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e; 2066 rows; 2019-05-13 to 2025-12-29) is already on disk and audit-clean. One-cycle scope.
- If S11-D1 produces a clean IS verdict and a clean OOS verdict with closed_trades >= 100, that is one piece of evidence — research only — that the underlying Donchian-on-equity-index-futures mechanic may have generalized across the IS/OOS split. If it produces INSUFFICIENT_SAMPLE on either side, the verdict is INDETERMINATE without any retroactive recovery of S10-D2's verdict.

## 3. S10-D2 lessons inherited (byte-equivalent unless noted)

- Donchian 55-day entry / 20-day exit channels (byte-equivalent to S10-D2 main.py CONFIG).
- Wilder ATR(20) for true range; 2N stop placement (byte-equivalent).
- 1% portfolio equity risk per unit, sized to ATR stop (byte-equivalent).
- max_units_per_market = 1 (no-pyramid invariant; byte-equivalent).
- AMB6 filter NONE (no additional gating; byte-equivalent).
- Cost-stress matrix S0/S1/S2/S3/S4 (5 tiers; byte-equivalent to S10-D2 CONFIG['cost_stress_tiers']).
- S1 baseline cost tier (default; byte-equivalent).
- RTH-only filter (per-market windows; for MNQ: 09:30-16:00 ET like NQ).
- Long+short bi-directional Donchian (long entry on N-day high; short entry on N-day low; byte-equivalent).
- Closed-trades portfolio count is the K9 / A1 evaluation unit (>=100 threshold; UNCHANGED).
- Sealed-chain verification framework: every phase produces a LESSON_HUNTER_004 canonical-seal report.
- Native OOS driver pattern (sibling file out_of_sample_driver.py) from S10-D2 P3.6 BUILD-EXTENSION — adopt at P3 BUILD time, NOT as a retrofit.
- C7 closed verdict enum: FAIL_SAFETY / INSUFFICIENT_SAMPLE / READY_FOR_LONGER_BACKTEST (never live-ready).
- 6-gate permanent live-block. Trading PAUSED. Live BLOCKED_AT_6_GATES. FRC never granted.
- Conservative interpretation discipline: positive metrics do NOT imply live-readiness; OOS pass is a research truth-test, not an approval to trade.

## 4. What is intentionally different from S10-D2

- UNIVERSE: {MNQ.c.0} only. S10-D2 was {NQ, GC, ZN, CL} (4 markets). LOCKED.
- STARTING_CASH: $50,000 (sized for MNQ's smaller contract). S10-D2 was $500,000 sized for NQ standard contract. The ratio reflects MNQ contract notional being ~1/10th of NQ.
- DATA_SOURCE: existing sealed MNQ.c.0 CSV at data/s10_d1_mnq_mgc_databento_long_history/raw/. S10-D2 used per-month .dbn.zst from data/databento_cache/. Different file format (CSV vs DBN), same upstream vendor (Databento), same schema family (ohlcv-1d for S11-D1 vs ohlcv-1m for S10-D2). NOTE: S10-D2 aggregated 1m bars to RTH daily; S11-D1 reuses already-daily CSV. The aggregation step is therefore DIFFERENT (none required); RTH already applied upstream.
- DATA_WINDOW: IS 2019-05-13 → 2023-12-29 (~4.6 years); OOS 2024-01-02 → 2025-12-30 (~2 years). S10-D2 was IS 2013-01-01 → 2022-12-30 (10 years) / OOS 2023-01-01 → 2025-12-31 (3 years). MNQ.c.0 instrument did not exist before 2019-05-06, so the IS window is structurally shorter.
- COST_MODEL: MNQ tick=0.25 index points / $0.50 per tick. S10-D2 NQ was tick=0.25 points / $5.00 per tick (10x). Other S10-D2 markets had their own ticks. Single-instrument single tick scale.
- PER_MARKET_CAP_TRACKER: NOT APPLICABLE for single-instrument. S10-D2 used PortfolioCapTracker(max_total_units=4, per_market_cap=1). S11-D1 uses trivially max_total_units=1 (only one instrument exists in the universe).
- CROSS_ASSET_DIVERSIFICATION: NONE by construction. S10-D2 had 4 asset classes. S11-D1 is single equity-index futures instrument. effective_independent_bets = 1 trivially.
- GC/ZN/CL: ABSENT from S11-D1. Per S10-D2 P11 PARK precedent: 'GC contributed -$345 over 10y IS (49 trades). Strategy edge is concentrated in CL/ZN/NQ; GC contributes diversification with near-zero realized return.' S11-D1 deliberately tests the NQ-leg / equity-index-futures mechanic in isolation.
- S10-D2 P3.6 BUILD-EXTENSION RETROFIT: AVOIDED at S11-D1. The S10-D2 OOS driver was added in a P3.6 retrofit (separate BUILD-EXTENSION) after the OOS-driver omission was discovered. S11-D1 authors the OOS driver as a sibling file at P3 BUILD time alongside the IS driver.
- ADVANCED-OOS-COST-STRESS: still NOT BUILT at SEAL. S10-D2 evaluated cost-stress at IS (P6.5) but never at OOS. S11-D1 may follow the same pattern (defer to a future research option) OR include OOS-cost-stress in the BUILD scope; deferred to SEAL-time decision.

## 5. Data requirements

| Field | Value |
|---|---|
| `vendor` | Databento |
| `dataset` | GLBX.MDP3 |
| `schema` | ohlcv-1d |
| `stype_in` | continuous |
| `symbol` | MNQ.c.0 |
| `primary_artifact` | data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_c_0_ohlcv_1d_20190513_20251230.csv |
| `primary_artifact_sha256_required` | 8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e |
| `primary_artifact_row_count_required` | 2066 |
| `primary_artifact_window_observed` | 2019-05-13, 2025-12-29 |
| `fresh_fetch_required` | False |
| `fresh_fetch_authorized_by_this_spec` | False |
| `audit_pre_existing` | True |
| `audit_anchors_inherited_from_s10_d1` | {"strict_audit_seal": "fd5cd136891638d2a1338850b616d000b969c7b46ce8c12365ba9498855e5865", "holiday_aware_audit_seal": "5f0258117cf35afa17ada593d464a0fc941e87c95bc52b76d54b8d719ee34686", "audit_verdict_for_mnq": "CLEAN (0 gaps > 5 days; max abs-log-return 0.1164; is_pct_observed 1.2365)"} |
| `secondary_data_authorized_by_this_spec` | False |
| `alternate_symbols_authorized_by_this_spec` | False |
| `alternate_schema_authorized_by_this_spec` | False |
| `alternate_vendor_authorized_by_this_spec` | False |

## 6. IS / OOS split plan

- **In-sample window:** 2019-05-13 → 2023-12-29 (~4.6 years)
- **Out-of-sample window:** 2024-01-02 → 2025-12-30 (~2.0 years)

IS start = first available MNQ.c.0 trading date (instrument launched 2019-05-06; first daily bar 2019-05-13 per the sealed CSV). IS end = 2023-12-29 (last trading day of 2023). OOS start = 2024-01-02 (first 2024 trading day). OOS end = 2025-12-30 (last available in sealed CSV). Inherits byte-equivalent split from the parallel-session s10-D1 sealed Tier-N spec at commit 9040429.

- OOS inspection blocked during IS phase: **YES**
- OOS evaluation uses native OOS driver: **YES** (lesson from S10-D2 P3.6 BUILD-EXTENSION)
- No train/validate/test, no purged k-fold, no walk-forward, no parameter tuning, no threshold loosening.

## 7. Entry/exit logic boundary (LOCKED at SEAL)

**Mechanic family:** F1 long+short bi-directional Donchian, no pyramid, ATR-stop, 1% per-trade risk

**Inheritance:** byte-equivalent to S10-D2 main.py CONFIG (Donchian 55/20; Wilder ATR(20); 2N stop; 1% risk; max_units=1; AMB6 NONE)

| Aspect | Value |
|---|---|
| `long_entry_signal` | Daily close > prior 55-day high (Donchian-55 upper band breakout) |
| `short_entry_signal` | Daily close < prior 55-day low (Donchian-55 lower band breakout) |
| `long_exit_signal` | Daily close < prior 20-day low (Donchian-20 lower band crossing) OR stop hit |
| `short_exit_signal` | Daily close > prior 20-day high (Donchian-20 upper band crossing) OR stop hit |
| `stop_method` | 2 * Wilder ATR(20) below entry (long) or above entry (short); set at entry; trail/lock per s10-D2 byte-equivalent (trailing per 2N method) |
| `pyramid_method` | NONE. max_units_per_market = 1 (no-pyramid invariant). Same as S10-D2. |
| `position_sizing` | 1% portfolio equity risk per unit; contracts = floor((0.01 * equity) / (ATR_entry * tick_value_usd)) |
| `tick_value_usd` | 0.5 |
| `tick_size_points` | 0.25 |
| `dollar_per_point` | 2.0 |
| `contract_multiplier` | MNQ: $2 * Nasdaq index value per point |
| `rth_window` | {"open_h": 9, "open_m": 30, "close_h": 16, "close_m": 0, "tz": "America/New_York"} |
| `intraday_data_used` | False |
| `daily_bars_only` | True |
| `roll_method` | Continuous front-month per Databento stype_in=continuous (vendor-side); no operator-side roll override |
| `amb6_filter` | NONE (preserved from S10-D2 NONE invariant) |
| `regime_overlay` | NONE |
| `correlation_filter` | NOT APPLICABLE (single instrument) |
| `vol_targeting` | NONE (not vol-targeting mechanic family) |
| `leverage_cap` | implicit via 1% per-trade risk sizing; no separate C4 leverage cap (not vol-targeting) |
| `logic_modification_post_seal_forbidden` | True |
| `logic_modification_requires_fresh_candidate_record_id` | True |

## 8. Cost assumptions (LOCKED at SEAL)

- Tick size: 0.25 points; tick value: $0.5; $/point: $2.00
- Commission per round-trip (default): $0.74
- Fees per round-trip (default): $0.36
- Slippage entry/stop/exit ticks (default): 1 / 1 / 1
- Cost-stress tiers byte-equivalent to S10-D2: **True**

### Cost-stress tiers (S0..S4)

| Tier | cost_scalar | slippage_scalar | Note |
|---|---:|---:|---|
| `S0` | 0.0 | 0.0 | zero-cost ideal; tests if a profitable kernel exists |
| `S1` | 1.0 | 1.0 | baseline retail; commission + fees + slip @ 1.0x |
| `S2` | 1.5 | 1.5 | stressed retail; cost + slip @ 1.5x |
| `S3` | 2.0 | 2.0 | adversarial; cost + slip @ 2.0x |
| `S4` | 3.0 | 3.0 | extreme adversarial; cost + slip @ 3.0x |

**S0 edge pre-registration at SEAL:** POSITIVE (operator pre-registers that the strategy is expected to be net-profitable under S0 zero-cost conditions over the IS window; falsifiable by the IS diagnostic)

## 9. Minimum trade count requirements + K9 risk

- **K9 closed-trades threshold:** **100**
- K9 threshold modification forbidden: **True**

**Expected trade count estimate (IS window):**

DAILY DONCHIAN-55/20 ON A SINGLE INSTRUMENT OVER 4.6 YEARS IS HISTORICALLY SPARSE. S10-D2 NQ produced 54 trades over 10 years (~5.4/year); scaled to a 4.6y single-instrument IS window, the expected closed_trades is approximately 25-50 BEFORE accounting for differences in market regime, contract size, or MNQ.c.0-vs-NQ.c.0 specific behavior. THIS IS BELOW THE K9 THRESHOLD OF 100.

**K9 risk disclosure at SEAL:**

IS RESULT MAY FIRE K9. If IS closed_trades < 100, the IS verdict will be INSUFFICIENT_SAMPLE (not FAIL_SAFETY). The chain shall NOT relax K9; the appropriate response is to seal the INSUFFICIENT_SAMPLE verdict and consider fresh research options under separate authorizations. The K9 risk is explicitly disclosed at SEAL; pursuing this candidate accepts the structural possibility of an INSUFFICIENT_SAMPLE IS verdict.

**Mitigation options NOT pre-approved by this spec:**

- Switch mechanic family to F3 (RSI mean-reversion) -- would produce higher trade frequency but introduces s9-RSI-2 failure-mode inheritance risk. REQUIRES FRESH CANDIDATE_RECORD_ID; not authorized here.
- Switch mechanic family to F2 (vol-targeting monthly rebal) -- would not produce more trades (~10-12/year max). NOT recommended.
- Shorten Donchian periods (e.g., 20/10 instead of 55/20) -- would change strategy logic; REQUIRES FRESH CANDIDATE_RECORD_ID; not authorized here.
- Reduce starting cash to size more aggressively -- does not change trade count.
- Extend OOS / IS windows with fresh data -- requires separate Databento fetch authorization.

## 10. K9 / OOS confirmation rules

- **K9 definition:** K9 fires iff closed_trades_portfolio < 100
- **K9 evaluated at IS:** True
- **K9 evaluated at OOS:** True
- **K9 threshold inviolate:** True

**OOS CONFIRMED iff (conjunction):**

OOS is CONFIRMED only iff ALL of: (a) C7 verdict is READY_FOR_LONGER_BACKTEST, (b) OOS closed_trades >= 100, (c) OOS sharpe > 0, (d) OOS expectancy > 0, (e) OOS trade_curve_maxdd_pct <= -30%, (f) all safety counters zero, (g) no-pyramid invariant held, (h) starting_cash invariant held.

**OOS INDETERMINATE iff:**

OOS is INDETERMINATE iff K9 fires (closed_trades < 100) AND no safety counter fires AND headline metrics (sharpe, expectancy, net PnL) are positive. This matches the S10-D2 OOS verdict and is NOT a confirmation.

**OOS KILLED iff:**

OOS is KILLED iff any safety K-gate fires (K6, K7, K8) OR any performance K-gate fires (K1 sharpe<0, K2 expectancy<=0, K4 trade-curve maxdd > 50%) on OOS.

OOS pass does NOT promote to live. OOS pass does NOT promote to paper. OOS pass is research-diagnostic only.

## 11. Rejection rules (K-gates and DR-gates)

### K-gates

| K-gate | Trigger |
|---|---|
| `K1_sharpe_proxy_lt_0` | if sharpe_proxy_per_trade < 0 -> FAIL_SAFETY |
| `K2_expectancy_le_0` | if expectancy_per_trade_usd <= 0 -> FAIL_SAFETY |
| `K4_trade_curve_maxdd_gt_50` | if |trade_curve_maxdd_pct| > 50% -> FAIL_SAFETY |
| `K6_safety_warning_count_gt_0` | if all_safety_warnings_zero is False -> FAIL_SAFETY |
| `K7_correlation_or_filter_silently_introduced` | if any filter/regime/correlation gate is introduced post-SEAL -> FAIL_SAFETY |
| `K8_sealed_parent_drift` | if any sealed parent seal does not match the embedded constant -> FAIL_SAFETY |
| `K9_closed_trades_lt_100` | if closed_trades_portfolio < 100 -> INSUFFICIENT_SAMPLE (NOT FAIL_SAFETY) |
| `K10_avg_pairwise_corr` | NOT APPLICABLE (single instrument; trivially 1 within itself) |
| `K11_cap_binding_events_gt_1000` | if cap_binding_events > 1000 (mostly N/A for single instrument 1-contract; primarily diagnostic) |
| `K12_DR_fires_on_cost_stress` | if any DR2/DR3/DR4/DR5 fires across S0/S2/S3/S4 cost-stress sweep at P6.5-equivalent |

### DR rules (evaluated at cost-stress sweep)

| DR | Trigger |
|---|---|
| `DR2_tier_net_pnl_le_0` | if any non-baseline tier net_pnl <= 0 |
| `DR3_tier_sharpe_proxy_le_0` | if any non-baseline tier sharpe <= 0 |
| `DR4_tier_expectancy_le_0` | if any non-baseline tier expectancy <= 0 |
| `DR5_tier_closed_trades_lt_100` | if any non-baseline tier closed_trades < 100 |

- No threshold loosening under any circumstance: **TRUE**
- No DR redefinition post-SEAL: **TRUE**
- No filter introduction post-SEAL: **TRUE**
- No universe widening post-SEAL: **TRUE**
- No starting cash modification post-SEAL: **TRUE**
- No strategy parameter modification post-SEAL: **TRUE**
- FAIL_SAFETY outcomes are terminal for this `candidate_record_id`: **TRUE**

## 12. Promotion rules

**Promotion at any stage is OUT OF SCOPE for this `candidate_record_id`. The 6-gate permanent live-block applies regardless of any verdict.**

- `permanent_live_block`: True
- `permanent_paper_block`: True
- `live_promotion_blocked_at_6_gates_permanently`: True
- `no_verdict_unblocks_live`: True
- `no_verdict_unblocks_paper_via_broker`: True
- `no_verdict_unblocks_frc`: True
- `no_verdict_unblocks_strategy_lab_promotion`: True
- `no_verdict_unblocks_review_queue_mutation`: True
- `promotion_at_any_stage_is_OUT_OF_SCOPE_FOR_THIS_RECORD_ID`: True
- `research_diagnostic_only`: True
- `diagnostic_only_not_live_grade_label`: True

## 13. Files allowed to be created or modified

### This SEAL turn creates exactly:

- `docs/s11_d1_mnq_c0_single_instrument_databento_long_history_tier_n_spec.md`
- `reports/s11_d1_mnq_c0_single_instrument_databento_long_history_tier_n_spec_sealed.json`

### Future phases may create (each under separate authorization):

#### `p3_build_runner_harness_and_drivers`
- `external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_runner_harness/__init__.py`
- `external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_runner_harness/main.py`
- `external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_runner_harness/execution_guard.py`
- `external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_runner_harness/in_sample_driver.py`
- `external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_runner_harness/out_of_sample_driver.py`

#### `p3_build_tests_scaffold`
- `external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_runner_harness/tests/__init__.py`
- `external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_runner_harness/tests/conftest.py`
- `external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_runner_harness/tests/fixtures/synthetic_mnq_daily.csv`
- `external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_runner_harness/tests/test_smoke_t1_t15.py`
- `external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_runner_harness/tests/test_oos_driver_invariants.py`

#### `p3_build_reports_sealed`
- `reports/external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_runner_build_report.json`
- `reports/external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_runner_build_report.md`
- `reports/external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_in_sample_driver_build_report.json`
- `reports/external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_in_sample_driver_build_report.md`
- `reports/external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_out_of_sample_driver_build_report.json`
- `reports/external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_out_of_sample_driver_build_report.md`

#### `p4_synthetic_smoke_report`
- `reports/external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_smoke_t1_t15_report.json`
- `reports/external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_smoke_t1_t15_report.md`

#### `p6_is_diagnostic_sealed`
- `reports/external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_in_sample_diagnostic_result_sealed.json`
- `reports/external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_in_sample_diagnostic_result_sealed.md`

#### `p6_5_cost_stress_matrix_sealed`
- `reports/external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_cost_stress_matrix_result_sealed.json`
- `reports/external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_cost_stress_matrix_result_sealed.md`

#### `p7_decision_memo_sealed`
- `reports/s11_d1_p7_decision_memo_sealed.json`
- `reports/s11_d1_p7_decision_memo_sealed.md`

#### `p10_oos_gate_sealed`
- `reports/s11_d1_p10_oos_gate_sealed.json`
- `reports/s11_d1_p10_oos_gate_sealed.md`

#### `p11_lifecycle_decision_sealed`
- `reports/s11_d1_p11_decision_memo_sealed.json`
- `reports/s11_d1_p11_decision_memo_sealed.md`

Naming and ordering locked at SEAL. Deviation from authorized file list requires explicit per-phase authorization.

## 14. Files explicitly forbidden from modification

(This turn AND all future S11-D1 turns, unless a separate authorization names the specific file as its target.)

- All S10-D2 sealed artifacts (commit 23c7164 PARK and all preceding sealed reports in the S10-D2 chain).
- All S10-D2 source files (in_sample_driver.py, out_of_sample_driver.py, main.py, execution_guard.py, test_smoke_t1_t15.py, test_oos_driver_invariants.py, conftest.py, synthetic CSV fixtures, __init__.py).
- All s10-D1 MNQ+MGC sealed artifacts (commit 1a9acec park and the full s10-D1 chain).
- All s10-D1 source files (loaders, validators, signal modules, simulators, aggregators, fetch tools, audit tools).
- All s9 RSI-2 ETF-proxy sealed artifacts.
- All s7 D1 ETF-proxy sealed artifacts.
- All B005_NNN sealed artifacts.
- All B006_001 sealed artifacts (LESSON_B006_001_002/003/004 anchor).
- All B006_002 sealed artifacts (LESSON_B006_002_001/002 anchor; DR11 C4-enforcement precedent).
- All s8-D1 cross-asset Donchian sealed artifacts.
- All s7-D1 (original s7-D1 cross-asset Donchian runner, not the ETF-proxy variant).
- T8 ETF-proxy family-park memo.
- S10-D1 micro availability probe memo.
- next_research_track_selection_plan_after_*_park.md files (parallel-session selection plans).
- review_queue.json.
- production idea_memory directory.
- All Strategy Lab artifacts.
- All ORB branch artifacts and Step 30 cost constants.
- obsidian-trade-logger / obsidian directory and contents.
- brain_memory/projects/trading_bot/lessons.md (this dirty tracked file is parallel-session work; explicitly off-limits this turn and in all future S11-D1 turns unless a separate authorization names it as the target).
- CLAUDE.md, docs/decisions.md (if exists), RUNBOOK, pipeline_manifest, .gitignore.
- Any data/databento_cache/ or data/databento_cache_oos/ or data/databento_cache_is_only/ contents (those are S10-D2-lineage caches; S11-D1 reuses the s10-D1 sealed CSV instead).
- Any candidate_record_id namespace other than s11-d1-mnq-c0-single-instrument-databento-long-history.

## 15. Exact next phase

NONE. This SEAL document does NOT pre-approve any subsequent phase. The next operator authorization shall reference this sealed Tier-N spec by exact path and shall be one of: (a) AUTHORIZE S11-D1 P1 plan-lock (locks the spec for build); (b) AUTHORIZE alternative track selection (rejects S11-D1 and picks another T2-T9 option from the selection plan at 556ab3f); (c) AUTHORIZE deferral (no S11-D1 work for now). The expected default forward path is (a) AUTHORIZE S11-D1 P1 plan-lock, but it is NOT pre-approved.

- No phase pre-approved by this SEAL: **TRUE**
- P1 plan-lock requires separate authorization: **TRUE**
- P3 BUILD requires separate authorization: **TRUE**
- P6 IS requires separate authorization: **TRUE**
- P10 OOS requires separate authorization: **TRUE**

## Parent references (READ-ONLY; not modified by this turn)

- `s11_d1_selection_plan_commit`: `556ab3f`
- `s11_d1_selection_plan_path`: `docs/next_research_track_selection_plan_after_s10_d1_park.md`
- `s10_d1_mnq_mgc_park_commit`: `1a9acec`
- `s10_d1_mnq_mgc_park_report_seal_sha256`: `32c1a87146264197fd852e53ba45baf6d6d45e40355b716e5a4d41a08edf1b2f`
- `s10_d1_mnq_mgc_tier_n_spec_commit`: `9040429`
- `s10_d1_mnq_mgc_step02c_audit_seal_sha256`: `fd5cd136891638d2a1338850b616d000b969c7b46ce8c12365ba9498855e5865`
- `s10_d1_mnq_mgc_step02c_holiday_aware_seal_sha256`: `5f0258117cf35afa17ada593d464a0fc941e87c95bc52b76d54b8d719ee34686`
- `s10_d1_micro_availability_probe_memo_sha256`: `76dcb833f89d3044547e0e361e03f39ae325a22a5c9c06baf1ec0f2e9df213fe`
- `s10_d2_park_commit`: `23c7164`
- `s10_d2_park_status`: `PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED`
- `s10_d2_p11_park_memo_seal_sha256`: `e121b82b411697c7d06bbe9ee1cc2df29c04df76712873ed0fbfd76f25fab1cb`
- `s10_d2_p7_decision_memo_seal_sha256`: `87baa6e8c4cc1eb47c1345b97990eab86d5cefb37636e9fe57a029506d398c05`
- `s10_d2_p6_is_diagnostic_seal_sha256`: `e6cdc7c68a9e2b7b6d749b73ff433e585c9de55890af5dce3dca51d74430c1b8`
- `s10_d2_p6_5_cost_stress_seal_sha256`: `f9a34674de4f7fdf8098b39959032d152bf2282e9ad57cedd68bc33cee2099ab`
- `s10_d2_p10_oos_gate_seal_sha256`: `4038e5334feba9ea61b91dcb47287a7a8f9f8fdfd8ad35990866bc9fbd106137`
- `s10_d2_phase2_plan_seal_sha256`: `7a48ad64236971e6fd2a2fa58ab7ab746a71543778ed0a868f3cdf9ff8f74ac3`
- `mnq_c0_daily_csv_path`: `data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_c_0_ohlcv_1d_20190513_20251230.csv`
- `mnq_c0_daily_csv_sha256`: `8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e`
- `mnq_c0_daily_csv_row_count`: `2066`
- `mnq_c0_daily_csv_window_observed`: `['2019-05-13', '2025-12-29']`

## Status / labels

- `trading_status`: PAUSED
- `live_status`: BLOCKED_AT_6_GATES
- `research_label`: DIAGNOSTIC_ONLY_NOT_LIVE_GRADE
- `spec_lifecycle_state`: SEALED

**Labels:**

- `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE`
- `TIER_N_SEALED_SPEC`
- `S11_D1_MNQ_SINGLE_INSTRUMENT_FALLBACK`
- `NOT_LIVE_READY`
- `NOT_PAPER_READY`
- `NO_FRC_GRANTED`
- `NO_PROFITABILITY_CLAIM`
- `NO_NEXT_PHASE_PRE_APPROVED`
- `S10_D2_TREATED_AS_PARENT_REFERENCE_ONLY`
- `S10_D2_NOT_REVIVED_NOT_MODIFIED_NOT_REINTERPRETED`
- `K9_THRESHOLD_INVIOLATE`
- `OOS_INDETERMINATE_RISK_ACKNOWLEDGED_AT_SEAL`

## Hard boundaries held (this SEAL turn)

- no_backtest: True
- no_broker_exchange_api: True
- no_commit_in_orchestrator: True
- no_d5_b005_001_nke_revival: True
- no_data_fetch: True
- no_databento_api_call: True
- no_k9_relaxation: True
- no_lessons_md_touched: True
- no_live_trading: True
- no_network_call: True
- no_obsidian_touched: True
- no_oos_inspection: True
- no_paper_trading: True
- no_phase_pre_approval: True
- no_profitability_claim: True
- no_promotion_to_live: True
- no_promotion_to_paper: True
- no_qc_runtime: True
- no_review_queue_mutation: True
- no_s10_d1_modification: True
- no_s10_d2_modification: True
- no_s10_d2_reinterpretation: True
- no_s10_d2_revival: True
- no_s9_or_s7_or_b006_revival: True
- no_safety_gate_relaxation: True
- no_signal_computation: True
- no_simulator: True
- no_source_modification: True
- no_strategy_execution: True
- no_threshold_loosening: True
- no_unrelated_tracked_file_modified: True

## Seal metadata

- Report seal sha256: `077e29e62f23dbc31823bad8447e5ef8d6f1a8c350d4f0c130c4f8f08be61a24`
- Seal method: LESSON_HUNTER_004 canonical roundtrip
- Reseal verified on disk: YES
