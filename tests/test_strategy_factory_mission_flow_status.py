"""Tests for the Strategy Factory Mission Flow status adapter (Block 71).

The adapter is a PURE, stdlib-only, read-only display/status feed for the JARVIS
"Mission Flow" panel. It maps where the Strategy Factory backbone stands as of
Bundle 49 (Crypto-D1 research-only dry-run preview contract complete) and proves
it executes nothing and unlocks nothing real.

Coverage:
- stable output schema (keys + types)
- mode RESEARCH_ONLY, read_only True, executes False, human_approval_required True
- Bundles 42-49 recognized complete; next stage is a research-only dry-run-review
  paper contract (to be BUILT, not real execution)
- Real Data QA blocked, Baseline Backtest blocked
- Paper Trading Gate locked, Micro-Live Gate locked + never automated
- no stage unlocks real data / QA / baseline / backtest / paper / live /
  broker / exchange / automation / runtime writes / registry writes /
  dashboard writes
- deterministic repeated calls; mutation-isolated copies
- no IO required for default status (stdlib import-root + forbidden-surface audit)
- commander_2_safety allowlist includes the new module + test paths
"""

from __future__ import annotations

import ast
import pathlib

from sparta_commander.strategy_factory_mission_flow_status import (
    MISSION_FLOW_VERSION,
    MISSION_FLOW_MODE,
    MISSION_FLOW_SAFETY_POSTURE,
    STATE_PASSED,
    STATE_COMPLETE,
    STATE_CURRENT,
    STATE_NEXT,
    STATE_BLOCKED,
    STATE_LOCKED,
    CURRENT_STAGE,
    LATEST_COMPLETED_BUNDLE,
    NEXT_REQUIRED_ACTION,
    human_workflow_lane,
    machine_pipeline_lane,
    blocked_gates,
    safety_flags,
    get_mission_flow_status,
)

_MODPATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "sparta_commander"
    / "strategy_factory_mission_flow_status.py"
)
_SAFETY_PATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "sparta_commander"
    / "commander_2_safety.py"
)


# --- 1: stable top-level schema --------------------------------------------

def test_status_schema_is_stable():
    s = get_mission_flow_status()
    assert set(s.keys()) == {
        "mission_flow_version",
        "mode",
        "read_only",
        "executes",
        "human_approval_required",
        "current_stage",
        "latest_completed_bundle",
        "next_required_action",
        "safety_posture",
        "human_workflow",
        "machine_pipeline",
        "blocked_gates",
        "safety",
    }
    assert s["mission_flow_version"] == MISSION_FLOW_VERSION == "v1"
    assert isinstance(s["human_workflow"], list)
    assert isinstance(s["machine_pipeline"], list)
    assert isinstance(s["blocked_gates"], list)
    assert isinstance(s["safety"], dict)
    assert isinstance(s["safety_posture"], dict)


def test_lane_rows_have_stable_keys():
    for lane in (human_workflow_lane(), machine_pipeline_lane(), blocked_gates()):
        assert lane, "lane must not be empty"
        for row in lane:
            assert set(row.keys()) == {"id", "label", "state", "reason"}
            for v in row.values():
                assert isinstance(v, str) and v


# --- 2: posture -------------------------------------------------------------

def test_mode_and_posture_flags():
    s = get_mission_flow_status()
    assert s["mode"] == MISSION_FLOW_MODE == "RESEARCH_ONLY"
    assert s["read_only"] is True
    assert s["executes"] is False
    assert s["human_approval_required"] is True


def test_safety_posture_all_false_except_gates():
    assert MISSION_FLOW_SAFETY_POSTURE["mode"] == "RESEARCH_ONLY"
    assert MISSION_FLOW_SAFETY_POSTURE["read_only"] is True
    assert MISSION_FLOW_SAFETY_POSTURE["human_approval_required"] is True
    for k, v in MISSION_FLOW_SAFETY_POSTURE.items():
        if k in ("mode", "read_only", "human_approval_required"):
            continue
        assert v is False, f"posture flag {k} must be False"


def test_safety_flags_all_false():
    flags = safety_flags()
    assert set(flags.keys()) == {
        "real_data", "qa", "baseline", "backtest", "simulation",
        "paper", "live", "broker", "exchange", "automation",
        "runtime_writes", "registry_writes", "dashboard_writes",
    }
    assert all(v is False for v in flags.values())


# --- 3: Bundles 42-48 complete; next = research-only dry-run-preview contract

def test_bundles_42_through_49_recognized_complete():
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    for stage_id in (
        "crypto_d1_acquire_decision_contract",          # Bundle 42
        "crypto_d1_source_class_contract",              # Bundle 43
        "crypto_d1_source_specification_contract",      # Bundle 44
        "crypto_d1_offline_acquisition_plan_contract",  # Bundle 45
        "crypto_d1_pre_acquisition_human_gate_contract",  # Bundle 46
        "crypto_d1_human_approved_offline_acquisition_execution_boundary_contract",  # Bundle 47  # noqa: E501
        "crypto_d1_post_boundary_research_only_next_step_contract",  # Bundle 48
        "crypto_d1_research_only_dry_run_preview_contract",  # Bundle 49
    ):
        assert pipe[stage_id]["state"] == STATE_COMPLETE, stage_id


