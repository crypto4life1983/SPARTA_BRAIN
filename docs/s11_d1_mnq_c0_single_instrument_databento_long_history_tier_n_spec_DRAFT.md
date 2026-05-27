# s11 D1 MNQ.c.0 Single-Instrument Databento Long-History -- Tier-N Specification DRAFT

Status: DRAFT (not sealed; operator confirms DRAFT ambiguities DA1-DA13 at SEAL; no code, no fetch, no run by this DRAFT).
Authored: 2026-05-27
Authorization: "Authorize s11 D1 MNQ.c.0 single-instrument Tier-N spec DRAFT."

Plan source: `docs/s11_d1_mnq_c0_single_instrument_databento_long_history_tier_n_spec_plan.md` (sha256 to-be-pinned-at-SEAL; committed at `488579e`)
Selection-plan source: `docs/next_research_track_selection_plan_after_s10_d1_park.md` (committed at `556ab3f`)
Predecessor parked candidate (read-only): `s10-d1-cross-asset-trend-or-meanrev-mnq-mgc-databento-long-history` parked `INCONCLUSIVE_HOLD` at commit `1a9acec`.
Audit-clean data anchor (MNQ.c.0): `data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_c_0_ohlcv_1d_20190513_20251230.csv` (sha256 `8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e`)

HARD BOUNDARIES (held by this DRAFT). Plan / spec DRAFT only. No strategy code. No backtest. No simulator. No signal computation. No data fetch. No yfinance / Yahoo Finance call. No Databento call. No DATABENTO_API_KEY access. No QC / LEAN call. No network IO. No review_queue.json mutation. No production idea_memory mutation. No Strategy Lab run. No candidate promotion. No s10 D1 / s9 / s7 D1 / B006_NNN sealed-artifact modification. No ORB branch artifact mutation. No Step 30 cost constant mutation. No CLAUDE.md modification. No docs/decisions.md modification. No RUNBOOK modification. No pipeline_manifest modification. No .gitignore modification. No `brain_memory/projects/trading_bot/lessons.md` modification or staging. No branch change. No branch creation. No git push. No live trading. No profitability claim. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES. FRC never granted.

----

## 1. Mechanic family choice -- RESOLVED to F1 trend-no-pyramid

The Tier-N spec PLAN section 8 enumerated four mechanic-family options: F1 trend-no-pyramid, F2 vol-targeting, F3 RSI mean-reversion, F4 carry / term-structure. This DRAFT RESOLVES the family to:

**F1 -- Long+Short Bi-Directional Donchian-N Trend, No Pyramid, ATR(P)-Based Stop, Single MNQ.c.0 Contract Per Signal.**

Rationale at DRAFT time (subject to operator confirmation or revision at SEAL):

- **F1 is the s10 D1 sealed mechanic on the audit-clean leg.** s10 D1's sealed Tier-N spec (commit `9040429`) locked F1 as the multi-symbol mechanic. s10 D1 was parked at the Step 02c audit phase due to MGC.c.0's DR9 fire -- the F1 signal logic on MNQ.c.0 was NEVER executed. This DRAFT proposes to test what was structurally locked but operationally untested.
- **F1 single-instrument scope is structurally compatible** with the sealed s10 D1 F1 mechanic byte-equivalent, removing the second-symbol coordination logic. The Donchian entry/exit, ATR stop, bi-directional sizing, no-pyramid invariant, and per-signal contract cap all carry without modification.
- **F2 was rejected at DRAFT** because monthly vol-targeting rebalance on a single instrument produces ~55 trades over 4.6 years IS, well below the K9 = 100 floor. F2 would force `INCONCLUSIVE_HOLD` on DR1 before any edge claim can be evaluated. The K9 fire is a structural failure mode, not a strategy verdict.
- **F3 was rejected at DRAFT** because the s9 ETF-proxy result (`PARKED_SAFE_BUT_NOT_MONEY_PROVEN`, negative S0 edge over 414 trades) carries an explicit framework lesson against mean-reversion at canonical parameters on cleanly-trending instruments. MNQ.c.0 over 2019-2023 spans a strongly upward-trending equity-index regime; an unfiltered RSI(2) <10 entry / >50 exit mechanic on MNQ is structurally biased against the regime. The first-principles burden for surviving where s9 failed is higher than F1's burden for surviving where s7 D1's pyramid-failure mode is structurally absent.
- **F4 was rejected at DRAFT** because carry / term-structure mechanics require basis or next-month-contract data beyond the audit-clean `ohlcv-1d` CSV. The data-scope friction is incompatible with the "zero-fresh-fetch" property that motivated T1's selection-plan recommendation in the first place.

