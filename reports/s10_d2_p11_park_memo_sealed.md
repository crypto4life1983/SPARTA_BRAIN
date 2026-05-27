# S10-D2 P11 PARK memo (sealed)

**Candidate:** `s10-cross-asset-donchian-no-pyramid-reparam-cap-nq-gc-zn-cl`
**Phase prefix:** `PHASE2-S10-D2-XAD-RC`
**Authored (UTC):** `2026-05-27T03:45:29.410279Z`
**Park status:** **PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED**
**Report seal sha256:** `e121b82b411697c7d06bbe9ee1cc2df29c04df76712873ed0fbfd76f25fab1cb`

## Executive park decision

S10-D2 (cross-asset Donchian no-pyramid reparam-cap NQ+GC+ZN+CL at $500,000 starting cash) is PARKED under PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED. The full chain passed cleanly through P6 IS (READY_FOR_LONGER_BACKTEST; 200 closed trades; all safety counters zero), P6.5 cost-stress matrix (READY_FOR_NEXT_PHASE; A8 PASS; K12 not fired; 0 DR fires across S0/S2/S3/S4), and P7 decision memo (ADVANCE_TO_P10_OOS_GATE). At P10 OOS, the candidate produced a directionally-consistent result (positive sharpe, expectancy, net PnL; all safety counters zero; max DD actually improved vs IS) but K9 fired because closed_trades=53 over the 3-year OOS window is below the 100-trade threshold required to statistically confirm the IS edge. The C7 verdict was INSUFFICIENT_SAMPLE; the OOS qualitative verdict was OOS_INDETERMINATE_BUT_DIRECTIONALLY_CONSISTENT. This is neither a confirmation nor a refutation — it is an absence of refutation under a structurally small sample. The conservative lifecycle action is PARK: do not promote, do not kill, do not re-tune.

## Park status decision logic

- P6 IS was clean enough to advance to cost-stress: 200 trades, all safety zero, 0 K-gates fired, all A-gates passed.
- P6.5 cost-stress matrix was clean enough to advance to OOS: matrix verdict READY_FOR_NEXT_PHASE; A8 PASS; K12 not fired; 0 DR fires.
- P7 correctly advanced to OOS gate as the next research truth-test.
- P10 OOS produced directionally-consistent metrics but K9 fired (closed_trades=53 < 100 threshold).
- Safety counters remained zero across IS + 5 cost tiers + OOS. No-pyramid invariant held everywhere. Starting cash invariant held.
- OOS sample was structurally limited by the available 3-year OOS window vs the 10-year IS window — this is a function of available history, not a function of the strategy.
- Positive OOS direction is encouraging but is NOT proof.
- Therefore the conservative lifecycle decision is PARK — not ADVANCE, not KILL, not PROMOTE.

## Chain evidence summary

| Phase | Verdict | Closed trades | Net PnL | Expectancy | Sharpe | MaxDD% | Safety zero | Seal |
|---|---|---:|---:|---:|---:|---:|:-:|---|
| **P6 IS** | READY_FOR_LONGER_BACKTEST | 200 | $973,098 | $4,865 | 0.1431 | -28.31% | True | `e6cdc7c68a9e2b7b...` |
| **P6.5 matrix** | READY_FOR_NEXT_PHASE (A8=PASS; K12=not_fired; DR=0) | — | — | — | — | — | — | `f9a34674de4f7fdf...` |
| **P7 decision** | ADVANCE_TO_P10_OOS_GATE | — | — | — | — | — | — | `87baa6e8c4cc1eb4...` |
| **P10 OOS** | C7=INSUFFICIENT_SAMPLE / qual=OOS_INDETERMINATE_BUT_DIRECTIONALLY_CONSISTENT | 53 | $113,450 | $2,141 | 0.1005 | -12.96% | True | `4038e5334feba9ea...` |

## P6.5 per-tier cost-stress carry-over (all 5 tiers; 0 DR fires)

