# s18-d1 broad-universe weekly relative-strength rotation — Tier-N spec DRAFT (sealed; NOT a Tier-N SEAL)

**Authored (UTC):** `2026-05-29T01:53:06.322577Z` · **report_seal:** `b173382c497a3026ce1409dc484837d87d23866beb821497380b7e1a2829a876`
**Candidate:** `s18-d1-broad-universe-weekly-relative-strength-rotation-24name-large-cap-long-history` · fresh sibling (not s17 _revN_; not a fortnightly rescue). Parent weekly PLAN `aa95e74` (sha `8a9efbeaf7b33947…`).

## Locked weekly design (DA1–DA22)
126-21 RS signal · **weekly (R=5)** · hold **top-8 equal-weight** · long-only · relative-rank exit · $100k · split_only · reuse 24-name DR9 data.

## Pre-SEAL K9 turnover measurement (signal-only, NO P&L, IS-only, OOS hard-excluded)
220 rebalances → **229 closed trades over IS** (1.041 exits/rebalance). Per-fold MEASURED (fully-IS): **F1=68, F2=69, F3=72** (~54–57/y each).

| Gate | basis | value | verdict |
|---|---|---|---|
| K9 aggregate (IS, ≥100) | MEASURED | 229 | **CLEARS** (margin) |
| K13 per-fold (~1.27y) | MEASURED F1/F2/F3 | 68/69/72 (~54–57/y) | **CLEARS** (F4/F5 projected ~58–59) |
| OOS K9 (≥50/y ⇒ ≥100/2y) | PROJECTED (per-fold rate; OOS not read) | ~100–113 (per-fold basis) / ~91 (conservative) | **CLEARS marginally** |
| DR10 v2 | turnover ~10–20×, cost_drag <1% | — | **CLEARS** (cost branch never fires) |

**Pre-SEAL K9 gate verdict: PASS** — weekly clears K9 reachability where the fortnightly sibling was projected short. The stop-before-SEAL K9 condition is NOT triggered.

## Binding caveats
- **Edge NOT inherited** from monthly s17 — weekly is the weakest first-principles edge basis in the ladder; the edge MUST be re-proven at P6 IS (K1/K2).
- **Stop-before-SEAL:** if the edge fails at P6 IS, or K13 shows <3/5 folds positive, or a fuller OOS K9 check at P10 shows <50/y → terminal; NOT rescued by cadence/M tuning (a further change = a fresh candidate). Here K9 passes; the **edge is the remaining open gate**.

## Boundaries
DRAFT only; no SEAL/BUILD/P&L-backtest/OOS-return-inspection/fetch/optimization/cadence-tuning/Strategy-Lab/live/FRC; no revival; no K9/K13/DR10 reinterpretation; no sealed-artifact modification; lessons.md untouched.

## Next
- Commit: `Authorize commit s18-d1 broad-universe weekly relative-strength rotation Tier-N spec DRAFT only.`
- Forward: `Authorize s18-d1 broad-universe weekly relative-strength rotation Tier-N spec SEAL only — bound by DR10 v2 + walk-forward K13.`
