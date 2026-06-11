"""Tests for the SPARTA Arbitrage Factory V1 Staged-Data Preparation Rules.

Everything here is pure and in-memory; no network, no credentials, no API call, no
exchange connection, no file read/write, no scanner, no scheduler, no gate is
unlocked. Manifests are descriptions of files an operator intends to stage; no
file is ever read."""

from __future__ import annotations

import ast

import sparta_commander.arbitrage_data_contract as dc
import sparta_commander.arbitrage_staged_data_preparation_rules_contract as pr


def _entry(**overrides):
    entry = {
        "filename": "funding_BTC_binance.csv",
        "kind": "funding_rates",
        "columns": ["timestamp_utc", "symbol", "venue", "funding_rate_8h",
                    "mark_price"],
        "first_timestamp_utc": "2026-05-20T00:00:00Z",
        "last_timestamp_utc": "2026-06-09T00:00:00Z",
    }
    entry.update(overrides)
    return entry


def _manifest(entries=None, **overrides):
    manifest = {
        "prepared_as_of_utc": "2026-06-10T00:00:00Z",
        "entries": entries if entries is not None else [_entry()],
    }
    manifest.update(overrides)
    return manifest


def _full_entries():
    return [
        _entry(),
        _entry(filename="basis_ETH_bybit.csv", kind="spot_perp_basis",
               columns=["timestamp_utc", "symbol", "venue", "spot_price",
                        "perp_price", "basis_pct"]),
        _entry(filename="quotes_SOL_okx.csv", kind="cross_exchange_quotes",
               columns=["timestamp_utc", "symbol", "venue", "bid", "ask",
                        "mid"]),
        {"filename": "fees_kraken.csv", "kind": "fee_schedule",
         "columns": ["venue", "symbol", "taker_fee_pct", "maker_fee_pct",
                     "withdrawal_flat_fee"]},
        _entry(filename="depth_BTC_coinbase.csv", kind="liquidity_depth",
               columns=["timestamp_utc", "symbol", "venue",
                        "bid_depth_usd_10bps", "ask_depth_usd_10bps",
                        "spread_bps"]),
    ]


# --------------------------------------------------------------------------- #
# ready data contract -> READY rules
# --------------------------------------------------------------------------- #
def test_rules_ready_on_real_chain():
    c = pr.build_staged_data_preparation_rules()
    assert c["verdict"] == pr.VERDICT_PREP_RULES_READY
    assert c["blockers"] == []
    assert c["data_contract_verdict"] == dc.VERDICT_DATA_CONTRACT_READY
    assert c["staging_folder"] == "data/arbitrage_factory_v1/staged/"
    assert c["next_required_action"] == "HUMAN_PLACES_STAGED_DATA_MANUALLY"


def test_rules_align_with_seq2_data_contract():
    c = pr.build_staged_data_preparation_rules()
    assert sorted(c["dataset_kinds"]) == sorted(dc.STAGED_DATASET_SPECS)
    for kind, cols in c["required_columns_by_kind"].items():
        assert tuple(cols) == dc.STAGED_DATASET_SPECS[kind]["required_columns"]
    assert tuple(c["allowed_symbols"]) == dc.ALLOWED_SYMBOLS
    assert tuple(c["allowed_venue_labels"]) == dc.ALLOWED_VENUE_LABELS
    assert c["max_staleness_days"] == dc.MAX_STALENESS_DAYS_FOR_RESEARCH


def test_preparation_rules_cover_the_core_set():
    joined = " ".join(pr.PREPARATION_RULES)
    assert "data_arbitrage_factory_v1_staged" in joined
    assert "no_fetch_no_api_no_connector" in joined
    assert "utc_iso8601" in joined
    assert "stale_data_must_be_explicitly_acknowledged" in joined
    assert "duplicate_filenames_refuse" in joined
    assert "missing_kinds_are_reported" in joined
    assert "forbidden_account_credential_order_position" in joined
    assert "never_a_scan_result" in joined


def test_build_is_deterministic():
    assert (pr.build_staged_data_preparation_rules()
            == pr.build_staged_data_preparation_rules())


# --------------------------------------------------------------------------- #
# filenames
# --------------------------------------------------------------------------- #
def test_valid_filenames_accepted_per_kind():
    cases = {
        "funding_BTC_binance.csv": "funding_rates",
        "basis_ETH_bybit.csv": "spot_perp_basis",
        "quotes_SOL_okx.csv": "cross_exchange_quotes",
        "fees_kraken.csv": "fee_schedule",
        "depth_BTC_coinbase.csv": "liquidity_depth",
    }
    for name, kind in cases.items():
        v = pr.validate_staged_file_name(name)
        assert v["acceptable"] is True, name
        assert v["kind"] == kind


