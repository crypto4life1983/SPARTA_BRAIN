"""Tests for the Strategy Factory Autopilot Research Loop V1 contract.

Proves: the four-candidate rejection ledger gates the loop live; all
safety locks enforced; zero trading/paper/live capability; no auto-push
or auto-commit; ordered loop stages; auto-rejection rules present; human
gates required; seeds future-family-only; candidate #5 cannot reuse a
rejected family unchanged; winner/profitability language is screened;
controller is research-only. Commander safety suite runs alongside."""

from __future__ import annotations

import ast

import sparta_commander.strategy_factory_autopilot_research_loop_v1_contract as ap


def test_contract_ready_and_gated_on_four_record_ledger():
    record = ap.build_autopilot_loop_contract()
    assert record["verdict"] == ap.VERDICT_AP_READY
    assert record["blockers"] == []
    assert ap.validate_autopilot_loop_contract(record)["valid"] is True
    from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
        REJECTION_STATUS as C1, REJECTION_REASON as R1)
    from sparta_commander.crypto_intraday_breakout_pullback_structure_v2_result_and_rejection_record_contract import (
        REJECTION_STATUS as C2, REJECTION_REASON as R2)
    from sparta_commander.btc_sol_long_trend_continuation_v1_result_and_rejection_record_contract import (
        REJECTION_STATUS as C3, REJECTION_REASON as R3)
    from sparta_commander.sol_btc_long_1h_swing_structure_rejection_record_contract import (
        REJECTION_STATUS as C4, REJECTION_REASON as R4)
    assert C1 == C2 == C3 == C4 == "REJECTED_KEPT_ON_RECORD"
    assert R1 == "COST_NON_VIABLE_RISK_GEOMETRY"
    assert R2 == ("EDGE_FAILURE_SURVIVED_ONE_AUTHORIZED_FILTER"
                  "_EXPERIMENT")
    assert R3 == "NEAR_ZERO_SETUPS_AFTER_ONE_AUTHORIZED_STRUCTURE_EDIT"
    assert R4 == ("EDGE_FAILURE_SURVIVED_ONE_AUTHORIZED_FILTER_ONLY"
                  "_EDIT")
    ledger = record["four_candidate_ledger"]
    for name in ("candidate_1", "candidate_2", "candidate_3",
                 "candidate_4"):
        assert ledger[name]["status"] == "REJECTED_KEPT_ON_RECORD", name
    assert ledger["zero_trades_zero_claims_zero_deleted_evidence"] is True
    assert record["ledger_head_at_definition"] == (
        "bed8f5241768ff6ec5e2cb8638ce1439ee2d9ee1")
    # determinism
    assert ap.build_autopilot_loop_contract() == record


def test_loop_stages_are_ordered():
    assert ap.LOOP_STAGES == (
        "candidate_spec",
        "detector_and_label_review",
        "real_candle_label_freeze",
        "fee_honest_replay",
        "replay_results_review",
        "one_authorized_edit_if_pre_committed_and_evidence_supported",
        "formal_rejection_record_or_promotion_to_human_review_record")
    # replay must come after labels are frozen; edit after review;
    # terminal record last
    assert ap.LOOP_STAGES.index("fee_honest_replay") > (
        ap.LOOP_STAGES.index("real_candle_label_freeze"))
    assert ap.LOOP_STAGES.index(
        "one_authorized_edit_if_pre_committed_and_evidence_supported"
    ) > ap.LOOP_STAGES.index("replay_results_review")
    assert ap.LOOP_STAGES[-1].startswith("formal_rejection_record")
    tampered = ap.build_autopilot_loop_contract()
    tampered["loop_stages_ordered"] = list(reversed(ap.LOOP_STAGES))
    assert ap.validate_autopilot_loop_contract(tampered)["valid"] is False


def test_auto_rejection_rules_present():
    rules = ap.AUTO_REJECTION_RULES
    for rule in ("gross_negative_and_net_negative_after_replay",
                 "below_breakeven_hit_rate",
                 "near_zero_setup_count_after_one_structure_edit",
                 "cost_nonviable_risk_geometry",
                 "filter_or_edit_spent_and_still_negative",
                 "correlation_or_overlap_adjusted_failure",
                 "any_artifact_hash_or_gate_mismatch"):
        assert rule in rules, rule
    tampered = ap.build_autopilot_loop_contract()
    tampered["auto_rejection_rules"] = list(rules[:2])
    assert ap.validate_autopilot_loop_contract(tampered)["valid"] is False


