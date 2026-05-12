from __future__ import annotations

import json
from pathlib import Path

import strategy_lab.anti_overfit_gate as anti_module
import strategy_lab.backtest_wrapper as backtest_module
import strategy_lab.evidence_pack as evidence_module
import strategy_lab.paper_arena as paper_module
import strategy_lab.registry as registry_module
import strategy_lab.regime_score as regime_module
import strategy_lab.research_plan as plan_module
from strategy_lab.anti_overfit_gate import AntiOverfitInput, evaluate_anti_overfit
from strategy_lab.backtest_wrapper import BacktestConfig
from strategy_lab.evidence_pack import (
    build_evidence_pack,
    get_latest_evidence_pack,
    load_evidence_packs,
)
from strategy_lab.paper_arena import PaperArenaConfig, PaperArenaSnapshot, create_paper_arena, update_paper_snapshot
from strategy_lab.registry import create_candidate, get_candidate
from strategy_lab.regime_score import RegimeTestInput, evaluate_regime_score
from strategy_lab.research_plan import create_research_plan


def _patch_roots(monkeypatch, leaf: str) -> Path:
    data_root = Path("strategy_lab/data") / leaf
    evidence_root = data_root / "evidence_packs"
    backtests_root = data_root / "backtests"
    anti_root = data_root / "anti_overfit"
    regime_root = data_root / "regime_scores"
    paper_root = data_root / "paper_arena"
    plans_root = data_root / "research_plans"
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
    return data_root


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _prepare_backtest(path_root: Path, candidate_id: str, total_return: float = 18.0, status: str = "OK") -> None:
    _write_json(
        path_root / "backtests" / f"{candidate_id}__btc__1D__2024-01-01_to_2024-12-31__20240501T000000Z.json",
        {
            "candidate_id": candidate_id,
            "result": {
                "candidate_id": candidate_id,
                "symbol": "BTCUSDT",
                "total_return": total_return,
                "max_drawdown": 0.18,
                "win_rate": 0.61,
                "expectancy": 0.8,
                "sharpe": 1.4,
                "trades_count": 42,
                "fees_paid": 20.0,
                "slippage_cost": 12.0,
                "status": status,
                "notes": "synthetic backtest",
            },
        },
    )


def _prepare_anti(path_root: Path, candidate_id: str, passed: bool = True) -> None:
    result = evaluate_anti_overfit(
        AntiOverfitInput(
            candidate_id=candidate_id,
            in_sample_return=24.0,
            out_of_sample_return=18.0 if passed else -1.0,
            walk_forward_pass_rate=0.92 if passed else 0.4,
            symbol_count_tested=4,
            regime_count_tested=4,
            trades_count=48,
            max_drawdown=0.18,
            parameter_sensitivity_score=0.32,
        )
    )
    assert result.candidate_id == candidate_id


def _prepare_regime(path_root: Path, candidate_id: str, passed: bool = True) -> None:
    result = evaluate_regime_score(
        RegimeTestInput(
            candidate_id=candidate_id,
            trend_return=14.0 if passed else -2.0,
            range_return=12.0,
            high_vol_return=11.0,
            low_vol_return=10.0,
            compression_return=9.0,
            expansion_return=13.0,
            regime_sample_count=6,
        )
    )
    assert result.candidate_id == candidate_id


def test_in_research_with_missing_evidence_returns_collect_more_evidence(monkeypatch):
    root = _patch_roots(monkeypatch, "in_research_missing")
    create_candidate({"candidate_id": "cand_pack_01", "status": "IN_RESEARCH", "lifecycle_state": "IN_RESEARCH"})
    _write_json(
        root / "research_plans" / "plans.json",
        {
            "schema_version": "strategy_lab.research_plan.v1",
            "generated_at": "2026-01-01T00:00:00+00:00",
            "mode": "EXPERIMENTAL",
            "plans": [],
        },
    )
    pack = build_evidence_pack("cand_pack_01")
    assert pack["recommendation"] == "collect_more_evidence"
    assert "research_plan" in pack["missing_evidence"]
    assert "backtest" in pack["missing_evidence"]
    assert "anti_overfit" in pack["missing_evidence"]
    assert "regime_score" in pack["missing_evidence"]
    assert get_candidate("cand_pack_01")["lifecycle_state"] == "IN_RESEARCH"


