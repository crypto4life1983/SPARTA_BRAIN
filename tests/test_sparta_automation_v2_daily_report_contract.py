"""Tests for the SPARTA Automation V2 -- Daily Decision Report bundle (contract + runner).

Verifies the read-only daily report content builder and the read-only runner: the report
includes the Automation V2 morning packet; surfaces C22 DATA_NOT_READY with the dataset-
staging recommendation (never labels, never fabricate data); shows the C1-C21 (26) ledger,
C21 rejected, no active candidate, and every dangerous channel locked; flags an unsafe git
state (dirty/staged -> RESOLVE_REPO) while still refusing to advance to labels; is
deterministic (the pinned sample markdown SHA256); targets the GITIGNORED reports artifact
path (never committed); and the runner is read-only (only allow-listed git READ
subcommands, no commit/push/fetch/add, no network, no scheduler install/trigger), writing
only into the approved gitignored path with side effects confined to main()."""
from __future__ import annotations

import ast
import hashlib
from pathlib import Path

import sparta_commander.sparta_automation_v2_daily_report_contract as dr


_CLEAN = {"head": "0609d626348fcaf96060144e2384001ee055deec",
          "origin": "0609d626348fcaf96060144e2384001ee055deec",
          "ahead": 0, "behind": 0, "clean": True, "staged_count": 0,
          "untracked_clutter_present": True, "untracked_clutter_ignored_by_path": True}

_R = dr.build_daily_report(_CLEAN, "2026-06-20T00:00:00Z")

_RUNNER = Path(dr.__file__).resolve().parents[1] / "tools" \
    / "sparta_automation_v2_daily_report_once.py"


# ---- core: report builds + validates ---------------------------------------

def test_report_builds_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_read_only_report"] is True
    assert _R["recommends_only"] is True
    assert _R["executes_nothing"] is True
    assert dr.validate_daily_report(_R)["valid"] is True


# ---- (1)+(2) report includes the Automation V2 packet + current state ------

def test_report_includes_v2_packet_and_current_state():
    assert _R["run_timestamp_utc"] == "2026-06-20T00:00:00Z"
    assert _R["git_head"] == "0609d626348fcaf96060144e2384001ee055deec"
    assert _R["in_sync"] is True
    assert _R["rejected_ledger_count"] == 26
    assert _R["last_rejected_candidate"] == "C21"
    assert _R["lane_active_candidate"] is None
    assert _R["c22_data_not_ready"] is True
    assert _R["last_verdict"] == "DATA_NOT_READY"
    assert "DATA_NOT_READY" in _R["blockers"]
    assert _R["evidence_chain_valid"] is True
    # the embedded V2 section is present + valid
    import sparta_commander.sparta_automation_v2_morning_integration_contract as mi
    assert mi.validate_v2_morning_section(_R["v2_morning_section"])["valid"] is True


# ---- (2) recommends dataset staging for C22, never labels ------------------

def test_recommends_dataset_staging_not_labels():
    assert _R["recommended_gate_kind"] == "RECOMMEND_DATASET_STAGING"
    assert _R["do_not_proceed_to_labels"] is True
    assert _R["do_not_fabricate_data"] is True
    assert _R["recommends_advancing_to_labels_while_blocked"] is False
    assert _R["next_human_approval_token"] == (
        "HUMAN_STAGE_FROZEN_TREND_RADAR_GC_DETECTOR_DATASET_THEN_REAUTHORISE_C22_LABELS")
    # tamper: flip to advance while blocked (repo safe) -> invalid
    bad = {**_R, "recommended_gate_kind": "RECOMMEND_ADVANCE_HUMAN_DECISION"}
    assert dr.validate_daily_report(bad)["valid"] is False
    bad2 = {**_R, "do_not_proceed_to_labels": False}
    assert dr.validate_daily_report(bad2)["valid"] is False


# ---- (1) deterministic: pinned sample markdown SHA256 ----------------------

def test_sample_report_deterministic_sha_pinned():
    md = dr.render_daily_report_markdown(dr.build_sample_report())
    sha = hashlib.sha256(md.encode("utf-8")).hexdigest()
    assert sha == dr.SAMPLE_MARKDOWN_SHA256
    # building twice with the same inputs is byte-identical (pure)
    md2 = dr.render_daily_report_markdown(
        dr.build_daily_report(dict(dr.SAMPLE_REPO_STATE), dr.SAMPLE_TIMESTAMP))
    assert md == md2


# ---- report flags unsafe git state (dirty/staged) --------------------------

def test_report_flags_unsafe_git_state():
    dirty = dr.build_daily_report(
        {"head": "x", "origin": "x", "ahead": 0, "behind": 0, "clean": False,
         "staged_count": 2, "untracked_clutter_present": True}, "2026-06-20T00:00:00Z")
    assert dirty["git_safe_to_automate"] is False
    assert "tracked_tree_dirty" in dirty["git_blockers"]
    assert "staged_files_present" in dirty["git_blockers"]
    assert dirty["recommended_gate_kind"] == "RECOMMEND_RESOLVE_REPO_BEFORE_AUTOMATION"
    # even while flagging unsafe git, it must NOT advance to labels + still says staging
    assert dirty["recommends_advancing_to_labels_while_blocked"] is False
    assert dirty["do_not_proceed_to_labels"] is True
    assert "STAGE_FROZEN_TREND_RADAR_GC_DETECTOR_DATASET" in (
        dirty["next_human_approval_token"])
    assert dr.validate_daily_report(dirty)["valid"] is True


