# s19-d1 weekly RS rotation INDEPENDENT-universe (24-name) availability probe + DR9 audit RUN_BOOK (NOT a SEAL)

**Authored (UTC):** `2026-05-29T02:37:21.252832Z`
**Authorization:** `Authorize s19-d1 weekly relative-strength rotation availability probe + DR9 audit framework only.`
**R1 of the post-s18 robustness-replication plan (`50e5fcf`).** RUN_BOOK only — no fetch, no DRAFT/SEAL/BUILD.

## Replication, NOT tuning
The s19 candidate will run the **IDENTICAL locked s18 mechanic byte-equivalent** (126-21 RS signal, weekly R=5, top-8 equal-weight, long-only, relative-rank exit, $100k, split_only). The **only change vs s18 is the UNIVERSE.** No parameter is altered/searched/tuned. s18 (SEAL `7e6aa36`; OOS_CONFIRMED P11 `5dde0f7`) is frozen and untouched. Purpose: test whether the s18 edge **generalizes** to independent data or was a single-universe artifact (LESSON_S18_D1_003/004). A pass would be corroborating diagnostic evidence — still DIAGNOSTIC_ONLY, still no live path.

## Independent universe (24; zero overlap with the s18/s17 basket)
ORCL, CSCO, ADBE, CRM, AMD, NFLX, TMUS, CMCSA, MCD, NKE, LOW, PEP, PM, MDLZ, GS, MS, WFC, AXP, LLY, ABT, TMO, SLB, EOG, HON
~8 GICS sectors (Tech, Comm Services, Consumer Disc/Staples, Financials, Health Care, Energy, Industrials). All 24 **fresh-fetch** (no reuse).

## Vendor / output
Tiingo `split_only` · window 2019-01-02→2025-12-30 · out dir `data/s19_d1_weekly_rs_rotation_independent_universe_long_history/raw` · manifest schema `sparta.s19.weekly_rs_rotation_independent_universe.step02b_fetch_manifest.v1`. TIINGO_API_KEY from env only; never printed.

## DR9 audit framework
gap_continuity ≥0.95 · max_gap_ratio ≤0.30 · quality ≤5 · roll NOT_APPLICABLE · documented_split_event_consistency PASS. No forward splits known in window for the 24 (verified at fetch via the Tiingo splitFactor stream); any spin-off factor (MRK-Organon precedent) is applied under split_only and verified for return-continuity.

## K9 / K13 / DR10 reachability
The s18 weekly mechanic MEASURED 229 IS / 117 OOS (58.7/y) trades on a 24-name basket → K9 aggregate + OOS K9 + K13 per-fold cleared. The identical mechanic on a same-size independent basket is EXPECTED to clear similarly; re-measured pre-SEAL on s19. K13 folds: identical DA22 scheme (warmup 0-159; F1 160-478…F5 1436-1758). DR10 v2 clears (weekly turnover ~20x but cost_drag <5%).

## Contingency tree
all 24 pass → s19 Tier-N spec PLAN (lock identical s18 mechanic); 1-8 fail → shrunk DR9 sealing (≥16 floor); 9+ fail → universe revision; split-consistency fail → INCONCLUSIVE_HOLD; vendor fail → blocker.

## Status
PAUSED · BLOCKED_AT_6_GATES · FRC NEVER_GRANTED · DIAGNOSTIC_ONLY_NOT_LIVE_GRADE · DR10 v2 + walk-forward K13 binding · s18 frozen (OOS_CONFIRMED diagnostic, not live). NOT a seal. lessons.md NOT touched.

## Next (post operator-side fetch)
`Authorize s19-d1 independent-universe Tiingo split_only fetch + DR9 result sealing workflow only.`
