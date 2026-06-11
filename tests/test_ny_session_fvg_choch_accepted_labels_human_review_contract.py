"""Tests for the SPARTA NY FVG+CHOCH Accepted Labels Human Review contract.

Proves the review freezes EXACTLY the 7 first-ever accepted setups (ids,
symbols, dates), validates their schema and provenance, confirms ARB/XRP
produced none, keeps every prior output byte-identical, and keeps replay
gated on a separate human approval even though replay_ready is True.
"""

from __future__ import annotations

import ast
import os.path

import pytest

import sparta_commander.ny_session_fvg_choch_accepted_labels_human_review_contract as al
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


def _accepted_label(symbol, date, setup_id):
    label = {name: None for name in LABEL_REQUIRED_FIELDS}
    label.update({
        "setup_id": setup_id,
        "candidate_id": "NY_SESSION_FVG_CHOCH_STRATEGY_CANDIDATE_V1",
        "symbol": symbol, "session_date": date, "direction": "long",
        "session_window": "09:30-13:00",
        "htf_timeframe": "15m", "ltf_timeframe": "1m",
        "htf_fvg_bounds": [100.0, 101.0], "htf_fvg_midpoint": 100.5,
        "htf_fvg_type": "bullish_fvg",
        "proposed_entry_price": 100.4, "proposed_stop_price": 100.1,
        "proposed_target_4r_price": 101.6,
        "fib_alignment_pass": True,
        "detector_status": "SETUP_LABEL_ACCEPTED_FOR_REPLAY_REVIEW",
        "label_authorizes_nothing": True,
    })
    return label


def _accepted():
    return [_accepted_label(*row) for row in _ACCEPTED]


def _summary(**overrides):
    summary = {
        "edit_id": "NY_SESSION_FVG_CHOCH_MUTABLE_CANDIDATE_EDIT_V1",
        "edited_candidate_parameters_active": {
            "max_fvg_age_bars": 24,
            "require_fresh_unmitigated_15m_fvg": True,
            "max_zone_touches_before_invalidation": 2},
        "replay_ready": True,
        "replay_requires_separate_human_approval": True,
    }
    summary.update(overrides)
    return summary


def _observation(**overrides):
    observation = {
        "labels_present": True, "summary_present": True,
        "accepted_labels": overrides.pop("accepted_labels", None)
        or _accepted(),
        "summary": overrides.pop("summary", None) or _summary(),
        "labels_sha256": al.EXPECTED_LABELS_SHA256,
        "expanded_review_verdict":
            "EXPANDED_REDETECTION_ACCEPTED_AWAITING_HUMAN_REPLAY_DECISION",
        "tracked_output_paths": [],
        "baseline_files_sha256": dict(al.BASELINE_PROTECTED_FILES),
        "batch2_manifest_sha256": al.BATCH2_MANIFEST_SHA256,
    }
    observation.update(overrides)
    return observation


def test_valid_accepted_set_approves_for_replay_decision():
    review = al.certify_accepted_labels(_observation())
    assert review["verdict"] == al.VERDICT_AL_APPROVED
    assert review["blockers"] == []
    assert review["accepted_total"] == 7
    assert review["replay_ready"] is True
    assert review["replay_authorized"] is False
    assert all(review["checklist_results"][n] is True
               for n in al.REVIEW_CHECKLIST)
    assert len(al.REVIEW_CHECKLIST) == 12
    assert al.validate_accepted_labels_human_review(review)["valid"] is True


def test_real_accepted_labels_review_when_present():
    if not os.path.isfile("C:/SPARTA_BRAIN/" + al.LABELS_PATH):
        pytest.skip("real expanded outputs absent on this machine")
    review = al.build_accepted_labels_human_review("C:/SPARTA_BRAIN",
                                                   tracked_paths=[])
    assert review["verdict"] == al.VERDICT_AL_APPROVED
    assert review["accepted_total"] == 7
    assert al.validate_accepted_labels_human_review(review)["valid"] is True


def test_frozen_setup_ids_and_symbol_date_map():
    assert al.FROZEN_ACCEPTED_SETUP_IDS == tuple(sorted(
        row[2] for row in _ACCEPTED))
    assert al.FROZEN_ACCEPTED_BY_SYMBOL_DATES == {
        "SOLUSD": ("2026-05-13", "2026-05-20", "2026-05-26"),
        "ETHUSD": ("2026-05-13", "2026-05-15"),
        "BTCUSD": ("2026-06-09",),
        "AVAXUSD": ("2026-05-29",)}
    assert al.ZERO_ACCEPTED_SYMBOLS == ("ARBUSD", "XRPUSD")


