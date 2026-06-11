"""Tests for the SPARTA NY FVG+CHOCH Public Candle Fetch Runner Dry Run.

The runner is built but never really run: no network, no transport, no
files, and the file-creation writer/token are never touched.
"""

from __future__ import annotations

import ast
import datetime as dt
import os.path

import sparta_commander.ny_session_fvg_choch_public_candle_fetch_runner_dry_run as fr


def _source_plan(**overrides):
    plan = {
        "source_name": "public_no_auth_historical_klines_source",
        "category": "no_auth_public_historical_endpoint_human_approved",
        "endpoint_path": "/api/v3/klines",
        "uses_authenticated_headers": False, "requires_api_key": False,
        "requires_credentials": False, "requires_login": False,
        "uses_private_endpoint": False, "is_live_polling": False,
        "historical_only": True,
        "symbol_mapping": {"BTCUSDT": "BTCUSD", "ETHUSDT": "ETHUSD",
                           "SOLUSDT": "SOLUSD", "AVAXUSDT": "AVAXUSD",
                           "ARBUSDT": "ARBUSD", "XRPUSDT": "XRPUSD"},
        "timeframe_mapping": {"1min": "1m", "15min": "15m"},
        "normalized_fields": ("timestamp", "open", "high", "low", "close",
                              "volume", "source", "timeframe", "symbol"),
        "provenance": "public no-auth historical klines, human-named later",
        "terms_and_limits": "public rate limits apply; historical only",
        "date_range": {"train_start": "2024-01-01",
                       "train_end": "2025-06-30",
                       "oos_start": "2025-07-01", "oos_end": "2025-12-31",
                       "no_oos_optimization": True},
        "session_coverage": {"session_window":
                             "09:30-13:00 America/New_York",
                             "pre_window_minutes": 120,
                             "post_window_minutes": 240},
    }
    plan.update(overrides)
    return plan


_ISO = ["2026-06-10T13:3%d:00Z" % i for i in range(3)]


def _epoch_ms(iso):
    return int(dt.datetime.fromisoformat(
        iso.replace("Z", "+00:00")).timestamp()) * 1000


def _raw_row(ts, **overrides):
    row = {"timestamp": ts, "open": "100.0", "high": "101.0", "low": "99.0",
           "close": "100.5", "volume": "12.5"}
    row.update(overrides)
    return row


def _batch(**overrides):
    batch = {"source_symbol": "BTCUSDT", "source_timeframe": "1min",
             "rows": [_raw_row(_ISO[0]), _raw_row(_ISO[1]),
                      _raw_row(_ISO[2])]}
    batch.update(overrides)
    return batch


def _no_staging_dir():
    assert not os.path.isdir("data/ny_fvg_choch")
    assert not os.path.isdir("C:/SPARTA_BRAIN/data/ny_fvg_choch")


def test_runner_built_disabled_and_gated_on_ready_plan():
    assert fr.RUNNER_ENABLED_BY_DEFAULT is False
    assert fr.REAL_TRANSPORT_BUILT is False
    record = fr.run_public_candle_fetch_runner_dry_run(_source_plan(),
                                                       [_batch()])
    assert record["runner_status"] == (
        "FETCH_RUNNER_DRY_RUN_READY_FOR_HUMAN_RUN_APPROVAL")
    assert record["errors"] == []
    assert record["runner_enabled_by_default"] is False
    assert record["real_transport_built"] is False
    assert fr.validate_fetch_runner_record(record)["valid"] is True
    _no_staging_dir()


def test_valid_fixture_rows_pass_full_dry_run_chain():
    record = fr.run_public_candle_fetch_runner_dry_run(
        _source_plan(),
        [_batch(),
         _batch(source_symbol="ETHUSDT",
                rows=[_raw_row(_ISO[i]) for i in range(3)])])
    assert record["batches_normalized"] == 2
    assert record["rows_normalized"] == 6
    assert record["file_creation_plan_status"] == (
        "FILE_CREATION_PLAN_READY_FOR_HUMAN_RUN_APPROVAL")
    assert len(record["planned_files"]) == 2
    assert record["planned_files"][0]["target_path"] == (
        "data/ny_fvg_choch/staged/BTCUSD_1m_2026-06-10_2026-06-10.csv")
    assert record["planned_files"][1]["symbol"] == "ETHUSD"
    for entry in record["planned_files"]:
        assert len(entry["sha256"]) == 64 and entry["row_count"] == 3
        assert "content" not in entry
    _no_staging_dir()


