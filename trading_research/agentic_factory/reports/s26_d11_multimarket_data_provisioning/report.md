# S26-D11 — Multi-Market Data Provisioning (data only, no strategy run)

**Provisions clean daily OHLCV CSVs for the S26 multi-market protocol (ES, MES, MNQ)
from Databento, into `data_offline/` under the committed S26-D10 naming/schema. DATA
ONLY — the S26 strategy was NOT run, nothing was optimized, no engine/test/parameter
was changed.** NQ files were left untouched. This step only expands the reusable data
library; it does **not** interpret strategy edge (that is S26-D12).

- **Created:** 2026-05-30 · **Reference commit:** `483aee4` (S26-D10
  PROTOCOL_REGISTERED)
- **Authorization:** operator confirmed Databento access and willingness to pay; pull
  scoped to ES/MES/MNQ, 2013–2025, no 2026 data.

---

## 1. Source & toolchain

| Field | Value |
|---|---|
| Provider | Databento Historical API |
| Dataset | `GLBX.MDP3` (CME Globex) |
| stype_in | `continuous` |
| Schema | `ohlcv-1d` (daily bars) |
| Symbols | `ES.c.0`, `MES.c.0`, `MNQ.c.0` (continuous front-month, rank 0) |
| Window | 2013-01-01 → 2025-12-31 (hard cap; **no 2026**) |
| API call | `databento.Historical(key).timeseries.get_range(...).to_df()` |
| Key source | env `DATABENTO_API_KEY` — never printed or logged |
| Price scaling | `to_df()` returns float-scaled prices (validated vs known index levels) |

**Toolchain summary:**
- **ES** — single `get_range` over the full 2013–2025 window succeeded in one shot.
- **MES / MNQ** — the single-shot call hit **transient `502`/`504` gateway errors**
  (server-side, not data absence). Re-pulled **per-year (2019–2025) with up to 4
  retries + backoff**; all years then succeeded.
- Each market written as **one CSV per year** via the S26-D10 convention
  `data_offline/<sym>_c0_ohlcv_1d_<YYYY>.csv`. **Existing files are never
  overwritten** — NQ was not touched.

Schema written (matches existing NQ files exactly):
`ts_event,open,high,low,close,volume,symbol` · `ts_event` UTC ISO-8601
(e.g. `2020-06-01 00:00:00+00:00`).

---

## 2. Produced CSV list (27 files, all gitignored under `data_offline/`)

| Market | Files | Years |
|---|---|---|
| **ES** | 13 | 2013, 2014, …, 2025 |
| **MES** | 7 | 2019, 2020, …, 2025 |
| **MNQ** | 7 | 2019, 2020, …, 2025 |

---

## 3. Year-by-year coverage & QA audit

**ES (independent S&P market) — coverage FULL** · 2013-01-02 → 2025-12-31 · 4031 bars
(IS 3096 / OOS 935) · schema OK all years · **0 duplicate dates, 0 invalid OHLC, 0
missing values, max calendar gap 4 days, 0 gaps >10d.**

| Year | rows | | Year | rows | | Year | rows |
|---|---|---|---|---|---|---|---|
| 2013 | 306 | | 2018 | 312 | | 2023 | 310 |
| 2014 | 302 | | 2019 | 312 | | 2024 | 313 |
| 2015 | 312 | | 2020 | 312 | | 2025 | 312 |
| 2016 | 310 | | 2021 | 311 | | | |
| 2017 | 309 | | 2022 | 310 | | | |

**MES (proxy_micro of ES) — coverage PARTIAL_IS** · 2019-05-05 → 2025-12-31 · 2075 bars
(IS 1140 / OOS 935) · schema OK · **0 dup, 0 invalid, 0 missing, max gap 3 days, 0 gaps
>10d.** Per-year: 2019=207 (launched 2019-05-05), 2020=312, 2021=311, 2022=310,
2023=310, 2024=313, 2025=312.

**MNQ (proxy_micro of NQ) — coverage PARTIAL_IS** · 2019-05-05 → 2025-12-31 · 2075 bars
(IS 1140 / OOS 935) · schema OK · **0 dup, 0 invalid, 0 missing, max gap 3 days, 0 gaps
>10d.** Per-year identical shape to MES: 2019=207, 2020=312, 2021=311, 2022=310,
2023=310, 2024=313, 2025=312.

