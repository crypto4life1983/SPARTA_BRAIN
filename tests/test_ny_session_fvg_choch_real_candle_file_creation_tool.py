"""Tests for the SPARTA NY FVG+CHOCH Real-Candle File Creation Tool.

The tool is built but NEVER run here: no test supplies the human run-approval
token together with a ready plan, so nothing is ever written.
"""

from __future__ import annotations

import ast
import os.path

import sparta_commander.ny_session_fvg_choch_real_candle_file_creation_tool as fc


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


def _no_staging_dir():
    assert not os.path.isdir("data/ny_fvg_choch")
    assert not os.path.isdir("C:/SPARTA_BRAIN/data/ny_fvg_choch")


def test_tool_is_built_disabled_and_not_run():
    assert fc.TOOL_ENABLED_BY_DEFAULT is False
    plan = fc.build_file_creation_plan(_proposal(), [_payload()])
    assert plan["plan_status"] == (
        "FILE_CREATION_PLAN_READY_FOR_HUMAN_RUN_APPROVAL")
    assert plan["tool_enabled_by_default"] is False
    assert plan["run_requires_exact_human_token"] is True
    assert plan["writes_files"] is False and plan["executes"] is False
    assert fc.validate_file_creation_plan(plan)["valid"] is True
    _no_staging_dir()


def test_plan_is_gated_on_pushed_staging_dry_run_verdict():
    import sparta_commander.ny_session_fvg_choch_real_candle_staging_dry_run as sd
    record = sd.run_real_candle_staging_dry_run(_proposal(), _payload())
    assert record["staging_status"] == (
        "STAGING_DRY_RUN_READY_FOR_HUMAN_FILE_APPROVAL")
    bad = fc.build_file_creation_plan(
        _proposal(category="repo_local_approved_historical_files"),
        [_payload()])
    assert bad["plan_status"] == (
        "FILE_CREATION_PLAN_REJECTED_SOURCE_NOT_APPROVED")
    assert bad["planned_files"] == []


def test_plan_contents_paths_and_checksums():
    fifteen = ["2026-06-10T13:%02d:00Z" % m for m in (30, 45)] + [
        "2026-06-10T14:00:00Z"]
    plan = fc.build_file_creation_plan(_proposal(), [
        _payload(),
        _payload(symbol="ETHUSD",
                 rows=[_row(_T[i], symbol="ETHUSD") for i in range(3)]),
        _payload(timeframe="15m",
                 rows=[_row(ts, timeframe="15m") for ts in fifteen]),
    ])
    assert plan["plan_status"] == (
        "FILE_CREATION_PLAN_READY_FOR_HUMAN_RUN_APPROVAL")
    assert len(plan["planned_files"]) == 3
    paths = [e["target_path"] for e in plan["planned_files"]]
    assert paths[0] == ("data/ny_fvg_choch/staged/"
                        "BTCUSD_1m_2026-06-10_2026-06-10.csv")
    assert paths[1].startswith("data/ny_fvg_choch/staged/ETHUSD_1m_")
    assert paths[2].startswith("data/ny_fvg_choch/staged/BTCUSD_15m_")
    for entry in plan["planned_files"]:
        assert entry["row_count"] == 3
        assert len(entry["sha256"]) == 64
        assert entry["content"].splitlines()[0] == (
            "timestamp,open,high,low,close,volume,source,timeframe,symbol")
    assert plan["manifest_plan"] == {
        "manifest_path": "data/ny_fvg_choch/staged/manifest.txt",
        "checksum_algorithm": "sha256",
        "line_format": "filename,sha256,row_count"}
    assert plan["staged_files_are_untracked_operational_data"] is True
    _no_staging_dir()


def test_wrong_symbols_and_timeframes_reject():
    plan = fc.build_file_creation_plan(_proposal(),
                                       [_payload(symbol="DOGEUSD")])
    assert plan["plan_status"] == (
        "FILE_CREATION_PLAN_REJECTED_PAYLOAD_INVALID")
    plan2 = fc.build_file_creation_plan(_proposal(),
                                        [_payload(timeframe="4h")])
    assert plan2["plan_status"] == (
        "FILE_CREATION_PLAN_REJECTED_PAYLOAD_INVALID")
    assert plan2["planned_files"] == []


