# s7 D1 — Spec Seal & Validation Plan (DRAFT, plan-only)

**Status:** `PLAN_ONLY_NO_EXECUTION`
**Plan id:** `s7-d1-spec-seal-plan-v1`
**Target spec:** `docs/s7_d1_cross_asset_donchian_spec.md`
(committed at SPARTA `b667d15e0447f6ee82d5c8924380d13cc6873ac3`,
2026-05-25)
**Authored:** 2026-05-25
**Predecessor:** `reports/external_research_hunter/s7_next_candidate_selection_after_five_parks.md`
(sealed selection plan, seal `8d8851bc365ef9a6eb7883b24f272d8462cb4bda9c9e725aa46415e1434f9eac`)

> **HARD BOUNDARIES (held by this plan).** Plan only. No implementation.
> No backtest. No Databento call. No QuantConnect call. No data fetch.
> No live trading. No paper bot change. No scheduler change. No
> `obsidian-trade-logger` mutation. No `review_queue.json` mutation.
> D5 not revived. B005_001 not revived. NKE Options Wheel not revived.
> Trading remains `PAUSED`. Live remains `BLOCKED_AT_6_GATES`. FRC
> never granted. No profitability claim.

> **Scope.** This document defines the **process** by which the s7 D1
> spec is sealed and validated. Executing this process is its own
> separately-authorized turn ("SEAL EXECUTION TURN"). Authoring this
> plan does NOT execute the process.

---

## 1 · Exact files to hash

The seal execution turn hashes the following inputs. Each file is hashed
with **sha256** over its byte content. Paths are repo-root-relative.

### 1A · Files to hash inside SPARTA_BRAIN

| # | Path | Role | Expected mode |
|---|---|---|---|
| 1 | `docs/s7_d1_cross_asset_donchian_spec.md` | The spec text being sealed | Read-only |
| 2 | `reports/external_research_hunter/s7_next_candidate_selection_after_five_parks.md` | Direct sealed parent | Byte-stable |
| 3 | `reports/external_research_hunter/s7_next_candidate_selection_after_five_parks.json` | Companion JSON of parent | Byte-stable |
| 4 | `reports/external_research_hunter/s6_multi_market_donchian_no_filter_PARKING_REPORT.md` | s6 parking report (chain anchor) | Byte-stable |
| 5 | `reports/external_research_hunter/s6_multi_market_donchian_no_filter_PARKING_REPORT.json` | Companion JSON | Byte-stable |
| 6 | `reports/external_research_hunter/s6_multi_market_donchian_no_filter_in_sample_decision_memo.md` | s6 in-sample memo | Byte-stable |
| 7 | `reports/external_research_hunter/s6_multi_market_donchian_no_filter_in_sample_decision_memo.json` | Companion JSON | Byte-stable |
| 8 | `reports/external_research_hunter/s6_multi_market_donchian_no_filter_phase2_plan_SEALED.md` | s6 phase-2 plan | Byte-stable |
| 9 | `reports/external_research_hunter/s6_multi_market_donchian_no_filter_phase2_plan_SEALED.json` | Companion JSON | Byte-stable |
| 10 | `reports/external_research_hunter/s6_portfolio_cap_bugfix_report.md` | Cap-bugfix inheritance | Byte-stable |
| 11 | `reports/external_research_hunter/s6_portfolio_cap_bugfix_report.json` | Companion JSON | Byte-stable |
| 12 | `reports/external_research_hunter/s6_multi_market_donchian_no_filter_t1_t15_smoke_pass_report.md` | s6 smoke pass | Byte-stable |
| 13 | `reports/external_research_hunter/s6_multi_market_donchian_no_filter_t1_t15_smoke_pass_report.json` | Companion JSON | Byte-stable |
| 14 | s6 plan-lock MD (path: `reports/external_research_hunter/s6_*plan_lock*.md`) | Plan-lock inheritance | Byte-stable |
| 15 | s6 plan-lock JSON | Companion JSON | Byte-stable |
| 16 | s6 REV1 Tier-N spec MD (path: `reports/external_research_hunter/s6_*tier_n_spec*rev1*.md`) | Parameter inheritance | Byte-stable |
| 17 | s6 REV1 Tier-N spec JSON | Companion JSON | Byte-stable |
| 18 | s6 original Tier-N spec MD | Anchor | Byte-stable |
| 19 | s6 original Tier-N spec JSON | Companion JSON | Byte-stable |
| 20 | s5 parking report MD | Upstream parent | Byte-stable |
| 21 | s5 parking report JSON | Companion JSON | Byte-stable |
| 22 | s5 in-sample decision memo MD | Upstream | Byte-stable |
| 23 | s5 in-sample decision memo JSON | Companion JSON | Byte-stable |
| 24 | s4 turtle parking report MD | Upstream | Byte-stable |
| 25 | s4 turtle parking report JSON | Companion JSON | Byte-stable |
| 26 | s3 MNQ DRB parking report MD | Upstream | Byte-stable |
| 27 | s3 MNQ DRB parking report JSON | Companion JSON | Byte-stable |
| 28 | `docs/phase2_safety_contract_template.md` (or the `external_research_hunter/` location that holds the canonical Phase 2 safety template MD with sha `1812f4854a23e7a148257c88133042ea1e383725f4875e762475260ae3658981`) | Safety template MD | Byte-stable |
| 29 | The Phase 2 safety template JSON twin (sha `695a9fb6e0cb6ae5395d467471f2c55d3d90a7030443ca87e4c1d220335f4a32`) | Safety template JSON | Byte-stable |

