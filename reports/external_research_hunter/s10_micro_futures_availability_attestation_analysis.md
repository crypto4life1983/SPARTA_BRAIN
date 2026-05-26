# S10 Micro Futures Availability Attestation Analysis (SEALED, PLAN/ANALYSIS-ONLY)

**Phase:** `S10_AVAILABILITY_ATTESTATION_ANALYSIS_SEALED_PLAN_ANALYSIS_ONLY`
**Operational status:** `AVAILABILITY_ATTESTATION_ANALYSIS_SEALED_RECOMMENDATION_S10_D2_AWAITING_OPERATOR_DECISION`
**Report date UTC:** 2026-05-26T21:18:35Z

**Analysis seal:** `417ed6c7b4e177e0681a3fe20a03744cb22c9946b9755e077a3def3afd7f50e7`
**Predecessor (S10 selection plan) seal:** `007110ff5a57dd04b184409bad64fd667374cd049155416c869a73f7af0c1f97`

> Labels: DIAGNOSTIC_ONLY_NOT_LIVE_GRADE, PLAN_AND_SPEC_ONLY, NO_FRC_GRANTED,
> S10_AVAILABILITY_ANALYSIS_SEALED, NO_TIER_N_SPEC_AUTHORED_THIS_TURN,
> RECOMMENDATION_S10_D2_HIGHER_CAPITAL_DUE_TO_MICRO_COVERAGE_CONSTRAINT
> Trading: PAUSED | Live: BLOCKED_AT_6_GATES | FRC: not granted
> No profitability claim.

---

## Operator-supplied probe results (verbatim)

### MNQ.c.0
- recognized: yes
- first successful probe date (non-empty): 2019-05-13
- last successful probe date  (non-empty): 2025-12-30
- per-date probes:
  - 2013-01-02: OK records=0
  - 2019-05-13: OK records=1301
  - 2021-07-19: OK records=1380
  - 2022-12-30: OK records=1320
  - 2023-01-03: OK records=1380
  - 2025-12-30: OK records=1380

### MGC.c.0
- recognized: yes
- first successful probe date (non-empty): 2013-01-02
- last successful probe date  (non-empty): 2025-12-30
- per-date probes:
  - 2013-01-02: OK records=286
  - 2019-05-13: OK records=990
  - 2021-07-19: OK records=1358
  - 2022-12-30: OK records=1296
  - 2023-01-03: OK records=1375
  - 2025-12-30: OK records=1380

### MCL.c.0
- recognized: yes
- first successful probe date (non-empty): 2021-07-19
- last successful probe date  (non-empty): 2025-12-30
- per-date probes:
  - 2013-01-02: OK records=0
  - 2019-05-13: OK records=0
  - 2021-07-19: OK records=244
  - 2022-12-30: OK records=1313
  - 2023-01-03: OK records=1374
  - 2025-12-30: OK records=1312

### ZN.c.0
- recognized: yes (already in s8-D1 cache)
- coverage: 2013-01-01..2025-12-30 (480 IS + 144 OOS files)
- notes: Already verified in s8-D1 chain; no probe needed.

---

## Trade-rate baseline (s8-D1 IS reference)

- IS window: 10.0 years (2013-2022)
- Total IS trades portfolio: 111
- Per-market: NQ=18, GC=28, ZN=48, CL=17
- Trades per year portfolio: 11.10
- K9 threshold (portfolio closed trades): 100

---

## Path comparison

| Path | Universe | IS window | IS years | Projected IS trades | K9 fires? | Sample-size risk | Comparability risk |
|---|---|---|---|---|---|---|---|
| **S10-D1A** | MNQ.c.0, MGC.c.0, ZN.c.0, MCL.c.0 | 2021-07-19 to 2022-12-30 | 1.45 | ~16 | **YES** | HIGH | LOW |
| **S10-D1B** | MNQ.c.0, MGC.c.0, ZN.c.0 | 2019-05-13 to 2022-12-30 | 3.63 | ~30 | **YES** | HIGH | MEDIUM |
| **S10-D1C** | Heterogeneous: NQ/GC/ZN/CL in IS, MNQ/MGC/ZN/MCL in OOS | 2013-01-01 to 2022-12-30 | 10.0 | ~111 | no | LOW | VERY HIGH |
| **S10-D2** | NQ.c.0, GC.c.0, ZN.c.0, CL.c.0 | 2013-01-01 to 2022-12-30 | 10.0 | ~111 | no | LOW | LOW |
| S10-D5 | (none) | (none) | (none) | (none) | N/A | N/A | N/A |

