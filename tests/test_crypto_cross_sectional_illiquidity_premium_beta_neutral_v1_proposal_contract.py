"""Tests for the Candidate #24 cross-sectional illiquidity-premium family proposal.

Proves the proposal is PURE / PROPOSAL-ONLY / QUEUED-BEHIND-C23: it is materially different
from all C1-C21 (26) rejected families AND from the in-flight C22 (external trend-radar) AND
from the on-deck C23 (low-volatility anomaly); it is a DOLLAR- and BETA-NEUTRAL cross-sectional
ILLIQUIDITY (Amihud) risk premium (not directional, not carry, not relative-value, not the
low-vol anomaly); it carries a clear distinctness matrix vs C1-C23; it does NOT displace C22
(stays HOLD) or C23 (stays on-deck), does NOT open C23/C24 as active, and does NOT touch the
C22 pipeline; it is judged vs a RANDOM NEUTRAL null (not buy-and-hold) + top-decile-winner
removal + residual beta ~ 0 + forward-OOS, net of an illiquidity-scaled cost overlay; it
builds no spec/detector/labels/replay, runs no optimization/data-fetch, connects nothing;
downstream gates stay locked; and every capability flag is False."""
from __future__ import annotations

import ast
from pathlib import Path

import sparta_commander.crypto_cross_sectional_illiquidity_premium_beta_neutral_v1_proposal_contract as c24  # noqa: E501
import sparta_commander.research_expansion_plan_v1_contract as rep

_P = c24.build_c24_proposal()


# ---- builds + validates ----------------------------------------------------

def test_proposal_builds_and_validates():
    assert _P["mode"] == "RESEARCH_ONLY"
    assert _P["is_pure_proposal_only"] is True
    assert _P["blockers"] == []
    assert _P["verdict"] == "C24_PROPOSAL_FROZEN_FOR_HUMAN_REVIEW"
    assert c24.validate_c24_proposal(_P)["valid"] is True


# ---- materially different from C1-C21 (26) AND C22 AND C23 -----------------

def test_materially_different_from_rejected_and_c22_and_c23():
    assert _P["candidate_family"] == "crypto_cross_sectional_illiquidity_premium_beta_neutral"
    assert _P["candidate_family"] not in rep.REJECTED_FAMILIES_C1_TO_C21
    assert _P["rejected_families_count"] == 26
    assert _P["candidate_not_in_rejected_ledger"] is True
    assert _P["candidate_distinct_from_c22"] is True
    assert _P["candidate_distinct_from_c23"] is True
    assert _P["candidate_family"] != "external_signum_trend_radar_gc_long_short"
    assert _P["candidate_family"] != "crypto_cross_sectional_low_volatility_anomaly_beta_neutral"
    diffs = " ".join(_P["why_different_from_rejected_and_c22_and_c23"])
    for ref in ("C20", "C21", "C19", "C17", "C22", "C23", "NEUTRAL", "ILLIQUIDITY"):
        assert ref in diffs, ref


# ---- clear distinctness matrix vs C1-C23 -----------------------------------

def test_distinctness_matrix_covers_c1_to_c23():
    matrix = _P["distinctness_matrix"]
    assert len(matrix) >= 8
    cells = " ".join(r["candidates"] for r in matrix)
    for ref in ("C22", "C23", "C19", "C20", "C21", "C17", "C16", "C8"):
        assert ref in cells, ref
    for r in matrix:
        assert r["prior_mechanism"] and r["c24_difference"]


# ---- queued BEHIND C23: does not displace the in-flight C22 or on-deck C23 --

def test_queued_behind_c23_does_not_displace_c22_or_c23():
    assert _P["is_queued_behind_c23_proposal"] is True
    assert _P["queue_position"] == "behind_c23"
    assert _P["active_candidate_in_flight"] == "C22"
    assert _P["c22_state_unchanged"] == "HOLD_FOR_MORE_FROZEN_DATA_WINDOWS"
    assert _P["on_deck_candidate"] == "C23"
    assert _P["c23_state_unchanged"] == "QUEUED_ON_DECK"
    assert _P["does_not_displace_active_c22"] is True
    assert _P["does_not_displace_on_deck_c23"] is True
    assert _P["does_not_open_c23_as_active"] is True
    assert _P["does_not_open_c24_as_active"] is True
    assert _P["does_not_touch_c22_collection_pipeline"] is True
    assert _P["displaces_active_c22"] is False
    assert _P["displaces_on_deck_c23"] is False
    assert _P["opens_c23_as_active"] is False
    assert _P["opens_c24_as_active"] is False
    assert _P["touches_c22_pipeline"] is False


