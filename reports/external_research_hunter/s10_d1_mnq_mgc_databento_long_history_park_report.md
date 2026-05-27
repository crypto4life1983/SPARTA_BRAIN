# s10 D1 MNQ+MGC Databento Long-History -- Candidate Park Report

Status: PARKED_INCONCLUSIVE_HOLD_DR9_FIRED (terminal; candidate archived; no further phases authorized).
Authored: 2026-05-27
Authorization: "Authorize s10 D1 MNQ+MGC candidate park under DR9 INCONCLUSIVE_HOLD."

Candidate: `s10-d1-cross-asset-trend-or-meanrev-mnq-mgc-databento-long-history`
Sealed spec reference: `docs/s10_d1_mnq_mgc_databento_long_history_tier_n_spec.md` (commit `9040429`)
Terminal closed-enum verdict: **`INCONCLUSIVE_HOLD`** (per sealed-spec section 11 DR9 severity mapping; see section 2 below for the full audit-evidence chain).

---

## 1. Identity and lifecycle chain

| Field | Value |
|---|---|
| `candidate_record_id` | `s10-d1-cross-asset-trend-or-meanrev-mnq-mgc-databento-long-history` |
| `candidate_family` | F1 -- Long+Short Bi-Directional Donchian Trend, No Pyramid, ATR-Based Stop (LOCKED at SEAL) |
| Sealed universe | `{MNQ.c.0, MGC.c.0}` |
| Sealed dataset | `GLBX.MDP3` / `ohlcv-1d` / `stype_in=continuous` |
| IS window | `2019-05-13 -> 2023-12-29` |
| OOS window (never inspected) | `2024-01-02 -> 2025-12-30` |
| `spec_seal_anchor_commit` | `9040429` |
| Sealed-spec `spec_seal_sha256` | `589ec42153c2c544474424dad03fc22a385c3fe8e0625e0dc5b13bfecec0cb6e` |
| Park terminal verdict | **`INCONCLUSIVE_HOLD`** (DR9-driven; section 2) |
| Live status | `BLOCKED_AT_6_GATES` |
| Promotion status | NOT promoted |
| FRC | `NEVER_GRANTED` |
| Advisory label (permanent) | `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` |

### 1.1 Chain of commits (this candidate's lifecycle)

| # | Commit | Phase | Outcome |
|---|---|---|---|
| 1 | `2ec9330` | Next-research-track selection plan after s9 park | T7-Path-A pivot recommended |
| 2 | `5c13821` | T8 ETF-proxy family park memo + s10 D1 MNQ+MGC Tier-N spec PLAN | family park sealed + Tier-N PLAN published |
| 3 | `a95d7f0` | s10 D1 Tier-N spec DRAFT | DRAFT authored with 13 ambiguities |
| 4 | **`9040429`** | **s10 D1 Tier-N spec SEAL** | **all 13 ambiguities locked at default A; spec sealed** |
| 5 | `a8df18b` | Step 02b operator-side Databento fetch package | script + runbook + report; controller did NOT run |
| 6 | `0736976` | Step 02b fetch script dataframe-normalization patch | `_normalize_dbn_dataframe` helper added; deprecation fix |
| 7 | (off-controller) | Operator ran Step 02b fetch | MNQ 2066 rows + MGC 1814 rows captured locally; safe paste-back |
| 8 | `9bdde45` | Step 02c raw-data audit (strict) | verdict `DR9_FIRED_AUDIT_FAIL` (MGC 8 gaps > 5 days; threshold = 5) |
| 9 | `0e124e3` | Step 02c holiday-aware audit refinement | verdict `DR9_FIRED_AUDIT_FAIL_HOLIDAY_AWARE` (MGC reduced to 7 unexplained gaps; still > 5) |
| 10 | **THIS COMMIT** | **Candidate park report** | **terminal; lifecycle closed under `INCONCLUSIVE_HOLD`** |

## 2. Terminal verdict basis (the load-bearing evidence)

