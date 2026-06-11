"""Tests for the SPARTA NY FVG+CHOCH Detector Labels Review contract.

Failure modes use synthetic observations (pure certification); acceptance is
also checked against the REAL detector outputs when present. Nothing is
modified, deleted, fetched, replayed, or scored.
"""

from __future__ import annotations

import ast
import os.path

import pytest

import sparta_commander.ny_session_fvg_choch_detector_labels_review_contract as dl
from sparta_commander.ny_session_fvg_choch_detector_spec import (
    LABEL_REQUIRED_FIELDS,
)

_DISTRIBUTION = (
    ("BTCUSD", 51, {"SETUP_REJECTED_FIB_MISALIGNMENT": 1}),
    ("ETHUSD", 23, {}),
    ("SOLUSD", 39, {"SETUP_REJECTED_FIB_MISALIGNMENT": 2}),
    ("AVAXUSD", 43, {}),
    ("ARBUSD", 60, {}),
    ("XRPUSD", 39, {"SETUP_REJECTED_MISSING_LTF_FVG": 1}),
)


def _label(symbol, status, n):
    label = {name: None for name in LABEL_REQUIRED_FIELDS}
    label.update({
        "setup_id": "%s_20260610_setup%03d" % (symbol, n),
        "candidate_id": "NY_SESSION_FVG_CHOCH_STRATEGY_CANDIDATE_V1",
        "symbol": symbol, "session_date": "2026-06-10",
        "direction": "long", "session_window": "09:30-13:00",
        "htf_timeframe": "15m", "ltf_timeframe": "1m",
        "rejection_reason": "condition_failed:synthetic",
        "detector_status": status,
        "label_authorizes_nothing": True,
    })
    return label


def _labels():
    out = []
    n = 0
    for symbol, choch_count, extras in _DISTRIBUTION:
        for _ in range(choch_count):
            n += 1
            out.append(_label(symbol, "SETUP_REJECTED_MISSING_CHOCH", n))
        for status, count in extras.items():
            for _ in range(count):
                n += 1
                out.append(_label(symbol, status, n))
    return out


def _observation(**overrides):
    labels = overrides.pop("labels", None) or _labels()
    observation = {
        "labels_present": True, "summary_present": True,
        "labels": labels,
        "summary": {"no_pnl_no_scoring_no_replay": True,
                    "labels_authorize_nothing": True,
                    "labels_total": len(labels),
                    "accepted_total": sum(
                        1 for x in labels if x["detector_status"]
                        == "SETUP_LABEL_ACCEPTED_FOR_REPLAY_REVIEW")},
        "tracked_label_paths": [],
        "staged_review_verdict":
            "REAL_CANDLE_STAGED_FILES_ACCEPTED_FOR_DETECTOR_RUN",
        "staged_manifest_sha256": dl.EXPECTED_STAGED_MANIFEST_SHA256,
    }
    observation.update(overrides)
    return observation


def test_valid_synthetic_label_set_reviews_successfully():
    review = dl.certify_detector_labels(_observation())
    assert review["verdict"] == dl.VERDICT_DL_EDIT_RECOMMENDED
    assert review["blockers"] == []
    assert review["labels_total"] == 259
    assert review["accepted_total"] == 0
    assert review["replay_ready"] is False
    assert all(review["checklist_results"][n] is True
               for n in dl.REVIEW_CHECKLIST)
    assert len(dl.REVIEW_CHECKLIST) == 12
    assert dl.validate_detector_labels_review(review)["valid"] is True


def test_real_detector_outputs_review_when_present():
    if not os.path.isfile("C:/SPARTA_BRAIN/" + dl.LABELS_PATH):
        pytest.skip("real detector outputs absent on this machine")
    review = dl.build_detector_labels_review("C:/SPARTA_BRAIN",
                                             tracked_paths=[])
    assert review["verdict"] == dl.VERDICT_DL_EDIT_RECOMMENDED
    assert review["labels_total"] == 259 and review["accepted_total"] == 0
    assert dl.validate_detector_labels_review(review)["valid"] is True


def test_missing_labels_or_summary_blocks():
    review = dl.certify_detector_labels(_observation(labels_present=False))
    assert review["verdict"] == dl.VERDICT_DL_BLOCKED
    assert "labels_or_summary_file_missing" in review["blockers"]
    review2 = dl.certify_detector_labels(_observation(summary_present=False))
    assert review2["verdict"] == dl.VERDICT_DL_BLOCKED
    assert dl.certify_detector_labels(None)["verdict"] == (
        dl.VERDICT_DL_BLOCKED)


def test_schema_mismatch_rejects():
    labels = _labels()
    del labels[0]["htf_fvg_bounds"]
    review = dl.certify_detector_labels(_observation(labels=labels))
    assert review["verdict"] == dl.VERDICT_DL_REJECTED
    assert ("check_failed:every_label_has_29_field_schema_plus_authorizes"
            "_nothing" in review["blockers"])
    labels2 = _labels()
    labels2[0]["label_authorizes_nothing"] = False
    review2 = dl.certify_detector_labels(_observation(labels=labels2))
    assert review2["verdict"] == dl.VERDICT_DL_REJECTED