The operator MAY override F1 at the SEAL turn by typing an explicit revision (e.g., "Authorize s11 D1 MNQ.c.0 Tier-N spec SEAL with revisions: family=F3"). Default at SEAL is "confirm F1 as drafted."

## 2. Why F1 on MNQ.c.0-only is not rescuing s7 D1, s9, B006_001/002, s10 D1

The s10 D1 family-park memo (T8, commit `5c13821`) and prior parking discipline require any forward candidate to satisfy the first-principles burden against each prior parked failure. F1 on MNQ.c.0-only satisfies the burden as follows:

### 2.1 F1 is not a rescue of s7 D1 (Donchian + pyramid on ETF-proxy)

| s7 D1 failure feature | F1 on MNQ.c.0-only treatment |
|---|---|
| Donchian-55 entry / Donchian-20 exit (low frequency) | Default F1 here is Donchian-N=20 / M=10 (DRAFT_AMBIGUITY DA1/DA2; faster signal -> higher trade density to mitigate K9 risk) |
| Pyramid +0.5N up to 4 units | LOCKED single contract per signal; `no_pyramid_per_signal` runtime invariant |
| 2N ATR stop | inherits ATR-based stop conceptually; DRAFT_AMBIGUITY DA3 (P=20) and DA4 (multiplier K=2.0) |
| Universe = 4-ETF basket (yfinance vendor) | Universe = `{MNQ.c.0}` only (Databento vendor); F1 is NOT operating on the parked universe |
| Cost: per-share commission + bps slippage on ETFs | LOCKED per-contract commission + tick-based slippage on micro futures (carried byte-equivalent from s10 D1) |
| K12 fired (DR2 + DR3) | DR2 + DR3 evaluated independently on the futures cost matrix; verdict driven by futures-specific cost-stress, not by ETF-proxy cost-stress |

### 2.2 F1 is not a rescue of s9 (RSI-2 mean-reversion on ETF-proxy)

| s9 failure feature | F1 on MNQ.c.0-only treatment |
|---|---|
| RSI(2) <10 / >50 (mean-reversion family) | F1 is trend-following (Donchian breakout); the mechanic family is structurally orthogonal -- breakout entries are the OPPOSITE direction of mean-reversion oversold-bounce entries |
| Long-only | F1 is bi-directional (long + short) by DRAFT default DA5 |
| Edge at S0 was negative (-$1211 over 414 trades) on ETF-proxy | F1's S0 edge sign is an OPEN question; the diagnostic falsifies it cleanly via K1+K2 if negative |
| Universe = SPY/TLT/GLD/USO ETF-proxy | Universe = `{MNQ.c.0}` only; structurally different |

### 2.3 F1 is not a rescue of B006_001 or B006_002 (SPY vol-targeting)

| B006 failure feature | F1 on MNQ.c.0-only treatment |
|---|---|
| Vol-targeting realized-vol sizing | F1 is signal-driven (Donchian breakout), NOT sizing-driven; different mechanic family |
| Single instrument SPY (equity ETF) | Single instrument MNQ.c.0 (micro futures); different asset class; different cost structure (per-share -> per-contract; bps -> ticks); different leverage mechanics (cash equity -> margin futures) |
| C4 leverage-cap-bound rate exceeded 10% on SPY | F1 has NO leverage cap (single contract per signal; per-trade risk sized via ATR stop). DR11 is structurally absent for this candidate. The B006_002 C4-violation pattern cannot recur because the binding mechanism doesn't exist in F1. |

### 2.4 F1 is not a rescue of s10 D1 MNQ+MGC

| s10 D1 failure feature | F1 on MNQ.c.0-only treatment |
|---|---|
| Universe = `{MNQ.c.0, MGC.c.0}` | Universe = `{MNQ.c.0}` only; MGC.c.0 explicitly excluded by sealed spec PLAN |
| MGC continuous-stitch DR9 fire (8 strict gaps / 7 holiday-aware) | MGC structurally absent; the DR9 failure mode cannot recur |
| Tier-N spec was sealed with F1 mechanic | This DRAFT preserves F1 mechanic byte-equivalent on the audit-clean leg only |
| Operationally untested signal logic | This DRAFT proposes to operationally test the F1 signal logic that s10 D1 sealed but never ran |

