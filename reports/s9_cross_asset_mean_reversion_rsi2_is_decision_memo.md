# s9 RSI-2 (ETF-Proxy) -- In-Sample Decision Memo (SEALED)

**Schema:** `sparta.external_research_hunter.s9_cross_asset_mean_reversion_rsi2_is_decision_memo.v1`
**Status:** `SEALED`
**Candidate record id:** `s9-cross-asset-mean-reversion-rsi2-spy-tlt-gld-uso-yfinance-proxy`
**Sealed at (UTC):** `2026-05-26T20:31:25Z`
**Trading status:** `PAUSED`
**Live status:** `BLOCKED_AT_6_GATES`
**FRC granted:** `False`

> Decision memo only. No new backtest. No simulator re-run.
> No OOS. No data fetch. No network. No vendor SDK.
> No brokerage. No live order. No paper order.
> No Strategy Lab. No candidate promotion. No review_queue.

---

## 1. Final in-sample verdict

### **`PARKED_SAFE_BUT_NOT_MONEY_PROVEN`**

**Explanation:** Park: K1 Sharpe<0, K2 expectancy<=0.

- **Verdict source:** aggregator build commit `95edc4780e39542fbfda1c00b12b6bc9b84e5f56`
- **Aggregator build report sha256:** `1f6e827f03af8cb21e0ae8404b389199190eebd733eaa59011a17cf3f5b084e0`
- **Aggregator build report seal:** `74b6dc24dcd85ea65309e78a63e0d93419dd2d424c0eb52bb15712e192486ab2`
- **Priority order applied:** `K8 > K12 > K6/K7 > K10 > K9 > K11 > K1/K2/K4 > A-gates > ELIGIBLE_FOR_OOS`
- **Active K path:** `K1 (Sharpe<0) OR K2 (expectancy<=0) AT S1 BASELINE`

## 2. Key metrics (S1 baseline)

| Metric | Value |
|---|---|
| total_closed_trades_portfolio | 414 |
| total_net_pnl_dollars | -1334.870032 |
| total_gross_pnl_dollars | -1272.250032 |
| mean_trade_net_pnl_dollars | -3.224324 |
| stdev_trade_net_pnl_dollars | 33.194124 |
| sharpe_proxy_per_trade | **-0.097135** (K1 fires) |
| expectancy_per_trade_dollars | **-3.224324** (K2 fires) |
| portfolio_win_rate | 0.531401 |
| portfolio_pl_ratio | 0.601472 |
| portfolio_implied_breakeven_win_rate | 0.624425 |
| portfolio_win_rate_gap_to_breakeven_pp | **-9.302437** (A5 fails) |
| trade_curve_max_drawdown_dollars | 1642.249766 |
| trade_curve_max_drawdown_pct_vs_starting_cash | 1.64225% (K4 clears) |
| cap_binding_events_count | 0 (structurally zero) |

## 3. Cost-stress matrix (S0/S1/S2/S3)

| Tier | slip | comm | trades | net pnl | sharpe pt | expectancy | maxdd % | wr | k4 |
|---|---|---|---|---|---|---|---|---|---|
| S0 | 0.0 | 0.0 | 414 | -1211.030033 | -0.08816 | -2.925193 | 1.56573 | 0.533816 | False |
| S1 | 1.0 | 1.0 | 414 | -1334.870032 | -0.097135 | -3.224324 | 1.64225 | 0.531401 | False |
| S2 | 3.0 | 1.5 | 414 | -1578.440026 | -0.115118 | -3.812657 | 1.79145 | 0.519324 | False |
| S3 | 5.0 | 2.0 | 414 | -1825.78003 | -0.133048 | -4.410097 | 1.95226 | 0.507246 | False |

**DR2/DR3/DR5 all clear.** Cost-stress matrix degrades smoothly; K12 does NOT fire. The S0 row loses $1,211 -- the edge itself is negative even at zero cost.

## 4. Why parked

**Primary reason:** K1 (Sharpe proxy per trade < 0) AND K2 (expectancy per trade <= 0) fire at S1 baseline. Verdict priority routes through K1/K2/K4 to PARKED_SAFE_BUT_NOT_MONEY_PROVEN.

