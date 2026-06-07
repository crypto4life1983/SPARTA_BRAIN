"""Tests for the Crypto-D1 Read-Only Real Data QA Boundary Plan Contract (Block 139).

The contract is a pure, stdlib-only, read-only RESEARCH_ONLY paper module. It
produces -- on paper only -- a deterministic PLAN for a future, human-approved,
READ-ONLY data / API step. It fetches no data, reads no dataset, calls no
Databento, checks no credential, exposes no secret, writes no manifest / runtime /
dashboard output, and unlocks no gate. These tests assert the schema / constants,
the mission-flow truth sync against the live status module, every one of the ten
required plan outputs, the missing-pair derivation, Databento presence-without-
secret, the forbidden-flag / unlock / fetch-now refusals, that a secret value is
never carried, determinism / isolation, validation, render, AST purity
(stdlib+typing only, no I/O), and the two additive commander_2_safety allowlist
entries.
"""

from __future__ import annotations

import ast
import pathlib

from sparta_commander.strategy_factory_crypto_d1_read_only_data_qa_boundary_plan_contract import (  # noqa: E501
    DEFAULT_PLAN_INPUT,
    MISSION_FLOW_CURRENT_STAGE,
    MISSION_FLOW_NEXT_REQUIRED_ACTION,
    PLAN_ALLOWED_LATER_CAPABILITIES,
    PLAN_ALLOWED_LATER_CHANGE_PATHS,
    PLAN_AUTHORIZATION_FLAGS,
    PLAN_CORE_RULE,
    PLAN_DEFAULT_DATA_STORE_PATH,
    PLAN_DEFAULT_NEEDED_SYMBOLS,
    PLAN_DEFAULT_NEEDED_TIMEFRAMES,
    PLAN_FORBIDDEN_TRADE_TERMS,
    PLAN_GATE_LOCK_FLAGS,
    PLAN_GATE_UNLOCK_REQUEST_FLAGS,
    PLAN_HARD_STOP_CONDITIONS,
    PLAN_LABEL,
    PLAN_MODE,
    PLAN_SAFETY_POSTURE,
    PLAN_SCHEMA_VERSION,
    PLAN_SCOPED_TESTS,
    PLAN_STATUS,
    PLAN_STILL_FORBIDDEN_CAPABILITIES,
    assess_read_only_data_qa_boundary_plan,
    build_crypto_d1_read_only_data_qa_boundary_plan_contract,
    render_crypto_d1_read_only_data_qa_boundary_plan_contract_markdown,
    validate_crypto_d1_read_only_data_qa_boundary_plan_contract,
)

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
_MODPATH = (
    _REPO_ROOT
    / "sparta_commander"
    / "strategy_factory_crypto_d1_read_only_data_qa_boundary_plan_contract.py"
)
_SAFETY_PATH = _REPO_ROOT / "sparta_commander" / "commander_2_safety.py"

_MODULE_ALLOWLIST_LINE = (
    "sparta_commander/strategy_factory_crypto_d1_read_only_data_qa_boundary_plan_contract.py"
)
_TEST_ALLOWLIST_LINE = (
    "tests/test_strategy_factory_crypto_d1_read_only_data_qa_boundary_plan_contract.py"
)

_ASSESS = assess_read_only_data_qa_boundary_plan
_BUILD = build_crypto_d1_read_only_data_qa_boundary_plan_contract
_VALIDATE = validate_crypto_d1_read_only_data_qa_boundary_plan_contract
_RENDER = render_crypto_d1_read_only_data_qa_boundary_plan_contract_markdown


