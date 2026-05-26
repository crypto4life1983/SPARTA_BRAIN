# Next Research-Track Selection Plan -- after s7 D1 ETF-proxy park

Status: PLAN_ONLY (no track is built or run by this plan; the next track requires its own separately authorized plan-authoring turn).
Authored: 2026-05-25
Predecessor park: s7 D1 cross-asset Donchian ETF-proxy, parked at REJECT_FAST.
Predecessor park report: reports/s7_d1_cross_asset_donchian_yfinance_proxy_park_report.json (sha256 5eb4309096a8377943799b7cc164cbbb13a86f327a813520255d0fa3b3e00263, seal e7f3fce5239d18f7cff78ddda81dde060b6842c54ddb1fdba95bfdcd584eb326, commit a5ac092)
Predecessor lesson append: brain_memory/projects/trading_bot/lessons.md (sha256 6d27e8e5b451b24aa2de025a48b53a862de1493ccec4fd0d6b94821c5a8d4778, commit c6730d2)

HARD BOUNDARIES (held by this plan). Plan only. No strategy code. No backtest. No simulator. No new signal computation. No OOS inspection. No data fetch. No yfinance import. No Yahoo Finance call. No Databento call. No DATABENTO_API_KEY access. No network IO. No review_queue.json mutation. No production idea_memory mutation. No Strategy Lab run. No candidate promotion. No s7 D1 resurrection. No s7 D1 code, report, CSV, manifest, or park report modification. No ORB branch artifact mutation. No Step 30 cost constant mutation. No CLAUDE.md modification. No docs/decisions.md modification. No RUNBOOK modification. No pipeline_manifest modification. No .gitignore modification. No branch change. No branch creation. No commit beyond the single new plan file. No git push. No live trading. No profitability claim. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES. FRC never granted.

----

## 1. Purpose

Author a sealed selection plan for the next trading research track to follow the s7 D1 cross-asset Donchian yfinance-proxy chain (now terminally parked at REJECT_FAST per commit a5ac092). The selection plan does NOT build any track; it surveys what is repo-available, applies the operator's selection criteria, ranks candidate directions, and produces a single recommended next track plus a recommended first step. The chosen track itself requires a fresh separately authorized plan-authoring turn before any code is written.

This selection plan inherits the validated cross-asset diversification finding (effective_independent_bets = 3.56, avg_pairwise_dependence = 0.041 on SPY/TLT/GLD/USO 2014-2022) and the explicit prohibition on resurrecting the locked no-filter Donchian-55 + 0.5N pyramid + 4-unit-max + 2N-stop mechanic on this universe under any threshold relaxation.

## 2. Current terminal state of s7 D1 ETF-proxy

The s7 D1 cross-asset Donchian yfinance-proxy chain is FORMALLY PARKED:

- candidate_record_id: `s7-cross-asset-donchian-no-filter-spy-tlt-gld-uso-yfinance-proxy`
- final_state: `PARKED_REJECT_FAST`
- park_report_commit: `a5ac092`
- lesson_append_commit: `c6730d2`
- full chain: 15 commits on master, `efdc307 ... c6730d2`
- terminal verdict: REJECT_FAST via K12 (DR2 fired + DR3 fired on the cost-stress matrix)
- supporting metrics: S1 net PnL +$589.59 / `trade_curve_max_drawdown_pct = 69.10%` / 37 closed trades / only USO net positive
- diversification finding: effective_independent_bets = 3.56, avg_pairwise_dependence = 0.041
- OOS: never inspected; remains structurally blocked
- Strategy Lab: untouched and blocked
- review_queue.json: untouched
- idea_memory: untouched
- broker: not connected
- live trading: BLOCKED at six gates
- "do not rescue this spec" recorded permanently in park report and lesson file

## 3. Lessons inherited from s7 D1

The next track MAY inherit (and SHOULD where applicable):