def test_missing_fields_and_bad_payloads_reject():
    bad_row = _row(_T[1])
    del bad_row["volume"]
    plan = fc.build_file_creation_plan(
        _proposal(), [_payload(rows=[_row(_T[0]), bad_row])])
    assert plan["plan_status"] == (
        "FILE_CREATION_PLAN_REJECTED_PAYLOAD_INVALID")
    assert any("missing_fields:volume" in e for e in plan["errors"])
    assert fc.build_file_creation_plan(_proposal(), [])["plan_status"] == (
        "FILE_CREATION_PLAN_REJECTED_PAYLOAD_INVALID")
    assert fc.build_file_creation_plan(_proposal(), None)["plan_status"] == (
        "FILE_CREATION_PLAN_REJECTED_PAYLOAD_INVALID")


def test_bad_timestamps_and_duplicates_reject():
    plan = fc.build_file_creation_plan(
        _proposal(), [_payload(rows=[_row(_T[1]), _row(_T[0])])])
    assert any("timestamps_not_monotonic" in e for e in plan["errors"])
    plan2 = fc.build_file_creation_plan(
        _proposal(), [_payload(rows=[_row(_T[0]), _row(_T[0])])])
    assert any("duplicate_candle" in e for e in plan2["errors"])
    same_target = fc.build_file_creation_plan(
        _proposal(), [_payload(), _payload()])
    assert any("duplicate_target_file" in e for e in same_target["errors"])


def test_bad_ohlcv_rejects():
    plan = fc.build_file_creation_plan(
        _proposal(), [_payload(rows=[_row(_T[0], volume=-1.0)])])
    assert any("negative_value:volume" in e for e in plan["errors"])
    plan2 = fc.build_file_creation_plan(
        _proposal(), [_payload(rows=[_row(_T[0], high=98.0)])])
    assert any("ohlc_inconsistent" in e for e in plan2["errors"])


def test_missing_source_rejects():
    plan = fc.build_file_creation_plan(
        _proposal(), [_payload(rows=[_row(_T[0], source="")])])
    assert plan["plan_status"] == (
        "FILE_CREATION_PLAN_REJECTED_PAYLOAD_INVALID")
    assert any("source_missing" in e for e in plan["errors"])


def test_unflagged_gaps_reject():
    gapped = [_row(_T[0]), _row(_T[1]), _row("2026-06-10T13:40:00Z")]
    plan = fc.build_file_creation_plan(_proposal(), [_payload(rows=gapped)])
    assert any("unflagged_gap_after" in e for e in plan["errors"])
    flagged = _payload(rows=gapped, flagged_gaps=[
        {"from_timestamp": _T[1], "to_timestamp": "2026-06-10T13:40:00Z"}])
    plan2 = fc.build_file_creation_plan(_proposal(), [flagged])
    assert plan2["plan_status"] == (
        "FILE_CREATION_PLAN_READY_FOR_HUMAN_RUN_APPROVAL")


def test_forbidden_credential_api_order_fields_reject():
    for bad in ("order_id", "api_key_env", "wallet_address",
                "account_balance", "login_token", "fetch_url"):
        plan = fc.build_file_creation_plan(_proposal(),
                                           [_payload(**{bad: "x"})])
        assert plan["plan_status"] == (
            "FILE_CREATION_PLAN_REJECTED_FORBIDDEN_CAPABILITY"), bad
    src_bad = fc.build_file_creation_plan(
        _proposal(requires_api_key=True), [_payload()])
    assert src_bad["plan_status"] == (
        "FILE_CREATION_PLAN_REJECTED_SOURCE_NOT_APPROVED")


def test_writer_refuses_without_exact_human_token():
    plan = fc.build_file_creation_plan(_proposal(), [_payload()])
    for token in (None, "", "yes", "approved",
                  fc.RUN_APPROVAL_TOKEN.lower()):
        result = fc.execute_file_creation(plan, token, "C:/SPARTA_BRAIN")
        assert result["run_status"] == "FILE_CREATION_REFUSED_NOT_APPROVED"
        assert result["files_written"] == []
        assert result["manifest_written"] is None
    _no_staging_dir()


