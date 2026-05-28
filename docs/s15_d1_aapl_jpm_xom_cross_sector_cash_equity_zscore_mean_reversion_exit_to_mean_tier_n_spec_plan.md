# s15 D1 AAPL + JPM + XOM Cross-Sector Cash-Equity Z-Score Mean-Reversion **Exit-to-Mean** Tier-N Specification Plan

Status: **PLAN_ONLY** (no code written, no spec drafted, no spec sealed, no data fetched by this plan; the next step is a separate operator authorization to commit this PLAN, then a Tier-N spec DRAFT).

Authored: 2026-05-28
Authorization phrase: `Authorize s15-d1 cross-sector cash-equity z-score mean-reversion exit-to-mean Tier-N spec PLAN only — bound by DR10 v2.`

Origin: Track **T1** of the selection plan `docs/next_research_track_selection_plan_after_s14_d1_cross_sector_terminal.md` (commit `89d6838`), the strongest-scored (59/70) next track after `s14-d1-aapl-jpm-xom-cross-sector-cash-equity-rsi-3-bi-directional-large-cap-long-history` terminated `FAIL_SAFETY` (P7 memo `6485ea9`). This is a **FRESH CANDIDATE** with a distinct `candidate_record_id`, **NOT a `_revN_` or patch** of the terminal s14-d1-cross-sector candidate.

Framework binding: **DR10 v2 AND-conjunction** (framework SEAL `78cd22e`). DR10 in this candidate's eventual SEAL shall carry the v2 definition verbatim. NO retroactive application to existing sealed candidates.

----

## HARD BOUNDARIES (held by this PLAN)

PLAN only. No DRAFT. No SEAL. No code. No backtest. No simulator. No signal computation. No data fetch. No yfinance / Tiingo / vendor API call. No API-key access. No network IO. No `review_queue.json` mutation. No production `idea_memory` mutation. No Strategy Lab run. No candidate promotion. **No `_revN_` / patch / parameter-iteration of s14-d1-cross-sector** (its RSI(3)+2N mechanic is terminal). **No revival of s14-d1-cross-sector / s13-d1 / s12-d1 / any parked candidate.** **No modification of any existing sealed artifact** (s14-d1-cross-sector SEAL/P1/P2/P3/P4/P6/P7; all-tech sibling DRAFT `214bae0`; multi-instrument chain; s13-d1 / s12-d1 chains; `framework_dr10_revision_seal_v2` `78cd22e` — all byte-stable). No reinterpretation of any sealed verdict. No phase-2 safety contract template modification. No CLAUDE.md / `.gitignore` modification. **No `brain_memory/projects/trading_bot/lessons.md` modification or staging.** No git commit by this PLAN turn (commit is a separate authorization). **No strategy parameter optimization / grid search** (`no_strategy_optimization_authorized`); all parameters below are first-principles proposals to be justified (not tuned) at SEAL. No live trading. No profitability claim. Trading remains `PAUSED`. Live remains `BLOCKED_AT_6_GATES`. FRC `NEVER_GRANTED`.

----

## 1. Purpose

Author a Tier-N specification PLAN for a **non-RSI z-score / Bollinger-band mean-reversion** candidate whose **exit and stop are first-principles aligned with the mean-reversion thesis**, on the **same DR9-passed AAPL/JPM/XOM cross-sector universe** that s14-d1-cross-sector used.

s14-d1-cross-sector cleared every structural gate (DR10-v2, K9-OOS, DR9, A7/K10 diversification) yet failed `FAIL_SAFETY` on per-trade edge (K1 sharpe_proxy/trade −0.1119; K2 expectancy −$39.53). Root cause (LESSON_S14_D1_002/003): an RSI(3) entry paired with a **hard 2N ATR stop** that truncated the reversion — winners exited small at the RSI mid-band, losers ran to the full 2N stop. This candidate **changes only the falsified component (the exit/stop mechanic)** while **holding the proven-diversified universe constant**, so the next experiment isolates exactly the variable that failed.

This PLAN does NOT seal the spec, does NOT fetch data, and does NOT modify any sealed artifact.

----

## 2. Candidate identification

