# C22 — B3 Stage Four: Fees / Tick-Lot-Min / Liquidity / Spread (run 20260911T131902Z)

Frozen steps ['5_fee_tick_lot_minimum_rules', '6_liquidity_and_spread_evidence'] (batch C22_FEES_AND_LIQUIDITY_FETCH_READY_FOR_HUMAN_AUTHORIZATION, token name HUMAN_DECISION_C22_FEES_AND_LIQUIDITY_FETCH_AUTHORIZE). Read-only. No performance, no cost arithmetic, no assumptions selected, no admission change.

- Fee evidence: {"current_fee_not_exposed_by_public_api": 16, "current_fee_only_available": 4, "historical_fee_proven": 0, "historical_fee_unresolved": 20, "instruments": 20}
- Tick/lot/minimum evidence: {"change_timestamp_after_window": [], "current_constraint_only": 20, "historical_constraint_proven": 0, "historical_constraint_unresolved": 20, "instruments": 20}
- Spread evidence: {"bbo_spread_observed": 0, "depth_proxy_observed_binance_bookdepth": 36, "fill_windows": 50, "unresolved_no_first_party_book": 14}
- Liquidity evidence: {"fill_windows": 50, "no_activity_in_window": 1, "observed_first_party": 49, "unresolved": 0}
- Verdicts: {"FAIL_NO_MARKET_ACTIVITY_AT_FILL": 1, "NOT_ELIGIBLE_PRIOR_STAGE": 3, "UNRESOLVED_HISTORICAL_FEE": 71}

## Step 5 per instrument

| asset | instrument | fee historical | fee current | fee values | constraint historical | current tick/lot/min | change ts |
|---|---|---|---|---|---|---|---|
| BINANCE:AAVEUSDT | AAVEUSDT @ BINANCE | HISTORICAL_FEE_UNRESOLVED | CURRENT_FEE_NOT_EXPOSED_BY_PUBLIC_API | null | HISTORICAL_CONSTRAINT_UNRESOLVED | {"tick_size": 0.01, "lot_step": 0.1, "min_qty": 0.1, "min_notional": 5.0} | None |
| BINANCE:CRVUSDT | CRVUSDT @ BINANCE | HISTORICAL_FEE_UNRESOLVED | CURRENT_FEE_NOT_EXPOSED_BY_PUBLIC_API | null | HISTORICAL_CONSTRAINT_UNRESOLVED | {"tick_size": 0.0001, "lot_step": 0.1, "min_qty": 0.1, "min_notional": 5.0} | None |
| BINANCE:IMXUSDT | IMXUSDT @ BINANCE | HISTORICAL_FEE_UNRESOLVED | CURRENT_FEE_NOT_EXPOSED_BY_PUBLIC_API | null | HISTORICAL_CONSTRAINT_UNRESOLVED | {"tick_size": 0.0001, "lot_step": 1.0, "min_qty": 1.0, "min_notional": 5.0} | None |
| BINANCE:INJUSDT | INJUSDT @ BINANCE | HISTORICAL_FEE_UNRESOLVED | CURRENT_FEE_NOT_EXPOSED_BY_PUBLIC_API | null | HISTORICAL_CONSTRAINT_UNRESOLVED | {"tick_size": 0.001, "lot_step": 0.1, "min_qty": 0.1, "min_notional": 5.0} | None |
| BINANCE:LINKUSDT | LINKUSDT @ BINANCE | HISTORICAL_FEE_UNRESOLVED | CURRENT_FEE_NOT_EXPOSED_BY_PUBLIC_API | null | HISTORICAL_CONSTRAINT_UNRESOLVED | {"tick_size": 0.001, "lot_step": 0.01, "min_qty": 0.01, "min_notional": 20.0} | None |
| BINANCE:PENDLEUSDT | PENDLEUSDT @ BINANCE | HISTORICAL_FEE_UNRESOLVED | CURRENT_FEE_NOT_EXPOSED_BY_PUBLIC_API | null | HISTORICAL_CONSTRAINT_UNRESOLVED | {"tick_size": 0.0001, "lot_step": 1.0, "min_qty": 1.0, "min_notional": 5.0} | None |
| BINANCE:QNTUSDT | QNTUSDT @ BINANCE | HISTORICAL_FEE_UNRESOLVED | CURRENT_FEE_NOT_EXPOSED_BY_PUBLIC_API | null | HISTORICAL_CONSTRAINT_UNRESOLVED | {"tick_size": 0.01, "lot_step": 0.1, "min_qty": 0.1, "min_notional": 5.0} | None |
| BINANCE:SOLUSDT | SOLUSDT @ BINANCE | HISTORICAL_FEE_UNRESOLVED | CURRENT_FEE_NOT_EXPOSED_BY_PUBLIC_API | null | HISTORICAL_CONSTRAINT_UNRESOLVED | {"tick_size": 0.01, "lot_step": 0.01, "min_qty": 0.01, "min_notional": 5.0} | None |
| BINANCE:SUNUSDT | SUNUSDT @ BINANCE | HISTORICAL_FEE_UNRESOLVED | CURRENT_FEE_NOT_EXPOSED_BY_PUBLIC_API | null | HISTORICAL_CONSTRAINT_UNRESOLVED | {"tick_size": 1e-06, "lot_step": 1.0, "min_qty": 1.0, "min_notional": 5.0} | None |
| BINANCE:TIAUSDT | TIAUSDT @ BINANCE | HISTORICAL_FEE_UNRESOLVED | CURRENT_FEE_NOT_EXPOSED_BY_PUBLIC_API | null | HISTORICAL_CONSTRAINT_UNRESOLVED | {"tick_size": 0.0001, "lot_step": 1.0, "min_qty": 1.0, "min_notional": 5.0} | None |
| BINANCE:TRXUSDT | TRXUSDT @ BINANCE | HISTORICAL_FEE_UNRESOLVED | CURRENT_FEE_NOT_EXPOSED_BY_PUBLIC_API | null | HISTORICAL_CONSTRAINT_UNRESOLVED | {"tick_size": 1e-05, "lot_step": 1.0, "min_qty": 1.0, "min_notional": 5.0} | None |
| BINANCE:VIRTUALUSDT | VIRTUALUSDT @ BINANCE | HISTORICAL_FEE_UNRESOLVED | CURRENT_FEE_NOT_EXPOSED_BY_PUBLIC_API | null | HISTORICAL_CONSTRAINT_UNRESOLVED | {"tick_size": 0.0001, "lot_step": 0.1, "min_qty": 0.1, "min_notional": 5.0} | None |
| BINANCE:ZECUSDT | ZECUSDT @ BINANCE | HISTORICAL_FEE_UNRESOLVED | CURRENT_FEE_NOT_EXPOSED_BY_PUBLIC_API | null | HISTORICAL_CONSTRAINT_UNRESOLVED | {"tick_size": 0.01, "lot_step": 0.001, "min_qty": 0.001, "min_notional": 5.0} | None |
| BITFINEX:LEOUSD | tLEOUSD @ BITFINEX | HISTORICAL_FEE_UNRESOLVED | CURRENT_FEE_NOT_EXPOSED_BY_PUBLIC_API | null | HISTORICAL_CONSTRAINT_UNRESOLVED | {"tick_size": null, "lot_step": null, "min_qty": 0.6, "max_qty": 50000.0, "min_notional": null} | None |
| BYBIT:GRAMUSDT | GRAMUSDT @ BYBIT | HISTORICAL_FEE_UNRESOLVED | CURRENT_FEE_NOT_EXPOSED_BY_PUBLIC_API | null | HISTORICAL_CONSTRAINT_UNRESOLVED | {"tick_size": 0.001, "lot_step": 0.1, "min_qty": 0.1, "min_notional": 5.0} | None |
| GATE:ASTERUSDT | ASTER_USDT @ GATE | HISTORICAL_FEE_UNRESOLVED | CURRENT_FEE_ONLY | {"maker": -0.0001, "taker": 0.00075} | HISTORICAL_CONSTRAINT_UNRESOLVED | {"tick_size": 0.0001, "lot_step": 1.0, "min_qty": 1.0, "contract_multiplier": 10.0, "min_notional": null} | 2026-09-01 |
| GATE:GTUSDT | GT_USDT @ GATE | HISTORICAL_FEE_UNRESOLVED | CURRENT_FEE_ONLY | {"maker": -0.0001, "taker": 0.00075} | HISTORICAL_CONSTRAINT_UNRESOLVED | {"tick_size": 0.001, "lot_step": 1.0, "min_qty": 1.0, "contract_multiplier": 0.1, "min_notional": null} | 2026-09-09 |
| KRAKEN:KASUSD | PF_KASUSD @ KRAKEN_FUTURES | HISTORICAL_FEE_UNRESOLVED | CURRENT_FEE_ONLY | {"schedule": "MTF Linear Rebate Fees", "tier0_maker": 0.02, "tier0_taker": 0.05} | HISTORICAL_CONSTRAINT_UNRESOLVED | {"tick_size": 1e-05, "lot_step": 1, "min_qty": null, "impact_mid_size": 64600.0, "min_notional": null} | None |
| KRAKEN:SPXUSD | PF_SPXUSD @ KRAKEN_FUTURES | HISTORICAL_FEE_UNRESOLVED | CURRENT_FEE_ONLY | {"schedule": "MTF Linear Rebate Fees", "tier0_maker": 0.02, "tier0_taker": 0.05} | HISTORICAL_CONSTRAINT_UNRESOLVED | {"tick_size": 0.0001, "lot_step": 1, "min_qty": null, "impact_mid_size": 6300.0, "min_notional": null} | None |
| OKX:OKBUSDT | OKB-USDT-SWAP @ OKX | HISTORICAL_FEE_UNRESOLVED | CURRENT_FEE_NOT_EXPOSED_BY_PUBLIC_API | null | HISTORICAL_CONSTRAINT_UNRESOLVED | {"tick_size": 0.01, "lot_step": 1.0, "min_qty": 1.0, "contract_value": 0.01, "min_notional": null} | None |

