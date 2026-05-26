# s7 D1 Cross-Asset Donchian - Step 07 Result-Aggregation Specification Plan

Status: PLAN_ONLY (build not yet authorized; execution requires a separately authorized turn).
Authored: 2026-05-25
BOUNDARY ALERT: THIRD-TIER boundary-crossing phase. Step 05 introduced channel/trigger code. Step 06 introduced position/sizing/stop/cost/ledger code. Step 07 introduces PORTFOLIO-LEVEL PERFORMANCE STATISTICS and the IS-CLOSE VERDICT (A1-A10 acceptance gates, K1-K11 rejection gates, K12/DR2/DR3/DR5 cost-stress fail-fast). The verdict is the first time the chain produces a PARK / REJECT_FAST / ELIGIBLE_FOR_OOS classification. This plan remains plan-only, in-sample-only, and contains no live-trading, no brokerage, no out-of-sample inspection, no Strategy Lab promotion, no review_queue mutation, and no auto-triggered OOS or post-aggregation execution.
Parent spec: docs/s7_d1_cross_asset_donchian_spec.md (sections 13 and 14 are the source of truth for A-gates and K-criteria)
Parent Step 06 build (simulator, verdict PASS): commit ecd03e5, build report sha256 cb826116c3a429fe341bc9d2c4b44a7e2312bb285f41bdd3a39baa7f78895254, seal db2b2e9a72d5713e0f44e1a9b44fb4ca59433db3211f3c0dc3ce40b0b4083a81
Parent Step 05 build (signal, verdict PASS): commit 25d262f, seal df0f28fa974868580e882ff364c3331d2feeab54d5d1d10c000e09c29701b4cc
Parent Step 04 build (validator, verdict PASS): commit a2ec179, seal 737a3f54b0a380e1c298a83a9fb8183b0fbdba23b42fa002a2b7fe0d9883ba3f
Parent Step 03 build (loader, verdict PASS): commit d7b2a0c, seal 89b2e14122113fa12a319c0b0d8331573aa3bca824a494c4b9e1a5a43601a80c
Step 02c audit (verdict PASS): commit 1b640d1, audit_manifest sha256 pin 794a9386abc68fdffe411e5a54534852293c8ba9c9c14fc4a2443c67a374bdcb
Naming convention: s7 D1 cross-asset Donchian yfinance proxy (alternate-vendor research track).

HARD BOUNDARIES (held by this plan). Plan only. No aggregation code. No simulator re-run. No backtest. No data fetch. No yfinance, Yahoo Finance, Databento. No DATABENTO_API_KEY access. No network IO. No OOS computation. No OOS inspection beyond structural counts already sealed in Step 04 / Step 05 / Step 06 reports. No OOS performance statistics. No live signal computation. No order creation. No brokerage connection. No paper order. No paper broker. No review_queue.json mutation. No production idea_memory mutation. No Strategy Lab run. No Strategy Lab promotion. No ORB branch artifact mutation. No Step 30 cost constant mutation. No existing source code modification. No tests modification. No CLAUDE.md modification. No docs/decisions.md modification. No RUNBOOK modification. No pipeline_manifest modification. No .gitignore modification. No branch change. No branch creation. No commit beyond the single new plan file. No git push. No live trading. No profitability claim. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES. FRC never granted.

----

## 1. Purpose

Define the canonical Python result-aggregation module for the s7 D1 cross-asset Donchian yfinance proxy research track. The module consumes one or more `SimulationResult` instances (typically four, one per cost tier S0/S1/S2/S3) from the Step 06 simulator and produces an `AggregationResult` carrying portfolio-level performance statistics, per-symbol breakdowns, the cost-stress matrix, K-criteria evaluation, A-gate evaluation, and the IS-close verdict per parent spec sections 13 and 14.

This module is where the chain first computes Sharpe-proxy-per-trade, expectancy, trade-curve max drawdown, win rate, per-market WR-gap vs P/L-implied breakeven, pairwise dependence measure across the four markets, and effective-independent-bets. It is also where the cost-stress fail-fast DR2 / DR3 / DR5 rules first execute. The output verdict is one of the spec-pinned status enums: `PARKED_FAILED_AT_INSUFFICIENT_SAMPLE`, `PARKED_SAFE_BUT_NOT_MONEY_PROVEN`, `PARKED_SAFETY_FAILED`, `PARKED_PROVENANCE_BROKEN`, `PARKED_FAILED_AT_DIVERSIFICATION_HYPOTHESIS`, `PARKED_CAP_BINDING`, `REJECT_FAST`, or `ELIGIBLE_FOR_OOS`.

The `ELIGIBLE_FOR_OOS` verdict does NOT auto-trigger any OOS work. It is a structural attestation that A1-A10 all pass on the in-sample matrix and no K-criterion fires; a separately authorized future operator turn is required to even consider OOS access.

## 2. Why Step 07 comes after Step 06 (and the third-tier boundary-crossing nature)

Step 06 sealed the simulator (verdict PASS at commit ecd03e5). The simulator produces a chronological trade ledger and an optional daily equity ledger over the in-sample window for a chosen cost tier. With the simulator in place, the next logical phase is the module that takes those ledgers and computes the verdict-grade statistics defined in spec sec 13 and sec 14.

Step 07 is the third-tier boundary-crossing phase. Step 05 introduced channel computation; Step 06 introduced position/sizing/stop/cost/trade-ledger; Step 07 introduces every remaining piece of the verdict vocabulary that the prior phases deliberately deferred:

- Sharpe-proxy-per-trade (A2 / K1).
- Expectancy per trade (A3 / K2).
- Trade-curve max drawdown (A4 / K4 cross-check; K4 also fires intra-simulator).
- Per-market win rate, P/L ratio, implied-breakeven win rate, win-rate-gap-vs-breakeven (A5).
- Validator pass-count (A6; this is an attestation that prior validator phases passed).
- Effective independent bets (A7) and average pairwise dependence measure (K10) -- both derived from the four-symbol daily-return matrix over the in-sample window.
- Cost-stress matrix across S0/S1/S2/S3 (A8), and DR2 / DR3 / DR5 fail-fast evaluation.
- Safety-template C1-C8 attestation (A9 / K6 / K7).
- Cap-binding events count (A10 / K11).
- Sealed-parent-drift attestation (K8; re-check every upstream sha256 pin matches what is now on disk).
- Trade sample size (A1 / K9).
- The verdict assembly per spec sec 13-14.

