# s10 D1 MNQ+MGC Step 02c Raw-Data Audit Report

Status: AUDIT_RUN_LOCALLY_BY_CONTROLLER (no Databento; no network; no OOS return analysis).
Authored: 2026-05-27 (audit run UTC: 2026-05-27T01:18:09Z)
Authorization: interpreted from operator's brief "autorize ok" as "Authorize s10 D1 MNQ+MGC Step 02c raw-data audit only."

Candidate: `s10-d1-cross-asset-trend-or-meanrev-mnq-mgc-databento-long-history`
Sealed spec reference: `docs/s10_d1_mnq_mgc_databento_long_history_tier_n_spec.md` (commit `9040429`)
Audit script: `tools/operator_side/s10_d1_mnq_mgc_step02c_audit_raw_data.py` (authored this turn; `py_compile` PASS)
Input artifacts: operator-captured Step 02b output in `data/s10_d1_mnq_mgc_databento_long_history/raw/`

---

## 1. Audit verdict (terminal)

# **`DR9_FIRED_AUDIT_FAIL`**

Closed-enum outcome: `DR9_FIRED_AUDIT_FAIL`. The audit was faithful to the sealed-spec DR9 thresholds; the fire originates from `MGC.c.0`'s `missing_observations` criterion. Per `no_dr_redefinition_post_seal`, the threshold is not negotiable; per `no_strategy_optimization_authorized`, parameter tuning is forbidden.

**This is NOT a parking memo** -- the operator must decide among three forward paths in section 11.

## 2. Sealed-spec DR9 thresholds applied (locked at SEAL)

| Threshold | Value |
|---|---|
| `DR9_MIN_PCT_EXPECTED_TRADING_DAYS` | **`0.95`** |
| `DR9_MAX_CONSECUTIVE_ABS_LOG_RETURN` | **`0.30`** |
| `DR9_MAX_MISSING_OBSERVATIONS` | **`5`** |
| `DR9_MAX_CONSECUTIVE_VIOLATION_THRESHOLD` | **`5`** |

## 3. Per-symbol audit results (computed by audit script)

### 3.1 MNQ.c.0 -- **CLEAN**

| Check | Value | Pass? |
|---|---|---|
| CSV sha256 matches manifest | `8b7b832c…dfa23e` | YES |
| Row count matches manifest | 2066 vs 2066 | YES |
| All required columns present | (`ts_event`, `open`, `high`, `low`, `close`, `volume`) | YES |
| First date | `2019-05-13` | within IS bounds |
| Last date | `2025-12-29` | within OOS bounds |
| IS-window row count | **1443** | observed |
| IS-window expected trading days (calendar baseline) | 1167 | -- |
| IS-window pct_observed | **1.2365** | PASS (>= 0.95) |
| IS-window calendar gaps > 5 days count | **0** | PASS (<= 5) |
| IS-window consecutive abs(log_return) > 0.30 count | **0** | PASS (<= 5) |
| IS-window max abs(log_return) observed (single day) | **0.1164** (~11.6%) | informational; well below 0.30 |
| OOS-window row count (structural; **NO return analysis**) | **622** | recorded |
| DR9 fire decision | **`clean`** | -- |

### 3.2 MGC.c.0 -- **DR9 FIRES**

| Check | Value | Pass? |
|---|---|---|
| CSV sha256 matches manifest | `79618abe…ccc4b` | YES |
| Row count matches manifest | 1814 vs 1814 | YES |
| All required columns present | (`ts_event`, `open`, `high`, `low`, `close`, `volume`) | YES |
| First date | `2019-05-13` | within IS bounds |
| Last date | `2025-12-28` | within OOS bounds |
| IS-window row count | **1247** | observed |
| IS-window expected trading days (calendar baseline) | 1167 | -- |
| IS-window pct_observed | **1.0686** | PASS (>= 0.95) |
| **IS-window calendar gaps > 5 days count** | **8** | **FAIL (> 5)** |
| IS-window consecutive abs(log_return) > 0.30 count | **0** | PASS (<= 5) |
| IS-window max abs(log_return) observed (single day) | **0.0713** (~7.1%) | informational; well below 0.30 |
| OOS-window row count (structural; **NO return analysis**) | **566** | recorded |
| **DR9 fire decision** | **`fire`** | -- |