### S10-D1A — Pure micro universe

- **Universe:** ['MNQ.c.0', 'MGC.c.0', 'ZN.c.0', 'MCL.c.0']
- **Binding constraint:** MCL.c.0 first non-empty bar 2021-07-19
- **IS window:** 2021-07-19 to 2022-12-30  (1.45 years)
- **OOS window:** 2023-01-01 to 2025-12-30
- **Projected IS trades portfolio:** ~16  (K9 threshold = 100)
- **K9 likely to fire in-sample:** True
- **Sample-size risk:** HIGH — projected ~17 portfolio trades vs K9 threshold 100; K9 fires with extremely high probability; verdict almost certain to be INSUFFICIENT_SAMPLE
- **Comparability risk:** LOW — same strategy parameters as s8-D1 except universe; clean delta
- **Addresses s8-D1 root cause cleanly:** True
- **In evidence terms:** False
- **Verdict predictability at C7:** INSUFFICIENT_SAMPLE (K9 fires)
- **Honest framing:** Pure micro is the conceptually-right candidate (fixes the exact $/pt issue) but Databento lacks the historical coverage to produce preregistered IS evidence that passes K9. Would essentially be an OPERATIONAL feasibility test (can it trade?) NOT a statistical validation test (does it preserve s8-D1 edge?). The verdict would be INSUFFICIENT_SAMPLE regardless of strategy quality.

### S10-D1B — Partial micro universe (drop MCL)

- **Universe:** ['MNQ.c.0', 'MGC.c.0', 'ZN.c.0']
- **Binding constraint:** MNQ.c.0 first non-empty bar 2019-05-13
- **IS window:** 2019-05-13 to 2022-12-30  (3.63 years)
- **OOS window:** 2023-01-01 to 2025-12-30
- **Projected IS trades portfolio:** ~30  (K9 threshold = 100)
- **K9 likely to fire in-sample:** True
- **Sample-size risk:** HIGH — projected ~30 portfolio trades vs K9 threshold 100; K9 fires; INSUFFICIENT_SAMPLE expected
- **Comparability risk:** MEDIUM — drops one market (CL/MCL) vs s8-D1's 4-market diversification basis; K10 hypothesis weakens to 3-market correlation; A7 effective_independent_bets formula changes (3 markets at OOS K10 0.052 → effective_bets ≈ 2.85 vs s8-D1 3.35)
- **Addresses s8-D1 root cause cleanly:** True
- **In evidence terms:** False
- **Verdict predictability at C7:** INSUFFICIENT_SAMPLE (K9 fires)
- **Honest framing:** Drops a market to extend IS window from 17.5mo to 3.65 years. Still too short for K9. Now ALSO weakens the diversification basis that motivated D1 originally. Strictly worse than S10-D1A (changes 2 things instead of 1) AND still fails K9.

### S10-D1C — Mixed full-size/micro (full IS 2013-2022, micros for OOS)

- **Universe:** Heterogeneous: NQ/GC/ZN/CL in IS, MNQ/MGC/ZN/MCL in OOS
- **Binding constraint:** None on IS (full-size always available); OOS uses micros
- **IS window:** 2013-01-01 to 2022-12-30  (10.0 years)
- **OOS window:** 2023-01-01 to 2025-12-30
- **Projected IS trades portfolio:** ~111  (K9 threshold = 100)
- **K9 likely to fire in-sample:** False
- **Sample-size risk:** LOW — full 10y IS window with ~111 projected trades (mirrors s8-D1 directly because IS contracts are identical to s8-D1)
- **Comparability risk:** VERY HIGH — IS results would be 100% identical to s8-D1 IS (same contracts, same data, same logic). OOS would use different contract universe (micros). Any IS-OOS divergence is confounded by the contract substitution AND the OOS regime AND the sizing change. DR4 (IS-S0 vs OOS-S0) becomes non-comparable.
- **Addresses s8-D1 root cause cleanly:** False
- **In evidence terms:** PARTIALLY (OOS would show whether micros trade; but IS is just s8-D1)
- **Verdict predictability at C7:** READY_FOR_LONGER_BACKTEST at IS (mirrors s8-D1); OOS result novel but confounded
- **Honest framing:** Effectively re-uses s8-D1 IS bytes (zero new information at IS) and tests micros only at OOS. The strategy is no longer a single coherent candidate; it's two different strategies (full at IS, micro at OOS) joined under one name. DR4 evaluation becomes meaningless. Worst comparability.

