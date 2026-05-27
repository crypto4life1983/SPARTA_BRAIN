# S13-D1 RSI(2) bi-directional MNQ.c.0 — DRAFT L1-Gap-Closure Addendum (sealed; binding)

- **Seal SHA-256:** `769eac9954e3da940d09913b63a6095e2d807da9f7b4d3291d7dc67236a64055`
- **Authored at UTC:** 2026-05-27T16:58:33.128471+00:00
- **Status:** `ADDENDUM_ONLY` — not a competing DRAFT, not a SEAL
- **Authorization phrase:** `Authorize a short S13-D1 L1-gap-closure addendum only`

## 1. Predecessor acceptance

| Artifact | Commit | Seal (truncated) |
|---|---|---|
| s13-d1 PLAN | `5e57984` | (no seal — markdown PLAN doc) |
| s13-d1 DRAFT | `8fcefaf` | (no seal — markdown DRAFT doc) |
| L1-discount memo | `2869945` | `e41690d6…` |
| s12-d1 P11 PARK (terminal) | `ecbd001` | `b9722d42…` |

S12-D1 terminal state preserved. Canonical SEAL-A harness byte-stable. No s12-d1 revival.

## 2. Addendum role

This addendum **attaches** a binding L1-discount framework + REC1_T1 disclosure to the s13-d1 DRAFT at `8fcefaf`. The DRAFT remains the source of truth for DA1–DA14 and locked-at-PLAN mechanic parameters. This addendum supplements but does NOT supersede or replace it. A future SEAL of s13-d1 shall carry both the DRAFT content AND this addendum's REC1_T1 disclosure byte-equivalent.

**This addendum is NOT a competing DRAFT and NOT a SEAL.**

## 3. Source classification for the T1 ~50–65 trades/year estimate

**Evidence provided in 5e57984 PLAN §9.2:**

- Larry Connors' published RSI(2) research suggesting 50–100 entries/year on liquid equity indices (name-checked; **no specific paper / edition / URL / page reference**)
- Bi-directional symmetric thresholds typically each contribute roughly equally to total trade count
- MNQ.c.0 vol profile is broadly similar to NQ.c.0 (scaled-down notional)

**Source class (per L1-memo taxonomy):** `PARTIAL_PUBLISHED_LITERATURE_WEAKLY_CITED`

**Default classification for this addendum's L1 table purposes:** `HEURISTIC_ESTIMATE_L1_DISCOUNT_APPLIES`

**Operator decision required:** If a specific Connors citation is available (e.g., *Connors & Alvarez, "Short-Term Trading Strategies That Work"*, specific chapter and table), source class upgrades to `PUBLISHED_LITERATURE` and L1 discount drops to 1.5×. Until then, conservative HEURISTIC classification applies and 2×/3× scenarios are binding for the lifecycle decision.

## 4. Formal L1 discount table

K9 floors: IS ≥ **21.74 trades/year** (4.6y window); OOS ≥ **50.00 trades/year** (2.0y window; **binding**).

### 4.1 Central (no L1 discount): 50–65/y

- **Trades/year range:** 50.0 – 57.5 – 65.0

| Position | IS K9 | OOS K9 |
|---|---|---|
| low | 50.0/y vs 21.74/y (margin 2.3x) → **CLEARS_WITH_MARGIN** | 50.0/y vs 50.00/y (margin 1.0x) → **AT_FLOOR_INDETERMINATE** |
| mid | 57.5/y vs 21.74/y (margin 2.645x) → **CLEARS_WITH_MARGIN** | 57.5/y vs 50.00/y (margin 1.15x) → **CLEARS_BORDERLINE** |
| high | 65.0/y vs 21.74/y (margin 2.99x) → **CLEARS_WITH_MARGIN** | 65.0/y vs 50.00/y (margin 1.3x) → **CLEARS_BORDERLINE** |

**Likely terminal risk:** OOS K9 CLEARS_BORDERLINE at low (50.0/y matches floor exactly), CLEARS_BORDERLINE at mid (1.15x), CLEARS_BORDERLINE at high (1.30x). Likely terminal risk: PASS_BUT_THIN_OOS_MARGIN if observed rate matches central estimate; INSUFFICIENT_SAMPLE if observed rate < 50/y.


### 4.2 2× L1 discount: 25–32.5/y

- **Trades/year range:** 25.0 – 28.75 – 32.5

| Position | IS K9 | OOS K9 |
|---|---|---|
| low | 25.0/y vs 21.74/y (margin 1.15x) → **CLEARS_BORDERLINE** | 25.0/y vs 50.00/y (margin 0.5x) → **FAILS** |
| mid | 28.75/y vs 21.74/y (margin 1.322x) → **CLEARS_BORDERLINE** | 28.75/y vs 50.00/y (margin 0.575x) → **FAILS** |
| high | 32.5/y vs 21.74/y (margin 1.495x) → **CLEARS_BORDERLINE** | 32.5/y vs 50.00/y (margin 0.65x) → **FAILS** |

