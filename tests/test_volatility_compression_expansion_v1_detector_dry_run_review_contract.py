"""Tests for the Candidate #7 detector dry-run review contract
(VOLATILITY_COMPRESSION_EXPANSION_V1).

Verifies: chain gates live (six-record ledger + V2 + Rec V1 + AP V1 +
C7 proposal + C7 spec review + C7 detector spec/dry-run); frozen
fixture counts, accepted setup geometry, anti-cluster facts, strict-
contraction fact, insufficient-history fact, universe enforcement,
WIDER-stop facts, floor facts, and the frozen findings tuple all
recompute live; review-only flags hold; downstream unlocks remain
locked; no trading-adjacent capability; AST/purity green. Commander
safety suite runs alongside (12 tests)."""

from __future__ import annotations

import ast

import sparta_commander.volatility_compression_expansion_v1_detector_dry_run_review_contract as c7r
import sparta_commander.volatility_compression_expansion_v1_detector_spec_dry_run_contract as c7d


def _record():
    return c7r.build_candidate_7_dry_run_review()


def test_review_frozen_and_gated_on_full_chain():
    record = _record()
    assert record["verdict"] == c7r.VERDICT_C7R_FROZEN
    assert record["blockers"] == []
    assert record["failures"] == []
    assert c7r.validate_candidate_7_dry_run_review(
        record)["valid"] is True
    # determinism
    assert _record() == record
    # explicit expectations match the pushed detector module
    assert record["expected_detector_verdict"] == (
        "CANDIDATE_7_DETECTOR_SPEC_READY")
    assert record["expected_dry_run_verdict"] == (
        "CANDIDATE_7_DETECTOR_DRY_RUN_PASSED")
    assert record["expected_combined_verdict"] == (
        "CANDIDATE_7_DETECTOR_SPEC_DRY_RUN_READY")


def test_frozen_fixture_counts_exact():
    record = _record()
    counts = record["expected_fixture_counts"]
    assert counts["valid_compression_expansion"] == {
        "attempts": 19, "accepted": 1}
    assert counts["no_contraction"] == {
        "attempts": 4,
        "statuses": ("rejected_contraction_window",)}
    assert counts["only_4_contraction_bars"] == {
        "attempts": 4, "accepted": 0}
    assert counts["expansion_below_1_8x"] == {
        "attempts": 19, "accepted": 0,
        "rejected_expansion_multiplier": 8}
    assert counts["close_at_midpoint"] == {
        "attempts": 19, "accepted": 0,
        "rejected_close_not_in_upper_third": 1}
    # any frozen count tamper rejects
    tampered = _record()
    tampered["expected_fixture_counts"] = dict(
        tampered["expected_fixture_counts"],
        valid_compression_expansion={"attempts": 19, "accepted": 2})
    assert c7r.validate_candidate_7_dry_run_review(
        tampered)["valid"] is False


def test_frozen_accepted_setup_geometry_exact():
    record = _record()
    accepted = record["expected_accepted_setup"]
    assert accepted["setup_id"] == "BTCUSD_2026-01-23T12:00:00Z"
    assert accepted["symbol"] == "BTCUSD"
    assert accepted["timeframe"] == "4h"
    assert accepted["direction"] == "long"
    assert accepted["event_index"] == 135
    assert accepted["entry_price"] == 50300.0
    assert accepted["contracted_atr"] == 1.5
    assert accepted["atr14_at_event"] == 24.285714
    # structure-wider proof: 301.0 > 1.5*24.285714 = 36.43
    assert accepted["structure_stop_distance"] == 301.0
    assert accepted["atr_stop_distance"] == 36.428571
    assert accepted["stop_distance"] == 301.0
    assert accepted["stop_price"] == 49999.0
    assert accepted["stop_source"] == "structure_wider_than_1_5x_atr"
    assert accepted["target_2r"] == 50902.0
    assert accepted["target_3r"] == 51203.0
    assert accepted["target_4r"] == 51504.0
    assert accepted["geometry_floor_pass_by_variant"] == {
        "2r": True, "3r": True, "4r": True}
    assert accepted["close_in_upper_third_passes"] is True
    assert accepted["contraction_window_passes"] is True
    assert accepted["status"] == "accepted_for_replay_review"
    # tamper any field -> review rejects via the recompute path
    tampered = _record()
    tampered["expected_accepted_setup"] = dict(
        tampered["expected_accepted_setup"], stop_distance=999.0)
    assert c7r.validate_candidate_7_dry_run_review(
        tampered)["valid"] is False


