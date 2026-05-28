# s14 D1 AAPL + JPM + XOM Cross-Sector Cash-Equity 3-Name Basket RSI(3) Bi-Directional Large-Cap Long-History Tier-N Specification Plan

Status: **PLAN_ONLY** (no code written, no spec drafted, no spec sealed, no data fetched by this plan; the next step is a separate operator authorization to author an availability-probe RUN_BOOK + DR9 audit for the new symbols, then DRAFT).

Authored: 2026-05-28
Authorization phrase: `Authorize s14-d1-cash-equity universe revision to cross-sector basket — bound by DR10 v2.`

Origin: cross-sector universe revision of the s14-d1-cash-equity research line, authored to address the A7 effective-independent-bets concern flagged in the all-tech DRAFT (commit `214bae0` §9). This is a **FRESH SIBLING CANDIDATE**, NOT a `_revN_` of the all-tech candidate.

Framework binding: **DR10 v2 AND-conjunction** (framework SEAL at commit `78cd22e`). DR10 in this candidate's eventual SEAL shall carry the v2 definition verbatim. NO retroactive application to existing sealed candidates.

----

## HARD BOUNDARIES (held by this PLAN)

PLAN only. No DRAFT. No SEAL. No code. No backtest. No simulator. No signal computation. No data fetch. No yfinance / Tiingo / vendor API call. No `DATABENTO_API_KEY` or any API-key access. No network IO. No `review_queue.json` mutation. No production `idea_memory` mutation. No Strategy Lab run. No candidate promotion. **No modification of the all-tech sibling DRAFT at `214bae0`** (it remains valid byte-stable). **No modification of the s14-d1-multi-instrument chain** (gate-blocked at Databento). **No retroactive application of DR10 v2 to any existing sealed candidate.** **No reinterpretation of any existing sealed candidate's verdict.** No s13-d1 / s12-d1 / parked-candidate revival. No s11-d1 / s10-d2 / s10-d1 / s9 / s7-d1 / B005_NNN / B006_NNN / T8 / NKE sealed-artifact modification. No phase-2 safety contract template modification. No CLAUDE.md / RUNBOOK / `.gitignore` modification. **No `brain_memory/projects/trading_bot/lessons.md` modification or staging.** No git commit by this PLAN turn (commit is a separate authorization). No live trading. No profitability claim. Trading remains `PAUSED`. Live remains `BLOCKED_AT_6_GATES`. FRC `NEVER_GRANTED`.

----

## 1. Purpose

Author a Tier-N specification PLAN for a cross-sector 3-name cash-equity basket using the same **Connors RSI(3) bi-directional mean-reversion mechanic** (F3-adjacent) as the all-tech sibling, but with a **cross-sector universe** chosen to improve A7 effective-independent-bets.

The all-tech sibling DRAFT (`{AAPL, MSFT, NVDA}`; commit `214bae0`) flagged A7 as a **load-bearing concern** — all 3 names are mega-cap tech with ~0.70-0.85 pairwise correlation, yielding expected A7 ≈ 1.5-2.0. This cross-sector candidate substitutes a financials name (JPM) and an energy name (XOM) for the two non-AAPL tech names, targeting much lower pairwise correlation (~0.3-0.5) and expected A7 ≈ 2.3-2.8.

This PLAN does NOT seal the spec, does NOT fetch data, and does NOT modify the all-tech sibling. The two cash-equity candidates (all-tech + cross-sector) are **non-mutually-exclusive siblings**; the operator chooses which (or both) to advance.

----

## 2. Candidate identification

| Field | Proposed value (LOCKED at PLAN unless noted) |
|---|---|
| `candidate_record_id` | **`s14-d1-aapl-jpm-xom-cross-sector-cash-equity-rsi-3-bi-directional-large-cap-long-history`** |
| `candidate_family` | **F3-adjacent RSI(3) bi-directional mean-reversion** (LOCKED at PLAN; same mechanic family as all-tech sibling) |
| `is_a_single_instrument_candidate` | **false** — multi-name cross-sector basket |
| `is_a_s14_d1_cash_equity_all_tech_revision` | **false** — fresh sibling under a distinct `candidate_record_id`; NOT a `_revN_`; the all-tech DRAFT at `214bae0` is preserved byte-stable |
| `is_a_s14_d1_multi_instrument_revision` | **false** — orthogonal asset class (cash equity vs micro-futures) AND orthogonal universe |
| `is_a_s13_d1_revision` | **false** — orthogonal asset class + slower RSI + cross-sector universe |
| `is_a_s9_revision` | **false** — s9 was 4-ETF basket (SPY/TLT/GLD/USO) long-only; this is single-name cross-sector basket bi-directional; different granularity + direction + RSI period |
| `is_a_s7_d1_revision` | **false** — s7-D1 was ETF basket; this is single-name equity basket |
| `predecessor_lineage_references_read_only` | `s14_d1_cash_equity_all_tech_draft` (sibling; `214bae0`), `s14_d1_multi_instrument_chain` (sibling; gate-blocked), `s13_d1_p7_terminal`, `s12_d1_p11_park`, `s11_d1_chain`, `s10_d2_park`, `s10_d1_park`, `s9_park`, `s7_d1_park`, `b005_b006_archival`, `t8_nke_archive`, `phase_2_safety_contract_template_C1_C8`, `framework_dr10_revision_seal_v2` |
| `diagnostic_only` | true |
| `default_advisory_label` | `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` |
| K9-reachability discipline applied at PLAN | **TRUE** |
| DR10-v2-reachability discipline applied at PLAN | **TRUE** |
| Framework DR10 binding | **v2 AND-conjunction** (commit `78cd22e`) |

