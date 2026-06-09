"""Tests for the Crypto-D1 Risk-Profile Revision Plan (READ-ONLY research plan).
Pure; the disk-backed test uses a FAKE baseline report JSON under tmp_path. No
network, no credentials, no real data, nothing is run."""

from __future__ import annotations

import ast
import json

import sparta_commander.strategy_factory_crypto_d1_risk_profile_revision_plan as rp
import sparta_commander.strategy_factory_crypto_d1_baseline_backtest_review_contract as rv
import sparta_commander.strategy_factory_crypto_d1_baseline_backtest_runner as br


def _blocked_decision():
    return {
        "promotion_decision": rv.DO_NOT_PROMOTE_TO_PAPER_YET,
        "blockers": ["max_drawdown_exceeds_limit"],
        "risk_notes": [
            "buy_and_hold_has_no_risk_management",
            "single_market_regime_sample",
            "return_concentrated_in_SOL",
        ],
        "metrics_reviewed": {
            "max_drawdown": -0.9210792624015145,
            "sharpe_ratio": 0.8954,
            "total_return": 9.0853,
            "trading_days": 2128,
        },
    }


def _promote_decision():
    return {
        "promotion_decision": rv.PROMOTE_TO_PAPER_PREP,
        "blockers": [],
        "risk_notes": [],
        "metrics_reviewed": {"max_drawdown": -0.20},
    }


def _baseline_report():
    return {
        "verdict": br.VERDICT_BASELINE_COMPLETE,
        "performance": {
            "max_drawdown": -0.9210792624015145,
            "sharpe_ratio": 0.8954,
            "total_return": 9.0853,
            "trading_days": 2128,
            "cagr": 0.4871,
        },
        "trade_summary": {"buys": 3, "sells": 0, "rebalances": 0},
        "per_symbol": [
            {"symbol": "BTC", "contribution_to_portfolio": 1.8459},
            {"symbol": "ETH", "contribution_to_portfolio": 1.4868},
            {"symbol": "SOL", "contribution_to_portfolio": 6.7526},
        ],
    }


# --------------------------------------------------------------------------- #
# triggering
# --------------------------------------------------------------------------- #
def test_blocked_decision_requires_revision():
    p = rp.build_revision_plan_from_decision(_blocked_decision())
    assert p["revision_required"] is True
    assert p["trigger"]["blockers"] == ["max_drawdown_exceeds_limit"]
    assert p["next_required_action"] == "HUMAN_APPROVED_RISK_CONTROLLED_VARIANT_BACKTEST_PREP"


def test_promote_decision_needs_no_revision():
    p = rp.build_revision_plan_from_decision(_promote_decision())
    assert p["revision_required"] is False
    assert "baseline_already_eligible_no_revision_required" in p["notes"]


# --------------------------------------------------------------------------- #
# risk controls
# --------------------------------------------------------------------------- #
def test_controls_cover_drawdown_and_concentration():
    p = rp.build_revision_plan_from_decision(_blocked_decision())
    ids = {c["id"] for c in p["risk_controls"]}
    assert {"trend_filter", "cash_regime", "volatility_cap", "stop_risk_off",
            "periodic_rebalance", "sol_concentration_cap"} <= ids


def test_drawdown_blocker_is_addressed_by_some_control():
    p = rp.build_revision_plan_from_decision(_blocked_decision())
    addressed = {t for c in p["risk_controls"] for t in c["targets"]}
    assert "max_drawdown_exceeds_limit" in addressed


def test_sol_concentration_is_addressed():
    p = rp.build_revision_plan_from_decision(_blocked_decision())
    sol = next(c for c in p["risk_controls"] if c["id"] == "sol_concentration_cap")
    assert "return_concentrated_in_SOL" in sol["targets"]


def test_every_control_is_a_fixed_rule_no_optimization():
    p = rp.build_revision_plan_from_decision(_blocked_decision())
    assert all(c["fixed_rule_no_optimization"] is True for c in p["risk_controls"])


def test_success_target_matches_promotion_floor():
    p = rp.build_revision_plan_from_decision(_blocked_decision())
    assert p["success_target"]["target_max_drawdown"] == rv.PROMOTION_CRITERIA["max_acceptable_drawdown"]
    assert p["success_target"]["primary_objective"] == "reduce_max_drawdown_within_promotion_floor"


