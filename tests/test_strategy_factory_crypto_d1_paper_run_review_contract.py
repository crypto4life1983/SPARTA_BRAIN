"""Tests for the Crypto-D1 V2 Simulated Paper-Run Review / Micro-Live Decision Contract
(READ-ONLY). Every paper-run report consumed here is a FAKE in-memory JSON (or one
written under tmp_path); no network, no credentials, no real data, no broker, no
exchange, no real order, no paper run, no gate is unlocked."""

from __future__ import annotations

import ast
import json

import sparta_commander.strategy_factory_crypto_d1_paper_run_review_contract as rv
import sparta_commander.strategy_factory_crypto_d1_paper_trading_run_simulated as pr


def _paper_report(*, halted, triggered, max_dd=-0.3226, sharpe=0.53,
                  total_return=0.6089, sim_trades=83, real_orders=0, complete=True,
                  gate_override=None):
    events = []
    if triggered:
        events = [{"date": "2021-05-19", "reason": "daily_loss_halt",
                   "drawdown": -0.18, "daily_return": -0.16, "equity_at_halt": 16089.12}]
    rep = {
        "schema_version": pr.PAPER_RUN_SCHEMA_VERSION,
        "verdict": pr.VERDICT_PAPER_RUN_COMPLETE if complete else pr.VERDICT_BLOCKED_NOT_READY,
        "selected_variant_id": "V2_trend_plus_cash_regime",
        "performance": {
            "starting_equity": 10000.0, "final_equity": 16089.12,
            "total_return": total_return, "max_drawdown": max_dd,
            "sharpe_ratio": sharpe, "annualized_volatility": 0.40,
            "trading_days": 2128,
        },
        "trade_summary": {"simulated_trades": sim_trades,
                          "total_simulated_costs": 95.52, "real_orders_placed": real_orders},
        "kill_switch_triggered": triggered,
        "kill_switch_events": events,
        "halted_at_end": halted,
        # safety posture (mirrors the runner's _base_report)
        "uses_real_money": False, "connects_broker": False, "connects_exchange": False,
        "executes_real_orders": False, "simulated_orders_only": True,
        "uses_network": False, "uses_credentials": False,
        "ran_optimization": False, "ran_parameter_search": False,
        "used_lookahead": False, "used_leverage": False, "used_shorting": False,
        "used_margin": False, "unlocks_downstream_gate": False,
        "authorizes_live_trading": False,
        "paper_trading_gate_locked": True, "micro_live_gate_locked": True,
        "live_gate_locked": True,
    }
    if gate_override:
        rep.update(gate_override)
    return rep


# --------------------------------------------------------------------------- #
# the real outcome -> DO NOT PROMOTE (run valid, kill acceptable, needs more evidence)
# --------------------------------------------------------------------------- #
def test_real_halted_run_does_not_promote():
    d = rv.review_paper_run_report(_paper_report(halted=True, triggered=True))
    assert d["verdict"] == rv.VERDICT_REVIEW_COMPLETE
    assert d["simulated_run_valid"] is True
    assert d["kill_switch_behavior_acceptable"] is True
    assert d["micro_live_decision"] == rv.DO_NOT_PROMOTE_TO_MICRO_LIVE_YET
    assert d["approved_for_micro_live"] is False
    assert d["more_simulated_paper_testing_needed"] is True
    assert "run_halted_pending_human_resume" in d["blockers"]
    assert "kill_switch_triggered_needs_resume_policy_review" in d["blockers"]
    assert "insufficient_regime_evidence_for_micro_live" in d["blockers"]
    assert d["next_required_action"] == "RUN_MORE_SIMULATED_PAPER_EVIDENCE_AND_REVIEW_RESUME_POLICY"


def test_review_unlocks_nothing():
    d = rv.review_paper_run_report(_paper_report(halted=True, triggered=True))
    assert d["paper_trading_gate_locked"] is True
    assert d["micro_live_gate_locked"] is True
    assert d["live_gate_locked"] is True
    assert d["authorizes_micro_live"] is False
    assert d["authorizes_live_trading"] is False
    assert d["promotes_gate"] is False
    assert d["unlocks_downstream_gate"] is False
    assert d["uses_real_money"] is False


# --------------------------------------------------------------------------- #
# even a clean run is not promotable from a single simulated regime
# --------------------------------------------------------------------------- #
def test_clean_run_blocked_by_single_regime():
    d = rv.review_paper_run_report(_paper_report(halted=False, triggered=False))
    assert d["kill_switch_behavior_acceptable"] is True
    assert d["micro_live_decision"] == rv.DO_NOT_PROMOTE_TO_MICRO_LIVE_YET
    assert "insufficient_regime_evidence_for_micro_live" in d["blockers"]
    assert "run_halted_pending_human_resume" not in d["blockers"]
    assert "single_market_regime_sample" in d["risk_notes"]


