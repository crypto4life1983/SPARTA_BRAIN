# S10-D2 P7 decision memo (sealed)

**Candidate:** `s10-cross-asset-donchian-no-pyramid-reparam-cap-nq-gc-zn-cl`
**Phase prefix:** `PHASE2-S10-D2-XAD-RC`
**Authored (UTC):** `2026-05-27T03:04:28.767045Z`
**Recommended next phase:** **ADVANCE_TO_P10_OOS_GATE**
**Report seal sha256:** `87baa6e8c4cc1eb47c1345b97990eab86d5cefb37636e9fe57a029506d398c05`

## Executive decision

Advance S10-D2 to the P10 OOS gate as the next research action. P6 IS produced a clean READY_FOR_LONGER_BACKTEST verdict (200 closed trades, 0 safety counters firing, 0 K-gates fired, no-pyramid invariant held, A1..A10 evaluated gates passing). P6.5 cost-stress matrix produced a clean READY_FOR_NEXT_PHASE verdict (A8 PASS, K12 not fired, 0 DR fires across all 4 non-baseline tiers S0/S2/S3/S4; monotonic PnL degradation S0->S4 as expected; closed trade count invariant at 200 across all 5 tiers). The IS layer of the lifecycle is complete. The next phase that produces new evidence about whether the strategy generalizes is the OOS gate, which is a research truth-test, NOT an approval to trade.

## Evidence summary — P6 IS (seal `e6cdc7c68a9e2b7b...`)

| Metric | Value |
|---|---|
| Verdict | **READY_FOR_LONGER_BACKTEST** |
| Starting cash | $500,000 |
| Final equity | $1,473,097.86 |
| Net PnL | +$973,097.86 |
| Closed trades | 200 (vs K9 threshold 100) |
| Wins / Losses | 70 / 130 |
| Win rate | 35.00% (vs breakeven 24.52%; gap +10.48 pp) |
| Expectancy / trade | +$4865.49 |
| PL ratio | 3.0781 |
| Sharpe proxy / trade | 0.143112 |
| Trade curve max DD | -28.3060% / $-141,529.98 |
| Long / Short PnL | +$458,468.05 / +$514,629.81 |
| Safety counters all zero | **True** |
| No-pyramid invariant held | **True** (max units observed: 1) |
| K-gates fired | 0 |
| Trading days in union | 2574 |

**Per-market PnL (P6 baseline S1):**

| Market | Trades | Net PnL | Win rate |
|---|---:|---:|---:|
| `CL` | 49 | $422,894.55 | 38.78% |
| `GC` | 49 | $-345.01 | 28.57% |
| `NQ` | 54 | $126,607.39 | 35.19% |
| `ZN` | 48 | $423,940.93 | 37.50% |

## Evidence summary — P6.5 cost-stress matrix (seal `f9a34674de4f7fdf...`)

**Matrix verdict:** **READY_FOR_NEXT_PHASE**
**Total DR fires (S0/S2/S3/S4):** 0
**K12_DR_fires_on_cost_stress:** not_fired
**A8_cost_stress_S0_S4_run:** **PASS**

| Tier | Net PnL | Closed trades | Expectancy | Sharpe | Max DD % | DR fires |
|---|---:|---:|---:|---:|---:|---|
| `S0` | $987,241.79 | 200 | $4,936.21 | 0.1450 | -27.9740% | none |
| `S1` | $973,097.86 | 200 | $4,865.49 | 0.1431 | -28.3060% | none |
| `S2` | $913,849.33 | 200 | $4,569.25 | 0.1400 | -29.7591% | none |
| `S3` | $824,422.94 | 200 | $4,122.11 | 0.1300 | -30.3483% | none |
| `S4` | $567,872.41 | 200 | $2,839.36 | 0.1056 | -36.9263% | none |

**Closed trade count is invariant at 200 across all 5 tiers** — entry signal is identical; only cost frictions differ. Monotonic PnL degradation S0 → S4 as expected. All 5 tiers held safety counters at zero, no-pyramid invariant held, and starting_cash invariant held.

## Risk interpretation

**Drawdown envelope under cost stress:**

- S0: trade-curve max DD = -27.9740%
- S1: trade-curve max DD = -28.3060%
- S2: trade-curve max DD = -29.7591%
- S3: trade-curve max DD = -30.3483%
- S4: trade-curve max DD = -36.9263%

S4 (adversarial cost tier) max DD = -36.93%, still well below the K4 threshold of -50%.

**Concentration risk:**

