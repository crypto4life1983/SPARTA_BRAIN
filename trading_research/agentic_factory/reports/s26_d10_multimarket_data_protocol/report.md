# S26-D10 — Pre-registered Multi-Market Data Protocol (specification only)

**Defines the fair data requirements and the FUTURE pass/fail gates for an S26
multi-market robustness test (S26-D11), registered BEFORE any new MNQ/ES/MES data is
sourced, run, or viewed.** This mirrors the D4-before-D5 pre-registration discipline.
**SPECIFICATION ONLY — not a backtest.** No data was fetched, decoded, transcoded, or
inspected; no strategy was run; the engine, tests, and parameters are unchanged.

- **Created:** 2026-05-30 · **Reference commit:** `a9cbfaa` (S26-D9
  DATA_LIMITED_INCONCLUSIVE)
- **Frozen engine (for D11):** `engine/trend_sr_ema_rsi_daily.py` — UNCHANGED.
- Prior chain: D3 IS_CONTINUE (marginal) · D5 OOS PASS · D6 ENTRY_EDGE_INCONCLUSIVE ·
  D7 SEQUENCE_RISK_INCONCLUSIVE · D8 CONCENTRATED_SUPPORT · D9
  DATA_LIMITED_INCONCLUSIVE (only NQ had clean local data).

---

## 1. Required markets & independence

| Market | Underlying | Role | Counts as independent? |
|---|---|---|---|
| **NQ** | Nasdaq-100 | reference (already evaluated D3–D9) | no — it's the thing being tested |
| **MNQ** | Nasdaq-100 | proxy_micro of NQ | **no** — same underlying |
| **ES** | S&P 500 | independent market | **yes** |
| **MES** | S&P 500 | proxy_micro of ES | **no** — same underlying |

**Independence is counted by distinct underlying index, not by ticker.** `{NQ or MNQ}`
= one underlying (Nasdaq); `{ES or MES}` = one underlying (S&P). **Critical honest
constraint:** from this symbol set there is at most **one independent market beyond
NQ** (the S&P, via ES/MES). So the **ceiling verdict reachable from {NQ,MNQ,ES,MES} is
PARTIAL_SUPPORT** — ROBUST_SUPPORT would require adding a *third* distinct underlying
(e.g. a non-equity-index) in a future protocol amendment.

---

## 2. Accepted file names

Pattern: **`data_offline/<sym>_c0_ohlcv_1d_<YYYY>.csv`**, one file per year, `c0` =
continuous front-month roll-adjusted series (same convention as the committed NQ
files). Tokens: NQ→`nq`, MNQ→`mnq`, ES→`es`, MES→`mes`.

Examples: `data_offline/mnq_c0_ohlcv_1d_2019.csv`, `data_offline/es_c0_ohlcv_1d_2021.csv`,
`data_offline/mes_c0_ohlcv_1d_2024.csv`.

D11 discovers files **only** by this glob; `data_offline/` is the only data source.

---

## 3. Accepted OHLCV schema

- **Required columns:** `ts_event, open, high, low, close` (header case-insensitive).
- **Optional:** `volume, symbol`.
- **Types:** OHLC float; `ts_event` ISO-8601 parseable by `datetime.fromisoformat`.
- Matches the existing loader `load_daily_bars(csv_path, timestamp_column='ts_event')`
  exactly — no loader change needed.
- A file missing a required column / with unparseable `ts_event` / non-numeric OHLC is
  **REJECTED**.

---

## 4. Timestamp convention

Daily (`1d`) bars, one row per trading day, `ts_event` ISO-8601, streamed sorted
ascending (loader already sorts). Timezone naive/exchange-local as in the NQ files and
consistent within a market.

---

## 5. Windows & minimum coverage

| Window | Years | Min bars | Notes |
|---|---|---|---|
| IS | 2013–2022 | ≥ 500 | use where available; standalone stream |
| OOS | 2023–2025 | ≥ 200 | fresh/holdout; standalone stream |

- IS and OOS streamed **separately per market** — no pooling; D11 runner must hard-assert
  no IS/OOS file overlap (same as D5/D9).
- Per market: ≥ 750 total bars, ≥ 2 OOS years present, **≥ 20 trades** for a window to
  count as a fair confirmation (mirrors D4/D5 n≥20, ideal ≥30).
- Below a floor → window flagged **INSUFFICIENT** (bars) or **LOW_SAMPLE** (trades) and
  excluded from upgrade counting.

### Partial-window coverage (MNQ/MES launched ~2019)

MNQ and MES micro contracts launched in **2019** and therefore **cannot** have a full
2013–2022 IS. D11 must **document the actual available start date** (first `ts_event`)
and classify coverage:

| Class | Meaning |
|---|---|
| FULL | spans the required window above floors |
| **PARTIAL_IS** | IS present but starts after 2013 (e.g. MNQ/MES ~2019); report start date; usable only if it still meets the IS bar floor and ≥20 trades |
| OOS_ONLY | no usable IS, only 2023–2025 |
| INSUFFICIENT | below bar/trade floor |
| DATA_FAIL | no matching clean files |

A PARTIAL_IS market may still confirm if its shortened IS **and** its OOS each meet
floors and the per-confirming thresholds — but the shortened IS must be flagged so the
comparison is honest. **A short window is never backfilled with the big-contract's
earlier data** (that violates the no-proxy rule).

---

## 6. Gap / duplicate rejection rules

- **Duplicate dates:** max 0 → else REJECT window.
- **Invalid OHLC rows** (high<low, any OHLC≤0, high<max(open,close), low>min(open,close)):
  max 0 → else REJECT window.
