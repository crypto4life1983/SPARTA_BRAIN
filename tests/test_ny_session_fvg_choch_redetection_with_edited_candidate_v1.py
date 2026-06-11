"""Tests for the SPARTA NY FVG+CHOCH Re-Detection With Edited Candidate V1.

Proves the re-detection used the edited candidate with active stale-FVG
controls, preserved candles and prior labels byte-for-byte, added no
replay/PnL/scoring fields, kept all gates locked, and that replay still
requires separate human approval.
"""

from __future__ import annotations

import ast
import os.path

import pytest

import sparta_commander.ny_session_fvg_choch_redetection_with_edited_candidate_v1 as rd
from sparta_commander.ny_session_fvg_choch_detector_spec import (
    LABEL_REQUIRED_FIELDS,
)

_DISTRIBUTION = (
    ("BTCUSD", 0, {"SETUP_REJECTED_FIB_MISALIGNMENT": 2}),
    ("ETHUSD", 2, {}),
    ("SOLUSD", 2, {"SETUP_REJECTED_FIB_MISALIGNMENT": 2}),
    ("AVAXUSD", 4, {}),
    ("ARBUSD", 2, {}),
    ("XRPUSD", 5, {"SETUP_REJECTED_MISSING_LTF_FVG": 1}),
)


