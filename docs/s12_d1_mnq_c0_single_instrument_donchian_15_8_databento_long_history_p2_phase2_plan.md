# S12-D1 P2 phase-2 plan (sealed)

**Candidate record id:** `s12-d1-mnq-c0-single-instrument-donchian-15-8-databento-long-history`
**Phase prefix:** `PHASE2-S12-D1-MNQ-DONCHIAN-15-8`
**Authored (UTC):** `2026-05-27T15:14:39.017279Z`
**Lifecycle state:** P2_PHASE_2_PLAN_SEALED
**Tier-N spec inherited byte-equivalent:** commit `66bbbd1` (seal `07c3200b5e23ab88e864f92926b83ded033a3d66c0e37e8cf8555985ad8f3b48`)
**P1 plan-lock inherited byte-equivalent:** commit `d8bd359` (seal `eb72798eb95c08407ead9c273a650853bd5e871942856f87b48f97f07a640340`)
**Report seal sha256:** `689dd3d06c0e2518ab5f6105544cb3d38194027647de10940da976e427c8efa9`
**Seal method:** LESSON_HUNTER_004 canonical roundtrip
**Reseal verified on disk:** YES

## Template inheritance

This P2 phase-2 plan adapts C1-C8 byte-equivalent from `docs/phase2_safety_contract_template.md` (source candidate parked: `s2-62fc753afc01f22c` NKE Options Wheel Tier-1 v6.1 -- PARKED_SAFE_BUT_NOT_MONEY_PROVEN). NKE strategy logic is NOT inherited; only the eight safety contracts.

### Anchors (READ-ONLY; preserved byte-stable)

- s12-d1 SEAL: commit `66bbbd1` (sha `07c3200b5e23ab88e864f92926b83ded033a3d66c0e37e8cf8555985ad8f3b48`)
- s12-d1 P1 plan-lock: commit `d8bd359` (sha `eb72798eb95c08407ead9c273a650853bd5e871942856f87b48f97f07a640340`)
- **REC1 `oos_k9_risk_disclosure` carried byte-equivalent: BINDING** (per operator authorization phrase: *"Preserve REC1 oos_k9_risk_disclosure as binding"*)
- Parallel-session SEAL at `9ce4d66`: acknowledged, NOT anchored

### Single-instrument futures adaptations

