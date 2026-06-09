"""Tests for the Crypto-D1 Real Data QA Plan-Only Contract (Block 171).

The module is a pure, stdlib-only, read-only PAPER contract realizing the
operator's PREPARE_REAL_DATA_QA_PLAN_ONLY decision. It defines, on paper only, the
QA scope, selected read-only spot provider boundaries, dataset manifest
requirements, approved symbols / daily timeframe / spot instrument type, rejection
conditions, abort rules, and the safety gates for a FUTURE, separately
human-controlled, read-only QA step. It authorizes nothing, unlocks nothing, and
executes nothing.

These tests assert: schema / label / mode / status; the parked mission-flow truth
synced against the live status module; the QA scope checks; provider boundaries;
dataset manifest requirements; allowed symbols / timeframe / instrument type;
rejection conditions; abort rules; safety gates BLOCKED / LOCKED; every capability
flag False; forbidden-flag inputs marking the contract unsafe; determinism /
mutation isolation; no trade language; no secret values; validation; render; AST
purity (only typing / sparta_commander roots, no os / network / credential
modules, no filesystem-write capability); and the two additive commander_2_safety
allowlist entries.
"""

from __future__ import annotations

import ast
import pathlib

from sparta_commander.strategy_factory_crypto_d1_real_data_qa_plan_only_contract import (  # noqa: E501
    ABORT_RULES,
    ALLOWED_INSTRUMENT_TYPE,
    ALLOWED_SYMBOLS,
    ALLOWED_TIMEFRAME,
    DATASET_MANIFEST_REQUIREMENTS,
    DEFAULT_PLAN_INPUT,
    MISSION_FLOW_CURRENT_STAGE,
    MISSION_FLOW_NEXT_REQUIRED_ACTION,
    PLAN_CORE_RULE,
    PLAN_FORBIDDEN_FLAGS,
    PLAN_FORBIDDEN_TRADE_TERMS,
    PLAN_LABEL,
    PLAN_MODE,
    PLAN_SAFETY_POSTURE,
    PLAN_SCHEMA_VERSION,
    PLAN_STATUS,
    PROVIDER_BOUNDARIES,
    QA_SCOPE_CHECKS,
    REJECTION_CONDITIONS,
    SAFETY_GATES,
    build_real_data_qa_plan_only_contract,
    render_real_data_qa_plan_only_contract_markdown,
    validate_real_data_qa_plan_only_contract,
)

_BUILD = build_real_data_qa_plan_only_contract
_VALIDATE = validate_real_data_qa_plan_only_contract
_RENDER = render_real_data_qa_plan_only_contract_markdown

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
_MODPATH = (
    _REPO_ROOT
    / "sparta_commander"
    / "strategy_factory_crypto_d1_real_data_qa_plan_only_contract.py"
)
_SAFETY_PATH = _REPO_ROOT / "sparta_commander" / "commander_2_safety.py"

_MODULE_ALLOWLIST_LINE = (
    "sparta_commander/strategy_factory_crypto_d1_real_data_qa_plan_only_contract.py"
)
_TEST_ALLOWLIST_LINE = (
    "tests/test_strategy_factory_crypto_d1_real_data_qa_plan_only_contract.py"
)


# --------------------------------------------------------------------------- #
# schema / identity
# --------------------------------------------------------------------------- #
def test_schema_label_mode_status():
    assert PLAN_SCHEMA_VERSION == (
        "strategy_factory_crypto_d1_real_data_qa_plan_only_contract.v1"
    )
    assert PLAN_LABEL == "Block 171 - Crypto-D1 Real Data QA Plan-Only Contract"
    assert PLAN_MODE == "RESEARCH_ONLY"
    assert PLAN_STATUS == "READ_ONLY_REAL_DATA_QA_PLAN_ONLY"


def test_build_carries_identity():
    c = _BUILD()
    assert c["schema_version"] == PLAN_SCHEMA_VERSION
    assert c["label"] == PLAN_LABEL
    assert c["mode"] == PLAN_MODE
    assert c["status"] == PLAN_STATUS
    assert c["core_rule"] == PLAN_CORE_RULE


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
    c = _BUILD()
    assert c["mission_flow_current_stage"] == MISSION_FLOW_CURRENT_STAGE
    assert c["mission_flow_next_required_action"] == MISSION_FLOW_NEXT_REQUIRED_ACTION
    assert c["mission_flow_aligned"] is True
    p = c["qa_plan"]
    assert p["parked_stage"] == MISSION_FLOW_CURRENT_STAGE
    assert p["parked_next_required_action"] == MISSION_FLOW_NEXT_REQUIRED_ACTION


# --------------------------------------------------------------------------- #
# QA scope / provider boundaries / manifest / scope data
# --------------------------------------------------------------------------- #
def test_qa_scope_checks_cover_core_quality_lanes():
    p = _BUILD()["qa_plan"]
    checks = p["qa_scope_checks"]
    assert len(checks) == len(QA_SCOPE_CHECKS)
    ids = {i["id"] for i in checks}
    for needle in (
        "schema_conformance",
        "null_check",
        "duplicate_check",
        "timestamp_monotonicity",
        "gap_detection",
        "range_sanity",
        "row_count_minimums",
        "symbol_coverage",
        "ohlcv_field_presence",
        "instrument_type_spot_only",
    ):
        assert needle in ids, needle
    for i in checks:
        assert set(i) == {"id", "description"}
        assert isinstance(i["description"], str) and i["description"].strip()


