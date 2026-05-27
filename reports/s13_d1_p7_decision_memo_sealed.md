# s13-d1 P7 decision memo (sealed)

**Candidate record id:** `s13-d1-mnq-c0-single-instrument-rsi-2-bi-directional-databento-long-history`
**Phase:** `PHASE2-S13-D1-MNQ-RSI-2-BIDIR` / `P7_DECISION_MEMO`
**Memo run_id:** `PHASE2-S13-D1-P7-232c5155f694`
**Authored (UTC):** `2026-05-27T18:56:09.265022Z`
**Lifecycle state:** `P7_DECISION_MEMO_SEALED_CANDIDATE_TERMINAL`
**Report seal sha256:** `f68dd92b00fd6c08b76a445b54ddab66555f41bd4f1eca6588977f1240de8af8`

## Formalized verdict: **`REJECT_FAST`**

The s13-d1 candidate is REJECT_FAST per the SEAL's canonical DR10 letter, evaluated at P6.5 cost-stress. This memo formalizes the verdict, records the framework reading, and declares the candidate-lifecycle TERMINAL.

## §1. Verdict driver — DR10 turnover_cost_explosion (canonical, binding)

| Field | Value |
|---|---|
| Rule | **DR10** |
| Canonical definition (SEAL) | `annual_turnover>0.50 OR S2_cost_drag>0.05 byte-equivalent (DA14=A) -> REJECT_FAST` |
| Branch fired | **`annual_turnover > 0.50`** |
| Observed S1 `annual_turnover` | **84.7851** (>> 0.50) |
| Threshold | 0.50 |
| Observed S2 `cost_drag` | 2.3467% (does NOT fire; < 5%) |
| Cost-drag branch fires | False |
| Turnover branch fires | True |
| DR10 outcome | **REJECT_FAST** |
| Precedence at SEAL | position 4 of 9 (`DR7 -> DR1 -> DR9 -> DR10 -> DR6 -> DR4 -> DR2 -> DR3 -> DR5`) |
| Mitigation note | DA4=C $200k START_CASH halves per-dollar cost-drag pressure (cost_drag branch mitigated). It does NOT reduce the annual_turnover ratio: contracts scale proportionally with equity, so `total_notional / start_cash` is invariant under capital rescaling. The turnover branch is intrinsic to the RSI(2) bi-directional mechanic family at the observed ~34/y trade rate. |

## §2. Non-drivers recorded for audit

| Rule | P6.5 outcome | Notes |
|---|---|---|
| DR3 (zero_cost_only_survival) | `DOES_NOT_FIRE` | All S1..S4 expectancy > 0 |
| DR5 (cost_stress_tier_flip)   | `DOES_NOT_FIRE` | No positive->negative tier flip |
| DR2 (oos_metrics_degrade_materially) | `DEFERRED_TO_OOS_P10_FOR_CANONICAL_EVALUATION` | Canonical OOS-specific; provisional IS reading does not fire |
| DR4 (oos_negative_while_is_positive) | `NOT_EVALUABLE_AT_P6_5_IS_ONLY; DEFERRED_TO_P10_OOS_GATE` | Canonical OOS-only; not evaluable at P6.5 IS-only |
| K12 (DR2/DR3/DR4/DR5 cost-stress aggregate) | `DOES_NOT_FIRE_AT_P6_5_IS_ONLY` | Binding scope DR3+DR5 strict |