| Tier | Source | Net PnL | Closed trades | Expectancy | Sharpe | MaxDD% | DR fires |
|---|---|---:|---:|---:|---:|---:|---|
| `S0` | EXECUTED_THIS_TURN_V2_RERUN | $987,242 | 200 | $4,936 | 0.1450 | -27.97% | none |
| `S1` | BASELINE_READ_FROM_P6_SEAL | $973,098 | 200 | $4,865 | 0.1431 | -28.31% | none |
| `S2` | EXECUTED_THIS_TURN_V2_RERUN | $913,849 | 200 | $4,569 | 0.1400 | -29.76% | none |
| `S3` | EXECUTED_THIS_TURN_V2_RERUN | $824,423 | 200 | $4,122 | 0.1300 | -30.35% | none |
| `S4` | EXECUTED_THIS_TURN_V2_RERUN | $567,872 | 200 | $2,839 | 0.1056 | -36.93% | none |

## OOS vs IS comparison

- IS window: ['2013-01-01', '2022-12-30'] (10 years)
- OOS window: ['2023-01-01', '2025-12-31'] (3 years)
- Ratios: {'expectancy_ratio': 0.4399500701337249, 'sharpe_ratio': 0.7023196897331654, 'trades_per_year_oos_vs_is': 0.8833333333333334}

### What survived

- Direction of edge (positive sharpe, expectancy, net PnL).
- All safety counters held zero across IS + 5 cost tiers + OOS.
- No-pyramid invariant held across all phases.
- Starting cash invariant ($500,000) held across all phases.
- Trade frequency roughly consistent (17.7 OOS/year vs 20 IS/year ≈ 0.88x).
- Max drawdown actually improved (OOS -12.96% vs IS -28.31%).

### What degraded

- Per-trade expectancy: OOS ~0.44x of IS magnitude.
- Per-trade sharpe proxy: OOS ~0.70x of IS magnitude.
- Net PnL per year: OOS ~0.39x of IS magnitude.
- Closed-trade count: 53 vs 200, leaving sample below K9 threshold of 100.

### Interpretation

The OOS edge appears to have survived in direction but degraded in magnitude. Whether the magnitude degradation reflects regime shift, sample noise, or true edge decay is INDETERMINATE from a 3-year OOS window with 53 closed trades. The conservative reading is that the strategy did not refute itself but also did not statistically confirm itself.

## Why PARK, not ADVANCE

- OOS closed-trade count (53) is below K9 threshold of 100. A1 acceptance gate FAILED.
- Advancing to live/paper promotion paths is permanently blocked at 6 gates regardless.
- Advancing to P10.5 / P11.5 / similar would require a fresh sealed authorization with a documented research hypothesis (e.g., longer OOS window, cost-stress OOS).
- The chain-of-custody framework is explicit: lacking statistical confirmation is not a basis for advancement.

## Why PARK, not KILL

- Safety counters held zero across IS + 5 cost tiers + OOS — no safety K-gate fired.
- Performance K-gates K1/K2/K4 did NOT fire on OOS (sharpe>0, expectancy>0, |maxdd|<50%).
- OOS direction is consistent with IS edge; magnitude degraded but stayed positive.
- Killing the candidate would discard usable evidence — the chain ran cleanly and produced an interpretable INDETERMINATE result.
- PARK preserves the chain artifacts for future cross-reference and successor design.

## Comparison vs s8-D1 PARK precedent

- s8-D1 park status: **PARKED_SAFE_BUT_NOT_MONEY_PROVEN_OOS_SIZING_UNDERSIZED** (commit `6e7b491`)
- s8-D1 binding reason: Capital-vs-contract-size mismatch in OOS: at $100k starting cash with full-size futures contracts, sizing produced 0 contracts for most signals, making OOS structurally undersized.
- s10-D2 binding reason: OOS sample insufficient (K9 fired at 53 < 100 trades over 3 years). S10-D2 explicitly raised starting cash to $500,000 to address the s8-D1 sizing problem; that fix succeeded (OOS trade frequency consistent with IS), but the OOS WINDOW LENGTH itself was the binding constraint, not sizing.

### Common lesson

- Both candidates produced clean IS verdicts.
- Both candidates were directionally consistent in OOS.
- Both candidates parked under different binding-constraint roots.
- Both candidates explicitly remained BLOCKED_AT_6_GATES with respect to live promotion.
- Neither candidate produced a 'profitable proven' claim.

### Difference between the two parks

s8-D1 parked due to capital-sizing structural under-allocation. S10-D2 parked due to sample-size structural insufficiency on a 3-year OOS window. The S10-D2 sizing fix succeeded in producing comparable per-year trade density; what S10-D2 needed and did not have was a longer OOS window (more market history).

## What the park means

