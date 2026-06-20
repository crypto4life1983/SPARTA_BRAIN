"""Tests for the SPARTA Research Factory Automation V2 / Morning Decision Packet bundle.

Verifies the seven cohesive read-only capabilities and the dangerous-action locks:
next-safe-task selector, morning decision packet, gate recommendation engine (DATA_NOT_
READY -> dataset staging not labels; profitable-but-failed-benchmark -> REJECT, distinct
from a true pass), dirty-git/clutter blocker, blast-radius test selector (full-suite
honestly unavailable), approval-token generator, automation safety locks. Includes
integration tests against the live lane + C22 chain (DATA_NOT_READY, C1-C21 ledger = 26,
no active candidate on the lane), proof it recommends dataset staging for C22 and never
proceeds to labels, and proof every dangerous action stays locked."""
from __future__ import annotations

import ast

import sparta_commander.sparta_research_factory_automation_v2_contract as v2


_CLEAN_SYNCED = {
    "head": "33f44f2d4c42b645594cb71c7d8566cd31695554",
    "origin": "33f44f2d4c42b645594cb71c7d8566cd31695554",
    "ahead": 0, "behind": 0, "clean": True, "staged_count": 0,
    "untracked_clutter_present": True, "untracked_clutter_ignored_by_path": True,
}

_P = v2.build_morning_decision_packet(_CLEAN_SYNCED)


# ---- core: packet builds, read-only, validates -----------------------------

def test_packet_builds_and_validates():
    assert _P["mode"] == "RESEARCH_ONLY"
    assert _P["is_read_only_packet"] is True
    assert _P["recommends_only"] is True
    assert _P["executes_nothing"] is True
    assert v2.validate_morning_decision_packet(_P)["valid"] is True


# ---- (2) morning decision packet has every required section ----------------

def test_packet_sections_present():
    assert _P["section"] == "morning_decision_packet"
    assert "repo_sync" in _P and "git_safety" in _P
    assert "candidate_status" in _P and "last_verdict" in _P
    assert "blockers" in _P and "evidence" in _P
    assert "recommended_gate" in _P and "next_recommended_human_action" in _P
    assert "copy_paste_approval_tokens" in _P and "danger_locks" in _P
    rs = _P["repo_sync"]
    assert rs["in_sync"] is True and rs["ahead"] == 0 and rs["behind"] == 0
    assert rs["clean"] is True


# ---- (1)+(3) integration: C22 DATA_NOT_READY -> dataset staging, not labels -

def test_c22_data_not_ready_recommends_staging_not_labels():
    c22 = _P["candidate_status"]["c22"]
    assert c22["candidate_id"] == "C22"
    assert c22["last_verdict"] == "DATA_NOT_READY"
    assert c22["blocked_reason"] == "DATA_NOT_READY"
    assert c22["labels_produced"] is False
    # the recommendation routes to DATASET STAGING -- never labels
    g = _P["recommended_gate"]
    assert g["recommendation_kind"] == v2.REC_STAGE_DATA
    assert g["auto_executes"] is False
    nra = _P["next_recommended_human_action"]
    assert "STAGE_FROZEN_TREND_RADAR_GC_DETECTOR_DATASET" in nra
    assert "LABEL" not in g["recommendation_kind"]
    # the next-safe-task selector agrees
    task = _P["next_safe_task"]
    assert task["c22_blocked_data_not_ready"] is True
    assert "STAGE_TREND_RADAR_GC_DETECTOR_DATASET" in task["next_safe_task"]
    assert task["never_skips_human_gate"] is True


def test_integration_lane_and_ledger_state():
    cs = _P["candidate_status"]
    assert cs["rejected_ledger_count"] == 26
    assert cs["rejected_ledger_is_c1_to_c21"] is True
    assert cs["last_rejected_candidate"] == "C21"
    assert cs["lane_active_candidate"] is None    # lane has no active candidate
    # C22 chain artifacts are all valid (evidence)
    assert _P["evidence"]["c22_chain_artifacts_valid"] is True
    assert len(_P["evidence"]["c22_evidence_test_files"]) == 4


# ---- (3) gate engine: distinguishes true pass from profitable-but-failed ----