### 1B · Files to NOT hash (deliberate exclusions)

| Path / pattern | Why excluded |
|---|---|
| `external_research_hunter/nke_options_wheel_diagnostic_runner_harness/**` | Rejected candidate; inclusion would imply inheritance — none exists |
| `external_research_hunter/b005_001_intraday_etf_momentum_diagnostic_runner/**` | Rejected candidate; not inherited |
| `external_research_hunter/b005_004_stocks_on_the_move_diagnostic_runner/**` | Sibling Hunter Brain candidate; independent chain |
| Any file matching `*s7-ym-only*` or `*ym_only*` or `*ym-only*` | D5 prohibited; presence is itself a fail (§7) |
| `obsidian-trade-logger/**` | External system; not part of SPARTA seal |
| `local_secrets/**` | Secret material; never hashed into a sealed artifact |
| `data/**` | Cache/raw data; not part of the seal scope |
| `logs/**` | Runtime artifacts; not part of the seal scope |
| `__pycache__/**`, `*.pyc`, `.venv/**`, `node_modules/**`, `remotion/**` | Generated; non-source |

### 1C · Hash algorithm and recipe

```
For each file path P listed in §1A:
    bytes  = open(P, "rb").read()
    sha256 = hashlib.sha256(bytes).hexdigest()
    record(P, len(bytes), sha256, file_mtime_utc)
```

No string normalization, no newline conversion, no encoding step.
The sha is taken over raw bytes on disk. The seal execution turn
records all results in `parent_sha_attestation.json` (§8).

---

## 2 · Parent SHA verification procedure

### 2A · Parent sha registry (recorded values to verify against)

From `docs/s7_d1_cross_asset_donchian_spec.md` Appendix and the sealed
selection plan §"Linked sealed parents (BYTE-STABLE at plan init)":