| Field | Proposed value (LOCKED at PLAN unless noted) |
|---|---|
| `candidate_record_id` | **`s15-d1-aapl-jpm-xom-cross-sector-cash-equity-zscore-mean-reversion-exit-to-mean`** |
| `candidate_family` | **F-new: z-score / Bollinger-band mean-reversion with exit-to-mean** (NON-RSI; LOCKED at PLAN) |
| `is_a_single_instrument_candidate` | false — multi-name cross-sector basket |
| `is_a_s14_d1_cross_sector_revision` | **false** — different mechanic FAMILY (z-score vs RSI(3)); different exit (exit-to-mean vs RSI-threshold); different stop (vol-scaled catastrophe vs fixed 2N). Distinct `candidate_record_id`. The s14-d1-cross-sector chain is preserved terminal/byte-stable. NOT a `_revN_`. |
| `is_a_s14_d1_all_tech_revision` | false — different mechanic family; all-tech DRAFT `214bae0` preserved byte-stable |
| `is_a_s13_d1_revision` | false — non-RSI; orthogonal mechanic |
| `is_a_s9_revision` | false — single-name cross-sector basket, non-RSI mean-reversion (z-score), bi-directional |
| `predecessor_lineage_references_read_only` | `s14_d1_cross_sector_terminal` (FAIL_SAFETY; P7 `6485ea9`), `s14_d1_all_tech_draft` (`214bae0`), `s14_d1_multi_instrument_chain`, `s13_d1_p7_terminal`, `s12_d1_p11_park`, `phase_2_safety_contract_template_C1_C8`, `framework_dr10_revision_seal_v2`, `next_track_selection_plan_after_s14_d1_cross_sector_terminal` (`89d6838`) |
| `diagnostic_only` | true |
| `default_advisory_label` | `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` |
| Exit/stop-first-principles discipline applied at PLAN (NEW binding axis) | **TRUE** |
| K9-reachability discipline applied at PLAN | TRUE |
| DR9 status | **ALREADY PASSED** for AAPL/JPM/XOM (reuse sealed CSVs; `b13af03`) |
| DR10-v2-reachability discipline applied at PLAN | TRUE |
| Framework DR10 binding | **v2 AND-conjunction** (`78cd22e`) |

----

## 3. The NEW binding axis — first-principles exit/stop edge design

This is the load-bearing section per LESSON_S14_D1_002/003 and the selection plan (`89d6838` §1.1). The selection plan established that **exit/stop edge design is the binding scoring axis** because s14-d1-cross-sector showed K9/DR9/DR10/A7/K10 can all pass while a mis-designed exit/stop still produces FAIL_SAFETY.

### 3.1 What s14-d1-cross-sector got wrong (the falsified design)

| Component | s14-d1-cross-sector (terminal) | Why it failed |
|---|---|---|
| Exit | RSI(3) crosses 55 (long) / 45 (short) — an **arbitrary oscillator threshold**, not the actual reversion target | Winners closed early for small gains before full mean recovery |
| Stop | **fixed 2N ATR hard stop** | Tight stop hit before the reversion completed → losers ran to 2N while winners were capped small → profit/loss ratio < 1 → negative expectancy despite 54.31% win rate |

### 3.2 First-principles fix (this candidate's exit/stop)

| Component | s15-d1 design | First-principles rationale |
|---|---|---|
| **Exit = exit-to-mean** | Close the position when price re-crosses the rolling mean (the Bollinger midline / SMA_L). | **The exit IS the thesis.** A mean-reversion trade's natural target is the mean itself, not an arbitrary oscillator level. Holding to the mean captures the full reversion the entry predicted. |
| **Stop = vol-scaled catastrophe brake** | Stop at `entry ∓ S·σ_L` with `S ≈ 3.5` (wider than the `k≈2.0` entry band); NOT a fixed 2N. | The stop is a **disaster brake for a broken thesis** (price extends far past entry instead of reverting), not a primary exit. Set wide enough (≈1.5σ beyond the entry band) that normal reversion is not truncated, while still capping tail risk. Scales with volatility so it adapts across regimes (no fixed-distance truncation in high vol). |
| **Time-stop fallback** | Max-hold `M ≈ 10` bars; if the mean is not recovered within the reversion horizon, exit flat. | Mean-reversion should resolve within a bounded horizon; an indefinite hold means the thesis has silently failed. Principled cap, not a tuned parameter. |
| **Sizing = vol-normalized** | `shares = floor(risk_$ / (S·σ_L))`, `risk_$ = 0.5% · equity`. | Sizing keyed to the actual stop distance (S·σ), so per-trade risk is constant in dollar terms and consistent with the vol-scaled stop — not keyed to a fixed ATR multiple. |