# ---- identity: market-neutral cross-sectional illiquidity risk premium ------

def test_identity_market_neutral_illiquidity_premium():
    ident = _P["strategy_identity"]
    assert ident["is_cross_sectional"] is True
    assert ident["is_dollar_neutral"] is True
    assert ident["is_beta_neutral"] is True
    assert ident["is_directional"] is False
    assert ident["carries_net_market_beta"] is False
    assert ident["is_carry_family"] is False
    assert ident["is_relative_value_mispricing_family"] is False
    assert ident["is_volatility_anomaly_family"] is False
    assert ident["distinct_edge_axis"] == (
        "cross_sectional_amihud_illiquidity_risk_premium_beta_neutral")
    assert _P["is_market_neutral"] is True
    assert _P["is_directional"] is False


# ---- six evaluation variants -----------------------------------------------

def test_six_evaluation_variants():
    keys = {s["key"] for s in _P["evaluation_variants"]}
    assert keys == {
        "baseline_illiquidity_long_short_beta_neutral", "fee_honest_cost_overlay",
        "beta_neutralization_ablation", "rebalance_frequency_turnover_ablation",
        "top_decile_winner_removal_robustness", "forward_oos_holdout"}


# ---- neutral evaluation: random neutral null, NOT buy-and-hold target ------

def test_neutral_evaluation_not_buy_and_hold_target():
    em = _P["evaluation_metrics"]
    assert "beats_random_neutral_null_risk_adjusted" in em["primary_neutral"]
    assert "residual_market_beta_near_zero" in em["primary_neutral"]
    assert em["is_market_neutral_evaluation"] is True
    assert em["buy_and_hold_is_context_reference_only_not_target"] is True
    assert em["illiquidity_cost_paradox_is_decisive"] is True
    assert "top_decile_winner_removal_survives" in em["robustness"]
    assert "survives_illiquidity_scaled_slippage" in em["robustness"]
    wc = em["win_condition"].lower()
    assert "random neutral null" in wc and "top-decile" in wc and "forward-oos" in wc


# ---- cost reserved for replay; illiquidity-scaled slippage; data boundary ---

def test_cost_reserved_and_data_boundary():
    ct = _P["cost_assumptions"]
    assert ct["all_in_round_trip_bps"] == 37.0
    assert ct["slippage_scaled_by_leg_illiquidity"] is True
    assert ct["cost_applied_only_at_replay_gate"] is True
    assert ct["applied_here"] is False
    drq = _P["data_requirements"]
    assert drq["uses_own_or_frozen_data_only"] is True
    assert drq["needs_volume_data"] is True
    assert drq["needs_options_or_implied_vol_data"] is False
    assert drq["needs_funding_or_basis_data"] is False
    assert drq["no_new_data_fetched_in_this_proposal"] is True
    assert drq["no_new_instrument_class"] is True


# ---- advances nothing; downstream gates locked; capability flags ------------

def test_advances_nothing_gates_locked_capabilities():
    assert _P["advances_nothing"] is True
    assert _P["next_required_action"] == (
        "HUMAN_DECISION_OPEN_CANDIDATE_24_AFTER_C23_CONCLUDES_OR_HOLD")
    for g in ("spec_gate_locked", "detector_gate_locked", "labels_gate_locked",
              "replay_gate_locked", "paper_trading_gate_locked", "live_gate_locked"):
        assert _P[g] is True, g
    for flag in c24._CAPABILITY_FLAGS_FALSE:
        assert _P[flag] is False, flag
        assert c24.validate_c24_proposal({**_P, flag: True})["valid"] is False
    for key, val in _P["scope_locks"].items():
        assert val is True, key


# ---- anti-tamper: cannot flip to directional / displace C22 or C23 / drop ledger --

def test_tamper_rejected():
    bad_ident = {**_P["strategy_identity"], "is_directional": True}
    assert c24.validate_c24_proposal(
        {**_P, "strategy_identity": bad_ident})["valid"] is False
    assert c24.validate_c24_proposal(
        {**_P, "does_not_displace_active_c22": False})["valid"] is False
    assert c24.validate_c24_proposal(
        {**_P, "does_not_displace_on_deck_c23": False})["valid"] is False
    assert c24.validate_c24_proposal(
        {**_P, "candidate_distinct_from_c23": False})["valid"] is False
    assert c24.validate_c24_proposal(
        {**_P, "queue_position": "ahead_of_c23"})["valid"] is False


# ---- module purity ---------------------------------------------------------

def test_module_purity():
    src = Path(c24.__file__).read_text(encoding="utf-8")
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
