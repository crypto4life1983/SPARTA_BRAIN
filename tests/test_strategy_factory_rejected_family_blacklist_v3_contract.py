"""Tests for the Rejected Family Blacklist V3 contract.

Verifies: seven-record ledger gates the build; V3 contains exactly 7
families (V2's 6 + the new C7 entry `volatility_compression
_expansion`); V2 blacklist remains a strict subset of V3; per-family
rejection reasons are pinned; C8 proposal requirements include all
seven differentiation targets and the inherited lessons; fee/floor/
anti-cluster/sample-size requirements held; downstream gates locked;
no Candidate #8 generation in this gate; no trading-adjacent
capability; AST/purity green. Commander safety suite runs alongside
(12 tests)."""

from __future__ import annotations

import ast

import sparta_commander.strategy_factory_overnight_research_autopilot_v2_contract as oap2
import sparta_commander.strategy_factory_rejected_family_blacklist_v3_contract as bl3
import sparta_commander.volatility_compression_expansion_v1_rejection_record as rj7


def _record():
    return bl3.build_rejected_family_blacklist_v3()


# (1) V3 passes when all 7 rejection records are live ----------------------

def test_1_v3_passes_when_seven_record_ledger_holds():
    record = _record()
    assert record["verdict"] == bl3.VERDICT_BL3_READY
    assert record["blockers"] == []
    assert bl3.validate_rejected_family_blacklist_v3(
        record)["valid"] is True
    assert record["ledger_all_rejected_kept_on_record"] is True
    assert list(record["ledger_status_seven_records"]) == [
        "REJECTED_KEPT_ON_RECORD"] * 7
    # determinism
    assert _record() == record


# (2) blacklist contains exactly 7 families --------------------------------

def test_2_blacklist_contains_exactly_seven_families():
    record = _record()
    assert record["blacklist_length"] == 7
    blacklist = tuple(record["rejected_family_logic_blacklist_v3"])
    assert blacklist == (
        "ny_session_fvg_choch_v3",
        "crypto_intraday_breakout_pullback_structure_v2",
        "btc_sol_long_trend_continuation_v1",
        "sol_btc_long_1h_swing_structure",
        "eth_sol_relative_strength_pullback_continuation_v1",
        "multi_symbol_relative_strength_rotation_filter",
        "volatility_compression_expansion")
    assert len(set(blacklist)) == 7  # unique
    assert record["new_entry_added"] == "volatility_compression_expansion"


# (3) V2 blacklist is a strict subset of V3 -------------------------------

def test_3_v2_blacklist_is_strict_subset_of_v3():
    record = _record()
    v2 = set(record["prior_v2_blacklist"])
    v3 = set(record["rejected_family_logic_blacklist_v3"])
    assert v2.issubset(v3)
    assert v3 - v2 == {"volatility_compression_expansion"}
    assert len(v3) == len(v2) + 1
    # the prior V2 blacklist exactly mirrors the pushed V2 contract
    assert tuple(record["prior_v2_blacklist"]) == tuple(
        oap2.REJECTED_FAMILY_LOGIC_BLACKLIST)


# (4) blocks if any C1-C7 ledger entry is not REJECTED_KEPT_ON_RECORD ----

def test_4_blocks_if_any_ledger_entry_drifts():
    import sparta_commander.strategy_factory_rejected_family_blacklist_v3_contract as mod
    originals = {key: getattr(mod, key) for key in
                 ("C1_STATUS", "C2_STATUS", "C3_STATUS", "C4_STATUS",
                  "C5_STATUS", "C6_STATUS", "C7_STATUS")}
    try:
        for key in originals:
            for replacement in ("APPROVED_FOR_TRADING", "PENDING", ""):
                setattr(mod, key, replacement)
                record = mod.build_rejected_family_blacklist_v3()
                assert record["verdict"] == bl3.VERDICT_BL3_BLOCKED, (
                    key, replacement)
                assert "seven_record_ledger_broken" in record[
                    "blockers"]
            setattr(mod, key, originals[key])
    finally:
        for key, value in originals.items():
            setattr(mod, key, value)
    # baseline restored
    assert mod.build_rejected_family_blacklist_v3()["verdict"] == (
        bl3.VERDICT_BL3_READY)