- **Cross-asset diversification works on this universe** when measured across SPY (equity-index), TLT (bonds), GLD (metals), USO (energy). avg_pairwise_dependence = 0.041 over the in-sample window; effective_independent_bets = 3.56. The four-symbol bundle behaves as four genuinely independent return series, validating the load-bearing hypothesis from spec section 1 H1.
- **The four-symbol ETF dataset itself is clean and auditable**. Step 02c raw-data audit verdict PASS; csv sha256 pins documented; 3116 rows per symbol; cross-symbol date sets aligned. Reusing this dataset for a different mechanic is zero-friction.
- **The protocol scaffolding (Step 03 loader / Step 04 validator / Step 05 signal scope / Step 06 simulator / Step 07 aggregator) is reusable as a template**. The pattern of plan -> build -> seal -> verdict with V-gates, T-tests, IS-only enforcement, and cost-stress matrix is reusable.
- **The cost-stress matrix S0/S1/S2/S3 + DR2/DR3/DR5 fail-fast caught a false-edge before any OOS authorization could be considered**. This is the protocol working as designed.

## 4. Lessons NOT inherited from s7 D1

The next track must NOT inherit (and SHALL refuse to inherit):

- **The locked no-filter Donchian-55 entry / Donchian-20 exit / pyramid +0.5N / 4-unit-max / 2N-stop mechanic** on the SPY/TLT/GLD/USO universe. This combination empirically failed cost-stress per K12 / DR2 / DR3 on the in-sample window 2014-2022.
- **Any rebadging of s7 D1 with relaxed K-thresholds**. The spec section 14 threshold-lock invariant forbids loosening; tightening requires a fresh `_revN_` spec. The next track must NOT silently relax `A4_TRADE_CURVE_MAXDD_PCT_MAX = 50.0`, `A1_MIN_CLOSED_TRADES = 100`, `K10_AVG_PAIRWISE_DEPENDENCE_MAX = 0.50`, `K11_CAP_BINDING_EVENTS_MAX = 1000`, or `DR2_S2_S3_DEGRADATION_THRESHOLD_FRACTION = 0.5`.
- **Any silent re-introduction of filters that the locked `Filter: NONE` spec removed**. Adding a same-direction trend filter, an MA filter, a regime filter, or a correlation gate to the s7 D1 mechanic would be a rebadging.
- **The 4-unit pyramid amplification mechanism**. The Databento-track sibling (s7 D1 NQ/GC/ZN/CL) also K4-fired at -221% MaxDD on the SAME pyramid; that's two independent universes pointing to the same mechanism. Future tracks may choose to inherit pyramid but must explicitly justify; the default position is no-pyramid until evidence shows otherwise.
- **Single-asset-carries-portfolio outcomes**. In s7 D1 ETF-proxy, only USO was net positive; SPY/TLT/GLD were net losers. A "diversified" portfolio whose PnL depends on one market is not actually diversified. The next track shall be evaluated against per-symbol contribution distribution, not just portfolio aggregates.

## 5. Candidate-track selection criteria (positive)

A candidate track is acceptable iff it satisfies ALL of:

C1. **Uses existing clean data or low-friction data**. The four sealed ETF CSVs at data/s7_d1_cross_asset_donchian/raw/ are the preferred dataset. Any additional data requires its own data-fetch authorization at zero or near-zero cost.

C2. **Has enough trade count to clear K9**. Expected `total_closed_trades >= 100` over the in-sample window. Tracks with sparse trade generation (<100 expected) require a justification.

C3. **Does not rely on one asset carrying all profit**. The track shall produce expected per-symbol contributions that are not maximally concentrated. A track that anticipates one-asset-dominance shall justify why and shall design diagnostics that detect that pattern explicitly.

C4. **Has explicit cost-stress testing from the beginning**. The S0/S1/S2/S3 cost-stress matrix from spec section 10 is locked. The candidate's diagnostic shall include all four tiers in the first IS run, not as an afterthought.

