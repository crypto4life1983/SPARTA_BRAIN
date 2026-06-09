"""Tests for the Crypto-D1 Selected Read-Only Spot Provider Fetch Runner Dry Run
(Block 169).

The contract is a pure, stdlib-only, read-only paper dry-run contract. It answers
exactly one research-only question, on paper: does a caller-supplied STATIC
description of a dry run of the selected read-only spot provider fetch runner --
exercised ONLY against an in-memory FAKE provider -- look complete and safe enough,
aligned with the Block 151 read-only spot provider adapter rules, to put in front of
a human for a dry-run review? It assesses the dry run into exactly ONE of two
outcomes (READY_FOR_HUMAN_DRY_RUN_REVIEW / HOLD_NEEDS_MORE_PREP) and authorizes /
unlocks nothing under either outcome -- even READY only means "the paper dry run is
sound enough for a human to review the exercise." These tests assert the schema, the
ten dry-run items, the READY-only-when-all-pass model, every missing-item HOLD case,
the safety-violation tripwire (any authorization / gate-unlock / promotion /
real-provider-injection / live-endpoint / credential-need / account-trade field /
boundary-crossing flag forces HOLD with a recorded violation), the
all-capability-flags-False / gates-locked posture, the mission-flow truth sync
against the live status module, determinism, isolation, validation, render, AST
purity, and the two additive commander_2_safety allowlist entries.
"""

from __future__ import annotations

import ast
import copy
import pathlib

from sparta_commander.strategy_factory_crypto_d1_selected_read_only_spot_provider_fetch_runner_dry_run import (  # noqa: E501
    DRY_RUN_ACCOUNT_TRADE_FIELDS,
    DRY_RUN_AUTHORIZATION_FLAGS,
    DRY_RUN_CORE_RULE,
    DRY_RUN_CREDENTIAL_NEED_FLAGS,
    DRY_RUN_CURRENT_STAGE,
    DRY_RUN_FORBIDDEN_PROMOTION_REQUEST_FLAGS,
    DRY_RUN_FORBIDDEN_TRADE_TERMS,
    DRY_RUN_GATE_LOCK_FLAGS,
    DRY_RUN_GATE_UNLOCK_REQUEST_FLAGS,
    DRY_RUN_ITEM_IDS,
    DRY_RUN_ITEMS,
    DRY_RUN_LABEL,
    DRY_RUN_LIVE_ENDPOINT_FLAGS,
    DRY_RUN_MISSION_FLOW_CURRENT_STAGE,
    DRY_RUN_MISSION_FLOW_NEXT_REQUIRED_ACTION,
    DRY_RUN_MODE,
    DRY_RUN_NEXT_REQUIRED_ACTION,
    DRY_RUN_OUTCOMES,
    DRY_RUN_REAL_PROVIDER_FLAGS,
    DRY_RUN_SAFETY_POSTURE,
    DRY_RUN_SCHEMA_VERSION,
    DRY_RUN_STATUS,
    DEFAULT_SAMPLE_DRY_RUN_INPUT,
    OUTCOME_HOLD,
    OUTCOME_READY,
    assess_selected_read_only_spot_provider_fetch_runner_dry_run,
    build_crypto_d1_selected_read_only_spot_provider_fetch_runner_dry_run,
    render_crypto_d1_selected_read_only_spot_provider_fetch_runner_dry_run_markdown,
    validate_crypto_d1_selected_read_only_spot_provider_fetch_runner_dry_run,
)

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
_MODPATH = (
    _REPO_ROOT
    / "sparta_commander"
    / "strategy_factory_crypto_d1_selected_read_only_spot_provider_fetch_runner_dry_run.py"
)
_SAFETY_PATH = _REPO_ROOT / "sparta_commander" / "commander_2_safety.py"

_MODULE_ALLOWLIST_LINE = (
    "sparta_commander/strategy_factory_crypto_d1_selected_read_only_spot_provider_fetch_runner_dry_run.py"
)
_TEST_ALLOWLIST_LINE = (
    "tests/test_strategy_factory_crypto_d1_selected_read_only_spot_provider_fetch_runner_dry_run.py"
)

_ASSESS = assess_selected_read_only_spot_provider_fetch_runner_dry_run
_BUILD = build_crypto_d1_selected_read_only_spot_provider_fetch_runner_dry_run
_VALIDATE = validate_crypto_d1_selected_read_only_spot_provider_fetch_runner_dry_run
_RENDER = render_crypto_d1_selected_read_only_spot_provider_fetch_runner_dry_run_markdown


