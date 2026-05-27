# Next Research-Track Selection Plan -- after s9 RSI-2 ETF-proxy park

Status: PLAN_ONLY (no track is built or run by this plan; the next track requires its own separately authorized plan-authoring turn).
Authored: 2026-05-26
Predecessor park: s9 cross-asset mean-reversion RSI-2 ETF-proxy, parked at PARKED_SAFE_BUT_NOT_MONEY_PROVEN.
Predecessor park report: reports/s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_park_report.json (sha256 cefa80e7b4c2e73f66d5ff4aad37bcb329247e7f16691f92b6d3b748666542c3, report_seal_sha256 026595ed2b1d81589d5a946bd0fd897e182736b75c15ce8a0c3e9f0d585b94c7, commit 9cf2f56)
Predecessor park report MD: reports/s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_park_report.md (sha256 7c2128b5faf1b872e0ac34d6050e60ab5ae64c90d5feb6eaedd1454ad6173b18)
Predecessor IS decision memo: reports/s9_cross_asset_mean_reversion_rsi2_is_decision_memo.json (sha256 30da17f4d9f04a07a36e5300df38f75ae111ba2c9dc15efa5f73ea7c660d8e71)
Predecessor lesson append: brain_memory/projects/trading_bot/lessons.md (terminal lesson appended at commit efa3076; further appends require separate authorization)
Sibling selection plan precedent: docs/next_research_track_selection_plan_after_s7_d1_park.md (this plan inherits its structure)

HARD BOUNDARIES (held by this plan). Plan only. No strategy code. No backtest. No simulator. No new signal computation. No OOS inspection. No data fetch. No yfinance import. No Yahoo Finance call. No Databento call. No DATABENTO_API_KEY access. No network IO. No review_queue.json mutation. No production idea_memory mutation. No Strategy Lab run. No candidate promotion. No s9 resurrection. No s9 code, report, CSV, manifest, or park report modification. No s7 D1 artifact mutation. No ORB branch artifact mutation. No Step 30 cost constant mutation. No CLAUDE.md modification. No docs/decisions.md modification. No RUNBOOK modification. No pipeline_manifest modification. No .gitignore modification. No branch change. No branch creation. No commit beyond the single new plan file. No git push. No live trading. No profitability claim. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES. FRC never granted.

----

## 1. Purpose

Author a sealed selection plan for the next trading research track to follow the s9 cross-asset mean-reversion RSI-2 ETF-proxy chain (now terminally parked at PARKED_SAFE_BUT_NOT_MONEY_PROVEN per commit 9cf2f56, terminal lesson appended at commit efa3076). The selection plan does NOT build any track; it surveys what is repo-available, applies the operator's selection criteria, ranks candidate directions, and produces a single recommended next track plus a recommended first step. The chosen track itself requires a fresh separately authorized plan-authoring turn before any code is written.

This selection plan inherits the cumulative two-track universe-level finding: on SPY/TLT/GLD/USO 2014-2022, both a trend-following mechanic (s7 D1 Donchian-55/20 with pyramid) and a mean-reversion mechanic (s9 RSI-2 Connors canonical) empirically failed at canonical parameters with realistic ETF-proxy costs. The validated diversification finding (effective_independent_bets ~ 3.56; avg_pairwise_dependence ~ 0.041) holds across both mechanics. The negative result is now a family-level finding, not a single-mechanic finding.

## 2. Current terminal state of s9 RSI-2 ETF-proxy

The s9 cross-asset RSI-2 mean-reversion ETF-proxy chain is FORMALLY PARKED:

- candidate_record_id: `s9-cross-asset-mean-reversion-rsi2-spy-tlt-gld-uso-yfinance-proxy`
- terminal_verdict: PARKED_SAFE_BUT_NOT_MONEY_PROVEN
- park_report_commit: `9cf2f56`
- lesson_append_commit: `efa3076`
- chain_commits: 10 commits ending at the park report
- active_K_path: K1 (Sharpe proxy per trade < 0) OR K2 (expectancy per trade <= 0) at S1 baseline
- DR rules fired: NONE (the verdict is via K-gates, not DR-rules)
- supporting metrics (S1 baseline):
  - `total_closed_trades_portfolio = 414` (clears K9 comfortably)
  - `total_net_pnl_dollars_s1_baseline = -1334.87` (negative at S1; primary trigger)
  - `sharpe_proxy_per_trade_s1 = -0.097135` (fails A2 threshold > 0)
  - `expectancy_per_trade_dollars_s1 = -3.224` (fails A3 threshold > $0)
  - `portfolio_win_rate_s1 = 0.5314` vs implied breakeven `0.6244` -> `win_rate_gap_to_breakeven_pp_s1 = -9.30 pp` (fails A5)
  - `trade_curve_max_drawdown_pct_vs_starting_cash_s1 = 1.64%` (clears K4 comfortably -> the SAFE part of the verdict)
  - `effective_independent_bets = 3.5585` (clears A7); `avg_pairwise_dependence_measure = 0.0414` (clears K10)
  - per-symbol net PnL S1: SPY +$140.09; GLD -$194.13; TLT -$104.23; USO -$1176.60
  - cost-stress matrix S0/S1/S2/S3 net PnL: -$1211 / -$1335 / -$1578 / -$1826 (all four tiers negative)
  - smoking-gun: at S0 (zero slippage, zero commission) the strategy STILL loses money over 414 trades -> negative edge before costs