### S10-D2 — Higher-capital full-contract successor

- **Universe:** ['NQ.c.0', 'GC.c.0', 'ZN.c.0', 'CL.c.0']
- **Binding constraint:** None (uses existing s8-D1 cache)
- **IS window:** 2013-01-01 to 2022-12-30  (10.0 years)
- **OOS window:** 2023-01-01 to 2025-12-30
- **Projected IS trades portfolio:** ~111  (K9 threshold = 100)
- **K9 likely to fire in-sample:** False
- **Sample-size risk:** LOW — full 10y IS window; >=111 trades expected; comfortable K9 clearance
- **Comparability risk:** LOW — single-parameter change (starting_cash $100k -> >=$476k); all other s8-D1 parameters byte-equivalent; clean attribution of any outcome difference
- **Addresses s8-D1 root cause cleanly:** True
- **In evidence terms:** True
- **Verdict predictability at C7:** UNKNOWN until run — could pass (READY_FOR_LONGER_BACKTEST) if signal survives at higher capital, or fail (INSUFFICIENT_SAMPLE/K1/K2/K4) if 2023-2025 OOS regime degraded the edge. True new information either way.
- **Honest framing:** Tests whether the s8-D1 signal works AS-DESIGNED at sufficient capital. All preregistered K-gates evaluable with adequate sample power. Practical limitation: $476k+ doesn't match typical $100k operator scale, so the answer is academic for smaller-capital users. But it's the only S10 path that produces preregistered statistical evidence on the s8-D1 signal under the OOS regime. Result will tell us: did s8-D1's signal genuinely survive 2023-2025 when capital wasn't the binding constraint, or was even the high-capital version not money-proven?

### S10-D5 — Stop/pivot — do not continue Donchian successor

- **Rationale:** Reallocate research attention. Parallel session is running s9-RSI-2 mean-reversion track. Operator may choose to focus there, or on other projects (hydra_video, youtube_growth, etc.).
- **Honest framing:** Legitimate operator choice; doesn't produce any new evidence on s8-D1.

---

## RECOMMENDATION

### Recommended: **`S10-D2` — Higher-capital full-contract successor (NQ+GC+ZN+CL, starting_cash >= $476k)**

### Rationale synthesis

The pure-micro path (S10-D1A) is the conceptually-right answer (fixes the exact $/pt sizing issue at $100k user scale), but Databento's historical coverage for MCL (launched 2021-07-12) limits the pure-micro in-sample window to ~17.5 months. At s8-D1's empirical 11.1 trades/year portfolio rate, that projects to ~17 IS trades — far below the K9 threshold of 100. The verdict would be INSUFFICIENT_SAMPLE by structural constraint, not strategy quality. S10-D1B (drop MCL) extends to 3.65 years but adds a second confound (3-market universe weakens K10/A7) and STILL fails K9 (~30 projected trades). S10-D1C (mixed full/micro) trivially re-uses s8-D1 IS bytes for IS (no new evidence) and confounds any IS-OOS divergence with the contract substitution. Only S10-D2 produces preregistered IS evidence with comfortable K9 clearance AND a single clean parameter delta (starting_cash). The honest tradeoff: S10-D2's $476k+ starting capital is less applicable to $100k operators, but the QUESTION it answers — did the s8-D1 signal survive 2023-2025 when capital wasn't the binding constraint? — is the load-bearing research question that should be answered before any future S11 micro candidate is attempted (perhaps in 2-3 years when micro contracts have more historical depth).

### What S10-D2 proves or disproves

- If S10-D2 OOS passes K-gates: the s8-D1 signal survived 2023-2025 OOS regime; capital was the limiting factor at $100k; a future S11 micro candidate with sufficient data depth becomes high-priority
- If S10-D2 OOS fails K1/K2 (signal collapse at OOS): s8-D1's IS signal did NOT survive 2023-2025 regardless of capital; the family is falsified for OOS; S11 micro would also fail; pivot research direction
- If S10-D2 OOS fails K4 (MaxDD blowup): risk per trade is too aggressive even at $476k; suggests a different sizing rule entirely, not a different contract size
- If S10-D2 OOS fails K10 (correlation regime shift): rare given OOS K10 PASS at s8-D1 OOS; would indicate further regime shift; pivot

