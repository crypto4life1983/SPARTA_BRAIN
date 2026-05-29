# Multi-Market Bad-Regime Predictor — Step 02 target-rule AMENDMENT

**content_sha256:** `72572a47eb60a11ff7d1393db0fc93ee544d4910a1282aa861346de6ccd9c9ff` · **authored:** 2026-05-29T16:47:26.589919Z · amends Step 02 (b6c30d5); grounded in Step 04 (1573893)

## Problem
Original target (absolute per-market fwd-maxDD >= 2019-2023 q80) made **CL degenerate (2024 base-rate 0.0%)**: CL's q80 = 0.152, inflated by the 2020-2022 oil period; calmer 2024 never reaches it.

## Options
- **A (absolute quantile, original):** REJECTED — fixed absolute level from an extreme regime is not regime-appropriate → degeneracy.
- **B (rolling/recent-window threshold):** valid; adapts to recent vol; heavier machinery.
- **C (volatility-scaled, regime-relative) — SELECTED:** `bad=1 iff z(t)=fwd_maxDD(t,H)/(trailing_21d_vol(t)·√H) ≥ K`, K = pooled 80th-pct of z over **2019-2023 only**, single K for all 4 markets. Regime/market-relative, comparable, single pre-committed threshold; removes the absolute-level inflation.

## No-tuning-to-2024
K fixed from 2019-2023 **before** any 2024 label is computed; 2024 base-rates measured once and reported as-is; method chosen on the degeneracy mechanism, not 2024 outcomes.

## Unchanged
inner-join common-4 calendar; t+H≤last-discovery-bar cap (no 2025 reach); decision-time features (≤ t); degraded-day rule; discovery-only fitting; 2025 sealed.

Guards: no model/cluster/signal/backtest; no returns/R/PnL/Sharpe; no 2025 inspection; no 2024 tuning; firewalled.