# (5) per-family rejection reasons frozen --------------------------------

def test_5_per_family_rejection_reasons_pinned():
    record = _record()
    reasons = record["per_family_rejection_reason"]
    assert set(reasons) == set(bl3.LEDGER_KEYS)
    # Specific phrasing from each rejection rationale
    assert "session-anchored" in reasons["C1"]
    assert "pullback-after-breakout" in reasons["C2"]
    assert "trend continuation" in reasons["C3"]
    assert "swing-structure" in reasons["C4"]
    assert "trigger-window extension" in reasons["C5"]
    assert "clustering filter" in reasons["C6"]
    assert "zero accepted real-candle setups" in reasons["C7"]
    assert "2026-05-02_2026-06-10" in reasons["C7"]


# (6) C8 proposal requirements include all seven differentiation targets -

def test_6_c8_proposal_requirements_include_all_seven_targets():
    record = _record()
    reqs = record["c8_proposal_requirements"]
    targets = reqs["differentiation_must_address_each_of"]
    assert tuple(targets) == (
        "ny_session_fvg_choch_v3",
        "crypto_intraday_breakout_pullback_structure_v2",
        "btc_sol_long_trend_continuation_v1",
        "sol_btc_long_1h_swing_structure",
        "eth_sol_relative_strength_pullback_continuation_v1",
        "multi_symbol_relative_strength_rotation_filter",
        "volatility_compression_expansion")
    assert tuple(reqs["rejected_family_logic_blacklist"]) == (
        tuple(record["rejected_family_logic_blacklist_v3"]))
    required_fields = reqs["required_fields"]
    for field in ("proposed_family_label", "hypothesis_statement",
                  "edge_source_hypothesis", "universe_proposal",
                  "timeframe_proposal", "direction_proposal",
                  "fee_assumption_round_trip_bps",
                  "minimum_gross_target_distance_floor_bps",
                  "sample_window_proposal",
                  "differentiation_from_each_rejected_family",
                  "explicit_non_reuse_of_rejected_family_logic",
                  "anti_cluster_protection_at_proposal_time",
                  "sample_size_adequacy_assessment_at_proposal_time",
                  "rationale_paragraph",
                  "human_review_required_at_every_gate",
                  "no_promotion_no_paper_no_live"):
        assert field in required_fields, field


# (7) 27 bps fee + 81 bps floor + anti-cluster + sample-size locked -----

def test_7_c8_must_keep_27_bps_fee_and_81_bps_floor_and_protections():
    record = _record()
    reqs = record["c8_proposal_requirements"]
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
    # tampering any of these flags rejects the record
    for key in ("fee_assumption_must_equal_27_bps_round_trip",
                "minimum_floor_must_equal_81_bps",
                "anti_cluster_protection_must_be_built_in_at_proposal"
                "_time",
                "sample_size_adequacy_must_be_assessed_at_proposal"
                "_time",
                "must_not_reuse_any_rejected_family_logic"):
        tampered = _record()
        tampered["c8_proposal_requirements"] = dict(
            tampered["c8_proposal_requirements"], **{key: False})
        assert bl3.validate_rejected_family_blacklist_v3(
            tampered)["valid"] is False, key


# (8) inherited lessons include C6 anti-cluster and C7 sample-size ------

def test_8_inherited_lessons_include_c6_and_c7():
    lessons = _record()["inherited_lessons"]
    joined = " || ".join(lessons)
    # one lesson per rejected candidate
    for key in ("c1_lesson", "c2_lesson", "c3_lesson", "c4_lesson",
                "c5_lesson", "c6_lesson", "c7_lesson"):
        assert key + ":" in joined, key
    # the C6 lesson must reference anti-cluster protection at proposal
    # time
    assert "anti-cluster protection at proposal time" in joined
    # the C7 lesson must reference sample-size adequacy at proposal
    # time
    assert "sample-size adequacy assessment at proposal time" in joined