# --------------------------------------------------------------------------- #
# variants
# --------------------------------------------------------------------------- #
def test_variants_present_and_reference_known_controls():
    p = rp.build_revision_plan_from_decision(_blocked_decision())
    control_ids = {c["id"] for c in p["risk_controls"]}
    variants = p["backtest_variants"]
    assert len(variants) >= 3
    for v in variants:
        assert v["controls"]
        assert set(v["controls"]) <= control_ids


def test_variant_constraints_forbid_optimization_and_leverage():
    c = rp.variant_constraints()
    assert c["optimization"] is False and c["parameter_search"] is False
    assert c["walk_forward"] is False and c["lookahead_allowed"] is False
    assert c["allow_shorting"] is False and c["allow_leverage"] is False
    assert c["long_only"] is True


# --------------------------------------------------------------------------- #
# disk-backed build
# --------------------------------------------------------------------------- #
def test_build_from_local_review(tmp_path):
    rep_dir = tmp_path / "reports" / "crypto_d1_baseline_backtest"
    rep_dir.mkdir(parents=True, exist_ok=True)
    (rep_dir / "baseline_backtest_report.json").write_text(
        json.dumps(_baseline_report()), encoding="utf-8"
    )
    p = rp.build_risk_profile_revision_plan(repo_root=str(tmp_path))
    assert p["revision_required"] is True
    assert p["source_review"]["baseline_report_found"] is True
    assert p["source_review"]["promotion_decision"] == rv.DO_NOT_PROMOTE_TO_PAPER_YET


def test_build_handles_missing_local_report(tmp_path):
    p = rp.build_risk_profile_revision_plan(repo_root=str(tmp_path))
    # no baseline report => review blocks => revision still required
    assert p["revision_required"] is True
    assert p["source_review"]["baseline_report_found"] is False


# --------------------------------------------------------------------------- #
# safety posture
# --------------------------------------------------------------------------- #
def test_plan_unlocks_no_gate():
    p = rp.build_revision_plan_from_decision(_blocked_decision())
    assert p["baseline_backtest_blocked"] is True
    assert p["paper_trading_gate_locked"] is True
    assert p["micro_live_gate_locked"] is True
    assert p["executes"] is False
    assert p["runs_backtest"] is False
    assert p["runs_optimization"] is False
    assert p["runs_parameter_search"] is False
    assert p["authorizes_variant_run"] is False
    assert p["authorizes_paper_trading"] is False
    assert p["unlocks_downstream_gate"] is False


def test_validate_passes():
    p = rp.build_revision_plan_from_decision(_blocked_decision())
    v = rp.validate_risk_profile_revision_plan(p)
    assert v["valid"] is True and v["errors"] == []


def test_validate_rejects_unlocked_gate():
    p = rp.build_revision_plan_from_decision(_blocked_decision())
    p["paper_trading_gate_locked"] = False
    v = rp.validate_risk_profile_revision_plan(p)
    assert v["valid"] is False
    assert any("gate_not_locked" in e for e in v["errors"])


def test_validate_rejects_optimization_constraint():
    p = rp.build_revision_plan_from_decision(_blocked_decision())
    p["variant_constraints"]["optimization"] = True
    v = rp.validate_risk_profile_revision_plan(p)
    assert v["valid"] is False
    assert any("constraint_not_false:optimization" in e for e in v["errors"])


def test_render_markdown_is_string():
    p = rp.build_revision_plan_from_decision(_blocked_decision())
    md = rp.render_risk_profile_revision_markdown(p)
    assert md.startswith("# Crypto-D1 Risk-Profile Revision Plan")
    assert "LOCKED" in md and "sol_concentration_cap" in md


def test_module_imports_no_network_or_credential_modules():
    with open(rp.__file__, "r", encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    banned = {
        "urllib",
        "requests",
        "socket",
        "http",
        "ftplib",
        "ccxt",
        "databento",
        "dotenv",
        "smtplib",
    }
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imported.add(n.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert not (imported & banned)
