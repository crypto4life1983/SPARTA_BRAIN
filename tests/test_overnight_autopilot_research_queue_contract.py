"""Tests for the SPARTA Overnight Autopilot Research Queue Contract.

Proves the autopilot can only ever execute the four safe offline task
types; that every human-gated research action is refusable-or-proposal-only;
that morning run records must name what ran, the artifacts, and the next
human gate with zero claims; that the two-candidate ledger is preserved
verbatim; and that no daemon/loop/scheduler exists in our code.
"""

from __future__ import annotations

import ast

import sparta_commander.overnight_autopilot_research_queue_contract as oa


def _task(**overrides):
    task = {"task_id": "t001", "task_type": "integrity_audit",
            "status": "queued", "params": {}}
    task.update(overrides)
    return task


def _run_record(**overrides):
    record = {
        "run_id": "overnight_20260613",
        "started_utc": "2026-06-13T02:00:00Z",
        "finished_utc": "2026-06-13T02:04:00Z",
        "tasks_executed": [{"task_id": "t001",
                            "task_type": "integrity_audit"}],
        "tasks_skipped": [],
        "proposals_surfaced_for_human": [],
        "artifacts_produced": ["data/overnight_autopilot/reports/x.json"],
        "integrity_status": "INTACT",
        "claims_made": "none",
        "no_commit_no_push": True,
        "next_human_gate": "HUMAN_DECISION_ON_NEXT_CANDIDATE_FAMILY",
    }
    record.update(overrides)
    return record


def test_contract_ready_and_gated_on_intact_ledger():
    record = oa.build_overnight_autopilot_contract()
    assert record["verdict"] == oa.VERDICT_OA_READY
    assert record["blockers"] == []
    assert oa.validate_overnight_autopilot_contract(record)["valid"] is True


def test_allowed_task_types_are_the_safe_four():
    assert oa.ALLOWED_TASK_TYPES == (
        "integrity_audit", "contract_certification_sweep",
        "safety_test_suite_report", "seed_research_brief_draft")
    for task_type in oa.ALLOWED_TASK_TYPES:
        check = oa.validate_queue_task(_task(task_type=task_type))
        assert check["executable"] is True, task_type
        assert check["errors"] == []
        assert task_type in oa.TASK_TYPE_DEFINITIONS


def test_human_gated_research_tasks_are_never_executable():
    for task_type in ("detection_run", "redetection_run", "replay_run",
                      "staging_run", "data_fetch_run", "candle_download",
                      "mutable_edit_application", "strategy_spec_build",
                      "commit_or_push", "mission_flow_registration",
                      "scorer_run", "optimizer_run", "paper_trading",
                      "live_trading", "promotion", "gate_unlock",
                      "evidence_deletion"):
        assert task_type in oa.FORBIDDEN_TASK_TYPES, task_type
        queued = oa.validate_queue_task(_task(task_type=task_type))
        assert queued["executable"] is False, task_type
        assert any("forbidden_task_type_can_only_be_a_proposal" in e
                   for e in queued["errors"]), task_type
        # the SAME type is valid purely as a proposal for the human
        proposal = oa.validate_queue_task(_task(
            task_type=task_type, status="proposal_for_human"))
        assert proposal["executable"] is False, task_type
        assert proposal["is_human_proposal"] is True, task_type


def test_unknown_types_bad_status_and_credentials_reject():
    unknown = oa.validate_queue_task(_task(task_type="mystery_task"))
    assert unknown["executable"] is False
    assert any("task_type_outside_closed_set" in e
               for e in unknown["errors"])
    bad_status = oa.validate_queue_task(_task(status="running_forever"))
    assert bad_status["executable"] is False
    done = oa.validate_queue_task(_task(status="done"))
    assert done["executable"] is False  # only queued tasks execute
    for bad in ("api_key", "wallet_address", "order_id", "broker_ref",
                "login_token", "password"):
        smuggled = oa.validate_queue_task(_task(**{bad: "x"}))
        assert smuggled["executable"] is False, bad
        smuggled2 = oa.validate_queue_task(_task(params={bad: "x"}))
        assert smuggled2["executable"] is False, bad
    assert oa.validate_queue_task(None)["executable"] is False
    no_id = oa.validate_queue_task(_task(task_id=""))
    assert no_id["executable"] is False