def test_bundle45_recognized_complete():
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    row = pipe["crypto_d1_offline_acquisition_plan_contract"]
    assert row["state"] == STATE_COMPLETE
    assert "Bundle 45" in row["reason"]


def test_bundle46_recognized_complete():
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    row = pipe["crypto_d1_pre_acquisition_human_gate_contract"]
    assert row["state"] == STATE_COMPLETE
    assert "Bundle 46" in row["reason"]


def test_bundle47_recognized_complete():
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    row = pipe["crypto_d1_human_approved_offline_acquisition_execution_boundary_contract"]  # noqa: E501
    assert row["state"] == STATE_COMPLETE
    assert "Bundle 47" in row["reason"]


def test_bundle47_authorizes_nothing_executes_nothing():
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    reason = pipe["crypto_d1_human_approved_offline_acquisition_execution_boundary_contract"]["reason"].lower()  # noqa: E501
    assert "authorizes nothing" in reason
    assert "executes nothing" in reason
    # the boundary contract existing does not flip any real capability on
    assert all(v is False for v in safety_flags().values())
    assert get_mission_flow_status()["executes"] is False


def test_bundle48_recognized_complete():
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    row = pipe["crypto_d1_post_boundary_research_only_next_step_contract"]
    assert row["state"] == STATE_COMPLETE
    assert "Bundle 48" in row["reason"]
    reason = row["reason"].lower()
    assert "authorizes nothing" in reason
    assert "executes nothing" in reason


def test_bundle49_recognized_complete():
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    row = pipe["crypto_d1_research_only_dry_run_preview_contract"]
    assert row["state"] == STATE_COMPLETE
    assert "Bundle 49" in row["reason"]
    reason = row["reason"].lower()
    assert "authorizes nothing" in reason
    assert "executes nothing" in reason


def test_latest_completed_bundle_is_bundle49():
    assert "Bundle 49" in LATEST_COMPLETED_BUNDLE
    assert "Research-Only Dry-Run Preview" in LATEST_COMPLETED_BUNDLE
    assert "Contract" in LATEST_COMPLETED_BUNDLE
    assert get_mission_flow_status()["latest_completed_bundle"] == LATEST_COMPLETED_BUNDLE


def test_next_required_action_is_research_only_dry_run_review_contract():
    assert NEXT_REQUIRED_ACTION == (
        "BUILD_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_REVIEW_CONTRACT"
    )
    # it names a research-only CONTRACT to be BUILT, not real execution
    assert "RESEARCH_ONLY" in NEXT_REQUIRED_ACTION
    assert "DRY_RUN_REVIEW" in NEXT_REQUIRED_ACTION
    assert NEXT_REQUIRED_ACTION.endswith("_CONTRACT")
    for banned in ("ACQUIRE", "FETCH", "EXECUTE", "EXECUTION", "QA",
                   "BACKTEST", "BASELINE", "PAPER", "LIVE", "BROKER",
                   "EXCHANGE"):
        assert banned not in NEXT_REQUIRED_ACTION, banned
    s = get_mission_flow_status()
    assert s["next_required_action"] == NEXT_REQUIRED_ACTION
    # building the next contract still unlocks nothing real
    assert all(v is False for v in safety_flags().values())
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    nxt = pipe["crypto_d1_research_only_dry_run_review_contract"]
    assert nxt["state"] == STATE_NEXT


def test_current_stage_is_after_bundle49():
    assert CURRENT_STAGE == (
        "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_REVIEW_CONTRACT_REQUIRED"
    )
    assert "RESEARCH_ONLY" in CURRENT_STAGE
    assert "DRY_RUN_REVIEW" in CURRENT_STAGE
    assert get_mission_flow_status()["current_stage"] == CURRENT_STAGE
    human = {r["id"]: r for r in human_workflow_lane()}
    assert human["operator_review_before_real_strategy_intake"]["state"] == STATE_CURRENT


def test_backbone_and_fake_lane_complete():
    human = {r["id"]: r for r in human_workflow_lane()}
    assert human["backbone_build"]["state"] == STATE_COMPLETE
    assert human["fake_lane"]["state"] == STATE_COMPLETE
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    assert pipe["fake_lane_closure"]["state"] == STATE_COMPLETE
    assert pipe["crypto_d1_intake_reconciliation"]["state"] == STATE_COMPLETE


# --- 4: downstream gates blocked / locked ----------------------------------

def test_real_data_qa_blocked():
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    assert pipe["real_data_qa"]["state"] == STATE_BLOCKED
    gates = {r["id"]: r for r in blocked_gates()}
    assert gates["real_data_qa"]["state"] == STATE_BLOCKED