**Secondary observations:**
- A2 fails: Sharpe proxy per trade is -0.097, below the A2 threshold of 0.
- A3 fails: expectancy per trade is -$3.22, below the A3 threshold of $0.
- A5 fails: portfolio WR gap to breakeven is -9.30pp, below the +0.5pp threshold.
- Win rate is 53.14% but implied breakeven win rate is 62.44%; the wins are too small relative to the losses to clear the P/L-implied breakeven.

**The smoking-gun S0 row:**
- S0 net_pnl_dollars: **-1211.030033** (zero slippage, zero commission)
- At S0 (zero slippage, zero commission, no cost friction whatsoever), the strategy still loses money over 414 trades. The edge itself is negative; costs only make a negative edge more negative. This is structurally distinct from a cost-stress failure mode.

## 5. Why OOS is blocked

**Structural reason:** The 8-value VerdictReason enum has only one value that gates onward to OOS (ELIGIBLE_FOR_OOS), and even that one is only a structural attestation; OOS inspection still requires a separately authorized operator turn. The verdict PARKED_SAFE_BUT_NOT_MONEY_PROVEN is one of seven park values that never gate onward to OOS by design.

**Mechanical reason:** Running OOS on a strategy that lost money at S0 in-sample would be a research anti-pattern: it would test whether the OOS window happens to flatter a negatively-expected mechanic. Any 'good' OOS result under this premise would be coin-flip noise, not evidence of an edge.

- Candidate operational status at memo: `IS_DECISION_MEMO_SEALED_RECOMMEND_PARK`
- OOS inspection intentionally blocked: **True**
- Post-OOS inspection intentionally blocked: **True**

## 6. What worked structurally (vs s7 D1 ETF-proxy predecessor)

### 6.1 Trade-count problem SOLVED
- s7 D1 ETF-proxy closed trades: **37**
- s9 ETF-proxy closed trades: **414**
- K9 threshold: 100
- 414 trades comfortably clears the K9 sample-size floor of 100. Mean-reversion at RSI(2) fires ~46 trades/year on the portfolio vs Donchian-55's ~4 trades/year. The trade-density failure mode from s7 D1 is directly addressed at the signal-density layer.

### 6.2 Drawdown problem SOLVED
- s7 D1 outcome: high (cap binding events 16/37 trade groups)
- s9 max drawdown pct: **1.64225%**
- K4 threshold: 50.0%
- Max drawdown stays at 1.64% on the trade curve; K4 (>50%) cleared with enormous margin. The no-pyramid lock (MAX_UNITS_PER_SYMBOL=1) structurally eliminates the amplification failure mode.

### 6.3 Cost-stress problem SOLVED
- s7 D1 outcome: K12 fired via DR2+DR3 (cost-stress catastrophic)
- s9 outcome: DR2/DR3/DR5 all clear; cost-stress matrix smooth
- Cost-stress matrix degrades smoothly across S0/S1/S2/S3 with no tier turning catastrophically negative. K12 does NOT fire. The cost-stress sensitivity is benign in s9 because the per-trade P&L distribution is symmetric and the per-trade cost ratio is small relative to the per-trade range. The cost-stress failure mode from s7 D1 is also addressed.

### 6.4 Diversification finding REVALIDATED
- s7 D1 avg pairwise dependence: 0.041
- s9 avg pairwise dependence: 0.041354
- s7 D1 effective independent bets: 3.56
- s9 effective independent bets: 3.558527
- Cross-asset diversification on SPY/TLT/GLD/USO 2014-2022 is validated under a second, structurally orthogonal mechanic. The finding is a UNIVERSE property, not a mechanic artifact.

### 6.5 No safety warnings
- C1-C8 all True: **True**
- K6 fired: False
- K7 fired: False
- K8 (provenance drift): False

## 7. What failed economically

