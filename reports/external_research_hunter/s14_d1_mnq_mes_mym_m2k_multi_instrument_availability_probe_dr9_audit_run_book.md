# s14-d1 multi-instrument availability probe + DR9 audit RUN_BOOK

**Document type:** RUN_BOOK (NOT a SEAL; no canonical `report_seal_sha256`)
**Authored (UTC):** `2026-05-27T20:31:11.140637Z`
**Lifecycle state:** `S14_D1_AVAILABILITY_PROBE_DR9_AUDIT_PENDING_OPERATOR_FETCH`
**Authorization phrase:** `Authorize s14-d1 multi-instrument availability probe + DR9 audit for MES, MYM, M2K only.`
**Anchored to s14-d1 PLAN at commit:** `5376de7` (file sha `be53ca7ecbb05ee4e243f15a98bf4e0208910d726e12ef787465544855f5f28f`)
**Anchored to s10-d1 fetch manifest model at:** `data/s10_d1_mnq_mgc_databento_long_history/raw/s10_d1_mnq_mgc_step02b_fetch_manifest.json` (sha `c4b7d2d064a601ce01e0c30190630640d27db0ef1cd9c5c5d8324b16655fc43b`)

----

## 0. Document scope

This document is a **RUN_BOOK** — controller-side advisory probe + pre-authored DR9 audit framework + operator-side fetch instructions. It is **NOT a SEAL**. No canonical `report_seal_sha256` is computed. The document records:

1. **Controller-side advisory probe** for MES.c.0 / MYM.c.0 / M2K.c.0 availability (based on vendor docs in `databento_vendor_docs/`, publicly-known CME equity-index micro futures launch info, and the s10-d1 fetch precedent).
2. **Pre-authored DR9 audit framework** (per-instrument check procedure + thresholds carried byte-equivalent from s10-d1 audit; thresholds immutable per `no_dr_redefinition_post_seal`).
3. **Operator-side fetch RUN_BOOK** (explicit step-by-step instructions for the operator to execute a Databento fetch with `DATABENTO_API_KEY` held only in their environment; controller never reads the key).
4. **Expected operator-captured artifacts** + paths.
5. **Contingency tree** per s14-d1 PLAN §3.2 (1-symbol fail / 2-symbol fail / 3-symbol fail / all pass / inconclusive_hold).

**Binding availability and DR9 outcomes can only be determined by operator-side fetch + controller-side audit at a separate authorization turn.** This RUN_BOOK does NOT report binding gate outcomes.

----

## 1. Explicit exclusions this turn

- No Databento call.
- No `DATABENTO_API_KEY` access.
- No network IO.
- No data fetch.
- No DR9 audit RESULTS sealed (only the framework is pre-authored; results require operator-captured CSVs at a future turn).
- No DRAFT, no SEAL, no BUILD, no backtest, no simulator, no signal computation, no OOS inspection.
- No live trading, no broker / exchange API.
- No Strategy Lab promotion, no candidate promotion.
- No s13-d1 / s12-d1 / parked-candidate revival.
- **No `brain_memory/projects/trading_bot/lessons.md` modification or staging.**
- No modification of any existing sealed artifact.

----

## 2. Controller-side advisory probe (NOT binding)

The controller reads (a) vendor docs in `databento_vendor_docs/`, (b) the s10-d1 fetch manifest as a model, and (c) publicly-known CME equity-index micro futures launch information. **No Databento call. No network IO.** Findings below are ADVISORY ONLY; binding availability is determined by operator-side fetch.

### 2.1 Known framework parameters

| Field | Value |
|---|---|
| Dataset | `GLBX.MDP3` (CME Globex; same dataset as MNQ.c.0 already in audit chain) |
| Schema | `ohlcv-1d` (daily aggregate bars; same as MNQ.c.0) |
| `stype_in` | `continuous` (same as MNQ.c.0) |
| Continuous contract convention | `{symbol_root}.c.0` = front-month continuous contract (Databento convention; verified for MNQ.c.0 / MGC.c.0) |
| Expected common-history start | `2019-05-13` (MNQ.c.0 start; CME launched MNQ/MES/MYM/M2K as a coordinated micro-futures family in May 2019) |
| Expected end date | `2025-12-30` (s14-d1 PLAN OOS window end) |

### 2.2 Per-symbol advisory probe

### MES.c.0 — Micro E-mini S&P 500

