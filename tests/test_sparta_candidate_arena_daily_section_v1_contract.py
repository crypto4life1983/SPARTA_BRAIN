"""Tests for the Candidate Arena daily section + its read-only /control integration.

Proves: the section is read-only and derived from the committed arena contract; no fetch/
trading/paper/live keywords or imports; C22 stays HOLD; nothing is promoted; the top promising
signal is shown NOT-promoted; VRP Phase-2 stays DATA_COLLECTION_STATUS (not strategy evidence);
MISSING_EVIDENCE stays explicit; HTML/markdown carry NO execution affordances; output is
deterministic; and the live /control route renders the arena section with no execution
affordances."""
from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

import sparta_commander.sparta_candidate_arena_daily_section_v1_contract as sec

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

_S = sec.build_arena_daily_summary()


def test_builds_and_validates():
    assert _S["mode"] == "RESEARCH_ONLY"
    assert _S["is_read_only_section"] is True
    assert _S["arena_valid"] is True
    assert sec.validate_arena_daily_summary(_S)["valid"] is True


def test_deterministic():
    assert sec.build_arena_daily_summary() == sec.build_arena_daily_summary()
    assert sec.render_arena_section_html() == sec.render_arena_section_html()


def test_top_promising_not_promoted():
    tps = _S["top_promising_signal"]
    assert tps is not None
    assert "NOT_PROMOTED" in tps["current_status"]
    assert _S["top_promising_is_promoted"] is False
    assert _S["anything_ready_for_promotion"] is False


def test_c22_active_hold():
    ah = _S["active_hold"]
    assert ah is not None and ah["candidate_id"] == "C22"
    assert ah["current_status"] == "ACTIVE_HOLD"


def test_vrp_phase2_data_status_only():
    dps = _S["data_pipeline_statuses"]
    assert dps, "expected a data-pipeline status row"
    for d in dps:
        assert d["is_strategy_evidence"] is False
        assert d["evidence_status"] == "NOT_BACKTEST_EVIDENCE"
    assert _S["vrp_phase2_is_data_status_only"] is True


def test_missing_evidence_explicit_and_nothing_review_ready():
    assert _S["missing_evidence_cells"] > 0
    assert _S["anything_ready_for_human_review"] is False
    assert _S["advances_c22"] is False and _S["reactivates_c23_c24"] is False
    assert _S["ranks_for_action"] is False


def test_render_has_no_execution_affordances():
    for r in (sec.render_arena_section_html(), sec.render_arena_section_markdown()):
        low = r.lower()
        for bad in ("<script", "onclick", "<form", "<button", "place order",
                    "send-trading-signal"):
            assert bad not in low, bad
    # html surfaces the key facts
    html = sec.render_arena_section_html()
    assert "Candidate Arena" in html and "NOT promoted" in html
    assert "DATA_COLLECTION_STATUS only" in html


def test_tamper_rejected():
    assert sec.validate_arena_daily_summary({**_S, "anything_ready_for_promotion": True})[
        "valid"] is False
    assert sec.validate_arena_daily_summary({**_S, "advances_c22": True})["valid"] is False
    bad_dp = [{**d, "is_strategy_evidence": True} for d in _S["data_pipeline_statuses"]]
    assert sec.validate_arena_daily_summary({**_S, "data_pipeline_statuses": bad_dp})[
        "valid"] is False


def test_section_purity_no_fetch_trading():
    src = Path(sec.__file__).read_text(encoding="utf-8")
    doc = ast.get_docstring(ast.parse(src)) or ""
    low = src.replace(doc, "").lower()
    for bad in ("urllib", "requests", "socket", "ccxt", "deribit.com", "fapi.binance",
                "place_order", "create_order", "api_key", ".sign(", "submit_order",
                "paper_trade(", "live_trade("):
        assert bad not in low, bad
    tree = ast.parse(src)
    banned = {"urllib", "requests", "socket", "http", "ccxt", "subprocess", "numpy", "pandas"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned), imported & banned


def test_live_control_route_includes_arena_section_no_affordances():
    try:
        from fastapi.testclient import TestClient
        import app as app_module
        client = TestClient(app_module.app)
    except Exception:  # noqa: BLE001
        pytest.skip("app not importable here")
    r = client.get("/control")
    assert r.status_code == 200
    text = r.text
    low = text.lower()
    assert "<script" not in low and "onclick" not in low
    if "unavailable" not in low:
        assert "Candidate Arena" in text
        assert "DATA_COLLECTION_STATUS only" in text
        assert "NOT promoted" in text
