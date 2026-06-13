"""Tests for the Candidate #8 formal rejection record (8th
rejected-family ledger entry).

Verifies: chain-gate on the seven-record ledger + the full pushed C8
chain through replay review + V3 + V2 + Recommendation V1 +
Autopilot V1; REJECTION_STATUS = REJECTED_KEPT_ON_RECORD;
FUTURE_FAMILY_BLACKLIST_ADDITION = liquidity_sweep_mean_reversion;
ledger position = 8; edit allowance NOT spent (token preserved
unconsumed); detection evidence (3840 bars, 133/73/51/60/22, status
breakdown) frozen; replay evidence (per-variant counts, gross/net R
sums, all-three-net-negative) frozen; SHA pins (labels artifact,
replay artifacts, staged source CSVs) frozen; all downstream
capability flags False; AST/purity green."""

from __future__ import annotations

import ast
import subprocess

import sparta_commander.liquidity_sweep_mean_reversion_v1_detector_dry_run_review_contract as c8r
import sparta_commander.liquidity_sweep_mean_reversion_v1_detector_spec_dry_run_contract as c8d
import sparta_commander.liquidity_sweep_mean_reversion_v1_family_proposal_contract as c8p
import sparta_commander.liquidity_sweep_mean_reversion_v1_real_candle_labels_review_contract as c8l
import sparta_commander.liquidity_sweep_mean_reversion_v1_rejection_record as rj8
import sparta_commander.liquidity_sweep_mean_reversion_v1_replay_review_contract as c8rr
import sparta_commander.liquidity_sweep_mean_reversion_v1_spec_review_contract as c8s
import sparta_commander.strategy_factory_autopilot_research_loop_v1_contract as ap
import sparta_commander.strategy_factory_candidate_recommendation_v1_contract as rec
import sparta_commander.strategy_factory_overnight_research_autopilot_v2_contract as oap2
import sparta_commander.strategy_factory_rejected_family_blacklist_v3_contract as bl3


def _tracked_paths():
    return subprocess.check_output(
        ["git", "ls-files"]).decode("utf-8").splitlines()


def _record():
    return rj8.build_c8_rejection_record(".", _tracked_paths())


# ---- chain gate + recorded verdict ----------------------------------------

def test_rejection_recorded_and_chain_gates_all_certify():
    assert c8p.build_candidate_8_family_proposal()["verdict"] == (
        c8p.VERDICT_C8P_READY)
    assert c8s.build_candidate_8_spec_review()["verdict"] == (
        c8s.VERDICT_C8S_READY)
    assert c8d.build_candidate_8_detector_spec_contract()[
        "verdict"] == c8d.VERDICT_C8D_READY
    assert c8r.build_candidate_8_dry_run_review()["verdict"] == (
        c8r.VERDICT_C8R_FROZEN)
    assert c8l.build_c8_labels_review(
        ".", _tracked_paths())["verdict"] == c8l.VERDICT_C8L_FROZEN
    assert c8rr.build_c8_replay_review(
        ".", _tracked_paths())["verdict"] == (
            c8rr.VERDICT_C8RR_FROZEN)
    assert bl3.build_rejected_family_blacklist_v3()["verdict"] == (
        bl3.VERDICT_BL3_READY)
    assert oap2.build_overnight_research_autopilot_v2_contract()[
        "verdict"] == oap2.VERDICT_OAP2_READY
    assert rec.build_candidate_recommendation()["verdict"] == (
        rec.VERDICT_CR_READY)
    assert ap.build_autopilot_loop_contract()["verdict"] == (
        ap.VERDICT_AP_READY)
    record = _record()
    assert record["verdict"] == rj8.VERDICT_RJ8_RECORDED
    assert record["blockers"] == []
    assert rj8.validate_c8_rejection_record(record)["valid"] is True


def test_rejection_status_and_classification_constants():
    assert rj8.REJECTION_STATUS == "REJECTED_KEPT_ON_RECORD"
    assert "ALL_REPLAY_VARIANTS" in rj8.REJECTION_REASON
    assert "NET_NEGATIVE" in rj8.REJECTION_REASON
    assert "EDIT_TOKEN_NOT_SPENT" in rj8.REJECTION_REASON
    assert "EDIT_TOKEN_NOT_SPENT" in rj8.EDIT_CLASSIFICATION
    assert "DEEP" in rj8.REPLAY_CLASSIFICATION
    assert "NOT_NEAR_MISS" in rj8.REPLAY_CLASSIFICATION
    assert rj8.FUTURE_FAMILY_BLACKLIST_ADDITION == (
        "liquidity_sweep_mean_reversion")
    record = _record()
    assert record["rejection_status"] == "REJECTED_KEPT_ON_RECORD"
    assert record["ledger_position"] == 8


