"""Tests for the SPARTA Safe Research Autopilot v1 PURE PLANNER.

Proves: it auto-advances ONLY the 3 low-risk research build gates (proposal ->
spec -> detector dry-run); it HARD STOPS before real-candle labels; it recommends
a rejection closeout (never edit/advance) for a structurally-rejected candidate
(labels or replay); it refuses a dirty repo / uncommitted artifacts; it refuses a
proposed family that is in the C1-C13 rejected ledger; across EVERY input it
never emits a forbidden-gate executor action and never sets
crossed_into_forbidden_gate; every capability flag is False; the morning-report
summary is render-ready; AST/purity green (no build/write/execute/IO)."""
from __future__ import annotations

import ast
import copy

import sparta_commander.safe_research_autopilot_v1_contract as sara

_CLEAN = {"clean": True, "uncommitted_candidate_artifacts": False}


def _decide(stage, repo=None, proposed_family=None, rejected=None):
    return sara.decide_next_safe_action(
        {"active_candidate": None if stage == sara.STAGE_NONE else "CXX",
         "stage": stage, "proposed_family": proposed_family},
        repo or _CLEAN, rejected)


# ---- the 3 low-risk auto-advance gates -------------------------------------

def test_none_recommends_open_proposal():
    d = _decide(sara.STAGE_NONE, proposed_family="some_new_family")
    assert d["next_safe_action"] == sara.ACTION_BUILD_PROPOSAL
    assert d["auto_advanceable"] is True
    assert d["requires_human_approval"] is False
    assert d["is_hard_stop"] is False
    assert sara.validate_safe_autopilot_decision(d)["valid"] is True


def test_proposal_ready_recommends_spec():
    d = _decide(sara.STAGE_PROPOSAL_READY)
    assert d["next_safe_action"] == sara.ACTION_BUILD_SPEC
    assert d["auto_advanceable"] is True
    assert sara.validate_safe_autopilot_decision(d)["valid"] is True


def test_spec_ready_recommends_detector():
    d = _decide(sara.STAGE_SPEC_READY)
    assert d["next_safe_action"] == sara.ACTION_BUILD_DETECTOR
    assert d["auto_advanceable"] is True
    assert sara.validate_safe_autopilot_decision(d)["valid"] is True


# ---- the hard stop before real-candle labels -------------------------------

def test_detector_dry_run_ready_hard_stops_before_labels():
    d = _decide(sara.STAGE_DETECTOR_DRY_RUN_READY)
    assert d["next_safe_action"] == sara.ACTION_STOP_BEFORE_LABELS
    assert d["auto_advanceable"] is False
    assert d["requires_human_approval"] is True
    assert d["is_hard_stop"] is True
    assert d["stops_before"] == "real_candle_labels"
    assert sara.validate_safe_autopilot_decision(d)["valid"] is True
    # cannot be tampered to auto-advance
    bad = copy.deepcopy(d)
    bad["auto_advanceable"] = True
    assert sara.validate_safe_autopilot_decision(bad)["valid"] is False


# ---- structural rejection -> recommend closeout (not edit/advance) ---------

def test_labels_structural_rejection_recommends_closeout():
    d = _decide(sara.STAGE_LABELS_STRUCTURAL_REJECTION)
    assert d["next_safe_action"] == sara.ACTION_RECOMMEND_CLOSEOUT
    assert d["auto_advanceable"] is False
    assert "closeout" in d["reason"].lower()
    assert "edit" in d["reason"].lower() or "advance" in d["reason"].lower()
    assert sara.validate_safe_autopilot_decision(d)["valid"] is True


def test_replay_structural_rejection_recommends_closeout():
    d = _decide(sara.STAGE_REPLAY_STRUCTURAL_REJECTION)
    assert d["next_safe_action"] == sara.ACTION_RECOMMEND_CLOSEOUT
    assert d["auto_advanceable"] is False
    assert sara.validate_safe_autopilot_decision(d)["valid"] is True


# ---- dirty repo / uncommitted artifacts ------------------------------------

def test_dirty_repo_stops_regardless_of_stage():
    for stage in (sara.STAGE_NONE, sara.STAGE_PROPOSAL_READY,
                  sara.STAGE_SPEC_READY, sara.STAGE_DETECTOR_DRY_RUN_READY):
        d = _decide(stage, repo={"clean": False,
                                 "uncommitted_candidate_artifacts": False})
        assert d["next_safe_action"] == sara.ACTION_STOP_DIRTY_REPO, stage
        assert d["auto_advanceable"] is False
        assert d["is_hard_stop"] is True


def test_uncommitted_artifacts_stops():
    d = _decide(sara.STAGE_PROPOSAL_READY,
                repo={"clean": True, "uncommitted_candidate_artifacts": True})
    assert d["next_safe_action"] == sara.ACTION_STOP_DIRTY_REPO
    assert d["auto_advanceable"] is False


# ---- respects the rejected ledger ------------------------------------------

