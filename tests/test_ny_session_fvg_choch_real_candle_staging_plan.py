"""Tests for the SPARTA NY FVG+CHOCH Real-Candle Staging Plan."""

from __future__ import annotations

import ast

import sparta_commander.ny_session_fvg_choch_real_candle_staging_plan as sp


def test_plan_gated_on_accepted_dry_run_review():
    plan = sp.build_real_candle_staging_plan()
    assert plan["verdict"] == sp.VERDICT_SP_READY
    assert plan["blockers"] == []
    assert plan["candidate_id"] == "NY_SESSION_FVG_CHOCH_STRATEGY_CANDIDATE_V1"
    assert sp.validate_real_candle_staging_plan(plan)["valid"] is True
    import sparta_commander.ny_session_fvg_choch_dry_run_replay_results_review_contract as rv
    assert rv.VERDICT_ACCEPTED == (
        "DRY_RUN_REPLAY_RESULTS_ACCEPTED_FOR_REAL_CANDLE_STAGING")
    assert sp.DRY_RUN_ACCEPTED == rv.VERDICT_ACCEPTED


def test_required_candle_schema_complete():
    assert sp.REQUIRED_TIMEFRAMES == ("1m", "15m")
    assert sp.REQUIRED_SYMBOLS == ("BTCUSD", "ETHUSD", "SOLUSD", "AVAXUSD",
                                   "ARBUSD", "XRPUSD")
    assert sp.REQUIRED_CANDLE_FIELDS == (
        "timestamp", "open", "high", "low", "close", "volume", "source",
        "timeframe", "symbol")
    full = sp.validate_candle_schema(list(sp.REQUIRED_CANDLE_FIELDS))
    assert full["acceptable"] is True and full["errors"] == []


def test_missing_fields_reject():
    columns = [c for c in sp.REQUIRED_CANDLE_FIELDS if c != "volume"]
    result = sp.validate_candle_schema(columns)
    assert result["acceptable"] is False
    assert "missing_required_field:volume" in result["errors"]
    assert sp.validate_candle_schema([])["acceptable"] is False
    assert sp.validate_candle_schema(None)["acceptable"] is False
    dup = sp.validate_candle_schema(list(sp.REQUIRED_CANDLE_FIELDS) + ["close"])
    assert "duplicate_column_names" in dup["errors"]


def _row(**overrides):
    row = {"timestamp": "2026-06-11T13:30:00Z", "open": 100.0, "high": 101.0,
           "low": 99.0, "close": 100.5, "volume": 12.5,
           "source": "human_approved_public_source", "timeframe": "1m",
           "symbol": "BTCUSD"}
    row.update(overrides)
    return row


def test_good_row_accepted_and_bad_timestamps_reject():
    assert sp.validate_candle_row(_row())["acceptable"] is True
    bad = sp.validate_candle_row(_row(timestamp="not-a-time"))
    assert bad["acceptable"] is False
    assert "timestamp_not_utc_iso8601" in bad["errors"]
    assert sp.validate_candle_row(None)["acceptable"] is False


def test_bad_ohlcv_values_reject():
    neg = sp.validate_candle_row(_row(volume=-1.0))
    assert "negative_value:volume" in neg["errors"]
    negp = sp.validate_candle_row(_row(low=-5.0))
    assert "negative_value:low" in negp["errors"]
    rel = sp.validate_candle_row(_row(high=98.0))
    assert "ohlc_relationship_invalid" in rel["errors"]
    nonnum = sp.validate_candle_row(_row(open="x"))
    assert "non_numeric:open" in nonnum["errors"]
    booly = sp.validate_candle_row(_row(close=True))
    assert "non_numeric:close" in booly["errors"]


def test_missing_source_provenance_rejects():
    result = sp.validate_candle_row(_row(source=""))
    assert result["acceptable"] is False
    assert "source_provenance_missing" in result["errors"]
    tf = sp.validate_candle_row(_row(timeframe="5m"))
    assert "timeframe_outside_required_set" in tf["errors"]
    sym = sp.validate_candle_row(_row(symbol="DOGEUSD"))
    assert "symbol_outside_required_set" in sym["errors"]


def _split(**overrides):
    plan = {"train_start": "2024-01-01", "train_end": "2025-06-30",
            "oos_start": "2025-07-01", "oos_end": "2025-12-31",
            "no_oos_optimization": True}
    plan.update(overrides)
    return plan


def test_train_oos_split_required_and_oos_optimization_forbidden():
    assert sp.validate_date_range_plan(_split())["acceptable"] is True
    missing = sp.validate_date_range_plan(_split(oos_end=None))
    assert "missing_window_bound:oos_end" in missing["errors"]
    overlap = sp.validate_date_range_plan(_split(oos_start="2025-01-01"))
    assert "windows_overlap_or_misordered" in overlap["errors"]
    tuned = sp.validate_date_range_plan(_split(no_oos_optimization=False))
    assert "oos_optimization_not_explicitly_forbidden" in tuned["errors"]
    assert sp.validate_date_range_plan(None)["acceptable"] is False
    assert ("no_parameter_tuning_or_selection_may_ever_use_the_oos_window"
            in sp.DATE_RANGE_PLAN_RULES)


