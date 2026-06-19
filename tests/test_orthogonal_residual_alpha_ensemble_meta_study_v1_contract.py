"""Tests for the Orthogonal Residual-Alpha Ensemble Meta-Study v1 contract.

Verifies: research-only, meta-study-only, descriptive/never-traded, executes nothing;
assigns NO C20 and creates no candidate/family proposal; uses committed C1-C19 evidence
only (no fetch / optimization / replay-beyond-committed); carries the four honest
C16-C19 failure summaries + the recurring failure modes; preserves the honest 'no
durable orthogonal residual alpha' finding (cannot be flipped to claim alpha);
recommends exactly one of the three advisory options and explicitly does NOT recommend
opening C20 outright; capability flags + scope locks; validator anti-tamper; module
purity."""
from __future__ import annotations

import ast

import sparta_commander.orthogonal_residual_alpha_ensemble_meta_study_v1_contract as ms


_R = ms.build_meta_study()


def test_meta_study_research_only_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_meta_study_only"] is True
    assert ms.validate_meta_study(_R)["valid"] is True


def test_does_not_assign_c20_or_create_candidate():
    assert _R["assigns_c20"] is False
    assert _R["c20_assigned"] is False
    assert _R["creates_candidate"] is False
    assert _R["creates_family_proposal"] is False
    assert _R["candidate_id"] is None
    assert _R["is_descriptive_never_traded"] is True


def test_uses_committed_evidence_only_no_fetch_no_optimization():
    assert _R["uses_committed_evidence_only"] is True
    assert _R["no_new_data_fetch"] is True
    assert _R["no_optimization_tuning_rescue"] is True
    assert _R["no_replay_or_pnl_beyond_committed_artifacts"] is True
    assert _R["rejected_ledger_count"] == 24


def test_failure_summaries_c16_to_c19():
    fs = _R["failure_summaries"]
    assert "NEUTRALITY FAILED OUT OF SAMPLE" in fs["C16"]
    assert "RISK-ADJUSTED BUY-AND-HOLD" in fs["C17"]
    assert "RISK-ADJUSTED REPLAY" in fs["C18"]
    assert "NEUTRALITY FAILED THE LABELS GATE" in fs["C19"]
    assert len(_R["common_failure_modes"]) >= 4
    # the failure summaries cannot be silently dropped
    bad = {**_R, "failure_summaries": {k: v for k, v in fs.items() if k != "C19"}}
    assert ms.validate_meta_study(bad)["valid"] is False


def test_orthogonal_residual_finding_honest_and_unflippable():
    assert _R["any_family_with_residual_alpha_worth_candidate"] is False
    assert "NO rejected" in _R["orthogonal_residual_finding"]
    groups = _R["residual_assessment_by_group"]
    for g in ("timing_signals_c14_c15", "market_neutral_rv_c16_c19",
              "allocation_overlay_c17", "directional_timing_c1_c13_c18"):
        assert g in groups and groups[g]
    # cannot be flipped to claim residual alpha
    bad = {**_R, "any_family_with_residual_alpha_worth_candidate": True}
    assert ms.validate_meta_study(bad)["valid"] is False


def test_recommendation_is_advisory_three_options():
    rec = _R["recommendation"]
    assert set(rec["options"]) == {
        "open_c20_with_a_new_family",
        "build_a_stronger_automation_machine_layer_first",
        "stop_and_expand_research_universe_or_data_only_with_explicit_approval"}
    assert rec["recommended_option"] == (
        "stop_and_expand_research_universe_or_data_only_with_explicit_approval")
    assert rec["is_advisory_human_decides"] is True
    assert rec["rationale"]
    # it explicitly does NOT recommend opening C20 outright
    assert "open_c20_with_a_new_family" in rec["explicitly_not_recommended"]
    bad = {**_R, "recommendation": {**rec, "recommended_option": "something_else"}}
    assert ms.validate_meta_study(bad)["valid"] is False


def test_human_gate_preserved_no_c20_without_token():
    assert _R["requires_human_approval_before_c20"] is True
    assert _R["opening_c20_requires_explicit_open_candidate_token"] is True
    nra = ms.get_meta_study_next_action()
    assert nra == _R["next_required_action"]
    assert "NO_C20_ASSIGNED" in nra


def test_no_rejected_family_reproposed():
    assert _R["no_rejected_family_reproposed"] is True
    # every family listed is from the committed rejected ledger (not a new proposal)
    import sparta_commander.research_expansion_plan_v1_contract as rep
    assert set(_R["rejected_families"]) == set(rep.REJECTED_FAMILIES_C1_TO_C19)


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in ms._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert ms.validate_meta_study(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_execute", "no_assign_c20", "no_create_candidate",
                 "no_family_proposal", "no_replay", "no_optimization",
                 "no_data_fetch", "no_repropose_rejected_family",
                 "no_trade_the_ensemble", "no_commit", "no_push", "no_paper_trading",
                 "no_live_trading"):
        assert _R["scope_locks"][must] is True, must


def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(ms.__file__, encoding="utf-8").read()
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
