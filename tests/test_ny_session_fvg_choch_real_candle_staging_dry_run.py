"""Tests for the SPARTA NY FVG+CHOCH Real-Candle Staging Dry Run."""

from __future__ import annotations

import ast

import sparta_commander.ny_session_fvg_choch_real_candle_staging_dry_run as sd


def _proposal(**overrides):
    proposal = {
        "source_name": "public_no_auth_historical_klines",
        "category": "no_auth_public_historical_endpoint_human_approved",
        "provenance": "public no-auth historical kline endpoint, human-named",
        "terms_and_limits": "public rate limits apply; historical only",
        "historical_only": True,
        "requires_login": False, "requires_api_key": False,
        "requires_credentials": False, "uses_private_endpoint": False,
        "is_live_polling": False,
        "symbols": ("BTCUSD", "ETHUSD", "SOLUSD", "AVAXUSD", "ARBUSD",
                    "XRPUSD"),
        "timeframes": ("1m", "15m"),
        "output_fields": ("timestamp", "open", "high", "low", "close",
                          "volume", "source", "timeframe", "symbol"),
    }
    proposal.update(overrides)
    return proposal


def _row(ts, **overrides):
    row = {"timestamp": ts, "open": 100.0, "high": 101.0, "low": 99.0,
           "close": 100.5, "volume": 12.5, "source": "public_no_auth",
           "timeframe": "1m", "symbol": "BTCUSD"}
    row.update(overrides)
    return row


_T = ["2026-06-10T13:3%d:00Z" % i for i in range(6)]


def _payload(**overrides):
    payload = {"symbol": "BTCUSD", "timeframe": "1m",
               "rows": [_row(_T[0]), _row(_T[1]), _row(_T[2])]}
    payload.update(overrides)
    return payload


def test_valid_approved_source_passes_staging_readiness():
    record = sd.run_real_candle_staging_dry_run(_proposal(), _payload())
    assert record["staging_status"] == (
        "STAGING_DRY_RUN_READY_FOR_HUMAN_FILE_APPROVAL")
    assert record["errors"] == []
    assert record["rows_validated"] == 3
    assert record["candidate_id"] == (
        "NY_SESSION_FVG_CHOCH_STRATEGY_CANDIDATE_V1")
    assert record["produces_files"] is False
    assert record["produces_readiness_result_only"] is True
    assert record[
        "actual_file_creation_requires_separate_human_approval"] is True
    assert sd.validate_staging_dry_run_record(record)["valid"] is True


def test_all_symbols_and_15m_supported():
    for symbol in ("BTCUSD", "ETHUSD", "SOLUSD", "AVAXUSD", "ARBUSD",
                   "XRPUSD"):
        rows = [_row(_T[i], symbol=symbol) for i in range(3)]
        record = sd.run_real_candle_staging_dry_run(
            _proposal(), _payload(symbol=symbol, rows=rows))
        assert record["staging_status"] == (
            "STAGING_DRY_RUN_READY_FOR_HUMAN_FILE_APPROVAL"), symbol
    fifteen = ["2026-06-10T13:%02d:00Z" % m for m in (30, 45)] + [
        "2026-06-10T14:00:00Z"]
    rows = [_row(ts, timeframe="15m") for ts in fifteen]
    record = sd.run_real_candle_staging_dry_run(
        _proposal(), _payload(timeframe="15m", rows=rows))
    assert record["staging_status"] == (
        "STAGING_DRY_RUN_READY_FOR_HUMAN_FILE_APPROVAL")


def test_unapproved_source_category_rejects():
    for category in ("repo_local_approved_historical_files",
                     "manually_supplied_human_approved_csv",
                     "scraping_behind_login"):
        record = sd.run_real_candle_staging_dry_run(
            _proposal(category=category), _payload())
        assert record["staging_status"] == (
            "STAGING_DRY_RUN_REJECTED_SOURCE_NOT_APPROVED"), category
    assert sd.APPROVED_SOURCE_CATEGORY_FOR_DRY_RUN == (
        "no_auth_public_historical_endpoint_human_approved")


def test_login_api_key_credential_source_rejects():
    for flag in ("requires_login", "requires_api_key",
                 "requires_credentials", "uses_private_endpoint"):
        record = sd.run_real_candle_staging_dry_run(
            _proposal(**{flag: True}), _payload())
        assert record["staging_status"] == (
            "STAGING_DRY_RUN_REJECTED_SOURCE_NOT_APPROVED"), flag
        assert any("forbidden_access_requirement" in e
                   for e in record["errors"]), flag


