"""Tests for the SPARTA Breakout-Pullback Replay Results Review.

Proves the evidence freeze: 105 trades at 27 bps, gross-negative in every
variant (edge failure, not cost failure), hit rates below gross breakeven,
candidate #2 NOT continuable as-is, exactly one V2 experiment (1h trend
filter) authorized -- and that any tampering REJECTS.
"""

from __future__ import annotations

import ast
import os.path

import pytest

import sparta_commander.crypto_intraday_breakout_pullback_structure_replay_results_review_contract as r2


def _results():
    out = []
    n = 0
    for name, (hits, stops, timeouts, _g, _n) in sorted(
            r2.EXPECTED_VARIANTS.items()):
        pass  # counts handled per-variant below
    # build 105 records whose per-variant outcomes reproduce the table
    spec = {name: ["target_hit"] * hits
            + ["stop_hit"] * stops + ["timeout_end_of_data"] * timeouts
            for name, (hits, stops, timeouts, _g, _n)
            in r2.EXPECTED_VARIANTS.items()}
    # per-variant gross to match: distribute totals across trades evenly is
    # complex; instead store gross/net per record so sums hit the totals.
    for i in range(105):
        n += 1
        record = {"setup_id": "S%03d" % n, "symbol": "BTCUSD",
                  "direction": "long", "stop_model": "structural_swing",
                  "cost_bps_charged": 27.0, "variants": {}}
        for name, (hits, stops, timeouts, gross, net) in (
                r2.EXPECTED_VARIANTS.items()):
            reason = spec[name][i]
            # put the entire residual on the last record for exact sums
            if i < 104:
                g = round(gross / 105, 6)
            else:
                g = round(gross - round(gross / 105, 6) * 104, 6)
            if i < 104:
                nv = round(net / 105, 6)
            else:
                nv = round(net - round(net / 105, 6) * 104, 6)
            record["variants"][name] = {"exit_reason": reason,
                                        "gross_r": g,
                                        "net_r_after_costs": nv}
        out.append(record)
    return out


def _summary(**overrides):
    summary = {
        "scope_sha256_of_sorted_ids": r2.EXPECTED_SCOPE_SHA256,
        "labels_replayed": 105,
        "entry_model": "entry at continuation-bar close; replay starts the "
                       "NEXT bar (anti-lookahead)",
        "conservative_rules": "stop before target each bar; adverse gaps "
                              "exit at open",
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
        "results_sha256": r2.EXPECTED_RESULTS_SHA256,
        "summary_sha256": r2.EXPECTED_SUMMARY_SHA256,
        "labels_sha256": r2.EXPECTED_LABELS_SHA256,
        "labels_review_verdict":
            "BP_REAL_CANDLE_DETECTOR_LABELS_ACCEPTED_FOR_REPLAY_REVIEW",
        "tracked_output_paths": [],
        "baseline_files_sha256": dict(r2.BASELINE_PROTECTED_FILES),
    }
    observation.update(overrides)
    return observation


def test_valid_replay_evidence_freezes_with_rejection_as_is():
    review = r2.certify_bp_replay_results(_observation())
    assert review["verdict"] == r2.VERDICT_BPR2_FROZEN
    assert review["blockers"] == []
    assert review["rejection_as_is_status"] == (
        "REJECTED_AS_IS_PENDING_ONE_V2_EXPERIMENT")
    assert review["failure_classification"] == (
        "EDGE_FAILURE_NOT_COST_FAILURE")
    assert review["candidate_2_may_continue_as_is"] is False
    assert review["candidate_approved_for_paper_or_live"] is False
    assert all(review["checklist_results"][n] is True
               for n in r2.REVIEW_CHECKLIST)
    assert len(r2.REVIEW_CHECKLIST) == 12
    assert r2.validate_bp_replay_results_review(review)["valid"] is True


def test_real_replay_artifacts_review_when_present():
    if not os.path.isfile("C:/SPARTA_BRAIN/" + r2.RESULTS_PATH):
        pytest.skip("real replay artifacts absent on this machine")
    review = r2.build_bp_replay_results_review("C:/SPARTA_BRAIN",
                                               tracked_paths=[])
    assert review["verdict"] == r2.VERDICT_BPR2_FROZEN
    assert r2.validate_bp_replay_results_review(review)["valid"] is True


def test_frozen_arithmetic_is_the_reported_table():
    assert r2.EXPECTED_VARIANTS == {
        "2r": (24, 79, 2, -30.403584, -55.607231),
        "3r": (18, 85, 2, -30.403583, -55.60723),
        "4r": (13, 90, 2, -37.403583, -62.60723)}
    for name, row in r2.BREAKEVEN_TABLE.items():
        assert row["observed_hit_rate"] < row["needed_gross_win_rate"], name
    assert abs(r2.BREAKEVEN_TABLE["2r"]["observed_hit_rate"]
               - 24 / 105) < 1e-9
    assert r2.EXPECTED_TRADES == 105 and r2.EXPECTED_COST_BPS == 27.0


def test_missing_artifacts_block_and_tampered_shas_reject():
    assert r2.certify_bp_replay_results(_observation(
        results_present=False))["verdict"] == r2.VERDICT_BPR2_BLOCKED
    assert r2.certify_bp_replay_results(None)["verdict"] == (
        r2.VERDICT_BPR2_BLOCKED)
    tampered = r2.certify_bp_replay_results(_observation(
        results_sha256="f" * 64))
    assert ("check_failed:replay_artifacts_present_and_sha_pinned"
            in tampered["blockers"])
    wrong_labels = r2.certify_bp_replay_results(_observation(
        labels_sha256="0" * 64))
    assert ("check_failed:labels_review_still_accepted_and_labels_sha"
            "_pinned" in wrong_labels["blockers"])


