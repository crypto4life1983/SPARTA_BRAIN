"""Tests for the SPARTA NY FVG+CHOCH Candle Source Approval contract."""

from __future__ import annotations

import ast

import sparta_commander.ny_session_fvg_choch_candle_source_approval_contract as sa


def test_contract_gated_on_ready_staging_plan():
    contract = sa.build_candle_source_approval_contract()
    assert contract["verdict"] == sa.VERDICT_SA_READY
    assert contract["blockers"] == []
    assert contract["candidate_id"] == (
        "NY_SESSION_FVG_CHOCH_STRATEGY_CANDIDATE_V1")
    assert sa.validate_candle_source_approval_contract(contract)["valid"] is True
    import sparta_commander.ny_session_fvg_choch_real_candle_staging_plan as plan_mod
    assert plan_mod.VERDICT_SP_READY == (
        "NY_FVG_CHOCH_REAL_CANDLE_STAGING_PLAN_READY")
    assert plan_mod.build_real_candle_staging_plan()["verdict"] == (
        plan_mod.VERDICT_SP_READY)


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


def test_approved_no_auth_historical_source_passes():
    result = sa.validate_candle_source_proposal(_proposal())
    assert result["approvable"] is True and result["errors"] == []
    assert result["human_signature_still_required"] is True
    for category in sa.ALLOWED_SOURCE_CATEGORIES:
        ok = sa.validate_candle_source_proposal(_proposal(category=category))
        assert ok["approvable"] is True, category


def test_credential_api_key_private_endpoint_sources_reject():
    bad = sa.validate_candle_source_proposal(_proposal(requires_api_key=True))
    assert bad["approvable"] is False
    assert "forbidden_access_requirement:requires_api_key" in bad["errors"]
    bad2 = sa.validate_candle_source_proposal(
        _proposal(requires_credentials=True))
    assert "forbidden_access_requirement:requires_credentials" in bad2["errors"]
    bad3 = sa.validate_candle_source_proposal(_proposal(requires_login=True))
    assert "forbidden_access_requirement:requires_login" in bad3["errors"]
    bad4 = sa.validate_candle_source_proposal(
        _proposal(uses_private_endpoint=True))
    assert "forbidden_access_requirement:uses_private_endpoint" in bad4["errors"]
    leak = sa.validate_candle_source_proposal(_proposal(api_key_env="X"))
    assert leak["approvable"] is False
    assert any(e.startswith("forbidden_proposal_field:") for e in leak["errors"])
    leak2 = sa.validate_candle_source_proposal(_proposal(wallet_address="0x"))
    assert leak2["approvable"] is False


def test_order_trade_endpoint_sources_reject():
    for endpoint in ("/api/v3/order", "/private/trade", "/v5/position/list",
                     "/account/balance", "/wallet/withdraw"):
        bad = sa.validate_candle_source_proposal(
            _proposal(endpoint_path=endpoint))
        assert bad["approvable"] is False, endpoint
        assert any(e.startswith("forbidden_endpoint_token:")
                   for e in bad["errors"]), endpoint
    good = sa.validate_candle_source_proposal(
        _proposal(endpoint_path="/api/v3/klines"))
    assert good["approvable"] is True


def test_live_polling_source_rejects():
    bad = sa.validate_candle_source_proposal(_proposal(is_live_polling=True))
    assert bad["approvable"] is False
    assert "live_polling_forbidden" in bad["errors"]
    bad2 = sa.validate_candle_source_proposal(_proposal(historical_only=False))
    assert "source_not_historical_only" in bad2["errors"]


def test_missing_provenance_rejects():
    bad = sa.validate_candle_source_proposal(_proposal(provenance=""))
    assert bad["approvable"] is False
    assert "provenance_missing" in bad["errors"]
    bad2 = sa.validate_candle_source_proposal(_proposal(terms_and_limits=" "))
    assert "terms_and_limits_missing" in bad2["errors"]
    missing = dict(_proposal())
    del missing["provenance"]
    bad3 = sa.validate_candle_source_proposal(missing)
    assert "missing_proposal_field:provenance" in bad3["errors"]
    assert sa.validate_candle_source_proposal(None)["approvable"] is False


def test_wrong_symbols_or_timeframes_reject():
    bad = sa.validate_candle_source_proposal(_proposal(symbols=("BTCUSD",)))
    assert "symbols_mismatch_with_staging_plan" in bad["errors"]
    bad2 = sa.validate_candle_source_proposal(
        _proposal(timeframes=("1m", "5m")))
    assert "timeframes_mismatch_with_staging_plan" in bad2["errors"]
    bad3 = sa.validate_candle_source_proposal(_proposal(timeframes=()))
    assert "timeframes_mismatch_with_staging_plan" in bad3["errors"]


