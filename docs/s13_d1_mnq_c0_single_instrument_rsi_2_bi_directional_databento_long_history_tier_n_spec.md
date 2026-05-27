# S13-D1 Tier-N specification (sealed)

**Candidate record id:** `s13-d1-mnq-c0-single-instrument-rsi-2-bi-directional-databento-long-history`
**Phase prefix:** `PHASE2-S13-D1-MNQ-RSI-2-BIDIR`
**Algo version:** `s13_d1_v0_1_0`
**Authored (UTC):** `2026-05-27T16:55:13.507655Z`
**Spec lifecycle state:** SEALED
**Report seal sha256:** `2f9d176388fe0b66c9ced19f33c68e079bb08112f3d52f3f20a9aba7d91bf775`
**Seal method:** LESSON_HUNTER_004 canonical roundtrip
**Reseal verified on disk:** YES (UTF-8 explicit)

## 1. Candidate purpose

Author a sealed Tier-N specification for a single-instrument MNQ.c.0 fresh-candidate research diagnostic using the Connors RSI(2) bi-directional mean-reversion mechanic (F3). Selected per selection-plan revision after s12-d1 park (`0e3f9d4`; T1 at 41/50). **The only track that clears K9 at BOTH IS AND OOS under the new K9-reachability discipline.** Tests whether RSI(2) bi-directional on single-instrument MNQ.c.0 futures produces a structurally different result from the s9 long-only ETF-proxy falsification. Research diagnostic only. No promotion. No live trading. No FRC. No profitability claim.

## 2. Why RSI(2) bi-directional fresh candidate is being tested

