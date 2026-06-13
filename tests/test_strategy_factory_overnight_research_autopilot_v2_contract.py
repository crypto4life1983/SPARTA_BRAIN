"""Tests for the Overnight Research Autopilot V2 contract.

Covers all 16 commanded requirements: passes when six-record ledger
holds; blocks when any C1-C6 is not REJECTED_KEPT_ON_RECORD; recognizes
C6 rejection reason; refuses to re-recommend C6's failed family;
freezes a valid next-candidate recommendation-plan schema; freezes a
valid morning-report schema; cannot authorize detector / real-candle
detection / replay / fetch / external data / paper / live / order-api-
wallet-account-credential / auto-commit / auto-push / scheduler
activation; claim locks held; AST/purity green. Commander safety suite
runs alongside (12 tests)."""

from __future__ import annotations

import ast

import sparta_commander.multi_symbol_relative_strength_rotation_filter_rejection_record_contract as rj6
import sparta_commander.strategy_factory_overnight_research_autopilot_v2_contract as oap2


def _record():
    return oap2.build_overnight_research_autopilot_v2_contract()


# (1) V2 passes when all six rejection records are live -------------------

def test_1_v2_passes_when_six_record_ledger_holds():
    record = _record()
    assert record["verdict"] == oap2.VERDICT_OAP2_READY
    assert record["blockers"] == []
    assert oap2.validate_overnight_research_autopilot_v2(
        record)["valid"] is True
    assert record["ledger_all_rejected_kept_on_record"] is True
    assert list(record["ledger_status_six_records"]) == [
        "REJECTED_KEPT_ON_RECORD"] * 6
    # determinism
    assert _record() == record


# (2) V2 blocks if any of C1-C6 is missing or not REJECTED_KEPT_ON_RECORD --

def test_2_v2_blocks_if_any_ledger_entry_not_rejected():
    # mock the ledger by reaching into the module and temporarily
    # rebinding one rejection status; restore afterwards
    import sparta_commander.strategy_factory_overnight_research_autopilot_v2_contract as mod
    originals = {
        "C1_STATUS": mod.C1_STATUS, "C2_STATUS": mod.C2_STATUS,
        "C3_STATUS": mod.C3_STATUS, "C4_STATUS": mod.C4_STATUS,
        "C5_STATUS": mod.C5_STATUS, "C6_STATUS": mod.C6_STATUS,
    }
    try:
        for key in originals:
            for replacement in ("APPROVED_FOR_TRADING", "PENDING",
                                "PROMOTED", ""):
                setattr(mod, key, replacement)
                record = (
                    mod.build_overnight_research_autopilot_v2_contract())
                assert record["verdict"] == oap2.VERDICT_OAP2_BLOCKED, (
                    key, replacement)
                assert "six_record_ledger_broken" in record[
                    "blockers"], (key, replacement)
                assert record[
                    "ledger_all_rejected_kept_on_record"] is False
            setattr(mod, key, originals[key])
    finally:
        for key, value in originals.items():
            setattr(mod, key, value)
    # baseline restored back to READY
    record = mod.build_overnight_research_autopilot_v2_contract()
    assert record["verdict"] == oap2.VERDICT_OAP2_READY


# (3) V2 recognizes C6 rejection reason EDIT_SPENT_AND_STILL_NEGATIVE... --

def test_3_v2_recognizes_c6_rejection_reason():
    record = _record()
    assert record["c6_rejection_reason"] == (
        "EDIT_SPENT_AND_STILL_NEGATIVE_EDGE_FAILURE")
    assert rj6.REJECTION_REASON == (
        "EDIT_SPENT_AND_STILL_NEGATIVE_EDGE_FAILURE")
    assert record["c6_rejection_reason"] == rj6.REJECTION_REASON


# (4) V2 does not reuse C6's failed family as a new recommendation -------

