# s14 D1 AAPL + MSFT + NVDA Cash-Equity 3-Name Basket RSI(3) Bi-Directional Large-Cap Long-History Tier-N Specification Plan

Status: **PLAN_ONLY** (no code written, no spec drafted, no spec sealed, no data fetched by this plan; the next step is a separate operator authorization to DRAFT the Tier-N spec).

Authored: 2026-05-27
Authorization phrase: `Authorize s14-d1 cash-equity 3-name basket RSI(3) bi-directional Tier-N spec PLAN only — bound by DR10 v2.`

Selection-plan source: `docs/next_research_track_selection_plan_after_s13_d1_terminal_rev2_under_dr10_v2.md` (committed in `ee2bfc1`; **T2 rev2 co-recommended at 43/60** alongside T1 rev2 multi-instrument basket).

Framework binding: this candidate is authored **under DR10 v2 AND-conjunction** (framework SEAL at commit `78cd22e`; `report_seal_sha256` `7794bb5222ed2a2cb1cd8e1ef2f43f3d1abc6f1539d71af31dda32d832b5e907`). DR10 in this candidate's eventual SEAL shall carry the v2 definition verbatim. **NO retroactive application** to existing sealed candidates.

Pivot context: the parallel T1 rev2 multi-instrument micro-futures basket (s14-d1 PLAN at commit `5376de7` + RUN_BOOK at `13ff641`) is structurally blocked at the operator-side Databento fetch gate as of 2026-05-27 (operator cannot perform Databento fetch at this time). T2 rev2 cash-equity is the documented fallback per the rev2 selection plan §7 "Recommended secondary (if T1 rev2 is rejected or blocked)" and is now the active forward path. The T1 rev2 PLAN + RUN_BOOK + decline memos remain on file byte-stable.

Predecessor terminal / parked candidates (READ-ONLY; not modified by this plan):
- `s14-d1-mnq-mes-mym-m2k-multi-instrument-rsi-2-bi-directional-databento-long-history` PLAN — gate-blocked (PLAN at `5376de7`, RUN_BOOK at `13ff641`, v1 decline at `c812c53`, v2 decline at `0063e8a`). **Not revived; not _revN_; cash-equity scope is orthogonal universe entirely.**
- `s13-d1-mnq-c0-single-instrument-rsi-2-bi-directional-databento-long-history` terminal REJECT_FAST at P7 (commit `cc1817b`). **Not revived; orthogonal universe + slower RSI period.**
- `s12-d1` / `s11-d1` / `s10-d2` / `s10-d1` / `s9` / `s7-d1` / `B005_NNN` / `B006_001/002` / T8 / NKE — READ-ONLY byte-stable.

Audit-clean data anchors:
- **NONE pre-existing for AAPL, MSFT, NVDA cash-equity OHLCV.** Fresh operator-side OHLCV fetch is required at next phase (vendor TBD at SEAL: yfinance / Polygon free tier / Tiingo / Alpha Vantage; cost-surface and provenance will be different from Databento futures and require equity-specific DR9-equivalent audit framework).

----

## HARD BOUNDARIES (held by this PLAN)

PLAN only. No DRAFT. No SEAL. No code. No backtest. No simulator. No signal computation. No data fetch. No yfinance / Yahoo Finance call. No Databento call. No `DATABENTO_API_KEY` access. No QC / LEAN call. No network IO. No `review_queue.json` mutation. No production `idea_memory` mutation. No Strategy Lab run. No candidate promotion. **No s13-d1 revival.** **No s14-d1 multi-instrument PLAN modification** (PLAN at `5376de7` + RUN_BOOK at `13ff641` + v1/v2 decline memos byte-stable). **No retroactive application of DR10 v2 to any existing sealed candidate.** **No reinterpretation of any existing sealed candidate's verdict.** **No modification of any existing sealed candidate artifact** (s11-d1 / s12-d1 / s13-d1 SEAL/P1/P2/P3/P4/P6/P6.5/P7 + framework_dr10_revision_seal_v2 + s14-d1 multi-instrument PLAN/RUN_BOOK/declines all byte-stable). No s12-d1 revival. No s10-d2 / s10-d1 / s9 / s7-d1 / B005_NNN / B006_NNN / T8 / NKE sealed-artifact modification. No phase-2 safety contract template modification. No CLAUDE.md modification. No RUNBOOK modification. No `pipeline_manifest` modification. No `.gitignore` modification. **No `brain_memory/projects/trading_bot/lessons.md` modification or staging.** No branch change. No git push. No live trading. No profitability claim. Trading remains `PAUSED`. Live remains `BLOCKED_AT_6_GATES`. FRC `NEVER_GRANTED`.

----

## 1. Purpose

