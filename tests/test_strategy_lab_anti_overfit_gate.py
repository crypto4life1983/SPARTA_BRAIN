from __future__ import annotations

from pathlib import Path

import strategy_lab.anti_overfit_gate as gate_module
from strategy_lab.anti_overfit_gate import AntiOverfitInput, AntiOverfitResult, evaluate_anti_overfit


def test_clean_robust_candidate_passes():
    result = evaluate_anti_overfit(
        AntiOverfitInput(
            candidate_id="cand_01",
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
    assert result.passed is True
    assert result.risk_level == "LOW"
    assert result.recommendation == "continue_research"
    assert result.score >= 80


def test_weak_oos_fails():
    result = evaluate_anti_overfit(
        AntiOverfitInput(
            candidate_id="cand_02",
            in_sample_return=20.0,
            out_of_sample_return=-1.0,
            walk_forward_pass_rate=0.88,
            symbol_count_tested=3,
            regime_count_tested=3,
            trades_count=40,
            max_drawdown=0.2,
            parameter_sensitivity_score=0.2,
        )
    )
    assert result.passed is False
    assert "out_of_sample_return_non_positive" in result.failure_reasons
    assert result.recommendation == "reject_or_rework"


def test_insufficient_symbols_fails():
    result = evaluate_anti_overfit(
        AntiOverfitInput(
            candidate_id="cand_03",
            in_sample_return=18.0,
            out_of_sample_return=10.0,
            walk_forward_pass_rate=0.8,
            symbol_count_tested=2,
            regime_count_tested=3,
            trades_count=40,
            max_drawdown=0.2,
            parameter_sensitivity_score=0.2,
        )
    )
    assert result.passed is False
    assert "symbol_count_tested_below_threshold" in result.failure_reasons


def test_high_parameter_sensitivity_fails():
    result = evaluate_anti_overfit(
        AntiOverfitInput(
            candidate_id="cand_04",
            in_sample_return=18.0,
            out_of_sample_return=12.0,
            walk_forward_pass_rate=0.8,
            symbol_count_tested=3,
            regime_count_tested=3,
            trades_count=40,
            max_drawdown=0.2,
            parameter_sensitivity_score=0.9,
        )
    )
    assert result.passed is False
    assert "parameter_sensitivity_score_above_threshold" in result.failure_reasons


def test_high_drawdown_fails():
    result = evaluate_anti_overfit(
        AntiOverfitInput(
            candidate_id="cand_05",
            in_sample_return=18.0,
            out_of_sample_return=12.0,
            walk_forward_pass_rate=0.8,
            symbol_count_tested=3,
            regime_count_tested=3,
            trades_count=40,
            max_drawdown=0.5,
            parameter_sensitivity_score=0.2,
        )
    )
    assert result.passed is False
    assert "max_drawdown_above_threshold" in result.failure_reasons


def test_result_serialization_round_trip():
    result = AntiOverfitResult(
        candidate_id="cand_06",
        passed=True,
        risk_level="LOW",
        score=92,
        failure_reasons=[],
        recommendation="continue_research",
    )
    payload = result.to_dict()
    clone = AntiOverfitResult.from_dict(payload)
    assert clone.to_dict()["candidate_id"] == "cand_06"
    assert clone.to_dict()["passed"] is True
    assert clone.to_dict()["recommendation"] == "continue_research"


def test_output_path_remains_inside_anti_overfit_root(monkeypatch):
    root = Path("strategy_lab/data/anti_overfit")
    monkeypatch.setattr(gate_module, "DATA_ROOT", Path("strategy_lab/data"))
    monkeypatch.setattr(gate_module, "ANTI_OVERFIT_ROOT", root)
    before = {path.name for path in root.glob("cand_07__*.json")} if root.exists() else set()
    result = evaluate_anti_overfit(
        AntiOverfitInput(
            candidate_id="cand_07",
            in_sample_return=18.0,
            out_of_sample_return=12.0,
            walk_forward_pass_rate=0.8,
            symbol_count_tested=3,
            regime_count_tested=3,
            trades_count=40,
            max_drawdown=0.2,
            parameter_sensitivity_score=0.2,
        )
    )
    assert result.candidate_id == "cand_07"
    matches = [path for path in root.glob("cand_07__*.json") if path.name not in before]
    assert len(matches) == 1
    assert matches[0].resolve().is_relative_to(root.resolve())
    for path in matches:
        path.unlink(missing_ok=True)


def test_source_has_no_forbidden_language():
    source = Path(gate_module.__file__).read_text(encoding="utf-8").lower()
    for forbidden in ("broker", "place_order", "submit_order", "execute_order", "live execution"):
        assert forbidden not in source

