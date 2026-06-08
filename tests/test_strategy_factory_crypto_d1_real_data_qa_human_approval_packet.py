"""Tests for the Crypto-D1 Real Data QA Boundary Decision Human Approval Packet
(Block 155).

The module is a pure, stdlib-only, read-only DECISION-BRIEFING packet. It states
that the Crypto-D1 chain is parked at the human-controlled real data QA boundary,
confirms the read-only provider / adapter / autopilot stack (Blocks 152 / 153 /
154) is shipped / registered / reflected, names what a SEPARATE future human
approval would permit, and names what stays forbidden. It authorizes nothing,
unlocks nothing, and executes nothing.

These tests assert: schema / label / mode / status; the parked mission-flow truth
synced against the live status module; the registered Block 152 label synced
against the live status module; prerequisite-block confirmation; the
what-approval-would-permit and what-remains-forbidden sections; gate states
BLOCKED / LOCKED; every capability flag False; forbidden-flag inputs marking the
packet unsafe; determinism / mutation isolation; no trade language; no secret
values; validation; render; AST purity (only typing / sparta_commander roots, no
os / network / credential modules, no filesystem-write capability); and the two
additive commander_2_safety allowlist entries.
"""

from __future__ import annotations

import ast
import pathlib

from sparta_commander.strategy_factory_crypto_d1_real_data_qa_human_approval_packet import (  # noqa: E501
    DEFAULT_PACKET_INPUT,
    MISSION_FLOW_CURRENT_STAGE,
    MISSION_FLOW_NEXT_REQUIRED_ACTION,
    PACKET_CORE_RULE,
    PACKET_FORBIDDEN_FLAGS,
    PACKET_FORBIDDEN_TRADE_TERMS,
    PACKET_LABEL,
    PACKET_MODE,
    PACKET_SAFETY_POSTURE,
    PACKET_SCHEMA_VERSION,
    PACKET_STATUS,
    PREREQUISITE_BLOCKS,
    PREREQUISITE_OVERNIGHT_RESEARCH_AUTOPILOT_CONTROLLER_LABEL,
    WHAT_HUMAN_APPROVAL_WOULD_PERMIT,
    WHAT_REMAINS_FORBIDDEN,
    build_real_data_qa_boundary_decision_human_approval_packet,
    render_real_data_qa_boundary_decision_human_approval_packet_markdown,
    validate_real_data_qa_boundary_decision_human_approval_packet,
)

_BUILD = build_real_data_qa_boundary_decision_human_approval_packet
_VALIDATE = validate_real_data_qa_boundary_decision_human_approval_packet
_RENDER = render_real_data_qa_boundary_decision_human_approval_packet_markdown

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
_MODPATH = (
    _REPO_ROOT
    / "sparta_commander"
    / "strategy_factory_crypto_d1_real_data_qa_human_approval_packet.py"
)
_SAFETY_PATH = _REPO_ROOT / "sparta_commander" / "commander_2_safety.py"

_MODULE_ALLOWLIST_LINE = (
    "sparta_commander/strategy_factory_crypto_d1_real_data_qa_human_approval_packet.py"
)
_TEST_ALLOWLIST_LINE = (
    "tests/test_strategy_factory_crypto_d1_real_data_qa_human_approval_packet.py"
)


# --------------------------------------------------------------------------- #
# schema / identity
# --------------------------------------------------------------------------- #
def test_schema_label_mode_status():
    assert PACKET_SCHEMA_VERSION == (
        "strategy_factory_crypto_d1_real_data_qa_human_approval_packet.v1"
    )
    assert PACKET_LABEL == (
        "Block 155 - Crypto-D1 Real Data QA Boundary Decision Human Approval Packet"
    )
    assert PACKET_MODE == "RESEARCH_ONLY"
    assert PACKET_STATUS == "HUMAN_APPROVAL_PACKET_ONLY"