### 3.3 Why this is expected to avoid the s14-d1 failure mode

The s14-d1 negative expectancy came from `avg_win` (small, RSI-mid exit) < `|avg_loss|` (large, 2N stop). Under exit-to-mean, the winner target moves from "RSI crosses mid" to "price reaches the mean" — a **larger, thesis-aligned capture**. The catastrophe stop at ≈3.5σ is **hit far less often** than a 2N stop and only when the reversion thesis is genuinely broken. The expected effect is `avg_win` ↑ and stop-frequency ↓, moving profit/loss ratio toward/above 1. **This is a hypothesis to be tested at P6 IS, not a claim** — but it is a first-principles-justified design, which is exactly what LESSON_S14_D1_003 requires before SEAL.

----

## 4. Strategy mechanic family LOCKED at PLAN: F-new z-score / Bollinger mean-reversion, exit-to-mean

| Field | Proposed LOCKED value at PLAN (first-principles; to be confirmed not tuned at SEAL) |
|---|---|
| Mechanic family | z-score / Bollinger-band mean-reversion (NON-RSI) |
| Lookback `L` | **20** (Bollinger standard; not optimized) |
| Band / z multiple `k` (entry) | **2.0** (Bollinger standard 2σ; not optimized) |
| Entry long | `z = (close − SMA_L)/σ_L ≤ −k` (price below lower band) |
| Entry short | `z ≥ +k` (price above upper band) |
| **Exit-to-mean** | long: close `≥ SMA_L`; short: close `≤ SMA_L` (re-cross of the rolling mean) |
| **Catastrophe stop** | `entry ∓ S·σ_L`, `S = 3.5` (vol-scaled; wider than entry band; NOT fixed 2N) |
| **Time-stop** | max-hold `M = 10` bars (fallback) |
| Signal direction | bi-directional (long+short symmetric) per-name |
| Per-name max positions | `max_positions_per_name = 1` |
| Portfolio max positions | `max_total_positions = 3` |
| Inter-name signal coordination | NONE (per-name independent) |
| Pyramid | NONE |
| Sizing | vol-normalized: `shares = floor((0.005·equity) / (S·σ_L))` |
| DA3 per-trade risk pct | `B = 0.005` (0.5%) — carried as proven-safe |
| DA4 START_CASH (proposed) | `B = $100,000` |
| Warmup | ≥ `L + margin` (proposed 30 bars) |

### 4.1 First-principles burden vs predecessors (this candidate is genuinely fresh)

- **vs s14-d1-cross-sector (terminal):** NON-RSI mechanic family (z-score vs RSI(3)); exit-to-mean vs RSI-threshold exit; vol-scaled catastrophe stop vs fixed 2N. The universe is held constant **deliberately, to isolate the exit/stop variable** — clean A/B experimental design, NOT a parameter patch. Clears **T-FORBID-13** (not RSI(3)+2N), **T-FORBID-14** (not a `_revN_`; different mechanic family), **T-FORBID-15** (exit/stop is first-principles justified per §3).
- **vs s13-d1:** non-RSI; orthogonal mechanic.
- **vs s9 / s7-D1:** single-name cross-sector basket, non-RSI z-score mean-reversion; different granularity/mechanic; s7-D1 concentration lesson addressed by the proven-balanced cross-sector basket (A7/K10 already measured in-band).

----

## 5. Universe precommitment (LOCKED at PLAN) — REUSE the DR9-passed cross-sector CSVs

| Field | LOCKED at PLAN value |
|---|---|
| Universe | **`{AAPL, JPM, XOM}`** (Tech / Financials / Energy) — identical to s14-d1-cross-sector, held constant by design |
| Data source | **REUSE the DR9-PASSED sealed CSVs** at `data/s14_d1_aapl_jpm_xom_cross_sector_cash_equity_long_history/raw/` (sealed `b13af03`): AAPL sha `f6625ff1…`, JPM sha `8aa244ab…`, XOM sha `fbbc462c…` |
| Adjustment convention | `split_only` (carry; reuse same CSVs; AAPL 2020-08-31 4:1 already applied+verified) |
| Vendor | tiingo (data already fetched; no new fetch) |
| **Fresh fetch required?** | **NO** — zero data-scope friction; DR9 already PASSED all 3 (sealed `b13af03`, result_seal `a8ff9126…`) |
| Universe widening / substitution post-SEAL | FORBIDDEN (fresh `candidate_record_id` required) |