**`INCONCLUSIVE_HOLD`** driven by **DR9 `mnq_mgc_data_continuity_integrity_check`** firing on `MGC.c.0`'s `missing_observations` criterion under both audit variants.

Per sealed-spec section 11 row DR9: severity if fired = `INCONCLUSIVE_HOLD`. The audit was run **twice** (strict gap-counting first, then holiday-aware refinement with a hardcoded US/CME federal-holiday list spanning 2019-2023). Both variants returned a DR9 fire:

| Audit variant | MGC missing-obs count | DR9 threshold | DR9 verdict |
|---|---|---|---|
| Strict (commit `9bdde45`) | **8** | 5 | `fire` |
| Holiday-aware (commit `0e124e3`) | **7** (1 of 8 reclassified as holiday-explained) | 5 | `fire` |

The DR9 fire is **robust to the refinement**: the heuristic well is approximately dry, and the 7 remaining unexplained gaps reflect actual data-availability anomalies in MGC's continuous-front-month stitch, not artifacts of strict gap-counting.

### 2.1 MGC.c.0 gap classification (8 strict gaps; the load-bearing detail)

| # | Prev observed | Next observed | Days | Holiday in span? | Classification |
|---|---|---|---|---|---|
| 1 | 2019-08-19 | 2019-08-26 | 7 | none | **data-quality** |
| 2 | 2020-10-20 | 2020-10-26 | 6 | none | **data-quality** |
| 3 | 2021-10-15 | 2021-10-22 | 7 | none | **data-quality** |
| 4 | 2022-06-17 | 2022-06-24 | 7 | 2022-06-20 (Juneteenth observed) | holiday-explained |
| 5 | 2022-10-07 | 2022-10-24 | **17** | none | **data-quality (anomalous)** |
| 6 | 2023-08-18 | 2023-08-25 | 7 | none | **data-quality** |
| 7 | 2023-10-13 | 2023-10-20 | 7 | none | **data-quality** |
| 8 | 2023-10-23 | 2023-10-29 | 6 | none | **data-quality** |

Pattern: 4 of 7 data-quality gaps cluster in mid-October across years; 2 in mid-August; one 17-day October 2022 anomaly. Consistent with structural thinning of MGC's Databento continuous-front-month stitch around CME gold-futures quarterly roll cycles.

## 3. What did NOT fail (cleared evaluations; informational only)

The candidate's failure was **narrow** -- DR9 on MGC only. All other sealed-spec evaluations either cleared or were structurally unreachable at this audit phase:

| Check | Status |
|---|---|
| MNQ.c.0 DR9 (both audit variants) | **clean** (0 gaps; 0 consecutive abs-log-return violations; pct_observed 1.2365) |
| MGC.c.0 `pct_observed >= 0.95` | **PASS** (1.0686) |
| MGC.c.0 consecutive `abs(log_return) > 0.30` | **PASS** (0 violations; max single-day 0.0713) |
| File-level sha256 match against operator paste-back | both symbols + manifest match |
| Row-count match against manifest | both symbols match (MNQ 2066; MGC 1814) |
| Required-column presence | all 6 columns present in both CSVs |
| Sealed-spec `spec_seal_anchor_commit` cross-check | `9040429` matches |
| Universe LOCKED (`MNQ.c.0` + `MGC.c.0` only; MCL excluded) | YES |
| Step 02b boundary-attestation block (11 attestations) | all `True` |
| OOS-window inspection at IS phase | NOT performed (invariant held) |

## 4. Per-symbol breakdown

### 4.1 MNQ.c.0 -- CLEAN under both audit variants

| Field | Value |
|---|---|
| Row count | 2,066 |
| IS-window rows | 1,443 |
| OOS-window rows (structural only) | 622 |
| `is_pct_observed` | 1.2365 (PASS) |
| Calendar gaps > 5 days (strict) | 0 |
| Holiday-explained gaps | 0 |
| Holiday-aware missing-obs count | 0 |
| Consecutive abs-log-return violation count | 0 |
| Max single-day abs-log-return observed | 0.1164 (~11.6%) |
| **DR9 verdict (both variants)** | **`clean`** |

