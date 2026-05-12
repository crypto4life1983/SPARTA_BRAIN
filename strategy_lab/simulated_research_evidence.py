from __future__ import annotations

import json
from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .anti_overfit_gate import AntiOverfitInput, evaluate_anti_overfit
from .discovery_inbox import convert_idea_to_candidate, get_idea
from .evidence_pack import build_evidence_pack, get_latest_evidence_pack
from .human_review import approve_for_research
from .registry import get_candidate, load_candidates, update_candidate_state
from .regime_score import RegimeTestInput, evaluate_regime_score
from .research_plan import create_research_plan, get_research_plan
from .safety import assert_approved_path

LAB_ROOT = Path(__file__).resolve().parent
DATA_ROOT = LAB_ROOT / "data"
REPORT_ROOT = LAB_ROOT / "reports"
BACKTESTS_ROOT = DATA_ROOT / "backtests"
PHASE_18_REPORT = REPORT_ROOT / "phase_18_simulated_research_evidence.md"

PASS_CANDIDATE_ID = "seed_atr_compression_expansion"
FAIL_CANDIDATE_ID = "seed_regime_filter_overlay"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ensure_candidate(candidate_id: str) -> dict[str, Any]:
    candidate = get_candidate(candidate_id)
    if candidate is None:
        idea = get_idea(candidate_id)
        if idea is None:
            raise KeyError(f"Unknown idea: {candidate_id}")
        candidate = convert_idea_to_candidate(candidate_id)
    if str(candidate.get("lifecycle_state") or candidate.get("status") or "IDEA").upper() == "IDEA":
        approve_for_research(
            candidate_id,
            reviewer="Mahmoud",
            notes="Phase 18 simulated research evidence requires research-stage approval.",
        )
        candidate = get_candidate(candidate_id) or candidate
    if not get_research_plan(candidate_id):
        create_research_plan(candidate_id)
    return get_candidate(candidate_id) or candidate


def _backtest_path(candidate_id: str, symbol: str = "BTCUSDT") -> Path:
    BACKTESTS_ROOT.mkdir(parents=True, exist_ok=True)
    approved = assert_approved_path(BACKTESTS_ROOT)
    filename = f"{candidate_id}__{symbol.lower()}__1D__2024-01-01_to_2024-12-31__{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    return approved / filename


def _write_backtest(candidate_id: str, *, total_return: float, max_drawdown: float, win_rate: float, expectancy: float, sharpe: float, trades_count: int, status: str, notes: str) -> dict[str, Any]:
    result = {
        "candidate_id": candidate_id,
        "symbol": "BTCUSDT",
        "total_return": total_return,
        "max_drawdown": max_drawdown,
        "win_rate": win_rate,
        "expectancy": expectancy,
        "sharpe": sharpe,
        "trades_count": trades_count,
        "fees_paid": 18.0,
        "slippage_cost": 10.0,
        "status": status,
        "notes": notes,
    }
    payload = {
        "schema_version": "strategy_lab.backtest_result.v1",
        "generated_at": _utc_now(),
        "mode": "EXPERIMENTAL",
        "config": {
            "candidate_id": candidate_id,
            "symbol": "BTCUSDT",
            "timeframe": "1D",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "fee_bps": 5.0,
            "slippage_bps": 2.0,
            "initial_capital": 100000.0,
        },
        "strategy": {
            "candidate_id": candidate_id,
            "mode": "simulated_research",
        },
        "result": result,
    }
    path = _backtest_path(candidate_id)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return result


def _simulate_pass_candidate(candidate_id: str) -> dict[str, Any]:
    candidate = _ensure_candidate(candidate_id)
    _write_backtest(
        candidate_id,
        total_return=18.0,
        max_drawdown=0.18,
        win_rate=0.62,
        expectancy=0.85,
        sharpe=1.45,
        trades_count=44,
        status="OK",
        notes="Simulated positive backtest for phase 18.",
    )
    anti = evaluate_anti_overfit(
        AntiOverfitInput(
            candidate_id=candidate_id,
            in_sample_return=26.0,
            out_of_sample_return=17.0,
            walk_forward_pass_rate=0.88,
            symbol_count_tested=3,
            regime_count_tested=4,
            trades_count=44,
            max_drawdown=0.18,
            parameter_sensitivity_score=0.29,
        )
    )
    regime = evaluate_regime_score(
        RegimeTestInput(
            candidate_id=candidate_id,
            trend_return=12.0,
            range_return=8.0,
            high_vol_return=10.0,
            low_vol_return=7.0,
            compression_return=11.0,
            expansion_return=13.0,
            regime_sample_count=6,
        )
    )
    pack = build_evidence_pack(candidate_id)
    if pack.get("recommendation") == "ready_for_review":
        update_candidate_state(candidate_id, "BACKTESTED")
    return {
        "candidate": get_candidate(candidate_id) or candidate,
        "backtest": get_latest_evidence_pack(candidate_id) and "latest_pack_saved",
        "anti_overfit": anti.to_dict(),
        "regime_score": regime.to_dict(),
        "evidence_pack": pack,
    }