----

## 3. Universe precommitment (LOCKED at PLAN; operator-revisable at next phase with first-principles justification)

| Field | LOCKED at PLAN value |
|---|---|
| Universe type | `multi_name_cross_sector_large_cap_cash_equity_basket` |
| Symbol 1 | **`AAPL`** (Apple Inc.; Information Technology; NASDAQ) — **data already captured + DR9-PASSED** in the all-tech fetch |
| Symbol 2 | **`JPM`** (JPMorgan Chase & Co.; Financials; NYSE) — **NOT yet fetched** |
| Symbol 3 | **`XOM`** (Exxon Mobil Corp.; Energy; NYSE) — **NOT yet fetched** |
| Symbol count at PLAN | exactly 3 |
| Sector spread | Information Technology / Financials / Energy (3 distinct GICS sectors) |
| Universe widening / substitution post-SEAL | FORBIDDEN (fresh `candidate_record_id` required for any change) |

### 3.1 Cross-sector rationale (the point of this revision)

| Metric | All-tech `{AAPL, MSFT, NVDA}` (DRAFT 214bae0) | Cross-sector `{AAPL, JPM, XOM}` (this PLAN) |
|---|---|---|
| GICS sectors | 1 (all Information Technology) | 3 (Tech / Financials / Energy) |
| Expected pairwise correlation | ~0.70-0.85 (high) | ~0.30-0.50 (moderate-low) |
| Expected A7 effective_independent_bets | ~1.5-2.0 (CONCERN) | **~2.3-2.8 (improved)** |
| Expected signal co-firing | high (correlated names move together) | lower (sectors diverge) |
| Concentration risk (A6) | NVDA-dominance risk (recent vol regime) | more balanced; no single-name dominance expected |

The cross-sector basket directly addresses the all-tech DRAFT's load-bearing A7 concern. Lower pairwise correlation also improves K9 reachability (higher effective signal independence — see §9).

### 3.2 Data reuse + fresh-fetch requirement

- **AAPL:** already captured + DR9-PASSED in the all-tech fetch (`data/s14_d1_aapl_msft_nvda_cash_equity_long_history/raw/AAPL_ohlcv_1d_20190102_20251230.csv`, sha `f6625ff1…`). **Reusable byte-equivalent** OR re-fetch into the cross-sector candidate's own directory at availability-probe time (operator decision; either way AAPL's DR9 PASS is established).
- **JPM, XOM:** **NOT yet fetched.** Require fresh operator-side Tiingo fetch + DR9 audit (same vendor + split_only convention that succeeded for the all-tech basket).

----

## 4. Strategy mechanic family LOCKED at PLAN: F3-adjacent Connors RSI(3) bi-directional (carried from all-tech lineage)

Identical mechanic to the all-tech sibling — the ONLY change in this candidate is the universe (cross-sector vs all-tech). Carrying the mechanic verbatim keeps the cross-sector test a clean A/B on diversification.

| Field | LOCKED value at PLAN |
|---|---|
| Mechanic family | F3-adjacent RSI(3) bi-directional mean-reversion |
| RSI period | 3 (Connors) |
| RSI long entry / long exit / short entry / short exit | `< 15` / `> 55` / `> 85` / `< 45` |
| Signal direction | bi-directional (long+short symmetric) per-name |
| Per-name max positions | `max_positions_per_name = 1` |
| Portfolio max positions | `max_total_positions = 3` |
| Inter-name signal coordination | NONE (per-name independent) |
| Stop method | ATR-based 2N (carried) |
| Pyramid | NONE |
| DA3 per-trade risk pct | `B = 0.005` (0.5%) |
| DA4 START_CASH (proposed) | `B = $100,000` |

### 4.1 First-principles burden (cross-sector vs predecessors)