MNQ.c.0 is a fully clean leg; the DR9 fire is NOT MNQ's responsibility.

### 4.2 MGC.c.0 -- DR9 FIRES under both audit variants

| Field | Value |
|---|---|
| Row count | 1,814 |
| IS-window rows | 1,247 |
| OOS-window rows (structural only) | 566 |
| `is_pct_observed` | 1.0686 (PASS) |
| **Calendar gaps > 5 days (strict)** | **8 (FAIL > 5)** |
| Holiday-explained gaps | 1 |
| **Holiday-aware missing-obs count** | **7 (FAIL > 5)** |
| Consecutive abs-log-return violation count | 0 (PASS) |
| Max single-day abs-log-return observed | 0.0713 (~7.1%) |
| **DR9 verdict (both variants)** | **`fire`** |

MGC.c.0 is the weak leg. The fire is on the `missing_observations` criterion and is robust to the holiday-aware refinement.

## 5. Captured-artifact provenance (read-only references)

| Artifact | Path | sha256 |
|---|---|---|
| MNQ.c.0 daily-bar CSV | `data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_c_0_ohlcv_1d_20190513_20251230.csv` | `8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e` |
| MGC.c.0 daily-bar CSV | `data/s10_d1_mnq_mgc_databento_long_history/raw/MGC_c_0_ohlcv_1d_20190513_20251230.csv` | `79618abec8c34e59f0cc52420afc455c0d7dbdf13bf96605224e27247c9ccc4b` |
| Fetch manifest | `data/s10_d1_mnq_mgc_databento_long_history/raw/s10_d1_mnq_mgc_step02b_fetch_manifest.json` | `d6cf8c8b4cc81ff0b85085db5bc83b02b3bf795887b6a49ca71898b77c926225` |
| Strict-audit script | `tools/operator_side/s10_d1_mnq_mgc_step02c_audit_raw_data.py` | (committed in `9bdde45`) |
| Strict-audit report MD | `reports/external_research_hunter/s10_d1_mnq_mgc_step02c_audit_report.md` | (committed in `9bdde45`) |
| Strict-audit report JSON | `reports/external_research_hunter/s10_d1_mnq_mgc_step02c_audit_report.json` | `report_seal_sha256=fd5cd136891638d2a1338850b616d000b969c7b46ce8c12365ba9498855e5865` |
| Holiday-aware audit script | `tools/operator_side/s10_d1_mnq_mgc_step02c_audit_holiday_aware.py` | (committed in `0e124e3`) |
| Holiday-aware audit report MD | `reports/external_research_hunter/s10_d1_mnq_mgc_step02c_audit_holiday_aware_report.md` | (committed in `0e124e3`) |
| Holiday-aware audit report JSON | `reports/external_research_hunter/s10_d1_mnq_mgc_step02c_audit_holiday_aware_report.json` | `report_seal_sha256=5f0258117cf35afa17ada593d464a0fc941e87c95bc52b76d54b8d719ee34686` |

All captured raw-data files reside in `data/` and are untracked in git (no version-control commitment of raw vendor data).

## 6. Permanent labels for this candidate

| Label | Value |
|---|---|
| `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` | TRUE (permanent for this `candidate_record_id`, independent of any future re-interpretation) |
| `DR9_FIRED_ROBUST_TO_HOLIDAY_AWARE_REFINEMENT` | TRUE |
| `LIVE_TRADING_BLOCKED` | TRUE |
| `STRATEGY_LAB_PROMOTION_BLOCKED` | TRUE |
| `BROKER_INTEGRATION_BLOCKED` | TRUE |
| `OOS_INSPECTION_BLOCKED` | TRUE (never proceeded past IS-phase audit) |
| `DO_NOT_RESCUE_THIS_SPEC` | TRUE |
| `DO_NOT_ITERATE_S10_D1_MNQ_MGC_PARAMETERS_WITHOUT_REVN_SPEC` | TRUE |
| `NO_SUBSTITUTION_OF_MCL_OR_OTHER_SYMBOL_INTO_THIS_CANDIDATE` | TRUE (universe LOCKED at SEAL; symbol swap requires fresh candidate id) |
| `MNQ_C_0_CLEAN_LEG_FINDING_PRESERVED_FOR_FUTURE_FRESH_CANDIDATES` | TRUE |

