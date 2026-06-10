"""Tests for the Crypto-D1 V2 Resume-Policy Research & Simulation Plan (READ-ONLY, PLAN
ONLY). This module PLANS but never runs anything: no simulation, no backtest, no
optimization, no parameter search, no broker, no exchange, no network, no credentials, no
real order, no gate unlock. The tests are fully hermetic (no disk, no network)."""

from __future__ import annotations

import ast

import sparta_commander.strategy_factory_crypto_d1_resume_policy_research_plan as rp
import sparta_commander.strategy_factory_crypto_d1_paper_run_review_contract as rv


# --------------------------------------------------------------------------- #
# build / shape
# --------------------------------------------------------------------------- #
def test_build_is_plan_ready_for_v2():
    plan = rp.build_resume_policy_plan(repo_root=".")
    assert plan["verdict"] == rp.VERDICT_PLAN_READY
    assert plan["mode"] == "RESEARCH_ONLY"
    assert plan["selected_variant_id"] == "V2_trend_plus_cash_regime"
    assert plan["next_required_action"] == rp.NEXT_REQUIRED_ACTION


def test_addresses_the_three_review_blockers():
    plan = rp.build_resume_policy_plan(repo_root=".")
    assert plan["addresses_blockers"] == [
        "run_halted_pending_human_resume",
        "kill_switch_triggered_needs_resume_policy_review",
        "insufficient_regime_evidence_for_micro_live",
    ]


def test_label():
    assert rp.get_resume_policy_plan_label() == rp.PLAN_LABEL


# --------------------------------------------------------------------------- #
# resume-policy candidates
# --------------------------------------------------------------------------- #
def test_six_candidates_each_well_formed():
    cands = rp.resume_policy_candidates()
    assert len(cands) == 6
    ids = [c["policy_id"] for c in cands]
    assert ids == [
        "RP1_wait_7d_trend_on", "RP2_wait_14d_trend_on", "RP3_wait_30d_trend_on",
        "RP4_breadth_2of3_above_sma200", "RP5_half_then_full_on_confirmation",
        "RP6_resume_after_volatility_cools",
    ]
    for c in cands:
        for key in ("policy_id", "description", "resume_trigger", "reentry_exposure", "hypothesis"):
            assert key in c
        assert isinstance(c["resume_trigger"], dict)


def test_staged_policy_has_half_then_full_exposure():
    rp5 = next(c for c in rp.resume_policy_candidates() if c["policy_id"] == "RP5_half_then_full_on_confirmation")
    assert rp5["reentry_exposure"] == "HALF_THEN_FULL"
    assert rp5["exposure_stages"] == [0.5, 1.0]


def test_candidates_are_deep_copied():
    a = rp.resume_policy_candidates()
    a[0]["resume_trigger"]["min_days_halted"] = 999
    b = rp.resume_policy_candidates()
    assert b[0]["resume_trigger"]["min_days_halted"] == 7


# --------------------------------------------------------------------------- #
# regimes
# --------------------------------------------------------------------------- #
def test_four_regimes_to_cover():
    regimes = rp.regimes_to_cover()
    assert len(regimes) == 4
    assert [r["regime_id"] for r in regimes] == [
        "2021_bull_then_may_crash", "2022_bear", "2023_2024_recovery", "2025_2026_recent",
    ]


# --------------------------------------------------------------------------- #
# simulation rerun plan -- one per policy, NOTHING RUN
# --------------------------------------------------------------------------- #
def test_one_rerun_per_policy_none_run():
    reruns = rp.simulation_rerun_plan()
    policy_ids = [c["policy_id"] for c in rp.resume_policy_candidates()]
    assert len(reruns) == len(policy_ids)
    assert sorted(r["policy_id"] for r in reruns) == sorted(policy_ids)
    for r in reruns:
        assert r["is_run"] is False
        assert r["requires_human_command"] is True
        assert r["selected_variant_id"] == "V2_trend_plus_cash_regime"
        assert r["data_scope"] == "QA_PASSED_LOCAL_CSV_ONLY"
        assert r["authorization_required"] == rp.NEXT_REQUIRED_ACTION


