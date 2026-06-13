"""Tests for the Candidate #6 real-candle labels review / evidence
freeze. Certify logic proven on synthetic observations for every failure
mode; one real-artifact test certifies the live files when present."""

from __future__ import annotations

import ast
import copy

import pytest

import sparta_commander.multi_symbol_relative_strength_rotation_filter_real_candle_labels_review_contract as c6l

REPO_ROOT = "C:/SPARTA_BRAIN"


def _good_observation():
    return {
        "labels_exists": True, "summary_exists": True,
        "labels_sha256": c6l.EXPECTED_LABELS_SHA256,
        "summary_sha256": c6l.EXPECTED_SUMMARY_SHA256,
        "labels_line_count": 389,
        "status_breakdown": dict(c6l.EXPECTED_STATUS_BREAKDOWN),
        "accepted_count": 135,
        "per_symbol_counts": copy.deepcopy({
            sym: c6l.EXPECTED_COUNTS[sym]
            for sym in ("BTCUSD", "ETHUSD", "SOLUSD")}),
        "accepted_setup_ids": c6l.EXPECTED_ACCEPTED_SETUP_IDS,
        "floor_pass_all_variants_for_all_accepted": True,
        "staged_shas_now": dict(c6l.EXPECTED_STAGED_SHAS),
        "staged_shas_match": True,
        "aggregation_counts": {sym: dict(value) for sym, value
                               in c6l.EXPECTED_AGGREGATION_COUNTS.items()},
        "alignment_status": c6l.EXPECTED_ALIGNMENT_STATUS,
        "candidate_id_in_summary": c6l.CANDIDATE_ID,
        "artifacts_tracked_in_git": [],
    }


def test_1_artifact_shas_validated_exactly():
    assert c6l.EXPECTED_LABELS_SHA256 == (
        "bc8471fc78bbfe409b5cb0efa951608cddd73f3485d66dbd8d711bb1f4307"
        "d7a")
    assert c6l.EXPECTED_SUMMARY_SHA256 == (
        "110b84b2ad96de5136d1a89da4ef26f2fbd1b4a0f45527f5e0f1a0c612fc"
        "18c7")
    bad = _good_observation()
    bad["labels_sha256"] = "00" * 32
    result = c6l.certify_c6_labels_review(bad)
    assert "labels_sha_mismatch" in result["failures"]
    bad2 = _good_observation()
    bad2["summary_sha256"] = "00" * 32
    assert "summary_sha_mismatch" in c6l.certify_c6_labels_review(
        bad2)["failures"]


def test_2_3_total_labels_389_accepted_135():
    assert c6l.EXPECTED_COUNTS["total"]["attempts"] == 389
    assert c6l.EXPECTED_COUNTS["total"]["accepted"] == 135
    assert c6l.EXPECTED_COUNTS["total"]["rejected"] == 254
    bad_total = _good_observation()
    bad_total["labels_line_count"] = 390
    assert "label_count_mismatch" in c6l.certify_c6_labels_review(
        bad_total)["failures"]
    bad_acc = _good_observation()
    bad_acc["accepted_count"] = 134
    assert "accepted_count_mismatch" in c6l.certify_c6_labels_review(
        bad_acc)["failures"]