| Field | Value |
|---|---|
| Exchange | CME Globex |
| Expected dataset | `GLBX.MDP3` |
| Expected tick size | 0.25 points |
| Expected dollar per point | $5.0 |
| Approx. 2024 notional per contract | ~$26,000 |
| Controller advisory availability estimate | EXPECTED AVAILABLE — CME Globex; launched 2019-05-06; common-history start expected to match MNQ.c.0's 2019-05-13 within days; widely-traded equity-index micro futures |
| Expected DR9 outcome | EXPECTED PASS — equity-index micro futures have continuous-stitch behavior similar to MNQ; high liquidity; minimal gap risk |
| Risk factors | Low (similar liquidity profile to MNQ; same exchange + schedule + roll pattern) |

### MYM.c.0 — Micro E-mini Dow

| Field | Value |
|---|---|
| Exchange | CME Globex |
| Expected dataset | `GLBX.MDP3` |
| Expected tick size | 1.0 points |
| Expected dollar per point | $0.5 |
| Approx. 2024 notional per contract | ~$20,000 |
| Controller advisory availability estimate | EXPECTED AVAILABLE — CME Globex; launched 2019-05-06; common-history start expected to match MNQ.c.0 |
| Expected DR9 outcome | EXPECTED PASS — same family as MNQ/MES; similar liquidity profile |
| Risk factors | Low (similar to MES) |

### M2K.c.0 — Micro E-mini Russell 2000

| Field | Value |
|---|---|
| Exchange | CME Globex |
| Expected dataset | `GLBX.MDP3` |
| Expected tick size | 0.1 points |
| Expected dollar per point | $5.0 |
| Approx. 2024 notional per contract | ~$11,000 |
| Controller advisory availability estimate | EXPECTED AVAILABLE — CME Globex; launched 2019-05-06; common-history start expected to match MNQ.c.0 |
| Expected DR9 outcome | PROBABLE PASS — small-cap index micro futures have slightly lower liquidity than MES/MYM; thin-trading-day gaps possible in early 2019 weeks; DR9 audit will determine binding outcome |
| Risk factors | Low-to-moderate (Russell 2000 small-cap exposure; slightly thinner liquidity than MES/MYM; risk of one or two thin days early in 2019 history) |


### 2.3 Controller finding

All three target symbols (MES.c.0, MYM.c.0, M2K.c.0) are **EXPECTED to be available** on `GLBX.MDP3` with continuous-stitch behavior similar to MNQ.c.0. **EXPECTED outcomes are NOT BINDING.** Binding availability + DR9 outcomes can only be determined by operator-side fetch + controller-side audit at a separate authorization turn.

----

## 3. Pre-authored DR9 audit framework

### 3.1 Thresholds (carried byte-equivalent from s10-d1; immutable per `no_dr_redefinition_post_seal`)

| Check | Threshold | Direction |
|---|---|---|
| `gap_continuity` | **≥ 0.95** | min |
| `max_gap_ratio` | **≤ 0.30** | max |
| `roll_event_count` | **≤ 5** | max (note: see §3.3 below for context on what this counts) |
| `quality_violation_count` | **≤ 5** | max |

### 3.2 Per-instrument check procedure (to be performed at a future audit turn after operator capture)

1. Verify the captured CSV exists at the expected path.
2. Verify CSV `sha256` against the recorded value in the operator-captured fetch manifest.
3. Parse CSV; verify schema matches `sparta.databento.ohlcv_1d.continuous` (fields: `ts_event`, `open`, `high`, `low`, `close`, `volume`).
4. Compute `gap_continuity` = (number of trading days with rows) / (number of expected trading days between `first_ts` and `last_ts` based on a CME-Globex US-equity-index session calendar). Threshold: **≥ 0.95**.
5. Compute `max_gap_ratio` = max(consecutive missing trading days) / total trading days. Threshold: **≤ 0.30** (any single gap longer than 30% of the total window flags failure).
6. Count `roll_event_count` via detected discontinuities (price-level jumps consistent with futures roll). For continuous-stitch contracts on CME equity-index micros, expected ~24 quarterly rolls over the 6.6y window. **NOTE: the s10-d1 DR9 threshold of `≤ 5` was for ROLL EVENTS THAT VIOLATE STITCH QUALITY (not all roll events).** Audit-turn note: confirm with operator the exact semantics used in s10-d1 framework; the threshold semantics are immutable.
7. Count `quality_violation_count` = total checks failed across (bar OHLC sanity: `low ≤ open ≤ high` AND `low ≤ close ≤ high`; `volume ≥ 0`; `ts_event` monotonic; no duplicate `ts_event`). Threshold: **≤ 5**.
8. Aggregate: per-instrument DR9 status = **PASS** if ALL thresholds met; **FAIL** if any threshold violated; **INCONCLUSIVE_HOLD** if ambiguous (per s12-d1 DR9 outcome class).

