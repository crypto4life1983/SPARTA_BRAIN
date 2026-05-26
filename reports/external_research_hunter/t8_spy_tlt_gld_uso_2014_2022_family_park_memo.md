# T8 -- SPY/TLT/GLD/USO 2014-2022 ETF-Proxy Universe -- Family-Level Park Memo

Status: RECORD_ONLY_FAMILY_LEVEL_PARK_MEMO (no track is opened, modified, resurrected, or extended by this memo; it is a closing record).
Authored: 2026-05-26
Authorization: "Authorize T8 + T7-Path-A paired next step after s9 park."
Selection plan reference: docs/next_research_track_selection_plan_after_s9_park.md (committed at 2ec9330)

HARD BOUNDARIES (held by this memo). Record-only memo. No strategy code. No backtest. No simulator run. No new signal computation. No OOS inspection. No data fetch. No yfinance import. No Yahoo Finance call. No Databento call. No DATABENTO_API_KEY access. No network IO. No review_queue.json mutation. No production idea_memory mutation. No Strategy Lab run. No candidate promotion. No s7 D1 resurrection. No s9 resurrection. No s7 D1 / s9 sealed-artifact modification. No B006_001 / B006_002 sealed-artifact modification. No ORB branch artifact mutation. No Step 30 cost constant mutation. No CLAUDE.md modification. No docs/decisions.md modification. No RUNBOOK modification. No pipeline_manifest modification. No .gitignore modification. No lessons.md modification or staging. No branch change. No branch creation. No git push. No live trading. No profitability claim. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES. FRC never granted.

----

## 1. Purpose

Author a single record-only memo that closes the `SPY/TLT/GLD/USO` 2014-2022 ETF-proxy universe at the family level. The memo cites two orthogonal-mechanic priors (s7 D1 Donchian trend; s9 RSI-2 mean-reversion) as the empirical evidence base, records the per-prior cost-stress and edge findings, and establishes a permanent "no further mechanic-variant candidates on this universe without first-principles burden satisfaction" rule for the universe. The memo does NOT modify any sealed prior artifact; it is additive evidence aggregation only.

This memo is the T8 component of the T8 + T7-Path-A pair recommended in `docs/next_research_track_selection_plan_after_s9_park.md` section 15. The T7-Path-A component (Tier-N spec plan for the fresh Databento MNQ+MGC long-history track) is authored separately as `docs/s10_d1_mnq_mgc_databento_long_history_tier_n_spec_plan.md` in the same controller turn.

## 2. Universe identification

| Field | Value |
|---|---|
| Universe identifier | `spy_tlt_gld_uso_2014_2022_etf_proxy` |
| Symbols | `SPY`, `TLT`, `GLD`, `USO` |
| Vendor | yfinance (operator-side fetch under Step 02b authorization) |
| Frequency | daily (close) |
| In-sample window | 2014-01-02 through 2022-12-30 |
| OOS window (never inspected on this universe) | 2023-01-01 through 2025-12-30 |
| Post-OOS data | 2026-01-02 through 2026-05-22 (informational only; no diagnostic uses) |
| Sealed dataset path | `data/s7_d1_cross_asset_donchian/raw/*.csv` (sha-pinned in audit_manifest.json) |
| Universe diversification (mechanic-agnostic) | `effective_independent_bets ~ 3.56`; `avg_pairwise_dependence_measure ~ 0.041` |

The universe itself is clean and audit-passed (Step 02c verdict PASS; 3116 rows per symbol; cross-symbol date sets aligned). The family-level park applies to the universe-mechanic-combination at canonical parameters, NOT to the underlying CSVs (which remain reusable for future authorized work).

## 3. Two orthogonal-mechanic priors cited

### 3.1 Prior P1 -- s7 D1 cross-asset Donchian trend-following

| Field | Value |
|---|---|
| `candidate_record_id` | `s7-cross-asset-donchian-no-filter-spy-tlt-gld-uso-yfinance-proxy` |
| Mechanic family | trend-following (Donchian-55 entry / Donchian-20 exit; pyramid +0.5N up to 4 units; 2N stop) |
| Park report path | `reports/s7_d1_cross_asset_donchian_yfinance_proxy_park_report.json` |
| Park report sha256 | `5eb4309096a8377943799b7cc164cbbb13a86f327a813520255d0fa3b3e00263` |
| Park report seal | `e7f3fce5239d18f7cff78ddda81dde060b6842c54ddb1fdba95bfdcd584eb326` |
| Park report MD | `reports/s7_d1_cross_asset_donchian_yfinance_proxy_park_report.md` |
| Park commit | `a5ac092` |
| Lesson append commit | `c6730d2` |
| Terminal verdict | `REJECT_FAST` |
| Active K-path | `K12` (DR2 fired + DR3 fired on the cost-stress matrix); `K4` trade-curve MaxDD > 50% also fired; `K9` sample size below 100 (37 trades) also fired |
| S1 net PnL on $100k | +$589.59 |
| Trade-curve MaxDD | 69.10% |
| Total closed trades | 37 |
| Per-symbol PnL pattern | SPY net negative (~-$45k); TLT net negative (~-$8k); GLD net negative (~-$43k); USO net positive (~+$96k); USO-only carries the portfolio |
| Diversification | `effective_independent_bets = 3.5585`; `avg_pairwise_dependence = 0.0414` |