def test_4_5_per_symbol_and_rejection_counts_exact():
    counts = c6l.EXPECTED_COUNTS
    assert counts["BTCUSD"] == {
        "attempts": 127, "accepted": 32, "rejected": 95,
        "rejected_not_strict_rank_1": 85,
        "rejected_rs_not_positive": 10,
        "floor_pass_2r": 32, "floor_pass_3r": 32,
        "floor_pass_4r": 32, "floor_fail": 0}
    assert counts["ETHUSD"] == {
        "attempts": 130, "accepted": 32, "rejected": 98,
        "rejected_not_strict_rank_1": 88,
        "rejected_rs_not_positive": 10,
        "floor_pass_2r": 32, "floor_pass_3r": 32,
        "floor_pass_4r": 32, "floor_fail": 0}
    assert counts["SOLUSD"] == {
        "attempts": 132, "accepted": 71, "rejected": 61,
        "rejected_not_strict_rank_1": 58,
        "rejected_rs_not_positive": 3,
        "floor_pass_2r": 71, "floor_pass_3r": 71,
        "floor_pass_4r": 71, "floor_fail": 0}
    for sym in ("BTCUSD", "ETHUSD", "SOLUSD"):
        c = counts[sym]
        assert c["accepted"] + c["rejected"] == c["attempts"]
        assert c["rejected_not_strict_rank_1"] + c[
            "rejected_rs_not_positive"] == c["rejected"]
    # totals reconcile
    for field in ("attempts", "accepted", "rejected",
                  "rejected_not_strict_rank_1",
                  "rejected_rs_not_positive",
                  "floor_pass_2r", "floor_pass_3r", "floor_pass_4r",
                  "floor_fail"):
        assert (counts["BTCUSD"][field] + counts["ETHUSD"][field]
                + counts["SOLUSD"][field]) == counts["total"][field], (
            field)
    assert c6l.EXPECTED_STATUS_BREAKDOWN == {
        "accepted_for_replay_review": 135,
        "rejected_not_strict_rank_1": 231,
        "rejected_rs_not_positive": 23}
    assert sum(c6l.EXPECTED_STATUS_BREAKDOWN.values()) == 389
    # per-symbol tamper
    bad = _good_observation()
    bad["per_symbol_counts"]["BTCUSD"]["accepted"] = 33
    assert "per_symbol_counts_mismatch:BTCUSD" in (
        c6l.certify_c6_labels_review(bad)["failures"])
    # status breakdown tamper
    bad2 = _good_observation()
    bad2["status_breakdown"]["rejected_rs_not_positive"] = 24
    assert "status_breakdown_mismatch" in (
        c6l.certify_c6_labels_review(bad2)["failures"])


def test_6_7_floor_pass_135_135_135_and_zero_fail():
    counts = c6l.EXPECTED_COUNTS["total"]
    assert counts["floor_pass_2r"] == 135
    assert counts["floor_pass_3r"] == 135
    assert counts["floor_pass_4r"] == 135
    assert counts["floor_fail"] == 0
    bad = _good_observation()
    bad["floor_pass_all_variants_for_all_accepted"] = False
    assert "accepted_set_must_pass_all_variant_floors" in (
        c6l.certify_c6_labels_review(bad)["failures"])


def test_8_six_staged_shas_validated_exactly():
    shas = c6l.EXPECTED_STAGED_SHAS
    assert len(shas) == 6
    pinned = {
        "BTCUSD_15m_2026-05-02_2026-06-09.csv":
            "4ee373b28caeafa47d463e0fc2582f1958b877a8f05df0714a0afd1"
            "298ee9f14",
        "BTCUSD_15m_2026-06-01_2026-06-10.csv":
            "4bb50873df5194de65315bf44f1823d17922e445745401eb01aa167"
            "0aed4956d",
        "ETHUSD_15m_2026-05-02_2026-06-09.csv":
            "2d96b6a1ed82293fc63fecf2f1948fd1990e0a1b42827670d6fcdce"
            "9abd6f980",
        "ETHUSD_15m_2026-06-01_2026-06-10.csv":
            "bc7e86f1e2294b2a826675eb80ee51f95a4f2b5ef55212eadad9247"
            "1668755f1",
        "SOLUSD_15m_2026-05-02_2026-06-09.csv":
            "f782856870d5d5652f3a42c619419fc56f90e89fdf5b036a56eeb34"
            "7aee2f884",
        "SOLUSD_15m_2026-06-01_2026-06-10.csv":
            "3437bf5d580f71108a1f5034104955eaf5d4bb4cd2255ea0dcd625c"
            "7b15b2f65",
    }
    for name, expected in pinned.items():
        key = "data/ny_fvg_choch/staged/" + name
        assert shas[key] == expected, name
    bad = _good_observation()
    bad["staged_shas_match"] = False
    assert "staged_data_shas_changed" in (
        c6l.certify_c6_labels_review(bad)["failures"])


def test_9_aggregation_counts_exact():
    assert c6l.EXPECTED_AGGREGATION_COUNTS == {
        "BTCUSD": {"bars_15m": 3840, "bars_1h": 960},
        "ETHUSD": {"bars_15m": 3840, "bars_1h": 960},
        "SOLUSD": {"bars_15m": 3840, "bars_1h": 960}}
    bad = _good_observation()
    bad["aggregation_counts"]["BTCUSD"] = {"bars_15m": 0, "bars_1h": 0}
    assert "aggregation_counts_mismatch" in (
        c6l.certify_c6_labels_review(bad)["failures"])


def test_10_alignment_status_exact():
    assert c6l.EXPECTED_ALIGNMENT_STATUS == (
        "aligned_across_btcusd_ethusd_solusd")
    bad = _good_observation()
    bad["alignment_status"] = "misaligned"
    assert "alignment_status_mismatch" in (
        c6l.certify_c6_labels_review(bad)["failures"])