- OOS: never inspected; structurally blocked per spec
- Strategy Lab: untouched
- review_queue.json: untouched
- idea_memory: untouched
- broker: not connected
- live trading: BLOCKED at six gates
- advisory_label_permanent: DIAGNOSTIC_ONLY_NOT_LIVE_GRADE
- "do not iterate s9 parameters without rev-N spec" recorded permanently in park report

## 3. Lessons inherited from s9 RSI-2

The next track MAY inherit (and SHOULD where applicable):

- **Cross-asset diversification works on this universe under mean-reversion sizing too**. avg_pairwise_dependence_measure = 0.0414 and effective_independent_bets = 3.5585 on SPY/TLT/GLD/USO with 414 RSI-2 trades. The diversification finding from s7 D1 (measured under trend-following) is mechanic-agnostic on this universe.
- **The Step 06 simulator framework (with full S0/S1/S2/S3 cost-stress matrix) is reusable byte-equivalent for any next mechanic**. The s9 build proved the simulator generalizes from trend-following to mean-reversion without modification.
- **The aggregator + K-gate framework correctly catches false-edge before any OOS authorization**. K1 + K2 fired before K9 (sample size) was ever an issue. Protocol working as designed.
- **A safe-but-not-money-proven outcome is a distinct closed-enum verdict from REJECT_FAST**. PARKED_SAFE_BUT_NOT_MONEY_PROVEN preserves the candidate's safety profile while explicitly disqualifying it on edge grounds. Future tracks may produce the same verdict class without contamination.
- **High trade density (414 trades over IS) does not rescue a negative-edge mechanic**. Trade count above K9 is necessary but not sufficient; if expectancy is negative, more trades produce more loss.
- **At S0 negative -> family-level falsification on this universe**. A mechanic that loses money at zero cost is structurally weak; cost only amplifies the loss. This is a stronger signal than s7 D1's cost-stress-sensitive REJECT_FAST.

## 4. Lessons NOT inherited from s9 RSI-2

The next track must NOT inherit (and SHALL refuse to inherit):

- **The locked RSI(2) <10 / >50 entry-exit thresholds on the SPY/TLT/GLD/USO universe at the s9 canonical sizing**. This combination empirically lost money at all four cost tiers including S0. Any "tightened RSI(2) <5 / >55" rebadge requires its own _revN_ spec under the threshold-lock invariant.
- **Any rebadging of s9 RSI-2 with relaxed A-thresholds**. The spec threshold-lock invariant forbids loosening `A2 sharpe_proxy_per_trade > 0` or `A3 expectancy_per_trade_dollars > 0`; loosening either would mean accepting that a money-losing mechanic is "good enough".
- **Single-asset-bears-loss outcomes**. In s9, USO was the dominant loss contributor (-$1177 of the -$1335 portfolio net). A future "diversified" track whose loss concentrates in one symbol replicates the structural pathology s9 exposed. Per-symbol contribution distribution shall remain a first-class diagnostic.
- **Any unjustified return to the SPY/TLT/GLD/USO 2014-2022 universe with a "third try" mechanic without a first-principles reason different mechanics would survive**. Two structurally orthogonal mechanics (trend / mean-reversion) at canonical parameters both empirically failed. A "third try" candidate must explicitly state why its mechanic addresses both failure modes (cost-sensitivity at s7 D1; negative-edge-at-S0 at s9).
- **Implicit assumption that diversification rescues a negative-edge mechanic**. avg_pairwise_dependence ~ 0.04 measures bet independence; it does NOT rescue an edge. Future plans shall keep these two concepts separate.

## 5. Candidate-track selection criteria (positive)

A candidate track is acceptable iff it satisfies ALL of:

C1. **Uses existing clean data or low-friction data**. The four sealed ETF CSVs at data/s7_d1_cross_asset_donchian/raw/ remain reusable. Any additional data requires its own data-fetch authorization at zero or near-zero cost.

C2. **Has enough trade count to clear K9**. Expected `total_closed_trades >= 100` over the in-sample window. s9 demonstrated 414 trades is feasible at RSI-2 frequency; future candidates can target similar or higher.

