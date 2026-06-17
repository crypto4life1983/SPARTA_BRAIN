"""Tests for the SPARTA Autopilot Morning Report / status surface.

Proves: the report is generated DETERMINISTICALLY from its inputs; a missing
overnight run file produces DID_NOT_RUN; a failed task produces FAILED; the C10
closed/rejected status appears; the next-human-gate paste text is surfaced; the
git/ahead-behind summary is included; and the reporting layer has NO
trading/paper/live/broker/order/detector/replay/portfolio capability and never
claims paper/live readiness."""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_TOOLS_DIR = _REPO_ROOT / "tools"
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))

import sparta_autopilot_morning_report as mr  # noqa: E402

TOOL_FILE = _TOOLS_DIR / "sparta_autopilot_morning_report.py"


# --- fixtures --------------------------------------------------------------- #

def _git_summary():
    return {"branch": "master", "staged": 0, "modified": 0, "untracked": 4400,
            "clean": True, "tracked_change_lines": [],
            "ahead_behind": {"upstream": "origin/master", "ahead": 0,
                             "behind": 0, "in_sync": True}}


def _candidate_status():
    return {
        "C10": {"family": "intraweek_calendar_seasonality_drift",
                "status": "REJECTED_KEPT_ON_RECORD", "active": False,
                "next_action": "NONE (closed, kept on record as research lesson)"},
        "C11": {"family": "cross_asset_dispersion_reversion",
                "status": "PROPOSED (proposal-only, awaiting human decision)",
                "active": False,
                "next_action": "HUMAN_DECISION_C11_ADVANCE_TO_SPEC_OR_REJECT_PROPOSAL"},
    }


def _success_run_state():
    return {
        "run_id": "overnight_20260616T050004Z",
        "run_time": "2026-06-16T05:00:45Z",
        "tasks_attempted": ["nightly_integrity", "seed_brief_draft"],
        "tasks_completed": ["nightly_integrity", "seed_brief_draft"],
        "tasks_failed": [], "tasks_skipped": [],
        "files_changed": ["data/overnight_autopilot/reports/seed_brief.md"],
        "tests_run": [{"command": "pytest -q", "result": "222 passed"}],
        "errors": [], "integrity_status": "INTACT", "explicit_status": None,
    }


# --- DID_NOT_RUN ------------------------------------------------------------ #

def test_missing_run_produces_did_not_run():
    assert mr.classify_run_status(None) == "DID_NOT_RUN"
    report = mr.build_morning_report(None, _git_summary(), _candidate_status())
    assert report["run_status"] == "DID_NOT_RUN"
    md = mr.render_markdown(report)
    assert "DID_NOT_RUN" in md
    assert "DID NOT RUN" in md.upper()


def test_load_run_state_missing_dir_returns_none(tmp_path):
    empty = tmp_path / "no_runs"
    empty.mkdir()
    assert mr.load_run_state(empty) is None


# --- FAILED ----------------------------------------------------------------- #

def test_failed_task_produces_failed():
    rs = _success_run_state()
    rs["tasks_failed"] = ["seed_brief_draft"]
    rs["tasks_completed"] = ["nightly_integrity"]
    rs["errors"] = ["seed_brief_draft: boom"]
    assert mr.classify_run_status(rs) == "FAILED"
    report = mr.build_morning_report(rs, _git_summary(), _candidate_status())
    assert report["run_status"] == "FAILED"
    assert "seed_brief_draft" in report["tasks_failed"]
    md = mr.render_markdown(report)
    assert "FAILED" in md
    assert "stopped safely" in md
    assert "seed_brief_draft: boom" in md


def test_integrity_breach_produces_failed():
    rs = _success_run_state()
    rs["integrity_status"] = "BREACHED"
    assert mr.classify_run_status(rs) == "FAILED"


def test_normalize_overnight_run_maps_errors_to_failed():
    raw = {
        "run_id": "overnight_x", "started_utc": "2026-06-16T05:00:00Z",
        "finished_utc": "2026-06-16T05:01:00Z", "integrity_status": "INTACT",
        "artifacts_produced": ["a.md"],
        "tasks_executed": [
            {"task_id": "t1", "outcome": {"errors": [], "intact": True}},
            {"task_id": "t2", "outcome": {"errors": ["bad"], "intact": False}},
        ],
        "tasks_skipped": [],
    }
    rs = mr.normalize_overnight_run(raw)
    assert rs["tasks_attempted"] == ["t1", "t2"]
    assert rs["tasks_completed"] == ["t1"]
    assert rs["tasks_failed"] == ["t2"]
    assert any("t2" in e for e in rs["errors"])
    assert mr.classify_run_status(rs) == "FAILED"


