# S13-D1 P2 phase-2 plan (sealed)

**Candidate record id:** `s13-d1-mnq-c0-single-instrument-rsi-2-bi-directional-databento-long-history`
**Phase prefix:** `PHASE2-S13-D1-MNQ-RSI-2-BIDIR`
**Authored (UTC):** `2026-05-27T17:17:18.601799Z`
**Lifecycle state:** P2_PHASE_2_PLAN_SEALED
**Tier-N spec inherited:** commit `262491c` (seal `2f9d176388fe0b66c9ced19f33c68e079bb08112f3d52f3f20a9aba7d91bf775`)
**P1 plan-lock inherited:** commit `005cb8a` (seal `1cac253cbbbf4cdab87e777edbe0bca00739e925de382bd1d687faae9731052c`)
**Report seal sha256:** `b181ce834f5eacd2fb9f6766d6ce9404a86ecfe3d2787c7e4899d3e47ba57ec6`
**Seal method:** LESSON_HUNTER_004 canonical roundtrip
**Reseal verified on disk:** YES (UTF-8 explicit)

## Anchors carried binding into C6

| Carried-binding field | Value | Origin |
|---|---|---|
| **DA3** per-trade risk | **0.5%** | DA3=B revised at SEAL for DR3 mitigation |
| **DA4** START_CASH | **$200,000** | DA4=C revised at SEAL for DR10 mitigation |
| K9-reachability discipline | applied at IS AND OOS | new framework standard from `0e3f9d4` |
| REC1-equivalent OOS K9 disclosure | binding (priority HIGH) | carried byte-equivalent from SEAL |

## Template inheritance

Adapts C1-C8 byte-equivalent from `docs/phase2_safety_contract_template.md`. NKE strategy logic NOT inherited (only safety contracts).

### Single-instrument futures + RSI(2) bi-directional adaptations

| Adaptation | Status |
|---|---|
| C5 corporate-action / event-risk | **STRUCTURALLY_ABSENT** (futures continuous-stitch) |
| C3 extended_hours_fill_warning_count | NOT_APPLICABLE (futures session) |
| C3 unsupported_order_type_detected_count | NOT_APPLICABLE (CSV simulator) |
| C4 RTH window | 09:30-16:00 ET America/New_York |
| C3 RSI-specific counters | NEW: `rsi_2_signal_count_per_year`, `atr_stop_breach_count`, `rsi_long_short_balance_ratio` |
| DR3 prior probability | **ELEVATED** (RSI lineage s9 precedent); mitigated via DA3=B |
| DR10 prior probability | **ELEVATED** (high-frequency ~50-65/y); mitigated via DA4=C |

## C1 -- LiveMode refusal

```python
if self.LiveMode:
    raise Exception(
        "LIVE_PATH_DETECTED: s13-d1-mnq-c0-single-instrument-rsi-2-bi-directional "
        "is paper-only forever; refuse to run in live mode."
    )
```

Output JSON `status_fields`: `trading_status: "PAUSED"` · `live_status: "BLOCKED_AT_6_GATES"` · `backtest_diagnostic_only: True` · `frc_status: "NEVER_GRANTED"`.

## C2 -- Provenance contract

Required CONFIG fields: `tier_spec_seal=2f9d176388fe0b66...`, `plan_lock_seal=1cac253cbbbf4cda...`, `p2_phase2_plan_seal=b181ce834f5eacd2...`, `algo_version_for_run_id=s13_d1_v0_1_0`, `start_date_is=(2019,5,13)`, `end_date_is=(2023,12,29)`, `start_date_oos=(2024,1,2)`, `end_date_oos=(2025,12,30)`, `plan_lock_window_ceiling=(2025,12,30)`.

Initialize cross-check + ceiling check + deterministic run_id via 7 hashed inputs (engine-truth dates; NOT CONFIG dates).

## C3 -- Safety counters

Universal: `stale_fill_warning_count` (0), `all_safety_warnings_zero` (True iff all zero), `forbidden_action_attempts_detected` (empty).