### 3.2 Prior P2 -- s9 RSI-2 cross-asset mean-reversion

| Field | Value |
|---|---|
| `candidate_record_id` | `s9-cross-asset-mean-reversion-rsi2-spy-tlt-gld-uso-yfinance-proxy` |
| Mechanic family | mean-reversion (RSI(2) < 10 entry / RSI(2) > 50 exit; Connors canonical; no filter, no regime gate, no asset selection) |
| Park report path | `reports/s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_park_report.json` |
| Park report sha256 | `cefa80e7b4c2e73f66d5ff4aad37bcb329247e7f16691f92b6d3b748666542c3` |
| Park report seal | `026595ed2b1d81589d5a946bd0fd897e182736b75c15ce8a0c3e9f0d585b94c7` |
| Park report MD | `reports/s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_park_report.md` |
| Park report MD sha256 | `7c2128b5faf1b872e0ac34d6050e60ab5ae64c90d5feb6eaedd1454ad6173b18` |
| IS decision memo path | `reports/s9_cross_asset_mean_reversion_rsi2_is_decision_memo.json` |
| IS decision memo sha256 | `30da17f4d9f04a07a36e5300df38f75ae111ba2c9dc15efa5f73ea7c660d8e71` |
| Park commit | `9cf2f56` |
| Lesson append commit | `efa3076` |
| Terminal verdict | `PARKED_SAFE_BUT_NOT_MONEY_PROVEN` |
| Active K-path | `K1` (Sharpe proxy per trade < 0) AND `K2` (expectancy per trade <= 0) at S1 baseline |
| S0 net PnL | -$1211.03 (negative even at zero slippage and zero commission) |
| S1 net PnL | -$1334.87 |
| S2 net PnL | -$1578.44 |
| S3 net PnL | -$1825.78 |
| Cost-stress | negative at all four tiers; cost amplifies the loss but does not cause it |
| Sharpe proxy per trade S1 | -0.097135 |
| Expectancy per trade S1 | -$3.224 |
| Portfolio WR S1 | 53.14% vs implied breakeven 62.44% -> gap -9.30 pp |
| Trade-curve MaxDD | 1.64% (clears K4 comfortably -> the SAFE part of the verdict) |
| Total closed trades | 414 (clears K9 comfortably) |
| Per-symbol PnL pattern | SPY +$140; GLD -$194; TLT -$104; USO -$1177; USO carries the loss |
| Diversification | `effective_independent_bets = 3.5585`; `avg_pairwise_dependence = 0.0414` |

## 4. Cumulative family-level finding

The two priors are STRUCTURALLY ORTHOGONAL in mechanic family:

- P1 is a low-frequency trend-following mechanic with pyramid amplification. Its failure mode is `K12` cost-stress sensitivity (DR2+DR3) combined with insufficient trade count (`K9`) and excessive drawdown (`K4`). Edge at S0 was positive (+$589) but cost-fragile.
- P2 is a high-frequency mean-reversion mechanic with no pyramid. Its failure mode is `K1` + `K2` negative edge at S0 baseline. Edge at S0 was negative (-$1211) and cost only amplifies the loss.

These two failure modes are on opposite ends of the cost-stress / trade-frequency spectrum:

| Axis | P1 (s7 D1 trend) | P2 (s9 RSI-2 mean-reversion) |
|---|---|---|
| Trade count over IS | 37 (insufficient) | 414 (ample) |
| Edge at S0 | +$589.59 (positive) | -$1211.03 (negative) |
| Failure mode | Cost-stress sensitivity destroys an S0 edge | Negative edge even before cost |
| MaxDD | 69.10% (excessive) | 1.64% (safe) |
| Per-symbol concentration | USO carries +$96k profit | USO carries -$1177 loss |
| Diversification (eff_indep_bets) | 3.5585 | 3.5585 |
| Diversification (avg_pairwise_dep) | 0.0414 | 0.0414 |