def test_ledger_position_and_prior_families():
    record = _record()
    assert record["ledger_position"] == 8
    assert record["ledger_now_contains_eight_records"] is True
    assert record["prior_seven_records_unchanged"] is True
    assert tuple(record["prior_ledger_families"]) == (
        "ny_session_fvg_choch_v3",
        "crypto_intraday_breakout_pullback_structure_v2",
        "btc_sol_long_trend_continuation_v1",
        "sol_btc_long_1h_swing_structure",
        "eth_sol_relative_strength_pullback_continuation_v1",
        "multi_symbol_relative_strength_rotation_filter",
        "volatility_compression_expansion")


def test_edit_token_was_not_spent():
    record = _record()
    state = record["expected_edit_token_state"]
    assert state["single_pre_committed_edit_originally_allowed"] == 1
    assert state["edit_token_spent_at_any_gate"] is False
    assert state["edit_token_consumed_by_anti_cluster"] is False
    assert state["edit_token_consumed_by_sample_size_threshold"] is (
        False)
    assert state["edit_token_consumed_by_rejection"] is False
    assert state["edits_remaining_at_rejection_time"] == 1
    assert state["rejection_chose_close_over_relaxation"] is True
    assert state["no_further_c8_edit_allowed_after_rejection"] is True
    assert state[
        "anti_cluster_gap_remained_proposal_level_locked"] is True
    assert state[
        "sample_size_threshold_remained_proposal_level_locked"] is (
        True)
    assert record["edit_allowance_spent"] is False
    assert record[
        "edit_allowance_preserved_unconsumed_but_family_closed"] is (
        True)
    assert record["applies_an_edit"] is False


def test_chain_blocks_when_ledger_breaks():
    import sparta_commander.liquidity_sweep_mean_reversion_v1_rejection_record as mod
    originals = {k: getattr(mod, k) for k in
                 ("C1_STATUS", "C2_STATUS", "C3_STATUS",
                  "C4_STATUS", "C5_STATUS", "C6_STATUS",
                  "C7_STATUS")}
    try:
        for key in originals:
            setattr(mod, key, "APPROVED_FOR_TRADING")
            record = mod.build_c8_rejection_record(
                ".", _tracked_paths())
            assert record["verdict"] == rj8.VERDICT_RJ8_BLOCKED, key
            assert "seven_record_ledger_broken" in record[
                "blockers"], key
            setattr(mod, key, originals[key])
    finally:
        for k, v in originals.items():
            setattr(mod, k, v)
    assert mod.build_c8_rejection_record(
        ".", _tracked_paths())["verdict"] == rj8.VERDICT_RJ8_RECORDED


# ---- frozen detection + replay evidence -----------------------------------

def test_detection_evidence_frozen():
    det = _record()["expected_detection_evidence"]
    assert det["head_at_labels_review"] == (
        "fb208252a5551937cb431eb25706b96ca92d43b7")
    assert det["bars_scanned"] == 3840
    assert det["total_attempts"] == 133
    assert det["accepted_pre_anti_cluster"] == 73
    assert det["accepted_post_anti_cluster"] == 51
    assert det["rejected_by_scanner"] == 60
    assert det["dropped_by_anti_cluster"] == 22
    assert det["status_breakdown"] == {
        "accepted_for_replay_review": 73,
        "rejected_no_qualifying_reclaim_within_4_bars": 57,
        "rejected_geometry_floor": 3,
        "rejected_clustered_within_8_bars_of_prior_accepted": 22}
    assert det["sample_size_adequacy_satisfied"] is True
    assert det["sample_size_adequacy_threshold_min_accepted"] == 20
    assert det["sample_size_adequacy_did_not_consume_edit_token"] is (
        True)
    assert det["anti_cluster_min_bar_gap"] == 8
    assert det["anti_cluster_did_not_consume_edit_token"] is True


