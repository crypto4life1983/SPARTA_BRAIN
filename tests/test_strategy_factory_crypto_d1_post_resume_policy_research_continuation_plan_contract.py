"""Tests for the Crypto-D1 V2 Post-Resume-Policy Research Continuation Plan (READ-ONLY).

Every decision consumed here is a FAKE in-memory dict (or one derived under tmp_path); no
network, no credentials, no real data, no broker, no exchange, no real order, no simulation,
no file write, no gate is unlocked. The plan decides what research to do next using the
resume-policy chain as evidence and strictly preserves DO_NOT_PROMOTE_RESUME_POLICY_YET."""

from __future__ import annotations

import ast
import json

import sparta_commander.strategy_factory_crypto_d1_post_resume_policy_research_continuation_plan_contract as rc
import sparta_commander.strategy_factory_crypto_d1_resume_policy_human_review_decision_contract as hr
import sparta_commander.strategy_factory_crypto_d1_resume_policy_results_review_contract as rr
import sparta_commander.strategy_factory_crypto_d1_resume_policy_simulation_runner as rs


def _policy(pid, *, mean_ret, worst_dd, mean_sharpe, regimes=4, real_orders=0):
    regime_results = []
    for k in range(regimes):
        regime_results.append({
            "regime_id": f"regime_{k}", "window": "2021-01-01..2021-12-31",
            "evaluated": True,
            "metrics": {
                "total_return": mean_ret, "max_drawdown": worst_dd,
                "sharpe_ratio": mean_sharpe, "real_orders_placed": real_orders,
                "num_kill_events": 1, "num_resume_events": 1, "halted_at_end": False,
            },
        })
    return {
        "policy_id": pid, "description": pid, "reentry_exposure": "FULL",
        "regime_results": regime_results,
        "aggregate": {
            "regimes_evaluated": regimes, "mean_total_return": mean_ret,
            "min_total_return": mean_ret, "worst_max_drawdown": worst_dd,
            "mean_sharpe_ratio": mean_sharpe,
        },
    }


def _sim_report(*, complete=True, rankings_leader="RP6_resume_after_volatility_cools",
                real_orders=0, override=None):
    from sparta_commander.strategy_factory_crypto_d1_paper_trading_prep_contract import build_paper_prep_config
    rep = rs._base_report(build_paper_prep_config())
    rep.update({
        "verdict": rs.VERDICT_RERUNS_COMPLETE if complete else rs.VERDICT_BLOCKED_NOT_READY,
        "blockers": [],
        "selected_variant_id": "V2_trend_plus_cash_regime",
        "symbols": ["BTC", "ETH", "SOL"],
        "policy_results": [
            _policy("RP1_wait_7d_trend_on", mean_ret=0.68, worst_dd=-0.61, mean_sharpe=0.09),
            _policy("RP6_resume_after_volatility_cools", mean_ret=1.55, worst_dd=-0.32,
                    mean_sharpe=0.57, real_orders=real_orders),
        ],
        "rankings": {
            "best_by_mean_return": rankings_leader,
            "best_by_worst_drawdown": rankings_leader,
            "best_by_mean_sharpe": rankings_leader,
        },
        "files_read": [], "files_written": [],
    })
    if override:
        rep.update(override)
    return rep


def _review_decision(**kwargs):
    d = rr.review_resume_policy_results(_sim_report(**kwargs))
    d["resume_policy_sim_report_found"] = True
    d["resume_policy_sim_report_path"] = "reports/crypto_d1_resume_policy_sim/resume_policy_sim_report.json"
    return d


def _human_review(**kwargs):
    """A valid Block 178 RECORDED human-review decision derived from a fake review."""
    return hr.record_human_review_decision(_review_decision(**kwargs))


# --------------------------------------------------------------------------- #
# disk-backed build: recorded upstream review -> READY plan, DO_NOT_PROMOTE kept
# --------------------------------------------------------------------------- #
def test_build_ready_plan_preserves_do_not_promote(tmp_path):
    out = tmp_path / "reports" / "crypto_d1_resume_policy_sim"
    out.mkdir(parents=True, exist_ok=True)
    (out / "resume_policy_sim_report.json").write_text(json.dumps(_sim_report()), encoding="utf-8")
    p = rc.build_post_resume_policy_research_continuation_plan(repo_root=str(tmp_path))
    assert p["verdict"] == rc.VERDICT_PLAN_READY
    assert p["human_decision"] == hr.DECISION_DO_NOT_PROMOTE
    assert p["human_decision"] == "DO_NOT_PROMOTE_RESUME_POLICY_YET"
    assert p["approved_for_execution"] is False
    assert p["human_review_required"] is True
    assert p["upstream_review_verdict"] == hr.VERDICT_HUMAN_REVIEW_RECORDED
    assert p["next_required_action"] == "HUMAN_SELECT_RESEARCH_CONTINUATION_DIRECTION"
    assert p["blockers"] == []