C5. **Inherits cross-asset diversification structure without inheriting the failed no-filter Donchian/Faith mechanic**. The candidate shall operate on a multi-symbol universe (preferably the same four ETFs to reuse the audit) and shall use a DIFFERENT signal/sizing mechanic from the parked s7 D1.

C6. **First-principles rationale**. The candidate shall have a stated reason WHY it might survive where s7 D1 did not. Not "it's worth trying" but "the mechanism that broke s7 D1 (cost-stress sensitivity of low-frequency trend-following on this universe) is structurally absent or addressed in this candidate."

C7. **One-cycle scope**. The candidate shall be doable in a single plan -> build -> seal -> verdict cycle within reasonable bounds. No multi-year build.

C8. **Inheritable safety template**. The candidate shall be able to inherit the Phase 2 safety template (C1-C8 attestations) byte-equivalent or with minor track-specific extensions.

## 6. Reject-fast criteria for next track (negative)

A candidate track is REJECTED FAST in this selection plan iff ANY of:

R1. Track rebadges s7 D1 or any other parked candidate.
R2. Track requires loosening any K-threshold or A-gate threshold.
R3. Track requires expensive data before a cheap diagnostic could be run.
R4. Track requires live trading or brokerage connection to evaluate.
R5. Track requires Strategy Lab promotion to evaluate.
R6. Track has structural sample-size bottleneck (expected closed trades < 100).
R7. Track silently re-introduces a filter that the s7 D1 spec locked to NONE.
R8. Track operates on a universe known to be empirically falsified (e.g., NKE single-symbol options, MNQ-only daily range breakout) without a fundamentally new mechanic.
R9. Track depends on a survivorship-cherry-pick selection rule (e.g., "pick the best of N markets after the run").

## 7. Data availability criteria

Preferred data sources (in priority order):

D1. **Sealed s7 D1 ETF-proxy CSVs**: SPY/TLT/GLD/USO daily bars, 2014-01-02 through 2026-05-22, sha-pinned in audit_manifest.json. Zero new fetch. Zero new vendor call. Re-use across mechanics is free.

D2. **A separately authorized expanded ETF universe via yfinance operator-side fetch**: e.g., add IWM/EFA/AGG/DBC to broaden the cross-asset bundle. Requires a Step 02b-equivalent operator-side fetch turn under its own authorization. Still zero paid data.

D3. **Databento `GLBX.MDP3` futures cache**: the parallel Databento-track s7 D1 used `data/databento_cache/` (NQ/GC/ZN/CL). Per parent spec sec 11, this is the primary vendor for the futures track. The ETF-proxy follow-up should NOT switch to Databento mid-stream; that's a different research track.

DR_REJECTED_FOR_THIS_TRACK. Any candidate requiring fresh paid data downloads is rejected for first-cycle evaluation; if the track survives a cheap-data diagnostic, an expensive-data follow-up may be authorized separately.

## 8. Cost-stress requirements

Every candidate track shall:

CS1. Define its cost model in the candidate's Tier-N spec at locking time, including the ETF-proxy adaptation (`ETF_DOLLAR_PER_SHARE = 1.0`; `ETF_TICK_SIZE = 0.01`; baseline commission and slippage).
CS2. Run the full S0/S1/S2/S3 cost-stress matrix in the first IS diagnostic (not deferred to a follow-up cycle).
CS3. Evaluate DR2 (S2/S3 material degradation), DR3 (zero-cost-only survival), DR5 (S0->S1 edge negative). DR4 deferred to OOS phase.
CS4. Pre-register the cost-stress tolerance: a track that survives ONLY at S0 is canonically false-edge.
CS5. If the candidate uses borrow cost (e.g., short ETFs), add a borrow-cost component to the cost model at S1 baseline, do not defer to a later phase.

## 9. Diversification requirements