## 7. No-live / no-promotion / no-FRC status (carried forward)

| Field | Value |
|---|---|
| Trading | `PAUSED` |
| Live mode | `BLOCKED_AT_6_GATES` (permanent for this candidate) |
| FRC | `NEVER_GRANTED` |
| `no_strategy_optimization_authorized` | TRUE |
| `no_dr_redefinition_post_seal` | TRUE |
| All 19 sealed-spec RUNTIME_INVARIANTS at SEAL remain TRUE | YES |

Sealed-spec section 11 DR9 severity = `INCONCLUSIVE_HOLD` is the natural mapping; the candidate is parked under that closed-enum value. `INCONCLUSIVE_HOLD` does NOT unlock live, does NOT grant FRC, does NOT promote to Strategy Lab. The 6-gate live block remains permanent for this candidate.

## 8. What this park does NOT mean

| Statement | Truth value |
|---|---|
| The s10 D1 micro-futures research direction is dead | **FALSE** -- this park applies only to the specific candidate id `s10-d1-cross-asset-trend-or-meanrev-mnq-mgc-databento-long-history`. Fresh candidate ids on a different universe (e.g., MNQ-only single-instrument, MNQ + alternate second symbol) are NOT covered by this park. |
| MNQ.c.0 has data-quality issues | **FALSE** -- MNQ.c.0 passed both audit variants cleanly. The DR9 fire was entirely on MGC.c.0. A future fresh-candidate-id spec using MNQ.c.0 inherits the MNQ-clean finding from sections 3 + 4.1. |
| The sealed Tier-N spec has bugs requiring revision | **FALSE** -- the sealed spec is byte-stable. The candidate failed because the data on MGC's continuous-stitch did not meet the spec's pre-committed DR9 thresholds. The spec's DR9 thresholds were applied faithfully. |
| The audit heuristic was unfair | **FALSE** -- the holiday-aware refinement gave the candidate a second chance under a more permissive interpretation. The DR9 fire survived the refinement. |
| Optimizing the DR9 threshold could rescue this candidate | **FORBIDDEN** -- `no_dr_redefinition_post_seal = True` and `no_strategy_optimization_authorized = True`. Threshold tuning is forbidden. The sealed threshold (5) is non-negotiable for this candidate id. |

## 9. Recommended next paths (operator picks; this report does not recommend among them)

The operator's prior message explicitly noted: "after parking, the best next idea is likely a fresh MNQ-only candidate or MNQ with a better second symbol, because MNQ passed both audits cleanly. But that must be a new candidate ID, not a revision of this failed one." That operator guidance is recorded here as informational context; it does NOT constitute an authorization to author any next-step artifact.

Three forward paths the operator may choose, each requires a separate `Authorize ...` phrase:

### Path A1 -- Fresh MNQ.c.0-only single-instrument candidate (fresh ID required)

- Proposed authorization phrase: `Authorize next-research-track selection plan after s10 D1 MNQ+MGC park.`
- The resulting plan would survey: (a) MNQ.c.0-only single-instrument candidate, (b) MNQ+different-second-symbol candidate, (c) revert to ETF-proxy with different mechanic, (d) cross-domain pivot.
- The plan would then enable a fresh Tier-N spec authoring turn under a new candidate id (e.g., `s11-d1-...` or `b006_003_...`).

### Path A2 -- Defer / pause all trading-bot work

