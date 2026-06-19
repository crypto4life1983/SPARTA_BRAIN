"""Tests for the C19 research-direction recommendation contract.

Verifies: research-only, recommendation-only, executes nothing; assigns / opens NO
C19 and creates no candidate; reviews the live lane (no active candidate, ledger 23,
C18 rejected); recommends exactly one preferred + two backup MARKET-NEUTRAL families,
none of which is one of the 23 rejected families, each with a distinctness rationale;
considers but does not reuse the H4 friend-style concept; declares the required data
(no new fetch, no new instrument class) and the full downstream gate chain; requires
the separate explicit human token to open C19; capability flags + scope locks;
validator anti-tamper; module purity."""
from __future__ import annotations

import ast

import sparta_commander.c19_research_direction_recommendation_v1_contract as c19
import sparta_commander.research_expansion_plan_v1_contract as rep


_R = c19.build_c19_research_direction_recommendation()


def test_recommendation_only_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_recommendation_only"] is True
    assert c19.validate_c19_research_direction_recommendation(_R)["valid"] is True


def test_does_not_assign_or_open_c19():
    assert _R["assigns_c19"] is False
    assert _R["c19_assigned"] is False
    assert _R["creates_candidate"] is False
    assert _R["candidate_id"] is None
    assert _R["is_active_candidate"] is False


def test_reviews_live_lane_state():
    # at recommendation time the lane had no active candidate; once C19 is opened
    # from this recommendation, the lane's active candidate is exactly C19 (the
    # preferred family) -- which is consistent, never a conflict.
    assert _R["lane_active_is_none_or_this_recommendation"] is True
    assert _R["lane_active_candidate"] in (None, "C19")
    assert _R["rejected_ledger_count"] == 23
    assert _R["uses_c1_to_c18_ledger"] is True
    assert _R["last_rejected_candidate"] == "C18"
    assert _R["c18_rejected_at_replay"] is True


def test_one_preferred_two_backups_all_market_neutral():
    dirs = _R["next_research_directions"]
    assert len(dirs) == 3
    preferred = [d for d in dirs if d["role"] == "preferred"]
    backups = [d for d in dirs if d["role"] == "backup"]
    assert len(preferred) == 1
    assert len(backups) == 2
    assert _R["preferred_direction_key"] == (
        "oos_validated_beta_neutral_cross_sectional_relative_value")
    assert _R["preferred_direction"]["rank"] == 1
    assert len(_R["backup_directions"]) == 2
    for d in dirs:
        assert d["market_neutral"] is True, d["key"]
        assert d["feasible_on_cached_data"] is True, d["key"]


def test_no_direction_is_a_rejected_family():
    rejected = set(rep.REJECTED_FAMILIES_C1_TO_C18)
    for d in _R["next_research_directions"]:
        assert d["key"] not in rejected, d["key"]
    assert _R["directions_are_distinct_from_rejected_ledger"] is True
    # tamper: a direction that IS a rejected family -> invalid
    bad_dirs = [{**_R["next_research_directions"][0],
                 "key": "h4_trend_following_market_structure"}] + \
        _R["next_research_directions"][1:]
    bad = {**_R, "next_research_directions": bad_dirs}
    assert c19.validate_c19_research_direction_recommendation(bad)["valid"] is False


def test_preferred_is_materially_different_and_explained():
    assert _R["why_preferred_is_materially_different"]
    p = _R["preferred_direction"]
    assert p["market_neutral"] is True
    assert "C16" in p["distinct_from_rejected"]
    assert "neutral" in p["mechanism"].lower()
    # the rationale ties to the C17/C18 risk-adjusted-vs-buy-and-hold rock
    assert "buy-and-hold" in _R["why_preferred_is_materially_different"].lower()


def test_h4_friend_concept_considered_not_reused():
    assert _R["h4_friend_concept_considered"] is True
    assert _R["h4_friend_concept_reused"] is False
    assert "C18" in _R["h4_friend_concept_note"]
    bad = {**_R, "h4_friend_concept_reused": True}
    assert c19.validate_c19_research_direction_recommendation(bad)["valid"] is False


def test_data_required_no_new_fetch_no_new_instrument():
    dr = _R["data_required"]
    assert dr["no_new_fetch_required"] is True
    assert dr["no_xauusd_or_new_instrument_class"] is True
    assert "cached" in dr["preferred"].lower()


def test_full_gate_chain_declared():
    gate_names = [g["gate"] for g in _R["gates_required"]]
    for required in ("human_open_c19", "family_proposal", "candidate_spec",
                     "detector_spec_dry_run", "real_candle_labels_review",
                     "fee_honest_replay_review", "rejection_or_promote_decision"):
        assert required in gate_names, required
    # the labels + replay gates carry the structural + market-neutral requirements
    g = {x["gate"]: x["what"] for x in _R["gates_required"]}
    assert ">=100" in g["real_candle_labels_review"]
    assert "37" in g["fee_honest_replay_review"]
    assert "forward-OOS" in g["fee_honest_replay_review"]


def test_human_token_to_open_c19_required_and_next_action_does_not_open():
    assert _R["requires_human_approval_before_c19"] is True
    assert _R["human_token_to_open_c19"] == (
        "HUMAN_APPROVED_C19_RESEARCH_DIRECTION__OPEN_CANDIDATE_FAMILY_PROPOSAL")
    nra = c19.get_c19_recommendation_next_action()
    assert nra == _R["next_required_action"]
    assert "NO_C19_ASSIGNED" in nra
    # the next action must NOT itself open C19
    assert "OPEN_CANDIDATE_FAMILY_PROPOSAL" not in nra


def test_downstream_locked_and_research_only():
    assert _R["real_data_qa_state"] == "BLOCKED"
    assert _R["replay_state"] == "BLOCKED"
    assert _R["paper_trading_state"] == "LOCKED"
    assert _R["live_trading_state"] == "LOCKED"
    assert _R["overnight_automation_research_only"] is True


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in c19._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert c19.validate_c19_research_direction_recommendation(
            bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_execute", "no_assign_c19", "no_open_candidate", "no_detector",
                 "no_labels", "no_replay", "no_optimization", "no_data_fetch",
                 "no_new_instrument_class", "no_xauusd", "no_reuse_rejected_family",
                 "no_reuse_h4_friend_concept", "no_commit", "no_push",
                 "no_paper_trading", "no_live_trading"):
        assert _R["scope_locks"][must] is True, must


def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(c19.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch(", "open(", "subprocess", "Popen"):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
              "subprocess", "websockets", "aiohttp", "schedule", "threading",
              "asyncio", "telegram", "csv", "hashlib", "os", "io", "shutil",
              "ssl", "ftplib", "pathlib", "datetime", "random", "numpy", "pandas"}
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
