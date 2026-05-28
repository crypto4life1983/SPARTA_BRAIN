# s16-d1 expanded-universe (12-name) cash-equity availability probe + DR9 audit RESULT (sealed)

**Authored (UTC):** `2026-05-28T21:58:56.753306Z`
**Lifecycle (post-audit):** `S16_D1_EXPANDED_CROSS_SECTOR_CASH_EQUITY_DR9_AUDIT_SEALED_BASKET_READY_FOR_PLAN`
**Report seal sha256:** `ec856253a28f7d538704b2610da8d1c3b13823335d741c356dd41259488b12e9`
**Authorization:** `Authorize s16-d1 expanded-universe Tiingo split_only fetch + DR9 result sealing workflow only.`

## Final verdict: **`DR9_ALL_12_PASS_EXPANDED_BASKET_READY_FOR_PLAN`** — all 12 PASS: **True**

## Provenance
Vendor: tiingo (split_only). Reused (DR9 carried by sha-match): AAPL/JPM/XOM (cross-sector a8ff9126), MSFT/NVDA (all-tech 1c93d429). Fresh Tiingo split_only: UNH, WMT, KO, META, AMZN, JNJ, CVX. Manifest: `data\s16_d1_expanded_cross_sector_cash_equity_long_history\raw\s16_d1_expanded_cross_sector_cash_equity_step02b_fetch_manifest.json` (sha `2825a762626e1faeb01ed6ec8e129edccaee675ff9bc6042b481b90eb4eb9e7f`).

## DR9 thresholds (cash-equity; immutable)
gap_continuity ≥ 0.95 · max_gap_ratio ≤ 0.30 · roll NOT_APPLICABLE · quality ≤ 5 · documented_split_event_consistency PASS

## Per-symbol results
| Symbol | rows | first | last | gap_continuity | max_gap_ratio | quality | split | DR9 |
|---|---|---|---|---|---|---|---|---|
| AAPL (REUSE; DR9 carried) | 1759 | 2019-01-02 | 2025-12-30 | 1.0 | 0.0 | 0 | PASS | **PASS** |
| MSFT (REUSE; DR9 carried) | 1759 | 2019-01-02 | 2025-12-30 | 1.0 | 0.0 | 0 | PASS | **PASS** |
| NVDA (REUSE; DR9 carried) | 1759 | 2019-01-02 | 2025-12-30 | 1.0 | 0.0 | 0 | PASS | **PASS** |
| JPM (REUSE; DR9 carried) | 1759 | 2019-01-02 | 2025-12-30 | 1.0 | 0.0 | 0 | PASS | **PASS** |
| XOM (REUSE; DR9 carried) | 1759 | 2019-01-02 | 2025-12-30 | 1.0 | 0.0 | 0 | PASS | **PASS** |
| UNH (fresh) | 1759 | 2019-01-02 | 2025-12-30 | 1.0 | 0.0 | 0 | PASS | **PASS** |
| WMT (fresh) | 1759 | 2019-01-02 | 2025-12-30 | 1.0 | 0.0 | 0 | PASS | **PASS** |
| KO (fresh) | 1759 | 2019-01-02 | 2025-12-30 | 1.0 | 0.0 | 0 | PASS | **PASS** |
| META (fresh) | 1759 | 2019-01-02 | 2025-12-30 | 1.0 | 0.0 | 0 | PASS | **PASS** |
| AMZN (fresh) | 1759 | 2019-01-02 | 2025-12-30 | 1.0 | 0.0 | 0 | PASS | **PASS** |
| JNJ (fresh) | 1759 | 2019-01-02 | 2025-12-30 | 1.0 | 0.0 | 0 | PASS | **PASS** |
| CVX (fresh) | 1759 | 2019-01-02 | 2025-12-30 | 1.0 | 0.0 | 0 | PASS | **PASS** |

Split-consistency highlights: AMZN 20:1 (2022-06-06) and WMT 3:1 (2024-02-26) verified under split_only; NVDA 4:1+10:1 and AAPL 4:1 carried; JNJ Kenvue spin-off (2023-08) informational (no split in window).

## Status
trading `PAUSED` · live `BLOCKED_AT_6_GATES` · FRC `NEVER_GRANTED` · DIAGNOSTIC_ONLY_NOT_LIVE_GRADE · s15/s14/s13/s12 terminal · framework DR10 v2 binding. Reused sources + all sealed artifacts preserved. lessons.md NOT touched.

## Next exact authorization
`Authorize s16-d1 expanded-universe Tier-N spec PLAN only — bound by DR10 v2.`

End of s16 expanded-universe DR9 audit result. Sealed. NOT a Tier-N SEAL. Mechanic selection deferred to the PLAN.
