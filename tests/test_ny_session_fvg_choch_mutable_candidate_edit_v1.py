"""Tests for the SPARTA NY FVG+CHOCH Mutable Candidate Edit V1.

Proves the edit touches ONLY the mutable candidate asset: locked scorer,
locked instructions, detector schema, replay logic, candles, and previous
labels are unchanged; nothing runs automatically; human approval still gates
any new detection pass.
"""

from __future__ import annotations

import ast
import hashlib
import os.path

import sparta_commander.ny_session_fvg_choch_mutable_candidate_edit_v1 as me
from sparta_commander.ny_session_fvg_choch_strategy_spec_contract import (
    build_candidate_asset_instance,
)


def test_edit_v1_is_ready_and_asset_accepted():
    record = me.build_mutable_candidate_edit_v1()
    assert record["verdict"] == me.VERDICT_ME_READY
    assert record["blockers"] == []
    assert record["edited_asset_verdict"] == (
        "CANDIDATE_ASSET_ACCEPTED_FOR_RESEARCH")
    assert record["candidate_id"] == (
        "NY_SESSION_FVG_CHOCH_STRATEGY_CANDIDATE_V1")
    assert me.validate_mutable_candidate_edit_v1(record)["valid"] is True


def test_exactly_three_approved_parameters_added():
    assert me.NEW_PARAMETERS == {
        "max_fvg_age_bars": 24,
        "require_fresh_unmitigated_15m_fvg": True,
        "max_zone_touches_before_invalidation": 2}
    edited = me.build_edited_candidate_asset()
    parameters = edited["fields"]["parameters"]
    for key, value in me.NEW_PARAMETERS.items():
        assert parameters[key] == value, key
    assert me.APPLIED_EDITS == ("add_max_fvg_age_bars",
                                "require_fresh_unmitigated_15m_fvg",
                                "add_max_zone_touches_before_invalidation")


def test_edits_drawn_only_from_review_recommendations():
    from sparta_commander.ny_session_fvg_choch_detector_labels_review_contract import (
        RECOMMENDED_MUTABLE_CANDIDATE_EDITS)
    recommended = set(RECOMMENDED_MUTABLE_CANDIDATE_EDITS)
    assert set(me.APPLIED_EDITS) <= recommended


def test_only_mutable_candidate_rules_changed():
    base = build_candidate_asset_instance()
    edited = me.build_edited_candidate_asset()
    # base builder output is NOT mutated by the edit
    assert "max_fvg_age_bars" not in base["fields"]["parameters"]
    assert "require_fresh_unmitigated_15m_fvg" not in (
        base["fields"]["parameters"])
    # outer research flags identical
    for key in ("research_only", "live_trading_authorized",
                "paper_trading_authorized", "human_review_required",
                "optimizer_may_edit", "locked_instructions_may_edit",
                "locked_scorer_may_edit"):
        assert edited[key] == base[key], key
    # only the expected editable fields differ
    changed = {name for name in base["fields"]
               if edited["fields"][name] != base["fields"][name]}
    assert changed == {"parameters", "constraints", "lineage", "status",
                       "audit_notes", "rationale"}
    # base parameters are preserved inside the edited parameters
    for key, value in base["fields"]["parameters"].items():
        assert edited["fields"]["parameters"][key] == value, key
    assert edited["fields"]["status"] == "proposed"
    assert edited["fields"]["candidate_id"] == base["fields"]["candidate_id"]


def test_locked_scorer_and_instructions_unchanged():
    from sparta_commander.crypto_d1_auto_research_strategy_optimizer_contract import (
        FORBIDDEN_FOREVER, LOCKED_HUMAN_INSTRUCTIONS, LOCKED_SCORING_RULES,
        build_optimizer_contract)
    assert len(LOCKED_HUMAN_INSTRUCTIONS) == 7
    assert len(LOCKED_SCORING_RULES) == 9
    assert len(FORBIDDEN_FOREVER) == 12
    assert build_optimizer_contract()["verdict"] == (
        "CRYPTO_D1_AUTO_RESEARCH_OPTIMIZER_CONTRACT_READY")
    record = me.build_mutable_candidate_edit_v1()
    assert record["modifies_locked_scorer"] is False
    assert record["modifies_locked_instructions"] is False
    edited = me.build_edited_candidate_asset()
    assert edited["locked_scorer_may_edit"] is False
    assert edited["locked_instructions_may_edit"] is False
    assert "locked_scorer_unchanged" in record["unchanged_guarantees"]
    assert "locked_instructions_unchanged" in record["unchanged_guarantees"]