def test_normalization_aliases_epoch_and_string_numbers():
    rows = [_raw_row(_epoch_ms(_ISO[0])), _raw_row(_epoch_ms(_ISO[1])),
            _raw_row(_epoch_ms(_ISO[2]))]
    result = fr.normalize_raw_batch(_source_plan(), _batch(rows=rows))
    assert result["acceptable"] is True
    payload = result["payload"]
    assert payload["symbol"] == "BTCUSD" and payload["timeframe"] == "1m"
    assert [r["timestamp"] for r in payload["rows"]] == _ISO
    first = payload["rows"][0]
    assert first["open"] == 100.0 and first["volume"] == 12.5
    assert first["source"] == "public_no_auth_historical_klines_source"
    fifteen = _source_plan()
    result2 = fr.normalize_raw_batch(fifteen, _batch(
        source_timeframe="15min",
        rows=[_raw_row("2026-06-10T13:30:00Z"),
              _raw_row("2026-06-10T13:45:00Z"),
              _raw_row("2026-06-10T14:00:00Z")]))
    assert result2["acceptable"] is True
    assert result2["payload"]["timeframe"] == "15m"


def test_wrong_endpoint_category_rejects():
    bad = fr.run_public_candle_fetch_runner_dry_run(
        _source_plan(category="manually_supplied_human_approved_csv"),
        [_batch()])
    assert bad["runner_status"] == "FETCH_RUNNER_REJECTED_SOURCE_PLAN_INVALID"
    bad2 = fr.run_public_candle_fetch_runner_dry_run(
        _source_plan(endpoint_path="/api/v3/ticker"), [_batch()])
    assert bad2["runner_status"] == (
        "FETCH_RUNNER_REJECTED_SOURCE_PLAN_INVALID")
    assert "endpoint_not_in_historical_allowlist" in bad2["errors"]


def test_private_order_account_wallet_balance_endpoints_reject():
    for endpoint in ("/private/klines", "/api/order_history/candles",
                     "/account/klines", "/wallet/candles",
                     "/balance/history", "/position/ohlcv"):
        bad = fr.run_public_candle_fetch_runner_dry_run(
            _source_plan(endpoint_path=endpoint), [_batch()])
        assert bad["runner_status"] == (
            "FETCH_RUNNER_REJECTED_SOURCE_PLAN_INVALID"), endpoint
        assert any(e.startswith("forbidden_endpoint_token:")
                   for e in bad["errors"]), endpoint


def test_auth_api_key_credential_config_rejects():
    for flag in ("uses_authenticated_headers", "requires_api_key",
                 "requires_credentials", "requires_login",
                 "uses_private_endpoint"):
        bad = fr.run_public_candle_fetch_runner_dry_run(
            _source_plan(**{flag: True}), [_batch()])
        assert bad["runner_status"] == (
            "FETCH_RUNNER_REJECTED_SOURCE_PLAN_INVALID"), flag
    polling = fr.run_public_candle_fetch_runner_dry_run(
        _source_plan(is_live_polling=True), [_batch()])
    assert "live_polling_forbidden" in polling["errors"]
    leak = fr.run_public_candle_fetch_runner_dry_run(
        _source_plan(), [_batch(api_key_header="x")])
    assert leak["runner_status"] == (
        "FETCH_RUNNER_REJECTED_FORBIDDEN_CAPABILITY")


def test_wrong_symbols_and_timeframes_reject():
    bad = fr.run_public_candle_fetch_runner_dry_run(
        _source_plan(), [_batch(source_symbol="DOGEUSDT")])
    assert bad["runner_status"] == "FETCH_RUNNER_REJECTED_REQUEST_INVALID"
    assert any("source_symbol_not_mapped" in e for e in bad["errors"])
    bad2 = fr.run_public_candle_fetch_runner_dry_run(
        _source_plan(), [_batch(source_timeframe="4h")])
    assert any("source_timeframe_not_mapped" in e for e in bad2["errors"])


