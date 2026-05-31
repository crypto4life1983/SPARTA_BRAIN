"""Tests for tools/strategy_factory_routines.py (Routine Layer v1).

All routines run against a synthetic temp repo root, so nothing in the real
reports/ or storage/ tree is touched. The tests assert the v1 safety contract
(read-only, no broker/network imports, pinned-False flags), graceful handling
of missing inputs, file creation, JSON validity, and the meaningful content
each routine must produce.
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

import strategy_factory_routines as sfr  # noqa: E402

TOOL_FILE = _TOOLS_DIR / "strategy_factory_routines.py"


# --- fixtures --------------------------------------------------------------

def _write_report(repo_root: Path, name: str, data: dict) -> None:
    d = (repo_root / "trading_research" / "agentic_factory" / "reports" / name)
    d.mkdir(parents=True, exist_ok=True)
    (d / "report.json").write_text(
        json.dumps(data, indent=2), encoding="utf-8")


@pytest.fixture
def populated_repo(tmp_path: Path) -> Path:
    """A temp repo with a roadmap memo, a launch bundle (gap_analysis) and a
    couple of branch reports."""
    _write_report(tmp_path, "crypto_d14_lane_closeout_and_next_roadmap", {
        "step": "Crypto-D14",
        "title": "Crypto Lane Closeout + Next-Roadmap Memo",
        "created": "2026-05-30",
        "memo_only": True,
        "final_recommendation": "REPO_HYGIENE_FIRST",
        "recommended_research_direction_after_hygiene": "CRYPTO_4H_PROTOCOL_NEXT",
        "7_final_recommendation": {
            "choice": "REPO_HYGIENE_FIRST",
            "research_direction_after_hygiene": "CRYPTO_4H_PROTOCOL_NEXT",
        },
        "validated_crypto_strategy": "NONE",
    })
    _write_report(tmp_path, "strategy_factory_v1_launch_bundle_001", {
        "title": "Launch Bundle 001",
        "created": "2026-05-30",
        "verdict": "FACTORY_V1_NEEDS_HYGIENE_FIRST",
        "candidate_registry": {"totals": {"tested": 8, "promoted": 0}},
        "gap_analysis": {
            "exists": ["a", "b", "c", "d", "e", "f", "g", "h"],
            "missing_for_overnight_automation": ["x", "y", "z", "p", "q", "r"],
        },
    })
    _write_report(tmp_path, "crypto_d13_crash_candle_oos_result", {
        "step": "Crypto-D13",
        "title": "CCR1 OOS Result",
        "created": "2026-05-30",
        "verdict": "OOS_FAIL",
    })
    # Provide a JARVIS snapshot to exercise the cross-reference path.
    snap_dir = tmp_path / "storage" / "jarvis" / "snapshots"
    snap_dir.mkdir(parents=True, exist_ok=True)
    (snap_dir / "latest_snapshot.json").write_text(
        json.dumps({"git": {"dirty": True}}), encoding="utf-8")
    return tmp_path


# --- safety: static source guarantees --------------------------------------

def test_tool_imports_no_network_or_broker_modules():
    tree = ast.parse(TOOL_FILE.read_text(encoding="utf-8"))
    forbidden = {
        "socket", "ssl", "http", "urllib", "requests", "httpx", "aiohttp",
        "ccxt", "alpaca", "alpaca_trade_api", "ib_insync", "binance",
        "websocket", "websockets", "smtplib", "ftplib", "telnetlib",
        "subprocess", "os", "dotenv",
    }
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported.add(node.module.split(".")[0])
    leaked = imported & forbidden
    assert not leaked, f"forbidden modules imported: {leaked}"


def test_tool_source_has_no_order_execution_identifiers():
    text = TOOL_FILE.read_text(encoding="utf-8").lower()
    for bad in (
        "place_order", "submit_order", "execute_order", "create_order",
        "live execution", "exchange write", "api_key", "secret_key",
    ):
        assert bad not in text, f"forbidden identifier present: {bad!r}"


def test_safety_flags_constant_is_all_false():
    assert sfr.SAFETY_FLAGS == {
        "live_trading_enabled": False,
        "broker_control_enabled": False,
        "paper_order_execution_enabled": False,
    }


# --- file creation + JSON validity -----------------------------------------

def _assert_valid_json(path: Path) -> dict:
    assert path.is_file(), f"missing output file: {path}"
    return json.loads(path.read_text(encoding="utf-8"))


def test_daily_state_creates_valid_files(populated_repo: Path):
    res = sfr.run_daily_state(populated_repo)
    data = _assert_valid_json(Path(res["paths"]["json"]))
    assert Path(res["paths"]["markdown"]).is_file()
    assert data["routine"] == "daily_state"
    assert data["report_count"] == 3
    assert data["safety_status"]["any_live_or_broker_control_exists"] is False
    for flag in sfr.SAFETY_FLAGS:
        assert data["safety_status"][flag] is False


def test_strategy_queue_creates_valid_files(populated_repo: Path):
    res = sfr.run_strategy_queue(populated_repo)
    data = _assert_valid_json(Path(res["paths"]["json"]))
    assert data["routine"] == "strategy_queue"
    assert data["queue_length"] == len(data["queue"])
    assert data["queue_length"] >= 8
    # Every queued item is research-only and carries the required fields.
    for item in data["queue"]:
        assert item["safety_level"] == "research_only"
        for field in (
            "lane", "priority", "reason", "required_inputs",
            "expected_output", "safety_level", "blocked",
            "next_bundle_suggestion",
        ):
            assert field in item


def test_weekly_review_creates_valid_files(populated_repo: Path):
    res = sfr.run_weekly_review(populated_repo)
    data = _assert_valid_json(Path(res["paths"]["json"]))
    assert data["routine"] == "weekly_review"
    scores = data["scores"]
    assert scores["safety_score"] == 100
    assert 0 <= scores["automation_readiness_score"] <= 100
    assert 0 <= scores["research_quality_score"] <= 100
    assert data["next_action_recommendation"]
    assert data["lane_deserving_next_deep_bundle"]


def test_jarvis_snapshot_has_required_fields(populated_repo: Path):
    res = sfr.run_jarvis_snapshot(populated_repo)
    data = _assert_valid_json(Path(res["paths"]["json"]))
    required = (
        "generated_at", "posture", "active_lane", "next_best_action",
        "blockers", "last_reports", "live_trading_enabled",
        "broker_control_enabled", "paper_order_execution_enabled",
        "safety_notes", "commander_color",
    )
    for field in required:
        assert field in data, f"snapshot missing required field: {field}"
    assert data["live_trading_enabled"] is False
    assert data["broker_control_enabled"] is False
    assert data["paper_order_execution_enabled"] is False
    assert data["commander_color"] in ("GREEN", "YELLOW", "RED")


# --- safety flags pinned False across every routine ------------------------

@pytest.mark.parametrize("runner", [
    sfr.run_daily_state,
    sfr.run_strategy_queue,
    sfr.run_weekly_review,
    sfr.run_jarvis_snapshot,
])
def test_every_routine_pins_safety_flags_false(populated_repo, runner):
    payload = runner(populated_repo)["payload"]
    blob = json.dumps(payload)
    assert '"live_trading_enabled": false' in blob or \
        payload.get("safety_status", {}).get(
            "live_trading_enabled") is False or \
        payload.get("live_trading_enabled") is False
    # No routine output may ever assert a True trading/broker flag.
    assert '"live_trading_enabled": true' not in blob.lower()
    assert '"broker_control_enabled": true' not in blob.lower()
    assert '"paper_order_execution_enabled": true' not in blob.lower()


# --- graceful degradation with no inputs -----------------------------------

def test_routines_do_not_crash_on_missing_reports(tmp_path: Path):
    # Empty repo: no factory reports, no jarvis snapshot.
    results = sfr.run_all(tmp_path)
    assert set(results.keys()) == {
        "daily-state", "strategy-queue", "weekly-review", "jarvis-snapshot"}
    daily = results["daily-state"]["payload"]
    assert daily["report_count"] == 0
    assert daily["research_posture"] in ("GREEN", "YELLOW", "RED")
    assert daily["missing_inputs"], "missing inputs should be reported"
    # Queue still degrades to the static research-only catalog.
    assert results["strategy-queue"]["payload"]["queue_length"] >= 8
    weekly = results["weekly-review"]["payload"]
    assert weekly["scores"]["safety_score"] == 100
    snap = results["jarvis-snapshot"]["payload"]
    assert snap["active_lane"] == "none"
    assert snap["live_trading_enabled"] is False


def test_no_credential_or_env_files_are_created(tmp_path: Path):
    sfr.run_all(tmp_path)
    forbidden_names = {".env", "credentials.json", "secrets.json"}
    created = {p.name for p in tmp_path.rglob("*") if p.is_file()}
    assert not (created & forbidden_names), "credential file was created"


def test_outputs_land_only_in_expected_dirs(tmp_path: Path):
    sfr.run_all(tmp_path)
    written = sorted(
        str(p.relative_to(tmp_path)).replace("\\", "/")
        for p in tmp_path.rglob("*") if p.is_file()
    )
    allowed_prefixes = (
        "reports/strategy_factory_routines/",
        "storage/jarvis/strategy_factory/",
    )
    for rel in written:
        assert rel.startswith(allowed_prefixes), \
            f"output written outside allowed dirs: {rel}"


# --- content grounding -----------------------------------------------------

def test_queue_marks_recommended_direction_and_hygiene_gate(populated_repo):
    q = sfr.build_strategy_queue(populated_repo)
    assert q["hygiene_first"] is True
    assert q["recommended_research_direction"] == "CRYPTO_4H_PROTOCOL_NEXT"
    lanes = {it["lane"]: it for it in q["queue"]}
    # Hygiene lanes are prioritized first when hygiene_first is set.
    assert lanes["data_qa_freeze"]["priority"] == 1
    assert lanes["jarvis_checkpoint"]["priority"] == 1
    # The recommended research lane is present and blocked behind hygiene.
    assert lanes["crypto_4h_protocol"]["blocked"] is True


def test_daily_state_next_action_reflects_memo(populated_repo):
    state = sfr.build_daily_state(populated_repo)
    assert "HYGIENE" in state["what_should_run_next"].upper()
    assert state["research_posture"] == "YELLOW"  # open blockers exist


def test_cli_all_runs_and_returns_zero(populated_repo, capsys):
    rc = sfr._cli(["all", "--repo-root", str(populated_repo)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "daily-state" in out and "jarvis-snapshot" in out
