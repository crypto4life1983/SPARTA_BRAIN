# s10 D1 MNQ+MGC Step 02c Holiday-Aware Audit Refinement Report

Status: REFINED_AUDIT_RUN_LOCALLY_BY_CONTROLLER (no Databento; no network; no OOS return analysis).
Authored: 2026-05-27 (audit run UTC: 2026-05-27T01:26:11Z)
Authorization: "Authorize s10 D1 MNQ+MGC Step 02c holiday-aware audit refinement only."

Candidate: `s10-d1-cross-asset-trend-or-meanrev-mnq-mgc-databento-long-history`
Sealed spec reference: `docs/s10_d1_mnq_mgc_databento_long_history_tier_n_spec.md` (commit `9040429`)
Predecessor (strict) audit script: `tools/operator_side/s10_d1_mnq_mgc_step02c_audit_raw_data.py` (commit `9bdde45`)
Predecessor (strict) audit report: `reports/external_research_hunter/s10_d1_mnq_mgc_step02c_audit_report.md`
This refinement audit script: `tools/operator_side/s10_d1_mnq_mgc_step02c_audit_holiday_aware.py` (`py_compile` PASS; ASCII-only)

---

## 1. Refined audit verdict (terminal)

# **`DR9_FIRED_AUDIT_FAIL_HOLIDAY_AWARE`**

The holiday-aware refinement reduced MGC.c.0's missing-observations count from **8 (strict)** to **7 (holiday-aware)**, but `7 > DR9_MAX_MISSING_OBSERVATIONS (5)` — DR9 still fires. The refinement was faithful and did NOT modify the sealed DR9 threshold; only the operationalization (excluding holiday-explained gaps) changed.

**Both audit variants agree: the candidate fails DR9 on MGC.c.0.**

## 2. Sealed DR9 thresholds (unchanged; non-negotiable)

| Threshold | Value | Modification status |
|---|---|---|
| `DR9_MIN_PCT_EXPECTED_TRADING_DAYS` | **`0.95`** | LOCKED |
| `DR9_MAX_CONSECUTIVE_ABS_LOG_RETURN` | **`0.30`** | LOCKED |
| `DR9_MAX_MISSING_OBSERVATIONS` | **`5`** | LOCKED |
| `DR9_MAX_CONSECUTIVE_VIOLATION_THRESHOLD` | **`5`** | LOCKED |

`no_dr_redefinition_post_seal = True` and `no_strategy_optimization_authorized = True` both held throughout this refinement.

## 3. US / CME federal-holiday list embedded in the refinement script

The script hardcodes 46 US/CME federal-holiday dates spanning the IS-window years 2019-2023:

| Year | Holidays embedded |
|---|---|
| 2019 | New Year, MLK, Presidents, Good Friday, Memorial, July 4, Labor, Thanksgiving, Christmas (9 entries) |
| 2020 | New Year, MLK, Presidents, Good Friday, Memorial, July 3 observed, Labor, Thanksgiving, Christmas (9) |
| 2021 | New Year, MLK, Presidents, Good Friday, Memorial, July 5 observed, Labor, Thanksgiving, Dec 24 observed (9) |
| 2022 | MLK, Presidents, Good Friday, Memorial, Juneteenth observed, July 4, Labor, Thanksgiving, Dec 26 observed (9) |
| 2023 | Jan 2 observed, MLK, Presidents, Good Friday, Memorial, Juneteenth, July 4, Labor, Thanksgiving, Christmas (10) |

A gap is classified `holiday_explained = True` iff at least one of these dates falls within the half-open span `(prev_observed_date, next_observed_date)`.