def test_build_carries_identity():
    p = _BUILD()
    assert p["schema_version"] == PACKET_SCHEMA_VERSION
    assert p["label"] == PACKET_LABEL
    assert p["mode"] == PACKET_MODE
    assert p["status"] == PACKET_STATUS
    assert p["core_rule"] == PACKET_CORE_RULE


# --------------------------------------------------------------------------- #
# mission-flow truth synced against the live status module
# --------------------------------------------------------------------------- #
def test_parked_mission_flow_matches_live_status_module():
    from sparta_commander import strategy_factory_mission_flow_status as status

    assert MISSION_FLOW_CURRENT_STAGE == status.CURRENT_STAGE
    assert MISSION_FLOW_NEXT_REQUIRED_ACTION == status.NEXT_REQUIRED_ACTION
    assert (
        MISSION_FLOW_CURRENT_STAGE
        == "HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION_REQUIRED"
    )
    assert (
        MISSION_FLOW_NEXT_REQUIRED_ACTION
        == "HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION"
    )


def test_prerequisite_controller_label_matches_live_status_module():
    from sparta_commander import strategy_factory_mission_flow_status as status

    assert (
        PREREQUISITE_OVERNIGHT_RESEARCH_AUTOPILOT_CONTROLLER_LABEL
        == status.LATEST_COMPLETED_OVERNIGHT_RESEARCH_AUTOPILOT_CONTROLLER
    )


def test_build_anchors_parked_stage():
    p = _BUILD()
    assert p["mission_flow_current_stage"] == MISSION_FLOW_CURRENT_STAGE
    assert p["mission_flow_next_required_action"] == MISSION_FLOW_NEXT_REQUIRED_ACTION
    assert p["mission_flow_aligned"] is True
    bd = p["boundary_decision"]
    assert bd["parked_stage"] == MISSION_FLOW_CURRENT_STAGE
    assert bd["parked_next_required_action"] == MISSION_FLOW_NEXT_REQUIRED_ACTION


# --------------------------------------------------------------------------- #
# prerequisite confirmation (Blocks 152 / 153 / 154)
# --------------------------------------------------------------------------- #
def test_prerequisites_confirmed_shipped_registered_reflected():
    p = _BUILD()
    assert p["prerequisite_block_152_shipped"] is True
    assert p["prerequisite_block_153_registered"] is True
    assert p["prerequisite_block_154_reflected"] is True


def test_prerequisite_blocks_cover_152_153_154():
    p = _BUILD()
    blocks = p["boundary_decision"]["prerequisite_blocks"]
    assert [b["block"] for b in blocks] == ["Block 152", "Block 153", "Block 154"]
    assert [b["state"] for b in blocks] == ["shipped", "registered", "reflected"]
    assert len(blocks) == len(PREREQUISITE_BLOCKS)
    for b in blocks:
        assert set(b) == {"block", "state", "description"}
        assert isinstance(b["description"], str) and b["description"].strip()


# --------------------------------------------------------------------------- #
# what approval would permit / what remains forbidden
# --------------------------------------------------------------------------- #
def test_what_approval_would_permit_present_and_narrow():
    p = _BUILD()
    permit = p["boundary_decision"]["what_human_approval_would_permit"]
    assert permit == list(WHAT_HUMAN_APPROVAL_WOULD_PERMIT)
    assert len(permit) >= 1
    blob = " ".join(permit).lower()
    # what approval would permit is strictly read-only QA PLANNING.
    assert "read-only" in blob
    assert "plan" in blob


def test_what_remains_forbidden_covers_the_hard_lanes():
    p = _BUILD()
    forbidden = " ".join(
        p["boundary_decision"]["what_remains_forbidden"]
    ).lower()
    assert forbidden == " ".join(WHAT_REMAINS_FORBIDDEN).lower()
    for needle in (
        "no data fetch",
        "no qa run",
        "no baseline",
        "no backtest",
        "no broker",
        "no paper",
        "no live",
        "auto-push",
        "no api",
        "no gate unlock",
    ):
        assert needle in forbidden, needle


