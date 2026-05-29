# s17 D1 Broad-Universe (24-name) Cross-Sectional Momentum Rotation Tier-N Specification Plan

Status: **PLAN_ONLY** (no code written, no spec drafted, no spec sealed, no data fetched/inspected by this plan; the next step is a separate operator authorization to commit this PLAN, then a Tier-N spec DRAFT).

Authored: 2026-05-28
Authorization phrase: `Authorize s17-d1 broad-universe cross-sectional momentum Tier-N spec PLAN only — bound by DR10 v2 + walk-forward K13.`
Origin: Track **T2** of the post-s16 selection plan rev2 (`75a22be`) — cross-sectional relative-strength rotation, scored the **most walk-forward-K13-aligned** direction (relative momentum rotates into each regime's leaders; the structural answer to s16's absolute-trend single-OOS failure). Realized on the **24-name broad large-cap basket** whose DR9 audit PASSED all 24 (result_seal `85667ab3`, committed `d86e5d1`). This is a **FRESH s17 candidate**, NOT a `_revN_`/patch of any prior candidate.

Framework binding: **DR10 v2 AND-conjunction** (framework SEAL `78cd22e`) **+ walk-forward K13 persistence** (framework SEAL `52a3b60`, report_seal `4268d6f7…`). s17 is the **first candidate authored under the K13 discipline.**

----

## HARD BOUNDARIES (held by this PLAN)

PLAN only. No DRAFT. No SEAL. No code. No backtest. No simulator. No signal computation. No OOS inspection. No data fetch (24-name basket already fetched + DR9-PASSED at `d86e5d1`; reuse only). No vendor API / API-key access. No network IO. No `review_queue.json` / `idea_memory` mutation. No Strategy Lab run. No candidate promotion. No FRC grant. **No per-fold parameter re-fitting / fold-scheme search (T-FORBID-22; the K13 SEAL anti-snoop safeguards are INVIOLATE).** **No strategy parameter optimization / grid search** (`no_strategy_optimization_authorized`); the parameters below are first-principles proposals to **justify (not tune)** at SEAL — a different cadence/lookback/held-N is a DIFFERENT (fresh) candidate, never a tune of this one. **No mean-reversion / absolute-trend re-skin** (clears T-FORBID-17/18/19/20/21). **No `_revN_`/patch/revival of s16/s15/s14/s13/s12.** **No retroactive application of K13 to any prior candidate.** **No modification of any existing sealed artifact** (incl. the s17 DR9 result `d86e5d1` + 24 sealed CSVs, the DR10 v2 SEAL `78cd22e`, the walk-forward SEAL `52a3b60`). No CLAUDE.md / `.gitignore` modification. **No `brain_memory/projects/trading_bot/lessons.md` modification or staging.** No git commit by this PLAN turn. No live trading. No profitability claim. Trading `PAUSED` · Live `BLOCKED_AT_6_GATES` · FRC `NEVER_GRANTED`.

----

## 1. Purpose

Author a Tier-N specification PLAN for a **long-only cross-sectional momentum (relative-strength) rotation** on the 24-name DR9-passed broad large-cap basket.

This is the **family-level response** to the three terminals (LESSON_S14/S15 IS-fail; LESSON_S16_D1_004 OOS-fail-after-IS-pass). Absolute-direction mechanics (trend, mean-reversion) bet on *one* market state and failed to persist. **Cross-sectional momentum is relative**: it ranks the universe and holds the leaders, structurally rotating into whichever names lead in each regime — the design hypothesis (tested, never assumed) for clearing the new **K13 walk-forward persistence** gate that s16 would have stressed.

----

## 2. Candidate identification