def test_backtested_missing_anti_overfit_returns_collect_more_evidence(monkeypatch):
    root = _patch_roots(monkeypatch, "backtested_missing_anti")
    create_candidate({"candidate_id": "cand_pack_02", "status": "BACKTESTED", "lifecycle_state": "BACKTESTED"})
    _prepare_backtest(root, "cand_pack_02", total_return=12.0)
    _prepare_regime(root, "cand_pack_02", passed=True)
    pack = build_evidence_pack("cand_pack_02")
    assert pack["recommendation"] == "collect_more_evidence"
    assert "anti_overfit" in pack["missing_evidence"]
    assert "research_plan" not in pack["missing_evidence"]
    assert get_candidate("cand_pack_02")["lifecycle_state"] == "BACKTESTED"


def test_complete_evidence_returns_ready_for_review(monkeypatch):
    root = _patch_roots(monkeypatch, "complete")
    create_candidate({"candidate_id": "cand_pack_03", "status": "IN_RESEARCH", "lifecycle_state": "IN_RESEARCH"})
    _write_json(
        root / "research_plans" / "plans.json",
        {
            "schema_version": "strategy_lab.research_plan.v1",
            "generated_at": "2026-01-01T00:00:00+00:00",
            "mode": "EXPERIMENTAL",
            "plans": [
                {
                    "candidate_id": "cand_pack_03",
                    "hypothesis": "Synthetic hypothesis",
                    "symbols_to_test": ["BTCUSDT"],
                    "timeframes_to_test": ["1D"],
                    "regimes_to_test": ["TREND"],
                    "required_min_trades": 30,
                    "required_oos_periods": 3,
                    "required_walk_forward_windows": 3,
                    "risk_questions": [],
                    "rejection_conditions": [],
                    "created_at": "2026-01-01T00:00:00+00:00",
                    "status": "EXPERIMENTAL",
                }
            ],
        },
    )
    _prepare_backtest(root, "cand_pack_03", total_return=15.0, status="OK")
    _prepare_anti(root, "cand_pack_03", passed=True)
    _prepare_regime(root, "cand_pack_03", passed=True)
    create_paper_arena(
        PaperArenaConfig(
            candidate_id="cand_pack_03",
            symbol="BTCUSDT",
            timeframe="1D",
            start_date="2024-01-01",
            initial_equity=100000.0,
            max_simulated_risk_per_trade=0.01,
        )
    )
    update_paper_snapshot(
        "cand_pack_03",
        PaperArenaSnapshot(
            candidate_id="cand_pack_03",
            symbol="BTCUSDT",
            simulated_equity=101000.0,
            simulated_open_positions=0,
            simulated_closed_trades=2,
            simulated_drawdown=0.02,
            status="EXPERIMENTAL",
            notes="snapshot present",
        ),
    )
    pack = build_evidence_pack("cand_pack_03")
    assert pack["recommendation"] == "ready_for_review"
    assert pack["evidence_summary"]["complete_required_set"] is True
    assert pack["paper_snapshot_found"] is True
    assert get_latest_evidence_pack("cand_pack_03")["candidate_id"] == "cand_pack_03"
    assert load_evidence_packs()
    assert get_candidate("cand_pack_03")["lifecycle_state"] == "IN_RESEARCH"
    assert (Path("strategy_lab/reports") / "strategy_lab_phase_12_evidence_pack.md").exists()


def test_failed_evidence_returns_reject_or_rework(monkeypatch):
    root = _patch_roots(monkeypatch, "failed")
    create_candidate({"candidate_id": "cand_pack_04", "status": "BACKTESTED", "lifecycle_state": "BACKTESTED"})
    _prepare_backtest(root, "cand_pack_04", total_return=-3.0, status="FAILED")
    _prepare_anti(root, "cand_pack_04", passed=True)
    _prepare_regime(root, "cand_pack_04", passed=True)
    pack = build_evidence_pack("cand_pack_04")
    assert pack["recommendation"] == "reject_or_rework"
    assert pack["evidence_summary"]["failed_evidence"] is True


def test_no_lifecycle_change(monkeypatch):
    root = _patch_roots(monkeypatch, "no_lifecycle")
    create_candidate({"candidate_id": "cand_pack_05", "status": "BACKTESTED", "lifecycle_state": "BACKTESTED"})
    _prepare_backtest(root, "cand_pack_05", total_return=14.0)
    _prepare_anti(root, "cand_pack_05", passed=True)
    _prepare_regime(root, "cand_pack_05", passed=True)
    before = get_candidate("cand_pack_05")["lifecycle_state"]
    build_evidence_pack("cand_pack_05")
    after = get_candidate("cand_pack_05")["lifecycle_state"]
    assert before == after == "BACKTESTED"


def test_safety_scan_still_passes():
    source = Path(evidence_module.__file__).read_text(encoding="utf-8").lower()
    for forbidden in ("broker", "place_order", "submit_order", "execute_order", "live execution"):
        assert forbidden not in source
