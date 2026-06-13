"""Tests for the Candidate #8 replay review / evidence-freeze
contract (LIQUIDITY_SWEEP_MEAN_REVERSION_V1).

Verifies: chain-gate on the seven-record ledger + the full C8 chain
through the pushed labels review + V3 + V2 + REC + AP; SHA-256 pins
of the untracked replay-ledger and replay-summary artifacts and the
upstream detector labels + detector summary + the two staged BTCUSD
15m CSVs; frozen replay policy (96-bar timeout, 27 bps fees, 81 bps
floor, REDUCE-OR-KEEP-ONLY non-overlap, STOP-FIRST same-bar
straddle); per-variant counts and gross/net R sums for 2R, 3R, 4R;
honest all-three-variants-net-negative-in-sample finding; single C8
edit token NOT consumed; runner and artifacts remain untracked;
contract AST/purity green."""

from __future__ import annotations

import ast
import subprocess

import sparta_commander.liquidity_sweep_mean_reversion_v1_detector_dry_run_review_contract as c8r
import sparta_commander.liquidity_sweep_mean_reversion_v1_detector_spec_dry_run_contract as c8d
import sparta_commander.liquidity_sweep_mean_reversion_v1_family_proposal_contract as c8p
import sparta_commander.liquidity_sweep_mean_reversion_v1_real_candle_labels_review_contract as c8l
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
    return c8rr.build_c8_replay_review(".", _tracked_paths())


# ---- chain gate + frozen verdict -------------------------------------------

def test_replay_review_frozen_and_chain_gates_all_certify():
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
    assert bl3.build_rejected_family_blacklist_v3()["verdict"] == (
        bl3.VERDICT_BL3_READY)
    assert oap2.build_overnight_research_autopilot_v2_contract()[
        "verdict"] == oap2.VERDICT_OAP2_READY
    assert rec.build_candidate_recommendation()["verdict"] == (
        rec.VERDICT_CR_READY)
    assert ap.build_autopilot_loop_contract()["verdict"] == (
        ap.VERDICT_AP_READY)
    record = _record()
    assert record["verdict"] == c8rr.VERDICT_C8RR_FROZEN
    assert record["blockers"] == []
    assert record["failures"] == []
    assert c8rr.validate_c8_replay_review(record)["valid"] is True


def test_seven_record_ledger_intact():
    record = _record()
    assert record["ledger_status_seven_records"] == [
        "REJECTED_KEPT_ON_RECORD"] * 7
    assert record["ledger_all_rejected_kept_on_record"] is True


def test_chain_blocks_when_ledger_breaks():
    import sparta_commander.liquidity_sweep_mean_reversion_v1_replay_review_contract as mod
    originals = {k: getattr(mod, k) for k in
                 ("C1_STATUS", "C2_STATUS", "C3_STATUS",
                  "C4_STATUS", "C5_STATUS", "C6_STATUS",
                  "C7_STATUS")}
    try:
        for key in originals:
            setattr(mod, key, "APPROVED_FOR_TRADING")
            record = mod.build_c8_replay_review(".",
                                                _tracked_paths())
            assert record["verdict"] == c8rr.VERDICT_C8RR_BLOCKED, key
            assert "seven_record_ledger_broken" in (
                record["blockers"]), key
            setattr(mod, key, originals[key])
    finally:
        for k, v in originals.items():
            setattr(mod, k, v)
    assert mod.build_c8_replay_review(
        ".", _tracked_paths())["verdict"] == c8rr.VERDICT_C8RR_FROZEN


# ---- SHA pins frozen ------------------------------------------------------

def test_replay_artifact_sha_pins_frozen():
    record = _record()
    assert record["expected_ledger_sha256"] == (
        "b7b12b8ef9ffe9bf3ab587ba4bd2b097d391a78f6761e52c7103"
        "146de58dfb92")
    assert record["expected_summary_sha256"] == (
        "2be19e38195a7a2414c661b6d3ec84a5fdc371c05e6cc7d46119"
        "9683944454db")
    assert record["head_at_replay"] == (
        "fb208252a5551937cb431eb25706b96ca92d43b7")
    assert record["runner_path_untracked_only"] == (
        "tools/c8_replay_once.py")
    assert record["ledger_path"] == (
        "data/liquidity_sweep_c8/replay_results/"
        "c8_replay_ledger_2026-05-02_2026-06-10.json")
    assert record["summary_path"] == (
        "data/liquidity_sweep_c8/replay_results/"
        "c8_replay_summary_2026-05-02_2026-06-10.json")
    for field in ("expected_ledger_sha256",
                  "expected_summary_sha256", "head_at_replay"):
        tampered = _record()
        tampered[field] = "0" * 64
        assert c8rr.validate_c8_replay_review(
            tampered)["valid"] is False, field