- **Calendar gaps:** weekends/holidays expected; a gap >10 consecutive calendar days
  *within* a covered year → GAP_WARNING; a year missing >25% of its ~252 expected
  sessions → that year REJECTED for that market.
- **No interpolation:** missing bars are reported, never filled or synthesized.
- Every rejection is logged in the D11 report with its exact reason — nothing dropped
  silently.

---

## 7. No-proxy rule

- **MNQ may NOT be treated as NQ; MES may NOT be treated as ES** for *independent*
  confirmation. A micro is a same-underlying replica, not a new market.
- A micro **may** be run and reported, but **must** be marked `role=proxy_micro` and
  **excluded from the independent-market count**.
- Forbidden: substituting one symbol's data for another, relabeling, averaging a micro
  into its big contract, or counting NQ+MNQ (or ES+MES) as two independent markets.

---

## 8. Symbol-to-loader convention

| Symbol | Glob | Role | Independent |
|---|---|---|---|
| NQ | `data_offline/nq_c0_ohlcv_1d_*.csv` | reference | no |
| MNQ | `data_offline/mnq_c0_ohlcv_1d_*.csv` | proxy_micro_of_NQ | no |
| ES | `data_offline/es_c0_ohlcv_1d_*.csv` | independent_market | **yes** |
| MES | `data_offline/mes_c0_ohlcv_1d_*.csv` | proxy_micro_of_ES | no |

D11 uses a **thin discovery/streaming adapter** that reuses `load_daily_bars` +
`simulate` + `summarize` UNCHANGED. If a symbol needs a different timestamp column, that
is a data-prep defect to **report first**, not silently adapt.

---

## 9. Future S26-D11 classification gates (pre-registered)

Evaluated with downgrade precedence: **WEAK_OR_NO_SUPPORT → DATA_LIMITED_INCONCLUSIVE →
NQ_ONLY_SUPPORT → PARTIAL_SUPPORT → ROBUST_SUPPORT** (final label = highest tier fully
met with no stronger downgrade firing).

| Verdict | Conditions |
|---|---|
| **ROBUST_SUPPORT** | ≥ **2 independent** markets beyond NQ runnable & confirming (IS>0 & OOS>0, positive without top-3, no single-year >50%, floors met). **Unreachable from this symbol set** (only 1 independent underlying available) — needs a 3rd underlying added later. |
| **PARTIAL_SUPPORT** | exactly **1 independent** market beyond NQ runnable & confirming. The realistic best case here (S&P via ES confirming NQ). Micro (MNQ/MES) results may corroborate but do not upgrade past this. |
| **NQ_ONLY_SUPPORT** | ≥1 independent market was **runnable** (clean, met floors) but **failed to confirm** (IS≤0 or OOS≤0, or winner-dependent, or single-year-dominated), while NQ stays positive. The edge was tested off-NQ and did not transfer. |
| **DATA_LIMITED_INCONCLUSIVE** | <1 independent market runnable (all DATA_FAIL / REJECTED / INSUFFICIENT / LOW_SAMPLE). The transfer question can't be fairly answered. **This is today's D9 state** and the default until clean independent data exists. |
| **WEAK_OR_NO_SUPPORT** | frozen logic non-positive across available markets (incl. NQ degrading), OR every runnable independent market fails and results hinge on one lucky cluster. |

### Minimum evidence thresholds (per confirming market)

- **IS total R > 0** and **OOS total R > 0** (OOS absent only with a documented reason;
  absent OOS cannot count as confirmation).
- **Positive without top-3 winners** — else flagged winner-dependent and downgraded.
- **No single year > 50%** of that market's window net — else downgrade one tier.
- **Must report for every market/window** (including rejected/insufficient, with reason):
  trade_count, total_r, avg_r, win_rate, **max_drawdown_r**, profit_factor,
  top3_winner_r, without_top3_r, positive_without_top3, per_year_r, data_coverage,
  qa_flags.
- **Reporting floor:** max drawdown (R) and trade count are mandatory for every
  market/window.

---

## 10. Verdict — **PROTOCOL_REGISTERED**

This step registers the protocol and the future gates only. No market was run, no data
fetched/decoded/inspected, no parameters touched. **S26 remains not deployable; no
paper/live recommendation.**

---

## 11. Recommendation for S26-D11 (data provisioning + test)

1. **Source clean offline daily CSVs** for ES (full 2013–2025 if possible) and, as
   same-underlying corroboration, MES and MNQ (PARTIAL_IS from ~2019 expected). Place
   them in `data_offline/` under the exact naming convention above. **No fetch inside the
   factory** — provisioning is a manual, offline, out-of-band step; D11's *run* stays
   offline-only.
2. **Honest expectation:** the best attainable verdict from {NQ,MNQ,ES,MES} is
   **PARTIAL_SUPPORT** (one independent underlying, the S&P). If ROBUST_SUPPORT is the
   real goal, amend this protocol first to add a third distinct underlying.
3. **Run D11 once**, frozen engine unchanged, judged strictly against these gates; do not
   alter the gates after seeing data.
4. If clean independent data still can't be sourced, S26 robustness stays
   **DATA_LIMITED_INCONCLUSIVE** and the branch is held — **not** promoted on
   single-market NQ evidence.

---

### Notes of record
- Specification only — no backtest, no data run, no fetch/decode, no engine/test change,
  no parameter change.
- Pre-registered BEFORE any MNQ/ES/MES data is run or viewed (D4-before-D5 discipline).
- Key constraint recorded honestly: {NQ,MNQ,ES,MES} → at most one independent underlying
  beyond NQ ⇒ PARTIAL_SUPPORT ceiling.
- No temp runner or generated artifact produced. Donchian/S23/S24 and templates/base.html
  untouched.