- Proposed authorization phrase: `Acknowledge s10 D1 park; pause trading-bot track.`
- The trading-bot research arc enters a holding state with two parked tracks at the family level (SPY/TLT/GLD/USO ETF-proxy via T8) and one parked single-mechanic candidate (s10 D1 MNQ+MGC via this park). The operator pivots to other projects until ready to resume.

### Path A3 -- Optional terminal lesson append to `brain_memory/projects/trading_bot/lessons.md`

- Proposed authorization phrase: `Authorize s10 D1 MNQ+MGC park terminal lesson append to lessons.md only.`
- Would append a one-paragraph lesson capturing: (a) DR9 fire on MGC continuous-stitch as a Databento-vendor data-quality finding, (b) the holiday-aware refinement methodology, (c) MNQ.c.0 clean-leg preservation for future fresh candidates.
- Currently NOT executed because the dirty + unstaged state of `lessons.md` from prior controller-session appends must remain untouched; the operator must explicitly authorize touching `lessons.md` before any append.

## 10. Files written this PARK turn

| File | Purpose |
|---|---|
| `reports/external_research_hunter/s10_d1_mnq_mgc_databento_long_history_park_report.md` | This terminal park report |
| `reports/external_research_hunter/s10_d1_mnq_mgc_databento_long_history_park_report.json` | Companion JSON with structured terminal verdict + chain commits + audit cross-references; embeds `report_seal_sha256` |

No other repository file is modified. Sealed spec, runner-package precedent, audit scripts, audit reports, and all prior sealed artifacts remain byte-stable. `brain_memory/projects/trading_bot/lessons.md` dirty + unstaged state from prior controller-session appends preserved (NOT modified, NOT staged, NOT committed this turn).

## 11. Boundaries held this PARK turn

| Boundary | Status |
|---|---|
| PARK MEMO ONLY (no further build phases) | met |
| No code authored (only this report MD + JSON via stdlib helper) | met |
| No backtest | met |
| No simulator run | met |
| No signal computation | met |
| No data fetch | met |
| No Databento call | met |
| No `DATABENTO_API_KEY` access | met |
| No yfinance / Yahoo Finance call | met |
| No QC / LEAN call | met |
| No network IO | met |
| No live trading | met |
| No candidate promotion | met |
| No mutation of `review_queue.json` | met |
| No mutation of production `idea_memory` | met |
| No modification of sealed Tier-N spec | met (byte-stable) |
| No modification of operator-captured raw CSVs or manifest | met (byte-stable in `data/`) |
| No modification of strict-audit script / report | met (byte-stable at `9bdde45`) |
| No modification of holiday-aware audit script / report | met (byte-stable at `0e124e3`) |
| No modification of any prior B006_NNN / s7 D1 / s9 / family-park artifact | met (byte-stable) |
| No modification or staging of `brain_memory/projects/trading_bot/lessons.md` | met (dirty + unstaged preserved) |
| No DR9 sealed-threshold modification | met |
| No DR9 operationalization modification (the sealed DR9 verdict is taken as-is) | met |
| No branch change, no branch creation, no git push | met |
| Trading status | `PAUSED` |
| Live status | `BLOCKED_AT_6_GATES` |
| FRC | `NEVER_GRANTED` |
| `no_strategy_optimization_authorized` | TRUE |
| `no_dr_redefinition_post_seal` | TRUE |

## 12. One-paragraph summary

