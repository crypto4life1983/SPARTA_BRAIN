"""Tests for the Candidate #25 video momentum-breakout / scalping INTAKE + DISTINCTNESS REVIEW.

Proves the review is PURE / REVIEW-ONLY / NO-GO: the 'break and bounce' 5-minute
momentum-breakout scalping family is NOT materially distinct (it recombines/reparameterizes
already-rejected directional families C3/C4 breakout-pullback, C14 conviction/reversal candle,
C15 time-series momentum, C18 MA trend-following, C8/C9 buy-the-dip); the overlap matrix cites
only REAL rejected families with >= 4 HIGH overlaps and contrasts the directional shape against
C22/C23/C24; the required skepticism (unverified claims, overfitting, 5-minute scalping
cost/slippage, drawdown gate, beat realistic costs + correct benchmark) is encoded; the
C22/C23/C24 queue is preserved with NO C25 proposal created and nothing mutated; and every
capability flag is False. It is an ADDITIVE new surface that modifies no C21-C24 or
lane-status file."""
from __future__ import annotations

import ast
from pathlib import Path

import sparta_commander.c25_video_momentum_breakout_scalping_intake_review_contract as c25r
import sparta_commander.research_expansion_plan_v1_contract as rep

_R = c25r.build_c25_intake_review()


# ---- builds + validates as a NO-GO review ----------------------------------

def test_review_builds_and_validates_as_no_go():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_pure_review_only"] is True
    assert _R["is_proposal"] is False
    assert _R["blockers"] == []
    assert _R["verdict"] == "C25_NO_GO_NEAR_DUPLICATE_OF_REJECTED_DIRECTIONAL_FAMILIES"
    assert _R["recommendation"] == "REMAIN_IDEA_BANK_NO_GO"
    assert c25r.validate_c25_intake_review(_R)["valid"] is True


# ---- NOT materially distinct: a recombination of rejected families ---------

def test_not_materially_distinct():
    assert _R["is_materially_distinct_enough_for_c25"] is False
    da = _R["distinctness_assessment"]
    assert da["introduces_new_edge_axis"] is False
    assert da["is_recombination_of_rejected_families"] is True
    assert da["is_reparameterization_of_rejected_families"] is True
    assert da["neutral_high_breadth_shape"] is False
    assert da["matched_rejected_family_count"] >= 4


# ---- overlap matrix cites only REAL rejected families, >= 4 HIGH -----------

def test_overlap_matrix_cites_real_rejected_families():
    matrix = _R["overlap_matrix"]
    highs = [r for r in matrix if r["overlap"] == "HIGH"]
    assert len(highs) >= 4
    matched = {r["matched_family"] for r in matrix if r["matched_family"]}
    for fam in matched:
        assert fam in rep.REJECTED_FAMILIES_C1_TO_C21, fam
    for must in ("h4_trend_following_market_structure",
                 "slow_vol_targeted_time_series_momentum",
                 "conviction_bar_follow_through",
                 "crypto_intraday_breakout_pullback_structure",
                 "liquidity_sweep_mean_reversion"):
        assert must in matched, must


# ---- directional shape contrasted against C22 (same) and C23/C24 (opposite) -

def test_directional_shape_contrast():
    blob = " ".join(str(r.get("also", "")) + " " + str(r.get("note", ""))
                    for r in _R["overlap_matrix"])
    assert "external_signum_trend_radar_gc_long_short" in blob
    assert "C23" in blob and "C24" in blob
    assert "NEUTRAL" in blob


# ---- required skepticism is encoded ----------------------------------------

def test_skepticism_flags_encoded():
    sf = _R["skepticism_flags"]
    for k in ("video_and_backtest_claims_unverified",
              "overfitting_risk_multiple_variants_and_brackets",
              "five_minute_scalping_cost_slippage_risk",
              "high_turnover_churn_destroys_edge_c20_lesson",
              "high_drawdown_unacceptable_without_strict_fee_honest_drawdown_gate",
              "must_beat_realistic_costs_not_just_buy_and_hold",
              "must_beat_correct_benchmark_not_buy_and_hold_only"):
        assert sf[k] is True, k
    assert len(_R["cost_drawdown_concerns"]) >= 3
    assert _R["must_beat_realistic_costs_and_correct_benchmark"] is True


# ---- queue preserved; no C25 proposal created; nothing mutated -------------

def test_queue_preserved_and_no_proposal_created():
    qs = _R["queue_snapshot"]
    assert qs["c22_state"] == "HOLD_FOR_MORE_FROZEN_DATA_WINDOWS"
    assert qs["c22_progress"] == "2/20"
    assert qs["c22_replay_locked"] is True
    assert qs["c23_on_deck"] is True
    assert qs["c24_queued_behind_c23"] is True
    assert qs["c25_created_as_proposal"] is False
    assert qs["c25_opened_as_active"] is False
    assert _R["creates_c25_proposal"] is False
    assert _R["promotes_to_c25"] is False
    assert _R["next_gate"] == "NONE_NO_GO_REMAINS_IDEA_BANK"
    for k in ("does_not_open_c25_as_active", "does_not_open_c24_as_active",
              "does_not_open_c23_as_active", "does_not_advance_c22",
              "does_not_modify_c21_c22_c23_c24_files",
              "does_not_modify_lane_status_surface"):
        assert _R[k] is True, k


# ---- advances nothing; capability flags all False --------------------------

def test_advances_nothing_capabilities_false():
    assert _R["advances_nothing"] is True
    for flag in c25r._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        assert c25r.validate_c25_intake_review({**_R, flag: True})["valid"] is False
    for key, val in _R["scope_locks"].items():
        assert val is True, key


# ---- anti-tamper: cannot flip to distinct / proposal / advance C22 ----------

def test_tamper_rejected():
    assert c25r.validate_c25_intake_review(
        {**_R, "is_materially_distinct_enough_for_c25": True})["valid"] is False
    assert c25r.validate_c25_intake_review(
        {**_R, "verdict": "C25_PROPOSAL_FROZEN_FOR_HUMAN_REVIEW"})["valid"] is False
    assert c25r.validate_c25_intake_review(
        {**_R, "creates_c25_proposal": True})["valid"] is False
    assert c25r.validate_c25_intake_review(
        {**_R, "does_not_advance_c22": False})["valid"] is False
    # a fabricated overlap citation (family not in the ledger) must fail
    bad_matrix = [{**_R["overlap_matrix"][0], "matched_family": "totally_made_up_family"}]
    assert c25r.validate_c25_intake_review(
        {**_R, "overlap_matrix": bad_matrix})["valid"] is False


# ---- module purity ---------------------------------------------------------

def test_module_purity():
    src = Path(c25r.__file__).read_text(encoding="utf-8")
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "open(",
                 "subprocess", "Popen", "urlopen", "requests.", "socket.connect",
                 "json.load", "read_text"):
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
