# s16 D1 Expanded Cross-Sector Cash-Equity Donchian Breakout Trend (Trailing-Stop) Tier-N Specification Plan

Status: **PLAN_ONLY** (no code written, no spec drafted, no spec sealed, no data fetched by this plan; the next step is a separate operator authorization to commit this PLAN, then a Tier-N spec DRAFT).

Authored: 2026-05-28
Authorization phrase: `Authorize s16-d1 expanded-universe Tier-N spec PLAN only — bound by DR10 v2.`
Origin: Track **T1** of the post-s15 selection plan (`343bdac`) — a NON-mean-reversion mechanic on a K9-clearing universe — now realized on the **12-name expanded cross-sector basket** whose DR9 audit PASSED all 12 (result_seal `ec856253`, committed `245ac0d`). This is a **FRESH s16 candidate**, NOT a `_revN_`/patch of any prior candidate.

Framework binding: **DR10 v2 AND-conjunction** (framework SEAL `78cd22e`).

----

## HARD BOUNDARIES (held by this PLAN)

PLAN only. No DRAFT. No SEAL. No code. No backtest. No simulator. No signal computation. No data fetch (12-name basket already fetched + DR9-PASSED at `245ac0d`; reuse only). No vendor API / API-key access. No network IO. No `review_queue.json` / `idea_memory` mutation. No Strategy Lab run. No candidate promotion. **No mean-reversion mechanic (T-FORBID-17/18: no RSI(3)+2N, no z-score exit-to-mean, no daily mean-reversion tweak on this universe).** **No `_revN_`/patch of s15-d1 / s14-d1-cross-sector (T-FORBID-16).** **No revival of s15/s14/s13/s12.** **No modification of any existing sealed artifact** (incl. the s16 DR9 result `245ac0d` and the 12 sealed CSVs). **No strategy parameter optimization / grid search** (`no_strategy_optimization_authorized`); parameters below are first-principles proposals to justify (not tune) at SEAL. No CLAUDE.md / `.gitignore` modification. **No `brain_memory/projects/trading_bot/lessons.md` modification or staging.** No git commit by this PLAN turn. No live trading. No profitability claim. Trading `PAUSED` · Live `BLOCKED_AT_6_GATES` · FRC `NEVER_GRANTED`.

----

## 1. Purpose

Author a Tier-N specification PLAN for a **trend-following Donchian channel breakout** (bi-directional, trailing-stop) candidate on the 12-name DR9-passed expanded cross-sector cash-equity basket.

This is the **family-level fix** for the s14/s15 finding (LESSON_S15_D1_002/003): two distinct *mean-reversion* mechanics failed FAIL_SAFETY on the 3-name AAPL/JPM/XOM basket because the mean-reversion edge there was structurally absent. A trend-following mechanic has the **opposite trade geometry** (ride winners with a trailing stop; cut losers fast) and is a genuinely different family. The 3-name basket made trend K9-light; the **12-name basket resolves that** (DR9-passed at `245ac0d`).

----

## 2. Candidate identification

| Field | Proposed value (LOCKED at PLAN unless noted) |
|---|---|
| `candidate_record_id` | **`s16-d1-expanded-cross-sector-cash-equity-donchian-breakout-trend-trailing-stop-large-cap-long-history`** |
| `candidate_family` | **F-trend: Donchian channel breakout (bi-directional) with trailing exit channel + ATR initial stop** (NON-mean-reversion; LOCKED at PLAN) |
| `is_a_mean_reversion_candidate` | **false** — trend-following; opposite geometry to s14/s15 |
| `is_a_s15_or_s14_revision` | **false** — different mechanic FAMILY and different (12-name) universe; clears T-FORBID-16/17/18 |
| `predecessor_lineage_references_read_only` | `s16_expanded_dr9_result` (`245ac0d`), `s16_run_book` (`4bcc396`), `selection_plan_after_s15` (`343bdac`), `s15_d1_p7_terminal` (`8abcd31`), `s14_d1_cross_sector_p7_terminal` (`6485ea9`), `phase_2_safety_contract_template_C1_C8`, `framework_dr10_revision_seal_v2` (`78cd22e`) |
| `diagnostic_only` | true · `default_advisory_label` `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` |
| Exit/stop-first-principles discipline applied at PLAN | **TRUE** (trend trailing-stop; §4) |
| K9-reachability discipline applied at PLAN | **TRUE** (§6 — the load-bearing axis this candidate was built to satisfy) |
| DR9 status | **ALREADY PASSED all 12** (reuse sealed CSVs; `245ac0d` / result_seal `ec856253`) |
| DR10-v2-reachability discipline applied at PLAN | **TRUE** (§7) |
| Framework DR10 binding | **v2 AND-conjunction** (`78cd22e`) |

