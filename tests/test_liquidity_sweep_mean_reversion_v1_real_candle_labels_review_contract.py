"""Tests for the Candidate #8 real-candle labels review / evidence-
freeze contract (LIQUIDITY_SWEEP_MEAN_REVERSION_V1).

Verifies: chain-gate on the seven-record ledger + C8 family proposal
+ C8 spec review + C8 detector spec + C8 dry-run review + V3
blacklist + V2 + Recommendation V1 + Autopilot V1; SHA-256 pins of
the untracked detector-labels and detector-summary artifacts and the
two staged BTCUSD 15m CSVs; frozen counts (3840 bars, 133 attempts,
73 accepted pre, 51 accepted post, 60 rejected, 22 anti-cluster
drops); identity checks; status breakdown; sample-size adequacy
SATISFIED (51 >= 20) without consuming the edit token; anti-cluster
gap = 8 without consuming the edit token; downstream replay /
relabel / paper / live gates remain locked; runner and artifacts
remain untracked; AST/purity green for the contract."""

from __future__ import annotations

import ast
import subprocess

import sparta_commander.liquidity_sweep_mean_reversion_v1_detector_dry_run_review_contract as c8r
import sparta_commander.liquidity_sweep_mean_reversion_v1_detector_spec_dry_run_contract as c8d
import sparta_commander.liquidity_sweep_mean_reversion_v1_family_proposal_contract as c8p
import sparta_commander.liquidity_sweep_mean_reversion_v1_real_candle_labels_review_contract as c8l
import sparta_commander.liquidity_sweep_mean_reversion_v1_spec_review_contract as c8s
import sparta_commander.strategy_factory_autopilot_research_loop_v1_contract as ap
import sparta_commander.strategy_factory_candidate_recommendation_v1_contract as rec
import sparta_commander.strategy_factory_overnight_research_autopilot_v2_contract as oap2
import sparta_commander.strategy_factory_rejected_family_blacklist_v3_contract as bl3


def _tracked_paths():
    return subprocess.check_output(
        ["git", "ls-files"]).decode("utf-8").splitlines()


def _record():
    return c8l.build_c8_labels_review(".", _tracked_paths())


# ---- chain gate + frozen verdict -------------------------------------------

def test_labels_review_frozen_and_chain_gates_all_certify():
    assert c8p.build_candidate_8_family_proposal()["verdict"] == (
        c8p.VERDICT_C8P_READY)
    assert c8s.build_candidate_8_spec_review()["verdict"] == (
        c8s.VERDICT_C8S_READY)
    assert c8d.build_candidate_8_detector_spec_contract()[
        "verdict"] == c8d.VERDICT_C8D_READY
    assert c8r.build_candidate_8_dry_run_review()["verdict"] == (
        c8r.VERDICT_C8R_FROZEN)
    assert bl3.build_rejected_family_blacklist_v3()["verdict"] == (
        bl3.VERDICT_BL3_READY)
    assert oap2.build_overnight_research_autopilot_v2_contract()[
        "verdict"] == oap2.VERDICT_OAP2_READY
    assert rec.build_candidate_recommendation()["verdict"] == (
        rec.VERDICT_CR_READY)
    assert ap.build_autopilot_loop_contract()["verdict"] == (
        ap.VERDICT_AP_READY)
    record = _record()
    assert record["verdict"] == c8l.VERDICT_C8L_FROZEN
    assert record["blockers"] == []
    assert record["failures"] == []
    assert c8l.validate_c8_labels_review(record)["valid"] is True


def test_seven_record_ledger_intact():
    record = _record()
    assert record["ledger_status_seven_records"] == [
        "REJECTED_KEPT_ON_RECORD"] * 7
    assert record["ledger_all_rejected_kept_on_record"] is True


def test_chain_blocks_when_ledger_breaks():
    import sparta_commander.liquidity_sweep_mean_reversion_v1_real_candle_labels_review_contract as mod
    originals = {k: getattr(mod, k) for k in
                 ("C1_STATUS", "C2_STATUS", "C3_STATUS",
                  "C4_STATUS", "C5_STATUS", "C6_STATUS",
                  "C7_STATUS")}
    try:
        for key in originals:
            setattr(mod, key, "APPROVED_FOR_TRADING")
            record = mod.build_c8_labels_review(".",
                                                _tracked_paths())
            assert record["verdict"] == c8l.VERDICT_C8L_BLOCKED, key
            assert "seven_record_ledger_broken" in (
                record["blockers"]), key
            setattr(mod, key, originals[key])
    finally:
        for k, v in originals.items():
            setattr(mod, k, v)
    assert mod.build_c8_labels_review(
        ".", _tracked_paths())["verdict"] == c8l.VERDICT_C8L_FROZEN


