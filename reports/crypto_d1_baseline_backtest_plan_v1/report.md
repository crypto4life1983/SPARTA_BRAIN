# SPARTA Crypto-D1 Baseline Backtest Plan v1 — build report

> **Research-only. Baseline backtest PLAN / pre-registration only.** No
> broker, no live trading, no paper-order execution, no exchange connection,
> no API keys, no scheduler, no external network calls, **no data fetch, no
> backtest execution, no dataset processing in this bundle. No real data
> files or backtest output files created.**

This bundle satisfies the PLAN layer of the **P3_baseline_strategy_impl**
phase of the Crypto-D1 Protocol Memo v1 (Bundle 11), following the
Crypto-D1 Data Contract v1 (Bundle 12), Dataset Manifest v1 (Bundle 13),
and QA / Freeze Spec v1 (Bundle 14). The future runner implementation is a
separate, separately-authorized bundle.

## Files changed

| Path | Purpose |
|---|---|
| `reports/crypto_d1_baseline_backtest_plan_v1/backtest_plan.json` | Machine-readable plan (validator source of truth). |
| `reports/crypto_d1_baseline_backtest_plan_v1/backtest_plan.md` | Human-readable plan: lane + scope; required prior artifacts; required dataset gate; 6 baseline strategy families; parameter policy; data + QA gate; IS / OOS + validation policy; cost / slippage / position-sizing / risk; 17 required metrics; 27-field report schema; PASS / WATCH / FAIL rules; kill conditions; forbidden actions; candidate-registry update rules; no-profit-claim policy; safety boundaries. |
| `reports/crypto_d1_baseline_backtest_plan_v1/report.md` | This build report. |
| `reports/crypto_d1_baseline_backtest_plan_v1/report.json` | Build report (machine). |
| `tools/crypto_d1_backtest_plan_check.py` | Stdlib-only validator (`validate` / `show` CLI). |
| `tests/test_crypto_d1_backtest_plan.py` | 35 tests. |
| `tools/strategy_candidate_registry.py` | Added two new backtest_plan docs to the `crypto_d1_protocol` seed's `extra_files`. Lane stays **WATCH** (never ACTIVE, never STRONG). |
| `brain_memory/projects/trading_bot/decisions.md` | Append-only Bundle 15 decision. |
| `brain_memory/projects/trading_bot/next_actions.md` | Append-only Bundle 16 candidate list. |

**Not touched:** `app.py`, `templates/*.html`, paper / live execution
code, sealed data, the Bundle 11–14 Crypto-D1 specs, all 8 prior
arbitrage validators + docs, `tools/strategy_next_bundle.py` (no
artificial selection nudge), `lessons.md`.

## What the Crypto-D1 Baseline Backtest Plan defines

1. **Lane + scope.** `crypto_d1_protocol`; BTC + ETH + SOL spot only on
   the daily timeframe; perps / dated / options / leveraged /
   margin-spot / synthetic instruments forbidden.
2. **Required prior artifacts.** Bundles 11–14 must all exist on disk
   and each must `validate: OK` before any runner may proceed.
3. **Required dataset gate.** Per-dataset folder under
   `data/crypto_d1_research/<dataset_id>/<dataset_version>/` must
   exist; `manifest.json` + `qa_report.json` must be present;
   `freeze_status == FROZEN`; `QA_status == QA_PASS` or approved
   `QA_WARN`; `dataset_id` + `dataset_version` +
   `data_contract_version` + `protocol_version` + `manifest_version` +
   `QA_report_id` all cited in every future report; QA's
   `no_lookahead` check + groups B / D / E / G blocking checks must
   be in the cited `qa_report.json`'s `checks_passed`.
4. **6 baseline strategy families.** `buy_and_hold_benchmark`
   (benchmark, not a candidate); `donchian_channel_breakout`,
   `moving_average_trend_filter`, `momentum_continuation`,
   `volatility_regime_gate` (all primary; vol-regime is an
   additive filter on top of B / C / D, never standalone);
   `mean_reversion` (**WATCH-only**; must not revive any prior
   CODR-\* parameter set).