| Field | Proposed value (LOCKED at PLAN unless noted) |
|---|---|
| `candidate_record_id` | **`s17-d1-broad-universe-cross-sectional-momentum-rotation-24name-large-cap-long-history`** |
| `candidate_family` | **F-xmom: cross-sectional (relative-strength) momentum rotation, long-only, periodic rebalance** (NON-trend-absolute, NON-mean-reversion; LOCKED at PLAN) |
| `is_a_mean_reversion_candidate` | **false** |
| `is_an_absolute_trend_candidate` | **false** — relative/cross-sectional ranking, not absolute breakout |
| `is_a_s16_or_s15_or_s14_revision` | **false** — different mechanic FAMILY + different (24-name) universe; clears T-FORBID-16..21 |
| `predecessor_lineage_references_read_only` | `s17_dr9_result` (`d86e5d1`; result_seal `85667ab3`), `s17_run_book` (`c5dac8a`), `selection_plan_rev2` (`75a22be`), `walk_forward_validation_seal` (`52a3b60`; report_seal `4268d6f7…`), `framework_dr10_revision_seal_v2` (`78cd22e`), `s16_d1_p11_terminal` (`99f58bd`), `phase_2_safety_contract_template_C1_C8` |
| `diagnostic_only` | true · `default_advisory_label` `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` |
| DR9 status | **ALREADY PASSED all 24** (reuse sealed CSVs; `d86e5d1` / result_seal `85667ab3`) |
| DR10-v2-reachability discipline applied at PLAN | **TRUE** (§7) |
| **K13 walk-forward discipline applied at PLAN** | **TRUE** (§5 — fold scheme; §6 — K13-per-fold + K9-per-fold reachability, the load-bearing axis) |
| K9-reachability discipline applied at PLAN | **TRUE** (§6 — and it is the candidate's PRIMARY kill-risk) |

----

## 3. Universe precommitment (LOCKED at PLAN; 24-name DR9-passed; reuse)

| Field | LOCKED at PLAN value |
|---|---|
| Universe (24) | **{AAPL, MSFT, NVDA, JPM, XOM, UNH, WMT, KO, META, AMZN, JNJ, CVX, GOOGL, V, MA, HD, PG, COST, ABBV, MRK, BAC, CAT, DIS, COP}** |
| Sectors spanned | ~8 GICS: Info Tech, Comm Services, Consumer Disc, Consumer Staples, Financials, Health Care, Energy, Industrials |
| Data source | **REUSE the 24 DR9-PASSED sealed CSVs** at `data/s17_d1_broad_universe_cross_sectional_momentum_long_history/raw/` (`d86e5d1`; manifest sha `660ece49…`; result_seal `85667ab3`) |
| Adjustment convention | `split_only` (GOOGL 20:1 FRESH verified; AMZN 20:1 / WMT 3:1 / NVDA 4:1+10:1 / AAPL 4:1 carried; **MRK Organon spin-off encoded by Tiingo as a 1.048 splitFactor → applied → return-continuous, documented PASS**; COST 2023 special dividend in the dividend stream → one-day drop, informational) |
| Vendor | tiingo (already fetched) · **Fresh fetch required? NO** |
| Universe widening/substitution post-SEAL | FORBIDDEN (fresh `candidate_record_id` required) |

Breadth rationale: 24 names give the **cross-sectional ranking breadth** a relative-momentum mechanic needs to select leaders; breadth helps *selection*, not *turnover* (§6).

----

## 4. Strategy mechanic family LOCKED at PLAN: F-xmom cross-sectional momentum rotation

| Field | Proposed LOCKED value at PLAN (first-principles; **confirm-not-tune** at SEAL) |
|---|---|
| Mechanic family | Cross-sectional relative-strength momentum rotation, long-only |
| Momentum signal | trailing total return over `L = 126` trading days (~6 months), **skipping the most recent `S = 21` days** (the classic Jegadeesh-Titman "6-1" skip-month momentum; first-principles, widely documented — NOT tuned) |
| Ranking | each rebalance, rank all 24 names by the 126-21 signal; **hold the top `M = 6`** (top quartile) |
| Rebalance cadence | **every `R = 21` trading days (monthly)** — the canonical academic cross-sectional-momentum cadence |
| Direction | **long-only** (no shorting, no leverage; DR11 NOT IN CHAIN) |
| Sizing (DA3) | **equal-weight `1/M` of equity per held name** (rebalanced to equal weight each `R`) |
| DA4 START_CASH (proposed) | `B = $100,000` |
| Pyramiding / inter-name coordination | NONE (rank-and-hold; no add-to-winner) |
| Entry/exit | a name is HELD while in the top-M at a rebalance; **a name fully EXITED when it leaves the top-M = one closed trade** (the K9-counted round-trip) |
| Warmup | ≥ `L + S + margin` = 126 + 21 + ~13 ≈ **160 bars** (~7.5 months) before the first tradable rebalance |

### 4.1 First-principles edge design (the binding axis, relative variant)

s14/s15 (mean-reversion) and s16 (absolute trend) each bet on a single market geometry and failed to persist. Cross-sectional momentum is **relative**: it does not predict the market's direction — it predicts that **recent relative winners continue to relatively outperform** (the Jegadeesh-Titman / Asness cross-sectional momentum premium). Its first-principles structure:

- **Signal = 126-21 trailing return** (skip the most recent month to avoid the well-documented short-term reversal that contaminates raw 6-month momentum). First-principles, not tuned.
- **Hold top-quartile, equal-weight**: express the premium with diversified concentration (M=6 across ~8 sectors → strong A7/K10 diversification expectation).
- **Why this is the K13 hypothesis (tested at P6.7, NOT a claim):** because it rotates into each regime's leaders, the same LOCKED rule plausibly stays positive across multiple sequential folds (e.g., it would have rotated into 2024-2025 defensive/quality leaders rather than holding s16's stale absolute-trend longs). **Whether the premium is actually present in this basket/window across folds is the P6 IS + P6.7 K13 test — never assumed.**