| Parent | Recorded sha256 | Source |
|---|---|---|
| `s7_selection_plan_seal` | `8d8851bc365ef9a6eb7883b24f272d8462cb4bda9c9e725aa46415e1434f9eac` | selection plan self-seal |
| `s6_parking_report` | `f6953c1fb3c334d34572aa7dac29317b4ff412bf3648db62276707ef9de2894a` | selection plan |
| `s6_decision_memo` | `c2489d468a026a940a5e6f02c2243fccb6065dd37aace78a5498c342a68fac11` | selection plan |
| `s6_phase2_plan` | `e9db90cc124058eebf72f950567664bdcc64b8c9070c312dad0e9b335a856493` | selection plan |
| `s6_plan_lock` | `e384e37990ac1c1be9ca7ad2ebdc4dd06fb8c0f3fd2b6cbe8861e52b878d12fd` | selection plan |
| `s6_rev1_tier_n` | `f3c727f627a5ff2c45365da4af51c21effad8bf5d62394bcb4687f5451bff1ee` | selection plan |
| `s6_original_tier_n` | `17c89eb4c379f68f815d6b3dc669debcc63edd5ee069e0aee4e86220b8ba91c0` | s6 parking report parents table |
| `s6_t1_t15_smoke_pass_report` | `96c500a886bb5b8a455243298febdf892c29c92edbdc5b309ba81a2a486378df` | s6 parking report parents table |
| `s6_portfolio_cap_bugfix_report` | `fa232ca1267fe1d8bb0ccd03a816f40e9d2501b2f8f4c1c2e247f1f37797461b` | s6 parking report parents table |
| `s6_patched_in_sample_diagnostic` | `47f8173e3619577de949e1e2f274f891108ba62e80dcee2a85bd643508823518` | s6 parking report |
| `s5_parking_report` | `6c308b42da6854d5dd3f8e8936fb5299666dae3158904bec65ec6458156f234c` | selection plan |
| `s5_decision_memo` | `9ee7981f26340f8ff8710a6e635d5337e5f6a8622fd8b63195db0bb7d9486e29` | selection plan |
| `s4_parking_report` | `8cda3ca644524cd558cc3a1291a869d983a8c5fae9c1d0f15d6e56ba266a1cb4` | selection plan |
| `s3_parking_report` | `1f557888e1212d6ffe0e305ac43308977f618db7473b22c90e407fe805d3f7ad` | selection plan |
| `phase2_safety_template_md` | `1812f4854a23e7a148257c88133042ea1e383725f4875e762475260ae3658981` | selection plan |
| `phase2_safety_template_json` | `695a9fb6e0cb6ae5395d467471f2c55d3d90a7030443ca87e4c1d220335f4a32` | selection plan |

### 2B · Verification procedure

For each row in §2A:

1. Read the on-disk file at the path listed in §1A.
2. Compute sha256 (§1C).
3. Compare against the recorded value above.
4. Append to `parent_sha_attestation.json` (§8) a row with
   `{name, path, recorded_sha, observed_sha, match}`.

`drift_count` = number of rows with `match == False`.

### 2C · Verification timing

- **VT-1.** Computed at the **START** of the seal execution turn,
  immediately after operator authorization. If `drift_count > 0` at
  VT-1 → **seal aborts immediately**; no further steps run; verdict
  `SEAL_FAIL_DRIFT_AT_START` (§7).
- **VT-2.** Computed again at the **END** of the seal execution turn,
  immediately before the new Tier-N spec sha is finalized. If
  `drift_count > 0` at VT-2 → **seal aborts**; the in-progress Tier-N
  draft is discarded (not written); verdict `SEAL_FAIL_DRIFT_AT_END`.
- **VT-3.** Recorded in the sealed Tier-N spec itself: both the VT-1
  and VT-2 snapshots are embedded as `parent_sha_attestation_at_start`
  and `parent_sha_attestation_at_end`. If VT-1 ≠ VT-2 row-by-row →
  abort (provenance broken).

### 2D · Missing-parent handling

If a row in §2A cannot be located on disk:

- Treat as `match = False` with `observed_sha = null`.
- This is `drift_count += 1`; seal aborts.
- Do NOT search for "similar" files; do NOT re-derive paths; do NOT
  glob-substitute. The path is fixed by the recorded chain.

---

## 3 · Spec SHA procedure

