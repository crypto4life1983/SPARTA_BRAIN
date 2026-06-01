# SPARTA Arbitrage Data Source Evaluation Memo v1

> **Research-only. Memo / specification only.**
> No broker control. No live trading. No paper-order execution. No exchange
> connection. No API keys. No `.env`. No credential handling. No scheduler /
> background daemon. **No external network calls. No data fetch. No backtest.
> No dataset processing in this bundle.** This document is a written
> assessment of which data-source classes could be acceptable for future
> arbitrage research and what approval gates must be met before any future
> data collection is authorized.

**Evaluation id:** `arbitrage_data_source_evaluation_v1` · **version:** `1.0`

**Companion documents:**
[`arbitrage_research_protocol_v1`](../arbitrage_research_protocol_v1/protocol.md) ·
[`arbitrage_data_contract_v1`](../arbitrage_data_contract_v1/data_contract.md) ·
[`arbitrage_dataset_manifest_v1`](../arbitrage_dataset_manifest_v1/dataset_manifest.md) ·
[`arbitrage_qa_harness_spec_v1`](../arbitrage_qa_harness_spec_v1/qa_harness_spec.md).

---

## 1. Research objective

Evaluate which data-source **classes** could later be acceptable for
arbitrage research, what risks each carries, and what strict approval gates
must be met **before** any future data collection is authorized. This memo
does not fetch, connect, process, backtest, or authorize trading. It is a
planning input only.

### Supported arbitrage categories this memo serves

This memo evaluates data sources for the five categories defined by
`arbitrage_research_protocol_v1`:

- **A.** Cross-exchange spot arbitrage.
- **B.** Spot-perp basis / funding arbitrage.
- **C.** Triangular arbitrage.
- **D.** Futures calendar / basis arbitrage.
- **E.** Statistical / relative-value mispricing (**NOT pure arbitrage**).

Word discipline from prior bundles is carried verbatim: category E is
**RELATIVE_VALUE**, not arbitrage. The source-class evaluation that follows
applies across all five.

## 2. Source classes evaluated

### A. Exchange public historical archives
**Examples:** Historical market-data downloads published by exchanges
(per-venue daily/monthly zip dumps).
- **Pros:** authoritative venue source · offline once downloaded · usually
  research-permitted · fee schedule + tick/lot lives alongside.
- **Cons:** venue-specific coverage · often coarser than live tick (e.g.,
  1m bars not L1 ticks) · L2 depth rarely included · funding-rate series
  often in a separate archive.
- **Timestamp-quality risk:** GOOD with `exchange_send_ts`; MEDIUM for
  minute-bars-only.
- **Coverage risk:** MEDIUM — gaps around launches / outages / renames.
- **Fee-schedule mismatch risk:** MEDIUM — pin the dated schedule.
- **Order-book depth limitations:** L2 typically absent; depth-at-size
  tests need a separate L2 source OR a documented L1-only haircut.
- **Survivorship / delisting risk:** MEDIUM.
- **Future approval requirements:** operator names the archive snapshot;
  TOS confirmed for window; manifest + QA produced; no live API.

### B. Exchange public APIs (future-only; **NOT authorized now**)
**Examples:** REST or WebSocket endpoints exposed by exchanges.
- **Pros:** sub-second timestamps · L2 / depth often available · closest
  to venue match engine.
- **Cons:** requires network at use time — **THIS MEMO does not
  authorize that** · rate-limit / IP-ban / TOS risk even keyless · most
  arbitrage-grade endpoints require API keys (credential handling not
  permitted here) · clock-skew not yet measured per venue.
- **Strict no-use in this bundle:** true.
- **Keyless public endpoint risks:** rate-limit / 429 ban mid-session;
  ToS may forbid systematic harvesting; freshness vs. consistency
  trade-offs vary per venue.
- **Rate limits:** per-venue; must be discovered and pinned before any
  future request.
- **Timestamp / latency issues:** publish-to-recv latency must be
  measured and recorded as a haircut.
- **Legal / TOS concerns:** systematic collection often restricted;
  jurisdiction may add limits; derived-dataset licensing not automatic.
- **Future authorization requirements:** SEPARATE explicit P2
  authorization · named venue / endpoint / symbols / window / rate-limit
  / max-bytes-cap · no credentials unless its own authorization adds
  `local_secrets/` handling · TOS review attached.

### C. Paid market data vendors
**Examples:** Generic professional vendors (e.g., Databento / Tiingo /
Polygon / Kaiko-class).
- **Pros:** cleaner provenance + symbol canonicalization · L2 / trades /
  funding often available · explicit research-use license · vendor-side
  outage / re-fill documented.
- **Cons:** real research expense · coverage gaps on small / new pairs ·
  vendor normalization can differ from venue-side · live-API flows still
  require keys (operator-side offline export flows are SAFER).
