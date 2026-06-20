"""Tests for the SPARTA Automation V2 -- Morning Surface Integration bundle.

Verifies the read-only integration of the Automation V2 / Morning Decision Packet into the
morning-report and autopilot-panel surfaces: the surface git-summary -> V2 repo_state
adapter; the display-ready V2 morning section (repo sync, git-safety, candidate status,
C22 DATA_NOT_READY blocker, evidence chain, recommended next safe task, exact next human
approval token, explicit danger-lock display); additive markdown + html renderers; the
NON-MUTATING augment_morning_report / augment_panel composers; the gate-token output
(DATA_NOT_READY -> dataset staging, NOT labels); and the locked dangerous channels. Proves
the current morning packet includes the live Automation V2 state, that C22 DATA_NOT_READY
recommends dataset staging only, and that the source surfaces are never mutated."""
from __future__ import annotations

import ast

import sparta_commander.sparta_automation_v2_morning_integration_contract as mi
import sparta_commander.sparta_research_factory_automation_v2_contract as v2


_GS_CLEAN = {"branch": "master", "staged": 0, "modified": 0, "untracked": 5,
             "clean": True}
_SYNC = {"head": "9cc7dcffd3fce83ce574c981d00e5cbdb22207ee",
         "origin": "9cc7dcffd3fce83ce574c981d00e5cbdb22207ee", "ahead": 0, "behind": 0}

_SECTION = mi.build_v2_morning_section(
    mi.repo_state_from_surface(_GS_CLEAN, _SYNC))


# ---- core: section builds + validates --------------------------------------

def test_section_builds_and_validates():
    assert _SECTION["mode"] == "RESEARCH_ONLY"
    assert _SECTION["read_only"] is True
    assert _SECTION["recommends_only"] is True
    assert _SECTION["executes_nothing"] is True
    assert mi.validate_v2_morning_section(_SECTION)["valid"] is True


# ---- (adapter) surface git-summary -> V2 repo_state ------------------------

def test_repo_state_adapter():
    rs = mi.repo_state_from_surface(_GS_CLEAN, _SYNC)
    assert rs["clean"] is True and rs["staged_count"] == 0
    assert rs["ahead"] == 0 and rs["behind"] == 0
    assert rs["untracked_clutter_present"] is True
    assert rs["_sync_info_known"] is True
    # without sync_info, ahead/behind default to 0 and sync is flagged unknown
    rs2 = mi.repo_state_from_surface({"staged": 2, "modified": 1})
    assert rs2["_sync_info_known"] is False
    assert rs2["staged_count"] == 2
    assert rs2["clean"] is False   # inferred from staged+modified


# ---- (1) morning report integration: includes live V2 state ----------------

def test_section_surfaces_live_candidate_state_and_c22_block():
    assert _SECTION["rejected_ledger_count"] == 26
    assert _SECTION["last_rejected_candidate"] == "C21"
    assert _SECTION["lane_active_candidate"] is None
    assert "C22" in _SECTION["candidate_status_line"]
    assert _SECTION["c22_data_not_ready"] is True
    assert _SECTION["last_verdict"] == "DATA_NOT_READY"
    assert "DATA_NOT_READY" in _SECTION["blockers"]
    assert _SECTION["evidence_chain_valid"] is True
    sv = _SECTION["c22_stage_verdicts"]
    assert sv["data_readiness"] == "DATA_NOT_READY"
    assert sv["detector_spec_dry_run"] == "C22_DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW"


# ---- (4)+(5) C22 DATA_NOT_READY -> dataset staging only, not labels --------

def test_c22_data_not_ready_recommends_staging_not_labels():
    assert _SECTION["recommended_gate_kind"] == v2.REC_STAGE_DATA
    assert _SECTION["do_not_proceed_to_labels"] is True
    assert _SECTION["do_not_fabricate_data"] is True
    assert _SECTION["recommends_advancing_to_labels_while_blocked"] is False
    tok = _SECTION["next_human_approval_token"]
    assert tok == ("HUMAN_STAGE_FROZEN_TREND_RADAR_GC_DETECTOR_DATASET_THEN_"
                   "REAUTHORISE_C22_LABELS")
    assert "LABELS_OR_REJECT" not in _SECTION["recommended_gate_kind"]
    # tamper: flip the recommendation to advance while blocked -> invalid
    bad = {**_SECTION, "recommended_gate_kind": v2.REC_ADVANCE}
    assert mi.validate_v2_morning_section(bad)["valid"] is False
    bad2 = {**_SECTION, "do_not_proceed_to_labels": False}
    assert mi.validate_v2_morning_section(bad2)["valid"] is False


# ---- (3) explicit safety-lock display + locked channels --------------------

