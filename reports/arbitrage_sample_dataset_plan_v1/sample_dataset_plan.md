# SPARTA Arbitrage Sample Dataset Plan v1

> **Research-only. Planning / specification only.**
> No broker control. No live trading. No paper-order execution. No exchange
> connection. No API keys. No `.env`. No credential handling. No scheduler /
> background daemon. **No external network calls. No data fetch. No backtest.
> No dataset processing in this bundle. No real data files are created here.**
> This document is the written plan for the **first tiny sample dataset**
> SPARTA might later collect; the actual collection is a SEPARATE,
> separately-authorized future bundle.

**Plan id:** `arbitrage_sample_dataset_plan_v1` · **version:** `1.0`

**Companion documents:**
[`arbitrage_research_protocol_v1`](../arbitrage_research_protocol_v1/protocol.md) ·
[`arbitrage_data_contract_v1`](../arbitrage_data_contract_v1/data_contract.md) ·
[`arbitrage_dataset_manifest_v1`](../arbitrage_dataset_manifest_v1/dataset_manifest.md) ·
[`arbitrage_qa_harness_spec_v1`](../arbitrage_qa_harness_spec_v1/qa_harness_spec.md) ·
[`arbitrage_data_source_evaluation_v1`](../arbitrage_data_source_evaluation_v1/data_source_evaluation.md).

---

## 1. Research objective

Define the tiny first sample dataset SPARTA might later collect for
arbitrage research — exactly which category, which symbol shape, which
time-window shape, which fields, how it would be named and stored, how it
would be QA'd, and which approval gates must be cleared first. This plan
**does not fetch**, **does not connect**, **does not run a backtest**, and
**does not authorize trading**. It is a planning input only.

### Supported arbitrage categories this plan serves

This plan serves the five categories defined by
`arbitrage_research_protocol_v1`. The first sample focuses on **category A
(cross-exchange spot)**; category B (spot-perp basis / funding) is held
back as an optional future extension; categories C, D, and E (the latter
labeled **NOT pure arbitrage**) are out of scope for the first sample.

## 2. Proposed sample scope (TINY)

- **Primary category:** `cross_exchange_spot`.
- **Secondary category (optional future extension only):**
  `spot_perp_basis_funding`.
- **Symbols (example only):** `BTC_USDT`, `ETH_USDT` — both deepest-liquidity
  pairs; cleanest first sample. The actual symbol list is approved later.
- **Venues (labels only, **not** credentials or live connectors):**
  `Venue_A`, `Venue_B`. The actual venue names are approved later.
- **Time window (shape only, **no dates set here**):** duration examples
  `1_hour` or `1_day`, UTC-aligned, with a warmup buffer and an IS/OOS
  split sealed before any run. Actual dates set at approval time.
- **Quote level required:** L1 (best bid/ask + sizes). L2 (top 5–10 levels)
  preferred if the future source supports it.
- **Fees:** dated per-venue schedule pinned in the manifest.
- **Funding:** only if the perp extension is later authorized.

### Explicit disclaimers

- **This plan is NOT an authorization to fetch data.**
- The venue names `Venue_A` / `Venue_B` are **labels only**; the actual
  venues must be **explicitly approved later**.
