# Framework discipline revision PLAN — walk-forward / multi-window validation (of LOCKED parameters)

Status: **PLAN_ONLY** (no code, no spec sealed, no framework SEAL written, no data fetched, no backtest, no OOS, no live; the next step is a separate operator authorization to SEAL this framework revision — analogous to the DR10 v2 SEAL at `78cd22e` — or to defer).

Authored: 2026-05-28
Authorization phrase: `Authorize framework walk-forward / multi-window validation discipline revision PLAN only.`
Predecessor framework revision: DR10 v2 AND-conjunction SEAL at `78cd22e` (`reports/framework_dr10_revision_seal_v2.json`). This PLAN proposes the NEXT framework-discipline revision; it does NOT seal it.
Trigger: the post-s16 selection plan (`56ddd4d`) identified a walk-forward / multi-window validation discipline as the highest-leverage response to three terminals (s14/s15 IS-fail; s16 OOS-fail-after-IS-pass). Lessons LESSON_S16_D1_004/005/006 committed at `90afbb8`.

----

## HARD BOUNDARIES (held by this PLAN)

PLAN only. **No framework SEAL written** (the SEAL is a separate authorization). No code/backtest/simulator/signal/fetch/OOS/live. No vendor API / network. No `review_queue`/`idea_memory` mutation. No Strategy Lab / promotion / FRC. **No retroactive application to any existing candidate** (s16/s15/s14/s13/s12 verdicts stand verbatim). **No relaxation of any existing gate** (this ADDS a robustness requirement; it removes nothing). **No `_revN_`/patch/revival of any candidate.** No modification of any existing sealed artifact (incl. `framework_dr10_revision_seal_v2` `78cd22e`, all candidate chains). No `lessons.md` modification or staging. No commit beyond this doc's own authorization. Trading `PAUSED` · Live `BLOCKED_AT_6_GATES` · FRC `NEVER_GRANTED`.

----

## 1. Motivation

s16-d1 passed P6 IS with a positive edge (+$17,129.69) AND survived full P6.5 cost-stress (S0-S4 net-positive), then **failed the single P10 OOS gate** (DR4: OOS −$2,837.19; REJECT_FAST). K9 OOS was satisfied — a genuine generalization failure (LESSON_S16_D1_004). A **single IS/OOS split** can produce a false positive: an edge that fits one in-sample window and one out-of-sample window's idiosyncrasies but does not persist.

The proposed discipline raises the bar from a single IS/OOS split to **persistence across multiple sequential windows**, so a candidate must demonstrate the locked edge generalizes repeatedly — not just once — before it can be called READY.

### 1.1 Honest framing (not a silver bullet)

s16's IS (2019-2023) **already spanned the 2022 bear**, yet the rule still failed 2024-2025. Walk-forward validation would have surfaced this (the locked rule would have failed some folds), **raising the rejection bar** — its expected effect is to **REJECT more candidates**, including possibly all current families. That is the point: avoid promoting non-generalizing edges. This discipline does NOT promise to find a winner; it promises to lower the false-positive rate.

----

## 2. Proposed discipline: walk-forward / multi-window VALIDATION (of LOCKED parameters)

### 2.1 Definition (load-bearing distinction)

**This is walk-forward VALIDATION, NOT walk-forward OPTIMIZATION.** The candidate's parameters remain LOCKED byte-equivalent at SEAL (DA register). Walk-forward here means: **re-evaluate the SAME locked rule across multiple sequential OOS folds** and require the edge to persist. There is **NO per-fold parameter re-fitting / re-optimization** — that would be data-snooping and would violate `no_strategy_optimization_authorized`. This safeguard is INVIOLATE.

### 2.2 Fold scheme (FIXED + pre-committed; proposed defaults, locked at the framework SEAL)