# --------------------------------------------------------------------------- #
# gate states + capability flags
# --------------------------------------------------------------------------- #
def test_gate_states_blocked_and_locked():
    p = _BUILD()
    assert p["real_data_qa_state"] == "BLOCKED"
    assert p["baseline_backtest_state"] == "BLOCKED"
    assert p["paper_live_state"] == "LOCKED"
    assert p["real_data_qa_blocked"] is True
    assert p["baseline_backtest_blocked"] is True
    assert p["paper_trading_gate_locked"] is True
    assert p["micro_live_gate_locked"] is True


def test_no_unlock_confirmation_block_locked():
    nuc = _BUILD()["boundary_decision"]["no_unlock_confirmation"]
    assert nuc["unlocks_real_data_qa"] is False
    assert nuc["unlocks_baseline_backtest"] is False
    assert nuc["unlocks_paper_trading"] is False
    assert nuc["unlocks_micro_live"] is False
    assert nuc["real_data_qa_state"] == "BLOCKED"
    assert nuc["baseline_backtest_state"] == "BLOCKED"
    assert nuc["paper_live_state"] == "LOCKED"


def test_every_capability_flag_is_false():
    p = _BUILD()
    for flag, value in PACKET_SAFETY_POSTURE.items():
        if value is False:
            assert p.get(flag) is False, flag
    assert p["authorizes_nothing"] is True
    assert p["this_packet_authorizes_boundary_crossing"] is False
    assert p["requires_separate_future_human_approved_step"] is True
    assert p["human_decision_required"] is True
    assert p["human_approval_required"] is True


def test_safety_posture_passthrough():
    assert _BUILD()["safety_posture"] == PACKET_SAFETY_POSTURE
    # posture facts True; everything else False.
    for key in (
        "read_only",
        "research_only",
        "human_approval_packet_only",
        "human_decision_required",
        "parked_at_boundary",
    ):
        assert PACKET_SAFETY_POSTURE[key] is True
    assert PACKET_SAFETY_POSTURE["executes"] is False
    assert PACKET_SAFETY_POSTURE["activates_autopilot"] is False
    assert PACKET_SAFETY_POSTURE["performs_auto_push"] is False


# --------------------------------------------------------------------------- #
# forbidden-flag inputs mark the packet unsafe (but never unlock anything)
# --------------------------------------------------------------------------- #
def test_default_packet_is_safe():
    p = _BUILD()
    assert p["safe"] is True
    assert p["forbidden_flag_hits"] == []


def test_each_forbidden_flag_marks_unsafe():
    for flag in PACKET_FORBIDDEN_FLAGS:
        p = _BUILD({**DEFAULT_PACKET_INPUT, flag: True})
        assert p["safe"] is False, flag
        assert flag in p["forbidden_flag_hits"], flag
        # even an unsafe input never flips a gate or a capability flag.
        assert p["real_data_qa_blocked"] is True
        assert p["unlocks_real_data_qa"] is False
        assert p["authorizes_nothing"] is True


def test_mission_flow_misalignment_marks_unsafe():
    p = _BUILD({**DEFAULT_PACKET_INPUT, "mission_flow_current_stage": "SOMEWHERE_ELSE"})
    assert p["mission_flow_aligned"] is False
    assert p["safe"] is False
    # gates remain blocked regardless.
    assert p["real_data_qa_blocked"] is True


# --------------------------------------------------------------------------- #
# determinism / mutation isolation
# --------------------------------------------------------------------------- #
def test_build_is_deterministic_and_isolated():
    a = _BUILD()
    b = _BUILD()
    assert a == b
    a["boundary_decision"]["what_remains_forbidden"].append("MUTATED")
    a["safety_posture"]["executes"] = True
    c = _BUILD()
    assert c["boundary_decision"]["what_remains_forbidden"] == list(
        WHAT_REMAINS_FORBIDDEN
    )
    assert c["safety_posture"]["executes"] is False


