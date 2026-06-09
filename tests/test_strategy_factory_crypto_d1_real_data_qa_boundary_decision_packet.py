"""Tests for the Crypto-D1 Human-Controlled Real Data QA Boundary Decision Packet
(Block 170).

The module is a pure, stdlib-only, read-only OPERATOR DECISION packet. It states
that the Crypto-D1 chain is parked at the human-controlled real data QA boundary,
summarizes the boundary truth, lists completed read-only evidence, lists what is
still missing before real_data_qa could be safely considered, offers four
recommendation-only decision options, and rejects any unlock / execute / fetch /
QA / credential / write / trade option. It authorizes nothing, unlocks nothing,
and executes nothing.

These tests assert: schema / label / mode / status; the parked mission-flow truth
synced against the live status module; the boundary-truth snapshot; the evidence
list; the missing-requirements list; the four allowed options being
recommendation-only; the forbidden options being rejected; the requested-decision
assessment; gate states BLOCKED / LOCKED; every capability flag False;
forbidden-flag inputs marking the packet unsafe; determinism / mutation
isolation; no trade language; no secret values; validation; render; AST purity
(only typing / sparta_commander roots, no os / network / credential modules, no
filesystem-write capability); and the two additive commander_2_safety allowlist
entries.
"""

from __future__ import annotations

import ast
import pathlib

from sparta_commander.strategy_factory_crypto_d1_real_data_qa_boundary_decision_packet import (  # noqa: E501
    ALLOWED_DECISION_OPTION_IDS,
    ALLOWED_DECISION_OPTIONS,
    BOUNDARY_TRUTH,
    DEFAULT_PACKET_INPUT,
    EVIDENCE_COMPLETED,
    FORBIDDEN_DECISION_OPTION_IDS,
    FORBIDDEN_DECISION_OPTIONS,
    MISSING_REQUIREMENTS,
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
    assess_requested_decision,
    build_real_data_qa_boundary_decision_packet,
    render_real_data_qa_boundary_decision_packet_markdown,
    validate_real_data_qa_boundary_decision_packet,
)

_BUILD = build_real_data_qa_boundary_decision_packet
_VALIDATE = validate_real_data_qa_boundary_decision_packet
_RENDER = render_real_data_qa_boundary_decision_packet_markdown
_ASSESS = assess_requested_decision

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
_MODPATH = (
    _REPO_ROOT
    / "sparta_commander"
    / "strategy_factory_crypto_d1_real_data_qa_boundary_decision_packet.py"
)
_SAFETY_PATH = _REPO_ROOT / "sparta_commander" / "commander_2_safety.py"

_MODULE_ALLOWLIST_LINE = (
    "sparta_commander/strategy_factory_crypto_d1_real_data_qa_boundary_decision_packet.py"
)
_TEST_ALLOWLIST_LINE = (
    "tests/test_strategy_factory_crypto_d1_real_data_qa_boundary_decision_packet.py"
)


# --------------------------------------------------------------------------- #
# schema / identity
# --------------------------------------------------------------------------- #
def test_schema_label_mode_status():
    assert PACKET_SCHEMA_VERSION == (
        "strategy_factory_crypto_d1_real_data_qa_boundary_decision_packet.v1"
    )
    assert PACKET_LABEL == (
        "Block 170 - Crypto-D1 Real Data QA Boundary Decision Packet"
    )
    assert PACKET_MODE == "RESEARCH_ONLY"
    assert PACKET_STATUS == "HUMAN_CONTROLLED_BOUNDARY_DECISION_PACKET_ONLY"


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


def test_build_anchors_parked_stage():
    p = _BUILD()
    assert p["mission_flow_current_stage"] == MISSION_FLOW_CURRENT_STAGE
    assert p["mission_flow_next_required_action"] == MISSION_FLOW_NEXT_REQUIRED_ACTION
    assert p["mission_flow_aligned"] is True
    bd = p["boundary_decision"]
    assert bd["parked_stage"] == MISSION_FLOW_CURRENT_STAGE
    assert bd["parked_next_required_action"] == MISSION_FLOW_NEXT_REQUIRED_ACTION


def test_boundary_truth_snapshot_matches_blocked_locked():
    truth = dict(BOUNDARY_TRUTH)
    assert truth["current_stage"] == MISSION_FLOW_CURRENT_STAGE
    assert truth["next_required_action"] == MISSION_FLOW_NEXT_REQUIRED_ACTION
    assert truth["real_data_qa"] == "BLOCKED"
    assert truth["baseline_backtest"] == "BLOCKED"
    assert truth["paper_trading_gate"] == "LOCKED"
    assert truth["micro_live_gate"] == "LOCKED"
    assert truth["real_strategy_intake"] == "BLOCKED"
    assert truth["executes"] == "False"