s12-d1 Donchian-15/8 single-instrument K9-mitigation hypothesis was falsified at P6 IS (48 trades vs DRAFT 80-200; `PARKED_SAFE_BUT_INSUFFICIENT_SAMPLE_AT_IS` at `ecbd001`). Selection-plan revision after s12-d1 park (`0e3f9d4`) identified T1 (RSI(2) bi-directional on MNQ.c.0) as the only track scoring 41/50 that clears K9-reachability at BOTH IS and OOS. RSI(2) produces ~50-65 trades/year on MNQ.c.0 (5-6× s12-d1's observed 10/y), structurally crossing the K9 floor at both windows.

**s9 RSI-2 falsification does NOT transfer** because (a) asset class differs (futures vs ETFs), (b) cost surface differs (per-contract vs per-share + bps), (c) signal direction differs (bi-directional vs long-only), (d) universe differs (single MNQ vs 4-ETF basket).

**Operator revised at SEAL:** DA3=B (per-trade risk **0.5%**) AND DA4=C (START_CASH **$200k**) -- combined revision is the most conservative DR3/DR10 posture mitigating both zero-cost-only-survival risk (DR3; s9 lineage) and turnover-cost-explosion risk (DR10; high-frequency).

## 3. s12-d1 lessons inherited byte-equivalent

- K9-reachability analysis MUST be performed at PLAN/DRAFT/SEAL time with explicit IS AND OOS calculations (NEW framework discipline introduced at `0e3f9d4`)
- Linear-scaling trade-count estimation is unreliable; bands should be conservatively wide
- K9 inviolacy is structural; positive headline economics do NOT override K9 verdict semantics
- DA4 (START_CASH) revision does NOT address K9 risk; sizing affects contracts-per-trade not trade-event frequency
- DR10 turnover risk should be calculated at PLAN/DRAFT time for high-frequency mechanics
- P3 source files SHOULD remain byte-stable across P6 execution
- **REC1-equivalent OOS K9 disclosure should propagate across SEAL -> P1 -> P2 -> P3 -> P4 -> P6 -> P11 chain**
- Park is mandatory under C8 when K9 fires; no parameter iteration to seek better trade counts

## 4. Intentional differences from s12-d1

| Aspect | s12-d1 | s13-d1 (this SEAL) | Reason |
|---|---|---|---|
| Mechanic family | F1 Donchian-15/8 trend | **F3 RSI(2) bi-directional mean-reversion** | Structurally orthogonal |
| Expected IS trade count | 80-200 (actual 48; FALSIFIED) | **230-300** | 5-6× higher signal density |
| Expected OOS trade count | implied 21 at observed rate (UNREACHABLE) | **100-130** | clears K9 at lower bound |
| Per-trade risk % | 1.0% | **0.5%** (DA3=B revised) | DR3 mitigation (s9 lineage) |
| START_CASH | $100,000 (DA4=B carried) | **$200,000** (DA4=C revised) | DR10 mitigation; halves cost-drag |
| DR3 risk | low (F1 trend) | **ELEVATED** (RSI lineage) | mitigated via DA3=B |
| DR10 risk | elevated | **FURTHER ELEVATED** | mitigated via DA4=C |

## 5. Entry/exit logic boundary (LOCKED at SEAL)

**Mechanic family:** F3 RSI(2) bi-directional mean-reversion, no pyramid, ATR-stop, **0.5% per-trade risk** (LOCKED at PLAN; DRAFT did NOT reopen mechanic-family menu)

| Aspect | Value |
|---|---|
| `rsi_period` | **2** (Connors classic) |
| `rsi_method` | Wilder smoothing on close-to-close returns |
| `rsi_long_entry_threshold` | **`< 10`** (oversold) |
| `rsi_long_exit_threshold` | **`> 50`** |
| `rsi_short_entry_threshold` | **`> 90`** (overbought; bi-directional symmetric) |
| `rsi_short_exit_threshold` | **`< 50`** |
| `atr_window_days_P` | 20 (DA1=A; Wilder) |
| `atr_stop_multiplier_K` | 2.0 (DA2=A) |
| `stop_method` | 2 × Wilder ATR(20); set at entry |
| `pyramid_method` | NONE; `max_units_per_market = 1` |
| **`per_trade_risk_pct`** | **0.005** (DA3=B; REVISED from 0.01) |
| `position_sizing_formula` | `contracts = floor((0.005 × equity) / (ATR_entry × tick_value_usd))` |
| `tick_value_usd` | 0.5 |
| `tick_size_points` | 0.25 |
| `dollar_per_point` | 2.0 |
| `rth_window` | DA12=A: `(9:30, 16:00, America/New_York)` |
| `intraday_data_used` | False |
| `roll_method` | Databento continuous front-month |
| `amb6_filter` | NONE |
| `regime_overlay` | NONE |
| `vol_targeting` | NONE |
| `leverage_cap` | NONE (DR11 structurally absent) |

## 6. Cost assumptions (LOCKED at SEAL)

- Tick size 0.25 points; tick value $0.50; $2.00/point
- **`START_CASH_USD`: $200,000** (DA4=C; REVISED from $100k; DR10 mitigation)
- Commission per round-trip: $0.74 (DA8=A)
- Fees per round-trip: $0.36 (DA9=A)
- Slippage entry/stop/exit ticks: 1 / 1 / 1 (DA10=A)
- WARMUP_DAYS: 220 (DA11=A)

### 6.1 Cost-stress tiers (5-tier; DA7=A; carried byte-equivalent)

| Tier | cost_scalar | slippage_scalar | Note |
|---|---:|---:|---|
| `S0` | 0.0 | 0.0 | zero-cost ideal |
| `S1` | 1.0 | 1.0 | baseline retail |
| `S2` | 1.5 | 1.5 | stressed retail |
| `S3` | 2.0 | 2.0 | adversarial |
| `S4` | 3.0 | 3.0 | extreme adversarial |

### 6.2 Pre-registered S0 edge sign

**OPEN QUESTION** -- no a-priori claim. s9's negative S0 finding on long-only ETF-proxy does NOT determine s13-d1 bi-directional MNQ futures result by first-principles. The diagnostic is genuinely open.

## 7. K9-reachability discipline applied at SEAL (NEW framework requirement)

Per the discipline introduced in the selection-plan revision at `0e3f9d4` (carried into PLAN and DRAFT), the SEAL records the explicit K9-reachability table:

| Window | Length (y) | Required trades/year for K9=100 | Expected s13-d1 (low / central / high) | Expected total | K9 status |
|---|---:|---|---|---|---|
| IS | 4.6 | ≥ 21.74 | 50 / 57 / 65 | 230 / 262 / 300 | **CLEARS WITH MARGIN (2.3-3.0×)** |
| **OOS** | **2.0** | **≥ 50.00** | 50 / 57 / 65 | **100 / 114 / 130** | **CLEARS (borderline at lower bound: 1.0-1.3×)** |

## 8. REC1-equivalent OOS K9 disclosure (BINDING; carried byte-equivalent)

> *"OOS K9 reachable at lower bound with thin margin (~50-65 trades/year vs 50/year floor). If observed IS rate falls below 25/year on RSI(2) bi-directional, OOS K9 unreachability becomes structurally probable. The s9 RSI-2 baseline observed 414 trades over long-only 4-ETF window; if MNQ.c.0 bi-directional rate falls below half that proportional rate, OOS K9 fires. If OOS K9 fires, the OOS verdict shall be OOS_INSUFFICIENT_SAMPLE or PARKED_SAFE_BUT_OOS_INDETERMINATE analogous to S10-D2 P11 PARK at 23c7164 and s12-d1 P11 park at ecbd001. The chain shall NOT relax K9 at OOS; the appropriate response is to seal the INSUFFICIENT_SAMPLE / INDETERMINATE verdict and park the candidate. Pursuing s13-d1 accepts the structural possibility of an OOS PARK outcome if the IS rate falls below the DRAFT-estimated 50-65/y band."*

- `rec1_equivalent_does_not_alter_DA1_through_DA14_resolutions`: True
- `rec1_equivalent_does_not_alter_DR9_or_DR10_thresholds`: True
- `rec1_equivalent_is_disclosure_only_not_a_DR_redefinition`: True
- `no_chain_response_relaxes_K9_at_OOS`: True

## 9. DRAFT ambiguities resolved at SEAL

| DA | Topic | Choice | Resolved value | Note |
|---|---|---|---|---|
| DA1 | ATR stop window P | A | 20 | Wilder |
| DA2 | ATR multiplier K | A | 2.0 | 2N stop |
| **DA3** | **Per-trade risk %** | **B (REVISED)** | **0.5%** | **DR3 mitigation; s9 lineage cost-erosion precedent** |
| **DA4** | **`START_CASH_USD`** | **C (REVISED)** | **$200,000** | **DR10 mitigation; halves per-dollar cost pressure** |
| DA5 | K4 max-drawdown threshold | A | 0.50 magnitude | byte-equivalent |
| DA6 | Output schema name | A | `sparta.s13.d1.mnq_c0.rsi_2_bidir.diagnostic_run_report.v1` | LOCKED |
| DA7 | Cost-stress tier set | A | 5-tier S0..S4 | LOCKED |
| DA8 | Commission per round-trip | A | $0.74 | LOCKED |
| DA9 | Fees per round-trip | A | $0.36 | LOCKED |
| DA10 | Slippage entry/stop/exit | A | 1/1/1 | LOCKED |
| DA11 | `WARMUP_DAYS` | A | 220 | -- |
| DA12 | RTH window | A | 09:30-16:00 ET America/New_York | LOCKED |
| DA13 | DR9 thresholds | A | 0.95/0.30/5/5 | LOCKED non-negotiable |
| DA14 | DR10 thresholds | A | annual_turnover>0.50 OR S2-drag>0.05 | LOCKED non-negotiable |

## 10. Rejection rules (K-gates + DR-gates)

K-gates: K1 (sharpe<0 at S1), K2 (expectancy≤0), K4 (\|maxdd\|>50%), K6 NOT_APPLICABLE, K7 (silent filter), K8 (sealed parent drift), K9 (closed_trades<100 → INSUFFICIENT_SAMPLE), K10 NOT_APPLICABLE, K11 NOT_APPLICABLE, K12 (DR fires on cost-stress; **MORE LIKELY for s13-d1 RSI lineage**).

DR-gates: DR1 OOS-only, DR2 cost-stress degradation, **DR3 zero-cost-only survival ELEVATED**, DR4 OOS-only, **DR5 cost-stress turns edge negative BINDING**, DR6 warmup sizing, DR7 missing OOS evidence, DR8 live path, DR9 data continuity, **DR10 turnover explosion ELEVATED (mitigated via DA4=C)**, DR11 NOT_IN_CHAIN.

DR precedence: `DR7 → DR1 → DR9 → DR10 → DR6 → DR4 → DR2 → DR3 → DR5`.

## 11. 25 RUNTIME_INVARIANTS at SEAL

7 B005_NNN · 4 B006_001 · 2 B006_002 (no leverage cap) · 5 s10-d1-specific · 3 s11-d1-specific · 4 NEW s13-d1-specific:
- `rsi_2_bi_directional_thresholds_locked_at_plan_no_retreat_to_long_only_or_different_thresholds`
- `mechanic_family_F3_lock_at_plan_no_reopening_at_draft_or_seal`
- `no_revision_of_s12_d1_terminal_park_via_this_candidate_id`
- `k9_reachability_discipline_applied_at_plan_time_per_new_framework_requirement`

## 12. Promotion rules

`permanent_live_block: True` · `permanent_paper_block: True` · `live_promotion_blocked_at_6_gates_permanently: True` · `no_verdict_unblocks_*: True` (live, paper, FRC, Strategy Lab, review_queue) · `promotion_at_any_stage_is_OUT_OF_SCOPE_FOR_THIS_RECORD_ID: True` · `research_diagnostic_only: True`.

## 13. Files allowed to be created or modified

### This SEAL turn creates exactly:

- `docs/s13_d1_mnq_c0_single_instrument_rsi_2_bi_directional_databento_long_history_tier_n_spec.md`
- `reports/s13_d1_mnq_c0_single_instrument_rsi_2_bi_directional_databento_long_history_tier_n_spec_sealed.json`

### Future phases may create (each under separate authorization):

See JSON sidecar `files_allowed_to_be_created_or_modified` for full per-phase allowed-files list. Each subsequent phase requires separate operator authorization.

## 14. Status

| Field | Value |
|---|---|
| trading_status | PAUSED |
| live_status | BLOCKED_AT_6_GATES |
| frc_status | NEVER_GRANTED |
| research_label | DIAGNOSTIC_ONLY_NOT_LIVE_GRADE |
| spec_lifecycle_state | SEALED |
| K9_THRESHOLD_INVIOLATE | True |
| REC1_EQUIVALENT_OOS_K9_DISCLOSURE_BINDING | True |
| s12-d1 terminal park preserved | True |

## 15. Exact next phase

**NONE.** This SEAL document does NOT pre-approve any subsequent phase. The next operator authorization shall reference this sealed Tier-N spec by exact path and shall be one of:

- `Authorize s13 D1 MNQ.c.0 P1 plan-lock.`
- `Authorize alternative selection plan rev2 only.`
- `Authorize cross-domain pivot only.`
- `Defer / Pause trading-bot track.`

## Seal metadata

- **Report seal sha256:** `2f9d176388fe0b66c9ced19f33c68e079bb08112f3d52f3f20a9aba7d91bf775`
- **Seal method:** LESSON_HUNTER_004 canonical roundtrip
- **Reseal verified on disk:** YES (UTF-8 explicit)