def test_build_acknowledges_leader_as_evidence_only(tmp_path):
    out = tmp_path / "reports" / "crypto_d1_resume_policy_sim"
    out.mkdir(parents=True, exist_ok=True)
    (out / "resume_policy_sim_report.json").write_text(json.dumps(_sim_report()), encoding="utf-8")
    p = rc.build_post_resume_policy_research_continuation_plan(repo_root=str(tmp_path))
    assert p["evidence_leading_policy"]["policy_id"] == "RP6_resume_after_volatility_cools"
    assert "acknowledged_evidence_leading_policy:RP6_resume_after_volatility_cools" in p["risk_notes"]
    assert "acknowledged_as_evidence_only_not_promotion" in p["risk_notes"]
    assert "promotion_requires_separate_explicit_human_command" in p["risk_notes"]


def test_build_blocks_when_no_local_report(tmp_path):
    p = rc.build_post_resume_policy_research_continuation_plan(repo_root=str(tmp_path))
    assert p["verdict"] == rc.VERDICT_PLAN_BLOCKED
    # the human decision is STILL preserved as DO_NOT_PROMOTE even when blocked
    assert p["human_decision"] == hr.DECISION_DO_NOT_PROMOTE
    assert "human_review_not_recorded" in p["blockers"]


# --------------------------------------------------------------------------- #
# the plan unlocks nothing and runs nothing
# --------------------------------------------------------------------------- #
def test_plan_unlocks_nothing(tmp_path):
    out = tmp_path / "reports" / "crypto_d1_resume_policy_sim"
    out.mkdir(parents=True, exist_ok=True)
    (out / "resume_policy_sim_report.json").write_text(json.dumps(_sim_report()), encoding="utf-8")
    p = rc.build_post_resume_policy_research_continuation_plan(repo_root=str(tmp_path))
    assert p["paper_trading_gate_locked"] is True
    assert p["micro_live_gate_locked"] is True
    assert p["live_gate_locked"] is True
    for key in (
        "executes", "writes_files", "runs_simulation", "runs_backtest",
        "runs_optimization", "ran_parameter_search", "parameters_changed_based_on_results",
        "fetches_data", "connects_broker", "connects_exchange", "uses_real_money",
        "uses_network", "uses_credentials", "authorizes_paper_execution",
        "authorizes_micro_live", "authorizes_live_trading", "promotes_gate",
        "promotes_resume_policy", "unlocks_downstream_gate",
    ):
        assert p[key] is False, key


# --------------------------------------------------------------------------- #
# research-continuation directions are fixed, inert, human-gated, non-optimizing
# --------------------------------------------------------------------------- #
def test_directions_are_fixed_inert_and_human_gated():
    dirs = rc.research_continuation_directions()
    assert len(dirs) == 4
    ids = [d["direction_id"] for d in dirs]
    assert len(ids) == len(set(ids))
    for d in dirs:
        assert d["is_executed"] is False
        assert d["requires_human_command"] is True
        assert d["changes_strategy_parameters"] is False
        assert d["is_optimization"] is False
        assert d["is_search"] is False
        assert d["data_scope"] in (
            "QA_PASSED_LOCAL_CSV_ONLY",
            "EXISTING_SIMULATED_OUTPUTS_ONLY",
            "DOCUMENTATION_ONLY",
        )


def test_directions_accessor_returns_copies():
    a = rc.research_continuation_directions()
    a[0]["is_executed"] = True
    a[0]["direction_id"] = "tampered"
    b = rc.research_continuation_directions()
    assert b[0]["is_executed"] is False
    assert b[0]["direction_id"] != "tampered"
    assert all(d["is_executed"] is False for d in rc.RESEARCH_CONTINUATION_DIRECTIONS)


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #
def test_validate_passes_on_ready(tmp_path):
    out = tmp_path / "reports" / "crypto_d1_resume_policy_sim"
    out.mkdir(parents=True, exist_ok=True)
    (out / "resume_policy_sim_report.json").write_text(json.dumps(_sim_report()), encoding="utf-8")
    p = rc.build_post_resume_policy_research_continuation_plan(repo_root=str(tmp_path))
    assert rc.validate_post_resume_policy_research_continuation_plan(p)["valid"] is True


