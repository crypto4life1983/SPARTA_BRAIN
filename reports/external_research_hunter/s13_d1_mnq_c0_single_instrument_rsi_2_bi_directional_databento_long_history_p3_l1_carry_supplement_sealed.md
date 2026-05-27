# S13-D1 P3 BUILD L1-Carry-Forward Supplement (sealed; binding)

- **Seal SHA-256:** `8d8abdbe98b7c83e5e944b7c1f6ad9e8b2f1bbbd4c3e5c2775222069345e3e04`
- **Authored at UTC:** 2026-05-27T18:03:20.820498+00:00
- **Status:** `SUPPLEMENT_ONLY` — not a P3 patch, not a P3 rebuild, not a P4/P6 authorization
- **Authorization phrase:** `Authorize S13-D1 P3 L1 carry-forward supplement only`

## 1. P3 BUILD acceptance

| Field | Value |
|---|---|
| P3 BUILD commit | `24625c6` |
| Files added | 16 (5 source + 5 test scaffold + 6 sealed build reports) |
| Runner build report seal | `6c8875cb791765193f6494183614c2c78e63b1ef9a53d1375a6dc44a235eb4a6` |
| In-sample driver report seal | `c4dc64bce87a6697ed7eeda3606dbe8247f21ad4a0fa3f753363872217f33e0a` |
| Out-of-sample driver report seal | `dd63e967fe70d12df56ac81cb5c85584194bb39a83288da0bd9de62974d092f6` |
| All 3 build reports self-verify | TRUE |
| Structurally valid | TRUE |

## 2. P3 anchors SEAL `262491c` + P1 `005cb8a` + P2 `beecd87`

All three anchors pinned byte-equivalent in P3 runner build report `parent_references` + `main.py` header. Tier-N seal `2f9d176388…`, P1 seal `1cac253c…`, P2 seal `b181ce83…`.

## 3. P3 source import-safe and no execution

- All 5 source files have **only `import datetime` + `import hashlib`** at module top level.
- No module-top-level `open` / `csv` / `pd.read` / `requests` / `httpx` / `urlopen` / `databento` / `db.` calls.
- `in_sample_driver.run_in_sample()` and `out_of_sample_driver.run_out_of_sample()` are **hard-raise stubs** (`raise RuntimeError`). P4/P6 authorization required to lift gates.
- `test_execution_status: NOT_RUN`.
- 33 hard boundaries assert: `no_p4_smoke_execution`, `no_is_diagnostic_execution`, `no_backtest`, `no_signal_computation`, `no_simulator_run`, `no_data_fetch`, `no_databento_api_call`, `no_databento_api_key_access`, `no_network_call`, `no_qc_runtime`, `no_oos_inspection`, and 22 more — all TRUE.

## 4. P3 preserves locked strategy params

| Param | Value | DA source |
|---|---|---|
| `rsi_period` | **2** | LOCKED at PLAN |
| `rsi_long_entry_threshold` | **10** | LOCKED at PLAN |
| `rsi_long_exit_threshold` | **50** | LOCKED at PLAN |
| `rsi_short_entry_threshold` | **90** | LOCKED at PLAN |
| `rsi_short_exit_threshold` | **50** | LOCKED at PLAN |
| `risk_pct_per_trade` | **0.005** | DA3=B (REVISED from 1.0% for DR3 mitigation) |
| `starting_cash_mnq_equivalent` | **200000** | DA4=C (REVISED from $100k for DR10 mitigation) |
| `max_total_units` | **1** | LOCKED at SEAL |
| `pyramid_method` | **NONE** | LOCKED at SEAL |
| `verdict_min_closed_trades` | **100** | K9 INVIOLATE |

## 5. Timeline + gap

P3 BUILD `24625c6` was authored AFTER addendum `e2ae683`, L1 memo `2869945`, and P1 supplement `b3b93f3` were committed, BUT BEFORE P2 supplement `508285f` was committed. Parallel session inherited byte-equivalent from P2/P1/SEAL chain, none of which cross-reference any L1-framework artifact. P3 therefore lacks:

- Cross-reference to L1-gap addendum `e2ae683`
- Cross-reference to P1 L1 carry supplement `b3b93f3`
- Cross-reference to P2 L1 carry supplement `508285f`
- Cross-reference to L1-discount memo `2869945`
- Formal L1 2× / 3× discount tables
- `REC1_T1_BINDING_K9_DISCLOSURE` naming

P3 *does* carry partial REC1-equivalent + 25/y tripwire via C6 inheritance from P2/P1/SEAL. This supplement closes the cross-reference gap **without modifying P3**.

### Autonomous-progression pattern (4th instance)

Parallel session has now auto-authored 4 chain steps without operator-explicit authorization: SEAL `262491c`, P1 `005cb8a`, P2 `beecd87`, P3 BUILD `24625c6`. The chain-step-supplement pattern (`b3b93f3` for P1, `508285f` for P2, this memo for P3) is the operator's defense to keep REC1_T1 visible at every chain step.

## 6. REC1_T1_BINDING_K9_DISCLOSURE attached to P3 BUILD chain step

Attached verbatim from L1-gap addendum `e2ae683` (seal `769eac99…`), P1 carry supplement `b3b93f3` (seal `a99898a4…`), and P2 carry supplement `508285f` (seal `84cecb78…`):

> *REC1_T1 (binding): Under the L1 epistemic-discount framework (memo 2869945 seal e41690d6b1ecd824fa5521525f64cdd13e3e558c6b8a93123e4a83f1d515c5b3), the T1 RSI(2) bi-directional MNQ.c.0 trade-rate estimate of 50-65 trades/year is classified as HEURISTIC_ESTIMATE_L1_DISCOUNT_APPLIES pending operator-supplied specific citation or hand-count validation. At the 2x conservative discount (25-32.5 trades/year), OOS K9 (>= 50/y over 2.0y = 100 trades) FIRES; expected OOS verdict is OOS_INSUFFICIENT_SAMPLE or PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED. At the 3x conservative discount (16.7-21.7 trades/year), BOTH IS K9 and OOS K9 fire; expected IS verdict is INSUFFICIENT_SAMPLE analogous to s12-d1 PARK at ecbd001 (48 closed trades < K9=100). The chain shall NOT relax K9 at any phase. The 25/y tripwire identified in DRAFT 8fcefaf §10.2 is the 2x discount low-end and remains the parking trigger. Pursuing s13-d1 without independent source validation of the 50-65/y estimate accepts the structural likelihood of OOS PARK (under 2x discount) or IS PARK (under 3x discount) outcomes analogous to s12-d1.*

Demotion or relaxation of REC1_T1 is **NOT authorized** by this supplement or any successor.

## 7. Cross-references (binding)

| Artifact | Commit | Seal SHA-256 |
|---|---|---|
| L1-gap addendum | `e2ae683` | `769eac9954e3da940d09913b63a6095e2d807da9f7b4d3291d7dc67236a64055` |
| P1 L1 carry supplement | `b3b93f3` | `a99898a49fe3b5939e7181dbd27644e6aec8491554e925a64b15bffb8160aa0e` |
| P2 L1 carry supplement | `508285f` | `84cecb780738e1ef3e202798c86ceb1680f9d069d46c829417aff5cf62aad34c` |
| L1-discount memo | `2869945` | `e41690d6b1ecd824fa5521525f64cdd13e3e558c6b8a93123e4a83f1d515c5b3` |

## 8. REC1_T1 byte-equivalent carry mandate (binding)

All future s13-d1 phases MUST carry REC1_T1 byte-equivalent:

| Phase | Description |
|---|---|
| **P4** | S13-D1 P4 synthetic smoke (T1–T15 battery against synthetic fixture; no real CSV) |
| **P6** | S13-D1 P6 IS diagnostic (load-bearing: real strategy execution; produces closed_trades for K9 evaluation) |
| **P6.5** | S13-D1 P6.5 cost-stress matrix (S0–S4; DR3+DR10) |
| **P7** | S13-D1 P7 decision memo |
| **P10** | S13-D1 P10 OOS gate |
| **P11** | S13-D1 P11 lifecycle decision |