def test_4_v2_refuses_to_re_recommend_c6_family():
    record = _record()
    blacklist = record["rejected_family_logic_blacklist"]
    assert "multi_symbol_relative_strength_rotation_filter" in (
        blacklist)
    # the plan schema's blacklist must include all six
    plan_blacklist = record[
        "next_candidate_recommendation_plan_schema"][
        "rejected_family_logic_blacklist"]
    for family in ("ny_session_fvg_choch_v3",
                   "crypto_intraday_breakout_pullback_structure_v2",
                   "btc_sol_long_trend_continuation_v1",
                   "sol_btc_long_1h_swing_structure",
                   "eth_sol_relative_strength_pullback_continuation_v1",
                   "multi_symbol_relative_strength_rotation_filter"):
        assert family in plan_blacklist, family
    # the plan also explicitly states it cannot reuse rejected logic
    assert record["next_candidate_recommendation_plan_schema"][
        "plan_cannot_reuse_any_rejected_family_logic"] is True
    # tampering with the blacklist invalidates the contract
    tampered = _record()
    tampered["rejected_family_logic_blacklist"] = []
    assert oap2.validate_overnight_research_autopilot_v2(
        tampered)["valid"] is False
    tampered = _record()
    tampered["next_candidate_recommendation_plan_schema"] = dict(
        tampered["next_candidate_recommendation_plan_schema"],
        rejected_family_logic_blacklist=[])
    assert oap2.validate_overnight_research_autopilot_v2(
        tampered)["valid"] is False


# (5) V2 produces a valid next-candidate recommendation-plan structure ----

def test_5_next_candidate_recommendation_plan_schema():
    record = _record()
    plan = record["next_candidate_recommendation_plan_schema"]
    assert plan["plan_kind"] == (
        "overnight_research_autopilot_v2_next_candidate_plan")
    required = plan["required_fields"]
    for field in ("proposed_family_label",
                  "hypothesis_statement",
                  "edge_source_hypothesis",
                  "universe_proposal",
                  "timeframe_proposal",
                  "direction_proposal",
                  "fee_assumption_round_trip_bps",
                  "minimum_gross_target_distance_floor_bps",
                  "sample_window_proposal",
                  "differentiation_from_each_rejected_family",
                  "explicit_non_reuse_of_rejected_family_logic",
                  "rationale_paragraph",
                  "human_review_required_at_every_gate",
                  "no_promotion_no_paper_no_live"):
        assert field in required, field
    assert plan["fee_assumption_must_equal_27_bps_round_trip"] is True
    assert plan["minimum_floor_must_equal_81_bps"] is True
    assert plan["plan_is_research_only"] is True
    assert plan["plan_authorizes_nothing"] is True
    assert plan["plan_is_not_a_promotion"] is True
    assert plan["human_review_required_at_every_gate"] is True
    # differentiation must reference each rejected family
    targets = plan["differentiation_must_address_each_of"]
    for family in ("ny_session_fvg_choch_v3",
                   "crypto_intraday_breakout_pullback_structure_v2",
                   "btc_sol_long_trend_continuation_v1",
                   "sol_btc_long_1h_swing_structure",
                   "eth_sol_relative_strength_pullback_continuation_v1",
                   "multi_symbol_relative_strength_rotation_filter"):
        assert family in targets, family


# (6) V2 produces a valid morning-report schema -------------------------

def test_6_morning_report_schema():
    record = _record()
    mr = record["morning_report_schema"]
    assert mr["report_kind"] == (
        "overnight_research_autopilot_v2_morning_report")
    required = mr["required_fields"]
    for field in ("report_date_utc", "head_at_report",
                  "previous_night_status",
                  "candidate_under_review",
                  "completed_gate", "blockers", "honest_verdict",
                  "next_human_gate",
                  "ledger_status_six_records",
                  "no_profitability_claim_lock",
                  "no_paper_approval_lock",
                  "no_live_approval_lock",
                  "no_winner_wording_lock",
                  "no_execution_lock",
                  "no_auto_commit_lock",
                  "no_auto_push_lock"):
        assert field in required, field
    assert mr["report_is_research_only"] is True
    assert mr["report_authorizes_nothing"] is True
    assert mr["report_is_not_a_profitability_claim"] is True
    # banned tokens checklist for the morning report's next_human_gate
    banned = mr["banned_tokens_in_next_human_gate"]
    for token in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                  "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                  "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert token in banned, token