Holding the universe constant is intentional: the s14-d1-cross-sector basket's diversification was *not* the failure (A7 2.09 / K10 0.4529 measured in-band). Reusing it isolates the exit/stop mechanic as the single changed variable.

----

## 6. Corporate-action profile (carried; already DR9-verified)

AAPL 2020-08-31 4:1 split applied+verified; JPM/XOM no splits in window; dividends NOT adjusted (`split_only`). All three already PASSED DR9 at `b13af03`. No new corporate-action audit required (data reused byte-equivalent). Confirmation that the sealed CSV shas match will occur at DRAFT/BUILD time via the reused `data_csv_registry`.

----

## 7. K9-reachability table at PLAN

z-score|2σ| daily mean-reversion is moderately frequent; exit-to-mean trades resolve within the reversion horizon (typically faster than an oscillator-threshold exit).

| Window | Length (y) | Required trades/y (basket) | Per-name expected | 3-name basket expected | K9 status |
|---|---:|---|---|---|---|
| IS (2019-01-02 → 2023-12-29) | ~5.0 | ≥ 20 | ~20-35/y | ~60-105/y | **CLEARS with strong margin** |
| **OOS (2024-01-02 → 2025-12-30)** | **~2.0** | **≥ 50** | ~20-35/y | ~60-105/y | **CLEARS** |

REC1-equivalent (BINDING; carried): if observed effective IS rate < 25/y basket-summed → OOS K9 unreachability structurally probable → PARK per precedent. Expected ~60-105/y comfortably exceeds the 25/y floor. **K9 is not expected to be the binding low** (the binding axis is exit/stop edge design per §3).

----

## 8. DR10-v2-reachability table at PLAN

| Component | Estimate |
|---|---|
| Expected annual_turnover | ~25-50 (turnover branch fires alone; non-binding under AND) |
| Expected S2 cost_drag | ~0.3-0.6% (cash-equity per-share commission; well under 5%) |
| **DR10 v2 status** | **CLEARS WITH STRONG MARGIN** (cost_drag branch does not fire; AND-conjunction not triggered) |

----

## 9. Diagnostic / diversification metrics (carried LOAD-BEARING; universe held constant)

A7 effective_independent_bets, K10 avg_pairwise_correlation, K6 per-symbol dispersion remain LOAD-BEARING and are expected to land in the same bands measured for s14-d1-cross-sector (A7 ~2.09, K10 ~0.45) since the universe is identical. These are **not** the candidate's risk axis this time (they already passed); the risk axis is per-trade edge under the new exit/stop design (§3).

----

## 10. DR register + K-gates (carried byte-equivalent; DR10 = v2)

DR register, DR precedence chain (`DR7 → DR1 → DR9 → DR10 → DR6 → DR4 → DR2 → DR3 → DR5`), and K-gates (K1/K2/K4/K6/K7/K8/K9/K10/K12; K11 NOT_APPLICABLE no leverage cap; DR11 NOT IN CHAIN for unlevered cash equity) carry byte-equivalent from the cross-sector lineage, with:
- DR9 = already PASSED all 3 (reuse; sealed `b13af03`)
- DR10 = v2 AND-conjunction by-reference (`78cd22e`)
- K1 (sharpe_proxy < 0) and K2 (expectancy ≤ 0) are the gates s14-d1-cross-sector failed; **this candidate's entire design thesis is to clear them via the §3 exit/stop redesign** — to be tested at P6 IS, never assumed.

----

## 11. Boundaries held this PLAN turn

