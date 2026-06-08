"""Tests for the Offline Strategy Factory Arc Hold Decision (Bundle 163).

The module is a pure, stdlib-only, read-only DECISION record. It resolves a single
verdict -- HOLD_ARC -- for the entire untracked OFFLINE-STRATEGY-FACTORY arc found
by Bundle 162. These tests assert: schema / label / verdict / arc status; that
every listed arc component is HELD (not adopted, not deleted, not staged, not
active); that the Phase 5 runner is flagged as the highest-risk component; that no
active registration / mission-flow wiring / JARVIS-active surfacing is allowed;
that the boundary is preserved (stage + next required action unchanged); that all
gates stay blocked/locked; that all capability flags stay False; determinism /
mutation isolation; validation; render; AST purity (only __future__ / typing, no
os / network / credential / filesystem-write capability); and the two additive
commander_2_safety allowlist entries.
"""

from __future__ import annotations

import ast
import pathlib

from sparta_commander.strategy_factory_offline_strategy_factory_arc_hold_decision import (  # noqa: E501
    ARC_ID,
    ARC_STATUS,
    CAPABILITY_FLAGS,
    DECISION_LABEL,
    DECISION_MODE,
    DECISION_SCHEMA_VERSION,
    DECISION_STATUS,
    GATE_STATES,
    MISSION_FLOW_CURRENT_STAGE,
    MISSION_FLOW_NEXT_REQUIRED_ACTION,
    PHASE5_COMPONENT_NAME,
    PHASE5_RISK,
    REQUIRED_FUTURE_ARC_LEVEL_DECISIONS,
    VERDICT,
    VERDICT_HOLD_ARC,
    build_offline_strategy_factory_arc_hold_decision,
    render_offline_strategy_factory_arc_hold_decision_markdown,
    validate_offline_strategy_factory_arc_hold_decision,
)

_BUILD = build_offline_strategy_factory_arc_hold_decision
_VALIDATE = validate_offline_strategy_factory_arc_hold_decision
_RENDER = render_offline_strategy_factory_arc_hold_decision_markdown

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
_MODPATH = (
    _REPO_ROOT
    / "sparta_commander"
    / "strategy_factory_offline_strategy_factory_arc_hold_decision.py"
)
_SAFETY_PATH = _REPO_ROOT / "sparta_commander" / "commander_2_safety.py"

_MODULE_ALLOWLIST_LINE = (
    "sparta_commander/strategy_factory_offline_strategy_factory_arc_hold_decision.py"
)
_TEST_ALLOWLIST_LINE = (
    "tests/test_strategy_factory_offline_strategy_factory_arc_hold_decision.py"
)

# The 13 arc components Bundle 162 found (by their recorded names).
_EXPECTED_COMPONENT_NAMES = {
    "strategy_factory_charter",
    "strategy_factory_idea_intake",
    "strategy_factory_source_registry",
    "strategy_factory_data_contract_gate",
    "strategy_factory_hypothesis_spec",
    "strategy_factory_backtest_readiness",
    "strategy_factory_template_registry",
    "strategy_factory_cost_slippage_registry",
    "strategy_factory_phase5_block_idea_draft",
    "strategy_factory_phase5_offline_backtest_run",
    "research_os/simulation_guard.py",
    "paired tests",
    "tests/conftest.py",
}


# --------------------------------------------------------------------------- #
# schema / identity / verdict
# --------------------------------------------------------------------------- #
def test_schema_label_mode_status():
    assert DECISION_SCHEMA_VERSION == (
        "strategy_factory_offline_strategy_factory_arc_hold_decision.v1"
    )
    assert DECISION_LABEL == (
        "Bundle 163 - Offline Strategy Factory Arc Hold Decision"
    )
    assert DECISION_MODE == "RESEARCH_ONLY"
    assert DECISION_STATUS == "READ_ONLY_DECISION_RECORD"
    assert ARC_ID == "OFFLINE-STRATEGY-FACTORY"


def test_verdict_is_hold_arc():
    assert VERDICT == VERDICT_HOLD_ARC == "HOLD_ARC"
    rec = _BUILD()
    assert rec["verdict"] == "HOLD_ARC"
    assert rec["arc_status"] == ARC_STATUS == "LOCAL_ONLY_UNTRACKED_HELD"


# --------------------------------------------------------------------------- #
# all arc components held
# --------------------------------------------------------------------------- #
def test_all_listed_arc_components_present_and_held():
    rec = _BUILD()
    names = {c["name"] for c in rec["components"]}
    assert names == _EXPECTED_COMPONENT_NAMES
    assert rec["component_count"] == len(rec["components"]) == 13
    for c in rec["components"]:
        assert c["held"] is True, c["name"]
        assert c["adopt_individually"] is False, c["name"]
        assert c["delete_individually"] is False, c["name"]
        assert c["staged"] is False, c["name"]
        assert c["active"] is False, c["name"]
        assert c["wired_into_mission_flow"] is False, c["name"]
        assert c["surfaced_in_jarvis_active"] is False, c["name"]
        assert c["status"] == "LOCAL_ONLY_UNTRACKED_HELD", c["name"]