# (9) downstream gates remain locked + no C8 generation ----------------

def test_9_downstream_gates_locked_and_no_c8_generation():
    record = _record()
    assert record["paper_trading_gate_locked"] is True
    assert record["micro_live_gate_locked"] is True
    assert record["live_gate_locked"] is True
    for key in ("generates_candidate_8_proposal_now",
                "drafts_candidate_8_in_this_gate",
                "generates_morning_report_now",
                "runs_detector", "runs_real_candle_detection",
                "runs_relabel", "runs_replay",
                "fetches_data", "calls_api", "uses_network",
                "uses_credentials", "uses_wallet", "uses_account",
                "connects_broker", "connects_exchange",
                "uses_real_money", "contains_order_logic",
                "contains_portfolio_allocation_logic",
                "starts_scheduler", "sends_notifications",
                "auto_commits", "auto_pushes",
                "authorizes_paper_execution",
                "authorizes_micro_live",
                "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate",
                "claims_profitability"):
        assert record[key] is False, key
        tampered = _record()
        tampered[key] = True
        assert bl3.validate_rejected_family_blacklist_v3(
            tampered)["valid"] is False, key
    locks = record["claim_locks"]
    for lock in ("no_profitability_claim",
                 "no_candidate_8_generation_in_this_gate",
                 "no_candidate_8_proposal_drafting_in_this_gate",
                 "no_auto_commit", "no_auto_push"):
        assert lock in locks, lock


# (10) C7 rejection status / reason / blacklist addition source-of-truth -

def test_10_c7_rejection_status_and_blacklist_addition_pinned():
    record = _record()
    assert record["c7_rejection_status"] == "REJECTED_KEPT_ON_RECORD"
    assert record["c7_rejection_status"] == rj7.REJECTION_STATUS
    assert record["c7_rejection_reason"] == rj7.REJECTION_REASON
    assert record["c7_future_family_blacklist_addition"] == (
        rj7.FUTURE_FAMILY_BLACKLIST_ADDITION)
    assert record["new_entry_added"] == (
        record["c7_future_family_blacklist_addition"])
    # tampering rejects
    bad = _record()
    bad["c7_rejection_status"] = "APPROVED"
    assert bl3.validate_rejected_family_blacklist_v3(
        bad)["valid"] is False
    bad2 = _record()
    bad2["new_entry_added"] = "some_other_family"
    assert bl3.validate_rejected_family_blacklist_v3(
        bad2)["valid"] is False


# (11) blacklist v3 tamper rejects, length must remain 7 ----------------

def test_11_blacklist_tampering_rejects_validation():
    for mutation in (
            [], ["only_one"],
            list(bl3.REJECTED_FAMILY_LOGIC_BLACKLIST_V3) + ["extra"],
            list(bl3.REJECTED_FAMILY_LOGIC_BLACKLIST_V3[:6])):
        tampered = _record()
        tampered["rejected_family_logic_blacklist_v3"] = mutation
        assert bl3.validate_rejected_family_blacklist_v3(
            tampered)["valid"] is False, mutation
    # blacklist_length must equal 7 specifically
    tampered = _record()
    tampered["blacklist_length"] = 6
    assert bl3.validate_rejected_family_blacklist_v3(
        tampered)["valid"] is False


# (12) AST/purity --------------------------------------------------------

def test_12_ast_purity_and_no_writers_or_runners():
    assert bl3.get_blacklist_v3_label() == bl3.BL3_LABEL
    assert bl3.BL3_MODE == "RESEARCH_ONLY"
    assert bl3.VERDICT_BL3_READY == (
        "STRATEGY_FACTORY_REJECTED_FAMILY_BLACKLIST_V3_READY")
    assert bl3.NEXT_REQUIRED_ACTION == (
        "HUMAN_DECISION_DRAFT_CANDIDATE_8_FAMILY_PROPOSAL_USING_V3"
        "_BLACKLIST")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in bl3.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(bl3.__file__, encoding="utf-8").read()
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
