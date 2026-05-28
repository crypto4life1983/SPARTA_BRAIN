"""Tests for GET /trade-ledger.

The route is a read-only SPARTA viewer over normalized trading decision
artifacts. It must never expose a trading control surface.
"""
from __future__ import annotations

import re

import pytest


pytest.importorskip("fastapi")


def test_trade_ledger_route_returns_200():
    import app as app_module
    from fastapi.testclient import TestClient

    client = TestClient(app_module.app)
    r = client.get("/trade-ledger")

    assert r.status_code == 200


def test_trade_ledger_contains_read_only_warning():
    import app as app_module
    from fastapi.testclient import TestClient

    client = TestClient(app_module.app)
    r = client.get("/trade-ledger")

    assert "READ ONLY" in r.text
    assert "no broker, no exchange, no order placement, no bot control" in r.text


def test_trade_ledger_has_no_post_action_or_trading_controls():
    import app as app_module
    from fastapi.testclient import TestClient

    client = TestClient(app_module.app)
    r = client.get("/trade-ledger")
    body_lower = r.text.lower()

    assert "<form" not in body_lower
    assert 'method="post"' not in body_lower
    assert "method='post'" not in body_lower
    assert "<button" not in body_lower
    assert "onclick=" not in body_lower

    forbidden_phrases = (
        "place order",
        "cancel order",
        "start bot",
        "stop bot",
        "execute trade",
        "go live",
        "submit order",
        "broker connect",
        "connect exchange",
        "live execution control",
    )
    for phrase in forbidden_phrases:
        assert phrase not in body_lower

    for token in ("buy", "sell", "execute"):
        assert not re.search(rf"\b{token}\b", body_lower)


def test_trade_ledger_route_405_on_non_get_verbs():
    import app as app_module
    from fastapi.testclient import TestClient

    client = TestClient(app_module.app)
    for verb in ("post", "put", "patch", "delete"):
        r = getattr(client, verb)("/trade-ledger")
        assert r.status_code == 405


def test_trade_ledger_route_fails_closed_if_adapter_throws(monkeypatch):
    import app as app_module
    from fastapi.testclient import TestClient
    from tools import trade_decision_ledger_adapter as ledger

    def _boom():
        raise RuntimeError("simulated ledger adapter failure")

    monkeypatch.setattr(ledger, "load_payload", _boom)

    client = TestClient(app_module.app)
    r = client.get("/trade-ledger")

    assert r.status_code == 200
    assert "ERROR" in r.text
    assert "simulated ledger adapter failure" in r.text
    assert "READ ONLY" in r.text


def test_base_navigation_links_trade_ledger():
    from pathlib import Path

    base = Path(__file__).resolve().parents[1] / "templates" / "base.html"
    body = base.read_text(encoding="utf-8")

    assert 'href="/trade-ledger"' in body
    assert "Trade Ledger" in body