K12 binding-scope evaluation does NOT fire. DR10 fires via **RF1** (rejection-fast criteria #1: any DR rule fires REJECT_FAST), upstream of K-gates and A-gates in the precedence chain.

## §3. Favorable economics — RECORD-ONLY, NOT overriding

Per `LESSON_B006_002_002` (carried byte-equivalent from prior framework lessons): favorable numbers do NOT override a fail-closed verdict by design. The following readings are recorded for the audit trail; they are NOT money-proof, NOT live-ready, NOT promotable.

| Tier | cost_x | slip_x | trades | net_pnl_usd | expectancy_usd | sharpe_proxy | \|maxDD%\| | cost_drag | annual_turnover | edge+ |
|---|---|---|---|---|---|---|---|---|---|---|
| S0 | 0.0 | 0.0 | 159 | $102,795.23 | $646.51 | 0.1237 | 15.2323% | 0.0000% | 88.3634 | YES |
| S1 | 1.0 | 1.0 | 159 | $85,975.59 | $540.73 | 0.1076 | 17.6842% | 1.5614% | 84.7851 | YES |
| S2 | 1.5 | 1.5 | 159 | $87,464.25 | $550.09 | 0.1096 | 17.1550% | 2.3467% | 84.9512 | YES |
| S3 | 2.0 | 2.0 | 159 | $83,206.05 | $523.31 | 0.1046 | 17.6128% | 3.1101% | 84.4207 | YES |
| S4 | 3.0 | 3.0 | 159 | $79,058.33 | $497.22 | 0.1000 | 18.5689% | 4.6305% | 83.7458 | YES |

- **K9 clearance:** 159 IS trades >= 100 inviolate (K9 PASSES at every tier).
- **A-gates:** all 4 pass at every tier (A1 trades>=100, A2 sharpe_proxy>0, A3 expectancy>0, A4 |maxdd|<=50%).
- **No DR3 zero-cost-only survival.** **No DR5 tier flip.** Edge stays positive at every tier including S4 (cost_x=3.0).
- **S0->S4 degradation:** sharpe_proxy 19.1593% / expectancy 23.0917% (well under the 50% provisional DR2 threshold).

These readings are recorded but do not change the verdict. DR precedence is upstream.

## §4. Framework reading

**What this outcome demonstrates:**

1. DR10's `annual_turnover > 0.50` branch is structurally hostile to RSI(2) bi-directional and any similar high-frequency mean-reversion family, at any practical capital base, because the turnover ratio is invariant under proportional capital+contract scaling.
2. DA4=C $200k mitigates the **cost_drag** branch of DR10 (S2 cost_drag 2.35% < 5%, as the SEAL intended), but the OR-disjunctive DR10 means a mitigated cost_drag branch does not prevent firing when the turnover branch is satisfied.
3. The SEAL anticipated this: it labeled DR10 as ELEVATED prior probability for the RSI 50-65 trades/y family. The P6.5 result confirms the prior; the SEAL was correctly calibrated.
4. Per SEAL `no_dr_redefinition_post_seal=True`: the DR10 turnover threshold cannot be reinterpreted or relaxed post-SEAL. Treating positive-edge economics or K9 clearance as overriding a fail-closed DR is exactly the failure mode that `LESSON_B006_002_002` captured.
5. K9 trade-count clearance and positive A-gates are necessary-but-not-sufficient for OOS progression: an upstream DR rule firing terminates the lifecycle at P7 ahead of K-gate / A-gate consideration.

**What this outcome does NOT demonstrate:**

1. The strategy lost money on IS — it did not; net PnL is positive at every cost-stress tier (S4 still nets $79,058 on $200k starting cash).
2. OOS K9 would have fired — REC1-equivalent indicated OOS K9 was reachable at lower bound; the candidate did not reach P10 so the OOS K9 question is unanswered (and remains unanswered per this memo).
3. The SEAL was wrong — the SEAL explicitly anticipated DR10 was ELEVATED for this family and applied DA4=C mitigation specifically to the cost_drag branch.
4. RSI(2) is fundamentally non-viable — under THIS framework with DR10 as locked, this mechanic family at this trade frequency is structurally rejected. A different framework, a lower trade frequency, or a different mechanic family is required for future investigation.

**Eligible lessons (NOT written to `lessons.md` this turn; require separate authorization):**

- LESSON_S13_D1_001 (eligible): DR10 turnover>0.50 branch is intrinsic to high-frequency RSI(2) bi-directional and analogous mean-reversion families; DA4 capital-base scaling addresses the cost_drag branch but not the turnover branch.
- LESSON_S13_D1_002 (eligible): A REJECT_FAST verdict at P6.5 is binding even when (a) IS K9 clears, (b) all A-gates pass, (c) all cost-stress tiers stay edge-positive, and (d) no other DR fires. DR precedence is upstream of K-gates and A-gates by SEAL design.
- LESSON_S13_D1_003 (eligible): Future high-frequency candidates in this framework must either lower trade frequency below 0.50 annual-turnover (structural redesign, not SEAL relaxation), or propose a framework-level DR10 revision via SEAL revision (NOT a post-SEAL re-interpretation), or accept that the family is structurally rejected.

These three lessons would land in `brain_memory/projects/trading_bot/lessons.md` only under a separate explicit operator authorization. This memo deliberately does NOT modify `lessons.md`.

## §5. Operator decision paths post-P7

| Path | Title | Requires new authorization | Default recommended |
|---|---|---|---|
| **A — Park** | Honor the REJECT_FAST verdict as terminal. No further work on this `candidate_record_id`. Catalog as ARCHIVED. | No | **YES** |
| B — New candidate, lower frequency | Author a NEW SEAL for a candidate that targets `annual_turnover < 0.50` by structural design. NOT a patch on s13-d1. | Yes | — |
| C — Framework-level DR10 revision | Propose a SEAL revision that revises DR10's definition (NOT a post-SEAL re-interpretation within s13-d1). | Yes | — |
| D — Defer / pause | Keep the sealed memo on file; no Path A/B/C action initiated. | No | — |

## §6. Candidate archival state

- **archived**: `True`
- **archival_reason**: REJECT_FAST at P6.5 driven by DR10 turnover_cost_explosion (canonical annual_turnover>0.50 branch)
- **archival_phase**: `P7_DECISION_MEMO`
- **candidate_lifecycle_terminal**: `True`
- **lifecycle_terminal_per_seal_clause**: `fail_safety_outcomes_terminal_for_this_candidate_record_id=True`
- **no_oos_inspection_in_this_lifecycle**: `True`
- **no_live_promotion_in_this_lifecycle**: `True`
- **no_strategy_lab_in_this_lifecycle**: `True`
- **no_frc_grant_in_this_lifecycle**: `True`
- **rec1_equivalent_oos_k9_disclosure_remains_binding_for_future_unrelated_candidates**: `True`

## §7. C6 inherited_constraints_block (carried verbatim from P2; 16 entries)

1. REC1-equivalent (BINDING): OOS K9 reachable at lower bound with thin margin (~50-65 trades/year vs 50/year floor). If observed IS rate falls below 25/year on RSI(2) bi-directional, OOS K9 unreachability becomes structurally probable. The s9 RSI-2 baseline observed 414 trades over long-only 4-ETF window; if MNQ.c.0 bi-directional rate falls below half that proportional rate, OOS K9 fires. If OOS K9 fires, the OOS verdict shall be OOS_INSUFFICIENT_SAMPLE or PARKED_SAFE_BUT_OOS_INDETERMINATE analogous to S10-D2 P11 PARK at 23c7164 and s12-d1 P11 park at ecbd001. The chain shall NOT relax K9 at OOS; the appropriate response is to seal the INSUFFICIENT_SAMPLE / INDETERMINATE verdict and park the candidate. Pursuing s13-d1 accepts the structural possibility of an OOS PARK outcome if the IS rate falls below the DRAFT-estimated 50-65/y band.
2. DA3=B (BINDING): per-trade risk pct = 0.005 (0.5%); REVISED at SEAL from default 1.0% for DR3 mitigation
3. DA4=C (BINDING): START_CASH_USD = 200000 ($200k); REVISED at SEAL from default $100k for DR10 mitigation
4. K9-reachability discipline (NEW framework standard from 0e3f9d4) applied at PLAN+DRAFT+SEAL+P1+P2+P3+P4+P6; binding for all subsequent phases
5. K9_THRESHOLD_INVIOLATE: closed_trades >= 100; no relaxation at any phase
6. Mechanic family F3 RSI(2) bi-directional mean-reversion LOCKED at PLAN
7. RSI thresholds 10/50/90/50 LOCKED at PLAN; modification post-SEAL FORBIDDEN per RF13
8. DR3 risk ELEVATED (RSI lineage s9 falsification precedent); mitigated via DA3=B
9. DR10 risk ELEVATED (high-frequency turnover ~50-65 trades/y); mitigated via DA4=C ($200k START_CASH)
10. Tier-N spec LOCKED byte-equivalent at 262491c
11. P1 plan-lock LOCKED byte-equivalent at 005cb8a
12. s12-d1 terminal park (PARKED_SAFE_BUT_INSUFFICIENT_SAMPLE_AT_IS at ecbd001) preserved unchanged
13. All parallel-session shorter-path sealed artifacts byte-stable; not anchored by this chain
14. Expected terminal verdict if OOS K9 fires: PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED
15. P6 PASS does NOT imply READY_FOR_LONGER_BACKTEST at OOS
16. P6 PASS NEVER implies live-readiness; 6-gate live-block applies regardless of any verdict

## §8. Parent references (READ-ONLY; sealed)

| Phase | Commit | File sha256 (independent re-verify) |
|---|---|---|
| Tier-N SEAL | `262491c` | (per P2 anchor) |
| P1 plan-lock | `005cb8a` | (per P2 anchor) |
| P2 phase-2 plan | `beecd87` | `cd04ca549c6d37c107812782c12822e3cf1922614029d30eee2ca59666b83ee1` |
| P3 BUILD (3 reports) | `24625c6` | (per P6 anchors) |
| P4 smoke | `c44fb13` | (per P6 anchors) |
| **P6 IS diagnostic** | `3fa479a` | `7b79d738dc5c797b8b4775ca4b8ce7929961fd5804779e75014b9420d20e5d3c` |
| **P6.5 cost-stress matrix** | `15c4fb1` | `00f0ca95e8fdcaf52a7095330d15315f0dd31a7c9d6d0b56541f5cfc76652ca3` |
| MNQ.c.0 CSV | (s10-d1 long-history) | `8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e` |

## §9. Hard boundaries held this P7 turn (40 attestations)

All True: no P10 OOS gate · no OOS inspection · no OOS data read · no DR10 modification · no DR redefinition post-SEAL · no turnover threshold reinterpretation · no data fetch · no network · no broker/exchange API · no live or paper-via-broker trading · no Strategy Lab invoked or promoted · no review-queue mutation · no QC runtime · **no `lessons.md` touched** · no s11-d1 / s12-d1 / s13-d1 SEAL+P1+P2+P3+P4+P6+P6.5 modification · no s12-d1 terminal-park revival · no P3 source-file modification · no parallel-session seal-chain modification · no unrelated tracked file modified · no threshold loosening · no K9 relaxation · no REC1-equivalent demotion · no RSI threshold modification · no candidate promotion · no FRC grant · no live-block relaxation · C6 carried verbatim · P6.5 DR10 firing recorded verbatim · candidate lifecycle marked terminal.

## §10. Status

trading: `PAUSED` · live: `BLOCKED_AT_6_GATES` · FRC: `NEVER_GRANTED` · lifecycle: `P7_DECISION_MEMO_SEALED_CANDIDATE_TERMINAL` · REC1-equivalent binding: `True` · DIAGNOSTIC_ONLY_NOT_LIVE_GRADE · candidate_lifecycle_terminal: `True`