The cumulative finding is:

> **On the SPY/TLT/GLD/USO universe over the 2014-2022 in-sample window, two structurally orthogonal mechanic families (trend-following and mean-reversion) at canonical parameters with realistic ETF-proxy costs both empirically failed to demonstrate a money-proven edge.** The validated diversification structure of this universe (`effective_independent_bets ~ 3.56`; `avg_pairwise_dependence ~ 0.041`) is genuine, mechanic-agnostic, and re-usable, but it does NOT rescue a negative or cost-fragile edge. Diversification independence is orthogonal to edge presence; the s9 result is the load-bearing demonstration of this principle.

## 5. Family-level park rule

For the SPY/TLT/GLD/USO 2014-2022 ETF-proxy universe at canonical mechanic parameters, the following rule is established:

**No further mechanic-variant candidates on this universe shall be authorized without first-principles burden satisfaction.**

A candidate satisfies the first-principles burden iff it explicitly states (in its Tier-N spec at locking time) BOTH:

R5_AB_a. WHY its mechanic is structurally different from BOTH P1 (trend-following) AND P2 (mean-reversion); AND

R5_AB_b. WHY it might survive where P1 failed on cost-stress sensitivity AND where P2 failed on negative S0 edge.

A candidate that addresses only ONE of these two failure modes does NOT satisfy the burden. A candidate that rebadges either P1 or P2 with relaxed thresholds does NOT satisfy the burden. A candidate that depends on diversification "rescuing" a negative edge does NOT satisfy the burden.

The rule is enforced by the next-research-track selection plan's section 6 reject-fast criterion `R8` (track operates on a universe known to be empirically falsified by at least two orthogonal-mechanic priors without a fundamentally new mechanic that explicitly addresses BOTH prior failure modes).

## 6. Related candidate evidence (single-instrument SPY context; informational)

Two SPY-only single-instrument candidates from the B006_NNN lineage are relevant context for the universe-level finding. They are NOT direct evidence for the multi-asset universe park (different scope) but they are evidence the SPY signal alone does not carry a money-proven edge under vol-targeting either.

### 6.1 B006_001 SPY vol-targeting

| Field | Value |
|---|---|
| `candidate_id` | `B006_001_SPY_VOL_TARGETING` |
| Mechanic | single-instrument SPY long with realized-vol sizing at 10% target |
| Final sealed verdict | `REQUEST_FULL_PREREGISTRATION_REVIEW` (archived without live unlock; no FRC; no promotion) |
| Lesson references | `LESSON_B006_001_002` (warmup guard) + `LESSON_B006_001_003` (DR6 narrowing) + `LESSON_B006_001_004` (runner enforcement of textual preconditions) |

### 6.2 B006_002 SPY vol-targeting C4-enforced

| Field | Value |
|---|---|
| `candidate_id` | `B006_002_SPY_VOL_TARGETING_C4_ENFORCED` |
| Mechanic | same B006_001 strategy + warmup guard + DR6 post-warmup narrowing + DR11 C4 enforcement at precedence position 3 |
| Final sealed verdict | `REJECT_FAST` (DR11 fired; leverage-cap-bound rate 15.625% > 0.10 threshold) |
| Lesson references | `LESSON_B006_002_001` (runner-enforced preconditions actually fire when calibrated) + `LESSON_B006_002_002` (favorable numbers do not override fail-closed verdicts) |

Note: these two candidates are SPY-only single-instrument vol-targeting, not multi-asset trend or mean-reversion. They are informational and do NOT extend the universe-level park to vol-targeting on the multi-asset basket -- such an extension would require its own diagnostic prior. They ARE evidence that the SPY signal alone has been subjected to multiple sealed disciplines and produced (a) a favorable-but-archived verdict at B006_001 and (b) a fail-closed verdict at B006_002, neither of which unlocks live.

## 7. What this memo does NOT do

| Action | Performed? |
|---|---|
| Modify any sealed prior artifact | NO |
| Author or modify strategy code | NO |
| Run any backtest or simulator | NO |
| Compute any signal | NO |
| Fetch any data | NO |
| Call yfinance / Yahoo Finance | NO |
| Call Databento | NO |
| Access DATABENTO_API_KEY | NO |
| Authorize live trading | NO |
| Grant FRC | NO |
| Promote any candidate | NO |
| Mutate `review_queue.json` | NO |
| Mutate production `idea_memory` | NO |
| Modify `brain_memory/projects/trading_bot/lessons.md` (dirty + unstaged; left untouched) | NO |
| Modify or stage anything outside the three planning artifacts named in the authorization | NO |
| Recommend a "third try" on this universe | NO (the memo explicitly establishes the first-principles burden for any such candidate) |