## 4. Heuristic limitation note (load-bearing for operator interpretation)

The sealed spec defines `DR9_MAX_MISSING_OBSERVATIONS = 5` as the threshold but does NOT define the operationalization of "missing observation." The audit script implements the following heuristic:

> **Count distinct calendar-day gaps `> 5` between consecutive observed dates within the IS window.**

This heuristic catches:
- Genuine data gaps (multi-day vendor outages, roll-stitch failures, etc.).
- **Long market closures that are NOT actually data quality issues** (e.g., Thanksgiving long weekends, Christmas-New-Year transitions, occasional 4-day weekends around US federal holidays).

The MNQ.c.0 audit returned **0 such gaps**, suggesting the Databento continuous-stitch produces denser bar coverage on MNQ (likely including Sunday-evening sessions that bridge weekend / holiday gaps).

The MGC.c.0 audit returned **8 such gaps**, of which an unknown subset are genuine missing observations versus year-end / holiday-driven roll-stitch sparsity. The audit script does not have a CME futures holiday calendar loaded (no network access at audit time; no operator-provided holiday list ingested).

**Two interpretations are both technically defensible:**

| Interpretation | Implication |
|---|---|
| **Strict** -- gaps > 5 days = "missing observations" regardless of cause | DR9 fires on MGC.c.0; this audit's verdict stands as `DR9_FIRED_AUDIT_FAIL` |
| **Holiday-aware** -- exclude gaps explained by known US/CME market holidays | Some unknown subset of the 8 MGC gaps would be reclassified as "expected closures, not missing observations"; the verdict could potentially flip to `clean` if the count drops to <= 5 |

The audit script implements the strict interpretation because the sealed spec does not codify a holiday-aware variant. A refinement audit under separate authorization could implement the holiday-aware variant; this would be an audit-side refinement, NOT a DR9 threshold modification (which `no_dr_redefinition_post_seal` forbids).

## 5. Operator-reported reduced-quality days handling

The Databento client emitted a `BentoWarning: reduced quality days including 2020-02-27, 2020-02-28, 2020-06-30` during the operator-side fetch.

Audit findings on these specific dates:

- All three dates fall within the **IS window** for both symbols.
- The audit's consecutive `abs(log_return) > 0.30` check (DR9 criterion) did NOT fire on either symbol; max abs(log_return) observed was 0.1164 (MNQ) and 0.0713 (MGC), well below the 0.30 threshold.
- The reduced-quality flag is **informational** for the operator; it did NOT cause the DR9 fire on MGC. The DR9 fire is on the `missing_observations` criterion (calendar gap counting), not on the consecutive-abs-log-return criterion.

## 6. OOS-window structural verification (NO return analysis)

The audit reports the OOS-window row counts ONLY as structural existence checks:

- MNQ.c.0 OOS row count: **622** (window `2024-01-02 -> 2025-12-30`)
- MGC.c.0 OOS row count: **566**

The audit did **NOT**:
- Compute returns, Sharpe, PnL, drawdown, win-rate, or any performance metric over the OOS window.
- Inspect OOS row values beyond timestamp parsing.
- Apply any DR9 sub-check to the OOS window (DR9 is evaluated on IS only at this phase per sealed-spec OOS-locking policy).

OOS data is fetched-and-locked per the sealed spec; this audit treats OOS rows as opaque structural payload.

## 7. Boundary-attestation block (audit script self-disclosure)

The audit script's behavior in this run:

