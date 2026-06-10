"""Tests for the Crypto-D1 Variant Backtest Review / Paper-Prep Decision Contract
(READ-ONLY). The variant report used by the disk-backed test is a FAKE in-memory JSON
under tmp_path; no network, no credentials, no real data, nothing is run, no gate is
unlocked."""

from __future__ import annotations

import ast
import json

import sparta_commander.strategy_factory_crypto_d1_variant_backtest_review_contract as rv
import sparta_commander.strategy_factory_crypto_d1_variant_backtest_runner as vr


def _variant(vid, *, max_dd, sharpe=1.10, total_return=2.0, trading_days=2128,
             eligible, blockers=None, beats_floor=None):
    if beats_floor is None:
        beats_floor = max_dd >= -0.50
    return {
        "variant_id": vid,
        "description": vid,
        "controls": ["trend_filter"],
        "performance": {
            "max_drawdown": max_dd,
            "sharpe_ratio": sharpe,
            "total_return": total_return,
            "trading_days": trading_days,
            "cagr": 0.50,
        },
        "beats_drawdown_floor": beats_floor,
        "promotion_decision": "PROMOTE_TO_PAPER_PREP" if eligible else "DO_NOT_PROMOTE_TO_PAPER_YET",
        "eligible_for_paper_prep": eligible,
        "eligibility_blockers": list(blockers or []),
    }


def _report_v2_eligible():
    """Mirrors the real run: only V2 clears the floor and is paper-prep eligible."""
    return {
        "verdict": vr.VERDICT_VARIANTS_COMPLETE,
        "variant_count": 5,
        "variant_results": [
            _variant("V1_trend_filter", max_dd=-0.5349, sharpe=0.92,
                     eligible=False, blockers=["max_drawdown_exceeds_limit"]),
            _variant("V2_trend_plus_cash_regime", max_dd=-0.4816, sharpe=1.10,
                     total_return=11.5528, eligible=True),
            _variant("V3_voltarget_concentration_cap", max_dd=-0.8512, sharpe=0.99,
                     eligible=False, blockers=["max_drawdown_exceeds_limit"]),
            _variant("V4_monthly_rebalance_capped", max_dd=-0.8438, sharpe=1.04,
                     eligible=False, blockers=["max_drawdown_exceeds_limit"]),
            _variant("V5_full_risk_managed", max_dd=-0.5085, sharpe=1.07,
                     eligible=False, blockers=["max_drawdown_exceeds_limit"]),
        ],
        "eligible_for_paper_prep": ["V2_trend_plus_cash_regime"],
        "any_variant_eligible_for_paper_prep": True,
    }


def _report_none_eligible():
    return {
        "verdict": vr.VERDICT_VARIANTS_COMPLETE,
        "variant_count": 2,
        "variant_results": [
            _variant("V1_trend_filter", max_dd=-0.5349, sharpe=0.92,
                     eligible=False, blockers=["max_drawdown_exceeds_limit"]),
            _variant("V3_voltarget_concentration_cap", max_dd=-0.8512, sharpe=0.99,
                     eligible=False, blockers=["max_drawdown_exceeds_limit"]),
        ],
        "eligible_for_paper_prep": [],
        "any_variant_eligible_for_paper_prep": False,
    }


# --------------------------------------------------------------------------- #
# the real outcome -> APPROVE PAPER PREP ONLY for V2
# --------------------------------------------------------------------------- #
def test_v2_only_eligible_approves_paper_prep():
    d = rv.review_variant_report(_report_v2_eligible())
    assert d["verdict"] == rv.VERDICT_REVIEW_COMPLETE
    assert d["paper_prep_decision"] == rv.APPROVE_PAPER_PREP_ONLY
    assert d["approved_for_paper_prep"] is True
    assert d["selected_variant_id"] == "V2_trend_plus_cash_regime"
    assert d["eligible_variant_ids"] == ["V2_trend_plus_cash_regime"]
    assert d["paper_prep_scope"] == rv.PAPER_PREP_SCOPE
    assert d["next_required_action"] == "HUMAN_APPROVED_PAPER_TRADING_PREP_FOR_SELECTED_VARIANT"


def test_approve_is_prep_only_no_gate_unlock():
    d = rv.review_variant_report(_report_v2_eligible())
    assert d["paper_trading_gate_locked"] is True
    assert d["micro_live_gate_locked"] is True
    assert d["authorizes_paper_trading"] is False
    assert d["builds_paper_runner"] is False
    assert d["promotes_gate"] is False
    assert d["unlocks_downstream_gate"] is False