def test_anti_cluster_facts_frozen():
    record = _record()
    anti = record["expected_anti_cluster"]
    assert anti["anti_cluster_min_bar_gap"] == 6
    assert anti["tie_breaker"] == (
        "keep_the_earlier_event_drop_the_later_one")
    assert anti["anti_cluster_does_not_consume_edit_token"] is True
    assert anti["boundary_at_6_is_kept"] is True
    assert anti["gap_of_5_is_dropped"] is True
    # tamper anti-cluster facts -> rejects
    tampered = _record()
    tampered["expected_anti_cluster"] = dict(
        tampered["expected_anti_cluster"],
        anti_cluster_min_bar_gap=4)
    assert c7r.validate_candidate_7_dry_run_review(
        tampered)["valid"] is False
    tampered2 = _record()
    tampered2["expected_anti_cluster"] = dict(
        tampered2["expected_anti_cluster"],
        anti_cluster_does_not_consume_edit_token=False)
    assert c7r.validate_candidate_7_dry_run_review(
        tampered2)["valid"] is False


def test_insufficient_history_and_strict_contraction_frozen():
    record = _record()
    hist = record["expected_insufficient_history_fact"]
    assert hist["min_event_index"] == 118
    assert hist["scanner_skips_below_min"] is True
    assert hist["fixture_with_warmup_30_attempts"] == 0
    assert hist["fixture_with_warmup_95_attempts"] == 0
    strict = record["expected_strict_contraction_fact"]
    assert strict["rule"] == "strict_less_than_0_6_x_rolling_avg"
    assert strict["equality_at_0_6_rejects"] is True


def test_universe_enforcement_frozen():
    record = _record()
    uni = record["expected_universe_enforcement"]
    assert uni["universe"] == ["BTCUSD"]
    assert uni["non_btcusd_raises_valueerror"] is True
    assert uni["non_list_bars_raises_valueerror"] is True


def test_wider_stop_and_floor_facts_frozen():
    record = _record()
    stop = record["expected_wider_stop_facts"]
    assert stop["formula"] == (
        "max(WIDER_STOP_ATR_MULTIPLIER * atr14, "
        "structure_stop_distance)")
    assert stop["wider_stop_atr_multiplier"] == 1.5
    assert stop["structure_lookback_bars"] == 10
    sw = stop["structure_wider_path_proven_at_entry_100_low_92_atr_2"]
    assert sw == {"atr_stop_distance": 3.0,
                  "structure_stop_distance": 8.0,
                  "stop_distance": 8.0, "stop_price": 92.0,
                  "valid": True}
    aw = stop["atr_wider_path_proven_at_entry_100_low_99_atr_4"]
    assert aw == {"atr_stop_distance": 6.0,
                  "structure_stop_distance": 1.0,
                  "stop_distance": 6.0, "stop_price": 94.0,
                  "valid": True}
    floor = record["expected_floor_facts"]
    assert floor["fee_round_trip_bps"] == 27.0
    assert floor["target_distance_floor_bps"] == 81.0
    assert floor[
        "tiny_stop_distance_1_at_entry_50000_all_variants_fail"] is (
        True)
    assert floor[
        "stop_distance_250_at_entry_50000_all_variants_pass"] is True
    assert floor["stop_distance_at_40_bps_only_3r_and_4r_pass"] == {
        "2r": False, "3r": True, "4r": True}


def test_frozen_findings_tuple_exact():
    findings = _record()["frozen_review_findings"]
    expected_phrases = (
        "one accepted setup with floor pass at 2r/3r/4r",
        "structure-wider stop",
        "min_event_index = 118",
        "5-bar contraction window",
        "strict less-than 0.6 threshold rejects equality",
        "expansion multiplier 1.7x",
        "close at midpoint",
        "btcusd-only universe is enforced",
        "non-list bars raises valueerror",
        "wider-stop formula",
        "81 bps floor per variant",
        "anti-cluster gap of 6 keeps boundary",
        "does NOT consume the single c7 edit token",
        "zero dry-run failures",
    )
    joined = " || ".join(findings)
    for phrase in expected_phrases:
        assert phrase in joined, phrase