F1 on MNQ.c.0-only satisfies all four first-principles-burden requirements. The candidate is **structurally fresh**, not a revision of any predecessor.

## 3. Universe (LOCKED at SEAL with operator confirmation)

| Field | LOCKED value (DRAFT) |
|---|---|
| Universe type | `single_fixed_instrument_continuous_micro_futures` |
| Symbol 1 (only symbol) | **`MNQ.c.0`** (Micro E-mini Nasdaq-100, continuous front-month) |
| `AddUniverse` calls | **0** (structurally absent) |
| `removed_from_universe` events | **0** (structurally absent) |
| Symbol count | exactly 1 |
| Symbol substitution clause at later phases | FORBIDDEN (LOCKED at SEAL via `single_instrument_universe_NO_widening_post_seal` invariant) |
| Universe widening at later phases | FORBIDDEN (any wider basket requires a fresh candidate id) |
| Common-history start (verified by s10 D1 audit) | **2019-05-13** |
| Universe-membership integrity surface | structurally N/A |
| Diversification claim by this candidate | NONE (single-instrument; explicit first-principles justification) |

## 4. Dataset (LOCKED at SEAL)

| Field | LOCKED value (DRAFT) |
|---|---|
| Vendor | **Databento Historical API** (vendor-level; controller-side never calls) |
| Dataset | **`GLBX.MDP3`** |
| Schema | **`ohlcv-1d`** |
| `stype_in` | **`continuous`** |
| Symbol requested | `["MNQ.c.0"]` |
| Re-use of existing audit-clean CSV | **TRUE** -- MNQ.c.0 CSV at `data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_c_0_ohlcv_1d_20190513_20251230.csv` (sha256 `8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e`) is reused byte-equivalent. ZERO new Databento call required. |
| Step 02b for this candidate | manifest cross-link only |
| API key handling | NOT REQUIRED at any phase of this candidate |
| Controller-side Databento call | LOCKED OFF at every phase |

## 5. Schema (LOCKED at SEAL)

| Field | LOCKED value |
|---|---|
| Schema | `ohlcv-1d` |
| Records expected per trading day | 1 (daily bar) |
| Fields | `ts_event`, `open`, `high`, `low`, `close`, `volume` |
| Intraday schemas | OUT OF SCOPE for this Tier-N |

## 6. stype_in (LOCKED at SEAL)

| Field | LOCKED value |
|---|---|
| `stype_in` | `continuous` |
| Continuous roll stitch | Databento native continuous-front-month synthesis |
| `no_continuous_roll_stitch_modification_post_seal` invariant | TRUE |

## 7. IS / OOS windows (LOCKED at SEAL)

| Field | LOCKED value |
|---|---|
| **IS window start** | **`2019-05-13`** |
| **IS window end** | **`2023-12-29`** |
| IS window length | ~4.6 years |
| MNQ.c.0 IS row count (audit-confirmed by s10 D1) | **1,443** (`is_pct_observed = 1.2365` PASS) |
| **OOS window start (never inspected at IS)** | **`2024-01-02`** |
| **OOS window end (never inspected at IS)** | **`2025-12-30`** |
| OOS window length | ~2 years |
| MNQ.c.0 OOS row count (structural only; NO return analysis) | **622** |
| Post-OOS data | `2026-01-02 onward` (informational only) |
| OOS inspection at IS-phase | FORBIDDEN (`oos_inspection_blocked_at_in_sample` invariant) |

## 8. Data availability assumptions and DR gates

### 8.1 Assumptions inherited from s10 D1 audits (commits `9bdde45` strict + `0e124e3` holiday-aware)

- `MNQ.c.0` over `2019-05-13 -> 2025-12-30` is **DR9-clean under both audit variants** (0 calendar gaps > 5 days; 0 consecutive abs-log-return > 0.30 violations; max single-day abs-log-return 0.1164; `is_pct_observed = 1.2365` PASS).
- DR9 for this candidate is structurally redefined as `mnq_c0_only_data_continuity_integrity_check`; thresholds carried byte-equivalent (`0.95` / `0.30` / `5` / `5`).
- The audit-clean status is already established; Step 02c for this candidate is a re-confirmation pass against the same CSV (no fresh Databento call).

