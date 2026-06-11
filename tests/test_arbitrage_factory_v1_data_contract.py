"""Tests for the SPARTA Arbitrage Factory V1 Data Contract (READ-ONLY).

(Named test_arbitrage_factory_v1_data_contract.py because the older
tests/test_arbitrage_data_contract.py belongs to the pre-existing
tools/arbitrage_data_contract_check.py system and must not be overwritten.)

Everything here is pure and in-memory; no network, no credentials, no API call, no
exchange connection, no file read/write, no scanner, no scheduler, no gate is
unlocked. The contract defines operator-staged dataset shapes and refuses any
account/credential/order/position field outright."""

from __future__ import annotations

import ast

import sparta_commander.arbitrage_data_contract as dc
import sparta_commander.arbitrage_scanner_spec_contract as sp


# --------------------------------------------------------------------------- #
# ready scanner spec -> READY data contract
# --------------------------------------------------------------------------- #
def test_data_contract_ready_on_real_chain():
    c = dc.build_arbitrage_data_contract()
    assert c["verdict"] == dc.VERDICT_DATA_CONTRACT_READY
    assert c["blockers"] == []
    assert c["scanner_spec_verdict"] == sp.VERDICT_SPEC_READY
    assert c["lane"] == "arbitrage_factory_v1"
    assert c["roadmap_seq"] == 2
    assert c["next_required_action"] == "HUMAN_APPROVED_FEE_SLIPPAGE_MODEL"


def test_dataset_specs_cover_all_six_families():
    c = dc.build_arbitrage_data_contract()
    fams: set[str] = set()
    for spec in c["staged_dataset_specs"].values():
        fams.update(spec["maps_to_families"])
    assert fams == {
        "ARB_F1_spot_perp_funding_basis",
        "ARB_F2_cross_exchange_basis_monitoring",
        "ARB_F3_btc_eth_sol_pair_spread_alerts",
        "ARB_F4_fee_adjusted_net_edge_scanner",
        "ARB_F5_liquidity_spread_slippage_filters",
    }
    # F6 is the report framework: fed by all datasets via the family mapping
    assert any(m["feeds"] == "ARB_F6" for m in c["family_mapping"])


def test_all_specs_stage_under_the_staging_root():
    c = dc.build_arbitrage_data_contract()
    for kind, spec in c["staged_dataset_specs"].items():
        assert spec["file_pattern"].startswith(dc.STAGING_ROOT), kind
    assert c["staging_is_manual_operator_only"] is True


def test_labels_are_labels_not_connections():
    c = dc.build_arbitrage_data_contract()
    assert tuple(c["allowed_symbols"]) == ("BTC", "ETH", "SOL")
    assert tuple(c["allowed_venue_labels"]) == (
        "binance", "bybit", "okx", "coinbase", "kraken")
    assert c["venue_labels_are_not_connections"] is True
    assert c["connects_exchange"] is False
    assert c["uses_network"] is False


def test_no_spec_contains_an_execution_or_account_field():
    for kind, spec in dc.STAGED_DATASET_SPECS.items():
        joined = " ".join(spec["required_columns"]).lower()
        for token in dc.FORBIDDEN_FIELD_TOKENS:
            assert token not in joined, (kind, token)


def test_validation_rules_cover_the_core_safety_set():
    joined = " ".join(dc.VALIDATION_RULES)
    assert "required_column" in joined
    assert "utc_iso8601" in joined
    assert "no_duplicate" in joined
    assert "non_negative" in joined
    assert "allowed_label_lists" in joined
    assert "stale_data" in joined and "never_silently_used" in joined
    assert "forbidden_field" in joined and "rejected_whole" in joined
    assert "missing_or_empty_files_block_readiness" in joined


def test_build_is_deterministic():
    assert dc.build_arbitrage_data_contract() == dc.build_arbitrage_data_contract()


# --------------------------------------------------------------------------- #
# descriptor validation: valid schemas accepted
# --------------------------------------------------------------------------- #
def test_valid_funding_descriptor_accepted():
    v = dc.validate_staged_dataset_descriptor(
        "funding_rates",
        ["timestamp_utc", "symbol", "venue", "funding_rate_8h", "mark_price"])
    assert v["acceptable"] is True
    assert v["errors"] == []


def test_valid_descriptor_with_extra_market_column_accepted():
    v = dc.validate_staged_dataset_descriptor(
        "liquidity_depth",
        ["timestamp_utc", "symbol", "venue", "bid_depth_usd_10bps",
         "ask_depth_usd_10bps", "spread_bps", "quote_volume_24h"])
    assert v["acceptable"] is True


def test_every_spec_kind_accepts_its_own_required_columns():
    for kind, spec in dc.STAGED_DATASET_SPECS.items():
        v = dc.validate_staged_dataset_descriptor(
            kind, list(spec["required_columns"]))
        assert v["acceptable"] is True, kind