def test_human_gates_required():
    gates = ap.HUMAN_GATES
    for gate in ("commit_approval", "push_approval",
                 "promotion_to_paper_review",
                 "promotion_to_paper_trading",
                 "promotion_to_micro_live",
                 "any_credential_api_or_order_capability"):
        assert gate in gates, gate
    assert any("weakens_entries_or_adds_trades_after_labels" in gate
               for gate in gates)
    tampered = ap.build_autopilot_loop_contract()
    tampered["human_gates"] = list(gates[:1])
    assert ap.validate_autopilot_loop_contract(tampered)["valid"] is False


def test_safety_locks_enforced():
    locks = ap.SAFETY_LOCKS
    for lock in ("paper_and_live_locked",
                 "order_account_wallet_api_capability_false",
                 "no_auto_delete_evidence",
                 "no_auto_overwrite_artifacts",
                 "no_profitability_claim_until_separate_promotion"
                 "_contract",
                 "no_winner_wording_from_small_samples",
                 "all_output_must_be_evidence_language_only",
                 "no_auto_push"):
        assert lock in locks, lock
    assert any("no_auto_commit_unless_a_future_human_approved_policy"
               in lock for lock in locks)
    record = ap.build_autopilot_loop_contract()
    for key in ("executes", "writes_files", "runs_real_detection_now",
                "runs_replay_now", "scores_now", "stages_data_now",
                "fetches_data", "calls_api", "uses_network",
                "uses_credentials", "uses_wallet", "uses_account",
                "connects_broker", "connects_exchange", "uses_real_money",
                "contains_order_logic", "starts_scheduler",
                "sends_notifications", "auto_commits", "auto_pushes",
                "auto_deletes_evidence", "auto_overwrites_artifacts",
                "starts_candidate_5_now",
                "authorizes_paper_execution", "authorizes_micro_live",
                "authorizes_live_trading", "promotes_gate",
                "unlocks_downstream_gate", "claims_profitability"):
        assert record[key] is False, key
    assert record["paper_trading_gate_locked"] is True
    assert record["micro_live_gate_locked"] is True
    assert record["live_gate_locked"] is True
    assert record["controller_is_research_only"] is True
    role = record["scheduled_role"]
    assert role["may_certify_ledger"] is True
    assert role["may_produce_research_status_report"] is True
    assert role["may_recommend_next_candidate_family"] is True
    for key in ("may_trade", "may_paper_trade", "may_push", "may_commit",
                "may_claim_profitability"):
        assert role[key] is False, key
    for field, value in (("safety_locks", []),
                         ("scheduled_role", {"may_trade": True}),
                         ("auto_pushes", True),
                         ("auto_commits", True),
                         ("auto_deletes_evidence", True),
                         ("starts_candidate_5_now", True),
                         ("claims_profitability", True),
                         ("live_gate_locked", False),
                         ("controller_is_research_only", False)):
        tampered = ap.build_autopilot_loop_contract()
        tampered[field] = value
        assert ap.validate_autopilot_loop_contract(
            tampered)["valid"] is False, field


def test_seeds_future_family_only_and_candidate_5_policy():
    policy = ap.CANDIDATE_5_POLICY
    assert any("non_overlap_cooldown" in item
               and "label_replay_time" in item for item in policy)
    assert any("structural_stop_geometry_must_be_tested_against_fees"
               in item for item in policy)
    assert any("too_small_to_promote" in item for item in policy)
    assert any("btc_weakness_in_c4_is_not_edge_evidence" in item
               for item in policy)
    assert any("overlapping_cluster" in item and "penalized" in item
               for item in policy)
    assert "candidate_5_must_not_reuse_c4_as_is" in policy
    assert "candidate_5_must_start_from_a_clean_hypothesis" in policy
    rules = ap.QUEUE_RULES
    assert any("inspiration only, never rescue" in rule for rule in rules)
    assert any("never be reused unchanged" in rule for rule in rules)
    tampered = ap.build_autopilot_loop_contract()
    tampered["candidate_5_policy"] = []
    assert ap.validate_autopilot_loop_contract(tampered)["valid"] is False


