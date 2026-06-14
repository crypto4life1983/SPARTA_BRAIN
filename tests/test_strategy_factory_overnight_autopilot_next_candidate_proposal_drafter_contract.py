"""Tests for the Overnight Autopilot Next-Candidate Proposal
Drafter contract.

Verifies: chain-gate on the nine-record ledger + V5 + V4 + V3 +
Overnight Autopilot V2 + Recommendation V1 + Autopilot Loop V1;
non-committed C10 proposal draft template (placeholders only);
non-committed morning autopilot report template (structural pre-
filled fields only); hard locks (no detection/replay/relabel/PnL/
fetch/API/paper/live/trading/scheduler/notifications/runners/
commit/push); validate_c10_proposal_draft enforces V5 blacklist
membership ban, 27 bps fee, 81 bps floor, human_review_required,
all 9 family differentiation, placeholder rejection, banned-token
ban in next_human_gate; AST/purity green."""

from __future__ import annotations

import ast
import copy

import sparta_commander.strategy_factory_autopilot_research_loop_v1_contract as ap
import sparta_commander.strategy_factory_candidate_recommendation_v1_contract as rec
import sparta_commander.strategy_factory_overnight_autopilot_next_candidate_proposal_drafter_contract as drafter
import sparta_commander.strategy_factory_overnight_research_autopilot_v2_contract as oap2
import sparta_commander.strategy_factory_rejected_family_blacklist_v3_contract as bl3
import sparta_commander.strategy_factory_rejected_family_blacklist_v4_contract as bl4
import sparta_commander.strategy_factory_rejected_family_blacklist_v5_contract as bl5


_R = (
    drafter
    .build_overnight_autopilot_next_candidate_proposal_drafter())


# ---- chain gate + ready verdict -------------------------------------------

def test_drafter_ready_and_chain_gates_all_certify():
    assert bl5.build_rejected_family_blacklist_v5()["verdict"] == (
        bl5.VERDICT_BL5_READY)
    assert bl4.build_rejected_family_blacklist_v4()["verdict"] == (
        bl4.VERDICT_BL4_READY)
    assert bl3.build_rejected_family_blacklist_v3()["verdict"] == (
        bl3.VERDICT_BL3_READY)
    assert oap2.build_overnight_research_autopilot_v2_contract()[
        "verdict"] == oap2.VERDICT_OAP2_READY
    assert rec.build_candidate_recommendation()["verdict"] == (
        rec.VERDICT_CR_READY)
    assert ap.build_autopilot_loop_contract()["verdict"] == (
        ap.VERDICT_AP_READY)
    assert _R["verdict"] == drafter.VERDICT_DRAFTER_READY
    assert _R["blockers"] == []
    assert drafter.validate_overnight_autopilot_next_candidate_proposal_drafter(
        _R)["valid"] is True


def test_nine_record_ledger_intact():
    assert _R["ledger_status_nine_records"] == [
        "REJECTED_KEPT_ON_RECORD"] * 9
    assert _R["ledger_all_rejected_kept_on_record"] is True


def test_chain_blocks_when_ledger_breaks():
    import sparta_commander.strategy_factory_overnight_autopilot_next_candidate_proposal_drafter_contract as mod
    originals = {k: getattr(mod, k) for k in
                 ("C1_STATUS", "C2_STATUS", "C3_STATUS",
                  "C4_STATUS", "C5_STATUS", "C6_STATUS",
                  "C7_STATUS", "C8_STATUS", "C9_STATUS")}
    try:
        for key in originals:
            setattr(mod, key, "APPROVED_FOR_TRADING")
            record = (mod
                .build_overnight_autopilot_next_candidate_proposal_drafter())
            assert record["verdict"] == (
                drafter.VERDICT_DRAFTER_BLOCKED), key
            assert "nine_record_ledger_broken" in record[
                "blockers"], key
            setattr(mod, key, originals[key])
    finally:
        for k, v in originals.items():
            setattr(mod, k, v)
    assert (mod
        .build_overnight_autopilot_next_candidate_proposal_drafter()
        )["verdict"] == drafter.VERDICT_DRAFTER_READY