def test_run_record_must_be_honest():
    good = oa.validate_run_record(_run_record())
    assert good["acceptable"] is True and good["errors"] == []
    claims = oa.validate_run_record(_run_record(claims_made="profitable!"))
    assert claims["acceptable"] is False
    assert "claims_must_be_none" in claims["errors"]
    pushed = oa.validate_run_record(_run_record(no_commit_no_push=False))
    assert "run_must_not_commit_or_push" in pushed["errors"]
    no_gate = oa.validate_run_record(_run_record(next_human_gate=""))
    assert "next_human_gate_required" in no_gate["errors"]
    missing = dict(_run_record())
    del missing["artifacts_produced"]
    assert oa.validate_run_record(missing)["acceptable"] is False
    ran_forbidden = oa.validate_run_record(_run_record(tasks_executed=[
        {"task_id": "x", "task_type": "replay_run"}]))
    assert ran_forbidden["acceptable"] is False
    assert any("executed_a_forbidden_task" in e
               for e in ran_forbidden["errors"])
    assert oa.validate_run_record(None)["acceptable"] is False


def test_ledger_preserved_verbatim():
    record = oa.build_overnight_autopilot_contract()
    ledger = record["preserved_ledger"]
    assert ledger["candidate_1"] == {
        "candidate_id": "NY_SESSION_FVG_CHOCH_STRATEGY_CANDIDATE_V1",
        "status": "REJECTED_KEPT_ON_RECORD",
        "reason": "COST_NON_VIABLE_RISK_GEOMETRY"}
    assert ledger["candidate_2"] == {
        "candidate_id": "CRYPTO_INTRADAY_BREAKOUT_PULLBACK_STRUCTURE_V1",
        "status": "REJECTED_KEPT_ON_RECORD",
        "reason": "EDGE_FAILURE_SURVIVED_ONE_AUTHORIZED_FILTER"
                  "_EXPERIMENT"}
    assert ledger["seeds_for_new_families_only"] == [
        "btc_was_net_positive_in_all_variants_small_sample",
        "sol_was_net_positive_at_3r_and_4r",
        "long_side_was_materially_stronger_than_shorts"]
    assert ledger["seeds_are_never_rescue_paths"] is True
    assert "reviving_rejected_candidates" in oa.FORBIDDEN
    tampered = oa.build_overnight_autopilot_contract()
    tampered["preserved_ledger"]["candidate_2"]["status"] = "REVIVED"
    assert oa.validate_overnight_autopilot_contract(tampered)[
        "valid"] is False
    # live cross-check against the pushed rejection records
    from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
        REJECTION_STATUS as C1)
    from sparta_commander.crypto_intraday_breakout_pullback_structure_v2_result_and_rejection_record_contract import (
        REJECTION_STATUS as C2)
    assert C1 == C2 == "REJECTED_KEPT_ON_RECORD"


def test_scheduling_model_is_human_installed_one_shot():
    record = oa.build_overnight_autopilot_contract()
    assert "WINDOWS TASK SCHEDULER" in record["scheduling_model"]
    assert "MANUALLY by the human" in record["scheduling_model"]
    assert "one-shot" in record["scheduling_model"]
    assert "no daemon" in record["scheduling_model"]
    assert record["task_install_is_manual_human_action"] is True
    assert record["runner_is_one_shot_no_daemon"] is True
    assert record["starts_scheduler"] is False
    assert ("in_process_daemons_loops_or_sleep_scheduling" in oa.FORBIDDEN)
    tampered = oa.build_overnight_autopilot_contract()
    tampered["runner_is_one_shot_no_daemon"] = False
    assert oa.validate_overnight_autopilot_contract(tampered)[
        "valid"] is False
    tampered2 = oa.build_overnight_autopilot_contract()
    tampered2["scheduling_model"] = "python daemon loop"
    assert oa.validate_overnight_autopilot_contract(tampered2)[
        "valid"] is False