def test_phase5_runner_flagged_highest_risk():
    rec = _BUILD()
    assert rec["phase5_component"] == PHASE5_COMPONENT_NAME
    assert rec["phase5_risk"] == PHASE5_RISK == (
        "BACKTEST_AND_OHLCV_READING_PRESENT_BUT_NOT_ADOPTED"
    )
    phase5 = [c for c in rec["components"]
              if c["name"] == PHASE5_COMPONENT_NAME]
    assert len(phase5) == 1
    p = phase5[0]
    assert p["highest_risk"] is True
    assert p["risk"] == PHASE5_RISK
    # exactly one component is the highest-risk one
    assert sum(bool(c.get("highest_risk")) for c in rec["components"]) == 1


# --------------------------------------------------------------------------- #
# no active registration / wiring / surfacing
# --------------------------------------------------------------------------- #
def test_no_active_registration_or_wiring_allowed():
    rec = _BUILD()
    assert rec["read_only"] is True
    assert rec["executes"] is False
    for c in rec["components"]:
        assert c["active"] is False
        assert c["wired_into_mission_flow"] is False
        assert c["surfaced_in_jarvis_active"] is False
    forbidden = " ".join(rec["what_remains_forbidden"]).lower()
    assert "wiring the arc into mission flow" in forbidden
    assert "adopting any single file" in forbidden
    assert "deleting any single file" in forbidden
    assert "staging any arc file" in forbidden


def test_required_future_decision_is_whole_arc_only():
    assert REQUIRED_FUTURE_ARC_LEVEL_DECISIONS == (
        "ADOPT_WHOLE_ARC",
        "DELETE_WHOLE_ARC",
        "IGNORE_WHOLE_ARC",
    )
    rec = _BUILD()
    assert rec["required_future_arc_level_decisions"] == [
        "ADOPT_WHOLE_ARC",
        "DELETE_WHOLE_ARC",
        "IGNORE_WHOLE_ARC",
    ]


# --------------------------------------------------------------------------- #
# boundary preserved + gates blocked/locked + flags False
# --------------------------------------------------------------------------- #
def test_no_boundary_advancement():
    rec = _BUILD()
    assert MISSION_FLOW_CURRENT_STAGE == (
        "HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION_REQUIRED"
    )
    assert MISSION_FLOW_NEXT_REQUIRED_ACTION == (
        "HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION"
    )
    assert rec["stage"] == MISSION_FLOW_CURRENT_STAGE
    assert rec["next_gate"] == MISSION_FLOW_CURRENT_STAGE
    assert rec["next_required_action"] == MISSION_FLOW_NEXT_REQUIRED_ACTION
    assert not rec["next_required_action"].startswith("BUILD_")


def test_all_gates_blocked_locked():
    rec = _BUILD()
    assert rec["gate_states"] == {
        "real_data_qa": "BLOCKED",
        "baseline_backtest": "BLOCKED",
        "paper_trading_gate": "LOCKED",
        "micro_live_gate": "LOCKED",
    }
    assert GATE_STATES["real_data_qa"] == "BLOCKED"
    assert GATE_STATES["baseline_backtest"] == "BLOCKED"
    assert GATE_STATES["paper_trading_gate"] == "LOCKED"
    assert GATE_STATES["micro_live_gate"] == "LOCKED"


def test_all_capability_flags_false():
    rec = _BUILD()
    assert len(CAPABILITY_FLAGS) == len(set(CAPABILITY_FLAGS))
    for flag in CAPABILITY_FLAGS:
        assert rec[flag] is False, flag
    # the adopt/delete/stage/wire/surface/advance locks are explicitly present
    for must in (
        "adopts_any_arc_file",
        "deletes_any_arc_file",
        "stages_any_arc_file",
        "wires_arc_into_mission_flow",
        "surfaces_arc_in_jarvis_active",
        "advances_boundary",
    ):
        assert must in CAPABILITY_FLAGS
        assert rec[must] is False


def test_reason_contains_safety_phrasing():
    rec = _BUILD()
    reason = rec["reason"].lower()
    assert "authorizes nothing" in reason
    assert "executes nothing" in reason
    assert "purely additive read-only decision metadata" in reason
    assert "never an unlock of real_data_qa" in reason


# --------------------------------------------------------------------------- #
# determinism / mutation isolation / validate / render
# --------------------------------------------------------------------------- #
def test_deterministic_and_mutation_isolated():
    assert _BUILD() == _BUILD()
    rec = _BUILD()
    rec["verdict"] = "TAMPERED"
    rec["executes"] = True
    rec["components"][0]["held"] = False
    rec["components"].append({"name": "TAMPERED"})
    rec["gate_states"]["real_data_qa"] = "OPEN"
    fresh = _BUILD()
    assert fresh["verdict"] == "HOLD_ARC"
    assert fresh["executes"] is False
    assert all(c["held"] is True for c in fresh["components"])
    assert len(fresh["components"]) == 13
    assert fresh["gate_states"]["real_data_qa"] == "BLOCKED"