def test_missing_inputs_block():
    assert al.certify_accepted_labels(_observation(labels_present=False))[
        "verdict"] == al.VERDICT_AL_BLOCKED
    assert al.certify_accepted_labels(_observation(summary_present=False))[
        "verdict"] == al.VERDICT_AL_BLOCKED
    assert al.certify_accepted_labels(None)["verdict"] == (
        al.VERDICT_AL_BLOCKED)


def test_uniqueness_and_exact_count_enforced():
    labels = _accepted()
    labels[1]["setup_id"] = labels[0]["setup_id"]  # duplicate id
    review = al.certify_accepted_labels(_observation(accepted_labels=labels))
    assert review["verdict"] == al.VERDICT_AL_REJECTED
    assert "check_failed:exactly_7_accepted_and_unique" in review["blockers"]
    six = al.certify_accepted_labels(
        _observation(accepted_labels=_accepted()[:6]))
    assert "check_failed:exactly_7_accepted_and_unique" in six["blockers"]
    eight = al.certify_accepted_labels(_observation(
        accepted_labels=_accepted() + [_accepted_label(
            "SOLUSD", "2026-05-27", "SOLUSD_20260527_editv1exp_extra")]))
    assert eight["verdict"] == al.VERDICT_AL_REJECTED


def test_setup_id_drift_rejects():
    labels = _accepted()
    labels[0]["setup_id"] = "BTCUSD_20260609_editv1exp_setup99_touch9"
    review = al.certify_accepted_labels(_observation(accepted_labels=labels))
    assert review["verdict"] == al.VERDICT_AL_REJECTED
    assert "check_failed:setup_ids_exactly_frozen" in review["blockers"]


def test_symbol_date_map_and_sample_membership_enforced():
    labels = _accepted()
    labels[0]["session_date"] = "2026-05-12"  # wrong date for BTC accepted
    review = al.certify_accepted_labels(_observation(accepted_labels=labels))
    assert ("check_failed:symbols_and_dates_match_frozen_map"
            in review["blockers"])
    labels2 = _accepted()
    labels2[0]["session_date"] = "2026-07-01"  # outside staged sample
    review2 = al.certify_accepted_labels(
        _observation(accepted_labels=labels2))
    assert ("check_failed:dates_inside_approved_staged_sample"
            in review2["blockers"])
    labels3 = _accepted()
    labels3[0]["symbol"] = "XRPUSD"  # zero-accepted symbol claims a label
    review3 = al.certify_accepted_labels(
        _observation(accepted_labels=labels3))
    assert ("check_failed:zero_accepted_symbols_confirmed"
            in review3["blockers"])


def test_schema_and_forbidden_field_screens():
    labels = _accepted()
    del labels[0]["htf_fvg_bounds"]
    review = al.certify_accepted_labels(_observation(accepted_labels=labels))
    assert ("check_failed:accepted_labels_have_29_field_schema_and"
            "_authorize_nothing" in review["blockers"])
    for bad in ("net_pnl", "profit_factor", "score_total", "win_rate",
                "replay_status", "fill_price", "order_id", "broker_account",
                "credential_path"):
        labels2 = _accepted()
        labels2[2][bad] = "x"
        review2 = al.certify_accepted_labels(
            _observation(accepted_labels=labels2))
        assert review2["verdict"] == al.VERDICT_AL_REJECTED, bad
        assert ("check_failed:no_forbidden_fields_in_accepted_labels"
                in review2["blockers"]), bad


def test_rule_drift_rejects():
    drifted = al.certify_accepted_labels(_observation(
        summary=_summary(edited_candidate_parameters_active={
            "max_fvg_age_bars": 48})))
    assert drifted["verdict"] == al.VERDICT_AL_REJECTED
    assert ("check_failed:frozen_rules_consistent_no_drift"
            in drifted["blockers"])
    assert al.FROZEN_RULES_ECHO["fib_level"] == 0.618
    assert al.FROZEN_RULES_ECHO["fib_tolerance"] == 0.05
    assert al.FROZEN_RULES_ECHO["risk_reward_target"] == 4.0
    assert al.FROZEN_RULES_ECHO["fvg_freshness_controls"] == {
        "max_fvg_age_bars": 24,
        "require_fresh_unmitigated_15m_fvg": True,
        "max_zone_touches_before_invalidation": 2}


def test_mutated_prior_outputs_or_wrong_expanded_verdict_reject():
    mutated = dict(al.BASELINE_PROTECTED_FILES)
    mutated[next(iter(mutated))] = "0" * 64
    review = al.certify_accepted_labels(_observation(
        baseline_files_sha256=mutated))
    assert ("check_failed:prior_outputs_and_candles_not_mutated"
            in review["blockers"])
    review2 = al.certify_accepted_labels(_observation(
        batch2_manifest_sha256="0" * 64))
    assert ("check_failed:prior_outputs_and_candles_not_mutated"
            in review2["blockers"])
    review3 = al.certify_accepted_labels(_observation(
        expanded_review_verdict="EXPANDED_REDETECTION_REJECTED"))
    assert ("check_failed:expanded_review_certified_accepted"
            in review3["blockers"])
    review4 = al.certify_accepted_labels(_observation(
        labels_sha256="f" * 64))
    assert ("check_failed:expanded_review_certified_accepted"
            in review4["blockers"])
    review5 = al.certify_accepted_labels(_observation(
        tracked_output_paths=["data/ny_fvg_choch/detector_labels/x"]))
    assert ("check_failed:prior_outputs_and_candles_not_mutated"
            in review5["blockers"])


