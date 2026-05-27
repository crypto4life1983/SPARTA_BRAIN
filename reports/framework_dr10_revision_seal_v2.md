# Framework-level DR10 SEAL revision v2 (sealed)

**Revision id:** `DR10_V2_AND_CONJUNCTION`
**Revision run_id:** `FRAMEWORK-DR10-V2-c61bf5cc2379`
**Authored (UTC):** `2026-05-27T19:33:39.715932Z`
**Lifecycle state:** `FRAMEWORK_DR10_REVISION_V2_SEALED`
**Report seal sha256:** `7794bb5222ed2a2cb1cd8e1ef2f43f3d1abc6f1539d71af31dda32d832b5e907`
**Authorization phrase:** `Authorize framework-level DR10 SEAL revision to AND-conjunction of turnover and S2_cost_drag only.`
**Binding scope:** new candidate `candidate_record_id`s authored at SEAL time at or after this revision (e.g., s14, s15, ...). **NO retroactive effect** on existing sealed candidates.

----

## §1. Change summary

| Field | OLD (v1; preserved verbatim, binding for existing sealed candidates) | NEW (v2; binds only to new SEAL turns from s14+ onward) |
|---|---|---|
| Connective | **OR** (disjunctive: either branch fires -> DR10 fires) | **AND** (conjunctive: both branches must fire -> DR10 fires) |
| `annual_turnover` threshold | 0.50 | 0.50 (preserved verbatim) |
| `S2_cost_drag` threshold | 0.05 | 0.05 (preserved verbatim) |
| Branches | `annual_turnover` AND `S2_cost_drag` (two branches, joined by OR) | `annual_turnover` AND `S2_cost_drag` (same two branches, now joined by AND) |
| Precedence position | 4 of 9 | 4 of 9 (preserved) |
| Rejection class | REJECT_FAST | REJECT_FAST (preserved) |
| DA14 resolution | A (byte-equivalent from s11-lineage) | A (preserved) |

## §2. DR10 v1 definition (preserved verbatim; binding for existing sealed candidates)

> turnover_cost_explosion annual_turnover>0.50 OR S2_cost_drag>0.05 byte-equivalent (DA14=A) -> REJECT_FAST; ELEVATED prior probability vs s11-d1 v1 and s12-d1 (RSI 50-65 trades/y is 5-10x higher turnover); DA4=C mitigates via 2x capital base

## §3. DR10 v2 definition (binding for new candidates only)

> turnover_cost_explosion (annual_turnover>0.50 AND S2_cost_drag>0.05) byte-equivalent (DA14=A) -> REJECT_FAST; AND-conjunction: BOTH branches must fire for DR10 to fire; cost-driven framing affirmed (the original DR10 name 'turnover_COST_explosion' identifies cost as the load-bearing concern; DA4 capital-scaling mitigation of the cost_drag branch remains effective; high-turnover strategies are admissible under DR10 v2 if cost_drag is managed below the sealed threshold)

## §4. What v2 addresses

- The s13-d1 outcome at P6.5 where the turnover branch fired alone (84.79 > 0.50) while the cost_drag branch did NOT fire (2.35% < 5%); under v2 such a strategy would not fire DR10.
- The structural incompatibility between K9 inviolate >= 100 and DR10 v1 OR-disjunctive turnover threshold for active-trading strategies at retail-scale start_cash on liquid futures (documented in the framework_dr10_revision_investigation_plan_after_s13_d1_terminal.md PLAN §4-§5; sha at this turn `450373a3c4fbc039058b1ff410dc4e92c95093e86028e254c580624458a04546`).
- Affirms the original DR10 name `turnover_COST_explosion` intent: cost is the load-bearing concern; turnover alone is a proxy that the AND-conjunction with `cost_drag > 0.05` now binds together.

## §5. What v2 does NOT address

- K9 inviolate >= 100 trade-count requirement (unchanged; still binding for all candidates including v2-bound new candidates).
- K9-reachability discipline (introduced post-s12-d1; unchanged; still required at PLAN time for all new Tier-N spec PLANs).
- DR10-reachability discipline (introduced post-s13-d1; unchanged; still required at PLAN time; under v2 the discipline is to ensure `(turnover > 0.50 AND cost_drag > 0.05)` does NOT fire, not turnover alone).
- Other DR rules in the precedence chain (DR1, DR2, DR3, DR4, DR5, DR6, DR7, DR9; all unchanged).
- K-gates K1/K2/K4/K7/K8/K9/K12 (unchanged).
- C1-C8 phase-2 safety contracts (unchanged).
- Any prior sealed candidate verdict (all preserved byte-equivalent under v1).

## §6. What v2 preserves