# ---- V5 inheritance ------------------------------------------------------

def test_v5_blacklist_and_lessons_carried_forward():
    assert _R["v5_blacklist_length"] == 9
    assert tuple(_R["v5_blacklist"]) == (
        "ny_session_fvg_choch_v3",
        "crypto_intraday_breakout_pullback_structure_v2",
        "btc_sol_long_trend_continuation_v1",
        "sol_btc_long_1h_swing_structure",
        "eth_sol_relative_strength_pullback_continuation_v1",
        "multi_symbol_relative_strength_rotation_filter",
        "volatility_compression_expansion",
        "liquidity_sweep_mean_reversion",
        "low_volume_downside_capitulation_mean_reversion")
    lessons = _R["inherited_lessons_from_v5"]
    assert len(lessons) == 9
    for i in range(1, 10):
        assert any(f"c{i}_lesson:" in lesson for lesson in lessons)


def test_locked_numerics_match_27_bps_and_81_bps():
    assert _R["locked_fee_round_trip_bps"] == 27
    assert _R["locked_gross_target_distance_floor_bps"] == 81


# ---- C10 draft template (non-committed, placeholders only) ---------------

def test_c10_draft_template_is_non_committed_and_unfilled():
    dt = _R["c10_proposal_draft_template"]
    assert dt["draft_kind"] == (
        "c10_family_proposal_draft_template_human_to_fill")
    assert dt["is_a_committed_proposal"] is False
    assert dt["is_a_promotion"] is False
    assert dt["is_a_winner_claim"] is False
    placeholders = dt["field_placeholders"]
    for field in dt["fields_for_human_to_fill"]:
        assert field in placeholders, field
        assert "TO_BE_FILLED_BY_HUMAN_REVIEW" in placeholders[field], (
            field)
    # The human-fill fields are exactly the placeholder keys: locked
    # numerics/flags (fees/floor/human-review/no-promotion) are NOT
    # human-fill, they live in pre_filled_locked_constraints.
    assert tuple(dt["fields_for_human_to_fill"]) == tuple(
        placeholders.keys())
    # Completeness: human-fill fields + locked/pre-filled fields cover
    # every required field V5 demands of a real C10 proposal.
    covered = set(dt["fields_for_human_to_fill"]) | {
        "fee_assumption_round_trip_bps",
        "minimum_gross_target_distance_floor_bps",
        "human_review_required_at_every_gate",
        "no_promotion_no_paper_no_live",
    }
    assert covered == set(bl5.C10_PROPOSAL_REQUIREMENTS["required_fields"])


def test_c10_draft_template_pre_filled_constraints_locked():
    pl = _R["c10_proposal_draft_template"][
        "pre_filled_locked_constraints"]
    assert tuple(pl["rejected_family_logic_blacklist"]) == tuple(
        _R["v5_blacklist"])
    assert pl["fee_assumption_round_trip_bps"] == 27
    assert pl["minimum_gross_target_distance_floor_bps"] == 81
    assert pl[
        "anti_cluster_protection_required_at_proposal_time"] is True
    assert pl[
        "sample_size_adequacy_required_at_proposal_time"] is True
    assert pl[
        "explicit_edge_argument_beyond_pattern_geometry_required"
    ] is True
    assert pl[
        "joint_or_intersection_trigger_sample_size_pre_justification"
        "_required_if_applicable"] is True
    assert pl["human_review_required_at_every_gate"] is True
    assert pl["no_promotion_no_paper_no_live"] is True


def test_c10_draft_template_validator_invariants_present():
    invariants = _R["c10_proposal_draft_template"][
        "validator_invariants"]
    joined = " || ".join(invariants)
    assert "MUST NOT appear in the V5 blacklist" in joined
    assert "fee_assumption_round_trip_bps MUST equal 27" in joined
    assert ("minimum_gross_target_distance_floor_bps MUST equal "
            "81") in joined
    assert ("human_review_required_at_every_gate MUST be True"
            ) in joined
    assert "no_promotion_no_paper_no_live MUST be True" in joined
    assert ("differentiation_from_each_rejected_family MUST explicitly"
            " address all 9 rejected families") in joined


