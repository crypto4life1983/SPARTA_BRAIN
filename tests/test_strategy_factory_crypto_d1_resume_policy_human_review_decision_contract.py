"""Tests for the Crypto-D1 V2 Resume-Policy HUMAN REVIEW Decision Contract (READ-ONLY).

Every decision consumed here is a FAKE in-memory dict (or one derived under tmp_path); no
network, no credentials, no real data, no broker, no exchange, no real order, no simulation,
no file write, no gate is unlocked. The contract records a human's review of resume-policy
results as research evidence only and never promotes a policy to execution."""

from __future__ import annotations

import ast
import json

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
    """A valid Block 177 reviewer decision derived from a fake sim report."""
    d = rr.review_resume_policy_results(_sim_report(**kwargs))
    d["resume_policy_sim_report_found"] = True
    d["resume_policy_sim_report_path"] = "reports/crypto_d1_resume_policy_sim/resume_policy_sim_report.json"
    return d


# --------------------------------------------------------------------------- #
# the real outcome -> RECORDED, DO NOT PROMOTE, RP6 acknowledged
# --------------------------------------------------------------------------- #
def test_records_human_review_do_not_promote_and_acknowledges_rp6():
    d = hr.record_human_review_decision(_review_decision())
    assert d["verdict"] == hr.VERDICT_HUMAN_REVIEW_RECORDED
    assert d["human_decision"] == hr.DECISION_DO_NOT_PROMOTE
    assert d["approved_for_execution"] is False
    assert d["human_review_required"] is True
    assert d["recommended_path"] == hr.RECOMMEND_SEPARATE_EXPLICIT_APPROVAL
    assert d["evidence_leading_policy"]["policy_id"] == "RP6_resume_after_volatility_cools"
    assert d["evidence_leading_policy"]["leads_all_categories"] is True
    assert "acknowledged_evidence_leading_policy:RP6_resume_after_volatility_cools" in d["risk_notes"]
    assert "evidence_leading_policy_leads_all_categories" in d["risk_notes"]
    assert "promotion_requires_separate_explicit_human_command" in d["risk_notes"]
    assert d["next_required_action"] == "CONTINUE_RESEARCH_OR_REQUEST_SEPARATE_HUMAN_APPROVAL"


def test_review_unlocks_nothing():
    d = hr.record_human_review_decision(_review_decision())
    assert d["paper_trading_gate_locked"] is True
    assert d["micro_live_gate_locked"] is True
    assert d["live_gate_locked"] is True
    assert d["authorizes_paper_execution"] is False
    assert d["authorizes_micro_live"] is False
    assert d["authorizes_live_trading"] is False
    assert d["promotes_gate"] is False
    assert d["promotes_resume_policy"] is False
    assert d["unlocks_downstream_gate"] is False
    assert d["uses_real_money"] is False
    assert d["runs_simulation"] is False
    assert d["writes_files"] is False
    assert d["executes"] is False


def test_carries_forward_review_blockers_and_notes():
    rd = _review_decision()
    d = hr.record_human_review_decision(rd)
    # Block 177 always carries the structural promotion blocker; it is preserved here.
    assert "execution_promotion_requires_separate_human_review" in d["review_blockers"]
    assert any(n.startswith("review_note:") for n in d["risk_notes"])


# --------------------------------------------------------------------------- #
# recommended path handling
# --------------------------------------------------------------------------- #
def test_each_recommended_path_is_accepted():
    for path in hr.RECOMMENDED_PATHS:
        d = hr.record_human_review_decision(_review_decision(), recommended_path=path)
        assert d["verdict"] == hr.VERDICT_HUMAN_REVIEW_RECORDED
        assert d["recommended_path"] == path


def test_invalid_recommended_path_blocks():
    d = hr.record_human_review_decision(_review_decision(), recommended_path="PROMOTE_NOW")
    assert d["verdict"] == hr.VERDICT_HUMAN_REVIEW_BLOCKED
    assert any(b.startswith("invalid_recommended_path:") for b in d["blockers"])
    assert d["recommended_path"] is None
    # even a bad request keeps the decision DO_NOT_PROMOTE and gates locked
    assert d["human_decision"] == hr.DECISION_DO_NOT_PROMOTE
    assert d["approved_for_execution"] is False


# --------------------------------------------------------------------------- #
# invalid / missing upstream input
# --------------------------------------------------------------------------- #
def test_missing_review_decision_blocks():
    d = hr.record_human_review_decision(None)
    assert d["verdict"] == hr.VERDICT_HUMAN_REVIEW_BLOCKED
    assert d["human_decision"] == hr.DECISION_DO_NOT_PROMOTE
    assert "results_review_decision_missing" in d["blockers"]


def test_incomplete_review_blocks():
    rd = _review_decision(complete=False)
    d = hr.record_human_review_decision(rd)
    assert d["verdict"] == hr.VERDICT_HUMAN_REVIEW_BLOCKED
    assert "results_review_not_complete" in d["blockers"]


def test_report_not_found_blocks():
    rd = _review_decision()
    rd["resume_policy_sim_report_found"] = False
    d = hr.record_human_review_decision(rd)
    assert d["verdict"] == hr.VERDICT_HUMAN_REVIEW_BLOCKED
    assert "resume_policy_sim_report_missing" in d["blockers"]


def test_invalid_review_decision_blocks():
    rd = _review_decision()
    rd["micro_live_gate_locked"] = False  # breaks Block 177's own validator
    d = hr.record_human_review_decision(rd)
    assert d["verdict"] == hr.VERDICT_HUMAN_REVIEW_BLOCKED
    assert "results_review_decision_invalid" in d["blockers"]


