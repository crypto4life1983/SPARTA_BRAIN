"""Tests for the SPARTA Breakout-Pullback Real-Candle Detector Labels
Review.

Failure modes use synthetic 559-label sets (pure certification); acceptance
is also checked against the REAL detector outputs when present. Nothing is
modified, deleted, fetched, replayed, or scored; replay stays human-gated.
"""

from __future__ import annotations

import ast
import os.path

import pytest

import sparta_commander.crypto_intraday_breakout_pullback_structure_real_candle_detector_labels_review_contract as bpl
from sparta_commander.crypto_intraday_breakout_pullback_structure_detector_spec import (
    BP_LABEL_REQUIRED_FIELDS,
)

_ACCEPTED_BY_SYMBOL = (("ARBUSD", 38), ("AVAXUSD", 25), ("ETHUSD", 15),
                       ("SOLUSD", 14), ("XRPUSD", 8), ("BTCUSD", 5))
_REJECTIONS = (("BP_SETUP_REJECTED_NO_CONTINUATION", 169),
               ("BP_SETUP_REJECTED_RISK_BELOW_81_BPS", 150),
               ("BP_SETUP_REJECTED_FAILED_RETEST", 65),
               ("BP_SETUP_REJECTED_WEAK_BREAKOUT", 60),
               ("BP_SETUP_REJECTED_NO_PULLBACK", 10))


def _label(symbol, status, n, risk=None, stop_model=None, direction="long"):
    label = {name: None for name in BP_LABEL_REQUIRED_FIELDS}
    label.update({
        "setup_id": "%s_synth_a%03d_bp_dry_run" % (symbol, n),
        "candidate_id": "CRYPTO_INTRADAY_BREAKOUT_PULLBACK_STRUCTURE_V1",
        "symbol": symbol, "session_date": "2026-05-12_2026-06-10",
        "direction": direction, "context_timeframe": "1h_15m",
        "trigger_timeframe": "15m", "range_lookback_bars": 20,
        "breakout_time": "2026-05-13T10:%02d:00Z" % (n % 60),
        "cost_floor_bps": 81,
        "cost_floor_pass": risk is not None and risk >= 81,
        "risk_distance_bps": risk,
        "stop_model": stop_model,
        "rejection_reason": (None if status
                             == "BP_SETUP_LABEL_ACCEPTED_FOR_REPLAY_REVIEW"
                             else "condition_failed:synthetic"),
        "detector_status": status,
        "label_authorizes_nothing": True,
    })
    return label


def _labels():
    out, n = [], 0
    accepted_made = 0
    for symbol, count in _ACCEPTED_BY_SYMBOL:
        for _ in range(count):
            n += 1
            accepted_made += 1
            if accepted_made == 1:
                risk = 81.767807
            elif accepted_made == 2:
                risk = 223.713647
            else:
                risk = 114.483206
            stop_model = ("structural_swing" if accepted_made <= 68
                          else "atr_1_5x")
            direction = "long" if accepted_made <= 42 else "short"
            out.append(_label(symbol,
                              "BP_SETUP_LABEL_ACCEPTED_FOR_REPLAY_REVIEW",
                              n, risk=risk, stop_model=stop_model,
                              direction=direction))
    for status, count in _REJECTIONS:
        for _ in range(count):
            n += 1
            out.append(_label("BTCUSD", status, n))
    return out


def _summary(**overrides):
    summary = {
        "candidate_id": "CRYPTO_INTRADAY_BREAKOUT_PULLBACK_STRUCTURE_V1",
        "labels_total": 559, "accepted_total": 105,
        "no_pnl_no_scoring_no_replay": True,
        "labels_authorize_nothing": True,
        "replay_ready": True,
        "replay_requires_separate_human_approval": True,
    }
    summary.update(overrides)
    return summary