| Contract aspect | Adaptation |
|---|---|
| **C5** corporate-action / event-risk | **STRUCTURALLY_ABSENT** (futures continuous-stitch via Databento `stype_in=continuous`; no splits, no dividends, no option corporate actions; quarterly roll vendor-side) |
| **C3** `extended_hours_fill_warning_count` | NOT_APPLICABLE (single-instrument futures session structure; no equity-options extended-hours-as-violation semantics) |
| **C3** `unsupported_order_type_detected_count` | NOT_APPLICABLE (CSV-based simulator at P6; no QC live brokerage path in s12-d1's chain) |
| **C4** RTH window | 09:30-16:00 ET America/New_York (MNQ regular session) |
| **C4** EOD cancel | trivially aligned (daily bars; `eod_cancel_time == rth_safe_window_close == (16,0)`) |

## C1 -- LiveMode refusal

**Required Initialize block:**
```python
if self.LiveMode:
    raise Exception(
        "LIVE_PATH_DETECTED: s12-d1-mnq-c0-single-instrument-donchian-15-8 "
        "is paper-only forever; refuse to run in live mode."
    )
```

**Required output JSON `status_fields`:**
- `trading_status: "PAUSED"`
- `live_status: "BLOCKED_AT_6_GATES"`
- `backtest_diagnostic_only: True`
- `frc_status: "NEVER_GRANTED"`

**Must NOT:** ever conditionally bypass the LiveMode check; reduce the status strings to anything weaker than PAUSED / BLOCKED_AT_6_GATES.

## C2 -- Provenance contract

### Required CONFIG fields (s12-d1-specific values pre-populated from SEAL + P1)

| Field | Value |
|---|---|
| `tier_spec_seal` | `07c3200b5e23ab88e864f92926b83ded033a3d66c0e37e8cf8555985ad8f3b48` |
| `plan_lock_seal` | `eb72798eb95c08407ead9c273a650853bd5e871942856f87b48f97f07a640340` |
| `plan_doc_sha256` | populated at P3 BUILD (sha256 of P1 plan-lock MD on disk) |
| `algo_version_for_run_id` | `s12_d1_v0_1_0` |
| `start_date_is` | `(2019, 5, 13)` |
| `end_date_is` | `(2023, 12, 29)` |
| `start_date_oos` | `(2024, 1, 2)` |
| `end_date_oos` | `(2025, 12, 30)` |
| `plan_lock_window_ceiling` | `(2025, 12, 30)` |

### Required `_compute_deterministic_run_id` inputs (hashed in order)

1. `tier_spec_seal`
2. `plan_lock_seal`
3. `plan_doc_sha256`
4. Phase literal tag: `b"PHASE2-S12-D1"`
5. `algo_version_for_run_id`
6. `self.StartDate.date()` (**engine truth, NOT CONFIG**)
7. `self.EndDate.date()` (**engine truth, NOT CONFIG**)

### Required Initialize cross-check (after `SetStartDate`/`SetEndDate`)

- `if self.StartDate.date() != date(*CONFIG['start_date_<phase>']) -> raise CONFIG_START_DATE_MISMATCH`
- `if self.EndDate.date() != date(*CONFIG['end_date_<phase>']) -> raise CONFIG_END_DATE_MISMATCH`

### Required ceiling check

- `if self.EndDate.date() > date(*CONFIG['plan_lock_window_ceiling']) -> raise WINDOW_EXTENSION_BEYOND_PLAN_LOCK_FORBIDDEN`

### Required output naming + seal

- `<output_dir>/<prefix>_<run_id_12hex>.{json,md}`
- `report_seal_sha256` via LESSON_HUNTER_004 canonical roundtrip (excluding `report_seal_sha256` + `seal_method`)

**Must NOT:** hash run_id from operator-mutable fields; skip the Initialize date cross-check; use CONFIG dates for run_id or CAGR when engine dates are readable; allow run_id from a hardcoded literal.

## C3 -- Safety counters

### Universal counters (every inheritor MUST track)

| Counter | Type | Required value for safety_zero |
|---|---|---|
| `stale_fill_warning_count` | int | 0 |
| `all_safety_warnings_zero` | bool | True iff all applicable counters are 0 |
| `forbidden_action_attempts_detected` | list | empty for READY_FOR_LONGER_BACKTEST |

### Asset-class-conditional counters -- s12-d1 status

| Counter | s12-d1 status |
|---|---|
| `extended_hours_fill_warning_count` | NOT_APPLICABLE (futures session structure) |
| `expiry_or_settlement_fills_outside_rth_count` | NOT_APPLICABLE (continuous front-month; vendor-side roll; no expiry surface) |
| `unsupported_order_type_detected_count` | NOT_APPLICABLE (CSV simulator; no QC live brokerage) |
| `donchian_15_8_signal_count_per_year` | NEW s12-d1-specific (disclosure; for DR10 risk monitoring) |
| `atr_stop_breach_count` | NEW s12-d1-specific (disclosure; for whipsaw signature detection) |

### Pseudocode pattern for unique-day counters (NKE v6.1 lesson; LOAD-BEARING)

```python
# Use a set of date objects, NOT a per-OnData increment
if today not in self._<category>_dates_seen:
    self._<category>_skip_count += 1
    self._<category>_dates_seen.add(today)
```

This prevents the inflated-counter defect observed in NKE v5/v6/v6.1 where per-minute-bar OnData increments produced counter values >300x the true unique-day count.

**Must NOT:** conflate QC lifecycle events with operator violations; mutate a counter without a corresponding `_forbidden_action_attempts` or `_skip_log` entry; use per-minute increments when per-day is intended.

## C4 -- RTH execution discipline

### Required CONFIG for s12-d1

| Field | Type | Value |
|---|---|---|
| `rth_safe_window_open` | tuple H,M | `(9, 30)` |
| `rth_safe_window_close` | tuple H,M | `(16, 0)` |
| `eod_cancel_time` | tuple H,M | `(16, 0)` (**MUST EQUAL `rth_safe_window_close`**) |
| `rth_window_tz` | string | `America/New_York` |
| `max_quote_age_seconds` | -- | NOT_APPLICABLE (daily bars) |
| `max_relative_spread` | -- | NOT_APPLICABLE (daily bars) |

### Required per-candidate checks (s12-d1 daily-bar adaptation)

1. Daily bar at RTH close (16:00 ET America/New_York)
2. Intraday bid/ask/spread/quote-age checks NOT APPLICABLE for daily-bar OHLCV ingestion
3. EOD cleanup trivially satisfied for daily-bar design (CSV simulator fills atomically per daily bar)

### Boundary alignment rule (NKE v6 lesson; LOAD-BEARING)

`eod_cancel_time` MUST equal `rth_safe_window_close`. **Trivially satisfied for s12-d1:** both equal `(16, 0)`.

### LIMIT-order discipline

NOT APPLICABLE at P6 CSV-simulator level. The simulator transacts at daily close. LIMIT-order discipline would apply only at a hypothetical future QC live-path which is BLOCKED by the 6-gate live-block invariant.

**Must NOT:** set `eod_cancel_time` later than `rth_safe_window_close`; submit MarketOrder/MarketOnClose for opens at a future QC path; use a wider RTH safe window than the MNQ regular session.

## C5 -- Corporate-action / event-risk contract

### s12-d1 status: STRUCTURALLY_ABSENT

**Rationale:** MNQ.c.0 is a continuous front-month futures contract synthesized vendor-side by Databento (`stype_in=continuous`). Futures do NOT have stock splits, dividends, or option-style corporate actions. Quarterly contract roll is handled by the Databento continuous-stitch (documented in s10-D1 audit; sealed CSV at sha `8b7b832c...fa23e`). The C5 corporate-action blackout / `known_corporate_actions` / LIMIT pre-close / MOC-rejection-detection mechanisms are STRUCTURALLY ABSENT for this candidate.

### Required CONFIG for s12-d1

| Field | Value |
|---|---|
| `known_corporate_actions` | `[]` (empty list; STRUCTURALLY_ABSENT) |
| `corp_action_blackout_days_before` | NOT_APPLICABLE |
| `corp_action_blackout_days_after` | NOT_APPLICABLE |
| `corp_action_pre_close_aggressive_ticks` | NOT_APPLICABLE |
| `futures_roll_method` | Databento native continuous-front-month synthesis (`stype_in=continuous`); vendor-side; byte-equivalent from s11-d1 v1 |
| `futures_roll_method_modification_post_seal_forbidden` | True |

### Operator responsibilities for s12-d1

- Verify the sealed MNQ.c.0 CSV at sha `8b7b832c...fa23e` remains byte-stable on disk at every phase
- No fresh fetch authorized; no re-stitching authorized; no roll-override authorized

**Must NOT:** introduce a synthetic corporate-action list to apply equity-class C5 logic to futures; submit MarketOnClose for the underlying contract; modify the Databento continuous-stitch method post-seal.

## C6 -- Diagnostic output schema

### Required top-level fields (universal)

See JSON sidecar `c6_diagnostic_output_schema.required_top_level_fields_universal` for the full list (26 required fields). Key load-bearing items:

- `schema_id` (candidate-specific; ends in `.v1`)
- `backtest_run_id` (`<PREFIX>-<run_id_12hex>`)
- `report_seal_sha256` (LESSON_HUNTER_004 canonical roundtrip)
- `linked_seals_at_init` (dict citing `tier_spec_seal`, `plan_lock_seal`, `p2_phase2_plan_seal`)
- `inherited_constraints_block` (list; **MUST include REC1 oos_k9_risk_disclosure verbatim**)
- `status_fields` (dict; `PAUSED` / `BLOCKED_AT_6_GATES`)
- `verdict` (closed enum)

### `performance_summary` required fields (s12-d1 specifics)

- `starting_cash_usd: 100000` (per DA4=B)
- `max_drawdown_pct` (**magnitude-based** per s11-d1 rev2 condition (e) correction byte-equivalent)
- `cagr_pct` (computed from `self.StartDate`/`self.EndDate`; NOT CONFIG)
- `win_rate_pct_or_NA_INSUFFICIENT_SAMPLE` (literal string `"NA_INSUFFICIENT_SAMPLE"` when `closed_trades < verdict_min_closed_trades`)
- `annual_turnover` (for DR10 monitoring)
- `s12_d1_specific_donchian_15_8_signal_density_per_year`

### REC1 inherited_constraints_block content (verbatim; LOAD-BEARING; binding)

> *"OOS K9 EXPECTED TO FIRE. Implied OOS trade count over 2.0y at IS rate is approximately 35-87 trades, below K9 = 100. If OOS K9 fires, the OOS verdict will be OOS_INSUFFICIENT_SAMPLE or PARKED_SAFE_BUT_OOS_INDETERMINATE analogous to S10-D2 P11 PARK at `23c7164`. The chain shall NOT relax K9 at OOS; the appropriate response is to seal the INSUFFICIENT_SAMPLE / INDETERMINATE verdict and park the candidate. Pursuing s12-d1 accepts the structural likelihood of an OOS PARK outcome."*

**Must NOT:** emit `win_rate` as a number when `closed_trades < verdict_min_closed_trades`; compute CAGR from CONFIG dates; omit `report_seal_sha256`; silently bump `schema_id`; **omit REC1 oos_k9_risk_disclosure from `inherited_constraints_block`**.

## C7 -- Verdict semantics

### Closed-enum allowed verdicts

- `FAIL_SAFETY`
- `INSUFFICIENT_SAMPLE`
- `READY_FOR_LONGER_BACKTEST`

### Verdict precedence (high to low; s12-d1 adapted)

1. `unsupported_order_type_detected_count > 0` -> FAIL_SAFETY (top priority; **NOT APPLICABLE** for s12-d1)
2. `stale_fill_warning_count > 0` -> FAIL_SAFETY (`extended_hours_fill_warning_count` NOT APPLICABLE for s12-d1)
3. `closed_trades < verdict_min_closed_trades` (= 100; K9 byte-equivalent) -> INSUFFICIENT_SAMPLE
4. else -> READY_FOR_LONGER_BACKTEST (with caveats appended to `verdict_reasons` if n < 100, DD > concern, etc.)

### Required CONFIG thresholds for s12-d1

| Threshold | Value | Source |
|---|---|---|
| `verdict_min_closed_trades` | 100 | K9 byte-equivalent; LOCKED non-negotiable per `no_k9_relaxation` |
| `verdict_max_drawdown_pct_magnitude_concern` | 0.30 | byte-equivalent from template |
| `verdict_max_drawdown_pct_magnitude_fail_safety` | 0.50 | per DA5=A |

### Never-live clause (LOAD-BEARING)

> `READY_FOR_LONGER_BACKTEST` is **exclusively a research label**. It NEVER signals readiness for live trading. The 6-gate live-block applies regardless of verdict for any candidate inheriting this template, including s12-d1.

### REC1 at C7 (LOAD-BEARING; binding)

Per REC1 `oos_k9_risk_disclosure` carried byte-equivalent from SEAL: the **EXPECTED OOS verdict for s12-d1 is INSUFFICIENT_SAMPLE / OOS_INDETERMINATE**. `READY_FOR_LONGER_BACKTEST` at IS does NOT imply OOS will reach READY; OOS is structurally expected to PARK at K9.

**Must NOT:** add a new verdict outside the closed enum without explicit operator-authorized schema bump; interpret `READY_FOR_LONGER_BACKTEST` as live-ready in any downstream automation; emit numeric win-rate when n < threshold; **treat REC1 OOS K9 disclosure as advisory only -- it is binding** per operator authorization.

## C8 -- Candidate lifecycle

### Allowed operational statuses

| Status | When |
|---|---|
| `ACTIVE_RESEARCH` | Default during s12-d1 Phase 2 ladder |
| `READY_FOR_LONGER_BACKTEST` | After a clean Step 5.x with sufficient sample (>=K9) |
| `PARKED_SAFE_BUT_NOT_MONEY_PROVEN` | Negative/neutral economics on clean run |
| `PARKED_FAILED_SAFETY` | Any safety counter > 0 that operator chooses not to repair |
| `PARKED_FALSIFIED_AT_OOS` | OOS run definitively negative per pre-committed thresholds |
| **`PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED`** | **(s12-d1 EXPECTED terminal verdict per REC1; analogous to S10-D2 P11 PARK at `23c7164`)** |
| `ARCHIVED` | Operator action; record preserved, no further activity |

### Transitions

- **To any `PARKED_*`:** operator authorization required; writes canonical parking report at `reports/external_research_hunter/<candidate>_PARKING_REPORT.md`; algorithm source preserved verbatim as reference
- **Revival from `PARKED_*`:** requires **FRESH SEALED RESEARCH CYCLE**. Fresh seals throughout, new plan-lock, new ladder. Not a continuation. Old run record stays intact.

### Permanent attributes (unchanged by parking)

- `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` secondary label
- All advisory labels
- 6-gate live-block
- FRC status (never granted)
- **REC1 oos_k9_risk_disclosure** (binding; carried into any future PARK memo for s12-d1)

### Weak-performance rejection rule (LOAD-BEARING)

> If a candidate shows decisively negative economics on a meaningful sample (Sharpe < 0, expectancy <= 0, profit-loss ratio < 0.5, `closed_trades >= verdict_min_closed_trades`), the operator MUST park it. Do NOT iterate parameters in search of better numbers -- that is optimization, which is forbidden by the safety-contract template.

### REC1 at C8 (LOAD-BEARING; binding)

s12-d1 expected terminal verdict is **`PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED`** per REC1. If OOS K9 fires (expected: 35-87 trades < K9=100), the operator MUST park s12-d1 under that status; the chain shall NOT relax K9 to extract a different verdict.

**Must NOT:** auto-revive a parked candidate; modify a parked candidate's record to claim better economics; use parking as a soft path back to live promotion; **treat REC1 OOS K9 disclosure as advisory only -- it is binding**.

## Pre-flight checklist for P3 BUILD

(See JSON sidecar `pre_flight_checklist_for_p3_build` for full content.)

### Required CONFIG fields to populate

- Identity: `candidate_record_id`, title, `candidate_grade`, `secondary_label`, `advisory_labels`
- Sealed chain: `tier_spec_seal`=07c3200b5e23ab88e864f92926b83ded033a3d66c0e37e8cf8555985ad8f3b48, `plan_lock_seal`=eb72798eb95c08407ead9c273a650853bd5e871942856f87b48f97f07a640340, `p2_phase2_plan_seal`=689dd3d06c0e2518ab5f6105544cb3d38194027647de10940da976e427c8efa9, `plan_doc_sha256`
- Instrument: `asset_class=futures`, `ticker_or_root_symbol=MNQ`, `continuous_contract_symbol=MNQ.c.0`, `resolution=daily`, `brokerage_model_name=NOT_APPLICABLE_CSV_SIMULATOR_AT_P6`
- Window: `start_date_is=(2019,5,13)`, `end_date_is=(2023,12,29)`, `start_date_oos=(2024,1,2)`, `end_date_oos=(2025,12,30)`, `plan_lock_window_ceiling=(2025,12,30)`
- Version: `algo_version_for_run_id=s12_d1_v0_1_0`, `phase_prefix=PHASE2-S12-D1-MNQ-DONCHIAN-15-8`
- Strategy params: `donchian_entry_period_n=15`, `donchian_exit_period_n=8`, `atr_period=20`, `atr_method=Wilder`, `stop_multiplier_in_atr=2.0`, `risk_pct_per_trade=0.01`, `max_units_per_market=1`, `starting_cash_mnq_equivalent=100000`, `tick_size_points=0.25`, `tick_value_usd=0.5`, `dollar_per_point=2.0`
- RTH window: `rth_safe_window_open=(9,30)`, `rth_safe_window_close=(16,0)`, `eod_cancel_time=(16,0)`, `tz=America/New_York`
- Event risk: `known_corporate_actions=[]` (STRUCTURALLY_ABSENT), `futures_roll_method=Databento_continuous`
- Verdict thresholds: `verdict_min_closed_trades=100`, `verdict_max_drawdown_pct_magnitude_concern=0.30`, `verdict_max_drawdown_pct_magnitude_fail_safety=0.50`

### Minimum tests before running P3 BUILD

| # | Test | Action |
|---|---|---|
| T1 | Sealed sha256s match disk | Verify `CONFIG['tier_spec_seal']==07c3200b5e23ab88e864f92926b83ded033a3d66c0e37e8cf8555985ad8f3b48` and `CONFIG['plan_lock_seal']==eb72798eb95c08407ead9c273a650853bd5e871942856f87b48f97f07a640340` byte-for-byte |
| T2 | Window ceiling | Confirm `CONFIG['end_date_oos']=(2025,12,30) <= plan_lock_window_ceiling=(2025,12,30)` |
| T3 | Boundary alignment | Confirm `rth_safe_window_close == eod_cancel_time == (16,0)` |
| T4 | Brokerage compatibility | NOT_APPLICABLE for s12-d1 (CSV simulator; no QC live path) |
| T5 | Distinct run_id | Compute deterministic run_id offline; confirm distinct from s11-d1 / s10-D2 / all prior s12-d1 algo versions |
| T6 | QC smoke init | NOT_APPLICABLE for s12-d1 (CSV simulator; no QC dependency in P3 BUILD per P1) |
| T7 | P4 synthetic smoke | T1-T15 + T7b + T7c per P1 section 10 |
| T8 | Validator pass at P4 | `execution_guard.full_guard_check` returns `overall_pass=True` |
| T9 | Verdict semantics | `READY_FOR_LONGER_BACKTEST` not interpreted as live-ready in any downstream automation; REC1 OOS K9 disclosure carried into output JSON `inherited_constraints_block` |

## What this P2 plan does NOT include

- NO strategy logic beyond what is already locked in SEAL + P1 plan-lock
- NO NKE-specific values (no split-2015-12-24, no DTE, no abs(delta), no S3 sizing, no BSM IV, no wheel state machine)
- NO live-promotion path
- NO revival mechanism for parked predecessors
- NO optimization permission (`no_strategy_optimization_authorized = True`)
- NO DR threshold relaxation (`no_dr_redefinition_post_seal = True`)
- NO K9 relaxation
- NO universe widening
- NO modification of s11-d1 v1 / P1 / P2 / clarification / rev2 sealed artifacts
- NO modification of s12-d1 SEAL at `66bbbd1` or P1 plan-lock at `d8bd359`
- NO modification of parallel-session SEAL at `9ce4d66`
- NO modification of `brain_memory/projects/trading_bot/lessons.md`

## Negative invariants

(See JSON sidecar `negative_invariants_for_p2_plan_usage` for full list; all 13 entries are `False`.)

- `claims_nke_strategy_money_proven`: False (NKE is parked as not money-proven)
- `nke_strategy_logic_reused_as_template`: False (only safety contracts extracted)
- `live_path_proposed_via_p2_plan`: False (6-gate live-block applies)
- `optimization_via_p2_plan_authorized`: False
- `parking_loophole_for_live_promotion`: False
- `verdict_enum_silently_extended`: False
- `schema_id_silently_bumped`: False
- `engine_date_check_silently_bypassed`: False
- `config_window_ceiling_extension_authorized`: False
- `fresh_sealed_revision_circumvented`: False
- **`rec1_oos_k9_risk_disclosure_demoted_to_advisory`: False**
- `s11_d1_sealed_artifacts_modified`: False
- `s12_d1_seal_or_p1_modified`: False

## Citation block for P3 BUILD to embed

```
# Inherits Phase 2 safety contracts (C1-C8) from:
#   docs/phase2_safety_contract_template.md
#   docs/phase2_safety_contract_template.json
# Template source candidate (parked, not money-proven):
#   s2-62fc753afc01f22c (NKE Options Wheel Tier-1 v6.1)
# Template reuse notice: NKE strategy logic NOT inherited;
#   only safety contracts.
# s12-d1 specific adaptations:
#   - C5 corporate-action/event-risk STRUCTURALLY_ABSENT (futures continuous-stitch)
#   - C3 extended_hours / unsupported_order_type NOT_APPLICABLE
#   - REC1 oos_k9_risk_disclosure carried binding
# Anchors:
#   tier_n_spec_seal = 07c3200b5e23ab88e864f92926b83ded033a3d66c0e37e8cf8555985ad8f3b48
#   p1_plan_lock_seal = eb72798eb95c08407ead9c273a650853bd5e871942856f87b48f97f07a640340
#   p2_phase2_plan_seal = 689dd3d06c0e2518ab5f6105544cb3d38194027647de10940da976e427c8efa9
```

## Explicit next-phase requirement

P2 phase-2 plan authoring + sealing + commit completes here. The NEXT phase is **P3 BUILD** (runner harness + drivers + tests). P3 BUILD REQUIRES SEPARATE OPERATOR AUTHORIZATION via the phrase: **"Authorize s12 D1 MNQ.c.0 P3 BUILD only"** (or P3-RUNNER / P3-IS-DRIVER / P3-OOS-DRIVER sub-phase split per P1 section 1).

P3 BUILD shall create 16 files in `external_research_hunter/s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_runner_harness/` namespace per P1 plan-lock section 1.

**NO PHASE BEYOND P3 IS PRE-APPROVED by this P2 plan.** Each subsequent phase requires its own separate operator authorization.

- Next phase pre-approved by this P2 plan: **False**
- P3 BUILD requires separate authorization: **True**
- P4 smoke requires separate authorization: **True**
- P6 IS requires separate authorization: **True**
- P6.5 cost-stress requires separate authorization: **True**
- P7 decision memo requires separate authorization: **True**
- P10 OOS gate requires separate authorization: **True**
- P11 lifecycle decision requires separate authorization: **True**

## Parent references (READ-ONLY)

(See JSON sidecar `parent_references` for full citation block.)

- `tier_n_spec_commit`: `66bbbd1` (s12-d1 SEAL; operator-preserved source of truth)
- `tier_n_spec_seal_sha256`: `07c3200b5e23ab88e864f92926b83ded033a3d66c0e37e8cf8555985ad8f3b48`
- `p1_plan_lock_commit`: `d8bd359`
- `p1_plan_lock_seal_sha256`: `eb72798eb95c08407ead9c273a650853bd5e871942856f87b48f97f07a640340`
- `s12_d1_plan_commit`: `b4eac65`
- `s12_d1_draft_commit`: `7e9c867`
- `s11_d1_v1_spec_commit`: `9c63088` / sha `077e29e6...`
- `s11_d1_rev2_commit`: `c110fd4` / sha `46659b4a...`
- `s11_d1_p1_plan_lock_commit`: `7d86486`
- `s11_d1_p2_phase_2_plan_commit`: `f64f984`
- `s10_d2_park_commit`: `23c7164`
- `s10_d1_mnq_mgc_park_commit`: `1a9acec`
- `mnq_c0_csv_path`: `data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_c_0_ohlcv_1d_20190513_20251230.csv`
- `mnq_c0_csv_sha256`: `8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e`

## Status / labels

- `trading_status`: PAUSED
- `live_status`: BLOCKED_AT_6_GATES
- `frc_status`: NEVER_GRANTED
- `research_label`: DIAGNOSTIC_ONLY_NOT_LIVE_GRADE
- `lifecycle_state`: P2_PHASE_2_PLAN_SEALED

**Labels** (see JSON sidecar `labels` for full list; 20 entries):

- `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE`
- `P2_PHASE_2_PLAN_SEALED`
- `S12_D1_MNQ_DONCHIAN_15_8_FRESH_CANDIDATE`
- `K9_THRESHOLD_INVIOLATE`
- `OOS_K9_STRUCTURALLY_UNREACHABLE_REC1_BINDING`
- `DR10_RISK_ELEVATED_MITIGATED_VIA_DA4_B_START_CASH_100K`
- `DONCHIAN_15_8_LOCKED_AT_PLAN_NO_RETREAT_TO_55_20`
- `MECHANIC_FAMILY_F1_LOCKED_AT_PLAN_NO_REOPENING`
- `TIER_N_SPEC_LOCKED_BYTE_EQUIVALENT_AT_66BBBD1`
- `P1_PLAN_LOCK_LOCKED_BYTE_EQUIVALENT_AT_D8BD359`
- `PARALLEL_SEAL_AT_9CE4D66_ACKNOWLEDGED_NOT_ANCHORED`
- `C1_THROUGH_C8_INHERITED_BYTE_EQUIVALENT_FROM_PHASE_2_TEMPLATE`
- `C5_CORPORATE_ACTION_STRUCTURALLY_ABSENT_FUTURES`
- `REC1_OOS_K9_RISK_DISCLOSURE_BINDING`
- `EXPECTED_TERMINAL_VERDICT_PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED`

## Hard boundaries held (this P2 phase-2 plan turn)

(See JSON sidecar `hard_boundaries_held_this_p2_phase2_plan_turn` for full attestation; 41 entries; all True.) Key additions specific to s12-d1 P2:

- `no_modification_of_s12_d1_seal_at_66bbbd1`: True (operator-preserved source of truth)
- `no_modification_of_s12_d1_p1_plan_lock_at_d8bd359`: True
- `no_modification_of_parallel_session_seal_at_9ce4d66`: True (parallel-session SEAL acknowledged not anchored)
- `no_modification_of_phase_2_safety_contract_template`: True
- `no_rec1_demotion_to_advisory`: True
- `preserves_seal_at_66bbbd1_and_p1_at_d8bd359_as_source_of_truth`: True
- `rec1_oos_k9_risk_disclosure_carried_byte_equivalent_binding`: True

## Seal metadata

- **Report seal sha256:** `689dd3d06c0e2518ab5f6105544cb3d38194027647de10940da976e427c8efa9`
- **Seal method:** LESSON_HUNTER_004 canonical roundtrip (json.dumps `sort_keys=True separators=',:' ensure_ascii=False default=str` EXCLUDING `report_seal_sha256` + `seal_method`)
- **Reseal verified on disk:** YES (in-script roundtrip assertion passed with explicit UTF-8 encoding)