# ---- (3) artifact targets the gitignored reports path, never committed -----

def test_artifact_path_gitignored_and_not_committed():
    art = _R["artifact"]
    assert art["dir"] == "reports/automation_v2_daily"
    assert art["dir"].startswith("reports/")
    assert art["gitignored"] is True
    assert art["committed_to_git"] is False
    assert dr.ARTIFACT_IS_GITIGNORED is True
    # the actual .gitignore covers the path
    gi = (Path(dr.__file__).resolve().parents[1] / ".gitignore").read_text(
        encoding="utf-8")
    assert "reports/automation_v2_daily/" in gi


# ---- (3)+(4) safety: danger locks + runner safety, no dangerous capability -

def test_danger_locks_and_runner_safety_displayed():
    disp = " || ".join(_R["danger_locks_display"]).lower()
    for must in ("no live trading", "no paper trading", "no broker/order",
                 "signum", "mcp", "hyperliquid", "no scheduler", "no auto commit"):
        assert must in disp, must
    rsf = _R["runner_safety"]
    for k in ("read_only", "no_git_commit", "no_git_push", "no_git_fetch",
              "no_data_fetch", "no_scheduler_install", "no_scheduler_trigger",
              "writes_only_to_gitignored_reports_path", "artifact_not_committed_to_git"):
        assert rsf[k] is True, k
    rsd = " || ".join(_R["runner_safety_display"]).lower()
    assert "no git commit" in rsd and "no scheduler install or trigger" in rsd


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in dr._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert dr.validate_daily_report(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key


# ---- (4) RUNNER purity: read-only, allow-listed git reads, no scheduler -----

def _runner_src() -> str:
    return _RUNNER.read_text(encoding="utf-8")


def test_runner_exists_and_has_main_guard():
    assert _RUNNER.exists()
    src = _runner_src()
    assert 'if __name__ == "__main__":' in src


def test_runner_only_allowlisted_read_only_git():
    src = _runner_src()
    # the allow-list of git READ subcommands is declared + enforced
    assert "GIT_READ_ALLOWLIST" in src
    for read_cmd in ('"rev-parse"', '"symbolic-ref"', '"rev-list"', '"status"'):
        assert read_cmd in src, read_cmd
    assert "refused_non_read_only_git_command" in src
    # NO mutating git subcommand is ever quoted as a command argument
    for bad in ('"commit"', '"push"', '"fetch"', '"add"', '"pull"', '"merge"',
                '"checkout"', '"reset"', '"rm"', '"git clean"'):
        assert bad not in src, bad
    # every subprocess.run call is inside the _git_read helper
    tree = ast.parse(src)
    gitread = next((n for n in tree.body
                    if isinstance(n, ast.FunctionDef) and n.name == "_git_read"), None)
    assert gitread is not None
    gr_lines = set(range(gitread.lineno, (gitread.end_lineno or gitread.lineno) + 1))
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            seg = ast.get_source_segment(src, node) or ""
            if "subprocess.run" in seg:
                assert node.lineno in gr_lines, node.lineno


def test_runner_no_network_no_scheduler_no_trading():
    src = _runner_src()
    for tok in ("import requests", "from requests", "import urllib", "import http",
                "import socket", "import ssl", "import ccxt", "import websockets",
                "import aiohttp", "urlopen", "api.binance", "fapi.binance",
                "schtasks", "Register-ScheduledTask", "crontab", "schedule.every",
                "os.environ", "getenv", "place_order", "create_order", "signum",
                "hyperliquid", "mcp_"):
        assert tok not in src, tok


def test_runner_writes_only_into_approved_gitignored_path():
    src = _runner_src()
    assert 'reports" / "automation_v2_daily"' in src
    assert "OUT_DIR" in src
    # side effects (mkdir / file writes / json.dump) only inside main()
    tree = ast.parse(src)
    main_fn = next((n for n in tree.body
                    if isinstance(n, ast.FunctionDef) and n.name == "main"), None)
    assert main_fn is not None
    main_lines = set(range(main_fn.lineno,
                           (main_fn.end_lineno or main_fn.lineno) + 1))
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            seg = ast.get_source_segment(src, node) or ""
            write_open = "open(" in seg and ('"w"' in seg or "'w'" in seg)
            if "mkdir" in seg or "json.dump" in seg or write_open:
                assert node.lineno in main_lines, (seg[:40], node.lineno)


# ---- module purity (the pure contract) -------------------------------------

def test_contract_module_purity():
    src = open(dr.__file__, encoding="utf-8").read()
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