### 8.2 DR rules adapted for single-instrument F1 (LOCKED at SEAL)

| Rule | Trigger | Severity | F1-single-instrument note |
|---|---|---|---|
| DR1 | `oos_rebalance_count < 36` (OOS phase only) | `INCONCLUSIVE_HOLD` | OOS-only; not evaluated at IS |
| DR2 | `oos_metrics_degrade_materially_under_cost_stress` | `REJECT_FAST` | unchanged |
| DR3 | `zero_cost_only_survival` | `REJECT_FAST` | unchanged |
| DR4 | `oos_negative_while_is_positive_unexplained` | `REJECT_FAST` | OOS-only |
| DR5 | `cost_stress_turns_edge_negative` (tier flip) | `REJECT_FAST` / `INCONCLUSIVE_HOLD` carveout | unchanged |
| DR6 | `post_warmup_sizing_ambiguity_or_invalid` (NARROWED post-warmup only) | `REJECT_FAST` | unchanged; carried from B006_002 |
| DR7 | `missing_oos_or_date_window_evidence` | `INCONCLUSIVE_HOLD` | unchanged |
| DR8 | `live_or_order_routing_path_detected` at Initialize | `HARD_FAIL_VOIDED` | unchanged |
| **DR9** | **`mnq_c0_only_data_continuity_integrity_check`** | `INCONCLUSIVE_HOLD` | redefined for single-instrument; MNQ-only audit-clean; MGC failure mode structurally absent |
| DR10 | `turnover_cost_explosion` (`annual_turnover > 0.50` OR `S2 cost drag > 0.05`) | `REJECT_FAST` | unchanged |
| DR11 | NOT IN CHAIN | -- | F1 has no leverage cap; DR11 is structurally absent |

DR precedence chain (DRAFT default; LOCKED at SEAL): `DR7 -> DR1 -> DR9 -> DR10 -> DR6 -> DR4 -> DR2 -> DR3 -> DR5` (carried byte-equivalent from s10 D1 minus DR11).

## 9. Cost stress from day 1 (LOCKED at SEAL)

Cost-stress matrix S0/S1/S2/S3 LOCKED in the first IS diagnostic; deferral forbidden.

### 9.1 Cost tiers (futures-specific; identical to s10 D1)

| Tier | Label | Commission per contract USD | Slippage ticks one-way |
|---|---|---|---|
| S0 | `source_or_default` | 0.00 | 0.0 |
| S1 | `futures_low_slippage` | **`0.85`** | **`0.5`** |
| S2 | `futures_mid_slippage` | 0.85 | **`1.5`** |
| S3 | `futures_high_slippage` | 0.85 | **`3.0`** |

### 9.2 Tick / contract specs (LOCKED at SEAL)

| Symbol | Tick size | Dollar per tick |
|---|---|---|
| `MNQ.c.0` | 0.25 index points | **$0.50 per contract** |

### 9.3 Pre-registered S0 edge sign and magnitude (DRAFT_AMBIGUITY for operator confirmation at SEAL)

| Field | DRAFT-proposed value |
|---|---|
| Expected S0 net PnL sign | open question (no a-priori claim) |
| Acceptance threshold S0 net PnL | `> 0` after >= 100 trades |
| Acceptance threshold S1 net PnL | `> 0` (K1 / K2 fire if `<= 0`) |
| Pre-registered max-drawdown tolerance | `<= 30%` of `START_CASH_USD` (DRAFT_AMBIGUITY DA8) |
| Pre-registered cost-stress survival | all four cost tiers OOS Sharpe > 0 -> `ELIGIBLE_FOR_HUMAN_REVIEW`; all > 0.5 -> `REQUEST_FULL_PREREGISTRATION_REVIEW`; DR2/DR3 fire -> `REJECT_FAST` |

## 10. Sample-size / K9 rules (LOCKED at SEAL)

| Field | LOCKED value (DRAFT) |
|---|---|
| K9 threshold | `total_closed_trades >= 100` over IS window |
| Expected trade count for F1 Donchian-20/10 bi-directional on MNQ.c.0 over 4.6y IS | **50-150 portfolio trades** (estimated; subject to Step 06 simulator) |
| K9 risk | **borderline** -- operator may wish to revise DA1/DA2 to Donchian-15/8 at SEAL to mitigate; DRAFT default is 20/10 |
| Per-symbol minimum | NOT APPLICABLE for single-instrument; K9 IS the per-symbol minimum |
| If K9 fires anyway | `DR1 INCONCLUSIVE_HOLD` (not REJECT_FAST); candidate archived without parameter modification |