# ---- SHA pins frozen ------------------------------------------------------

def test_artifact_sha_pins_frozen():
    record = _record()
    assert record["expected_labels_sha256"] == (
        "f323ff7188b672a9af2521e30d3b7a4052217d86c7bbb0f8c0e8"
        "6405cb81fee3")
    assert record["expected_summary_sha256"] == (
        "d1655123990b0080ef741bda49ea5baa20d6640c4b2d4476986f"
        "29deb2e4ae90")
    assert record["head_at_detection"] == (
        "6d62f936e135cedc5317edf92cb875de31333215")
    assert record["runner_path_untracked_only"] == (
        "tools/c8_real_candle_detection_once.py")
    assert record["labels_path"] == (
        "data/liquidity_sweep_c8/detector_labels/"
        "c8_detector_labels_2026-05-02_2026-06-10.json")
    assert record["summary_path"] == (
        "data/liquidity_sweep_c8/detector_labels/"
        "c8_detector_summary_2026-05-02_2026-06-10.json")
    for field in ("expected_labels_sha256",
                  "expected_summary_sha256", "head_at_detection"):
        tampered = _record()
        tampered[field] = "0" * 64
        assert c8l.validate_c8_labels_review(
            tampered)["valid"] is False, field


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
    tampered = _record()
    tampered["expected_staged_shas"] = {}
    assert c8l.validate_c8_labels_review(
        tampered)["valid"] is False


# ---- frozen counts --------------------------------------------------------

def test_frozen_bars_scanned_window_and_counts():
    record = _record()
    assert record["expected_sample_tag"] == "2026-05-02_2026-06-10"
    assert record["expected_start_inclusive_utc"] == (
        "2026-05-02T00:00:00Z")
    assert record["expected_end_inclusive_utc"] == (
        "2026-06-10T23:45:00Z")
    assert record["expected_bars_scanned"] == 3840
    assert record["expected_first_bar_time"] == (
        "2026-05-02T00:00:00Z")
    assert record["expected_last_bar_time"] == (
        "2026-06-10T23:45:00Z")
    assert record["expected_total_attempts"] == 133
    assert record["expected_accepted_pre_anti_cluster"] == 73
    assert record["expected_accepted_post_anti_cluster"] == 51
    assert record["expected_rejected_by_scanner"] == 60
    assert record["expected_dropped_by_anti_cluster"] == 22
    for field, bad in (("expected_bars_scanned", 0),
                       ("expected_bars_scanned", 1000),
                       ("expected_total_attempts", 0),
                       ("expected_accepted_pre_anti_cluster", 0),
                       ("expected_accepted_post_anti_cluster", 0),
                       ("expected_rejected_by_scanner", 0),
                       ("expected_dropped_by_anti_cluster", 0)):
        tampered = _record()
        tampered[field] = bad
        assert c8l.validate_c8_labels_review(
            tampered)["valid"] is False, (field, bad)


def test_identity_checks_consistent():
    record = _record()
    identity = record["expected_identity_checks"]
    assert identity[
        "accepted_pre_plus_rejected_equals_attempts"] is True
    assert identity[
        "accepted_post_plus_dropped_equals_accepted_pre"] is True
    # Arithmetic verification
    assert (record["expected_accepted_pre_anti_cluster"]
            + record["expected_rejected_by_scanner"]
            == record["expected_total_attempts"])
    assert (record["expected_accepted_post_anti_cluster"]
            + record["expected_dropped_by_anti_cluster"]
            == record["expected_accepted_pre_anti_cluster"])