def _safe_input(**overrides):
    """A safe static plan input: at the human boundary, all gates locked, two
    declared datasets covering BTCUSD/1d and MNQ+MGC/1d, needing the three crypto
    majors at 1d -> ETHUSD@1d and SOLUSD@1d come out missing."""
    payload = {
        "mode": "RESEARCH_ONLY",
        "read_only": True,
        "executes": False,
        "mission_flow_current_stage": MISSION_FLOW_CURRENT_STAGE,
        "mission_flow_next_required_action": MISSION_FLOW_NEXT_REQUIRED_ACTION,
        "real_data_qa_blocked": True,
        "baseline_backtest_blocked": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
        "needed_symbols": ["BTCUSD", "ETHUSD", "SOLUSD"],
        "needed_timeframes": ["1d"],
        "declared_local_datasets": [
            {
                "name": "databento_cache",
                "path": "data/databento_cache/",
                "symbols": ["BTCUSD"],
                "timeframes": ["1d"],
            },
            {
                "name": "databento_long_history",
                "path": "data/s10_d1_mnq_mgc_databento_long_history/",
                "symbols": ["MNQ", "MGC"],
                "timeframes": ["1d"],
            },
        ],
        "data_store_path": "data/databento_cache/",
        "databento_config_declared": False,
    }
    payload.update(overrides)
    return payload


# --------------------------------------------------------------------------- #
# Schema / constants
# --------------------------------------------------------------------------- #
def test_schema_version_and_labels():
    assert PLAN_SCHEMA_VERSION == (
        "strategy_factory_crypto_d1_read_only_data_qa_boundary_plan_contract.v1"
    )
    assert PLAN_LABEL == (
        "Block 139 - Crypto-D1 Read-Only Real Data QA Boundary Plan Contract"
    )
    assert PLAN_STATUS == "READ_ONLY_DATA_QA_PLAN_ONLY"
    assert PLAN_MODE == "RESEARCH_ONLY"
    assert "NEVER unlocks Real Data QA" in PLAN_CORE_RULE


def test_allowed_later_capabilities_are_read_only_data_only():
    assert PLAN_ALLOWED_LATER_CAPABILITIES == (
        "read_only_market_data_inventory",
        "read_only_missing_data_acquisition",
        "databento_historical_market_data_read_only",
        "local_dataset_inspection",
        "manifest_gap_report",
    )


def test_still_forbidden_capabilities_cover_every_execution_surface():
    f = PLAN_STILL_FORBIDDEN_CAPABILITIES
    for cap in (
        "exchange_trading_api",
        "broker_api",
        "order_placement",
        "paper_live_trading",
        "account_control",
        "portfolio_control",
        "telegram_trade_command",
        "tradingview_execution_webhook",
        "strategy_promotion",
        "automation_that_trades",
        "credentials_in_logs_or_reports",
    ):
        assert cap in f, cap


def test_default_coverage_constants():
    assert PLAN_DEFAULT_NEEDED_SYMBOLS == ("BTCUSD", "ETHUSD", "SOLUSD")
    assert PLAN_DEFAULT_NEEDED_TIMEFRAMES == ("1d",)
    assert PLAN_DEFAULT_DATA_STORE_PATH == "data/databento_cache/"


def test_hard_stop_conditions_present():
    blob = " ".join(PLAN_HARD_STOP_CONDITIONS).lower()
    assert "credential" in blob
    assert "broker" in blob
    assert "databento" in blob
    assert "unlocked" in blob or "unlock" in blob
    assert len(PLAN_HARD_STOP_CONDITIONS) >= 8


def test_safety_posture_true_facts_all_capability_false():
    posture = PLAN_SAFETY_POSTURE
    posture_true = {"read_only", "research_only", "human_approval_required"}
    for key in posture_true:
        assert posture[key] is True, key
    for key, value in posture.items():
        if key in posture_true:
            continue
        assert value is False, key


# --------------------------------------------------------------------------- #
# Mission-flow truth sync
# --------------------------------------------------------------------------- #
def test_mission_flow_truth_matches_live_status_module():
    from sparta_commander import strategy_factory_mission_flow_status as status

    assert MISSION_FLOW_CURRENT_STAGE == status.CURRENT_STAGE
    assert MISSION_FLOW_NEXT_REQUIRED_ACTION == status.NEXT_REQUIRED_ACTION