def test_validate_accepts_built_record():
    assert _VALIDATE(_BUILD()) is True


def test_validate_rejects_tampered_records():
    bad = _BUILD()
    bad["verdict"] = "ADOPT_WHOLE_ARC"
    assert _VALIDATE(bad) is False

    bad2 = _BUILD()
    bad2["executes"] = True
    assert _VALIDATE(bad2) is False

    bad3 = _BUILD()
    bad3["stage"] = "SOMETHING_ELSE"
    assert _VALIDATE(bad3) is False

    bad4 = _BUILD()
    bad4["components"][0]["adopt_individually"] = True
    assert _VALIDATE(bad4) is False

    bad5 = _BUILD()
    for c in bad5["components"]:
        if c["name"] == PHASE5_COMPONENT_NAME:
            c["highest_risk"] = False
    assert _VALIDATE(bad5) is False

    assert _VALIDATE({}) is False
    assert _VALIDATE("nope") is False


def test_render_markdown_is_safe_text():
    md = _RENDER()
    assert "Offline Strategy Factory Arc Hold Decision" in md
    assert "HOLD_ARC" in md
    assert "HIGHEST RISK" in md
    assert "ADOPT_WHOLE_ARC" in md
    assert "real_data_qa: BLOCKED" in md
    # render takes a prebuilt record too
    assert _RENDER(_BUILD()) == md


# --------------------------------------------------------------------------- #
# AST purity / no I/O capability
# --------------------------------------------------------------------------- #
_ALLOWED_IMPORT_ROOTS = {"__future__", "typing"}
_FORBIDDEN_MODULE_TOKENS = {
    "os",
    "sys",
    "subprocess",
    "socket",
    "shutil",
    "pathlib",
    "requests",
    "http",
    "urllib",
    "importlib",
    "pandas",
    "numpy",
    "ccxt",
    "databento",
    "dotenv",
    "datetime",
    "time",
    "random",
    "pickle",
    "sqlite3",
    "csv",
    "json",
    "hashlib",
}


def _module_ast():
    return ast.parse(_MODPATH.read_text(encoding="utf-8"))


def test_module_is_pure_stdlib_within_allowed_roots():
    for node in ast.walk(_module_ast()):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] in _ALLOWED_IMPORT_ROOTS, (
                    alias.name
                )
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            assert root in _ALLOWED_IMPORT_ROOTS, node.module


def test_module_imports_no_fs_network_or_credential_modules():
    imported_roots = set()
    for node in ast.walk(_module_ast()):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            imported_roots.add((node.module or "").split(".")[0])
    assert not (imported_roots & _FORBIDDEN_MODULE_TOKENS), (
        imported_roots & _FORBIDDEN_MODULE_TOKENS
    )


def test_module_never_reads_environment():
    for node in ast.walk(_module_ast()):
        if isinstance(node, ast.Attribute):
            assert node.attr not in {"environ", "getenv", "environb"}, node.attr


def test_module_has_no_eval_exec_import_dunder():
    for node in ast.walk(_module_ast()):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id not in {
                "eval", "exec", "compile", "__import__", "input"
            }


def test_module_has_no_filesystem_write_capability():
    src = _MODPATH.read_text(encoding="utf-8")
    assert "open(" not in src
    assert ".write_text(" not in src
    assert ".write_bytes(" not in src
    assert "write_json(" not in src
    for node in ast.walk(_module_ast()):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                assert node.func.id != "open"
            if isinstance(node.func, ast.Attribute):
                assert node.func.attr not in {
                    "write_text", "write_bytes", "write_json"
                }


def test_building_writes_no_files(tmp_path):
    before = set(tmp_path.iterdir())
    _BUILD()
    _RENDER()
    _VALIDATE(_BUILD())
    after = set(tmp_path.iterdir())
    assert before == after


# --------------------------------------------------------------------------- #
# commander_2_safety allowlist (exactly two additive lines)
# --------------------------------------------------------------------------- #
def test_commander_safety_allowlist_includes_the_two_additive_entries():
    from sparta_commander.commander_2_safety import (
        COMMANDER_2_MODULES,
        COMMANDER_2_TESTS,
    )

    assert _MODULE_ALLOWLIST_LINE in COMMANDER_2_MODULES
    assert _TEST_ALLOWLIST_LINE in COMMANDER_2_TESTS
    assert COMMANDER_2_MODULES.count(_MODULE_ALLOWLIST_LINE) == 1
    assert COMMANDER_2_TESTS.count(_TEST_ALLOWLIST_LINE) == 1


def test_commander_safety_only_two_new_lines_for_this_module():
    src = _SAFETY_PATH.read_text(encoding="utf-8")
    assert src.count(_MODULE_ALLOWLIST_LINE + '"') == 1
    assert src.count(_TEST_ALLOWLIST_LINE + '"') == 1