def test_refuses_proposing_a_rejected_family():
    for fam in ("intraweek_calendar_seasonality_drift",         # C10
                "cross_asset_dispersion_reversion",             # C11
                "failed_breakdown_reclaim_reversal",            # C12
                "lead_lag_propagation_continuation",            # C13
                "conviction_bar_follow_through",                # C14
                "slow_vol_targeted_time_series_momentum",       # C15
                "cointegration_pairs_market_neutral"):          # C16
        d = _decide(sara.STAGE_NONE, proposed_family=fam)
        assert d["next_safe_action"] == sara.ACTION_HALT_FAMILY_REJECTED, fam
        assert d["auto_advanceable"] is False
        assert d["is_hard_stop"] is True


def test_default_ledger_contains_c10_through_c16():
    led = sara.DEFAULT_REJECTED_FAMILIES
    for fam in ("intraweek_calendar_seasonality_drift",
                "cross_asset_dispersion_reversion",
                "failed_breakdown_reclaim_reversal",
                "lead_lag_propagation_continuation",
                "conviction_bar_follow_through",
                "slow_vol_targeted_time_series_momentum",
                "cointegration_pairs_market_neutral"):
        assert fam in led, fam
    assert len(led) == 21


# ---- forbidden gates: any labels/replay/etc stage -> hard stop -------------

def test_forbidden_stages_hard_stop():
    for stage in sara.FORBIDDEN_STAGES:
        d = _decide(stage)
        assert d["next_safe_action"] == sara.ACTION_HARD_STOP_FORBIDDEN, stage
        assert d["auto_advanceable"] is False
        assert d["is_hard_stop"] is True
        assert sara.validate_safe_autopilot_decision(d)["valid"] is True


# ---- GLOBAL SAFETY PROOF: never crosses into a forbidden gate ---------------

def test_never_emits_forbidden_action_across_all_states():
    stages = [sara.STAGE_NONE, sara.STAGE_PROPOSAL_READY, sara.STAGE_SPEC_READY,
              sara.STAGE_DETECTOR_DRY_RUN_READY,
              sara.STAGE_LABELS_STRUCTURAL_REJECTION,
              sara.STAGE_REPLAY_STRUCTURAL_REJECTION,
              "unknown_weird_stage"] + list(sara.FORBIDDEN_STAGES)
    repos = [{"clean": True, "uncommitted_candidate_artifacts": False},
             {"clean": False, "uncommitted_candidate_artifacts": False},
             {"clean": True, "uncommitted_candidate_artifacts": True}]
    for stage in stages:
        for repo in repos:
            d = _decide(stage, repo=repo, proposed_family="x_new_family")
            # action is always in the complete allowlist
            assert d["next_safe_action"] in sara.ALL_EMITTABLE_ACTIONS
            # never crosses into a forbidden gate
            assert d["crossed_into_forbidden_gate"] is False
            # auto-advance only ever the 3 build gates
            if d["auto_advanceable"]:
                assert d["next_safe_action"] in sara.AUTO_ADVANCE_ACTIONS
            # the emitted token never names a forbidden executor
            low = (d["recommended_token"] or "").lower()
            for g in ("run_labels", "run_replay", "compute_pnl", "fetch",
                      "place_order", "broker_connect"):
                assert g not in low
            assert sara.validate_safe_autopilot_decision(d)["valid"] is True


def test_capability_flags_all_false_and_tamper_rejected():
    d = _decide(sara.STAGE_SPEC_READY)
    for flag in sara._CAPABILITY_FLAGS_FALSE:
        assert d[flag] is False, flag
        bad = copy.deepcopy(d)
        bad[flag] = True
        assert sara.validate_safe_autopilot_decision(bad)["valid"] is False, flag


def test_tamper_action_to_forbidden_executor_rejected():
    d = _decide(sara.STAGE_SPEC_READY)
    bad = copy.deepcopy(d)
    bad["next_safe_action"] = "RUN_REPLAY_NOW"
    assert sara.validate_safe_autopilot_decision(bad)["valid"] is False


# ---- morning-report summary ------------------------------------------------

def test_morning_report_summary_shows_advance_and_stop():
    adv = sara.summarize_for_morning_report(_decide(sara.STAGE_SPEC_READY))
    assert adv["would_auto_advance"] is True
    assert adv["next_safe_action"] == sara.ACTION_BUILD_DETECTOR
    assert adv["executes_nothing"] is True
    stop = sara.summarize_for_morning_report(
        _decide(sara.STAGE_DETECTOR_DRY_RUN_READY))
    assert stop["would_auto_advance"] is False
    assert stop["stopped_before"] == "real_candle_labels"
    assert stop["is_hard_stop"] is True


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(sara.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch(", "open(", "subprocess", "Popen"):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
              "subprocess", "websockets", "aiohttp", "schedule", "threading",
              "asyncio", "telegram", "csv", "hashlib", "os", "io", "shutil",
              "ssl", "ftplib", "pathlib", "datetime", "random", "json"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned), imported & banned
    for call in ast.walk(tree):
        if isinstance(call, ast.Call):
            name = (call.func.attr if isinstance(call.func, ast.Attribute)
                    else getattr(call.func, "id", ""))
            assert name not in ("open", "exec", "eval", "compile", "__import__"), name