def test_classify_replay_outcome_distinguishes_pass_from_profitable_fail():
    # C21 shape: net-positive but loses to null + OOS fails -> NOT a pass
    assert v2.classify_replay_outcome(0.202, False, False, False, False) == (
        "PROFITABLE_BUT_FAILED_BENCHMARK")
    # net-positive but only fails OOS -> still not a pass
    assert v2.classify_replay_outcome(0.50, True, True, False, False) == (
        "PROFITABLE_BUT_FAILED_BENCHMARK")
    # true pass: beats null + buy-and-hold + holds OOS + all gates pass
    assert v2.classify_replay_outcome(0.30, True, True, True, True) == "TRUE_PASS"
    # negative -> fail
    assert v2.classify_replay_outcome(-0.10, False, False, False, False) == "FAIL"


def test_gate_engine_routes_true_pass_to_advance_and_profitfail_to_reject():
    # a true-pass replay -> ADVANCE (human); a profitable-but-failed -> REJECT
    g_pass = v2.recommend_gate({
        "git_safety": {"safe_to_automate": True, "ahead": 0, "blockers": []},
        "candidate": {"replay_outcome": "TRUE_PASS",
                      "next_required_action": "HUMAN_DECISION_ADVANCE"}})
    assert g_pass["recommendation_kind"] == v2.REC_ADVANCE
    g_fail = v2.recommend_gate({
        "git_safety": {"safe_to_automate": True, "ahead": 0, "blockers": []},
        "candidate": {"replay_outcome": "PROFITABLE_BUT_FAILED_BENCHMARK",
                      "next_required_action": "HUMAN_DECISION_REJECT_OR_PROMOTE"}})
    assert g_fail["recommendation_kind"] == v2.REC_REJECT
    assert g_pass["auto_executes"] is False and g_fail["auto_executes"] is False


# ---- (4) dirty-git / clutter blocker ---------------------------------------

def test_git_safety_blocks_dirty_and_staged_and_behind():
    dirty = v2.git_safety_gate({"clean": False, "staged_count": 0, "ahead": 0,
                                "behind": 0})
    assert dirty["safe_to_automate"] is False
    assert "tracked_tree_dirty" in dirty["blockers"]
    staged = v2.git_safety_gate({"clean": True, "staged_count": 3, "ahead": 0,
                                 "behind": 0})
    assert staged["safe_to_automate"] is False
    assert "staged_files_present" in staged["blockers"]
    behind = v2.git_safety_gate({"clean": True, "staged_count": 0, "ahead": 0,
                                 "behind": 2})
    assert behind["safe_to_automate"] is False
    assert "local_branch_behind_origin" in behind["blockers"]


def test_git_safety_allows_clean_with_clutter_and_flags_ahead():
    ok = v2.git_safety_gate({"clean": True, "staged_count": 0, "ahead": 0, "behind": 0,
                             "untracked_clutter_present": True,
                             "untracked_clutter_ignored_by_path": True})
    assert ok["safe_to_automate"] is True
    assert ok["clutter_blocks_automation"] is False
    assert any("untracked_clutter" in w for w in ok["warnings"])
    ahead = v2.git_safety_gate({"clean": True, "staged_count": 0, "ahead": 1,
                                "behind": 0})
    assert ahead["safe_to_automate"] is True   # ahead alone does not block
    assert any("ahead_needs_human_push_approval" in n for n in ahead["notes"])


def test_dirty_repo_packet_recommends_resolve_repo():
    dirty_packet = v2.build_morning_decision_packet(
        {"head": "x", "origin": "x", "clean": False, "staged_count": 2,
         "ahead": 0, "behind": 0})
    assert dirty_packet["recommended_gate"]["recommendation_kind"] == (
        v2.REC_RESOLVE_REPO)
    assert v2.validate_morning_decision_packet(dirty_packet)["valid"] is True


# ---- (5) blast-radius test selector + honest full-suite unavailability -----

def test_blast_radius_selector_and_full_suite_honesty():
    br = v2.blast_radius_tests([
        "sparta_commander/crypto_d1_candidate_research_lane_status_v1_contract.py",
        "tests/test_external_signum_trend_radar_gc_long_short_v1_data_readiness_contract.py"])
    assert ("tests/test_crypto_d1_candidate_research_lane_status_v1_contract.py"
            in br["targeted_tests"])
    # the readiness test passed in directly is included as-is
    assert ("tests/test_external_signum_trend_radar_gc_long_short_v1_data_readiness_contract.py"
            in br["targeted_tests"])
    # curated adjacency for the lane surface
    assert any("automation_readiness_bundle_integration" in a
               for a in br["adjacent_regression_tests"])
    # HONEST: full suite is not a usable gate here
    assert br["full_suite_runnable_as_gate"] is False
    assert "hang" in br["full_suite_unavailable_reason"].lower()