def test_malformed_normalized_rows_reject():
    missing = _raw_row(_ISO[1])
    del missing["volume"]
    bad = fr.run_public_candle_fetch_runner_dry_run(
        _source_plan(), [_batch(rows=[_raw_row(_ISO[0]), missing])])
    assert bad["runner_status"] == "FETCH_RUNNER_REJECTED_REQUEST_INVALID"
    assert any("missing_fields:volume" in e for e in bad["errors"])
    bad2 = fr.run_public_candle_fetch_runner_dry_run(
        _source_plan(), [_batch(rows=[_raw_row("not-a-time")])])
    assert any("timestamp_not_normalizable" in e for e in bad2["errors"])
    bad3 = fr.run_public_candle_fetch_runner_dry_run(
        _source_plan(), [_batch(rows=[_raw_row(_ISO[0], close="abc")])])
    assert any("non_numeric:close" in e for e in bad3["errors"])
    bad4 = fr.run_public_candle_fetch_runner_dry_run(
        _source_plan(),
        [_batch(rows=[_raw_row(_ISO[0], high="98.0")])])
    assert any("ohlc_inconsistent" in e for e in bad4["errors"])
    bad5 = fr.run_public_candle_fetch_runner_dry_run(_source_plan(), [])
    assert "raw_batches_missing_or_empty" in bad5["errors"]


def test_unflagged_gap_rejects_and_flagged_passes_through():
    gapped = [_raw_row(_ISO[0]), _raw_row(_ISO[1]),
              _raw_row("2026-06-10T13:40:00Z")]
    bad = fr.run_public_candle_fetch_runner_dry_run(
        _source_plan(), [_batch(rows=gapped)])
    assert bad["runner_status"] == "FETCH_RUNNER_REJECTED_REQUEST_INVALID"
    assert any("unflagged_gap_after" in e for e in bad["errors"])
    ok = fr.run_public_candle_fetch_runner_dry_run(
        _source_plan(), [_batch(rows=gapped, flagged_gaps=[
            {"from_timestamp": _ISO[1],
             "to_timestamp": "2026-06-10T13:40:00Z"}])])
    assert ok["runner_status"] == (
        "FETCH_RUNNER_DRY_RUN_READY_FOR_HUMAN_RUN_APPROVAL")


def test_real_run_always_refuses():
    for attempt in (fr.attempt_real_fetch_run(),
                    fr.attempt_real_fetch_run("please"),
                    fr.attempt_real_fetch_run(run_approval="anything",
                                              transport=object())):
        assert attempt["runner_status"] == (
            "FETCH_RUNNER_REFUSED_REAL_RUN_NOT_APPROVED")
        assert ("real_transport_not_built_requires_future_human_approved_block"
                in attempt["errors"])
        assert attempt["planned_files"] == []
    _no_staging_dir()


def test_runner_cannot_write_run_or_unlock():
    record = fr.run_public_candle_fetch_runner_dry_run(_source_plan(),
                                                       [_batch()])
    for key in ("executes", "writes_files", "writes_reports",
                "runs_detector_now", "runs_replay_now", "scores_now",
                "fetches_data", "calls_api", "uses_network",
                "uses_credentials", "uses_wallet", "connects_broker",
                "connects_exchange", "uses_real_money",
                "contains_order_logic", "starts_scheduler",
                "sends_notifications", "authorizes_paper_execution",
                "authorizes_micro_live", "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate"):
        assert record[key] is False, key
    assert record["paper_trading_gate_locked"] is True
    assert record["micro_live_gate_locked"] is True
    assert record["live_gate_locked"] is True
    tampered = fr.run_public_candle_fetch_runner_dry_run(_source_plan(),
                                                         [_batch()])
    tampered["uses_network"] = True
    assert fr.validate_fetch_runner_record(tampered)["valid"] is False
    tampered2 = fr.run_public_candle_fetch_runner_dry_run(_source_plan(),
                                                          [_batch()])
    tampered2["runner_enabled_by_default"] = True
    assert fr.validate_fetch_runner_record(tampered2)["valid"] is False
    tampered3 = fr.run_public_candle_fetch_runner_dry_run(_source_plan(),
                                                          [_batch()])
    tampered3["real_transport_built"] = True
    assert fr.validate_fetch_runner_record(tampered3)["valid"] is False


def test_file_creation_tool_not_executed_and_token_not_used():
    import sparta_commander.ny_session_fvg_choch_real_candle_file_creation_tool as fc
    runner_src = open(fr.__file__, encoding="utf-8").read()
    assert "execute_file_creation" not in runner_src
    assert "RUN_APPROVAL_TOKEN" not in runner_src
    test_src = open(__file__, encoding="utf-8").read()
    assert fc.RUN_APPROVAL_TOKEN not in test_src
    _no_staging_dir()


