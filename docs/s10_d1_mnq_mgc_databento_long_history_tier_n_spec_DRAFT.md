# s10 D1 MNQ+MGC Databento Long-History -- Tier-N Specification DRAFT

Status: DRAFT (not sealed; operator confirms DRAFT ambiguities at SEAL turn; no code, no fetch, no run by this DRAFT).
Authored: 2026-05-26
Authorization: "Authorize s10 D1 MNQ+MGC Databento long-history Tier-N spec DRAFT."

Plan source: docs/s10_d1_mnq_mgc_databento_long_history_tier_n_spec_plan.md (sha256 0d07fa1cc89f484307537439d609a431a7eb23ed5dc975dfd7c7f9875a3801ae; committed at 5c13821)
Family-park reference: reports/external_research_hunter/t8_spy_tlt_gld_uso_2014_2022_family_park_memo.json (sha256 5ba11ea7f51e693d505e50d255830acfe63ccb66c0e23e23432d9ab5f9886518)
Availability evidence: reports/external_research_hunter/s10_d1_micro_availability_probe_result_memo.json (sha256 76dcb833f89d3044547e0e361e03f39ae325a22a5c9c06baf1ec0f2e9df213fe)
Predecessor priors (read-only):
- s7 D1 ETF-proxy park report (sha256 5eb4309096a8377943799b7cc164cbbb13a86f327a813520255d0fa3b3e00263; verdict REJECT_FAST)
- s9 RSI-2 ETF-proxy park report (sha256 cefa80e7b4c2e73f66d5ff4aad37bcb329247e7f16691f92b6d3b748666542c3; verdict PARKED_SAFE_BUT_NOT_MONEY_PROVEN)

HARD BOUNDARIES (held by this DRAFT). Plan / spec DRAFT only. No strategy code. No backtest. No simulator. No signal computation. No data fetch. No yfinance / Yahoo Finance call. No Databento call. No DATABENTO_API_KEY access. No QC / LEAN call. No network IO. No review_queue.json mutation. No production idea_memory mutation. No Strategy Lab run. No candidate promotion. No s7 D1 / s9 / B006_001 / B006_002 sealed-artifact modification. No ORB branch artifact mutation. No Step 30 cost constant mutation. No CLAUDE.md modification. No docs/decisions.md modification. No RUNBOOK modification. No pipeline_manifest modification. No .gitignore modification. No `brain_memory/projects/trading_bot/lessons.md` modification or staging. No branch change. No branch creation. No git push. No live trading. No profitability claim. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES. FRC never granted.

----

## 1. Mechanic family choice -- RESOLVED to F1 trend-no-pyramid

The Tier-N spec PLAN section 5 enumerated four mechanic-family options: F1 trend-no-pyramid, F2 cross-sectional rotation, F3 vol-targeted basket, F4 carry / term-structure. This DRAFT RESOLVES the family to:

**F1 -- Long+Short Bi-Directional Donchian Trend, No Pyramid, ATR-Based Stop.**

Rationale at DRAFT time (subject to operator confirmation or revision at SEAL):

- F1 directly addresses the s7 D1 (P1) pyramid amplification failure by structurally removing the +0.5N pyramid mechanism (single contract per symbol per signal); the locked `no_pyramid_per_signal` invariant carries from the s7 D1 sibling Databento-track lesson.
- F1 is in a structurally different mechanic family from s9 RSI-2 (P2 mean-reversion); the family-park memo section 5 first-principles burden for surviving P2 is satisfied by family-orthogonality at the mechanic level.
- F1 on futures has a different cost structure than F1 on ETF proxies (tick-based slippage vs bps-based; per-contract commission vs per-share); the cost-stress sensitivity that broke s7 D1 has a different sensitivity surface here.
- F1 daily Donchian-N at moderate N (e.g., N=20 entry / N=10 exit; subject to DRAFT_AMBIGUITY operator confirmation) on 2 micro futures over a 4.6-year IS window is expected to fire 50-150 entries per symbol -> 100-300 portfolio trades, comfortably clearing K9.
- F1 bi-directional (long+short) addresses the s7 D1 / s9 per-symbol concentration pathology (USO-carries-all on ETF proxies); short side gives the strategy a path to participate in down-trends without requiring the up-trend assumption to hold across all symbols.
- F2 (rotation) was rejected at DRAFT: 2-symbol rotation is binary; expected ~28 trades over 4.6 years; fails K9 with high probability before the diagnostic even completes.
- F3 (vol-targeted basket) was rejected at DRAFT: tests sizing not signal; would essentially re-run B006_002's vol-targeting logic on a 2-asset basket without a structural break from prior B006_NNN line.
- F4 (carry / term-structure) was rejected at DRAFT: requires basis / front-month-next-month data beyond ohlcv-1d; out of scope for the Databento ingest budget on this first cycle.

