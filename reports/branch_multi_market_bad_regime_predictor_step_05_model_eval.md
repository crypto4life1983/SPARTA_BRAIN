# Multi-Market Bad-Regime Predictor — Step 05 discovery-only model + CV evaluation

**content_sha256:** `7376761230394cab409f0eaaa25f39a474a3ad9fcd3d245d16ba425cec27a982` · **authored:** 2026-05-29T17:06:10.924190Z
**Source:** Step 04 table `9164bd7` + Step 02 amendment `5c2bea7`. **VERDICT: `PASS`** (evaluation validly conducted; NOT a tradeability/profitability/OOS claim).

## Candidate models
- **M1 logistic regression** (deterministic numpy GD; 8 decision-time features; pooled across markets; per-fold standardization).
- **B0 base-rate baseline** (AUC 0.5).
- **Univariate rule-table diagnostic** (in-sample AUC per feature; screening only).
- **Excluded features:** `z_vol_scaled_fwd_maxdd` (label-derived → leakage), `dow`/`month` (calendar; off primary).

## CV design (leakage-safe)
Purged + **embargoed (H=21)** blocked time-series K-fold (K=5) by decision-date; train excludes test dates and any date within H of the test block; train-fold-only standardization. OOF coverage **100.0%**.

## Key findings (substantive: NEGATIVE)
- NEGATIVE RESULT (substantive): the simple pooled linear model shows NO out-of-fold predictive edge within 2024 -- pooled OOF AUC 0.4711 is at/below the 0.5 random baseline; precision-lift vs base-rate 1.018 (~1.0 = none).
- Per-market OOF AUCs are HIGHLY DISPERSED (ES 0.705 / GC 0.198 / CL 0.456 / 6E 0.382), several below 0.5 (inverted). With ~245 rows/market and few positives this dispersion is consistent with small-sample noise, NOT a stable per-market edge.
- Univariate IN-SAMPLE feature AUCs are mildly above 0.5 for volatility/range features (vol_21 0.643, vol_63 0.614, range_21 0.607) but this in-sample signal does NOT survive the leakage-safe pooled OOF cross-validation -- a textbook in-sample-vs-OOF gap.
- Implication for the sealed 2025 OOS: there is NO discovery-stage edge to confirm, so the sealed 2025 OOS should NOT be unsealed/spent on this model. Doing so now would waste the one-shot OOS on a model with no demonstrated discovery signal.

## OOF metrics (discovery in-sample, 2024)
- **Pooled AUC: 0.4711** (baseline 0.5) · Brier 0.16943 · pooled base-rate 0.1551.
- Threshold = (1−base_rate) score-quantile → confusion {'tp': 24, 'fp': 128, 'fn': 128, 'tn': 700, 'precision': 0.15789473684210525, 'recall': 0.15789473684210525, 'f1': 0.15789473684210525} · precision-lift vs base-rate 1.018.

| Market | n | base-rate | AUC | precision@thr | recall | lift |
|---|---|---|---|---|---|---|
| ES | 245 | 0.1469 | 0.7053 | 0.0833 | 0.0833 | 0.567 |
| GC | 245 | 0.0735 | 0.1977 | 0.0 | 0.0 | None |
| CL | 245 | 0.1837 | 0.4562 | 0.2222 | 0.2222 | 1.21 |
| 6E | 245 | 0.2163 | 0.3819 | 0.2642 | 0.2642 | 1.221 |

## Univariate in-sample feature AUC (diagnostic only)
{"ret_21": 0.5532, "ret_63": 0.5659, "vol_21": 0.6426, "vol_63": 0.6142, "range_21": 0.6072, "dist_high_252": 0.5496, "xmkt_corr_21": 0.5311, "xmkt_disp_21": 0.5531}

## Honest limitations
- DISCOVERY IN-SAMPLE ONLY: cross-validation is within a SINGLE year (2024) -> evaluates within-2024 generalization across dates, NOT across regimes/years; 2025 OOS untouched.
- Small sample: 245 2024 decision dates x 4 markets = 980 rows; label base-rates 7-22% (class imbalance); CV folds are small.
- Label autocorrelation: overlapping forward windows make adjacent dates' labels correlated; purge+embargo (H=21) mitigates but does not eliminate finite-sample optimism.
- Pooled model treats markets jointly; per-market metrics have fewer rows/positives -> noisier.
- Metrics are CLASSIFICATION diagnostics ONLY (AUC/precision/recall/calibration/lift). They are NOT returns, PnL, Sharpe, or any tradeability/profitability measure; no strategy was constructed or backtested.
- Univariate AUCs are IN-SAMPLE diagnostics (feature screening), not the cross-validated result.
- A single deterministic linear model + simple features; no model selection/tuning performed (would need its own pre-registered protocol).

## Verdict
**PASS** — discovery-only, leakage-safe within-2024 CV validly conducted; metrics computed honestly. This certifies the EVALUATION, not an edge: it is NOT tradeability, OOS confirmation, live readiness, or profitability. 2025 OOS untouched.

## Recommended next authorization
Operator's choice between two in-protocol paths (the sealed 2025 OOS stays SEALED in BOTH): (A) CATALOG-AND-PARK -- 'Authorize Multi-Market Bad-Regime Predictor catalog + park as DISCOVERY-NEGATIVE only' -- record that a simple pooled linear model found no leakage-safe within-2024 OOF edge; close the modeling line; commit Step 05 + catalog memo; OR (B) ONE pre-registered alternative-model attempt -- 'Authorize Multi-Market Bad-Regime Predictor Step 05b pre-registered alternative-model discovery-only CV evaluation only' -- a SINGLE fixed, pre-declared protocol (e.g. per-market logistic + one shallow nonlinear baseline) under the SAME purged/embargoed within-discovery CV, with a pre-committed discovery AUC/lift threshold that MUST be met before any future 2025-OOS authorization, NO threshold tuning, NO 2025 inspection, NO backtest/returns/signals. Default recommendation: (A), given the negative result; commit Step 05 outputs first under a separate commit authorization either way.