- **Cost / licensing / coverage / depth / timestamp considerations** —
  named, dated, attached.
- **Future approval requirements:** named vendor + dated license · cost
  cap in the authorization message · offline export path preferred ·
  manifest + QA as usual.

### D. Existing local CSV datasets
**Examples:** Files already on the operator's machine.
- **Pros:** no network · already on disk · can satisfy contract +
  manifest + QA without any acquisition.
- **Cons:** vague provenance · schema may not match contract · manual-
  edit possibility · older timestamps may not satisfy sub-second
  requirements.
- **Provenance risk:** HIGH unless a written memo + sha256 attest the
  files first.
- **Schema mismatch risk:** MEDIUM-HIGH — needs a normalization step
  pinned in the manifest.
- **Manual-edit risk:** PRESENT — mitigated by sha256 + a written
  "no manual edits since" attestation.
- **Timestamp risk:** MEDIUM.
- **Qualification path:** provenance memo → sha256 → contract
  normalization → QA harness → QA_PASS / accepted QA_WARN.

### E. Web-scraped or unofficial data
**Examples:** Scraping a venue's HTML; pulling from undocumented mirrors.
- **Pros:** free; sometimes the only place to find a particular series.
- **Cons:** unstable (format changes silently corrupt) · usually
  violates TOS for systematic collection · timestamp unreliable · depth
  / fees / funding rarely present · row-level provenance hard to attest.
- **Default recommended status:** **REJECTED** for evidence-grade
  arbitrage research. **WATCH-with-warning** only for anecdotal
  exploration that NEVER produces a PASS verdict.
- **Explicit reasons to reject:** unstable; legal / TOS risk; timestamp
  unreliable; missing depth / fees / funding; not suitable for
  arbitrage evidence by default.

### F. Manually copied prices or screenshots
**Examples:** Operator-typed quotes, screenshots, hand-written ticker
sheets.
- **Pros:** useful for anecdotal flagging only.
- **Cons:** not reproducible byte-for-byte · cannot be tied to a venue
  clock · no fees / depth / funding · QA category checks fail by
  construction.
- **Rejected for quantitative validation:** true.
- **Allowed only for anecdotal notes:** operator memos may cite a
  screenshot as the trigger for a research question. The screenshot
  itself NEVER counts as evidence and NEVER moves any candidate to
  ACTIVE / STRONG.

## 3. Decision matrix

| Source class | `allowed_now` | `future_possible` | Order book | Fees | Funding | Timestamp | Legal/TOS | Cost | Evidence | **Status** |
|---|:-:|:-:|---|---|---|---|---|---|---|:-:|
| A. Exchange historical archives | **false** | true | L1 (L2 rarely) | with pinned schedule | partial | medium–high | low–med | low | medium | **ACCEPTABLE** |
| B. Exchange public APIs | **false** | true | L1/L2 often | reference required | often | high | medium–high | low–medium | high (if properly authorized) | **WATCH** |
| C. Paid market-data vendors | **false** | true | L1/L2 often | reference required | often | high | low (licensed) | medium–high | high (licensed + pinned) | **PREFERRED** |
| D. Existing local CSV | **false** | true | varies | varies | varies | medium | low–med | low | medium (if provenance) | **ACCEPTABLE** |
| E. Web-scraped / unofficial | **false** | false | none / fragile | rarely | rarely | low | **high** | low–med | low | **REJECTED** |
| F. Manually copied / screenshots | **false** | false | no | no | no | low | low | none | none | **REJECTED** |

`allowed_now` is **false** for **every** real data-fetching source
class — Bundle 8 does not authorize any fetch. `future_possible` is **true**
only for A, B, C, D.

## 4. Approval gates (before any future data collection)

All of the following must be satisfied:

1. **Explicit operator authorization** — written message in the SPARTA
   control surface naming this bundle and what is permitted.
2. **Exact source named** — source class **and** the specific instance
   (venue archive URL, vendor product SKU, file path, etc.).
3. **Exact symbols named** — per-venue symbol list.
4. **Exact venues named** — per-source venue list.
5. **Exact time window named** — ISO-8601 UTC start + end.
6. **Data contract version referenced** — `arbitrage_data_contract_v1`
   version pin.
7. **Dataset manifest version referenced** — `arbitrage_dataset_manifest_v1`
   version pin.
8. **QA harness spec version referenced** — `arbitrage_qa_harness_spec_v1`
   version pin.
9. **Storage path named** — on-disk path where the offline data will
   live; never a network URL.
10. **No credentials unless separately authorized** — credential handling
    requires its own explicit authorization message.
11. **No private keys.**
12. **No trading permissions** — the authorization message MUST NOT
    grant order, paper, or live trading permissions.
