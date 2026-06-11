"""Tests for the SPARTA NY FVG+CHOCH Public Candle Fetch Plan.

The plan is rules only: nothing is retrieved, written, or run here. The file
creation tool is never invoked with the human token.
"""

from __future__ import annotations

import ast
import os.path

import sparta_commander.ny_session_fvg_choch_public_candle_fetch_plan as fp


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
        "timeframe_mapping": {"1m": "1m", "15m": "15m"},
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


def _no_staging_dir():
    assert not os.path.isdir("data/ny_fvg_choch")
    assert not os.path.isdir("C:/SPARTA_BRAIN/data/ny_fvg_choch")


def test_fetch_plan_gated_on_ready_file_creation_tool():
    plan = fp.build_public_candle_fetch_plan()
    assert plan["verdict"] == fp.VERDICT_FP_READY
    assert plan["blockers"] == []
    assert plan["candidate_id"] == (
        "NY_SESSION_FVG_CHOCH_STRATEGY_CANDIDATE_V1")
    assert fp.validate_public_candle_fetch_plan(plan)["valid"] is True
    import sparta_commander.ny_session_fvg_choch_real_candle_file_creation_tool as fc
    assert fc.TOOL_ENABLED_BY_DEFAULT is False
    _no_staging_dir()


def test_approved_no_auth_public_historical_source_plan_passes():
    result = fp.validate_fetch_source_plan(_source_plan())
    assert result["approvable"] is True and result["errors"] == []
    assert result["human_run_approval_still_required"] is True
    for endpoint in ("/api/v3/klines", "/public/candles",
                     "/market/history/ohlcv"):
        ok = fp.validate_fetch_source_plan(
            _source_plan(endpoint_path=endpoint))
        assert ok["approvable"] is True, endpoint


def test_authenticated_or_api_key_source_rejects():
    for flag in ("uses_authenticated_headers", "requires_api_key",
                 "requires_credentials", "requires_login"):
        bad = fp.validate_fetch_source_plan(_source_plan(**{flag: True}))
        assert bad["approvable"] is False, flag
        assert "forbidden_access_requirement:" + flag in bad["errors"]


def test_private_endpoint_rejects():
    bad = fp.validate_fetch_source_plan(
        _source_plan(uses_private_endpoint=True))
    assert "forbidden_access_requirement:uses_private_endpoint" in (
        bad["errors"])
    bad2 = fp.validate_fetch_source_plan(
        _source_plan(endpoint_path="/private/candles"))
    assert "forbidden_endpoint_token:private" in bad2["errors"]


def test_order_trade_position_account_wallet_balance_endpoints_reject():
    for endpoint, token in (("/api/v3/order_history", "order"),
                            ("/v5/trade/candles", "trade"),
                            ("/position/klines", "position"),
                            ("/account/candles", "account"),
                            ("/wallet/history", "wallet"),
                            ("/balance/ohlcv", "balance"),
                            ("/user/klines", "user"),
                            ("/margin/history", "margin")):
        bad = fp.validate_fetch_source_plan(
            _source_plan(endpoint_path=endpoint))
        assert bad["approvable"] is False, endpoint
        assert "forbidden_endpoint_token:" + token in bad["errors"], endpoint
    not_historical = fp.validate_fetch_source_plan(
        _source_plan(endpoint_path="/api/v3/ticker"))
    assert "endpoint_not_in_historical_allowlist" in not_historical["errors"]
    missing = fp.validate_fetch_source_plan(_source_plan(endpoint_path=""))
    assert "endpoint_path_missing" in missing["errors"]


def test_live_polling_source_rejects():
    bad = fp.validate_fetch_source_plan(_source_plan(is_live_polling=True))
    assert "live_polling_forbidden" in bad["errors"]
    bad2 = fp.validate_fetch_source_plan(_source_plan(historical_only=False))
    assert "source_not_historical_only" in bad2["errors"]