# --------------------------------------------------------------------------- #
# Ten required plan outputs
# --------------------------------------------------------------------------- #
def test_plan_exposes_all_ten_required_outputs():
    plan = _BUILD()["plan"]
    for key in (
        "datasets_to_inventory",          # 1
        "needed_symbols",                 # 2
        "needed_timeframes",              # 2
        "missing_pairs",                  # 3
        "databento_config_present_declared",  # 4
        "read_only_api_calls_needed_later",   # 5
        "data_store_path",                # 6
        "allowed_later_change_paths",     # 7
        "scoped_tests",                   # 8
        "hard_stop_conditions",           # 9
        "no_trading_confirmation",        # 10
    ):
        assert key in plan, key


def test_datasets_to_inventory_echo_declared_descriptors():
    plan = _BUILD(_safe_input())["plan"]
    names = [d["name"] for d in plan["datasets_to_inventory"]]
    assert names == ["databento_cache", "databento_long_history"]
    for d in plan["datasets_to_inventory"]:
        assert "read_only" in d["action"]


def test_needed_pairs_and_missing_pairs_derivation():
    contract = _BUILD(_safe_input())
    plan = contract["plan"]
    assert plan["needed_symbols"] == ["BTCUSD", "ETHUSD", "SOLUSD"]
    assert plan["needed_timeframes"] == ["1d"]
    assert plan["needed_pairs"] == ["BTCUSD@1d", "ETHUSD@1d", "SOLUSD@1d"]
    assert plan["missing_pairs"] == ["ETHUSD@1d", "SOLUSD@1d"]
    assert plan["covered_pairs"] == ["BTCUSD@1d"]


def test_read_only_api_calls_match_missing_pairs_and_are_read_only():
    plan = _BUILD(_safe_input())["plan"]
    calls = plan["read_only_api_calls_needed_later"]
    assert len(calls) == len(plan["missing_pairs"])
    for call in calls:
        assert "read-only" in call.lower()
        assert "ETHUSD" in call or "SOLUSD" in call


def test_data_store_path_and_allowed_later_change_paths():
    plan = _BUILD(_safe_input())["plan"]
    assert plan["data_store_path"] == "data/databento_cache/"
    assert list(PLAN_ALLOWED_LATER_CHANGE_PATHS) == plan["allowed_later_change_paths"]


def test_scoped_tests_name_this_test_and_the_safety_test():
    plan = _BUILD()["plan"]
    assert _TEST_ALLOWLIST_LINE in plan["scoped_tests"]
    assert "tests/test_sparta_commander_2_safety.py" in plan["scoped_tests"]
    assert list(PLAN_SCOPED_TESTS) == plan["scoped_tests"]


def test_no_trading_confirmation_affirms_all_eight_facts():
    confirmation = _BUILD()["plan"]["no_trading_confirmation"]
    for key in (
        "no_trading",
        "no_exchange_or_broker_execution",
        "no_order_placement",
        "no_paper_or_live_trading",
        "no_account_or_portfolio_control",
        "no_strategy_promotion",
        "no_trading_automation",
        "no_credentials_in_logs_or_reports",
    ):
        assert confirmation[key] is True, key


# --------------------------------------------------------------------------- #
# Databento presence without exposing a secret
# --------------------------------------------------------------------------- #
def test_databento_presence_is_a_declared_bool_no_secret():
    plan = _BUILD(_safe_input(databento_config_declared=True))["plan"]
    assert plan["databento_config_present_declared"] is True
    assert plan["databento_secret_exposed"] is False
    assert "static operator assertion" in plan["databento_config_note"].lower()


def test_default_input_declares_no_databento_config():
    plan = _BUILD()["plan"]
    assert plan["databento_config_present_declared"] is False
    assert plan["databento_secret_exposed"] is False


