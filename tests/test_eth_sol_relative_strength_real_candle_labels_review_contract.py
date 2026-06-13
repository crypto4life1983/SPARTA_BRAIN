"""Tests for the Candidate #5 real-candle labels review / evidence
freeze. Certify logic proven on synthetic observations for every failure
mode; one real-artifact test certifies the live files when present."""

from __future__ import annotations

import ast
import copy

import pytest

import sparta_commander.eth_sol_relative_strength_real_candle_labels_review_contract as c5l

REPO_ROOT = "C:/SPARTA_BRAIN"


def _good_observation():
    return {
        "labels_exists": True, "summary_exists": True,
        "labels_sha256": c5l.EXPECTED_LABELS_SHA256,
        "summary_sha256": c5l.EXPECTED_SUMMARY_SHA256,
        "labels_line_count": 411,
        "status_breakdown": dict(c5l.EXPECTED_STATUS_BREAKDOWN),
        "accepted_count": 6,
        "per_symbol_counts": {
            "ETHUSD": {"attempts": 213, "accepted": 3, "rejected": 210},
            "SOLUSD": {"attempts": 198, "accepted": 3, "rejected": 195}},
        "variant_accepts": {"2r": 6, "3r": 6, "4r": 6},
        "variant_floor_fail_counts": {"2r": 0, "3r": 0, "4r": 0},
        "partial_eligibility_ids": [],
        "accepted_geometry": copy.deepcopy(
            c5l.EXPECTED_ACCEPTED_SETUPS),
        "trigger_range": dict(c5l.EXPECTED_TRIGGER_RANGE),
        "staged_shas_now": dict(c5l.EXPECTED_STAGED_SHAS),
        "staged_shas_match": True,
        "candidate_id_in_labels": None,
        "artifacts_tracked_in_git": [],
    }


def test_certify_passes_on_expected_observation():
    result = c5l.certify_c5_labels_review(_good_observation())
    assert result["certified"] is True
    assert result["failures"] == []


def test_certify_failure_modes():
    cases = (
        ({"labels_exists": False}, "labels_artifact_missing"),
        ({"summary_exists": False}, "summary_artifact_missing"),
        ({"labels_sha256": "00" * 32}, "labels_sha_mismatch"),
        ({"summary_sha256": "00" * 32}, "summary_sha_mismatch"),
        ({"labels_line_count": 410}, "label_count_mismatch"),
        ({"accepted_count": 7}, "accepted_count_mismatch"),
        ({"status_breakdown": {"accepted_for_replay_review": 6}},
         "status_breakdown_mismatch"),
        ({"variant_accepts": {"2r": 5, "3r": 6, "4r": 6}},
         "variant_accepts_mismatch"),
        ({"variant_floor_fail_counts": {"2r": 1, "3r": 0, "4r": 0}},
         "variant_floor_fail_counts_mismatch"),
        ({"partial_eligibility_ids": ["X"]},
         "partial_eligibility_must_be_empty"),
        ({"trigger_range": {"earliest": "X", "latest": "Y"}},
         "trigger_range_mismatch"),
        ({"staged_shas_match": False}, "staged_data_shas_changed"),
        ({"artifacts_tracked_in_git": [c5l.RUNNER_PATH]},
         "runner_and_artifacts_must_stay_untracked"),
    )
    for override, expected_failure in cases:
        observation = _good_observation()
        observation.update(override)
        result = c5l.certify_c5_labels_review(observation)
        assert result["certified"] is False, expected_failure
        assert expected_failure in result["failures"], expected_failure
    bad_geometry = _good_observation()
    bad_geometry["accepted_geometry"][
        "ETHUSD_2026-05-13T08:00:00Z"]["entry"] = 1.0
    result = c5l.certify_c5_labels_review(bad_geometry)
    assert any(f.startswith("accepted_geometry_mismatch")
               for f in result["failures"])
    extra_id = _good_observation()
    extra_id["accepted_geometry"]["ETHUSD_2026-06-01T00:00:00Z"] = {
        "entry": 1.0, "stop": 0.9, "bps_2r": 200.0,
        "rs_symbol_pct": 1.0, "rs_other_pct": 0.0}
    assert "accepted_setup_ids_mismatch" in (
        c5l.certify_c5_labels_review(extra_id)["failures"])
    extra_symbol = _good_observation()
    extra_symbol["per_symbol_counts"]["BTCUSD"] = {
        "attempts": 1, "accepted": 0, "rejected": 1}
    assert "unexpected_symbols_in_labels" in (
        c5l.certify_c5_labels_review(extra_symbol)["failures"])
    assert c5l.certify_c5_labels_review(None)["certified"] is False


