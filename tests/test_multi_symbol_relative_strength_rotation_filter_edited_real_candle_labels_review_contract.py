"""Tests for the Candidate #6 edited real-candle labels review.

Covers all 20 commanded requirements: artifact sha freezes, total
counts, per-symbol reconciliation, 81 bps floor pass/fail, aggregation
counts, timestamp alignment, the 36 kept setup IDs, the exact pushed
24-bar clustering filter constants, replay/edit/profitability locks,
no trading-adjacent capability, AST/purity. Commander safety suite
runs alongside (12 tests)."""

from __future__ import annotations

import ast
import copy

import pytest

import sparta_commander.multi_symbol_relative_strength_rotation_filter_edited_real_candle_labels_review_contract as c6el
import sparta_commander.multi_symbol_relative_strength_rotation_filter_real_candle_labels_review_contract as c6l
import sparta_commander.multi_symbol_relative_strength_rotation_filter_single_edit_clustering_filter_contract as c6e

REPO_ROOT = "C:/SPARTA_BRAIN"


def _good_observation():
    return {
        "labels_exists": True, "summary_exists": True,
        "labels_sha256": c6el.EXPECTED_LABELS_SHA256,
        "summary_sha256": c6el.EXPECTED_SUMMARY_SHA256,
        "labels_line_count": c6el.EXPECTED_TOTAL_ATTEMPTS,
        "accepted_count_before_edit":
            c6el.EXPECTED_ACCEPTED_BEFORE_EDIT,
        "accepted_count_after_edit":
            c6el.EXPECTED_ACCEPTED_AFTER_EDIT,
        "removed_by_clustering_total":
            c6el.EXPECTED_REMOVED_BY_CLUSTERING_TOTAL,
        "scanner_rejected_total":
            c6el.EXPECTED_SCANNER_REJECTED_TOTAL,
        "per_symbol_counts": copy.deepcopy(
            {sym: dict(v) for sym, v
             in c6el.EXPECTED_PER_SYMBOL_EDITED.items()
             if sym != "total"}),
        "kept_accepted_setup_ids":
            c6el.EXPECTED_KEPT_ACCEPTED_SETUP_IDS,
        "floor_pass_after_edit": dict(
            c6el.EXPECTED_FLOOR_PASS_AFTER_EDIT),
        "floor_fail_after_edit": dict(
            c6el.EXPECTED_FLOOR_FAIL_AFTER_EDIT),
        "all_kept_pass_floor_at_all_variants": True,
        "edit_constants_in_summary": dict(
            c6el.EXPECTED_EDIT_CONSTANTS),
        "summary_aggregation_counts": dict(
            c6el.EXPECTED_AGGREGATION_COUNTS_FROZEN),
        "summary_alignment_status":
            c6el.EXPECTED_ALIGNMENT_STATUS_FROZEN,
        "summary_replay_executed_now": False,
        "summary_no_second_edit": True,
        "summary_no_detector_rewrite": True,
        "summary_no_parameter_changes": True,
        "summary_no_profitability_claim": True,
        "summary_no_paper_or_live_authorization": True,
        "candidate_id_in_summary":
            "MULTI_SYMBOL_RELATIVE_STRENGTH_ROTATION_FILTER_V1",
        "staged_shas_now": dict(
            c6el.EXPECTED_STAGED_SHAS_FROZEN),
        "staged_shas_match": True,
        "artifacts_tracked_in_git": [],
    }


# (1) Validate edited artifact shas exactly -----------------------------------

def test_1_edited_artifact_shas_exact():
    assert c6el.EXPECTED_LABELS_SHA256 == (
        "a2c720be296914edc863835c02b71949cbf727ae67b0853018983f4a8ae9"
        "d987")
    assert c6el.EXPECTED_SUMMARY_SHA256 == (
        "92bdf76ec9474292a92ce687a5d830b5f1d66ad65cc4f49c86489219d044"
        "6f7a")
    bad = _good_observation()
    bad["labels_sha256"] = "00" * 32
    assert "edited_labels_sha_mismatch" in (
        c6el.certify_c6_edited_labels_review(bad)["failures"])
    bad2 = _good_observation()
    bad2["summary_sha256"] = "00" * 32
    assert "edited_summary_sha_mismatch" in (
        c6el.certify_c6_edited_labels_review(bad2)["failures"])


# (2) Validate original accepted = 135 ---------------------------------------

def test_2_original_accepted_equals_135():
    assert c6el.EXPECTED_ACCEPTED_BEFORE_EDIT == 135
    bad = _good_observation()
    bad["accepted_count_before_edit"] = 100
    assert "accepted_before_edit_must_equal_135" in (
        c6el.certify_c6_edited_labels_review(bad)["failures"])