The DRAFT explicitly does NOT propose F2/F3/F4 as alternatives; the operator MAY override the F1 selection at SEAL turn by typing an explicit revision authorization. Default at SEAL is "confirm F1 as drafted."

## 2. Why the chosen family is not rescuing s7 or s9

The family-park memo (T8) section 5 imposes a first-principles burden: any "next" candidate on or after the SPY/TLT/GLD/USO 2014-2022 universe park must address BOTH the s7 D1 (cost-stress sensitivity destroys S0 edge) and s9 (negative S0 edge before any cost friction) failure modes. F1 on the MNQ+MGC futures basket satisfies this burden as follows:

### 2.1 F1 is not a rescue of s7 D1

| s7 D1 failure feature | F1 on MNQ+MGC treatment |
|---|---|
| Donchian-55 entry / Donchian-20 exit (low frequency) | F1 entries at moderate N (e.g., N=20 entry / N=10 exit; DRAFT_AMBIGUITY) -> higher trade density; explicit K9 buffer |
| Pyramid +0.5N up to 4 units | LOCKED single contract per symbol per signal; no pyramid; `no_pyramid_per_signal` runtime invariant |
| 2N ATR stop | inherits 2N ATR stop conceptually but ATR window subject to DRAFT_AMBIGUITY (default ATR(20)) |
| Universe = SPY/TLT/GLD/USO ETF proxies (4 symbols, yfinance vendor) | Universe = MNQ.c.0 + MGC.c.0 (2 symbols, Databento `GLBX.MDP3` vendor); F1 is NOT operating on the universe that empirically failed |
| Cost model: per-share commission + bps slippage on ETFs | LOCKED per-contract commission + tick-based slippage on futures; structurally different cost surface; the s7 D1 cost-stress sensitivity does not transfer 1:1 to per-contract micro futures |
| K12 fired (DR2 + DR3) | DR2 + DR3 evaluated independently here on the futures cost matrix; verdict driven by the futures-specific cost-stress, not by the ETF-proxy cost-stress |

F1 on MNQ+MGC is therefore a different candidate on a different universe with a structurally different cost model. It does NOT rebadge s7 D1.

### 2.2 F1 is not a rescue of s9

| s9 failure feature | F1 on MNQ+MGC treatment |
|---|---|
| RSI(2) <10 entry / >50 exit (mean-reversion family) | F1 is trend-following (Donchian breakout); the mechanic family is structurally orthogonal -- mean-reversion buys oversold-bounces, trend buys breakouts; the two are explicitly opposite-direction signals |
| Long-only | F1 is bi-directional (long + short); addresses the s7 D1 / s9 per-symbol concentration pathology |
| Edge at S0 was negative (-$1211 on $100k over 414 trades) | F1's S0 edge sign is an OPEN question to be answered by the diagnostic, NOT an assumed positive. The K1+K2 pre-registration applies: if F1 also shows K1+K2 fire on this universe, the verdict is PARKED_SAFE_BUT_NOT_MONEY_PROVEN by design |
| Universe = SPY/TLT/GLD/USO ETF proxies | Universe = MNQ.c.0 + MGC.c.0; F1 is NOT operating on the universe that empirically failed |
| Connors-canonical no filter / no regime / no asset selection | F1 carries no filter / no regime / no asset selection BYTE-EQUIVALENT (per family-park R7 reject-fast: silent filter introduction is forbidden) |
| 414 trades over IS (clears K9) | F1 expects 100-300 portfolio trades over IS; both candidates clear K9; F1 is NOT relying on more trades than s9 to rescue an edge |

F1 on MNQ+MGC is in a structurally different mechanic family (trend) on a structurally different universe (futures) with a structurally different cost model. It does NOT rebadge s9. The first-principles burden of the family-park memo is satisfied.

## 3. Universe (LOCKED at SEAL with operator confirmation)

| Field | LOCKED value (DRAFT) |
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