def test_writer_refuses_invalid_or_tampered_plan_even_with_token():
    rejected = fc.build_file_creation_plan(_proposal(),
                                           [_payload(symbol="DOGEUSD")])
    result = fc.execute_file_creation(rejected, fc.RUN_APPROVAL_TOKEN,
                                      "C:/SPARTA_BRAIN")
    assert result["run_status"] == "FILE_CREATION_REFUSED_PLAN_INVALID"
    assert result["files_written"] == []
    tampered = fc.build_file_creation_plan(_proposal(), [_payload()])
    tampered["planned_files"][0]["target_path"] = "sparta_commander/evil.csv"
    result2 = fc.execute_file_creation(tampered, fc.RUN_APPROVAL_TOKEN,
                                       "C:/SPARTA_BRAIN")
    assert result2["run_status"] == "FILE_CREATION_REFUSED_PLAN_INVALID"
    assert result2["files_written"] == []
    tampered2 = fc.build_file_creation_plan(_proposal(), [_payload()])
    tampered2["live_gate_locked"] = False
    result3 = fc.execute_file_creation(tampered2, fc.RUN_APPROVAL_TOKEN,
                                       "C:/SPARTA_BRAIN")
    assert result3["run_status"] == "FILE_CREATION_REFUSED_PLAN_INVALID"
    assert result3["files_written"] == []
    _no_staging_dir()


def test_plan_cannot_run_fetch_or_unlock_and_validator_strict():
    plan = fc.build_file_creation_plan(_proposal(), [_payload()])
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
    tampered = fc.build_file_creation_plan(_proposal(), [_payload()])
    tampered["tool_enabled_by_default"] = True
    assert fc.validate_file_creation_plan(tampered)["valid"] is False
    tampered2 = fc.build_file_creation_plan(_proposal(), [_payload()])
    tampered2["fetches_data"] = True
    assert fc.validate_file_creation_plan(tampered2)["valid"] is False
    tampered3 = fc.build_file_creation_plan(_proposal(), [_payload()])
    tampered3["staging_root"] = "data/elsewhere"
    assert fc.validate_file_creation_plan(tampered3)["valid"] is False
    for item in ("running_during_build_or_tests", "hidden_auto_run",
                 "while_true_loops", "scheduler_or_cron_behavior",
                 "optimizer_execution", "detector_replay_scorer_execution",
                 "broker_exchange_private_api_access",
                 "credentials_or_api_keys", "account_wallet_login_access",
                 "trading_endpoints_of_any_kind",
                 "paper_live_micro_live_authorization", "gate_unlocks",
                 "report_artifact_creation_in_this_block"):
        assert item in fc.FORBIDDEN, item


def test_plan_is_deterministic_and_no_files_created():
    a = fc.build_file_creation_plan(_proposal(), [_payload()])
    b = fc.build_file_creation_plan(_proposal(), [_payload()])
    assert a == b
    _no_staging_dir()


def test_upstream_stack_and_pm_lane_untouched():
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


def test_label_action_no_auto_run_and_imports_clean():
    assert fc.get_real_candle_file_creation_tool_label() == fc.FC_LABEL
    assert "READ-ONLY" in fc.FC_LABEL and fc.FC_MODE == "RESEARCH_ONLY"
    assert fc.NEXT_REQUIRED_ACTION == (
        "HUMAN_RUN_APPROVAL_FOR_REAL_CANDLE_FILE_CREATION")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in fc.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(fc.__file__, encoding="utf-8").read()
    assert "__main__" not in src  # no hidden auto-run entry point
    assert "while true" not in src.lower() and "sleep(" not in src.lower()
    tree = ast.parse(src)
    banned_mods = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
                   "subprocess", "websockets", "aiohttp", "schedule",
                   "apscheduler", "threading", "asyncio", "time", "telegram",
                   "email", "csv", "pandas", "json", "shutil", "databento",
                   "ssl", "ftplib"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods)
    # the ONLY open() calls live inside execute_file_creation (the gated
    # writer); no other function may touch the filesystem
    open_calls_outside_writer = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for call in ast.walk(node):
                if (isinstance(call, ast.Call)
                        and getattr(call.func, "id", "") == "open"
                        and node.name != "execute_file_creation"):
                    open_calls_outside_writer.append(node.name)
    assert open_calls_outside_writer == []
    _no_staging_dir()