def test_baseline_backtest_blocked():
    pipe = {r["id"]: r for r in machine_pipeline_lane()}
    assert pipe["baseline_backtest"]["state"] == STATE_BLOCKED
    gates = {r["id"]: r for r in blocked_gates()}
    assert gates["baseline_backtest"]["state"] == STATE_BLOCKED


def test_paper_trading_gate_locked():
    gates = {r["id"]: r for r in blocked_gates()}
    assert gates["paper_trading_gate"]["state"] == STATE_LOCKED
    assert "human approval" in gates["paper_trading_gate"]["reason"].lower()


def test_micro_live_gate_locked_never_automated():
    gates = {r["id"]: r for r in blocked_gates()}
    assert gates["micro_live_gate"]["state"] == STATE_LOCKED
    assert "never automated" in gates["micro_live_gate"]["reason"].lower()


def test_real_strategy_intake_blocked():
    human = {r["id"]: r for r in human_workflow_lane()}
    assert human["real_strategy_intake"]["state"] == STATE_BLOCKED


# --- 5: no stage unlocks anything real -------------------------------------

def test_no_stage_state_is_an_execution_signal():
    allowed_states = {
        STATE_PASSED, STATE_COMPLETE, STATE_CURRENT,
        STATE_NEXT, STATE_BLOCKED, STATE_LOCKED,
    }
    s = get_mission_flow_status()
    for lane in (s["human_workflow"], s["machine_pipeline"], s["blocked_gates"]):
        for row in lane:
            assert row["state"] in allowed_states, row["state"]


def test_no_real_capability_marked_unlocked():
    # Every real-world capability flag must stay False regardless of how the
    # snapshot is read; reaching any mapped stage unlocks nothing real.
    assert all(v is False for v in safety_flags().values())
    assert get_mission_flow_status()["executes"] is False


# --- 6: determinism + mutation isolation -----------------------------------

def test_repeated_calls_are_identical():
    assert get_mission_flow_status() == get_mission_flow_status()
    assert human_workflow_lane() == human_workflow_lane()
    assert machine_pipeline_lane() == machine_pipeline_lane()
    assert blocked_gates() == blocked_gates()
    assert safety_flags() == safety_flags()


def test_returned_structures_are_mutation_isolated():
    a = get_mission_flow_status()
    a["mode"] = "TAMPERED"
    a["human_workflow"][0]["state"] = "TAMPERED"
    a["safety"]["live"] = True
    b = get_mission_flow_status()
    assert b["mode"] == "RESEARCH_ONLY"
    assert b["human_workflow"][0]["state"] != "TAMPERED"
    assert b["safety"]["live"] is False
    # module-level posture constant is also protected
    safety_flags()["broker"] = True
    assert safety_flags()["broker"] is False


# --- 7: pure stdlib import-root audit --------------------------------------

def test_import_roots_are_allowed_only():
    src = _MODPATH.read_text(encoding="utf-8")
    roots: set[str] = set()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    allowed = {"__future__", "typing", "sparta_commander"}
    assert roots <= allowed, f"unexpected import roots: {sorted(roots - allowed)}"
    for banned in ("os", "sys", "subprocess", "socket", "requests",
                   "urllib", "pathlib", "json", "http", "asyncio",
                   "datetime", "time", "random", "glob", "importlib",
                   "shutil", "io"):
        assert banned not in roots, f"banned import root present: {banned}"


# --- 8: forbidden-surface audit (no IO / network / exec / control) ---------

def test_no_forbidden_call_surface():
    src = _MODPATH.read_text(encoding="utf-8")
    forbidden = (
        "open(", "write_text(", "write_bytes(", ".write(", "read_text(",
        "read_bytes(", ".read(", "json.dump(", "json.load(",
        "import subprocess", "from subprocess", "Popen", "os.system",
        "os.listdir", "os.scandir", "os.walk", "listdir(", "scandir(",
        "glob(", "iglob(", "import socket", "socket.socket", "urllib",
        "requests", "httpx", "http.client", "asyncio", "place_order",
        "submit_order", "create_order", "cancel_order", "ccxt", "freqtrade",
        "paper_trade", "live_trade", "autopilot(", ".upload(", "datetime.",
        "time.time(", "random.", "subprocess.run", "check_output",
        "importlib", "__import__", "eval(", "exec(", "compile(",
    )
    hits = [tok for tok in forbidden if tok in src]
    assert hits == [], f"forbidden surface tokens present: {hits}"


def test_no_filesystem_surface():
    src = _MODPATH.read_text(encoding="utf-8")
    for tok in ("open(", ".write(", ".read(", "write_text(", "read_text(",
                "write_bytes(", "read_bytes(", "Path(", "pathlib"):
        assert tok not in src, tok


# --- 9: commander_2_safety allowlist ---------------------------------------

def test_commander_2_safety_allowlist_includes_new_paths():
    src = _SAFETY_PATH.read_text(encoding="utf-8")
    assert '"sparta_commander/strategy_factory_mission_flow_status.py"' in src
    assert '"tests/test_strategy_factory_mission_flow_status.py"' in src
