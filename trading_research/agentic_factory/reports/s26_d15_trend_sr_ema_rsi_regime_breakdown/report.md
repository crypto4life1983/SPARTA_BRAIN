# S26-D15 — Regime Breakdown (frozen engine, validation only)

**Analyzes S26 performance by regime (volatility, year/period, trend) on the two primary
markets NQ and ES, using the FROZEN engine and existing daily CSVs. VALIDATION ONLY — no
optimization, no parameter change, no strategy rule change, no new filters, no source/
engine/test change. Regime thresholds are fixed mechanically (IS tertiles), never chosen
after seeing OOS.**

- **Created:** 2026-05-30 · **Reference commit:** `ff6b779` (S26-D14 gate design)
- **Frozen engine:** `engine/trend_sr_ema_rsi_daily.py` — UNCHANGED.
- **Faithfulness:** the per-window overalls below reproduce the committed D3/D5/D12 numbers
  exactly, confirming the regime tags sit on the real frozen trade lists.

---

## 1. S26 current status

- **RESEARCH_CANDIDATE only.**
- **NOT paper-ready.**
- **NOT live-ready.** (Not deployable.)

This step is diagnostic. It produces **no** trading recommendation.

## 2. Method (fixed, non-optimized)

- **Data:** `data_offline/` daily CSVs (gitignored). NQ/ES 2013–2025, MNQ/MES 2019–2025. No
  2026. No data file modified.
- **Windows:** IS 2013–2022, OOS 2023–2025, streamed **separately per market** (same as
  D3/D5/D12).
- **Trend regime — DEGENERATE by construction:** every entry requires
  `close>EMA200 AND EMA50>EMA200`, so **100% of trades are bull-stack**. The trend filter
  *is* the entry rule; it cannot discriminate trades. (Confirmed: bull_stack holds for all.)
- **Volatility regime:** `ATR20/close` at the **signal bar**; low/mid/high split by the
  33rd/67th percentile computed **mechanically from each market's IS trades only**, then the
  **same thresholds applied to OOS**. No threshold chosen after seeing OOS.
- **Year regime:** tagged by exit/realization year (matches prior `year_R` convention).

## 3. NQ regime breakdown (reference primary)

IS vol thresholds (ATR%/close): t33 = 1.098%, t67 = 1.467%.

**IS 2013–2022** — overall 117 trades, +7.6536R, PF 1.2016, win 39.3%, max DD 10.5943R.

| Vol regime | n | Total R | PF | Win% | Share of net |
|---|---|---|---|---|---|
| low | 39 | +1.2853 | 1.0848 | 28.2% | 16.8% |
| **mid** | 39 | **+7.1403** | 1.5527 | 43.6% | **93.3%** |
| high | 39 | **−0.7720** | 0.9219 | 46.2% | **−10.1%** |

**OOS 2023–2025** — overall 32 trades, +7.9990R, PF 1.7694, win 53.1%, max DD 2.1827R.

| Vol regime | n | Total R | PF | Win% | Share of net |
|---|---|---|---|---|---|
| low | 0 | 0.0 | — | — | 0% |
| **mid** | 17 | **+6.7393** | 2.2043 | 47.1% | **84.3%** |
| high | 15 | +1.2597 | 1.2624 | 60.0% | 15.8% |

- **NQ year R (IS):** 2013 +3.29, 2014 −1.25, 2015 −2.73, 2016 −4.45, 2017 +4.29, 2018
  +0.35, 2019 +1.78, 2020 +4.82, 2021 +2.54, 2022 −0.99 (6/10 positive).
- **NQ year R (OOS):** 2023 +0.65 (8.2%), **2024 +4.93 (61.7%)**, 2025 +2.41 (30.1%).
- **NQ drawdown clusters:** IS worst **10.59R across 2014–2016** (34-trade span); OOS worst
  2.18R in 2025 (4-trade span, small).
- **NQ reading:** profit concentrated in **mid-vol**; **high-vol is net negative** (PF
  0.92). OOS leans on 2024.

## 4. ES regime breakdown (independent primary)

IS vol thresholds (ATR%/close): t33 = 0.909%, t67 = 1.167%.

**IS 2013–2022** — overall 125 trades, +7.6725R, PF 1.2003, win 38.4%, max DD 16.7281R.

| Vol regime | n | Total R | PF | Win% | Share of net |
|---|---|---|---|---|---|
| low | 42 | **−0.4850** | 0.9727 | 33.3% | **−6.3%** |
| mid | 41 | +1.9807 | 1.1762 | 34.2% | 25.8% |
| **high** | 42 | **+6.1768** | 1.6626 | 47.6% | **80.5%** |

**OOS 2023–2025** — overall 27 trades, +11.4584R, PF 2.2352, win 59.3%, max DD 2.0697R.

| Vol regime | n | Total R | PF | Win% | Share of net |
|---|---|---|---|---|---|
| low | 4 | +2.0000 | 2.0000 | 50.0% | 17.5% |
| mid | 15 | +4.8370 | 1.9541 | 60.0% | 42.2% |
| high | 8 | +4.6214 | 3.0943 | 62.5% | 40.3% |