s13-d1-specific NEW counters: `rsi_2_signal_count_per_year`, `atr_stop_breach_count`, `rsi_long_short_balance_ratio` (disclosure-only).

Unique-day counter pseudocode pattern (NKE v6.1 lesson; set-based).

## C4 -- RTH execution discipline

CONFIG: `rth_safe_window_open=(9,30)`, `rth_safe_window_close=(16,0)`, `eod_cancel_time=(16,0)` (== close; boundary alignment), `tz=America/New_York`.

LIMIT-order discipline NOT_APPLICABLE at P6 CSV-simulator level.

## C5 -- Corporate-action / event-risk (STRUCTURALLY_ABSENT for futures)

`known_corporate_actions = []`. Quarterly roll handled vendor-side via Databento `stype_in=continuous`. `futures_roll_method_modification_post_seal_forbidden: True`.

## C6 -- Diagnostic output schema (LOAD-BEARING; carries operator-binding constraints)

### Required `inherited_constraints_block` (verbatim binding; appears in every output JSON)

1. REC1-equivalent (BINDING): OOS K9 reachable at lower bound with thin margin (~50-65 trades/year vs 50/year floor). If observed IS rate falls below 25/year on RSI(2) bi-directional, OOS K9 unreachability becomes structurally probable. The s9 RSI-2 baseline observed 414 trades over long-only 4-ETF window; if MNQ.c.0 bi-directional rate falls below half that proportional rate, OOS K9 fires. If OOS K9 fires, the OOS verdict shall be OOS_INSUFFICIENT_SAMPLE or PARKED_SAFE_BUT_OOS_INDETERMINATE analogous to S10-D2 P11 PARK at 23c7164 and s12-d1 P11 park at ecbd001. The chain shall NOT relax K9 at OOS; the appropriate response is to seal the INSUFFICIENT_SAMPLE / INDETERMINATE verdict and park the candidate. Pursuing s13-d1 accepts the structural possibility of an OOS PARK outcome if the IS rate falls below the DRAFT-estimated 50-65/y band.
2. DA3=B (BINDING): per-trade risk pct = 0.005 (0.5%); REVISED at SEAL from default 1.0% for DR3 mitigation (s9 RSI lineage cost-erosion precedent)
3. DA4=C (BINDING): START_CASH_USD = 200000 ($200k); REVISED at SEAL from default $100k for DR10 mitigation (high-frequency turnover); halves per-dollar cost pressure
4. K9-reachability discipline (NEW framework standard from selection-plan revision 0e3f9d4) applied at PLAN + DRAFT + SEAL + P1 + P2; binding for all subsequent phases
5. K9_THRESHOLD_INVIOLATE: closed_trades >= 100; no relaxation at any phase
6. Mechanic family F3 RSI(2) bi-directional mean-reversion LOCKED at PLAN; no reopening at DRAFT/SEAL
7. RSI thresholds 10/50/90/50 LOCKED at PLAN; threshold modification post-SEAL FORBIDDEN per RF13
8. DR3 risk ELEVATED (RSI lineage s9 falsification precedent); mitigated via DA3=B
9. DR10 risk ELEVATED (high-frequency turnover ~50-65 trades/y); mitigated via DA4=C ($200k START_CASH)
10. Tier-N spec LOCKED byte-equivalent at 262491c (sha 2f9d176388fe0b66c9ced19f33c68e079bb08112f3d52f3f20a9aba7d91bf775)
11. P1 plan-lock LOCKED byte-equivalent at 005cb8a (sha 1cac253cbbbf4cdab87e777edbe0bca00739e925de382bd1d687faae9731052c)
12. s12-d1 terminal park (PARKED_SAFE_BUT_INSUFFICIENT_SAMPLE_AT_IS at ecbd001) preserved unchanged
13. All parallel-session shorter-path sealed artifacts byte-stable; not anchored by this chain
14. Expected terminal verdict if OOS K9 fires: PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED (analogous to S10-D2 P11 PARK)
15. P2 PASS does NOT imply READY_FOR_LONGER_BACKTEST; requires P6 IS diagnostic under separate authorization
16. P2 PASS NEVER implies live-readiness; 6-gate live-block applies regardless of any verdict

