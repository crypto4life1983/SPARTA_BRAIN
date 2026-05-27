# s14 D1 MNQ.c.0 + MES.c.0 + MYM.c.0 + M2K.c.0 Multi-Instrument RSI(2) Bi-Directional Databento Long-History Tier-N Specification Plan

Status: **PLAN_ONLY** (no code written, no spec drafted, no spec sealed, no data fetched by this plan; the next step is a separate operator authorization to DRAFT the Tier-N spec).

Authored: 2026-05-27
Authorization phrase: `Authorize s14-d1 multi-instrument RSI(2) bi-directional micro-futures basket Tier-N spec PLAN only — bound by DR10 v2.`

Selection-plan source: `docs/next_research_track_selection_plan_after_s13_d1_terminal_rev2_under_dr10_v2.md` (committed in `ee2bfc1`; **T1 rev2 co-recommended at 43/60** alongside T2 rev2 cash-equity basket).

Framework binding: this candidate is authored **under DR10 v2 AND-conjunction** (framework SEAL at commit `78cd22e`; `report_seal_sha256` `7794bb5222ed2a2cb1cd8e1ef2f43f3d1abc6f1539d71af31dda32d832b5e907`). DR10 in this candidate's eventual SEAL shall carry the v2 definition verbatim. **NO retroactive application** to existing sealed candidates.

Predecessor terminal / parked candidates (READ-ONLY; not modified by this plan):
- `s13-d1-mnq-c0-single-instrument-rsi-2-bi-directional-databento-long-history` — terminal REJECT_FAST at P7 (commit `cc1817b`) under DR10 v1 turnover branch. **Not revived; not _revN_; multi-instrument scope structurally differentiates s14-d1 from s13-d1's single-instrument scope.**
- `s12-d1-mnq-c0-single-instrument-donchian-15-8-databento-long-history` — terminal park (commit `ecbd001`). **Not revived.**
- s11-d1 v1 / rev2 chain, s10-d2 park, s10-d1 park, s9 RSI-2 ETF-proxy park, s7-D1 park, B005_NNN / B006_001/002 archival, T8 / NKE archive — all READ-ONLY byte-stable.

Audit-clean data anchor (already in repo; reused byte-equivalent for MNQ.c.0; OTHERS subject to availability/DR9 gating):
- `MNQ.c.0`: `data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_c_0_ohlcv_1d_20190513_20251230.csv` (sha256 `8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e`; 2066 rows; 2019-05-13 → 2025-12-29)
- `MES.c.0`, `MYM.c.0`, `M2K.c.0`: **NOT yet acquired**; subject to availability/DR9 gating at next phase (operator-side Databento fetch + DR9 audit prerequisite).

----

## HARD BOUNDARIES (held by this PLAN)

PLAN only. No DRAFT. No SEAL. No code. No backtest. No simulator. No signal computation. No data fetch. No yfinance / Yahoo Finance call. No Databento call. No `DATABENTO_API_KEY` access. No QC / LEAN call. No network IO. No `review_queue.json` mutation. No production `idea_memory` mutation. No Strategy Lab run. No candidate promotion. **No s13-d1 revival.** **No s13-d1 `_revN_` revision authored by this plan.** **No retroactive application of DR10 v2 to any existing sealed candidate.** **No reinterpretation of any existing sealed candidate's verdict.** **No modification of any existing sealed candidate artifact** (s11-d1 / s12-d1 / s13-d1 SEAL/P1/P2/P3/P4/P6/P6.5/P7 + framework_dr10_revision_seal_v2 all byte-stable). No s12-d1 revival. No s10-d2 / s10-d1 / s9 / s7-d1 / B005_NNN / B006_NNN / T8 / NKE sealed-artifact modification. No phase-2 safety contract template modification. No CLAUDE.md modification. No RUNBOOK modification. No `pipeline_manifest` modification. No `.gitignore` modification. **No `brain_memory/projects/trading_bot/lessons.md` modification or staging.** No branch change. No git push. No live trading. No profitability claim. Trading remains `PAUSED`. Live remains `BLOCKED_AT_6_GATES`. FRC `NEVER_GRANTED`.

----

## 1. Purpose

Author a Tier-N specification PLAN for the first fresh candidate under the DR10 v2 AND-conjunction framework. The candidate is a multi-instrument basket of liquid equity-index micro-futures using the **Connors RSI(2) bi-directional mean-reversion mechanic** (F3 family) — the same mechanic that proved economically profitable on single MNQ.c.0 in s13-d1 (terminal REJECT_FAST by DR10 v1 turnover branch on a single-instrument scope) but applied to a structurally-different MULTI-INSTRUMENT basket and bound by DR10 v2 (AND-conjunction, which the same mechanic clears via the cost_drag branch).

This PLAN locks the **mechanic family, RSI thresholds, universe (subject to availability gating), signal direction, sizing scheme, and pyramid policy** AT PLAN time. The DRAFT and SEAL turns (separate authorizations) shall further lock the operational parameters (ATR settings, cost-stress matrix, K-gate thresholds, output schema).

The PLAN does NOT seal the spec. No code, no data fetch, no Databento call, no backtest, no OOS inspection, no broker / live / Strategy Lab interaction is performed by this PLAN.

----

## 2. Candidate identification

