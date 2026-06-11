"""Tests for the SPARTA NY FVG+CHOCH Expanded Sample Re-Detection Review.

Proves the review certifies the 619-label / 7-accepted expanded run only
when the edited candidate was active without drift, controls fully account
for every zone, prior outputs are byte-identical, and replay remains gated
on separate human approval even though replay_ready is True.
"""

from __future__ import annotations

import ast
import os.path

import pytest

import sparta_commander.ny_session_fvg_choch_expanded_sample_redetection_review_contract as ex
from sparta_commander.ny_session_fvg_choch_detector_spec import (
    LABEL_REQUIRED_FIELDS,
)

_ACCEPTED = (
    ("BTCUSD", "2026-06-09", "BTCUSD_20260609_editv1exp_setup05_touch1"),
    ("ETHUSD", "2026-05-13", "ETHUSD_20260513_editv1exp_setup01_touch2"),
    ("ETHUSD", "2026-05-15", "ETHUSD_20260515_editv1exp_setup02_touch2"),
    ("SOLUSD", "2026-05-13", "SOLUSD_20260513_editv1exp_setup02_touch1"),
    ("SOLUSD", "2026-05-20", "SOLUSD_20260520_editv1exp_setup02_touch1"),
    ("SOLUSD", "2026-05-26", "SOLUSD_20260526_editv1exp_setup01_touch1"),
    ("AVAXUSD", "2026-05-29", "AVAXUSD_20260529_editv1exp_setup04_touch2"),
)
_REJECT_MIX = (
    ("ARBUSD", {"SETUP_REJECTED_MISSING_CHOCH": 84,
                "SETUP_REJECTED_FIB_MISALIGNMENT": 26,
                "SETUP_REJECTED_MISSING_LTF_FVG": 1}),
    ("AVAXUSD", {"SETUP_REJECTED_MISSING_CHOCH": 69,
                 "SETUP_REJECTED_FIB_MISALIGNMENT": 30,
                 "SETUP_REJECTED_MISSING_LTF_FVG": 1}),
    ("BTCUSD", {"SETUP_REJECTED_MISSING_CHOCH": 53,
                "SETUP_REJECTED_FIB_MISALIGNMENT": 53,
                "SETUP_REJECTED_MISSING_HTF_FVG": 1,
                "SETUP_REJECTED_MISSING_LTF_FVG": 3}),
    ("ETHUSD", {"SETUP_REJECTED_MISSING_CHOCH": 63,
                "SETUP_REJECTED_FIB_MISALIGNMENT": 34,
                "SETUP_REJECTED_MISSING_LTF_FVG": 3}),
    ("SOLUSD", {"SETUP_REJECTED_MISSING_CHOCH": 58,
                "SETUP_REJECTED_FIB_MISALIGNMENT": 39,
                "SETUP_REJECTED_MISSING_LTF_FVG": 1}),
    ("XRPUSD", {"SETUP_REJECTED_MISSING_CHOCH": 61,
                "SETUP_REJECTED_FIB_MISALIGNMENT": 29,
                "SETUP_REJECTED_MISSING_LTF_FVG": 3}),
)


def _label(symbol, status, n, session_date, setup_id=None):
    label = {name: None for name in LABEL_REQUIRED_FIELDS}
    label.update({
        "setup_id": setup_id or "%s_%s_editv1exp_r%03d" % (
            symbol, session_date.replace("-", ""), n),
        "candidate_id": "NY_SESSION_FVG_CHOCH_STRATEGY_CANDIDATE_V1",
        "symbol": symbol, "session_date": session_date,
        "direction": "long", "session_window": "09:30-13:00",
        "htf_timeframe": "15m", "ltf_timeframe": "1m",
        "rejection_reason": None if setup_id else "condition_failed:synth",
        "detector_status": status,
        "label_authorizes_nothing": True,
    })
    return label


def _labels():
    out, n = [], 0
    for symbol, date, setup_id in _ACCEPTED:
        n += 1
        out.append(_label(symbol, "SETUP_LABEL_ACCEPTED_FOR_REPLAY_REVIEW",
                          n, date, setup_id=setup_id))
    for symbol, mix in _REJECT_MIX:
        for status, count in mix.items():
            for _ in range(count):
                n += 1
                # exactly 20 labels carry the 2026-06-10 session date
                date = "2026-06-10" if (symbol == "ARBUSD"
                                        and status
                                        == "SETUP_REJECTED_MISSING_CHOCH"
                                        and n <= 27) else "2026-05-14"
                out.append(_label(symbol, status, n, date))
    return out