| Attestation | Status |
|---|---|
| Local file reads only | TRUE |
| No Databento call | TRUE |
| No network IO | TRUE |
| No `DATABENTO_API_KEY` access | TRUE |
| No OOS return summary | TRUE |
| No strategy performance evaluation | TRUE |
| No Sharpe / PnL / drawdown / win-rate computation | TRUE |
| `abs(log_return)` computed ONLY for DR9 outlier check, not for any strategy claim | TRUE |
| No row content printed (only counts, shas, timestamps, DR9 metrics) | TRUE |
| No mutation of `review_queue.json` | TRUE |
| No mutation of production `idea_memory` | TRUE |
| No mutation of any sealed prior artifact | TRUE |
| No mutation of `brain_memory/projects/trading_bot/lessons.md` (dirty + unstaged preserved) | TRUE |
| Sealed-spec `commit_anchor` cross-checked against manifest before audit run | TRUE (both `9040429`) |

## 8. Per-file sha256 ledger (cross-checked)

| File | sha256 | Bytes |
|---|---|---|
| `data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_c_0_ohlcv_1d_20190513_20251230.csv` | `8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e` | 178,349 |
| `data/s10_d1_mnq_mgc_databento_long_history/raw/MGC_c_0_ohlcv_1d_20190513_20251230.csv` | `79618abec8c34e59f0cc52420afc455c0d7dbdf13bf96605224e27247c9ccc4b` | 142,234 |
| `data/s10_d1_mnq_mgc_databento_long_history/raw/s10_d1_mnq_mgc_step02b_fetch_manifest.json` | `d6cf8c8b4cc81ff0b85085db5bc83b02b3bf795887b6a49ca71898b77c926225` | 2,432 |

All three match the operator paste-back from the Step 02b run.

## 9. Files written this AUDIT turn

| File | Purpose |
|---|---|
| `tools/operator_side/s10_d1_mnq_mgc_step02c_audit_raw_data.py` | Audit script (local-only; ASCII-only; `py_compile` PASS; no network; no Databento) |
| `reports/external_research_hunter/s10_d1_mnq_mgc_step02c_audit_report.md` | This audit report |
| `reports/external_research_hunter/s10_d1_mnq_mgc_step02c_audit_report.json` | Companion JSON with structured verdict and full per-symbol audit dump; embeds `report_seal_sha256` |

No other repository file is modified. `brain_memory/projects/trading_bot/lessons.md` dirty + unstaged state preserved.

## 10. Status carried forward (UNCHANGED by this audit)

| Field | Value |
|---|---|
| Trading | `PAUSED` |
| Live mode | `BLOCKED_AT_6_GATES` |
| FRC | `NEVER_GRANTED` |
| `no_strategy_optimization_authorized` | TRUE |
| `no_dr_redefinition_post_seal` | TRUE |
| `no_live_trading` | TRUE |
| `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` | permanent |

## 11. Three operator-facing forward paths (each requires separate authorization)

This audit report does **not** recommend among the three options. The operator picks one.

### Path A -- Accept the strict-DR9 verdict and park the candidate under `DR9_FIRED_INCONCLUSIVE_HOLD`

- Authorization phrase (proposed): `Authorize s10 D1 MNQ+MGC candidate park under DR9 INCONCLUSIVE_HOLD.`
- Outcome: candidate archived without further build phases; full B006_NNN-style park memo authored separately.
- Pros: most conservative; respects strict interpretation of the sealed threshold; consistent with `no_strategy_optimization_authorized`.
- Cons: parks a candidate where some unknown fraction of the gap count is likely holiday-driven, not actual missing observations.

### Path B -- Authorize a refinement audit using a holiday-aware gap classification