Every candidate track shall:

DV1. Operate on at least 4 distinct asset families (equity-index, bonds, metals, energy, or substitutes) UNLESS the candidate is explicitly a single-symbol diagnostic justified by first-principles.
DV2. Measure per-symbol contribution to portfolio PnL. A track whose IS run shows one symbol contributing > 80% of net PnL is structurally suspect and warrants additional scrutiny (similar to s7 D1's USO-only pattern).
DV3. Compute and report `avg_pairwise_dependence_measure` and `effective_independent_bets` per the aggregator pattern; A7 (`effective_independent_bets >= 2.5`) and K10 (`avg_pairwise_dependence_measure <= 0.50`) thresholds inherited byte-equivalent.

## 10. Sample-size requirements

SS1. Expected `total_closed_trades >= 100` across the in-sample window (per K9 threshold).
SS2. If trade frequency is lower than s7 D1's (~4/year/symbol), the track shall justify the trade-density tradeoff in the plan.
SS3. Per-symbol minimum: at least 10 closed trades per symbol over the IS window (per-market WR computation is unreliable below this).
SS4. The K9 sample-size bottleneck is the most common parking cause in the s2-s8 chain (parked s4 with 20 trades; parked s5 with 64). Tracks that anticipate < 100 trades shall justify or pre-register a wider sample collection.

## 11. OOS-locking policy (inherited unchanged)

The spec section 11 `oos_inspection_blocked_at_in_sample` invariant remains in force for every future track:

OL1. OOS data (`2023-01-01` through `2025-12-30`) shall not be inspected, computed against, simulated over, or queried in any form during the in-sample diagnostic phase.
OL2. Post-OOS data (`2026-01-02` through `2026-05-22` for the ETF proxy track) is informational only; no diagnostic uses it.
OL3. OOS inspection requires a separately authorized turn that follows an IS-window run verdict of ELIGIBLE_FOR_OOS plus an explicit operator approval.
OL4. The next track's loader, validator, signal, simulator, and aggregator modules shall inherit the IS-only structural enforcement pattern from the s7 D1 modules.

## 12. No-live / no-Strategy-Lab / no-brokerage policy (inherited unchanged)

Every future track shall enforce:

NL1. No live trading authorization conferred by any IS verdict.
NL2. No Strategy Lab promotion conferred by any IS verdict.
NL3. No brokerage connection conferred by any IS verdict.
NL4. No review_queue.json mutation.
NL5. No production idea_memory mutation outside explicitly authorized memory/lesson append targets.
NL6. No paper-trade loop, no scheduler integration, no autopilot, no FRC gate touch.
NL7. The six live-trading gates remain BLOCKED regardless of verdict, regardless of how many sealed seals stack.

## 13. Candidate ranking rubric

Each candidate is scored 0-5 against 10 criteria (50 max):

- **R1_addresses_s7_d1_root_cause:** 5 = directly addresses cost-stress sensitivity OR low trade density (the two s7-D1-ETF-proxy failure modes); 0 = doesn't address.
- **R2_uses_existing_clean_data:** 5 = reuses sealed ETF CSVs as-is; 3 = expands the universe with cheap fetch; 1 = requires expensive new data.
- **R3_clears_K9_sample_size:** 5 = expected >> 100 trades; 3 = expected ~100-200; 1 = expected < 100.
- **R4_per_symbol_contribution_balance_expected:** 5 = expected balanced contribution; 3 = expected some concentration; 0 = expected one-asset dominance.
- **R5_built_in_cost_stress:** 5 = cost-stress matrix natural to the design; 3 = cost-stress adds late; 0 = no cost model.
- **R6_first_principles_rationale:** 5 = strong, falsifiable, ties to s7 D1 evidence; 1 = ad hoc.
- **R7_different_family_from_donchian_faith:** 5 = mean-reversion / vol-targeting / rotation; 3 = trend-following but different lookback; 0 = pure rebadge.
- **R8_one_cycle_scope:** 5 = clearly doable; 1 = scope-creep risk.
- **R9_safety_template_inheritable:** 5 = inherits byte-equivalent; 1 = needs adaptation.
- **R10_explicit_oos_blocked:** 5 = OOS structurally blocked by design; 1 = needs extra plumbing.

Total >= 40 is acceptable; >= 45 is recommended.

## 14. Possible next tracks discovered from the repo

Read-only repo survey (no files modified during this enumeration) reveals the following possible directions:

T1. **Cross-asset mean-reversion on the existing SPY/TLT/GLD/USO universe**. Examples: 2-period RSI oversold-bounce; Bollinger band reversal; n-day pullback within a longer-term uptrend filter (caveat: "filter" inheritance concern per R7).

T2. **Cross-asset cross-sectional momentum rotation**. Each month rank the four ETFs by trailing 3-6 month total return; hold top 2; rebalance monthly. Different from time-series trend-following; lower trade frequency but possibly higher per-trade quality.

T3. **Volatility-targeted long-only basket on the four ETFs**. Mirrors the existing `b006_001_spy_vol_targeting_diagnostic_runner` lineage but expanded to the four-symbol universe. Different family (risk-management, not signal-mechanic).

T4. **Risk-parity rebalanced four-asset portfolio**. Target equal risk contribution from each of SPY/TLT/GLD/USO; rebalance quarterly or monthly. Trade count depends on rebalance frequency.

T5. **Defer to s8 Databento no-pyramid result (await convergence)**. The concurrent s8 D1 (no-pyramid Donchian on NQ/GC/ZN/CL futures via Databento) is in flight at the time of this plan. Wait for that verdict before authorizing the next ETF-proxy track; carry the cross-track lesson into the ETF-proxy next-track decision.

T6. **Pivot off all trend-following on this universe**. Declare trend-following family empirically exhausted at the SPY/TLT/GLD/USO universe for now; spec a different family entirely (statistical arbitrage, carry, term-structure, vol-of-vol).

T7. **Hunter-brain harness expansion**. Several diagnostic harness directories exist in `external_research_hunter/` (`b005_001_intraday_etf_momentum`, `b005_004_stocks_on_the_move`, `b005_005_lower_turnover_clenow`, `b005_006_dr9_refined_lower_turnover_clenow`, `b006_001_spy_vol_targeting`, `packet3_coverage_scan_harness`). Per session-summary context, b005_001 and b005_004 are parked / rejected. b005_005 / b005_006 / b006_001 / packet3 may be unfinished and worth a status survey before authorizing a brand-new track.

## 15. Recommended next track

**Recommendation:** T1 -- **cross-asset mean-reversion on the existing SPY/TLT/GLD/USO universe**.

Proposed candidate_record_id: `s9-cross-asset-mean-reversion-rsi2-spy-tlt-gld-uso-yfinance-proxy` (sequential to s7-D1; deliberately NOT s8 because s8 is in flight on the Databento futures track for no-pyramid Donchian; this is a separate research thread that operates on the ETF-proxy universe).

Scoring against section 13 rubric:

| Criterion | Score |
|---|---:|
| R1_addresses_s7_d1_root_cause | 5 (addresses BOTH cost-stress sensitivity via higher trade count + frequency, AND low trade density directly) |
| R2_uses_existing_clean_data | 5 (reuses sealed SPY/TLT/GLD/USO CSVs as-is) |
| R3_clears_K9_sample_size | 5 (RSI-2 oversold-bounce on 4 symbols typically fires 50-150 times per year per symbol; expected several thousand trades over 9-year IS) |
| R4_per_symbol_contribution_balance_expected | 4 (mean-reversion typically more balanced than trend-following; tail risk of one-symbol concentration remains) |
| R5_built_in_cost_stress | 5 (Step 06 simulator's CostTier S0/S1/S2/S3 framework directly reusable) |
| R6_first_principles_rationale | 5 (mean-reversion captures different effect than trend; if s7 D1 trend-edge failed cost-stress, mean-reversion edge tests an orthogonal hypothesis) |
| R7_different_family_from_donchian_faith | 5 (mean-reversion is a structurally different family from trend-following Donchian) |
| R8_one_cycle_scope | 5 (single-mechanic, single-universe, sealed-template reuse) |
| R9_safety_template_inheritable | 5 (Phase 2 safety template C1-C8 inheritable byte-equivalent) |
| R10_explicit_oos_blocked | 5 (Step 03 loader / Step 04 validator / Step 05 signal scope already enforce IS-only structurally) |
| **Total** | **49 / 50** |

## 16. Why that track is next (rationale)

**The two structural failure modes of s7 D1 ETF-proxy were (a) cost-stress sensitivity and (b) low trade density on a low-frequency 55-day Donchian mechanic.** A mean-reversion family addresses BOTH simultaneously:

- **Trade density**: RSI-2 / Bollinger reversal mechanics typically fire weekly per symbol, not annually. On four symbols over 9 IS years, expected trade count is in the low thousands -- orders of magnitude above the K9 threshold of 100.
- **Cost-stress sensitivity**: Mean-reversion edges are typically smaller per-trade than trend-following but more frequent; the aggregate edge has a DIFFERENT cost-stress sensitivity profile. Whether it survives is a genuine open question, NOT a foregone conclusion.
- **Validated diversification carries forward**: avg_pairwise_dependence = 0.041 on this universe is family-agnostic; the diversification finding applies equally to mean-reversion signals on the same four symbols.
- **No mechanic rebadge**: mean-reversion is a structurally different signal family. There is no risk of accidentally relaxing s7 D1's K-thresholds because the mechanic itself is different.
- **Same protocol scaffolding**: Step 03 loader / Step 04 validator / Step 06 simulator core (without the Donchian-channel computation) is reusable. The signal module is what changes; everything around it is the same.
- **Cheap diagnostic**: zero new data fetch; reuses sealed CSVs; runs on existing infrastructure.
- **Honest falsifiability**: if mean-reversion also fails cost-stress on this universe, that is a strong family-level finding (two structurally orthogonal mechanics both empirically falsified -> the universe itself is suspect). If it survives, the diversification finding plus a working mean-reversion edge is a research-grade outcome.

**Why NOT T2 (cross-sectional momentum rotation):** trade count is low (~12 rebalances/year * 4 symbols = 48 / year, but most rebalances are zero-trade if rank order unchanged -> expected <100 actual trades over 9 years; K9 borderline). Also still in the momentum family; less of a structural break from trend-following.

**Why NOT T3 (vol-targeted long-only basket):** essentially buy-and-hold with sizing; minimal trade decisions; trade count is very low. Tests sizing, not signal. Useful as a control benchmark but not as a next research track.

**Why NOT T4 (risk-parity rebalance):** similar to T3 in trade-count concern. Useful as a benchmark.

**Why NOT T5 (defer to s8 Databento):** that's a different universe (futures) and a different team (concurrent session). The ETF-proxy thread is independent; waiting adds calendar time without resolving the ETF-proxy question.

**Why NOT T6 (pivot off trend-following entirely on this universe):** premature without testing at least one orthogonal-family mechanic on this universe. T1 IS the orthogonal-family test.

**Why NOT T7 (hunter-brain survey first):** worth doing as a parallel triage but not blocking the next research track. The existing diagnostic harnesses are mostly parked or rejected per session context.

## 17. First step of the recommended next track

The first step of the recommended next track is to author its **Tier-N specification plan** under a separately authorized turn (mirroring how s7 D1 ETF-proxy began with Step 02b plan-authoring on a fresh commit). The first-step plan shall include:

FS1. A fresh `candidate_record_id` distinct from any parked predecessor. Proposed: `s9-cross-asset-mean-reversion-rsi2-spy-tlt-gld-uso-yfinance-proxy`.

FS2. A locked signal mechanic definition. Default proposal (subject to operator revision in the first-step plan turn): RSI(2) oversold-bounce on close: enter long when RSI(2) < 10; exit when RSI(2) > 50. NO trend filter (to keep the test of mean-reversion clean). NO regime gate. NO asset selection. Bidirectional optional (short entry when RSI(2) > 90) -- operator decides at spec time.

FS3. A locked sizing mechanic. Default proposal: equal-dollar per signal at 1% portfolio-equity risk per signal using ATR(20) for stop distance. NO pyramid (single unit per symbol per signal). Inherits the no-pyramid lesson from s7 D1's sibling Databento s8 track (when that converges).

FS4. A locked cost model with full S0/S1/S2/S3 cost-stress matrix, inheriting the ETF-proxy adaptation from s7 D1 (`ETF_DOLLAR_PER_SHARE = 1.0`, `ETF_TICK_SIZE = 0.01`, baseline commission and slippage). Optionally includes borrow-cost component at S1 baseline if short side is enabled.

FS5. A locked acceptance gate set: inherit A1-A10 from spec section 13 byte-equivalent (`A1 >= 100 trades`, `A2 sharpe > 0`, `A3 expectancy > 0`, `A4 MaxDD <= 50%`, `A5 WR-gap >= +0.5pp portfolio AND >= 2/4 markets`, `A6 upstream PASS`, `A7 effective_independent_bets >= 2.5`, `A8 cost-stress matrix complete`, `A9 C1-C8 safety`, `A10 cap_binding == 0`).

FS6. A locked rejection gate set: inherit K1-K11 + K12 byte-equivalent.

FS7. A locked OOS-blocking structural enforcement plan.

FS8. A planned protocol step sequence: Step 02b (already done as data inheritance), Step 02c (re-audit on the same CSVs is optional given the s7 D1 audit; can attest by reference instead), Step 03 (new loader package or reuse s7 D1 loader byte-equivalent -- TBD in the first-step plan), Step 04 (new validator), Step 05 (NEW signal module for RSI-2 mean-reversion; this replaces the Donchian channel computation), Step 06 (simulator with no-pyramid sizing), Step 07 (aggregator with same verdict enum).

The first-step plan is NOT authored by THIS selection plan; it requires a fresh operator authorization turn.

## 18. Files that may be created later (by future authorized turns; NOT this turn)

If the recommended next track is authorized in a subsequent turn, the following file paths MAY be created by future build phases (each requires its own separate authorization):

- `docs/s9_cross_asset_mean_reversion_rsi2_spec.md` (Tier-N spec)
- `docs/s9_cross_asset_mean_reversion_rsi2_step_*.md` (per-step plans mirroring the s7 D1 structure)
- `external_research_hunter/s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_loader/` (likely reuses s7 D1 loader byte-equivalent; TBD in the first-step plan)
- `external_research_hunter/s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_validator/`
- `external_research_hunter/s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_signal/` (NEW signal module; this is where RSI-2 logic lives)
- `external_research_hunter/s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_simulator/` (likely reuses s7 D1 simulator with no-pyramid configured)
- `external_research_hunter/s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_aggregator/` (likely reuses s7 D1 aggregator byte-equivalent)
- `tests/external_research_hunter/s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_*/`
- `reports/s9_cross_asset_mean_reversion_rsi2_step_*_build_report.{json,md}`

Naming, ordering, and exact paths are determined by the first-step plan turn, not by this selection plan.

## 19. Files that must not be touched (this turn or any onward turn outside its own scope)

Permanently off-limits unless an explicitly authorized turn names the specific file as its target:

- All s7 D1 ETF-proxy artifacts (every file in `external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_*/`, every file in `tests/external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_*/`, every `reports/s7_d1_cross_asset_donchian_*` file).
- The four canonical CSVs at `data/s7_d1_cross_asset_donchian/raw/*.csv`.
- `data/s7_d1_cross_asset_donchian/raw/fetch_run_manifest.json` and `audit_manifest.json`.
- All s7 D1 plan files in `docs/s7_d1_cross_asset_donchian_step_*.md`.
- The s7 D1 spec `docs/s7_d1_cross_asset_donchian_spec.md`.
- The s7 D1 park report.
- The brain_memory lesson appended at commit c6730d2 (further appends to the same file require separate authorization; the existing entry shall NOT be modified or rewritten).
- All Databento-track artifacts under `external_research_hunter/s7_d1_cross_asset_donchian_runner_harness/`, `external_research_hunter/s8_d1_cross_asset_donchian_no_pyramid_runner_harness/`, and any Databento cache directory.
- `review_queue.json`, the production `idea_memory` directory, all Strategy Lab artifacts.
- All ORB branch artifacts and Step 30 cost constants.
- `CLAUDE.md`, `docs/decisions.md`, `RUNBOOK`, `pipeline_manifest`, `.gitignore`.

## 20. Validation gates and HALT conditions for this selection plan

Validation gates the plan-authoring turn satisfies:

V1. ASCII-only.
V2. Numbered sections in monotonic order (1..21).
V3. No execution language (no "build the next track now"; no "fetch data now").
V4. No self-authorization (this plan does NOT authorize the recommended track to be built; only a separate operator turn does that).
V5. No code modification.
V6. No backtest run.
V7. No simulator run.
V8. No signal computation.
V9. No data fetch.
V10. No network IO.
V11. No live trading.
V12. No prior-phase artifact modification.
V13. The committed plan file is the ONLY file changed in this turn's commit.

HALT conditions:

H1. If any V-gate fails, the plan-authoring turn HALTs.
H2. If the pre-stage git index is non-empty, the turn HALTs and remediates by unstaging contaminants before staging the plan.
H3. If the staged file count is anything other than 1 at commit time, the turn HALTs and remediates.
H4. If the seal recomputation of any prior phase report does not match its pinned value, the turn HALTs and surfaces the drift.

## 21. Next authorization language

A future operator authorization is required to proceed beyond this selection plan. That authorization shall reference this plan by exact path:

`docs/next_research_track_selection_plan_after_s7_d1_park.md`

The next operator authorization in the established controller-session pattern shall use one of these scopes:

- **"Authorize s9 cross-asset mean-reversion RSI-2 Tier-N specification plan only"** (if accepting the recommended track and beginning the first-step plan-authoring turn).
- **"Authorize alternative track selection plan revision only"** (if rejecting T1 and asking for a different recommendation among T2-T7).
- **"Authorize hunter-brain survey only"** (if first wanting a triage of the existing `b005_*` / `b006_*` / `packet3_*` diagnostic harness directories before committing to any track).
- **"Authorize family-level park only"** (if accepting that mean-reversion test is premature and choosing to formally park the trend-following + mean-reversion + sizing-variation arc on this universe altogether).

This selection plan is the source of truth for the four authorized next-step options. Authorizing anything else requires either a fresh selection-plan revision or an out-of-band justification.

No phase of this chain confers any standing authorization for live trading, brokerage connection, Strategy Lab promotion, OOS inspection, or production candidate registration. Each remains BLOCKED at separate plans. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES.

----

End of plan. Plan-authoring turn only. No code. No backtest. No simulator. No signal. No data fetch. No yfinance. No Yahoo Finance. No Databento. No DATABENTO_API_KEY access. No brokerage. No real order. No paper order. No Strategy Lab promotion. No review_queue mutation. No production idea_memory mutation. No ORB branch mutation. No live trading. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES.
