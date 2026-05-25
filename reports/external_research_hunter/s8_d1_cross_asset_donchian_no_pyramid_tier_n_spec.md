# s8-D1 Cross-Asset Donchian No-Pyramid - Tier-N Spec (SEALED)

**Artifact type:** `tier_n_spec`
**Canonical record id:** `s8-cross-asset-donchian-no-pyramid-nq-gc-zn-cl`
**Spec version:** v1
**Phase:** `TIER_N_SPEC_SEALED_BUILD_NOT_AUTHORIZED`
**Authored UTC:** 2026-05-25T22:54:40Z
**Authored by:** SPARTA_CLAUDE

**Tier-N seal sha256:** `8cff6babf8e4a451adf02e94a684924ff8b32a7e0f5a795a13c65c845a12e0f4`
**Seal method:** `LESSON_HUNTER_004` canonical roundtrip

**Draft spec MD:** `docs/s8_d1_cross_asset_donchian_no_pyramid_spec.md`
**Draft spec MD sha256:** `ada2c060a63a9f3bba81ab43f6cf30a926b6cfb95b58784796f1f2c2846b9d52`
**Draft spec MD size:** 34631 bytes

> **Labels:** EXTERNAL_CLAIM_ONLY, NEEDS_VERIFICATION, NOT_A_SIGNAL,
> DIAGNOSTIC_ONLY_NOT_LIVE_GRADE, PLAN_AND_SPEC_ONLY, NO_FRC_GRANTED,
> S8_D1_CANDIDATE_TIER_N_SEALED, SINGLE_DELTA_FROM_S7_D1_MAX_UNITS_1,
> NO_S7_D1_REVIVAL, NO_D5_REVIVAL, NO_B005_001_REVIVAL, NO_NKE_REVIVAL

---

## Selection source

- **Selection plan JSON:** `reports/external_research_hunter/s8_next_candidate_selection_after_six_parks.json`
- **Selection plan seal:** `6b7bdb4c350f4a779611546dcb32f6a83db2371c66d7b6ba0118121783801441`
- **Selection score:** 39 / 40

**Selection rule cited from S8 plan:**

> D1 is the only direction that DIRECTLY tests the load-bearing remaining hypothesis from s7-D1: K4 fired at -221% DD; the proximate cause is pyramid amplification; the direct fix is removing the pyramid (max_units = 1). Every other direction either (a) doesn't address K4, (b) adds ad-hoc parameter knobs, (c) is a known overfit trap, or (d) is premature without D1's answer.

---

## Single delta from s7-D1

| Field | s7-D1 | s8-D1 |
|---|---|---|
| `max_units_per_market` | **4** | **1** |
| All other locked parameters | (s7-D1 spec) | (byte-equivalent) |

Mechanical effect: per market, at most 1 unit open at a time. Pyramid second-unit trigger (0.5N spacing) never fires under max_units=1. PyramidManager helper from s7-D1 works trivially with max_units=1.

---

## s7-D1 revival attestation

- **s7-D1 chain status:** `PERMANENTLY_PARKED_AT_COMMIT_f08220a`
- **s7-D1 revived by this spec:** `False`
- **s7-D1 used as:** UPSTREAM EVIDENCE AND MECHANICAL BASELINE ONLY
- **s7-D1 chain artifacts:** 14 (all byte-stable at authorship)
- **S-STOP-12 monitors s7-D1 byte-stability through s8 work**

---

## Locked parameters (excerpt)

| Parameter | Value |
|---|---|
| Entry channel length | 55 |
| Exit channel length | 20 |
| Stop multiplier | 2N |
| Wilder ATR period | 20 |
| `max_units_per_market` | **1** |
| Pyramid spacing (vestigial) | 0.5N |
| Per-unit risk | 1.0% portfolio equity |
| Entry timing | ONO |
| Filter | NONE (AMB6 locked) |
| Universe | NQ.c.0, GC.c.0, ZN.c.0, CL.c.0 |
| In-sample window | 2013-01-01..2022-12-30 UTC |
| OOS window | 2023-01-01..2025-12-30 UTC (no inspection in-sample) |
| Starting cash | $100,000 MNQ-equivalent |
| Portfolio cap | 4 markets x 1 unit = 4 units max (structurally non-binding) |

---

## Cost-stress matrix (inherited byte-equivalent from s7-D1)

| Tier | Slip x | Cost x | Purpose |
|---|---|---|---|
| S0 | 0 | 0 | Diagnostic floor (DR3 fires if S0-only) |
| S1 | 1 | 1 | Baseline preregistered |
| S2 | 3 | 1.5 | Mild stress |
| S3 | 5 | 2 | Realistic adverse |
| S4 | 8 | 3 | Tail stress (informational only) |

DR rules: DR2 (S2/S3 degrade), DR3 (S0-only survival), DR4 (IS+ OOS-), DR5 (S0->S1 negative).

---

## Acceptance gates (all must pass)

- **A1** closed trades portfolio >= 100
- **A2** sharpe_proxy_per_trade > 0
- **A3** expectancy_per_trade > 0
- **A4** trade_curve_maxdd_pct <= 50% magnitude (the gate that fired in s7-D1)
- **A5** >= 2 of 4 markets WR-gap >= 0 and portfolio WR-gap >= +0.5pp
- **A6** validator pass 16/16 + s8 specific
- **A7** effective independent bets >= 2.5
- **A8** cost-stress S0-S4 run; DR2/DR3/DR5 not fired
- **A9** Phase 2 C1-C8 inheritance attestable
- **A10** cap_binding_events_count == 0 portfolio level

---

## Rejection gates (kill criteria)