def _ready_input(**overrides):
    """A payload where all ten dry-run items pass and no unsafe flag is set, so the
    assessment reaches READY unless an override degrades it."""
    payload = copy.deepcopy(DEFAULT_SAMPLE_DRY_RUN_INPUT)
    payload.update(overrides)
    return payload


# --------------------------------------------------------------------------- #
# Schema / constants
# --------------------------------------------------------------------------- #
def test_schema_version_and_labels():
    assert DRY_RUN_SCHEMA_VERSION == (
        "strategy_factory_crypto_d1_selected_read_only_spot_provider_fetch_runner_dry_run.v1"
    )
    assert DRY_RUN_LABEL == (
        "Block 169 - Crypto-D1 Selected Read-Only Spot Provider Fetch Runner Dry "
        "Run"
    )
    assert DRY_RUN_STATUS == (
        "READ_ONLY_CRYPTO_D1_SELECTED_SPOT_PROVIDER_FETCH_RUNNER_DRY_RUN"
    )
    assert DRY_RUN_MODE == "RESEARCH_ONLY"
    assert "authorizes nothing and runs nothing" in DRY_RUN_CORE_RULE


def test_next_action_and_stage_are_build_only():
    assert DRY_RUN_NEXT_REQUIRED_ACTION == (
        "BUILD_CRYPTO_D1_SELECTED_READ_ONLY_SPOT_PROVIDER_FETCH_RUNNER_DRY_RUN"
    )
    assert DRY_RUN_CURRENT_STAGE == (
        "CRYPTO_D1_SELECTED_READ_ONLY_SPOT_PROVIDER_FETCH_RUNNER_DRY_RUN_REQUIRED"
    )


def test_outcomes_are_exactly_two_ready_or_hold():
    assert DRY_RUN_OUTCOMES == (OUTCOME_READY, OUTCOME_HOLD)
    assert OUTCOME_READY == "READY_FOR_HUMAN_DRY_RUN_REVIEW"
    assert OUTCOME_HOLD == "HOLD_NEEDS_MORE_PREP"


def test_ten_dry_run_items_are_exactly_the_items():
    assert len(DRY_RUN_ITEM_IDS) == 10
    assert DRY_RUN_ITEM_IDS == (
        "uses_fake_provider_only",
        "read_only_fetch_call_only",
        "returns_required_ohlcv_fields",
        "spot_instrument_type_only",
        "daily_timeframe_only",
        "no_credentials_in_dry_run",
        "deterministic_dry_run_result",
        "no_real_data_persisted",
        "no_network_in_dry_run",
        "matches_block151_adapter_contract",
    )
    for item_id, label in DRY_RUN_ITEMS:
        assert isinstance(label, str) and label


def test_safety_posture_three_true_facts_all_else_false():
    posture = DRY_RUN_SAFETY_POSTURE
    assert posture["read_only"] is True
    assert posture["research_only"] is True
    assert posture["human_approval_required"] is True
    assert posture["executes"] is False
    for key, value in posture.items():
        if key in ("read_only", "research_only", "human_approval_required"):
            continue
        assert value is False, key


# --------------------------------------------------------------------------- #
# Mission-flow truth sync
# --------------------------------------------------------------------------- #
def test_mission_flow_truth_matches_live_status_module():
    from sparta_commander import strategy_factory_mission_flow_status as status

    assert (
        DRY_RUN_MISSION_FLOW_CURRENT_STAGE == status.CURRENT_STAGE
    )
    assert (
        DRY_RUN_MISSION_FLOW_NEXT_REQUIRED_ACTION
        == status.NEXT_REQUIRED_ACTION
    )


# --------------------------------------------------------------------------- #
# Dry-run model
# --------------------------------------------------------------------------- #
def test_default_sample_is_ready():
    result = _ASSESS(DEFAULT_SAMPLE_DRY_RUN_INPUT)
    assert result["outcome"] == OUTCOME_READY
    assert result["ready"] is True
    assert result["ready_for_human_dry_run_review"] is True
    assert result["failed_item_ids"] == []
    assert len(result["passed_item_ids"]) == 10
    assert result["unsafe_flag_hits"] == []
    assert result["safety_violation"] is False
    # READY still authorizes and unlocks nothing.
    assert result["authorizes_nothing"] is True
    assert result["injects_real_provider"] is False
    assert result["calls_endpoint"] is False
    assert result["fetches_url"] is False
    assert result["acquires_real_data"] is False
    assert result["unlocks_real_data_qa"] is False
    assert result["crosses_boundary"] is False