def test_a_secret_value_in_input_is_never_carried_into_contract():
    # Even if a caller smuggles a secret-looking key, the contract never echoes a
    # value, and validation flags it.
    payload = _safe_input(databento_api_key="SHOULD-NEVER-APPEAR")
    contract = _BUILD(payload)
    assert "SHOULD-NEVER-APPEAR" not in _RENDER(contract)
    # the contract itself carries no populated secret-looking field.
    assert _VALIDATE(contract)["no_secret_value_fields"] is True


# --------------------------------------------------------------------------- #
# Safety posture in the built contract
# --------------------------------------------------------------------------- #
def test_assessment_reports_safe_at_boundary():
    result = _ASSESS(_safe_input())
    assert result["safe"] is True
    assert result["mission_flow_aligned"] is True
    assert result["forbidden_flag_hits"] == []
    assert result["fetches_data"] is False
    assert result["calls_databento"] is False
    assert result["authorizes_nothing"] is True


def test_built_contract_keeps_every_gate_blocked_and_flag_false():
    contract = _BUILD(_safe_input())
    assert contract["real_data_qa_blocked"] is True
    assert contract["baseline_backtest_blocked"] is True
    assert contract["paper_trading_gate_locked"] is True
    assert contract["micro_live_gate_locked"] is True
    assert contract["real_data_qa_state"] == "BLOCKED"
    assert contract["paper_live_state"] == "LOCKED"
    for flag in (
        "executes",
        "fetches_data",
        "inspects_datasets",
        "calls_databento",
        "checks_live_credentials",
        "exposes_secret",
        "writes_manifest",
        "writes_runtime_outputs",
        "writes_dashboard_outputs",
        "authorizes_trading",
        "authorizes_broker_exchange",
        "authorizes_order_placement",
        "authorizes_strategy_promotion",
        "unlocks_real_data_qa",
        "unlocks_baseline_backtest",
        "unlocks_paper_trading",
        "unlocks_micro_live",
    ):
        assert contract[flag] is False, flag
    assert contract["authorizes_nothing"] is True
    assert contract["read_only"] is True
    assert contract["human_approval_required"] is True


# --------------------------------------------------------------------------- #
# Unsafe-flag refusals
# --------------------------------------------------------------------------- #
def test_authorization_flag_marks_unsafe():
    for flag in PLAN_AUTHORIZATION_FLAGS:
        result = _ASSESS(_safe_input(**{flag: True}))
        assert result["safe"] is False, flag
        assert flag in result["forbidden_flag_hits"], flag


def test_gate_unlock_or_fetch_now_request_marks_unsafe():
    for flag in PLAN_GATE_UNLOCK_REQUEST_FLAGS:
        result = _ASSESS(_safe_input(**{flag: True}))
        assert result["safe"] is False, flag
        assert flag in result["forbidden_flag_hits"], flag


def test_unlocking_a_locked_gate_marks_unsafe():
    for flag in PLAN_GATE_LOCK_FLAGS:
        result = _ASSESS(_safe_input(**{flag: False}))
        assert result["safe"] is False, flag
        assert ("unlocked:" + flag) in result["forbidden_flag_hits"], flag


def test_off_boundary_mission_flow_marks_unsafe():
    result = _ASSESS(_safe_input(mission_flow_current_stage="SOMETHING_ELSE"))
    assert result["mission_flow_aligned"] is False
    assert result["safe"] is False


def test_unsafe_contract_still_keeps_gates_locked_and_flags_false():
    # Even when an unsafe flag is set, the contract never flips a capability flag
    # or unlocks a gate -- it only reports safe=False.
    contract = _BUILD(_safe_input(authorizes_trading=True))
    assert contract["safe"] is False
    assert contract["unlocks_real_data_qa"] is False
    assert contract["real_data_qa_blocked"] is True
    assert contract["authorizes_trading"] is False  # contract flag stays False