def test_unknown_detector_status_rejects():
    labels = _labels()
    labels[0]["detector_status"] = "SETUP_TOTALLY_NEW_STATUS"
    review = dl.certify_detector_labels(_observation(labels=labels))
    assert review["verdict"] == dl.VERDICT_DL_REJECTED
    assert ("check_failed:every_status_in_closed_9_set" in review["blockers"])


def test_accepted_count_mismatch_rejects():
    labels = _labels()
    labels[0]["detector_status"] = "SETUP_LABEL_ACCEPTED_FOR_REPLAY_REVIEW"
    observation = _observation(labels=labels)
    observation["summary"]["accepted_total"] = 1
    review = dl.certify_detector_labels(observation)
    assert review["verdict"] == dl.VERDICT_DL_REJECTED
    assert "check_failed:accepted_labels_zero" in review["blockers"]


def test_rejection_count_mismatch_rejects():
    labels = _labels()
    labels[0]["detector_status"] = "SETUP_REJECTED_AMBIGUOUS"
    review = dl.certify_detector_labels(_observation(labels=labels))
    assert review["verdict"] == dl.VERDICT_DL_REJECTED
    assert ("check_failed:rejection_counts_match_observed_run"
            in review["blockers"])
    short = dl.certify_detector_labels(_observation(labels=_labels()[:-1]))
    assert "check_failed:total_labels_259" in short["blockers"]


def test_pnl_or_profitability_field_rejects():
    labels = _labels()
    labels[0]["net_pnl"] = 5.0
    review = dl.certify_detector_labels(_observation(labels=labels))
    assert review["verdict"] == dl.VERDICT_DL_REJECTED
    assert ("check_failed:no_replay_pnl_or_scoring_fields_in_labels"
            in review["blockers"])
    observation = _observation()
    observation["summary"]["no_pnl_no_scoring_no_replay"] = False
    review2 = dl.certify_detector_labels(observation)
    assert ("check_failed:summary_records_no_pnl_no_scoring_no_replay"
            in review2["blockers"])


def test_replay_scorer_optimizer_fields_reject():
    for bad in ("replay_status", "score_total", "profit_factor",
                "win_rate_claimed"):
        labels = _labels()
        labels[3][bad] = "x"
        review = dl.certify_detector_labels(_observation(labels=labels))
        assert review["verdict"] == dl.VERDICT_DL_REJECTED, bad
        assert ("check_failed:no_replay_pnl_or_scoring_fields_in_labels"
                in review["blockers"]), bad


def test_tracked_detector_outputs_reject():
    review = dl.certify_detector_labels(_observation(
        tracked_label_paths=["data/ny_fvg_choch/detector_labels/x.jsonl"]))
    assert review["verdict"] == dl.VERDICT_DL_REJECTED
    assert ("check_failed:outputs_untracked_not_in_git_index"
            in review["blockers"])


def test_modified_staged_candles_reject():
    review = dl.certify_detector_labels(_observation(
        staged_review_verdict="REAL_CANDLE_STAGED_FILES_REJECTED"))
    assert review["verdict"] == dl.VERDICT_DL_REJECTED
    assert ("check_failed:staged_candles_byte_identical_and_still_accepted"
            in review["blockers"])
    review2 = dl.certify_detector_labels(_observation(
        staged_manifest_sha256="0" * 64))
    assert ("check_failed:staged_candles_byte_identical_and_still_accepted"
            in review2["blockers"])


def test_zero_accepted_labels_prevents_replay_ready():
    review = dl.certify_detector_labels(_observation())
    assert review["replay_ready"] is False
    assert "REPLAY_READY" not in review["verdict"]
    assert ("zero_accepted_labels_means_no_replay_should_run_yet"
            in review["research_interpretation"])
    tampered = dl.certify_detector_labels(_observation())
    tampered["replay_ready"] = True
    assert dl.validate_detector_labels_review(tampered)["valid"] is False


def test_edit_recommendation_allowed_but_changes_no_rules():
    review = dl.certify_detector_labels(_observation())
    assert review["recommended_mutable_candidate_edits"] == [
        "add_max_fvg_age_bars",
        "require_fresh_unmitigated_15m_fvg",
        "tighten_or_revise_htf_context_touch_logic",
        "revise_choch_watch_window",
        "review_fib_0618_tolerance",
        "add_max_zone_touches_before_invalidation"]
    assert review["this_review_changes_no_rules"] is True
    assert review["edit_path_rule"] == dl.EDIT_PATH_RULE
    assert "never_locked_scorer" in dl.EDIT_PATH_RULE
    tampered = dl.certify_detector_labels(_observation())
    tampered["this_review_changes_no_rules"] = False
    assert dl.validate_detector_labels_review(tampered)["valid"] is False
    tampered2 = dl.certify_detector_labels(_observation())
    tampered2["recommended_mutable_candidate_edits"] = ["weaken_everything"]
    assert dl.validate_detector_labels_review(tampered2)["valid"] is False
    # the frozen strategy rules are untouched by this review
    from sparta_commander.ny_session_fvg_choch_strategy_spec_contract import (
        DETERMINISTIC_RULES, FIB_LEVEL, FIB_TOLERANCE)
    assert FIB_LEVEL == 0.618 and FIB_TOLERANCE == 0.05
    assert "htf_15m_bullish_fvg" in DETERMINISTIC_RULES