- S10-D2 has been carefully and conservatively evaluated through the full sealed IS + cost-stress + OOS lifecycle.
- All safety guards held throughout; no safety K-gate fired anywhere.
- The candidate is intellectually 'still alive' in the sense that no evidence has refuted the IS-derived hypothesis — but the OOS evidence is not statistically sufficient to confirm it.
- The PARK preserves all sealed artifacts (10 commits across the chain) for future reference, comparison, or successor candidate design.
- Any future continuation must come through a separate fresh sealed authorization.

## What the park does NOT mean

- Does NOT mean the strategy is live-ready or paper-ready.
- Does NOT mean OOS results 'confirm' the IS edge.
- Does NOT mean future P&L will resemble IS or OOS P&L.
- Does NOT mean threshold loosening or re-tuning is in scope.
- Does NOT mean any successor candidate (S11-D1, longer OOS, OOS cost-stress, fresh candidate) is pre-approved.
- Does NOT lift the permanent 6-gate live-block.
- Does NOT promote this candidate beyond research-diagnostic status.
- Does NOT make any profitability claim.
- Does NOT shorten any future research-validation requirement.

## Explicit blocked actions

- DO NOT advance S10-D2 to live trading.
- DO NOT advance S10-D2 to paper trading via broker connection.
- DO NOT modify any sealed Tier-N / plan-lock / phase-2 / P3 / P3.5 / P3.6 / P4 / P6 / P6.5 / P7 / P10 file.
- DO NOT modify in_sample_driver.py, out_of_sample_driver.py, main.py, execution_guard.py, or any other S10-D2 source file in response to this PARK decision.
- DO NOT change Donchian periods, ATR multiplier, risk %, max_units, AMB6 filter, starting_cash, cost-tier definitions, or any other strategy parameter to make a future verdict cleaner.
- DO NOT relax K9 threshold to 'confirm' OOS.
- DO NOT re-run OOS with different parameters or different cost tiers without a fresh sealed authorization that documents the research hypothesis.
- DO NOT pre-emptively author S11-D1 Tier-N specification without a separate operator authorization.
- DO NOT make any profitability claim outside this conservative PARK framing.
- DO NOT touch obsidian-trade-logger.
- DO NOT mutate review_queue.json.
- DO NOT touch brain_memory/projects/trading_bot/lessons.md.
- DO NOT revive S8-D1, S7-D1, D5, B005_001, or NKE in response to this PARK.
- DO NOT call Databento API, QuantConnect, or any broker/exchange/wallet API in response to this PARK.

## Future research options (NOT pre-approved)

**All four options below require separate fresh sealed authorization. None is pre-approved by this memo.**

### Option 1 S11 D1 Mnq C 0 Single Instrument Fallback

Switch research focus to the parallel-session S11-D1 MNQ.c.0 single-instrument selection plan (committed at 556ab3f). A single-instrument design may produce different OOS trade-density dynamics worth investigating.

**Prerequisites for authorization:**
- Operator review of the S11-D1 selection plan at commit 556ab3f.
- Fresh AUTHORIZE S11-D1 Tier-N specification turn with full enumerated scope.

- Preserves S10-D2 sealed chain: **True**

### Option 2 Longer Oos Window

Wait for additional months of OOS market data (e.g., 2026+ as it becomes available) and re-attempt the OOS gate with a larger sample. Could push closed-trade count above the K9 threshold of 100 by extending the window.

**Prerequisites for authorization:**
- Wait for sufficient additional OOS history to accumulate.
- Fresh AUTHORIZE turn for a sealed Databento fetch extension (OOS-only).
- Fresh AUTHORIZE S10-D2 P10-rerun turn after the extended OOS cache is sealed.

- Preserves S10-D2 sealed chain: **True**

### Option 3 Oos Cost Stress Sweep

Run cost-stress matrix S0/S1/S2/S3/S4 against OOS data (analog of P6.5 but on OOS instead of IS). Would test robustness of the OOS result under cost variation. Same K9 sample-size constraint would still apply to each tier.

**Prerequisites for authorization:**
- Fresh AUTHORIZE turn explicitly framing OOS cost-stress as a research diagnostic (not as a re-evaluation of the OOS verdict).
- Expected ~80s per tier x 4 non-baseline tiers + S1 baseline = ~6-7 min wall.

- Preserves S10-D2 sealed chain: **True**

### Option 4 Fresh Candidate Different Markets Or Regime Overlay

