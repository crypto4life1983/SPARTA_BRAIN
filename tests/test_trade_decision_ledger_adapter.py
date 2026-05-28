"""Tests for the SPARTA Trade Decision Ledger adapter.

The adapter is a SPARTA-side read-only normalizer over existing external
trading artifacts. These tests pin the safety contract: safe reads only,
malformed source rows become PARSE_ERROR, and missing files are explicit.
"""
from __future__ import annotations

import json
from pathlib import Path


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_adapter_reads_sample_json_and_jsonl_safely(tmp_path, monkeypatch):
    from tools import trade_decision_ledger_adapter as ledger

    root = tmp_path / "external"
    decisions = root / "data" / "btc" / "decisions.jsonl"
    decisions.parent.mkdir(parents=True, exist_ok=True)
    decisions.write_text(
        json.dumps({
            "timestamp": "2026-05-20T00:00:00+00:00",
            "candidate": {
                "pair": "BTC/USD",
                "strategy": "ema_pullback",
                "direction": "buy",
                "price": 100.5,
                "tags": ["pullback", "newyork-session"],
            },
            "decision": {
                "allow_trade": False,
                "blocked_reasons": ["risk_gate_failed"],
                "metadata": {"strategy_known": True},
            },
        }) + "\n",
        encoding="utf-8",
    )
    _write_json(root / "data" / "strategy_decision_state.json", {
        "mode": "SAFE_OBSERVE",
        "decisions": {
            "ema_pullback": {
                "allowed": True,
                "reason": "recommend_block_low_confidence",
                "confidence": 40,
                "closed_trades": 3,
            }
        },
    })
    _write_json(root / "data" / "trade_coordinator_state.json", {
        "last_blocked": {
            "timestamp": "2026-05-20T00:01:00+00:00",
            "strategy": "ema_pullback",
            "symbol": "BTCUSDT",
            "requested_side": "long",
            "reason": "duplicate_symbol_exposure",
        }
    })
    _write_json(root / "data" / "evidence_gate.json", {
        "mode": "READ_ONLY",
        "global_status": "WATCHLIST",
        "go_no_go_decision": "WATCH",
        "symbols": {
            "BTC": {
                "status": "WAIT",
                "blockers": ["NO_SYNC_CONFIRMATION"],
            }
        },
    })
    _write_json(root / "data" / "final_stack_paper_state.json", {
        "paper_only": True,
        "no_live_execution": True,
        "symbols": ["BTCUSDT"],
        "candidate_rows": 7,
    })

    monkeypatch.setattr(ledger, "external_root", lambda: root)

    payload = ledger.load_payload()

    assert payload["status"] == "OK"
    assert payload["summary"]["total_records"] >= 5
    assert payload["summary"]["blocked_records"] >= 2
    assert payload["summary"]["symbols_found"] >= 1
    assert any(row["symbol"] == "BTC/USD" for row in payload["records"])
    assert any(row["source_hash"] != "MISSING" for row in payload["records"])
    assert any(h["status"] == "OK" for h in payload["source_health"])


def test_malformed_jsonl_line_becomes_parse_error(tmp_path, monkeypatch):
    from tools import trade_decision_ledger_adapter as ledger

    root = tmp_path / "external"
    decisions = root / "data" / "eth" / "decisions.jsonl"
    decisions.parent.mkdir(parents=True, exist_ok=True)
    decisions.write_text("{not-json}\n", encoding="utf-8")
    monkeypatch.setattr(ledger, "external_root", lambda: root)

    payload = ledger.load_payload()

    assert payload["summary"]["parse_errors"] == 1
    assert any(row["final_state"] == "PARSE_ERROR" for row in payload["records"])
    assert any(h["status"] == "PARSE_ERROR" for h in payload["source_health"])


def test_missing_files_become_missing_source_health(tmp_path, monkeypatch):
    from tools import trade_decision_ledger_adapter as ledger

    root = tmp_path / "external"
    (root / "data").mkdir(parents=True)
    monkeypatch.setattr(ledger, "external_root", lambda: root)

    payload = ledger.load_payload()

    missing = [row for row in payload["source_health"] if row["status"] == "MISSING"]
    assert missing
    assert payload["summary"]["missing_sources"] == len(missing)
    assert payload["status"] == "MISSING"


def test_source_hash_is_created_for_each_real_record(tmp_path, monkeypatch):
    from tools import trade_decision_ledger_adapter as ledger

    root = tmp_path / "external"
    decisions = root / "data" / "sol" / "decisions.jsonl"
    decisions.parent.mkdir(parents=True, exist_ok=True)
    decisions.write_text(
        json.dumps({
            "timestamp": "2026-05-20T00:00:00+00:00",
            "candidate": {"pair": "SOL/USD"},
            "decision": {"allow_trade": True},
        }) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(ledger, "external_root", lambda: root)

    payload = ledger.load_payload()

    hashes = [
        row["source_hash"]
        for row in payload["records"]
        if row["source_type"] != "parse_error"
    ]
    assert hashes
    assert all(isinstance(h, str) and len(h) == 64 for h in hashes)


def test_adapter_source_has_no_forbidden_imports_or_network_surfaces():
    src = (
        Path(__file__).resolve().parents[1]
        / "tools"
        / "trade_decision_ledger_adapter.py"
    ).read_text(encoding="utf-8")
    lower = src.lower()
    forbidden = (
        "import bot_core",
        "from bot_core",
        "import kraken_adapter",
        "from kraken_adapter",
        "import live_bot_xrp_rbr",
        "from live_bot_xrp_rbr",
        "import auto_go_live",
        "from auto_go_live",
        "subprocess",
        "requests",
        "urllib",
        "http.client",
        "socket",
        ".env",
        "apikey",
        "api_key",
        "secret",
        "token",
    )
    for needle in forbidden:
        assert needle not in lower, f"forbidden surface in adapter: {needle}"
