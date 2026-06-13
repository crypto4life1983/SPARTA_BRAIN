"""Tests for the Strategy Factory Rejected Family Blacklist V4
contract (extends V3 with the C8 family rejection).

Verifies: chain-gate on the eight-record ledger + C8 rejection record
+ V3 + V2 + Recommendation V1 + Autopilot V1; eight-family blacklist;
V3 is a strict subset of V4 with exactly +1 entry; new entry =
liquidity_sweep_mean_reversion; C9 proposal requirements include the
new C8 lesson (explicit-edge-argument-beyond-pattern-geometry);
inherited lessons C1-C8; downstream execution surface remains
locked; AST/purity green."""

from __future__ import annotations

import ast

import sparta_commander.liquidity_sweep_mean_reversion_v1_rejection_record as rj8
import sparta_commander.strategy_factory_autopilot_research_loop_v1_contract as ap
import sparta_commander.strategy_factory_candidate_recommendation_v1_contract as rec
import sparta_commander.strategy_factory_overnight_research_autopilot_v2_contract as oap2
import sparta_commander.strategy_factory_rejected_family_blacklist_v3_contract as bl3
import sparta_commander.strategy_factory_rejected_family_blacklist_v4_contract as bl4


def _record():
    return bl4.build_rejected_family_blacklist_v4()


# ---- chain gate + ready verdict -------------------------------------------

def test_blacklist_v4_ready_and_chain_gates_all_certify():
    assert rj8.build_c8_rejection_record()["verdict"] == (
        rj8.VERDICT_RJ8_RECORDED)
    assert bl3.build_rejected_family_blacklist_v3()["verdict"] == (
        bl3.VERDICT_BL3_READY)
    assert oap2.build_overnight_research_autopilot_v2_contract()[
        "verdict"] == oap2.VERDICT_OAP2_READY
    assert rec.build_candidate_recommendation()["verdict"] == (
        rec.VERDICT_CR_READY)
    assert ap.build_autopilot_loop_contract()["verdict"] == (
        ap.VERDICT_AP_READY)
    record = _record()
    assert record["verdict"] == bl4.VERDICT_BL4_READY
    assert record["blockers"] == []
    assert bl4.validate_rejected_family_blacklist_v4(
        record)["valid"] is True


def test_eight_record_ledger_intact():
    record = _record()
    assert record["ledger_status_eight_records"] == [
        "REJECTED_KEPT_ON_RECORD"] * 8
    assert record["ledger_all_rejected_kept_on_record"] is True


def test_chain_blocks_when_ledger_breaks():
    import sparta_commander.strategy_factory_rejected_family_blacklist_v4_contract as mod
    originals = {k: getattr(mod, k) for k in
                 ("C1_STATUS", "C2_STATUS", "C3_STATUS",
                  "C4_STATUS", "C5_STATUS", "C6_STATUS",
                  "C7_STATUS", "C8_STATUS")}
    try:
        for key in originals:
            setattr(mod, key, "APPROVED_FOR_TRADING")
            record = mod.build_rejected_family_blacklist_v4()
            assert record["verdict"] == bl4.VERDICT_BL4_BLOCKED, key
            assert "eight_record_ledger_broken" in record[
                "blockers"], key
            setattr(mod, key, originals[key])
    finally:
        for k, v in originals.items():
            setattr(mod, k, v)
    assert mod.build_rejected_family_blacklist_v4()["verdict"] == (
        bl4.VERDICT_BL4_READY)


# ---- eight-family blacklist + V3 strict-subset --------------------------