- **vs all-tech sibling:** same mechanic; DIFFERENT universe (cross-sector vs all-tech). Distinct `candidate_record_id`. This is a deliberate diversification A/B, NOT a `_revN_`.
- **vs s9:** different universe granularity (single-name cross-sector vs 4-ETF basket) + bi-directional vs long-only + RSI(3) vs RSI(2). The cross-sector single-name basket is structurally distinct from s9's mixed-asset-class ETF basket.
- **vs s7-D1:** s7-D1 was an ETF basket with USO-dominance concentration pathology. This cross-sector single-name basket explicitly targets balanced A6/A7 (low single-name dominance) — directly informed by the s7-D1 lesson.
- **vs s14-d1-multi-instrument:** orthogonal asset class entirely (cash equity vs micro-futures).

----

## 5. Corporate-action profile (cross-sector; load-bearing for DR9 at availability-probe phase)

| Symbol | Splits in 2019-2025 window | Dividends | DR9 split-event-consistency concern |
|---|---|---|---|
| AAPL | 2020-08-31 4:1 | regular quarterly | Already verified PASS in all-tech fetch (split_only consistency confirmed) |
| JPM | **NONE in window** (last split 2000) | regular quarterly (higher yield than tech) | Low — no split to verify; split_only = raw close |
| XOM | **NONE in window** (last split 2001) | regular quarterly (high yield ~3-5%) | Low — no split to verify; split_only = raw close |

**Note on dividend yield:** JPM and XOM have materially higher dividend yields than tech names. Under `split_only` convention (dividends NOT adjusted into price), ex-dividend dates will show small downward price jumps. These are typically <1% of price (JPM ~$1/share quarterly on ~$200 stock; XOM ~$1/share on ~$110 stock) — small relative to typical daily moves, so should not materially distort RSI(3) signal generation. This will be confirmed at the DR9 audit / DRAFT phase. The all-tech DRAFT's `split_only` advisory rationale carries.

----

## 6. K9-reachability table at PLAN

| Window | Length (y) | Required trades/y | Per-name expected | 3-name effective (at ~75% independence) | Total | K9 status |
|---|---:|---|---|---|---|---|
| IS | ~5.0 | ≥ 20.0 | 20-35/y | 45-79/y | 225-395 | **CLEARS WITH STRONG MARGIN** (~11-20x floor) |
| **OOS** | **~2.0** | **≥ 50.0** | 20-35/y | 45-79/y | 90-158 | **CLEARS** (1.8-3.2x floor) — **improved vs all-tech** (which was borderline 36 at low estimate) |

**Key improvement vs all-tech:** lower cross-sector correlation → higher effective signal independence (~75% vs all-tech's ~60%) → OOS K9 clears with margin even at the low estimate (90 > 50/y floor), whereas the all-tech basket was BORDERLINE at its low estimate (36 < 50). **K9 OOS risk for cross-sector: LOW-MODERATE** (vs all-tech's MODERATE).

REC1-equivalent (BINDING): if observed effective IS rate < 25/y basket-summed, OOS K9 unreachability becomes structurally probable → PARK per precedent. Cross-sector expected effective rate (45-79/y) comfortably exceeds the 25/y critical floor.

----

## 7. DR10-v2-reachability table at PLAN

Identical cost surface to the all-tech sibling (cash equity; per-share commission tiny fraction of notional).

| Component | Estimate |
|---|---|
| Expected annual_turnover | ~30-60 (turnover branch fires alone; non-binding under AND) |
| Expected S2 cost_drag | ~0.3-0.6% (well under 5% threshold) |
| **DR10 v2 status** | **CLEARS WITH STRONG MARGIN** (cost_drag branch does not fire; AND-conjunction not triggered) |

----

## 8. Diversification metrics (LOAD-BEARING at SEAL; the central improvement of this candidate)

| Metric | All-tech expected | Cross-sector expected (this candidate) |
|---|---|---|
| A7 effective_independent_bets | 1.5-2.0 (concern) | **2.3-2.8 (improved; the point of the revision)** |
| K10 avg_pairwise_correlation | 0.70-0.85 | **0.30-0.50 (improved)** |
| K6 per_symbol_dispersion | TBD | TBD (expected higher dispersion across sectors) |
| A6 concentration_index | NVDA-dominance risk | **more balanced (no single-name dominance expected)** |

This candidate exists specifically to test whether the cross-sector diversification materially improves the basket's risk profile vs the all-tech sibling, holding the mechanic constant.

----

## 9. DR register + K-gates (carried byte-equivalent from all-tech DRAFT; DR10 = v2)