Author a fresh candidate (different candidate_record_id) with different market selection, regime overlay, or signal design. Treat S10-D2 lessons as inputs to the design but do not modify S10-D2 itself.

**Prerequisites for authorization:**
- Fresh AUTHORIZE Tier-N specification for the new candidate with full enumerated scope.
- S10-D2 sealed chain remains as the parent / predecessor reference.

- Preserves S10-D2 sealed chain: **True**

## Seal metadata

- Report seal sha256: `e121b82b411697c7d06bbe9ee1cc2df29c04df76712873ed0fbfd76f25fab1cb`
- Seal method: LESSON_HUNTER_004 canonical roundtrip
- Reseal verified on disk: YES

**Inherited seals:**

- `tier_n_spec_seal_sha256`: `f5ca5ee63024e9c8b7b1e85762558ec35eb3d4ebb9ce2a160cbe0f1a0e80a679`
- `plan_lock_seal_sha256`: `ba8bf954d44b373c0ffdc38a1cf8f73dec31a9fc538f0b7584a20659d79ea354`
- `phase2_plan_seal_sha256`: `7a48ad64236971e6fd2a2fa58ab7ab746a71543778ed0a868f3cdf9ff8f74ac3`
- `p3_build_runner_report_seal_sha256`: `1eb04aa312f4053134c1e9387be7716aa4564c019168ee2cedcf789063d96405`
- `p3_build_in_sample_driver_report_seal_sha256`: `ddd604c96508a0ab835bcbae6e72fabc2993cd3f0dc459898ca326617dd96443`
- `p3_5_scaffold_completion_seal_sha256`: `66d38f359b54882b3107c4ad4291673d63f05f5b0d3daa19088b4a4c76469261`
- `p3_6_oos_driver_build_seal_sha256`: `c7d9d7888f2bc5df6850ab37f9bde0b95c3c794486382c4b0d45f32b6bd1b73d`
- `p4_smoke_seal_sha256`: `c31ded81f9a2883586883aadda4d64d629a047917fcebd56169ca42eccf4fdde`
- `p6_is_diagnostic_seal_sha256`: `e6cdc7c68a9e2b7b6d749b73ff433e585c9de55890af5dce3dca51d74430c1b8`
- `p6_5_cost_stress_matrix_seal_sha256`: `f9a34674de4f7fdf8098b39959032d152bf2282e9ad57cedd68bc33cee2099ab`
- `p7_decision_memo_seal_sha256`: `87baa6e8c4cc1eb47c1345b97990eab86d5cefb37636e9fe57a029506d398c05`
- `p10_oos_gate_seal_sha256`: `4038e5334feba9ea61b91dcb47287a7a8f9f8fdfd8ad35990866bc9fbd106137`

## Commit candidate summary

**Files authorized by operator (exactly 2):**

- `reports/s10_d2_p11_park_memo_sealed.json`
- `reports/s10_d2_p11_park_memo_sealed.md`

**Commit subject:** `Seal S10-D2 P11 PARK memo`

**Files explicitly NOT to be staged:**

- brain_memory/projects/trading_bot/lessons.md (long-running parallel-session dirty file; not mine)
- any other unrelated tracked file

**Pathspec commit mode required:** YES

**Verification before commit:** `git status --short -uall` must show ONLY the 2 new authorized files staged.

## Hard boundaries held (this memo authoring turn)

- no_backtest: True
- no_broker_adapter_touched: True
- no_broker_exchange_api: True
- no_commit_in_orchestrator: True
- no_d5_b005_001_nke_revival: True
- no_data_fetch: True
- no_databento_api_call: True
- no_db_historical: True
- no_lessons_md_touched: True
- no_live_trading: True
- no_network_call: True
- no_obsidian_touched: True
- no_oos_confirmation_claim: True
- no_oos_inspection_beyond_sealed_p10: True
- no_paper_trading: True
- no_pre_approval_of_any_successor: True
- no_profitability_claim: True
- no_promotion_to_live: True
- no_qc_runtime: True
- no_re_tuning: True
- no_review_queue_mutation: True
- no_s11_d1_started: True
- no_s8_d1_or_s7_d1_revival: True
- no_scheduler_change: True
- no_source_modification: True
- no_strategy_execution: True
- no_threshold_loosening: True
- no_unrelated_tracked_file_modified: True
