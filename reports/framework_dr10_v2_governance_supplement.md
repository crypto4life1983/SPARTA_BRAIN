# Framework-level DR10 v2 Governance Supplement

**Supplement ID:** `DR10_V2_GOV_SUPPLEMENT_V1`
**Schema:** `sparta.framework.dr10_v2_governance_supplement.v1`
**Phase:** `FRAMEWORK_DR10_V2_GOVERNANCE_SUPPLEMENT`
**Lifecycle state:** `FRAMEWORK_DR10_V2_GOVERNANCE_SUPPLEMENT_SEALED`
**Authored at (UTC):** `2026-05-27T20:12:00.000000+00:00`
**Sealed JSON:** `reports/framework_dr10_v2_governance_supplement.json`
**Report seal sha-256:** `953ad6f3b398f86d875ea3bad64087f11a1eaaaf9bd1f1171e9cf336d3b2b4f8`

This supplement is INFORMATIONAL AND GOVERNANCE ONLY. It does not modify the
DR10 v2 SEAL at `78cd22e`, does not change any candidate's terminal verdict,
and does not authorize any new candidate, T1/T6 next-research-track, live
activity, FRC grant, or live-block-gate relaxation.

## Parent references

| Anchor | Commit | File / report sha-256 |
|---|---|---|
| DR10 v2 SEAL revision | `78cd22e` | report_seal: `7794bb5222ed2a2cb1cd8e1ef2f43f3d1abc6f1539d71af31dda32d832b5e907` |
| Master reconciliation memo | `1e51680` | report_seal: `e2714c8e379f0391920d890f65c9f4d525971ea5ca5261c6c9756e003aba3349` |
| DR10 investigation plan | `28cbaea` | md file sha: `450373a3c4fbc039058b1ff410dc4e92c95093e86028e254c580624458a04546` |
| S13-D1 P7 decision memo | `cc1817b` | file: `ec5addcc045e6e1c34c7769459c28212ef475c3a7a363f29769604bfcad98ba0` |
| S13-D1 SEAL | `262491c` | report_seal: `2f9d176388fe0b66c9ced19f33c68e079bb08112f3d52f3f20a9aba7d91bf775` |

## 1. Acceptance of DR10 v2

DR10 v2 SEAL at `78cd22e` is accepted as structurally valid and binding ONLY
for new candidate_record_ids authored at or after the v2 SEAL time
(`s14`, `s15`, `s16`, ...). The v2 SEAL self-verifies under
LESSON_HUNTER_004 canonical recipe; existing sealed candidates remain
byte-stable; old DR10 v1 definition preserved verbatim; new DR10 v2 definition
recorded verbatim; ~60 hard boundaries attested; old-vs-new verdict table is
informational only.

## 2. Existing candidates governed by DR10 v1

All existing sealed candidates (`s7-d1`, `s9`, `s10-d1`, `s10-d2`,
`s11-d1-v1`, `s12-d1`, `s13-d1`, `B005`, `B006`, `T8 lineage`) remain governed
by **DR10 v1 (OR-disjunctive)**. Their sealed verdicts are byte-equivalent and
immutable under v2. There is no v1-to-v2 verdict migration; there is no
reinterpretation of DR10 in any existing sealed candidate.

## 3. S13-D1 terminal preservation

**S13-D1 REJECT_FAST under DR10 v1 remains terminal.** Turnover branch fired
(84.79 > 0.50); cost_drag branch did NOT fire (2.35% < 5%); OR-disjunctive =>
DR10 fired => REJECT_FAST. Per the s13-d1 SEAL's
`no_dr_redefinition_post_seal=True` and
`fail_safety_outcomes_terminal_for_this_candidate_record_id=True`
attestations, the v1 binding for s13-d1 is immutable. DR10 v2 does not
promote s13-d1 to OOS, P10, Strategy Lab, live, or FRC. The s13-d1 P7
decision memo at `cc1817b` remains canonical.

## 4. Strategic intent statement

> The research intent is to discover **retail-scale tradable strategies**
> while preserving **fail-closed discipline**. DR10 v2 is accepted as a
> pragmatic recalibration for future candidates, not as a retroactive rescue
> of any prior candidate and not as permission to ignore cost/turnover risk.

This intent does NOT authorize: live trading, FRC grant, relaxation of any of
the 6 live-block gates, promotion of any terminal candidate, any candidate
authoring, selection of T1/T6/halt, revision of DR10 v2 thresholds, removal
of K9 inviolacy, removal of K9-reachability or DR10-reachability disciplines,
or modification of any C1-C8 safety contract.

## 5. Pragmatic recalibration framing

DR10 v2 is a **pragmatic recalibration** of one rule's logical connective. It
addresses the structural incompatibility between K9 inviolate>=100 closed
trades and DR10 v1 OR-disjunctive turnover threshold for active-trading
strategies at retail-scale start_cash on liquid futures (per master memo
section 7 and investigation plan sections 4-5). It is NOT a rule relaxation,
NOT a rescue of any past candidate, NOT a grant of live permission, and NOT
a disabling of cost or turnover screening.

## 6. Option F documented (old vs new rule)

| Version | Rule | Connective |
|---|---|---|
| DR10 v1 (existing candidates) | `annual_turnover > 0.50 OR S2_cost_drag > 0.05 -> REJECT_FAST` | OR (disjunctive) |
| DR10 v2 (s14+ only) | `annual_turnover > 0.50 AND S2_cost_drag > 0.05 -> REJECT_FAST` | AND (conjunctive) |

Thresholds unchanged. Precedence chain position preserved. Rejection class
preserved (REJECT_FAST). DA14 resolution preserved (A).