- CL (+$422,895) and ZN (+$423,941) each contributed ~43.5% of total IS net PnL.
- NQ contributed +$126,607 (~13%).
- **GC contributed -$345 (essentially flat over 10 years / 49 trades)** — diversification value but near-zero realized return on its own.
- If GC is removed, the strategy edge concentrates in CL/ZN, which has implications for OOS robustness (if either CL or ZN regime changes, the strategy may lose half its IS edge).

**Long vs. short balance:**

- 111 long / 89 short over 10y IS.
- Long PnL +$458,468.05, Short PnL +$514,629.81.
- Short side contributes ~53% of net PnL — the strategy is genuinely bi-directional in its IS realization, not just a long-bias dressed up as Donchian.

**Unobserved risks (from chain context, NOT from these IS reports):**

- Out-of-sample generalization (2023+).
- Regime-specific behavior (rate hikes, vol spikes, exchange holiday quirks not in IS window).
- Live execution friction beyond the modeled cost-stress envelope.
- Concurrent risk to correlated positions (cross-market correlation effects under stress).

## Cost / friction interpretation

Each tier step S0->S1->S2->S3->S4 erodes net PnL by approximately ~$14k, ~$59k, ~$89k, and ~$257k respectively (cumulative). The S4 result of +$568k on $500k starting cash is the most conservative cost-modeled IS outcome and still cleared DR2..DR5.

**Frictions modeled in P6/P6.5:**

- commission
- fees
- slippage_ticks (entry/stop/exit) scaled by tick_value

**Frictions NOT modeled in P6/P6.5:**

- Liquidity impact on large orders (sizing is 1% portfolio per unit; small enough that point-tick slippage is generally a reasonable proxy).
- Exchange outage / circuit breaker behavior.
- Margin call cascades during stress events.
- Roll execution slippage beyond the +1 spread tick model.
- Funding/borrowing cost asymmetry for shorts.

**What the P6.5 cost-stress passes do NOT say:**

These cost-stress results are model-level frictions applied to historical IS data. They do NOT model live broker-level execution variance, exchange-level idiosyncrasies, or stress regime conditions that may exist outside the 2013-2022 window. Live frictions can exceed the S4 model.

## Why this is ready for OOS

**Ready:** **YES** (subject to conservative interpretation below).

**Reasons ready:**

- P6 IS produced READY_FOR_LONGER_BACKTEST with 0 K-gates fired and all evaluated A-gates passing.
- Closed trade count (200) is 2x the K9 threshold (100) - the sample is structurally sufficient for the per-trade-statistics gates that apply at this stage.
- All safety counters held zero in P6 IS AND in all 4 P6.5 non-baseline tiers (no cap binding, no N-drift, no non-RTH fills, no rollover violations, no stale fills, no unsupported order types, no pyramid state machine violations, no per-market unit invariant violations).
- No-pyramid invariant (max_units_per_market=1) held across all 5 tiers; second_unit_add_attempt_count=0.
- starting_cash invariant ($500,000) held across all 5 tiers (S-STOP-14 not fired).
- P6.5 cost-stress sweep cleared A8 with K12 not fired; even adversarial S4 tier remained profitable, positive-expectancy, positive-sharpe, and above the trade-count floor.
- Inherited seal chain (Tier-N -> P1 -> P2 -> P3 -> P3.5 -> P4 -> P6 -> P6.5) is intact and verified at each step; assert_seal_inheritance() passed at every P6/P6.5 invocation.

**What this does NOT mean (read carefully):**

- IS results do not generalize automatically to OOS.
- Cost-stress matrix passes do not imply live execution will match modeled frictions.
- K-gate / A-gate / DR-rule passes are necessary but not sufficient for live promotion.
- Live promotion path remains BLOCKED_AT_6_GATES permanently regardless of OOS outcome (per phase-2 plan; this is a research lifecycle, not a deployment lifecycle).
- No statement about future P&L is implied by these results.
- OOS is the next truth-test; it has the power to invalidate the IS conclusion. Approaching OOS with the expectation that it MIGHT fail is the correct stance.

## Recommended next phase

**ADVANCE_TO_P10_OOS_GATE** — Advance to P10 OOS gate.

P10 OOS is the next research truth-test. It executes the same locked S10-D2 harness against the 144-file OOS window (2023+) currently sequestered at `data/databento_cache_oos/` per parallel-session commit `1ddf441`. P10 has the structural power to invalidate the IS conclusion (e.g., regime change, microstructure shift, dataset error, etc.) — that possibility is the entire point of OOS, and approaching P10 with the expectation that it MIGHT fail is the correct epistemological stance for a research lifecycle.

