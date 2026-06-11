"""Tests for the SPARTA NY FVG+CHOCH Additional Session Days Staged Candles
Review.

Proves the sample-expansion contract enforces append-only staging, byte
identity of all prior outputs, the same approved source/schema, a minimum
session-day count, and that detection/replay/PnL/scoring/live capability
stay impossible without further human approvals.
"""

from __future__ import annotations

import ast
import datetime as dt
import os.path

import sparta_commander.ny_session_fvg_choch_additional_session_days_staged_candles_review as ad


def _dates(count, start="2026-06-11"):
    first = dt.date.fromisoformat(start)
    return [(first + dt.timedelta(days=i)).isoformat()
            for i in range(count)]


def _proposal(**overrides):
    proposal = {
        "session_dates": _dates(12),
        "symbols": ("BTCUSD", "ETHUSD", "SOLUSD", "AVAXUSD", "ARBUSD",
                    "XRPUSD"),
        "timeframes": ("1m", "15m"),
        "source_category": "no_auth_public_historical_endpoint_human_approved",
        "output_fields": ("timestamp", "open", "high", "low", "close",
                          "volume", "source", "timeframe", "symbol"),
        "session_coverage": {"session_window":
                             "09:30-13:00 America/New_York",
                             "pre_window_minutes": 120,
                             "post_window_minutes": 240},
        "uses_same_approved_fetch_pattern": True,
        "append_only": True,
        "mutates_prior_staged_files": False,
        "mutates_prior_labels": False,
        "deletes_prior_outputs": False,
        "runs_detector_automatically": False,
        "runs_replay": False,
        "changes_detector_rules": False,
        "changes_candidate_asset": False,
    }
    proposal.update(overrides)
    return proposal


def test_contract_ready_and_gated_on_edit_v1():
    record = ad.build_additional_session_days_review()
    assert record["verdict"] == ad.VERDICT_AD_READY
    assert record["blockers"] == []
    assert record["candidate_id"] == (
        "NY_SESSION_FVG_CHOCH_STRATEGY_CANDIDATE_V1")
    assert ad.validate_additional_session_days_review(record)["valid"] is True
    assert record["min_additional_session_days"] == 10
    assert record["recommended_additional_session_days"] == 20
    assert record["target_eligible_fresh_zones_before_judging"] == 100


def test_valid_expansion_proposal_passes():
    result = ad.validate_additional_staging_proposal(_proposal())
    assert result["approvable"] is True and result["errors"] == []
    assert result["human_run_approval_still_required"] is True
    twenty = ad.validate_additional_staging_proposal(
        _proposal(session_dates=_dates(20)))
    assert twenty["approvable"] is True


def test_too_few_session_days_rejects():
    result = ad.validate_additional_staging_proposal(
        _proposal(session_dates=_dates(9)))
    assert result["approvable"] is False
    assert "too_few_session_days_minimum_10" in result["errors"]
    empty = ad.validate_additional_staging_proposal(
        _proposal(session_dates=[]))
    assert "session_dates_missing_or_empty" in empty["errors"]


def test_duplicate_or_invalid_session_dates_reject():
    dup_existing = ad.validate_additional_staging_proposal(
        _proposal(session_dates=_dates(11) + ["2026-06-10"]))
    assert ("duplicates_already_staged_session_day:2026-06-10"
            in dup_existing["errors"])
    dup_internal = ad.validate_additional_staging_proposal(
        _proposal(session_dates=_dates(11) + ["2026-06-11"]))
    assert "duplicate_session_dates_in_proposal" in dup_internal["errors"]
    bad_format = ad.validate_additional_staging_proposal(
        _proposal(session_dates=_dates(11) + ["June 25"]))
    assert "invalid_session_date:June 25" in bad_format["errors"]


def test_source_schema_timeframe_requirements_enforced():
    wrong_symbols = ad.validate_additional_staging_proposal(
        _proposal(symbols=("BTCUSD",)))
    assert "symbols_mismatch_with_staging_plan" in wrong_symbols["errors"]
    wrong_tf = ad.validate_additional_staging_proposal(
        _proposal(timeframes=("1m", "4h")))
    assert "timeframes_mismatch_with_staging_plan" in wrong_tf["errors"]
    wrong_source = ad.validate_additional_staging_proposal(
        _proposal(source_category="authenticated_api"))
    assert "source_category_not_approved" in wrong_source["errors"]
    wrong_schema = ad.validate_additional_staging_proposal(
        _proposal(output_fields=("timestamp", "open", "close")))
    assert "schema_incompatible_with_staging_plan" in wrong_schema["errors"]
    wrong_coverage = ad.validate_additional_staging_proposal(
        _proposal(session_coverage=None))
    assert "session_coverage_missing_or_wrong" in wrong_coverage["errors"]
    assert ad.validate_additional_staging_proposal(None)["approvable"] is False


