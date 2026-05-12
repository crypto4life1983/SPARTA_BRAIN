from __future__ import annotations

import shutil
from pathlib import Path

import pytest

import strategy_lab.anti_overfit_gate as anti_module
import strategy_lab.backtest_wrapper as backtest_module
import strategy_lab.evidence_pack as evidence_module
import strategy_lab.paper_arena as paper_module
import strategy_lab.registry as registry_module
import strategy_lab.regime_score as regime_module
import strategy_lab.research_plan as plan_module
import strategy_lab.review_decision as review_module
from strategy_lab.anti_overfit_gate import AntiOverfitInput, evaluate_anti_overfit
from strategy_lab.backtest_wrapper import BacktestConfig
from strategy_lab.evidence_pack import build_evidence_pack
from strategy_lab.paper_arena import PaperArenaConfig, PaperArenaSnapshot, create_paper_arena, update_paper_snapshot
from strategy_lab.registry import create_candidate, get_candidate
from strategy_lab.regime_score import RegimeTestInput, evaluate_regime_score


def _patch_roots(monkeypatch, leaf: str) -> Path:
    data_root = Path("strategy_lab/data") / leaf
    evidence_root = data_root / "evidence_packs"
    review_root = data_root / "review_decisions"
    backtests_root = data_root / "backtests"
    anti_root = data_root / "anti_overfit"
    regime_root = data_root / "regime_scores"
    paper_root = data_root / "paper_arena"
    plans_root = data_root / "research_plans"
    monkeypatch.setattr(review_module, "DATA_ROOT", data_root)
    monkeypatch.setattr(review_module, "REPORT_ROOT", Path("strategy_lab/reports"))
    monkeypatch.setattr(review_module, "REVIEW_DECISIONS_ROOT", review_root)
    monkeypatch.setattr(review_module, "DECISIONS_FILE", review_root / "decisions.json")
    monkeypatch.setattr(review_module, "REPORT_FILE", Path("strategy_lab/reports/strategy_lab_phase_13_review_decision.md"))
    monkeypatch.setattr(evidence_module, "DATA_ROOT", data_root)
    monkeypatch.setattr(evidence_module, "REPORT_ROOT", Path("strategy_lab/reports"))
    monkeypatch.setattr(evidence_module, "EVIDENCE_PACKS_ROOT", evidence_root)
    monkeypatch.setattr(evidence_module, "PACKS_FILE", evidence_root / "packs.json")
    monkeypatch.setattr(evidence_module, "REPORT_FILE", Path("strategy_lab/reports/strategy_lab_phase_12_evidence_pack.md"))
    monkeypatch.setattr(evidence_module, "BACKTESTS_ROOT", backtests_root)
    monkeypatch.setattr(evidence_module, "ANTI_OVERFIT_ROOT", anti_root)
    monkeypatch.setattr(evidence_module, "REGIME_SCORES_ROOT", regime_root)
    monkeypatch.setattr(evidence_module, "RESEARCH_PLANS_ROOT", plans_root)
    monkeypatch.setattr(evidence_module, "PAPER_ARENA_FILE", paper_root / "paper_arena.json")
    monkeypatch.setattr(backtest_module, "DATA_ROOT", data_root)
    monkeypatch.setattr(backtest_module, "BACKTESTS_ROOT", backtests_root)
    monkeypatch.setattr(anti_module, "DATA_ROOT", data_root)
    monkeypatch.setattr(anti_module, "ANTI_OVERFIT_ROOT", anti_root)
    monkeypatch.setattr(regime_module, "DATA_ROOT", data_root)
    monkeypatch.setattr(regime_module, "REGIME_SCORES_ROOT", regime_root)
    monkeypatch.setattr(paper_module, "DATA_ROOT", data_root)
    monkeypatch.setattr(paper_module, "PAPER_ARENA_ROOT", paper_root)
    monkeypatch.setattr(paper_module, "PAPER_ARENA_FILE", paper_root / "paper_arena.json")
    monkeypatch.setattr(plan_module, "DATA_ROOT", data_root)
    monkeypatch.setattr(plan_module, "RESEARCH_PLANS_ROOT", plans_root)
    monkeypatch.setattr(plan_module, "PLANS_FILE", plans_root / "plans.json")
    monkeypatch.setattr(registry_module, "DATA_ROOT", data_root)
    monkeypatch.setattr(registry_module, "CANDIDATES_FILE", data_root / "candidates.json")
    if data_root.exists():
        shutil.rmtree(data_root, ignore_errors=True)
    return data_root


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(__import__("json").dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _prepare_ready_evidence(root: Path, candidate_id: str) -> None:
    _write_json(
        root / "research_plans" / "plans.json",
        {
            "schema_version": "strategy_lab.research_plan.v1",
            "generated_at": "2026-01-01T00:00:00+00:00",
            "mode": "EXPERIMENTAL",
            "plans": [],
        },
    )
    _write_json(
        root / "backtests" / f"{candidate_id}__btc__1D__2024-01-01_to_2024-12-31__20240501T000000Z.json",
        {
            "candidate_id": candidate_id,
            "result": {
                "candidate_id": candidate_id,
                "symbol": "BTCUSDT",
                "total_return": 15.0,
                "max_drawdown": 0.18,
                "win_rate": 0.61,
                "expectancy": 0.8,
                "sharpe": 1.4,
                "trades_count": 42,
                "fees_paid": 20.0,
                "slippage_cost": 12.0,
                "status": "OK",
                "notes": "synthetic backtest",
            },
        },
    )
    evaluate_anti_overfit(
        AntiOverfitInput(
            candidate_id=candidate_id,
            in_sample_return=24.0,
            out_of_sample_return=18.0,
            walk_forward_pass_rate=0.92,
            symbol_count_tested=4,
            regime_count_tested=4,
            trades_count=48,
            max_drawdown=0.18,
            parameter_sensitivity_score=0.32,
        )
    )
    evaluate_regime_score(
        RegimeTestInput(
            candidate_id=candidate_id,
            trend_return=14.0,
            range_return=12.0,
            high_vol_return=11.0,
            low_vol_return=10.0,
            compression_return=9.0,
            expansion_return=13.0,
            regime_sample_count=6,
        )
    )
    create_paper_arena(
        PaperArenaConfig(
            candidate_id=candidate_id,
            symbol="BTCUSDT",
            timeframe="1D",
            start_date="2024-01-01",
            initial_equity=100000.0,
            max_simulated_risk_per_trade=0.01,
        )
    )
    update_paper_snapshot(
        candidate_id,
        PaperArenaSnapshot(
            candidate_id=candidate_id,
            symbol="BTCUSDT",
            simulated_equity=101000.0,
            simulated_open_positions=0,
            simulated_closed_trades=2,
            simulated_drawdown=0.02,
            status="EXPERIMENTAL",
            notes="snapshot present",
        ),
    )
    build_evidence_pack(candidate_id)


def test_approve_backtested_to_robust_with_ready_evidence(monkeypatch):
    root = _patch_roots(monkeypatch, "approve_ready")
    create_candidate({"candidate_id": "cand_rev_01", "status": "BACKTESTED", "lifecycle_state": "BACKTESTED"})
    _prepare_ready_evidence(root, "cand_rev_01")
    decision = review_module.approve_backtested_to_robust("cand_rev_01", reviewer="alice", notes="Approve to robust")
    assert decision["decision"] == "APPROVE_FOR_ROBUST"
    assert decision["evidence_recommendation"] == "ready_for_review"
    assert get_candidate("cand_rev_01")["lifecycle_state"] == "ROBUST"
    assert review_module.load_review_decisions()


def test_block_approval_if_evidence_missing(monkeypatch):
    _patch_roots(monkeypatch, "block_missing")
    create_candidate({"candidate_id": "cand_rev_02", "status": "BACKTESTED", "lifecycle_state": "BACKTESTED"})
    with pytest.raises(ValueError):
        review_module.approve_backtested_to_robust("cand_rev_02", reviewer="alice", notes="Approve")


def test_block_approval_if_evidence_collect_more(monkeypatch):
    root = _patch_roots(monkeypatch, "block_collect_more")
    create_candidate({"candidate_id": "cand_rev_03", "status": "BACKTESTED", "lifecycle_state": "BACKTESTED"})
    _write_json(
        root / "backtests" / "cand_rev_03__btc__1D__2024-01-01_to_2024-12-31__20240501T000000Z.json",
        {
            "candidate_id": "cand_rev_03",
            "result": {
                "candidate_id": "cand_rev_03",
                "symbol": "BTCUSDT",
                "total_return": 10.0,
                "max_drawdown": 0.18,
                "win_rate": 0.61,
                "expectancy": 0.8,
                "sharpe": 1.4,
                "trades_count": 42,
                "fees_paid": 20.0,
                "slippage_cost": 12.0,
                "status": "OK",
                "notes": "synthetic backtest",
            },
        },
    )
    evaluate_regime_score(
        RegimeTestInput(
            candidate_id="cand_rev_03",
            trend_return=14.0,
            range_return=12.0,
            high_vol_return=11.0,
            low_vol_return=10.0,
            compression_return=9.0,
            expansion_return=13.0,
            regime_sample_count=6,
        )
    )
    build_evidence_pack("cand_rev_03")
    with pytest.raises(ValueError):
        review_module.approve_backtested_to_robust("cand_rev_03", reviewer="alice", notes="Approve")


def test_reject_logs_decision(monkeypatch):
    root = _patch_roots(monkeypatch, "reject")
    create_candidate({"candidate_id": "cand_rev_04", "status": "BACKTESTED", "lifecycle_state": "BACKTESTED"})
    _prepare_ready_evidence(root, "cand_rev_04")
    decision = review_module.reject_from_evidence("cand_rev_04", reviewer="bob", notes="Reject from review")
    assert decision["decision"] == "REJECT"
    assert decision["new_state"] == "REJECTED"
    assert get_candidate("cand_rev_04")["lifecycle_state"] == "REJECTED"


def test_reviewer_required(monkeypatch):
    root = _patch_roots(monkeypatch, "reviewer_required")
    create_candidate({"candidate_id": "cand_rev_05", "status": "BACKTESTED", "lifecycle_state": "BACKTESTED"})
    _prepare_ready_evidence(root, "cand_rev_05")
    with pytest.raises(ValueError):
        review_module.approve_backtested_to_robust("cand_rev_05", reviewer="", notes="Approve to robust")


def test_notes_required(monkeypatch):
    root = _patch_roots(monkeypatch, "notes_required")
    create_candidate({"candidate_id": "cand_rev_06", "status": "BACKTESTED", "lifecycle_state": "BACKTESTED"})
    _prepare_ready_evidence(root, "cand_rev_06")
    with pytest.raises(ValueError):
        review_module.approve_backtested_to_robust("cand_rev_06", reviewer="alice", notes="")


def test_no_live_state_emitted(monkeypatch):
    root = _patch_roots(monkeypatch, "no_live")
    create_candidate({"candidate_id": "cand_rev_07", "status": "BACKTESTED", "lifecycle_state": "BACKTESTED"})
    _prepare_ready_evidence(root, "cand_rev_07")
    decision = review_module.approve_backtested_to_robust("cand_rev_07", reviewer="alice", notes="Approve to robust")
    assert decision["new_state"] == "ROBUST"
    source = Path(review_module.__file__).read_text(encoding="utf-8").lower()
    assert "live_ready" not in source


def test_safety_scan_still_passes():
    source = Path(review_module.__file__).read_text(encoding="utf-8").lower()
    for forbidden in ("broker", "place_order", "submit_order", "execute_order", "live execution"):
        assert forbidden not in source