def test_status_breakdown_frozen():
    record = _record()
    breakdown = record["expected_status_breakdown"]
    assert breakdown["accepted_for_replay_review"] == 73
    assert breakdown[
        "rejected_no_qualifying_reclaim_within_4_bars"] == 57
    assert breakdown["rejected_geometry_floor"] == 3
    assert breakdown[
        "rejected_clustered_within_8_bars_of_prior_accepted"] == 22
    assert sum(breakdown.values()) == 133 + 22  # 133 attempts + 22 dropped recounted
    tampered = _record()
    tampered["expected_status_breakdown"] = {}
    assert c8l.validate_c8_labels_review(
        tampered)["valid"] is False


# ---- sample-size adequacy + anti-cluster locks ----------------------------

def test_sample_size_adequacy_satisfied_and_proposal_locked():
    record = _record()
    sa = record["expected_sample_size_adequacy"]
    assert sa["accepted_count"] == 51
    assert sa["minimum_required_at_labels_review_gate"] == 20
    assert sa["below_minimum_at_dry_run"] is False
    assert sa["enforced_at_labels_review_gate_only"] is True
    assert sa["does_not_consume_edit_token"] is True
    assert record["expected_sample_size_satisfied"] is True
    assert 51 >= 20  # explicit arithmetic verification
    for bad in (False, None):
        tampered = _record()
        tampered["expected_sample_size_satisfied"] = bad
        assert c8l.validate_c8_labels_review(
            tampered)["valid"] is False, bad


def test_anti_cluster_proposal_locked_and_not_edit_token():
    record = _record()
    anti = record["expected_anti_cluster_facts"]
    assert anti["anti_cluster_min_bar_gap"] == 8
    assert anti["tie_breaker"] == (
        "keep_the_earlier_event_drop_the_later_one")
    assert anti["anti_cluster_does_not_consume_edit_token"] is True
    assert anti["accepted_before_anti_cluster"] == 73
    assert anti["accepted_after_anti_cluster"] == 51
    assert anti["dropped_by_anti_cluster"] == 22
    tampered = _record()
    tampered["expected_anti_cluster_facts"] = {}
    assert c8l.validate_c8_labels_review(
        tampered)["valid"] is False


def test_claim_locks_present_including_proposal_locks():
    record = _record()
    locks = record["claim_locks"]
    for required in (
            "no_profitability_claim", "no_paper_approval",
            "no_live_approval", "no_execution_approval",
            "no_winner_wording",
            "no_replay_authorized_by_this_gate",
            "no_relabel_authorized_by_this_gate",
            "no_edit_token_applied_by_this_gate",
            "no_rejection_decision_made_by_this_gate",
            "anti_cluster_gap_remains_proposal_level_locked",
            "sample_size_threshold_remains_proposal_level_locked"):
        assert required in locks, required
    tampered = _record()
    tampered["claim_locks"] = []
    assert c8l.validate_c8_labels_review(
        tampered)["valid"] is False


# ---- scope locks + summary self-claims ------------------------------------

def test_expected_scope_locks_all_true():
    locks = _record()["expected_scope_locks"]
    for key in ("no_replay", "no_relabel", "no_pnl", "no_fetch",
                "no_network", "no_api", "no_credentials",
                "no_broker", "no_exchange", "no_wallet",
                "no_scheduler", "no_paper_trading", "no_micro_live",
                "no_live_trading", "no_edit_token_consumed",
                "no_downstream_gates_unlocked"):
        assert locks[key] is True, key


def test_expected_summary_self_claims():
    record = _record()
    claims = record["expected_summary_self_claims"]
    assert claims["candidate_id"] == "LIQUIDITY_SWEEP_MEAN_REVERSION_V1"
    assert claims["candidate_family"] == "liquidity_sweep_mean_reversion"
    assert claims["symbol"] == "BTCUSD"
    assert claims["timeframe"] == "15m"
    assert claims["direction"] == "long_only"
    assert claims["attempts"] == 133
    assert claims["accepted_pre_anti_cluster"] == 73
    assert claims["accepted_post_anti_cluster"] == 51
    assert claims["rejected"] == 60
    assert claims["anti_cluster_drops"] == 22
    assert claims["bars_scanned"] == 3840
    assert claims["anti_cluster_does_not_consume_edit_token"] is True
    assert claims["source_unchanged_during_detection"] is True


# ---- frozen review findings -----------------------------------------------

