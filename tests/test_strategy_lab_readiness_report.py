from __future__ import annotations

import json
from pathlib import Path

import strategy_lab.readiness_report as readiness_module
from strategy_lab.readiness_report import build_master_readiness_report, write_master_readiness_report


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def test_report_handles_empty_registry(monkeypatch):
    monkeypatch.setattr(readiness_module, "load_candidates", lambda: [])
    report = build_master_readiness_report()
    assert report["summary"]["candidate_count"] == 0
    assert report["summary"]["live_ready"] is False
    assert "LIVE_READY" not in json.dumps(report)


def test_failed_anti_overfit_is_reject(monkeypatch, tmp_path):
    monkeypatch.setattr(readiness_module, "load_candidates", lambda: [
        {"candidate_id": "cand_reject", "name": "Reject", "status": "BACKTESTED", "current_scorecard": {}}
    ])
    monkeypatch.setattr(readiness_module, "ANTI_OVERFIT_ROOT", tmp_path / "anti_overfit")
    monkeypatch.setattr(readiness_module, "REGIME_SCORES_ROOT", tmp_path / "regime_scores")
    monkeypatch.setattr(readiness_module, "BACKTESTS_ROOT", tmp_path / "backtests")
    monkeypatch.setattr(readiness_module, "PAPER_ARENA_FILE", tmp_path / "paper_arena" / "paper_arena.json")
    _write_json(
        tmp_path / "anti_overfit" / "cand_reject__001.json",
        {
            "result": {
                "candidate_id": "cand_reject",
                "passed": False,
                "recommendation": "reject_or_rework",
                "failure_reasons": ["out_of_sample_return_non_positive"],
            }
        },
    )
    _write_json(
        tmp_path / "regime_scores" / "cand_reject__001.json",
        {
            "result": {
                "candidate_id": "cand_reject",
                "passed": True,
                "recommendation": "continue_research",
                "weak_regimes": [],
            }
        },
    )
    _write_json(
        tmp_path / "backtests" / "cand_reject__001.json",
        {"result": {"candidate_id": "cand_reject", "status": "EXPERIMENTAL"}},
    )
    report = build_master_readiness_report()
    candidate = report["candidates"][0]
    assert candidate["readiness"] == "REJECT"
    assert "out_of_sample_return_non_positive" in candidate["reasons"]


def test_robust_plus_regime_pass_is_paper_ready(monkeypatch, tmp_path):
    monkeypatch.setattr(readiness_module, "load_candidates", lambda: [
        {"candidate_id": "cand_paper", "name": "Paper", "status": "ROBUST", "current_scorecard": {}}
    ])
    monkeypatch.setattr(readiness_module, "ANTI_OVERFIT_ROOT", tmp_path / "anti_overfit")
    monkeypatch.setattr(readiness_module, "REGIME_SCORES_ROOT", tmp_path / "regime_scores")
    monkeypatch.setattr(readiness_module, "BACKTESTS_ROOT", tmp_path / "backtests")
    monkeypatch.setattr(readiness_module, "PAPER_ARENA_FILE", tmp_path / "paper_arena" / "paper_arena.json")
    _write_json(
        tmp_path / "anti_overfit" / "cand_paper__001.json",
        {
            "result": {
                "candidate_id": "cand_paper",
                "passed": True,
                "recommendation": "continue_research",
                "failure_reasons": [],
            }
        },
    )
    _write_json(
        tmp_path / "regime_scores" / "cand_paper__001.json",
        {
            "result": {
                "candidate_id": "cand_paper",
                "passed": True,
                "recommendation": "continue_research",
                "weak_regimes": [],
            }
        },
    )
    _write_json(
        tmp_path / "backtests" / "cand_paper__001.json",
        {"result": {"candidate_id": "cand_paper", "status": "EXPERIMENTAL"}},
    )
    report = build_master_readiness_report()
    candidate = report["candidates"][0]
    assert candidate["readiness"] == "PAPER_READY"


def test_paper_tested_candidate_is_watchlist_ready(monkeypatch, tmp_path):
    monkeypatch.setattr(readiness_module, "load_candidates", lambda: [
        {"candidate_id": "cand_watch", "name": "Watch", "status": "PAPER_TESTING", "current_scorecard": {}}
    ])
    monkeypatch.setattr(readiness_module, "ANTI_OVERFIT_ROOT", tmp_path / "anti_overfit")
    monkeypatch.setattr(readiness_module, "REGIME_SCORES_ROOT", tmp_path / "regime_scores")
    monkeypatch.setattr(readiness_module, "BACKTESTS_ROOT", tmp_path / "backtests")
    monkeypatch.setattr(readiness_module, "PAPER_ARENA_FILE", tmp_path / "paper_arena" / "paper_arena.json")
    _write_json(
        tmp_path / "anti_overfit" / "cand_watch__001.json",
        {
            "result": {
                "candidate_id": "cand_watch",
                "passed": True,
                "recommendation": "continue_research",
                "failure_reasons": [],
            }
        },
    )
    _write_json(
        tmp_path / "regime_scores" / "cand_watch__001.json",
        {
            "result": {
                "candidate_id": "cand_watch",
                "passed": True,
                "recommendation": "continue_research",
                "weak_regimes": [],
            }
        },
    )
    _write_json(
        tmp_path / "backtests" / "cand_watch__001.json",
        {"result": {"candidate_id": "cand_watch", "status": "EXPERIMENTAL"}},
    )
    _write_json(
        tmp_path / "paper_arena" / "paper_arena.json",
        {
            "schema_version": "strategy_lab.paper_arena.v1",
            "generated_at": "2026-05-12T00:00:00+00:00",
            "mode": "EXPERIMENTAL",
            "arenas": [
                {
                    "candidate_id": "cand_watch",
                    "symbol": "BTCUSDT",
                    "status": "EXPERIMENTAL",
                    "snapshots": [{"candidate_id": "cand_watch", "symbol": "BTCUSDT", "simulated_equity": 100500.0}],
                }
            ],
        },
    )
    report = build_master_readiness_report()
    candidate = report["candidates"][0]
    assert candidate["readiness"] == "WATCHLIST_READY"


def test_report_never_emits_live_ready(monkeypatch):
    monkeypatch.setattr(readiness_module, "load_candidates", lambda: [])
    report = build_master_readiness_report()
    payload = json.dumps(report)
    assert "LIVE_READY" not in payload
    assert report["summary"]["live_ready"] is False


def test_report_path_stays_inside_allowed_report_output_paths(monkeypatch):
    monkeypatch.setattr(readiness_module, "load_candidates", lambda: [])
    report = write_master_readiness_report()
    assert report["summary"]["live_ready"] is False
    assert readiness_module.READINESS_JSON.resolve().is_relative_to(readiness_module.REPORT_ROOT.resolve())
    assert readiness_module.READINESS_MD.resolve().is_relative_to(readiness_module.REPORT_ROOT.resolve())
    assert readiness_module.REPORT_ROOT.resolve().is_relative_to(Path("strategy_lab/reports").resolve())


def test_source_has_no_forbidden_language():
    source = Path(readiness_module.__file__).read_text(encoding="utf-8").lower()
    for forbidden in ("broker", "place_order", "submit_order", "execute_order", "live execution"):
        assert forbidden not in source

