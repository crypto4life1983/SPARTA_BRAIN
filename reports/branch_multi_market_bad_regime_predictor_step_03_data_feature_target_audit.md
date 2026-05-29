# Multi-Market Bad-Regime Predictor — Step 03: Data/Feature/Target AUDIT

**content_sha256:** `52df42868876adf02cbbd62d53236c56cdef54dae6eebc5165a3c2baec8e4a53` · **authored:** 2026-05-29T15:07:34.659517Z
**Source of truth:** Step 02 methodology plan — commit `b6c30d5` (content_sha256 `26b3cd10d5d735ac…`)
**VERDICT: `HALT`** (audit only; no data/model/returns/claims)

## Data inventory (availability only; no DBN/2025 content read)
| Market | Present | Format | Coverage | 2024 discovery | Assembled daily |
|---|---|---|---|---|---|
| ES | yes | parquet ohlcv-1d (ES.c.0, GLBX) | 2012-06..2022-12 (127 mo files) | **ABSENT (ends 2022-12)** | NO |
| GC | yes | DBN .dbn.zst (GC.c.0) | cache 2013..2022 · oos 2023..2025 | **only in oos cache** | NO |
| CL | yes | DBN .dbn.zst (CL.c.0) | cache 2013..2022 · oos 2023..2025 | **only in oos cache** | NO |
| **6E** | **NO** | — | **ABSENT (0 files)** | **MISSING** | NO |

## Required-check results
- **1. 2024 availability/coverage:** `FAIL` — 6E absent; ES/GC/CL undecoded/heterogeneous; 2024 GC/CL only inside the OOS-named cache.
- **2. point-in-time / roll correctness:** `NOT_EVALUABLE_BLOCKED` — series not decoded/assembled; roll convention unreconciled.
- **3. cross-market calendar/session alignment:** `NOT_EVALUABLE_BLOCKED` — 6E missing; multi-venue sessions differ; unverifiable.
- **4. target computability + base-rate:** `NOT_EVALUABLE_BLOCKED` — well-defined but not confirmable without assembled series (no labels/returns computed).
- **5. decision-time feature computability (≤ t):** `DESIGN_VALID_DATA_BLOCKED` — design-valid; data-blocked.
- **6. no feature↔target leakage:** `DESIGN_PASS` — rules sound; nothing computed.
- **7. discovery/OOS firewall enforceability:** `CONCERN` — **CONCERN:** 2024 & 2025 physically co-located in `databento_cache_oos`; need physical separation.
- **8. 2025 OOS blocked:** `CONFIRMED_BLOCKED_WITH_CAVEAT` — sealed/unused (availability listed only; values NOT inspected); 6E 2025 absent.
- **9. scope/guard compliance:** `PASS` — PASS (no model/cluster/signal/backtest/returns/fetch/2025-inspection/claims; no SPARTA contamination).

## Verdict: HALT
- TWO of four markets lack 2024 discovery data: 6E entirely absent (0 files), AND ES parquet ends 2022-12 (no ES 2023/2024/2025 in repo) -> 4-market scope not satisfiable from repo data (A3.1 FAIL).
- Only GC/CL have 2024 -- as UNDECODED DBN, and only inside the OOS-named cache (databento_cache_oos); not assembled into a unified point-in-time daily series; roll + cross-market calendar alignment unverifiable (A3.2/A3.3 blocked).
- 2024 discovery GC/CL co-located with sealed 2025 OOS in databento_cache_oos -> firewall needs physical separation (A3.7 concern).
- Target computability/base-rate and feature computability blocked on the above (A3.4 blocked; A3.5 data-blocked).

Design/process checks that PASS: feature/target leakage rules, scope/guard compliance, and 2025 procedural-seal (uninspected).

## Final-report fields
- **row/session counts:** NOT established (ES parquet + GC/CL DBN undecoded; 6E = 0); coverage at month granularity only.
- **coverage status:** ES parquet **2012-06..2022-12 only (2024 ABSENT)**; GC/CL present (DBN; 2024 only in oos cache); **6E ABSENT** -> **2 of 4 markets lack 2024 data**.
- **alignment status:** NOT_EVALUABLE_BLOCKED.
- **target computability:** NOT_EVALUABLE_BLOCKED (defined, not confirmable).
- **base-rate sanity:** NOT_ESTABLISHED (no computation).
- **feature availability:** DESIGN_VALID / DATA_BLOCKED.
- **leakage/firewall checks:** leakage rules DESIGN_PASS; discovery/OOS firewall CONCERN (physical co-mingling).
- **2025 OOS blocked:** CONFIRMED (sealed, not inspected; co-mingling caveat).
- **PASS/HALT:** **HALT.**

## Recommended next authorization
A bounded, separate **data acquisition + assembly + firewall-separation** step:
`Authorize Multi-Market Bad-Regime Predictor data acquisition + assembly + firewall-separation step (discovery 2024 + warmup only; acquire 6E; decode/assemble ES/GC/CL to unified point-in-time daily continuous; physically separate 2024-discovery from a SEALED 2025-OOS; no model/cluster/signal/backtest/returns; do not inspect 2025 values).`
Then re-run this Step 03 audit against the assembled discovery dataset.

## Guards
Audit only — no train/cluster/signal/backtest; no returns/R/PnL/Sharpe; no fetch; no 2025 value inspection; no tradeability/OOS/live/profitability claims; contamination firewall intact. Not committed.