def test_detector_label_schema_unchanged():
    from sparta_commander.ny_session_fvg_choch_detector_spec import (
        DETECTOR_STATUSES, LABEL_REQUIRED_FIELDS)
    assert len(LABEL_REQUIRED_FIELDS) == 29
    assert len(DETECTOR_STATUSES) == 9
    record = me.build_mutable_candidate_edit_v1()
    assert record["modifies_detector_label_schema"] is False
    assert ("detector_label_schema_unchanged_29_fields"
            in record["unchanged_guarantees"])
    # frozen deterministic rule TEXT untouched
    from sparta_commander.ny_session_fvg_choch_strategy_spec_contract import (
        DETERMINISTIC_RULES, FIB_LEVEL, FIB_TOLERANCE, RISK_REWARD_TARGET)
    assert FIB_LEVEL == 0.618 and FIB_TOLERANCE == 0.05
    assert RISK_REWARD_TARGET == 4.0
    assert "htf_15m_bullish_fvg" in DETERMINISTIC_RULES


def test_no_replay_pnl_or_scoring_fields_added():
    edited = me.build_edited_candidate_asset()
    for name in list(edited["fields"]) + list(
            edited["fields"]["parameters"]):
        lowered = str(name).lower()
        for token in ("pnl", "profit", "replay", "win_rate", "net_r",
                      "gross_r"):
            assert token not in lowered, name
    record = me.build_mutable_candidate_edit_v1()
    assert record["runs_replay_now"] is False
    assert record["scores_now"] is False
    assert "no_pnl_logic_anywhere" in record["unchanged_guarantees"]
    assert "replay_logic_unchanged" in record["unchanged_guarantees"]


def test_no_live_trading_capability_added():
    edited = me.build_edited_candidate_asset()
    assert edited["research_only"] is True
    assert edited["live_trading_authorized"] is False
    assert edited["paper_trading_authorized"] is False
    record = me.build_mutable_candidate_edit_v1()
    for key in ("authorizes_paper_execution", "authorizes_micro_live",
                "authorizes_live_trading", "uses_real_money",
                "contains_order_logic", "promotes_gate",
                "unlocks_downstream_gate"):
        assert record[key] is False, key
    assert record["paper_trading_gate_locked"] is True
    assert record["micro_live_gate_locked"] is True
    assert record["live_gate_locked"] is True
    tampered = me.build_mutable_candidate_edit_v1()
    tampered["live_gate_locked"] = False
    assert me.validate_mutable_candidate_edit_v1(tampered)["valid"] is False


def test_no_network_credential_or_order_access():
    record = me.build_mutable_candidate_edit_v1()
    for key in ("fetches_data", "calls_api", "uses_network",
                "uses_credentials", "uses_wallet", "connects_broker",
                "connects_exchange"):
        assert record[key] is False, key
    # the pushed asset-spec token screen still rejects smuggled fields
    from sparta_commander.crypto_d1_auto_research_mutable_candidate_asset_spec import (
        validate_candidate_asset)
    smuggled = me.build_edited_candidate_asset()
    smuggled["fields"] = dict(smuggled["fields"], api_key_env="X")
    assert validate_candidate_asset(smuggled)["verdict"] == (
        "CANDIDATE_ASSET_REJECTED")
    smuggled2 = me.build_edited_candidate_asset()
    smuggled2["fields"] = dict(smuggled2["fields"], order_endpoint="X")
    assert validate_candidate_asset(smuggled2)["verdict"] == (
        "CANDIDATE_ASSET_REJECTED")


def test_no_candle_mutation():
    record = me.build_mutable_candidate_edit_v1()
    assert record["modifies_staged_candles"] is False
    assert "staged_candles_unchanged" in record["unchanged_guarantees"]
    manifest = "C:/SPARTA_BRAIN/data/ny_fvg_choch/staged/manifest.txt"
    if os.path.isfile(manifest):
        sha = hashlib.sha256(open(manifest, "rb").read()).hexdigest()
        assert sha == ("cbe83729cea90f233c257078063f0bd342baac64bef1a9a4"
                       "ef64a6f9539de82e")