# --------------------------------------------------------------------------- #
# descriptor validation: unsafe fields refused whole
# --------------------------------------------------------------------------- #
def test_credential_fields_refuse_descriptor():
    for bad_col in ("api_key", "exchange_secret", "session_token", "passphrase"):
        v = dc.validate_staged_dataset_descriptor(
            "funding_rates",
            ["timestamp_utc", "symbol", "venue", "funding_rate_8h",
             "mark_price", bad_col])
        assert v["acceptable"] is False, bad_col
        assert any("forbidden_field" in e for e in v["errors"])


def test_account_and_wallet_fields_refuse_descriptor():
    for bad_col in ("account_id", "wallet_address", "usdt_balance", "equity"):
        v = dc.validate_staged_dataset_descriptor(
            "fee_schedule",
            ["venue", "symbol", "taker_fee_pct", "maker_fee_pct",
             "withdrawal_flat_fee", bad_col])
        assert v["acceptable"] is False, bad_col


def test_order_fill_and_position_fields_refuse_descriptor():
    for bad_col in ("order_id", "fill_price", "open_position", "position_size",
                    "leverage", "margin_used", "realized_pnl", "execution_venue"):
        v = dc.validate_staged_dataset_descriptor(
            "cross_exchange_quotes",
            ["timestamp_utc", "symbol", "venue", "bid", "ask", "mid", bad_col])
        assert v["acceptable"] is False, bad_col


def test_forbidden_field_refuses_even_a_complete_valid_schema():
    # the rest of the schema is perfect -- one poisoned column kills the file
    v = dc.validate_staged_dataset_descriptor(
        "spot_perp_basis",
        ["timestamp_utc", "symbol", "venue", "spot_price", "perp_price",
         "basis_pct", "account_balance"])
    assert v["acceptable"] is False
    # the refusal happens FIRST; no missing-column noise alongside it
    assert all("forbidden_field" in e for e in v["errors"])


def test_unknown_kind_and_missing_columns_refused():
    v = dc.validate_staged_dataset_descriptor("live_positions", ["timestamp_utc"])
    assert v["acceptable"] is False
    assert any("unknown_dataset_kind" in e for e in v["errors"])
    v2 = dc.validate_staged_dataset_descriptor(
        "funding_rates", ["timestamp_utc", "symbol"])
    assert v2["acceptable"] is False
    assert any("missing_required_column" in e for e in v2["errors"])
    v3 = dc.validate_staged_dataset_descriptor("funding_rates", [])
    assert v3["acceptable"] is False
    v4 = dc.validate_staged_dataset_descriptor(
        "funding_rates",
        ["timestamp_utc", "symbol", "venue", "funding_rate_8h", "mark_price",
         "mark_price"])
    assert v4["acceptable"] is False
    assert "duplicate_column_names" in v4["errors"]


# --------------------------------------------------------------------------- #
# gating on the scanner spec
# --------------------------------------------------------------------------- #
def test_missing_scanner_spec_blocks():
    c = dc.record_arbitrage_data_contract(None)
    assert c["verdict"] == dc.VERDICT_DATA_CONTRACT_BLOCKED
    assert "scanner_spec_missing" in c["blockers"]


def test_invalid_scanner_spec_blocks():
    spec = sp.build_arbitrage_scanner_spec()
    spec["runs_scanner"] = True  # breaks the scanner spec validator
    c = dc.record_arbitrage_data_contract(spec)
    assert c["verdict"] == dc.VERDICT_DATA_CONTRACT_BLOCKED
    assert "scanner_spec_invalid" in c["blockers"]


def test_blocked_scanner_spec_blocks():
    blocked_spec = sp.record_arbitrage_scanner_spec(None)
    c = dc.record_arbitrage_data_contract(blocked_spec)
    assert c["verdict"] == dc.VERDICT_DATA_CONTRACT_BLOCKED
    assert "scanner_spec_not_ready" in c["blockers"]


# --------------------------------------------------------------------------- #
# posture: nothing read, nothing connected, gates untouched
# --------------------------------------------------------------------------- #
def test_contract_is_inert_on_all_paths():
    contracts = [
        dc.build_arbitrage_data_contract(),
        dc.record_arbitrage_data_contract(None),
    ]
    for c in contracts:
        assert c["contract_reads_no_files"] is True
        assert c["output_is_readiness_only_never_a_scan_result"] is True
        assert c["data_describes_markets_never_accounts"] is True
        assert c["no_execution_fields_exist_in_any_spec"] is True
        assert c["human_review_required"] is True
        for key in (
            "executes", "writes_files", "runs_scanner", "runs_simulation",
            "runs_backtest", "runs_optimization", "starts_scheduler",
            "starts_daemon", "starts_background_worker", "runs_loop",
            "fetches_data", "calls_api", "connects_broker", "connects_exchange",
            "uses_real_money", "uses_network", "uses_credentials",
            "contains_order_logic", "authorizes_paper_execution",
            "authorizes_micro_live", "authorizes_live_trading", "promotes_gate",
            "unlocks_downstream_gate",
        ):
            assert c[key] is False, key
        assert c["paper_trading_gate_locked"] is True
        assert c["micro_live_gate_locked"] is True
        assert c["live_gate_locked"] is True


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #
def test_validate_passes_on_ready_and_blocked():
    assert dc.validate_arbitrage_data_contract(
        dc.build_arbitrage_data_contract())["valid"] is True
    assert dc.validate_arbitrage_data_contract(
        dc.record_arbitrage_data_contract(None))["valid"] is True