def test_safety_lock_display_and_locks():
    disp = " || ".join(_SECTION["danger_locks_display"]).lower()
    for must in ("no live trading", "no paper trading", "no broker/order",
                 "signum", "mcp", "hyperliquid", "credentials", "no claude routines",
                 "no bot edits", "no scheduler", "no auto commit"):
        assert must in disp, must
    dl = _SECTION["danger_locks"]
    for k in ("live_trading_locked", "paper_trading_locked", "broker_locked",
              "signum_locked", "mcp_locked", "hyperliquid_locked", "scheduler_locked",
              "bot_edits_locked", "trades_locked", "no_automatic_commit",
              "no_automatic_push", "no_automatic_data_fetch",
              "no_automatic_candidate_promotion", "never_skips_human_gates"):
        assert dl[k] is True, k


# ---- renderers: markdown + html surface the V2 packet ----------------------

def test_markdown_render_includes_v2_packet():
    md = mi.render_v2_section_markdown(_SECTION)
    assert "Automation V2" in md
    assert "DATA_NOT_READY" in md
    assert "HUMAN_STAGE_FROZEN_TREND_RADAR_GC_DETECTOR_DATASET" in md
    assert "DO NOT proceed to labels" in md
    assert "no live trading" in md and "no Signum" in md


def test_html_render_includes_v2_packet():
    html = mi.render_v2_section_html(_SECTION)
    assert "Automation V2" in html
    assert "DATA_NOT_READY" in html
    assert "HUMAN_STAGE_FROZEN_TREND_RADAR_GC_DETECTOR_DATASET" in html
    assert "do NOT proceed to labels" in html


# ---- (1)+(2) augmenters are NON-MUTATING and attach the V2 section ----------

def test_augment_morning_report_non_mutating():
    report = {"section": "autopilot_morning_report",
              "git_status_summary": dict(_GS_CLEAN),
              "what_to_do_next": "x", "autopilot_plan": {}}
    aug = mi.augment_morning_report(report, sync_info=_SYNC)
    # the original report is never mutated
    assert "automation_v2_packet" not in report
    # the augmented copy carries the section + its markdown
    assert aug["automation_v2_integrated"] is True
    assert aug["automation_v2_source_unmutated"] is True
    assert aug["automation_v2_packet"]["c22_data_not_ready"] is True
    assert "DATA_NOT_READY" in aug["automation_v2_packet_markdown"]
    # the pre-existing report keys are preserved untouched
    assert aug["what_to_do_next"] == "x"
    assert mi.validate_v2_morning_section(aug["automation_v2_packet"])["valid"] is True


def test_augment_panel_non_mutating():
    panel = {"available": True,
             "automation_readiness": {"git_status_summary": dict(_GS_CLEAN)}}
    aug = mi.augment_panel(panel, sync_info=_SYNC)
    assert "automation_v2" not in panel             # original unmutated
    assert aug["automation_v2_integrated"] is True
    assert aug["automation_v2"]["c22_data_not_ready"] is True
    assert "Automation V2" in aug["automation_v2_html"]
    assert aug["available"] is True                 # original keys preserved


def test_augment_markdown_appends_section():
    base = "# Morning report\n\nsome existing content"
    out = mi.augment_morning_report_markdown(base, _SECTION)
    assert out.startswith("# Morning report")
    assert "Automation V2" in out
    assert "HUMAN_STAGE_FROZEN_TREND_RADAR_GC_DETECTOR_DATASET" in out


# ---- regression safety: V2 bundle still read-only + unchanged --------------

def test_underlying_v2_bundle_still_read_only():
    pkt = v2.build_morning_decision_packet({
        "head": "x", "origin": "x", "ahead": 0, "behind": 0, "clean": True,
        "staged_count": 0})
    assert v2.validate_morning_decision_packet(pkt)["valid"] is True
    assert pkt["executes_nothing"] is True
    # the integration never claims to mutate the source surfaces
    assert _SECTION["mutates_source_surfaces"] is False


# ---- capability flags + module purity --------------------------------------

def test_capability_flags_all_false_and_tamper_rejected():
    for flag in mi._CAPABILITY_FLAGS_FALSE:
        assert _SECTION[flag] is False, flag
        bad = {**_SECTION, flag: True}
        assert mi.validate_v2_morning_section(bad)["valid"] is False, flag


def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(mi.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch(", "open(", "subprocess", "Popen", "urlopen"):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
              "subprocess", "websockets", "aiohttp", "schedule", "threading",
              "asyncio", "telegram", "os", "io", "shutil", "ssl", "ftplib",
              "datetime", "random", "numpy", "pandas"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned), imported & banned
    for call in ast.walk(tree):
        if isinstance(call, ast.Call):
            name = (call.func.attr if isinstance(call.func, ast.Attribute)
                    else getattr(call.func, "id", ""))
            assert name not in ("open", "exec", "eval", "compile"), name
