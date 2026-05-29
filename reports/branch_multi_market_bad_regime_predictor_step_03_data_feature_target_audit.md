# Multi-Market Bad-Regime Predictor — Step 03 RE-AUDIT (assembled discovery dataset)

**content_sha256:** `185ef1783e1e66b418dec109d15b12ec36d759cea84266d66dd6fe55e8c1d83f` · **authored:** 2026-05-29T16:25:09.655112Z
**Source of truth:** Step 02 `b6c30d5` (sha `26b3cd10d5d735ac…`) + acquisition `aba1796` (manifest sha `310084ef9fda5900…`)
**VERDICT: `PASS_CONDITIONAL`** — prior data-availability HALT RESOLVED; cleared to proceed to Step 04 labeling on discovery (audit-only; no modeling/returns/claims).

## Discovery inventory (2019-01-02..2024-12-30; discovery CSVs read; OHLC/monotonic integrity)
| Mkt | rows | 2024 days | OHLC viol | non-mono | dupes | sha256 |
|---|---|---|---|---|---|---|
| ES | 1866 | 312 | 0 | 0 | 0 | `3d98248541bb974a…` |
| GC | 1589 | **266** | 0 | 0 | 0 | `ebac946c8de6127f…` |
| CL | 1863 | 312 | 0 | 0 | 0 | `a9d5ea657ca06b2c…` |
| 6E | 1798 | 311 | 0 | 0 | 0 | `3d88c08586ef0715…` |

## Check results (A3.1–A3.9)
- **A3.1 availability/coverage:** `PASS_WITH_CAVEAT` — all 4 present (6E + ES-2024 gaps RESOLVED); GC 2024 day-count low (caveat).
- **A3.2 point-in-time/roll:** `PASS` — uniform continuous c.0; OHLC sane; dates strictly increasing; 0 dupes.
- **A3.3 calendar alignment:** `PASS_WITH_CONCERN` — inner-join common-4 2024 = **266** (union 312); GC shortfall = session-convention (GC continuous daily omits a recurring weekday set; the ES-extra dates concentrate on specific weekdays) -- NOT large contiguous data gaps; ES-not-GC weekdays {'Sun': 32, 'Mon': 4, 'Wed': 5, 'Fri': 2, 'Tue': 3}.
- **A3.4 target computability:** `PASS_WITH_CONSTRAINT` — computable; **label window must not reach sealed 2025 (cap t+H ≤ 2024-12-30)**; no labels computed.
- **A3.5 base-rate sanity:** `DEFERRED_NOT_COMPUTED` — estimable-in-principle; NOT computed (deferred to labeling; no returns).
- **A3.6 feature ≤ t computability:** `DESIGN_VALID_DATA_READY` — design-valid; data now ready.
- **A3.7 no leakage:** `DESIGN_PASS` — rules sound; nothing computed; forward-cap prevents 2025 reach.
- **A3.8 discovery/OOS firewall:** `PASS` — distinct dirs; SEALED marker=True; discovery has no 2025; **OOS CSVs not opened** (availability/hash via manifest only).
- **A3.9 scope/guard:** `PASS` — PASS.

## Explicitly evaluated
- **GC coverage discrepancy:** GC 2024 = 266 days vs ES 312 / CL 312 / 6E 311; Δ vs ES = 46. Diagnosis: session-convention (GC continuous daily omits a recurring weekday set; the ES-extra dates concentrate on specific weekdays) -- NOT large contiguous data gaps. Resolution: inner-join common-4 calendar (266 2024 days).
- **Degraded-day flags:** Databento flagged degraded days in 2019 warmup (and a few in sealed 2025, not inspected) → pre-committed quality rule before labeling (C2).
- **Inner-join common-4 rule:** decision-time index = days all 4 markets trade (266 in 2024); no forward-fill.
- **Physical separation:** `discovery_2019_2024` vs `oos_2025_sealed` distinct; SEALED marker present; discovery 2025-free; OOS not value-inspected.

## Conditions carried (not blockers)
- C1 (GC coverage): accept/justify GC's lower 2024 session count (266) and use the inner-join common-4 calendar (266 2024 dates) as the decision-time index; session-convention (GC continuous daily omits a recurring weekday set; the ES-extra dates concentrate on specific weekdays) -- NOT large contiguous data gaps.
- C2 (degraded days): Databento flagged 'degraded'-quality days in the warmup (several in 2019) and in the SEALED 2025 set; before labeling, apply a PRE-COMMITTED quality rule (e.g., exclude or flag degraded discovery days). Degraded != missing; bars were returned.
- C3 (forward-window cap): cap labelable discovery decision dates at t+H <= last discovery bar so the target window never reaches sealed 2025.
- C4 (base-rate): compute the discovery base-rate in the authorized labeling step (not here); verify non-degeneracy then.
- C5 (firewall): keep oos_2025_sealed untouched until a separate pre-registered OOS gate.

## Final
**VERDICT: PASS_CONDITIONAL** (prior HALT resolved; cleared for Step 04 labeling on discovery; not a tradeability/OOS/profitability claim). Audit-only; no commit.

## Recommended next authorization
`Authorize Multi-Market Bad-Regime Predictor Step 04 feature/target construction on DISCOVERY only — commit aba1796 data; apply the inner-join common-4 calendar (266 2024 days), a pre-committed degraded-day rule, and the t+H<=last-discovery-bar label cap; compute decision-time features (<= t) and the binary bad-regime label + discovery base-rate; NO model/cluster/signal/backtest, NO returns/R/PnL/Sharpe, NO 2025 inspection, NO tradeability/profitability claims.`