C3. **Does not rely on one asset carrying all profit or all loss**. The track shall produce expected per-symbol contributions that are not maximally concentrated. A track that anticipates one-asset-dominance shall justify why and shall design diagnostics that detect that pattern explicitly.

C4. **Has explicit cost-stress testing from the beginning**. The S0/S1/S2/S3 cost-stress matrix from spec section 10 is locked. The candidate's diagnostic shall include all four tiers in the first IS run, not as an afterthought.

C5. **Addresses the cumulative two-track universe falsification**. Either (a) move OFF the SPY/TLT/GLD/USO universe to a different asset class / universe where the falsification does not apply; OR (b) state a falsifiable first-principles reason a third mechanic on the same universe would survive where trend + mean-reversion both failed. Option (b) carries a higher burden of justification than option (a).

C6. **First-principles rationale**. The candidate shall have a stated reason WHY it might survive where s7 D1 + s9 did not. Not "it's worth trying" but a concrete falsifiable hypothesis about the mechanism that broke both prior tracks.

C7. **One-cycle scope**. The candidate shall be doable in a single plan -> build -> seal -> verdict cycle within reasonable bounds. No multi-year build.

C8. **Inheritable safety template**. The candidate shall be able to inherit the Phase 2 safety template (C1-C8 attestations) byte-equivalent or with minor track-specific extensions.

## 6. Reject-fast criteria for next track (negative)

A candidate track is REJECTED FAST in this selection plan iff ANY of:

R1. Track rebadges s7 D1 or s9 or any other parked candidate.
R2. Track requires loosening any K-threshold or A-gate threshold.
R3. Track requires expensive data before a cheap diagnostic could be run.
R4. Track requires live trading or brokerage connection to evaluate.
R5. Track requires Strategy Lab promotion to evaluate.
R6. Track has structural sample-size bottleneck (expected closed trades < 100).
R7. Track silently re-introduces a filter, regime gate, or selection rule that the prior parked spec locked to NONE.
R8. Track operates on a universe known to be empirically falsified by at least two orthogonal-mechanic priors (e.g., a "third mechanic on SPY/TLT/GLD/USO 2014-2022") without a fundamentally new mechanic that explicitly addresses BOTH prior failure modes.
R9. Track depends on a survivorship-cherry-pick selection rule (e.g., "pick the best of N markets after the run").
R10. Track conflates diversification with edge (assumes effective_independent_bets > 2.5 implies positive edge).

## 7. Data availability criteria

Preferred data sources (in priority order):

D1. **Sealed s7 D1 / s9 ETF-proxy CSVs (same dataset)**: SPY/TLT/GLD/USO daily bars, 2014-01-02 through 2026-05-22, sha-pinned in audit_manifest.json. Zero new fetch. Zero new vendor call. Re-use across mechanics is free. Note: if the next track moves off this universe (per C5 option a), this data source is not relevant for the new universe.

D2. **A separately authorized expanded ETF universe via yfinance operator-side fetch**: e.g., add IWM/EFA/AGG/DBC (broaden the cross-asset bundle) OR shift to sector ETFs (XLE/XLF/XLK/XLV/XLU) OR shift to international (EFA/EEM/EWJ/IWM) OR shift to single-name equities. Each is a separate Step 02b-equivalent operator-side fetch turn under its own authorization. Still zero paid data.

D3. **Databento `GLBX.MDP3` futures cache**: parallel-track sibling continues to use Databento. The ETF-proxy follow-up should NOT switch vendors mid-stream; that's a different research track and a separate authorization scope.

D4. **The s10 D1 micro futures availability probe matrix (operator-side, sealed read-only memo)**: `reports/external_research_hunter/s10_d1_micro_availability_probe_result_memo.md` documents what continuous micro futures symbols (MNQ.c.0 / MGC.c.0 / MCL.c.0) are available on Databento by date. Re-usable if a micro-futures candidate is selected; does NOT require any new vendor call to consult.

DR_REJECTED_FOR_THIS_TRACK. Any candidate requiring fresh paid data downloads is rejected for first-cycle evaluation; if the track survives a cheap-data diagnostic, an expensive-data follow-up may be authorized separately.

## 8. Cost-stress requirements

Every candidate track shall:

CS1. Define its cost model in the candidate's Tier-N spec at locking time, including the ETF-proxy adaptation (`ETF_DOLLAR_PER_SHARE = 1.0`; `ETF_TICK_SIZE = 0.01`; baseline commission and slippage) or its appropriate analog for the chosen universe.
CS2. Run the full S0/S1/S2/S3 cost-stress matrix in the first IS diagnostic (not deferred to a follow-up cycle).
CS3. Evaluate DR2 (S2/S3 material degradation), DR3 (zero-cost-only survival), DR5 (S0->S1 edge negative), K1 (Sharpe<0), K2 (expectancy<=0). DR4 deferred to OOS phase.
CS4. Pre-register the cost-stress tolerance: a track that survives ONLY at S0 is canonically false-edge (s7 D1 lesson); a track that fails at S0 is canonically negative-edge (s9 lesson). Either is a park signal.
CS5. If the candidate uses borrow cost (e.g., short ETFs), add a borrow-cost component to the cost model at S1 baseline, do not defer.

