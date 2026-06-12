"""Tests for the SPARTA BP V2 Result + Candidate #2 Rejection Record.

Proves the freeze: 559/105/64, filter-only proof, per-variant arithmetic
recomputed from raw records, below gross breakeven everywhere, candidate #2
rejected with no further edits possible, seeds preserved as non-rescue --
and that any tampering REJECTS.
"""

from __future__ import annotations

import ast
import os.path

import pytest

import sparta_commander.crypto_intraday_breakout_pullback_structure_v2_result_and_rejection_record_contract as rj2


def _results():
    out = []
    spec = {name: ["target_hit"] * hits + ["stop_hit"] * stops
            + ["timeout_end_of_data"] * timeouts
            for name, (hits, stops, timeouts, _g, _n, _m)
            in rj2.EXPECTED_V2_VARIANTS.items()}
    for i in range(64):
        record = {"setup_id": "V2S%03d" % i, "symbol": "BTCUSD",
                  "direction": "long", "stop_model": "structural_swing",
                  "cost_bps_charged": 27.0, "variants": {}}
        for name, (hits, stops, timeouts, gross, net, _mean) in (
                rj2.EXPECTED_V2_VARIANTS.items()):
            if i < 63:
                g = round(gross / 64, 6)
                n = round(net / 64, 6)
            else:
                g = round(gross - round(gross / 64, 6) * 63, 6)
                n = round(net - round(net / 64, 6) * 63, 6)
            record["variants"][name] = {"exit_reason": spec[name][i],
                                        "gross_r": g,
                                        "net_r_after_costs": n}
        out.append(record)
    return out


def _summary(**overrides):
    summary = {
        "attempts_total": 559, "base_accepted": 105, "v2_survivors": 64,
        "filter_only_proof": {"attempts_lte_559": True,
                              "survivors_lte_105": True,
                              "survivors_subset_of_frozen_105": True},
        "honesty_note": "NO profitability claim is made or permitted",
        "replay_authorizes_nothing": True,
        "no_orders_no_credentials_no_paper_no_live": True,
    }
    summary.update(overrides)
    return summary


def _observation(**overrides):
    observation = {
        "results_present": True, "summary_present": True,
        "results": overrides.pop("results", None) or _results(),
        "summary": overrides.pop("summary", None) or _summary(),
        "results_sha256": rj2.EXPECTED_V2_RESULTS_SHA256,
        "summary_sha256": rj2.EXPECTED_V2_SUMMARY_SHA256,
        "labels_sha256": rj2.EXPECTED_LABELS_SHA256,
        "v2_edit_verdict": "BP_MUTABLE_EDIT_V2_1H_TREND_FILTER_READY",
        "replay_freeze_verdict":
            "BP_REPLAY_RESULTS_FROZEN_CANDIDATE_REJECTED_AS_IS",
        "tracked_output_paths": [],
        "baseline_files_sha256": dict(rj2.BASELINE_PROTECTED_FILES),
    }
    observation.update(overrides)
    return observation


def test_valid_v2_result_records_formal_rejection():
    record = rj2.certify_bp_v2_rejection(_observation())
    assert record["verdict"] == rj2.VERDICT_RJ2_RECORDED
    assert record["blockers"] == []
    assert record["rejection_status"] == "REJECTED_KEPT_ON_RECORD"
    assert record["rejection_reason"] == (
        "EDGE_FAILURE_SURVIVED_ONE_AUTHORIZED_FILTER_EXPERIMENT")
    assert record["candidate_2_may_continue_as_is"] is False
    assert record["candidate_2_may_receive_another_mutable_edit"] is False
    assert all(record["checklist_results"][n] is True
               for n in rj2.REVIEW_CHECKLIST)
    assert len(rj2.REVIEW_CHECKLIST) == 10
    assert rj2.validate_bp_v2_rejection_record(record)["valid"] is True


