"""Tests for the SPARTA Prediction Market Factory V1 Data Contract."""

from __future__ import annotations

import ast

import sparta_commander.prediction_market_data_contract as pd
import sparta_commander.prediction_market_scanner_spec_contract as ps


def test_data_contract_ready_on_real_chain():
    c = pd.build_prediction_market_data_contract()
    assert c["verdict"] == pd.VERDICT_PM_DATA_READY
    assert c["blockers"] == []
    assert c["scanner_spec_verdict"] == ps.VERDICT_PM_SPEC_READY
    assert c["lane"] == "prediction_market_factory_v1"
    assert c["roadmap_seq"] == 2
    assert c["staging_root"] == "data/prediction_market_factory_v1/staged/"
    assert c["next_required_action"] == "HUMAN_APPROVED_PM_COST_SETTLEMENT_MODEL"


def test_six_dataset_kinds_with_required_fields():
    c = pd.build_prediction_market_data_contract()
    assert set(c["staged_dataset_specs"]) == {
        "markets", "outcome_prices", "orderbook_quotes", "liquidity_depth",
        "event_relationships", "cost_assumptions"}
    cols = c["staged_dataset_specs"]
    assert "market_id" in cols["markets"]["required_columns"]
    assert "resolution_date_utc" in cols["markets"]["required_columns"]
    assert "outcome_yes_price" in cols["outcome_prices"]["required_columns"]
    assert "yes_bid" in cols["orderbook_quotes"]["required_columns"]
    assert "relationship_type" in cols["event_relationships"]["required_columns"]
    assert "settlement_cost_bps" in cols["cost_assumptions"]["required_columns"]
    for spec in cols.values():
        assert "provenance_label" in spec["required_columns"]
        assert spec["file_pattern"].startswith(pd.STAGING_ROOT)


def test_allowed_labels_closed_lists():
    assert pd.ALLOWED_MARKET_STATUS == ("open", "closed", "resolved", "paused")
    assert pd.ALLOWED_RELATIONSHIPS == (
        "same_event", "mutually_exclusive", "correlated", "inverse",
        "parent_child")


def test_valid_descriptors_accepted():
    for kind, spec in pd.STAGED_DATASET_SPECS.items():
        v = pd.validate_pm_dataset_descriptor(kind, list(spec["required_columns"]))
        assert v["acceptable"] is True, kind


def test_unsafe_private_data_refused():
    base = list(pd.STAGED_DATASET_SPECS["outcome_prices"]["required_columns"])
    for bad in ("wallet_address", "private_key", "seed_phrase",
                "account_balance", "open_position", "order_id", "fill_price",
                "deposit_amount", "withdrawal_tx", "login_name", "session_id",
                "cookie_value", "api_key", "auth_token"):
        v = pd.validate_pm_dataset_descriptor("outcome_prices", base + [bad])
        assert v["acceptable"] is False, bad
        assert any("forbidden_field" in e for e in v["errors"])
    assert pd.validate_pm_dataset_descriptor("live_positions", base)[
        "acceptable"] is False
    v2 = pd.validate_pm_dataset_descriptor("outcome_prices", base[:2])
    assert any("missing_required_column" in e for e in v2["errors"])
    v3 = pd.validate_pm_dataset_descriptor("outcome_prices", base + [base[0]])
    assert "duplicate_column_names" in v3["errors"]


def test_probability_sanity_checks():
    ok = pd.validate_outcome_price_row(0.62, 0.39)
    assert ok["acceptable"] is True and ok["flags"] == []
    drift = pd.validate_outcome_price_row(0.30, 0.30)
    assert drift["acceptable"] is True
    assert "yes_no_sum_outside_sanity_band_check_data_quality" in drift["flags"]
    bad = pd.validate_outcome_price_row(1.4, -0.1)
    assert bad["acceptable"] is False
    assert any("probability_out_of_range" in e for e in bad["errors"])
    assert pd.validate_outcome_price_row("x", 0.5)["acceptable"] is False


def test_gating_blocks_on_bad_upstream():
    assert pd.record_prediction_market_data_contract(None)["verdict"] == (
        pd.VERDICT_PM_DATA_BLOCKED)
    spec = ps.build_prediction_market_scanner_spec()
    spec["runs_scanner"] = True
    c = pd.record_prediction_market_data_contract(spec)
    assert c["verdict"] == pd.VERDICT_PM_DATA_BLOCKED
    assert "scanner_spec_invalid" in c["blockers"]
    blocked = ps.record_prediction_market_scanner_spec(None)
    c2 = pd.record_prediction_market_data_contract(blocked)
    assert "scanner_spec_not_ready" in c2["blockers"]


def test_inert_and_gates_locked_on_all_paths():
    for c in (pd.build_prediction_market_data_contract(),
              pd.record_prediction_market_data_contract(None)):
        assert c["data_describes_markets_never_accounts"] is True
        assert c["contract_reads_no_files"] is True
        assert c["output_is_readiness_only_never_a_scan_result"] is True
        for key in ("executes", "writes_files", "runs_scanner", "fetches_data",
                    "calls_api", "uses_network", "uses_credentials",
                    "uses_wallet", "contains_order_logic", "starts_scheduler",
                    "promotes_gate", "unlocks_downstream_gate"):
            assert c[key] is False, key
        assert c["paper_trading_gate_locked"] is True
        assert c["micro_live_gate_locked"] is True
        assert c["live_gate_locked"] is True


def test_validate_passes_and_catches_tampering():
    ok = pd.build_prediction_market_data_contract()
    assert pd.validate_prediction_market_data_contract(ok)["valid"] is True
    assert pd.validate_prediction_market_data_contract(
        pd.record_prediction_market_data_contract(None))["valid"] is True
    c1 = pd.build_prediction_market_data_contract()
    c1["staged_dataset_specs"]["outcome_prices"]["required_columns"] = (
        "timestamp_utc", "market_id", "wallet_address")
    v1 = pd.validate_prediction_market_data_contract(c1)
    assert v1["valid"] is False
    assert "forbidden_field_in_spec:outcome_prices" in v1["errors"]
    c2 = pd.build_prediction_market_data_contract()
    c2["forbidden_field_tokens"] = [
        t for t in c2["forbidden_field_tokens"] if t != "wallet"]
    assert pd.validate_prediction_market_data_contract(c2)["valid"] is False
    c3 = pd.build_prediction_market_data_contract()
    c3["allowed_market_status"].append("trading")
    assert pd.validate_prediction_market_data_contract(c3)["valid"] is False
    c4 = pd.build_prediction_market_data_contract()
    c4["micro_live_gate_locked"] = False
    assert pd.validate_prediction_market_data_contract(c4)["valid"] is False


def test_build_is_deterministic():
    assert (pd.build_prediction_market_data_contract()
            == pd.build_prediction_market_data_contract())


def test_label_action_and_imports_clean():
    assert pd.get_prediction_market_data_contract_label() == pd.PM_DATA_LABEL
    assert "READ-ONLY" in pd.PM_DATA_LABEL and pd.PM_DATA_MODE == "RESEARCH_ONLY"
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in pd.NEXT_REQUIRED_ACTION.upper(), banned
    tree = ast.parse(open(pd.__file__, encoding="utf-8").read())
    banned_mods = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
                   "subprocess", "websockets", "aiohttp", "schedule",
                   "apscheduler", "threading", "asyncio", "time", "telegram",
                   "email", "csv", "pandas", "pathlib", "os", "io", "json"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods)