## 8. Permanent labels for this universe

| Label | Value |
|---|---|
| `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` | TRUE for any candidate operating on the SPY/TLT/GLD/USO 2014-2022 ETF-proxy universe at canonical parameters |
| `FAMILY_LEVEL_PARK_TWO_ORTHOGONAL_MECHANICS_FAILED` | TRUE |
| `DIVERSIFICATION_HOLDS_BUT_DOES_NOT_RESCUE_EDGE` | TRUE |
| `FIRST_PRINCIPLES_BURDEN_REQUIRED_FOR_THIRD_MECHANIC_CANDIDATE` | TRUE |
| `LIVE_TRADING_BLOCKED` | TRUE (independent of any future verdict on this universe) |
| `STRATEGY_LAB_PROMOTION_BLOCKED` | TRUE |
| `BROKER_INTEGRATION_BLOCKED` | TRUE |
| `OOS_BLOCKED` | TRUE (no prior reached ELIGIBLE_FOR_OOS) |
| `DO_NOT_RESCUE_S7_D1_SPEC` | TRUE (inherited from s7 D1 park report) |
| `DO_NOT_ITERATE_S9_PARAMETERS_WITHOUT_REVN_SPEC` | TRUE (inherited from s9 park report) |
| `DO_NOT_LOOSEN_K_THRESHOLDS_OR_A_GATE_THRESHOLDS_RETROACTIVELY` | TRUE |

## 9. Files written this memo turn

| File | Purpose |
|---|---|
| `reports/external_research_hunter/t8_spy_tlt_gld_uso_2014_2022_family_park_memo.md` | This record-only family-level park memo (Markdown body) |
| `reports/external_research_hunter/t8_spy_tlt_gld_uso_2014_2022_family_park_memo.json` | Companion JSON (machine-readable; embeds `report_seal_sha256` over canonical body) |
| `docs/s10_d1_mnq_mgc_databento_long_history_tier_n_spec_plan.md` | T7-Path-A Tier-N spec plan (sibling file authored in the same controller turn) |

The brain_memory `lessons.md` dirty state from prior controller-session appends (LESSON_B006_002_001 / LESSON_B006_002_002 at lines 4356+) is LEFT UNSTAGED AND UNMODIFIED by this memo. No other repository file is modified.

## 10. Status carried forward

| Field | Value |
|---|---|
| Trading | `PAUSED` |
| Live mode | `BLOCKED_AT_6_GATES` |
| FRC | `NEVER_GRANTED` |
| `no_strategy_optimization_authorized` | TRUE |
| `no_live_trading` | TRUE |
| `no_strategy_lab_promotion` | TRUE |
| `no_brokerage_connection` | TRUE |
| `no_external_network` | TRUE |
| `no_databento` (this turn) | TRUE |
| `no_review_queue_mutation` | TRUE |
| `no_production_idea_memory_mutation` | TRUE |
| `no_profitability_claim` | TRUE |

## 11. Next-step authorization scope

This memo does NOT authorize any next step on the SPY/TLT/GLD/USO universe (the universe is family-level parked). A future authorization on a different universe (e.g., the T7-Path-A Databento MNQ+MGC futures track plan authored alongside this memo, or any T4/T5/T6 option from the selection plan section 14) is required to advance any further research track.

Authorization paths available after this memo:

- **Build the T7-Path-A Databento MNQ+MGC long-history Tier-N spec** (under `Authorize T7-Path-A Databento MNQ+MGC long-history Tier-N specification plan SEAL only` or equivalent operator-typed scope): would build on top of `docs/s10_d1_mnq_mgc_databento_long_history_tier_n_spec_plan.md` (the sibling plan file authored in this same turn).
- **Stay at family-level park only**: no further track opened; trading-bot research arc pauses. Available as default if the operator chooses to consolidate without extending.
- **Pivot to a different universe entirely (T4 sector ETFs / T5 international / T6 single-name equities)**: requires a fresh selection-plan revision or out-of-band justification per section 21 of `docs/next_research_track_selection_plan_after_s9_park.md`.

This memo is the source of truth for the family-level park finding on SPY/TLT/GLD/USO 2014-2022. Future memos that contradict it require an explicit out-of-band justification.

----

End of memo. Record-only family-level park memo. No code. No backtest. No simulator. No signal. No data fetch. No yfinance. No Yahoo Finance. No Databento. No DATABENTO_API_KEY access. No brokerage. No real order. No paper order. No Strategy Lab promotion. No review_queue mutation. No production idea_memory mutation. No ORB branch mutation. No lessons.md modification or staging. No live trading. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES.
