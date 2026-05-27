# s14-d1-cash-equity availability probe + DR9 audit RUN_BOOK

**Document type:** RUN_BOOK (NOT a SEAL; no canonical `report_seal_sha256` computed)
**Authored (UTC):** `2026-05-27T23:24:13.694509Z`
**Lifecycle state:** `S14_D1_CASH_EQUITY_AVAILABILITY_PROBE_DR9_AUDIT_PENDING_OPERATOR_FETCH`
**Authorization phrase:** `Authorize s14-d1-cash-equity multi-name OHLCV availability probe + DR9 audit framework only.`
**Anchored to s14-d1-cash-equity PLAN at commit:** `a6cbafd` (file sha `6a3a186aa665829abca3e5a40b770ae8df44438f2f0f888a4f482cebda8a5bdd`)
**Anchored to s14-d1-multi-instrument RUN_BOOK model at commit:** `13ff641` (md sha `96b2304fba53dd88f3e7cc1db8088008aa3537d5eeedb20569dbd3df61df6d3c`)
**Anchored to s10-d1 fetch manifest model:** `data/s10_d1_mnq_mgc_databento_long_history/raw/s10_d1_mnq_mgc_step02b_fetch_manifest.json` (sha `c4b7d2d064a601ce01e0c30190630640d27db0ef1cd9c5c5d8324b16655fc43b`)

----

## 0. Document scope

RUN_BOOK + vendor comparison + pre-authored DR9 audit framework for cash-equity OHLCV (AAPL/MSFT/NVDA). **NOT a SEAL.** No canonical `report_seal_sha256` computed. The document records:

1. **Vendor comparison** (yfinance / Polygon free + paid / Tiingo / Alpha Vantage / paid vendor) — admissibility + trade-offs
2. **Pre-authored OHLCV fetch requirements** (window, schema, adjustment convention precommit options)
3. **Expected output paths + manifest schema** (analogous to s10-d1 model)
4. **Pre-authored DR9 audit framework adapted for cash equity** (no continuous-stitch; splits/dividends instead; NYSE/NASDAQ trading calendar)
5. **Per-symbol risk assessment** (AAPL/MSFT/NVDA corporate actions in window; NVDA 2024-06-10 10:1 split is load-bearing)
6. **Contingency tree**

**Binding availability and DR9 outcomes can only be determined by operator-side fetch + controller-side audit at a separate authorization turn.**

----

## 1. Explicit exclusions this turn

- No vendor API call by controller (no yfinance / Polygon / Tiingo / Alpha Vantage / paid-vendor call).
- No `DATABENTO_API_KEY` or any other API-key access.
- No network IO. No data fetch.
- No DR9 audit RESULTS sealed (only the framework is pre-authored).
- No DR9 audit RUN executed.
- No DRAFT, no SEAL, no BUILD, no backtest, no simulator, no signal computation, no OOS inspection.
- No live trading, no broker / exchange API.
- No Strategy Lab promotion, no candidate promotion.
- No s13-d1 / s12-d1 / parked-candidate revival.
- No modification of s14-d1-multi-instrument RUN_BOOK at `13ff641` / PLAN at `5376de7` / cash-equity PLAN at `a6cbafd` / any other sealed artifact.
- **No `brain_memory/projects/trading_bot/lessons.md` modification or staging.**

----

## 2. Vendor comparison (controller advisory; operator selects)

The controller compares vendor options based on (a) data coverage for AAPL/MSFT/NVDA over the s14-d1-cash-equity 5y IS + 2y OOS window (2019-01-02 to 2025-12-30), (b) free-tier limits + paid-tier availability, (c) adjustment-convention configurability, (d) documented quality reputation. **All comparisons below are ADVISORY ONLY**; binding availability is operator-fetch-determined.

### yfinance

| Field | Value |
|---|---|
| Type | Python library wrapping Yahoo Finance |
| Cost | FREE |
| Free tier limits | no formal limit but rate-limited / can be throttled by Yahoo; recommended < 1 req/sec |
| Paid tier available | False |
| Data coverage for AAPL/MSFT/NVDA | AAPL/MSFT/NVDA: full history back to IPO (AAPL 1980, MSFT 1986, NVDA 1999); daily OHLCV reliable on major equities |
| Adjustment convention default | split+dividend adjusted (yfinance default); unadjusted available via auto_adjust=False |
| Adjustment convention configurable | True |

**Pros:**
  - Easiest install (`pip install yfinance`); minimal setup
  - No API key required
  - Adequate quality for most modern history (post-2010 generally clean)

