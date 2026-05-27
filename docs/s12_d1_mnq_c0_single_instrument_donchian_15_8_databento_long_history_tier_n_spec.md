# S12-D1 Tier-N specification (sealed)

**Candidate record id:** `s12-d1-mnq-c0-single-instrument-donchian-15-8-databento-long-history`
**Phase prefix:** `PHASE2-S12-D1-MNQ-DONCHIAN-15-8`
**Algo version:** `s12_d1_v0_1_0`
**Authored (UTC):** `2026-05-27T14:38:51.562701Z`
**Spec lifecycle state:** SEALED
**Report seal sha256:** `07c3200b5e23ab88e864f92926b83ded033a3d66c0e37e8cf8555985ad8f3b48`
**Seal method:** LESSON_HUNTER_004 canonical roundtrip
**Reseal verified on disk:** YES

## 1. Candidate purpose

Author a sealed Tier-N specification for a single-instrument MNQ.c.0 fresh-candidate research diagnostic using a deliberately faster Donchian channel (15/8) than s11-d1 v1's Donchian-55/20. The candidate's load-bearing structural property is a faster signal frequency intended to bring the expected IS-window closed-trade count above the K9 floor of 100 (s11-d1 v1 disclosed expected ~25-50 trades; s12-d1 expects ~80-200). The s11-d1 v1 SEAL explicitly stated that shortening Donchian periods requires a fresh `candidate_record_id`; this SEAL satisfies that clause structurally. Research diagnostic only. No promotion. No live trading. No paper trading. No FRC. No profitability claim.

## 2. Why Donchian-15/8 fresh candidate is being tested

s11-d1 v1 sealed Tier-N spec at commit `9c63088` (seal sha `077e29e62f23dbc31823bad8447e5ef8d6f1a8c350d4f0c130c4f8f08be61a24`) section 9 "Mitigation options NOT pre-approved by this spec" states verbatim: *"Shorten Donchian periods (e.g., 20/10 instead of 55/20) -- would change strategy logic; REQUIRES FRESH CANDIDATE_RECORD_ID; not authorized here."* s12-d1 honors that clause: it is a structurally fresh `candidate_record_id`, not a revision of s11-d1.

The Donchian-15/8 choice is targeted at K9-mitigation: s11-d1 v1 disclosed expected closed_trades over 4.6y IS of ~25-50 (below K9 floor of 100); the faster channel is expected to produce 80-200 trades (borderline-to-clearing). The trade-off is elevated DR10 turnover-cost-explosion risk; the operator mitigated this at SEAL via DA4=B (raising START_CASH from $50k to $100k), which roughly halves contracts-per-trade for a given ATR and reduces per-dollar commission/slip pressure. The DR10 thresholds themselves remain byte-equivalent (no DR redefinition).

## 3. s11-d1 v1 lessons inherited (byte-equivalent unless noted)

- Donchian channel mechanic with ATR-based stop and per-trade risk sizing is structurally sound F1 family on MNQ.c.0 futures (byte-equivalent).
- Wilder ATR(20) + 2N stop placement (byte-equivalent; DA1=A, DA2=A).
- 1% portfolio equity risk per unit (byte-equivalent; DA3=A).
- `max_units_per_market = 1` (no-pyramid invariant; byte-equivalent).
- Long+short bi-directional Donchian (byte-equivalent).
- RTH-only 09:30-16:00 ET filter (byte-equivalent; DA12=A).
- Closed-trades portfolio count is the K9 evaluation unit (>=100 threshold; inviolate; DA13/DA14 byte-equivalent).
- Sealed-chain verification framework: every phase produces a LESSON_HUNTER_004 canonical-seal report.
- Native OOS driver pattern (sibling `out_of_sample_driver.py` at P3 BUILD time, not retrofit).
- C7 closed verdict enum: FAIL_SAFETY / INSUFFICIENT_SAMPLE / READY_FOR_LONGER_BACKTEST (never live-ready).
- 6-gate permanent live-block. Trading PAUSED. Live BLOCKED_AT_6_GATES. FRC never granted.
- `oos_confirmation_definition` condition (e) magnitude-based form per s11-d1 rev2 (`c110fd4`) byte-equivalent.
- Conservative interpretation discipline: positive metrics do NOT imply live-readiness; OOS pass is a research truth-test, not approval to trade.

