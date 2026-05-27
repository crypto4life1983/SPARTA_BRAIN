# S13-D1 P1 L1-Carry-Forward Supplement (sealed; binding)

- **Seal SHA-256:** `a99898a49fe3b5939e7181dbd27644e6aec8491554e925a64b15bffb8160aa0e`
- **Authored at UTC:** 2026-05-27T17:23:11.233507+00:00
- **Status:** `SUPPLEMENT_ONLY` — not a P1 rewrite, not P1_rev_M, not a P2 authorization
- **Authorization phrase:** `Authorize a short S13-D1 P1 L1 carry-forward supplement only`

## 1. P1 acceptance

| Field | Value |
|---|---|
| P1 commit | `005cb8a` |
| P1 seal SHA-256 | `1cac253cbbbf4cdab87e777edbe0bca00739e925de382bd1d687faae9731052c` |
| Structurally valid | TRUE |
| Self-verifies | TRUE |

## 2. P1 anchors SEAL `262491c`

P1 `parent_references.tier_n_spec_commit = 262491c` + `tier_n_spec_seal_sha256 = 2f9d176388fe0b66c9ced19f33c68e079bb08112f3d52f3f20a9aba7d91bf775` (byte-equivalent to canonical SEAL hash). 7 hits for `262491c` and 4 for `2f9d1763` across P1 body.

## 3. P1 does NOT authorize P2 / P3 / BUILD / execution

All future phases (P2, P3 BUILD, P4, P6, P6.5, P7, P10, P11) require separate operator authorization phrases per P1's own `explicit_next_phase_requirement` block. Hard boundaries `no_phase_pre_approval_beyond_plan_lock`, `no_build`, `no_strategy_build` all TRUE.

## 4. Timeline + gap

P1 `005cb8a` was authored BEFORE the L1-gap addendum `e2ae683`. P1 therefore inherits only the partial REC1-equivalent + 25/y tripwire from SEAL `262491c` (which itself predates the addendum). P1 lacks:

- Cross-reference to L1-gap addendum `e2ae683`
- Cross-reference to L1-discount memo `2869945`
- Formal L1 2× / 3× discount tables
- `REC1_T1_BINDING_K9_DISCLOSURE` naming

This supplement closes the cross-reference gap **without modifying P1**.

## 5. REC1_T1_BINDING_K9_DISCLOSURE attached to P1 chain step

Attached verbatim from L1-gap addendum `e2ae683` (seal `769eac99…`):

> *REC1_T1 (binding): Under the L1 epistemic-discount framework (memo 2869945 seal e41690d6b1ecd824fa5521525f64cdd13e3e558c6b8a93123e4a83f1d515c5b3), the T1 RSI(2) bi-directional MNQ.c.0 trade-rate estimate of 50-65 trades/year is classified as HEURISTIC_ESTIMATE_L1_DISCOUNT_APPLIES pending operator-supplied specific citation or hand-count validation. At the 2x conservative discount (25-32.5 trades/year), OOS K9 (>= 50/y over 2.0y = 100 trades) FIRES; expected OOS verdict is OOS_INSUFFICIENT_SAMPLE or PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED. At the 3x conservative discount (16.7-21.7 trades/year), BOTH IS K9 and OOS K9 fire; expected IS verdict is INSUFFICIENT_SAMPLE analogous to s12-d1 PARK at ecbd001 (48 closed trades < K9=100). The chain shall NOT relax K9 at any phase. The 25/y tripwire identified in DRAFT 8fcefaf §10.2 is the 2x discount low-end and remains the parking trigger. Pursuing s13-d1 without independent source validation of the 50-65/y estimate accepts the structural likelihood of OOS PARK (under 2x discount) or IS PARK (under 3x discount) outcomes analogous to s12-d1.*

Demotion or relaxation of REC1_T1 is **NOT authorized** by this supplement or any successor.

## 6. Cross-references (binding)

| Artifact | Commit | Seal SHA-256 |
|---|---|---|
| L1-gap addendum | `e2ae683` | `769eac9954e3da940d09913b63a6095e2d807da9f7b4d3291d7dc67236a64055` |
| L1-discount memo | `2869945` | `e41690d6b1ecd824fa5521525f64cdd13e3e558c6b8a93123e4a83f1d515c5b3` |

## 7. REC1_T1 byte-equivalent carry mandate (binding)