def test_detector_input_sha_pins_pulled_forward():
    record = _record()
    assert record["expected_detector_labels_sha256"] == (
        "f323ff7188b672a9af2521e30d3b7a4052217d86c7bbb0f8c0e8"
        "6405cb81fee3")
    assert record["expected_detector_summary_sha256"] == (
        "d1655123990b0080ef741bda49ea5baa20d6640c4b2d4476986f"
        "29deb2e4ae90")
    assert record["expected_detector_labels_path"] == (
        "data/liquidity_sweep_c8/detector_labels/"
        "c8_detector_labels_2026-05-02_2026-06-10.json")
    assert record["expected_detector_summary_path"] == (
        "data/liquidity_sweep_c8/detector_labels/"
        "c8_detector_summary_2026-05-02_2026-06-10.json")


def test_staged_source_data_sha_pins_frozen():
    record = _record()
    pins = record["expected_staged_shas"]
    assert pins[
        "data/ny_fvg_choch/staged/BTCUSD_15m_2026-05-02_2026-06-09.csv"
    ] == ("4ee373b28caeafa47d463e0fc2582f1958b877a8f05df0714a0a"
          "fd1298ee9f14")
    assert pins[
        "data/ny_fvg_choch/staged/BTCUSD_15m_2026-06-01_2026-06-10.csv"
    ] == ("4bb50873df5194de65315bf44f1823d17922e445745401eb01aa"
          "1670aed4956d")


# ---- frozen replay policy -------------------------------------------------

def test_replay_policy_frozen_27_bps_81_bps_96_bars_stop_first():
    policy = _record()["expected_replay_policy"]
    assert policy["timeout_bars"] == 96
    assert policy["fee_round_trip_bps"] == 27.0
    assert policy["target_distance_floor_bps"] == 81.0
    assert policy["variants"] == ["2r", "3r", "4r"]
    assert policy["same_bar_straddle_policy"] == (
        "stop_first_conservative_miss")
    assert policy["non_overlap_policy"] == (
        "reduce_or_keep_only_never_add")
    assert policy["evaluation_horizon_hours_at_15m"] == 24.0
    tampered = _record()
    tampered["expected_replay_policy"]["timeout_bars"] = 50
    assert c8rr.validate_c8_replay_review(
        tampered)["valid"] is False


# ---- frozen per-variant aggregates ---------------------------------------

def test_variant_aggregate_2r():
    record = _record()
    v = record["expected_variant_aggregates"]["2r"]
    assert v["variant_r_multiple"] == 2.0
    assert v["kept_count"] == 51
    assert v["dropped_overlap_count"] == 0
    assert v["decisive_count"] == 51
    assert v["open_or_truncated_count"] == 0
    assert v["counts"] == {
        "hit": 11, "miss": 38, "miss_same_bar_straddle": 0,
        "timeout": 2, "open_at_sample_end": 0,
        "no_start_bar_in_sample": 0}
    assert v["gross_r_sum_decisive"] == -15.814923512147077
    assert v["net_r_sum_decisive"] == -45.77781173130582
    assert v[
        "structurally_net_positive_in_sample_decisive_only"
    ] is False
    # Identity: counts sum == 51
    assert sum(v["counts"].values()) == 51


def test_variant_aggregate_3r():
    v = _record()["expected_variant_aggregates"]["3r"]
    assert v["variant_r_multiple"] == 3.0
    assert v["counts"] == {
        "hit": 3, "miss": 42, "miss_same_bar_straddle": 0,
        "timeout": 6, "open_at_sample_end": 0,
        "no_start_bar_in_sample": 0}
    assert v["gross_r_sum_decisive"] == -28.876621100398147
    assert v["net_r_sum_decisive"] == -58.83950931955688
    assert v[
        "structurally_net_positive_in_sample_decisive_only"
    ] is False
    assert sum(v["counts"].values()) == 51


def test_variant_aggregate_4r():
    v = _record()["expected_variant_aggregates"]["4r"]
    assert v["variant_r_multiple"] == 4.0
    assert v["counts"] == {
        "hit": 0, "miss": 43, "miss_same_bar_straddle": 0,
        "timeout": 8, "open_at_sample_end": 0,
        "no_start_bar_in_sample": 0}
    assert v["gross_r_sum_decisive"] == -35.82079188422728
    assert v["net_r_sum_decisive"] == -65.78368010338602
    assert v[
        "structurally_net_positive_in_sample_decisive_only"
    ] is False
    assert sum(v["counts"].values()) == 51