## 9. Diversification requirements

Every candidate track shall:

DV1. Operate on at least 4 distinct asset families (equity-index, bonds, metals, energy, or substitutes) UNLESS the candidate is explicitly a single-symbol diagnostic justified by first-principles.
DV2. Measure per-symbol contribution to portfolio PnL AND per-symbol contribution to portfolio loss. A track whose IS run shows one symbol contributing > 80% of net PnL or > 80% of net loss is structurally suspect.
DV3. Compute and report `avg_pairwise_dependence_measure` and `effective_independent_bets` per the aggregator pattern; A7 (`effective_independent_bets >= 2.5`) and K10 (`avg_pairwise_dependence_measure <= 0.50`) thresholds inherited byte-equivalent.
DV4. Explicitly disclaim that diversification independence does NOT imply positive edge (carried lesson from s9).

## 10. Sample-size requirements

SS1. Expected `total_closed_trades >= 100` across the in-sample window (per K9 threshold).
SS2. s9 produced 414 trades; future RSI-frequency mechanics on similar universes can safely target similar.
SS3. Per-symbol minimum: at least 10 closed trades per symbol over the IS window (per-market WR computation is unreliable below this).
SS4. The K9 sample-size bottleneck is no longer the dominant park cause (s9 cleared it comfortably); the dominant park cause is now negative edge at S0 (s9) or cost-stress sensitivity (s7 D1). Tracks shall pre-register their expected edge sign and magnitude.

## 11. OOS-locking policy (inherited unchanged)

The spec section 11 `oos_inspection_blocked_at_in_sample` invariant remains in force for every future track:

OL1. OOS data (`2023-01-01` through `2025-12-30`) shall not be inspected, computed against, simulated over, or queried in any form during the in-sample diagnostic phase.
OL2. Post-OOS data (`2026-01-02` through `2026-05-22` for the ETF proxy track) is informational only; no diagnostic uses it.
OL3. OOS inspection requires a separately authorized turn that follows an IS-window run verdict of ELIGIBLE_FOR_OOS plus an explicit operator approval.
OL4. The next track's loader, validator, signal, simulator, and aggregator modules shall inherit the IS-only structural enforcement pattern from the s7 D1 / s9 modules.

## 12. No-live / no-Strategy-Lab / no-brokerage policy (inherited unchanged)

Every future track shall enforce:

NL1. No live trading authorization conferred by any IS verdict.
NL2. No Strategy Lab promotion conferred by any IS verdict.
NL3. No brokerage connection conferred by any IS verdict.
NL4. No review_queue.json mutation.
NL5. No production idea_memory mutation outside explicitly authorized memory/lesson append targets.
NL6. No paper-trade loop, no scheduler integration, no autopilot, no FRC gate touch.
NL7. The six live-trading gates remain BLOCKED regardless of verdict, regardless of how many sealed seals stack.
NL8. The `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` advisory label is the default for every park-class verdict; it does not lift under any verdict in the closed enum.

## 13. Candidate ranking rubric

Each candidate is scored 0-5 against 10 criteria (50 max):

- **R1_addresses_both_prior_failure_modes:** 5 = directly addresses BOTH cost-stress sensitivity (s7 D1) AND negative-edge-at-S0 (s9); 0 = doesn't address.
- **R2_uses_existing_clean_data_OR_moves_off_falsified_universe:** 5 = reuses sealed ETF CSVs as-is on a different mechanic with strong first-principles for survival; 5 = moves off SPY/TLT/GLD/USO to a different universe where the falsification does not apply; 1 = expensive new data needed.
- **R3_clears_K9_sample_size:** 5 = expected >> 100 trades; 3 = expected ~100-200; 1 = expected < 100.
- **R4_per_symbol_contribution_balance_expected:** 5 = expected balanced contribution; 3 = expected some concentration; 0 = expected one-asset dominance (loss OR profit).
- **R5_built_in_cost_stress_AND_s0_edge_pre_registered:** 5 = candidate explicitly pre-registers expected sign and magnitude of edge at S0; 3 = cost-stress framework reusable but no pre-registration; 0 = no edge sign claim.
- **R6_first_principles_rationale:** 5 = strong, falsifiable, ties to BOTH s7 D1 AND s9 evidence; 1 = ad hoc.
- **R7_different_family_from_donchian_AND_rsi2:** 5 = orthogonal to both trend-following AND mean-reversion families (e.g., carry, rotation, vol-targeting, statistical arbitrage); 3 = same family with different parameters (caveat: R1/R2 below); 0 = pure rebadge.
- **R8_one_cycle_scope:** 5 = clearly doable; 1 = scope-creep risk.
- **R9_safety_template_inheritable:** 5 = inherits byte-equivalent; 1 = needs adaptation.
- **R10_explicit_oos_blocked:** 5 = OOS structurally blocked by design; 1 = needs extra plumbing.