# ---- (6) approval-token generator ------------------------------------------

def test_approval_tokens_present_with_restrictions_and_git_state():
    t = v2.approval_tokens(unit_name="c22 next unit", files=["a.py", "b.py"],
                           commit_hash="deadbeef", candidate="C22",
                           stage="real_candle_labels")
    assert t["commit"]["token"] == "APPROVE_COMMIT_C22_NEXT_UNIT_ONLY"
    assert t["commit"]["approved_files"] == ["a.py", "b.py"]
    assert t["commit"]["expected_git_state_before"]["nothing_staged"] is True
    assert t["push"]["token"] == "APPROVE_PUSH_C22_NEXT_UNIT_ONLY"
    assert t["push"]["commit_to_push"] == "deadbeef"
    assert t["push"]["expected_git_state_before"]["ahead"] == 1
    assert "ADVANCE" in t["advance"]["token"]
    assert t["hold"]["token"].startswith("HOLD_C22_AT_")
    assert "REJECT_OR_PROMOTE" in t["reject"]["token"]
    assert "STAGE" in t["data_staging"]["token"]
    # every token carries hard restrictions and none contains a forbidden verb
    for kind in ("commit", "push", "advance", "reject", "data_staging"):
        assert t[kind]["hard_restrictions"]
    low = " ".join(t[k]["token"].lower() for k in t)
    for bad in ("live_trade", "place_order", "auto_push", "api_key", "git add ."):
        assert bad not in low


# ---- (7) automation safety locks -- dangerous actions pinned ---------------

def test_automation_safety_locks_all_dangerous_actions_locked():
    locks = v2.automation_safety_locks()
    for k in ("no_automatic_commit", "no_automatic_push", "no_automatic_data_fetch",
              "no_automatic_candidate_promotion", "no_broad_git_add",
              "never_skips_human_gates", "live_trading_locked", "paper_trading_locked",
              "broker_locked", "order_logic_locked", "api_keys_locked",
              "credentials_locked", "signum_locked", "hyperliquid_locked", "mcp_locked",
              "claude_routines_locked", "scheduler_locked", "bot_edits_locked",
              "trades_locked"):
        assert locks[k] is True, k
    assert locks["executes"] is False
    # the packet surfaces these and the validator enforces them
    for flag in v2._CAPABILITY_FLAGS_FALSE:
        assert _P[flag] is False, flag
        bad = {**_P, flag: True}
        assert v2.validate_morning_decision_packet(bad)["valid"] is False, flag


def test_packet_cannot_be_flipped_to_skip_gate_or_fake_labels():
    # tamper: claim C22 produced labels while DATA_NOT_READY -> invalid
    bad_c22 = {**_P["candidate_status"]["c22"], "labels_produced": True}
    bad_cs = {**_P["candidate_status"], "c22": bad_c22}
    bad = {**_P, "candidate_status": bad_cs}
    assert v2.validate_morning_decision_packet(bad)["valid"] is False
    # tamper: flip the recommendation away from staging while DATA_NOT_READY -> invalid
    bad_gate = {**_P["recommended_gate"], "recommendation_kind": v2.REC_ADVANCE}
    bad2 = {**_P, "recommended_gate": bad_gate}
    assert v2.validate_morning_decision_packet(bad2)["valid"] is False


# ---- scope locks + module purity -------------------------------------------

def test_scope_locks_all_true():
    for key, val in _P["scope_locks"].items():
        assert val is True, key


def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(v2.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch(", "open(", "subprocess", "Popen", "urlopen"):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
              "subprocess", "websockets", "aiohttp", "schedule", "threading",
              "asyncio", "telegram", "os", "io", "shutil", "ssl", "ftplib",
              "datetime", "random", "numpy", "pandas"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned), imported & banned
    for call in ast.walk(tree):
        if isinstance(call, ast.Call):
            name = (call.func.attr if isinstance(call.func, ast.Attribute)
                    else getattr(call.func, "id", ""))
            assert name not in ("open", "exec", "eval", "compile"), name