----

## 3. Universe precommitment (LOCKED at PLAN; 12-name DR9-passed; reuse)

| Field | LOCKED at PLAN value |
|---|---|
| Universe | **{AAPL, MSFT, NVDA, JPM, XOM, UNH, WMT, KO, META, AMZN, JNJ, CVX}** (12 names) |
| Sectors spanned | Information Technology (AAPL/MSFT/NVDA), Financials (JPM), Energy (XOM/CVX), Health Care (UNH/JNJ), Consumer Staples (WMT/KO), Communication Services (META), Consumer Discretionary (AMZN) — ~7 GICS sectors |
| Data source | **REUSE the 12 DR9-PASSED sealed CSVs** at `data/s16_d1_expanded_cross_sector_cash_equity_long_history/raw/` (`245ac0d`; manifest sha `2825a762`; result_seal `ec856253`) |
| Adjustment convention | `split_only` (AMZN 20:1 + WMT 3:1 + NVDA 4:1/10:1 + AAPL 4:1 applied/verified; JNJ Kenvue spin-off informational) |
| Vendor | tiingo (already fetched) · **Fresh fetch required? NO** |
| Universe widening/substitution post-SEAL | FORBIDDEN (fresh `candidate_record_id` required) |

----

## 4. Strategy mechanic family LOCKED at PLAN: F-trend Donchian breakout, trailing stop

| Field | Proposed LOCKED value at PLAN (first-principles; confirm not tune at SEAL) |
|---|---|
| Mechanic family | Donchian channel breakout, bi-directional, trend-following |
| Entry channel `N_entry` | **20** (enter long when close > prior 20-day high; short when close < prior 20-day low) |
| Trailing exit channel `N_exit` | **10** (exit long when close < prior 10-day low; exit short when close > prior 10-day high) — the trend-following **trailing stop** |
| Initial catastrophe stop | **2 × ATR(14)** from entry (floor; whichever of trailing-channel / ATR-stop triggers first) |
| Signal direction | bi-directional (long+short) per-name |
| Per-name max positions | `max_positions_per_name = 1` |
| Portfolio max positions | `max_total_positions = 6` (≤50% of the 12-name universe concurrently deployed; diversified trend exposure with concentration cap) |
| Inter-name coordination | NONE (per-name independent) · Pyramid | NONE |
| Sizing | vol-normalized: `shares = floor((0.005·equity) / (2·ATR14))` (DA3=B 0.5% risk per name) |
| DA4 START_CASH (proposed) | `B = $100,000` |
| Warmup | ≥ `max(N_entry, ATR period) + margin` (proposed 40 bars) |

### 4.1 First-principles exit/stop edge design (the binding axis, trend variant)

s14/s15 failed because a *mean-reversion* entry was paired with an exit/stop that fought the thesis. A **trend** mechanic inverts the geometry, and its first-principles exit IS a trailing stop:

- **Exit = trailing Donchian channel (N_exit=10):** the position stays open while the trend persists and closes only when price reverses through the opposite 10-day channel — *let winners run, cut losers*. This is aligned with the trend thesis (the exact opposite of mean-reversion's exit-to-mean).
- **Initial stop = 2×ATR(14):** a volatility-scaled floor that caps the loss before the trailing channel tightens.
- **Expected payoff geometry (HYPOTHESIS, tested at P6 IS — not a claim):** trend systems characteristically have **win rate < 50% but profit/loss ratio > 1** (a few large trend winners pay for many small losers) — the mirror image of the s14/s15 mean-reversion profile (win rate > 50%, P/L < 1, which failed). Whether this basket/window actually trends is the P6 IS test.

----

## 5. Corporate-action profile (carried; already DR9-verified at 245ac0d)

All 12 split-events handled under split_only and DR9-PASSED: AAPL 4:1, NVDA 4:1+10:1, AMZN 20:1, WMT 3:1 verified (ratio ~1.0 under split_only); MSFT/JPM/XOM/UNH/KO/META/CVX no splits; JNJ Kenvue spin-off (2023-08) informational (non-split distribution; one-day price drop under split_only). No new corporate-action audit required (data reused byte-equivalent; sha-verified at BUILD).

----

## 6. K9-reachability table at PLAN (the load-bearing axis — the reason for the 12-name expansion)

| Window | Length (y) | K9 floor | Donchian-20/10 per-name | 12-name basket | K9 status |
|---|---:|---|---|---|---|
| IS 2019-01-02 → 2023-12-29 | ~5.0 | ≥ 20/y (≥100 total) | ~8-15/y | ~96-180/y | **CLEARS with strong margin** |
| **OOS 2024-01-02 → 2025-12-30** | **~2.0** | **≥ 50/y (BINDING)** | ~8-15/y | ~96-180/y | **CLEARS** (≈192-360 over 2y) |

This is the explicit fix for the s15-selection-plan blocker (trend on 3 names ≈ 6-24/y << 50/y). At 12 names a medium Donchian breakout clears OOS K9 with margin. **REC1-equivalent (BINDING):** if observed effective IS rate < 25/y basket-summed → OOS K9 unreachability probable → PARK per precedent (expected 96-180/y comfortably exceeds the floor). The s16 DRAFT/SEAL must still carry its own K9 table; if the chosen `N_entry`/`N_exit` lower frequency below the floor, the candidate is K9-blocked.

----

## 7. DR10-v2-reachability table at PLAN

| Component | Estimate |
|---|---|
| Expected annual_turnover | ~5-15 (medium breakout; turnover branch fires alone; non-binding under AND) |
| Expected S2 cost_drag | ~0.3-0.8% (cash-equity per-share commission + ~1bp slippage; well under 5%) |
| **DR10 v2 status** | **CLEARS WITH STRONG MARGIN** (cost_drag branch does not fire; AND-conjunction not triggered) |

----

## 8. DR register + K-gates (carried; DR10 = v2)

DR precedence chain `DR7 → DR1 → DR9 → DR10 → DR6 → DR4 → DR2 → DR3 → DR5`; DR10 v2 by-reference (`78cd22e`); DR11 NOT IN CHAIN (unlevered cash equity). K-gates K1/K2/K4/K6/K7/K8/K9/K10/K12; K11 NOT_APPLICABLE. DR9 = already PASSED all 12 (reuse; `ec856253`). **K1 (sharpe_proxy<0) / K2 (expectancy≤0)** are the binding edge gates — this candidate's trend hypothesis is tested against them at P6 IS, never assumed. A7/K10/K6 LOAD-BEARING diversification diagnostics (12 names across ~7 sectors → expected higher A7 / lower K10 than the 3-name basket).

----

## 9. First-principles burden (fresh; clears forbidden tracks)

- **vs s15-d1 / s14-d1-cross-sector (terminal):** NON-mean-reversion mechanic FAMILY (trend breakout vs RSI/z-score mean-reversion); trailing-stop exit (vs exit-to-mean / RSI-mid); DIFFERENT (12-name) universe. Clears **T-FORBID-16** (not a `_revN_`), **T-FORBID-17** (not a daily MR tweak on AAPL/JPM/XOM), **T-FORBID-18** (not RSI(3)+2N or z-score exit-to-mean). The terminal chains are preserved byte-stable.
- **vs s12-d1 (Donchian-15/8 futures):** different asset class (cash equity vs micro-futures), different universe (12 large-caps vs single MNQ), different periods (20/10 vs 15/8), bi-directional multi-name. s12-d1 was a single-instrument futures Donchian; this is a 12-name cash-equity breakout basket — orthogonal.
- **vs s10-d2 (Donchian-55/20):** different periods + universe + asset scope.

----

## 10. Boundaries held this PLAN turn

| Boundary | Status |
|---|---|
| PLAN only (no DRAFT/SEAL/BUILD/fetch/backtest/OOS) | met |
| No mean-reversion mechanic (T-FORBID-17/18) | met |
| No `_revN_`/patch of s15/s14 (T-FORBID-16) | met |
| No revival of s15/s14/s13/s12 | met |
| No modification of any sealed artifact (incl. s16 DR9 result 245ac0d + 12 CSVs) | met |
| No data fetch (reuse DR9-passed basket) | met |
| No strategy parameter optimization / grid search | met |
| `lessons.md` not modified | met |
| No git commit by this PLAN turn | met |
| Trading `PAUSED` · Live `BLOCKED_AT_6_GATES` · FRC `NEVER_GRANTED` | met |
| Exit/stop-first-principles + K9 + DR10-v2 disciplines applied | TRUE |

----

## 11. Files written this PLAN turn

| File | Purpose |
|---|---|
| `docs/s16_d1_expanded_cross_sector_cash_equity_donchian_breakout_trend_trailing_stop_tier_n_spec_plan.md` | This Tier-N spec PLAN (PLAN only; no JSON sidecar; no seal — planning document, per predecessor convention). |

No other repository file is modified.

----

## 12. Next-step authorization scope

### Commit this PLAN (recommended first step)
```
Authorize commit s16-d1 expanded-universe trend/breakout Tier-N spec PLAN only.
```

### Proceed to DRAFT (no fresh fetch needed — 12-name basket reused)
```
Authorize s16-d1 expanded-universe trend/breakout Tier-N spec DRAFT only — bound by DR10 v2.
```
The DRAFT will formalize the §4 mechanic + DA register (first-principles justified, not tuned) and a K9-reachability table for the locked `N_entry`/`N_exit`, reusing the DR9-passed CSVs.

### Defer
```
Defer / Pause s16-d1 expanded-universe PLAN.
```

----

## 13. Carried-forward status (UNCHANGED across this PLAN turn)

| Field | Value |
|---|---|
| Trading / Live / FRC | `PAUSED` / `BLOCKED_AT_6_GATES` / `NEVER_GRANTED` |
| `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` | applies to this candidate + descendants |
| `no_strategy_optimization_authorized` / `no_dr_redefinition_post_seal` | TRUE |
| s15-d1 / s14-d1-cross-sector / s13-d1 / s12-d1 lifecycles terminal | TRUE — preserved verbatim; NOT revived/patched |
| s16 expanded-universe DR9 result (`245ac0d`; result_seal `ec856253`) + 12 sealed CSVs | reused byte-equivalent; no fresh fetch |
| `framework_dr10_revision_seal_v2` `78cd22e` | binding for s14+ |
| LESSON_S15_D1_001/002/003 committed at `fb805a1` | cited as design rationale; not modified |
| K9-reachability + DR10-v2-reachability + exit/stop-first-principles disciplines | binding |
| s16-d1 lifecycle state | `S16_D1_EXPANDED_CROSS_SECTOR_CASH_EQUITY_DONCHIAN_BREAKOUT_TREND_TIER_N_SPEC_PLAN_AUTHORED` (this PLAN turn; NOT committed) |

----

End of PLAN. PLAN-authoring turn only. No code. No backtest. No fetch. No DRAFT. No SEAL. No BUILD. No commit. No strategy optimization. **No mean-reversion re-skin. No `_revN_`/patch/revival. No modification of any sealed artifact (incl. the s16 DR9 result + 12 CSVs). No `lessons.md` modification or staging.** Trading remains `PAUSED`. Live `BLOCKED_AT_6_GATES`. FRC `NEVER_GRANTED`. Fresh candidate; non-mean-reversion trend family; 12-name basket resolves the K9-OOS blocker; trailing-stop exit is first-principles aligned with the trend thesis (tested at P6 IS, never assumed).
