"""Tests for the C22 CURRENT morning packet (authoritative next-action surface).

Proves the current packet supersedes the stale DATA_NOT_READY / dataset-staging view: C21
closed (ledger 26); C22 active HOLD_FOR_MORE_FROZEN_DATA_WINDOWS with replay locked and
progress 1/20 (baseline) or live-injected; the AUTHORITATIVE next action is the collect
token while < 20 and the SUGGESTED review token (never auto-run) at >= 20, NEVER the old
dataset-staging token; C23 is queued/on-deck (proposal frozen, not active); it is a status
surface (no C21/C22/C23 logic mutation, no labels/replay/fetch); and every capability flag
is False."""
from __future__ import annotations

import ast
from pathlib import Path

import sparta_commander.sparta_c22_current_morning_packet_contract as cur

_STAGING = "HUMAN_STAGE_FROZEN_TREND_RADAR_GC_DETECTOR_DATASET_THEN_REAUTHORISE_C22_LABELS"
_COLLECT = "HUMAN_STAGE_MORE_FROZEN_DAILY_TREND_RADAR_GC_WINDOWS_THEN_REREVIEW_C22_LABELS"
_REVIEW = "HUMAN_APPROVED_C22_SIGNUM_GC_FROZEN_DATA_WINDOW_REVIEW"
_C23_OPEN = "HUMAN_DECISION_OPEN_CANDIDATE_23_AFTER_C22_CONCLUDES_OR_HOLD"

_P = cur.build_c22_current_morning_packet()


# ---- builds + validates; C21 closed; C22 active HOLD; 1/20 -----------------

def test_builds_validates_c21_closed_c22_active_hold():
    assert _P["verdict"] == "C22_CURRENT_MORNING_PACKET_AUTHORITATIVE"
    assert cur.validate_c22_current_morning_packet(_P)["valid"] is True
    assert _P["c21_closed_rejected"] is True
    assert _P["rejected_ledger_count"] == 26
    assert _P["active_candidate"] == "C22"
    assert _P["c22_state"] == "HOLD_FOR_MORE_FROZEN_DATA_WINDOWS"
    assert _P["c22_replay_locked"] is True
    assert _P["collection_progress"] == "1/20"
    assert _P["collected_windows"] == 1 and _P["required_windows"] == 20
    assert _P["ready_for_review"] is False


# ---- authoritative = collect token (<20); supersedes staging ---------------

def test_authoritative_is_collect_token_supersedes_staging():
    assert _P["authoritative_next_action_source"] == "C22_CURRENT_COLLECTION"
    assert _P["authoritative_next_action"] == _COLLECT
    assert _P["authoritative_next_action"] != _STAGING
    assert _P["supersedes_automation_v2_data_not_ready_packet"] is True
    assert _P["does_not_present_dataset_staging_as_current_action"] is True
    assert _P["review_token_when_ready"] == _REVIEW
    assert _P["review_token_is_suggestion_only"] is True
    assert _P["auto_executes_review_token"] is False


# ---- C23 queued / on-deck only ---------------------------------------------

def test_c23_on_deck_not_active():
    assert _P["c23_on_deck"] is True
    assert _P["c23_is_active"] is False
    assert _P["c23_proposal_frozen"] is True
    assert _P["c23_open_gate"] == _C23_OPEN


# ---- ready branch: at >= 20 the authoritative is the SUGGESTED review token -

def test_ready_branch_suggests_review_token_only():
    r = cur.build_c22_current_morning_packet(collected_windows=20)
    assert r["ready_for_review"] is True
    assert r["collection_progress"] == "20/20"
    assert r["authoritative_next_action"] == _REVIEW
    assert r["auto_executes_review_token"] is False
    assert cur.validate_c22_current_morning_packet(r)["valid"] is True
    # live injection consistency at an intermediate count
    r5 = cur.build_c22_current_morning_packet(collected_windows=5)
    assert r5["collection_progress"] == "5/20" and r5["windows_remaining"] == 15
    assert r5["authoritative_next_action"] == _COLLECT


# ---- rendered sections surface the facts; never staging as authoritative ----

def test_render_markdown_html():
    md = cur.render_current_packet_markdown(_P)
    assert "HOLD_FOR_MORE_FROZEN_DATA_WINDOWS" in md
    assert "1/20" in md
    assert _COLLECT in md
    assert "queued / ON-DECK" in md
    assert _STAGING not in md
    html = cur.render_current_packet_html(_P)
    assert "HOLD_FOR_MORE_FROZEN_DATA_WINDOWS" in html
    assert "1/20" in html
    assert "<script" not in html.lower()


# ---- anti-tamper -----------------------------------------------------------

def test_tamper_rejected():
    # staging token as authoritative -> invalid
    bad = {**_P, "authoritative_next_action": _STAGING}
    assert cur.validate_c22_current_morning_packet(bad)["valid"] is False
    # C23 shown active -> invalid
    assert cur.validate_c22_current_morning_packet(
        {**_P, "c23_is_active": True})["valid"] is False
    # review token auto-execute -> invalid
    assert cur.validate_c22_current_morning_packet(
        {**_P, "auto_executes_review_token": True})["valid"] is False


# ---- capability flags + purity ---------------------------------------------

def test_capability_flags_and_purity():
    for flag in ("modifies_c22_pipeline", "modifies_c21_rejection_logic",
                 "modifies_c23_proposal", "opens_c23_as_active",
                 "auto_executes_review_token", "runs_labels", "runs_replay",
                 "fetches_data", "reopens_c21"):
        assert _P[flag] is False, flag
    for flag in cur._CAPABILITY_FLAGS_FALSE:
        assert _P[flag] is False, flag
        assert cur.validate_c22_current_morning_packet({**_P, flag: True})["valid"] is False
    for key, val in _P["scope_locks"].items():
        assert val is True, key
    src = Path(cur.__file__).read_text(encoding="utf-8")
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "open(",
                 "subprocess", "Popen", "urlopen", "json.load", "read_text", "glob("):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned = {"urllib", "requests", "socket", "http", "ccxt", "subprocess",
              "os", "io", "shutil", "json", "hashlib", "pathlib", "numpy", "pandas"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned), imported & banned