def test_validate_rejects_smuggled_account_column():
    c = dc.build_arbitrage_data_contract()
    c["staged_dataset_specs"]["funding_rates"]["required_columns"] = (
        "timestamp_utc", "symbol", "venue", "funding_rate_8h", "wallet_balance")
    v = dc.validate_arbitrage_data_contract(c)
    assert v["valid"] is False
    assert "forbidden_field_in_spec:funding_rates" in v["errors"]


def test_validate_rejects_spec_outside_staging_root():
    c = dc.build_arbitrage_data_contract()
    c["staged_dataset_specs"]["fee_schedule"]["file_pattern"] = "C:/anywhere/fees.csv"
    v = dc.validate_arbitrage_data_contract(c)
    assert v["valid"] is False
    assert "spec_outside_staging_root:fee_schedule" in v["errors"]


def test_validate_rejects_added_or_removed_dataset_kind():
    c = dc.build_arbitrage_data_contract()
    c["staged_dataset_specs"]["live_positions"] = {
        "file_pattern": dc.STAGING_ROOT + "positions.csv",
        "required_columns": ("timestamp_utc",), "maps_to_families": ()}
    v = dc.validate_arbitrage_data_contract(c)
    assert v["valid"] is False
    assert "dataset_specs_tampered" in v["errors"]


def test_validate_rejects_weakened_forbidden_tokens_or_labels():
    c = dc.build_arbitrage_data_contract()
    c["forbidden_field_tokens"] = [
        t for t in c["forbidden_field_tokens"] if t != "position"]
    v = dc.validate_arbitrage_data_contract(c)
    assert v["valid"] is False
    assert "forbidden_tokens_weakened" in v["errors"]
    c2 = dc.build_arbitrage_data_contract()
    c2["allowed_venue_labels"].append("my_private_exchange")
    v2 = dc.validate_arbitrage_data_contract(c2)
    assert v2["valid"] is False
    assert "venues_tampered" in v2["errors"]


def test_validate_rejects_connection_or_scan_claims():
    c = dc.build_arbitrage_data_contract()
    c["venue_labels_are_not_connections"] = False
    v = dc.validate_arbitrage_data_contract(c)
    assert v["valid"] is False
    assert "venues_treated_as_connections" in v["errors"]
    c2 = dc.build_arbitrage_data_contract()
    c2["output_is_readiness_only_never_a_scan_result"] = False
    v2 = dc.validate_arbitrage_data_contract(c2)
    assert v2["valid"] is False
    assert "scan_result_claimed" in v2["errors"]


def test_validate_rejects_unlocked_gate_or_capability():
    c = dc.build_arbitrage_data_contract()
    c["micro_live_gate_locked"] = False
    v = dc.validate_arbitrage_data_contract(c)
    assert v["valid"] is False
    assert any("gate_not_locked:micro_live_gate_locked" in e for e in v["errors"])
    c2 = dc.build_arbitrage_data_contract()
    c2["fetches_data"] = True
    v2 = dc.validate_arbitrage_data_contract(c2)
    assert v2["valid"] is False
    assert any("capability_not_false:fetches_data" in e for e in v2["errors"])


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #
def test_render_markdown_ready_and_blocked():
    md = dc.render_arbitrage_data_contract_markdown(
        dc.build_arbitrage_data_contract())
    assert md.startswith(
        "# SPARTA Arbitrage Factory V1 Data Contract (STAGED DATA ONLY)")
    assert "Venue labels are NOT connections" in md
    assert "readiness only, never a scan result" in md
    assert "Forbidden fields" in md
    assert "LOCKED" in md
    md2 = dc.render_arbitrage_data_contract_markdown(
        dc.record_arbitrage_data_contract(None))
    assert "BLOCKED defines nothing usable" in md2


# --------------------------------------------------------------------------- #
# label / posture / no banned imports
# --------------------------------------------------------------------------- #
def test_label_is_read_only_staged_label():
    assert dc.get_arbitrage_data_contract_label() == dc.DATA_CONTRACT_LABEL
    assert "READ-ONLY" in dc.DATA_CONTRACT_LABEL
    assert "STAGED DATA ONLY" in dc.DATA_CONTRACT_LABEL
    assert dc.DATA_CONTRACT_MODE == "RESEARCH_ONLY"


def test_action_carries_no_execution_or_promotion_verbs():
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE", "EXECUTION",
                   "BACKTEST", "BASELINE", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in dc.NEXT_REQUIRED_ACTION.upper(), banned


def test_module_imports_no_network_exchange_or_credential_modules():
    with open(dc.__file__, "r", encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    banned = {"urllib", "requests", "socket", "http", "ftplib", "ccxt", "databento",
              "dotenv", "smtplib", "subprocess", "websocket", "websockets", "aiohttp",
              "schedule", "apscheduler", "threading", "multiprocessing", "asyncio",
              "sched", "time", "telegram", "email", "csv", "sqlite3", "pandas"}
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imported.add(n.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert not (imported & banned)