Total >= 40 is acceptable; >= 45 is recommended.

## 14. Possible next tracks discovered from the repo

Read-only repo survey (no files modified during this enumeration) reveals the following possible directions:

T1. **Cross-sectional momentum rotation on the existing four-ETF universe** (and/or a wider ETF basket). Each month rank N ETFs by trailing 3-6 month total return; hold top K; rebalance monthly. Caveat per s9 finding: rotation is loosely a third family but still trend-adjacent on this universe; first-principles burden is high.

T2. **Risk-parity rebalanced N-asset portfolio** on SPY/TLT/GLD/USO (or wider). Targets equal risk contribution per asset; rebalances quarterly or monthly. Tests sizing, not signal. Useful as a control benchmark.

T3. **Vol-targeted long-only basket** on the four ETFs. Mirrors the existing `b006_001` / `b006_002` SPY-only vol-targeting lineage but expanded to a 4-asset universe. Caveat: B006_002 archival memo identified the C4 leverage-cap-bound pattern as intrinsic to the SPY 10%-target / 1.0x-cap design; expanding to 4 assets does not automatically escape this.

T4. **Move off SPY/TLT/GLD/USO to a sector-ETF universe**: XLE/XLF/XLK/XLV/XLU/XLI/XLB/XLP/XLY/XLRE/XLC. Either same mechanic on a different universe (re-test the universe-falsification finding) OR a different mechanic on a different universe (move two axes). Requires separately authorized Step 02b-equivalent fetch.

T5. **Move off SPY/TLT/GLD/USO to international ETF universe**: EFA / EEM / EWJ / VEU / VWO. Same comments as T4.

T6. **Move off ETF-proxy universe to single-name equities**: a Donchian or RSI-2 mechanic on a 10-20 single-name equity basket. Different universe; different cost structure (per-share commission scales differently than ETF); different signal density. Highest data-fetch friction among the options.

T7. **Pivot to a Databento micro-futures track**: per S10-D1 memo (`reports/external_research_hunter/s10_d1_micro_availability_probe_result_memo.md`), MNQ.c.0 / MGC.c.0 are available from 2019 onward (MGC from 2013); MCL.c.0 from mid-2021 onward. Three sub-options inherited from S10-D1 section 6: Path A (long-history MNQ+MGC two-market candidate), Path B (2021+ MNQ+MGC+MCL short-history), Path C (probe alternate micros). Substantial structural break from the ETF-proxy chain.

T8. **Family-level park**. Declare the SPY/TLT/GLD/USO 2014-2022 universe empirically falsified across two orthogonal mechanics; formally park the whole arc (trend / mean-reversion / sizing-variations on this universe) without authorizing another track on the same universe.

T9. **Hunter-brain harness survey**. Several diagnostic harness directories exist under `external_research_hunter/`. The B006_001 SPY vol-targeting lifecycle is COMPLETE+ARCHIVED (verdict REQUEST_FULL_PREREGISTRATION_REVIEW; archived). The B006_002 SPY vol-targeting C4-enforced lifecycle is COMPLETE+ARCHIVED (verdict REJECT_FAST). The b005_001/b005_004/b005_005/b005_006/packet3 harnesses may be in various unfinished states. A read-only triage may be worth doing as a parallel low-cost survey before authorizing any new build.

T10. **Operator-directed pivot to a different research domain entirely** (e.g., NKE single-name options revisit, Hydra/video work, affiliate work). Not strictly a "next research track" within the trading-bot project but available per the s9 park report's "operator-directed pivot" option.

## 15. Recommended next track

**Recommendation:** **T8 paired with T7-Path-A** -- formally park the SPY/TLT/GLD/USO 2014-2022 ETF-proxy universe at the family level (two orthogonal mechanics empirically falsified), AND open a parallel new track on a structurally different universe via the Databento micro-futures Path A (long-history MNQ+MGC two-market candidate per the S10-D1 memo).