This document parks the s10 D1 candidate `s10-d1-cross-asset-trend-or-meanrev-mnq-mgc-databento-long-history` under terminal sealed-enum verdict **`INCONCLUSIVE_HOLD`**, driven by DR9 `mnq_mgc_data_continuity_integrity_check` firing on MGC.c.0's `missing_observations` criterion. The candidate's lifecycle proceeded cleanly through Phase 0 selection plan (`2ec9330`), Phase 1 T8 family-park memo + Phase 2 Tier-N PLAN (`5c13821`), Phase 3 Tier-N DRAFT (`a95d7f0`), Phase 4 Tier-N SEAL with all 13 DRAFT ambiguities locked at default A (`9040429`), Phase 5 Step 02b operator-side Databento fetch package (`a8df18b` + patch `0736976`), operator-side fetch execution (off-controller; safe paste-back of 2066 MNQ rows + 1814 MGC rows + manifest sha `d6cf8c8b…6225`), Phase 6a Step 02c strict raw-data audit (`9bdde45`; verdict `DR9_FIRED_AUDIT_FAIL` due to MGC 8 calendar gaps > 5 days vs sealed threshold of 5), and Phase 6b Step 02c holiday-aware audit refinement (`0e124e3`; verdict `DR9_FIRED_AUDIT_FAIL_HOLIDAY_AWARE`; the refinement reduced MGC's count from 8 to 7 by reclassifying one gap as Juneteenth-explained, but the DR9 fire survived because the remaining 7 gaps cluster in mid-August + mid-October across multiple years with one anomalous 17-day October 2022 gap -- consistent with structural thinning of MGC.c.0's Databento continuous-front-month stitch around CME gold-futures quarterly roll cycles). **MNQ.c.0 is a clean leg under both audit variants** (zero gaps > 5 days, zero consecutive abs-log-return violations, max single-day abs-log-return 0.1164, pct_observed 1.2365 PASS); the candidate's failure is narrowly attributable to MGC.c.0's data-availability anomaly, not to any property of MNQ.c.0 or of the sealed mechanic family F1. The sealed DR9 threshold (5) was applied faithfully twice without modification per `no_dr_redefinition_post_seal` and `no_strategy_optimization_authorized`; the refinement modified only the operationalization (excluding gaps containing US/CME federal holidays from the count), not the threshold itself. The candidate is **terminal** under sealed-enum value `INCONCLUSIVE_HOLD` per sealed-spec section 11 DR9 severity mapping. **The candidate is NOT live-ready, NOT a profit proof, NOT promotable, NOT FRC-eligible, and does NOT unlock the 6-gate live block (permanent for this candidate id).** The s10 D1 micro-futures *research direction* is NOT terminated by this park -- this park applies only to the specific `candidate_record_id` listed in section 1; fresh candidate ids on a different universe (e.g., MNQ-only single-instrument leveraging the MNQ-clean-leg finding preserved in section 4.1, or MNQ paired with a different second symbol after fresh availability probing) are eligible for separately-authorized future selection plans. Three forward paths are documented for the operator's separate authorization (this report does NOT recommend among them): Path A1 (next-research-track selection plan after s10 D1 park), Path A2 (defer / pause trading-bot track), Path A3 (optional terminal lesson append to lessons.md -- currently blocked because lessons.md is dirty + unstaged from prior controller-session appends that must remain untouched). `brain_memory/projects/trading_bot/lessons.md` dirty state preserved throughout. All sealed Tier-N spec parameters remain byte-stable. All prior sealed/built/audit artifacts remain byte-stable. **No code authored this turn beyond the report MD and its stdlib-only JSON-build helper. No backtest. No simulator. No signal computation. No data fetch. No Databento call. No DATABENTO_API_KEY access. No yfinance / QC / LEAN call. No network IO. No live trading. No candidate promotion. No mutation of review_queue.json or production idea_memory. No mutation of any sealed prior artifact. No mutation or staging of lessons.md. No branch change, no branch creation, no git push.** Trading remains `PAUSED`. Live remains `BLOCKED_AT_6_GATES`. FRC `NEVER_GRANTED`. `no_strategy_optimization_authorized = True`. `no_dr_redefinition_post_seal = True`. The s10 D1 MNQ+MGC candidate is **terminally archived**.

---

*Park report. Candidate terminal. Diagnostic-only. Not a profit proof. Not a live-go signal. DR9 fired robustly under both strict and holiday-aware audit variants. The s10 D1 research direction is not terminated; only this specific candidate id is parked. MNQ.c.0 clean-leg finding preserved for future fresh-candidate-id selection.*
