"""Tests for the Crypto-D1 V2 Resume-Policy Results Review / Decision Contract (READ-ONLY).

Every report consumed here is a FAKE in-memory JSON (or one written under tmp_path); no
network, no credentials, no real data, no broker, no exchange, no real order, no simulation,
no gate is unlocked. The contract treats resume-policy results as research evidence only and
never promotes a policy to execution."""

from __future__ import annotations

import ast
import json

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
    # Build the safety skeleton from the runner so validate_resume_policy_simulation_report passes.
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


# --------------------------------------------------------------------------- #
# the real outcome -> DO NOT PROMOTE, RP6 leads
# --------------------------------------------------------------------------- #
def test_complete_results_do_not_promote_and_rp6_leads():
    d = rr.review_resume_policy_results(_sim_report())
    assert d["verdict"] == rr.VERDICT_REVIEW_COMPLETE
    assert d["results_valid"] is True
    assert d["promotion_decision"] == rr.DO_NOT_PROMOTE_RESUME_POLICY_YET
    assert d["approved_for_execution"] is False
    assert d["human_review_required"] is True
    assert d["evidence_leading_policy"]["policy_id"] == "RP6_resume_after_volatility_cools"
    assert d["evidence_leading_policy"]["leads_all_categories"] is True
    assert "execution_promotion_requires_separate_human_review" in d["blockers"]
    assert d["next_required_action"] == "HUMAN_REVIEW_OF_RESUME_POLICY_SIMULATION_RESULTS"


def test_review_unlocks_nothing():
    d = rr.review_resume_policy_results(_sim_report())
    assert d["paper_trading_gate_locked"] is True
    assert d["micro_live_gate_locked"] is True
    assert d["live_gate_locked"] is True
    assert d["authorizes_paper_execution"] is False
    assert d["authorizes_micro_live"] is False
    assert d["authorizes_live_trading"] is False
    assert d["promotes_gate"] is False
    assert d["unlocks_downstream_gate"] is False
    assert d["uses_real_money"] is False
    assert d["runs_simulation"] is False


def test_leading_policy_summarized_in_risk_notes():
    d = rr.review_resume_policy_results(_sim_report())
    assert "evidence_leading_policy:RP6_resume_after_volatility_cools" in d["risk_notes"]
    assert "human_review_required_before_any_execution_promotion" in d["risk_notes"]
    assert len(d["policy_summaries"]) == 2


# --------------------------------------------------------------------------- #
# invalid / missing input
# --------------------------------------------------------------------------- #
def test_missing_report_blocks():
    d = rr.review_resume_policy_results(None)
    assert d["verdict"] == rr.VERDICT_REVIEW_BLOCKED
    assert d["promotion_decision"] == rr.DO_NOT_PROMOTE_RESUME_POLICY_YET
    assert "resume_policy_sim_report_missing" in d["blockers"]


def test_incomplete_run_blocks():
    d = rr.review_resume_policy_results(_sim_report(complete=False))
    assert d["verdict"] == rr.VERDICT_REVIEW_BLOCKED
    assert "resume_policy_sim_not_complete" in d["blockers"]


def test_invalid_safety_posture_blocks():
    d = rr.review_resume_policy_results(_sim_report(override={"micro_live_gate_locked": False}))
    assert d["results_valid"] is False
    assert "resume_policy_sim_safety_invalid" in d["blockers"]
    assert d["verdict"] == rr.VERDICT_REVIEW_BLOCKED


def test_real_orders_detected_blocks():
    d = rr.review_resume_policy_results(_sim_report(real_orders=2))
    assert any(b.startswith("real_orders_detected:") for b in d["blockers"])


# --------------------------------------------------------------------------- #
# advisory risk-note thresholds
# --------------------------------------------------------------------------- #
def test_leading_policy_breaching_drawdown_flags_risk_note():
    rep = _sim_report(rankings_leader="RP1_wait_7d_trend_on")  # RP1 worst_dd -0.61 < -0.50
    d = rr.review_resume_policy_results(rep)
    assert d["evidence_leading_policy"]["policy_id"] == "RP1_wait_7d_trend_on"
    assert "leading_policy_worst_drawdown_breaches_hard_kill" in d["risk_notes"]
    assert "leading_policy_mean_sharpe_below_advisory_minimum" in d["risk_notes"]


# --------------------------------------------------------------------------- #
# disk-backed build
# --------------------------------------------------------------------------- #
def test_build_reads_local_report(tmp_path):
    out = tmp_path / "reports" / "crypto_d1_resume_policy_sim"
    out.mkdir(parents=True, exist_ok=True)
    (out / "resume_policy_sim_report.json").write_text(json.dumps(_sim_report()), encoding="utf-8")
    d = rr.build_resume_policy_results_review_decision(repo_root=str(tmp_path))
    assert d["resume_policy_sim_report_found"] is True
    assert d["promotion_decision"] == rr.DO_NOT_PROMOTE_RESUME_POLICY_YET


def test_build_handles_missing_local_report(tmp_path):
    d = rr.build_resume_policy_results_review_decision(repo_root=str(tmp_path))
    assert d["resume_policy_sim_report_found"] is False
    assert "resume_policy_sim_report_missing" in d["blockers"]


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #
def test_validate_passes_on_do_not_promote():
    d = rr.review_resume_policy_results(_sim_report())
    assert rr.validate_resume_policy_results_review_decision(d)["valid"] is True


def test_validate_passes_on_promote_shape():
    # Hand-build a hypothetical clean promote decision to exercise the PROMOTE branch; the
    # reviewer itself never emits this (it always carries the structural blocker).
    d = rr.review_resume_policy_results(_sim_report())
    d["blockers"] = []
    d["risk_notes"] = []
    d["promotion_decision"] = rr.PROMOTE_RESUME_POLICY_FOR_EXECUTION
    d["approved_for_execution"] = True
    d["human_review_required"] = False
    assert rr.validate_resume_policy_results_review_decision(d)["valid"] is True


def test_validate_rejects_unlocked_gate():
    d = rr.review_resume_policy_results(_sim_report())
    d["micro_live_gate_locked"] = False
    v = rr.validate_resume_policy_results_review_decision(d)
    assert v["valid"] is False
    assert any("gate_not_locked:micro_live_gate_locked" in e for e in v["errors"])


def test_validate_rejects_authorizes_execution_true():
    d = rr.review_resume_policy_results(_sim_report())
    d["authorizes_paper_execution"] = True
    v = rr.validate_resume_policy_results_review_decision(d)
    assert v["valid"] is False
    assert any("capability_not_false:authorizes_paper_execution" in e for e in v["errors"])


def test_validate_rejects_blocked_marked_approved():
    d = rr.review_resume_policy_results(_sim_report())
    d["approved_for_execution"] = True
    v = rr.validate_resume_policy_results_review_decision(d)
    assert v["valid"] is False
    assert any("blocked_decision_marked_approved" in e for e in v["errors"])


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #
def test_render_markdown_is_string():
    md = rr.render_resume_policy_results_review_markdown(rr.review_resume_policy_results(_sim_report()))
    assert md.startswith("# Crypto-D1 V2 Resume-Policy Results Review / Decision")
    assert "DO_NOT_PROMOTE_RESUME_POLICY_YET" in md and "LOCKED" in md
    assert "RP6_resume_after_volatility_cools" in md


# --------------------------------------------------------------------------- #
# no network / credential imports
# --------------------------------------------------------------------------- #
def test_module_imports_no_network_or_credential_modules():
    with open(rr.__file__, "r", encoding="utf-8") as fh:
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