def test_real_v2_artifacts_record_rejection_when_present():
    if not os.path.isfile("C:/SPARTA_BRAIN/" + rj2.V2_RESULTS_PATH):
        pytest.skip("real V2 artifacts absent on this machine")
    record = rj2.build_bp_v2_rejection_record("C:/SPARTA_BRAIN",
                                              tracked_paths=[])
    assert record["verdict"] == rj2.VERDICT_RJ2_RECORDED
    assert rj2.validate_bp_v2_rejection_record(record)["valid"] is True


def test_frozen_table_is_the_reported_arithmetic():
    assert rj2.EXPECTED_V2_VARIANTS == {
        "2r": (16, 46, 2, -13.403583, -28.520186, -0.445628),
        "3r": (14, 48, 2, -5.403583, -20.520186, -0.320628),
        "4r": (11, 51, 2, -6.403583, -21.520186, -0.336253)}
    for name, row in rj2.BREAKEVEN_TABLE.items():
        assert row["observed"] < row["needed"], name
    assert rj2.EXPECTED_ATTEMPTS == 559
    assert rj2.EXPECTED_BASE_ACCEPTED == 105
    assert rj2.EXPECTED_V2_SURVIVORS == 64


def test_missing_artifacts_block_and_tampered_inputs_reject():
    assert rj2.certify_bp_v2_rejection(_observation(
        results_present=False))["verdict"] == rj2.VERDICT_RJ2_BLOCKED
    assert rj2.certify_bp_v2_rejection(None)["verdict"] == (
        rj2.VERDICT_RJ2_BLOCKED)
    tampered = rj2.certify_bp_v2_rejection(_observation(
        results_sha256="f" * 64))
    assert ("check_failed:v2_artifacts_present_and_sha_pinned"
            in tampered["blockers"])
    not_ready = rj2.certify_bp_v2_rejection(_observation(
        v2_edit_verdict="BP_MUTABLE_EDIT_V2_1H_TREND_FILTER_BLOCKED"))
    assert ("check_failed:v2_edit_ready_and_replay_freeze_frozen"
            in not_ready["blockers"])


def test_count_or_proof_mismatch_rejects():
    wrong = rj2.certify_bp_v2_rejection(_observation(
        summary=_summary(v2_survivors=70)))
    assert ("check_failed:counts_559_105_64_and_filter_only_proof"
            in wrong["blockers"])
    no_proof = rj2.certify_bp_v2_rejection(_observation(summary=_summary(
        filter_only_proof={"attempts_lte_559": True,
                           "survivors_lte_105": False,
                           "survivors_subset_of_frozen_105": True})))
    assert no_proof["verdict"] == rj2.VERDICT_RJ2_REVIEW_REJECTED
    short = rj2.certify_bp_v2_rejection(_observation(
        results=_results()[:-1]))
    assert short["verdict"] == rj2.VERDICT_RJ2_REVIEW_REJECTED


def test_tampered_arithmetic_or_fake_winner_rejects():
    results = _results()
    results[0]["variants"]["3r"]["net_r_after_costs"] = 40.0
    review = rj2.certify_bp_v2_rejection(_observation(results=results))
    assert ("check_failed:per_variant_arithmetic_matches_frozen_table"
            in review["blockers"])
    results2 = _results()
    assert results2[40]["variants"]["2r"]["exit_reason"] == "stop_hit"
    results2[40]["variants"]["2r"]["exit_reason"] = "target_hit"
    review2 = rj2.certify_bp_v2_rejection(_observation(results=results2))
    assert review2["verdict"] == rj2.VERDICT_RJ2_REVIEW_REJECTED
    no_cost = _results()
    no_cost[3]["cost_bps_charged"] = 0.0
    review3 = rj2.certify_bp_v2_rejection(_observation(results=no_cost))
    assert ("check_failed:survivors_unique_and_cost_27bps_on_every_trade"
            in review3["blockers"])