def test_default_input_not_mutated_by_build():
    snapshot = dict(DEFAULT_PACKET_INPUT)
    _BUILD()
    assert DEFAULT_PACKET_INPUT == snapshot


# --------------------------------------------------------------------------- #
# narrative purity
# --------------------------------------------------------------------------- #
def test_narrative_has_no_trade_language():
    p = _BUILD()
    blob = " ".join(
        [
            p["operator_next_step"],
            p["packet_summary"],
            p["core_rule"],
            *p["human_operator_required_next_steps"],
        ]
    ).lower()
    tokens = set()
    word = []
    for ch in blob:
        if ch.isalnum() or ch == "_":
            word.append(ch)
        elif word:
            tokens.add("".join(word))
            word = []
    if word:
        tokens.add("".join(word))
    assert not (tokens & set(PACKET_FORBIDDEN_TRADE_TERMS))


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #
def test_validate_default_packet_is_valid():
    verdict = _VALIDATE(_BUILD())
    assert verdict["valid"] is True
    assert verdict["missing_fields"] == []
    for key, value in verdict.items():
        if key in ("valid", "missing_fields"):
            continue
        assert value is True, key


def test_validate_rejects_non_dict():
    verdict = _VALIDATE("not a packet")
    assert verdict["valid"] is False


def test_validate_rejects_tampered_gate():
    p = _BUILD()
    p["real_data_qa_blocked"] = False
    verdict = _VALIDATE(p)
    assert verdict["valid"] is False
    assert verdict["gates_locked"] is False


def test_validate_rejects_flipped_capability_flag():
    p = _BUILD()
    p["executes"] = True
    verdict = _VALIDATE(p)
    assert verdict["valid"] is False
    assert verdict["flags_false"] is False


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #
def test_render_is_deterministic_markdown():
    p = _BUILD()
    md1 = _RENDER(p)
    md2 = _RENDER(p)
    assert md1 == md2
    assert md1.startswith(
        "# Crypto-D1 Real Data QA Boundary Decision Human Approval Packet"
    )
    assert "## What Human Approval Would Permit" in md1
    assert "## What Remains Forbidden" in md1
    assert "## Prerequisite Stack (shipped / registered / reflected)" in md1
    assert "Block 152" in md1
    assert "BLOCKED" in md1
    assert "LOCKED" in md1


def test_render_handles_non_dict():
    assert _RENDER("x").startswith(
        "# Crypto-D1 Real Data QA Boundary Decision Human Approval Packet"
    )


# --------------------------------------------------------------------------- #
# AST purity
# --------------------------------------------------------------------------- #
_ALLOWED_IMPORT_ROOTS = {"__future__", "typing", "sparta_commander"}
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
}


def _module_ast():
    return ast.parse(_MODPATH.read_text(encoding="utf-8"))


def test_module_imports_are_within_allowed_roots():
    for node in ast.walk(_module_ast()):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] in _ALLOWED_IMPORT_ROOTS, alias.name
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            assert root in _ALLOWED_IMPORT_ROOTS, node.module


def test_module_imports_no_os_network_or_credential_modules():
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
            assert node.func.id not in {"eval", "exec", "compile", "__import__", "input"}


def test_module_has_no_filesystem_write_capability_of_its_own():
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
                assert node.func.attr not in {"write_text", "write_bytes", "write_json"}


def test_building_writes_no_files(tmp_path):
    before = set(tmp_path.iterdir())
    _BUILD()
    _BUILD({**DEFAULT_PACKET_INPUT, "authorizes_trading": True})
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
    assert src.count(_MODULE_ALLOWLIST_LINE) == 1
    assert src.count(_TEST_ALLOWLIST_LINE) == 1