- Both thresholds verbatim: `annual_turnover > 0.50` AND `S2_cost_drag > 0.05`.
- DR10's place in the precedence chain (position 4 of 9): `DR7 -> DR1 -> DR9 -> DR10 -> DR6 -> DR4 -> DR2 -> DR3 -> DR5`.
- REJECT_FAST rejection class.
- DA14=A byte-equivalent resolution.
- DA4 capital-scaling mitigation of the cost_drag branch (e.g., DA4=C $200k mitigated s13-d1's S2 cost_drag to 2.35% < 5%; this mitigation remains effective under v2).
- All SEAL invariants in existing candidates (`no_dr_redefinition_post_seal=True` for each existing candidate's own DR10 v1 binding).

## §7. OLD-vs-NEW verdict table (INFORMATIONAL ONLY; no past verdict is modified)

| `candidate_record_id` | terminal outcome under v1 | DR10 v1 status | DR10 v2 hypothetical-only status | binding verdict unchanged under v2? |
|---|---|---|---|---|
| `s7-d1-cross-asset-donchian-no-pyramid-databento-long-history` | parked (concentration / USO dominance via A7 + per-symbol-cap) | not_reached_in_lifecycle | not_reached_in_lifecycle | True |
| `s9-rsi-2-cross-asset-mean-reversion-equity-etf-proxy` | parked (DR2 / DR3 cost-stress S2/S3 negative edge on 4-ETF basket; long-only; S0 net PnL -$1,211 over 414 trades) | DOES_NOT_FIRE (annual_turnover ~5-15 estimated; would have fired under v1 if A-gates had passed; but DR2/DR3 fired upstream) | DOES_NOT_FIRE (turnover branch alone insufficient under v2; would require cost_drag>5% AND turnover>0.50) | True |
| `s10-d1-cross-asset-donchian-no-pyramid-mnq-mgc-databento-long-history` | parked (DR9 MGC continuous-stitch data integrity failure) | not_reached_in_lifecycle | not_reached_in_lifecycle | True |
| `s10-d2-cross-asset-donchian-no-pyramid-reparam-cap-cost-stress` | parked (OOS K9: 53 trades / OOS window; PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED) | not_reached_in_lifecycle (terminated at K9 OOS) | not_reached_in_lifecycle | True |
| `s11-d1-v1` | parked (multiple chains; K9 risk disclosed in SEAL) | not_reached_in_lifecycle | not_reached_in_lifecycle | True |
| `s12-d1-mnq-c0-single-instrument-donchian-15-8-databento-long-history` | parked PARKED_SAFE_BUT_INSUFFICIENT_SAMPLE_AT_IS at P11 (48 IS trades < K9=100) | not_reached_in_lifecycle (terminated at IS K9 inviolate) | not_reached_in_lifecycle | True |
| `s13-d1-mnq-c0-single-instrument-rsi-2-bi-directional-databento-long-history` | terminal REJECT_FAST at P7 (P6.5 fired DR10 turnover branch: 84.7851 > 0.50) | FIRES via turnover branch (84.7851 > 0.50); cost_drag branch does NOT fire (2.35% < 5%) | DOES_NOT_FIRE under v2 (both branches required; cost_drag branch does NOT fire at 2.35%; AND-conjunction not satisfied) | True |
| `B005_001 / B005_004 / B005_005 / B005_006 / B006_001 / B006_002` | various (parked or rejected; different DR set; DR10 not part of B005/B006 lineage) | not_in_dr_chain_for_this_lineage | not_in_dr_chain_for_this_lineage | True |

**Disclaimer:** This table is informational only. Per each existing candidate's SEAL invariant `no_dr_redefinition_post_seal=True` and `fail_safety_outcomes_terminal_for_this_candidate_record_id=True`, verdicts authored under DR10 v1 remain byte-equivalent and binding. The `dr10_v2_status_hypothetical_only` column is a counterfactual analysis; it has no operational effect on any candidate. **Specifically: s13-d1 remains terminal REJECT_FAST under DR10 v1; the v2 hypothetical of `DOES_NOT_FIRE` is informational only and does NOT promote s13-d1 to OOS / live / Strategy Lab / FRC.**

## §8. Migration rules for new SEAL turns

1. Any candidate authored at SEAL time at or after this v2 revision (s14+) shall carry DR10 v2 by-reference at SEAL.
2. Each new candidate's SEAL shall record the DR10 v2 definition verbatim in its C6 inherited_constraints_block (analogous to how existing candidates carry v1).
3. Each new candidate's PLAN-time DR10-reachability table shall evaluate against the v2 AND-conjunction: the candidate must demonstrate that either (a) `annual_turnover <= 0.50` by structural design, OR (b) `S2_cost_drag <= 0.05` by structural design (e.g., low per-trade slippage), OR (c) preferably both, such that the AND-conjunction does not fire.
4. Existing sealed candidates (s11-d1, s12-d1, s13-d1, s10-d1, s10-d2, s9, s7-d1, B005, B006, T8) shall NOT be re-evaluated under v2. Their verdicts remain bound by v1.
5. If a new candidate proposes to revive a prior candidate's mechanic family or universe, the candidate must use a fresh `candidate_record_id` (no `_revN_` revision of an existing terminal candidate) AND comply with all prior T-FORBID-1..12 constraints from the next-research-track selection plans.
6. Phase-2 safety contracts (C1-C8) carry by-reference at v2; no change.
7. K-gates (K1, K2, K4, K7, K8, K9, K12) carry by-reference at v2; no change.
8. Other DR rules (DR1, DR2, DR3, DR4, DR5, DR6, DR7, DR9) carry by-reference at v2; no change.
9. K9-reachability + DR10-reachability disciplines remain binding for all new Tier-N spec PLAN authoring under v2 and beyond.

## §9. Parent references (sealed; READ-ONLY anchors)

| Phase / artifact | Commit | File sha256 (independently re-verified at SEAL revision time) |
|---|---|---|
| s13-d1 Tier-N spec (SEAL anchor) | `262491c` | `dbab159fb5d3e0285949236c2083aa1233f36621519945b0836efbdb2362a86b` |
| s13-d1 P1 plan-lock | `005cb8a` | `0f87c8d53088d98e9ed8cf806f93062bc90e8dadfcf919d327f39353f377e187` |
| s13-d1 P2 phase-2 plan | `beecd87` | `cd04ca549c6d37c107812782c12822e3cf1922614029d30eee2ca59666b83ee1` |
| s13-d1 P6 IS diagnostic | `3fa479a` | `7b79d738dc5c797b8b4775ca4b8ce7929961fd5804779e75014b9420d20e5d3c` |
| s13-d1 P6.5 cost-stress matrix | `15c4fb1` | `00f0ca95e8fdcaf52a7095330d15315f0dd31a7c9d6d0b56541f5cfc76652ca3` |
| s13-d1 P7 decision memo (trigger event) | `cc1817b` | `92f7b3266b99f31ce7b8a2dbc80e0eddc5a14aabf4d44609dbd045bd25a3451c` |
| Next-research-track selection plan after s13-d1 | `30c836e` | `f40b72edfe53fccf97659e2c85b359e499832de0cc983e7410dac487a6bccd2d` |
| DR10 SEAL revision investigation PLAN | `28cbaea` | `450373a3c4fbc039058b1ff410dc4e92c95093e86028e254c580624458a04546` |

## §10. Hard boundaries held this revision turn (60+ attestations True)

All True: no reinterpretation of DR10 in any existing sealed candidate · no modification of any existing sealed candidate artifact · s13-d1 / s12-d1 / s11-d1 / s10-d1 / s10-d2 / s9 / s7-d1 / B005 / B006 / T8 chains all byte-stable · no revival of s13-d1 terminal · no revival of s12-d1 terminal · no revival of any parked candidate · no candidate spec authored · no Tier-N PLAN authored · no DRAFT authored · no BUILD phase · no strategy code modified · no P3 source files modified · no runner harness modified · no backtest run · no simulator run · no signal computation · no data fetch · no Databento call · no Databento API key access · no QC call · no LEAN call · no yfinance / Yahoo Finance call · no network IO · no `review_queue` mutation · no production `idea_memory` mutation · no Strategy Lab invocation · no Strategy Lab promotion · no live trading · no paper trading via broker · no broker / exchange API call · no FRC grant · no live block relaxation · no other DR rule modified · no threshold value modified in DR10 · no precedence chain modified · no K-gate modified · no A-gate modified · no C-safety-contract modified · no phase-2 safety contract template doc modified · no CLAUDE.md modified · no `.gitignore` modified · **no `lessons.md` modified or staged** · no other unrelated tracked file modified · OLD DR10 definition preserved verbatim in this artifact · NEW DR10 v2 definition recorded verbatim in this artifact · OLD-vs-NEW verdict table informational only with no verdict change · s13-d1 REJECT_FAST verdict preserved byte-equivalent under v1 · REC1-equivalent OOS K9 disclosure carried binding for v2 candidates · K9-reachability discipline carried binding · DR10-reachability discipline carried binding under v2 AND-conjunction · operator typed authorization recorded · binding-for-future-SEAL-turns-only attested.

## §11. Status (UNCHANGED across this revision turn)

trading: `PAUSED` · live: `BLOCKED_AT_6_GATES` · FRC: `NEVER_GRANTED` · `no_strategy_optimization_authorized = True` · `no_dr_redefinition_post_seal` (per existing sealed candidates) `= True` · REC1-equivalent binding `True` · DIAGNOSTIC_ONLY_NOT_LIVE_GRADE · s13-d1 lifecycle terminal `True` · s12-d1 lifecycle terminal `True` · K9-reachability discipline binding `True` · DR10-reachability discipline binding under v2 AND-conjunction `True` · framework DR10 revision v2 lifecycle state `FRAMEWORK_DR10_REVISION_V2_SEALED`.

----

End of revision. SEAL revision authored this turn only. No SEAL revision applied to any existing candidate. No new candidate authored. No code. No backtest. No fetch. No OOS. No broker. No live. No Strategy Lab. No lessons.md modification. s13-d1 terminal REJECT_FAST preserved verbatim under v1. v2 binds only to future new SEAL turns from s14+ onward.