def test_live_polling_source_rejects():
    record = sd.run_real_candle_staging_dry_run(
        _proposal(is_live_polling=True), _payload())
    assert record["staging_status"] == (
        "STAGING_DRY_RUN_REJECTED_SOURCE_NOT_APPROVED")
    assert "live_polling_forbidden" in record["errors"]
    record2 = sd.run_real_candle_staging_dry_run(
        _proposal(historical_only=False), _payload())
    assert "source_not_historical_only" in record2["errors"]


def test_wrong_symbol_and_timeframe_reject():
    record = sd.run_real_candle_staging_dry_run(
        _proposal(), _payload(symbol="DOGEUSD"))
    assert record["staging_status"] == (
        "STAGING_DRY_RUN_REJECTED_PAYLOAD_INVALID")
    assert any(e.startswith("symbol_not_in_approved_set:")
               for e in record["errors"])
    record2 = sd.run_real_candle_staging_dry_run(
        _proposal(), _payload(timeframe="5m"))
    assert any(e.startswith("timeframe_not_supported:")
               for e in record2["errors"])
    mismatch = _payload(rows=[_row(_T[0], symbol="ETHUSD"), _row(_T[1])])
    record3 = sd.run_real_candle_staging_dry_run(_proposal(), mismatch)
    assert any("symbol_mismatch_with_declared" in e
               for e in record3["errors"])
    tf_mismatch = _payload(rows=[_row(_T[0], timeframe="15m"), _row(_T[1])])
    record4 = sd.run_real_candle_staging_dry_run(_proposal(), tf_mismatch)
    assert any("timeframe_mismatch_with_declared" in e
               for e in record4["errors"])


def test_missing_required_field_rejects():
    bad = _row(_T[1])
    del bad["volume"]
    record = sd.run_real_candle_staging_dry_run(
        _proposal(), _payload(rows=[_row(_T[0]), bad]))
    assert record["staging_status"] == (
        "STAGING_DRY_RUN_REJECTED_PAYLOAD_INVALID")
    assert any("missing_fields:volume" in e for e in record["errors"])
    record2 = sd.run_real_candle_staging_dry_run(_proposal(),
                                                 _payload(rows=[]))
    assert "rows_missing_or_empty" in record2["errors"]


def test_bad_timestamp_order_rejects():
    record = sd.run_real_candle_staging_dry_run(
        _proposal(), _payload(rows=[_row(_T[1]), _row(_T[0])]))
    assert any("timestamps_not_monotonic" in e for e in record["errors"])
    naive = _payload(rows=[_row("2026-06-10 13:30:00")])
    record2 = sd.run_real_candle_staging_dry_run(_proposal(), naive)
    assert any("timestamp_not_utc_normalized" in e for e in record2["errors"])
    offset = _payload(rows=[_row("2026-06-10T09:30:00-04:00")])
    record3 = sd.run_real_candle_staging_dry_run(_proposal(), offset)
    assert any("timestamp_not_utc_normalized" in e for e in record3["errors"])


def test_duplicate_candles_reject():
    record = sd.run_real_candle_staging_dry_run(
        _proposal(), _payload(rows=[_row(_T[0]), _row(_T[0])]))
    assert record["staging_status"] == (
        "STAGING_DRY_RUN_REJECTED_PAYLOAD_INVALID")
    assert any("duplicate_candle" in e for e in record["errors"])


def test_negative_ohlcv_rejects():
    record = sd.run_real_candle_staging_dry_run(
        _proposal(), _payload(rows=[_row(_T[0], volume=-1.0)]))
    assert any("negative_value:volume" in e for e in record["errors"])
    record2 = sd.run_real_candle_staging_dry_run(
        _proposal(), _payload(rows=[_row(_T[0], low=-5.0, open=1.0,
                                         close=1.0, high=2.0)]))
    assert any("negative_value:low" in e for e in record2["errors"])
    record3 = sd.run_real_candle_staging_dry_run(
        _proposal(), _payload(rows=[_row(_T[0], close="x")]))
    assert any("non_numeric:close" in e for e in record3["errors"])


def test_ohlc_inconsistency_rejects():
    record = sd.run_real_candle_staging_dry_run(
        _proposal(), _payload(rows=[_row(_T[0], high=98.0)]))
    assert any("ohlc_inconsistent" in e for e in record["errors"])
    record2 = sd.run_real_candle_staging_dry_run(
        _proposal(), _payload(rows=[_row(_T[0], close=200.0)]))
    assert any("ohlc_inconsistent" in e for e in record2["errors"])


