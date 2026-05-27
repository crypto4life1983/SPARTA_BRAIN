# S12-D1 P11 lifecycle park memo (sealed)

**Candidate record id:** `s12-d1-mnq-c0-single-instrument-donchian-15-8-databento-long-history`
**Phase:** `PHASE2-S12-D1-MNQ-DONCHIAN-15-8` / `P11_LIFECYCLE_DECISION`
**Authored (UTC):** `2026-05-27T16:16:46.475514Z`
**Lifecycle state transition:** `ACTIVE_RESEARCH` -> **`PARKED_SAFE_BUT_INSUFFICIENT_SAMPLE_AT_IS`**
**Report seal sha256:** `b9722d424f6faabea96dc892f811f57826a382263f2d8480e4205c789f3f9dad`
**Seal method:** LESSON_HUNTER_004 canonical roundtrip
**Reseal verified on disk:** YES (UTF-8 explicit)

## Park decision driver

**Driver:** P6 IS diagnostic verdict `INSUFFICIENT_SAMPLE` (`closed_trades = 48 < K9 = 100` over 4.6y IS window)

**C8 weak-performance / insufficient-sample rejection rule applied:** Per C8, when a candidate produces `closed_trades < verdict_min_closed_trades` on a clean run, the operator MUST park it. Do NOT iterate parameters in search of better trade counts — that would be optimization, which is forbidden by the safety-contract template.

**Parameters NOT authorized to modify** at park time: Donchian periods, ATR period/multiplier, starting cash, warmup days, K9 threshold.

## P6 IS verdict anchor (READ-ONLY; carried byte-equivalent)

- P6 IS report seal sha256: `33c91592c09860c3ab9469aab38741b7378f54ad56ff3772f9ef6a03ea92156d`
- P6 IS commit: `9241ed6`
- Verdict: `INSUFFICIENT_SAMPLE`
- Closed trades observed: **48**
- K9 threshold: 100
- K9 fired: **YES** (A1 fails)

### Informational economics observed (CANNOT override K9 verdict per LESSON_B006_002_002)

| Metric | Value |
|---|---|
| `net_pnl_usd` | +$93,921.42 |
| `starting_cash_usd` | $100,000.00 (DA4=B) |
| `final_equity_usd` | $193,921.43 |
| `cagr_pct` | 15.3788% |
| `sharpe_annualized` | 0.5038 |
| `sharpe_proxy_per_trade` | 0.1192 |
| `expectancy_per_trade_usd` | +$1,956.70 |
| `max_drawdown_pct_magnitude` | 37.62% |
| `win_rate_pct_or_NA_INSUFFICIENT_SAMPLE` | `NA_INSUFFICIENT_SAMPLE` |
| `trades_per_year_observed` | 10.37 |

**Disclaimer:** Net economics were positive, but per LESSON_B006_002_002 favorable economic numbers DO NOT override fail-closed verdicts by design. K9 inviolacy is structural; the verdict is `INSUFFICIENT_SAMPLE` regardless of how positive headline metrics appear. The park is mandatory under C8.

### K-gates NOT triggered at S1 baseline

| K-gate | Triggered |
|---|---|
| K1 sharpe_proxy < 0 | No |
| K2 expectancy ≤ 0 | No |
| K4 \|maxdd\| > 50% | No (37.62% < 50%; above 30% concern threshold) |

## K9-mitigation hypothesis: FALSIFIED