Each of these was forbidden in Step 06 by token grep. The Step 07 plan unblocks them STRUCTURALLY (the aggregator IS the statistics-and-verdict module) while keeping a different list of tokens forbidden: every live-trading and brokerage token, every OOS-simulation token, every parameter-optimization token, every filter / regime / asset-selection token, every vendor / credential / network token, and every production-integration (Strategy Lab / review_queue / idea_memory / scheduler / autopilot / FRC gate) token.

The IS-only enforcement is inherited TRANSITIVELY: the aggregator consumes simulator output, the simulator only produced IS trades (per Step 06 enforcement), and Step 07 additionally checks that every TradeUnit and DailyEquityPoint date in every consumed `SimulationResult` lies in `IN_SAMPLE_WINDOW`. The aggregator does NOT call the simulator with OOS dates. The aggregator does NOT read LoadedSymbol bars outside the in-sample window for any computation. The aggregator produces no OOS statistic.

The verdict `ELIGIBLE_FOR_OOS` is a structural attestation only. It does not change the chain's blocking posture. OOS inspection, Strategy Lab promotion, brokerage connection, and live trading all remain blocked at separate plans beyond Step 07; this plan does not pre-authorize any of those.

## 3. Inputs from prior phases

The aggregator depends on the public API surfaces of the Step 03 loader (for daily-return computation only) and the Step 06 simulator (the source of trade ledgers). The aggregator does NOT call the loader, validator, signal, or simulator itself; the caller is responsible for calling those in order and passing the results.

Locked input contract:

- `loaded: Mapping[str, LoadedSymbol]` (from `load_all()`); used by the aggregator ONLY for daily-return computation in pairwise-dependence and effective-independent-bets calculations. The aggregator reads `loaded.adj_close` and `loaded.dates` only; restricted to bars within `IN_SAMPLE_WINDOW`.
- `simulation_results: Mapping[str, SimulationResult]` keyed by cost-tier string (e.g., `{"S0": sim_s0, "S1": sim_s1, "S2": sim_s2, "S3": sim_s3}`); each `SimulationResult` produced by the Step 06 simulator at the corresponding `CostTier`. The map must contain at least the "S1" key (baseline mandatory); "S0", "S2", "S3" are mandatory for the cost-stress matrix per spec sec 13 A8.
- `safety_attestations: Mapping[str, bool]` carrying the Phase 2 C1-C8 contracts (for A9 / K6 / K7). The aggregator does not compute the C1-C8 contracts; the caller supplies them.

The aggregator does not accept `lookback=`, `window=`, `enable_oos=`, `optimize_=`, `tune_=`, or any other parameter that would relax the spec-pinned thresholds or window. The aggregator does not accept any kwarg outside the three pinned inputs.

## 4. Outputs the future build turn will create

The build turn for Step 07 shall create the following artifacts and no others:

- external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_aggregator/aggregator.py
- external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_aggregator/__init__.py (re-exports per section 7)
- external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_aggregator/README.md
- tests/external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_aggregator/test_aggregator.py
- tests/external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_aggregator/__init__.py
- reports/s7_d1_cross_asset_donchian_step_07_aggregator_build_report.json (sealed)
- reports/s7_d1_cross_asset_donchian_step_07_aggregator_build_report.md (companion)

No other files. No log files. No data files.

## 5. Files the build turn may create or modify later

- The seven output files in section 4.
- A temporary build script under scripts/ (suggested: scripts/_s7_d1_donchian_step_07_aggregator_build.py), written, run once, deleted on success.
- A temporary commit-message file under scripts/ if needed (mirroring the Step 05/06 build-message workaround), deleted on success.

Temp scripts byte-deleted on success; failures leave them pending a separately authorized cleanup turn.

## 6. Files the build turn must not modify

This list is exhaustive for the categories enumerated; any file not listed is also not permitted unless it is in section 5.