# ---- morning report template ---------------------------------------------

def test_morning_report_template_is_non_committed_and_pre_filled():
    mr = _R["morning_autopilot_report_template"]
    assert mr["report_kind"] == (
        "overnight_autopilot_morning_report_template_v1")
    assert mr["is_a_committed_report"] is False
    assert mr["is_a_promotion"] is False
    assert mr["is_a_winner_claim"] is False
    assert mr["report_is_research_only"] is True
    assert mr["report_authorizes_nothing"] is True
    assert mr["report_is_not_a_profitability_claim"] is True
    pf = mr["pre_filled_structural_fields"]
    assert pf["ledger_status_nine_records"] == [
        "REJECTED_KEPT_ON_RECORD"] * 9
    assert pf["v5_blacklist_length"] == 9
    assert pf["v5_blacklist_families"] == _R["v5_blacklist"]
    assert pf["current_open_gate"] == (
        "HUMAN_DECISION_DRAFT_CANDIDATE_10_FAMILY_PROPOSAL_USING"
        "_V5_BLACKLIST")
    assert pf["next_human_gate"] == pf["current_open_gate"]
    for lock_key in ("no_profitability_claim_lock",
                     "no_paper_approval_lock",
                     "no_live_approval_lock",
                     "no_winner_wording_lock",
                     "no_execution_lock", "no_auto_commit_lock",
                     "no_auto_push_lock"):
        assert pf[lock_key] is True, lock_key


def test_morning_report_banned_tokens_present():
    banned = tuple(_R["morning_autopilot_report_template"][
        "banned_tokens_in_next_human_gate"])
    for token in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                  "EXECUTION", "BACKTEST", "BASELINE", "PAPER",
                  "LIVE", "BROKER", "EXCHANGE", "AUTOMATION", "ORDER",
                  "TRACK"):
        assert token in banned, token


# ---- hard locks + downstream gates locked --------------------------------

def test_hard_locks_present():
    locks = _R["hard_locks"]
    for required in (
            "no_c10_proposal_committed_in_this_gate",
            "no_c10_proposal_drafting_beyond_placeholder_template",
            "no_real_candle_detection", "no_dry_run_detection",
            "no_replay", "no_relabel", "no_pnl_computation",
            "no_data_fetch", "no_api_call", "no_network_call",
            "no_credentials_use", "no_wallet_use", "no_account_use",
            "no_paper_trading", "no_micro_live", "no_live_trading",
            "no_broker_interaction", "no_exchange_interaction",
            "no_order_logic", "no_portfolio_logic",
            "no_scheduler_start", "no_notifications",
            "no_runner_generation", "no_data_artifact_generation",
            "no_detection_file_generation",
            "no_replay_file_generation",
            "no_trading_file_generation",
            "no_staging", "no_commit", "no_push",
            "no_auto_promotion", "no_human_review_bypass",
            "no_winner_wording", "no_profitability_claim"):
        assert required in locks, required


def test_no_downstream_unlocks_or_c10_generation():
    assert _R["human_review_required"] is True
    assert _R["paper_trading_gate_locked"] is True
    assert _R["micro_live_gate_locked"] is True
    assert _R["live_gate_locked"] is True
    for key in ("executes", "writes_files",
                "runs_detector", "runs_real_candle_detection",
                "runs_dry_run_detection", "runs_relabel",
                "runs_replay", "labels_now",
                "runs_real_detection_now", "runs_replay_now",
                "scores_now", "stages_data_now", "fetches_data",
                "calls_api", "uses_network", "uses_credentials",
                "uses_wallet", "uses_account", "connects_broker",
                "connects_exchange", "uses_real_money",
                "contains_order_logic",
                "contains_portfolio_allocation_logic",
                "starts_scheduler", "sends_notifications",
                "auto_commits", "auto_pushes",
                "creates_runners_now",
                "creates_data_artifacts_now",
                "creates_detector_implementation_now",
                "modifies_staged_market_data",
                "drafts_c10_proposal_contract_now",
                "commits_c10_proposal_now",
                "approves_c10_proposal_now",
                "generates_morning_report_now",
                "authorizes_paper_execution",
                "authorizes_micro_live", "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate",
                "claims_profitability", "bypasses_human_review",
                "uses_external_data_source"):
        assert _R[key] is False, key
        tampered = copy.deepcopy(_R)
        tampered[key] = True
        assert (drafter
            .validate_overnight_autopilot_next_candidate_proposal_drafter(
                tampered))["valid"] is False, key


