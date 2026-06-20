"""Tests for the SPARTA Control Panel renderer (Bundle B).

Proves the renderer derives the four status badges (HEALTHY / NEEDS_ATTENTION / BLOCKED /
NOT_READY_COLLECTING) from the Bundle A current-state packet, renders repo + lane + C22
collection + scheduled-task health + the suggested next-action tokens (suggestion only), and
recomputes nothing (single source = the packet). No script tags / execution affordances."""
from __future__ import annotations

import ast
from pathlib import Path

import sparta_commander.sparta_control_panel_render_v1_contract as cpr
import sparta_commander.sparta_current_state_control_packet_contract as cp
import sparta_commander.sparta_scheduled_task_health_classifier_contract as th

_CLEAN = {"head": "h", "origin": "h", "ahead": 0, "behind": 0, "clean": True,
          "staged_paths": []}
_OK_HEALTH = th.build_task_health(
    [{"name": n, "found": True, "last_result": 0, "hours_since_last_run": 3.0}
     for n in th.PRIORITY_TASKS])


def _packet(repo=None, collected=1, latest="2026-06-20", days=1, health=None):
    return cp.build_current_state_packet(repo or _CLEAN, collected, latest, days,
                                         health or _OK_HEALTH)


# ---- the four badges -------------------------------------------------------

def test_badge_not_ready_collecting():
    assert cpr.compute_badge(_packet(collected=1)) == "NOT_READY_COLLECTING"


def test_badge_healthy_at_2020():
    assert cpr.compute_badge(_packet(collected=20, latest="2026-07-09", days=0)) == "HEALTHY"


def test_badge_needs_attention_on_missing_export():
    # export gap >1 day, but nothing blocking
    assert cpr.compute_badge(_packet(latest="2026-06-17", days=3)) == "NEEDS_ATTENTION"


def test_badge_blocked_on_dangerous_staged():
    repo = {**_CLEAN, "clean": False,
            "staged_paths": ["data/external_signum_trend_radar_gc/x.json"]}
    assert cpr.compute_badge(_packet(repo=repo)) == "BLOCKED"


def test_badge_blocked_on_priority_task_failed():
    bad = th.build_task_health([
        {"name": "C22_Signum_GC_Import_Automation", "found": True, "last_result": 2,
         "hours_since_last_run": 6.0}])
    assert cpr.compute_badge(_packet(health=bad)) == "BLOCKED"


# ---- markdown render surfaces all required facts ---------------------------

def test_render_markdown_facts():
    md = cpr.render_control_panel_markdown(_packet())
    assert "SPARTA Control Panel" in md
    assert "Status: NOT_READY_COLLECTING" in md
    assert "HOLD_FOR_MORE_FROZEN_DATA_WINDOWS" in md
    assert "ledger 26" in md
    assert "1/20" in md
    assert "C23: on-deck True" in md
    assert "HUMAN_STAGE_MORE_FROZEN_DAILY_TREND_RADAR_GC_WINDOWS_THEN_REREVIEW_C22_LABELS" in md
    assert "HUMAN_APPROVED_C22_SIGNUM_GC_FROZEN_DATA_WINDOW_REVIEW" in md
    assert "HUMAN_DECISION_OPEN_CANDIDATE_23_AFTER_C22_CONCLUDES_OR_HOLD" in md
    assert "suggestion only" in md
    # scheduled task names present
    assert "C22_Signum_GC_Download_Pickup" in md


# ---- html render surfaces facts, badge, no script tags ---------------------

def test_render_html_facts_and_safe():
    html = cpr.render_control_panel_html(_packet())
    assert "SPARTA STATUS: NOT_READY_COLLECTING" in html
    assert "HOLD_FOR_MORE_FROZEN_DATA_WINDOWS" in html
    assert "1/20" in html
    assert "suggestion only" in html
    assert "<script" not in html.lower()
    assert "onclick" not in html.lower()


def test_html_surfaces_missing_export_and_readiness():
    miss = cpr.render_control_panel_html(_packet(latest="2026-06-17", days=3))
    assert "MISSING EXPORT" in miss
    ready = cpr.render_control_panel_html(_packet(collected=20, latest="2026-07-09", days=0))
    assert "READINESS" in ready


# ---- renderer recomputes nothing (single source = packet) ------------------

def test_renderer_reads_only_the_packet():
    # a packet with an injected progress is rendered verbatim (no recompute)
    p = _packet(collected=7, latest="2026-06-26", days=0)
    assert p["c22_collection"]["progress"] == "7/20"
    assert "7/20" in cpr.render_control_panel_html(p)
    assert "7/20" in cpr.render_control_panel_markdown(p)


# ---- module purity ---------------------------------------------------------

def test_module_purity():
    src = Path(cpr.__file__).read_text(encoding="utf-8")
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "open(",
                 "subprocess", "Popen", "urlopen", "json.load", "read_text", "glob(",
                 "requests.", "Get-ScheduledTask"):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned = {"urllib", "requests", "socket", "http", "ccxt", "subprocess",
              "os", "io", "shutil", "json", "hashlib", "pathlib", "numpy", "pandas"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned), imported & banned