def test_11_135_accepted_setup_ids_frozen_and_deterministic():
    ids = c6l.EXPECTED_ACCEPTED_SETUP_IDS
    assert isinstance(ids, tuple)  # immutable
    assert len(ids) == 135
    assert len(set(ids)) == 135  # unique
    assert list(ids) == sorted(ids)  # deterministic ordering
    assert sum(1 for sid in ids if sid.startswith("BTCUSD")) == 32
    assert sum(1 for sid in ids if sid.startswith("ETHUSD")) == 32
    assert sum(1 for sid in ids if sid.startswith("SOLUSD")) == 71
    bad = _good_observation()
    bad["accepted_setup_ids"] = tuple(list(ids) + ["EXTRA"])
    assert "accepted_setup_ids_mismatch" in (
        c6l.certify_c6_labels_review(bad)["failures"])
    extra_symbol = _good_observation()
    extra_symbol["per_symbol_counts"]["DOGEUSD"] = {
        "attempts": 1, "accepted": 0, "rejected": 1,
        "rejected_not_strict_rank_1": 1,
        "rejected_rs_not_positive": 0,
        "floor_pass_2r": 0, "floor_pass_3r": 0,
        "floor_pass_4r": 0, "floor_fail": 0}
    assert "unexpected_symbols_in_labels" in (
        c6l.certify_c6_labels_review(extra_symbol)["failures"])


def test_12_full_chain_certifies_live():
    import sparta_commander.multi_symbol_relative_strength_rotation_filter_dry_run_review_contract as c6r
    import sparta_commander.multi_symbol_relative_strength_rotation_filter_detector_spec_contract as c6d
    import sparta_commander.multi_symbol_relative_strength_rotation_filter_spec_review_contract as c6s
    import sparta_commander.multi_symbol_relative_strength_rotation_filter_family_proposal_contract as c6p
    import sparta_commander.strategy_factory_candidate_recommendation_v1_contract as cr
    import sparta_commander.strategy_factory_autopilot_research_loop_v1_contract as ap
    assert c6p.build_candidate_6_family_proposal()["verdict"] == (
        "CANDIDATE_6_FAMILY_PROPOSAL_READY")
    assert c6s.build_candidate_6_spec_review()["verdict"] == (
        "CANDIDATE_6_SPEC_REVIEW_READY")
    assert c6d.build_c6_detector_spec_contract()["verdict"] == (
        "CANDIDATE_6_DETECTOR_SPEC_READY")
    assert c6r.build_c6_dry_run_review()["verdict"] == (
        "CANDIDATE_6_DRY_RUN_REVIEW_FROZEN")
    assert cr.build_candidate_recommendation()["verdict"] == (
        "STRATEGY_FACTORY_CANDIDATE_RECOMMENDATION_V1_READY")
    assert ap.build_autopilot_loop_contract()["verdict"] == (
        "STRATEGY_FACTORY_AUTOPILOT_RESEARCH_LOOP_V1_READY")
    from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
        REJECTION_STATUS as C1)
    from sparta_commander.crypto_intraday_breakout_pullback_structure_v2_result_and_rejection_record_contract import (
        REJECTION_STATUS as C2)
    from sparta_commander.btc_sol_long_trend_continuation_v1_result_and_rejection_record_contract import (
        REJECTION_STATUS as C3)
    from sparta_commander.sol_btc_long_1h_swing_structure_rejection_record_contract import (
        REJECTION_STATUS as C4)
    from sparta_commander.eth_sol_relative_strength_rejection_record_contract import (
        REJECTION_STATUS as C5)
    assert C1 == C2 == C3 == C4 == C5 == "REJECTED_KEPT_ON_RECORD"