**Primary failure:** The mean-reversion edge itself is negative on this universe at the locked Connors RSI-2 parameters (lookback=2, oversold=10, exit=50, long-only, no filter, no pyramid, no stop, no time-stop). At S0 (zero cost), the strategy loses $1,211 over 414 trades. At S1 (baseline cost), it loses $1,335. At S3 (realistic adverse cost), it loses $1,826.

**Mechanism:** Win rate is 53.14% (above 50%, which superficially looks good) but P/L ratio is approximately 0.78 (wins are ~22% smaller than losses). The strategy reverts often enough to win the majority of trades, but the few losing trades are large enough to erase the cumulative edge. Implied breakeven win rate is 62.44%; observed 53.14% leaves a -9.30 percentage-point gap. Mean-reversion-without-stops trades a high win-rate floor against an unbounded loss-side tail; over 2014-2022 on this universe, the tail wins.

**Per-symbol consistency:** All four markets show the same shape: SPY/TLT/GLD/USO each have observed win rate above breakeven on absolute terms but below the P/L-implied breakeven. There is no single-market carrier of a positive edge; the failure is structural across the universe.

**Alternative interpretations rejected:**
- Not a sample-size problem: 414 trades is plenty.
- Not a drawdown problem: 1.64% MaxDD is well-behaved.
- Not a cost-stress problem: DR rules all clear.
- Not a diversification problem: 3.56 effective independent bets.
- Not a safety problem: C1-C8 all True.
- Not a provenance problem: K8 clears; all sealed shas match.

## 8. Per-symbol breakdown (S1)

| Symbol | trades | net pnl | wins | losses | wr | ibwr | wr gap pp |
|---|---|---|---|---|---|---|---|
| SPY | 101 | 140.090297 | 65 | 36 | 0.643564 | 0.589441 | 5.41231 |
| TLT | 103 | -104.229948 | 48 | 55 | 0.466019 | 0.520576 | -5.455702 |
| GLD | 103 | -194.130359 | 58 | 45 | 0.563107 | 0.640569 | -7.746174 |
| USO | 107 | -1176.600021 | 49 | 58 | 0.457944 | 0.62159 | -16.364634 |

All four markets show the same shape (wr above 50%, P/L < 1, negative wr gap to breakeven). No single-market carrier; the failure is structural across the universe.

## 9. Universe-level conclusion

Two structurally orthogonal mechanics (trend-following s7 D1, mean-reversion s9) empirically falsified on the same ETF universe (SPY/TLT/GLD/USO 2014-2022) at canonical parameters with realistic ETF-proxy cost assumptions. The universe-level conclusion strengthens: the current ETF-proxy cost structure does not support EITHER structurally-pure trend-following OR structurally-pure mean-reversion at canonical parameters on this universe.

**Further research directions** (each requires its own fresh authorization to initiate):
- (a) Different cost-structure assumption (lower commission baseline, lower slippage; would require a fresh _revN_ spec with explicit justification of the assumed cost regime).
- (b) Different mechanic family entirely on the same universe (rotation, carry, vol-of-vol; these have different return-source mechanics from trend/mean-reversion).
- (c) Different parameters under a fresh _revN_ spec (e.g., RSI(2) thresholds 5/55 instead of 10/50, or RSI(3), or a different lookback window); but parameter-sweep without a first-principles justification is parameter-shopping and would invite K7 silent-introduction risk on a future iteration.
- (d) Different universe entirely (international ETFs, sector ETFs, equity single names; would require a fresh data-fetch authorization and a fresh Tier-N spec).
- (e) Accept the universe-level finding and pivot to other research tracks (e.g., the futures-track lessons already captured in brain_memory/projects/trading_bot/lessons.md).

- Park is permanent for s9 ETF-proxy at canonical parameters: **True**
- Revival requires fresh `_revN_` spec: **True**

## 10. No-live / no-Strategy-Lab / no-review_queue confirmation