- The candidate's full diagnostic history (e.g., cash-equity 2019-01-02..2025-12-30) is partitioned into a **fixed, pre-committed sequence of contiguous OOS test folds** (proposed: **5 rolling OOS folds**, each preceded by its own indicator-warmup; expanding-or-rolling-window choice locked at SEAL).
- The fold boundaries are **declared at the candidate's PLAN/SEAL time and never searched** (no anchoring folds to known-good periods). The same fold scheme applies to all s17+ candidates of a given asset/frequency class.
- Each fold re-runs the LOCKED rule; per-fold metrics (expectancy, sharpe_proxy, maxdd, closed_trades) are recorded.

### 2.3 New gate: K13 walk-forward persistence

| Field | Proposed (locked at framework SEAL) |
|---|---|
| Gate id | **K13_walk_forward_persistence** |
| Pass condition | the locked edge is positive (expectancy > 0 AND sharpe_proxy > 0 AND no K1/K2 fire) in **≥ a supermajority of OOS folds** (proposed threshold: **≥ ceil(0.6·N)**, e.g., ≥3 of 5) **AND** aggregate-across-folds net is positive **AND** per-fold/aggregate K9 reachability holds |
| Fail verdict | **OOS_NOT_ROBUST → REJECT_FAST** (terminal) — a candidate positive in only a minority of folds is not OOS-robust |
| Precedence | evaluated as a robustness gate; does NOT override existing fail-closed gates (K1/K2/K4/K9/DR chain) — it is ADDITIVE |
| Anti-snoop | fold scheme + threshold fixed pre-evaluation; locked params; no per-fold refit |

### 2.4 Where it sits in the ladder + binding scope

