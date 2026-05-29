# s19-d1 independent-universe weekly RS rotation — P11 lifecycle decision (sealed; TERMINAL by INSUFFICIENT_SAMPLE/K9 at P10)

**Authored (UTC):** `2026-05-29T03:21:08.214047Z` · **report_seal:** `3f648187f10c2e64f87c3eaa5d791499354b17daccc8dc637b565d542ad713d6` · **run_id:** `PHASE2-S19-D1-P11-9725c1d5cc5c`
**Verdict: `INSUFFICIENT_SAMPLE`** — lifecycle TERMINAL (K9 at P10). NUANCED replication outcome.

## Terminal driver: K9 (OOS 87 trades / 43.65/y < 50/y floor)
The independent-universe OOS turnover fell below the K9 floor (87 < 100 over 2y; 43.6/y < 50/y). K9 is INVIOLATE and precedes DR4 -> INSUFFICIENT_SAMPLE, even though the OOS edge was positive (DR4 would not have fired). Pre-SEAL projection (~90-117) was optimistic vs the actual 87.

## The edge GENERALIZED (corroborates s18)
s19 OOS net **+$44,049.52**, expectancy **+$336.08/trade** (vs s18 +$210.43), sharpe **+0.238** (vs +0.125), win 59.77%, PF 2.23 — **stronger per-trade than s18**. IS + cost-stress + 5/5 K13 + positive OOS all held on genuinely independent data. The weekly RS edge direction is corroborated as real/portable, NOT an s18 single-universe artifact.

## Does s19 confirm or reject s18?
**PARTIAL/NUANCED:** corroborates the s18 EDGE's generalization; does NOT yield a 2nd OOS_CONFIRMED candidate (the s19 candidate is K9-terminal at OOS). Edge replicates; candidate does not clear the sample gate. **Not a rejection** of the s18 edge.

## Honest caveats
DIAGNOSTIC_ONLY / NOT live-ready; an edge present but thin-sample at OOS is unverifiable at the K9 floor (s17 lesson recurring); single replication; projections != measured counts. No tuning to manufacture trades (would be a fresh candidate).

## Status
PAUSED · BLOCKED_AT_6_GATES · FRC NEVER_GRANTED · DIAGNOSTIC_ONLY_NOT_LIVE_GRADE · candidate TERMINAL · C6 16 verbatim · s18 frozen. lessons.md NOT touched this phase.

## Next framework authorization (research-phase only; NO live path by design)
- **Lessons (recommended):** `Authorize s19-d1 P11 lessons.md update only.`
- **Park / Defer.**