**Likely terminal risk:** OOS K9 FAILS across the entire range (25-32.5/y < 50/y floor). IS K9 clears borderline at high (32.5/y) and mid (28.75/y); fails-borderline at low (25/y < 21.74/y floor only barely clears at 1.15x). Likely terminal risk: INSUFFICIENT_SAMPLE_AT_OOS_K9_FIRED analogous to s12-d1 PARK pattern. PARK is expected terminal outcome.


### 4.3 3× L1 discount: 16.7–21.7/y

- **Trades/year range:** 16.7 – 19.2 – 21.7

| Position | IS K9 | OOS K9 |
|---|---|---|
| low | 16.7/y vs 21.74/y (margin 0.768x) → **FAILS** | 16.7/y vs 50.00/y (margin 0.334x) → **FAILS** |
| mid | 19.2/y vs 21.74/y (margin 0.883x) → **FAILS** | 19.2/y vs 50.00/y (margin 0.384x) → **FAILS** |
| high | 21.7/y vs 21.74/y (margin 0.998x) → **AT_FLOOR_INDETERMINATE** | 21.7/y vs 50.00/y (margin 0.434x) → **FAILS** |

**Likely terminal risk:** OOS K9 FAILS SEVERELY across entire range (16.7-21.7/y vs 50/y floor; 0.33-0.43x). IS K9 FAILS at low (16.7/y < 21.74/y) and mid (19.2/y); marginally clears at high (21.7/y - essentially AT_FLOOR_INDETERMINATE). Likely terminal risk: BOTH IS AND OOS K9 FIRED. PARK at IS without even reaching P10. Direct replication of s12-d1 PARK pattern.

## 5. Explicit 3× discount scenario disclosure

The s13-d1 PLAN/DRAFT do NOT disclose the 3× discount scenario. This addendum makes it **explicit and binding**:

- **IS K9 outcome at 3×:** FAILS at low (16.7/y) and mid (19.2/y); barely AT_FLOOR_INDETERMINATE at high (21.7/y vs 21.74/y floor)
- **OOS K9 outcome at 3×:** FAILS SEVERELY (margins 0.33 / 0.38 / 0.43)
- **Lifecycle implication:** PARK at IS analogous to s12-d1 (INSUFFICIENT_SAMPLE at IS K9 fire), without reaching P10. Direct replication of the s12-d1 PARK pattern.
- **Operator must explicitly accept this risk before sealing s13-d1.**

Structural parallel: s12-d1 PARKed at 48 closed trades (48% of K9 floor). Under 3× L1 mid, s13-d1 would produce ~88 closed trades (88% of K9 floor) — less severe but still K9-failing.

## 6. REC1_T1_BINDING_K9_DISCLOSURE

The DRAFT 8fcefaf's *"REC1-equivalent disclosure"* (§10.2) is hereby **formally renamed** and **reinforced** as **`REC1_T1_BINDING_K9_DISCLOSURE`** with the full L1-discount framework attached:

> *REC1_T1 (binding): Under the L1 epistemic-discount framework (memo 2869945 seal `e41690d6…`), the T1 RSI(2) bi-directional MNQ.c.0 trade-rate estimate of 50–65 trades/year is classified as HEURISTIC_ESTIMATE_L1_DISCOUNT_APPLIES pending operator-supplied specific citation or hand-count validation. At the 2× conservative discount (25–32.5 trades/year), OOS K9 (≥ 50/y over 2.0y = 100 trades) FIRES; expected OOS verdict is OOS_INSUFFICIENT_SAMPLE or PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED. At the 3× conservative discount (16.7–21.7 trades/year), BOTH IS K9 and OOS K9 fire; expected IS verdict is INSUFFICIENT_SAMPLE analogous to s12-d1 PARK at `ecbd001` (48 closed trades < K9=100). The chain shall NOT relax K9 at any phase. The 25/y tripwire identified in DRAFT 8fcefaf §10.2 is the 2× discount low-end and remains the parking trigger. Pursuing s13-d1 without independent source validation of the 50–65/y estimate accepts the structural likelihood of OOS PARK (under 2× discount) or IS PARK (under 3× discount) outcomes analogous to s12-d1.*

**Byte-equivalent carry required through (load-bearing):**

- s13-d1 Tier-N spec SEAL
- Step 02b manifest cross-link
- P1 plan-lock
- P2 phase-2 plan
- P3 BUILD
- P4 synthetic smoke
- P6 IS diagnostic
- P6.5 cost-stress
- P7 decision memo
- P10 OOS gate
- P11 lifecycle decision

