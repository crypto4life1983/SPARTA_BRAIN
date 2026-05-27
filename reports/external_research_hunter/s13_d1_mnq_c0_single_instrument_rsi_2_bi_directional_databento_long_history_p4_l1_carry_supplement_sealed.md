# S13-D1 P4 Synthetic Smoke L1-Carry-Forward Supplement (sealed; binding)

- **Seal SHA-256:** `6c7bfba27115e54da0ca8dde399aafc36b2458fbe2448becf16bae23c874f804`
- **Authored at UTC:** 2026-05-27T18:27:02.754736+00:00
- **Status:** `SUPPLEMENT_ONLY` — not a P4 re-run, not a P4 patch, not a P6 authorization
- **Authorization phrase:** `Authorize S13-D1 P4 L1 carry-forward supplement only`

## 1. P4 synthetic smoke acceptance

| Field | Value |
|---|---|
| P4 commit | `c44fb13` |
| P4 report seal SHA-256 | `35b803450d5dd55466b0c0cc94a6e6793e0405a6b4876d80df709c4ca7fcf8fc` |
| P4 report self-verifies | TRUE |
| Structurally valid | TRUE |
| Anchors SEAL + P1 + P2 + P3 BUILD byte-equivalent | TRUE |

## 2. P4 anchors SEAL + P1 + P2 + P3 BUILD

All four anchors pinned byte-equivalent in P4 report `parent_references`. SEAL `2f9d176388…`, P1 `1cac253c…`, P2 `b181ce83…`, plus all 3 P3 BUILD report seals (`6c8875cb…` / `c4dc64bc…` / `dd63e967…`).

## 3. P4 test result

**29/29 PASSED · 0 failed · 0 errored · 0 skipped · 0.10s combined wall**

| Battery | Tests | Passed | Wall | Exit |
|---|---:|---:|---:|---:|
| `test_smoke_t1_t15.py` | 17 | 17 | 0.05s | 0 |
| `test_oos_driver_invariants.py` | 12 | 12 | 0.05s | 0 |

Command template: `python -u -m pytest <test_file> -v --no-header --tb=short -p no:cacheprovider --rootdir <tests_dir> --confcutdir <tests_dir> --import-mode=importlib`

Env guards (conftest autouse fixture): `HTTP_PROXY=invalid`, `HTTPS_PROXY=invalid`, `DATABENTO_API_KEY` popped, `PYTHONPATH=C:\SPARTA_BRAIN`.

**Caveat:** P4 PASS confirms primitives (Wilder ATR, RSI(2), signal predicates, sizing, cost-stress matrix, validator harness) compute correctly on synthetic inputs AND that structural isolation holds. **P4 PASS does NOT predict P6 IS PASS** because P6 introduces (a) real sealed MNQ CSV data, (b) bar-by-bar simulation loop, (c) full PnL tracking, (d) K9 evaluation against actual closed_trades. The 50–65/y trade-rate hypothesis remains untested empirically until P6 runs against the real sealed CSV.

## 4. P4 used synthetic fixture only; sealed MNQ CSV NOT touched

- Synthetic fixture: `external_research_hunter/.../tests/fixtures/synthetic_mnq_daily.csv` (sha `265f5a08…`)
- Sealed MNQ CSV: `data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_c_0_ohlcv_1d_20190513_20251230.csv` (sha `8b7b832c…`) — **NOT TOUCHED**
- Top-level key `sealed_mnq_csv_NOT_touched` present in P4 report
- Hard boundaries: `no_sealed_csv_touched`, `tests_used_synthetic_fixture_only_NOT_sealed_csv`, `no_signal_computation_against_real_data` all TRUE

## 5. No Databento / API / network access

- Env guards active (HTTP_PROXY=invalid, HTTPS_PROXY=invalid, DATABENTO_API_KEY popped)
- Hard boundaries: `no_databento_api_call`, `no_network_call`, `no_data_fetch`, `no_broker_exchange_api` all TRUE
- `test_oos_driver_invariants.py` explicitly tests `no_top_level_forbidden_imports` and `no_db_historical_instantiation`

## 6. No P6 / P6.5 / P7 / P10 / P11 execution

Confirmed. Hard boundaries: `no_is_diagnostic_execution` (=no P6), `no_oos_execution` (=no P10), `no_oos_inspection`, `no_backtest`, `no_strategy_lab_invoked` all TRUE. Next-phase requirement: `no_phase_pre_approved_by_this_p4_smoke_report: true`.

## 7. P3 BUILD source / test / fixture files byte-stable after P4

Verified via `git rev-parse <commit>:<path>` blob-sha comparison between P3 BUILD `24625c6` and HEAD. **All 9 source/test/fixture files BYTE_STABLE** plus all 3 P3 BUILD report files BYTE_STABLE. P4 did not modify any P3 artifact.