def _label(symbol, status, n):
    label = {name: None for name in LABEL_REQUIRED_FIELDS}
    label.update({
        "setup_id": "%s_20260610_editv1_setup%02d" % (symbol, n),
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
    out, n = [], 0
    for symbol, choch_count, extras in _DISTRIBUTION:
        for _ in range(choch_count):
            n += 1
            out.append(_label(symbol, "SETUP_REJECTED_MISSING_CHOCH", n))
        for status, count in extras.items():
            for _ in range(count):
                n += 1
                out.append(_label(symbol, status, n))
    return out


def _summary(**overrides):
    summary = {
        "edit_id": "NY_SESSION_FVG_CHOCH_MUTABLE_CANDIDATE_EDIT_V1",
        "edited_candidate_parameters_active": {
            "max_fvg_age_bars": 24,
            "require_fresh_unmitigated_15m_fvg": True,
            "max_zone_touches_before_invalidation": 2},
        "stale_fvg_controls": {"zones_with_session_touch": 259,
                               "zones_filtered_stale_age": 237,
                               "zones_filtered_mitigated": 11,
                               "zones_eligible_fresh": 11,
                               "touches_capped_beyond_limit": 52},
        "comparison_to_previous_run": {
            "previous_labels_total": 259, "previous_accepted_total": 0,
            "new_labels_total": 20, "new_accepted_total": 0,
            "junk_label_reduction": 239},
        "no_pnl_no_scoring_no_replay": True,
        "labels_authorize_nothing": True,
        "staged_manifest_sha256": rd.EXPECTED_MANIFEST_SHA256,
        "prior_labels_sha256_after_run": rd.EXPECTED_PRIOR_LABELS_SHA256,
        "replay_ready": False,
        "replay_requires_separate_human_approval": True,
    }
    summary.update(overrides)
    return summary


def _observation(**overrides):
    observation = {
        "labels_present": True, "summary_present": True,
        "labels": overrides.pop("labels", None) or _labels(),
        "summary": overrides.pop("summary", None) or _summary(),
        "tracked_output_paths": [],
        "staged_manifest_sha256": rd.EXPECTED_MANIFEST_SHA256,
        "prior_labels_sha256": rd.EXPECTED_PRIOR_LABELS_SHA256,
    }
    observation.update(overrides)
    return observation


def test_valid_synthetic_redetection_accepts():
    review = rd.certify_redetection(_observation())
    assert review["verdict"] == rd.VERDICT_RD_ACCEPTED
    assert review["blockers"] == []
    assert review["labels_total"] == 20
    assert review["accepted_total"] == 0
    assert review["replay_ready"] is False
    assert all(review["checklist_results"][n] is True
               for n in rd.REVIEW_CHECKLIST)
    assert len(rd.REVIEW_CHECKLIST) == 12
    assert rd.validate_redetection_review(review)["valid"] is True


def test_real_redetection_outputs_review_when_present():
    if not os.path.isfile("C:/SPARTA_BRAIN/" + rd.NEW_LABELS_PATH):
        pytest.skip("real re-detection outputs absent on this machine")
    review = rd.build_redetection_review("C:/SPARTA_BRAIN",
                                         tracked_paths=[])
    assert review["verdict"] == rd.VERDICT_RD_ACCEPTED
    assert review["labels_total"] == 20 and review["accepted_total"] == 0
    assert rd.validate_redetection_review(review)["valid"] is True


def test_edited_candidate_asset_is_used():
    review = rd.certify_redetection(_observation())
    assert review["checklist_results"]["edited_candidate_asset_used"] is True
    assert review["edit_id"] == "NY_SESSION_FVG_CHOCH_MUTABLE_CANDIDATE_EDIT_V1"
    wrong_edit = rd.certify_redetection(_observation(
        summary=_summary(edit_id="SOME_OTHER_EDIT")))
    assert wrong_edit["verdict"] == rd.VERDICT_RD_REJECTED
    assert "check_failed:edited_candidate_asset_used" in wrong_edit["blockers"]
    wrong_params = rd.certify_redetection(_observation(
        summary=_summary(edited_candidate_parameters_active={
            "max_fvg_age_bars": 9999})))
    assert "check_failed:edited_candidate_asset_used" in (
        wrong_params["blockers"])


def test_stale_fvg_controls_active_and_accounted():
    review = rd.certify_redetection(_observation())
    assert review["checklist_results"][
        "stale_fvg_controls_active_and_accounted"] is True
    # the three buckets must exactly account for every touched zone
    controls = rd.EXPECTED_CONTROLS
    assert (controls["zones_filtered_stale_age"]
            + controls["zones_filtered_mitigated"]
            + controls["zones_eligible_fresh"]
            == controls["zones_with_session_touch"] == 259)
    broken = rd.certify_redetection(_observation(
        summary=_summary(stale_fvg_controls={
            "zones_with_session_touch": 259,
            "zones_filtered_stale_age": 0,
            "zones_filtered_mitigated": 0,
            "zones_eligible_fresh": 259,
            "touches_capped_beyond_limit": 0})))
    assert broken["verdict"] == rd.VERDICT_RD_REJECTED


def test_comparison_259_to_20_recorded():
    review = rd.certify_redetection(_observation())
    assert review["checklist_results"][
        "comparison_to_previous_run_recorded"] is True
    assert rd.EXPECTED_JUNK_REDUCTION == 239
    bad = rd.certify_redetection(_observation(summary=_summary(
        comparison_to_previous_run={"previous_labels_total": 100,
                                    "previous_accepted_total": 0,
                                    "new_labels_total": 20,
                                    "new_accepted_total": 0,
                                    "junk_label_reduction": 80})))
    assert "check_failed:comparison_to_previous_run_recorded" in (
        bad["blockers"])


def test_missing_files_block_and_count_mismatches_reject():
    assert rd.certify_redetection(_observation(labels_present=False))[
        "verdict"] == rd.VERDICT_RD_BLOCKED
    assert rd.certify_redetection(_observation(summary_present=False))[
        "verdict"] == rd.VERDICT_RD_BLOCKED
    assert rd.certify_redetection(None)["verdict"] == rd.VERDICT_RD_BLOCKED
    short = rd.certify_redetection(_observation(labels=_labels()[:-1]))
    assert "check_failed:new_totals_match_observed_run" in short["blockers"]
    flipped = _labels()
    flipped[0]["detector_status"] = "SETUP_LABEL_ACCEPTED_FOR_REPLAY_REVIEW"
    review = rd.certify_redetection(_observation(labels=flipped))
    assert review["verdict"] == rd.VERDICT_RD_REJECTED
    broken_schema = _labels()
    del broken_schema[0]["htf_fvg_bounds"]
    review2 = rd.certify_redetection(_observation(labels=broken_schema))
    assert ("check_failed:every_label_has_29_field_schema_plus_authorizes"
            "_nothing" in review2["blockers"])


def test_same_staged_candle_manifest_sha_is_preserved():
    review = rd.certify_redetection(_observation())
    assert review["checklist_results"][
        "staged_manifest_sha_preserved"] is True
    changed = rd.certify_redetection(_observation(
        staged_manifest_sha256="0" * 64))
    assert changed["verdict"] == rd.VERDICT_RD_REJECTED
    assert ("check_failed:staged_manifest_sha_preserved"
            in changed["blockers"])


def test_prior_labels_are_preserved():
    review = rd.certify_redetection(_observation())
    assert review["checklist_results"]["prior_labels_sha_preserved"] is True
    assert review["previous_labels_kept_on_record"] is True
    changed = rd.certify_redetection(_observation(
        prior_labels_sha256="f" * 64))
    assert changed["verdict"] == rd.VERDICT_RD_REJECTED
    assert "check_failed:prior_labels_sha_preserved" in changed["blockers"]


def test_no_replay_pnl_or_scoring_fields_appear():
    labels = _labels()
    labels[0]["net_pnl"] = 1.0
    review = rd.certify_redetection(_observation(labels=labels))
    assert review["verdict"] == rd.VERDICT_RD_REJECTED
    assert ("check_failed:no_replay_pnl_or_scoring_fields"
            in review["blockers"])
    labels2 = _labels()
    labels2[1]["replay_status"] = "x"
    review2 = rd.certify_redetection(_observation(labels=labels2))
    assert ("check_failed:no_replay_pnl_or_scoring_fields"
            in review2["blockers"])
    bad_summary = rd.certify_redetection(_observation(
        summary=_summary(no_pnl_no_scoring_no_replay=False)))
    assert bad_summary["verdict"] == rd.VERDICT_RD_REJECTED


def test_no_live_or_paper_trading_capability():
    review = rd.certify_redetection(_observation())
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
    tampered = rd.certify_redetection(_observation())
    tampered["authorizes_live_trading"] = True
    assert rd.validate_redetection_review(tampered)["valid"] is False
    tampered2 = rd.certify_redetection(_observation())
    tampered2["forbidden"] = tampered2["forbidden"][:3]
    assert rd.validate_redetection_review(tampered2)["valid"] is False


def test_human_approval_remains_required_before_any_replay():
    review = rd.certify_redetection(_observation())
    assert review["replay_ready"] is False
    assert review["replay_requires_separate_human_approval"] is True
    assert review["next_required_action"] == (
        "HUMAN_DECISION_ON_NEXT_RESEARCH_STEP")
    tampered = rd.certify_redetection(_observation())
    tampered["replay_ready"] = True
    assert rd.validate_redetection_review(tampered)["valid"] is False
    tampered2 = rd.certify_redetection(_observation())
    tampered2["replay_requires_separate_human_approval"] = False
    assert rd.validate_redetection_review(tampered2)["valid"] is False
    no_flag = rd.certify_redetection(_observation(
        summary=_summary(replay_requires_separate_human_approval=False)))
    assert no_flag["verdict"] == rd.VERDICT_RD_REJECTED


def test_tracked_outputs_reject_and_review_deterministic():
    tracked = rd.certify_redetection(_observation(
        tracked_output_paths=["data/ny_fvg_choch/detector_labels/x.jsonl"]))
    assert tracked["verdict"] == rd.VERDICT_RD_REJECTED
    assert (rd.certify_redetection(_observation())
            == rd.certify_redetection(_observation()))


def test_upstream_stack_and_pm_lane_untouched():
    import sparta_commander.ny_session_fvg_choch_mutable_candidate_edit_v1 as me
    record = me.build_mutable_candidate_edit_v1()
    assert record["verdict"] == "NY_FVG_CHOCH_MUTABLE_CANDIDATE_EDIT_V1_READY"
    import sparta_commander.ny_session_fvg_choch_detector_labels_review_contract as dl
    assert dl.NEXT_REQUIRED_ACTION == (
        "HUMAN_DECISION_ON_MUTABLE_CANDIDATE_EDIT")
    import sparta_commander.ny_session_fvg_choch_real_candle_staged_files_review_contract as sr
    assert sr.VERDICT_SR_ACCEPTED == (
        "REAL_CANDLE_STAGED_FILES_ACCEPTED_FOR_DETECTOR_RUN")
    from sparta_commander.ny_session_fvg_choch_detector_spec import (
        DETECTOR_STATUSES)
    assert len(DETECTOR_STATUSES) == 9
    from sparta_commander.ny_session_fvg_choch_strategy_spec_contract import (
        DETERMINISTIC_RULES, FIB_LEVEL)
    assert FIB_LEVEL == 0.618
    assert "htf_15m_bullish_fvg" in DETERMINISTIC_RULES
    from sparta_commander.crypto_d1_auto_research_strategy_optimizer_contract import (
        build_optimizer_contract)
    assert build_optimizer_contract()["verdict"] == (
        "CRYPTO_D1_AUTO_RESEARCH_OPTIMIZER_CONTRACT_READY")
    from sparta_commander.strategy_factory_mission_flow_status import (
        LATEST_COMPLETED_PM_LANE_CHAIN)
    assert "Research Only" in LATEST_COMPLETED_PM_LANE_CHAIN


def test_label_action_read_only_and_imports_clean():
    assert rd.get_redetection_review_label() == rd.RD_LABEL
    assert "READ-ONLY" in rd.RD_LABEL and rd.RD_MODE == "RESEARCH_ONLY"
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in rd.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(rd.__file__, encoding="utf-8").read()
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