def test_13_review_fails_on_any_fact_change():
    # any-tracked-runner: certification fails
    bad = _good_observation()
    bad["artifacts_tracked_in_git"] = [c6l.RUNNER_PATH]
    assert "runner_and_artifacts_must_stay_untracked" in (
        c6l.certify_c6_labels_review(bad)["failures"])
    # record-level tamper invalidates validator
    for field, value in (
            ("head_at_detection", "00" * 20),
            ("expected_labels_sha256", "00" * 32),
            ("expected_summary_sha256", "00" * 32),
            ("expected_staged_shas", {}),
            ("expected_aggregation_counts", {}),
            ("expected_alignment_status", "X"),
            ("expected_counts", {}),
            ("expected_status_breakdown", {}),
            ("expected_accepted_setup_ids", []),
            ("frozen_detection_facts", []),
            ("claim_locks", []),
            ("replay_has_run", True),
            ("replay_authorized_by_this_gate", True),
            ("edit_decision_made", True),
            ("rejection_decision_made", True),
            ("claims_profitability", True),
            ("authorizes_paper_execution", True),
            ("authorizes_live_trading", True),
            ("live_gate_locked", False),
            ("candidate_id", "CANDIDATE_5_REVIVED")):
        tampered = c6l.build_c6_labels_review(REPO_ROOT,
                                              tracked_paths=[])
        tampered[field] = value
        assert c6l.validate_c6_labels_review(
            tampered)["valid"] is False, field
    frozen_with_failures = c6l.build_c6_labels_review(
        REPO_ROOT, tracked_paths=[])
    frozen_with_failures["failures"] = ["fake"]
    assert c6l.validate_c6_labels_review(
        frozen_with_failures)["valid"] is False


def test_14_replay_locked_and_decisions_pending():
    record = c6l.build_c6_labels_review(REPO_ROOT, tracked_paths=[])
    assert record["replay_has_run"] is False
    assert record["replay_authorized_by_this_gate"] is False
    assert record["edit_decision_made"] is False
    assert record["rejection_decision_made"] is False
    locks = record["claim_locks"]
    assert "no_replay_authorized_by_this_gate" in locks
    assert "no_edit_or_rejection_decision_made_yet" in locks


def test_15_no_profitability_paper_live_or_winner_wording():
    locks = c6l.CLAIM_LOCKS
    for lock in ("no_profitability_claim", "no_paper_approval",
                 "no_live_approval", "no_execution_approval",
                 "no_winner_wording",
                 "no_replay_authorized_by_this_gate",
                 "no_edit_or_rejection_decision_made_yet"):
        assert lock in locks, lock
    # the frozen facts use evidence language only
    facts = c6l.FROZEN_DETECTION_FACTS
    combined = " ".join(facts).lower()
    for banned in ("winner", "profitable", "profitability proven",
                   "edge confirmed", "guaranteed", "ready for live",
                   "ready for paper"):
        assert banned not in combined, banned


def test_16_no_trading_adjacent_capability_exists():
    record = c6l.build_c6_labels_review(REPO_ROOT, tracked_paths=[])
    for key in ("executes", "writes_files", "labels_now",
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
                "modifies_staged_market_data",
                "authorizes_paper_execution", "authorizes_micro_live",
                "authorizes_live_trading", "promotes_gate",
                "unlocks_downstream_gate", "claims_profitability"):
        assert record[key] is False, key
    assert record["paper_trading_gate_locked"] is True
    assert record["micro_live_gate_locked"] is True
    assert record["live_gate_locked"] is True


def test_real_artifacts_certify_when_present():
    import pathlib
    if not (pathlib.Path(REPO_ROOT) / c6l.LABELS_PATH).is_file():
        pytest.skip("candidate #6 label artifacts not present")
    record = c6l.build_c6_labels_review(REPO_ROOT, tracked_paths=[])
    assert record["verdict"] == c6l.VERDICT_C6L_FROZEN
    assert record["failures"] == []
    assert c6l.validate_c6_labels_review(record)["valid"] is True


def test_17_ast_purity_and_no_writers_beyond_reading():
    assert c6l.get_c6_labels_review_label() == c6l.C6L_LABEL
    assert "READ-ONLY" in c6l.C6L_LABEL
    assert "135 LABELS FROZEN" in c6l.C6L_LABEL
    assert "NOT A PROFITABILITY CLAIM" in c6l.C6L_LABEL
    assert c6l.C6L_MODE == "RESEARCH_ONLY"
    assert c6l.NEXT_REQUIRED_ACTION == (
        "HUMAN_DECISION_C6_REPLAY_OR_EDIT_OR_REJECT")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in c6l.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(c6l.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    assert "random" not in src
    assert "now(" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch("):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned_mods = {"urllib", "requests", "socket", "http", "ccxt",
                   "smtplib", "subprocess", "websockets", "aiohttp",
                   "schedule", "apscheduler", "threading", "asyncio",
                   "time", "sched", "telegram", "email", "csv", "pandas",
                   "os", "io", "shutil", "databento", "ssl", "ftplib",
                   "datetime", "statistics", "random"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods)
    assert not any(
        call.func.attr == "open" if isinstance(call.func, ast.Attribute)
        else getattr(call.func, "id", "") == "open"
        for call in ast.walk(tree) if isinstance(call, ast.Call))
