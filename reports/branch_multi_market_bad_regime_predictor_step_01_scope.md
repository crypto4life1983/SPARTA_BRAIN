# Multi-Market Bad-Regime Predictor — Step 01: Scope (definitional)

**content_sha256:** `b5ffe4daa72260992cf453922e4d053a0dd388e9ae156908360a28e78c9ea009` · **authored:** 2026-05-29T14:53:15.944871Z

## Objective
Define the scope of a research project to PREDICT, at decision time, whether the near-future environment of each of four futures markets (ES, GC, CL, 6E) is a 'bad regime' (to be precisely defined in Step 02) -- a supervised classification/forecasting problem, NOT a trading system.

## What this is
A multi-market, decision-time predictive-classification study: given only information available at time t, estimate the probability/label that market m enters a 'bad regime' over a forward horizon H. The deliverable is predictive understanding + honestly-measured classification quality -- never orders, signals, or P&L.

## What this is NOT
- NOT a trading strategy, signal generator, or execution system.
- NOT a returns/PnL/Sharpe study -- evaluation is classification quality only (e.g., AUC/precision/recall/calibration), computed in later authorized steps.
- NOT a claim of tradeability, OOS confirmation, live readiness, or profitability at any stage of this branch.

## Markets in scope (FIXED)
ES (E-mini S&P 500), GC (Gold), CL (WTI Crude), 6E (Euro FX) — four structurally-distinct, liquid futures across equity/metal/energy/FX.

## Temporal scope
- **Discovery:** 2024 (in-sample; all design/fitting/inspection).
- **OOS holdout:** 2025 (strictly SEALED; untouched until a separate pre-registered gate).

## Deliverable chain
Step 01 scope → Step 02 methodology → Step 03 data/feature/target audit → later (separately authorized) steps.

## Contamination firewall
Self-contained. Does NOT import SPARTA_BRAIN weekly-RS rotation / FRC / BLOCKED_AT_6_GATES / DR-K gates / Strategy-Lab or any cross-project vocabulary. This branch's gates and terminology are its own.

## Guards (this step)
Definitional only — no data fetch, no model, no clustering, no signals, no backtest, no returns/R/PnL/Sharpe; no tradeability/OOS/live/profitability claims; prediction research, not trading.