Byte-equivalent means: REC1_T1 verbatim text appears in each future phase's sealed JSON body in a seal-included field; cross-references to `e2ae683`, `b3b93f3`, `508285f`, and `2869945` are present in the same body. Any phase that fails to carry REC1_T1 byte-equivalent without explicit operator override is a chain-integrity defect and shall trigger its own carry-forward supplement before the next phase. **P6 is the load-bearing execution phase** — produces the actual closed_trades count against which the 25/y tripwire is evaluated.

## 9. Recommended future P4 authorization language

```
Authorize s13 D1 MNQ.c.0 P4 synthetic smoke only. 
Carry REC1_T1_BINDING_K9_DISCLOSURE byte-equivalent per addendum e2ae683 
and P1/P2/P3 L1 carry supplements.
```

**Rationale:** the `only` clause restricts scope; the `Carry REC1_T1…` clause makes the byte-equivalent carry mandate explicit; `P1/P2/P3 L1 carry supplements` phrasing references `b3b93f3`, `508285f`, and this supplement.

## 10. S12-D1 terminal preservation

| Field | Value |
|---|---|
| s12-d1 lifecycle state | `PARKED_SAFE_BUT_INSUFFICIENT_SAMPLE_AT_IS` |
| s12-d1 P11 PARK commit | `ecbd001` |
| s12-d1 P11 PARK seal | `b9722d42…` |
| s12-d1 chain byte-stable | TRUE |
| s12-d1 revival authorized by this supplement | FALSE |

## 11. No P4 / P6 / P6.5 / P7 / P10 / P11 execution authorized

Confirmed. ~60 hard boundaries asserted in JSON sidecar. Highlights: supplement-only / no P3 patch / no P3 rebuild / no P4 authorization / no P6 authorization / no SEAL authoring / no test / no diagnostic / no signal / no CSV read / no fetch / no Databento / no network / no S12-D1 SEAL-A or SEAL-B chain modified / no `24625c6` / `508285f` / `beecd87` / `b3b93f3` / `005cb8a` / `262491c` / `8fcefaf` / `5e57984` / `e2ae683` / `2869945` modified / no P3 source / report / test / fixture files modified / no `lessons.md`, `tmp/build_s12_d1_seal_artifacts.py`, or `tmp/run_s12_d1_p6_is_diagnostic.py` touched. No K9 relaxation. No REC1 / REC1_T1 demotion. No DR redefinition. No staging. No commit.

## 12. Posture invariants

- Trading **PAUSED** · Live **BLOCKED_AT_6_GATES** · FRC **NEVER_GRANTED**
- DIAGNOSTIC_ONLY_NOT_LIVE_GRADE permanent
- No profitability / live-readiness / OOS-confirmation / paper-ready / money-proven claims
- K9 not relaxed · REC1 not demoted · REC1_T1 not demoted · No DR redefinition

## 13. Final status

- Supplement role: ATTACH_REC1_T1_BINDING_TO_P3_BUILD_CHAIN_STEP_BEFORE_P4_OR_P6
- P3 BUILD acceptance: structurally valid
- REC1_T1 attached: verbatim from e2ae683 + b3b93f3 + 508285f
- Cross-references: e2ae683 (`769eac99…`) + b3b93f3 (`a99898a4…`) + 508285f (`84cecb78…`) + 2869945 (`e41690d6…`)
- Byte-equivalent carry mandate: P4 / P6 / P6.5 / P7 / P10 / P11
- S12-D1 terminal: preserved
- No P4/P6/P6.5/P7/P10/P11 execution authorized

## 14. Next-step authorization (NONE pre-approved)

Operator must explicitly choose one of:
- `Authorize s13 D1 MNQ.c.0 P4 synthetic smoke only. Carry REC1_T1_BINDING_K9_DISCLOSURE byte-equivalent per addendum e2ae683 and P1/P2/P3 L1 carry supplements.` *(recommended)*
- `Authorize ALT_A hand-count protocol PLAN-only memo` (validate 50–65/y on sealed CSV before P4/P6)
- `Authorize alternative selection plan rev2 only` (reject T1; reconsider)
- `Defer / Pause trading-bot track` (halt)
- Some other scope of operator's choosing.