# --- PARTIAL / SUCCESS ------------------------------------------------------ #

def test_skipped_no_failure_produces_partial():
    rs = _success_run_state()
    rs["tasks_skipped"] = ["extra_task"]
    assert mr.classify_run_status(rs) == "PARTIAL"


def test_clean_run_produces_success():
    assert mr.classify_run_status(_success_run_state()) == "SUCCESS"


# --- determinism ------------------------------------------------------------ #

def test_report_is_deterministic():
    rs, gs, cs = _success_run_state(), _git_summary(), _candidate_status()
    r1 = mr.build_morning_report(rs, gs, cs, report_generated_at="2026-06-16T06:00:00Z")
    r2 = mr.build_morning_report(rs, gs, cs, report_generated_at="2026-06-16T06:00:00Z")
    assert r1 == r2
    assert mr.render_markdown(r1) == mr.render_markdown(r2)
    # json round-trips identically
    assert json.dumps(r1, sort_keys=True) == json.dumps(r2, sort_keys=True)


# --- C10 closed + next gate paste text -------------------------------------- #

def test_c10_closed_status_appears():
    report = mr.build_morning_report(_success_run_state(), _git_summary(),
                                     _candidate_status())
    c10 = report["candidate_status"]["C10"]
    assert c10["status"] == "REJECTED_KEPT_ON_RECORD"
    assert c10["active"] is False
    md = mr.render_markdown(report)
    assert "REJECTED_KEPT_ON_RECORD" in md
    assert "intraweek_calendar_seasonality_drift" in md


def test_next_human_gate_paste_text_surfaced():
    report = mr.build_morning_report(_success_run_state(), _git_summary(),
                                     _candidate_status())
    gate = report["next_required_human_gate"]
    assert gate["candidate"] == "C11"
    assert gate["action"] == (
        "HUMAN_DECISION_C11_ADVANCE_TO_SPEC_OR_REJECT_PROPOSAL")
    assert gate["approval_text_to_paste"] == "APPROVE_C11_ADVANCE_TO_CANDIDATE_SPEC"
    assert gate["reject_text_to_paste"] == "REJECT_C11_FAMILY_PROPOSAL"
    md = mr.render_markdown(report)
    assert "APPROVE_C11_ADVANCE_TO_CANDIDATE_SPEC" in md
    assert "REJECT_C11_FAMILY_PROPOSAL" in md


def test_what_to_do_next_plain_english():
    report = mr.build_morning_report(_success_run_state(), _git_summary(),
                                     _candidate_status())
    wtdn = report["what_to_do_next"]
    assert "paste" in wtdn.lower()
    assert "APPROVE_C11_ADVANCE_TO_CANDIDATE_SPEC" in wtdn


def test_git_and_ahead_behind_included():
    report = mr.build_morning_report(_success_run_state(), _git_summary(),
                                     _candidate_status())
    assert report["git_status_summary"]["branch"] == "master"
    assert report["ahead_behind"]["in_sync"] is True


# --- all 12 required sections present in markdown --------------------------- #

def test_all_twelve_sections_present():
    md = mr.render_markdown(mr.build_morning_report(
        _success_run_state(), _git_summary(), _candidate_status()))
    for n, title in (
            (1, "Last run time"), (2, "Run status"), (3, "Tasks attempted"),
            (4, "Tasks completed"), (5, "Files created / changed"),
            (6, "Tests run and results"), (7, "Current candidate status"),
            (8, "Current next required human gate"), (9, "Git status summary"),
            (10, "Ahead / behind"), (11, "Error summary"),
            (12, "What I should do next")):
        assert ("## %d. %s" % (n, title)) in md, (n, title)


# --- no trading / paper / live / broker / order capability ------------------ #