The s12-d1 fresh-candidate hypothesis (PLAN §8 / DRAFT §1) was that Donchian-15/8 on MNQ.c.0 over 4.6y IS would produce ~80-200 portfolio trades (3-4x s11-d1 v1's 25-50 Donchian-55/20 expectation), thereby crossing K9=100.

| Field | Value |
|---|---|
| DRAFT-estimated IS trade count band | 80 (low) / 140 (central) / 200 (high) |
| DRAFT-estimated trades/year band | 17.4 / 30.4 / 43.5 |
| **Actual observed IS trade count** | **48** |
| **Actual observed trades/year** | **10.37** |
| Actual / DRAFT lower bound ratio | 48/80 = 0.60 (40% shortfall vs lower bound) |
| Actual / DRAFT central ratio | 48/140 = 0.34 (66% shortfall vs central) |
| Hypothesis status | **FALSIFIED** |

**Implication:** Donchian-15/8 does NOT solve the IS K9 problem on a single MNQ.c.0 instrument. Further iteration of N/M would be optimization, which is forbidden. Pursuing a different mechanic family (RSI mean-reversion / vol-targeting / carry) or different universe (multi-instrument) would require a FRESH candidate_record_id under separate operator authorization.

## REC1 reinforcement at P11

**REC1 verbatim (carried byte-equivalent):**

> *"OOS K9 EXPECTED TO FIRE. Implied OOS trade count over 2.0y at IS rate is approximately 35-87 trades, below K9 = 100. If OOS K9 fires, the OOS verdict will be OOS_INSUFFICIENT_SAMPLE or PARKED_SAFE_BUT_OOS_INDETERMINATE analogous to S10-D2 P11 PARK at 23c7164. The chain shall NOT relax K9 at OOS; the appropriate response is to seal the INSUFFICIENT_SAMPLE / INDETERMINATE verdict and park the candidate. Pursuing s12-d1 accepts the structural likelihood of an OOS PARK outcome."*

| Field | Value |
|---|---|
| REC1 originally anchored at | SEAL `66bbbd1` |
| REC1 original implied OOS band | 35-87 trades (low-high) over 2.0y at DRAFT IS rate |
| Actual observed IS rate at P6 | 10.37 trades/year |
| **Implied OOS trade count at actual IS rate** | **~21 trades over 2.0y** (10.37 × 2.0 = 20.7) |
| Implied OOS vs K9 at actual rate | 21/100 = 0.21 ratio |

**REC1 reinforcement summary:** REC1's structural OOS K9 unreachability finding is NOT contradicted by the IS result — it is **STRENGTHENED**. REC1 originally projected 35-87 implied OOS trades (a 0.35-0.87 ratio to K9). With the actual IS rate of 10.37 trades/year, the implied OOS count is approximately **21 trades over the 2.0y OOS window — a 0.21 ratio to K9, even further below the floor than REC1 originally disclosed.**

Pursuing P10 OOS execution would simply ratify the K9 fire that REC1 already structurally predicted; the operator chose to park at P11 rather than incur further sealed-artifact cost for a structurally predetermined OOS PARK verdict.

`rec1_binding_preserved_at_p11`: **True**

## Park status

| Field | Value |
|---|---|
| `operational_status` | **`PARKED_SAFE_BUT_INSUFFICIENT_SAMPLE_AT_IS`** |
| `park_is_terminal_for_this_candidate_record_id` | True |
| `revival_requires_FRESH_SEALED_RESEARCH_CYCLE` | True |
| `revival_fresh_candidate_id_required` | True |
| `revival_not_authorized_by_this_park_memo` | True |
| `fresh_revN_revision_of_s12_d1_NOT_authorized` | True |

### Permanent attributes unchanged by parking

- `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` secondary label
- All advisory labels
- 6-gate live-block
- FRC status (never granted)
- **REC1 `oos_k9_risk_disclosure` binding** (carried byte-equivalent into park memo)
- `no_strategy_optimization_authorized = True`
- `no_dr_redefinition_post_seal = True`
- `K9_threshold_inviolate = True`
- Donchian-15/8 locked at PLAN no retreat to 55/20
- Mechanic family F1 locked at PLAN no reopening at DRAFT or SEAL

## No promotion attestation

| Field | Value |
|---|---|
| `no_promotion_to_live` | True |
| `no_promotion_to_paper` | True |
| `no_promotion_to_frc` | True |
| `no_promotion_to_strategy_lab` | True |
| `no_promotion_to_review_queue` | True |
| `permanent_live_block_remains_active` | True |
| `6_gate_live_block_remains_active` | True |
| `promotion_at_any_stage_OUT_OF_SCOPE_for_this_record_id` | True |
| `p11_park_memo_DOES_NOT_grant_any_promotion_pathway` | True |

## Future research options NOT authorized by this memo

(See JSON sidecar `future_research_options_NOT_authorized_by_this_memo`.) Options include:
- Run P6.5 cost-stress on s12-d1 (cannot change INSUFFICIENT_SAMPLE verdict)
- Run P7 decision memo on s12-d1 (already effectively decided via this P11)
- Run P10 OOS gate on s12-d1 (per C7 OOS requires IS verdict ELIGIBLE_FOR_OOS; INSUFFICIENT_SAMPLE does not qualify)
- Fresh _revN_ revision of s12-d1 changing Donchian periods (FORBIDDEN per Tier-N spec invariants)
- Fresh candidate_record_id pursuing different mechanic family on MNQ.c.0 (requires fresh selection plan)
- Fresh candidate_record_id pursuing multi-instrument basket (requires fresh selection plan)
- Pivot to a different project entirely

## Lessons learned (documented in park memo only; `lessons.md` NOT modified this turn)

(See JSON sidecar `lessons_learned_for_future_candidates_NOT_modifying_lessons_md_this_turn` for full list.) Highlights:

1. Donchian-15/8 on a single MNQ.c.0 instrument over 4.6y produces ~10 trades/year, NOT the 17-43 trades/year that linear-scaling-from-NQ-10y estimates suggested. The DRAFT estimate (80-200 IS trades) was substantially over-optimistic by ~2-3x.
2. K9-mitigation via shorter Donchian periods on a SINGLE futures instrument is structurally hard. Future candidates seeking K9 clearance on similar windows likely need either multi-instrument scope or higher-frequency mechanics.
3. REC1's structural unreachability framework was correct (and conservatively understated). Future Phase 2 candidates should apply REC1-style OOS-K9-reachability analysis at DRAFT time before authoring SEAL.
4. Positive headline economics (+15% CAGR, positive Sharpe/expectancy) do NOT override K9 verdict semantics. C8 framework working as designed.
5. DA4=B START_CASH revision did not materially affect trade count (sizing affects contracts-per-trade, not trade-event frequency). The DR10 mitigation lever does not address K9 risk.
6. P3 source files SHOULD remain byte-stable across P6 execution. The simulator pattern (tmp/ script importing primitives) preserves the P3 BUILD seal chain integrity.
7. REC1 binding propagation across the full sealing chain (SEAL → P1 → P2 → P3 → P4 → P6 → P11) provides traceable accountability for the structural OOS K9 unreachability finding from initial DRAFT review through terminal park.

`lessons_md_modified_this_turn`: **False** · `lessons_md_separate_authorization_required_to_modify`: True

## Chain anchors byte-stable at park

| Phase | Commit | Seal sha256 |
|---|---|---|
| Tier-N SEAL | `66bbbd1` | `07c3200b5e23ab88e864f92926b83ded033a3d66c0e37e8cf8555985ad8f3b48` |
| P1 plan-lock | `d8bd359` | `eb72798eb95c08407ead9c273a650853bd5e871942856f87b48f97f07a640340` |
| P2 phase-2 plan | `0b8d948` | `689dd3d06c0e2518ab5f6105544cb3d38194027647de10940da976e427c8efa9` |
| P3 BUILD (3 reports) | `91e740e` | runner / IS-driver / OOS-driver sealed |
| P4 smoke | `ea78845` | `6d2bff4d2b40d4349a1c26d37375ca6d9e8ea616ff9f85d3d9f56293325b8bd4` |
| P6 IS diagnostic | `9241ed6` | `33c91592c09860c3ab9469aab38741b7378f54ad56ff3772f9ef6a03ea92156d` |
| **P11 park memo (this)** | (this commit) | `b9722d424f6faabea96dc892f811f57826a382263f2d8480e4205c789f3f9dad` |

## Hard boundaries held (this P11 park memo turn; ~35 boundaries; all True)

See JSON sidecar `hard_boundaries_held_this_p11_park_memo_turn` for full attestation. Key:
- `no_p6_5_cost_stress_run`, `no_p7_decision_memo`, `no_p10_oos_gate`, `no_oos_inspection`
- `no_data_fetch`, `no_databento_api_call`, `no_network_call`
- `no_live_trading`, `no_paper_trading`, `no_broker_exchange_api`, `no_brokerage_connection`
- `no_strategy_lab_invoked`, `no_strategy_lab_promotion`
- **`no_lessons_md_touched`: True** (per operator instruction; lifecycle lessons documented in park memo only)
- `no_modification_of_s11_d1_sealed_artifacts`
- `no_modification_of_s12_d1_seal_at_66bbbd1 / p1_at_d8bd359 / p2_at_0b8d948 / p3_build_at_91e740e / p4_smoke_at_ea78845 / p6_is_at_9241ed6`
- `no_modification_of_p3_source_files`
- `no_rec1_demotion_to_advisory`
- `no_revival_authorized_by_this_park_memo`
- `no_fresh_revN_revision_authorized`
- `no_promotion_pathway_granted`
- `park_is_terminal_for_this_candidate_record_id`

## Status

| Field | Value |
|---|---|
| trading_status | PAUSED |
| live_status | BLOCKED_AT_6_GATES |
| frc_status | NEVER_GRANTED |
| research_label | DIAGNOSTIC_ONLY_NOT_LIVE_GRADE |
| **lifecycle_state** | **PARKED_SAFE_BUT_INSUFFICIENT_SAMPLE_AT_IS** |
| rec1_oos_k9_risk_disclosure_binding | True |
| candidate_terminal_for_this_record_id | True |

## Next step options post-park (all require separate operator authorization)

- `Authorize alternative track selection plan revision only.`
- `Authorize cross-domain pivot only.`
- `Defer / Pause trading-bot track.`
- (Fresh candidate with different mechanic/universe — requires fresh selection plan + fresh PLAN/DRAFT/SEAL lifecycle under new candidate_record_id)

s12-d1 lifecycle is **TERMINAL** at this park. No phase pre-approved.