def test_leading_policy_not_leading_all_categories_is_noted():
    rd = _review_decision()
    rd["evidence_leading_policy"]["leads_all_categories"] = False
    d = hr.record_human_review_decision(rd)
    assert "evidence_leading_policy_does_not_lead_all_categories" in d["risk_notes"]


# --------------------------------------------------------------------------- #
# disk-backed build
# --------------------------------------------------------------------------- #
def test_build_reads_local_report(tmp_path):
    out = tmp_path / "reports" / "crypto_d1_resume_policy_sim"
    out.mkdir(parents=True, exist_ok=True)
    (out / "resume_policy_sim_report.json").write_text(json.dumps(_sim_report()), encoding="utf-8")
    d = hr.build_resume_policy_human_review_decision(repo_root=str(tmp_path))
    assert d["resume_policy_sim_report_found"] is True
    assert d["verdict"] == hr.VERDICT_HUMAN_REVIEW_RECORDED
    assert d["human_decision"] == hr.DECISION_DO_NOT_PROMOTE
    assert d["results_review_verdict"] == rr.VERDICT_REVIEW_COMPLETE


def test_build_handles_missing_local_report(tmp_path):
    d = hr.build_resume_policy_human_review_decision(repo_root=str(tmp_path))
    assert d["resume_policy_sim_report_found"] is False
    assert d["verdict"] == hr.VERDICT_HUMAN_REVIEW_BLOCKED
    assert "resume_policy_sim_report_missing" in d["blockers"]


# --------------------------------------------------------------------------- #
# separate-approval-path metadata is inert
# --------------------------------------------------------------------------- #
def test_separate_approval_path_is_inert():
    sap = hr.separate_approval_path()
    assert sap["is_authorization"] is False
    assert sap["unlocks_any_gate"] is False
    assert isinstance(sap["required_future_steps"], list) and sap["required_future_steps"]
    # mutating the returned copy must not affect the module constant
    sap["required_future_steps"].append("tampered")
    assert "tampered" not in hr.SEPARATE_APPROVAL_PATH["required_future_steps"]


def test_decision_embeds_inert_separate_approval_path():
    d = hr.record_human_review_decision(_review_decision())
    sap = d["separate_approval_path"]
    assert sap["is_authorization"] is False
    assert sap["unlocks_any_gate"] is False


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #
def test_validate_passes_on_recorded():
    d = hr.record_human_review_decision(_review_decision())
    assert hr.validate_resume_policy_human_review_decision(d)["valid"] is True


def test_validate_passes_on_blocked():
    d = hr.record_human_review_decision(None)
    assert hr.validate_resume_policy_human_review_decision(d)["valid"] is True


def test_validate_rejects_unlocked_gate():
    d = hr.record_human_review_decision(_review_decision())
    d["micro_live_gate_locked"] = False
    v = hr.validate_resume_policy_human_review_decision(d)
    assert v["valid"] is False
    assert any("gate_not_locked:micro_live_gate_locked" in e for e in v["errors"])


def test_validate_rejects_authorizes_execution_true():
    d = hr.record_human_review_decision(_review_decision())
    d["authorizes_paper_execution"] = True
    v = hr.validate_resume_policy_human_review_decision(d)
    assert v["valid"] is False
    assert any("capability_not_false:authorizes_paper_execution" in e for e in v["errors"])


def test_validate_rejects_marked_approved():
    d = hr.record_human_review_decision(_review_decision())
    d["approved_for_execution"] = True
    v = hr.validate_resume_policy_human_review_decision(d)
    assert v["valid"] is False
    assert any("decision_marked_approved" in e for e in v["errors"])


def test_validate_rejects_promote_decision():
    d = hr.record_human_review_decision(_review_decision())
    d["human_decision"] = "PROMOTE_RESUME_POLICY_FOR_EXECUTION"
    v = hr.validate_resume_policy_human_review_decision(d)
    assert v["valid"] is False
    assert any("human_decision_not_do_not_promote" in e for e in v["errors"])


def test_validate_rejects_authorizing_separate_path():
    d = hr.record_human_review_decision(_review_decision())
    d["separate_approval_path"]["is_authorization"] = True
    v = hr.validate_resume_policy_human_review_decision(d)
    assert v["valid"] is False
    assert any("separate_approval_path_claims_authorization" in e for e in v["errors"])


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #
def test_render_markdown_is_string():
    md = hr.render_resume_policy_human_review_decision_markdown(
        hr.record_human_review_decision(_review_decision())
    )
    assert md.startswith("# Crypto-D1 V2 Resume-Policy Human Review Decision")
    assert "DO_NOT_PROMOTE_RESUME_POLICY_YET" in md and "LOCKED" in md
    assert "RP6_resume_after_volatility_cools" in md
    assert "authorizes nothing" in md


# --------------------------------------------------------------------------- #
# label
# --------------------------------------------------------------------------- #
def test_label_is_read_only_research_label():
    assert hr.get_resume_policy_human_review_decision_label() == hr.HUMAN_REVIEW_LABEL
    assert "READ-ONLY" in hr.HUMAN_REVIEW_LABEL
    assert hr.HUMAN_REVIEW_MODE == "RESEARCH_ONLY"


# --------------------------------------------------------------------------- #
# no network / credential imports
# --------------------------------------------------------------------------- #
def test_module_imports_no_network_or_credential_modules():
    with open(hr.__file__, "r", encoding="utf-8") as fh:
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