### Performance summary required fields (s13-d1 specifics)

- `starting_cash_usd: 200000` (DA4=C)
- `max_drawdown_pct` (magnitude-based per s11-d1 rev2)
- `annual_turnover` (DR10 monitoring; ELEVATED)
- `s2_cost_drag_fraction` (DR10 critical threshold)
- `rsi_2_signal_density_per_year` (K9-reachability monitoring)
- `rsi_long_short_balance_ratio` (bi-directional symmetry diagnostic)
- `win_rate_pct_or_NA_INSUFFICIENT_SAMPLE` (literal string when n<100)

## C7 -- Verdict semantics

Closed enum: `FAIL_SAFETY` / `INSUFFICIENT_SAMPLE` / `READY_FOR_LONGER_BACKTEST`.

Precedence: unsupported_order_type (N/A) > stale_fill > K9<100 (INSUFFICIENT_SAMPLE) > else READY_FOR_LONGER_BACKTEST.

Thresholds: `verdict_min_closed_trades=100`, `verdict_max_drawdown_pct_magnitude_fail_safety=0.50` (DA5=A).

**REC1-equivalent at C7 (BINDING):** EXPECTED OOS verdict if IS rate below 25/year is INSUFFICIENT_SAMPLE / OOS_INDETERMINATE. READY_FOR_LONGER_BACKTEST at IS does NOT imply OOS will reach READY.

## C8 -- Candidate lifecycle

Allowed statuses include `PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED` (s13-d1 expected if OOS K9 fires; analogous to S10-D2 P11 PARK at `23c7164` and s12-d1 P11 PARK at `ecbd001`).

**Revival from PARKED requires fresh sealed research cycle** (fresh seals; new plan-lock; not a continuation).

Permanent attributes unchanged by parking include `REC1-equivalent oos_k9_risk_disclosure binding`, `RSI thresholds 10/50/90/50 LOCKED at PLAN`, `DA3=B + DA4=C carried-binding`.

**Weak-performance rejection rule (LOAD-BEARING):** If Sharpe<0 AND expectancy<=0 AND PLR<0.5 AND closed_trades>=100, operator MUST park. No parameter iteration. Optimization forbidden.

## Pre-flight checklist for P3 BUILD

(See JSON sidecar for full content.) Key:
- T1 Sealed sha256s match disk: `tier_spec_seal=2f9d176388fe0b66...`, `plan_lock_seal=1cac253cbbbf4cda...`
- T2 Window ceiling: `end_date_oos=(2025,12,30) <= plan_lock_window_ceiling=(2025,12,30)`
- T3 Boundary alignment: `rth_safe_window_close == eod_cancel_time == (16,0)`
- T4-T6 NOT_APPLICABLE (CSV simulator)
- T7 P4 synthetic smoke (T1-T15 + T7b + T7c) per P1 §10
- T8 Validator pass at P4
- T9 Verdict semantics: READY_FOR_LONGER_BACKTEST not interpreted as live-ready; REC1-equivalent carried into output JSON `inherited_constraints_block`

## What this P2 plan does NOT include

- NO strategy logic beyond what's locked in SEAL + P1
- NO NKE-specific values
- NO live-promotion path
- NO revival of s12-d1 terminal park
- NO optimization permission
- NO DR threshold relaxation
- NO K9 relaxation
- NO RSI threshold modification
- NO modification of s11-d1 / s12-d1 / s13-d1 sealed chain
- NO modification of parallel-session shorter-path artifacts
- NO modification of `lessons.md`

## Negative invariants

(See JSON sidecar `negative_invariants_for_p2_plan_usage`; 15 entries; all False.)