def test_append_only_and_no_mutation_flags_enforced():
    for flag, bad_value in (("append_only", False),
                            ("uses_same_approved_fetch_pattern", False),
                            ("mutates_prior_staged_files", True),
                            ("mutates_prior_labels", True),
                            ("deletes_prior_outputs", True),
                            ("runs_detector_automatically", True),
                            ("runs_replay", True),
                            ("changes_detector_rules", True),
                            ("changes_candidate_asset", True)):
        result = ad.validate_additional_staging_proposal(
            _proposal(**{flag: bad_value}))
        assert result["approvable"] is False, flag
        assert "rule_flag_wrong:" + flag in result["errors"], flag
    for rule in ("existing_staged_csvs_and_manifest_are_never_rewritten_or"
                 "_deleted",
                 "each_new_staging_batch_writes_new_files_plus_its_own_new"
                 "_manifest_file",
                 "prior_label_files_and_summaries_are_never_modified_or"
                 "_deleted",
                 "new_session_dates_must_not_duplicate_already_staged_dates",
                 "exclusive_create_only_no_overwrites",
                 "manifest_sha_tracking_every_batch_records_filename_sha256"
                 "_row_count"):
        assert rule in ad.APPEND_ONLY_RULES, rule


def test_existing_staged_candles_remain_byte_identical():
    # pure: byte-identity verification logic
    perfect = dict(ad.BASELINE_PROTECTED_FILES)
    check = ad.verify_append_only_integrity(perfect)
    assert check["intact"] is True and check["errors"] == []
    mutated = dict(ad.BASELINE_PROTECTED_FILES)
    first = next(iter(mutated))
    mutated[first] = "0" * 64
    check2 = ad.verify_append_only_integrity(mutated)
    assert check2["intact"] is False
    assert any(e.startswith("protected_file_mutated:")
               for e in check2["errors"])
    deleted = dict(ad.BASELINE_PROTECTED_FILES)
    deleted[first] = None
    check3 = ad.verify_append_only_integrity(deleted)
    assert any(e.startswith("protected_file_missing_or_deleted:")
               for e in check3["errors"])
    # live: the real baseline on this machine is intact (skip if absent)
    if os.path.isfile("C:/SPARTA_BRAIN/data/ny_fvg_choch/staged/"
                      "manifest.txt"):
        observed = ad.observe_baseline_integrity("C:/SPARTA_BRAIN")
        live = ad.verify_append_only_integrity(observed)
        assert live["intact"] is True, live["errors"]
    assert len(ad.BASELINE_PROTECTED_FILES) == 5


def test_detector_is_not_run_automatically():
    record = ad.build_additional_session_days_review()
    assert record["runs_detector_now"] is False
    assert ("redetection_after_staging_requires_separate_human_approval"
            in [k for k, v in record.items() if v is True])
    assert "automatic_detector_runs" in ad.FORBIDDEN
    src = open(ad.__file__, encoding="utf-8").read()
    assert "detector_run_once" not in src
    assert "redetection_run_once" not in src
    assert "__main__" not in src


def test_replay_ready_remains_false_until_human_approved_redetection():
    record = ad.build_additional_session_days_review()
    assert record[
        "replay_ready_remains_false_until_accepted_labels_exist"] is True
    tampered = ad.build_additional_session_days_review()
    tampered["replay_ready_remains_false_until_accepted_labels_exist"] = False
    assert ad.validate_additional_session_days_review(tampered)[
        "valid"] is False
    # the pushed redetection review still pins replay_ready False
    import sparta_commander.ny_session_fvg_choch_redetection_with_edited_candidate_v1 as rd
    sample = rd.certify_redetection(None)
    assert sample["replay_ready"] is False


