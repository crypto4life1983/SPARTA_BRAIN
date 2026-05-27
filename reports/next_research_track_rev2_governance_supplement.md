# Next-Research-Track Rev2 Governance Supplement

**Supplement ID:** `NEXT_TRACK_REV2_GOV_SUPPLEMENT_V1`
**Schema:** `sparta.next_research_track.rev2_governance_supplement.v1`
**Phase:** `NEXT_RESEARCH_TRACK_REV2_GOVERNANCE_SUPPLEMENT`
**Lifecycle state:** `NEXT_RESEARCH_TRACK_REV2_GOVERNANCE_SUPPLEMENT_SEALED`
**Authored at (UTC):** `2026-05-27T21:05:00.000000+00:00`
**Sealed JSON:** `reports/next_research_track_rev2_governance_supplement.json`
**Report seal sha-256:** `eba24331eeb7a03bb8c6728e2dd36f0b47873ae2345b21ae2abcfc4f74ddb533`

This supplement is INFORMATIONAL AND GOVERNANCE ONLY. It does not modify the
rev2 plan at `ee2bfc1`, the s14-d1 PLAN at `5376de7`, the race recovery memos
at `2b43b0b`, or any sealed candidate / framework artifact. It does not
authorize T1 rev2, T2 rev2, S14-D1 advancement, halt, framework revision,
live activity, FRC grant, or live-block-gate relaxation.

## Parent references

| Anchor | Commit | File / report sha-256 |
|---|---|---|
| Rev2 next-track plan | `ee2bfc1` | md: `11dffb7b66fe8113367ecb9a6a2eb0d852ae1935622d44e8956e7070ad5797c4` |
| Race recovery (4 memos) | `2b43b0b` | 4 files, all preserved byte-stable |
| S14-D1 T1 rev2 PLAN (parallel-authored) | `5376de7` | md: `be53ca7ecbb05ee4e243f15a98bf4e02…` |
| Rev1 next-track plan (superseded) | `30c836e` | md: `f40b72edfe53fccf97659e2c85b359e4…` |
| DR10 v2 SEAL | `78cd22e` | report_seal: `7794bb5222ed2a2cb1cd8e1ef2f43f3d1abc6f1539d71af31dda32d832b5e907` |
| DR10 v2 governance supplement | `fdf9d6e` | report_seal: `953ad6f3b398f86d875ea3bad64087f11a1eaaaf9bd1f1171e9cf336d3b2b4f8` |
| Master reconciliation memo | `1e51680` | report_seal: `e2714c8e379f0391920d890f65c9f4d525971ea5ca5261c6c9756e003aba3349` |
| S13-D1 SEAL | `262491c` | report_seal: `2f9d176388fe0b66c9ced19f33c68e079bb08112f3d52f3f20a9aba7d91bf775` |

## 1. Acceptance of rev2 plan

The rev2 next-research-track selection plan at `ee2bfc1` is accepted as a
**structurally valid PLAN-only artifact under DR10 v2 binding scope**.
Independently audited (read-only); ~30 hard boundaries enumerated and
attested; T-FORBID-1..12 carried verbatim; explicit non-revival
attestations; explicit non-retroactive-v2-application attestation; explicit
no-modification attestation for all existing sealed candidate artifacts;
K9-reachability + DR10-reachability disciplines carried (DR10 updated for
v2 AND-conjunction); 6 tracks scored. Supersedes rev1 at `30c836e`.

## 2. Forensic note: subject/stat mismatch at ee2bfc1 + race recovery at 2b43b0b

**Mismatch:** the commit subject of `ee2bfc1` describes 4 memo files
(`trading_research_session_synthesis.{json,md}` +
`trading_research_next_direction_memo.{json,md}`). The actual git stat shows
**1 file**: the rev2 plan markdown. **Documented index race** between parallel
session staging steps.

**Recovery:** at `2b43b0b`, the 4 memo files were committed separately with
subject *"non-destructive race recovery; commits the 4 memo files whose
staging was lost in the ee2bfc1 race; ee2bfc1 left untouched; no amend; no
revert; no parallel-file modification"*. Recovery method is **clean**:
ee2bfc1 was preserved; no amend; no revert; no parallel-file modification.

**Race pattern count:** this is the 17th documented race pattern in this
session (autonomous-progression with index race). The new rule in section 11
plus `GOV-RULE-FRAMEWORK-REVISION-OPERATOR-PHRASE-V1` (from `fdf9d6e`) are
intended to reduce future occurrences.