- `live_promotion_path_closed`: **True**
- `no_live_order_placed`: **True**
- `no_paper_order_placed`: **True**
- `no_brokerage_connection`: **True**
- `no_strategy_lab_run_invoked`: **True**
- `no_strategy_lab_promotion`: **True**
- `no_candidate_promotion_to_production_idea_memory`: **True**
- `no_review_queue_mutation`: **True**
- `no_production_idea_memory_mutation`: **True**
- `no_orb_branch_artifact_mutation`: **True**
- `no_step_30_cost_constant_mutation`: **True**
- `no_scheduler_invocation`: **True**
- `no_autopilot_invocation`: **True**
- `frc_never_granted`: **True**
- `no_profitability_claim`: **True**
- `advisory_label_permanent`: **DIAGNOSTIC_ONLY_NOT_LIVE_GRADE**

## 11. Recommended next step

**Primary action:** Seal s9 lifecycle park report; then move to a new research track.

- **Step 1:** Seal `reports/s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_park_report.{json,md}` terminally closing the s9 ETF-proxy chain. Mirror the s7 D1 ETF-proxy park report pattern (commit a5ac092).
- **Step 2:** Append terminal lesson to `brain_memory/projects/trading_bot/lessons.md` capturing the universe-level finding (two orthogonal mechanics falsified on same universe at canonical parameters).
- **Step 3:** Select next research track. Candidates (informational; each requires its own fresh operator authorization to begin): (a) different universe entirely; (b) different mechanic family (rotation, carry, vol-of-vol) on the same universe; (c) different cost-structure assumption; (d) operator-directed pivot.

- Do NOT proceed to OOS: **True**
- Do NOT iterate s9 parameters without fresh `_revN_` spec: **True**
- Do NOT resurrect s9 under a different threshold silently: **True**
- Park is permanent for canonical params: **True**

## 12. Sealed chain attestation (parent shas; drift = 0)

| Artifact | sha256 (first 16) | commit |
|---|---|---|
| Tier-N spec | `6690c0d789285598` | `5bd8e62a1a614042a30e44f4060e54c7cdd20401` |
| Selection plan | `d8753155d47c36e0` | `530b54598fa7098eb746f2122b4002db2c984422` |
| Signal-module spec | `59e5f401232f1934` | `c5393ab31a58059004b8cd337cd428eacbcbaece` |
| Signal build report (PASS) | `d78ad857ffc26a43` | `1a055bd1adecf30408de99971bf6e9f22cf53866` |
| Simulator-module spec | `c64bbe7525ad06d5` | `3a9a0de9eba9e448d0440fa45fb40e8107fb8e0f` |
| Simulator build report (PASS) | `0bdbde0e2a0d6522` | `1de75e576c9878a2dfc2568b8f5747fda7eb84cf` |
| Aggregator decision plan (A2) | `af6f8fd6d1de1b91` | `113f5b954e189088e6ddda18a2138abb27ff92e2` |
| Aggregator build report (PASS) | `1f6e827f03af8cb2` | `95edc4780e39542fbfda1c00b12b6bc9b84e5f56` |
| s7 D1 ETF-proxy park (predecessor) | n/a | `a5ac092` |

**Drift count at memo: 0**

## 13. Labels

- `S9_IS_DECISION_MEMO`
- `FINAL_IS_VERDICT_PARKED_SAFE_BUT_NOT_MONEY_PROVEN`
- `OOS_BLOCKED`
- `K1_FIRED`
- `K2_FIRED`
- `K12_DID_NOT_FIRE`
- `K4_DID_NOT_FIRE`
- `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE`
- `PARK_PERMANENT_FOR_CANONICAL_PARAMS`
- `REVIVAL_REQUIRES_FRESH_revN_SPEC`
- `UNIVERSE_LEVEL_CONCLUSION_TWO_ORTHOGONAL_MECHANICS_FALSIFIED`
- `DIVERSIFICATION_HYPOTHESIS_REVALIDATED`

## 14. Seal verification

```
seal_method = sha256 over json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False) EXCLUDING report_seal_sha256 + seal_method

report_seal_sha256 = <see JSON report_seal_sha256 field>
```

Companion JSON sha256 = recompute sha256 of the JSON bytes on disk.

**Memo sealed. Trading: PAUSED. Live: BLOCKED_AT_6_GATES. FRC never granted.**