def test_next_required_action_no_banned_tokens():
    assert _R["next_required_action"] == (
        "HUMAN_DECISION_DRAFT_CANDIDATE_10_FAMILY_PROPOSAL_USING_V5"
        "_BLACKLIST")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH",
                   "EXECUTE", "EXECUTION", "BACKTEST", "BASELINE",
                   "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in drafter.NEXT_REQUIRED_ACTION.upper(), (
            banned)


def test_label_text_locks_and_mode():
    assert drafter.get_drafter_label() == drafter.DRAFTER_LABEL
    assert drafter.DRAFTER_MODE == "RESEARCH_ONLY"
    for phrase in ("READ-ONLY", "RESEARCH ONLY", "NO EXECUTION",
                   "NO TRADING", "NO AUTO-PUSH", "NO SCHEDULER",
                   "NOT A PROFITABILITY CLAIM"):
        assert phrase in drafter.DRAFTER_LABEL, phrase
    for banned_phrase in ("WINNER", "PROFITABLE",
                          "EDGE CONFIRMED",
                          "APPROVED FOR PAPER",
                          "APPROVED FOR LIVE"):
        assert banned_phrase not in drafter.DRAFTER_LABEL.upper(), (
            banned_phrase)


# ---- validate_c10_proposal_draft enforcement -----------------------------

def _valid_c10_draft():
    """A fully-filled hypothetical C10 draft that passes the
    validator. Uses placeholder text 'tbd_hypothetical_c10_family'
    as the family label so the test never references a real
    family idea (the human decides that, not the test)."""
    diff = {family: "differentiated_by_test_only_not_a_real_proposal"
            for family in _R["v5_blacklist"]}
    return {
        "proposed_family_label": "tbd_hypothetical_c10_family",
        "hypothesis_statement": "test_only_hypothesis",
        "edge_source_hypothesis": "test_only_edge_source",
        "explicit_edge_argument_beyond_pattern_geometry":
            "test_only_explicit_edge_argument",
        "joint_or_intersection_trigger_sample_size_pre"
        "_justification":
            "test_only_joint_trigger_pre_justification",
        "universe_proposal": "test_only_universe",
        "timeframe_proposal": "test_only_timeframe",
        "direction_proposal": "test_only_direction",
        "fee_assumption_round_trip_bps": 27,
        "minimum_gross_target_distance_floor_bps": 81,
        "sample_window_proposal": "test_only_sample_window",
        "differentiation_from_each_rejected_family": diff,
        "explicit_non_reuse_of_rejected_family_logic":
            "test_only_non_reuse_statement",
        "anti_cluster_protection_at_proposal_time":
            "test_only_anti_cluster",
        "sample_size_adequacy_assessment_at_proposal_time":
            "test_only_sample_size_assessment",
        "rationale_paragraph": "test_only_rationale",
        "human_review_required_at_every_gate": True,
        "no_promotion_no_paper_no_live": True,
        "next_human_gate":
            "HUMAN_DECISION_REVIEW_C10_FAMILY_PROPOSAL_DRAFT",
    }


def test_validate_c10_draft_passes_on_valid_input():
    result = drafter.validate_c10_proposal_draft(_valid_c10_draft())
    assert result["valid"] is True, result["errors"]


def test_validate_c10_draft_rejects_v5_blacklisted_label():
    for blacklisted in _R["v5_blacklist"]:
        d = _valid_c10_draft()
        d["proposed_family_label"] = blacklisted
        result = drafter.validate_c10_proposal_draft(d)
        assert result["valid"] is False
        assert "proposed_family_label_in_v5_blacklist" in result[
            "errors"], blacklisted