def test_no_pnl_replay_scoring_or_live_capability():
    record = ad.build_additional_session_days_review()
    for key in ("executes", "writes_files", "writes_reports",
                "modifies_labels", "deletes_labels", "modifies_staged_files",
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
    tampered = ad.build_additional_session_days_review()
    tampered["scores_now"] = True
    assert ad.validate_additional_session_days_review(tampered)[
        "valid"] is False
    tampered2 = ad.build_additional_session_days_review()
    tampered2["forbidden"] = tampered2["forbidden"][:4]
    assert ad.validate_additional_session_days_review(tampered2)[
        "valid"] is False
    for item in ("detector_rule_changes", "mutable_candidate_asset_changes",
                 "locked_instructions_or_scorer_changes", "replay_runs",
                 "pnl_calculation", "scoring_fields", "optimizer_runs",
                 "automatic_detector_runs",
                 "mutation_of_prior_staged_candles",
                 "mutation_of_prior_labels", "deletion_of_prior_outputs",
                 "broker_exchange_credential_access", "order_endpoints",
                 "auto_promotion", "paper_live_micro_live_authorization",
                 "gate_unlocks"):
        assert item in ad.FORBIDDEN, item


def test_rules_and_candidate_asset_unchanged():
    record = ad.build_additional_session_days_review()
    assert record["rules_and_candidate_asset_unchanged"] is True
    from sparta_commander.ny_session_fvg_choch_strategy_spec_contract import (
        DETERMINISTIC_RULES, FIB_LEVEL, FIB_TOLERANCE, RISK_REWARD_TARGET)
    assert FIB_LEVEL == 0.618 and FIB_TOLERANCE == 0.05
    assert RISK_REWARD_TARGET == 4.0
    assert "trigger_1m_bullish_choch" in DETERMINISTIC_RULES
    from sparta_commander.ny_session_fvg_choch_mutable_candidate_edit_v1 import (
        NEW_PARAMETERS)
    assert NEW_PARAMETERS == {"max_fvg_age_bars": 24,
                              "require_fresh_unmitigated_15m_fvg": True,
                              "max_zone_touches_before_invalidation": 2}


def test_review_is_deterministic():
    assert (ad.build_additional_session_days_review()
            == ad.build_additional_session_days_review())


def test_upstream_stack_and_pm_lane_untouched():
    import sparta_commander.ny_session_fvg_choch_redetection_with_edited_candidate_v1 as rd
    assert rd.EXPECTED_NEW_TOTAL == 20 and rd.EXPECTED_NEW_ACCEPTED == 0
    import sparta_commander.ny_session_fvg_choch_mutable_candidate_edit_v1 as me
    assert me.build_mutable_candidate_edit_v1()["verdict"] == (
        "NY_FVG_CHOCH_MUTABLE_CANDIDATE_EDIT_V1_READY")
    import sparta_commander.ny_session_fvg_choch_detector_labels_review_contract as dl
    assert dl.EXPECTED_TOTAL_LABELS == 259
    import sparta_commander.ny_session_fvg_choch_real_candle_staged_files_review_contract as sr
    assert sr.VERDICT_SR_ACCEPTED == (
        "REAL_CANDLE_STAGED_FILES_ACCEPTED_FOR_DETECTOR_RUN")
    import sparta_commander.ny_session_fvg_choch_public_candle_fetch_runner_dry_run as fr
    assert fr.RUNNER_ENABLED_BY_DEFAULT is False
    import sparta_commander.ny_session_fvg_choch_real_candle_file_creation_tool as fc
    assert fc.TOOL_ENABLED_BY_DEFAULT is False
    from sparta_commander.crypto_d1_auto_research_strategy_optimizer_contract import (
        build_optimizer_contract)
    assert build_optimizer_contract()["verdict"] == (
        "CRYPTO_D1_AUTO_RESEARCH_OPTIMIZER_CONTRACT_READY")
    from sparta_commander.strategy_factory_mission_flow_status import (
        LATEST_COMPLETED_PM_LANE_CHAIN)
    assert "Research Only" in LATEST_COMPLETED_PM_LANE_CHAIN


def test_label_action_read_only_and_imports_clean():
    assert ad.get_additional_session_days_review_label() == ad.AD_LABEL
    assert "READ-ONLY" in ad.AD_LABEL and ad.AD_MODE == "RESEARCH_ONLY"
    assert ad.NEXT_REQUIRED_ACTION == (
        "HUMAN_RUN_APPROVAL_FOR_ADDITIONAL_SESSION_DAYS_STAGING")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in ad.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(ad.__file__, encoding="utf-8").read()
    assert "while true" not in src.lower() and "sleep(" not in src.lower()
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch("):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned_mods = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
                   "subprocess", "websockets", "aiohttp", "schedule",
                   "apscheduler", "threading", "asyncio", "time", "telegram",
                   "email", "csv", "pandas", "os", "io", "json", "shutil",
                   "databento", "ssl", "ftplib"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods)
    assert not any(call.func.attr == "open" if isinstance(call.func, ast.Attribute)
                   else getattr(call.func, "id", "") == "open"
                   for call in ast.walk(tree) if isinstance(call, ast.Call))