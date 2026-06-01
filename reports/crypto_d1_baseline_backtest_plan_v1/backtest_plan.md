# SPARTA Crypto-D1 Baseline Backtest Plan v1

> **Research-only. Baseline backtest PLAN / pre-registration only.**
> No broker control. No live trading. No paper-order execution. No exchange
> connection. No API keys. No `.env`. No credential handling. No scheduler /
> background daemon. **No external network calls. No data fetch. No backtest
> execution. No dataset processing. No real data files or backtest outputs
> created in this bundle.** This document pre-registers EXACTLY what the
> first future Crypto-D1 backtest runner must test, how results must be
> reported, and what PASS / WATCH / FAIL gates will apply — **before** any
> backtest is allowed to run.

**Backtest plan id:** `crypto_d1_baseline_backtest_plan_v1` · **version:** `1.0`

**Companion documents (read-only references):**
- `reports/crypto_d1_protocol_v1/{protocol.md, protocol.json}` — protocol.
- `reports/crypto_d1_data_contract_v1/{data_contract.md, data_contract.json}` — data contract.
- `reports/crypto_d1_dataset_manifest_v1/{dataset_manifest.md, dataset_manifest.json}` — dataset manifest spec.
- `reports/crypto_d1_qa_freeze_spec_v1/{qa_freeze_spec.md, qa_freeze_spec.json}` — QA / freeze spec.

---

## 1. Lane + scope

- **Lane:** `crypto_d1_protocol`.
- **Target assets:** **BTC**, **ETH**, **SOL** (all required).
- **Timeframe:** daily (`1d`) only. Intraday is **explicitly out of scope**.
- **Allowed market type:** `spot` only.
- **Forbidden market types:** perp futures, dated futures, options,
  leveraged tokens, margin / borrow-facilitated spot, synthetic
  instruments.

## 2. Required prior artifacts

This plan only makes sense layered on top of:

1. Bundle 11 — `reports/crypto_d1_protocol_v1/protocol.{json,md}`.
2. Bundle 12 — `reports/crypto_d1_data_contract_v1/data_contract.{json,md}`.
3. Bundle 13 — `reports/crypto_d1_dataset_manifest_v1/dataset_manifest.{json,md}`.
4. Bundle 14 — `reports/crypto_d1_qa_freeze_spec_v1/qa_freeze_spec.{json,md}`.

All four MUST exist on disk and each MUST `validate: OK`. The runner
bundle (separately-authorized) will check this gate at startup.

## 3. Required dataset gate (every future run)

Before any backtest in this plan may execute:

- A per-dataset folder under `data/crypto_d1_research/<dataset_id>/<dataset_version>/` MUST exist.
- `manifest.json` MUST be present and pass
  `tools/crypto_d1_dataset_manifest_check.py` (extended for per-dataset use).
- `qa_report.json` MUST be present (emitted by the future QA harness
  per Bundle 14).
- `manifest.freeze_status == "FROZEN"`.
- `manifest.QA_status == "QA_PASS"` OR `"QA_WARN"` with an explicit
  operator-acceptance note attached.
- The backtest report MUST cite: `dataset_id`, `dataset_version`,
  `data_contract_version`, `protocol_version`, `manifest_version`,
  `QA_report_id`.
- The QA harness's `no_lookahead` check MUST be in the cited
  `qa_report.json`'s `checks_passed` list.
- QA groups B (timestamp) / D (volume) / E (symbol-source) / G
  (freeze) blocking checks MUST all be in `checks_passed`.

## 4. Baseline strategy families

**Define, do not implement.** The runner bundle (separate, Codex-led)
implements these.