def test_validate_c10_draft_rejects_wrong_fee_or_floor():
    for bad_fee in (0, 1, 5, 10, 20, 26, 28, 50, 100):
        d = _valid_c10_draft()
        d["fee_assumption_round_trip_bps"] = bad_fee
        result = drafter.validate_c10_proposal_draft(d)
        assert result["valid"] is False
        assert "fee_assumption_must_equal_27_bps" in result["errors"]
    for bad_floor in (0, 1, 27, 50, 80, 82, 100, 200):
        d = _valid_c10_draft()
        d["minimum_gross_target_distance_floor_bps"] = bad_floor
        result = drafter.validate_c10_proposal_draft(d)
        assert result["valid"] is False
        assert "floor_must_equal_81_bps" in result["errors"]


def test_validate_c10_draft_rejects_missing_differentiation():
    d = _valid_c10_draft()
    d["differentiation_from_each_rejected_family"] = {
        "ny_session_fvg_choch_v3": "x"}
    result = drafter.validate_c10_proposal_draft(d)
    assert result["valid"] is False
    assert any(e.startswith("differentiation_missing_families:")
               for e in result["errors"])


def test_validate_c10_draft_rejects_placeholders():
    for field in ("hypothesis_statement", "edge_source_hypothesis",
                  "explicit_edge_argument_beyond_pattern_geometry",
                  "anti_cluster_protection_at_proposal_time",
                  "sample_size_adequacy_assessment_at_proposal_time",
                  "rationale_paragraph"):
        d = _valid_c10_draft()
        d[field] = "TO_BE_FILLED_BY_HUMAN_REVIEW"
        result = drafter.validate_c10_proposal_draft(d)
        assert result["valid"] is False
        assert ("required_field_still_placeholder:" + field) in (
            result["errors"]), field


def test_validate_c10_draft_rejects_human_review_bypass():
    d = _valid_c10_draft()
    d["human_review_required_at_every_gate"] = False
    result = drafter.validate_c10_proposal_draft(d)
    assert result["valid"] is False
    assert "human_review_required_must_be_true" in result["errors"]


def test_validate_c10_draft_rejects_promotion_paper_live_flag():
    d = _valid_c10_draft()
    d["no_promotion_no_paper_no_live"] = False
    result = drafter.validate_c10_proposal_draft(d)
    assert result["valid"] is False
    assert "no_promotion_no_paper_no_live_must_be_true" in result[
        "errors"]


def test_validate_c10_draft_rejects_banned_tokens_in_next_human_gate():
    for banned in ("PROMOTE", "UNLOCK", "EXECUTE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "ORDER"):
        d = _valid_c10_draft()
        d["next_human_gate"] = (
            f"HUMAN_DECISION_{banned}_C10_FAMILY_PROPOSAL")
        result = drafter.validate_c10_proposal_draft(d)
        assert result["valid"] is False
        assert ("next_human_gate_has_banned_token:" + banned) in (
            result["errors"]), banned


def test_validate_c10_draft_rejects_non_dict():
    assert drafter.validate_c10_proposal_draft(None)["valid"] is False
    assert drafter.validate_c10_proposal_draft([])["valid"] is False
    assert drafter.validate_c10_proposal_draft("x")["valid"] is False
    assert drafter.validate_c10_proposal_draft(42)["valid"] is False


# ---- module purity --------------------------------------------------------

def test_module_purity_no_banned_imports_no_open_no_main():
    src = open(drafter.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir",
                 "rmdir", "rename", "touch("):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned_mods = {"urllib", "requests", "socket", "http", "ccxt",
                   "smtplib", "subprocess", "websockets", "aiohttp",
                   "schedule", "apscheduler", "threading", "asyncio",
                   "time", "sched", "telegram", "email", "csv",
                   "pandas", "pathlib", "os", "io", "json", "shutil",
                   "databento", "ssl", "ftplib", "hashlib",
                   "datetime", "statistics", "random"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods), imported & banned_mods
    for call in ast.walk(tree):
        if not isinstance(call, ast.Call):
            continue
        name = (call.func.attr if isinstance(call.func, ast.Attribute)
                else getattr(call.func, "id", ""))
        assert name not in ("open", "exec", "eval", "compile"), name