# (3) Validate edited accepted = 36 ------------------------------------------

def test_3_edited_accepted_equals_36():
    assert c6el.EXPECTED_ACCEPTED_AFTER_EDIT == 36
    bad = _good_observation()
    bad["accepted_count_after_edit"] = 35
    assert "accepted_after_edit_must_equal_36" in (
        c6el.certify_c6_edited_labels_review(bad)["failures"])


# (4) Validate removed by clustering = 99 ------------------------------------

def test_4_removed_by_clustering_equals_99():
    assert c6el.EXPECTED_REMOVED_BY_CLUSTERING_TOTAL == 99
    bad = _good_observation()
    bad["removed_by_clustering_total"] = 100
    assert "removed_by_clustering_total_must_equal_99" in (
        c6el.certify_c6_edited_labels_review(bad)["failures"])
    # accepted_before - accepted_after must equal removed_by_clustering
    assert (c6el.EXPECTED_ACCEPTED_BEFORE_EDIT
            - c6el.EXPECTED_ACCEPTED_AFTER_EDIT
            == c6el.EXPECTED_REMOVED_BY_CLUSTERING_TOTAL)


# (5) Validate total attempts = 389 ------------------------------------------

def test_5_total_attempts_equals_389():
    assert c6el.EXPECTED_TOTAL_ATTEMPTS == 389
    bad = _good_observation()
    bad["labels_line_count"] = 388
    assert "label_count_must_equal_389" in (
        c6el.certify_c6_edited_labels_review(bad)["failures"])


# (6) Validate original scanner rejected = 254 -------------------------------

def test_6_scanner_rejected_total_equals_254():
    assert c6el.EXPECTED_SCANNER_REJECTED_TOTAL == 254
    bad = _good_observation()
    bad["scanner_rejected_total"] = 200
    assert "scanner_rejected_total_must_equal_254" in (
        c6el.certify_c6_edited_labels_review(bad)["failures"])
    # 254 = 389 - 135 (the edit cannot promote rejected setups)
    assert (c6el.EXPECTED_TOTAL_ATTEMPTS
            - c6el.EXPECTED_ACCEPTED_BEFORE_EDIT
            == c6el.EXPECTED_SCANNER_REJECTED_TOTAL)


# (7) Validate per-symbol edited counts exactly ------------------------------

def test_7_per_symbol_edited_counts_exact():
    split = c6el.EXPECTED_PER_SYMBOL_EDITED
    assert split["BTCUSD"] == {
        "attempts": 127, "accepted_before_edit": 32,
        "accepted_after_edit": 9, "scanner_rejected": 95,
        "removed_by_clustering": 23,
        "floor_pass_2r": 9, "floor_pass_3r": 9,
        "floor_pass_4r": 9, "floor_fail": 0}
    assert split["ETHUSD"] == {
        "attempts": 130, "accepted_before_edit": 32,
        "accepted_after_edit": 11, "scanner_rejected": 98,
        "removed_by_clustering": 21,
        "floor_pass_2r": 11, "floor_pass_3r": 11,
        "floor_pass_4r": 11, "floor_fail": 0}
    assert split["SOLUSD"] == {
        "attempts": 132, "accepted_before_edit": 71,
        "accepted_after_edit": 16, "scanner_rejected": 61,
        "removed_by_clustering": 55,
        "floor_pass_2r": 16, "floor_pass_3r": 16,
        "floor_pass_4r": 16, "floor_fail": 0}
    bad = _good_observation()
    bad["per_symbol_counts"]["SOLUSD"]["accepted_after_edit"] = 10
    assert "per_symbol_counts_mismatch:SOLUSD" in (
        c6el.certify_c6_edited_labels_review(bad)["failures"])


# (8) Validate BTC/ETH/SOL totals reconcile to global totals ------------------

def test_8_per_symbol_totals_reconcile_to_global():
    split = c6el.EXPECTED_PER_SYMBOL_EDITED
    total = split["total"]
    for key in ("attempts", "accepted_before_edit",
                "accepted_after_edit", "scanner_rejected",
                "removed_by_clustering",
                "floor_pass_2r", "floor_pass_3r", "floor_pass_4r",
                "floor_fail"):
        assert (split["BTCUSD"][key]
                + split["ETHUSD"][key]
                + split["SOLUSD"][key]) == total[key], key
    # total.accepted_after_edit + total.removed_by_clustering
    # = total.accepted_before_edit
    assert (total["accepted_after_edit"]
            + total["removed_by_clustering"]
            == total["accepted_before_edit"])
    # attempts == accepted_before_edit + scanner_rejected
    assert (total["accepted_before_edit"] + total["scanner_rejected"]
            == total["attempts"])


