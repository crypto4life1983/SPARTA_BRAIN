# s18-d1 weekly RS rotation — P11 lifecycle decision (sealed; OOS_CONFIRMED_DIAGNOSTIC)

**Authored (UTC):** `2026-05-29T02:27:31.444026Z` · **report_seal:** `7897cb1998303de4d359c2e33e8178eba4eedb4851b8dca293386fb4abb5b0d7` · **run_id:** `PHASE2-S18-D1-WEEKLY-P11-0bd07d8a31c2`
**Verdict: `OOS_CONFIRMED_DIAGNOSTIC`** — lifecycle COMPLETE (not terminal-by-failure). **First candidate in the s12->s18 line to clear the full gated ladder** (P6 IS + P6.5 + P6.7 K13 + P10 OOS).

## Full arc
- P6 IS (`3911970`): READY — exp +$370.2776/trade, 229 trades.
- P6.5 (`1db075d`): PASS_COST_STRESS_ELIGIBLE (S0-S4 positive).
- P6.7 K13 (`aa762f0`): K13_PASS marginal 3/5 (F5 2024-25 NEGATIVE).
- P10 OOS (`522df8d`): **OOS_CONFIRMED_DIAGNOSTIC** — 117 trades (58.7/y), net +$39,785.68, exp +$210.4281/trade, sharpe +0.125359, maxDD 22.5951%, +39.7857%; DR4 did NOT fire.

## Honest caveats (load-bearing)
- **DIAGNOSTIC_ONLY / NOT live-ready** — 6-gate live-block + FRC-never-granted apply regardless. No promotion.
- OOS edge **thinner** than IS (exp +$210 vs +$370; sharpe +0.125 vs +0.187).
- **Within-OOS fragility:** K13 F5 (late-2024..2025) was negative; the contiguous-OOS positive is driven by strong early-2024. Recent sub-period was weak.
- K13 was a marginal 3/5; single OOS window, single universe; weekly is cost-heaviest.

## Disposition
CONFIRMED_DIAGNOSTIC, lifecycle complete. Catalogued as the line's strongest diagnostic result; **NOT promoted** (framework provides no live path; FRC NEVER_GRANTED).

## Next framework authorization (research-phase only; NO live-promotion phrase exists by design)
- **Lessons (recommended):** `Authorize s18-d1 weekly relative-strength rotation P11 lessons.md update only.`
- **Robustness replication (fresh candidate):** `Authorize next research-track robustness-replication selection plan after s18-d1 OOS_CONFIRMED only.`
- Park / Defer.

## Status
PAUSED · BLOCKED_AT_6_GATES · FRC NEVER_GRANTED · DIAGNOSTIC_ONLY_NOT_LIVE_GRADE · C6 15 verbatim. lessons.md NOT touched this phase.