def test_provider_boundaries_are_read_only_spot_only():
    p = _BUILD()["qa_plan"]
    blob = " ".join(p["provider_boundaries"]).lower()
    assert p["provider_boundaries"] == list(PROVIDER_BOUNDARIES)
    assert "read-only" in blob
    assert "spot" in blob
    assert "no network" in blob
    assert "no credential" in blob


def test_dataset_manifest_requirements_present():
    p = _BUILD()["qa_plan"]
    reqs = p["dataset_manifest_requirements"]
    assert len(reqs) == len(DATASET_MANIFEST_REQUIREMENTS)
    fields = {r["field"] for r in reqs}
    for needle in (
        "provider_name",
        "source_license",
        "symbols",
        "timeframe",
        "instrument_type",
        "date_range_start",
        "date_range_end",
        "files",
        "required_fields",
        "read_only_attestation",
    ):
        assert needle in fields, needle
    for r in reqs:
        assert set(r) == {"field", "description"}


def test_allowed_scope_is_daily_spot_allowlist():
    p = _BUILD()["qa_plan"]
    assert p["allowed_symbols"] == list(ALLOWED_SYMBOLS)
    assert p["allowed_timeframe"] == ALLOWED_TIMEFRAME == "1d"
    assert p["allowed_instrument_type"] == ALLOWED_INSTRUMENT_TYPE == "spot"
    assert ALLOWED_SYMBOLS  # non-empty


# --------------------------------------------------------------------------- #
# rejection conditions / abort rules / safety gates
# --------------------------------------------------------------------------- #
def test_rejection_conditions_cover_the_hard_rejects():
    p = _BUILD()["qa_plan"]
    rej = p["rejection_conditions"]
    assert len(rej) == len(REJECTION_CONDITIONS)
    ids = {i["id"] for i in rej}
    for needle in (
        "wrong_instrument_type",
        "missing_required_field",
        "non_daily_timeframe",
        "unapproved_symbol",
        "unclear_source_or_license",
        "credentialed_provider",
        "schema_mismatch",
        "non_monotonic_timestamps",
        "duplicate_rows",
        "out_of_range_values",
    ):
        assert needle in ids, needle


def test_abort_rules_cover_boundary_crossing():
    p = _BUILD()["qa_plan"]
    rules = p["abort_rules"]
    assert len(rules) == len(ABORT_RULES)
    ids = {i["id"] for i in rules}
    for needle in (
        "network_or_endpoint_attempted",
        "credential_required_or_read",
        "write_outside_read_only",
        "execution_or_trade_surface_touched",
        "gate_unlock_requested",
        "boundary_crossing_required",
    ):
        assert needle in ids, needle


def test_safety_gates_blocked_and_locked():
    p = _BUILD()["qa_plan"]
    gates = {g["gate"]: g["state"] for g in p["safety_gates"]}
    assert gates["real_data_qa"] == "BLOCKED"
    assert gates["baseline_backtest"] == "BLOCKED"
    assert gates["paper_trading_gate"] == "LOCKED"
    assert gates["micro_live_gate"] == "LOCKED"
    assert gates["real_strategy_intake"] == "BLOCKED"
    assert len(p["safety_gates"]) == len(SAFETY_GATES)


def test_top_level_gate_states_blocked_and_locked():
    c = _BUILD()
    assert c["real_data_qa_state"] == "BLOCKED"
    assert c["baseline_backtest_state"] == "BLOCKED"
    assert c["paper_live_state"] == "LOCKED"
    assert c["real_strategy_intake_state"] == "BLOCKED"
    assert c["real_data_qa_blocked"] is True
    assert c["baseline_backtest_blocked"] is True
    assert c["paper_trading_gate_locked"] is True
    assert c["micro_live_gate_locked"] is True


def test_no_unlock_confirmation_block_locked():
    nuc = _BUILD()["qa_plan"]["no_unlock_confirmation"]
    assert nuc["unlocks_real_data_qa"] is False
    assert nuc["unlocks_baseline_backtest"] is False
    assert nuc["unlocks_paper_trading"] is False
    assert nuc["unlocks_micro_live"] is False
    assert nuc["real_data_qa_state"] == "BLOCKED"
    assert nuc["baseline_backtest_state"] == "BLOCKED"
    assert nuc["paper_live_state"] == "LOCKED"


# --------------------------------------------------------------------------- #
# capability flags
# --------------------------------------------------------------------------- #
def test_every_capability_flag_is_false():
    c = _BUILD()
    for flag, value in PLAN_SAFETY_POSTURE.items():
        if value is False:
            assert c.get(flag) is False, flag
    assert c["authorizes_nothing"] is True
    assert c["this_plan_authorizes_boundary_crossing"] is False
    assert c["this_plan_unlocks_real_data_qa"] is False
    assert c["requires_separate_future_human_controlled_step"] is True
    assert c["human_decision_required"] is True
    assert c["human_approval_required"] is True