def test_per_variant_identity_checks_all_true():
    checks = _record()["expected_per_variant_identity_checks"]
    for key in ("2r_counts_sum_equals_kept",
                "3r_counts_sum_equals_kept",
                "4r_counts_sum_equals_kept",
                "2r_kept_plus_overlap_equals_accepted_input",
                "3r_kept_plus_overlap_equals_accepted_input",
                "4r_kept_plus_overlap_equals_accepted_input"):
        assert checks[key] is True, key


def test_accepted_input_count_51():
    assert _record()["expected_accepted_input_count"] == 51


# ---- headline net-negative finding ----------------------------------------

def test_all_three_variants_net_negative_in_sample():
    finding = _record()["expected_headline_finding"]
    assert finding[
        "all_three_variants_structurally_net_negative_in_sample"
    ] is True
    assert finding[
        "any_variant_structurally_net_positive_in_sample_decisive"
        "_only"] is False
    assert finding["no_edge_demonstrated"] is True
    assert finding["no_live_profitability_claimed"] is True
    assert finding["no_winner_designation"] is True
    assert finding["no_paper_approval"] is True
    assert finding["no_micro_live_approval"] is True
    assert finding["no_live_approval"] is True
    assert finding["no_edit_token_consumed_by_this_gate"] is True
    assert finding[
        "no_downstream_gate_unlocked_by_this_gate"] is True
    for key in ("no_edge_demonstrated",
                "no_live_profitability_claimed",
                "no_winner_designation",
                "no_edit_token_consumed_by_this_gate"):
        tampered = _record()
        tampered["expected_headline_finding"][key] = False
        assert c8rr.validate_c8_replay_review(
            tampered)["valid"] is False, key


def test_claim_locks_present_including_edit_token_lock():
    locks = _record()["claim_locks"]
    for required in (
            "no_profitability_claim", "no_paper_approval",
            "no_live_approval", "no_execution_approval",
            "no_winner_wording",
            "no_replay_re_run_authorized_by_this_gate",
            "no_relabel_authorized_by_this_gate",
            "no_detector_change_authorized_by_this_gate",
            "no_edit_token_applied_by_this_gate",
            "no_rejection_decision_made_by_this_gate",
            "anti_cluster_gap_remains_proposal_level_locked",
            "sample_size_threshold_remains_proposal_level_locked"):
        assert required in locks, required
    tampered = _record()
    tampered["claim_locks"] = []
    assert c8rr.validate_c8_replay_review(
        tampered)["valid"] is False


# ---- scope locks + summary self-claims -----------------------------------

def test_expected_scope_locks_all_true():
    locks = _record()["expected_scope_locks"]
    for key in ("no_paper_trading", "no_micro_live",
                "no_live_trading", "no_broker", "no_exchange",
                "no_wallet", "no_account", "no_credentials",
                "no_order_logic", "no_portfolio_allocation",
                "no_api", "no_network", "no_fetch",
                "no_notification", "no_scheduler",
                "no_relabel", "no_detector_change",
                "no_edit_token_use", "no_profitability_claim",
                "no_downstream_gate_unlock", "no_staging",
                "no_commit", "no_push"):
        assert locks[key] is True, key


def test_expected_summary_self_claims_frozen():
    claims = _record()["expected_summary_self_claims"]
    assert claims["candidate_id"] == "LIQUIDITY_SWEEP_MEAN_REVERSION_V1"
    assert claims["symbol"] == "BTCUSD"
    assert claims["timeframe"] == "15m"
    assert claims["direction"] == "long_only"
    assert claims["sample_tag"] == "2026-05-02_2026-06-10"
    assert claims["timeout_bars"] == 96
    assert claims["fee_round_trip_bps"] == 27.0
    assert claims["target_distance_floor_bps"] == 81.0
    assert claims["variants"] == ["2r", "3r", "4r"]
    assert claims["accepted_post_anti_cluster_input_count"] == 51
    assert claims["inputs_unchanged_during_evaluation"] is True


# ---- frozen review findings ----------------------------------------------