def test_default_build_is_ready():
    contract = _BUILD()
    assert contract["outcome"] == OUTCOME_READY
    assert contract["ready"] is True


def test_each_missing_dry_run_item_forces_hold():
    for item_id in DRY_RUN_ITEM_IDS:
        result = _ASSESS(_ready_input(**{item_id: False}))
        assert result["outcome"] == OUTCOME_HOLD, item_id
        assert item_id in result["failed_item_ids"], item_id
        assert result["ready"] is False, item_id


def test_missing_fake_provider_only_is_hold():
    result = _ASSESS(_ready_input(uses_fake_provider_only=False))
    assert result["outcome"] == OUTCOME_HOLD
    assert "uses_fake_provider_only" in result["failed_item_ids"]
    assert result["safety_violation"] is False


def test_missing_read_only_fetch_call_only_is_hold():
    result = _ASSESS(_ready_input(read_only_fetch_call_only=False))
    assert result["outcome"] == OUTCOME_HOLD
    assert "read_only_fetch_call_only" in result["failed_item_ids"]


def test_missing_ohlcv_fields_is_hold():
    result = _ASSESS(_ready_input(returns_required_ohlcv_fields=False))
    assert result["outcome"] == OUTCOME_HOLD
    assert "returns_required_ohlcv_fields" in result["failed_item_ids"]


# --------------------------------------------------------------------------- #
# Safety-violation tripwire: an unsafe flag can never be READY
# --------------------------------------------------------------------------- #
def test_authorization_flag_forces_hold_with_violation():
    for flag in DRY_RUN_AUTHORIZATION_FLAGS:
        result = _ASSESS(_ready_input(**{flag: True}))
        assert result["outcome"] == OUTCOME_HOLD, flag
        assert result["safety_violation"] is True, flag
        assert flag in result["unsafe_flag_hits"], flag
        assert result["ready"] is False, flag


def test_gate_unlock_request_forces_hold_with_violation():
    for flag in DRY_RUN_GATE_UNLOCK_REQUEST_FLAGS:
        result = _ASSESS(_ready_input(**{flag: True}))
        assert result["outcome"] == OUTCOME_HOLD, flag
        assert result["safety_violation"] is True, flag
        assert flag in result["unsafe_flag_hits"], flag


def test_unlocking_a_locked_gate_forces_hold_with_violation():
    for flag in DRY_RUN_GATE_LOCK_FLAGS:
        result = _ASSESS(_ready_input(**{flag: False}))
        assert result["outcome"] == OUTCOME_HOLD, flag
        assert result["safety_violation"] is True, flag
        assert ("unlocked:" + flag) in result["unsafe_flag_hits"], flag


def test_forbidden_promotion_request_forces_hold_with_violation():
    for flag in DRY_RUN_FORBIDDEN_PROMOTION_REQUEST_FLAGS:
        result = _ASSESS(_ready_input(**{flag: True}))
        assert result["outcome"] == OUTCOME_HOLD, flag
        assert result["safety_violation"] is True, flag
        assert flag in result["unsafe_flag_hits"], flag


def test_real_provider_injection_forces_hold_with_violation():
    for flag in DRY_RUN_REAL_PROVIDER_FLAGS:
        result = _ASSESS(_ready_input(**{flag: True}))
        assert result["outcome"] == OUTCOME_HOLD, flag
        assert result["safety_violation"] is True, flag
        assert flag in result["unsafe_flag_hits"], flag


def test_live_endpoint_flag_forces_hold_with_violation():
    for flag in DRY_RUN_LIVE_ENDPOINT_FLAGS:
        result = _ASSESS(_ready_input(**{flag: True}))
        assert result["outcome"] == OUTCOME_HOLD, flag
        assert result["safety_violation"] is True, flag
        assert flag in result["unsafe_flag_hits"], flag


def test_credential_need_flag_forces_hold_with_violation():
    for flag in DRY_RUN_CREDENTIAL_NEED_FLAGS:
        result = _ASSESS(_ready_input(**{flag: True}))
        assert result["outcome"] == OUTCOME_HOLD, flag
        assert result["safety_violation"] is True, flag
        assert flag in result["unsafe_flag_hits"], flag


def test_account_trade_field_forces_hold_with_violation():
    for field in DRY_RUN_ACCOUNT_TRADE_FIELDS:
        result = _ASSESS(_ready_input(**{field: "something"}))
        assert result["outcome"] == OUTCOME_HOLD, field
        assert result["safety_violation"] is True, field
        assert field in result["unsafe_flag_hits"], field