def test_frozen_counts_and_breakdown_consistency():
    assert c5l.EXPECTED_COUNTS["ETHUSD"] == {
        "attempts": 213, "accepted": 3, "rejected": 210}
    assert c5l.EXPECTED_COUNTS["SOLUSD"] == {
        "attempts": 198, "accepted": 3, "rejected": 195}
    assert c5l.EXPECTED_COUNTS["total"] == {
        "attempts": 411, "accepted": 6, "rejected": 405}
    assert sum(c5l.EXPECTED_STATUS_BREAKDOWN.values()) == 411
    assert c5l.EXPECTED_STATUS_BREAKDOWN == {
        "accepted_for_replay_review": 6,
        "rejected_pullback_too_long": 372,
        "rejected_pullback_too_short": 21,
        "rejected_pullback_too_deep": 8,
        "rejected_rs_not_stronger": 4}
    assert c5l.EXPECTED_VARIANT_ACCEPTS == {"2r": 6, "3r": 6, "4r": 6}
    assert c5l.EXPECTED_LABELS_SHA256 == (
        "72dd8aec73b492b25968c8578bc471716d277d9027cd89a54fab8981b432"
        "8d87")
    assert c5l.EXPECTED_SUMMARY_SHA256 == (
        "6bf7d34d0ca14d1a2601627fc7d7d0db628aa3b77cffff95402b05953ac9"
        "f6d1")
    assert c5l.HEAD_AT_DETECTION == (
        "c511db021476ac0db611919f752a0fed7f1b038d")


def test_frozen_accepted_geometry():
    setups = c5l.EXPECTED_ACCEPTED_SETUPS
    assert len(setups) == 6
    assert sum(1 for sid in setups if sid.startswith("ETHUSD")) == 3
    assert sum(1 for sid in setups if sid.startswith("SOLUSD")) == 3
    assert setups["ETHUSD_2026-05-13T08:00:00Z"] == {
        "entry": 2316.64, "stop": 2295.63, "bps_2r": 181.4,
        "rs_symbol_pct": 1.21, "rs_other_pct": 0.37}
    assert setups["SOLUSD_2026-05-09T01:00:00Z"]["bps_2r"] == 380.7
    for setup_id, geometry in setups.items():
        assert geometry["stop"] < geometry["entry"], setup_id
        assert geometry["bps_2r"] >= 81, setup_id
        assert 151 <= geometry["bps_2r"] <= 381, setup_id
        assert geometry["rs_symbol_pct"] > geometry["rs_other_pct"], (
            setup_id)
        assert geometry["rs_symbol_pct"] > 0, setup_id
    assert c5l.EXPECTED_TRIGGER_RANGE == {
        "earliest": "2026-05-02T21:00:00Z",
        "latest": "2026-06-10T23:00:00Z"}


def test_frozen_facts_and_small_sample_flags():
    facts = c5l.FROZEN_DETECTION_FACTS
    assert any("no fetch" in fact for fact in facts)
    assert any("both symbols loaded simultaneously" in fact
               for fact in facts)
    assert any("960 1h bars each" in fact for fact in facts)
    assert any("timestamp alignment asserted" in fact for fact in facts)
    assert any("exactly once per symbol" in fact for fact in facts)
    assert any("no replay; labels only" in fact for fact in facts)
    assert any("zero variant-floor fails" in fact for fact in facts)
    assert any("151-381 bps" in fact for fact in facts)
    assert any("no non-overlap removals at label time" in fact
               for fact in facts)
    flags = c5l.FROZEN_SMALL_SAMPLE_FLAGS
    assert any("small sample" in flag and "ten" in flag
               for flag in flags)
    assert any("sample_size_not_near_zero" in flag for flag in flags)
    assert any("candidate #3 scarcity pattern" in flag for flag in flags)
    assert any("human decision" in flag for flag in flags)
    assert any("no profitability claim" in flag for flag in flags)