def test_bad_filenames_refused():
    assert pr.validate_staged_file_name("funding_DOGE_binance.csv")[
        "acceptable"] is False
    assert pr.validate_staged_file_name("funding_BTC_myexchange.csv")[
        "acceptable"] is False
    assert pr.validate_staged_file_name("positions_BTC_binance.csv")[
        "acceptable"] is False
    assert pr.validate_staged_file_name("funding_BTC.csv")["acceptable"] is False
    assert pr.validate_staged_file_name("fees_kraken_extra.csv")[
        "acceptable"] is False
    assert pr.validate_staged_file_name("funding_BTC_binance.xlsx")[
        "acceptable"] is False
    assert pr.validate_staged_file_name("../funding_BTC_binance.csv")[
        "acceptable"] is False
    assert pr.validate_staged_file_name("sub/funding_BTC_binance.csv")[
        "acceptable"] is False
    assert pr.validate_staged_file_name(None)["acceptable"] is False


# --------------------------------------------------------------------------- #
# manifests: valid accepted
# --------------------------------------------------------------------------- #
def test_valid_single_entry_manifest_accepted_but_incomplete():
    r = pr.validate_staging_manifest(_manifest())
    assert r["verdict"] == pr.VERDICT_MANIFEST_ACCEPTED
    assert r["entry_errors"] == {}
    assert r["kinds_covered"] == ["funding_rates"]
    assert "fee_schedule" in r["missing_kinds"]
    assert r["manifest_complete_for_all_kinds"] is False
    assert r["acceptance_is_readiness_only_never_a_scan_result"] is True
    assert r["no_file_was_read"] is True


def test_full_manifest_accepted_and_complete():
    r = pr.validate_staging_manifest(_manifest(entries=_full_entries()))
    assert r["verdict"] == pr.VERDICT_MANIFEST_ACCEPTED
    assert r["missing_kinds"] == []
    assert r["manifest_complete_for_all_kinds"] is True


def test_stale_data_accepted_only_with_acknowledgement():
    stale = _entry(first_timestamp_utc="2026-01-01T00:00:00Z",
                   last_timestamp_utc="2026-02-01T00:00:00Z")
    r = pr.validate_staging_manifest(_manifest(entries=[stale]))
    assert r["verdict"] == pr.VERDICT_MANIFEST_REFUSED
    assert any("stale_data_not_acknowledged" in e
               for e in r["entry_errors"]["funding_BTC_binance.csv"])
    acknowledged = dict(stale, stale_acknowledged=True)
    r2 = pr.validate_staging_manifest(_manifest(entries=[acknowledged]))
    assert r2["verdict"] == pr.VERDICT_MANIFEST_ACCEPTED


def test_manifest_is_deterministic():
    assert pr.validate_staging_manifest(_manifest(entries=_full_entries())) == (
        pr.validate_staging_manifest(_manifest(entries=_full_entries())))


# --------------------------------------------------------------------------- #
# manifests: unsafe refused
# --------------------------------------------------------------------------- #
def test_credential_account_order_position_columns_refuse_entry():
    for bad_col in ("api_key", "account_id", "wallet_balance", "order_id",
                    "open_position", "leverage", "margin_used", "realized_pnl"):
        bad = _entry(columns=_entry()["columns"] + [bad_col])
        r = pr.validate_staging_manifest(_manifest(entries=[bad]))
        assert r["verdict"] == pr.VERDICT_MANIFEST_REFUSED, bad_col
        assert any("forbidden_field" in e
                   for e in r["entry_errors"]["funding_BTC_binance.csv"])


def test_duplicate_filenames_refused():
    r = pr.validate_staging_manifest(_manifest(entries=[_entry(), _entry()]))
    assert r["verdict"] == pr.VERDICT_MANIFEST_REFUSED
    assert any("duplicate_filename_in_manifest" in e
               for errs in r["entry_errors"].values() for e in errs)


def test_kind_filename_mismatch_refused():
    mismatched = _entry(kind="liquidity_depth")
    r = pr.validate_staging_manifest(_manifest(entries=[mismatched]))
    assert r["verdict"] == pr.VERDICT_MANIFEST_REFUSED
    errs = r["entry_errors"]["funding_BTC_binance.csv"]
    assert any("declared_kind_does_not_match_filename_pattern" in e for e in errs)


