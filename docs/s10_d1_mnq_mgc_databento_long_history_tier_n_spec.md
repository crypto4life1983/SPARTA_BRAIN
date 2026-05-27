# s10 D1 MNQ+MGC Databento Long-History -- Tier-N Specification (SEALED)

Status: SEALED (operator confirmed all 13 DRAFT ambiguities DA1-DA13 at default A; no parameter, threshold, or invariant may be modified post-seal except by an explicit `_revN_` re-spec under separate authorization).
Sealed: 2026-05-26
Authorization: "Authorize s10 D1 MNQ+MGC Tier-N spec SEAL. Confirm all 13 DRAFT ambiguities DA1-DA13 as default A."

Source DRAFT: docs/s10_d1_mnq_mgc_databento_long_history_tier_n_spec_DRAFT.md (committed at a95d7f0)
Source PLAN: docs/s10_d1_mnq_mgc_databento_long_history_tier_n_spec_plan.md (committed at 5c13821)
Family-park reference: reports/external_research_hunter/t8_spy_tlt_gld_uso_2014_2022_family_park_memo.json (sha256 5ba11ea7f51e693d505e50d255830acfe63ccb66c0e23e23432d9ab5f9886518; report_seal_sha256 4f375af7a46d059078782ba490a91e80ef3e1329db7fc710b66b67615e2b0b65)
Availability evidence: reports/external_research_hunter/s10_d1_micro_availability_probe_result_memo.json (sha256 76dcb833f89d3044547e0e361e03f39ae325a22a5c9c06baf1ec0f2e9df213fe)
Predecessor priors (read-only):
- s7 D1 ETF-proxy park (sha256 5eb4309096a8377943799b7cc164cbbb13a86f327a813520255d0fa3b3e00263; verdict REJECT_FAST)
- s9 RSI-2 ETF-proxy park (sha256 cefa80e7b4c2e73f66d5ff4aad37bcb329247e7f16691f92b6d3b748666542c3; verdict PARKED_SAFE_BUT_NOT_MONEY_PROVEN)

HARD BOUNDARIES (held by this SEAL). Plan / SEAL only. No strategy code. No backtest. No simulator. No signal computation. No data fetch. No yfinance / Yahoo Finance call. No Databento call. No DATABENTO_API_KEY access. No QC / LEAN call. No network IO. No review_queue.json mutation. No production idea_memory mutation. No Strategy Lab run. No candidate promotion. No s7 D1 / s9 / B006_001 / B006_002 sealed-artifact modification. No ORB branch artifact mutation. No Step 30 cost constant mutation. No CLAUDE.md modification. No docs/decisions.md modification. No RUNBOOK modification. No pipeline_manifest modification. No .gitignore modification. No `brain_memory/projects/trading_bot/lessons.md` modification or staging. No branch change. No branch creation. No git push. No live trading. No profitability claim. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES. FRC never granted.

----

## 1. Identity (LOCKED at SEAL)

| Field | LOCKED value |
|---|---|
| `candidate_record_id` | **`s10-d1-cross-asset-trend-or-meanrev-mnq-mgc-databento-long-history`** |
| `candidate_family` | **F1 -- long_plus_short_bi_directional_donchian_trend_no_pyramid_atr_stop** |
| `mechanic_family_at_seal` | trend_following (orthogonal to s9 RSI-2 mean-reversion; sibling to s7 D1 trend without pyramid) |
| `is_a_trade_candidate` | true |
| `is_an_equity_universe_candidate` | false |
| `is_a_b006_001_revision` | false |
| `is_a_b006_002_revision` | false |
| `is_a_s7_d1_revision` | false |
| `is_a_s9_revision` | false |
| `predecessor_lineage_references_read_only` | `s7_d1_etf_proxy_park`, `s9_rsi2_etf_proxy_park`, `b006_001_archival`, `b006_002_archival`, `s10_d1_micro_availability_probe`, `t8_etf_proxy_family_park` |
| `diagnostic_only` | true |
| `not_promotable_via_this_diagnostic` | true |
| `default_advisory_label` | `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` (permanent for this candidate independent of verdict) |
| 19 RUNTIME_INVARIANTS | all `true` at SEAL (see §15) |
| 6-gate live block | permanent for this candidate |
| FRC | `NEVER_GRANTED` |

## 2. Mechanic family (LOCKED at SEAL; family-park burden satisfied)

Mechanic family LOCKED to **F1 -- Long+Short Bi-Directional Donchian Trend, No Pyramid, ATR-Based Stop.**

First-principles burden satisfaction (per `reports/external_research_hunter/t8_spy_tlt_gld_uso_2014_2022_family_park_memo.json` section 5):

- **R5_AB_a -- mechanic is structurally different from BOTH P1 and P2:** F1 is trend-following (Donchian breakout); P1 (s7 D1) was also trend-following BUT on ETF proxies with pyramid amplification -- F1 removes pyramid and changes universe; P2 (s9) was mean-reversion (RSI-2 oversold-bounce) which is the structural opposite of breakout entries. F1 is NOT in the mean-reversion family AND F1 is NOT the pyramid-amplified trend mechanic that broke at K12. The family-orthogonality requirement is satisfied at the mechanic level.
- **R5_AB_b -- candidate explicitly addresses BOTH prior failure modes:** P1 failed on K12 cost-stress sensitivity (DR2+DR3 on ETF-proxy cost surface) and K4 trade-curve drawdown 69.10% under pyramid. F1 addresses both by (a) locking `no_pyramid_per_signal` invariant and (b) operating on a structurally different cost surface (per-contract commission + tick-based slippage on futures vs per-share commission + bps slippage on ETFs). P2 failed on negative S0 edge over 414 mean-reversion trades on ETFs. F1 addresses P2 by operating in a different mechanic family AND on a different universe; the S0 edge sign for trend-following on MNQ+MGC futures is a genuine open question, not an a-priori claim of survival.