def _summary(**overrides):
    summary = {
        "edit_id": "NY_SESSION_FVG_CHOCH_MUTABLE_CANDIDATE_EDIT_V1",
        "edited_candidate_parameters_active": {
            "max_fvg_age_bars": 24,
            "require_fresh_unmitigated_15m_fvg": True,
            "max_zone_touches_before_invalidation": 2},
        "session_dates": ["2026-05-12", "2026-05-13", "2026-05-14",
                          "2026-05-15", "2026-05-18", "2026-05-19",
                          "2026-05-20", "2026-05-21", "2026-05-22",
                          "2026-05-25", "2026-05-26", "2026-05-27",
                          "2026-05-28", "2026-05-29", "2026-06-01",
                          "2026-06-02", "2026-06-03", "2026-06-04",
                          "2026-06-05", "2026-06-09", "2026-06-10"],
        "stale_fvg_controls": dict(ex.EXPECTED_CONTROLS),
        "comparison": dict(ex.EXPECTED_COMPARISON),
        "no_pnl_no_scoring_no_replay": True,
        "labels_authorize_nothing": True,
        "replay_ready": True,
        "replay_requires_separate_human_approval": True,
    }
    summary.update(overrides)
    return summary


def _observation(**overrides):
    observation = {
        "labels_present": True, "summary_present": True,
        "labels": overrides.pop("labels", None) or _labels(),
        "summary": overrides.pop("summary", None) or _summary(),
        "labels_sha256": ex.EXPECTED_LABELS_SHA256,
        "tracked_output_paths": [],
        "baseline_files_sha256": dict(ex.BASELINE_PROTECTED_FILES),
    }
    observation.update(overrides)
    return observation


def test_synthetic_fixture_distribution_is_consistent():
    labels = _labels()
    assert len(labels) == 619
    accepted = [x for x in labels if x["detector_status"]
                == "SETUP_LABEL_ACCEPTED_FOR_REPLAY_REVIEW"]
    assert len(accepted) == 7
    assert sum(1 for x in labels
               if x["session_date"] == "2026-06-10") == 20


def test_valid_expanded_run_accepts_with_replay_ready_true():
    review = ex.certify_expanded_redetection(_observation())
    assert review["verdict"] == ex.VERDICT_EX_ACCEPTED
    assert review["blockers"] == []
    assert review["labels_total"] == 619
    assert review["accepted_total"] == 7
    assert review["replay_ready"] is True
    assert review["replay_authorized"] is False
    assert all(review["checklist_results"][n] is True
               for n in ex.REVIEW_CHECKLIST)
    assert len(ex.REVIEW_CHECKLIST) == 14
    assert ex.validate_expanded_redetection_review(review)["valid"] is True


def test_real_expanded_outputs_review_when_present():
    if not os.path.isfile("C:/SPARTA_BRAIN/" + ex.LABELS_PATH):
        pytest.skip("real expanded outputs absent on this machine")
    review = ex.build_expanded_redetection_review("C:/SPARTA_BRAIN",
                                                  tracked_paths=[])
    assert review["verdict"] == ex.VERDICT_EX_ACCEPTED
    assert review["labels_total"] == 619 and review["accepted_total"] == 7
    assert review["replay_ready"] is True
    assert ex.validate_expanded_redetection_review(review)["valid"] is True


def test_missing_files_block():
    assert ex.certify_expanded_redetection(
        _observation(labels_present=False))["verdict"] == (
        ex.VERDICT_EX_BLOCKED)
    assert ex.certify_expanded_redetection(
        _observation(summary_present=False))["verdict"] == (
        ex.VERDICT_EX_BLOCKED)
    assert ex.certify_expanded_redetection(None)["verdict"] == (
        ex.VERDICT_EX_BLOCKED)


def test_candidate_drift_rejects():
    wrong_params = ex.certify_expanded_redetection(_observation(
        summary=_summary(edited_candidate_parameters_active={
            "max_fvg_age_bars": 48})))
    assert wrong_params["verdict"] == ex.VERDICT_EX_REJECTED
    assert ("check_failed:edited_candidate_v1_active_no_drift"
            in wrong_params["blockers"])
    wrong_edit = ex.certify_expanded_redetection(_observation(
        summary=_summary(edit_id="EDIT_V2")))
    assert ("check_failed:edited_candidate_v1_active_no_drift"
            in wrong_edit["blockers"])