def test_no_further_edits_or_continuation_possible():
    record = rj2.certify_bp_v2_rejection(_observation())
    assert "continuing_candidate_2_as_is" in rj2.FORBIDDEN
    assert "another_mutable_edit_for_candidate_2" in rj2.FORBIDDEN
    assert "using_seed_observations_to_rescue_candidate_2" in rj2.FORBIDDEN
    for flag in ("candidate_2_may_continue_as_is",
                 "candidate_2_may_receive_another_mutable_edit",
                 "candidate_approved_for_paper_or_live",
                 "profitability_claim_permitted",
                 "evidence_deleted_or_hidden"):
        tampered = rj2.certify_bp_v2_rejection(_observation())
        tampered[flag] = True
        assert rj2.validate_bp_v2_rejection_record(tampered)[
            "valid"] is False, flag
    assert record["verdict"] == rj2.VERDICT_RJ2_RECORDED


def test_seeds_preserved_as_non_rescue_only():
    record = rj2.certify_bp_v2_rejection(_observation())
    seeds = record["future_seeds_not_rescue_paths"]
    assert "btc_was_net_positive_in_all_variants_small_sample" in seeds
    assert "sol_was_net_positive_at_3r_and_4r" in seeds
    assert "long_side_was_materially_stronger_than_shorts" in seeds
    assert ("these_observations_seed_future_new_candidate_families_only"
            "_and_are_never_rescue_paths_for_candidate_2" in seeds)
    tampered = rj2.certify_bp_v2_rejection(_observation())
    tampered["future_seeds_not_rescue_paths"] = ["revive_candidate_2"]
    assert rj2.validate_bp_v2_rejection_record(tampered)["valid"] is False


def test_prior_evidence_and_candidate_1_preserved():
    mutated = dict(rj2.BASELINE_PROTECTED_FILES)
    mutated[next(iter(mutated))] = "0" * 64
    review = rj2.certify_bp_v2_rejection(_observation(
        baseline_files_sha256=mutated))
    assert ("check_failed:prior_evidence_byte_identical"
            in review["blockers"])
    wrong_labels = rj2.certify_bp_v2_rejection(_observation(
        labels_sha256="0" * 64))
    assert wrong_labels["verdict"] == rj2.VERDICT_RJ2_REVIEW_REJECTED
    good = rj2.certify_bp_v2_rejection(_observation())
    assert good["checklist_results"][
        "candidate_1_rejection_preserved"] is True
    from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
        REJECTION_STATUS)
    assert REJECTION_STATUS == "REJECTED_KEPT_ON_RECORD"


def test_capabilities_false_gates_locked_and_deterministic():
    record = rj2.certify_bp_v2_rejection(_observation())
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
    tampered = rj2.certify_bp_v2_rejection(_observation())
    tampered["forbidden"] = tampered["forbidden"][:3]
    assert rj2.validate_bp_v2_rejection_record(tampered)["valid"] is False
    tampered2 = rj2.certify_bp_v2_rejection(_observation())
    tampered2["rejection_reason"] = "CHANGED_MY_MIND"
    assert rj2.validate_bp_v2_rejection_record(tampered2)["valid"] is False
    assert (rj2.certify_bp_v2_rejection(_observation())
            == rj2.certify_bp_v2_rejection(_observation()))


def test_label_action_read_only_and_imports_clean():
    assert rj2.get_bp_v2_rejection_record_label() == rj2.RJ2_LABEL
    assert "READ-ONLY" in rj2.RJ2_LABEL and rj2.RJ2_MODE == "RESEARCH_ONLY"
    assert rj2.NEXT_REQUIRED_ACTION == (
        "HUMAN_DECISION_ON_NEXT_CANDIDATE_FAMILY")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in rj2.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(rj2.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    assert "while true" not in src.lower() and "sleep(" not in src.lower()
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch("):
        assert verb not in src, verb
    tree = ast.parse(src)
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