Author a Tier-N specification PLAN for the **second fresh candidate** under the DR10 v2 AND-conjunction framework (the first being s14-d1 multi-instrument micro-futures basket, currently gate-blocked). The candidate is a 3-name cash-equity basket using the **Connors RSI(3) bi-directional mean-reversion mechanic** (F3-adjacent; slower RSI period than s13-d1's RSI(2)).

This PLAN locks the **mechanic family, RSI thresholds, universe (precommitted), signal direction, sizing scheme, pyramid policy** AT PLAN time. The DRAFT and SEAL turns (separate authorizations) shall further lock operational parameters (ATR settings, cost-stress matrix, K-gate thresholds, output schema, OHLCV vendor selection).

The PLAN does NOT seal the spec. No code, no data fetch, no vendor API call, no backtest, no OOS inspection, no broker / live / Strategy Lab interaction is performed by this PLAN.

----

## 2. Candidate identification

| Field | Proposed value (LOCKED at PLAN unless noted) |
|---|---|
| `candidate_record_id` | **`s14-d1-aapl-msft-nvda-cash-equity-rsi-3-bi-directional-large-cap-long-history`** |
| `candidate_family` | **F3-adjacent RSI(3) bi-directional mean-reversion** (LOCKED at PLAN; slower RSI period than s13-d1's RSI(2); cash-equity asset class is structurally orthogonal to s9 ETF-proxy + s13-d1 micro-futures) |
| `is_a_trade_candidate` | true |
| `is_a_single_instrument_candidate` | **false** — load-bearing structural property: **multi-name basket** |
| `is_a_s13_d1_revision` | **false** (s13-d1 was MNQ.c.0 single futures; s14-d1-cash-equity is `{AAPL, MSFT, NVDA}` cash equity — orthogonal asset class + orthogonal universe + slower RSI period) |
| `is_a_s13_d1_revN_revision` | **false** |
| `is_a_s14_d1_multi_instrument_revision` | **false** (multi-instrument micro-futures basket vs cash-equity basket — orthogonal asset class; both are fresh candidates under DR10 v2; not _revN_ of each other; both have distinct `candidate_record_id`s) |
| `is_a_s12_d1_revision` | false |
| `is_a_s11_d1_revision` | false |
| `is_a_s10_d2_revision` | false |
| `is_a_s10_d1_revision` | false |
| `is_a_s9_revision` | **false** (s9 was 4-ETF basket SPY/TLT/GLD/USO long-only; s14-d1-cash-equity is single-name large-cap basket bi-directional; different universe + different asset granularity + different signal direction + slower RSI period) |
| `is_a_s7_d1_revision` | false (s7-D1 was ETF basket; this is single-name equity basket) |
| `is_a_b006_NNN_extension` | false (B006 was SPY vol-targeting; orthogonal mechanic) |
| `predecessor_lineage_references_read_only` | `s14_d1_multi_instrument_plan` (gate-blocked), `s13_d1_p7_terminal`, `s12_d1_p11_park`, `s11_d1_v1_rev2_chain`, `s10_d2_park`, `s10_d1_park`, `s9_rsi2_etf_proxy_park`, `s7_d1_park`, `b005_b006_archival`, `t8_nke_archive`, `phase_2_safety_contract_template_C1_C8`, `framework_dr10_revision_seal_v2` |
| `diagnostic_only` | true |
| `not_promotable_via_this_diagnostic` | true |
| `default_advisory_label` | `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` |
| Selection-plan source score (rev2) | **43 / 60** (co-recommended primary alongside T1 rev2 multi-instrument basket) |
| K9-reachability discipline applied at PLAN time | **TRUE** |
| **DR10-v2-reachability discipline applied at PLAN time** | **TRUE** |
| REC1-equivalent OOS-K9 disclosure carried | TRUE (with cash-equity adjustment; see §9.4) |
| **Framework DR10 binding** | **v2 AND-conjunction (NOT v1)** per `framework_dr10_revision_seal_v2` at commit `78cd22e` |

----

## 3. Universe precommitment (LOCKED at PLAN; operator may revise shortlist at DRAFT/SEAL with first-principles justification)

| Field | LOCKED at PLAN value |
|---|---|
| Universe type | `multi_name_large_cap_cash_equity_basket` |
| Symbol 1 | **`AAPL`** (Apple Inc.; large-cap tech; CIK 0000320193) |
| Symbol 2 | **`MSFT`** (Microsoft Corp.; large-cap tech; CIK 0000789019) |
| Symbol 3 | **`NVDA`** (NVIDIA Corp.; large-cap tech; CIK 0001045810) |
| Symbol count at PLAN | exactly 3 |
| Universe widening at later phases | FORBIDDEN (any wider basket = fresh `candidate_record_id`) |
| Universe substitution at later phases | OPERATOR-REVISABLE at DRAFT with explicit first-principles justification; FORBIDDEN post-SEAL |
| Per-symbol diversification claim | LIMITED (all 3 are mega-cap US tech; pairwise correlation expected high; A7 effective-independent-bets is LOAD-BEARING at SEAL) |
| Cross-sector diversification | NONE (all tech) — operator may revise to cross-sector basket (e.g., `{AAPL, JPM, XOM}`) at DRAFT for stronger A7 |
| K10 / K6 / A7 / A6 metrics applicability | **applicable** (multi-name basket; carries from s10-d2 / s7-D1 lineage) |

### 3.1 Universe-choice rationale (operator-revisable)

The PLAN-time choice of `{AAPL, MSFT, NVDA}` is the example shortlist from the rev2 selection plan T2 rev2 description. Trade-offs:

**Pros of AAPL/MSFT/NVDA same-sector basket:**
- High liquidity; small bid-ask spreads; reliable OHLCV from any major vendor
- Similar cost-surface across all 3 names (simpler S2 cost-drag calibration)
- Clean fresh universe (no overlap with s7-D1 / s9 / B006 forbidden universes)
- Continuous trading history extends back decades (no common-history-start concern)

**Cons:**
- High pairwise correlation (~0.7-0.85 expected) → low A7 effective_independent_bets (~1.5-2.0)
- Same-sector concentration risk (e.g., 2025-04-style tech selloff would hit all 3 simultaneously)
- DR10-related concern: similar signal patterns across all 3 names → trades may co-fire → effective trade count lower than naive 3× per-name rate

**Alternative cross-sector basket (operator may propose at DRAFT):**
- `{AAPL (tech), JPM (financials), XOM (energy)}` — lower correlation; higher A7; stronger diversification
- `{AAPL, JPM, JNJ}` — tech/finance/healthcare; similar A7 benefit
- Cross-sector adds first-principles strength but may add data-vendor complexity (different sector cost-surfaces)

### 3.2 Universe-substitution policy at DRAFT

Operator may revise the shortlist at DRAFT with documented first-principles justification (e.g., "switching from same-sector tech to cross-sector for stronger A7"). Substitution post-SEAL is FORBIDDEN.

----

## 4. Strategy mechanic family LOCKED at PLAN: F3-adjacent Connors RSI(3) bi-directional

s14-d1-cash-equity LOCKS the mechanic family AT PLAN time. The candidate's load-bearing structural properties are (a) **per-name independent RSI(3) bi-directional signal generation**, (b) **cash-equity asset class**, and (c) **slower RSI period than s13-d1's RSI(2)**. Any of these changes would defeat the fresh-candidate justification.

### 4.1 Mechanic primitives (LOCKED at PLAN)

| Field | LOCKED value at PLAN |
|---|---|
| Mechanic family | **F3-adjacent RSI(3) bi-directional mean-reversion** |
| RSI computation | **Connors RSI(3)** (3-period RSI; Wilder smoothing on close-to-close returns) per-name independent — **slower period than s13-d1's RSI(2)** |
| **RSI long entry threshold** | **`< 15`** (oversold; less extreme than s13-d1's `< 10` because RSI(3) has narrower distribution) |
| **RSI long exit threshold** | **`> 55`** (mean-reversion complete; tighter than s13-d1's `> 50`) |
| **RSI short entry threshold** | **`> 85`** (overbought; symmetric to long entry) |
| **RSI short exit threshold** | **`< 45`** (mean-reversion complete; tighter than s13-d1's `< 50`) |
| Signal direction | **bi-directional** (long+short symmetric thresholds) per-name |
| Per-name max units (positions) | **`max_positions_per_name = 1`** (no pyramid per signal per name) |
| Portfolio-level max positions | **`max_total_positions = 3`** (one per name; full basket max) |
| Inter-name signal coordination | **NONE** — each name's RSI/ATR/signal generation is INDEPENDENT |
| Stop method | ATR-based 2N stop (carried byte-equivalent from s13-d1 SEAL adapted for cash equity) |
| Risk method | per-trade risk percentage of portfolio equity, sized via per-name ATR; per-name independent sizing (carried byte-equivalent adapted for cash equity); subject to portfolio-level cap |
| Pyramid mechanism | **NONE** (per-name structurally forbidden via `max_positions_per_name = 1`) |

### 4.2 Why s14-d1-cash-equity is NOT a rescue of s13-d1 (first-principles burden)

| s13-d1 falsification feature | s14-d1-cash-equity treatment |
|---|---|
| Universe = `{MNQ.c.0}` (single MICRO-FUTURES contract) | Universe = `{AAPL, MSFT, NVDA}` (3 single-name CASH EQUITIES; **orthogonal asset class**) |
| RSI(2) period; thresholds 10/50/90/50 | **RSI(3)** period (slower); thresholds 15/55/85/45 (tighter) |
| DA4 = C (`$200k` start_cash) | DA4 LOCKED at SEAL; PLAN-time proposal DA4=B (`$100k`); cash-equity cost surface is structurally lower-drag than futures contract-quantization |
| Fired DR10 v1 OR-disjunctive turnover branch | s14-d1-cash-equity is bound by **DR10 v2 AND-conjunction**; cash-equity cost_drag branch is structurally well below 5% (per-share commission ~$0.005 + small bid-ask spread is tiny fraction of equity notional) |

**First-principles claim:** s13-d1's DR10 v1 firing was specific to micro-futures contract-quantization + OR-disjunctive DR10. Under cash-equity sizing (fine-grained share counts; tiny per-share commission relative to notional) + DR10 v2 (AND-conjunction; cost_drag branch is binding co-condition; trivially clears for cash equity), the structural constraint is removed. s14-d1-cash-equity tests whether the RSI mean-reversion edge transfers to a cash-equity multi-name basket with operator-friendlier data access.

### 4.3 Why s14-d1-cash-equity is NOT a rescue of s9 (first-principles burden)

| s9 falsification feature | s14-d1-cash-equity treatment |
|---|---|
| Universe = SPY/TLT/GLD/USO (4-ETF basket; **mixed asset classes**: equity ETF + bond ETF + commodity ETFs) | Universe = `{AAPL, MSFT, NVDA}` (3 single-name large-cap equities; **single asset class; single-name vs ETF granularity**) |
| Long-only | **Bi-directional** (long+short symmetric thresholds); structural asymmetry break |
| RSI(2) period; thresholds 10/50/90/50 (with original s9 thresholds for long entry only) | **RSI(3)** period (slower); thresholds 15/55/85/45; bi-directional |
| Cost surface: per-share commission + bps slippage on ETFs | Cost surface: per-share commission + half-bid-ask on single-name large-caps (similar structure but DIFFERENT specific cost levels; AAPL/MSFT/NVDA have tighter spreads than mid-cap ETFs) |
| S0 edge negative (-$1,211 over 414 trades) | S0 edge sign on s14-d1-cash-equity is **open question**; no a-priori claim; s13-d1's S0-positive single-MNQ result is partial validation but does not transfer mechanically |
| Falsification cause: instrument-specific cost/edge interaction on equity ETFs + long-only asymmetry | s14-d1-cash-equity tests slower RSI + bi-directional + single-name granularity (vs ETF granularity) |

**First-principles claim:** the s9 falsification does NOT transfer to s14-d1-cash-equity because (a) the universe granularity differs (single-name large-caps vs ETF basket), (b) the signal direction differs (bi-directional vs long-only), (c) the RSI period differs (RSI(3) slower than RSI(2)), and (d) the cost surface differs at the specific-name level even if the cost-structure category (per-share) is similar.

### 4.4 Why s14-d1-cash-equity is NOT a rescue of s14-d1-multi-instrument (gate-blocked sibling)

The s14-d1 multi-instrument PLAN at `5376de7` is currently gate-blocked at operator-side Databento fetch. s14-d1-cash-equity is the documented fallback per the rev2 selection plan but is a **structurally distinct fresh candidate**, not a `_revN_` of the multi-instrument variant:

| Field | s14-d1 multi-instrument | s14-d1-cash-equity |
|---|---|---|
| Asset class | micro-futures | cash equity |
| Universe | `{MNQ.c.0, MES.c.0, MYM.c.0, M2K.c.0}` | `{AAPL, MSFT, NVDA}` |
| Mechanic family | F3 RSI(2) bi-directional | F3-adjacent RSI(3) bi-directional |
| RSI thresholds | 10/50/90/50 | 15/55/85/45 |
| Vendor | Databento (paid) | yfinance / Polygon free / Tiingo (operator selects at DRAFT) |
| `candidate_record_id` | distinct | distinct |

Each is a separate fresh candidate. Both PLANs remain valid; the operator chooses which (or both, sequentially or in parallel) to advance to DRAFT. s14-d1-cash-equity's PLAN does NOT modify, supersede, or revive the multi-instrument PLAN.

----

## 5. Data assumptions (LOCKED at SEAL; vendor selection at DRAFT)

| Field | Proposed value (LOCKED at SEAL) |
|---|---|
| Vendor | **TBD at DRAFT** — operator selects from {yfinance / Polygon free tier / Tiingo / Alpha Vantage / paid vendor}. **No paid-vendor dependency at PLAN** (operator-side fetch is the binding constraint; vendor must support OHLCV daily for all 3 names over the IS+OOS windows). |
| Schema | **`ohlcv-daily`** (daily aggregate bars per name; fields: `date`, `open`, `high`, `low`, `close`, `volume`, optional `adjusted_close`) |
| Adjustment convention | **TBD at DRAFT** — operator must precommit either (a) split-adjusted only OR (b) split+dividend-adjusted; CANNOT mix or switch post-SEAL |
| Symbols requested | `["AAPL", "MSFT", "NVDA"]` (or operator-revised shortlist at DRAFT) |
| **Pre-existing audit-clean CSV reuse** | **FALSE** — no AAPL/MSFT/NVDA cash-equity OHLCV exists in the repo audit chain. Fresh operator-side fetch required at next phase. |
| API key handling at any phase | operator-side only; controller never accesses any vendor API key |
| Controller-side vendor call at any phase | **LOCKED OFF** |

----

## 6. Schema + adjustment convention (LOCKED at SEAL)

| Field | LOCKED value |
|---|---|
| Schema | `ohlcv-daily` |
| Fields | `date`, `open`, `high`, `low`, `close`, `volume`, optional `adjusted_close` |
| Adjustment convention | TBD at DRAFT; operator MUST precommit at SEAL (cannot mix or switch post-SEAL) |
| Intraday schemas | OUT OF SCOPE for this Tier-N |
| Per-name common-history start | TBD at availability probe (operator-side); expected ≥ 2010-01-01 for all 3 names (mega-cap tech with long public-trading history) |

----

## 7. IS / OOS windows (LOCKED at SEAL; subject to common-history intersection + operator preference)

| Field | LOCKED value (TBD at SEAL; PLAN-time proposal) |
|---|---|
| Proposed IS window start | `2019-01-02` (proposed — gives ~5y IS; operator may revise to a longer window if data allows) |
| Proposed IS window end | `2023-12-29` |
| Proposed IS window length | ~5.0 years |
| Proposed OOS window start (never inspected at IS) | `2024-01-02` |
| Proposed OOS window end (never inspected at IS) | `2025-12-30` |
| Proposed OOS window length | ~2.0 years |
| OOS inspection at IS phase | FORBIDDEN (`oos_inspection_blocked_at_in_sample` invariant per-name) |
| Common-history adjustment at SEAL | if any name has a later inception date, the IS window start shifts forward; the OOS window shifts proportionally |

----

## 8. Sizing precommitment (LOCKED at PLAN; LOCKED at SEAL)

| Field | LOCKED at PLAN value | Rationale |
|---|---|---|
| **DA3 (per-trade risk percentage)** | **`B` (= 0.5%)** | **Standard** — not nano. Under DR10 v2, the cost_drag branch (very low on cash equity due to tiny per-share commission relative to notional) is the binding co-condition; nano-sizing is NOT required to clear DR10 v2 on cash equity (unlike the rev1 plan's T1 cash-equity proposal which required nano under DR10 v1) |
| **DA4 (`START_CASH_USD`)** | **TBD at DRAFT; PLAN-time proposal `B` (= $100,000)** | Operator may select B ($100k) or higher at DRAFT/SEAL. PLAN-time math at $100k shows DR10 v2 clears with strong margin |
| Per-name max positions | `max_positions_per_name = 1` | LOCKED at PLAN |
| Portfolio-level max positions | `max_total_positions = 3` | LOCKED at PLAN |
| Per-name independent sizing | TRUE | Each name's shares = `floor(risk_pct × equity / (ATR × price_proxy))` per-name |
| Portfolio-level cap | basket equity-protection rule TBD at DRAFT | Not LOCKED at PLAN |

----

## 9. K9-reachability table at PLAN time (binding framework discipline)

### 9.1 Required trade-count thresholds (carried byte-equivalent from s11-lineage)

| Window | Length (y) | Required closed_trades/year for K9=100 | Status threshold |
|---|---:|---|---|
| IS | ~5.0 | ≥ 20.0 trades/y | K9_IS_REACHABLE if ≥ |
| **OOS** | **~2.0** | **≥ 50.0 trades/y** (BINDING) | **K9_OOS_REACHABLE if ≥** |

### 9.2 Expected trade count for s14-d1-cash-equity RSI(3) bi-directional on 3-name large-cap basket

**Per-name signal density basis (PLAN-time estimate; subject to P6 IS confirmation):**

- Connors RSI(3) on large-cap US equities historically produces ~20-35 trades/year per name when bi-directional (long+short symmetric thresholds 15/85). Tighter thresholds (15/85 vs s13-d1's 10/90) yield slightly higher signal density than s13-d1's RSI(2) at the per-event basis because the tighter thresholds catch more events even though the slower period dampens noise.
- Hand-wave estimate: AAPL/MSFT/NVDA expected ~25-35/y per name (large-cap with active vol regimes through 2020-2023; recent NVDA vol regime is elevated).
- Per-name signal independence: **NOT structurally guaranteed** — same-sector basket (all tech) has high pairwise return correlation (~0.7-0.85). Conservatively estimate signal independence at **~60%** (lower than the multi-instrument micro-futures basket's 70% because tech is more correlated than the 4 equity-index micros which span large-cap/mid-cap/Dow/small-cap).

### 9.3 K9-reachability assessment for s14-d1-cash-equity

| Window | Required trades/y | Expected per-name trades/y (low / central / high) | Effective 3-name total (at 60% independence) | Expected total trades | K9 status |
|---|---|---|---|---|---|
| IS (5.0y) | ≥ 20.0 | 20 / 28 / 35 | 36 / 50 / 63 | 180 / 250 / 315 | **CLEARS K9 WITH MARGIN** (~9-16x the floor) |
| **OOS (2.0y)** | **≥ 50.0** | **20 / 28 / 35** | **36 / 50 / 63** | **72 / 100 / 126** | **CLEARS K9** at central/high estimate (~1.4-2.5x the floor); **BORDERLINE at low estimate** (36 < 50) |

### 9.4 K9-reachability disclosure

- s14-d1-cash-equity has **strong K9 IS margin** but **borderline-to-clearing K9 OOS** at the lower-bound estimate.
- If at P6 IS execution the observed effective rate falls below 25 trades/y basket-summed, OOS K9 unreachability becomes structurally probable.
- **REC1-equivalent disclosure for s14-d1-cash-equity:** if observed effective IS rate < 25/y basket-summed (i.e., per-name effective < ~14/y given 60% independence assumption), OOS K9 fires structurally. Expected central effective rate is 50/y — exactly at the floor. **K9 OOS risk is MODERATE.** Lower-bound observation requires PARK per REC1-binding precedent (s10-d2 / s12-d1).

### 9.5 K9 mitigation levers if observed rate borderline at IS

The following are explicitly NOT authorized by this PLAN (per `no_strategy_optimization_authorized`):

- Add a 4th name to widen the basket — would alter A7/K10 metrics; forbidden post-SEAL; requires fresh `candidate_record_id`
- Tighten RSI thresholds — would alter signal density; forbidden post-SEAL
- Switch RSI period to RSI(2) — would defeat the slower-period justification vs s13-d1; structurally different mechanic
- Switch to cross-sector basket — admissible at DRAFT only (operator must propose), forbidden post-SEAL

----

## 10. DR10-v2-reachability table at PLAN time (NEW framework discipline under v2)

Per the DR10-reachability discipline introduced post-s13-d1 (rev1 plan §3) and updated under DR10 v2 (rev2 plan §3.2), every Tier-N spec PLAN bound by v2 shall include an explicit DR10-v2-reachability calculation evaluating the AND-conjunction.

### 10.1 DR10 v2 binding evaluation criterion

Under DR10 v2: `(annual_turnover > 0.50 AND S2_cost_drag > 0.05) → REJECT_FAST`. The candidate CLEARS DR10 v2 if **EITHER** branch fails to fire (since both must fire for AND to trigger). The cost_drag branch is the binding co-condition for cost-managed strategies.

### 10.2 PLAN-time DR10-v2-reachability table for s14-d1-cash-equity at DA3=B + DA4=B

| Component | Estimate at PLAN |
|---|---|
| Per-trade notional per name (AAPL @ ~$200 × 200 shares ≈ $40k; MSFT @ ~$400 × 100 shares ≈ $40k; NVDA @ ~$130 × 300 shares ≈ $40k; risk-based sizing at 0.5% of $100k = $500 risk per trade / ATR estimates) | ~$30-50k per trade per name |
| Per-name trades/year | 20-35 (central 28/y) |
| Total trades/year (basket; 60% independence) | 36-63 (central ~50/y) |
| Total round-trip notional/year | ~$3-6M (per-trade-notional × trades/year × 2 legs) |
| `start_cash` | $100,000 (DA4=B) |
| **Expected `annual_turnover`** | **~30-60** (turnover branch FIRES at >> 0.50; **this alone does NOT fire DR10 v2**) |
| **Expected S2 cost_drag** (per-share commission ~$0.005 × ~200 shares × 50 trades × 2 legs ≈ $100/y per name × 3 names = ~$300/y at S1; at S2 cost_scalar 1.5 = ~$450/y; cost_drag = $450 / $100k = **0.45%**) | **~0.3-0.6% at S2** (very low; well under 5% threshold) |
| **DR10 v2 cost_drag branch status** | **CLEARS WITH STRONG MARGIN** (~0.5% << 5%) |
| **DR10 v2 status at DA3=B + DA4=B** | **CLEARS WITH STRONG MARGIN** — turnover branch fires alone but cost_drag branch DOES NOT fire; AND-conjunction does NOT trigger |

### 10.3 Comparison to s14-d1 multi-instrument micro-futures DR10 v2 status

| Candidate | Expected S2 cost_drag at DA4=B | DR10 v2 status |
|---|---|---|
| s14-d1 multi-instrument (futures) | ~4-5% (borderline 5% threshold) | CLEARS CONDITIONAL |
| **s14-d1-cash-equity** | **~0.3-0.6%** | **CLEARS WITH STRONG MARGIN** |

**Implication:** s14-d1-cash-equity has a STRUCTURALLY STRONGER DR10 v2 cost_drag margin than the multi-instrument futures alternative. The cash-equity cost surface (tiny per-share commission relative to notional) is the load-bearing reason. This is the rev2 selection plan's load-bearing finding for T2 rev2 scoring (DR10 v2 = 9/10 for cash equity vs 7/10 for multi-instrument futures).

### 10.4 DR10-v2-reachability disclosure

- s14-d1-cash-equity is **structurally well-positioned** to clear DR10 v2 at any practical retail-scale start_cash ($100k–$1M+) at standard 0.5% risk sizing.
- The DR10 v2 mitigation lever (DA4 capital scaling) is NOT needed here — cost_drag is already structurally low. DA4=B at $100k is sufficient; DA4=C at $200k would push cost_drag even lower (~0.15-0.3%).

----

## 11. Pre-registered S0 edge sign expectations (PLAN-time)

| Field | PLAN-proposed value |
|---|---|
| Expected S0 net PnL sign for the 3-name basket | **Open question** (PLAN-time; no a-priori claim) — s13-d1's S0-positive result on single MNQ provides partial precedent for RSI mean-reversion edge on a single index instrument, but cash-equity single-name behavior may differ |
| Acceptance threshold S0 net PnL | `> 0` after ≥ 100 trades basket-summed (K9 IS clears reliably; A3 expectancy gate) |
| Acceptance threshold S1 net PnL | `> 0` (K2 fires if `≤ 0`) |
| Pre-registered max-drawdown tolerance | TBD at DRAFT; proposed K4 = 50% magnitude (carried byte-equivalent) |
| Pre-registered cost-stress survival | S0/S1/S2/S3/S4 all positive Sharpe → `ELIGIBLE_FOR_LONGER_BACKTEST`; degradation > 50% S0→S4 → K12 cost-stress concern |
| **DR10 v2 turnover-cost-explosion risk** | **CLEARS with strong margin** at DA4=B |
| Cost-stress matrix | 5-tier S0..S4 carried byte-equivalent from s13-d1 SEAL (`0.0/1.0/1.5/2.0/3.0` scalars) |

----

## 12. DR rules adapted for multi-name F3 RSI(3) bi-directional under DR10 v2 (LOCKED at SEAL)

Carried byte-equivalent from s13-d1 SEAL chain with the following adaptations:

- **DR10 binding is v2 AND-conjunction** (not v1 OR-disjunctive) per framework SEAL `78cd22e`
- DR9 evaluated per-name (3 names × 4-threshold check)
- A7 effective_independent_bets metric is LOAD-BEARING (multi-name + same-sector tech basket; high pairwise correlation expected)
- K10 (avg pairwise correlation) and K6 (per-symbol dispersion) are LOAD-BEARING

| Rule | Trigger | Severity | s14-d1-cash-equity multi-name note |
|---|---|---|---|
| DR1 | `oos_rebalance_count < 36` (OOS phase only) | `INCONCLUSIVE_HOLD` | basket-summed |
| DR2 | `oos_metrics_degrade_materially_under_cost_stress` | `REJECT_FAST` | OOS-only; binding at P10 |
| DR3 | `zero_cost_only_survival` (S0 > 0 AND all S1..S4 ≤ 0) | `REJECT_FAST` | **HIGHER prior probability** for RSI lineage (s9-lineage observation); s13-d1 did NOT fire DR3 on single MNQ; cash-equity multi-name is hypothesis-fresh |
| DR4 | `oos_negative_while_is_positive_unexplained` | `REJECT_FAST` | OOS-only |
| DR5 | `cost_stress_turns_edge_negative` (tier flip) | `REJECT_FAST` / `INCONCLUSIVE_HOLD` carveout | binding for high-frequency; lower risk for cash-equity due to low cost_drag |
| DR6 | `post_warmup_sizing_ambiguity_or_invalid` | `REJECT_FAST` | per-name check |
| DR7 | `missing_oos_or_date_window_evidence` | `INCONCLUSIVE_HOLD` | basket-summed |
| DR8 | `live_or_order_routing_path_detected` at Initialize | `HARD_FAIL_VOIDED` | unchanged |
| DR9 | `data_continuity_integrity_check` thresholds 0.95/0.30/5/5 | `INCONCLUSIVE_HOLD` | **per-name; 3 separate checks**; cash equity data continuity expected clean (major US large-caps; vendor-dependent for exact gap behavior) |
| **DR10 v2** | **`turnover_cost_explosion (annual_turnover > 0.50 AND S2_cost_drag > 0.05)`** | `REJECT_FAST` | **Bound by v2 AND-conjunction**; CLEARS with strong margin at DA4=B |
| DR11 | NOT IN CHAIN | -- | F3 has no leverage cap (cash equity unlevered); DR11 structurally absent |

DR precedence chain (LOCKED at SEAL; same as s13-d1): `DR7 → DR1 → DR9 → DR10 → DR6 → DR4 → DR2 → DR3 → DR5`.

----

## 13. Sample-size / K9 rules (LOCKED at SEAL)

| Field | LOCKED value |
|---|---|
| K9 threshold | `total_closed_trades_basket_summed ≥ 100` over IS window |
| K9 threshold modification | FORBIDDEN |
| Expected IS basket-summed trade count (5.0y) | **180 / 250 / 315 (low / central / high; 60% signal independence assumption)** — clears K9 with margin |
| Expected OOS basket-summed trade count (2.0y) | **72 / 100 / 126 (low / central / high)** — clears K9 at central/high; BORDERLINE at low (36 < 50/y floor) |
| K9 risk at IS | LOW (clears with margin even at low end) |
| K9 risk at OOS | **MODERATE** (borderline at low end of estimate band) |
| K9 inviolacy | FORBIDDEN to relax |

----

## 14. Diversification metrics (LOCKED at SEAL)

Multi-name basket makes the following metrics applicable and LOAD-BEARING:

| Metric | Applicability | s14-d1-cash-equity expected value | Threshold |
|---|---|---|---|
| **A7 effective_independent_bets** | applicable | TBD at SEAL; expected **1.5-2.0** given high tech-sector pairwise correlation (potential concern) | TBD |
| **K10 avg_pairwise_correlation** | applicable | TBD at SEAL; expected **0.7-0.85** (US large-cap tech) | K10 thresholds carried from s10-d2 chain |
| **K6 per_symbol_dispersion** | applicable | TBD at SEAL | K6 thresholds carried |
| **A6 concentration_index** | applicable | TBD at SEAL; concern if NVDA dominates PnL (recent vol regime concentration) — analogous to s7-D1's USO-dominance pathology | TBD |

**A7 concern is the load-bearing diversification risk for this basket.** Cross-sector substitution at DRAFT (e.g., `{AAPL, JPM, XOM}`) would substantially improve A7 at the cost of mixed-cost-surface complexity. Operator decision at DRAFT.

----

## 15. REC1-equivalent OOS K9 disclosure (carried; cash-equity-adapted)

> **REC1-equivalent (BINDING):** OOS K9 reachable at central/high estimate (~100-126 trades at expected per-name 25-35/y rate × 60% independence × 2.0y OOS) but **BORDERLINE at low-bound estimate** (~72 trades). If observed effective IS rate falls below 25 trades/y per name (basket-summed below 36/y), OOS K9 unreachability becomes structurally probable. The s13-d1 single-MNQ baseline observed 34.34 trades/y on a faster RSI(2); RSI(3) slower period combined with cash-equity vol regime is hypothesis-fresh. **If OOS K9 fires anyway, the OOS verdict shall be `OOS_INSUFFICIENT_SAMPLE` or `PARKED_SAFE_BUT_OOS_INDETERMINATE` analogous to S10-D2 / s12-d1 park precedents. The chain shall NOT relax K9 at OOS; the appropriate response is to seal the INSUFFICIENT_SAMPLE verdict and park the candidate.**

----

## 16. Forbidden tracks (T-FORBID-1..12 from rev2 carry verbatim)

All 12 forbidden tracks from the post-s13-d1 next-track selection plans carry verbatim. The s14-d1-cash-equity candidate explicitly clears each:

| T-FORBID | s14-d1-cash-equity status |
|---|---|
| T-FORBID-1 (re-attempt Donchian-15/8 single MNQ) | NOT VIOLATED (F3 RSI(3), not F1 Donchian; cash equity not futures) |
| T-FORBID-2 (s12-d1 _revN_) | NOT VIOLATED |
| T-FORBID-3 (s10-D2 revival via parameter iteration) | NOT VIOLATED |
| T-FORBID-4 (s10-d1 MGC continuous-stitch revival) | NOT VIOLATED |
| T-FORBID-5 (s9 4-ETF SPY/TLT/GLD/USO basket revival) | NOT VIOLATED (`{AAPL, MSFT, NVDA}` single-name basket, NOT 4-ETF basket) |
| T-FORBID-6 (s7-D1 / T8 ETF-proxy on SPY/TLT/GLD/USO) | NOT VIOLATED |
| T-FORBID-7 (B006 SPY vol-targeting) | NOT VIOLATED (different mechanic; SPY not in universe) |
| T-FORBID-8 (NKE Options Wheel mechanic) | NOT VIOLATED |
| T-FORBID-9 (s13-d1: RSI(2) bidir single-MNQ DA3=B+DA4=C) | NOT VIOLATED (cash equity, not single MNQ; different RSI period) |
| T-FORBID-10 (s13-d1 _revN_ parameter changes) | NOT VIOLATED (fresh candidate_record_id; orthogonal asset class) |
| T-FORBID-11 (DR10 threshold reinterpretation) | NOT VIOLATED (uses DR10 v2 by-reference) |
| T-FORBID-12 (PLAN-time DR10 failure under v2) | **CLEARED with strong margin** (§10 DR10-v2-reachability table shows CLEARS WITH STRONG MARGIN) |

----

## 17. Boundaries held this PLAN turn

| Boundary | Status |
|---|---|
| PLAN only (no DRAFT / no SEAL / no BUILD / no fetch) | met |
| No strategy code | met |
| No backtest / simulator / signal computation | met |
| No data fetch / vendor API call | met |
| No network IO | met |
| No live trading | met |
| No candidate promotion | met |
| **No retroactive application of DR10 v2 to any existing sealed candidate** | met |
| **No reinterpretation of any existing sealed candidate's verdict** | met |
| **No modification of any existing sealed candidate artifact** (s11-d1 / s12-d1 / s13-d1 + framework_dr10_revision_seal_v2 + s14-d1 multi-instrument PLAN/RUN_BOOK/declines byte-stable) | met |
| **No s13-d1 revival** | met |
| **No s12-d1 revival** | met |
| **No s14-d1 multi-instrument PLAN modification** | met |
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
| K9-reachability discipline | binding (applied at §9) |
| **DR10-v2-reachability discipline** | **binding (applied at §10; CLEARS WITH STRONG MARGIN)** |
| All T-FORBID-1..12 forbidden tracks | carried (see §16); cleared by s14-d1-cash-equity |
| Universe precommitment at PLAN | `{AAPL, MSFT, NVDA}` (operator-revisable at DRAFT with first-principles justification) |
| Mechanic + thresholds + signal direction LOCKED at PLAN | met |
| DA3=B LOCKED at PLAN; DA4 TBD at DRAFT (PLAN-time proposal DA4=B) | met |

----

## 18. Files written this PLAN turn

| File | Purpose |
|---|---|
| `docs/s14_d1_aapl_msft_nvda_cash_equity_rsi_3_bi_directional_large_cap_long_history_tier_n_spec_plan.md` | This Tier-N spec PLAN (PLAN only; no JSON sidecar at PLAN phase; no canonical seal sha256). |

No other repository file is modified. The `brain_memory/projects/trading_bot/lessons.md` dirty + unstaged state from prior controller sessions remains **untouched**.

----

## 19. Next-phase authorization scope

After operator review of this PLAN, the next-phase authorization shall be one of:

### Primary forward path: availability probe + DR9 audit framework

```
Authorize s14-d1-cash-equity multi-name OHLCV availability probe + DR9 audit framework only.
```

Authors a RUN_BOOK analogous to the s14-d1 multi-instrument RUN_BOOK at `13ff641`, adapted for cash-equity OHLCV. Vendor selection (yfinance / Polygon / Tiingo / etc.) precommitted at the RUN_BOOK level. **Likely operator-friendlier than the Databento futures fetch** — most candidate vendors have free tiers or low-cost API access.

### Primary forward path (if operator confident in vendor + skip probe): DRAFT

```
Authorize s14-d1-cash-equity Tier-N spec DRAFT only — bound by DR10 v2.
```

Skips the explicit probe phase and goes directly to DRAFT (expands DA register DA1-DA20, finalizes ATR settings + K-gate thresholds + cost-stress matrix calibration). Operator must complete OHLCV fetch + DR9 audit before P3 BUILD. NOT RECOMMENDED unless operator is confident in vendor + universe choice.

### Universe revision

```
Authorize s14-d1-cash-equity universe revision to cross-sector basket — bound by DR10 v2.
```

Re-authors this PLAN with cross-sector universe (e.g., `{AAPL, JPM, XOM}`) under a fresh `candidate_record_id` for stronger A7. NOT a `_revN_` of THIS PLAN; produces a fresh sibling PLAN.

### Defer / pause

```
Defer / Pause s14-d1-cash-equity PLAN.
```

Keep the PLAN on file; no further work authorized.

### Sibling: revisit s14-d1 multi-instrument if Databento access restored

If/when operator-side Databento fetch capacity is restored, the s14-d1 multi-instrument PLAN at `5376de7` remains valid and can be re-authorized via the existing RUN_BOOK §4 unblock path. The two PLANs (multi-instrument futures + cash-equity) are non-mutually-exclusive — both can advance to DRAFT independently or in parallel.

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
| s14-d1 multi-instrument PLAN at `5376de7` + RUN_BOOK at `13ff641` + v1 decline at `c812c53` + v2 decline at `0063e8a` | byte-stable; PLAN remains valid pending operator-side Databento access restoration |
| `framework_dr10_revision_seal_v2` at `78cd22e` | binding for s14+ new SEAL turns |
| `lessons.md` dirty + unstaged + uncommitted (NOT touched this turn) | TRUE |
| K9-reachability discipline | binding |
| **DR10-v2-reachability discipline** | **binding (CLEARS WITH STRONG MARGIN for s14-d1-cash-equity)** |
| s14-d1-cash-equity lifecycle state | `S14_D1_CASH_EQUITY_TIER_N_SPEC_PLAN_AUTHORED` (this PLAN turn) |
| Operator-side Databento fetch capacity as of 2026-05-27 | NOT AVAILABLE (per project memory `project_s14_d1_blocked_no_databento_fetch.md`) |
| Cash-equity OHLCV vendor selection at next phase | TBD at RUN_BOOK / DRAFT; operator-friendlier than Databento futures fetch (free-tier vendors available) |

----

End of PLAN. PLAN-authoring turn only. No code. No backtest. No simulator. No signal. No data fetch. No vendor API call. No `DATABENTO_API_KEY` access. No QC. No LEAN. No brokerage. No real order. No paper order. No Strategy Lab promotion. No `review_queue` mutation. No production `idea_memory` mutation. **No retroactive application of DR10 v2 to existing candidates. No s13-d1 / s12-d1 / parked-candidate revival. No s14-d1 multi-instrument PLAN modification. No `lessons.md` modification or staging.** No live trading. Trading remains `PAUSED`. Live remains `BLOCKED_AT_6_GATES`. FRC `NEVER_GRANTED`. s13-d1 + s12-d1 lifecycles terminal preserved verbatim. Universe precommitted operator-revisable at DRAFT. DR10 v2 CLEARS WITH STRONG MARGIN at PLAN-time analysis.