# (9) Validate all 36 kept labels pass the 81 bps floor at 2R/3R/4R ----------

def test_9_floor_pass_after_edit_all_variants():
    assert c6el.EXPECTED_FLOOR_PASS_AFTER_EDIT == {
        "2r": 36, "3r": 36, "4r": 36}
    bad = _good_observation()
    bad["all_kept_pass_floor_at_all_variants"] = False
    assert "kept_set_must_pass_all_variant_floors" in (
        c6el.certify_c6_edited_labels_review(bad)["failures"])
    bad2 = _good_observation()
    bad2["floor_pass_after_edit"] = {"2r": 35, "3r": 35, "4r": 35}
    assert "floor_pass_after_edit_mismatch" in (
        c6el.certify_c6_edited_labels_review(bad2)["failures"])


# (10) Validate floor fail count = 0 ------------------------------------------

def test_10_floor_fail_count_zero_everywhere():
    assert c6el.EXPECTED_FLOOR_FAIL_AFTER_EDIT == {
        "2r": 0, "3r": 0, "4r": 0}
    for name in ("2r", "3r", "4r"):
        assert c6el.EXPECTED_PER_SYMBOL_EDITED["BTCUSD"][
            "floor_pass_" + name] + c6el.EXPECTED_PER_SYMBOL_EDITED[
            "ETHUSD"]["floor_pass_" + name] + (
            c6el.EXPECTED_PER_SYMBOL_EDITED["SOLUSD"][
                "floor_pass_" + name]) == 36, name
    bad = _good_observation()
    bad["floor_fail_after_edit"] = {"2r": 1, "3r": 0, "4r": 0}
    assert "floor_fail_after_edit_must_be_zero_everywhere" in (
        c6el.certify_c6_edited_labels_review(bad)["failures"])


# (11) Validate aggregation counts 3840 → 960 per symbol --------------------

def test_11_aggregation_counts_3840_to_960_per_symbol():
    counts = c6el.EXPECTED_AGGREGATION_COUNTS_FROZEN
    for sym in ("BTCUSD", "ETHUSD", "SOLUSD"):
        assert counts[sym] == {"bars_15m": 3840, "bars_1h": 960}, sym
    bad = _good_observation()
    bad["summary_aggregation_counts"] = {
        "BTCUSD": {"bars_15m": 3840, "bars_1h": 960},
        "ETHUSD": {"bars_15m": 3840, "bars_1h": 960},
        "SOLUSD": {"bars_15m": 3840, "bars_1h": 100}}
    assert "aggregation_counts_in_summary_mismatch" in (
        c6el.certify_c6_edited_labels_review(bad)["failures"])


# (12) Validate timestamp alignment fact exactly ----------------------------

def test_12_timestamp_alignment_exact():
    assert c6el.EXPECTED_ALIGNMENT_STATUS_FROZEN == (
        "aligned_across_btcusd_ethusd_solusd")
    bad = _good_observation()
    bad["summary_alignment_status"] = "alignment_unknown"
    assert "alignment_status_in_summary_mismatch" in (
        c6el.certify_c6_edited_labels_review(bad)["failures"])


# (13) Validate the 36 edited accepted setup IDs are frozen + deterministic --

def test_13_kept_accepted_setup_ids_frozen():
    kept = c6el.EXPECTED_KEPT_ACCEPTED_SETUP_IDS
    assert len(kept) == 36
    assert len(set(kept)) == 36  # unique
    # sorted lexically (ascending), deterministic
    assert tuple(sorted(kept)) == kept
    # subset of the pushed-original 135 accepted set
    assert set(kept).issubset(set(c6l.EXPECTED_ACCEPTED_SETUP_IDS))
    # per-symbol counts derived from IDs match the per-symbol table
    by_sym = {sym: sum(1 for sid in kept if sid.startswith(sym))
              for sym in ("BTCUSD", "ETHUSD", "SOLUSD")}
    assert by_sym == {"BTCUSD": 9, "ETHUSD": 11, "SOLUSD": 16}
    bad = _good_observation()
    bad["kept_accepted_setup_ids"] = kept[:35]
    assert "kept_accepted_setup_ids_mismatch" in (
        c6el.certify_c6_edited_labels_review(bad)["failures"])


# (14) Validate the edit rule is exactly the pushed 24-bar clustering filter -

