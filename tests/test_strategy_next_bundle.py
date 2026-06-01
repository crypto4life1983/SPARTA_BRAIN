"""Tests for tools/strategy_next_bundle.py (Next Bundle Generator v1).

Pure stdlib + pytest. All runs use a synthetic temp repo root so nothing in the
real reports/ or storage/ tree is touched. Asserts the v1 safety contract
(research-only; no broker/live/paper-exec/network/credentials; stdlib only),
graceful handling of missing/invalid inputs, deterministic selection, JSON
schema validity, and the safety phrasing of the generated prompt.
"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]
_TOOLS_DIR = _REPO_ROOT / "tools"
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))

import strategy_next_bundle as snb  # noqa: E402

TOOL_FILE = _TOOLS_DIR / "strategy_next_bundle.py"


# --- fixtures --------------------------------------------------------------

def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _sample_queue(items=None) -> dict:
    if items is None:
        items = [
            {
                "title": "Strategy Factory Routine Layer hardening",
                "lane": "jarvis_automation",
                "priority": 2,
                "blocked": False,
                "safety_level": "research_only",
                "reason": "Reduce copy-paste by hardening the daily snapshot + queue automation.",
                "required_inputs": ["existing reports"],
                "expected_output": "Hardened summary registry + snapshot",
                "next_bundle_suggestion": "Claude: routine-layer hardening",
            },
            {
                "title": "Donchian-S20 protocol pre-registration",
                "lane": "futures_donchian",
                "priority": 1,
                "blocked": False,
                "safety_level": "research_only",
                "reason": "Protocol/spec is missing; write pre-registration memo before any backtest.",
                "required_inputs": ["frozen IS data"],
                "expected_output": "Pre-registration memo + data contract",
                "next_bundle_suggestion": "Claude: protocol prereg",
            },
            {
                "title": "Crypto BTC 4H exploration",
                "lane": "crypto_btc_4h",
                "priority": 4,
                "blocked": False,
                "safety_level": "research_only",
                "reason": "Exploratory crypto research.",
                "required_inputs": ["crypto 4H data"],
                "expected_output": "Exploration memo",
                "next_bundle_suggestion": "Claude: crypto exploration",
            },
            {
                "title": "Live broker integration smoke",
                "lane": "live_broker",
                "priority": 1,
                "blocked": True,
                "safety_level": "execution",
                "reason": "Live trading via broker; place orders for smoke test.",
                "required_inputs": ["broker credentials"],
                "expected_output": "Live trade",
                "next_bundle_suggestion": "(forbidden)",
            },
            {
                "title": "Sneaky paper order execution",
                "lane": "paper_orders",
                "priority": 1,
                "blocked": False,  # tries to slip through without blocked flag
                "safety_level": "research_only",
                "reason": "Place order through paper-order execution path.",
                "required_inputs": [],
                "expected_output": "paper-order placed",
                "next_bundle_suggestion": "(forbidden)",
            },
        ]
    return {
        "schema_version": 1,
        "layer": "strategy_factory_routine_layer_v1",
        "routine": "strategy_queue",
        "generated_at": "2026-06-01T00:00:00Z",
        "read_only": True,
        "queue": items,
        "queue_length": len(items),
        "hygiene_first": True,
        "missing_inputs": [],
        "recommended_research_direction": "futures-first; protocol-first",
        "safety_notes": ["research-only"],
        "safety_status": "GREEN",
    }


def _sample_daily(active_lanes=("futures_donchian",)) -> dict:
    return {
        "schema_version": 1,
        "generated_at": "2026-06-01T00:00:00Z",
        "research_posture": "YELLOW",
        "active_lanes": list(active_lanes),
        "blockers": [],
        "recently_completed_reports": [],
        "report_count": 0,
        "what_should_run_next": "protocol prereg",
        "read_only": True,
        "safety_notes": [],
        "safety_status": "GREEN",
        "missing_inputs": [],
        "routine": "daily_state",
        "layer": "strategy_factory_routine_layer_v1",
    }


def _sample_weekly(deserving="futures_donchian", wasting=("crypto_btc_4h",)) -> dict:
    return {
        "schema_version": 1,
        "generated_at": "2026-06-01T00:00:00Z",
        "window_start": "2026-05-25",
        "window_end": "2026-05-31",
        "what_was_tested_or_built": [],
        "what_passed": [],
        "what_failed": [],
        "what_remains_uncertain": [],
        "closer_to_real_edge": False,
        "validated_strategy_exists": False,
        "lanes_wasting_time": list(wasting),
        "lane_deserving_next_deep_bundle": deserving,
        "next_action_recommendation": "protocol prereg",
        "scores": {"safety": 10, "automation_readiness": 7, "research_quality": 6},
        "automation_readiness_detail": {},
        "reports_in_window": 0,
        "read_only": True,
        "safety_notes": [],
        "safety_status": "GREEN",
        "missing_inputs": [],
        "routine": "weekly_review",
        "layer": "strategy_factory_routine_layer_v1",
    }


def _sample_snapshot(color="YELLOW") -> dict:
    return {
        "schema_version": 1,
        "generated_at": "2026-06-01T00:00:00Z",
        "kind": "strategy_factory_snapshot",
        "read_only": True,
        "posture": color,
        "active_lane": "futures_donchian",
        "next_best_action": "Write the Donchian-S20 prereg memo.",
        "blockers": [],
        "last_reports": [],
        "safety_notes": [],
        "commander_color": color,
        "live_trading_enabled": False,
        "broker_control_enabled": False,
        "paper_order_execution_enabled": False,
        "layer": "strategy_factory_routine_layer_v1",
    }


@pytest.fixture
def full_inputs(tmp_path: Path) -> Path:
    _write_json(tmp_path / snb.QUEUE_REL, _sample_queue())
    _write_json(tmp_path / snb.DAILY_REL, _sample_daily())
    _write_json(tmp_path / snb.WEEKLY_REL, _sample_weekly())
    _write_json(tmp_path / snb.SNAPSHOT_REL, _sample_snapshot())
    return tmp_path


# --- tests -----------------------------------------------------------------

def test_generate_with_full_inputs(full_inputs):
    payload = snb.generate(full_inputs)
    assert payload["title"] == "Donchian-S20 protocol pre-registration"
    assert payload["lane"] == "futures_donchian"
    assert payload["blocked"] is False
    assert payload["safety_level"] == "research_only"
    out = full_inputs / snb.OUTPUT_DIR_REL
    for fn in (snb.OUTPUT_JSON, snb.OUTPUT_MD, snb.OUTPUT_PROMPT):
        assert (out / fn).exists()


def test_generate_with_missing_inputs(tmp_path):
    # No files written; generator must NOT crash.
    payload = snb.generate(tmp_path)
    assert payload["title"] == "(no eligible bundle in queue)"
    assert payload["lane"] is None
    assert len(payload["warnings"]) == 4
    assert all(w.startswith("missing:") for w in payload["warnings"])


def test_generate_with_invalid_json(tmp_path):
    qp = tmp_path / snb.QUEUE_REL
    qp.parent.mkdir(parents=True, exist_ok=True)
    qp.write_text("{ this is not json", encoding="utf-8")
    payload = snb.generate(tmp_path)
    assert payload["title"] == "(no eligible bundle in queue)"
    assert any(w.startswith("invalid:") for w in payload["warnings"])
    assert (tmp_path / snb.OUTPUT_DIR_REL / snb.OUTPUT_JSON).exists()


def test_schema_keys_present(full_inputs):
    payload = snb.generate(full_inputs)
    for k in snb.REQUIRED_JSON_KEYS:
        assert k in payload, f"missing key: {k}"
    assert payload["safety_flags"] == snb.SAFETY_FLAGS
    for f in ("live_trading_enabled", "broker_control_enabled", "paper_order_execution_enabled"):
        assert payload["safety_flags"][f] is False


def test_prompt_contains_research_only_safety(full_inputs):
    snb.generate(full_inputs)
    text = (full_inputs / snb.OUTPUT_DIR_REL / snb.OUTPUT_PROMPT).read_text(encoding="utf-8")
    assert "Research-only." in text
    assert "No broker control" in text
    assert "No live trading" in text
    assert "No paper order execution" in text
    assert "No order placement" in text
    assert "No external network calls" in text
    assert "No API keys" in text
    assert "TESTS REQUIRED" in text
    assert "ACCEPTANCE CRITERIA" in text
    assert "Do not stage" in text
    assert "Do not commit" in text


def test_prompt_includes_tests_and_commit_boundary(full_inputs):
    snb.generate(full_inputs)
    text = (full_inputs / snb.OUTPUT_DIR_REL / snb.OUTPUT_PROMPT).read_text(encoding="utf-8")
    assert "python -m pytest tests/test_strategy_next_bundle.py" in text
    assert "Do not stage. Do not commit." in text
    assert "git commit -- <paths>" in text


def test_blocked_task_never_selected_over_safe(full_inputs):
    # The "Live broker integration smoke" item is priority 1 + blocked.
    # The "Sneaky paper order execution" item is priority 1 + danger keyword.
    # Neither must be selected.
    payload = snb.generate(full_inputs)
    assert payload["title"] != "Live broker integration smoke"
    assert payload["title"] != "Sneaky paper order execution"
    assert payload["blocked"] is False
    # Also: ranked list excludes them entirely.
    rank_titles = {r["title"] for r in payload["ranked_candidates"]}
    assert "Live broker integration smoke" not in rank_titles
    assert "Sneaky paper order execution" not in rank_titles


def test_deterministic_selection_is_stable(full_inputs):
    p1 = snb.generate(full_inputs)
    p2 = snb.generate(full_inputs)
    # The only field that changes turn-over-turn is generated_at; everything else identical.
    for k in ("selected_bundle_id", "title", "lane", "priority", "ranked_candidates"):
        assert p1[k] == p2[k], f"non-deterministic field: {k}"


def test_only_writes_inside_output_folder(tmp_path):
    snb.generate(tmp_path)
    out = tmp_path / snb.OUTPUT_DIR_REL
    written = sorted(p.relative_to(tmp_path).as_posix() for p in tmp_path.rglob("*") if p.is_file())
    for w in written:
        assert w.startswith(snb.OUTPUT_DIR_REL), f"file written outside output folder: {w}"


def test_validate_after_generate(full_inputs):
    snb.generate(full_inputs)
    ok, errors = snb.validate(full_inputs)
    assert ok is True, errors
    assert errors == []


def test_validate_detects_missing_file(tmp_path):
    ok, errs = snb.validate(tmp_path)
    assert ok is False
    assert any("missing" in e for e in errs)


def test_validate_detects_unpinned_safety_flag(full_inputs):
    snb.generate(full_inputs)
    jpath = full_inputs / snb.OUTPUT_DIR_REL / snb.OUTPUT_JSON
    data = json.loads(jpath.read_text(encoding="utf-8"))
    data["safety_flags"]["live_trading_enabled"] = True  # tamper
    jpath.write_text(json.dumps(data, indent=2), encoding="utf-8")
    ok, errs = snb.validate(full_inputs)
    assert ok is False
    assert any("live_trading_enabled" in e for e in errs)


def test_no_network_or_broker_imports_in_source():
    src = TOOL_FILE.read_text(encoding="utf-8")
    forbidden = (
        "import requests", "from requests",
        "import urllib", "from urllib",
        "import http", "from http",
        "import socket", "import ssl",
        "import tiingo", "from tiingo",
        "import ccxt", "from ccxt",
        "import alpaca", "from alpaca",
        "import binance", "from binance",
        "import dotenv", "from dotenv",
        "import subprocess", "from subprocess",
        "import os\n", "import os ",  # avoid `import os` (we use only Path/stdlib)
        "os.environ", "getenv",
        "urlopen", "api.telegram.org",
    )
    for tok in forbidden:
        assert tok not in src, f"forbidden token in generator source: {tok!r}"


def test_only_stdlib_imports():
    tree = ast.parse(TOOL_FILE.read_text(encoding="utf-8"))
    stdlib_ok = {
        "argparse", "json", "sys", "datetime", "pathlib", "typing", "__future__",
    }
    seen = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                seen.add(n.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            mod = (node.module or "").split(".")[0]
            seen.add(mod)
    extra = seen - stdlib_ok
    assert not extra, f"unexpected imports: {extra}"


def test_show_after_generate(full_inputs, capsys):
    snb.generate(full_inputs)
    rc = snb.main(["show", "--repo-root", str(full_inputs)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "selected:" in out
    assert "prompt:" in out


def test_cli_generate_show_validate(full_inputs, capsys):
    assert snb.main(["generate", "--repo-root", str(full_inputs)]) == 0
    assert snb.main(["validate", "--repo-root", str(full_inputs)]) == 0
    assert snb.main(["show", "--repo-root", str(full_inputs)]) == 0


def test_runtime_output_folder_is_gitignored():
    # The .gitignore must contain a line for next_bundle/ so generated files
    # are never accidentally committed.
    gi = (_REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "reports/strategy_factory_routines/next_bundle/" in gi


def test_danger_keyword_filter_does_not_kill_protocol_word():
    # "spec " / " spec" should not match unrelated phrases like "perspective" /
    # "respect" — keep a regression here.
    item = {
        "title": "Perspective review of past lanes",
        "lane": "review",
        "priority": 3,
        "blocked": False,
        "safety_level": "research_only",
        "reason": "We respect prior decisions; no spec authored yet.",
        "required_inputs": [],
        "expected_output": "review memo",
        "next_bundle_suggestion": "Claude: review",
    }
    danger, hits = snb._has_danger_signals(item)
    assert danger is False, hits


def test_active_lane_bonus_changes_selection(tmp_path):
    # Two items at equal nominal priority; the one matching active_lanes wins.
    items = [
        {"title": "A", "lane": "lane_a", "priority": 3, "blocked": False,
         "safety_level": "research_only", "reason": "A", "required_inputs": [],
         "expected_output": "A out", "next_bundle_suggestion": ""},
        {"title": "B", "lane": "lane_b", "priority": 3, "blocked": False,
         "safety_level": "research_only", "reason": "B", "required_inputs": [],
         "expected_output": "B out", "next_bundle_suggestion": ""},
    ]
    _write_json(tmp_path / snb.QUEUE_REL, _sample_queue(items))
    _write_json(tmp_path / snb.DAILY_REL, _sample_daily(active_lanes=("lane_b",)))
    _write_json(tmp_path / snb.WEEKLY_REL, _sample_weekly(deserving="(none)", wasting=()))
    _write_json(tmp_path / snb.SNAPSHOT_REL, _sample_snapshot())
    p = snb.generate(tmp_path)
    assert p["title"] == "B"