## 11. Diversification expectations -- single-instrument scope (LOCKED at SEAL)

| Field | LOCKED value |
|---|---|
| `A7_effective_independent_bets_min` | **NOT APPLICABLE** (trivially 1 by construction; removed from acceptance gate set) |
| `K10_avg_pairwise_dependence_max` | **NOT APPLICABLE** (no pairs; removed from K-gate set) |
| `K6_per_symbol_observed_win_rate_dispersion` | **NOT APPLICABLE** (no dispersion to measure) |
| Per-symbol contribution distribution | trivially 100% to MNQ.c.0; standalone risk profile IS the entire diagnostic |
| Diversification claim by this candidate | **NONE** -- explicit first-principles single-instrument justification: "the s10 D1 MNQ-clean-leg is the only structurally-useful finding preserved by the parked candidate; test it on its own merits before extending to any multi-symbol design" |
| Disclaimer carried byte-equivalent | "Diversification independence does NOT imply positive edge" (LESSON_B006_002_002) -- applies trivially here |

## 12. OOS locking policy (LOCKED at SEAL; carried byte-equivalent)

| Policy | Status |
|---|---|
| OOS data shall not be inspected, computed against, simulated over, or queried during IS phase | LOCKED |
| Post-OOS data is informational only; no diagnostic uses it | LOCKED |
| OOS inspection requires a separately authorized turn after IS verdict `ELIGIBLE_FOR_OOS` + explicit operator approval | LOCKED |
| Modules shall structurally enforce IS-only computation | LOCKED (`oos_inspection_blocked_at_in_sample`) |

## 13. No-live / no-Strategy-Lab / no-brokerage policy (LOCKED at SEAL; carried byte-equivalent)

Total invariants at SEAL: **19** for F1 (no DR11; no C4 invariants).

7 inherited B005_NNN framework:
- `no_live_trading` · `no_strategy_lab_promotion` · `no_review_queue_mutation` · `no_brokerage_connection` · `no_external_network` · `no_databento_at_runtime` · `no_production_signal`

4 inherited B006_001:
- `no_strategy_optimization_authorized` · `no_profitability_claim` · `no_universe_membership_logic` · `no_dr_redefinition_post_seal`