| K | Trigger | Park status |
|---|---|---|
| K1 | sharpe_proxy < 0 | PARKED_SAFE_BUT_NOT_MONEY_PROVEN |
| K2 | expectancy <= 0 | PARKED_SAFE_BUT_NOT_MONEY_PROVEN |
| K4 | trade_curve_maxdd_pct > 50 | PARKED_SAFE_BUT_NOT_MONEY_PROVEN |
| K6 | safety_warning_count > 0 | PARKED_SAFETY_FAILED |
| K7 | filter/correlation gate silently introduced | PARKED_SAFETY_FAILED |
| K8 | sealed_parent_drift > 0 | PARKED_PROVENANCE_BROKEN |
| K9 | closed_trades < 100 | PARKED_FAILED_AT_INSUFFICIENT_SAMPLE |
| K10 | avg_pairwise_corr > 0.50 | PARKED_FAILED_AT_DIVERSIFICATION_HYPOTHESIS |
| K11 | cap_binding > 1000 | PARKED_CAP_BINDING |
| K12 | DR2/DR3/DR5 fire | REJECT_FAST |

Threshold-lock invariant: loosening post-seal forbidden; tightening requires fresh `_revN_` spec.

---

## Inherited seal registry (17 parents, all byte-stable at authorship)

| Inherited | sha256 | reason |
|---|---|---|
| `phase2_safety_template_json` | `695a9fb6e0cb6ae5...` | PHASE_2_C1_C8_SAFETY_TEMPLATE_JSON_SOURCE |
| `phase2_safety_template_md` | `1812f4854a23e7a1...` | PHASE_2_C1_C8_SAFETY_TEMPLATE_MD_SOURCE |
| `s7_d1_blocked_report` | `f0f465d4c9b9199c...` | P6_FAILURE_AUDIT_TRAIL |
| `s7_d1_decision_memo` | `5354d3395319e309...` | DECISION_RATIONALE_TO_PARK_S7_D1_AND_GO_TO_S8 |
| `s7_d1_diag_prior_p65` | `157ad1bf5a8994ea...` | PRIOR_BUGGY_P65_RESULT_HISTORICAL_RECORD_NOT_STRATEGY_INTERPRETATION |
| `s7_d1_diag_rev2` | `2563ef9309217171...` | OPERATIVE_S7_D1_STRATEGY_RESULT_LOAD_BEARING_EVIDENCE |
| `s7_d1_driver_build_report` | `26e9c6f0c217f1f2...` | LOCAL_DATABENTO_DRIVER_BASELINE |
| `s7_d1_execution_guard_build_report` | `5cfbfdbbb9fc6956...` | EXECUTION_GUARD_PATTERN_BASELINE |
| `s7_d1_p65a_patch_plan` | `d03201de481f8712...` | OFF_BY_ONE_PATCH_AUDIT_TRAIL |
| `s7_d1_parking_report` | `551fdce46c0e373e...` | S7_D1_PERMANENT_PARK_STATE_NOT_REVIVED_BY_S8_D1 |
| `s7_d1_patch_build_report` | `2ab3ed5852de0dad...` | PATCHED_DRIVER_MECHANIC_INHERITED_AS_BASELINE_FOR_S8_D1 |
| `s7_d1_phase2_plan` | `e1800ee28bd99a27...` | PHASE2_C1_C8_SAFETY_TEMPLATE_INHERITED_BYTE_EQUIVALENT |
| `s7_d1_plan_lock` | `0f8e9fe6bc4f50e4...` | PLAN_LOCK_PATTERN_REFERENCE |
| `s7_d1_runner_build_report` | `10610a6ad47c2fd5...` | RUNNER_HARNESS_PATTERN_BASELINE |
| `s7_d1_smoke_pass_report` | `ec244e92953ab850...` | T1_T15_SMOKE_TEST_PATTERN_BASELINE |
| `s7_d1_tier_n_spec` | `72602305ef8d6781...` | STRATEGY_PARAMETER_BASELINE_ALL_PRESERVED_EXCEPT_MAX_UNITS_DELTA |
| `s8_selection_plan` | `6b7bdb4c350f4a77...` | DIRECT_PREDECESSOR_RECOMMENDS_S8_D1_AT_39_OF_40 |

Drift count at authorship: **0**

---

## Boundaries held by this Tier-N spec

- No code authored this turn
- No Databento call, no QC call, no fetch, no network call
- No backtest, no run, no OOS inspection
- No live trading change, no paper trading change, no scheduler change
- No review_queue.json mutation, no Strategy Lab promotion
- No obsidian-trade-logger mutation
- No credential logged, no Databento key printed
- No D5 revival (neither s7 YM-only nor s8 ZN-only)
- No B005_001 revival, no NKE revival, no s7-D1 revival
- FRC never granted; no profitability claim

---

## Next step (requires separate explicit operator authorization for each)

1. P1 plan-lock authoring
2. P2 Phase-2 plan-doc authoring
3. P3 BUILD ONLY (runner + execution_guard + tests; under s8-D1 namespace)
4. P4 T1-T15 synthetic smoke pass
5. (no P5 fetch needed - s7-D1 P5 cache re-usable)
6. P6 in-sample run at S1 baseline (optionally S0/S2/S3/S4)
7. P7 in-sample decision memo
8. P8 lifecycle transition (PARK or OOS-AUTHORIZE)

No step pre-approved by this spec. Each requires explicit operator AUTHORIZE.

---

*End of s8-D1 Tier-N spec (SEALED). Spec only - no code, no backtest, no Databento, no QC, no fetch, no live/paper trading, no scheduler change, no obsidian mutation, no review_queue mutation, no D5/B005_001/NKE/s7-D1 revival.*