def test_frozen_detection_facts_complete():
    findings = _record()["frozen_detection_facts"]
    joined = " || ".join(findings)
    assert "single-symbol btcusd 15m" in joined
    assert "3840 staged btcusd 15m bars" in joined
    assert "133 attempts" in joined
    assert "73 accepted before anti-cluster" in joined
    assert "51 accepted after anti-cluster" in joined
    assert "22 dropped by 8-bar anti-cluster" in joined
    assert "57 on no_qualifying_reclaim_within_4_bars" in joined
    assert "3 on geometry_floor" in joined
    assert "73 + 60 = 133" in joined
    assert "51 + 22 = 73" in joined
    assert "sample-size adequacy SATISFIED: 51 >= 20" in joined
    assert "anti-cluster gap remains proposal-level locked and does" \
        " NOT consume the single c8 edit token" in joined
    assert "sample-size adequacy threshold remains proposal-level " \
        "locked and does NOT consume the single c8 edit token" \
        in joined
    assert "no replay; no pnl; no relabel; no edit token applied" \
        in joined


# ---- labels-review-only safety / capability flags ------------------------

def test_labels_review_only_with_all_downstream_locked():
    record = _record()
    assert record["is_labels_review_only"] is True
    assert record["current_loop_stage"] == (
        "detector_and_label_review")
    assert record["human_review_required"] is True
    assert record["paper_trading_gate_locked"] is True
    assert record["micro_live_gate_locked"] is True
    assert record["live_gate_locked"] is True
    for key in ("edit_token_applied_by_this_gate",
                "rejection_decision_made_by_this_gate",
                "replay_authorized_by_this_gate",
                "relabel_authorized_by_this_gate"):
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
        assert c8l.validate_c8_labels_review(
            tampered)["valid"] is False, key


def test_label_next_required_action_and_label_text():
    record = _record()
    assert record["next_required_action"] == (
        "HUMAN_APPROVED_CANDIDATE_8_REPLAY")
    # The next-action token is allowed to contain REPLAY (this is
    # the explicit named next gate), but no execution / trading
    # tokens should appear.
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH",
                   "EXECUTE", "EXECUTION", "BACKTEST", "BASELINE",
                   "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in c8l.NEXT_REQUIRED_ACTION.upper(), banned
    assert c8l.get_candidate_8_labels_review_label() == c8l.C8L_LABEL
    assert c8l.C8L_MODE == "RESEARCH_ONLY"
    for phrase in ("READ-ONLY", "RESEARCH ONLY", "NOT A RESCUE",
                   "NOT A PROFITABILITY CLAIM",
                   "SAMPLE-SIZE ADEQUACY SATISFIED",
                   "51 ACCEPTED POST ANTI-CLUSTER"):
        assert phrase in c8l.C8L_LABEL, phrase
    for banned_phrase in ("WINNER", "PROFITABLE", "EDGE CONFIRMED",
                          "APPROVED FOR PAPER",
                          "APPROVED FOR LIVE"):
        assert banned_phrase not in c8l.C8L_LABEL.upper(), (
            banned_phrase)


def test_runner_and_artifacts_remain_untracked_in_git():
    """The runner, labels artifact, summary artifact, and the c8
    operational data directory must NEVER appear in `git ls-files`."""
    tracked = _tracked_paths()
    for path in (c8l.RUNNER_PATH, c8l.LABELS_PATH, c8l.SUMMARY_PATH):
        assert path not in tracked, path
    # Defense: the operational data prefix as a whole must stay
    # untracked (no other files committed under
    # data/liquidity_sweep_c8/).
    for tracked_path in tracked:
        assert not tracked_path.startswith(
            "data/liquidity_sweep_c8/"), tracked_path
    record = _record()
    assert record["failures"] == []


# ---- module purity --------------------------------------------------------

def test_module_purity_no_banned_imports_no_open_no_main():
    src = open(c8l.__file__, encoding="utf-8").read()
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
    # The contract observes via Path.read_bytes() / is_file(); it
    # must not call open() / exec() / eval() / compile() directly.
    for call in ast.walk(tree):
        if not isinstance(call, ast.Call):
            continue
        name = (call.func.attr if isinstance(call.func, ast.Attribute)
                else getattr(call.func, "id", ""))
        assert name not in ("open", "exec", "eval", "compile"), name