**Implication for rev2 plan legitimacy:** the rev2 plan file content is
itself legitimate. The mismatch is at the commit-message level only. The
plan's own line-6 authorization phrase (`Authorize alternative next-track
selection plan rev2 only.`) matches the actual file content; the 4 memo
files described in the commit body were preserved via 2b43b0b.

## 3. Existing candidates governed by DR10 v1; preserved byte-stable

All existing sealed candidates (`s7-D1`, `s9`, `s10-D1`, `s10-D2`,
`s11-D1-v1`, `s12-D1`, `s13-D1` full chain, `B005`, `B006`, `T8 lineage`)
remain governed by DR10 v1. Their sealed verdicts are byte-equivalent and
immutable under the rev2 plan. There is no v1-to-v2 verdict migration; there
is no reinterpretation of DR10 in any existing sealed candidate; there is no
revival of any parked candidate. **S13-D1 REJECT_FAST under DR10 v1 remains
terminal.**

## 4. No execution / build / fetch / diagnostics / promotion authorized

Rev2 plan §8 boundaries (all met): PLAN only · no DRAFT · no SEAL · no
BUILD · no fetch · no strategy code · no backtest · no simulator · no
signal computation · no data fetch · no Databento call · no DATABENTO_API_KEY
access · no network IO · no live trading · no candidate promotion · no
Strategy Lab run · no review_queue mutation · no idea_memory mutation. §10
next-step authorizations are all PLAN-time.

## 5. Parallel S14-D1 / T1 rev2 PLAN at 5376de7 — authorship context

**Fact:** the parallel session authored `5376de7 Add s14-d1 multi-instrument
RSI(2) bi-directional micro-futures basket Tier-N spec PLAN` **after** the
rev2 plan but **without** explicit operator-side selection between T1 rev2
and T2 rev2.

**Race pattern classification:** 18th documented race pattern —
autonomous-progression of a downstream PLAN (s14-d1) before operator-side
selection between co-primary tracks was explicitly typed.

**Operator-side explicit selection status at 5376de7 landing:**
`NO_EXPLICIT_OPERATOR_SIDE_SELECTION_PHRASE_TYPED`.

## 6. Treatment of 5376de7: provisional, not fully ratified

- **Rollback authorized?** NO. Rolling back 5376de7 would unwind
  structurally legitimate PLAN-only work, risk a precedent that
  parallel-session autonomous-progression is reversible by operator-side
  governance supplements, and create churn without integrity benefit (the
  PLAN does not author DRAFT/SEAL/BUILD on its own).
- **Treated as fully operator-ratified?** NO. The structural PLAN is
  legitimate; the *implicit* selection of T1 rev2 over T2 rev2 via the
  autonomous PLAN authoring is NOT ratified.
- **Status:** `PROVISIONAL_NOT_FULLY_RATIFIED` — accepted structurally,
  preserved as committed, but NOT treated as the operator's explicit
  T1-over-T2 selection.
- **Downstream implication:** any subsequent S14-D1 DRAFT/SEAL/BUILD turn
  must require explicit operator-typed selection per section 7 before
  proceeding, regardless of the existence of 5376de7's PLAN.

## 7. Operator selection required before any S14-D1 advancement

**Before any S14-D1 DRAFT/SEAL/BUILD/P4/P6/P6.5/P7/P10/P11 turn proceeds,
the operator must type an explicit selection phrase naming one of:**

| Option | Label | Implication |
|---|---|---|
| **T1 primary** | T1 rev2 micro-futures basket as primary | 5376de7 PLAN is canonical for the chosen track; proceed to DRAFT only after typed authorization phrase. |
| **T2 co-primary or alternative** | T2 rev2 cash-equity basket as co-primary OR as alternative to T1 | 5376de7 PLAN remains valid for T1 path but operator selects T2 (or both as parallel tracks); a new s14-d1 cash-equity PLAN would be authored. |
| **Halt / defer** | T7 rev2 from rev2 plan §5.7 | 5376de7 PLAN remains in repo as PLAN-only artifact; no further phase proceeds. |

Implicit selection via parallel-session autonomous progression **does NOT**
satisfy this requirement.

## 8. T1 rev2 K9 caveat: basket-correlation-conditional, not per-instrument-linear

**Rev2 plan claim:** T1 rev2 K9 IS/OOS = 4 instruments × ~34 trades/y per
instrument = ~136 trades/y portfolio; clears K9 OOS (≥50/y) with strong
margin.

**Structural concern:** MNQ, MES, MYM, M2K are all US equity-index
micro-futures. In normal market regimes their realized return correlations
typically exceed 0.95 (pairwise) and their RSI(2) signal alignment is
strongly correlated. The effective number of independent trading bets across
the 4-instrument basket is structurally **far below 4**. The A7 metric
(`effective_independent_bets` via correlation eigenvalue decomposition) is
the canonical phase-2 measure and was load-bearing in s7-D1's USO
concentration finding.

**Implication:** if effective independent bets is closer to 1.5-2 (typical
for highly correlated equity-index basket), the effective trade count per
year at portfolio level is closer to 51-68 trades/y. This still clears K9 IS
(≥21.74) but the OOS margin vs the ≥50/y floor is reduced to **borderline**
(51-68 vs floor of 50). The "strong margin" claim in rev2 plan §5.1 may be
optimistic.

**Required at SEAL time:**
- A7 `effective_independent_bets` evidence computed on actual historical
  correlations of MNQ/MES/MYM/M2K (not assumed at 4)
- K9 OOS margin recomputed using effective independent bets
- K11-style portfolio-cap aggregation explicitly precommitted at SEAL
- Explicit SEAL-artifact acknowledgment that basket K9 margin is
  **BASKET-CORRELATION-CONDITIONAL**

This supplement does NOT compute correlations; that belongs at SEAL time
under separate operator authorization.

## 9. T1 rev2 DR10 v2 caveat: cost_drag borderline at DA4=B $100k

**Rev2 plan claim:** T1 rev2 DR10 v2 clears via cost_drag branch; S2
cost_drag estimated at ~3-5% at DA4=B $100k start_cash; AND-conjunction does
not fire because cost_drag < 5%.

**Structural concern:** under DR10 v2 AND-conjunction (per `fdf9d6e` and
`78cd22e`), DR10 fires only if **both** turnover > 0.50 **and** cost_drag >
0.05. T1 rev2 turnover at DA4=B is estimated at 30-50 (clearly fires);
therefore the cost_drag branch is the **only load-bearing screen**. If
cost_drag is at 4.7%, a **0.3pp estimation error** in actual MES/MYM/M2K
commission + slippage flips the verdict from CLEARS to REJECT_FAST.
**Calibration-fragility on the load-bearing branch.**

**Required at SEAL time:**
- MES, MYM, M2K actual per-contract commission from broker fee schedule
  (NOT extrapolated from MNQ); precommitted in SEAL artifact
- MES, MYM, M2K actual half-bid-ask slippage measured from sealed CSV
  bar-level data (operator-side data fetch + DR9 audit; separate
  authorization required)
- S2 cost_drag computed from actual MES/MYM/M2K cost model, NOT
  extrapolated from MNQ at scale-by-cash-ratio approximation
- If actual S2 cost_drag at DA4=B comes in above 5%: **DR10 v2 fires under
  AND-conjunction and T1 rev2 is REJECT_FAST at P6.5** (mirroring s13-d1
  under v1 but with the AND mechanism)
- DA4 choice (B at $100k vs alternative larger start_cash) explicitly
  precommitted at SEAL with documented cost_drag estimate

**This supplement does NOT authorize any DR10 v2 threshold modification or
SEAL-time cost relaxation.**

## 10. T1 rev2 vs T2 rev2 comparison

| Dimension | T1 rev2 (micro-futures basket) | T2 rev2 (cash-equity basket) |
|---|---|---|
| Universe | {MNQ, MES, MYM, M2K} | {AAPL, MSFT, NVDA} placeholder |
| Mechanic | RSI(2) bi-directional (s13-d1 mechanic on different universe) | RSI(3) bi-directional (slower) |
| Sizing | DA3=B 0.5% × DA4=B $100k | DA3=B 0.5% × DA4 standard |
| Score (rev2 plan) | 43/60 | 43/60 (tied) |
| K9 status | 9/9 per linear extrapolation — BUT A7 caveat (§8) | 8/8 |
| DR10 v2 status | 7/10 borderline (cost_drag ~4.7% vs 5% — §9) | 9/10 clean (cost_drag << 5%) |
| Data scope friction | Fresh Databento + DR9 audit for MES/MYM/M2K | Fresh daily OHLCV for 3-name basket |
| First-principles burden | Orthogonal universe + DA4 vs s13-d1; same mechanic family | Orthogonal universe (cash equity vs micro-futures); orthogonal cost surface |
| Futures continuity | RICHER (reuses MNQ CSV for 1/4 instruments) | NONE (new equity asset class) |
| Concentration risk | HIGH (4 correlated equity-index micros; A7 eff_indep_bets << 4) | MEDIUM (3-name large-cap tech; first-principles burden vs s9 4-ETF) |
| 5376de7 authored for this track? | YES | NO |

**Summary:** T1 rev2 retains the s13-d1-proven RSI(2) mechanic with richer
futures continuity but carries two technical caveats (K9 basket
extrapolation + DR10 v2 cost_drag borderline). T2 rev2 has stronger DR10 v2
operational robustness and truly orthogonal universe but requires fresh
OHLCV fetch and new equity cost surface calibration. The operator's choice
depends on whether **richer futures continuity (T1)** outweighs **cleaner
DR10 v2 margin (T2)**. **This supplement does NOT make the choice.**

## 11. Future governance rule: co-primary operator selection phrase

**`GOV-RULE-CO-PRIMARY-OPERATOR-SELECTION-PHRASE-V1`:** When a
research-track selection plan (or revision thereof) presents **two or more
co-primary tracks** with comparable scores and asks the operator to choose,
no downstream candidate PLAN/DRAFT/SEAL/BUILD turn shall proceed until the
operator has typed an explicit selection phrase in the operator's own
controller session **naming the chosen track unambiguously**.

Implicit selection via parallel-session autonomous progression (e.g.,
authoring a downstream PLAN for one of the co-primary tracks before
operator-side selection) does NOT satisfy this rule. If a downstream
PLAN/DRAFT/SEAL/BUILD turn has already been autonomously authored prior to
operator selection (as with 5376de7 vs ee2bfc1's two co-primary T1/T2
paths), the autonomous artifact is preserved as PLAN-only without operator
ratification, and a subsequent operator-typed selection phrase + governance
supplement (this artifact) are required before any further phase
advancement.

**Applies to:** research-track selection plans · framework-revision plans ·
candidate selection plans presenting 2+ co-primary options.

**Does not apply to:** selection plans with single recommended path · plans
where only one track passes all gates · autonomously-authored PLAN-only
artifacts that do NOT trigger downstream phase advancement · L1
carry-forward supplements · lifecycle memos · read-only audits.

**Does not apply retroactively to** `5376de7` (preserved as
PROVISIONAL_NOT_FULLY_RATIFIED per §6).

**Complements** `GOV-RULE-FRAMEWORK-REVISION-OPERATOR-PHRASE-V1` from
`fdf9d6e`.

## 12. No T1 / T2 / S14 candidate authorization granted

This supplement does **NOT** authorize T1 rev2 advancement, T2 rev2
advancement, S14-D1 advancement to DRAFT/SEAL/BUILD, candidate authoring,
revival of any parked candidate, framework revision, halt, live activity,
FRC grant, or any of the 6 live-block gate relaxations.

## 13. No DR10 change

DR10 v1 binding for existing candidates remains intact. DR10 v2 binding for
s14+ candidates (per `78cd22e`) remains intact. DR10 v2 governance
supplement (per `fdf9d6e`) remains intact. No threshold modification. No
connective modification. No precedence chain modification.

## 14. Posture invariants

- Trading: **PAUSED**
- Live: **BLOCKED_AT_6_GATES**
- FRC: **NEVER_GRANTED**
- Research grade: **DIAGNOSTIC_ONLY_NOT_LIVE_GRADE**
- K9 inviolacy: **PRESERVED** (≥ 100 closed trades; OOS K9 ≥ 50/y binding)
- K9-reachability discipline: **BINDING**
- DR10-reachability discipline (under v2 AND-conjunction): **BINDING**
- DR10 v1 binding for existing candidates · DR10 v2 binds future s14+ only
- s13-d1 REJECT_FAST: **TERMINAL under DR10 v1**
- All existing sealed candidates: **BYTE-STABLE**
- ee2bfc1 / 2b43b0b / 5376de7 / 78cd22e / fdf9d6e / 1e51680: **BYTE-STABLE**
- Profitability claim: **NONE**
- Live-readiness claim: **NONE**
- OOS-confirmation claim: **NONE**
- Advisory only · Operator-typed authorization required for any action

## Seal

```
report_seal_sha256: eba24331eeb7a03bb8c6728e2dd36f0b47873ae2345b21ae2abcfc4f74ddb533
seal_method:        LESSON_HUNTER_004 canonical roundtrip
```