def test_replay_evidence_frozen_all_three_variants_net_negative():
    rev = _record()["expected_replay_evidence"]
    assert rev["head_at_replay_review"] == (
        "146dce2976f1bece54122ec1f7652df58324655f")
    assert rev["accepted_input_count"] == 51
    assert rev[
        "all_three_variants_structurally_net_negative_in_sample"
    ] is True
    assert rev[
        "any_variant_structurally_net_positive_in_sample_decisive"
        "_only"] is False
    assert rev["best_variant_label"] == "2r"
    assert rev["best_variant_net_r_sum"] == -45.77781173130582
    assert rev["best_variant_is_a_near_miss"] is False
    # per-variant
    v2 = rev["variant_2r"]
    assert v2["counts"] == {
        "hit": 11, "miss": 38, "miss_same_bar_straddle": 0,
        "timeout": 2, "open_at_sample_end": 0,
        "no_start_bar_in_sample": 0}
    assert v2["gross_r_sum_decisive"] == -15.814923512147077
    assert v2["net_r_sum_decisive"] == -45.77781173130582
    assert v2[
        "structurally_net_positive_in_sample_decisive_only"] is False
    v3 = rev["variant_3r"]
    assert v3["counts"]["hit"] == 3
    assert v3["net_r_sum_decisive"] == -58.83950931955688
    assert v3[
        "structurally_net_positive_in_sample_decisive_only"] is False
    v4 = rev["variant_4r"]
    assert v4["counts"]["hit"] == 0
    assert v4["net_r_sum_decisive"] == -65.78368010338602
    assert v4[
        "structurally_net_positive_in_sample_decisive_only"] is False


def test_artifact_sha_pins_pulled_forward():
    record = _record()
    assert record["expected_detector_labels_path"] == (
        "data/liquidity_sweep_c8/detector_labels/"
        "c8_detector_labels_2026-05-02_2026-06-10.json")
    assert record["expected_replay_ledger_path"] == (
        "data/liquidity_sweep_c8/replay_results/"
        "c8_replay_ledger_2026-05-02_2026-06-10.json")
    det = record["expected_detection_evidence"]
    assert det["labels_sha256"] == (
        "f323ff7188b672a9af2521e30d3b7a4052217d86c7bbb0f8c0e8"
        "6405cb81fee3")
    rev = record["expected_replay_evidence"]
    assert rev["ledger_sha256"] == (
        "b7b12b8ef9ffe9bf3ab587ba4bd2b097d391a78f6761e52c7103"
        "146de58dfb92")
    assert rev["summary_sha256"] == (
        "2be19e38195a7a2414c661b6d3ec84a5fdc371c05e6cc7d46119"
        "9683944454db")


def test_staged_source_data_sha_pins_frozen():
    pins = _record()["expected_staged_source_shas"]
    assert pins[
        "data/ny_fvg_choch/staged/BTCUSD_15m_2026-05-02_2026-06-09.csv"
    ] == ("4ee373b28caeafa47d463e0fc2582f1958b877a8f05df0714a0a"
          "fd1298ee9f14")
    assert pins[
        "data/ny_fvg_choch/staged/BTCUSD_15m_2026-06-01_2026-06-10.csv"
    ] == ("4bb50873df5194de65315bf44f1823d17922e445745401eb01aa"
          "1670aed4956d")


# ---- rejection narrative + seeds -----------------------------------------

def test_rejection_facts_and_evidence_notes():
    record = _record()
    facts = " || ".join(record["rejection_facts"])
    assert "candidate #8 is rejected" in facts
    assert "eighth ledger entry" in facts
    assert "REJECT WITHOUT SPENDING THE SINGLE C8 EDIT TOKEN" in facts
    assert "single pre-committed edit allowance was preserved " \
        "unconsumed" in facts
    assert "deeply negative and is NOT a near-miss" in facts
    assert "no profitability claim permitted" in facts
    assert "no winner wording permitted" in facts
    notes = " || ".join(record["evidence_notes"])
    assert ("liquidity-sweep-mean-reversion hypothesis is unsupported"
            in notes)
    assert "no replay re-run was attempted" in notes
    assert "anti-cluster gap stayed proposal-level locked at 8 bars" \
        in notes
    assert "sample-size adequacy threshold stayed proposal-level " \
        "locked at 20 accepted setups" in notes
    assert "single c8 edit token was never spent" in notes


def test_seeds_for_future_families_only_never_rescue():
    record = _record()
    assert record["seeds_are_never_rescue_paths"] is True
    seeds = " || ".join(record["seeds_for_future_families_only"])
    assert "do_not_reuse_c8_as_is" in seeds
    assert "any_future_candidate_must_be_a_new_clean_hypothesis" \
        in seeds
    assert "structural_cleanliness_alone_does_not_produce_edge" \
        in seeds
    assert "fee_aware_geometry_with_an_81_bps_floor_remains_in" \
        "violable" in seeds