2 inherited B006_002 (F1 doesn't use leverage cap; only the non-leverage-cap-specific invariants carry):
- `no_warmup_order_submission`
- `dr6_warmup_contamination_blocked`

3 inherited s10 D1-specific:
- `no_continuous_roll_stitch_modification_post_seal`
- `no_intraday_schema_ingest_under_daily_only_design`
- `databento_api_key_read_from_env_only_never_logged_or_saved` (vacuously true since no fresh Databento call required at any phase)

3 NEW s11-D1-specific (LOCKED at SEAL):
- `single_instrument_universe_NO_widening_post_seal`
- `no_substitution_of_any_symbol_into_this_universe_post_seal`
- `mnq_c0_csv_reuse_from_s10_d1_byte_equivalent_no_fresh_fetch`

Status surface (permanent for this candidate, independent of any future verdict):

| Field | Value |
|---|---|
| Trading | `PAUSED` |
| Live mode | `BLOCKED_AT_6_GATES` |
| FRC | `NEVER_GRANTED` |
| `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` | permanent |
| Six live-trading gates BLOCKED regardless of verdict | YES |

## 14. Reject-fast criteria (LOCKED at SEAL)

The candidate is REJECTED FAST if ANY of:

- **RF1** Any DR rule fires `REJECT_FAST` (DR2 / DR3 / DR4 / DR5 / DR6 / DR10)
- **RF2** DR9 `mnq_c0_only_data_continuity_integrity_failure` AND > 5 violations (extremely unlikely given s10 D1 audit-clean finding)
- **RF3** DR6 post-warmup invalid-sizing event count > 0
- **RF4** Any forbidden-verdict-token in runner output
- **RF5** Runner attempts `SetLiveMode` / `SetBrokerageModel` / `DeployAlgorithm` / unauthorized network call / unauthorized Databento call at runtime
- **RF6** Any order-submit attempt while in warmup window
- **RF7** Runner mutates any s10 D1 / s9 / s7 D1 / B006_NNN / T8 / s11 D1 sealed artifact (byte-shift)
- **RF8** Runner makes a Databento API call at any phase (controller-side; this candidate is "zero-fresh-fetch")
- **RF9** Runner caches `.dbn.zst` files anywhere
- **RF10** Runner accesses `DATABENTO_API_KEY` at any phase
- **RF11** Track silently re-introduces a filter, regime gate, or selection rule
- **RF12** Pyramid mechanism re-introduced in code
- **RF13** Mechanic family silently switched from F1 post-SEAL
- **RF14** Universe widening or symbol substitution attempted at any phase
- **RF15** Track depends on a survivorship-cherry-pick rule

K-gates carried byte-equivalent (with single-instrument simplifications):

- **K1** `sharpe_proxy_per_trade_below_zero_at_S1`
- **K2** `expectancy_per_trade_dollars_nonpositive_at_S1`
- **K4** `trade_curve_max_drawdown_above_threshold` (DA8 default 30%)
- **K6** NOT APPLICABLE (single-instrument)
- **K7** `silent_filter_introduction_after_lock`
- **K8** `runtime_safety_invariant_false`
- **K9** `closed_trades_below_100`
- **K10** NOT APPLICABLE (single-instrument)
- **K11** NOT APPLICABLE (no leverage cap for F1)
- **K12** composite cost-stress fail (DR2 + DR3)

K-gate firing priority order: `K8 > K12 > K7 > K9 > K1/K2/K4 > A-gates > ELIGIBLE_FOR_OOS`.

## 15. Validation gates

Validation gates the DRAFT-authoring turn satisfies:

- **V1** ASCII-only.
- **V2** Numbered sections in monotonic order (1..17).
- **V3** No execution language.
- **V4** No self-authorization (this DRAFT does NOT authorize SEAL; only a separate operator turn does that).
- **V5** No code modification.
- **V6** No backtest run.
- **V7** No simulator run.
- **V8** No signal computation.
- **V9** No data fetch.
- **V10** No network IO.
- **V11** No live trading.
- **V12** No prior-phase artifact modification.
- **V13** The committed DRAFT file is the ONLY new file in this turn's commit.
- **V14** The brain_memory dirty `lessons.md` remains UNSTAGED and UNTOUCHED.
- **V15** Mechanic family RESOLVED to F1 in section 1; F2/F3/F4 explicitly rejected at DRAFT.
- **V16** Single-instrument adaptations explicit (A7/K10/K6 NOT APPLICABLE; DR11 structurally absent).

## 16. HALT conditions + DRAFT ambiguity register

HALT conditions:

- **H1** If any V-gate fails, the turn HALTs.
- **H2** If pre-stage git index is non-empty, the turn HALTs.
- **H3** If staged file count is anything other than 1 at commit time, the turn HALTs.
- **H4** If staged file is anything other than `docs/s11_d1_mnq_c0_single_instrument_databento_long_history_tier_n_spec_DRAFT.md`, the turn HALTs.
- **H5** If `lessons.md` is accidentally staged, the turn HALTs and `git restore --staged brain_memory/projects/trading_bot/lessons.md` before retrying.
- **H6** If any prior-phase artifact (sealed spec / parked predecessors / Tier-N PLAN at `488579e`) is detected as modified, the turn HALTs.

### 16.1 DRAFT ambiguity register (for operator confirmation at SEAL; operator types option letter)

- **DA1** Donchian entry window N: A `20` (default; DRAFT recommended; gives 50-150 trades) / B `15` (faster; gives 80-200 trades; mitigates K9 risk) / C `10` (faster still; gives 150-300 trades)
- **DA2** Donchian exit window M: A `10` (default; symmetric to N=20) / B `8` (faster exit) / C `5` (much faster exit)
- **DA3** ATR stop window P: A `20` (default; DRAFT recommended) / B `14` (Wilder canonical) / C `10` (faster stop)
- **DA4** ATR stop multiplier K: A `2.0` (default; s10 D1 byte-equivalent) / B `1.5` (tighter) / C `2.5` (looser)
- **DA5** Side: A `long_plus_short_bi_directional` (default; DRAFT recommended) / B `long_only` / C `short_only` (rejected)
- **DA6** Per-trade risk percentage: A `1.0%` of portfolio equity (default) / B `0.5%` (more conservative) / C `2.0%` (more aggressive; flagged for K4 risk)
- **DA7** Per-signal contract cap: A `1` (default; LOCKED non-negotiable; `no_pyramid_per_signal`) -- not negotiable
- **DA8** K4 max-drawdown threshold: A `0.30` (30% of `START_CASH_USD`; DRAFT recommended) / B `0.25` (B006_002 byte-equivalent) / C `0.50` (s7 D1 legacy; rejected)
- **DA9** K9 minimum trade-count threshold: A `100` (default; LOCKED; carried from s10 D1; framework byte-equivalent) -- not negotiable
- **DA10** `START_CASH_USD`: A `100000` (default; LOCKED non-negotiable; B006/s10 D1 byte-equivalent) -- not negotiable
- **DA11** `WARMUP_DAYS`: A `MAX(longest_lookback, 220)` -> resolved to `220` (default; B006/s10 D1 lineage carried) -- LOCKED at SEAL
- **DA12** Output schema name: A `sparta.s11.mnq_c0.trend_no_pyramid.diagnostic_run_report.v1` (default; DRAFT recommended) -- LOCKED at SEAL
- **DA13** DR9 thresholds (carried byte-equivalent from s10 D1 sealed spec): A all four thresholds locked (`DR9_MIN_PCT_EXPECTED_TRADING_DAYS = 0.95`, `DR9_MAX_CONSECUTIVE_ABS_LOG_RETURN = 0.30`, `DR9_MAX_MISSING_OBSERVATIONS = 5`, `DR9_MAX_CONSECUTIVE_VIOLATION_THRESHOLD = 5`) -- not negotiable

The operator confirms DA1-DA13 at the SEAL turn by typing an explicit revision authorization (e.g., "Authorize s11 D1 MNQ.c.0 Tier-N spec SEAL. Confirm all DRAFT ambiguities as default A.") or revises specific items (e.g., "...Confirm DA1=B, DA2=B; all others as default A").

## 17. Next authorization language

A future operator authorization is required to proceed beyond this DRAFT. That authorization shall reference this DRAFT by exact path:

`docs/s11_d1_mnq_c0_single_instrument_databento_long_history_tier_n_spec_DRAFT.md`

The next operator authorization in the established controller-session pattern shall use one of these scopes:

- **"Authorize s11 D1 MNQ.c.0 Tier-N spec SEAL. Confirm all DRAFT ambiguities as default A."** -- begin the SEAL flow with DRAFT defaults accepted (F1 mechanic family LOCKED; Donchian-20/10; ATR-20 K=2.0; bi-directional; 1.0% risk; no pyramid; K4 30%; K9 100; START_CASH $100k; WARMUP 220; DR9 thresholds carried byte-equivalent).
- **"Authorize s11 D1 MNQ.c.0 Tier-N spec SEAL with revisions: DA1=B, DA2=B, ..."** -- begin the SEAL flow with specific DRAFT ambiguity revisions (e.g., faster Donchian-15/8 to mitigate K9 risk).
- **"Authorize alternative track selection plan revision only"** -- if the operator rejects F1 mechanic-family resolution and wants a fresh selection-plan revision.
- **"Authorize cross-domain pivot only"** -- if the operator pivots to a different project entirely.
- **"Defer / Pause trading-bot track"** -- if the operator holds the DRAFT on file without advancing.

This DRAFT is the source of truth for the s11 D1 MNQ.c.0 single-instrument candidate's intended Tier-N spec scope at DRAFT time. Future SEAL / BUILD / RUN phases that contradict this DRAFT require either a fresh DRAFT revision or an out-of-band justification.

No phase of this chain confers any standing authorization for live trading, brokerage connection, Strategy Lab promotion, OOS inspection, or production candidate registration. Each remains BLOCKED at separate phases. Trading remains `PAUSED`. Live remains `BLOCKED_AT_6_GATES`. FRC `NEVER_GRANTED`.

----

End of DRAFT. Plan / spec DRAFT only. No code. No backtest. No simulator. No signal. No data fetch. No yfinance. No Yahoo Finance. No Databento. No DATABENTO_API_KEY access. No QC. No LEAN. No brokerage. No real order. No paper order. No Strategy Lab promotion. No review_queue mutation. No production idea_memory mutation. No ORB branch mutation. No lessons.md modification or staging. No live trading. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES.