- The data source class must be **explicitly approved later** (from Bundle
  8's allowed classes only — A, B, C, or D; never E or F).
- The storage path must be **explicitly approved later**.
- The symbol examples (`BTC_USDT`, `ETH_USDT`) are illustrative; the actual
  symbol set is approved later.

## 3. Candidate venues / symbols / time windows

- **Candidate venues:** no live venue is named in this plan. Future
  approval will name 1–2 specific spot venues from the operator-approved
  source class (preferred: paid-vendor offline export covering 2 venues;
  alternative: each venue's public historical archive).
- **Candidate symbols:** illustrative only (`BTC_USDT`, `ETH_USDT`). Each
  symbol must exist on BOTH named venues for cross-exchange spot; each
  carries its per-venue canonical name + SPARTA canonical name.
- **Candidate time windows:** shape documented (1 hour / 1 day, UTC,
  warmup buffer required, IS/OOS sealed before run); **no actual dates**
  set in this plan.

## 4. Required fields

### Per quote row
`venue_id_canonical` · `symbol_per_venue` · `symbol_canonical` ·
`exchange_send_ts` · `local_recv_ts` · `best_bid` · `bid_size` ·
`best_ask` · `ask_size` · `sequence_no_if_present`.

### Per order-book row (optional, L2 if source supports)
`venue_id_canonical` · `symbol_canonical` · `exchange_send_ts` · `side` ·
`level_index` · `price` · `size`.

### Per fee reference
`venue_id_canonical` · `instrument_class` · `maker_fee_bps` ·
`taker_fee_bps` · `schedule_date` · `schedule_url_or_local_pin`.

### Per funding row (only if perp extension authorized)
`venue_id_canonical` · `symbol_canonical` · `settlement_ts` ·
`funding_rate` · `funding_interval_seconds`.

### Per-row provenance (required)
`source_id` · `data_contract_version_pin` · `dataset_version_pin` ·
`ingest_pipeline_version`.

## 5. Manifest + QA requirements

- **Manifest:** must satisfy all 32 required fields of
  `arbitrage_dataset_manifest_v1.manifest_schema.required_future_manifest_fields`.
  Must pin the versions of **protocol / data contract / dataset manifest /
  QA harness spec / data source evaluation / sample dataset plan**.
  Freeze target: **FROZEN**. QA target: **QA_PASS** (or explicitly-accepted
  **QA_WARN**).
- **QA:** must satisfy `arbitrage_qa_harness_spec_v1` (all 8 QA check
  groups). Must run BEFORE any research use. Must produce a `qa_report.json`
  satisfying the 23-field future QA report schema.
- **QA_PASS does NOT imply** edge / profitability / live-readiness /
  authorization to backtest / promotion to ACTIVE / STRONG.

## 6. Storage plan

- **Root path pattern:** `data/arbitrage_research/<dataset_id>/<dataset_version>/`
- **Frozen subfolder:** `frozen/`
- **QA subfolder:** `qa/`
- **No network URL** allowed in `source_location`.
- **No write** to paper / live execution paths.
- **Checksums per file:** `sha256`, stored in `CHECKSUMS.txt`.
- The actual root path is set by future authorization.
- **No real data files are created in this bundle.**

## 7. Naming convention (examples only)

| Slot | Pattern | Example (label only) |
|---|---|---|
| `dataset_id` | `ARB_<CATEGORY_TAG>_<SYMBOL_TAG>_SAMPLE_V<NNN>` | `ARB_XSPOT_BTCUSDT_SAMPLE_V001` · `ARB_XSPOT_ETHUSDT_SAMPLE_V001` |
| `dataset_version` | monotonically-increasing integer starting at `001` | `001`, `002`, … |
| Manifest filename | `manifest.json` | — |
| Raw quote file | `quotes.csv` (parquet preferred) | — |
| Raw order book file (optional) | `order_book.csv` (parquet preferred) | — |
| Raw fee reference file | `fees.json` | — |
| Raw funding file (only if perp extension authorized) | `funding.csv` (parquet preferred) | — |
| QA report file | `qa_report.json` | — |
| Checksum file | `CHECKSUMS.txt` | — |
| Freeze record file | `FREEZE_RECORD.txt` | — |

**No real files are created in this bundle.**

## 8. Freeze plan (future, in a separate bundle)

1. Compute `sha256` per file; write `CHECKSUMS.txt`.
2. Author `manifest.json` with all 32 required future manifest fields
   populated.
3. Set `manifest.freeze_status = FROZEN` with `freeze_timestamp_utc`.
4. Re-verify `sha256` against `CHECKSUMS.txt`; mismatch invalidates the
   freeze.
5. Persist `FREEZE_RECORD.txt` with operator identity + UTC timestamp +
   reason.

**Frozen means** all of the following hold: `freeze_status == FROZEN`;
`freeze_timestamp` present and not in the future; all per-file checksums
stored and verifiable; `row_count_expected == row_count_actual` (or a
documented gap explains it); the manifest validates without warnings.

## 9. Approval gates (before any future data collection)

All of the following must be satisfied **before** any acquisition runs:

1. **Explicit operator authorization** — written message naming this plan
   and what is permitted.
2. **Named source class from Bundle 8** — one of A_archives / B_apis /
   C_paid_vendor / D_local_csv (NOT E web-scraped, NOT F manual).
3. **Exact source named** — vendor product / archive URL / file path.
4. **Exact venue names.**
5. **Exact symbols named.**
6. **Exact time window named** — ISO-8601 UTC start + end.
7. **Exact storage path named** — on-disk path under
   `data/arbitrage_research/...`.
8. **Protocol version referenced.**
9. **Data contract version referenced.**
10. **Dataset manifest version referenced.**
11. **QA harness spec version referenced.**
12. **Data source evaluation version referenced.**
13. **Sample dataset plan version referenced** (this document).
14. **No credentials unless separately approved.**
15. **No private keys.**
16. **No trading permissions.**
17. **No automatic scheduler.**
18. **No live or paper execution.**
19. **TOS / licensing review if applicable.**

## 10. Rejection rules

- Reject this plan as a basis for collection if source class is
  **E_web_scraped_or_unofficial_data** or
  **F_manually_copied_prices_or_screenshots**.
- Reject if `source_location` would be a live network URL at use time.
- Reject if the time window is **wider than the smallest realistic first
  slice** (avoid overcollecting).
- Reject if the symbol list is **broader than the smallest realistic first
  slice**.
- Reject if the manifest cannot be fully populated against
  `arbitrage_dataset_manifest_v1`.
- Reject if the QA harness cannot fully cover the planned data shape.
- Reject if any prior arbitrage validator (protocol / data contract /
  dataset manifest / qa harness / data source evaluation) currently FAILs.

## 11. Future collection steps (separately-authorized future bundle)

1. **source_approval** — operator authorizes a specific Bundle-8 source
   class instance.
2. **manifest_draft** — author a per-dataset manifest; `freeze_status`
   starts at DRAFT.
3. **collection_command_proposal** — write down the exact offline command
   the operator would run (no execution from this bundle).
4. **safety_review** — re-verify all approval gates in writing before any
   command runs.
5. **explicit_operator_authorization** — a SEPARATE authorization is the
   only way the acquisition step can run.
6. **data_collection_in_separate_bundle** — actual collection happens in a
   SEPARATE, separately-authorized bundle (never in this plan).
7. **checksum_generation** — sha256 per file → `CHECKSUMS.txt`.
8. **manifest_freeze** — `freeze_status=FROZEN` + `freeze_timestamp`.
9. **qa_run** — run the (future) harness implementation against the frozen
   dataset + manifest.
10. **qa_report** — persist `qa_report.json` per
    `arbitrage_qa_harness_spec_v1.report_schema`.
11. **research_use_only_if_QA_PASS_or_QA_WARN_with_explicit_approval** —
    never research-use a `QA_FAIL` / `BLOCKED` / `RETIRED` dataset; never
    research-use without a written approval if `QA_WARN`.

## 12. Forbidden actions in this bundle

- Do not fetch data in this bundle.
- Do not connect to any exchange.
- Do not call any external network endpoint.
- Do not place any order anywhere.
- Do not run any backtest.
- Do not process any dataset.
- Do not create any real data files.
- Do not create any credential file.
- Do not install any scheduler / cron / daemon.
- Do not modify paper / live execution files.
- Do not promote the arbitrage lane to ACTIVE / STRONG.
- Do not claim profitability or edge.

## 13. Required future artifacts

- Per-sample **data-acquisition memo** (named source + instance + symbols
  + venues + window + storage path + license / TOS pin + cost cap).
- Per-sample **manifest** under `arbitrage_dataset_manifest_v1` with all 32
  required-future-manifest fields populated.
- Per-sample **CHECKSUMS.txt** with sha256 per file (when `freeze_status`
  → FROZEN).
- Per-sample **FREEZE_RECORD.txt** with operator identity + UTC
  `freeze_timestamp`.
- Per-sample **QA report file** under `arbitrage_qa_harness_spec_v1`
  reaching QA_PASS or accepted QA_WARN.
- Per-sample **retirement memo** if the sample is later RETIRED.

## 14. PASS / WATCH / FAIL rules (for THIS plan)

- **PASS** — All required top-level sections present; `proposed_sample_scope`
  is TINY and conservative (1–2 symbols, narrow window, top-of-book
  preferred); naming convention + storage plan + freeze plan exist with no
  real files created; approval gates include explicit operator authorization
  AND all five upstream version pins (protocol / contract / manifest / qa /
  evaluation); future collection steps include
  `explicit_operator_authorization` and `data_collection_in_separate_bundle`;
  no safety flag True; no forbidden phrase.
- **WATCH** — Plan satisfied but at least one section is borderline (e.g.,
  symbol list at the upper edge of "tiny"); documented and re-checked.
- **FAIL** — Any required section missing; any safety flag True; storage
  plan permits a network URL; proposed scope wider than "tiny"; approval
  gates omit explicit operator authorization; future collection steps omit
  `explicit_operator_authorization` or `data_collection_in_separate_bundle`;
  any forbidden phrase present.

## 15. No-profit-claim policy

- **A sample dataset does not imply edge.**
- **A clean sample does not imply profitability.**
- **A price gap is not profit.**
- **Sample data cannot authorize trading.**
- **Sample data cannot authorize backtesting** unless a SEPARATE future
  backtest bundle is approved.

## 16. Safety boundaries (pinned, non-negotiable)

- Research-only. Planning / specification only.
- No broker control, no exchange connection, no API keys, no `.env`, no
  credential handling.
- No live trading. No paper-order execution. No order placement.
- No scheduler / background daemon. No external network calls in this
  plan's runtime.
- **No data fetch. No backtest. No dataset processing. No real data files
  created in this bundle.**
- Do not modify paper / live execution files.
- Do not claim profitability. Do not claim live-readiness. Do not claim
  STRONG evidence from this plan alone.
- A price gap is not profit. A sample does not imply edge.