def test_blacklist_has_eight_families_and_includes_c8():
    record = _record()
    blacklist = tuple(record["rejected_family_logic_blacklist_v4"])
    assert len(blacklist) == 8
    assert record["blacklist_length"] == 8
    assert "liquidity_sweep_mean_reversion" in blacklist
    assert record["new_entry_added"] == (
        "liquidity_sweep_mean_reversion")
    for expected_family in (
            "ny_session_fvg_choch_v3",
            "crypto_intraday_breakout_pullback_structure_v2",
            "btc_sol_long_trend_continuation_v1",
            "sol_btc_long_1h_swing_structure",
            "eth_sol_relative_strength_pullback_continuation_v1",
            "multi_symbol_relative_strength_rotation_filter",
            "volatility_compression_expansion",
            "liquidity_sweep_mean_reversion"):
        assert expected_family in blacklist, expected_family


def test_v3_strict_subset_of_v4_with_exactly_one_new_entry():
    record = _record()
    prior_v3 = set(record["prior_v3_blacklist"])
    v4 = set(record["rejected_family_logic_blacklist_v4"])
    assert prior_v3.issubset(v4)
    assert v4 - prior_v3 == {"liquidity_sweep_mean_reversion"}
    assert len(v4) == len(prior_v3) + 1


def test_c8_rejection_status_and_reason_carried_forward():
    record = _record()
    assert record["c8_rejection_status"] == "REJECTED_KEPT_ON_RECORD"
    assert "ALL_REPLAY_VARIANTS" in record["c8_rejection_reason"]
    assert "NET_NEGATIVE" in record["c8_rejection_reason"]
    assert "EDIT_TOKEN_NOT_SPENT" in record["c8_rejection_reason"]
    assert record["c8_future_family_blacklist_addition"] == (
        "liquidity_sweep_mean_reversion")


# ---- per-family rejection reasons ----------------------------------------

def test_per_family_rejection_reason_complete_for_c1_through_c8():
    reasons = _record()["per_family_rejection_reason"]
    for key in ("C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8"):
        assert key in reasons, key
        assert len(reasons[key]) > 50, key
    c8 = reasons["C8"]
    assert "liquidity sweep mean reversion" in c8
    assert "51 accepted-post-anti-cluster" in c8
    assert "2R net = -45.78" in c8
    assert "3R = -58.84" in c8
    assert "4R = -65.78" in c8
    assert "single edit token NOT spent" in c8


def test_ledger_family_labels_complete():
    labels = _record()["ledger_family_labels"]
    assert labels == {
        "C1": "ny_session_fvg_choch_v3",
        "C2": "crypto_intraday_breakout_pullback_structure_v2",
        "C3": "btc_sol_long_trend_continuation_v1",
        "C4": "sol_btc_long_1h_swing_structure",
        "C5": "eth_sol_relative_strength_pullback_continuation_v1",
        "C6": "multi_symbol_relative_strength_rotation_filter",
        "C7": "volatility_compression_expansion",
        "C8": "liquidity_sweep_mean_reversion"}


# ---- C9 proposal requirements --------------------------------------------

def test_c9_proposal_requirements_include_c8_lesson():
    record = _record()
    reqs = record["c9_proposal_requirements"]
    assert "explicit_edge_argument_beyond_pattern_geometry" in (
        reqs["required_fields"])
    assert reqs[
        "explicit_edge_argument_beyond_pattern_geometry_required"
    ] is True
    assert reqs[
        "fee_assumption_must_equal_27_bps_round_trip"] is True
    assert reqs["minimum_floor_must_equal_81_bps"] is True
    assert reqs[
        "anti_cluster_protection_must_be_built_in_at_proposal_time"
    ] is True
    assert reqs[
        "sample_size_adequacy_must_be_assessed_at_proposal_time"
    ] is True
    assert reqs["must_not_reuse_any_rejected_family_logic"] is True
    assert reqs["human_review_required_at_every_gate"] is True
    assert reqs["plan_is_not_a_promotion"] is True
    # differentiation must address every rejected family (incl. C8)
    diff_targets = tuple(
        reqs["differentiation_must_address_each_of"])
    assert len(diff_targets) == 8
    assert "liquidity_sweep_mean_reversion" in diff_targets