## 4. What is intentionally different from s11-d1 v1

| Aspect | s11-d1 v1 (sealed at `9c63088`) | s12-d1 (this SEAL) | Reason |
|---|---|---|---|
| Donchian entry channel | **55 days** | **15 days** | LOCKED at PLAN; load-bearing K9 mitigation |
| Donchian exit channel | **20 days** | **8 days** | LOCKED at PLAN; load-bearing K9 mitigation |
| Expected IS trade count | ~25-50 (fires K9) | ~80-200 (borderline-to-clearing) | structural test of K9-mitigation hypothesis |
| DR10 turnover risk | low | ELEVATED (load-bearing trade-off accepted at PLAN) | faster channel raises annual turnover materially |
| `START_CASH_USD` | $50,000 | **$100,000** | **DA4=B revised at SEAL** for DR10 mitigation; halves contracts-per-trade for given ATR |
| All other parameters | -- | byte-equivalent carry via DRAFT defaults A for DA1/DA2/DA3/DA5/DA6/DA7/DA8/DA9/DA10/DA11/DA12/DA13/DA14 | -- |

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
| `controller_side_databento_call_authorized_any_phase` | False |
| `databento_api_key_access_required_any_phase` | False |

## 6. IS / OOS split plan

- **In-sample window:** 2019-05-13 -> 2023-12-29 (~4.6 years; 1,443 rows audit-confirmed)
- **Out-of-sample window:** 2024-01-02 -> 2025-12-30 (~2.0 years; 622 rows structural only)
- **OOS inspection blocked during IS phase:** YES
- **OOS evaluation uses native OOS driver:** YES (sibling file at P3 BUILD time)
- **No train/validate/test, no purged k-fold, no walk-forward, no parameter tuning, no threshold loosening.**

## 7. Entry/exit logic boundary (LOCKED at SEAL)

**Mechanic family:** F1 long+short bi-directional Donchian, no pyramid, ATR-stop, 1% per-trade risk (LOCKED at PLAN; DRAFT did NOT reopen mechanic-family menu)