def test_missing_source_rejects():
    record = sd.run_real_candle_staging_dry_run(
        _proposal(), _payload(rows=[_row(_T[0], source="")]))
    assert record["staging_status"] == (
        "STAGING_DRY_RUN_REJECTED_PAYLOAD_INVALID")
    assert any("source_missing" in e for e in record["errors"])


def test_unflagged_gap_blocks_and_flagged_gap_passes():
    gapped = [_row(_T[0]), _row(_T[1]), _row("2026-06-10T13:40:00Z")]
    record = sd.run_real_candle_staging_dry_run(
        _proposal(), _payload(rows=gapped))
    assert record["staging_status"] == (
        "STAGING_DRY_RUN_REJECTED_PAYLOAD_INVALID")
    assert any("unflagged_gap_after" in e for e in record["errors"])
    flagged = _payload(rows=gapped, flagged_gaps=[
        {"from_timestamp": _T[1], "to_timestamp": "2026-06-10T13:40:00Z"}])
    record2 = sd.run_real_candle_staging_dry_run(_proposal(), flagged)
    assert record2["staging_status"] == (
        "STAGING_DRY_RUN_READY_FOR_HUMAN_FILE_APPROVAL")
    assert record2["gaps_flagged_count"] == 1


def test_forbidden_payload_fields_reject():
    for bad in ("order_id", "api_key_env", "wallet_address",
                "account_balance", "login_token", "fetch_url",
                "live_authorized_flag"):
        record = sd.run_real_candle_staging_dry_run(
            _proposal(), _payload(**{bad: "x"}))
        assert record["staging_status"] == (
            "STAGING_DRY_RUN_REJECTED_FORBIDDEN_CAPABILITY"), bad


def test_dry_run_cannot_fetch_write_run_or_unlock():
    record = sd.run_real_candle_staging_dry_run(_proposal(), _payload())
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
    tampered = sd.run_real_candle_staging_dry_run(_proposal(), _payload())
    tampered["writes_files"] = True
    assert sd.validate_staging_dry_run_record(tampered)["valid"] is False
    tampered2 = sd.run_real_candle_staging_dry_run(_proposal(), _payload())
    tampered2["live_gate_locked"] = False
    assert sd.validate_staging_dry_run_record(tampered2)["valid"] is False


def test_dry_run_is_deterministic_and_returns_result_not_files():
    a = sd.run_real_candle_staging_dry_run(_proposal(), _payload())
    b = sd.run_real_candle_staging_dry_run(_proposal(), _payload())
    assert a == b
    import os.path
    assert not os.path.isdir("data/ny_fvg_choch")
    assert not os.path.isdir("C:/SPARTA_BRAIN/data/ny_fvg_choch")


def test_upstream_stack_and_pm_lane_untouched():
    import sparta_commander.ny_session_fvg_choch_real_candle_staging_plan as plan_mod
    assert plan_mod.build_real_candle_staging_plan()["verdict"] == (
        "NY_FVG_CHOCH_REAL_CANDLE_STAGING_PLAN_READY")
    import sparta_commander.ny_session_fvg_choch_candle_source_approval_contract as sa
    assert sa.build_candle_source_approval_contract()["verdict"] == (
        "NY_FVG_CHOCH_CANDLE_SOURCE_APPROVAL_READY")
    import sparta_commander.ny_session_fvg_choch_dry_run_replay_results_review_contract as rv
    assert rv.build_dry_run_replay_results_review()["verdict"] == (
        "DRY_RUN_REPLAY_RESULTS_ACCEPTED_FOR_REAL_CANDLE_STAGING")
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


def test_label_action_and_imports_clean():
    assert sd.get_real_candle_staging_dry_run_label() == sd.SD_LABEL
    assert "READ-ONLY" in sd.SD_LABEL and sd.SD_MODE == "RESEARCH_ONLY"
    assert sd.NEXT_REQUIRED_ACTION == (
        "HUMAN_APPROVED_REAL_CANDLE_FILE_CREATION")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in sd.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(sd.__file__, encoding="utf-8").read()
    assert "while true" not in src.lower() and "sleep(" not in src.lower()
    tree = ast.parse(src)
    banned_mods = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
                   "subprocess", "websockets", "aiohttp", "schedule",
                   "apscheduler", "threading", "asyncio", "time", "telegram",
                   "email", "csv", "pandas", "pathlib", "os", "io", "json",
                   "shutil", "databento"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods)
    assert not any(call.func.attr == "open" if isinstance(call.func, ast.Attribute)
                   else getattr(call.func, "id", "") == "open"
                   for call in ast.walk(tree) if isinstance(call, ast.Call))
