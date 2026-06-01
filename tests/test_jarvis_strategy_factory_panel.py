"""Bundle 1 — JARVIS Strategy Factory dashboard integration (read-only).

Covers the additive ``/api/jarvis/status`` section ``strategy_factory`` and the
backend reader ``_jarvis_strategy_factory_snapshot``, which surfaces the
gitignored runtime snapshot written by
``tools/strategy_factory_routines.py jarvis-snapshot``.

Invariants enforced:
- the status aggregate exposes ``strategy_factory`` and stays read-only,
- the reader fails closed on a missing OR corrupt snapshot (never raises),
- the three trading-safety booleans are ALWAYS False in the API response,
- an on-disk snapshot claiming a True trading flag is treated as an anomaly
  (pinned False + commander_color RED), never trusted,
- the dashboard template carries the panel + research-only wording and adds no
  execution / broker / order control.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

pytest.importorskip("fastapi")

import app as app_module  # noqa: E402

_REPO_ROOT = Path(__file__).resolve().parents[1]
_FLAGS = ("live_trading_enabled", "broker_control_enabled",
          "paper_order_execution_enabled")


# --- status wiring ---------------------------------------------------------

def test_status_exposes_strategy_factory():
    status = app_module.api_jarvis_status()
    assert "strategy_factory" in status
    sf = status["strategy_factory"]
    assert isinstance(sf, dict)
    assert sf["read_only"] is True
    for flag in _FLAGS:
        assert sf[flag] is False


def test_status_strategy_factory_flags_always_false():
    # Regardless of disk state, the API response pins all three flags False.
    sf = app_module.api_jarvis_status()["strategy_factory"]
    for flag in _FLAGS:
        assert sf[flag] is False
    assert sf["commander_color"] in ("GREEN", "YELLOW", "RED")


# --- fail-closed reader ----------------------------------------------------

def test_missing_snapshot_does_not_crash(monkeypatch):
    # Point the rel-path at a file that does not exist under BASE.
    monkeypatch.setattr(
        app_module, "_JARVIS_STRATEGY_FACTORY_SNAPSHOT_REL",
        "storage/jarvis/strategy_factory/__definitely_missing__.json")
    out = app_module._jarvis_strategy_factory_snapshot()
    assert out["state"] == "missing"
    assert out["read_only"] is True
    for flag in _FLAGS:
        assert out[flag] is False
    assert out["posture"] == "UNKNOWN"
    assert out["blockers"] == []


def test_invalid_snapshot_json_does_not_crash(monkeypatch):
    bad = app_module.BASE / "storage" / "jarvis" / "strategy_factory" \
        / "__corrupt_test__.json"
    bad.parent.mkdir(parents=True, exist_ok=True)
    bad.write_text("{ this is not valid json ", encoding="utf-8")
    try:
        monkeypatch.setattr(
            app_module, "_JARVIS_STRATEGY_FACTORY_SNAPSHOT_REL",
            str(bad.relative_to(app_module.BASE)).replace("\\", "/"))
        out = app_module._jarvis_strategy_factory_snapshot()
        assert out["state"] == "invalid"
        assert out["read_only"] is True
        for flag in _FLAGS:
            assert out[flag] is False
        assert "detail" in out
    finally:
        bad.unlink(missing_ok=True)


def test_non_object_snapshot_fails_closed(monkeypatch):
    bad = app_module.BASE / "storage" / "jarvis" / "strategy_factory" \
        / "__notobj_test__.json"
    bad.parent.mkdir(parents=True, exist_ok=True)
    bad.write_text(json.dumps([1, 2, 3]), encoding="utf-8")
    try:
        monkeypatch.setattr(
            app_module, "_JARVIS_STRATEGY_FACTORY_SNAPSHOT_REL",
            str(bad.relative_to(app_module.BASE)).replace("\\", "/"))
        out = app_module._jarvis_strategy_factory_snapshot()
        assert out["state"] == "invalid"
        for flag in _FLAGS:
            assert out[flag] is False
    finally:
        bad.unlink(missing_ok=True)


def test_valid_snapshot_surfaces_fields(monkeypatch):
    good = app_module.BASE / "storage" / "jarvis" / "strategy_factory" \
        / "__valid_test__.json"
    good.parent.mkdir(parents=True, exist_ok=True)
    good.write_text(json.dumps({
        "generated_at": "2026-05-31T19:40:54+00:00",
        "posture": "yellow",
        "active_lane": "infra_hygiene",
        "next_best_action": "Continue from latest report",
        "blockers": ["working tree dirty"],
        "last_reports": [
            {"name": "r1", "outcome": "fail", "modified_at": "2026-05-31"},
        ],
        "safety_notes": ["Research-only routine layer."],
        "commander_color": "yellow",
        "live_trading_enabled": False,
        "broker_control_enabled": False,
        "paper_order_execution_enabled": False,
    }), encoding="utf-8")
    try:
        monkeypatch.setattr(
            app_module, "_JARVIS_STRATEGY_FACTORY_SNAPSHOT_REL",
            str(good.relative_to(app_module.BASE)).replace("\\", "/"))
        out = app_module._jarvis_strategy_factory_snapshot()
        assert out["state"] == "ready"
        assert out["posture"] == "YELLOW"
        assert out["active_lane"] == "infra_hygiene"
        assert out["commander_color"] == "YELLOW"
        assert out["safety_anomaly"] is False
        assert out["last_reports"][0]["name"] == "r1"
        for flag in _FLAGS:
            assert out[flag] is False
    finally:
        good.unlink(missing_ok=True)


@pytest.mark.parametrize("bad_flag", _FLAGS)
def test_anomalous_true_flag_is_pinned_false_and_red(monkeypatch, bad_flag):
    # A tampered/erroneous snapshot claiming a trading flag True must never be
    # trusted: the API pins it False and forces commander_color RED.
    payload = {
        "posture": "GREEN", "commander_color": "GREEN",
        "live_trading_enabled": False, "broker_control_enabled": False,
        "paper_order_execution_enabled": False,
    }
    payload[bad_flag] = True
    snap = app_module.BASE / "storage" / "jarvis" / "strategy_factory" \
        / "__anomaly_test__.json"
    snap.parent.mkdir(parents=True, exist_ok=True)
    snap.write_text(json.dumps(payload), encoding="utf-8")
    try:
        monkeypatch.setattr(
            app_module, "_JARVIS_STRATEGY_FACTORY_SNAPSHOT_REL",
            str(snap.relative_to(app_module.BASE)).replace("\\", "/"))
        out = app_module._jarvis_strategy_factory_snapshot()
        assert out["safety_anomaly"] is True
        assert out["commander_color"] == "RED"
        for flag in _FLAGS:
            assert out[flag] is False
        assert any("ANOMALY" in b for b in out["blockers"])
    finally:
        snap.unlink(missing_ok=True)


# --- template: panel present, research-only wording, no controls -----------

def test_template_has_strategy_factory_panel():
    body = (_REPO_ROOT / "templates" / "jarvis.html").read_text(encoding="utf-8")
    assert "pStrategyFactory" in body
    assert "Strategy Factory" in body


def test_template_has_research_only_wording():
    low = (_REPO_ROOT / "templates" / "jarvis.html").read_text(
        encoding="utf-8").lower()
    assert "research-only" in low
    assert "live trading: disabled" in low
    assert "broker control: disabled" in low
    assert "paper order execution: disabled" in low


def test_template_panel_adds_no_execution_controls():
    # The whole template must stay control-free; this guards our addition too.
    low = (_REPO_ROOT / "templates" / "jarvis.html").read_text(
        encoding="utf-8").lower()
    for tok in ("<button", "<form", "onclick", 'method="post"',
                "/api/jarvis/refresh"):
        assert tok not in low