----

## 5. K13 walk-forward fold scheme (proposed at PLAN; LOCKED byte-equivalent at SEAL; declared-before-evaluation, UNSEARCHED)

Per the walk-forward SEAL (`52a3b60`): **N = 5 fixed pre-committed sequential OOS folds; window_mode declared at candidate PLAN; no fold-anchoring to known-favorable periods; uniform per asset/frequency class.**

| Field | Proposed LOCKED value |
|---|---|
| `n_folds` | **5** (per SEAL; not searched) |
| `window_mode` | **rolling** — each fold carries its own ~160-bar warmup, then a contiguous OOS test segment (no parameter fit occurs in any window — params are LOCKED — so there is no "train" split; "warmup" = indicator lookback only) |
| Partition | reserve the first ~160 bars (≈2019-01-02 → ~2019-08) as initial warmup, then **uniformly tile the remaining ~1599 bars into 5 contiguous, equal-length OOS test folds of ~320 bars (~1.27y) each** (uniform partition — NOT anchored to known-good periods) |
| Approx fold test windows (exact bar-index boundaries LOCKED at SEAL DA register) | F1 ~2019-08→2020-11 · F2 ~2020-11→2022-02 · F3 ~2022-02→2023-05 · F4 ~2023-05→2024-08 · F5 ~2024-08→2025-12-30 |
| P10 final hold-out | **RETAINED separately** (2024-01-02 → 2025-12-30, LOCKED/not-inspected) — K13 (P6.7) must clear *before* P10; P10 remains the final untouched OOS gate |
| Anti-snoop | fold count + boundaries + the K13 ≥3/5 threshold are declared HERE (pre-evaluation) and NEVER searched; locked params re-evaluated per fold; **NO per-fold refit** (T-FORBID-22; SEAL §core_distinction INVIOLATE) |

----

## 6. K13-per-fold + K9-per-fold reachability tables (THE LOAD-BEARING AXIS — the candidate's primary kill-risk)

### 6.1 K13 pass structure (LOCKED by SEAL `52a3b60`; results computed at P6.7, never assumed here)

K13 PASS ⇔ the LOCKED rule is positive (`expectancy>0 AND sharpe_proxy_per_trade>0 AND no K1/K2 fire`) in **≥ ceil(0.6·5) = 3 of 5** OOS folds **AND** aggregate-across-folds net > 0 **AND** K9 reachability holds (per-fold OR aggregate). Else **OOS_NOT_ROBUST → REJECT_FAST** (terminal).

| Fold | Approx window | Length | Per-fold edge (computed at P6.7 — placeholder) | Per-fold K1/K2 (computed) |
|---|---|---:|---|---|
| F1 | ~2019-08→2020-11 | ~1.27y | TBD at P6.7 | TBD |
| F2 | ~2020-11→2022-02 | ~1.27y | TBD at P6.7 | TBD |
| F3 | ~2022-02→2023-05 | ~1.27y | TBD at P6.7 | TBD |
| F4 | ~2023-05→2024-08 | ~1.27y | TBD at P6.7 | TBD |
| F5 | ~2024-08→2025-12-30 | ~1.27y | TBD at P6.7 | TBD |
| **Gate** | | | **≥3/5 positive AND aggregate net>0** | **no K1/K2 in the counted folds** |

### 6.2 K9-per-fold trade-count reachability (the binding concern flagged by the RUN_BOOK + selection plan)

Cross-sectional momentum rotation is **structurally low-turnover**: trades ≈ rebalances/year × names-replaced/rebalance. For monthly (R=21, ~12/y) top-6-of-24 with 126-21 momentum, empirical monthly turnover replaces ~1–3 names/rebalance → **closed trades ≈ ~12–36 /year**.