def test_future_family_blacklist_export_and_pushed_chain():
    record = _record()
    assert record["future_family_blacklist_addition"] == (
        "liquidity_sweep_mean_reversion")
    assert "candidate_8_rejected" in record[
        "future_family_blacklist_reason"]
    assert "edit_token_not_spent" in record[
        "future_family_blacklist_reason"]
    chain = record["pushed_evidence_chain"]
    assert "liquidity_sweep_mean_reversion_v1_family_proposal_contract" \
        in chain
    assert "liquidity_sweep_mean_reversion_v1_spec_review_contract" \
        in chain
    assert (
        "liquidity_sweep_mean_reversion_v1_detector_spec_dry_run"
        "_contract") in chain
    assert (
        "liquidity_sweep_mean_reversion_v1_detector_dry_run_review"
        "_contract") in chain
    assert (
        "liquidity_sweep_mean_reversion_v1_real_candle_labels_review"
        "_contract") in chain
    assert "liquidity_sweep_mean_reversion_v1_replay_review_contract" \
        in chain
    assert "strategy_factory_rejected_family_blacklist_v3_contract" \
        in chain


# ---- downstream gates remain locked ---------------------------------------

def test_no_downstream_gate_unlocked_and_no_trading_capability():
    record = _record()
    assert record["paper_trading_gate_locked"] is True
    assert record["micro_live_gate_locked"] is True
    assert record["live_gate_locked"] is True
    assert record["candidate_8_may_continue_as_is"] is False
    assert record["candidate_8_may_be_re_proposed_as_is"] is False
    assert record[
        "candidate_8_may_receive_an_edit_after_rejection"] is False
    assert record["further_detections_authorized"] is False
    assert record["further_replays_authorized"] is False
    assert record["further_relabels_authorized"] is False
    for key in ("runs_real_candle_detection",
                "runs_real_detection_now", "labels_now",
                "runs_replay", "runs_replay_now", "runs_relabel",
                "scores_now", "stages_data_now",
                "fetches_data", "calls_api", "uses_network",
                "uses_credentials", "uses_wallet", "uses_account",
                "connects_broker", "connects_exchange",
                "uses_real_money", "contains_order_logic",
                "contains_portfolio_allocation_logic",
                "starts_scheduler", "sends_notifications",
                "auto_commits", "auto_pushes",
                "creates_runners_now", "creates_data_artifacts_now",
                "creates_detector_implementation_now",
                "computes_pnl_now", "applies_an_edit",
                "modifies_staged_market_data",
                "modifies_detector_artifacts",
                "modifies_labels_artifacts",
                "modifies_replay_artifacts",
                "authorizes_paper_execution",
                "authorizes_micro_live", "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate",
                "claims_profitability", "executes", "writes_files"):
        assert record[key] is False, key
        tampered = _record()
        tampered[key] = True
        assert rj8.validate_c8_rejection_record(
            tampered)["valid"] is False, key


def test_label_and_next_required_action():
    record = _record()
    assert record["next_required_action"] == (
        "HUMAN_DECISION_ON_NEXT_CANDIDATE_FAMILY")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH",
                   "EXECUTE", "EXECUTION", "BACKTEST", "BASELINE",
                   "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in rj8.NEXT_REQUIRED_ACTION.upper(), banned
    assert rj8.get_c8_rejection_record_label() == rj8.RJ8_LABEL
    assert rj8.RJ8_MODE == "RESEARCH_ONLY"
    for phrase in ("READ-ONLY", "RESEARCH ONLY",
                   "REJECTED KEPT ON RECORD",
                   "ALL REPLAY VARIANTS NET-NEGATIVE",
                   "EDIT TOKEN NOT SPENT",
                   "NOT A PROFITABILITY CLAIM"):
        assert phrase in rj8.RJ8_LABEL, phrase
    for banned_phrase in ("WINNER", "PROFITABLE",
                          "EDGE CONFIRMED",
                          "APPROVED FOR PAPER",
                          "APPROVED FOR LIVE"):
        assert banned_phrase not in rj8.RJ8_LABEL.upper(), (
            banned_phrase)


# ---- module purity --------------------------------------------------------

def test_module_purity_no_banned_imports_no_open_no_main():
    src = open(rj8.__file__, encoding="utf-8").read()
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
