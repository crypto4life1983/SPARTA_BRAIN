# s14-d1-cross-sector cash-equity availability probe + DR9 audit RESULT (sealed)

**Authored (UTC):** `2026-05-28T18:13:56.548842Z`
**Lifecycle (post-audit):** `S14_D1_CROSS_SECTOR_CASH_EQUITY_AVAILABILITY_PROBE_DR9_AUDIT_SEALED_BASKET_READY_FOR_DRAFT`
**Report seal sha256:** `a8ff91263e64529d52ac8b974ec01d8517d4bc7187df124b9938323870078a9c`
**Candidate:** `s14-d1-aapl-jpm-xom-cross-sector-cash-equity-rsi-3-bi-directional-large-cap-long-history`
**Authorization:** `Authorize s14-d1-cross-sector Tiingo split_only fetch + DR9 result sealing workflow only.`

## Final verdict: **`DR9_ALL_3_PASS_CROSS_SECTOR_BASKET_READY_FOR_DRAFT`**
All 3 symbols DR9 PASS: **True**

## Provenance
| Field | Value |
|---|---|
| Vendor | tiingo (split_only) |
| AAPL | REUSED byte-equivalent from all-tech (sha `f6625ff1a6f8026369344bd50ca82bffcba716f1f3be9cdcfb5b905e35f893a9`); DR9 PASS carried from all-tech result_seal `1c93d4294e193b25b239fd613f4ff1e9d24a16860376ee31efd7ec2ef01eda40` |
| JPM, XOM | fresh Tiingo split_only fetch (no splits in window) |
| Manifest | `data\s14_d1_aapl_jpm_xom_cross_sector_cash_equity_long_history\raw\s14_d1_cross_sector_cash_equity_step02b_fetch_manifest.json` (sha `dbd886eb1cc424aea29fd60405a6b83e09ef4454a593ce8bbb3be586768ba983`) |
| Cross-sector PLAN | commit `c61860d` |
| Cross-sector RUN_BOOK | commit `4fc06ec` |

## DR9 thresholds (cash-equity adapted; immutable)
gap_continuity ≥ 0.95 · max_gap_ratio ≤ 0.30 · roll_event_count NOT_APPLICABLE_CASH_EQUITY · quality_violation_count ≤ 5 · documented_split_event_consistency PASS

## Per-symbol results
| Symbol | rows | first | last | gap_continuity | max_gap_ratio | quality_viol | split_consistency | DR9 |
|---|---|---|---|---|---|---|---|---|
| AAPL (REUSED from all-tech; DR9 PASS carried by sha-match) | 1759 | 2019-01-02 | 2025-12-30 | 1.0 | 0.0 | 0 | PASS | **PASS** |
| JPM | 1759 | 2019-01-02 | 2025-12-30 | 1.0 | 0.0 | 0 | PASS | **PASS** |
| XOM | 1759 | 2019-01-02 | 2025-12-30 | 1.0 | 0.0 | 0 | PASS | **PASS** |

## Status
trading `PAUSED` · live `BLOCKED_AT_6_GATES` · FRC `NEVER_GRANTED` · DIAGNOSTIC_ONLY_NOT_LIVE_GRADE · s13-d1 + s12-d1 terminal · framework DR10 v2 binding for s14+. all-tech sibling DRAFT (214bae0) + all-tech AAPL source preserved byte-stable. lessons.md NOT touched.

## Next exact authorization
`Authorize s14-d1-cross-sector cash-equity Tier-N spec DRAFT only — bound by DR10 v2.`

End of cross-sector DR9 audit result. Sealed. NOT a Tier-N SEAL.