Proposed candidate_record_id for the new track: `s10-d1-cross-asset-trend-or-meanrev-mnq-mgc-databento-long-history` (deliberately NOT s9-revN; deliberately NOT on the falsified ETF-proxy universe; uses the S10-D1 memo's verified availability matrix to start from 2019 onward).

Scoring against section 13 rubric:

| Criterion | Score |
|---|---:|
| R1_addresses_both_prior_failure_modes | 5 (moves off the falsified universe; cost structure and edge dynamics differ on futures) |
| R2_uses_existing_clean_data_OR_moves_off_falsified_universe | 5 (uses Databento micros per S10-D1 memo verified availability) |
| R3_clears_K9_sample_size | 4 (depends on mechanic; default daily-bar trend or RSI mechanics on 2 symbols over ~6 years expect 100-400+ trades) |
| R4_per_symbol_contribution_balance_expected | 4 (two-market basket; concentration risk is binary; tail risk noted) |
| R5_built_in_cost_stress_AND_s0_edge_pre_registered | 5 (next track's Tier-N plan shall pre-register expected edge sign at S0) |
| R6_first_principles_rationale | 5 (futures cost structure, leverage capability, and edge profile are structurally different from ETF proxies; the SPY/TLT/GLD/USO falsification does not transfer to MNQ/MGC) |
| R7_different_family_from_donchian_AND_rsi2 | 4 (the first-step plan picks mechanic family; recommended default: a different family than both s7 D1 and s9; specific choice deferred to first-step plan) |
| R8_one_cycle_scope | 4 (clearly doable but Databento data ingest path needs its own Step 02b-equivalent under operator-side fetch authorization) |
| R9_safety_template_inheritable | 5 (Phase 2 safety template C1-C8 inheritable byte-equivalent) |
| R10_explicit_oos_blocked | 5 (OOS structurally blocked by design; inherits from s7 D1 / s9 patterns) |
| **Total** | **46 / 50** |

The T8 component (family-level park of SPY/TLT/GLD/USO) is a record-only finding that does not consume a build cycle; it is authored alongside or before the T7-Path-A first-step plan.

## 16. Why that track is next (rationale)

**Two structurally orthogonal mechanics (s7 D1 Donchian trend; s9 RSI-2 mean-reversion) at canonical parameters with realistic ETF-proxy costs both failed on SPY/TLT/GLD/USO 2014-2022.** That is a family-level finding, not a single-mechanic finding. The honest interpretation is:

- **The universe is now empirically suspect at canonical parameters across mechanics**. A "third try" on the same universe with a third mechanic carries a high first-principles burden (per C5 / R8). Most candidates that would naively be "the third try" (rotation, risk-parity, vol-targeting) do not have a strong first-principles answer for what they fix that the prior two missed.
- **The diversification finding (effective_independent_bets ~ 3.56) is genuine and re-usable**, but it does NOT rescue an edge. The s9 lesson is explicit: 4 truly independent loss-makers produce 4 truly independent losses.
- **Moving off the falsified universe is the cleanest forward step**. Different asset class (futures), different cost structure (per-contract scaling), different signal density (intraday data available), different edge profile (term-structure / carry / overnight / margin dynamics).
- **The S10-D1 memo already provides verified availability evidence** for MNQ.c.0 (2019+) and MGC.c.0 (2013+). Path A's two-market candidate is the lowest-friction pivot: long-history MGC + post-2019 MNQ; common-history start 2019; sample size adequate; no waiting for additional probes.
- **Authoring the family-level park (T8) alongside the pivot does NOT consume resources**; it is a one-time record-only memo that closes the SPY/TLT/GLD/USO 2014-2022 arc and prevents future "third try" candidates from accidentally being authorized.

**Why NOT T1 (cross-sectional momentum rotation on the same universe):** rotation is loosely a third family but still trend-adjacent on this universe; the s7 D1 failure was at low frequency, the s9 failure was at high frequency, and rotation lives somewhere in between. The first-principles burden for surviving where both endpoints failed is high.

**Why NOT T2 / T3 (risk-parity / vol-targeted basket on same universe):** both test sizing, not signal. They risk producing the same per-asset pathology (per-symbol contribution concentration) without a different signal mechanic. The B006_002 archival memo's identification of the SPY 10%-target / 1.0x-cap leverage-cap-bound pattern as intrinsic also applies to expanded vol-targeting variants on this universe.

**Why NOT T4 / T5 (sector / international ETFs):** these are valid moves OFF the falsified universe but require fresh Step 02b-equivalent operator-side fetch turns AND a fresh mechanic selection AND test universe-falsification on a new universe. T4/T5 are good Phase-N follow-ups after T7-Path-A's first cycle completes.

**Why NOT T6 (single-name equities):** highest data-fetch friction; per-share commission scaling differs from ETFs; signal density depends on liquidity assumptions. Defer until after the futures pivot.

**Why NOT T9 (hunter-brain survey first):** worth doing as a parallel triage but not blocking the next research track. The major B006_NNN candidates are now complete (B006_001 archived REQUEST_FULL_PREREGISTRATION_REVIEW; B006_002 archived REJECT_FAST). Remaining surveys are cleanup, not blockers.

**Why NOT T10 (cross-domain pivot):** out of scope for "next research track" within the trading-bot project. Available as an operator-directed override but not a default.

## 17. First step of the recommended next track

The first step of the recommended next track is to author the **family-level park memo (T8)** AND the **Tier-N specification plan for the T7-Path-A futures candidate**, each under a separately authorized turn (mirroring how s7 D1 began with its Step 02b plan). The first-step plans shall include:

FS1. A fresh `candidate_record_id` distinct from any parked predecessor. Proposed for the futures track: `s10-d1-cross-asset-trend-or-meanrev-mnq-mgc-databento-long-history` or similar; exact name fixed at first-step plan turn.

FS2. A locked mechanic-family selection (default proposal subject to operator revision): given that BOTH trend and mean-reversion families have empirical priors on the ETF-proxy universe, the futures candidate should default to either (a) the same family the operator has the strongest prior for, OR (b) a structurally different family (e.g., carry / term-structure / volatility-of-volatility). The exact choice is deferred to the first-step plan.

FS3. A locked sizing mechanic. Default proposal: per-contract notional sizing at 1% portfolio-equity risk per signal using ATR(20) for stop distance; NO pyramid (single contract per symbol per signal). Inherits the no-pyramid lesson from s7 D1's sibling Databento s8 track.

FS4. A locked cost model with full S0/S1/S2/S3 cost-stress matrix, inheriting the futures-contract adaptation (per-contract commission, ATR-scaled slippage in ticks). Pre-registered S0 edge sign and magnitude (carried lesson from s9).

FS5. A locked acceptance gate set: inherit A1-A10 from the s7 D1 / s9 spec section 13 byte-equivalent.

FS6. A locked rejection gate set: inherit K1-K12 byte-equivalent.

FS7. A locked OOS-blocking structural enforcement plan.

FS8. A planned protocol step sequence: Step 02b (Databento operator-side fetch authorization for MNQ.c.0 + MGC.c.0 daily bars over the IS window starting 2019-01-02 or earliest common-history), Step 02c (raw-data audit), Step 03 (loader, may inherit s7 D1 loader byte-equivalent for daily bars), Step 04 (validator), Step 05 (NEW signal module for the chosen mechanic family), Step 06 (simulator with no-pyramid sizing), Step 07 (aggregator with same verdict enum).

The first-step plan is NOT authored by THIS selection plan; it requires a fresh operator authorization turn.

In parallel, the family-level park memo (T8) for the SPY/TLT/GLD/USO 2014-2022 universe is a separate single-turn record-only memo that closes the arc:

T8_FS1. Park report path: `reports/spy_tlt_gld_uso_2014_2022_etf_proxy_universe_family_level_park_memo.{md,json}` (or similar; exact path fixed at the memo-authoring turn).
T8_FS2. Cites s7 D1 + s9 + B006_001 + B006_002 as the four cumulative pieces of evidence.
T8_FS3. Records explicit "no further mechanic-variant candidates on this universe without first-principles burden satisfaction" rule.
T8_FS4. Records `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` permanent advisory for the universe.
T8_FS5. Does NOT modify s7 D1 / s9 / B006_001 / B006_002 sealed artifacts.

## 18. Files that may be created later (by future authorized turns; NOT this turn)

If the recommended next track is authorized in a subsequent turn, the following file paths MAY be created by future build phases (each requires its own separate authorization):

- `docs/spy_tlt_gld_uso_etf_proxy_universe_family_level_park_memo_plan.md` (T8 memo-authoring plan)
- `reports/spy_tlt_gld_uso_2014_2022_etf_proxy_universe_family_level_park_memo.{md,json}` (T8 memo itself)
- `docs/s10_d1_databento_long_history_mnq_mgc_tier_n_spec.md` (T7-Path-A Tier-N spec)
- `docs/s10_d1_databento_long_history_mnq_mgc_step_*.md` (per-step plans mirroring the s7 D1 / s9 structures)
- `external_research_hunter/s10_d1_databento_long_history_mnq_mgc_*/` (loader / validator / signal / simulator / aggregator package directories)
- `tests/external_research_hunter/s10_d1_databento_long_history_mnq_mgc_*/`
- `reports/s10_d1_databento_long_history_mnq_mgc_step_*_build_report.{json,md}`
- `data/s10_d1_databento_long_history_mnq_mgc/raw/*.csv` (or equivalent Databento ingest path)

Naming, ordering, and exact paths are determined by the first-step plan turns, not by this selection plan.

## 19. Files that must not be touched (this turn or any onward turn outside its own scope)

Permanently off-limits unless an explicitly authorized turn names the specific file as its target:

- All s7 D1 ETF-proxy artifacts (every file in `external_research_hunter/s7_d1_*_yfinance_proxy_*/`, every `reports/s7_d1_*` file, the s7 D1 plan files in `docs/s7_d1_*.md`, the four canonical CSVs at `data/s7_d1_cross_asset_donchian/raw/*.csv`, the s7 D1 park report).
- All s9 RSI-2 ETF-proxy artifacts (`external_research_hunter/s9_*/` directories, `reports/s9_*` files, `docs/s9_*.md` plan files, the s9 park report, the s9 IS decision memo, the s9 signal/simulator/aggregator build reports).
- The brain_memory lessons appended at commits a5ac092 (s7 D1) and efa3076 (s9). The existing entries shall NOT be modified or rewritten. The lessons.md file MAY have additional staged appends in future authorized turns but the historical entries are immutable.
- The brain_memory unstaged dirty state from prior controller-session appends (e.g., LESSON_B006_002_001, LESSON_B006_002_002). These shall remain dirty in the working tree; this turn does NOT stage them. Future commit hygiene is a separate authorization.
- All B006_NNN sealed artifacts (`external_research_hunter/b006_001_*/`, `external_research_hunter/b006_002_*/`, `reports/external_research_hunter/b006_*_archival_memo.{md,json}`, `reports/external_research_hunter/b006_*_result_sealing_report.{md,json}`, `reports/external_research_hunter/b006_002_qc_run_capture/*`, the B006_002 RUN_BOOK, the B006_002 operator prep, the B006_002 operator QC execution acknowledgment).
- The S10-D1 micro availability probe result memo (`reports/external_research_hunter/s10_d1_micro_availability_probe_result_memo.{md,json}`).
- All Databento-track artifacts under `external_research_hunter/s7_d1_*_runner_harness/`, `external_research_hunter/s8_d1_*_runner_harness/`, and any Databento cache directory.
- `review_queue.json`, the production `idea_memory` directory, all Strategy Lab artifacts.
- All ORB branch artifacts and Step 30 cost constants.
- `CLAUDE.md`, `docs/decisions.md` (if it exists), `RUNBOOK`, `pipeline_manifest`, `.gitignore`.

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
V14. The brain_memory dirty lessons.md remains UNSTAGED and UNTOUCHED (the LESSON_B006_002_001 / LESSON_B006_002_002 appends from prior controller-session work stay in the working tree as dirty changes; this turn does NOT add them to the index).

HALT conditions:

H1. If any V-gate fails, the plan-authoring turn HALTs.
H2. If the pre-stage git index is non-empty, the turn HALTs and remediates by unstaging contaminants before staging the plan.
H3. If the staged file count is anything other than 1 at commit time, the turn HALTs and remediates.
H4. If the staged file is anything other than `docs/next_research_track_selection_plan_after_s9_park.md`, the turn HALTs and remediates.
H5. If the dirty lessons.md is accidentally staged, the turn HALTs and `git restore --staged brain_memory/projects/trading_bot/lessons.md` before retrying.

## 21. Next authorization language

A future operator authorization is required to proceed beyond this selection plan. That authorization shall reference this plan by exact path:

`docs/next_research_track_selection_plan_after_s9_park.md`

The next operator authorization in the established controller-session pattern shall use one of these scopes:

- **"Authorize SPY/TLT/GLD/USO ETF-proxy universe family-level park memo only"** (if accepting the T8 record-only memo as the next step before opening the T7-Path-A track).
- **"Authorize s10 D1 Databento long-history MNQ+MGC Tier-N specification plan only"** (if accepting the recommended futures-pivot track and beginning the first-step plan-authoring turn).
- **"Authorize alternative track selection plan revision only"** (if rejecting the T7-Path-A + T8 pair and asking for a different recommendation among T1-T10).
- **"Authorize hunter-brain survey only"** (if first wanting a triage of the remaining diagnostic harness directories before committing to any track).
- **"Authorize family-level park only without opening new track"** (if accepting the T8 universe park but choosing not to open T7-Path-A or any other futures pivot at this time).
- **"Authorize cross-domain pivot only"** (if accepting that no further trading-bot research track is opened and the operator pivots to a different project).

This selection plan is the source of truth for the six authorized next-step options. Authorizing anything else requires either a fresh selection-plan revision or an out-of-band justification.

No phase of this chain confers any standing authorization for live trading, brokerage connection, Strategy Lab promotion, OOS inspection, or production candidate registration. Each remains BLOCKED at separate plans. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES.

----

End of plan. Plan-authoring turn only. No code. No backtest. No simulator. No signal. No data fetch. No yfinance. No Yahoo Finance. No Databento. No DATABENTO_API_KEY access. No brokerage. No real order. No paper order. No Strategy Lab promotion. No review_queue mutation. No production idea_memory mutation. No ORB branch mutation. No live trading. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES.