def test_wrong_symbols_and_timeframes_reject():
    bad = fp.validate_fetch_source_plan(
        _source_plan(symbol_mapping={"BTCUSDT": "BTCUSD"}))
    assert "symbol_mapping_does_not_cover_required_symbols" in bad["errors"]
    bad2 = fp.validate_fetch_source_plan(
        _source_plan(symbol_mapping={"DOGEUSDT": "DOGEUSD"}))
    assert "symbol_mapping_does_not_cover_required_symbols" in bad2["errors"]
    bad3 = fp.validate_fetch_source_plan(
        _source_plan(timeframe_mapping={"1m": "1m"}))
    assert ("timeframe_mapping_does_not_cover_required_timeframes"
            in bad3["errors"])
    bad4 = fp.validate_fetch_source_plan(
        _source_plan(timeframe_mapping={"1m": "1m", "4h": "4h",
                                        "15m": "15m"}))
    assert ("timeframe_mapping_does_not_cover_required_timeframes"
            in bad4["errors"])


def test_missing_normalization_schema_rejects():
    bad = fp.validate_fetch_source_plan(
        _source_plan(normalized_fields=("timestamp", "open", "close")))
    assert "normalization_schema_missing_or_wrong" in bad["errors"]
    bad2 = fp.validate_fetch_source_plan(_source_plan(normalized_fields=None))
    assert "normalization_schema_missing_or_wrong" in bad2["errors"]


def test_missing_provenance_rejects():
    bad = fp.validate_fetch_source_plan(_source_plan(provenance=""))
    assert "provenance_missing" in bad["errors"]
    bad2 = fp.validate_fetch_source_plan(_source_plan(terms_and_limits=" "))
    assert "terms_and_limits_missing" in bad2["errors"]
    assert fp.validate_fetch_source_plan(None)["approvable"] is False


def test_missing_date_range_or_session_coverage_rejects():
    bad = fp.validate_fetch_source_plan(_source_plan(date_range=None))
    assert "date_range_plan_missing_or_invalid" in bad["errors"]
    tuned = _source_plan()
    tuned["date_range"] = dict(tuned["date_range"],
                               no_oos_optimization=False)
    assert "date_range_plan_missing_or_invalid" in (
        fp.validate_fetch_source_plan(tuned)["errors"])
    bad2 = fp.validate_fetch_source_plan(_source_plan(session_coverage=None))
    assert "session_coverage_missing_or_wrong" in bad2["errors"]
    bad3 = fp.validate_fetch_source_plan(_source_plan(
        session_coverage={"session_window": "09:30-13:00 America/New_York",
                          "pre_window_minutes": 0,
                          "post_window_minutes": 0}))
    assert "session_coverage_missing_or_wrong" in bad3["errors"]


def test_plan_content_mappings_and_handoff():
    plan = fp.build_public_candle_fetch_plan()
    assert plan["source_category"] == (
        "no_auth_public_historical_endpoint_human_approved")
    assert plan["source_name_placeholder"] == (
        "public_no_auth_historical_klines_source_to_be_named_by_human")
    assert plan["endpoint_allowlist_tokens"] == ["klines", "candles",
                                                 "ohlcv", "history"]
    assert plan["symbol_mapping_plan"]["BTCUSD"] == ["BTCUSD", "BTCUSDT",
                                                     "BTC-USD"]
    assert set(plan["symbol_mapping_plan"]) == {
        "BTCUSD", "ETHUSD", "SOLUSD", "AVAXUSD", "ARBUSD", "XRPUSD"}
    assert plan["timeframe_mapping_plan"] == {"1m": ["1m", "1min", "60"],
                                              "15m": ["15m", "15min", "900"]}
    assert plan["normalized_fields"] == [
        "timestamp", "open", "high", "low", "close", "volume", "source",
        "timeframe", "symbol"]
    assert ("timestamps_normalize_to_utc_iso8601_z"
            in plan["normalization_rules"])
    assert ("gaps_are_flagged_in_flagged_gaps_never_silently_filled"
            in plan["normalization_rules"])
    assert plan["provenance_fields"] == ["source", "endpoint_path_note",
                                         "retrieval_date_note"]
    assert plan["session_coverage"]["session_window"] == (
        "09:30-13:00 America/New_York")
    assert plan["handoff_contract"] == [
        "normalized_rows_pass_through_run_real_candle_staging_dry_run",
        "then_build_file_creation_plan_produces_paths_and_sha256_checksums",
        "then_execute_file_creation_refuses_without_the_exact_human_token",
        "staged_files_remain_untracked_operational_data"]
    assert plan["future_run_approval_required"] is True
    assert plan["rate_limit_terms_note"]