## 4. Dataset (LOCKED at SEAL)

| Field | LOCKED value (DRAFT) |
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
| Records expected per symbol per day | 1 (daily bar) |
| Fields | `ts_event`, `open`, `high`, `low`, `close`, `volume` |
| Intraday schemas (1s / 1m / 1h) | DEFERRED to a possible follow-up cycle; out of scope for this DRAFT |

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

## 8. Data availability assumptions and DR gates

### 8.1 Assumptions verified by S10-D1 probe

- `MNQ.c.0` returns >= 1,300 records on 2019-05-13 and 1,380 records (full CME Globex session) by 2021-07-19 on `ohlcv-1m` schema; the equivalent `ohlcv-1d` schema is expected to return 1 record per trading day over the IS window with no gaps.
- `MGC.c.0` is available across the full IS+OOS window per the S10-D1 probe (which used 1m schema; daily schema equivalence is asserted at SEAL).
- `MCL.c.0` is NOT in the universe; the candidate is structurally insulated from MCL's pre-2021 availability gap.

### 8.2 DR9 -- data continuity integrity check (REDEFINED for this universe at SEAL)

| Threshold | Locked value (DRAFT) |
|---|---|
| `DR9_MIN_PCT_EXPECTED_TRADING_DAYS` | **`0.95`** (carried byte-equivalent from B006_001/B006_002) |
| `DR9_MAX_CONSECUTIVE_ABS_LOG_RETURN` | **`0.30`** (carried byte-equivalent; tightens may apply to futures gap risk; DRAFT_AMBIGUITY) |
| `DR9_MAX_MISSING_OBSERVATIONS` | **`5`** per symbol over IS+OOS |
| `DR9_MAX_CONSECUTIVE_VIOLATION_THRESHOLD` | **`5`** |
| Trigger conditions | (a) gap > 5 trading days on either symbol; OR (b) > 5 missing observations on either symbol; OR (c) two consecutive abs(log_return) > 0.30 on either symbol; OR (d) any `Open/High/Low/Close <= 0` on either symbol |
| Severity if fired | `INCONCLUSIVE_HOLD` |
| `no_dr9_redefinition_post_seal` invariant | TRUE |

### 8.3 DR rules adapted for this candidate (LOCKED at SEAL)

| Rule | Trigger | Severity | Carried from |
|---|---|---|---|
| DR1 | `oos_rebalance_count < 36` (or equivalent for chosen frequency; DRAFT_AMBIGUITY) | `INCONCLUSIVE_HOLD` | s7 D1 / s9 / B006_002 |
| DR2 | `oos_metrics_degrade_materially_under_cost_stress` (S0 sharpe > 0 AND (S2 OR S3 degrades > 50%)) | `REJECT_FAST` | s7 D1 K12 component |
| DR3 | `zero_cost_only_survival` (S0 > 0 AND all S1/S2/S3 <= 0) | `REJECT_FAST` | s7 D1 K12 component |
| DR4 | `oos_negative_while_is_positive_unexplained` | `REJECT_FAST` | s7 D1 / B006_002 |
| DR5 | `cost_stress_turns_edge_negative` (tier flip) | `REJECT_FAST` / `INCONCLUSIVE_HOLD` (carveout) | s7 D1 / B006_002 |
| DR6 | `post_warmup_sizing_ambiguity_or_invalid` (NARROWED post-warmup only) | `REJECT_FAST` | B006_002 LESSON_B006_001_003 |
| DR7 | `missing_oos_or_date_window_evidence` | `INCONCLUSIVE_HOLD` | s7 D1 / B006_002 |
| DR8 | `live_or_order_routing_path_detected` at Initialize | `HARD_FAIL_VOIDED` | B006_002 |
| DR9 | `mnq_mgc_data_continuity_integrity_check` (REDEFINED per 8.2) | `INCONCLUSIVE_HOLD` | s7 D1 (REDEFINED) |
| DR10 | `turnover_cost_explosion` (`annual_turnover > 0.50` OR `S2 cost drag > 0.05`) | `REJECT_FAST` | s7 D1 / B006_002 |

DR11 (`c4_leverage_cap_bound_rate_exceeded`) is NOT carried for F1 because F1 does NOT use a leverage cap (single-contract per signal makes the leverage-cap-bound concept structurally inapplicable). DR11 would only carry if F3 were selected instead of F1.