def test_safety_posture_passthrough():
    assert _BUILD()["safety_posture"] == PLAN_SAFETY_POSTURE
    for key in (
        "read_only",
        "research_only",
        "plan_only",
        "human_decision_required",
        "parked_at_boundary",
    ):
        assert PLAN_SAFETY_POSTURE[key] is True
    assert PLAN_SAFETY_POSTURE["executes"] is False
    assert PLAN_SAFETY_POSTURE["writes_manifest"] is False
    assert PLAN_SAFETY_POSTURE["accesses_credentials"] is False
    assert PLAN_SAFETY_POSTURE["performs_auto_push"] is False


# --------------------------------------------------------------------------- #
# forbidden-flag inputs mark unsafe (but never unlock anything)
# --------------------------------------------------------------------------- #
def test_default_contract_is_safe():
    c = _BUILD()
    assert c["safe"] is True
    assert c["forbidden_flag_hits"] == []


def test_each_forbidden_flag_marks_unsafe():
    for flag in PLAN_FORBIDDEN_FLAGS:
        c = _BUILD({**DEFAULT_PLAN_INPUT, flag: True})
        assert c["safe"] is False, flag
        assert flag in c["forbidden_flag_hits"], flag
        assert c["real_data_qa_blocked"] is True
        assert c["unlocks_real_data_qa"] is False
        assert c["authorizes_nothing"] is True


def test_mission_flow_misalignment_marks_unsafe():
    c = _BUILD({**DEFAULT_PLAN_INPUT, "mission_flow_current_stage": "SOMEWHERE_ELSE"})
    assert c["mission_flow_aligned"] is False
    assert c["safe"] is False
    assert c["real_data_qa_blocked"] is True


# --------------------------------------------------------------------------- #
# determinism / mutation isolation
# --------------------------------------------------------------------------- #
def test_build_is_deterministic_and_isolated():
    a = _BUILD()
    b = _BUILD()
    assert a == b
    a["qa_plan"]["abort_rules"].append({"x": 1})
    a["safety_posture"]["executes"] = True
    c = _BUILD()
    assert len(c["qa_plan"]["abort_rules"]) == len(ABORT_RULES)
    assert c["safety_posture"]["executes"] is False


def test_default_input_not_mutated_by_build():
    snapshot = dict(DEFAULT_PLAN_INPUT)
    _BUILD()
    assert DEFAULT_PLAN_INPUT == snapshot


# --------------------------------------------------------------------------- #
# narrative purity
# --------------------------------------------------------------------------- #
def test_narrative_has_no_trade_language():
    c = _BUILD()
    blob = " ".join(
        [
            c["operator_next_step"],
            c["plan_summary"],
            c["core_rule"],
            *c["human_operator_required_next_steps"],
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
    assert not (tokens & set(PLAN_FORBIDDEN_TRADE_TERMS))


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #
def test_validate_default_contract_is_valid():
    verdict = _VALIDATE(_BUILD())
    assert verdict["valid"] is True
    assert verdict["missing_fields"] == []
    for key, value in verdict.items():
        if key in ("valid", "missing_fields"):
            continue
        assert value is True, key


def test_validate_rejects_non_dict():
    assert _VALIDATE("not a contract")["valid"] is False


def test_validate_rejects_tampered_gate():
    c = _BUILD()
    c["real_data_qa_blocked"] = False
    verdict = _VALIDATE(c)
    assert verdict["valid"] is False
    assert verdict["gates_locked"] is False


def test_validate_rejects_flipped_capability_flag():
    c = _BUILD()
    c["executes"] = True
    verdict = _VALIDATE(c)
    assert verdict["valid"] is False
    assert verdict["flags_false"] is False


def test_validate_rejects_tampered_scope():
    c = _BUILD()
    c["qa_plan"]["allowed_instrument_type"] = "futures"
    verdict = _VALIDATE(c)
    assert verdict["valid"] is False
    assert verdict["scope_data_ok"] is False


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #
def test_render_is_deterministic_markdown():
    c = _BUILD()
    md1 = _RENDER(c)
    md2 = _RENDER(c)
    assert md1 == md2
    assert md1.startswith("# Crypto-D1 Real Data QA Plan-Only Contract")
    assert "## QA Scope Checks" in md1
    assert "## Provider Boundaries" in md1
    assert "## Dataset Manifest Requirements" in md1
    assert "## Rejection Conditions" in md1
    assert "## Abort Rules" in md1
    assert "## Safety Gates" in md1
    assert "BLOCKED" in md1
    assert "LOCKED" in md1
    assert "spot" in md1


def test_render_handles_non_dict():
    assert _RENDER("x").startswith("# Crypto-D1 Real Data QA Plan-Only Contract")


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
    _BUILD({**DEFAULT_PLAN_INPUT, "fetch_data_now": True})
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