## 3. Universe (LOCKED at SEAL)

| Field | LOCKED value |
|---|---|
| Universe type | `two_symbol_fixed_basket_continuous_micro_futures` |
| Symbol 1 | **`MNQ.c.0`** (Micro E-mini Nasdaq-100, continuous front-month) |
| Symbol 2 | **`MGC.c.0`** (Micro Gold, continuous front-month) |
| `AddUniverse` calls | **0** (structurally absent) |
| `removed_from_universe` events | **0** (structurally absent) |
| Common-history start (verified by S10-D1 probe) | **2019-05-13** (MNQ launch-adjacent; MGC available; 1,301 records on this date for MNQ.c.0 confirmed) |
| Symbol explicitly excluded | **`MCL.c.0`** (per S10-D1 memo: unreliable before 2021; excluded to preserve clean common-history window starting in 2019) |
| Asset families covered | equity-index (MNQ) + metals (MGC) -- two structurally distinct families |
| Universe-membership integrity surface | structurally N/A (fixed two-symbol basket; no point-in-time universe ledger) |

## 4. Data assumptions (LOCKED at SEAL)

| Field | LOCKED value |
|---|---|
| Vendor | **Databento Historical API** |
| Dataset | **`GLBX.MDP3`** |
| Schema | **`ohlcv-1d`** |
| `stype_in` | **`continuous`** |
| Symbols requested | `["MNQ.c.0", "MGC.c.0"]` |
| Local cache writes outside operator-explicit ingest directory | LOCKED OFF (no `.dbn.zst` files outside `data/s10_d1_mnq_mgc_databento_long_history/raw/`) |
| API key handling | reads `DATABENTO_API_KEY` from environment ONLY at Step 02b operator-side fetch turn (NOT at controller turn); never echoed, logged, or saved |
| Controller-side Databento call | LOCKED OFF (every controller turn for this candidate is BUILD/PLAN/SEAL-only; controller does not call Databento at any phase) |

## 5. Schema (LOCKED at SEAL)

| Field | LOCKED value |
|---|---|
| Schema | `ohlcv-1d` |
| Records expected per symbol per trading day | 1 (daily bar) |
| Fields | `ts_event`, `open`, `high`, `low`, `close`, `volume` |
| Intraday schemas (1s / 1m / 1h) | OUT OF SCOPE for this SEAL; future `_revN_` may include separately |

## 6. stype_in (LOCKED at SEAL)

| Field | LOCKED value |
|---|---|
| `stype_in` | `continuous` |
| Continuous roll stitch | Databento native continuous-front-month synthesis; details out of operator's modification scope |
| `no_continuous_roll_stitch_modification_post_seal` invariant | TRUE |

## 7. IS / OOS windows (LOCKED at SEAL)

| Field | LOCKED value |
|---|---|
| **IS window start** | **`2019-05-13`** |
| **IS window end** | **`2023-12-29`** |
| IS window length | ~4.6 years (~1,140 trading days per symbol) |
| **OOS window start (never inspected at IS)** | **`2024-01-02`** |
| **OOS window end (never inspected at IS)** | **`2025-12-30`** |
| OOS window length | ~2 years (~500 trading days per symbol) |
| Post-OOS data | `2026-01-02 onward` (informational only; no diagnostic) |
| OOS inspection at IS-phase | FORBIDDEN (`oos_inspection_blocked_at_in_sample` invariant carried byte-equivalent from s7 D1 / s9) |

## 8. Strategy concept (LOCKED at SEAL)

> **Long+Short bi-directional Donchian-N breakout trend on a 2-symbol micro futures basket (MNQ.c.0 + MGC.c.0). Enter long when daily close breaks above the trailing N-day high; exit long when daily close breaks below the trailing M-day low. Enter short when daily close breaks below the trailing N-day low; exit short when daily close breaks above the trailing M-day high. Single contract per symbol per signal (no pyramid). ATR(P)-based stop at K*ATR distance from entry. Per-trade risk percentage of portfolio equity sized to the stop distance.**

Where (LOCKED values per §9):

- N = 20 (Donchian entry window)
- M = 10 (Donchian exit window)
- P = 20 (ATR stop window)
- K = 2.0 (ATR stop multiplier)
- Per-trade risk = 1.0% of portfolio equity
- Per-symbol contract cap = 1

## 9. Locked parameter values (all 13 DRAFT ambiguities DA1-DA13 confirmed at default A)

The operator confirmed all 13 DRAFT ambiguities at SEAL time. **No optimization post-seal** (per the `no_strategy_optimization_authorized = true` invariant and the §17 explicit prohibition).