13. **No automatic scheduler** — one-shot operator-driven run.
14. **No live or paper execution.**
15. **ToS / licensing review required if applicable.**

## 5. Rejection rules

- Any source whose use requires a network call from THIS memo's runtime
  → REJECTED for THIS bundle.
- Any source requiring an API key / OAuth / `.env` → REJECTED unless a
  separate authorization adds credential handling under gitignored
  `local_secrets/`.
- Manually copied prices / screenshots → REJECTED for quantitative
  validation.
- Web-scraping / unofficial mirrors → REJECTED for evidence;
  WATCH-with-warning only for anecdotal exploration.
- Any source whose TOS forbids research use → REJECTED.
- Any source whose provenance cannot be attested row-by-row → REJECTED
  for evidence.
- Any source whose OOS window was peeked before sealing → REJECTED.

## 6. Required metadata

- `source_class` (A / B / C / D / E / F).
- `source_instance_name` (venue, vendor product, file path).
- `license_or_tos_pin` (text or URL + date).
- `expected_coverage` (symbols / venues / time window).
- `expected_timestamp_quality` (per-venue clock + skew).
- `expected_depth_availability` (L1 / L2 / trades / funding).
- `expected_fee_schedule_pin`.
- `expected_cost_in_USD`.
- `expected_storage_path`.
- `operator_provenance_attestation`.
- `approval_message_reference`.

## 7. Expected risks

ToS / legal · coverage gaps · timestamp / clock-skew · missing L2 depth ·
vendor-side normalization disagreement · manual edits · cost overruns ·
survivorship / delisting bias · OOS leakage.

## 8. Source-quality dimensions

`timestamp_quality` · `depth_availability` · `fee_schedule_attached` ·
`funding_attached` · `provenance_attestable_per_row` ·
`license_research_use_permitted` · `cost_to_operator` ·
`reproducibility`.

## 9. Future allowed / forbidden source plan

**Allowed (future, with their own authorization each):**

1. **Preferred:** operator-supplied paid-vendor offline export
   (Class C) for the chosen first category, on a narrow window (1–3 months),
   smallest realistic symbol set.
2. **Alternative:** venue public historical archive (Class A) provided
   TOS permits research use for the window AND the archive carries the
   needed L1 / depth / funding fields.
3. **Backup:** qualified existing-local CSV (Class D) with provenance
   memo + sha256 + contract pin + QA_PASS first.

**Forbidden (future-plan as well, until a SEPARATE bundle changes it):**

- Class B until a separate authorization adds rate-limit / TOS / credential
  / cap policy.
- Class E for evidence — only WATCH-with-warning for anecdotal exploration.
- Class F for any quantitative claim.

## 10. Required future artifacts

- Per-acquisition **data acquisition memo** (named source + instance +
  symbols + venues + window + storage path + license/TOS pin + cost cap).
- Per-acquisition **manifest** under `arbitrage_dataset_manifest_v1`.
- Per-acquisition **QA report** under `arbitrage_qa_harness_spec_v1`
  reaching QA_PASS or accepted QA_WARN.
- Per-acquisition **cost-model snapshot** tied to the chosen source.
- Per-acquisition **closeout memo** if the source is later RETIRED.

## 11. PASS / WATCH / FAIL rules (for THIS memo)

- **PASS** — All required top-level sections present; all 6 source classes
  evaluated; decision matrix has all required fields for every row;
  `allowed_now` is False for every real data-fetching source class;
  manually-copied and web-scraped sources are REJECTED for evidence;
  approval gates include explicit operator authorization; no safety flag
  True; no forbidden phrase.
- **WATCH** — Memo satisfied but at least one row is borderline (e.g., a
  vendor's licensing terms need re-verification); documented and
  re-checked.
- **FAIL** — Any required section missing; any safety flag True; any
  source class missing; `allowed_now` True for a real data-fetching
  source; any required decision-matrix field absent; any forbidden phrase
  present.

## 12. No-profit-claim policy

- **A data source does not imply edge.**
- **Clean data does not imply profit.**
- **Price differences are not profit.**
- **Source approval does not authorize trading.**
- **Source approval does not authorize backtesting** unless a SEPARATE
  bundle approves a test.

## 13. Safety boundaries (pinned, non-negotiable)

- Research-only. Memo / specification only.
- No broker control, no exchange connection, no API keys, no `.env`, no
  credential handling.
- No live trading. No paper-order execution. No order placement.
- No scheduler / background daemon. No external network calls in this
  memo's runtime.
- **No data fetch. No backtest. No dataset processing in this bundle.**
- Do not modify paper / live execution files.
- Do not claim profitability. Do not claim live-readiness. Do not claim
  STRONG evidence from this memo alone.
- A price gap is not profit. Source approval is not edge. Apparent edge ≠
  profit.