def test_controls_must_fully_account_for_zones():
    bad = ex.certify_expanded_redetection(_observation(
        summary=_summary(stale_fvg_controls={
            "zones_with_session_touch": 5573,
            "zones_filtered_stale_age": 0,
            "zones_filtered_mitigated": 0,
            "zones_eligible_fresh": 5573,
            "touches_capped_beyond_limit": 0})))
    assert bad["verdict"] == ex.VERDICT_EX_REJECTED
    controls = ex.EXPECTED_CONTROLS
    assert (controls["zones_filtered_stale_age"]
            + controls["zones_filtered_mitigated"]
            + controls["zones_eligible_fresh"]
            == controls["zones_with_session_touch"] == 5573)
    assert controls["zones_eligible_fresh"] == 377 >= 100


def test_totals_and_accepted_ids_must_match_exactly():
    labels = _labels()
    labels[0]["detector_status"] = "SETUP_REJECTED_AMBIGUOUS"
    review = ex.certify_expanded_redetection(_observation(labels=labels))
    assert review["verdict"] == ex.VERDICT_EX_REJECTED
    swapped = _labels()
    swapped[0]["setup_id"] = "BTCUSD_20260609_editv1exp_setup99_touch9"
    review2 = ex.certify_expanded_redetection(_observation(labels=swapped))
    assert ("check_failed:accepted_setup_ids_match_exactly"
            in review2["blockers"])
    short = ex.certify_expanded_redetection(
        _observation(labels=_labels()[:-1]))
    assert ("check_failed:totals_match_observed_run_619_and_7_accepted"
            in short["blockers"])


def test_2026_06_10_must_reproduce_edit_v1_result():
    labels = _labels()
    for x in labels:
        if x["session_date"] == "2026-06-10":
            x["session_date"] = "2026-05-22"
            break
    review = ex.certify_expanded_redetection(_observation(labels=labels))
    assert review["verdict"] == ex.VERDICT_EX_REJECTED
    assert ("check_failed:session_day_2026_06_10_reproduced_edit_v1_result"
            in review["blockers"])


def test_comparison_across_three_runs_required():
    bad = ex.certify_expanded_redetection(_observation(
        summary=_summary(comparison={"oops": True})))
    assert ("check_failed:comparison_across_all_three_runs_recorded"
            in bad["blockers"])
    assert ex.EXPECTED_COMPARISON["first_run_2026_06_10"]["labels"] == 259
    assert ex.EXPECTED_COMPARISON["edit_v1_run_2026_06_10"]["labels"] == 20
    assert ex.EXPECTED_COMPARISON["expanded_21_sessions"]["accepted"] == 7


def test_no_replay_pnl_or_scoring_fields():
    labels = _labels()
    labels[10]["net_pnl"] = 4.0
    review = ex.certify_expanded_redetection(_observation(labels=labels))
    assert review["verdict"] == ex.VERDICT_EX_REJECTED
    assert ("check_failed:no_replay_pnl_or_scoring_fields"
            in review["blockers"])
    bad_summary = ex.certify_expanded_redetection(_observation(
        summary=_summary(no_pnl_no_scoring_no_replay=False)))
    assert bad_summary["verdict"] == ex.VERDICT_EX_REJECTED


def test_baseline_mutation_or_sha_mismatch_rejects():
    mutated = dict(ex.BASELINE_PROTECTED_FILES)
    first = next(iter(mutated))
    mutated[first] = "0" * 64
    review = ex.certify_expanded_redetection(_observation(
        baseline_files_sha256=mutated))
    assert review["verdict"] == ex.VERDICT_EX_REJECTED
    assert ("check_failed:baseline_and_prior_outputs_byte_identical"
            in review["blockers"])
    wrong_sha = ex.certify_expanded_redetection(_observation(
        labels_sha256="f" * 64))
    assert "check_failed:labels_file_sha_pinned" in wrong_sha["blockers"]


