"""Tests for the Candidate #22 external Signum trend-radar GC long/short family
proposal contract (external_signum_trend_radar_gc_long_short_v1).

Verifies: research-only, pure-proposal-only, executes nothing; chain-gated on the lane's
C22 family-proposal READINESS state (C21 rejected, no active candidate, ledger C1-C21 =
26, next = the C22 readiness token); the EXTERNAL Signum source (prompt TR-GC-Crypto-LS-2,
Bot 25792) is reference-only and connects NOTHING -- no Signum/MCP/Hyperliquid/API/
credentials/orders/bot-edits/Claude-routines; a DIRECTIONAL long/short family materially
different from the rejected C1-C21 families with a distinct external-productized edge axis
and an HONEST directional-trend-graveyard disclosure (C5/C14/C15/C18); judged vs random/
null AND buy-and-hold (mandatory) AND forward-OOS with cost reserved for replay; six
evaluation variants/ablations; preserves the gate sequence; downstream gates locked;
advances nothing; capability flags + scope locks; validator anti-tamper; module purity."""
from __future__ import annotations

import ast

import sparta_commander.external_signum_trend_radar_gc_long_short_v1_proposal_contract as c22  # noqa: E501


_R = c22.build_c22_proposal()


# ---- core: research-only, pure proposal, validates -------------------------

def test_proposal_frozen_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_pure_proposal_only"] is True
    assert _R["blockers"] == []
    assert _R["verdict"] == "C22_PROPOSAL_FROZEN_FOR_HUMAN_REVIEW"
    assert c22.validate_c22_proposal(_R)["valid"] is True


def test_candidate_identity():
    assert _R["candidate_id"] == "C22"
    assert _R["candidate_token"] == "C22_EXTERNAL_SIGNUM_TREND_RADAR_GC_LONG_SHORT_V1"
    assert _R["candidate_family"] == "external_signum_trend_radar_gc_long_short"
    assert _R["candidate_name"] == "external_signum_trend_radar_gc_long_short_v1"


# ---- chain-gated on the lane C22 readiness state ---------------------------

def test_chain_gated_on_lane_c22_readiness():
    assert _R["lane_status_valid"] is True
    assert _R["lane_active_candidate"] is None
    assert _R["lane_next_required_action"] == (
        "HUMAN_DECISION_OPEN_CANDIDATE_22_FAMILY_PROPOSAL_OR_HOLD")
    assert _R["lane_last_rejected_candidate"] == "C21"
    assert _R["opened_from_lane_c22_proposal_readiness"] is True
    # tamper: pretend the lane still had an active candidate -> invalid
    bad = {**_R, "lane_active_candidate": "C21"}
    assert c22.validate_c22_proposal(bad)["valid"] is False
    bad2 = {**_R, "lane_next_required_action": "SOMETHING_ELSE"}
    assert c22.validate_c22_proposal(bad2)["valid"] is False


# ---- external source is reference-only and connects NOTHING ----------------

def test_external_source_reference_only_connects_nothing():
    ext = _R["external_source"]
    assert ext["provider"] == "Signum"
    assert ext["strategy_prompt_id"] == "TR-GC-Crypto-LS-2"
    assert ext["bot_id"] == "25792"
    assert ext["reference_only_not_connected"] is True
    assert ext["exact_rules_transcribed_verbatim_readonly_at_spec_gate"] is True
    assert ext["no_rule_numbers_invented_in_this_proposal"] is True
    for k in ("connects_to_signum", "uses_mcp", "accesses_hyperliquid", "sends_trades",
              "edits_bots", "creates_claude_routines", "uses_api_keys_or_credentials"):
        assert ext[k] is False, k
        bad_ext = {**ext, k: True}
        bad = {**_R, "external_source": bad_ext}
        assert c22.validate_c22_proposal(bad)["valid"] is False, k


# ---- live-trading / external-integration locks -----------------------------

def test_live_trading_and_integration_locks():
    for flag in ("connects_signum", "uses_mcp", "accesses_hyperliquid", "sends_trades",
                 "edits_bots", "creates_claude_routines", "uses_api_keys",
                 "uses_credentials", "connects_broker", "connects_exchange",
                 "places_orders", "contains_order_logic", "paper_trading",
                 "live_trading", "deploys_capital", "installs_scheduler",
                 "modifies_scheduler", "uses_real_money"):
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert c22.validate_c22_proposal(bad)["valid"] is False, flag
    for lock in ("no_signum_connection", "no_mcp", "no_hyperliquid", "no_api_keys",
                 "no_credentials", "no_bot_edits", "no_claude_routines",
                 "no_send_trades", "no_paper_trading", "no_live_trading",
                 "no_scheduler_install", "no_order_logic"):
        assert _R["scope_locks"][lock] is True, lock


# ---- materially different from C1-C21 (honest disclosure) ------------------