def test_replay_gated_and_scope_locked_to_7_labels():
    review = al.certify_accepted_labels(_observation())
    assert review["replay_ready"] is True
    assert review["replay_authorized"] is False
    assert review["replay_scope_is_exactly_these_7_labels_only"] is True
    assert review["next_required_action"] == (
        "HUMAN_APPROVED_FEE_HONEST_REPLAY_OF_7_ACCEPTED_LABELS_ONLY")
    tampered = al.certify_accepted_labels(_observation())
    tampered["replay_authorized"] = True
    assert al.validate_accepted_labels_human_review(tampered)[
        "valid"] is False
    tampered2 = al.certify_accepted_labels(_observation())
    tampered2["replay_scope_is_exactly_these_7_labels_only"] = False
    assert al.validate_accepted_labels_human_review(tampered2)[
        "valid"] is False
    no_gate = al.certify_accepted_labels(_observation(
        summary=_summary(replay_requires_separate_human_approval=False)))
    assert no_gate["verdict"] == al.VERDICT_AL_REJECTED
    rejected = al.certify_accepted_labels(_observation(
        labels_sha256="f" * 64))
    assert rejected["replay_ready"] is False
    rejected["replay_ready"] = True
    assert al.validate_accepted_labels_human_review(rejected)[
        "valid"] is False


def test_capabilities_false_gates_locked_and_validator_strict():
    review = al.certify_accepted_labels(_observation())
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
    tampered = al.certify_accepted_labels(_observation())
    tampered["frozen_accepted_setup_ids"] = ["fake"]
    assert al.validate_accepted_labels_human_review(tampered)[
        "valid"] is False
    tampered2 = al.certify_accepted_labels(_observation())
    tampered2["forbidden"] = tampered2["forbidden"][:3]
    assert al.validate_accepted_labels_human_review(tampered2)[
        "valid"] is False
    for item in ("replay_runs", "pnl_calculation", "profitability_scoring",
                 "optimizer_runs", "rule_changes",
                 "candidate_asset_changes",
                 "modifying_labels_candles_or_summaries",
                 "broker_exchange_credential_access", "order_endpoints",
                 "paper_live_micro_live_authorization", "gate_unlocks"):
        assert item in al.FORBIDDEN, item


def test_review_is_deterministic():
    assert (al.certify_accepted_labels(_observation())
            == al.certify_accepted_labels(_observation()))


def test_upstream_stack_and_pm_lane_untouched():
    import sparta_commander.ny_session_fvg_choch_expanded_sample_redetection_review_contract as ex
    assert ex.EXPECTED_ACCEPTED == 7 and ex.EXPECTED_TOTAL_LABELS == 619
    import sparta_commander.ny_session_fvg_choch_mutable_candidate_edit_v1 as me
    assert me.build_mutable_candidate_edit_v1()["verdict"] == (
        "NY_FVG_CHOCH_MUTABLE_CANDIDATE_EDIT_V1_READY")
    import sparta_commander.ny_session_fvg_choch_additional_session_days_staged_candles_review as ad
    assert len(ad.BASELINE_PROTECTED_FILES) == 5
    from sparta_commander.ny_session_fvg_choch_replay_runner_dry_run import (
        get_replay_runner_dry_run_label)
    assert "Replay Runner" in get_replay_runner_dry_run_label()
    from sparta_commander.crypto_d1_auto_research_strategy_optimizer_contract import (
        build_optimizer_contract)
    assert build_optimizer_contract()["verdict"] == (
        "CRYPTO_D1_AUTO_RESEARCH_OPTIMIZER_CONTRACT_READY")
    from sparta_commander.strategy_factory_mission_flow_status import (
        LATEST_COMPLETED_PM_LANE_CHAIN)
    assert "Research Only" in LATEST_COMPLETED_PM_LANE_CHAIN


def test_label_action_read_only_and_imports_clean():
    assert al.get_accepted_labels_human_review_label() == al.AL_LABEL
    assert "READ-ONLY" in al.AL_LABEL and al.AL_MODE == "RESEARCH_ONLY"
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in al.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(al.__file__, encoding="utf-8").read()
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
        for fragment in ("replay_runner", "replay_spec", "optimizer"):
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