# --------------------------------------------------------------------------- #
# capability / gate posture
# --------------------------------------------------------------------------- #
def test_plan_runs_nothing_and_locks_all_gates():
    plan = rp.build_resume_policy_plan(repo_root=".")
    for key in ("runs_simulation", "runs_backtest", "runs_optimization",
                "runs_parameter_search", "executes", "connects_broker",
                "connects_exchange", "uses_real_money", "uses_network",
                "uses_credentials", "authorizes_micro_live", "authorizes_live_trading",
                "unlocks_downstream_gate"):
        assert plan[key] is False
    assert plan["paper_trading_gate_locked"] is True
    assert plan["micro_live_gate_locked"] is True
    assert plan["live_gate_locked"] is True


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #
def test_validate_passes_on_built_plan():
    plan = rp.build_resume_policy_plan(repo_root=".")
    assert rp.validate_resume_policy_plan(plan)["valid"] is True


def test_validate_rejects_non_dict():
    v = rp.validate_resume_policy_plan(None)
    assert v["valid"] is False
    assert "plan_not_a_dict" in v["errors"]


def test_validate_rejects_unlocked_gate():
    plan = rp.build_resume_policy_plan(repo_root=".")
    plan["micro_live_gate_locked"] = False
    v = rp.validate_resume_policy_plan(plan)
    assert v["valid"] is False
    assert any("gate_not_locked:micro_live_gate_locked" in e for e in v["errors"])


def test_validate_rejects_runs_simulation_true():
    plan = rp.build_resume_policy_plan(repo_root=".")
    plan["runs_simulation"] = True
    v = rp.validate_resume_policy_plan(plan)
    assert v["valid"] is False
    assert any("capability_not_false:runs_simulation" in e for e in v["errors"])


def test_validate_rejects_rerun_marked_run():
    plan = rp.build_resume_policy_plan(repo_root=".")
    plan["simulation_rerun_plan"][0]["is_run"] = True
    v = rp.validate_resume_policy_plan(plan)
    assert v["valid"] is False
    assert any(e.startswith("rerun_marked_run:") for e in v["errors"])


def test_validate_rejects_rerun_not_human_gated():
    plan = rp.build_resume_policy_plan(repo_root=".")
    plan["simulation_rerun_plan"][0]["requires_human_command"] = False
    v = rp.validate_resume_policy_plan(plan)
    assert v["valid"] is False
    assert any(e.startswith("rerun_not_human_gated:") for e in v["errors"])


def test_validate_rejects_rerun_unknown_policy():
    plan = rp.build_resume_policy_plan(repo_root=".")
    plan["simulation_rerun_plan"][0]["policy_id"] = "RP_DOES_NOT_EXIST"
    v = rp.validate_resume_policy_plan(plan)
    assert v["valid"] is False
    assert any(e.startswith("rerun_references_unknown_policy:") for e in v["errors"])


def test_validate_rejects_duplicate_policy_id():
    plan = rp.build_resume_policy_plan(repo_root=".")
    plan["resume_policy_candidates"].append(dict(plan["resume_policy_candidates"][0]))
    v = rp.validate_resume_policy_plan(plan)
    assert v["valid"] is False
    assert any(e.startswith("duplicate_policy_id:") for e in v["errors"])


# --------------------------------------------------------------------------- #
# current review wiring (best-effort, never raises)
# --------------------------------------------------------------------------- #
def test_current_review_decision_is_do_not_promote_when_report_present():
    # The local real report (if present) must never read as a promotion; absent report
    # leaves the field None. Either way micro-live stays locked.
    plan = rp.build_resume_policy_plan(repo_root=".")
    assert plan["current_review_decision"] in (None, rv.DO_NOT_PROMOTE_TO_MICRO_LIVE_YET)
    assert plan["micro_live_gate_locked"] is True


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #
def test_render_markdown_is_string():
    md = rp.render_resume_policy_plan_markdown(rp.build_resume_policy_plan(repo_root="."))
    assert md.startswith("# Crypto-D1 V2 Resume-Policy Research & Simulation Plan")
    assert "RP1_wait_7d_trend_on" in md
    assert "LOCKED" in md
    assert "NOT YET RUN" in md


# --------------------------------------------------------------------------- #
# no network / credential imports
# --------------------------------------------------------------------------- #
def test_module_imports_no_network_or_credential_modules():
    with open(rp.__file__, "r", encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    banned = {"urllib", "requests", "socket", "http", "ftplib", "ccxt", "databento", "dotenv", "smtplib"}
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imported.add(n.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert not (imported & banned)