def test_tampered_net_or_counts_reject():
    results = _results()
    results[0]["variants"]["2r"]["net_r_after_costs"] = 50.0  # fake winner
    review = r2.certify_bp_replay_results(_observation(results=results))
    assert review["verdict"] == r2.VERDICT_BPR2_REVIEW_REJECTED
    assert ("check_failed:per_variant_arithmetic_matches_frozen_table"
            in review["blockers"])
    results2 = _results()
    # record 50's 4r outcome is a stop exit; flipping it shifts the counts
    assert results2[50]["variants"]["4r"]["exit_reason"] == "stop_hit"
    results2[50]["variants"]["4r"]["exit_reason"] = "target_hit"
    review2 = r2.certify_bp_replay_results(_observation(results=results2))
    assert review2["verdict"] == r2.VERDICT_BPR2_REVIEW_REJECTED
    short = r2.certify_bp_replay_results(_observation(
        results=_results()[:-1]))
    assert ("check_failed:scope_was_exactly_the_105_frozen_setup_ids"
            in short["blockers"])


def test_cost_removal_rejects():
    results = _results()
    results[5]["cost_bps_charged"] = 0.0
    review = r2.certify_bp_replay_results(_observation(results=results))
    assert ("check_failed:cost_27bps_charged_on_every_trade"
            in review["blockers"])


def test_profitability_or_paper_live_claims_reject():
    bad = r2.certify_bp_replay_results(_observation(
        summary=_summary(honesty_note="this strategy is profitable")))
    assert bad["verdict"] == r2.VERDICT_BPR2_REVIEW_REJECTED
    claimed = r2.certify_bp_replay_results(_observation(
        summary=_summary(profitability_claim="edge found")))
    assert claimed["verdict"] == r2.VERDICT_BPR2_REVIEW_REJECTED
    for flag in ("candidate_approved_for_paper_or_live",
                 "profitability_claim_permitted",
                 "candidate_2_may_continue_as_is"):
        tampered = r2.certify_bp_replay_results(_observation())
        tampered[flag] = True
        assert r2.validate_bp_replay_results_review(tampered)[
            "valid"] is False, flag


def test_v2_experiment_scope_locked_to_1h_trend_filter():
    review = r2.certify_bp_replay_results(_observation())
    assert review["one_v2_experiment_scope"] == "add_1h_trend_filter_only"
    assert review["next_required_action"] == (
        "HUMAN_APPROVED_BP_MUTABLE_V2_1H_TREND_FILTER_EDIT")
    assert ("one_v2_experiment_authorized_add_the_1h_trend_filter_a"
            "_stricter_filter_not_loosening"
            in review["honest_interpretation"])
    assert ("if_v2_also_fails_fee_honest_replay_the_candidate_is_rejected"
            "_and_kept_on_record" in review["honest_interpretation"])
    tampered = r2.certify_bp_replay_results(_observation())
    tampered["one_v2_experiment_scope"] = "loosen_everything"
    assert r2.validate_bp_replay_results_review(tampered)["valid"] is False
    tampered2 = r2.certify_bp_replay_results(_observation())
    tampered2["honest_interpretation"] = ["all_good"]
    assert r2.validate_bp_replay_results_review(tampered2)["valid"] is False


def test_prior_evidence_and_candidate_1_preserved():
    mutated = dict(r2.BASELINE_PROTECTED_FILES)
    mutated[next(iter(mutated))] = "0" * 64
    review = r2.certify_bp_replay_results(_observation(
        baseline_files_sha256=mutated))
    assert ("check_failed:prior_evidence_byte_identical"
            in review["blockers"])
    tracked = r2.certify_bp_replay_results(_observation(
        tracked_output_paths=["data/breakout_pullback/x"]))
    assert tracked["verdict"] == r2.VERDICT_BPR2_REVIEW_REJECTED
    good = r2.certify_bp_replay_results(_observation())
    assert good["checklist_results"]["candidate_1_rejection_preserved"] is True
    from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
        REJECTION_STATUS)
    assert REJECTION_STATUS == "REJECTED_KEPT_ON_RECORD"


def test_capabilities_false_gates_locked_and_deterministic():
    review = r2.certify_bp_replay_results(_observation())
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
        assert review[key] is False, key
    assert review["paper_trading_gate_locked"] is True
    assert review["micro_live_gate_locked"] is True
    assert review["live_gate_locked"] is True
    tampered = r2.certify_bp_replay_results(_observation())
    tampered["forbidden"] = tampered["forbidden"][:3]
    assert r2.validate_bp_replay_results_review(tampered)["valid"] is False
    for item in ("another_replay_run", "continuing_candidate_2_as_is",
                 "profitability_claims",
                 "paper_live_micro_live_authorization",
                 "deleting_or_hiding_candidate_1_rejected_evidence",
                 "gate_unlocks"):
        assert item in r2.FORBIDDEN, item
    assert (r2.certify_bp_replay_results(_observation())
            == r2.certify_bp_replay_results(_observation()))


def test_label_action_read_only_and_imports_clean():
    assert r2.get_bp_replay_results_review_label() == r2.BPR2_LABEL
    assert "READ-ONLY" in r2.BPR2_LABEL and r2.BPR2_MODE == "RESEARCH_ONLY"
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in r2.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(r2.__file__, encoding="utf-8").read()
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