def test_14_edit_rule_matches_pushed_single_edit_contract():
    # the expected edit constants in this contract MUST equal the pushed
    # single-edit contract's frozen rule
    assert c6el.EXPECTED_EDIT_CONSTANTS == {
        "min_bars_between_same_symbol_accepted_events_1h": 24,
        "tie_breaker": "keep_the_earlier_event_drop_the_later_one",
        "scope": "per_symbol",
        "applies_at": "label_emission_time_before_replay"}
    # equality with the pushed single-edit contract source-of-truth
    assert c6el.EXPECTED_EDIT_CONSTANTS[
        "min_bars_between_same_symbol_accepted_events_1h"] == (
        c6e.MIN_BARS_BETWEEN_SAME_SYMBOL_ACCEPTED_EVENTS_1H)
    assert c6el.EXPECTED_EDIT_CONSTANTS["tie_breaker"] == (
        c6e.EDIT_RULE["tie_breaker"])
    assert c6el.EXPECTED_EDIT_CONSTANTS["scope"] == (
        c6e.EDIT_RULE["scope"])
    assert c6el.EXPECTED_EDIT_CONSTANTS["applies_at"] == (
        c6e.EDIT_RULE["applies_at"])
    # mutating the summary's reported edit constants rejects
    for mutation in (
            {"min_bars_between_same_symbol_accepted_events_1h": 12},
            {"min_bars_between_same_symbol_accepted_events_1h": 48},
            {"tie_breaker": "keep_the_later_event_drop_earlier"},
            {"scope": "global"},
            {"applies_at": "replay_time"}):
        bad = _good_observation()
        bad["edit_constants_in_summary"] = dict(
            bad["edit_constants_in_summary"], **mutation)
        assert "edit_constants_in_summary_mismatch" in (
            c6el.certify_c6_edited_labels_review(bad)["failures"]), \
            mutation


# (15) Review fails if any artifact sha/count/per-symbol count/floor/
#      alignment/edit-rule fact changes ----------------------------------------

def test_15_review_fails_on_any_frozen_record_change():
    record = c6el.build_c6_edited_labels_review(
        REPO_ROOT, tracked_paths=[])
    for field, value in (
            ("expected_labels_sha256", "00" * 32),
            ("expected_summary_sha256", "00" * 32),
            ("expected_total_attempts", 0),
            ("expected_accepted_before_edit", 100),
            ("expected_accepted_after_edit", 35),
            ("expected_removed_by_clustering_total", 100),
            ("expected_scanner_rejected_total", 0),
            ("expected_per_symbol_edited", {}),
            ("expected_floor_pass_after_edit", {}),
            ("expected_floor_fail_after_edit", {"2r": 1}),
            ("expected_aggregation_counts", {}),
            ("expected_alignment_status", "unaligned"),
            ("expected_kept_accepted_setup_ids", []),
            ("expected_edit_constants",
             {"min_bars_between_same_symbol_accepted_events_1h": 12}),
            ("expected_staged_shas", {}),
            ("frozen_review_facts", []),
            ("claim_locks", []),
            ("head_at_edited_relabel", "00" * 20),
            ("verdict", "CANDIDATE_6_APPROVED_FOR_TRADING")):
        tampered = c6el.build_c6_edited_labels_review(
            REPO_ROOT, tracked_paths=[])
        tampered[field] = value
        assert c6el.validate_c6_edited_labels_review(
            tampered)["valid"] is False, field


# (16) Replay remains locked --------------------------------------------------

def test_16_replay_remains_locked():
    record = c6el.build_c6_edited_labels_review(
        REPO_ROOT, tracked_paths=[])
    assert record["replay_authorized_by_this_gate"] is False
    assert record["runs_replay_now"] is False
    assert record["labels_now"] is False
    assert "no_replay_authorized_by_this_gate" in record["claim_locks"]
    # a summary that claims replay was run rejects
    bad = _good_observation()
    bad["summary_replay_executed_now"] = True
    assert "summary_must_record_no_replay_executed" in (
        c6el.certify_c6_edited_labels_review(bad)["failures"])
    # flipping replay_authorized_by_this_gate to True rejects record
    tampered = c6el.build_c6_edited_labels_review(
        REPO_ROOT, tracked_paths=[])
    tampered["replay_authorized_by_this_gate"] = True
    assert c6el.validate_c6_edited_labels_review(
        tampered)["valid"] is False


# (17) Second edit remains impossible ----------------------------------------