| Window | Length | K9 floor | Est. closed trades (monthly, M=6) | K9 status |
|---|---:|---|---|---|
| Per K13 fold | ~1.27y | (per-fold leg of OOS ≥50/y) | ~15–46 | **TIGHT → AT RISK of falling below the per-fold floor** |
| OOS 2024-01-02→2025-12-30 (P10) | ~2.0y | **≥ 50/y (BINDING at P10)** | ~24–72 over 2y (≈12–36/y) | **AT RISK — monthly may NOT clear ≥50/y** |
| Aggregate over full 2019-2025 history | ~7y | ≥ 100 total | ~84–252 | **CLEARS aggregate ≥100** |

**Honest read (load-bearing, surfaced per discipline):** the K13 K9-component permits **per-fold OR aggregate** reachability, and the aggregate (~84–252) **clears ≥100** — so K13's K9 sub-condition is plausibly satisfiable on aggregate. **BUT** the standalone **P10 OOS K9 ≥50/y** is a SEPARATE binding gate, and a monthly top-6 rotation is genuinely **at risk of producing <50 trades/year** in the OOS window. There is a real **edge-vs-sample tension**: cross-sectional momentum's premium is strongest at monthly-to-quarterly cadence (weekly is noise-dominated), yet a slower cadence yields fewer trades. 

**Disciplined resolution (NOT a tuning hatch):** this PLAN proposes the **principled monthly cadence** and commits that **if the DRAFT/P6/P10 measured OOS trade count is < the K9 floor, the candidate is K9-BLOCKED (terminal) — it will NOT be rescued by raising the cadence.** A higher-cadence (e.g., fortnightly/weekly) or wider-held-N variant would be a **separate fresh `candidate_record_id`**, never a tune of this one (preserves `no_strategy_optimization_authorized` + T-FORBID-22). The DRAFT must carry the exact K9 table for the LOCKED cadence; the SEAL must not adjust cadence to chase the floor.

----

## 7. DR10-v2-reachability table at PLAN

| Component | Estimate |
|---|---|
| Expected annual_turnover | ~1–3 (monthly top-6 rotation; turnover branch may fire alone; **non-binding under the v2 AND**) |
| Expected S2 cost_drag | ~0.2–0.6% (cash-equity per-share commission + ~1bp slippage on monthly rebalances; well under 5%) |
| **DR10 v2 status** | **CLEARS WITH STRONG MARGIN** (cost_drag branch does not fire; the AND-conjunction `turnover>0.50 AND cost_drag>0.05` is not triggered) |

----

## 8. DR register + K-gates (carried; DR10 = v2; K13 ADDED)

DR precedence chain `DR7 → DR1 → DR9 → DR10 → DR6 → DR4 → DR2 → DR3 → DR5`; DR10 v2 by-reference (`78cd22e`); DR11 NOT IN CHAIN (unlevered cash equity). K-gates K1/K2/K4/K6/K7/K8/K9/K10/K12; K11 NOT_APPLICABLE (no leverage cap); **K13 walk-forward persistence ADDED at the new P6.7 phase** (by-reference to `52a3b60`). DR9 = already PASSED all 24 (reuse; `85667ab3`). **K1 (sharpe_proxy/trade<0) / K2 (expectancy≤0)** are the binding edge gates per fold and in aggregate — the momentum-premium hypothesis is tested against them, never assumed. A7/K10/K6 LOAD-BEARING diversification diagnostics (24 names across ~8 sectors → strong expected diversification). **DR4 (oos-negative-while-is-positive) carries** — but K13 (P6.7) now precedes P10, so a non-persistent edge is expected to be caught earlier by K13 than by the single DR4 check.

----

## 9. First-principles burden (fresh; clears forbidden tracks)

- **vs s16-d1 (absolute Donchian trend, terminal OOS-fail):** RELATIVE cross-sectional ranking, not absolute breakout; no channel/trailing-stop; long-only rotation. Clears **T-FORBID-19/20/21** (not an s16 `_revN_`/OOS-tweak/DR4-relaxation/post-hoc-regime-rescue) and **T-FORBID-22** (locked params, pre-committed unsearched folds, no per-fold refit).
- **vs s15-d1 / s14-d1 (mean-reversion, terminal):** opposite thesis (momentum continuation vs reversion); clears **T-FORBID-16/17/18**.
- **vs s12/s13 (single-instrument futures Donchian / RSI):** different asset class, universe, mechanic family — orthogonal.

----

## 10. Boundaries held this PLAN turn