def test_inherited_lessons_include_c8_explicit_edge_argument():
    lessons = _record()["inherited_lessons"]
    assert len(lessons) == 8
    joined = " || ".join(lessons)
    assert "c1_lesson:" in joined
    assert "c2_lesson:" in joined
    assert "c3_lesson:" in joined
    assert "c4_lesson:" in joined
    assert "c5_lesson:" in joined
    assert "c6_lesson:" in joined
    assert "c7_lesson:" in joined
    assert "c8_lesson:" in joined
    assert "EXPLICIT EDGE ARGUMENT BEYOND PATTERN GEOMETRY" in joined
    assert "structural cleanliness alone does not produce edge" in (
        joined)


# ---- downstream gates locked ---------------------------------------------

def test_no_downstream_unlocks_or_candidate_9_generation():
    record = _record()
    assert record["human_review_required"] is True
    assert record["paper_trading_gate_locked"] is True
    assert record["micro_live_gate_locked"] is True
    assert record["live_gate_locked"] is True
    for key in ("executes", "writes_files",
                "runs_detector", "runs_real_candle_detection",
                "runs_relabel", "runs_replay", "labels_now",
                "runs_real_detection_now", "runs_replay_now",
                "scores_now", "stages_data_now", "fetches_data",
                "calls_api", "uses_network", "uses_credentials",
                "uses_wallet", "uses_account", "connects_broker",
                "connects_exchange", "uses_real_money",
                "contains_order_logic",
                "contains_portfolio_allocation_logic",
                "starts_scheduler", "sends_notifications",
                "auto_commits", "auto_pushes", "creates_runners_now",
                "creates_data_artifacts_now",
                "creates_detector_implementation_now",
                "modifies_staged_market_data",
                "generates_candidate_9_proposal_now",
                "generates_morning_report_now",
                "drafts_candidate_9_in_this_gate",
                "authorizes_paper_execution", "authorizes_micro_live",
                "authorizes_live_trading", "promotes_gate",
                "unlocks_downstream_gate", "claims_profitability",
                "uses_external_data_source"):
        assert record[key] is False, key
        tampered = _record()
        tampered[key] = True
        assert bl4.validate_rejected_family_blacklist_v4(
            tampered)["valid"] is False, key


def test_claim_locks_present():
    locks = _record()["claim_locks"]
    for required in ("no_profitability_claim", "no_paper_approval",
                     "no_live_approval", "no_execution_approval",
                     "no_winner_wording", "no_promotion_by_v4",
                     "no_unlock_by_v4", "no_scheduler_activation",
                     "no_auto_commit", "no_auto_push",
                     "no_candidate_9_generation_in_this_gate",
                     "no_candidate_9_proposal_drafting_in_this_gate"):
        assert required in locks, required
    tampered = _record()
    tampered["claim_locks"] = []
    assert bl4.validate_rejected_family_blacklist_v4(
        tampered)["valid"] is False


def test_next_required_action_and_label_text():
    record = _record()
    assert record["next_required_action"] == (
        "HUMAN_DECISION_DRAFT_CANDIDATE_9_FAMILY_PROPOSAL_USING_V4"
        "_BLACKLIST")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH",
                   "EXECUTE", "EXECUTION", "BACKTEST", "BASELINE",
                   "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in bl4.NEXT_REQUIRED_ACTION.upper(), banned
    assert bl4.get_blacklist_v4_label() == bl4.BL4_LABEL
    assert bl4.BL4_MODE == "RESEARCH_ONLY"
    for phrase in ("READ-ONLY", "RESEARCH ONLY",
                   "NO EXECUTION", "NO TRADING",
                   "NO AUTO-PUSH", "NO SCHEDULER",
                   "NOT A PROFITABILITY CLAIM",
                   "EIGHT-FAMILY BLACKLIST"):
        assert phrase in bl4.BL4_LABEL, phrase


# ---- module purity --------------------------------------------------------

def test_module_purity_no_banned_imports_no_open_no_main():
    src = open(bl4.__file__, encoding="utf-8").read()
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