# (7) V2 cannot authorize detector execution ---------------------------

def test_7_v2_cannot_authorize_detector_execution():
    record = _record()
    assert record["runs_detector"] is False
    assert record["creates_detector_implementation_now"] is False
    tampered = _record()
    tampered["runs_detector"] = True
    assert oap2.validate_overnight_research_autopilot_v2(
        tampered)["valid"] is False


# (8) V2 cannot authorize real-candle detection ------------------------

def test_8_v2_cannot_authorize_real_candle_detection():
    record = _record()
    assert record["runs_real_candle_detection"] is False
    assert record["runs_real_detection_now"] is False
    tampered = _record()
    tampered["runs_real_candle_detection"] = True
    assert oap2.validate_overnight_research_autopilot_v2(
        tampered)["valid"] is False


# (9) V2 cannot authorize replay ---------------------------------------

def test_9_v2_cannot_authorize_replay():
    record = _record()
    assert record["runs_replay"] is False
    assert record["runs_replay_now"] is False
    assert record["runs_relabel"] is False
    tampered = _record()
    tampered["runs_replay"] = True
    assert oap2.validate_overnight_research_autopilot_v2(
        tampered)["valid"] is False
    tampered2 = _record()
    tampered2["runs_relabel"] = True
    assert oap2.validate_overnight_research_autopilot_v2(
        tampered2)["valid"] is False


# (10) V2 cannot authorize fetch or external data ---------------------

def test_10_v2_cannot_authorize_fetch_or_external_data():
    record = _record()
    assert record["fetches_data"] is False
    assert record["uses_external_data_source"] is False
    assert record["uses_network"] is False
    tampered = _record()
    tampered["fetches_data"] = True
    assert oap2.validate_overnight_research_autopilot_v2(
        tampered)["valid"] is False
    tampered2 = _record()
    tampered2["uses_external_data_source"] = True
    assert oap2.validate_overnight_research_autopilot_v2(
        tampered2)["valid"] is False
    tampered3 = _record()
    tampered3["uses_network"] = True
    assert oap2.validate_overnight_research_autopilot_v2(
        tampered3)["valid"] is False


# (11) V2 cannot authorize paper/live trading -------------------------

def test_11_v2_cannot_authorize_paper_or_live():
    record = _record()
    assert record["authorizes_paper_execution"] is False
    assert record["authorizes_micro_live"] is False
    assert record["authorizes_live_trading"] is False
    assert record["paper_trading_gate_locked"] is True
    assert record["micro_live_gate_locked"] is True
    assert record["live_gate_locked"] is True
    for field in ("authorizes_paper_execution",
                  "authorizes_micro_live",
                  "authorizes_live_trading"):
        tampered = _record()
        tampered[field] = True
        assert oap2.validate_overnight_research_autopilot_v2(
            tampered)["valid"] is False, field


# (12) V2 cannot use order/API/wallet/account/credential capability --

def test_12_v2_cannot_use_order_api_wallet_account_credential():
    record = _record()
    for key in ("contains_order_logic",
                "contains_portfolio_allocation_logic",
                "calls_api", "uses_credentials", "uses_wallet",
                "uses_account", "connects_broker",
                "connects_exchange", "uses_real_money"):
        assert record[key] is False, key
        tampered = _record()
        tampered[key] = True
        assert oap2.validate_overnight_research_autopilot_v2(
            tampered)["valid"] is False, key


# (13) V2 cannot auto-commit or auto-push -----------------------------