DR precedence chain (LOCKED at SEAL; DRAFT_AMBIGUITY for exact order): proposed `DR7 -> DR1 -> DR9 -> DR10 -> DR6 -> DR4 -> DR2 -> DR3 -> DR5`. First fire wins.

## 9. Cost stress from day 1 (LOCKED at SEAL)

The cost-stress matrix S0/S1/S2/S3 is locked in the FIRST IS diagnostic; deferral to a follow-up cycle is forbidden by the family-park memo R8 and the s7 D1 K12 lesson.

### 9.1 Cost tiers (futures-specific)

| Tier | Label | Commission per contract USD | Slippage ticks one-way |
|---|---|---|---|
| S0 | `source_or_default` | 0.00 | 0.0 |
| S1 | `futures_low_slippage` | **`0.85`** (typical micro futures) | **`0.5`** |
| S2 | `futures_mid_slippage` | 0.85 | **`1.5`** |
| S3 | `futures_high_slippage` | 0.85 | **`3.0`** |

### 9.2 Tick / contract specs (LOCKED at SEAL; subject to operator verification against CME contract specs at SEAL)

| Symbol | Tick size | Dollar per tick | Notes |
|---|---|---|---|
| `MNQ.c.0` | 0.25 index points | **$0.50 per contract** | Micro E-mini Nasdaq-100 |
| `MGC.c.0` | 0.10 dollars/oz | **$1.00 per contract** (10-oz contract) | Micro Gold |

### 9.3 Pre-registered S0 edge sign and magnitude

Per `LESSON_B006_002_002` (favorable economic numbers do not override fail-closed verdicts by design), the operator pre-registers the expected S0 edge sign before the SEAL turn locks the spec:

**S0 edge sign and magnitude pre-registration (DRAFT_AMBIGUITY for operator confirmation at SEAL):**