def test_runner_is_deterministic():
    a = fr.run_public_candle_fetch_runner_dry_run(_source_plan(), [_batch()])
    b = fr.run_public_candle_fetch_runner_dry_run(_source_plan(), [_batch()])
    assert a == b


def test_upstream_stack_and_pm_lane_untouched():
    import sparta_commander.ny_session_fvg_choch_public_candle_fetch_plan as fp
    assert fp.build_public_candle_fetch_plan()["verdict"] == (
        "NY_FVG_CHOCH_PUBLIC_CANDLE_FETCH_PLAN_READY")
    import sparta_commander.ny_session_fvg_choch_real_candle_file_creation_tool as fc
    assert fc.TOOL_ENABLED_BY_DEFAULT is False
    import sparta_commander.ny_session_fvg_choch_real_candle_staging_dry_run as sd
    assert sd.APPROVED_SOURCE_CATEGORY_FOR_DRY_RUN == (
        "no_auth_public_historical_endpoint_human_approved")
    import sparta_commander.ny_session_fvg_choch_candle_source_approval_contract as sa
    assert sa.build_candle_source_approval_contract()["verdict"] == (
        "NY_FVG_CHOCH_CANDLE_SOURCE_APPROVAL_READY")
    import sparta_commander.ny_session_fvg_choch_real_candle_staging_plan as plan_mod
    assert plan_mod.build_real_candle_staging_plan()["verdict"] == (
        "NY_FVG_CHOCH_REAL_CANDLE_STAGING_PLAN_READY")
    import sparta_commander.ny_session_fvg_choch_dry_run_replay_results_review_contract as rv
    assert rv.build_dry_run_replay_results_review()["verdict"] == (
        "DRY_RUN_REPLAY_RESULTS_ACCEPTED_FOR_REAL_CANDLE_STAGING")
    from sparta_commander.ny_session_fvg_choch_replay_runner_dry_run import (
        get_replay_runner_dry_run_label)
    assert "Replay Runner" in get_replay_runner_dry_run_label()
    from sparta_commander.ny_session_fvg_choch_replay_spec import (
        build_ny_fvg_choch_replay_spec)
    assert build_ny_fvg_choch_replay_spec()["verdict"] == (
        "NY_FVG_CHOCH_REPLAY_SPEC_READY")
    from sparta_commander.ny_session_fvg_choch_detector_spec import (
        LABEL_REQUIRED_FIELDS)
    assert len(LABEL_REQUIRED_FIELDS) == 29
    from sparta_commander.ny_session_fvg_choch_strategy_spec_contract import (
        CANDIDATE_ID)
    assert CANDIDATE_ID == "NY_SESSION_FVG_CHOCH_STRATEGY_CANDIDATE_V1"
    from sparta_commander.crypto_d1_auto_research_mutable_candidate_asset_spec import (
        ALLOWED_EDITABLE_FIELDS)
    assert len(ALLOWED_EDITABLE_FIELDS) == 16
    from sparta_commander.crypto_d1_auto_research_strategy_optimizer_contract import (
        build_optimizer_contract)
    assert build_optimizer_contract()["verdict"] == (
        "CRYPTO_D1_AUTO_RESEARCH_OPTIMIZER_CONTRACT_READY")
    from sparta_commander.strategy_factory_mission_flow_status import (
        LATEST_COMPLETED_PM_LANE_CHAIN)
    assert "Research Only" in LATEST_COMPLETED_PM_LANE_CHAIN


def test_label_action_no_autorun_no_network_imports_no_files():
    assert fr.get_public_candle_fetch_runner_label() == fr.FR_LABEL
    assert "READ-ONLY" in fr.FR_LABEL and fr.FR_MODE == "RESEARCH_ONLY"
    assert fr.NEXT_REQUIRED_ACTION == (
        "HUMAN_RUN_APPROVAL_FOR_REAL_CANDLE_FILE_CREATION")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in fr.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(fr.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    assert "while true" not in src.lower() and "sleep(" not in src.lower()
    tree = ast.parse(src)
    banned_mods = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
                   "subprocess", "websockets", "aiohttp", "schedule",
                   "apscheduler", "threading", "asyncio", "time", "telegram",
                   "email", "csv", "pandas", "pathlib", "os", "io", "json",
                   "shutil", "databento", "ssl", "ftplib", "hashlib"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods)
    assert not any(call.func.attr == "open" if isinstance(call.func, ast.Attribute)
                   else getattr(call.func, "id", "") == "open"
                   for call in ast.walk(tree) if isinstance(call, ast.Call))
    _no_staging_dir()