def test_fetch_not_run_and_plan_cannot_run_or_unlock():
    plan = fp.build_public_candle_fetch_plan()
    for key in ("executes", "writes_files", "writes_reports",
                "runs_detector_now", "runs_replay_now", "scores_now",
                "fetches_data", "calls_api", "uses_network",
                "uses_credentials", "uses_wallet", "connects_broker",
                "connects_exchange", "uses_real_money",
                "contains_order_logic", "starts_scheduler",
                "sends_notifications", "authorizes_paper_execution",
                "authorizes_micro_live", "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate"):
        assert plan[key] is False, key
    assert plan["paper_trading_gate_locked"] is True
    assert plan["micro_live_gate_locked"] is True
    assert plan["live_gate_locked"] is True
    tampered = fp.build_public_candle_fetch_plan()
    tampered["uses_network"] = True
    assert fp.validate_public_candle_fetch_plan(tampered)["valid"] is False
    tampered2 = fp.build_public_candle_fetch_plan()
    tampered2["live_gate_locked"] = False
    assert fp.validate_public_candle_fetch_plan(tampered2)["valid"] is False
    tampered3 = fp.build_public_candle_fetch_plan()
    tampered3["forbidden"] = tampered3["forbidden"][:4]
    assert fp.validate_public_candle_fetch_plan(tampered3)["valid"] is False
    tampered4 = fp.build_public_candle_fetch_plan()
    tampered4["endpoint_allowlist_tokens"] = ["klines", "anything"]
    assert fp.validate_public_candle_fetch_plan(tampered4)["valid"] is False
    for item in ("running_a_data_pull_in_this_block",
                 "network_calls_in_tests_or_build", "file_writes",
                 "creating_data_ny_fvg_choch_directory",
                 "api_keys_secrets_credentials",
                 "login_account_wallet_access", "private_endpoints",
                 "trading_endpoints_of_any_kind", "live_market_polling",
                 "detector_replay_scorer_runs", "optimizer_runs",
                 "paper_live_micro_live_authorization", "gate_unlocks"):
        assert item in fp.FORBIDDEN, item
    _no_staging_dir()


def test_file_creation_tool_not_run_and_token_not_used():
    import sparta_commander.ny_session_fvg_choch_real_candle_file_creation_tool as fc
    src = open(__file__, encoding="utf-8").read()
    # the human run token literal never appears in this test file
    assert fc.RUN_APPROVAL_TOKEN not in src
    plan_src = open(fp.__file__, encoding="utf-8").read()
    assert "execute_file_creation" not in plan_src.replace(
        "then_execute_file_creation_refuses_without_the_exact_human_token",
        "")  # plan module never calls the writer
    assert "RUN_APPROVAL_TOKEN" not in plan_src
    _no_staging_dir()


def test_plan_is_deterministic():
    assert (fp.build_public_candle_fetch_plan()
            == fp.build_public_candle_fetch_plan())


def test_upstream_stack_and_pm_lane_untouched():
    import sparta_commander.ny_session_fvg_choch_real_candle_file_creation_tool as fc
    assert fc.TOOL_ENABLED_BY_DEFAULT is False
    assert fc.NEXT_REQUIRED_ACTION == (
        "HUMAN_RUN_APPROVAL_FOR_REAL_CANDLE_FILE_CREATION")
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


def test_label_action_no_network_imports_and_no_files():
    assert fp.get_public_candle_fetch_plan_label() == fp.FP_LABEL
    assert "READ-ONLY" in fp.FP_LABEL and fp.FP_MODE == "RESEARCH_ONLY"
    assert fp.NEXT_REQUIRED_ACTION == (
        "HUMAN_RUN_APPROVAL_FOR_REAL_CANDLE_FILE_CREATION")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in fp.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(fp.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    assert "while true" not in src.lower() and "sleep(" not in src.lower()
    tree = ast.parse(src)
    banned_mods = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
                   "subprocess", "websockets", "aiohttp", "schedule",
                   "apscheduler", "threading", "asyncio", "time", "telegram",
                   "email", "csv", "pandas", "pathlib", "os", "io", "json",
                   "shutil", "databento", "ssl", "ftplib", "datetime",
                   "hashlib"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods)
    assert not any(call.func.attr == "open" if isinstance(call.func, ast.Attribute)
                   else getattr(call.func, "id", "") == "open"
                   for call in ast.walk(tree) if isinstance(call, ast.Call))
    _no_staging_dir()