def test_only_one_variant_eligible_is_noted():
    d = rv.review_variant_report(_report_v2_eligible())
    assert "only_one_variant_eligible" in d["risk_notes"]
    assert any(n.startswith("variants_exceeding_drawdown_floor") for n in d["risk_notes"])


# --------------------------------------------------------------------------- #
# no eligible variant -> DO NOT APPROVE
# --------------------------------------------------------------------------- #
def test_no_eligible_variant_blocks_paper_prep():
    d = rv.review_variant_report(_report_none_eligible())
    assert d["paper_prep_decision"] == rv.DO_NOT_APPROVE_PAPER_PREP_YET
    assert d["approved_for_paper_prep"] is False
    assert d["selected_variant_id"] is None
    assert "no_paper_prep_eligible_variant" in d["blockers"]
    assert d["next_required_action"] == "REVISE_VARIANTS_BEFORE_PAPER_PREP"


# --------------------------------------------------------------------------- #
# missing / malformed input
# --------------------------------------------------------------------------- #
def test_missing_report_is_blocked():
    d = rv.review_variant_report(None)
    assert d["verdict"] == rv.VERDICT_REVIEW_BLOCKED
    assert d["paper_prep_decision"] == rv.DO_NOT_APPROVE_PAPER_PREP_YET
    assert "variant_report_missing" in d["blockers"]


def test_incomplete_run_is_blocked():
    rep = _report_v2_eligible()
    rep["verdict"] = "BLOCKED_NOT_READY"
    d = rv.review_variant_report(rep)
    assert "variant_backtest_not_complete" in d["blockers"]
    assert d["paper_prep_decision"] == rv.DO_NOT_APPROVE_PAPER_PREP_YET


def test_no_results_is_blocked():
    d = rv.review_variant_report({"verdict": vr.VERDICT_VARIANTS_COMPLETE, "variant_results": []})
    assert "no_variant_results" in d["blockers"]


# --------------------------------------------------------------------------- #
# disk-backed build
# --------------------------------------------------------------------------- #
def test_build_reads_local_report(tmp_path):
    rep_dir = tmp_path / "reports" / "crypto_d1_variant_backtest"
    rep_dir.mkdir(parents=True, exist_ok=True)
    (rep_dir / "variant_backtest_report.json").write_text(
        json.dumps(_report_v2_eligible()), encoding="utf-8"
    )
    d = rv.build_variant_review_decision(repo_root=str(tmp_path))
    assert d["variant_report_found"] is True
    assert d["paper_prep_decision"] == rv.APPROVE_PAPER_PREP_ONLY
    assert d["selected_variant_id"] == "V2_trend_plus_cash_regime"


def test_build_handles_missing_local_report(tmp_path):
    d = rv.build_variant_review_decision(repo_root=str(tmp_path))
    assert d["variant_report_found"] is False
    assert "variant_report_missing" in d["blockers"]


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #
def test_validate_passes_on_approve_and_block():
    approve = rv.review_variant_report(_report_v2_eligible())
    block = rv.review_variant_report(_report_none_eligible())
    assert rv.validate_variant_review_decision(approve)["valid"] is True
    assert rv.validate_variant_review_decision(block)["valid"] is True


def test_validate_rejects_unlocked_gate():
    d = rv.review_variant_report(_report_v2_eligible())
    d["paper_trading_gate_locked"] = False
    v = rv.validate_variant_review_decision(d)
    assert v["valid"] is False
    assert any("gate_not_locked" in e for e in v["errors"])


def test_validate_rejects_approved_with_blockers():
    d = rv.review_variant_report(_report_v2_eligible())
    d["blockers"] = ["some_blocker"]
    v = rv.validate_variant_review_decision(d)
    assert v["valid"] is False
    assert any("approved_with_blockers" in e for e in v["errors"])


def test_validate_rejects_builds_paper_runner_true():
    d = rv.review_variant_report(_report_v2_eligible())
    d["builds_paper_runner"] = True
    v = rv.validate_variant_review_decision(d)
    assert v["valid"] is False
    assert any("capability_not_false:builds_paper_runner" in e for e in v["errors"])


def test_render_markdown_is_string():
    md = rv.render_variant_review_markdown(rv.review_variant_report(_report_v2_eligible()))
    assert md.startswith("# Crypto-D1 Variant Backtest Review / Paper-Prep Decision")
    assert "APPROVE_PAPER_PREP_ONLY" in md and "LOCKED" in md
    assert "V2_trend_plus_cash_regime" in md


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
