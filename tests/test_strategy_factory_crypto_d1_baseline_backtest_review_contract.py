"""Tests for the Crypto-D1 Baseline Backtest Review / Promotion Decision Contract
(READ-ONLY). The baseline report used by the disk-backed tests is a FAKE in-memory
JSON under tmp_path; no network, no credentials, no real data, nothing is run."""

from __future__ import annotations

import ast
import json

import sparta_commander.strategy_factory_crypto_d1_baseline_backtest_review_contract as rv
import sparta_commander.strategy_factory_crypto_d1_baseline_backtest_runner as br


def _report(*, max_drawdown, sharpe=1.5, total_return=2.0, trading_days=2000,
            verdict=br.VERDICT_BASELINE_COMPLETE):
    return {
        "verdict": verdict,
        "performance": {
            "max_drawdown": max_drawdown,
            "sharpe_ratio": sharpe,
            "total_return": total_return,
            "trading_days": trading_days,
            "cagr": 0.30,
        },
        "trade_summary": {"sells": 0, "rebalances": 0},
        "per_symbol": [
            {"symbol": "BTC", "contribution_to_portfolio": 1.0},
            {"symbol": "ETH", "contribution_to_portfolio": 1.0},
            {"symbol": "SOL", "contribution_to_portfolio": 1.0},
        ],
    }


def _actual_baseline_report():
    """Mirrors the real completed local baseline (drawdown -92.11%)."""
    return {
        "verdict": br.VERDICT_BASELINE_COMPLETE,
        "performance": {
            "max_drawdown": -0.9210792624015145,
            "sharpe_ratio": 0.8954024052845803,
            "total_return": 9.085264896464968,
            "trading_days": 2128,
            "cagr": 0.4871470740200221,
        },
        "trade_summary": {"buys": 3, "sells": 0, "rebalances": 0},
        "per_symbol": [
            {"symbol": "BTC", "contribution_to_portfolio": 1.8459},
            {"symbol": "ETH", "contribution_to_portfolio": 1.4868},
            {"symbol": "SOL", "contribution_to_portfolio": 6.7526},
        ],
    }


# --------------------------------------------------------------------------- #
# the actual baseline -> DO NOT PROMOTE (drawdown too large)
# --------------------------------------------------------------------------- #
def test_actual_baseline_is_not_promoted_due_to_drawdown():
    d = rv.review_baseline_report(_actual_baseline_report())
    assert d["promotion_decision"] == rv.DO_NOT_PROMOTE_TO_PAPER_YET
    assert d["eligible_for_paper_prep"] is False
    assert "max_drawdown_exceeds_limit" in d["blockers"]
    # sharpe 0.90 clears the 0.50 floor, so drawdown is the dominant blocker
    assert "sharpe_below_minimum" not in d["blockers"]
    assert d["next_required_action"] == "REVISE_BASELINE_RISK_PROFILE_BEFORE_PAPER_PREP"


def test_actual_baseline_flags_concentration_in_sol():
    d = rv.review_baseline_report(_actual_baseline_report())
    assert "return_concentrated_in_SOL" in d["risk_notes"]
    assert "buy_and_hold_has_no_risk_management" in d["risk_notes"]


# --------------------------------------------------------------------------- #
# threshold behavior
# --------------------------------------------------------------------------- #
def test_shallow_drawdown_can_promote():
    d = rv.review_baseline_report(_report(max_drawdown=-0.25))
    assert d["promotion_decision"] == rv.PROMOTE_TO_PAPER_PREP
    assert d["eligible_for_paper_prep"] is True
    assert d["blockers"] == []
    assert d["next_required_action"] == "HUMAN_APPROVED_PAPER_TRADING_PREP_GATE"


def test_drawdown_exactly_at_limit_is_ok():
    d = rv.review_baseline_report(_report(max_drawdown=-0.50))
    assert "max_drawdown_exceeds_limit" not in d["blockers"]


def test_low_sharpe_blocks():
    d = rv.review_baseline_report(_report(max_drawdown=-0.10, sharpe=0.10))
    assert "sharpe_below_minimum" in d["blockers"]
    assert d["promotion_decision"] == rv.DO_NOT_PROMOTE_TO_PAPER_YET


def test_negative_return_blocks():
    d = rv.review_baseline_report(_report(max_drawdown=-0.10, total_return=-0.20))
    assert "total_return_below_minimum" in d["blockers"]


