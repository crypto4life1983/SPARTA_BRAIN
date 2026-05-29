# s19-d1 independent-universe weekly RS rotation — Tier-N spec DRAFT (sealed; REPLICATION of s18; NOT a Tier-N SEAL)

**Authored (UTC):** `2026-05-29T02:48:53.715442Z` · **report_seal:** `8231f11105614ace32874519eb5501dd0ebc67a9e61ddb12c2ebbfc44b016a8e`
**Candidate:** `s19-d1-independent-universe-weekly-relative-strength-rotation-24name-large-cap-long-history` · REPLICATION of the OOS_CONFIRMED s18 mechanic (SEAL `7e6aa36`). Parent s19 PLAN `6981339` (sha `6f0eb127284524dd…`); s19 DR9 `574fa9e`/`0c8e21f2…`.

## Replication, not tuning
Mechanic LOCKED byte-identical to s18 (126-21 RS signal, weekly R=5, top-8 equal-weight, long-only, relative-rank exit). DA1-DA22 mirror s18 **except** DA1 (id), DA14/DA16 (s19 provenance), DA17 (independent 24-name universe). No param changed/searched. s18 frozen.

## Pre-SEAL K9 turnover measurement (signal-only, NO P&L, s19 IS-only, OOS hard-excluded)
220 rebalances → **226 IS closed trades**. Per-fold MEASURED: F1=54 (~43/y), F2=79 (~62/y), F3=71 (~56/y).

| Gate | basis | value | verdict |
|---|---|---|---|
| K9 aggregate (IS, ≥100) | MEASURED | 226 | **CLEARS** |
| K13 per-fold | MEASURED F1/F2/F3 | 54/79/71 | CLEARS (F1 ~43/y marginal alone; aggregate clears) |
| OOS K9 (≥50/y) | PROJECTED (OOS not read) | ~90–117/2y | **CLEARS marginally** |
| DR10 v2 | turnover ~20×, cost_drag <1% | — | **CLEARS** |

**Pre-SEAL K9 gate: PASS** — K9 reachability REPLICATES s18 on the independent universe (s18: 229 IS/117 OOS).

## Edge NOT inherited
s18's OOS edge was thin + recently-weak (F5 negative). The s19 edge is re-proven from scratch at P6 IS (K1/K2). A null/negative s19 = s18 was universe-specific (accepted, informative). Stop-before-SEAL on edge/K13/P10-K9 failure; NOT rescued by tuning (a tune = not a replication).

## T-FORBID 16–24 cleared (incl. 23 replication-not-tune; 24 pre-SEAL K9 measured).

## Status
PAUSED · BLOCKED_AT_6_GATES · FRC NEVER_GRANTED · DIAGNOSTIC_ONLY_NOT_LIVE_GRADE. lessons.md NOT touched.

## Next
- Commit: `Authorize commit s19-d1 independent-universe weekly relative-strength rotation Tier-N spec DRAFT only.`
- Forward: `Authorize s19-d1 independent-universe weekly relative-strength rotation Tier-N spec SEAL only — bound by DR10 v2 + walk-forward K13.`