| Boundary | Status |
|---|---|
| PLAN only (no DRAFT / SEAL / BUILD / fetch / backtest / OOS) | met |
| No data fetch / vendor API / API-key access (data reused) | met |
| No signal computation / simulator | met |
| **No `_revN_` / patch / parameter-iteration of s14-d1-cross-sector** | met |
| **No strategy parameter optimization / grid search** (params are first-principles proposals) | met |
| **No revival of s14-d1-cross-sector / s13-d1 / s12-d1 / parked candidates** | met |
| **No modification of any sealed artifact** (s14-d1-cross-sector chain, all-tech DRAFT 214bae0, multi-instrument, s13/s12, DR10 v2 78cd22e byte-stable) | met |
| No reinterpretation of any sealed verdict | met |
| No phase-2 safety contract template / CLAUDE.md / .gitignore modification | met |
| **No `brain_memory/projects/trading_bot/lessons.md` modification or staging** | met |
| No git commit by this PLAN turn | met (commit is a separate authorization) |
| No `review_queue` / `idea_memory` mutation | met |
| No profitability claim | met |
| Trading / Live / FRC | `PAUSED` / `BLOCKED_AT_6_GATES` / `NEVER_GRANTED` |
| Exit/stop-first-principles + K9 + DR10-v2 disciplines applied at PLAN | TRUE |
| T-FORBID-1..15 (incl. 13/14/15) cleared | TRUE |

----

## 12. Files written this PLAN turn

| File | Purpose |
|---|---|
| `docs/s15_d1_aapl_jpm_xom_cross_sector_cash_equity_zscore_mean_reversion_exit_to_mean_tier_n_spec_plan.md` | This Tier-N spec PLAN (PLAN only; no JSON sidecar at PLAN phase; no canonical seal sha256; NOT committed by this turn) |

No other repository file is modified. All sealed artifacts and `lessons.md` are untouched.

----

## 13. Next-step authorization scope

### Commit this PLAN (recommended first step)

```
Authorize commit s15-d1 cross-sector cash-equity z-score exit-to-mean Tier-N spec PLAN only.
```

### Proceed to DRAFT (no fresh fetch needed — data reused)

```
Authorize s15-d1 cross-sector cash-equity z-score exit-to-mean Tier-N spec DRAFT only — bound by DR10 v2.
```

Authors the DRAFT, which will formalize the §3 exit/stop design and the §4 DA register (first-principles justified, not tuned), reusing the DR9-passed cross-sector CSVs. No fetch / DR9 re-audit needed (data already sealed at `b13af03`).

### Defer

```
Defer / Pause s15-d1 cross-sector cash-equity PLAN.
```

----

## 14. Carried-forward status (UNCHANGED across this PLAN turn)

| Field | Value |
|---|---|
| Trading / Live / FRC | `PAUSED` / `BLOCKED_AT_6_GATES` / `NEVER_GRANTED` |
| `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` | applies to this candidate + descendants |
| `no_strategy_optimization_authorized` | TRUE |
| `no_dr_redefinition_post_seal` (existing sealed candidates) | TRUE |
| s14-d1-cross-sector lifecycle terminal (FAIL_SAFETY; P7 `6485ea9`) | TRUE — preserved verbatim; NOT revived/patched |
| all-tech sibling DRAFT `214bae0` | byte-stable; NOT advanced (shares the failed RSI(3)+2N mechanic) |
| s14-d1-multi-instrument / s13-d1 / s12-d1 chains | byte-stable; preserved |
| `framework_dr10_revision_seal_v2` `78cd22e` | binding for s15+ |
| LESSON_S14_D1_001/002/003 committed at `5085d2a` | cited as design source; not modified |
| DR9-passed cross-sector CSVs (`b13af03`) | reused byte-equivalent; no fresh fetch |
| K9-reachability + DR10-v2-reachability + exit/stop-first-principles disciplines | binding |
| s15-d1 lifecycle state | `S15_D1_CROSS_SECTOR_CASH_EQUITY_ZSCORE_EXIT_TO_MEAN_TIER_N_SPEC_PLAN_AUTHORED` (this PLAN turn; NOT committed) |

----

End of PLAN. PLAN-authoring turn only. No code. No backtest. No fetch. No vendor API. No DRAFT. No SEAL. No BUILD. No commit. No strategy optimization. **No `_revN_`/patch/revival of s14-d1-cross-sector or any terminal/parked candidate. No modification of any sealed artifact. No `lessons.md` modification or staging.** Trading remains `PAUSED`. Live remains `BLOCKED_AT_6_GATES`. FRC `NEVER_GRANTED`. Fresh candidate; the new binding axis is first-principles exit/stop edge design (§3); universe held constant (DR9-passed, reused) to isolate the falsified exit/stop variable.