def test_non_utc_timestamps_refused():
    for bad_ts in ("2026-06-09T00:00:00", "2026-06-09T00:00:00+02:00",
                   "June 9 2026", None):
        bad = _entry(last_timestamp_utc=bad_ts)
        r = pr.validate_staging_manifest(_manifest(entries=[bad]))
        assert r["verdict"] == pr.VERDICT_MANIFEST_REFUSED, bad_ts
        assert any("timestamps_missing_or_not_utc_iso8601" in e
                   for e in r["entry_errors"]["funding_BTC_binance.csv"])


def test_reversed_timestamps_refused():
    bad = _entry(first_timestamp_utc="2026-06-09T00:00:00Z",
                 last_timestamp_utc="2026-05-01T00:00:00Z")
    r = pr.validate_staging_manifest(_manifest(entries=[bad]))
    assert r["verdict"] == pr.VERDICT_MANIFEST_REFUSED
    assert any("last_timestamp_before_first" in e
               for e in r["entry_errors"]["funding_BTC_binance.csv"])


def test_missing_or_malformed_manifest_refused():
    assert pr.validate_staging_manifest(None)["verdict"] == (
        pr.VERDICT_MANIFEST_REFUSED)
    assert pr.validate_staging_manifest({})["verdict"] == (
        pr.VERDICT_MANIFEST_REFUSED)
    no_entries = pr.validate_staging_manifest(
        {"prepared_as_of_utc": "2026-06-10T00:00:00Z", "entries": []})
    assert no_entries["verdict"] == pr.VERDICT_MANIFEST_REFUSED
    assert "entries_missing_or_empty" in no_entries["errors"]
    bad_asof = pr.validate_staging_manifest(
        {"prepared_as_of_utc": "yesterday", "entries": [_entry()]})
    assert bad_asof["verdict"] == pr.VERDICT_MANIFEST_REFUSED


def test_fee_schedule_needs_no_timestamps():
    fee_only = {"filename": "fees_binance.csv", "kind": "fee_schedule",
                "columns": ["venue", "symbol", "taker_fee_pct",
                            "maker_fee_pct", "withdrawal_flat_fee"]}
    r = pr.validate_staging_manifest(_manifest(entries=[fee_only]))
    assert r["verdict"] == pr.VERDICT_MANIFEST_ACCEPTED


# --------------------------------------------------------------------------- #
# gating on the seq-2 data contract
# --------------------------------------------------------------------------- #
def test_missing_data_contract_blocks():
    c = pr.record_staged_data_preparation_rules(None)
    assert c["verdict"] == pr.VERDICT_PREP_RULES_BLOCKED
    assert "data_contract_missing" in c["blockers"]


def test_invalid_data_contract_blocks():
    contract = dc.build_arbitrage_data_contract()
    contract["fetches_data"] = True
    c = pr.record_staged_data_preparation_rules(contract)
    assert c["verdict"] == pr.VERDICT_PREP_RULES_BLOCKED
    assert "data_contract_invalid" in c["blockers"]


def test_blocked_data_contract_blocks():
    blocked = dc.record_arbitrage_data_contract(None)
    c = pr.record_staged_data_preparation_rules(blocked)
    assert c["verdict"] == pr.VERDICT_PREP_RULES_BLOCKED
    assert "data_contract_not_ready" in c["blockers"]


# --------------------------------------------------------------------------- #
# posture
# --------------------------------------------------------------------------- #
def test_rules_are_inert_on_all_paths():
    contracts = [
        pr.build_staged_data_preparation_rules(),
        pr.record_staged_data_preparation_rules(None),
    ]
    for c in contracts:
        assert c["operator_staged_only_no_fetch_no_api_no_connector"] is True
        assert c["scanner_remains_blocked"] is True
        assert c["rules_read_no_files"] is True
        assert c["output_is_readiness_only_never_a_scan_result"] is True
        assert c["human_review_required"] is True
        for key in (
            "executes", "writes_files", "writes_reports", "sends_notifications",
            "runs_scanner", "runs_simulation", "runs_backtest",
            "runs_optimization", "starts_scheduler", "starts_daemon",
            "starts_background_worker", "runs_loop", "fetches_data", "calls_api",
            "connects_broker", "connects_exchange", "uses_real_money",
            "uses_network", "uses_credentials", "contains_order_logic",
            "authorizes_paper_execution", "authorizes_micro_live",
            "authorizes_live_trading", "promotes_gate", "unlocks_downstream_gate",
        ):
            assert c[key] is False, key
        assert c["paper_trading_gate_locked"] is True
        assert c["micro_live_gate_locked"] is True
        assert c["live_gate_locked"] is True


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #
def test_validate_passes_on_ready_and_blocked():
    assert pr.validate_staged_data_preparation_rules(
        pr.build_staged_data_preparation_rules())["valid"] is True
    assert pr.validate_staged_data_preparation_rules(
        pr.record_staged_data_preparation_rules(None))["valid"] is True