| Aspect | Value |
|---|---|
| `long_entry_signal` | Daily close > prior 15-day high (Donchian-15 upper band breakout) |
| `short_entry_signal` | Daily close < prior 15-day low (Donchian-15 lower band breakout) |
| `long_exit_signal` | Daily close < prior 8-day low (Donchian-8 lower band crossing) OR stop hit |
| `short_exit_signal` | Daily close > prior 8-day high (Donchian-8 upper band crossing) OR stop hit |
| `donchian_entry_channel_days_N` | **15** (LOCKED at PLAN; load-bearing departure from s11-d1 v1's 55) |
| `donchian_exit_channel_days_M` | **8** (LOCKED at PLAN; load-bearing departure from s11-d1 v1's 20) |
| `atr_window_days_P` | **20** (DA1=A; Wilder; carried byte-equivalent from s11-d1 v1) |
| `atr_method` | Wilder |
| `atr_stop_multiplier_K` | **2.0** (DA2=A; 2N stop; carried byte-equivalent from s11-d1 v1) |
| `stop_method` | 2 * Wilder ATR(20) below entry (long) or above entry (short); set at entry; trail/lock per s11-d1 v1 byte-equivalent (trailing per 2N method) |
| `pyramid_method` | NONE. max_units_per_market = 1 (no-pyramid invariant). |
| `per_trade_risk_pct` | **0.01** (DA3=A; 1.0% portfolio equity risk per unit) |
| `position_sizing_formula` | `contracts = floor((0.01 * equity) / (ATR_entry * tick_value_usd))` |
| `tick_value_usd` | 0.5 |
| `tick_size_points` | 0.25 |
| `dollar_per_point` | 2.0 |
| `contract_multiplier` | MNQ: $2 * Nasdaq index value per point |
| `rth_window` | DA12=A: `{"open_h": 9, "open_m": 30, "close_h": 16, "close_m": 0, "tz": "America/New_York"}` |
| `intraday_data_used` | False |
| `daily_bars_only` | True |
| `roll_method` | Continuous front-month per Databento `stype_in=continuous` (vendor-side); no operator-side roll override |
| `amb6_filter` | NONE |
| `regime_overlay` | NONE |
| `correlation_filter` | NOT APPLICABLE (single instrument) |
| `vol_targeting` | NONE (not vol-targeting mechanic family) |
| `leverage_cap` | implicit via 1% per-trade risk sizing; no separate C4 leverage cap (not vol-targeting); DR11 structurally absent |
| `logic_modification_post_seal_forbidden` | True |
| `logic_modification_requires_fresh_candidate_record_id` | True |

## 8. Cost assumptions (LOCKED at SEAL)

- Tick size: 0.25 points; tick value: $0.5; $/point: $2.00
- **`START_CASH_USD`: $100,000** (DA4=B revised at SEAL for DR10 mitigation)
- Commission per round-trip: $0.74 (DA8=A; byte-equivalent)
- Fees per round-trip: $0.36 (DA9=A; byte-equivalent)
- Slippage entry/stop/exit ticks: 1 / 1 / 1 (DA10=A; byte-equivalent)
- `WARMUP_DAYS`: 220 (DA11=A; `MAX(longest_lookback, 220)`)
- Cost-stress tiers byte-equivalent to s11-d1 v1 (DA7=A): **5-tier S0/S1/S2/S3/S4**

### Cost-stress tiers (S0..S4; DA7=A)

| Tier | cost_scalar | slippage_scalar | Note |
|---|---:|---:|---|
| `S0` | 0.0 | 0.0 | zero-cost ideal; tests if a profitable kernel exists |
| `S1` | 1.0 | 1.0 | baseline retail; commission + fees + slip @ 1.0x |
| `S2` | 1.5 | 1.5 | stressed retail; cost + slip @ 1.5x |
| `S3` | 2.0 | 2.0 | adversarial; cost + slip @ 2.0x |
| `S4` | 3.0 | 3.0 | extreme adversarial; cost + slip @ 3.0x |

**S0 edge pre-registration at SEAL:** POSITIVE (operator pre-registers that the strategy is expected to be net-profitable under S0 zero-cost conditions over the IS window; falsifiable by the IS diagnostic). Open question; no a-priori claim of magnitude.

## 9. Minimum trade count requirements + K9 risk (IS + OOS disclosures)

- **K9 closed-trades threshold:** **100**
- K9 threshold modification forbidden: **True**
- K9 evaluated at IS: **True**
- K9 evaluated at OOS: **True**
- K9 threshold inviolate at both IS and OOS: **True**

### 9.1 IS K9 risk disclosure at SEAL (carried byte-equivalent + Donchian-15/8 K9-mitigation hypothesis)

DAILY DONCHIAN-15/8 ON A SINGLE INSTRUMENT OVER 4.6 YEARS IS EXPECTED TO PRODUCE ~3-4x THE SIGNAL DENSITY OF DONCHIAN-55/20. s11-d1 v1 disclosed ~25-50 expected trades (below K9 floor); s12-d1 expects approximately **80 (low) / 140 (central) / 200 (high)** portfolio trades over the 4.6y IS window. The lower bound is below K9; the central and upper bounds clear the K9 floor.

IS RESULT MAY STILL FIRE K9 AT LOWER-BOUND TRADE-COUNT SCENARIOS. If IS closed_trades < 100, the IS verdict will be INSUFFICIENT_SAMPLE (not FAIL_SAFETY). The chain shall NOT relax K9; the appropriate response is to seal the INSUFFICIENT_SAMPLE verdict and consider further fresh research options under separate authorizations.

### 9.2 OOS K9 risk disclosure at SEAL (REC1 from addendum memo `538eaf3` incorporated; priority HIGH)

**OOS K9 EXPECTED TO FIRE.** Implied OOS trade count over 2.0y at IS rate is approximately **35-87 trades**, below K9 = 100. If OOS K9 fires, the OOS verdict will be OOS_INSUFFICIENT_SAMPLE or PARKED_SAFE_BUT_OOS_INDETERMINATE analogous to S10-D2 P11 PARK at `23c7164`. The chain shall NOT relax K9 at OOS; the appropriate response is to seal the INSUFFICIENT_SAMPLE / INDETERMINATE verdict and park the candidate. **Pursuing s12-d1 accepts the structural likelihood of an OOS PARK outcome.**

Reachability arithmetic:

| Window | Length (years) | Per-year rate (low / central / high) | Expected trades (low / central / high) | K9 status |
|---|---:|---|---|---|
| IS | 4.6 | 17.4 / 30.4 / 43.5 | 80 / 140 / 200 | central CLEARS K9 with margin; lower BORDERLINE |
| **OOS** | **2.0** | **(carried from IS rate)** | **35 / 61 / 87** | **STRUCTURALLY UNREACHABLE: all three estimates < K9 = 100** |

**Why OOS K9 cannot be solved by s12-d1's Donchian-15/8 choice:** the OOS window length is inherited byte-equivalent from s11-d1 v1 sealed spec at 2.0 years. Even the upper estimate of the DRAFT-documented IS trade-rate band (43.5 trades/year) scaled to 2.0y produces ~87 trades, still below K9=100. Extending the OOS window would require fresh Databento fetch plus a further-fresh `candidate_record_id`; both are out of scope for this SEAL.

**Candidate acceptance implication at SEAL:** Sealing this candidate via this SEAL turn explicitly accepts the structural likelihood that the s12-d1 lifecycle terminal verdict will be OOS PARK regardless of IS outcome. The candidate's research value lies in (a) testing the K9-mitigation IS hypothesis and (b) producing a reusable single-instrument Donchian-15/8 runner-harness scaffolding pattern -- NOT in producing an OOS-confirmed strategy.

**REC1 scope (disclosure only, NOT a DR redefinition):**
- REC1 does NOT alter DA1-DA14 resolutions
- REC1 does NOT alter DR9 or DR10 thresholds
- REC1 is documentation-completeness; the underlying parameters and DR semantics are byte-equivalent
- REC1 does NOT violate `no_dr_redefinition_post_seal` (it adds a disclosure record, not a threshold change)

### 9.3 DR10 risk disclosure at SEAL

DONCHIAN-15/8 RAISES ANNUAL TURNOVER MATERIALLY VS DONCHIAN-55/20. If S2 cost drag exceeds 5% of portfolio equity, DR10 fires REJECT_FAST. The operator mitigated this at SEAL via DA4=B (raising `START_CASH_USD` from $50k to $100k), which halves contracts-per-trade for a given ATR and reduces per-dollar commission/slip pressure. This is the load-bearing trade-off accepted at PLAN and explicitly addressed at SEAL.

## 10. K9 / OOS confirmation rules

- **K9 definition:** K9 fires iff `closed_trades_portfolio < 100`
- **K9 evaluated at IS:** True
- **K9 evaluated at OOS:** True
- **K9 threshold inviolate:** True

**OOS CONFIRMED iff (conjunction; s11-d1 rev2 magnitude-based form carried byte-equivalent):**

OOS is CONFIRMED only iff ALL of: (a) C7 verdict is READY_FOR_LONGER_BACKTEST, (b) OOS closed_trades >= 100, (c) OOS sharpe > 0, (d) OOS expectancy > 0, (e) OOS trade_curve_maxdd_pct >= -30% (equivalently |trade_curve_maxdd_pct| <= 30%; i.e., the realized OOS drawdown shall not exceed 30% in magnitude), (f) all safety counters zero, (g) no-pyramid invariant held, (h) starting_cash invariant held.

OOS pass does NOT promote to live. OOS pass does NOT promote to paper. OOS pass is research-diagnostic only.

## 11. Rejection rules (K-gates and DR-gates)

### K-gates

| K-gate | Trigger |
|---|---|
| `K1_sharpe_proxy_lt_0` | if sharpe_proxy_per_trade < 0 -> FAIL_SAFETY |
| `K2_expectancy_le_0` | if expectancy_per_trade_usd <= 0 -> FAIL_SAFETY |
| `K4_trade_curve_maxdd_pct_magnitude_gt_50` | if \|trade_curve_maxdd_pct\| > 50% (DA5=A) -> FAIL_SAFETY |
| `K6_per_symbol_dispersion` | NOT APPLICABLE (single instrument) |
| `K7_correlation_or_filter_silently_introduced` | if any filter/regime/correlation gate is introduced post-SEAL -> FAIL_SAFETY |
| `K8_sealed_parent_drift` | if any sealed parent seal does not match the embedded constant -> FAIL_SAFETY |
| `K9_closed_trades_lt_100` | if closed_trades_portfolio < 100 -> INSUFFICIENT_SAMPLE (NOT FAIL_SAFETY) |
| `K10_avg_pairwise_corr` | NOT APPLICABLE (single instrument) |
| `K11_cap_binding_events` | NOT APPLICABLE (F1 no leverage cap) |
| `K12_DR_fires_on_cost_stress` | if any DR2/DR3/DR4/DR5 fires across S0/S2/S3/S4 cost-stress sweep at P6.5-equivalent |

### DR rules

| DR | Trigger |
|---|---|
| `DR2_tier_net_pnl_le_0` | if any non-baseline tier net_pnl <= 0 |
| `DR3_tier_sharpe_proxy_le_0` | if any non-baseline tier sharpe <= 0 |
| `DR4_tier_expectancy_le_0` | if any non-baseline tier expectancy <= 0 |
| `DR5_tier_closed_trades_lt_100` | if any non-baseline tier closed_trades < 100 |
| `DR9` | `mnq_c0_only_data_continuity_integrity_check` thresholds 0.95/0.30/5/5 byte-equivalent (DA13=A) |
| `DR10` | `turnover_cost_explosion` annual_turnover>0.50 OR S2_cost_drag>0.05 byte-equivalent (DA14=A); **ELEVATED prior probability** vs s11-d1 v1; mitigated via DA4=B |

DR precedence chain (LOCKED at SEAL): `DR7 -> DR1 -> DR9 -> DR10 -> DR6 -> DR4 -> DR2 -> DR3 -> DR5` (carried byte-equivalent from s11-d1 v1; DR11 omitted because F1 has no leverage cap).

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

## 13. DRAFT ambiguities resolved at SEAL

| DA | Topic | Operator choice | Resolved value | Notes |
|---|---|---|---|---|
| DA1 | ATR stop window P | **A** | 20 | Wilder ATR(20) carried byte-equivalent |
| DA2 | ATR stop multiplier K | **A** | 2.0 | 2N stop carried byte-equivalent |
| DA3 | Per-trade risk percentage | **A** | 1.0% | carried byte-equivalent |
| DA4 | `START_CASH_USD` | **B (REVISED)** | **$100,000** | **REVISED FROM DRAFT DEFAULT $50k for DR10 mitigation** |
| DA5 | K4 max-drawdown threshold | **A** | 0.50 (50%) | carried byte-equivalent from s11-d1 v1 K4 formula |
| DA6 | Output schema name | **A** | `sparta.s12.d1.mnq_c0.donchian_15_8.diagnostic_run_report.v1` | LOCKED |
| DA7 | Cost-stress tier set | **A** | 5-tier S0..S4 | LOCKED non-negotiable |
| DA8 | Commission per round-trip | **A** | $0.74 | LOCKED |
| DA9 | Fees per round-trip | **A** | $0.36 | LOCKED |
| DA10 | Slippage entry/stop/exit ticks | **A** | 1/1/1 | LOCKED |
| DA11 | `WARMUP_DAYS` | **A** | 220 | `MAX(longest_lookback, 220)` |
| DA12 | RTH window | **A** | 09:30-16:00 ET America/New_York | LOCKED |
| DA13 | DR9 thresholds | **A** | 0.95/0.30/5/5 | LOCKED non-negotiable |
| DA14 | DR10 thresholds | **A** | `annual_turnover>0.50` OR `S2 cost drag>0.05` | LOCKED non-negotiable |

## 14. RUNTIME_INVARIANTS at SEAL (25 total; no DR11; no leverage cap)

7 B005_NNN framework:
- `no_live_trading` * `no_strategy_lab_promotion` * `no_review_queue_mutation` * `no_brokerage_connection` * `no_external_network` * `no_databento_at_runtime` * `no_production_signal`

4 B006_001 inherited:
- `no_strategy_optimization_authorized` * `no_profitability_claim` * `no_universe_membership_logic` * `no_dr_redefinition_post_seal`

2 B006_002 inherited (F1 has no leverage cap; leverage-cap-specific invariants NOT carried):
- `no_warmup_order_submission` * `dr6_warmup_contamination_blocked`

5 s10-d1-specific inherited:
- `no_continuous_roll_stitch_modification_post_seal` * `no_mcl_inclusion_under_long_history_scope` * `no_intraday_schema_ingest_under_daily_only_design` * `databento_api_key_read_from_env_only_never_logged_or_saved` * `no_pyramid_per_signal`

3 s11-d1-specific inherited:
- `single_instrument_universe_NO_widening_post_seal` * `no_substitution_of_any_symbol_into_this_universe_post_seal` * `mnq_c0_csv_reuse_byte_equivalent_no_fresh_fetch`

4 NEW s12-d1-specific (LOCKED at SEAL):
- `donchian_15_8_locked_at_plan_no_retreat_to_55_20`
- `no_revision_of_s11_d1_sealed_artifacts`
- `s12_d1_does_not_supersede_s11_d1_v1_p1_p2_clarification_rev2`
- `mechanic_family_lock_at_plan_no_reopening_at_draft_or_seal`

## 15. Files allowed to be created or modified

### This SEAL turn creates exactly:

- `docs/s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_tier_n_spec.md`
- `reports/s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_tier_n_spec_sealed.json`

### Future phases may create (each under separate authorization):

See JSON sidecar field `files_allowed_to_be_created_or_modified` for the full per-phase allowed-files list (P3 runner harness + drivers + tests; P3 build reports; P4 synthetic smoke; P6 IS diagnostic; P6.5 cost-stress matrix; P7 decision memo; P10 OOS gate; P11 lifecycle decision). Each phase requires separate operator authorization; deviation from the authorized file list requires explicit per-phase authorization.

## 16. Files explicitly forbidden from modification

(This turn AND all future S12-D1 turns, unless a separate authorization names the specific file as its target.)

- All s11-d1 v1 / P1 / P2 / clarification memo / rev2 sealed artifacts (byte-stable; treated as binding parent references)
- All S10-D2 sealed artifacts (commit `23c7164` park and all preceding S10-D2 sealed reports)
- All s10-D1 MNQ+MGC sealed artifacts (commit `1a9acec` park and full s10-D1 chain)
- All s10-D1 source files (loaders, validators, signal modules, simulators, aggregators, fetch tools, audit tools)
- All s9 RSI-2 ETF-proxy sealed artifacts
- All s7 D1 ETF-proxy sealed artifacts
- All B005_NNN sealed artifacts
- All B006_001 sealed artifacts (LESSON_B006_001_002/003/004 anchor)
- All B006_002 sealed artifacts (LESSON_B006_002_001/002 anchor)
- All s8-D1 cross-asset Donchian sealed artifacts
- T8 ETF-proxy family-park memo
- S10-D1 micro availability probe memo
- `next_research_track_selection_plan_after_*_park.md` files (parallel-session selection plans)
- `review_queue.json`
- Production `idea_memory` directory
- All Strategy Lab artifacts
- All ORB branch artifacts and Step 30 cost constants
- `obsidian-trade-logger` / `obsidian` directory and contents
- **`brain_memory/projects/trading_bot/lessons.md`** (dirty + unstaged from prior controller-session appends; explicitly off-limits this turn AND all future S12-D1 turns unless a separate authorization names it as the target)
- `CLAUDE.md`, `docs/decisions.md` (if exists), `RUNBOOK`, `pipeline_manifest`, `.gitignore`
- Any `data/databento_cache/` or `data/databento_cache_oos/` or `data/databento_cache_is_only/` contents (S10-D2-lineage caches; s12-d1 reuses the s10-d1 sealed CSV instead)
- Any `candidate_record_id` namespace other than `s12-d1-mnq-c0-single-instrument-donchian-15-8-databento-long-history`

## 17. Exact next phase

**NONE.** This SEAL document does NOT pre-approve any subsequent phase. The next operator authorization shall reference this sealed Tier-N spec by exact path and shall be one of:

- **"Authorize s12 D1 MNQ.c.0 P1 plan-lock"** -- locks the spec for build
- **"Authorize s12 D1 MNQ.c.0 Step 02b manifest cross-link only"** -- audit-clean CSV cross-link manifest
- **"Authorize alternative track selection"** -- rejects s12-d1 and picks another track
- **"Defer / Pause trading-bot track"** -- no further s12-d1 work for now

The expected default forward path is P1 plan-lock, but it is NOT pre-approved.

- No phase pre-approved by this SEAL: **TRUE**
- P1 plan-lock requires separate authorization: **TRUE**
- P3 BUILD requires separate authorization: **TRUE**
- P6 IS requires separate authorization: **TRUE**
- P10 OOS requires separate authorization: **TRUE**

## Parent references (READ-ONLY; not modified by this turn)

- `s12_d1_plan_commit`: `b4eac65`
- `s12_d1_draft_commit`: `7e9c867`
- `s11_d1_v1_spec_commit`: `9c63088`
- `s11_d1_v1_spec_seal_sha256`: `077e29e62f23dbc31823bad8447e5ef8d6f1a8c350d4f0c130c4f8f08be61a24`
- `s11_d1_rev2_commit`: `c110fd4`
- `s11_d1_rev2_seal_sha256`: `46659b4a8a73cb72fbe0153efed80aaf97b40557f8dfed51a9ba3199c243ed8d`
- `s11_d1_p1_plan_lock_commit`: `7d86486`
- `s11_d1_p2_phase_2_plan_commit`: `f64f984`
- `s11_d1_clarification_memo_commit`: `d13b56a`
- `s11_d1_clarification_memo_seal_sha256`: `eda08aceeb4afd7d4f985a739d6e87b3e803daff8da3f645f016b0a56a3af871`
- `s10_d2_park_commit`: `23c7164`
- `s10_d1_mnq_mgc_park_commit`: `1a9acec`
- `s10_d1_mnq_mgc_park_report_seal_sha256`: `32c1a87146264197fd852e53ba45baf6d6d45e40355b716e5a4d41a08edf1b2f`
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
- `S12_D1_MNQ_DONCHIAN_15_8_FRESH_CANDIDATE`
- `NOT_LIVE_READY`
- `NOT_PAPER_READY`
- `NO_FRC_GRANTED`
- `NO_PROFITABILITY_CLAIM`
- `NO_NEXT_PHASE_PRE_APPROVED`
- `S11_D1_TREATED_AS_PARENT_REFERENCE_ONLY`
- `S11_D1_NOT_REVISED_NOT_MODIFIED_NOT_REINTERPRETED`
- `K9_THRESHOLD_INVIOLATE`
- `DR10_RISK_ELEVATED_MITIGATED_VIA_DA4_B_START_CASH_100K`
- `DR_REDEFINITION_POST_SEAL_FORBIDDEN`
- `DONCHIAN_15_8_LOCKED_AT_PLAN_NO_RETREAT_TO_55_20`
- `MECHANIC_FAMILY_F1_LOCKED_AT_PLAN_NO_REOPENING`
- `OOS_K9_STRUCTURALLY_UNREACHABLE_TERMINAL_OOS_PARK_LIKELY`
- `ADDENDUM_MEMO_REC1_INCORPORATED_AT_SEAL_OOS_K9_DISCLOSURE_ADDED`

## Hard boundaries held (this SEAL turn)

See JSON sidecar field `hard_boundaries_held_this_seal_turn` for the full attestation (60+ boundaries; all True). The set is identical-or-stricter to the s11-d1 v1 SEAL boundary set, with explicit additions for s12-d1's fresh-candidate posture (`no_modification_of_s11_d1_sealed_artifacts: True`, `no_revision_of_s11_d1_sealed_artifacts: True`).

## Seal metadata

- **Report seal sha256:** `07c3200b5e23ab88e864f92926b83ded033a3d66c0e37e8cf8555985ad8f3b48`
- **Seal method:** LESSON_HUNTER_004 canonical roundtrip (json.dumps `sort_keys=True separators=',:' ensure_ascii=False default=str` EXCLUDING `report_seal_sha256` + `seal_method`)
- **Reseal verified on disk:** YES (in-script roundtrip assertion passed)