REC1_T1 relaxation or demotion to advisory is **NOT authorized**.

## 7. Cross-reference: L1-discount memo `2869945`

- **Commit:** `2869945`
- **Seal SHA-256:** `e41690d6b1ecd824fa5521525f64cdd13e3e558c6b8a93123e4a83f1d515c5b3`
- **JSON:** `reports/external_research_hunter/next_track_selection_plan_revision_l1_discount_memo_sealed.json`
- **MD:** `reports/external_research_hunter/next_track_selection_plan_revision_l1_discount_memo_sealed.md`

Memo lessons applied here: L1 discount factors 2× and 3× · source-class taxonomy (PUBLISHED/HAND-COUNT/HEURISTIC) · REC1_T1 draft template · K9 OOS floor 50/y binding · ALT_A hand-count path remains available.

## 8. Embedded-discount reconciliation

**Issue:** The 5e57984 PLAN §9.2 derives 50–65/y from Connors' ~50–100/y long-only equity-index rate, doubled approximately for bi-directional (→100–200/y), then implicitly reduced to 50–65/y for MNQ futures. The reduction step (100–200/y → 50–65/y) is unacknowledged but corresponds to a ~2–3× cross-instrument extrapolation discount (equity → futures).

**Two possible readings:**

- **READING_A (no embedded discount):** 50–65/y is the raw central; L1 2×/3× are first-application; 25–32.5/y and 16.7–21.7/y are the conservative scenarios. **This addendum's table assumes READING_A.**
- **READING_B (embedded 2–3× already applied):** 50–65/y already silently includes a Connors-to-MNQ discount; further L1 would be a compound 4–6× discount from Connors baseline.

**Resolution required before SEAL.** Operator must explicitly choose READING_A or READING_B and document the choice. Either is defensible; the absence of a documented choice is the gap this addendum surfaces.

**Default for this addendum:** READING_A (more conservative; treats estimate as discount-free).

## 9. S12-D1 terminal preservation

| Field | Value |
|---|---|
| s12-d1 lifecycle state | `PARKED_SAFE_BUT_INSUFFICIENT_SAMPLE_AT_IS` |
| s12-d1 P11 PARK commit | `ecbd001` |
| s12-d1 P11 PARK seal | `b9722d42…` |
| s12-d1 chain byte-stable at HEAD | TRUE |
| s12-d1 revival authorized by this addendum | FALSE |

## 10. No SEAL / BUILD / tests / diagnostics / execution authorized

Confirmed. ~45 hard boundaries asserted in JSON sidecar. Highlights: addendum-only / no code / no build / no tests / no diagnostics / no signal computation / no CSV read / no data fetch / no Databento / no network / no s13-d1 SEAL or any later phase authored / no modification of `5e57984` PLAN / `8fcefaf` DRAFT / `2869945` L1-discount memo / SEAL-A chain / SEAL-B chain / runner harness / drivers / cache / data directory / lessons.md / tmp/ helpers. No K9 relaxation. No REC1 demotion. No DR redefinition. No staging. No commit. No phase pre-approved.

## 11. Posture invariants

- Trading **PAUSED** · Live **BLOCKED_AT_6_GATES** · FRC **NEVER_GRANTED**
- DIAGNOSTIC_ONLY_NOT_LIVE_GRADE permanent
- No profitability / live-readiness / OOS-confirmation / paper-ready / money-proven claims
- K9 not relaxed · REC1 not demoted · No DR redefinition · No threshold loosening

## 12. Final status

- Source class default: `HEURISTIC_ESTIMATE_L1_DISCOUNT_APPLIES`
- Central (no discount): clears OOS K9 borderline (1.00–1.30×)
- 2× L1 discount: **FAILS OOS K9** across entire range
- 3× L1 discount: **FAILS BOTH IS AND OOS K9** (s12-d1 PARK pattern repeats)
- Embedded-discount reading: READING_A or READING_B operator choice required at SEAL
- REC1_T1 carry: byte-equivalent through future SEAL/P1/P2/P3/P4/P6/P6.5/P7/P10/P11
- s12-d1 terminal: preserved

## 13. Next-step authorization (NONE pre-approved)

Operator must choose one of:
- `Authorize s13 D1 MNQ.c.0 Tier-N spec SEAL. Confirm all DRAFT ambiguities as default A. Adopt READING_A. Carry REC1_T1_BINDING_K9_DISCLOSURE byte-equivalent.` (full DRAFT + addendum carried)
- `Authorize ALT_A hand-count protocol PLAN-only memo` (validate 50–65/y on sealed CSV before SEAL)
- `Authorize alternative selection plan rev2 only` (reject T1; reconsider)
- `Defer / Pause trading-bot track` (halt)
- Some other scope of operator's choosing.