All future s13-d1 phases MUST carry REC1_T1 byte-equivalent:

| Phase | Description |
|---|---|
| **P2** | S13-D1 P2 phase-2 plan |
| **P3** | S13-D1 P3 BUILD (runner harness + IS/OOS drivers + tests + sealed build reports) |
| **P4** | S13-D1 P4 synthetic smoke |
| **P6** | S13-D1 P6 IS diagnostic |
| **P6.5** | S13-D1 P6.5 cost-stress matrix |
| **P7** | S13-D1 P7 decision memo |
| **P10** | S13-D1 P10 OOS gate |
| **P11** | S13-D1 P11 lifecycle decision |

Byte-equivalent means: REC1_T1 verbatim text appears in each future phase's sealed JSON body in a seal-included field; cross-references to `e2ae683` and `2869945` are present in the same body. Any phase that fails to carry REC1_T1 byte-equivalent without explicit operator override is a chain-integrity defect and shall trigger its own carry-forward supplement before the next phase.

## 8. Recommended future P2 authorization language

```
Authorize s13 D1 MNQ.c.0 P2 phase-2 plan only. 
Carry REC1_T1_BINDING_K9_DISCLOSURE byte-equivalent per addendum e2ae683.
```

**Rationale:** the `only` clause restricts scope to P2; the `Carry REC1_T1…` clause makes the byte-equivalent carry mandate explicit at operator-authorization time, providing an extra-strong signal to any P2-authoring turn (parallel or otherwise) that REC1_T1 must appear in the P2 sealed body.

## 9. S12-D1 terminal preservation

| Field | Value |
|---|---|
| s12-d1 lifecycle state | `PARKED_SAFE_BUT_INSUFFICIENT_SAMPLE_AT_IS` |
| s12-d1 P11 PARK commit | `ecbd001` |
| s12-d1 P11 PARK seal | `b9722d42…` |
| s12-d1 chain byte-stable | TRUE |
| s12-d1 revival authorized by this supplement | FALSE |

## 10. No P2 / P3 / BUILD / execution authorized

Confirmed. ~50 hard boundaries asserted in JSON sidecar. Highlights: supplement-only / no P1 rewrite / no P1_rev_M / no P2 authorization / no P3 BUILD authorization / no SEAL authoring / no test / no diagnostic / no signal / no CSV read / no fetch / no Databento / no network / no S12-D1 SEAL-A or SEAL-B chain modified / no `005cb8a` / `262491c` / `8fcefaf` / `5e57984` / `e2ae683` / `2869945` modified / no `lessons.md`, `tmp/build_s12_d1_seal_artifacts.py`, or `tmp/run_s12_d1_p6_is_diagnostic.py` touched. No K9 relaxation. No REC1 / REC1_T1 demotion. No DR redefinition. No staging. No commit.

## 11. Posture invariants

- Trading **PAUSED** · Live **BLOCKED_AT_6_GATES** · FRC **NEVER_GRANTED**
- DIAGNOSTIC_ONLY_NOT_LIVE_GRADE permanent
- No profitability / live-readiness / OOS-confirmation / paper-ready / money-proven claims
- K9 not relaxed · REC1 not demoted · REC1_T1 not demoted · No DR redefinition

## 12. Final status

- Supplement role: ATTACH_REC1_T1_BINDING_TO_P1_CHAIN_STEP_BEFORE_P2
- P1 acceptance: structurally valid
- REC1_T1 attached: verbatim from e2ae683
- Cross-references: e2ae683 (seal `769eac99…`) + 2869945 (seal `e41690d6…`)
- Byte-equivalent carry mandate: P2 / P3 / P4 / P6 / P6.5 / P7 / P10 / P11
- S12-D1 terminal: preserved
- No P2/P3/BUILD/execution authorized

## 13. Next-step authorization (NONE pre-approved)

Operator must explicitly choose one of:
- `Authorize s13 D1 MNQ.c.0 P2 phase-2 plan only. Carry REC1_T1_BINDING_K9_DISCLOSURE byte-equivalent per addendum e2ae683.` *(recommended)*
- `Authorize ALT_A hand-count protocol PLAN-only memo` (validate 50–65/y on sealed CSV before P2)
- `Authorize alternative selection plan rev2 only` (reject T1; reconsider)
- `Defer / Pause trading-bot track` (halt)
- Some other scope of operator's choosing.