**Cons:**
  - Quality variability is the main concern; recommend sha256 of fetched CSV pinned at fetch time to detect future drift
  - Yahoo Finance is unofficial/scraping-based; could break without notice
  - Not appropriate for production-quality bind

**Controller advisory:** ADMISSIBLE for diagnostic-only research; precommit adjustment convention + pin sha256 at fetch time to detect future drift

### Polygon free tier

| Field | Value |
|---|---|
| Type | REST API; official broker data aggregator |
| Cost | FREE tier; paid tiers available |
| Free tier limits | 5 calls/min on free tier; 2y of historical data on free tier (insufficient for s14-d1 5y IS window — NEEDS PAID TIER) |
| Paid tier available | True |
| Data coverage for AAPL/MSFT/NVDA | AAPL/MSFT/NVDA: 30+ year history on paid tier; 2y on free tier (LIMITING for our 5y IS window requirement) |
| Adjustment convention default | configurable: adjusted=true/false query parameter; defaults to adjusted |
| Adjustment convention configurable | True |

**Pros:**
  - High quality reference data (official exchange aggregation)
  - Configurable adjustment convention
  - Well-documented REST API

**Cons:**
  - Free tier 2y history limit is INSUFFICIENT for our 5y IS window (2019-01-02 to 2023-12-29)
  - Paid tier required for full s14-d1 window — operator-cost decision
  - 5 calls/min rate limit OK for 3 names × 1 historical fetch

**Controller advisory:** EXCELLENT QUALITY but free tier insufficient for s14-d1's 5y window; admissible only if operator authorizes paid tier OR shortens IS window to ~2y (which would weaken K9 IS margin)

### Tiingo

| Field | Value |
|---|---|
| Type | REST API; well-respected data quality reputation |
| Cost | FREE tier; paid tiers available |
| Free tier limits | 500 unique symbols/hour on free tier; 1000 requests/hour; 30y+ daily history included |
| Paid tier available | True |
| Data coverage for AAPL/MSFT/NVDA | AAPL/MSFT/NVDA: full history back to IPO; well-known clean historical record |
| Adjustment convention default | configurable: adjClose vs close columns; both available in single response |
| Adjustment convention configurable | True |

**Pros:**
  - High data quality reputation
  - Free tier includes full historical depth (no s14-d1 window blocker)
  - Both adjusted and unadjusted columns in single response (no need to choose convention at fetch — can defer to SEAL)
  - Free API key registration is fast