5. **Parameter policy.** Small pre-registered grids only; ≤ 3 free
   params per family; ≤ 10 combinations per family; no unlimited
   optimization; no genetic search; no AI-picked best on OOS; no
   repeated tuning on OOS; all combinations logged; chosen parameter
   must be explainable (e.g., "median of grid on IS", not "best on
   OOS"); baseline first, complexity later.
6. **Data and QA gate.** Backtest execution allowed only after the
   required dataset gate is satisfied.
7. **IS / OOS + walk-forward policy.** IS / OOS declared in writing
   before any run; no training on OOS; OOS unread until after IS
   verdict; single OOS attempt per dataset_version; walk-forward is
   a separately-authorized step after a non-FAIL static-split verdict;
   minimum 20 trades per asset, 30 trades per family on OOS; multi-
   asset checked separately and combined; 2020–2025 framing may be
   mentioned only as future planning context.
8. **Cost + slippage model.** Spot taker fees required, dated, pre-
   declared; default assumption TAKER on every leg; slippage
   conservative slow-day haircut (constant-bps + one-tick); spread
   proxy when quote data absent; cost sensitivity required before
   any PASS; no PASS if costs ignored; fees as a distinct PnL line.
9. **Position sizing + risk.** No leverage; long-only spot first; no
   shorting; equal-notional or volatility-scaled future sizing
   options; cash / risk-off state required; drawdown measurement per
   asset + per basket; per-asset + portfolio drawdown kill pre-
   declared (logged kill-switch, not a future trade trigger); tail-
   risk disclosure required; no post-hoc stop-loss addition.
10. **17 required metrics.** `CAGR_or_total_return`,
    `annualized_volatility`, `max_drawdown`,
    `sharpe_like_risk_metric_with_caveats`, `win_rate`,
    `trade_count`, `average_trade_return`, `median_trade_return`,
    `exposure_percentage`, `turnover`, `fee_slippage_paid`,
    `OOS_return`, `OOS_drawdown`, `per_asset_results`,
    `basket_results`, `benchmark_comparison`, `sensitivity_summary`.
11. **27-field report schema.** Every future per-strategy
    `report.json` must populate all 27 fields (including
    `protocol_version`, `data_contract_version`, `manifest_version`,
    `QA_report_id` — so every report pins all four spec layers).
12. **Candidate-registry update rules.** Adding this plan to
    `extra_files` does **NOT** promote `crypto_d1_protocol` to
    ACTIVE; lane stays WATCH. Promotion requires a future per-strategy
    PASS verdict + explicit operator decision.
13. **PASS / WATCH / FAIL rules + kill conditions + forbidden
    actions + required future artifacts + safety boundaries +
    no-profit-claim policy.**

## Safety guarantees (enforced by tests)

- **Seven** execution / fetch / connection / backtest-execution /
  dataset-processing flags pinned **False**:
  `data_fetch_enabled`, `exchange_connection_enabled`,
  `live_trading_enabled`, `broker_control_enabled`,
  `paper_order_execution_enabled`, `backtest_execution_enabled`,
  `dataset_processing_enabled`.
- `research_only: true` asserted.
- `lane == "crypto_d1_protocol"` asserted.
- Target assets MUST include BTC, ETH, SOL.
- `allowed_market_type == "spot"`; perps / dated / options /
  leveraged in `forbidden_market_types`.
- Timeframe `1d`; `intraday_explicitly_out_of_scope = True`.
- All 6 baseline strategy families present;
  `mean_reversion.status == "WATCH_only"`;
  `buy_and_hold_benchmark.status == "benchmark"`.
- `parameter_policy.no_unlimited_optimization`,
  `.no_genetic_search`,
  `.no_ai_selected_best_parameter_after_seeing_oos`,
  `.no_repeated_tuning_on_oos`,
  `.all_combinations_logged` all True.
- `required_dataset_gate` carries 12 required keys (existence,
  manifest, qa_report, FROZEN, QA_PASS-or-approved-WARN, 5 version
  citations, no-lookahead check, B/D/E/G checks passed).
- All 17 required metrics present.
- All 27 `report_schema.required_fields` present; `field_count` == 27.
- `cost_model_requirements.no_pass_if_costs_ignored = True`;
  `slippage_model_requirements.no_zero_slippage_baseline = True`;
  `position_sizing_policy.no_leverage = True`, `.long_only_spot_first
  = True`, `.no_shorting_in_this_protocol = True`.
- `pass_watch_fail_rules` carries PASS / WATCH / FAIL; `kill_conditions`
  and `forbidden_actions` non-empty.
- `safety_boundaries` carries `research-only`, `no broker`, `no
  live`, `no order`.
- MD carries all 8 distinction phrases.
- Validator scans MD + JSON for forbidden capability claims.
- Tool is **stdlib-only** (AST scan; only `argparse`, `json`,
  `pathlib`, `__future__`).
- Dedicated test asserts **exactly 4 spec files** exist and no
  `.csv` / `.parquet` / `.pq` / `.pickle` / `.feather` / `.h5` /
  `.npz` / `.pkl` files were created.

## Tests run

```bash
python -m pytest tests/test_crypto_d1_backtest_plan.py --rootdir=tests -q
→ 35 passed

python -m pytest tests/test_crypto_d1_backtest_plan.py tests/test_crypto_d1_qa_freeze_spec.py tests/test_crypto_d1_dataset_manifest.py tests/test_crypto_d1_data_contract.py tests/test_crypto_d1_protocol.py tests/test_arbitrage_readiness_gate.py tests/test_arbitrage_sample_dataset_plan.py tests/test_arbitrage_data_source_evaluation.py tests/test_arbitrage_qa_harness_spec.py tests/test_arbitrage_dataset_manifest.py tests/test_arbitrage_data_contract.py tests/test_arbitrage_research_protocol.py tests/test_strategy_candidate_registry.py tests/test_strategy_next_bundle.py --rootdir=tests -q
→ 358 passed across Bundles 2-15
```

## JSON validity

```
python tools/crypto_d1_backtest_plan_check.py validate          → validate: OK
python tools/crypto_d1_qa_freeze_spec_check.py validate         → validate: OK
python tools/crypto_d1_dataset_manifest_check.py validate       → validate: OK
python tools/crypto_d1_data_contract_check.py validate          → validate: OK
python tools/crypto_d1_protocol_check.py validate               → validate: OK
python tools/arbitrage_readiness_gate_check.py validate         → validate: OK
python tools/arbitrage_sample_dataset_plan_check.py validate    → validate: OK
python tools/arbitrage_data_source_evaluation_check.py validate → validate: OK
python tools/arbitrage_qa_harness_spec_check.py validate        → validate: OK
python tools/arbitrage_dataset_manifest_check.py validate       → validate: OK
python tools/arbitrage_data_contract_check.py validate          → validate: OK
python tools/arbitrage_protocol_check.py validate               → validate: OK
python tools/strategy_candidate_registry.py validate            → validate: OK
python tools/strategy_next_bundle.py validate                   → validate: OK
```

## Crypto-D1 Baseline Backtest Plan validation result

**`validate: OK`** on the committed plan. All required top-level
keys present; all 7 safety flags pinned `False`; lane =
`crypto_d1_protocol`; target_assets include BTC + ETH + SOL;
`allowed_market_type` = `spot`; perps / dated / options / leveraged
in `forbidden_market_types`; timeframe.primary = `1d` with intraday
explicitly out of scope; **6 baseline strategy families** present;
`mean_reversion` is `WATCH_only`; `buy_and_hold_benchmark` is
`benchmark`; parameter policy forbids unlimited / genetic /
post-OOS / repeated tuning; required dataset gate carries 12 keys;
**17 metrics** required; **27 report-schema fields** present
(`field_count` = 27); cost / slippage / position-sizing
requirements populated; MD carries all 8 distinction phrases;
zero forbidden capability phrases.

## Candidate registry status for crypto_d1 after build

- **status:** **`WATCH`** ✅ (lane_status_override fires because
  the seed's `extra_files` now include 10 docs total: protocol +
  data contract + dataset manifest + qa_freeze_spec + backtest_plan,
  all on disk).
- **evidence_level:** `MIXED` (25 matched docs across historical
  CODR-1 reports + the five new Crypto-D1 specs; cannot reach
  `STRONG`).
- The new backtest_plan docs are added to `source_reports`.
- Guards held: **never ACTIVE / never STRONG**.

## Next-bundle generator selected bundle after update

**Selects "Arbitrage research protocol"** (lane =
`arbitrage_research_protocol`, priority = 3) — same as Bundles
10–14. Both arbitrage and crypto_d1 are still WATCH with the same
`+15` bonus; arbitrage still wins on the existing protocol-first /
data-first scoring hints. **Deterministic logic was not artificially
modified.** Operator picks the actual Bundle 16.

## How this follows Crypto-D1 QA / Freeze Spec v1

1. Bundle 14 declared "Crypto-D1 Baseline Backtest Plan v1" as an
   allowed next step and defined the `QA_status` model +
   `QA_report_schema` this plan consumes.
2. This bundle authors the PLAN — pre-registration only; no
   backtest is executed, no data is fetched, no real data files or
   backtest outputs are created.
3. All seven safety flags from the protocol / data contract /
   dataset manifest / QA spec carry verbatim into this plan; an
   eighth renamed flag (`backtest_execution_enabled = false`)
   makes it explicit that EXECUTION itself is forbidden.
4. Lane scope identical: BTC / ETH / SOL, spot only, daily only,
   24/7.
5. `required_dataset_gate` explicitly pins `QA_status` to `QA_PASS`
   or approved `QA_WARN`; future backtest reports must cite all 5
   versions + `QA_report_id`.
6. `report_schema`'s 27 required fields include `protocol_version`,
   `data_contract_version`, `manifest_version`, and `QA_report_id`
   — so any future backtest report pins all four spec layers.
7. PASS rules require: no lookahead (Bundle 14 group B/C check),
   QA_PASS or approved QA_WARN (Bundle 14 model), full costs
   (Bundle 12 + 14 fee/slippage), trade-count floors,
   OOS-survives-IS, multi-asset robustness, drawdown within
   pre-declared limits, fee/slippage sensitivity, AND meaningful
   beat over buy-and-hold AFTER costs on a risk-adjusted basis.

## Recommended next bundle (Bundle 16 — use Codex, not Claude)

The next bundle implements the **Crypto-D1 Backtest Runner v1**
against a FROZEN, QA_PASS dataset. This is the FIRST code-heavy
bundle in the Crypto-D1 lane:

- Deterministic data loader (CSV / Parquet) against a manifest-
  validated dataset.
- Per-family strategy implementations (B / C / D / E + benchmark
  A; F WATCH-only).
- Cost / slippage model wired to the dataset's `fees.json`.
- IS / OOS split driver pinned to a pre-registered addendum.
- Walk-forward driver (gated behind a non-FAIL static-split
  verdict).
- Sensitivity sweep (fees ± N bps, slippage ± M bps).
- Report emitter that fills all 27 `report_schema.required_fields`
  and emits both `report.json` + `report.md` per strategy run.

**Strong recommendation: use Codex for Bundle 16, NOT Claude.** The
runner is code-heavy and benefits from Codex's strengths in
deterministic, structured-code generation.

Alternative spec-only bundles also available, each separately
authorized:

- **Crypto-D1 Data Collection Authorization Draft** — still
  spec-only; only if the operator wants to start the path toward an
  actual P2 acquisition. Does not authorize anything by itself.
- **Crypto-D1 Data Source Evaluation Memo v1** — written
  assessment of which offline data sources could later satisfy the
  QA / freeze spec. Memo only, no fetch.