| ID | Status | Pre-registered shape |
|---|---|---|
| **A. `buy_and_hold_benchmark`** | benchmark | Long-only spot. BTC / ETH / SOL **separately** + an **equal-weight monthly-rebalanced basket**. Used as the comparison floor for every active strategy. NOT a candidate. |
| **B. `donchian_channel_breakout`** | primary | Entry: `close > N-day rolling high`. Exit: `close < M-day rolling low` OR trailing-channel exit. Daily close only; no intraday execution. Pre-registered grid: `N ∈ {20, 40, 60}`, `M ∈ {10, 20}`. No stop-loss in baseline. |
| **C. `moving_average_trend_filter`** | primary | Trade only when `close > long-EMA(W)`; flat otherwise. Long-only. Daily close only. Pre-registered grid: `W ∈ {50, 100, 200}`. Base signal under the filter: a documented trend follower (Donchian-lite or simple trailing trend). |
| **D. `momentum_continuation`** | primary | Long-only. Long if rolling-`k`-day return > 0 (optional skip-month); exit on signal flip. Daily close only. Pre-registered grid: `k ∈ {30, 90, 180}`, `skip ∈ {0, 7}`. |
| **E. `volatility_regime_gate`** | primary (additive filter) | Pass entry through only when rolling realised vol over the past `V` days is within a pre-declared band; otherwise stay flat. Tested **only as an additive filter** on (B) / (C) / (D); never standalone. Grid: `V ∈ {20, 60}`, vol band pre-declared per asset. |
| **F. `mean_reversion`** | **WATCH-only** | Pre-registered single-rule pullback entry; single-rule snap-back exit. Long-only. Daily close only. Pre-registered grid: pullback window `N ∈ {3, 5, 7}`. **WATCH-only**; never primary. **Must NOT revive any prior CODR-\* parameter set** — those lines were closed under `crypto_d7` / `crypto_d14` closeout memos. |

## 5. Parameter policy

- **Small pre-registered grid only.** Grids do not grow at runtime.
- **No unlimited optimization.**
- **No genetic / evolutionary search.**
- **No AI-selected best parameter after seeing OOS.**
- **No repeated tuning on OOS.**
- **Budget:** ≤ 3 free parameters per family at baseline; ≤ 10
  combinations per family.
- **All combinations logged** in the backtest report's `parameters`
  field; no silent dropouts.