DR register, DR precedence chain (`DR7 → DR1 → DR9 → DR10 → DR6 → DR4 → DR2 → DR3 → DR5`), and K-gates (K1/K2/K4/K6/K7/K8/K9/K10/K12; K11 NOT_APPLICABLE no leverage cap) carry byte-equivalent from the all-tech DRAFT at `214bae0`, with:
- DR9 evaluated per-name (3 separate checks; AAPL already PASSED; JPM + XOM pending fresh fetch)
- DR10 = v2 AND-conjunction by-reference (framework SEAL `78cd22e`)
- A7 / K10 / K6 / A6 LOAD-BEARING (multi-name; this candidate's A7 is the central improvement metric)

----

## 10. Boundaries held this PLAN turn

| Boundary | Status |
|---|---|
| PLAN only (no DRAFT / SEAL / BUILD / fetch) | met |
| No data fetch / vendor API call / API-key access | met |
| No backtest / simulator / signal computation / OOS inspection | met |
| **No modification of the all-tech sibling DRAFT at `214bae0`** | met |
| **No modification of the s14-d1-multi-instrument chain** | met |
| No retroactive application of DR10 v2 to existing candidates | met |
| No s13-d1 / s12-d1 / parked-candidate revival | met |
| No modification of any existing sealed artifact | met |
| **No `brain_memory/projects/trading_bot/lessons.md` modification or staging** | met |
| No git commit by this PLAN turn | met (commit is a separate authorization) |
| No profitability claim | met |
| Trading / Live / FRC | `PAUSED` / `BLOCKED_AT_6_GATES` / `NEVER_GRANTED` |
| K9-reachability + DR10-v2-reachability disciplines applied | TRUE |

----

## 11. Files written this PLAN turn

| File | Purpose |
|---|---|
| `docs/s14_d1_aapl_jpm_xom_cross_sector_cash_equity_rsi_3_bi_directional_large_cap_long_history_tier_n_spec_plan.md` | This cross-sector sibling Tier-N spec PLAN (PLAN only; no JSON sidecar at PLAN phase; no canonical seal sha256; NOT committed by this turn) |

No other repository file is modified. The all-tech sibling DRAFT, the multi-instrument chain, and `lessons.md` are all untouched.

----

## 12. Next-step authorization scope

### Commit this PLAN (recommended first step)

```
Authorize commit s14-d1-cross-sector cash-equity Tier-N spec PLAN only.
```

### Availability probe + DR9 audit for the new symbols

```
Authorize s14-d1-cross-sector cash-equity multi-name OHLCV availability probe + DR9 audit framework only.
```

Authors a RUN_BOOK (analogous to the all-tech RUN_BOOK at `529bb6b`) for JPM + XOM fresh fetch (AAPL data reusable / re-fetchable). Tiingo split_only convention carries.

### Sibling all-tech path remains available

The all-tech DRAFT at `214bae0` is valid and can proceed to SEAL independently:
```
Authorize s14-d1-cash-equity Tier-N spec SEAL only — bound by DR10 v2.
```

### Defer

```
Defer / Pause s14-d1-cross-sector cash-equity PLAN.
```

----

## 13. Carried-forward status (UNCHANGED across this PLAN turn)

| Field | Value |
|---|---|
| Trading / Live / FRC | `PAUSED` / `BLOCKED_AT_6_GATES` / `NEVER_GRANTED` |
| `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` | applies to this candidate + descendants |
| `no_strategy_optimization_authorized` | TRUE |
| `no_dr_redefinition_post_seal` (existing sealed candidates) | TRUE |
| s13-d1 / s12-d1 lifecycles terminal | TRUE — preserved |
| all-tech sibling DRAFT at `214bae0` | byte-stable; valid; non-mutually-exclusive with this candidate |
| s14-d1-multi-instrument chain | byte-stable; gate-blocked at Databento |
| `framework_dr10_revision_seal_v2` at `78cd22e` | binding for s14+ |
| `lessons.md` (NOT touched this turn) | pre-existing modified state preserved |
| K9-reachability + DR10-v2-reachability disciplines | binding |
| s14-d1-cross-sector cash-equity lifecycle state | `S14_D1_CROSS_SECTOR_CASH_EQUITY_TIER_N_SPEC_PLAN_AUTHORED` (this PLAN turn; NOT committed) |

----

End of PLAN. PLAN-authoring turn only. No code. No backtest. No fetch. No vendor API call. No DRAFT. No SEAL. No BUILD. No commit. **No modification of the all-tech sibling DRAFT or any sealed artifact. No `lessons.md` modification or staging.** Trading remains `PAUSED`. Live remains `BLOCKED_AT_6_GATES`. Fresh sibling candidate; all-tech sibling preserved; cross-sector universe targets improved A7 vs all-tech.
