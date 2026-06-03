# SPARTA Crypto-D1 Backtest Runner v1 -- Run Report

> **Research-only. Local-only.** No data fetched. No exchange contacted. No order placed. No paper or live trading authorized.

- **run_id:** `2a3be425522a04ec`
- **generated_at:** 2026-06-03T20:47:44Z
- **runner_version:** crypto_d1_backtest_runner_v1
- **plan_version:** crypto_d1_baseline_backtest_plan_v1
- **protocol_version:** crypto_d1_protocol_v1
- **data_contract_version:** crypto_d1_data_contract_v1
- **dataset_manifest_spec_version:** crypto_d1_dataset_manifest_v1
- **qa_freeze_spec_version:** crypto_d1_qa_freeze_spec_v1
- **input_data_dir:** `data/crypto_d1_research/CRYPTO_D1_SPOT_BTC_ETH_SOL_V001/V002`
- **input_data_hash (short):** `2a3be425522a04ec`

## Config mode: `momentum_confirmation_v1`
- **batch:** Momentum confirmation pass, N=20/N=30 (momentum_confirmation_v1)
- **IS window:** 2021-06-17 -> 2024-06-16
- **OOS window:** 2024-06-17 -> 2025-12-31
- **cost per side (bps):** fee=40.0 + slip=10.0 + spread=10.0 = 60.0 (round-trip 120.0)
- **cost source:** v002_fees_json
- **strategies deferred:** volatility_regime_gate, mean_reversion
- **missing days (true gaps, never filled):** {'BTC': {'count': 1, 'dates': ['2024-03-31']}}

- **momentum lookbacks confirmed (pre-registered):** [20, 30]
- **primary basket benchmark:** buy_and_hold_basket_equal_weight
- **basket OOS reporting:** allocate_once_oos_window_split
- **per-family OOS trade counts (operator-side floor 30, NOT enforced in classify_run):**
  - `momentum_20`: total=86 meets_floor=True {'BTC': 32, 'ETH': 31, 'SOL': 23}
  - `momentum_30`: total=64 meets_floor=True {'BTC': 27, 'ETH': 19, 'SOL': 18}

## Safety flags (pinned)
- research_only: True
- data_fetch_enabled: False
- exchange_connection_enabled: False
- live_trading_enabled: False
- broker_control_enabled: False
- paper_order_execution_enabled: False
- order_placement_enabled: False

## Assets
- **seen:** BTC, ETH, SOL
- **missing:** (none)

## Verdict
- **pass_watch_fail_status:** **WATCH**
- **next_action:** 4 strategy result(s) show positive OOS + above-benchmark risk-adjusted return; this is INCOMPLETE evidence and does NOT promote the lane. PASS requires explicit operator review.

## Warnings
- BTC: missing 1 day(s) between 2024-03-30 and 2024-04-01 -- flagged, never silently forward-filled

## Benchmark results
- `buy_and_hold_benchmark_btc` (BTC): total_return=1.2841179309946296, max_drawdown=-0.7667251827270063, trade_count=1
- `buy_and_hold_benchmark_eth` (ETH): total_return=0.24339783051361863, max_drawdown=-0.7932916425063543, trade_count=1
- `buy_and_hold_benchmark_sol` (SOL): total_return=2.160833631484786, max_drawdown=-0.9627710983105888, trade_count=1
- `buy_and_hold_basket_equal_weight` (BASKET): total_return=1.2294497976643508, max_drawdown=-0.8836003042598654, trade_count=1

## Strategy results
- `momentum_20_btc` (BTC): total_return=30.08301972702824, oos_total_return=1.393056559049819, oos_trade_count=32
- `momentum_30_btc` (BTC): total_return=24.619967592325676, oos_total_return=1.3426920483046128, oos_trade_count=27
- `momentum_20_eth` (ETH): total_return=43.69140269134636, oos_total_return=1.6086095472227697, oos_trade_count=31
- `momentum_30_eth` (ETH): total_return=47.65396810815449, oos_total_return=2.135313725081248, oos_trade_count=19
- `momentum_20_sol` (SOL): total_return=1062.456733938877, oos_total_return=2.441737329704632, oos_trade_count=23
- `momentum_30_sol` (SOL): total_return=1297.0824583141775, oos_total_return=2.593327645039861, oos_trade_count=18

## Forbidden next steps
- Trade live or paper based on these results.
- Connect SPARTA's runtime to any exchange or vendor over the network.
- Promote crypto_d1_protocol to ACTIVE / STRONG without a separate operator decision.
- Schedule a daemon / cron / background process that touches this runner.
- Modify paper / live execution files.
- Install or read any API key, OAuth token, or .env credential.
- Use any synthetic / mock-priced data as evidence.

## Safety notes
- Research-only. Local-only.
- No data was fetched. No exchange was contacted. No order was placed.
- Results do not imply profitability. Crypto trend ideas are not profitable until tested with full costs AND forward-validated under a separately authorized future plan; neither is authorized by this runner.
- A future PASS verdict is not trading authorization.