| # | Parameter | LOCKED value | DA confirmation |
|---|---|---|---|
| 1 | `DONCHIAN_ENTRY_WINDOW_N` | **`20`** | DA1 = A (default; DRAFT recommended) |
| 2 | `DONCHIAN_EXIT_WINDOW_M` | **`10`** | DA2 = A (default; symmetric to N=20) |
| 3 | `ATR_STOP_WINDOW_P` | **`20`** | DA3 = A (default; DRAFT recommended) |
| 4 | `ATR_STOP_MULTIPLIER_K` | **`2.0`** | DA4 = A (default; s7 D1 byte-equivalent) |
| 5 | `SIDE` | **`long_plus_short_bi_directional`** | DA5 = A (default; DRAFT recommended) |
| 6 | `PER_TRADE_RISK_PCT_PORTFOLIO_EQUITY` | **`0.010`** (1.0%) | DA6 = A (default; DRAFT recommended) |
| 7 | `PER_SYMBOL_CONTRACT_CAP_PER_SIGNAL` | **`1`** | DA7 = A (LOCKED; non-negotiable) |
| 8 | `DR9_MAX_CONSECUTIVE_ABS_LOG_RETURN` | **`0.30`** | DA8 = A (default; B006_002 byte-equivalent) |
| 9 | `K4_TRADE_CURVE_MAX_DRAWDOWN_PCT_THRESHOLD` | **`0.30`** (30% of `START_CASH_USD`) | DA9 = A (default; DRAFT recommended) |
| 10 | `PER_SYMBOL_MIN_TRADE_COUNT_OVER_IS` | **`30`** | DA10 = A (default; stricter than s7 D1's 10 for 2-symbol basket) |
| 11 | `START_CASH_USD` | **`100000`** | DA11 = A (LOCKED; non-negotiable; B006_NNN / s7 D1 / s9 byte-equivalent) |
| 12 | `WARMUP_DAYS` | **`MAX(longest_lookback_window, 220)` -> resolved to `220`** since `MAX(20, 10, 20, 220) = 220` | DA12 = A (default; B006 lineage carried) |
| 13 | Output schema name | **`sparta.s10.mnq_mgc.trend_no_pyramid.diagnostic_run_report.v1`** | DA13 = A (default; DRAFT recommended) |

Additional locked constants (carried from DRAFT §3-9 with no DA assignment):

| Constant | LOCKED value |
|---|---|
| `MNQ_TICK_SIZE` (index points) | `0.25` |
| `MNQ_DOLLAR_PER_TICK` | `0.50` USD per contract per tick |
| `MGC_TICK_SIZE` (dollars/oz) | `0.10` |
| `MGC_DOLLAR_PER_TICK` | `1.00` USD per contract per tick (10-oz contract) |
| `IS_WINDOW_START` | `2019-05-13` |
| `IS_WINDOW_END` | `2023-12-29` |
| `OOS_WINDOW_START` | `2024-01-02` |
| `OOS_WINDOW_END` | `2025-12-30` |
| `MIN_TRADE_NOTIONAL_USD` (per-trade floor) | `100` (carried from B006_002 byte-equivalent) |
| `K9_MIN_CLOSED_TRADES_PORTFOLIO` | `100` |
| `A7_EFFECTIVE_INDEPENDENT_BETS_MIN` | `1.5` (lowered from s7 D1's 2.5 for 2-symbol basket; locked at SEAL with first-principles justification) |
| `K10_AVG_PAIRWISE_DEPENDENCE_MAX` | `0.50` (carried byte-equivalent) |

## 10. Cost stress + sizing stress matrices (LOCKED at SEAL)

### 10.1 Cost stress S0-S3 (futures-specific)

| Tier | Label | Commission per contract USD | Slippage ticks one-way |
|---|---|---|---|
| S0 | `source_or_default` | **`0.00`** | **`0.0`** |
| S1 | `futures_low_slippage` | **`0.85`** | **`0.5`** |
| S2 | `futures_mid_slippage` | **`0.85`** | **`1.5`** |
| S3 | `futures_high_slippage` | **`0.85`** | **`3.0`** |

### 10.2 Cost-stress matrix is run in the FIRST IS diagnostic

Deferral of any of S0/S1/S2/S3 to a follow-up cycle is FORBIDDEN by family-park memo R8 and the s7 D1 K12 lesson. All four tiers are computed and reported in the same Step 06 simulator run.

### 10.3 Sizing-stress matrix (DEFERRED -- LOCKED OFF for this candidate)

This candidate locks `PER_TRADE_RISK_PCT_PORTFOLIO_EQUITY = 1.0%` and `PER_SYMBOL_CONTRACT_CAP_PER_SIGNAL = 1`. No sizing-multiplier sweep is performed at this candidate's IS diagnostic; sizing-stress is OUT OF SCOPE for this SEAL. A future `_revN_` candidate may include sizing-stress as a separately authorized scope addition.

## 11. DR rules DR1-DR10 (LOCKED at SEAL) + precedence chain

| # | Rule | Trigger | Severity |
|---|---|---|---|
| DR1 | `insufficient_oos_rebalance_count` | OOS daily bars < a threshold equivalent to K9's 100-trade floor (LOCKED at SEAL: trigger if `oos_observed_close_trades < 36` after the IS verdict is favorable; only evaluated when IS verdict is `ELIGIBLE_FOR_OOS`) | `INCONCLUSIVE_HOLD` |
| DR2 | `oos_metrics_degrade_materially_under_cost_stress` | S0 Sharpe > 0 AND (S2 or S3 Sharpe degrades > 50% OR flips negative) | `REJECT_FAST` |
| DR3 | `zero_cost_only_survival` | S0 > 0 AND all S1/S2/S3 <= 0 | `REJECT_FAST` |
| DR4 | `oos_negative_while_is_positive_unexplained` | IS S0 > 0 AND OOS S0 < 0 (only evaluated at OOS phase) | `REJECT_FAST` |
| DR5 | `cost_stress_turns_edge_negative` | tier flip; S3-only monotone-smooth carveout downgrades to `INCONCLUSIVE_HOLD` | `REJECT_FAST` (with carveout) |
| DR6 | `post_warmup_sizing_ambiguity_or_invalid` (NARROWED post-warmup only) | After warmup: NaN/Inf/negative target_contracts; `realized_vol_used_for_sizing == 0`; `spy_price` not finite (or `mnq_price`, `mgc_price` analogs) | `REJECT_FAST` (B006_002 byte-equivalent) |
| DR7 | `missing_oos_or_date_window_evidence` | OOS or IS returns empty | `INCONCLUSIVE_HOLD` |
| DR8 | `live_or_order_routing_path_detected` | live mode detected at Initialize | `HARD_FAIL_VOIDED` |
| DR9 | `mnq_mgc_data_continuity_integrity_check` (REDEFINED for this universe) | (a) gap > 5 trading days on either symbol; OR (b) > 5 missing observations on either symbol over IS+OOS; OR (c) two consecutive abs(log_return) > 0.30 on either symbol; OR (d) any `Open/High/Low/Close <= 0` on either symbol | `INCONCLUSIVE_HOLD` |
| DR10 | `turnover_cost_explosion` | `annual_turnover > 0.50` OR `S2 cost drag > 0.05` | `REJECT_FAST` |

DR11 (`c4_leverage_cap_bound_rate_exceeded`) is NOT carried for F1 because F1 does NOT use a leverage cap (single-contract per signal makes the leverage-cap-bound concept structurally inapplicable). DR11 would only apply if F3 were the selected mechanic; this SEAL locks F1, so DR11 is structurally excluded.

### 11.1 DR precedence chain (LOCKED at SEAL)

```
DR7 -> DR1 -> DR9 -> DR10 -> DR6 -> DR4 -> DR2 -> DR3 -> DR5
```

First fire wins. `no_dr_redefinition_post_seal` invariant locks the chain post-SEAL.

### 11.2 `latent_fail_closed_rules_evaluation`

All DR1-DR10 are evaluated AT EVERY IS-phase run; the latent-evaluation table is published in the compact diagnostic summary (boolean `would_have_fired`, `severity_if_fired`, `is_the_actual_verdict_driver`) -- mirrors B006_002 byte-equivalent.

### 11.3 K-gates (LOCKED at SEAL; carried byte-equivalent from s7 D1 / s9)

| Gate | Trigger | Verdict mapping |
|---|---|---|
| K1 | `sharpe_proxy_per_trade < 0 at S1 baseline` | contributes to `PARKED_SAFE_BUT_NOT_MONEY_PROVEN` verdict |
| K2 | `expectancy_per_trade_dollars <= 0 at S1 baseline` | contributes to `PARKED_SAFE_BUT_NOT_MONEY_PROVEN` verdict |
| K4 | `trade_curve_max_drawdown_pct > 30%` (LOCKED at SEAL DA9 = A) | `REJECT_FAST` |
| K6 | `per_symbol_observed_win_rate_dispersion > threshold` | `INCONCLUSIVE_HOLD` |
| K7 | `silent_filter_introduction_after_lock` (any post-SEAL filter / regime / asset-selection logic in code) | `HARD_FAIL_VOIDED` |
| K8 | `runtime_safety_invariant_false` (any of 19 invariants observed False at runtime) | `HARD_FAIL_VOIDED` |
| K9 | `total_closed_trades < 100` over IS | `INCONCLUSIVE_HOLD` |
| K10 | `avg_pairwise_dependence_measure > 0.50` | `INCONCLUSIVE_HOLD` |
| K11 | (not applicable to F1; reserved for vol-targeted variants) | -- |
| K12 | composite cost-stress fail (DR2 fired + DR3 fired) | `REJECT_FAST` |

K-gate firing priority order: `K8 > K12 > K6/K7 > K10 > K9 > K11 > K1/K2/K4 > A-gates > ELIGIBLE_FOR_OOS` (carried byte-equivalent from s9).

### 11.4 A-gates (LOCKED at SEAL; carried byte-equivalent)

| Gate | Threshold |
|---|---|
| A1 | `total_closed_trades >= 100` over IS |
| A2 | `sharpe_proxy_per_trade > 0` at S1 baseline |
| A3 | `expectancy_per_trade_dollars > 0` at S1 baseline |
| A4 | `trade_curve_max_drawdown_pct <= 30%` (LOCKED DA9 = A) |
| A5 | `portfolio_win_rate_gap_to_breakeven_pp_at_s1 >= +0.5 pp` AND `>= 1/2 symbols` showing positive WR-gap |
| A6 | upstream PASS (Step 02c audit clean) |
| A7 | `effective_independent_bets >= 1.5` (lowered from s7 D1's 2.5 for 2-symbol basket; LOCKED with first-principles justification at SEAL) |
| A8 | cost-stress matrix complete (all 4 tiers run in IS) |
| A9 | C1-C8 safety attestations present (Phase 2 safety template) |
| A10 | `cap_binding_events == 0` (structurally always TRUE for F1's single-contract-per-signal design) |

## 12. Sample-size / K9 rules (LOCKED at SEAL)

| Field | LOCKED value |
|---|---|
| `K9_MIN_CLOSED_TRADES_PORTFOLIO` | `100` |
| `PER_SYMBOL_MIN_TRADE_COUNT_OVER_IS` (DA10 = A) | `30` |
| Expected trade count (F1 Donchian-20/10 bi-directional on 2 micros over 4.6 years) | 100-300 portfolio trades (estimate; actual subject to Step 06 simulator) |
| If K9 fires anyway | verdict path is `DR1 INCONCLUSIVE_HOLD` (not REJECT_FAST); candidate archived under INCONCLUSIVE_HOLD without modification |
| If per-symbol min < 30 fires | reported in compact summary; treated as a contributor to A5 evaluation |

## 13. Diversification expectations (LOCKED at SEAL)

| Field | LOCKED value |
|---|---|
| `A7_EFFECTIVE_INDEPENDENT_BETS_MIN` | `1.5` |
| `K10_AVG_PAIRWISE_DEPENDENCE_MAX` | `0.50` |
| Asset family count | 2 distinct families (equity-index MNQ + metals MGC) |
| Per-symbol contribution distribution requirement | reported in compact summary; if one symbol contributes > 80% of profit OR > 80% of loss, flagged as suspect |
| Diversification independence does NOT rescue edge | EXPLICITLY DISCLAIMED in spec (carried lesson from s9; LESSON_B006_002_002 reinforces) |
| Diversification finding from s7 D1 / s9 on 4-symbol ETF basket | NOT applicable to 2-symbol futures basket; this candidate measures its own diversification independently |

## 14. OOS locking policy (LOCKED at SEAL; carried byte-equivalent)

| Policy | Status |
|---|---|
| OOS data (`2024-01-02 -> 2025-12-30`) shall not be inspected, computed against, simulated over, or queried in any form during the in-sample diagnostic phase | LOCKED |
| Post-OOS data (`2026-01-02 onward`) is informational only; no diagnostic uses it | LOCKED |
| OOS inspection requires a separately authorized turn after IS verdict `ELIGIBLE_FOR_OOS` plus explicit operator approval | LOCKED |
| The loader / validator / signal / simulator / aggregator modules shall structurally enforce IS-only computation at every code path | LOCKED (`oos_inspection_blocked_at_in_sample` invariant) |

## 15. No-live safety contracts (19 RUNTIME_INVARIANTS -- all True at SEAL)

7 inherited from B005_NNN framework:
- `no_live_trading`
- `no_strategy_lab_promotion`
- `no_review_queue_mutation`
- `no_brokerage_connection`
- `no_external_network` (runtime)
- `no_databento_at_runtime_only_at_explicit_ingest_phase`
- `no_production_signal`

4 inherited from B006_001 family:
- `no_strategy_optimization_authorized`
- `no_profitability_claim`
- `no_universe_membership_logic`
- `no_dr_redefinition_post_seal`

3 inherited from B006_002 (carried byte-equivalent; DR11 not in this spec but the discipline carries):
- `no_warmup_order_submission`
- `dr6_warmup_contamination_blocked`
- `no_b006_NNN_AND_s7_AND_s9_sealed_artifact_mutation`

5 NEW s10 D1-specific (LOCKED at SEAL):
- `no_continuous_roll_stitch_modification_post_seal`
- `no_mcl_inclusion_under_long_history_scope`
- `no_intraday_schema_ingest_under_daily_only_design`
- `databento_api_key_read_from_env_only_never_logged_or_saved`
- `no_pyramid_per_signal` (F1-specific)

**Total: 19 RUNTIME_INVARIANTS, all True at SEAL.**

Status surface (permanent for this candidate):

| Field | Value |
|---|---|
| Trading | `PAUSED` |
| Live mode | `BLOCKED_AT_6_GATES` (permanent for this candidate, independent of any future verdict) |
| FRC | `NEVER_GRANTED` |
| 6-gate live block independent of any future verdict outcome | YES |
| `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` advisory label | permanent for this candidate |

## 16. Closed verdict enum + forbidden-token blocklist (LOCKED at SEAL)

```
PERMITTED_VERDICTS = (
    "REJECT_FAST",
    "INCONCLUSIVE_HOLD",
    "ELIGIBLE_FOR_HUMAN_REVIEW",
    "REQUEST_FULL_PREREGISTRATION_REVIEW",
    "PARKED_SAFE_BUT_NOT_MONEY_PROVEN",
    "HARD_FAIL_VOIDED",
    "ELIGIBLE_FOR_OOS",
)
FORBIDDEN_VERDICT_TOKENS = (
    "PASS", "APPROVE", "LIVE", "PROMOTE",
    "SIGNAL", "FOR_PRODUCTION", "EXECUTE", "ROUTE_ORDER",
)
```

Verified at SEAL: none of the 7 permitted verdict values contains any of the 8 forbidden tokens. `PARKED_SAFE_BUT_NOT_MONEY_PROVEN` is carried from s9 precedent. `ELIGIBLE_FOR_OOS` is added for the IS->OOS gating model (no IS verdict implies a live unlock or strategy lab promotion; `ELIGIBLE_FOR_OOS` is a precondition only). `HARD_FAIL_VOIDED` is added for DR8 / K7 / K8 paths.

Output schema name: `sparta.s10.mnq_mgc.trend_no_pyramid.diagnostic_run_report.v1` (DA13 = A confirmed).

## 17. NO STRATEGY OPTIMIZATION (explicit prohibition; mirrors B006_002 / s9)

| Prohibition | Status |
|---|---|
| No parameter tuning of any locked constant post-SEAL | LOCKED |
| No DR9 redefinition post-SEAL | LOCKED |
| No optimization of cost stress S0..S3 post-SEAL | LOCKED |
| No optimization of K9 / K10 / A7 / K4 thresholds post-SEAL | LOCKED |
| No optimization of DR6 severity or evaluation window post-SEAL | LOCKED |
| No introduction of filters / regime gates / asset selection post-SEAL (would trigger K7) | LOCKED |
| If unfavorable verdict -> response | archive candidate under that verdict; do not modify any parameter or DR rule |
| Runner is a deterministic, parameter-free reproducer of this sealed spec | LOCKED |

## 18. Kill criteria K1-K12 (LOCKED at SEAL)

| # | Kill trigger | Source |
|---|---|---|
| K1 | any DR rule fires `REJECT_FAST` (DR2 / DR3 / DR4 / DR5 / DR6 / DR10) | DR framework |
| K2 | DR9 `mnq_mgc_data_continuity_integrity_failure` AND > 5 violations | §11 DR9 |
| K3 | DR6 post-warmup invalid-sizing event count > 0 (single event -> REJECT_FAST) | §11 DR6 |
| K4 | `trade_curve_max_drawdown_pct > 30%` of `START_CASH_USD` | §11.3 K4 |
| K5 | any forbidden-verdict-token appears in runner output | §16 hygiene |
| K6 | runner attempts `SetLiveMode` / `SetBrokerageModel` / `DeployAlgorithm` / unauthorized network call / unauthorized Databento call at runtime | DR8 / RUNTIME_INVARIANTS |
| K7 | any order-submit attempt while in warmup window | §15 `no_warmup_order_submission` |
| K8 | runner mutates any s7 D1 / s9 / B006_NNN / T8 family-park sealed artifact (byte-shift) | §15 `no_b006_NNN_AND_s7_AND_s9_sealed_artifact_mutation` |
| K9 | runner makes a Databento API call outside the explicitly authorized Step 02b ingest phase | §15 |
| K10 | runner caches `.dbn.zst` files outside `data/s10_d1_mnq_mgc_databento_long_history/raw/` | §15 |
| K11 | runner accesses `DATABENTO_API_KEY` outside the explicitly authorized ingest phase | §15 |
| K12 | composite cost-stress fail (DR2 fired + DR3 fired in the same IS run) | §11.3 |

Any K1-K12 -> archive under `REJECT_FAST` (or `HARD_FAIL_VOIDED` for K6 / K7 / K8); no parameter tuning per §17.

## 19. Continue criteria C1-C5+ (LOCKED at SEAL)

| # | Criterion | Verdict mapping |
|---|---|---|
| C1 | all DR1-DR10 latent-eval `would_have_fired = False` | precondition |
| C2 | IS S0 Sharpe > 0 | precondition |
| C3 | IS max drawdown <= 30% of `START_CASH_USD` | precondition |
| C4 | NOT APPLICABLE (DR11 / leverage-cap-bound rate is not in this spec) | -- |
| C5 | Cost-stress matrix positive Sharpe at all tiers S0/S1/S2/S3 | `ELIGIBLE_FOR_HUMAN_REVIEW` |
| C5+ | all 4 cost tiers Sharpe > 0.5 | `REQUEST_FULL_PREREGISTRATION_REVIEW` |
| C-OOS | IS verdict in `{ELIGIBLE_FOR_HUMAN_REVIEW, REQUEST_FULL_PREREGISTRATION_REVIEW}` AND explicit operator authorization | `ELIGIBLE_FOR_OOS` |

Even `REQUEST_FULL_PREREGISTRATION_REVIEW` does NOT unlock live, does NOT grant FRC, does NOT promote to Strategy Lab. Even `ELIGIBLE_FOR_OOS` does NOT unlock live; it gates a separate OOS-phase authorization only.

## 20. Locked seal decisions (all 13 DA confirmations)

| # | Topic | Confirmed | Locked value |
|---|---|---|---|
| DA1 | Donchian entry window N | **A** | `20` |
| DA2 | Donchian exit window M | **A** | `10` |
| DA3 | ATR stop window P | **A** | `20` |
| DA4 | ATR stop multiplier K | **A** | `2.0` |
| DA5 | Side | **A** | `long_plus_short_bi_directional` |
| DA6 | Per-trade risk percentage | **A** | `1.0%` of portfolio equity |
| DA7 | Per-symbol contract cap | **A** | `1` (non-negotiable; no_pyramid) |
| DA8 | `DR9_MAX_CONSECUTIVE_ABS_LOG_RETURN` threshold | **A** | `0.30` |
| DA9 | K4 / A4 max-drawdown threshold | **A** | `0.30` (30% of `START_CASH_USD`) |
| DA10 | Per-symbol minimum trade count | **A** | `30` |
| DA11 | `START_CASH_USD` | **A** | `100000` (non-negotiable) |
| DA12 | `WARMUP_DAYS` for runner | **A** | `MAX(longest_lookback, 220) -> 220` |
| DA13 | Output schema name | **A** | `sparta.s10.mnq_mgc.trend_no_pyramid.diagnostic_run_report.v1` |

All 13 confirmed at the recommended primary. No revisions. Spec advances to SEAL with default discipline preserved.

## 21. Phase ladder

| # | Phase | Status (this turn) | Authorization template |
|---|---|---|---|
| 0 | Selection plan | implicit (`docs/next_research_track_selection_plan_after_s9_park.md`) | -- |
| 1 | T8 family-park memo | COMPLETE prior commit `5c13821` | -- |
| 2 | Tier-N spec PLAN | COMPLETE prior commit `5c13821` | -- |
| 3 | Tier-N spec DRAFT | COMPLETE prior commit `a95d7f0` | -- |
| 4 | **Tier-N spec SEAL** | **COMPLETE THIS TURN** | -- |
| 5 | Step 02b Databento operator-side data fetch | NOT AUTHORIZED | `Authorize s10 D1 MNQ+MGC Step 02b operator-side Databento fetch only` |
| 6 | Step 02c raw-data audit | NOT AUTHORIZED | `Authorize s10 D1 MNQ+MGC Step 02c raw-data audit only` |
| 7 | Step 03 loader BUILD ONLY | NOT AUTHORIZED | `Authorize s10 D1 MNQ+MGC Step 03 loader BUILD only` |
| 8 | Step 04 validator BUILD ONLY | NOT AUTHORIZED | `Authorize s10 D1 MNQ+MGC Step 04 validator BUILD only` |
| 9 | Step 05 signal BUILD ONLY | NOT AUTHORIZED | `Authorize s10 D1 MNQ+MGC Step 05 signal BUILD only` |
| 10 | Step 06 simulator BUILD ONLY | NOT AUTHORIZED | `Authorize s10 D1 MNQ+MGC Step 06 simulator BUILD only` |
| 11 | Step 07 aggregator BUILD ONLY | NOT AUTHORIZED | `Authorize s10 D1 MNQ+MGC Step 07 aggregator BUILD only` |
| 12 | IS decision memo + park or eligibility | NOT AUTHORIZED | `Authorize s10 D1 MNQ+MGC IS decision memo only` |

## 22. Boundaries held this SEAL turn

| Boundary | Status |
|---|---|
| PLAN / SEAL ONLY | met |
| No code (no `.py` written by this SEAL; sealed spec is markdown only) | met |
| No backtest | met |
| No simulator run | met |
| No signal computation | met |
| No data fetch | met |
| No Databento call | met |
| No `DATABENTO_API_KEY` access | met |
| No yfinance / Yahoo Finance call | met |
| No QC / LEAN call | met |
| No network IO | met |
| No live trading | met |
| No mutation of `review_queue.json` | met |
| No mutation of production `idea_memory` | met |
| No Strategy Lab run | met |
| No candidate promotion | met |
| No modification of s7 D1 / s9 sealed artifacts | met -- byte-stable |
| No modification of B006_001 / B006_002 sealed artifacts | met -- byte-stable |
| No modification of ORB branch artifacts | met |
| No modification of CLAUDE.md / docs/decisions.md / RUNBOOK / pipeline_manifest / .gitignore | met |
| No modification or staging of `brain_memory/projects/trading_bot/lessons.md` (dirty + unstaged from prior session; left untouched) | met |
| No branch change or creation | met |
| No git push | met |
| Trading status | `PAUSED` |
| Live status | `BLOCKED_AT_6_GATES` |
| FRC | `NEVER_GRANTED` |

## 23. Files written this SEAL turn

| File | Purpose |
|---|---|
| `docs/s10_d1_mnq_mgc_databento_long_history_tier_n_spec.md` | This sealed Tier-N specification (single file; markdown body containing all locked parameters, DR rules, K-gates, A-gates, invariants, kill criteria, continue criteria, and DA confirmations) |

No other repository file is modified by this SEAL. The brain_memory `lessons.md` dirty + unstaged state from prior controller-session appends remains untouched.

## 24. Next-step authorization scope

The next operator authorization in the established controller-session pattern shall use this scope to advance:

- **"Authorize s10 D1 MNQ+MGC Step 02b operator-side Databento fetch only"** -- begin the Databento ingest phase: operator runs the data-fetch script outside the controller session, in their own environment, with `DATABENTO_API_KEY` read from environment and never echoed. Output: `data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_c_0_ohlcv_1d_IS.csv` and `MGC_c_0_ohlcv_1d_IS.csv` (or operator's preferred filenames pinned by Step 02b plan).

Alternative scopes:

- **"Authorize alternative track selection plan revision only"** -- if the operator decides to abandon this track in favor of a different option from `docs/next_research_track_selection_plan_after_s9_park.md` section 14.
- **"Authorize family-level park only without opening new track"** -- if the operator decides not to advance this candidate after seeing the sealed spec.
- **"Authorize cross-domain pivot only"** -- if the operator pivots to a different project entirely.

This sealed spec is the source of truth for the s10 D1 MNQ+MGC Databento long-history candidate. Future BUILD / FETCH / RUN phases that contradict this spec require either a fresh `_revN_` re-spec (under separate authorization) or an out-of-band justification.

## 25. One-paragraph summary

This document is the sealed Tier-N specification for `s10-d1-cross-asset-trend-or-meanrev-mnq-mgc-databento-long-history`, a fresh research candidate on the Databento micro futures universe (`MNQ.c.0` + `MGC.c.0`) authorized as the T7-Path-A pivot off the SPY/TLT/GLD/USO 2014-2022 ETF-proxy universe (family-level parked per the T8 memo at `5ba11ea7...86518`, report seal `4f375af7...b0b65`). The mechanic family is LOCKED to **F1 long+short bi-directional Donchian trend with no pyramid and ATR-based stop**, satisfying the family-park memo first-principles burden by (a) being structurally different from s9's mean-reversion family and (b) explicitly removing the pyramid mechanism that broke s7 D1 with cost-stress sensitivity. The spec is sealed with **all 13 DRAFT ambiguities DA1-DA13 resolved to default A**: `DONCHIAN_ENTRY_WINDOW_N = 20`, `DONCHIAN_EXIT_WINDOW_M = 10`, `ATR_STOP_WINDOW_P = 20`, `ATR_STOP_MULTIPLIER_K = 2.0`, `SIDE = long_plus_short_bi_directional`, `PER_TRADE_RISK_PCT_PORTFOLIO_EQUITY = 0.010`, `PER_SYMBOL_CONTRACT_CAP_PER_SIGNAL = 1`, `DR9_MAX_CONSECUTIVE_ABS_LOG_RETURN = 0.30`, `K4_TRADE_CURVE_MAX_DRAWDOWN_PCT_THRESHOLD = 0.30`, `PER_SYMBOL_MIN_TRADE_COUNT_OVER_IS = 30`, `START_CASH_USD = 100000`, `WARMUP_DAYS = 220`, `output_schema = sparta.s10.mnq_mgc.trend_no_pyramid.diagnostic_run_report.v1`. The IS window is `2019-05-13 -> 2023-12-29` (~4.6 years); the OOS window is `2024-01-02 -> 2025-12-30` (~2 years; never inspected at IS phase per `oos_inspection_blocked_at_in_sample` invariant). Data scope: `GLBX.MDP3` dataset, `ohlcv-1d` schema, `stype_in = continuous`; `DATABENTO_API_KEY` read from environment only at the explicit Step 02b operator-side fetch turn; controller never calls Databento. Cost-stress matrix S0/S1/S2/S3 LOCKED with futures-specific cost model (commission $0.85/contract at S1-S3 baseline; slippage 0.0/0.5/1.5/3.0 ticks one-way); the matrix is computed in the FIRST IS diagnostic per family-park memo R8. DR rules DR1-DR10 LOCKED with precedence chain `DR7 -> DR1 -> DR9 -> DR10 -> DR6 -> DR4 -> DR2 -> DR3 -> DR5`; DR11 (`c4_leverage_cap_bound_rate_exceeded`) is structurally NOT in this spec because F1 does not use a leverage cap. K1-K12 kill gates and A1-A10 acceptance gates carried byte-equivalent from s7 D1 / s9 / B006_002 lineage with `A7_effective_independent_bets_min` lowered to `1.5` (justified for 2-symbol basket; locked with first-principles documentation). **19 RUNTIME_INVARIANTS all True at SEAL** (7 inherited B005_NNN + 4 inherited B006_001 + 3 inherited B006_002 + 5 NEW s10 D1-specific: `no_continuous_roll_stitch_modification_post_seal`, `no_mcl_inclusion_under_long_history_scope`, `no_intraday_schema_ingest_under_daily_only_design`, `databento_api_key_read_from_env_only_never_logged_or_saved`, `no_pyramid_per_signal`). Closed verdict enum extended to 7 values (adds `PARKED_SAFE_BUT_NOT_MONEY_PROVEN` from s9 precedent, `ELIGIBLE_FOR_OOS` for IS->OOS gating, `HARD_FAIL_VOIDED` for DR8/K7/K8); forbidden-token blocklist unchanged. Even the most favorable verdict (`REQUEST_FULL_PREREGISTRATION_REVIEW`) does NOT unlock live, does NOT grant FRC, does NOT promote to Strategy Lab. `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` advisory label is permanent for this candidate independent of any future verdict. **No code authored this turn. No backtest. No simulator. No signal computation. No data fetch. No yfinance / Yahoo Finance call. No Databento call. No DATABENTO_API_KEY access. No QC / LEAN call. No network IO. No mutation of review_queue.json. No mutation of production idea_memory. No Strategy Lab run. No candidate promotion. No modification of s7 D1 / s9 / B006_001 / B006_002 sealed artifacts. No modification of ORB branch artifacts. No modification of CLAUDE.md / docs/decisions.md / RUNBOOK / pipeline_manifest / .gitignore. No modification or staging of brain_memory/projects/trading_bot/lessons.md. No branch change. No branch creation. No git push.** Trading remains `PAUSED`. Live remains `BLOCKED_AT_6_GATES` (permanent for this candidate). FRC `NEVER_GRANTED`. **Next required step: `Authorize s10 D1 MNQ+MGC Step 02b operator-side Databento fetch only`.**

----

*Sealed spec. Diagnostic-only. Not a profit proof. Not a live-go signal. No code authored. No backtest. No data fetch. No Databento call. No DATABENTO_API_KEY access. Mechanic family F1 LOCKED at SEAL with all 13 DRAFT ambiguities confirmed at default A.*