def test_17_second_edit_remains_impossible():
    record = c6el.build_c6_edited_labels_review(
        REPO_ROOT, tracked_paths=[])
    assert record["second_edit_possible"] is False
    assert record["edit_authorized_by_this_gate"] is False
    assert "no_second_edit_possible" in record["claim_locks"]
    assert "edit_token_already_spent_no_refund" in record["claim_locks"]
    # a summary that claims a second edit happened rejects
    bad = _good_observation()
    bad["summary_no_second_edit"] = False
    assert "summary_must_record_no_second_edit" in (
        c6el.certify_c6_edited_labels_review(bad)["failures"])
    # flipping second_edit_possible / edit_authorized_by_this_gate to
    # True rejects record
    for flag in ("second_edit_possible", "edit_authorized_by_this_gate"):
        tampered = c6el.build_c6_edited_labels_review(
            REPO_ROOT, tracked_paths=[])
        tampered[flag] = True
        assert c6el.validate_c6_edited_labels_review(
            tampered)["valid"] is False, flag


# (18) No profitability/paper/live/winner wording introduced -----------------

def test_18_no_profitability_paper_live_winner_wording():
    record = c6el.build_c6_edited_labels_review(
        REPO_ROOT, tracked_paths=[])
    locks = record["claim_locks"]
    for lock in ("no_profitability_claim", "no_paper_approval",
                 "no_live_approval", "no_execution_approval",
                 "no_winner_wording"):
        assert lock in locks, lock
    # the label must include the read-only / not-a-profitability-claim
    # framing and must not include any banned wording
    label = c6el.C6EL_LABEL
    assert "READ-ONLY" in label
    assert "NOT A PROFITABILITY CLAIM" in label
    for banned_phrase in ("WINNER", "PROFITABLE", "EDGE CONFIRMED",
                          "APPROVED FOR PAPER", "APPROVED FOR LIVE"):
        assert banned_phrase not in label.upper(), banned_phrase
    # mutating the summary or record to add a profitability claim
    # rejects
    bad = _good_observation()
    bad["summary_no_profitability_claim"] = False
    assert "summary_must_record_no_profitability_claim" in (
        c6el.certify_c6_edited_labels_review(bad)["failures"])
    bad2 = _good_observation()
    bad2["summary_no_paper_or_live_authorization"] = False
    assert "summary_must_record_no_paper_or_live" in (
        c6el.certify_c6_edited_labels_review(bad2)["failures"])


# (19) No trading-adjacent capability ----------------------------------------

def test_19_no_trading_adjacent_capability():
    record = c6el.build_c6_edited_labels_review(
        REPO_ROOT, tracked_paths=[])
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


# (20) AST/purity ------------------------------------------------------------

def test_20_ast_purity_and_no_writers_or_runners():
    assert c6el.get_c6_edited_labels_review_label() == c6el.C6EL_LABEL
    assert c6el.C6EL_MODE == "RESEARCH_ONLY"
    assert c6el.VERDICT_C6EL_FROZEN == (
        "CANDIDATE_6_EDITED_REAL_CANDLE_LABELS_FROZEN_READY_FOR_HUMAN_"
        "REVIEW")
    assert c6el.NEXT_REQUIRED_ACTION == (
        "HUMAN_DECISION_C6_AUTHORIZE_EDITED_REPLAY_OR_CLOSE_FAMILY")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in c6el.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(c6el.__file__, encoding="utf-8").read()
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


# Real-artifact end-to-end live certification ---------------------------------

def test_real_edited_artifacts_certify_when_present():
    import pathlib
    if not (pathlib.Path(REPO_ROOT) / c6el.LABELS_PATH).is_file():
        pytest.skip("candidate #6 edited labels not present")
    record = c6el.build_c6_edited_labels_review(
        REPO_ROOT, tracked_paths=[])
    assert record["verdict"] == c6el.VERDICT_C6EL_FROZEN
    assert record["failures"] == []
    assert c6el.validate_c6_edited_labels_review(
        record)["valid"] is True
    # determinism
    assert c6el.build_c6_edited_labels_review(
        REPO_ROOT, tracked_paths=[]) == record


def test_chain_gate_and_runner_untracked():
    bad = _good_observation()
    bad["artifacts_tracked_in_git"] = [c6el.RUNNER_PATH]
    assert "edited_runner_and_artifacts_must_stay_untracked" in (
        c6el.certify_c6_edited_labels_review(bad)["failures"])
    bad2 = _good_observation()
    bad2["staged_shas_match"] = False
    assert "staged_data_shas_changed_by_or_after_edit" in (
        c6el.certify_c6_edited_labels_review(bad2)["failures"])