def test_forbidden_live_api_credential_order_fields_reject():
    for bad in ("order_id", "api_key", "credential_path", "wallet_address",
                "account_balance", "login_token", "fetch_url",
                "live_authorized_flag", "paper_authorized_flag"):
        result = sp.validate_candle_schema(
            list(sp.REQUIRED_CANDLE_FIELDS) + [bad])
        assert result["acceptable"] is False, bad
        assert any(e.startswith("forbidden_field:") for e in result["errors"])


def test_quality_provenance_session_and_storage_plan_content():
    plan = sp.build_real_candle_staging_plan()
    assert plan["session_coverage"]["session_window"] == (
        "09:30-13:00 America/New_York")
    assert plan["session_coverage"]["pre_window_minutes"] >= 60
    assert plan["session_coverage"]["post_window_minutes"] >= 60
    assert "gaps_explicitly_flagged_never_silently_filled" in (
        plan["data_quality_checks"])
    assert "timestamps_monotonic_increasing" in plan["data_quality_checks"]
    assert "no_duplicate_candles_per_symbol_timeframe" in (
        plan["data_quality_checks"])
    assert "1m_and_15m_series_aligned_on_shared_boundaries" in (
        plan["data_quality_checks"])
    assert "source_must_be_human_approved_before_any_staging" in (
        plan["provenance_rules"])
    assert "no_live_market_polling_ever" in plan["provenance_rules"]
    assert set(plan["staging_path_patterns"]) == {"1m", "15m"}
    for pattern in plan["staging_path_patterns"].values():
        assert pattern.startswith("data/ny_fvg_choch/staged/")
    assert plan["plan_stages_no_files"] is True
    assert plan["future_artifacts_require_separate_human_approval"] is True
    assert "only_accepted_detector_labels_can_enter_replay" in (
        plan["replay_eligibility_rules"])
    assert "rejected_labels_remain_auditable" in (
        plan["replay_eligibility_rules"])
    assert "fee_spread_slippage_assumptions_required_before_replay" in (
        plan["replay_eligibility_rules"])
    assert "locked_scorer_review_remains_a_future_separate_approval" in (
        plan["replay_eligibility_rules"])


def test_plan_cannot_fetch_create_run_or_unlock():
    plan = sp.build_real_candle_staging_plan()
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
    assert plan["plan_fetches_nothing"] is True
    tampered = sp.build_real_candle_staging_plan()
    tampered["fetches_data"] = True
    assert sp.validate_real_candle_staging_plan(tampered)["valid"] is False
    tampered2 = sp.build_real_candle_staging_plan()
    tampered2["live_gate_locked"] = False
    assert sp.validate_real_candle_staging_plan(tampered2)["valid"] is False
    tampered3 = sp.build_real_candle_staging_plan()
    tampered3["forbidden"] = tampered3["forbidden"][:3]
    assert sp.validate_real_candle_staging_plan(tampered3)["valid"] is False
    tampered4 = sp.build_real_candle_staging_plan()
    tampered4["required_symbols"] = ["BTCUSD"]
    assert sp.validate_real_candle_staging_plan(tampered4)["valid"] is False


def test_forbidden_list_complete():
    for item in ("data_fetch_in_this_block", "network_calls",
                 "broker_or_exchange_api_calls", "credential_access",
                 "wallet_account_login_fields", "order_placement",
                 "paper_live_micro_live_authorization", "optimizer_execution",
                 "overnight_loop", "auto_promotion", "gate_unlocks",
                 "report_artifact_creation_in_this_block"):
        assert item in sp.FORBIDDEN, item


def test_plan_is_deterministic():
    assert (sp.build_real_candle_staging_plan()
            == sp.build_real_candle_staging_plan())


def test_upstream_stack_and_pm_lane_untouched():
    import sparta_commander.ny_session_fvg_choch_dry_run_replay_results_review_contract as rv
    assert rv.build_dry_run_replay_results_review()["verdict"] == (
        rv.VERDICT_ACCEPTED)
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
    assert sp.get_real_candle_staging_plan_label() == sp.SP_LABEL
    assert "READ-ONLY" in sp.SP_LABEL and sp.SP_MODE == "RESEARCH_ONLY"
    assert sp.NEXT_REQUIRED_ACTION == "HUMAN_APPROVED_CANDLE_SOURCE_FOR_STAGING"
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in sp.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(sp.__file__, encoding="utf-8").read()
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
