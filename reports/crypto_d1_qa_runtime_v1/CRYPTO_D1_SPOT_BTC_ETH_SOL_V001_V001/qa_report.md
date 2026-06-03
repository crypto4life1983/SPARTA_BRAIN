# SPARTA Crypto-D1 Data QA Runtime Tool v1 -- QA report

> **Research-only. Local-only.** No data fetched. No exchange contacted. No order placed. QA_PASS does NOT authorize paper or live trading.

- **qa_report_id:** `741f5efe87054dd7`
- **generated_at:** 2026-06-03T16:56:15Z
- **tool_version:** crypto_d1_data_qa_runtime_tool_v1
- **qa_freeze_spec_version:** crypto_d1_qa_freeze_spec_v1
- **dataset_id:** `CRYPTO_D1_SPOT_BTC_ETH_SOL_V001`
- **dataset_version:** `V001`
- **data_contract_version:** crypto_d1_data_contract_v1
- **protocol_version:** crypto_d1_protocol_v1
- **dataset_dir:** `data/crypto_d1_research/CRYPTO_D1_SPOT_BTC_ETH_SOL_V001/V001`

## QA verdict
- **qa_status:** **QA_FAIL**
- **checks_run:** 37 (passed 35 / warned 1 / failed 1)
- **allowed_next_step:** Remediation requires a NEW dataset_version. Do not reference this dataset.

## Safety flags (pinned)
- research_only: True
- data_fetch_enabled: False
- exchange_connection_enabled: False
- live_trading_enabled: False
- broker_control_enabled: False
- paper_order_execution_enabled: False
- order_placement_enabled: False

## Blocking failures
- [G_freeze] freeze_record_has_timestamp: FREEZE_RECORD.txt missing 'freeze_timestamp_utc' key

## Warnings
- [B_timestamp] missing_days_reconciled: missing days observed: [{'symbol': 'BTC', 'missing_days': 1}]; manifest's missing_day_policy text present

## Row counts
- total: 4976
  - BTC: 1658
  - ETH: 1659
  - SOL: 1659

## Forbidden next steps
- Trade live or paper based on a QA_PASS verdict.
- Connect SPARTA's runtime to any exchange or vendor over the network.
- Promote crypto_d1_protocol to ACTIVE / STRONG without a separate operator decision.
- Schedule a daemon / cron / background process that touches this tool.
- Modify paper / live execution files.
- Install or read any API key, OAuth token, or .env credential.
- Use any synthetic / mock-priced data as evidence.

## Safety notes
- Research-only. Local-only.
- No data was fetched. No exchange was contacted. No order was placed.
- QA_PASS is the deterministic outcome of mechanical checks; it does NOT imply profitability and does NOT authorize a backtest plan by itself.
- Per Bundle 14, a QA_PASS qa_report is a PRECONDITION for a future backtest plan -- never the authorization itself.
- A QA report cannot authorize paper or live trading.
