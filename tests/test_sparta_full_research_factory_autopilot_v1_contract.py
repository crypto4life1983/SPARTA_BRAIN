"""Tests for the SPARTA Full Research Factory Autopilot v1 contract.

Verifies the encoded machine goal + its safety envelope: the factory CAN autonomously
discover / propose / spec / dry-run / reject / rank research candidates; it CANNOT paper
trade, live trade, connect a broker / use API keys, place orders, or allocate capital;
human approval is REQUIRED before paper / live (and before labels / replay / broker /
order / capital / optimization); the rejected-ledger lessons are respected (C1-C20 / 25,
never retunes a rejected candidate); the current active candidate C21 stays authoritative;
C20 stays rejected; and C22 is NOT started (only created later through the gated
pipeline). Plus: capability flags pinned False, full scope locks, validator anti-tamper,
and module purity (pure declaration -- executes nothing)."""
from __future__ import annotations

import ast

import sparta_commander.sparta_full_research_factory_autopilot_v1_contract as f


_R = f.build_factory_architecture()


# ---- core: research-only, pure, validates ----------------------------------

def test_factory_research_only_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["factory_name"] == "SPARTA_FULL_RESEARCH_FACTORY_AUTOPILOT_V1"
    assert _R["is_pure_architecture_declaration_only"] is True
    assert _R["executes_nothing"] is True
    assert f.validate_factory_architecture(_R)["valid"] is True


# ---- the factory CAN discover / test / reject / rank by itself -------------

def test_factory_can_discover_propose_test_reject_rank():
    for cap in ("can_discover_candidates", "can_propose_candidates",
                "can_generate_specs", "can_generate_detector_and_dry_run",
                "can_reject_on_failed_evidence", "can_rank_on_passed_evidence",
                "can_review_portfolio_before_paper",
                "can_prepare_next_candidate_after_rejection"):
        assert _R[cap] is True, cap
    # the autonomous research stages include the full discover->rank research arc
    auto = _R["autonomous_research_stage_ids"]
    for sid in ("idea_intake", "candidate_proposal_generation",
                "deterministic_spec_generation",
                "detector_spec_and_synthetic_dry_run",
                "formal_rejection_on_failed_evidence", "ranking_on_passed_evidence",
                "next_candidate_preparation_after_rejection"):
        assert sid in auto, sid
        assert f.factory_can_autonomously(sid) is True, sid
    # tamper: dropping a research autonomy must fail validation
    bad = {**_R, "can_reject_on_failed_evidence": False}
    assert f.validate_factory_architecture(bad)["valid"] is False


# ---- the factory CANNOT paper trade ----------------------------------------

def test_factory_cannot_paper_trade():
    assert _R["paper_trades"] is False
    assert "no_paper_trading" in _R["hard_locks"]
    assert _R["scope_locks"]["no_paper_trading"] is True
    assert f.factory_can_autonomously("paper_trading") is False
    assert "paper_trading" not in _R["autonomous_research_stage_ids"]
    bad = {**_R, "paper_trades": True}
    assert f.validate_factory_architecture(bad)["valid"] is False


# ---- the factory CANNOT live trade -----------------------------------------

def test_factory_cannot_live_trade():
    assert _R["live_trades"] is False
    assert "no_live_trading" in _R["hard_locks"]
    assert _R["scope_locks"]["no_live_trading"] is True
    assert f.factory_can_autonomously("live_trading") is False
    bad = {**_R, "live_trades": True}
    assert f.validate_factory_architecture(bad)["valid"] is False


# ---- the factory CANNOT connect broker / order APIs ------------------------

def test_factory_cannot_connect_broker_or_place_orders():
    for flag in ("connects_broker", "connects_exchange", "uses_api_keys",
                 "uses_credentials", "places_orders", "contains_order_logic",
                 "calls_api", "uses_network"):
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert f.validate_factory_architecture(bad)["valid"] is False, flag
    for lock in ("no_broker_connection", "no_api_key_use", "no_order_placement"):
        assert lock in _R["hard_locks"], lock


# ---- human approval REQUIRED before paper / live ---------------------------

def test_human_approval_required_before_paper_and_live():
    assert _R["requires_human_before_paper_trading"] is True
    assert _R["requires_human_before_live_trading"] is True
    for must in ("paper_trading", "live_trading", "broker_or_api_key_use",
                 "order_placement", "capital_allocation",
                 "any_optimization_tuning_or_edit_beyond_permitted_rule"):
        assert must in _R["human_gates_before"], must
        assert f.human_gate_required_before(must) is True, must
    # labels + replay are research, but only AFTER the human gate
    assert _R["real_data_labels_requires_human_gate"] is True
    assert _R["fee_honest_replay_requires_human_gate"] is True
    assert "real_data_labels" in _R["human_gated_stage_ids"]
    assert "fee_honest_replay" in _R["human_gated_stage_ids"]
    assert f.factory_can_autonomously("real_data_labels") is False
    assert f.factory_can_autonomously("fee_honest_replay") is False
    bad = {**_R, "requires_human_before_paper_trading": False}
    assert f.validate_factory_architecture(bad)["valid"] is False