**Cons:**
  - Requires free API key registration (operator-side; controller doesn't access)
  - Smaller community than yfinance — less troubleshooting context

**Controller advisory:** RECOMMENDED PRIMARY for s14-d1-cash-equity: high quality + full historical depth on free tier + both adjustment conventions in single fetch

### Alpha Vantage

| Field | Value |
|---|---|
| Type | REST API |
| Cost | FREE tier; paid tiers available |
| Free tier limits | 5 calls/min, 500 calls/day on free tier; 20y+ historical daily on free tier |
| Paid tier available | True |
| Data coverage for AAPL/MSFT/NVDA | AAPL/MSFT/NVDA: 20y+ daily on free tier (sufficient for s14-d1 5y IS window) |
| Adjustment convention default | TIME_SERIES_DAILY (unadjusted) vs TIME_SERIES_DAILY_ADJUSTED (split-only or split+dividend depending on endpoint) |
| Adjustment convention configurable | True |

**Pros:**
  - Free tier includes 20y+ depth
  - Multiple adjustment-convention endpoints
  - Free API key registration

**Cons:**
  - Tight rate limits (5 calls/min)
  - TIME_SERIES_DAILY_ADJUSTED on free tier was deprecated in 2024; only paid tier now has adjusted
  - Requires verification of current free-tier endpoint availability before operator commits

**Controller advisory:** ADMISSIBLE but verify current free-tier endpoint availability for adjusted data; Tiingo may be lower-friction overall

### Paid vendor (Polygon paid / IEX Cloud / Refinitiv / Bloomberg)

| Field | Value |
|---|---|
| Type | REST API / direct feed; institutional-grade |
| Cost | PAID ($30-thousands/mo depending on vendor) |
| Free tier limits | n/a (paid) |
| Paid tier available | True |
| Data coverage for AAPL/MSFT/NVDA | Full historical; institutional reliability; SLAs |
| Adjustment convention default | vendor-specific; all support both conventions |
| Adjustment convention configurable | True |

**Pros:**
  - SLA + reliability
  - Best historical data quality
  - No rate-limit concerns

**Cons:**
  - Cost; overkill for diagnostic-only research at this scale
  - Operator decision on cost-benefit

**Controller advisory:** OVERKILL for diagnostic-only at this scale; admissible if operator already has paid access; otherwise free-tier options (Tiingo recommended) are sufficient


### 2.1 Controller advisory vendor preference

| Rank | Vendor | Rationale |
|---|---|---|
| **PRIMARY** | **Tiingo** | Free tier includes full historical depth; both adjusted+unadjusted columns in single response (defer convention to SEAL); generous rate limits; high quality reputation |
| Secondary | yfinance | Zero-setup (no API key); admissible for diagnostic-only research with sha256 pinning at fetch time |
| Tertiary | Alpha Vantage / Polygon paid / Other paid | Admissible but verify endpoint availability / cost-benefit |

**Recommendation is NOT binding.** Operator selects vendor at Step 1 of the unblock path (§4).

----

## 3. Per-symbol risk assessment

The controller's per-symbol advisory based on publicly-known corporate-action history. **Advisory only; binding via operator fetch + DR9 audit.**

### AAPL — Apple Inc.

| Field | Value |
|---|---|
| Exchange | NASDAQ |
| CIK | 0000320193 |
| IPO date (approximate) | 1980-12-12 |
| Common history start for 5y IS window | 2019-01-02 (well within historical depth on all candidate vendors) |
| Controller advisory availability | EXPECTED AVAILABLE on all candidate vendors with clean data |
| Expected DR9 outcome | EXPECTED PASS (high liquidity; clean historical record) |
| Risk factors | Low (mega-cap with well-documented corporate actions) |

**Known corporate actions 2019-2025:**
  - Stock splits: AAPL 4:1 on 2020-08-31; no other splits in window
  - Dividends: regular quarterly ~$0.20-0.25/share; split-adjusted convention dependent

### MSFT — Microsoft Corp.

| Field | Value |
|---|---|
| Exchange | NASDAQ |
| CIK | 0000789019 |
| IPO date (approximate) | 1986-03-13 |
| Common history start for 5y IS window | 2019-01-02 (well within historical depth) |
| Controller advisory availability | EXPECTED AVAILABLE on all candidate vendors with clean data |
| Expected DR9 outcome | EXPECTED PASS (high liquidity; no splits in window; clean record) |
| Risk factors | Very low (no splits in our window; minimal corporate-action complexity) |

**Known corporate actions 2019-2025:**
  - Stock splits: NONE in 2019-2025 window (last split 2003)
  - Dividends: regular quarterly; split-adjusted convention dependent

### NVDA — NVIDIA Corp.

| Field | Value |
|---|---|
| Exchange | NASDAQ |
| CIK | 0001045810 |
| IPO date (approximate) | 1999-01-22 |
| Common history start for 5y IS window | 2019-01-02 (well within historical depth) |
| Controller advisory availability | EXPECTED AVAILABLE on all candidate vendors with clean data |
| Expected DR9 outcome | EXPECTED PASS but the 10:1 split in 2024-06-10 is the LOAD-BEARING audit check — must verify vendor applies it correctly per chosen adjustment convention |
| Risk factors | Moderate (recent large 10:1 split is the load-bearing audit concern; vendors that mis-apply it would produce ~$1300/share pre-split prices that wreck RSI calculation) |

**Known corporate actions 2019-2025:**
  - Stock splits: NVDA 4:1 on 2021-07-20; NVDA 10:1 on 2024-06-10 (LARGE recent split — critical to verify vendor applies correctly per chosen adjustment convention)
  - Dividends: small regular quarterly until 2024 paused / changed


### 3.1 Load-bearing audit concern: NVDA 2024-06-10 10:1 split

The NVDA 10:1 split on 2024-06-10 is the **load-bearing DR9 audit check** for s14-d1-cash-equity. A vendor that misapplies this split would produce ~$1,300/share pre-split prices that are 10x the actual traded prices, which would wreck RSI signal generation (RSI thresholds 15/85 calibrated for typical AAPL/MSFT/NVDA modern price ranges). The DR9 audit framework (§5) explicitly verifies `documented_split_event_consistency` for each known split in the window.

----

## 4. Adjustment convention precommit (REQUIRED at SEAL; not at this RUN_BOOK turn)

Operator MUST precommit one of:

1. **`split_only`**: raw close × split factor; dividends NOT adjusted into price. Dividends appear as instant downward jumps on ex-div date. Closer to actual traded prices. Commonly used for short-term trading strategies.
2. **`split_plus_dividend`**: total-return convention. Dividends + splits both adjusted into price. Smooth total-return series; no dividend jumps. Commonly used for long-term performance research.

**Controller advisory for RSI(3) bi-directional mean-reversion:** `split_only` likely more appropriate — preserves actual price jumps that the mechanic responds to. Dividend jumps on ex-div date are small relative to typical price moves on AAPL/MSFT/NVDA (~$0.20-0.25/share on AAPL is <0.1% of price) so should not materially affect signal generation. **Operator final decision at SEAL.**

**Switching post-SEAL: FORBIDDEN.** Mixing conventions across symbols: FORBIDDEN.

----

## 5. Pre-authored DR9 audit framework (cash-equity adapted)

### 5.1 Thresholds (carried from s10-d1 with cash-equity adaptations; immutable per `no_dr_redefinition_post_seal`)

| Check | Threshold | Direction | Cash-equity adaptation |
|---|---|---|---|
| `gap_continuity` | **≥ 0.95** | min | Unchanged (rows present per expected NYSE trading day; calendar = NYSE/NASDAQ US equity) |
| `max_gap_ratio` | **≤ 0.30** | max | Unchanged |
| `roll_event_count` | **NOT_APPLICABLE_CASH_EQUITY** | n/a | Structurally absent (cash equity does not have futures rolls) |
| `quality_violation_count` | **≤ 5** | max | Unchanged (OHLC sanity, ts monotonic, no duplicates) |
| `documented_split_event_consistency` (NEW) | **PASS** required | n/a | Vendor must apply known splits per chosen adjustment convention |

### 5.2 8-step per-symbol check procedure (to be performed at a future audit turn after operator capture)

1. Verify the captured CSV exists at the expected path.
2. Verify CSV `sha256` against the recorded value in the operator-captured fetch manifest.
3. Parse CSV; verify schema matches the manifest-declared schema (`date`, `open`, `high`, `low`, `close`, `volume`, optional `adjusted_close`).
4. Determine NYSE/NASDAQ trading day count between `first_ts` and `last_ts` using a public US equity trading calendar (e.g., `pandas_market_calendars`).
5. Compute `gap_continuity` = `rows_present / expected_trading_days`. Threshold **≥ 0.95**.
6. Compute `max_gap_ratio` = max consecutive missing trading days / total trading days. Threshold **≤ 0.30**.
7. Count `quality_violation_count` across (OHLC sanity: `low ≤ open ≤ high` AND `low ≤ close ≤ high`; `volume ≥ 0`; `ts` monotonic; no duplicate `ts`). Threshold **≤ 5**.
8. Verify `documented_split_event_consistency`: for each known split in window, check the CSV's price series shows EITHER (a) a clean discontinuity at the ex-split date (if unadjusted) OR (b) NO discontinuity at the ex-split date (if adjusted). Mixed/partial application FAILS.
9. Aggregate: per-symbol DR9 status = **PASS** / **FAIL** / **INCONCLUSIVE_HOLD**.

### 5.3 Per-symbol audit result schema

```json
{
  "symbol": "<AAPL | MSFT | NVDA>",
  "csv_path": "<absolute path>",
  "csv_sha256": "<hex>",
  "row_count": "<int>",
  "first_date": "<ISO date>",
  "last_date": "<ISO date>",
  "expected_trading_days_nyse_calendar": "<int>",
  "gap_continuity": "<float in [0,1]>",
  "max_gap_ratio": "<float in [0,1]>",
  "quality_violation_count": "<int>",
  "documented_split_event_consistency": "<PASS | FAIL | INCONCLUSIVE_HOLD>",
  "splits_in_window": "<array of {date, ratio, applied_per_convention}>",
  "dr9_per_instrument_status": "<PASS | FAIL | INCONCLUSIVE_HOLD>",
  "dr9_failure_branches_if_any": "<array>"
}
```

----

## 6. Operator-side fetch RUN_BOOK

### 6.1 Step 1 — Operator selects vendor

Options: `yfinance, Polygon free tier, Tiingo, Alpha Vantage, Paid vendor (Polygon paid / IEX Cloud / Refinitiv / Bloomberg)`. Controller advisory: **Tiingo recommended** (see §2.1).

### 6.2 Step 2 — Operator selects adjustment convention

Options: `split_only` OR `split_plus_dividend`. Controller advisory for RSI(3) bi-directional: `split_only`. **Switching post-SEAL forbidden.**

### 6.3 Step 3 — Operator fetches data

For each of AAPL / MSFT / NVDA:
- Fetch daily OHLCV from selected vendor over window `2019-01-02` to `2025-12-30` inclusive
- Apply selected adjustment convention
- Save to `data/s14_d1_aapl_msft_nvda_cash_equity_long_history/raw/<symbol>_ohlcv_1d_20190102_20251230_<adj_convention>.csv`
- Compute `sha256` of the saved CSV

### 6.4 Step 4 — Operator writes manifest

Path: `data/s14_d1_aapl_msft_nvda_cash_equity_long_history/raw/s14_d1_cash_equity_step02b_fetch_manifest.json`

Schema: `sparta.s14.cash_equity.step02b_fetch_manifest.v1` — see §7 below for required fields.

### 6.5 Step 5 — Operator verifies + re-issues authorization

Verify: all 3 CSVs exist at expected paths + manifest exists with `sha256` entries + adjustment convention recorded.

Then re-issue: `Authorize s14-d1-cash-equity multi-name OHLCV availability probe + DR9 audit RESULT SEALING only.`

Controller then verifies captured artifact `sha256`s + performs DR9 audit per §5 + seals result.

### 6.6 Required operator-side fetch boundaries

- `vendor_api_key_read_from_env_only` (if applicable; n/a for yfinance)
- `vendor_api_key_never_printed_or_logged_or_saved`
- `no_signal_computation`, `no_backtest`, `no_simulator_run`
- `no_oos_inspection_by_this_fetch`
- `no_review_queue_mutation`
- `no_strategy_lab_promotion`
- `no_live_trading`
- `raw_csv_only_written_to_approved_directory`

----

## 7. Manifest schema (pre-authored; operator populates at fetch)

```
{
  "schema": "sparta.s14.cash_equity.step02b_fetch_manifest.v1",
  "candidate_record_id": "s14-d1-aapl-msft-nvda-cash-equity-rsi-3-bi-directional-large-cap-long-history",
  "sealed_spec_commit_anchor": "<future Tier-N SEAL commit hash; placeholder at fetch>",
  "vendor": "<yfinance | polygon | tiingo | alpha_vantage | paid:<name>>",
  "vendor_endpoint": "<URL or library function>",
  "adjustment_convention": "<split_only | split_plus_dividend>",
  "schema": "ohlcv-daily",
  "start_date_inclusive": "2019-01-02",
  "end_date_inclusive": "2025-12-30",
  "is_window_start": "2019-01-02",
  "is_window_end": "2023-12-29",
  "oos_window_start_LOCKED_NOT_INSPECTED": "2024-01-02",
  "oos_window_end_LOCKED_NOT_INSPECTED": "2025-12-30",
  "fetch_run_utc": "<ISO UTC>",
  "symbols": [
    {
      "symbol": "AAPL",
      "output_path": "data/s14_d1_aapl_msft_nvda_cash_equity_long_history/raw/AAPL_ohlcv_1d_20190102_20251230_<adj>.csv",
      "row_count": "<int>",
      "size_bytes": "<int>",
      "sha256": "<hex>",
      "first_timestamp": "<ISO>",
      "last_timestamp": "<ISO>",
      "vendor": "<vendor>",
      "schema": "ohlcv-daily",
      "adjustment_convention": "<convention>",
      "start": "2019-01-02",
      "end": "2025-12-30",
      "known_splits_in_window": [{"date": "2020-08-31", "ratio": "4:1"}],
      "splits_applied_by_vendor": "<bool>",
      "vendor_specific_notes": "<optional>"
    },
    /* similar entries for MSFT, NVDA */
  ],
  "boundaries_held": {
    "vendor_api_key_read_from_env_only": true,
    "vendor_api_key_never_printed_or_logged_or_saved": true,
    "no_signal_computation": true,
    "no_backtest": true,
    "no_simulator_run": true,
    "no_oos_inspection_by_this_fetch": true,
    "no_review_queue_mutation": true,
    "no_strategy_lab_promotion": true,
    "no_live_trading": true,
    "raw_csv_only_written_to_approved_directory": true
  }
}
```

----

## 8. Contingency tree

| Contingency | Next authorization (each separate) |
|---|---|
| **All 3 symbols pass DR9** | `Authorize s14-d1-cash-equity Tier-N spec DRAFT only — bound by DR10 v2.` |
| **1 symbol fails DR9** (most likely NVDA due to 10:1 split) | `Authorize s14-d1-cash-equity shrunk-basket Tier-N spec PLAN only — bound by DR10 v2.` (fresh `candidate_record_id`; substitution forbidden) |
| **2 or 3 symbols fail DR9** | `Authorize s14-d1-cash-equity universe revision to alternative shortlist — bound by DR10 v2.` |
| **Any `INCONCLUSIVE_HOLD`** | Operator manual review; no auto-progression |
| **Vendor fetch fails** (API down, quota, network) | Operator retries with different vendor or later time; this RUN_BOOK remains the reference framework |

----

## 9. Hard boundaries held this RUN_BOOK turn

All True:

- No vendor API call by controller · no Databento API key access · no other API key access · no network IO · no data fetch
- **No DR9 audit RESULTS sealed** · **no DR9 audit RUN executed**
- No DRAFT · no SEAL · no BUILD · no backtest · no simulator · no signal computation · no OOS inspection
- No live trading · no broker / exchange API
- No Strategy Lab invoked or promoted · no candidate promotion
- No s13-d1 / s12-d1 / parked-candidate revival
- No modification of s14-d1-multi-instrument RUN_BOOK at `13ff641` / PLAN at `5376de7` / cash-equity PLAN at `a6cbafd` / any existing sealed artifact
- No phase-2-safety-contract template / CLAUDE.md / .gitignore modification
- **No `brain_memory/projects/trading_bot/lessons.md` modification or staging**
- No `review_queue` / `idea_memory` mutation
- No profitability claim
- **This document is NOT a SEAL** (`document_type = RUN_BOOK_NOT_SEALED`; no `report_seal_sha256` computed)
- Controller vendor recommendation is ADVISORY ONLY — binding selection pending operator decision
- DR9 audit framework is PRE-AUTHORED ONLY — binding outcomes are operator-CSV-determined

----

## 10. Status (UNCHANGED across this RUN_BOOK turn)

trading: `PAUSED` · live: `BLOCKED_AT_6_GATES` · FRC: `NEVER_GRANTED` · `no_strategy_optimization_authorized = True` · REC1-equivalent binding True · DIAGNOSTIC_ONLY_NOT_LIVE_GRADE · s13-d1 + s12-d1 lifecycles terminal · framework DR10 v2 binding for s14+.

**s14-d1-cash-equity lifecycle state:** `S14_D1_CASH_EQUITY_AVAILABILITY_PROBE_DR9_AUDIT_PENDING_OPERATOR_FETCH` (advanced from `S14_D1_CASH_EQUITY_TIER_N_SPEC_PLAN_AUTHORED`).

**s14-d1-multi-instrument lifecycle state (sibling):** `S14_D1_AVAILABILITY_PROBE_DR9_AUDIT_PENDING_OPERATOR_FETCH` (still gate-blocked at Databento fetch unavailability; PLAN + RUN_BOOK + decline memos all byte-stable).

----

## 11. Next-step authorization scope

### Primary forward (operator-side action; outside controller scope)

Operator performs Steps 1-5 of §6 (vendor selection → adjustment convention → fetch → manifest → verify + re-issue). Then types:

```
Authorize s14-d1-cash-equity multi-name OHLCV availability probe + DR9 audit RESULT SEALING only.
```

### Alternative (defer)

```
Defer / Pause s14-d1-cash-equity multi-name OHLCV availability probe + DR9 audit.
```

Keep the RUN_BOOK on file; no operator fetch initiated.

### Alternative (universe revision; if A7 concern dominates)

```
Authorize s14-d1-cash-equity universe revision to cross-sector basket — bound by DR10 v2.
```

Re-authors the PLAN under a fresh `candidate_record_id` (e.g., `s14-d1-aapl-jpm-xom-cash-equity-...`). Would require a fresh RUN_BOOK turn after the new PLAN.

----

End of RUN_BOOK. NOT a SEAL. No code, no backtest, no fetch, no vendor API call, no API key access, no QC, no LEAN, no brokerage, no live trading. **No fabrication. No retroactive application of DR10 v2. No s13-d1 / s12-d1 / parked-candidate revival. No `lessons.md` modification or staging.** Trading remains `PAUSED`. Live remains `BLOCKED_AT_6_GATES`. Binding availability + DR9 outcomes pending operator-side fetch + future result-sealing authorization turn.