def test_real_artifacts_certify_when_present():
    import pathlib
    if not (pathlib.Path(REPO_ROOT) / c5l.LABELS_PATH).is_file():
        pytest.skip("candidate #5 label artifacts not present")
    record = c5l.build_c5_labels_review(REPO_ROOT, tracked_paths=[])
    assert record["verdict"] == c5l.VERDICT_C5L_FROZEN
    assert record["failures"] == []
    assert c5l.validate_c5_labels_review(record)["valid"] is True


def test_record_tampering_invalidates():
    record = c5l.build_c5_labels_review(REPO_ROOT, tracked_paths=[])
    for field, value in (
            ("head_at_detection", "00" * 20),
            ("expected_labels_sha256", "00" * 32),
            ("expected_summary_sha256", "00" * 32),
            ("expected_staged_shas", {}),
            ("expected_counts", {}),
            ("expected_status_breakdown", {}),
            ("expected_variant_accepts", {}),
            ("expected_accepted_setups", {}),
            ("expected_trigger_range", {}),
            ("frozen_detection_facts", []),
            ("frozen_small_sample_flags", []),
            ("replay_has_run", True),
            ("replay_edit_or_reject_is_human_decision", False),
            ("claims_profitability", True),
            ("auto_pushes", True),
            ("runs_replay_now", True),
            ("live_gate_locked", False),
            ("candidate_id", "CANDIDATE_4_REVIVED")):
        tampered = c5l.build_c5_labels_review(REPO_ROOT,
                                              tracked_paths=[])
        tampered[field] = value
        assert c5l.validate_c5_labels_review(
            tampered)["valid"] is False, field
    frozen_with_failures = c5l.build_c5_labels_review(REPO_ROOT,
                                                      tracked_paths=[])
    frozen_with_failures["failures"] = ["fake"]
    assert c5l.validate_c5_labels_review(
        frozen_with_failures)["valid"] is False


def test_chain_gate_and_capabilities():
    import sparta_commander.eth_sol_relative_strength_pullback_continuation_dry_run_review_contract as c5r
    import sparta_commander.strategy_factory_autopilot_research_loop_v1_contract as ap
    assert c5r.build_c5_dry_run_review()["verdict"] == (
        "CANDIDATE_5_DRY_RUN_REVIEW_FROZEN")
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
    assert C1 == C2 == C3 == C4 == "REJECTED_KEPT_ON_RECORD"
    record = c5l.build_c5_labels_review(REPO_ROOT, tracked_paths=[])
    assert record["verdict"] != c5l.VERDICT_C5L_BLOCKED
    assert record["replay_has_run"] is False
    assert record["replay_edit_or_reject_is_human_decision"] is True
    for key in ("executes", "writes_files", "labels_now",
                "runs_real_detection_now", "runs_replay_now",
                "scores_now", "stages_data_now", "fetches_data",
                "calls_api", "uses_network", "uses_credentials",
                "uses_wallet", "uses_account", "connects_broker",
                "connects_exchange", "uses_real_money",
                "contains_order_logic", "starts_scheduler",
                "sends_notifications", "auto_commits", "auto_pushes",
                "creates_runners_now", "creates_data_artifacts_now",
                "modifies_staged_market_data",
                "authorizes_paper_execution", "authorizes_micro_live",
                "authorizes_live_trading", "promotes_gate",
                "unlocks_downstream_gate", "claims_profitability"):
        assert record[key] is False, key
    assert record["paper_trading_gate_locked"] is True
    assert record["micro_live_gate_locked"] is True
    assert record["live_gate_locked"] is True


def test_label_action_and_module_purity():
    assert c5l.get_c5_labels_review_label() == c5l.C5L_LABEL
    assert "READ-ONLY" in c5l.C5L_LABEL
    assert "SMALL SAMPLE" in c5l.C5L_LABEL
    assert "NOT A PROFITABILITY CLAIM" in c5l.C5L_LABEL
    assert c5l.C5L_MODE == "RESEARCH_ONLY"
    assert c5l.VERDICT_C5L_FROZEN == (
        "CANDIDATE_5_REAL_CANDLE_LABELS_FROZEN_READY_FOR_HUMAN_REVIEW")
    assert c5l.NEXT_REQUIRED_ACTION == (
        "HUMAN_DECISION_C5_REPLAY_SMALL_SAMPLE_OR_EDIT_OR_REJECT")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in c5l.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(c5l.__file__, encoding="utf-8").read()
    assert "__main__" not in src
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