def test_dangerous_capabilities_locked_forever():
    record = oa.build_overnight_autopilot_contract()
    for item in ("wallet_account_order_trading_live_capability",
                 "api_keys_or_broker_credentials",
                 "automatic_paper_or_live_promotion",
                 "automatic_commit_or_push",
                 "deleting_or_hiding_failed_evidence",
                 "executing_human_gated_research_tasks",
                 "profitability_claims", "gate_unlocks"):
        assert item in oa.FORBIDDEN, item
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
    assert record[
        "every_candidate_still_requires_evidence_freeze_and_human"
        "_gates"] is True
    tampered = oa.build_overnight_autopilot_contract()
    tampered["forbidden"] = tampered["forbidden"][:3]
    assert oa.validate_overnight_autopilot_contract(tampered)[
        "valid"] is False
    tampered2 = oa.build_overnight_autopilot_contract()
    tampered2["live_gate_locked"] = False
    assert oa.validate_overnight_autopilot_contract(tampered2)[
        "valid"] is False


def test_deterministic_and_upstream_untouched():
    assert (oa.build_overnight_autopilot_contract()
            == oa.build_overnight_autopilot_contract())
    import sparta_commander.ny_session_fvg_choch_additional_session_days_staged_candles_review as ad
    assert len(ad.BASELINE_PROTECTED_FILES) == 5
    from sparta_commander.crypto_d1_auto_research_strategy_optimizer_contract import (
        build_optimizer_contract)
    assert build_optimizer_contract()["verdict"] == (
        "CRYPTO_D1_AUTO_RESEARCH_OPTIMIZER_CONTRACT_READY")
    from sparta_commander.strategy_factory_mission_flow_status import (
        LATEST_COMPLETED_PM_LANE_CHAIN)
    assert "Research Only" in LATEST_COMPLETED_PM_LANE_CHAIN


def test_label_action_and_no_scheduler_imports():
    assert oa.get_overnight_autopilot_contract_label() == oa.OA_LABEL
    assert "READ-ONLY" in oa.OA_LABEL and oa.OA_MODE == "RESEARCH_ONLY"
    assert oa.NEXT_REQUIRED_ACTION == (
        "HUMAN_APPROVED_OVERNIGHT_AUTOPILOT_FIRST_RUN_ONCE")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in oa.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(oa.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    assert "while true" not in src.lower() and "sleep(" not in src.lower()
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch("):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned_mods = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
                   "subprocess", "websockets", "aiohttp", "schedule",
                   "apscheduler", "threading", "asyncio", "time", "sched",
                   "telegram", "email", "csv", "pandas", "pathlib", "os",
                   "io", "json", "shutil", "databento", "ssl", "ftplib",
                   "datetime", "hashlib"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods)
    assert not any(call.func.attr == "open" if isinstance(call.func, ast.Attribute)
                   else getattr(call.func, "id", "") == "open"
                   for call in ast.walk(tree) if isinstance(call, ast.Call))

def _load_runner_module():
    import importlib.util
    import pathlib
    runner_path = (pathlib.Path(oa.__file__).resolve().parents[1]
                   / "tools" / "overnight_autopilot_run_once.py")
    spec = importlib.util.spec_from_file_location("oa_runner", runner_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_runner_reseed_requeues_defaults_and_preserves_proposals():
    runner = _load_runner_module()
    proposal = {"task_id": "human_idea_1", "task_type": "detection_run",
                "status": "proposal_for_human",
                "params": {"note": "needs HUMAN_APPROVED gate"}}
    proposal_frozen = dict(proposal, params=dict(proposal["params"]))
    queue = [dict(task, status="done") for task in runner.DEFAULT_QUEUE]
    queue.append(proposal)
    reseeded = runner.reseed_queue(queue)
    defaults = [t for t in reseeded
                if t["task_id"] != proposal["task_id"]]
    assert len(defaults) == 4
    assert all(t["status"] == "queued" for t in defaults)
    assert {t["task_type"] for t in defaults} == set(oa.ALLOWED_TASK_TYPES)
    kept = [t for t in reseeded if t["task_id"] == proposal["task_id"]]
    assert kept == [proposal_frozen]  # untouched, byte-for-byte
    # a default task missing from the file is restored as queued
    partial = [dict(runner.DEFAULT_QUEUE[0], status="done")]
    restored = runner.reseed_queue(partial)
    assert len(restored) == 4
    assert all(t["status"] == "queued" for t in restored)
    # reseeded forbidden proposals are STILL not executable afterwards
    for task in reseeded:
        check = oa.validate_queue_task(task)
        if task["task_id"] == proposal["task_id"]:
            assert check["executable"] is False
            assert check["is_human_proposal"] is True
        else:
            assert check["executable"] is True