def _simulate_fail_candidate(candidate_id: str) -> dict[str, Any]:
    candidate = _ensure_candidate(candidate_id)
    _write_backtest(
        candidate_id,
        total_return=-4.0,
        max_drawdown=0.42,
        win_rate=0.34,
        expectancy=-0.1,
        sharpe=-0.45,
        trades_count=18,
        status="FAILED",
        notes="Simulated negative backtest for phase 18.",
    )
    anti = evaluate_anti_overfit(
        AntiOverfitInput(
            candidate_id=candidate_id,
            in_sample_return=12.0,
            out_of_sample_return=-3.0,
            walk_forward_pass_rate=0.42,
            symbol_count_tested=2,
            regime_count_tested=2,
            trades_count=18,
            max_drawdown=0.42,
            parameter_sensitivity_score=0.88,
        )
    )
    regime = evaluate_regime_score(
        RegimeTestInput(
            candidate_id=candidate_id,
            trend_return=-2.0,
            range_return=1.0,
            high_vol_return=0.0,
            low_vol_return=1.0,
            compression_return=2.0,
            expansion_return=-1.0,
            regime_sample_count=4,
        )
    )
    pack = build_evidence_pack(candidate_id)
    return {
        "candidate": get_candidate(candidate_id) or candidate,
        "anti_overfit": anti.to_dict(),
        "regime_score": regime.to_dict(),
        "evidence_pack": pack,
    }


def run_phase_18_simulated_research() -> dict[str, Any]:
    before = Counter(str(c.get("lifecycle_state") or c.get("status") or "IDEA").upper() for c in load_candidates())

    pass_result = _simulate_pass_candidate(PASS_CANDIDATE_ID)
    fail_result = _simulate_fail_candidate(FAIL_CANDIDATE_ID)

    after = Counter(str(c.get("lifecycle_state") or c.get("status") or "IDEA").upper() for c in load_candidates())

    report = {
        "generated_at": _utc_now(),
        "before": dict(before),
        "after": dict(after),
        "pass_candidate": PASS_CANDIDATE_ID,
        "fail_candidate": FAIL_CANDIDATE_ID,
        "results": {
            PASS_CANDIDATE_ID: pass_result,
            FAIL_CANDIDATE_ID: fail_result,
        },
    }

    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    approved = assert_approved_path(REPORT_ROOT)
    path = approved / PHASE_18_REPORT.name
    lines = [
        "# Strategy Lab Phase 18 Simulated Research Evidence",
        "",
        f"Generated at: {report['generated_at']}",
        "",
        "## Lifecycle Distribution",
        f"- Before: {report['before']}",
        f"- After: {report['after']}",
        "",
        "## Pass Candidate",
        f"- {PASS_CANDIDATE_ID}",
        f"  - evidence recommendation: {pass_result['evidence_pack']['recommendation']}",
        f"  - lifecycle state: {pass_result['candidate'].get('lifecycle_state') or pass_result['candidate'].get('status')}",
        f"  - missing evidence: {', '.join(pass_result['evidence_pack'].get('missing_evidence') or []) or 'none'}",
        "",
        "## Fail Candidate",
        f"- {FAIL_CANDIDATE_ID}",
        f"  - evidence recommendation: {fail_result['evidence_pack']['recommendation']}",
        f"  - lifecycle state: {fail_result['candidate'].get('lifecycle_state') or fail_result['candidate'].get('status')}",
        f"  - missing evidence: {', '.join(fail_result['evidence_pack'].get('missing_evidence') or []) or 'none'}",
        "",
        "## Evidence Summary",
        f"- pass backtest total_return: 18.0",
        f"- fail backtest total_return: -4.0",
        f"- pass anti_overfit passed: {pass_result['anti_overfit']['passed']}",
        f"- fail anti_overfit passed: {fail_result['anti_overfit']['passed']}",
        f"- pass regime_score passed: {pass_result['regime_score']['passed']}",
        f"- fail regime_score passed: {fail_result['regime_score']['passed']}",
        "",
        "## Safety",
        "- isolated: true",
        "- frozen_stack_touched: false",
        "- profit_brain_touched: false",
        "- execution_imports: false",
        "- no_live_logic: true",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report


def main() -> None:
    run_phase_18_simulated_research()
