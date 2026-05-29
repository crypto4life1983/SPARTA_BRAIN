# Multi-Market Bad-Regime Predictor — CATALOG & PARK memo (read-only)

**content_sha256:** `ea0d0379e9b9e028eab45b4d8580a00060ebc458a0e9bdf55fdd7d4211d4defd` · **authored:** 2026-05-29T17:09:43.284951Z
**Status: `PARKED_DISCOVERY_NEGATIVE`** · **Source of truth:** Step 05 model eval `026d2c5` (sha `7376761230394cab`).

The Multi-Market Bad-Regime Predictor branch is PARKED as DISCOVERY-NEGATIVE: the data pipeline and vol-scaled target rebuild passed, but the simple pooled decision-time classification model showed NO leakage-safe within-2024 out-of-fold edge (pooled OOF AUC 0.471; no useful precision lift). The sealed 2025 OOS was never inspected and stays sealed.

## What passed
- Scope + methodology defined and contamination-firewalled (no SPARTA / weekly-RS / FRC / BLOCKED_AT_6_GATES concepts imported).
- Data acquisition/assembly: uniform ohlcv-1d continuous c.0 for ES/GC/CL/6E; discovery 2019-2024 physically separated from sealed 2025 OOS; SHA + calendar + roll documented.
- Target-rule amendment: vol-scaled regime-relative threshold (K from pooled 2019-2023 z-q80, NOT tuned to 2024) resolved CL degeneracy; all 4 markets non-degenerate.
- Step 04 feature/target table rebuilt (980 rows; 8 decision-time features; leaky z identified and excluded from modeling).
- Step 05 evaluation conducted leakage-safe: purged + embargoed (H=21) blocked within-2024 time-series CV, K=5, train-fold-only standardization, OOF coverage 100%, both classes present.

## What did not work (the reason for parking)
- Pooled out-of-fold AUC 0.471 -- at/below the 0.5 random baseline; no out-of-fold predictive edge from the simple pooled linear model within 2024.
- Precision-lift vs base-rate ~1.02 -- effectively no lift over the unconditional bad-regime base-rate (pooled 15.5%).
- Per-market OOF AUCs highly dispersed (ES 0.71 / GC 0.20 / CL 0.46 / 6E 0.38), several inverted -- consistent with small-sample noise (~245 rows/market, 7-22% base-rates), not a stable per-market edge.
- Mild IN-SAMPLE volatility/range-feature signal (vol_21 0.64, vol_63 0.61, range_21 0.61) did NOT survive the leakage-safe pooled OOF cross-validation (textbook in-sample-vs-OOF gap).

## Honest scope of this finding
This is a within-a-single-year (2024) discovery-stage finding using one simple deterministic linear model on 8 decision-time features. It is NOT a claim that bad regimes are unpredictable in general, nor a claim about any other model class, feature set, horizon, or market. It is a specific NEGATIVE result for THIS model on THIS discovery slice. No backtest, no signals, no returns/R/PnL/Sharpe, no trading system was ever built.

## Lifecycle ledger
| Step | Commit | Outcome | Note |
|---|---|---|---|
| 01 scope | `b6c30d5` | DEFINED | Prediction/classification research scope for bad regimes in ES/GC/CL/6E; explicitly NOT a trading system; contamination-firewalled (no SPARTA vocabulary). |
| 02 methodology plan | `b6c30d5` | DEFINED | Source-of-truth methodology: discovery 2019-2024 + sealed 2025 OOS; common-4 inner-join calendar; purged/embargoed time-series CV; classification metrics only. |
| 02 target-rule amendment | `5c2bea7` | PASS | Vol-scaled regime-relative target z(t)=fwd_maxDD/(trailing_21d_vol*sqrt(H)) >= K, K = pooled 2019-2023 z-q80 (n=5152, K=1.5575). Fixed CL degeneracy WITHOUT tuning to 2024. |
| 03 data/feature/target re-audit | `b1411c7` | PASS_CONDITIONAL | Assembled discovery dataset audited; GC Sunday-session coverage discrepancy diagnosed benign (max contiguous gap 2); inner-join common-4 calendar + physical 2024/2025 separation confirmed. |
| acquisition/assembly | `aba1796` | PASS | All 4 markets fetched uniform ohlcv-1d continuous c.0; discovery (2019-2024) physically separate from sealed 2025 OOS (SEALED_DO_NOT_INSPECT marker); values not inspected. |
| 04 feature/target rebuild (amended target) | `9164bd7` | PASS | 980 rows (245 labelable 2024 common-4 dates x 4 markets); 8 decision-time (<=t) features + leaky z (flagged exclude); base-rates ES 14.7%/GC 7.3%/CL 18.4%/6E 21.6%; pooled 15.5%; all 4 non-degenerate. |
| 05 model fit + within-2024 CV evaluation | `026d2c5` | PASS_METHODOLOGY / NEGATIVE_RESULT | Deterministic pooled logistic regression on the 8 decision-time features (leaky z excluded); purged + embargoed (H=21) blocked CV (K=5), OOF coverage 100%. Pooled OOF AUC 0.471 (<=0.5), precision-lift ~1.02 (none); per-market AUC dispersed (ES 0.71/GC 0.20/CL 0.46/6E 0.38) = small-sample noise; in-sample volatility-feature signal did not survive OOF. |

## Sealed 2025 OOS
**SEALED / NEVER INSPECTED** — No discovery-stage edge exists to confirm, so the one-shot 2025 OOS was not unsealed/spent; it remains available for a future pre-registered evaluation only if a discovery edge is first demonstrated under a pre-committed threshold.

## Park decision
Close the modeling line for this branch. Retain all artifacts read-only. Do NOT proceed to 2025 OOS. Any future revival requires a NEW pre-registered protocol (fixed model class, fixed features, pre-committed discovery AUC/lift threshold that must be met BEFORE any 2025-OOS authorization; no threshold tuning).

## Recommended next authorization
No further action required to park. If/when desired, either: (i) leave parked (no authorization needed); or (ii) 'Authorize Multi-Market Bad-Regime Predictor Step 05b pre-registered alternative-model discovery-only CV evaluation only' -- a SINGLE fixed pre-declared protocol under the same purged/embargoed within-discovery CV with a pre-committed edge threshold gating any future 2025-OOS use; no tuning, no 2025 inspection, no backtest/returns/signals. Commit of THIS memo requires a separate explicit authorization.
