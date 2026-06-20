"""Tests for the realigned (V2) crypto-D1 candidate research lane-status surface.

Proves the additive realigned surface accurately shows: C21 closed/rejected (ledger 26,
rejection logic unchanged); C22 the active collection lane at HOLD_FOR_MORE_FROZEN_DATA_
WINDOWS, replay locked, progress 1/20 from the committed tracker logic; C23 queued/on-deck
with its proposal frozen, NOT active, opening only via
HUMAN_DECISION_OPEN_CANDIDATE_23_AFTER_C22_CONCLUDES_OR_HOLD. Also proves it is a status
surface only (no labels/replay/fetch/pipeline mutation), that v1 is left FROZEN, and --
critically -- that the pushed v1 lane status + C22 proposal + C23 proposal contracts still
validate unchanged (the additive realignment broke no frozen chain)."""
from __future__ import annotations

import ast
from pathlib import Path

import sparta_commander.crypto_d1_candidate_research_lane_status_v2_realigned_contract as ls2
import sparta_commander.crypto_d1_candidate_research_lane_status_v1_contract as ls1
import sparta_commander.external_signum_trend_radar_gc_long_short_v1_proposal_contract as c22p
import sparta_commander.crypto_cross_sectional_low_volatility_anomaly_beta_neutral_v1_proposal_contract as c23p

_R = ls2.build_realigned_lane_status()


# ---- builds + validates ----------------------------------------------------

def test_realigned_builds_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_realigned_current_lane_status"] is True
    assert _R["verdict"] == "CRYPTO_D1_LANE_STATUS_REALIGNED_C22_ACTIVE_C23_ON_DECK"
    assert ls2.validate_realigned_lane_status(_R)["valid"] is True


# ---- C21 closed/rejected, ledger 26, logic unchanged -----------------------

def test_c21_closed_rejected_ledger_26():
    assert _R["last_rejected_candidate"] == "C21"
    assert _R["c21_closed_rejected"] is True
    assert _R["rejected_ledger_count"] == 26
    assert _R["c21_rejection_verdict"] == "C21_REJECTED_AT_FEE_HONEST_REPLAY"
    assert _R["c21_rejection_logic_unchanged"] is True


# ---- C22 active collection lane, HOLD, replay locked, 1/20 ------------------

def test_c22_active_hold_replay_locked_progress():
    assert _R["active_candidate"] == "C22"
    assert _R["c22_is_active"] is True
    assert _R["c22_state"] == "HOLD_FOR_MORE_FROZEN_DATA_WINDOWS"
    assert _R["c22_replay_locked"] is True
    ad = _R["active_candidate_detail"]
    assert ad["family"] == "external_signum_trend_radar_gc_long_short"
    assert ad["is_active_collection_lane"] is True
    assert ad["required_windows"] == 20
    assert ad["collected_windows"] == 1            # committed tracker bootstrap baseline
    assert ad["collection_progress"] == "1/20"
    assert ad["windows_remaining"] == 19
    assert ad["collection_pipeline_untouched"] is True


def test_live_collected_count_override_is_consistent():
    r = ls2.build_realigned_lane_status(collected_windows=5)
    ad = r["active_candidate_detail"]
    assert ad["collected_windows"] == 5
    assert ad["collection_progress"] == "5/20"
    assert ad["windows_remaining"] == 15
    assert ls2.validate_realigned_lane_status(r)["valid"] is True


# ---- C23 queued/on-deck, proposal frozen, not active -----------------------

def test_c23_on_deck_not_active():
    assert _R["on_deck_candidate"] == "C23"
    assert _R["c23_is_active"] is False
    assert _R["c23_is_queued_on_deck"] is True
    assert _R["c23_open_gate_after_c22_concludes"] == (
        "HUMAN_DECISION_OPEN_CANDIDATE_23_AFTER_C22_CONCLUDES_OR_HOLD")
    od = _R["on_deck_candidate_detail"]
    assert od["family"] == "crypto_cross_sectional_low_volatility_anomaly_beta_neutral"
    assert od["proposal_verdict"] == "C23_PROPOSAL_FROZEN_FOR_HUMAN_REVIEW"
    assert od["proposal_frozen_for_human_review"] is True
    assert od["is_active"] is False
    assert od["must_not_become_active_until_c22_concludes"] is True


# ---- status surface only; advances nothing; capability flags ---------------

def test_status_surface_only_capabilities():
    assert _R["is_status_surface_only"] is True
    assert _R["advances_nothing"] is True
    assert _R["next_required_action"] == (
        "HUMAN_STAGE_MORE_FROZEN_DAILY_TREND_RADAR_GC_WINDOWS_THEN_REREVIEW_C22_LABELS")
    for flag in ("opens_c23_as_active", "modifies_c21_rejection_logic",
                 "modifies_c22_pipeline", "modifies_c23_proposal", "mutates_lane_status_v1",
                 "runs_labels", "runs_replay", "fetches_data", "reopens_c21"):
        assert _R[flag] is False, flag
    for flag in ls2._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        assert ls2.validate_realigned_lane_status({**_R, flag: True})["valid"] is False
    for key, val in _R["scope_locks"].items():
        assert val is True, key


# ---- anti-tamper: cannot show C23 active / C22 not-hold --------------------

def test_tamper_rejected():
    assert ls2.validate_realigned_lane_status({**_R, "c23_is_active": True})["valid"] is False
    assert ls2.validate_realigned_lane_status(
        {**_R, "active_candidate": "C23"})["valid"] is False
    bad_detail = {**_R["active_candidate_detail"], "replay_locked": False}
    assert ls2.validate_realigned_lane_status(
        {**_R, "active_candidate_detail": bad_detail})["valid"] is False


# ---- CRITICAL: the frozen v1 chain still validates unchanged ----------------

def test_frozen_v1_chain_unbroken():
    # v1 lane status still validates as the frozen readiness snapshot (active==None)
    v1 = ls1.get_lane_status()
    assert ls1.validate_lane_status(v1)["valid"] is True
    assert v1["active_candidate"] is None      # v1 left frozen, NOT mutated
    # the pushed C22 proposal still chain-validates as FROZEN (depends on v1 active==None)
    c22 = c22p.build_c22_proposal()
    assert c22["verdict"] == "C22_PROPOSAL_FROZEN_FOR_HUMAN_REVIEW"
    assert c22p.validate_c22_proposal(c22)["valid"] is True
    # the pushed C23 proposal still validates frozen
    c23 = c23p.build_c23_proposal()
    assert c23["verdict"] == "C23_PROPOSAL_FROZEN_FOR_HUMAN_REVIEW"
    assert c23p.validate_c23_proposal(c23)["valid"] is True


# ---- module purity ---------------------------------------------------------

def test_module_purity():
    src = Path(ls2.__file__).read_text(encoding="utf-8")
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "open(",
                 "subprocess", "Popen", "urlopen", "requests.", "socket.connect",
                 "json.load", "read_text", "glob("):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
              "subprocess", "websockets", "aiohttp", "schedule", "threading",
              "asyncio", "telegram", "os", "io", "shutil", "ssl", "ftplib",
              "json", "hashlib", "pathlib", "numpy", "pandas"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned), imported & banned