def test_validate_passes_on_blocked(tmp_path):
    p = rc.build_post_resume_policy_research_continuation_plan(repo_root=str(tmp_path))
    assert rc.validate_post_resume_policy_research_continuation_plan(p)["valid"] is True


def test_validate_rejects_unlocked_gate(tmp_path):
    out = tmp_path / "reports" / "crypto_d1_resume_policy_sim"
    out.mkdir(parents=True, exist_ok=True)
    (out / "resume_policy_sim_report.json").write_text(json.dumps(_sim_report()), encoding="utf-8")
    p = rc.build_post_resume_policy_research_continuation_plan(repo_root=str(tmp_path))
    p["micro_live_gate_locked"] = False
    v = rc.validate_post_resume_policy_research_continuation_plan(p)
    assert v["valid"] is False
    assert any("gate_not_locked:micro_live_gate_locked" in e for e in v["errors"])


def test_validate_rejects_promote_decision(tmp_path):
    out = tmp_path / "reports" / "crypto_d1_resume_policy_sim"
    out.mkdir(parents=True, exist_ok=True)
    (out / "resume_policy_sim_report.json").write_text(json.dumps(_sim_report()), encoding="utf-8")
    p = rc.build_post_resume_policy_research_continuation_plan(repo_root=str(tmp_path))
    p["human_decision"] = "PROMOTE_RESUME_POLICY_FOR_EXECUTION"
    v = rc.validate_post_resume_policy_research_continuation_plan(p)
    assert v["valid"] is False
    assert any("human_decision_not_do_not_promote" in e for e in v["errors"])


def test_validate_rejects_executed_direction(tmp_path):
    out = tmp_path / "reports" / "crypto_d1_resume_policy_sim"
    out.mkdir(parents=True, exist_ok=True)
    (out / "resume_policy_sim_report.json").write_text(json.dumps(_sim_report()), encoding="utf-8")
    p = rc.build_post_resume_policy_research_continuation_plan(repo_root=str(tmp_path))
    p["research_continuation_directions"][0]["is_executed"] = True
    v = rc.validate_post_resume_policy_research_continuation_plan(p)
    assert v["valid"] is False
    assert any(e.startswith("direction_marked_executed:") for e in v["errors"])


def test_validate_rejects_optimizing_direction(tmp_path):
    out = tmp_path / "reports" / "crypto_d1_resume_policy_sim"
    out.mkdir(parents=True, exist_ok=True)
    (out / "resume_policy_sim_report.json").write_text(json.dumps(_sim_report()), encoding="utf-8")
    p = rc.build_post_resume_policy_research_continuation_plan(repo_root=str(tmp_path))
    p["research_continuation_directions"][0]["is_optimization"] = True
    v = rc.validate_post_resume_policy_research_continuation_plan(p)
    assert v["valid"] is False
    assert any("direction_capability_not_false:is_optimization" in e for e in v["errors"])


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #
def test_render_markdown_is_string(tmp_path):
    out = tmp_path / "reports" / "crypto_d1_resume_policy_sim"
    out.mkdir(parents=True, exist_ok=True)
    (out / "resume_policy_sim_report.json").write_text(json.dumps(_sim_report()), encoding="utf-8")
    p = rc.build_post_resume_policy_research_continuation_plan(repo_root=str(tmp_path))
    md = rc.render_post_resume_policy_research_continuation_plan_markdown(p)
    assert md.startswith("# Crypto-D1 V2 Post-Resume-Policy Research Continuation Plan")
    assert "DO_NOT_PROMOTE_RESUME_POLICY_YET" in md and "LOCKED" in md
    assert "RP6_resume_after_volatility_cools" in md


# --------------------------------------------------------------------------- #
# label / posture
# --------------------------------------------------------------------------- #
def test_label_is_read_only_research_label():
    assert rc.get_post_resume_policy_research_continuation_plan_label() == rc.PLAN_LABEL
    assert "READ-ONLY" in rc.PLAN_LABEL
    assert rc.PLAN_MODE == "RESEARCH_ONLY"


def test_label_and_action_carry_no_execution_or_promotion_verbs():
    for text in (rc.PLAN_LABEL.upper(), rc.NEXT_REQUIRED_ACTION.upper()):
        for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE", "EXECUTION",
                       "BACKTEST", "BASELINE", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                       "AUTOMATION", "ORDER", "TRACK"):
            assert banned not in text, banned


# --------------------------------------------------------------------------- #
# no network / credential imports
# --------------------------------------------------------------------------- #
def test_module_imports_no_network_or_credential_modules():
    with open(rc.__file__, "r", encoding="utf-8") as fh:
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