# --------------------------------------------------------------------------- #
# evidence completed
# --------------------------------------------------------------------------- #
def test_evidence_completed_covers_known_research():
    p = _BUILD()
    evidence = p["boundary_decision"]["evidence_completed"]
    assert len(evidence) == len(EVIDENCE_COMPLETED)
    labels = " ".join(e["label"] for e in evidence).lower()
    for needle in (
        "external bot",
        "hyperliquid whale",
        "funding rate",
        "bitcoin cycle timing",
        "daily alpha brief",
        "selected read-only spot provider",
    ):
        assert needle in labels, needle
    for e in evidence:
        assert set(e) == {"label", "state", "description"}
        assert e["state"] == "completed"
        assert isinstance(e["description"], str) and e["description"].strip()


# --------------------------------------------------------------------------- #
# missing requirements
# --------------------------------------------------------------------------- #
def test_missing_requirements_cover_the_hard_gaps():
    p = _BUILD()
    missing = p["boundary_decision"]["missing_requirements"]
    assert len(missing) == len(MISSING_REQUIREMENTS)
    keys = {m["requirement"] for m in missing}
    for needle in (
        "selected_data_provider_final_human_approval",
        "exact_read_only_data_scope",
        "credentials_boundary_confirmation_if_applicable",
        "dataset_manifest_plan",
        "qa_checklist",
        "failure_rejection_conditions",
        "rollback_abort_conditions",
        "proof_no_execution_trading_permissions_enabled",
    ):
        assert needle in keys, needle
    for m in missing:
        assert set(m) == {"requirement", "description"}
        assert isinstance(m["description"], str) and m["description"].strip()


# --------------------------------------------------------------------------- #
# allowed decision options (recommendations only)
# --------------------------------------------------------------------------- #
def test_allowed_decision_options_are_the_four_and_recommendation_only():
    p = _BUILD()
    options = p["boundary_decision"]["allowed_decision_options"]
    assert [o["id"] for o in options] == list(ALLOWED_DECISION_OPTION_IDS)
    assert list(ALLOWED_DECISION_OPTION_IDS) == [
        "KEEP_BLOCKED",
        "PREPARE_REAL_DATA_QA_PLAN_ONLY",
        "REQUEST_ADDITIONAL_RESEARCH",
        "AUTHORIZE_NEXT_READ_ONLY_CONTRACT_ONLY",
    ]
    assert len(ALLOWED_DECISION_OPTIONS) == 4
    for o in options:
        assert o["recommendation_only"] is True
        assert o["authorizes_execution"] is False
        assert o["crosses_boundary"] is False


def test_highest_allowed_option_is_bounded_to_read_only_contract():
    p = _BUILD()
    assert p["highest_option_authorizes_only_read_only_contract"] is True
    summaries = {
        o["id"]: o["summary"]
        for o in p["boundary_decision"]["allowed_decision_options"]
    }
    blob = summaries["AUTHORIZE_NEXT_READ_ONLY_CONTRACT_ONLY"].lower()
    assert "read-only" in blob
    assert "research-only" in blob or "research only" in blob


def test_assess_each_allowed_option_is_recommendation_only():
    for oid in ALLOWED_DECISION_OPTION_IDS:
        a = _ASSESS(oid)
        assert a["allowed"] is True
        assert a["rejected"] is False
        assert a["recommendation_only"] is True
        assert a["authorizes_execution"] is False
        assert a["crosses_boundary"] is False


def test_default_packet_requests_no_decision():
    p = _BUILD()
    rda = p["boundary_decision"]["requested_decision_assessment"]
    assert rda["requested"] is None
    assert rda["allowed"] is False
    assert rda["rejected"] is False
    assert p["safe"] is True


def test_requesting_an_allowed_option_stays_safe():
    p = _BUILD({**DEFAULT_PACKET_INPUT, "requested_decision": "KEEP_BLOCKED"})
    assert p["safe"] is True
    rda = p["boundary_decision"]["requested_decision_assessment"]
    assert rda["allowed"] is True
    assert rda["authorizes_execution"] is False
    # selecting an option never flips a gate or capability flag.
    assert p["real_data_qa_blocked"] is True
    assert p["unlocks_real_data_qa"] is False


# --------------------------------------------------------------------------- #
# forbidden decision options (always rejected)
# --------------------------------------------------------------------------- #
def test_forbidden_decision_options_cover_the_dangerous_lanes():
    p = _BUILD()
    forbidden = p["boundary_decision"]["forbidden_decision_options"]
    assert [o["id"] for o in forbidden] == list(FORBIDDEN_DECISION_OPTION_IDS)
    for needle in (
        "UNLOCK_REAL_DATA_QA",
        "UNLOCK_BASELINE_BACKTEST",
        "UNLOCK_PAPER_TRADING",
        "UNLOCK_LIVE_TRADING",
        "ENABLE_BROKER_EXCHANGE",
        "FETCH_DATA_NOW",
        "RUN_QA_NOW",
        "ACCESS_CREDENTIALS",
        "WRITE_RUNTIME_DASHBOARD_STORAGE",
        "GENERATE_TRADE_SIGNALS_ORDERS",
    ):
        assert needle in FORBIDDEN_DECISION_OPTION_IDS, needle
    for o in forbidden:
        assert o["rejected"] is True