def test_13_v2_cannot_auto_commit_or_auto_push():
    record = _record()
    assert record["auto_commits"] is False
    assert record["auto_pushes"] is False
    for field in ("auto_commits", "auto_pushes"):
        tampered = _record()
        tampered[field] = True
        assert oap2.validate_overnight_research_autopilot_v2(
            tampered)["valid"] is False, field
    locks = record["claim_locks"]
    assert "no_auto_commit" in locks
    assert "no_auto_push" in locks


# (14) V2 cannot activate a scheduler ---------------------------------

def test_14_v2_cannot_activate_scheduler():
    record = _record()
    assert record["starts_scheduler"] is False
    assert record["sends_notifications"] is False
    for field in ("starts_scheduler", "sends_notifications"):
        tampered = _record()
        tampered[field] = True
        assert oap2.validate_overnight_research_autopilot_v2(
            tampered)["valid"] is False, field
    assert "no_scheduler_activation" in record["claim_locks"]


# (15) Claim locks held: no profitability, no winner, no paper/live ---

def test_15_claim_locks_held():
    record = _record()
    locks = record["claim_locks"]
    for lock in ("no_profitability_claim", "no_paper_approval",
                 "no_live_approval", "no_execution_approval",
                 "no_winner_wording", "no_promotion_by_v2",
                 "no_unlock_by_v2",
                 "no_scheduler_activation", "no_auto_commit",
                 "no_auto_push",
                 "no_morning_report_generation_now",
                 "no_next_candidate_proposal_drafting_now"):
        assert lock in locks, lock
    assert record["claims_profitability"] is False
    assert record["generates_morning_report_now"] is False
    assert record["generates_next_candidate_proposal_now"] is False
    tampered = _record()
    tampered["claim_locks"] = []
    assert oap2.validate_overnight_research_autopilot_v2(
        tampered)["valid"] is False
    tampered = _record()
    tampered["claims_profitability"] = True
    assert oap2.validate_overnight_research_autopilot_v2(
        tampered)["valid"] is False
    # label must include READ-ONLY / NOT A PROFITABILITY CLAIM framing
    label = oap2.OAP2_LABEL
    assert "READ-ONLY" in label
    assert "NO EXECUTION" in label
    assert "NO TRADING" in label
    assert "NO AUTO-PUSH" in label
    assert "NO SCHEDULER" in label
    assert "NOT A PROFITABILITY CLAIM" in label


# (16) AST / purity ----------------------------------------------------

def test_16_ast_purity_and_no_writers_or_runners():
    assert oap2.get_overnight_autopilot_v2_label() == oap2.OAP2_LABEL
    assert oap2.OAP2_MODE == "RESEARCH_ONLY"
    assert oap2.VERDICT_OAP2_READY == (
        "STRATEGY_FACTORY_OVERNIGHT_RESEARCH_AUTOPILOT_V2_READY")
    assert oap2.NEXT_REQUIRED_ACTION == (
        "HUMAN_DECISION_GENERATE_MORNING_REPORT_OR_PROPOSE_NEXT"
        "_CANDIDATE_FAMILY")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in oap2.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(oap2.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    assert "random" not in src
    assert "now(" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch(", "subprocess", "Popen", "system("):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned_mods = {"urllib", "requests", "socket", "http", "ccxt",
                   "smtplib", "subprocess", "websockets", "aiohttp",
                   "schedule", "apscheduler", "threading", "asyncio",
                   "time", "sched", "telegram", "email", "csv", "pandas",
                   "pathlib", "os", "io", "json", "shutil", "databento",
                   "ssl", "ftplib", "datetime", "hashlib", "statistics",
                   "random"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods)
    assert not any(
        call.func.attr == "open" if isinstance(call.func, ast.Attribute)
        else getattr(call.func, "id", "") == "open"
        for call in ast.walk(tree) if isinstance(call, ast.Call))