def test_validate_rejects_moved_folder_or_tampered_kinds():
    c = pr.build_staged_data_preparation_rules()
    c["staging_folder"] = "C:/anywhere/"
    v = pr.validate_staged_data_preparation_rules(c)
    assert v["valid"] is False
    assert "staging_folder_moved" in v["errors"]
    c2 = pr.build_staged_data_preparation_rules()
    c2["dataset_kinds"].append("live_positions")
    v2 = pr.validate_staged_data_preparation_rules(c2)
    assert v2["valid"] is False
    assert "dataset_kinds_tampered" in v2["errors"]


def test_validate_rejects_diverged_columns_or_labels():
    c = pr.build_staged_data_preparation_rules()
    c["required_columns_by_kind"]["funding_rates"] = ["timestamp_utc"]
    v = pr.validate_staged_data_preparation_rules(c)
    assert v["valid"] is False
    assert "required_columns_diverge_from_data_contract" in v["errors"]
    c2 = pr.build_staged_data_preparation_rules()
    c2["allowed_venue_labels"].append("my_private_exchange")
    v2 = pr.validate_staged_data_preparation_rules(c2)
    assert v2["valid"] is False
    assert "venues_tampered" in v2["errors"]


def test_validate_rejects_dropped_operator_rule_or_scanner_block():
    c = pr.build_staged_data_preparation_rules()
    c["operator_staged_only_no_fetch_no_api_no_connector"] = False
    v = pr.validate_staged_data_preparation_rules(c)
    assert v["valid"] is False
    assert "operator_only_rule_dropped" in v["errors"]
    c2 = pr.build_staged_data_preparation_rules()
    c2["scanner_remains_blocked"] = False
    v2 = pr.validate_staged_data_preparation_rules(c2)
    assert v2["valid"] is False
    assert "scanner_block_dropped" in v2["errors"]


def test_validate_rejects_unlocked_gate_or_capability():
    c = pr.build_staged_data_preparation_rules()
    c["micro_live_gate_locked"] = False
    v = pr.validate_staged_data_preparation_rules(c)
    assert v["valid"] is False
    assert any("gate_not_locked:micro_live_gate_locked" in e for e in v["errors"])
    c2 = pr.build_staged_data_preparation_rules()
    c2["fetches_data"] = True
    v2 = pr.validate_staged_data_preparation_rules(c2)
    assert v2["valid"] is False
    assert any("capability_not_false:fetches_data" in e for e in v2["errors"])


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #
def test_render_markdown_ready_and_blocked():
    md = pr.render_staged_data_preparation_rules_markdown(
        pr.build_staged_data_preparation_rules())
    assert md.startswith(
        "# SPARTA Arbitrage Factory V1 Staged-Data Preparation Rules")
    assert "no fetch, no API, no connector" in md
    assert "scanner remains BLOCKED" in md
    assert "funding_{symbol}_{venue}.csv" in md
    assert "fees_{venue}.csv" in md
    assert "LOCKED" in md
    md2 = pr.render_staged_data_preparation_rules_markdown(
        pr.record_staged_data_preparation_rules(None))
    assert "BLOCKED defines nothing usable" in md2


# --------------------------------------------------------------------------- #
# label / posture / no banned imports
# --------------------------------------------------------------------------- #
def test_label_is_read_only_rules_label():
    assert pr.get_staged_data_preparation_rules_label() == pr.PREP_LABEL
    assert "READ-ONLY" in pr.PREP_LABEL
    assert "RULES ONLY" in pr.PREP_LABEL
    assert pr.PREP_MODE == "RESEARCH_ONLY"


def test_action_carries_no_execution_or_promotion_verbs():
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE", "EXECUTION",
                   "BACKTEST", "BASELINE", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in pr.NEXT_REQUIRED_ACTION.upper(), banned


def test_module_imports_no_network_exchange_or_credential_modules():
    with open(pr.__file__, "r", encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    banned = {"urllib", "requests", "socket", "http", "ftplib", "ccxt", "databento",
              "dotenv", "smtplib", "subprocess", "websocket", "websockets", "aiohttp",
              "schedule", "apscheduler", "threading", "multiprocessing", "asyncio",
              "sched", "time", "telegram", "email", "csv", "sqlite3", "pandas",
              "pathlib", "os", "io"}
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imported.add(n.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert not (imported & banned)
