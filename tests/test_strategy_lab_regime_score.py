from __future__ import annotations

from pathlib import Path

import strategy_lab.regime_score as regime_module
from strategy_lab.regime_score import RegimeScoreResult, RegimeTestInput, evaluate_regime_score, score_regime_fit


def test_balanced_candidate_passes():
    result = evaluate_regime_score(
        RegimeTestInput(
            candidate_id="cand_01",
            trend_return=14.0,
            range_return=12.0,
            high_vol_return=11.0,
            low_vol_return=10.0,
            compression_return=9.0,
            expansion_return=13.0,
            regime_sample_count=6,
        )
    )
    assert result.passed is True
    assert result.recommendation == "continue_research"
    assert result.strongest_regime in {"TREND", "EXPANSION"}
    assert result.weakest_regime in {"LOW_VOL", "COMPRESSION", "RANGE"}


def test_negative_trend_regime_fails():
    result = evaluate_regime_score(
        RegimeTestInput(
            candidate_id="cand_02",
            trend_return=-2.0,
            range_return=10.0,
            high_vol_return=8.0,
            low_vol_return=9.0,
            compression_return=7.0,
            expansion_return=11.0,
            regime_sample_count=6,
        )
    )
    assert result.passed is False
    assert "TREND" in result.weak_regimes
    assert result.recommendation == "reject_or_rework"


def test_low_sample_count_fails():
    result = evaluate_regime_score(
        RegimeTestInput(
            candidate_id="cand_03",
            trend_return=10.0,
            range_return=9.0,
            high_vol_return=8.0,
            low_vol_return=7.0,
            compression_return=6.0,
            expansion_return=11.0,
            regime_sample_count=2,
        )
    )
    assert result.passed is False
    assert result.regime_score <= 35


def test_strongest_and_weakest_regime_detected():
    result = evaluate_regime_score(
        RegimeTestInput(
            candidate_id="cand_04",
            trend_return=5.0,
            range_return=7.0,
            high_vol_return=3.0,
            low_vol_return=6.0,
            compression_return=2.0,
            expansion_return=9.0,
            regime_sample_count=5,
        )
    )
    assert result.strongest_regime == "EXPANSION"
    assert result.weakest_regime == "COMPRESSION"
    assert "COMPRESSION" in result.weak_regimes


def test_regime_result_serialization_round_trip():
    result = RegimeScoreResult(
        candidate_id="cand_05",
        regime_score=83,
        passed=True,
        weak_regimes=[],
        strongest_regime="EXPANSION",
        weakest_regime="COMPRESSION",
        recommendation="continue_research",
    )
    payload = result.to_dict()
    clone = RegimeScoreResult.from_dict(payload)
    assert clone.to_dict()["candidate_id"] == "cand_05"
    assert clone.to_dict()["passed"] is True
    assert clone.to_dict()["strongest_regime"] == "EXPANSION"


def test_output_path_remains_inside_regime_scores_root(monkeypatch):
    root = Path("strategy_lab/data/regime_scores")
    monkeypatch.setattr(regime_module, "DATA_ROOT", Path("strategy_lab/data"))
    monkeypatch.setattr(regime_module, "REGIME_SCORES_ROOT", root)
    before = {path.name for path in root.glob("cand_06__*.json")} if root.exists() else set()
    result = evaluate_regime_score(
        RegimeTestInput(
            candidate_id="cand_06",
            trend_return=9.0,
            range_return=8.0,
            high_vol_return=7.0,
            low_vol_return=6.0,
            compression_return=5.0,
            expansion_return=10.0,
            regime_sample_count=6,
        )
    )
    assert result.candidate_id == "cand_06"
    matches = [path for path in root.glob("cand_06__*.json") if path.name not in before]
    assert len(matches) == 1
    assert matches[0].resolve().is_relative_to(root.resolve())
    for path in matches:
        path.unlink(missing_ok=True)


def test_score_regime_fit_helper_works():
    payload = score_regime_fit({"candidate_id": "cand_07", "trend_return": 4.0}, regime="trend")
    assert payload["candidate_id"] == "cand_07"
    assert payload["regime"] == "TREND"
    assert payload["score"] > 0


def test_source_has_no_forbidden_language():
    source = Path(regime_module.__file__).read_text(encoding="utf-8").lower()
    for forbidden in ("broker", "place_order", "submit_order", "execute_order", "live execution"):
        assert forbidden not in source