### Secondary path (only if operator prefers micro despite constraints)

S10-D1A pure-micro can still be pursued as an OPERATIONAL feasibility test (knowing in advance that the C7 verdict will be INSUFFICIENT_SAMPLE due to K9 firing). This would establish that the strategy CAN open trades on all 4 markets at $100k OOS without producing preregistered statistical validation. Operator should explicitly acknowledge this framing if choosing S10-D1A.

### Rejected paths (brief rationale)

- **S10-D1A**: Conceptually right; structurally K9-blocked by Databento coverage. Operational feasibility test only.
- **S10-D1B**: Adds 3-market universe confound on top of the K9 problem. Strictly worse than S10-D1A.
- **S10-D1C**: IS bytes identical to s8-D1 (no new IS information). DR4 evaluation meaningless under contract substitution.
- **S10-D5**: Legitimate operator choice but doesn't answer the load-bearing s8-D1 follow-up question.

### What happens next IF operator accepts the recommendation

> AUTHORIZE S10-D2 Tier-N spec draft (PLAN-ONLY) — universe NQ.c.0+GC.c.0+ZN.c.0+CL.c.0; starting_cash_mnq_equivalent = $500,000 (round number above $476k NQ-clearing threshold); all other s8-D1 strategy parameters byte-equivalent; in-sample window 2013-01-01..2022-12-30; OOS window 2023-01-01..2025-12-30; uses existing s8-D1 cache; no new fetch required; single sealed pair under reports/external_research_hunter/s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_tier_n_spec.{md,json}.

- No Tier-N spec authored by this analysis: **True**
- Tier-N spec authoring requires separate explicit operator authorization: **True**

---

## Non-revival attestations

- `s8_d1_revived_by_this_analysis`: False
- `s7_d1_revived`: False
- `s7_d5_revived`: False
- `s8_d5_revived`: False
- `b005_001_revived`: False
- `nke_options_wheel_revived`: False
- `any_fresh_candidate_requires_separate_operator_authorization`: True
- `tier_n_spec_NOT_authored_in_this_analysis`: True

---

## Parent chain (8 byte-stable; drift=0)

- `S10_selection_plan`: `007110ff5a57dd04...`
- `S8_D1_P11_lifecycle`: `c79b06206c51d9b9...`
- `S8_D1_P9_5b_sizing`: `957ede055785faf0...`
- `S8_D1_P10_decision`: `a493931f0b812fad...`
- `S8_D1_P6_in_sample`: `07a3fa91509f2206...`
- `S8_D1_tier_n_spec`: `8cff6babf8e4a451...`
- `S8_D1_plan_lock`: `612abbbda7235c8c...`
- `S8_selection_plan`: `6b7bdb4c350f4a77...`

---

## Negative invariants this turn (all True)

- `no_audit_re_run`: True
- `no_b005_001_revival`: True
- `no_backtest`: True
- `no_candidate_record_id_reserved`: True
- `no_code_authored`: True
- `no_d5_revival`: True
- `no_data_fetch`: True
- `no_databento_api_call`: True
- `no_db_historical_instantiated`: True
- `no_frc_granted`: True
- `no_live_promotion`: True
- `no_live_trading_change`: True
- `no_network_call`: True
- `no_nke_revival`: True
- `no_obsidian_trade_logger_mutation`: True
- `no_oos_inspection`: True
- `no_paper_trading_change`: True
- `no_profitability_claim`: True
- `no_qc_api_call`: True
- `no_review_queue_mutation`: True
- `no_s7_d1_revival`: True
- `no_s8_d1_file_modification`: True
- `no_s8_d1_revival`: True
- `no_scheduler_change`: True
- `no_tier_n_spec_authored`: True

*End of S10 availability attestation analysis. Sealed at `417ed6c7b4e177e0681a3fe20a03744cb22c9946b9755e077a3def3afd7f50e7`. PLAN/ANALYSIS-ONLY. No Tier-N spec authored. No code. No backtest. No fetch.*