- Authorization phrase (proposed): `Authorize s10 D1 MNQ+MGC Step 02c holiday-aware audit refinement only.`
- Outcome: new audit script that ingests a hardcoded US/CME federal-holiday list, excludes gaps explained by those holidays from the `missing_observations` count, and re-evaluates DR9 under the refined heuristic. The DR9 *threshold* (5) remains sealed; only the operationalization of "missing observation" changes.
- Pros: more faithful to the spirit of DR9 (catch genuine data gaps, not market holidays).
- Cons: introduces a new heuristic at audit time; if MGC still fires under the refined audit, the candidate is parked.
- Risk surface: a hardcoded holiday list is brittle (Good Friday, exchange-specific market closures, occasional emergency closures); a refined audit's output is only as good as the holiday list it embeds.

### Path C -- Authorize an alternative-track selection plan revision

- Authorization phrase (proposed): `Authorize alternative track selection plan revision only.`
- Outcome: revise `docs/next_research_track_selection_plan_after_s9_park.md` to consider a different track (T1 / T2 / T3 / T4 / T5 / T6 / T9 / T10), given that this Databento futures pivot encountered a DR9 fire at the audit phase.
- Pros: pivots away from the MNQ+MGC universe if the operator judges the data-quality finding is structural to MGC's continuous-stitch.
- Cons: extends time-to-completion of the trading-bot research arc.

---

## 12. One-paragraph summary

The s10 D1 Step 02c raw-data audit ran locally (no Databento, no network, no OOS return analysis) against the operator-captured Step 02b output. The audit verified file-level sha256 anchors, row-count match against manifest, required-column presence, and applied the sealed-spec DR9 thresholds (`DR9_MIN_PCT_EXPECTED_TRADING_DAYS = 0.95`, `DR9_MAX_CONSECUTIVE_ABS_LOG_RETURN = 0.30`, `DR9_MAX_MISSING_OBSERVATIONS = 5`, `DR9_MAX_CONSECUTIVE_VIOLATION_THRESHOLD = 5`) to each symbol's IS-window data. **MNQ.c.0 is clean across all four DR9 criteria** (1,443 IS rows; pct_observed 1.2365; 0 gaps > 5 days; 0 consecutive abs-log-return violations; max single-day abs-log-return 0.1164). **MGC.c.0 fails the `missing_observations` criterion** with 8 calendar gaps > 5 days versus the threshold of 5, though it passes the other three DR9 criteria (1,247 IS rows; pct_observed 1.0686; 0 consecutive abs-log-return violations; max single-day abs-log-return 0.0713). The audit verdict is **`DR9_FIRED_AUDIT_FAIL`**. The audit script's missing-observations heuristic counts calendar-day gaps > 5 strictly, without a CME holiday calendar; an unknown subset of the 8 MGC gaps may be holiday-driven rather than genuine missing observations. The operator-reported Databento `BentoWarning: reduced quality days` flag for 2020-02-27 / 2020-02-28 / 2020-06-30 is informational only -- those dates did NOT trigger the DR9 consecutive-abs-log-return criterion (max abs-log-return well below the 0.30 threshold across both symbols). OOS-window structural row counts are recorded (MNQ 622; MGC 566) without any return / Sharpe / PnL analysis. The operator has three forward paths: (A) accept the strict-DR9 verdict and park the candidate under `DR9_FIRED_INCONCLUSIVE_HOLD`; (B) authorize a holiday-aware audit refinement that excludes holiday-explained gaps from the `missing_observations` count (the DR9 threshold remains sealed; only the operationalization changes); or (C) revise the next-research-track selection plan to consider an alternative track. This report does NOT recommend among the three. No code beyond the audit script was authored. No Databento call. No network. No `DATABENTO_API_KEY` access. No OOS return summary. No strategy performance evaluation. No mutation of any sealed prior artifact. `brain_memory/projects/trading_bot/lessons.md` dirty + unstaged state preserved. Trading remains `PAUSED`. Live remains `BLOCKED_AT_6_GATES`. FRC `NEVER_GRANTED`.

---

*Audit report. Local-only. No Databento. No network. No OOS return summary. No strategy evaluation. Faithful application of sealed-spec DR9 thresholds; heuristic limitation explicitly disclosed in section 4.*