# --------------------------------------------------------------------------- #
# Determinism / isolation
# --------------------------------------------------------------------------- #
def test_assessment_is_deterministic():
    payload = _safe_input()
    assert _ASSESS(payload) == _ASSESS(payload)


def test_build_does_not_mutate_caller_payload():
    import copy

    payload = _safe_input()
    snapshot = copy.deepcopy(payload)
    _BUILD(payload)
    assert payload == snapshot


def test_default_input_is_not_shared_between_builds():
    d1 = _BUILD()
    d2 = _BUILD()
    d1["plan"]["missing_pairs"].append("TAMPERED@1d")
    assert "TAMPERED@1d" not in d2["plan"]["missing_pairs"]
    assert DEFAULT_PLAN_INPUT["databento_config_declared"] is False


# --------------------------------------------------------------------------- #
# Validation / render
# --------------------------------------------------------------------------- #
def test_default_contract_validates():
    verdict = _VALIDATE(_BUILD())
    assert verdict["valid"] is True
    assert verdict["missing_fields"] == []
    assert verdict["flags_false"] is True
    assert verdict["gates_locked"] is True
    assert verdict["authorizes_nothing"] is True
    assert verdict["mission_flow_refs_ok"] is True
    assert verdict["posture_ok"] is True
    assert verdict["states_blocked_locked"] is True
    assert verdict["secret_not_exposed"] is True
    assert verdict["no_secret_value_fields"] is True
    assert verdict["acquires_nothing"] is True
    assert verdict["no_trading_confirmed"] is True
    assert verdict["no_trade_language"] is True
    assert verdict["forbidden_list_intact"] is True
    assert verdict["no_forbidden_in_allowed"] is True


def test_safe_and_unsafe_inputs_both_validate_structurally():
    for payload in (_safe_input(), _safe_input(authorizes_trading=True), None):
        verdict = _VALIDATE(_BUILD(payload))
        assert verdict["valid"] is True, payload


def test_validate_rejects_tampered_executes():
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
    assert verdict["flags_false"] is False


def test_validate_rejects_unlocked_gate():
    contract = _BUILD()
    contract["real_data_qa_blocked"] = False
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["gates_locked"] is False


def test_validate_rejects_exposed_secret():
    contract = _BUILD()
    contract["plan"]["databento_api_key"] = "leaked-value"
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["no_secret_value_fields"] is False


def test_validate_rejects_forbidden_capability_leaking_into_allowed():
    contract = _BUILD()
    contract["allowed_later_capabilities"].append("order_placement")
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["no_forbidden_in_allowed"] is False


def test_render_is_a_readonly_markdown_string():
    text = _RENDER(_BUILD())
    assert isinstance(text, str)
    assert text.startswith(
        "# Crypto-D1 Read-Only Real Data QA Boundary Plan"
    )
    assert "## 1. Datasets To Inventory" in text
    assert "## 3. Possibly Missing Pairs" in text
    assert "## 5. Read-Only API Calls Needed Later" in text
    assert "## 9. Hard-Stop Conditions" in text
    assert "## 10. No-Execution Confirmation" in text
    assert "## Still Forbidden (always)" in text


def test_authored_narrative_has_no_execution_verbs():
    contract = _BUILD(_safe_input())
    blob = " ".join(
        str(contract.get(k, ""))
        for k in ("operator_next_step", "plan_summary", "core_rule")
    )
    blob += " " + " ".join(
        str(s) for s in contract.get("human_operator_required_next_steps", [])
    )
    tokens = set(
        "".join(
            c if (c.isalnum() or c == "_") else " " for c in blob.lower()
        ).split()
    )
    for term in PLAN_FORBIDDEN_TRADE_TERMS:
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


def test_building_writes_no_files(tmp_path):
    before = set(tmp_path.iterdir())
    _BUILD()
    _BUILD(_safe_input())
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