def _observation(**overrides):
    observation = {
        "labels_present": True, "summary_present": True,
        "labels": overrides.pop("labels", None) or _labels(),
        "summary": overrides.pop("summary", None) or _summary(),
        "labels_sha256": bpl.EXPECTED_LABELS_SHA256,
        "summary_sha256": bpl.EXPECTED_SUMMARY_SHA256,
        "tracked_output_paths": [],
        "baseline_files_sha256": dict(bpl.BASELINE_PROTECTED_FILES),
    }
    observation.update(overrides)
    return observation


def test_synthetic_fixture_distribution_is_consistent():
    labels = _labels()
    assert len(labels) == 559
    accepted = [x for x in labels if x["detector_status"]
                == "BP_SETUP_LABEL_ACCEPTED_FOR_REPLAY_REVIEW"]
    assert len(accepted) == 105
    risks = sorted(x["risk_distance_bps"] for x in accepted)
    assert risks[0] == 81.767807
    assert risks[len(risks) // 2] == 114.483206
    assert risks[-1] == 223.713647


def test_complete_valid_label_set_reviews_successfully():
    review = bpl.certify_bp_detector_labels(_observation())
    assert review["verdict"] == bpl.VERDICT_BPL_ACCEPTED
    assert review["blockers"] == []
    assert review["labels_total"] == 559
    assert review["accepted_total"] == 105
    assert review["replay_ready"] is True
    assert review["replay_authorized"] is False
    assert all(review["checklist_results"][n] is True
               for n in bpl.REVIEW_CHECKLIST)
    assert len(bpl.REVIEW_CHECKLIST) == 14
    assert bpl.validate_bp_detector_labels_review(review)["valid"] is True


def test_real_detector_outputs_review_when_present():
    if not os.path.isfile("C:/SPARTA_BRAIN/" + bpl.LABELS_PATH):
        pytest.skip("real BP detector outputs absent on this machine")
    review = bpl.build_bp_detector_labels_review("C:/SPARTA_BRAIN",
                                                 tracked_paths=[])
    assert review["verdict"] == bpl.VERDICT_BPL_ACCEPTED
    assert review["labels_total"] == 559
    assert review["accepted_total"] == 105
    assert bpl.validate_bp_detector_labels_review(review)["valid"] is True


def test_missing_labels_or_summary_blocks():
    assert bpl.certify_bp_detector_labels(_observation(
        labels_present=False))["verdict"] == bpl.VERDICT_BPL_BLOCKED
    assert bpl.certify_bp_detector_labels(_observation(
        summary_present=False))["verdict"] == bpl.VERDICT_BPL_BLOCKED
    assert bpl.certify_bp_detector_labels(None)["verdict"] == (
        bpl.VERDICT_BPL_BLOCKED)


def test_schema_mismatch_rejects():
    labels = _labels()
    del labels[0]["range_high"]
    review = bpl.certify_bp_detector_labels(_observation(labels=labels))
    assert review["verdict"] == bpl.VERDICT_BPL_REJECTED
    assert ("check_failed:every_label_38_field_schema_candidate_id"
            "_authorizes_nothing" in review["blockers"])
    labels2 = _labels()
    labels2[1]["label_authorizes_nothing"] = False
    assert bpl.certify_bp_detector_labels(_observation(labels=labels2))[
        "verdict"] == bpl.VERDICT_BPL_REJECTED


def test_unknown_detector_status_rejects():
    labels = _labels()
    labels[200]["detector_status"] = "BP_SETUP_BRAND_NEW_STATUS"
    review = bpl.certify_bp_detector_labels(_observation(labels=labels))
    assert review["verdict"] == bpl.VERDICT_BPL_REJECTED
    assert ("check_failed:every_status_in_closed_10_set"
            in review["blockers"])


def test_accepted_count_mismatch_rejects():
    labels = _labels()
    labels[0]["detector_status"] = "BP_SETUP_REJECTED_AMBIGUOUS_STRUCTURE"
    review = bpl.certify_bp_detector_labels(_observation(labels=labels))
    assert review["verdict"] == bpl.VERDICT_BPL_REJECTED
    assert ("check_failed:totals_559_accepted_105_rejected_454"
            in review["blockers"])
    short = bpl.certify_bp_detector_labels(
        _observation(labels=_labels()[:-1]))
    assert short["verdict"] == bpl.VERDICT_BPL_REJECTED


def test_rejection_count_mismatch_rejects():
    labels = _labels()
    for x in labels:
        if x["detector_status"] == "BP_SETUP_REJECTED_NO_PULLBACK":
            x["detector_status"] = "BP_SETUP_REJECTED_FAILED_RETEST"
            break
    review = bpl.certify_bp_detector_labels(_observation(labels=labels))
    assert review["verdict"] == bpl.VERDICT_BPL_REJECTED
    assert ("check_failed:rejection_counts_match_observed_run"
            in review["blockers"])


def test_risk_floor_violation_among_accepted_rejects():
    labels = _labels()
    for x in labels:
        if x["detector_status"] == "BP_SETUP_LABEL_ACCEPTED_FOR_REPLAY_REVIEW":
            x["risk_distance_bps"] = 50.0  # below floor but still 'accepted'
            x["cost_floor_pass"] = True
            break
    review = bpl.certify_bp_detector_labels(_observation(labels=labels))
    assert review["verdict"] == bpl.VERDICT_BPL_REJECTED
    assert "check_failed:all_accepted_pass_81bps_floor" in review["blockers"]
    labels2 = _labels()
    for x in labels2:
        if x["detector_status"] == "BP_SETUP_LABEL_ACCEPTED_FOR_REPLAY_REVIEW":
            x["cost_floor_pass"] = False
            break
    review2 = bpl.certify_bp_detector_labels(_observation(labels=labels2))
    assert ("check_failed:all_accepted_pass_81bps_floor"
            in review2["blockers"])


def test_risk_summary_and_split_mismatches_reject():
    labels = _labels()
    for x in labels:
        if x["risk_distance_bps"] == 223.713647:
            x["risk_distance_bps"] = 500.0  # fake a wider max
            break
    review = bpl.certify_bp_detector_labels(_observation(labels=labels))
    assert ("check_failed:accepted_risk_min_median_max_match"
            in review["blockers"])
    labels2 = _labels()
    for x in labels2:
        if x["stop_model"] == "atr_1_5x":
            x["stop_model"] = "structural_swing"
            break
    review2 = bpl.certify_bp_detector_labels(_observation(labels=labels2))
    assert ("check_failed:stop_model_and_direction_split_match"
            in review2["blockers"])


def test_pnl_replay_scorer_fields_reject():
    labels = _labels()
    labels[3]["net_pnl"] = 9.0
    review = bpl.certify_bp_detector_labels(_observation(labels=labels))
    assert review["verdict"] == bpl.VERDICT_BPL_REJECTED
    assert ("check_failed:no_replay_pnl_or_scoring_fields"
            in review["blockers"])
    for bad in ("replay_status", "profit_factor", "score_total"):
        labels2 = _labels()
        labels2[7][bad] = "x"
        assert bpl.certify_bp_detector_labels(_observation(
            labels=labels2))["verdict"] == bpl.VERDICT_BPL_REJECTED, bad
    bad_summary = bpl.certify_bp_detector_labels(_observation(
        summary=_summary(no_pnl_no_scoring_no_replay=False)))
    assert bad_summary["verdict"] == bpl.VERDICT_BPL_REJECTED
    no_gate = bpl.certify_bp_detector_labels(_observation(
        summary=_summary(replay_requires_separate_human_approval=False)))
    assert ("check_failed:replay_ready_only_with_separate_human_approval"
            "_flag" in no_gate["blockers"])


def test_tracked_outputs_and_modified_candles_reject():
    tracked = bpl.certify_bp_detector_labels(_observation(
        tracked_output_paths=["data/breakout_pullback/x.jsonl"]))
    assert tracked["verdict"] == bpl.VERDICT_BPL_REJECTED
    mutated = dict(bpl.BASELINE_PROTECTED_FILES)
    mutated[next(iter(mutated))] = "0" * 64
    review = bpl.certify_bp_detector_labels(_observation(
        baseline_files_sha256=mutated))
    assert ("check_failed:staged_candles_byte_identical"
            in review["blockers"])
    wrong_sha = bpl.certify_bp_detector_labels(_observation(
        labels_sha256="f" * 64))
    assert ("check_failed:labels_and_summary_present_and_sha_pinned"
            in wrong_sha["blockers"])


def test_replay_stays_human_gated_and_validator_strict():
    review = bpl.certify_bp_detector_labels(_observation())
    assert review["replay_ready"] is True
    assert review["replay_authorized"] is False
    assert review["next_required_action"] == (
        "HUMAN_APPROVED_BP_FEE_HONEST_REPLAY_OF_105_ACCEPTED_LABELS")
    tampered = bpl.certify_bp_detector_labels(_observation())
    tampered["replay_authorized"] = True
    assert bpl.validate_bp_detector_labels_review(tampered)["valid"] is False
    rejected = bpl.certify_bp_detector_labels(_observation(
        labels_sha256="f" * 64))
    assert rejected["replay_ready"] is False
    rejected["replay_ready"] = True
    assert bpl.validate_bp_detector_labels_review(rejected)["valid"] is False
    for key in ("executes", "writes_files", "modifies_labels",
                "deletes_labels", "modifies_staged_files",
                "runs_detector_now", "runs_replay_now", "scores_now",
                "fetches_data", "uses_network", "uses_credentials",
                "uses_wallet", "connects_broker", "connects_exchange",
                "contains_order_logic", "authorizes_paper_execution",
                "authorizes_micro_live", "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate"):
        assert review[key] is False, key
    assert review["paper_trading_gate_locked"] is True
    assert review["micro_live_gate_locked"] is True
    assert review["live_gate_locked"] is True
    tampered2 = bpl.certify_bp_detector_labels(_observation())
    tampered2["forbidden"] = tampered2["forbidden"][:3]
    assert bpl.validate_bp_detector_labels_review(tampered2)["valid"] is False
    assert (bpl.certify_bp_detector_labels(_observation())
            == bpl.certify_bp_detector_labels(_observation()))


def test_candidate_1_preserved_and_upstream_untouched():
    review = bpl.certify_bp_detector_labels(_observation())
    assert review["checklist_results"][
        "labels_only_run_and_candidate_1_preserved"] is True
    assert review["candidate_1_evidence_kept_on_record"] is True
    from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
        REJECTION_REASON, REJECTION_STATUS)
    assert REJECTION_STATUS == "REJECTED_KEPT_ON_RECORD"
    assert REJECTION_REASON == "COST_NON_VIABLE_RISK_GEOMETRY"
    import sparta_commander.crypto_intraday_breakout_pullback_structure_detector_spec as bpd
    assert len(bpd.BP_LABEL_REQUIRED_FIELDS) == 38
    assert len(bpd.BP_DETECTOR_STATUSES) == 10
    import sparta_commander.ny_session_fvg_choch_additional_session_days_staged_candles_review as ad
    assert len(ad.BASELINE_PROTECTED_FILES) == 5
    from sparta_commander.strategy_factory_mission_flow_status import (
        LATEST_COMPLETED_PM_LANE_CHAIN)
    assert "Research Only" in LATEST_COMPLETED_PM_LANE_CHAIN


def test_label_action_read_only_and_imports_clean():
    assert bpl.get_bp_labels_review_label() == bpl.BPL_LABEL
    assert "READ-ONLY" in bpl.BPL_LABEL and bpl.BPL_MODE == "RESEARCH_ONLY"
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in bpl.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(bpl.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    assert "while true" not in src.lower() and "sleep(" not in src.lower()
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch("):
        assert verb not in src, verb
    tree = ast.parse(src)
    sparta_imports = {node.module for node in ast.walk(tree)
                      if isinstance(node, ast.ImportFrom) and node.module
                      and node.module.startswith("sparta_commander")}
    for module in sparta_imports:
        for fragment in ("replay_runner", "replay_spec", "optimizer",
                         "fetch", "dry_run"):
            assert fragment not in module, module
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