def test_materially_different_from_c1_c21():
    assert _R["candidate_not_in_rejected_ledger"] is True
    assert _R["candidate_family"] not in c22.REJECTED_FAMILIES_C1_TO_C21
    assert _R["rejected_families_count"] == 26
    assert len(c22.REJECTED_FAMILIES_C1_TO_C21) == 26
    assert _R["honest_directional_trend_graveyard_disclosure"] is True
    ident = _R["strategy_identity"]
    assert ident["is_external_sourced"] is True
    assert ident["is_directional"] is True
    assert ident["is_long_short_symmetric"] is True
    assert ident["is_long_biased"] is False
    assert ident["is_market_neutral"] is False
    assert ident["is_reparameterization_of_a_rejected_family"] is False
    assert ident["distinct_edge_axis"] == (
        "external_productized_multi_confirmation_trend_radar_long_short")
    # the difference text honestly names the rejected internal trend families
    joined = " ".join(_R["why_different_from_c1_c21"])
    for must in ("C5", "C14", "C15", "C18", "EXTERNAL", "LONG/SHORT"):
        assert must in joined, must
    # tamper: dropping the honest disclosure must fail
    bad = {**_R, "honest_directional_trend_graveyard_disclosure": False}
    assert c22.validate_c22_proposal(bad)["valid"] is False


# ---- directional -> buy-and-hold is a mandatory benchmark ------------------

def test_directional_buy_and_hold_mandatory_benchmark():
    em = _R["evaluation_metrics"]
    assert "beats_buy_and_hold_risk_adjusted" in em["primary_directional"]
    assert em["buy_and_hold_is_mandatory_benchmark"] is True
    assert em["judged_against_buy_and_hold"] is True
    wc = em["win_condition"].lower()
    assert "random" in wc and "buy-and-hold" in wc and "forward-oos" in wc
    assert _R["buy_and_hold_is_mandatory_benchmark"] is True
    bad_em = {**em, "judged_against_buy_and_hold": False}
    bad = {**_R, "evaluation_metrics": bad_em}
    assert c22.validate_c22_proposal(bad)["valid"] is False


# ---- six evaluation variants / ablations -----------------------------------

def test_six_evaluation_variants():
    keys = {v["key"] for v in _R["evaluation_variants"]}
    assert len(_R["evaluation_variants"]) == 6
    for must in ("faithful_replication_as_specified", "fee_honest_cost_overlay",
                 "long_short_vs_long_only_ablation",
                 "trend_radar_only_vs_plus_gc_confirmation_ablation",
                 "turnover_capped_variant", "forward_oos_holdout"):
        assert must in keys, must


# ---- cost reserved for replay; OOS required, rules held fixed --------------

def test_cost_reserved_and_oos_required():
    ct = _R["cost_assumptions"]
    assert ct["all_in_round_trip_bps"] == 37.0
    assert ct["cost_applied_only_at_replay_gate"] is True
    assert ct["applied_here"] is False
    oos = _R["oos_validation"]
    assert oos["forward_oos_required"] is True
    assert oos["forward_oos_must_beat_buy_and_hold_risk_adjusted"] is True
    assert oos["no_parameter_optimization"] is True
    assert oos["faithful_external_rules_held_fixed"] is True
    bad_ct = {**ct, "applied_here": True}
    assert c22.validate_c22_proposal({**_R, "cost_assumptions": bad_ct})["valid"] is False


# ---- data boundary: own/frozen only, no connection/fetch -------------------

def test_data_boundary_no_connection_no_fetch():
    drq = _R["data_requirements"]
    for k in ("uses_own_or_frozen_data_only", "no_signum_connection",
              "no_exchange_or_hyperliquid_fetch", "no_mcp",
              "no_api_keys_or_credentials", "no_new_data_fetched_in_this_proposal"):
        assert drq[k] is True, k
    assert _R["fetches_data"] is False
    assert _R["uses_network"] is False


# ---- gate sequence + downstream locked + advances nothing ------------------

def test_gate_sequence_and_downstream_locked():
    assert _R["gate_sequence"] == [
        "family_proposal", "candidate_spec", "detector_spec_dry_run",
        "real_candle_labels_review", "fee_honest_replay_review",
        "rejection_or_promote_decision"]
    nra = c22.get_candidate_22_proposal_next_action()
    assert nra == _R["next_required_action"]
    assert nra == "HUMAN_DECISION_C22_ADVANCE_TO_CANDIDATE_SPEC_OR_REJECT"
    assert _R["advances_nothing"] is True
    for gate in ("spec_gate_locked", "detector_gate_locked", "labels_gate_locked",
                 "replay_gate_locked", "paper_trading_gate_locked", "live_gate_locked"):
        assert _R[gate] is True, gate
        bad = {**_R, gate: False}
        assert c22.validate_c22_proposal(bad)["valid"] is False, gate


# ---- capability flags + scope locks ----------------------------------------

def test_capability_flags_all_false_and_tamper_rejected():
    for flag in c22._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert c22.validate_c22_proposal(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(c22.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    # no side-effect / network verbs (the strings "mcp"/"hyperliquid" legitimately
    # appear in the lock field names, so they are checked via the import AST below).
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