## 7. Governance caveat: Option F weakens the raw-turnover-only screen

Option F (OR -> AND) removes the ability of DR10 to fire on raw
annual_turnover alone. A hypothetical future strategy with very high
annual_turnover but cost_drag below the 5% threshold would pass DR10 v2
cleanly, even though it would have REJECT_FAST under DR10 v1. This is a
deliberate weakening and is the principal integrity-trade-off documented in
master reconciliation memo section 8.

Partial compensation exists via **DR5** (cost-stress tier-flip across
S0/S1/S2/S3 cost tiers), but DR5 is not identical to a raw-turnover screen
and does not fire on the raw-turnover branch alone. DR10 v2's effectiveness
depends entirely on the cost_drag 5% threshold being correctly calibrated.

## 8. Option F vs C vs B comparison

| Aspect | Option F (chosen) | Option C (master-memo recommended) | Option B (alternative) |
|---|---|---|---|
| Rule | `turnover>0.50 AND cost_drag>0.05` | `cost_drag>0.05` (drop turnover branch) | `turnover>X (recalibrated) OR cost_drag>0.05` |
| Integrity vs raw turnover | WEAKENS | Honestly drops turnover proxy | Preserves and recalibrates |
| Permissiveness | MOST_PERMISSIVE | MEDIUM | LEAST (if X >= 5) |
| S13-D1 hypothetical | DOES_NOT_FIRE | DOES_NOT_FIRE | depends on X |
| High-turnover/low-cost future strategy | ADMISSIBLE | ADMISSIBLE | REJECT_FAST if turnover > X |
| High-turnover/high-cost future strategy | REJECT_FAST | REJECT_FAST | REJECT_FAST |

**Integrity-preservation ordering:** C > B > F. **Permissiveness ordering:**
B < C < F.

## 9. Why Option F is accepted despite being more permissive

1. **Thresholds unchanged:** `annual_turnover > 0.50` and `S2_cost_drag >
   0.05` preserved verbatim. No calibration debate opened.
2. **Cost remains load-bearing:** under v2 AND, cost is a required condition
   for DR10 to fire. Original name `turnover_COST_explosion` identifies cost
   as primary concern; v2 makes that explicit.
3. **Existing verdicts preserved:** all prior sealed candidates including
   S13-D1 remain governed by DR10 v1. Verdicts byte-equivalent and immutable.
4. **Future candidates still require cost-stress testing:** DR5, S2/S3
   cost-tier evaluations, DA4 capital-scaling, K-gates K1/K2/K4/K7/K8/K9/K12,
   and C1-C8 contracts all remain binding.
5. **No live-readiness implication:** live remains BLOCKED_AT_6_GATES; FRC
   remains NEVER_GRANTED. v2 binds only PLAN/SEAL-time admissibility of new
   s14+ candidates.

Trade-offs acknowledged: Option F is more permissive than C and B for the
high-turnover/low-cost cell; effectiveness depends on cost_drag 5% calibration;
master memo's primary recommendation (C) was not adopted.

## 10. Future framework governance rule

**`GOV-RULE-FRAMEWORK-REVISION-OPERATOR-PHRASE-V1`:** Future framework SEAL
revisions that change any reject-fast condition (any DR rule's definition,
threshold, connective, or rejection class) require BOTH:

(a) explicit operator-typed authorization phrase in the operator's own
controller session, AND

(b) a governance supplement (analogous to this one) documenting strategic
intent, the specific option selected versus alternatives considered,
integrity-preservation ranking, and acceptance reasons.

The governance supplement may be authored in the same turn as the framework
revision or in a follow-up turn, but it must exist before subsequent
framework changes are made.

This rule applies to all DR rules, all K-gates, all C1-C8 contracts, and any
new reject-fast condition introduced at framework level. It does not apply
retroactively to `78cd22e`. It does not apply to candidate-scoped PLAN/SEAL
authoring, L1 carry-forward supplements, lifecycle memos, or read-only audits
(all governed by existing per-candidate workflows).

## 11. No candidate authorized

No candidate, no candidate_record_id, no Tier-N PLAN, no DRAFT, no SEAL, no
P1/P2/P3/P4/P6/P6.5/P7/P10/P11 turn is authorized by this supplement.

## 12. No DR10 v2 rollback or modification

DR10 v2 SEAL at `78cd22e` is preserved as-is. No rollback, no modification,
no competing framework revision, no DR10 re-revision is authorized.

## 13. No T1/T6/halt path selected

The post-s13-d1 next-research-track selection plan at `30c836e` remains
unsettled. T1 RSI MNQ is NOT authorized. T6 alternative is NOT authorized.
The halt path is NOT authorized. Operator-typed authorization phrase remains
required for next-track selection.

## 14. Posture invariants

- Trading: **PAUSED**
- Live: **BLOCKED_AT_6_GATES**
- FRC: **NEVER_GRANTED**
- Research grade: **DIAGNOSTIC_ONLY_NOT_LIVE_GRADE**
- K9 inviolacy: **PRESERVED** (>= 100 closed trades)
- K9-reachability discipline: **BINDING**
- DR10-reachability discipline (under v2 AND-conjunction): **BINDING**
- REC1_T1 binding K9 disclosure: **PRESERVED**
- All existing sealed candidates: **BYTE-STABLE**
- Profitability claim: **NONE**
- Live-readiness claim: **NONE**
- OOS-confirmation claim: **NONE**
- Advisory only · Operator-typed authorization required for any action

## Seal

```
report_seal_sha256: 953ad6f3b398f86d875ea3bad64087f11a1eaaaf9bd1f1171e9cf336d3b2b4f8
seal_method:        LESSON_HUNTER_004 canonical roundtrip
```