- The four canonical CSVs at data/s7_d1_cross_asset_donchian/raw/*.csv.
- data/s7_d1_cross_asset_donchian/raw/fetch_run_manifest.json.
- data/s7_d1_cross_asset_donchian/raw/audit_manifest.json.
- All reports/s7_d1_cross_asset_donchian_step_02b/02c/03/04/05/06_*.{json,md}.
- docs/s7_d1_cross_asset_donchian_spec.md and all docs/s7_d1_cross_asset_donchian_step_02b/02c/03/04/05/06_*.md.
- This Step 07 plan file.
- external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_loader/, _validator/, _signal/, _simulator/ contents.
- tests/external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_loader/, _validator/, _signal/, _simulator/ contents.
- CLAUDE.md, docs/decisions.md, RUNBOOK (if present), pipeline_manifest (if present), .gitignore.
- All ORB branch artifacts and all Step 30 cost constants.
- review_queue.json, idea_memory directory, all Strategy Lab artifacts.
- The Databento-track runner harness path external_research_hunter/s7_d1_cross_asset_donchian_runner_harness/.

## 7. API surface

The aggregator module shall expose exactly the following public API and no other public symbols:

- IN_SAMPLE_WINDOW: tuple[str, str] = ("2013-01-01", "2022-12-30") (hardcoded; matches all prior phases).
- A1_MIN_CLOSED_TRADES: int = 100 (spec sec 13 A1 / sec 14 K9).
- A2_SHARPE_PROXY_MIN: float = 0.0 (strict greater-than per spec; positive Sharpe required).
- A3_EXPECTANCY_MIN: float = 0.0 (strict greater-than per spec).
- A4_TRADE_CURVE_MAXDD_PCT_MAX: float = 50.0 (spec sec 13 A4 / sec 14 K4).
- A5_PORTFOLIO_WR_GAP_PP_MIN: float = 0.5 (spec sec 13 A5).
- A5_PER_MARKET_WR_GAP_MIN_COUNT: int = 2 (at least 2 of 4 markets with WR-gap >= 0).
- A7_EFFECTIVE_INDEPENDENT_BETS_MIN: float = 2.5 (spec sec 13 A7).
- A10_CAP_BINDING_EVENTS_MAX: int = 0 (spec sec 13 A10).
- K10_AVG_PAIRWISE_DEPENDENCE_MAX: float = 0.50 (spec sec 14 K10; "avg_pairwise_correlation" in spec language; the aggregator reports this as "avg_pairwise_dependence_measure" to keep the spec's quantitative threshold).
- K11_CAP_BINDING_EVENTS_MAX: int = 1000 (spec sec 14 K11).
- DR_STRESS_TIERS_REQUIRED: tuple = ("S0", "S1", "S2", "S3") (spec sec 13 A8 / sec 14 K12; the cost-stress matrix requires all four; "S4" reserved per spec is OUT OF SCOPE per Step 06).
- DR2_S2_S3_DEGRADATION_THRESHOLD_FRACTION: float = 0.5 (the Step 07 plan pins "materially degrade" quantitatively: total_net_pnl at S2 or S3 less than 50% of S1, OR turns non-positive while S1 was positive. This is a Step 07 spec choice; the spec sec 10 used qualitative wording "materially").
- class VerdictReason(Enum) - 8 spec-pinned values (see section 16).
- class AggregatorError(Exception) - base for refusal modes.
- class AggregatorInputError(AggregatorError)
- class AggregatorOosBlockedError(AggregatorError)
- class AggregatorParameterOverrideError(AggregatorError)
- class AggregatorProvenanceDriftError(AggregatorError) - K8 sealed-parent-drift detected.
- @dataclass(frozen=True) class PerTradeStats - per-TradeGroup row.
- @dataclass(frozen=True) class PerSymbolStats - one row per symbol.
- @dataclass(frozen=True) class PortfolioStats - one row at portfolio level.
- @dataclass(frozen=True) class CostStressRow - one row per cost tier.
- @dataclass(frozen=True) class KCriteriaResults - K1..K11 outcomes.
- @dataclass(frozen=True) class AGateResults - A1..A10 outcomes.
- @dataclass(frozen=True) class AggregationResult - the top-level return.
- def aggregate(loaded, simulation_results, safety_attestations) -> AggregationResult - the single entry point.

No other public function. No public mutable state. No module-level data load at import time. No public function accepting `lookback=`, `window=`, `optimize_=`, `tune_=`, `enable_oos=`, or any other relaxation parameter.

## 8. AggregationResult schema (cross-referenced from sections 9-16)

`AggregationResult` (immutable, returned by `aggregate`):

- schema: str = "sparta.donchian.step_07_aggregation_result.v1".
- inputs_provenance: Mapping[str, str] -- the sha256 of every input the aggregator read (loaded CSVs, audit_manifest, signal-module sha, simulator-module sha, validator-module sha) plus the seal of every prior phase's build report. Used by K8 sealed-parent-drift check (section 14).
- per_trade_stats: tuple[PerTradeStats, ...] -- one row per TradeGroup, chronological.
- per_symbol_stats: Mapping[str, PerSymbolStats] -- one per symbol.
- portfolio_stats: PortfolioStats -- one at portfolio level (computed at S1 baseline; the cost-stress matrix below covers all tiers).
- cost_stress_matrix: Mapping[str, CostStressRow] -- one per tier in DR_STRESS_TIERS_REQUIRED.
- k_criteria_results: KCriteriaResults -- K1..K11 evaluation.
- a_gate_results: AGateResults -- A1..A10 evaluation.
- avg_pairwise_dependence_measure: float -- the four-market average pairwise dependence measure over the in-sample window (K10 check).
- effective_independent_bets: float -- per A7 (section 12 formula).
- dr_rule_fires: Mapping[str, bool] -- DR2 / DR3 / DR5 evaluation per the cost-stress matrix.
- verdict: VerdictReason -- the one final verdict per spec sec 13-14.
- verdict_explanation: str -- a one-paragraph explanation of which gate or criterion drove the verdict.
- oos_inspection_intentionally_omitted: bool (always True; permanent attestation).
- post_oos_inspection_intentionally_omitted: bool (always True; permanent attestation).
- live_trading_intentionally_blocked: bool (always True; permanent attestation).
- strategy_lab_promotion_intentionally_blocked: bool (always True; permanent attestation).
- companion_md_sha256: str (filled when companion MD is sealed).
- seal_method: str (canonical).
- report_seal_sha256: str (canonical seal, computed as the canonical Python-side seal scheme used by prior s7 D1 reports).

The aggregator's `aggregate()` function returns an `AggregationResult` with the schema-mandated fields populated. The seal fields are populated when the build script writes the build report; the function itself does not seal (the build script does, mirroring the pattern of every prior s7 D1 build).

## 9. Per-trade metric definitions

For each `TradeGroup` `g` in the S1-baseline `SimulationResult.trade_groups`, compute:

- trade_pnl_dollars: g.group_net_pnl_dollars.
- trade_open_date: g.group_open_date (in IN_SAMPLE_WINDOW per Step 06 enforcement).
- trade_close_date: g.group_close_date (in IN_SAMPLE_WINDOW).
- trade_duration_days: integer day count between open and close (calendar days, not trading days).
- trade_direction: g.direction.
- trade_n_entry_dollars: g.n_entry_dollars.
- trade_unit_count: g.group_unit_count.
- trade_exit_reason: g.group_close_reason.value.
- trade_r_multiple: trade_pnl_dollars / (per_unit_dollar_risk_at_first_unit), where per_unit_dollar_risk_at_first_unit = first_unit.shares * STOP_DISTANCE_N_MULTIPLE * trade_n_entry_dollars (defaults to None if first_unit.shares == 0; that is a degenerate skipped case the simulator should not produce, but the aggregator records None defensively).
- trade_is_win: trade_pnl_dollars > 0 (strict positive net PnL).

These are persisted in `PerTradeStats` rows on `AggregationResult.per_trade_stats`.

## 10. Per-symbol metric definitions

For each symbol s in {"SPY","TLT","GLD","USO"}, compute over the trades in the S1-baseline result whose symbol == s:

- symbol: s.
- trades_count: int.
- net_pnl_dollars: sum across trades.
- gross_pnl_dollars: sum across trades.
- avg_win_dollars: mean over wins (trades with trade_pnl_dollars > 0); None if no wins.
- avg_loss_dollars: absolute mean over losses (trades with trade_pnl_dollars < 0); None if no losses.
- pl_ratio: avg_win_dollars / avg_loss_dollars; None if any side is None or zero.
- win_count: count of trades with trade_pnl_dollars > 0.
- loss_count: count of trades with trade_pnl_dollars < 0.
- breakeven_count: count of trades with trade_pnl_dollars == 0.
- observed_win_rate: win_count / trades_count; None if trades_count == 0.
- implied_breakeven_win_rate: 1 / (1 + pl_ratio); None if pl_ratio is None.
- win_rate_gap_to_breakeven_pp: (observed_win_rate - implied_breakeven_win_rate) * 100.0; None if either is None.

The 0/0 cases (no trades at all on a symbol; no wins; no losses) are handled by storing None in the relevant fields, NOT by raising. The aggregator does not generate trades; it summarizes what the simulator produced.

## 11. Portfolio-level metric definitions

Computed at S1 baseline only (cost-stress matrix in section 13 carries the four tiers):

- total_closed_trades: sum of per-symbol trades_count.
- total_net_pnl_dollars: sum across trades.
- total_gross_pnl_dollars: sum across trades.
- mean_trade_net_pnl_dollars: mean over all trades; None if total_closed_trades == 0.
- stdev_trade_net_pnl_dollars: sample stdev over all trades (Bessel's correction; n-1); None if total_closed_trades < 2.
- sharpe_proxy_per_trade: mean_trade_net_pnl_dollars / stdev_trade_net_pnl_dollars; None if stdev is None or 0.
- expectancy_per_trade_dollars: mean_trade_net_pnl_dollars (same as the mean; the spec's "MNQ-equivalent" phrasing in sec 13 A3 reduces to "in dollars" for the ETF-proxy track since the unit of account is already dollars).
- portfolio_win_rate: total_wins / total_closed_trades; None if total_closed_trades == 0.
- portfolio_pl_ratio: pooled portfolio-wide avg_win / avg_loss; None if either side missing.
- portfolio_implied_breakeven_win_rate: 1 / (1 + portfolio_pl_ratio); None if pl_ratio is None.
- portfolio_win_rate_gap_to_breakeven_pp: (portfolio_win_rate - portfolio_implied_breakeven_win_rate) * 100.0; None if either is None.
- trade_curve_cumulative_pnl_dollars: tuple of (close_date, cumulative_net_pnl) sorted by close_date.
- trade_curve_high_water_mark_dollars: max of cumulative_pnl over all points.
- trade_curve_max_drawdown_dollars: max over all points of (high_water_at_that_point - cumulative_pnl_at_that_point).
- trade_curve_max_drawdown_pct_vs_starting_cash: trade_curve_max_drawdown_dollars / starting_cash * 100.0.
- cap_binding_events_count: count of pyramid-block events from the simulator (the simulator currently does not export this; the aggregator infers it as the number of pyramid attempts that were blocked by the 4-unit-per-group cap; in the current Step 06 simulator there is no explicit log of such events, so the aggregator computes it indirectly by inspecting the unit-count distribution; this is a documented Step 07 spec choice and noted in the build report).

## 12. Pairwise dependence measure rules (A7 + K10)

Pairwise dependence measure inputs: the daily-return series of each of the four symbols over the in-sample window. Returns are computed from `loaded[sym].adj_close` over `loaded[sym].dates` whose dates lie in `IN_SAMPLE_WINDOW`:

- daily_return_t = (adj_close_t / adj_close_{t-1}) - 1 for t >= 1 within the in-sample slice.

The aggregator reads `loaded[sym].adj_close` only for in-sample dates. The aggregator does NOT read any OOS or post-OOS adj_close value. The slice is determined by `loaded[sym].dates` against `IN_SAMPLE_WINDOW`. This is a structural in-sample-only constraint; any attempt to read an OOS adj_close raises `AggregatorOosBlockedError`.

Per-pair dependence measure: Pearson product-moment over the daily-return vectors. For four symbols there are C(4,2) = 6 unique pairs.

- avg_pairwise_dependence_measure: mean of the 6 pairwise Pearson values.
- effective_independent_bets: 4.0 / (1.0 + (4 - 1) * avg_pairwise_dependence_measure). This is the canonical simple approximation used in Faith literature (Stevens / Meucci-style). If avg_pairwise_dependence_measure is None or non-finite, effective_independent_bets is None.

A7 evaluation: PASS if effective_independent_bets >= A7_EFFECTIVE_INDEPENDENT_BETS_MIN.
K10 evaluation: FIRE (and PARK) if avg_pairwise_dependence_measure > K10_AVG_PAIRWISE_DEPENDENCE_MAX.

## 13. Cost-stress matrix construction (A8 + DR2 + DR3 + DR5)

The aggregator consumes one `SimulationResult` per cost tier in `DR_STRESS_TIERS_REQUIRED = ("S0", "S1", "S2", "S3")`. For each tier:

CostStressRow:

- tier: "S0" | "S1" | "S2" | "S3".
- slippage_scalar: 0.0 | 1.0 | 3.0 | 5.0.
- commission_scalar: 0.0 | 1.0 | 1.5 | 2.0.
- total_closed_trades: same as per-tier simulation_results[tier].num_closed_units_total interpreted at the group level (sum over trade_groups of group_unit_count).
- total_net_pnl_dollars: sum across all trade groups in this tier's simulation.
- portfolio_sharpe_proxy_per_trade: same formula as section 11 but using this tier's trades.
- portfolio_expectancy_dollars: same as section 11 for this tier.
- portfolio_trade_curve_max_drawdown_pct: same as section 11 for this tier.
- portfolio_win_rate: same.
- portfolio_pl_ratio: same.
- k4_fired_in_simulator: this tier's simulation_results[tier].k4_fired.

DR rule evaluation (each independently):

- DR2: IS metrics degrade materially under S2 or S3.
  - Pinned threshold (this plan): total_net_pnl at S2 is non-positive while S1 was positive, OR total_net_pnl at S2 is positive but less than DR2_S2_S3_DEGRADATION_THRESHOLD_FRACTION (= 0.5) times S1's; same check at S3.
  - DR2 FIRES if either S2 or S3 satisfies the degradation condition relative to S1.
- DR3: zero_cost_only_survival.
  - DR3 FIRES if S0.total_net_pnl > 0 AND (S1.total_net_pnl <= 0 OR S2.total_net_pnl <= 0 OR S3.total_net_pnl <= 0).
- DR5: cost_stress_turns_edge_negative between S0 and S1.
  - DR5 FIRES if S0.total_net_pnl > 0 AND S1.total_net_pnl <= 0.

A8 evaluation: A8 is NOT a pass-gate per spec; it is an attestation that all four tiers were run and the cost-stress matrix was sealed.

K12 (REJECT_FAST) evaluation: FIRES if DR2 OR DR3 OR DR5 fires.

DR4 (IS positive but OOS negative at S0 baseline): NOT EVALUATED in Step 07. This rule is OOS-side and requires OOS simulation, which is OUT OF SCOPE for this in-sample-only aggregator. The aggregator documents DR4 as "DEFERRED_TO_OOS_PHASE" in `dr_rule_fires`.

## 14. K-criteria evaluation (K1..K11; K12 = DR rules per section 13)

For the S1-baseline portfolio_stats:

- K1: portfolio_stats.sharpe_proxy_per_trade < 0 (None treated as False since negative requires a number).
- K2: portfolio_stats.expectancy_per_trade_dollars <= 0.
- K3: reserved per spec; not used at D1; always False.
- K4: portfolio_stats.trade_curve_max_drawdown_pct_vs_starting_cash > 50.0.
- K5: reserved; always False.
- K6: any safety_attestations[c] is False for c in C1..C8 (i.e., safety_warning_count > 0).
- K7: safety_attestations.get("filter_silently_introduced_attestation") is True OR safety_attestations.get("dependence_gate_silently_introduced_attestation") is True. (Spec spells it as "correlation_gate_silently_introduced_attestation"; this plan accepts that spelling on input and exposes the result under either alias for backward compatibility, but the public field is `K7_filter_or_dependence_gate_silently_introduced`.)
- K8: ANY upstream sealed sha pin no longer matches what is on disk now (inputs_provenance mismatch). The aggregator computes K8 by re-reading the sha256 of every input it relied on and comparing to the pinned values in this plan (and in the prior phases' anchors). Mismatch -> K8 FIRES and AggregatorProvenanceDriftError IS RAISED at the end of aggregate (after the AggregationResult has been computed and the K8 outcome captured) -- alternative: K8 is captured as a flag and the verdict is set to PARKED_PROVENANCE_BROKEN without raising. The plan REQUIRES the flag pattern (no raise; K8 flows into the verdict).
- K9: portfolio_stats.total_closed_trades < A1_MIN_CLOSED_TRADES (=100).
- K10: avg_pairwise_dependence_measure > K10_AVG_PAIRWISE_DEPENDENCE_MAX (= 0.50).
- K11: portfolio_stats.cap_binding_events_count > K11_CAP_BINDING_EVENTS_MAX (= 1000).

`KCriteriaResults` records each K outcome as a boolean. The aggregator does NOT short-circuit on the first K fire; all K outcomes are evaluated and recorded.

## 15. A-gate evaluation (A1..A10)

For the S1-baseline portfolio_stats:

- A1: portfolio_stats.total_closed_trades >= A1_MIN_CLOSED_TRADES.
- A2: portfolio_stats.sharpe_proxy_per_trade is not None AND > A2_SHARPE_PROXY_MIN.
- A3: portfolio_stats.expectancy_per_trade_dollars is not None AND > A3_EXPECTANCY_MIN.
- A4: portfolio_stats.trade_curve_max_drawdown_pct_vs_starting_cash <= A4_TRADE_CURVE_MAXDD_PCT_MAX.
- A5: count of per_symbol_stats[s].win_rate_gap_to_breakeven_pp >= 0 (for s in {SPY,TLT,GLD,USO}; None treated as False) >= A5_PER_MARKET_WR_GAP_MIN_COUNT AND portfolio_stats.portfolio_win_rate_gap_to_breakeven_pp >= A5_PORTFOLIO_WR_GAP_PP_MIN.
- A6: all four upstream phase verdicts are PASS (loader, validator, signal, simulator). The aggregator reads each build report's `audit_overall_verdict` field; if any is not PASS the A6 outcome is False. Spec sec 13 A6 also references "VALIDATOR_PASS 16/16"; this aggregator equates that with all upstream phases reporting PASS.
- A7: effective_independent_bets is not None AND >= A7_EFFECTIVE_INDEPENDENT_BETS_MIN.
- A8: cost_stress_matrix contains all four tiers (S0..S3) AND DR2 AND DR3 AND DR5 are all False. (A8 by itself is the attestation; DR2/DR3/DR5 firing triggers K12 = REJECT_FAST.)
- A9: all C1..C8 in safety_attestations are True.
- A10: portfolio_stats.cap_binding_events_count == 0 (NOT > 0).

`AGateResults` records each A outcome as a boolean.

## 16. Verdict assembly (per spec sections 13-14)

`VerdictReason` enum values (locked):

- PARKED_FAILED_AT_INSUFFICIENT_SAMPLE
- PARKED_SAFE_BUT_NOT_MONEY_PROVEN
- PARKED_SAFETY_FAILED
- PARKED_PROVENANCE_BROKEN
- PARKED_FAILED_AT_DIVERSIFICATION_HYPOTHESIS
- PARKED_CAP_BINDING
- REJECT_FAST
- ELIGIBLE_FOR_OOS

Verdict assembly order (the FIRST matching condition wins):

1. K8 fires -> PARKED_PROVENANCE_BROKEN. (Provenance is the most fundamental check; if upstream sealed bytes have drifted, no further reasoning is reliable.)
2. K12 fires (DR2 / DR3 / DR5) -> REJECT_FAST.
3. K6 fires -> PARKED_SAFETY_FAILED.
4. K7 fires -> PARKED_SAFETY_FAILED.
5. K10 fires -> PARKED_FAILED_AT_DIVERSIFICATION_HYPOTHESIS.
6. K9 fires (sample size) -> PARKED_FAILED_AT_INSUFFICIENT_SAMPLE.
7. K11 fires -> PARKED_CAP_BINDING.
8. K1 OR K2 OR K4 fires -> PARKED_SAFE_BUT_NOT_MONEY_PROVEN.
9. Otherwise check A-gates A1..A10. If ALL pass -> ELIGIBLE_FOR_OOS. If any fails:
   a. If A1 fails -> PARKED_FAILED_AT_INSUFFICIENT_SAMPLE (defensive duplicate of K9 path).
   b. Else if A6 fails -> PARKED_PROVENANCE_BROKEN (an upstream phase did not PASS).
   c. Else if A7 fails -> PARKED_FAILED_AT_DIVERSIFICATION_HYPOTHESIS (diversification hypothesis empirically rejected).
   d. Else if A9 fails -> PARKED_SAFETY_FAILED.
   e. Else if A10 fails -> PARKED_CAP_BINDING.
   f. Else (one of A2/A3/A4/A5 fails) -> PARKED_SAFE_BUT_NOT_MONEY_PROVEN.

The `ELIGIBLE_FOR_OOS` verdict authorizes ONE further separately authorized operator turn to consider OOS access. It does NOT auto-trigger OOS. It does NOT change any blocking posture. Live trading, Strategy Lab promotion, brokerage connection, and review_queue mutation all remain blocked regardless of verdict.

## 17. In-sample-only enforcement + out-of-sample protection + no live trading

The aggregator inherits the in-sample-only enforcement from the simulator and the signal module. In addition, the aggregator enforces:

- For each consumed `SimulationResult`, the aggregator verifies that `result.in_sample_window` equals the spec-pinned `IN_SAMPLE_WINDOW`. Mismatch raises `AggregatorOosBlockedError`.
- For each TradeGroup in each consumed `SimulationResult.trade_groups`, the aggregator verifies that `group_open_date` and `group_close_date` lie in `IN_SAMPLE_WINDOW`. Mismatch raises `AggregatorOosBlockedError`.
- For each TradeUnit in each group, the aggregator verifies that `entry_trigger_date`, `entry_fill_date`, and `exit_date` lie in `IN_SAMPLE_WINDOW`.
- For each daily_equity_ledger entry in each consumed `SimulationResult`, the aggregator verifies that `date` lies in `IN_SAMPLE_WINDOW`.
- For the daily-return computation in section 12, the aggregator slices `loaded[sym].adj_close` over dates in `IN_SAMPLE_WINDOW` only. Any OOS read raises `AggregatorOosBlockedError`.
- The aggregator does NOT call the simulator. The aggregator does NOT call the signal module. The aggregator does NOT call the loader's `load_symbol()` or `load_all()`.
- The aggregator does NOT compute any OOS statistic. The aggregator does NOT recommend any OOS run as a runtime action; it ONLY produces the structural attestation `ELIGIBLE_FOR_OOS` if the criteria are met.
- The aggregator does NOT change any blocking-posture flag, write any "trading enabled" marker, modify review_queue.json, mutate idea_memory, promote anything to Strategy Lab, connect to any broker, place any order, or call any production scheduler / autopilot / FRC gate.

The `AggregationResult` permanent attestation fields:

- oos_inspection_intentionally_omitted: True
- post_oos_inspection_intentionally_omitted: True
- live_trading_intentionally_blocked: True
- strategy_lab_promotion_intentionally_blocked: True

## 18. Refusal modes and HALT conditions

The aggregator HALTs by raising:

- AggregatorInputError: bad input shape; loaded not Mapping; loaded keys != {SPY,TLT,GLD,USO}; simulation_results not Mapping; simulation_results missing "S1" key OR missing one of S0/S2/S3 when running the cost-stress matrix; SimulationResult structurally invalid; safety_attestations not Mapping; safety_attestations missing C1..C8 keys; loaded[sym] does not look like a LoadedSymbol.
- AggregatorOosBlockedError: any date check fails IN_SAMPLE_WINDOW containment (per section 17).
- AggregatorParameterOverrideError: any unknown kwarg passed; any tier not in DR_STRESS_TIERS_REQUIRED used internally; any attempt to override a hardcoded threshold via attribute mutation post-import (defensive).
- AggregatorProvenanceDriftError: NOT raised by `aggregate()`; recorded as K8 flag and routed to PARKED_PROVENANCE_BROKEN verdict. This class is exported for API completeness only.
- AggregatorError (base): any other unhandled refusal.

NOT refusal modes (recorded as data, not raised):

- Verdict outcomes (all 8 VerdictReason values) are normal results, not exceptions.
- K-criteria firing is normal; recorded in KCriteriaResults.
- A-gate failures are normal; recorded in AGateResults.

The aggregator shall NOT support:

- any parameter optimization or search.
- any alternative threshold (no relaxing A2_SHARPE_PROXY_MIN, no relaxing A4_TRADE_CURVE_MAXDD_PCT_MAX, etc.).
- any filter on top of the trades (no excluding losing trades from the cost-stress matrix; no winning-only mode).
- any winner-symbol selection rule (no "compute portfolio_stats using only SPY trades since SPY has more").
- any opt-out from the cost-stress matrix (all four tiers S0..S3 must be provided).
- any partial cost-stress matrix (e.g., providing only S0 and S1) -- raises AggregatorInputError.
- any tax modeling or leverage adjustment.

## 19. Forbidden tokens, forbidden imports, ORB / Databento / Strategy Lab / brokerage / live trading prohibition

Forbidden imports (verified by static grep over aggregator.py):

- import yfinance, import databento, import requests, import urllib.*, from urllib *, import http.client, import socket, import curl_cffi, import aiohttp, import httpx, import grpc, import pyarrow.flight.
- import strategy_lab, import sparta_commander, import spartacus, import hydra_video, import app, import sparta_brain.
- import broker, import interactive_brokers, import alpaca, import tradestation, import ibapi, import binance, import oanda, import ib_insync.
- import quantconnect, import lean, import qcalgorithm.

Forbidden tokens (verified by static grep; comment-marker FORBIDDEN_TOKEN_EXCLUSION allowed for documentation):

Vendor / credential / network:

- DATABENTO_API_KEY, yfinance, yahoo_finance, databento, requests.get, urllib.request, socket.connect, http.client, curl_cffi, aiohttp, httpx.

Live trading / brokerage / production:

- Strategy Lab (with space), strategy_lab, review_queue, idea_memory.
- live trading (with space), live_trading.
- brokerage, broker_api, broker_session.
- alpaca, interactive_brokers, ibkr, ibapi, ib_insync, tradestation, binance, oanda.
- order_send, place_order, submit_order, cancel_order, modify_order, route_order.
- production_signal.
- paper_broker, paper_trade.
- scheduler, autopilot.
- frc_gate.

OOS-related tokens forbidden:

- simulate_oos, simulate_full_window, simulate_post_oos.
- compute_signals_oos.
- oos_simulation (the English term; the SCHEMA FIELD `oos_inspection_intentionally_omitted` is permitted).
- post_oos_simulation.

Parameter optimization tokens forbidden:

- _optimize_, _sweep_, _tune_, _grid_search_, _bayes_search_.
- alternative_lookback, lookback_grid, parameter_grid.
- winner_selection, asset_selection, top_n_pick.

Filter / regime tokens forbidden:

- regime_filter, regime_gate, ma_filter, vol_filter.
- dependence_filter (NOTE: "dependence_measure" as a SCHEMA FIELD is PERMITTED; the FILTER form is what is forbidden).

Tokens NEWLY UNBLOCKED in Step 07 (these were forbidden in Step 06; they are necessary for the aggregator's spec-mandated computations):

- sharpe, sharpe_proxy.
- sortino, calmar.
- expectancy.
- win_rate, breakeven_win_rate.
- correlation, covariance, pearson, .pct_change(.
- effective_independent_bets, avg_pairwise_correlation, avg_pairwise_dependence_measure.
- (Note: the aggregator may use "correlation" in its computation of the four-symbol dependence matrix; the spec uses "pairwise correlation" wording in A7 / K10. The aggregator is permitted to use these tokens.)

ORB isolation: the aggregator shall NOT read or modify any ORB branch artifact; shall NOT modify any Step 30 cost constant.

The build report shall include an api_key_safety_confirmation block attesting:

- databento_called: false
- databento_api_key_accessed: false
- os_environ_DATABENTO_API_KEY_referenced: false
- yfinance_imported_by_aggregator: false
- yahoo_finance_called_by_aggregator: false
- any_network_call_by_aggregator: false
- any_file_io_by_aggregator: false (the aggregator is pure in-memory; the BUILD ORCHESTRATOR writes the build report, not the aggregator)
- any_brokerage_call_by_aggregator: false
- any_strategy_lab_call_by_aggregator: false
- any_review_queue_mutation_by_aggregator: false
- any_oos_inspection_by_aggregator: false

## 20. V-gates V1-V10, tests T1-T16, build-script safety guardrails

V-gates the build turn shall verify in order:

V1. The seven output files in section 4 exist at the locked paths.
V2. The aggregator module is syntactically valid Python (AST compiles).
V3. The aggregator module imports cleanly without performing any file IO at import time.
V4. The public API surface (section 7) matches exactly.
V5. The aggregator module contains no forbidden import (section 19 list).
V6. The aggregator module contains no forbidden token from the section 19 list, outside designated FORBIDDEN_TOKEN_EXCLUSION comment lines.
V7. The test suite runs to completion under stdlib unittest with all tests passing. No skipped. No xfail.
V8. The test suite includes every test T1..T16. Missing or renamed tests HALT.
V9. A live in-sample integration test: load_all then compute_signals_all then simulate at S0/S1/S2/S3 then aggregate -- returns an AggregationResult with a valid verdict (one of the 8 VerdictReason values), no OOS dates in any computation, and the seal-method canonical fields populated.
V10. Negative-path tests: aggregate raises AggregatorInputError on bad input shape; raises AggregatorOosBlockedError when a synthetic SimulationResult with an OOS TradeUnit is injected; raises AggregatorParameterOverrideError on unknown kwargs.

T-tests the build turn shall implement (renames forbidden):

- T1: aggregator imports loader/simulator outputs only (no external network or vendor SDK).
- T2: every per-trade and per-symbol and portfolio metric is computed over IS dates only.
- T3: OOS injection blocked: construct a synthetic SimulationResult with one TradeGroup whose group_close_date is "2024-06-15"; aggregate raises AggregatorOosBlockedError.
- T4: no live-trading code path: aggregate accepts only the three positional args; extra kwargs raise.
- T5: no brokerage / Strategy Lab / review_queue imports.
- T6: deterministic: aggregate called twice on the same inputs returns field-equal AggregationResult.
- T7: parameter override rejection: unknown kwargs raise.
- T8: no Databento / yfinance / network imports.
- T9: no production scheduler / autopilot / FRC-gate references.
- T10: cost-stress matrix has exactly four tiers; missing a tier raises AggregatorInputError.
- T11: K8 sealed_parent_drift test: temp-modify a checked sha (via in-memory dict override of inputs_provenance pin), assert verdict becomes PARKED_PROVENANCE_BROKEN.
- T12: K9 sample-size: synthesize a result with < 100 trades, assert verdict is PARKED_FAILED_AT_INSUFFICIENT_SAMPLE.
- T13: A1-A10 all-pass synthetic: synthesize SimulationResults that satisfy every A-gate (sample >= 100, sharpe > 0, expectancy > 0, MaxDD <= 50, WR-gap >= 0.5pp on portfolio AND at least 2 markets, effective_independent_bets >= 2.5, no K fire); assert verdict is ELIGIBLE_FOR_OOS.
- T14: DR2 fire: synthesize a cost-stress matrix where S2.total_net_pnl is half of S1 and S1 was positive; assert DR2 fires, K12 fires, verdict is REJECT_FAST.
- T15: DR3 fire: synthesize S0 positive AND S1 non-positive; assert DR3 fires, verdict REJECT_FAST.
- T16: DR5 fire: synthesize S0 positive AND S1 non-positive; assert DR5 fires (DR5 is a more specific subset of DR3 with S0->S1 transition only; both can fire together); verdict REJECT_FAST.

Build-script safety guardrails:

- The script shall not write to any path outside section 4 + section 5 temp paths.
- The script shall not import any forbidden vendor / brokerage / production package.
- The script shall not set any environment variable beginning with DATABENTO_.
- The script shall not disable SSL verification.
- The script shall log build steps to stdout for the build report writer.
- The script shall self-delete on success.

## 21. Build report schema, build acceptance checklist, what build is NOT allowed to do, next authorization

Build report schema (sparta.donchian.step_07_aggregator_build_report.v1):

- schema, phase, controller_session, report_date_utc.
- plan_anchor, step_06_anchor, step_05_anchor, step_04_anchor, step_03_anchor, step_02c_anchor.
- output_files (path -> sha256 + bytes).
- aggregator_api_surface_observed.
- v_gate_results (V1..V10).
- t_test_results (T1..T16).
- forbidden_token_grep_results, forbidden_import_grep_results.
- boundaries_held, negative_invariants.
- api_key_safety_confirmation (11 fields per section 19).
- oos_protection_attestation (no_oos_inspection_by_aggregator, no_post_oos_inspection_by_aggregator, no_oos_value_inspected_for_metric_computation).
- live_trading_blocking_attestation (no_live_trading_signal, no_brokerage_call, no_real_order_placed, no_paper_order_placed, no_strategy_lab_promotion, no_review_queue_mutation).
- companion_md_sha256, seal_method, report_seal_sha256.

Build acceptance checklist (the future build turn must satisfy):

- A separate operator authorization explicitly authorizes the Step 07 build.
- The plan path is exactly docs/s7_d1_cross_asset_donchian_step_07_result_aggregation_specification_plan.md.
- The Step 03 loader, Step 04 validator, Step 05 signal module, and Step 06 simulator are byte-unchanged.
- The four CSVs and audit_manifest.json are byte-unchanged.
- Output paths in section 4 are confirmed MISSING via L_FILE_SAFETY pre-state capture.
- No co-active Databento path, no co-active OOS path, no co-active live-trading path, no co-active Strategy Lab promotion.
- The build writes only the seven output files plus the optional temp scripts (each deleted on success).

What the build is NOT allowed to do:

- Compute any OOS statistic; inspect any OOS bar; iterate any OOS date.
- Simulate the OOS window or the post-OOS window.
- Make any live order, paper order, broker call, broker session, scheduler call, production-signal write.
- Promote any candidate to Strategy Lab. Mutate review_queue.json. Mutate idea_memory.
- Modify any canonical CSV, manifest, loader, validator, signal, simulator, spec, plan, ORB artifact, or Step 30 cost constant.
- Modify CLAUDE.md, docs/decisions.md, RUNBOOK, pipeline_manifest, or .gitignore.
- Switch branches or create branches. Push to any remote.
- Call yfinance, Yahoo Finance, or any network resource.
- Call Databento. Access DATABENTO_API_KEY.
- Disable SSL certificate verification.
- Treat the ELIGIBLE_FOR_OOS verdict as a permission to do OOS work.
- Treat the ELIGIBLE_FOR_OOS verdict as a permission to do Strategy Lab promotion.
- Treat any phase of this chain as conferring standing authorization for live trading.
- Use the phrase "run aggregator now" or "execute OOS now" as an active directive (these appear here only as forbidden text).
- Treat the phrase "authorize Step 07 build" as a completed or current action.

A future operator authorization is required to proceed beyond this plan. That authorization shall reference this plan by exact path. This plan is the source of truth; the build turn is not pre-authorized by the plan itself. No phase of this chain confers any standing authorization for OOS access, Strategy Lab promotion, brokerage connection, or live trading; each requires its own explicit fresh operator approval.

Future expected status on the Step 07 build turn (informational; not granted here):

STEP_07_AGGREGATOR_BUILT
AGGREGATOR_TEST_SUITE_PASSED_T1_TO_T16
AGGREGATOR_BUILD_REPORT_SEALED
NO_CSV_MODIFIED
NO_AUDIT_MANIFEST_MODIFIED
NO_FETCH_RUN_MANIFEST_MODIFIED
NO_LOADER_MODIFIED
NO_VALIDATOR_MODIFIED
NO_SIGNAL_MODULE_MODIFIED
NO_SIMULATOR_MODIFIED
NO_OOS_INSPECTION
NO_POST_OOS_INSPECTION
NO_DATA_FETCH
NO_NETWORK_CALL
NO_DATABENTO_CALL
NO_DATABENTO_API_KEY_ACCESS
NO_BROKERAGE_CONNECTION
NO_REAL_ORDER
NO_PAPER_ORDER
NO_STRATEGY_LAB_PROMOTION
NO_REVIEW_QUEUE_MUTATION
NO_ORB_BRANCH_MUTATION
NO_LIVE_TRADING

Downstream-phase reminder (informational; not authorized by this plan):

- OOS inspection: separate plan beyond Step 07. Even when Step 07 outputs ELIGIBLE_FOR_OOS, OOS inspection requires its own separately authorized operator turn. The OOS-inspection plan shall enumerate every safety boundary that re-applies in the OOS context (no re-fit of any parameter, no choosing the best of multiple OOS runs, no relaxation of K-thresholds, no Strategy Lab promotion until OOS PASS plus operator review).
- Strategy Lab promotion / production candidate registration: separate plan; remains blocked.
- Brokerage connection / paper trading / live trading: separate plans; all remain blocked at six gates. No phase of this chain confers any standing authorization for them.

----

End of plan. Plan-authoring turn only. No aggregator code. No simulator re-run. No backtest. No OOS computation. No data fetch. No network. No Databento. No DATABENTO_API_KEY access. No brokerage. No real order. No paper order. No Strategy Lab promotion. No review_queue mutation. No ORB branch mutation. No live trading. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES.