P10 is NOT an approval to trade. It is a research diagnostic. The 6-gate live-block remains permanent regardless of any OOS outcome.

## Explicit blocked actions

- DO NOT advance to live trading.
- DO NOT advance to paper trading via broker connection.
- DO NOT modify any sealed Tier-N / plan-lock / phase-2 / P3 / P3.5 / P4 / P6 / P6.5 file.
- DO NOT revisit the OOS window (2023+) before a separate AUTHORIZE S10-D2 P10 OOS gate turn is issued.
- DO NOT relax any K-gate / A-gate / DR threshold to make a future verdict cleaner.
- DO NOT change the candidate_record_id, starting_cash, max_units_per_market, AMB6 filter, Donchian 55/20, Wilder ATR(20), 2N stop, or 1% risk sizing.
- DO NOT revive S8-D1, S7-D1, D5, B005_001, or NKE.
- DO NOT make any profitability claim outside this conservative diagnostic framing.
- DO NOT touch obsidian-trade-logger.
- DO NOT mutate review_queue.json.
- DO NOT fetch or call Databento or QuantConnect or any broker/exchange/wallet API.

## Seal metadata

- Report seal sha256: `87baa6e8c4cc1eb47c1345b97990eab86d5cefb37636e9fe57a029506d398c05`
- Seal method: LESSON_HUNTER_004 canonical roundtrip (json.dumps sort_keys=True, separators=',:', ensure_ascii=False, default=str EXCLUDING report_seal_sha256 + seal_method)
- Reseal verified on disk: YES

**Inherited seals:**

- `tier_n_spec_seal_sha256`: `f5ca5ee63024e9c8b7b1e85762558ec35eb3d4ebb9ce2a160cbe0f1a0e80a679`
- `plan_lock_seal_sha256`: `ba8bf954d44b373c0ffdc38a1cf8f73dec31a9fc538f0b7584a20659d79ea354`
- `phase2_plan_seal_sha256`: `7a48ad64236971e6fd2a2fa58ab7ab746a71543778ed0a868f3cdf9ff8f74ac3`
- `p3_build_runner_report_seal_sha256`: `1eb04aa312f4053134c1e9387be7716aa4564c019168ee2cedcf789063d96405`
- `p3_build_in_sample_driver_report_seal_sha256`: `ddd604c96508a0ab835bcbae6e72fabc2993cd3f0dc459898ca326617dd96443`
- `p3_5_scaffold_completion_seal_sha256`: `66d38f359b54882b3107c4ad4291673d63f05f5b0d3daa19088b4a4c76469261`
- `p4_smoke_seal_sha256`: `c31ded81f9a2883586883aadda4d64d629a047917fcebd56169ca42eccf4fdde`
- `p6_is_diagnostic_seal_sha256`: `e6cdc7c68a9e2b7b6d749b73ff433e585c9de55890af5dce3dca51d74430c1b8`
- `p6_5_cost_stress_matrix_seal_sha256`: `f9a34674de4f7fdf8098b39959032d152bf2282e9ad57cedd68bc33cee2099ab`

## Commit candidate summary

**Files authorized by operator (exactly 2):**

- `reports/s10_d2_p7_decision_memo_sealed.json`
- `reports/s10_d2_p7_decision_memo_sealed.md`

**Commit subject:** `Seal S10-D2 P7 decision memo`

**Files explicitly NOT to be staged:**

- brain_memory/projects/trading_bot/lessons.md (long-running parallel-session dirty file; not mine)
- any other unrelated tracked file (none of which are mine)

**Pathspec commit mode required:** YES

**Verification before commit:** `git status --short -uall` must show ONLY the 2 new authorized files staged (no other staged paths).

## Hard boundaries held (this memo authoring turn)

- no_backtest: True
- no_broker_adapter_touched: True
- no_commit_in_orchestrator: True
- no_d5_b005_001_nke_revival: True
- no_data_fetch: True
- no_databento_api_call: True
- no_db_historical: True
- no_lessons_md_touched: True
- no_live_trading: True
- no_network_call: True
- no_obsidian_touched: True
- no_oos_inspection: True
- no_paper_trading: True
- no_profitability_claim: True
- no_promotion_to_live: True
- no_qc_runtime: True
- no_review_queue_mutation: True
- no_scheduler_change: True
- no_source_modification: True
- no_strategy_execution: True
- no_unrelated_tracked_file_modified: True