def test_capability_flags_all_no_execution():
    report = mr.build_morning_report(_success_run_state(), _git_summary(),
                                     _candidate_status())
    for flag, val in report["capability_flags"].items():
        assert val is True, flag
    assert report["no_paper_live_readiness_claim"] is True


def test_no_paper_live_readiness_claim_in_markdown():
    md = mr.render_markdown(mr.build_morning_report(
        _success_run_state(), _git_summary(), _candidate_status())).lower()
    for banned in ("approved for paper", "approved for live",
                   "ready for live", "ready for paper", "profit guarantee",
                   "place order", "broker connected"):
        assert banned not in md, banned


def test_tool_has_no_broker_exchange_order_imports():
    """AST-based: no broker/exchange/network library imports and no order-call.
    Bare words like 'broker'/'exchange' appear only in the safety docstring, so
    we check imports + call names, not raw substrings."""
    src = TOOL_FILE.read_text(encoding="utf-8")
    tree = ast.parse(src)
    banned_mods = {"ccxt", "alpaca", "binance", "requests", "websockets",
                   "aiohttp", "dotenv", "smtplib", "telegram", "kraken",
                   "coinbase", "ib_insync", "socket", "http", "urllib"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods), imported & banned_mods
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = (node.func.attr if isinstance(node.func, ast.Attribute)
                    else getattr(node.func, "id", ""))
            assert name not in ("place_order", "create_order", "submit_order",
                                "getenv"), name
    # specific raw tokens that must never appear as code
    for tok in ("api.telegram.org", "os.environ", "place_order("):
        assert tok not in src, tok


def test_tool_subprocess_only_calls_git():
    """The only subprocess use is read-only git; no other executable."""
    src = TOOL_FILE.read_text(encoding="utf-8")
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            seg = ast.get_source_segment(src, node) or ""
            if "subprocess" in seg and "check_output" in seg:
                assert '["git"]' in seg or "[\"git\"] + args" in seg \
                    or '"git"' in seg, seg


# --- live candidate-status ledger (not the synthetic fixture) --------------- #

def test_live_ledger_reflects_c10_c11_c12_all_closed():
    """gather_candidate_status() reads the committed rejection-record contracts;
    after C10/C11/C12 all closed it must NOT show C11 as 'PROPOSED' and must
    include C12 -- all REJECTED_KEPT_ON_RECORD, inactive, no open gate."""
    status = mr.gather_candidate_status()
    for key, family in (("C10", "intraweek_calendar_seasonality_drift"),
                        ("C11", "cross_asset_dispersion_reversion"),
                        ("C12", "failed_breakdown_reclaim_reversal")):
        assert key in status, key
        c = status[key]
        assert c["family"] == family, key
        assert c["status"] == "REJECTED_KEPT_ON_RECORD", key
        assert c["active"] is False, key
        assert c["next_action"].startswith("NONE"), key
    # no stale 'PROPOSED' wording, and no false open human gate
    assert "PROPOSED" not in json.dumps(status)
    gate = mr._open_human_gate(status)
    assert gate["candidate"] is None
    assert gate["action"] == "NONE"


# --- generated latest artifacts are regenerable output, not source-of-truth - #

def test_latest_artifacts_gitignored_and_not_tracked():
    """reports/autopilot_morning/latest.{md,json} are REGENERABLE report output:
    they must stay gitignored and must NEVER be tracked source-of-truth."""
    import subprocess
    rel_md = mr.OUT_MD.relative_to(_REPO_ROOT).as_posix()
    rel_json = mr.OUT_JSON.relative_to(_REPO_ROOT).as_posix()
    assert rel_md == "reports/autopilot_morning/latest.md"
    assert rel_json == "reports/autopilot_morning/latest.json"
    # NOT tracked (the whole dir must carry no tracked files)
    tracked = subprocess.run(
        ["git", "ls-files", "reports/autopilot_morning/"],
        cwd=_REPO_ROOT, capture_output=True, text=True).stdout.split()
    assert tracked == [], tracked
    # gitignored (check-ignore echoes each ignored path, rc 0)
    ci = subprocess.run(
        ["git", "check-ignore", rel_md, rel_json],
        cwd=_REPO_ROOT, capture_output=True, text=True)
    assert ci.returncode == 0
    assert rel_md in ci.stdout and rel_json in ci.stdout