| Boundary | Status |
|---|---|
| PLAN only (no DRAFT/SEAL/BUILD/fetch/backtest/OOS) | met |
| No per-fold refit / no fold-scheme search (T-FORBID-22; K13 anti-snoop INVIOLATE) | met |
| No strategy parameter optimization / grid search | met |
| No mean-reversion / absolute-trend re-skin (T-FORBID-16..21) | met |
| No `_revN_`/patch/revival of s16/s15/s14/s13/s12 | met |
| No retroactive K13 application to any prior candidate | met |
| No modification of any sealed artifact (incl. s17 DR9 result `d86e5d1` + 24 CSVs, `78cd22e`, `52a3b60`) | met |
| No data fetch (reuse DR9-passed basket) | met |
| `lessons.md` not modified | met |
| No git commit by this PLAN turn | met |
| Trading `PAUSED` · Live `BLOCKED_AT_6_GATES` · FRC `NEVER_GRANTED` | met |
| K13-per-fold + K9-per-fold + DR10-v2 reachability tables provided | TRUE (§5/§6/§7) |

----

## 11. Files written this PLAN turn

| File | Purpose |
|---|---|
| `docs/s17_d1_broad_universe_cross_sectional_momentum_rotation_tier_n_spec_plan.md` | This Tier-N spec PLAN (PLAN only; no JSON sidecar; no seal — planning document, per predecessor convention). |

No other repository file is modified.

----

## 12. Next-step authorization scope

### Commit this PLAN (recommended first step)
```
Authorize commit s17-d1 broad-universe cross-sectional momentum Tier-N spec PLAN only.
```

### Proceed to DRAFT (no fresh fetch — 24-name basket reused)
```
Authorize s17-d1 broad-universe cross-sectional momentum Tier-N spec DRAFT only — bound by DR10 v2 + walk-forward K13.
```
The DRAFT will formalize the §4 mechanic + DA register (first-principles justified, not tuned), the §5 fold scheme (exact boundaries), and the §6 K13/K9 reachability for the LOCKED cadence — reusing the DR9-passed CSVs.

### Defer
```
Defer / Pause s17-d1 broad-universe PLAN.
```

----

## 13. Carried-forward status (UNCHANGED across this PLAN turn)

| Field | Value |
|---|---|
| Trading / Live / FRC | `PAUSED` / `BLOCKED_AT_6_GATES` / `NEVER_GRANTED` |
| `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` | applies to this candidate + descendants |
| `no_strategy_optimization_authorized` / `no_dr_redefinition_post_seal` | TRUE (and: K13 = VALIDATION, NOT optimization — INVIOLATE) |
| s16/s15/s14/s13/s12 lifecycles terminal | TRUE — preserved verbatim; NOT revived/patched; NOT re-evaluated under K13 |
| s17 DR9 result (`d86e5d1`; result_seal `85667ab3`) + 24 sealed CSVs | reused byte-equivalent; no fresh fetch |
| `framework_dr10_revision_seal_v2` `78cd22e` | binding for s14+ |
| `walk_forward_validation_seal` `52a3b60` (K13; 5-fold; P6.7) | binding for s17+; **s17 is the first candidate under it** |
| LESSON_S16_D1_004/005/006 committed at `90afbb8` | cited as design rationale; not modified |
| K13-per-fold + K9-per-fold + DR10-v2 + first-principles disciplines | binding |
| s17-d1 lifecycle state | `S17_D1_BROAD_UNIVERSE_CROSS_SECTIONAL_MOMENTUM_TIER_N_SPEC_PLAN_AUTHORED` (this PLAN turn; NOT committed) |

----

End of PLAN. PLAN-authoring turn only. No code. No backtest. No fetch. No DRAFT. No SEAL. No BUILD. No OOS inspection. No commit. No strategy optimization. **No per-fold refit / no fold-scheme search. No mean-reversion / absolute-trend re-skin. No `_revN_`/patch/revival. No retroactive K13. No modification of any sealed artifact (incl. the s17 DR9 result + 24 CSVs, DR10 v2 `78cd22e`, walk-forward `52a3b60`). No `lessons.md` modification or staging.** Trading remains `PAUSED`. Live `BLOCKED_AT_6_GATES`. FRC `NEVER_GRANTED`. Fresh candidate; cross-sectional relative-momentum family; 24-name basket gives ranking breadth; **K9-per-fold (and standalone P10 K9 ≥50/y) is the candidate's primary kill-risk and will be treated as a terminal block, not a tuning trigger, if the LOCKED monthly cadence falls short.** The momentum premium is the K13 hypothesis — tested at P6 IS + P6.7 walk-forward, never assumed.