def test_short_coverage_blocks():
    d = rv.review_baseline_report(_report(max_drawdown=-0.10, trading_days=100))
    assert "coverage_below_minimum" in d["blockers"]


def test_incomplete_baseline_blocks():
    d = rv.review_baseline_report(_report(max_drawdown=-0.10, verdict="BLOCKED_NOT_READY"))
    assert "baseline_not_complete" in d["blockers"]


# --------------------------------------------------------------------------- #
# missing / malformed input
# --------------------------------------------------------------------------- #
def test_missing_report_is_blocked():
    d = rv.review_baseline_report(None)
    assert d["verdict"] == rv.VERDICT_REVIEW_BLOCKED
    assert d["promotion_decision"] == rv.DO_NOT_PROMOTE_TO_PAPER_YET
    assert "baseline_report_missing" in d["blockers"]


def test_missing_performance_is_blocked():
    d = rv.review_baseline_report({"verdict": br.VERDICT_BASELINE_COMPLETE})
    assert "performance_missing" in d["blockers"]


# --------------------------------------------------------------------------- #
# disk-backed build
# --------------------------------------------------------------------------- #
def test_build_reads_local_report(tmp_path):
    rep_dir = tmp_path / "reports" / "crypto_d1_baseline_backtest"
    rep_dir.mkdir(parents=True, exist_ok=True)
    (rep_dir / "baseline_backtest_report.json").write_text(
        json.dumps(_actual_baseline_report()), encoding="utf-8"
    )
    d = rv.build_baseline_review_decision(repo_root=str(tmp_path))
    assert d["baseline_report_found"] is True
    assert d["promotion_decision"] == rv.DO_NOT_PROMOTE_TO_PAPER_YET


def test_build_handles_missing_local_report(tmp_path):
    d = rv.build_baseline_review_decision(repo_root=str(tmp_path))
    assert d["baseline_report_found"] is False
    assert "baseline_report_missing" in d["blockers"]


# --------------------------------------------------------------------------- #
# safety posture
# --------------------------------------------------------------------------- #
def test_decision_unlocks_no_gate():
    d = rv.review_baseline_report(_actual_baseline_report())
    assert d["baseline_backtest_blocked"] is True
    assert d["paper_trading_gate_locked"] is True
    assert d["micro_live_gate_locked"] is True
    assert d["executes"] is False
    assert d["authorizes_paper_trading"] is False
    assert d["authorizes_live_trading"] is False
    assert d["promotes_gate"] is False
    assert d["unlocks_downstream_gate"] is False


def test_even_a_promote_decision_keeps_gates_locked():
    d = rv.review_baseline_report(_report(max_drawdown=-0.10))
    assert d["promotion_decision"] == rv.PROMOTE_TO_PAPER_PREP
    # eligible recommendation, but the gate itself is NOT unlocked by this contract
    assert d["paper_trading_gate_locked"] is True
    assert d["micro_live_gate_locked"] is True
    assert d["promotes_gate"] is False


def test_validate_passes_on_blocked_and_promote():
    blocked = rv.review_baseline_report(_actual_baseline_report())
    promote = rv.review_baseline_report(_report(max_drawdown=-0.10))
    assert rv.validate_baseline_review_decision(blocked)["valid"] is True
    assert rv.validate_baseline_review_decision(promote)["valid"] is True


def test_validate_rejects_unlocked_gate():
    d = rv.review_baseline_report(_actual_baseline_report())
    d["paper_trading_gate_locked"] = False
    v = rv.validate_baseline_review_decision(d)
    assert v["valid"] is False
    assert any("gate_not_locked" in e for e in v["errors"])


def test_validate_rejects_blocked_marked_eligible():
    d = rv.review_baseline_report(_actual_baseline_report())
    d["eligible_for_paper_prep"] = True
    v = rv.validate_baseline_review_decision(d)
    assert v["valid"] is False
    assert any("blocked_decision_marked_eligible" in e or "eligible_with_blockers" in e
               for e in v["errors"])


def test_render_markdown_is_string():
    md = rv.render_baseline_review_markdown(rv.review_baseline_report(_actual_baseline_report()))
    assert md.startswith("# Crypto-D1 Baseline Backtest Review")
    assert "DO_NOT_PROMOTE_TO_PAPER_YET" in md and "LOCKED" in md


def test_module_imports_no_network_or_credential_modules():
    with open(rv.__file__, "r", encoding="utf-8") as fh:
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