Coverage classes per the committed S26-D10 definitions (FULL / PARTIAL_IS / OOS_ONLY /
INSUFFICIENT / DATA_FAIL): **ES = FULL, MES = PARTIAL_IS, MNQ = PARTIAL_IS.** All three
clear the protocol floors (IS ≥ 500 bars, OOS ≥ 200 bars).

### Data-quality note (transparency)
Databento raised a `BentoWarning: reduced quality (degraded)` for a **small number of
source days** across all markets (examples: 2019-01-15, 2020-02-27/28, 2022-01-02,
2025-09-17/24, 2025-11-28). These bars are retained **as delivered**. They are
**source-condition flags, not duplicate/invalid-OHLC defects**, and do **not** trigger
the S26-D10 rejection rules (which key on duplicates, invalid OHLC, missing values, and
>25%-missing years — none of which fired). Flagged here so D12 can weigh them honestly.

---

## 4. Rejected files / years

**None.** Every produced file passed the S26-D10 QA gates: 0 duplicate dates, 0 invalid
OHLC rows, 0 missing values, no year missing >25% of sessions, and all schemas exact.
The earlier MES/MNQ single-shot `502`/`504` were **transient gateway errors**, resolved
by the per-year retry — they were **not** data-absence DATA_FAILs.

---

## 5. Is S26-D12 frozen robustness test now runnable?

**Yes — runnable, with a pre-registered ceiling of PARTIAL_SUPPORT.**
- **ES** provides a clean, FULL, genuinely **independent** market (S&P 500) — the one
  underlying beyond NQ that the committed D10 protocol identified as reachable.
- **MES** and **MNQ** provide **same-underlying corroboration** (PARTIAL_IS from
  2019-05-05); per the no-proxy rule they count as `proxy_micro`, **not** independent
  markets.
- Therefore exactly **one independent market beyond NQ** is available ⇒ by the
  committed D10 gates the **maximum attainable D12 verdict is PARTIAL_SUPPORT**, not
  ROBUST_SUPPORT (which would need a 2nd independent underlying / 3rd market).

---

## 6. Verdict — **DATA_PROVISIONED**

Clean daily data for ES (FULL) + MES/MNQ (PARTIAL_IS) is now in `data_offline/` under
the protocol convention, fully audited, zero QA rejections. **No strategy was run; no
edge was interpreted.** S26 remains not deployable; no paper/live recommendation.

---

## 7. Recommendation for S26-D12 (separate one-shot robustness test)

- Run the **frozen** S26-D2 engine (unchanged) **once** per market/window, judged
  **strictly** against the **pre-registered S26-D10 gates** — do not alter the gates
  after seeing results.
- Treat **ES** as the independent confirmation market; report **MNQ/MES** as
  same-underlying corroboration only (cannot upgrade past PARTIAL_SUPPORT).
- For the PARTIAL_IS micros, **document the 2019-05-05 start** and judge their
  shortened IS honestly (they meet the floors but cover a different, shorter regime
  span than ES/NQ).
- Report per market/window: trade count, total R, avg R, win rate, **max drawdown R**,
  profit factor, top-3 winner dependence, positive-without-top-3, per-year R, and the
  degraded-day caveat.
- If ES fails to confirm NQ → **NQ_ONLY_SUPPORT**; if ES confirms → **PARTIAL_SUPPORT**
  (the realistic ceiling here). Either way, **no deployment**.

---

### Notes of record
- Data provisioning only — no strategy run, no optimization, no engine/test/parameter
  change. Frozen engine untouched.
- Databento daily continuous-c0 bars; ES one-shot, MES/MNQ per-year-with-retry after
  transient gateway errors. API key read from env only, never logged.
- 27 CSVs written under `data_offline/` (gitignored). NQ files NOT overwritten.
  Donchian/S23/S24 and `templates/base.html` untouched.
- Temp provisioning scripts (`_s26_d11_provision.py`, `_s26_d11_retry_micros.py`,
  `_s26_d11_build_report.py`) are generated artifacts — deleted after this report;
  the data CSVs are the durable deliverable.