def test_assess_each_forbidden_option_is_rejected():
    for oid in FORBIDDEN_DECISION_OPTION_IDS:
        a = _ASSESS(oid)
        assert a["allowed"] is False
        assert a["rejected"] is True
        assert a["authorizes_execution"] is False
        assert a["crosses_boundary"] is False


def test_requesting_a_forbidden_option_marks_unsafe_but_unlocks_nothing():
    for oid in FORBIDDEN_DECISION_OPTION_IDS:
        p = _BUILD({**DEFAULT_PACKET_INPUT, "requested_decision": oid})
        assert p["safe"] is False, oid
        rda = p["boundary_decision"]["requested_decision_assessment"]
        assert rda["rejected"] is True
        # rejected request never flips a gate or capability flag.
        assert p["real_data_qa_blocked"] is True
        assert p["unlocks_real_data_qa"] is False
        assert p["authorizes_nothing"] is True


def test_requesting_unrecognized_option_is_rejected():
    p = _BUILD({**DEFAULT_PACKET_INPUT, "requested_decision": "DO_SOMETHING_WILD"})
    assert p["safe"] is False
    rda = p["boundary_decision"]["requested_decision_assessment"]
    assert rda["allowed"] is False
    assert rda["rejected"] is True


# --------------------------------------------------------------------------- #
# gate states + capability flags
# --------------------------------------------------------------------------- #
def test_gate_states_blocked_and_locked():
    p = _BUILD()
    assert p["real_data_qa_state"] == "BLOCKED"
    assert p["baseline_backtest_state"] == "BLOCKED"
    assert p["paper_live_state"] == "LOCKED"
    assert p["real_strategy_intake_state"] == "BLOCKED"
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
    assert p["requires_separate_future_human_controlled_step"] is True
    assert p["human_decision_required"] is True
    assert p["human_approval_required"] is True


def test_safety_posture_passthrough():
    assert _BUILD()["safety_posture"] == PACKET_SAFETY_POSTURE
    for key in (
        "read_only",
        "research_only",
        "decision_packet_only",
        "human_decision_required",
        "parked_at_boundary",
    ):
        assert PACKET_SAFETY_POSTURE[key] is True
    assert PACKET_SAFETY_POSTURE["executes"] is False
    assert PACKET_SAFETY_POSTURE["accesses_credentials"] is False
    assert PACKET_SAFETY_POSTURE["performs_auto_push"] is False
    assert PACKET_SAFETY_POSTURE["generates_order"] is False


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
        assert p["real_data_qa_blocked"] is True
        assert p["unlocks_real_data_qa"] is False
        assert p["authorizes_nothing"] is True


def test_mission_flow_misalignment_marks_unsafe():
    p = _BUILD({**DEFAULT_PACKET_INPUT, "mission_flow_current_stage": "SOMEWHERE_ELSE"})
    assert p["mission_flow_aligned"] is False
    assert p["safe"] is False
    assert p["real_data_qa_blocked"] is True


# --------------------------------------------------------------------------- #
# determinism / mutation isolation
# --------------------------------------------------------------------------- #
def test_build_is_deterministic_and_isolated():
    a = _BUILD()
    b = _BUILD()
    assert a == b
    a["boundary_decision"]["missing_requirements"].append({"x": 1})
    a["safety_posture"]["executes"] = True
    c = _BUILD()
    assert len(c["boundary_decision"]["missing_requirements"]) == len(
        MISSING_REQUIREMENTS
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


def test_validate_rejects_tampered_allowed_option():
    p = _BUILD()
    p["boundary_decision"]["allowed_decision_options"][0]["authorizes_execution"] = True
    verdict = _VALIDATE(p)
    assert verdict["valid"] is False
    assert verdict["allowed_options_ok"] is False


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #
def test_render_is_deterministic_markdown():
    p = _BUILD()
    md1 = _RENDER(p)
    md2 = _RENDER(p)
    assert md1 == md2
    assert md1.startswith("# Crypto-D1 Real Data QA Boundary Decision Packet")
    assert "## Boundary Truth" in md1
    assert "## Evidence Completed" in md1
    assert "## Missing Requirements Before Real Data QA" in md1
    assert "## Allowed Decision Options (recommendations only)" in md1
    assert "## Forbidden Decision Options (always rejected)" in md1
    assert "KEEP_BLOCKED" in md1
    assert "UNLOCK_REAL_DATA_QA" in md1
    assert "BLOCKED" in md1
    assert "LOCKED" in md1


def test_render_handles_non_dict():
    assert _RENDER("x").startswith(
        "# Crypto-D1 Real Data QA Boundary Decision Packet"
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
    _BUILD({**DEFAULT_PACKET_INPUT, "requested_decision": "FETCH_DATA_NOW"})
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