### 3.3 Audit result schema per instrument (controller will populate at audit turn)

```json
{
  "symbol": "<MES.c.0 | MYM.c.0 | M2K.c.0>",
  "csv_path": "<absolute path>",
  "csv_sha256": "<hex>",
  "row_count": "<int>",
  "first_ts_event": "<ISO date>",
  "last_ts_event": "<ISO date>",
  "gap_continuity": "<float in [0,1]>",
  "max_gap_ratio": "<float in [0,1]>",
  "roll_event_count": "<int>",
  "quality_violation_count": "<int>",
  "dr9_per_instrument_status": "<PASS | FAIL | INCONCLUSIVE_HOLD>",
  "dr9_failure_branches_if_any": "<array of branch names that failed>"
}
```

----

## 4. Operator-side fetch RUN_BOOK

### 4.1 Executor + authorization scope

| Field | Value |
|---|---|
| Executor | **Operator** (separate browser session / local machine with `DATABENTO_API_KEY` in environment) |
| `DATABENTO_API_KEY` access | operator-side only; controller never reads the key |
| Network IO | operator-side only |
| Controller action this turn | **NONE** beyond authoring this RUN_BOOK |

### 4.2 Expected output directory + files

```
data/s14_d1_mnq_mes_mym_m2k_databento_long_history/
└── raw/
    ├── MES_c_0_ohlcv_1d_20190513_20251230.csv
    ├── MYM_c_0_ohlcv_1d_20190513_20251230.csv
    ├── M2K_c_0_ohlcv_1d_20190513_20251230.csv
    └── s14_d1_mes_mym_m2k_step02b_fetch_manifest.json
```

The manifest file shall conform to `sparta.s14.mes_mym_m2k.step02b_fetch_manifest.v1` (analogous to `sparta.s10.mnq_mgc.step02b_fetch_manifest.v1` at the s10-d1 model path).

### 4.3 Fetch parameters

| Parameter | Value |
|---|---|
| `dataset` | `GLBX.MDP3` |
| `schema` | `ohlcv-1d` |
| `stype_in` | `continuous` |
| `symbols` | `["MES.c.0", "MYM.c.0", "M2K.c.0"]` |
| `start_date_inclusive` | `2019-05-13` |
| `end_date_inclusive` | `2025-12-30` |
| `is_window_start` | `2019-05-13` |
| `is_window_end` | `2023-12-29` |
| `oos_window_start_LOCKED_NOT_INSPECTED` | `2024-01-02` |
| `oos_window_end_LOCKED_NOT_INSPECTED` | `2025-12-30` |

### 4.4 Required operator-side fetch boundaries (must hold during fetch)

- `databento_api_key_read_from_env_only` = `True`
- `databento_api_key_never_printed_or_logged_or_saved` = `True`
- `no_dbn_zst_cache_written_by_client_no_path_kwarg_passed` = `True`
- `no_signal_computation` = `True`
- `no_backtest` = `True`
- `no_simulator_run` = `True`
- `no_oos_inspection_by_this_fetch` = `True`
- `no_review_queue_mutation` = `True`
- `no_strategy_lab_promotion` = `True`
- `no_live_trading` = `True`
- `raw_csv_only_written_to_approved_directory` = `True`

### 4.5 Post-fetch action

After all 3 CSVs + the manifest exist at the expected paths, the operator types:

```
Authorize s14-d1 multi-instrument availability probe + DR9 audit RESULT SEALING only.
```

This is a **separate authorization turn** that invokes controller-side DR9 audit + sealed result. The current RUN_BOOK does NOT authorize the audit result sealing; only the framework.

----

## 5. Contingency tree per s14-d1 PLAN §3.2