- **Binds s17+ candidates only** (analogous to DR10 v2 binding s14+). Existing/in-flight candidates keep their sealed methodology; their verdicts stand.
- Proposed placement: a new phase **P6.7 walk-forward validation**, sitting AFTER P6.5 cost-stress and BEFORE the final P10 OOS gate. A candidate must clear K13 (P6.7) before P10. (Alternatively the framework SEAL may fold walk-forward INTO the P6/P10 methodology; the exact placement is locked at the SEAL.)
- The existing single P10 OOS gate is RETAINED as the final hold-out (the last fold's forward segment serves as the untouched final OOS, OR P10 remains a separate final hold-out — locked at SEAL).

----

## 3. Anti-overfitting safeguards (INVIOLATE in the eventual SEAL)

1. **Validation, not optimization:** locked params re-evaluated per fold; NO per-fold re-fitting (preserves `no_strategy_optimization_authorized`).
2. **Pre-committed fold scheme:** fold boundaries + count + the K13 threshold are declared before any fold is evaluated and are NOT searched.
3. **No fold-anchoring:** folds are not aligned to known-favorable periods; a uniform scheme per asset/frequency class.
4. **K9 still inviolate per the discipline:** walk-forward does not relax K9; each fold (or the aggregate) must meet K9 reachability.
5. **DR chain unchanged:** DR4 (oos-negative-while-is-positive), DR2/DR3/DR5, DR10 v2 carry; K13 is additive, not a substitute.
6. **No retroactive application:** binds s17+ only; no re-opening s14/s15/s16.

----

## 4. What this revision does NOT change

- DR precedence chain `DR7→DR1→DR9→DR10→DR6→DR4→DR2→DR3→DR5` (unchanged).
- DR10 v2 AND-conjunction (`78cd22e`) — unchanged and carried.
- K-gates K1/K2/K4/K6/K7/K8/K9/K10/K11/K12 — unchanged; K13 is ADDED.
- K9 inviolate (≥100; OOS ≥50/y) — unchanged.
- REC1-equivalent OOS-K9 disclosure — unchanged and binding.
- Phase-2 C1-C8 safety contracts — unchanged.
- All existing candidate verdicts (s14/s15/s16 terminal; s13/s12 terminal) — preserved verbatim; **NOT re-evaluated under this discipline**.
- `no_strategy_optimization_authorized`, `no_dr_redefinition_post_seal` — unchanged (this is a new SEALED discipline, not a post-hoc reinterpretation).

----

## 5. Honest limitations + expected effect

- **Raises the bar; rejects more.** Expected to reject candidates that pass a single IS/OOS split but not multi-fold persistence — including, plausibly, trend/mean-reversion families already tried. That is the intended risk-reduction, not a defect.
- **Not a guarantee of a winner.** §1.1: s16's IS already spanned 2022; walk-forward raises confidence but does not manufacture a generalizing edge where none exists.
- **Costs more compute/phases per candidate** (multiple folds). Mitigated by the simulator-in-tmp pattern and the cheap CSV simulator.
- **Could itself be gamed** if the fold scheme were searched — which is exactly why §3.2 (pre-committed, unsearched fold scheme) is inviolate.

----

## 6. Boundaries held this PLAN turn

| Boundary | Status |
|---|---|
| PLAN only (no framework SEAL; no code/backtest/fetch/OOS) | met |
| No retroactive application to s16/s15/s14/s13/s12 | met |
| No relaxation of any existing gate (K13 is additive) | met |
| No `_revN_`/patch/revival of any candidate | met |
| No modification of any sealed artifact (incl. DR10 v2 78cd22e) | met |
| `lessons.md` not modified | met |
| No data fetch / vendor API / network | met |
| Trading `PAUSED` · Live `BLOCKED_AT_6_GATES` · FRC `NEVER_GRANTED` | met |

----

## 7. Files written this PLAN turn

| File | Purpose |
|---|---|
| `docs/framework_walk_forward_multi_window_validation_discipline_revision_plan.md` | This framework-discipline revision PLAN (PLAN only; no JSON sidecar; no seal — the framework SEAL is a separate authorization, analogous to DR10 v2). |

No other repository file is modified.

----

## 8. Next-step authorization scope

### Seal this framework revision (recommended)
```
Authorize framework walk-forward / multi-window validation discipline revision SEAL only.
```
Seals the discipline (K13 walk-forward persistence gate + fixed fold scheme + anti-snoop safeguards), binding s17+ candidates; analogous to the DR10 v2 SEAL at `78cd22e`. The SEAL would lock the fold count (proposed 5), the K13 threshold (proposed ≥ceil(0.6·N)), and the P6.7 placement.

### Defer
```
Defer / Pause framework walk-forward validation revision at PLAN.
```

### Proceed to a candidate under current rules (NOT recommended before sealing)
A fresh s17 candidate could still be authored under the existing ladder, but it would NOT benefit from the walk-forward filter; sealing the discipline first is the higher-leverage path.

----

## 9. Carried-forward status (UNCHANGED across this PLAN turn)

| Field | Value |
|---|---|
| Trading / Live / FRC | `PAUSED` / `BLOCKED_AT_6_GATES` / `NEVER_GRANTED` |
| `no_strategy_optimization_authorized` | TRUE (and explicitly reinforced: walk-forward is VALIDATION, not optimization) |
| `no_dr_redefinition_post_seal` (existing candidates) | TRUE |
| DR10 v2 (`78cd22e`) | unchanged; binding for s14+ |
| s16/s15/s14/s13/s12 lifecycles terminal | preserved verbatim; NOT re-evaluated |
| LESSON_S14/S15/S16 entries committed | cited as rationale; not modified |
| Proposed K13 binding scope | s17+ (on framework SEAL) |

----

End of PLAN. PLAN-authoring turn only. No framework SEAL. No code/backtest/fetch/OOS/live. **Walk-forward = VALIDATION of LOCKED parameters, NOT optimization** (inviolate). No retroactive application; no existing-gate relaxation; no candidate revival; no sealed-artifact modification; no `lessons.md` modification or staging. Trading remains `PAUSED`. Live `BLOCKED_AT_6_GATES`. FRC `NEVER_GRANTED`.