def test_review_only_no_downstream_unlocks_or_capability():
    record = _record()
    assert record["is_review_only"] is True
    for key in ("runs_real_candle_detection", "runs_relabel",
                "runs_replay", "labels_now",
                "runs_real_detection_now", "runs_replay_now",
                "scores_now", "stages_data_now",
                "fetches_data", "calls_api", "uses_network",
                "uses_credentials", "uses_wallet", "uses_account",
                "connects_broker", "connects_exchange",
                "uses_real_money", "contains_order_logic",
                "contains_portfolio_allocation_logic",
                "starts_scheduler", "sends_notifications",
                "auto_commits", "auto_pushes",
                "creates_runners_now", "creates_data_artifacts_now",
                "modifies_staged_market_data",
                "authorizes_paper_execution",
                "authorizes_micro_live",
                "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate",
                "unlocks_real_candle_detection",
                "unlocks_labels_now", "unlocks_replay_now",
                "unlocks_relabel_now",
                "claims_profitability", "executes", "writes_files"):
        assert record[key] is False, key
        tampered = dict(record)
        tampered[key] = True
        assert c7r.validate_candidate_7_dry_run_review(
            tampered)["valid"] is False, key
    assert record["paper_trading_gate_locked"] is True
    assert record["micro_live_gate_locked"] is True
    assert record["live_gate_locked"] is True


def test_claim_locks_held():
    locks = _record()["claim_locks"]
    for lock in (
            "no_real_candle_detection_authorized_by_this_gate",
            "no_labels_authorized_by_this_gate",
            "no_replay_authorized_by_this_gate",
            "no_relabel_authorized_by_this_gate",
            "no_paper_approval", "no_live_approval",
            "no_execution_approval", "no_winner_wording",
            "no_profitability_claim",
            "anti_cluster_gap_remains_proposal_level_locked"):
        assert lock in locks, lock


def test_recompute_pipeline_catches_detector_drift():
    # If the pushed detector module is replaced with a stub whose
    # dry-run verdict differs, the review must flip to REJECTED.
    import sparta_commander.volatility_compression_expansion_v1_detector_dry_run_review_contract as mod
    original = mod._det.run_c7_detector_dry_run
    try:
        mod._det.run_c7_detector_dry_run = (
            lambda: {"verdict": "SOMETHING_ELSE",
                     "failures": [], "fixtures": {},
                     "uses_synthetic_fixtures_only": True,
                     "reads_real_candles": False,
                     "reads_staged_data": False,
                     "reads_any_files": False})
        rec_bad = mod.build_candidate_7_dry_run_review()
        assert rec_bad["verdict"] == c7r.VERDICT_C7R_REJECTED
        assert any("dry_run_verdict_mismatch" in f
                   for f in rec_bad["failures"])
    finally:
        mod._det.run_c7_detector_dry_run = original
    # baseline restored
    assert mod.build_candidate_7_dry_run_review()["verdict"] == (
        c7r.VERDICT_C7R_FROZEN)


def test_chain_blocks_when_ledger_breaks():
    import sparta_commander.volatility_compression_expansion_v1_detector_dry_run_review_contract as mod
    originals = {key: getattr(mod, key) for key in
                 ("C1_STATUS", "C2_STATUS", "C3_STATUS", "C4_STATUS",
                  "C5_STATUS", "C6_STATUS")}
    try:
        for key in originals:
            setattr(mod, key, "APPROVED_FOR_TRADING")
            rec = mod.build_candidate_7_dry_run_review()
            assert rec["verdict"] == c7r.VERDICT_C7R_BLOCKED, key
            assert "six_record_ledger_broken" in rec["blockers"], key
            setattr(mod, key, originals[key])
    finally:
        for key, value in originals.items():
            setattr(mod, key, value)
    assert mod.build_candidate_7_dry_run_review()["verdict"] == (
        c7r.VERDICT_C7R_FROZEN)


def test_label_next_action_and_module_purity():
    record = _record()
    assert record["next_required_action"] == (
        "HUMAN_APPROVED_CANDIDATE_7_REAL_CANDLE_DETECTION")
    assert c7r.VERDICT_C7R_FROZEN == "CANDIDATE_7_DRY_RUN_REVIEW_FROZEN"
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in c7r.NEXT_REQUIRED_ACTION.upper(), banned
    assert c7r.get_candidate_7_dry_run_review_label() == c7r.C7R_LABEL
    assert "READ-ONLY" in c7r.C7R_LABEL
    assert "RESEARCH ONLY" in c7r.C7R_LABEL
    assert "SYNTHETIC OUTCOMES ONLY" in c7r.C7R_LABEL
    assert "NOT A PROFITABILITY CLAIM" in c7r.C7R_LABEL
    src = open(c7r.__file__, encoding="utf-8").read()
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