def test_replay_remains_gated_on_separate_human_approval():
    review = ex.certify_expanded_redetection(_observation())
    assert review["replay_ready"] is True
    assert review["replay_authorized"] is False
    assert review["replay_requires_separate_human_approval"] is True
    assert review["next_required_action"] == (
        "HUMAN_REVIEW_OF_EXPANDED_SAMPLE_ACCEPTED_LABELS")
    tampered = ex.certify_expanded_redetection(_observation())
    tampered["replay_authorized"] = True
    assert ex.validate_expanded_redetection_review(tampered)["valid"] is False
    no_gate = ex.certify_expanded_redetection(_observation(
        summary=_summary(replay_requires_separate_human_approval=False)))
    assert no_gate["verdict"] == ex.VERDICT_EX_REJECTED
    # a non-accepted run can never claim replay_ready
    rejected = ex.certify_expanded_redetection(_observation(
        labels_sha256="f" * 64))
    assert rejected["replay_ready"] is False
    rejected["replay_ready"] = True
    assert ex.validate_expanded_redetection_review(rejected)["valid"] is False


def test_capabilities_false_gates_locked_and_validator_strict():
    review = ex.certify_expanded_redetection(_observation())
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
    tampered = ex.certify_expanded_redetection(_observation())
    tampered["runs_replay_now"] = True
    assert ex.validate_expanded_redetection_review(tampered)["valid"] is False
    tampered2 = ex.certify_expanded_redetection(_observation())
    tampered2["forbidden"] = tampered2["forbidden"][:3]
    assert ex.validate_expanded_redetection_review(tampered2)["valid"] is False
    tampered3 = ex.certify_expanded_redetection(_observation())
    tampered3["accepted_setup_ids"] = ["fake_setup"]
    assert ex.validate_expanded_redetection_review(tampered3)["valid"] is False
    for item in ("replay_runs", "pnl_calculation", "scoring_fields",
                 "optimizer_runs", "rule_changes",
                 "candidate_asset_changes",
                 "locked_scorer_or_instruction_changes",
                 "modifying_staged_candles", "modifying_prior_labels",
                 "deleting_prior_outputs",
                 "broker_exchange_credential_access", "order_endpoints",
                 "paper_live_micro_live_authorization", "gate_unlocks"):
        assert item in ex.FORBIDDEN, item


def test_review_is_deterministic():
    assert (ex.certify_expanded_redetection(_observation())
            == ex.certify_expanded_redetection(_observation()))


def test_upstream_stack_and_pm_lane_untouched():
    import sparta_commander.ny_session_fvg_choch_additional_session_days_staged_candles_review as ad
    assert ad.build_additional_session_days_review()["verdict"] == (
        "NY_FVG_CHOCH_ADDITIONAL_SESSION_DAYS_REVIEW_READY")
    import sparta_commander.ny_session_fvg_choch_redetection_with_edited_candidate_v1 as rd
    assert rd.EXPECTED_NEW_TOTAL == 20 and rd.EXPECTED_NEW_ACCEPTED == 0
    import sparta_commander.ny_session_fvg_choch_mutable_candidate_edit_v1 as me
    assert me.NEW_PARAMETERS["max_fvg_age_bars"] == 24
    from sparta_commander.ny_session_fvg_choch_strategy_spec_contract import (
        DETERMINISTIC_RULES, FIB_LEVEL, FIB_TOLERANCE, RISK_REWARD_TARGET)
    assert FIB_LEVEL == 0.618 and FIB_TOLERANCE == 0.05
    assert RISK_REWARD_TARGET == 4.0
    assert "trigger_1m_bullish_choch" in DETERMINISTIC_RULES
    from sparta_commander.crypto_d1_auto_research_strategy_optimizer_contract import (
        build_optimizer_contract)
    assert build_optimizer_contract()["verdict"] == (
        "CRYPTO_D1_AUTO_RESEARCH_OPTIMIZER_CONTRACT_READY")
    from sparta_commander.strategy_factory_mission_flow_status import (
        LATEST_COMPLETED_PM_LANE_CHAIN)
    assert "Research Only" in LATEST_COMPLETED_PM_LANE_CHAIN


def test_label_action_read_only_and_imports_clean():
    assert ex.get_expanded_sample_review_label() == ex.EX_LABEL
    assert "READ-ONLY" in ex.EX_LABEL and ex.EX_MODE == "RESEARCH_ONLY"
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in ex.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(ex.__file__, encoding="utf-8").read()
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