| Field | DRAFT-proposed value |
|---|---|
| Expected S0 net PnL sign | open question (no a-priori claim; the s9 lesson is explicit that diversification does NOT rescue edge; F1 on futures is a genuine test) |
| Acceptance threshold S0 net PnL | `> 0` after 100+ trades |
| Acceptance threshold S1 net PnL | `> 0` after 100+ trades (K1 / K2 fire if `<= 0`) |
| Pre-registered max-drawdown tolerance | `<= 30%` of `START_CASH_USD` (looser than B006_002's `-25%` because futures inherently have higher leverage; DRAFT_AMBIGUITY) |
| Pre-registered cost-stress survival | S0/S1/S2/S3 all positive Sharpe (C5+) -> `ELIGIBLE_FOR_HUMAN_REVIEW`; S0/S1 positive but S2/S3 degrade > 50% -> `K12` REJECT_FAST |

## 10. Sample-size / K9 rules (LOCKED at SEAL)

| Field | LOCKED value (DRAFT) |
|---|---|
| K9 threshold | `total_closed_trades >= 100` over IS window |
| Expected trade count for F1 Donchian-20/10 bi-directional on 2 micros over 4.6 years | **100-300 portfolio trades** (estimated; actual subject to diagnostic outcome) |
| Per-symbol minimum | `>= 30 closed trades per symbol` over IS window (DRAFT_AMBIGUITY: relaxes s7 D1's per-symbol-10 to a stricter per-symbol-30 because 2-symbol basket has fewer per-symbol-degrees-of-freedom) |
| K9 buffer rationale | F1 at moderate Donchian-N produces ~1-3 entries/symbol/month on micros; 4.6 years * 12 months/year * 2 symbols * (1-3 entries) = 110-330 entries; comfortably above 100 |
| Trade density justification at DRAFT | F1 was explicitly chosen over F2 (rotation) and F3 (vol-targeted basket) BECAUSE rotation/vol-target on 2 symbols would not clear K9 |
| If K9 fires anyway | verdict path is `DR1 INCONCLUSIVE_HOLD` (not REJECT_FAST); candidate is then archived under INCONCLUSIVE_HOLD without modification |

## 11. Diversification expectations (LOCKED at SEAL)

| Field | LOCKED value (DRAFT) |
|---|---|
| `A7_effective_independent_bets_min` | **`1.5`** (lowered from s7 D1's 2.5 for 2-symbol basket; documented and locked at SEAL) |
| `K10_avg_pairwise_dependence_max` | **`0.50`** (carried byte-equivalent from s7 D1 / s9) |
| Asset family count | 2 distinct families (equity-index MNQ + metals MGC); DV1 first-principles-justification is "deliberate scope-limit on first cycle Databento ingest" |
| Per-symbol contribution distribution requirement | reported in compact summary; if one symbol contributes > 80% of profit OR > 80% of loss, flagged as suspect (carried from s7 D1 USO-only pattern and s9 USO-bears-loss pattern) |
| Diversification independence does NOT rescue edge | EXPLICITLY DISCLAIMED in spec (carried lesson from s9; LESSON_B006_002_002 reinforces) |
| Diversification finding from s7 D1 / s9 on 4-symbol ETF basket | NOT applicable to 2-symbol futures basket; this candidate measures its own diversification independently |

## 12. OOS locking policy (LOCKED at SEAL; carried byte-equivalent)

| Policy | Status |
|---|---|
| OOS data (`2024-01-02 -> 2025-12-30`) shall not be inspected, computed against, simulated over, or queried in any form during the in-sample diagnostic phase | LOCKED |
| Post-OOS data (`2026-01-02 onward`) is informational only; no diagnostic uses it | LOCKED |
| OOS inspection requires a separately authorized turn after IS verdict `ELIGIBLE_FOR_OOS` plus explicit operator approval | LOCKED |
| The loader / validator / signal / simulator / aggregator modules shall structurally enforce IS-only computation | LOCKED (`oos_inspection_blocked_at_in_sample` invariant) |

## 13. No-live / no-Strategy-Lab / no-brokerage policy (LOCKED at SEAL; carried byte-equivalent)

| Invariant | Value at runtime |
|---|---|
| `no_live_trading` | TRUE |
| `no_strategy_lab_promotion` | TRUE |
| `no_review_queue_mutation` | TRUE |
| `no_brokerage_connection` | TRUE |
| `no_external_network_at_runtime` | TRUE |
| `no_databento_at_runtime_only_at_explicit_ingest_phase` | TRUE |
| `no_production_signal` | TRUE |
| `no_strategy_optimization_authorized` | TRUE |
| `no_profitability_claim` | TRUE |
| `no_universe_membership_logic` | TRUE |
| `no_dr_redefinition_post_seal` | TRUE |
| `no_warmup_order_submission` (F1 has no warmup-period orders; carries from B006_002 byte-equivalent) | TRUE |
| `dr6_warmup_contamination_blocked` | TRUE |
| `no_b006_NNN_AND_s7_AND_s9_sealed_artifact_mutation` | TRUE |
| `no_continuous_roll_stitch_modification_post_seal` | TRUE |
| `no_mcl_inclusion_under_long_history_scope` | TRUE |
| `no_intraday_schema_ingest_under_daily_only_design` | TRUE |
| `databento_api_key_read_from_env_only_never_logged_or_saved` | TRUE |
| `no_pyramid_per_signal` (F1-specific) | TRUE |

Total runtime invariants at SEAL: **19**. Operator confirms exact list at SEAL.

Trading remains `PAUSED` throughout the candidate's lifecycle. Live remains `BLOCKED_AT_6_GATES`. FRC `NEVER_GRANTED`. No verdict in the closed enum unlocks live; the `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` advisory label is permanent for this candidate independent of any future verdict.

## 14. Reject-fast criteria (LOCKED at SEAL; mirrors family-park memo section 6)

The candidate is REJECTED FAST if ANY of:

- **RF1** Any DR rule fires `REJECT_FAST` (DR2 / DR3 / DR4 / DR5 / DR6 / DR10)
- **RF2** DR9 `mnq_mgc_data_continuity_integrity_failure` AND > 5 violations
- **RF3** DR6 post-warmup invalid-sizing event count > 0 (`REJECT_FAST` severity)
- **RF4** Any forbidden-verdict-token in runner output
- **RF5** Runner attempts `SetLiveMode` / `SetBrokerageModel` / `DeployAlgorithm` / unauthorized network call / unauthorized Databento call at runtime
- **RF6** Any order-submit attempt while in warmup window
- **RF7** Runner mutates any s7 D1 / s9 / B006_NNN / T8 family-park sealed artifact (byte-shift)
- **RF8** Runner makes a Databento API call outside the explicitly authorized Step 02b ingest phase
- **RF9** Runner caches `.dbn.zst` files outside the operator's explicit ingest directory
- **RF10** Runner accesses `DATABENTO_API_KEY` outside the explicitly authorized ingest phase
- **RF11** Track silently re-introduces a filter, regime gate, or selection rule that this DRAFT locked to NONE
- **RF12** Pyramid mechanism re-introduced in code (multi-contract pyramid)
- **RF13** Mechanic family silently switched from F1 to F2/F3/F4 post-SEAL
- **RF14** Track depends on a survivorship-cherry-pick selection rule (e.g., "pick best of N micros after the run")

K-gates (carried from s7 D1 / s9 byte-equivalent):

- **K1** `sharpe_proxy_per_trade_below_zero_at_S1`
- **K2** `expectancy_per_trade_dollars_nonpositive_at_S1`
- **K4** `trade_curve_max_drawdown_above_threshold` (DRAFT-proposed threshold 30% of `START_CASH_USD`)
- **K6** `per_symbol_observed_win_rate_dispersion_above_threshold`
- **K7** `silent_filter_introduction_after_lock`
- **K8** `runtime_safety_invariant_false`
- **K9** `closed_trades_below_100`
- **K10** `avg_pairwise_dependence_above_0_50`
- **K11** `cap_binding_events_above_threshold` (only if F3 were selected; not applicable to F1)
- **K12** composite cost-stress fail (DR2 + DR3)

K-gate firing priority order: `K8 > K12 > K6/K7 > K10 > K9 > K11 > K1/K2/K4 > A-gates > ELIGIBLE_FOR_OOS` (mirrors s9 byte-equivalent).

## 15. Validation gates

Validation gates the DRAFT-authoring turn satisfies:

- **V1** ASCII-only.
- **V2** Numbered sections in monotonic order (1..17).
- **V3** No execution language (no "seal the spec now"; no "fetch data now"; no "run the simulator now").
- **V4** No self-authorization (this DRAFT does NOT authorize the spec to be SEALed; only a separate operator turn does that).
- **V5** No code modification.
- **V6** No backtest run.
- **V7** No simulator run.
- **V8** No signal computation.
- **V9** No data fetch.
- **V10** No network IO.
- **V11** No live trading.
- **V12** No prior-phase artifact modification.
- **V13** The committed DRAFT file is the ONLY new file changed in this turn's commit.
- **V14** The brain_memory dirty `lessons.md` remains UNSTAGED and UNTOUCHED.
- **V15** Mechanic family RESOLVED to F1 in section 1; alternative F2/F3/F4 explicitly rejected at DRAFT.
- **V16** Family-park memo first-principles burden satisfied (section 2).

## 16. HALT conditions

- **H1** If any V-gate fails, the DRAFT-authoring turn HALTs.
- **H2** If the pre-stage git index is non-empty, the turn HALTs and remediates by unstaging contaminants before staging the DRAFT.
- **H3** If the staged file count is anything other than 1 at commit time, the turn HALTs and remediates.
- **H4** If the staged file is anything other than `docs/s10_d1_mnq_mgc_databento_long_history_tier_n_spec_DRAFT.md`, the turn HALTs and remediates.
- **H5** If the dirty `lessons.md` is accidentally staged, the turn HALTs and `git restore --staged brain_memory/projects/trading_bot/lessons.md` before retrying.
- **H6** If any prior-phase artifact (`docs/s10_d1_mnq_mgc_databento_long_history_tier_n_spec_plan.md`, `reports/external_research_hunter/t8_*.md`, `reports/external_research_hunter/t8_*.json`, `reports/external_research_hunter/s10_d1_micro_availability_probe_result_memo.{md,json}`, any s7 D1 / s9 / B006_NNN sealed artifact) is detected as modified, the turn HALTs and surfaces the drift.

DRAFT ambiguity register (for operator confirmation at SEAL turn; operator types option letter):

- **DA1** Donchian entry window N: A `20` (default; DRAFT recommended) / B `40` / C `55` (s7 D1 legacy; rejected by family-park burden, listed only for completeness)
- **DA2** Donchian exit window M: A `10` (default; symmetric to N=20) / B `20` (matches s7 D1 exit) / C `5` (faster cut)
- **DA3** ATR stop window: A `20` (default; DRAFT recommended) / B `14` (Wilder canonical) / C `10` (faster stop)
- **DA4** ATR stop multiplier: A `2.0` (default; s7 D1 byte-equivalent) / B `1.5` (tighter) / C `2.5` (looser)
- **DA5** Side: A `long_plus_short_bi_directional` (default; DRAFT recommended) / B `long_only` (rejected at DRAFT for per-symbol concentration concerns) / C `short_only` (rejected)
- **DA6** Per-trade risk percentage: A `1.0%` of portfolio equity (default; DRAFT recommended) / B `0.5%` (more conservative) / C `2.0%` (more aggressive; flagged for K4 risk)
- **DA7** Per-symbol contract cap: A `1` (default; LOCKED no_pyramid invariant) -- not negotiable
- **DA8** `DR9_MAX_CONSECUTIVE_ABS_LOG_RETURN` threshold: A `0.30` (default; carried from B006_002) / B `0.20` (tightened for futures gap risk; DRAFT_AMBIGUITY) / C `0.40` (loosened; rejected at DRAFT)
- **DA9** K4 max-drawdown threshold: A `0.30` (30% of `START_CASH_USD`; DRAFT recommended) / B `0.25` (B006_002 byte-equivalent; tighter) / C `0.50` (s7 D1 legacy; rejected at DRAFT)
- **DA10** Per-symbol minimum trade count: A `30` (default; DRAFT recommended; stricter than s7 D1's 10 for 2-symbol basket) / B `10` (s7 D1 legacy) / C `50` (stricter)
- **DA11** START_CASH_USD: A `100000` (default; B006_NNN / s7 D1 / s9 byte-equivalent) -- not negotiable
- **DA12** WARMUP_DAYS for the runner: A `MAX(longest_lookback_window, 220)` (default; B006 lineage carried) / B `MAX(longest_lookback_window, 60)` (tighter) -- LOCKED at SEAL
- **DA13** Output schema name: A `sparta.s10.mnq_mgc.trend_no_pyramid.diagnostic_run_report.v1` (default; DRAFT recommended) -- LOCKED at SEAL

The operator confirms DA1-DA13 at the SEAL turn by typing an explicit revision authorization (e.g., "Authorize s10 D1 MNQ+MGC Tier-N spec SEAL. Confirm all DRAFT ambiguities as default A.") or revises specific items as needed.

## 17. Next authorization language

A future operator authorization is required to proceed beyond this DRAFT. That authorization shall reference this DRAFT by exact path:

`docs/s10_d1_mnq_mgc_databento_long_history_tier_n_spec_DRAFT.md`

The next operator authorization in the established controller-session pattern shall use one of these scopes:

- **"Authorize s10 D1 MNQ+MGC Tier-N spec SEAL. Confirm all DRAFT ambiguities as default A."** -- begin the SEAL flow with DRAFT defaults accepted.
- **"Authorize s10 D1 MNQ+MGC Tier-N spec SEAL with revisions: DA1=B, DA3=C, ..."** -- begin the SEAL flow with specific DRAFT ambiguity revisions.
- **"Authorize alternative track selection plan revision only"** -- if the operator rejects this DRAFT in favor of a different track per `docs/next_research_track_selection_plan_after_s9_park.md` section 14.
- **"Authorize family-level park only without opening new track"** -- if the operator accepts the T8 family-park memo as sufficient consolidation and chooses NOT to advance this candidate.
- **"Authorize cross-domain pivot only"** -- if the operator pivots to a different project entirely.

This DRAFT is the source of truth for the s10 D1 MNQ+MGC Databento long-history Tier-N spec at DRAFT time. Future SEAL / BUILD / FETCH / RUN phases that contradict this DRAFT require either a fresh DRAFT revision (authored under separate authorization) or an out-of-band justification.

No phase of this chain confers any standing authorization for live trading, brokerage connection, Strategy Lab promotion, OOS inspection, or production candidate registration. Each remains BLOCKED at separate phases. Trading remains `PAUSED`. Live remains `BLOCKED_AT_6_GATES`. FRC `NEVER_GRANTED`.

----

End of DRAFT. Plan / spec DRAFT only. No code. No backtest. No simulator. No signal. No data fetch. No yfinance. No Yahoo Finance. No Databento. No DATABENTO_API_KEY access. No QC. No LEAN. No brokerage. No real order. No paper order. No Strategy Lab promotion. No review_queue mutation. No production idea_memory mutation. No ORB branch mutation. No lessons.md modification or staging. No live trading. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES.