# --------------------------------------------------------------------------- #
# kill switch behavior assessment
# --------------------------------------------------------------------------- #
def test_kill_triggered_but_not_halted_is_unacceptable():
    d = rv.review_paper_run_report(_paper_report(halted=False, triggered=True))
    assert d["kill_switch_behavior_acceptable"] is False
    assert any(n.startswith("kill_event:") for n in d["risk_notes"])
    assert "kill_triggered_but_not_halted" in d["risk_notes"]


# --------------------------------------------------------------------------- #
# invalid / missing input
# --------------------------------------------------------------------------- #
def test_invalid_safety_posture_blocks():
    bad = _paper_report(halted=True, triggered=True, gate_override={"micro_live_gate_locked": False})
    d = rv.review_paper_run_report(bad)
    assert d["simulated_run_valid"] is False
    assert "paper_run_safety_invalid" in d["blockers"]
    assert d["verdict"] == rv.VERDICT_REVIEW_BLOCKED
    assert d["micro_live_decision"] == rv.DO_NOT_PROMOTE_TO_MICRO_LIVE_YET


def test_real_orders_detected_blocks():
    bad = _paper_report(halted=False, triggered=False, real_orders=2)
    d = rv.review_paper_run_report(bad)
    assert "real_orders_detected" in d["blockers"]


def test_missing_report_blocks():
    d = rv.review_paper_run_report(None)
    assert d["verdict"] == rv.VERDICT_REVIEW_BLOCKED
    assert d["micro_live_decision"] == rv.DO_NOT_PROMOTE_TO_MICRO_LIVE_YET
    assert "paper_run_report_missing" in d["blockers"]


def test_incomplete_run_blocks():
    d = rv.review_paper_run_report(_paper_report(halted=False, triggered=False, complete=False))
    assert "simulated_run_not_complete" in d["blockers"]


# --------------------------------------------------------------------------- #
# disk-backed build
# --------------------------------------------------------------------------- #
def test_build_reads_local_report(tmp_path):
    out = tmp_path / "reports" / "crypto_d1_paper_prep"
    out.mkdir(parents=True, exist_ok=True)
    (out / "paper_run_report.json").write_text(
        json.dumps(_paper_report(halted=True, triggered=True)), encoding="utf-8"
    )
    d = rv.build_paper_run_review_decision(repo_root=str(tmp_path))
    assert d["paper_run_report_found"] is True
    assert d["micro_live_decision"] == rv.DO_NOT_PROMOTE_TO_MICRO_LIVE_YET


def test_build_handles_missing_local_report(tmp_path):
    d = rv.build_paper_run_review_decision(repo_root=str(tmp_path))
    assert d["paper_run_report_found"] is False
    assert "paper_run_report_missing" in d["blockers"]


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #
def test_validate_passes_on_do_not_promote():
    d = rv.review_paper_run_report(_paper_report(halted=True, triggered=True))
    assert rv.validate_paper_run_review_decision(d)["valid"] is True


def test_validate_passes_on_promote_shape():
    # hand-build a hypothetical clean promote decision (no blockers) to exercise the
    # PROMOTE validation branch; the reviewer itself never emits this from one regime.
    d = rv.review_paper_run_report(_paper_report(halted=False, triggered=False))
    d["blockers"] = []
    d["risk_notes"] = []
    d["micro_live_decision"] = rv.PROMOTE_TO_MICRO_LIVE
    d["approved_for_micro_live"] = True
    d["more_simulated_paper_testing_needed"] = False
    assert rv.validate_paper_run_review_decision(d)["valid"] is True


def test_validate_rejects_unlocked_gate():
    d = rv.review_paper_run_report(_paper_report(halted=True, triggered=True))
    d["micro_live_gate_locked"] = False
    v = rv.validate_paper_run_review_decision(d)
    assert v["valid"] is False
    assert any("gate_not_locked:micro_live_gate_locked" in e for e in v["errors"])


def test_validate_rejects_authorizes_micro_live_true():
    d = rv.review_paper_run_report(_paper_report(halted=True, triggered=True))
    d["authorizes_micro_live"] = True
    v = rv.validate_paper_run_review_decision(d)
    assert v["valid"] is False
    assert any("capability_not_false:authorizes_micro_live" in e for e in v["errors"])


def test_validate_rejects_blocked_marked_approved():
    d = rv.review_paper_run_report(_paper_report(halted=True, triggered=True))
    d["approved_for_micro_live"] = True
    v = rv.validate_paper_run_review_decision(d)
    assert v["valid"] is False
    assert any("blocked_decision_marked_approved" in e for e in v["errors"])


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #
def test_render_markdown_is_string():
    md = rv.render_paper_run_review_markdown(
        rv.review_paper_run_report(_paper_report(halted=True, triggered=True))
    )
    assert md.startswith("# Crypto-D1 V2 Simulated Paper-Run Review / Micro-Live Decision")
    assert "DO_NOT_PROMOTE_TO_MICRO_LIVE_YET" in md and "LOCKED" in md
    assert "V2_trend_plus_cash_regime" in md


# --------------------------------------------------------------------------- #
# no network / credential imports
# --------------------------------------------------------------------------- #
def test_module_imports_no_network_or_credential_modules():
    with open(rv.__file__, "r", encoding="utf-8") as fh:
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