## Step 6 per fill window (30 minutes after 00:00 UTC of the fill date)

| instrument | fill date | liquidity | class | trades / depth summary | spread |
|---|---|---|---|---|---|
| QNTUSDT @ BINANCE | 2026-06-21 | LIQUIDITY_OBSERVED_FIRST_PARTY | DERIVED_FROM_OBSERVED_DATA | {"snapshot_utc": "2026-06-21 00:00:04", "bid_notional_within_0_2pct": 5073.139, "ask_notional_within_0_2pct": 21622.12} | DEPTH_AT_PERCENT_LEVELS_OBSERVED_NOT_BBO_SPREAD |
| QNTUSDT @ BINANCE | 2026-06-22 | LIQUIDITY_OBSERVED_FIRST_PARTY | DERIVED_FROM_OBSERVED_DATA | {"snapshot_utc": "2026-06-22 00:00:04", "bid_notional_within_0_2pct": 4022.816, "ask_notional_within_0_2pct": 14244.256} | DEPTH_AT_PERCENT_LEVELS_OBSERVED_NOT_BBO_SPREAD |
| ASTER_USDT @ GATE | 2026-06-22 | LIQUIDITY_OBSERVED_FIRST_PARTY | OBSERVED_FIRST_PARTY | {"trade_count": 156, "first_trade_utc": "2026-06-22T00:00:17.802000+00:00", "last_trade_utc": "2026-06-22T00:29:30.923000+00:00", "price_min": 0.6358, "price_ma | UNRESOLVED_NO_FIRST_PARTY_HISTORICAL_BOOK |
| OKB-USDT-SWAP @ OKX | 2026-06-24 | LIQUIDITY_OBSERVED_FIRST_PARTY | OBSERVED_FIRST_PARTY | {"trade_count": 600, "first_trade_utc": "2026-06-24T00:23:05.988000+00:00", "last_trade_utc": "2026-06-24T00:29:55.680000+00:00", "price_min": 77.54, "price_max | UNRESOLVED_NO_FIRST_PARTY_HISTORICAL_BOOK |
| TIAUSDT @ BINANCE | 2026-06-29 | LIQUIDITY_OBSERVED_FIRST_PARTY | DERIVED_FROM_OBSERVED_DATA | {"snapshot_utc": "2026-06-29 00:00:04", "bid_notional_within_0_2pct": 22153.0255, "ask_notional_within_0_2pct": 31377.8601} | DEPTH_AT_PERCENT_LEVELS_OBSERVED_NOT_BBO_SPREAD |
| TIAUSDT @ BINANCE | 2026-07-01 | LIQUIDITY_OBSERVED_FIRST_PARTY | DERIVED_FROM_OBSERVED_DATA | {"snapshot_utc": "2026-07-01 00:00:04", "bid_notional_within_0_2pct": 39452.1512, "ask_notional_within_0_2pct": 38212.3373} | DEPTH_AT_PERCENT_LEVELS_OBSERVED_NOT_BBO_SPREAD |
| PF_SPXUSD @ KRAKEN_FUTURES | 2026-06-29 | LIQUIDITY_OBSERVED_FIRST_PARTY | OBSERVED_FIRST_PARTY | {"trade_count": 8, "first_trade_utc": "2026-06-29T00:03:16.804000+00:00", "last_trade_utc": "2026-06-29T00:20:52.342000+00:00", "price_min": 0.3299, "price_max" | UNRESOLVED_NO_FIRST_PARTY_HISTORICAL_BOOK |
| PF_SPXUSD @ KRAKEN_FUTURES | 2026-07-04 | LIQUIDITY_OBSERVED_FIRST_PARTY | OBSERVED_FIRST_PARTY | {"trade_count": 8, "first_trade_utc": "2026-07-04T00:00:15.130000+00:00", "last_trade_utc": "2026-07-04T00:08:25.847000+00:00", "price_min": 0.4079, "price_max" | UNRESOLVED_NO_FIRST_PARTY_HISTORICAL_BOOK |
| PF_SPXUSD @ KRAKEN_FUTURES | 2026-07-06 | LIQUIDITY_OBSERVED_FIRST_PARTY | OBSERVED_FIRST_PARTY | {"trade_count": 6, "first_trade_utc": "2026-07-06T00:00:48.858000+00:00", "last_trade_utc": "2026-07-06T00:25:38.709000+00:00", "price_min": 0.3894, "price_max" | UNRESOLVED_NO_FIRST_PARTY_HISTORICAL_BOOK |
| TIAUSDT @ BINANCE | 2026-07-02 | LIQUIDITY_OBSERVED_FIRST_PARTY | DERIVED_FROM_OBSERVED_DATA | {"snapshot_utc": "2026-07-02 00:00:04", "bid_notional_within_0_2pct": 29165.1405, "ask_notional_within_0_2pct": 31736.7435} | DEPTH_AT_PERCENT_LEVELS_OBSERVED_NOT_BBO_SPREAD |
| TIAUSDT @ BINANCE | 2026-07-05 | LIQUIDITY_OBSERVED_FIRST_PARTY | DERIVED_FROM_OBSERVED_DATA | {"snapshot_utc": "2026-07-05 00:00:04", "bid_notional_within_0_2pct": 34493.074, "ask_notional_within_0_2pct": 35160.764} | DEPTH_AT_PERCENT_LEVELS_OBSERVED_NOT_BBO_SPREAD |
| TIAUSDT @ BINANCE | 2026-07-07 | LIQUIDITY_OBSERVED_FIRST_PARTY | DERIVED_FROM_OBSERVED_DATA | {"snapshot_utc": "2026-07-07 00:00:04", "bid_notional_within_0_2pct": 137774.1231, "ask_notional_within_0_2pct": 32469.2413} | DEPTH_AT_PERCENT_LEVELS_OBSERVED_NOT_BBO_SPREAD |
| SOLUSDT @ BINANCE | 2026-07-03 | LIQUIDITY_OBSERVED_FIRST_PARTY | DERIVED_FROM_OBSERVED_DATA | {"snapshot_utc": "2026-07-03 00:00:04", "bid_notional_within_0_2pct": 3374874.0518, "ask_notional_within_0_2pct": 3090772.4213} | DEPTH_AT_PERCENT_LEVELS_OBSERVED_NOT_BBO_SPREAD |
| SOLUSDT @ BINANCE | 2026-07-05 | LIQUIDITY_OBSERVED_FIRST_PARTY | DERIVED_FROM_OBSERVED_DATA | {"snapshot_utc": "2026-07-05 00:00:04", "bid_notional_within_0_2pct": 3029645.3071, "ask_notional_within_0_2pct": 4290461.7919} | DEPTH_AT_PERCENT_LEVELS_OBSERVED_NOT_BBO_SPREAD |
| SOLUSDT @ BINANCE | 2026-07-07 | LIQUIDITY_OBSERVED_FIRST_PARTY | DERIVED_FROM_OBSERVED_DATA | {"snapshot_utc": "2026-07-07 00:00:04", "bid_notional_within_0_2pct": 3309474.9396, "ask_notional_within_0_2pct": 3404581.2726} | DEPTH_AT_PERCENT_LEVELS_OBSERVED_NOT_BBO_SPREAD |
| PENDLEUSDT @ BINANCE | 2026-07-04 | LIQUIDITY_OBSERVED_FIRST_PARTY | DERIVED_FROM_OBSERVED_DATA | {"snapshot_utc": "2026-07-04 00:00:04", "bid_notional_within_0_2pct": 38724.2829, "ask_notional_within_0_2pct": 20754.057} | DEPTH_AT_PERCENT_LEVELS_OBSERVED_NOT_BBO_SPREAD |
| PENDLEUSDT @ BINANCE | 2026-07-10 | LIQUIDITY_OBSERVED_FIRST_PARTY | DERIVED_FROM_OBSERVED_DATA | {"snapshot_utc": "2026-07-10 00:00:03", "bid_notional_within_0_2pct": 23916.7485, "ask_notional_within_0_2pct": 33178.6119} | DEPTH_AT_PERCENT_LEVELS_OBSERVED_NOT_BBO_SPREAD |
| PENDLEUSDT @ BINANCE | 2026-07-06 | LIQUIDITY_OBSERVED_FIRST_PARTY | DERIVED_FROM_OBSERVED_DATA | {"snapshot_utc": "2026-07-06 00:00:04", "bid_notional_within_0_2pct": 16513.4447, "ask_notional_within_0_2pct": 16455.8238} | DEPTH_AT_PERCENT_LEVELS_OBSERVED_NOT_BBO_SPREAD |
| GT_USDT @ GATE | 2026-07-05 | LIQUIDITY_OBSERVED_FIRST_PARTY | OBSERVED_FIRST_PARTY | {"trade_count": 5, "first_trade_utc": "2026-07-05T00:05:40.777000+00:00", "last_trade_utc": "2026-07-05T00:15:27.579000+00:00", "price_min": 6.743, "price_max": | UNRESOLVED_NO_FIRST_PARTY_HISTORICAL_BOOK |
| GT_USDT @ GATE | 2026-07-20 | LIQUIDITY_OBSERVED_FIRST_PARTY | OBSERVED_FIRST_PARTY | {"trade_count": 55, "first_trade_utc": "2026-07-20T00:00:10.687000+00:00", "last_trade_utc": "2026-07-20T00:28:58.623000+00:00", "price_min": 6.686, "price_max" | UNRESOLVED_NO_FIRST_PARTY_HISTORICAL_BOOK |
| GT_USDT @ GATE | 2026-07-06 | LIQUIDITY_OBSERVED_FIRST_PARTY | OBSERVED_FIRST_PARTY | {"trade_count": 13, "first_trade_utc": "2026-07-06T00:03:14.842000+00:00", "last_trade_utc": "2026-07-06T00:25:00.659000+00:00", "price_min": 6.713, "price_max" | UNRESOLVED_NO_FIRST_PARTY_HISTORICAL_BOOK |
| GT_USDT @ GATE | 2026-07-23 | LIQUIDITY_OBSERVED_FIRST_PARTY | OBSERVED_FIRST_PARTY | {"trade_count": 1, "first_trade_utc": "2026-07-23T00:00:09.308000+00:00", "last_trade_utc": "2026-07-23T00:00:09.308000+00:00", "price_min": 6.659, "price_max": | UNRESOLVED_NO_FIRST_PARTY_HISTORICAL_BOOK |
| CRVUSDT @ BINANCE | 2026-07-06 | LIQUIDITY_OBSERVED_FIRST_PARTY | DERIVED_FROM_OBSERVED_DATA | {"snapshot_utc": "2026-07-06 00:00:04", "bid_notional_within_0_2pct": 32261.30922, "ask_notional_within_0_2pct": 24347.98893} | DEPTH_AT_PERCENT_LEVELS_OBSERVED_NOT_BBO_SPREAD |
| CRVUSDT @ BINANCE | 2026-07-16 | LIQUIDITY_OBSERVED_FIRST_PARTY | DERIVED_FROM_OBSERVED_DATA | {"snapshot_utc": "2026-07-16 00:00:03", "bid_notional_within_0_2pct": 27988.52746, "ask_notional_within_0_2pct": 46402.19837} | DEPTH_AT_PERCENT_LEVELS_OBSERVED_NOT_BBO_SPREAD |
| GRAMUSDT @ BYBIT | 2026-07-06 | LIQUIDITY_OBSERVED_FIRST_PARTY | OBSERVED_FIRST_PARTY | {"trade_count": 4496, "first_trade_utc": "2026-07-06T00:00:01.196000+00:00", "last_trade_utc": "2026-07-06T00:29:57.241000+00:00", "price_min": 1.77, "price_max | UNRESOLVED_NO_FIRST_PARTY_HISTORICAL_BOOK |
| PF_KASUSD @ KRAKEN_FUTURES | 2026-07-06 | FAIL_NO_MARKET_ACTIVITY_IN_FILL_WINDOW | OBSERVED_FIRST_PARTY | {"trade_count": 0, "summary_class": "DERIVED_FROM_OBSERVED_DATA"} | UNRESOLVED_NO_FIRST_PARTY_HISTORICAL_BOOK |
| IMXUSDT @ BINANCE | 2026-07-07 | LIQUIDITY_OBSERVED_FIRST_PARTY | DERIVED_FROM_OBSERVED_DATA | {"snapshot_utc": "2026-07-07 00:00:04", "bid_notional_within_0_2pct": 13418.0748, "ask_notional_within_0_2pct": 4789.7073} | DEPTH_AT_PERCENT_LEVELS_OBSERVED_NOT_BBO_SPREAD |
| IMXUSDT @ BINANCE | 2026-07-30 | LIQUIDITY_OBSERVED_FIRST_PARTY | DERIVED_FROM_OBSERVED_DATA | {"snapshot_utc": "2026-07-30 00:00:01", "bid_notional_within_0_2pct": 5893.4743, "ask_notional_within_0_2pct": 7698.3392} | DEPTH_AT_PERCENT_LEVELS_OBSERVED_NOT_BBO_SPREAD |
| SUNUSDT @ BINANCE | 2026-07-07 | LIQUIDITY_OBSERVED_FIRST_PARTY | DERIVED_FROM_OBSERVED_DATA | {"snapshot_utc": "2026-07-07 00:00:04", "bid_notional_within_0_2pct": 14313.438513, "ask_notional_within_0_2pct": 10942.978276} | DEPTH_AT_PERCENT_LEVELS_OBSERVED_NOT_BBO_SPREAD |
| SUNUSDT @ BINANCE | 2026-07-09 | LIQUIDITY_OBSERVED_FIRST_PARTY | DERIVED_FROM_OBSERVED_DATA | {"snapshot_utc": "2026-07-09 00:00:06", "bid_notional_within_0_2pct": 11413.720726, "ask_notional_within_0_2pct": 9155.159161} | DEPTH_AT_PERCENT_LEVELS_OBSERVED_NOT_BBO_SPREAD |
| TRXUSDT @ BINANCE | 2026-07-07 | LIQUIDITY_OBSERVED_FIRST_PARTY | DERIVED_FROM_OBSERVED_DATA | {"snapshot_utc": "2026-07-07 00:00:04", "bid_notional_within_0_2pct": 360795.36805, "ask_notional_within_0_2pct": 336433.99363} | DEPTH_AT_PERCENT_LEVELS_OBSERVED_NOT_BBO_SPREAD |
| TRXUSDT @ BINANCE | 2026-07-26 | LIQUIDITY_OBSERVED_FIRST_PARTY | DERIVED_FROM_OBSERVED_DATA | {"snapshot_utc": "2026-07-26 00:00:01", "bid_notional_within_0_2pct": 262141.27025, "ask_notional_within_0_2pct": 281594.82971} | DEPTH_AT_PERCENT_LEVELS_OBSERVED_NOT_BBO_SPREAD |
| TRXUSDT @ BINANCE | 2026-07-28 | LIQUIDITY_OBSERVED_FIRST_PARTY | DERIVED_FROM_OBSERVED_DATA | {"snapshot_utc": "2026-07-28 00:00:01", "bid_notional_within_0_2pct": 369086.28953, "ask_notional_within_0_2pct": 335341.32092} | DEPTH_AT_PERCENT_LEVELS_OBSERVED_NOT_BBO_SPREAD |
| TIAUSDT @ BINANCE | 2026-07-09 | LIQUIDITY_OBSERVED_FIRST_PARTY | DERIVED_FROM_OBSERVED_DATA | {"snapshot_utc": "2026-07-09 00:00:06", "bid_notional_within_0_2pct": 31142.0481, "ask_notional_within_0_2pct": 27848.7637} | DEPTH_AT_PERCENT_LEVELS_OBSERVED_NOT_BBO_SPREAD |
| TIAUSDT @ BINANCE | 2026-07-11 | LIQUIDITY_OBSERVED_FIRST_PARTY | DERIVED_FROM_OBSERVED_DATA | {"snapshot_utc": "2026-07-11 00:00:03", "bid_notional_within_0_2pct": 50753.8449, "ask_notional_within_0_2pct": 34540.1695} | DEPTH_AT_PERCENT_LEVELS_OBSERVED_NOT_BBO_SPREAD |
| TIAUSDT @ BINANCE | 2026-07-13 | LIQUIDITY_OBSERVED_FIRST_PARTY | DERIVED_FROM_OBSERVED_DATA | {"snapshot_utc": "2026-07-13 00:00:03", "bid_notional_within_0_2pct": 38689.5286, "ask_notional_within_0_2pct": 42875.293} | DEPTH_AT_PERCENT_LEVELS_OBSERVED_NOT_BBO_SPREAD |
| ZECUSDT @ BINANCE | 2026-07-09 | LIQUIDITY_OBSERVED_FIRST_PARTY | DERIVED_FROM_OBSERVED_DATA | {"snapshot_utc": "2026-07-09 00:00:06", "bid_notional_within_0_2pct": 481289.23922, "ask_notional_within_0_2pct": 557106.51341} | DEPTH_AT_PERCENT_LEVELS_OBSERVED_NOT_BBO_SPREAD |
| ZECUSDT @ BINANCE | 2026-07-12 | LIQUIDITY_OBSERVED_FIRST_PARTY | DERIVED_FROM_OBSERVED_DATA | {"snapshot_utc": "2026-07-12 00:00:03", "bid_notional_within_0_2pct": 1114656.20875, "ask_notional_within_0_2pct": 532912.86422} | DEPTH_AT_PERCENT_LEVELS_OBSERVED_NOT_BBO_SPREAD |
| ZECUSDT @ BINANCE | 2026-07-14 | LIQUIDITY_OBSERVED_FIRST_PARTY | DERIVED_FROM_OBSERVED_DATA | {"snapshot_utc": "2026-07-14 00:00:03", "bid_notional_within_0_2pct": 444921.67701, "ask_notional_within_0_2pct": 648459.89138} | DEPTH_AT_PERCENT_LEVELS_OBSERVED_NOT_BBO_SPREAD |
| INJUSDT @ BINANCE | 2026-07-12 | LIQUIDITY_OBSERVED_FIRST_PARTY | DERIVED_FROM_OBSERVED_DATA | {"snapshot_utc": "2026-07-12 00:00:03", "bid_notional_within_0_2pct": 55289.0622, "ask_notional_within_0_2pct": 56128.4286} | DEPTH_AT_PERCENT_LEVELS_OBSERVED_NOT_BBO_SPREAD |
| INJUSDT @ BINANCE | 2026-07-17 | LIQUIDITY_OBSERVED_FIRST_PARTY | DERIVED_FROM_OBSERVED_DATA | {"snapshot_utc": "2026-07-17 00:00:03", "bid_notional_within_0_2pct": 93545.1156, "ask_notional_within_0_2pct": 77800.7659} | DEPTH_AT_PERCENT_LEVELS_OBSERVED_NOT_BBO_SPREAD |
| INJUSDT @ BINANCE | 2026-07-13 | LIQUIDITY_OBSERVED_FIRST_PARTY | DERIVED_FROM_OBSERVED_DATA | {"snapshot_utc": "2026-07-13 00:00:03", "bid_notional_within_0_2pct": 62790.9434, "ask_notional_within_0_2pct": 57105.9968} | DEPTH_AT_PERCENT_LEVELS_OBSERVED_NOT_BBO_SPREAD |
| VIRTUALUSDT @ BINANCE | 2026-07-13 | LIQUIDITY_OBSERVED_FIRST_PARTY | DERIVED_FROM_OBSERVED_DATA | {"snapshot_utc": "2026-07-13 00:00:03", "bid_notional_within_0_2pct": 48094.83075, "ask_notional_within_0_2pct": 63047.25709} | DEPTH_AT_PERCENT_LEVELS_OBSERVED_NOT_BBO_SPREAD |
| VIRTUALUSDT @ BINANCE | 2026-07-22 | LIQUIDITY_OBSERVED_FIRST_PARTY | DERIVED_FROM_OBSERVED_DATA | {"snapshot_utc": "2026-07-22 00:00:01", "bid_notional_within_0_2pct": 67543.42887, "ask_notional_within_0_2pct": 41227.66321} | DEPTH_AT_PERCENT_LEVELS_OBSERVED_NOT_BBO_SPREAD |
| LINKUSDT @ BINANCE | 2026-07-16 | LIQUIDITY_OBSERVED_FIRST_PARTY | DERIVED_FROM_OBSERVED_DATA | {"snapshot_utc": "2026-07-16 00:00:03", "bid_notional_within_0_2pct": 249581.17844, "ask_notional_within_0_2pct": 348029.8728} | DEPTH_AT_PERCENT_LEVELS_OBSERVED_NOT_BBO_SPREAD |
| LINKUSDT @ BINANCE | 2026-07-18 | LIQUIDITY_OBSERVED_FIRST_PARTY | DERIVED_FROM_OBSERVED_DATA | {"snapshot_utc": "2026-07-18 00:00:03", "bid_notional_within_0_2pct": 287645.85714, "ask_notional_within_0_2pct": 304183.2237} | DEPTH_AT_PERCENT_LEVELS_OBSERVED_NOT_BBO_SPREAD |
| LINKUSDT @ BINANCE | 2026-07-20 | LIQUIDITY_OBSERVED_FIRST_PARTY | DERIVED_FROM_OBSERVED_DATA | {"snapshot_utc": "2026-07-20 00:00:01", "bid_notional_within_0_2pct": 340688.89377, "ask_notional_within_0_2pct": 315601.67868} | DEPTH_AT_PERCENT_LEVELS_OBSERVED_NOT_BBO_SPREAD |
| tLEOUSD @ BITFINEX | 2026-07-16 | LIQUIDITY_OBSERVED_FIRST_PARTY | OBSERVED_FIRST_PARTY | {"trade_count": 6, "first_trade_utc": "2026-07-16T00:03:02.596000+00:00", "last_trade_utc": "2026-07-16T00:29:01.825000+00:00", "price_min": 9.811, "price_max": | UNRESOLVED_NO_FIRST_PARTY_HISTORICAL_BOOK |
| tLEOUSD @ BITFINEX | 2026-07-18 | LIQUIDITY_OBSERVED_FIRST_PARTY | OBSERVED_FIRST_PARTY | {"trade_count": 8, "first_trade_utc": "2026-07-18T00:01:02.849000+00:00", "last_trade_utc": "2026-07-18T00:29:51.425000+00:00", "price_min": 9.811, "price_max": | UNRESOLVED_NO_FIRST_PARTY_HISTORICAL_BOOK |
| tLEOUSD @ BITFINEX | 2026-07-20 | LIQUIDITY_OBSERVED_FIRST_PARTY | OBSERVED_FIRST_PARTY | {"trade_count": 5, "first_trade_utc": "2026-07-20T00:01:02.424000+00:00", "last_trade_utc": "2026-07-20T00:25:02.025000+00:00", "price_min": 9.7803, "price_max" | UNRESOLVED_NO_FIRST_PARTY_HISTORICAL_BOOK |

## Per-signal verdicts

| signal | S3 | fee | constraint | **S4** | missing |
|---|---|---|---|---|---|
| 2026-06-26|BINANCE:AAVEUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; no_executed_fill_in_lifecycle |
| 2026-07-05|BINANCE:CRVUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum |
| 2026-07-07|BINANCE:CRVUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; no_executed_fill_in_lifecycle |
| 2026-07-08|BINANCE:CRVUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; no_executed_fill_in_lifecycle |
| 2026-07-12|BINANCE:CRVUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; no_executed_fill_in_lifecycle |
| 2026-07-14|BINANCE:CRVUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; no_executed_fill_in_lifecycle |
| 2026-07-06|BINANCE:IMXUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum |
| 2026-07-11|BINANCE:INJUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum |
| 2026-07-12|BINANCE:INJUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; no_executed_fill_in_lifecycle |
| 2026-07-15|BINANCE:INJUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; no_executed_fill_in_lifecycle |
| 2026-07-15|BINANCE:LINKUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum |
| 2026-07-03|BINANCE:PENDLEUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum |
| 2026-07-04|BINANCE:PENDLEUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; no_executed_fill_in_lifecycle |
| 2026-07-05|BINANCE:PENDLEUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; no_executed_fill_in_lifecycle |
| 2026-07-07|BINANCE:PENDLEUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; no_executed_fill_in_lifecycle |
| 2026-07-08|BINANCE:PENDLEUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; no_executed_fill_in_lifecycle |
| 2026-06-20|BINANCE:QNTUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum |
| 2026-06-21|BINANCE:QNTUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; no_executed_fill_in_lifecycle |
| 2026-06-23|BINANCE:QNTUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; no_executed_fill_in_lifecycle |
| 2026-06-24|BINANCE:QNTUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; no_executed_fill_in_lifecycle |
| 2026-07-11|BINANCE:QNTUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; no_executed_fill_in_lifecycle |
| 2026-07-02|BINANCE:SOLUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum |
| 2026-07-06|BINANCE:SUNUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum |
| 2026-07-07|BINANCE:SUNUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; no_executed_fill_in_lifecycle |
| 2026-06-28|BINANCE:TIAUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum |
| 2026-06-29|BINANCE:TIAUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; no_executed_fill_in_lifecycle |
| 2026-07-01|BINANCE:TIAUSDT|HEDGE_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum |
| 2026-07-02|BINANCE:TIAUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; no_executed_fill_in_lifecycle |
| 2026-07-03|BINANCE:TIAUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; no_executed_fill_in_lifecycle |
| 2026-07-08|BINANCE:TIAUSDT|HEDGE_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum |
| 2026-07-06|BINANCE:TRXUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum |
| 2026-07-07|BINANCE:TRXUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; no_executed_fill_in_lifecycle |
| 2026-07-08|BINANCE:TRXUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; no_executed_fill_in_lifecycle |
| 2026-07-09|BINANCE:TRXUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; no_executed_fill_in_lifecycle |
| 2026-07-10|BINANCE:TRXUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; no_executed_fill_in_lifecycle |
| 2026-07-11|BINANCE:TRXUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; no_executed_fill_in_lifecycle |
| 2026-07-12|BINANCE:TRXUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; no_executed_fill_in_lifecycle |
| 2026-07-13|BINANCE:TRXUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; no_executed_fill_in_lifecycle |
| 2026-07-14|BINANCE:TRXUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; no_executed_fill_in_lifecycle |
| 2026-07-15|BINANCE:TRXUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; no_executed_fill_in_lifecycle |
| 2026-07-12|BINANCE:VIRTUALUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum |
| 2026-07-08|BINANCE:ZECUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum |
| 2026-07-09|BINANCE:ZECUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; no_executed_fill_in_lifecycle |
| 2026-07-10|BINANCE:ZECUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; no_executed_fill_in_lifecycle |
| 2026-07-15|BITFINEX:LEOUSD|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; spread_evidence_at_fill:['2026-07-16', '2026-07-18', '2026-07-16', '2026-07-20'] |
| 2026-07-05|BYBIT:GRAMUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; spread_evidence_at_fill:['2026-07-06', '2026-07-06'] |
| 2026-07-06|BYBIT:GRAMUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; no_executed_fill_in_lifecycle |
| 2026-07-07|BYBIT:GRAMUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; no_executed_fill_in_lifecycle |
| 2026-07-08|BYBIT:GRAMUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; no_executed_fill_in_lifecycle |
| 2026-07-09|BYBIT:TELUSDT|BEAR_SHORT | NOT_ELIGIBLE_STAGE_ONE_ELIMINATED | None | None | **NOT_ELIGIBLE_PRIOR_STAGE** |  |
| 2026-07-01|COINBASE:MORPHOUSD|BEAR_SHORT | NOT_ELIGIBLE_EXCLUDED_VENUE_POLICY | None | None | **NOT_ELIGIBLE_PRIOR_STAGE** |  |
| 2026-07-06|COINBASE:MORPHOUSD|HEDGE_SHORT | NOT_ELIGIBLE_EXCLUDED_VENUE_POLICY | None | None | **NOT_ELIGIBLE_PRIOR_STAGE** |  |
| 2026-06-21|GATE:ASTERUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; spread_evidence_at_fill:['2026-06-22', '2026-06-22'] |
| 2026-07-04|GATE:ASTERUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; no_executed_fill_in_lifecycle |
| 2026-07-05|GATE:ASTERUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; no_executed_fill_in_lifecycle |
| 2026-07-04|GATE:GTUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; spread_evidence_at_fill:['2026-07-05', '2026-07-20', '2026-07-06', '2026-07-23'] |
| 2026-07-05|GATE:GTUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; no_executed_fill_in_lifecycle |
| 2026-07-06|GATE:GTUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; no_executed_fill_in_lifecycle |
| 2026-07-07|GATE:GTUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; no_executed_fill_in_lifecycle |
| 2026-07-08|GATE:GTUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; no_executed_fill_in_lifecycle |
| 2026-07-09|GATE:GTUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; no_executed_fill_in_lifecycle |
| 2026-07-10|GATE:GTUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; no_executed_fill_in_lifecycle |
| 2026-07-11|GATE:GTUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; no_executed_fill_in_lifecycle |
| 2026-07-12|GATE:GTUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; no_executed_fill_in_lifecycle |
| 2026-07-13|GATE:GTUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; no_executed_fill_in_lifecycle |
| 2026-07-14|GATE:GTUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; no_executed_fill_in_lifecycle |
| 2026-07-15|GATE:GTUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; no_executed_fill_in_lifecycle |
| 2026-07-05|KRAKEN:KASUSD|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **FAIL_NO_MARKET_ACTIVITY_AT_FILL** | historical_fee; historical_tick_lot_minimum |
| 2026-07-06|KRAKEN:KASUSD|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; no_executed_fill_in_lifecycle |
| 2026-06-28|KRAKEN:SPXUSD|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; spread_evidence_at_fill:['2026-06-29', '2026-07-04', '2026-06-29', '2026-07-06'] |
| 2026-06-29|KRAKEN:SPXUSD|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; no_executed_fill_in_lifecycle |
| 2026-06-30|KRAKEN:SPXUSD|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; no_executed_fill_in_lifecycle |
| 2026-07-01|KRAKEN:SPXUSD|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; no_executed_fill_in_lifecycle |
| 2026-07-02|KRAKEN:SPXUSD|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; no_executed_fill_in_lifecycle |
| 2026-06-23|OKX:OKBUSDT|BEAR_SHORT | PASS_OHLC_COVERAGE | HISTORICAL_FEE_UNRESOLVED | HISTORICAL_CONSTRAINT_UNRESOLVED | **UNRESOLVED_HISTORICAL_FEE** | historical_fee; historical_tick_lot_minimum; spread_evidence_at_fill:['2026-06-24', '2026-06-24'] |

## Evidence classes

- observed_first_party: depth snapshots (Binance archived bookDepth); public trades (Bybit archive, OKX, Gate, Kraken Futures, Bitfinex); current instrument filters; current fee values where public
- derived_from_observed_data: trade-window summaries (count, VWAP, notional, price range)
- frozen_conservative_assumption: none
- sensitivity_only: 37 bps round-trip (pre-existing, not used here)
- unresolved: historical fee schedules with effective dates (all venues); historical tick/lot/minimum effective dates (all venues); best-bid/ask spread at fill timestamps (all venues); order-book depth at fill (non-Binance venues)

## Funnel

| item | value |
|---|---|
| excluded_venue_policy | 2 |
| fee_honestly_replayable_trades | 0 |
| frozen_long_signals_no_execution_evidence_yet | 13 |
| frozen_short_signals | 75 |
| frozen_v2_signals | 88 |
| stage1_eliminated_preserved | 1 |
| stage1_survivors | 74 |
| stage2_decisive_executable | 72 |
| stage3_fail_gap | 0 |
| stage3_ohlc_coverage_pass | 72 |
| stage3_unresolved | 0 |
| steps_remaining_before_admission | ['7_full_holding_period_coverage', 'admission_review', 'cost_base_case_governance'] |
| stage4_pass | 0 |
| stage4_unresolved | 71 |
| stage4_fail | 1 |

## Blockers before admission

- historical fee schedules with effective dates are not exposed by any venue's public API (T2 archived fee records required, or a frozen conservative fee ASSUMPTION adopted through governance and labelled as such)
- historical tick/lot/minimum effective dates are not exposed (Gate's config_change_time proves changes AFTER the window for GT_USDT/ASTER_USDT); a governance decision is needed on CURRENT_CONSTRAINT_ONLY values
- best-bid/ask spread at the fill timestamps is unavailable first-party for every venue; Binance archived bookDepth provides a depth proxy only
- step 7 full-holding-period sign-off, admission review token, cost base case freeze, weekend-rule ruling, basis review, long-signal execution evidence

## Raw sources

| raw file | sha256 |
|---|---|
| data/c22_short_instrument_evidence/raw/BINANCE/CRV/BINANCE__CRV__stage4_bookdepth_2026-07-06__20260911T131902Z__2026-09-11T131937Z.raw.json | `00558bd49c8f8b14d2a4bc59e393d6b1d2802c429a870b976906348b1935f1a3` |
| data/c22_short_instrument_evidence/raw/BINANCE/CRV/BINANCE__CRV__stage4_bookdepth_2026-07-16__20260911T131902Z__2026-09-11T131938Z.raw.json | `bda75bc5d3ccb4050238fa8bf90bb07489a09b85df24e77188192e03be173dc5` |
| data/c22_short_instrument_evidence/raw/BINANCE/IMX/BINANCE__IMX__stage4_bookdepth_2026-07-07__20260911T131902Z__2026-09-11T131942Z.raw.json | `b4ebc94823796b3f63be412e078c81482874b713f7e67f9ecd5c82aea8dea7c0` |
| data/c22_short_instrument_evidence/raw/BINANCE/IMX/BINANCE__IMX__stage4_bookdepth_2026-07-30__20260911T131902Z__2026-09-11T131943Z.raw.json | `02533a1dff94876ca06ab66e647365d088e7c051ea724da98d33bfb7c03868a8` |
| data/c22_short_instrument_evidence/raw/BINANCE/INJ/BINANCE__INJ__stage4_bookdepth_2026-07-12__20260911T131902Z__2026-09-11T131957Z.raw.json | `f1f86139dfa54ab8020f25f727e43997a9dde8b6d57a84dbaf74aeb8f6a6ad47` |
| data/c22_short_instrument_evidence/raw/BINANCE/INJ/BINANCE__INJ__stage4_bookdepth_2026-07-13__20260911T131902Z__2026-09-11T132000Z.raw.json | `67d44ad2591d5ec2e0b5bf21f8f84f3953aa87066e25354b23fce5ac51981076` |
| data/c22_short_instrument_evidence/raw/BINANCE/INJ/BINANCE__INJ__stage4_bookdepth_2026-07-17__20260911T131902Z__2026-09-11T131958Z.raw.json | `33ed11d1f876f75b69f9232e386a21cea04d6f436b890825f183c20d10445841` |
| data/c22_short_instrument_evidence/raw/BINANCE/LINK/BINANCE__LINK__stage4_bookdepth_2026-07-16__20260911T131902Z__2026-09-11T132004Z.raw.json | `a094831af3fe77ad1e6e8efc27565814496fdcdd2bce733132cd985b62e42fd1` |
| data/c22_short_instrument_evidence/raw/BINANCE/LINK/BINANCE__LINK__stage4_bookdepth_2026-07-18__20260911T131902Z__2026-09-11T132004Z.raw.json | `810cbdd3492be4da88841e72047780028876c010aeef68efa67d626a22fa62ab` |
| data/c22_short_instrument_evidence/raw/BINANCE/LINK/BINANCE__LINK__stage4_bookdepth_2026-07-20__20260911T131902Z__2026-09-11T132006Z.raw.json | `71c277e4508c961f4e50e016b7e03a6788803df6d8da2ae4cd8e5db43b9a9fb0` |
| data/c22_short_instrument_evidence/raw/BINANCE/PENDLE/BINANCE__PENDLE__stage4_bookdepth_2026-07-04__20260911T131902Z__2026-09-11T131929Z.raw.json | `c53f9bd5461f7af1453e54905d061a7e51d19abe57d7e916e91b9f923471d024` |
| data/c22_short_instrument_evidence/raw/BINANCE/PENDLE/BINANCE__PENDLE__stage4_bookdepth_2026-07-06__20260911T131902Z__2026-09-11T131931Z.raw.json | `f209bba7dbda5d64a33b295e804b40acd5416b6cf2c211078deb009d69e905b9` |
| data/c22_short_instrument_evidence/raw/BINANCE/PENDLE/BINANCE__PENDLE__stage4_bookdepth_2026-07-10__20260911T131902Z__2026-09-11T131930Z.raw.json | `9df6faefded774383fc2f87fd9bc04dd7df0c0d02deef89fc6b9b8daecffa78d` |
| data/c22_short_instrument_evidence/raw/BINANCE/QNT/BINANCE__QNT__stage4_bookdepth_2026-06-21__20260911T131902Z__2026-09-11T131910Z.raw.json | `52698a9d816cf853f3ba7adaf430cd2d2509fd35c7d7038637b64eda984b55ab` |
| data/c22_short_instrument_evidence/raw/BINANCE/QNT/BINANCE__QNT__stage4_bookdepth_2026-06-22__20260911T131902Z__2026-09-11T131911Z.raw.json | `c4b9374a81d613195340deeaac339662214188416abc1c36cd1c2b5355c1679e` |
| data/c22_short_instrument_evidence/raw/BINANCE/SOL/BINANCE__SOL__stage4_bookdepth_2026-07-03__20260911T131902Z__2026-09-11T131925Z.raw.json | `dcbcf376f0dadb93b902d5c5c3159e9d89fd5fc889c22bd62260e5da59e5f5cf` |
| data/c22_short_instrument_evidence/raw/BINANCE/SOL/BINANCE__SOL__stage4_bookdepth_2026-07-05__20260911T131902Z__2026-09-11T131927Z.raw.json | `0ae391ccd8e4d2abaaa303075714bbcd2d74fcc0e9f61f68c9e00110351a7260` |
| data/c22_short_instrument_evidence/raw/BINANCE/SOL/BINANCE__SOL__stage4_bookdepth_2026-07-07__20260911T131902Z__2026-09-11T131928Z.raw.json | `e639c175bc605ce44f2f71a859d07ac1a17f6e2389119a8701b91fbeb1463e64` |
| data/c22_short_instrument_evidence/raw/BINANCE/SUN/BINANCE__SUN__stage4_bookdepth_2026-07-07__20260911T131902Z__2026-09-11T131944Z.raw.json | `5cc6b95652a28f7152a20e4b572d65700a533cabbb4ebd0c9dfa25b8fe771da4` |
| data/c22_short_instrument_evidence/raw/BINANCE/SUN/BINANCE__SUN__stage4_bookdepth_2026-07-09__20260911T131902Z__2026-09-11T131945Z.raw.json | `bf44cde25f8724bc1b99f8f186d66d47176bac15dbf5aadae9b61c3de60ff9f9` |
| data/c22_short_instrument_evidence/raw/BINANCE/TIA/BINANCE__TIA__stage4_bookdepth_2026-06-29__20260911T131902Z__2026-09-11T131917Z.raw.json | `60cdcec017a776b8d62a7df799ad84aa70dc2dfd2b03cba5e3cd27e1da9ba7b1` |
| data/c22_short_instrument_evidence/raw/BINANCE/TIA/BINANCE__TIA__stage4_bookdepth_2026-07-01__20260911T131902Z__2026-09-11T131918Z.raw.json | `e2db387f3c7ef6572783fd802957bcdb6470389478b5107e6774a4aeba412a81` |
| data/c22_short_instrument_evidence/raw/BINANCE/TIA/BINANCE__TIA__stage4_bookdepth_2026-07-02__20260911T131902Z__2026-09-11T131921Z.raw.json | `784e09a22f57f573d8ac2eeb6a5e5887e0ceb9996087eb399ddc4f094e4f697a` |
| data/c22_short_instrument_evidence/raw/BINANCE/TIA/BINANCE__TIA__stage4_bookdepth_2026-07-05__20260911T131902Z__2026-09-11T131922Z.raw.json | `cc3e1edf55917aabdb2b1210047867c5694f2c57636a4ac7ee69c41dc386e8fc` |
| data/c22_short_instrument_evidence/raw/BINANCE/TIA/BINANCE__TIA__stage4_bookdepth_2026-07-07__20260911T131902Z__2026-09-11T131924Z.raw.json | `ca37f79508197c0a28a052106d415ea2156ce0d1f1defbec9fba0d31d88981c2` |
| data/c22_short_instrument_evidence/raw/BINANCE/TIA/BINANCE__TIA__stage4_bookdepth_2026-07-09__20260911T131902Z__2026-09-11T131950Z.raw.json | `59f1f84edf871ce79a82bb5bdc9013bc6c5beb8da169a214909f37817f007931` |
| data/c22_short_instrument_evidence/raw/BINANCE/TIA/BINANCE__TIA__stage4_bookdepth_2026-07-11__20260911T131902Z__2026-09-11T131951Z.raw.json | `6897f5106e71b74f40fe5ace38359ed8129b9261ea954fa4cc98b012e75d3f9b` |
| data/c22_short_instrument_evidence/raw/BINANCE/TIA/BINANCE__TIA__stage4_bookdepth_2026-07-13__20260911T131902Z__2026-09-11T131952Z.raw.json | `959ba5a98d16f0006cceb627c32e11db343ba0dcd901f9503aa6a1a013d53cc0` |
| data/c22_short_instrument_evidence/raw/BINANCE/TRX/BINANCE__TRX__stage4_bookdepth_2026-07-07__20260911T131902Z__2026-09-11T131947Z.raw.json | `35f0236e69ff7e1563508db7e62c7805d6add0a760eae8cf70f7ee485eec4a68` |
| data/c22_short_instrument_evidence/raw/BINANCE/TRX/BINANCE__TRX__stage4_bookdepth_2026-07-26__20260911T131902Z__2026-09-11T131948Z.raw.json | `a555a6d33d00eb565acdda0f8120ce883e962c0f4fed3084ac92c45eb68702dd` |
| data/c22_short_instrument_evidence/raw/BINANCE/TRX/BINANCE__TRX__stage4_bookdepth_2026-07-28__20260911T131902Z__2026-09-11T131949Z.raw.json | `15e6697eda9d6b2855b491924e7d0e05eca817479047e992a107a300756377e1` |
| data/c22_short_instrument_evidence/raw/BINANCE/VIRTUAL/BINANCE__VIRTUAL__stage4_bookdepth_2026-07-13__20260911T131902Z__2026-09-11T132001Z.raw.json | `bd63563cb2953cbff7b97a5ba25048663d1b46599299a5f236b0871299126b9a` |
| data/c22_short_instrument_evidence/raw/BINANCE/VIRTUAL/BINANCE__VIRTUAL__stage4_bookdepth_2026-07-22__20260911T131902Z__2026-09-11T132002Z.raw.json | `7f5701705451092b1f26b5a966c0d668d6c23b6a58d586ed4a749f696a4fdfb9` |
| data/c22_short_instrument_evidence/raw/BINANCE/ZEC/BINANCE__ZEC__stage4_bookdepth_2026-07-09__20260911T131902Z__2026-09-11T131954Z.raw.json | `29321430c1a9631a93c17fae96ee72907c2a65cd54af6c6098791547ce769824` |
| data/c22_short_instrument_evidence/raw/BINANCE/ZEC/BINANCE__ZEC__stage4_bookdepth_2026-07-12__20260911T131902Z__2026-09-11T131955Z.raw.json | `a9f479ab2e4b5017e20d935a2696c062fbedcaab259767aef84290fe41ed3b8d` |
| data/c22_short_instrument_evidence/raw/BINANCE/ZEC/BINANCE__ZEC__stage4_bookdepth_2026-07-14__20260911T131902Z__2026-09-11T131956Z.raw.json | `c9ccd28b41e59149407382953018679d3d9a2acf6df1c839f269bf8dda3f9c2d` |
| data/c22_short_instrument_evidence/raw/BINANCE/_shared/BINANCE___shared__stage4_usdm_exchangeinfo__20260911T131902Z__2026-09-11T131902Z.raw.json | `b46d606170205aec8576a325418c393d88f2bb1adefa9426739628ec7fa0c0a0` |
| data/c22_short_instrument_evidence/raw/BITFINEX/LEO/BITFINEX__LEO__stage4_public_trades_2026-07-16__20260911T131902Z__2026-09-11T132007Z.raw.json | `bd1a0c12cb2f2241f02322e64a12fa5e26d56a485db8a2dec542aeb921f06ae0` |
| data/c22_short_instrument_evidence/raw/BITFINEX/LEO/BITFINEX__LEO__stage4_public_trades_2026-07-18__20260911T131902Z__2026-09-11T132008Z.raw.json | `a5dc5b48bf8c25f71b7aab0c50da7759d8f01d9374794e5a409bcce103c67a7b` |
| data/c22_short_instrument_evidence/raw/BITFINEX/LEO/BITFINEX__LEO__stage4_public_trades_2026-07-20__20260911T131902Z__2026-09-11T132008Z.raw.json | `d83e436ee44c071220c8d618e09107481e557fce0a2b9d72d42cbe402d84084e` |
| data/c22_short_instrument_evidence/raw/BITFINEX/_shared/BITFINEX___shared__stage4_conf_pub_info_pair__20260911T131902Z__2026-09-11T131905Z.raw.json | `1455ca8151f8c57f990cdf15a5a9ec131ae062912795b0873b7f894bd12430d5` |
| data/c22_short_instrument_evidence/raw/BYBIT/GRAM/BYBIT__GRAM__stage4_linear_instruments_info__20260911T131902Z__2026-09-11T131906Z.raw.json | `2720a598435f4768bec185d972943b4bbafda22c893971a840c07979e423cf66` |
| data/c22_short_instrument_evidence/raw/BYBIT/GRAM/BYBIT__GRAM__stage4_public_trades_2026-07-06__20260911T131902Z__2026-09-11T131939Z.raw.json | `65c2733b3d3d5e8d58819dada205a74b01c105ff4de60c73313a0b13a93fe8f4` |
| data/c22_short_instrument_evidence/raw/GATE/ASTER/GATE__ASTER__stage4_futures_trades_2026-06-22__20260911T131902Z__2026-09-11T131912Z.raw.json | `c77fdd6a6d617784f126c57312948f50fc535f10c2d9e8369fd084fa8336ba72` |
| data/c22_short_instrument_evidence/raw/GATE/ASTER/GATE__ASTER__stage4_futures_usdt_contract__20260911T131902Z__2026-09-11T131906Z.raw.json | `b1ceda564b14f3529d2d704615d1163f8adcfb9ef5dbdaf537f38fa87134e147` |
| data/c22_short_instrument_evidence/raw/GATE/GT/GATE__GT__stage4_futures_trades_2026-07-05__20260911T131902Z__2026-09-11T131933Z.raw.json | `20828a82a3062e021ef23e3e6d2f094adee4dd06ab63ceea4f0d05e4a21acfa8` |
| data/c22_short_instrument_evidence/raw/GATE/GT/GATE__GT__stage4_futures_trades_2026-07-06__20260911T131902Z__2026-09-11T131935Z.raw.json | `f397521b0a61d9c3d5cb256705f97fcb70a4d4e72a40a6c6f595f0c4a98ef88c` |
| data/c22_short_instrument_evidence/raw/GATE/GT/GATE__GT__stage4_futures_trades_2026-07-20__20260911T131902Z__2026-09-11T131934Z.raw.json | `7148c7220c1267eb46a9824d046fac794eea9e5b6184ce93854db3dbc001ee36` |
| data/c22_short_instrument_evidence/raw/GATE/GT/GATE__GT__stage4_futures_trades_2026-07-23__20260911T131902Z__2026-09-11T131936Z.raw.json | `048cf4fe2501cbc7caec62ce475ea67848178f35029d89a66738c04096ceeed9` |
| data/c22_short_instrument_evidence/raw/GATE/GT/GATE__GT__stage4_futures_usdt_contract__20260911T131902Z__2026-09-11T131907Z.raw.json | `3644831c37c6e828427eb2849c8a8d1e4961f316c1082514b7d8e8cb99eec5cd` |
| data/c22_short_instrument_evidence/raw/KRAKEN/KAS/KRAKEN__KAS__stage4_executions_2026-07-06_p00__20260911T131902Z__2026-09-11T131941Z.raw.json | `c94188f9c9003d1e1b499232bb157f55a5705cf1f84fdca1f354d41e8739c1cc` |
| data/c22_short_instrument_evidence/raw/KRAKEN/SPX/KRAKEN__SPX__stage4_executions_2026-06-29_p00__20260911T131902Z__2026-09-11T131919Z.raw.json | `83fa53c31c860bcef50c0103369b78e02d517aae812790f663385aad02980c98` |
| data/c22_short_instrument_evidence/raw/KRAKEN/SPX/KRAKEN__SPX__stage4_executions_2026-07-04_p00__20260911T131902Z__2026-09-11T131920Z.raw.json | `72eb1d8894cef32613573177545d71ecc252ad55fafd1dbc26d1a8ec97ea80b9` |
| data/c22_short_instrument_evidence/raw/KRAKEN/SPX/KRAKEN__SPX__stage4_executions_2026-07-06_p00__20260911T131902Z__2026-09-11T131921Z.raw.json | `371592af51e9bffd9daeabcee3159253153800bfa529a5e8111ec0c69cd49daa` |
| data/c22_short_instrument_evidence/raw/KRAKEN/_shared/KRAKEN___shared__stage4_feeschedules_current__20260911T131902Z__2026-09-11T131909Z.raw.json | `2f3a186dcf39053ac8733d5ac9ca8bf3967735679fab2e88c312d6299bcfea03` |
| data/c22_short_instrument_evidence/raw/KRAKEN/_shared/KRAKEN___shared__stage4_futures_instruments__20260911T131902Z__2026-09-11T131908Z.raw.json | `7a79def3a49e945c0126b6349e9569c6dbe762999fb37108571ba4d4f0c490a6` |
| data/c22_short_instrument_evidence/raw/OKX/OKB/OKX__OKB__stage4_history_trades_2026-06-24_p00__20260911T131902Z__2026-09-11T131914Z.raw.json | `306d18fb0342633afdc1f6be16749379bcfd3b06e06a9648b1a318b3bb5ceb59` |
| data/c22_short_instrument_evidence/raw/OKX/OKB/OKX__OKB__stage4_history_trades_2026-06-24_p01__20260911T131902Z__2026-09-11T131914Z.raw.json | `e4ac8eef4eb8697a0b5393ec21d2876bf41285fc62d95b53dee7abd3a3683f99` |
| data/c22_short_instrument_evidence/raw/OKX/OKB/OKX__OKB__stage4_history_trades_2026-06-24_p02__20260911T131902Z__2026-09-11T131914Z.raw.json | `18070ee990e09735ee423c68acb9b2a1cb5ea7bc32ac7843ec9336bc0735c095` |
| data/c22_short_instrument_evidence/raw/OKX/OKB/OKX__OKB__stage4_history_trades_2026-06-24_p03__20260911T131902Z__2026-09-11T131915Z.raw.json | `b09c584c2031a5f4ca7679b56b95d616f9e005d192b6b217996c825006041f80` |
| data/c22_short_instrument_evidence/raw/OKX/OKB/OKX__OKB__stage4_history_trades_2026-06-24_p04__20260911T131902Z__2026-09-11T131916Z.raw.json | `3fec98c7e5163edd99a72fd3593ed2e7c6aa1a04a08b3c6799a77e3830a6110c` |
| data/c22_short_instrument_evidence/raw/OKX/OKB/OKX__OKB__stage4_history_trades_2026-06-24_p05__20260911T131902Z__2026-09-11T131916Z.raw.json | `c2e758bfdfe4240038613cfab136735b7a67351bd4b83972299186488b7239d7` |
| data/c22_short_instrument_evidence/raw/OKX/OKB/OKX__OKB__stage4_public_instruments_swap__20260911T131902Z__2026-09-11T131909Z.raw.json | `9f6e49cf2b58d07cfa75b20e0ad15177f919c7f2c781f140bc81ee7d040a240d` |