| Contingency | Description | Next authorization (each separate) |
|---|---|---|
| **All 3 symbols pass DR9** | MES, MYM, M2K all pass with thresholds met. 4-instrument basket fully available. | `Authorize s14-d1 multi-instrument RSI(2) bi-directional Tier-N spec DRAFT only — bound by DR10 v2.` |
| **1 symbol fails DR9** | One of MES/MYM/M2K fails DR9 (most likely M2K thin-liquidity gap, per advisory risk assessment). | `Authorize s14-d1 shrunk-basket Tier-N spec PLAN only — bound by DR10 v2.` (requires fresh `candidate_record_id`; substitution forbidden) |
| **2 symbols fail DR9** | Two fail. 2-symbol remaining + MNQ may not have enough diversification/signal density. | `Authorize s14-d1 cash-equity 3-name basket RSI(3) bi-directional Tier-N spec PLAN only — bound by DR10 v2.` (T2 rev2 documented fallback) |
| **3 symbols fail DR9** | All MES, MYM, M2K fail. Multi-instrument micro-futures hypothesis fails at data-quality gate. | Same as 2-symbol-fail: T2 rev2 cash-equity alternative. |
| **Any INCONCLUSIVE_HOLD** | DR9 returns ambiguous outcome on any symbol. | Operator manual review + decision; no auto-progression. (Analogous to s10-d1 INCONCLUSIVE_HOLD park.) |

----

## 6. Hard boundaries held this RUN_BOOK turn

All True:

- No Databento call · no API key access · no network IO · no data fetch
- **No DR9 audit RESULTS sealed** (only the framework is pre-authored)
- **No DR9 audit RUN executed** (the audit awaits operator-captured CSVs)
- No DRAFT · no SEAL · no BUILD · no backtest · no simulator · no signal computation · no OOS inspection
- No live trading · no broker / exchange API
- No Strategy Lab invoked or promoted · no candidate promotion
- No s13-d1 / s12-d1 / parked-candidate revival
- No modification of any existing sealed artifact
- No phase-2-safety-contract template / CLAUDE.md / .gitignore modification
- **No `brain_memory/projects/trading_bot/lessons.md` modification or staging**
- No `review_queue` / `idea_memory` mutation
- No profitability claim
- **This document is NOT a SEAL** (no canonical `report_seal_sha256` computed; `document_type = RUN_BOOK_NOT_SEALED`)
- Controller advisory probe outcomes are ADVISORY ONLY — binding availability is operator-fetch-determined
- DR9 audit framework is PRE-AUTHORED ONLY — binding outcomes are operator-CSV-determined

----

## 7. Status (UNCHANGED across this RUN_BOOK turn)

trading: `PAUSED` · live: `BLOCKED_AT_6_GATES` · FRC: `NEVER_GRANTED` · `no_strategy_optimization_authorized = True` · `no_dr_redefinition_post_seal` (per existing sealed candidates) `= True` · REC1-equivalent binding `True` · DIAGNOSTIC_ONLY_NOT_LIVE_GRADE · s13-d1 + s12-d1 lifecycles terminal · framework DR10 revision v2 lifecycle `FRAMEWORK_DR10_REVISION_V2_SEALED` (binding for s14+ only)

s14-d1 lifecycle state: **`S14_D1_AVAILABILITY_PROBE_DR9_AUDIT_PENDING_OPERATOR_FETCH`**

----

## 8. Next-step authorization scope

### Primary forward (operator-side action; outside controller scope)

The operator performs the fetch per §4 of this RUN_BOOK and confirms the captured artifacts at the expected paths. Then types:

```
Authorize s14-d1 multi-instrument availability probe + DR9 audit RESULT SEALING only.
```

### Alternative (defer)

```
Defer / Pause s14-d1 multi-instrument availability probe + DR9 audit.
```

Keep the RUN_BOOK on file; no operator fetch initiated.

### Alternative (revert to T2 rev2)

If the operator prefers to skip the multi-instrument micro-futures fetch entirely:

```
Authorize s14-d1 cash-equity 3-name basket RSI(3) bi-directional Tier-N spec PLAN only — bound by DR10 v2.
```

----

End of RUN_BOOK. NOT a SEAL. No code, no backtest, no simulator, no signal, no data fetch, no Databento, no API key access, no QC, no LEAN, no brokerage, no real order, no paper order, no Strategy Lab promotion, no `review_queue` mutation, no production `idea_memory` mutation. **No retroactive application of DR10 v2 to existing candidates. No s13-d1 / s12-d1 / parked-candidate revival. No `lessons.md` modification or staging.** No live trading. Trading remains `PAUSED`. Live remains `BLOCKED_AT_6_GATES`. Binding availability + DR9 outcomes pending operator-side fetch.