def test_candidate_5_cannot_reuse_rejected_family_unchanged():
    for family in ap.REJECTED_FAMILIES:
        proposal = {"family": family,
                    "hypothesis": "a fresh idea",
                    "difference_from_rejected_families": "none",
                    "uses_seeds_as_rescue": False}
        check = ap.validate_candidate_family_proposal(proposal)
        assert check["acceptable"] is False, family
        assert ("rejected_family_must_not_be_reused_unchanged"
                in check["errors"]), family
    good = {"family": "a_materially_new_family",
            "hypothesis": ("test whether 4h structure with built-in "
                           "non-overlap at label time clears fees"),
            "difference_from_rejected_families": (
                "different timeframe and built-in dedup vs all four"),
            "uses_seeds_as_rescue": False}
    assert ap.validate_candidate_family_proposal(good)["acceptable"] \
        is True
    rescue = dict(good, uses_seeds_as_rescue=True)
    assert ap.validate_candidate_family_proposal(
        rescue)["acceptable"] is False
    missing = dict(good, hypothesis="")
    assert ap.validate_candidate_family_proposal(
        missing)["acceptable"] is False
    assert ap.validate_candidate_family_proposal(
        None)["acceptable"] is False


def test_no_winner_or_profitability_language_allowed():
    for bad in ("this is a WINNER", "clearly profitable",
                "edge confirmed at last", "ready for live deployment",
                "the holy grail", "guaranteed returns",
                "ready for paper next week"):
        result = ap.screen_output_language(bad)
        assert result["acceptable"] is False, bad
        assert result["violations"], bad
    good = ("22 labels replayed at 27 bps; all variants net-negative; "
            "rejection pressure recorded; evidence frozen")
    assert ap.screen_output_language(good)["acceptable"] is True
    assert ap.screen_output_language(None)["acceptable"] is False
    bad_proposal = {"family": "new_family",
                    "hypothesis": "this winner strategy will print",
                    "difference_from_rejected_families": "x",
                    "uses_seeds_as_rescue": False}
    check = ap.validate_candidate_family_proposal(bad_proposal)
    assert check["acceptable"] is False
    assert "forbidden_language_in_hypothesis" in check["errors"]
    tampered = ap.build_autopilot_loop_contract()
    tampered["forbidden_output_language"] = []
    assert ap.validate_autopilot_loop_contract(tampered)["valid"] is False


def test_ledger_and_head_tamper_invalidates():
    for field, value in (
            ("ledger_head_at_definition", "00" * 20),
            ("four_candidate_ledger", {}),
            ("rejected_families", []),
            ("queue_rules", []),
            ("human_gates", []),
            ("cost_floor_bps", 54)):
        tampered = ap.build_autopilot_loop_contract()
        tampered[field] = value
        assert ap.validate_autopilot_loop_contract(
            tampered)["valid"] is False, field
    revived = ap.build_autopilot_loop_contract()
    revived["four_candidate_ledger"]["candidate_4"]["status"] = "REVIVED"
    assert ap.validate_autopilot_loop_contract(revived)["valid"] is False


def test_label_action_and_module_purity():
    assert ap.get_autopilot_loop_label() == ap.AP_LABEL
    assert "READ-ONLY" in ap.AP_LABEL
    assert "NEVER A TRADER" in ap.AP_LABEL
    assert ap.AP_MODE == "RESEARCH_ONLY"
    assert ap.VERDICT_AP_READY == (
        "STRATEGY_FACTORY_AUTOPILOT_RESEARCH_LOOP_V1_READY")
    assert ap.NEXT_REQUIRED_ACTION == (
        "HUMAN_APPROVED_CANDIDATE_5_FAMILY_PROPOSAL_VIA_AUTOPILOT_LOOP")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in ap.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(ap.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch("):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned_mods = {"urllib", "requests", "socket", "http", "ccxt",
                   "smtplib", "subprocess", "websockets", "aiohttp",
                   "schedule", "apscheduler", "threading", "asyncio",
                   "time", "sched", "telegram", "email", "csv", "pandas",
                   "pathlib", "os", "io", "json", "shutil", "databento",
                   "ssl", "ftplib", "datetime", "hashlib", "statistics"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods)
    assert not any(
        call.func.attr == "open" if isinstance(call.func, ast.Attribute)
        else getattr(call.func, "id", "") == "open"
        for call in ast.walk(tree) if isinstance(call, ast.Call))