def test_unsafe_flag_also_fails_no_network_item():
    result = _ASSESS(_ready_input(opens_network=True))
    assert "no_network_in_dry_run" in result["failed_item_ids"]


def test_real_provider_injection_also_fails_no_network_item():
    result = _ASSESS(_ready_input(injects_real_provider=True))
    assert "no_network_in_dry_run" in result["failed_item_ids"]


def test_mission_flow_misalignment_fails_block151_item():
    result = _ASSESS(_ready_input(mission_flow_current_stage="SOMETHING_ELSE"))
    assert result["outcome"] == OUTCOME_HOLD
    assert result["mission_flow_aligned"] is False
    assert "matches_block151_adapter_contract" in result["failed_item_ids"]


def test_safety_violation_with_missing_item_still_holds():
    result = _ASSESS(
        _ready_input(
            uses_fake_provider_only=False, authorizes_trading=True
        )
    )
    assert result["outcome"] == OUTCOME_HOLD
    assert result["safety_violation"] is True


# --------------------------------------------------------------------------- #
# Determinism / isolation
# --------------------------------------------------------------------------- #
def test_assessment_is_deterministic():
    payload = _ready_input()
    assert _ASSESS(payload) == _ASSESS(payload)


def test_build_does_not_mutate_caller_payload():
    payload = _ready_input()
    snapshot = copy.deepcopy(payload)
    _BUILD(payload)
    assert payload == snapshot


def test_default_sample_is_not_shared_between_builds():
    c1 = _BUILD()
    c2 = _BUILD()
    c1["failed_item_ids"].append("tampered")
    assert "tampered" not in c2["failed_item_ids"]
    assert (
        DEFAULT_SAMPLE_DRY_RUN_INPUT["uses_fake_provider_only"]
        is True
    )


# --------------------------------------------------------------------------- #
# Validation
# --------------------------------------------------------------------------- #
def test_default_contract_validates():
    verdict = _VALIDATE(_BUILD())
    assert verdict["valid"] is True
    assert verdict["missing_fields"] == []
    assert verdict["no_trade_language"] is True
    assert verdict["flags_false"] is True
    assert verdict["gates_locked"] is True
    assert verdict["authorizes_nothing"] is True
    assert verdict["mission_flow_refs_ok"] is True
    assert verdict["ten_dry_run_items"] is True
    assert verdict["ready_only_when_all_pass"] is True
    assert verdict["real_data_qa_stays_blocked"] is True
    assert verdict["outcomes_ok"] is True


def test_every_outcome_path_validates():
    payloads = [
        DEFAULT_SAMPLE_DRY_RUN_INPUT,                       # ready
        _ready_input(uses_fake_provider_only=False),        # hold (missing)
        _ready_input(authorizes_trading=True),              # hold (violation)
        _ready_input(requires_api_key=True),                # hold (credential)
        _ready_input(injects_real_provider=True),           # hold (real provider)
        _ready_input(implements_live_provider=True),        # hold (live endpoint)
        _ready_input(real_data_qa_blocked=False),           # hold (gate unlock)
        _ready_input(mission_flow_current_stage="X"),       # hold (misaligned)
    ]
    for payload in payloads:
        verdict = _VALIDATE(_BUILD(payload))
        assert verdict["valid"] is True, payload


def test_validate_rejects_tampered_contract():
    contract = _BUILD()
    contract["executes"] = True
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["executes_false"] is False


def test_validate_rejects_unlocked_real_data_qa():
    contract = _BUILD()
    contract["unlocks_real_data_qa"] = True
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["real_data_qa_stays_blocked"] is False


def test_validate_rejects_endpoint_call_flag():
    contract = _BUILD()
    contract["calls_endpoint"] = True
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["flags_false"] is False


def test_validate_rejects_real_provider_injection_flag():
    contract = _BUILD()
    contract["injects_real_provider"] = True
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["flags_false"] is False


def test_validate_rejects_ready_without_all_items_passing():
    contract = _BUILD(_ready_input(uses_fake_provider_only=False))
    assert contract["outcome"] == OUTCOME_HOLD
    contract["ready"] = True
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["ready_only_when_all_pass"] is False


def test_validate_rejects_ready_with_safety_violation():
    contract = _BUILD(_ready_input(authorizes_trading=True))
    assert contract["outcome"] == OUTCOME_HOLD
    contract["ready"] = True
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["ready_only_when_all_pass"] is False


