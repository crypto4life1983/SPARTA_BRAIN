"""Tests for the SPARTA Candidate Arena v1 contract + report runner.

Proves: frozen-data only (no network/exchange/live/paper imports or actions); missing evidence
is EXPLICIT (not guessed); C22 remains HOLD; C23/C24 remain blocked by the broad-crypto-universe
(survivorship) issue; VRP Phase-1 appears PROMISING but NOT promoted; VRP Phase-2 forward
snapshot/scheduler is NOT treated as backtest evidence; output is deterministic; and nothing is
marked promotion/review-ready."""
from __future__ import annotations

import ast
from pathlib import Path

import sparta_commander.sparta_candidate_arena_v1_contract as arena
import tools.sparta_candidate_arena_report_once as runner


_A = arena.build_candidate_arena()


def test_builds_and_validates():
    assert _A["mode"] == "RESEARCH_ONLY"
    assert _A["is_read_only_arena"] is True
    assert arena.validate_candidate_arena(_A)["valid"] is True
    # all 12 columns on every row
    for r in _A["rows"]:
        for c in arena.COLUMNS:
            assert c in r, (r["candidate_id"], c)


def test_deterministic():
    a = arena.build_candidate_arena()
    b = arena.build_candidate_arena()
    assert a == b
    assert a["rows"] == b["rows"] and a["as_of"] == b["as_of"]


def test_c22_remains_hold():
    c22 = next(r for r in _A["rows"] if r["candidate_id"] == "C22")
    assert c22["current_status"] == "ACTIVE_HOLD"
    assert _A["c22_is_hold"] is True
    assert c22["return_engine_score"] == arena.MISSING  # not replayed -> explicit MISSING


def test_c23_c24_blocked_by_broad_universe():
    for cid in ("C23", "C24"):
        r = next(x for x in _A["rows"] if x["candidate_id"] == cid)
        assert r["current_status"] == "REJECTED"
        assert "SURVIVORSHIP-BIASED broad crypto universe" in r["blocker_reason"]
    assert _A["c23_c24_blocked_by_broad_universe"] is True


def test_vrp_phase1_promising_not_promoted():
    v = next(r for r in _A["rows"] if r["candidate_id"] == "VRP_PHASE1")
    assert v["evidence_status"] == "PROMISING_INDEX_LEVEL_PROXY"
    assert "NOT_PROMOTED" in v["current_status"]
    assert _A["vrp_phase1_promising_not_promoted"] is True
    assert _A["anything_ready_for_promotion"] is False


def test_vrp_phase2_not_backtest_evidence():
    v = next(r for r in _A["rows"] if r["candidate_id"] == "VRP_PHASE2_DATA")
    assert v["evidence_status"] == "NOT_BACKTEST_EVIDENCE"
    assert v["current_status"] == "DATA_COLLECTION_STATUS"
    assert _A["vrp_phase2_not_backtest_evidence"] is True


def test_missing_evidence_is_explicit():
    assert _A["missing_evidence_cells"] > 0
    # C22 (not replayed) carries MISSING on the strategy axes
    c22 = next(r for r in _A["rows"] if r["candidate_id"] == "C22")
    for axis in ("return_engine_score", "drawdown_score", "benchmark_score",
                 "cost_sensitivity_score", "correlation_or_diversifier_score"):
        assert c22[axis] == arena.MISSING


def test_nothing_promotion_or_review_ready_and_tamper():
    assert _A["anything_ready_for_promotion"] is False
    assert _A["anything_ready_for_human_review"] is False
    for flag in arena._CAPABILITY_FLAGS_FALSE:
        assert _A[flag] is False, flag
        assert arena.validate_candidate_arena({**_A, flag: True})["valid"] is False
    for k, v in _A["scope_locks"].items():
        assert v is True, k
    # cannot flip C22 off HOLD, mark VRP2 as evidence, or claim promotion-ready
    bad = {**_A, "rows": [{**r, "current_status": "PROMOTED"} if r["candidate_id"] == "C22"
                          else r for r in _A["rows"]], "c22_is_hold": False}
    assert arena.validate_candidate_arena(bad)["valid"] is False
    assert arena.validate_candidate_arena({**_A, "anything_ready_for_promotion": True})["valid"] is False


def test_contract_and_runner_purity_no_exchange_live_paper():
    for mod in (arena, runner):
        src = Path(mod.__file__).read_text(encoding="utf-8")
        doc = ast.get_docstring(ast.parse(src)) or ""
        low = src.replace(doc, "").lower()
        for bad in ("urllib", "requests", "socket", "ccxt", "deribit.com", "fapi.binance",
                    "place_order", "create_order", "api_key", "private_key", ".sign(",
                    "paper_trade(", "live_trade(", "submit_order"):
            assert bad not in low, (mod.__name__, bad)
        tree = ast.parse(src)
        banned = {"urllib", "requests", "socket", "http", "ccxt", "subprocess", "numpy", "pandas"}
        imported = {n.name.split(".")[0] for node in ast.walk(tree)
                    if isinstance(node, ast.Import) for n in node.names} | {
            node.module.split(".")[0] for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module}
        assert not (imported & banned), (mod.__name__, imported & banned)


def test_runner_builds_valid_arena():
    rec = runner._arena.build_candidate_arena()
    assert runner._arena.validate_candidate_arena(rec)["valid"] is True