- **ES year R (IS):** 2013 +3.91, 2014 −3.55, 2015 −4.59, **2016 −8.34**, 2017 +7.01, 2018
  −0.79, 2019 +3.61, 2020 +5.05, 2021 +5.76, 2022 −0.38.
- **ES year R (OOS):** 2023 −0.93 (−8.1%), 2024 +4.05 (35.3%), **2025 +8.34 (72.8%)**.
- **ES drawdown clusters:** IS worst **16.73R across 2014–2016** (49-trade span, deep); OOS
  worst 2.07R in 2024 (3-trade span, small).
- **ES reading:** profit concentrated in **high-vol**; **low-vol is slightly negative**.
  OOS heavily leans on 2025.

## 5. Optional proxy/micro notes (descriptive only — NOT independent)

MNQ (proxy of NQ) and MES (proxy of ES) are same-underlying micros, PARTIAL_IS from
2019-05-05; they cannot change the verdict. Their shortened IS spans a different regime
window and their own ATR%-tertiles differ, so their per-regime splits are not comparable to
the full-history primaries. Headline: MNQ OOS +7.68R (PF 1.72, 2024 = 64% of net), MES OOS
+11.79R (PF 2.33, 2025 = 74% of net) — same recent-year lean as their big contracts.

## 6. Year-by-year concentration

OOS profit is **single-year-dominated on both primaries**: NQ 2024 = 61.7% of OOS net; ES
2025 = 72.8% of OOS net. IS is more distributed (6/10 positive years on NQ; ES carried by
2013/2017/2019/2020/2021) but both endured a sustained **2014–2016 losing stretch**.

## 7. Volatility regime concentration

**The defining finding: the volatility regime that carries profit is inconsistent across the
two primary markets.**
- **NQ:** profit in **MID** vol; **HIGH** vol net negative (−0.77R, PF 0.92).
- **ES:** profit in **HIGH** vol; **LOW** vol slightly negative (−0.49R, PF 0.97).

So the edge does **not** live in the same volatility regime across NQ and ES — a mixed /
contradictory split rather than one consistent profitable regime. (OOS is more balanced on
ES across mid/high; NQ OOS has zero low-vol entries because 2023–2025 ran hotter than the
IS-defined low band.)

## 8. Trend regime concentration

**Degenerate.** Every entry is bull-stack by construction (the trend filter is the entry),
so 100% of trades fall in one trend regime and the axis cannot discriminate. Recorded for
completeness, not used in the verdict.

## 9. Drawdown cluster notes

Both markets' **worst IS drawdown clusters coincide in 2014–2016** (NQ 10.59R / 34 trades;
ES 16.73R / 49 trades) — the choppy, non-trending mid-decade range was the hardest regime
for a pullback-long edge on both. OOS drawdowns are small on both (≤2.2R).

## 10. Final D15 verdict — **REGIME_RISK_INCONCLUSIVE**

- **Not REGIME_RISK_ACCEPTABLE:** the volatility-regime profile is inconsistent across NQ vs
  ES (high-vol negative on NQ, high-vol best on ES), and OOS profit is single-year-dominated
  on both markets — cannot cleanly call regime risk acceptable.
- **Not REGIME_RISK_FAIL:** no major regime *consistently* destroys the strategy across both
  markets; ES does **not** contradict NQ in net direction (both IS and OOS positive); the
  shared 2014–2016 drawdown still recovered to net positive.
- **Not a clean REGIME_RISK_CONCENTRATED:** profit is **not** isolated to one tiny regime —
  it spreads across mid+high volatility and several positive years. The D14 hard blocker
  *"profit only from one narrow regime"* did **not** fire. But per-regime samples are small
  after splitting and the volatility split is mixed/contradictory between markets, so the
  honest call is **INCONCLUSIVE with flagged concentration cautions**.

**Flags carried forward:** (1) recent-year carries most OOS profit (NQ 2024 61.7%, ES 2025
72.8%); (2) the profitable volatility regime differs by market (NQ mid, ES high); (3) a
vol cell goes negative on each market (NQ high, ES low); (4) deep shared 2014–2016 IS
drawdown; (5) small per-regime samples.

## 11. Does D15 block or permit D16?

**Permits D16 — does not block.** No D14 hard blocker fired (profit is not from one narrow
regime; ES does not contradict NQ). REGIME_RISK_INCONCLUSIVE allows proceeding **cautiously**
to **S26-D16 walk-forward / rolling-window stability**, which is precisely the test to
resolve the temporal / single-year concentration this step flagged. **This is not a
clearance to paper trade.**

## 12. Trading recommendation

**NONE.** No deployment, no paper, no live. **S26 remains a RESEARCH_CANDIDATE.**

---

### Notes of record
- Validation only — frozen engine, fixed regime definitions, IS-mechanical volatility
  tertiles applied unchanged to OOS. No optimization, no parameter/rule/source/engine/test
  change, no new filters.
- Trend regime degenerate by construction (all bull-stack). Volatility + year are the
  discriminating axes.
- Donchian/S23/S24/S25, JARVIS, and `templates/base.html` untouched.
- `_regime_raw.json` in this folder is a generated artifact — left untracked. The temp
  runner `_s26_d15_regime.py` was deleted after this report; `report.json` + `report.md`
  are the durable deliverables.