| Field | Proposed value (LOCKED at PLAN unless noted) |
|---|---|
| `candidate_record_id` | **`s14-d1-mnq-mes-mym-m2k-multi-instrument-rsi-2-bi-directional-databento-long-history`** |
| `candidate_family` | **F3 RSI(2) bi-directional mean-reversion** (LOCKED at PLAN; same mechanic family as s13-d1) |
| `is_a_trade_candidate` | true |
| `is_a_single_instrument_candidate` | **false** — load-bearing structural property: **multi-instrument basket** |
| `is_a_s13_d1_revision` | **false** (s13-d1 was SINGLE-INSTRUMENT `{MNQ.c.0}`; s14-d1 is MULTI-INSTRUMENT `{MNQ.c.0, MES.c.0, MYM.c.0, M2K.c.0}` — orthogonal universe scope) |
| `is_a_s13_d1_revN_revision` | **false** (s13-d1 terminal at P7; s14-d1 uses a fresh `candidate_record_id`; T-FORBID-10 not triggered because parameters change AND universe scope changes) |
| `is_a_s12_d1_revision` | false (s12-d1 was F1 Donchian; s14-d1 is F3 RSI mean-reversion — orthogonal mechanic family) |
| `is_a_s11_d1_revision` | false |
| `is_a_s10_d2_revision` | false |
| `is_a_s10_d1_revision` | **false** (s10-d1 was MNQ+MGC pair; s14-d1 is 4 equity-index micros NO MGC; orthogonal basket) |
| `is_a_s9_revision` | **false** (s9 was 4-ETF basket SPY/TLT/GLD/USO long-only; s14-d1 is 4 equity-index micro-FUTURES bi-directional; different asset class + different cost surface + different signal direction) |
| `is_a_s7_d1_revision` | false |
| `is_a_b006_NNN_extension` | false |
| `predecessor_lineage_references_read_only` | `s13_d1_p7_terminal`, `s12_d1_p11_park`, `s11_d1_v1_rev2_chain`, `s10_d2_park`, `s10_d1_park`, `s9_rsi2_etf_proxy_park`, `s7_d1_park`, `b005_b006_archival`, `t8_nke_archive`, `phase_2_safety_contract_template_C1_C8`, `framework_dr10_revision_seal_v2` |
| `diagnostic_only` | true |
| `not_promotable_via_this_diagnostic` | true |
| `default_advisory_label` | `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` |
| Selection-plan source score (rev2) | **43 / 60** (co-recommended primary alongside T2 rev2 cash-equity basket) |
| K9-reachability discipline applied at PLAN time | **TRUE** |
| **DR10-v2-reachability discipline applied at PLAN time (NEW under v2)** | **TRUE** |
| REC1-equivalent OOS-K9 disclosure carried | TRUE (with multi-instrument adjustment; see §9.4) |
| **Framework DR10 binding** | **v2 AND-conjunction (NOT v1)** per `framework_dr10_revision_seal_v2` at commit `78cd22e` |

----

## 3. Universe precommitment (LOCKED at PLAN; subject to availability/data-quality gating)

| Field | LOCKED at PLAN value |
|---|---|
| Universe type | `multi_instrument_continuous_micro_futures_basket` |
| Symbol 1 | **`MNQ.c.0`** (Micro E-mini Nasdaq-100; continuous front-month; **already in audit chain**) |
| Symbol 2 | **`MES.c.0`** (Micro E-mini S&P 500; continuous front-month; **NOT yet acquired**) |
| Symbol 3 | **`MYM.c.0`** (Micro E-mini Dow; continuous front-month; **NOT yet acquired**) |
| Symbol 4 | **`M2K.c.0`** (Micro E-mini Russell 2000; continuous front-month; **NOT yet acquired**) |
| Symbol count at PLAN | exactly 4 |
| Universe widening at later phases | FORBIDDEN (any wider basket = fresh `candidate_record_id`) |
| Universe substitution at later phases | FORBIDDEN (substitution of any symbol post-SEAL = fresh `candidate_record_id`) |
| Common-history start | **subject to MES/MYM/M2K availability probe** (TBD at next phase) |
| Per-symbol diversification claim | YES (4 distinct equity-index exposures: Nasdaq-100, S&P 500, Dow, Russell 2000) |
| Pairwise correlation expected | high (all US-equity-index based); **A7 effective-independent-bets metric is LOAD-BEARING at SEAL** |
| K10 / K6 metrics applicability | **applicable** (multi-symbol diversification governance carries from s10-d2 / s7-D1 lineage) |

### 3.1 Availability / data-quality gating (precommitment contingency)

The universe is precommitted **conditional on** each non-MNQ instrument passing the following gates at the next-phase operator-side fetch + audit:

1. **Databento availability:** each symbol must be available on `GLBX.MDP3` (or alternative vendor approved at SEAL) with `ohlcv-1d` schema and `stype_in=continuous`.
2. **Common-history start:** intersection of common-history starts across all 4 symbols must be ≥ 2019-05-13 (the s10-d1 chain's MNQ.c.0 common-history start). If the intersection is later (e.g., M2K may not have full 2019 history), the IS window start shifts forward at SEAL.
3. **DR9 audit:** each non-MNQ symbol must pass DR9-equivalent thresholds (`gap_continuity ≥ 0.95`, `max_gap ≤ 0.30`, `roll_event_count ≤ 5`, `quality_violation_count ≤ 5`) carried byte-equivalent from s10-d1 audit framework.

### 3.2 Contingency outcomes if gating fails

If at the next-phase operator-side probe + DR9 audit any symbol FAILS:

| Failure mode | Contingency authorized by this PLAN |
|---|---|
| 1-symbol DR9 failure (e.g., M2K continuous-stitch fails like MGC did in s10-d1) | **Shrink to remaining 3-symbol basket** (re-author PLAN under fresh `candidate_record_id` with 3-symbol scope; THIS PLAN does NOT authorize the shrunk variant — requires a separate PLAN turn) |
| 2-symbol DR9 failure | **Shrink to remaining 2-symbol basket** (requires fresh `candidate_record_id` + separate PLAN turn; basket may need to revert to MNQ-only or be re-planned entirely) |
| 3-symbol DR9 failure | **Candidate aborts at PLAN/DRAFT boundary**; the multi-instrument hypothesis fails availability gating; alternative tracks (T2 rev2 cash-equity basket, etc.) become preferred |
| All 4 symbols DR9 clear | **Proceed to next-phase DRAFT under this PLAN's full 4-symbol scope** |
| Substitution (e.g., replace M2K with 6E.c.0 or ZN.c.0) | **FORBIDDEN** — substitution requires a fresh `candidate_record_id` AND a fresh PLAN turn; this PLAN explicitly forbids in-place symbol substitution |

----

## 4. Strategy mechanic family LOCKED at PLAN: F3 Connors RSI(2) bi-directional

s14-d1 LOCKS the mechanic family AT PLAN time. The candidate's load-bearing structural properties are (a) **per-instrument independent RSI(2) bi-directional signal generation** and (b) **multi-instrument basket scope**. Either changes would defeat the fresh-candidate justification.

### 4.1 Mechanic primitives (LOCKED at PLAN)

| Field | LOCKED value at PLAN |
|---|---|
| Mechanic family | **F3 RSI(2) bi-directional mean-reversion** |
| RSI computation | **Connors RSI(2)** (2-period RSI; Wilder smoothing on close-to-close returns) per-instrument independent |
| **RSI long entry threshold** | **`< 10`** (oversold) per-instrument |
| **RSI long exit threshold** | **`> 50`** (mean-reversion complete) per-instrument |
| **RSI short entry threshold** | **`> 90`** (overbought; bi-directional symmetric) per-instrument |
| **RSI short exit threshold** | **`< 50`** (mean-reversion complete) per-instrument |
| Signal direction | **bi-directional** (long+short symmetric thresholds) per-instrument |
| Per-instrument max units | **`max_units_per_market = 1`** (no pyramid per signal per instrument) |
| Portfolio-level max units | **`max_total_units = 4`** (one per instrument; full basket max) |
| Inter-instrument signal coordination | **NONE** — each instrument's RSI/ATR/signal generation is INDEPENDENT |
| Stop method | ATR-based 2N stop (carried byte-equivalent from s13-d1 SEAL) |
| Risk method | per-trade risk percentage of portfolio equity, sized via per-instrument ATR (carried byte-equivalent; subject to portfolio-level cap) |
| Pyramid mechanism | **NONE** (per-instrument structurally forbidden via `max_units_per_market = 1`) |

### 4.2 Why s14-d1 is NOT a rescue of s13-d1 (first-principles burden)

| s13-d1 falsification feature | s14-d1 treatment |
|---|---|
| Universe = `{MNQ.c.0}` (single-instrument) | Universe = `{MNQ.c.0, MES.c.0, MYM.c.0, M2K.c.0}` (multi-instrument; **load-bearing universe scope difference**) |
| DA4 = C (`$200k` start_cash) | DA4 = B (`$100k` start_cash; **load-bearing DA4 difference** — combined with universe difference, this is structurally NOT s13-d1 territory under T-FORBID-9 which requires BOTH same-universe AND same-DA-combination) |
| s13-d1 fired DR10 v1 OR-disjunctive turnover branch (84.79 > 0.50) | s14-d1 is bound by **DR10 v2 AND-conjunction**; the turnover branch alone does NOT fire DR10 v2 (cost_drag branch is the binding co-condition) |
| RSI(2) mechanic with bi-directional thresholds 10/50/90/50 | **Same mechanic** (the candidate's hypothesis is that the RSI(2) bi-directional mechanic, proven economically profitable on single MNQ.c.0 in s13-d1's S0-S4 cost-stress tiers, transfers to a multi-instrument equity-index basket under DR10 v2) |

**First-principles claim:** s13-d1's DR10 v1 firing was a framework-level constraint specific to OR-disjunctive DR10 + single-instrument contract-quantization at retail-scale start_cash. Under DR10 v2 AND-conjunction (framework SEAL `78cd22e`), the turnover branch alone does not fire DR10. The s13-d1 mechanic was economically profitable (positive net PnL at every cost-stress tier S0-S4; 159 trades clearing K9; sharpe_proxy 0.1076 > 0; expectancy $540.73 > 0; |maxDD| 17.68% well under K4 50%). s14-d1 tests the same mechanic on a multi-instrument basket with structurally-higher trade count (~136/y) under the v2 framework.

### 4.3 Why s14-d1 is NOT a rescue of s9 (first-principles burden)

| s9 falsification feature | s14-d1 treatment |
|---|---|
| Universe = SPY/TLT/GLD/USO (4-ETF basket; **mixed asset classes**: equity ETF + bond ETF + commodity ETFs) | Universe = `{MNQ.c.0, MES.c.0, MYM.c.0, M2K.c.0}` (4 equity-index MICRO-FUTURES; single asset class; **fundamentally different cost surface and signal generator validity**) |
| Long-only | **Bi-directional** (long+short symmetric thresholds); structural asymmetry break |
| Cost surface: per-share commission + bps slippage on ETFs | Cost surface: **per-contract commission + tick slippage on micro-futures** (carried from s12-d1 / s13-d1 chain) |
| S0 edge negative (-$1,211 over 414 trades) | S0 edge sign on s14-d1 is **open question**; s13-d1's S0 edge was POSITIVE ($102,795 over 159 trades on MNQ alone) — strong PLAN-time signal but not a binding pre-registered claim |
| Falsification cause: instrument-specific cost/edge interaction on equity ETFs (per-share commission structure) | s14-d1 tests on a structurally different asset class (futures vs ETFs) with different cost structure |

**First-principles claim:** the s9 falsification does NOT transfer to s14-d1 because (a) the asset class differs (futures vs ETFs), (b) the cost surface differs (per-contract vs per-share + bps), (c) the signal direction differs (bi-directional vs long-only), and (d) the universe differs (4 equity-index micros vs 4 mixed-asset-class ETFs). s13-d1's S0-positive result on single MNQ already partially answered this question (the RSI(2) signal generator IS valid on micro-futures cost surface).

### 4.4 Why s14-d1 is NOT a rescue of s10-d1 / s10-d2 (first-principles burden)

| Predecessor | Failure | s14-d1 treatment |
|---|---|---|
| s10-d1 (MNQ + MGC 2-symbol basket) | DR9 fired on MGC continuous-stitch | s14-d1 EXPLICITLY EXCLUDES MGC; only equity-index micros |
| s10-d2 (4-market Donchian-55/20 basket at $500k cash) | OOS K9 fired (53 trades < 100) | s14-d1 mechanic is RSI(2) bi-directional, structurally higher signal density (~30-40/y per instrument × 4 = ~136/y) vs Donchian-55/20 (~3-15/y per instrument); K9 reachability fundamentally better |

----

## 5. Data assumptions (LOCKED at SEAL; subject to availability gating at DRAFT)

| Field | Proposed value (LOCKED at SEAL) |
|---|---|
| Vendor | **Databento Historical API** (operator-side; controller-side never calls) |
| Dataset | **`GLBX.MDP3`** |
| Schema | **`ohlcv-1d`** |
| `stype_in` | **`continuous`** |
| Symbols requested | `["MNQ.c.0", "MES.c.0", "MYM.c.0", "M2K.c.0"]` |
| **Re-use of existing MNQ.c.0 audit-clean CSV** | **TRUE** — `data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_c_0_ohlcv_1d_20190513_20251230.csv` (sha256 `8b7b832c…23e`) reused byte-equivalent. **ZERO new Databento call required for MNQ.c.0.** |
| Fresh Databento fetch for MES / MYM / M2K | **REQUIRED at next phase** (operator-side; outside this PLAN's scope). New step-02b manifest authored per s10-d1 fetch pattern; DR9 audit per-instrument. |
| API key handling at any phase | operator-side only; controller never accesses `DATABENTO_API_KEY` |
| Controller-side Databento call at any phase | **LOCKED OFF** |

----

## 6. Schema + stype_in (LOCKED at SEAL)

| Field | LOCKED value |
|---|---|
| Schema | `ohlcv-1d` |
| Fields | `ts_event`, `open`, `high`, `low`, `close`, `volume` |
| Intraday schemas | OUT OF SCOPE for this Tier-N |
| `stype_in` | `continuous` (per-symbol) |
| `no_continuous_roll_stitch_modification_post_seal` invariant | TRUE per-symbol |

----

## 7. IS / OOS windows (LOCKED at SEAL; subject to common-history intersection)

| Field | LOCKED value (subject to common-history adjustment) |
|---|---|
| Proposed IS window start | `2019-05-13` (MNQ.c.0 start; may shift later if MES/MYM/M2K have shorter history) |
| Proposed IS window end | `2023-12-29` |
| Proposed IS window length | ~4.6 years |
| Proposed OOS window start (never inspected at IS) | `2024-01-02` |
| Proposed OOS window end (never inspected at IS) | `2025-12-30` |
| Proposed OOS window length | ~2.0 years |
| OOS inspection at IS phase | FORBIDDEN (`oos_inspection_blocked_at_in_sample` invariant per-symbol) |
| Common-history adjustment at SEAL | if intersection of common-history starts across all 4 symbols is later than 2019-05-13, **the IS window start shifts forward at SEAL**; the OOS window window shifts proportionally to preserve 2.0y OOS length |

----

## 8. Sizing precommitment (LOCKED at PLAN; LOCKED at SEAL)

| Field | LOCKED at PLAN value | Rationale |
|---|---|---|
| **DA3 (per-trade risk percentage)** | **`B` (= 0.5%)** | Carry-over from s13-d1 SEAL as a **PROVEN-effective DR3 mitigation** (RSI lineage cost-erosion was DR3-elevated; s13-d1 demonstrated DR3 does NOT fire under DA3=B with positive edge across all cost tiers) |
| **DA4 (`START_CASH_USD`)** | **`B` (= $100,000)** | **Materially different from s13-d1's DA4=C ($200k)** — load-bearing differentiation under T-FORBID-9 (which requires BOTH same-universe AND same-DA-combination to fire) |
| Per-instrument max units | `max_units_per_market = 1` | LOCKED at PLAN |
| Portfolio-level max units | `max_total_units = 4` | LOCKED at PLAN |
| Per-instrument independent sizing | TRUE | Each instrument's contracts = `floor(risk_pct × equity / (ATR × tick_value))` per-instrument |
| Portfolio-level cap | basket equity-protection rule TBD at DRAFT (e.g., max simultaneous notional < N× equity) | Not LOCKED at PLAN; subject to DRAFT proposal + SEAL lock |

### 8.1 Note on DA4=B borderline DR10 v2 cost_drag

At DA4=B ($100k start_cash) with 4-instrument basket trading at ~136/y, the S2 cost_drag is **borderline 5%** (s13-d1 at $200k single-instrument single-MNQ had S2 cost_drag 2.35%; multi-instrument at half the capital base would scale to ~4-5%). DR10 v2 AND-conjunction requires BOTH turnover>0.50 AND cost_drag>0.05 to fire — at DA4=B the cost_drag branch is the BINDING co-condition that needs careful SEAL-time precommitment.

**Operator option at DRAFT/SEAL (NOT pre-approved at PLAN):** revise DA4 to C ($200k) if SEAL-time DR10-v2-reachability analysis shows DA4=B cost_drag at S2 exceeds 5%. DA4=C with multi-instrument scope is **NOT T-FORBID-9 territory** because T-FORBID-9 requires BOTH same single-instrument scope AND same DA combination; multi-instrument scope alone differentiates regardless of DA4.

----

## 9. K9-reachability table at PLAN time (binding framework discipline)

### 9.1 Required trade-count thresholds (carried byte-equivalent from s11-lineage)

| Window | Length (y) | Required closed_trades/year for K9=100 | Status threshold |
|---|---:|---|---|
| IS | ~4.6 | ≥ 21.74 trades/y | K9_IS_REACHABLE if ≥ |
| **OOS** | **~2.0** | **≥ 50.00 trades/y** (BINDING) | **K9_OOS_REACHABLE if ≥** |

### 9.2 Expected trade count for s14-d1 RSI(2) bi-directional on 4-instrument equity-index micro basket

**Per-instrument signal density basis (PLAN-time estimate; subject to P6 IS confirmation):**

- s13-d1 observed **34.34 trades/year on MNQ.c.0** single-instrument bi-directional RSI(2) over 4.6y IS (159 trades total).
- MES.c.0 / MYM.c.0 / M2K.c.0 expected per-instrument signal density at **~20-40/year** (similar vol regime; broadly correlated to MNQ; signal density on equity-index micros is dominated by RSI(2) signal frequency on daily bars, which is structurally similar across these 4 instruments).
- Per-instrument signal independence is **NOT structurally guaranteed** — equity-index micros are highly correlated, so signals may co-fire. However: per-instrument RSI computation is independent, and signals on different instruments produce DIFFERENT entry timing even when correlation is high. Conservatively estimate signal independence at ~70% (i.e., effective independent trade rate = 0.7 × per-instrument summed rate).

### 9.3 K9-reachability assessment for s14-d1

| Window | Required trades/y | Expected per-instrument trades/y (low / central / high) | Effective 4-instrument total (at 70% independence) | Expected total trades | K9 status |
|---|---|---|---|---|---|
| IS (4.6y) | ≥ 21.74 | 20 / 30 / 40 | 56 / 84 / 112 | 257 / 386 / 514 | **CLEARS K9 WITH STRONG MARGIN** (~12-24x the floor) |
| **OOS (2.0y)** | **≥ 50.00** | **20 / 30 / 40** | **56 / 84 / 112** | **112 / 168 / 224** | **CLEARS K9 WITH MARGIN** at every estimate point (~2-4x the floor) |

### 9.4 K9-reachability disclosure

- s14-d1 has **the strongest K9-reachability margin of any candidate authored to date**.
- K9 IS clears at 12-24x the floor; K9 OOS clears at 2-4x the floor across the PLAN-time estimate band.
- s13-d1's lesson L8 ("DR10 binding for high-frequency families; DA4 capital scaling addresses cost_drag branch only") informed the multi-instrument scope choice: more instruments at lower per-instrument frequency vs single-instrument high frequency.
- **REC1-equivalent disclosure for s14-d1** (carried byte-equivalent from s13-d1 SEAL with multi-instrument adjustment): if observed effective IS rate falls below 25 trades/y (basket-summed), OOS K9 unreachability becomes structurally probable. The expected effective rate is 56-112/y; lower-bound observation below 25/y would require parking.

### 9.5 K9 mitigation levers NOT pre-approved by this PLAN

The following are explicitly NOT authorized by this PLAN (per `no_strategy_optimization_authorized`):

- Add a 5th instrument to widen the basket (forbidden post-SEAL; would require fresh `candidate_record_id`)
- Tighten RSI thresholds (e.g., `< 5` instead of `< 10`) — would alter signal density; forbidden post-SEAL
- Widen RSI thresholds (e.g., `< 15`) — same restriction
- Switch RSI period (e.g., RSI(3)) — would alter signal density; forbidden post-SEAL
- Convert to long-only / short-only — defeats bi-directional design; structurally different mechanic
- Remove inter-instrument independence assumption (e.g., portfolio-level signal aggregation) — would defeat per-instrument scope structure

----

## 10. DR10-v2-reachability table at PLAN time (NEW framework discipline under v2)

Per the DR10-reachability discipline introduced post-s13-d1 (rev1 plan §3) and updated under DR10 v2 (rev2 plan §3.2), every Tier-N spec PLAN bound by v2 shall include an explicit DR10-v2-reachability calculation evaluating the AND-conjunction.

### 10.1 DR10 v2 binding evaluation criterion

Under DR10 v2: `(annual_turnover > 0.50 AND S2_cost_drag > 0.05) → REJECT_FAST`. The candidate CLEARS DR10 v2 if **EITHER** branch fails to fire (since both must fire for AND to trigger). The cost_drag branch is the binding co-condition for cost-managed strategies.

### 10.2 PLAN-time DR10-v2-reachability table for s14-d1 at DA3=B + DA4=B

| Component | Estimate at PLAN |
|---|---|
| Per-trade notional (MNQ at ~$15k index × $2 multiplier; ~5-10 contracts at 0.5% risk on $100k = ~$30k risk per trade / ($100 ATR × $0.5 tick value) = ~6 contracts × $30k = $180k per MNQ trade; analogous per-instrument) | ~$80-200k per trade (varies by instrument) |
| Per-instrument trades/year | 20-40 (central 30/y) |
| Total trades/year (basket; 70% independence) | 56-112 (central ~84/y) |
| Total round-trip notional/year | ~ $10-30M (per-trade-notional × trades/year × 2 legs) |
| `start_cash` | $100,000 (DA4=B) |
| **Expected `annual_turnover`** | **~100-300** (turnover branch FIRES at >> 0.50; **this alone does NOT fire DR10 v2**) |
| Expected S2 cost_drag (extrapolated from s13-d1's 2.35% at $200k single-MNQ; basket at $100k roughly doubles cost_drag) | **~4-5% (borderline 5% threshold)** |
| **DR10 v2 cost_drag branch status** | **BORDERLINE-TO-CLEARS** (if observed S2 cost_drag < 5%, cost_drag branch DOES NOT fire and AND-conjunction does NOT trigger) |
| **DR10 v2 status at DA3=B + DA4=B** | **CLEARS (CONDITIONAL ON cost_drag BORDERLINE)** — turnover branch alone does not fire DR10 v2; cost_drag branch is the binding co-condition and is borderline 5% |

### 10.3 Sensitivity analysis (DA4 alternative at DRAFT/SEAL)

| DA4 setting | start_cash | Expected S2 cost_drag (scaled from s13-d1 baseline) | DR10 v2 cost_drag branch status | DR10 v2 overall status |
|---|---|---|---|---|
| **B (LOCKED at PLAN)** | $100,000 | ~4-5% | BORDERLINE | **CLEARS conditional** |
| C (alternative at SEAL if BORDERLINE concern) | $200,000 | ~2-3% (s13-d1 baseline at same capital) | CLEARS with margin | CLEARS with margin |
| A (default; NOT proposed) | $50,000 | ~8-10% | FIRES | DR10 v2 FIRES → REJECT_FAST at PLAN |

### 10.4 DR10-v2-reachability disclosure

- **s14-d1 at DA3=B + DA4=B is BORDERLINE on DR10 v2 cost_drag branch.** Conservative estimate ~4-5% at S2 tier; SEAL-time confirmation required before P3 BUILD authorization.
- If at SEAL-time analysis the projected S2 cost_drag exceeds 5%, the operator's options are:
  1. **Revise DA4 to C at SEAL** ($200k; cost_drag scales down to ~2-3%; **NOT T-FORBID-9** because multi-instrument scope alone differentiates)
  2. **Tighten per-trade risk via DA3** (e.g., DA3 = C = 0.25% risk; halves per-trade notional; halves cost_drag at given turnover)
  3. **Reduce universe to 3 instruments** at SEAL (smaller basket; lower total cost flow); requires fresh `candidate_record_id`
- **DR10 v2 mitigation lever for s14-d1** is DA4 capital scaling, which directly reduces the cost_drag branch (the binding co-condition under v2). DA4=C is the conservative path; DA4=B is the borderline path with operator-accepted risk.

----

## 11. Pre-registered S0 edge sign expectations (PLAN-time)

| Field | PLAN-proposed value |
|---|---|
| Expected S0 net PnL sign for MNQ component alone | **Positive** (s13-d1 demonstrated S0 net PnL +$102,795 on single MNQ; PLAN-time prior is strongly positive for MNQ; **NOT a binding pre-registered claim**) |
| Expected S0 net PnL sign for MES/MYM/M2K | **Open question** (PLAN-time; no a-priori claim; high correlation with MNQ suggests similar sign but signal-to-noise ratios may differ) |
| Expected S0 net PnL sign for basket | **Likely positive** (dominated by MNQ if signal-correlation is high; PLAN-time prior; NOT binding) |
| Acceptance threshold S0 net PnL | `> 0` after ≥ 100 trades basket-summed (K9 IS clears reliably; A3 expectancy gate) |
| Acceptance threshold S1 net PnL | `> 0` (K2 fires if `≤ 0`) |
| Pre-registered max-drawdown tolerance | TBD at DRAFT; proposed K4 = 50% magnitude (carried byte-equivalent) |
| Pre-registered cost-stress survival | S0/S1/S2/S3/S4 all positive Sharpe → `ELIGIBLE_FOR_LONGER_BACKTEST`; degradation > 50% S0→S4 → K12 cost-stress concern |
| **DR10 v2 turnover-cost-explosion risk** | **BORDERLINE-CLEARS** at DA4=B; **CLEARS with margin** at DA4=C |
| Cost-stress matrix | 5-tier S0..S4 carried byte-equivalent from s13-d1 SEAL (`0.0/1.0/1.5/2.0/3.0` scalars) |

----

## 12. DR rules adapted for multi-instrument F3 RSI(2) bi-directional under DR10 v2 (LOCKED at SEAL)

Carried byte-equivalent from s13-d1 SEAL chain section 11 with the following adaptations:

- **DR10 binding is v2 AND-conjunction** (not v1 OR-disjunctive) per framework SEAL `78cd22e`
- DR9 evaluated per-instrument (4 instruments × 4-threshold check)
- A7 effective_independent_bets metric becomes load-bearing (multi-symbol)
- K10 (avg pairwise correlation) and K6 (per-symbol dispersion) become evaluable (single-instrument candidates had these as NOT_APPLICABLE)

| Rule | Trigger | Severity | s14-d1 multi-instrument note |
|---|---|---|---|
| DR1 | `oos_rebalance_count < 36` (OOS phase only) | `INCONCLUSIVE_HOLD` | basket-summed |
| DR2 | `oos_metrics_degrade_materially_under_cost_stress` | `REJECT_FAST` | OOS-only; binding at P10 |
| DR3 | `zero_cost_only_survival` (S0 > 0 AND all S1..S4 ≤ 0) | `REJECT_FAST` | **HIGHER prior probability** for RSI lineage (s9-lineage observation); s13-d1 did NOT fire DR3 on single MNQ; multi-instrument is hypothesis-fresh |
| DR4 | `oos_negative_while_is_positive_unexplained` | `REJECT_FAST` | OOS-only |
| DR5 | `cost_stress_turns_edge_negative` (tier flip) | `REJECT_FAST` / `INCONCLUSIVE_HOLD` carveout | binding for high-frequency; s13-d1 did NOT fire DR5 (S4 still positive); multi-instrument is hypothesis-fresh |
| DR6 | `post_warmup_sizing_ambiguity_or_invalid` | `REJECT_FAST` | per-instrument check |
| DR7 | `missing_oos_or_date_window_evidence` | `INCONCLUSIVE_HOLD` | basket-summed |
| DR8 | `live_or_order_routing_path_detected` at Initialize | `HARD_FAIL_VOIDED` | unchanged |
| DR9 | `data_continuity_integrity_check` thresholds 0.95/0.30/5/5 | `INCONCLUSIVE_HOLD` | **per-instrument; 4 separate checks**; ANY instrument failing DR9 triggers the contingency at §3.2 |
| **DR10 v2** | **`turnover_cost_explosion (annual_turnover > 0.50 AND S2_cost_drag > 0.05)`** | `REJECT_FAST` | **Bound by v2 AND-conjunction** (NOT v1 OR); cost_drag branch is binding co-condition; BORDERLINE at DA4=B |
| DR11 | NOT IN CHAIN | -- | F3 has no leverage cap (margin-based); DR11 structurally absent |

DR precedence chain (LOCKED at SEAL; same as s13-d1): `DR7 → DR1 → DR9 → DR10 → DR6 → DR4 → DR2 → DR3 → DR5`.

----

## 13. Sample-size / K9 rules (LOCKED at SEAL)

| Field | LOCKED value |
|---|---|
| K9 threshold | `total_closed_trades_basket_summed ≥ 100` over IS window |
| K9 threshold modification | FORBIDDEN |
| Expected IS basket-summed trade count (4.6y) | **257 / 386 / 514 (low / central / high; 70% signal independence assumption)** — clears K9 with strong margin |
| Expected OOS basket-summed trade count (2.0y) | **112 / 168 / 224 (low / central / high)** — clears K9 with 2-4x margin |
| K9 risk at IS | **VERY LOW** |
| K9 risk at OOS | **LOW** (margin even at lower bound of estimate) |
| K9 inviolacy | FORBIDDEN to relax |

----

## 14. Diversification metrics (LOCKED at SEAL)

Multi-instrument scope makes the following metrics applicable (unlike s12-d1 / s13-d1 single-instrument candidates):

| Metric | Applicability | s14-d1 expected value | Threshold |
|---|---|---|---|
| **A7 effective_independent_bets** | applicable | TBD at SEAL; expected 1.5-2.5 given high equity-index pairwise correlation | TBD |
| **K10 avg_pairwise_correlation** | applicable | TBD at SEAL; expected 0.7-0.9 (US equity-index micros) | K10 thresholds carried from s10-d2 chain |
| **K6 per_symbol_dispersion** | applicable | TBD at SEAL | K6 thresholds carried |
| **A6 concentration_index** | applicable | TBD at SEAL; concern if one instrument dominates PnL (e.g., MNQ-dominance; analogous to s7-D1's USO-dominance pathology) | TBD |

----

## 15. REC1-equivalent OOS K9 disclosure (carried; multi-instrument-adapted)

> **REC1-equivalent (BINDING):** OOS K9 reachable with margin (~112-224 trades at expected per-instrument 20-40/y rate over 2.0y OOS). If observed effective IS rate falls below 12-15 trades/y per instrument (basket-summed below 25/y), OOS K9 unreachability becomes structurally probable. The s13-d1 single-MNQ baseline observed 34.34 trades/y; assuming similar per-instrument rates on MES/MYM/M2K, the 4-instrument basket should comfortably exceed the 25/y critical floor. **If OOS K9 fires anyway, the OOS verdict shall be `OOS_INSUFFICIENT_SAMPLE` or `PARKED_SAFE_BUT_OOS_INDETERMINATE` analogous to S10-D2 / s12-d1 park precedents. The chain shall NOT relax K9 at OOS; the appropriate response is to seal the INSUFFICIENT_SAMPLE verdict and park the candidate.**

----

## 16. Forbidden tracks (T-FORBID-1..12 from rev2 carry verbatim)

All 12 forbidden tracks from the post-s13-d1 next-track selection plans (rev1 commit `30c836e` + rev2 in `ee2bfc1`) carry verbatim. The s14-d1 candidate explicitly clears each:

| T-FORBID | s14-d1 status |
|---|---|
| T-FORBID-1 (re-attempt Donchian-15/8 single MNQ) | NOT VIOLATED (F3 RSI, not F1 Donchian) |
| T-FORBID-2 (s12-d1 _revN_) | NOT VIOLATED |
| T-FORBID-3 (s10-D2 revival via parameter iteration) | NOT VIOLATED (different mechanic; 4-equity-index basket vs s10-d2's 4-market mixed-asset basket) |
| T-FORBID-4 (s10-d1 MGC continuous-stitch revival) | NOT VIOLATED (MGC explicitly excluded) |
| T-FORBID-5 (s9 4-ETF basket revival) | NOT VIOLATED (different asset class; bi-directional) |
| T-FORBID-6 (s7-D1 / T8 ETF-proxy revival) | NOT VIOLATED |
| T-FORBID-7 (B006 SPY vol-targeting revival) | NOT VIOLATED |
| T-FORBID-8 (NKE Options Wheel mechanic revival) | NOT VIOLATED |
| **T-FORBID-9 (s13-d1: RSI(2) bidir single-MNQ DA3=B+DA4=C)** | **NOT VIOLATED** — s14-d1 is MULTI-instrument (universe scope differs) AND DA4=B (DA combination differs); both differentiations independent and individually sufficient |
| **T-FORBID-10 (s13-d1 _revN_ parameter changes)** | **NOT VIOLATED** — fresh `candidate_record_id`; structural changes (universe scope; DA4) materially differ from s13-d1's parameters; not a _revN_ revision |
| T-FORBID-11 (DR10 threshold reinterpretation) | NOT VIOLATED — s14-d1 uses DR10 v2 by-reference (framework SEAL `78cd22e`); thresholds (0.50; 0.05) preserved verbatim |
| **T-FORBID-12 (PLAN-time DR10 failure)** | **CONDITIONALLY CLEARED** under v2 AND — DR10-v2-reachability table §10.2 shows BORDERLINE-CLEARS at DA4=B; SEAL-time confirmation required; DA4=C alternative available if borderline becomes binding |

----

## 17. Boundaries held this PLAN turn

| Boundary | Status |
|---|---|
| PLAN only (no DRAFT / no SEAL / no BUILD / no fetch) | met |
| No strategy code | met |
| No backtest / simulator / signal computation | met |
| No data fetch / Databento call / `DATABENTO_API_KEY` access | met |
| No network IO | met |
| No live trading | met |
| No candidate promotion | met |
| **No retroactive application of DR10 v2 to any existing sealed candidate** | met |
| **No reinterpretation of any existing sealed candidate's verdict** | met |
| **No modification of any existing sealed candidate artifact** (s11-d1 / s12-d1 / s13-d1 SEAL/P1/P2/P3/P4/P6/P6.5/P7 + framework_dr10_revision_seal_v2 byte-stable) | met |
| **No s13-d1 revival** | met |
| **No s12-d1 revival** | met |
| No s10-D2 / s10-d1 / s9 / s7-d1 / B005 / B006 / T8 / NKE revival | met |
| No phase-2 safety contract template modification | met |
| No CLAUDE.md / RUNBOOK / pipeline_manifest / .gitignore modification | met |
| **No `brain_memory/projects/trading_bot/lessons.md` modification or staging** | met |
| No mutation of `review_queue.json` | met |
| No mutation of production `idea_memory` | met |
| No profitability claim | met |
| Trading status | `PAUSED` |
| Live status | `BLOCKED_AT_6_GATES` |
| FRC | `NEVER_GRANTED` |
| `no_strategy_optimization_authorized` | TRUE |
| `no_dr_redefinition_post_seal` (per existing sealed candidates) | TRUE |
| K9-reachability discipline | binding (carried; applied at §9) |
| **DR10-v2-reachability discipline (NEW under v2)** | **binding** (applied at §10) |
| All T-FORBID-1..12 forbidden tracks | carried (see §16); cleared by s14-d1 |
| Universe precommitment at PLAN | `{MNQ.c.0, MES.c.0, MYM.c.0, M2K.c.0}` subject to availability/DR9 gating |
| Mechanic + thresholds + signal direction LOCKED at PLAN | met |
| DA3=B + DA4=B LOCKED at PLAN (DA4=C admissible alternative at SEAL if cost_drag borderline) | met |

----

## 18. Files written this PLAN turn

| File | Purpose |
|---|---|
| `docs/s14_d1_mnq_mes_mym_m2k_multi_instrument_rsi_2_bi_directional_databento_long_history_tier_n_spec_plan.md` | This Tier-N spec PLAN (PLAN only; no JSON sidecar at PLAN phase; no canonical seal sha256 since this is a planning document, not a sealed artifact). |

No other repository file is modified. The `brain_memory/projects/trading_bot/lessons.md` dirty + unstaged state from prior controller sessions remains **untouched**.

----

## 19. Next-phase authorization scope

After operator review of this PLAN, the next-phase authorization shall be one of:

### Primary forward path: DRAFT (after availability gate-passing)

```
Authorize s14-d1 multi-instrument RSI(2) bi-directional Tier-N spec DRAFT only — bound by DR10 v2.
```

**Prerequisite:** operator-side Databento fetch + DR9 audit for MES / MYM / M2K must complete first (operator may issue a separate authorization for the fetch + audit phase). Once 4/4 instruments pass availability/DR9 gates, the DRAFT authorization can proceed. The DRAFT turn expands the DA register (DA1-DA20 analogous to s13-d1), proposes the ATR settings, finalizes K-gate thresholds, and produces a DRAFT artifact at `reports/external_research_hunter/s14_d1_..._tier_n_spec_DRAFT.{json,md}`.

### Availability-gate path (if MES / MYM / M2K not yet acquired)

```
Authorize s14-d1 multi-instrument availability probe + DR9 audit for MES, MYM, M2K only.
```

Operator-side Databento fetch (controller never calls); produces sealed step-02b manifest + per-instrument DR9 audit reports. No backtest, no signal, no candidate-level work in this authorization.

### Contingency path (1+ instrument fails availability/DR9)

```
Authorize s14-d1 shrunk-basket Tier-N spec PLAN only — bound by DR10 v2.
```

Re-author this PLAN under a fresh `candidate_record_id` reflecting the actual passing subset (e.g., 3-instrument basket if M2K fails). NOT authorized in advance by this PLAN.

### Alternative: shift to T2 rev2 cash-equity basket

```
Authorize s14-d1 cash-equity 3-name basket RSI(3) bi-directional Tier-N spec PLAN only — bound by DR10 v2.
```

If the operator decides the multi-instrument micro-futures availability friction outweighs T1 rev2's K9 + mechanic-continuity benefits, T2 rev2 is the co-recommended alternative from the rev2 selection plan.

### Defer

```
Defer / Pause s14-d1 PLAN.
```

Keep the PLAN on file; no DRAFT / availability-probe / contingency work authorized.

----

## 20. Carried-forward status (UNCHANGED across this PLAN turn)

| Field | Value |
|---|---|
| Trading | `PAUSED` |
| Live mode | `BLOCKED_AT_6_GATES` |
| FRC | `NEVER_GRANTED` |
| `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` advisory label applies to this candidate and any descendant | TRUE |
| `no_strategy_optimization_authorized` | TRUE |
| `no_dr_redefinition_post_seal` (per existing sealed candidates) | TRUE |
| s13-d1 lifecycle terminal | TRUE — preserved verbatim under DR10 v1 |
| s12-d1 lifecycle terminal | TRUE — preserved |
| s11-d1 / s10-d2 / s10-d1 / s9 / s7-d1 / B005 / B006 / T8 / NKE byte-stable | TRUE — preserved |
| `framework_dr10_revision_seal_v2` at `78cd22e` | binding for s14+ new SEAL turns |
| `lessons.md` dirty + unstaged + uncommitted (NOT touched this turn) | TRUE |
| K9-reachability discipline | binding |
| **DR10-v2-reachability discipline** | **binding (applied at §10)** |
| s14-d1 lifecycle state | `S14_D1_TIER_N_SPEC_PLAN_AUTHORED` (this PLAN turn) |
| Next-phase contingency | availability gate for MES / MYM / M2K must pass before DRAFT |

----

End of PLAN. PLAN-authoring turn only. No code. No backtest. No simulator. No signal. No data fetch. No Databento. No `DATABENTO_API_KEY` access. No QC. No LEAN. No brokerage. No real order. No paper order. No Strategy Lab promotion. No `review_queue` mutation. No production `idea_memory` mutation. **No retroactive application of DR10 v2 to existing candidates. No s13-d1 / s12-d1 / parked-candidate revival. No `lessons.md` modification or staging.** No live trading. Trading remains `PAUSED`. Live remains `BLOCKED_AT_6_GATES`. FRC `NEVER_GRANTED`. s13-d1 + s12-d1 lifecycles terminal preserved verbatim. Universe precommitted subject to availability/DR9 gating.
