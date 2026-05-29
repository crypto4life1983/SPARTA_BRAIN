# Multi-Market Bad-Regime Predictor — Step 02: Methodology plan (definitional)

**content_sha256:** `26b3cd10d5d735aca0078dc8ff5a13698d050713f6edc1cfbd30998613bef6d0` · **authored:** 2026-05-29T14:53:15.944871Z · anchors Step 01 (`b5ffe4daa7226099…`)
> Replaces the previously-cited but non-existent Step 02 commit `2a85b96`. THIS committed document is the source of truth for Step 03.

## Objective
For each market m in {ES, GC, CL, 6E} and each decision time t, produce a calibrated estimate (and binary label) of whether m will be in a 'bad regime' over the forward horizon H, using ONLY information available at or before t. Goal = predictive quality (classification), explicitly NOT trading signals or P&L.

## Target definition (binary, per market × decision-time t)
- **Rule (conceptual):** y=1 ('bad regime') iff the realized forward window (t, t+H] of market m meets a PRE-COMMITTED adverse-condition rule (e.g., elevated realized volatility and/or a large sustained adverse excursion); else 0. Thresholds pre-committed, estimated on **2024 only**.
- **Horizon H:** a single pre-committed forward horizon (fixed before labeling; not searched per result).
- **By design:** the TARGET may use the forward window (that is the label); FEATURES may not.
- **Computation:** NOT computed in Steps 01–03 (no returns/R/PnL/Sharpe). Step 03 audits only well-definedness + computability-in-principle + non-degenerate discovery base-rate. The adverse condition is a market-STATE labeling statistic, not a strategy return.

## Allowed decision-time features
Only features fully computable from data with timestamp ≤ t (point-in-time). Families (conceptual): trailing realized-vol/dispersion/momentum of m up to t; cross-market co-movement/dispersion up to t; term-structure/roll-state at t; point-in-time calendar/event flags. **Every feature window ends ≤ t; the label window opens strictly after t.**

## Forbidden features / leakage rules
No future data (timestamp > t); no target/label-window-derived features; no contemporaneous-bar leakage; point-in-time rolls/adjustments only (no future-baked back-adjustment); no OOS (2025) peeking; no outcome-based selection of thresholds/horizon/features; no SPARTA cross-project features.

## Data requirements (SPEC only — no fetch in this branch step)
ES/GC/CL/6E futures continuous-contract daily series (roll convention fixed + documented; point-in-time), fields date/OHLCV/OI/roll-metadata; discovery = full 2024 + prior warmup for the longest lookback; OOS = full 2025 (sealed; availability auditable, values not inspected).

## Discovery (2024) vs OOS (2025)
All design/fitting/inspection on **2024**. **2025 is a sealed write-once holdout** — not inspected/fitted/thresholded until a separate pre-registered OOS gate; target rule + H + feature set + metrics frozen before any 2025 touch.

## Validation gates (this branch's own — NOT SPARTA's)
G1 data integrity/point-in-time · G2 no feature↔target leakage · G3 target well-defined + sane base-rate · G4 discovery-only fitting · G5 OOS sealed until pre-registered · G6 honest reporting = **classification quality only** (AUC/precision/recall/calibration), never returns/PnL/Sharpe/tradeability/profitability.

## Exact Step 03 audit requirements
A3.1 data availability/coverage (ES/GC/CL/6E daily, 2024+warmup; 2025 availability only) · A3.2 point-in-time/roll correctness · A3.3 cross-market calendar alignment · A3.4 target computability/definedness + non-degenerate discovery base-rate (no returns computed) · A3.5 feature decision-time validity (windows ≤ t; no leaky feature) · A3.6 leakage + discovery/OOS firewall enforceable · A3.7 scope/guard compliance (no model/cluster/signal/backtest/returns; no tradeability/OOS/live/profitability claims; no SPARTA contamination). **Must not** train/cluster/signal/backtest, compute returns/R/PnL/Sharpe, fetch/inspect 2025 labels, or make tradeability/OOS/live/profitability claims. Output = exactly the two Step 03 files, grounded in (cite) this document. Commit only if separately authorized.

## Contamination firewall
Self-contained; imports NO SPARTA weekly-RS / FRC / BLOCKED_AT_6_GATES / DR-K-gate / Strategy-Lab concepts.

## Status
METHODOLOGY_DEFINED_READY_FOR_STEP_03_AUDIT · no data · no model · no claims.