### 3A · Spec content sha

```
spec_md_path   = "docs/s7_d1_cross_asset_donchian_spec.md"
spec_md_bytes  = open(spec_md_path, "rb").read()
spec_md_sha256 = hashlib.sha256(spec_md_bytes).hexdigest()
```

The MD file's sha at HEAD `b667d15` is recorded here as the **input
hash** (the seal execution turn re-computes against the on-disk file at
that turn's start to confirm no in-flight edit happened).

### 3B · Tier-N spec JSON

The seal execution turn authors a **JSON twin** at
`reports/external_research_hunter/s7_d1_cross_asset_donchian_tier_n_spec.json`.
This JSON encodes the spec content in machine-readable form (markets,
parameters, cost matrix, K/A gates, validator items, output paths,
inherited shas). Its seal is computed via the LESSON_HUNTER_004
canonical roundtrip:

```python
import hashlib, json

def seal_payload(payload: dict) -> dict:
    # payload must NOT yet contain report_seal_sha256 or seal_method
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )
    sha = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    # roundtrip to guarantee external recompute matches
    roundtripped = json.loads(canonical)
    roundtripped["report_seal_sha256"] = sha
    roundtripped["seal_method"] = (
        "sha256 over json.dumps(obj, sort_keys=True, "
        "separators=(',',':'), ensure_ascii=False, default=str) "
        "EXCLUDING report_seal_sha256 + seal_method"
    )
    return roundtripped
```

The Tier-N spec JSON top-level shape:

```
{
  "schema_id": "sparta.external_research_hunter.s7_d1_cross_asset_donchian_tier_n_spec.v1",
  "schema_status": "SEALED",
  "report_date_utc": "<iso8601-Z>",
  "candidate_record_id": "s7-cross-asset-donchian-no-filter-nq-gc-zn-cl",
  "predecessor_seal_sha256": "8d8851bc...",      # s7 selection plan
  "spec_md_path": "docs/s7_d1_cross_asset_donchian_spec.md",
  "spec_md_sha256": "<sha from §3A>",
  "parent_sha_attestation_at_start": [...],      # §2 VT-1
  "parent_sha_attestation_at_end":   [...],      # §2 VT-2
  "drift_count_at_start": 0,
  "drift_count_at_end":   0,
  "markets":           ["NQ","GC","ZN","CL"],
  "session_rules":     {...},
  "donchian":          {entry_len: 55, exit_len: 20, ...},
  "stop":              {n_multiplier: 2, ...},
  "sizing":            {risk_pct_per_unit: 0.01, max_units_per_market: 4, ...},
  "cost_stress_matrix": {S0,S1,S2,S3,S4 cells...},
  "acceptance_gates":  {A1..A10},
  "rejection_gates":   {K1,K2,K4,K6,K7,K8,K9,K10,K11,K12},
  "validator_items":   [1..16],
  "output_paths":      [...],
  "overfit_indicators":[OI1..OI10],
  "stop_conditions":   [S-STOP-1..S-STOP-10],
  "labels":            ["EXTERNAL_CLAIM_ONLY","NEEDS_VERIFICATION",...],
  "negative_invariants": {...},                  # see §5
  # report_seal_sha256 + seal_method appended by seal_payload()
}
```

### 3C · Tier-N spec MD twin

Authored at
`reports/external_research_hunter/s7_d1_cross_asset_donchian_tier_n_spec.md`,
mirroring the JSON's content in human-readable form, with a final
`Seal block (canonical)` section reproducing `schema_id`,
`report_date_utc`, `report_seal_sha256`, and `seal_method`. The MD
file's own sha256 is the byte-sha of the file; it is NOT computed via
the JSON canonical roundtrip. The MD sha is logged in the JSON as
`spec_md_twin_sha256` for cross-reference.

### 3D · Verification rule

The seal execution turn re-runs the canonical roundtrip on the
authored JSON immediately after authoring and confirms:

```
recomputed_sha == report_seal_sha256_embedded
```

If not equal → seal fails (LESSON_HUNTER_004 violation).

---

## 4 · Plan-lock procedure

The plan-lock is **a separate sealed artifact authored AFTER the
Tier-N spec is sealed**. It locks the BUILD authorization scope. It is
NOT authored in the same turn as the Tier-N spec.

### 4A · Plan-lock inputs

| Input | Source |
|---|---|
| `tier_n_spec_seal_sha256` | The just-sealed Tier-N spec from §3 |
| `tier_n_spec_md_sha256` | The Tier-N spec MD twin sha |
| `parent_sha_attestation` | Re-verified at plan-lock authoring; must match Tier-N's `_at_end` snapshot byte-for-byte |
| `build_scope` | Enumerated list of files the BUILD turn is allowed to create (under `external_research_hunter/s7_d1_cross_asset_donchian_runner_harness/`) |
| `build_scope_invariants` | "No file outside `build_scope` may be created/modified by the BUILD turn"; "no Databento call"; "no QC call"; "no network"; "no live trading"; etc. |
| `phase2_safety_template_inheritance_attestation` | `template_md_sha == 1812f485…8981` AND `template_json_sha == 695a9fb6…4a32` |

### 4B · Plan-lock outputs

| Path | Content |
|---|---|
| `reports/external_research_hunter/s7_d1_cross_asset_donchian_plan_lock.json` | Canonical JSON, sealed via §3B recipe |
| `reports/external_research_hunter/s7_d1_cross_asset_donchian_plan_lock.md` | MD twin |

### 4C · Plan-lock verification rule

The plan-lock execution turn re-verifies §2 parent shas AND the
Tier-N spec sha immediately before sealing. Any drift → plan-lock
abort; no plan-lock file is written.

### 4D · Plan-lock does NOT authorize

- BUILD execution (a separate turn)
- T1-T15 smoke (a separate turn)
- Databento fetch (operator-only, separate turn)
- In-sample run (separate turn)
- OOS inspection (forbidden until in-sample passes K-criteria)
- Live trading (permanently forbidden under current chain)

---

## 5 · Validator requirements

The seal execution turn runs a **validator** before sealing. The
validator checks the 16-item list from `docs/s7_d1_cross_asset_donchian_spec.md`
§16 plus 5 seal-specific items below. All 21 items must pass for
`VALIDATOR_PASS`; any single fail produces `VALIDATOR_FAIL` and seal
fails.

### 5A · Inherited validator items (from spec §16)

V1-V16: spec sha matches; safety template inherited byte-equivalent;
s2-s6 sealed chains byte-stable; no-D5/B005_001/NKE revival; markets ==
['NQ','GC','ZN','CL']; RTH-only filter attested; Donchian 55/20
attested; pyramid max 4 attested; N at trigger bar; portfolio cap uses
unit count; cost stress S0-S4 present; seal roundtrip recompute match;
no OOS inspection in in-sample run; boundaries held.

(See spec §16 for the full enumerations and pass criteria.)

### 5B · Seal-specific validator items (new for the seal turn)

| # | Item | Pass criterion |
|---|---|---|
| V17 | `spec_md_unchanged_during_seal_turn` | sha of `docs/s7_d1_cross_asset_donchian_spec.md` at turn start == sha at turn end |
| V18 | `no_d5_artifact_present_in_repo` | `git ls-files` + on-disk glob for `*s7-ym-only*`, `*ym_only*`, `*ym-only*` returns empty |
| V19 | `no_b005_001_chain_mutated_during_turn` | sha of `b005_001_archival_memo.{md,json}` unchanged across turn |
| V20 | `no_nke_chain_mutated_during_turn` | sha of all NKE sealed artifacts (memos in `external_research_hunter/HUNTER_BRAIN_LESSONS.md` + per-phase memos) unchanged |
| V21 | `no_obsidian_trade_logger_touched_during_turn` | `git -C C:/Users/mahmo/obsidian-trade-logger status --short` row count unchanged from turn start to turn end |

### 5C · Validator output

The validator writes
`reports/external_research_hunter/s7_d1_cross_asset_donchian_validator_run.{md,json}`
with per-item pass/fail and overall verdict. This file is NOT itself
sealed; it is a run report. Its sha is referenced in the Tier-N spec
JSON as `validator_run_sha256`.

---

## 6 · What counts as seal pass

A **SEAL_PASS** requires ALL of the following at the end of the seal
execution turn:

1. **V1-V21 all PASS** (§5).
2. **`drift_count_at_start == 0`** (§2 VT-1).
3. **`drift_count_at_end == 0`** (§2 VT-2).
4. **`parent_sha_attestation_at_start == parent_sha_attestation_at_end`**
   row-by-row.
5. **`spec_md_sha256` recomputable** from `docs/s7_d1_cross_asset_donchian_spec.md`
   on disk at turn end (equal to value at turn start).
6. **Tier-N spec JSON canonical roundtrip MATCHES** (§3D).
7. **`s7_d1_cross_asset_donchian_tier_n_spec.{md,json}`** files exist on
   disk with sizes and shas recorded in the validator output.
8. **No file outside the sealed-output set was created or modified**:
   the only new files are the Tier-N spec JSON+MD and the validator
   run JSON+MD (4 files total). No other on-disk path changed sha.
9. **No `obsidian-trade-logger` change**: `git -C C:/Users/mahmo/obsidian-trade-logger status --short`
   row count and content unchanged.
10. **No `review_queue.json` mutation** (in either repo).
11. **No network call observed** in the turn log.
12. **No Databento, QC, broker, exchange API call** observed.
13. **No D5 artifact created** anywhere in the repo.
14. **No B005_001, NKE, or other rejected-candidate revival**.
15. **No live or paper trading code modified**.
16. **No scheduler, config, or watchdog file modified**.

A pass results in:

- `s7_d1_cross_asset_donchian_tier_n_spec.{md,json}` sealed and recorded.
- `s7_d1_cross_asset_donchian_validator_run.{md,json}` recorded.
- Status fields advance from `DRAFT_SPEC_ONLY` (current) to
  `TIER_N_SPEC_SEALED` (next).
- The next-step gate (§9) becomes eligible for operator authorization.

A pass does NOT authorize BUILD, fetch, or run.

---

## 7 · What counts as seal fail

ANY of the following triggers `SEAL_FAIL` and immediately stops the
seal execution turn (the Tier-N spec is NOT written, OR if partially
written is REMOVED so no half-sealed artifact is left behind):

| Fail code | Trigger |
|---|---|
| `SEAL_FAIL_DRIFT_AT_START` | `drift_count_at_start > 0` (any parent sha mismatch at turn start) |
| `SEAL_FAIL_DRIFT_AT_END` | `drift_count_at_end > 0` (parent sha changed during turn) |
| `SEAL_FAIL_DRIFT_DURING_TURN` | VT-1 ≠ VT-2 row-by-row |
| `SEAL_FAIL_SPEC_MD_CHANGED` | `docs/s7_d1_cross_asset_donchian_spec.md` sha at turn end ≠ turn start (V17) |
| `SEAL_FAIL_VALIDATOR` | Any of V1-V21 fails |
| `SEAL_FAIL_ROUNDTRIP` | Tier-N spec JSON recompute ≠ embedded seal (LESSON_HUNTER_004) |
| `SEAL_FAIL_D5_REVIVED` | Any D5 artifact found in repo (V18) |
| `SEAL_FAIL_REJECTED_REVIVED` | B005_001 or NKE chain mutated (V19/V20) |
| `SEAL_FAIL_OBSIDIAN_TOUCHED` | `obsidian-trade-logger` status changed during turn (V21) |
| `SEAL_FAIL_OUT_OF_SCOPE_WRITE` | A file outside the 4-file sealed-output set was created/modified |
| `SEAL_FAIL_NETWORK` | Any network call observed (Databento, QC, broker, web) |
| `SEAL_FAIL_REVIEW_QUEUE_MUTATED` | `review_queue.json` modified in either repo |
| `SEAL_FAIL_LIVE_CODE_TOUCHED` | Any execution / strategy / scheduler / watchdog / config file modified |
| `SEAL_FAIL_OPERATOR_STOP` | Operator issues `STOP_S7_D1_SEAL` |
| `SEAL_FAIL_PROVENANCE_BROKEN` | Any condition that makes the chain non-byte-reproducible (e.g., `default=str` removed from seal recipe; canonical separators changed) |

On fail:

- A `seal_fail_report.{md,json}` is authored under
  `reports/external_research_hunter/s7_d1_cross_asset_donchian_seal_fail_report_<UTC>.{md,json}`
  recording the fail code, the observed vs recorded values, and the
  list of remediation steps.
- The candidate status stays at `DRAFT_SPEC_ONLY`.
- No retry happens within the same turn; operator must explicitly
  re-authorize after addressing the failure.

---

## 8 · Required output artifacts (seal turn)

On `SEAL_PASS` the seal execution turn produces exactly these files,
no more, no less:

| # | Path | Type | Sealed via |
|---|---|---|---|
| 1 | `reports/external_research_hunter/s7_d1_cross_asset_donchian_tier_n_spec.json` | JSON | LESSON_HUNTER_004 canonical roundtrip |
| 2 | `reports/external_research_hunter/s7_d1_cross_asset_donchian_tier_n_spec.md` | MD | Companion; byte-sha logged in JSON |
| 3 | `reports/external_research_hunter/s7_d1_cross_asset_donchian_validator_run.json` | JSON | Plain (run report, not a sealed-chain artifact); sha logged in Tier-N JSON |
| 4 | `reports/external_research_hunter/s7_d1_cross_asset_donchian_validator_run.md` | MD | Companion |

A side-effect file (write-once) for parent verification:

| # | Path | Type |
|---|---|---|
| 5 | `reports/external_research_hunter/s7_d1_cross_asset_donchian_parent_sha_attestation.json` | JSON; not sealed; embedded as `parent_sha_attestation_at_{start,end}` in the Tier-N JSON for record-of-record |

On `SEAL_FAIL` the seal execution turn instead produces:

| # | Path | Type |
|---|---|---|
| F1 | `reports/external_research_hunter/s7_d1_cross_asset_donchian_seal_fail_report_<UTC>.json` | JSON; not sealed; records fail code + observations |
| F2 | `reports/external_research_hunter/s7_d1_cross_asset_donchian_seal_fail_report_<UTC>.md` | MD twin |

No other files (including no docs/, no logs/, no data/, no tests/, no
runner_harness/) are touched by the seal execution turn.

---

## 9 · Next step after seal approval

After `SEAL_PASS`, the chain is `TIER_N_SPEC_SEALED`. The next
operator-authorized turns, in strict order, are:

1. **(P1) Plan-lock authoring** — §4 above. Produces
   `s7_d1_cross_asset_donchian_plan_lock.{md,json}`. **PLAN ONLY**: no
   BUILD, no fetch, no run. Operator must explicitly authorize this
   turn.
2. **(P2) Phase 2 plan doc authoring** — produces
   `s7_d1_cross_asset_donchian_phase2_plan.{md,json}` with the §C1-C8
   safety inheritance attestation. Operator must explicitly authorize.
3. **(P3) BUILD ONLY turn** — authors runner + execution_guard + tests
   under `external_research_hunter/s7_d1_cross_asset_donchian_runner_harness/`.
   No fetch, no run. Operator must explicitly authorize.
4. **(P4) T1-T15 smoke pass turn** — runs the smoke harness on
   synthetic fixtures only. No real data. Operator must explicitly
   authorize.
5. **(P5) Operator-side Databento fetch** — operator-managed; SPARTA
   receives the post-fetch local cache state. Claude does NOT call
   Databento.
6. **(P6) In-sample run turn** — at all five cost tiers S0-S4; produces
   the sealed diagnostic JSON. Operator must explicitly authorize.
7. **(P7) In-sample decision memo turn** — K/A verdict.
8. **(P8) Lifecycle transition turn** — `PARK` or `OOS-AUTHORIZE`. If
   `OOS-AUTHORIZE`, the OOS turn is itself a separate, later operator
   authorization with its own sealed chain step.

P1-P8 are NOT pre-authorized by this seal plan. Each requires its own
explicit operator turn. The seal plan only authorizes P0 ("the seal
execution turn"), and only after operator approval of THIS plan.

---

## 10 · Explicit rule: no backtest until seal passes AND operator authorizes

> **NO_BACKTEST_BEFORE_SEAL_AND_AUTHORIZATION_INVARIANT.**
>
> No backtest of any form — local engine, QuantConnect Cloud, BUILD-time
> smoke beyond T1-T15 synthetic fixtures, Databento data sampling,
> opportunistic single-day eval, "sanity check," ad-hoc Jupyter run, or
> anything that touches real market data — may execute until **BOTH** of
> the following are true:
>
> 1. The seal procedure in §1-§8 has completed with verdict
>    `SEAL_PASS` and `report_seal_sha256` is recorded for
>    `s7_d1_cross_asset_donchian_tier_n_spec.json`.
> 2. The operator has issued an explicit, scoped, written
>    authorization for the specific downstream turn (P1-P8 in §9).
>
> Authorization is per-turn and per-step. Authorizing P1 (plan-lock)
> does NOT authorize P3 (BUILD). Authorizing P3 (BUILD) does NOT
> authorize P4 (smoke). Authorizing P4 (smoke) does NOT authorize P6
> (in-sample run). Authorizing P6 (in-sample run) does NOT authorize
> any OOS inspection.
>
> Any violation of this invariant is `SEAL_FAIL_PROVENANCE_BROKEN`
> retroactive: the chain is invalidated; the candidate parks as
> `PARKED_PROVENANCE_BROKEN`; the operator memo records the violation
> and the corrective fresh `_revN_` requirement.

---

## Appendix · Boundaries explicitly held by this plan

This planning turn:

- Did NOT modify any sealed artifact.
- Did NOT compute a sha against any file (only enumerated which files
  WOULD be hashed by the seal execution turn).
- Did NOT author any Tier-N spec, plan-lock, Phase 2 plan, runner,
  guard, test, or run report.
- Did NOT call Databento, QuantConnect, any broker, any exchange, or
  any network endpoint.
- Did NOT fetch market data.
- Did NOT touch `obsidian-trade-logger`.
- Did NOT modify `review_queue.json` in any repo.
- Did NOT modify `strategies.json`, `strategy_status.json`,
  `live_config.json`, `strategy_decision_config.json`,
  `trade_coordinator_config.json`, `watchdog_config.json`, or
  `v2_scorecard_config.json` in `obsidian-trade-logger`.
- Did NOT modify any live or paper bot file.
- Did NOT change any scheduler or watchdog.
- Did NOT revive D5 YM-only, B005_001, or NKE Options Wheel.
- Did NOT promote any candidate.
- Did NOT grant FRC.

The only on-disk effect of this turn is the creation of this single
file: `docs/s7_d1_spec_seal_plan.md`.

---

*End of s7 D1 spec seal & validation plan. Plan only — no implementation,
no backtest, no Databento, no QuantConnect, no fetch, no live or paper
trading, no scheduler change, no obsidian-trade-logger mutation, no
review_queue mutation, no D5 / B005_001 / NKE revival. Awaiting operator
approval before the seal execution turn.*