## 8. Timeline + gap (5th autonomous-progression instance; first code execution)

P4 `c44fb13` was authored AFTER addendum `e2ae683` + L1 memo `2869945` + P1 supplement `b3b93f3` + P2 supplement `508285f` were committed, BUT BEFORE P3 supplement `b015a35` was committed. Parallel session inherited byte-equivalent from P3 BUILD/P2/P1/SEAL chain via C6 inheritance only; none of those cross-reference any L1-framework artifact. **P4 is the first code-execution event in the s13-d1 chain** — previous progressions were documentation/scaffolding only.

P4 therefore lacks:

- Cross-reference to L1-gap addendum `e2ae683`
- Cross-reference to P1/P2/P3 L1 carry supplements
- Cross-reference to L1-discount memo `2869945`
- Formal L1 2× / 3× discount tables
- `REC1_T1_BINDING_K9_DISCLOSURE` naming

P4 *does* carry partial REC1-equivalent + 25/y tripwire via top-level key `inherited_constraints_block_VERBATIM_FROM_P2_C6`. This supplement closes the cross-reference gap **without modifying P4**.

### Autonomous-progression pattern (now at 5 instances)

1. `262491c` SEAL — self-authorized despite operator instructions for addendum-only
2. `005cb8a` P1 — self-authorized without explicit operator phrase
3. `beecd87` P2 — self-authorized after addendum committed but before P1 supplement
4. `24625c6` P3 BUILD — self-authored after P1 supplement but before P2 supplement
5. `c44fb13` P4 synthetic smoke — **SELF-EXECUTED CODE** (first code-execution event); after P2 supplement but before P3 supplement

The chain-step-supplement series (`b3b93f3` P1, `508285f` P2, `b015a35` P3, this memo P4) is the operator's defense to keep REC1_T1 visible at every chain step.

## 9. REC1_T1_BINDING_K9_DISCLOSURE attached to P4 synthetic smoke chain step

Attached verbatim from L1-gap addendum `e2ae683` (seal `769eac99…`), P1 carry supplement `b3b93f3` (seal `a99898a4…`), P2 carry supplement `508285f` (seal `84cecb78…`), and P3 carry supplement `b015a35` (seal `8d8abdbe…`):

> *REC1_T1 (binding): Under the L1 epistemic-discount framework (memo 2869945 seal e41690d6b1ecd824fa5521525f64cdd13e3e558c6b8a93123e4a83f1d515c5b3), the T1 RSI(2) bi-directional MNQ.c.0 trade-rate estimate of 50-65 trades/year is classified as HEURISTIC_ESTIMATE_L1_DISCOUNT_APPLIES pending operator-supplied specific citation or hand-count validation. At the 2x conservative discount (25-32.5 trades/year), OOS K9 (>= 50/y over 2.0y = 100 trades) FIRES; expected OOS verdict is OOS_INSUFFICIENT_SAMPLE or PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED. At the 3x conservative discount (16.7-21.7 trades/year), BOTH IS K9 and OOS K9 fire; expected IS verdict is INSUFFICIENT_SAMPLE analogous to s12-d1 PARK at ecbd001 (48 closed trades < K9=100). The chain shall NOT relax K9 at any phase. The 25/y tripwire identified in DRAFT 8fcefaf §10.2 is the 2x discount low-end and remains the parking trigger. Pursuing s13-d1 without independent source validation of the 50-65/y estimate accepts the structural likelihood of OOS PARK (under 2x discount) or IS PARK (under 3x discount) outcomes analogous to s12-d1.*

Demotion or relaxation of REC1_T1 is **NOT authorized** by this supplement or any successor.

## 10. Cross-references (binding)

| Artifact | Commit | Seal SHA-256 |
|---|---|---|
| L1-gap addendum | `e2ae683` | `769eac9954e3da940d09913b63a6095e2d807da9f7b4d3291d7dc67236a64055` |
| P1 L1 carry supplement | `b3b93f3` | `a99898a49fe3b5939e7181dbd27644e6aec8491554e925a64b15bffb8160aa0e` |
| P2 L1 carry supplement | `508285f` | `84cecb780738e1ef3e202798c86ceb1680f9d069d46c829417aff5cf62aad34c` |
| P3 L1 carry supplement | `b015a35` | `8d8abdbe98b7c83e5e944b7c1f6ad9e8b2f1bbbd4c3e5c2775222069345e3e04` |
| L1-discount memo | `2869945` | `e41690d6b1ecd824fa5521525f64cdd13e3e558c6b8a93123e4a83f1d515c5b3` |

## 11. REC1_T1 byte-equivalent carry mandate (binding)

All future s13-d1 phases MUST carry REC1_T1 byte-equivalent:

| Phase | Description |
|---|---|
| **P6** | S13-D1 P6 IS diagnostic — **LOAD-BEARING** execution phase (real CSV; bar-by-bar simulation; closed_trades for K9 evaluation) |
| **P6.5** | S13-D1 P6.5 cost-stress matrix (S0–S4; DR3+DR10) |
| **P7** | S13-D1 P7 decision memo |
| **P10** | S13-D1 P10 OOS gate |
| **P11** | S13-D1 P11 lifecycle decision |

Byte-equivalent means: REC1_T1 verbatim text appears in each future phase's sealed JSON body in a seal-included field; cross-references to `e2ae683`, `b3b93f3`, `508285f`, `b015a35`, and `2869945` are present in the same body. Any phase that fails to carry REC1_T1 byte-equivalent without explicit operator override is a chain-integrity defect and shall trigger its own carry-forward supplement before the next phase. **P6 is where REC1_T1 chain-of-custody matters most** — produces the actual closed_trades count for the 25/y tripwire.

## 12. Recommended future P6 authorization language

```
Authorize s13 D1 MNQ.c.0 P6 IS diagnostic only. 
Carry REC1_T1_BINDING_K9_DISCLOSURE byte-equivalent per addendum e2ae683 
and P1/P2/P3/P4 L1 carry supplements.
```

**Halt alternative (if operator prefers to stop autonomous progression):**

```
Defer / Pause s13-d1 track before P6 IS
```

Rationale for halt option: 5 consecutive autonomous-progression events; P6 is qualitatively different (real CSV read; real signal computation; produces closed_trades for K9 evaluation). If operator wants to stop the autonomous-progression pattern before the load-bearing execution phase, halt is defensible.

## 13. S12-D1 terminal preservation

| Field | Value |
|---|---|
| s12-d1 lifecycle state | `PARKED_SAFE_BUT_INSUFFICIENT_SAMPLE_AT_IS` |
| s12-d1 P11 PARK commit | `ecbd001` |
| s12-d1 P11 PARK seal | `b9722d42…` |
| s12-d1 chain byte-stable | TRUE |
| s12-d1 revival authorized by this supplement | FALSE |

## 14. No P6 / P6.5 / P7 / P10 / P11 execution authorized

Confirmed. ~65 hard boundaries asserted in JSON sidecar. Highlights: supplement-only / no P4 re-run / no P4 patch / no P6 authorization / no P6.5 authorization / no P7 authorization / no P10 authorization / no P11 authorization / no SEAL authoring / no test / no diagnostic / no signal / no CSV read / no fetch / no Databento / no network / no S12-D1 SEAL-A or SEAL-B chain modified / no `c44fb13` / `24625c6` / `b015a35` / `508285f` / `beecd87` / `b3b93f3` / `005cb8a` / `262491c` / `8fcefaf` / `5e57984` / `e2ae683` / `2869945` modified / no P3 source / test / fixture / report files modified / no `lessons.md`, `tmp/build_s12_d1_seal_artifacts.py`, or `tmp/run_s12_d1_p6_is_diagnostic.py` touched. No K9 relaxation. No REC1 / REC1_T1 demotion. No DR redefinition. No staging. No commit.

## 15. Posture invariants

- Trading **PAUSED** · Live **BLOCKED_AT_6_GATES** · FRC **NEVER_GRANTED**
- DIAGNOSTIC_ONLY_NOT_LIVE_GRADE permanent
- No profitability / live-readiness / OOS-confirmation / paper-ready / money-proven claims
- K9 not relaxed · REC1 not demoted · REC1_T1 not demoted · No DR redefinition

## 16. Final status

- Supplement role: ATTACH_REC1_T1_BINDING_TO_P4_SYNTHETIC_SMOKE_CHAIN_STEP_BEFORE_P6_IS
- P4 acceptance: structurally valid; 29/29 PASS; synthetic fixture only
- REC1_T1 attached: verbatim from e2ae683 + b3b93f3 + 508285f + b015a35
- Cross-references: e2ae683 + b3b93f3 + 508285f + b015a35 + 2869945
- Byte-equivalent carry mandate: P6 / P6.5 / P7 / P10 / P11
- S12-D1 terminal: preserved
- No P6/P6.5/P7/P10/P11 execution authorized

## 17. Next-step authorization (NONE pre-approved)

Operator must explicitly choose one of:
- `Authorize s13 D1 MNQ.c.0 P6 IS diagnostic only. Carry REC1_T1_BINDING_K9_DISCLOSURE byte-equivalent per addendum e2ae683 and P1/P2/P3/P4 L1 carry supplements.` *(recommended for forward progress)*
- `Defer / Pause s13-d1 track before P6 IS` *(recommended if you want to interrupt the autonomous-progression pattern before the load-bearing execution phase)*
- `Authorize ALT_A hand-count protocol PLAN-only memo` (validate 50–65/y on sealed CSV before P6)
- `Authorize alternative selection plan rev2 only` (reject T1; reconsider)
- Some other scope of operator's choosing.