# ---- rejected-ledger lessons respected -------------------------------------

def test_rejected_ledger_lessons_respected():
    assert _R["respects_rejected_ledger"] is True
    assert _R["rejected_ledger_count"] == 26
    assert _R["rejected_ledger_is_c1_to_c21"] is True
    assert _R["never_reproposes_rejected_family"] is True
    assert _R["never_retunes_rejected_candidate"] is True
    assert "no_retuning_rejected_candidates" in _R["hard_locks"]
    bad = {**_R, "never_retunes_rejected_candidate": False}
    assert f.validate_factory_architecture(bad)["valid"] is False


# ---- no active candidate; C21+C20 rejected; C22 not started ----------------

def test_c21_authoritative_c20_rejected_c22_not_started():
    assert _R["active_candidate"] is None
    assert _R["active_candidate_is_none_authoritative"] is True
    assert _R["last_rejected_candidate"] == "C21"
    assert _R["c21_remains_rejected"] is True
    assert _R["c20_remains_rejected"] is True
    assert "no_rescue_of_c20" in _R["hard_locks"]
    assert _R["c22_started"] is False
    assert _R["c22_candidate_id"] is None
    assert _R["c22_is_next_proposal_readiness_only"] is True
    assert _R["c22_only_created_after_current_candidate_resolved"] is True
    for bad_kv in (("active_candidate", "C22"), ("c20_remains_rejected", False),
                   ("c21_remains_rejected", False), ("c22_started", True)):
        bad = {**_R, bad_kv[0]: bad_kv[1]}
        assert f.validate_factory_architecture(bad)["valid"] is False, bad_kv[0]


# ---- no silent gate crossing -----------------------------------------------

def test_no_silent_gate_crossing():
    assert _R["crosses_human_gate_silently"] is False
    assert _R["advances_without_human_approval"] is False
    assert _R["promotes_to_paper_without_human"] is False
    assert _R["promotes_to_live_without_human"] is False
    assert "no_crossing_human_gates_silently" in _R["hard_locks"]
    assert _R["scope_locks"]["no_silent_gate_cross"] is True


# ---- pipeline is complete + every stage classified -------------------------

def test_pipeline_complete_and_every_stage_classified():
    stages = _R["pipeline_stages"]
    ids = [s["id"] for s in stages]
    assert len(ids) == len(set(ids))   # no duplicates
    assert len(ids) == 11              # the full declared pipeline
    for s in stages:
        assert s["autonomy"] in (f.AUTONOMY_RESEARCH, f.AUTONOMY_HUMAN_GATED)
        if s["autonomy"] == f.AUTONOMY_HUMAN_GATED:
            assert s["human_gate"], s["id"]
        else:
            assert s["human_gate"] is None, s["id"]


# ---- capability flags + scope locks ----------------------------------------

def test_capability_flags_all_false_and_tamper_rejected():
    for flag in f._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert f.validate_factory_architecture(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_execute", "no_labels", "no_replay", "no_broker", "no_api_keys",
                 "no_order_logic", "no_paper_trading", "no_live_trading",
                 "no_capital_allocation", "no_hidden_optimization",
                 "no_retune_rejected", "no_rescue_c20", "no_silent_gate_cross"):
        assert _R["scope_locks"][must] is True, must


# ---- morning-report-style output -------------------------------------------

def test_summarize_for_morning_report():
    summ = f.summarize_for_morning_report()
    assert summ["section"] == "sparta_full_research_factory_autopilot_v1"
    assert summ["factory_name"] == "SPARTA_FULL_RESEARCH_FACTORY_AUTOPILOT_V1"
    assert summ["active_candidate"] is None
    assert summ["active_candidate_is_none_authoritative"] is True
    assert summ["last_rejected_candidate"] == "C21"
    assert summ["c21_remains_rejected"] is True
    assert summ["c20_remains_rejected"] is True
    assert summ["c22_started"] is False
    assert summ["requires_human_before_paper_trading"] is True
    assert summ["requires_human_before_live_trading"] is True
    assert "real_data_labels" in summ["human_gated_stages"]
    assert "fee_honest_replay" in summ["human_gated_stages"]
    assert summ["executes_nothing"] is True


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(f.__file__, encoding="utf-8").read()
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