def test_previous_labels_kept_on_record_and_unchanged():
    record = me.build_mutable_candidate_edit_v1()
    assert record["previous_labels_kept_on_record"] is True
    assert record["modifies_previous_labels"] is False
    labels = ("C:/SPARTA_BRAIN/data/ny_fvg_choch/detector_labels/"
              "detector_labels_2026-06-10.jsonl")
    if os.path.isfile(labels):
        sha = hashlib.sha256(open(labels, "rb").read()).hexdigest()
        assert sha == ("bd4241d8235cab57c013fd51661846fd583d871c4c33e057"
                       "5c7768ea457795c5")


def test_redetection_not_run_automatically():
    record = me.build_mutable_candidate_edit_v1()
    assert record["runs_detector_now"] is False
    assert record["redetection_not_run_here"] is True
    src = open(me.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    assert "detector_run_once" not in src  # never imports the run tool
    assert "automatic_redetection" in me.FORBIDDEN


def test_human_approval_required_before_new_detection_pass():
    record = me.build_mutable_candidate_edit_v1()
    assert record["redetection_requires_separate_human_approval"] is True
    assert record["next_required_action"] == (
        "HUMAN_APPROVED_REDETECTION_WITH_EDITED_CANDIDATE")
    assert record["human_review_required"] is True
    tampered = me.build_mutable_candidate_edit_v1()
    tampered["redetection_requires_separate_human_approval"] = False
    assert me.validate_mutable_candidate_edit_v1(tampered)["valid"] is False


def test_validator_strict_and_deterministic():
    assert (me.build_mutable_candidate_edit_v1()
            == me.build_mutable_candidate_edit_v1())
    tampered = me.build_mutable_candidate_edit_v1()
    tampered["new_parameters"] = dict(tampered["new_parameters"],
                                      max_fvg_age_bars=9999)
    assert me.validate_mutable_candidate_edit_v1(tampered)["valid"] is False
    tampered2 = me.build_mutable_candidate_edit_v1()
    tampered2["applied_edits"] = ["weaken_everything"]
    assert me.validate_mutable_candidate_edit_v1(tampered2)["valid"] is False
    tampered3 = me.build_mutable_candidate_edit_v1()
    tampered3["forbidden"] = tampered3["forbidden"][:3]
    assert me.validate_mutable_candidate_edit_v1(tampered3)["valid"] is False
    tampered4 = me.build_mutable_candidate_edit_v1()
    tampered4["edited_asset"]["fields"]["parameters"]["max_fvg_age_bars"] = 1
    assert me.validate_mutable_candidate_edit_v1(tampered4)["valid"] is False


def test_upstream_stack_and_pm_lane_untouched():
    import sparta_commander.ny_session_fvg_choch_detector_labels_review_contract as dl
    assert dl.NEXT_REQUIRED_ACTION == "HUMAN_DECISION_ON_MUTABLE_CANDIDATE_EDIT"
    import sparta_commander.ny_session_fvg_choch_real_candle_staged_files_review_contract as sr
    assert sr.VERDICT_SR_ACCEPTED == (
        "REAL_CANDLE_STAGED_FILES_ACCEPTED_FOR_DETECTOR_RUN")
    import sparta_commander.ny_session_fvg_choch_public_candle_fetch_runner_dry_run as fr
    assert fr.RUNNER_ENABLED_BY_DEFAULT is False
    import sparta_commander.ny_session_fvg_choch_real_candle_file_creation_tool as fc
    assert fc.TOOL_ENABLED_BY_DEFAULT is False
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
    from sparta_commander.strategy_factory_mission_flow_status import (
        LATEST_COMPLETED_PM_LANE_CHAIN)
    assert "Research Only" in LATEST_COMPLETED_PM_LANE_CHAIN


def test_label_action_and_imports_clean():
    assert me.get_mutable_candidate_edit_v1_label() == me.ME_LABEL
    assert "READ-ONLY" in me.ME_LABEL and me.ME_MODE == "RESEARCH_ONLY"
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in me.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(me.__file__, encoding="utf-8").read()
    assert "while true" not in src.lower() and "sleep(" not in src.lower()
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch("):
        assert verb not in src, verb
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