Key: `rec1_equivalent_oos_k9_disclosure_demoted_to_advisory: False`, `da3_b_or_da4_c_demoted_to_advisory_only: False`, `rsi_thresholds_silently_modified: False`.

## Citation block for P3 BUILD to embed

```
# Inherits Phase 2 safety contracts (C1-C8) from:
#   docs/phase2_safety_contract_template.md
# Template source candidate (parked, not money-proven):
#   s2-62fc753afc01f22c (NKE Options Wheel Tier-1 v6.1)
# Template reuse: NKE strategy logic NOT inherited; only safety contracts.
# s13-d1 specific adaptations:
#   - C5 corporate-action/event-risk STRUCTURALLY_ABSENT (futures)
#   - C3 extended_hours / unsupported_order_type NOT_APPLICABLE
#   - DR3 ELEVATED (RSI s9 lineage); mitigated via DA3=B
#   - DR10 ELEVATED (high-frequency); mitigated via DA4=C
#   - REC1-equivalent + DA3=B + DA4=C + K9-reachability carried binding in C6
# Anchors:
#   tier_n_spec_seal     = 2f9d176388fe0b66c9ced19f33c68e079bb08112f3d52f3f20a9aba7d91bf775
#   p1_plan_lock_seal    = 1cac253cbbbf4cdab87e777edbe0bca00739e925de382bd1d687faae9731052c
#   p2_phase2_plan_seal  = b181ce834f5eacd2fb9f6766d6ce9404a86ecfe3d2787c7e4899d3e47ba57ec6
```

## Explicit next-phase requirement

P2 phase-2 plan authoring + sealing + commit completes here. The NEXT phase is **P3 BUILD**. P3 BUILD REQUIRES SEPARATE OPERATOR AUTHORIZATION via the phrase: **`Authorize s13 D1 MNQ.c.0 P3 BUILD only`**.

P3 BUILD creates 16 files in `external_research_hunter/s13_d1_mnq_c0_single_instrument_rsi_2_bi_directional_databento_long_history_runner_harness/` namespace per P1 plan-lock §1.

**NO PHASE BEYOND P3 IS PRE-APPROVED by this P2.**

## Parent references (READ-ONLY)

| Field | Value |
|---|---|
| Tier-N SEAL | commit `262491c` / sha `2f9d176388fe0b66c9ced19f33c68e079bb08112f3d52f3f20a9aba7d91bf775` |
| P1 plan-lock | commit `005cb8a` / sha `1cac253cbbbf4cdab87e777edbe0bca00739e925de382bd1d687faae9731052c` |
| s13-d1 PLAN | commit `5e57984` |
| s13-d1 DRAFT | commit `8fcefaf` |
| Selection-plan revision | commit `0e3f9d4` |
| s12-d1 P11 park (TERMINAL) | commit `ecbd001` |
| s9 RSI-2 ETF-proxy | PARKED_SAFE_BUT_NOT_MONEY_PROVEN |
| MNQ.c.0 CSV path | `data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_c_0_ohlcv_1d_20190513_20251230.csv` |
| MNQ.c.0 CSV sha256 | `8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e` |

## Status

| Field | Value |
|---|---|
| trading_status | PAUSED |
| live_status | BLOCKED_AT_6_GATES |
| frc_status | NEVER_GRANTED |
| research_label | DIAGNOSTIC_ONLY_NOT_LIVE_GRADE |
| lifecycle_state | P2_PHASE_2_PLAN_SEALED |
| K9_THRESHOLD_INVIOLATE | True |
| REC1_EQUIVALENT + DA3=B + DA4=C + K9-reachability carried binding in C6 | True |

## Seal metadata

- **Report seal sha256:** `b181ce834f5eacd2fb9f6766d6ce9404a86ecfe3d2787c7e4899d3e47ba57ec6`
- **Seal method:** LESSON_HUNTER_004 canonical roundtrip
- **Reseal verified on disk:** YES (UTF-8 explicit)