**Acknowledged brittleness:** the list does NOT enumerate emergency closures (e.g., 9/11-style, weather, exchange-specific outages). It does NOT include Easter Monday (US doesn't observe). Good Friday observance on CME varies by product. This list is a refinement, not a guarantee.

## 4. Per-symbol findings (holiday-aware)

### 4.1 MNQ.c.0 — CLEAN under both variants

| Field | Value |
|---|---|
| `is_window_row_count` | 1,443 |
| `is_pct_observed` | 1.2365 (PASS) |
| Strict missing-obs count | 0 |
| Holiday-explained gap count | 0 |
| Holiday-aware missing-obs count | 0 |
| Consecutive abs-log-return violation count | 0 |
| Max single-day abs-log-return observed | 0.1164 |
| **DR9 fire decision (holiday-aware)** | **`clean`** |
| DR9 fire decision (strict for comparison) | `clean` |
| OOS row count (structural only; NO return analysis) | 622 |

### 4.2 MGC.c.0 — DR9 FIRES under both variants (refinement reduces but does not clear)

| Field | Value |
|---|---|
| `is_window_row_count` | 1,247 |
| `is_pct_observed` | 1.0686 (PASS) |
| **Strict missing-obs count** | **8** (FAIL > 5) |
| **Holiday-explained gap count** | **1** (Juneteenth 2022 weekend) |
| **Holiday-aware missing-obs count** | **7** (FAIL > 5) |
| Consecutive abs-log-return violation count | 0 (PASS) |
| Max single-day abs-log-return observed | 0.0713 |
| **DR9 fire decision (holiday-aware)** | **`fire`** |
| DR9 fire decision (strict for comparison) | `fire` |
| OOS row count (structural only; NO return analysis) | 566 |

## 5. MGC.c.0 gap-by-gap classification (8 gaps; the load-bearing finding)

Each MGC IS-window calendar gap > 5 days, with holiday-aware classification:

| # | Prev observed | Next observed | Days | Holiday-explained? | Holidays in span |
|---|---|---|---|---|---|
| 1 | 2019-08-19 | 2019-08-26 | 7 | **NO** | none |
| 2 | 2020-10-20 | 2020-10-26 | 6 | **NO** | none |
| 3 | 2021-10-15 | 2021-10-22 | 7 | **NO** | none |
| 4 | 2022-06-17 | 2022-06-24 | 7 | **YES** | 2022-06-20 (Juneteenth observed) |
| 5 | 2022-10-07 | 2022-10-24 | **17** | **NO** | none |
| 6 | 2023-08-18 | 2023-08-25 | 7 | **NO** | none |
| 7 | 2023-10-13 | 2023-10-20 | 7 | **NO** | none |
| 8 | 2023-10-23 | 2023-10-29 | 6 | **NO** | none |

**Pattern observed (informational, not a sealed metric):**

- **4 of 7 data-quality gaps fall in mid-October** (2020, 2021, 2023 × 2). No US federal holidays in mid-October.
- **2 of 7 data-quality gaps fall in mid-August** (2019, 2023). No US federal holidays in mid-August.
- **1 gap in October 2022 spans 17 calendar days** — by far the largest single anomaly.
- The Juneteenth-observed gap (2022) is the ONLY clearly holiday-explained one.

**Plausible structural reading (informational; NOT a sealed verdict):**

CME gold futures (GC) have monthly expirations; MGC's Databento continuous-front-month stitch may exhibit thin / gapped coverage around the front-contract roll into a next-month contract that isn't yet sufficiently liquid. Mid-August and mid-October aligning with quarterly roll cycles is consistent with this hypothesis. The 17-day October 2022 gap is the most extreme and warrants operator attention if a future candidate uses MGC.

This is a **structural data-availability finding about MGC.c.0's continuous-stitch on Databento** — not an artifact of the audit heuristic and not a holiday-explainable phenomenon. The DR9 fire is real.

## 6. Comparison vs strict audit

| Metric | Strict audit (commit `9bdde45`) | Holiday-aware audit (this turn) |
|---|---|---|
| MNQ.c.0 verdict | `clean` | `clean` |
| MGC.c.0 missing-observations count | 8 | 7 (after excluding 1 holiday-explained gap) |
| MGC.c.0 verdict | `fire` | `fire` |
| Final verdict | `DR9_FIRED_AUDIT_FAIL` | `DR9_FIRED_AUDIT_FAIL_HOLIDAY_AWARE` |
| Verdict changed? | — | **NO** |

The refinement reduced the missing-observations count by 1 (one gap reclassified as holiday-explained) but did not clear the DR9 fire (7 > 5 threshold).

## 7. OOS-window structural verification (NO return analysis)

- MNQ.c.0 OOS row count: 622 (window `2024-01-02 → 2025-12-30`)
- MGC.c.0 OOS row count: 566
- Returns / Sharpe / PnL / drawdown / win-rate over OOS: **NOT COMPUTED**
- `oos_inspection_blocked_at_in_sample` invariant held throughout this refinement.

The OOS row counts are structurally present; the OOS window was NOT subjected to gap analysis at this audit phase per the IS-only enforcement contract.

## 8. Boundary-attestation block (this refinement run)

| Attestation | Status |
|---|---|
| Local file reads only | TRUE |
| No Databento call | TRUE |
| No network IO | TRUE |
| No `DATABENTO_API_KEY` access | TRUE |
| No OOS return summary | TRUE |
| No strategy performance evaluation | TRUE |
| No Sharpe / PnL / drawdown / win-rate computation | TRUE |
| `abs(log_return)` computed ONLY for DR9 outlier check | TRUE |
| No row content printed (only counts, shas, timestamps, DR9 metrics, gap dates + holiday classification) | TRUE |
| No mutation of `review_queue.json` | TRUE |
| No mutation of production `idea_memory` | TRUE |
| No mutation of any sealed prior artifact | TRUE |
| No mutation of `brain_memory/projects/trading_bot/lessons.md` (dirty + unstaged preserved) | TRUE |
| Sealed-spec `commit_anchor` cross-checked against manifest | TRUE (both `9040429`) |
| DR9 sealed threshold (5) NOT modified | TRUE (operationalization only) |
| `no_dr_redefinition_post_seal` invariant held | TRUE |
| `no_strategy_optimization_authorized` invariant held | TRUE |

## 9. Files written this REFINEMENT turn

| File | Purpose |
|---|---|
| `tools/operator_side/s10_d1_mnq_mgc_step02c_audit_holiday_aware.py` | Holiday-aware audit script (local-only; ASCII-only; py_compile PASS) |
| `reports/external_research_hunter/s10_d1_mnq_mgc_step02c_audit_holiday_aware_report.md` | This refined audit report |
| `reports/external_research_hunter/s10_d1_mnq_mgc_step02c_audit_holiday_aware_report.json` | Companion JSON with structured verdict + verbatim audit-summary; embeds `report_seal_sha256` |

No other repository file is modified. The strict-audit script and strict-audit report from commit `9bdde45` remain byte-stable.

## 10. Status carried forward (UNCHANGED by this refinement)

| Field | Value |
|---|---|
| Trading | `PAUSED` |
| Live mode | `BLOCKED_AT_6_GATES` |
| FRC | `NEVER_GRANTED` |
| `no_strategy_optimization_authorized` | TRUE |
| `no_dr_redefinition_post_seal` | TRUE |
| `no_live_trading` | TRUE |
| `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` | permanent |

## 11. Narrowed forward paths (Path B refinement exhausted)

The holiday-aware refinement has been tried and the DR9 fire persists. The audit verdict is robust: 7 of MGC's 8 gaps are genuinely data-quality issues (mid-August and mid-October gaps that no holiday explains; one 17-day gap in October 2022). The remaining forward paths are NARROWER than before (this report does NOT recommend among them):

### Path A (now-recommended-by-default since Path B is exhausted) — Park the candidate

Authorization phrase (proposed):
```
Authorize s10 D1 MNQ+MGC candidate park under DR9 INCONCLUSIVE_HOLD.
```

The DR9 fire is robust under both strict and holiday-aware variants. The candidate cannot proceed to Step 03 loader build under the sealed-spec discipline. A full B006_NNN-style park memo would be authored under separate authorization to close the candidate lifecycle cleanly.

### Path C — Pivot to an alternative track

Authorization phrase (proposed):
```
Authorize alternative track selection plan revision only.
```

Options the operator might consider in a revised selection plan (NOT recommended by this report):

- **MNQ.c.0-only single-instrument candidate.** MNQ passed both audit variants cleanly. A fresh `B006_NNN`-style spec for an MNQ-only trend-following or vol-targeting candidate is structurally possible; would require a brand-new fresh-candidate-id spec drafted under separate authorization (NOT a B006_NNN revision; NOT an `_revN_` of s10 D1; the sealed s10 D1 universe is locked to MNQ+MGC together).
- **A 2-symbol futures candidate with a different second symbol** (e.g., M2K.c.0 micro Russell, MES.c.0 micro S&P 500). These need fresh S10-D1 availability probes against Databento; the existing S10-D1 memo only covered MNQ, MGC, MCL.
- **A back-to-ETF-proxy pivot** with a different mechanic family (T1-T7 from `docs/next_research_track_selection_plan_after_s9_park.md`).

### Path B+ — Try yet-deeper audit refinement (NOT recommended; documented for completeness only)

A speculative further refinement could attempt to characterize MGC's roll-period gaps using a quarterly-expiration calendar. This would be an audit-side refinement, not a sealed-spec change. But: the 17-day October 2022 gap, the August 2019 gap, and the dispersed mid-October pattern across 3 different years suggest the gaps are not cleanly tied to a roll-cycle window either. Further refinement is unlikely to recover the DR9 fire. The audit-heuristic refinement well is approximately dry.

## 12. One-paragraph summary

The holiday-aware audit refinement applied a hardcoded US/CME federal-holiday list (46 entries spanning 2019-2023) to the gap-counting heuristic of the strict s10 D1 Step 02c audit, reclassifying calendar gaps > 5 days that contained at least one federal holiday in their span as "holiday-explained" rather than "missing observations." The sealed DR9 threshold (`DR9_MAX_MISSING_OBSERVATIONS = 5`) was not modified; only the operationalization changed. MNQ.c.0 remained clean under both variants (0 gaps under both). **MGC.c.0's strict count of 8 gaps was reduced to a holiday-aware count of 7** — only 1 of the 8 gaps was holiday-explained (June 17-24, 2022, containing the Juneteenth observed holiday Mon June 20). The remaining 7 gaps fall in mid-August and mid-October across multiple years (2019, 2020, 2021, 2023×2 in October; 2019, 2023 in August) and include a particularly anomalous 17-day gap spanning October 7-24, 2022. None of these 7 gaps are explainable by any US federal holiday on the embedded list. The DR9 fire on MGC.c.0 is therefore robust — it is NOT an artifact of the strict heuristic over-counting holiday closures. The terminal refined verdict is **`DR9_FIRED_AUDIT_FAIL_HOLIDAY_AWARE`**, agreeing with the strict-audit verdict `DR9_FIRED_AUDIT_FAIL`. The likely structural reading (informational, not a sealed metric) is that MGC.c.0's Databento continuous-front-month stitch exhibits thin coverage around CME gold-futures roll cycles in certain months, particularly mid-August and mid-October; the October 2022 17-day gap is the most extreme single anomaly. The OOS-window structural row counts are recorded (MNQ 622, MGC 566) without any return / Sharpe / PnL analysis; `oos_inspection_blocked_at_in_sample` invariant held throughout. The Path B refinement well is approximately dry; the operator has two materially-distinct forward paths: Path A — park the candidate under `DR9 INCONCLUSIVE_HOLD` (DR9-robust, default); or Path C — pivot to an alternative track via a fresh selection-plan revision (e.g., MNQ-only single-instrument candidate as a brand-new candidate id, NOT a B006_NNN or s10 D1 revision). This report does **NOT** recommend among them. No Databento call. No network. No `DATABENTO_API_KEY` access. No OOS return summary. No strategy performance evaluation. No code beyond the holiday-aware audit script was authored. No mutation of any sealed prior artifact. `brain_memory/projects/trading_bot/lessons.md` dirty + unstaged state preserved. Trading remains `PAUSED`. Live remains `BLOCKED_AT_6_GATES`. FRC `NEVER_GRANTED`.

---

*Refined audit report. Local-only. No Databento. No network. No OOS return summary. No strategy evaluation. Faithful application of sealed-spec DR9 thresholds with holiday-aware operationalization refinement. Verdict robust to refinement.*