def test_missing_schema_compatibility_rejects():
    bad = sa.validate_candle_source_proposal(_proposal(
        output_fields=("timestamp", "open", "high", "low", "close")))
    assert bad["approvable"] is False
    assert "schema_incompatible_with_staging_plan" in bad["errors"]
    bad2 = sa.validate_candle_source_proposal(_proposal(
        category="scraping_behind_login"))
    assert any(e.startswith("category_not_allowed:") for e in bad2["errors"])


def test_allowed_categories_and_requirements_frozen():
    assert sa.ALLOWED_SOURCE_CATEGORIES == (
        "repo_local_approved_historical_files",
        "manually_supplied_human_approved_csv",
        "no_auth_public_historical_endpoint_human_approved",
        "approved_read_only_historical_provider_adapter_no_credentials")
    for req in ("no_login_no_api_key_no_secret_no_credential",
                "no_account_no_wallet_access",
                "no_private_endpoint_no_trading_endpoint",
                "no_live_market_polling_historical_only",
                "no_network_call_in_this_block",
                "source_provenance_recorded",
                "symbols_and_timeframes_match_staging_plan",
                "output_satisfies_staging_plan_schema",
                "actual_staging_requires_separate_human_approval"):
        assert req in sa.SOURCE_REQUIREMENTS, req
    for item in ("data_fetch_in_this_block", "file_creation_in_this_block",
                 "api_key_usage", "credential_loading",
                 "wallet_account_login_access", "private_endpoint_access",
                 "trading_endpoints_of_any_kind",
                 "paper_live_micro_live_authorization",
                 "detector_replay_scorer_runs", "optimizer_execution",
                 "report_artifact_creation", "gate_unlocks"):
        assert item in sa.FORBIDDEN, item


def test_approval_cannot_fetch_create_run_or_unlock():
    contract = sa.build_candle_source_approval_contract()
    for key in ("executes", "writes_files", "writes_reports",
                "runs_detector_now", "runs_replay_now", "scores_now",
                "fetches_data", "calls_api", "uses_network",
                "uses_credentials", "uses_wallet", "connects_broker",
                "connects_exchange", "uses_real_money",
                "contains_order_logic", "starts_scheduler",
                "sends_notifications", "authorizes_paper_execution",
                "authorizes_micro_live", "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate"):
        assert contract[key] is False, key
    assert contract["paper_trading_gate_locked"] is True
    assert contract["micro_live_gate_locked"] is True
    assert contract["live_gate_locked"] is True
    assert contract["approves_source_rules_only"] is True
    assert contract["every_concrete_source_needs_human_signature"] is True
    assert contract["actual_staging_requires_separate_human_approval"] is True
    tampered = sa.build_candle_source_approval_contract()
    tampered["fetches_data"] = True
    assert sa.validate_candle_source_approval_contract(tampered)["valid"] is False
    tampered2 = sa.build_candle_source_approval_contract()
    tampered2["live_gate_locked"] = False
    assert sa.validate_candle_source_approval_contract(tampered2)["valid"] is False
    tampered3 = sa.build_candle_source_approval_contract()
    tampered3["forbidden"] = tampered3["forbidden"][:4]
    assert sa.validate_candle_source_approval_contract(tampered3)["valid"] is False
    tampered4 = sa.build_candle_source_approval_contract()
    tampered4["allowed_source_categories"] = (
        tampered4["allowed_source_categories"] + ["authenticated_api"])
    assert sa.validate_candle_source_approval_contract(tampered4)["valid"] is False


def test_contract_is_deterministic():
    assert (sa.build_candle_source_approval_contract()
            == sa.build_candle_source_approval_contract())


def test_upstream_stack_and_pm_lane_untouched():
    import sparta_commander.ny_session_fvg_choch_real_candle_staging_plan as plan_mod
    plan = plan_mod.build_real_candle_staging_plan()
    assert plan["verdict"] == "NY_FVG_CHOCH_REAL_CANDLE_STAGING_PLAN_READY"
    assert plan_mod.validate_real_candle_staging_plan(plan)["valid"] is True
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
    assert sa.get_candle_source_approval_label() == sa.SA_LABEL
    assert "READ-ONLY" in sa.SA_LABEL and sa.SA_MODE == "RESEARCH_ONLY"
    assert sa.NEXT_REQUIRED_ACTION == "HUMAN_APPROVED_REAL_CANDLE_STAGING"
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in sa.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(sa.__file__, encoding="utf-8").read()
    assert "while true" not in src.lower() and "sleep(" not in src.lower()
    tree = ast.parse(src)
    banned_mods = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
                   "subprocess", "websockets", "aiohttp", "schedule",
                   "apscheduler", "threading", "asyncio", "time", "telegram",
                   "email", "csv", "pandas", "pathlib", "os", "io", "json",
                   "shutil", "databento", "datetime"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods)
    assert not any(call.func.attr == "open" if isinstance(call.func, ast.Attribute)
                   else getattr(call.func, "id", "") == "open"
                   for call in ast.walk(tree) if isinstance(call, ast.Call))