- **Chosen parameter must be explainable** (e.g., "median of grid on
  IS"; **not** "best on OOS").
- **Baseline first, complexity later** — no cross-family combinations
  until each family has its own sealed PASS / WATCH / FAIL verdict.

## 6. Data and QA gate

Future backtest execution is allowed **only after**:

- The dataset exists on disk under the manifest's `source_location`.
- A dataset manifest exists and validates.
- A QA / freeze report exists.
- The dataset is `FROZEN`.
- `QA_PASS` OR explicitly approved `QA_WARN`.
- `dataset_id` and `dataset_version` are cited in the backtest report.
- Data contract version is cited.
- No-lookahead QA check passes.
- Duplicate / missing / timestamp checks pass.

## 7. IS / OOS and validation policy

- **In-sample / out-of-sample split** declared in writing before any
  run; window dates pin to the dataset's `time_start` / `time_end`.
- **No training on OOS.**
- **OOS unread until after IS verdict.**
- **Single OOS attempt per `dataset_version`** — re-running OOS after
  seeing results creates a new `dataset_version` OR the plan is
  treated as failed.
- **Walk-forward / rolling validation** is a SEPARATELY-authorized
  step AFTER the static IS / OOS split returns a non-FAIL verdict.
- **Minimum trade count:** ≥ 20 per asset, ≥ 30 per family on OOS.
- **Multiple assets checked separately AND combined**; no
  single-asset-only PASS unless explicitly WATCH.
- **Crypto market regimes** are acknowledged. A 2020–2025 framing
  MAY be mentioned only as future planning context — **no current
  data claim** is made by this bundle. If used, the IS / OOS split
  MUST avoid a single-bubble-regime IS or OOS unless flagged WATCH.

## 8. Cost and slippage model

- **Spot taker fee assumption required** per venue, dated, pre-
  declared in the dataset's `fees.json`.
- **Default sizing assumption: TAKER on every leg.** Optional maker
  fee recorded only when a strategy variant pre-registers maker
  fills.
- **Slippage assumption required** — conservative slow-day haircut
  (constant-bps + one-tick).
- **Spread proxy required** when quote data is unavailable —
  constant-bps proxy declared per asset; conservative.
- **Depth-aware slippage** replaces the constant-bps proxy if L2
  quote data is attached.
- **Cost-sensitivity checks required**: fees ± N bps, slippage ± M
  bps; result must survive.
- **Fees as a distinct PnL line.**
- **No PASS allowed if costs are ignored.**

## 9. Position sizing and risk

- **No leverage.**
- **Long-only spot first.** **No shorting** in this protocol.
- Future sizing options: equal-notional (default; pre-declared) or
  volatility-scaled (future option; pre-declared with target vol
  band).
- Max position exposure: 100% of cash per asset; max basket
  exposure: 100% of cash.
- **Cash / risk-off state required** — when no signal active, the
  portfolio sits in cash (no implicit leverage; no short proxy).
- **Drawdown measurement required**: per-asset and per-basket
  daily-bar max drawdown.
- **Per-asset and portfolio drawdown kill** pre-declared (logged
  kill-switch, not a future trade trigger).
- **Tail-risk disclosure required** in every future report (worst-
  day / week / month + at least one named stress scenario).
- **No post-hoc stop-loss addition.**
- **No compounding tricks** unless explicitly documented.

## 10. Required metrics (17)

Every future per-strategy backtest report includes:

`CAGR_or_total_return`, `annualized_volatility`, `max_drawdown`,
`sharpe_like_risk_metric_with_caveats`, `win_rate`, `trade_count`,
`average_trade_return`, `median_trade_return`,
`exposure_percentage`, `turnover`, `fee_slippage_paid`,
`OOS_return`, `OOS_drawdown`, `per_asset_results`, `basket_results`,
`benchmark_comparison`, `sensitivity_summary`.

## 11. Report schema (27 required fields)

Every future per-strategy `report.json` MUST populate **all 27**:

`run_id`, `strategy_id`, `dataset_id`, `dataset_version`,
`protocol_version`, `data_contract_version`, `manifest_version`,
`QA_report_id`, `generated_at`, `assets`, `timeframe`,
`market_type`, `strategy_family`, `parameters`, `cost_model`,
`slippage_model`, `IS_period`, `OOS_period`, `metrics`,
`per_asset_metrics`, `benchmark_metrics`, `pass_watch_fail_status`,
`failure_reasons`, `warnings`, `next_action`, `forbidden_next_steps`,
`safety_flags`.

## 12. PASS / WATCH / FAIL rules

- **PASS** — All of: data was FROZEN + QA_PASS (or approved
  QA_WARN); no lookahead; full costs (fees + slippage); enough
  trades (≥ 30 per family, ≥ 20 per asset on OOS); OOS survives the
  IS pattern in sign + magnitude within a pre-registered tolerance;
  result does NOT depend on a single asset; drawdown within pre-
  declared per-asset and portfolio limits; robust to fees ± N bps
  and slippage ± M bps; rules remain simple + explainable; no rule
  was changed mid-study; **AND** the strategy meaningfully **beats
  buy-and-hold AFTER costs on a risk-adjusted basis**.
- **WATCH** — Promising but at least one of: OOS materially weaker
  than IS; one asset works, others do not; trade count below the
  WATCH-floor; sensitive to small fee / slippage changes; high
  drawdown but possibly improvable; market-regime dependent; or
  buy-and-hold beaten only on raw return, not risk-adjusted.
- **FAIL** — No OOS edge; excessive drawdown (above pre-declared
  kill); overfit parameters (grid edge or post-hoc selection); only
  works in one bubble regime; edge disappears with realistic costs;
  insufficient trades; **worse than buy-and-hold after risk
  adjustment**; OOS window peeked before sealing; or any safety
  flag tripped.

## 13. Kill conditions

- OOS window is peeked before sealing.
- Parameter sweep extends beyond the pre-registered grid.
- Backtest cannot be reproduced bit-for-bit by a second offline
  run on the same `dataset_version`.
- An assumption (no-fee, no-slippage, no-borrow, no-funding for
  spot) is silently dropped.
- Edge depends on data that has been manually edited without
  documentation + revalidation.
- Any safety flag flips to True in the runner.

## 14. Forbidden actions (this bundle and any runner that cites it)

- Fetch data from any live exchange API.
- Connect SPARTA's runtime to any exchange or vendor over the
  network.
- **Execute a backtest from this bundle** — this bundle is a PLAN
  only; the runner is a SEPARATE, separately-authorized bundle.
- Run any paper-order or live-trading flow on the basis of any
  future PASS alone.
- Modify paper / live execution files.
- Schedule any background daemon or cron job.
- Install or read any API key, OAuth token, or `.env` credential.
- Use any synthetic / mock-priced data as evidence.
- **Revive any prior CODR-\* parameter set** (mean-reversion
  lineage) under the v1 plan.
- Promote `crypto_d1_protocol` to ACTIVE / STRONG by this bundle's
  existence alone.

## 15. Candidate-registry update rules

- Adding this plan to the registry's `extra_files` does **NOT**
  promote `crypto_d1_protocol` to ACTIVE; lane stays **WATCH**.
- Never ACTIVE in the auto path.
- Never STRONG in the auto path.
- Promotion to ACTIVE requires a future per-strategy backtest
  `report.json` + `report.md` PASS verdict AND an explicit operator
  decision; **not produced by this bundle.**

## 16. No-profit-claim policy

- **This plan does not imply edge.**
- **No backtest is run by this bundle.**
- **No historical result is produced by this bundle.**
- **A future PASS is not trading authorization.**
- **No paper/live trading is authorized.**
- **No data fetch is authorized.**
- **Crypto trend ideas are not profitable until tested.**
- **A good historical chart does not imply future returns.**

## 17. Required future artifacts

- **Crypto-D1 Backtest Runner v1** (P3 / P4 / P5) — CODE bundle that
  implements the runner against a FROZEN QA_PASS dataset
  (separately authorized; **recommend using Codex for the next
  bundle, not Claude, since it will be code-heavy**).
- **Per-strategy backtest `report.json` + `report.md`** following
  the report_schema declared here (P3 / P4 OUTPUT; separately
  authorized).
- **IS / OOS window addendum** — explicit IS / OOS date ranges
  pinned to a specific `dataset_id` + `dataset_version`; can fold
  into the runner bundle or its own pre-registration memo.
- **Crypto-D1 Data Source Evaluation Memo v1** — written assessment
  of which offline data sources could later satisfy the QA / freeze
  spec (memo only, no fetch).
- **Crypto-D1 Data Acquisition Authorization Draft** — still spec-
  only; only if the operator wants to start the path toward an
  actual P2 acquisition.

## 18. Safety boundaries (pinned, non-negotiable)

- Research-only. Baseline backtest PLAN / pre-registration only.
- No broker control, no exchange connection, no API keys, no
  `.env`, no credential handling.
- No live trading. No paper-order execution. No order placement.
- No scheduler / background daemon. No external network calls in
  this plan's runtime.
- **No data fetch. No backtest execution. No dataset processing.
  No real data files or backtest outputs created in this bundle.**
- Do not modify paper / live execution files.
- Do not claim profitability. Do not claim live-readiness. Do not
  claim STRONG evidence from this plan alone.
- **This plan does not imply edge. No backtest is run by this
  bundle. No historical result is produced by this bundle. A future
  PASS is not trading authorization. No paper/live trading is
  authorized. No data fetch is authorized. Crypto trend ideas are
  not profitable until tested with full costs. A good historical
  chart does not imply future returns. 24/7** crypto session
  handling; weekday-only filters forbidden.