def test_review_cannot_run_anything_or_unlock():
    review = dl.certify_detector_labels(_observation())
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
        assert review[key] is False, key
    assert review["paper_trading_gate_locked"] is True
    assert review["micro_live_gate_locked"] is True
    assert review["live_gate_locked"] is True
    tampered = dl.certify_detector_labels(_observation())
    tampered["runs_replay_now"] = True
    assert dl.validate_detector_labels_review(tampered)["valid"] is False
    tampered2 = dl.certify_detector_labels(_observation())
    tampered2["forbidden"] = tampered2["forbidden"][:3]
    assert dl.validate_detector_labels_review(tampered2)["valid"] is False
    for item in ("replay_runs", "scorer_runs", "optimizer_runs",
                 "report_artifact_creation", "modifying_labels",
                 "deleting_labels", "modifying_staged_candles",
                 "network_retrieval", "broker_exchange_private_api_access",
                 "credentials_or_api_keys", "account_wallet_login_access",
                 "trading_endpoints_of_any_kind",
                 "paper_live_micro_live_authorization", "gate_unlocks"):
        assert item in dl.FORBIDDEN, item


def test_review_is_deterministic():
    assert (dl.certify_detector_labels(_observation())
            == dl.certify_detector_labels(_observation()))


def test_upstream_stack_and_pm_lane_untouched():
    import sparta_commander.ny_session_fvg_choch_real_candle_staged_files_review_contract as sr
    assert sr.VERDICT_SR_ACCEPTED == (
        "REAL_CANDLE_STAGED_FILES_ACCEPTED_FOR_DETECTOR_RUN")
    import sparta_commander.ny_session_fvg_choch_public_candle_fetch_runner_dry_run as fr
    assert fr.RUNNER_ENABLED_BY_DEFAULT is False
    import sparta_commander.ny_session_fvg_choch_real_candle_file_creation_tool as fc
    assert fc.TOOL_ENABLED_BY_DEFAULT is False
    import sparta_commander.ny_session_fvg_choch_candle_source_approval_contract as sa
    assert sa.build_candle_source_approval_contract()["verdict"] == (
        "NY_FVG_CHOCH_CANDLE_SOURCE_APPROVAL_READY")
    import sparta_commander.ny_session_fvg_choch_real_candle_staging_plan as plan_mod
    assert plan_mod.build_real_candle_staging_plan()["verdict"] == (
        "NY_FVG_CHOCH_REAL_CANDLE_STAGING_PLAN_READY")
    import sparta_commander.ny_session_fvg_choch_dry_run_replay_results_review_contract as rv
    assert rv.build_dry_run_replay_results_review()["verdict"] == (
        "DRY_RUN_REPLAY_RESULTS_ACCEPTED_FOR_REAL_CANDLE_STAGING")
    from sparta_commander.ny_session_fvg_choch_detector_spec import (
        DETECTOR_STATUSES)
    assert len(DETECTOR_STATUSES) == 9
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


def test_label_action_read_only_and_imports_clean():
    assert dl.get_detector_labels_review_label() == dl.DL_LABEL
    assert "READ-ONLY" in dl.DL_LABEL and dl.DL_MODE == "RESEARCH_ONLY"
    assert dl.NEXT_REQUIRED_ACTION == (
        "HUMAN_DECISION_ON_MUTABLE_CANDIDATE_EDIT")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in dl.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(dl.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    assert "while true" not in src.lower() and "sleep(" not in src.lower()
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch("):
        assert verb not in src, verb
    tree = ast.parse(src)
    sparta_imports = {node.module for node in ast.walk(tree)
                      if isinstance(node, ast.ImportFrom) and node.module
                      and node.module.startswith("sparta_commander")}
    for module in sparta_imports:
        for fragment in ("replay_runner", "replay_spec", "optimizer",
                         "fetch"):
            assert fragment not in module, module
    banned_mods = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
                   "subprocess", "websockets", "aiohttp", "schedule",
                   "apscheduler", "threading", "asyncio", "time", "telegram",
                   "email", "csv", "pandas", "os", "io", "shutil",
                   "databento", "ssl", "ftplib", "datetime"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods)
    assert not any(call.func.attr == "open" if isinstance(call.func, ast.Attribute)
                   else getattr(call.func, "id", "") == "open"
                   for call in ast.walk(tree) if isinstance(call, ast.Call))