def test_ready_contract_unlocks_no_gate():
    contract = _BUILD(_ready_input())
    assert contract["outcome"] == OUTCOME_READY
    assert contract["ready"] is True
    assert contract["promotes_beyond_boundary"] is False
    assert contract["injects_real_provider"] is False
    assert contract["calls_endpoint"] is False
    assert contract["fetches_url"] is False
    assert contract["acquires_real_data"] is False
    assert contract["unlocks_real_data_qa"] is False
    assert contract["unlocks_baseline_backtest"] is False
    assert contract["unlocks_paper_trading"] is False
    assert contract["unlocks_micro_live"] is False
    assert contract["crosses_boundary"] is False
    assert contract["real_data_qa_blocked"] is True
    assert contract["baseline_backtest_blocked"] is True
    assert contract["paper_trading_gate_locked"] is True
    assert contract["micro_live_gate_locked"] is True
    assert contract["authorizes_nothing"] is True
    assert contract["requires_separate_future_human_approved_step"] is True


def test_all_capability_flags_false_under_every_outcome():
    flags = (
        "authorizes_trading",
        "authorizes_data_fetch",
        "authorizes_backtest",
        "authorizes_paper_trading",
        "authorizes_live_trading",
        "authorizes_broker_exchange",
        "authorizes_automation",
        "authorizes_real_world_action",
        "injects_real_provider",
        "implements_provider",
        "calls_endpoint",
        "fetches_url",
        "opens_network",
        "reads_credential",
        "acquires_real_data",
        "unlocks_downstream_gate",
        "unlocks_real_data_qa",
        "unlocks_baseline_backtest",
        "unlocks_paper_trading",
        "unlocks_micro_live",
        "crosses_boundary",
        "promotes_beyond_boundary",
        "executes",
    )
    for payload in (None, _ready_input(authorizes_trading=True)):
        contract = _BUILD(payload)
        for flag in flags:
            assert contract[flag] is False, (payload, flag)
        for gate in DRY_RUN_GATE_LOCK_FLAGS:
            assert contract[gate] is True, (payload, gate)


# --------------------------------------------------------------------------- #
# Render
# --------------------------------------------------------------------------- #
def test_render_is_a_readonly_markdown_string():
    text = _RENDER(_BUILD())
    assert isinstance(text, str)
    assert text.startswith(
        "# Crypto-D1 Selected Read-Only Spot Provider Fetch Runner Dry Run"
    )
    assert "## Dry Run" in text
    assert "## No Execution Authorization" in text
    assert "## Operator Next Step" in text


def test_generated_guidance_has_no_execution_verbs():
    contract = _BUILD()
    blob = " ".join(
        str(contract.get(k, ""))
        for k in ("operator_next_step", "operator_notes", "core_rule")
    )
    blob += " " + " ".join(
        str(s) for s in contract.get("human_operator_required_next_steps", [])
    )
    tokens = set(
        "".join(
            ch if (ch.isalnum() or ch == "_") else " " for ch in blob.lower()
        ).split()
    )
    for term in DRY_RUN_FORBIDDEN_TRADE_TERMS:
        assert term not in tokens, term


# --------------------------------------------------------------------------- #
# AST purity: stdlib-only, no I/O, no forbidden imports
# --------------------------------------------------------------------------- #
_ALLOWED_IMPORTS = {"__future__", "typing"}
_FORBIDDEN_CALL_NAMES = {"open", "__import__", "eval", "exec", "compile", "input"}
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
    "datetime",
    "time",
    "random",
    "pickle",
    "sqlite3",
}


def _module_ast():
    return ast.parse(_MODPATH.read_text(encoding="utf-8"))


def test_module_imports_are_stdlib_typing_only():
    for node in ast.walk(_module_ast()):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] in _ALLOWED_IMPORTS, alias.name
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            assert root in _ALLOWED_IMPORTS, node.module


def test_module_has_no_forbidden_calls():
    for node in ast.walk(_module_ast()):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id not in _FORBIDDEN_CALL_NAMES, node.func.id


def test_module_has_no_forbidden_module_tokens():
    imported_roots = set()
    for node in ast.walk(_module_ast()):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            imported_roots.add((node.module or "").split(".")[0])
    assert not (imported_roots & _FORBIDDEN_MODULE_TOKENS)


def test_module_does_not_import_the_registry():
    # The contract must stay pure so the registry can import IT (no circular dep).
    src = _MODPATH.read_text(encoding="utf-8")
    assert "strategy_factory_mission_flow_bundle_registry" not in src
    assert "strategy_factory_mission_flow_status" not in src


def test_building_writes_no_files(tmp_path):
    before = set(tmp_path.iterdir())
    _BUILD()
    _BUILD(_ready_input())
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