def test_frozen_review_findings_complete():
    findings = _record()["frozen_review_findings"]
    joined = " || ".join(findings)
    assert "51 accepted-post-anti-cluster" in joined
    assert "REDUCE-OR-KEEP-ONLY never add" in joined
    assert "STOP-FIRST conservative miss" in joined
    assert "27 bps round-trip fee" in joined
    assert "81 bps gross target-distance floor" in joined
    assert "variant 2r: 11 hit, 38 miss" in joined
    assert "variant 3r:  3 hit, 42 miss" in joined
    assert "variant 4r:  0 hit, 43 miss" in joined
    assert "structurally net-negative in this in-sample window" \
        in joined
    assert "NOT a live profitability claim" in joined
    assert "NO edge has been demonstrated" in joined
    assert "single c8 edit token has NOT been consumed" in joined
    assert "spend the single c8 edit token on a different " \
        "structural parameter" in joined
    assert "OR reject candidate 8" in joined


# ---- review-only safety / capability flags --------------------------------

def test_review_only_with_all_downstream_locked():
    record = _record()
    assert record["is_review_only"] is True
    assert record["current_loop_stage"] == (
        "detector_and_label_review")
    assert record["human_review_required"] is True
    assert record["paper_trading_gate_locked"] is True
    assert record["micro_live_gate_locked"] is True
    assert record["live_gate_locked"] is True
    for key in ("edit_token_applied_by_this_gate",
                "rejection_decision_made_by_this_gate",
                "replay_re_run_authorized_by_this_gate",
                "relabel_authorized_by_this_gate",
                "detector_change_authorized_by_this_gate"):
        assert record[key] is False, key
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
                "computes_pnl_now",
                "modifies_staged_market_data",
                "authorizes_paper_execution",
                "authorizes_micro_live", "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate",
                "unlocks_real_candle_detection",
                "unlocks_replay_now", "unlocks_relabel_now",
                "unlocks_edit_token_now", "claims_profitability",
                "executes", "writes_files"):
        assert record[key] is False, key
        tampered = _record()
        tampered[key] = True
        assert c8rr.validate_c8_replay_review(
            tampered)["valid"] is False, key


def test_next_required_action_and_label_text():
    record = _record()
    assert record["next_required_action"] == (
        "HUMAN_DECISION_C8_SPEND_SINGLE_EDIT_OR_REJECT_ON_NET"
        "_NEGATIVE_IN_SAMPLE")
    for banned in ("PROMOTE", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER",
                   "LIVE", "BROKER", "EXCHANGE", "AUTOMATION",
                   "ORDER", "TRACK"):
        assert banned not in c8rr.NEXT_REQUIRED_ACTION.upper(), (
            banned)
    assert c8rr.get_candidate_8_replay_review_label() == (
        c8rr.C8RR_LABEL)
    assert c8rr.C8RR_MODE == "RESEARCH_ONLY"
    for phrase in ("READ-ONLY", "RESEARCH ONLY",
                   "ALL VARIANTS NET-NEGATIVE IN-SAMPLE",
                   "NO EDGE DEMONSTRATED",
                   "NOT A PROFITABILITY CLAIM",
                   "NOT A RESCUE"):
        assert phrase in c8rr.C8RR_LABEL, phrase
    for banned_phrase in ("WINNER", "PROFITABLE",
                          "EDGE CONFIRMED",
                          "APPROVED FOR PAPER",
                          "APPROVED FOR LIVE"):
        assert banned_phrase not in c8rr.C8RR_LABEL.upper(), (
            banned_phrase)


def test_runner_and_artifacts_remain_untracked_in_git():
    tracked = _tracked_paths()
    for path in (c8rr.RUNNER_PATH, c8rr.LEDGER_PATH,
                 c8rr.SUMMARY_PATH):
        assert path not in tracked, path
    # The c8 replay-results operational data directory must stay
    # untracked.
    for tracked_path in tracked:
        assert not tracked_path.startswith(
            "data/liquidity_sweep_c8/replay_results/"), tracked_path
    record = _record()
    assert record["failures"] == []


# ---- module purity --------------------------------------------------------

def test_module_purity_no_banned_imports_no_open_no_main():
    src = open(c8rr.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir",
                 "rmdir", "rename", "touch("):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned_mods = {"urllib", "requests", "socket", "http", "ccxt",
                   "smtplib", "subprocess", "websockets", "aiohttp",
                   "schedule", "apscheduler", "threading", "asyncio",
                   "time", "sched", "telegram", "email", "csv",
                   "pandas", "os", "io", "shutil", "databento",
                   "ssl", "ftplib", "datetime", "statistics",
                   "random"}
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
